---
title: "Архитектура приложения: MVVM, MVI, Clean Architecture"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/architecture
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-compose]]"
  - "[[android-data-persistence]]"
  - "[[design-patterns]]"
  - "[[clean-code-solid]]"
  - "[[kotlin-flow]]"
cs-foundations: [separation-of-concerns, unidirectional-data-flow, dependency-inversion, layered-architecture]
---

# Архитектура приложения: MVVM, MVI, Clean Architecture

Архитектура определяет, как организован код приложения: где хранится state, как компоненты взаимодействуют, как тестировать логику. **MVVM** — рекомендуемый Google паттерн для Android. **MVI** добавляет unidirectional data flow. **Clean Architecture** разделяет приложение на независимые слои.

> **Prerequisites:**
> - [[android-architecture]] — понимание слоёв архитектуры
> - [[android-activity-lifecycle]] — проблемы lifecycle
> - Базовое понимание паттернов проектирования

---

## Терминология

| Термин | Значение |
|--------|----------|
| **MVVM** | Model-View-ViewModel — UI паттерн |
| **MVI** | Model-View-Intent — MVVM + unidirectional flow |
| **ViewModel** | Хранит UI state, переживает config change |
| **Repository** | Абстракция над источниками данных |
| **Use Case** | Бизнес-логика (Clean Architecture) |
| **UDF** | Unidirectional Data Flow — однонаправленный поток |
| **State** | Текущее состояние UI |
| **Event/Intent** | Действие пользователя или системы |
| **Effect** | Одноразовое событие (navigation, toast) |

---

## Зачем нужна архитектура? Почему нельзя писать всё в Activity?

### Проблема без архитектуры

```kotlin
// ❌ Типичный "God Activity" — всё в одном месте
class UsersActivity : AppCompatActivity() {

    private lateinit var api: ApiService
    private var users: List<User> = emptyList()
    private var isLoading = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_users)

        // Инициализация сети прямо в Activity
        api = Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
            .create(ApiService::class.java)

        loadUsers()
    }

    private fun loadUsers() {
        isLoading = true
        showLoading()

        // Сетевой запрос в Activity
        lifecycleScope.launch {
            try {
                users = api.getUsers()
                // Обновление UI
                recyclerView.adapter = UsersAdapter(users)
                hideLoading()
            } catch (e: Exception) {
                showError(e.message)
            }
            isLoading = false
        }
    }

    // При повороте экрана:
    // 1. Activity уничтожается
    // 2. users теряется
    // 3. loadUsers() вызывается заново
    // 4. Пользователь видит loading снова
}
```

### Что происходит без архитектуры

| Проблема | Последствие |
|----------|-------------|
| **Потеря данных при повороте** | Activity пересоздаётся → данные теряются → повторный запрос |
| **Невозможно тестировать** | UI, сеть, логика смешаны → нужен эмулятор для любого теста |
| **Дублирование кода** | Тот же запрос в 5 экранах → 5 копий кода |
| **Race conditions** | Быстрый поворот экрана → несколько параллельных запросов |
| **Утечки памяти** | Callback держит ссылку на уничтоженную Activity |
| **Сложность поддержки** | Activity на 2000 строк → никто не понимает код |

### Какие есть альтернативы

**1. Сохранять в onSaveInstanceState:**
```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    outState.putParcelableArrayList("users", ArrayList(users))
}
```
- Ограничение ~1MB на весь Bundle
- Только Parcelable данные
- Сложная сериализация
- Не решает проблему тестирования

**2. Singleton для хранения данных:**
```kotlin
object UserCache {
    var users: List<User> = emptyList()
}
```
- Живёт пока живёт процесс (может быть убит)
- Глобальное состояние → сложно отследить изменения
- Memory leaks если хранить Context
- Не решает проблему тестирования

**3. Static переменные:**
```kotlin
companion object {
    var users: List<User> = emptyList()
}
```
- Те же проблемы что и Singleton
- Ещё хуже для тестов (состояние между тестами)

**4. База данных для всего:**
- Overhead для временных данных (loading state)
- Сложность для простых случаев
- Не решает проблему организации кода

### Почему ViewModel решает эти проблемы

```kotlin
// ViewModel переживает configuration change
class UsersViewModel(
    private val repository: UserRepository  // Зависимость инжектируется
) : ViewModel() {

    // StateFlow вместо переменной — реактивное обновление UI
    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {  // Автоматическая отмена при onCleared()
            _uiState.update { it.copy(isLoading = true) }

            repository.getUsers()
                .onSuccess { users ->
                    _uiState.update { it.copy(isLoading = false, users = users) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                }
        }
    }
}

// Activity становится тонкой
@Composable
fun UsersScreen(viewModel: UsersViewModel = viewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()

    // UI только отображает state, никакой логики
    when {
        state.isLoading -> LoadingIndicator()
        state.error != null -> ErrorMessage(state.error!!)
        else -> UserList(state.users)
    }
}
```

| Было (без архитектуры) | Стало (MVVM) |
|------------------------|--------------|
| Данные теряются при повороте | ViewModel переживает rotation |
| Тесты требуют эмулятор | ViewModel тестируется unit-тестами |
| Код дублируется | Repository переиспользуется |
| Race conditions | viewModelScope отменяет при уничтожении |
| Activity на 2000 строк | Activity ~50 строк, логика в ViewModel |

### Недостатки MVVM

1. **Boilerplate код** — нужно создавать UiState, ViewModel, Repository для каждого экрана
2. **Сложность для простых экранов** — для экрана с одной кнопкой MVVM избыточен
3. **Кривая обучения** — новичкам сложнее, чем "всё в Activity"
4. **Не решает все проблемы** — navigation, one-time events требуют дополнительных решений

### Когда НЕ нужна сложная архитектура

- Прототип или MVP (Minimum Viable Product)
- Экран без логики (статичный About)
- Одноразовое приложение
- Обучение Android (сначала понять basics)

---

## MVVM: основы

### Структура

```
┌─────────────────────────────────────────────────────────────────┐
│                           MVVM                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐         ┌─────────────┐         ┌───────────┐ │
│  │    VIEW     │◄────────│  VIEWMODEL  │◄────────│   MODEL   │ │
│  │ (Activity/  │ observes│             │  uses   │(Repository│ │
│  │  Fragment/  │  state  │ - UI State  │         │   / API)  │ │
│  │  Compose)   │─────────│ - Logic     │─────────│           │ │
│  │             │ actions │             │ data    │           │ │
│  └─────────────┘         └─────────────┘         └───────────┘ │
│                                                                 │
│  State flows DOWN (ViewModel → View)                            │
│  Events flow UP (View → ViewModel)                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Реализация

```kotlin
// UI State
data class UsersUiState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null
)

// ViewModel
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

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

    fun deleteUser(user: User) {
        viewModelScope.launch {
            repository.deleteUser(user)
            loadUsers()
        }
    }
}

// View (Compose)
@Composable
fun UsersScreen(viewModel: UsersViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        uiState.isLoading -> LoadingIndicator()
        uiState.error != null -> ErrorMessage(uiState.error!!) { viewModel.loadUsers() }
        else -> UserList(
            users = uiState.users,
            onDelete = { viewModel.deleteUser(it) }
        )
    }
}
```

---

## MVI: Unidirectional Data Flow

MVI добавляет строгий однонаправленный поток данных.

### Структура

```
┌─────────────────────────────────────────────────────────────────┐
│                           MVI                                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│        ┌──────────────────────────────────────────────┐        │
│        │                                              │        │
│        ▼                                              │        │
│  ┌───────────┐    ┌───────────┐    ┌───────────┐    │        │
│  │   VIEW    │────│  INTENT   │────│  REDUCER  │    │        │
│  │           │    │ (Action)  │    │           │    │        │
│  └───────────┘    └───────────┘    └─────┬─────┘    │        │
│        ▲                                 │          │        │
│        │                                 ▼          │        │
│        │                          ┌───────────┐    │        │
│        │                          │   STATE   │    │        │
│        │                          │           │────┘        │
│        │                          └───────────┘             │
│        │                                 │                  │
│        └─────────────────────────────────┘                  │
│                                                             │
│  View → Intent → Reducer → State → View (цикл)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Реализация

```kotlin
// Intent (Events от UI)
sealed class UsersIntent {
    object LoadUsers : UsersIntent()
    data class DeleteUser(val user: User) : UsersIntent()
    data class SearchUsers(val query: String) : UsersIntent()
}

// State
data class UsersState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val error: String? = null,
    val searchQuery: String = ""
)

// Side Effects (one-time events)
sealed class UsersEffect {
    data class ShowToast(val message: String) : UsersEffect()
    data class NavigateToDetail(val userId: Long) : UsersEffect()
}

// ViewModel
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UsersState())
    val state: StateFlow<UsersState> = _state.asStateFlow()

    private val _effect = Channel<UsersEffect>()
    val effect: Flow<UsersEffect> = _effect.receiveAsFlow()

    fun onIntent(intent: UsersIntent) {
        when (intent) {
            is UsersIntent.LoadUsers -> loadUsers()
            is UsersIntent.DeleteUser -> deleteUser(intent.user)
            is UsersIntent.SearchUsers -> search(intent.query)
        }
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }

            repository.getUsers()
                .onSuccess { users ->
                    _state.update { it.copy(isLoading = false, users = users) }
                }
                .onFailure { e ->
                    _state.update { it.copy(isLoading = false, error = e.message) }
                    _effect.send(UsersEffect.ShowToast("Failed to load"))
                }
        }
    }

    private fun deleteUser(user: User) {
        viewModelScope.launch {
            repository.deleteUser(user)
            _effect.send(UsersEffect.ShowToast("User deleted"))
            loadUsers()
        }
    }

    private fun search(query: String) {
        _state.update { it.copy(searchQuery = query) }
        // Debounce and search...
    }
}

// View
@Composable
fun UsersScreen(viewModel: UsersViewModel = viewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val context = LocalContext.current

    // Handle one-time effects
    LaunchedEffect(Unit) {
        viewModel.effect.collect { effect ->
            when (effect) {
                is UsersEffect.ShowToast -> {
                    Toast.makeText(context, effect.message, Toast.LENGTH_SHORT).show()
                }
                is UsersEffect.NavigateToDetail -> {
                    // Navigate
                }
            }
        }
    }

    UsersContent(
        state = state,
        onLoadUsers = { viewModel.onIntent(UsersIntent.LoadUsers) },
        onDeleteUser = { viewModel.onIntent(UsersIntent.DeleteUser(it)) }
    )
}
```

---

## Clean Architecture

### Слои

```
┌─────────────────────────────────────────────────────────────────┐
│                    CLEAN ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    PRESENTATION                          │   │
│  │  UI (Activity, Fragment, Compose)                        │   │
│  │  ViewModel                                               │   │
│  │  UI Models (UiState, Events)                             │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │ depends on                         │
│  ┌─────────────────────────▼───────────────────────────────┐   │
│  │                      DOMAIN                               │   │
│  │  Use Cases (GetUsersUseCase, DeleteUserUseCase)          │   │
│  │  Domain Models (User, Order)                             │   │
│  │  Repository Interfaces                                    │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │ depends on                         │
│  ┌─────────────────────────▼───────────────────────────────┐   │
│  │                        DATA                               │   │
│  │  Repository Implementations                               │   │
│  │  Data Sources (API, Database)                            │   │
│  │  Data Models (UserDto, UserEntity)                       │   │
│  │  Mappers (Dto → Domain, Entity → Domain)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Зависимости направлены ВНУТРЬ (к Domain)                       │
│  Domain ничего не знает о Data и Presentation                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Реализация

```kotlin
// === DOMAIN LAYER ===

// Domain Model
data class User(
    val id: Long,
    val name: String,
    val email: String
)

// Repository Interface (в domain!)
interface UserRepository {
    suspend fun getUsers(): List<User>
    suspend fun getUser(id: Long): User
    suspend fun deleteUser(id: Long)
}

// Use Case
class GetUsersUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(): Result<List<User>> {
        return runCatching { repository.getUsers() }
    }
}

class DeleteUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(userId: Long): Result<Unit> {
        return runCatching { repository.deleteUser(userId) }
    }
}


// === DATA LAYER ===

// API Model
@Serializable
data class UserDto(
    val id: Long,
    val name: String,
    val email: String,
    @SerialName("created_at")
    val createdAt: String
)

// Database Entity
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String,
    val cachedAt: Long
)

// Mappers
fun UserDto.toDomain() = User(id = id, name = name, email = email)
fun UserEntity.toDomain() = User(id = id, name = name, email = email)
fun User.toEntity(cachedAt: Long = System.currentTimeMillis()) =
    UserEntity(id = id, name = name, email = email, cachedAt = cachedAt)

// Repository Implementation
class UserRepositoryImpl(
    private val api: ApiService,
    private val dao: UserDao
) : UserRepository {

    override suspend fun getUsers(): List<User> {
        return try {
            val users = api.getUsers().map { it.toDomain() }
            dao.insertAll(users.map { it.toEntity() })
            users
        } catch (e: Exception) {
            dao.getAll().map { it.toDomain() }
        }
    }

    override suspend fun getUser(id: Long): User {
        return api.getUser(id).toDomain()
    }

    override suspend fun deleteUser(id: Long) {
        api.deleteUser(id)
        dao.deleteById(id)
    }
}


// === PRESENTATION LAYER ===

class UsersViewModel(
    private val getUsersUseCase: GetUsersUseCase,
    private val deleteUserUseCase: DeleteUserUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(UsersUiState())
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            getUsersUseCase()
                .onSuccess { users ->
                    _uiState.update { it.copy(isLoading = false, users = users) }
                }
                .onFailure { e ->
                    _uiState.update { it.copy(isLoading = false, error = e.message) }
                }
        }
    }
}
```

### Структура пакетов

```
com.example.app/
├── data/
│   ├── api/
│   │   ├── ApiService.kt
│   │   └── dto/
│   │       └── UserDto.kt
│   ├── database/
│   │   ├── AppDatabase.kt
│   │   ├── dao/
│   │   │   └── UserDao.kt
│   │   └── entity/
│   │       └── UserEntity.kt
│   └── repository/
│       └── UserRepositoryImpl.kt
├── domain/
│   ├── model/
│   │   └── User.kt
│   ├── repository/
│   │   └── UserRepository.kt
│   └── usecase/
│       ├── GetUsersUseCase.kt
│       └── DeleteUserUseCase.kt
└── presentation/
    ├── ui/
    │   └── users/
    │       ├── UsersScreen.kt
    │       ├── UsersViewModel.kt
    │       └── UsersUiState.kt
    └── navigation/
        └── AppNavigation.kt
```

---

## Dependency Injection

### Hilt

```kotlin
// Module
@Module
@InstallIn(SingletonComponent::class)
object DataModule {

    @Provides
    @Singleton
    fun provideApiService(): ApiService {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .build()
            .create(ApiService::class.java)
    }

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(context, AppDatabase::class.java, "app.db").build()
    }

    @Provides
    fun provideUserRepository(api: ApiService, db: AppDatabase): UserRepository {
        return UserRepositoryImpl(api, db.userDao())
    }
}

// ViewModel с Hilt
@HiltViewModel
class UsersViewModel @Inject constructor(
    private val getUsersUseCase: GetUsersUseCase
) : ViewModel() {
    // ...
}

// Activity
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    // viewModels автоматически инжектируются
}
```

---

## Когда что использовать

| Размер проекта | Рекомендация |
|----------------|--------------|
| Маленький (1-3 экрана) | MVVM без Use Cases |
| Средний (5-15 экранов) | MVVM + Repository |
| Большой (15+ экранов) | Clean Architecture |
| Сложный state | MVI |
| Multiplatform | Clean + KMP |

---

## Когда какой паттерн НЕ подходит

| Паттерн | НЕ подходит когда | Почему |
|---------|------------------|--------|
| **MVC** (Model-View-Controller) | Android приложения в принципе | Activity/Fragment — это и View, и Controller одновременно. Получается "Massive View Controller" с запутанной логикой. Нет решения для configuration changes. |
| **MVP** (Model-View-Presenter) | Compose UI | Presenter держит reference на View интерфейс → утечки памяти при rotation. Много boilerplate (interface для каждого View). Устарел с появлением ViewModel. |
| **MVVM** | Сложные формы с множеством взаимосвязанных полей | State может обновляться из разных мест → трудно отследить источник изменений. Race conditions при параллельных updates. Нет строгого порядка событий. |
| **MVVM** | Real-time приложения (чаты, стримы) | События приходят асинхронно и могут конфликтовать. Сложно гарантировать порядок обработки. State может быть inconsistent между обновлениями. |
| **MVI** | Простые CRUD экраны | Избыточный boilerplate: Intent sealed class для каждого действия, reducer логика, Effect обработка. 3x больше кода чем MVVM для простого списка. |
| **MVI** | Прототипы и MVP | Долгая настройка архитектуры (Intent, State, Effect, Reducer). Сложнее onboarding новых разработчиков. Замедляет итерации. |
| **Clean Architecture** | Маленькие приложения (< 5 экранов) | Over-engineering: Use Cases для простой логики, 3 модели (Dto/Domain/Ui) для одной сущности, множество mapper'ов. Сложность не окупается. |
| **Clean Architecture** | Tight deadlines | Начальная настройка требует времени: модульная структура, DI setup, слои абстракций. Медленнее добавлять features на старте. |
| **Clean Architecture** | Команда джунов | Высокий порог входа: понимание Dependency Rule, слоёв, SOLID. Легко нарушить архитектуру неправильными зависимостями. |

---

## Чеклист

```
□ ViewModel не держит reference на View/Context
□ UI State — immutable data class
□ Один source of truth для state
□ Repository абстрагирует источники данных
□ Use Cases для переиспользуемой бизнес-логики
□ Маппинг между слоями (Dto → Domain → UiModel)
□ DI для зависимостей (Hilt/Koin)
□ Side effects через Channel/SharedFlow
```

---

## Проверь себя

**1. Чем MVVM отличается от MVP?**

<details>
<summary>Ответ</summary>

**MVP (устаревший):**
- Presenter держит **reference на View** (interface) → нужно отписываться в onDestroy
- View **активно вызывает** методы Presenter
- Presenter **напрямую управляет** View через методы (`view.showLoading()`)
- Проблемы с lifecycle → утечки памяти

**MVVM (современный):**
- ViewModel **не знает о View** → не держит reference
- View **наблюдает** за State через Flow/LiveData → автоматическая отписка
- ViewModel **обновляет State**, View реагирует реактивно
- ViewModel **переживает** configuration changes

```kotlin
// MVP - Presenter знает о View
interface UsersView {
    fun showLoading()
    fun showUsers(users: List<User>)
}

class UsersPresenter(private val view: UsersView) {
    fun loadUsers() {
        view.showLoading()  // Напрямую управляет View
        // ...
    }
}

// MVVM - ViewModel не знает о View
class UsersViewModel : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadUsers() {
        _state.update { it.copy(isLoading = true) }  // Только меняет State
    }
}
```

</details>

---

**2. Что такое unidirectional data flow и зачем он нужен?**

<details>
<summary>Ответ</summary>

**Unidirectional Data Flow (UDF)** — данные движутся строго в одном направлении по циклу:

```
View → Intent/Event → ViewModel → State → View
  ▲                                          │
  └──────────────────────────────────────────┘
```

**Зачем нужен:**

1. **Предсказуемость** — всегда понятно откуда пришло изменение state
2. **Отладка** — можно логировать каждый Intent и видеть всю цепочку
3. **Time-travel debugging** — можно воспроизвести последовательность событий
4. **Избегание race conditions** — state обновляется в одном месте (reducer)

**Без UDF (MVVM):**
```kotlin
class UsersViewModel : ViewModel() {
    fun loadUsers() { _state.update { ... } }
    fun onSearchChanged(query: String) { _state.update { ... } }
    fun onRefresh() { _state.update { ... } }
    // State обновляется в 10 разных местах → сложно отследить
}
```

**С UDF (MVI):**
```kotlin
class UsersViewModel : ViewModel() {
    fun onIntent(intent: UsersIntent) {
        when (intent) {
            is LoadUsers -> handleLoadUsers()
            is SearchChanged -> handleSearch(intent.query)
            is Refresh -> handleRefresh()
        }
    }
    // Одна точка входа → легко логировать и тестировать
}
```

</details>

---

**3. Почему MVI хорошо сочетается с Compose?**

<details>
<summary>Ответ</summary>

**Compose и MVI основаны на одних принципах:**

1. **Immutable State**
   - Compose: `@Composable` функции должны быть pure (одинаковый state → одинаковый UI)
   - MVI: State — immutable data class, обновляется через `copy()`

2. **Unidirectional Data Flow**
   - Compose: State flows down, Events flow up
   - MVI: То же самое через Intent → State цикл

3. **Declarative UI**
   - Compose: UI = функция от state (`UI = f(state)`)
   - MVI: State полностью описывает UI, нет императивных команд

4. **Простота обработки событий**
```kotlin
@Composable
fun UsersScreen(viewModel: UsersViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    UsersContent(
        state = state,
        // Все события — через один метод onIntent
        onEvent = { viewModel.onIntent(it) }
    )
}
```

5. **Side Effects**
   - Compose: `LaunchedEffect`, `SideEffect`
   - MVI: Effect channel для навигации, toast, etc.

**Альтернатива (MVVM) тоже работает**, но MVI более явный и консистентный.

</details>

---

**4. Когда Clean Architecture — overkill?**

<details>
<summary>Ответ</summary>

Clean Architecture избыточна когда:

**1. Маленькое приложение (< 5 экранов)**
```kotlin
// Overkill для простого TODO приложения:
data/repository/TaskRepositoryImpl.kt
domain/repository/TaskRepository.kt
domain/model/Task.kt
domain/usecase/GetTasksUseCase.kt
domain/usecase/AddTaskUseCase.kt
domain/usecase/DeleteTaskUseCase.kt
presentation/ui/tasks/TasksViewModel.kt
presentation/ui/tasks/TasksUiState.kt

// Достаточно простого MVVM:
TaskRepository.kt
Task.kt
TasksViewModel.kt
```

**2. Prototype / MVP**
- Нужна скорость итераций, а не долгосрочная поддержка
- Требования постоянно меняются → переделывать слои дорого
- Неизвестно будет ли проект жить

**3. Простая бизнес-логика**
- CRUD без правил (просто показать данные с API)
- Нет переиспользуемой логики → Use Cases пустые обертки
```kotlin
// Use Case не добавляет ценности
class GetUsersUseCase(private val repo: UserRepository) {
    suspend operator fun invoke() = repo.getUsers()  // Просто проксирует
}
```

**4. Tight deadline**
- Настройка модулей, DI, слоев занимает время
- На старте Clean Architecture замедляет фичи

**5. Команда джунов**
- Сложно поддерживать Dependency Rule
- Легко сломать архитектуру неправильными зависимостями

**Когда Clean Architecture оправдана:**
- 15+ экранов
- Сложная бизнес-логика (финтех, e-commerce)
- Долгосрочный проект (5+ лет)
- Большая команда (нужны чёткие границы)
- Multiplatform (domain переиспользуется)

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Use Case = один метод Repository" | Если UseCase просто проксирует Repository — он не нужен. UseCase для orchestration между repositories, validation, business rules |
| "Domain layer обязателен" | Для простых CRUD apps domain layer = boilerplate. Google recommendations: optional domain layer. Добавляй когда логика усложняется |
| "MVVM = ViewModel + LiveData" | MVVM — паттерн UI layer, не про LiveData. StateFlow, RxJava, Compose state — всё MVVM если есть separation View/ViewModel |
| "MVI сложнее MVVM" | Базовый MVI = MVVM + explicit Intent. StateFlow + sealed class Intent + reducer function. Не rocket science |
| "Repository всегда возвращает Domain model" | Repository может возвращать DTO если domain = DTO. Mapping нужен когда форматы расходятся или нужна изоляция от API changes |
| "Clean Architecture от Uncle Bob = Android Clean" | Uncle Bob's Clean — для enterprise. Android адаптация проще: data/domain/presentation достаточно. Не нужны все слои оригинала |
| "ViewModel = Presenter" | ViewModel переживает config change, Presenter нет. ViewModel не знает о View, Presenter держит reference. Разные lifecycle |
| "Dependency Inversion везде" | DI между модулями важен. Но внутри модуля интерфейс для одной реализации — overengineering. Балансируй |
| "Модуляризация = Clean Architecture" | Модуляризация про build time и team boundaries. Clean Architecture про dependency direction. Можно делать отдельно |
| "Compose убил MVP/MVVM" | Compose = UI layer. MVP/MVVM/MVI — presentation patterns. Compose отлично работает с любым. Просто state hoisting проще |

---

## CS-фундамент

| CS-концепция | Как применяется в Architecture |
|--------------|--------------------------------|
| **Separation of Concerns** | View отвечает за отображение. ViewModel за UI логику. Repository за данные. Каждый компонент — одна ответственность |
| **Dependency Inversion** | High-level modules не зависят от low-level. ViewModel зависит от interface Repository, не от implementation |
| **Unidirectional Data Flow** | State flows down (ViewModel → View). Events flow up (View → ViewModel). Single source of truth |
| **Observer Pattern** | LiveData/StateFlow notify observers. View подписывается. Слабая связанность producer/consumer |
| **State Machine** | MVI Reducer: (State, Intent) → State. Deterministic transitions. Легко тестировать, логировать |
| **Layered Architecture** | Presentation → Domain → Data. Dependencies направлены вниз. Domain не знает о Android |
| **Repository Pattern** | Abstraction над data sources. ViewModel не знает откуда данные: network, database, cache |
| **Command Pattern** | MVI Intent = Command object. Encapsulation запроса. Можно queue, log, replay |
| **Immutability** | UI State immutable. Изменение = новый объект. Thread safety, предсказуемость |
| **Single Source of Truth** | Один источник данных для UI. StateFlow в ViewModel. Нет conflicting state |

---

## Связи

**Android раздел:**
→ [[android-overview]] — карта раздела
→ [[android-activity-lifecycle]] — ViewModel переживает lifecycle, решает проблему потери данных при rotation
→ [[android-compose]] — declarative UI идеально сочетается с MVI (state flows down, events flow up)
→ [[android-threading]] — coroutines в viewModelScope, StateFlow/SharedFlow для reactive state

**Архитектура:**
→ [[design-patterns]] — Repository, Observer, Strategy используются в MVVM/MVI
→ [[clean-code-solid]] — Clean Architecture построена на принципах SOLID (особенно Dependency Inversion)
→ [[microservices-vs-monolith]] — принципы разделения слоёв похожи (границы, независимость)

**Kotlin:**
→ [[kotlin-flow]] — StateFlow для UI state, Channel для side effects в MVI

---

## Источники

**Официальная документация:**
- [Guide to App Architecture](https://developer.android.com/topic/architecture) — официальное руководство
- [Recommendations for Android Architecture](https://developer.android.com/topic/architecture/recommendations) — best practices
- [UI Layer](https://developer.android.com/topic/architecture/ui-layer) — ViewModel, UI State
- [Data Layer](https://developer.android.com/topic/architecture/data-layer) — Repository pattern
- [Domain Layer](https://developer.android.com/topic/architecture/domain-layer) — Use Cases

**Практические ресурсы:**
- [Now in Android](https://github.com/android/nowinandroid) — официальный sample с MVVM + Clean Architecture
- [Architecture Samples](https://github.com/android/architecture-samples) — варианты реализации

---

*Проверено: 2026-01-09 | На основе официальной документации Android*
