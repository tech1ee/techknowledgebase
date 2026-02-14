---
title: "KMP Troubleshooting: Решение типичных проблем"
created: 2026-01-04
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - troubleshooting
  - gradle
  - xcode
  - topic/ios
  - debugging
  - type/concept
  - level/advanced
related:
  - "[[kmp-production-checklist]]"
  - "[[kmp-debugging]]"
  - "[[kmp-ios-deep-dive]]"
  - "[[kmp-gradle-deep-dive]]"
prerequisites:
  - "[[kmp-debugging]]"
  - "[[kmp-gradle-deep-dive]]"
  - "[[kmp-ios-deep-dive]]"
cs-foundations:
  - root-cause-analysis
  - debugging-methodology
  - error-taxonomy
  - toolchain-complexity
status: published
reading_time: 30
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# KMP Troubleshooting

> **TL;DR:** Главные проблемы 2025-2026: Xcode 16 linker (exit code 138 → `-ld_classic`), AGP 9 миграция (`com.android.kotlin.multiplatform.library`), CrashKiOS crash on launch с dynamic frameworks. Expect/actual: default implementations только через interfaces. Memory: freeze() deprecated, new memory manager default. iOS: default arguments не работают через ObjC bridge, используй explicit overloads.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| KMP Basics | Понимание структуры проекта | [[kmp-project-structure]] |
| iOS Integration | iOS-специфичные проблемы | [[kmp-ios-deep-dive]] |
| Gradle Configuration | Build system issues | [[kmp-gradle-deep-dive]] |
| Debugging | Инструменты отладки | [[kmp-debugging]] |
| **CS: Root Cause Analysis** | Систематический debugging | [[cs-root-cause-analysis]] |

## Почему KMP troubleshooting сложнее single-platform?

**Toolchain Complexity:** KMP = Kotlin compiler + Gradle + Android toolchain + Xcode + LLVM + CocoaPods/SPM. Ошибка в одном месте может проявиться как cryptic message в другом. Exit code 138 — это SIGBUS от нового Xcode linker, но сообщение не говорит "use -ld_classic".

**Error Taxonomy:** Ошибки классифицируются по layer: Gradle sync → Kotlin compilation → iOS linking → Runtime. Понимание какой layer сломался = 80% решения. "Framework not found" может быть: wrong search path, wrong architecture, missing build step.

**Root Cause ≠ Symptom:** "App crash on launch" после добавления `-ld_classic` — это не проблема linker flag, а incompatibility CrashKiOS с dynamic frameworks. Без понимания layers вы будете чинить симптомы.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Exit code 138** | Xcode linker crash (SIGBUS) | Авария на сборочной линии |
| **ld_classic** | Старый Apple linker | Проверенный старый инструмент |
| **AGP 9** | Android Gradle Plugin 9.x | Новая версия сборщика |
| **Sync failure** | IDE не может загрузить проект | Компьютер не понимает инструкции |
| **dSYM** | Debug symbols для iOS | Словарь для расшифровки crash logs |

---

## Quick Diagnostics

```
┌─────────────────────────────────────────────────────────────┐
│              KMP PROBLEM DIAGNOSTICS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   СИМПТОМ                    →  ВЕРОЯТНАЯ ПРИЧИНА          │
│   ─────────────────────────────────────────────────────    │
│   Gradle sync failed          →  Версии, withJava()        │
│   Exit code 138               →  Xcode 16 linker           │
│   Framework not found         →  Search paths, архитектура │
│   App crash on launch         →  CrashKiOS, dynamic fw     │
│   expect/actual error         →  Default implementations   │
│   Memory leak iOS             →  Retain cycles, GC         │
│   Undefined symbols           →  Architecture mismatch     │
│   Pod install failed          →  CocoaPods config          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Gradle Issues

### 1.1 AGP 9 Sync Failure

**Симптом:**
```
Could not resolve all files for configuration
Plugin with id 'com.android.library' not found
```

**Причина:** AGP 9+ требует новый KMP plugin.

**Решение:**

```kotlin
// build.gradle.kts (module)

// ❌ OLD (deprecated in AGP 9)
plugins {
    kotlin("multiplatform")
    id("com.android.library")
}

// ✅ NEW (AGP 9+)
plugins {
    kotlin("multiplatform")
    id("com.android.kotlin.multiplatform.library")
}
```

```kotlin
// Также меняется configuration block:

// ❌ OLD
androidLibrary {
    compileSdk = 35
}

// ✅ NEW (AGP 8.12.0-alpha04+)
android {
    compileSdk = 35
}
```

**Таймлайн:**
- AGP 9.0 (Q4 2025): deprecated warnings
- AGP 10.0 (H2 2026): старый API удалён

---

### 1.2 withJava() Deprecation

**Симптом:**
```
'withJava()' is deprecated and should be removed
```

**Причина:** Kotlin 2.1.20+ создаёт Java source sets автоматически.

**Решение:**

```kotlin
// build.gradle.kts

kotlin {
    jvm {
        // ❌ REMOVE if Gradle 8.7+ and no Java plugins
        // withJava()

        // ✅ Keep only if you need Java plugin integration
        // withJava() // Only if using Java, Java Library, or Application plugin
    }
}
```

**Проверка:** Если не используете Java plugins - просто удалите `withJava()`.

---

### 1.3 CInterop Sync Failure

**Симптом:**
```
Task 'compileCommonMainKotlinMetadata' failed during sync
```

**Причина:** CInterop commonization запускает компиляцию при sync.

**Решение:**

```properties
# gradle.properties

# ❌ Causes sync issues
# kotlin.mpp.enableCInteropCommonization=true

# ✅ Disable during development, enable for CI
kotlin.mpp.enableCInteropCommonization=false
```

---

### 1.4 Java Test Fixtures Issue

**Симптом:**
```
Java test fixtures plugin not working
```

**Причина:** Kotlin 2.1.20 + Gradle 8.7+ bug.

**Решение:**
```properties
# gradle/libs.versions.toml

[versions]
kotlin = "2.1.21"  # Fixed in 2.1.21
```

---

### 1.5 Version Compatibility Matrix

```
┌─────────────────────────────────────────────────────────────┐
│              VERSION COMPATIBILITY (2026)                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Kotlin     Gradle      AGP         Status                 │
│   ────────────────────────────────────────────────────────  │
│   2.1.20     8.7+        8.x         ✅ Stable              │
│   2.1.21     8.7+        8.x         ✅ Fixes test fixtures │
│   2.2.x      8.11+       9.x         ⚠️ Beta (migration)    │
│                                                             │
│   ВАЖНО: AGP 9 требует новый KMP plugin!                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. iOS Build Errors

### 2.1 Xcode 16 Linker (Exit Code 138)

**Симптом:**
```
ld: Linking with a linker failed with exit code 138
ld: ignoring duplicate libraries: '-ldl', '-lobjc'
SIGBUS
```

**Причина:** Xcode 16 new linker incompatibility (KT-70202).

**Решение:**

```kotlin
// build.gradle.kts

kotlin {
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = "shared"

            // ✅ Fix for Xcode 16 linker
            linkerOpts("-ld_classic")
        }
    }
}
```

**Важно:** После добавления `-ld_classic` проверь запуск приложения - может быть crash с CrashKiOS.

---

### 2.2 CrashKiOS Launch Crash

**Симптом:**
```
App crashes immediately on launch after adding -ld_classic
EXC_BAD_ACCESS in CrashKiOS initialization
```

**Причина:** CrashKiOS 0.9.x несовместим с dynamic frameworks + `-ld_classic`.

**Решение:**

```kotlin
// Временно отключить CrashKiOS
// iosMain/kotlin/CrashReporter.kt

actual fun initCrashReporting() {
    // TODO: Re-enable when CrashKiOS fixes dynamic framework issue
    // See: https://github.com/nicklockwood/CrashKiOS/issues/69

    // CrashKiOS.configure() // Disabled temporarily
}
```

**Альтернатива:** Использовать static framework:

```kotlin
kotlin {
    iosTarget.binaries.framework {
        isStatic = true  // Static framework doesn't have the issue
    }
}
```

---

### 2.3 Framework Not Found

**Симптом:**
```
ld: framework not found shared
clang: error: linker command failed
```

**Решения:**

**1. Framework Search Paths:**
```
Xcode → Build Settings → Framework Search Paths:
$(SRCROOT)/../shared/build/xcode-frameworks/$(CONFIGURATION)/$(SDK_NAME)
```

**2. Build Active Architecture Only:**
```
Xcode → Build Settings → Build Active Architecture Only: Yes (Debug)
```

**3. Проверь embedAndSign script:**
```bash
# Build Phases → Run Script
cd "$SRCROOT/../shared"
./gradlew embedAndSignAppleFrameworkForXcode
```

**4. Используй .xcworkspace:**
```bash
# ❌ Wrong
open iosApp.xcodeproj

# ✅ Correct (if using CocoaPods)
open iosApp.xcworkspace
```

---

### 2.4 Architecture Mismatch

**Симптом:**
```
building for iOS Simulator-arm64 but attempting to link
with file built for iOS Simulator-x86_64
```

**Решение:**

```kotlin
// build.gradle.kts

kotlin {
    // Убедись что все архитектуры включены
    iosX64()           // Intel Mac simulator
    iosArm64()         // Device + M1/M2 simulator release
    iosSimulatorArm64() // M1/M2 simulator debug
}
```

**Xcode workaround:**
```
Build Settings → Excluded Architectures:
Debug → Any iOS Simulator SDK: arm64 (for Intel Mac)
```

---

### 2.5 SQLDelight Linker Error

**Симптом:**
```
Undefined symbols: _sqlite3_open, _sqlite3_close
```

**Решение:**
```
Xcode → Build Settings → Other Linker Flags:
-lsqlite3
```

---

## 3. Expect/Actual Errors

### 3.1 Default Implementation Error

**Симптом:**
```
Expect declaration with body is not allowed
Expected declaration must not have a body
```

**Причина:** expect classes не могут иметь реализации.

**❌ Неправильно:**
```kotlin
// commonMain
expect class DataProvider {
    fun getData(): String = "default"  // ❌ Error!
}
```

**✅ Правильно (через interface):**
```kotlin
// commonMain
interface DataProviderInterface {
    fun getData(): String = "default"  // ✅ Interface can have default
}

expect class DataProvider() : DataProviderInterface

// androidMain
actual class DataProvider actual constructor() : DataProviderInterface {
    override fun getData(): String = "Android: ${super.getData()}"
}

// iosMain
actual class DataProvider actual constructor() : DataProviderInterface {
    // Uses default implementation automatically
}
```

---

### 3.2 Actual Not Found

**Симптом:**
```
Expected class 'Foo' has no actual declaration in module
```

**Checklist:**

```kotlin
// 1. Проверь package
// commonMain: com.example.shared.Foo
// iosMain: com.example.shared.Foo  // ✅ Same package!

// 2. Проверь source set hierarchy
kotlin {
    sourceSets {
        commonMain.dependencies { }
        iosMain.dependsOn(commonMain)  // ✅ Hierarchy correct
    }
}

// 3. Проверь actual keyword
actual class Foo  // ✅ Not just "class Foo"
```

---

### 3.3 iOS Default Arguments Issue

**Симптом:** Swift не видит default arguments из Kotlin.

**Причина:** ObjC bridge не поддерживает default arguments.

**❌ Проблема:**
```kotlin
// commonMain
fun fetchUser(id: String, includeDetails: Boolean = true): User
```

```swift
// Swift - default argument NOT available
user = fetchUser(id: "123") // ❌ Error: missing argument
```

**✅ Решение (overloads):**
```kotlin
// commonMain
fun fetchUser(id: String, includeDetails: Boolean): User
fun fetchUser(id: String): User = fetchUser(id, true)
```

```swift
// Swift - works!
user = fetchUser(id: "123") // ✅ Uses overload
```

**Будущее:** Swift Export (Kotlin 2.2.20+) решит эту проблему.

---

### 3.4 Generics Limitation

**Симптом:**
```
Type argument is not reified
Generic type information erased
```

**Причина:** ObjC не поддерживает generics полностью.

**Workaround:**
```kotlin
// ❌ Problem: generic type erased
expect fun <T> parseJson(json: String): T

// ✅ Solution: concrete types
expect fun parseUserJson(json: String): User
expect fun parseProductJson(json: String): Product

// Или с type parameter в class
expect class JsonParser<T>(type: KClass<T>) {
    fun parse(json: String): T
}
```

---

## 4. Memory Issues

### 4.1 Freeze Deprecation Errors

**Симптом:**
```
freeze() is deprecated and does nothing
InvalidMutabilityException
```

**Решение:** Просто удали freeze():

```kotlin
// ❌ OLD (deprecated)
val data = sharedData.freeze()

// ✅ NEW (just use directly)
val data = sharedData  // Works with new memory manager
```

**Проверка memory manager:**
```kotlin
// Должен быть true в новых проектах
println(kotlin.native.isExperimentalMM())  // true = new MM
```

---

### 4.2 iOS Memory Leak

**Симптом:** Память растёт, не освобождается.

**Диагностика:**
```kotlin
// Проверь GC stats
fun checkMemory() {
    val info = kotlin.native.internal.GC.lastGCInfo
    println("Heap: ${info?.memoryUsageBefore} → ${info?.memoryUsageAfter}")
}

// Force GC
kotlin.native.internal.GC.collect()
```

**Типичные причины:**

```kotlin
// 1. Mixed retain cycles
class SwiftDelegate { /* holds Kotlin object */ }
class KotlinManager(val delegate: SwiftDelegate) { /* holds Swift object */ }
// ❌ Cycle: Kotlin → Swift → Kotlin - NOT collected!

// ✅ Solution: weak reference on one side (in Swift)
weak var kotlinManager: KotlinManager?

// 2. Long-running loops without autoreleasepool
fun processImages(images: List<NSData>) {
    images.forEach { image ->
        // ❌ Memory accumulates
        processImage(image)
    }
}

// ✅ Solution: autoreleasepool
fun processImages(images: List<NSData>) {
    images.forEach { image ->
        autoreleasepool {
            processImage(image)
        }  // Memory released here
    }
}
```

---

### 4.3 UIImage Memory Growth

**Симптом:** Передача UIImage между Kotlin и Swift вызывает memory spikes.

**Решение:**
```kotlin
// ❌ Don't hold UIImage references in Kotlin
class ImageCache {
    private val images = mutableMapOf<String, UIImage>()  // ❌ Leak prone
}

// ✅ Use native caching or convert immediately
class ImageCache {
    private val imageData = mutableMapOf<String, ByteArray>()  // ✅ Kotlin types
}

// ✅ Or process immediately without storing
fun processImage(image: UIImage): Result {
    val result = analyzeImage(image)
    // Let Swift handle UIImage lifecycle
    return result
}
```

---

### 4.4 iOS Extension Memory Limits

**Симптом:** iOS kills network extension (50MB limit).

**Решение:**
```kotlin
// gradle.properties

# Reduce startup memory
kotlin.native.binary.pagedAllocator=false

# Smaller strings
kotlin.native.binary.latin1Strings=true
```

```kotlin
// Force GC more aggressively in extensions
fun periodicCleanup() {
    kotlin.native.internal.GC.collect()
    kotlin.native.internal.GC.collectCyclic()
}
```

---

## 5. CocoaPods Issues

### 5.1 Pod Install Failed

**Симптом:**
```
[!] Unable to find a specification for 'shared'
```

**Checklist:**

```bash
# 1. Generate podspec
./gradlew :shared:podspec

# 2. Check podspec exists
ls shared/build/cocoapods/podspec/shared.podspec

# 3. Clean and reinstall
cd iosApp
rm -rf Pods Podfile.lock
pod install --repo-update

# 4. Check Podfile path
cat Podfile | grep shared
# Should be: pod 'shared', :path => '../shared'
```

---

### 5.2 Static vs Dynamic Framework

**Симптом:**
```
'shared' requires dynamic framework
Library not loaded: @rpath/shared.framework
```

**Решение:**

```kotlin
// build.gradle.kts
cocoapods {
    framework {
        baseName = "shared"
        isStatic = true  // или false, но consistent!
    }
}
```

```ruby
# Podfile - должен соответствовать
use_frameworks! :linkage => :static  # если isStatic = true
# или
use_frameworks!  # если isStatic = false (dynamic)
```

---

### 5.3 Pod Version Mismatch

**Симптом:**
```
The sandbox is not in sync with the Podfile.lock
```

**Решение:**
```bash
# Clean everything
cd iosApp
rm -rf Pods Podfile.lock
rm -rf ~/Library/Caches/CocoaPods

# Rebuild shared framework
cd ..
./gradlew :shared:podspec

# Reinstall pods
cd iosApp
pod install
```

---

## 6. SPM Issues

### 6.1 SPM Package Resolution Failed

**Симптом:**
```
Failed to resolve dependencies
Package.swift not found
```

**Setup:**

```kotlin
// build.gradle.kts
kotlin {
    iosTarget.binaries.framework {
        baseName = "shared"
        isStatic = false
    }
}

// XCFramework task
tasks.register("buildXCFramework") {
    dependsOn("assembleXCFramework")
}
```

```bash
# Generate XCFramework
./gradlew assembleXCFramework

# Check output
ls shared/build/XCFrameworks/release/shared.xcframework
```

---

### 6.2 SPM Binary Target Issues

**Package.swift:**
```swift
// Package.swift
let package = Package(
    name: "SharedKit",
    platforms: [.iOS(.v14)],
    products: [
        .library(name: "SharedKit", targets: ["shared"])
    ],
    targets: [
        .binaryTarget(
            name: "shared",
            path: "./shared.xcframework"  // ✅ Local path
            // или
            // url: "https://...",        // Remote URL
            // checksum: "..."            // Required for remote
        )
    ]
)
```

---

## 7. CI/CD Issues

### 7.1 iOS Build Fails on CI

**Симптом:** Локально работает, на CI падает.

**Checklist:**

```yaml
# GitHub Actions
- name: Setup Xcode
  uses: maxim-lobanov/setup-xcode@v1
  with:
    xcode-version: '16.0'  # Match local version!

- name: Accept Xcode License
  run: sudo xcodebuild -license accept

- name: Install CocoaPods
  run: |
    gem install cocoapods
    cd iosApp && pod install

- name: Build Framework
  run: |
    ./gradlew :shared:linkDebugFrameworkIosSimulatorArm64
  env:
    JAVA_HOME: ${{ env.JAVA_HOME_17_X64 }}
```

---

### 7.2 Gradle Daemon Memory

**Симптом:**
```
GC overhead limit exceeded
Gradle build daemon disappeared
```

**Решение:**
```properties
# gradle.properties
org.gradle.jvmargs=-Xmx6g -XX:+UseParallelGC -XX:MaxMetaspaceSize=1g
org.gradle.daemon=true
org.gradle.caching=true
org.gradle.parallel=true

# For CI specifically
org.gradle.daemon=false  # Disable daemon on CI
```

---

## 8. Quick Reference

### Error Message → Solution

```
┌─────────────────────────────────────────────────────────────┐
│              QUICK FIX REFERENCE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ERROR MESSAGE                  SOLUTION                   │
│   ─────────────────────────────────────────────────────    │
│   exit code 138                  linkerOpts("-ld_classic") │
│   framework not found            Check search paths         │
│   withJava() deprecated          Remove if Gradle 8.7+      │
│   freeze() deprecated            Just remove it             │
│   actual not found               Check package, source set  │
│   pod install failed             pod install --repo-update  │
│   sandbox not in sync            rm Pods && pod install     │
│   -lsqlite3 undefined           Add to Other Linker Flags  │
│   architecture mismatch          Check EXCLUDED_ARCHS       │
│   memory leak                    autoreleasepool, weak refs │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Useful Commands

```bash
# Clean everything
./gradlew clean
rm -rf ~/.gradle/caches
rm -rf build
rm -rf */build

# iOS specific clean
cd iosApp
rm -rf Pods Podfile.lock
rm -rf ~/Library/Developer/Xcode/DerivedData/*

# Check Kotlin version
./gradlew kotlinVersion

# Check dependencies
./gradlew :shared:dependencies

# Build specific target
./gradlew :shared:linkDebugFrameworkIosArm64
./gradlew :shared:linkReleaseFrameworkIosArm64
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Clean build решает все проблемы" | Clean = workaround. Если помогло — найди root cause, иначе повторится |
| "Stack Overflow/Google достаточно" | KMP меняется быстро. SO ответы 2023 года могут не работать в 2025 |
| "iOS ошибки = проблема Kotlin" | Часто проблема в Xcode settings, CocoaPods config, или Apple toolchain |
| "AGP 9 сломает всё" | Migration guide существует. Главное — менять plugin ID вовремя |
| "Если работает локально — работает везде" | CI environment отличается: Xcode version, caches, permissions |

## CS-фундамент

| Концепция | Применение в Troubleshooting |
|-----------|----------------------------|
| Root Cause Analysis | Отличай symptom от причины (exit code 138 ≠ bad code) |
| Error Taxonomy | Классифицируй по layer: Gradle/Kotlin/Linking/Runtime |
| Toolchain Complexity | Понимай зависимости: Kotlin→LLVM→Xcode→ld |
| Debugging Methodology | Изолируй проблему: minimal repro, binary search |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [KMP Compatibility Guide](https://kotlinlang.org/docs/multiplatform/multiplatform-compatibility-guide.html) | Official | Breaking changes |
| [Known Issues - Android Studio](https://developer.android.com/studio/known-issues) | Official | IDE issues |
| [Kotlin Slack #multiplatform](https://kotlinlang.slack.com/) | Community | Real-time help |
| [YouTrack KMP Issues](https://youtrack.jetbrains.com/issues/KT?q=Multiplatform) | Official | Bug tracker |
| [Touchlab Blog](https://touchlab.co/blog) | Expert | iOS-specific issues |

---

## Связь с другими темами

- **[[kmp-production-checklist]]** — Troubleshooting часто возникает при подготовке к production. Проблемы из чеклиста (dSYM не загружен, crash reporting не работает, CI падает) имеют конкретные решения, описанные здесь. Чеклист говорит «настрой crash reporting», а troubleshooting объясняет, почему CrashKiOS крашится с dynamic framework и как это исправить через static framework или временное отключение.

- **[[kmp-debugging]]** — Debugging и troubleshooting — две стороны одной медали. Debugging — это проактивный процесс поиска багов в коде, а troubleshooting — реактивное решение проблем окружения и toolchain. Инструменты пересекаются: LLDB, xcode-kotlin, KDoctor используются и для отладки, и для диагностики. Понимание root cause analysis из debugging помогает систематически решать проблемы, а не применять workarounds.

- **[[kmp-ios-deep-dive]]** — Большинство проблем в KMP troubleshooting связаны с iOS: exit code 138 (Xcode linker), framework not found, architecture mismatch, CocoaPods/SPM issues. Глубокое понимание iOS-интеграции позволяет не просто применять fix из таблицы, а понимать причину: почему новый Xcode 16 linker несовместим, почему нужен `-ld_classic`, почему static и dynamic frameworks ведут себя по-разному.

- **[[kmp-gradle-deep-dive]]** — Gradle-проблемы (AGP 9 sync failure, withJava() deprecation, daemon memory) составляют отдельную категорию troubleshooting. Понимание Gradle internals — task graph, configuration phase, dependency resolution — позволяет диагностировать проблемы сборки на уровне причин, а не симптомов. Version compatibility matrix (Kotlin + Gradle + AGP) — ключевой инструмент превентивного troubleshooting.

## Источники и дальнейшее чтение

- Moskala M. (2021). *Effective Kotlin.* — Многие проблемы в troubleshooting (freeze deprecated, generics limitation, default arguments на iOS) связаны с неправильным использованием языковых конструкций Kotlin. Книга помогает писать код, который изначально избегает типичных ловушек expect/actual, nullable generics и exception handling.

- Jemerov D., Isakova S. (2017). *Kotlin in Action.* — Фундаментальное понимание компиляции Kotlin (JVM bytecode vs Native machine code), системы типов и interop с Java необходимо для диагностики ошибок компиляции и линковки. Когда вы понимаете, что Kotlin/Native проходит через LLVM, exit code 138 (SIGBUS от линкера) обретает логический смысл.

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive.* — Проблемы с freeze() и InvalidMutabilityException (старая memory model) связаны с многопоточностью корутин. Книга объясняет, почему новая memory model убрала freeze, как Dispatchers взаимодействуют с потоками и почему Dispatchers.Main не работает в unit tests без мока.

---

## Проверь себя

> [!question]- Вы получаете ошибку "Framework not found Shared" при сборке iOS в Xcode. Какие шаги диагностики?
> 1) Проверить, что ./gradlew :shared:linkDebugFrameworkIosSimulatorArm64 успешен, 2) Проверить Framework Search Paths в Xcode Build Settings, 3) Clean Build Folder в Xcode, 4) Проверить Direct Integration / CocoaPods конфигурацию, 5) Убедиться что target architecture совпадает (arm64 vs x86_64).

> [!question]- Gradle sync зависает на 5+ минут в KMP-проекте. Какие причины и решения?
> Причины: слишком много targets, buildSrc invalidation, network issues при resolve dependencies. Решения: convention plugins вместо buildSrc, configuration cache, offline mode для dev, отключение ненужных targets, проверка proxy/firewall.

> [!question]- Почему "Unresolved reference" в commonMain при использовании platform API -- самая частая ошибка новичков?
> Новички пытаются использовать java.io.File или UIKit в commonMain, не понимая правил видимости source sets. commonMain видит только Kotlin stdlib и multiplatform-библиотеки. Platform API доступен только в platform source sets.

---

## Ключевые карточки

Какие категории проблем чаще всего возникают в KMP?
?
Gradle (sync, build, dependencies), Xcode (framework not found, signing, architecture mismatch), Memory (leaks, retain cycles на iOS), Linker (duplicate symbols, missing symbols), Kotlin/Native (slow compilation, large binary).

Как диагностировать Gradle-проблемы в KMP?
?
./gradlew --info для verbose output, ./gradlew dependencies для dependency tree, ./gradlew --scan для build scan (performance analysis), --no-build-cache для исключения cache issues, --stacktrace для full error.

Как решить "Duplicate symbols" при линковке iOS framework?
?
Обычно вызвано экспортом одной библиотеки из нескольких модулей. Решение: убрать дубликаты из export() в umbrella module, использовать isStatic = true для static linking, проверить transitive dependencies.

Как решить проблемы с Xcode и KMP framework?
?
Clean Build Folder (Cmd+Shift+K), пересобрать framework (./gradlew linkDebugFramework...), проверить Framework Search Paths, убедиться в совпадении architecture (arm64 simulator vs device), обновить Xcode и CocoaPods.

Как диагностировать memory leaks в KMP iOS?
?
Xcode Instruments -> Leaks, Memory Graph Debugger для визуализации retain cycles, Kermit logging для отслеживания object lifecycle, CrashKiOS для crash traces. Искать циклы Swift closure -> Kotlin object -> callback.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-getting-started]] | Вернуться к основам при необходимости |
| Углубиться | [[kmp-debugging]] | Продвинутые инструменты отладки |
| Смежная тема | [[kmp-gradle-deep-dive]] | Детальное решение Gradle-проблем |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Kotlin 2.1.x, Xcode 16, AGP 8.x/9.x*
