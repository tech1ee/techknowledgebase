---
title: "State: управление поведением через состояние"
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
  - "[[kotlin-oop]]"
  - "[[android-architecture-patterns]]"
  - "[[android-state-management]]"
---

# State: управление поведением через состояние

Заказ можно оплатить только из состояния «создан». Отменить — из «оплачен» или «создан», но не из «доставлен». В Java это заканчивается кашей из `if (status == "paid" && !isCancelled && !isShipped)`. В Kotlin `sealed class` + `when` решает задачу иначе: компилятор сам гарантирует, что все состояния обработаны, а невалидные переходы не скомпилируются. Это настолько мощный инструмент, что `sealed class UiState` стал де-факто стандартом в Android-разработке.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **State** | Внутреннее состояние объекта, определяющее его поведение |
| **State Machine (FSM)** | Finite State Machine — модель с конечным набором состояний и переходов |
| **Transition** | Переход из одного состояния в другое по событию |
| **Context** | Объект, поведение которого зависит от текущего состояния |
| **Sealed class** | Закрытая иерархия: все подтипы известны на compile-time |
| **Exhaustive when** | `when`-выражение, проверенное компилятором на полноту |
| **UiState** | Паттерн представления состояния экрана в Android (Loading/Content/Error) |

---

## Проблема: поведение зависит от состояния

### Заказ без State Machine

```kotlin
// ❌ Ад boolean-флагов
class Order(
    var status: String = "created",
    var isPaid: Boolean = false,
    var isShipped: Boolean = false,
    var isCancelled: Boolean = false,
    var isDelivered: Boolean = false
) {
    fun pay(amount: Double) {
        if (status == "created" && !isCancelled && !isPaid) {
            isPaid = true
            status = "paid"
            // А что если status = "created" но isPaid = true?
            // Невалидное состояние — и никто не ловит.
        }
    }

    fun ship(trackingId: String) {
        if (isPaid && !isShipped && !isCancelled) {
            isShipped = true
            status = "shipped"
        }
    }

    fun cancel(reason: String) {
        if (!isDelivered && !isCancelled) {
            if (isPaid) {
                // refund...
            }
            isCancelled = true
            status = "cancelled"
        }
    }

    // 5 boolean флагов = 2^5 = 32 комбинации
    // Из них валидных — 5-6. Остальные 26 — баги.
}
```

**Проблемы:**
1. **Невалидные комбинации:** `isPaid = true && isCancelled = true` — оплачен и отменён?
2. **Забытые проверки:** добавил новый флаг — нужно обновить все `if`
3. **Нет гарантий:** компилятор не поможет, ошибки только в runtime
4. **String-based status:** опечатка `"shiped"` — молчаливый баг

---

## Классический State Pattern (GoF)

### Структура

```
┌──────────────────────────────────────────────────────────────┐
│                         STATE                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│   Context                     State (interface)              │
│   ├── state: State            ├── handle(context)            │
│   └── request() {             │                              │
│         state.handle(this)    │                              │
│       }                       │                              │
│                                      ↑                       │
│                          ┌───────────┼───────────┐           │
│                          │           │           │           │
│                    ConcreteStateA ConcreteStateB ConcreteStateC│
│                    handle() {    handle() {    handle() {    │
│                      // behavior   // behavior   // behavior │
│                      // может      // может      // может   │
│                      // сменить    // сменить    // сменить  │
│                      // state      // state      // state    │
│                    }             }             }             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Participants

| Компонент | Роль | Пропустишь — сломаешь |
|-----------|------|----------------------|
| **State** | Интерфейс поведения, зависящего от состояния | Контракт для всех состояний |
| **ConcreteState** | Реализация поведения для конкретного состояния | Каждое состояние = свой класс |
| **Context** | Хранит текущее состояние, делегирует ему поведение | **Ключевой!** Без него состояния висят в воздухе |

### Java-стиль: State через интерфейс

```kotlin
// Классический GoF State — каждое состояние = класс
interface OrderState {
    fun pay(context: OrderContext, amount: Double): OrderState
    fun ship(context: OrderContext, trackingId: String): OrderState
    fun cancel(context: OrderContext, reason: String): OrderState
    fun deliver(context: OrderContext): OrderState
}

class CreatedState : OrderState {
    override fun pay(context: OrderContext, amount: Double): OrderState {
        context.processPayment(amount)
        return PaidState(amount)
    }

    override fun ship(context: OrderContext, trackingId: String): OrderState {
        throw IllegalStateException("Cannot ship: order not paid")
    }

    override fun cancel(context: OrderContext, reason: String): OrderState {
        return CancelledState(reason, refundAmount = 0.0)
    }

    override fun deliver(context: OrderContext): OrderState {
        throw IllegalStateException("Cannot deliver: order not shipped")
    }
}

class PaidState(val amount: Double) : OrderState {
    override fun pay(context: OrderContext, amount: Double): OrderState {
        throw IllegalStateException("Already paid")
    }

    override fun ship(context: OrderContext, trackingId: String): OrderState {
        context.createShipment(trackingId)
        return ShippedState(trackingId)
    }

    override fun cancel(context: OrderContext, reason: String): OrderState {
        context.processRefund(amount)
        return CancelledState(reason, refundAmount = amount)
    }

    override fun deliver(context: OrderContext): OrderState {
        throw IllegalStateException("Cannot deliver: order not shipped")
    }
}

// ... ещё ShippedState, DeliveredState, CancelledState
// Каждый с 4 методами. 5 состояний * 4 метода = 20 методов.
// Большинство — throw IllegalStateException.
```

**Проблема классического подхода:** слишком много boilerplate. Большинство методов в каждом состоянии кидают исключение — это шум, а не полезный код.

---

## Kotlin sealed class как State Machine

> [!info] Kotlin-нюанс
> `sealed class` — это **алгебраический тип данных (Sum Type)**. Компилятор знает все подтипы на этапе компиляции. `when` по sealed class не нуждается в `else` и **обязан** обработать все варианты.

### Определение состояний

```kotlin
sealed class OrderState {
    /** Заказ создан, ожидает оплаты */
    data object Created : OrderState()

    /** Оплачен на указанную сумму */
    data class Paid(val amount: Money) : OrderState()

    /** Отправлен, есть трек-номер */
    data class Shipped(
        val trackingId: String,
        val shippedAt: Instant = Instant.now()
    ) : OrderState()

    /** Доставлен получателю */
    data class Delivered(
        val deliveredAt: Instant = Instant.now()
    ) : OrderState()

    /** Отменён по причине */
    data class Cancelled(
        val reason: String,
        val refundAmount: Money = Money.ZERO
    ) : OrderState()
}
```

**Что это даёт:**
1. **Невалидные комбинации невозможны:** нельзя быть одновременно `Paid` и `Cancelled` — это разные типы
2. **Каждое состояние несёт свои данные:** `Paid` имеет `amount`, `Shipped` — `trackingId`, `Cancelled` — `reason`
3. **Нет boolean-флагов:** состояние определяется типом, не набором флагов
4. **Compile-time safety:** забыл обработать `Delivered` в `when` — не скомпилируется

### Exhaustive `when` — компилятор проверяет полноту

```kotlin
fun describeOrder(state: OrderState): String = when (state) {
    is OrderState.Created -> "Ожидает оплаты"
    is OrderState.Paid -> "Оплачен: ${state.amount}"
    is OrderState.Shipped -> "В пути: ${state.trackingId}"
    is OrderState.Delivered -> "Доставлен ${state.deliveredAt}"
    is OrderState.Cancelled -> "Отменён: ${state.reason}"
    // else НЕ НУЖЕН — компилятор знает все варианты
}

// Добавили новое состояние Processing:
// sealed class OrderState {
//     data class Processing(val estimatedTime: Duration) : OrderState()
//     ...
// }
//
// ❌ Ошибка компиляции:
// "'when' expression must be exhaustive,
//  add necessary 'is Processing' branch or 'else' branch instead"
//
// Компилятор ЗАСТАВИТ обновить ВСЕ when-выражения. Ни одно не забудешь.
```

### State transitions как функции

```kotlin
// Переходы — чистые функции: State + Event → новый State
fun OrderState.pay(amount: Money): OrderState = when (this) {
    is OrderState.Created -> OrderState.Paid(amount)
    is OrderState.Paid -> error("Заказ уже оплачен")
    is OrderState.Shipped -> error("Заказ уже отправлен")
    is OrderState.Delivered -> error("Заказ уже доставлен")
    is OrderState.Cancelled -> error("Заказ отменён")
}

fun OrderState.ship(trackingId: String): OrderState = when (this) {
    is OrderState.Paid -> OrderState.Shipped(trackingId)
    is OrderState.Created -> error("Нельзя отправить неоплаченный заказ")
    is OrderState.Shipped -> error("Заказ уже отправлен")
    is OrderState.Delivered -> error("Заказ уже доставлен")
    is OrderState.Cancelled -> error("Заказ отменён")
}

fun OrderState.cancel(reason: String): OrderState = when (this) {
    is OrderState.Created -> OrderState.Cancelled(reason)
    is OrderState.Paid -> OrderState.Cancelled(reason, refundAmount = amount)
    is OrderState.Shipped -> error("Нельзя отменить отправленный заказ")
    is OrderState.Delivered -> error("Нельзя отменить доставленный заказ")
    is OrderState.Cancelled -> error("Заказ уже отменён")
}
```

**Диаграмма переходов:**

```
                    ┌──── cancel("причина") ────┐
                    │                           │
                    ▼                           │
              ┌───────────┐              ┌──────┴────┐
              │ Cancelled │              │  Created   │
              │ (reason,  │              │            │
              │  refund)  │              └──────┬─────┘
              └───────────┘                     │
                    ▲                     pay(amount)
                    │                           │
              cancel("причина")                 ▼
                    │                    ┌──────┴─────┐
                    └────────────────────│    Paid    │
                                        │  (amount)  │
                                        └──────┬─────┘
                                               │
                                        ship(trackingId)
                                               │
                                               ▼
                                        ┌──────┴─────┐
                                        │  Shipped   │
                                        │ (tracking) │
                                        └──────┬─────┘
                                               │
                                          deliver()
                                               │
                                               ▼
                                        ┌──────┴─────┐
                                        │ Delivered  │
                                        │ (datetime) │
                                        └────────────┘
```

### Безопасные переходы через Result

Вместо `error()` (исключение) — возвращаем `Result`:

```kotlin
sealed class TransitionResult {
    data class Success(val newState: OrderState) : TransitionResult()
    data class Rejected(val reason: String) : TransitionResult()
}

fun OrderState.tryPay(amount: Money): TransitionResult = when (this) {
    is OrderState.Created -> TransitionResult.Success(OrderState.Paid(amount))
    else -> TransitionResult.Rejected(
        "Нельзя оплатить заказ в состоянии ${this::class.simpleName}"
    )
}

// Использование
when (val result = currentState.tryPay(Money(99.99))) {
    is TransitionResult.Success -> {
        currentState = result.newState
        notifyUser("Оплата прошла")
    }
    is TransitionResult.Rejected -> {
        showError(result.reason)
    }
}
```

---

## State vs Strategy: ключевое различие

Оба паттерна выглядят похоже (интерфейс + конкретные реализации + контекст), но решают разные задачи:

```
┌──────────────────────────────────────────────────────────────────┐
│              STATE vs STRATEGY: СРАВНЕНИЕ                         │
├────────────────┬──────────────────┬──────────────────────────────┤
│ Критерий       │ State            │ Strategy                     │
├────────────────┼──────────────────┼──────────────────────────────┤
│ Кто меняет     │ Объект сам       │ Клиент извне                 │
│                │ меняет состояние │ выбирает стратегию           │
├────────────────┼──────────────────┼──────────────────────────────┤
│ Переходы       │ Состояние знает  │ Стратегия не знает           │
│                │ про переходы     │ про другие стратегии         │
├────────────────┼──────────────────┼──────────────────────────────┤
│ Количество     │ Конечное, полное │ Любое, набор может расти     │
│ вариантов      │ (FSM)            │                              │
├────────────────┼──────────────────┼──────────────────────────────┤
│ Пример         │ Заказ: Created → │ Сортировка: QuickSort,       │
│                │ Paid → Shipped   │ MergeSort, HeapSort          │
├────────────────┼──────────────────┼──────────────────────────────┤
│ Kotlin-идиома  │ sealed class +   │ (T) -> R или                 │
│                │ when             │ fun interface + лямбда       │
├────────────────┼──────────────────┼──────────────────────────────┤
│ Замена в       │ Внутренняя       │ Внешняя                      │
│ runtime        │ (по событию)     │ (по выбору клиента)          │
└────────────────┴──────────────────┴──────────────────────────────┘
```

**Мнемоника:**
- **State** — светофор: сам переключается по таймеру (красный → жёлтый → зелёный)
- **Strategy** — навигатор: пользователь сам выбирает маршрут (быстрый / короткий / без платных дорог)

```kotlin
// STATE: объект сам меняет состояние по событию
order.pay(amount)  // Created → Paid (внутренний переход)

// STRATEGY: клиент извне выбирает алгоритм
val sorter = Sorter(strategy = QuickSort)  // клиент решает
sorter.sort(data)
```

---

## UiState: главный State-паттерн Android

`sealed interface UiState` — **самый распространённый** Kotlin-паттерн в мобильной разработке. Каждый экран имеет конечный набор состояний, и `when` гарантирует их полную обработку.

### Базовый UiState

```kotlin
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String, val cause: Throwable? = null) : UiState<Nothing>
}
```

> [!info] Kotlin-нюанс
> `sealed interface` (Kotlin 1.5+) вместо `sealed class` — подтипы могут реализовывать несколько sealed interface. `out T` — ковариантность: `UiState<Article>` можно присвоить `UiState<Any>`.

### ViewModel с UiState

```kotlin
class ArticleListViewModel(
    private val repository: ArticleRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<Article>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<Article>>> = _uiState.asStateFlow()

    init {
        loadArticles()
    }

    fun loadArticles() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val articles = repository.getArticles()
                _uiState.value = UiState.Success(articles)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(
                    message = e.localizedMessage ?: "Неизвестная ошибка",
                    cause = e
                )
            }
        }
    }

    fun retry() = loadArticles()
}
```

### UI: exhaustive when в Compose

```kotlin
@Composable
fun ArticleListScreen(viewModel: ArticleListViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is UiState.Loading -> {
            CircularProgressIndicator(
                modifier = Modifier.fillMaxSize().wrapContentSize()
            )
        }
        is UiState.Success -> {
            LazyColumn {
                items(state.data) { article ->
                    ArticleItem(article = article)
                }
            }
        }
        is UiState.Error -> {
            ErrorScreen(
                message = state.message,
                onRetry = viewModel::retry
            )
        }
        // Добавили UiState.Empty? Compose не скомпилируется,
        // пока не добавим ветку сюда.
    }
}
```

### Расширенный UiState для сложных экранов

```kotlin
// Экран профиля — несколько независимых секций
data class ProfileScreenState(
    val userState: UserState = UserState.Loading,
    val postsState: PostsState = PostsState.Loading,
    val isRefreshing: Boolean = false
) {
    sealed interface UserState {
        data object Loading : UserState
        data class Loaded(val user: User) : UserState
        data class Error(val message: String) : UserState
    }

    sealed interface PostsState {
        data object Loading : PostsState
        data class Loaded(val posts: List<Post>) : PostsState
        data object Empty : PostsState
        data class Error(val message: String) : PostsState
    }
}

// ViewModel
class ProfileViewModel(
    private val userRepo: UserRepository,
    private val postRepo: PostRepository
) : ViewModel() {

    private val _state = MutableStateFlow(ProfileScreenState())
    val state: StateFlow<ProfileScreenState> = _state.asStateFlow()

    fun loadProfile(userId: UserId) {
        viewModelScope.launch {
            // Загружаем параллельно
            launch {
                _state.update { it.copy(userState = ProfileScreenState.UserState.Loading) }
                try {
                    val user = userRepo.getUser(userId)
                    _state.update { it.copy(userState = ProfileScreenState.UserState.Loaded(user)) }
                } catch (e: Exception) {
                    _state.update { it.copy(userState = ProfileScreenState.UserState.Error(e.message ?: "")) }
                }
            }
            launch {
                _state.update { it.copy(postsState = ProfileScreenState.PostsState.Loading) }
                try {
                    val posts = postRepo.getUserPosts(userId)
                    _state.update {
                        it.copy(postsState = if (posts.isEmpty())
                            ProfileScreenState.PostsState.Empty
                        else
                            ProfileScreenState.PostsState.Loaded(posts)
                        )
                    }
                } catch (e: Exception) {
                    _state.update { it.copy(postsState = ProfileScreenState.PostsState.Error(e.message ?: "")) }
                }
            }
        }
    }
}
```

---

## Продвинутое: State Machine с событиями (MVI-bridge)

MVI (Model-View-Intent) — архитектура, где State Machine обрабатывает события и трансформирует состояние:

```kotlin
// Состояние экрана
data class CounterState(
    val count: Int = 0,
    val isLoading: Boolean = false
)

// Намерения (события) от UI
sealed interface CounterIntent {
    data object Increment : CounterIntent
    data object Decrement : CounterIntent
    data object Reset : CounterIntent
    data class SetValue(val value: Int) : CounterIntent
}

// ViewModel как State Machine
class CounterViewModel : ViewModel() {

    private val _state = MutableStateFlow(CounterState())
    val state: StateFlow<CounterState> = _state.asStateFlow()

    fun processIntent(intent: CounterIntent) {
        _state.update { currentState ->
            when (intent) {
                is CounterIntent.Increment -> currentState.copy(count = currentState.count + 1)
                is CounterIntent.Decrement -> currentState.copy(count = currentState.count - 1)
                is CounterIntent.Reset -> CounterState()
                is CounterIntent.SetValue -> currentState.copy(count = intent.value)
            }
        }
    }
}

// UI
@Composable
fun CounterScreen(viewModel: CounterViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Column {
        Text("Count: ${state.count}")
        Button(onClick = { viewModel.processIntent(CounterIntent.Increment) }) {
            Text("+1")
        }
        Button(onClick = { viewModel.processIntent(CounterIntent.Decrement) }) {
            Text("-1")
        }
    }
}
```

### Полноценная State Machine с валидацией переходов

```kotlin
// Обобщённая State Machine
class StateMachine<S : Any, E : Any>(
    initialState: S,
    private val transitions: Map<Pair<KClass<out S>, KClass<out E>>, (S, E) -> S>
) {
    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<S> = _state.asStateFlow()

    fun send(event: E) {
        val currentState = _state.value
        val key = currentState::class to event::class
        val transition = transitions[key]
            ?: error("No transition from ${currentState::class.simpleName} on ${event::class.simpleName}")

        _state.value = transition(currentState, event)
    }
}

// DSL для построения
class StateMachineBuilder<S : Any, E : Any> {
    val transitions = mutableMapOf<Pair<KClass<out S>, KClass<out E>>, (S, E) -> S>()

    inline fun <reified STATE : S, reified EVENT : E> on(
        noinline action: (STATE, EVENT) -> S
    ) {
        @Suppress("UNCHECKED_CAST")
        transitions[STATE::class to EVENT::class] = action as (S, E) -> S
    }

    fun build(initialState: S) = StateMachine(initialState, transitions)
}

inline fun <S : Any, E : Any> stateMachine(
    initialState: S,
    block: StateMachineBuilder<S, E>.() -> Unit
): StateMachine<S, E> = StateMachineBuilder<S, E>().apply(block).build(initialState)

// Использование
val orderMachine = stateMachine<OrderState, OrderEvent>(OrderState.Created) {
    on<OrderState.Created, OrderEvent.Pay> { _, event ->
        OrderState.Paid(event.amount)
    }
    on<OrderState.Paid, OrderEvent.Ship> { _, event ->
        OrderState.Shipped(event.trackingId)
    }
    on<OrderState.Shipped, OrderEvent.Deliver> { _, _ ->
        OrderState.Delivered(Instant.now())
    }
    on<OrderState.Created, OrderEvent.Cancel> { _, event ->
        OrderState.Cancelled(event.reason)
    }
    on<OrderState.Paid, OrderEvent.Cancel> { state, event ->
        OrderState.Cancelled(event.reason, refundAmount = state.amount)
    }
}
```

---

## `sealed interface` для расширяемых иерархий

```kotlin
// sealed class — все подтипы в одном файле
// sealed interface — подтипы могут реализовывать несколько sealed interface

sealed interface Loadable {
    data object Loading : Loadable
}

sealed interface Errorable {
    data class Error(val message: String) : Errorable
}

// Объединяем два аспекта
sealed interface ScreenState : Loadable, Errorable {
    data object Idle : ScreenState
    data class Content(val data: String) : ScreenState

    // Loading и Error наследуются через sealed interface
    // ВАЖНО: тут они должны быть объявлены заново
}

// Или проще: sealed interface как маркер
sealed interface Refreshable
sealed interface UiState {
    data object Loading : UiState, Refreshable
    data class Success(val data: List<Item>) : UiState, Refreshable
    data class Error(val message: String) : UiState
    // Error нельзя refresh — не реализует Refreshable
}

fun handleRefresh(state: UiState) {
    if (state is Refreshable) {
        // Можно обновить
    }
}
```

---

## Когда использовать

```
┌─────────────────────────────────────────────────────────────────┐
│                   КОГДА STATE PATTERN                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ✅ Используй когда:                                            │
│  • Объект имеет конечное число состояний                         │
│  • Поведение зависит от текущего состояния                       │
│  • Переходы между состояниями нужно контролировать              │
│  • UI состояния: Loading / Content / Error / Empty               │
│  • Бизнес-процессы: заказ, платёж, документ                      │
│  • Нужна compile-time гарантия обработки всех состояний          │
│                                                                 │
│  ❌ Не используй когда:                                          │
│  • Состояний 2-3 и логика тривиальная (хватит enum или boolean)  │
│  • Поведение не меняется от состояния к состоянию               │
│  • Нет чётких переходов — состояние «плавает»                   │
│  • Состояния не взаимоисключающие                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Anti-patterns

### 1. Boolean-флаги вместо состояний

```kotlin
// ❌ Плохо: набор флагов создаёт невалидные комбинации
data class ScreenState(
    val isLoading: Boolean = false,
    val data: List<Item>? = null,
    val error: String? = null
)
// isLoading = true && data != null && error != null — ???
// 2^3 = 8 комбинаций, большинство невалидны

// ✅ Хорошо: sealed class исключает невалидные состояния
sealed interface ScreenState {
    data object Loading : ScreenState
    data class Success(val data: List<Item>) : ScreenState
    data class Error(val message: String) : ScreenState
}
// Ровно 3 состояния. Каждое содержит только свои данные.
```

### 2. String-based состояния

```kotlin
// ❌ Плохо: состояние — строка
var status: String = "pending"

fun process() {
    if (status == "pendnig") { /* опечатка — никто не заметит */ }
    status = "processing"  // Какие ещё значения валидны? Неизвестно.
}

// ✅ Хорошо: sealed class или enum
sealed interface Status {
    data object Pending : Status
    data object Processing : Status
    data object Completed : Status
}
// Опечатка = ошибка компиляции. Все значения известны.
```

### 3. Mutable state без машины

```kotlin
// ❌ Плохо: состояние меняется из любого места
class OrderService {
    fun processOrder(order: Order) {
        order.status = "paid"       // прямая мутация
        // ... кто-то в другом потоке:
        order.status = "cancelled"  // гонка!
    }
}

// ✅ Хорошо: иммутабельные переходы
fun OrderState.pay(amount: Money): OrderState = when (this) {
    is OrderState.Created -> OrderState.Paid(amount)
    else -> error("Invalid transition")
}
// Новый объект вместо мутации. Thread-safe by design.
```

### 4. Гигантский when без декомпозиции

```kotlin
// ❌ Плохо: 200-строчный when
fun handleState(state: AppState) = when (state) {
    is AppState.Loading -> { /* 30 строк */ }
    is AppState.LoggedIn -> { /* 50 строк */ }
    is AppState.Error -> { /* 40 строк */ }
    // ...
}

// ✅ Хорошо: каждая ветка — отдельная функция
fun handleState(state: AppState) = when (state) {
    is AppState.Loading -> showLoading()
    is AppState.LoggedIn -> showContent(state)
    is AppState.Error -> showError(state)
}
```

---

## Проверь себя

> [!question]- Почему sealed class лучше boolean-флагов для состояний?
> Boolean-флаги создают невалидные комбинации: для n флагов — 2^n состояний, из которых большинство невалидны (isLoading = true && data != null). Sealed class определяет только валидные состояния, каждое со своими данными. Невалидная комбинация не может быть выражена в типе — ошибка невозможна.

> [!question]- В чём ключевое отличие State от Strategy?
> State: объект сам меняет своё поведение при переходе в другое состояние (внутренний переход). Strategy: клиент извне выбирает алгоритм. State знает о возможных переходах (Created → Paid). Strategy не знает о других стратегиях. Аналогия: State = светофор (переключается сам), Strategy = навигатор (пользователь выбирает маршрут).

> [!question]- Что гарантирует exhaustive when для sealed class?
> Компилятор проверяет, что все подтипы sealed class обработаны в when-выражении. Если добавить новый подтип — все when без обработки не скомпилируются. Это compile-time гарантия полноты: невозможно забыть обработать новое состояние. `else` не нужен и нежелателен — он скрывает новые состояния.

> [!question]- Когда использовать sealed class, а когда enum для состояний?
> Enum — когда все значения имеют одинаковую структуру (Color: RED, GREEN, BLUE — у каждого rgb). Sealed class — когда разные состояния несут разные данные (Success(data), Error(message), Loading — разные поля). Sealed class поддерживает вложенные иерархии и множественное наследование через sealed interface.

> [!question]- Почему UiState лучше делать sealed interface, а не sealed class (начиная с Kotlin 1.5)?
> `sealed interface` позволяет подтипу реализовывать несколько sealed interface (маркеры Refreshable, Cacheable). Sealed class ограничивает единственным наследованием. Также sealed interface не навязывает конструктор — data object Loading : UiState проще, чем data object Loading : UiState().

---

## Ключевые карточки

Что такое State Pattern и какую проблему решает?
?
Поведенческий паттерн: объект меняет поведение при смене внутреннего состояния. Решает проблему сложных условий (if/else по состоянию) и невалидных комбинаций boolean-флагов. В Kotlin реализуется через sealed class + when с compile-time проверкой полноты.

Чем sealed class лучше boolean-флагов для состояний?
?
n boolean-флагов = 2^n комбинаций, большинство невалидных. Sealed class определяет только валидные состояния, каждое со своими данными. `isLoading = true && error != null` невозможно выразить в sealed class: Loading и Error — разные типы. Компилятор гарантирует обработку всех состояний через exhaustive when.

Чем State отличается от Strategy?
?
State: объект сам меняет поведение по событию (внутренний переход, знает о переходах). Strategy: клиент извне выбирает алгоритм (не знает о других стратегиях). State = конечный автомат (FSM). Strategy = взаимозаменяемые алгоритмы. Kotlin: State = sealed class + when. Strategy = fun interface + лямбда.

Что такое UiState и почему это стандарт в Android?
?
`sealed interface UiState<out T>` с Loading/Success(data)/Error(message) — паттерн представления состояния экрана. Используется с StateFlow в ViewModel + collectAsStateWithLifecycle в Compose. Exhaustive when гарантирует обработку всех состояний. Добавление нового состояния (Empty) — ошибка компиляции во всех UI-обработчиках.

Как реализовать безопасные переходы состояний?
?
State transitions как чистые функции: `fun OrderState.pay(amount): OrderState = when(this) { Created -> Paid(amount), else -> error(...) }`. Exhaustive when проверяет все состояния. Для безопасности без исключений — возвращать sealed class Result (Success/Rejected) вместо throw.

Зачем sealed interface вместо sealed class?
?
sealed interface (Kotlin 1.5+) позволяет подтипу реализовывать несколько sealed interface (маркеры: Refreshable, Cacheable). Sealed class ограничен одиночным наследованием. Sealed interface не навязывает конструктор. data object Loading : UiState (без скобок) чище чем с sealed class.

Как State Pattern связан с MVI-архитектурой?
?
MVI = Model-View-Intent. State (Model) — sealed class/data class с данными экрана. Intent (Event) — sealed class с действиями пользователя. ViewModel как State Machine: `fun reduce(state: State, intent: Intent): State`. Однонаправленный поток: Intent → ViewModel → State → UI. State Pattern — ядро MVI.

Когда State Pattern — overkill?
?
Когда состояний 2-3 и логика тривиальная — хватит enum или boolean. Когда поведение не меняется от состояния. Когда нет чётких переходов. Когда состояния не взаимоисключающие (нужны комбинации — лучше data class с полями).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Сравнить | [[strategy-pattern]] | Strategy vs State: разница в направлении изменения |
| Обзор | [[design-patterns-overview]] | Место State среди 23 GoF-паттернов |
| Kotlin-deep | [[kotlin-oop]] | sealed class, data class, when — инструменты State |
| Android | [[android-architecture-patterns]] | MVI/MVVM + State в реальных приложениях |
| Android | [[android-mvi-deep-dive]] | State Machine в MVI (sealed class + when + reducer) |
| Android | [[android-state-management]] | StateFlow, LiveData, Compose state |

---

## Источники

### Первоисточники
- Gamma E., Helm R., Johnson R., Vlissides J. *Design Patterns: Elements of Reusable Object-Oriented Software* (1994) — оригинальное описание State (Chapter 5: Behavioral Patterns)
- Nystrom R. *Game Programming Patterns* (2014) — [Chapter: State](https://gameprogrammingpatterns.com/state.html) — лучшее объяснение State Machine с примерами из геймдева

### Kotlin-специфичные
- Moskala M. *Effective Kotlin* (2021) — sealed class, exhaustive when, immutable state
- [Kotlin Documentation: Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html) — официальная документация
- [ProAndroidDev: Kotlin Design Patterns — State Explained](https://proandroiddev.com/kotlin-design-patterns-state-explained-14f680e0178f) — практический разбор State в Kotlin
- [OneUptime: How to Use Sealed Classes for Type-Safe State](https://oneuptime.com/blog/post/2026-02-02-kotlin-sealed-classes-state/view) — type-safe state с sealed class

### State Machine реализации
- [Tinder/StateMachine](https://github.com/Tinder/StateMachine) — Kotlin DSL для finite state machine от Tinder
- [thoughtbot: Finite State Machines + Android + Kotlin](https://thoughtbot.com/blog/finite-state-machines-android-kotlin-good-times) — FSM в Android-приложении
- [sp4ghetticode: Finite State Machines in Kotlin](https://sp4ghetticode.medium.com/finite-state-machines-in-kotlin-part-1-57e68d54d93b) — пошаговая реализация DFA

### Android UiState и архитектура
- [Android Developers: State holders and UI state](https://developer.android.com/topic/architecture/ui-layer/stateholders) — официальный гайд Google по UI state
- [droidcon: Reactive State Management in Compose — MVI Architecture](https://www.droidcon.com/2025/04/29/reactive-state-management-in-compose-mvi-architecture/) — MVI + sealed class в Compose
- [zsmb.co: Designing and Working with Single View States](https://zsmb.co/designing-and-working-with-single-view-states-on-android/) — проектирование UiState
- [benigumo: MVI-style Best Practice using StateFlow and Channel](https://android.benigumo.com/20260207/mvi-combine-merge/) — современные практики MVI

### Визуальные справочники
- [Refactoring Guru: State](https://refactoring.guru/design-patterns/state) — визуальный справочник с UML
- [Refactoring Guru: State vs Strategy](https://refactoring.guru/design-patterns/state) — сравнение паттернов

---

*Проверено: 2026-02-19*
