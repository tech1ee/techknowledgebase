---
title: "KMP Interop Deep Dive: ObjC, Swift Export, cinterop"
created: 2026-01-04
modified: 2026-01-04
tags:
  - topic/jvm
  - topic/kmp
  - interop
  - objc
  - topic/swift
  - cinterop
  - skie
  - type/deep-dive
  - level/advanced
related:
  - "[[kmp-ios-deep-dive]]"
  - "[[kmp-memory-management]]"
  - "[[kmp-expect-actual]]"
prerequisites:
  - "[[kmp-expect-actual]]"
  - "[[kmp-ios-deep-dive]]"
  - "[[kmp-memory-management]]"
cs-foundations:
  - "[[abi-calling-conventions]]"
  - "[[ffi-foreign-function-interface]]"
  - "[[bridges-bindings-overview]]"
  - "[[memory-layout-marshalling]]"
status: published
---

# KMP Interop Deep Dive

> **TL;DR:** Три механизма interop: Objective-C bridge (stable, Kotlin→ObjC→Swift), Swift Export (experimental, прямой Swift), cinterop (C/ObjC библиотеки). SKIE добавляет async/await и Flow→AsyncSequence пока Swift Export не ready. Suspend функции → completionHandler/async. @Throws для исключений. Generics ограничены в ObjC (T→T?). @ObjCName для Swift-friendly имён.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **ABI & Calling Conventions** | Как функции вызываются между языками | [[abi-calling-conventions]] |
| **FFI** | Foreign Function Interface механизмы | [[ffi-foreign-function-interface]] |
| **Bridges & Bindings** | Как генерируются обёртки | [[bridges-bindings-overview]] |
| KMP Architecture | Структура проекта | [[kmp-project-structure]] |
| expect/actual | Платформенный код | [[kmp-expect-actual]] |

> **Рекомендация:** Для глубокого понимания interop прочитай CS-фундамент об ABI и FFI. Это объяснит ПОЧЕМУ существуют ограничения и overhead.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **cinterop** | Инструмент для C/ObjC биндингов | Переводчик с C на Kotlin |
| **ObjC Bridge** | Мост между Kotlin и Swift через ObjC | Двойной перевод: книга → английский → русский |
| **Swift Export** | Прямой экспорт в Swift (без ObjC) | Прямой перевод без посредников |
| **SKIE** | Swift Kotlin Interface Enhancer | Улучшитель перевода — делает текст более естественным |
| **.def файл** | Конфигурация cinterop | Инструкция переводчику — что и как переводить |
| **Framework** | Скомпилированный модуль для iOS | Готовая книга с переводом |

---

## Почему это сложно

### Проблема разных миров

Kotlin и Swift — современные языки с похожими фичами: generics, nullability, enums с associated values, async/await. Но они не могут напрямую общаться. Почему?

**Причина:** Нет общего ABI (Application Binary Interface).

```
Kotlin/Native → LLVM IR → Machine code (с K/N runtime)
Swift         → LLVM IR → Machine code (с Swift runtime)
```

Оба компилируются в машинный код через LLVM, но runtimes разные. Kotlin/Native runtime управляет памятью через GC, Swift — через ARC. Объекты имеют разный layout в памяти. Функции используют разные calling conventions.

### Почему через Objective-C?

Исторически iOS SDK написан на Objective-C. Apple создала стабильный ObjC runtime с предсказуемым ABI. Swift может общаться с ObjC через `@objc`. Kotlin/Native тоже умеет генерировать ObjC-совместимые заголовки.

**Результат:** Kotlin → ObjC headers → Swift

Это работает, но теряются фичи, которых нет в ObjC:
- Generics с constraints
- Enums с associated values
- Sealed classes
- Default arguments
- Suspend → completion handler (не async/await)

### Эволюция interop

| Период | Подход | Ограничения |
|--------|--------|-------------|
| 2017-2023 | ObjC bridge only | Потеря Swift фич |
| 2023+ | SKIE (Touchlab) | Flow→AsyncSequence, sealed→enum |
| 2024+ | Swift Export (preview) | Прямой экспорт, enums |
| 2026 (plan) | Swift Export stable | Полная Swift интеграция |

### Реальные последствия

| Аспект | Проблема | Решение |
|--------|----------|---------|
| **Enums** | Kotlin enum → ObjC class | SKIE или Swift Export |
| **Generics** | T → T? (nullable) | `<T : Any>` constraint |
| **Async** | suspend → completionHandler | SKIE async/await |
| **Sealed** | Нет exhaustive switch | SKIE |
| **Collections** | Double conversion overhead | NSArray напрямую |

---

## Три механизма Interop

```
┌─────────────────────────────────────────────────────────────┐
│              KMP INTEROP MECHANISMS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. OBJECTIVE-C INTEROP (Stable)                           │
│   ─────────────────────────────────                         │
│   Kotlin → ObjC Headers → Swift                             │
│   ✅ Production ready                                       │
│   ⚠️ Generic limitations                                    │
│   ⚠️ Collections overhead                                   │
│                                                             │
│   2. SWIFT EXPORT (Experimental)                            │
│   ────────────────────────────────                          │
│   Kotlin → Swift directly                                   │
│   ✅ Better types (enums, nullability)                      │
│   ❌ Not production ready                                   │
│   🎯 Target: Stable 2026                                    │
│                                                             │
│   3. CINTEROP (Stable)                                      │
│   ─────────────────────                                     │
│   C/ObjC Libraries → Kotlin                                 │
│   ✅ Any C library                                          │
│   ✅ iOS SDK access                                         │
│   ✅ Static libraries                                       │
│                                                             │
│   BONUS: SKIE (Touchlab)                                    │
│   ───────────────────────                                   │
│   Enhanced ObjC bridge                                      │
│   ✅ Flow → AsyncSequence                                   │
│   ✅ Suspend → async/await                                  │
│   ✅ Sealed → Swift enum                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Objective-C Interop

### Type Mappings

```
┌─────────────────────────────────────────────────────────────┐
│              KOTLIN ↔ SWIFT/OBJECTIVE-C MAPPINGS             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   KOTLIN              SWIFT              OBJECTIVE-C        │
│   ──────              ─────              ───────────        │
│   class               class              @interface         │
│   interface           protocol           @protocol          │
│   enum class          class(!)           @interface         │
│   object              class+shared       class+shared       │
│                                                             │
│   String              String             NSString           │
│   List<T>             Array              NSArray            │
│   Map<K,V>            Dictionary         NSDictionary       │
│   Set<T>              Set                NSSet              │
│                                                             │
│   suspend fun         async/completion   completionHandler  │
│   Int                 Int32              int32_t            │
│   Long                Int64              int64_t            │
│   Boolean             Bool               BOOL               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Classes

```kotlin
// Kotlin
class User(val id: String, val name: String) {
    fun greet(): String = "Hello, $name!"
}

// Generated Objective-C header
@interface SharedUser : SharedBase
@property (readonly) NSString *id;
@property (readonly) NSString *name;
- (NSString *)greet;
- (instancetype)initWithId:(NSString *)id name:(NSString *)name;
@end

// Swift usage
let user = User(id: "123", name: "John")
print(user.greet())  // "Hello, John!"
```

### Suspending Functions

```kotlin
// Kotlin
class Repository {
    suspend fun fetchUser(id: String): User {
        delay(1000)
        return User(id, "John")
    }
}
```

```swift
// Swift 5.5+ (async/await)
let user = try await repository.fetchUser(id: "123")

// Traditional (completion handler)
repository.fetchUser(id: "123") { user, error in
    if let user = user {
        print(user.name)
    }
}
```

### Exception Handling

```kotlin
// Kotlin — используй @Throws для propagation в Swift
class Repository {
    @Throws(IOException::class)
    fun readFile(path: String): String {
        if (!File(path).exists()) {
            throw IOException("File not found: $path")
        }
        return File(path).readText()
    }
}
```

```swift
// Swift — теперь можно ловить ошибки
do {
    let content = try repository.readFile(path: "/path/to/file")
    print(content)
} catch {
    print("Error: \(error)")
}
```

```kotlin
// ⚠️ БЕЗ @Throws — исключения НЕ propagate!
// Это вызовет crash на iOS без возможности поймать
fun dangerousOperation() {
    throw IllegalStateException("Oops!")  // Crash!
}
```

### Generics Limitations

```kotlin
// Kotlin
class Container<T>(val item: T) {
    fun getItem(): T = item
}

// Swift — T становится T? из-за ObjC ограничений!
let container = Container<NSString>(item: "Hello")
let item: String? = container.getItem()  // Optional!

// Решение: явный non-null constraint
class Container<T : Any>(val item: T) {
    fun getItem(): T = item  // Теперь non-null в Swift
}
```

```
┌─────────────────────────────────────────────────────────────┐
│              GENERICS: KOTLIN vs SWIFT                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   KOTLIN                          SWIFT                     │
│   ──────                          ─────                     │
│                                                             │
│   class Box<T>                    class Box<T>              │
│     fun get(): T                    func get() -> T?        │
│                                     ↑ NULLABLE!             │
│                                                             │
│   class Box<T : Any>              class Box<T>              │
│     fun get(): T                    func get() -> T         │
│                                     ↑ NON-NULL              │
│                                                             │
│   Правило: всегда используй <T : Any> для non-null          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Naming & Visibility

```kotlin
// Кастомные имена для Swift
@ObjCName(swiftName = "UserProfile")
class User {
    @ObjCName("displayName")
    val name: String = "John"

    @ObjCName("fullGreeting")
    fun greet(@ObjCName("for") target: String): String {
        return "Hello, $target!"
    }
}

// Swift usage — чистые имена
let profile = UserProfile()
print(profile.displayName)
print(profile.fullGreeting(for: "World"))
```

```kotlin
// Скрыть от Swift/ObjC
@HiddenFromObjC
internal fun internalHelper() { }

// Сделать "приватным" в Swift (__ prefix)
@ShouldRefineInSwift
fun complexFunction() { }  // Виден как __complexFunction
```

### Collections Performance

```kotlin
// ⚠️ ПРОБЛЕМА: двойная конверсия
// Kotlin List → NSArray → Swift Array

// Swift side:
// let items: [String] = kotlinObject.getItems()  // Overhead!
```

```swift
// ✅ РЕШЕНИЕ: работай с NSArray напрямую
let nsItems: NSArray = kotlinObject.getItems() as NSArray
for item in nsItems {
    let str = item as! NSString
    print(str.length)
}

// Или кастуй в конце
let items = kotlinObject.getItems() as! [String]
// Но это всё равно одна конверсия
```

---

## 2. Swift Export (Experimental)

### Setup

```kotlin
// build.gradle.kts
kotlin {
    iosArm64()
    iosSimulatorArm64()

    swiftExport {
        moduleName = "Shared"
        flattenPackage = "com.example.app"

        export(project(":core")) {
            moduleName = "Core"
        }
    }
}
```

```bash
# Xcode Build Phase
# Заменить embedAndSignAppleFrameworkForXcode на:
./gradlew :shared:embedSwiftExportForXcode
```

### Improved Type Mappings

```kotlin
// Kotlin enum class
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF)
}
```

```swift
// Swift Export — настоящий Swift enum!
public enum Color: CaseIterable, RawRepresentable {
    case RED, GREEN, BLUE
    public var rgb: Int32 { get }
}

// Можно использовать в switch
switch color {
case .RED: print("Red!")
case .GREEN: print("Green!")
case .BLUE: print("Blue!")
}

// ObjC interop — это класс, не enum
// class Color { static let RED, GREEN, BLUE }
```

### Nullability

```kotlin
// Kotlin
class User {
    val age: Int? = null
}
```

```swift
// Swift Export — native Optional
var age: Int32?  // ✅ Native Swift optional

// ObjC Interop — boxed type
var age: KotlinInt?  // ⚠️ Wrapper class
```

### Packages as Enums

```kotlin
// Kotlin packages
package com.example.users
fun getUser(): User { }

package com.example.orders
fun getOrder(): Order { }
```

```swift
// Swift Export — nested enums для namespace
com.example.users.getUser()
com.example.orders.getOrder()

public enum com {
    public enum example {
        public enum users { }
        public enum orders { }
    }
}
```

### Current Limitations

```kotlin
// ❌ НЕ поддерживается:

// 1. Functional types export
val onClick: () -> Unit = {}  // Cannot export

// 2. Subclassing from Swift
open class Base { }  // Swift cannot subclass

// 3. Collection inheritance
class MyList : List<String> { }  // Ignored

// 4. Generic type parameters (erased)
class Box<T>(val item: T)  // T erased to upper bound
```

---

## 3. SKIE (Swift Kotlin Interface Enhancer)

### Setup

```kotlin
// build.gradle.kts
plugins {
    kotlin("multiplatform")
    id("co.touchlab.skie") version "0.9.3"
}

skie {
    features {
        // Включить все улучшения
        enableAll()
    }
}
```

### Flow → AsyncSequence

```kotlin
// Kotlin
class ViewModel {
    val users: Flow<List<User>> = repository.observeUsers()
}
```

```swift
// БЕЗ SKIE:
// Нужен KMP-NativeCoroutines или ручные обёртки

// С SKIE — native AsyncSequence!
for try await users in viewModel.users {
    updateUI(with: users)
}
```

### Suspend → async/await

```kotlin
// Kotlin
suspend fun fetchData(): String {
    delay(1000)
    return "Data"
}
```

```swift
// С SKIE — native Swift async
let data = try await fetchData()

// Автоматическая отмена при Task cancellation!
let task = Task {
    let data = try await fetchData()
}
task.cancel()  // Cancellation propagates to Kotlin!
```

### Sealed Classes

```kotlin
// Kotlin
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}
```

```swift
// С SKIE — exhaustive switch!
switch result {
case let .success(data):
    print(data.data)
case let .error(error):
    print(error.message)
case .loading:
    showLoader()
}

// БЕЗ SKIE:
// if result is ResultSuccess { }
// else if result is ResultError { }
// else { /* ???  */ }
```

### Enums with Associated Values

```kotlin
// Kotlin
sealed interface NetworkError {
    data class HttpError(val code: Int, val body: String) : NetworkError
    data class Timeout(val duration: Long) : NetworkError
    object NoConnection : NetworkError
}
```

```swift
// С SKIE — Swift-like API
switch error {
case let .httpError(code, body):
    print("HTTP \(code): \(body)")
case let .timeout(duration):
    print("Timeout after \(duration)ms")
case .noConnection:
    print("No connection")
}
```

---

## 4. cinterop (C/Objective-C Libraries)

### .def File Structure

```
# nativeInterop/cinterop/libcrypto.def

# Заголовки для генерации биндингов
headers = openssl/crypto.h openssl/evp.h

# Фильтр (что включить)
headerFilter = openssl/*

# Kotlin package
package = crypto

# Compiler flags
compilerOpts = -I/usr/local/include

# Linker flags
linkerOpts = -L/usr/local/lib -lcrypto

# Для static library
staticLibraries = libcrypto.a
libraryPaths = /usr/local/lib
```

### Gradle Configuration

```kotlin
// build.gradle.kts
kotlin {
    iosArm64 {
        compilations.getByName("main") {
            cinterops {
                val libcrypto by creating {
                    defFile(project.file("nativeInterop/cinterop/libcrypto.def"))

                    // Дополнительные опции
                    compilerOpts("-I/usr/local/include")
                    includeDirs.allHeaders("/usr/local/include")
                }
            }
        }
    }
}
```

### Using Generated Bindings

```kotlin
// После cinterop: доступен package crypto

import crypto.*

fun encryptData(data: ByteArray): ByteArray {
    // Сгенерированные биндинги
    val ctx = EVP_CIPHER_CTX_new()
    EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), null, key, iv)
    // ...
    EVP_CIPHER_CTX_free(ctx)
    return encrypted
}
```

### Platform Libraries (Built-in)

```kotlin
// Многие iOS frameworks доступны без cinterop!

import platform.Foundation.*
import platform.UIKit.*
import platform.CoreLocation.*

// Пример: работа с файловой системой
val fileManager = NSFileManager.defaultManager
val documents = fileManager.URLsForDirectory(
    NSDocumentDirectory,
    NSUserDomainMask
).firstOrNull() as? NSURL

// Пример: геолокация
class LocationManager : NSObject(), CLLocationManagerDelegateProtocol {
    private val manager = CLLocationManager()

    fun start() {
        manager.delegate = this
        manager.requestWhenInUseAuthorization()
        manager.startUpdatingLocation()
    }

    override fun locationManager(
        manager: CLLocationManager,
        didUpdateLocations: List<*>
    ) {
        val location = didUpdateLocations.lastOrNull() as? CLLocation
        println("Location: ${location?.coordinate}")
    }
}
```

### Calling Swift from Kotlin (via cinterop)

```swift
// Swift code with @objc
// Sources/SwiftHelper/SwiftHelper.swift

import Foundation

@objc public class SwiftHelper: NSObject {
    @objc public static func processData(_ data: Data) -> String {
        // Swift-only API usage
        return String(data: data, encoding: .utf8) ?? ""
    }
}
```

```
# nativeInterop/cinterop/SwiftHelper.def
language = Objective-C
headers = SwiftHelper-Swift.h
package = swifthelper
```

```kotlin
// Kotlin usage
import swifthelper.SwiftHelper

fun useSwiftCode() {
    val result = SwiftHelper.processData(data)
}
```

---

## 5. Best Practices

### API Design

```kotlin
// ✅ DO: design for Swift consumers

// 1. Use @ObjCName for clean Swift API
@ObjCName(swiftName = "UserRepository")
class KmpUserRepository {
    @ObjCName("getUser")
    suspend fun fetchUserById(@ObjCName("id") userId: String): User
}

// 2. Use sealed classes for Result types
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val message: String) : ApiResult<Nothing>()
}

// 3. Avoid raw Result<T> — use sealed classes
// ❌ fun getData(): Result<String>
// ✅ fun getData(): ApiResult<String>

// 4. Use @Throws for expected exceptions
@Throws(NetworkException::class)
suspend fun fetchData(): String
```

### Performance

```kotlin
// ❌ AVOID: passing large collections frequently
fun processItems(items: List<Item>): List<Result>  // Expensive!

// ✅ BETTER: batch processing
fun processItems(items: List<Item>, callback: (Result) -> Unit)

// ✅ BETTER: streaming
fun processItems(items: List<Item>): Flow<Result>
```

### Error Handling

```kotlin
// ❌ ПЛОХО: исключения теряются
suspend fun fetchData(): String {
    throw IllegalStateException("Error!")  // Lost in Swift!
}

// ✅ ХОРОШО: Result type
sealed class FetchResult {
    data class Success(val data: String) : FetchResult()
    data class Error(
        val message: String,
        val stackTrace: String? = null
    ) : FetchResult()
}

suspend fun fetchData(): FetchResult {
    return try {
        FetchResult.Success(api.getData())
    } catch (e: Exception) {
        FetchResult.Error(
            message = e.message ?: "Unknown error",
            stackTrace = e.stackTraceToString()
        )
    }
}
```

### Visibility

```kotlin
// ✅ Explicit visibility control

// Public API
class PublicRepository {
    fun getUser(): User  // Visible in Swift
}

// Internal implementation
@HiddenFromObjC
internal class InternalHelper {
    fun helperMethod()  // Hidden from Swift
}

// Refinement for Swift
@ShouldRefineInSwift
fun _internalButNeeded()  // Visible as __internalButNeeded
```

---

## Migration: ObjC → Swift Export

```kotlin
// Когда Swift Export станет stable:

// 1. Добавь swiftExport {} в build.gradle.kts
kotlin {
    swiftExport {
        moduleName = "Shared"
    }
}

// 2. Замени Build Phase в Xcode
// embedAndSignAppleFrameworkForXcode → embedSwiftExportForXcode

// 3. Обнови Swift код
// - enum class станут native Swift enums
// - Optional primitives без боксинга
// - Packages станут namespaces

// 4. Постепенно удаляй workarounds
// - SKIE может быть не нужен
// - @ObjCName можно убрать (лучшие дефолтные имена)
```

---

## Troubleshooting

### "Missing symbol" at Runtime

```bash
# Проблема: класс не найден при запуске

# Причина: strong linking к недоступному API
# Решение: оберни в Swift/ObjC с проверкой доступности

# Swift wrapper:
# @available(iOS 15.0, *)
# public func newApiWrapper() { }
```

### Generic Type Lost

```kotlin
// Проблема: T становится Any в Swift

// Решение: явный constraint
class Box<T : Any>(val item: T)  // T non-null

// Или: SKIE для лучшего generic support
```

### Collections Slow

```swift
// Проблема: медленная работа с коллекциями

// Решение: работай с NSArray напрямую
let nsArray = kotlinList as NSArray
for item in nsArray {
    // ...
}
```

### Exception Not Caught

```kotlin
// Проблема: Swift не ловит Kotlin исключение

// Решение: добавь @Throws
@Throws(IOException::class)
fun riskyOperation()

// Или: используй Result type
fun safeOperation(): Result<Data>
```

---

## Comparison Table

| Feature | ObjC Interop | Swift Export | SKIE |
|---------|-------------|--------------|------|
| Status | ✅ Stable | 🧪 Experimental | ✅ Stable |
| Enum | Class | Native enum | Native enum |
| Sealed | Classes | (Limited) | Exhaustive switch |
| Nullability | Boxed (Int?) | Native | Native |
| Flow | Manual | (Planned) | AsyncSequence |
| Suspend | completionHandler | (Planned) | async/await |
| Generics | Limited | Erased | Better |

---

## Мифы и заблуждения

### Миф 1: "Swift Export заменит всё остальное"

**Реальность:** Swift Export — это экспорт Kotlin → Swift. Он НЕ заменяет:
- cinterop (импорт C/ObjC библиотек → Kotlin)
- Работу с iOS SDK (platform.*)
- Вызов Swift кода из Kotlin (всё ещё через @objc)

Swift Export улучшает **одно направление**: как Swift видит твой Kotlin код.

### Миф 2: "SKIE — это костыль, скоро не нужен"

**Реальность:** SKIE решает проблемы, которые Swift Export пока НЕ планирует решать:
- Flow → AsyncSequence (Swift Export планирует, но не скоро)
- Cancellation support для suspend
- Sealed classes → exhaustive switch

Даже с Swift Export, SKIE может остаться полезным для coroutines/Flow.

### Миф 3: "Interop overhead незначителен"

**Реальность:** Каждый crossing boundary имеет cost:
- String: Kotlin → NSString → Swift String (две копии!)
- Collections: аналогично
- Вызовы: dispatch через ObjC runtime

Для hot paths это может быть значимым. Если передаёшь 10000 строк — это 20000 копий.

### Миф 4: "Pure Swift modules скоро будут поддержаны"

**Реальность:** JetBrains НЕ анонсировала поддержку pure Swift modules. Swift Export — это **экспорт** Kotlin в Swift, не импорт Swift в Kotlin. Для вызова Swift из Kotlin всё ещё нужен `@objc`.

### Миф 5: "@Throws нужен для всех функций"

**Реальность:** @Throws нужен только если хочешь, чтобы Swift МОГ поймать исключение. Без @Throws:
- Non-suspend: исключение = crash (не ловится)
- Suspend: только CancellationException propagates

Если функция не должна бросать исключения на Swift стороне — @Throws не нужен.

---

## Рекомендуемые источники

### Official Documentation

| Источник | Описание |
|----------|----------|
| [ObjC Interop](https://kotlinlang.org/docs/native-objc-interop.html) | Полная документация type mappings, annotations |
| [Swift Export](https://kotlinlang.org/docs/native-swift-export.html) | Experimental guide для прямого Swift экспорта |
| [C Interop](https://kotlinlang.org/docs/native-c-interop.html) | cinterop guide для C/ObjC библиотек |
| [ARC Integration](https://kotlinlang.org/docs/native-arc-integration.html) | Memory management на границе |

### Tools & Libraries

| Источник | Описание |
|----------|----------|
| [SKIE](https://skie.touchlab.co/) | Production-ready Swift enhancer |
| [KMP-NativeCoroutines](https://github.com/rickclephas/KMP-NativeCoroutines) | Coroutines для Swift |
| [Swift Interopedia](https://github.com/kotlin-hands-on/kotlin-swift-interopedia) | Примеры mappings |

### CS-фундамент

| Источник | Зачем |
|----------|-------|
| [[abi-calling-conventions]] | Понять почему нужен bridge |
| [[ffi-foreign-function-interface]] | Как работают биндинги |
| [[bridges-bindings-overview]] | Общая картина генераторов |

---

## Связь с другими темами

- **[[kmp-ios-deep-dive]]** — Interop — это механизм, через который Kotlin-код становится доступен в iOS-проекте. Понимание того, как XCFramework собирается, как CocoaPods/SPM доставляют framework в Xcode и как Swift импортирует Kotlin-модуль, является необходимым контекстом для осознанной работы с ObjC bridge, Swift Export и cinterop. Без этого знания ограничения interop кажутся случайными, а не следствиями архитектурных решений.

- **[[kmp-memory-management]]** — На границе Kotlin-Swift происходит критическое взаимодействие двух моделей памяти: GC и ARC. Каждый объект, пересекающий границу interop, требует корректного управления lifetime. Mixed retain cycles, autoreleasepool для interop-циклов и overhead коллекций (двойная конверсия List→NSArray→Array) — всё это проблемы на стыке interop и memory management.

- **[[kmp-expect-actual]]** — Механизм expect/actual и interop решают похожую задачу — доступ к платформенному коду — но на разных уровнях. expect/actual работает внутри Kotlin (между source sets), а interop — между Kotlin и Swift/ObjC. Часто они используются вместе: expect/actual для cinterop-биндингов, а ObjC bridge для экспорта результата в Swift. Понимание обоих механизмов позволяет выбрать правильный инструмент для каждой задачи.

## Источники и дальнейшее чтение

- Jemerov D., Isakova S. (2017). *Kotlin in Action.* — Главы о системе типов, generics и аннотациях Kotlin дают необходимый фундамент для понимания маппинга типов между Kotlin и ObjC/Swift. Ограничения generics в interop (T→T?) становятся понятнее, когда знаешь, как Kotlin обрабатывает type erasure и variance.

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive.* — Suspend-функции — ключевой элемент interop, поскольку их маппинг в Swift completionHandler/async/await определяет DX iOS-разработчиков. Книга объясняет внутреннее устройство suspend и CancellationException, что критично для понимания работы SKIE и правильного проектирования async API.

- Moskala M. (2021). *Effective Kotlin.* — Рекомендации по проектированию API (видимость, именование, default arguments) напрямую применимы к дизайну Kotlin-кода, экспортируемого в Swift. Помогает создавать API, которое будет удобно использовать по обе стороны границы interop.

---

*Проверено: 2026-01-09 | SKIE 0.9.3, Swift Export Experimental, Kotlin 2.1.21*
