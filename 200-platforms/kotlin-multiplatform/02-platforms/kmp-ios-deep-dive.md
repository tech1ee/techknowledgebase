---
title: "KMP iOS Deep Dive: Полный гайд по iOS интеграции"
created: 2026-01-03
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - topic/ios
  - topic/swift
  - swiftui
  - xcode
  - cocoapods
  - spm
  - skie
  - memory
  - type/deep-dive
  - level/advanced
related:
  - "[[kmp-overview]]"
  - "[[kmp-android-integration]]"
  - "[[kmp-expect-actual]]"
  - "[[compose-mp-ios]]"
prerequisites:
  - "[[kmp-getting-started]]"
  - "[[kmp-project-structure]]"
  - "[[kmp-expect-actual]]"
  - "[[kmp-android-integration]]"
cs-foundations:
  - "[[abi-calling-conventions]]"
  - "[[ffi-foreign-function-interface]]"
  - "[[bridges-bindings-overview]]"
  - "[[memory-model-fundamentals]]"
  - "[[garbage-collection-explained]]"
  - "[[reference-counting-arc]]"
status: published
reading_time: 36
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# KMP iOS Deep Dive

> **TL;DR:** iOS — полноценный Tier 1 target в KMP. Compose Multiplatform for iOS стал Stable в мае 2025 (1.8.0). Swift Export (экспериментальный) убирает Objective-C прослойку. SKIE улучшает Swift API (Flow → AsyncSequence, suspend → async/await). Новый memory model убрал freeze(). Интеграция через XCFramework: Direct, CocoaPods или SPM. Performance: startup сравним с native, scrolling on par с SwiftUI, +9 MB к размеру приложения.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **ABI & FFI** | Почему нужен ObjC bridge | [[abi-calling-conventions]], [[ffi-foreign-function-interface]] |
| **GC vs ARC** | Как работает память на границе | [[garbage-collection-explained]], [[reference-counting-arc]] |
| **Bridges & Bindings** | Как генерируются обёртки | [[bridges-bindings-overview]] |
| KMP Project Structure | Основы KMP | [[kmp-project-structure]] |
| Swift/SwiftUI | iOS фреймворки | [Swift.org](https://swift.org/documentation/) |

> **Рекомендация:** Для понимания ПОЧЕМУ iOS интеграция сложнее Android прочитай CS-фундамент об ABI/FFI и GC/ARC. Это объяснит архитектурные решения.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **XCFramework** | Универсальный бинарный формат для Apple | Чемодан с колёсами — подходит для любого типа путешествия |
| **Swift Export** | Новый способ экспорта Kotlin → Swift | Прямой перевод без посредника-переводчика |
| **SKIE** | Plugin для улучшения Swift API | Адаптер розетки — делает чужое совместимым |
| **cinterop** | Интеграция C/Obj-C библиотек | Таможня для импорта товаров |
| **BundledSQLiteDriver** | Встроенный SQLite для всех платформ | Универсальный ключ |
| **Freeze (deprecated)** | Старый механизм thread-safety | Замораживание продуктов (больше не нужно) |

---

## Теоретические основы

### Формальное определение

> **Foreign Function Interface (FFI)** — механизм, позволяющий коду, написанному на одном языке, вызывать функции, написанные на другом языке, через согласованный бинарный интерфейс (ABI) (Koenig, 1997).

Интеграция KMP с iOS основана на FFI через Objective-C bridge: Kotlin/Native генерирует ObjC headers, которые Swift импортирует через стандартный Apple interop.

### Теория двух моделей управления памятью

| Характеристика | Tracing GC (Kotlin/Native) | ARC (Swift/ObjC) |
|---------------|---------------------------|-------------------|
| Принцип | Периодическая трассировка графа объектов | Подсчёт ссылок при каждом присваивании |
| Обнаружение циклов | Автоматическое (mark-and-sweep) | Требует weak/unowned references |
| Предсказуемость | Паузы GC (stop-the-world) | Детерминированное освобождение |
| Overhead | Batch deallocation | Per-reference-count increment/decrement |
| Формализация | McCarthy, 1960 (Lisp GC) | Collins, 1960 (reference counting) |

### Эволюция iOS-интеграции в KMP

| Версия Kotlin | Год | Memory Model | Interop |
|--------------|-----|-------------|---------|
| 1.3 | 2018 | Strict (freeze required) | ObjC only |
| 1.6 | 2021 | New MM Preview | ObjC + experimental coroutines |
| 1.7 | 2022 | New MM Default | ObjC + KMP-NativeCoroutines |
| 2.0 | 2024 | Stable GC | ObjC + SKIE |
| 2.2 | 2025 | Optimized GC | Swift Export (experimental) |

### Формальная модель: ObjC Bridge как адаптер

ObjC bridge реализует паттерн **Adapter** (Gamma et al., 1994): каждый Kotlin-класс получает ObjC-обёртку с совместимым ABI. Потери при трансляции:

| Kotlin-конструкция | ObjC/Swift-представление | Потеря |
|-------------------|-------------------------|--------|
| `sealed class` | Обычный class hierarchy | Нет exhaustive switch |
| `suspend fun` | completionHandler | Нет async/await |
| `Flow<T>` | FlowCollector protocol | Нет AsyncSequence |
| `enum class` | NSString constants | Нет Swift enum |

SKIE и Swift Export решают эти потери на уровне кодогенерации — см. [[bridges-bindings-overview]] и [[ffi-foreign-function-interface]].


## Почему iOS сложнее Android

### Фундаментальные различия

На Android Kotlin работает в JVM — это "родная" среда. На iOS Kotlin компилируется в native code через LLVM, и взаимодействует со Swift/ObjC через FFI. Это создаёт несколько уровней сложности:

```
Android: Kotlin → JVM bytecode → Same runtime as Java
iOS:     Kotlin → LLVM IR → Native code → ObjC bridge → Swift
```

### Проблема двух memory моделей

| Аспект | Kotlin/Native | Swift |
|--------|--------------|-------|
| Memory management | Tracing GC | ARC (reference counting) |
| Deallocation | Периодически, batch | Немедленно, при каждом release |
| Retain cycles | GC справляется | Нужны weak references |
| Threading | GC safe-points | Thread-safe by design |

**Результат:** Объекты на границе Kotlin↔Swift живут по разным правилам. Mixed retain cycles не собираются автоматически.

### Проблема Objective-C bridge

Swift не имеет стабильного ABI для FFI. Objective-C — имеет. Поэтому Kotlin генерирует ObjC headers, которые Swift импортирует.

**Что теряется:**
- Kotlin `enum class` → ObjC class (не Swift enum)
- Kotlin `sealed class` → обычные classes (нет exhaustive switch)
- Kotlin `suspend fun` → completionHandler (не async/await)
- Kotlin generics: `T` → `T?` (nullable)

**Решения:**
- SKIE — добавляет Swift-native поведение
- Swift Export (experimental) — прямой экспорт без ObjC

### Сравнение developer experience

| Аспект | Android | iOS |
|--------|---------|-----|
| Debugging | Full support | Breakpoints OK, expression eval нет |
| IDE integration | Native (Android Studio) | Xcode plugin нужен |
| Build time | Быстрый (JVM bytecode) | Медленнее (LLVM) |
| Memory debugging | Studio Profiler | Instruments + signposts |
| Coroutines | Нативные | SKIE/KMP-NativeCoroutines |

### Почему это улучшается?

1. **Swift Export** (2026 stable goal) — прямой экспорт без ObjC
2. **SKIE** — уже сейчас делает Swift API нативным
3. **Compose MP для iOS** — stable, shared UI без Swift
4. **xcode-kotlin 2.0** — debugging в 5x быстрее
5. **KMP IDE Plugin** — cross-language navigation

---

## Статус iOS в KMP (январь 2026)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KMP iOS STATUS MATRIX                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Component                    Status        Notes                  │
│   ─────────────────────────────────────────────────────────         │
│   Kotlin/Native iOS            ✅ Stable     Tier 1 support         │
│   Compose Multiplatform iOS    ✅ Stable     Since May 2025 (1.8.0) │
│   Swift Export                 🧪 Experimental  K 2.2.20+           │
│   SKIE                         ✅ Stable     Touchlab plugin        │
│   XCFramework                  ✅ Stable     arm64, x86_64, sim     │
│   CocoaPods Integration        ✅ Stable     Gradle plugin          │
│   SPM Integration              ⚠️ Community  KMMBridge, spmForKmp   │
│   New Memory Model             ✅ Default    freeze() deprecated    │
│                                                                     │
│   Supported Architectures:                                          │
│   • iosArm64 (iPhone, iPad)                                         │
│   • iosSimulatorArm64 (M1/M2/M3 Mac simulators)                     │
│   • iosX64 (Intel Mac simulators)                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Методы интеграции iOS

### Обзор подходов

| Метод | Когда использовать | Сложность |
|-------|-------------------|-----------|
| **Direct Integration** | Монорепо, нет CocoaPods deps | Низкая |
| **CocoaPods (локальный)** | Есть CocoaPods зависимости | Средняя |
| **CocoaPods (remote)** | Распространение как pod | Высокая |
| **SPM (XCFramework)** | Современный Apple workflow | Средняя |

### Direct Integration (рекомендуется)

**Лучший выбор для:** проектов без CocoaPods зависимостей

**Как работает:**
1. Kotlin Multiplatform IDE plugin настраивает Xcode проект
2. Специальный скрипт в Build Phases компилирует Kotlin
3. Kotlin build становится частью iOS build

**build.gradle.kts:**

```kotlin
kotlin {
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "SharedKit"
            isStatic = true  // Рекомендуется для размера
        }
    }
}
```

**Xcode Build Phase Script:**

```bash
cd "$SRCROOT/.."
./gradlew :shared:embedAndSignAppleFrameworkForXcode
```

### CocoaPods Integration

**Лучший выбор для:** проектов с CocoaPods зависимостями

**build.gradle.kts:**

```kotlin
plugins {
    kotlin("multiplatform")
    kotlin("native.cocoapods")
}

kotlin {
    cocoapods {
        summary = "Shared KMP module"
        homepage = "https://example.com"
        version = "1.0"
        ios.deploymentTarget = "15.0"

        framework {
            baseName = "SharedKit"
            isStatic = true
        }

        // Импорт iOS зависимостей
        pod("Alamofire") {
            version = "~> 5.9"
        }
    }

    iosX64()
    iosArm64()
    iosSimulatorArm64()
}
```

**Podfile (iOS проект):**

```ruby
platform :ios, '15.0'

target 'MyiOSApp' do
  use_frameworks!

  pod 'SharedKit', :path => '../shared'
end
```

**Sync:**

```bash
# Из iOS директории
pod install
```

### Swift Package Manager (SPM)

**Лучший выбор для:** remote distribution, современный Apple workflow

**Вариант 1: spmForKmp Plugin**

```kotlin
plugins {
    kotlin("multiplatform")
    id("io.github.AaaBbb.spm-for-kmp") version "1.0.0"
}

kotlin {
    iosArm64()
    iosSimulatorArm64()

    spmForKmp {
        // Конфигурация SPM
    }
}
```

**Вариант 2: KMMBridge (Touchlab)**

```kotlin
plugins {
    kotlin("multiplatform")
    id("co.touchlab.kmmbridge") version "1.0.0"
}

kmmbridge {
    frameworkName = "SharedKit"
    spm()
}
```

**Package.swift (сгенерированный):**

```swift
// swift-tools-version:5.9
import PackageDescription

let package = Package(
    name: "SharedKit",
    platforms: [.iOS(.v15)],
    products: [
        .library(name: "SharedKit", targets: ["SharedKit"])
    ],
    targets: [
        .binaryTarget(
            name: "SharedKit",
            url: "https://example.com/SharedKit.xcframework.zip",
            checksum: "abc123..."
        )
    ]
)
```

---

## Compose Multiplatform на iOS

### Статус (Stable с мая 2025)

```
┌─────────────────────────────────────────────────────────────────────┐
│               COMPOSE MULTIPLATFORM iOS METRICS                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Performance:                                                      │
│   • Startup time: сравним с native                                  │
│   • Scrolling: on par с SwiftUI (даже ProMotion 120Hz)              │
│   • 96% разработчиков не сообщают о проблемах с performance         │
│                                                                     │
│   Size:                                                             │
│   • +9 MB к размеру iOS приложения                                  │
│   • Включает Skia renderer                                          │
│                                                                     │
│   Code Sharing:                                                     │
│   • Apps like The Respawn: 96% shared code                          │
│   • Forbes: 80%+ shared code                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Базовая структура

```kotlin
// commonMain/kotlin/App.kt
@Composable
fun App() {
    MaterialTheme {
        var count by remember { mutableStateOf(0) }

        Column(
            modifier = Modifier.fillMaxSize(),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            Text("Count: $count")
            Button(onClick = { count++ }) {
                Text("Increment")
            }
        }
    }
}
```

```kotlin
// iosMain/kotlin/MainViewController.kt
fun MainViewController() = ComposeUIViewController { App() }
```

```swift
// ContentView.swift
import SwiftUI
import SharedKit

struct ContentView: View {
    var body: some View {
        ComposeView()
            .ignoresSafeArea()
    }
}

struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
```

### SwiftUI ↔ Compose Interop

**Embed Compose в SwiftUI:**

```swift
// SwiftUI wrapper для Compose
struct ComposeViewWrapper: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        return MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}

// Использование в SwiftUI
struct MySwiftUIView: View {
    var body: some View {
        VStack {
            Text("SwiftUI Header")
            ComposeViewWrapper()
                .frame(height: 300)
            Text("SwiftUI Footer")
        }
    }
}
```

**Embed SwiftUI в Compose:**

```kotlin
// commonMain - expect declaration
@Composable
expect fun NativeMapView(modifier: Modifier)

// iosMain - actual с SwiftUI
@Composable
actual fun NativeMapView(modifier: Modifier) {
    UIKitView(
        factory = {
            // Создать MKMapView или обёртку SwiftUI
            MKMapView()
        },
        modifier = modifier
    )
}
```

---

## Swift Export (Experimental)

### Что это?

Swift Export позволяет экспортировать Kotlin код напрямую в Swift без Objective-C прослойки.

### Сравнение с Obj-C Export

| Аспект | Obj-C Export | Swift Export |
|--------|--------------|--------------|
| Размер кода | 175 строк | 28 строк |
| Nullable primitives | `KotlinInt` wrapper | `Int?` напрямую |
| Overloaded functions | Конфликты | Работают корректно |
| Package structure | Плоская | Сохраняется через enums |
| Статус | Stable | Experimental |

### Настройка

**build.gradle.kts:**

```kotlin
kotlin {
    iosArm64 {
        binaries.framework {
            baseName = "SharedKit"
        }
    }

    // Включить Swift Export
    swiftExport {
        moduleName = "SharedKit"
    }
}
```

**Xcode Build Phase (новый скрипт):**

```bash
cd "$SRCROOT/.."
# Вместо embedAndSignAppleFrameworkForXcode
./gradlew :shared:embedSwiftExportForXcode
```

### Ограничения Swift Export

- Experimental статус
- Не все Kotlin конструкции поддерживаются
- Coroutines/Flow требуют дополнительной работы

---

## SKIE — Swift Kotlin Interface Enhancer

### Что такое SKIE?

SKIE — Gradle plugin от Touchlab, который улучшает сгенерированный Swift API:
- Kotlin Flow → Swift AsyncSequence
- Kotlin suspend → Swift async/await
- Sealed classes → Swift enums с exhaustive checking

### Установка

**build.gradle.kts:**

```kotlin
plugins {
    kotlin("multiplatform")
    id("co.touchlab.skie") version "0.10.0"
}
```

### Примеры улучшений

**Без SKIE:**

```swift
// Использование Flow из Swift — сложно
class Observer: NSObject, FlowCollector {
    func emit(value: Any?, completionHandler: @escaping (Error?) -> Void) {
        // Handle value
        completionHandler(nil)
    }
}

viewModel.todosFlow.collect(collector: Observer()) { _ in }
```

**С SKIE:**

```swift
// Flow автоматически становится AsyncSequence
Task {
    for await todos in viewModel.todosFlow {
        // Нативный Swift синтаксис!
        updateUI(with: todos)
    }
}
```

**Suspend функции:**

```swift
// Без SKIE — callbacks
viewModel.loadData { result, error in
    // ...
}

// С SKIE — async/await
Task {
    let data = try await viewModel.loadData()
}
```

**Sealed classes:**

```kotlin
// Kotlin
sealed class Result<T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error<T>(val message: String) : Result<T>()
    class Loading<T> : Result<T>()
}
```

```swift
// Swift с SKIE — exhaustive switch
switch result {
case .success(let data):
    handleSuccess(data)
case .error(let message):
    handleError(message)
case .loading:
    showLoading()
}  // Нет default — compiler проверяет все cases
```

### SKIE Configuration

```kotlin
skie {
    features {
        // Отключить конкретные features
        group("co.touchlab.skie.features") {
            SealedInterop.enabled.set(false)
        }
    }

    analytics {
        enabled.set(false)  // Disable analytics
    }
}
```

---

## Memory Management

### Новый Memory Model (Default)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KOTLIN/NATIVE MEMORY MODEL                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   OLD MODEL (deprecated)         NEW MODEL (default)                │
│   ─────────────────────          ──────────────────                 │
│   • freeze() required            • No freeze() needed               │
│   • Strict thread isolation      • Shared objects freely            │
│   • InvalidMutabilityException   • Standard multithreading          │
│   • Complex coroutines           • Simple coroutines                │
│                                                                     │
│   Garbage Collector:                                                │
│   • Stop-the-world mark + concurrent sweep                          │
│   • No generational separation (пока)                               │
│   • Runs on separate thread                                         │
│   • Triggered by memory pressure or timer                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### freeze() — Deprecated

```kotlin
// OLD — больше не нужно!
val sharedData = MyData()
sharedData.freeze()  // ❌ Deprecated

// NEW — просто используйте
val sharedData = MyData()
// Можно использовать в любом потоке без freeze
```

### Мониторинг памяти

```kotlin
// Получить статистику последней GC
val gcInfo = kotlin.native.internal.GC.lastGCInfo()
println("GC duration: ${gcInfo?.pauseTime}")
println("Heap size: ${gcInfo?.memoryUsageAfter}")

// Принудительный запуск GC
kotlin.native.internal.GC.collect()

// Настройка GC
kotlin.native.internal.GC.threshold = 10_000_000  // bytes
```

### Debugging Memory Issues

**Xcode Instruments:**

1. Product → Profile (⌘I)
2. Choose "Allocations" template
3. Record app usage
4. Analyze memory graph

**VM Tracker:**
- Kotlin память помечена специальным идентификатором
- Можно отслеживать отдельно от Swift памяти

**Signposts для GC:**

```kotlin
// GC pauses видны в Instruments как signposts
// Позволяет коррелировать GC с UI freezes
```

### Предотвращение утечек

```swift
// iOS сторона — использовать autoreleasepool
autoreleasepool {
    for item in largeCollection {
        processKotlinObject(item)
    }
}
```

```kotlin
// Kotlin сторона — избегать долгоживущих references
class ViewModel {
    // ⚠️ Осторожно с callbacks из iOS
    private var onUpdate: ((String) -> Unit)? = null

    fun cleanup() {
        onUpdate = null  // Явная очистка
    }
}
```

---

## Debugging в Xcode

### Xcode Kotlin Plugin (Touchlab)

**Установка:**

```bash
# Через Homebrew
brew install xcode-kotlin

# Или вручную
git clone https://github.com/nicklockwood/xcode-kotlin
cd xcode-kotlin
./install.sh
```

**Возможности:**
- Breakpoints в Kotlin коде из Xcode
- Step through Kotlin code
- Inspect Kotlin variables
- Cross-language debugging

### LLDB команды для Kotlin

```lldb
# Показать Kotlin объект
(lldb) po kotlinObject

# Показать тип
(lldb) expr -l kotlin -- kotlinObject::class

# Вызвать Kotlin метод
(lldb) expr -l kotlin -- kotlinObject.someMethod()
```

### Crash Symbolication

**dSYM для Kotlin Native:**

```kotlin
kotlin {
    iosArm64 {
        binaries.framework {
            // Включить debug symbols
            freeCompilerArgs += listOf("-Xg0")
        }
    }
}
```

---

## Распространённые проблемы и решения

### 1. "Framework not found SharedKit"

**Причина:** Framework не собран или путь неверный

**Решение:**
```bash
# Проверить сборку
./gradlew :shared:linkDebugFrameworkIosSimulatorArm64

# Проверить путь в Xcode
# Build Settings → Framework Search Paths
```

### 2. "Class 'X' is not found"

**Причина:** Proguard/R8 удалил класс

**Решение (proguard-rules.pro):**
```
-keep class com.example.shared.** { *; }
```

### 3. Slow Build Times

**Решение (gradle.properties):**
```properties
kotlin.native.cacheKind.iosArm64=static
kotlin.native.cacheKind.iosSimulatorArm64=static
kotlin.native.cacheKind.iosX64=static
kotlin.incremental.native=true
```

### 4. "InvalidMutabilityException" (старые проекты)

**Причина:** Старая библиотека использует freeze

**Решение (gradle.properties):**
```properties
kotlin.native.binary.freezing=disabled
```

### 5. High Memory/CPU on iOS

**Причина:** Известная issue в некоторых версиях

**Решение:**
- Обновить до последней версии Kotlin
- Проверить GitHub issues
- Профилировать с Instruments

### 6. Coroutines не работают в background

**Причина:** Main dispatcher не сконфигурирован

**Решение:**
```kotlin
// Добавить зависимость
commonMain.dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")
}

iosMain.dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core-iosx64:1.8.0")
}
```

---

## Performance Best Practices

### Оптимизация размера бинарника

```kotlin
kotlin {
    iosArm64 {
        binaries.framework {
            isStatic = true  // Static linking — меньше размер

            // Strip debug symbols для release
            freeCompilerArgs += listOf(
                "-Xstrip-symbols"
            )
        }
    }
}
```

### Оптимизация startup

```kotlin
// Ленивая инициализация тяжёлых объектов
object AppDI {
    val database by lazy { createDatabase() }
    val networkClient by lazy { createHttpClient() }
}
```

### Compiler options для production

```kotlin
kotlin {
    targets.withType<KotlinNativeTarget> {
        binaries.all {
            freeCompilerArgs += listOf(
                "-opt-in=kotlin.RequiresOptIn",
                "-Xallocator=custom",  // Custom allocator
            )
        }

        binaries.framework {
            // Release optimizations
            if (buildType == RELEASE) {
                freeCompilerArgs += listOf("-Xstrip-symbols")
            }
        }
    }
}
```

---

## Кто использует KMP iOS в production

| Компания | Продукт | Результат |
|----------|---------|-----------|
| **Netflix** | Studio apps | 60% shared code, 12+ apps |
| **McDonald's** | Global app | Fewer crashes, better performance |
| **Google Docs** | iOS app | "KMP validated", on par performance |
| **Cash App** | Fintech | Shared business logic |
| **Philips** | Healthcare | Critical medical apps |
| **Forbes** | News | 80%+ shared code |
| **Airbnb** | Booking | 95% code sharing (2025) |
| **The Respawn** | Gaming | 96% shared code with Compose MP |

---

## Мифы и заблуждения

### Миф 1: "KMP на iOS — это второсортный опыт"

**Реальность:** iOS — Tier 1 target в KMP. Google Docs iOS использует KMP и показывает "on par or better" performance. Netflix использует в 12+ приложениях. Compose MP для iOS стал Stable. Developer experience улучшается каждый релиз.

### Миф 2: "SPM — лучший способ интеграции"

**Реальность:** SPM официально поддерживается, но имеет ограничения:
- Нельзя одновременно SPM зависимости и CocoaPods в shared module
- Требует дополнительных инструментов (KMMBridge)
- Для локальной разработки Touchlab рекомендует Direct linking

**Когда SPM:** remote distribution, уже используете SPM в проекте

### Миф 3: "Compose MP заменяет SwiftUI"

**Реальность:** Это разные подходы:
- **Compose MP**: shared UI, один код для всех платформ
- **SwiftUI + shared logic**: native UI, shared бизнес-логика

Оба валидны. Compose MP добавляет ~9 MB и Skia renderer. SwiftUI даёт 100% native look. Выбор зависит от приоритетов.

### Миф 4: "SKIE обязателен для production"

**Реальность:** SKIE сильно улучшает Swift API, но не обязателен. Без SKIE:
- Flow → FlowCollector protocol (работает, но verbose)
- Suspend → completionHandler (работает)
- Sealed → is/as checks (работает, но без exhaustive)

SKIE делает Swift код идиоматичным, но добавляет complexity в build.

### Миф 5: "iOS developers не могут работать с KMP"

**Реальность:** Современный workflow:
- xcode-kotlin для debugging в Xcode
- SKIE для native Swift API
- KMMBridge для SPM distribution
- IDE Plugin для navigation

iOS developers могут работать с KMP SDK как с любой другой Swift библиотекой.

### Миф 6: "Можно использовать несколько Kotlin frameworks"

**Реальность:** Нельзя. Два Kotlin-derived frameworks будут incompatible на binary level. Решение: umbrella module, объединяющий все shared модули в один XCFramework.

---

## Рекомендуемые источники

### CS-фундамент для глубокого понимания

| Материал | Зачем нужен |
|----------|-------------|
| [[abi-calling-conventions]] | Почему нужен ObjC bridge |
| [[ffi-foreign-function-interface]] | Как работает кросс-языковой вызов |
| [[bridges-bindings-overview]] | Типы интеграций: статические/динамические |
| [[garbage-collection-explained]] | Tracing GC в Kotlin/Native |
| [[reference-counting-arc]] | ARC в Swift/ObjC |
| [[memory-model-fundamentals]] | Threading и memory visibility |

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [iOS Integration Methods](https://kotlinlang.org/docs/multiplatform/multiplatform-ios-integration-overview.html) | Official | Методы интеграции |
| [Swift Export](https://kotlinlang.org/docs/native-swift-export.html) | Official | Новый Swift interop |
| [Memory Management](https://kotlinlang.org/docs/native-memory-manager.html) | Official | GC и память |
| [Compose MP iOS](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-multiplatform-ios.html) | Official | Compose на iOS |

### Инструменты

| Источник | Тип | Описание |
|----------|-----|----------|
| [SKIE](https://skie.touchlab.co/) | Plugin | Улучшенный Swift API |
| [KMMBridge](https://kmmbridge.touchlab.co/) | Tool | SPM/CocoaPods distribution |
| [Xcode Kotlin Plugin](https://github.com/nicklockwood/xcode-kotlin) | Plugin | Debugging в Xcode |

### Статьи и блоги

| Источник | Тип | Описание |
|----------|-----|----------|
| [Touchlab Blog](https://touchlab.co/blog) | Expert | iOS best practices |
| [Compose MP 1.8.0 Release](https://blog.jetbrains.com/kotlin/2025/05/compose-multiplatform-1-8-0-released-compose-multiplatform-for-ios-is-stable-and-production-ready/) | Official | iOS Stable announcement |
| [John O'Reilly](https://johnoreilly.dev/) | Blog | Practical KMP iOS |

---

## Связь с другими темами

**[[kmp-overview]]** — Обзор KMP объясняет общую архитектуру мультиплатформенных проектов, включая роль Kotlin/Native компилятора для iOS target. iOS является наиболее сложной платформой для интеграции из-за различий в memory model, concurrency и tooling. Понимание общей структуры KMP помогает правильно организовать iOS-специфичный код и expect/actual декларации.

**[[kmp-android-integration]]** — Сравнение Android и iOS интеграции выявляет ключевые различия платформ: Android работает на JVM с прямым доступом к Kotlin API, тогда как iOS требует Objective-C/Swift interop через фреймворки. Опыт Android-интеграции помогает понять, какие паттерны переносимы на iOS, а какие требуют платформенных адаптаций (SKIE, Swift Export).

**[[kmp-expect-actual]]** — Механизм expect/actual является основой платформенной абстракции в KMP и особенно важен для iOS. На iOS expect-декларации реализуются через iosMain source set с доступом к Foundation, UIKit и другим Apple-фреймворкам. Глубокое понимание expect/actual необходимо для создания iOS-нативных реализаций shared-интерфейсов.

**[[compose-mp-ios]]** — Compose Multiplatform для iOS предоставляет альтернативу нативному SwiftUI/UIKit для построения UI из shared-кода. Данный deep dive фокусируется на низкоуровневой интеграции (XCFramework, SKIE, memory management), тогда как compose-mp-ios описывает UI-слой поверх этого фундамента. Вместе они формируют полное понимание iOS-разработки в KMP.

## Источники и дальнейшее чтение

### Теоретические основы

- **McCarthy J. (1960).** *Recursive Functions of Symbolic Expressions.* — Теоретическая основа garbage collection, используемого в Kotlin/Native.
- **Collins G. (1960).** *A Method for Overlapping and Erasure of Lists.* — Reference counting, лежащий в основе ARC (Swift/ObjC).
- **Gamma E. et al. (1994).** *Design Patterns.* — ObjC bridge как реализация Adapter Pattern между Kotlin/Native и Swift runtime.

### Практические руководства

- **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* — Основа для понимания Kotlin-кода, компилируемого через Kotlin/Native в iOS frameworks.
- **Moskala M. (2022).** *Kotlin Coroutines: Deep Dive.* — Suspend-функции, Flow и их маппинг в Swift async/await через SKIE/KMP-NativeCoroutines.
- [SKIE Documentation](https://skie.touchlab.co/) — Инструмент для улучшения Kotlin→Swift interop.

---

## Проверь себя

> [!question]- Почему SKIE критически важен для iOS-разработчиков, работающих с KMP?
> Без SKIE Kotlin-код выглядит в Swift как Objective-C с неудобным API: sealed classes не маппятся в enums, Flow не становится AsyncSequence, корутины не превращаются в async/await. SKIE трансформирует Kotlin API в идиоматичный Swift, снижая сопротивление iOS-команды.

> [!question]- iOS-разработчик жалуется на retain cycle при использовании KMP-объекта в closure. Какова причина и решение?
> Kotlin/Native использует reference counting (ARC) на iOS. Если Swift closure захватывает KMP-объект, а KMP-объект ссылается на closure -- образуется retain cycle. Решение: использовать [weak self] в Swift closure или разрывать цикл через SKIE-преобразование Flow в AsyncSequence.

> [!question]- Почему для distribution KMP framework рекомендуется XCFramework, а не обычный .framework?
> XCFramework объединяет бинарники для нескольких архитектур (arm64 device, arm64 simulator, x86_64 simulator) в один пакет. Обычный .framework содержит одну архитектуру. Без XCFramework невозможно распространять universal framework через SPM или CocoaPods.

> [!question]- Почему Swift Export считается будущей заменой Objective-C interop в KMP?
> Текущий interop идёт через Objective-C bridge, что ограничивает маппинг типов (нет generics, нет Swift enums для sealed classes). Swift Export генерирует прямые Swift-биндинги без Objective-C промежуточного слоя, что даёт более нативный Swift API.

---

## Ключевые карточки

Как Kotlin/Native компилирует код для iOS?
?
Kotlin компилируется в LLVM IR, затем LLVM (встроенный в Xcode) генерирует native binary для ARM64 (device) или x86_64/ARM64 (simulator). Результат -- .framework, который iOS-проект импортирует как обычную нативную библиотеку.

Что делает SKIE (Swift-Kotlin Interface Enhancer)?
?
SKIE трансформирует Kotlin API в идиоматичный Swift: sealed classes в Swift enums, Flow в AsyncSequence, suspend functions в async/await, Kotlin nullability в Swift optionals. Устраняет основные проблемы ObjC interop.

Какие три способа интеграции KMP framework в iOS-проект?
?
Direct Integration (простейший, по умолчанию), CocoaPods (если проект уже использует Pods), SPM (для distribution). Для начала рекомендуется Direct Integration.

Как Kotlin/Native управляет памятью на iOS?
?
Kotlin/Native использует ARC-совместимый garbage collector с трассировкой циклов. Объекты Kotlin совместимы с Swift ARC. Потенциальные проблемы -- retain cycles при взаимных ссылках между Swift closures и Kotlin-объектами.

Что такое Swift Export и чем он отличается от текущего ObjC interop?
?
Экспериментальная фича, генерирующая прямые Swift-биндинги без Objective-C промежуточного слоя. Поддерживает Swift generics, enums, actors. Текущий interop через ObjC ограничивает маппинг типов.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-desktop-jvm]] | Desktop-платформа на JVM |
| Углубиться | [[kmp-interop-deep-dive]] | ObjC bridge, Swift Export, cinterop подробно |
| Смежная тема | [[kmp-memory-management]] | GC, ARC, retain cycles в KMP |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Compose Multiplatform 1.8.0, Kotlin 2.1.21, SKIE 0.10.0, Xcode 16*
