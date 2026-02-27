---
title: "KMP Case Studies: Реальные примеры в production"
created: 2026-01-04
modified: 2026-02-13
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
reading_time: 30
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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


## Теоретические основы

### Формальное определение

> **Case study (исследование случая)** — эмпирический метод исследования, изучающий современное явление в его реальном контексте, особенно когда границы между явлением и контекстом размыты (Yin, 2014, Case Study Research).

### Методология анализа case studies

Robert Yin (2014) выделяет три типа case study, все применимые к анализу KMP adoption:

| Тип | Цель | Пример в контексте KMP |
|-----|------|----------------------|
| **Exploratory** | Исследовать новое явление | «Возможен ли 80% shared code?» |
| **Descriptive** | Описать процесс | «Как Netflix внедрял KMP?» |
| **Explanatory** | Объяснить причины | «Почему McDonald's снизил crash rate на 60%?» |

### Survivorship Bias

> **Survivorship bias** (Wald, 1943) — систематическая ошибка, при которой анализируются только «выжившие» (успешные случаи), а неудачные игнорируются.

Применительно к KMP case studies:
- **Публикуются:** Netflix, McDonald's, Cash App (успешные)
- **Не публикуются:** проекты, откатившие KMP; команды, не справившиеся с migration
- **Airbnb (2018):** редкий пример публичного отказа от cross-platform (React Native), ставший ценным data point

### Technology Adoption Lifecycle

Everett Rogers (1962), *Diffusion of Innovations*:

| Категория | Доля | KMP adoption |
|-----------|------|-------------|
| Innovators | 2.5% | 2020-2021: Cash App, TouchLab |
| Early Adopters | 13.5% | 2022-2023: Netflix, Philips |
| Early Majority | 34% | 2024-2025: McDonald's, Google Docs |
| Late Majority | 34% | 2026+: Enterprise adoption |
| Laggards | 16% | — |

KMP в 2025-2026 находится на переходе от Early Majority к массовому adoption (подтверждено Google I/O 2025: «KMP recommended for business logic sharing»).

> **CS-фундамент:** Анализ case studies связан с [[kmp-production-checklist]] (что нужно для production) и [[kmp-architecture-patterns]] (паттерны успешных проектов). Теоретическая база — Case Study Research (Yin, 2014), Diffusion of Innovations (Rogers, 1962), Survivorship Bias (Wald, 1943).

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

### Теоретические основы

- **Yin R. (2014).** *Case Study Research: Design and Methods.* 5th ed. — Методология case study: exploratory, descriptive, explanatory подходы.
- **Rogers E. (1962).** *Diffusion of Innovations.* — Technology Adoption Lifecycle для анализа KMP adoption.
- **Wald A. (1943).** *A Method of Estimating Plane Vulnerability Based on Damage of Survivors.* — Survivorship bias как ключевой фактор при анализе case studies.

### Практические руководства

- [KMP Case Studies (JetBrains)](https://kotlinlang.org/docs/multiplatform/case-studies.html) — Официальные case studies.
- [Netflix KMP](https://netflixtechblog.com/) — Технический блог Netflix.
- [Cash App KMP](https://cash.app/blog) — Опыт Cash App с KMP (7+ лет в production).

---

## Проверь себя

> [!question]- Почему Netflix начал внедрение KMP именно со studio tools, а не с основного приложения?
> Studio tools -- внутренние приложения с меньшим risk tolerance. Позволяют проверить технологию без влияния на миллионы пользователей. После успеха (60% shared code) KMP был расширен на другие приложения. Типичная стратегия enterprise adoption.

> [!question]- Какой общий паттерн прослеживается в подходе Netflix, McDonald's и Cash App к внедрению KMP?
> Все начали со shared business logic (data layer, networking, repositories), оставив UI нативным. Постепенно расширяли shared code от 10-20% до 60-80%. Никто не делал полную переписку. Все использовали модульный подход.

> [!question]- Почему Google выбрал KMP для Google Docs iOS, а не Flutter?
> Google Docs iOS нуждался в нативном iOS experience (UIKit/SwiftUI) с shared business logic между Android и iOS. Flutter потребовал бы переписку UI на Dart. KMP позволил вынести document editing logic в shared, сохранив нативный iOS UI.

---

## Ключевые карточки

Какие крупные компании используют KMP в production?
?
Netflix (studio apps, 60% shared), McDonald's (global app), Google Docs (iOS), Cash App (fintech), Philips (healthcare), Forbes (mobile), 9GAG (70% shared). 20,000+ компаний по данным JetBrains.

Какой процент кода обычно выносится в shared?
?
Типично 60-80% для зрелых KMP-проектов. Netflix -- 60%, 9GAG -- 70%. Начинают с 10-20% (networking/data layer) и постепенно расширяют. UI обычно остаётся нативным (20-40%).

С чего начинают крупные компании при внедрении KMP?
?
Shared data layer: networking, models, repositories, use cases. Минимальный риск, максимальная выгода. Не затрагивает UI. Proof of concept на одном модуле, затем масштабирование.

Какие business results показывают KMP-проекты?
?
Сокращение дублирования кода на 60-80%, ускорение feature delivery на 25-40%, унификация бизнес-логики (один баг -- одно исправление), снижение стоимости поддержки.

Какие уроки из case studies самые важные?
?
Начинать с малого (один модуль), получить buy-in iOS-команды (SKIE/Swift Export), измерять ROI (shared code %, build time, bugs), не переписывать UI на первом этапе, использовать proven архитектуру (Clean Architecture + MVI).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-production-checklist]] | Чеклист перед запуском в production |
| Углубиться | [[kmp-migration-from-native]] | Как повторить путь Netflix/McDonald's |
| Смежная тема | [[kmp-architecture-patterns]] | Архитектура, используемая в case studies |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Данные актуальны на январь 2026*
