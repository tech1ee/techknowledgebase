---
title: "MVI на Android: от Redux до Orbit — unidirectional data flow в деталях"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
status: published
cs-foundations: [state-machine, unidirectional-data-flow, reducer-pattern, event-sourcing, command-pattern]
tags:
  - topic/android
  - topic/architecture
  - type/deep-dive
  - level/advanced
related:
  - "[[android-architecture-patterns]]"
  - "[[android-architecture-evolution]]"
  - "[[android-mvvm-deep-dive]]"
  - "[[android-compose-architectures]]"
  - "[[android-clean-architecture]]"
  - "[[android-state-management]]"
  - "[[state-pattern]]"
  - "[[observer-pattern]]"
  - "[[strategy-pattern]]"
  - "[[solid-principles]]"
  - "[[functional-programming]]"
  - "[[concurrency-fundamentals]]"
  - "[[testing-fundamentals]]"
  - "[[error-handling]]"
  - "[[event-driven-architecture]]"
prerequisites:
  - "[[android-mvvm-deep-dive]]"
  - "[[android-architecture-patterns]]"
  - "[[kotlin-flow]]"
reading_time: 45
difficulty: 7
study_status: not_started
mastery: 0
---

# MVI на Android: от Redux до Orbit — unidirectional data flow в деталях

MVI --- это не библиотека и не checkbox в архитектурном чеклисте. Это **спектр** от "MVVM с `sealed class Intent`" до полноценного Redux с time-travel debugging и middleware. Когда разработчик говорит "я использую MVI", он может иметь в виду 30 строк ручного кода с `StateFlow` + `sealed class` --- или 500 строк с MVIKotlin Store, Executor, Reducer и Labels. Оба варианта --- MVI. Разница --- в степени формализации однонаправленного потока данных.

Этот файл --- полный разбор: от истоков паттерна через ручную реализацию до четырёх ведущих библиотек с кодом, сравнением и критериями выбора.

---

## Истоки MVI: от Elm до Android

### Хронология

```
2012    Elm Architecture (Evan Czaplicki)
        Model → Update → View
        Чистые функции, иммутабельность, нет side effects
        ↓
2014    Flux (Facebook)
        Dispatcher → Store → View → Action
        Первый mainstream UDF для JavaScript
        ↓
2015    Redux (Dan Abramov)
        Single Store, pure Reducers, middleware
        "Single source of truth" + time-travel debugging
        ↓
2015    Cycle.js / MVI (André Staltz)
        Intent → Model → View как потоки Observable
        "Unidirectional User Interface Architectures" (доклад)
        User as a function: user(view(model(intent(user))))
        ↓
2017    Android MVI (Hannes Dorfmann)
        "Reactive Apps with Model-View-Intent"
        Адаптация MVI для Android с RxJava
        ↓
2019    MVIKotlin (Arkadii Ivanov / Arkivanov)
        Строгий Redux на Kotlin Multiplatform
        ↓
2020    Orbit MVI (Babylon Health → open source)
        "MVI without the baggage" — MVVM-подобный API
        ↓
2021    Ballast (Casey Brooks / Copper Leaf)
        KMP-first, batteries included
        ↓
2022+   FlowMVI (Respawn)
        Coroutines-first, plugin system
```

### Elm Architecture (2012)

Evan Czaplicki создал Elm --- чисто функциональный язык для веб-интерфейсов. Model (иммутабельное состояние) → Update (чистая функция `(Model, Msg) → Model`) → View (`Model → Html`). Никаких side effects в Update --- побочные эффекты описываются как команды (Cmd), которые runtime выполняет за пределами чистого кода. Фундаментальная идея, которая через Redux дошла до Android.

### Redux (2015)

Dan Abramov адаптировал идеи Elm для JavaScript: **Single Store** (одно дерево состояния), **Reducer** (`(State, Action) → State`), **Middleware** (перехват Action до Reducer), **time-travel debugging**. Ключевой принцип: **State is read-only. The only way to change state is to dispatch an Action.**

### Cycle.js / MVI (André Staltz, 2015)

Staltz пошёл дальше: вся архитектура --- потоки Observable. **Intent** конвертирует события в потоки действий, **Model** трансформирует действия в потоки состояния, **View** рендерит состояние. Его доклад "Unidirectional User Interface Architectures" систематизировал Flux, Redux, Elm и MVI как семейство UDF-архитектур. Именно Staltz ввёл термин **Model-View-Intent**.

### Hannes Dorfmann и Android MVI (2017)

Dorfmann адаптировал MVI для Android (серия "Reactive Apps with Model-View-Intent", RxJava) и показал, как UDF решает три проблемы MVVM: (1) State update из разных мест → единственная точка обновления, (2) race conditions → Intent сериализуются, (3) сложность отладки → каждое изменение прослеживается до конкретного Intent.

---

## MVI: концептуальный фундамент

### Цикл данных

```
┌─────────────────────────────────────────────────────────────────┐
│                         MVI ЦИКЛ                                │
│                                                                 │
│         ┌──────────────────────────────────────────┐           │
│         │                                          │           │
│         ▼                                          │           │
│   ┌───────────┐    ┌───────────┐    ┌───────────┐ │           │
│   │   VIEW    │───▶│  INTENT   │───▶│  REDUCER  │ │           │
│   │           │    │ (Action)  │    │ (pure fn) │ │           │
│   └───────────┘    └───────────┘    └─────┬─────┘ │           │
│         ▲                                 │       │           │
│         │                                 ▼       │           │
│         │                          ┌───────────┐  │           │
│         │                          │   STATE   │──┘           │
│         │                          │(immutable)│              │
│         │                          └─────┬─────┘              │
│         │                                │                    │
│         └────────────────────────────────┘                    │
│                                                                │
│   View ──Intent──▶ Reducer ──State──▶ View (однонаправленный)  │
│                        │                                       │
│                        ▼                                       │
│                  ┌───────────┐                                 │
│                  │  EFFECTS  │  (навигация, toast, analytics)  │
│                  │(one-time) │                                 │
│                  └───────────┘                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Reducer как pure function

Центр MVI --- **Reducer**: чистая функция без побочных эффектов.

```kotlin
// Reducer: (State, Intent) -> State
// Чистая функция: одинаковый вход → одинаковый выход
// Нет IO, нет сети, нет базы данных
fun reduce(state: ScreenState, intent: ScreenIntent): ScreenState =
    when (intent) {
        is ScreenIntent.LoadStarted -> state.copy(isLoading = true)
        is ScreenIntent.DataLoaded -> state.copy(
            isLoading = false,
            items = intent.items
        )
        is ScreenIntent.ErrorOccurred -> state.copy(
            isLoading = false,
            error = intent.message
        )
    }
```

Почему это важно:
- **Предсказуемость** --- одинаковый State + Intent всегда даёт одинаковый результат
- **Тестируемость** --- не нужны моки, просто `assertEquals`
- **Отладка** --- можно записать последовательность Intent и воспроизвести баг
- **Time-travel** --- можно "отмотать" State назад, применяя Intent в обратном порядке

### Side Effects: что не помещается в State

Не всё --- State. Навигация, Toast, аналитика --- это **одноразовые события**, которые нельзя хранить в State (иначе повторный рендер покажет Toast дважды). MVI-библиотеки решают это по-разному --- подробнее в разделе "State vs Effect".

### Сравнение с MVVM

| Аспект | MVVM | MVI |
|--------|------|-----|
| **Точки входа** | Много методов ViewModel | Один `onIntent()` / `store.accept()` |
| **State update** | `_state.update{}` из разных мест | Единственный Reducer |
| **Намерения** | Implicit (вызов метода) | Explicit (`sealed class Intent`) |
| **Побочные эффекты** | `Channel`/`SharedFlow` (ad hoc) | Формализованные Effect/Label/Event |
| **Тестирование** | Мокаем зависимости | Тестируем Reducer как pure function |
| **Отладка** | Breakpoint в методе | Лог Intent → State transitions |
| **Boilerplate** | Минимальный | Больше (sealed class для каждого Intent) |
| **Кривая обучения** | Пологая | Крутая для строгого MVI |
| **Time-travel** | Невозможен | Возможен (MVIKotlin, FlowMVI) |

---

## Manual MVI: ручная реализация

### Минимальный MVI: sealed Intent + StateFlow

Самый простой MVI --- это MVVM с явными Intent. 30-40 строк, нулевые зависимости:

```kotlin
// ─── Contract ───
sealed interface CounterIntent {
    data object Increment : CounterIntent
    data object Decrement : CounterIntent
    data class SetValue(val value: Int) : CounterIntent
}

data class CounterState(
    val count: Int = 0,
    val isLoading: Boolean = false
)

// ─── ViewModel ───
class CounterViewModel : ViewModel() {

    private val _state = MutableStateFlow(CounterState())
    val state: StateFlow<CounterState> = _state.asStateFlow()

    fun onIntent(intent: CounterIntent) {
        // Reducer: чистая трансформация State
        _state.update { currentState ->
            when (intent) {
                is CounterIntent.Increment -> currentState.copy(count = currentState.count + 1)
                is CounterIntent.Decrement -> currentState.copy(count = currentState.count - 1)
                is CounterIntent.SetValue -> currentState.copy(count = intent.value)
            }
        }
    }
}

// ─── Compose UI ───
@Composable
fun CounterScreen(viewModel: CounterViewModel = viewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text("Count: ${state.count}", style = MaterialTheme.typography.headlineMedium)
        Row {
            Button(onClick = { viewModel.onIntent(CounterIntent.Decrement) }) { Text("-") }
            Spacer(modifier = Modifier.width(16.dp))
            Button(onClick = { viewModel.onIntent(CounterIntent.Increment) }) { Text("+") }
        }
    }
}
```

Это уже MVI: явные Intent, единая точка обновления State, однонаправленный поток. Но нет Side Effects и нет async.

### Расширенный MVI: + Side Effects

Добавляем `Channel` для одноразовых событий и async-обработку Intent:

```kotlin
// ─── Contract ───
sealed interface UsersIntent {
    data object Load : UsersIntent
    data class Search(val query: String) : UsersIntent
    data class Delete(val userId: Long) : UsersIntent
}

data class UsersState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val searchQuery: String = "",
    val error: String? = null
)

sealed interface UsersEffect {
    data class ShowToast(val message: String) : UsersEffect
    data class NavigateToDetail(val userId: Long) : UsersEffect
}

// ─── ViewModel ───
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UsersState())
    val state: StateFlow<UsersState> = _state.asStateFlow()

    private val _effects = Channel<UsersEffect>(Channel.BUFFERED)
    val effects: Flow<UsersEffect> = _effects.receiveAsFlow()

    fun onIntent(intent: UsersIntent) {
        when (intent) {
            is UsersIntent.Load -> load()
            is UsersIntent.Search -> search(intent.query)
            is UsersIntent.Delete -> delete(intent.userId)
        }
    }

    private fun load() {
        viewModelScope.launch {
            reduce { it.copy(isLoading = true, error = null) }
            repository.getUsers()
                .onSuccess { users ->
                    reduce { it.copy(isLoading = false, users = users) }
                }
                .onFailure { e ->
                    reduce { it.copy(isLoading = false, error = e.message) }
                    _effects.send(UsersEffect.ShowToast("Ошибка загрузки"))
                }
        }
    }

    private fun search(query: String) {
        reduce { it.copy(searchQuery = query) }
        // debounce + filter...
    }

    private fun delete(userId: Long) {
        viewModelScope.launch {
            repository.deleteUser(userId)
            _effects.send(UsersEffect.ShowToast("Пользователь удалён"))
            load() // перезагрузить список
        }
    }

    private fun reduce(reducer: (UsersState) -> UsersState) {
        _state.update(reducer)
    }
}
```

### Полный MVI: + Middleware Pipeline

Для сложных сценариев --- middleware, который перехватывает Intent до обработки:

```kotlin
// ─── Middleware ───
fun interface Middleware<I, S> {
    suspend fun process(intent: I, state: S, next: suspend (I) -> Unit)
}

// ─── ViewModel с Middleware pipeline ───
abstract class MviViewModel<I, S, E>(
    initialState: S,
    private val middlewares: List<Middleware<I, S>> = emptyList()
) : ViewModel() {

    private val _state = MutableStateFlow(initialState)
    val state: StateFlow<S> = _state.asStateFlow()

    private val _effects = Channel<E>(Channel.BUFFERED)
    val effects: Flow<E> = _effects.receiveAsFlow()

    fun onIntent(intent: I) {
        viewModelScope.launch {
            // Цепочка: каждый middleware вызывает next() для передачи дальше
            val chain = middlewares.foldRight<Middleware<I, S>, suspend (I) -> Unit>(
                { processedIntent -> handleIntent(processedIntent) }
            ) { middleware, next ->
                { i -> middleware.process(i, _state.value, next) }
            }
            chain(intent)
        }
    }

    protected abstract suspend fun handleIntent(intent: I)
    protected fun reduce(reducer: (S) -> S) { _state.update(reducer) }
    protected suspend fun postEffect(effect: E) { _effects.send(effect) }
}

// Использование:
val logging = Middleware<MyIntent, MyState> { intent, state, next ->
    println("Intent: $intent | State: $state")
    next(intent)
}
val analytics = Middleware<MyIntent, MyState> { intent, _, next ->
    analytics.track("intent", mapOf("type" to intent::class.simpleName))
    next(intent)
}
// val vm = MyViewModel(initialState, listOf(logging, analytics))
```

### Когда ручной MVI достаточен

| Критерий | Ручной MVI | Библиотека |
|----------|-----------|------------|
| Простой экран (1-3 Intent) | Достаточно | Overkill |
| 5-10 Intent, async, effects | Можно, но растёт | Стоит рассмотреть |
| 10+ экранов, команда 3+ человек | Дублирование boilerplate | Рекомендуется |
| Time-travel debugging нужен | Невозможно | MVIKotlin, FlowMVI |
| KMP shared logic | Много ручной работы | MVIKotlin, Ballast, FlowMVI |
| Тестирование через DSL | Нет | Orbit, MVIKotlin |

---

## MVI библиотеки: детальный обзор

### 5.1 Orbit MVI

**Философия:** "MVI without the baggage" --- знакомый MVVM-подобный API с формализованным однонаправленным потоком.

**GitHub:** [orbit-mvi/orbit-mvi](https://github.com/orbit-mvi/orbit-mvi)
**Текущая версия:** 9.x (2025)
**KMP:** Да (Android, iOS, Desktop, Web)

#### Архитектура

```
ContainerHost (ViewModel)
  └── Container
        ├── intent { }  ──▶  reduce { state.copy(...) }     ──▶ stateFlow ──▶ UI
        └── intent { }  ──▶  postSideEffect(...)             ──▶ sideEffectFlow ──▶ UI
```

Три ключевых компонента:
- **ContainerHost** --- интерфейс, который реализует ViewModel (или любой класс)
- **Container** --- управляет State и SideEffect, предоставляет `stateFlow` и `sideEffectFlow`
- **intent{}** --- DSL-блок для бизнес-логики: внутри доступны `reduce{}` и `postSideEffect{}`

#### Полная реализация экрана

```kotlin
// ─── Contract ───
data class ProductListState(
    val products: List<Product> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val searchQuery: String = "",
    val selectedCategory: Category? = null
)

sealed interface ProductListSideEffect {
    data class ShowToast(val message: String) : ProductListSideEffect
    data class NavigateToDetail(val productId: Long) : ProductListSideEffect
    data object NavigateToCart : ProductListSideEffect
}

// ─── ViewModel ───
class ProductListViewModel(
    private val repository: ProductRepository,
    private val cartService: CartService,
    private val analytics: Analytics
) : ContainerHost<ProductListState, ProductListSideEffect>, ViewModel() {

    override val container = container<ProductListState, ProductListSideEffect>(
        initialState = ProductListState()
    ) {
        // onCreate — вызывается один раз при создании Container
        loadProducts()
    }

    fun loadProducts() = intent {
        reduce { state.copy(isLoading = true, error = null) }

        val result = repository.getProducts(state.searchQuery, state.selectedCategory)

        result.fold(
            onSuccess = { products ->
                reduce { state.copy(isLoading = false, products = products) }
            },
            onFailure = { error ->
                reduce { state.copy(isLoading = false, error = error.message) }
                postSideEffect(ProductListSideEffect.ShowToast("Ошибка: ${error.message}"))
            }
        )
    }

    fun onSearch(query: String) = intent {
        reduce { state.copy(searchQuery = query) }
        loadProducts() // перезагрузить с новым запросом
    }

    fun onCategorySelected(category: Category?) = intent {
        reduce { state.copy(selectedCategory = category) }
        loadProducts()
    }

    fun onProductClick(productId: Long) = intent {
        analytics.track("product_click", mapOf("id" to productId))
        postSideEffect(ProductListSideEffect.NavigateToDetail(productId))
    }

    fun onAddToCart(product: Product) = intent {
        cartService.add(product)
        postSideEffect(ProductListSideEffect.ShowToast("${product.name} добавлен в корзину"))
    }
}

// ─── Compose UI ───
@Composable
fun ProductListScreen(viewModel: ProductListViewModel = viewModel()) {
    val state by viewModel.container.stateFlow.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.container.sideEffectFlow.collect { effect ->
            when (effect) {
                is ProductListSideEffect.ShowToast -> { /* Snackbar */ }
                is ProductListSideEffect.NavigateToDetail -> { /* navigate */ }
                is ProductListSideEffect.NavigateToCart -> { /* navigate */ }
            }
        }
    }

    ProductListContent(state = state, onIntent = { /* dispatch intents */ })
}
```

#### Тестирование с Orbit Test

```kotlin
@Test
fun `loadProducts updates state`() = runTest {
    val vm = ProductListViewModel(FakeRepo(products), FakeCartService(), FakeAnalytics())
    vm.test(this) {
        expectInitialState()
        vm.loadProducts()
        expectState { copy(isLoading = true, error = null) }
        expectState { copy(isLoading = false, products = products) }
    }
}

@Test
fun `onProductClick emits navigation`() = runTest {
    val vm = ProductListViewModel(FakeRepo(), FakeCartService(), FakeAnalytics())
    vm.test(this) {
        expectInitialState()
        vm.onProductClick(42L)
        expectSideEffect(ProductListSideEffect.NavigateToDetail(42L))
    }
}
```

#### Плюсы и минусы

**Плюсы:**
- Минимальный boilerplate --- ближе всего к "голому" MVVM
- Знакомый API для MVVM-разработчиков --- миграция за часы
- Отличная интеграция с Compose и Lifecycle
- 130+ публичных проектов используют Orbit
- Простой DSL: `intent{}`, `reduce{}`, `postSideEffect{}`
- Хорошая тестовая инфраструктура

**Минусы:**
- Менее строгий, чем классический MVI --- нет гарантий на уровне типов
- Нет time-travel debugging
- Нет IDE-плагина и remote debugger
- Менее активная разработка в 2025-2026
- Документация не покрывает сложные сценарии

---

### 5.2 MVIKotlin (Arkivanov)

**Философия:** строгий Redux-like подход. Каждый компонент имеет чёткую ответственность. Максимальная предсказуемость за счёт boilerplate.

**GitHub:** [arkivanov/MVIKotlin](https://github.com/arkivanov/MVIKotlin)
**Текущая версия:** 4.x (2025)
**KMP:** Да (все таргеты Kotlin)

#### Архитектура

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         MVIKotlin Store                                  │
│                                                                          │
│  ┌────────────┐                                                         │
│  │Bootstrapper│──Action──┐                                              │
│  │(init logic)│          │                                              │
│  └────────────┘          │                                              │
│                          ▼                                              │
│  Intent ────────▶ ┌────────────┐ ──Message──▶ ┌─────────┐ ──▶ State    │
│  (from UI)        │  Executor  │              │ Reducer │    (to UI)   │
│                   │(async work)│              │(pure fn)│              │
│                   └────────────┘              └─────────┘              │
│                          │                                              │
│                          │                                              │
│                       Label ──────────────────────────▶ (one-time)     │
│                   (side effects)                                        │
│                                                                          │
│  Bootstrapper: начальные действия при создании Store                    │
│  Executor:     бизнес-логика, async, доступ к State                    │
│  Message:      внутреннее событие от Executor к Reducer                │
│  Reducer:      (State, Message) → State (pure function)                │
│  Label:        одноразовые события наружу (навигация, toast)           │
│  Intent:       входящие действия от UI                                 │
│  State:        текущее состояние, доступное UI                         │
└──────────────────────────────────────────────────────────────────────────┘
```

Шесть ключевых компонентов:
- **Store** --- контейнер бизнес-логики, принимает Intent, выдаёт State и Label
- **Bootstrapper** --- запускает начальные Action при инициализации Store
- **Executor** --- обрабатывает Intent и Action, выполняет async работу, отправляет Message и Label
- **Message** --- внутреннее событие от Executor к Reducer (не виден снаружи)
- **Reducer** --- чистая функция `(State, Message) -> State`
- **Label** --- одноразовые события наружу (аналог SideEffect в Orbit)

#### Полная реализация экрана

```kotlin
// ─── Store Interface ───
internal interface ProductListStore : Store<
    ProductListStore.Intent,
    ProductListStore.State,
    ProductListStore.Label
> {
    sealed interface Intent {
        data object Load : Intent
        data class Search(val query: String) : Intent
        data class SelectCategory(val category: Category?) : Intent
        data class ProductClicked(val productId: Long) : Intent
        data class AddToCart(val product: Product) : Intent
    }

    data class State(
        val products: List<Product> = emptyList(),
        val isLoading: Boolean = false,
        val error: String? = null,
        val searchQuery: String = "",
        val selectedCategory: Category? = null
    )

    sealed interface Label {
        data class NavigateToDetail(val productId: Long) : Label
        data class ShowToast(val message: String) : Label
    }
}

// ─── Store Factory ───
internal class ProductListStoreFactory(
    private val storeFactory: StoreFactory,
    private val repository: ProductRepository,
    private val cartService: CartService
) {
    fun create(): ProductListStore =
        object : ProductListStore,
            Store<ProductListStore.Intent, ProductListStore.State, ProductListStore.Label>
            by storeFactory.create(
                name = "ProductListStore",
                initialState = ProductListStore.State(),
                bootstrapper = BootstrapperImpl(),
                executorFactory = { ExecutorImpl() },
                reducer = ReducerImpl
            ) {}

    // ─── Bootstrapper ───
    private class BootstrapperImpl : CoroutineBootstrapper<Action>() {
        override fun invoke() {
            dispatch(Action.LoadInitial)
        }
    }

    // ─── Action (внутренний, от Bootstrapper к Executor) ───
    private sealed interface Action {
        data object LoadInitial : Action
    }

    // ─── Message (внутренний, от Executor к Reducer) ───
    private sealed interface Msg {
        data object Loading : Msg
        data class ProductsLoaded(val products: List<Product>) : Msg
        data class Error(val message: String) : Msg
        data class SearchChanged(val query: String) : Msg
        data class CategoryChanged(val category: Category?) : Msg
    }

    // ─── Executor ───
    private inner class ExecutorImpl : CoroutineExecutor<
        ProductListStore.Intent,
        Action,
        ProductListStore.State,
        Msg,
        ProductListStore.Label
    >() {
        override fun executeAction(action: Action) {
            when (action) {
                is Action.LoadInitial -> loadProducts()
            }
        }

        override fun executeIntent(intent: ProductListStore.Intent) {
            when (intent) {
                is ProductListStore.Intent.Load -> loadProducts()
                is ProductListStore.Intent.Search -> {
                    dispatch(Msg.SearchChanged(intent.query))
                    loadProducts()
                }
                is ProductListStore.Intent.SelectCategory -> {
                    dispatch(Msg.CategoryChanged(intent.category))
                    loadProducts()
                }
                is ProductListStore.Intent.ProductClicked -> {
                    publish(ProductListStore.Label.NavigateToDetail(intent.productId))
                }
                is ProductListStore.Intent.AddToCart -> {
                    scope.launch {
                        cartService.add(intent.product)
                        publish(ProductListStore.Label.ShowToast(
                            "${intent.product.name} добавлен"
                        ))
                    }
                }
            }
        }

        private fun loadProducts() {
            scope.launch {
                dispatch(Msg.Loading)
                val query = state().searchQuery
                val category = state().selectedCategory

                repository.getProducts(query, category)
                    .onSuccess { dispatch(Msg.ProductsLoaded(it)) }
                    .onFailure { dispatch(Msg.Error(it.message ?: "Неизвестная ошибка")) }
            }
        }
    }

    // ─── Reducer (чистая функция) ───
    private object ReducerImpl : Reducer<ProductListStore.State, Msg> {
        override fun ProductListStore.State.reduce(msg: Msg): ProductListStore.State =
            when (msg) {
                is Msg.Loading -> copy(isLoading = true, error = null)
                is Msg.ProductsLoaded -> copy(isLoading = false, products = msg.products)
                is Msg.Error -> copy(isLoading = false, error = msg.message)
                is Msg.SearchChanged -> copy(searchQuery = msg.query)
                is Msg.CategoryChanged -> copy(selectedCategory = msg.category)
            }
    }
}

// ─── Подключение к Compose ───
@Composable
fun ProductListScreen(store: ProductListStore) {
    val state by store.stateFlow.collectAsStateWithLifecycle()
    LaunchedEffect(store) {
        store.labels.collect { label -> /* навигация, toast */ }
    }
    ProductListContent(state = state, onIntent = store::accept)
}
```

#### Time-Travel Debugging

```kotlin
// Заменяем DefaultStoreFactory на TimeTravelStoreFactory:
val storeFactory = TimeTravelStoreFactory(fallback = DefaultStoreFactory())
// Все Store записывают историю: Intent → Message → State → Label
// Просмотр: IDEA plugin, Chrome DevTools extension, TimeTravelController API
```

#### Тестирование Reducer (pure function — без моков)

```kotlin
@Test
fun `reducer handles Loading`() {
    val newState = with(ReducerImpl) { ProductListStore.State().reduce(Msg.Loading) }
    assertEquals(true, newState.isLoading)
}

@Test
fun `reducer handles ProductsLoaded`() {
    val products = listOf(Product(1, "Phone"))
    val newState = with(ReducerImpl) { ProductListStore.State(isLoading = true).reduce(Msg.ProductsLoaded(products)) }
    assertEquals(products, newState.products)
    assertEquals(false, newState.isLoading)
}
```

#### Плюсы и минусы

**Плюсы:**
- Самый строгий MVI --- каждый компонент имеет одну ответственность
- Time-travel debugging из коробки (IDE + Chrome)
- Зрелая экосистема: Decompose (навигация), Essenty (lifecycle)
- Полный KMP на всех таргетах
- Проверен в enterprise и крупных проектах
- Исчерпывающие примеры и sample-приложения

**Минусы:**
- Больше всего boilerplate (Store + Executor + Reducer + Msg + Label + Action)
- Крутая кривая обучения: 6+ концепций для простого экрана
- Main-thread only ограничения
- Нет state persistence из коробки
- Не coroutines-first (поддерживает и Reaktive)

---

### 5.3 Ballast (Copper Leaf)

**Философия:** opinionated, batteries included. Всё нужное для приложения --- в одном фреймворке.

**GitHub:** [copper-leaf/ballast](https://github.com/copper-leaf/ballast)
**Текущая версия:** 4.x (2025)
**KMP:** Да (Android, iOS, Desktop, JS, WasmJS)

#### Архитектура

Ballast изначально проектировался для Compose Desktop, а не Android. Это делает его по-настоящему мультиплатформенным.

Три ключевых компонента:
- **InputHandler** --- обрабатывает Input (аналог Intent), может менять State, отправлять Event, запускать Side-Job
- **EventHandler** --- обрабатывает одноразовые события (навигация, toast) на стороне UI
- **InputStrategy** --- стратегия обработки входящих Input (LIFO, FIFO, Parallel)

#### Полная реализация экрана

```kotlin
// ─── Contract ───
object ProductListContract {
    data class State(
        val products: List<Product> = emptyList(),
        val isLoading: Boolean = false,
        val error: String? = null,
        val searchQuery: String = ""
    )

    sealed interface Inputs {
        data object Load : Inputs
        data class Search(val query: String) : Inputs
        data class ProductClicked(val productId: Long) : Inputs
        data class AddToCart(val product: Product) : Inputs
    }

    sealed interface Events {
        data class NavigateToDetail(val productId: Long) : Events
        data class ShowToast(val message: String) : Events
    }
}

// ─── InputHandler ───
class ProductListInputHandler(
    private val repository: ProductRepository,
    private val cartService: CartService
) : InputHandler<
    ProductListContract.Inputs,
    ProductListContract.Events,
    ProductListContract.State
> {
    override suspend fun InputHandlerScope<
        ProductListContract.Inputs,
        ProductListContract.Events,
        ProductListContract.State
    >.handleInput(
        input: ProductListContract.Inputs
    ) = when (input) {
        is ProductListContract.Inputs.Load -> {
            updateState { it.copy(isLoading = true, error = null) }
            sideJob("loadProducts") {
                repository.getProducts(getCurrentState().searchQuery)
                    .onSuccess { products ->
                        updateState { it.copy(isLoading = false, products = products) }
                    }
                    .onFailure { e ->
                        updateState { it.copy(isLoading = false, error = e.message) }
                        postEvent(ProductListContract.Events.ShowToast("Ошибка загрузки"))
                    }
            }
        }
        is ProductListContract.Inputs.Search -> {
            updateState { it.copy(searchQuery = input.query) }
            postInput(ProductListContract.Inputs.Load)
        }
        is ProductListContract.Inputs.ProductClicked -> {
            postEvent(ProductListContract.Events.NavigateToDetail(input.productId))
        }
        is ProductListContract.Inputs.AddToCart -> {
            sideJob("addToCart") {
                cartService.add(input.product)
                postEvent(ProductListContract.Events.ShowToast(
                    "${input.product.name} добавлен"
                ))
            }
        }
    }
}

// ─── EventHandler (обработка one-time событий на стороне UI) ───
class ProductListEventHandler(
    private val navigator: Navigator
) : EventHandler<ProductListContract.Inputs, ProductListContract.Events, ProductListContract.State> {
    override suspend fun EventHandlerScope<
        ProductListContract.Inputs, ProductListContract.Events, ProductListContract.State
    >.handleEvent(event: ProductListContract.Events) = when (event) {
        is ProductListContract.Events.NavigateToDetail -> navigator.navigate("product/${event.productId}")
        is ProductListContract.Events.ShowToast -> { /* snackbar */ }
    }
}

// ─── ViewModel ───
class ProductListViewModel(
    coroutineScope: CoroutineScope,
    repository: ProductRepository,
    cartService: CartService
) : BasicViewModel<ProductListContract.Inputs, ProductListContract.Events, ProductListContract.State>(
    config = BallastViewModelConfiguration.Builder()
        .withViewModel(
            initialState = ProductListContract.State(),
            inputHandler = ProductListInputHandler(repository, cartService),
            name = "ProductList"
        )
        .apply {
            this += BallastDebuggerInterceptor(debuggerConnection) // remote debugging
            this += LoggingInterceptor()
        }
        .build(),
    eventHandler = ProductListEventHandler(navigator),
    coroutineScope = coroutineScope,
)
```

#### Input Strategies

Уникальная фича Ballast --- стратегия обработки Input:
- **LIFO** (default): новый Input отменяет текущий (идеально для поиска)
- **FIFO**: Input обрабатываются по очереди (отправка форм)
- **Parallel**: Input параллельно (независимые загрузки)

#### Встроенные модули

ballast-debugger (remote debugging), ballast-undo (undo/redo), ballast-navigation (KMP routing), ballast-repository (кэширование), ballast-firebase-analytics, ballast-saved-state.

#### Плюсы и минусы

**Плюсы:**
- Второй по количеству фич после FlowMVI
- Input Strategies --- уникальная система управления порядком обработки
- Встроенные undo/redo, навигация, кэширование
- Remote debugging
- Изначально KMP (не Android-first)
- Хорошая документация с примерами

**Минусы:**
- Opinionated --- сложно отклониться от заданных паттернов
- Смешение стилей API (Builder + DSL + лямбды + фабрики)
- Меньшее комьюнити по сравнению с Orbit и MVIKotlin
- Verbose типизация (три generic-параметра повсюду)

---

### 5.4 FlowMVI (Respawn)

**Философия:** coroutines-first, всё --- через plugin system. Максимальная гибкость и модульность.

**GitHub:** [respawn-app/FlowMVI](https://github.com/respawn-app/FlowMVI)
**Текущая версия:** 3.x (2025-2026)
**KMP:** Да (9+ таргетов)

#### Архитектура

FlowMVI построен вокруг **цепочки плагинов** (Chain of Responsibility). Каждый аспект --- обработка Intent, логирование, аналитика, восстановление после ошибок --- это отдельный Plugin.

```
Intent ──▶ [Logging] ──▶ [Analytics] ──▶ [Recover] ──▶ [Reduce] ──▶ State / Action
           Plugin 1      Plugin 2        Plugin 3      Plugin N
           (Chain of Responsibility — порядок установки определяет порядок выполнения)
```

#### Два стиля: MVI и MVVM+

```kotlin
// ─── MVI стиль: sealed interface для Intent ───
sealed interface CounterIntent : MVIIntent {
    data object Increment : CounterIntent
    data object Decrement : CounterIntent
}
sealed interface CounterState : MVIState {
    data object Loading : CounterState
    data class Content(val count: Int) : CounterState
}
sealed interface CounterAction : MVIAction {
    data class ShowToast(val message: String) : CounterAction
}

val counterStore = store(initial = CounterState.Loading) {
    configure { debuggable = BuildConfig.DEBUG; name = "Counter" }
    loggingPlugin()
    recover { e -> action(CounterAction.ShowToast("Ошибка: ${e.message}")); null }
    reduce { intent: CounterIntent ->
        when (intent) {
            is CounterIntent.Increment -> updateState<CounterState.Content, _> { copy(count = count + 1) }
            is CounterIntent.Decrement -> updateState<CounterState.Content, _> { copy(count = count - 1) }
        }
    }
}

// ─── MVVM+ стиль: лямбды вместо sealed class ───
class ProductViewModel(private val repository: ProductRepository) : ViewModel() {
    val store = store(initial = ProductState()) {
        configure { debuggable = true }
        reduceLambdas() // обязательный plugin для MVVM+ стиля
    }
    fun loadProducts() = store.intent {
        updateState { copy(isLoading = true) }
        val products = repository.getProducts()
        updateState { copy(isLoading = false, products = products) }
    }
}
```

#### Plugin System: ключевые плагины

```kotlin
val store = store(initial = MyState.Loading) {
    configure { debuggable = BuildConfig.DEBUG; name = "ProductList" }

    loggingPlugin()                                    // логирование
    recover { e -> updateState { MyState.Error(e.message) }; null }  // ошибки
    init { val data = repo.load(); updateState { MyState.Content(data) } }  // инит
    whileSubscribed { repo.observe().collect { updateState<MyState.Content, _> { copy(items = it) } } }
    savedState(saver = JsonSaver(), file = "product_list")  // persistence
    timeTravelPlugin()                                 // time-travel
    undoRedo(maxQueueSize = 20)                        // undo/redo
    manageJobs()                                       // job management по ключу

    reduce { intent ->  // обработка Intent
        when (intent) {
            is MyIntent.Load -> { /* ... */ }
            is MyIntent.Search -> { /* ... */ }
        }
    }
}
// Порядок plugins ВАЖЕН: они выполняются в порядке установки (Chain of Responsibility)
```

#### Плюсы и минусы

**Плюсы:**
- Наибольшее количество фич (76+ по сравнительному анализу)
- Plugin system --- добавляй что нужно, не тащи лишнее
- Coroutines-first --- нативная поддержка structured concurrency
- Минимальный boilerplate с MVVM+ стилем
- IDE plugin и remote debugger
- Отличная производительность (бенчмарки)
- Параллельная и последовательная обработка Intent

**Минусы:**
- Крутая кривая обучения (Plugin system = "чёрная магия")
- Требует глубокого понимания корутин
- Самая молодая из четырёх --- меньше production-примеров
- Нет RxJava-адаптеров (только coroutines)
- Стандартизация в команде сложнее из-за гибкости

---

### 5.5 Сравнительная таблица

| Критерий | Orbit MVI | MVIKotlin | Ballast | FlowMVI |
|----------|-----------|-----------|---------|---------|
| **API стиль** | MVVM-like DSL | Redux-like | Opinionated OOP | Plugin DSL |
| **KMP** | Да | Да (все таргеты) | Да (5+ таргетов) | Да (9+ таргетов) |
| **Boilerplate** | Очень мало | Много | Умеренный | Мало |
| **Кривая обучения** | Пологая | Крутая | Умеренная | Крутая |
| **Time-travel** | Нет | Да (IDE + Chrome) | Да (plugin) | Да (plugin) |
| **IDE plugin** | Нет | Да | Нет | Да |
| **Тестовые утилиты** | OrbitTestSubject | TestExecutor | BallastTest | TestPlugin |
| **Navigation** | Нет (внешняя) | Decompose | ballast-navigation | Нет (внешняя) |
| **Compose** | Нативная | Через extensions | Нативная | Нативная |
| **Side Effects** | postSideEffect | Label | Event | Action |
| **Undo/Redo** | Нет | Нет | Да | Да |
| **State persistence** | Нет | Нет | Да | Да |
| **Coroutines-first** | Да | Нет (+ Reaktive) | Да | Да |
| **Community / GitHub** | ~130 usages | Крупнейший ecosystem | Маленькое | Растущее |
| **Зрелость** | 2020+ | 2019+ | 2021+ | 2022+ |
| **Идеален для** | Миграция с MVVM | Enterprise, строгость | Batteries included | Стартап, модульность |

---

## State vs Effect: обработка одноразовых событий

### Фундаментальная проблема

Некоторые действия **не являются состоянием**: навигация, Toast, Snackbar, аналитика, вибрация. Если записать "показать Toast" в State, то при recomposition Toast покажется повторно. MVI-библиотеки предлагают разные решения:

### Подходы библиотек

| Библиотека | Механизм | Тип | Доставка |
|------------|----------|-----|----------|
| **Orbit** | `postSideEffect()` → `sideEffectFlow` | `Flow<SideEffect>` | Replay при подписке |
| **MVIKotlin** | `publish(Label)` → `labels` / `labelFlow` | `Flow<Label>` | Одноразовая |
| **Ballast** | `postEvent()` → `EventHandler` | Callback | Гарантированная |
| **FlowMVI** | `action()` → `actions` | `Flow<Action>` | Configurable |

### Альтернатива: "reduce to state" (Google recommendation)

Google рекомендует минимизировать одноразовые события и выражать всё через State:

```kotlin
data class ScreenState(
    val userMessage: UserMessage? = null // показать и потом обнулить
)

// UI: показать Snackbar → сообщить ViewModel → обнулить userMessage
LaunchedEffect(state.userMessage) {
    state.userMessage?.let { message ->
        snackbarHostState.showSnackbar(message.text)
        viewModel.onIntent(ScreenIntent.MessageShown) // reduce { copy(userMessage = null) }
    }
}
```

### Когда какой подход

| Сценарий | State | Effect |
|----------|-------|--------|
| Toast / Snackbar | Можно (через id) | Можно |
| Навигация | Нежелательно | Рекомендуется |
| Аналитика | Не подходит | Единственный вариант |
| Показ диалога | Рекомендуется (State) | Можно |
| Вибрация / звук | Не подходит | Единственный вариант |
| Скролл к элементу | Можно (через id) | Можно |

**Правило:** если действие может быть пропущено без ущерба UX --- Effect. Если повторение безопасно --- State. Если событие привязано к аналитике или навигации --- всегда Effect.

---

## Продвинутые MVI паттерны

### Multiple Stores (микро-Store)

MVIKotlin подход: один Store на один domain concern (listStore, filterStore, cartStore, searchStore), а не один монолит на экран. Stores общаются через Labels: `searchStore.labels → listStore.accept(Intent.SearchChanged)`. Плюсы: каждый Store прост, тестируем отдельно, переиспользуем. Минусы: оркестрация между Store требует дополнительного кода.

### Nested State Machines

Для сложных workflow --- состояние внутри состояния: `sealed interface CheckoutState` содержит `Cart`, `Shipping(shippingState: ShippingFormState)`, `Payment(paymentState: PaymentFormState)`, `Confirmation(order)`. Каждый вложенный state (`ShippingFormState: Entering | Validating | Valid | Error`) имеет свои Intent. Reducer обрабатывает Intent в зависимости от текущего "внешнего" состояния.

### Debouncing / Throttling Intent

Классический use case --- поиск:

```kotlin
// Ручной MVI: cancel previous Job + delay
searchJob?.cancel()
searchJob = viewModelScope.launch { delay(300); performSearch(query) }

// Ballast: LifoInputStrategy — новый Input автоматически отменяет текущий
config.inputStrategy = LifoInputStrategy

// FlowMVI: manageJobs plugin — launchForIntent(key = "search") отменяет предыдущий
```

### Optimistic Updates

Паттерн: (1) запомнить текущий State, (2) оптимистично обновить UI, (3) отправить на сервер, (4) при ошибке --- откат к сохранённому State. В MVI это естественно: `reduce { copy(products = without(product)) }` → сеть → `onFailure { reduce { copy(products = savedProducts) } }`.

### Undo/Redo

MVI --- естественный fit для undo/redo: State иммутабелен, достаточно хранить историю.

```kotlin
// Концепт: список State + указатель текущей позиции
// undo = currentIndex--; redo = currentIndex++
// При новом действии — обрезаем "будущие" состояния

// FlowMVI: одна строка
store(initial = EditorState()) {
    undoRedo(maxQueueSize = 50) // plugin — всё из коробки
}

// Ballast: модуль ballast-undo с аналогичным API
```

### Inter-feature Communication

Два подхода: (1) **Labels** --- Store A публикует Label, Store B подписывается на `storeA.labels` и конвертирует в свой Intent; (2) **Shared Store** --- общий Store (например, CartStore), на который подписываются несколько feature через `store.states`.

---

## Тестирование MVI

MVI --- это "testability by design". Reducer --- чистая функция, Side Effects --- изолированные, Intent --- explicit.

### Тестирование Reducer (pure function)

```kotlin
// Не нужны моки. Не нужны coroutines. Просто assertEquals.
class CounterReducerTest {

    @Test
    fun `Increment increases count by 1`() {
        val state = CounterState(count = 5)
        val intent = CounterIntent.Increment

        val newState = reduce(state, intent)

        assertEquals(6, newState.count)
    }

    @Test
    fun `Decrement does not go below zero`() {
        val state = CounterState(count = 0)
        val intent = CounterIntent.Decrement

        val newState = reduce(state, intent)

        assertEquals(0, newState.count) // бизнес-правило
    }

    private fun reduce(state: CounterState, intent: CounterIntent): CounterState =
        when (intent) {
            is CounterIntent.Increment -> state.copy(count = state.count + 1)
            is CounterIntent.Decrement -> state.copy(count = maxOf(0, state.count - 1))
            is CounterIntent.SetValue -> state.copy(count = intent.value)
        }
}
```

### Тестирование Side Effects

```kotlin
@Test
fun `delete emits ShowToast effect`() = runTest {
    val vm = UsersViewModel(FakeRepository())
    val effects = mutableListOf<UsersEffect>()
    backgroundScope.launch { vm.effects.toList(effects) }
    vm.onIntent(UsersIntent.Delete(userId = 42))
    advanceUntilIdle()
    assertTrue(effects.any { it is UsersEffect.ShowToast })
}
```

### Orbit: TestContainerHost

```kotlin
@Test
fun `load products updates state correctly`() = runTest {
    val vm = ProductListViewModel(FakeRepo(products), FakeCartService(), FakeAnalytics())
    vm.test(this) {
        expectInitialState()
        vm.loadProducts()
        expectState { copy(isLoading = true, error = null) }
        expectState { copy(isLoading = false, products = products) }
    }
}
```

### MVIKotlin: Reducer + Executor

Reducer тестируется как pure function (см. выше). Executor --- через `TestStore`: `store.accept(Intent.Load)` → проверяем `store.messages` (последовательность Msg).

### Property-Based Testing для Reducer

Reducer как чистая функция идеально подходит для property-based тестов (kotest-property):

```kotlin
// Генерируем случайные State + Intent → проверяем инварианты
test("count is never negative") {
    checkAll(Arb.int(0..1000), Arb.element(CounterIntent.Increment, CounterIntent.Decrement)) {
        initialCount, intent ->
        val newState = reduce(CounterState(count = initialCount), intent)
        newState.count shouldBeGreaterThanOrEqual 0 // инвариант
    }
}
```

---

## MVI vs MVVM: когда переходить

### Decision Flowchart

```
Экран простой (1-3 действия)?          ──▶ MVVM
State из 3+ мест?                      ──▶ Нет → MVVM + sealed Intent
Race conditions / сложная отладка?     ──▶ Нет → Ручной MVI (30 строк)
Нужен time-travel / undo?             ──▶ Нет → Orbit MVI
KMP shared logic?                      ──▶ Нет → Orbit или FlowMVI
Строгость > удобство?                 ──▶ Да → MVIKotlin + Decompose
Plugin extensibility?                  ──▶ Да → FlowMVI / Нет → Ballast
```

### Decision Matrix

| Фактор | Остаться на MVVM | Ручной MVI | Orbit | MVIKotlin | Ballast | FlowMVI |
|--------|-----------------|------------|-------|-----------|---------|---------|
| Простые экраны | Идеально | Overkill | Overkill | Overkill | Overkill | Overkill |
| Сложный State | Трудно | Хорошо | Хорошо | Отлично | Хорошо | Отлично |
| Команда 1-2 | Любой | Любой | Хорошо | Излишне | Хорошо | Хорошо |
| Команда 5+ | Хаос | Расхождения | Хорошо | Отлично | Хорошо | Рискованно |
| Миграция с MVVM | --- | 1 час | 2 часа | 1 день | 4 часа | 4 часа |
| KMP | Нет | Ручная | Да | Да | Да | Да |
| Time-travel | Нет | Нет | Нет | Да | Да | Да |

### Стоимость и гибридный подход

**Boilerplate:** каждый экран получает sealed Intent + data class State + sealed Effect. На 20 экранов --- 60+ файлов. **Кривая обучения:** новый разработчик должен понять UDF, sealed Intent, reduce-паттерн; для MVIKotlin ещё Executor, Message, Label, Bootstrapper.

Многие команды используют гибрид: **простые экраны** (настройки, профиль) --- MVVM; **сложные экраны** (чат, редактор) --- MVI с Orbit или FlowMVI; **shared KMP logic** --- MVIKotlin Store. MVI --- инструмент, а не религия.

---

## Мифы и заблуждения

### Миф 1: "MVI = Redux для Android"

**Реальность:** MVI вдохновлён Redux, но это не копия. Redux --- single global store для всего приложения. Android MVI --- обычно один Store на экран (или на feature). Redux middleware --- это middleware. Android MVI может использовать любую обработку side effects. Общее: Reducer как чистая функция и однонаправленный поток.

### Миф 2: "MVI требует библиотеку"

**Реальность:** Минимальный MVI --- это 30 строк: `sealed class Intent` + `data class State` + `StateFlow` + `when`-выражение в `onIntent()`. Библиотека нужна для time-travel, тестовых утилит, plugin system. Но базовый MVI --- это паттерн, а не зависимость.

### Миф 3: "MVI сложнее MVVM"

**Реальность:** Базовый MVI --- это MVVM + `sealed class Intent`. Вместо пяти публичных методов в ViewModel (`loadUsers()`, `search()`, `delete()`, `refresh()`, `filter()`) --- один `onIntent(intent)` с exhaustive `when`. Строгий MVI с MVIKotlin --- да, сложнее. Orbit MVI --- практически тот же MVVM.

### Миф 4: "Orbit — не настоящий MVI"

**Реальность:** MVI --- это спектр. Orbit реализует все три принципа: явные Intent (через `intent{}`), единственный Reducer (`reduce{}`), однонаправленный поток. Формально это MVI. Менее строгий, чем MVIKotlin? Да. Не MVI? Нет.

### Миф 5: "MVI убивает performance"

**Реальность:** `StateFlow` --- это уже оптимизированный механизм Kotlin Coroutines. `data class` с `copy()` --- дешёвая операция (shallow copy). Compose сравнивает State через `equals()` и рендерит только изменённые части. Bottleneck MVI --- не в паттерне, а в бизнес-логике (сеть, БД). FlowMVI публикует бенчмарки, подтверждающие минимальный overhead.

### Миф 6: "Нужно одно состояние на весь экран"

**Реальность:** Micro-stores (MVIKotlin подход) --- один Store на один concern. Экран с поиском, списком и корзиной может иметь три независимых Store. Это уменьшает размер State, упрощает тестирование и позволяет переиспользовать Store между экранами.

### Миф 7: "MVI не совместим с Compose"

**Реальность:** MVI и Compose --- естественный fit. Compose уже работает по принципу `State → UI`: Composable-функция принимает State и рендерит UI. MVI формализует откуда берётся этот State и как он обновляется. Все четыре библиотеки имеют нативную поддержку Compose.

---

## CS-фундамент

| CS-концепция | Где в MVI | Пример |
|-------------|-----------|--------|
| **State Machine (FSM)** | Reducer: `(State, Intent) → State` | Каждый Intent --- переход между состояниями |
| **Unidirectional Data Flow** | Core principle | View → Intent → Reducer → State → View |
| **Reducer Pattern** | Центр MVI | Pure function: `(S, A) → S` |
| **Event Sourcing** | Intent log | Восстановление State по последовательности Intent |
| **Command Pattern** | `sealed class Intent` | Инкапсуляция запроса как объекта |
| **Observer Pattern** | StateFlow / labels | UI подписывается на State |
| **Strategy Pattern** | Plugin / Middleware | Подмена обработки Intent (logging, analytics) |
| **Chain of Responsibility** | FlowMVI Plugin pipeline | Plugin перехватывают Intent по цепочке |
| **Immutability** | `data class State` + `copy()` | State никогда не мутируется |
| **Pure Functions** | Reducer | Нет side effects, детерминированный результат |
| **Separation of Concerns** | Intent ≠ Reducer ≠ Effect | Каждый компонент --- одна ответственность |

---

## Связь с другими темами

**[[state-pattern]]** --- MVI Reducer **является** конечным автоматом. `sealed class Intent` --- события-переходы, `data class State` --- текущее состояние, `when` в Reducer --- таблица переходов. Exhaustive `when` гарантирует обработку всех переходов на compile-time.

**[[observer-pattern]]** --- StateFlow в MVI --- реализация Observer. UI подписывается на поток состояний. В Compose `collectAsStateWithLifecycle()` превращает Flow в Compose State, а recomposition --- в автоматический `update()`.

**[[strategy-pattern]]** --- Middleware и Plugin --- это Strategy: разные алгоритмы обработки Intent через общий интерфейс. InputStrategy в Ballast (LIFO/FIFO/Parallel) --- каноничный пример.

**[[solid-principles]]** --- Reducer следует SRP (только трансформация State). Sealed Intent следует OCP (новый Intent не ломает существующие). Plugin system FlowMVI --- пример ISP.

**[[functional-programming]]** --- Reducer --- чистая функция. Иммутабельность State через `data class` + `copy()`. Композиция Middleware через `foldRight` --- функциональная комбинация.

**[[concurrency-fundamentals]]** --- MVI решает race conditions: Intent сериализуются через один канал. Вместо пяти параллельных `_state.update{}` --- одна точка обновления. FlowMVI: выбор между последовательной и параллельной обработкой.

**[[testing-fundamentals]]** --- MVI = "testability by design". Reducer тестируется как `assertEquals(expected, reduce(state, intent))`. Не нужны моки, coroutines, Android-контекст.

**[[error-handling]]** --- Ошибка --- **явный вариант State**: `data class Error(val message: String) : ScreenState`. FlowMVI `recover{}` формализует обработку ошибок на уровне Store.

**[[event-driven-architecture]]** --- MVI --- event-driven на уровне UI. Intent = события, Reducer = обработчик, лог Intent = event log для восстановления State (аналог event sourcing).

**[[android-mvvm-deep-dive]]** --- MVI --- эволюция MVVM. Orbit MVI --- мост: MVVM API + MVI принципы. Миграция: замена публичных методов на `intent{}`.

**[[android-compose-architectures]]** --- Compose и MVI --- естественная пара. Composable уже работает как View: принимает State, возвращает UI. MVI формализует источник State.

---

## Источники

| # | Название | URL | Тип |
|---|---------|-----|-----|
| 1 | Orbit MVI — official documentation | [orbit-mvi.org](https://orbit-mvi.org/) | Документация |
| 2 | MVIKotlin — official documentation | [arkivanov.github.io/MVIKotlin](https://arkivanov.github.io/MVIKotlin/) | Документация |
| 3 | Ballast — official documentation | [copper-leaf.github.io/ballast](https://copper-leaf.github.io/ballast/) | Документация |
| 4 | FlowMVI — official documentation | [opensource.respawn.pro/FlowMVI](https://opensource.respawn.pro/FlowMVI/) | Документация |
| 5 | André Staltz — Unidirectional User Interface Architectures | [staltz.com/unidirectional-user-interface-architectures.html](https://staltz.com/unidirectional-user-interface-architectures.html) | Статья (2015) |
| 6 | Best Kotlin MVI Architecture Libraries 2025-2026 | [nek12.dev/blog/en/best-kotlin-mvi-architecture-libraries-2025-2026](https://nek12.dev/blog/en/best-kotlin-mvi-architecture-libraries-2025-2026-for-state-management-android-and-compose) | Сравнение |
| 7 | Hannes Dorfmann — Reactive Apps with MVI | [hannesdorfmann.com/android/mosby3-mvi-1](http://hannesdorfmann.com/android/mosby3-mvi-1/) | Серия статей (2017) |
| 8 | MVI Library Feature Comparison (Ballast) | [copper-leaf.github.io/ballast/wiki/feature-comparison](https://copper-leaf.github.io/ballast/wiki/feature-comparison/) | Таблица |
| 9 | Dan Abramov — Redux documentation | [redux.js.org](https://redux.js.org/) | Документация |
| 10 | droidcon — Yes, That's MVI: Full History | [droidcon.com/2025/06/10/yes-thats-mvi](https://www.droidcon.com/2025/06/10/yes-thats-mvi-the-patterns-full-history-misconceptions-and-modern-android-form/) | Доклад |

---

## Проверь себя

<details>
<summary>Чем Reducer в MVI отличается от обычного метода update в MVVM?</summary>

Reducer --- **чистая функция** `(State, Intent) -> State`: не имеет побочных эффектов, не обращается к сети/БД, детерминирован. В MVVM `_state.update{}` вызывается из разных методов, может содержать побочные эффекты внутри, и нет гарантии, что обновление State --- единственная операция в методе. Reducer гарантирует: одна функция, один вход, один выход, никаких сюрпризов.
</details>

<details>
<summary>В чём ключевое архитектурное различие между Orbit MVI и MVIKotlin?</summary>

**Orbit** объединяет бизнес-логику и трансформацию State в одном `intent{}` блоке --- внутри можно и сходить в сеть, и вызвать `reduce{}`. Это удобно, но менее строго.

**MVIKotlin** разделяет: Executor занимается бизнес-логикой и async-работой, а Reducer --- только трансформацией State. Executor не может напрямую менять State --- только отправлять Message в Reducer. Это добавляет boilerplate (Message как отдельный тип), но гарантирует, что Reducer остаётся pure function и тестируется без моков.
</details>

<details>
<summary>Когда FlowMVI предпочтительнее MVIKotlin, и наоборот?</summary>

**FlowMVI** предпочтительнее, когда: нужна модульная plugin-система (logging, analytics, undo/redo подключаются одной строкой), команда маленькая и опытная в coroutines, важна гибкость и минимальный boilerplate, проект новый (нет legacy).

**MVIKotlin** предпочтительнее, когда: команда большая (5+) и нужна строгая дисциплина, проект enterprise-уровня (строгое разделение Executor/Reducer предотвращает "ленивый" код), нужна экосистема Decompose для навигации, time-travel debugging через IDE --- критично для отладки.
</details>

---

## Ключевые карточки

**Q:** Что такое Reducer в контексте MVI?
**A:** Чистая функция `(State, Intent) → State`. Не имеет побочных эффектов, не обращается к IO. Одинаковый вход всегда даёт одинаковый выход. Центральный элемент MVI, обеспечивающий предсказуемость и тестируемость.

**Q:** Как Orbit MVI обрабатывает side effects?
**A:** Через `postSideEffect()` внутри `intent{}` блока. Side effects доставляются в UI через `container.sideEffectFlow`. Это `Flow`, на который UI подписывается в `LaunchedEffect`.

**Q:** Какие компоненты MVIKotlin Store участвуют в обработке Intent?
**A:** Intent → **Executor** (бизнес-логика, async) → **Message** (внутреннее событие) → **Reducer** (pure function) → **State**. Executor также может публиковать **Label** (одноразовые события наружу). При инициализации **Bootstrapper** запускает начальные Action.

**Q:** Что такое Plugin в FlowMVI?
**A:** Единица бизнес-логики в Chain of Responsibility. Всё в FlowMVI --- Plugin: reduce, logging, recover, analytics, undo/redo, time-travel. Plugins выполняются в порядке установки. Каждый Plugin может перехватить Intent, модифицировать State, отправить Action или обработать ошибку.

**Q:** В чём уникальность InputStrategy в Ballast?
**A:** Ballast позволяет выбрать стратегию обработки входящих Input: **LIFO** (default) --- новый Input отменяет текущий (поиск), **FIFO** --- Input обрабатываются по очереди (отправка форм), **Parallel** --- Input обрабатываются параллельно. Это решает типичные проблемы concurrency на уровне архитектуры.

**Q:** Минимальный MVI без библиотек --- сколько кода?
**A:** ~30 строк: `sealed interface Intent`, `data class State`, `MutableStateFlow`, `fun onIntent(intent)` с `when`-выражением и `_state.update{}`. Это уже MVI: явные Intent, единственная точка обновления State, однонаправленный поток данных.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| MVVM deep dive | [[android-mvvm-deep-dive]] | Сравнить с MVI, понять откуда выросло |
| State management | [[android-state-management]] | Полная картина управления состоянием |
| Compose архитектуры | [[android-compose-architectures]] | MVI + Compose в деталях |
| Clean Architecture | [[android-clean-architecture]] | Как MVI вписывается в слоистую архитектуру |
| Architecture Patterns | [[android-architecture-patterns]] | Обзор всех паттернов: MVC, MVP, MVVM, MVI |
| Architecture Evolution | [[android-architecture-evolution]] | Историческая перспектива |
| State Pattern | [[state-pattern]] | CS-фундамент: конечные автоматы |
| Functional Programming | [[functional-programming]] | Pure functions, immutability --- основа Reducer |
| Concurrency | [[concurrency-fundamentals]] | Почему MVI решает race conditions |
| Testing | [[testing-fundamentals]] | Как тестировать pure functions |
