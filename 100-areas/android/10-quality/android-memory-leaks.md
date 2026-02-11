---
title: "Memory Leaks в Android: паттерны, обнаружение и предотвращение"
created: 2026-01-27
modified: 2026-01-27
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/memory
  - topic/performance
  - type/deep-dive
  - level/advanced
related:
  - "[[android-handler-looper]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-process-memory]]"
  - "[[android-state-management]]"
  - "[[android-compose]]"
  - "[[android-viewmodel-internals]]"
  - "[[android-bundle-parcelable]]"
cs-foundations: [garbage-collection, reference-counting, reachability-analysis, weak-reference, observer-pattern, graph-traversal]
prerequisites:
  - "[[android-activity-lifecycle]]"
  - "[[android-threading]]"
  - "[[android-process-memory]]"
---

# Memory Leaks в Android: паттерны, обнаружение и предотвращение

> **TL;DR:** Memory leak = объект удерживается в памяти после того, как он больше не нужен. Топ-7 причин: non-static inner class, Handler с delayed messages, незарегистрированные listeners, static references с Context, GlobalScope корутины, CustomView после detach, Compose lambda capture. **LeakCanary** — gold standard обнаружения: ObjectWatcher + WeakReference + ReferenceQueue → heap dump → Shark analysis → leak trace. Предотвращение: lifecycle-aware компоненты, WeakReference, viewModelScope, DisposableEffect (Compose).

---

## Зачем это нужно

### Проблема: невидимый враг производительности

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| OutOfMemoryError (OOM) | Объекты не освобождаются GC | Crash приложения |
| Постепенное замедление приложения | Рост потребления памяти | Пользователь уходит |
| ANR после долгого использования | GC Pause на большой куче | 5-секундный таймаут |
| Повышенное потребление батареи | Частые GC циклы | Негативные отзывы |
| Crash при ротации экрана | Activity leak × N ротаций | N × Activity в памяти |
| Фоновые утечки | Leaked Service/BroadcastReceiver | LMK не может освободить |

### Актуальность в 2024-2026

**Memory leaks — хроническая проблема Android:**

```
СТАТИСТИКА (2024-2025):
• Memory leaks — в ТОП-5 причин крашей в production
• ~70% Android-приложений имеют хотя бы 1 memory leak
• Средний memory leak: +2-20 МБ на каждую ротацию экрана
• Средний бюджет памяти Android-приложения: 128-512 МБ
• 5 ротаций × 20 МБ leak = 100 МБ потеряно = OOM

НОВЫЕ ВЫЗОВЫ В COMPOSE ERA:
• Lambda capture leaks — новый паттерн
• remember {} с долгоживущими ссылками
• ViewModel + Composable lambda = leak
• DisposableEffect как замена onDestroy()
```

**Что вы узнаете:**
1. Как работает GC и почему возникают leaks (GC Roots, reachability)
2. Топ-7 паттернов утечек с кодом и исправлениями
3. Java Reference Types: Strong → Soft → Weak → Phantom
4. LeakCanary: как работает изнутри (ObjectWatcher, Shark, heap dump)
5. Предотвращение: lifecycle-aware подходы, Compose patterns
6. Профилирование: Android Studio Memory Profiler

---

## Prerequisites

| Тема | Зачем | Где изучить |
|------|-------|-------------|
| **[[android-activity-lifecycle]]** | Leak привязан к lifecycle: Activity уничтожена но не собрана GC | Раздел Android |
| **[[android-process-memory]]** | Heap, GC, LMK — основы управления памятью | Раздел Android |
| **[[android-handler-looper]]** | Handler — один из главных источников leaks | Раздел Android |
| **Основы Java GC** | Garbage Collector, heap, object graph | CS foundations |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Memory Leak** | Объект удерживается в памяти, хотя больше не нужен | Гость, который не уходит после вечеринки — занимает место |
| **GC Root** | Стартовая точка для GC: если объект достижим от GC Root, он живой | Корни дерева — всё что связано с корнем, живёт |
| **Leak Trace** | Цепочка ссылок от GC Root до leaked объекта | Цепочка "кто кого держит" — как детектив ищет виновника |
| **Retained Object** | Объект, который должен быть собран GC, но не собран | Удерживаемый заложник — должен быть свободен, но кто-то его держит |
| **WeakReference** | Ссылка, не предотвращающая сборку GC | Визитная карточка — знаете адрес, но не удерживаете человека |
| **SoftReference** | Ссылка, очищаемая только при нехватке памяти | Запасной стул — убирают только когда места не хватает |
| **PhantomReference** | Ссылка для cleanup-операций после GC | Некролог — уведомление что объект "умер" |
| **ReferenceQueue** | Очередь, куда GC кладёт очищенные Reference | Почтовый ящик — уведомления о "смерти" объектов |
| **LeakCanary** | Библиотека для автоматического обнаружения memory leaks | Канарейка в шахте — предупреждает об опасности раньше всех |
| **Heap Dump** | Снимок всей кучи Java в файл (.hprof) | Фотография комнаты — видно кто занимает место |
| **ObjectWatcher** | Компонент LeakCanary, следящий за destroyed объектами | Охранник — проверяет ушли ли гости после вечеринки |

---

## 1. Как работает Garbage Collector в Android

### 1.1. GC Roots и Reachability Analysis

```
ПРИНЦИП РАБОТЫ GC:

GC не считает ссылки (reference counting).
GC проверяет ДОСТИЖИМОСТЬ от GC Roots.

GC ROOTS (стартовые точки):
┌─────────────────────────────────────────────────────┐
│ 1. Local variables на стеке активных потоков         │
│ 2. Static fields (Class → static field → object)    │
│ 3. JNI references (нативный код)                    │
│ 4. Активные Thread объекты                           │
│ 5. Объекты в synchronized блоках (monitors)          │
│ 6. System class loader                              │
└─────────────────────────────────────────────────────┘

REACHABILITY ANALYSIS:
GC Root A ─→ Object B ─→ Object C ─→ Object D
                                       ↑
                                  ДОСТИЖИМ = ЖИВОЙ

GC Root A ─→ Object B ─→ Object C
                              ✗─→ Object D (ссылка удалена)
                                       ↑
                                  НЕДОСТИЖИМ = МЁРТВЫЙ → GC собирает

MEMORY LEAK:
GC Root A ─→ Static field ─→ leaked Activity ─→ View hierarchy
                                                 (всё дерево View!)
                                       ↑
Leaked Activity ДОСТИЖИМА через static field
→ GC НЕ МОЖЕТ её собрать → LEAK!
```

### 1.2. Почему Memory Leak — особая проблема Android

```
ПОЧЕМУ ANDROID УЯЗВИМ К LEAKS:

1. ОГРАНИЧЕННАЯ ПАМЯТЬ
   ┌─────────────────────────────────────────────┐
   │ Desktop JVM: 2-16 ГБ heap                    │
   │ Android: 128-512 МБ (зависит от устройства) │
   │ Low-end: всего 64-128 МБ!                   │
   └─────────────────────────────────────────────┘

2. ЧАСТОЕ ПЕРЕСОЗДАНИЕ ОБЪЕКТОВ
   ┌─────────────────────────────────────────────┐
   │ Configuration change (ротация) =            │
   │   старая Activity уничтожается +             │
   │   новая Activity создаётся                   │
   │                                              │
   │ Если старая не собирается GC:                │
   │   1 ротация = 2 Activity в памяти            │
   │   5 ротаций = 6 Activity в памяти!           │
   │   Каждая Activity = View hierarchy + Bitmap  │
   └─────────────────────────────────────────────┘

3. ДОЛГОЖИВУЩИЕ ОБЪЕКТЫ
   ┌─────────────────────────────────────────────┐
   │ Singleton (живёт весь процесс) →             │
   │   держит Activity Context →                  │
   │   Activity не собирается →                   │
   │   LEAK на весь процесс                       │
   └─────────────────────────────────────────────┘
```

---

## 2. Топ-7 паттернов Memory Leaks

### 2.1. Non-Static Inner Class

**Проблема:** Внутренний (non-static) класс в Java/Kotlin имеет **неявную ссылку** на outer class (Activity).

```kotlin
// ❌ LEAK: Non-static inner class

class ProfileActivity : AppCompatActivity() {

    // MyTask — inner class, имеет неявную ссылку на ProfileActivity
    inner class MyTask : AsyncTask<Void, Void, String>() {
        override fun doInBackground(vararg params: Void?): String {
            Thread.sleep(30_000)  // 30 секунд работы
            return "result"
        }

        override fun onPostExecute(result: String) {
            // Обращаемся к Activity через неявную ссылку
            textView.text = result
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        MyTask().execute()
        // Пользователь поворачивает экран →
        // Activity уничтожается, но MyTask всё ещё бежит →
        // MyTask держит ссылку на старую Activity →
        // LEAK на 30 секунд!
    }
}
```

```kotlin
// ✅ ИСПРАВЛЕНИЕ: Три подхода

// Подход 1: Static nested class + WeakReference
class ProfileActivity : AppCompatActivity() {

    // НЕ inner — нет неявной ссылки на Activity
    private class MyTask(activity: ProfileActivity) : AsyncTask<Void, Void, String>() {
        // WeakReference — не предотвращает GC
        private val activityRef = WeakReference(activity)

        override fun doInBackground(vararg params: Void?): String {
            Thread.sleep(30_000)
            return "result"
        }

        override fun onPostExecute(result: String) {
            // Проверяем: Activity ещё жива?
            val activity = activityRef.get() ?: return  // Уже собрана GC — выходим
            activity.textView.text = result
        }
    }
}

// Подход 2 (СОВРЕМЕННЫЙ): Корутины с viewModelScope
class ProfileViewModel : ViewModel() {
    private val _result = MutableStateFlow<String?>(null)
    val result: StateFlow<String?> = _result.asStateFlow()

    fun loadData() {
        viewModelScope.launch {  // Автоматически отменяется при cleared()
            delay(30_000)
            _result.value = "result"
        }
    }
}

// Подход 3 (COMPOSE): LaunchedEffect
@Composable
fun ProfileScreen(viewModel: ProfileViewModel = viewModel()) {
    val result by viewModel.result.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.loadData()  // Отменяется при выходе из composition
    }

    result?.let { Text(it) }
}
```

### 2.2. Handler с Delayed Messages

**Проблема:** `Handler.postDelayed()` помещает Message в MessageQueue. Message держит ссылку на Handler, который (если inner class) держит ссылку на Activity.

```kotlin
// ❌ LEAK: Handler postDelayed

class SplashActivity : AppCompatActivity() {

    // Anonymous inner class → неявная ссылка на SplashActivity
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Сообщение будет в очереди 3 секунды
        handler.postDelayed({
            // Этот Runnable = anonymous inner class
            // → держит ссылку на SplashActivity
            startActivity(Intent(this, MainActivity::class.java))
            finish()
        }, 3000)

        // Если пользователь нажмёт "Назад" до истечения 3 секунд:
        // Activity destroyed, но Message в очереди держит Runnable →
        // Runnable держит Activity → LEAK!
    }
}

// ✅ ИСПРАВЛЕНИЕ: removeCallbacksAndMessages в onDestroy

class SplashActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handler.postDelayed(navigateRunnable, 3000)
    }

    // Отдельная ссылка для возможности удаления
    private val navigateRunnable = Runnable {
        startActivity(Intent(this, MainActivity::class.java))
        finish()
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)  // Удаляем ВСЕ сообщения!
    }
}

// ✅ СОВРЕМЕННАЯ АЛЬТЕРНАТИВА: lifecycleScope
class SplashActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            delay(3000)  // Автоматически отменяется при onDestroy
            startActivity(Intent(this@SplashActivity, MainActivity::class.java))
            finish()
        }
    }
}
```

### 2.3. Незарегистрированные Listeners / Observers

**Проблема:** Регистрация listener в объекте с большим lifecycle (Singleton, System Service) без последующей отписки.

```kotlin
// ❌ LEAK: Listener не отписан

class LocationActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // SensorManager — системный сервис, живёт весь процесс
        val sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        val sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)

        // Регистрируем this как listener
        sensorManager.registerListener(
            this as SensorEventListener,  // Activity = listener
            sensor,
            SensorManager.SENSOR_DELAY_NORMAL
        )
        // Забыли unregisterListener в onDestroy()!
        // SensorManager (живёт весь процесс) → держит Activity → LEAK!
    }
}

// ✅ ИСПРАВЛЕНИЕ: Всегда отписывайтесь

class LocationActivity : AppCompatActivity(), SensorEventListener {

    private lateinit var sensorManager: SensorManager

    override fun onResume() {
        super.onResume()
        sensorManager = getSystemService(SENSOR_SERVICE) as SensorManager
        val sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        sensorManager.registerListener(this, sensor, SensorManager.SENSOR_DELAY_NORMAL)
    }

    override fun onPause() {
        super.onPause()
        sensorManager.unregisterListener(this)  // Отписываемся!
    }

    override fun onSensorChanged(event: SensorEvent?) { /* ... */ }
    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) { /* ... */ }
}

// ✅ COMPOSE: DisposableEffect для автоматической отписки
@Composable
fun AccelerometerScreen() {
    val context = LocalContext.current

    DisposableEffect(Unit) {
        val sensorManager = context.getSystemService(SENSOR_SERVICE) as SensorManager
        val sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent?) { /* ... */ }
            override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) { /* ... */ }
        }
        sensorManager.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_NORMAL)

        onDispose {
            sensorManager.unregisterListener(listener)  // Автоматический cleanup!
        }
    }
}
```

### 2.4. Static References с Context

**Проблема:** Singleton или static поле хранит ссылку на Activity Context.

```kotlin
// ❌ LEAK: Singleton с Activity Context

object Analytics {
    private var context: Context? = null  // Static → живёт весь процесс

    fun init(context: Context) {
        this.context = context  // Если передан Activity Context → LEAK!
    }

    fun trackEvent(event: String) {
        // Используем context для получения device info
        val packageName = context?.packageName
    }
}

// В Activity:
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Analytics.init(this)  // ❌ Activity Context в Singleton!
        // Activity destroyed → Singleton всё ещё держит ссылку → LEAK!
    }
}

// ✅ ИСПРАВЛЕНИЕ: Application Context

object Analytics {
    private lateinit var appContext: Context

    fun init(context: Context) {
        // applicationContext — живёт столько же сколько процесс
        this.appContext = context.applicationContext  // ✅ Безопасно!
    }
}

// ✅ ЕЩЁ ЛУЧШЕ: Hilt DI
@Module
@InstallIn(SingletonComponent::class)
object AnalyticsModule {
    @Provides
    @Singleton
    fun provideAnalytics(
        @ApplicationContext context: Context  // Hilt гарантирует Application Context
    ): Analytics = Analytics(context)
}
```

### 2.5. Coroutines и GlobalScope

**Проблема:** `GlobalScope` не привязан к lifecycle — корутина живёт пока бежит, даже если Activity уничтожена.

```kotlin
// ❌ LEAK: GlobalScope захватывает Activity

class DownloadActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        GlobalScope.launch {  // Живёт вечно!
            val data = repository.downloadLargeFile()
            withContext(Dispatchers.Main) {
                // this@DownloadActivity — захвачена в lambda
                progressBar.visibility = View.GONE  // ❌ Activity может быть destroyed
                textView.text = "Downloaded"
            }
        }
    }
}

// ✅ ИСПРАВЛЕНИЕ: lifecycle-aware scopes

class DownloadActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // lifecycleScope — отменяется при onDestroy
        lifecycleScope.launch {
            val data = repository.downloadLargeFile()
            // Безопасно — корутина отменена если Activity destroyed
            progressBar.visibility = View.GONE
            textView.text = "Downloaded"
        }
    }
}

// ✅ ЕЩЁ ЛУЧШЕ: repeatOnLifecycle для Flow
class DownloadActivity : AppCompatActivity() {

    private val viewModel: DownloadViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Подписка активна только когда Activity STARTED+
                // Автоматически отписывается при STOPPED
                viewModel.downloadState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

### 2.6. WebView Leak

**Проблема:** WebView — один из самых "тяжёлых" Android компонентов. Он создаёт внутренние потоки, JS-движок и нативные ресурсы, которые могут не освободиться.

```kotlin
// ❌ LEAK: WebView в layout

class ArticleActivity : AppCompatActivity() {
    // WebView в XML layout → держит Activity Context
    // + Внутренние потоки WebView не завершаются при onDestroy
}

// ✅ ИСПРАВЛЕНИЕ: Программное создание с Application Context + cleanup

class ArticleActivity : AppCompatActivity() {

    private var webView: WebView? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_article)

        // Создаём WebView программно с Application Context
        webView = WebView(applicationContext).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
        }
        findViewById<FrameLayout>(R.id.web_container).addView(webView)
        webView?.loadUrl("https://example.com")
    }

    override fun onDestroy() {
        // Полный cleanup WebView
        webView?.let { wv ->
            wv.stopLoading()
            wv.clearHistory()
            wv.clearCache(true)
            wv.loadUrl("about:blank")
            wv.onPause()
            wv.removeAllViews()
            (wv.parent as? ViewGroup)?.removeView(wv)
            wv.destroy()
        }
        webView = null
        super.onDestroy()
    }
}
```

### 2.7. Compose: Lambda Capture Leak

**Проблема:** В Compose lambdas, переданные в ViewModel или remember, могут захватить ссылки на composition-scoped объекты.

```kotlin
// ❌ LEAK: Composable lambda в ViewModel

@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val context = LocalContext.current  // Activity Context

    // Lambda захватывает context (Activity)
    // ViewModel живёт дольше Activity → LEAK!
    LaunchedEffect(Unit) {
        viewModel.setCallback { message ->
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
            // context = Activity Context, захвачен в lambda
            // lambda хранится в ViewModel
            // ViewModel переживает Activity → LEAK!
        }
    }
}

// ✅ ИСПРАВЛЕНИЕ: DisposableEffect + cleanup

@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val context = LocalContext.current

    DisposableEffect(viewModel) {
        val callback: (String) -> Unit = { message ->
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        }
        viewModel.setCallback(callback)

        onDispose {
            viewModel.clearCallback()  // Очищаем ссылку!
        }
    }
}

// ✅ ЕЩЁ ЛУЧШЕ: Events через SharedFlow (без callback)
class UserViewModel : ViewModel() {
    private val _events = MutableSharedFlow<String>()
    val events = _events.asSharedFlow()

    fun showMessage(message: String) {
        viewModelScope.launch { _events.emit(message) }
    }
}

@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val context = LocalContext.current

    // Собираем events lifecycle-aware
    LaunchedEffect(Unit) {
        viewModel.events.collect { message ->
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        }
    }
    // LaunchedEffect автоматически отменяется при выходе из composition
}
```

---

## 3. Java Reference Types

### 3.1. Иерархия ссылок

```
JAVA REFERENCE TYPES (от сильной к слабой):

STRONG REFERENCE (обычная ссылка)
│  val activity = MainActivity()
│  → GC НИКОГДА не соберёт пока ссылка существует
│
├── SOFT REFERENCE
│   val softRef = SoftReference(bitmap)
│   → GC собирает ТОЛЬКО при нехватке памяти (перед OOM)
│   → Подходит для кэшей
│
├── WEAK REFERENCE
│   val weakRef = WeakReference(activity)
│   → GC собирает при ПЕРВОМ GC цикле (как только нет strong refs)
│   → Подходит для preventing leaks
│
└── PHANTOM REFERENCE
    val phantomRef = PhantomReference(obj, referenceQueue)
    → get() ВСЕГДА возвращает null
    → Уведомление о сборке через ReferenceQueue
    → Замена finalize()
```

### 3.2. Как WeakReference предотвращает leaks

```kotlin
// МЕХАНИЗМ WeakReference:

class Holder {
    // Strong: Activity НЕ будет собрана GC пока Holder жив
    var strongRef: Activity = activity

    // Weak: Activity БУДЕТ собрана GC даже если Holder жив
    var weakRef: WeakReference<Activity> = WeakReference(activity)
}

// ИСПОЛЬЗОВАНИЕ:
val activity = weakRef.get()  // Activity или null (если GC собрал)
if (activity != null) {
    // Activity ещё жива — можно использовать
    activity.updateUI()
} else {
    // Activity уже собрана GC — ничего не делаем
    // Это НОРМАЛЬНО и ОЖИДАЕМО
}
```

### 3.3. ReferenceQueue — механизм уведомления

```kotlin
// ReferenceQueue — основа работы LeakCanary

// Создаём очередь уведомлений
val queue = ReferenceQueue<Activity>()

// Создаём WeakReference с привязкой к очереди
val weakRef = WeakReference(activity, queue)

// Когда GC соберёт activity:
// 1. weakRef.get() вернёт null
// 2. weakRef будет помещён в queue
// 3. Мы можем проверить queue.poll() чтобы узнать что объект собран

// LeakCanary использует это так:
// 1. Создаёт WeakReference на destroyed Activity с ReferenceQueue
// 2. Ждёт 5 секунд
// 3. Проверяет: WeakReference попала в queue?
//    → ДА: объект собран GC, всё OK
//    → НЕТ: объект НЕ собран, потенциальный LEAK!
```

### 3.4. Сравнительная таблица

| Тип ссылки | Когда GC собирает | get() возвращает | ReferenceQueue | Use Case |
|------------|-------------------|-----------------|----------------|----------|
| **Strong** | Никогда (пока есть ссылка) | Всегда объект | N/A | Обычное использование |
| **Soft** | При нехватке памяти (перед OOM) | Объект или null | Опционально | Кэши изображений |
| **Weak** | При первом GC цикле | Объект или null | Опционально | Preventing leaks |
| **Phantom** | После финализации | Всегда null | Обязательно | Cleanup ресурсов |

---

## 4. LeakCanary: как работает изнутри

### 4.1. Архитектура LeakCanary 2

```
PIPELINE LEAKCANARY:

ЭТАП 1: WATCH (AppWatcher)
┌─────────────────────────────────────────────────────┐
│ Автоматически следит за:                             │
│ • Activity.onDestroy()   → watch(activity)          │
│ • Fragment.onDestroy()   → watch(fragment)           │
│ • Fragment.onDestroyView()→ watch(fragmentView)      │
│ • ViewModel.onCleared()  → watch(viewModel)         │
│                                                     │
│ ObjectWatcher:                                       │
│ → WeakReference(object, referenceQueue)             │
│ → UUID для каждого watched object                   │
│ → Map<UUID, KeyedWeakReference>                     │
└─────────────────────────────────────────────────────┘
         │
         ▼ (5 секунд + GC.trigger)
ЭТАП 2: DETECT (Retained Objects)
┌─────────────────────────────────────────────────────┐
│ Проверяем ReferenceQueue:                           │
│ → Для каждого reference в queue:                    │
│   → Удаляем из Map (объект собран, всё OK)         │
│ → Оставшиеся в Map = RETAINED (не собраны!)        │
│                                                     │
│ Threshold:                                          │
│ • App visible: 5 retained objects → dump            │
│ • App background: 1 retained object → dump          │
│ • Notification tap: dump немедленно                 │
└─────────────────────────────────────────────────────┘
         │
         ▼
ЭТАП 3: DUMP (Heap Dump)
┌─────────────────────────────────────────────────────┐
│ Debug.dumpHprofData(filePath)                       │
│ → Freezes app на короткое время                     │
│ → Сохраняет .hprof файл на диск                    │
│ → Toast: "Dumping heap, app will freeze"            │
└─────────────────────────────────────────────────────┘
         │
         ▼
ЭТАП 4: ANALYZE (Shark)
┌─────────────────────────────────────────────────────┐
│ Shark — heap analyzer (100% Kotlin):                │
│                                                     │
│ 1. Парсит .hprof файл                               │
│ 2. Находит retained objects по UUID                 │
│ 3. Для каждого retained object:                     │
│    → BFS от GC Roots                                │
│    → Находит КРАТЧАЙШИЙ путь (leak trace)          │
│    → Определяет "подозреваемых" в цепочке          │
│ 4. Вычисляет signature (SHA-1 от подозреваемых)    │
│ 5. Группирует leaks с одинаковым signature          │
└─────────────────────────────────────────────────────┘
         │
         ▼
ЭТАП 5: REPORT
┌─────────────────────────────────────────────────────┐
│ • Notification с количеством leaks                  │
│ • Logcat с полным leak trace                        │
│ • Классификация: Application Leak vs Library Leak   │
│ • UI с деталями в LeakCanary Activity               │
└─────────────────────────────────────────────────────┘
```

### 4.2. Подключение LeakCanary

```kotlin
// build.gradle.kts
dependencies {
    // Только для debug сборок! Не включайте в release
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
}

// Всё! Никакого кода инициализации не нужно.
// LeakCanary автоматически:
// 1. Регистрирует ActivityLifecycleCallbacks
// 2. Регистрирует FragmentLifecycleCallbacks
// 3. Начинает следить за destroyed объектами

// Для кастомных объектов:
class MyPresenter {
    fun destroy() {
        // Просим LeakCanary следить за этим объектом
        AppWatcher.objectWatcher.expectWeaklyReachable(
            this,
            "MyPresenter was destroyed"
        )
    }
}
```

### 4.3. Чтение Leak Trace

```
ПРИМЕР LEAK TRACE:

┌───────────────────────────────────────────────────────────┐
│ GC ROOT: thread (main)                                     │
│ │                                                          │
│ ├── com.example.app.MySingleton                            │
│ │   ↓ static instance                                     │
│ ├── com.example.app.MySingleton                            │
│ │   ↓ listener                                             │
│ ├── com.example.app.ProfileActivity                        │ ← LEAK!
│ │   Leaking: YES (Activity.mDestroyed is true)            │
│ │   ↓ mDecorView                                          │
│ ├── com.android.internal.policy.DecorView                  │
│ │   ↓ всё дерево View                                      │
│ └── ...                                                    │
│                                                            │
│ ЧТЕНИЕ:                                                    │
│ MySingleton (static, живёт весь процесс)                   │
│   → хранит listener                                        │
│   → listener = ProfileActivity (уже destroyed!)            │
│   → ProfileActivity не может быть собрана GC               │
│   → + вся View hierarchy                                   │
│                                                            │
│ РЕШЕНИЕ: Unregister listener в onDestroy()                 │
│          или использовать WeakReference для listener       │
└───────────────────────────────────────────────────────────┘
```

---

## 5. Предотвращение Memory Leaks

### 5.1. Чек-лист для каждого компонента

```
PREVENTION CHECKLIST:

ACTIVITY / FRAGMENT:
☐ Все listeners отписаны в onDestroy() / onDestroyView()
☐ Handler.removeCallbacksAndMessages(null) в onDestroy()
☐ Никакие Singleton не хранят Activity Context
☐ Корутины используют lifecycleScope, не GlobalScope
☐ WebView properly destroyed (если используется)

VIEWMODEL:
☐ Не хранит Context, View, Activity, Fragment
☐ Не хранит Composable lambdas
☐ Использует viewModelScope для корутин
☐ Repository получает Application Context через DI

COMPOSE:
☐ remember {} не хранит долгоживущие ссылки
☐ DisposableEffect с onDispose для cleanup
☐ LaunchedEffect с правильными keys
☐ Нет Composable lambdas в ViewModel
☐ collectAsStateWithLifecycle вместо collectAsState

SINGLETON / DI:
☐ Только Application Context (никогда Activity)
☐ @ApplicationContext в Hilt/Dagger
☐ Listener callbacks через WeakReference
☐ Очистка ресурсов при необходимости
```

### 5.2. Decision Tree: какой Context использовать

```
КАКОЙ CONTEXT ИСПОЛЬЗОВАТЬ?

Нужен для чего?
│
├── Show Dialog / Toast → Activity Context
│   (нужен Window token)
│
├── Inflate layout → Activity Context
│   (нужна Theme)
│
├── Start Activity → Любой Context
│   (но из non-Activity нужен FLAG_ACTIVITY_NEW_TASK)
│
├── Access Resources → Любой Context
│   (но Activity Context для правильной конфигурации)
│
├── Singleton / Repository → Application Context ✅
│   (живёт весь процесс, безопасно)
│
├── Database / File access → Application Context ✅
│   (не привязан к lifecycle Activity)
│
└── System Service → Application Context ✅
    (getSystemService работает с любым Context)
```

---

## 6. Android Studio Memory Profiler

### 6.1. Основные возможности

```
MEMORY PROFILER WORKFLOW:

1. CAPTURE HEAP DUMP
   ┌─────────────────────────────────────────┐
   │ Android Studio → Profiler → Memory      │
   │ → "Dump Java Heap" (📷 иконка)          │
   │ → Анализ аллокаций по классам           │
   │ → Фильтр по package вашего приложения  │
   └─────────────────────────────────────────┘

2. СРАВНЕНИЕ ДВУХ HEAP DUMPS
   ┌─────────────────────────────────────────┐
   │ Dump 1: До ротации экрана               │
   │ Dump 2: После ротации экрана            │
   │                                          │
   │ Если Activity count вырос:              │
   │ Dump 1: 1 × MainActivity               │
   │ Dump 2: 2 × MainActivity ← LEAK!       │
   └─────────────────────────────────────────┘

3. TRACK ALLOCATIONS
   ┌─────────────────────────────────────────┐
   │ Record → выполнить действие → Stop      │
   │ → Увидеть все аллокации за период       │
   │ → Stack trace каждой аллокации          │
   └─────────────────────────────────────────┘
```

### 6.2. Команды adb для диагностики

```bash
# Получить информацию о памяти приложения
adb shell dumpsys meminfo com.example.app

# Принудительный GC
adb shell am force-gc com.example.app

# Heap dump в файл
adb shell am dumpheap com.example.app /data/local/tmp/heap.hprof
adb pull /data/local/tmp/heap.hprof

# Мониторинг аллокаций в реальном времени
adb shell dumpsys meminfo -d com.example.app
```

---

## 7. ART Garbage Collector: Deep Dive

### 7.1. Эволюция GC в Android

```
ИСТОРИЯ GC В ANDROID:

Android 1.0-2.2 (Dalvik):
┌─────────────────────────────────────────────────────┐
│ • Stop-the-world GC                                 │
│ • Паузы 50-200ms на каждый GC цикл                 │
│ • Пользователь видел "заикания" UI                 │
│ • Heap fragmentation → OutOfMemoryError            │
└─────────────────────────────────────────────────────┘

Android 2.3-4.4 (Dalvik улучшенный):
┌─────────────────────────────────────────────────────┐
│ • Concurrent Mark Sweep (частично)                  │
│ • Паузы уменьшились до 5-10ms                      │
│ • Всё ещё stop-the-world для некоторых фаз        │
└─────────────────────────────────────────────────────┘

Android 5.0+ (ART):
┌─────────────────────────────────────────────────────┐
│ • Concurrent Copying GC (Android 8+)               │
│ • Generational collection                          │
│ • Паузы < 2ms для большинства операций             │
│ • Compacting GC — нет фрагментации                 │
│ • Read barriers для concurrent доступа             │
└─────────────────────────────────────────────────────┘
```

### 7.2. Структура Heap в ART

```
ART HEAP ARCHITECTURE:

┌─────────────────────────────────────────────────────────────────┐
│                        ART MANAGED HEAP                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐  ┌──────────────────────────────────┐│
│  │    YOUNG GENERATION   │  │         OLD GENERATION           ││
│  │    (Nursery Space)    │  │       (Main/Large Space)         ││
│  │                       │  │                                  ││
│  │  • Новые объекты      │  │  • Объекты, пережившие N GC     ││
│  │  • Частый Minor GC    │  │  • Редкий Major GC               ││
│  │  • Быстрая аллокация  │  │  • Large objects (> 12KB)       ││
│  │  • Bump pointer       │  │                                  ││
│  │  • ~2-4 MB            │  │  • Остальной heap                ││
│  └──────────────────────┘  └──────────────────────────────────┘│
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    IMAGE SPACE (read-only)                │  │
│  │  • Preloaded classes (framework)                         │  │
│  │  • Shared между процессами (Zygote)                       │  │
│  │  • Не участвует в GC                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    ZYGOTE SPACE (copy-on-write)          │  │
│  │  • Общие объекты от Zygote                               │  │
│  │  • Становится private при модификации                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

NATIVE HEAP (не управляется GC):
┌─────────────────────────────────────────────────────────────────┐
│  • Bitmap pixel data (до Android 8.0)                          │
│  • Direct ByteBuffer                                            │
│  • JNI allocations                                             │
│  • Graphics buffers                                             │
│  • Native libraries (.so)                                       │
│                                                                 │
│  ⚠️ Native memory leaks не видны в Java heap!                  │
│  ⚠️ Используйте Android Studio Native Memory Profiler          │
└─────────────────────────────────────────────────────────────────┘
```

### 7.3. GC Алгоритмы ART

```kotlin
// CONCURRENT COPYING GC (Android 8+):
// Основной алгоритм современного ART

/*
ФАЗЫ CONCURRENT COPYING:

1. INITIAL MARK (stop-the-world ~1ms)
   ┌────────────────────────────────────────────┐
   │ • Помечаем корни (GC Roots)                │
   │ • Очень короткая пауза                     │
   │ • Все потоки остановлены                    │
   └────────────────────────────────────────────┘

2. CONCURRENT MARK (параллельно с приложением)
   ┌────────────────────────────────────────────┐
   │ • GC thread обходит граф объектов          │
   │ • Приложение продолжает работать           │
   │ • Read barriers отслеживают изменения      │
   │ • Write barriers записывают мутации        │
   └────────────────────────────────────────────┘

3. CONCURRENT COPY (параллельно с приложением)
   ┌────────────────────────────────────────────┐
   │ • Живые объекты копируются в новое место  │
   │ • Compacting — нет фрагментации           │
   │ • Forwarding pointers обновляют ссылки    │
   └────────────────────────────────────────────┘

4. FINAL MARK (stop-the-world ~1ms)
   ┌────────────────────────────────────────────┐
   │ • Обрабатываем изменения с фазы 2-3       │
   │ • Финализируем копирование                │
   │ • Обновляем корневые ссылки               │
   └────────────────────────────────────────────┘

5. SWEEP (concurrent или stop-the-world)
   ┌────────────────────────────────────────────┐
   │ • Освобождаем старое пространство          │
   │ • Обновляем metadata                       │
   └────────────────────────────────────────────┘
*/

// Как увидеть GC в logcat:
// adb logcat -s "art"

/*
Примеры GC логов:

// Minor GC (молодое поколение):
I/art: Explicit concurrent copying GC freed 12340(1024KB) AllocSpace objects,
       2(64KB) LOS objects, 49% free, 12MB/24MB, paused 1.2ms total 23.4ms

// Major GC (полный heap):
I/art: Background concurrent copying GC freed 234567(8MB) AllocSpace objects,
       12(2MB) LOS objects, 38% free, 64MB/104MB, paused 2.1ms total 156ms

РАЗБОР ЛОГА:
• "concurrent copying" — алгоритм GC
• "freed 12340(1024KB)" — освобождено объектов (размер)
• "LOS objects" — Large Object Space
• "49% free" — свободно в heap
• "12MB/24MB" — используется/выделено
• "paused 1.2ms" — stop-the-world пауза
• "total 23.4ms" — общее время GC цикла
*/
```

### 7.4. GC Triggers и Tuning

```kotlin
// КОГДА СРАБАТЫВАЕТ GC:

/*
АВТОМАТИЧЕСКИЕ ТРИГГЕРЫ:

1. ALLOCATION FAILURE
   ┌────────────────────────────────────────────┐
   │ Heap заполнен → нужна память → GC          │
   │ Сначала Minor GC, потом Major если мало    │
   └────────────────────────────────────────────┘

2. CONCURRENT GC THRESHOLD
   ┌────────────────────────────────────────────┐
   │ Heap достиг порогового значения            │
   │ GC запускается в фоне, не блокируя app    │
   │ Порог: обычно 75% от max heap             │
   └────────────────────────────────────────────┘

3. EXPLICIT GC REQUEST
   ┌────────────────────────────────────────────┐
   │ System.gc() — hint, не гарантия           │
   │ Runtime.gc() — то же самое                │
   │ ART может проигнорировать!                │
   └────────────────────────────────────────────┘

4. NATIVE ALLOCATION PRESSURE
   ┌────────────────────────────────────────────┐
   │ Native memory растёт → GC для cleanup     │
   │ Bitmap, DirectByteBuffer triggers          │
   └────────────────────────────────────────────┘

5. BACKGROUND GC
   ┌────────────────────────────────────────────┐
   │ Приложение ушло в фон                      │
   │ ART запускает агрессивный GC              │
   │ Compacting для уменьшения footprint       │
   └────────────────────────────────────────────┘
*/

// Мониторинг GC программно:
class GcMonitor {

    private var lastGcTime = 0L
    private var gcCount = 0

    fun startMonitoring() {
        // Debug-only: отслеживаем GC события
        val runtime = Runtime.getRuntime()

        Thread {
            while (true) {
                val beforeFree = runtime.freeMemory()
                System.gc()  // Hint только!
                Thread.sleep(100)
                val afterFree = runtime.freeMemory()

                if (afterFree > beforeFree + 1_000_000) {
                    gcCount++
                    Log.d("GcMonitor", "GC detected #$gcCount, freed ${(afterFree - beforeFree) / 1024}KB")
                }

                Thread.sleep(5000)
            }
        }.start()
    }
}

// Получение информации о памяти:
fun getMemoryInfo(): String {
    val runtime = Runtime.getRuntime()
    val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
    val memoryInfo = ActivityManager.MemoryInfo()
    activityManager.getMemoryInfo(memoryInfo)

    return buildString {
        appendLine("=== JVM Heap ===")
        appendLine("Max heap: ${runtime.maxMemory() / 1024 / 1024} MB")
        appendLine("Total heap: ${runtime.totalMemory() / 1024 / 1024} MB")
        appendLine("Free in heap: ${runtime.freeMemory() / 1024 / 1024} MB")
        appendLine("Used heap: ${(runtime.totalMemory() - runtime.freeMemory()) / 1024 / 1024} MB")
        appendLine()
        appendLine("=== System Memory ===")
        appendLine("Available RAM: ${memoryInfo.availMem / 1024 / 1024} MB")
        appendLine("Total RAM: ${memoryInfo.totalMem / 1024 / 1024} MB")
        appendLine("Low memory: ${memoryInfo.lowMemory}")
        appendLine("Threshold: ${memoryInfo.threshold / 1024 / 1024} MB")
    }
}
```

### 7.5. GC и производительность

```
ВЛИЯНИЕ GC НА ПРОИЗВОДИТЕЛЬНОСТЬ:

┌─────────────────────────────────────────────────────────────────┐
│                     GC PAUSE IMPACT                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  60 FPS = 16.67ms на кадр                                      │
│                                                                 │
│  Frame budget:                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │████████████████████████████████████│     │              │   │
│  │        App work (14ms)             │ GC  │   Idle       │   │
│  │                                    │(2ms)│              │   │
│  └─────────────────────────────────────────────────────────┘   │
│  0ms                                16.67ms                     │
│                                                                 │
│  ✅ GC пауза 2ms → кадр успевает                               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │████████████████████████████████████████████│            │   │
│  │        App work (14ms)                      │   GC      │   │
│  │                                             │ (10ms)    │   │
│  └─────────────────────────────────────────────────────────┘   │
│  0ms                                16.67ms   │← FRAME DROPPED │
│                                                                 │
│  ❌ GC пауза 10ms → jank (заикание)                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ОПТИМИЗАЦИЯ АЛЛОКАЦИЙ:                                        │
│                                                                 │
│  Меньше аллокаций → Меньше GC → Меньше пауз → Плавный UI      │
│                                                                 │
│  ❌ ПЛОХО: аллокации в onDraw(), onBindViewHolder()            │
│  ✅ ХОРОШО: переиспользование объектов, Object Pool            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

```kotlin
// ANTI-PATTERNS: Аллокации в hot paths

// ❌ ПЛОХО: новый объект в каждом onDraw
class BadCustomView(context: Context) : View(context) {
    override fun onDraw(canvas: Canvas) {
        val paint = Paint()  // ❌ Аллокация каждый кадр!
        val rect = RectF(0f, 0f, width.toFloat(), height.toFloat())  // ❌
        canvas.drawRect(rect, paint)
    }
}

// ✅ ХОРОШО: переиспользование объектов
class GoodCustomView(context: Context) : View(context) {
    // Создаём один раз
    private val paint = Paint()
    private val rect = RectF()

    override fun onDraw(canvas: Canvas) {
        rect.set(0f, 0f, width.toFloat(), height.toFloat())  // Reuse
        canvas.drawRect(rect, paint)  // Reuse
    }
}

// ❌ ПЛОХО: строковые конкатенации в цикле
fun badStringBuilding(items: List<Item>): String {
    var result = ""
    for (item in items) {
        result += item.name + ", "  // ❌ Новая строка каждую итерацию!
    }
    return result
}

// ✅ ХОРОШО: StringBuilder
fun goodStringBuilding(items: List<Item>): String {
    return buildString {
        items.forEachIndexed { index, item ->
            if (index > 0) append(", ")
            append(item.name)
        }
    }
}

// ❌ ПЛОХО: Boxing в hot path
fun badBoxing(values: IntArray): List<Int> {
    return values.map { it }  // ❌ Каждый int → Integer (boxing)
}

// ✅ ХОРОШО: примитивные коллекции
// Используйте IntArray, LongArray или специализированные коллекции
// из библиотек (Eclipse Collections, Trove, fastutil)
```

---

## 8. Дополнительные паттерны Memory Leaks

### 8.1. InputMethodManager Leak

```kotlin
// InputMethodManager — известный системный leak в Android

/*
ПРОБЛЕМА:
InputMethodManager хранит ссылку на последний focused View.
Если этот View принадлежит Activity, которая уничтожается,
InputMethodManager продолжает держать ссылку.

Это СИСТЕМНЫЙ leak, который Google периодически фиксит,
но он появляется снова в разных версиях Android.
*/

// Workaround для старых версий Android:
class KeyboardLeakFixer {

    companion object {
        fun fixInputMethodManagerLeak(activity: Activity) {
            if (Build.VERSION.SDK_INT < Build.VERSION_CODES.Q) {
                // Только для Android < 10
                try {
                    val imm = activity.getSystemService(Context.INPUT_METHOD_SERVICE)
                        as? InputMethodManager ?: return

                    val currentFocus = activity.currentFocus
                    currentFocus?.let {
                        imm.hideSoftInputFromWindow(it.windowToken, 0)
                    }

                    // Reflection workaround (не рекомендуется, но иногда необходимо)
                    val viewField = InputMethodManager::class.java
                        .getDeclaredField("mServedView")
                    viewField.isAccessible = true
                    val view = viewField.get(imm) as? View
                    if (view?.context === activity) {
                        viewField.set(imm, null)
                    }
                } catch (e: Exception) {
                    Log.w("KeyboardLeakFixer", "Failed to fix IMM leak", e)
                }
            }
        }
    }
}

// Использование в BaseActivity:
abstract class BaseActivity : AppCompatActivity() {
    override fun onDestroy() {
        KeyboardLeakFixer.fixInputMethodManagerLeak(this)
        super.onDestroy()
    }
}
```

### 8.2. BroadcastReceiver Leak

```kotlin
// ❌ LEAK: BroadcastReceiver не отписан

class NetworkActivity : AppCompatActivity() {

    private val networkReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            // this имеет неявную ссылку на NetworkActivity
            updateNetworkStatus()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Регистрируем receiver
        registerReceiver(
            networkReceiver,
            IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        )
        // Забыли unregisterReceiver! → LEAK
    }
}

// ✅ ИСПРАВЛЕНИЕ: Отписка в правильном lifecycle методе

class NetworkActivity : AppCompatActivity() {

    private val networkReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            updateNetworkStatus()
        }
    }

    override fun onStart() {
        super.onStart()
        registerReceiver(
            networkReceiver,
            IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION),
            RECEIVER_NOT_EXPORTED  // Android 14+ требует флаг
        )
    }

    override fun onStop() {
        super.onStop()
        unregisterReceiver(networkReceiver)  // ✅ Обязательно!
    }
}

// ✅ СОВРЕМЕННЫЙ ПОДХОД: ConnectivityManager.NetworkCallback

class NetworkActivity : AppCompatActivity() {

    private lateinit var connectivityManager: ConnectivityManager

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            runOnUiThread { showOnline() }
        }

        override fun onLost(network: Network) {
            runOnUiThread { showOffline() }
        }
    }

    override fun onStart() {
        super.onStart()
        connectivityManager = getSystemService(ConnectivityManager::class.java)
        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()
        connectivityManager.registerNetworkCallback(request, networkCallback)
    }

    override fun onStop() {
        super.onStop()
        connectivityManager.unregisterNetworkCallback(networkCallback)
    }
}
```

### 8.3. Cursor Leak

```kotlin
// ❌ LEAK: Cursor не закрыт

fun badQueryUsers(): List<User> {
    val cursor = contentResolver.query(
        UsersContract.CONTENT_URI,
        null, null, null, null
    )
    // cursor не закрыт! → Native memory leak

    val users = mutableListOf<User>()
    while (cursor?.moveToNext() == true) {
        users.add(User(
            id = cursor.getLong(0),
            name = cursor.getString(1)
        ))
    }
    return users
    // cursor утёк — нативные ресурсы не освобождены
}

// ✅ ИСПРАВЛЕНИЕ: use {} автоматически закрывает

fun goodQueryUsers(): List<User> {
    return contentResolver.query(
        UsersContract.CONTENT_URI,
        null, null, null, null
    )?.use { cursor ->  // ✅ use автоматически вызовет close()
        generateSequence { if (cursor.moveToNext()) cursor else null }
            .map { User(id = it.getLong(0), name = it.getString(1)) }
            .toList()
    } ?: emptyList()
}

// ✅ СОВРЕМЕННЫЙ ПОДХОД: Room Database
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllUsers(): List<User>  // Room сам управляет Cursor

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>>  // Реактивно
}
```

### 8.4. Bitmap Leak

```kotlin
// BITMAP MEMORY MODEL:

/*
До Android 8.0 (API 26):
┌─────────────────────────────────────────────────────┐
│ Bitmap объект в Java Heap                           │
│ ↓                                                   │
│ Pixel data в Native Heap (через JNI)               │
│                                                     │
│ Проблема: GC видит маленький Java объект,          │
│ не видит большой native buffer                     │
│ → OOM даже при "свободной" Java памяти             │
└─────────────────────────────────────────────────────┘

Android 8.0+ (API 26+):
┌─────────────────────────────────────────────────────┐
│ Bitmap объект в Java Heap                           │
│ ↓                                                   │
│ Pixel data тоже в Java Heap (NativeAllocationReg.)│
│                                                     │
│ GC видит полный размер → корректный GC trigger    │
└─────────────────────────────────────────────────────┘
*/

// ❌ LEAK: Bitmap не переработан

class ImageActivity : AppCompatActivity() {
    private var bitmap: Bitmap? = null

    fun loadHugeImage() {
        bitmap = BitmapFactory.decodeResource(resources, R.drawable.huge_image)
        // 4000x3000 px × 4 bytes = 48 MB!
    }

    // При уничтожении Activity bitmap продолжает занимать память
    // пока GC не решит его собрать (а он может быть занят)
}

// ✅ ИСПРАВЛЕНИЕ: Явное освобождение и правильный lifecycle

class ImageActivity : AppCompatActivity() {
    private var bitmap: Bitmap? = null

    fun loadImage() {
        // 1. Сначала узнаём размер без декодирования
        val options = BitmapFactory.Options().apply {
            inJustDecodeBounds = true
        }
        BitmapFactory.decodeResource(resources, R.drawable.huge_image, options)

        // 2. Вычисляем sample size для уменьшения
        options.inSampleSize = calculateInSampleSize(options, reqWidth = 800, reqHeight = 600)
        options.inJustDecodeBounds = false

        // 3. Декодируем уменьшенную версию
        bitmap = BitmapFactory.decodeResource(resources, R.drawable.huge_image, options)
    }

    override fun onDestroy() {
        super.onDestroy()
        bitmap?.recycle()  // Явно освобождаем native memory
        bitmap = null
    }

    private fun calculateInSampleSize(
        options: BitmapFactory.Options,
        reqWidth: Int,
        reqHeight: Int
    ): Int {
        val (height, width) = options.outHeight to options.outWidth
        var inSampleSize = 1

        if (height > reqHeight || width > reqWidth) {
            val halfHeight = height / 2
            val halfWidth = width / 2

            while ((halfHeight / inSampleSize) >= reqHeight &&
                   (halfWidth / inSampleSize) >= reqWidth) {
                inSampleSize *= 2
            }
        }
        return inSampleSize
    }
}

// ✅ ЛУЧШИЙ ПОДХОД: Используйте библиотеки (Coil, Glide)

@Composable
fun UserAvatar(imageUrl: String) {
    AsyncImage(
        model = ImageRequest.Builder(LocalContext.current)
            .data(imageUrl)
            .crossfade(true)
            .size(Size.ORIGINAL)  // Или конкретный размер
            .build(),
        contentDescription = "Avatar",
        modifier = Modifier.size(48.dp)
    )
    // Coil автоматически:
    // - Управляет памятью
    // - Кэширует
    // - Отменяет при выходе из composition
}
```

### 8.5. Thread Leak

```kotlin
// ❌ LEAK: Thread держит ссылку на Activity

class DownloadActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        Thread {
            // this@DownloadActivity захвачена в lambda
            val data = downloadLargeFile()
            runOnUiThread {
                // Если Activity уничтожена, это безопасно вызовет crash
                // или будет держать Activity в памяти
                textView.text = data
            }
        }.start()
    }

    // Activity destroyed → Thread всё ещё бежит → LEAK
}

// ✅ ИСПРАВЛЕНИЕ: Lifecycle-aware подход с отменой

class DownloadActivity : AppCompatActivity() {

    private var downloadJob: Job? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        downloadJob = lifecycleScope.launch(Dispatchers.IO) {
            val data = downloadLargeFile()
            withContext(Dispatchers.Main) {
                // Если scope отменён, этот код не выполнится
                textView.text = data
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        downloadJob?.cancel()  // Явная отмена (хотя lifecycleScope сам отменит)
    }
}

// ✅ ПРОДВИНУТЫЙ: ViewModel + WorkManager для долгих операций

class DownloadViewModel : ViewModel() {
    private val workManager = WorkManager.getInstance(application)

    fun startDownload(url: String) {
        val request = OneTimeWorkRequestBuilder<DownloadWorker>()
            .setInputData(workDataOf("url" to url))
            .build()

        workManager.enqueue(request)
    }

    fun observeProgress(workId: UUID): Flow<WorkInfo?> {
        return workManager.getWorkInfoByIdFlow(workId)
    }
}
```

---

## 9. Production Debugging: Memory Issues

### 9.1. Crash Reporting Integration

```kotlin
// ИНТЕГРАЦИЯ С FIREBASE CRASHLYTICS

class MemoryMonitor(private val context: Context) {

    private val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE)
        as ActivityManager

    fun logMemoryState() {
        val memoryInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memoryInfo)

        val runtime = Runtime.getRuntime()
        val usedHeap = runtime.totalMemory() - runtime.freeMemory()
        val maxHeap = runtime.maxMemory()
        val heapUsagePercent = (usedHeap * 100 / maxHeap).toInt()

        // Логируем в Crashlytics для анализа OOM
        Firebase.crashlytics.apply {
            setCustomKey("heap_used_mb", usedHeap / 1024 / 1024)
            setCustomKey("heap_max_mb", maxHeap / 1024 / 1024)
            setCustomKey("heap_usage_percent", heapUsagePercent)
            setCustomKey("system_low_memory", memoryInfo.lowMemory)
            setCustomKey("available_ram_mb", memoryInfo.availMem / 1024 / 1024)
        }

        // Предупреждение при высоком использовании
        if (heapUsagePercent > 80) {
            Firebase.crashlytics.log("WARNING: High memory usage: $heapUsagePercent%")

            // Можно записать non-fatal exception для отслеживания
            Firebase.crashlytics.recordException(
                MemoryWarningException("Heap usage at $heapUsagePercent%")
            )
        }
    }

    class MemoryWarningException(message: String) : Exception(message)
}

// Мониторинг в критических точках:
class ProfileFragment : Fragment() {

    private val memoryMonitor by lazy { MemoryMonitor(requireContext()) }

    override fun onResume() {
        super.onResume()
        memoryMonitor.logMemoryState()  // Логируем при входе на экран
    }

    override fun onDestroyView() {
        super.onDestroyView()
        memoryMonitor.logMemoryState()  // Логируем при выходе
    }
}
```

### 9.2. OOM Analysis Pipeline

```
PRODUCTION OOM DEBUGGING WORKFLOW:

1. COLLECT DATA
   ┌─────────────────────────────────────────────────────┐
   │ • Crashlytics: stack trace, custom keys            │
   │ • Device info: RAM, Android version, manufacturer   │
   │ • App state: visible Activity, fragment stack       │
   │ • Memory state перед crash (если успели залогить) │
   └─────────────────────────────────────────────────────┘

2. REPRODUCE LOCALLY
   ┌─────────────────────────────────────────────────────┐
   │ • Ограничьте heap: adb shell setprop                │
   │ • Stress test: быстрые ротации экрана               │
   │ • Memory pressure: запустите другие тяжёлые apps   │
   │ • LeakCanary в debug build                          │
   └─────────────────────────────────────────────────────┘

3. CAPTURE HEAP DUMP
   ┌─────────────────────────────────────────────────────┐
   │ Debug build: Android Studio Memory Profiler        │
   │ Production: Debug.dumpHprofData() по триггеру      │
   │ → Загрузка .hprof на сервер для анализа            │
   └─────────────────────────────────────────────────────┘

4. ANALYZE
   ┌─────────────────────────────────────────────────────┐
   │ • MAT (Memory Analyzer Tool)                       │
   │ • Android Studio Profiler                          │
   │ • Shark CLI (от LeakCanary)                        │
   │ Ищем: Dominator Tree, Retained Size, Leak Suspects │
   └─────────────────────────────────────────────────────┘

5. FIX & VERIFY
   ┌─────────────────────────────────────────────────────┐
   │ • Исправляем leak                                  │
   │ • Добавляем regression test                        │
   │ • Мониторим production metrics после release       │
   └─────────────────────────────────────────────────────┘
```

### 9.3. Conditional Heap Dump в Production

```kotlin
// ОСТОРОЖНО: Heap dump в production замораживает приложение!
// Используйте только для critical debugging

class ProductionHeapDumper(private val context: Context) {

    private val prefs = context.getSharedPreferences("heap_dump", Context.MODE_PRIVATE)

    // Включается удалённо через Firebase Remote Config
    fun shouldDumpHeap(): Boolean {
        val remoteConfig = Firebase.remoteConfig
        return remoteConfig.getBoolean("enable_heap_dump") &&
               !prefs.getBoolean("heap_dumped_this_session", false)
    }

    fun dumpHeapIfNeeded(trigger: String) {
        if (!shouldDumpHeap()) return

        val runtime = Runtime.getRuntime()
        val usedHeap = runtime.totalMemory() - runtime.freeMemory()
        val maxHeap = runtime.maxMemory()
        val usagePercent = usedHeap * 100 / maxHeap

        // Dump только при критическом использовании памяти
        if (usagePercent < 85) return

        try {
            val fileName = "heap_${System.currentTimeMillis()}.hprof"
            val file = File(context.cacheDir, fileName)

            // Предупреждаем пользователя
            Toast.makeText(context, "Collecting debug data...", Toast.LENGTH_SHORT).show()

            // Dump heap (FREEZES APP!)
            Debug.dumpHprofData(file.absolutePath)

            // Помечаем что dump сделан
            prefs.edit().putBoolean("heap_dumped_this_session", true).apply()

            // Загружаем на сервер в фоне
            uploadHeapDump(file, trigger)

        } catch (e: Exception) {
            Firebase.crashlytics.recordException(e)
        }
    }

    private fun uploadHeapDump(file: File, trigger: String) {
        // Загрузка в Firebase Storage или свой backend
        // Важно: файл может быть 50-200 MB!
        // Загружайте только по WiFi

        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED)  // Только WiFi
            .build()

        val uploadWork = OneTimeWorkRequestBuilder<HeapUploadWorker>()
            .setInputData(workDataOf(
                "file_path" to file.absolutePath,
                "trigger" to trigger
            ))
            .setConstraints(constraints)
            .build()

        WorkManager.getInstance(context).enqueue(uploadWork)
    }
}
```

---

## 10. Compose Memory Management

### 10.1. Composition Lifecycle и память

```
COMPOSE MEMORY MODEL:

COMPOSITION TREE:
┌─────────────────────────────────────────────────────────────────┐
│                    Composition Owner                             │
│                    (ViewTreeOwner)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐                                        │
│  │   Slot Table         │ ← Хранит состояние всех Composables  │
│  │                      │                                       │
│  │  • Group slots       │ ← Структура UI дерева                │
│  │  • State slots       │ ← remember {}, mutableStateOf()      │
│  │  • Node slots        │ ← LayoutNode, Modifier               │
│  └─────────────────────┘                                        │
│                                                                 │
│  При RECOMPOSITION:                                             │
│  • Slot Table обновляется in-place                             │
│  • Старые slots переиспользуются                               │
│  • Новые slots добавляются/удаляются                           │
│                                                                 │
│  При DISPOSAL (выход из composition):                          │
│  • onDispose callbacks вызываются                               │
│  • Slots освобождаются                                          │
│  • remember {} объекты становятся доступны для GC              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

ПОТЕНЦИАЛЬНЫЕ LEAKS В COMPOSE:

1. remember {} с Activity Context
2. ViewModel хранит Composable lambda
3. LaunchedEffect без proper cancellation
4. derivedStateOf с тяжёлыми вычислениями
5. Callbacks переданные в non-Compose код
```

### 10.2. Паттерны безопасного Compose кода

```kotlin
// 1. ПРАВИЛЬНОЕ ИСПОЛЬЗОВАНИЕ remember {}

// ❌ LEAK: remember хранит Activity Context
@Composable
fun BadRememberExample() {
    val context = LocalContext.current  // Activity Context

    val analytics = remember {
        // Analytics singleton теперь держит Activity Context!
        Analytics(context)  // ❌ LEAK при configuration change
    }
}

// ✅ ИСПРАВЛЕНИЕ: Application Context
@Composable
fun GoodRememberExample() {
    val context = LocalContext.current.applicationContext  // App Context

    val analytics = remember {
        Analytics(context)  // ✅ Безопасно
    }
}

// ✅ ЕЩЁ ЛУЧШЕ: DI (Hilt)
@Composable
fun BestRememberExample(
    analytics: Analytics = hiltViewModel<AnalyticsViewModel>().analytics
) {
    // Analytics инжектирован с правильным scope
}


// 2. DISPOSABLEEFFECT ДЛЯ CLEANUP

// ❌ LEAK: Callback не очищен
@Composable
fun BadCallbackExample(viewModel: SomeViewModel) {
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        viewModel.setCallback { message ->
            // context (Activity) захвачен в lambda
            // lambda хранится в ViewModel
            // ViewModel переживает Activity → LEAK!
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        }
    }
}

// ✅ ИСПРАВЛЕНИЕ: DisposableEffect с cleanup
@Composable
fun GoodCallbackExample(viewModel: SomeViewModel) {
    val context = LocalContext.current

    DisposableEffect(viewModel) {
        val callback: (String) -> Unit = { message ->
            Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
        }
        viewModel.setCallback(callback)

        onDispose {
            viewModel.clearCallback()  // ✅ Очищаем!
        }
    }
}


// 3. COLLECTASSTATEWITHLIFECYCLE vs COLLECTASSTATE

// ❌ ПРОБЛЕМА: collectAsState продолжает collect даже когда app в фоне
@Composable
fun BadFlowCollection(viewModel: SomeViewModel) {
    val state by viewModel.heavyFlow.collectAsState(initial = State.Loading)
    // Flow продолжает emit даже когда Activity STOPPED
    // → лишние вычисления, потенциально лишние аллокации
}

// ✅ ИСПРАВЛЕНИЕ: collectAsStateWithLifecycle
@Composable
fun GoodFlowCollection(viewModel: SomeViewModel) {
    val state by viewModel.heavyFlow.collectAsStateWithLifecycle(
        initialValue = State.Loading,
        minActiveState = Lifecycle.State.STARTED  // Default
    )
    // Collection останавливается когда Activity STOPPED
}


// 4. DERIVEDSTATEOF ДЛЯ ТЯЖЁЛЫХ ВЫЧИСЛЕНИЙ

// ❌ ПЛОХО: пересчёт на каждую recomposition
@Composable
fun BadDerivedState(items: List<Item>) {
    val filteredItems = items.filter { it.isActive }  // ❌ Каждую recomposition
    val sortedItems = filteredItems.sortedBy { it.name }  // ❌ Каждую recomposition

    LazyColumn {
        items(sortedItems) { /* ... */ }
    }
}

// ✅ ХОРОШО: derivedStateOf кэширует результат
@Composable
fun GoodDerivedState(items: List<Item>) {
    val processedItems by remember(items) {
        derivedStateOf {
            items.filter { it.isActive }.sortedBy { it.name }
        }
    }
    // Пересчёт только когда items изменился

    LazyColumn {
        items(processedItems) { /* ... */ }
    }
}


// 5. SNAPSHOTFLOW ДЛЯ НАБЛЮДЕНИЯ ЗА STATE

@Composable
fun SnapshotFlowExample(viewModel: SearchViewModel) {
    var searchQuery by remember { mutableStateOf("") }

    // Дебаунс поиска через snapshotFlow
    LaunchedEffect(Unit) {
        snapshotFlow { searchQuery }
            .debounce(300)
            .distinctUntilChanged()
            .collect { query ->
                viewModel.search(query)
            }
    }
    // LaunchedEffect автоматически отменяется при disposal

    TextField(
        value = searchQuery,
        onValueChange = { searchQuery = it }
    )
}
```

### 10.3. Compose-специфичный LeakCanary

```kotlin
// LeakCanary 2.10+ автоматически отслеживает Compose

/*
COMPOSE OBJECTS, ОТСЛЕЖИВАЕМЫЕ LEAKCANARY:

1. ComposeView — когда removed из window
2. ViewTreeLifecycleOwner — когда destroyed
3. Composition — когда disposed
4. ViewModel в Compose — когда cleared

LEAK TRACE В COMPOSE выглядит так:

┌───────────────────────────────────────────────────────────┐
│ GC ROOT thread main                                        │
│ │                                                          │
│ ├── SomeViewModel                                          │
│ │   ↓ callback                                             │
│ ├── Function1 (lambda)                                     │
│ │   ↓ $context (captured)                                  │
│ ├── MainActivity                                           │
│ │   Leaking: YES (Activity.mDestroyed is true)            │
│ │                                                          │
│ ПРИЧИНА: ViewModel хранит lambda, захватившую Activity    │
│ РЕШЕНИЕ: DisposableEffect с onDispose { clearCallback() } │
└───────────────────────────────────────────────────────────┘
*/

// Кастомное отслеживание Compose компонентов:
@Composable
fun WatchedScreen(screenName: String) {
    // Следим за lifecycle этого Composable
    DisposableEffect(screenName) {
        val watchId = "$screenName-${System.identityHashCode(this)}"

        onDispose {
            // Сообщаем LeakCanary что этот "компонент" уничтожен
            // и должен быть собран GC
            AppWatcher.objectWatcher.expectWeaklyReachable(
                watchedObject = this,
                description = "Composable screen $screenName was disposed"
            )
        }
    }

    // UI content...
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|------------|
| "GC автоматически убирает все утечки" | GC не может собрать объект, достижимый от GC Root. Именно поэтому leaks возможны |
| "Memory leaks — проблема только legacy кода" | Compose имеет свои leak patterns (lambda capture, remember с долгоживущими refs) |
| "WeakReference решает все проблемы" | WeakReference — костыль. Лучше исправить архитектуру: lifecycle-aware компоненты |
| "SoftReference хорош для кэша на Android" | На Android SoftReference работает непредсказуемо. Используйте LruCache |
| "LeakCanary можно включить в production" | LeakCanary замораживает приложение при heap dump. Только для debug! |
| "ViewModel не может создать leak" | ViewModel, хранящий Context/View/Composable lambda, создаёт leak |
| "Compose не имеет проблем с leaks" | remember {} с Activity Context, ViewModel + Composable callback, неочищенный DisposableEffect — все создают leaks |
| "Если приложение не крашится, leaks нет" | Leak может не вызвать OOM сразу, но постепенно деградирует производительность |
| "GC.gc() принудительно освободит память" | System.gc() — только РЕКОМЕНДАЦИЯ. GC решает сам когда и что собирать |
| "finalize() — хороший способ cleanup" | finalize() deprecated, непредсказуем, замедляет GC. Используйте PhantomReference или Cleaner |
| "Bitmap.recycle() обязателен" | На Android 8.0+ pixel data в managed heap — GC сам освободит. recycle() — оптимизация, не необходимость |
| "Static переменные всегда утечка" | Static с Application Context безопасен. Проблема — static с Activity/View/Fragment Context |
| "onDestroy() всегда вызывается" | При process death onDestroy() может не вызваться! Не полагайтесь только на него для cleanup |
| "Kotlin автоматически предотвращает leaks" | Kotlin имеет те же проблемы что Java: inner class, captured lambdas, static refs. Просто синтаксис другой |
| "Room/Retrofit не создают leaks" | Если передать Activity Context в Singleton-scoped Repository — leak. Всегда Application Context для DI |

### Детальный разбор популярных мифов

```
МИФ 1: "Я вызову System.gc() и память освободится"

РЕАЛЬНОСТЬ:
┌─────────────────────────────────────────────────────────────────┐
│ System.gc() — это только HINT для JVM/ART                       │
│                                                                 │
│ ART может:                                                      │
│ • Проигнорировать полностью                                    │
│ • Отложить GC                                                  │
│ • Выполнить частичный GC                                       │
│ • Выполнить полный GC (редко)                                  │
│                                                                 │
│ ПОЧЕМУ: GC оптимизирован для throughput и latency.            │
│ Внешние вызовы нарушают его эвристики.                        │
│                                                                 │
│ КОГДА System.gc() может помочь:                                │
│ • Перед профилированием (для чистого baseline)                │
│ • В тестах (для детерминизма)                                 │
│ • LeakCanary использует для форсирования проверки             │
│                                                                 │
│ НИКОГДА не используйте System.gc() для "освобождения памяти" │
│ в production — это ухудшит производительность!                │
└─────────────────────────────────────────────────────────────────┘

МИФ 2: "Activity leak = OOM"

РЕАЛЬНОСТЬ:
┌─────────────────────────────────────────────────────────────────┐
│ Activity leak НЕ ВСЕГДА приводит к OOM.                        │
│                                                                 │
│ Что держит Activity:                                           │
│ • View hierarchy (может быть большой)                          │
│ • Bitmap'ы (если не recycled / не в Glide)                    │
│ • Adapter data                                                  │
│ • Fragment back stack                                           │
│                                                                 │
│ Размер leaked Activity: от 500KB до 50MB                       │
│                                                                 │
│ Простая Activity без картинок: ~1-2 MB                         │
│ Activity с большим RecyclerView: ~5-20 MB                      │
│ Activity с высокоразрешёнными Bitmap: ~20-100 MB               │
│                                                                 │
│ Heap на современном устройстве: 256-512 MB                     │
│ → Может пережить 5-10 Activity leaks до OOM                   │
│                                                                 │
│ НО: каждый leak замедляет GC, увеличивает latency,            │
│ потребляет батарею, делает app "тяжелее" для системы.        │
└─────────────────────────────────────────────────────────────────┘

МИФ 3: "В Kotlin нет inner class проблемы"

РЕАЛЬНОСТЬ:
┌─────────────────────────────────────────────────────────────────┐
│ Kotlin inner class ИДЕНТИЧЕН Java inner class:                 │
│                                                                 │
│ // Kotlin:                                                      │
│ class Outer {                                                   │
│     inner class Inner {  // ← имеет ссылку на Outer           │
│         fun foo() = this@Outer  // явный доступ               │
│     }                                                           │
│ }                                                               │
│                                                                 │
│ // Без inner — НЕТ ссылки на Outer:                            │
│ class Outer {                                                   │
│     class Nested {  // ← НЕТ ссылки на Outer                  │
│         // this@Outer — compilation error                      │
│     }                                                           │
│ }                                                               │
│                                                                 │
│ LAMBDA в Kotlin:                                                │
│ • Если lambda захватывает this — имеет ссылку                 │
│ • Если lambda не захватывает — singleton (no leak)            │
│                                                                 │
│ Пример захвата:                                                 │
│ button.setOnClickListener { updateUI() }                       │
│                     // ↑ updateUI() = this.updateUI()          │
│                     // lambda держит ссылку на Activity!       │
└─────────────────────────────────────────────────────────────────┘
```

---

## CS-фундамент

| CS-концепция | Применение в Memory Leaks |
|-------------|--------------------------|
| **Garbage Collection** | Reachability analysis от GC Roots определяет живые объекты. Leak = ложная достижимость |
| **Graph Traversal (BFS)** | Shark (LeakCanary) ищет кратчайший путь от GC Root до retained object через BFS |
| **Reference Types** | Strong → Soft → Weak → Phantom — иерархия "силы" ссылок, влияющая на GC |
| **Observer Pattern** | Listeners — главный источник leaks. Observer должен отписываться при уничтожении |
| **Object Pool** | Parcel.obtain()/recycle() — правильный подход (не leak). Но pool с Activity refs = leak |
| **Scope/Lifetime** | Nested lifetime: Activity < Application. Нарушение (длинный lifetime держит короткий) = leak |
| **Decorator Pattern** | WeakReference "оборачивает" сильную ссылку, меняя её семантику для GC |
| **Mark-and-Sweep** | Классический GC алгоритм: mark живые объекты, sweep мёртвые. ART использует улучшенную версию |
| **Generational GC** | Young/Old generation hypothesis: большинство объектов умирают молодыми. Minor GC для young, Major GC для old |
| **Compaction** | Перемещение живых объектов для устранения фрагментации. ART Concurrent Copying делает это параллельно |
| **Read/Write Barriers** | Механизм отслеживания изменений во время concurrent GC. Позволяет GC работать параллельно с приложением |
| **Reference Counting** | Альтернатива tracing GC (не используется в JVM/ART). Проблема: циклические ссылки |
| **RAII (Resource Acquisition Is Initialization)** | Паттерн из C++. В Kotlin: `use {}` для Closeable. Гарантирует cleanup |

### Глубокое погружение в алгоритмы GC

```
СРАВНЕНИЕ GC АЛГОРИТМОВ:

REFERENCE COUNTING (НЕ используется в JVM/ART):
┌─────────────────────────────────────────────────────────────────┐
│ Принцип: каждый объект хранит счётчик ссылок                   │
│ Удаление: когда счётчик = 0                                    │
│                                                                 │
│ ✅ Немедленное освобождение                                    │
│ ✅ Нет пауз                                                    │
│ ❌ Циклические ссылки не собираются (A → B → A)               │
│ ❌ Overhead на каждое присваивание                             │
│                                                                 │
│ Используется в: Python, Swift (ARC), Rust (Rc/Arc)            │
└─────────────────────────────────────────────────────────────────┘

TRACING GC (используется в JVM/ART):
┌─────────────────────────────────────────────────────────────────┐
│ Принцип: обход графа от GC Roots, недостижимые = мёртвые      │
│                                                                 │
│ MARK-AND-SWEEP:                                                │
│ 1. Mark: BFS/DFS от GC Roots, помечаем живые                  │
│ 2. Sweep: проходим весь heap, освобождаем непомеченные        │
│                                                                 │
│ MARK-COMPACT:                                                  │
│ 1. Mark: то же                                                 │
│ 2. Compact: перемещаем живые объекты, устраняем фрагментацию  │
│                                                                 │
│ COPYING:                                                        │
│ 1. Делим heap на from-space и to-space                        │
│ 2. Копируем живые объекты из from в to                        │
│ 3. Меняем местами spaces                                       │
│                                                                 │
│ ✅ Собирает циклические ссылки                                 │
│ ❌ Stop-the-world паузы (улучшено в concurrent GC)            │
└─────────────────────────────────────────────────────────────────┘

TRI-COLOR MARKING (основа concurrent GC):
┌─────────────────────────────────────────────────────────────────┐
│ Три цвета для объектов:                                        │
│ • WHITE: не посещён (кандидат на удаление)                    │
│ • GRAY: посещён, но children не обработаны                    │
│ • BLACK: посещён, все children обработаны (живой)             │
│                                                                 │
│ Алгоритм:                                                       │
│ 1. Все объекты WHITE                                           │
│ 2. GC Roots → GRAY                                             │
│ 3. Пока есть GRAY:                                             │
│    - Взять GRAY объект                                         │
│    - Его children → GRAY                                       │
│    - Сам объект → BLACK                                        │
│ 4. Все WHITE → мёртвые, можно освободить                      │
│                                                                 │
│ Concurrent: приложение может создавать новые ссылки           │
│ → Write barrier: при A.field = B, если A=BLACK, B=WHITE       │
│   → B помечается GRAY (иначе leak!)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

### Вопросы уровня "Основы"

**Q1:** Что такое memory leak в контексте Android?

<details>
<summary>Ответ</summary>

Memory leak — это ситуация, когда объект удерживается в памяти (достижим от GC Root), хотя он больше не нужен приложению. Типичный пример: Activity уничтожена (onDestroy вызван), но GC не может её собрать, потому что на неё существует цепочка сильных ссылок от GC Root (например, static field → listener → Activity).

</details>

**Q2:** Почему `inner class` в Kotlin создаёт risk memory leak?

<details>
<summary>Ответ</summary>

`inner class` (в отличие от обычного `class` без модификатора `inner`) имеет неявную ссылку на экземпляр внешнего класса. Если внешний класс — Activity, а inner class живёт дольше (например, запущен в фоновом потоке), он удерживает Activity от сборки GC. Решение: использовать обычный `class` (без `inner`) + `WeakReference` для доступа к Activity.

</details>

**Q3:** Какой Context использовать в Singleton?

<details>
<summary>Ответ</summary>

Только `Application Context`. Singleton живёт весь процесс. Если передать Activity Context, Activity не сможет быть собрана GC, пока Singleton существует (весь процесс). Application Context живёт столько же, сколько процесс, поэтому безопасен. Получение: `context.applicationContext` или через Hilt `@ApplicationContext`.

</details>

**Q4:** Почему Handler.postDelayed() может создать leak?

<details>
<summary>Ответ</summary>

`postDelayed()` помещает Message в MessageQueue. Message держит ссылку на Runnable (callback). Если Runnable — anonymous inner class или lambda, захватившая Activity, он держит ссылку на Activity. Если Activity уничтожается до истечения delay, Message всё ещё в очереди и держит Activity. Решение: `handler.removeCallbacksAndMessages(null)` в `onDestroy()` или использовать `lifecycleScope.launch { delay() }`.

</details>

### Вопросы уровня "Продвинутое"

**Q5:** Как LeakCanary определяет, что объект — retained (потенциальный leak)?

<details>
<summary>Ответ</summary>

LeakCanary использует `ObjectWatcher`, который создаёт `WeakReference` с `ReferenceQueue` для каждого watched объекта (destroyed Activity/Fragment/ViewModel). После 5 секунд LeakCanary запускает GC и проверяет `ReferenceQueue`: если WeakReference попала в queue — объект собран (OK). Если НЕ попала — объект retained (потенциальный leak). Когда количество retained объектов достигает threshold (5 при видимом app, 1 в фоне), LeakCanary делает heap dump и анализирует его через Shark.

</details>

**Q6:** В чём разница между WeakReference и SoftReference и когда использовать каждый?

<details>
<summary>Ответ</summary>

`WeakReference` собирается при **первом** GC цикле, как только нет strong-ссылок. Подходит для preventing leaks (callbacks, listeners). `SoftReference` собирается только при **нехватке памяти** (перед OOM). Подходит для кэшей. Однако на Android `SoftReference` работает непредсказуемо из-за динамического heap — рекомендуется использовать `LruCache` вместо SoftReference для кэширования.

</details>

**Q7:** Объясните разницу между GC Root types в Android.

<details>
<summary>Ответ</summary>

Основные GC Roots в Android/JVM:

1. **Local variables** на стеке активных потоков — локальные переменные в активных методах
2. **Static fields** — `companion object`, `object`, статические поля в Java. Живут весь процесс.
3. **Active threads** — объекты Thread, которые еще не завершились
4. **JNI references** — ссылки, созданные в нативном коде через JNI
5. **System class loader** — классы, загруженные системным загрузчиком

Наиболее частые причины Android leaks: static fields (Singleton с Activity Context), active threads (AsyncTask, Thread), JNI (некорректный нативный код).

</details>

**Q8:** Как работает Concurrent Copying GC в ART?

<details>
<summary>Ответ</summary>

Concurrent Copying GC (Android 8+) работает в 5 фаз:

1. **Initial Mark** (stop-the-world ~1ms): помечаем GC Roots, короткая пауза
2. **Concurrent Mark** (параллельно): GC thread обходит граф объектов, приложение работает, read/write barriers отслеживают изменения
3. **Concurrent Copy** (параллельно): живые объекты копируются в новое место (compacting), forwarding pointers обновляют ссылки
4. **Final Mark** (stop-the-world ~1ms): обрабатываем изменения с фаз 2-3, финализируем
5. **Sweep**: освобождаем старое пространство

Преимущества: минимальные паузы (<2ms), нет фрагментации (compacting), параллельная работа с приложением.

</details>

### Вопросы уровня "Экспертное"

**Q9:** Опишите полный pipeline LeakCanary от уничтожения Activity до отображения leak trace.

<details>
<summary>Ответ</summary>

1. **Watch:** `ActivityLifecycleCallbacks.onActivityDestroyed()` вызывает `AppWatcher.objectWatcher.expectWeaklyReachable(activity)`. ObjectWatcher создаёт `KeyedWeakReference(activity, UUID, ReferenceQueue)`.

2. **Detect:** Через 5 секунд ObjectWatcher: (a) проверяет ReferenceQueue — удаляет из map все references попавшие в queue; (b) вызывает `Runtime.gc()` для форсирования GC; (c) снова проверяет queue; (d) оставшиеся в map = retained objects.

3. **Threshold:** Если retained count >= 5 (видимое) или >= 1 (фон) — переход к dump.

4. **Dump:** `Debug.dumpHprofData(filePath)` создаёт .hprof файл. App замораживается на время dump.

5. **Analyze:** Shark парсит .hprof, находит retained objects по UUID, для каждого выполняет BFS от GC Roots, находит кратчайшую цепочку сильных ссылок (leak trace), определяет подозреваемых (leaking: YES/NO/MAYBE).

6. **Report:** Вычисляет signature (SHA-1 от suspected references), группирует leaks, показывает notification + Logcat + UI.

</details>

**Q10:** Как предотвратить memory leak в Compose при работе с callbacks в ViewModel?

<details>
<summary>Ответ</summary>

Проблема: если ViewModel хранит lambda (callback), которая захватила Composable context (например, `LocalContext.current`), ViewModel переживёт Activity/Fragment и будет держать leaked контекст.

Решения:
1. **DisposableEffect с onDispose**: установить callback в DisposableEffect, очистить в onDispose
2. **SharedFlow/Channel вместо callbacks**: ViewModel emit events, Composable collect через LaunchedEffect (автоматически отменяется)
3. **Не захватывать Activity Context**: использовать `applicationContext` если нужен Context в callback
4. **rememberUpdatedState**: для callbacks, которые должны видеть актуальное состояние без пересоздания lambda

```kotlin
// Правильный паттерн:
DisposableEffect(viewModel) {
    val callback = { viewModel.doSomething() }  // Не захватываем Activity
    viewModel.setCallback(callback)
    onDispose { viewModel.clearCallback() }
}
```

</details>

**Q11:** Объясните, как анализировать heap dump с помощью MAT (Memory Analyzer Tool).

<details>
<summary>Ответ</summary>

Workflow анализа heap dump в MAT:

1. **Получение dump**: Android Studio Profiler → Dump Java Heap → Export as HPROF
2. **Конвертация**: `hprof-conv android.hprof mat.hprof` (Android формат → standard Java HPROF)
3. **Открытие в MAT**: File → Open Heap Dump

**Ключевые представления:**
- **Histogram**: все классы отсортированы по количеству instances и retained size. Ищем аномалии (много Activity instances).
- **Dominator Tree**: кто "владеет" памятью. Показывает retained size для каждого объекта.
- **Leak Suspects Report**: автоматический анализ подозрительных объектов.
- **Path to GC Roots**: для конкретного объекта показывает цепочку ссылок до GC Root (аналог LeakCanary leak trace).

**Типичный workflow:**
1. Открыть Histogram, отфильтровать по package приложения
2. Найти Activity/Fragment с count > 1 (должно быть 0-1)
3. Right-click → Path to GC Roots → exclude weak references
4. Изучить цепочку, найти "виновника"

</details>

**Q12:** Как организовать мониторинг memory leaks в production без LeakCanary?

<details>
<summary>Ответ</summary>

Production-ready подход:

1. **Metrics Collection**: логировать heap usage в key points (Activity onCreate/onDestroy)
   ```kotlin
   Firebase.crashlytics.setCustomKey("heap_used_mb", usedHeap / 1024 / 1024)
   ```

2. **OOM Breadcrumbs**: перед potential OOM записывать состояние
   ```kotlin
   if (heapUsagePercent > 80) {
       Firebase.crashlytics.log("High memory: $heapUsagePercent%")
   }
   ```

3. **Conditional Heap Dump**: по Remote Config флагу для отдельных пользователей
   - Только по WiFi (файл 50-200 MB)
   - Предупреждение пользователю (app freezes)
   - Upload в Firebase Storage / S3

4. **Memory Pressure Testing**: CI с ограниченным heap, stress tests

5. **Regression Detection**: track memory metrics между releases в Firebase Performance / custom dashboard

6. **Alerting**: alert если среднее heap usage растёт между версиями

</details>

---

## Связанные темы

### Обязательные связи
- **[[android-activity-lifecycle]]** — onDestroy() как точка cleanup; понимание когда объекты должны быть released
- **[[android-handler-looper]]** — Handler/MessageQueue — один из топ-источников leaks; removeCallbacksAndMessages
- **[[android-process-memory]]** — GC, heap, LMK — фундамент понимания memory management

### Углубление
- **[[android-state-management]]** — Правильное управление состоянием предотвращает leaks: ViewModel + SavedStateHandle
- **[[android-viewmodel-internals]]** — ViewModel не хранит Context; ViewModelStore lifecycle
- **[[android-bundle-parcelable]]** — Bitmap в Bundle = потенциальный OOM; размер savedInstanceState

### Смежные темы
- **[[android-compose]]** — DisposableEffect, remember, LaunchedEffect — Compose patterns для prevention
- **[[android-context-internals]]** — Application vs Activity Context: правила использования
- **[[android-performance-profiling]]** — Memory Profiler, heap dump analysis, allocation tracking

---

## Источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [How LeakCanary Works — Square](https://square.github.io/leakcanary/fundamentals-how-leakcanary-works/) | Docs | Официальная документация внутреннего устройства LeakCanary |
| [LeakCanary GitHub](https://github.com/square/leakcanary) | Code | Исходный код LeakCanary 2.14+ |
| [The LeakCanary Method — Block Engineering](https://engineering.block.xyz/blog/the-leakcanary-method) | Article | Философия и подход к обнаружению leaks |
| [Top 7 Android Memory Leaks 2025 — Artem Asoyan](https://artemasoyan.medium.com/top-7-android-memory-leaks-and-how-to-avoid-them-in-2025-b77e15a7b62e) | Article | Актуальный обзор паттернов утечек |
| [Memory Leaks in Compose — ProAndroidDev](https://proandroiddev.com/memory-leaks-in-jetpack-compose-a-technical-deep-dive-3afb7b78a82e) | Article | Compose-специфичные leak patterns |
| [Handler Inner Class Memory Leak — Android Design Patterns](https://www.androiddesignpatterns.com/2013/01/inner-class-handler-memory-leak.html) | Article | Классический разбор Handler leak pattern |
| [Understanding References in Java/Android — Enrique López-Mañas](https://medium.com/google-developer-experts/finally-understanding-how-references-work-in-android-and-java-26a0d9c92f83) | Article | Reference types deep dive с Android примерами |
| [State Lifespans in Compose — Android Developers](https://developer.android.com/develop/ui/compose/state-lifespans) | Docs | Официальный гайд по lifecycle state в Compose |
| [ViewModel Overview — Android Developers](https://developer.android.com/topic/libraries/architecture/viewmodel) | Docs | Правила использования ViewModel (no Context) |
| [Weak, Soft, Phantom References — DZone](https://dzone.com/articles/weak-soft-and-phantom-references-in-java-and-why-they-matter) | Article | Детальное сравнение Java reference types |

---

## Источники и дальнейшее чтение

- Goetz (2006). *Java Concurrency in Practice*. — фундаментальное понимание Java Memory Model, happens-before, visibility и thread safety, без которого невозможно понять, почему Handler leaks и threading-связанные утечки возникают на уровне JVM.
- Vasavada (2019). *Android Internals*. — глубокое погружение в процессную модель Android, GC в ART, heap management и Low Memory Killer, что даёт системный контекст для понимания, почему memory leaks критичны на мобильных устройствах.
- Moskala (2022). *Kotlin Coroutines Deep Dive*. — детальный разбор coroutine scopes, structured concurrency и правильной отмены, что напрямую связано с предотвращением утечек через GlobalScope и неправильное использование корутин.

---

*Последнее обновление: 2026-01-27*
*Эталон стиля: [[android-handler-looper]] (Gold Standard)*
