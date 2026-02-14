---
title: "Architecture Interview Questions 2025: MVVM, MVI, Clean Architecture"
created: 2025-12-26
modified: 2026-02-13
type: reference
status: published
confidence: high
tags:
  - topic/career
  - type/reference
  - level/advanced
  - interview
related:
  - "[[android-questions]]"
  - "[[system-design-android]]"
  - "[[technical-interview]]"
prerequisites:
  - "[[android-questions]]"
  - "[[kotlin-questions]]"
reading_time: 18
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Architecture Interview Questions: проектирование Android приложений

Senior позиции требуют не только знания паттернов, но понимания ПОЧЕМУ выбрать один над другим. MVI vs MVVM — не про "что лучше", а про trade-offs для конкретного проекта. Clean Architecture — не dogma, а tool. Этот справочник — ключевые вопросы по архитектуре с ответами, которые покажут senior thinking.

---

## MVVM

### Что такое MVVM и как работает?

```
MVVM = Model-View-ViewModel

┌─────────────────────────────────────────────────┐
│                    VIEW                          │
│   (Activity/Fragment/Composable)                │
│   • Отображает UI state                          │
│   • Передаёт user events в ViewModel            │
└───────────────────┬─────────────────────────────┘
                    │ observes StateFlow/LiveData
                    ↓
┌─────────────────────────────────────────────────┐
│                 VIEWMODEL                        │
│   • Держит UI state                              │
│   • Обрабатывает user events                    │
│   • Вызывает Use Cases/Repository               │
│   • Переживает configuration changes            │
└───────────────────┬─────────────────────────────┘
                    │ calls
                    ↓
┌─────────────────────────────────────────────────┐
│                   MODEL                          │
│   (Repository, Use Cases, Data Sources)         │
│   • Business logic                               │
│   • Data operations                              │
└─────────────────────────────────────────────────┘
```

### Как обрабатывать one-time events в MVVM?

```kotlin
// Проблема: UI state переживает rotation.
// Но navigation/snackbar должны показаться ОДИН раз.

// Решение 1: Channel (recommended)
class ViewModel : ViewModel() {
    private val _events = Channel<UiEvent>(Channel.BUFFERED)
    val events = _events.receiveAsFlow()

    fun onButtonClick() {
        viewModelScope.launch {
            _events.send(UiEvent.NavigateToDetails)
        }
    }
}

// В UI:
LaunchedEffect(Unit) {
    viewModel.events.collect { event ->
        when (event) {
            is UiEvent.NavigateToDetails -> navController.navigate(...)
        }
    }
}

// Решение 2: SharedFlow с replay = 0
private val _events = MutableSharedFlow<UiEvent>()
```

### В чём проблема с LiveData для events?

```kotlin
// Проблема: LiveData всегда re-emits последнее значение
// при новой подписке (rotation, fragment recreation)

class ViewModel : ViewModel() {
    private val _navigateEvent = MutableLiveData<Event<String>>()
}

// Event wrapper (устаревший подход):
class Event<T>(private val content: T) {
    private var hasBeenHandled = false
    fun getContentIfNotHandled(): T? {
        return if (hasBeenHandled) null
        else { hasBeenHandled = true; content }
    }
}

// Современное решение: Channel/SharedFlow (см. выше)
```

---

## MVI

### Что такое MVI и когда использовать?

```
MVI = Model-View-Intent

┌─────────────────────────────────────────────────┐
│                    VIEW                          │
│   • Renders State                                │
│   • Emits Intents (user actions)                │
└───────────────────┬──────────────────────┬──────┘
                    │ Intent               │ State
                    ↓                      │
┌─────────────────────────────────────────────────┐
│                 PROCESSOR                        │
│   (ViewModel/Store)                             │
│   • Receives Intent                              │
│   • Produces new State                          │
│   • Single source of truth                      │
└───────────────────┬─────────────────────────────┘
                    │ observes
                    ↓
┌─────────────────────────────────────────────────┐
│                   STATE                          │
│   (Immutable data class)                        │
│   • Everything needed to render UI              │
└─────────────────────────────────────────────────┘

Unidirectional Data Flow:
Intent → Processor → State → View → Intent
```

### Пример MVI implementation

```kotlin
// State
data class SearchState(
    val query: String = "",
    val results: List<Item> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// Intents
sealed class SearchIntent {
    data class QueryChanged(val query: String) : SearchIntent()
    data object Search : SearchIntent()
    data object Retry : SearchIntent()
}

// ViewModel
class SearchViewModel(private val repo: Repository) : ViewModel() {
    private val _state = MutableStateFlow(SearchState())
    val state = _state.asStateFlow()

    fun handleIntent(intent: SearchIntent) {
        when (intent) {
            is SearchIntent.QueryChanged -> {
                _state.update { it.copy(query = intent.query) }
            }
            is SearchIntent.Search -> search()
            is SearchIntent.Retry -> search()
        }
    }

    private fun search() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            try {
                val results = repo.search(_state.value.query)
                _state.update { it.copy(results = results, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }
}
```

### MVVM vs MVI — когда что выбрать?

```
MVVM:
├── Pros:
│   ├── Simpler для небольших экранов
│   ├── Меньше boilerplate
│   └── Легче onboard новых разработчиков
├── Cons:
│   ├── Multiple state streams → hard to debug
│   └── Side effects scattered
└── Use when:
    ├── Simple screens
    ├── Team new to reactive
    └── Quick iteration needed

MVI:
├── Pros:
│   ├── Single source of truth
│   ├── State легко логировать (time-travel debug)
│   ├── Predictable state changes
│   └── Easier testing (pure functions)
├── Cons:
│   ├── More boilerplate
│   ├── Steeper learning curve
│   └── Reducer can become complex
└── Use when:
    ├── Complex UI state
    ├── Heavy state management
    ├── Need for debugging/logging
    └── Long-term maintainability

Senior answer: "It depends on project needs.
For simple forms, MVVM is enough.
For complex dashboards with many interactions, MVI provides
better predictability and debugging."
```

---

## Clean Architecture

### Что такое Clean Architecture?

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                       │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  UI (Activity/Fragment/Composable)                  │   │
│   │  ViewModel                                          │   │
│   └─────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│   ─────────────────────────────────────────────────────────  │
│                            ↓                                 │
│                     DOMAIN LAYER                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Use Cases / Interactors                            │   │
│   │  Domain Models                                      │   │
│   │  Repository Interfaces                              │   │
│   └─────────────────────────────────────────────────────┘   │
│                            ↓                                 │
│   ─────────────────────────────────────────────────────────  │
│                            ↓                                 │
│                       DATA LAYER                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Repository Implementations                         │   │
│   │  Data Sources (Remote, Local)                       │   │
│   │  Data Models (DTOs, Entities)                       │   │
│   └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

Dependency Rule:
• Outer layers depend on inner layers
• Domain layer has NO dependencies on other layers
• Data layer implements interfaces defined in Domain
```

### Зачем нужны Use Cases?

```kotlin
// Use Case = single business operation
class GetUserProfileUseCase(
    private val userRepository: UserRepository,
    private val analyticsRepository: AnalyticsRepository
) {
    suspend operator fun invoke(userId: String): UserProfile {
        analyticsRepository.trackProfileView(userId)
        return userRepository.getProfile(userId)
    }
}

// Benefits:
// 1. Single Responsibility — one operation per class
// 2. Testable — easy to mock dependencies
// 3. Reusable — can be called from multiple ViewModels
// 4. Encapsulates business logic — not in ViewModel

// ViewModel uses:
class ProfileViewModel(
    private val getUserProfile: GetUserProfileUseCase
) {
    fun loadProfile(id: String) {
        viewModelScope.launch {
            val profile = getUserProfile(id)
            _state.update { it.copy(profile = profile) }
        }
    }
}
```

### Когда Use Cases избыточны?

```kotlin
// Over-engineering example:
class GetUserByIdUseCase(private val repo: UserRepository) {
    suspend operator fun invoke(id: String) = repo.getUser(id)
}
// Это просто прокси! Никакой логики.

// Лучше:
class UserViewModel(private val userRepository: UserRepository) {
    // Call repository directly for simple CRUD
}

// Use Cases нужны когда:
// 1. Combine multiple repositories
// 2. Complex business logic
// 3. Need for reuse across ViewModels
// 4. Team agreement на always use cases
```

---

## Modularization

### Как структурировать multi-module проект?

```
app/                    ← Точка входа, DI setup
│
├── feature/
│   ├── feature-home/   ← UI + ViewModel для home
│   ├── feature-profile/
│   └── feature-settings/
│
├── core/
│   ├── core-ui/        ← Общие UI компоненты, theme
│   ├── core-network/   ← Retrofit, API клиенты
│   ├── core-database/  ← Room, DAOs
│   ├── core-domain/    ← Use Cases, Domain models
│   └── core-common/    ← Utilities, extensions
│
└── data/
    ├── data-user/      ← Repository impl для user
    └── data-product/

Dependencies:
• feature modules → core modules
• core-domain → ничего (чистый Kotlin)
• data modules → core-domain (implements interfaces)
• feature modules НЕ зависят друг от друга
```

### Преимущества modularization

```
Build time:
├── Parallel compilation
├── Incremental builds (change in one module ≠ rebuild all)
└── ~30-50% faster builds

Scalability:
├── Teams can own modules
├── Clear boundaries prevent spaghetti
└── Easier code review

Reusability:
├── Share modules across apps
└── Dynamic feature modules (Play Feature Delivery)

Testability:
├── Test modules in isolation
└── Faster test execution
```

---

## Dependency Injection

### Hilt vs Koin vs Manual DI — когда что?

```
Hilt:
├── Compile-time verification
├── Android-specific (scopes, ViewModel)
├── Google-backed, recommended for Android
├── Steeper learning curve
└── Use for: production Android apps

Koin:
├── Simpler API (DSL-based)
├── Runtime resolution
├── Kotlin-first
├── No code generation
└── Use for: simpler projects, quick prototyping

Manual DI:
├── No library overhead
├── Full control
├── More boilerplate
└── Use for: small apps, libraries

Senior answer: "For Android production apps,
I prefer Hilt because of compile-time safety
and official Android support. For KMP projects
where Hilt isn't available, Koin works well."
```

### Как работает Hilt?

```kotlin
// Setup
@HiltAndroidApp
class MyApp : Application()

// Module
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .build()
}

// Injection
@HiltViewModel
class MyViewModel @Inject constructor(
    private val repository: Repository
) : ViewModel()

// Scopes:
// SingletonComponent — app lifetime
// ActivityComponent — activity lifetime
// ViewModelComponent — ViewModel lifetime
// FragmentComponent — fragment lifetime
```

---

## Testing

### Как тестировать ViewModel?

```kotlin
class UserViewModelTest {
    private lateinit var viewModel: UserViewModel
    private val repository: UserRepository = mockk()

    @Before
    fun setup() {
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser updates state with user`() = runTest {
        // Given
        val user = User(id = "1", name = "John")
        coEvery { repository.getUser("1") } returns user

        // When
        viewModel.loadUser("1")

        // Then
        assertEquals(user, viewModel.state.value.user)
        assertEquals(false, viewModel.state.value.isLoading)
    }

    @Test
    fun `loadUser shows error on failure`() = runTest {
        // Given
        coEvery { repository.getUser(any()) } throws Exception("Network error")

        // When
        viewModel.loadUser("1")

        // Then
        assertEquals("Network error", viewModel.state.value.error)
    }
}
```

### Что тестировать в каждом слое?

```
Presentation Layer:
├── ViewModel: state transitions, event handling
├── UI: snapshot tests, integration tests
└── Не тестируй: Android framework code

Domain Layer:
├── Use Cases: business logic, edge cases
├── Unit tests with mocked repositories
└── 100% покрытие желательно

Data Layer:
├── Repository: data transformation, error handling
├── Local: Room DAO queries (instrumented)
├── Remote: API response parsing
└── Integration tests для complex flows
```

---

## Common Questions

### Как обрабатывать navigation в clean architecture?

```kotlin
// Option 1: Events from ViewModel
sealed class NavigationEvent {
    data class ToDetails(val id: String) : NavigationEvent()
    data object Back : NavigationEvent()
}

class ViewModel {
    private val _navigation = Channel<NavigationEvent>()
    val navigation = _navigation.receiveAsFlow()

    fun onItemClick(id: String) {
        viewModelScope.launch {
            _navigation.send(NavigationEvent.ToDetails(id))
        }
    }
}

// Option 2: Navigation Use Case
class NavigateToDetailsUseCase(private val navigator: Navigator) {
    operator fun invoke(id: String) = navigator.navigateTo(Details(id))
}
```

### Как структурировать state в сложном экране?

```kotlin
// Single state object (recommended)
data class CheckoutState(
    val items: List<CartItem> = emptyList(),
    val address: Address? = null,
    val paymentMethod: PaymentMethod? = null,
    val isLoading: Boolean = false,
    val error: String? = null,
    val step: CheckoutStep = CheckoutStep.CART
)

// Pros:
// - Single source of truth
// - Easy to debug/log
// - Atomic updates

// Cons:
// - Can become large
// - Recomposition scope (Compose)

// Solution for recomposition:
// Split into smaller state classes
// Use derivedStateOf for computed values
```

---

## Red Flags в ответах

```
❌ "Всегда использую MVVM/MVI"
   → Should choose based on project needs

❌ "Use Cases для каждой операции"
   → Over-engineering для simple CRUD

❌ "Clean Architecture — единственный правильный подход"
   → It's a tool, not a religion

❌ "Не использую DI в маленьких проектах"
   → Even small projects benefit from testability

✓ Good answer: "I choose architecture based on
   project size, team experience, and long-term
   maintenance requirements."
```

---

## Связь с другими темами

- **[[android-questions]]** — Базовые Android-вопросы (lifecycle, Compose, coroutines) — фундамент, на котором строятся архитектурные решения. Невозможно проектировать MVI без понимания StateFlow, или Clean Architecture без знания ViewModel lifecycle. Интервьюеры часто переходят от базовых вопросов к архитектурным, проверяя глубину понимания.

- **[[system-design-android]]** — System Design — расширение архитектурных вопросов на уровень всей системы: не только UI-архитектура, но и networking, caching, sync, и scaling. На Staff+ интервью System Design занимает до 30% всего процесса. Умение масштабировать архитектурное мышление от экрана до системы — ключевой Senior+ навык.

- **[[technical-interview]]** — Архитектурные вопросы — один из столпов технического интервью наряду с coding и System Design. Понимание формата интервью помогает правильно структурировать ответы: не просто описать паттерн, а обсудить trade-offs и показать decision-making process.

---

## Источники и дальнейшее чтение

- **Xu A. (2020). System Design Interview.** — Даёт фреймворк для обсуждения архитектурных решений на интервью: как структурировать ответ, какие trade-offs обсуждать, как рисовать диаграммы. Хотя фокус на backend, подход полностью применим к mobile architecture.

- **McDowell G.L. (2015). Cracking the Coding Interview.** — Главы об Object-Oriented Design показывают, как интервьюеры оценивают архитектурное мышление. Полезна для понимания формата вопросов и ожидаемой глубины ответов на Senior-позиции.

- **Larson W. (2022). Staff Engineer: Leadership Beyond the Management Track.** — Объясняет, как архитектурные решения связаны с technical leadership на Staff+ уровне. Помогает выйти за рамки паттернов к стратегическому мышлению об архитектуре.

---

## Источники

- [ProAndroidDev: Android Architecture](https://proandroiddev.com/android-interview-series-2024-part-8-android-architecture-07ca74eee000)
- [Medium: MVI and Clean Architecture](https://medium.com/@sharmapraveen91/mastering-mvi-and-clean-architecture-20-advanced-interview-questions-every-android-developer-bf0d9e02d22b)
- [DroidChef: Architecture Patterns](https://blog.droidchef.dev/android-architecture-patterns-a-comprehensive-pre-interview-guide/)
- [GitHub: Android Interview Questions](https://github.com/amitshekhariitbhu/android-interview-questions)

---

## Куда дальше

### Общая архитектура

**Паттерны:**
→ [[microservices-vs-monolith]] — когда монолит, когда микросервисы
→ [[api-design]] — REST vs GraphQL vs gRPC
→ [[event-driven-architecture]] — Event Sourcing, Saga

**Производительность:**
→ [[caching-strategies]] — стратегии кэширования
→ [[performance-optimization]] — от 3s к 300ms

### Mobile-specific

→ [[system-design-android]] — Mobile System Design интервью
→ [[android-architecture-patterns]] — MVVM, MVI на практике
→ [[android-modularization]] — multi-module проекты

---

---

## Проверь себя

> [!question]- Новый проект: 3 экрана, 2 разработчика, дедлайн 4 недели. Ты предлагаешь Clean Architecture с Use Cases или прямой MVVM без domain layer? Обоснуй.
> Для маленького проекта с жёстким дедлайном — MVVM без отдельного domain layer. Use Cases для simple CRUD — это over-engineering (просто прокси к repository). Clean Architecture оправдана когда: (1) несколько repositories комбинируются, (2) бизнес-логика сложная, (3) reuse Use Cases между ViewModels. Senior answer: "It depends on project needs" — Clean Architecture это tool, не religion.

> [!question]- Почему для one-time events (navigation, snackbar) нельзя использовать StateFlow, и какое решение правильное?
> StateFlow всегда replay last value новым collectors. При rotation новый collector получит уже обработанный event — navigation произойдёт дважды. Решения: (1) Channel с receiveAsFlow() — event потребляется один раз. (2) SharedFlow с replay = 0. Event wrapper (Event<T>) с hasBeenHandled — устаревший подход, не рекомендуется. Channel — recommended solution.

> [!question]- Команда спорит: Hilt vs Koin для KMP проекта. Какой выбор и почему?
> Koin — потому что Hilt привязан к Android (использует kapt/annotation processing). В KMP-проекте shared module должен быть чистым Kotlin, и Hilt там не работает. Koin: DSL-based, Kotlin-first, no code generation, runtime resolution. Для чисто Android-проекта — Hilt (compile-time safety, official Android support). Для KMP — Koin или kotlin-inject.

> [!question]- Как правильно структурировать multi-module проект, чтобы feature modules не зависели друг от друга?
> Структура: app/ (DI setup, точка входа) -> feature/ (feature-home, feature-profile — независимые) -> core/ (core-ui, core-network, core-database, core-domain) -> data/ (data-user, data-product). Feature modules зависят только от core modules. core-domain не зависит ни от чего (чистый Kotlin). data modules implements interfaces из core-domain. Навигация между features — через абстракцию (NavigationEvent) или Navigation Component.

> [!question]- Почему MVI лучше MVVM для time-travel debugging и как это работает?
> В MVI каждое изменение state проходит через explicit intent -> reducer -> new state. Все state transitions логируемы: записывая sequence of intents, можно воспроизвести точное состояние UI в любой момент. В MVVM state может меняться из нескольких мест (multiple LiveData/StateFlow), что делает debugging непредсказуемым. MVI: single source of truth + immutable state = полная воспроизводимость.

---

## Ключевые карточки

MVVM vs MVI — когда что выбрать?
?
MVVM: simple screens, быстрая итерация, команда новая в reactive. MVI: complex UI state, heavy state management, нужен debugging/logging, долгосрочная поддержка. Senior: "It depends on project needs."

Clean Architecture — Dependency Rule?
?
Outer layers зависят от inner layers. Domain layer не зависит ни от чего. Data layer implements interfaces из Domain. Presentation зависит от Domain. Зависимости направлены внутрь.

Когда Use Cases избыточны?
?
Когда Use Case — просто прокси к repository без дополнительной логики. Нужны когда: (1) combine multiple repositories, (2) complex business logic, (3) reuse across ViewModels, (4) team agreement на always use cases.

Hilt vs Koin — ключевые различия?
?
Hilt: compile-time verification, Android-specific (scopes, ViewModel), Google-backed. Steeper learning curve. Koin: simpler DSL API, runtime resolution, Kotlin-first, no code generation. Hilt для production Android, Koin для KMP и простых проектов.

Modularization — главные преимущества?
?
Build time: parallel compilation, incremental builds (~30-50% faster). Scalability: teams own modules, clear boundaries. Reusability: share across apps. Testability: test modules in isolation.

One-time events в MVVM — правильное решение?
?
Channel с receiveAsFlow() или SharedFlow с replay = 0. Не StateFlow (replays last value при rotation). Не LiveData Event wrapper (устаревший подход). Channel — recommended.

Что тестировать в каждом слое Clean Architecture?
?
Presentation: ViewModel state transitions, event handling. Domain: Use Case business logic, edge cases (100% покрытие). Data: Repository data transformation, error handling, Room DAO queries (instrumented), API response parsing.

---

## Куда дальше

| Направление | Ссылка | Зачем |
|-------------|--------|-------|
| Следующий шаг | [[system-design-android]] | Mobile System Design — расширение архитектуры на уровень системы |
| Углубиться | [[android-architecture-patterns]] | MVVM и MVI на практике с реальными примерами |
| Смежная тема | [[design-patterns]] | Общие паттерны проектирования за пределами mobile |
| Обзор | [[technical-interview]] | Формат технического интервью — контекст для архитектурных вопросов |

---

*Обновлено: 2026-02-13*

---

*Проверено: 2026-02-13*
