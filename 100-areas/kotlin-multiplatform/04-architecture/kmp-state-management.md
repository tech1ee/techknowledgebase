---
title: "KMP State Management: StateFlow, MVI, Redux patterns"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, state, stateflow, sharedflow, mvi, redux, compose]
related:
  - "[[00-kmp-overview]]"
  - "[[kmp-architecture-patterns]]"
  - "[[kotlin-flow]]"
cs-foundations:
  - "[[reactive-programming-paradigm]]"
  - "[[observer-pattern]]"
  - "[[immutability-principles]]"
  - "[[concurrency-primitives]]"
---

# KMP State Management

> **TL;DR:** StateFlow — основа state management в KMP (single source of truth). MutableStateFlow для ViewModel, collectAsState() для Compose. iOS требует bridging: SKIE или KMP-NativeCoroutines для Swift async/await. MutableState только для UI-локального state. MVI паттерн для predictable state с unidirectional data flow. Всегда обновляйте state на Main thread (iOS crashes на background updates). Redux-Kotlin для complex global state.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin Coroutines | Async operations | [[kotlin-coroutines]] |
| Kotlin Flow | Reactive streams | [[kotlin-flow]] |
| Compose Basics | UI state | [[compose-basics]] |
| **CS-foundations** | | |
| Observer Pattern | Основа reactive UI | [[observer-pattern]] |
| Immutability | Predictable state updates | [[immutability-principles]] |
| Concurrency | Thread-safe state | [[concurrency-primitives]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **StateFlow** | Hot flow с текущим значением | Табло с текущей температурой |
| **SharedFlow** | Hot flow без начального значения | Лента новостей |
| **MutableState** | Compose-specific state | Локальная переменная UI |
| **Single Source of Truth** | Одно место хранения state | Единый паспорт гражданина |
| **Unidirectional Data Flow** | Однонаправленный поток | Конвейер на фабрике |
| **Reducer** | Функция создания нового state | Рецепт приготовления |

---

## Почему State Management — это Observer + Immutability?

### Основа: Observer Pattern (GoF, 1994)

**State Management** в UI-приложениях построен на **Observer Pattern**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    OBSERVER PATTERN В UI                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Subject (Observable)                   Observers (Subscribers)    │
│   ┌──────────────────┐                                              │
│   │                  │  ──► notify() ──►  ┌──────────────┐          │
│   │   StateFlow      │                    │  Compose UI  │          │
│   │   (state holder) │  ──► notify() ──►  └──────────────┘          │
│   │                  │                    ┌──────────────┐          │
│   │   state.value    │  ──► notify() ──►  │  SwiftUI     │          │
│   │      = X         │                    └──────────────┘          │
│   └──────────────────┘                                              │
│                                                                     │
│   collectAsState()  = подписка на Observable                        │
│   emit()            = публикация изменений                          │
│   .value            = текущее значение Subject                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**StateFlow vs LiveData vs Observable:**

| Концепция | Реализация | Особенности |
|-----------|------------|-------------|
| Subject | StateFlow | Hot stream, replay = 1 |
| Subject | LiveData | Lifecycle-aware, Android-only |
| Subject | BehaviorSubject (Rx) | Replay last value |
| Observer | collectAsState() | Compose subscription |
| Observer | observe() | LiveData subscription |

### Почему Immutability критична для State?

**Проблема с mutable state:**

```kotlin
// ❌ MUTABLE STATE — источник багов
data class MutableUserState(
    var name: String = "",
    val items: MutableList<Item> = mutableListOf()
)

// Проблема 1: Race condition
thread1 { state.name = "Alice" }
thread2 { state.name = "Bob" }
// Какое значение? Непредсказуемо!

// Проблема 2: UI не узнаёт об изменении
state.items.add(newItem)  // Compose не видит изменения — нет recomposition!
```

**Решение: Immutable State + Copy:**

```kotlin
// ✅ IMMUTABLE STATE — предсказуемость
data class UserState(
    val name: String = "",
    val items: List<Item> = emptyList()
)

// Новый объект → новый identity → UI видит изменение
_state.update { it.copy(name = "Alice") }
_state.update { it.copy(items = it.items + newItem) }
```

**Почему это работает?**

```
┌─────────────────────────────────────────────────────────────────────┐
│              IMMUTABILITY + STRUCTURAL SHARING                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   state1 = UserState(name="A", items=[1,2,3])                       │
│   state2 = state1.copy(name="B")                                    │
│                                                                     │
│   Memory:                                                           │
│   ┌─────────────┐                                                   │
│   │   state1    │ ───► name: "A"                                    │
│   │             │ ───┐                                              │
│   └─────────────┘    │    ┌───────────────┐                         │
│                      └───►│ items: [1,2,3]│ ◄───┐                   │
│   ┌─────────────┐    ┌───►│               │     │                   │
│   │   state2    │ ───┘    └───────────────┘     │                   │
│   │             │ ───► name: "B"                │                   │
│   └─────────────┘         shared reference ─────┘                   │
│                                                                     │
│   Items list НЕ копируется — shared reference!                      │
│   Kotlin copy() эффективен благодаря structural sharing             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Unidirectional Data Flow (UDF)

**UDF** — архитектурный паттерн, делающий state предсказуемым:

```
┌─────────────────────────────────────────────────────────────────────┐
│              UNIDIRECTIONAL DATA FLOW                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                    ┌──────────────┐                                 │
│         ┌─────────│     VIEW     │◄─────────┐                       │
│         │         │  (Compose)   │          │                       │
│         │         └──────────────┘          │                       │
│         │               │                   │                       │
│         │               │ User Events       │ State                 │
│         │               │ (clicks, input)   │ (data to display)     │
│         │               ▼                   │                       │
│         │         ┌──────────────┐          │                       │
│         │         │   VIEWMODEL  │──────────┘                       │
│         │         │   (Intent)   │                                  │
│         │         └──────────────┘                                  │
│         │               │                                           │
│         │               │ Actions                                   │
│         │               ▼                                           │
│         │         ┌──────────────┐                                  │
│         └────────►│    MODEL     │                                  │
│                   │  (Reducer)   │                                  │
│                   └──────────────┘                                  │
│                                                                     │
│   Данные текут в ОДНОМ направлении:                                 │
│   View → Intent → Model → State → View                              │
│                                                                     │
│   Преимущества:                                                     │
│   • Предсказуемость (всегда знаем откуда state)                     │
│   • Тестируемость (Reducer — pure function)                         │
│   • Debugging (можно записать все transitions)                      │
│   • Time-travel (можно "перемотать" state)                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Hot vs Cold Streams

**Критически важно понимать разницу:**

| Характеристика | Cold (Flow) | Hot (StateFlow/SharedFlow) |
|----------------|-------------|---------------------------|
| Активация | При первом collect | Сразу при создании |
| Subscribers | Независимые executions | Shared execution |
| Replay | Нет (начинает с начала) | Да (replay buffer) |
| Память | Создаётся при collect | Живёт пока scope жив |
| Use case | API calls, DB queries | UI state, events |

```kotlin
// COLD: каждый collect запускает новый HTTP запрос
val userFlow: Flow<User> = flow {
    emit(api.getUser())  // Вызывается при каждом collect
}

// HOT: один источник, много подписчиков
val userState: StateFlow<User?> = MutableStateFlow(null)
// Все collectors видят одно и то же значение
```

### Почему Main Thread для iOS критичен?

**UIKit/SwiftUI требуют UI updates на Main thread:**

```
┌─────────────────────────────────────────────────────────────────────┐
│              iOS THREADING MODEL                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Kotlin Coroutine                      iOS Main Thread             │
│   (Background)                          (UI Thread)                 │
│                                                                     │
│   ┌──────────────┐                      ┌──────────────┐            │
│   │ Dispatchers  │  ─── emit() ───►     │   UIKit      │            │
│   │     .IO      │     state update     │   Runtime    │            │
│   └──────────────┘                      └──────────────┘            │
│                                                │                    │
│                                                ▼                    │
│                                         ┌──────────────┐            │
│                                         │    CRASH!    │            │
│                                         │ "not on main │            │
│                                         │   thread"    │            │
│                                         └──────────────┘            │
│                                                                     │
│   РЕШЕНИЕ: Dispatchers.Main.immediate                               │
│   ─────────────────────────────────────                             │
│   withContext(Dispatchers.Main.immediate) {                         │
│       _state.value = newState  // Safe!                             │
│   }                                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## StateFlow vs SharedFlow vs MutableState

```
┌─────────────────────────────────────────────────────────────────────┐
│                    STATE TYPES COMPARISON                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   STATEFLOW                                                         │
│   ─────────────────────────────                                     │
│   • Требует initial value                                           │
│   • Emits only when value changes                                   │
│   • Direct access via .value                                        │
│   • Идеален для UI state в ViewModel                                │
│                                                                     │
│   SHAREDFLOW                                                        │
│   ─────────────────────────────                                     │
│   • No initial value needed                                         │
│   • Emits every event (even duplicates)                             │
│   • No direct .value access                                         │
│   • Идеален для one-time events                                     │
│                                                                     │
│   MUTABLESTATE (Compose)                                            │
│   ─────────────────────────────                                     │
│   • Compose-specific                                                │
│   • Triggers recomposition                                          │
│   • For local UI state only                                         │
│   • НЕ использовать в ViewModel                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Когда использовать

| Use Case | StateFlow | SharedFlow | MutableState |
|----------|-----------|------------|--------------|
| ViewModel UI state | ✅ | ❌ | ❌ |
| One-time events | ❌ | ✅ | ❌ |
| Local Compose state | ❌ | ❌ | ✅ |
| Configuration state | ✅ | ❌ | ❌ |
| Navigation events | ❌ | ✅ | ❌ |
| Form input | ✅ | ❌ | ⚠️ local only |

---

## StateFlow в ViewModel

### Базовый паттерн

```kotlin
// commonMain/presentation/UserListViewModel.kt
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class UserListViewModel(
    private val getUsersUseCase: GetUsersUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserListState())
    val uiState: StateFlow<UserListState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            getUsersUseCase()
                .onSuccess { users ->
                    _uiState.update {
                        it.copy(isLoading = false, users = users, error = null)
                    }
                }
                .onFailure { error ->
                    _uiState.update {
                        it.copy(isLoading = false, error = error.message)
                    }
                }
        }
    }

    fun onUserClicked(user: User) {
        // Handle user click
    }
}

data class UserListState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null
)
```

### Compose Collection

```kotlin
// commonMain/ui/UserListScreen.kt
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue

@Composable
fun UserListScreen(
    viewModel: UserListViewModel
) {
    val state by viewModel.uiState.collectAsState()

    when {
        state.isLoading -> LoadingIndicator()
        state.error != null -> ErrorMessage(state.error!!)
        else -> UserList(
            users = state.users,
            onUserClick = viewModel::onUserClicked
        )
    }
}
```

---

## One-Time Events с SharedFlow

### Events Pattern

```kotlin
class ProfileViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileState())
    val uiState: StateFlow<ProfileState> = _uiState.asStateFlow()

    // SharedFlow для one-time events
    private val _events = MutableSharedFlow<ProfileEvent>()
    val events: SharedFlow<ProfileEvent> = _events.asSharedFlow()

    fun saveProfile(name: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isSaving = true) }

            repository.saveProfile(name)
                .onSuccess {
                    _uiState.update { it.copy(isSaving = false) }
                    _events.emit(ProfileEvent.SaveSuccess)
                }
                .onFailure { error ->
                    _uiState.update { it.copy(isSaving = false) }
                    _events.emit(ProfileEvent.SaveError(error.message ?: "Unknown error"))
                }
        }
    }
}

sealed interface ProfileEvent {
    data object SaveSuccess : ProfileEvent
    data class SaveError(val message: String) : ProfileEvent
    data class Navigate(val route: String) : ProfileEvent
}

data class ProfileState(
    val name: String = "",
    val email: String = "",
    val isSaving: Boolean = false
)
```

### Collecting Events

```kotlin
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel,
    onNavigate: (String) -> Unit
) {
    val state by viewModel.uiState.collectAsState()

    // Collect one-time events
    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is ProfileEvent.SaveSuccess -> {
                    // Show snackbar
                }
                is ProfileEvent.SaveError -> {
                    // Show error dialog
                }
                is ProfileEvent.Navigate -> {
                    onNavigate(event.route)
                }
            }
        }
    }

    ProfileContent(state = state, onSave = viewModel::saveProfile)
}
```

---

## iOS Bridging

### Проблема

```
⚠️ StateFlow НЕ работает напрямую в Swift

1. Generic types теряются при экспорте в Obj-C
2. Swift не может collect Flow без wrapper
3. Lifecycle management требует ручной работы
```

### Решение 1: SKIE (Рекомендуется)

```kotlin
// build.gradle.kts
plugins {
    id("co.touchlab.skie") version "0.9.3"
}
```

```swift
// Swift: SKIE автоматически конвертирует Flow в AsyncSequence
import Shared

@MainActor
class UserListViewModelWrapper: ObservableObject {
    private let viewModel = UserListViewModel()
    @Published var state = UserListState()

    init() {
        Task {
            for await newState in viewModel.uiState {
                self.state = newState
            }
        }
    }
}
```

### Решение 2: KMP-NativeCoroutines

```kotlin
// build.gradle.kts
plugins {
    id("com.rickclephas.kmp.nativecoroutines") version "1.0.0-ALPHA-35"
}
```

```kotlin
// commonMain
import com.rickclephas.kmp.nativecoroutines.NativeCoroutines

class UserListViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UserListState())

    @NativeCoroutines
    val uiState: StateFlow<UserListState> = _uiState.asStateFlow()
}
```

```swift
// Swift with Combine
import KMPNativeCoroutinesCombine

class UserListViewModelWrapper: ObservableObject {
    private let viewModel = UserListViewModel()
    @Published var state = UserListState()
    private var cancellables = Set<AnyCancellable>()

    init() {
        createPublisher(for: viewModel.uiStateFlow)
            .receive(on: DispatchQueue.main)
            .sink { _ in } receiveValue: { [weak self] state in
                self?.state = state
            }
            .store(in: &cancellables)
    }
}
```

### Решение 3: Custom Wrapper

```kotlin
// iosMain/FlowWrapper.kt
class FlowWrapper<T>(private val flow: Flow<T>) {
    fun subscribe(
        scope: CoroutineScope,
        onEach: (T) -> Unit,
        onError: (Throwable) -> Unit,
        onComplete: () -> Unit
    ): Cancellable {
        val job = scope.launch {
            try {
                flow.collect { onEach(it) }
                onComplete()
            } catch (e: Throwable) {
                onError(e)
            }
        }
        return object : Cancellable {
            override fun cancel() {
                job.cancel()
            }
        }
    }
}

interface Cancellable {
    fun cancel()
}

// Extension для создания wrapper
fun <T> Flow<T>.wrap(): FlowWrapper<T> = FlowWrapper(this)
```

```swift
// Swift
class UserListViewModelWrapper: ObservableObject {
    private let viewModel = UserListViewModel()
    @Published var state = UserListState()
    private var cancellable: Cancellable?

    init() {
        cancellable = viewModel.uiStateWrapper.subscribe(
            scope: viewModel.viewModelScope,
            onEach: { [weak self] state in
                DispatchQueue.main.async {
                    self?.state = state
                }
            },
            onError: { _ in },
            onComplete: { }
        )
    }

    deinit {
        cancellable?.cancel()
    }
}
```

---

## MVI State Management

### Full MVI Pattern

```kotlin
// State
data class CounterState(
    val count: Int = 0,
    val isLoading: Boolean = false
)

// Intent (User actions)
sealed interface CounterIntent {
    data object Increment : CounterIntent
    data object Decrement : CounterIntent
    data class SetValue(val value: Int) : CounterIntent
}

// Side Effects
sealed interface CounterEffect {
    data class ShowToast(val message: String) : CounterEffect
}

// ViewModel with MVI
class CounterViewModel : ViewModel() {
    private val _state = MutableStateFlow(CounterState())
    val state: StateFlow<CounterState> = _state.asStateFlow()

    private val _effects = MutableSharedFlow<CounterEffect>()
    val effects: SharedFlow<CounterEffect> = _effects.asSharedFlow()

    fun processIntent(intent: CounterIntent) {
        when (intent) {
            is CounterIntent.Increment -> {
                _state.update { it.copy(count = it.count + 1) }
                checkThreshold()
            }
            is CounterIntent.Decrement -> {
                _state.update { it.copy(count = it.count - 1) }
            }
            is CounterIntent.SetValue -> {
                _state.update { it.copy(count = intent.value) }
            }
        }
    }

    private fun checkThreshold() {
        if (_state.value.count >= 10) {
            viewModelScope.launch {
                _effects.emit(CounterEffect.ShowToast("Reached 10!"))
            }
        }
    }
}
```

### MVI with Reducer

```kotlin
// Pure Reducer function
object CounterReducer {
    fun reduce(state: CounterState, intent: CounterIntent): CounterState {
        return when (intent) {
            is CounterIntent.Increment -> state.copy(count = state.count + 1)
            is CounterIntent.Decrement -> state.copy(count = state.count - 1)
            is CounterIntent.SetValue -> state.copy(count = intent.value)
        }
    }
}

class CounterViewModel : ViewModel() {
    private val _state = MutableStateFlow(CounterState())
    val state: StateFlow<CounterState> = _state.asStateFlow()

    fun processIntent(intent: CounterIntent) {
        _state.update { currentState ->
            CounterReducer.reduce(currentState, intent)
        }
    }
}
```

---

## Redux Pattern

### Redux-Kotlin Setup

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("org.reduxkotlin:redux-kotlin-threadsafe:0.6.0")
        }
    }
}
```

### Store Implementation

```kotlin
// State
data class AppState(
    val counter: Int = 0,
    val user: User? = null,
    val isLoading: Boolean = false
)

// Actions
sealed interface AppAction {
    data object Increment : AppAction
    data object Decrement : AppAction
    data class SetUser(val user: User) : AppAction
    data class SetLoading(val loading: Boolean) : AppAction
}

// Reducer
val appReducer: Reducer<AppState> = { state, action ->
    when (action) {
        is AppAction.Increment -> state.copy(counter = state.counter + 1)
        is AppAction.Decrement -> state.copy(counter = state.counter - 1)
        is AppAction.SetUser -> state.copy(user = action.user)
        is AppAction.SetLoading -> state.copy(isLoading = action.loading)
        else -> state
    }
}

// Store
val store = createThreadSafeStore(
    reducer = appReducer,
    preloadedState = AppState()
)

// Usage
store.dispatch(AppAction.Increment)
val currentState = store.state
```

### Redux with Middleware

```kotlin
// Logging middleware
val loggingMiddleware: Middleware<AppState> = { store ->
    { next ->
        { action ->
            println("Dispatching: $action")
            val result = next(action)
            println("New state: ${store.state}")
            result
        }
    }
}

// Thunk middleware for async actions
val thunkMiddleware: Middleware<AppState> = { store ->
    { next ->
        { action ->
            if (action is ThunkAction) {
                action.invoke(store::dispatch, store::getState)
            } else {
                next(action)
            }
        }
    }
}

typealias ThunkAction = (dispatch: (Any) -> Any, getState: () -> AppState) -> Unit

// Async action
fun loadUser(userId: String): ThunkAction = { dispatch, _ ->
    dispatch(AppAction.SetLoading(true))
    // Async operation
    val user = userRepository.getUser(userId)
    dispatch(AppAction.SetUser(user))
    dispatch(AppAction.SetLoading(false))
}

// Store with middleware
val store = createThreadSafeStore(
    reducer = appReducer,
    preloadedState = AppState(),
    enhancer = applyMiddleware(loggingMiddleware, thunkMiddleware)
)
```

---

## Best Practices

### 1. Main Thread Updates (iOS Critical)

```kotlin
// ⚠️ iOS CRASHES на background state updates

class SafeViewModel(
    private val mainDispatcher: CoroutineDispatcher = Dispatchers.Main
) : ViewModel() {

    private val _state = MutableStateFlow(MyState())

    fun updateState(newValue: String) {
        viewModelScope.launch(mainDispatcher) {
            _state.update { it.copy(value = newValue) }
        }
    }
}
```

### 2. Immutable State

```kotlin
// ✅ Immutable data class
data class UserState(
    val name: String = "",
    val items: List<Item> = emptyList()  // List is immutable
)

// ✅ Update with copy
_state.update { it.copy(name = newName) }

// ❌ НЕ мутировать state напрямую
// state.value.items.add(item)  // WRONG!
```

### 3. State Hoisting

```kotlin
// ✅ State в ViewModel, UI stateless
@Composable
fun UserScreen(viewModel: UserViewModel) {
    val state by viewModel.state.collectAsState()
    UserContent(
        state = state,
        onNameChange = viewModel::updateName,
        onSave = viewModel::save
    )
}

@Composable
fun UserContent(
    state: UserState,
    onNameChange: (String) -> Unit,
    onSave: () -> Unit
) {
    // Stateless composable
}
```

### 4. Derived State

```kotlin
class ListViewModel : ViewModel() {
    private val _items = MutableStateFlow<List<Item>>(emptyList())

    // Derived state
    val itemCount: StateFlow<Int> = _items
        .map { it.size }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0)

    val hasItems: StateFlow<Boolean> = _items
        .map { it.isNotEmpty() }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), false)
}
```

---

## Мифы и заблуждения

### Миф 1: "MutableState из Compose можно использовать в ViewModel"

**Реальность:** `MutableState` — это Compose-specific API, работающий через snapshot system. В ViewModel используйте `StateFlow`:
- StateFlow = multiplatform, testable, lifecycle-agnostic
- MutableState = Compose-only, tied to composition

### Миф 2: "StateFlow медленнее LiveData"

**Реальность:** Разница в performance negligible для UI. StateFlow даже эффективнее благодаря:
- conflation (не emit duplicates по умолчанию)
- structured concurrency
- no lifecycle overhead

### Миф 3: "SharedFlow replaces Channels для events"

**Реальность:** SharedFlow и Channel имеют разные гарантии:
- SharedFlow: broadcast (все subscribers получают)
- Channel: send-receive (один consumer забирает)

Для navigation events иногда Channel лучше (гарантия что event обработан один раз).

### Миф 4: "SKIE решает все iOS bridging проблемы"

**Реальность:** SKIE упрощает многое, но:
- Добавляет compile time overhead
- Некоторые advanced scenarios требуют custom wrappers
- Debugging может быть сложнее (generated code)

Для простых проектов — отличное решение. Для complex — оценивайте trade-offs.

### Миф 5: "Redux-Kotlin нужен для любого серьёзного state management"

**Реальность:** Redux-Kotlin полезен для:
- Global app state
- Complex multi-reducer scenarios
- Time-travel debugging needs

Для большинства feature-level state — StateFlow + MVVM достаточно. Redux adds complexity.

### Миф 6: "collectAsState() всегда вызывает recomposition"

**Реальность:** collectAsState() вызывает recomposition **только когда state меняется**. StateFlow имеет conflation — одинаковые значения не emit.

```kotlin
_state.value = currentState  // Если currentState == _state.value, emit НЕ произойдёт
```

### Миф 7: "Любой background thread можно использовать для state updates на iOS"

**Реальность:** iOS **crashes** при UI updates не с Main thread. Всегда используйте:
```kotlin
withContext(Dispatchers.Main.immediate) {
    _state.value = newState
}
```
Или update() который thread-safe.

---

## Рекомендуемые источники

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [StateFlow & SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) | Official | Android docs |
| [StateFlow API](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/) | Official | Kotlin docs |

### Статьи

| Источник | Тип | Описание |
|----------|-----|----------|
| [StateFlow in KMP](https://johnoreilly.dev/posts/state-flow-multiplatform/) | Blog | Practical guide |
| [State Management Survival Guide](https://medium.com/@hiren6997/state-management-in-kotlin-multiplatform-my-complete-survival-guide-c03b32c08038) | Blog | Comprehensive |
| [Flow to Combine Bridge](https://johnoreilly.dev/posts/kotlinmultiplatform-swift-combine_publisher-flow/) | Blog | iOS bridging |

### Libraries

| Library | Описание |
|---------|----------|
| [SKIE](https://skie.touchlab.co/) | Swift-friendly Kotlin APIs |
| [KMP-NativeCoroutines](https://github.com/rickclephas/KMP-NativeCoroutines) | Swift async/await support |
| [Redux-Kotlin](https://reduxkotlin.org/) | Redux for KMP |
| [MVIKotlin](https://github.com/arkivanov/MVIKotlin) | MVI framework |

### CS-фундамент

| Тема | Почему важно | Где изучить |
|------|--------------|-------------|
| Observer Pattern | Основа reactive UI | [[observer-pattern]] |
| Immutability | Predictable state updates | [[immutability-principles]] |
| Concurrency | Thread-safe operations | [[concurrency-primitives]] |
| Hot vs Cold Streams | StateFlow vs Flow | [[reactive-programming-paradigm]] |
| Structural Sharing | Efficient copy() | [[persistent-data-structures]] |

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, kotlinx-coroutines 1.8.0, SKIE 0.9.3*
