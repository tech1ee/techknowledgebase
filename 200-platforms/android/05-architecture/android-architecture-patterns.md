---
title: "Архитектурные паттерны Android: обзор и сравнение"
created: 2025-12-17
modified: 2026-02-19
type: overview
area: android
confidence: high
tags:
  - topic/android
  - topic/architecture
  - type/overview
  - level/intermediate
related:
  - "[[android-architecture-evolution]]"
  - "[[android-mvc-mvp]]"
  - "[[android-mvvm-deep-dive]]"
  - "[[android-mvi-deep-dive]]"
  - "[[android-clean-architecture]]"
  - "[[android-compose-architectures]]"
  - "[[android-viewmodel-internals]]"
  - "[[android-repository-pattern]]"
  - "[[android-modularization]]"
  - "[[android-activity-lifecycle]]"
  - "[[solid-principles]]"
  - "[[design-patterns-overview]]"
  - "[[coupling-cohesion]]"
  - "[[kotlin-flow]]"
cs-foundations: [separation-of-concerns, unidirectional-data-flow, dependency-inversion, layered-architecture, state-management]
prerequisites:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
reading_time: 25
difficulty: 5
study_status: not_started
mastery: 0
---

# Архитектурные паттерны Android: обзор и сравнение

Это **навигационный хаб** по архитектурным паттернам Android. Здесь собраны сравнения, таблицы решений и ссылки на детальные разборы каждого паттерна. Код и реализации вынесены в отдельные deep-dive файлы.

> **Prerequisites:**
> - [[android-overview]] — общее понимание платформы
> - [[android-activity-lifecycle]] — проблемы lifecycle и configuration changes
> - Базовое понимание паттернов проектирования

---

## Зачем нужна архитектура?

Без архитектуры весь код живёт в Activity: сеть, база, UI-логика, навигация. Результат -- "God Activity" на тысячи строк. Это не абстрактная проблема: любое Android-приложение сталкивается с configuration changes (поворот экрана), process death (система убивает фоновый процесс) и конкурентными запросами.

**Проблемы без архитектуры:**

| Проблема | Последствие | Как архитектура решает |
|----------|-------------|----------------------|
| **Потеря данных при повороте** | Activity пересоздаётся, данные теряются, повторный запрос | ViewModel переживает config change |
| **Невозможно тестировать** | UI, сеть, логика смешаны, нужен эмулятор для любого теста | ViewModel тестируется unit-тестами без Android |
| **Дублирование кода** | Тот же запрос в 5 экранах, 5 копий кода | Repository переиспользуется между экранами |
| **Race conditions** | Быстрый поворот экрана, несколько параллельных запросов | viewModelScope автоматически отменяет при уничтожении |
| **Утечки памяти** | Callback держит ссылку на уничтоженную Activity | ViewModel не держит reference на View |
| **Сложность поддержки** | Activity на 2000 строк, никто не понимает код | Activity ~50 строк, логика в ViewModel |

**Наивные решения и их ограничения:**

| Подход | Проблема |
|--------|----------|
| `onSaveInstanceState` + Bundle | Ограничение ~1MB, только Parcelable, не решает проблему тестирования |
| Singleton / static переменные | Глобальное состояние, memory leaks с Context, состояние между тестами |
| База данных для всего | Overhead для временных данных (loading state), сложность для простых случаев |
| Retained Fragment | Deprecated, сложный lifecycle, не работает с Compose |

Архитектура разделяет код на слои с чёткими ответственностями: UI отображает, ViewModel хранит state и логику, Repository получает данные. Каждый слой тестируется отдельно. Это не "лучшая практика ради практики" -- это решение конкретных проблем Android-платформы.

> Пример "God Activity" и пошаговая миграция на MVVM с кодом: [[android-mvc-mvp]]

**Когда НЕ нужна сложная архитектура:**
- Прототип или MVP (Minimum Viable Product) -- скорость важнее структуры
- Экран без логики (статичный About, лицензии)
- Одноразовое приложение (хакатон, демо)
- Обучение Android -- сначала понять basics, потом добавлять слои
- Виджет или простой утилитарный экран внутри большого приложения

---

## Терминология

| Термин | Значение |
|--------|----------|
| **MVC** | Model-View-Controller -- классический UI паттерн |
| **MVP** | Model-View-Presenter -- MVC с явным контрактом View |
| **MVVM** | Model-View-ViewModel -- UI паттерн с data binding |
| **MVI** | Model-View-Intent -- MVVM + unidirectional flow |
| **Clean Architecture** | Разделение на Presentation/Domain/Data слои |
| **ViewModel** | Хранит UI state, переживает config change |
| **Repository** | Абстракция над источниками данных |
| **Use Case** | Бизнес-логика (Clean Architecture) |
| **UDF** | Unidirectional Data Flow -- однонаправленный поток |
| **State** | Текущее состояние UI |
| **Event/Intent** | Действие пользователя или системы |
| **Effect** | Одноразовое событие (navigation, toast) |
| **Presenter** | Посредник между View и Model (MVP) |
| **Reducer** | Pure function: (State, Intent) -> State |

---

## Почему Android-архитектура особенная

Android-архитектура отличается от generic software architecture из-за уникальных ограничений платформы:

| Ограничение платформы | Влияние на архитектуру | Решение |
|----------------------|----------------------|---------|
| **Configuration changes** (rotation, locale, dark mode) | Activity уничтожается и создаётся заново | ViewModel переживает config change |
| **Process death** | Система убивает фоновый процесс при нехватке памяти | SavedStateHandle для восстановления критичных данных |
| **Lifecycle complexity** | Activity/Fragment имеют сложный lifecycle с множеством состояний | Lifecycle-aware компоненты, collectAsStateWithLifecycle() |
| **UI thread constraint** | Тяжёлые операции блокируют UI, ANR через 5 секунд | Coroutines + Dispatchers, viewModelScope |
| **Permission model** | Runtime permissions прерывают flow приложения | Отделение UI (запрос permission) от логики (обработка результата) |
| **Navigation complexity** | Back stack, deep links, multi-module navigation | Navigation Component, type-safe routes |
| **Background restrictions** | Doze mode, app standby, battery optimization | WorkManager, foreground services |

Эти ограничения объясняют, почему Android не может просто взять паттерны из web/backend. ViewModel, SavedStateHandle, viewModelScope -- это не "Android boilerplate", а решения реальных проблем платформы.

> Подробнее об Activity lifecycle: [[android-activity-lifecycle]]
> ViewModel под капотом: [[android-viewmodel-internals]]

---

## Быстрое сравнение паттернов

| Критерий | MVC | MVP | MVVM | MVI | Clean Architecture | Compose-native |
|----------|-----|-----|------|-----|-------------------|----------------|
| **View-Logic связь** | Тесная (Activity = оба) | Через интерфейс | Через наблюдение за state | Через наблюдение за state | Через слои абстракций | Через state hoisting |
| **Logic знает о View** | Да | Да (interface) | Нет | Нет | Нет | Нет |
| **State management** | В Activity | В Presenter | Multiple StateFlow | Single State object | Зависит от UI паттерна | Single State + Compose state |
| **Data flow** | Bidirectional | Bidirectional | Mixed (semi-UDF) | Unidirectional | Unidirectional | Unidirectional |
| **Testability** | Poor | Medium | Good | Excellent | Excellent | Excellent |
| **Boilerplate** | Minimal | High (interfaces) | Low | Medium (Intent/State) | High (layers, mappers) | Low-Medium |
| **Lifecycle safety** | Нет | Manual | Auto (ViewModel) | Auto (ViewModel) | Auto (ViewModel) | Auto (ViewModel) |
| **KMP support** | Нет | Partial | Partial | Good (MVIKotlin) | Excellent (domain pure Kotlin) | Good (Decompose, Circuit) |
| **Google recommendation** | Нет | Устарел | Рекомендован (2017+) | Рекомендован (UDF, 2020+) | Optional domain layer | Compose-first (2023+) |
| **Best for** | Прототипы | Legacy проекты | Простые-средние apps | Сложный state | Большие команды/проекты | Современные Compose apps |

> Детальные реализации каждого паттерна с кодом:
> - MVC/MVP: [[android-mvc-mvp]]
> - MVVM: [[android-mvvm-deep-dive]]
> - MVI: [[android-mvi-deep-dive]]
> - Clean Architecture: [[android-clean-architecture]]
> - Compose-native (Circuit, Decompose, Molecule): [[android-compose-architectures]]

---

## Детальное сравнение по критериям

### Separation of Concerns

**MVC** не разделяет View и Controller -- Activity выполняет обе роли, что приводит к "Massive View Controller". Бизнес-логика, навигация, работа с сетью и отображение данных смешаны в одном классе.

**MVP** формализует разделение через интерфейс View, но Presenter всё ещё знает о View (держит reference на интерфейс). Это создаёт тесную связь: изменение UI требует изменения контракта.

**MVVM** полностью разрывает связь: ViewModel экспонирует state через StateFlow, View подписывается. ViewModel ничего не знает о том, кто его наблюдает. Но state может обновляться из нескольких мест внутри ViewModel.

**MVI** идёт дальше -- единый State object вместо множества observables. Все изменения проходят через reducer, что формализует каждое изменение state.

**Clean Architecture** добавляет разделение по слоям (Presentation/Domain/Data), где Domain не зависит от платформы. Это самый строгий уровень separation, но и самый дорогой по boilerplate.

**Compose-native** фреймворки (Circuit, Decompose) формализуют separation через Presenter как Composable function: state in, events out. UI и логика -- разные Composable, соединяемые фреймворком.

> Подробнее о Separation of Concerns как CS-концепции: [[coupling-cohesion]]

### Testability

**MVC** -- тесты практически невозможны без instrumented tests. Вся логика привязана к Activity lifecycle.

**MVP** -- Presenter тестируется с mock View, но тесты хрупкие: завязаны на порядок вызовов методов View-интерфейса. Изменение UI ломает тесты логики.

**MVVM** -- ViewModel тестируется как обычный Kotlin-класс с JUnit. StateFlow проверяется через Turbine. Не нужен Android Framework. Типичный тест: создать ViewModel с fake Repository, вызвать метод, проверить state.

**MVI** -- лучшая тестируемость из всех паттернов. Reducer = pure function: (State, Intent) -> State. Тестируется без coroutines, без mock'ов, без Android. Каждый state transition проверяется изолированно.

**Clean Architecture** -- Domain layer компилируется как чистый Kotlin/JVM модуль, Use Cases тестируются мгновенно (нет Android зависимостей). Data layer тестируется отдельно с fake API/DB.

**Compose-native** -- Presenter в Circuit/Molecule = Composable function, тестируется через Molecule testing utilities. UI тестируется отдельно через Compose testing с fake state.

> Примеры тестов для каждого паттерна: [[android-mvvm-deep-dive]], [[android-mvi-deep-dive]]

### Boilerplate

| Паттерн | Что нужно создать на каждый экран |
|---------|----------------------------------|
| **MVC** | Activity (всё в одном) |
| **MVP** | View interface + Presenter interface + Presenter impl + Activity |
| **MVVM** | UiState data class + ViewModel + Screen composable |
| **MVI** | State + Intent sealed class + Effect sealed class + ViewModel с reducer + Screen |
| **Clean** | Dto + Domain model + UiModel + Mappers + Repository interface + Repository impl + UseCase + ViewModel + Screen |
| **Compose-native** | State + Event + Presenter composable + UI composable (фреймворк снижает boilerplate) |

**MVC** -- минимальный boilerplate, но ценой хаоса в коде. **MVP** -- высокий: 4 файла на экран. **MVVM** -- умеренный: 2-3 файла. **MVI** -- выше чем MVVM из-за sealed classes. **Clean Architecture** -- самый высокий: до 8-10 файлов на feature. **Compose-native** (Orbit, Circuit) -- снижают boilerplate MVI через DSL и convention-over-configuration.

### State Management

**MVC/MVP** -- state разбросан по полям Activity/Presenter, нет единого источника правды. При rotation state теряется или дублируется.

**MVVM** -- state в нескольких StateFlow/LiveData. Проблема: если ViewModel имеет `_users`, `_isLoading`, `_error` как отдельные потоки, возможна рассинхронизация (loading = false, но users ещё пустой). Решение: единый UiState data class.

**MVI** -- единый immutable State object, все изменения через reducer: гарантия consistency. State transitions детерминированы: одинаковая последовательность Intent'ов всегда даёт одинаковый State. Идеально для time-travel debugging.

**Compose-native** -- единый state + Compose `remember`/`derivedStateOf` для производных состояний. Compose сам оптимизирует recomposition на основе изменений state.

Для complex forms и real-time данных MVI/Compose-native дают лучшую предсказуемость. Для простых CRUD -- MVVM с единым UiState достаточно.

### Lifecycle Safety

**MVC** -- никакой защиты, все данные теряются при rotation. Callback'и могут вызываться на уничтоженной Activity.

**MVP** -- Presenter нужно вручную привязывать/отвязывать от View. Забыл `detachView()` в `onDestroy()` -- утечка памяти. Забыл проверку `isViewAttached()` -- crash.

**MVVM/MVI/Clean/Compose** -- ViewModel переживает configuration change автоматически (хранится в ViewModelStore). Coroutines в viewModelScope отменяются при onCleared(). StateFlow с `collectAsStateWithLifecycle()` безопасно останавливает подписку когда UI в background.

**Важно:** ViewModel НЕ переживает process death. Для восстановления критичных данных (ID выбранного элемента, позиция скролла, введённый текст) нужен SavedStateHandle.

> Детали lifecycle ViewModel: [[android-viewmodel-internals]]

### KMP Compatibility

| Паттерн | KMP-ready | Что переносимо | Что остаётся Android-only |
|---------|-----------|----------------|--------------------------|
| **MVC/MVP** | Нет | -- | Всё привязано к Activity |
| **MVVM** | Частично | Бизнес-логика (если выделена) | AndroidX ViewModel, lifecycle |
| **MVI** | Хорошо | State, Intent, Reducer | UI, navigation |
| **Clean** | Отлично | Весь Domain layer | Presentation, Data (частично) |
| **Compose-native** | Хорошо-Отлично | Presenter, State, логика | Platform-specific UI |

**MVIKotlin** изначально мультиплатформенный: Store (reducer + executor) = pure Kotlin. **Decompose** полностью KMP-ready с navigation и lifecycle. **Circuit** пока Android/JVM only (Compose Multiplatform support в разработке).

> Подробнее о KMP-архитектурах: [[android-compose-architectures]]

---

## Decision Tree: какой паттерн выбрать

### Шаг 1: UI Framework

```
Используете Compose?
├── НЕТ (XML Views) ──────────────────────────────┐
│                                                   │
│   Это legacy проект?                             │
│   ├── ДА → Оставить MVP как есть                 │
│   │        Новые экраны: MVVM + LiveData/StateFlow│
│   │        → [[android-mvc-mvp]]                  │
│   │                                               │
│   └── НЕТ → Почему не Compose?                   │
│             ├── Начните миграцию на Compose        │
│             └── Пока: MVVM + StateFlow + ViewBinding│
│                                                   │
└── ДА (Compose) ──────────────────── → Шаг 2      │
```

### Шаг 2: Размер и сложность (Compose)

```
Размер проекта?
│
├── Малый (1-5 экранов, 1-2 разработчика)
│   └── MVVM + StateFlow + Compose
│       Без domain layer, без MVI overhead
│       → [[android-mvvm-deep-dive]]
│
├── Средний (5-20 экранов, 2-5 разработчиков)
│   │
│   ├── Сложный state (формы, real-time, multi-source)?
│   │   ├── ДА → MVI: Orbit (простой) или ручной MVI
│   │   │        → [[android-mvi-deep-dive]]
│   │   └── НЕТ → MVVM + StateFlow достаточно
│   │            → [[android-mvvm-deep-dive]]
│   │
│   └── Нужен domain layer?
│       ├── Сложная бизнес-логика → Да, Clean Architecture
│       └── Простой CRUD → Нет, ViewModel + Repository
│
└── Большой (20+ экранов, 5+ разработчиков)
    │
    ├── Нужен KMP (Android + iOS + Desktop)?
    │   ├── ДА → Decompose + MVIKotlin + Clean Architecture
    │   │        → [[android-compose-architectures]]
    │   └── НЕТ → Circuit (Slack) или Ballast
    │            → [[android-compose-architectures]]
    │
    └── Clean Architecture рекомендована
        → [[android-clean-architecture]]
```

### Шаг 3: Нужна ли Clean Architecture? (ортогонально к UI паттерну)

```
Добавлять Domain Layer?
│
├── ДА, если выполняется хотя бы 2 из:
│   ✓ Команда > 5 человек
│   ✓ Сложная бизнес-логика (валидация, расчёты, правила)
│   ✓ KMP / переиспользование логики
│   ✓ Долгосрочный проект (3+ лет поддержки)
│   ✓ Use Cases переиспользуются между экранами
│   → [[android-clean-architecture]]
│
└── НЕТ, если:
    ✗ < 5 экранов
    ✗ Tight deadlines (MVP продукт)
    ✗ Простой CRUD без бизнес-логики
    ✗ Прототип / хакатон
    → ViewModel + Repository достаточно
```

---

## Когда что использовать

| Критерий | MVC | MVP | MVVM | MVI | Clean Arch | Compose-native |
|----------|-----|-----|------|-----|------------|----------------|
| **Размер проекта** | Прототип | Legacy | Малый-средний | Средний-большой | Большой | Средний-большой |
| **Команда** | 1 человек | Любая (legacy) | 1-5 | 3-10 | 5+ | 3-10 |
| **Сложность state** | Минимальная | Простой | Простой-средний | Сложный | Любая | Сложный |
| **KMP** | Нет | Нет | Ограниченно | MVIKotlin | Domain layer | Decompose |
| **Compose** | Нет | Нет | Да | Да | Да | Нативно |
| **Новый проект (2025)** | Нет | Нет | Да (простой) | Да (сложный) | По необходимости | Да |
| **Time to market** | Быстро | Средне | Быстро | Средне | Медленно | Средне |
| **Onboarding новичков** | Просто | Средне | Просто | Средне | Сложно | Средне |
| **Рефакторинг** | Легко сломать | Контракт помогает | Хорошо | Отлично | Отлично | Хорошо |
| **Debugging state** | Сложно | Сложно | Средне | Просто (UDF) | Средне | Просто (UDF) |

**Краткая рекомендация по состоянию на 2025 год:**
- **Большинство новых проектов:** MVVM + Compose + StateFlow. Добавить MVI при росте сложности state
- **Большие команды / сложная логика:** Clean Architecture + MVI
- **KMP проекты:** Decompose + MVIKotlin или KMP ViewModel
- **Legacy проекты:** не трогать MVP, новые экраны на MVVM/MVI

---

## Когда какой паттерн НЕ подходит

| Паттерн | НЕ подходит когда | Почему |
|---------|------------------|--------|
| **MVC** (Model-View-Controller) | Android приложения в принципе | Activity/Fragment -- это и View, и Controller одновременно. Получается "Massive View Controller" с запутанной логикой. Нет решения для configuration changes. |
| **MVP** (Model-View-Presenter) | Compose UI | Presenter держит reference на View интерфейс, утечки памяти при rotation. Много boilerplate (interface для каждого View). Устарел с появлением ViewModel. |
| **MVVM** | Сложные формы с множеством взаимосвязанных полей | State может обновляться из разных мест, трудно отследить источник изменений. Race conditions при параллельных updates. Нет строгого порядка событий. |
| **MVVM** | Real-time приложения (чаты, стримы) | События приходят асинхронно и могут конфликтовать. Сложно гарантировать порядок обработки. State может быть inconsistent между обновлениями. |
| **MVI** | Простые CRUD экраны | Избыточный boilerplate: Intent sealed class для каждого действия, reducer логика, Effect обработка. 3x больше кода чем MVVM для простого списка. |
| **MVI** | Прототипы и MVP | Долгая настройка архитектуры (Intent, State, Effect, Reducer). Сложнее onboarding новых разработчиков. Замедляет итерации. |
| **Clean Architecture** | Маленькие приложения (< 5 экранов) | Over-engineering: Use Cases для простой логики, 3 модели (Dto/Domain/Ui) для одной сущности, множество mapper'ов. Сложность не окупается. |
| **Clean Architecture** | Tight deadlines | Начальная настройка требует времени: модульная структура, DI setup, слои абстракций. Медленнее добавлять features на старте. |
| **Clean Architecture** | Команда джунов | Высокий порог входа: понимание Dependency Rule, слоёв, SOLID. Легко нарушить архитектуру неправильными зависимостями. |
| **Compose-native** (Circuit, Decompose) | Legacy View-based проекты | Требуют полного перехода на Compose. Дополнительная зависимость от библиотеки. Молодая экосистема, меньше ресурсов и community support. |
| **Compose-native** | Маленькие приложения | Overhead фреймворка не оправдан. Обычный ViewModel + StateFlow проще и достаточно для 1-5 экранов. |

---

## Эволюция рекомендаций Google

| Год | Рекомендованный подход | Ключевая библиотека/инструмент | Примечание |
|-----|----------------------|-------------------------------|------------|
| **2008-2013** | Нет рекомендаций | Activity, Fragment (2011) | "Пишите как хотите". God Activity -- норма. AsyncTask для сети |
| **2014-2016** | MVP (community) | Mosby, Moxy, RxJava | Google не давал рекомендаций. Community самостоятельно выработал MVP. Google Architecture Blueprints (2016) показали варианты |
| **2017** | MVVM | Architecture Components: ViewModel, LiveData, Room, Lifecycle | Google I/O 2017 -- первые официальные рекомендации по архитектуре. "Guide to App Architecture" v1 |
| **2018-2019** | MVVM + Repository | Jetpack: Navigation, Paging 2, WorkManager | Расширение Jetpack. Navigation Component для Single Activity. Coroutines входят в mainstream |
| **2020-2021** | MVVM + UDF | StateFlow, Hilt, Paging 3, DataStore | Переход с LiveData на StateFlow. Hilt как official DI. Kotlin-first подход |
| **2022-2023** | Compose + UDF/MVI | Compose 1.0+, collectAsStateWithLifecycle, Material 3 | "Guide to App Architecture" v2. Compose-first. UiState pattern. Now in Android sample |
| **2024-2025** | Compose-first + UDF | Compose Multiplatform, Circuit, Navigation 3 (alpha) | KMP-ready архитектуры. Compose для Android, Desktop, iOS, Web. Type-safe navigation |

**Ключевые точки перелома:**
- **2017**: до этого года у Android не было официальной архитектурной рекомендации. Каждая команда изобретала своё
- **2020**: StateFlow заменил LiveData как рекомендованный механизм для UI state (LiveData не deprecated, но StateFlow предпочтительнее)
- **2023**: Compose стал default для нового UI. View-based разработка перешла в режим поддержки

> Полная хронология с деталями каждого этапа: [[android-architecture-evolution]]

---

## Чеклист архитектуры

**Базовый (любой проект):**
```
□ ViewModel не держит reference на View/Context
□ UI State — immutable data class (не отдельные var поля)
□ Один source of truth для state (единый StateFlow на экран)
□ Repository абстрагирует источники данных
□ DI для зависимостей (Hilt/Koin)
□ Side effects через Channel/SharedFlow, не через LiveData
□ collectAsStateWithLifecycle() вместо collectAsState()
□ SavedStateHandle для данных, переживающих process death
```

**Расширенный (средний/большой проект):**
```
□ Use Cases для переиспользуемой бизнес-логики (не для простого проксирования)
□ Маппинг между слоями (Dto → Domain → UiModel) при расхождении моделей
□ Error handling стратегия (Result type, sealed class)
□ Offline-first: данные из кэша при отсутствии сети
□ Navigation отделена от ViewModel (навигация через events)
□ Модульная структура для feature-modules (при 15+ экранах)
□ Lint rules для проверки dependency direction между слоями
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "MVVM устарел, нужен только MVI" | MVVM отлично работает для большинства приложений. MVI добавляет сложность. Для простых CRUD экранов MVVM проще и достаточно. MVI оправдан для сложных multi-source state экранов |
| "Clean Architecture обязательна" | Clean Architecture -- overkill для малых приложений. Для MVP (Minimum Viable Product) достаточно ViewModel + Repository. Google: domain layer is optional |
| "Use Case = один метод Repository" | Если UseCase просто проксирует Repository -- он не нужен. UseCase для orchestration между repositories, validation, business rules |
| "Domain layer обязателен" | Для простых CRUD apps domain layer = boilerplate. Google: optional domain layer. Добавляй когда логика усложняется |
| "MVVM = ViewModel + LiveData" | MVVM -- паттерн UI layer, не про LiveData. StateFlow, RxJava, Compose state -- всё MVVM если есть separation View/ViewModel |
| "MVI сложнее MVVM" | Базовый MVI = MVVM + explicit Intent. StateFlow + sealed class Intent + reducer function. Не rocket science |
| "ViewModel решает все проблемы lifecycle" | ViewModel не переживает process death. Для восстановления нужен SavedStateHandle. ViewModel -- про config changes, не про полное сохранение состояния |
| "Compose требует MVI" | Compose работает с любой архитектурой. ViewModel + StateFlow = pseudo-MVI без explicit Intents. Полноценный MVI нужен для complex state management |
| "MVP полностью мёртв" | MVP всё ещё используется в legacy проектах. Миграция на MVVM часто не оправдана для стабильного кода. Новые проекты -- да, MVVM/MVI лучше |
| "Модуляризация = Clean Architecture" | Модуляризация про build time и team boundaries. Clean Architecture про dependency direction. Можно делать отдельно |

---

## CS-фундамент

| CS-концепция | Как применяется в архитектуре |
|--------------|-------------------------------|
| **Separation of Concerns** | View отвечает за отображение, ViewModel за UI логику, Repository за данные. Каждый компонент -- одна ответственность |
| **Dependency Inversion** | High-level modules не зависят от low-level. ViewModel зависит от interface Repository, не от implementation. Domain layer определяет интерфейсы |
| **Unidirectional Data Flow** | State flows down (ViewModel -> View). Events flow up (View -> ViewModel). Single source of truth. Предсказуемость изменений |
| **Observer Pattern** | StateFlow/LiveData notify observers. View подписывается. Слабая связанность producer/consumer |
| **State Machine** | MVI Reducer: (State, Intent) -> State. Deterministic transitions. Одинаковый input = одинаковый output |
| **Layered Architecture** | Presentation -> Domain -> Data. Dependencies направлены внутрь. Domain не знает о Android |
| **Repository Pattern** | Abstraction над data sources. ViewModel не знает откуда данные: network, database, cache |
| **Command Pattern** | MVI Intent = Command object. Encapsulation запроса. Можно queue, log, replay |
| **Immutability** | UI State immutable. Изменение = новый объект. Thread safety, предсказуемость |
| **Single Source of Truth** | Один источник данных для UI. StateFlow в ViewModel. Нет conflicting state |

---

## Типичные сценарии выбора

### Сценарий 1: Новый проект, маленькая команда (1-3 человека)
**Контекст:** Стартап, MVP продукт, 5-10 экранов, Compose UI, нужно быстро выйти на рынок.
**Рекомендация:** MVVM + Repository + StateFlow. Без domain layer. Hilt для DI.
**Почему:** Минимальный boilerplate, быстрый старт, достаточная testability. Domain layer добавить позже при росте сложности.
> Реализация: [[android-mvvm-deep-dive]]

### Сценарий 2: Средний проект, сложные формы
**Контекст:** Банковское приложение, 20+ экранов, сложные формы с валидацией, несколько источников данных.
**Рекомендация:** MVI (Orbit или ручной) + Clean Architecture + Hilt.
**Почему:** MVI гарантирует predictable state для форм. Clean Architecture изолирует бизнес-правила валидации в Domain layer. Use Cases переиспользуются между экранами.
> Реализация: [[android-mvi-deep-dive]], [[android-clean-architecture]]

### Сценарий 3: Мультиплатформенный проект
**Контекст:** Android + iOS + Desktop, общая бизнес-логика, Compose Multiplatform.
**Рекомендация:** Decompose + MVIKotlin + Clean Architecture (domain = pure Kotlin).
**Почему:** Decompose предоставляет KMP-ready lifecycle и navigation. MVIKotlin -- мультиплатформенный MVI. Domain layer шарится между платформами без изменений.
> Реализация: [[android-compose-architectures]]

### Сценарий 4: Legacy проект, постепенная миграция
**Контекст:** Приложение на Java + XML + MVP, 100+ экранов, 10+ разработчиков, нельзя переписать всё.
**Рекомендация:** Постепенная миграция MVP -> MVVM для новых экранов. Compose для новых features. Legacy экраны не трогать.
**Почему:** Миграция стабильного MVP-кода не оправдана. Новые экраны на MVVM + Compose. Общий Repository layer для обоих подходов.
> Миграция: [[android-mvc-mvp]]

### Сценарий 5: Compose-first, modern stack
**Контекст:** Новый проект полностью на Compose, команда 5+ человек, сложный navigation.
**Рекомендация:** Circuit (Slack) или Decompose + Compose Navigation.
**Почему:** Circuit нативно интегрируется с Compose, Presenter = Composable. Decompose даёт KMP-ready navigation. Обе библиотеки формализуют separation of concerns на уровне фреймворка.
> Реализация: [[android-compose-architectures]]

---

## Связь с другими темами

### Паттерны (deep-dives)

**[[android-mvc-mvp]]** -- детальный разбор MVC и MVP паттернов: почему MVC не работает в Android (Activity = View + Controller), как устроен MVP с контрактами (View interface, Presenter), примеры God Activity и пошаговая миграция на MVVM. Начните здесь если работаете с legacy кодом или хотите понять историю.

**[[android-mvvm-deep-dive]]** -- полная реализация MVVM: UiState data class patterns (sealed vs data class), обработка one-time events (Channel vs SharedFlow), ViewModel + StateFlow vs LiveData, Compose integration. Код примеров для каждого сценария и testing best practices.

**[[android-mvi-deep-dive]]** -- MVI библиотеки в сравнении: Orbit MVI (самый простой), MVIKotlin (KMP-ready), Ballast (feature-rich). Реализация reducer, Side Effects, время-travel debugging. Выбирайте если у вас сложный multi-source state.

**[[android-clean-architecture]]** -- слои Presentation/Domain/Data, Use Cases (когда нужны, когда нет), Dependency Rule, структура пакетов, маппинг моделей (Dto -> Domain -> UiModel). Практические примеры: когда domain layer оправдан, а когда это over-engineering.

**[[android-compose-architectures]]** -- Compose-native фреймворки: Circuit (Slack) -- Presenter + UI как отдельные Composable; Decompose (Arkivanov) -- KMP lifecycle и navigation; Molecule (CashApp) -- StateFlow из Composable. Архитектуры, спроектированные для Compose с нуля.

### Контекст и фундамент

**[[android-architecture-evolution]]** -- полная хронология эволюции Android-архитектуры: от God Activity (2008) через MVP-эпоху (2014) к Architecture Components (2017), Compose (2021) и KMP (2024). Контекст для понимания "почему рекомендации менялись".

**[[android-viewmodel-internals]]** -- как ViewModel работает под капотом: ViewModelStore, ViewModelProvider, SavedStateHandle, CreationExtras. Почему ViewModel переживает rotation но не process death. Необходимо для debugging проблем с lifecycle.

**[[android-repository-pattern]]** -- Repository pattern в деталях: offline-first стратегии, кэширование (memory -> disk -> network), Single Source of Truth для данных, стратегии синхронизации, обработка ошибок.

**[[android-modularization]]** -- модульная архитектура: feature modules, api/impl split, build time optimization, team boundaries. Не путать с Clean Architecture -- модуляризация про физическое разделение кода, Clean Architecture про логическое.

### CS-фундамент

**[[solid-principles]]** -- SOLID как фундамент архитектурных решений. Clean Architecture целиком построена на Dependency Inversion (Domain определяет интерфейсы) и Single Responsibility (каждый слой -- одна задача). Interface Segregation определяет размер Repository интерфейсов.

**[[coupling-cohesion]]** -- связность и сцепленность: метрики для оценки качества разделения на модули и слои. Архитектурная цель: высокая cohesion внутри модуля (всё в feature module связано), low coupling между модулями (общение через интерфейсы).

**[[design-patterns-overview]]** -- архитектурные паттерны Android строятся на классических GoF-паттернах: Repository (Facade + Gateway), Observer (StateFlow/LiveData), Strategy (инъекция Use Cases), Command (MVI Intent). Понимание базовых паттернов помогает глубже осмыслить архитектурные решения.

**[[kotlin-flow]]** -- StateFlow является стандартным механизмом для UI state в MVVM/MVI. Channel используется для one-shot side effects (навигация, Snackbar). Понимание cold/hot flows, operators и backpressure критично для правильной реализации reactive state management.

---

## Источники и дальнейшее чтение

**Книги:**
- Meier R. (2022). Professional Android, 4th Edition. -- комплексное руководство по Android-разработке, включая архитектурные паттерны и ViewModel
- Moskala M. (2021). Effective Kotlin. -- лучшие практики Kotlin, применяемые в архитектурных паттернах (sealed classes для state, coroutines для async)
- Bloch J. (2018). Effective Java, 3rd Edition. -- лучшие практики Java/JVM, принципы проектирования интерфейсов и классов
- Moskala M. (2022). Kotlin Coroutines: Deep Dive. -- корутины и Flow, основа reactive state management в MVVM/MVI
- Martin R. (2017). Clean Architecture. -- оригинальный источник Clean Architecture, Dependency Rule, SOLID

**Официальная документация:**
- [Guide to App Architecture](https://developer.android.com/topic/architecture) -- официальное руководство
- [Recommendations for Android Architecture](https://developer.android.com/topic/architecture/recommendations) -- best practices
- [UI Layer](https://developer.android.com/topic/architecture/ui-layer) -- ViewModel, UI State
- [Data Layer](https://developer.android.com/topic/architecture/data-layer) -- Repository pattern
- [Domain Layer](https://developer.android.com/topic/architecture/domain-layer) -- Use Cases (optional)

**Практические ресурсы:**
- [Now in Android](https://github.com/android/nowinandroid) -- официальный sample с MVVM + Clean Architecture
- [Architecture Samples](https://github.com/android/architecture-samples) -- варианты реализации
- [Orbit MVI](https://github.com/orbit-mvi/orbit-mvi) -- MVI фреймворк для Android
- [Circuit](https://github.com/slackhq/circuit) -- Compose-native архитектура от Slack
- [Decompose](https://github.com/arkivanov/Decompose) -- KMP lifecycle-aware business logic

---

## Проверь себя

> [!question]- Почему Google рекомендует MVVM/MVI с UDF, а не MVP для новых проектов?
> MVP тесно связывает Presenter и View через интерфейсы -- при изменении UI нужно менять контракт. MVVM с UDF: ViewModel не знает о View, предоставляет StateFlow. View подписывается. Преимущества: 1) Легче тестировать (ViewModel без Android зависимостей). 2) Lifecycle-safe (StateFlow не вызывает методы View). 3) Compose-friendly (state -> UI естественно).

> [!question]- Сценарий: команда спорит между Clean Architecture и MVVM. Какие критерии для выбора?
> Clean Architecture добавляет слой domain с use cases. Оправдана когда: 1) Сложная бизнес-логика (банкинг, медицина). 2) Логика переиспользуется между платформами (KMP). 3) Команда > 5 человек. Для простых CRUD приложений MVVM без domain layer достаточно -- лишний слой замедляет разработку без пользы. Решение: начать с MVVM, добавить domain при росте сложности.

> [!question]- Почему Domain layer не должен зависеть от Android Framework?
> Domain содержит бизнес-логику. Зависимость от Android: 1) Невозможно тестировать без эмулятора. 2) Невозможно переиспользовать в KMP. 3) Нарушает Dependency Inversion. Domain определяет интерфейсы (Repository, UseCase), Data layer реализует их. Результат: domain тестируется обычными JUnit, компилируется быстрее как Kotlin/JVM модуль.

> [!question]- В чём принципиальная разница между MVVM с единым UiState и MVI?
> Формально -- минимальна. MVVM с единым UiState data class и обработкой действий через методы ViewModel -- это "pseudo-MVI". Настоящий MVI добавляет: 1) Explicit Intent sealed class -- все действия формализованы как типы. 2) Reducer -- pure function (State, Intent) -> State -- детерминизм. 3) Side Effects как отдельный поток. Преимущество MVI: логирование всех Intent'ов, time-travel debugging, гарантия порядка обработки. Для простых экранов разница не оправдывает boilerplate.

> [!question]- Когда стоит выбрать Compose-native фреймворк (Circuit, Decompose) вместо обычного ViewModel + Compose?
> Compose-native фреймворки оправданы когда: 1) Нужна встроенная navigation (Circuit). 2) Нужен KMP с shared presentation logic (Decompose). 3) Команда > 5 человек и нужны строгие conventions. 4) Сложный граф экранов с deep links. Для простых проектов ViewModel + StateFlow + Compose Navigation достаточно -- меньше зависимостей и проще onboarding.

---

## Ключевые карточки

Чем MVVM отличается от MVI?
?
MVVM: ViewModel хранит несколько StateFlow, View подписывается на каждый. MVI: единый State object, Intent -> Reducer -> State. MVI строже (один источник правды), MVVM гибче (меньше boilerplate). MVI лучше для сложных экранов.

Что такое Clean Architecture в Android?
?
Три слоя: Presentation (UI + ViewModel), Domain (UseCase, Repository interfaces, модели), Data (Repository impl, API, DB). Зависимости направлены внутрь: Presentation -> Domain <- Data. Domain не знает о платформе.

Что такое UseCase (Interactor)?
?
Класс с единственной ответственностью в Domain layer. Инкапсулирует бизнес-правило. Может комбинировать несколько репозиториев. Пример: GetUserWithPostsUseCase вызывает UserRepository + PostsRepository и объединяет данные.

Что такое UDF (Unidirectional Data Flow)?
?
Данные текут в одном направлении: UI -> Intent/Event -> ViewModel -> State -> UI. Предсказуемость: каждое состояние результат конкретного события. Упрощает debugging и тестирование.

Какие слои в рекомендуемой архитектуре Google?
?
UI Layer (Activity/Compose + ViewModel), Domain Layer (optional, UseCases), Data Layer (Repository + DataSource). Потоки: UI -> events -> ViewModel -> Repository -> DataSource. Data flows up, events flow down.

Чем MVC отличается от MVP?
?
MVC: Controller = Activity, совмещает логику и UI, нет разделения. MVP: Presenter -- отдельный класс, View -- интерфейс, чёткий контракт. MVP тестируемее, но много boilerplate. Оба устарели для новых Android-проектов.

В чём преимущество Compose-native архитектур (Circuit, Decompose)?
?
Presenter = Composable function, нативная интеграция с Compose lifecycle. Circuit: Presenter + UI как отдельные Composable, navigation встроена. Decompose: KMP-ready, lifecycle-aware компоненты. Меньше boilerplate чем классический MVI.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Паттерн: MVC/MVP | [[android-mvc-mvp]] | Классические паттерны, legacy код, миграция |
| Паттерн: MVVM | [[android-mvvm-deep-dive]] | Реализация MVVM, UiState, events, best practices |
| Паттерн: MVI | [[android-mvi-deep-dive]] | MVI библиотеки, reducer, side effects |
| Паттерн: Clean | [[android-clean-architecture]] | Слои, Use Cases, Dependency Rule |
| Паттерн: Compose | [[android-compose-architectures]] | Circuit, Decompose, Molecule |
| Под капотом | [[android-viewmodel-internals]] | Как ViewModel работает внутри |
| Данные | [[android-repository-pattern]] | Repository, offline-first, кэширование |
| Масштабирование | [[android-modularization]] | Модульная архитектура |
| Хронология | [[android-architecture-evolution]] | Эволюция Android-архитектуры |
| Обзор | [[android-overview]] | Вернуться к карте раздела |

*Проверено: 2026-02-19 | Навигационный хаб по архитектурным паттернам Android*
