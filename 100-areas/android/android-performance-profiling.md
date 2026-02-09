---
title: "Профилирование производительности Android"
created: 2025-12-25
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [profiling, sampling, tracing, memory-analysis]
tags:
  - topic/android
  - topic/performance
  - type/deep-dive
  - level/advanced
related:
  - "[[android-view-rendering-pipeline]]"
  - "[[android-compose-internals]]"
  - "[[android-process-memory]]"
---

# Android Performance Profiling

## Терминология

| Термин | Значение |
|--------|----------|
| **TTID** | Time to Initial Display — время до первого frame |
| **TTFD** | Time to Full Display — время до полной готовности UI |
| **Jank** | Пропуск frames, заикания UI |
| **ANR** | Application Not Responding — зависание > 5 секунд |
| **Heap Dump** | Снимок памяти со всеми объектами |
| **Baseline Profile** | Предкомпилированные hot paths для быстрого старта |
| **R8** | Компилятор для shrinking, obfuscation, optimization |
| **Perfetto** | Системный tracing tool для глубокого анализа |

---

## ПОЧЕМУ: Зачем профилировать

### Проблемы без профилирования

```kotlin
// "Почему приложение тормозит?"
// "Откуда memory leaks?"
// "Почему ANR?"
// "Почему startup медленный?"
// Без профилирования — гадание на кофейной гуще
```

### Когда профилирование обязательно

| Сценарий | Инструменты |
|----------|-------------|
| Jank в UI | Profile GPU Rendering, Perfetto |
| Memory leaks | LeakCanary, Memory Profiler |
| Slow startup | Macrobenchmark, Baseline Profiles |
| Battery drain | Energy Profiler |
| Network issues | Network Profiler |
| ANR | Perfetto, StrictMode |

### Аналогия: Медицинская диагностика

```
Симптомы → Анализы → Диагноз → Лечение

Jank (симптом) → Perfetto (анализ) →
→ "Главный thread заблокирован" (диагноз) →
→ Вынести работу в background (лечение)
```

---

## ЧТО: Инструменты профилирования

### Android Studio Profiler

```
View → Tool Windows → Profiler
```

| Profiler | Что показывает | Типичные проблемы |
|----------|----------------|-------------------|
| **CPU** | Thread activity, call stacks | Блокировки, тяжёлые операции |
| **Memory** | Heap, allocations, GC | Leaks, excessive allocations |
| **Network** | Requests, timing, payload | Slow APIs, large payloads |
| **Energy** | Wake locks, GPS, radio | Battery drain |

### CPU Profiler

```
┌─────────────────────────────────────────────────────────────┐
│ Timeline: Threads                                            │
│ ─────────────────────────────────────────────────────────── │
│ main      [████████░░░░████████████░░░░░░░]                 │
│ worker-1  [░░░░████████████░░░░░░░░░░░░░░░]                 │
│ worker-2  [░░░░░░░░░░░░░░░░████████████░░░]                 │
│                                                              │
│ Legend: █ Running  ░ Waiting/Sleeping                        │
└─────────────────────────────────────────────────────────────┘
```

**Trace Types:**

| Type | Overhead | Precision | Когда |
|------|----------|-----------|-------|
| Sample Java | Low | ~100μs | General profiling |
| Trace Java | High | Exact | Precise timing |
| Sample C++ | Low | ~100μs | Native code |
| System Trace | Low | Kernel level | Scheduling, I/O |

### Memory Profiler

```
┌─────────────────────────────────────────────────────────────┐
│ Memory: 128 MB                                               │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Java: 64 MB    Native: 32 MB    Graphics: 24 MB        │ │
│ │ Code: 4 MB     Stack: 2 MB      Other: 2 MB            │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                              │
│ [Capture Heap Dump]  [Record Allocations]                   │
└─────────────────────────────────────────────────────────────┘
```

**Heap Dump показывает:**
- Все живые объекты
- Размер каждого объекта (shallow/retained)
- Reference chains (кто держит объект)
- Potential leaks

### Perfetto

```bash
# Record trace
adb shell perfetto -o /data/misc/perfetto-traces/trace.pb \
  -t 10s sched freq idle am wm gfx view

# Pull trace
adb pull /data/misc/perfetto-traces/trace.pb

# Open in browser
# → ui.perfetto.dev
```

**Что искать в Perfetto:**

| Track | Показывает |
|-------|------------|
| `Choreographer#doFrame` | Frame rendering |
| `RenderThread` | GPU work |
| `Binder transactions` | IPC calls |
| `CPU scheduling` | Thread scheduling |
| `Expected/Actual Timeline` | Jank detection |

### Profile GPU Rendering

```
Developer Options → Profile GPU Rendering → On screen as bars

┌─────────────────────────────────────────────────────────────┐
│ ═══════════════════════ 16ms line ═══════════════════════  │
│     ║   ║        ║     ║║║   ║                              │
│  ║  ║   ║ ║      ║     ║║║   ║  ║                           │
│  ║  ║   ║ ║  ║   ║ ║   ║║║   ║  ║ ║                         │
│  ║  ║ ║ ║ ║  ║ ║ ║ ║ ║ ║║║ ║ ║  ║ ║ ║                       │
└─────────────────────────────────────────────────────────────┘
```

**Цвета полос:**

| Цвет | Фаза | Высокая = проблема с |
|------|------|---------------------|
| Orange | Input | Touch handlers |
| Red | Animation | Animators |
| Yellow | Measure/Layout | View hierarchy |
| Green | Draw | onDraw() |
| Purple | Sync/Upload | Bitmaps |
| Dark Blue | Issue Commands | Draw calls |
| Light Green | Swap Buffers | GPU load |

---

## КАК: Практические сценарии

### 1. LeakCanary — детекция memory leaks

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
}

// Всё! Автоматически отслеживает:
// - Activities
// - Fragments
// - ViewModels
// - Views
// - Services
```

**Как работает:**

```
Object destroyed
       ↓
WeakReference created
       ↓
Wait 5 seconds + GC
       ↓
Still reachable? → LEAK!
       ↓
Heap dump → analyze → notification
```

**Типичные leaks:**

```kotlin
// ❌ Static reference to Activity
companion object {
    var activity: MainActivity? = null  // LEAK!
}

// ❌ Inner class holds outer reference
class MyActivity : Activity() {
    inner class MyHandler : Handler() {  // Holds reference to Activity
        override fun handleMessage(msg: Message) { }
    }
}

// ✅ Static nested class + WeakReference
class MyActivity : Activity() {
    class MyHandler(activity: MyActivity) : Handler() {
        private val activityRef = WeakReference(activity)
        override fun handleMessage(msg: Message) {
            activityRef.get()?.doSomething()
        }
    }
}
```

### 2. Baseline Profiles — ускорение startup

```kotlin
// :baselineprofile module
// BaselineProfileGenerator.kt

@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generate() = rule.collect(
        packageName = "com.example.app",
        maxIterations = 15
    ) {
        // App startup
        pressHome()
        startActivityAndWait()

        // Critical user journeys
        device.findObject(By.res("main_list")).apply {
            scroll(Direction.DOWN, 2f)
            scroll(Direction.UP, 2f)
        }

        // Open detail screen
        device.findObject(By.res("item_0")).click()
        device.waitForIdle()
    }
}
```

```kotlin
// build.gradle.kts (:app)
plugins {
    id("androidx.baselineprofile")
}

dependencies {
    baselineProfile(project(":baselineprofile"))
}
```

**Результаты:**
- Startup: 30-40% faster
- Scroll: 15-25% less jank
- Applies from first launch (не нужен JIT warmup)

### 3. Macrobenchmark — измерение performance

```kotlin
// :benchmark module
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun coldStartup() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 10,
        startupMode = StartupMode.COLD,
        setupBlock = {
            pressHome()
        }
    ) {
        startActivityAndWait()
    }

    @Test
    fun scrollPerformance() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(FrameTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.WARM
    ) {
        startActivityAndWait()

        val list = device.findObject(By.res("main_list"))
        repeat(5) {
            list.scroll(Direction.DOWN, 2f)
            device.waitForIdle()
        }
    }
}
```

**Вывод:**
```
StartupBenchmark_coldStartup
timeToInitialDisplayMs   min 324.5,   median 342.1,   max 385.2
timeToFullDisplayMs      min 512.3,   median 548.7,   max 612.4

ScrollBenchmark_scrollPerformance
frameDurationCpuMs       P50    8.2,   P90   12.4,   P99   18.3
frameOverrunMs           P50   -4.2,   P90    2.1,   P99    8.7
```

### 4. R8 — shrinking и optimization

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

```proguard
# proguard-rules.pro

# Keep data classes for serialization
-keep class com.example.app.data.model.** { *; }

# Keep Retrofit interfaces
-keep interface com.example.app.network.** { *; }

# Keep enum values
-keepclassmembers enum * { *; }

# Debugging: keep line numbers
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile
```

**Проверка размера:**
```bash
# Analyze APK
Android Studio → Build → Analyze APK

# Сравнение
Before R8: 15 MB
After R8:  9 MB (-40%)
```

### 5. StrictMode — детекция проблем в runtime

```kotlin
// Application.onCreate()
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .penaltyFlashScreen()  // Visual feedback
            .build()
    )

    StrictMode.setVmPolicy(
        StrictMode.VmPolicy.Builder()
            .detectLeakedSqlLiteObjects()
            .detectLeakedClosableObjects()
            .detectActivityLeaks()
            .penaltyLog()
            .build()
    )
}
```

### 6. Layout Inspector для Compose

```
Tools → Layout Inspector

Compose tab:
├── Recomposition count (сколько раз)
├── Skip count (сколько пропущено)
├── Component tree
└── State values
```

**Что искать:**
- Высокий recomposition count → проблема со stability
- Низкий skip count → неэффективные параметры
- Глубокое дерево → potential performance issue

---

## Performance Targets

### Startup

| Metric | Good | Acceptable | Bad |
|--------|------|------------|-----|
| Cold start | < 500ms | < 1s | > 2s |
| Warm start | < 200ms | < 500ms | > 1s |
| Hot start | < 100ms | < 200ms | > 500ms |

### Rendering

| Metric | Good | Acceptable | Bad |
|--------|------|------------|-----|
| Frame time | < 16ms | < 20ms | > 32ms |
| Jank frames | < 1% | < 5% | > 10% |
| Frozen frames | 0% | < 0.1% | > 0.5% |

### Stability

| Metric | Good | Acceptable | Bad |
|--------|------|------------|-----|
| Crash rate | < 0.5% | < 1% | > 2% |
| ANR rate | < 0.1% | < 0.47% | > 1% |

---

## КОГДА НЕ профилировать

### Debug vs Release

```kotlin
// ❌ Профилирование debug build
// Результаты неточные:
// - Нет R8 optimization
// - Debugger overhead
// - Дополнительные assertions

// ✅ Профилирование release build с profileable
android {
    buildTypes {
        release {
            // Для профилирования в release
        }
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:profileable="true"
    android:profileableByShell="true">
```

### Premature Optimization

```kotlin
// ❌ Оптимизируем без данных
"Мне кажется, этот метод медленный"

// ✅ Сначала измеряем, потом оптимизируем
1. Macrobenchmark показывает startup 800ms
2. Perfetto показывает 400ms в database init
3. Оптимизируем database init
4. Проверяем: startup теперь 450ms
```

---

## Типичные ошибки

### 1. Профилирование debug build

```kotlin
// Debug build:
// - Нет R8 → больше code
// - Нет shrinking → больше APK
// - Debug logging → overhead
// - ProGuard off → slower execution

// Release build:
// - Реальные условия пользователя
// - Точные метрики
```

### 2. Игнорирование small leaks

```kotlin
// "Это маленький leak, потом пофиксим"
// 10 screens × 1MB leak = 10MB → OOM

// ✅ Fix ALL leaks immediately
debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
```

### 3. Отсутствие Baseline Profiles

```kotlin
// Без Baseline Profile:
// - Каждый launch: JIT compilation
// - Первые 10-20 секунд медленнее
// - Плохой first impression

// С Baseline Profile:
// - AOT compilation hot paths
// - Fast from first launch
// - 30%+ improvement
```

### 4. R8 без тестирования

```kotlin
// R8 может сломать:
// - Reflection
// - Serialization
// - Dynamic class loading

// ✅ Всегда тестируйте release build
// ✅ Добавляйте keep rules при необходимости
```

---

## Checklist перед релизом

- [ ] LeakCanary не показывает leaks
- [ ] Baseline Profiles сгенерированы
- [ ] Macrobenchmark показывает приемлемые метрики
- [ ] R8 включён и протестирован
- [ ] StrictMode не находит нарушений
- [ ] Profile GPU Rendering < 16ms
- [ ] Memory stable (нет постоянного роста)
- [ ] ANR rate < 0.47% в Firebase/Play Console

---

## ПОЧЕМУ: Глубокое понимание профилирования

### Почему профилирование требует release build?

**Debug build ≠ Production:**

```kotlin
// Debug build overhead:
// 1. Logging (Timber, Logcat) → I/O operations
// 2. Debug metadata → larger APK
// 3. No R8 optimization → slower code execution
// 4. Debuggable flag → runtime checks
// 5. ART optimizations disabled → interpreted code

// Release build:
// - R8 shrinking/optimization
// - ProGuard obfuscation
// - ART AOT compilation
// - Real-world performance

// Типичная разница:
// Debug startup: 2.5s
// Release startup: 1.2s (52% faster!)
```

**Как профилировать release:**

```kotlin
// build.gradle.kts
buildTypes {
    release {
        isDebuggable = true  // Временно! Для профилирования
        isMinifyEnabled = true
        isShrinkResources = true
    }
}

// Или создать отдельный buildType:
buildTypes {
    create("benchmark") {
        initWith(getByName("release"))
        isDebuggable = true
        signingConfig = signingConfigs.getByName("debug")
        matchingFallbacks += listOf("release")
    }
}
```

### Почему Baseline Profiles дают 30%+ улучшения?

**Проблема cold start:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Без Baseline Profile:                                            │
│                                                                 │
│ App Launch → JIT Compile → Interpreted → JIT → Optimized Code   │
│              ─────────────────────────────────────────────────  │
│              │← Медленно: первые 10-20 секунд неоптимизированы→│ │
│                                                                 │
│ С Baseline Profile:                                              │
│                                                                 │
│ Install → AOT Compile hot paths → Launch → Fast from start       │
│           ─────────────────────   │                             │
│           │← Предкомпилировано →│  │← Сразу быстро            │ │
└─────────────────────────────────────────────────────────────────┘
```

**Что включает Baseline Profile:**

```kotlin
// Baseline Profile определяет "hot paths":
// - Startup code (Application.onCreate, MainActivity)
// - First-screen rendering
// - Common user journeys

// Эти paths компилируются AOT при установке
// Остальной код — JIT при необходимости
```

### Почему memory leaks сложно детектировать?

**Garbage Collection не всё решает:**

```kotlin
// GC удаляет объекты без references
// Но если reference существует — объект жив

class BadActivity : Activity() {
    companion object {
        var leakedContext: Context? = null  // static reference!
    }

    override fun onCreate() {
        leakedContext = this  // Activity никогда не будет собрана
    }
}

// GC не может удалить Activity:
// Root → Companion → leakedContext → Activity → Resources, Views...
```

**Как LeakCanary находит leaks:**

```kotlin
// 1. LeakCanary отслеживает Activity/Fragment destruction
// 2. Ждёт GC (форсирует через Runtime.gc())
// 3. Проверяет WeakReference на destroyed объект
// 4. Если объект ещё жив → это leak
// 5. Делает heap dump и анализирует reference chain

// Анализ heap dump:
// Root → Field → Field → ... → Leaked Object
// Показывает ТОЧНЫЙ путь, кто держит reference
```

### Почему ANR происходит при >5 секундах?

**Main thread — UI thread:**

```kotlin
// Android использует single-threaded UI model
// Main thread:
// - Обрабатывает touch events
// - Рендерит UI (measure, layout, draw)
// - Выполняет lifecycle callbacks
// - Обрабатывает BroadcastReceivers

// Если main thread занят >5 секунд:
// 1. Touch events не обрабатываются
// 2. UI не обновляется
// 3. Пользователь думает "приложение зависло"
// 4. Android показывает ANR dialog

// BroadcastReceiver: таймаут 10 секунд (foreground) / 60 секунд (background)
// Service: таймаут 20 секунд (foreground) / 200 секунд (background)
```

**Perfetto показывает причину:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Perfetto Timeline:                                               │
│                                                                 │
│ main thread [████████████████████████████████████████████]       │
│              │← doHeavyWork() блокирует 7 секунд →│              │
│                                                                 │
│ Input events: [XX] [XX] [XX] ← не обработаны                    │
│                                                                 │
│ Результат: ANR                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Advanced: Perfetto для глубокого анализа

### Что такое Perfetto?

```kotlin
// Perfetto = системный tracer для Android
// Записывает:
// - CPU scheduling (какой thread на каком core)
// - GPU rendering
// - Memory allocations
// - Disk I/O
// - Network activity
// - Custom trace events

// Более мощный чем Android Studio Profiler
// Используется Google для анализа Android itself
```

### Запуск Perfetto trace

```bash
# Простой trace через ADB
adb shell perfetto -o /data/misc/perfetto-traces/trace.pb -t 10s sched freq idle

# Или через Android Studio: Profile → Record → System Trace
```

### Анализ Perfetto trace

```kotlin
// Открыть в https://ui.perfetto.dev/

// Ключевые метрики:
// 1. Main thread занятость (должна быть <60%)
// 2. Frame timing (каждый frame <16ms)
// 3. GC паузы (должны быть <10ms)
// 4. Binder transactions (IPC latency)
// 5. Disk I/O на main thread (должен быть 0!)
```

### Custom trace events

```kotlin
// Добавляем свои trace events для анализа
import android.os.Trace

fun loadData() {
    Trace.beginSection("loadData")
    try {
        val data = repository.getData()
        Trace.beginSection("processData")
        processData(data)
        Trace.endSection()
    } finally {
        Trace.endSection()
    }
}

// В Perfetto увидим:
// loadData [███████████████████]
//   └── processData [████████████]
```

---

## Firebase Performance Monitoring

### Автоматические метрики

```kotlin
// Firebase собирает автоматически:
// - App startup time
// - Screen rendering (slow/frozen frames)
// - Network request latency
// - HTTP success rate

// Добавить в build.gradle:
implementation("com.google.firebase:firebase-perf-ktx:20.5.1")
```

### Custom traces

```kotlin
// Измерение конкретных операций
val trace = Firebase.performance.newTrace("load_user_profile")
trace.start()

val user = userRepository.loadProfile(userId)

trace.putAttribute("user_type", user.type)
trace.putMetric("items_count", user.items.size.toLong())

trace.stop()

// В Firebase Console:
// - Распределение времени выполнения
// - Breakdown по attributes
// - Тренды во времени
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Профилирование debug build достаточно" | Debug build в 2-3x медленнее release. R8 optimization, ProGuard, ART AOT — всё это отсутствует в debug. Профилируйте release с debuggable=true |
| "Memory leak один раз — не страшно" | Leak накапливается при каждом recreation (rotation, navigation). 10 leaks × 1MB = OOM через несколько минут использования |
| "Baseline Profiles нужны только большим приложениям" | Даже небольшие приложения получают 15-30% улучшение startup. Google рекомендует для ВСЕХ приложений |
| "ANR = бесконечный цикл" | ANR — это ЛЮБАЯ операция >5 секунд на main thread: disk I/O, network, heavy computation. Даже SharedPreferences.commit() может вызвать ANR |
| "StrictMode только для development" | StrictMode должен быть включён в debug builds постоянно. Это catching проблем ДО production |
| "R8 автоматически оптимизирует всё" | R8 не может оптимизировать алгоритмическую сложность. O(n²) останется O(n²). R8 оптимизирует bytecode, не логику |
| "GPU Profiler показывает GPU проблемы" | Profile GPU Rendering показывает время КАЖДОЙ фазы: measure, layout, draw, sync. Большинство проблем — в measure/layout, не GPU |
| "Perfetto сложный, достаточно Android Studio" | Android Studio Profiler — simplified view. Perfetto показывает system-wide picture: scheduling, IPC, I/O. Для серьёзных проблем — Perfetto обязателен |
| "Macrobenchmark заменяет manual testing" | Macrobenchmark измеряет метрики, но не UX. Пользователь может заметить jank, который benchmark пропустит. Используйте оба подхода |
| "Один раз настроил профилирование — готово" | Performance регрессирует с каждым релизом. CI/CD должен включать benchmark tests. Firebase Performance мониторит production 24/7 |

---

## CS-фундамент

| CS-концепция | Применение в Performance Profiling |
|--------------|-----------------------------------|
| **Sampling vs Instrumentation** | CPU Profiler использует sampling (периодические snapshot стека) vs instrumentation (вставка кода в каждый метод). Sampling дешевле, но менее точен |
| **Heap Analysis** | Memory Profiler строит object graph из heap dump. GC roots → reachable objects. Unreachable = garbage. Retained size = объект + всё, что он держит |
| **Call Graph** | CPU traces визуализируются как flame graph / call tree. Показывает иерархию вызовов и время в каждом методе |
| **Statistical Profiling** | Sampling даёт статистическую оценку времени. Чем дольше trace, тем точнее результат. Короткие методы могут быть недопредставлены |
| **Garbage Collection Algorithms** | Android использует concurrent GC (minimal pause). Профилирование показывает GC events и их влияние на latency |
| **Reference Counting vs Tracing GC** | Java/Kotlin используют tracing GC (mark-sweep). Leaks = объекты достижимые от GC roots, но логически мёртвые |
| **Time Complexity Analysis** | Profiler показывает WHERE тратится время, но не WHY. Алгоритмическая сложность требует code review (O(n²) в loop = проблема) |
| **Cache Optimization** | Baseline Profiles = application-level caching. Предкомпилированный код загружается из storage вместо JIT compilation |
| **Concurrency Profiling** | Thread timeline показывает: running, runnable, sleeping, blocked. Lock contention виден как blocked state |
| **Distributed Tracing** | Firebase Performance = distributed tracing для мобильных. Correlates client-side с server-side metrics через trace IDs |

---

## Связанные материалы

| Материал | Зачем смотреть |
|----------|----------------|
| [android-view-rendering-pipeline.md](android-view-rendering-pipeline.md) | Понимание rendering |
| [android-compose-internals.md](android-compose-internals.md) | Compose recomposition |
| [android-threading.md](android-threading.md) | Background work |

---

## Проверь себя

1. Какие 4 типа профилировщиков есть в Android Studio?
2. Что показывает Profile GPU Rendering?
3. Как LeakCanary детектирует leaks?
4. Что такое Baseline Profiles и какой эффект дают?
5. Чем Macrobenchmark отличается от Microbenchmark?
6. Какие файлы нужны для R8 конфигурации?
7. Что такое TTID и TTFD?
8. Почему нужно профилировать release build?

---

## Источники

- [Android Developers — Profile App Performance](https://developer.android.com/studio/profile)
- [Android Developers — Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview)
- [Android Developers — Macrobenchmark](https://developer.android.com/topic/performance/baselineprofiles/measure-baselineprofile)
- [LeakCanary Documentation](https://square.github.io/leakcanary/)
- [Perfetto Documentation](https://perfetto.dev/docs/)
- [Android Developers — R8/ProGuard](https://developer.android.com/build/shrink-code)
- [Android Developers — ANR Diagnosis](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs)

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
