---
title: "Cross-Platform: Profiling — Instruments vs Android Studio Profiler"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - profiling
  - instruments
  - performance
  - type/comparison
  - level/intermediate
reading_time: 66
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-memory-management]]"
  - "[[cross-graphics-rendering]]"
related:
  - "[[ios-performance-profiling]]"
  - "[[android-performance-profiling]]"
  - "[[performance-optimization]]"
---

# Cross-Platform: Profiling Tools Comparison

Сравнение инструментов профилирования iOS (Instruments) и Android (Android Studio Profiler) для выявления узких мест производительности.

---

## 1. TL;DR — Сравнительная таблица

### Быстрое сравнение инструментов

| Аспект | iOS (Instruments) | Android (Studio Profiler) |
|--------|-------------------|---------------------------|
| **Запуск** | Xcode -> Product -> Profile (Cmd+I) | View -> Tool Windows -> Profiler |
| **CPU Profiling** | Time Profiler | CPU Profiler |
| **Memory** | Allocations, Leaks, Memory Graph | Memory Profiler, LeakCanary |
| **Network** | Network Profiler | Network Profiler |
| **GPU/UI** | Core Animation, Metal System Trace | Profile GPU Rendering, Perfetto |
| **Production** | MetricKit | Firebase Performance |
| **Сложность освоения** | Высокая | Средняя |
| **Глубина анализа** | Очень глубокая | Глубокая |
| **Интеграция в IDE** | Отдельное приложение | Встроен в IDE |

### Когда что использовать

```
┌─────────────────────────────────────────────────────────────────┐
│                    ВЫБОР ИНСТРУМЕНТА                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  UI лагает / Jank:                                               │
│  ├─ iOS:     Time Profiler → Core Animation                      │
│  └─ Android: CPU Profiler → Profile GPU Rendering                │
│                                                                   │
│  Память растёт / Leaks:                                          │
│  ├─ iOS:     Allocations → Memory Graph Debugger                 │
│  └─ Android: Memory Profiler → LeakCanary                        │
│                                                                   │
│  Медленный запуск:                                               │
│  ├─ iOS:     App Launch template → os_signpost                   │
│  └─ Android: Macrobenchmark → Baseline Profiles                  │
│                                                                   │
│  Проблемы в проде:                                               │
│  ├─ iOS:     MetricKit → Xcode Organizer                         │
│  └─ Android: Firebase Performance → Play Console Vitals          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Целевые метрики обеих платформ

| Метрика | iOS Target | Android Target |
|---------|------------|----------------|
| Cold Start | < 400ms до first render | < 500ms TTID |
| Frame Time | 16.67ms (60 FPS) | < 16ms |
| Hang/ANR | < 500ms | < 5s (ANR threshold) |
| Memory Baseline | < 200MB | Зависит от device class |
| Crash Rate | < 0.1% | < 0.5% |

---

## 2. Обзор инструментов

### iOS: Instruments.app

```
┌─────────────────────────────────────────────────────────────────┐
│  INSTRUMENTS — Комплекс профилирования Apple                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ДОСТУПНЫЕ TEMPLATES                                     │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  Time Profiler      — CPU sampling, call trees          │    │
│  │  Allocations        — heap tracking, memory growth      │    │
│  │  Leaks             — автоматический поиск утечек        │    │
│  │  Core Animation     — FPS, GPU, offscreen rendering     │    │
│  │  Network           — HTTP requests, latency             │    │
│  │  System Trace      — всё: scheduling, I/O, IPC          │    │
│  │  App Launch        — startup profiling                  │    │
│  │  Metal System Trace — GPU pipeline analysis             │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ОСОБЕННОСТИ:                                                    │
│  • Отдельное приложение (не в Xcode)                            │
│  • Множество templates для разных задач                         │
│  • Возможность комбинировать instruments                        │
│  • Высокий порог входа                                          │
│  • Мощные визуализации (flame graphs, call trees)               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Android: Android Studio Profiler

```
┌─────────────────────────────────────────────────────────────────┐
│  ANDROID STUDIO PROFILER — Встроенный инструментарий            │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  ВСТРОЕННЫЕ PROFILERS                                    │    │
│  ├─────────────────────────────────────────────────────────┤    │
│  │  CPU Profiler       — threads, call stacks, flame graph │    │
│  │  Memory Profiler    — heap, allocations, GC events      │    │
│  │  Network Profiler   — requests, timing, payload size    │    │
│  │  Energy Profiler    — wake locks, GPS, network radio    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ДОПОЛНИТЕЛЬНЫЕ ИНСТРУМЕНТЫ:                                    │
│  • Perfetto           — системный tracing (ui.perfetto.dev)     │
│  • Profile GPU Rendering — визуальные бары на экране           │
│  • Layout Inspector   — Compose recomposition analysis          │
│  • Macrobenchmark     — автоматизированные измерения           │
│  • LeakCanary         — runtime детекция memory leaks          │
│                                                                   │
│  ОСОБЕННОСТИ:                                                    │
│  • Интегрирован в IDE                                           │
│  • Удобный unified timeline                                     │
│  • Быстрый доступ при debug сессии                              │
│  • Экспорт в Perfetto для глубокого анализа                     │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Архитектурное сравнение

```
iOS Workflow:
┌──────────┐    Cmd+I    ┌─────────────┐    Select    ┌───────────┐
│  Xcode   │────────────►│ Instruments │─────────────►│  Template │
│          │             │    .app     │              │           │
└──────────┘             └─────────────┘              └───────────┘
                               │
                               ▼
                     ┌─────────────────┐
                     │   Recording &   │
                     │    Analysis     │
                     └─────────────────┘

Android Workflow:
┌──────────────────────────────────────────────────────────────────┐
│                    Android Studio                                 │
│  ┌──────────────┐              ┌───────────────────────────────┐ │
│  │    Editor    │              │         Profiler Tab          │ │
│  │              │              │  ┌─────────────────────────┐  │ │
│  │              │◄────────────►│  │ CPU │ Memory │ Network │  │ │
│  │              │   Integrated │  └─────────────────────────┘  │ │
│  └──────────────┘              └───────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. CPU Profiling — Сравнение

### Методы сбора данных

| Характеристика | iOS Time Profiler | Android CPU Profiler |
|----------------|-------------------|----------------------|
| **Sampling** | 1ms intervals | Sample Java (~100us) |
| **Tracing** | Через os_signpost | Trace Java (exact) |
| **Native Code** | Полная поддержка | Sample C++ |
| **System Calls** | System Trace template | System Trace mode |
| **Overhead** | Низкий (sampling) | Зависит от режима |

### iOS: Time Profiler

```swift
// Запуск: Xcode → Product → Profile → Time Profiler

// Как читать Call Tree:
// Weight = время выполнения функции + всех вызываемых функций
// Self Weight = время только в этой функции

// ❌ ПРОБЛЕМА: Blocking main thread
class BadViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Time Profiler покажет эту функцию как hotspot
        let data = loadDataSynchronously()  // 500ms на main thread!
        processData(data)  // ещё 200ms!
    }
}

// ✅ РЕШЕНИЕ: Async loading
class GoodViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        Task {
            let data = try await loadDataAsync()
            await MainActor.run {
                processData(data)
            }
        }
    }
}
```

### Android: CPU Profiler

```kotlin
// Запуск: View → Tool Windows → Profiler → CPU

// Режимы записи:
// 1. Sample Java Methods - для общего профилирования
// 2. Trace Java Methods - для точного timing
// 3. Sample C/C++ Functions - для native кода
// 4. Trace System Calls - для scheduling и I/O

// ❌ ПРОБЛЕМА: Тяжёлые операции на main thread
class BadActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // CPU Profiler покажет main thread занятым
        val users = database.getAllUsersSync()  // ANR риск!
        adapter.submitList(users)
    }
}

// ✅ РЕШЕНИЕ: Coroutines
class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val users = withContext(Dispatchers.IO) {
                database.getAllUsers()
            }
            adapter.submitList(users)
        }
    }
}
```

### Визуализация Call Trees

```
iOS Time Profiler:                      Android CPU Profiler:

Call Tree                               Call Chart (Top Down)
┌────────────────────────────────┐     ┌────────────────────────────────┐
│ Weight  Self   Symbol          │     │ Total  Self   Method           │
├────────────────────────────────┤     ├────────────────────────────────┤
│ 850ms   10ms  main             │     │ 850ms  10ms  onCreate()        │
│ └840ms  5ms   viewDidLoad      │     │ └840ms 5ms   loadData()        │
│   └835ms 15ms  loadData        │     │   └835ms 20ms parseJson()      │
│     └820ms 200ms parseJSON     │     │     └800ms 800ms decode()      │
│       └620ms 620ms decode      │     │                                │
└────────────────────────────────┘     └────────────────────────────────┘

Flame Graph (обе платформы поддерживают):

     ┌──────────────────────────────────────────────────────────┐
     │                        main / onCreate                    │
     ├──────────────────────────────────────────────────────────┤
     │                         loadData                          │
     ├────────────────────────────────────────┬─────────────────┤
     │              parseJSON                  │   setupUI       │
     ├────────────────────────────────────────┼─────────────────┤
     │                decode                   │  layout         │
     └────────────────────────────────────────┴─────────────────┘

     Ширина = время выполнения
     Глубина = call stack
```

### Custom Instrumentation

```swift
// iOS: os_signpost для custom intervals
import os

let log = OSLog(subsystem: "com.app", category: "Performance")

func loadImages() {
    os_signpost(.begin, log: log, name: "Image Loading")
    // ... loading code ...
    os_signpost(.end, log: log, name: "Image Loading")
}

// Видно в Instruments → os_signpost instrument
```

```kotlin
// Android: Trace API для custom sections
import android.os.Trace

fun loadImages() {
    Trace.beginSection("Image Loading")
    try {
        // ... loading code ...
    } finally {
        Trace.endSection()
    }
}

// Видно в Perfetto и System Trace
```

---

## 4. Memory Profiling — Сравнение

### Обзор возможностей

| Функция | iOS | Android |
|---------|-----|---------|
| **Live Memory** | Debug Gauges | Memory Profiler timeline |
| **Heap Dump** | Memory Graph Debugger | Capture Heap Dump |
| **Allocations** | Allocations instrument | Record Allocations |
| **Leak Detection** | Leaks instrument | LeakCanary (library) |
| **Retain Cycles** | Memory Graph визуализация | Reference chains |

### iOS: Memory Graph Debugger

```swift
// Запуск: Debug → Debug Memory Graph (во время debug сессии)

// Что показывает:
// • Все живые объекты с типами
// • Reference graph (кто кого держит)
// • Retain cycles с визуализацией
// • Purple = potential issues

// ❌ Типичный retain cycle
class DetailViewController: UIViewController {
    var viewModel: DetailViewModel!

    override func viewDidLoad() {
        super.viewDidLoad()

        viewModel.onUpdate = { [self] data in  // ← STRONG capture!
            self.updateUI(with: data)
        }
    }
}

class DetailViewModel {
    var onUpdate: ((Data) -> Void)?  // Strong reference to closure
}

// Memory Graph покажет:
// DetailViewController ←──┐
//         │               │ strong
//         │ strong        │
//         ▼               │
//   DetailViewModel ──────┘
//         │      closure captures self
//         ▼
//     Closure

// ✅ РЕШЕНИЕ: weak self
viewModel.onUpdate = { [weak self] data in
    self?.updateUI(with: data)
}
```

### Android: Memory Profiler + LeakCanary

```kotlin
// Memory Profiler: View → Tool Windows → Profiler → Memory

// Heap Dump показывает:
// • Java heap: все Java объекты
// • Native heap: native allocations
// • Graphics: GPU buffers
// • Stack: thread stacks
// • Code: compiled code

// LeakCanary: автоматическая детекция
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
}

// ❌ Типичная утечка: статическая ссылка
object DataHolder {
    var currentActivity: Activity? = null  // LEAK!
}

class MainActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        DataHolder.currentActivity = this  // Activity никогда не освободится
    }
}

// LeakCanary покажет notification:
// "MainActivity leaked! Reference chain:
//  DataHolder.currentActivity → MainActivity"

// ✅ РЕШЕНИЕ: очистка ссылок
override fun onDestroy() {
    super.onDestroy()
    if (DataHolder.currentActivity === this) {
        DataHolder.currentActivity = null
    }
}
```

### Паттерны утечек на обеих платформах

```
┌─────────────────────────────────────────────────────────────────┐
│               ОБЩИЕ ПАТТЕРНЫ MEMORY LEAKS                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. CLOSURE CAPTURES                                             │
│  ┌────────────────────────────────┬────────────────────────────┐│
│  │           iOS                  │          Android           ││
│  ├────────────────────────────────┼────────────────────────────┤│
│  │ closure = { self.doWork() }   │ callback = { doWork() }    ││
│  │ // strong capture              │ // implicit this capture   ││
│  │                                │                            ││
│  │ Fix: [weak self]               │ Fix: weak reference        ││
│  └────────────────────────────────┴────────────────────────────┘│
│                                                                   │
│  2. DELEGATE/LISTENER PATTERNS                                   │
│  ┌────────────────────────────────┬────────────────────────────┐│
│  │           iOS                  │          Android           ││
│  ├────────────────────────────────┼────────────────────────────┤│
│  │ var delegate: MyDelegate?     │ var listener: Listener?    ││
│  │ // should be weak              │ // should clear onDestroy  ││
│  │                                │                            ││
│  │ Fix: weak var delegate        │ Fix: listener = null       ││
│  └────────────────────────────────┴────────────────────────────┘│
│                                                                   │
│  3. SINGLETON/STATIC REFERENCES                                  │
│  ┌────────────────────────────────┬────────────────────────────┐│
│  │           iOS                  │          Android           ││
│  ├────────────────────────────────┼────────────────────────────┤│
│  │ static var current: VC?       │ object { var ctx: Ctx? }   ││
│  │ // VC never deallocated        │ // Context leaked          ││
│  │                                │                            ││
│  │ Fix: weak reference            │ Fix: applicationContext    ││
│  └────────────────────────────────┴────────────────────────────┘│
│                                                                   │
│  4. TIMER/OBSERVER NOT INVALIDATED                               │
│  ┌────────────────────────────────┬────────────────────────────┐│
│  │           iOS                  │          Android           ││
│  ├────────────────────────────────┼────────────────────────────┤│
│  │ Timer.scheduledTimer(...)     │ Handler().postDelayed(...) ││
│  │ // not invalidated in deinit   │ // not removed onDestroy   ││
│  │                                │                            ││
│  │ Fix: timer.invalidate()        │ Fix: handler.removeCallbacks│
│  └────────────────────────────────┴────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 5. Network Profiling — Сравнение

### Встроенные инструменты

| Возможность | iOS Network Profiler | Android Network Profiler |
|-------------|---------------------|--------------------------|
| **Request Timeline** | Да | Да |
| **Response Body** | Да | Да (до API 26) |
| **Latency** | Да | Да |
| **Payload Size** | Да | Да |
| **SSL Inspection** | Требует proxy | Требует proxy |

### iOS: Network Instrument

```swift
// В Instruments выбираем Network template

// Показывает:
// • Все HTTP/HTTPS запросы
// • Timing: DNS, Connect, TLS, Request, Response
// • Размер payload
// • Response codes

// Для детального анализа используем Charles Proxy или Proxyman

// URLSession автоматически инструментирована
let task = URLSession.shared.dataTask(with: url) { data, response, error in
    // Instruments увидит этот запрос
}
task.resume()

// os_signpost для custom network spans
os_signpost(.begin, log: networkLog, name: "API Call", "%{public}s", endpoint)
// ... network call ...
os_signpost(.end, log: networkLog, name: "API Call")
```

### Android: Network Profiler

```kotlin
// View → Tool Windows → Profiler → Network

// Показывает:
// • Timeline всех requests
// • Thread, который инициировал запрос
// • Call stack
// • Request/Response details

// OkHttp автоматически инструментирован
val client = OkHttpClient.Builder()
    .addInterceptor(HttpLoggingInterceptor())  // для logcat
    .build()

// Для production используем Chucker
debugImplementation("com.github.chuckerteam.chucker:library:4.0.0")

// Custom events через Trace
Trace.beginSection("API: $endpoint")
try {
    api.getData()
} finally {
    Trace.endSection()
}
```

### Сравнение Network Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                  NETWORK DEBUGGING WORKFLOW                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  iOS                              Android                        │
│  ───                              ───────                        │
│                                                                   │
│  1. Quick Look:                   1. Quick Look:                 │
│     Debug Gauges (Network)           Network Profiler timeline   │
│                                                                   │
│  2. Detailed Analysis:            2. Detailed Analysis:          │
│     Network instrument               Network Profiler details    │
│     + Charles Proxy                  + Chucker library           │
│                                                                   │
│  3. SSL Inspection:               3. SSL Inspection:             │
│     Charles + certificate            Network Security Config +   │
│     trust settings                   debug certificate           │
│                                                                   │
│  4. Production Monitoring:        4. Production Monitoring:      │
│     MetricKit (network metrics)      Firebase Performance        │
│     Custom backend logs              Custom network traces       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. Production Monitoring — MetricKit vs Firebase Performance

### Сравнение решений

| Аспект | iOS (MetricKit) | Android (Firebase) |
|--------|-----------------|-------------------|
| **Интеграция** | Встроено в iOS 13+ | Требует SDK |
| **Данные** | Daily aggregated reports | Real-time + aggregated |
| **Custom Traces** | Через os_signpost | performance.trace() |
| **Crash Reporting** | MXDiagnosticPayload | Firebase Crashlytics |
| **Dashboard** | Xcode Organizer | Firebase Console |
| **Стоимость** | Бесплатно | Бесплатный tier |

### iOS: MetricKit

```swift
import MetricKit

// AppDelegate или dedicated class
class PerformanceMonitor: NSObject, MXMetricManagerSubscriber {

    static let shared = PerformanceMonitor()

    func startMonitoring() {
        MXMetricManager.shared.add(self)
    }

    // Вызывается раз в ~24 часа с агрегированными данными
    func didReceive(_ payloads: [MXMetricPayload]) {
        for payload in payloads {
            // CPU metrics
            if let cpuMetrics = payload.cpuMetrics {
                let cumulativeCPU = cpuMetrics.cumulativeCPUTime
                analytics.log("cpu_time", value: cumulativeCPU)
            }

            // Memory metrics
            if let memoryMetrics = payload.memoryMetrics {
                let peakMemory = memoryMetrics.peakMemoryUsage
                analytics.log("peak_memory", value: peakMemory)
            }

            // Launch metrics
            if let launchMetrics = payload.applicationLaunchMetrics {
                let coldLaunch = launchMetrics.histogrammedTimeToFirstDraw
                analytics.log("cold_launch", histogram: coldLaunch)
            }

            // Hang metrics (> 500ms main thread blocks)
            if let hangMetrics = payload.applicationResponsivenessMetrics {
                let hangRate = hangMetrics.applicationHangTime
                analytics.log("hang_time", value: hangRate)
            }
        }
    }

    // Diagnostic reports (crashes, hangs with stack traces)
    func didReceive(_ payloads: [MXDiagnosticPayload]) {
        for payload in payloads {
            if let crashDiagnostics = payload.crashDiagnostics {
                for crash in crashDiagnostics {
                    // Stack trace available
                    let callStack = crash.callStackTree
                    crashReporter.send(callStack)
                }
            }

            if let hangDiagnostics = payload.hangDiagnostics {
                for hang in hangDiagnostics {
                    // Where was the hang?
                    let callStack = hang.callStackTree
                    analytics.log("hang_diagnostic", stack: callStack)
                }
            }
        }
    }
}
```

### Android: Firebase Performance

```kotlin
// build.gradle.kts
plugins {
    id("com.google.firebase.firebase-perf")
}

dependencies {
    implementation("com.google.firebase:firebase-perf-ktx")
}

// Автоматически собирает:
// • App startup time
// • Screen rendering (frozen/slow frames)
// • HTTP/S network requests

// Custom Traces
class CheckoutViewModel : ViewModel() {

    fun processCheckout(cart: Cart) {
        val trace = Firebase.performance.newTrace("checkout_flow")
        trace.start()

        viewModelScope.launch {
            try {
                // Metrics внутри trace
                trace.putMetric("cart_items", cart.items.size.toLong())

                val paymentResult = processPayment(cart)
                trace.putAttribute("payment_method", paymentResult.method)

                if (paymentResult.success) {
                    trace.putMetric("success", 1)
                } else {
                    trace.putMetric("failure", 1)
                }

            } finally {
                trace.stop()
            }
        }
    }
}

// Network monitoring (автоматически для OkHttp)
// Или manual для custom clients:
val metric = Firebase.performance.newHttpMetric(
    url,
    FirebasePerformance.HttpMethod.GET
)
metric.start()
// ... request ...
metric.setHttpResponseCode(response.code)
metric.setResponsePayloadSize(response.body?.contentLength() ?: 0)
metric.stop()
```

### Production Monitoring Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              PRODUCTION MONITORING STACK                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  iOS Stack:                       Android Stack:                 │
│  ──────────                       ─────────────                  │
│                                                                   │
│  ┌─────────────────┐              ┌─────────────────┐            │
│  │    MetricKit    │              │ Firebase Perf   │            │
│  │   (Built-in)    │              │    (SDK)        │            │
│  └────────┬────────┘              └────────┬────────┘            │
│           │                                │                      │
│           ▼                                ▼                      │
│  ┌─────────────────┐              ┌─────────────────┐            │
│  │ Xcode Organizer │              │ Firebase Console│            │
│  │   + Custom      │              │ + Play Console  │            │
│  │   Analytics     │              │   Vitals        │            │
│  └─────────────────┘              └─────────────────┘            │
│                                                                   │
│  Общие метрики:                                                  │
│  • Startup time (cold/warm/hot)                                  │
│  • Crash rate                                                    │
│  • ANR/Hang rate                                                 │
│  • Frame rendering (jank)                                        │
│  • Memory usage                                                  │
│  • Network latency                                               │
│                                                                   │
│  Alerting:                                                       │
│  ├─ iOS:  App Store Connect thresholds                          │
│  └─ Android: Firebase alerts + Play Console warnings             │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. Шесть распространённых ошибок профилирования

### Ошибка 1: Профилирование debug build

```
❌ НЕПРАВИЛЬНО:
"Запускаю Time Profiler на debug build из Xcode..."
"CPU Profiler показывает медленный код..."

Результаты НЕТОЧНЫЕ потому что:
• Debug: нет оптимизаций компилятора
• Debug: дополнительные assertions и проверки
• Debug: debugger overhead
• Debug: отсутствует R8/Swift optimization

✅ ПРАВИЛЬНО:
iOS: Profile конфигурация или Release с debug symbols
Android: Release build с android:profileable="true"
```

```swift
// iOS: Убедитесь что используете Release
// Edit Scheme → Profile → Build Configuration → Release
```

```kotlin
// Android: AndroidManifest.xml
<application
    android:profileable="true"
    android:profileableByShell="true">
```

### Ошибка 2: Профилирование на эмуляторе

```
❌ НЕПРАВИЛЬНО:
"iPhone Simulator показывает хороший FPS..."
"Android Emulator — всё быстро работает..."

ПРОБЛЕМЫ:
• Simulator/Emulator используют CPU/GPU хоста
• Нет thermal throttling
• Другая memory архитектура
• iOS Simulator = x86, реальные устройства = ARM

✅ ПРАВИЛЬНО:
Всегда профилируем на РЕАЛЬНОМ устройстве!
Желательно на low-end device (iPhone SE, бюджетный Android)
```

### Ошибка 3: Игнорирование cold start vs warm start

```
❌ НЕПРАВИЛЬНО:
"Startup 200ms — отлично!"
(измеряли warm start после 10 запусков)

РЕАЛЬНОСТЬ:
• Cold start: процесс создаётся с нуля
• Warm start: процесс в памяти, Activity/VC пересоздаётся
• Hot start: всё в памяти, только выводим на экран

✅ ПРАВИЛЬНО:
Измеряем ВСЕ три сценария отдельно:

iOS:                              Android:
────                              ───────
Cold: Force Quit → Launch         Cold: adb shell am force-stop
Warm: Background → Foreground     Warm: Home → Recent Apps → Launch
Hot: Recent Apps → Resume         Hot: Home → Launch (same process)
```

### Ошибка 4: Одноразовое измерение

```
❌ НЕПРАВИЛЬНО:
"Time Profiler показал 150ms для этой функции"
(одно измерение)

ПРОБЛЕМЫ:
• JIT компиляция (особенно Android)
• Кэширование
• Background процессы
• Thermal state устройства
• GC паузы

✅ ПРАВИЛЬНО:
Минимум 10 итераций + статистика:

// iOS: XCTest Performance
func testStartupPerformance() throws {
    measure(metrics: [XCTApplicationLaunchMetric()]) {
        XCUIApplication().launch()
    }
}

// Android: Macrobenchmark
@Test
fun coldStartup() = benchmarkRule.measureRepeated(
    packageName = "com.app",
    iterations = 10,  // минимум!
    startupMode = StartupMode.COLD
) { ... }
```

### Ошибка 5: Профилирование не того что болит

```
❌ НЕПРАВИЛЬНО:
"Оптимизировал этот метод на 50%!"
(метод занимал 1% общего времени)

ЗАКОН АМДАЛА:
Если оптимизируешь 1% кода на 50%,
общее улучшение = 0.5%

✅ ПРАВИЛЬНО:
1. Сначала найди TOP bottlenecks (> 10% времени)
2. Оптимизируй самые тяжёлые части
3. Перемеряй после каждого изменения

Time Profiler / CPU Profiler:
Смотри на "Weight" или "Total Time"
Начинай с самых тяжёлых функций
```

### Ошибка 6: Не использовать production данные

```
❌ НЕПРАВИЛЬНО:
"На моём iPhone 15 Pro Max всё летает!"
"В dev environment всё быстро!"

РЕАЛЬНОСТЬ:
• Пользователи на старых устройствах
• Разные условия сети
• Большие датасеты (годы использования)
• Thermal throttling в жару

✅ ПРАВИЛЬНО:
Используй MetricKit / Firebase Performance для РЕАЛЬНЫХ данных:

// Смотри на percentiles, не averages:
P50: 200ms  ← "Средний" пользователь
P90: 500ms  ← 10% пользователей хуже
P99: 2000ms ← 1% страдает очень сильно

Оптимизируй P90/P99, не P50!
```

---

## 8. Три ментальные модели

### Модель 1: "Профайлер = МРТ, не лечение"

```
┌─────────────────────────────────────────────────────────────────┐
│                    МРТ vs ЛЕЧЕНИЕ                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Профайлер показывает ГДЕ болит, но не КАК лечить               │
│                                                                   │
│  1. ДИАГНОСТИКА (Профайлер):                                     │
│     "CPU 100% в parseJSON()"                                     │
│     "Memory растёт при скролле"                                  │
│     "Network latency 500ms"                                      │
│                                                                   │
│  2. АНАЛИЗ (Разработчик):                                        │
│     "parseJSON вызывается 1000 раз в цикле"                      │
│     "Изображения не кэшируются"                                  │
│     "API делает N+1 запросов"                                    │
│                                                                   │
│  3. ЛЕЧЕНИЕ (Код):                                               │
│     "Batch parsing + кэш результатов"                            │
│     "Image cache + lazy loading"                                 │
│     "GraphQL / batch endpoint"                                   │
│                                                                   │
│  Профайлер ≠ Автоматический фикс                                │
│  Профайлер = Информация для принятия решений                    │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Модель 2: "Zoom In / Zoom Out"

```
┌─────────────────────────────────────────────────────────────────┐
│                    УРОВНИ МАСШТАБА                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ZOOM OUT — Системный уровень:                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  System Trace / Perfetto                                  │    │
│  │  • Все процессы                                           │    │
│  │  • Scheduling                                             │    │
│  │  • IPC                                                    │    │
│  │  • I/O                                                    │    │
│  │  Вопрос: "Почему система тормозит?"                       │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           ↓                                      │
│  MEDIUM — Уровень приложения:                                    │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  Time Profiler / CPU Profiler                             │    │
│  │  • Threads                                                │    │
│  │  • Call stacks                                            │    │
│  │  • CPU time                                               │    │
│  │  Вопрос: "Какой код медленный?"                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           ↓                                      │
│  ZOOM IN — Уровень кода:                                         │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  os_signpost / Trace.beginSection                         │    │
│  │  • Конкретные функции                                     │    │
│  │  • Custom metrics                                         │    │
│  │  • Business logic timing                                  │    │
│  │  Вопрос: "Что именно в этой функции медленно?"            │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  Стратегия: Начни с Zoom Out → найди проблемную область         │
│            → Zoom In для детального анализа                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Модель 3: "Budget Frame Time"

```
┌─────────────────────────────────────────────────────────────────┐
│                    БЮДЖЕТ ВРЕМЕНИ КАДРА                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  60 FPS = 16.67ms на кадр                                        │
│  120 FPS (ProMotion) = 8.33ms на кадр                            │
│                                                                   │
│  Как распределяется время:                                       │
│                                                                   │
│  ┌──────────────────────────────────────────────────┐           │
│  │                   16.67ms                         │           │
│  ├───────┬───────┬───────┬───────┬─────────────────┤           │
│  │ Input │Layout │ Draw  │ GPU   │    Свободно     │           │
│  │  2ms  │  3ms  │  4ms  │  4ms  │      3.67ms     │           │
│  └───────┴───────┴───────┴───────┴─────────────────┘           │
│                                                                   │
│  Если хоть одна фаза > бюджета → JANK (пропуск кадра)           │
│                                                                   │
│  iOS (Core Animation instrument):                                │
│  • Render Prepare                                                │
│  • Render Execute                                                │
│  • Display (vsync wait)                                          │
│                                                                   │
│  Android (Profile GPU Rendering bars):                           │
│  • Input (orange)                                                │
│  • Animation (red)                                               │
│  • Measure/Layout (yellow)                                       │
│  • Draw (green)                                                  │
│  • Sync/Upload (purple)                                          │
│  • GPU Execute (dark blue)                                       │
│  • Swap (light green)                                            │
│                                                                   │
│  Ключевое понимание:                                             │
│  Не "как быстро работает код",                                   │
│  а "укладывается ли код в БЮДЖЕТ времени"                        │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 9. Quiz — Проверь понимание

### Вопрос 1: Выбор инструмента

```
СЦЕНАРИЙ:
Пользователи жалуются что приложение "подвисает" на 2-3 секунды
при открытии детального экрана. Проблема воспроизводится
в debug сборке на эмуляторе.

Какой следующий шаг?

A) Сразу запустить Time Profiler / CPU Profiler на эмуляторе
B) Добавить логи в код для отладки
C) Собрать Release build и протестировать на реальном устройстве
D) Оптимизировать код детального экрана "на глаз"
```

<details>
<summary>Ответ</summary>

**C) Собрать Release build и протестировать на реальном устройстве**

Причины:
1. Debug build содержит overhead от debugger и отсутствие оптимизаций
2. Эмулятор не репрезентативен для реальной производительности
3. Проблема может не существовать в Release на реальном устройстве
4. Профилирование debug на эмуляторе даст ложные данные

После подтверждения проблемы на Release + реальном устройстве:
- iOS: Time Profiler на Release build
- Android: CPU Profiler с profileable Release build

</details>

### Вопрос 2: Memory Leak Detection

```
СЦЕНАРИЙ:
Memory Profiler показывает что после закрытия экрана профиля
ViewModel этого экрана остаётся в памяти.

Код (Kotlin):
class ProfileViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _user = MutableStateFlow<User?>(null)
    val user = _user.asStateFlow()

    init {
        repository.userUpdates.onEach { user ->
            _user.value = user
        }.launchIn(viewModelScope)
    }
}

class UserRepository {
    val userUpdates = MutableSharedFlow<User>()
    // ... обновляет userUpdates при изменениях
}

Где утечка?

A) viewModelScope не отменяется
B) MutableStateFlow держит ссылку
C) Repository — singleton, держит collector
D) Нужно использовать WeakReference для user
```

<details>
<summary>Ответ</summary>

**A) viewModelScope не отменяется — ЧАСТИЧНО**

Но основная проблема глубже:

**C) Repository — singleton, держит collector** — более точно

Если UserRepository — singleton, то:
1. `userUpdates.onEach { }.launchIn(viewModelScope)` создаёт collector
2. SharedFlow хранит ссылку на активных collectors пока они не отменены
3. viewModelScope должен отменяться при onCleared()...

НО если Repository реализован неправильно (держит сильные ссылки на listeners), ViewModel не освободится.

**Правильное решение:**

```kotlin
class ProfileViewModel(...) : ViewModel() {
    init {
        viewModelScope.launch {
            repository.userUpdates.collect { user ->
                _user.value = user
            }
        }
        // collect автоматически отменится при cancellation viewModelScope
    }
}
```

И убедиться что Repository использует SharedFlow корректно (не хранит сильных ссылок на collectors).

</details>

### Вопрос 3: Интерпретация данных

```
СЦЕНАРИЙ:
Macrobenchmark показывает следующие результаты для cold startup:

Iteration 1:  1200ms
Iteration 2:   450ms
Iteration 3:   420ms
Iteration 4:   440ms
Iteration 5:   430ms
Iteration 6:   425ms

Median: 437ms
P90: 450ms
P99: 1200ms

Какое значение использовать для оценки реального пользовательского опыта?

A) Median (437ms) — большинство пользователей увидят это
B) P90 (450ms) — 90% пользователей увидят это или лучше
C) P99 (1200ms) — нужно оптимизировать для worst case
D) Первая итерация аномалия, её нужно исключить
```

<details>
<summary>Ответ</summary>

**Зависит от контекста, но D) близко к правде**

Анализ:
1. Iteration 1 (1200ms) — скорее всего JIT warmup / first-run initialization
2. Iterations 2-6 (420-450ms) — стабильные, реальные значения

**Для оценки:**
- **P90 (450ms)** — хороший индикатор реального опыта большинства
- **Median (437ms)** — типичный опыт после первого запуска

**Для cold start реальных пользователей:**
- Многие увидят "Iteration 1" сценарий (первый запуск после установки)
- Нужно оптимизировать ОБА случая

**Правильная интерпретация:**
1. Baseline Profile поможет с первой итерацией (JIT warmup)
2. Median/P90 показывает "регулярный" cold start
3. P99 важен для понимания worst case

Если требование < 500ms — приложение проходит для большинства,
но первый запуск после установки всё ещё проблема.

</details>

---

## 10. Связанные материалы

### Внутренние ссылки

- [[ios-performance-profiling]] — глубокое погружение в Instruments
- [[android-performance-profiling]] — детали Android Studio Profiler и Perfetto

### Практические workflows

#### iOS: Полный цикл профилирования

```
1. Baseline измерение
   ├─ XCTest Performance Tests
   └─ App Launch template в Instruments

2. Идентификация проблемы
   ├─ Time Profiler для CPU
   ├─ Allocations/Leaks для Memory
   └─ Core Animation для UI

3. Оптимизация
   ├─ Исправление кода
   └─ Профилирование снова

4. Production мониторинг
   ├─ MetricKit subscription
   └─ Xcode Organizer review
```

#### Android: Полный цикл профилирования

```
1. Baseline измерение
   ├─ Macrobenchmark tests
   └─ Baseline Profile generation

2. Идентификация проблемы
   ├─ CPU Profiler / Perfetto
   ├─ Memory Profiler / LeakCanary
   └─ Layout Inspector для Compose

3. Оптимизация
   ├─ Исправление кода
   └─ Профилирование снова

4. Production мониторинг
   ├─ Firebase Performance
   └─ Play Console Vitals
```

### Чеклист перед релизом

```
┌─────────────────────────────────────────────────────────────────┐
│              PRE-RELEASE PERFORMANCE CHECKLIST                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  iOS:                              Android:                      │
│  ────                              ────────                      │
│  □ Cold start < 400ms              □ Cold start < 500ms          │
│  □ No Memory Graph warnings        □ LeakCanary clean            │
│  □ 60 FPS при скролле              □ < 5% janky frames           │
│  □ No main thread hangs            □ No StrictMode violations    │
│  □ MetricKit subscriber added      □ Firebase Perf integrated    │
│  □ Release build profiled          □ Baseline Profile generated  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Связь с другими темами

**[[ios-performance-profiling]]** — Instruments — это мощнейший инструмент профилирования от Apple, включающий Time Profiler, Allocations, Leaks, Core Animation и Metal System Trace. Заметка детально разбирает каждый инструмент, интерпретацию flame graphs, отладку hitches и MetricKit для production-мониторинга. Понимание Instruments необходимо для диагностики проблем производительности, которые проявляются только на iOS-таргете KMP-приложения.

**[[android-performance-profiling]]** — Android Studio Profiler объединяет CPU, Memory, Network и Energy profilers в единый интерфейс. Заметка раскрывает System Trace, Perfetto, Baseline Profiles, Macrobenchmark/Microbenchmark и Firebase Performance для production-метрик. Сравнение с Instruments в текущем файле показывает, что Android предоставляет более интегрированный в IDE опыт, тогда как Apple делает ставку на глубину анализа.

**[[performance-optimization]]** — Общие принципы оптимизации производительности (lazy loading, caching, batching, prefetching) применимы к обеим платформам. Заметка объясняет, как измерять и оптимизировать cold start, rendering performance и memory footprint. Это теоретическая основа, которая дополняет практическое сравнение инструментов профилирования из текущего файла.

---

## Источники и дальнейшее чтение

- **Meier R. (2022). *Professional Android*.** — Содержит главы по профилированию Android-приложений: CPU, memory, battery profiling, Baseline Profiles и Macrobenchmark. Помогает освоить Android Studio Profiler и интерпретировать результаты.
- **Neuburg M. (2023). *iOS Programming Fundamentals*.** — Раскрывает основы работы с Instruments, debugging в Xcode и оптимизацию производительности iOS-приложений. Даёт фундамент для эффективного использования профайлера Apple.
- **Martin R. (2017). *Clean Architecture*.** — Принципы разделения ответственности помогают изолировать «горячие» пути кода и оптимизировать их независимо от UI-слоя. Чистая архитектура облегчает профилирование, потому что бизнес-логика не переплетена с платформенным кодом.

---

## Проверь себя

> [!question]- Почему профилирование нужно проводить на Release-сборке, а не на Debug? Какие различия в производительности между ними?
> Debug-сборка: отключены оптимизации компилятора (-O0), включены assertions, debug symbols увеличивают размер, на iOS -- debug malloc guard pages, на Android -- debuggable flag отключает некоторые ART оптимизации. Release: compiler optimizations (inlining, dead code elimination), ProGuard/R8 (Android) убирает неиспользуемый код, Swift compiler optimizations (whole module). Разница производительности: 2-10x. Профилирование Debug даёт ложные bottlenecks, которые не существуют в Release.

> [!question]- Сценарий: cold start приложения занимает 3 секунды. Как диагностировать и оптимизировать на обеих платформах?
> iOS: Instruments App Launch template -> Time Profiler покажет hot functions в main()/applicationDidFinishLaunchingWithOptions. Типичные причины: синхронная инициализация DI, загрузка storyboard, Core Data migration. Android: Android Studio Profiler -> CPU -> App Startup, System Trace/Perfetto. Причины: MultiDex на старых API, тяжёлая Application.onCreate(), ContentProvider initialization. Оптимизации обе платформы: lazy initialization, async loading, Baseline Profiles (Android), pre-main dyld optimization (iOS -- уменьшить количество frameworks).

> [!question]- Чем MetricKit (iOS) отличается от Firebase Performance (Android) для production-мониторинга?
> MetricKit: Apple-provided, агрегированные метрики (24-часовые отчёты), включает CPU, memory, disk, network, hang rate, launch time, MXSignpost для custom traces. Данные приходят через MXMetricManagerSubscriber delegate. Firebase Performance: Google-provided, real-time dashboard, custom traces и HTTP/S network monitoring, automatic screen rendering metrics. Ключевое: MetricKit -- privacy-first (агрегированные данные), Firebase -- более детальный (per-user traces, но требует consent). В KMP-проектах используют Firebase для обеих платформ.

> [!question]- Почему Baseline Profiles важны для Android-приложений и есть ли аналог на iOS?
> Baseline Profiles: предкомпилированные DEX-методы (AOT) для критических путей приложения. Без них: ART использует JIT при первом запуске, что медленнее. С Baseline Profiles: cold start на 30-40% быстрее, рендеринг на 20% быстрее. Генерируются через Macrobenchmark тесты. iOS аналог: нет необходимости -- Swift компилируется в native code (AOT) всегда, нет JIT overhead. Но iOS имеет аналогичную оптимизацию через Profile-Guided Optimization (PGO) в Xcode.

---

## Ключевые карточки

Какие основные инструменты профилирования на iOS и Android?
?
iOS: Instruments (Time Profiler, Allocations, Leaks, Core Animation, Network, Energy), Memory Graph Debugger (Xcode), MetricKit (production). Android: Android Studio Profiler (CPU, Memory, Network, Energy), System Trace/Perfetto, LeakCanary (memory leaks), Firebase Performance (production), Macrobenchmark (automated). iOS Instruments -- standalone app, Android Profiler -- integrated в IDE.

Что такое Baseline Profiles на Android?
?
Baseline Profiles -- список критических methods/classes, предкомпилированных AOT при установке. Генерируются через Macrobenchmark тесты (BaselineProfileRule). Включаются в AAB. ART компилирует эти methods при install, минуя JIT. Результат: cold start на 30-40% быстрее, rendering на 20% быстрее. Обязательны для production-приложений.

Как измерить jank (пропущенные кадры) на обеих платформах?
?
iOS: Core Animation Instruments (frame drops), RenderLoop hitch detection, MetricKit MXAnimationMetric. Android: GPU Profiler (HWUI), JankStats API (Jetpack), System Trace (Choreographer frame timeline). Целевой показатель: <5% janky frames. 16.67ms budget для 60fps, 8.33ms для 120fps. Jank = frame rendering > budget.

Что такое MetricKit на iOS?
?
MetricKit -- Apple framework для сбора performance и diagnostic метрик в production. MXMetricPayload: CPU time, memory peaks, disk writes, network usage, launch time, hang rate. MXDiagnosticPayload: crash logs, hang diagnostics. Агрегируются за 24 часа, приходят через MXMetricManagerSubscriber. Privacy-first: данные анонимизированы. Доступен с iOS 13, расширен в iOS 14-17.

Как профилировать memory leaks на обеих платформах?
?
iOS: Memory Graph Debugger (Xcode, визуальный граф объектов), Instruments Leaks template, Instruments Allocations (generation analysis). Android: LeakCanary (автоматическое обнаружение, heap dump analysis), Android Studio Memory Profiler (heap dump, allocation tracking). Общий подход: найти объекты, которые должны быть deallocated но живы, отследить retain path/GC root path до источника утечки.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-memory-management]] | Memory management -- основная область профилирования |
| Углубиться | [[ios-performance-profiling]] | Instruments deep dive из раздела iOS |
| Смежная тема | [[android-performance-profiling]] | Android Studio Profiler из раздела Android |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |
