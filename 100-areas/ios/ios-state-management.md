---
title: "Управление состоянием в iOS"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/state-management
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-state-management]]"
  - "[[ios-swiftui]]"
  - "[[ios-architecture-patterns]]"
---

## TL;DR

SwiftUI предоставляет мощную систему управления состоянием через property wrappers: `@State` для локального состояния, `@Binding` для передачи состояния вниз по иерархии, `@StateObject` для владения ObservableObject, `@ObservedObject` для наблюдения, `@EnvironmentObject` для глобального состояния, `@Environment` для системных значений, `@AppStorage` для UserDefaults и `@SceneStorage` для восстановления состояния сцены. Ключевой принцип — single source of truth.

## Аналогии

1. **@State vs @Binding** — как владелец дома (@State) и арендатор (@Binding): владелец контролирует недвижимость, арендатор может использовать, но не владеет
2. **@StateObject vs @ObservedObject** — как создатель (@StateObject) и наблюдатель (@ObservedObject): создатель ответственен за жизненный цикл объекта, наблюдатель только следит
3. **@EnvironmentObject** — как атмосфера, которой дышат все: доступна везде в иерархии без явной передачи
4. **Single Source of Truth** — как единая база данных вместо множества копий: одно место истины предотвращает рассинхронизацию

## Основы State Management в SwiftUI

### 1. @State — Локальное Состояние View

`@State` используется для простых value types, которыми владеет конкретная view.

```swift
struct CounterView: View {
    @State private var count = 0
    @State private var isAnimating = false

    var body: some View {
        VStack(spacing: 20) {
            Text("Count: \(count)")
                .font(.title)
                .scaleEffect(isAnimating ? 1.2 : 1.0)

            Button("Increment") {
                withAnimation(.spring()) {
                    count += 1
                    isAnimating = true
                }

                DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
                    isAnimating = false
                }
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }
}
```

**Диаграмма потока состояния:**

```
┌─────────────────────────────────────┐
│     CounterView                     │
│  ┌──────────────────────────────┐   │
│  │  @State count = 0            │   │
│  │  @State isAnimating = false  │   │
│  └──────────────────────────────┘   │
│              ↓                      │
│         [Body renders]              │
│              ↓                      │
│      [User taps button]             │
│              ↓                      │
│     count += 1 (mutation)           │
│              ↓                      │
│    SwiftUI re-renders view          │
└─────────────────────────────────────┘
```

### 2. @Binding — Двусторонняя Передача Состояния

`@Binding` создает двустороннюю связь между parent и child view.

```swift
struct VolumeControlView: View {
    @State private var volume: Double = 0.5

    var body: some View {
        VStack {
            Text("Volume: \(Int(volume * 100))%")
                .font(.headline)

            VolumeSlider(volume: $volume)

            HStack {
                Button("Mute") { volume = 0 }
                Button("Max") { volume = 1.0 }
            }
        }
    }
}

struct VolumeSlider: View {
    @Binding var volume: Double

    var body: some View {
        VStack {
            Slider(value: $volume, in: 0...1)

            HStack {
                Button(action: { volume = max(0, volume - 0.1) }) {
                    Image(systemName: "speaker.wave.1")
                }

                Button(action: { volume = min(1, volume + 0.1) }) {
                    Image(systemName: "speaker.wave.3")
                }
            }
        }
        .padding()
    }
}
```

**Диаграмма Binding потока:**

```
┌────────────────────────────────────────┐
│  VolumeControlView (Parent)            │
│  ┌──────────────────────────────┐      │
│  │  @State volume = 0.5         │      │
│  └──────────────────────────────┘      │
│              ↓ (pass reference)        │
│  ┌──────────────────────────────┐      │
│  │  VolumeSlider (Child)        │      │
│  │  ┌────────────────────────┐  │      │
│  │  │ @Binding var volume    │  │      │
│  │  └────────────────────────┘  │      │
│  │           ↓                  │      │
│  │   User changes slider        │      │
│  │           ↓                  │      │
│  │   Binding updates parent     │      │
│  └──────────────────────────────┘      │
│              ↓                         │
│      Parent re-renders                 │
└────────────────────────────────────────┘
```

### 3. @StateObject vs @ObservedObject

**@StateObject** — view владеет объектом и управляет его жизненным циклом.
**@ObservedObject** — view наблюдает за объектом, созданным извне.

```swift
// ObservableObject модель
@MainActor
class TimerViewModel: ObservableObject {
    @Published var secondsElapsed = 0
    @Published var isRunning = false

    private var timer: Timer?

    func start() {
        guard !isRunning else { return }
        isRunning = true

        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.secondsElapsed += 1
        }
    }

    func stop() {
        isRunning = false
        timer?.invalidate()
        timer = nil
    }

    func reset() {
        stop()
        secondsElapsed = 0
    }

    deinit {
        timer?.invalidate()
    }
}

// Parent view создает и владеет объектом
struct TimerContainerView: View {
    @StateObject private var viewModel = TimerViewModel()

    var body: some View {
        VStack(spacing: 20) {
            Text("Timer Container")
                .font(.title)

            // Передаем viewModel дочерней view
            TimerDisplayView(viewModel: viewModel)

            TimerControlsView(viewModel: viewModel)
        }
    }
}

// Child view наблюдает за объектом
struct TimerDisplayView: View {
    @ObservedObject var viewModel: TimerViewModel

    var body: some View {
        VStack {
            Text("\(viewModel.secondsElapsed)s")
                .font(.system(size: 60, weight: .bold, design: .monospaced))
                .foregroundColor(viewModel.isRunning ? .green : .primary)
        }
        .padding()
        .background(Color.gray.opacity(0.1))
        .cornerRadius(12)
    }
}

struct TimerControlsView: View {
    @ObservedObject var viewModel: TimerViewModel

    var body: some View {
        HStack(spacing: 16) {
            Button(viewModel.isRunning ? "Stop" : "Start") {
                if viewModel.isRunning {
                    viewModel.stop()
                } else {
                    viewModel.start()
                }
            }
            .buttonStyle(.borderedProminent)

            Button("Reset") {
                viewModel.reset()
            }
            .buttonStyle(.bordered)
            .disabled(viewModel.isRunning)
        }
    }
}
```

**Диаграмма жизненного цикла:**

```
┌─────────────────────────────────────────────────┐
│  TimerContainerView                             │
│  ┌───────────────────────────────────────────┐  │
│  │ @StateObject viewModel = TimerViewModel() │  │
│  │        (owns lifecycle)                   │  │
│  └───────────────────────────────────────────┘  │
│              ↓                 ↓                 │
│    ┌─────────────────┐  ┌──────────────────┐    │
│    │ TimerDisplayView│  │ TimerControlsView│    │
│    │ @ObservedObject │  │  @ObservedObject │    │
│    │   (observes)    │  │    (observes)    │    │
│    └─────────────────┘  └──────────────────┘    │
│              ↓                 ↓                 │
│         [Both listen to @Published changes]     │
│              ↓                                   │
│    viewModel.secondsElapsed changes              │
│              ↓                                   │
│       Both views re-render                       │
└─────────────────────────────────────────────────┘
```

### 4. @EnvironmentObject — Глобальное Состояние

`@EnvironmentObject` передает данные через всю иерархию view без явной передачи.

```swift
// Глобальная модель настроек
@MainActor
class AppSettings: ObservableObject {
    @Published var theme: Theme = .light
    @Published var fontSize: FontSize = .medium
    @Published var notificationsEnabled = true

    enum Theme: String, CaseIterable {
        case light, dark, auto
    }

    enum FontSize: String, CaseIterable {
        case small, medium, large

        var scale: CGFloat {
            switch self {
            case .small: return 0.8
            case .medium: return 1.0
            case .large: return 1.2
            }
        }
    }
}

// Root view внедряет объект
@main
struct MyApp: App {
    @StateObject private var settings = AppSettings()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(settings)
        }
    }
}

// Любая view в иерархии может получить доступ
struct ContentView: View {
    var body: some View {
        NavigationStack {
            VStack {
                Text("Main Screen")

                NavigationLink("Settings") {
                    SettingsView()
                }
            }
        }
    }
}

struct SettingsView: View {
    @EnvironmentObject private var settings: AppSettings

    var body: some View {
        Form {
            Section("Appearance") {
                Picker("Theme", selection: $settings.theme) {
                    ForEach(AppSettings.Theme.allCases, id: \.self) { theme in
                        Text(theme.rawValue.capitalized).tag(theme)
                    }
                }

                Picker("Font Size", selection: $settings.fontSize) {
                    ForEach(AppSettings.FontSize.allCases, id: \.self) { size in
                        Text(size.rawValue.capitalized).tag(size)
                    }
                }
            }

            Section("Notifications") {
                Toggle("Enable Notifications", isOn: $settings.notificationsEnabled)
            }
        }
        .navigationTitle("Settings")
    }
}

// Глубоко вложенная view тоже имеет доступ
struct DeepNestedView: View {
    @EnvironmentObject private var settings: AppSettings

    var body: some View {
        Text("Font size: \(settings.fontSize.rawValue)")
            .scaleEffect(settings.fontSize.scale)
    }
}
```

**Диаграмма EnvironmentObject:**

```
┌──────────────────────────────────────────┐
│  MyApp                                   │
│  @StateObject settings = AppSettings()  │
│  .environmentObject(settings)            │
└──────────────────┬───────────────────────┘
                   ↓ (injected into environment)
         ┌─────────────────────┐
         │   ContentView       │
         │ (no direct access)  │
         └─────────┬───────────┘
                   ↓
         ┌─────────────────────┐
         │   SettingsView      │
         │ @EnvironmentObject  │
         │     settings        │
         └─────────┬───────────┘
                   ↓
         ┌─────────────────────┐
         │  DeepNestedView     │
         │ @EnvironmentObject  │
         │     settings        │
         └─────────────────────┘
```

### 5. @Environment — Системные Значения

`@Environment` предоставляет доступ к системным значениям SwiftUI.

```swift
struct AdaptiveView: View {
    @Environment(\.colorScheme) private var colorScheme
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @Environment(\.dismiss) private var dismiss
    @Environment(\.scenePhase) private var scenePhase

    var body: some View {
        VStack(spacing: 20) {
            Text("Color Scheme: \(colorScheme == .dark ? "Dark" : "Light")")

            Text("Layout: \(horizontalSizeClass == .compact ? "Compact" : "Regular")")

            Text("Scene Phase: \(scenePhaseText)")

            Button("Dismiss") {
                dismiss()
            }
        }
        .padding()
        .background(colorScheme == .dark ? Color.black : Color.white)
        .onChange(of: scenePhase) { oldPhase, newPhase in
            handleScenePhaseChange(newPhase)
        }
    }

    private var scenePhaseText: String {
        switch scenePhase {
        case .active: return "Active"
        case .inactive: return "Inactive"
        case .background: return "Background"
        @unknown default: return "Unknown"
        }
    }

    private func handleScenePhaseChange(_ phase: ScenePhase) {
        switch phase {
        case .active:
            print("App became active")
        case .inactive:
            print("App became inactive")
        case .background:
            print("App moved to background")
        @unknown default:
            break
        }
    }
}

// Кастомные Environment Values
struct UserIDKey: EnvironmentKey {
    static let defaultValue: String = "guest"
}

extension EnvironmentValues {
    var userID: String {
        get { self[UserIDKey.self] }
        set { self[UserIDKey.self] = newValue }
    }
}

struct ParentView: View {
    var body: some View {
        ChildView()
            .environment(\.userID, "user_123")
    }
}

struct ChildView: View {
    @Environment(\.userID) private var userID

    var body: some View {
        Text("User ID: \(userID)")
    }
}
```

### 6. @AppStorage — UserDefaults Binding

`@AppStorage` автоматически синхронизирует значение с UserDefaults.

```swift
struct UserPreferencesView: View {
    @AppStorage("username") private var username = "Guest"
    @AppStorage("isDarkMode") private var isDarkMode = false
    @AppStorage("notificationTime") private var notificationTime = Date()
    @AppStorage("favoriteColor") private var favoriteColor = Color.blue

    var body: some View {
        Form {
            Section("Profile") {
                TextField("Username", text: $username)

                Toggle("Dark Mode", isOn: $isDarkMode)
            }

            Section("Preferences") {
                DatePicker("Notification Time",
                          selection: $notificationTime,
                          displayedComponents: .hourAndMinute)

                ColorPicker("Favorite Color", selection: $favoriteColor)
            }

            Section {
                Button("Reset to Defaults") {
                    username = "Guest"
                    isDarkMode = false
                    notificationTime = Date()
                    favoriteColor = .blue
                }
            }
        }
        .navigationTitle("Preferences")
    }
}

// AppStorage с кастомными типами через RawRepresentable
enum SortOrder: String {
    case ascending, descending, none
}

struct SortableListView: View {
    @AppStorage("sortOrder") private var sortOrder: SortOrder = .none

    var body: some View {
        VStack {
            Picker("Sort Order", selection: $sortOrder) {
                Text("None").tag(SortOrder.none)
                Text("Ascending").tag(SortOrder.ascending)
                Text("Descending").tag(SortOrder.descending)
            }
            .pickerStyle(.segmented)

            Text("Current: \(sortOrder.rawValue)")
        }
        .padding()
    }
}
```

### 7. @SceneStorage — Восстановление Состояния Сцены

`@SceneStorage` сохраняет состояние для конкретной сцены (окна).

```swift
struct DocumentEditorView: View {
    @SceneStorage("selectedTab") private var selectedTab = 0
    @SceneStorage("editorText") private var editorText = ""
    @SceneStorage("scrollPosition") private var scrollPosition: CGFloat = 0
    @SceneStorage("isEditing") private var isEditing = false

    var body: some View {
        TabView(selection: $selectedTab) {
            // Tab 1: Editor
            VStack {
                TextEditor(text: $editorText)
                    .frame(maxWidth: .infinity, maxHeight: .infinity)
                    .border(Color.gray, width: 1)

                HStack {
                    Text("\(editorText.count) characters")
                        .foregroundColor(.secondary)

                    Spacer()

                    Button(isEditing ? "Done" : "Edit") {
                        isEditing.toggle()
                    }
                }
                .padding()
            }
            .tabItem {
                Label("Editor", systemImage: "doc.text")
            }
            .tag(0)

            // Tab 2: Preview
            ScrollView {
                Text(editorText.isEmpty ? "No content" : editorText)
                    .padding()
            }
            .tabItem {
                Label("Preview", systemImage: "eye")
            }
            .tag(1)
        }
    }
}

// Multiple scene support
struct MultiWindowApp: App {
    var body: some Scene {
        WindowGroup {
            MainSceneView()
        }

        // Каждое окно имеет собственный SceneStorage
        WindowGroup("Document", for: Document.ID.self) { $documentID in
            if let id = documentID {
                DocumentSceneView(documentID: id)
            }
        }
    }
}

struct MainSceneView: View {
    @SceneStorage("mainTab") private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            Text("Home").tabItem { Label("Home", systemImage: "house") }.tag(0)
            Text("Settings").tabItem { Label("Settings", systemImage: "gear") }.tag(1)
        }
    }
}
```

## Single Source of Truth Pattern

Фундаментальный принцип SwiftUI — каждый кусочек данных имеет единственный источник истины.

```swift
// ❌ НЕПРАВИЛЬНО: Дублирование состояния
struct BadCounterView: View {
    @State private var count = 0  // Source 1
    @State private var displayCount = 0  // Source 2 (duplicate!)

    var body: some View {
        VStack {
            Text("Count: \(displayCount)")
            Button("Increment") {
                count += 1
                displayCount = count  // Manual sync - error prone!
            }
        }
    }
}

// ✅ ПРАВИЛЬНО: Единый источник истины
struct GoodCounterView: View {
    @State private var count = 0  // Single source

    var body: some View {
        VStack {
            Text("Count: \(count)")  // Derived from source
            Button("Increment") {
                count += 1
            }
        }
    }
}

// Пример с вычисляемыми свойствами
@MainActor
class ShoppingCartViewModel: ObservableObject {
    @Published var items: [CartItem] = []

    // Вычисляемые свойства вместо дублирования
    var totalItems: Int {
        items.reduce(0) { $0 + $1.quantity }
    }

    var totalPrice: Double {
        items.reduce(0) { $0 + ($1.price * Double($1.quantity)) }
    }

    var hasItems: Bool {
        !items.isEmpty
    }

    func addItem(_ item: CartItem) {
        if let index = items.firstIndex(where: { $0.id == item.id }) {
            items[index].quantity += 1
        } else {
            items.append(item)
        }
    }
}

struct CartItem: Identifiable {
    let id: UUID
    var name: String
    var price: Double
    var quantity: Int
}
```

**Диаграмма Single Source of Truth:**

```
┌─────────────────────────────────────────┐
│   ShoppingCartViewModel                 │
│  ┌───────────────────────────────────┐  │
│  │ @Published items: [CartItem]     │  │
│  │     (SINGLE SOURCE OF TRUTH)     │  │
│  └───────────────────────────────────┘  │
│              ↓           ↓         ↓    │
│      ┌───────────┐ ┌──────────┐ ┌─────┐│
│      │totalItems │ │totalPrice│ │has  ││
│      │(computed) │ │(computed)│ │Items││
│      └───────────┘ └──────────┘ └─────┘│
│              ↓                          │
│        [Views observe]                  │
└─────────────────────────────────────────┘
```

## Redux-Like Pattern в iOS

Реализация унидирекционального потока данных в стиле Redux.

```swift
// State
struct AppState {
    var counter: Int = 0
    var todos: [Todo] = []
    var isLoading: Bool = false
    var errorMessage: String?
}

struct Todo: Identifiable, Equatable {
    let id: UUID
    var title: String
    var isCompleted: Bool
}

// Actions
enum AppAction {
    case increment
    case decrement
    case addTodo(title: String)
    case toggleTodo(id: UUID)
    case removeTodo(id: UUID)
    case setLoading(Bool)
    case setError(String?)
}

// Reducer
func appReducer(state: inout AppState, action: AppAction) {
    switch action {
    case .increment:
        state.counter += 1

    case .decrement:
        state.counter -= 1

    case .addTodo(let title):
        let todo = Todo(id: UUID(), title: title, isCompleted: false)
        state.todos.append(todo)

    case .toggleTodo(let id):
        if let index = state.todos.firstIndex(where: { $0.id == id }) {
            state.todos[index].isCompleted.toggle()
        }

    case .removeTodo(let id):
        state.todos.removeAll { $0.id == id }

    case .setLoading(let isLoading):
        state.isLoading = isLoading

    case .setError(let message):
        state.errorMessage = message
    }
}

// Store
@MainActor
class Store: ObservableObject {
    @Published private(set) var state: AppState
    private let reducer: (inout AppState, AppAction) -> Void

    init(
        initialState: AppState = AppState(),
        reducer: @escaping (inout AppState, AppAction) -> Void
    ) {
        self.state = initialState
        self.reducer = reducer
    }

    func dispatch(_ action: AppAction) {
        reducer(&state, action)
    }

    // Middleware support для async операций
    func dispatch(_ asyncAction: @escaping (Store) async -> Void) {
        Task {
            await asyncAction(self)
        }
    }
}

// Async Actions (Thunks)
extension Store {
    func fetchTodos() async {
        dispatch(.setLoading(true))
        dispatch(.setError(nil))

        do {
            // Simulate network call
            try await Task.sleep(for: .seconds(1))

            dispatch(.addTodo(title: "Sample Todo 1"))
            dispatch(.addTodo(title: "Sample Todo 2"))
            dispatch(.setLoading(false))
        } catch {
            dispatch(.setError(error.localizedDescription))
            dispatch(.setLoading(false))
        }
    }
}

// Views
struct ReduxAppView: View {
    @StateObject private var store = Store(reducer: appReducer)

    var body: some View {
        NavigationStack {
            VStack {
                CounterSection(store: store)

                Divider()

                TodoListSection(store: store)
            }
            .navigationTitle("Redux Pattern")
        }
    }
}

struct CounterSection: View {
    @ObservedObject var store: Store

    var body: some View {
        VStack {
            Text("Counter: \(store.state.counter)")
                .font(.title)

            HStack {
                Button("Decrement") {
                    store.dispatch(.decrement)
                }
                .buttonStyle(.bordered)

                Button("Increment") {
                    store.dispatch(.increment)
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding()
    }
}

struct TodoListSection: View {
    @ObservedObject var store: Store
    @State private var newTodoTitle = ""

    var body: some View {
        VStack {
            HStack {
                TextField("New todo", text: $newTodoTitle)
                    .textFieldStyle(.roundedBorder)

                Button("Add") {
                    guard !newTodoTitle.isEmpty else { return }
                    store.dispatch(.addTodo(title: newTodoTitle))
                    newTodoTitle = ""
                }
                .buttonStyle(.borderedProminent)
            }
            .padding()

            if store.state.isLoading {
                ProgressView()
            }

            if let error = store.state.errorMessage {
                Text(error)
                    .foregroundColor(.red)
                    .padding()
            }

            List {
                ForEach(store.state.todos) { todo in
                    HStack {
                        Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                            .foregroundColor(todo.isCompleted ? .green : .gray)
                            .onTapGesture {
                                store.dispatch(.toggleTodo(id: todo.id))
                            }

                        Text(todo.title)
                            .strikethrough(todo.isCompleted)

                        Spacer()
                    }
                }
                .onDelete { indexSet in
                    indexSet.forEach { index in
                        let todo = store.state.todos[index]
                        store.dispatch(.removeTodo(id: todo.id))
                    }
                }
            }
        }
    }
}
```

**Диаграмма Redux потока:**

```
┌────────────────────────────────────────────────┐
│                    View                        │
│          (dispatch action)                     │
└───────────────────┬────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│                  Action                        │
│   (.increment, .addTodo, etc.)                 │
└───────────────────┬────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│                 Reducer                        │
│     (pure function: state + action → state)    │
└───────────────────┬────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│               New State                        │
│         (@Published triggers)                  │
└───────────────────┬────────────────────────────┘
                    ↓
┌────────────────────────────────────────────────┐
│              View Re-renders                   │
│        (SwiftUI observes @Published)           │
└────────────────────────────────────────────────┘
```

## Combine-Based State Store

Использование Combine для реактивного управления состоянием.

```swift
import Combine

// Store с Combine publishers
@MainActor
class CombineStore: ObservableObject {
    // Published state
    @Published private(set) var users: [User] = []
    @Published private(set) var isLoading = false
    @Published private(set) var error: Error?

    // Subjects для событий
    private let userAddedSubject = PassthroughSubject<User, Never>()
    private let errorSubject = PassthroughSubject<Error, Never>()

    // Publishers для подписки
    var userAddedPublisher: AnyPublisher<User, Never> {
        userAddedSubject.eraseToAnyPublisher()
    }

    var errorPublisher: AnyPublisher<Error, Never> {
        errorSubject.eraseToAnyPublisher()
    }

    // Computed publishers
    var userCountPublisher: AnyPublisher<Int, Never> {
        $users
            .map { $0.count }
            .eraseToAnyPublisher()
    }

    var activeUsersPublisher: AnyPublisher<[User], Never> {
        $users
            .map { $0.filter { $0.isActive } }
            .eraseToAnyPublisher()
    }

    private var cancellables = Set<AnyCancellable>()

    init() {
        setupBindings()
    }

    private func setupBindings() {
        // Error handling pipeline
        errorSubject
            .sink { [weak self] error in
                self?.error = error
                print("Error occurred: \(error)")
            }
            .store(in: &cancellables)

        // User added analytics
        userAddedSubject
            .debounce(for: .seconds(0.5), scheduler: DispatchQueue.main)
            .sink { user in
                print("Analytics: User added - \(user.name)")
            }
            .store(in: &cancellables)
    }

    func addUser(_ user: User) {
        users.append(user)
        userAddedSubject.send(user)
    }

    func removeUser(id: UUID) {
        users.removeAll { $0.id == id }
    }

    func fetchUsers() {
        isLoading = true

        // Simulate network request with Combine
        Future<[User], Error> { promise in
            DispatchQueue.global().asyncAfter(deadline: .now() + 1) {
                let mockUsers = [
                    User(name: "Alice", email: "alice@example.com", isActive: true),
                    User(name: "Bob", email: "bob@example.com", isActive: false)
                ]
                promise(.success(mockUsers))
            }
        }
        .receive(on: DispatchQueue.main)
        .sink { [weak self] completion in
            self?.isLoading = false
            if case .failure(let error) = completion {
                self?.errorSubject.send(error)
            }
        } receiveValue: { [weak self] users in
            self?.users = users
        }
        .store(in: &cancellables)
    }
}

struct User: Identifiable {
    let id = UUID()
    var name: String
    var email: String
    var isActive: Bool
}

// View с Combine подписками
struct CombineStoreView: View {
    @StateObject private var store = CombineStore()
    @State private var userCount = 0
    @State private var activeUsers: [User] = []

    var body: some View {
        VStack(spacing: 20) {
            Text("Total Users: \(userCount)")
                .font(.headline)

            Text("Active Users: \(activeUsers.count)")
                .font(.subheadline)

            if store.isLoading {
                ProgressView()
            }

            List(store.users) { user in
                HStack {
                    VStack(alignment: .leading) {
                        Text(user.name)
                            .font(.headline)
                        Text(user.email)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    Spacer()

                    Circle()
                        .fill(user.isActive ? Color.green : Color.gray)
                        .frame(width: 10, height: 10)
                }
            }

            Button("Fetch Users") {
                store.fetchUsers()
            }
            .buttonStyle(.borderedProminent)
        }
        .onReceive(store.userCountPublisher) { count in
            userCount = count
        }
        .onReceive(store.activeUsersPublisher) { users in
            activeUsers = users
        }
        .onReceive(store.errorPublisher) { error in
            print("Received error: \(error)")
        }
    }
}
```

## State Restoration Strategies

Стратегии восстановления состояния приложения.

```swift
// 1. Scene-based restoration
struct RestorationApp: App {
    @StateObject private var appState = AppStateManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .onAppear {
                    appState.restoreState()
                }
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            if newPhase == .background {
                appState.saveState()
            }
        }
    }

    @Environment(\.scenePhase) private var scenePhase
}

// State Manager
@MainActor
class AppStateManager: ObservableObject {
    @Published var navigationPath: [NavigationDestination] = []
    @Published var selectedTab = 0
    @Published var userData: UserData?

    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    private var stateFileURL: URL {
        FileManager.default
            .urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("app_state.json")
    }

    func saveState() {
        let state = PersistableState(
            navigationPath: navigationPath,
            selectedTab: selectedTab,
            userData: userData
        )

        do {
            let data = try encoder.encode(state)
            try data.write(to: stateFileURL)
            print("State saved successfully")
        } catch {
            print("Failed to save state: \(error)")
        }
    }

    func restoreState() {
        guard FileManager.default.fileExists(atPath: stateFileURL.path) else {
            print("No saved state found")
            return
        }

        do {
            let data = try Data(contentsOf: stateFileURL)
            let state = try decoder.decode(PersistableState.self, from: data)

            navigationPath = state.navigationPath
            selectedTab = state.selectedTab
            userData = state.userData

            print("State restored successfully")
        } catch {
            print("Failed to restore state: \(error)")
        }
    }

    func clearState() {
        try? FileManager.default.removeItem(at: stateFileURL)
        navigationPath = []
        selectedTab = 0
        userData = nil
    }
}

struct PersistableState: Codable {
    var navigationPath: [NavigationDestination]
    var selectedTab: Int
    var userData: UserData?
}

enum NavigationDestination: Codable, Hashable {
    case detail(id: String)
    case settings
    case profile
}

struct UserData: Codable {
    var name: String
    var email: String
    var preferences: [String: String]
}

// 2. Incremental state saving
@MainActor
class IncrementalStateManager: ObservableObject {
    @Published var documents: [Document] = [] {
        didSet {
            saveDocuments()
        }
    }

    @Published var recentSearches: [String] = [] {
        didSet {
            saveRecentSearches()
        }
    }

    private let documentsKey = "saved_documents"
    private let searchesKey = "recent_searches"

    init() {
        loadDocuments()
        loadRecentSearches()
    }

    private func saveDocuments() {
        if let encoded = try? JSONEncoder().encode(documents) {
            UserDefaults.standard.set(encoded, forKey: documentsKey)
        }
    }

    private func loadDocuments() {
        if let data = UserDefaults.standard.data(forKey: documentsKey),
           let decoded = try? JSONDecoder().decode([Document].self, from: data) {
            documents = decoded
        }
    }

    private func saveRecentSearches() {
        UserDefaults.standard.set(recentSearches, forKey: searchesKey)
    }

    private func loadRecentSearches() {
        recentSearches = UserDefaults.standard.stringArray(forKey: searchesKey) ?? []
    }
}

struct Document: Codable, Identifiable {
    let id: UUID
    var title: String
    var content: String
    var lastModified: Date
}
```

**Диаграмма стратегии восстановления:**

```
┌──────────────────────────────────────────────┐
│         App Launch                           │
└────────────────┬─────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│    Check for saved state                     │
│    (FileManager / UserDefaults)              │
└────────────────┬─────────────────────────────┘
                 ↓
         ┌───────┴────────┐
         │                │
    State exists    No state found
         │                │
         ↓                ↓
┌────────────────┐  ┌─────────────────┐
│ Decode & Load  │  │ Initialize fresh│
│ Restore state  │  │  default state  │
└────────┬───────┘  └────────┬────────┘
         │                   │
         └────────┬──────────┘
                  ↓
┌──────────────────────────────────────────────┐
│       App running with state                 │
└────────────────┬─────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│  State changes (@Published triggers)         │
└────────────────┬─────────────────────────────┘
                 ↓
┌──────────────────────────────────────────────┐
│  Save state on background / changes          │
│  (Incremental or on phase change)            │
└──────────────────────────────────────────────┘
```

## 6 Типичных Ошибок State Management

### Ошибка 1: Использование @StateObject вместо @ObservedObject в Child View

❌ **Неправильно:**

```swift
struct ParentView: View {
    @StateObject private var viewModel = MyViewModel()

    var body: some View {
        ChildView(viewModel: viewModel)
    }
}

// ❌ Child view создает новый экземпляр при каждом re-render!
struct ChildView: View {
    @StateObject var viewModel: MyViewModel  // WRONG!

    var body: some View {
        Text(viewModel.title)
    }
}
```

✅ **Правильно:**

```swift
struct ParentView: View {
    @StateObject private var viewModel = MyViewModel()

    var body: some View {
        ChildView(viewModel: viewModel)
    }
}

// ✅ Child view наблюдает за объектом, созданным parent
struct ChildView: View {
    @ObservedObject var viewModel: MyViewModel  // CORRECT!

    var body: some View {
        Text(viewModel.title)
    }
}
```

### Ошибка 2: Мутация @Binding внутри View без контроля

❌ **Неправильно:**

```swift
struct SliderView: View {
    @Binding var value: Double

    var body: some View {
        VStack {
            Slider(value: $value, in: 0...100)

            // ❌ Прямая мутация в body - может вызвать бесконечный цикл!
            Button("Set to 50") {
                value = 50  // Dangerous in certain contexts!
            }
            .onAppear {
                value = 25  // ❌ NEVER mutate state in onAppear!
            }
        }
    }
}
```

✅ **Правильно:**

```swift
struct SliderView: View {
    @Binding var value: Double

    var body: some View {
        VStack {
            Slider(value: $value, in: 0...100)

            // ✅ Мутация в action handler
            Button("Set to 50") {
                value = 50
            }
        }
        .task {
            // ✅ Если нужна инициализация, используйте task
            if value == 0 {
                value = 25
            }
        }
    }
}
```

### Ошибка 3: Неправильное использование @EnvironmentObject без инъекции

❌ **Неправильно:**

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
            // ❌ Забыли инъектировать EnvironmentObject!
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var settings: AppSettings  // CRASH!

    var body: some View {
        Text("Settings: \(settings.theme)")
    }
}
```

✅ **Правильно:**

```swift
@main
struct MyApp: App {
    @StateObject private var settings = AppSettings()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(settings)  // ✅ Inject!
        }
    }
}

struct ContentView: View {
    @EnvironmentObject var settings: AppSettings

    var body: some View {
        Text("Settings: \(settings.theme)")
    }
}

// Или используйте Preview с инъекцией
#Preview {
    ContentView()
        .environmentObject(AppSettings())
}
```

### Ошибка 4: Дублирование состояния вместо Single Source of Truth

❌ **Неправильно:**

```swift
@MainActor
class BadViewModel: ObservableObject {
    @Published var items: [Item] = []
    @Published var itemCount: Int = 0  // ❌ Дубликат!
    @Published var isEmpty: Bool = true  // ❌ Дубликат!

    func addItem(_ item: Item) {
        items.append(item)
        itemCount = items.count  // ❌ Ручная синхронизация
        isEmpty = items.isEmpty  // ❌ Легко забыть обновить
    }
}
```

✅ **Правильно:**

```swift
@MainActor
class GoodViewModel: ObservableObject {
    @Published var items: [Item] = []

    // ✅ Computed properties - single source of truth
    var itemCount: Int {
        items.count
    }

    var isEmpty: Bool {
        items.isEmpty
    }

    func addItem(_ item: Item) {
        items.append(item)
        // ✅ Автоматически обновляются!
    }
}
```

### Ошибка 5: Использование @State для Reference Types

❌ **Неправильно:**

```swift
// ❌ @State предназначен для Value Types!
struct BadView: View {
    @State private var viewModel = MyViewModel()  // Reference type!

    var body: some View {
        Text(viewModel.title)
    }
}
```

✅ **Правильно:**

```swift
// ✅ Используйте @StateObject для reference types
struct GoodView: View {
    @StateObject private var viewModel = MyViewModel()

    var body: some View {
        Text(viewModel.title)
    }
}

// Или @State для value types
struct CounterView: View {
    @State private var count: Int = 0  // ✅ Value type
    @State private var isEnabled: Bool = true  // ✅ Value type

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Toggle("Enabled", isOn: $isEnabled)
        }
    }
}
```

### Ошибка 6: Забывание @MainActor для ObservableObject

❌ **Неправильно:**

```swift
// ❌ Без @MainActor - может вызвать UI updates на background thread!
class BadViewModel: ObservableObject {
    @Published var data: [String] = []

    func fetchData() {
        URLSession.shared.dataTask(with: URL(string: "...")!) { data, _, _ in
            // ❌ CRASH! Обновление @Published на background thread
            self.data = parseData(data)
        }.resume()
    }
}
```

✅ **Правильно:**

```swift
// ✅ @MainActor гарантирует UI updates на main thread
@MainActor
class GoodViewModel: ObservableObject {
    @Published var data: [String] = []

    func fetchData() async {
        do {
            let (data, _) = try await URLSession.shared.data(from: URL(string: "...")!)
            // ✅ Автоматически на main thread благодаря @MainActor
            self.data = parseData(data)
        } catch {
            print("Error: \(error)")
        }
    }

    private func parseData(_ data: Data?) -> [String] {
        // Parse logic
        return []
    }
}

// Использование в view
struct DataView: View {
    @StateObject private var viewModel = GoodViewModel()

    var body: some View {
        List(viewModel.data, id: \.self) { item in
            Text(item)
        }
        .task {
            await viewModel.fetchData()
        }
    }
}
```

## Сравнительная Таблица Property Wrappers

| Property Wrapper | Использование | Ownership | Lifecycle | Persistence |
|-----------------|---------------|-----------|-----------|-------------|
| @State | Local value types | View owns | View lifetime | No |
| @Binding | Two-way reference | Parent owns | Passed reference | No |
| @StateObject | ObservableObject creation | View owns | View lifetime | No |
| @ObservedObject | ObservableObject observation | External owns | External | No |
| @EnvironmentObject | Global shared state | App/Scene owns | Injected | No |
| @Environment | System/custom values | System/custom | Inherited | No |
| @AppStorage | UserDefaults binding | App owns | App lifetime | Yes (UserDefaults) |
| @SceneStorage | Scene state restoration | Scene owns | Scene lifetime | Yes (Scene state) |

## Лучшие Практики

1. **Используйте @State для локальных value types** (Int, String, Bool, struct)
2. **Используйте @StateObject для создания ObservableObject** в view
3. **Используйте @ObservedObject только для переданных извне объектов**
4. **Следуйте Single Source of Truth** — избегайте дублирования данных
5. **Помечайте ObservableObject классы как @MainActor** для thread safety
6. **Используйте @EnvironmentObject для глобального состояния**, доступного многим views
7. **Предпочитайте computed properties** вместо дублирования состояния
8. **Используйте @AppStorage для простых настроек**, сохраняемых между запусками
9. **Используйте @SceneStorage для восстановления состояния** конкретной сцены
10. **Применяйте Redux/Combine patterns** для сложных приложений с предсказуемым state flow

## Related Links

- [[android-state-management]] — сравнение с подходами Android (Jetpack Compose)
- [[swiftui-architecture-patterns]] — архитектурные паттерны для SwiftUI
- [[combine-framework]] — реактивное программирование с Combine
- [[swift-concurrency]] — async/await и actors для state management

---

*Последнее обновление: 2026-01-11*
