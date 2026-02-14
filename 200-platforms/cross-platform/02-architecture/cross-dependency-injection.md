---
title: "Cross-Platform: Dependency Injection — Swinject vs Hilt"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - di
  - swinject
  - hilt
  - koin
  - type/comparison
  - level/intermediate
reading_time: 14
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-architecture]]"
related:
  - "[[android-dependency-injection]]"
  - "[[ios-dependency-injection]]"
  - "[[dependency-injection-fundamentals]]"
---

# Dependency Injection: iOS vs Android

## TL;DR: Сравнительная таблица

| Аспект | iOS | Android |
|--------|-----|---------|
| **Manual DI** | Initializer injection | Constructor injection |
| **Container (популярный)** | Swinject | Hilt (официальный) |
| **Container (альтернатива)** | Needle, Factory | Koin, Dagger |
| **Compile-time safety** | Needle | Dagger/Hilt |
| **Runtime регистрация** | Swinject | Koin |
| **Scopes** | Container hierarchy | @Singleton, @ViewModelScoped |
| **SwiftUI/Compose** | @EnvironmentObject | @HiltViewModel |
| **KMP** | — | Koin, kotlin-inject |

---

## 1. Manual DI: Базовый подход

### iOS: Initializer Injection

```swift
protocol UserRepositoryProtocol {
    func getUser(id: String) async throws -> User
}

@MainActor
final class UserViewModel: ObservableObject {
    private let repository: UserRepositoryProtocol

    init(repository: UserRepositoryProtocol) {
        self.repository = repository
    }
}

// Composition Root
final class AppDependencies {
    private lazy var apiClient: APIClientProtocol = APIClient()
    private lazy var userRepository: UserRepositoryProtocol = UserRepositoryImpl(api: apiClient)

    func makeUserViewModel() -> UserViewModel {
        UserViewModel(repository: userRepository)
    }
}
```

### Android: Constructor Injection

```kotlin
interface UserRepository {
    suspend fun getUser(id: String): User
}

class UserViewModel(
    private val repository: UserRepository
) : ViewModel()

// Composition Root
class AppDependencies(context: Context) {
    private val apiClient: ApiClient by lazy { ApiClient() }
    private val userRepository: UserRepository by lazy { UserRepositoryImpl(apiClient) }

    fun createUserViewModel() = UserViewModel(userRepository)
}
```

---

## 2. Container-based DI: Swinject vs Hilt

### iOS: Swinject

```swift
import Swinject

let container = Container()

container.register(APIClientProtocol.self) { _ in APIClient() }
    .inObjectScope(.container)

container.register(UserRepositoryProtocol.self) { r in
    UserRepositoryImpl(api: r.resolve(APIClientProtocol.self)!)
}.inObjectScope(.container)

container.register(UserViewModel.self) { r in
    UserViewModel(repository: r.resolve(UserRepositoryProtocol.self)!)
}

// Assembly для модульности
final class NetworkAssembly: Assembly {
    func assemble(container: Container) {
        container.register(APIClientProtocol.self) { _ in APIClient() }
            .inObjectScope(.container)
    }
}
```

### Android: Hilt

```kotlin
@HiltAndroidApp
class MyApplication : Application()

@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    @Provides
    @Singleton
    fun provideUserRepository(api: ApiClient): UserRepository = UserRepositoryImpl(api)
}

@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel()

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    private val viewModel: UserViewModel by viewModels()
}

@Composable
fun UserScreen(viewModel: UserViewModel = hiltViewModel()) { }
```

---

## 3. Scopes: Application, Screen, Request

### iOS: Swinject Scopes

```swift
// Application Scope (singleton)
container.register(AnalyticsProtocol.self) { _ in Analytics() }
    .inObjectScope(.container)

// Screen Scope — child container
let screenContainer = Container(parent: container)
screenContainer.register(ProfileCoordinator.self) { r in
    ProfileCoordinator(repo: r.resolve(UserRepositoryProtocol.self)!)
}.inObjectScope(.container)

// Request Scope — graph
container.register(RequestContext.self) { _ in RequestContext() }
    .inObjectScope(.graph)
```

### Android: Hilt Scopes

```kotlin
// SingletonComponent → ActivityRetainedComponent → ViewModelComponent → ActivityComponent

@Provides @Singleton  // Application scope
fun provideDatabase(context: Context): AppDatabase

@Provides @ActivityScoped  // Activity scope
fun provideNavigator(activity: Activity): Navigator

@HiltViewModel  // ViewModel scope автоматически
class ProfileViewModel @Inject constructor(...)
```

| Scope | iOS (Swinject) | Android (Hilt) |
|-------|----------------|----------------|
| **Application** | `.container` | `@Singleton` |
| **Screen** | Child Container | `@ActivityRetainedScoped` |
| **ViewModel** | — | `@ViewModelScoped` |
| **Request** | `.graph` | Custom Scope |
| **Per-call** | `.transient` | Без аннотации |

---

## 4. Альтернативы: Needle, Factory, Koin

### iOS: Factory

```swift
import Factory

extension Container {
    var apiClient: Factory<APIClientProtocol> { self { APIClient() }.singleton }
    var userRepository: Factory<UserRepositoryProtocol> {
        self { UserRepositoryImpl(api: self.apiClient()) }
    }
}

struct UserView: View {
    @Injected(\.userRepository) private var repository
}
```

### Android: Koin

```kotlin
val appModule = module {
    single<ApiClient> { ApiClient() }
    single<UserRepository> { UserRepositoryImpl(get()) }
    viewModelOf(::UserViewModel)
}

class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin { modules(appModule) }
    }
}

@Composable
fun UserScreen(viewModel: UserViewModel = koinViewModel()) { }
```

---

## 5. KMP DI: Koin или kotlin-inject

### Koin для KMP

```kotlin
// commonMain
val commonModule = module {
    single<UserRepository> { UserRepositoryImpl(get()) }
}

expect fun platformModule(): Module

// androidMain
actual fun platformModule() = module {
    single<DatabaseDriver> { AndroidSqliteDriver(Schema, get(), "app.db") }
}

// iosMain
actual fun platformModule() = module {
    single<DatabaseDriver> { NativeSqliteDriver(Schema, "app.db") }
}
```

### kotlin-inject (Compile-time)

```kotlin
@Inject class UserRepositoryImpl(private val api: Api) : UserRepository

@Component
abstract class CommonComponent {
    abstract val userRepository: UserRepository
    @Provides protected fun provideApi(): Api = ApiImpl()
}
```

---

## 6. Шесть распространённых ошибок

### 1. Service Locator вместо DI

```swift
// ❌ Зависимость скрыта
class UserViewModel {
    private let repo = Container.shared.resolve(UserRepositoryProtocol.self)!
}
// ✅ Явная зависимость
class UserViewModel {
    init(repo: UserRepositoryProtocol) { self.repo = repo }
}
```

### 2. Circular Dependencies

```swift
// ❌ A→B→A
// ✅ Выделить общий протокол или разбить на мелкие классы
```

### 3. Слишком много зависимостей (>5)

```kotlin
// ❌ God Object
class MegaViewModel(repo1, repo2, repo3, repo4, repo5, analytics, logger, cache)
// ✅ Разбить на UseCase'ы
class CheckoutViewModel(processCheckout: ProcessCheckoutUseCase, analytics)
```

### 4. Неправильный Scope

```swift
// ❌ Screen state как singleton
.inObjectScope(.container)
// ✅ Transient для per-screen
.inObjectScope(.transient)
```

### 5. Force Unwrap при resolve

```swift
// ❌ Crash в runtime
container.resolve(UserViewModel.self)!
// ✅ Guard или compile-time DI (Needle/Factory)
```

### 6. Зависимость от реализации

```kotlin
// ❌ Конкретный класс
class ViewModel(private val repo: UserRepositoryImpl)
// ✅ Интерфейс
class ViewModel(private val repo: UserRepository)
```

---

## 7. Три ментальные модели

### Модель 1: Граф как дерево

```
Application (Singleton)
├── APIClient, Database, Analytics
├── Screen A (Screen Scope) → ViewModelA
└── Screen B (Screen Scope) → ViewModelB
```

### Модель 2: Время жизни = Scope

- **Singleton** — пока App работает
- **Screen** — пока экран открыт
- **ViewModel** — пока ViewModel жив
- **Transient** — создаётся каждый раз

### Модель 3: Инверсия контроля

```
БЕЗ DI: ViewModel → Repository → API (VM контролирует)
С DI:   Container → API → Repository → ViewModel (Container контролирует)
```

---

## 8. Quiz: Проверь понимание

**Q1:** Какой фреймворк даёт compile-time проверку?
- A) Swinject  B) Koin  C) Hilt  D) Все

<details><summary>Ответ</summary>C) Hilt — kapt/ksp проверяет граф. Needle на iOS тоже.</details>

**Q2:** Какой scope для Repository с кэшем?
- A) Transient  B) Singleton  C) ViewModel  D) Activity

<details><summary>Ответ</summary>B) Singleton — кэш общий для всех экранов.</details>

**Q3:** Что не так с `@Injected` в ViewModel?
```swift
class ProfileViewModel: ObservableObject {
    @Injected(\.repository) private var repository
}
```

<details><summary>Ответ</summary>Service Locator — зависимости скрыты, сложнее тестировать. Constructor injection лучше.</details>

---

## 9. Связь с другими темами

[[android-dependency-injection]] — Android DI экосистема включает Hilt (официальный, compile-time, поверх Dagger), Koin (runtime, DSL-based, KMP-совместимый), Dagger (низкоуровневый, максимальная производительность) и kotlin-inject (compile-time, KMP). Заметка детально разбирает Hilt components hierarchy, scopes, @AssistedInject, multibinding и тестирование с @UninstallModules. Понимание Android DI необходимо для сравнения с iOS-подходами и для выбора DI-фреймворка в KMP-проектах.

[[ios-dependency-injection]] — iOS DI менее стандартизирован, чем Android: нет официального фреймворка. Swinject (runtime, container-based), Needle (compile-time, code generation), Factory (property wrapper, SwiftUI-friendly) — каждый решает проблему по-своему. Заметка объясняет Container hierarchies, Assembly pattern, @Injected property wrapper и тестирование через mock-замену в контейнере. Сравнение с Hilt показывает, как отсутствие единого стандарта влияет на архитектурные решения.

[[dependency-injection-fundamentals]] — Фундаментальные принципы DI: Inversion of Control, Composition Root, Constructor vs Property vs Method injection, Service Locator antipattern. Заметка объясняет, зачем нужен DI (тестируемость, модульность, loose coupling), и как правильно проектировать граф зависимостей. Эти знания первичны — без них использование Hilt или Swinject превращается в карго-культ без понимания целей.

---

## Источники и дальнейшее чтение

- Martin R. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design.* — Глава о Dependency Inversion Principle и Composition Root — теоретическая основа DI. Объясняет, почему зависимости должны указывать на абстракции, а не на реализации, и как это влияет на архитектуру мобильных приложений.
- Gamma E., Helm R., Johnson R., Vlissides J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software.* — Паттерны Factory, Abstract Factory и Strategy напрямую связаны с DI. Книга закладывает основу для понимания инверсии управления и подмены реализаций через интерфейсы.
- Moskala M. (2021). *Effective Kotlin: Best Practices.* — Практические рекомендации по организации DI в Kotlin-проектах: конструкторы, default parameters, Koin DSL и интеграция с Coroutines scope. Актуальна для Android и KMP.

---

## Резюме

| Проект | iOS | Android | KMP |
|--------|-----|---------|-----|
| **Простой** | Manual DI | Manual DI | Koin |
| **Средний** | Factory | Hilt | Koin |
| **Большой** | Needle | Hilt | kotlin-inject |

**Правило:** Constructor Injection > Property Injection > Service Locator

---

## Проверь себя

> [!question]- Почему Service Locator считается антипаттерном по сравнению с Constructor Injection?
> Service Locator скрывает зависимости: глядя на конструктор класса, невозможно понять, что ему нужно для работы. Это усложняет тестирование (нужно настраивать глобальный контейнер), затрудняет рефакторинг и может привести к runtime-ошибкам, если зависимость не зарегистрирована. Constructor Injection делает зависимости явными и проверяемыми на этапе компиляции.

> [!question]- Сценарий: Repository с кэшем зарегистрирован как Transient. Какую проблему это создаёт?
> Каждый запрос создаёт новый экземпляр Repository с пустым кэшем. Кэширование теряет смысл, потому что данные не сохраняются между вызовами. Repository с кэшем должен быть Singleton -- общий для всех экранов.

> [!question]- Почему у ViewModel больше 5 зависимостей -- это code smell?
> Это признак God Object -- класс делает слишком много. Решение: разбить логику на UseCase-классы, каждый из которых инкапсулирует одну операцию бизнес-логики. ViewModel получает 2-3 UseCase вместо 8 Repository/Service.

> [!question]- Какой DI-фреймворк выбрать для KMP-проекта и почему?
> Для простых и средних проектов -- Koin: runtime-based, DSL для commonMain, поддерживает expect/actual для платформенных модулей. Для больших проектов -- kotlin-inject: compile-time safety, генерация кода. Hilt и Swinject не работают в commonMain, так как платформо-специфичны.

---

## Ключевые карточки

Какой DI-фреймворк даёт compile-time проверку графа зависимостей?
?
Hilt (Android) через kapt/ksp проверяет граф на этапе компиляции. На iOS -- Needle делает то же самое через code generation. Koin и Swinject -- runtime, ошибки обнаруживаются только при запуске.

Чем отличаются Swinject Scopes от Hilt Scopes?
?
Swinject: .container (singleton), child container (screen), .graph (request), .transient (per-call). Hilt: @Singleton, @ActivityRetainedScoped, @ViewModelScoped, @ActivityScoped, без аннотации (transient). Hilt имеет встроенную иерархию компонентов.

Что такое Composition Root в контексте DI?
?
Composition Root -- единственное место в приложении, где создаются и связываются все зависимости. На iOS это AppDelegate/App struct, на Android -- Application class или Hilt modules. Вся остальная логика получает зависимости через инъекцию.

Как Koin решает проблему платформенных зависимостей в KMP?
?
Через expect/actual для platformModule(): commonModule содержит общие зависимости (Repository, UseCase), а platformModule() в androidMain и iosMain регистрирует платформенные реализации (DatabaseDriver, HttpEngine). Оба модуля объединяются при старте через startKoin.

Какое правило определяет выбор между Constructor, Property и Service Locator injection?
?
Constructor Injection > Property Injection > Service Locator. Constructor делает зависимости явными и проверяемыми на этапе компиляции. Property injection используется когда конструктор недоступен (Android Activity). Service Locator -- только как крайняя мера.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-kmp-patterns]] | expect/actual и SKIE для KMP-разработки |
| Углубиться | [[android-hilt-deep-dive]] | Детальное погружение в Hilt из раздела Android |
| Смежная тема | [[clean-code-solid]] | SOLID-принципы как теоретическая основа DI |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |
