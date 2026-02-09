---
title: "KMP Memory Management: GC, ARC, и их взаимодействие"
created: 2026-01-04
modified: 2026-01-04
tags:
  - topic/jvm
  - topic/kmp
  - memory
  - gc
  - arc
  - native
  - ios
  - type/concept
  - level/advanced
related:
  - "[[kmp-performance-optimization]]"
  - "[[kmp-ios-deep-dive]]"
  - "[[kmp-debugging]]"
cs-foundations:
  - "[[garbage-collection-explained]]"
  - "[[reference-counting-arc]]"
  - "[[memory-model-fundamentals]]"
  - "[[memory-safety-ownership]]"
status: published
---

# KMP Memory Management

> **TL;DR:** Kotlin/Native использует tracing GC (stop-the-world mark + concurrent sweep), Swift — ARC. Интеграция автоматическая, НО mixed retain cycles (Kotlin + Obj-C) не собираются — используй weak references! Для interop loops — autoreleasepool. freeze() deprecated с Kotlin 1.7.20. Мониторинг: `-Xruntime-logs=gc=info` и Xcode Instruments signposts.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Stack vs Heap** | Где живут объекты | [[memory-model-fundamentals]] |
| **Garbage Collection** | Как работает tracing GC | [[garbage-collection-explained]] |
| **ARC** | Reference counting для iOS | [[reference-counting-arc]] |
| KMP Architecture | Структура проекта | [[kmp-project-structure]] |
| Coroutines | Threading model | [[kotlin-coroutines]] |

> **Рекомендация:** Если ты не понимаешь разницу между GC и ARC, **обязательно** начни с CS-фундамента выше. Без этого материал будет неполным.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Tracing GC** | Сборщик мусора с обходом графа объектов | Уборщик проверяет каждую комнату — пустые убирает |
| **ARC** | Automatic Reference Counting | Счётчик посетителей — как только 0, закрываем |
| **Retain Cycle** | Взаимные ссылки, блокирующие освобождение | Два человека держат друг друга за руки — никто не уйдёт |
| **Stop-the-World** | Пауза всех threads для GC | "Замри!" — все застыли пока идёт уборка |
| **autoreleasepool** | Явный scope для освобождения объектов | Мусорный бак — кидаешь туда, потом всё разом выносится |
| **Weak Reference** | Ссылка, не мешающая освобождению | Знакомство без обязательств — ушёл и забыл |

---

## Почему это важно

### Проблема двух миров

Kotlin Multiplatform соединяет две принципиально разные модели управления памятью:

1. **Kotlin/Native** → Tracing GC (похож на JVM)
2. **Swift/Objective-C** → ARC (reference counting)

Это как если бы два человека говорили на разных языках: один считает посетителей у двери (ARC), другой периодически обходит весь дом и выносит мусор (GC). Когда объекты пересекают границу — могут возникнуть недопонимания.

### Эволюция: от freeze к свободе

**2017-2021: Старая модель (freeze)**
- Чтобы передать объект между потоками, его нужно было "заморозить" (`freeze()`)
- Замороженный объект становился immutable навсегда
- Изменение замороженного объекта = `InvalidMutabilityException`
- Код становился сложным, error-prone, непохожим на обычный Kotlin

**2021-2022: Новая модель (preview)**
- JetBrains переписали memory manager с нуля
- Убрали requirement на freeze
- Добавили нормальный tracing GC

**2022+: Новая модель (default)**
- Kotlin 1.7.20: новый MM стал default
- Kotlin 1.9.20: старый MM полностью удалён
- freeze() стал no-op, потом deprecated

**Почему сменили?** Старая модель была попыткой избежать GC через ownership-like систему (как в Rust). Но без поддержки компилятора (ownership в Rust — compile-time, freeze в K/N — runtime) это создавало больше проблем, чем решало.

### Реальные последствия

| Аспект | Что нужно знать |
|--------|-----------------|
| **Mixed cycles** | Retain cycle Kotlin ↔ Swift = memory leak |
| **Deallocation timing** | K/N: периодически, Swift: немедленно |
| **Memory footprint** | Compose UI может занимать больше памяти чем SwiftUI |
| **GC pauses** | Могут вызывать микро-freezes UI |

---

## Две модели памяти

```
┌─────────────────────────────────────────────────────────────┐
│                 KMP MEMORY MODELS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   KOTLIN/NATIVE (Tracing GC)       SWIFT (ARC)              │
│   ─────────────────────────        ─────────────            │
│                                                             │
│   ┌─────┐   ┌─────┐                ┌─────┐   ┌─────┐        │
│   │ Obj │──▶│ Obj │                │ Obj │──▶│ Obj │        │
│   └─────┘   └─────┘                └──┬──┘   └──┬──┘        │
│       │         │                     │ ref=1   │ ref=1     │
│       ▼         │                     │         │           │
│   ┌─────┐       │                     ▼         ▼           │
│   │ Obj │◀──────┘                  ref=0 → freed            │
│   └─────┘                                                   │
│                                                             │
│   GC обходит граф                  Счётчик ссылок           │
│   Находит недостижимые             ref=0 → сразу freed      │
│   Периодическая сборка             Нет задержки             │
│                                                             │
│   ✅ Circular refs OK              ❌ Circular refs = leak  │
│   ❌ GC pauses                     ✅ Deterministic         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Kotlin/Native Garbage Collector

### Алгоритм

```
┌─────────────────────────────────────────────────────────────┐
│              KOTLIN/NATIVE GC PHASES                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. STOP THE WORLD                                         │
│      Все application threads останавливаются                │
│                                                             │
│   2. MARK PHASE (parallel)                                  │
│      ┌───────────────────────────────────────┐              │
│      │ App Thread 1 ──▶ marks objects        │              │
│      │ App Thread 2 ──▶ marks objects        │              │
│      │ GC Thread    ──▶ marks objects        │              │
│      │ Marker Thread ──▶ marks objects       │              │
│      └───────────────────────────────────────┘              │
│                                                             │
│   3. SWEEP PHASE (concurrent)                               │
│      App threads resume                                     │
│      GC thread sweeps unmarked objects                      │
│                                                             │
│   4. WEAK REFS PROCESSING                                   │
│      Обработка weak references                              │
│      (параллельно по умолчанию)                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Когда запускается GC

```kotlin
// GC запускается автоматически:
// 1. По memory pressure (заканчивается память)
// 2. По таймеру (периодически)
// 3. Вручную:

import kotlin.native.internal.GC

// Принудительный запуск и ожидание завершения
GC.collect()

// Информация о последней сборке
val info = GC.lastGCInfo
println("Memory after GC: ${info?.memoryUsageAfter}")
```

### Настройки GC

```properties
# gradle.properties

# === GC Mode ===
# Default: parallel mark + concurrent sweep
kotlin.native.binary.gc=cms          # Concurrent marking (Experimental)
kotlin.native.binary.gc=noop         # Disable GC (только для тестов!)

# === Mark Phase ===
# Отключить параллельный mark (увеличит паузы)
kotlin.native.binary.gcMarkSingleThreaded=true

# === Logging ===
# Логирование GC в stderr
-Xruntime-logs=gc=info

# === App State Tracking (iOS) ===
# Отключает timer-based GC в background
kotlin.native.binary.appStateTracking=enabled
```

---

## Swift/Objective-C ARC Integration

### Как работает interop

```
┌─────────────────────────────────────────────────────────────┐
│              KOTLIN ←→ SWIFT MEMORY INTEROP                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   KOTLIN SIDE                    SWIFT SIDE                 │
│   ───────────                    ──────────                 │
│                                                             │
│   ┌─────────────┐    pass to    ┌─────────────┐            │
│   │ KotlinUser  │──────────────▶│ Disposable  │            │
│   │ (GC tracks) │               │ Handle      │            │
│   └─────────────┘               └──────┬──────┘            │
│                                        │                    │
│                                        │ wraps              │
│                                        ▼                    │
│                                 ┌─────────────┐            │
│                                 │ Swift Obj   │            │
│                                 │ (ARC tracks)│            │
│                                 └─────────────┘            │
│                                                             │
│   GC освобождает когда         ARC освобождает когда       │
│   недостижим в Kotlin          ref count = 0 в Swift       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Deinitializers: важные детали

```kotlin
// Kotlin объект с destructor-like поведением
class KotlinResource {
    // Этот код НЕ гарантированно выполнится на определённом thread!
}

// Swift side
class SwiftUser {
    var kotlinResource: KotlinResource?

    deinit {
        // ⚠️ Может выполниться на:
        // - Main thread (если объект передан с main thread)
        // - GC thread (если с другого thread или main queue не обрабатывается)
    }
}
```

```properties
# Принудительно deinit на GC thread (не main)
kotlin.native.binary.objcDisposeOnMain=false
```

---

## ⚠️ Retain Cycles: Главная проблема

### Mixed Retain Cycles НЕ собираются!

```
┌─────────────────────────────────────────────────────────────┐
│              MIXED RETAIN CYCLE = MEMORY LEAK!               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   KOTLIN                        SWIFT                       │
│   ┌───────────┐                ┌───────────┐               │
│   │ KotlinObj │───strong──────▶│ SwiftObj  │               │
│   │           │◀───strong──────│           │               │
│   └───────────┘                └───────────┘               │
│                                                             │
│   Kotlin GC видит:             Swift ARC видит:            │
│   "KotlinObj достижим          "SwiftObj имеет             │
│   через SwiftObj"              reference count > 0"        │
│                                                             │
│   ➡️ НИКТО НЕ ОСВОБОДИТ! ➡️ MEMORY LEAK!                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Решение: weak references

```swift
// Swift side — используй weak или unowned

// ❌ ПЛОХО: strong reference → retain cycle
class SwiftController {
    var kotlinViewModel: KotlinViewModel?  // Strong ref!

    init() {
        kotlinViewModel = KotlinViewModel()
        kotlinViewModel?.delegate = self  // Cycle!
    }
}

// ✅ ХОРОШО: weak reference → no cycle
class SwiftController {
    var kotlinViewModel: KotlinViewModel?

    init() {
        kotlinViewModel = KotlinViewModel()
        kotlinViewModel?.delegate = WeakRef(self)  // Breaks cycle
    }
}

// Или в Kotlin создай wrapper
class WeakDelegate<T: AnyObject> {
    weak var value: T?
}
```

```kotlin
// Kotlin side — экспортируй weak wrapper

// В commonMain
expect class WeakReference<T : Any>(referred: T) {
    fun get(): T?
}

// В iosMain
actual class WeakReference<T : Any> actual constructor(referred: T) {
    private val weakRef = kotlin.native.ref.WeakReference(referred)
    actual fun get(): T? = weakRef.get()
}
```

---

## autoreleasepool для Interop Loops

### Проблема: накопление объектов

```kotlin
// ❌ ПЛОХО: объекты накапливаются до следующего GC
fun processLargeDataset() {
    repeat(1_000_000) { index ->
        val nsData = createNSData(index)  // Obj-C объект
        processData(nsData)
        // nsData живёт до конца loop или GC!
    }
    // Огромный memory spike!
}
```

### Решение: autoreleasepool

```kotlin
import platform.Foundation.NSAutoreleasePool

// ✅ ХОРОШО: явный scope для освобождения
fun processLargeDataset() {
    repeat(1_000_000) { index ->
        autoreleasepool {
            val nsData = createNSData(index)
            processData(nsData)
        }  // nsData освобождается здесь!
    }
    // Стабильное потребление памяти
}

// Kotlin предоставляет удобную функцию
inline fun <T> autoreleasepool(block: () -> T): T {
    val pool = NSAutoreleasePool()
    try {
        return block()
    } finally {
        pool.drain()
    }
}
```

```
┌─────────────────────────────────────────────────────────────┐
│              MEMORY USAGE: WITH vs WITHOUT AUTORELEASEPOOL   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Without autoreleasepool:                                  │
│   Memory ▲                                                  │
│          │                    ╱╲                            │
│          │                 ╱╱  ╲╲                           │
│          │              ╱╱      ╲╲  (GC kick in)            │
│          │           ╱╱          ╲╲                         │
│          │        ╱╱               ───                      │
│          │     ╱╱                                           │
│          │  ╱╱                                              │
│          └──────────────────────────────────▶ Time          │
│                                                             │
│   With autoreleasepool:                                     │
│   Memory ▲                                                  │
│          │  ─────────────────────────────────               │
│          │                                                  │
│          │  (stable, no spikes)                             │
│          │                                                  │
│          └──────────────────────────────────▶ Time          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Мониторинг памяти

### GC Logging

```kotlin
// build.gradle.kts
kotlin {
    targets.withType<org.jetbrains.kotlin.gradle.plugin.mpp.KotlinNativeTarget> {
        binaries.all {
            freeCompilerArgs += listOf(
                "-Xruntime-logs=gc=info"
            )
        }
    }
}
```

```
// Пример вывода GC logs:
[GC] Pause: 2.5ms, Allocated: 15MB, Freed: 12MB, Live: 3MB
[GC] Pause: 1.8ms, Allocated: 8MB, Freed: 7MB, Live: 4MB
```

### Xcode Instruments

```properties
# gradle.properties — включить signposts
kotlin.native.binary.enableSafepointSignposts=true
```

```
┌─────────────────────────────────────────────────────────────┐
│              XCODE INSTRUMENTS SETUP                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. Product → Profile (⌘I)                                 │
│   2. Select "os_signpost" template                          │
│   3. Configure:                                             │
│      Subsystem: org.kotlinlang.native.runtime               │
│      Category: safepoint                                    │
│   4. Click Record                                           │
│                                                             │
│   GC pauses появятся как синие блоки                        │
│   Можно соотнести с UI freezes                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Программный мониторинг

```kotlin
import kotlin.native.internal.GC

@OptIn(ExperimentalStdlibApi::class)
fun monitorMemory() {
    // Принудительный GC
    GC.collect()

    // Информация о последней сборке
    val info = GC.lastGCInfo ?: return

    val heapBefore = info.memoryUsageBefore["heap"]
    val heapAfter = info.memoryUsageAfter["heap"]

    println("Heap before: ${heapBefore?.totalObjectsSizeBytes} bytes")
    println("Heap after: ${heapAfter?.totalObjectsSizeBytes} bytes")
    println("Freed: ${(heapBefore?.totalObjectsSizeBytes ?: 0) -
                      (heapAfter?.totalObjectsSizeBytes ?: 0)} bytes")
}

// Тест на memory leaks
@OptIn(ExperimentalStdlibApi::class)
fun testNoMemoryLeak() {
    fun getHeapSize(): Long {
        GC.collect()
        return GC.lastGCInfo!!.memoryUsageAfter["heap"]!!.totalObjectsSizeBytes
    }

    val before = getHeapSize()

    // Код который проверяем
    repeat(1000) {
        val data = processData()
        // data должен освободиться
    }

    val after = getHeapSize()

    // Если after значительно больше before — возможен leak
    require(after - before < 10_000) { "Potential memory leak detected!" }
}
```

---

## Оптимизация потребления памяти

### 1. Отключение paged allocator

```properties
# gradle.properties
# Уменьшает startup memory (но отключает Apple memory tracking)
kotlin.native.binary.pagedAllocator=false
```

### 2. Latin-1 строки

```properties
# gradle.properties
# Строки в Latin-1 занимают 1 byte вместо 2 (UTF-16)
kotlin.native.binary.latin1Strings=true

# ⚠️ Побочный эффект: String.pin(), usePinned(), refTo()
# могут конвертировать в UTF-16 автоматически
```

### 3. Background app tracking

```properties
# gradle.properties
# Отключает timer-based GC когда app в background
# GC только при critical memory pressure
kotlin.native.binary.appStateTracking=enabled
```

### 4. Lazy initialization

```kotlin
// ❌ ПЛОХО: всё создаётся сразу
class ViewModel {
    val heavyResource = loadHeavyResource()  // Сразу грузится
    val database = createDatabase()          // Сразу создаётся
}

// ✅ ХОРОШО: lazy loading
class ViewModel {
    val heavyResource by lazy { loadHeavyResource() }  // По запросу
    val database by lazy { createDatabase() }          // По запросу
}
```

### 5. Avoid unnecessary allocations

```kotlin
// ❌ ПЛОХО: создаёт новый объект каждый раз
fun formatPrice(price: Double): String {
    val formatter = NumberFormat.getCurrencyInstance()  // Новый объект!
    return formatter.format(price)
}

// ✅ ХОРОШО: переиспользуй formatter
private val priceFormatter = NumberFormat.getCurrencyInstance()

fun formatPrice(price: Double): String {
    return priceFormatter.format(price)
}
```

---

## Threading и память

### New Memory Model (default с Kotlin 1.7.20)

```kotlin
// СТАРАЯ модель (deprecated):
// - Объекты нужно было "замораживать" для передачи между threads
// - freeze() делал объект immutable
// - Сложно и error-prone

// НОВАЯ модель (текущая):
// - freeze() deprecated
// - Объекты можно свободно передавать между threads
// - Обычная concurrent programming как на JVM

// ✅ Работает без freeze!
class SharedData {
    var counter = 0
}

val shared = SharedData()

CoroutineScope(Dispatchers.Default).launch {
    shared.counter++  // OK в новой модели
}
```

### Unit Tests и Main Thread

```kotlin
// ⚠️ В unit tests main thread queue не обрабатывается!
// Dispatchers.Main не работает без мока

// ❌ ПЛОХО: зависнет
@Test
fun testWithMainDispatcher() = runTest {
    withContext(Dispatchers.Main) {  // Зависнет!
        doSomething()
    }
}

// ✅ ХОРОШО: mock main dispatcher
@Test
fun testWithMainDispatcher() = runTest {
    Dispatchers.setMain(StandardTestDispatcher())

    withContext(Dispatchers.Main) {  // Работает!
        doSomething()
    }
}
```

---

## Известные проблемы

### UIImage Memory Leak

```kotlin
// ⚠️ Передача UIImage в Kotlin может вызвать memory spike
// iOS side:
// let image = UIImage(named: "large_image")
// kotlinViewModel.processImage(image)  // Memory grows!

// Решение: передавай Data вместо UIImage
// iOS side:
// let imageData = image.pngData()
// kotlinViewModel.processImageData(imageData)
```

### Ktor Darwin Memory

```kotlin
// Некоторые отмечают рост памяти при каждом HTTP запросе
// с Ktor Darwin engine

// Возможные решения:
// 1. Переиспользуй HttpClient (не создавай новый на каждый запрос)
// 2. Явно закрывай response
// 3. Используй autoreleasepool вокруг запросов

val client = HttpClient(Darwin)  // Создай один раз

suspend fun fetchData(): String {
    return autoreleasepool {
        client.get("https://api.example.com/data").bodyAsText()
    }
}
```

### Constants Off Main Thread

```kotlin
// ⚠️ Использование Kotlin констант с Swift не на main thread
// может вызвать memory leaks

// Kotlin:
object Constants {
    const val API_URL = "https://api.example.com"
}

// Swift (off main thread):
// DispatchQueue.global().async {
//     print(Constants.API_URL)  // Potential leak!
// }

// Решение: используй константы только на main thread
// или копируй значение в Swift переменную
```

---

## Мифы и заблуждения

### Миф 1: "K/N GC медленнее чем Swift ARC"

**Реальность:** Это oversimplification. ARC выполняет работу при каждом retain/release (каждое присваивание!). GC выполняет работу пачками, периодически. В одних сценариях быстрее ARC (immediate cleanup), в других — GC (batched работа, нет overhead на каждое присваивание).

**Когда ARC лучше:** Immediate deallocation критичен (освобождение файловых дескрипторов).

**Когда GC лучше:** Много temporary objects, сложные графы объектов, циклические ссылки.

### Миф 2: "Retain cycles — это только Swift проблема"

**Реальность:** Чистые Kotlin retain cycles собираются K/N GC автоматически. Проблема возникает только на границе: если cycle содержит хотя бы один ObjC/Swift объект — он не соберётся.

### Миф 3: "autoreleasepool нужен везде в iOS коде"

**Реальность:** autoreleasepool нужен только в tight loops с interop вызовами. Обычный код не требует явных autoreleasepool — GC и ARC справляются автоматически.

**Признак проблемы:** В GC логах "stable refs in root set" постоянно растёт.

### Миф 4: "freeze() всё ещё нужен для thread safety"

**Реальность:** freeze() deprecated и по сути no-op с Kotlin 1.7.20+. Для thread safety используй обычные механизмы: Mutex, Atomic, @Volatile, synchronized collections.

### Миф 5: "Compose Multiplatform всегда хуже по памяти чем SwiftUI"

**Реальность:** Compose может использовать больше памяти из-за разницы GC vs ARC deallocation timing. Но это не значит "хуже" — GC может быть более efficient в throughput за счёт batching. Реальное влияние зависит от конкретного приложения.

---

## Best Practices

### Memory Management

```kotlin
// ✅ DO
// - Используй autoreleasepool для interop loops
// - Ломай retain cycles через weak references
// - Мониторь GC через logs и Instruments
// - Используй lazy для тяжёлых ресурсов
// - Переиспользуй объекты вместо создания новых

// ❌ DON'T
// - Не создавай mixed retain cycles (Kotlin ↔ Swift)
// - Не передавай большие объекты (UIImage) напрямую
// - Не отключай GC в production
// - Не игнорируй memory warnings
// - Не полагайся на deterministic cleanup (это GC, не ARC)
```

### Debugging Memory Issues

```kotlin
// 1. Включи GC logging
// -Xruntime-logs=gc=info

// 2. Включи Instruments signposts
// kotlin.native.binary.enableSafepointSignposts=true

// 3. Используй Xcode Memory Graph Debugger
// Debug → Debug Memory Graph

// 4. Проверяй heap size программно
// GC.lastGCInfo?.memoryUsageAfter

// 5. Ищи retain cycles в Instruments
// Leaks instrument
```

---

## Troubleshooting

### Growing Memory Usage

```kotlin
// 1. Проверь retain cycles
// Xcode → Debug Memory Graph → ищи cycles

// 2. Проверь autoreleasepool в loops
// Оберни interop вызовы в autoreleasepool

// 3. Проверь lazy vs eager loading
// Используй by lazy для тяжёлых ресурсов

// 4. Проверь Ktor client reuse
// Не создавай новый HttpClient на каждый запрос
```

### GC Pauses Causing UI Freezes

```kotlin
// 1. Включи signposts и проверь в Instruments
// kotlin.native.binary.enableSafepointSignposts=true

// 2. Попробуй concurrent marking
// kotlin.native.binary.gc=cms

// 3. Уменьши allocation rate
// Переиспользуй объекты, используй object pools

// 4. Профилируй allocation hotspots
// Instruments → Allocations
```

---

## Рекомендуемые источники

### Official Documentation

| Источник | Описание |
|----------|----------|
| [Native Memory Manager](https://kotlinlang.org/docs/native-memory-manager.html) | Полная документация GC, tuning parameters |
| [ARC Integration](https://kotlinlang.org/docs/native-arc-integration.html) | Swift interop, autoreleasepool, retain cycles |
| [Migration Guide](https://kotlinlang.org/docs/native-migration-guide.html) | Миграция со старой модели, deprecated APIs |

### Практические статьи

| Источник | Описание |
|----------|----------|
| [Memory Management XCFramework](https://dev.to/arsenikavalchuk/memory-management-and-garbage-collection-in-kotlin-multiplatform-xcframework-15pa) | GC logging, stable refs, practical iOS examples |
| [GC in KMP Part 1](https://www.droidcon.com/2024/09/20/garbage-collector-in-kmp-part-1/) | GC architecture deep dive |
| [GC in KMP Part 2](https://www.droidcon.com/2024/09/24/garbage-collector-in-kmp-part-2/) | iOS-specific memory, ARC interaction |

### CS-фундамент (изучи перед этим материалом)

| Источник | Зачем |
|----------|-------|
| [[garbage-collection-explained]] | Понять tracing GC algorithms |
| [[reference-counting-arc]] | Понять ARC и retain cycles |
| [[memory-model-fundamentals]] | Понять stack vs heap |

### Case Studies

| Компания | Результат |
|----------|-----------|
| Netflix | Первый FAANG в production с KMP |
| McDonald's | ~40% efficiency gains |
| Cash App | Shared business logic |

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, New Memory Model, Compose Multiplatform 1.7*
