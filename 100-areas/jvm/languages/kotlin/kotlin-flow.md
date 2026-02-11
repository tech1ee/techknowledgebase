---
title: "Kotlin Flow: Реактивные потоки данных"
created: 2025-11-25
modified: 2026-01-03
tags:
  - topic/jvm
  - flow
  - reactive
  - stateflow
  - sharedflow
  - coroutines
  - type/concept
  - level/intermediate
prerequisites:
  - "[[kotlin-coroutines]]"
  - "[[kotlin-functional]]"
related:
  - "[[kotlin-coroutines]]"
  - "[[android-state-management]]"
  - "[[kotlin-channels]]"
status: published
---

# Kotlin Flow: реактивные потоки данных

> **TL;DR:** Flow — реактивные потоки данных на базе корутин. Cold Flow (flow{}) запускается при collect. Hot Flow: StateFlow для состояния (замена LiveData), SharedFlow для событий. Backpressure из коробки через suspend. flowOn для смены Dispatcher, stateIn/shareIn для конвертации cold→hot. В Android: collectAsStateWithLifecycle() в Compose, repeatOnLifecycle в Fragment.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin Coroutines | suspend, CoroutineScope, Dispatchers | [[kotlin-coroutines]] |
| Reactive programming | Понимать streams, operators | Любой RxJava/Reactor tutorial |
| Android Lifecycle | lifecycleScope, repeatOnLifecycle | [[android-architecture]] |

---

## Зачем это нужно

**Проблема:** В приложениях часто нужно работать с потоками данных:
- **Обновления из базы данных** — Room возвращает новые данные при изменении
- **Сетевые события** — WebSocket соединения, Server-Sent Events
- **UI события** — клики, ввод текста, скролл
- **Местоположение** — GPS обновления приходят постоянно

**Попытки решения и их проблемы:**
- **Callbacks** — callback hell, сложно комбинировать, нет backpressure
- **LiveData** — только для UI, нет трансформаций, привязан к Android
- **RxJava** — 2500+ методов, сложный learning curve, отдельная dependency

**Решение Flow:** Kotlin Flow — реактивные потоки, встроенные в корутины:
- **Простой API** — знакомые операторы (map, filter, flatMap)
- **Backpressure из коробки** — suspend функции естественно контролируют скорость
- **Часть kotlinx.coroutines** — не нужна отдельная библиотека
- **Structured concurrency** — автоматическая отмена при отмене корутины

**В Android:** Flow заменяет LiveData. StateFlow хранит состояние UI, SharedFlow транслирует события. Google рекомендует Flow как стандарт для реактивных потоков.

### Актуальность 2024-2025

| API | Статус | Описание |
|-----|--------|----------|
| **collectAsStateWithLifecycle()** | ✅ Best Practice | Lifecycle-aware collection в Compose |
| **repeatOnLifecycle** | ✅ Стандарт | Правильный collect в Activity/Fragment |
| **MutableStateFlow.update{}** | ✅ Рекомендован | Атомарные обновления (вместо .value =) |
| **SharingStarted.WhileSubscribed(5000)** | ✅ Best Practice | Оптимальная стратегия для ViewModels |
| **Channel для events** | ✅ Альтернатива | Вместо SharedFlow для one-time events |

**Критические изменения:**

```kotlin
// ❌ УСТАРЕЛО: collect без lifecycle
lifecycleScope.launch {
    viewModel.state.collect { ... }  // Утечка при background!
}

// ✅ ПРАВИЛЬНО 2024: collectAsStateWithLifecycle в Compose
@Composable
fun Screen(viewModel: MyViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()
}

// ✅ ПРАВИЛЬНО 2024: repeatOnLifecycle в Fragment
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.state.collect { ... }
    }
}
```

---

## Типы Flow

Flow делятся на холодные и горячие:

- **Cold Flow** (`flow {}`) — запускается только при collect, каждый подписчик получает свою копию
- **Hot Flow** — работает независимо от подписчиков:
  - **StateFlow** — хранит текущее состояние (замена LiveData)
  - **SharedFlow** — для событий без состояния (one-time events)

Операторы (map, filter, flatMapLatest) работают как в коллекциях, но асинхронно. `flowOn` переключает Dispatcher, `stateIn/shareIn` превращают холодный поток в горячий.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Flow** | Асинхронная последовательность значений | Река — данные текут к потребителю |
| **Cold Flow** | Запускается только при подписке (collect) | Netflix — фильм начинается когда нажал play |
| **Hot Flow** | Работает независимо от подписчиков | Радио — вещает всегда, слышишь когда включил |
| **Emit** | Отправка значения в поток | Отправить письмо в почтовый ящик |
| **Collect** | Подписка и получение значений | Проверять почтовый ящик и забирать письма |
| **Backpressure** | Контроль скорости производства/потребления | Шлюз на реке — регулирует поток воды |
| **StateFlow** | Горячий поток с текущим состоянием | Термометр — всегда показывает текущую температуру |
| **SharedFlow** | Горячий поток для событий без состояния | Школьный звонок — слышат все кто рядом |
| **Upstream** | Операции до текущей точки | Выше по течению реки |
| **Downstream** | Операции после текущей точки | Ниже по течению реки |
| **flowOn** | Смена Dispatcher для upstream операций | Переключить на другой конвейер |
| **stateIn/shareIn** | Конвертация cold→hot | Превратить on-demand сервис в live трансляцию |

---

## Основы Flow

### Что такое Flow?

Flow создаётся через builder `flow {}`, внутри которого `emit()` отправляет значения подписчику. Каждый `delay()` приостанавливает корутину, не блокируя поток:

```kotlin
fun simpleFlow(): Flow<Int> = flow {
    for (i in 1..3) {
        delay(1000)  // Эмулируем async работу
        emit(i)      // Испускаем значение
    }
}

suspend fun collectFlow() {
    simpleFlow().collect { value ->
        println(value)  // 1, 2, 3 с задержкой по 1 сек
    }
}
```

Ключевое свойство холодного Flow -- каждый вызов `collect` запускает поток заново. Два подписчика получат две независимые копии данных:

```kotlin
fun numbers(): Flow<Int> = flow {
    emit(1); emit(2); emit(3)
}

suspend fun main() {
    val flow = numbers()
    flow.collect { println("First: $it") }   // 1, 2, 3
    flow.collect { println("Second: $it") }  // 1, 2, 3 снова
}
```

**Почему Flow?**
- Асинхронность: на базе корутин, не блокируют потоки
- Холодные: не работают пока нет подписчика
- Backpressure из коробки: suspend функции естественным образом контролируют поток
- Интеграция с корутинами: можно использовать все возможности корутин

### Flow builders

Kotlin предлагает несколько способов создания Flow. Простейшие -- `flowOf` для фиксированных значений и `asFlow` для конвертации коллекций:

```kotlin
val flow1 = flow { emit(1); emit(2); emit(3) }
val flow2 = flowOf(1, 2, 3, 4, 5)
val flow3 = listOf(1, 2, 3).asFlow()
val flow4 = (1..5).asFlow()
val empty = emptyFlow<Int>()
```

Для интеграции с callback-based API (Firebase, Bluetooth, сенсоры) используется `channelFlow`. Он позволяет отправлять значения из callback-ов, которые вызываются из других потоков:

```kotlin
fun callbackFlow(): Flow<String> = channelFlow {
    val callback = object : Callback {
        override fun onData(data: String) {
            trySend(data)  // Отправка из callback
        }
        override fun onComplete() {
            close()
        }
    }
    registerCallback(callback)
    awaitClose { unregisterCallback(callback) }
}
```

### Отмена Flow

```kotlin
// Flow автоматически отменяется при отмене корутины
fun main() = runBlocking {
    val job = launch {
        flow {
            repeat(10) {
                delay(100)
                emit(it)
            }
        }.collect { value ->
            println(value)
        }
    }

    delay(350)
    job.cancel()  // Flow остановится
}
// Output: 0, 1, 2 (остановится на 3)

// Cleanup в onCompletion
flow {
    try {
        emit(1)
        emit(2)
    } finally {
        println("Flow completed")
    }
}.onCompletion {
    println("Cleanup")
}.collect { println(it) }
```

## Flow операторы

### Промежуточные операторы (intermediate)

Промежуточные операторы трансформируют поток, не запуская его. `map` и `filter` работают как в коллекциях, но асинхронно -- каждый элемент может приостанавливаться:

```kotlin
flowOf(1, 2, 3).map { it * 2 }
    .collect { println(it) }  // 2, 4, 6

(1..10).asFlow().filter { it % 2 == 0 }
    .collect { println(it) }  // 2, 4, 6, 8, 10
```

`transform` -- наиболее гибкий оператор: он позволяет emit несколько значений на каждый входной элемент. `take` и `drop` ограничивают количество элементов, а `distinctUntilChanged` убирает повторяющиеся подряд:

```kotlin
(1..3).asFlow().transform { value ->
    emit("Start $value")  // Можем emit несколько значений
    delay(100)
    emit("End $value")
}

(1..10).asFlow().take(3)
    .collect { println(it) }  // 1, 2, 3

flowOf(1, 1, 2, 2, 3, 1).distinctUntilChanged()
    .collect { println(it) }  // 1, 2, 3, 1
```

### Операторы контекста

`flowOn` переключает dispatcher для всех операций выше себя (upstream). Это правильный способ разделить контексты: производство на IO, потребление на Main:

```kotlin
fun fetchData(): Flow<String> = flow {
    repeat(3) { delay(1000); emit("Data $it") }
}.flowOn(Dispatchers.IO)  // upstream выполнится на IO

suspend fun main() = coroutineScope {
    fetchData()
        .map { it.uppercase() }
        .collect { println(it) }  // На текущем контексте
}
```

`buffer` позволяет производителю и потребителю работать параллельно. Без буфера каждый emit ждёт обработки предыдущего. С буфером -- производитель продолжает работать, пока потребитель обрабатывает:

```kotlin
flow { repeat(3) { delay(100); emit(it) } }
    .buffer()
    .collect { delay(300); println(it) }
// Без buffer: 1200ms. С buffer: ~900ms
```

`conflate` идёт дальше: если потребитель не успевает, промежуточные значения пропускаются. Потребитель всегда получает последнее актуальное значение:

```kotlin
flow { repeat(10) { delay(100); emit(it) } }
    .conflate()
    .collect { delay(500); println(it) }
// 0, 4, 8 (промежуточные пропущены)
```

**Почему flowOn нужен?**
- Разделение контекстов: производство на IO, потребление на Main
- В отличие от withContext: flowOn меняет контекст для всех upstream операций
- Позволяет создавать правильную архитектуру: Repository на IO, UI на Main

### Комбинирование потоков

`zip` комбинирует элементы двух потоков попарно. Когда один поток заканчивается -- результат тоже:

```kotlin
val numbers = (1..3).asFlow()
val strings = flowOf("one", "two", "three")

numbers.zip(strings) { num, str -> "$num -> $str" }
    .collect { println(it) }
// 1 -> one, 2 -> two, 3 -> three
```

`combine` работает иначе: при каждом новом значении из любого потока он комбинирует его с последним значением из другого. Это идеально для UI, где нужно реагировать на изменение любого источника:

```kotlin
val nums = flow { emit(1); delay(500); emit(2) }
val strs = flow { emit("a"); delay(250); emit("b"); delay(250); emit("c") }

nums.combine(strs) { num, str -> "$num$str" }
    .collect { println(it) }
// 1a, 1b, 2b, 2c
```

Три варианта flatMap отличаются стратегией обработки внутренних потоков. `flatMapConcat` обрабатывает последовательно, `flatMapMerge` -- параллельно, `flatMapLatest` отменяет предыдущий при появлении нового значения:

```kotlin
// flatMapConcat -- строго последовательно
(1..3).asFlow().flatMapConcat { value ->
    flow { emit("$value: First"); delay(500); emit("$value: Second") }
}.collect { println(it) }
// 1: First, 1: Second, 2: First, 2: Second, 3: First, 3: Second
```

`flatMapLatest` особенно полезен для поиска: при каждом новом символе предыдущий запрос отменяется и запускается новый:

```kotlin
flow { emit(1); delay(150); emit(2); delay(150); emit(3) }
    .flatMapLatest { value ->
        flow { emit("$value: First"); delay(500); emit("$value: Second") }
    }.collect { println(it) }
// 1: First, 2: First, 3: First, 3: Second (1 и 2 отменяются)
```

**Когда использовать какой flatMap:**
- `flatMapConcat`: когда важен порядок, последовательная обработка
- `flatMapMerge`: для параллельной обработки, порядок не важен
- `flatMapLatest`: для поиска/автодополнения, нужно только последнее значение

## StateFlow - состояние

### Основы StateFlow

StateFlow -- горячий поток, который всегда хранит текущее значение. Паттерн с `MutableStateFlow` внутри и read-only `StateFlow` снаружи -- стандарт для ViewModel:

```kotlin
class CounterViewModel {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter

    fun increment() { _counter.value++ }
    fun decrement() { _counter.value-- }
}
```

Подписчик получает текущее значение сразу при подписке. Новый подписчик не пропустит состояние -- он увидит последнее значение:

```kotlin
val viewModel = CounterViewModel()
println(viewModel.counter.value)  // 0

launch {
    viewModel.counter.collect { value ->
        println("Counter: $value")
    }
}

viewModel.increment()  // Counter: 1
viewModel.increment()  // Counter: 2
```

**Почему StateFlow?**
- Горячий: всегда активен, хранит текущее значение
- Thread-safe: безопасное обновление из любого потока
- Conflated: пропускает промежуточные значения если подписчик медленный
- Замена LiveData: лучше интеграция с корутинами

### StateFlow vs LiveData

Ключевое преимущество StateFlow перед LiveData -- thread-safety: `_data.value = value` можно вызывать с любого потока без `postValue()`:

```kotlin
// LiveData: update только с Main потока
class LiveDataViewModel : ViewModel() {
    private val _data = MutableLiveData<String>()
    val data: LiveData<String> = _data
    fun update(value: String) { _data.value = value }
}

// StateFlow: thread-safe из любого потока
class StateFlowViewModel : ViewModel() {
    private val _data = MutableStateFlow("")
    val data: StateFlow<String> = _data
    fun update(value: String) { _data.value = value }
}
```

В UI подписка на StateFlow требует lifecycle-aware подхода. Без него Flow продолжит collect даже в background, тратя ресурсы:

```kotlin
// LiveData -- lifecycle-aware из коробки
viewModel.data.observe(viewLifecycleOwner) { updateUI(it) }

// StateFlow -- используйте flowWithLifecycle
lifecycleScope.launch {
    viewModel.data.flowWithLifecycle(lifecycle)
        .collect { updateUI(it) }
}
```

### Обновление StateFlow

Для сложного UI-состояния используют data class с `copy()`. Метод `update {}` обеспечивает атомарность -- важно при обновлении из нескольких корутин:

```kotlin
data class UiState(
    val isLoading: Boolean = false,
    val data: List<String> = emptyList(),
    val error: String? = null
)

class ViewModel {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState

    // update -- атомарное обновление (рекомендован)
    fun addItem(item: String) {
        _uiState.update { it.copy(data = it.data + item) }
    }
}
```

Типичный паттерн загрузки данных: показать loading, загрузить, обработать ошибку. Все обновления через `update {}` для thread-safety:

```kotlin
fun loadData() {
    viewModelScope.launch {
        _uiState.update { it.copy(isLoading = true, error = null) }
        try {
            val data = fetchData()
            _uiState.update { it.copy(isLoading = false, data = data) }
        } catch (e: Exception) {
            _uiState.update { it.copy(isLoading = false, error = e.message) }
        }
    }
}
```

### Производные StateFlow

```kotlin
class UserViewModel {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user

    // Производное состояние
    val userName: StateFlow<String> = _user
        .map { it?.name ?: "Guest" }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = "Guest"
        )

    val isLoggedIn: StateFlow<Boolean> = _user
        .map { it != null }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.Eagerly,
            initialValue = false
        )
}

// Комбинирование нескольких StateFlow
class CombinedViewModel {
    private val _firstName = MutableStateFlow("")
    private val _lastName = MutableStateFlow("")

    val fullName: StateFlow<String> = combine(
        _firstName,
        _lastName
    ) { first, last ->
        "$first $last".trim()
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(),
        initialValue = ""
    )
}
```

**SharingStarted стратегии:**
- `Eagerly`: запускается сразу, никогда не останавливается
- `Lazily`: запускается при первом подписчике, никогда не останавливается
- `WhileSubscribed(stopTimeout)`: активен пока есть подписчики + timeout

## SharedFlow - события

### Основы SharedFlow

```kotlin
// SharedFlow - горячий поток для событий (нет текущего состояния)
class EventViewModel {
    private val _events = MutableSharedFlow<String>()
    val events: SharedFlow<String> = _events

    suspend fun sendEvent(event: String) {
        _events.emit(event)  // suspend, ждёт пока подписчики обработают
    }

    fun tryEmit(event: String): Boolean {
        return _events.tryEmit(event)  // не suspend, может не доставить
    }
}

// Использование
val viewModel = EventViewModel()

// Подписка
launch {
    viewModel.events.collect { event ->
        println("Received: $event")
    }
}

// Отправка
viewModel.sendEvent("Click")  // Получат все текущие подписчики
```

**StateFlow vs SharedFlow:**
- StateFlow: для состояния, всегда есть value, conflated
- SharedFlow: для событий, нет текущего value, можно настроить буферизацию

### Конфигурация SharedFlow

```kotlin
// replay - сколько последних значений получит новый подписчик
val flow1 = MutableSharedFlow<String>(replay = 0)  // Ничего не получит
val flow2 = MutableSharedFlow<String>(replay = 1)  // Получит последнее
val flow3 = MutableSharedFlow<String>(replay = 5)  // Получит 5 последних

// extraBufferCapacity - дополнительный буфер
val flow4 = MutableSharedFlow<String>(
    replay = 1,
    extraBufferCapacity = 10  // Буфер на 11 значений (replay + extra)
)

// onBufferOverflow - стратегия при переполнении
val flow5 = MutableSharedFlow<String>(
    replay = 1,
    extraBufferCapacity = 10,
    onBufferOverflow = BufferOverflow.DROP_OLDEST  // Удалить старые
)

// DROP_LATEST - удалить новые
// SUSPEND - suspend emit до освобождения места
```

### SharedFlow для событий UI

```kotlin
sealed class UiEvent {
    data class ShowSnackbar(val message: String) : UiEvent()
    data class Navigate(val route: String) : UiEvent()
    object ShowLoading : UiEvent()
    object HideLoading : UiEvent()
}

class MyViewModel : ViewModel() {
    private val _events = MutableSharedFlow<UiEvent>()
    val events = _events.asSharedFlow()

    fun onButtonClick() {
        viewModelScope.launch {
            _events.emit(UiEvent.ShowSnackbar("Button clicked"))
        }
    }

    fun loadData() {
        viewModelScope.launch {
            _events.emit(UiEvent.ShowLoading)
            try {
                val data = fetchData()
                _events.emit(UiEvent.HideLoading)
            } catch (e: Exception) {
                _events.emit(UiEvent.HideLoading)
                _events.emit(UiEvent.ShowSnackbar("Error: ${e.message}"))
            }
        }
    }
}

// В UI
lifecycleScope.launch {
    viewModel.events.collect { event ->
        when (event) {
            is UiEvent.ShowSnackbar -> showSnackbar(event.message)
            is UiEvent.Navigate -> navigate(event.route)
            UiEvent.ShowLoading -> showProgressBar()
            UiEvent.HideLoading -> hideProgressBar()
        }
    }
}
```

## Backpressure и буферизация

### Естественный backpressure

```kotlin
// Flow с suspend естественно поддерживает backpressure
fun producer() = flow {
    repeat(100) {
        emit(it)  // suspend пока потребитель обрабатывает
    }
}

suspend fun slowConsumer() {
    producer().collect { value ->
        delay(1000)  // Медленная обработка
        println(value)
    }
    // Производитель автоматически замедляется
}
```

### Стратегии буферизации

```kotlin
val flow = flow {
    repeat(10) {
        delay(100)
        emit(it)
        println("Emitted $it")
    }
}

// Без buffer - последовательно
flow.collect {
    delay(500)
    println("Collected $it")
}
// Emitted 0, Collected 0 (600ms), Emitted 1, Collected 1 (600ms)...

// С buffer - параллельно
flow.buffer().collect {
    delay(500)
    println("Collected $it")
}
// Emitted 0, 1, 2, 3... (быстро), Collected 0, 1, 2... (медленно)

// conflate - пропуск промежуточных
flow.conflate().collect {
    delay(500)
    println("Collected $it")
}
// Collected 0, 4, 8... (пропускает промежуточные)

// collectLatest - отменяет предыдущий при новом
flow.collectLatest { value ->
    println("Start $value")
    delay(500)
    println("End $value")  // Может не выполниться
}
// Start 0, Start 1, Start 2, ..., End 9 (только последний завершится)
```

**Когда использовать:**
- `buffer()`: производитель и потребитель должны работать параллельно
- `conflate()`: важны только последние значения (UI updates)
- `collectLatest()`: важно обрабатывать только последнее (поиск, автодополнение)

## Обработка ошибок

### try-catch в Flow

```kotlin
// try-catch внутри flow builder
fun fetchData(): Flow<String> = flow {
    try {
        val data = apiCall()
        emit(data)
    } catch (e: Exception) {
        emit("Error: ${e.message}")
    }
}

// try-catch при сборе
suspend fun collectSafely() {
    try {
        fetchData().collect { value ->
            println(value)
        }
    } catch (e: Exception) {
        println("Collection error: $e")
    }
}
```

### catch оператор

```kotlin
// catch для обработки upstream исключений
flow {
    emit(1)
    emit(2)
    throw Exception("Error in flow")
    emit(3)  // Не выполнится
}
    .catch { e ->
        println("Caught: $e")
        emit(-1)  // Можем emit fallback значение
    }
    .collect { value ->
        println("Collected: $value")
    }
// Collected: 1
// Collected: 2
// Caught: Exception: Error in flow
// Collected: -1

// catch НЕ ловит исключения в collect!
flow {
    emit(1)
    emit(2)
}
    .catch { e ->
        println("Never called")
    }
    .collect { value ->
        throw Exception("Error in collect")  // НЕ будет поймано!
    }

// Правильно: onEach + catch
flow {
    emit(1)
    emit(2)
}
    .onEach { value ->
        if (value == 2) throw Exception("Error")
    }
    .catch { e ->
        println("Caught: $e")
    }
    .collect()
```

### retry оператор

```kotlin
// retry - повторная попытка при ошибке
fun unstableFlow() = flow {
    emit(1)
    emit(2)
    if (Random.nextBoolean()) {
        throw Exception("Random error")
    }
    emit(3)
}

unstableFlow()
    .retry(retries = 3)  // До 3 повторных попыток
    .collect { println(it) }

// retry с условием
unstableFlow()
    .retry(retries = 3) { cause ->
        cause is IOException  // Только для IO ошибок
    }
    .collect { println(it) }

// retryWhen - полный контроль
fun fetchData() = flow<String> {
    // Может упасть
}

fetchData()
    .retryWhen { cause, attempt ->
        if (cause is IOException && attempt < 3) {
            delay(1000 * attempt)  // Экспоненциальная задержка
            true  // Повторить
        } else {
            false  // Не повторять
        }
    }
    .collect { println(it) }
```

## Тестирование Flow

### Тестирование с runTest

```kotlin
import kotlinx.coroutines.test.*

class FlowTest {
    @Test
    fun testSimpleFlow() = runTest {
        val flow = flowOf(1, 2, 3)

        val result = flow.toList()

        assertEquals(listOf(1, 2, 3), result)
    }

    @Test
    fun testFlowWithDelay() = runTest {
        val flow = flow {
            emit(1)
            delay(1000)
            emit(2)
            delay(1000)
            emit(3)
        }

        val result = flow.toList()
        // delay автоматически ускоряется в runTest

        assertEquals(listOf(1, 2, 3), result)
    }

    @Test
    fun testStateFlow() = runTest {
        val stateFlow = MutableStateFlow(0)

        assertEquals(0, stateFlow.value)

        stateFlow.value = 1
        assertEquals(1, stateFlow.value)
    }
}
```

### Turbine для тестирования Flow

```kotlin
import app.cash.turbine.test

class FlowTest {
    @Test
    fun testFlowWithTurbine() = runTest {
        val flow = flow {
            emit(1)
            delay(100)
            emit(2)
            delay(100)
            emit(3)
        }

        flow.test {
            assertEquals(1, awaitItem())
            assertEquals(2, awaitItem())
            assertEquals(3, awaitItem())
            awaitComplete()
        }
    }

    @Test
    fun testStateFlowUpdates() = runTest {
        val stateFlow = MutableStateFlow(0)

        launch {
            stateFlow.test {
                assertEquals(0, awaitItem())
                assertEquals(1, awaitItem())
                assertEquals(2, awaitItem())
                awaitComplete()
            }
        }

        stateFlow.value = 1
        stateFlow.value = 2
    }
}
```

## Практические паттерны

### Repository паттерн

```kotlin
interface UserRepository {
    fun getUser(id: String): Flow<User>
    fun observeUsers(): Flow<List<User>>
    suspend fun updateUser(user: User)
}

class UserRepositoryImpl(
    private val api: UserApi,
    private val db: UserDatabase
) : UserRepository {

    // Холодный Flow для разовых запросов
    override fun getUser(id: String): Flow<User> = flow {
        // Сначала из кэша
        val cached = db.getUser(id)
        if (cached != null) {
            emit(cached)
        }

        // Затем с сервера
        val fresh = api.fetchUser(id)
        db.saveUser(fresh)
        emit(fresh)
    }.flowOn(Dispatchers.IO)

    // Горячий Flow для наблюдения
    override fun observeUsers(): Flow<List<User>> {
        return db.observeUsers()  // Room Flow
            .flowOn(Dispatchers.IO)
    }

    override suspend fun updateUser(user: User) = withContext(Dispatchers.IO) {
        api.updateUser(user)
        db.saveUser(user)
    }
}
```

### Кэширование с SharedFlow

```kotlin
class DataRepository {
    private val _dataFlow = MutableSharedFlow<Data>(
        replay = 1,  // Кэшируем последнее значение
        extraBufferCapacity = 1
    )

    val dataFlow: SharedFlow<Data> = _dataFlow

    private var isFetching = false

    suspend fun fetchData() {
        if (isFetching) return  // Избегаем дублирующих запросов

        isFetching = true
        try {
            val data = api.fetchData()
            _dataFlow.emit(data)
        } finally {
            isFetching = false
        }
    }

    // Все подписчики получат один и тот же результат
}
```

### Search с debounce

```kotlin
class SearchViewModel : ViewModel() {
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery

    val searchResults: StateFlow<List<Result>> = _searchQuery
        .debounce(300)  // Ждём 300ms после последнего ввода
        .filter { it.length >= 3 }  // Минимум 3 символа
        .distinctUntilChanged()  // Не повторяем тот же запрос
        .flatMapLatest { query ->
            searchRepository.search(query)  // Отменяем предыдущий при новом
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }
}
```

### Pagination с Flow

```kotlin
class PaginationViewModel : ViewModel() {
    private val _page = MutableStateFlow(0)

    val items: StateFlow<List<Item>> = _page
        .flatMapLatest { page ->
            repository.fetchPage(page)
        }
        .scan(emptyList<Item>()) { accumulated, newItems ->
            accumulated + newItems  // Аккумулируем результаты
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(),
            initialValue = emptyList()
        )

    fun loadNextPage() {
        _page.value++
    }
}
```

## Распространённые ошибки

### 1. Забыли flowOn для тяжёлых операций

```kotlin
// ❌ Тяжёлая работа на текущем потоке
fun getData(): Flow<Data> = flow {
    val data = heavyComputation()  // На каком потоке вызывается collect!
    emit(data)
}

// ✅ Явно указываем диспетчер
fun getData(): Flow<Data> = flow {
    val data = heavyComputation()
    emit(data)
}.flowOn(Dispatchers.Default)
```

### 2. Множественные подписки на холодный Flow

```kotlin
// ❌ Каждый collect запускает flow заново
val flow = flow {
    println("Fetching from network")
    emit(apiCall())
}

launch { flow.collect { /* ... */ } }  // Запрос 1
launch { flow.collect { /* ... */ } }  // Запрос 2!

// ✅ Используйте SharedFlow или shareIn
val sharedFlow = flow {
    println("Fetching from network")
    emit(apiCall())
}.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(),
    replay = 1
)

launch { sharedFlow.collect { /* ... */ } }  // Один запрос
launch { sharedFlow.collect { /* ... */ } }  // Тот же результат
```

### 3. catch не ловит исключения в collect

```kotlin
// ❌ catch не поймает
flow { emit(1) }
    .catch { /* Never called */ }
    .collect { throw Exception() }

// ✅ Используйте onEach перед catch
flow { emit(1) }
    .onEach {
        if (it == 1) throw Exception()
    }
    .catch { /* Will catch */ }
    .collect()

// Или try-catch вокруг collect
try {
    flow { emit(1) }.collect { throw Exception() }
} catch (e: Exception) {
    // Поймаем здесь
}
```

### 4. Утечка StateFlow/SharedFlow

```kotlin
// ❌ Горячий flow без привязки к scope
class MyClass {
    val flow = flow { /* ... */ }
        .stateIn(
            scope = GlobalScope,  // Будет жить вечно!
            started = SharingStarted.Eagerly,
            initialValue = null
        )
}

// ✅ Используйте подходящий scope
class MyViewModel : ViewModel() {
    val flow = flow { /* ... */ }
        .stateIn(
            scope = viewModelScope,  // Отменится с ViewModel
            started = SharingStarted.WhileSubscribed(),
            initialValue = null
        )
}
```

### 5. StateFlow пропускает одинаковые значения

```kotlin
// ❌ Одинаковые значения пропускаются
val stateFlow = MutableStateFlow(0)

launch {
    stateFlow.collect { println(it) }
}

stateFlow.value = 0  // Не напечатается (то же значение)
stateFlow.value = 1  // Напечатается
stateFlow.value = 1  // Не напечатается

// ✅ Используйте SharedFlow если нужны дубликаты
val sharedFlow = MutableSharedFlow<Int>()

launch {
    sharedFlow.collect { println(it) }
}

sharedFlow.emit(0)  // Напечатается
sharedFlow.emit(0)  // Напечатается снова
```

## Чеклист

- [ ] Используете холодные Flow для разовых операций
- [ ] Применяете StateFlow для состояния
- [ ] Используете SharedFlow для событий
- [ ] Добавляете flowOn для переключения диспетчера
- [ ] Обрабатываете ошибки через catch и retry
- [ ] Применяете shareIn/stateIn для разделения работы между подписчиками
- [ ] Используете правильные SharingStarted стратегии
- [ ] Знаете разницу между buffer/conflate/collectLatest
- [ ] Понимаете что catch не ловит в collect
- [ ] Привязываете горячие flow к правильному scope

## Куда дальше

**Если здесь впервые:**
→ [[kotlin-coroutines]] — без понимания корутин Flow не имеет смысла. Suspend, scope, dispatchers — всё оттуда.

**Углубление:**
→ [[kotlin-collections]] — операторы Flow (map, filter, fold) работают так же. Понимание одного помогает с другим.

**Практика:**
→ [[kotlin-testing]] — тестирование Flow с runTest и Turbine. Как проверять асинхронные потоки.
→ [[android-architecture]] — Flow в контексте Android: ViewModel, Repository, UI layer.

**Альтернативы и сравнение:**
→ [[android-threading]] — как Flow соотносится с другими способами асинхронности в Android.

---

## Проверь себя

### Вопросы для самопроверки

1. **В чём разница между холодным и горячим Flow?**
   - Cold Flow (flow{}) — запускается при collect, каждый подписчик получает свою копию
   - Hot Flow (StateFlow/SharedFlow) — работает независимо от подписчиков

2. **Когда использовать StateFlow vs SharedFlow?**
   - StateFlow — для состояния (UI state), всегда имеет значение
   - SharedFlow — для событий (navigation, toast), replay=0 по умолчанию

3. **Почему collect без lifecycle опасен?**
   - Flow продолжает collect даже когда app в background
   - Тратит ресурсы, может вызвать crash при обновлении UI
   - Решение: collectAsStateWithLifecycle() или repeatOnLifecycle

4. **Что делает flowOn?**
   - Меняет Dispatcher для UPSTREAM операций (до flowOn)
   - НЕ влияет на downstream и collect
   - Нельзя вызывать emit() после flowOn

5. **Почему catch не ловит исключения в collect?**
   - catch обрабатывает только upstream ошибки
   - Исключение в collect — это downstream
   - Решение: onEach перед catch или try-catch вокруг collect

---

## Кто использует и реальные примеры

| Компания | Как используют Flow | Результаты |
|----------|---------------------|------------|
| **Google** | Jetpack Compose state management | StateFlow как стандарт для UI state |
| **Square** | Cash App, Retrofit integration | SharedFlow для events, StateFlow для state |
| **Netflix** | Real-time data streams | Замена RxJava, проще debugging |
| **Twitter/X** | Timeline updates, notifications | Reactive UI с backpressure |
| **Airbnb** | Search filters, availability updates | Debounce + flatMapLatest для поиска |
| **Spotify** | Now Playing state, playlist updates | StateFlow для playback state |

### Flow vs RxJava: миграция

```
До (RxJava):                         После (Flow):
────────────────────────────────     ────────────────────────────────
Observable<T>                    →   Flow<T>
Single<T>                        →   suspend fun: T
BehaviorSubject<T>               →   MutableStateFlow<T>
PublishSubject<T>                →   MutableSharedFlow<T>
.subscribeOn(Schedulers.io())    →   .flowOn(Dispatchers.IO)
.observeOn(AndroidSchedulers)    →   collect на Main
CompositeDisposable              →   CoroutineScope

Результаты миграции:
- Меньше dependencies (kotlinx.coroutines включает Flow)
- Один async паттерн вместо двух (RxJava + Coroutines)
- Structured concurrency = меньше утечек памяти
- Learning curve: 2500+ методов RxJava → ~50 операторов Flow
```

### Паттерны в production

```
Паттерн 1: Search с debounce (Airbnb style)
─────────────────────────────────────────────
searchQuery
    .debounce(300)
    .filter { it.length >= 3 }
    .distinctUntilChanged()
    .flatMapLatest { searchRepository.search(it) }
    .stateIn(viewModelScope, WhileSubscribed(5000), emptyList())

Паттерн 2: Combine multiple sources (Spotify style)
─────────────────────────────────────────────
combine(
    userFlow,
    nowPlayingFlow,
    playlistFlow
) { user, track, playlist ->
    PlayerState(user, track, playlist)
}.stateIn(scope, SharingStarted.Eagerly, initialState)

Паттерн 3: One-time events (Square Cash App)
─────────────────────────────────────────────
private val _events = MutableSharedFlow<Event>()
val events = _events.asSharedFlow()

// или Channel для guaranteed delivery
private val _events = Channel<Event>(Channel.BUFFERED)
val events = _events.receiveAsFlow()
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Flow — это просто обёртка над Sequences" | Flow — cold asynchronous stream с suspend операциями. Sequences синхронные. Flow поддерживает backpressure, context switching, cancellation |
| "StateFlow и SharedFlow взаимозаменяемы" | StateFlow — всегда одно значение с conflation. SharedFlow — буфер и replay. StateFlow для state, SharedFlow для events |
| "collect() блокирует поток" | collect() suspend-функция, не блокирующая. Coroutine приостанавливается, thread освобождается для других задач |
| "flowOn меняет контекст collect" | flowOn влияет только на upstream (emissions). collect всегда выполняется в контексте вызывающего scope |
| "SharedFlow автоматически буферизует" | По умолчанию replay=0, extraBufferCapacity=0. Без буфера suspend пока subscriber не готов. Нужно явно настраивать |
| "StateFlow.value всегда актуален для UI" | value доступен синхронно, но может пропустить промежуточные значения (conflation). Для UI лучше collect с lifecycle |
| "flatMapLatest отменяет автоматически и мгновенно" | Отмена cooperative — внутренний flow должен проверять isActive или использовать cancellable операции |
| "stateIn(Eagerly) всегда лучше" | Eagerly потребляет ресурсы даже без subscribers. WhileSubscribed экономит ресурсы, но может пропустить начальные значения |
| "Flow.catch ловит все исключения" | catch ловит только upstream exceptions. Исключения в collect не перехватываются. Нужен отдельный try-catch |
| "callbackFlow устаревший из-за Compose" | callbackFlow всё ещё нужен для интеграции с callback-based API (Firebase, Bluetooth, Sensors). Compose не заменяет его |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin Flow |
|--------------|--------------------------|
| **Reactive Streams** | Flow реализует паттерн Publisher/Subscriber. Backpressure через suspension — producer ждёт consumer |
| **Cold vs Hot Observables** | Flow (cold) — новый stream для каждого collector. StateFlow/SharedFlow (hot) — shared state |
| **Continuation-Passing Style** | suspend collect реализован через CPS — состояние сохраняется между emissions |
| **Conflation** | StateFlow использует conflation — при медленном consumer промежуточные значения пропускаются |
| **Buffer Strategies** | SharedFlow поддерживает DROP_OLDEST, DROP_LATEST, SUSPEND — стратегии обработки переполнения |
| **Structured Concurrency** | Flow следует structured concurrency — cancellation propagates, resources cleaned up |
| **Context Propagation** | flowOn использует CoroutineContext — контекст передаётся по цепочке операторов |
| **Lazy Evaluation** | Flow operations lazy — chain строится, но не выполняется до terminal operation |
| **Monadic Composition** | map, flatMap, filter — функторные операции для композиции transformations |
| **Pull-based vs Push-based** | Flow pull-based (collector запрашивает) с push семантикой (producer отправляет когда готов) |

---

## Связь с другими темами

**[[kotlin-coroutines]]** — Flow полностью построен на coroutines: `flow {}` builder создаёт cold stream, который выполняется только при `collect` в coroutine scope. Cancellation, dispatchers, structured concurrency — всё это механизмы coroutines, которые Flow наследует. Без прочного понимания coroutines невозможно отлаживать Flow (deadlocks, cancellation, backpressure). Обязательно изучите coroutines перед Flow.

**[[android-state-management]]** — StateFlow и SharedFlow заменили LiveData как основной механизм UI state management в Android. StateFlow хранит текущее состояние экрана, SharedFlow транслирует одноразовые события (навигация, snackbar). Понимание Flow operators (map, combine, stateIn) необходимо для построения reactive UI architecture. Flow — технический механизм, state management — архитектурный паттерн его использования.

**[[kotlin-channels]]** — Channel и Flow решают разные задачи: Channel для communication между coroutines (fan-out, fan-in), Flow для reactive streams данных. SharedFlow внутри использует Channel для буферизации. Понимание различий помогает выбрать правильный инструмент: Channel для point-to-point, Flow для broadcast. Изучите оба для полной картины async-примитивов в Kotlin.

---

## Источники и дальнейшее чтение

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive*. — Главы о Flow: cold vs hot streams, операторы, backpressure, StateFlow/SharedFlow internals. Единственная книга с глубоким разбором Flow architecture.
- Jemerov D., Isakova S. (2024). *Kotlin in Action, 2nd Edition*. — Введение в Flow и reactive streams в контексте Kotlin-экосистемы. Хорошая стартовая точка.
- Elizarov R. (2019). *Cold flows, hot channels* (KotlinConf talk). — Доклад автора библиотеки о design decisions: почему Flow холодный, как он соотносится с Channel и Reactive Streams. Объясняет философию API.
- Yigit Boyar (2021). *A safer way to collect flows from Android UIs* (Android Dev Blog). — Практическое руководство Google по lifecycle-aware collection: repeatOnLifecycle, collectAsStateWithLifecycle. Обязательно для Android-разработчиков.

---

*Проверено: 2026-01-09 | Источники: Kotlin docs, Android Dev Summit 2024, Square engineering blog — Педагогический контент проверен*
