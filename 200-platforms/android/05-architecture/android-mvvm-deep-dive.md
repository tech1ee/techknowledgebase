---
title: "MVVM на Android: от LiveData к Compose --- все вариации паттерна"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
status: published
cs-foundations: [observer-pattern, data-binding, reactive-programming, state-management, lifecycle-awareness]
tags:
  - topic/android
  - topic/architecture
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-architecture-patterns]]"
  - "[[android-architecture-evolution]]"
  - "[[android-mvi-deep-dive]]"
  - "[[android-mvc-mvp]]"
  - "[[android-viewmodel-internals]]"
  - "[[android-repository-pattern]]"
  - "[[android-clean-architecture]]"
  - "[[android-compose]]"
  - "[[android-state-management]]"
  - "[[kotlin-flow]]"
  - "[[observer-pattern]]"
  - "[[state-pattern]]"
  - "[[solid-principles]]"
  - "[[coupling-cohesion]]"
  - "[[testing-fundamentals]]"
  - "[[error-handling]]"
  - "[[functional-programming]]"
prerequisites:
  - "[[android-activity-lifecycle]]"
  - "[[android-architecture-patterns]]"
  - "[[android-viewmodel-internals]]"
reading_time: 40
difficulty: 6
study_status: not_started
mastery: 0
---

# MVVM на Android: от LiveData к Compose --- все вариации паттерна

Ваш MVVM --- это уже MVI, вы просто не знаете об этом. Когда вы собрали все поля экрана в один `data class UiState`, заменили россыпь LiveData на единый StateFlow и начали обрабатывать пользовательские действия через sealed class `UiAction` --- вы де-факто реализовали MVI. Граница между MVVM и MVI на Android стёрлась к 2023 году, но терминология осталась. Этот файл --- не учебник "как написать MVVM". Это карта всех вариаций паттерна, которые существовали с 2017 по 2025 год: от россыпи MutableLiveData до `collectAsStateWithLifecycle` в Compose. Для каждой вариации --- код, проблемы и причины, по которым индустрия двинулась дальше.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Activity Lifecycle | ViewModel привязан к lifecycle --- без этого не понять scoping | [[android-activity-lifecycle]] |
| Архитектурные паттерны | Общий обзор MVC/MVP/MVVM/MVI + UDF | [[android-architecture-patterns]] |
| ViewModel Internals | Как ViewModel переживает rotation, ViewModelStore, SavedStateHandle | [[android-viewmodel-internals]] |
| Kotlin Coroutines | StateFlow, viewModelScope, launch | [[android-coroutines-guide]] |

---

## Истоки MVVM: от Smalltalk до Android

### Presentation Model (Martin Fowler, 2004)

В июле 2004 года Мартин Фаулер опубликовал паттерн **Presentation Model** --- выделение состояния и поведения UI в отдельный класс, независимый от конкретного фреймворка отображения. Presentation Model хранит данные экрана и логику их трансформации, а View подписывается на изменения и синхронизирует себя.

### MVVM (Microsoft, 2005)

В 2005 году архитекторы Microsoft Кен Купер и Тед Петерс адаптировали Presentation Model для WPF (Windows Presentation Foundation), а Джон Госсман опубликовал паттерн под названием **Model-View-ViewModel** в своём блоге. Ключевая идея: WPF предоставлял декларативный data binding (XAML), и ViewModel мог связываться с View автоматически --- без ручных вызовов `view.setText()`. MVVM стал стандартом в мире .NET/WPF/Silverlight.

### MVVM приходит на Android (2017)

До 2017 года Android-сообщество использовало MVC (God Activity) и MVP. На Google I/O 2017 были представлены **Architecture Components**: ViewModel, LiveData, Room, Lifecycle. LiveData --- lifecycle-aware observable, по сути реализация Observer pattern из WPF, адаптированная под Android lifecycle. С этого момента MVVM стал рекомендуемым паттерном.

```
ЭВОЛЮЦИЯ MVVM

2004  Martin Fowler: Presentation Model
  |     "Состояние UI --- отдельный объект"
  |
2005  Microsoft WPF: Model-View-ViewModel
  |     "Presentation Model + Data Binding (XAML)"
  |
2015  Android Data Binding Library (Google)
  |     "Попытка перенести WPF-подход на Android XML"
  |
2017  Architecture Components (Google I/O)
  |     "ViewModel + LiveData = MVVM без WPF-style binding"
  |
2019  Kotlin Coroutines + StateFlow
  |     "LiveData → StateFlow: Kotlin-native reactive streams"
  |
2021  Jetpack Compose 1.0
  |     "collectAsStateWithLifecycle --- declarative binding"
  |
2023  Google: "reduce events to state"
  |     "Manuel Vivo: one-off events --- антипаттерн"
  |
2025  MVVM/MVI конвергенция
        "Single UiState + sealed Actions = неявный MVI"
```

**Ключевой инсайт:** MVVM на Android никогда не был тем же MVVM, что в WPF. В WPF связь View-ViewModel обеспечивал двусторонний data binding. На Android связь обеспечивает Observer pattern (LiveData/StateFlow) + односторонний поток данных (UDF). Android-MVVM ближе к Presentation Model Фаулера, чем к MVVM Госсмана.

---

## Три поколения MVVM на Android

### Поколение 1: Россыпь LiveData (2017--2019)

Первая реакция на Architecture Components --- каждое поле экрана получало свой MutableLiveData. Три LiveData в ViewModel, три `observe` в Activity.

```kotlin
// ===== ПОКОЛЕНИЕ 1: Multiple LiveData fields (2017-2019) =====

class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    // Три отдельных MutableLiveData
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error

    init { loadUsers() }

    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null

            try {
                _users.value = repository.getUsers()
            } catch (e: Exception) {
                _error.value = e.message
            } finally {
                _isLoading.value = false
            }
        }
    }
}

// Activity: три observe-блока --- каждое поле отдельно
class UsersActivity : AppCompatActivity() {
    private val viewModel: UsersViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_users)

        viewModel.isLoading.observe(this) { progressBar.isVisible = it }
        viewModel.users.observe(this) { adapter.submitList(it) }
        viewModel.error.observe(this) { it?.let { msg -> showToast(msg) } }
    }
}
```

**Проблемы поколения 1:**

| Проблема | Описание |
|----------|----------|
| Рассинхронизация | `isLoading = false` может прийти до `users`, и View мигнёт пустым экраном |
| Race conditions | Параллельные запросы обновляют разные LiveData независимо |
| Observe boilerplate | Каждое поле --- отдельный `observe` блок |
| Нет атомарности | Нельзя обновить `isLoading` и `users` одной транзакцией |
| Масштабирование | 10 полей на экране = 10 LiveData + 10 observe |

### Поколение 2: Единый UiState (2019--2021)

Осознание: состояние экрана --- это один снимок (snapshot), а не набор независимых полей. Один `data class UiState` вместо десяти LiveData.

```kotlin
// ===== ПОКОЛЕНИЕ 2: Single UiState + StateFlow (2019-2021) =====

data class UsersUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null
)

class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    init { loadUsers() }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val users = repository.getUsers()
                _uiState.update { it.copy(isLoading = false, users = users) }
            } catch (e: Exception) {
                _uiState.update { it.copy(isLoading = false, error = e.message) }
            }
        }
    }
}

// Activity: один collect вместо трёх observe
class UsersActivity : AppCompatActivity() {
    private val viewModel: UsersViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val binding = ActivityUsersBinding.inflate(layoutInflater)
        setContentView(binding.root)
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    binding.progressBar.isVisible = state.isLoading
                    binding.recyclerView.isVisible = state.users.isNotEmpty()
                    adapter.submitList(state.users)
                    state.error?.let { showSnackbar(it) }
                }
            }
        }
    }
}
```

**Преимущества поколения 2:**
- **Атомарные обновления:** `copy()` создаёт новый снимок целиком --- нет рассинхронизации
- **One source of truth:** одно поле `uiState`, один `collect`
- **Thread-safety:** `MutableStateFlow.update {}` использует CAS (compare-and-set)
- **Тестируемость:** один assert на весь state вместо трёх

### Поколение 3: Compose + StateFlow (2021--2025)

Jetpack Compose устраняет последний boilerplate --- `repeatOnLifecycle` + `collect`. Compose-функция подписывается на StateFlow одной строкой.

```kotlin
// ===== ПОКОЛЕНИЕ 3: Compose + StateFlow (2021-2025) =====

// ViewModel --- тот же, что в поколении 2

// Composable: одна строка подписки
@Composable
fun UsersScreen(viewModel: UsersViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        uiState.isLoading -> {
            Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        }
        uiState.error != null -> {
            ErrorScreen(
                message = uiState.error!!,
                onRetry = viewModel::loadUsers
            )
        }
        else -> {
            UserList(
                users = uiState.users,
                onRefresh = viewModel::loadUsers
            )
        }
    }
}
```

**Преимущества поколения 3:**
- **Lifecycle-safe:** `collectAsStateWithLifecycle` автоматически подписывается/отписывается по lifecycle
- **Нет observer boilerplate:** нет `lifecycleScope.launch { repeatOnLifecycle }` --- одна строка
- **Preview support:** Composable можно рендерить в Preview с фейковым UiState
- **Declarative UI:** View --- чистая функция от State. Нет императивных `binding.progressBar.isVisible`

```
ЭВОЛЮЦИЯ ПОДПИСКИ НА STATE

Gen 1 (2017):  viewModel.isLoading.observe(this) { ... }
               viewModel.users.observe(this) { ... }
               viewModel.error.observe(this) { ... }
               // 3 observe-блока, 3 LiveData

Gen 2 (2019):  lifecycleScope.launch {
                   repeatOnLifecycle(STARTED) {
                       viewModel.uiState.collect { ... }
                   }
               }
               // 1 collect, но boilerplate repeatOnLifecycle

Gen 3 (2021):  val uiState by viewModel.uiState.collectAsStateWithLifecycle()
               // 1 строка. Всё.
```

---

## UiState: архитектура состояния

UiState --- ядро MVVM на Android. Как вы моделируете состояние экрана определяет: можно ли допустить невалидную комбинацию полей, насколько удобен `when`-exhaustiveness check, как работает тестирование. Четыре подхода, каждый --- для своей ситуации.

### Подход 1: Sealed class UiState (Loading / Content / Error)

```kotlin
sealed interface UsersUiState {
    data object Loading : UsersUiState
    data class Content(val users: List<User>) : UsersUiState
    data class Error(val message: String) : UsersUiState
}

class UsersViewModel(private val repository: UserRepository) : ViewModel() {
    private val _uiState = MutableStateFlow<UsersUiState>(UsersUiState.Loading)
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UsersUiState.Loading
            repository.getUsers()
                .onSuccess { _uiState.value = UsersUiState.Content(it) }
                .onFailure { _uiState.value = UsersUiState.Error(it.message ?: "Error") }
        }
    }
}

@Composable
fun UsersScreen(viewModel: UsersViewModel = hiltViewModel()) {
    when (val uiState = viewModel.uiState.collectAsStateWithLifecycle().value) {
        is UsersUiState.Loading -> LoadingIndicator()
        is UsersUiState.Content -> UserList(uiState.users)
        is UsersUiState.Error -> ErrorScreen(uiState.message)
    }
}
```

**Когда использовать:** простые экраны с 2--3 взаимоисключающими состояниями (Loading ИЛИ Content ИЛИ Error).

**Плюсы:** exhaustive `when`, невозможно показать Loading и Error одновременно. **Минусы:** нельзя показать Loading + частичные данные; pull-to-refresh требует хака или четвёртого состояния.

### Подход 2: Data class UiState с флагами

```kotlin
data class UsersUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null,
    val isRefreshing: Boolean = false,
    val searchQuery: String = ""
)

class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            repository.getUsers()
                .onSuccess { users ->
                    _uiState.update { it.copy(isLoading = false, users = users) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                }
        }
    }

    fun refresh() {
        viewModelScope.launch {
            _uiState.update { it.copy(isRefreshing = true) }
            repository.getUsers()
                .onSuccess { _uiState.update { s -> s.copy(isRefreshing = false, users = it) } }
                .onFailure { _uiState.update { s -> s.copy(isRefreshing = false, error = it.message) } }
        }
    }

    fun onSearchQueryChanged(query: String) { _uiState.update { it.copy(searchQuery = query) } }
}
```

**Когда использовать:** сложные экраны с комбинируемыми состояниями --- pull-to-refresh, поиск, пагинация.

**Плюсы:** гибкость, `copy()` обновляет отдельные поля. **Минусы:** невалидные комбинации возможны (`isLoading = true` и `error != null`), нет exhaustive check.

### Подход 3: Nested UiState (вложенные sealed class)

```kotlin
// Для сложного экрана: checkout form
data class CheckoutUiState(
    val deliveryAddress: AddressState = AddressState.Empty,
    val payment: PaymentState = PaymentState.NotSelected,
    val orderSummary: OrderSummaryState = OrderSummaryState.Loading,
    val canSubmit: Boolean = false
)

sealed interface AddressState {
    data object Empty : AddressState
    data class Editing(val address: Address, val errors: List<FieldError>) : AddressState
    data class Confirmed(val address: Address) : AddressState
}

sealed interface PaymentState {
    data object NotSelected : PaymentState
    data class Card(val last4: String, val isDefault: Boolean) : PaymentState
    data class GooglePay(val isAvailable: Boolean) : PaymentState
}

sealed interface OrderSummaryState {
    data object Loading : OrderSummaryState
    data class Ready(val items: List<OrderItem>, val total: Money) : OrderSummaryState
    data class Error(val message: String) : OrderSummaryState
}
```

**Когда использовать:** экраны с несколькими независимыми секциями (checkout, profile editing, multi-step forms). Каждая секция имеет exhaustive when, но обновляется независимо --- баланс типобезопасности и гибкости.

### Подход 4: UiState для списков (item-level state)

```kotlin
data class TaskListUiState(
    val tasks: List<TaskItemUiState> = emptyList(),
    val isLoading: Boolean = false,
    val selectedCount: Int = 0
)

data class TaskItemUiState(
    val id: String,
    val title: String,
    val isCompleted: Boolean,
    val isSelected: Boolean = false,
    val isExpanded: Boolean = false
)

class TaskListViewModel(
    private val repository: TaskRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(TaskListUiState())
    val uiState: StateFlow<TaskListUiState> = _uiState.asStateFlow()

    fun toggleSelection(taskId: String) {
        _uiState.update { state ->
            val updatedTasks = state.tasks.map { task ->
                if (task.id == taskId) task.copy(isSelected = !task.isSelected)
                else task
            }
            state.copy(
                tasks = updatedTasks,
                selectedCount = updatedTasks.count { it.isSelected }
            )
        }
    }

    fun toggleExpanded(taskId: String) {
        _uiState.update { state ->
            state.copy(
                tasks = state.tasks.map { task ->
                    if (task.id == taskId) task.copy(isExpanded = !task.isExpanded)
                    else task
                }
            )
        }
    }
}
```

**Когда использовать:** списки с per-item состоянием (выбор, раскрытие, свайп). Compose LazyColumn перекомпоновывает только изменившиеся item-ы (при правильном `key`).

### Сравнение подходов UiState

```
SEALED CLASS vs DATA CLASS: ДЕРЕВО РЕШЕНИЙ

            Экран имеет 2-3 взаимоисключающих состояния?
                    /                       \
                  ДА                        НЕТ
                  |                          |
          Sealed class               Возможны комбинации?
          Loading/Content/Error      (loading + данные, refresh + данные)
                                      /                 \
                                    ДА                   НЕТ
                                    |                     |
                            Data class             Sealed class
                            с флагами              + подумай ещё раз
                                    |
                            Секции экрана независимы?
                            /                        \
                          ДА                          НЕТ
                          |                            |
                  Nested: data class             Data class
                  + sealed fields                с флагами
```

| Критерий | Sealed class | Data class с флагами | Nested |
|----------|-------------|---------------------|--------|
| Exhaustive when | Компилятор проверяет | Нет | Для каждого sealed-поля |
| Невалидные комбинации | Невозможны | Возможны | Частично невозможны |
| Pull-to-refresh | Неудобно | Естественно | Естественно |
| Количество полей | 0--2 на state | Любое | Любое |
| Тестирование | `is Loading` | Проверка каждого поля | Гибридное |
| Compose Preview | Прямолинейно | Прямолинейно | Требует фабрики |
| Сложность | Низкая | Средняя | Высокая |

---

## Events: великий спор

Как обрабатывать одноразовые эффекты --- навигация, Toast, Snackbar --- главный нерешённый вопрос MVVM на Android. За 8 лет индустрия прошла путь от SingleLiveEvent до рекомендации Google "превращайте всё в state".

### Подход 1: SingleLiveEvent (антипаттерн)

```kotlin
// АНТИПАТТЕРН: SingleLiveEvent (2017-2018)
// Модифицированная LiveData, которая уведомляет observer только один раз.

class SingleLiveEvent<T> : MutableLiveData<T>() {

    private val pending = AtomicBoolean(false)

    @MainThread
    override fun observe(owner: LifecycleOwner, observer: Observer<in T>) {
        super.observe(owner) { t ->
            if (pending.compareAndSet(true, false)) {
                observer.onChanged(t)
            }
        }
    }

    @MainThread
    override fun setValue(t: T?) {
        pending.set(true)
        super.setValue(t)
    }
}

// Использование в ViewModel
class UsersViewModel : ViewModel() {
    private val _navigateToDetail = SingleLiveEvent<String>()
    val navigateToDetail: LiveData<String> = _navigateToDetail

    fun onUserClicked(userId: String) {
        _navigateToDetail.value = userId
    }
}
```

**Почему антипаттерн:**
- Поддерживает только одного observer --- второй Fragment/Activity не получит event
- При configuration change event может потеряться (если pending уже сброшен)
- Google никогда не включал SingleLiveEvent в библиотеку --- это community-хак из Architecture Samples

### Подход 2: Channel для одноразовых эффектов

```kotlin
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    // Channel гарантирует доставку одному потребителю
    private val _effects = Channel<UsersEffect>(Channel.BUFFERED)
    val effects: Flow<UsersEffect> = _effects.receiveAsFlow()

    fun onUserClicked(userId: String) {
        viewModelScope.launch {
            _effects.send(UsersEffect.NavigateToDetail(userId))
        }
    }

    fun onDeleteConfirmed(userId: String) {
        viewModelScope.launch {
            repository.deleteUser(userId)
            _effects.send(UsersEffect.ShowSnackbar("User deleted"))
            loadUsers()
        }
    }
}

sealed interface UsersEffect {
    data class NavigateToDetail(val userId: String) : UsersEffect
    data class ShowSnackbar(val message: String) : UsersEffect
}

// Activity / Composable
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.effects.collect { effect ->
            when (effect) {
                is UsersEffect.NavigateToDetail ->
                    navigator.navigateTo(UserDetailRoute(effect.userId))
                is UsersEffect.ShowSnackbar ->
                    snackbarHostState.showSnackbar(effect.message)
            }
        }
    }
}
```

**Плюсы:** гарантированная однократная доставка (один receiver получит event). Буфер (BUFFERED) не потеряет event во время configuration change, если ViewModel жив.

**Минусы:** Channel --- примитив для одного потребителя. Два Fragment-а не могут слушать один Channel (второй не получит ничего). Manuel Vivo (Google): "A Channel doesn't guarantee the delivery and processing of the events" --- если никто не слушает, event буферизируется, но не обрабатывается.

### Подход 3: SharedFlow с replay=0

```kotlin
class UsersViewModel : ViewModel() {

    private val _effects = MutableSharedFlow<UsersEffect>()
    val effects: SharedFlow<UsersEffect> = _effects.asSharedFlow()

    fun onUserClicked(userId: String) {
        viewModelScope.launch {
            _effects.emit(UsersEffect.NavigateToDetail(userId))
        }
    }
}
```

**Плюсы:** поддерживает множество подписчиков (broadcast). SharedFlow с replay=0 не воспроизводит старые события новым подписчикам.

**Минусы:** если нет активного collector в момент emit --- event потерян безвозвратно. Во время configuration change (Activity пересоздаётся) нет collector-а несколько миллисекунд. Это ненадёжно.

### Подход 4: Google-рекомендация --- "reduce to state" (Manuel Vivo, 2023)

В 2023 году Manuel Vivo (Google DevRel) опубликовал статью "ViewModel: One-off event antipatterns". Суть: **одноразовые события из ViewModel должны быть немедленно превращены в state**. ViewModel --- единственный source of truth, и если он выбрасывает event, который не отражён в state --- он перестаёт быть source of truth.

```kotlin
// ВМЕСТО: _effects.send(NavigateToDetail(userId))
// Google рекомендует: превратить в state

data class UsersUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val navigateToDetail: String? = null,  // <-- event как state
    val userMessage: UserMessage? = null   // <-- snackbar как state
)

data class UserMessage(
    val id: Long,
    val text: String
)

class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    fun onUserClicked(userId: String) {
        _uiState.update { it.copy(navigateToDetail = userId) }
    }

    // View вызывает после обработки навигации
    fun onNavigationHandled() {
        _uiState.update { it.copy(navigateToDetail = null) }
    }

    fun onDeleteConfirmed(userId: String) {
        viewModelScope.launch {
            repository.deleteUser(userId)
            _uiState.update {
                it.copy(
                    userMessage = UserMessage(
                        id = System.currentTimeMillis(),
                        text = "User deleted"
                    )
                )
            }
            loadUsers()
        }
    }

    // View вызывает после показа Snackbar
    fun onMessageShown(messageId: Long) {
        _uiState.update {
            if (it.userMessage?.id == messageId) it.copy(userMessage = null)
            else it
        }
    }
}

// Compose
@Composable
fun UsersScreen(
    viewModel: UsersViewModel = hiltViewModel(),
    onNavigateToDetail: (String) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // Навигация как state
    uiState.navigateToDetail?.let { userId ->
        LaunchedEffect(userId) {
            onNavigateToDetail(userId)
            viewModel.onNavigationHandled()
        }
    }

    // Snackbar как state
    uiState.userMessage?.let { message ->
        val snackbarHostState = remember { SnackbarHostState() }
        LaunchedEffect(message.id) {
            snackbarHostState.showSnackbar(message.text)
            viewModel.onMessageShown(message.id)
        }
    }

    // ... остальной UI
}
```

**Суть:** events исчезают. Всё --- state. Навигация --- `navigateToDetail: String?`. Snackbar --- `userMessage: UserMessage?`. View обрабатывает и вызывает `onHandled()` для сброса.

### Подход 5: Consumed events pattern

Вариация подхода 4: wrapper-класс `Event<T>` с `hasBeenHandled` флагом и `getContentIfNotHandled()`. Явная семантика "одноразовости", но `data class` с мутабельным полем нарушает контракт `equals`/`hashCode`. StateFlow может не увидеть "новый" event, если content тот же. Google не рекомендует.

### Сравнение всех подходов

```
ДЕРЕВО РЕШЕНИЙ: ОБРАБОТКА СОБЫТИЙ

                Событие влияет на UI state?
                    /                \
                  ДА                 НЕТ
                  |                   |
          Reduce to state       Это side-effect?
          (Google-рекомендация)  (навигация, Toast)
                                  /            \
                                ДА              НЕТ
                                |                |
                        Channel +          Пересмотри:
                        receiveAsFlow      скорее всего
                        (прагматичный      это state
                        подход)
```

| Подход | Надёжность | Сложность | Google-рекомендация | Compose support | Multiple observers |
|--------|-----------|-----------|--------------------|-----------------|--------------------|
| SingleLiveEvent | Низкая | Низкая | Нет (антипаттерн) | Плохая | Нет |
| Channel | Средняя | Средняя | Нет (но прагматично) | Хорошая | Нет |
| SharedFlow replay=0 | Низкая | Средняя | Нет | Хорошая | Да |
| Reduce to state | Высокая | Средняя | Да (официально) | Отличная | Да |
| Consumed Event | Средняя | Высокая | Нет | Средняя | Да |

**Прагматический подход (2025):** большинство команд используют гибрид --- state для всего, что можно, Channel для навигации и one-off side effects, которые неудобно выражать через state. Google-рекомендация "reduce to state" идеальна в теории, но `onNavigationHandled()` / `onMessageShown()` добавляют boilerplate, который не все готовы принять.

---

## ViewModel patterns

### SavedStateHandle: переживаем Process Death

ViewModel переживает configuration change, но НЕ переживает process death. Для этого нужен **SavedStateHandle** --- key-value хранилище, которое сериализуется в Bundle.

```kotlin
class SearchViewModel(
    private val savedStateHandle: SavedStateHandle,
    private val repository: SearchRepository
) : ViewModel() {

    // getStateFlow --- восстанавливает значение после process death
    val searchQuery: StateFlow<String> =
        savedStateHandle.getStateFlow("query", "")

    // Реактивная цепочка: query меняется → поиск запускается
    val searchResults: StateFlow<SearchUiState> = searchQuery
        .debounce(300)
        .flatMapLatest { query ->
            if (query.isBlank()) flowOf(SearchUiState.Empty)
            else repository.search(query)
                .map<List<SearchResult>, SearchUiState> { SearchUiState.Results(it) }
                .catch { emit(SearchUiState.Error(it.message ?: "Error")) }
                .onStart { emit(SearchUiState.Loading) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = SearchUiState.Empty
        )

    fun onQueryChanged(query: String) {
        savedStateHandle["query"] = query
    }
}

sealed interface SearchUiState {
    data object Empty : SearchUiState
    data object Loading : SearchUiState
    data class Results(val items: List<SearchResult>) : SearchUiState
    data class Error(val message: String) : SearchUiState
}
```

**Правила SavedStateHandle:**
- Хранить только Parcelable, примитивы, String. Не хранить большие объекты.
- `getStateFlow()` --- реактивно отслеживает изменения ключа (с lifecycle 2.5.0)
- При process death: SavedStateHandle восстанавливает значения → StateFlow получает сохранённый query → цепочка запускает поиск заново
- Максимальный размер Bundle: ~500 KB. Не сохранять списки данных --- только ID и параметры запроса

### Shared ViewModel: Fragment-to-Fragment

```kotlin
// Два Fragment-а общаются через общий ViewModel (Activity scope)

class SharedOrderViewModel : ViewModel() {
    private val _selectedItems = MutableStateFlow<List<MenuItem>>(emptyList())
    val selectedItems: StateFlow<List<MenuItem>> = _selectedItems.asStateFlow()

    fun addItem(item: MenuItem) { _selectedItems.update { it + item } }
    fun removeItem(item: MenuItem) { _selectedItems.update { list -> list - item } }
}

// Fragment A: выбор блюд
class MenuFragment : Fragment() {
    private val sharedViewModel: SharedOrderViewModel by activityViewModels()
    fun onAddToCart(item: MenuItem) { sharedViewModel.addItem(item) }
}

// Fragment B: корзина --- тот же ViewModel через activityViewModels()
class CartFragment : Fragment() {
    private val sharedViewModel: SharedOrderViewModel by activityViewModels()
    // collect sharedViewModel.selectedItems в onViewCreated
}
```

**Когда использовать:** Fragment-ы одного flow с общими данными (заказ, корзина, multi-step wizard). **Когда НЕ использовать:** Fragment-ы из разных feature-модулей --- лучше Navigation arguments или shared data layer.

### ViewModel Scoping

```
SCOPING: ГДЕ ЖИВЁТ VIEWMODEL

┌──────────────────────────────────────────────────────────┐
│                       ACTIVITY                            │
│  ViewModelStoreOwner                                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │              NAVIGATION GRAPH                       │  │
│  │  ViewModelStoreOwner                               │  │
│  │  ┌──────────────────────┐  ┌─────────────────────┐ │  │
│  │  │     FRAGMENT A       │  │    FRAGMENT B        │ │  │
│  │  │  ViewModelStoreOwner │  │ ViewModelStoreOwner  │ │  │
│  │  │                      │  │                      │ │  │
│  │  │  by viewModels()     │  │  by viewModels()     │ │  │
│  │  │  → Fragment scope    │  │  → Fragment scope     │ │  │
│  │  │                      │  │                      │ │  │
│  │  │  by activityVM()     │  │  by activityVM()     │ │  │
│  │  │  → Activity scope    │  │  → Activity scope    │ │  │
│  │  │                      │  │                      │ │  │
│  │  │  by navGraphVM(id)   │  │  by navGraphVM(id)   │ │  │
│  │  │  → NavGraph scope    │  │  → NavGraph scope    │ │  │
│  │  └──────────────────────┘  └─────────────────────┘ │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

| Scope | Делегат | Lifetime | Когда использовать |
|-------|---------|----------|--------------------|
| Fragment | `by viewModels()` | Пока Fragment жив | Локальный state одного экрана |
| Activity | `by activityViewModels()` | Пока Activity жива | Shared state между Fragment-ами |
| NavGraph | `by navGraphViewModels(R.id.graph)` | Пока граф на back stack | Shared state внутри feature flow |
| Compose NavBackStackEntry | `hiltViewModel()` / `viewModel()` | Пока destination на back stack | Default scope в Compose Navigation |

```kotlin
// Compose: ViewModel scoped to Navigation Graph
@Composable
fun OrderNavGraph(navController: NavHostController) {
    val orderViewModel: OrderViewModel = hiltViewModel(
        // Scope ViewModel to the NavBackStackEntry of the parent graph
        viewModelStoreOwner = navController.getBackStackEntry("order_graph")
    )

    NavHost(navController, startDestination = "menu") {
        composable("menu") {
            MenuScreen(orderViewModel = orderViewModel)
        }
        composable("cart") {
            CartScreen(orderViewModel = orderViewModel)
        }
        composable("checkout") {
            CheckoutScreen(orderViewModel = orderViewModel)
        }
    }
}
```

### ViewModel Factory с Hilt

```kotlin
// Стандартный Hilt ViewModel --- @Inject constructor
@HiltViewModel
class UsersViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Hilt автоматически создаёт Factory
    // savedStateHandle предоставляется фреймворком
}

// AssistedInject: для динамических параметров (не из DI)
@HiltViewModel(assistedFactory = UserDetailViewModel.Factory::class)
class UserDetailViewModel @AssistedInject constructor(
    @Assisted private val userId: String,
    private val repository: UserRepository
) : ViewModel() {

    @AssistedFactory
    interface Factory {
        fun create(userId: String): UserDetailViewModel
    }
}

// Использование в Compose
@Composable
fun UserDetailScreen(userId: String) {
    val viewModel = hiltViewModel<UserDetailViewModel, UserDetailViewModel.Factory> { factory ->
        factory.create(userId)
    }
    // ...
}
```

---

## DataBinding, ViewBinding, Compose: эволюция UI binding

### DataBinding (2015--2020): попытка перенести WPF

Google выпустил Data Binding Library в 2015 --- двусторонний binding из WPF на Android XML: `@{viewModel.userName}`, `@={viewModel.searchQuery}`.

**Почему DataBinding стал legacy:** генерация кода замедляла сборку (kapt); ошибки в XML-expressions --- runtime, не compile-time; expression language ограничен; codelab помечен "(Deprecated)"; Compose заменил его полностью.

### ViewBinding (2019--2022): type-safe доступ

ViewBinding --- легковесный: type-safe references (`binding.progressBar`), нет annotation processing, быстрая сборка. Но binding логика --- в Kotlin-коде, не в XML. Нет expression language, нет two-way binding.

### Compose State (2021+): декларативный binding

```kotlin
@Composable
fun UsersScreen(viewModel: UsersViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    // Нет binding. Нет observe. Нет inflate.
    // UI перерисовывается автоматически при изменении state.
    if (uiState.isLoading) CircularProgressIndicator()
    LazyColumn {
        items(uiState.users) { user ->
            UserCard(user = user, onClick = { viewModel.onUserClicked(user.id) })
        }
    }
}
```

### Эволюция binding: сравнение

| Аспект | DataBinding (2015) | ViewBinding (2019) | Compose (2021) |
|--------|-------------------|-------------------|----------------|
| Binding logic | XML expressions | Kotlin code | Composable functions |
| Two-way binding | Да (`@={}`) | Нет | State hoisting |
| Type safety | Частичная (runtime errors) | Полная | Полная |
| Build speed | Медленная (kapt) | Быстрая | Быстрая (Compose compiler) |
| IDE support | Ограниченная | Хорошая | Отличная |
| Тестирование | Сложное | Ручное | ComposeTestRule |
| Status (2025) | Legacy/Deprecated | Maintenance | Recommended |
| Recomposition | Нет (one-time bind) | Ручное | Автоматическая |

---

## Тестирование MVVM

### Правило 1: MainDispatcherRule

ViewModel использует `Dispatchers.Main` через `viewModelScope`. В unit-тестах Main dispatcher не существует. `MainDispatcherRule` заменяет его на `UnconfinedTestDispatcher`:

```kotlin
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) { Dispatchers.setMain(dispatcher) }
    override fun finished(description: Description) { Dispatchers.resetMain() }
}
```

### Unit test ViewModel + StateFlow

```kotlin
class UsersViewModelTest {
    @get:Rule val mainDispatcherRule = MainDispatcherRule()
    private val fakeRepository = FakeUserRepository()

    @Test
    fun `loadUsers success updates state with users`() = runTest {
        val expectedUsers = listOf(User("1", "Alice"), User("2", "Bob"))
        fakeRepository.setUsers(expectedUsers)
        val viewModel = UsersViewModel(fakeRepository)

        viewModel.loadUsers()

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals(expectedUsers, state.users)
        assertNull(state.error)
    }

    @Test
    fun `loadUsers error updates state with error`() = runTest {
        fakeRepository.setShouldFail(true)
        val viewModel = UsersViewModel(fakeRepository)

        viewModel.loadUsers()

        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertTrue(state.users.isEmpty())
        assertNotNull(state.error)
    }
}
```

### Тестирование StateFlow с Turbine

Turbine --- библиотека от Cash App для тестирования Flow. Позволяет assert-ить промежуточные значения, не только финальный `.value`.

```kotlin
// build.gradle.kts
// testImplementation("app.cash.turbine:turbine:1.1.0")

class UsersViewModelTurbineTest {
    @get:Rule val mainDispatcherRule = MainDispatcherRule()
    private val fakeRepository = FakeUserRepository()

    @Test
    fun `loadUsers emits loading then content`() = runTest {
        fakeRepository.setUsers(listOf(User("1", "Alice")))
        val viewModel = UsersViewModel(fakeRepository)

        viewModel.uiState.test {
            val initial = awaitItem()
            assertTrue(initial.isLoading)

            val content = awaitItem()
            assertFalse(content.isLoading)
            assertEquals(1, content.users.size)
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `refresh produces loading then updated content`() = runTest {
        val viewModel = UsersViewModel(fakeRepository)
        viewModel.uiState.test {
            skipItems(2) // Skip init loading + content
            viewModel.loadUsers()
            assertTrue(awaitItem().isLoading)
            assertFalse(awaitItem().isLoading)
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Тестирование one-time effects (Channel)

```kotlin
class UsersViewModelEffectsTest {
    @get:Rule val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `onUserClicked sends NavigateToDetail effect`() = runTest {
        val viewModel = UsersViewModel(FakeUserRepository())
        viewModel.effects.test {
            viewModel.onUserClicked("user-123")
            val effect = awaitItem()
            assertIs<UsersEffect.NavigateToDetail>(effect)
            assertEquals("user-123", effect.userId)
            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Fake Repository вместо Mock

```kotlin
// Fake: реальная реализация с контролируемым поведением.
// Лучше mock: не зависит от Mockito/MockK, проверяет реальное поведение.

class FakeUserRepository : UserRepository {
    private var users: List<User> = emptyList()
    private var shouldFail: Boolean = false

    fun setUsers(users: List<User>) { this.users = users }
    fun setShouldFail(fail: Boolean) { this.shouldFail = fail }

    override suspend fun getUsers(): Result<List<User>> =
        if (shouldFail) Result.failure(RuntimeException("Test error"))
        else Result.success(users)

    override suspend fun deleteUser(userId: String): Result<Unit> =
        if (shouldFail) Result.failure(RuntimeException("Test error"))
        else { users = users.filter { it.id != userId }; Result.success(Unit) }
}
```

---

## MVVM vs MVI: где граница?

### "Your MVVM is already MVI"

Посмотрите на типичный MVVM 2025 года:

```kotlin
// "MVVM" в 2025
data class ProfileUiState(
    val name: String = "",
    val email: String = "",
    val isLoading: Boolean = false,
    val error: String? = null
)

sealed interface ProfileAction {
    data class NameChanged(val name: String) : ProfileAction
    data class EmailChanged(val email: String) : ProfileAction
    data object SaveClicked : ProfileAction
    data object RetryClicked : ProfileAction
}

class ProfileViewModel(
    private val repository: ProfileRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(ProfileUiState())
    val uiState: StateFlow<ProfileUiState> = _uiState.asStateFlow()

    fun onAction(action: ProfileAction) {
        when (action) {
            is ProfileAction.NameChanged ->
                _uiState.update { it.copy(name = action.name) }
            is ProfileAction.EmailChanged ->
                _uiState.update { it.copy(email = action.email) }
            is ProfileAction.SaveClicked -> saveProfile()
            is ProfileAction.RetryClicked -> loadProfile()
        }
    }
    // ...
}
```

Это MVVM? Это MVI? Формально --- MVVM (ViewModel + StateFlow, нет Reducer как чистой функции). Практически --- это MVI: single UiState, sealed Actions, unidirectional data flow. Разница --- только в отсутствии явного Reducer.

### Когда переходить на явный MVI

| Критерий | MVVM достаточно | Явный MVI (Orbit / Circuit) |
|----------|----------------|-----------------------------|
| Экран | 3--5 полей, 2--3 actions | 15+ полей, 10+ actions, middleware |
| Side effects | Простые (навигация, snackbar) | Сложные цепочки, retry, debounce |
| Тестирование | `.value` assert достаточно | Нужен replay действий, time-travel debug |
| Команда | 1--3 человека, единый стиль | 5+ человек, нужен строгий контракт |
| State transitions | Линейные (load → show) | Графовые (state machine с валидацией переходов) |

### Гибридный подход

Прагматичные команды используют MVVM для простых экранов (ProfileScreen, SettingsScreen) и MVI для сложных (ChatScreen, CheckoutFlow). Jetpack ViewModel одинаково работает в обоих случаях --- разница только в организации кода внутри ViewModel.

---

## Мифы и заблуждения

**Миф 1: "MVVM = ViewModel + LiveData"**

Реальность: MVVM --- это архитектурный паттерн (Martin Fowler, 2004), а не конкретная библиотека. Можно реализовать MVVM без LiveData, без ViewModel из Jetpack, даже без Android. Суть MVVM --- View наблюдает за ViewModel через Observer, ViewModel не знает о View. LiveData и Jetpack ViewModel --- инструменты, упрощающие реализацию на Android, но не сам паттерн.

**Миф 2: "LiveData deprecated"**

Реальность: LiveData НЕ deprecated. Библиотека `lifecycle-livedata-ktx` поддерживается и обновляется. Но Google рекомендует StateFlow для новых проектов: StateFlow --- часть Kotlin (не Android), работает в Domain/Data layer, поддерживает `flatMapLatest`, `combine`, `debounce` без обёрток. LiveData остаётся валидным выбором для существующих проектов.

**Миф 3: "ViewModel переживает process death"**

Реальность: ViewModel переживает ТОЛЬКО configuration change (rotation, language change, resize). Process death уничтожает ViewModel полностью. Для выживания при process death нужен `SavedStateHandle`, который сериализует данные в Bundle. Подробности --- [[android-viewmodel-internals]].

**Миф 4: "Один ViewModel на экран --- единственный правильный подход"**

Реальность: Shared ViewModel (`activityViewModels()`, `navGraphViewModels()`) --- валидный паттерн для Fragment-to-Fragment communication и multi-step flows. Compose позволяет создавать ViewModel-ы, привязанные к NavGraph scope. Один экран может использовать несколько ViewModel-ов для разных аспектов (основной state, analytics, feature flags).

**Миф 5: "DataBinding = MVVM"**

Реальность: DataBinding --- опциональный инструмент для связывания View с ViewModel через XML expressions. MVVM прекрасно работает без DataBinding: с ViewBinding, с ручным `observe`/`collect`, и особенно --- с Compose. DataBinding codelab помечен Google как "(Deprecated)". Compose заменил его полностью.

**Миф 6: "Channel --- единственный надёжный способ для one-off effects"**

Реальность: Google (Manuel Vivo, 2023) рекомендует превращать events в state ("reduce to state"). Channel --- прагматичный компромисс, но не единственный и не рекомендованный Google подход. State-based event handling (`navigateToDetail: String? = null` + `onNavigationHandled()`) надёжнее, потому что state не теряется при configuration change.

**Миф 7: "StateFlow заменяет LiveData один к одному"**

Реальность: StateFlow требует начальное значение (LiveData --- нет). StateFlow не lifecycle-aware сам по себе --- нужен `repeatOnLifecycle` или `collectAsStateWithLifecycle`. StateFlow использует equality check (`distinctUntilChanged`) --- если emit тот же объект, collector не получит обновление. LiveData уведомляет при каждом `setValue`. Миграция не тривиальна.

---

## CS-фундамент

| CS-концепция | Как проявляется в MVVM |
|-------------|----------------------|
| **Observer Pattern** | LiveData/StateFlow --- реализация Observer. View подписывается, ViewModel уведомляет. Без Observer MVVM невозможен |
| **State Machine** | `sealed class UiState` --- конечный автомат (Loading → Content, Loading → Error). Переходы определены, невалидные --- невозможны |
| **Unidirectional Data Flow** | State flows DOWN (ViewModel → View), events flow UP (View → ViewModel). Нет циклических зависимостей |
| **Separation of Concerns** | ViewModel: бизнес-логика + state. View: отображение. Repository: данные. Каждый слой --- одна ответственность |
| **Reactive Programming** | StateFlow --- горячий реактивный поток. `combine`, `flatMapLatest`, `map` --- реактивные операторы |
| **Immutability** | UiState --- immutable data class. Новое состояние через `copy()`. Нет мутации --- нет race conditions |
| **Data Binding** | Автоматическая синхронизация ViewModel ↔ View. В WPF через XAML, на Android через DataBinding/Compose |
| **Lifecycle Awareness** | LiveData/`collectAsStateWithLifecycle` --- подписка активна только в safe lifecycle state |
| **CAS (Compare-And-Set)** | `MutableStateFlow.update {}` использует CAS для thread-safe обновлений без lock-ов |

---

## Связь с другими темами

**[[observer-pattern]]** --- LiveData и StateFlow --- реализации Observer pattern. В GoF Observer Subject хранит observers и вызывает `notify()`. LiveData делает то же: уведомляет при `setValue()`, автоматически отписывает при lifecycle event. StateFlow --- hot flow с `combine`, `map`, `flatMapLatest` --- реактивное расширение Observer. Compose `State<T>` --- следующая эволюция: runtime автоматически отслеживает чтения и перекомпоновывает затронутые Composable.

**[[state-pattern]]** --- `sealed class UiState` (Loading/Content/Error) --- это State Machine pattern в чистом виде. Каждое состояние --- отдельный подтип, переходы определены в ViewModel. Kotlin `when` с exhaustive check гарантирует обработку всех состояний. Nested UiState (data class с sealed-полями) --- это иерархический state machine, где каждая секция экрана имеет свой набор состояний.

**[[solid-principles]]** --- SRP: ViewModel --- state + логика, View --- только рендеринг. DIP: ViewModel зависит от `UserRepository` interface, не от реализации --- FakeRepository в тестах. OCP: новое поле в UiState не требует изменения View (Compose перекомпонуется автоматически).

**[[coupling-cohesion]]** --- MVVM минимизирует coupling между View и ViewModel: ViewModel НЕ знает о View (unidirectional dependency). View зависит от ViewModel через Observer --- слабая связь. В MVP coupling был bidirectional (Presenter ↔ View interface). Cohesion растёт: ViewModel содержит только бизнес-логику и state, View --- только rendering.

**[[testing-fundamentals]]** --- ViewModel --- чистый Kotlin-класс, тестируемый без эмулятора. Пирамида: Unit tests (ViewModel + FakeRepository), Integration tests (ViewModel + real Repository + fake DataSource), UI tests (ComposeTestRule). Fake Repository --- стандарт MVVM-тестирования.

**[[mocking-strategies]]** --- Fake вместо Mock: FakeUserRepository --- реальная реализация с контролируемым поведением. Не зависит от Mockito/MockK, проверяет поведение (не вызовы), переиспользуется между тестами. Mock-и --- для edge cases: verify analytics, verify event dispatch.

**[[error-handling]]** --- `Result<T>` --- стандарт передачи успеха/ошибки из Repository в ViewModel. ViewModel преобразует `Result.failure` в `UiState(error = message)`. Sealed class `NetworkError` моделирует типы ошибок (Timeout, NotFound, Unauthorized) с разной реакцией UI. Arrow `Either` --- альтернатива для типизированных ошибок.

**[[functional-programming]]** --- Compose-функция --- чистая функция: `(UiState) -> UI`. Immutable UiState + `copy()` --- immutable data transformation из FP. `combine`, `map`, `flatMapLatest` --- функциональные операторы. MVVM в Compose --- по сути функциональная архитектура.

**[[android-viewmodel-internals]]** --- ViewModel переживает configuration change благодаря `NonConfigurationInstance` и `ViewModelStore`. При rotation Activity уничтожается, но ViewModelStore передаётся новому экземпляру. `onCleared()` --- только при финальном уничтожении. SavedStateHandle сериализуется в Bundle для process death.

**[[android-mvi-deep-dive]]** --- MVI --- эволюция MVVM: explicit Reducer (pure function), strict unidirectional flow, side effects как отдельный канал. MVVM с single UiState + sealed Actions почти неотличим от MVI. Явный MVI (Orbit, Circuit) --- для сложных state machines.

**[[android-compose]]** --- Compose устранил главный boilerplate MVVM --- подписку на state. `collectAsStateWithLifecycle()` заменила `repeatOnLifecycle { collect }`. Snapshot system отслеживает зависимости и перекомпоновывает только затронутые элементы. MVVM + Compose --- самая компактная комбинация на Android 2025.

---

## Источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Guide to App Architecture --- Android Developers](https://developer.android.com/topic/architecture) | Документация | Официальный гайд Google: UI Layer, Data Layer, Domain Layer |
| [UI Layer --- Android Developers](https://developer.android.com/topic/architecture/ui-layer) | Документация | UiState, state holders, ViewModel scoping |
| [UI Events --- Android Developers](https://developer.android.com/topic/architecture/ui-layer/events) | Документация | Обработка user events и ViewModel events |
| [ViewModel One-off Event Antipatterns --- Manuel Vivo](https://medium.com/androiddevelopers/viewmodel-one-off-event-antipatterns-16a1da869b95) | Статья (2023) | Почему Channel и SharedFlow для events --- антипаттерн. "Reduce to state" |
| [Turbine --- Cash App](https://github.com/cashapp/turbine) | Библиотека | Тестирование Flow/StateFlow: awaitItem(), test {} |
| [Migrate from LiveData to StateFlow --- Jose Alcérreca](https://medium.com/androiddevelopers/migrating-from-livedata-to-kotlins-flow-379292f419fb) | Статья | Практический гайд миграции LiveData → StateFlow/SharedFlow |
| [Now in Android (NiA) --- GitHub](https://github.com/android/nowinandroid) | Reference app | Официальный пример Google: MVVM + Compose + Hilt + StateFlow |
| [Martin Fowler --- Presentation Model](https://martinfowler.com/eaaDev/PresentationModel.html) | Статья (2004) | Оригинальный паттерн, из которого вырос MVVM |
| [WPF Apps with MVVM --- Microsoft](https://learn.microsoft.com/en-us/archive/msdn-magazine/2009/february/patterns-wpf-apps-with-the-model-view-viewmodel-design-pattern) | Статья (2009) | MVVM в контексте WPF: как задумывался паттерн |
| [SavedStateHandle --- Android Developers](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-savedstate) | Документация | getStateFlow(), process death survival |

---

## Проверь себя

> [!question]- Почему Google рекомендует "reduce events to state" вместо Channel для one-off effects?
> Channel не гарантирует обработку event-а --- если нет активного collector (например, во время configuration change), event буферизируется, но не обрабатывается View. SharedFlow с replay=0 теряет events без collector-а. State-based подход надёжнее: state всегда доступен последнему значению StateFlow, и при восстановлении View (`collectAsStateWithLifecycle`) View получит актуальный state с pending event. ViewModel остаётся единственным source of truth. Минус: boilerplate `onEventHandled()` для каждого one-off event.

> [!question]- Чем отличается `MutableStateFlow.update {}` от прямого присваивания `.value =`? Когда это критично?
> `update {}` использует CAS (compare-and-set) loop: читает текущее значение, применяет lambda, атомарно записывает результат. Если другой поток изменил значение между чтением и записью --- повторяет. Прямое `.value = newValue` не атомарно для read-modify-write: `_uiState.value = _uiState.value.copy(isLoading = true)` --- между чтением и записью другой coroutine может изменить state, и его изменения потеряются. Критично при параллельных операциях: два `viewModelScope.launch` обновляют разные поля UiState одновременно.

> [!question]- Назовите три ключевых отличия sealed class UiState от data class UiState с флагами. В каком случае выбрать каждый?
> 1. **Exhaustive check**: sealed class заставляет обработать все состояния в `when`; data class --- нет. 2. **Невалидные комбинации**: sealed class делает невозможным `isLoading = true && error != null`; data class допускает. 3. **Гибкость**: data class поддерживает pull-to-refresh (isRefreshing + видимые данные) и partial updates через `copy()`; sealed class --- нет. Выбор: sealed class для простых экранов с 2--3 взаимоисключающими состояниями (Loading/Content/Error). Data class для сложных экранов с комбинируемыми состояниями, фильтрами, пагинацией, pull-to-refresh.

---

## Ключевые карточки

**Q: Какие три поколения MVVM существовали на Android и чем они отличаются?**
A: Gen 1 (2017--2019): множество MutableLiveData полей, множество `observe` блоков, проблема рассинхронизации. Gen 2 (2019--2021): единый `data class UiState` + StateFlow, атомарные обновления через `copy()`, один `collect`. Gen 3 (2021--2025): StateFlow + Compose `collectAsStateWithLifecycle`, одна строка подписки, declarative UI как чистая функция от state.

**Q: Что такое "reduce to state" и почему Google рекомендует этот подход для events?**
A: "Reduce to state" --- превращение one-off events (навигация, snackbar) в поля UiState: `navigateToDetail: String? = null`. View обрабатывает event и вызывает `onHandled()` для сброса. Надёжнее Channel/SharedFlow, потому что state не теряется при configuration change и ViewModel остаётся единственным source of truth.

**Q: Когда использовать SavedStateHandle, а когда обычный StateFlow?**
A: SavedStateHandle --- для данных, которые должны пережить process death (поисковый запрос, выбранный фильтр, ID элемента). Обычный StateFlow --- для данных, которые можно перезагрузить из сети/БД (список пользователей, контент). Правило: если потеря данных при process death раздражает пользователя --- SavedStateHandle. Если данные легко перезапросить --- StateFlow.

**Q: Чем MVVM 2025 года отличается от MVI?**
A: Почти ничем. MVVM с single UiState + sealed class Actions + `onAction()` метод --- это де-факто MVI без явного Reducer. Явный MVI (Orbit, Circuit) добавляет: Reducer как чистую функцию, middleware для side effects, time-travel debug. Граница: MVVM для простых экранов, MVI для сложных state machines.

**Q: Почему DataBinding стал legacy и что его заменило?**
A: DataBinding (2015) --- попытка перенести WPF двусторонний binding на Android XML. Проблемы: генерация кода через kapt (медленная сборка), ошибки в XML expressions только в runtime, ограниченный expression language. Заменён: ViewBinding (2019) для XML --- type-safe без expression language. Compose (2021) --- declarative UI, `collectAsStateWithLifecycle`, автоматическая recomposition. Google codelab по DataBinding помечен "(Deprecated)".

**Q: Как MutableStateFlow.update {} обеспечивает thread-safety?**
A: `update {}` реализован через CAS (compare-and-set) loop: 1) Читает текущее значение. 2) Применяет lambda к нему (`copy(isLoading = true)`). 3) Атомарно пытается записать новое значение. 4) Если между шагами 1 и 3 другой поток изменил значение --- цикл повторяется с новым текущим значением. Это lock-free алгоритм, аналогичный `AtomicReference.updateAndGet()`.

---

## Куда дальше

| Направление | Файл | Зачем |
|------------|------|-------|
| MVI deep-dive | [[android-mvi-deep-dive]] | Следующая эволюция: Reducer, middleware, Orbit/Circuit |
| MVC и MVP | [[android-mvc-mvp]] | Предыдущая эра: почему MVVM заменил MVP |
| ViewModel Internals | [[android-viewmodel-internals]] | ViewModelStore, NonConfigurationInstance, SavedStateHandle --- как это работает внутри |
| Compose state | [[android-state-management]] | State hoisting, remember, derivedStateOf --- state management в Compose |
| Kotlin Flow | [[kotlin-flow]] | StateFlow, SharedFlow, operators --- reactive foundation MVVM |
| Clean Architecture | [[android-clean-architecture]] | Как MVVM вписывается в многослойную архитектуру |
| Repository Pattern | [[android-repository-pattern]] | Откуда ViewModel берёт данные --- Data Layer |
| Эволюция архитектуры | [[android-architecture-evolution]] | Хронологический контекст: God Activity → MVP → MVVM → MVI |
| Observer Pattern | [[observer-pattern]] | CS-фундамент Observer: от GoF до StateFlow |
| State Pattern | [[state-pattern]] | sealed class UiState --- State Machine в действии |
