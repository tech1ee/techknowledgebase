---
title: "Эволюция архитектуры Android-приложений"
created: 2025-01-15
modified: 2026-02-19
type: overview
status: published
cs-foundations: [architectural-patterns, separation-of-concerns, state-management, design-evolution]
tags:
  - topic/android
  - topic/architecture
  - type/overview
  - level/intermediate
related:
  - "[[android-architecture-patterns]]"
  - "[[android-mvc-mvp]]"
  - "[[android-mvvm-deep-dive]]"
  - "[[android-mvi-deep-dive]]"
  - "[[android-compose-architectures]]"
  - "[[android-viewmodel-internals]]"
  - "[[android-state-management]]"
  - "[[android-activity-lifecycle]]"
  - "[[solid-principles]]"
  - "[[coupling-cohesion]]"
reading_time: 35
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Эволюция архитектуры Android-приложений: от God Activity к MVI

> От 2000-строчных Activity к современным Compose + MVI решениям

---

## Теоретические основы

> **Architectural evolution** — закономерный процесс усложнения программных систем, формализованный Lehman в **законах эволюции программного обеспечения** (Lehman, 1980): система, используемая в реальном мире, неизбежно усложняется, если ей не противодействовать (Law of Increasing Complexity).

Эволюция архитектуры Android отражает общую траекторию GUI-архитектур, начиная с **MVC** (Reenskaug, Smalltalk-80, 1979). Каждый переход решал конкретную проблему предыдущего поколения:

| Переход | Год (Android) | Решаемая проблема | Теоретическая основа |
|---------|--------------|-------------------|---------------------|
| Монолит → MVC/MVP | 2014 | God Activity (SRP violation) | Separation of Concerns (Dijkstra, 1974) |
| MVP → MVVM | 2017 | Boilerplate, ручной lifecycle | Observer pattern (Gamma et al., 1994) |
| MVVM → MVI | 2020 | Race conditions, multiple states | FSM + Event Sourcing (Fowler, 2005) |
| MVI → Compose-native | 2023 | ViewModel overhead, testability | Functional UI (Elliott/Hudak, 1997) |

> **Separation of Concerns** (Dijkstra, 1974) — принцип, согласно которому программа должна быть разделена на секции, каждая из которых отвечает за отдельный аспект функциональности. Все архитектурные паттерны Android — это варианты разделения трёх concerns: **UI rendering**, **business logic** и **data management**.

Параллельная эволюция на других платформах подтверждает универсальность этих переходов: iOS прошла путь MVC → MVVM → TCA (The Composable Architecture), Web — от jQuery спагетти через MVC (Backbone) к Component Architecture (React) и далее к Server Components. Каждая платформа приходит к **Unidirectional Data Flow** (UDF) как к конвергентному решению проблемы state management.

---

## Зачем это нужно

**Проблема:** Android-разработка сильно изменилась за 15+ лет. Код, написанный "правильно" в 2015, сегодня считается антипаттерном. Без понимания эволюции:
- Работа с legacy-кодом превращается в мучение
- Непонятно, почему рекомендации Google менялись
- Сложно объяснить на собеседовании "почему так, а не иначе"

**Что произошло:**
- **2008-2012:** "God Activity" — вся логика в Activity, AsyncTask для фона
- **2014-2016:** MVP — первое разделение ответственности, но много boilerplate
- **2017-2019:** MVVM + Architecture Components — ViewModel, LiveData, Room
- **2020-2022:** StateFlow/SharedFlow, MVI, Compose
- **2023-2025:** Compose-first, KMP, type-safe navigation

**Результат понимания:** Вы поймёте, почему Google рекомендует MVVM, зачем нужен MVI для сложных экранов, и как правильно мигрировать legacy-код.

### Актуальность 2024-2025: Официальные рекомендации Google

| Компонент | Рекомендация Google | Статус |
|-----------|---------------------|--------|
| Architecture | MVVM с UDF | ✅ Текущий стандарт |
| UI | Jetpack Compose-first | ✅ Приоритет |
| State | StateFlow + SavedStateHandle | ✅ Best Practice |
| DI | Hilt | ✅ Рекомендован |
| Navigation | Type-safe Navigation Compose | 🆕 Новинка 2024 |
| Модуляризация | Feature modules | ✅ Для средних+ проектов |

**Ключевые изменения 2024:**
- **Single-activity architecture** — один Activity как контейнер для Compose/Fragments
- **collectAsStateWithLifecycle()** — обязательно для lifecycle-aware collection
- **Navigation Compose 2.8+** — type-safe routes без строк
- **Kotlin 2.0 + Compose Compiler Plugin** — улучшенная производительность

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **God Activity** | Anti-pattern: Activity содержит всю логику приложения |
| **MVC** | Model-View-Controller — классический паттерн |
| **MVP** | Model-View-Presenter — separation of concerns |
| **MVVM** | Model-View-ViewModel — data binding и reactive |
| **MVI** | Model-View-Intent — unidirectional data flow |
| **UDF** | Unidirectional Data Flow — данные текут в одном направлении |
| **Architecture Components** | Jetpack библиотеки (ViewModel, LiveData, Room) |
| **State Hoisting** | Подъём состояния вверх по иерархии |

---

## Timeline: Эволюция архитектуры (2008-2025)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                  ЭВОЛЮЦИЯ АРХИТЕКТУРЫ ANDROID-ПРИЛОЖЕНИЙ                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  2008-2012: Dark Ages                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • God Activities на 2000+ строк                                    │   │
│  │  • Вся логика в Activity/Fragment                                   │   │
│  │  • AsyncTask для фоновых операций                                   │   │
│  │  • Нет паттернов, нет тестов                                        │   │
│  │  • "Работает — не трогай"                                           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  2014-2016: MVP Era                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • MVP становится стандартом                                        │   │
│  │  • Mosby, Nucleus, другие MVP-библиотеки                           │   │
│  │  • Dagger 2 для DI (2015)                                          │   │
│  │  • RxJava набирает популярность                                     │   │
│  │  • Проблема: boilerplate, lifecycle issues                         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  2017-2019: Architecture Components Revolution                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Google I/O 2017: ViewModel, LiveData, Room                       │   │
│  │  • MVVM становится официальной рекомендацией                        │   │
│  │  • Lifecycle-aware components                                       │   │
│  │  • Navigation Component (2018)                                      │   │
│  │  • Coroutines production-ready (2019)                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  2020-2022: Modern Android                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Jetpack Compose (stable 2021)                                    │   │
│  │  • StateFlow/SharedFlow заменяют LiveData                           │   │
│  │  • MVI для сложных экранов                                          │   │
│  │  • Hilt упрощает DI (2020)                                          │   │
│  │  • Модуляризация как стандарт                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  2023-2025: Modern Compose Era                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Compose-first архитектура                                        │   │
│  │  • Circuit, Decompose, Ballast (MVI библиотеки)                    │   │
│  │  • Kotlin Multiplatform                                             │   │
│  │  • Strong typing для navigation                                     │   │
│  │  • AI-assisted development                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Эра 1: God Activity (2008-2012)

### Как писали код

```kotlin
// ❌ Типичный код 2010 года — всё в одном месте
class MainActivity : Activity() {
    private var users: ArrayList<User> = ArrayList()
    private lateinit var db: SQLiteDatabase

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        db = DatabaseHelper(this).writableDatabase          // БД в Activity
        findViewById<Button>(R.id.loadButton).setOnClickListener { loadUsers() }
    }

    private fun loadUsers() {
        object : AsyncTask<Void, Void, List<User>>() {     // Сеть в Activity
            override fun doInBackground(vararg p: Void?) = parseUsers(URL("..."))
            override fun onPostExecute(result: List<User>) {
                users.addAll(result)
                updateUI()                                   // UI в Activity
                saveToDatabase(result)                       // Persist в Activity
            }
        }.execute()
    }
    // ... saveToDatabase(), 500+ строк, onDestroy() ...
}
```

> [!tip] Подробный разбор MVC на Android и почему God Activity — антипаттерн: [[android-mvc-mvp]]

### Проблемы

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ПРОБЛЕМЫ GOD ACTIVITY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Configuration Change = Катастрофа                                      │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │  Поворот экрана:                                                │    │
│     │  • Activity уничтожается                                        │    │
│     │  • users = ArrayList() — данные потеряны                        │    │
│     │  • AsyncTask продолжает работать                                │    │
│     │  • onPostExecute вызывается на мёртвой Activity                 │    │
│     │  • Crash или утечка памяти                                      │    │
│     └─────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  2. Невозможно тестировать                                                 │
│     • UI, сеть, БД, логика — всё переплетено                              │
│     • Нужен эмулятор для любого теста                                     │
│     • Мокать Context, SQLite — ад                                         │
│                                                                             │
│  3. Дублирование кода                                                      │
│     • loadUsers() копируется в 5 экранов                                  │
│     • saveToDatabase() — в 10                                              │
│     • Баг исправляется в одном месте, забывается в других                 │
│                                                                             │
│  4. Сложность поддержки                                                    │
│     • Activity на 2000 строк                                               │
│     • 50 полей состояния                                                   │
│     • Новый разработчик — неделя на понимание                             │
│                                                                             │
│  5. Memory Leaks                                                            │
│     • AsyncTask держит reference на Activity                              │
│     • Inner class → implicit reference                                     │
│     • Static Handler с Activity context                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Почему так писали

1. **Android был новым** — не было best practices
2. **iOS тоже так писал** — massive UIViewController был нормой
3. **Простота для новичков** — всё в одном месте "понятнее"
4. **Официальные примеры** — Google сам показывал такой код
5. **Маленькие приложения** — работало для 3-5 экранов

---

## Эра 2: MVP (2014-2016)

### Почему MVP

К 2014 году проблемы стали очевидны. Сообщество искало решения. MVP пришёл из desktop/web разработки как способ разделить ответственности.

### Структура MVP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              MVP PATTERN                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐                              ┌─────────────────┐      │
│  │      VIEW       │◄────────────────────────────▶│    PRESENTER    │      │
│  │                 │        View Interface        │                 │      │
│  │  - Activity     │                              │  - Бизнес-логика│      │
│  │  - Fragment     │────────▶ User Actions        │  - Управляет    │      │
│  │  - Пассивная    │                              │    View         │      │
│  │  - Только UI    │◀──────── View Commands       │  - Держит state │      │
│  └─────────────────┘                              └────────┬────────┘      │
│                                                            │               │
│                                                            ▼               │
│                                                   ┌─────────────────┐      │
│                                                   │      MODEL      │      │
│                                                   │                 │      │
│                                                   │  - Repository   │      │
│                                                   │  - API          │      │
│                                                   │  - Database     │      │
│                                                   └─────────────────┘      │
│                                                                             │
│  Ключевые особенности:                                                     │
│  • Presenter ЗНАЕТ о View (через interface)                                │
│  • View ПАССИВНАЯ (не принимает решений)                                  │
│  • Bidirectional: Presenter ↔ View                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Реализация MVP

```kotlin
// Contract — ключевая особенность MVP
interface UsersView {
    fun showLoading()
    fun hideLoading()
    fun showUsers(users: List<User>)
    fun showError(message: String)
}

// Presenter — бизнес-логика отделена от Activity
class UsersPresenter(private val repository: UserRepository) {
    private var view: UsersView? = null

    fun attachView(view: UsersView) { this.view = view }
    fun detachView() { this.view = null }

    fun loadUsers() {
        view?.showLoading()
        repository.getUsers(object : Callback<List<User>> {
            override fun onSuccess(users: List<User>) {
                view?.hideLoading()       // ← null check обязателен
                view?.showUsers(users)
            }
            override fun onError(error: Throwable) {
                view?.hideLoading()
                view?.showError(error.message ?: "Unknown error")
            }
        })
    }
}
// Activity реализует UsersView, вызывает presenter.attachView(this) / detachView()
```

> [!tip] Полный разбор MVP, все библиотеки (Mosby, Moxy, Nucleus) и миграция на MVVM: [[android-mvc-mvp]]

### Проблемы MVP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ПРОБЛЕМЫ MVP                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Lifecycle Hell                                                          │
│     ┌─────────────────────────────────────────────────────────────────┐    │
│     │  • Когда вызывать attachView/detachView?                        │    │
│     │  • Что если callback приходит после detach?                     │    │
│     │  • Configuration change = новая View, старый Presenter          │    │
│     │  • Retained Fragment для Presenter? → Сложность                 │    │
│     └─────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  2. Boilerplate                                                             │
│     • Interface для каждой View                                            │
│     • 10 методов в interface для простого экрана                           │
│     • Дублирование между Presenter'ами                                     │
│                                                                             │
│  3. View Reference в Presenter                                              │
│     • Потенциальные memory leaks                                           │
│     • Null checks везде (view?.showLoading())                              │
│     • Сложнее тестировать (нужно мокать View)                              │
│                                                                             │
│  4. State не сохраняется                                                    │
│     • При process death Presenter теряет state                             │
│     • Нужно заново загружать данные                                        │
│     • onSaveInstanceState в Presenter? → Сложно                            │
│                                                                             │
│  5. Не Reactive                                                             │
│     • Императивный подход (view.showLoading())                             │
│     • Сложно комбинировать данные из разных источников                    │
│     • RxJava добавляет сложность к и так сложному коду                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Эра 3: MVVM и Architecture Components (2017-2019)

### Google I/O 2017: Revolution

Google представил **Architecture Components**:
- **ViewModel** — переживает configuration changes
- **LiveData** — lifecycle-aware observable
- **Room** — type-safe SQLite
- **Lifecycle** — наблюдение за lifecycle

### Почему это изменило всё

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   MVP VS MVVM: КЛЮЧЕВОЕ ОТЛИЧИЕ                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  MVP: Presenter ЗНАЕТ о View                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   Presenter ────────▶ View Interface                               │   │
│  │       │                    │                                        │   │
│  │       │                    ▼                                        │   │
│  │       │              ┌──────────┐                                   │   │
│  │       │              │ Activity │                                   │   │
│  │       └──────────────│          │                                   │   │
│  │                      └──────────┘                                   │   │
│  │                                                                     │   │
│  │   Проблема: Presenter держит reference → lifecycle issues         │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  MVVM: ViewModel НЕ ЗНАЕТ о View                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   ViewModel ────────▶ LiveData/StateFlow (state)                   │   │
│  │       │                      ▲                                      │   │
│  │       │                      │ observes                             │   │
│  │       │              ┌───────┴────┐                                 │   │
│  │       X              │  Activity  │                                 │   │
│  │   (no reference)     │            │                                 │   │
│  │                      └────────────┘                                 │   │
│  │                                                                     │   │
│  │   Решение: ViewModel не знает о View → нет lifecycle issues       │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MVVM реализация (2017 стиль — исторический снимок)

```kotlin
// ViewModel с LiveData — революция 2017 года
class UsersViewModel(private val repository: UserRepository) : ViewModel() {
    private val _isLoading = MutableLiveData<Boolean>()
    val isLoading: LiveData<Boolean> = _isLoading

    private val _users = MutableLiveData<List<User>>()
    val users: LiveData<List<User>> = _users

    fun loadUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            try { _users.value = repository.getUsers() }
            catch (e: Exception) { /* handle error */ }
            finally { _isLoading.value = false }
        }
    }
}
// Activity: viewModel.users.observe(this) { adapter.submitList(it) }
// Нет attachView/detachView, нет onDestroy boilerplate!
```

### Что решили Architecture Components

| Проблема MVP | Решение в MVVM |
|--------------|----------------|
| attachView/detachView | ViewModel автоматически привязан к lifecycle |
| Reference на View | ViewModel не знает о View |
| Configuration change | ViewModel переживает rotation |
| Callback после detach | LiveData lifecycle-aware |
| Boilerplate interfaces | Observe паттерн вместо callbacks |

> [!tip] Три поколения MVVM, UiState паттерны, обработка событий и тестирование: [[android-mvvm-deep-dive]]

---

## Эра 4: MVI и Unidirectional Data Flow (2020-2022)

### Почему MVI

MVVM решил проблемы lifecycle, но создал новые:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ПРОБЛЕМЫ MVVM → ПОЧЕМУ MVI                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Проблема 1: State Update из разных мест                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  class UsersViewModel : ViewModel() {                               │   │
│  │      fun loadUsers() { _state.update { ... } }     // источник 1   │   │
│  │      fun onSearch(q: String) { _state.update { ... } } // источник 2│   │
│  │      fun onFilter(f: Filter) { _state.update { ... } } // источник 3│   │
│  │      fun onRefresh() { _state.update { ... } }     // источник 4   │   │
│  │      fun onDeleteUser(u: User) { _state.update { ... } } // источник 5 │
│  │                                                                     │   │
│  │      // State обновляется из 5 мест → сложно отследить баг         │   │
│  │  }                                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Проблема 2: Race Conditions                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  // Пользователь быстро кликает:                                    │   │
│  │  onSearch("a")       // запускает coroutine 1                       │   │
│  │  onSearch("ab")      // запускает coroutine 2                       │   │
│  │  onSearch("abc")     // запускает coroutine 3                       │   │
│  │                                                                     │   │
│  │  // Coroutines завершаются в неправильном порядке:                 │   │
│  │  // 2, 3, 1 → state содержит результаты для "a", а не "abc"        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Проблема 3: Сложность отладки                                             │
│  • Как state попал в текущее состояние?                                    │
│  • Какие события привели к багу?                                           │
│  • Time-travel debugging невозможен                                        │
│                                                                             │
│  MVI Решение: Одна точка входа (Intent) → одна точка обновления (Reducer)  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MVI Архитектура

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MVI PATTERN                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌───────────────────────────────────┐                   │
│                    │                                   │                   │
│                    ▼                                   │                   │
│  ┌─────────────────────────┐                          │                   │
│  │          VIEW           │                          │                   │
│  │                         │                          │                   │
│  │   Renders State         │──────┐                   │                   │
│  │   Sends Intents         │      │                   │                   │
│  └─────────────────────────┘      │                   │                   │
│              │                    │                   │                   │
│              │ Intent             │                   │                   │
│              ▼                    │                   │                   │
│  ┌─────────────────────────┐      │                   │                   │
│  │       PROCESSOR         │      │ Side              │                   │
│  │                         │      │ Effects           │                   │
│  │   Handles Intents       │──────┘                   │                   │
│  │   Produces Results      │                          │                   │
│  └─────────────────────────┘                          │                   │
│              │                                        │                   │
│              │ Result                                 │                   │
│              ▼                                        │                   │
│  ┌─────────────────────────┐                          │                   │
│  │        REDUCER          │                          │                   │
│  │                         │                          │                   │
│  │   (State, Result) →     │──────────────────────────┘                   │
│  │   New State             │                                              │
│  └─────────────────────────┘                                              │
│                                                                             │
│  Unidirectional: View → Intent → Processor → Result → Reducer → State → View │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MVI реализация

```kotlin
// Intent — все возможные действия пользователя
sealed class UsersIntent {
    object LoadUsers : UsersIntent()
    data class Search(val query: String) : UsersIntent()
    data class DeleteUser(val userId: Long) : UsersIntent()
}

// State — единый объект состояния экрана
data class UsersState(
    val isLoading: Boolean = false,
    val users: List<User> = emptyList(),
    val searchQuery: String = "",
    val error: String? = null
)

// ViewModel — ЕДИНСТВЕННАЯ точка входа для всех действий
class UsersViewModel(private val repository: UserRepository) : ViewModel() {
    private val _state = MutableStateFlow(UsersState())
    val state: StateFlow<UsersState> = _state.asStateFlow()

    fun onIntent(intent: UsersIntent) {
        when (intent) {
            is UsersIntent.LoadUsers -> loadUsers()
            is UsersIntent.Search -> reduce { it.copy(searchQuery = intent.query) }
            is UsersIntent.DeleteUser -> { /* ... */ }
        }
    }

    private fun reduce(reducer: (UsersState) -> UsersState) {
        _state.update(reducer)
    }
}
// View вызывает onIntent(), подписывается на state — однонаправленный поток
```

> [!tip] MVI от ручной реализации до Orbit, MVIKotlin, Ballast — все вариации: [[android-mvi-deep-dive]]

---

## Эра 5: Modern Compose Era (2023-2025)

### Compose меняет архитектуру

```kotlin
// State Hoisting — паттерн Compose
@Composable
fun UsersScreen(
    viewModel: UsersViewModel = viewModel()
) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    UsersContent(
        state = state,
        onEvent = viewModel::onEvent
    )
}

// Stateless composable — легко тестировать
@Composable
fun UsersContent(
    state: UsersState,
    onEvent: (UsersEvent) -> Unit
) {
    // Pure function: same state → same UI
}

// Preview работает без ViewModel
@Preview
@Composable
fun UsersContentPreview() {
    UsersContent(
        state = UsersState(users = listOf(User.mock())),
        onEvent = {}
    )
}
```

### Современные паттерны

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MODERN COMPOSE ARCHITECTURE (2025)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. State Hoisting                                                          │
│     • State живёт в ViewModel                                              │
│     • Composables — stateless functions                                    │
│     • Events поднимаются вверх                                             │
│                                                                             │
│  2. Unidirectional Data Flow                                               │
│     • State flows down                                                     │
│     • Events flow up                                                       │
│     • Single source of truth                                               │
│                                                                             │
│  3. Typed Navigation                                                        │
│     • Type-safe routes                                                     │
│     • Compile-time safety                                                  │
│     • Deep linking встроен                                                 │
│                                                                             │
│  4. Circuit/Decompose/Ballast                                              │
│     • MVI из коробки                                                       │
│     • Navigation интегрирован                                              │
│     • KMP ready                                                            │
│                                                                             │
│  5. Module per Feature                                                      │
│     • :feature:users                                                       │
│     • :feature:profile                                                     │
│     • :core:network, :core:database                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Circuit (Slack) — пример нового подхода

```kotlin
// Screen = контракт: State + Events
@Parcelize
data class UsersScreen : Screen {
    data class State(
        val users: List<User>,
        val isLoading: Boolean,
        val eventSink: (Event) -> Unit   // ← events как часть state
    ) : CircuitUiState

    sealed class Event : CircuitUiEvent {
        data class DeleteUser(val id: Long) : Event()
    }
}

// Presenter — @Composable функция, возвращает State
// UI — @Composable функция, принимает State
// Полное разделение: Presenter тестируется без UI, UI — без логики
```

> [!tip] Circuit, Decompose и Molecule — Compose-native архитектуры в деталях: [[android-compose-architectures]]

---

## Сравнение паттернов

Детальное сравнение всех паттернов (MVC, MVP, MVVM, MVI, Compose-native) по 15+ критериям, decision tree и рекомендации: [[android-architecture-patterns]]

---

## Мифы об эволюции архитектуры

| Миф | Реальность |
|-----|-----------|
| "God Activity — просто плохая практика" | God Activity был нормой до 2017. Architecture Components появились с Android Jetpack. Понимание эволюции помогает рефакторить legacy код |
| "MVP полностью мёртв" | MVP всё ещё используется в legacy проектах. Миграция на MVVM часто не оправдана для стабильного кода. Новые проекты — да, MVVM/MVI лучше |
| "Architecture Components решили все проблемы" | ViewModel не переживает process death (нужен SavedStateHandle). LiveData заменяется на StateFlow. Это был большой шаг, но эволюция продолжается |
| "Каждая новая эра отменяет предыдущую" | Паттерны накапливаются, а не заменяются. MVVM вобрал идеи MVP. MVI добавил UDF поверх MVVM. Compose-native взял лучшее из всех подходов |

> Полный список мифов об архитектурных паттернах: [[android-architecture-patterns#Мифы и заблуждения]]

---

## CS-фундамент эволюции

| CS-концепция | Роль в эволюции архитектуры |
|--------------|-------------------------------|
| **Separation of Concerns** | Главный двигатель: God Activity → MVP → MVVM → разделение ответственности на каждом шаге |
| **Observer Pattern** | От callback hell (MVP) → LiveData (MVVM) → StateFlow (MVI). Каждая эра улучшала подписку на данные |
| **State Machine** | MVI Reducer — pure function: (State, Intent) → State. Кульминация эволюции state management |
| **Layered Architecture** | Presentation → Domain → Data. Постепенное появление слоёв от God Activity к Clean Architecture |
| **Immutability** | От mutable ArrayList в God Activity → data class с val → sealed class State. Эволюция безопасности данных |

> Полная таблица CS-фундамента для архитектурных паттернов: [[android-architecture-patterns#CS-фундамент]]

---

## Связи

- **[[android-architecture-patterns]]** — хаб: сравнение паттернов, decision tree, рекомендации
- **[[android-mvc-mvp]]** — детальный разбор MVC, MVP, библиотеки, миграция
- **[[android-mvvm-deep-dive]]** — три поколения MVVM, UiState, события, тестирование
- **[[android-mvi-deep-dive]]** — MVI: Orbit, MVIKotlin, Ballast, ручная реализация
- **[[android-compose-architectures]]** — Circuit, Decompose, Molecule
- **[[android-viewmodel-internals]]** — как ViewModel переживает rotation
- **[[android-state-management]]** — StateFlow vs SharedFlow vs Channel
- **[[android-activity-lifecycle]]** — понимание lifecycle для архитектуры
- **[[solid-principles]]** — принципы, которые двигали эволюцию
- **[[coupling-cohesion]]** — от tight coupling God Activity к loose coupling MVI

---

## Источники

### Теоретические основы

- **Lehman M. (1980). Programs, Life Cycles, and Laws of Software Evolution.** — Законы эволюции ПО (Law of Increasing Complexity)
- **Dijkstra E. (1974). On the Role of Scientific Thought.** — Separation of Concerns
- **Reenskaug T. (1979). Models-Views-Controllers.** — Оригинальный MVC (Smalltalk-80)
- **Fowler M. (2005). Event Sourcing.** — Основа MVI: state как результат применения событий

### Практические руководства

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Guide to App Architecture](https://developer.android.com/topic/architecture) | Docs | Официальные рекомендации Google |
| 2 | [Architecture Samples](https://github.com/android/architecture-samples) | GitHub | Референсная реализация |
| 3 | [Circuit by Slack](https://slackhq.github.io/circuit/) | Library | Compose-native MVI |
| 4 | [Decompose](https://arkivanov.github.io/Decompose/) | Library | Navigation + MVI для KMP |
| 5 | [Compose UI Architecture](https://developer.android.com/develop/ui/compose/architecture) | Docs | Compose + архитектура |

---

---

## Проверь себя

> [!question]- Почему Android-сообщество пришло к MVVM после MVC и MVP?
> MVC (Activity = God Object): Activity совмещал View и Controller, 3000+ строк кода. MVP: выделил Presenter, но тесная связь через интерфейсы. MVVM: ViewModel не знает о View, lifecycle-aware через LiveData/StateFlow. Каждый шаг -- ответ на проблемы предыдущего подхода. Декларативный UI (Compose) сделал MVVM/MVI естественным выбором.

> [!question]- Сценарий: legacy-проект на MVP. Стоит ли мигрировать на MVVM?
> Зависит от: 1) Активно ли разрабатывается (если maintenance mode -- не трогать). 2) Есть ли проблемы с lifecycle (crashes при rotation). 3) Планируется ли Compose (тогда MVVM/MVI обязателен). Стратегия: новые экраны на MVVM + Compose, существующие мигрировать при рефакторинге. Полная миграция без бизнес-необходимости -- пустая трата.


---

## Ключевые карточки

Какие этапы эволюции архитектуры Android?
?
1) God Activity (2008-2014): всё в Activity. 2) MVP (2014-2017): Presenter + View interface. 3) MVVM + AAC (2017-2021): ViewModel + LiveData. 4) MVI + Compose (2021+): Unidirectional Data Flow + декларативный UI.

Что такое Architecture Components (AAC)?
?
Набор библиотек Google (2017): ViewModel, LiveData, Room, Navigation, Lifecycle. Решили главные проблемы: lifecycle management, data persistence, configuration changes. Стандартизировали архитектуру Android.

Почему God Activity -- антипаттерн?
?
Activity совмещает UI, бизнес-логику, сеть, БД. Проблемы: невозможно тестировать, 3000+ строк, lifecycle баги, невозможно переиспользовать логику. Нарушает Single Responsibility Principle.

Что изменил Compose в архитектуре?
?
1) State hoisting вместо двустороннего binding. 2) UDF стал естественным (state -> composable). 3) Navigation стала type-safe. 4) Screen-level composable = View в MVVM, без Fragment overhead.

Как менялся подход к асинхронности?
?
AsyncTask (2008, deprecated) -> RxJava (2015) -> Coroutines (2018) -> Flow (2019) -> Compose State (2021). Каждый шаг упрощал код и улучшал lifecycle safety.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-architecture-patterns]] | Сравнение всех паттернов, decision tree |
| MVC/MVP | [[android-mvc-mvp]] | Детали MVC, MVP, библиотеки, миграция |
| MVVM | [[android-mvvm-deep-dive]] | Три поколения, UiState, события |
| MVI | [[android-mvi-deep-dive]] | Orbit, MVIKotlin, Ballast |
| Clean Arch | [[android-clean-architecture]] | Слои, Use Cases, Dependency Rule |
| Compose | [[android-compose-architectures]] | Circuit, Decompose, Molecule |
| Навигация | [[android-navigation-evolution]] | Параллельная эволюция навигации |
| Обзор | [[android-overview]] | Вернуться к карте Android |


*Проверено: 2026-01-09 — Педагогический контент проверен*
