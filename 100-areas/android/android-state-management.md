---
title: "Android State Management"
created: 2025-01-15
modified: 2026-01-05
cs-foundations: [state-machine, reactive-streams, single-source-of-truth, event-sourcing]
tags:
  - android
  - state
  - stateflow
  - sharedflow
  - channel
  - compose
  - architecture
related:
  - "[[android-viewmodel-internals]]"
  - "[[android-architecture-patterns]]"
  - "[[android-coroutines-mistakes]]"
  - "[[kotlin-flow]]"
---

# Android State Management: StateFlow, SharedFlow, Channel и Compose State

> Как правильно управлять состоянием UI: StateFlow для состояния, Channel для событий

---

## Зачем это нужно

**Проблема:** Android UI имеет сложный lifecycle. Данные должны:
- Переживать rotation (configuration change)
- Не теряться при уходе в background
- Корректно обрабатывать one-time events (toast, navigation)
- Не вызывать memory leaks

**Типичные ошибки без понимания state management:**
- **Toast показывается повторно** после rotation — event хранился в StateFlow
- **Утечка памяти** — observe LiveData в ViewModel
- **Потеря events** — SharedFlow(replay=0) без активного collector
- **Race conditions** — несколько источников изменяют state одновременно

**Решение:** Разделение State и Events:
- **State (StateFlow)** — текущее состояние UI, replay=1, новый подписчик получает последнее значение
- **Events (Channel)** — one-time действия (toast, navigation), каждый collector получает своё

**Результат:** Предсказуемое поведение UI, корректная работа с lifecycle, отсутствие дублирования событий.

### Актуальность 2024-2025

| Год | Рекомендация Google | Статус |
|-----|---------------------|--------|
| 2019 | LiveData | Устарело |
| 2021 | StateFlow + Flow | Текущий стандарт |
| 2024 | StateFlow + SavedStateHandle + Compose | Best Practice |
| 2025 | Molecule + Circuit (эксперименты) | Новые подходы |

**Ключевые изменения:**
- **collectAsStateWithLifecycle()** — стандарт для Compose (добавлен в lifecycle-runtime-compose)
- **SavedStateHandle** — обязателен для выживания process death
- **repeatOnLifecycle** — правильный способ collect в Fragment/Activity
- **MutableStateFlow.update{}** — атомарные обновления (вместо .value =)

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **State** | Текущее состояние UI, долгоживущее |
| **Event** | Одноразовое действие (toast, navigation) |
| **StateFlow** | Hot Flow с текущим значением (replay = 1) |
| **SharedFlow** | Configurable hot Flow (любой replay) |
| **Channel** | Для one-time events (каждый collector получает своё) |
| **LiveData** | Устаревший Android-specific observable |
| **State Hoisting** | Подъём состояния вверх в Compose |
| **UDF** | Unidirectional Data Flow — данные в одном направлении |
| **Side Effect** | Действие, выходящее за пределы Composition |

---

## State vs Events: Ключевое отличие

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      STATE VS EVENTS                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  STATE (состояние)                    EVENTS (одноразовые события)         │
│  ─────────────────                    ────────────────────────────         │
│                                                                             │
│  • Текущее значение                   • Происходит один раз                │
│  • Можно прочитать в любой момент     • Пропущенное = потерянное           │
│  • Новый collector получает           • Новый collector НЕ получает        │
│    последнее значение                   старые события                     │
│  • Сохраняется при rotation           • НЕ должно повторяться              │
│                                                                             │
│  Примеры State:                       Примеры Events:                      │
│  ┌────────────────────────┐           ┌────────────────────────┐           │
│  │ • isLoading: Boolean   │           │ • ShowToast(message)   │           │
│  │ • users: List<User>    │           │ • NavigateTo(screen)   │           │
│  │ • searchQuery: String  │           │ • ShowDialog()         │           │
│  │ • selectedTab: Int     │           │ • HideKeyboard()       │           │
│  │ • error: String?       │           │ • PlaySound()          │           │
│  └────────────────────────┘           └────────────────────────┘           │
│                                                                             │
│  Используйте:                         Используйте:                         │
│  StateFlow                            Channel или SharedFlow(replay=0)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Проблема Events как State

```kotlin
// ❌ ПЛОХО: Event как State
data class UiState(
    val users: List<User> = emptyList(),
    val showToast: String? = null  // ❌ Это event, не state!
)

class BadViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun deleteUser(userId: Long) {
        viewModelScope.launch {
            repository.deleteUser(userId)
            _state.update { it.copy(showToast = "User deleted") }

            // Проблема 1: Как сбросить?
            delay(100)
            _state.update { it.copy(showToast = null) }
            // Проблема 2: Race condition при быстрых кликах
        }
    }
}

@Composable
fun UsersScreen(viewModel: BadViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // Проблема 3: Toast показывается снова при rotation
    state.showToast?.let { message ->
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }
}
```

```kotlin
// ✅ ХОРОШО: Events через Channel
sealed class UiEvent {
    data class ShowToast(val message: String) : UiEvent()
    data class NavigateTo(val route: String) : UiEvent()
}

class GoodViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()

    private val _events = Channel<UiEvent>()
    val events: Flow<UiEvent> = _events.receiveAsFlow()

    fun deleteUser(userId: Long) {
        viewModelScope.launch {
            repository.deleteUser(userId)
            _events.send(UiEvent.ShowToast("User deleted"))
            // Не нужно сбрасывать, Channel сам удаляет после receive
        }
    }
}

@Composable
fun UsersScreen(viewModel: GoodViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val context = LocalContext.current

    // Обработка events — не повторяется при rotation
    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowToast -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
                is UiEvent.NavigateTo -> {
                    // Navigate
                }
            }
        }
    }
}
```

---

## StateFlow vs SharedFlow vs Channel

### Сравнение

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  STATEFLOW VS SHAREDFLOW VS CHANNEL                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                     StateFlow       SharedFlow       Channel                │
│  ────────────────────────────────────────────────────────────────────────  │
│  Hot/Cold           Hot             Hot              Hot                   │
│                                                                             │
│  Имеет текущее      ✅ Да           Зависит от      ❌ Нет                 │
│  значение           (.value)        replay                                 │
│                                                                             │
│  Replay             1 (всегда)      Настраивается    0                     │
│  (для новых                         (0, 1, N)                              │
│  collectors)                                                                │
│                                                                             │
│  Множественные      Все получают    Все получают    Каждый получает       │
│  collectors         одинаково       одинаково        своё (fan-out)        │
│                                                                             │
│  Conflation         Да (только      Настраивается   Нет                   │
│  (пропуск старых)   последнее)      (onBufferOverflow)                    │
│                                                                             │
│  Null значения      ❌ Нет           ✅ Да            ✅ Да                  │
│                                                                             │
│  Использование      UI State        Hot events,      One-time events      │
│                                     broadcast                              │
│                                                                             │
│  Пример             isLoading,      Location         ShowToast,           │
│                     users           updates          Navigate             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### StateFlow

```kotlin
// StateFlow — для UI State
class UsersViewModel : ViewModel() {

    // Создание
    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    // Обновление через update (atomic)
    fun setLoading(isLoading: Boolean) {
        _uiState.update { currentState ->
            currentState.copy(isLoading = isLoading)
        }
    }

    // Или через value (не atomic)
    fun setLoadingUnsafe(isLoading: Boolean) {
        _uiState.value = _uiState.value.copy(isLoading = isLoading)
        // ⚠️ Race condition если несколько coroutines обновляют
    }

    // Получение текущего значения
    fun getCurrentUsers(): List<User> {
        return _uiState.value.users
    }
}

// Collect в Compose
@Composable
fun UsersScreen(viewModel: UsersViewModel) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // uiState автоматически обновляется
    if (uiState.isLoading) {
        LoadingIndicator()
    }
}

// Collect в Activity/Fragment
class UsersFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    // Update UI
                }
            }
        }
    }
}
```

### SharedFlow

```kotlin
// SharedFlow — для broadcast events
class LocationService {

    // Все collectors получают одинаковые updates
    private val _locationUpdates = MutableSharedFlow<Location>(
        replay = 1,  // Новый collector получает последнее значение
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val locationUpdates: SharedFlow<Location> = _locationUpdates.asSharedFlow()

    suspend fun emitLocation(location: Location) {
        _locationUpdates.emit(location)
    }
}

// SharedFlow для events (replay = 0)
class AnalyticsManager {

    private val _events = MutableSharedFlow<AnalyticsEvent>(
        replay = 0,  // Пропущенные events потеряны
        extraBufferCapacity = 64,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<AnalyticsEvent> = _events.asSharedFlow()

    // Все subscribers получают event
    suspend fun track(event: AnalyticsEvent) {
        _events.emit(event)
    }
}
```

### Channel

```kotlin
// Channel — для one-time events (fan-out)
class UsersViewModel : ViewModel() {

    // Каждый event получает только один collector
    private val _events = Channel<UiEvent>(Channel.BUFFERED)
    val events: Flow<UiEvent> = _events.receiveAsFlow()

    fun showToast(message: String) {
        viewModelScope.launch {
            _events.send(UiEvent.ShowToast(message))
        }
    }

    // Или без suspend (если не нужно ждать)
    fun showToastTrySend(message: String) {
        _events.trySend(UiEvent.ShowToast(message))
    }
}

// Collect events
@Composable
fun UsersScreen(viewModel: UsersViewModel) {
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowToast -> {
                    Toast.makeText(context, event.message, Toast.LENGTH_SHORT).show()
                }
            }
        }
    }
}
```

---

## LiveData vs StateFlow

### Почему StateFlow лучше для новых проектов

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     LIVEDATA VS STATEFLOW                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                        LiveData              StateFlow                      │
│  ───────────────────────────────────────────────────────────────────────   │
│  Платформа            Android-only           Kotlin Multiplatform           │
│                                                                             │
│  Null значения        ✅ Да                   ❌ Нет                         │
│                       (может быть null)       (начальное обязательно)       │
│                                                                             │
│  Начальное значение   Опционально             Обязательно                   │
│                                                                             │
│  Трансформации        Transformations.map()   flow operators                │
│                       (ограничены)            (богатый набор)               │
│                                                                             │
│  Combine              MediatorLiveData        combine() operator            │
│                       (boilerplate)           (простой)                     │
│                                                                             │
│  Testing              InstantTaskExecutor     runTest                       │
│                       Rule нужен              (стандартный)                  │
│                                                                             │
│  Lifecycle aware      Автоматически           repeatOnLifecycle             │
│                                               (явно)                        │
│                                                                             │
│  distinctUntilChanged Нет (по умолчанию)      Да (встроен)                  │
│                                                                             │
│  debounce, map, etc.  Нет                     Да (flow operators)           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Миграция с LiveData на StateFlow

```kotlin
// LiveData (старый код)
class OldViewModel : ViewModel() {
    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    fun loadUsers() {
        _isLoading.value = true
        viewModelScope.launch {
            _users.value = repository.getUsers()
            _isLoading.value = false
        }
    }
}

// StateFlow (новый код)
class NewViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            val users = repository.getUsers()
            _uiState.update { it.copy(isLoading = false, users = users) }
        }
    }
}

data class UsersUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList()
)

// Observe в Fragment
// LiveData
viewModel.users.observe(viewLifecycleOwner) { users ->
    // Update UI
}

// StateFlow
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state ->
            // Update UI
        }
    }
}

// Compose (одинаково для обоих)
// LiveData
val users by viewModel.users.observeAsState(emptyList())

// StateFlow
val state by viewModel.uiState.collectAsStateWithLifecycle()
```

---

## Compose State Management

### State Hoisting

```kotlin
// State Hoisting — подъём состояния вверх
// Composable становится stateless → легко тестировать и переиспользовать

// ❌ ПЛОХО: State внутри Composable
@Composable
fun BadSearchBar() {
    var query by remember { mutableStateOf("") }  // State внутри

    TextField(
        value = query,
        onValueChange = { query = it }
    )
    // Нельзя контролировать извне
    // Сложно тестировать
}

// ✅ ХОРОШО: State hoisted
@Composable
fun GoodSearchBar(
    query: String,                    // State приходит сверху
    onQueryChange: (String) -> Unit   // Events уходят вверх
) {
    TextField(
        value = query,
        onValueChange = onQueryChange
    )
}

// Использование
@Composable
fun SearchScreen(viewModel: SearchViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    GoodSearchBar(
        query = state.query,
        onQueryChange = viewModel::onQueryChange
    )
}
```

### remember vs rememberSaveable

```kotlin
@Composable
fun ExampleScreen() {
    // remember — сохраняет при recomposition
    // Теряется при configuration change!
    var count1 by remember { mutableStateOf(0) }

    // rememberSaveable — сохраняет при configuration change
    // Использует onSaveInstanceState
    var count2 by rememberSaveable { mutableStateOf(0) }

    // Для сложных объектов нужен Saver
    var user by rememberSaveable(stateSaver = UserSaver) {
        mutableStateOf(User.default())
    }

    Column {
        Text("remember: $count1")      // Сбросится при rotation
        Text("rememberSaveable: $count2")  // Сохранится
    }
}

// Custom Saver
val UserSaver = run {
    val idKey = "id"
    val nameKey = "name"

    mapSaver(
        save = { mapOf(idKey to it.id, nameKey to it.name) },
        restore = { User(it[idKey] as Long, it[nameKey] as String) }
    )
}
```

### derivedStateOf

```kotlin
@Composable
fun FilteredList(
    items: List<Item>,
    searchQuery: String
) {
    // ❌ ПЛОХО: пересчитывается при каждом recomposition
    val filteredItems = items.filter { it.name.contains(searchQuery) }

    // ✅ ХОРОШО: пересчитывается только при изменении items или searchQuery
    val filteredItems by remember(items, searchQuery) {
        derivedStateOf {
            items.filter { it.name.contains(searchQuery) }
        }
    }

    LazyColumn {
        items(filteredItems) { item ->
            ItemRow(item)
        }
    }
}
```

### produceState

```kotlin
// Конвертация Flow в Compose State
@Composable
fun UserProfile(userId: Long) {
    // produceState для async операций
    val user by produceState<User?>(initialValue = null, userId) {
        value = repository.getUser(userId)
    }

    // Или через collectAsStateWithLifecycle
    val userFlow = remember(userId) {
        repository.getUserFlow(userId)
    }
    val user by userFlow.collectAsStateWithLifecycle(initialValue = null)

    user?.let { UserCard(it) }
}
```

---

## Side Effects в Compose

### LaunchedEffect

```kotlin
// LaunchedEffect — для coroutines в Compose
@Composable
fun UserScreen(userId: Long) {
    // Запускается когда userId меняется
    LaunchedEffect(userId) {
        // Coroutine отменяется при выходе из composition
        // или когда userId меняется
        viewModel.loadUser(userId)
    }

    // Для one-time setup (Unit не меняется)
    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            // Handle events
        }
    }
}
```

### SideEffect и DisposableEffect

```kotlin
// SideEffect — вызывается после каждого successful recomposition
@Composable
fun AnalyticsScreen(screenName: String) {
    SideEffect {
        // Не suspend, выполняется синхронно
        analytics.setCurrentScreen(screenName)
    }
}

// DisposableEffect — с cleanup
@Composable
fun LocationScreen() {
    val context = LocalContext.current

    DisposableEffect(Unit) {
        val locationManager = context.getSystemService<LocationManager>()
        val listener = LocationListener { /* ... */ }

        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            1000L,
            10f,
            listener
        )

        onDispose {
            // Cleanup при выходе из composition
            locationManager.removeUpdates(listener)
        }
    }
}
```

### rememberCoroutineScope

```kotlin
// Для launch из callbacks (onClick и т.д.)
@Composable
fun ButtonScreen() {
    val scope = rememberCoroutineScope()

    Button(
        onClick = {
            scope.launch {
                // Coroutine привязан к lifecycle Composable
                doSomethingSuspend()
            }
        }
    ) {
        Text("Click me")
    }
}
```

---

## SavedStateHandle и Process Death

### Проблема Process Death

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROCESS DEATH LIFECYCLE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Сценарий: Пользователь сворачивает приложение, система убивает процесс    │
│                                                                             │
│  App → Background → System kills process → User returns → App recreated    │
│                                                                             │
│  ЧТО СОХРАНЯЕТСЯ:                                                          │
│  ├── onSaveInstanceState() Bundle ✅                                        │
│  ├── SavedStateHandle ✅                                                    │
│  ├── rememberSaveable ✅                                                    │
│  └── Persistent storage (Room, DataStore) ✅                               │
│                                                                             │
│  ЧТО ТЕРЯЕТСЯ:                                                             │
│  ├── ViewModel data (если не в SavedStateHandle) ❌                         │
│  ├── remember { } ❌                                                        │
│  ├── In-memory cache ❌                                                     │
│  └── StateFlow/LiveData values ❌                                           │
│                                                                             │
│  ВАЖНО: Configuration change (rotation) НЕ убивает ViewModel!              │
│         Process death УБИВАЕТ ViewModel полностью!                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### SavedStateHandle

```kotlin
// SavedStateHandle — интеграция ViewModel с onSaveInstanceState
class SearchViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // Способ 1: Делегат (рекомендуется для простых типов)
    var searchQuery: String by savedStateHandle.saveable { "" }

    // Способ 2: StateFlow из SavedStateHandle (2024 best practice)
    private val _searchQuery = savedStateHandle.getStateFlow("query", "")
    val searchQuery: StateFlow<String> = _searchQuery

    fun updateQuery(query: String) {
        savedStateHandle["query"] = query  // Автоматически сохраняется
    }

    // Способ 3: MutableStateFlow с синхронизацией
    private val _uiState = MutableStateFlow(
        savedStateHandle.get<SearchUiState>("state") ?: SearchUiState()
    )
    val uiState: StateFlow<SearchUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            _uiState.collect { state ->
                savedStateHandle["state"] = state  // Сохраняем при каждом изменении
            }
        }
    }
}

// Hilt integration
@HiltViewModel
class HiltSearchViewModel @Inject constructor(
    private val repository: SearchRepository,
    private val savedStateHandle: SavedStateHandle  // Автоматически inject
) : ViewModel() {
    // ...
}
```

### Ограничения SavedStateHandle

```kotlin
// ⚠️ ОГРАНИЧЕНИЯ SavedStateHandle
// Только простые типы и Parcelable/Serializable

// ✅ Поддерживается
savedStateHandle["id"] = 123L                  // Long
savedStateHandle["name"] = "John"              // String
savedStateHandle["items"] = arrayListOf(1, 2)  // ArrayList
savedStateHandle["user"] = userParcelable      // Parcelable

// ❌ НЕ поддерживается напрямую
savedStateHandle["list"] = listOf(1, 2, 3)     // List → конвертировать в ArrayList
savedStateHandle["set"] = setOf("a", "b")      // Set → конвертировать
savedStateHandle["largeData"] = bigBitmap      // Большие данные → в storage

// Лимит Bundle: ~500KB (TransactionTooLargeException)

// Для сложных объектов — Parcelable
@Parcelize
data class SearchUiState(
    val query: String = "",
    val filters: List<Filter> = emptyList()
) : Parcelable
```

### Полный паттерн с Process Death

```kotlin
// Современный подход: StateFlow + SavedStateHandle + Room

@HiltViewModel
class UsersViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // UI State переживает process death
    private val searchQuery = savedStateHandle.getStateFlow("search", "")
    private val selectedFilter = savedStateHandle.getStateFlow("filter", Filter.ALL)

    // Данные из Room (переживают всё)
    private val usersFlow = repository.getUsersFlow()

    // Combine: reactive UI state
    val uiState: StateFlow<UsersUiState> = combine(
        searchQuery,
        selectedFilter,
        usersFlow
    ) { query, filter, users ->
        UsersUiState(
            searchQuery = query,
            filter = filter,
            users = users
                .filter { it.name.contains(query, ignoreCase = true) }
                .filter { filter.matches(it) },
            isLoading = false
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = UsersUiState(isLoading = true)
    )

    // Actions
    fun onSearchQueryChange(query: String) {
        savedStateHandle["search"] = query
    }

    fun onFilterChange(filter: Filter) {
        savedStateHandle["filter"] = filter
    }
}
```

### Тестирование Process Death

```kotlin
// Как протестировать process death:

// Способ 1: Developer Options → Don't keep activities
// Settings → Developer Options → Don't keep activities ✓

// Способ 2: ADB команда
// adb shell am kill com.example.app

// Способ 3: Android Studio Profiler → Terminate Process

// Способ 4: Программно (для unit tests)
@Test
fun `state survives process death`() = runTest {
    // Given: ViewModel с начальным состоянием
    val savedStateHandle = SavedStateHandle(
        mapOf("query" to "test")
    )
    val viewModel = SearchViewModel(savedStateHandle)

    // When: "Process death" — создаём новый ViewModel с тем же handle
    val newSavedStateHandle = SavedStateHandle(
        savedStateHandle.keys().associateWith { savedStateHandle.get<Any>(it) }
    )
    val restoredViewModel = SearchViewModel(newSavedStateHandle)

    // Then: State восстановлен
    assertEquals("test", restoredViewModel.searchQuery.value)
}
```

---

## Паттерны State Management

### Single State vs Multiple States

```kotlin
// Подход 1: Single UiState (рекомендуется)
data class UsersUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val searchQuery: String = "",
    val error: String? = null,
    val selectedUserId: Long? = null
)

class UsersViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()
}

// Преимущества:
// + Атомарные обновления (всё или ничего)
// + Легко тестировать (один assert)
// + Нет рассинхрона между states

// Недостатки:
// - Большой data class для сложных экранов
// - Частые recomposition всего UI


// Подход 2: Multiple StateFlows
class UsersViewModel : ViewModel() {
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error.asStateFlow()
}

// Преимущества:
// + Granular updates (меньше recomposition)
// + Проще для простых экранов

// Недостатки:
// - Возможен рассинхрон (isLoading=false, users=old)
// - Сложнее тестировать
// - Boilerplate
```

### Sealed Class State

```kotlin
// Подход 3: Sealed class для mutually exclusive states
sealed class UsersUiState {
    object Loading : UsersUiState()
    data class Success(val users: List<User>) : UsersUiState()
    data class Error(val message: String) : UsersUiState()
}

class UsersViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UsersUiState>(UsersUiState.Loading)
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UsersUiState.Loading

            repository.getUsers()
                .onSuccess { _uiState.value = UsersUiState.Success(it) }
                .onFailure { _uiState.value = UsersUiState.Error(it.message ?: "Error") }
        }
    }
}

@Composable
fun UsersScreen(viewModel: UsersViewModel) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    when (state) {
        is UsersUiState.Loading -> LoadingIndicator()
        is UsersUiState.Success -> UserList((state as UsersUiState.Success).users)
        is UsersUiState.Error -> ErrorMessage((state as UsersUiState.Error).message)
    }
}

// Преимущества:
// + Явные состояния
// + Exhaustive when (compiler проверяет)
// + Нет impossible states (isLoading=true + error!=null)

// Недостатки:
// - Сложнее для комбинированных состояний
// - Smart cast или is check нужен
```

### Combine для сложных states

```kotlin
class SearchViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val searchQuery = MutableStateFlow("")
    private val sortOrder = MutableStateFlow(SortOrder.NAME)
    private val filterActive = MutableStateFlow(false)

    // Combine multiple flows
    val uiState: StateFlow<SearchUiState> = combine(
        searchQuery,
        sortOrder,
        filterActive,
        repository.getUsersFlow()
    ) { query, order, active, users ->
        val filtered = users
            .filter { it.name.contains(query, ignoreCase = true) }
            .filter { if (active) it.isActive else true }
            .sortedWith(order.comparator)

        SearchUiState(
            query = query,
            sortOrder = order,
            filterActive = active,
            users = filtered
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = SearchUiState()
    )

    fun onQueryChange(query: String) {
        searchQuery.value = query
    }

    fun onSortOrderChange(order: SortOrder) {
        sortOrder.value = order
    }
}
```

---

## Common Mistakes и Anti-patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STATE MANAGEMENT ANTI-PATTERNS                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❌ 1. Mutable collections в State                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  data class UiState(                                                │   │
│  │      val users: MutableList<User> = mutableListOf()  // ❌          │   │
│  │  )                                                                  │   │
│  │                                                                     │   │
│  │  // Проблема: мутация не триггерит recomposition                   │   │
│  │  _state.value.users.add(newUser)  // UI не обновится!              │   │
│  │                                                                     │   │
│  │  // ✅ Решение: immutable collections                              │   │
│  │  data class UiState(val users: List<User> = emptyList())           │   │
│  │  _state.update { it.copy(users = it.users + newUser) }             │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ❌ 2. Collect без lifecycle awareness                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // ❌ Утечка памяти, collect продолжается в background            │   │
│  │  lifecycleScope.launch {                                            │   │
│  │      viewModel.uiState.collect { state ->                           │   │
│  │          updateUI(state)                                            │   │
│  │      }                                                              │   │
│  │  }                                                                  │   │
│  │                                                                     │   │
│  │  // ✅ Правильно                                                   │   │
│  │  lifecycleScope.launch {                                            │   │
│  │      repeatOnLifecycle(Lifecycle.State.STARTED) {                   │   │
│  │          viewModel.uiState.collect { state ->                       │   │
│  │              updateUI(state)                                        │   │
│  │          }                                                          │   │
│  │      }                                                              │   │
│  │  }                                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ❌ 3. Event как State                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  data class UiState(                                                │   │
│  │      val showToast: String? = null,  // ❌ Это event!              │   │
│  │      val navigateTo: String? = null  // ❌ Это event!              │   │
│  │  )                                                                  │   │
│  │                                                                     │   │
│  │  // ✅ Решение: Channel для events                                 │   │
│  │  sealed class UiEvent {                                             │   │
│  │      data class ShowToast(val message: String) : UiEvent()          │   │
│  │  }                                                                  │   │
│  │  private val _events = Channel<UiEvent>()                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ❌ 4. State update не через update/copy                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // ❌ Race condition                                              │   │
│  │  _state.value = _state.value.copy(isLoading = true)                 │   │
│  │                                                                     │   │
│  │  // ✅ Атомарное обновление                                        │   │
│  │  _state.update { it.copy(isLoading = true) }                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ❌ 5. SharedFlow вместо Channel для one-time events                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // ❌ Если 2 collectors — оба получат toast                       │   │
│  │  private val _events = MutableSharedFlow<UiEvent>()                 │   │
│  │                                                                     │   │
│  │  // ✅ Channel — только один collector получит                     │   │
│  │  private val _events = Channel<UiEvent>()                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Decision Tree: Что использовать

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     DECISION TREE: STATE MANAGEMENT                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Нужно хранить текущее состояние UI?                                       │
│  ├── ДА ─────────────────────────────────────────────────────────┐         │
│  │                                                               │         │
│  │   Нужен null как валидное значение?                          │         │
│  │   ├── ДА → SharedFlow(replay=1) или StateFlow<T?>            │         │
│  │   │                                                           │         │
│  │   └── НЕТ → StateFlow (рекомендуется)                        │         │
│  │                                                               │         │
│  └── НЕТ (это event) ────────────────────────────────────────────┤         │
│                                                                   │         │
│      Несколько collectors должны получить?                        │         │
│      ├── ДА → SharedFlow(replay=0)                               │         │
│      │        (broadcast events, analytics)                      │         │
│      │                                                           │         │
│      └── НЕТ → Channel (рекомендуется для UI events)            │         │
│                (toast, navigation)                               │         │
│                                                                             │
│                                                                             │
│  Для Compose:                                                               │
│  ├── State с ViewModel → collectAsStateWithLifecycle()                     │
│  ├── Local UI state → remember { mutableStateOf() }                        │
│  ├── Survive rotation → rememberSaveable { mutableStateOf() }              │
│  └── Expensive computation → derivedStateOf                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "LiveData устарел" | LiveData всё ещё поддерживается и работает. StateFlow рекомендуется для новых проектов из-за KMP и операторов Flow, но LiveData не deprecated. Миграция не обязательна. |
| "StateFlow заменяет все LiveData use cases" | StateFlow требует начальное значение, что не всегда нужно. Для nullable-by-design используйте `stateIn()` с `SharingStarted.WhileSubscribed()` или оберните в sealed class. |
| "SharedFlow с replay=1 = StateFlow" | **Почти, но не совсем.** StateFlow имеет distinctUntilChanged встроенный, SharedFlow(replay=1) — нет. StateFlow требует initial value, SharedFlow — нет. Семантика разная. |
| "Channel — лучший способ для events" | Channel имеет проблемы: events теряются если collector не активен. Лучше использовать SharedFlow(replay=0) + Lifecycle для one-time events, или Orbit MVI pattern. |
| "ViewModel.viewModelScope достаточно для всего" | viewModelScope cancels при ViewModel.onCleared(). Для операций, которые должны пережить ViewModel (например, запись в БД), используйте ProcessLifecycleOwner или WorkManager. |
| "remember сохраняет между rotations" | `remember` сохраняет только между recompositions. Для rotation/process death используйте `rememberSaveable`. Для ViewModel state — `SavedStateHandle`. |
| "SavedStateHandle переживает process death навсегда" | SavedStateHandle сохраняет только при Activity.onStop(). Если process death произошёл во время активной работы — данные не сохранятся. Критичные данные → persistent storage. |
| "Compose State и ViewModel State — одно и то же" | **Разные уровни.** Compose State (remember) — для UI-only state (scroll position, expanded state). ViewModel State — для business state, переживающего config changes. |
| "MutableStateFlow thread-safe, можно писать из любого потока" | Да, но `update {}` atomicity гарантируется только для одной операции. Для сложных multi-step updates нужна дополнительная синхронизация или Mutex. |
| "collectAsStateWithLifecycle заменяет repeatOnLifecycle" | `collectAsStateWithLifecycle` — для Compose UI. `repeatOnLifecycle` — для View system. В Compose используйте первое, в View/Fragment — второе. |

---

## CS-фундамент

| CS-концепция | Применение в State Management |
|--------------|-------------------------------|
| **Observer pattern** | StateFlow/LiveData — это Observable. Collectors/Observers подписываются и получают updates. Отписка при уничтожении lifecycle owner. |
| **Unidirectional Data Flow** | State flows вниз (ViewModel → UI), Events вверх (UI → ViewModel). Предсказуемость, легче debugging, нет циклов. |
| **Immutability** | State должен быть immutable (`val`, `copy()`). Мутация коллекций не триггерит updates. Новый объект = новое notification. |
| **State Machine** | UI State = finite set of states (Loading, Success, Error). Transitions управляются events. MVI формализует это. |
| **Memoization** | `derivedStateOf` = memoization с automatic invalidation. Пересчитывает только при изменении зависимостей. |
| **Serialization** | SavedStateHandle сериализует state в Bundle (Parcelable/Serializable). Ограничение 1MB. Для больших данных — persistent storage. |
| **Hot vs Cold streams** | StateFlow = Hot (всегда активен, имеет current value). Flow = Cold (выполняется при collect). SharedFlow = Hot multicast. |
| **Backpressure** | StateFlow conflated — только последнее значение. Channel и Flow имеют buffer strategies (SUSPEND, DROP_OLDEST, DROP_LATEST). |
| **Reference equality vs Structural equality** | StateFlow использует `equals()` для distinctUntilChanged. Compose State — reference equality для skipping. Выбор влияет на recomposition. |
| **Publish-Subscribe** | SharedFlow = pub-sub pattern. Один publisher, multiple subscribers. replay определяет сколько событий получат новые subscribers. |

---

## Проверь себя

### Вопросы для самопроверки

1. **В чём разница между State и Event?**
   - State: текущее значение, можно прочитать когда угодно, replay для новых collectors
   - Event: происходит один раз, пропущенное потеряно, не должно повторяться

2. **Почему StateFlow лучше LiveData для новых проектов?**
   - Kotlin Multiplatform
   - Богатые flow operators (map, combine, debounce)
   - Проще тестировать
   - Встроенный distinctUntilChanged

3. **Когда использовать Channel вместо SharedFlow?**
   - Для one-time events (toast, navigation)
   - Когда нужен fan-out (каждый collector получает своё)
   - Когда event должен быть обработан ровно один раз

4. **Что такое State Hoisting в Compose?**
   - Подъём состояния вверх по иерархии
   - Composable становится stateless (принимает state как параметр)
   - Упрощает тестирование и переиспользование

5. **Почему нельзя использовать mutable collections в State?**
   - Мутация не триггерит recomposition
   - StateFlow сравнивает references, а не содержимое
   - Нужно создавать новую коллекцию через copy

---

## Связи

- **[[android-viewmodel-internals]]** — ViewModel как holder для State
- **[[android-architecture-patterns]]** — MVVM/MVI паттерны
- **[[android-coroutines-mistakes]]** — ошибки с Flow и coroutines
- **[[kotlin-flow]]** — детали Flow API
- **[[android-bundle-parcelable]]** — Bundle internals, savedInstanceState механизм, SavedStateHandle и путь данных через system_server

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) | Docs | Основы StateFlow vs SharedFlow |
| 2 | [Compose State](https://developer.android.com/jetpack/compose/state) | Docs | State hoisting, remember |
| 3 | [Side Effects in Compose](https://developer.android.com/jetpack/compose/side-effects) | Docs | LaunchedEffect, DisposableEffect |
| 4 | [A safer way to collect flows](https://medium.com/androiddevelopers/a-safer-way-to-collect-flows-from-android-uis-23080b1f8bda) | Article | repeatOnLifecycle best practices |
| 5 | [Saved State module for ViewModel](https://developer.android.com/topic/libraries/architecture/viewmodel-savedstate) | Docs | SavedStateHandle API |
| 6 | [Handle configuration changes](https://developer.android.com/guide/topics/resources/runtime-changes) | Docs | Configuration change vs process death |
| 7 | [Save UI states](https://developer.android.com/topic/libraries/architecture/saving-states) | Docs | Полный гайд по сохранению состояния |
| 8 | [LiveData vs StateFlow](https://proandroiddev.com/livedata-vs-stateflow-6a9f0387c2e7) | Article | Сравнение подходов |
| 9 | [Reddit: SavedStateHandle experiences](https://reddit.com/r/androiddev) | Community | Практические кейсы |
| 10 | [Compose lifecycle](https://developer.android.com/jetpack/compose/lifecycle) | Docs | Lifecycle-aware state collection |
| 11 | [collectAsStateWithLifecycle](https://developer.android.com/reference/kotlin/androidx/lifecycle/compose/package-summary) | Docs | API reference |
| 12 | [Molecule by Cash App](https://github.com/cashapp/molecule) | GitHub | Альтернативный подход 2024 |

---

*Проверено: 2026-01-09 | Обновлено с Мифами и CS-фундаментом*
