---
title: "In-Demand Android Skills 2025: что учить, что забыть"
created: 2025-12-26
modified: 2026-02-13
type: deep-dive
status: published
confidence: high
tags:
  - topic/career
  - type/reference
  - level/intermediate
related:
  - "[[android-job-market-2025]]"
  - "[[salary-benchmarks]]"
  - "[[interview-process]]"
prerequisites:
  - "[[android-job-market-2025]]"
reading_time: 15
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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

## Связь с другими темами

- **[[android-job-market-2025]]** — Востребованные навыки напрямую определяются состоянием рынка: какие компании нанимают, какие технологии внедряют, куда движется индустрия. Рыночный анализ объясняет ПОЧЕМУ определённые навыки ценятся, а этот гайд показывает КАКИЕ именно. Вместе они формируют полную картину для принятия решений о развитии.

- **[[salary-benchmarks]]** — Каждый навык имеет прямое влияние на зарплату: KMP даёт +15-25%, System Design обязателен для Staff+. Salary benchmarks переводят навыки в конкретные финансовые показатели и помогают приоритизировать обучение по ROI. Инвестируя время в правильные навыки, ты максимизируешь доход.

- **[[interview-process]]** — Навыки из этого гайда — это именно то, что спрашивают на интервью. Понимание формата интервью помогает расставить приоритеты: System Design важен для Senior+, а Compose internals спрашивают в каждом техническом раунде. Interview process определяет глубину, до которой нужно знать каждый навык.

---

## Источники и дальнейшее чтение

- **McDowell G.L. (2015). Cracking the Coding Interview.** — Хотя фокус на алгоритмах, главы о подготовке к техническим интервью показывают, какие навыки ценятся в FAANG и как их демонстрировать. Помогает перевести список навыков в конкретные действия для подготовки.

- **Xu A. (2020). System Design Interview.** — System Design — один из ключевых Strong Advantage навыков для Senior+. Эта книга даёт фреймворк для mobile-specific design questions, которые всё чаще появляются на интервью.

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

---

## Проверь себя

> [!question]- Почему KMP считается главным differentiator 2025 и как он влияет на зарплату?
> KMP позволяет Android-разработчику деливерить на iOS без полного знания Swift — таких специалистов мало. Google Docs, Netflix, McDonald's уже в production на KMP. Impact на зарплату: +15-25% к базе. Компании экономят на двух отдельных командах, поэтому готовы платить больше одному KMP-инженеру.

> [!question]- Mid-разработчик (3 года) хочет вырасти до Senior за год. Составь приоритетный план обучения, основываясь на рыночных данных.
> Приоритет 1: Jetpack Compose (basics, advanced layouts, animations, state hoisting) — без Compose нет новых проектов. Приоритет 2: Architecture deep dive (Clean Architecture, переход MVVM к MVI, тестирование). Приоритет 3: System Design basics (mobile-specific patterns, offline-first, caching). AI tools (Copilot/Cursor) — параллельно. KMP — после закрепления Compose.

> [!question]- Чем отличается знание Kotlin на уровне Junior, Mid и Senior на интервью?
> Junior: синтаксис (data class, null safety). Mid: правильное использование scope functions, sealed classes, extension functions. Senior: inline functions с reified generics, coroutine internals (Continuation, Dispatcher), DSL-построение, контракты (@OptIn ExperimentalContracts). Разница — от "использую" к "понимаю как работает внутри".

> [!question]- Какие навыки уже устарели и должны быть убраны из резюме Android-разработчика?
> Java как primary language, RxJava без знания Coroutines, AsyncTask/Loaders, XML layouts без Compose, MVP без MVVM/MVI. Grey zone: Data Binding (legacy), Navigation Component XML (Compose Navigation растёт), Dagger 2 (Hilt проще). Наличие только устаревших навыков ограничивает legacy-проектами.

> [!question]- Как AI меняет ежедневный workflow разработчика и почему это становится baseline?
> Без AI: придумай решение, напиши код, найди ошибки, исправь. С AI: опиши задачу, получи варианты, выбери лучший, review и рефакторинг. Экономия 30-50% на boilerplate. 65% разработчиков уже используют AI еженедельно — это не преимущество, а baseline. Кто без AI — медленнее рынка.

---

## Ключевые карточки

Три уровня навыков Android 2025 — Must-Have?
?
Kotlin (70%+ вакансий), Jetpack Compose (новый стандарт UI), Coroutines/Flow (async-first), MVVM/Clean Architecture (baseline для Senior).

Strong Advantage навыки Android 2025?
?
KMP (+15-25% к зарплате), MVI Architecture (Senior+ роли), System Design (обязательно для Staff+), AI Tools Proficiency (становится baseline).

Чем MVI лучше MVVM для сложных приложений?
?
MVI: predictable (каждый state change через intent), testable (воспроизводимые state transitions), debuggable (логирование intents/states), scalable (complex flows). MVVM стало baseline, MVI — для complex apps.

Что ожидают от Senior в Jetpack Compose?
?
Понимание recomposition и оптимизация, state hoisting, custom layouts и modifiers, Animation APIs, side effects (LaunchedEffect, SideEffect, DisposableEffect).

KMP Architecture — типичная структура?
?
Shared Module (business logic, data models, repositories, Ktor networking, SQLDelight storage) + platform-specific UI (Compose на Android, SwiftUI на iOS). expect/actual для platform-specific кода.

Какие темы System Design спрашивают на Mobile интервью?
?
Design offline-first app с sync, image loading library, chat/messaging feature, feed with pagination. Оценивают: breakdown problem, trade-off discussions, mobile-specific considerations, scalability.

Salary impact навыка KMP?
?
+15-25% к зарплате. Редкий и востребованный навык. Для сравнения: Compose expert +5-10% (становится baseline), System Design +10-20% (обязательно для Staff+).

Эволюция Android архитектуры 2015-2025?
?
Java+XML+AsyncTask+MVP (2015) -> Kotlin+MVVM (2018) -> Coroutines+Flow (2019) -> Compose+UDF+MVI (2020-2024) -> MVI+KMP+AI (2025). Каждый виток добавляет abstraction layer.

---

## Куда дальше

| Направление | Ссылка | Зачем |
|-------------|--------|-------|
| Следующий шаг | [[system-design-android]] | Подготовка к design rounds — ключевой Strong Advantage |
| Углубиться | [[android-compose]] | Deep dive в Compose — must-have навык |
| Смежная тема | [[kotlin-coroutines]] | Coroutine internals для Senior-уровня |
| Обзор | [[android-job-market-2025]] | Рыночный контекст для приоритизации навыков |

---

*Обновлено: 2026-02-13*

---

*Проверено: 2026-02-13*
