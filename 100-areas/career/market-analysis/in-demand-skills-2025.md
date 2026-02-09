---
title: "In-Demand Android Skills 2025: что учить, что забыть"
created: 2025-12-26
modified: 2025-12-26
type: deep-dive
status: published
confidence: high
tags:
  - topic/career
  - topic/android
  - type/market-analysis
  - level/senior
related:
  - "[[android-job-market-2025]]"
  - "[[salary-benchmarks]]"
  - "[[interview-process]]"
---

# Android Skills 2025: эволюция от кода к оркестрации

Несколько лет назад Java была доминантой, XML — единственным UI, а RxJava — признаком продвинутости. Сейчас Kotlin — дефолт, Jetpack Compose заменяет XML, а KMP обещает shared logic на iOS. И над всем этим — 65% разработчиков, использующих AI еженедельно. Роль изменилась: меньше boilerplate, больше architecture decisions.

---

## Терминология

| Термин | Что это |
|--------|---------|
| **UDF** | Unidirectional Data Flow — данные текут в одном направлении |
| **KMP** | Kotlin Multiplatform — shared code между Android/iOS/Desktop |
| **MVI** | Model-View-Intent — архитектура с state machine |
| **Compose** | Декларативный UI toolkit, замена XML |

---

## Эволюция: как мы сюда пришли

```
2015-2018: Java + XML + AsyncTask + MVP
     ↓
2018-2019: Kotlin появляется, MVVM становится стандартом
     ↓
2019-2022: Kotlin Coroutines + Flow заменяют RxJava
           MVVM — дефолт
     ↓
2020-2024: Jetpack Compose делает UDF мейнстримом
           MVI набирает популярность
     ↓
2025:      MVI + State Machine для complex apps
           Compose — новый стандарт
           KMP — в production у Google Docs, Netflix
           AI — часть ежедневного workflow
```

Каждый виток добавлял abstraction layer. От "напиши всё руками" к "оркестрируй готовые решения".

---

## Три уровня навыков

### Must-Have: без этого не рассматривают

| Навык | Почему критично | % вакансий |
|-------|-----------------|------------|
| **Kotlin** | Официальный язык. Java — legacy | 70%+ требуют |
| **Jetpack Compose** | Новые проекты пишут на Compose | Растёт экспоненциально |
| **Coroutines/Flow** | Async-first мир. RxJava уходит | Стандарт |
| **MVVM/Clean Architecture** | Ожидается на Senior | Baseline |

Если чего-то из этого нет в твоём опыте — это первый приоритет. Без Kotlin + Compose + Coroutines в 2025 ты ограничен legacy проектами.

### Strong Advantage: выделяют из толпы

| Навык | Почему ценится | Impact на зарплату |
|-------|----------------|-------------------|
| **KMP (Kotlin Multiplatform)** | Google Docs, Netflix, McDonald's используют | +10-20% |
| **MVI Architecture** | State machine, predictable, testable | Senior+ роли |
| **System Design** | Mobile architecture interviews | Обязательно для Staff+ |
| **AI Tools Proficiency** | 55% рост продуктивности | Становится baseline |

KMP — главный differentiator 2025. Android-разработчик, который может деливерить на iOS без полного знания Swift — редкость.

### Nice-to-Have: приятный бонус

```
• Compose Multiplatform (iOS, Desktop, Web)
• Gradle/Build optimization
• CI/CD (GitHub Actions, Bitrise)
• Performance profiling (Memory, CPU, Battery)
• Accessibility (a11y)
```

---

## Deep Dive: Must-Have навыки

### Kotlin: уровень владения

Базовый Kotlin знают все. Что отличает Senior:

```kotlin
// Junior: знает синтаксис
data class User(val name: String, val age: Int)

// Mid: использует scope functions правильно
val user = fetchUser()?.let { validateUser(it) } ?: defaultUser

// Senior: понимает internals и оптимизирует
inline fun <reified T> parseJson(json: String): T =
    Json.decodeFromString(json)

// Senior+: DSL, контракты, multiplatform expect/actual
@OptIn(ExperimentalContracts::class)
fun requireNotEmpty(value: String?) {
    contract { returns() implies (value != null) }
    require(!value.isNullOrEmpty())
}
```

**Что проверяют на интервью:**
- Delegation (by lazy, by observable)
- Inline functions и reified generics
- Sealed classes и exhaustive when
- Coroutine internals (Continuation, Dispatcher)

### Jetpack Compose: новый стандарт

Compose — не просто другой синтаксис. Это paradigm shift.

```kotlin
// XML-мышление (плохо в Compose):
// "У меня есть View, я меняю его state"

// Compose-мышление (правильно):
// "UI — функция от state. State меняется → UI перерисовывается"

@Composable
fun UserCard(
    user: User,
    onEditClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(modifier = modifier) {
        Column {
            Text(text = user.name, style = MaterialTheme.typography.titleMedium)
            Text(text = user.email, style = MaterialTheme.typography.bodyMedium)
            Button(onClick = onEditClick) {
                Text("Edit")
            }
        }
    }
}
```

**Что ожидают от Senior:**
- Понимание recomposition и оптимизация
- State hoisting и правильная архитектура
- Custom layouts и modifiers
- Animation APIs
- Side effects (LaunchedEffect, SideEffect, DisposableEffect)

### Coroutines/Flow: async-first

RxJava ещё жив в legacy, но новые проекты — Coroutines.

```kotlin
// Базовый уровень: использование
viewModelScope.launch {
    val users = repository.getUsers()
    _state.value = UiState.Success(users)
}

// Senior уровень: понимание structured concurrency
suspend fun fetchAllData() = coroutineScope {
    val users = async { userRepository.getUsers() }
    val posts = async { postRepository.getPosts() }

    // Если один fails — другой cancels
    CombinedData(users.await(), posts.await())
}

// Senior+: custom Flows и операторы
fun <T> Flow<T>.throttleFirst(periodMillis: Long): Flow<T> = flow {
    var lastEmissionTime = 0L
    collect { value ->
        val currentTime = System.currentTimeMillis()
        if (currentTime - lastEmissionTime >= periodMillis) {
            lastEmissionTime = currentTime
            emit(value)
        }
    }
}
```

**Критические темы:**
- CoroutineContext, Dispatchers, SupervisorJob
- Exception handling в coroutines
- Hot vs Cold Flows
- StateFlow vs SharedFlow vs Channel

---

## Deep Dive: Strong Advantage

### KMP (Kotlin Multiplatform)

Google Docs в production на KMP. Netflix использует для networking. McDonald's — для business logic.

```
KMP Architecture (типичная):

┌─────────────────────────────────────────┐
│            Shared Module (KMP)          │
│  ┌─────────────────────────────────┐   │
│  │  Business Logic, Use Cases      │   │
│  │  Data Models, Repositories      │   │
│  │  Networking (Ktor)              │   │
│  │  Local Storage (SQLDelight)     │   │
│  └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
         ↓                    ↓
┌─────────────────┐   ┌─────────────────┐
│   Android App   │   │     iOS App     │
│   Compose UI    │   │   SwiftUI       │
└─────────────────┘   └─────────────────┘
```

**Что нужно знать:**
- expect/actual для platform-specific
- Ktor для networking (или other HTTP clients)
- SQLDelight для local storage
- Compose Multiplatform для shared UI (опционально)

**Почему это важно для карьеры:**
- Меньше специалистов → выше зарплата
- Можешь закрывать iOS-часть без знания Swift
- Компании экономят на двух отдельных командах

### MVI Architecture

MVVM стало baseline. MVI — для complex apps.

```kotlin
// MVI: явные states и intents
sealed class UserIntent {
    object LoadUsers : UserIntent()
    data class SelectUser(val userId: String) : UserIntent()
    data class DeleteUser(val userId: String) : UserIntent()
}

data class UserState(
    val users: List<User> = emptyList(),
    val selectedUser: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

sealed class UserSideEffect {
    data class ShowToast(val message: String) : UserSideEffect()
    object NavigateToDetails : UserSideEffect()
}

class UserViewModel : ViewModel() {
    private val _state = MutableStateFlow(UserState())
    val state = _state.asStateFlow()

    private val _sideEffect = Channel<UserSideEffect>()
    val sideEffect = _sideEffect.receiveAsFlow()

    fun processIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUsers -> loadUsers()
            is UserIntent.SelectUser -> selectUser(intent.userId)
            is UserIntent.DeleteUser -> deleteUser(intent.userId)
        }
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val users = repository.getUsers()
                _state.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }
}
```

**Преимущества MVI:**
- Predictable: каждый state change — через intent
- Testable: легко воспроизвести state transitions
- Debuggable: можно логировать все intents и states
- Scalable: подходит для complex flows

### System Design

Senior+ интервью включают mobile system design. Типичные вопросы:

```
"Design Instagram feed for Android"
"Design offline-first note-taking app"
"Design real-time messaging system"
"Design image loading and caching library"
```

**Что нужно уметь:**
- Разбивать систему на components
- Обсуждать trade-offs (consistency vs availability)
- Рисовать architecture diagrams
- Оценивать performance и scaling

### AI Tools Proficiency

65% разработчиков используют AI еженедельно. 55% рост продуктивности.

```
Как AI меняет workflow:

БЕЗ AI:
1. Придумай решение
2. Напиши код
3. Найди ошибки
4. Исправь
5. Repeat

С AI:
1. Опиши задачу AI
2. Получи варианты решений
3. Выбери лучший и адаптируй
4. Review и рефакторинг
5. Deploy

Экономия: 30-50% времени на boilerplate
```

**Что использовать:**
- GitHub Copilot / Cursor — code completion
- ChatGPT / Claude — architecture discussions, problem-solving
- AI-assisted code review — поиск bugs

**Что это значит для карьеры:**
- AI автоматизирует junior-работу
- Ценность сдвигается к architecture и decisions
- "Разработчик + AI" > "Разработчик без AI"

---

## Что устарело (убери из резюме)

```
❌ Java как primary language (OK как secondary)
❌ RxJava без Coroutines знания
❌ AsyncTask, Loaders
❌ XML layouts без Compose опыта
❌ MVP без MVVM/MVI
❌ "Android Developer" без Kotlin
❌ Eclipse IDE (seriously)
```

**Grey zone (зависит от контекста):**
- Data Binding — legacy, но много проектов
- Navigation Component XML — Compose Navigation растёт
- Dagger 2 — Hilt проще, но Dagger глубже

---

## Roadmap: что учить и в каком порядке

### Если ты Mid (3-5 лет)

```
Приоритет 1: Jetpack Compose
├── Basics: layouts, modifiers, state
├── Advanced: custom layouts, animations
└── Architecture: state hoisting, navigation

Приоритет 2: Architecture deep dive
├── Clean Architecture понимание
├── MVVM → MVI transition
└── Testing архитектуры

Приоритет 3: System Design basics
├── Mobile-specific patterns
├── Offline-first design
└── Caching strategies
```

### Если ты Senior (5+ лет)

```
Приоритет 1: KMP
├── Setup и structure
├── Ktor, SQLDelight
└── expect/actual patterns

Приоритет 2: System Design mastery
├── Распределённые системы для mobile
├── Real-time communication
└── Scaling strategies

Приоритет 3: AI integration
├── AI tools в workflow
├── On-device ML (если relevant)
└── AI-assisted development patterns
```

---

## Salary Impact навыков

| Навык | Impact на зарплату | Комментарий |
|-------|-------------------|-------------|
| KMP production experience | +15-25% | Редкий, востребованный |
| System Design strong | +10-20% | Senior+ обязательно |
| Compose Multiplatform | +10-15% | Emerging, но ценится |
| AI/ML on-device | +10-20% | Нишево, но высоко оплачивается |
| Jetpack Compose expert | +5-10% | Становится baseline |
| Clean Architecture | Baseline | Ожидается от всех Senior |

---

## Что спрашивают на интервью

### Technical rounds

```
Kotlin:
• Difference between object and companion object
• When to use inline functions
• Sealed class vs enum
• Extension functions internals

Compose:
• How recomposition works
• remember vs rememberSaveable
• Side effects и их use cases
• State management patterns

Architecture:
• MVVM vs MVI trade-offs
• Clean Architecture layers
• How would you design X (open-ended)

Coroutines:
• Structured concurrency
• Exception handling
• Hot vs Cold flows
• Backpressure handling
```

### System Design rounds

```
Типичные задачи:
1. Design offline-first app с sync
2. Design image loading library
3. Design chat/messaging feature
4. Design feed with pagination

Что оценивают:
• Ability to break down problem
• Trade-off discussions
• Mobile-specific considerations
• Scalability thinking
```

---

## Практические шаги

### На этой неделе

1. **Проверь свои навыки** — есть ли must-have?
2. **Обнови проект** — добавь Compose если нет
3. **Setup AI tool** — Copilot или Cursor

### На этом месяце

1. **KMP pet project** — простой, но в production-ready structure
2. **System Design study** — 1 design task в неделю
3. **Refactor к MVI** — один модуль в существующем проекте

### На этом квартале

1. **Open source contribution** — Compose library или KMP tool
2. **Technical writing** — статья о KMP или System Design
3. **Interview practice** — 2-3 mock interviews

---

## Куда дальше

→ [[android-job-market-2025]] — состояние рынка
→ [[system-design-android]] — подготовка к design interviews
→ [[interview-process]] — полный breakdown интервью
→ [[portfolio-strategy]] — как показать skills

---

## Источники

Исследование: 20+ источников

Ключевые:
- [TechHub Asia: Android Career Outlook 2025](https://techhub.asia/android-developer-career/)
- [Medium: Modern Android Architecture 2025](https://medium.com/@androidlab/modern-android-app-architecture-in-2025-mvvm-mvi-and-clean-architecture-with-jetpack-compose-c0df3c727334)
- [Medium: Hot Android Skills 2025](https://medium.com/@androidlab/hot-android-skills-in-2025-what-employers-projects-are-demanding-a6478cd0aa90)
- [JetBrains: KMP Roadmap 2025](https://blog.jetbrains.com/kotlin/2025/08/kmp-roadmap-aug-2025/)
- [droidcon: 15 Years of Android Architectures](https://www.droidcon.com/2025/10/20/15-years-of-android-app-architectures/)

---

*Обновлено: 2025-12-26*

---

*Проверено: 2026-01-09*
