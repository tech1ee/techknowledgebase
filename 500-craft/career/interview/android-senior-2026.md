---
title: "Android Senior Interview 2026: полный гайд"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
status: published
confidence: high
tags:
  - topic/career
  - type/guide
  - level/advanced
  - interview
related:
  - "[[android-questions]]"
  - "[[system-design-android]]"
  - "[[staff-plus-engineering]]"
  - "[[se-interview-foundation]]"
prerequisites:
  - "[[se-interview-foundation]]"
  - "[[system-design-android]]"
  - "[[android-questions]]"
reading_time: 24
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Android Senior Interview 2026: полный гайд

> **TL;DR:** Senior Android в 2026 — это не просто Kotlin + Compose. Это System Design, AI tools proficiency, KMP experience, и leadership skills. Entry-level hiring упал на 73%, конкуренция сместилась на Senior+. Этот гайд — всё что нужно для L5/E5 позиций в FAANG и top-tier компаниях.

---

## Ландшафт 2026

```
2025 → 2026 ИЗМЕНЕНИЯ:

SKILLS SHIFT:
┌─────────────────────────────────────────────────────────────────────────┐
│  WAS (2024-2025)                  NOW (2026)                            │
├─────────────────────────────────────────────────────────────────────────┤
│  Kotlin basics                →   Kotlin advanced + KMP                 │
│  Compose UI                   →   Compose internals + performance       │
│  XML still relevant           →   Compose-first mandatory               │
│  Basic coroutines             →   Structured concurrency mastery        │
│  MVVM pattern                 →   MVI + unidirectional data flow        │
│  Single platform              →   KMP / cross-platform exposure         │
│  Manual testing               →   AI-assisted development               │
│  Algorithms focus             →   System Design focus                   │
│  Individual contributor       →   Technical leadership expected         │
└─────────────────────────────────────────────────────────────────────────┘

HIRING REALITY:
• Entry-level: -73% hiring
• Senior/Staff: Stable/growing demand
• AI/ML Android: +74% YoY growth
• Remote: 23% (down from 67%)
• Average applications per role: 250+
```

### What Companies Want in 2026

```
MUST-HAVE:
├── Kotlin (advanced, coroutines, Flow)
├── Jetpack Compose (production experience)
├── Architecture (Clean, MVI/MVVM)
├── Testing (unit, integration, UI)
├── System Design (mobile-specific)
└── AI tools proficiency (Copilot, Cursor)

STRONG ADVANTAGE:
├── KMP (Kotlin Multiplatform)
├── Compose Multiplatform
├── Performance optimization
├── Large-scale app experience
└── Team leadership / mentoring

EMERGING REQUIREMENTS:
├── AI/ML integration in apps
├── On-device ML (TensorFlow Lite)
├── LLM integration experience
└── AI-assisted development workflow
```

---

## Interview Structure: Senior Android

### Typical Process (4-6 weeks)

```
WEEK 1-2:
├── Recruiter Screen (30 min)
│   └── Background, motivation, logistics
└── Technical Phone Screen (45-60 min)
    └── 1-2 coding problems, basic Android

WEEK 3-4:
└── Onsite / Virtual Loop (4-6 hours)
    ├── Coding #1: DSA (45-60 min)
    ├── Coding #2: Android-specific (45-60 min)
    ├── System Design: Mobile (45-60 min)
    ├── Behavioral: STAR (45-60 min)
    └── Optional: Domain Deep-Dive (45 min)

WEEK 4-5:
├── Debrief (internal)
└── Decision + Offer/Reject

WEEK 5-6:
└── Negotiation (if offer)
```

### Time Allocation by Round Type

| Round Type | Weight | What's Tested |
|------------|--------|---------------|
| DSA Coding | 25% | Problem-solving, code quality |
| Android Coding | 20% | Domain knowledge, patterns |
| System Design | 30% | Architecture, scale, trade-offs |
| Behavioral | 20% | Leadership, collaboration |
| Domain Deep-Dive | 5% | Depth of expertise |

---

## Pillar 1: Technical Knowledge

### Core Topics Checklist

```markdown
## KOTLIN MASTERY

### Fundamentals
- [ ] Null safety: nullable types, safe calls, Elvis operator
- [ ] Data classes: copy, destructuring, component functions
- [ ] Sealed classes: exhaustive when, state modeling
- [ ] Object declarations: singleton, companion objects
- [ ] Extension functions: use cases, best practices
- [ ] Scope functions: let, run, with, apply, also

### Advanced
- [ ] Inline functions: performance, reified types
- [ ] Delegation: by lazy, observable, custom delegates
- [ ] Generics: variance (in/out), type projections
- [ ] Contracts: callsInPlace, returns
- [ ] Context receivers (experimental)
- [ ] Value classes: inline, performance

### Coroutines & Flow
- [ ] Structured concurrency: scope, job hierarchy
- [ ] Dispatchers: Main, IO, Default, Unconfined
- [ ] Exception handling: supervisorScope, CEH
- [ ] Flow operators: map, filter, flatMapLatest
- [ ] StateFlow vs SharedFlow vs LiveData
- [ ] Channel: buffer, conflation, fan-out

---

## JETPACK COMPOSE

### Fundamentals
- [ ] Composable functions: rules, restrictions
- [ ] State: remember, mutableStateOf, hoisting
- [ ] Recomposition: when, why, scope
- [ ] Side effects: LaunchedEffect, DisposableEffect

### Performance
- [ ] Stability: @Stable, @Immutable
- [ ] Smart recomposition: skipping unchanged
- [ ] derivedStateOf: computed state optimization
- [ ] key(): identity for lazy lists
- [ ] remember with keys: dependency tracking

### Advanced
- [ ] Custom layouts: Layout composable
- [ ] Modifiers: custom, order matters
- [ ] Animation: animate*AsState, Transition
- [ ] Composition Local: dependency injection
- [ ] SubcomposeLayout: measure before compose

---

## ARCHITECTURE

### Patterns
- [ ] MVVM: ViewModel, LiveData/StateFlow
- [ ] MVI: unidirectional flow, Intent, State
- [ ] Clean Architecture: layers, dependencies
- [ ] Repository pattern: data abstraction
- [ ] Use cases: business logic encapsulation

### Components
- [ ] ViewModel: scope, SavedStateHandle
- [ ] Navigation: Compose, type-safe args
- [ ] Dependency Injection: Hilt, Koin
- [ ] Data layer: Room, Retrofit, DataStore

---

## ANDROID INTERNALS

### Lifecycle
- [ ] Activity lifecycle: all callbacks
- [ ] Fragment lifecycle: nested, ViewLifecycle
- [ ] ViewModel lifecycle: vs Activity/Fragment
- [ ] Process death: testing, handling
- [ ] Configuration changes: retention

### System
- [ ] Context: Application vs Activity
- [ ] Handler/Looper: message queue
- [ ] Binder: IPC mechanism
- [ ] Content Providers: when to use
- [ ] Broadcast Receivers: implicit, explicit
```

### Must-Know Code Patterns

#### Coroutines Exception Handling

```kotlin
// Правильный паттерн
class MyViewModel : ViewModel() {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)
    val state: StateFlow<UiState> = _state.asStateFlow()

    fun loadData() {
        viewModelScope.launch {
            _state.value = UiState.Loading
            try {
                val result = withContext(Dispatchers.IO) {
                    repository.getData()
                }
                _state.value = UiState.Success(result)
            } catch (e: Exception) {
                if (e is CancellationException) throw e
                _state.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

#### Compose State Management (MVI)

```kotlin
// State
data class ScreenState(
    val items: List<Item> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// Intent/Event
sealed interface ScreenIntent {
    data object LoadItems : ScreenIntent
    data class DeleteItem(val id: String) : ScreenIntent
}

// ViewModel
class ScreenViewModel : ViewModel() {
    private val _state = MutableStateFlow(ScreenState())
    val state: StateFlow<ScreenState> = _state.asStateFlow()

    fun onIntent(intent: ScreenIntent) {
        when (intent) {
            is ScreenIntent.LoadItems -> loadItems()
            is ScreenIntent.DeleteItem -> deleteItem(intent.id)
        }
    }

    private fun loadItems() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true, error = null) }
            repository.getItems()
                .onSuccess { items ->
                    _state.update { it.copy(items = items, isLoading = false) }
                }
                .onFailure { e ->
                    _state.update { it.copy(error = e.message, isLoading = false) }
                }
        }
    }
}
```

#### Compose Side Effects

```kotlin
@Composable
fun Screen(viewModel: ScreenViewModel) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    // One-time effect
    LaunchedEffect(Unit) {
        viewModel.onIntent(ScreenIntent.LoadItems)
    }

    // Effect with cleanup
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                viewModel.onIntent(ScreenIntent.Refresh)
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
        }
    }

    // Derived state for performance
    val showEmptyState by remember {
        derivedStateOf { state.items.isEmpty() && !state.isLoading }
    }
}
```

---

## Pillar 2: System Design (Mobile)

### Framework: RESHADED for Mobile

```
R - REQUIREMENTS
    Functional: what the app does
    Non-functional: offline, performance, battery

E - ESTIMATIONS
    Users, data size, request frequency
    Mobile-specific: storage limits, bandwidth

S - STORAGE SCHEMA
    Local DB (Room), cache, preferences
    Sync strategy with backend

H - HIGH-LEVEL DESIGN
    MVVM/MVI layers
    Data flow diagram
    Key components

A - API DESIGN
    REST/GraphQL contracts
    Pagination, caching headers
    Error handling

D - DETAILED DESIGN
    Deep-dive on 1-2 components
    Caching strategy
    Sync mechanism

E - EVALUATE
    Trade-offs discussion
    Alternatives considered

D - DISTINCTIVE
    Monitoring, analytics
    Accessibility, testing
```

### Common Mobile SD Problems

| Problem | Key Considerations | Time |
|---------|-------------------|------|
| **Design Twitter Feed** | Pagination, caching, real-time, offline | 45 min |
| **Design Offline Notes** | Sync conflict resolution, storage | 45 min |
| **Design Image Gallery** | Image caching, memory management | 45 min |
| **Design Chat App** | WebSocket, presence, delivery status | 45 min |
| **Design E-commerce** | Product cache, cart sync, checkout | 45 min |

### Mobile SD Example: Design Twitter Feed

```
REQUIREMENTS (5 min):

Functional:
• View home feed with tweets
• Pull-to-refresh
• Infinite scroll pagination
• Like/retweet/reply actions

Non-functional:
• Offline support (cached feed)
• Fast initial load (<2s)
• Smooth scrolling (60fps)
• Low battery impact

---

HIGH-LEVEL ARCHITECTURE:

┌─────────────────────────────────────────────────────────────────────────┐
│                              UI LAYER                                    │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐              │
│  │ FeedScreen   │    │ TweetCard    │    │ ComposeView  │              │
│  │ (Compose)    │    │ (Compose)    │    │ (Compose)    │              │
│  └──────┬───────┘    └──────────────┘    └──────────────┘              │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────┐                                                      │
│  │ FeedViewModel│ ← StateFlow<FeedState>                               │
│  └──────┬───────┘                                                      │
└─────────┼───────────────────────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────────────────────────┐
│         ▼          DOMAIN LAYER                                         │
│  ┌──────────────┐    ┌──────────────┐                                  │
│  │GetFeedUseCase│    │LikeTweetUC   │                                  │
│  └──────┬───────┘    └──────────────┘                                  │
└─────────┼───────────────────────────────────────────────────────────────┘
          │
┌─────────┼───────────────────────────────────────────────────────────────┐
│         ▼          DATA LAYER                                           │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │                    FeedRepository                              │      │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │      │
│  │  │ RemoteDS    │    │ LocalDS     │    │ CachePolicy │       │      │
│  │  │ (Retrofit)  │    │ (Room)      │    │             │       │      │
│  │  └─────────────┘    └─────────────┘    └─────────────┘       │      │
│  └──────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────┘

---

CACHING STRATEGY:

1. Network-first with fallback:
   • Always try network for fresh data
   • On failure, serve cached data
   • Update cache on success

2. Cache invalidation:
   • TTL: 5 min for feed
   • User action: invalidate on post/like
   • Pull-to-refresh: force network

3. Pagination cache:
   • Store cursor/offset
   • Append new pages to cache
   • Clear on refresh

---

DEEP DIVE: Offline & Sync

Optimistic updates:
1. User likes tweet
2. Update UI immediately
3. Queue action for sync
4. On network: send action
5. On failure: revert + show error

Conflict resolution:
• Server timestamp wins
• Client tracks pending actions
• Retry queue with exponential backoff
```

---

## Pillar 3: Behavioral for Senior

### Senior-Specific Dimensions

| Dimension | What They Look For | Example Question |
|-----------|-------------------|------------------|
| **Technical Leadership** | Influence architecture decisions | "Led migration to Compose" |
| **Mentoring** | Grow junior engineers | "Onboarded 3 new developers" |
| **Cross-team** | Work beyond your team | "Collaborated with iOS team on shared SDK" |
| **Ambiguity** | Navigate unclear requirements | "Defined scope when PM was unsure" |
| **Impact** | Measurable business results | "Reduced crash rate by 80%" |
| **Conflict** | Handle disagreements professionally | "Resolved architecture debate" |

### STAR Stories for Senior Android

#### Story 1: Technical Leadership

```
SITUATION:
Our 3-year-old Android app with 2M users was built entirely in XML.
Team of 6 developers, each feature taking 2x longer than iOS counterpart.

TASK:
As the most senior Android developer, I was tasked with evaluating
and potentially leading migration to Jetpack Compose.

ACTION:
1. Built proof-of-concept in 2 weeks comparing performance and DX
2. Created migration strategy: new features in Compose, gradual conversion
3. Developed internal Compose component library for consistency
4. Led training sessions for 5 team members
5. Established coding standards and review guidelines

RESULT:
• 40% reduction in UI development time
• 30% less UI-related bugs
• Team adopted Compose in 4 months
• Strategy became template for other teams
```

#### Story 2: Handling Failure

```
SITUATION:
Released new payment feature to 100% of users. Within hours,
crash rate spiked from 0.1% to 2%.

TASK:
I was on-call and needed to diagnose and fix the critical issue
that was impacting revenue.

ACTION:
1. Immediately analyzed crash logs: NPE in new payment flow
2. Identified root cause: race condition in state management
3. Shipped hotfix within 3 hours
4. Conducted post-mortem with team
5. Implemented testing improvements to prevent recurrence

RESULT:
• Resolved critical issue in 3 hours vs 8-hour SLA
• Created automated test that catches similar issues
• Established stricter release process
• Shared learnings in engineering all-hands
```

---

## Pillar 4: AI Integration

### What's Expected in 2026

```
MUST DEMONSTRATE:
• Use AI coding assistants (Copilot, Cursor)
• Validate AI-generated code
• Integrate AI in development workflow
• Understand AI limitations

INTERVIEW SCENARIOS:
1. AI-enabled coding round (Meta, others)
   → AI assistant available during problem solving
   → Evaluated on how you USE AI, not avoid it

2. AI in mobile discussion
   → Experience integrating LLMs in apps
   → On-device ML (TensorFlow Lite, Core ML)

3. AI tools workflow
   → How do you use AI in daily work?
   → What are the risks and mitigations?
```

### AI-Enabled Interview Strategy

```
DO:
• Use AI for boilerplate code
• Validate every AI suggestion
• Explain what you're doing to interviewer
• Catch AI mistakes (shows expertise)
• Ask AI clarifying questions, not solutions

DON'T:
• Prompt AI for complete solutions
• Copy AI output without review
• Let AI drive the conversation
• Show you don't understand AI-generated code
• Rely on AI for algorithm design
```

### AI in Android Development Questions

```
COMMON QUESTIONS:

Q: "How do you use AI tools in your development workflow?"
A: "I use Copilot for boilerplate like data classes and mappers.
   For complex logic, I write it myself then use AI to suggest
   edge cases I might have missed. I always review AI suggestions
   for security and performance implications."

Q: "How would you integrate an LLM into an Android app?"
A: Architecture considerations:
   • API layer for LLM calls (OpenAI, Anthropic API)
   • Caching responses for cost/latency
   • Streaming for better UX
   • Offline fallback strategy
   • Content moderation

Q: "Experience with on-device ML?"
A: TensorFlow Lite for:
   • Image classification
   • Object detection
   • Text classification
   Model optimization:
   • Quantization for size
   • GPU delegate for speed
   • Model versioning strategy
```

---

## Question Bank: Android Senior

### Lifecycle & Architecture (20+ questions)

```
1. Explain Activity lifecycle callbacks in order.
2. What's the difference between onStop and onDestroy?
3. How does ViewModel survive configuration changes?
4. What happens during process death? How to handle?
5. When is onSaveInstanceState called? vs onPause?
6. Explain Fragment lifecycle vs Activity lifecycle.
7. What is ViewLifecycleOwner in Fragment?
8. How does SavedStateHandle work?
9. Explain MVVM vs MVI trade-offs.
10. What are the layers in Clean Architecture?
11. When to use Repository pattern?
12. How to handle one-time events in MVVM?
13. What's the difference between SharedFlow and Channel for events?
14. How to scope ViewModel to navigation graph?
15. What is Hilt and how does it work?
16. Explain component hierarchy in Hilt.
17. How to test ViewModel with dependencies?
18. What's the difference between @Inject and @Provides?
19. How to handle multiple implementations in DI?
20. Explain Android's Context types and when to use each.
```

### Jetpack Compose (20+ questions)

```
1. What is recomposition and when does it happen?
2. How does remember work internally?
3. What's the difference between remember and rememberSaveable?
4. Explain state hoisting pattern.
5. What are side effects in Compose? Name the types.
6. When to use LaunchedEffect vs rememberCoroutineScope?
7. Explain derivedStateOf and when to use it.
8. What makes a type stable in Compose?
9. How does @Stable annotation work?
10. What is a recomposition scope?
11. How to avoid unnecessary recompositions?
12. Explain Modifier order importance.
13. How to create a custom Modifier?
14. What is CompositionLocal? When to use?
15. How does collectAsStateWithLifecycle work?
16. Explain Compose phases: Composition, Layout, Drawing.
17. What is SubcomposeLayout?
18. How to implement custom layouts?
19. What's the difference between Box, Column, Row internally?
20. How does lazy list handle item recycling?
```

### Coroutines & Flow (15+ questions)

```
1. What's the difference between launch and async?
2. Explain structured concurrency.
3. What is CoroutineScope and how to create one?
4. Difference between viewModelScope and lifecycleScope?
5. How to cancel a coroutine properly?
6. Explain exception handling in coroutines.
7. What's the difference between supervisorScope and coroutineScope?
8. What are Dispatchers and when to use each?
9. What is a Flow? Cold vs Hot?
10. Difference between StateFlow and SharedFlow?
11. When to use Channel vs SharedFlow?
12. Explain flatMapLatest vs flatMapMerge.
13. How to combine multiple flows?
14. What is conflation in Flow?
15. How to test coroutines and flows?
```

### Performance & Optimization (10+ questions)

```
1. How to detect memory leaks?
2. What causes ANR? How to avoid?
3. How to optimize app startup time?
4. What are Baseline Profiles?
5. How to profile Compose performance?
6. What causes jank? How to debug?
7. Explain R8 and ProGuard optimization.
8. How to reduce APK size?
9. Battery optimization strategies?
10. How to implement efficient image loading?
```

---

## Salary Benchmarks 2026

### By Company (Senior / L5 / E5)

| Company | Base | RSU/year | Bonus | Total Comp |
|---------|------|----------|-------|------------|
| Google L5 | $180-220K | $80-150K | 15% | $300-400K |
| Meta E5 | $200-240K | $100-200K | 15% | $350-500K |
| Amazon L5 | $170-200K | $60-120K | ~10% | $250-350K |
| Apple ICT4 | $180-220K | $80-130K | ~10% | $280-380K |
| Netflix | $350-500K | included | - | $350-500K |

### By Region (Remote)

| Region | Senior Android (Net) |
|--------|---------------------|
| US Remote | $130-180K |
| UK Remote | £65-90K |
| EU Remote | €60-85K |
| UAE (tax-free) | $60-100K |

### Staff Level (for reference)

| Company | Level | Total Comp |
|---------|-------|------------|
| Google L6 | Staff | $400-600K |
| Meta E6 | Staff | $450-700K |
| Amazon L6 | Principal | $350-500K |

---

## Preparation Timeline

### 12-Week Plan

```
WEEKS 1-3: DSA FOUNDATION
├── Patterns: Two Pointers, Sliding Window, BFS/DFS
├── 50-70 LeetCode problems (Medium focus)
├── Daily: 1-2 problems, 1 hour
└── Goal: Solve Medium in 25-30 min

WEEKS 4-6: ANDROID DEEP-DIVE
├── Compose internals, performance
├── Coroutines advanced patterns
├── Architecture patterns practice
└── Goal: Answer any Android question confidently

WEEKS 7-9: SYSTEM DESIGN
├── Mobile SD fundamentals
├── 5-7 common problems practiced
├── RESHADED framework mastery
└── Goal: 45-min SD feels comfortable

WEEKS 10-11: BEHAVIORAL + MOCKS
├── 7 STAR stories prepared
├── 4-6 mock interviews
├── Company-specific research
└── Goal: Confident in all round types

WEEK 12: POLISH
├── Light review (no cramming)
├── Rest and mental prep
├── Logistics confirmed
└── Goal: Peak performance for interviews
```

---

## Resources

### Technical

| Resource | Type | Focus |
|----------|------|-------|
| [Android Developers](https://developer.android.com) | Docs | Official guides |
| [Philipp Lackner](https://youtube.com/@PhilippLackner) | Video | Compose, Kotlin |
| [ProAndroidDev](https://proandroiddev.com) | Blog | Advanced topics |
| [Android Weekly](https://androidweekly.net) | Newsletter | Stay current |

### Interview Prep

| Resource | Type | Focus |
|----------|------|-------|
| [Mobile System Design](https://github.com/weeeBox/mobile-system-design) | GitHub | SD framework |
| [NeetCode](https://neetcode.io) | Course | DSA patterns |
| [HelloInterview](https://hellointerview.com) | Mock | Practice |

### AI-Enabled

| Resource | Type | Focus |
|----------|------|-------|
| [Cursor](https://cursor.sh) | IDE | AI coding |
| [Final Round AI](https://finalroundai.com) | Mock | AI interviews |

---

## Куда дальше

**Foundation:**
→ [[se-interview-foundation]] — Universal SE prep
→ [[android-questions]] — Full question bank

**System Design:**
→ [[system-design-android]] — Mobile SD deep-dive

**Next Level:**
→ [[staff-plus-engineering]] — Staff+ path

**AI Prep:**
→ [[ai-interview-preparation]] — AI-assisted prep

---

## Связь с другими темами

- [[android-questions]] — Полный банк вопросов по Android: Lifecycle, Compose, Coroutines, Architecture, Performance. Текущий материал даёт обзор 60+ вопросов по категориям, а android-questions содержит детальные ответы с примерами кода и follow-up вопросами. Используй как reference для domain deep-dive раунда.

- [[system-design-android]] — Детальный гайд по Mobile System Design с framework, примерами и mobile-specific considerations. System Design составляет 30% веса на Senior интервью и является deciding factor для L5/E5. Текущий материал даёт RESHADED framework обзорно, а system-design-android разбирает каждый шаг с реальными задачами.

- [[staff-plus-engineering]] — Следующий уровень после Senior. Понимание Staff expectations помогает на Senior интервью: показывая leadership potential и cross-team thinking, ты демонстрируешь growth trajectory. Hiring managers ищут кандидатов, которые не просто "хороший Senior", а потенциальный Staff.

- [[se-interview-foundation]] — Универсальная база для всех SE интервью: DSA паттерны, System Design компоненты, STAR method, AI-enabled формат. Текущий материал специализирован для Android, а foundation даёт кросс-платформенный фундамент, который нужен для coding rounds и general system design.

## Источники и дальнейшее чтение

- McDowell G. L. (2015). *Cracking the Coding Interview*. — Покрывает DSA-подготовку, которая составляет 25% веса на Senior Android интервью. 189 задач с разбором, паттерны решения, стратегии для каждого типа coding round.

- Xu A. (2020). *System Design Interview*. — System Design = 30% веса. Книга даёт backend-ориентированный framework, который нужно адаптировать для mobile: добавить offline-first, caching, sync и battery considerations из текущего материала.

- Larson W. (2022). *Staff Engineer: Leadership Beyond the Management Track*. — Для behavioral раунда (20% веса) важно показать leadership potential. Книга объясняет разницу между Senior execution и Staff influence, что помогает правильно позиционировать STAR-истории на интервью.

## Источники

- [Built In: Android Developer Salary 2026](https://builtin.com/salaries/us/remote/android-developer)
- [Levels.fyi: Compensation Data](https://levels.fyi)
- [Final Round AI: Job Market 2026](https://www.finalroundai.com/blog/software-engineering-job-market-2026)
- [Index.dev: Android Interview Questions 2026](https://www.index.dev/interview-questions/android)

---

## Проверь себя

> [!question]- Почему Senior Android в 2026 -- это не только Kotlin + Compose, и какие навыки стали обязательными?
> Senior 2026 оценивается по четырём измерениям: 1) Technical depth (Kotlin, Compose, Coroutines). 2) System Design (mobile architecture для миллионов пользователей). 3) AI tools proficiency (Copilot, Cursor как рабочие инструменты). 4) Leadership (cross-team influence, mentoring). KMP experience стал strong advantage. Entry-level hiring упал на 73%, конкуренция сместилась на Senior+.

> [!question]- Ты готовишься к Google L5 интервью. Какой план на 8 недель и как распределить время между DSA, System Design и Behavioral?
> Weeks 1-3: DSA (50% времени Senior) -- NeetCode 150, pattern-based подход. Weeks 4-6: System Design (35%) -- mobile-specific задачи, RESHADED framework. Weeks 5-7: Behavioral (25%, параллельно) -- 7 STAR историй, Googleyness. Week 8: polish + mock interviews. Google делает упор на coding больше других, но слабый SD = no offer для Senior.

> [!question]- Как отличается подготовка к Meta E5 от Google L5 для Android-разработчика?
> Meta: AI-enabled coding (AI-assistant доступен), отдельный Android-specific раунд, фокус на "Move Fast" culture, 45 мин behavioral. Google: классический coding без AI, Role-Related Knowledge (Android deep dive), Googleyness assessment, больший вес coding vs design. Meta ценит скорость и impact, Google -- intellectual humility и collaboration.

---

## Ключевые карточки

Android Senior 2026 -- must-have навыки?
?
Kotlin (advanced), Jetpack Compose (state, recomposition, performance), Coroutines/Flow (structured concurrency), System Design (mobile-specific), AI tools proficiency (Copilot, Cursor). Strong advantage: KMP, product thinking, leadership.

Типичная структура Senior Android интервью (FAANG)?
?
1) Recruiter Screen (30 мин). 2) Technical Phone (45-60 мин, LeetCode Medium). 3) Onsite 4-5 раундов: Coding #1 (Algorithm), Coding #2 (Android-specific), System Design (mobile architecture), Behavioral (STAR), Optional (App Design / Product sense).

Senior Android -- время поиска работы 2026?
?
Senior (5+ лет): 2-3 месяца. 50%+ открытых вакансий -- senior и выше. Зарплаты держатся или растут (3-5% YoY). Но ожидания выросли: system design skills, cross-platform experience, AI tools proficiency, product thinking.

Google L5 vs Meta E5 -- ключевые различия интервью?
?
Google L5: 2 coding (LeetCode Medium-Hard) + System Design + RRK (Android deep dive) + Behavioral. Meta E5: AI-enabled coding + System Design + Product Architecture + Behavioral (45 мин). Meta разрешает AI на coding; Google -- нет.

---

## Куда дальше

| Направление | Тема | Ссылка |
|------------|------|--------|
| Следующий шаг | Android-specific вопросы для интервью | [[android-questions]] |
| Углубиться | Mobile System Design для Senior/Staff | [[system-design-android]] |
| Смежная тема | Путь выше Senior: Staff+ Engineering | [[staff-plus-engineering]] |
| Обзор | Фундамент подготовки к интервью | [[se-interview-foundation]] |

---

*Обновлено: 2026-02-13*

---

*Проверено: 2026-02-13*
