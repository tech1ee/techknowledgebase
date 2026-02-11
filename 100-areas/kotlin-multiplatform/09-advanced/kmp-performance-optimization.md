---
title: "KMP Performance Optimization: Build, Size, Runtime"
created: 2026-01-04
modified: 2026-01-04
tags:
  - topic/jvm
  - topic/kmp
  - performance
  - k2
  - native
  - build-time
  - type/concept
  - level/advanced
related:
  - "[[kmp-gradle-deep-dive]]"
  - "[[kmp-memory-management]]"
  - "[[kmp-debugging]]"
prerequisites:
  - "[[kmp-gradle-deep-dive]]"
  - "[[kmp-memory-management]]"
  - "[[kmp-ios-deep-dive]]"
cs-foundations:
  - "[[compilation-pipeline]]"
  - "[[native-compilation-llvm]]"
  - "[[cpu-architecture-basics]]"
  - "[[memory-model-fundamentals]]"
status: published
---

# KMP Performance Optimization

> **TL;DR:** Три области оптимизации: build time (K2 даёт до 94% ускорения, linkDebug* вместо build), binary size (embedBitcode=DISABLE, limit exposed interface, dead_strip), runtime (value classes, sequences, tailrec, platform-specific hot paths). Google Docs iOS на KMP показывает "on par or better" производительность vs native Swift. Профилируй перед оптимизацией.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Compilation Pipeline** | Понять что оптимизируем | [[compilation-pipeline]] |
| **Native/LLVM** | Как работает K/N компиляция | [[native-compilation-llvm]] |
| **CPU & Cache** | Почему inline важен | [[cpu-architecture-basics]] |
| KMP Architecture | Как устроен KMP | [[kmp-project-structure]] |
| Gradle Configuration | Build система | [[kmp-gradle-deep-dive]] |

> **Совет:** Понимание compilation pipeline поможет осознанно выбирать между Debug/Release и понять почему K2 быстрее.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **K2 Compiler** | Новый компилятор Kotlin 2.0+ | Двигатель V8 после V6 — быстрее, мощнее |
| **Value Class** | Inline класс без object allocation | Подарочная обёртка, которая исчезает — внутри голый подарок |
| **Dead Code Elimination** | Удаление неиспользуемого кода | Уборка квартиры — выбрасываем ненужное |
| **Incremental Compilation** | Компиляция только изменений | Перепечатать только страницу с ошибкой, не всю книгу |
| **Bitcode** | Промежуточное представление Apple | Черновик перед чистовиком — можно убрать |
| **Inlining** | Вставка тела функции в место вызова | Копипаста рецепта вместо ссылки на книгу |

---

## Почему production важна оптимизация

### Проблема build time

Kotlin/Native компилирует в machine code через LLVM. Это даёт native performance, но compilation медленнее чем JVM bytecode:

```
Kotlin/JVM:   Source → Bytecode (быстро)
Kotlin/Native: Source → IR → LLVM IR → Machine Code (медленно)
```

**Факт:** Release build в 10x медленнее Debug из-за LLVM оптимизаций. Команда сидит и ждёт. Developer experience страдает.

**K2 решение:** Новый frontend компилятора (analysis phase) в 2-4x быстрее. Это не ускоряет LLVM, но сокращает frontend overhead.

### Проблема binary size

Каждый public class в Kotlin = ObjC adapter + metadata в binary. Типичная библиотека:
- kotlinx-serialization: +3 MB
- Ktor Client: +13 MB
- SQLDelight: +2 MB

**Факт:** KMP binary = Kotlin runtime + LLVM compiled code + ObjC adapters. Это больше чем чистый Swift.

### Проблема runtime

Kotlin/Native GC имеет stop-the-world pauses. Value classes помогают избежать allocation. Sequences помогают избежать intermediate collections. Inline functions убирают call overhead.

**Google Docs результат:** "on par or better" vs native Swift после оптимизаций. Это возможно, но требует понимания.

### Trade-offs

| Оптимизация | Выигрыш | Цена |
|-------------|---------|------|
| Debug builds | 10x быстрее компиляция | Медленнее runtime |
| Value classes | 0 allocations | Boxing при generics/nullable |
| Sequences | Меньше памяти | Overhead для маленьких коллекций |
| inline | Быстрее вызов | Больше code size |

---

## Три области оптимизации

```
┌─────────────────────────────────────────────────────────────┐
│                KMP PERFORMANCE TRIANGLE                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                    BUILD TIME                               │
│                        △                                    │
│                       /│\                                   │
│                      / │ \                                  │
│                     /  │  \                                 │
│                    /   │   \                                │
│                   /    │    \                               │
│                  /     │     \                              │
│   BINARY SIZE ◁───────┼───────▷ RUNTIME                    │
│                        │                                    │
│                                                             │
│   Build Time: K2, caching, debug builds                     │
│   Binary Size: dead code, bitcode, exposed API              │
│   Runtime: value classes, sequences, algorithms             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Build Time Optimization

### K2 Compiler Performance

```
┌─────────────────────────────────────────────────────────────┐
│              K2 COMPILER BENCHMARKS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Clean Build (Anki-Android):                               │
│   K1: ████████████████████████████████ 57.7s                │
│   K2: ████████████████ 29.7s (-49%)                         │
│                                                             │
│   Initialization Phase:                                     │
│   K1: ███████████████████████████ 0.126s                    │
│   K2: █ 0.022s (-83%, 488% faster)                          │
│                                                             │
│   Analysis Phase:                                           │
│   K1: ██████████████████████████████ 0.581s                 │
│   K2: ██████ 0.122s (-79%, 376% faster)                     │
│                                                             │
│   IDE Highlighting:                                         │
│   K1: ████████████████████████████████ baseline             │
│   K2: ████████████████████ 1.8x faster                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Gradle Configuration

```properties
# gradle.properties — ОБЯЗАТЕЛЬНЫЕ настройки

# === Memory ===
org.gradle.jvmargs=-Xmx6g -XX:+UseParallelGC

# === Parallelization ===
org.gradle.parallel=true
org.gradle.workers.max=8  # CPU cores - 2

# === Caching ===
org.gradle.caching=true
org.gradle.configuration-cache=true

# === Kotlin/Native ===
kotlin.incremental.native=true  # Experimental
kotlin.native.cacheKind=static

# === НЕ ДОБАВЛЯЙ (устаревшее) ===
# kotlin.native.disableCompilerDaemon=true  # ПЛОХО
# kotlin.native.cacheKind=none              # ПЛОХО
```

### Debug vs Release Builds

```kotlin
// ПРАВИЛЬНО: используй Debug для разработки
// tasks linkDebug* вместо build или assemble

// В Gradle: проверь что не запускаются Release tasks
// ./gradlew :shared:linkDebugFrameworkIosSimulatorArm64

// Release builds в 10x медленнее из-за оптимизаций!
// Используй только для production сборок
```

```
┌─────────────────────────────────────────────────────────────┐
│              DEBUG vs RELEASE BUILD TIME                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Debug:   ████████ ~2 min                                  │
│   Release: ████████████████████████████████████████ ~20 min │
│                                                             │
│   Правило: Release только перед публикацией!                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Specific Task Selection

```bash
# ПЛОХО: собирает всё
./gradlew build
./gradlew assemble

# ХОРОШО: только нужное
./gradlew :shared:linkDebugFrameworkIosSimulatorArm64

# Для Xcode (iOS)
./gradlew :shared:embedAndSignAppleFrameworkForXcode

# Проверка что собирается
./gradlew :shared:tasks | grep link
```

### Caching ~/.konan

```bash
# ~/.konan содержит Kotlin/Native toolchain (~1GB+)
# Обязательно кэшировать в CI!

# GitHub Actions
- name: Cache Kotlin/Native
  uses: actions/cache@v4
  with:
    path: ~/.konan
    key: konan-${{ runner.os }}-${{ hashFiles('**/*.gradle*') }}

# Кастомная локация
# gradle.properties
kotlin.data.dir=/custom/path/konan
```

### Windows Optimization

```powershell
# Windows Defender замедляет Kotlin/Native
# Добавь исключение:

# PowerShell (Admin)
Add-MpPreference -ExclusionPath "$env:USERPROFILE\.konan"

# Или через Windows Security:
# Settings → Virus & threat protection → Exclusions → Add
# Path: %USERPROFILE%\.konan
```

---

## 2. Binary Size Optimization

### Framework Size Reality

```
┌─────────────────────────────────────────────────────────────┐
│              iOS FRAMEWORK SIZE BREAKDOWN                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Minimum "Hello World":    ~6 MB (release, single arch)    │
│   + Ktor Client:            +13 MB → ~19 MB                 │
│   + SQLDelight:             +2 MB  → ~21 MB                 │
│   + kotlinx-serialization:  +3 MB  → ~24 MB                 │
│                                                             │
│   Final IPA на устройстве:                                  │
│   - Bare minimum: ~500 KB                                   │
│   - Typical app: 2-5 MB                                     │
│                                                             │
│   Важно: смотри финальный IPA, не disk framework!           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Disable Bitcode (iOS 16+)

```kotlin
// build.gradle.kts
kotlin {
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = "Shared"

            // Bitcode deprecated since iOS 16
            // Экономит ~3 MB
            embedBitcode = BitcodeEmbeddingMode.DISABLE
        }
    }
}
```

### Dead Code Stripping

```kotlin
// build.gradle.kts
kotlin {
    iosArm64().binaries.framework {
        // Удаляет неиспользуемый код
        freeCompilerArgs += listOf(
            "-Xbinary=strip=true",       // Strip debug symbols
        )

        // Linker options
        linkerOpts += listOf(
            "-dead_strip",               // Remove unused code
            "-ObjC",                     // Required for Obj-C interop
        )
    }
}
```

### Limit Exposed Interface

```kotlin
// ПРОБЛЕМА: каждый public class = Obj-C adapter в binary

// shared/src/commonMain/kotlin/domain/User.kt
// ПЛОХО: всё public
data class User(
    val id: String,
    val name: String,
    val email: String,
    val settings: UserSettings,
    val preferences: UserPreferences,
    // ... 20 properties
)

// ХОРОШО: только нужное для iOS
// shared/src/commonMain/kotlin/domain/User.kt
data class User(
    val id: String,
    val name: String,
    val email: String,
    internal val settings: UserSettings,      // internal = не в Obj-C
    internal val preferences: UserPreferences // internal = не в Obj-C
)

// Для iOS создай специальный API layer
// shared/src/iosMain/kotlin/api/UserApi.kt
class UserApi(private val user: User) {
    val id: String get() = user.id
    val displayName: String get() = user.name
    // Только нужные iOS поля
}
```

### Umbrella Framework Pattern

```kotlin
// Для multi-module проектов: один framework для iOS
// Предотвращает дублирование зависимостей

// umbrella/build.gradle.kts
kotlin {
    iosArm64().binaries.framework {
        baseName = "Umbrella"

        // Включаем все модули
        export(project(":shared:core"))
        export(project(":shared:network"))
        export(project(":shared:database"))

        // Не используй transitiveExport — замедляет компиляцию!
        // transitiveExport = true  // ПЛОХО
    }
}
```

---

## 3. Runtime Performance

### Value Classes (Zero-Cost Abstractions)

```kotlin
// ПРОБЛЕМА: wrapper class создаёт объект
data class UserId(val value: String)  // Object allocation каждый раз

// РЕШЕНИЕ: value class — zero allocation
@JvmInline
value class UserId(val value: String)

// Компилируется в:
// fun getUser(userId: String) — голый String, без wrapper

// Использование
fun getUser(userId: UserId): User {
    return repository.findById(userId.value)
}

val user = getUser(UserId("123"))  // Никакого объекта UserId!
```

```
┌─────────────────────────────────────────────────────────────┐
│              VALUE CLASS vs DATA CLASS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   data class UserId(val value: String)                      │
│   ────────────────────────────────────                      │
│   Memory: █████ Object + String reference                   │
│   GC:     ██████ Needs garbage collection                   │
│                                                             │
│   @JvmInline value class UserId(val value: String)          │
│   ────────────────────────────────────────────────          │
│   Memory: ██ Just the String itself                         │
│   GC:     █ No extra allocation                             │
│                                                             │
│   Performance: 2-3x faster in tight loops                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### When Value Classes Get Boxed

```kotlin
// Boxing происходит в этих случаях:

// 1. Nullable types
val userId: UserId? = null  // Boxed!

// 2. Generic types (без specialization)
fun <T> process(item: T) {}
process(UserId("123"))  // Boxed!

// 3. When stored as Any
val any: Any = UserId("123")  // Boxed!

// ПРАВИЛО: value classes лучше всего в type-safe APIs
// и performance-critical non-nullable contexts
```

### Sequences vs Collections

```kotlin
// ПРОБЛЕМА: промежуточные коллекции
val result = users
    .filter { it.isActive }    // Создаёт List
    .map { it.name }           // Создаёт List
    .take(10)                  // Создаёт List
    .toList()                  // 3 промежуточных списка!

// РЕШЕНИЕ: Sequences для больших коллекций
val result = users.asSequence()
    .filter { it.isActive }    // Lazy
    .map { it.name }           // Lazy
    .take(10)                  // Lazy
    .toList()                  // Только 1 список в конце

// Sequences выгодны когда:
// - 10,000+ элементов
// - Есть early termination (take, first, find)
// - Несколько трансформаций подряд
```

```
┌─────────────────────────────────────────────────────────────┐
│              SEQUENCE vs LIST PERFORMANCE                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   100,000 items, filter + map + take(10):                   │
│                                                             │
│   List:     █████████████████████████████████ 45ms          │
│   Sequence: ██ 2ms                                          │
│                                                             │
│   Memory allocations:                                       │
│   List:     ███████████████████████████ 3 intermediate      │
│   Sequence: █ 1 final                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tail Recursion

```kotlin
// ПРОБЛЕМА: глубокая рекурсия = Stack Overflow
fun factorial(n: Long): Long {
    return if (n <= 1) 1
    else n * factorial(n - 1)  // Stack overflow при n > 10,000
}

// РЕШЕНИЕ: tailrec оптимизация
tailrec fun factorial(n: Long, accumulator: Long = 1): Long {
    return if (n <= 1) accumulator
    else factorial(n - 1, n * accumulator)  // Компилируется в loop!
}

// Компилятор превращает в:
fun factorial(n: Long, accumulator: Long = 1): Long {
    var n = n
    var acc = accumulator
    while (n > 1) {
        acc = n * acc
        n = n - 1
    }
    return acc
}
```

### Inline Functions

```kotlin
// inline убирает overhead вызова функции
// Особенно полезно для higher-order functions

// БЕЗ inline: лямбда создаёт анонимный класс
fun measure(block: () -> Unit) {
    val start = System.currentTimeMillis()
    block()  // Вызов через анонимный класс
    println("Took ${System.currentTimeMillis() - start}ms")
}

// С inline: лямбда вставляется на месте
inline fun measure(block: () -> Unit) {
    val start = System.currentTimeMillis()
    block()  // Код вставляется сюда
    println("Took ${System.currentTimeMillis() - start}ms")
}

// Kotlin 2.1.20: новый inlining pass даёт 9.5% улучшение runtime
```

### Platform-Specific Hot Paths

```kotlin
// Для performance-critical кода используй expect/actual

// commonMain
expect fun encryptData(data: ByteArray, key: ByteArray): ByteArray

// androidMain — используй Android Crypto API
actual fun encryptData(data: ByteArray, key: ByteArray): ByteArray {
    val cipher = Cipher.getInstance("AES/GCM/NoPadding")
    // ... оптимизированная Android реализация
}

// iosMain — используй iOS CryptoKit
actual fun encryptData(data: ByteArray, key: ByteArray): ByteArray {
    // CommonCrypto или CryptoKit через cinterop
    // ... оптимизированная iOS реализация
}
```

---

## 4. Profiling Tools

### Android Profiling

```kotlin
// Android Studio Profiler
// View → Tool Windows → Profiler

// CPU Profiler
// - System Trace: low-level performance
// - Java/Kotlin Method Trace: call stacks
// - Sample-based: minimal overhead

// Memory Profiler
// - Heap dump analysis
// - Allocation tracking
// - Leak detection

// Build Analyzer
// Build → Analyze Build → Build Analyzer
// Показывает самые долгие Gradle tasks
```

### iOS Profiling

```bash
# Xcode Instruments
# Product → Profile (⌘I)

# Полезные instruments:
# - Time Profiler: CPU usage
# - Allocations: memory allocations
# - Leaks: memory leaks
# - Core Animation: UI performance

# LLDB Debugging
# Работает с Kotlin/Native!
# Можно ставить breakpoints в Kotlin коде

# Memory Graph Debugger
# Debug → Debug Memory Graph
```

### Gradle Build Scans

```bash
# Детальный анализ билда
./gradlew :shared:linkDebugFrameworkIosArm64 --scan

# Откроет в браузере:
# - Timeline: какие tasks когда выполнялись
# - Performance: bottlenecks
# - Dependencies: resolution time
# - Configuration: cache hits/misses
```

---

## 5. Real-World Benchmarks

### Google Docs iOS (KMP)

```
┌─────────────────────────────────────────────────────────────┐
│              GOOGLE DOCS iOS (KMP) METRICS                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Runtime performance: "on par or better" vs native Swift   │
│   Code sharing: 95%+ shared with Android                    │
│   Build time: acceptable for enterprise                     │
│                                                             │
│   Google contributions:                                     │
│   - LLVM 16 upgrade for Kotlin/Native                       │
│   - More efficient garbage collector                        │
│   - Improved string implementation                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Framework Comparison

```
┌─────────────────────────────────────────────────────────────┐
│              KMP vs FLUTTER vs RN PERFORMANCE                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Startup Time:                                             │
│   Native:  ████████████ baseline                            │
│   KMP:     █████████████ +5-10%                             │
│   Flutter: ██████████████████ +30-50% (engine load)         │
│   RN:      ████████████████████ +40-60% (JS bridge)         │
│                                                             │
│   Memory Usage:                                             │
│   Native:  ████████████ baseline                            │
│   KMP:     █████████████ +5-15%                             │
│   Flutter: ██████████████████ +30-40%                       │
│   RN:      ██████████████████████ +50-70%                   │
│                                                             │
│   App Size:                                                 │
│   Native:  ████████████ baseline                            │
│   KMP:     █████████████ +10-20%                            │
│   Flutter: ████████████████████ +5-7 MB (engine)            │
│   RN:      ██████████████████ +3-5 MB (bridge)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Best Practices Summary

### Build Time

```kotlin
// ✅ DO
// - Используй Kotlin 2.1.21+ (K2 compiler)
// - Включи caching и parallel builds
// - Используй linkDebug* для разработки
// - Кэшируй ~/.konan в CI
// - Избегай transitiveExport = true

// ❌ DON'T
// - Не запускай Release builds при разработке
// - Не отключай Gradle daemon
// - Не используй устаревшие kotlin.native.* опции
// - Не собирай все targets одновременно
```

### Binary Size

```kotlin
// ✅ DO
// - embedBitcode = DISABLE (iOS 16+)
// - Используй internal для implementation details
// - Добавь -dead_strip linker option
// - Один umbrella framework для iOS
// - Смотри финальный IPA, не raw framework

// ❌ DON'T
// - Не делай всё public
// - Не добавляй ненужные зависимости
// - Не используй transitiveExport
// - Не судись по disk size framework
```

### Runtime

```kotlin
// ✅ DO
// - Профилируй ПЕРЕД оптимизацией
// - Используй value classes для wrappers
// - Sequences для больших коллекций
// - tailrec для recursion
// - inline для higher-order functions
// - Platform-specific для hot paths

// ❌ DON'T
// - Не оптимизируй без измерений
// - Не используй value classes с generics/nullables
// - Не используй sequences для маленьких коллекций
// - Не забывай про boxing
```

---

## Troubleshooting

### Slow iOS Builds

```kotlin
// 1. Проверь что используешь Debug
./gradlew :shared:tasks | grep -i release
// Если есть linkRelease* в логах — проблема

// 2. Проверь кэширование
cat gradle.properties | grep -E "caching|native"

// 3. Проверь память
// gradle.properties
org.gradle.jvmargs=-Xmx6g  // Увеличь если <4g

// 4. Windows: исключи антивирус
// Добавь ~/.konan в исключения
```

### Large Binary Size

```kotlin
// 1. Аудит зависимостей
./gradlew :shared:dependencies

// 2. Проверь exposed API
// Ищи public classes которые не нужны iOS
grep -r "public class" shared/src/commonMain/

// 3. Включи dead stripping
// build.gradle.kts
linkerOpts += "-dead_strip"

// 4. Отключи bitcode
embedBitcode = BitcodeEmbeddingMode.DISABLE
```

### Slow Runtime

```kotlin
// 1. Профилируй сначала!
// Android: Studio Profiler
// iOS: Instruments

// 2. Ищи allocations в hot paths
// Memory Profiler → Allocations

// 3. Проверь sequences usage
// Большие коллекции должны использовать asSequence()

// 4. Проверь coroutines
// Избегай blocking calls в main thread
```

---

## Мифы и заблуждения

### Миф 1: "KMP всегда медленнее native Swift"

**Реальность:** Google Docs iOS на KMP показывает "on par or better" performance vs native Swift. Проблема не в KMP, а в неоптимизированном коде. С правильными техниками KMP конкурентоспособен.

### Миф 2: "K2 ускоряет всё в 2x"

**Реальность:** K2 ускоряет только frontend (analysis phase). Для Kotlin/Native основной bottleneck — LLVM backend, который K2 не затрагивает. K2 даёт 40-90% улучшение общего build time, но не 2x для iOS builds.

### Миф 3: "Value classes — серебряная пуля"

**Реальность:** Value classes создают boxing при:
- Nullable типах: `UserId?` = boxed
- Generics: `List<UserId>` = каждый element boxed
- Any: `val x: Any = UserId(...)` = boxed

Используй только для non-nullable, non-generic hot paths.

### Миф 4: "Sequences всегда лучше чем List"

**Реальность:** Sequences имеют overhead на создание iterator. Для маленьких коллекций (<100 элементов) или одной операции List быстрее. Sequences выгодны при:
- 1000+ элементов
- Несколько chained операций
- Early termination (take, first)

### Миф 5: "inline везде = быстрее"

**Реальность:** inline увеличивает code size (код вставляется в каждое место вызова). Для больших функций это может ухудшить instruction cache performance. inline выгоден для:
- Маленьких функций
- Higher-order functions (убирает lambda allocation)
- Горячих путей

---

## Рекомендуемые источники

### Official Documentation

| Источник | Описание |
|----------|----------|
| [Native Compilation Tips](https://kotlinlang.org/docs/native-improving-compilation-time.html) | Build time optimization guide |
| [K2 Benchmarks](https://blog.jetbrains.com/kotlin/2024/04/k2-compiler-performance-benchmarks/) | K2 compiler performance |
| [Value Classes](https://kotlinlang.org/docs/inline-classes.html) | Zero-cost abstractions |
| [KMP Roadmap 2025](https://blog.jetbrains.com/kotlin/2024/10/kotlin-multiplatform-development-roadmap-for-2025/) | Будущие улучшения |

### Tools

| Инструмент | Назначение |
|------------|-----------|
| [kotlinx-benchmark](https://github.com/Kotlin/kotlinx-benchmark) | Multiplatform benchmarking |
| Gradle Build Scan | Build analysis (--scan) |
| Android Profiler | Runtime profiling |
| Xcode Instruments | iOS profiling |

### CS-фундамент

| Источник | Зачем |
|----------|-------|
| [[compilation-pipeline]] | Понять что оптимизируем |
| [[native-compilation-llvm]] | Почему LLVM медленный |
| [[cpu-architecture-basics]] | Понять cache и inline

---

## Связь с другими темами

- **[[kmp-gradle-deep-dive]]** — Оптимизация build time начинается с глубокого понимания Gradle: DAG задач, кэширование, configuration cache и параллельное выполнение. Без правильной Gradle-конфигурации никакие другие оптимизации не помогут — большая часть «медленных» KMP-сборок связана именно с неоптимальными настройками Gradle, а не с Kotlin/Native. Этот материал объясняет, как устроена сборка изнутри и какие tasks можно безопасно пропускать.

- **[[kmp-memory-management]]** — Runtime-производительность напрямую зависит от управления памятью: GC-паузы вызывают UI-фризы, чрезмерные аллокации увеличивают давление на GC, а memory spikes при interop-вызовах деградируют user experience. Value classes, sequences и object reuse — это техники, которые одновременно решают и memory, и performance проблемы. Профилирование через Instruments показывает оба аспекта.

- **[[kmp-debugging]]** — Профилирование перед оптимизацией — золотое правило, и инструменты отладки (Android Studio Profiler, Xcode Instruments, Gradle Build Scans) являются основным средством поиска bottlenecks. Без измерений оптимизация превращается в угадывание. Материал по debugging объясняет, как настроить GC-логирование, signposts для Instruments и build scans для Gradle — всё то, что необходимо для data-driven оптимизации.

## Источники и дальнейшее чтение

- Moskala M. (2021). *Effective Kotlin.* — Книга содержит детальный разбор производительности Kotlin-конструкций: когда sequences выгоднее list, как inline влияет на code size, когда value classes дают реальный выигрыш, а когда приводят к boxing. Прямые практические рекомендации, применимые к оптимизации KMP-кода.

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive.* — Асинхронный код — частый источник performance-проблем: неправильный выбор Dispatcher, blocking calls на main thread, утечки корутинных scope. Книга объясняет, как structured concurrency помогает контролировать ресурсы и избегать типичных ошибок.

- Martin R. (2017). *Clean Architecture.* — Архитектурные решения (разделение на слои, dependency rule) определяют, какой код оказывается на hot path и как легко его оптимизировать. Правильная архитектура позволяет изолировать performance-critical участки и применять platform-specific оптимизации через expect/actual без рефакторинга всего проекта.

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, K2 Compiler, Compose Multiplatform 1.7*
