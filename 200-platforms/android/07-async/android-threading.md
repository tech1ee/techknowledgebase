---
title: "Threading в Android: Main Thread и Coroutines"
created: 2025-12-17
modified: 2026-02-13
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/threading
  - topic/kotlin
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-handler-looper]]"
  - "[[android-coroutines-mistakes]]"
  - "[[kotlin-coroutines]]"
  - "[[kotlin-flow]]"
  - "[[os-processes-threads]]"
  - "[[os-scheduling]]"
cs-foundations: [thread-safety, main-thread-rule, thread-pool, dispatcher-pattern]
prerequisites:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
reading_time: 40
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Threading в Android: Main Thread и Coroutines

Android имеет строгую модель потоков: UI можно модифицировать только из Main Thread, а тяжёлые операции нельзя выполнять на Main Thread. Нарушение этих правил ведёт к ANR (Application Not Responding) или crashes. Kotlin Coroutines — современный способ управления асинхронностью, интегрированный с lifecycle Android-компонентов.

> **Prerequisites:**
> - [[os-processes-threads]] — потоки на уровне ОС, контекст переключения
> - [[os-synchronization]] — mutex, race conditions, deadlock
> - [[android-activity-lifecycle]] — lifecycle компонентов и scopes

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Main Thread** | Главный поток приложения, он же UI Thread |
| **ANR** | Application Not Responding — UI заблокирован >5 секунд |
| **Looper** | Цикл обработки сообщений в потоке |
| **Handler** | Отправляет задачи в очередь Looper |
| **Dispatcher** | Определяет, на каком потоке выполняется coroutine |
| **lifecycleScope** | CoroutineScope, привязанный к lifecycle компонента |
| **viewModelScope** | CoroutineScope, привязанный к ViewModel |
| **Structured Concurrency** | Иерархия coroutines с автоматической отменой |

---

## Почему UI работает в одном потоке?

### Проблема: что если бы UI был многопоточным

```kotlin
// ❌ Гипотетический многопоточный UI
class HypotheticalMultiThreadedUI {

    fun updateFromThread1() {
        textView.text = "Hello"          // Thread 1
        textView.color = Color.RED       // Thread 1
    }

    fun updateFromThread2() {
        textView.text = "World"          // Thread 2 — в этот момент?
        textView.color = Color.BLUE      // Thread 2
    }
}

// Что увидит пользователь?
// Вариант 1: "Hello" + RED
// Вариант 2: "World" + BLUE
// Вариант 3: "Hello" + BLUE (inconsistent state!)
// Вариант 4: "World" + RED (inconsistent state!)
// Вариант 5: Crash из-за race condition внутри TextView
```

### Race conditions в UI: конкретные проблемы

**1. Измерение и отрисовка (Measure → Layout → Draw):**
```
Thread 1: measure()   →   layout()   →   draw()
Thread 2:     measure()   →   layout()   →   draw()
                  ↑
            View изменилась между measure и layout
            Размер посчитан неправильно → visual glitch
```

**2. Иерархия View:**
```kotlin
// Thread 1
parentView.addChild(childA)

// Thread 2 одновременно
parentView.removeChild(childB)

// Итог: ArrayList внутри ViewGroup повреждён
// ConcurrentModificationException или некорректный индекс
```

**3. Состояние анимации:**
```kotlin
// Thread 1: animation.start()
// Thread 2: animation.cancel()
// Thread 1: animation.onUpdate() — но она уже отменена!
```

### Какие альтернативы существуют

**1. Thread-safe UI framework (полная синхронизация):**
```kotlin
class ThreadSafeTextView {
    private val lock = ReentrantLock()

    fun setText(text: String) {
        lock.withLock {
            this.text = text
            invalidate()
        }
    }
}
```
**Проблемы:**
- Каждая операция с UI требует захвата lock
- При 60 FPS это тысячи lock/unlock в секунду
- Deadlocks при сложных иерархиях View
- Серьёзное падение производительности

**2. Полностью immutable UI (как React Native пытался):**
```kotlin
// Каждое изменение создаёт новый UI tree
fun render(state: AppState): ViewTree {
    return ViewTree(
        TextView(text = state.title),
        Button(onClick = { /* ... */ })
    )
}
```
**Проблемы:**
- Overhead на создание/сравнение деревьев
- Сложность с анимациями и переходами
- Потеря фокуса, scroll position при пересоздании

**3. Copy-on-write (каждый поток видит свою копию):**
**Проблемы:**
- Огромное потребление памяти
- Синхронизация копий между потоками
- Какая копия "правильная"?

### Почему single-threaded — лучший выбор для UI

| Критерий | Multi-threaded | Single-threaded |
|----------|----------------|-----------------|
| **Производительность** | Locks на каждую операцию | Без locks, максимальная скорость |
| **Предсказуемость** | Race conditions | Детерминированный порядок |
| **Сложность кода** | Синхронизация везде | Простой последовательный код |
| **Отладка** | Heisenbugs, сложно воспроизвести | Баги воспроизводимы |
| **Анимации** | Сложная синхронизация | Естественный последовательный flow |

### Как это работает на практике

```
┌─────────────────────────────────────────────────────────────────┐
│                    SINGLE-THREADED UI MODEL                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Background Thread         Main Thread                          │
│  ┌─────────────────┐      ┌─────────────────────────────────┐  │
│  │ Сетевой запрос  │      │         Message Queue           │  │
│  │ Парсинг JSON    │      │  ┌───┐ ┌───┐ ┌───┐ ┌───┐      │  │
│  │ Работа с БД     │─────▶│  │ 1 │ │ 2 │ │ 3 │ │ 4 │      │  │
│  │                 │ post │  └───┘ └───┘ └───┘ └───┘      │  │
│  └─────────────────┘      │         │                       │  │
│                           │         ▼                       │  │
│                           │  ┌─────────────────┐            │  │
│                           │  │ Обработка по    │            │  │
│                           │  │ одному сообщению│            │  │
│                           │  │ последовательно │            │  │
│                           │  └─────────────────┘            │  │
│                           └─────────────────────────────────┘  │
│                                                                 │
│  Нет race conditions!                                           │
│  Сообщения обрабатываются строго по порядку                     │
│  UI всегда в консистентном состоянии                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Исторический контекст

Single-threaded UI model — это не изобретение Android. Эту модель используют:
- **Windows** — UI thread + message pump (с 1985 года)
- **macOS/iOS** — Main thread + RunLoop
- **Swing (Java)** — Event Dispatch Thread
- **Qt** — GUI thread + event loop
- **Electron/Chrome** — Renderer process main thread

Все пришли к одному выводу: **проще и надёжнее выделить один поток для UI**.

### Недостатки single-threaded UI

1. **Легко заблокировать UI:**
   - Любая длительная операция на Main Thread → приложение "зависает"
   - Разработчик должен знать, какие операции "тяжёлые"

2. **Дополнительная сложность для async:**
   - Нужны механизмы для переключения между потоками
   - Handler, post, runOnUiThread, Coroutines — всё это overhead

3. **Не использует все ядра CPU для UI:**
   - Даже на 8-ядерном процессоре UI рендерится в одном потоке
   - (Частично решается RenderThread для отрисовки)

### Compose и threading

Jetpack Compose сохраняет single-threaded модель, но оптимизирует её:

```kotlin
@Composable
fun MyScreen(viewModel: MyViewModel) {
    // Composition происходит на Main Thread
    // Но recomposition умная — обновляется только то, что изменилось

    val state by viewModel.state.collectAsStateWithLifecycle()

    // Compose использует snapshot system для отслеживания изменений
    // Это не multi-threading, но эффективная работа в одном потоке
    Text(text = state.title)
    Button(onClick = { viewModel.onAction() }) {
        Text("Click")
    }
}
```

---

## Main Thread: сердце UI

### Что выполняется на Main Thread

```
┌─────────────────────────────────────────────────────────────────┐
│                         MAIN THREAD                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    MESSAGE QUEUE                          │   │
│  │                                                           │   │
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐              │   │
│  │  │Touch│ │Draw │ │Life-│ │Anim-│ │Your │              │   │
│  │  │Event│ │Frame│ │cycle│ │ation│ │Code │              │   │
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘              │   │
│  │                                                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│                    ┌─────────────┐                             │
│                    │   LOOPER    │                             │
│                    │ (бесконечный│                             │
│                    │   цикл)     │                             │
│                    └─────────────┘                             │
│                                                                 │
│  Один кадр = 16ms (60 FPS)                                     │
│  Если обработка занимает >16ms → пропуск кадра (jank)          │
│  Если Main Thread заблокирован >5s → ANR диалог                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Правило 16ms

Для плавной анимации нужно 60 кадров в секунду. Это даёт 16ms на обработку каждого кадра:

```kotlin
// ПЛОХО: блокируем Main Thread
button.setOnClickListener {
    val data = fetchDataFromNetwork()  // 2 секунды!
    // UI завис на 2 секунды
    textView.text = data
}

// ЕЩЁ ХУЖЕ: парсинг большого JSON
button.setOnClickListener {
    val json = File("large.json").readText()
    val items = parseJson(json)  // 500ms парсинга
    // Пропуск ~30 кадров!
    adapter.submitList(items)
}
```

### ANR: когда приложение не отвечает

```
ANR происходит когда Main Thread заблокирован:
- > 5 секунд для foreground Activity
- > 10 секунд для BroadcastReceiver

Типичные причины:
- Сетевой запрос на Main Thread
- Чтение большого файла
- Тяжёлые вычисления
- Deadlock
- Долгий запрос к базе данных
```

---

## Модификация UI только из Main Thread

### Почему это правило

View system не thread-safe. Если два потока одновременно модифицируют View, результат непредсказуем — от некорректного отображения до crash.

```kotlin
// CRASH: android.view.ViewRootImpl$CalledFromWrongThreadException
// "Only the original thread that created a view hierarchy can touch its views"
thread {
    val result = fetchData()
    textView.text = result  // CRASH!
}

// ПРАВИЛЬНО: переключиться на Main Thread
thread {
    val result = fetchData()
    runOnUiThread {
        textView.text = result  // OK
    }
}
```

### Способы переключения на Main Thread

```kotlin
// 1. runOnUiThread (в Activity)
runOnUiThread {
    textView.text = "Updated"
}

// 2. View.post
textView.post {
    textView.text = "Updated"
}

// 3. Handler
val handler = Handler(Looper.getMainLooper())
handler.post {
    textView.text = "Updated"
}

// 4. Coroutines (рекомендуется)
lifecycleScope.launch {
    val result = withContext(Dispatchers.IO) {
        fetchData()
    }
    textView.text = result  // Автоматически на Main Thread
}
```

---

## Kotlin Coroutines в Android

### Dispatchers

```kotlin
// Dispatchers.Main — Main Thread
// Для UI операций, обновления View
lifecycleScope.launch(Dispatchers.Main) {
    textView.text = "Hello"  // UI
}

// Dispatchers.IO — пул потоков для I/O
// Для сети, файлов, базы данных
lifecycleScope.launch(Dispatchers.IO) {
    val data = api.fetchData()  // Сеть
    val file = File("data.txt").readText()  // Файл
    database.insertAll(items)  // БД
}

// Dispatchers.Default — пул потоков для CPU
// Для тяжёлых вычислений
lifecycleScope.launch(Dispatchers.Default) {
    val sorted = hugeList.sortedBy { it.name }  // CPU работа
    val parsed = parseJson(largeJson)  // Парсинг
}
```

### lifecycleScope: безопасные coroutines

`lifecycleScope` привязан к lifecycle Activity/Fragment. Coroutines автоматически отменяются при destroy:

```kotlin
class MyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Эта coroutine отменится при onDestroy
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.loadData()
            }
            binding.textView.text = data
        }
    }
}
```

### viewModelScope: coroutines в ViewModel

```kotlin
class UserViewModel(private val repository: UserRepository) : ViewModel() {

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun loadUsers() {
        // viewModelScope отменяется при onCleared()
        viewModelScope.launch {
            val result = repository.getUsers()  // suspend функция
            _users.value = result
        }
    }
}
```

### repeatOnLifecycle: Flow и lifecycle

Flow нужно собирать с учётом lifecycle — иначе будут утечки:

```kotlin
class MyFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ПРАВИЛЬНО: отменяется когда view destroyed
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Этот блок выполняется только когда lifecycle >= STARTED
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

**Почему repeatOnLifecycle:**
- `collect` — suspend функция, которая никогда не завершается для hot flow
- Без repeatOnLifecycle collection продолжается в onStop/onDestroy
- Это тратит ресурсы и может вызвать crashes (обращение к destroyed view)

Подробнее о Flow — в [[kotlin-flow]].

---

## Structured Concurrency

### Иерархия отмены

```kotlin
// Parent coroutine
viewModelScope.launch {
    // Child 1
    launch {
        loadUsers()
    }

    // Child 2
    launch {
        loadPosts()
    }
}

// Если viewModelScope отменяется:
// - Parent отменяется
// - Все children автоматически отменяются
// - Не нужно вручную отслеживать и отменять
```

### Обработка исключений

```kotlin
viewModelScope.launch {
    try {
        val users = repository.getUsers()
        _users.value = users
    } catch (e: Exception) {
        // Обработать ошибку
        _error.value = e.message
    }
}

// Или с помощью supervisorScope для независимых задач
viewModelScope.launch {
    supervisorScope {
        // Ошибка в одном child не отменяет другие
        launch { loadUsers() }   // Может упасть
        launch { loadPosts() }   // Продолжит работу
    }
}
```

Подробнее — в [[kotlin-coroutines]].

---

## Практические паттерны

### Загрузка данных в ViewModel

```kotlin
class ProductViewModel(
    private val repository: ProductRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    init {
        loadProducts()
    }

    fun loadProducts() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val products = repository.getProducts()
                _uiState.value = UiState.Success(products)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }

    fun refresh() {
        loadProducts()
    }
}

sealed class UiState {
    object Loading : UiState()
    data class Success(val products: List<Product>) : UiState()
    data class Error(val message: String) : UiState()
}
```

### Параллельные запросы

```kotlin
suspend fun loadDashboard(): Dashboard {
    return coroutineScope {
        // Запускаем параллельно
        val userDeferred = async { repository.getUser() }
        val postsDeferred = async { repository.getPosts() }
        val notificationsDeferred = async { repository.getNotifications() }

        // Ждём все результаты
        Dashboard(
            user = userDeferred.await(),
            posts = postsDeferred.await(),
            notifications = notificationsDeferred.await()
        )
    }
}
```

### Debounce для поиска

```kotlin
class SearchViewModel : ViewModel() {

    private val searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<SearchResult>> = searchQuery
        .debounce(300)  // Ждать 300ms после последнего ввода
        .filter { it.length >= 2 }  // Минимум 2 символа
        .distinctUntilChanged()  // Игнорировать дубликаты
        .flatMapLatest { query ->
            // Отменить предыдущий поиск, начать новый
            flow {
                emit(repository.search(query))
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

### Отмена при навигации

```kotlin
class DetailFragment : Fragment() {

    private var loadJob: Job? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        loadJob = viewLifecycleOwner.lifecycleScope.launch {
            val detail = repository.loadDetail(itemId)
            // Если Fragment уже destroyed, эта строка не выполнится
            binding.textView.text = detail.description
        }
    }

    override fun onDestroyView() {
        // Явная отмена (необязательно с lifecycleScope, но может быть полезно)
        loadJob?.cancel()
        super.onDestroyView()
    }
}
```

---

## Тестирование coroutines

```kotlin
@Test
fun `loadUsers updates state with success`() = runTest {
    // Arrange
    val testUsers = listOf(User("1", "Alice"))
    coEvery { repository.getUsers() } returns testUsers

    // Act
    val viewModel = UserViewModel(repository)

    // Assert
    assertEquals(UiState.Success(testUsers), viewModel.uiState.value)
}

@Test
fun `loadUsers handles error`() = runTest {
    // Arrange
    coEvery { repository.getUsers() } throws Exception("Network error")

    // Act
    val viewModel = UserViewModel(repository)

    // Assert
    assertTrue(viewModel.uiState.value is UiState.Error)
}
```

---

## Типичные ошибки threading

### CalledFromWrongThreadException

Самая частая ошибка при попытке обновить UI из background потока:

```kotlin
// CRASH!
thread {
    val result = api.fetchData()
    textView.text = result
    // android.view.ViewRootImpl$CalledFromWrongThreadException:
    // Only the original thread that created a view hierarchy can touch its views
}

// ПРАВИЛЬНО
thread {
    val result = api.fetchData()
    runOnUiThread {
        textView.text = result  // OK — на Main Thread
    }
}
```

**Почему происходит:**
- View system не thread-safe
- Android проверяет, что UI обновляется только из Main Thread
- Проверка в `ViewRootImpl.checkThread()`

### ANR (Application Not Responding)

ANR диалог появляется, когда Main Thread заблокирован слишком долго:

```kotlin
// ПЛОХО: ANR через 5+ секунд
button.setOnClickListener {
    val data = api.fetchData()  // 10 секунд блокировки Main Thread!
    textView.text = data
    // Система покажет диалог "App is not responding"
}
```

**Временные лимиты для ANR:**
- **5 секунд** — для input events (touch, key press)
- **5 секунд** — для BroadcastReceiver в foreground
- **10 секунд** — для BroadcastReceiver в background
- **20 секунд** — для Service.startForeground()

**Типичные причины ANR:**
1. Синхронный сетевой запрос на Main Thread
2. Чтение большого файла (например, JSON 50MB)
3. Тяжелые вычисления (сортировка 100k элементов)
4. Запрос к базе данных без suspend/async
5. Deadlock между потоками

**Как избежать:**
```kotlin
// ПРАВИЛЬНО: асинхронная работа
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        api.fetchData()  // Выполняется в background
    }
    textView.text = data  // Обновление UI на Main Thread
}
```

### Memory leaks через Handler/AsyncTask

**Problem: Handler держит ссылку на Activity:**

```kotlin
class MyActivity : AppCompatActivity() {

    // УТЕЧКА ПАМЯТИ!
    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            // Activity может быть уже destroyed
            // Но Handler держит на неё ссылку ещё 10 секунд
            textView.text = "Updated"
        }, 10_000)

        // Если пользователь повернул экран или нажал Back,
        // Activity destroyed, но Handler + Activity остаются в памяти
    }
}
```

**Почему происходит утечка:**
1. Handler создаётся как inner class (неявно держит `this`)
2. Handler постит задачу в Message Queue
3. Message Queue держит ссылку на Handler
4. Handler держит ссылку на Activity
5. Activity не может быть собрана сборщиком мусора

**Правильное решение:**

```kotlin
class MyActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        handler.postDelayed({
            textView.text = "Updated"
        }, 10_000)
    }

    override fun onDestroy() {
        // Отменить все pending сообщения
        handler.removeCallbacksAndMessages(null)
        super.onDestroy()
    }
}
```

**Ещё лучше — использовать Coroutines:**

```kotlin
class MyActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Автоматически отменяется при onDestroy
        lifecycleScope.launch {
            delay(10_000)
            textView.text = "Updated"
        }
    }

    // Не нужен onDestroy — утечки нет!
}
```

**AsyncTask — устарел и опасен:**

```kotlin
// DEPRECATED и УТЕЧКА!
class MyAsyncTask(private val textView: TextView) : AsyncTask<Void, Void, String>() {

    override fun doInBackground(vararg params: Void?): String {
        Thread.sleep(10_000)
        return "Data"
    }

    override fun onPostExecute(result: String) {
        // TextView может быть из destroyed Activity
        textView.text = result  // Crash или утечка
    }
}

// Проблемы:
// 1. AsyncTask держит ссылку на View/Activity
// 2. Нет автоматической отмены при destroy
// 3. API deprecated с Android 11
```

### Race conditions в shared state

**Проблема: два потока модифицируют общее состояние:**

```kotlin
class Counter {
    var count = 0  // НЕ thread-safe!

    fun increment() {
        count++  // Три операции: read, increment, write
    }
}

// Thread 1 и Thread 2 одновременно:
thread {
    repeat(1000) { counter.increment() }
}
thread {
    repeat(1000) { counter.increment() }
}

// Ожидаем: 2000
// Получаем: 1537 (или другое случайное число)
// Причина: race condition в count++
```

**Что происходит:**

```
Thread 1                    Thread 2                    count
─────────────────────────────────────────────────────────────
read count (0)
                            read count (0)
increment → 1
                            increment → 1
write count = 1
                            write count = 1             1 (!)

Должно быть 2, но получилось 1
```

**Решение 1: Синхронизация (для shared mutable state):**

```kotlin
class Counter {
    private var count = 0
    private val lock = ReentrantLock()

    fun increment() {
        lock.withLock {
            count++  // Теперь атомарно
        }
    }

    fun get(): Int = lock.withLock { count }
}
```

**Решение 2: Atomic types:**

```kotlin
class Counter {
    private val count = AtomicInteger(0)

    fun increment() {
        count.incrementAndGet()  // Атомарная операция
    }

    fun get(): Int = count.get()
}
```

**Решение 3: Single Thread (рекомендуется для Android):**

```kotlin
class CounterViewModel : ViewModel() {

    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    // Все изменения на Main Thread через viewModelScope
    fun increment() {
        viewModelScope.launch {
            _count.value++  // Safe — один поток
        }
    }
}
```

**Почему single-threaded лучше:**
- Нет locks, нет race conditions
- Проще тестировать и отлаживать
- StateFlow/LiveData гарантируют UI updates на Main Thread
- Structured Concurrency автоматически управляет lifecycle

---

## Распространённые ошибки

### 1. GlobalScope вместо lifecycleScope

```kotlin
// ПЛОХО: утечка, не отменяется при destroy
GlobalScope.launch {
    val data = repository.loadData()
    binding.textView.text = data  // Crash если Activity destroyed
}

// ХОРОШО
lifecycleScope.launch {
    val data = repository.loadData()
    binding.textView.text = data  // Безопасно
}
```

### 2. Blocking calls внутри coroutine

```kotlin
// ПЛОХО: блокирует Main Thread несмотря на launch
lifecycleScope.launch {
    val data = blockingNetworkCall()  // НЕ suspend функция!
    binding.textView.text = data
}

// ХОРОШО
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        blockingNetworkCall()  // Выполняется на IO
    }
    binding.textView.text = data
}
```

### 3. Забытый withContext

```kotlin
// ПЛОХО: Dispatchers.IO внутри launch всё равно выполняется на IO
// НО когда вернёмся, мы уже не на Main Thread!
lifecycleScope.launch(Dispatchers.IO) {
    val data = repository.loadData()
    binding.textView.text = data  // CRASH или undefined behavior
}

// ХОРОШО
lifecycleScope.launch {
    val data = withContext(Dispatchers.IO) {
        repository.loadData()
    }
    // Мы снова на Main Thread
    binding.textView.text = data
}
```

---

## Чеклист

```
□ Все I/O операции на Dispatchers.IO
□ Все CPU-heavy операции на Dispatchers.Default
□ Все UI операции на Dispatchers.Main (lifecycleScope по умолчанию)
□ Используем lifecycleScope в Activity/Fragment
□ Используем viewModelScope в ViewModel
□ Flow собираем с repeatOnLifecycle
□ Нет GlobalScope в production коде
□ Обрабатываем исключения в coroutines
□ Тестируем с runTest
```

---

## Связь с другими темами

### [[android-overview]]
Threading — одна из ключевых тем в экосистеме Android, связанная с производительностью, UI-отзывчивостью и background work. Карта Android раздела показывает, как threading пересекается с activity lifecycle, service, networking и data persistence. Понимание общей архитектуры платформы помогает выбрать правильный threading-механизм для каждой задачи.

### [[android-activity-lifecycle]]
Lifecycle компонентов напрямую влияет на threading: lifecycleScope автоматически отменяет корутины при уничтожении Activity, repeatOnLifecycle запускает/останавливает сбор Flow при переходах между состояниями. Без понимания lifecycle невозможно безопасно работать с потоками — утечки, краши после onDestroy() и обновления невидимого UI. Изучите lifecycle перед threading.

### [[android-handler-looper]]
Handler и Looper — низкоуровневый механизм, на котором построен Main Thread и межпоточное взаимодействие в Android. Main Thread — это Thread с Looper, обрабатывающий Message queue. Корутины с Dispatchers.Main используют Handler внутри для отправки задач на Main Thread. Понимание Handler-Looper объясняет, почему ANR происходит и как Choreographer координирует рендеринг.

### [[kotlin-coroutines]]
Корутины — основной механизм асинхронности в современном Android. Suspend-функции, Dispatchers (Main, IO, Default), structured concurrency и CoroutineScope — инструменты, которые заменили AsyncTask, HandlerThread и RxJava. Без глубокого понимания корутин невозможно писать production-ready асинхронный код. Рекомендуется изучить основы threading, затем углубиться в корутины.

### [[kotlin-flow]]
Flow — реактивный примитив для потоковой обработки данных, построенный на корутинах. StateFlow и SharedFlow используются для передачи данных между потоками и UI. Операторы flowOn, buffer, conflate управляют тем, на каких потоках выполняется работа. Понимание Flow критично для reactive state management и efficient data streaming.

### [[os-processes-threads]]
Потоки на уровне ОС — фундамент, на котором построена вся модель threading в Android. Понимание thread states, context switching, CPU scheduling и thread priorities объясняет, почему Dispatchers.IO имеет пул из 64 потоков, а Dispatchers.Default — по числу ядер CPU. Изучите OS-уровень для глубокого понимания производительности и trade-offs.

### [[os-scheduling]]
Алгоритмы планирования потоков ОС (CFS в Linux) определяют, как Android распределяет CPU-время между потоками приложения. Priority inversion, thread starvation и preemption — концепции, которые объясняют поведение многопоточного кода. Android использует cgroups и nice values для приоритизации foreground-потоков над background.

### [[os-synchronization]]
Mutex, semaphore, race conditions и deadlock — фундаментальные концепции синхронизации, актуальные для Android threading. Kotlin Mutex, synchronized блоки, AtomicReference и Channel — всё это построено на OS-примитивах синхронизации. Понимание этих концепций предотвращает data races и deadlocks в многопоточном коде.

---

## Источники

- [Kotlin Coroutines on Android - Android Developers](https://developer.android.com/kotlin/coroutines) — официальный гайд
- [Best Practices for Coroutines in Android](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) — лучшие практики
- [Coroutines Overview - Kotlin Documentation](https://kotlinlang.org/docs/coroutines-overview.html) — официальная документация Kotlin
- [Improve App Performance with Kotlin Coroutines](https://developer.android.com/kotlin/coroutines/coroutines-adv) — продвинутые техники

## Источники и дальнейшее чтение

- **Goetz B. (2006). Java Concurrency in Practice.** — Фундаментальная книга по многопоточности на JVM: thread safety, visibility, ordering, concurrent collections. Несмотря на возраст, концепции актуальны — корутины строятся поверх тех же JVM-потоков. Обязательна для глубокого понимания threading.
- **Moskala M. (2022). Kotlin Coroutines Deep Dive.** — Полное руководство по корутинам: от suspend-функций до structured concurrency, Dispatchers и Flow. Объясняет, как корутины работают внутри и как правильно использовать их в Android. Лучший ресурс по теме.
- **Meier R. (2022). Professional Android.** — Практическое покрытие threading в контексте Android: Main Thread rule, background processing, WorkManager и интеграция корутин с lifecycle компонентов.

---

---

## Проверь себя

> [!question]- Почему Android запрещает выполнение сетевых операций на Main Thread?
> Main Thread отвечает за рендеринг UI с частотой 60 FPS (16ms на кадр). Сетевая операция может занять 100ms-10s, блокируя рендеринг. После 5 секунд система показывает ANR dialog. StrictMode.ThreadPolicy по умолчанию бросает NetworkOnMainThreadException для раннего обнаружения.

> [!question]- Сценарий: приложение использует Thread() для загрузки данных. Какие проблемы возникнут?
> 1) Memory leak: Thread держит reference на Activity (через inner class или lambda). 2) Crash при обновлении UI: CalledFromWrongThreadException. 3) Нет lifecycle awareness: Thread продолжает работу после onDestroy(). 4) Нет cancellation: невозможно остановить при навигации. Решение: Coroutines с viewModelScope.


---

## Ключевые карточки

Какие потоки есть в Android-приложении?
?
Main Thread (UI Thread): рендеринг, touch events, lifecycle callbacks. Background threads: сеть, БД, тяжелые вычисления. RenderThread: GPU операции (с Android 5.0). Binder threads: IPC вызовы.

Что такое ANR и когда возникает?
?
Application Not Responding. Main Thread заблокирован > 5 секунд (touch/key events) или BroadcastReceiver не завершился за 10 секунд. Система показывает диалог 'приложение не отвечает'. Причина: тяжелая работа на UI Thread.

Какие способы фоновой работы в Android?
?
Coroutines (рекомендуемый), Executors/Thread pools, HandlerThread, WorkManager (periodic/deferred), RxJava (legacy). Coroutines: lightweight, structured concurrency, lifecycle-aware через viewModelScope.

Что такое Dispatchers в корутинах?
?
Main: UI operations. IO: сетевые/дисковые операции (64 потока). Default: CPU-bound (кол-во cores). Unconfined: стартует в текущем потоке. Main.immediate: без переключения если уже на Main.

Что такое StrictMode?
?
Debug tool для обнаружения операций на неправильном потоке. ThreadPolicy: disk/network на Main Thread. VmPolicy: leaks, cleartext traffic. Включать в debug builds. Помогает находить проблемы до production.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-handler-looper]] | Handler/Looper — основа Threading в Android |
| Практика | [[android-coroutines-guide]] | Практический гайд по корутинам в Android |
| Углубиться | [[android-coroutines-mistakes]] | Типичные ошибки с корутинами |
| Смежная тема | [[ios-threading-fundamentals]] | Threading в iOS: GCD и async/await |
| Обзор | [[android-overview]] | Вернуться к карте раздела |


*Проверено: 2026-01-09 | Обновлено с 18 | На основе официальной документации Android и Kotlin*
