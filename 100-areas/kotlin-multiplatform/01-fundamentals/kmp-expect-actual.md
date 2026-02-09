---
title: "expect/actual: Платформо-зависимый код в KMP"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - expect-actual
  - platform-specific
  - type/concept
  - level/beginner
related:
  - "[[kmp-project-structure]]"
  - "[[kmp-source-sets]]"
  - "[[kmp-getting-started]]"
cs-foundations:
  - "[[type-systems-theory]]"
  - "[[compilation-pipeline]]"
  - "[[polymorphism-fundamentals]]"
  - "[[oop-abstraction-patterns]]"
status: published
---

# expect/actual: мост между платформами

> **TL;DR:** expect объявляет "контракт" в common коде, actual предоставляет реализацию для каждой платформы. Правила: одинаковое имя + один package + expect без реализации. Работает для functions, properties, objects, classes (Beta), enums, annotations. typealias маппит на существующие platform types. Best practice: предпочитать interfaces + DI когда возможно, expect/actual только для low-level platform access.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **KMP Project Structure** | Понимание source sets и targets | [[kmp-project-structure]] |
| **Kotlin basics** | Классы, функции, интерфейсы | [[kotlin-overview]] |
| **Type systems** | Понимание type checking и contracts | [[type-systems-theory]] |
| **Polymorphism** | Как разные реализации подходят под один интерфейс | [[polymorphism-fundamentals]] |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|----------|---------------------|
| **expect** | Объявление того, что нужно от платформы | **Заказ в ресторане** — "мне нужно блюдо X" |
| **actual** | Реализация для конкретной платформы | **Приготовленное блюдо** — как именно повар это сделал |
| **Contract** | Контракт между common и platform кодом | **Договор** — обе стороны знают обязательства |
| **typealias** | Псевдоним для существующего типа | **Никнейм** — другое имя для того же человека |
| **Platform API** | API специфичное для платформы (Android SDK, iOS UIKit) | **Местные законы** — действуют только в этой стране |
| **Factory function** | Функция создающая объект | **Производственная линия** — выдаёт готовые изделия |
| **Intermediate source set** | Source set между common и platform | **Региональный офис** — между главным и местными |

---

## Почему expect/actual устроен именно так

### Фундаментальная проблема: платформенный полиморфизм

В традиционных языках **полиморфизм** достигается через:
- Interfaces / Abstract classes (runtime dispatch)
- Generics (compile-time parametric polymorphism)

Но **кросс-платформенная разработка** добавляет новое измерение:

```
                    Traditional OOP               KMP expect/actual
                    ─────────────────             ─────────────────
Полиморфизм:       Runtime (vtable)              Compile-time (per-target)

                   interface Storage              expect class Storage
                        ↓                              ↓ (компилятор)
                   ┌────┴────┐                    ┌────┴────┬────────┐
                   │         │                    │         │        │
               FileStorage  CloudStorage      Android    iOS     Desktop
                   ↓         ↓                actual     actual   actual
              (одна JVM)   (одна JVM)        (JVM)     (Native) (JVM)

Выбор:          Runtime      Runtime          Compile-time (per platform)
```

**expect/actual — это compile-time platform polymorphism.**

### Почему не просто interfaces

Interfaces работают **внутри одного runtime**. Но проблема:

```kotlin
// Проблема: Android Context НЕ существует на iOS

interface Storage {
    fun save(data: String)
}

// Android implementation нужен Context
class AndroidStorage(context: Context) : Storage { ... }

// iOS implementation нужен NSUserDefaults
class IOSStorage() : Storage { ... }

// Как создать в common коде?
fun commonCode() {
    val storage: Storage = ???  // Откуда взять Context или NSUserDefaults?
}
```

**expect/actual решает это:**

```kotlin
// commonMain — объявляем ЧТО нужно
expect fun createStorage(): Storage

// androidMain — КОМПИЛЯТОР знает что этот код для Android
actual fun createStorage(): Storage {
    return AndroidStorage(applicationContext)  // Context доступен на Android
}

// iosMain — КОМПИЛЯТОР знает что этот код для iOS
actual fun createStorage(): Storage {
    return IOSStorage()  // NSUserDefaults доступен на iOS
}
```

### Связь с type system

**expect** — это **type signature без implementation**:

```
expect fun f(): T
        ↓
Компилятор гарантирует:
1. ВСЕ targets имеют actual с СОВМЕСТИМОЙ сигнатурой
2. Нельзя вызвать expect без actual
3. Type checking происходит в compile-time
```

Это похоже на **abstract methods** в OOP, но на уровне **всей compilation unit**.

### Почему typealias работает

**typealias** — это **structural type equivalence**:

```kotlin
// commonMain
expect class AtomicInt(value: Int) {
    fun get(): Int
    fun incrementAndGet(): Int
}

// jvmMain
actual typealias AtomicInt = java.util.concurrent.atomic.AtomicInteger
```

Это работает потому что:
1. `AtomicInteger` имеет constructor с `Int`
2. `AtomicInteger` имеет методы `get()` и `incrementAndGet()`
3. Type system подтверждает **structural compatibility**

> **CS-фундамент:** Детали в [[type-systems-theory]] (contracts, structural typing) и [[polymorphism-fundamentals]] (compile-time vs runtime dispatch).

---

## Концепция expect/actual

### Как это работает

```
┌─────────────────────────────────────────────────────────────┐
│                    EXPECT/ACTUAL FLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  commonMain:                                                │
│  ┌────────────────────────────────────────────┐            │
│  │ expect fun getPlatformName(): String       │            │
│  │                                            │            │
│  │ // Использование в common коде:            │            │
│  │ fun greet() = "Hello from ${getPlatformName()}"        │
│  └────────────────────────────────────────────┘            │
│                          │                                  │
│            ┌─────────────┼─────────────┐                   │
│            ▼             ▼             ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ androidMain  │ │   iosMain    │ │   jvmMain    │       │
│  ├──────────────┤ ├──────────────┤ ├──────────────┤       │
│  │actual fun    │ │actual fun    │ │actual fun    │       │
│  │getPlatform   │ │getPlatform   │ │getPlatform   │       │
│  │Name() =      │ │Name() =      │ │Name() =      │       │
│  │"Android"     │ │"iOS"         │ │"JVM"         │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Главные правила

```kotlin
// ═══════════════════════════════════════════════════════════
// ПРАВИЛО 1: expect в common, actual в platform source sets
// ═══════════════════════════════════════════════════════════

// commonMain/kotlin/Platform.kt
expect fun getPlatformName(): String  // ✅ expect в common

// androidMain/kotlin/Platform.android.kt
actual fun getPlatformName(): String = "Android"  // ✅ actual в platform

// ═══════════════════════════════════════════════════════════
// ПРАВИЛО 2: Одинаковое имя и один package
// ═══════════════════════════════════════════════════════════

// commonMain/kotlin/com/example/Platform.kt
package com.example
expect fun getPlatformName(): String

// androidMain/kotlin/com/example/Platform.android.kt
package com.example  // ✅ Тот же package
actual fun getPlatformName(): String = "Android"

// ═══════════════════════════════════════════════════════════
// ПРАВИЛО 3: expect НИКОГДА не содержит реализацию
// ═══════════════════════════════════════════════════════════

// ❌ НЕПРАВИЛЬНО — реализация в expect
expect fun getPlatformName(): String = "Default"

// ✅ ПРАВИЛЬНО — expect абстрактен
expect fun getPlatformName(): String

// ═══════════════════════════════════════════════════════════
// ПРАВИЛО 4: actual для КАЖДОЙ платформы
// ═══════════════════════════════════════════════════════════

// Если объявлены targets: android, ios, jvm
// То нужны actual в: androidMain, iosMain, jvmMain
// Компилятор выдаст ошибку если пропустить хотя бы один
```

---

## Синтаксис для разных конструкций

### expect/actual Functions

```kotlin
// ═══════════════════════════════════════════════════════════
// SIMPLE FUNCTION
// ═══════════════════════════════════════════════════════════

// commonMain
expect fun getPlatformName(): String

// androidMain
actual fun getPlatformName(): String =
    "Android ${android.os.Build.VERSION.SDK_INT}"

// iosMain
import platform.UIKit.UIDevice
actual fun getPlatformName(): String =
    UIDevice.currentDevice.systemName() + " " +
    UIDevice.currentDevice.systemVersion

// jvmMain
actual fun getPlatformName(): String =
    "JVM ${System.getProperty("java.version")}"

// ═══════════════════════════════════════════════════════════
// FUNCTION WITH PARAMETERS
// ═══════════════════════════════════════════════════════════

// commonMain
expect fun formatDate(timestamp: Long, pattern: String): String

// androidMain
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

actual fun formatDate(timestamp: Long, pattern: String): String {
    val sdf = SimpleDateFormat(pattern, Locale.getDefault())
    return sdf.format(Date(timestamp))
}

// iosMain
import platform.Foundation.*

actual fun formatDate(timestamp: Long, pattern: String): String {
    val formatter = NSDateFormatter().apply {
        dateFormat = pattern
    }
    val date = NSDate.dateWithTimeIntervalSince1970(timestamp / 1000.0)
    return formatter.stringFromDate(date)
}
```

### expect/actual Properties

```kotlin
// commonMain
expect val isDebug: Boolean
expect val appVersion: String

// androidMain
actual val isDebug: Boolean = BuildConfig.DEBUG
actual val appVersion: String = BuildConfig.VERSION_NAME

// iosMain
actual val isDebug: Boolean = Platform.isDebugBinary
actual val appVersion: String =
    NSBundle.mainBundle.objectForInfoDictionaryKey("CFBundleShortVersionString") as String
```

### expect/actual Objects

```kotlin
// commonMain
expect object Logger {
    fun log(message: String)
    fun error(message: String, throwable: Throwable? = null)
}

// androidMain
import android.util.Log

actual object Logger {
    actual fun log(message: String) {
        Log.d("App", message)
    }

    actual fun error(message: String, throwable: Throwable?) {
        Log.e("App", message, throwable)
    }
}

// iosMain
actual object Logger {
    actual fun log(message: String) {
        println("[INFO] $message")
    }

    actual fun error(message: String, throwable: Throwable?) {
        println("[ERROR] $message: ${throwable?.message}")
    }
}
```

### expect/actual Classes (Beta)

```kotlin
// ⚠️ ВАЖНО: Classes в Beta, требуют compiler flag
// gradle.properties или build.gradle.kts:
// kotlin.compilerOptions.freeCompilerArgs.add("-Xexpect-actual-classes")

// commonMain
expect class UUID() {
    fun generateString(): String
}

// androidMain
actual class UUID {
    private val uuid = java.util.UUID.randomUUID()

    actual fun generateString(): String = uuid.toString()
}

// iosMain
import platform.Foundation.NSUUID

actual class UUID {
    private val uuid = NSUUID()

    actual fun generateString(): String = uuid.UUIDString
}
```

### expect/actual с typealias

```kotlin
// ═══════════════════════════════════════════════════════════
// TYPEALIAS — маппинг на существующие platform types
// ═══════════════════════════════════════════════════════════

// commonMain
expect class AtomicInt(value: Int) {
    fun get(): Int
    fun set(value: Int)
    fun incrementAndGet(): Int
}

// jvmMain — используем java.util.concurrent
actual typealias AtomicInt = java.util.concurrent.atomic.AtomicInteger

// nativeMain — используем kotlin.native.concurrent
actual typealias AtomicInt = kotlin.native.concurrent.AtomicInt

// ═══════════════════════════════════════════════════════════
// TYPEALIAS для Enum
// ═══════════════════════════════════════════════════════════

// commonMain
expect enum class Month {
    JANUARY, FEBRUARY, MARCH, APRIL, MAY, JUNE,
    JULY, AUGUST, SEPTEMBER, OCTOBER, NOVEMBER, DECEMBER
}

// jvmMain
actual typealias Month = java.time.Month
```

### expect/actual Annotations

```kotlin
// commonMain
@Target(AnnotationTarget.CLASS)
@Retention(AnnotationRetention.RUNTIME)
expect annotation class Serializable()

// jvmMain — маппим на java.io.Serializable
actual typealias Serializable = java.io.Serializable

// iosMain — нет serializable, создаём пустую
actual annotation class Serializable
```

---

## Практические паттерны

### Pattern 1: Factory Function + Interface

**Лучший паттерн для большинства случаев:**

```kotlin
// ═══════════════════════════════════════════════════════════
// COMMONMAIN — interface + expect factory
// ═══════════════════════════════════════════════════════════

// commonMain/kotlin/storage/KeyValueStorage.kt
package storage

interface KeyValueStorage {
    fun getString(key: String, default: String = ""): String
    fun putString(key: String, value: String)
    fun getInt(key: String, default: Int = 0): Int
    fun putInt(key: String, value: Int)
    fun clear()
}

expect fun createKeyValueStorage(): KeyValueStorage

// Использование в common коде:
class UserPreferences(
    private val storage: KeyValueStorage = createKeyValueStorage()
) {
    var theme: String
        get() = storage.getString("theme", "light")
        set(value) = storage.putString("theme", value)

    var fontSize: Int
        get() = storage.getInt("fontSize", 16)
        set(value) = storage.putInt("fontSize", value)
}

// ═══════════════════════════════════════════════════════════
// ANDROIDMAIN — SharedPreferences implementation
// ═══════════════════════════════════════════════════════════

// androidMain/kotlin/storage/KeyValueStorage.android.kt
package storage

import android.content.Context
import android.content.SharedPreferences

class AndroidKeyValueStorage(
    private val prefs: SharedPreferences
) : KeyValueStorage {

    override fun getString(key: String, default: String): String =
        prefs.getString(key, default) ?: default

    override fun putString(key: String, value: String) {
        prefs.edit().putString(key, value).apply()
    }

    override fun getInt(key: String, default: Int): Int =
        prefs.getInt(key, default)

    override fun putInt(key: String, value: Int) {
        prefs.edit().putInt(key, value).apply()
    }

    override fun clear() {
        prefs.edit().clear().apply()
    }
}

// Нужен context — используем Application context через DI
lateinit var applicationContext: Context

actual fun createKeyValueStorage(): KeyValueStorage {
    val prefs = applicationContext.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
    return AndroidKeyValueStorage(prefs)
}

// ═══════════════════════════════════════════════════════════
// IOSMAIN — UserDefaults implementation
// ═══════════════════════════════════════════════════════════

// iosMain/kotlin/storage/KeyValueStorage.ios.kt
package storage

import platform.Foundation.NSUserDefaults

class IOSKeyValueStorage : KeyValueStorage {
    private val defaults = NSUserDefaults.standardUserDefaults

    override fun getString(key: String, default: String): String =
        defaults.stringForKey(key) ?: default

    override fun putString(key: String, value: String) {
        defaults.setObject(value, forKey = key)
    }

    override fun getInt(key: String, default: Int): Int =
        defaults.integerForKey(key).toInt()

    override fun putInt(key: String, value: Int) {
        defaults.setInteger(value.toLong(), forKey = key)
    }

    override fun clear() {
        val domain = NSBundle.mainBundle.bundleIdentifier ?: return
        defaults.removePersistentDomainForName(domain)
    }
}

actual fun createKeyValueStorage(): KeyValueStorage = IOSKeyValueStorage()
```

### Pattern 2: Dependency Injection с expect/actual

```kotlin
// ═══════════════════════════════════════════════════════════
// KOIN DI — platform-specific modules
// ═══════════════════════════════════════════════════════════

// commonMain
import org.koin.core.module.Module

expect val platformModule: Module

// Общие модули
val commonModule = module {
    single { UserRepository(get()) }
    single { AuthService(get()) }
}

// androidMain
import io.ktor.client.engine.okhttp.OkHttp
import org.koin.dsl.module

actual val platformModule: Module = module {
    single { OkHttp.create() }  // HTTP engine для Android
    single { AndroidKeyValueStorage(get()) as KeyValueStorage }
    single { AndroidLogger() as Logger }
}

// iosMain
import io.ktor.client.engine.darwin.Darwin
import org.koin.dsl.module

actual val platformModule: Module = module {
    single { Darwin.create() }  // HTTP engine для iOS
    single { IOSKeyValueStorage() as KeyValueStorage }
    single { IOSLogger() as Logger }
}

// Использование
fun initKoin() {
    startKoin {
        modules(commonModule, platformModule)
    }
}
```

### Pattern 3: Platform Context

```kotlin
// ═══════════════════════════════════════════════════════════
// PLATFORM CONTEXT — для platform-specific initialization
// ═══════════════════════════════════════════════════════════

// commonMain
expect class PlatformContext

expect fun initializePlatform(context: PlatformContext)

class AppInitializer(private val context: PlatformContext) {
    fun initialize() {
        initializePlatform(context)
        // Common initialization...
    }
}

// androidMain
actual typealias PlatformContext = android.content.Context

actual fun initializePlatform(context: PlatformContext) {
    // Android-specific initialization
    applicationContext = context.applicationContext
}

// iosMain
actual class PlatformContext  // Пустой класс для iOS

actual fun initializePlatform(context: PlatformContext) {
    // iOS-specific initialization
}
```

---

## expect/actual vs Interfaces

### Когда использовать expect/actual

```
┌─────────────────────────────────────────────────────────────┐
│              КОГДА ИСПОЛЬЗОВАТЬ EXPECT/ACTUAL                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Доступ к platform APIs (Context, UIDevice, etc.)        │
│  ✅ Разные типы на разных платформах (typealias)           │
│  ✅ Singleton objects (Logger, Config)                      │
│  ✅ Compile-time проверка наличия реализаций               │
│  ✅ Low-level platform access (native libraries)           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Когда использовать Interfaces + DI

```
┌─────────────────────────────────────────────────────────────┐
│              КОГДА ИСПОЛЬЗОВАТЬ INTERFACES + DI              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Нужно несколько реализаций (mock для тестов)           │
│  ✅ Реализация может меняться runtime                       │
│  ✅ Нужна инъекция зависимостей                            │
│  ✅ Loose coupling architecture                             │
│  ✅ A/B testing разных реализаций                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Сравнение

```kotlin
// ═══════════════════════════════════════════════════════════
// APPROACH 1: Pure expect/actual (менее гибко)
// ═══════════════════════════════════════════════════════════

// commonMain
expect object Analytics {
    fun trackEvent(name: String, params: Map<String, Any>)
}

// androidMain
actual object Analytics {
    actual fun trackEvent(name: String, params: Map<String, Any>) {
        Firebase.analytics.logEvent(name, bundleOf(*params.toList().toTypedArray()))
    }
}

// Проблема: нельзя подменить для тестов!

// ═══════════════════════════════════════════════════════════
// APPROACH 2: Interface + DI (более гибко) ✅ РЕКОМЕНДУЕТСЯ
// ═══════════════════════════════════════════════════════════

// commonMain
interface Analytics {
    fun trackEvent(name: String, params: Map<String, Any>)
}

expect fun createAnalytics(): Analytics

// androidMain
class FirebaseAnalytics : Analytics {
    override fun trackEvent(name: String, params: Map<String, Any>) {
        Firebase.analytics.logEvent(name, bundleOf(*params.toList().toTypedArray()))
    }
}

actual fun createAnalytics(): Analytics = FirebaseAnalytics()

// Теперь легко подменить для тестов:
class FakeAnalytics : Analytics {
    val events = mutableListOf<Pair<String, Map<String, Any>>>()

    override fun trackEvent(name: String, params: Map<String, Any>) {
        events.add(name to params)
    }
}
```

---

## Типичные ошибки

### 1. Реализация в expect

```kotlin
// ❌ НЕПРАВИЛЬНО
expect fun calculate(): Int {
    return 42  // Нельзя! expect всегда abstract
}

// ✅ ПРАВИЛЬНО
expect fun calculate(): Int
// actual implementations provide the logic
```

### 2. Разные packages

```kotlin
// ❌ НЕПРАВИЛЬНО
// commonMain/kotlin/com/example/utils/Platform.kt
package com.example.utils
expect fun getPlatform(): String

// androidMain/kotlin/com/example/Platform.kt
package com.example  // Другой package!
actual fun getPlatform(): String = "Android"

// ✅ ПРАВИЛЬНО — одинаковый package
package com.example.utils
actual fun getPlatform(): String = "Android"
```

### 3. Пропущенный actual

```kotlin
// commonMain
expect fun doSomething()

// androidMain
actual fun doSomething() { /* ... */ }

// iosMain
// Забыли actual!

// ❌ Ошибка компиляции:
// "Expected function 'doSomething' has no actual declaration in module..."
```

### 4. Неправильные constructor arguments в expect class

```kotlin
// ❌ НЕПРАВИЛЬНО — разные конструкторы
// commonMain
expect class Logger(tag: String)

// androidMain
actual class Logger(
    tag: String,
    context: Context  // Дополнительный аргумент — не сработает!
) { ... }

// ✅ ПРАВИЛЬНО — используем factory function
// commonMain
interface Logger { ... }
expect fun createLogger(tag: String): Logger

// androidMain — context передаётся иначе
actual fun createLogger(tag: String): Logger =
    AndroidLogger(tag, applicationContext)
```

### 5. expect class вместо interface

```kotlin
// ❌ МЕНЕЕ ГИБКО
expect class UserRepository {
    fun getUser(id: String): User
}

// ✅ БОЛЕЕ ГИБКО — interface + factory
interface UserRepository {
    fun getUser(id: String): User
}

expect fun createUserRepository(): UserRepository
```

---

## Intermediate Source Sets

```kotlin
// ═══════════════════════════════════════════════════════════
// ACTUAL В INTERMEDIATE SOURCE SET
// ═══════════════════════════════════════════════════════════

// Если iosX64, iosArm64, iosSimulatorArm64 имеют одинаковую реализацию,
// достаточно одного actual в iosMain

// commonMain
expect fun getDeviceId(): String

// iosMain — один actual для всех iOS targets
import platform.UIKit.UIDevice

actual fun getDeviceId(): String =
    UIDevice.currentDevice.identifierForVendor?.UUIDString ?: "unknown"

// НЕ нужно дублировать в iosX64Main, iosArm64Main, iosSimulatorArm64Main!
```

---

## Кто использует и реальные примеры

| Компания | Паттерн | Применение |
|----------|---------|------------|
| **Ktor** | expect/actual для HTTP engines | OkHttp (Android), Darwin (iOS), CIO (JVM) |
| **SQLDelight** | expect/actual для SqlDriver | AndroidSqliteDriver, NativeSqliteDriver |
| **Koin 4.1+** | expect val для platform modules | KoinMultiplatformApplication |
| **Cash App** | Interface + DI | Testable architecture |

---

## Мифы и заблуждения о expect/actual

### ❌ "expect/actual — это замена interfaces"

**Реальность:** Это **дополнение**, не замена. expect/actual для **compile-time platform selection**, interfaces для **runtime polymorphism**.

```kotlin
// Используйте ВМЕСТЕ:
interface Analytics { ... }           // Для testability
expect fun createAnalytics(): Analytics  // Для platform selection
```

### ❌ "expect class лучше чем expect fun + interface"

**Реальность:** `expect class` (Beta) **менее гибкий**:
- Нельзя создать mock для тестов
- Нельзя иметь несколько реализаций
- Сложнее dependency injection

**Best practice:** `interface + expect factory function`.

### ❌ "Нужен actual в каждом target source set"

**Реальность:** actual можно определить в **intermediate source set**:

```kotlin
// commonMain
expect fun getDeviceId(): String

// iosMain — один actual для ВСЕХ iOS targets
actual fun getDeviceId(): String = UIDevice.currentDevice.identifierForVendor
// Работает для iosArm64, iosX64, iosSimulatorArm64
```

### ❌ "typealias всегда лучше actual class"

**Реальность:** typealias требует **exact structural compatibility**:

```kotlin
// ✅ Работает — AtomicInteger имеет нужные методы
actual typealias AtomicInt = java.util.concurrent.atomic.AtomicInteger

// ❌ НЕ работает — если platform type не имеет нужных методов
actual typealias MyDate = NSDate  // NSDate не имеет тех же методов!
```

### ❌ "expect/actual добавляет runtime overhead"

**Реальность:** **Нулевой runtime overhead**. expect/actual — это compile-time механизм:
- Компилятор подставляет actual на этапе компиляции
- В runtime нет dispatch, нет vtable lookup
- Как если бы вы написали platform code напрямую

### ❌ "Можно использовать default implementation в expect"

**Реальность:** **Невозможно**. expect всегда abstract:

```kotlin
// ❌ Compilation error
expect fun getPlatform(): String = "Default"

// ✅ Если нужен default — используйте wrapper
expect fun getPlatformImpl(): String

fun getPlatform(): String = getPlatformImpl().ifEmpty { "Unknown" }
```

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Expected/Actual Declarations](https://kotlinlang.org/docs/multiplatform/multiplatform-expect-actual.html) | Official Doc | Полная документация |
| [Touchlab - Expect/Actuals](https://touchlab.co/expect-actuals-statements-kotlin-multiplatform) | Expert Blog | 5-минутный гайд |
| [ProAndroidDev - Expect/Actual Explained](https://proandroiddev.com/expect-actual-mechanism-in-kotlin-multiplatform-explained-a91e7d85af4e) | Blog | Практические примеры |
| [Koin Multiplatform](https://insert-koin.io/docs/reference/koin-mp/kmp/) | Official Doc | DI с expect/actual |

### CS-фундамент

| Концепция | Материал | Почему важно |
|-----------|----------|--------------|
| Type Systems | [[type-systems-theory]] | Contracts, structural compatibility |
| Polymorphism | [[polymorphism-fundamentals]] | Compile-time vs runtime dispatch |
| Compilation | [[compilation-pipeline]] | Per-target code generation |
| Abstraction | [[oop-abstraction-patterns]] | Interface vs implementation |

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, expect classes в Beta*
