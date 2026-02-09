---
title: "Cross-Platform: State Management — @State vs StateFlow"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - state
  - swiftui
  - compose
  - type/comparison
  - level/intermediate
---

# Cross-Platform State Management: SwiftUI vs Jetpack Compose

## TL;DR

| Аспект | SwiftUI | Jetpack Compose |
|--------|---------|-----------------|
| **Локальное состояние** | `@State` | `remember { mutableStateOf() }` |
| **Объект состояния** | `@StateObject` | `remember { ViewModel() }` |
| **Наблюдаемые свойства** | `@Published` | `MutableStateFlow` |
| **Передача состояния** | `@Binding` | Параметр + callback |
| **Внедрение зависимостей** | `@EnvironmentObject` | `CompositionLocal` |
| **Реактивные потоки** | Combine (`Publisher`) | Kotlin Flow (`StateFlow`) |
| **Подписка на поток** | `.onReceive()` | `collectAsState()` |
| **Время жизни** | Привязано к View | Привязано к Composition |
| **Сравнение значений** | `Equatable` | `equals()` / Structural |
| **Thread-safety** | MainActor | `Dispatchers.Main` |

---

## 1. State Wrappers: Локальное состояние

### SwiftUI: @State

```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Счётчик: \(count)")
            Button("Увеличить") {
                count += 1
            }
        }
    }
}
```

### Compose: remember + mutableStateOf

```kotlin
@Composable
fun CounterView() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Счётчик: $count")
        Button(onClick = { count++ }) {
            Text("Увеличить")
        }
    }
}
```

**Ключевые различия:**
- SwiftUI: `@State` — property wrapper, управляется фреймворком
- Compose: `remember` сохраняет значение между рекомпозициями
- SwiftUI: значение хранится вне View struct
- Compose: `by` делегат обеспечивает удобный синтаксис

---

## 2. State Wrappers: Объекты состояния

### SwiftUI: @StateObject + @Published

```swift
class UserViewModel: ObservableObject {
    @Published var name: String = ""
    @Published var email: String = ""
    @Published var isLoading: Bool = false

    func loadUser() async {
        isLoading = true
        defer { isLoading = false }

        // Загрузка данных...
        name = "Иван"
        email = "ivan@example.com"
    }
}

struct UserProfileView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
            } else {
                Text(viewModel.name)
                Text(viewModel.email)
            }
        }
        .task {
            await viewModel.loadUser()
        }
    }
}
```

### Compose: ViewModel + StateFlow

```kotlin
class UserViewModel : ViewModel() {
    private val _name = MutableStateFlow("")
    val name: StateFlow<String> = _name.asStateFlow()

    private val _email = MutableStateFlow("")
    val email: StateFlow<String> = _email.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun loadUser() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                // Загрузка данных...
                _name.value = "Иван"
                _email.value = "ivan@example.com"
            } finally {
                _isLoading.value = false
            }
        }
    }
}

@Composable
fun UserProfileView(
    viewModel: UserViewModel = viewModel()
) {
    val name by viewModel.name.collectAsState()
    val email by viewModel.email.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    Column {
        if (isLoading) {
            CircularProgressIndicator()
        } else {
            Text(name)
            Text(email)
        }
    }

    LaunchedEffect(Unit) {
        viewModel.loadUser()
    }
}
```

**Ключевые различия:**
- SwiftUI: `@StateObject` создаёт и владеет объектом
- Compose: `viewModel()` получает из ViewModelStore
- SwiftUI: `@Published` автоматически уведомляет
- Compose: `StateFlow` + `collectAsState()` для подписки

---

## 3. State Wrappers: Передача состояния вниз

### SwiftUI: @Binding

```swift
struct ParentView: View {
    @State private var text = ""

    var body: some View {
        ChildView(text: $text)
    }
}

struct ChildView: View {
    @Binding var text: String

    var body: some View {
        TextField("Введите текст", text: $text)
    }
}
```

### Compose: State hoisting

```kotlin
@Composable
fun ParentView() {
    var text by remember { mutableStateOf("") }

    ChildView(
        text = text,
        onTextChange = { text = it }
    )
}

@Composable
fun ChildView(
    text: String,
    onTextChange: (String) -> Unit
) {
    TextField(
        value = text,
        onValueChange = onTextChange,
        label = { Text("Введите текст") }
    )
}
```

**Ключевые различия:**
- SwiftUI: `@Binding` — двусторонняя связь через property wrapper
- Compose: явная передача значения и callback (state hoisting)
- SwiftUI: `$` создаёт Binding из State
- Compose: более явный, но verbose подход

---

## 4. Reactive Streams: Combine vs Flow

### SwiftUI + Combine

```swift
class SearchViewModel: ObservableObject {
    @Published var query: String = ""
    @Published var results: [String] = []

    private var cancellables = Set<AnyCancellable>()

    init() {
        $query
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .flatMap { query in
                self.search(query)
                    .catch { _ in Just([]) }
            }
            .receive(on: RunLoop.main)
            .assign(to: &$results)
    }

    private func search(_ query: String) -> AnyPublisher<[String], Error> {
        // API вызов
        Future { promise in
            // Имитация поиска
            DispatchQueue.global().asyncAfter(deadline: .now() + 0.5) {
                promise(.success(["Результат 1", "Результат 2"]))
            }
        }
        .eraseToAnyPublisher()
    }
}

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()

    var body: some View {
        VStack {
            TextField("Поиск", text: $viewModel.query)

            List(viewModel.results, id: \.self) { result in
                Text(result)
            }
        }
    }
}
```

### Compose + Kotlin Flow

```kotlin
class SearchViewModel : ViewModel() {
    private val _query = MutableStateFlow("")
    val query: StateFlow<String> = _query.asStateFlow()

    val results: StateFlow<List<String>> = _query
        .debounce(300)
        .distinctUntilChanged()
        .filter { it.isNotEmpty() }
        .flatMapLatest { query ->
            search(query).catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun updateQuery(newQuery: String) {
        _query.value = newQuery
    }

    private fun search(query: String): Flow<List<String>> = flow {
        delay(500)
        emit(listOf("Результат 1", "Результат 2"))
    }
}

@Composable
fun SearchView(
    viewModel: SearchViewModel = viewModel()
) {
    val query by viewModel.query.collectAsState()
    val results by viewModel.results.collectAsState()

    Column {
        TextField(
            value = query,
            onValueChange = viewModel::updateQuery,
            label = { Text("Поиск") }
        )

        LazyColumn {
            items(results) { result ->
                Text(result)
            }
        }
    }
}
```

### Сравнение операторов

| Операция | Combine | Kotlin Flow |
|----------|---------|-------------|
| Задержка | `debounce(for:scheduler:)` | `debounce(timeMillis)` |
| Уникальные | `removeDuplicates()` | `distinctUntilChanged()` |
| Фильтр | `filter { }` | `filter { }` |
| Трансформация | `map { }` | `map { }` |
| Flat map | `flatMap { }` | `flatMapLatest { }` |
| Обработка ошибок | `catch { }` | `catch { }` |
| Поток | `receive(on:)` | `flowOn()` |
| Подписка | `sink { }` / `assign(to:)` | `collect { }` / `collectAsState()` |

---

## 5. Unidirectional Data Flow (UDF)

### SwiftUI: TCA-inspired architecture

```swift
// State
struct AppState: Equatable {
    var counter: Int = 0
    var isLoading: Bool = false
    var error: String?
}

// Action
enum AppAction {
    case increment
    case decrement
    case loadData
    case dataLoaded(Result<Int, Error>)
}

// Reducer
func appReducer(state: inout AppState, action: AppAction) -> Effect<AppAction> {
    switch action {
    case .increment:
        state.counter += 1
        return .none

    case .decrement:
        state.counter -= 1
        return .none

    case .loadData:
        state.isLoading = true
        return .run { send in
            do {
                let value = try await fetchData()
                await send(.dataLoaded(.success(value)))
            } catch {
                await send(.dataLoaded(.failure(error)))
            }
        }

    case .dataLoaded(let result):
        state.isLoading = false
        switch result {
        case .success(let value):
            state.counter = value
        case .failure(let error):
            state.error = error.localizedDescription
        }
        return .none
    }
}

// Store
@MainActor
class Store<State, Action>: ObservableObject {
    @Published private(set) var state: State
    private let reducer: (inout State, Action) -> Effect<Action>

    init(
        initialState: State,
        reducer: @escaping (inout State, Action) -> Effect<Action>
    ) {
        self.state = initialState
        self.reducer = reducer
    }

    func send(_ action: Action) {
        let effect = reducer(&state, action)
        // Обработка эффектов...
    }
}

// View
struct CounterView: View {
    @ObservedObject var store: Store<AppState, AppAction>

    var body: some View {
        VStack {
            Text("Счётчик: \(store.state.counter)")

            HStack {
                Button("-") { store.send(.decrement) }
                Button("+") { store.send(.increment) }
            }

            if store.state.isLoading {
                ProgressView()
            }
        }
    }
}
```

### Compose: MVI architecture

```kotlin
// State
data class AppState(
    val counter: Int = 0,
    val isLoading: Boolean = false,
    val error: String? = null
)

// Intent (Action)
sealed class AppIntent {
    object Increment : AppIntent()
    object Decrement : AppIntent()
    object LoadData : AppIntent()
}

// Side Effect
sealed class AppEffect {
    data class ShowError(val message: String) : AppEffect()
}

// ViewModel с MVI
class AppViewModel : ViewModel() {
    private val _state = MutableStateFlow(AppState())
    val state: StateFlow<AppState> = _state.asStateFlow()

    private val _effect = Channel<AppEffect>()
    val effect: Flow<AppEffect> = _effect.receiveAsFlow()

    fun processIntent(intent: AppIntent) {
        when (intent) {
            is AppIntent.Increment -> {
                _state.update { it.copy(counter = it.counter + 1) }
            }
            is AppIntent.Decrement -> {
                _state.update { it.copy(counter = it.counter - 1) }
            }
            is AppIntent.LoadData -> loadData()
        }
    }

    private fun loadData() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val value = fetchData()
                _state.update { it.copy(counter = value, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(isLoading = false, error = e.message) }
                _effect.send(AppEffect.ShowError(e.message ?: "Ошибка"))
            }
        }
    }
}

// Composable
@Composable
fun CounterScreen(
    viewModel: AppViewModel = viewModel()
) {
    val state by viewModel.state.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.effect.collect { effect ->
            when (effect) {
                is AppEffect.ShowError -> {
                    // Показать Snackbar
                }
            }
        }
    }

    Column {
        Text("Счётчик: ${state.counter}")

        Row {
            Button(onClick = { viewModel.processIntent(AppIntent.Decrement) }) {
                Text("-")
            }
            Button(onClick = { viewModel.processIntent(AppIntent.Increment) }) {
                Text("+")
            }
        }

        if (state.isLoading) {
            CircularProgressIndicator()
        }
    }
}
```

---

## 6. KMP State Sharing: expect/actual

### Общий модуль (commonMain)

```kotlin
// commonMain/kotlin/SharedState.kt

// Expect класс для платформенной реализации
expect class PlatformDispatcher() {
    val main: CoroutineDispatcher
    val io: CoroutineDispatcher
}

// Общий State
data class UserState(
    val id: String = "",
    val name: String = "",
    val isAuthenticated: Boolean = false
)

// Общий ViewModel
class SharedUserViewModel(
    private val dispatcher: PlatformDispatcher
) {
    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    private val scope = CoroutineScope(dispatcher.main + SupervisorJob())

    fun login(username: String, password: String) {
        scope.launch {
            withContext(dispatcher.io) {
                // Аутентификация
                val user = authenticate(username, password)
                _state.update {
                    it.copy(
                        id = user.id,
                        name = user.name,
                        isAuthenticated = true
                    )
                }
            }
        }
    }

    fun logout() {
        _state.value = UserState()
    }

    fun onCleared() {
        scope.cancel()
    }
}

// Expect функция для DI
expect fun createSharedUserViewModel(): SharedUserViewModel
```

### Android (androidMain)

```kotlin
// androidMain/kotlin/PlatformDispatcher.kt

actual class PlatformDispatcher actual constructor() {
    actual val main: CoroutineDispatcher = Dispatchers.Main
    actual val io: CoroutineDispatcher = Dispatchers.IO
}

actual fun createSharedUserViewModel(): SharedUserViewModel {
    return SharedUserViewModel(PlatformDispatcher())
}

// Использование в Compose
@Composable
fun UserScreen() {
    val viewModel = remember { createSharedUserViewModel() }
    val state by viewModel.state.collectAsState()

    DisposableEffect(Unit) {
        onDispose { viewModel.onCleared() }
    }

    // UI...
}
```

### iOS (iosMain)

```kotlin
// iosMain/kotlin/PlatformDispatcher.kt

actual class PlatformDispatcher actual constructor() {
    actual val main: CoroutineDispatcher = Dispatchers.Main
    actual val io: CoroutineDispatcher = Dispatchers.Default
}

actual fun createSharedUserViewModel(): SharedUserViewModel {
    return SharedUserViewModel(PlatformDispatcher())
}
```

### Использование в SwiftUI

```swift
import shared // KMP модуль

class UserViewModelWrapper: ObservableObject {
    private let sharedViewModel: SharedUserViewModel

    @Published var state: UserState

    private var cancellable: Cancellable?

    init() {
        sharedViewModel = SharedUserViewModelKt.createSharedUserViewModel()
        state = sharedViewModel.state.value

        // Подписка на StateFlow
        cancellable = FlowCollector(
            flow: sharedViewModel.state,
            onEach: { [weak self] newState in
                DispatchQueue.main.async {
                    self?.state = newState
                }
            }
        )
    }

    func login(username: String, password: String) {
        sharedViewModel.login(username: username, password: password)
    }

    func logout() {
        sharedViewModel.logout()
    }

    deinit {
        sharedViewModel.onCleared()
        cancellable?.cancel()
    }
}

struct UserScreen: View {
    @StateObject private var viewModel = UserViewModelWrapper()

    var body: some View {
        VStack {
            if viewModel.state.isAuthenticated {
                Text("Привет, \(viewModel.state.name)!")
                Button("Выйти") {
                    viewModel.logout()
                }
            } else {
                LoginForm(onLogin: viewModel.login)
            }
        }
    }
}
```

---

## 7. Шесть распространённых ошибок

### Ошибка 1: Создание @StateObject в body

```swift
// НЕПРАВИЛЬНО - создаётся заново при каждом рендере
struct BadView: View {
    var body: some View {
        let viewModel = ViewModel() // Каждый раз новый!
        Text(viewModel.text)
    }
}

// ПРАВИЛЬНО
struct GoodView: View {
    @StateObject private var viewModel = ViewModel()

    var body: some View {
        Text(viewModel.text)
    }
}
```

```kotlin
// НЕПРАВИЛЬНО в Compose
@Composable
fun BadView() {
    val viewModel = ViewModel() // Создаётся при каждой рекомпозиции!
    Text(viewModel.text)
}

// ПРАВИЛЬНО
@Composable
fun GoodView() {
    val viewModel = remember { ViewModel() }
    // или
    val viewModel: MyViewModel = viewModel()
    Text(viewModel.text)
}
```

### Ошибка 2: Забыли remember в Compose

```kotlin
// НЕПРАВИЛЬНО - состояние сбрасывается
@Composable
fun Counter() {
    var count = mutableStateOf(0) // Нет remember!
    Button(onClick = { count.value++ }) {
        Text("Count: ${count.value}")
    }
}

// ПРАВИЛЬНО
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }
    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

### Ошибка 3: Мутация состояния напрямую

```swift
// НЕПРАВИЛЬНО - мутируем массив без триггера обновления
class BadViewModel: ObservableObject {
    @Published var items: [String] = []

    func addItem(_ item: String) {
        items.append(item) // Работает, но...
    }

    func modifyItem(at index: Int) {
        items[index] = "Modified" // Может не триггерить обновление!
    }
}

// ПРАВИЛЬНО - создаём новый массив
class GoodViewModel: ObservableObject {
    @Published var items: [String] = []

    func modifyItem(at index: Int) {
        var newItems = items
        newItems[index] = "Modified"
        items = newItems
    }
}
```

```kotlin
// НЕПРАВИЛЬНО в Compose
@Composable
fun BadList() {
    val items = remember { mutableListOf("A", "B") }

    Button(onClick = {
        items.add("C") // UI не обновится!
    }) {
        Text("Items: ${items.size}")
    }
}

// ПРАВИЛЬНО
@Composable
fun GoodList() {
    var items by remember { mutableStateOf(listOf("A", "B")) }

    Button(onClick = {
        items = items + "C" // Новый список
    }) {
        Text("Items: ${items.size}")
    }
}
```

### Ошибка 4: Обновление состояния не на главном потоке

```swift
// НЕПРАВИЛЬНО
class BadViewModel: ObservableObject {
    @Published var data: String = ""

    func fetchData() {
        DispatchQueue.global().async {
            let result = self.loadFromNetwork()
            self.data = result // Crash или warning!
        }
    }
}

// ПРАВИЛЬНО
class GoodViewModel: ObservableObject {
    @Published var data: String = ""

    func fetchData() {
        Task {
            let result = await loadFromNetwork()
            await MainActor.run {
                self.data = result
            }
        }
    }
}
```

```kotlin
// НЕПРАВИЛЬНО
class BadViewModel : ViewModel() {
    private val _data = MutableStateFlow("")

    fun fetchData() {
        thread {
            val result = loadFromNetwork()
            _data.value = result // Может работать, но не идиоматично
        }
    }
}

// ПРАВИЛЬНО
class GoodViewModel : ViewModel() {
    private val _data = MutableStateFlow("")

    fun fetchData() {
        viewModelScope.launch {
            val result = withContext(Dispatchers.IO) {
                loadFromNetwork()
            }
            _data.value = result // На Main диспетчере
        }
    }
}
```

### Ошибка 5: Утечка подписок

```swift
// НЕПРАВИЛЬНО - утечка памяти
class LeakyViewModel: ObservableObject {
    private var cancellables = Set<AnyCancellable>()

    func subscribe(to publisher: AnyPublisher<String, Never>) {
        publisher
            .sink { [self] value in // Strong self!
                self.handleValue(value)
            }
            .store(in: &cancellables)
    }
}

// ПРАВИЛЬНО
class SafeViewModel: ObservableObject {
    private var cancellables = Set<AnyCancellable>()

    func subscribe(to publisher: AnyPublisher<String, Never>) {
        publisher
            .sink { [weak self] value in
                self?.handleValue(value)
            }
            .store(in: &cancellables)
    }
}
```

```kotlin
// НЕПРАВИЛЬНО - корутина живёт после уничтожения
class LeakyViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)

    fun startObserving(flow: Flow<String>) {
        scope.launch {
            flow.collect { /* ... */ }
        }
    }
    // Нет отмены scope!
}

// ПРАВИЛЬНО
class SafeViewModel : ViewModel() {
    fun startObserving(flow: Flow<String>) {
        viewModelScope.launch {
            flow.collect { /* ... */ }
        }
    }
    // viewModelScope отменяется автоматически
}
```

### Ошибка 6: Избыточные рекомпозиции/перерисовки

```swift
// НЕПРАВИЛЬНО - всё перерисовывается
struct BadParent: View {
    @State private var counter = 0
    @State private var unrelatedData = "Static"

    var body: some View {
        VStack {
            Text("Counter: \(counter)")
            ExpensiveChild(data: unrelatedData) // Перерисовывается!
            Button("+") { counter += 1 }
        }
    }
}

// ПРАВИЛЬНО - используем EquatableView или извлекаем
struct GoodParent: View {
    @State private var counter = 0

    var body: some View {
        VStack {
            Text("Counter: \(counter)")
            StaticChild() // Не зависит от counter
            Button("+") { counter += 1 }
        }
    }
}

struct StaticChild: View, Equatable {
    var body: some View {
        ExpensiveContent()
    }
}
```

```kotlin
// НЕПРАВИЛЬНО - лишние рекомпозиции
@Composable
fun BadParent() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter")
        ExpensiveChild(data = "Static") // Рекомпозируется!
        Button(onClick = { counter++ }) { Text("+") }
    }
}

// ПРАВИЛЬНО - используем remember для стабильных данных
@Composable
fun GoodParent() {
    var counter by remember { mutableStateOf(0) }
    val stableData = remember { "Static" }

    Column {
        Text("Counter: $counter")
        ExpensiveChild(data = stableData) // Стабильный параметр
        Button(onClick = { counter++ }) { Text("+") }
    }
}

// Или используем key для контроля
@Composable
fun BetterParent() {
    var counter by remember { mutableStateOf(0) }

    Column {
        Text("Counter: $counter")
        key("expensive-child") {
            ExpensiveChild(data = "Static")
        }
        Button(onClick = { counter++ }) { Text("+") }
    }
}
```

---

## 8. Три ментальные модели

### Модель 1: "Источник истины" (Single Source of Truth)

```
┌─────────────────────────────────────────────────────────────┐
│                    ИСТОЧНИК ИСТИНЫ                          │
│                                                             │
│  SwiftUI:                    Compose:                       │
│  ┌─────────────┐             ┌─────────────┐               │
│  │ @State      │             │ remember    │               │
│  │ @StateObject│             │ ViewModel   │               │
│  │ Store       │             │ StateFlow   │               │
│  └──────┬──────┘             └──────┬──────┘               │
│         │                           │                       │
│         ▼                           ▼                       │
│  ┌─────────────┐             ┌─────────────┐               │
│  │    View     │             │ Composable  │               │
│  │  (читает)   │             │  (читает)   │               │
│  └──────┬──────┘             └──────┬──────┘               │
│         │                           │                       │
│         ▼                           ▼                       │
│  ┌─────────────┐             ┌─────────────┐               │
│  │   Action    │             │   Intent    │               │
│  │ (изменяет)  │             │ (изменяет)  │               │
│  └─────────────┘             └─────────────┘               │
└─────────────────────────────────────────────────────────────┘

Правило: Состояние изменяется только через определённые точки входа.
         UI только читает и отображает.
```

### Модель 2: "Жизненный цикл состояния"

```
SwiftUI:
┌─────────────────────────────────────────────────────────────┐
│  View появляется                                            │
│       │                                                     │
│       ▼                                                     │
│  @StateObject создаётся ──────────────────────┐            │
│       │                                        │            │
│       ▼                                        │            │
│  View обновляется (много раз) ◄───┐           │            │
│       │                           │            │            │
│       ├───── @State сохраняется ──┘           │            │
│       │                                        │            │
│       ▼                                        │            │
│  View исчезает                                 │            │
│       │                                        │            │
│       ▼                                        │            │
│  @StateObject уничтожается ◄──────────────────┘            │
└─────────────────────────────────────────────────────────────┘

Compose:
┌─────────────────────────────────────────────────────────────┐
│  Composable входит в композицию                             │
│       │                                                     │
│       ▼                                                     │
│  remember { } выполняется ────────────────────┐            │
│       │                                        │            │
│       ▼                                        │            │
│  Рекомпозиция (много раз) ◄───┐               │            │
│       │                        │               │            │
│       ├── remember сохраняет ──┘               │            │
│       │                                        │            │
│       ▼                                        │            │
│  Composable покидает композицию                │            │
│       │                                        │            │
│       ▼                                        │            │
│  remember очищается ◄─────────────────────────┘            │
└─────────────────────────────────────────────────────────────┘
```

### Модель 3: "Поток данных"

```
Unidirectional Data Flow (однонаправленный поток данных):

     ┌──────────────────────────────────────────────┐
     │                                              │
     │    ┌─────────┐                               │
     │    │  STATE  │ ◄─────────────────────┐      │
     │    └────┬────┘                       │      │
     │         │                            │      │
     │         │ (данные текут вниз)        │      │
     │         ▼                            │      │
     │    ┌─────────┐                       │      │
     │    │   UI    │                       │      │
     │    └────┬────┘                       │      │
     │         │                            │      │
     │         │ (события текут вверх)      │      │
     │         ▼                            │      │
     │    ┌─────────┐                       │      │
     │    │ ACTION  │ ──────────────────────┘      │
     │    └─────────┘                              │
     │                                              │
     └──────────────────────────────────────────────┘

SwiftUI:  State → View → User Action → @State mutation → View update
Compose:  State → Composable → User Event → Intent → State update → Recomposition
```

---

## 9. Quiz: Проверь себя

### Вопрос 1

Что произойдёт при выполнении этого кода?

**SwiftUI:**
```swift
struct QuizView: View {
    var count = 0

    var body: some View {
        Button("Count: \(count)") {
            count += 1  // ???
        }
    }
}
```

**Compose:**
```kotlin
@Composable
fun QuizView() {
    var count = 0

    Button(onClick = { count++ }) {
        Text("Count: $count")
    }
}
```

<details>
<summary>Ответ</summary>

**SwiftUI:** Ошибка компиляции — `count` это `let` (struct неизменяем), нужен `@State`.

**Compose:** Код скомпилируется, но счётчик всегда будет 0. Переменная пересоздаётся при каждой рекомпозиции. Нужен `remember { mutableStateOf(0) }`.

</details>

---

### Вопрос 2

В чём разница между этими двумя подходами?

**Вариант A:**
```swift
struct ParentView: View {
    @StateObject var viewModel = ViewModel()

    var body: some View {
        ChildView(viewModel: viewModel)
    }
}

struct ChildView: View {
    @ObservedObject var viewModel: ViewModel
    // ...
}
```

**Вариант B:**
```swift
struct ParentView: View {
    @StateObject var viewModel = ViewModel()

    var body: some View {
        ChildView(viewModel: viewModel)
    }
}

struct ChildView: View {
    @StateObject var viewModel: ViewModel  // StateObject вместо ObservedObject
    // ...
}
```

<details>
<summary>Ответ</summary>

**Вариант A (правильный):** `@ObservedObject` в ChildView означает, что View не владеет объектом, а только наблюдает за ним. ViewModel создаётся один раз в ParentView.

**Вариант B (неправильный):** `@StateObject` в ChildView попытается создать новый ViewModel при инициализации. Это приведёт к игнорированию переданного viewModel и созданию нового экземпляра.

**Правило:** `@StateObject` = создаю и владею, `@ObservedObject` = получаю и наблюдаю.

</details>

---

### Вопрос 3

Почему этот код может вызвать проблемы с производительностью?

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn {
        items(users) { user ->
            UserCard(
                user = user,
                onClick = { handleClick(user) }  // ???
            )
        }
    }
}

@Composable
fun UserCard(
    user: User,
    onClick: () -> Unit
) {
    // ...
}
```

<details>
<summary>Ответ</summary>

Лямбда `{ handleClick(user) }` создаётся заново при каждой рекомпозиции, что делает `onClick` нестабильным параметром. Это приводит к рекомпозиции всех `UserCard` даже когда данные не изменились.

**Решение 1:** Использовать `remember` с ключом:
```kotlin
items(users, key = { it.id }) { user ->
    val onClick = remember(user.id) { { handleClick(user) } }
    UserCard(user = user, onClick = onClick)
}
```

**Решение 2:** Передавать ID вместо лямбды:
```kotlin
UserCard(
    user = user,
    onClickUserId = user.id,
    onUserClick = ::handleClick
)
```

</details>

---

## 10. Связанные заметки

- [[ios-state-management]] — Глубокое погружение в SwiftUI state management
- [[android-state-management]] — Детальный разбор Compose state
- [[kotlin-multiplatform-architecture]] — Архитектура KMP приложений
- [[reactive-programming-fundamentals]] — Основы реактивного программирования
- [[combine-vs-rxswift]] — Сравнение реактивных фреймворков iOS
- [[kotlin-flow-guide]] — Полное руководство по Kotlin Flow

---

## Ссылки

- [SwiftUI State Management](https://developer.apple.com/documentation/swiftui/state-and-data-flow)
- [Compose State](https://developer.android.com/jetpack/compose/state)
- [KMP Shared ViewModel](https://kotlinlang.org/docs/multiplatform-mobile-ktor-sqldelight.html)
- [TCA - The Composable Architecture](https://github.com/pointfreeco/swift-composable-architecture)
- [MVI Architecture](https://orbit-mvi.org/)
