---
title: "Cross-Platform: Architecture — MVVM, Clean Architecture"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - topic/architecture
  - mvvm
  - clean-architecture
  - type/comparison
  - level/intermediate
reading_time: 30
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[kmp-architecture-patterns]]"
related:
  - "[[android-architecture-patterns]]"
  - "[[ios-architecture-patterns]]"
  - "[[kmp-architecture-patterns]]"
---

# Архитектурные паттерны: iOS vs Android

## TL;DR: Сравнительная таблица

| Аспект | iOS (Swift) | Android (Kotlin) |
|--------|-------------|------------------|
| **Основной паттерн** | MVVM + Combine/async | MVVM + Flow/Coroutines |
| **ViewModel** | ObservableObject | ViewModel (AAC) |
| **Реактивное состояние** | @Published, @State | StateFlow, LiveData |
| **DI** | Manual / Swinject | Hilt / Koin |
| **Навигация** | Coordinator / NavigationStack | Navigation Component |
| **Lifecycle** | Нет официального | Lifecycle-aware components |
| **Clean Architecture** | Вручную | Официальные гайды Google |
| **Repository** | Protocol + Impl | Interface + Impl |
| **UseCase** | Interactor / UseCase | UseCase class |
| **Multiplatform** | — | KMP commonMain |

---

## 1. MVVM: Сравнение подходов

### iOS: ObservableObject + @Published

```swift
// ViewModel
@MainActor
final class UserViewModel: ObservableObject {
    // Состояние
    @Published private(set) var user: User?
    @Published private(set) var isLoading = false
    @Published private(set) var error: Error?

    private let repository: UserRepositoryProtocol

    init(repository: UserRepositoryProtocol) {
        self.repository = repository
    }

    func loadUser(id: String) async {
        isLoading = true
        error = nil

        do {
            user = try await repository.getUser(id: id)
        } catch {
            self.error = error
        }

        isLoading = false
    }
}

// View
struct UserView: View {
    @StateObject private var viewModel: UserViewModel

    init(repository: UserRepositoryProtocol) {
        _viewModel = StateObject(wrappedValue: UserViewModel(repository: repository))
    }

    var body: some View {
        Group {
            if viewModel.isLoading {
                ProgressView()
            } else if let user = viewModel.user {
                UserContent(user: user)
            } else if let error = viewModel.error {
                ErrorView(error: error)
            }
        }
        .task {
            await viewModel.loadUser(id: "123")
        }
    }
}
```

### Android: ViewModel + StateFlow

```kotlin
// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    // UI State
    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }

            repository.getUser(id)
                .onSuccess { user ->
                    _uiState.update { it.copy(user = user, isLoading = false) }
                }
                .onFailure { error ->
                    _uiState.update { it.copy(error = error, isLoading = false) }
                }
        }
    }
}

data class UserUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: Throwable? = null
)

// Composable
@Composable
fun UserScreen(
    viewModel: UserViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.loadUser("123")
    }

    when {
        uiState.isLoading -> CircularProgressIndicator()
        uiState.user != null -> UserContent(uiState.user!!)
        uiState.error != null -> ErrorView(uiState.error!!)
    }
}
```

### Ключевые различия MVVM

| iOS | Android |
|-----|---------|
| `@Published` — отдельные свойства | `StateFlow<UiState>` — единый стейт |
| `@StateObject` создаёт VM | `hiltViewModel()` инжектит |
| `.task { }` для async | `LaunchedEffect` для корутин |
| `@MainActor` для UI потока | `viewModelScope` автоматически |

---

## 2. Clean Architecture: Слои

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                        │
│  ┌─────────────────────┐    ┌─────────────────────┐         │
│  │   iOS: SwiftUI      │    │  Android: Compose   │         │
│  │   View + ViewModel  │    │  Screen + ViewModel │         │
│  └─────────────────────┘    └─────────────────────┘         │
├─────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Entities (Models) │ UseCases │ Repository Protocols │    │
│  │         Чистый Swift/Kotlin — без фреймворков        │    │
│  └─────────────────────────────────────────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                       DATA LAYER                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐    │
│  │  Repository   │  │    Remote     │  │    Local      │    │
│  │    Impl       │  │  DataSource   │  │  DataSource   │    │
│  └───────────────┘  └───────────────┘  └───────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Domain Layer: Entities

```swift
// iOS: Domain/Entities/User.swift
struct User: Equatable, Sendable {
    let id: String
    let name: String
    let email: String
}
```

```kotlin
// Android: domain/model/User.kt
data class User(
    val id: String,
    val name: String,
    val email: String
)
```

### Domain Layer: UseCase

```swift
// iOS: Domain/UseCases/GetUserUseCase.swift
protocol GetUserUseCaseProtocol {
    func execute(id: String) async throws -> User
}

final class GetUserUseCase: GetUserUseCaseProtocol {
    private let repository: UserRepositoryProtocol

    init(repository: UserRepositoryProtocol) {
        self.repository = repository
    }

    func execute(id: String) async throws -> User {
        guard !id.isEmpty else {
            throw DomainError.invalidInput
        }
        return try await repository.getUser(id: id)
    }
}
```

```kotlin
// Android: domain/usecase/GetUserUseCase.kt
class GetUserUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(id: String): Result<User> {
        if (id.isBlank()) {
            return Result.failure(DomainException.InvalidInput)
        }
        return repository.getUser(id)
    }
}
```

### Domain Layer: Repository Protocol/Interface

```swift
// iOS: Domain/Repositories/UserRepositoryProtocol.swift
protocol UserRepositoryProtocol: Sendable {
    func getUser(id: String) async throws -> User
    func saveUser(_ user: User) async throws
    func deleteUser(id: String) async throws
}
```

```kotlin
// Android: domain/repository/UserRepository.kt
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    suspend fun saveUser(user: User): Result<Unit>
    suspend fun deleteUser(id: String): Result<Unit>
}
```

---

## 3. Repository Pattern: Реализация

### iOS: Repository Implementation

```swift
// Data/Repositories/UserRepository.swift
final class UserRepository: UserRepositoryProtocol {
    private let remoteDataSource: UserRemoteDataSourceProtocol
    private let localDataSource: UserLocalDataSourceProtocol

    init(
        remoteDataSource: UserRemoteDataSourceProtocol,
        localDataSource: UserLocalDataSourceProtocol
    ) {
        self.remoteDataSource = remoteDataSource
        self.localDataSource = localDataSource
    }

    func getUser(id: String) async throws -> User {
        // Стратегия: сначала кэш, потом сеть
        if let cached = try? await localDataSource.getUser(id: id) {
            return cached
        }

        let remote = try await remoteDataSource.fetchUser(id: id)
        try? await localDataSource.saveUser(remote)
        return remote
    }

    func saveUser(_ user: User) async throws {
        try await remoteDataSource.updateUser(user)
        try await localDataSource.saveUser(user)
    }

    func deleteUser(id: String) async throws {
        try await remoteDataSource.deleteUser(id: id)
        try await localDataSource.deleteUser(id: id)
    }
}

// Data/DataSources/UserRemoteDataSource.swift
protocol UserRemoteDataSourceProtocol: Sendable {
    func fetchUser(id: String) async throws -> User
    func updateUser(_ user: User) async throws
    func deleteUser(id: String) async throws
}

final class UserRemoteDataSource: UserRemoteDataSourceProtocol {
    private let apiClient: APIClientProtocol

    init(apiClient: APIClientProtocol) {
        self.apiClient = apiClient
    }

    func fetchUser(id: String) async throws -> User {
        let dto: UserDTO = try await apiClient.request(.getUser(id: id))
        return dto.toDomain()
    }

    func updateUser(_ user: User) async throws {
        let dto = UserDTO(from: user)
        try await apiClient.request(.updateUser(dto))
    }

    func deleteUser(id: String) async throws {
        try await apiClient.request(.deleteUser(id: id))
    }
}
```

### Android: Repository Implementation

```kotlin
// data/repository/UserRepositoryImpl.kt
class UserRepositoryImpl(
    private val remoteDataSource: UserRemoteDataSource,
    private val localDataSource: UserLocalDataSource,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) : UserRepository {

    override suspend fun getUser(id: String): Result<User> =
        withContext(dispatcher) {
            // Стратегия: сначала кэш, потом сеть
            localDataSource.getUser(id)?.let { cached ->
                return@withContext Result.success(cached)
            }

            remoteDataSource.fetchUser(id)
                .onSuccess { user ->
                    localDataSource.saveUser(user)
                }
        }

    override suspend fun saveUser(user: User): Result<Unit> =
        withContext(dispatcher) {
            remoteDataSource.updateUser(user)
                .onSuccess {
                    localDataSource.saveUser(user)
                }
        }

    override suspend fun deleteUser(id: String): Result<Unit> =
        withContext(dispatcher) {
            remoteDataSource.deleteUser(id)
                .onSuccess {
                    localDataSource.deleteUser(id)
                }
        }
}

// data/datasource/UserRemoteDataSource.kt
interface UserRemoteDataSource {
    suspend fun fetchUser(id: String): Result<User>
    suspend fun updateUser(user: User): Result<Unit>
    suspend fun deleteUser(id: String): Result<Unit>
}

class UserRemoteDataSourceImpl(
    private val apiService: UserApiService
) : UserRemoteDataSource {

    override suspend fun fetchUser(id: String): Result<User> = runCatching {
        apiService.getUser(id).toDomain()
    }

    override suspend fun updateUser(user: User): Result<Unit> = runCatching {
        apiService.updateUser(user.toDto())
    }

    override suspend fun deleteUser(id: String): Result<Unit> = runCatching {
        apiService.deleteUser(id)
    }
}
```

---

## 4. KMP: Общая архитектура в commonMain

```kotlin
// shared/src/commonMain/kotlin/domain/model/User.kt
data class User(
    val id: String,
    val name: String,
    val email: String
)

// shared/src/commonMain/kotlin/domain/repository/UserRepository.kt
interface UserRepository {
    suspend fun getUser(id: String): Result<User>
    suspend fun saveUser(user: User): Result<Unit>
}

// shared/src/commonMain/kotlin/domain/usecase/GetUserUseCase.kt
class GetUserUseCase(
    private val repository: UserRepository
) {
    suspend operator fun invoke(id: String): Result<User> {
        require(id.isNotBlank()) { "User ID cannot be blank" }
        return repository.getUser(id)
    }
}

// shared/src/commonMain/kotlin/presentation/UserViewModel.kt
class UserViewModel(
    private val getUserUseCase: GetUserUseCase
) : ViewModel() {

    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }

            getUserUseCase(id)
                .onSuccess { user ->
                    _state.update { it.copy(user = user, isLoading = false) }
                }
                .onFailure { error ->
                    _state.update { it.copy(error = error.message, isLoading = false) }
                }
        }
    }
}

data class UserState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)
```

### Платформенные реализации

```kotlin
// shared/src/androidMain/kotlin/data/UserRepositoryImpl.kt
actual class UserRepositoryImpl(
    private val retrofit: UserApi,
    private val roomDao: UserDao
) : UserRepository {

    actual override suspend fun getUser(id: String): Result<User> = runCatching {
        roomDao.getUser(id) ?: retrofit.getUser(id).also {
            roomDao.insert(it)
        }
    }
}

// shared/src/iosMain/kotlin/data/UserRepositoryImpl.kt
actual class UserRepositoryImpl(
    private val ktor: HttpClient,
    private val realm: Realm
) : UserRepository {

    actual override suspend fun getUser(id: String): Result<User> = runCatching {
        realm.query<UserEntity>("id == $0", id).first().find()?.toDomain()
            ?: ktor.get("users/$id").body<UserDto>().toDomain().also {
                realm.write { copyToRealm(UserEntity(it)) }
            }
    }
}
```

### Структура KMP проекта

```
shared/
├── src/
│   ├── commonMain/kotlin/
│   │   ├── domain/
│   │   │   ├── model/
│   │   │   ├── repository/
│   │   │   └── usecase/
│   │   ├── presentation/
│   │   │   └── viewmodel/
│   │   └── di/
│   │       └── Koin.kt
│   ├── androidMain/kotlin/
│   │   └── data/
│   │       ├── repository/
│   │       └── datasource/
│   └── iosMain/kotlin/
│       └── data/
│           ├── repository/
│           └── datasource/
```

---

## 5. Шесть типичных ошибок

### Ошибка 1: ViewModel хранит Context (Android)

```kotlin
// Плохо: утечка памяти
class BadViewModel(
    private val context: Context  // Activity context = утечка!
) : ViewModel()

// Хорошо: Application context или избегать
class GoodViewModel(
    private val repository: UserRepository  // Только зависимости
) : ViewModel()

// Если нужен context — используй Hilt
@HiltViewModel
class BetterViewModel @Inject constructor(
    @ApplicationContext private val context: Context
) : ViewModel()
```

### Ошибка 2: Бизнес-логика во View (iOS)

```swift
// Плохо: логика в View
struct BadUserView: View {
    @State private var user: User?

    var body: some View {
        Button("Load") {
            Task {
                // Прямой API вызов во View!
                let url = URL(string: "api/user")!
                let (data, _) = try await URLSession.shared.data(from: url)
                user = try JSONDecoder().decode(User.self, from: data)
            }
        }
    }
}

// Хорошо: логика в ViewModel
struct GoodUserView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        Button("Load") {
            Task { await viewModel.loadUser() }
        }
    }
}
```

### Ошибка 3: Нарушение Dependency Rule

```swift
// Плохо: Domain зависит от Data
// Domain/UseCase/GetUserUseCase.swift
import Alamofire  // Фреймворк в Domain слое!

class BadUseCase {
    func execute() async throws -> User {
        let response = await AF.request("api/user").serializingDecodable(User.self)
        return try response.value
    }
}

// Хорошо: Domain зависит только от протоколов
class GoodUseCase {
    private let repository: UserRepositoryProtocol  // Протокол из Domain

    init(repository: UserRepositoryProtocol) {
        self.repository = repository
    }

    func execute() async throws -> User {
        try await repository.getUser()
    }
}
```

### Ошибка 4: Отсутствие error handling

```kotlin
// Плохо: игнорирование ошибок
class BadViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.getData()  // Может упасть!
            _state.value = data
        }
    }
}

// Хорошо: явная обработка
class GoodViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }

            repository.getData()
                .onSuccess { data ->
                    _state.update { it.copy(data = data, isLoading = false) }
                }
                .onFailure { error ->
                    _state.update {
                        it.copy(error = error.toUiError(), isLoading = false)
                    }
                }
        }
    }
}
```

### Ошибка 5: Множественные источники правды

```swift
// Плохо: состояние дублируется
class BadViewModel: ObservableObject {
    @Published var userName: String = ""
    @Published var userEmail: String = ""
    @Published var userAge: Int = 0
    // 10+ отдельных @Published для одной сущности
}

// Хорошо: единый источник правды
class GoodViewModel: ObservableObject {
    @Published private(set) var state = UserState()

    struct UserState {
        var user: User?
        var isLoading = false
        var error: Error?
    }
}
```

### Ошибка 6: Repository без кэширования

```kotlin
// Плохо: каждый раз сетевой запрос
class BadRepository(
    private val api: UserApi
) : UserRepository {
    override suspend fun getUser(id: String) = api.getUser(id)
}

// Хорошо: стратегия кэширования
class GoodRepository(
    private val api: UserApi,
    private val cache: UserCache,
    private val dispatcher: CoroutineDispatcher
) : UserRepository {

    override suspend fun getUser(id: String) = withContext(dispatcher) {
        // 1. Проверяем кэш
        cache.get(id)?.let { return@withContext Result.success(it) }

        // 2. Запрос к API
        api.getUser(id)
            .onSuccess { cache.put(id, it) }
    }
}
```

---

## 6. Три ментальные модели

### Модель 1: "Луковица" (Onion Architecture)

```
            ┌─────────────────────────┐
            │     Presentation        │  ← Зависит от всего
            │  (View, ViewModel)      │
            ├─────────────────────────┤
            │       Domain            │  ← Чистый, без зависимостей
            │  (Entity, UseCase,      │
            │   Repository Protocol)  │
            ├─────────────────────────┤
            │        Data             │  ← Реализует Domain протоколы
            │  (Repository Impl,      │
            │   DataSource, API)      │
            └─────────────────────────┘

Правило: стрелки зависимостей направлены ВНУТРЬ
```

### Модель 2: "Конвейер" данных

```
┌───────┐    ┌───────┐    ┌────────┐    ┌──────┐    ┌──────┐
│  API  │ -> │  DTO  │ -> │ Domain │ -> │ UiState │-> │ View │
└───────┘    └───────┘    └────────┘    └──────┘    └──────┘
   Network      Data        Domain      Presentation    UI
   Response     Model       Entity        Model       Render

Каждый слой трансформирует данные в свой формат:
- DTO: JSON mapping, nullable поля, snake_case
- Domain: бизнес-правила, валидация
- UiState: форматирование для отображения
```

### Модель 3: "Dependency Injection = Сменные батарейки"

```
┌─────────────────────────────────────────┐
│              ViewModel                   │
│  ┌─────────────────────────────────┐    │
│  │     Repository Protocol         │    │  ← "Слот для батарейки"
│  │  ┌───────────┐  ┌───────────┐   │    │
│  │  │   Real    │  │   Mock    │   │    │  ← Разные "батарейки"
│  │  │   Impl    │  │   Impl    │   │    │
│  │  └───────────┘  └───────────┘   │    │
│  └─────────────────────────────────┘    │
└─────────────────────────────────────────┘

Production: RealRepository (API + DB)
Testing:    MockRepository (in-memory)
Preview:    StubRepository (hardcoded data)
```

---

## 7. Quiz: проверь понимание

### Вопрос 1
Почему Domain слой не должен импортировать Alamofire/Retrofit?

<details>
<summary>Ответ</summary>

Domain — центр приложения, содержит бизнес-логику. Он не должен знать о деталях реализации (сеть, БД, UI). Это позволяет:
- Тестировать без моков фреймворков
- Менять сетевой слой без изменения бизнес-логики
- Переиспользовать Domain в других проектах

Domain зависит только от языка (Swift/Kotlin) и своих протоколов.
</details>

### Вопрос 2
Чем `@Published` (iOS) отличается от `StateFlow` (Android) концептуально?

<details>
<summary>Ответ</summary>

**@Published:**
- Property wrapper для ObservableObject
- Автоматически уведомляет SwiftUI о изменениях
- Обычно отдельные свойства: `@Published var name`, `@Published var age`

**StateFlow:**
- Hot flow с текущим значением
- Требует явного collect в Composable
- Обычно единый UiState: `StateFlow<UserUiState>`

Концептуально @Published = "реактивное свойство", StateFlow = "реактивный поток с кэшем".
</details>

### Вопрос 3
Зачем в KMP commonMain выносить ViewModel, если на iOS обычно используют ObservableObject?

<details>
<summary>Ответ</summary>

KMP ViewModel в commonMain:
- Общая бизнес-логика на обеих платформах
- StateFlow работает и на Android, и на iOS (через SKIE/KMP-NativeCoroutines)
- На iOS можно обернуть в ObservableObject:

```swift
@MainActor
class IOSUserViewModel: ObservableObject {
    @Published var state: UserState = .init()

    private let shared: SharedUserViewModel

    init(shared: SharedUserViewModel) {
        self.shared = shared
        // Подписка на StateFlow
        shared.state.collect { [weak self] state in
            self?.state = state
        }
    }
}
```

Выигрыш: единая логика, разный UI.
</details>

---

## Связь с другими темами

[[android-architecture-patterns]] — Архитектурные паттерны Android (MVI, MVVM, Clean Architecture) отражают специфику платформы: тесная связь с жизненным циклом Activity/Fragment, необходимость переживать configuration changes, интеграция с Hilt для DI. Понимание Android-паттернов позволяет точнее видеть, где подходы платформ совпадают (MVVM как доминирующий шаблон), а где расходятся (MVI популярнее на Android, VIPER — на iOS). Сравнение помогает выбирать архитектуру для KMP-проектов, где бизнес-логика должна быть платформонезависимой.

[[ios-architecture-patterns]] — iOS-архитектура строится вокруг SwiftUI/UIKit, Combine и протокол-ориентированного подхода. MVVM на iOS использует @Published и @StateObject вместо StateFlow и ViewModel из Jetpack. Знание iOS-паттернов (VIPER, TCA, MVVM-C) необходимо для понимания того, как один и тот же принцип разделения ответственности реализуется по-разному в зависимости от платформенных API. Это критически важно при проектировании shared-модулей в KMP.

[[kmp-architecture-patterns]] — Архитектура KMP-проектов объединяет лучшие практики обеих платформ в общем коде. Shared ViewModel через expect/actual, единый Repository слой и общий Domain — всё это позволяет избежать дублирования бизнес-логики. Заметка раскрывает, как адаптировать Clean Architecture для мультиплатформенного контекста, включая интеграцию с SKIE для Swift и нативный доступ из Android-кода.

---

## Источники и дальнейшее чтение

- Martin R. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design.* — Фундаментальная книга о принципах архитектуры: границы, зависимости, слои. Напрямую применима к mobile-архитектуре и разделению shared/platform кода.
- Gamma E., Helm R., Johnson R., Vlissides J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software.* — Классический справочник паттернов проектирования (Observer, Strategy, Factory), которые лежат в основе архитектурных решений на обеих платформах.
- Moskala M. (2021). *Effective Kotlin: Best Practices.* — Практические рекомендации по Kotlin, включая архитектурные решения для ViewModel, UseCase и Repository, актуальные для Android и KMP.

---

## Проверь себя

> [!question]- Почему Domain слой не должен импортировать Alamofire или Retrofit?
> Domain -- центр приложения с бизнес-логикой. Если он зависит от фреймворков, то нельзя тестировать без моков этих фреймворков, нельзя менять сетевой слой без изменения бизнес-логики, и нельзя переиспользовать Domain в других проектах. Domain должен зависеть только от языка (Swift/Kotlin) и своих протоколов/интерфейсов.

> [!question]- Сценарий: ваш ViewModel на Android хранит Context. Какие проблемы это создаёт и как их решить?
> Хранение Activity Context в ViewModel -- это утечка памяти, потому что ViewModel переживает Activity при configuration changes. Activity уничтожается, но ViewModel держит на неё ссылку. Решение: использовать только Application Context через @ApplicationContext в Hilt, или вообще избегать Context в ViewModel, инжектируя только repository/usecase.

> [!question]- Чем @Published в iOS концептуально отличается от StateFlow в Android?
> @Published -- property wrapper для отдельных свойств ObservableObject, автоматически уведомляющий SwiftUI. StateFlow -- hot flow с текущим значением, требующий явного collect в Composable. Концептуально @Published = "реактивное свойство", StateFlow = "реактивный поток с кэшем". На iOS часто используют отдельные @Published, на Android -- единый StateFlow<UiState>.

> [!question]- Почему в KMP commonMain имеет смысл выносить ViewModel, хотя на iOS обычно используют ObservableObject?
> Shared ViewModel в commonMain содержит единую бизнес-логику для обеих платформ. StateFlow работает и на Android, и на iOS (через SKIE/KMP-NativeCoroutines). На iOS Kotlin ViewModel оборачивается в ObservableObject-wrapper, который подписывается на StateFlow. Выигрыш -- единая логика, разный UI.

---

## Ключевые карточки

Какой основной архитектурный паттерн используется на iOS и Android?
?
MVVM: на iOS -- ObservableObject + @Published + async/await, на Android -- ViewModel (AAC) + StateFlow + Coroutines. Оба используют реактивное связывание, но iOS предпочитает отдельные свойства, а Android -- единый UiState.

Что такое Dependency Rule в Clean Architecture?
?
Зависимости направлены только внутрь: Presentation зависит от Domain, Data реализует Domain-протоколы, но Domain не знает ни о Presentation, ни о Data. Domain содержит только Entity, UseCase и Repository Protocol/Interface.

Какова роль DTO в "конвейере данных"?
?
DTO (Data Transfer Object) -- модель для JSON mapping с nullable полями и snake_case. Данные проходят конвейер: API Response -> DTO (Data) -> Domain Entity (Domain) -> UiState (Presentation) -> View (UI). Каждый слой трансформирует данные в свой формат.

Как Repository Pattern реализуется на iOS и Android?
?
iOS: protocol UserRepositoryProtocol + final class UserRepository. Android: interface UserRepository + class UserRepositoryImpl. Оба реализуют стратегию кэширования: сначала проверяют локальный кэш, затем делают сетевой запрос, сохраняют результат в кэш.

Почему множественные @Published для одной сущности -- плохая практика?
?
Дублирование состояния нарушает Single Source of Truth. Несколько @Published для userName, userEmail, userAge создают риск рассинхронизации. Лучше использовать единый @Published state: UserState с полями user, isLoading, error.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-dependency-injection]] | DI-фреймворки для реализации Clean Architecture |
| Углубиться | [[kmp-architecture-patterns]] | Архитектура в KMP с shared ViewModel |
| Смежная тема | [[design-patterns]] | Паттерны проектирования из раздела Programming |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |
