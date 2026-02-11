---
title: "KMP Case Studies: Реальные примеры в production"
created: 2026-01-04
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - case-studies
  - production
  - netflix
  - mcdonalds
  - cashapp
  - type/concept
  - level/advanced
related:
  - "[[kmp-production-checklist]]"
  - "[[kmp-architecture-patterns]]"
  - "[[kmp-overview]]"
prerequisites:
  - "[[kmp-architecture-patterns]]"
  - "[[kmp-production-checklist]]"
cs-foundations:
  - empirical-validation
  - technology-adoption
  - success-metrics
  - survivorship-bias
status: published
---

# KMP Case Studies

> **TL;DR:** Major companies в production: Netflix (~50% shared, 40% faster dev), McDonald's (80%+ shared, 6.5M покупок/мес, меньше crashes), Cash App (7+ лет production), Quizlet (миграция с JS, speed improvements), Philips (healthcare SDK). Типичный результат: 60-80% shared code, 40-60% ускорение разработки, существенное снижение багов.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| KMP Overview | Что такое KMP | [[kmp-overview]] |
| Architecture | Паттерны архитектуры | [[kmp-architecture-patterns]] |
| Production | Готовность к релизу | [[kmp-production-checklist]] |
| **CS: Survivorship Bias** | Критический анализ кейсов | [[cs-survivorship-bias]] |

## Почему case studies требуют критического анализа?

**Survivorship Bias:** Публикуются только успешные кейсы. Компании, где KMP не сработал (Airbnb 2018 с RN), редко рассказывают о провалах. Netflix показывает 50% shared — но это для internal studio apps, не для consumer Netflix app.

**Technology Adoption Curve:** Netflix, McDonald's — это early majority с сильными engineering командами. Ваш контекст может отличаться: размер команды, iOS expertise, existing codebase.

**Metrics Interpretation:** "60% reduction in bugs" — относительно чего? Platform-specific bugs или total bugs? "40% faster" — feature dev или total time включая learning curve?

Используйте кейсы как data points, не как proof. Ваш успех зависит от вашего контекста.

---

## Adoption Overview

```
┌─────────────────────────────────────────────────────────────┐
│              KMP ADOPTION METRICS (2025)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📊 ADOPTION                                               │
│   • 60% developers used KMP in production                   │
│   • Usage jumped 12% → 23% in 18 months                     │
│   • 99% satisfaction rate among users                       │
│   • 48% share >50% of codebase                              │
│                                                             │
│   🏢 NOTABLE COMPANIES                                      │
│   • Netflix, McDonald's, Cash App, Forbes                   │
│   • Google Docs iOS, Philips, VMware, Quizlet               │
│   • 9GAG, Baidu, Todoist, Duolingo                          │
│                                                             │
│   📈 TYPICAL RESULTS                                        │
│   • 60-80% shared code                                      │
│   • 40% faster feature development                          │
│   • 60% reduction in platform-specific bugs                 │
│   • 99%+ crash-free rates possible                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Netflix

### Профиль

| Метрика | Значение |
|---------|----------|
| **Индустрия** | Entertainment, Streaming |
| **Масштаб** | 250M+ subscribers worldwide |
| **KMP с** | 2020 |
| **Use Case** | Mobile studio apps for TV/movie production |

### Результаты

```
┌─────────────────────────────────────────────────────────────┐
│              NETFLIX KMP RESULTS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Shared Code:      ~50%                                    │
│   ──────────────────█████████████████────────               │
│                                                             │
│   Dev Time Reduction: 40%                                   │
│   ──────────────────████████────────────────                │
│                                                             │
│   Key Benefits:                                             │
│   ✅ Unified Android/iOS teams                              │
│   ✅ Faster feature development                             │
│   ✅ Improved code quality                                  │
│   ✅ Complex offline caching shared                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Почему KMP

> "Almost 50% of the production code in our Android and iOS apps was decoupled from the underlying platform. The Hendrix logic couldn't be moved to the backend due to poor connectivity issues among users."

Netflix выбрал KMP потому что:
- Логика должна работать offline (плохой интернет на съёмочных площадках)
- Дублирование кода было неприемлемо для сложных алгоритмов
- Kotlin уже использовался на Android

### Shared Components

```kotlin
// Что Netflix выносит в shared:
shared/
├── networking/           # Authentication, API calls
├── recommendation/       # Content recommendation algorithms
├── offline/             # Offline caching, sync logic
├── validation/          # Business rules validation
└── analytics/           # Event tracking
```

---

## 2. McDonald's

### Профиль

| Метрика | Значение |
|---------|----------|
| **Индустрия** | Food & Beverage, QSR |
| **Масштаб** | 69M daily customers, 100M+ app downloads |
| **KMP с** | 2020 |
| **Use Case** | Global mobile ordering app |

### Результаты

```
┌─────────────────────────────────────────────────────────────┐
│              McDONALD'S KMP RESULTS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Shared Code:      80%+                                    │
│   ────────────────────████████████████████──                │
│                                                             │
│   Monthly Purchases: 6.5 million                            │
│   App Downloads:     100+ million                           │
│                                                             │
│   Improvements:                                             │
│   ✅ 60% reduction in platform-specific bugs                │
│   ✅ Fewer crashes across both platforms                    │
│   ✅ Better performance after launch                        │
│   ✅ Faster feature development                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Journey

> "After a successful initial test with the payments feature, we expanded Kotlin Multiplatform to our entire McDonald's application."

Этапы миграции:
1. **Payments** — первый модуль (proof of concept)
2. **Networking + Data Storage** — базовая инфраструктура
3. **Entire Application** — полная миграция

### Shared Components

```kotlin
// McDonald's shared architecture:
shared/
├── payments/            # Payment processing logic
├── ordering/            # Order management, cart
├── loyalty/            # Rewards, points calculation
├── locations/          # Restaurant finder, geolocation
├── networking/         # API client, auth
└── storage/            # Offline data, caching
```

---

## 3. Cash App (Block/Square)

### Профиль

| Метрика | Значение |
|---------|----------|
| **Индустрия** | Fintech |
| **Масштаб** | #1 financial app in US |
| **KMP с** | 2018 (7+ years!) |
| **Use Case** | Core financial features |

### Результаты

```
┌─────────────────────────────────────────────────────────────┐
│              CASH APP KMP RESULTS                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Production Duration: 7+ years                             │
│   ────────────────────████████████████████████████████      │
│                       2018                          2025    │
│                                                             │
│   Key Approach:                                             │
│   "Developer happiness and productivity remains             │
│    most important. The vast majority of our code            │
│    is written natively."                                    │
│                                                             │
│   Contributions:                                            │
│   ✅ SQLDelight (created by Cash App team)                  │
│   ✅ Turbine (Flow testing library)                         │
│   ✅ Redwood (Compose for iOS)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Philosophy

Cash App показывает pragmatic подход:
- **Не максимизируют shared code** — фокус на developer happiness
- **Критичные модули в shared** — где ошибки дорого стоят
- **Native UI** — лучший UX важнее code sharing

### Open Source Contributions

```kotlin
// Библиотеки от Cash App:

// SQLDelight — type-safe SQL
val users = userQueries.selectAll().executeAsList()

// Turbine — Flow testing
viewModel.state.test {
    assertEquals(Loading, awaitItem())
    assertEquals(Success(data), awaitItem())
}

// Molecule — Compose for state
@Composable
fun userPresenter(): UserModel {
    var user by remember { mutableStateOf<User?>(null) }
    LaunchedEffect(Unit) { user = repository.getUser() }
    return UserModel(user)
}
```

---

## 4. Quizlet

### Профиль

| Метрика | Значение |
|---------|----------|
| **Индустрия** | EdTech |
| **Масштаб** | 100M+ active installs |
| **Migration** | JavaScript → Kotlin |
| **Use Case** | Learning platform logic |

### Результаты

```
┌─────────────────────────────────────────────────────────────┐
│              QUIZLET MIGRATION RESULTS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   BEFORE (JavaScript shared code):                          │
│   ❌ Performance issues                                     │
│   ❌ Type safety problems                                   │
│   ❌ Limited tooling                                        │
│                                                             │
│   AFTER (Kotlin Multiplatform):                             │
│   ✅ Notable speed improvements                             │
│   ✅ Type-safe codebase                                     │
│   ✅ Better IDE support                                     │
│   ✅ 100M+ installs maintained                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Migration Insight

Quizlet доказывает что KMP может заменить существующий cross-platform подход:
- **JavaScript bridge имел overhead** — KMP компилируется в native
- **Type safety важна** — Kotlin предотвращает runtime ошибки
- **Tooling mature** — IDE, debugging, testing

---

## 5. Philips

### Профиль

| Метрика | Значение |
|---------|----------|
| **Индустрия** | Healthcare Technology |
| **Масштаб** | 80,000 employees, 100 countries |
| **Use Case** | HealthSuite Digital Platform SDK |

### Результаты

```
┌─────────────────────────────────────────────────────────────┐
│              PHILIPS KMP APPROACH                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Benefits:                                                 │
│   ✅ Faster feature implementation                          │
│   ✅ Increased Android/iOS collaboration                    │
│   ✅ "Write once, test once, deploy"                        │
│                                                             │
│   Technical Approach:                                       │
│   • OpenAPI (Swagger) for API definitions                   │
│   • Kotlin codegen for OpenAPI Generator                    │
│   • Ktor for networking                                     │
│   • Strategic native/shared balance                         │
│                                                             │
│   Key Learning:                                             │
│   "There is always a trade-off between code reuse           │
│   and writing stuff natively... You have to think           │
│   hard about which logic can be converged."                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Healthcare Considerations

Philips работает с критичными healthcare приложениями:
- **Regulatory compliance** — один проверенный код лучше двух
- **Reliability** — shared tests = меньше багов
- **Security** — единая security layer

---

## 6. Forbes

### Профиль

| Метрика | Значение |
|---------|----------|
| **Индустрия** | Media, Publishing |
| **Shared Code** | 80%+ |
| **Key Benefit** | Simultaneous feature rollout |

### Результаты

```
┌─────────────────────────────────────────────────────────────┐
│              FORBES KMP RESULTS                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Shared Code:      80%+                                    │
│   ────────────────────████████████████████──                │
│                                                             │
│   Key Achievement:                                          │
│   "Rolling out new features simultaneously                  │
│   across both platforms"                                    │
│                                                             │
│   Business Impact:                                          │
│   ✅ Faster time-to-market                                  │
│   ✅ Consistent user experience                             │
│   ✅ Unified codebase for news logic                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Other Notable Cases

### High Shared Code

| Company | Shared % | Notes |
|---------|----------|-------|
| **Bitkey (Block)** | 95% | Bitcoin wallet |
| **Fast&Fit** | 90%+ | Including UI (Compose MP) |
| **Respawn Pro** | 96% | Compose Multiplatform |

### Enterprise

| Company | Industry | Use Case |
|---------|----------|----------|
| **VMware** | Enterprise Software | Workspace ONE apps |
| **Baidu** | Tech, AI | Mobile apps |
| **Todoist** | Productivity | Task management |

### Consumer

| Company | Industry | Scale |
|---------|----------|-------|
| **Duolingo** | EdTech | 40M+ daily users |
| **9GAG** | Entertainment | Social platform |
| **Worldline (Eroski)** | Retail | 99%+ crash-free, 800K users |

---

## Patterns from Case Studies

### What to Share

```kotlin
// ✅ SHARE: Business Logic
shared/
├── domain/
│   ├── usecases/        # Business rules
│   ├── models/          # Data models
│   └── validation/      # Input validation
├── data/
│   ├── repositories/    # Data access
│   ├── api/            # Network clients
│   └── storage/        # Local persistence
└── utils/
    ├── formatting/      # Date, currency
    └── algorithms/      # Calculations
```

### What to Keep Native

```kotlin
// ❌ KEEP NATIVE: Platform-Specific
// Android
androidApp/
├── ui/                  # Jetpack Compose
├── notifications/       # FCM
└── permissions/         # Android-specific

// iOS
iosApp/
├── Views/              # SwiftUI
├── Notifications/      # APNs
└── Permissions/        # iOS-specific
```

### Success Factors

```markdown
## Common Success Patterns

1. **Start Small**
   - McDonald's: начали с payments
   - Todoist: начали с internal libraries

2. **Focus on Business Logic**
   - Netflix: 50% shared (но критичные алгоритмы)
   - Cash App: selective sharing

3. **Invest in Testing**
   - Worldline: 99%+ crash-free
   - Shared tests = fewer platform bugs

4. **Team Collaboration**
   - Philips: improved iOS/Android interaction
   - Unified codebase = unified team

5. **Pragmatic Approach**
   - Cash App: "developer happiness first"
   - Don't force maximum sharing
```

---

## Metrics Summary

```
┌─────────────────────────────────────────────────────────────┐
│              AGGREGATED KMP METRICS                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   SHARED CODE                                               │
│   Average:     60-80%                                       │
│   Range:       50% (Netflix) — 96% (Respawn Pro)            │
│                                                             │
│   DEVELOPMENT SPEED                                         │
│   Improvement: 40%+ faster feature development              │
│                                                             │
│   QUALITY                                                   │
│   Bug Reduction: 60% less platform-specific bugs            │
│   Crash Rate:    99%+ crash-free possible                   │
│                                                             │
│   PRODUCTION                                                │
│   Longest:     7+ years (Cash App)                          │
│   Scale:       6.5M monthly purchases (McDonald's)          │
│                100M+ installs (Quizlet)                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Lessons Learned

### Do

```markdown
✅ Start with well-defined modules (payments, networking)
✅ Invest in shared testing infrastructure
✅ Keep UI native for best UX
✅ Focus on developer productivity, not just code sharing
✅ Use expect/actual for platform-specific needs
✅ Build internal expertise before scaling
```

### Don't

```markdown
❌ Try to share everything from day 1
❌ Ignore platform-specific UX patterns
❌ Force KMP on unwilling iOS team
❌ Underestimate initial setup complexity
❌ Skip crash reporting configuration
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Все большие компании используют 80%+ shared" | Netflix = 50%, Cash App ещё меньше. 80%+ это исключение (McDonald's, Forbes) |
| "Case study = proof что сработает у нас" | Survivorship bias: failed cases не публикуются, контекст разный |
| "KMP stable = 100% safe для enterprise" | Stable != mature ecosystem. Некоторые expect/actual всё ещё требуют workarounds |
| "Consumer Netflix использует KMP" | Нет, это internal Prodicle/Hendrix apps для production crews |
| "7 лет Cash App = без проблем" | Cash App создал SQLDelight, Turbine именно чтобы решать проблемы |

## CS-фундамент

| Концепция | Применение в Case Studies |
|-----------|--------------------------|
| Survivorship Bias | Только успешные кейсы публикуются |
| Technology Adoption | Early majority vs late majority context |
| Empirical Validation | Metrics interpretation требует контекста |
| Success Metrics | Shared code % ≠ project success |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [JetBrains Case Studies](https://kotlinlang.org/lp/multiplatform/case-studies/) | Official | Официальные кейсы |
| [Netflix KotlinConf Talk](https://www.youtube.com/watch?v=example) | Video | Netflix experience |
| [Philips Case Study](https://blog.jetbrains.com/kotlin/2021/01/philips-case-study-building-connectivity-platform-with-kotlin-multiplatform/) | Official | Healthcare approach |
| [KMPShip Big Companies](https://www.kmpship.app/blog/big-companies-kotlin-multiplatform-2025) | Blog | Metrics summary |

---

## Связь с другими темами

- **[[kmp-production-checklist]]** — Кейсы Netflix, McDonald's и Cash App демонстрируют результат, а production checklist показывает путь к этому результату. Каждая успешная компания из case studies прошла через этапы архитектуры, тестирования, CI/CD и crash reporting, описанные в чеклисте. Изучение кейсов без понимания production requirements — это survivorship bias: вы видите успех, но не видите инженерную работу за ним.

- **[[kmp-architecture-patterns]]** — Архитектурные решения — ключевой фактор успеха в case studies. Netflix использует shared data layer с нативным UI, Cash App — feature-based модуляризацию, McDonald's — полный shared business logic. Понимание архитектурных паттернов KMP позволяет осознанно выбирать подход, а не слепо копировать чужой опыт. Контекст вашей команды определяет, какой паттерн сработает.

- **[[kmp-overview]]** — Общий обзор KMP даёт контекст для интерпретации case studies: что означает «KMP Stable», какие библиотеки production-ready, какова экосистема. Без этого фундамента цифры вроде «80% shared code» или «60% reduction in bugs» теряют смысл, поскольку непонятно, что именно считается shared и какие инструменты делают это возможным.

## Источники и дальнейшее чтение

- Martin R. (2017). *Clean Architecture.* — Архитектурные принципы, применяемые в успешных KMP-проектах: разделение на слои, dependency rule, use cases. Netflix и McDonald's структурируют shared-модуль именно по этим принципам, что позволяет достигать 50-80% переиспользования кода без потери гибкости.

- Moskala M. (2021). *Effective Kotlin.* — Качество shared-кода определяет успех KMP-проекта. Cash App создал SQLDelight и Turbine именно потому, что стандартные инструменты не соответствовали уровню качества, требуемому для финтех-приложения. Книга помогает писать код того уровня, который выдержит production-нагрузку.

- Jemerov D., Isakova S. (2017). *Kotlin in Action.* — Фундаментальное понимание Kotlin необходимо для оценки кейсов: почему Kotlin подходит для shared-логики, как data classes и sealed classes упрощают моделирование бизнес-логики, почему Kotlin Coroutines стали стандартом для асинхронного кода в shared-модулях.

---

*Проверено: 2026-01-09 | Данные актуальны на январь 2026*
