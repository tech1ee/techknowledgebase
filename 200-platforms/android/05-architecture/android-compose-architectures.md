---
title: "Compose-Native архитектуры: Circuit, Decompose и Molecule"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
status: published
cs-foundations: [functional-ui, declarative-programming, state-hoisting, component-architecture, unidirectional-data-flow]
tags:
  - topic/android
  - topic/architecture
  - topic/compose
  - type/deep-dive
  - level/advanced
related:
  - "[[android-architecture-patterns]]"
  - "[[android-architecture-evolution]]"
  - "[[android-mvi-deep-dive]]"
  - "[[android-mvvm-deep-dive]]"
  - "[[android-clean-architecture]]"
  - "[[android-compose]]"
  - "[[android-compose-internals]]"
  - "[[android-navigation]]"
  - "[[android-modularization]]"
  - "[[functional-programming]]"
  - "[[observer-pattern]]"
  - "[[state-pattern]]"
  - "[[strategy-pattern]]"
  - "[[decorator-pattern]]"
  - "[[solid-principles]]"
  - "[[coupling-cohesion]]"
  - "[[testing-fundamentals]]"
prerequisites:
  - "[[android-compose]]"
  - "[[android-mvi-deep-dive]]"
  - "[[android-mvvm-deep-dive]]"
reading_time: 40
difficulty: 8
study_status: not_started
mastery: 0
---

# Compose-Native архитектуры: Circuit, Decompose и Molecule

Compose изменил не только UI --- он изменил, где живёт состояние. Три компании (Slack, JetBrains/Arkivanov, Cash App) построили три разных ответа на этот вопрос. Circuit превращает Presenter в `@Composable`-функцию. Decompose строит дерево компонентов с жизненным циклом, независимых от UI-фреймворка. Molecule использует Compose runtime без единого пикселя на экране --- только для production состояния. Все три подхода объединяет идея: **UI = f(state)**, но реализуют её принципиально по-разному.

> **Prerequisites:**
> - [[android-compose]] --- Composable, State, Recomposition, Modifier
> - [[android-mvi-deep-dive]] --- UDF, Intent/State/Effect
> - [[android-mvvm-deep-dive]] --- ViewModel, StateFlow, LiveData

---

## Терминология

| Термин | Значение |
|--------|----------|
| **State Hoisting** | Подъём state в родительский composable: state вверх, events вниз |
| **UDF** | Unidirectional Data Flow --- события идут вверх, состояние течёт вниз |
| **Presenter** | Компонент, производящий UI state из бизнес-логики |
| **Screen** | Единица навигации: связка Presenter + Ui (Circuit) |
| **Component** | Lifecycle-aware бизнес-логика + навигация (Decompose) |
| **ComponentContext** | Контейнер lifecycle/stateKeeper/instanceKeeper/backHandler (Decompose) |
| **Molecule** | Compose runtime без UI --- production StateFlow через recomposition |
| **eventSink** | `(Event) -> Unit` callback в state-объекте (Circuit) |
| **rememberRetained** | Сохранение state через configuration changes без ViewModel (Circuit) |
| **childStack** | Type-safe стек навигации из Component-ов (Decompose) |

---

## Как Compose меняет архитектуру

### Фундаментальный сдвиг

До Compose архитектура строилась вокруг lifecycle: Activity создаётся, Fragment прикрепляется, View инфлейтится. Compose убирает этот слой. Нет Fragment lifecycle hell. Нет `onCreateView` / `onDestroyView` / `onViewStateRestored`. Есть **функции, которые описывают UI по текущему state**.

```
┌──────────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL vs COMPOSE                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  TRADITIONAL:                     COMPOSE:                           │
│                                                                      │
│  Activity                         NavHost                            │
│    └── Fragment                     └── Screen Composable            │
│          ├── onCreateView()               ├── ViewModel / Presenter  │
│          ├── onViewCreated()              └── Content Composable     │
│          ├── onDestroyView()                    ├── state: State     │
│          └── View hierarchy                     └── onEvent: λ      │
│                ├── XML inflate                                       │
│                ├── findViewById                                      │
│                └── Manual binding                                    │
│                                                                      │
│  ПРОБЛЕМЫ:                        РЕШЕНИЯ:                           │
│  - Lifecycle несовпадения         - Нет Fragment lifecycle           │
│  - View state restoration         - State hoisting                   │
│  - Fragment transaction bugs      - Навигация через state            │
│  - Memory leaks на binding        - Автоматическая подписка          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Ключевые принципы

**State hoisting** --- state поднимается вверх, events спускаются вниз. Composable-функция не владеет state, она его получает:

```kotlin
// Stateful — знает про ViewModel
@Composable
fun UsersScreen(viewModel: UsersViewModel = viewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    UsersContent(state = state, onEvent = viewModel::onEvent)
}

// Stateless — чистая функция state → UI
@Composable
fun UsersContent(state: UsersState, onEvent: (UsersEvent) -> Unit) {
    // Same state → same UI. Всегда.
}
```

**Composable = pure function of state**. Один и тот же state всегда даёт одинаковый UI. Это открывает путь к snapshot testing, @Preview без ViewModel, и детерминированному поведению.

**Recomposition как архитектурная основа**. Compose "вызывает" UI заново при изменении state. Не патчит DOM, не мутирует View --- полный ре-рендер (с оптимизациями через Slot Table). Это значит: архитектура должна производить **один иммутабельный state-объект**, а не серию мутаций.

**"Всё --- функция" парадигма**. `@Composable` --- не класс, не интерфейс. Это функция. Presenter --- функция. Ui --- функция. Навигация --- тоже функция. Это сближает Android-архитектуру с [[functional-programming]].

---

## Vanilla подход: ViewModel + Compose

### Google-рекомендованный паттерн

Google рекомендует стандартный подход: ViewModel производит StateFlow, Composable подписывается через `collectAsStateWithLifecycle()`. Stateful Screen делегирует stateless Content:

```kotlin
class TaskListViewModel(private val repository: TaskRepository) : ViewModel() {
    private val _state = MutableStateFlow(TaskListState())
    val state: StateFlow<TaskListState> = _state.asStateFlow()

    fun onEvent(event: TaskListEvent) { /* update _state */ }
}

// Stateful Screen — знает про ViewModel
@Composable
fun TaskListScreen(viewModel: TaskListViewModel = viewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    TaskListContent(state = state, onEvent = viewModel::onEvent)
}

// Stateless Content — pure function, @Preview работает без ViewModel
@Composable
fun TaskListContent(state: TaskListState, onEvent: (TaskListEvent) -> Unit) {
    // Same state → same UI. Всегда.
}
```

### Ограничения Vanilla подхода

| Ограничение | Детали |
|-------------|--------|
| **Android-зависимость** | ViewModel из `androidx.lifecycle` --- не работает в KMP без expect/actual |
| **Тестирование** | Нужен `MainDispatcherRule`, `runTest`, mock ViewModel |
| **Навигация отдельно** | Navigation Component / Type-safe Navigation --- отдельная библиотека |
| **Boilerplate** | ViewModel + State + Event + Screen + Content на каждый экран |
| **State production** | StateFlow с `_state.update {}` --- императивный стиль, не Compose-native |

### Когда Vanilla достаточно

| Критерий | Vanilla ОК | Нужен фреймворк |
|----------|:----------:|:----------------:|
| 1-10 экранов | да | нет |
| Только Android | да | нет |
| KMP / iOS | нет | да (Decompose) |
| Сложная навигация (nested, deep link) | зависит | да |
| Команда знакомится с Compose | да | нет |
| Максимальная тестируемость | частично | да (Circuit, Molecule) |

---

## Circuit (Slack)

### Философия

> "Separate state production from UI rendering. UI is a function of state."

Circuit --- Compose-driven архитектурный фреймворк от Slack. Ключевая идея: **Presenter и Ui не знают друг о друге**. Они общаются исключительно через State и Events. Presenter --- это `@Composable`-функция, которая использует Compose runtime (remember, LaunchedEffect) для управления состоянием, но **не рендерит UI**.

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CIRCUIT ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐                                                   │
│  │    Screen     │ ← @Parcelize data class (navigation key)        │
│  │  (UsersScreen)│ ← Contains: State interface, Event interface    │
│  └──────┬───────┘                                                   │
│         │                                                           │
│    ┌────▼─────┐        State         ┌──────────┐                  │
│    │ Presenter │ ──────────────────► │    Ui    │                  │
│    │ @Composable│                     │ @Composable│                │
│    │ present() │ ◄────────────────── │ render() │                  │
│    └────┬──────┘      eventSink      └──────────┘                  │
│         │                                                           │
│    ┌────▼──────┐                                                    │
│    │ Navigator │ ← goTo(screen), pop(), resetRoot(screen)          │
│    └───────────┘                                                    │
│                                                                     │
│  ПРАВИЛО: Presenter и Ui НИКОГДА не ссылаются друг на друга.       │
│  Единственный канал связи — State (вниз) и eventSink (вверх).      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Screen Definition

Screen --- единица навигации. Это `@Parcelize` data class, содержащий аргументы экрана, а также вложенные интерфейсы State и Event:

```kotlin
@Parcelize
data class TaskDetailScreen(val taskId: Long) : Screen {

    data class State(
        val task: Task?,
        val isLoading: Boolean,
        val eventSink: (Event) -> Unit  // ← ключевой паттерн Circuit
    ) : CircuitUiState

    sealed interface Event : CircuitUiEvent {
        data object ToggleComplete : Event
        data object Delete : Event
        data object NavigateBack : Event
    }
}
```

Обрати внимание: `eventSink` --- это `(Event) -> Unit` callback внутри State. UI вызывает `state.eventSink(Event.Delete)`, а не держит ссылку на Presenter. Это **паттерн Event Sink** --- альтернатива классическому `onEvent: (Event) -> Unit` параметру.

### Presenter

Presenter --- это `@Composable`-функция, которая возвращает State. Она может использовать `remember`, `LaunchedEffect`, `rememberRetained` --- весь Compose runtime, но запрещено вызывать UI-composables (Text, Button и т.д.). Это гарантирует аннотация `@ComposableTarget("presenter")`.

```kotlin
class TaskDetailPresenter @AssistedInject constructor(
    @Assisted private val screen: TaskDetailScreen,
    @Assisted private val navigator: Navigator,
    private val repository: TaskRepository
) : Presenter<TaskDetailScreen.State> {

    @Composable
    override fun present(): TaskDetailScreen.State {
        // Compose runtime для state management
        var task by rememberRetained { mutableStateOf<Task?>(null) }
        var isLoading by remember { mutableStateOf(true) }

        // Side effects через LaunchedEffect
        LaunchedEffect(screen.taskId) {
            task = repository.getTask(screen.taskId)
            isLoading = false
        }

        return TaskDetailScreen.State(
            task = task,
            isLoading = isLoading,
            eventSink = { event ->
                when (event) {
                    TaskDetailScreen.Event.ToggleComplete -> {
                        task?.let { current ->
                            task = current.copy(isCompleted = !current.isCompleted)
                            // Persist in background
                        }
                    }
                    TaskDetailScreen.Event.Delete -> {
                        navigator.pop()
                    }
                    TaskDetailScreen.Event.NavigateBack -> {
                        navigator.pop()
                    }
                }
            }
        )
    }

    @CircuitInject(TaskDetailScreen::class, AppScope::class)
    @AssistedFactory
    fun interface Factory {
        fun create(screen: TaskDetailScreen, navigator: Navigator): TaskDetailPresenter
    }
}
```

**Retention-стратегии:**
- `remember` --- сбрасывается при configuration change
- `rememberRetained` --- переживает rotation/configuration change (аналог ViewModel)
- `rememberSaveable` --- переживает process death

### Ui

Ui --- чистая функция, которая принимает State и рендерит UI. `@CircuitInject` связывает Ui с конкретным Screen:

```kotlin
@CircuitInject(TaskDetailScreen::class, AppScope::class)
@Composable
fun TaskDetailUi(state: TaskDetailScreen.State, modifier: Modifier = Modifier) {
    if (state.isLoading) {
        Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }
    val task = state.task ?: return
    Column(modifier = modifier.padding(16.dp)) {
        Text(text = task.title, style = MaterialTheme.typography.headlineMedium)
        Spacer(modifier = Modifier.height(8.dp))
        Text(text = task.description, style = MaterialTheme.typography.bodyLarge)
        Spacer(modifier = Modifier.height(16.dp))
        Button(onClick = { state.eventSink(TaskDetailScreen.Event.ToggleComplete) }) {
            Text(if (task.isCompleted) "Mark Incomplete" else "Mark Complete")
        }
        OutlinedButton(onClick = { state.eventSink(TaskDetailScreen.Event.Delete) }) {
            Text("Delete")
        }
    }
}
```

### Навигация

Circuit предоставляет встроенную навигацию на основе BackStack:

```kotlin
// Навигация в Presenter
navigator.goTo(TaskDetailScreen(taskId = 42))    // Push экрана
navigator.pop()                                    // Назад
navigator.resetRoot(HomeScreen)                    // Сброс стека

// Настройка в Activity
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val circuit = Circuit.Builder()
            .addPresenterFactories(presenterFactories)  // Dagger-generated
            .addUiFactories(uiFactories)                // Dagger-generated
            .build()

        setContent {
            val backStack = rememberSaveableBackStack(root = HomeScreen)
            val navigator = rememberCircuitNavigator(backStack)

            CircuitCompositionLocals(circuit) {
                NavigableCircuitContent(navigator = navigator, backStack = backStack)
            }
        }
    }
}
```

### DI интеграция

Circuit глубоко интегрирован с Dagger/Hilt через code generation:

```kotlin
// @CircuitInject генерирует:
// 1. Presenter.Factory для DI
// 2. Ui.Factory для DI
// 3. Multibinding в Dagger-граф

@CircuitInject(TaskListScreen::class, AppScope::class)
@Composable
fun TaskListUi(state: TaskListScreen.State, modifier: Modifier = Modifier) { /* ... */ }

// Presenter использует assisted injection
class TaskListPresenter @AssistedInject constructor(
    @Assisted private val navigator: Navigator,
    private val repository: TaskRepository   // ← из Dagger-графа
) : Presenter<TaskListScreen.State> { /* ... */ }
```

### Плюсы и минусы

| Плюсы | Минусы |
|-------|--------|
| Чистое разделение Presenter / Ui | Привязка к Dagger (KSP code gen) |
| Compose-native state management | Меньшее комьюнити, чем ViewModel |
| Встроенная навигация с BackStack | Ментальная модель непривычна после MVVM |
| Отличная тестируемость (FakeNavigator, Turbine) | Eventink в State объекте --- нетипично |
| Proven в production (Slack) | Документация менее обширна, чем Jetpack |
| `rememberRetained` = ViewModel без ViewModel | KMP поддержка развивается |
| Snapshot testing из коробки (state → UI) | |

### Когда выбирать Circuit

| Критерий | Circuit подходит |
|----------|:----------------:|
| Android-first или Android-only проект | да |
| Уже используется Dagger/Hilt | да |
| Максимальная тестируемость Presenter | да |
| Нужна встроенная навигация | да |
| Compose-first команда | да |
| KMP с iOS/Desktop | частично (растёт) |
| Маленький проект (1-5 экранов) | overkill |
| Команда с Koin | требует миграции на Dagger |

---

## Decompose (Arkivanov)

### Философия

> "Lifecycle-aware business logic components with routing and pluggable UI."

Decompose --- KMP-first библиотека от Arkadiy Ivanov. Ключевая идея: **бизнес-логика живёт в Component-дереве с собственным lifecycle**, а UI (Compose, SwiftUI, React) --- подключаемый рендерер. Component знает о lifecycle, но ничего не знает о UI-фреймворке.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DECOMPOSE ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─── RootComponent ───────────────────────────────────────────┐   │
│  │ ComponentContext: lifecycle, stateKeeper, instanceKeeper     │   │
│  │                                                             │   │
│  │  childStack<Config, Child>                                  │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │   │
│  │  │ TaskList     │  │ TaskDetail   │  │ Settings     │     │   │
│  │  │ Component    │  │ Component    │  │ Component    │     │   │
│  │  │              │  │              │  │              │     │   │
│  │  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │     │   │
│  │  │ │StateFlow │ │  │ │StateFlow │ │  │ │StateFlow │ │     │   │
│  │  │ └──────────┘ │  │ └──────────┘ │  │ └──────────┘ │     │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │   │
│  │         │                   │                │             │   │
│  └─────────┼───────────────────┼────────────────┼─────────────┘   │
│            │                   │                │                  │
│    ┌───────▼───────┐  ┌───────▼───────┐ ┌──────▼────────┐        │
│    │ Compose UI    │  │ Compose UI    │ │ SwiftUI       │        │
│    │ (Android)     │  │ (Android)     │ │ (iOS)         │        │
│    └───────────────┘  └───────────────┘ └───────────────┘        │
│                                                                     │
│  ПРАВИЛО: Component не знает о UI-фреймворке. UI подключается.     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### ComponentContext

Каждый Component получает `ComponentContext` --- контейнер с четырьмя ключевыми возможностями:

```kotlin
interface ComponentContext {
    val lifecycle: Lifecycle          // Started, Resumed, Stopped, Destroyed
    val stateKeeper: StateKeeper      // Сохранение state через process death
    val instanceKeeper: InstanceKeeper // Удержание объектов через config changes
    val backHandler: BackHandler       // Обработка системной кнопки "Назад"
}
```

- **lifecycle** --- Component знает, когда он активен (в стеке) или в фоне
- **stateKeeper** --- аналог `SavedStateHandle`: сериализация state через `kotlinx.serialization`
- **instanceKeeper** --- аналог ViewModel: объект переживает configuration change
- **backHandler** --- перехват системного "назад" на уровне Component

### Навигация

Decompose предоставляет type-safe навигацию без строк и Route:

```kotlin
// ── Конфигурация навигации ─────────────────────────────────────────
@Serializable
sealed interface Config {
    @Serializable
    data object TaskList : Config

    @Serializable
    data class TaskDetail(val taskId: Long) : Config

    @Serializable
    data object Settings : Config
}
```

**childStack** --- основная модель навигации (стек экранов):

```kotlin
class RootComponent(
    componentContext: ComponentContext
) : ComponentContext by componentContext {

    private val navigation = StackNavigation<Config>()

    val childStack: Value<ChildStack<Config, Child>> = childStack(
        source = navigation,
        serializer = Config.serializer(),  // Автоматическое сохранение/восстановление
        initialConfiguration = Config.TaskList,
        childFactory = ::createChild
    )

    private fun createChild(config: Config, context: ComponentContext): Child =
        when (config) {
            is Config.TaskList -> Child.TaskList(
                TaskListComponent(
                    componentContext = context,
                    onTaskSelected = { taskId -> navigation.push(Config.TaskDetail(taskId)) },
                    onSettingsClicked = { navigation.push(Config.Settings) }
                )
            )
            is Config.TaskDetail -> Child.TaskDetail(
                TaskDetailComponent(
                    componentContext = context,
                    taskId = config.taskId,
                    onBack = { navigation.pop() }
                )
            )
            is Config.Settings -> Child.Settings(
                SettingsComponent(
                    componentContext = context,
                    onBack = { navigation.pop() }
                )
            )
        }

    sealed interface Child {
        data class TaskList(val component: TaskListComponent) : Child
        data class TaskDetail(val component: TaskDetailComponent) : Child
        data class Settings(val component: SettingsComponent) : Child
    }
}
```

Помимо `childStack`, Decompose предоставляет:
- **childSlot** --- один активный child (диалог, bottom sheet)
- **childPages** --- список страниц с выбранной (ViewPager)
- **childPanels** --- multi-pane layout (master-detail на планшете)

### Полная реализация экрана

```kotlin
// ── Component (бизнес-логика) ──────────────────────────────────────
class TaskListComponent(
    componentContext: ComponentContext,
    private val repository: TaskRepository,
    private val onTaskSelected: (Long) -> Unit
) : ComponentContext by componentContext {

    // instanceKeeper = аналог ViewModel, переживает configuration change
    private val scope = coroutineScope(Dispatchers.Main + SupervisorJob())
    private val _state = MutableValue(TaskListState())
    val state: Value<TaskListState> = _state

    init { lifecycle.doOnStart { refresh() } }

    fun refresh() {
        scope.launch {
            _state.update { it.copy(isLoading = true) }
            val tasks = repository.getTasks()
            _state.update { it.copy(tasks = tasks, isLoading = false) }
        }
    }

    fun onTaskClicked(taskId: Long) = onTaskSelected(taskId)
}

// ── Compose UI (подключаемый рендерер) ─────────────────────────────
@Composable
fun TaskListContent(component: TaskListComponent) {
    val state by component.state.subscribeAsState()
    LazyColumn {
        items(state.tasks) { task ->
            TaskItem(task = task, onClick = { component.onTaskClicked(task.id) })
        }
    }
}
```

### Multi-platform

Тот же Component работает на Android, iOS, Desktop, Web. Component --- pure Kotlin (shared module), UI подключается на каждой платформе:

```kotlin
// Shared: Component одинаков для всех платформ
class TaskListComponent(
    componentContext: ComponentContext,
    private val repository: TaskRepository,     // interface в shared module
    private val onTaskSelected: (Long) -> Unit
) : ComponentContext by componentContext { /* ... */ }

// Android: component.state.subscribeAsState() → Compose UI
// iOS: ObservableValue<State> → SwiftUI View
// Desktop: component.state.subscribeAsState() → Compose Desktop
```

### DI интеграция

Decompose не привязан к DI-фреймворку. Работает с Koin, manual DI или любым DI. Зависимости передаются через конструктор Component --- конструкторный DI без аннотаций и code generation.

### Плюсы и минусы

| Плюсы | Минусы |
|-------|--------|
| True KMP: один Component для всех платформ | Крутая кривая обучения |
| Нет зависимости от Android в бизнес-логике | Verbose setup (ComponentContext, Config, Child) |
| Мощная type-safe навигация | Ручной DI или Koin (нет code gen) |
| Lifecycle-aware из коробки | Больше boilerplate, чем Circuit |
| Зрелая библиотека (production: Badoo, JetBrains) | Value вместо StateFlow (свой API) |
| Pluggable UI: Compose, SwiftUI, React | Component дерево сложно для простых приложений |
| childStack/childSlot/childPages покрывают все сценарии | |

### Когда выбирать Decompose

| Критерий | Decompose подходит |
|----------|:------------------:|
| KMP проект (Android + iOS) | да (основной выбор) |
| Compose Multiplatform (Desktop, Web) | да |
| Сложная навигация (nested stacks, deep links) | да |
| Android-only проект | избыточно |
| Маленький проект | избыточно |
| Команда знает Compose, но не KMP | не сейчас |
| Нужен Hilt/Dagger | неудобно |
| SwiftUI + shared logic | да |

---

## Molecule (Cash App)

### Философия

> "Use Compose runtime WITHOUT UI --- just for state production."

Molecule --- минималистичная библиотека от Cash App. Идея элегантна: **Compose runtime может производить не UI, а данные**. `@Composable`-функция с `remember`, `LaunchedEffect`, `collectAsState` возвращает не UI-дерево, а State-объект. Molecule превращает такую функцию в `StateFlow` или `Flow`.

```
┌─────────────────────────────────────────────────────────────────────┐
│                       MOLECULE ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  @Composable fun Presenter(events: Flow<Event>): State              │
│       │  (remember, LaunchedEffect, collectAsState)                 │
│       ▼                                                             │
│  Molecule Runtime (launchMolecule / moleculeFlow)                   │
│       ▼                                                             │
│  StateFlow<State> ── потребитель: Compose UI / ViewModel / тест     │
│                                                                     │
│  ПРАВИЛО: Molecule не заменяет UI. Он заменяет способ               │
│  production состояния.                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Концепция: Compose runtime без UI

Ключевой инсайт Cash App: Compose compiler и runtime --- это не UI-библиотека. Это система **инкрементального вычисления**. Slot Table, Recomposition, `remember` --- всё это работает с любыми данными, не только с пикселями. Molecule снимает UI-слой и оставляет голый computation engine.

### launchMolecule / moleculeFlow

Два способа запустить Molecule:

```kotlin
// ── launchMolecule: возвращает StateFlow ───────────────────────────
val scope = CoroutineScope(Dispatchers.Main)

val stateFlow: StateFlow<TaskListState> = scope.launchMolecule(
    mode = RecompositionMode.ContextClock  // Синхронизация с UI frame
) {
    TaskListPresenter(events = eventsFlow)
}

// ── moleculeFlow: возвращает Flow (для тестов и non-UI) ────────────
val flow: Flow<TaskListState> = moleculeFlow(
    mode = RecompositionMode.Immediate     // Без frame clock
) {
    TaskListPresenter(events = eventsFlow)
}
```

**RecompositionMode:**
- `ContextClock` --- берёт `MonotonicFrameClock` из CoroutineContext. На Android это `AndroidUiDispatcher.Main`, синхронизированный с frame rate. Для production.
- `Immediate` --- создаёт собственный clock, эмитит при каждом изменении state. Для тестов и background.

### Presenter Pattern

```kotlin
@Composable
fun TaskListPresenter(
    events: Flow<TaskListEvent>,
    repository: TaskRepository
): TaskListState {
    var tasks by remember { mutableStateOf(emptyList<Task>()) }
    var isLoading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    // Загрузка данных
    LaunchedEffect(Unit) {
        try {
            tasks = repository.getTasks()
        } catch (e: Exception) {
            error = e.message
        } finally {
            isLoading = false
        }
    }

    // Обработка событий
    LaunchedEffect(Unit) {
        events.collect { event ->
            when (event) {
                is TaskListEvent.ToggleComplete -> {
                    tasks = tasks.map { task ->
                        if (task.id == event.taskId) task.copy(isCompleted = !task.isCompleted)
                        else task
                    }
                }
                is TaskListEvent.Refresh -> {
                    isLoading = true
                    tasks = repository.getTasks()
                    isLoading = false
                }
                is TaskListEvent.Delete -> {
                    tasks = tasks.filter { it.id != event.taskId }
                }
            }
        }
    }

    return TaskListState(tasks = tasks, isLoading = isLoading, error = error)
}
```

### Интеграция с ViewModel

Molecule часто используется **внутри** ViewModel --- не вместо, а как улучшение state production:

```kotlin
class TaskListViewModel(
    private val repository: TaskRepository
) : ViewModel() {

    private val events = MutableSharedFlow<TaskListEvent>()

    val state: StateFlow<TaskListState> = viewModelScope.launchMolecule(
        mode = RecompositionMode.ContextClock
    ) {
        TaskListPresenter(events = events, repository = repository)
    }

    fun onEvent(event: TaskListEvent) {
        viewModelScope.launch { events.emit(event) }
    }
}
```

Это позволяет использовать Compose runtime для state management, сохраняя привычный ViewModel API для UI-слоя.

### Плюсы и минусы

| Плюсы | Минусы |
|-------|--------|
| Минимальный API (одна функция) | Нет навигации (не фреймворк) |
| Элегантная концепция: Compose = computation | Нишевое применение |
| Compose-native state management | Требует понимания Compose runtime |
| Cash App proven в production | Один --- не заменяет архитектуру |
| Отлично тестируется (moleculeFlow + Turbine) | Нет DI-интеграции |
| Работает с ViewModel и без | Маленькое комьюнити |
| KMP-совместим | |

### Когда выбирать Molecule

| Критерий | Molecule подходит |
|----------|:-----------------:|
| Сложный state с множеством source | да |
| Уже есть ViewModel, хочется Compose-native state | да (внутри ViewModel) |
| Нужен полноценный фреймворк | нет (не фреймворк) |
| Нужна навигация | нет |
| Тестируемый state production | да |
| Понимание Compose runtime в команде | обязательно |
| Прототип / эксперимент | да |

---

## UDF at Scale: паттерны для больших Compose-приложений

### Screen-level ViewModel vs Feature-level Presenter

В больших приложениях выбор между "один ViewModel на экран" и "один Presenter на feature" критичен:

```
┌─────────────────────────────────────────────────────────────────────┐
│              SCREEN-LEVEL vs FEATURE-LEVEL                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  SCREEN-LEVEL (Vanilla):          FEATURE-LEVEL (Circuit):         │
│                                                                     │
│  ProfileScreen                    ProfileScreen                     │
│  └── ProfileViewModel             ├── ProfilePresenter              │
│       ├── loadProfile()           │    └── present(): State         │
│       ├── loadPosts()             ├── ProfileUi(state)              │
│       ├── loadFriends()           │                                 │
│       └── StateFlow<State>        ├── PostListPresenter             │
│                                   │    └── present(): State         │
│  Один ViewModel = God Object     ├── PostListUi(state)             │
│  при росте экрана.                │                                 │
│                                   └── FriendListPresenter           │
│                                        └── present(): State         │
│                                                                     │
│  Каждый Presenter — один feature. Composition, не inheritance.     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Shared state across screens

Три подхода к shared state:

1. **Shared ViewModel** (Vanilla) --- `activityViewModels()` или `navGraphViewModels()`
2. **DI-scoped state** (Circuit) --- state-holder в Dagger-scope, инжектится в Presenter-ы
3. **Parent Component** (Decompose) --- родительский Component хранит state, передаёт children

```kotlin
// Decompose: parent Component управляет shared state
class MainComponent(componentContext: ComponentContext) : ComponentContext by componentContext {

    private val _userSession = MutableValue(UserSession())
    val userSession: Value<UserSession> = _userSession

    // Children получают shared state через конструктор
    private fun createChild(config: Config, context: ComponentContext): Child =
        when (config) {
            Config.Profile -> Child.Profile(
                ProfileComponent(context, userSession = _userSession)
            )
            Config.Settings -> Child.Settings(
                SettingsComponent(context, userSession = _userSession)
            )
        }
}
```

### Module boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│              MODULE STRUCTURE PER FRAMEWORK                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  CIRCUIT:                          DECOMPOSE:                       │
│                                                                     │
│  :feature:tasks                    :shared:feature:tasks            │
│    ├── TaskListScreen.kt             ├── TaskListComponent.kt       │
│    ├── TaskListPresenter.kt          ├── TaskListState.kt           │
│    └── TaskListUi.kt                 └── TaskListEvent.kt           │
│                                                                     │
│  :feature:profile                  :android:feature:tasks           │
│    ├── ProfileScreen.kt               └── TaskListContent.kt        │
│    ├── ProfilePresenter.kt                (Compose UI)              │
│    └── ProfileUi.kt                                                 │
│                                    :ios:feature:tasks               │
│  :core:circuit                       └── TaskListView.swift         │
│    └── Circuit DI setup                   (SwiftUI)                 │
│                                                                     │
│  Всё в одном модуле.              Split: shared logic + platform UI │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Сравнительная таблица

Это ключевая часть файла --- детальное сравнение всех подходов.

| Критерий | Vanilla ViewModel | Circuit (Slack) | Decompose (Arkivanov) | Molecule (Cash App) |
|----------|:-----------------:|:---------------:|:---------------------:|:-------------------:|
| **Тип** | Стандарт Google | Фреймворк | Фреймворк | Библиотека |
| **Парадигма** | MVVM/MVI | Presenter + Ui | Component tree + BLoC | Compose as computation |
| **KMP поддержка** | Нет (androidx) | Растёт | Полная | Да |
| **Навигация** | Отдельно (Navigation Component) | Встроенная (BackStack) | Встроенная (childStack/Slot/Pages) | Нет |
| **DI подход** | Hilt / Koin / Manual | Dagger + @CircuitInject | Koin / Manual | Любой |
| **State management** | StateFlow + update {} | Compose runtime (remember) | Value / StateFlow | Compose runtime → StateFlow |
| **Lifecycle handling** | ViewModel scoping | rememberRetained | ComponentContext.lifecycle | Через CoroutineScope |
| **Тестирование** | MainDispatcherRule + runTest | Presenter.test() + Turbine | DefaultComponentContext | moleculeFlow + Turbine |
| **Compose зависимость** | UI only | Presenter + UI | UI only (Component чист) | Runtime only (без UI) |
| **UI framework lock-in** | Compose only | Compose only | Нет (pluggable) | Нет (production → любой consumer) |
| **Boilerplate** | Средний | Низкий-средний | Высокий | Минимальный |
| **Кривая обучения** | Низкая | Средняя | Высокая | Средняя |
| **Production adoption** | Google, все | Slack | Badoo, JetBrains, Bumble | Cash App |
| **Комьюнити** | Огромное | Растёт | Среднее | Небольшое |
| **Минимальный API level** | 21 | 21 | 21 (Android), KMP targets | 21 |
| **Актуальная версия** | Jetpack Lifecycle 2.8+ | 0.24+ (active dev) | 3.x | 2.2.0 |
| **Документация** | Отличная (d.android.com) | Хорошая (slackhq.github.io) | Хорошая (arkivanov.github.io) | Базовая (README + blog) |
| **Миграция с ViewModel** | N/A | Средняя сложность | Высокая сложность | Минимальная (внутри VM) |
| **Snapshot testing** | Требует setup | Из коробки (state → UI) | Compose UI часть | N/A |
| **Process death** | SavedStateHandle | rememberSaveable | stateKeeper + serialization | Через ViewModel |
| **Nested navigation** | NavHost вложение | BackStack + goTo | childStack в childStack | N/A |
| **Deep linking** | Встроен (Navigation) | Ручная настройка | Config → deep link mapping | N/A |

---

## Миграция с ViewModel

### ViewModel → Circuit Presenter (4 шага)

1. **Создать Screen** с State (CircuitUiState) + Event (CircuitUiEvent) + eventSink
2. **Конвертировать ViewModel → Presenter**: `viewModelScope.launch` → `LaunchedEffect`, `_state.update` → `remember`/`rememberRetained` + прямое присваивание
3. **Извлечь Ui**: Screen Composable → `@CircuitInject` Composable с `state: State` параметром
4. **Навигация**: `NavController.navigate()` → `navigator.goTo(Screen)`

```kotlin
// БЫЛО: ViewModel
class TaskListViewModel(private val repo: TaskRepository) : ViewModel() {
    private val _state = MutableStateFlow(TaskListState())
    val state = _state.asStateFlow()
    fun onRefresh() { viewModelScope.launch { /* update _state */ } }
}

// СТАЛО: Circuit Presenter
class TaskListPresenter @AssistedInject constructor(
    @Assisted private val navigator: Navigator,
    private val repo: TaskRepository
) : Presenter<TaskListScreen.State> {
    @Composable override fun present(): TaskListScreen.State {
        var tasks by rememberRetained { mutableStateOf(emptyList<Task>()) }
        var isLoading by remember { mutableStateOf(true) }
        LaunchedEffect(Unit) { tasks = repo.getTasks(); isLoading = false }
        return TaskListScreen.State(tasks, isLoading) { event -> /* handle */ }
    }
}
```

### ViewModel → Decompose Component (4 шага)

1. **Создать Component** с `ComponentContext by componentContext` и конструкторным DI
2. **Перенести логику**: `viewModelScope` → `coroutineScope()` (Decompose extension), `StateFlow` → `Value`
3. **Навигация через callback**: `onTaskSelected: (Long) -> Unit` в конструкторе
4. **RootComponent**: все Screen → `@Serializable Config`, все NavHost → `childStack`

### Gradual Migration

Circuit и ViewModel сосуществуют: новые экраны на Circuit, старые на ViewModel. Кастомный `Ui.Factory` делегирует legacy экранам. Molecule можно использовать внутри ViewModel без изменения внешнего API.

### Decision Framework: мигрировать или остаться?

| Ситуация | Рекомендация |
|----------|--------------|
| Новый проект, Android-only, Dagger | Circuit |
| Новый проект, KMP (Android + iOS) | Decompose |
| Существующий проект, довольны ViewModel | Оставаться + рассмотреть Molecule |
| Существующий проект, проблемы с тестированием | Circuit (постепенно) |
| Существующий проект, планируется iOS | Decompose (с нуля или постепенно) |
| Хочется Compose-native state, но не менять архитектуру | Molecule внутри ViewModel |

---

## Тестирование Compose архитектур

### Circuit: Presenter Test

```kotlin
@Test
fun `loading state then tasks loaded`() = runTest {
    val repository = FakeTaskRepository(
        tasks = listOf(Task(id = 1, title = "Test", isCompleted = false))
    )
    val presenter = TaskListPresenter(
        navigator = FakeNavigator(TaskListScreen),
        repository = repository
    )

    presenter.test {
        // Начальное состояние
        val loading = awaitItem()
        assertTrue(loading.isLoading)
        assertTrue(loading.tasks.isEmpty())

        // После загрузки
        val loaded = awaitItem()
        assertFalse(loaded.isLoading)
        assertEquals(1, loaded.tasks.size)
        assertEquals("Test", loaded.tasks.first().title)

        // Тестирование event
        loaded.eventSink(TaskListScreen.Event.Refresh)
        val refreshing = awaitItem()
        assertTrue(refreshing.isLoading)
    }
}
```

`Presenter.test {}` под капотом использует Molecule + Turbine. `FakeNavigator` записывает все вызовы `goTo()` / `pop()`.

### Decompose: Component Test

```kotlin
@Test
fun `component loads tasks on start`() {
    val repository = FakeTaskRepository(
        tasks = listOf(Task(id = 1, title = "Test", isCompleted = false))
    )
    val navigatedIds = mutableListOf<Long>()

    val component = TaskListComponent(
        componentContext = DefaultComponentContext(LifecycleRegistry()),
        repository = repository,
        onTaskSelected = { navigatedIds.add(it) }
    )

    // Проверяем state
    val state = component.state.value
    assertEquals(1, state.tasks.size)

    // Проверяем навигацию
    component.onTaskClicked(taskId = 1)
    assertEquals(1L, navigatedIds.first())
}
```

`DefaultComponentContext` --- test-friendly реализация. Не нужен Android framework.

### Molecule: Presenter Test

```kotlin
@Test
fun `presenter produces correct states`() = runTest {
    val events = MutableSharedFlow<TaskListEvent>()
    val repository = FakeTaskRepository(
        tasks = listOf(Task(id = 1, title = "Test", isCompleted = false))
    )

    moleculeFlow(RecompositionMode.Immediate) {
        TaskListPresenter(events = events, repository = repository)
    }.test {
        // Начальное состояние: loading
        val loading = awaitItem()
        assertTrue(loading.isLoading)

        // После загрузки
        val loaded = awaitItem()
        assertFalse(loaded.isLoading)
        assertEquals(1, loaded.tasks.size)

        // Отправка события
        events.emit(TaskListEvent.Delete(taskId = 1))
        val afterDelete = awaitItem()
        assertTrue(afterDelete.tasks.isEmpty())
    }
}
```

`moleculeFlow(Immediate)` + Turbine `.test {}` --- стандартная комбинация для тестирования Molecule-презентеров.

### Compose UI Testing (общее для всех)

```kotlin
@get:Rule
val composeTestRule = createComposeRule()

@Test
fun `task list displays items`() {
    val state = TaskListScreen.State(
        tasks = listOf(Task(id = 1, title = "Buy groceries", isCompleted = false)),
        isLoading = false,
        eventSink = {}
    )

    composeTestRule.setContent {
        TaskListUi(state = state)
    }

    composeTestRule.onNodeWithText("Buy groceries").assertIsDisplayed()
}
```

Все три подхода выигрывают от stateless Composable: передаёшь state --- проверяешь UI. Не нужен ViewModel, Repository, DI.

---

## Мифы и заблуждения

### Миф 1: "Compose требует MVI"

**Реальность:** Compose работает с любой архитектурой. MVVM + StateFlow + Compose --- самый популярный паттерн. MVI --- опция для сложного state, не обязательное условие. Google официально рекомендует ViewModel + StateFlow, а не MVI.

### Миф 2: "ViewModel больше не нужен"

**Реальность:** ViewModel остаётся рекомендацией Google. Он решает конкретную проблему: сохранение state через configuration change и scoping к NavBackStackEntry. Circuit заменяет его через `rememberRetained`, Decompose --- через `instanceKeeper`, но это **альтернативы**, а не доказательство ненужности ViewModel.

### Миф 3: "Circuit = MVI"

**Реальность:** Circuit --- это presentation-layer фреймворк с паттерном Presenter + Ui. Он не навязывает MVI. Presenter может использовать любой подход к state management: один `remember`, `rememberRetained`, или полноценный MVI с Reducer. eventSink --- не то же самое, что Intent в MVI.

### Миф 4: "Decompose слишком сложный"

**Реальность:** Decompose сложен для простых приложений --- это правда. Но для KMP-проекта с 3+ платформами его complexity оправдана. ComponentContext, childStack, Config --- это инфраструктура, которую настраиваешь один раз. После этого добавление нового экрана --- 1 Component + 1 Config + 1 Compose UI.

### Миф 5: "Molecule заменяет ViewModel"

**Реальность:** Molecule **дополняет**, не заменяет. Самый частый паттерн --- Molecule *внутри* ViewModel. Molecule --- это способ production состояния через Compose runtime. ViewModel --- это lifecycle-aware контейнер. Они решают разные задачи и отлично работают вместе.

### Миф 6: "Эти фреймворки не production-ready"

**Реальность:** Circuit используется в Slack (миллионы пользователей). Decompose --- в Badoo/Bumble (сотни миллионов пользователей), JetBrains Toolbox. Molecule --- в Cash App. Все три --- battle-tested в масштабных production-приложениях.

---

## CS-фундамент

| CS-концепция | Проявление в Compose-архитектурах |
|-------------|-----------------------------------|
| **Functional UI** | Composable = pure function: `(State) -> UI`. Circuit Ui, Decompose Compose Content, vanilla Content --- все следуют этому принципу |
| **Declarative Programming** | Описание "что" показать (State), а не "как" обновить (imperative View mutation). Recomposition автоматически синхронизирует UI с State |
| **State Hoisting** | State поднимается в Presenter/Component/ViewModel, Composable получает его как параметр. Ключевой паттерн всех подходов |
| **Component Architecture** | Decompose буквально: Component tree с lifecycle, parent-child, navigation. Circuit: Screen как component boundary |
| **Unidirectional Data Flow** | State flows down, Events flow up. Circuit eventSink, Decompose onEvent callback, ViewModel onEvent --- один паттерн |
| **Separation of Concerns** | Circuit: Presenter ≠ Ui (нет ссылок). Decompose: Component ≠ UI (pluggable). Molecule: State production ≠ consumption |
| **Dependency Inversion** | Circuit: @CircuitInject + Dagger. Decompose: конструктор Component. Molecule: функция-параметр. Все зависят от абстракций |
| **Incremental Computation** | Compose runtime (Slot Table + Recomposition) = инкрементальное вычисление. Molecule эксплуатирует это для state production |
| **Tree-structured Lifecycle** | Decompose Component tree: parent lifecycle управляет children. Compose Composition tree: parent recomposition вызывает children |
| **Strategy Pattern** | Pluggable Presenter (Circuit), pluggable UI renderer (Decompose), pluggable state producer (Molecule) --- взаимозаменяемые стратегии |

---

## Связь с другими темами

**[[functional-programming]]** --- Compose = функциональный UI. `@Composable` --- чистая функция, State immutable, side effects изолированы. Circuit Presenter возвращает State, Molecule --- computation engine. Все три подхода: composition over inheritance, immutability over mutation.

**[[observer-pattern]]** --- Наблюдение за state --- основа: Vanilla (`StateFlow` + `collectAsStateWithLifecycle`), Decompose (`Value` + `subscribeAsState`), Molecule (production `StateFlow`), Circuit (Compose runtime `mutableStateOf`). Четыре реализации Observer, один принцип.

**[[state-pattern]]** --- `sealed interface UiState` во всех подходах. `CircuitUiState`, State data class (Decompose), return type Molecule presenter. Compile-time exhaustive `when` гарантирует обработку всех состояний.

**[[strategy-pattern]]** --- Pluggable Presenter (Circuit DI factory), pluggable UI renderer (Decompose: Compose/SwiftUI), pluggable state producer (Molecule function parameter). Взаимозаменяемые стратегии = тестируемость.

**[[decorator-pattern]]** --- Modifier chain = каноничный Decorator. Circuit Overlay для dialog/sheet. Decompose ComponentContext через `by` delegation.

**[[solid-principles]]** --- SRP: Presenter ≠ Ui (Circuit), Component ≠ UI (Decompose). OCP: новый Screen = новый Presenter + Ui. DIP: зависимости от абстракций (`Presenter<State>`, `ComponentContext`).

**[[coupling-cohesion]]** --- Circuit: low coupling через State/Event интерфейсы. Decompose: high cohesion --- Component = вся логика feature. Модульная структура естественна для обоих.

**[[android-mvi-deep-dive]]** --- Circuit и Decompose можно рассматривать как MVI: Event = Intent, State = State, eventSink = Side Effect. Но оба шире MVI: навигация, lifecycle, KMP.

**[[android-mvvm-deep-dive]]** --- Миграция: ViewModel + StateFlow → Circuit Presenter + rememberRetained. ViewModel + Navigation → Decompose Component + childStack. Molecule работает внутри ViewModel.

**[[android-modularization]]** --- Circuit: один module = один feature (Screen + Presenter + Ui). Decompose: shared module (Component) + platform modules. Чёткие module boundaries.

**[[android-compose]]** --- Все три фреймворка построены на Compose runtime. Recomposition, Slot Table, State snapshot --- необходимо для Circuit Presenter и Molecule.

---

## Источники

| Источник | Описание | URL |
|----------|----------|-----|
| **Circuit Documentation** | Официальная документация фреймворка | [slackhq.github.io/circuit](https://slackhq.github.io/circuit/) |
| **Circuit GitHub** | Исходный код, примеры, changelog | [github.com/slackhq/circuit](https://github.com/slackhq/circuit) |
| **Decompose Documentation** | Официальная документация, guides | [arkivanov.github.io/Decompose](https://arkivanov.github.io/Decompose/) |
| **Decompose GitHub** | Исходный код, samples, releases | [github.com/arkivanov/Decompose](https://github.com/arkivanov/Decompose) |
| **Molecule GitHub** | Исходный код, README, API docs | [github.com/cashapp/molecule](https://github.com/cashapp/molecule) |
| **Molecule Blog Post** | "The state of managing state (with Compose)" от Cash App | [code.cash.app/the-state-of-managing-state-with-compose](https://code.cash.app/the-state-of-managing-state-with-compose) |
| **Molecule 1.0 Announcement** | Стабильный мультиплатформенный релиз | [code.cash.app/molecule-1-0](https://code.cash.app/molecule-1-0) |
| **Google Compose Architecture** | Официальный guide по архитектуре Compose | [developer.android.com/develop/ui/compose/architecture](https://developer.android.com/develop/ui/compose/architecture) |
| **Modern Compose Architecture with Circuit** | Доклад Zac Sweers (Slack) | [speakerdeck.com/zacsweers](https://speakerdeck.com/zacsweers/modern-compose-architecture-with-circuit) |
| **Circuit vs ViewModel Analysis** | Сравнительный анализ подходов | [medium.com/@keisardev](https://medium.com/@keisardev/circuit-vs-jetpack-compose-viewmodel-in-depth-analysis-d3c8f4d02cc1) |

---

## Проверь себя

<details>
<summary>1. Чем Circuit Presenter отличается от обычного ViewModel? Какую проблему решает eventSink?</summary>

Presenter --- `@Composable`-функция, возвращающая State напрямую (не через StateFlow). Использует `rememberRetained` вместо ViewModel scoping. Не может рендерить UI (`@ComposableTarget("presenter")`). **eventSink** (`(Event) -> Unit` внутри State) --- Ui не знает о Presenter, не держит ссылку. Единственный канал --- callback в State-объекте. Упрощает тестирование и snapshot testing.

</details>

<details>
<summary>2. Почему Decompose лучше подходит для KMP, чем Circuit и ViewModel?</summary>

Decompose --- единственный, где бизнес-логика отделена от UI-фреймворка: Component = pure Kotlin (ComponentContext, Value, StackNavigation). Навигация через `@Serializable` Config (без Parcelable). Lifecycle от Essenty (не Android). stateKeeper через kotlinx.serialization (не Bundle). Circuit привязан к Compose runtime, ViewModel --- к `androidx.lifecycle`.

</details>

<details>
<summary>3. Molecule внутри ViewModel vs самостоятельно? ContextClock vs Immediate?</summary>

**Внутри ViewModel** --- Compose-native state + привычный ViewModel API. **Самостоятельно** --- KMP shared module, background, тесты. **ContextClock** --- берёт MonotonicFrameClock, recomposition раз в frame (production). **Immediate** --- свой clock, эмитит сразу при изменении (тесты, background).

</details>

---

## Ключевые карточки

**Q:** Что такое Circuit eventSink pattern?
**A:** `eventSink: (Event) -> Unit` --- callback внутри State-объекта. Ui вызывает `state.eventSink(Event.Refresh)` для отправки событий Presenter-у. Presenter и Ui не знают друг о друге --- только State и eventSink.

---

**Q:** Какие три retention-стратегии есть в Circuit?
**A:** `remember` --- переживает recomposition. `rememberRetained` --- переживает configuration change (аналог ViewModel). `rememberSaveable` --- переживает process death (аналог SavedStateHandle).

---

**Q:** Четыре составляющих ComponentContext в Decompose?
**A:** `lifecycle` (Started/Resumed/Stopped/Destroyed), `stateKeeper` (сохранение state через process death), `instanceKeeper` (удержание объектов через config change, аналог ViewModel), `backHandler` (перехват системного "назад").

---

**Q:** Чем moleculeFlow отличается от launchMolecule?
**A:** `launchMolecule` запускает в CoroutineScope и возвращает `StateFlow` (hot). `moleculeFlow` возвращает cold `Flow` без привязки к scope. Для production --- `launchMolecule` с `ContextClock`. Для тестов --- `moleculeFlow` с `Immediate`.

---

**Q:** Какой фреймворк выбрать для KMP (Android + iOS)?
**A:** Decompose. Component --- pure Kotlin, не зависит от UI. childStack навигация через @Serializable Config. Один Component --- Compose на Android, SwiftUI на iOS. Circuit и ViewModel привязаны к Compose runtime / Android framework.

---

**Q:** Можно ли использовать Circuit и ViewModel в одном приложении?
**A:** Да. Gradual migration: новые экраны на Circuit, старые на ViewModel. CircuitContent и NavHost могут сосуществовать. Кастомный Ui.Factory делегирует legacy экранам. Molecule можно использовать внутри существующих ViewModel без изменения архитектуры.

---

## Куда дальше

| Направление | Файл | Зачем |
|-------------|------|-------|
| Compose основы | [[android-compose]] | State, Recomposition, Modifier --- фундамент для всех фреймворков |
| Compose internals | [[android-compose-internals]] | Slot Table, Recomposition engine --- как работает runtime |
| MVI паттерн | [[android-mvi-deep-dive]] | Базовый UDF паттерн, на котором построены Circuit и Decompose |
| MVVM паттерн | [[android-mvvm-deep-dive]] | Vanilla подход, от которого мигрируют |
| Модуляризация | [[android-modularization]] | Как организовать module-per-feature с Circuit/Decompose |
| Навигация | [[android-navigation]] | Jetpack Navigation для сравнения с Circuit/Decompose навигацией |
| Clean Architecture | [[android-clean-architecture]] | Domain/Data слои --- общие для всех presentation-фреймворков |
| Functional Programming | [[functional-programming]] | Теоретическая основа: pure functions, composition, immutability |
| Архитектурная эволюция | [[android-architecture-evolution]] | Контекст: как Android пришёл от MVC к Compose-native архитектурам |
