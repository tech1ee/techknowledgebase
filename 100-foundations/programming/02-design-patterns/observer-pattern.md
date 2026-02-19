---
title: "Observer: реакция на изменения состояния"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/design-patterns
  - topic/kotlin
  - pattern/behavioral
related:
  - "[[design-patterns-overview]]"
  - "[[strategy-pattern]]"
  - "[[state-pattern]]"
  - "[[kotlin-flow]]"
  - "[[android-state-management]]"
---

# Observer: реакция на изменения состояния

GoF Observer --- это `Subject.addObserver()` / `notify()` / `Observer.update()`. В Kotlin этот паттерн прошёл четыре эволюционные стадии: **callback-интерфейсы** (Java-стиль) -> **`Delegates.observable()`** (property-level) -> **`Flow`/`StateFlow`/`SharedFlow`** (реактивные потоки) -> **Compose `State`** (UI-наблюдение). Каждая стадия решала проблемы предыдущей. Сегодня `StateFlow` --- стандарт для наблюдения за состоянием, а `callbackFlow` --- мост из мира callback в мир корутин.

---

## Проблема: зависимые объекты не знают об изменениях

Представь приложение для торговли акциями. Цена акции изменилась --- и об этом должны узнать: график на экране, таблица портфолио, виджет уведомлений, модуль аналитики, push-сервис. Каждый из них живёт в своём модуле и не должен знать друг о друге.

```kotlin
// ПЛОХО: StockPrice знает обо ВСЕХ зависимых объектах
class StockPrice(var price: Double) {

    fun updatePrice(newPrice: Double) {
        price = newPrice

        // StockPrice привязан ко ВСЕМ потребителям
        chartWidget.redraw(price)
        portfolioTable.recalculate(price)
        notificationWidget.check(price)
        analyticsModule.track("price_change", price)
        pushService.notifySubscribers(price)
        // Каждый новый потребитель = изменение StockPrice
    }
}
```

**Три проблемы:**
1. **Tight coupling** --- StockPrice знает обо всех потребителях
2. **Нарушение Open/Closed** --- добавление потребителя = изменение StockPrice
3. **Невозможность тестирования** --- нельзя протестировать StockPrice без всех зависимостей

---

## Классический Observer: Subject/Observer

```
+---------------------------------------------------------+
|                      OBSERVER                           |
+---------------------------------------------------------+
|   Subject (interface)          Observer (interface)     |
|   +-- attach(observer)         +-- update(state)        |
|   +-- detach(observer)                |                 |
|   +-- notify()                 +------+------+          |
|          |                ConcreteA    ConcreteB         |
|   ConcreteSubject         update()     update()         |
|   +-- state                                             |
|   +-- notify() {                                        |
|     observers.forEach { it.update(state) }              |
|   }                                                     |
+---------------------------------------------------------+
```

| Компонент | Роль | Без него |
|-----------|------|----------|
| **Subject** | Управляет подписками, уведомляет | Нет механизма подписки |
| **ConcreteSubject** | Хранит состояние, вызывает notify | Нет источника событий |
| **Observer** | Контракт с методом update() | Нет единого способа реагировать |
| **ConcreteObserver** | Конкретная реакция на событие | Нечему реагировать |

**Ключевой принцип:** Subject и Observer связаны только через интерфейс. Subject не знает конкретных типов подписчиков.

---

## Эволюция Observer в Kotlin

```
Callback (Java-style)
    |
    | Проблемы: callback hell, утечки памяти, ручная отписка
    v
Delegates.observable()
    |
    | Проблемы: одно свойство, синхронно, нет backpressure
    v
Flow / StateFlow / SharedFlow
    |
    | Проблемы: нужны корутины
    v
Compose State / MutableState
    |
    Для UI: автоматическая рекомпозиция
```

---

## Стадия 1: Callback-интерфейсы (Java-style)

```kotlin
// Классический Observer через callback interface
interface StockObserver {
    fun onPriceChanged(symbol: String, oldPrice: Double, newPrice: Double)
}

class StockTicker(private val symbol: String) {
    private val observers = mutableSetOf<StockObserver>()
    private var price: Double = 0.0

    fun addObserver(observer: StockObserver) {
        observers.add(observer)
    }

    fun removeObserver(observer: StockObserver) {
        observers.remove(observer)
    }

    fun updatePrice(newPrice: Double) {
        val oldPrice = price
        price = newPrice
        // Уведомляем всех подписчиков
        observers.forEach { it.onPriceChanged(symbol, oldPrice, newPrice) }
    }
}

// Конкретные observers
class ChartWidget : StockObserver {
    override fun onPriceChanged(symbol: String, oldPrice: Double, newPrice: Double) {
        println("Chart: $symbol $oldPrice -> $newPrice")
        // Перерисовать график
    }
}

class AlertService(private val threshold: Double) : StockObserver {
    override fun onPriceChanged(symbol: String, oldPrice: Double, newPrice: Double) {
        if (newPrice > threshold) {
            println("ALERT: $symbol exceeded $threshold!")
        }
    }
}

// Использование
val ticker = StockTicker("AAPL")
val chart = ChartWidget()
val alert = AlertService(150.0)

ticker.addObserver(chart)
ticker.addObserver(alert)
ticker.updatePrice(155.0)
// Chart: AAPL 0.0 -> 155.0
// ALERT: AAPL exceeded 150.0!

// КРИТИЧНО: не забыть отписаться!
ticker.removeObserver(chart)  // Иначе --- утечка памяти
```

### Lambda-style callbacks (Kotlin-улучшение)

```kotlin
// Вместо interface --- лямбда
class StockTicker(private val symbol: String) {
    private val listeners = mutableSetOf<(String, Double, Double) -> Unit>()
    private var price: Double = 0.0

    fun onPriceChanged(listener: (String, Double, Double) -> Unit): () -> Unit {
        listeners.add(listener)
        // Возвращаем функцию отписки
        return { listeners.remove(listener) }
    }

    fun updatePrice(newPrice: Double) {
        val oldPrice = price
        price = newPrice
        listeners.forEach { it(symbol, oldPrice, newPrice) }
    }
}

// Использование --- компактнее
val ticker = StockTicker("AAPL")

val unsubscribe = ticker.onPriceChanged { symbol, old, new ->
    println("$symbol: $old -> $new")
}

ticker.updatePrice(155.0)
unsubscribe()  // Отписка
```

**Проблемы callback-подхода:**
- Memory leaks --- забытая подписка держит объект в памяти
- Callback hell --- вложенные callbacks при цепочке операций
- Threading --- callbacks вызываются в потоке уведомителя
- Нет backpressure --- медленный observer не тормозит быстрый subject

---

## Стадия 2: `Delegates.observable()` --- наблюдение за свойством

```kotlin
import kotlin.properties.Delegates

class UserProfile {
    // observable --- вызывает лямбду ПОСЛЕ изменения значения
    var name: String by Delegates.observable("Unknown") { property, oldValue, newValue ->
        println("${property.name}: '$oldValue' -> '$newValue'")
        // Обновить UI, сохранить в БД, отправить аналитику...
    }

    // vetoable --- вызывает лямбду ПЕРЕД изменением, может отклонить
    var age: Int by Delegates.vetoable(0) { _, _, newValue ->
        newValue in 0..150  // Отклоняем невалидные значения
    }
}

val profile = UserProfile()
profile.name = "Alice"   // Выведет: name: 'Unknown' -> 'Alice'
profile.name = "Bob"     // Выведет: name: 'Alice' -> 'Bob'

profile.age = 25         // OK
profile.age = -5         // Отклонено! age остаётся 25
println(profile.age)     // 25
```

> [!info] Kotlin-нюанс
> `Delegates.observable()` --- Observer на уровне одного свойства. Это мини-паттерн, не требующий инфраструктуры Subject/Observer. Идеален для простых случаев: логирование изменений, валидация, обновление связанного свойства.

### Custom delegate для наблюдения

```kotlin
import kotlin.properties.ReadWriteProperty
import kotlin.reflect.KProperty

// Кастомный delegate --- observable с поддержкой нескольких listeners
class ObservableProperty<T>(
    private var value: T,
    private val listeners: MutableList<(T, T) -> Unit> = mutableListOf()
) : ReadWriteProperty<Any?, T> {

    fun addListener(listener: (old: T, new: T) -> Unit): () -> Unit {
        listeners.add(listener)
        return { listeners.remove(listener) }
    }

    override fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        val old = this.value
        this.value = value
        if (old != value) {
            listeners.forEach { it(old, value) }
        }
    }
}

// Использование
class Settings {
    private val _themeDelegate = ObservableProperty("light")
    var theme: String by _themeDelegate

    init {
        _themeDelegate.addListener { old, new ->
            println("Theme changed: $old -> $new")
            // Применить тему
        }
    }
}
```

**Ограничения `Delegates.observable()`:**
- Наблюдение за одним свойством (не за объектом в целом)
- Синхронное выполнение (блокирует setter)
- Нет lifecycle awareness
- Нет backpressure

---

## Стадия 3: `Flow` / `StateFlow` / `SharedFlow` --- реактивные потоки

### Cold Flow: ленивый поток данных

```kotlin
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.delay

// Cold Flow --- поток, который начинает emit при collect
fun stockPrices(symbol: String): Flow<Double> = flow {
    var price = 100.0
    while (true) {
        price += (-5..5).random()
        emit(price)               // Отправляем значение подписчику
        delay(1000)               // Каждую секунду
    }
}

// Подписка --- через collect в корутине
suspend fun main() {
    stockPrices("AAPL")
        .filter { it > 100 }             // Фильтруем
        .map { "%.2f".format(it) }        // Форматируем
        .take(10)                          // Берём первые 10
        .collect { price ->                // Подписываемся
            println("AAPL: $$price")
        }
}
```

**Cold vs Hot:**
- **Cold Flow** (flow {}) --- запускается заново для каждого collector. Как видео по запросу.
- **Hot Flow** (StateFlow, SharedFlow) --- существует независимо от collectors. Как прямой эфир.

### `StateFlow` --- Subject из Observer pattern

```kotlin
import kotlinx.coroutines.flow.*

// StateFlow --- Observable + текущее значение
class StockRepository {
    // MutableStateFlow --- Subject (источник данных)
    private val _price = MutableStateFlow(0.0)

    // StateFlow --- read-only для наблюдателей
    val price: StateFlow<Double> = _price.asStateFlow()

    fun updatePrice(newPrice: Double) {
        _price.value = newPrice  // Все collectors получат новое значение
    }
}
```

```
+---------------------------------------------------------------+
|                  StateFlow как Observer                        |
+---------------------------------------------------------------+
|                                                               |
|   MutableStateFlow    =    Subject (хранит state, notify)     |
|   .value = newVal     =    setState() + notifyAll()           |
|                                                               |
|   StateFlow           =    Read-only Subject (for observers)  |
|   .collect { }        =    Observer.update()                  |
|                                                               |
|   Автоматическая      =    Нет memory leaks                  |
|   отписка при cancel        (lifecycle-aware)                 |
|                                                               |
+---------------------------------------------------------------+
```

### Android ViewModel + StateFlow

```kotlin
// ViewModel --- Subject
class StockViewModel(
    private val repository: StockRepository
) : ViewModel() {

    // UI State --- StateFlow (hot, всегда имеет значение)
    private val _uiState = MutableStateFlow<StockUiState>(StockUiState.Loading)
    val uiState: StateFlow<StockUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            repository.price
                .map { price ->
                    StockUiState.Data(
                        price = price,
                        change = calculateChange(price),
                        trend = if (price > previousPrice) Trend.UP else Trend.DOWN
                    )
                }
                .catch { error ->
                    _uiState.value = StockUiState.Error(error.message ?: "Unknown error")
                }
                .collect { state ->
                    _uiState.value = state
                }
        }
    }
}

sealed class StockUiState {
    data object Loading : StockUiState()
    data class Data(val price: Double, val change: Double, val trend: Trend) : StockUiState()
    data class Error(val message: String) : StockUiState()
}

// Activity/Fragment --- Observer
class StockActivity : ComponentActivity() {
    private val viewModel: StockViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // collect в lifecycle-aware scope --- автоматическая отписка
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    when (state) {
                        is StockUiState.Loading -> showLoading()
                        is StockUiState.Data -> showData(state)
                        is StockUiState.Error -> showError(state.message)
                    }
                }
            }
        }
    }
}
```

> [!info] Kotlin-нюанс
> `repeatOnLifecycle(Lifecycle.State.STARTED)` решает проблему memory leaks Observer: подписка автоматически отменяется когда Activity уходит в background и возобновляется в foreground. Это то, чего не хватало callback-подходу.

### `SharedFlow` --- для событий (one-shot)

```kotlin
class EventBus {
    // SharedFlow --- для событий, которые не нужно "помнить"
    private val _events = MutableSharedFlow<AppEvent>(
        replay = 0,              // Не воспроизводить старые события
        extraBufferCapacity = 64 // Буфер для быстрых emit
    )
    val events: SharedFlow<AppEvent> = _events.asSharedFlow()

    suspend fun emit(event: AppEvent) {
        _events.emit(event)
    }
}

sealed class AppEvent {
    data class ShowSnackbar(val message: String) : AppEvent()
    data class NavigateTo(val route: String) : AppEvent()
    data object LogOut : AppEvent()
}

// Использование: несколько подписчиков получают одно событие
class MainViewModel(private val eventBus: EventBus) : ViewModel() {
    val events = eventBus.events  // Expose как SharedFlow

    fun onLogout() {
        viewModelScope.launch {
            eventBus.emit(AppEvent.LogOut)
        }
    }
}
```

### StateFlow vs SharedFlow: когда что

```
+---------------------------------------------------------------+
|              StateFlow           |   SharedFlow               |
+---------------------------------------------------------------+
|  Всегда имеет значение          |   Может не иметь значений  |
|  (.value доступен)              |   (нет .value)             |
|                                 |                            |
|  Хранит только последнее        |   Настраиваемый replay     |
|  значение                       |   (0, 1, N)               |
|                                 |                            |
|  Не emit дубликаты              |   Emit всё                |
|  (distinctUntilChanged)         |                            |
|                                 |                            |
|  Для STATE:                     |   Для EVENTS:              |
|  UI state, settings,            |   navigation, snackbar,    |
|  current data                   |   one-shot actions         |
+---------------------------------------------------------------+
```

---

## Стадия 4: Compose `State` (UI observation)

```kotlin
// Jetpack Compose --- Observer встроен в UI framework
@Composable
fun StockPriceCard(viewModel: StockViewModel) {
    // collectAsState() --- автоматическая подписка на StateFlow
    val uiState by viewModel.uiState.collectAsState()

    when (val state = uiState) {
        is StockUiState.Loading -> CircularProgressIndicator()
        is StockUiState.Data -> {
            Card(modifier = Modifier.padding(16.dp)) {
                Column {
                    Text(
                        text = "$${state.price}",
                        style = MaterialTheme.typography.headlineLarge
                    )
                    Text(
                        text = "${if (state.change >= 0) "+" else ""}${state.change}%",
                        color = if (state.change >= 0) Color.Green else Color.Red
                    )
                }
            }
        }
        is StockUiState.Error -> {
            Text(text = "Error: ${state.message}", color = Color.Red)
        }
    }
}

// MutableState --- локальный Observer внутри Composable
@Composable
fun Counter() {
    // remember + mutableStateOf = observable state
    var count by remember { mutableStateOf(0) }

    // При изменении count --- автоматическая рекомпозиция
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

> [!info] Kotlin-нюанс
> В Compose Observer-паттерн полностью скрыт от разработчика. Ты просто читаешь `state.value`, и Compose автоматически отслеживает зависимости и перерисовывает только затронутые участки. Это **snapshot system** --- продвинутая реализация Observer на уровне runtime.

---

## Callback -> Flow: миграция

### `callbackFlow` --- мост из callback-мира в Flow

```kotlin
import kotlinx.coroutines.channels.awaitClose
import kotlinx.coroutines.flow.callbackFlow

// Было: callback-based API
interface LocationCallback {
    fun onLocationUpdate(lat: Double, lon: Double)
    fun onError(error: Throwable)
}

class LocationManager {
    fun requestUpdates(callback: LocationCallback) { /* ... */ }
    fun removeUpdates(callback: LocationCallback) { /* ... */ }
}

// Стало: Flow-based API через callbackFlow
fun LocationManager.locationFlow(): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback {
        override fun onLocationUpdate(lat: Double, lon: Double) {
            // trySend --- неблокирующая отправка в канал
            trySend(Location(lat, lon))
        }

        override fun onError(error: Throwable) {
            close(error)  // Закрываем Flow с ошибкой
        }
    }

    requestUpdates(callback)

    // awaitClose вызывается когда collector отменяет подписку
    awaitClose {
        removeUpdates(callback)  // Cleanup! Нет утечек памяти
    }
}

// Использование --- reactive!
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        locationManager.locationFlow()
            .filter { it.accuracy < 50 }       // Только точные
            .distinctUntilChanged()             // Без дубликатов
            .debounce(1000)                     // Не чаще раза в секунду
            .collect { location ->
                updateMap(location)
            }
    }
}
```

### `suspendCancellableCoroutine` --- one-shot callback -> suspend

```kotlin
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException

// One-shot callback -> suspend function
suspend fun LocationManager.getLastLocation(): Location =
    suspendCancellableCoroutine { continuation ->
        getLastKnownLocation(
            onSuccess = { lat, lon ->
                continuation.resume(Location(lat, lon))
            },
            onError = { error ->
                continuation.resumeWithException(error)
            }
        )

        continuation.invokeOnCancellation {
            // Cleanup при отмене корутины
            cancelLocationRequest()
        }
    }

// Использование --- как обычная suspend-функция
val location = locationManager.getLastLocation()
```

### Android: LiveData -> StateFlow

```kotlin
// БЫЛО: LiveData (Android-specific)
class OldViewModel : ViewModel() {
    private val _data = MutableLiveData<String>()
    val data: LiveData<String> = _data

    fun load() {
        _data.value = "loaded"
    }
}

// СТАЛО: StateFlow (Kotlin-стандарт, мультиплатформенный)
class NewViewModel : ViewModel() {
    private val _data = MutableStateFlow("")
    val data: StateFlow<String> = _data.asStateFlow()

    fun load() {
        _data.value = "loaded"
    }
}

// Room: возвращает Flow вместо LiveData
@Dao
interface UserDao {
    // Каждое изменение таблицы --- новое значение в Flow
    @Query("SELECT * FROM users WHERE active = 1")
    fun getActiveUsers(): Flow<List<User>>
}

// ViewModel конвертирует cold Flow -> hot StateFlow
class UserViewModel(private val dao: UserDao) : ViewModel() {
    val users: StateFlow<List<User>> = dao.getActiveUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

---

## Когда что использовать

```
+---------------------------------------------------------------+
|  Сценарий                    |  Инструмент                    |
+---------------------------------------------------------------+
|  Простой 1-к-1 callback      |  Lambda: (T) -> Unit           |
|  (кнопка, dialog)           |                                |
+---------------------------------------------------------------+
|  Наблюдение за одним         |  Delegates.observable()        |
|  свойством                   |                                |
+---------------------------------------------------------------+
|  Поток данных (реактивный)   |  Flow (cold)                   |
|  Room queries, network       |                                |
+---------------------------------------------------------------+
|  UI State (текущее значение) |  StateFlow (hot)               |
|  ViewModel -> UI             |                                |
+---------------------------------------------------------------+
|  Events (one-shot)           |  SharedFlow (replay=0)         |
|  Navigation, snackbar        |  или Channel                   |
+---------------------------------------------------------------+
|  UI-наблюдение (Compose)     |  mutableStateOf / collectAsState|
+---------------------------------------------------------------+
|  Legacy callback -> Flow     |  callbackFlow {}               |
+---------------------------------------------------------------+
|  Legacy callback -> suspend  |  suspendCancellableCoroutine   |
+---------------------------------------------------------------+
```

---

## Anti-patterns

### 1. Memory leaks: забытая подписка

```kotlin
// ПЛОХО: подписка без отписки
class StockFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // Collect в lifecycleScope БЕЗ repeatOnLifecycle
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                // Продолжает обновлять UI даже когда fragment в background!
                updateUI(state)
            }
        }
    }
}

// ХОРОШО: lifecycle-aware подписка
class StockFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

### 2. Callback hell

```kotlin
// ПЛОХО: вложенные callbacks
fun loadUserData(userId: String) {
    fetchUser(userId) { user ->
        fetchOrders(user.id) { orders ->
            fetchRecommendations(user.id) { recs ->
                updateUI(user, orders, recs)
                // 3+ уровня вложенности --- ад
            }
        }
    }
}

// ХОРОШО: Flow + combine
fun loadUserData(userId: String): Flow<UserData> {
    return combine(
        fetchUserFlow(userId),
        fetchOrdersFlow(userId),
        fetchRecommendationsFlow(userId)
    ) { user, orders, recs ->
        UserData(user, orders, recs)
    }
}
```

### 3. Нарушение порядка событий

```kotlin
// ПЛОХО: observers обрабатываются в произвольном порядке
class EventBus {
    private val listeners = mutableSetOf<(Event) -> Unit>()

    fun emit(event: Event) {
        // Порядок Set не гарантирован!
        listeners.forEach { it(event) }
    }
}

// ХОРОШО: если порядок важен --- используй List
class OrderedEventBus {
    private val listeners = mutableListOf<Pair<Int, (Event) -> Unit>>()

    fun on(priority: Int = 0, listener: (Event) -> Unit) {
        listeners.add(priority to listener)
        listeners.sortByDescending { it.first }
    }

    fun emit(event: Event) {
        listeners.forEach { (_, listener) -> listener(event) }
    }
}
```

### 4. StateFlow emit в UI-потоке

```kotlin
// ПЛОХО: тяжёлая операция в Main thread при emit
private val _state = MutableStateFlow<List<Item>>(emptyList())

fun loadItems() {
    viewModelScope.launch {
        val items = repository.fetchAll()  // IO thread
        val sorted = items.sortedBy { it.name }  // Тяжёлая сортировка 10K items
        _state.value = sorted  // ОК, но map/filter в collect будет на Main
    }
}

// ХОРОШО: трансформации на background
val items: StateFlow<List<Item>> = repository.itemsFlow()
    .map { items -> items.sortedBy { it.name } }  // На IO dispatcher
    .flowOn(Dispatchers.Default)                    // Явный dispatcher
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())
```

---

## Real-world примеры

### Room + Flow: реактивные запросы к БД

```kotlin
@Dao
interface TaskDao {
    @Query("SELECT * FROM tasks ORDER BY created_at DESC")
    fun getAllTasks(): Flow<List<TaskEntity>>

    @Query("SELECT * FROM tasks WHERE completed = 0")
    fun getPendingTasks(): Flow<List<TaskEntity>>

    @Query("SELECT COUNT(*) FROM tasks WHERE completed = 0")
    fun getPendingCount(): Flow<Int>
}

// ViewModel автоматически обновляется при изменении таблицы
class TaskViewModel(private val dao: TaskDao) : ViewModel() {

    val tasks: StateFlow<List<Task>> = dao.getAllTasks()
        .map { entities -> entities.map { it.toDomain() } }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    val pendingBadge: StateFlow<Int> = dao.getPendingCount()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0)
}
```

### Click listeners -> callbackFlow (Android Views)

```kotlin
// Extension: View clicks как Flow
fun View.clicks(): Flow<Unit> = callbackFlow {
    setOnClickListener { trySend(Unit) }
    awaitClose { setOnClickListener(null) }
}

// Extension: EditText text changes как Flow
fun EditText.textChanges(): Flow<String> = callbackFlow {
    val watcher = object : TextWatcher {
        override fun beforeTextChanged(s: CharSequence?, start: Int, count: Int, after: Int) {}
        override fun onTextChanged(s: CharSequence?, start: Int, before: Int, count: Int) {
            trySend(s?.toString().orEmpty())
        }
        override fun afterTextChanged(s: Editable?) {}
    }
    addTextChangedListener(watcher)
    awaitClose { removeTextChangedListener(watcher) }
}

// Использование: debounce для поиска
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        searchEditText.textChanges()
            .debounce(300)                    // Ждём 300ms после остановки ввода
            .distinctUntilChanged()           // Игнорируем одинаковые запросы
            .filter { it.length >= 2 }        // Минимум 2 символа
            .flatMapLatest { query ->         // Отменяем предыдущий запрос
                repository.search(query)
            }
            .collect { results ->
                adapter.submitList(results)
            }
    }
}
```

### Multiplatform: StateFlow в KMP

```kotlin
// Shared module (commonMain)
class SharedViewModel {
    private val _counter = MutableStateFlow(0)
    val counter: StateFlow<Int> = _counter.asStateFlow()

    fun increment() {
        _counter.value++
    }
}

// Android --- collect как обычно
lifecycleScope.launch {
    viewModel.counter.collect { count ->
        textView.text = "Count: $count"
    }
}

// iOS (Swift) --- через wrapper
// StateFlow.collect --- suspend, нужен wrapper для Swift
class FlowWrapper<T>(private val flow: StateFlow<T>) {
    fun watch(block: (T) -> Unit): Closeable {
        val job = CoroutineScope(Dispatchers.Main).launch {
            flow.collect { block(it) }
        }
        return object : Closeable {
            override fun close() { job.cancel() }
        }
    }
}
```

---

## Подводные камни

### Pitfall 1: `stateIn` и `shareIn` --- когда начинать

```kotlin
// SharingStarted.Eagerly --- сразу при создании
// SharingStarted.Lazily --- при первом collector
// SharingStarted.WhileSubscribed(timeout) --- пока есть collectors + timeout

// Для UI: WhileSubscribed(5000) --- оптимальный выбор
// 5 секунд после последнего collector (rotation, navigation)
val data: StateFlow<Data> = repository.dataFlow()
    .stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = Data.empty()
    )
```

### Pitfall 2: StateFlow не emit дубликаты

```kotlin
val _state = MutableStateFlow(listOf("a", "b"))

_state.value = listOf("a", "b")  // НЕ будет emit! equals() == true

// Если нужно принудительно обновить:
// Используй data class с counter или SharedFlow
```

### Pitfall 3: SharedFlow без подписчиков теряет события

```kotlin
val _events = MutableSharedFlow<Event>(replay = 0)

// Если emit вызван до collect --- событие потеряно!
viewModelScope.launch {
    _events.emit(Event.ShowError("Oops"))  // Потеряно если нет collectors
}

// Решение: replay = 1 или Channel для гарантированной доставки
val _events = MutableSharedFlow<Event>(replay = 1)
// или
val _events = Channel<Event>(Channel.BUFFERED)
```

---

## Проверь себя

> [!question]- Чем StateFlow отличается от SharedFlow?
> StateFlow всегда имеет текущее значение (.value), хранит только последнее, не emit дубликаты (distinctUntilChanged встроен). SharedFlow может не иметь значений, поддерживает настраиваемый replay (0, 1, N), emit все значения включая дубликаты. StateFlow для STATE (UI state, settings), SharedFlow для EVENTS (navigation, snackbar).

> [!question]- Как `callbackFlow` решает проблему memory leaks?
> `callbackFlow` использует `awaitClose {}` --- блок, который вызывается при отмене collect. В нём разработчик отписывается от callback. Когда collector отменяется (lifecycle, scope cancel), awaitClose автоматически вызывает cleanup. Это встроенный аналог removeObserver/unsubscribe.

> [!question]- Почему `repeatOnLifecycle` нужен при collect в Android?
> Без `repeatOnLifecycle` collect продолжается даже когда Activity в background: (1) обновляет невидимый UI (лишняя работа); (2) может вызвать crashes (обращение к detached views); (3) держит ресурсы. `repeatOnLifecycle(STARTED)` автоматически cancel/restart collect при переходах foreground/background.

> [!question]- Когда `Delegates.observable()` лучше Flow?
> Для простых случаев: наблюдение за одним свойством, синхронная реакция, нет необходимости в lifecycle awareness. Примеры: логирование изменений, валидация при setter, обновление зависимого свойства. Flow лучше когда: асинхронные данные, множество observers, нужен backpressure, lifecycle-aware.

> [!question]- Чем `suspendCancellableCoroutine` отличается от `callbackFlow`?
> `suspendCancellableCoroutine` --- для one-shot callback (один результат или ошибка). Возвращает `T`. Аналог: Promise/Future. `callbackFlow` --- для streaming callback (много значений). Возвращает `Flow<T>`. Аналог: Observable. Location один раз = suspendCancellableCoroutine. GPS updates непрерывно = callbackFlow.

---

## Ключевые карточки

Какие четыре стадии эволюции Observer в Kotlin?
?
1) Callback interfaces (Java-style) --- ручная подписка/отписка, memory leaks. 2) Delegates.observable() --- property-level observation, синхронное. 3) Flow/StateFlow/SharedFlow --- реактивные потоки, lifecycle-aware, backpressure. 4) Compose State --- UI observation, автоматическая рекомпозиция.

Что такое MutableStateFlow и как он реализует Observer?
?
MutableStateFlow = Subject из GoF Observer. Хранит текущее значение (.value), уведомляет всех collectors при изменении. StateFlow (read-only) экспонируется для observers. collect {} = Observer.update(). Отмена корутины = автоматическая отписка. Нет memory leaks.

Что делает callbackFlow и зачем нужен awaitClose?
?
callbackFlow конвертирует callback-based API в Flow. Внутри: регистрирует callback, trySend отправляет значения в Flow. awaitClose {} вызывается при отмене collect --- в нём разработчик отписывается от callback. Без awaitClose Flow завершится немедленно.

Чем hot Flow отличается от cold Flow?
?
Cold Flow (flow {}) --- запускается заново для каждого collector, как видео по запросу. Hot Flow (StateFlow, SharedFlow) --- существует независимо от collectors, как прямой эфир. StateFlow всегда имеет значение; SharedFlow может не иметь.

Когда StateFlow, когда SharedFlow, когда Channel?
?
StateFlow: UI state (текущее значение, distinctUntilChanged). SharedFlow: broadcast events для нескольких observers (replay настраиваемый). Channel: one-to-one events с гарантированной доставкой (не теряются без subscribers).

Что такое Delegates.observable() и его ограничения?
?
Property delegate, вызывающий лямбду после каждого изменения значения: `var name by Delegates.observable("") { _, old, new -> ... }`. Ограничения: одно свойство, синхронное, нет lifecycle awareness, нет backpressure. Для простых случаев (логирование, валидация).

Как repeatOnLifecycle решает проблему Observer в Android?
?
repeatOnLifecycle(Lifecycle.State.STARTED) автоматически cancel collect когда Activity/Fragment уходит в background и restart когда возвращается. Решает: memory leaks, crashes от обновления detached UI, лишнюю работу в background. Стандарт для collect StateFlow в Android.

Как Compose реализует Observer-паттерн?
?
mutableStateOf / collectAsState() --- Compose автоматически отслеживает чтение state в @Composable функциях. При изменении state --- рекомпозиция только затронутых участков. Snapshot system --- продвинутый Observer, полностью скрытый от разработчика. Нет явной подписки/отписки.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Фундамент | [[design-patterns-overview]] | Обзор всех GoF паттернов |
| Связанный паттерн | [[strategy-pattern]] | Strategy --- выбор алгоритма, Observer --- реакция на события |
| Связанный паттерн | [[state-pattern]] | State machine + Observer = reactive state management |
| Kotlin-инструменты | [[kotlin-flow]] | Глубокое погружение в Flow API |
| Android | [[android-state-management]] | LiveData, StateFlow, Compose State в Android |
| Android | [[android-mvvm-deep-dive]] | Observer через LiveData/StateFlow в MVVM |
| Android | [[android-mvi-deep-dive]] | Observer в MVI через единый StateFlow |
| Обзор | [[design-patterns-overview]] | Вернуться к карте раздела Design Patterns |

---

## Источники

- Gamma E. et al. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software* --- оригинальное описание Observer pattern в GoF каталоге
- Moskala M. (2024). *Kotlin Coroutines: Deep Dive* --- StateFlow, SharedFlow, callbackFlow, реактивные паттерны
- Nystrom R. (2014). *Game Programming Patterns*, Chapter "Observer" --- наглядное объяснение с примерами из геймдева
- [Android Developers: StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) --- официальный guide по hot flows в Android
- [Kotlin Documentation: callbackFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html) --- API reference для callbackFlow
- [Kotlin Documentation: Delegated properties](https://kotlinlang.org/docs/delegated-properties.html) --- Delegates.observable(), vetoable() и custom delegates
- [Callbacks and Kotlin Flows (Roman Elizarov)](https://elizarov.medium.com/callbacks-and-kotlin-flows-2b53aa2525cf) --- миграция callback -> Flow от lead разработчика корутин
- [Converting Callbacks to Coroutines and Flows (carrion.dev)](https://carrion.dev/en/posts/callback-to-flow-conversion/) --- практический guide по конвертации
- [SharedFlow and StateFlow (Kt. Academy)](https://kt.academy/article/cc-sharedflow-stateflow) --- глубокое сравнение hot flows
- [Observable and Vetoable delegates (Kt. Academy)](https://kt.academy/article/ak-observable-vetoable) --- property delegation для наблюдения
- [Wikipedia: Lapsed Listener Problem](https://en.wikipedia.org/wiki/Lapsed_listener_problem) --- memory leaks в Observer pattern

---

*Проверено: 2026-02-19*
