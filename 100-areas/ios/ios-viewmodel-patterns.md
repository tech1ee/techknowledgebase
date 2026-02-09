---
date: 2026-01-11
tags: [ios, swiftui, mvvm, viewmodel, combine, observable, state-management]
related: "[[android-viewmodel-internals]]"
---

# iOS ViewModel Patterns

## TL;DR

ViewModels в SwiftUI служат посредниками между View и бизнес-логикой, управляя состоянием и обрабатывая пользовательский ввод. Основные подходы: ObservableObject с @Published (iOS 13+), новый @Observable macro (iOS 17+), Input-Output pattern для четкого разделения событий и состояния, async/await для асинхронных операций, и protocol-based ViewModels для тестируемости. Правильный выбор паттерна зависит от версии iOS, сложности состояния и требований к тестированию.

## Аналогии

**ViewModel как диспетчер светофора**: View (водители) видят только сигналы (состояние), а ViewModel (диспетчер) получает данные о трафике (бизнес-логика) и решает, какой свет включить. Водители не знают о камерах и датчиках, они просто реагируют на цвет.

**@Published как радиовещание**: Когда радиостанция (@Published свойство) меняет передачу, все настроенные приемники (SwiftUI Views) автоматически получают новый сигнал. Не нужно вручную звонить каждому слушателю.

**@Observable как умный дом**: Старый способ (@Published) — это кнопки для каждого устройства. Новый @Observable — это умный дом, который сам отслеживает, что изменилось, и обновляет только то, что нужно, без лишних кнопок и проводов.

## Диаграммы

```
┌─────────────────────────────────────────────────────────────┐
│                    ViewModel Lifecycle                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  View Created  →  ViewModel Init  →  Bind State  →  Updates │
│       │                 │                │              │     │
│       └─────────────────┴────────────────┴──────────────┘     │
│                         │                                     │
│                    View Dismissed                             │
│                         │                                     │
│                    ViewModel Deinit                          │
│                    (Cancel subscriptions)                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              ObservableObject vs @Observable                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ObservableObject (iOS 13+)    │   @Observable (iOS 17+)    │
│  ─────────────────────────────────────────────────────────  │
│                                                               │
│  class VM: ObservableObject {  │   @Observable             │
│    @Published var count = 0    │   class VM {              │
│  }                             │     var count = 0         │
│                                │   }                       │
│                                                               │
│  • Manual @Published           │   • Automatic tracking    │
│  • objectWillChange publisher  │   • Macro-based           │
│  • Combines with Combine       │   • Better performance    │
│  • More boilerplate            │   • Less boilerplate      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Input-Output Pattern                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│           User Actions (Input)                               │
│                    │                                         │
│                    ↓                                         │
│         ┌──────────────────────┐                            │
│         │     ViewModel        │                            │
│         │  ┌──────────────┐   │                            │
│  Input  │  │ Business     │   │  Output                    │
│  ─────→ │  │ Logic        │   │  ─────→  UI State         │
│         │  └──────────────┘   │                            │
│         │         │            │                            │
│         │         ↓            │                            │
│         │  ┌──────────────┐   │                            │
│         │  │ Side Effects │   │                            │
│         │  │ (API calls)  │   │                            │
│         │  └──────────────┘   │                            │
│         └──────────────────────┘                            │
│                    │                                         │
│                    ↓                                         │
│            UI Updates (SwiftUI)                              │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    State Machine Flow                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│     ┌──────────┐   load()   ┌──────────┐                   │
│     │  Idle    │ ─────────→ │ Loading  │                   │
│     └──────────┘            └──────────┘                   │
│          ↑                       │                           │
│          │                       ↓                           │
│          │              ┌────────┴────────┐                 │
│          │     success  │                 │  failure        │
│          │         ┌────┤   Processing    ├────┐            │
│          │         │    │                 │    │            │
│          │         ↓    └─────────────────┘    ↓            │
│     ┌────┴─────┐                          ┌─────────┐      │
│     │ Success  │                          │  Error  │      │
│     └──────────┘                          └─────────┘      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Основные паттерны

### 1. ObservableObject Protocol

**Описание**: Классический подход для создания ViewModels в SwiftUI с использованием Combine framework. ObservableObject автоматически публикует изменения через objectWillChange publisher.

**Когда использовать**:
- iOS 13+ совместимость
- Интеграция с Combine pipelines
- Нужен контроль над публикацией изменений

```swift
import SwiftUI
import Combine

class UserProfileViewModel: ObservableObject {
    // @Published автоматически вызывает objectWillChange.send()
    @Published var username: String = ""
    @Published var email: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    private let userService: UserServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    init(userService: UserServiceProtocol = UserService()) {
        self.userService = userService
    }

    func loadUserProfile(userId: String) {
        isLoading = true
        errorMessage = nil

        userService.fetchUser(id: userId)
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isLoading = false
                if case .failure(let error) = completion {
                    self?.errorMessage = error.localizedDescription
                }
            } receiveValue: { [weak self] user in
                self?.username = user.name
                self?.email = user.email
            }
            .store(in: &cancellables)
    }

    // Ручная публикация для батч-обновлений
    func updateProfile(name: String, email: String) {
        objectWillChange.send() // Отправить перед изменением
        username = name
        self.email = email
    }
}

// Использование в View
struct UserProfileView: View {
    @StateObject private var viewModel = UserProfileViewModel()

    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
            } else {
                TextField("Username", text: $viewModel.username)
                TextField("Email", text: $viewModel.email)
            }

            if let error = viewModel.errorMessage {
                Text(error).foregroundColor(.red)
            }
        }
        .onAppear {
            viewModel.loadUserProfile(userId: "123")
        }
    }
}
```

### 2. @Published Property Wrapper

**Описание**: Property wrapper, который автоматически публикует изменения значения через Combine publisher. Работает только с классами, соответствующими ObservableObject.

**Особенности**:
- Публикует изменение **до** того, как значение изменится (willSet, а не didSet)
- Создает publisher для каждого свойства
- Автоматическая интеграция с objectWillChange

```swift
class ShoppingCartViewModel: ObservableObject {
    struct CartItem: Identifiable {
        let id: UUID
        var name: String
        var quantity: Int
        var price: Double
    }

    // @Published на массиве - любое изменение массива триггерит обновление
    @Published var items: [CartItem] = []

    // Computed property для общей суммы
    var totalPrice: Double {
        items.reduce(0) { $0 + ($1.price * Double($1.quantity)) }
    }

    // @Published для состояний загрузки
    @Published var isProcessingPayment = false
    @Published var paymentStatus: PaymentStatus = .idle

    enum PaymentStatus {
        case idle
        case processing
        case success
        case failed(Error)
    }

    func addItem(_ item: CartItem) {
        items.append(item)
        // View автоматически обновится
    }

    func removeItem(id: UUID) {
        items.removeAll { $0.id == id }
    }

    func updateQuantity(itemId: UUID, quantity: Int) {
        if let index = items.firstIndex(where: { $0.id == itemId }) {
            items[index].quantity = quantity
            // items изменился - View обновится
        }
    }

    // Пример использования custom publisher для totalPrice
    var totalPricePublisher: AnyPublisher<Double, Never> {
        $items // $ дает доступ к publisher
            .map { items in
                items.reduce(0) { $0 + ($1.price * Double($1.quantity)) }
            }
            .eraseToAnyPublisher()
    }
}

struct ShoppingCartView: View {
    @StateObject private var viewModel = ShoppingCartViewModel()

    var body: some View {
        List {
            ForEach(viewModel.items) { item in
                HStack {
                    Text(item.name)
                    Spacer()
                    Stepper("\(item.quantity)", value: Binding(
                        get: { item.quantity },
                        set: { viewModel.updateQuantity(itemId: item.id, quantity: $0) }
                    ))
                    Text("$\(item.price * Double(item.quantity), specifier: "%.2f")")
                }
            }
            .onDelete { indexSet in
                indexSet.forEach { index in
                    viewModel.removeItem(id: viewModel.items[index].id)
                }
            }

            Section {
                Text("Total: $\(viewModel.totalPrice, specifier: "%.2f")")
                    .font(.headline)
            }
        }
    }
}
```

### 3. Combine-based ViewModels

**Описание**: ViewModels, построенные на Combine framework с использованием publishers, operators и subscribers для реактивного управления состоянием и side effects.

**Преимущества**:
- Декларативная обработка асинхронных операций
- Композиция операций через operators
- Автоматическая отмена subscriptions

```swift
import Combine
import Foundation

class SearchViewModel: ObservableObject {
    // Input
    @Published var searchQuery: String = ""

    // Output
    @Published var searchResults: [SearchResult] = []
    @Published var isSearching: Bool = false
    @Published var errorMessage: String?

    private let searchService: SearchServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    struct SearchResult: Identifiable {
        let id: String
        let title: String
        let description: String
    }

    init(searchService: SearchServiceProtocol = SearchService()) {
        self.searchService = searchService
        setupBindings()
    }

    private func setupBindings() {
        // Debounce поиска с автоматической отменой предыдущих запросов
        $searchQuery
            .debounce(for: .milliseconds(500), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .handleEvents(receiveOutput: { [weak self] _ in
                self?.isSearching = true
                self?.errorMessage = nil
            })
            .flatMap { [weak self] query -> AnyPublisher<[SearchResult], Error> in
                guard let self = self else {
                    return Empty().eraseToAnyPublisher()
                }
                return self.searchService.search(query: query)
            }
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                self?.isSearching = false
                if case .failure(let error) = completion {
                    self?.errorMessage = error.localizedDescription
                    self?.searchResults = []
                }
            } receiveValue: { [weak self] results in
                self?.searchResults = results
            }
            .store(in: &cancellables)
    }

    // Combine операторы для сложной логики
    func loadRecommendations() {
        let recentSearches = searchService.getRecentSearches()
        let trendingTopics = searchService.getTrendingTopics()

        Publishers.Zip(recentSearches, trendingTopics)
            .map { recent, trending in
                // Комбинируем результаты
                Array(Set(recent + trending).prefix(10))
            }
            .receive(on: DispatchQueue.main)
            .sink { [weak self] completion in
                if case .failure(let error) = completion {
                    self?.errorMessage = error.localizedDescription
                }
            } receiveValue: { [weak self] recommendations in
                self?.searchResults = recommendations
            }
            .store(in: &cancellables)
    }
}

// Пример использования с multiple publishers
class FormViewModel: ObservableObject {
    @Published var email: String = ""
    @Published var password: String = ""
    @Published var confirmPassword: String = ""

    @Published var isEmailValid: Bool = false
    @Published var isPasswordValid: Bool = false
    @Published var doPasswordsMatch: Bool = false
    @Published var canSubmit: Bool = false

    private var cancellables = Set<AnyCancellable>()

    init() {
        // Email validation
        $email
            .map { email in
                let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
                let predicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
                return predicate.evaluate(with: email)
            }
            .assign(to: &$isEmailValid)

        // Password validation
        $password
            .map { $0.count >= 8 }
            .assign(to: &$isPasswordValid)

        // Password match
        Publishers.CombineLatest($password, $confirmPassword)
            .map { password, confirm in
                !password.isEmpty && password == confirm
            }
            .assign(to: &$doPasswordsMatch)

        // Overall form validation
        Publishers.CombineLatest3($isEmailValid, $isPasswordValid, $doPasswordsMatch)
            .map { $0 && $1 && $2 }
            .assign(to: &$canSubmit)
    }
}
```

### 4. @Observable Macro (iOS 17+)

**Описание**: Новый подход к observable state в SwiftUI, основанный на Swift macros. Автоматически отслеживает изменения свойств без необходимости в @Published.

**Преимущества**:
- Меньше boilerplate кода
- Лучшая производительность (только измененные свойства триггерят обновления)
- Поддержка computed properties
- Работает со structs и actors

```swift
import Observation
import SwiftUI

// @Observable автоматически генерирует код для отслеживания изменений
@Observable
class TodoListViewModel {
    struct Todo: Identifiable {
        let id: UUID
        var title: String
        var isCompleted: Bool
        var priority: Priority

        enum Priority: String, CaseIterable {
            case low = "Low"
            case medium = "Medium"
            case high = "High"
        }
    }

    // Не нужен @Published!
    var todos: [Todo] = []
    var filterOption: FilterOption = .all
    var isLoading = false

    enum FilterOption {
        case all, active, completed
    }

    // Computed properties автоматически отслеживаются
    var filteredTodos: [Todo] {
        switch filterOption {
        case .all:
            return todos
        case .active:
            return todos.filter { !$0.isCompleted }
        case .completed:
            return todos.filter { $0.isCompleted }
        }
    }

    var completionProgress: Double {
        guard !todos.isEmpty else { return 0 }
        let completed = todos.filter { $0.isCompleted }.count
        return Double(completed) / Double(todos.count)
    }

    private let repository: TodoRepositoryProtocol

    init(repository: TodoRepositoryProtocol = TodoRepository()) {
        self.repository = repository
    }

    func loadTodos() async {
        isLoading = true
        defer { isLoading = false }

        do {
            todos = try await repository.fetchTodos()
        } catch {
            print("Failed to load todos: \(error)")
        }
    }

    func addTodo(title: String, priority: Todo.Priority) {
        let todo = Todo(id: UUID(), title: title, isCompleted: false, priority: priority)
        todos.append(todo)

        Task {
            try? await repository.save(todo)
        }
    }

    func toggleCompletion(id: UUID) {
        guard let index = todos.firstIndex(where: { $0.id == id }) else { return }
        todos[index].isCompleted.toggle()

        Task {
            try? await repository.update(todos[index])
        }
    }

    func deleteTodo(id: UUID) {
        todos.removeAll { $0.id == id }

        Task {
            try? await repository.delete(id: id)
        }
    }
}

// Использование в View - автоматическое отслеживание зависимостей
struct TodoListView: View {
    @State private var viewModel = TodoListViewModel()
    @State private var newTodoTitle = ""

    var body: some View {
        List {
            // View обновится только при изменении filteredTodos
            ForEach(viewModel.filteredTodos) { todo in
                HStack {
                    Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                        .foregroundColor(todo.isCompleted ? .green : .gray)
                        .onTapGesture {
                            viewModel.toggleCompletion(id: todo.id)
                        }

                    Text(todo.title)
                        .strikethrough(todo.isCompleted)

                    Spacer()

                    Text(todo.priority.rawValue)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .onDelete { indexSet in
                indexSet.forEach { index in
                    viewModel.deleteTodo(id: viewModel.filteredTodos[index].id)
                }
            }
        }
        .toolbar {
            Picker("Filter", selection: $viewModel.filterOption) {
                Text("All").tag(TodoListViewModel.FilterOption.all)
                Text("Active").tag(TodoListViewModel.FilterOption.active)
                Text("Completed").tag(TodoListViewModel.FilterOption.completed)
            }
        }
        .task {
            await viewModel.loadTodos()
        }
    }
}

// @Observable с MainActor для UI updates
@Observable
@MainActor
class WeatherViewModel {
    var temperature: Double?
    var condition: String?
    var isLoading = false
    var error: Error?

    private let weatherService: WeatherServiceProtocol

    init(weatherService: WeatherServiceProtocol = WeatherService()) {
        self.weatherService = weatherService
    }

    func loadWeather(for city: String) async {
        isLoading = true
        error = nil

        do {
            let weather = try await weatherService.fetch(city: city)
            temperature = weather.temperature
            condition = weather.condition
        } catch {
            self.error = error
        }

        isLoading = false
    }
}
```

### 5. Input-Output Pattern

**Описание**: Архитектурный паттерн, разделяющий ViewModel на четкие Input (действия пользователя) и Output (состояние UI). Улучшает тестируемость и понятность data flow.

**Структура**:
- Input: методы/свойства для пользовательских действий
- Output: published properties для UI состояния
- Transform: преобразование input в output

```swift
import Combine
import Foundation

protocol ViewModelType {
    associatedtype Input
    associatedtype Output

    func transform(input: Input) -> Output
}

class LoginViewModel: ViewModelType {
    // MARK: - Input
    struct Input {
        let emailText: AnyPublisher<String, Never>
        let passwordText: AnyPublisher<String, Never>
        let loginTap: AnyPublisher<Void, Never>
    }

    // MARK: - Output
    struct Output {
        let isEmailValid: AnyPublisher<Bool, Never>
        let isPasswordValid: AnyPublisher<Bool, Never>
        let canLogin: AnyPublisher<Bool, Never>
        let loginResult: AnyPublisher<LoginResult, Never>
        let isLoading: AnyPublisher<Bool, Never>
    }

    enum LoginResult {
        case success(User)
        case failure(Error)
    }

    private let authService: AuthServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    init(authService: AuthServiceProtocol = AuthService()) {
        self.authService = authService
    }

    func transform(input: Input) -> Output {
        // Email validation
        let isEmailValid = input.emailText
            .map { email in
                let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
                let predicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
                return predicate.evaluate(with: email)
            }
            .eraseToAnyPublisher()

        // Password validation
        let isPasswordValid = input.passwordText
            .map { $0.count >= 6 }
            .eraseToAnyPublisher()

        // Can login
        let canLogin = Publishers.CombineLatest(isEmailValid, isPasswordValid)
            .map { $0 && $1 }
            .eraseToAnyPublisher()

        // Loading state subject
        let isLoadingSubject = PassthroughSubject<Bool, Never>()

        // Login flow
        let credentials = Publishers.CombineLatest(input.emailText, input.passwordText)

        let loginResult = input.loginTap
            .withLatestFrom(credentials)
            .handleEvents(receiveOutput: { _ in
                isLoadingSubject.send(true)
            })
            .flatMap { [weak self] email, password -> AnyPublisher<LoginResult, Never> in
                guard let self = self else {
                    return Empty().eraseToAnyPublisher()
                }

                return self.authService.login(email: email, password: password)
                    .map { LoginResult.success($0) }
                    .catch { Just(LoginResult.failure($0)) }
                    .eraseToAnyPublisher()
            }
            .handleEvents(receiveOutput: { _ in
                isLoadingSubject.send(false)
            })
            .share()
            .eraseToAnyPublisher()

        return Output(
            isEmailValid: isEmailValid,
            isPasswordValid: isPasswordValid,
            canLogin: canLogin,
            loginResult: loginResult,
            isLoading: isLoadingSubject.eraseToAnyPublisher()
        )
    }
}

// Custom operator для withLatestFrom
extension Publisher {
    func withLatestFrom<Other: Publisher, Result>(
        _ other: Other
    ) -> AnyPublisher<Result, Failure> where Other.Failure == Failure, Other.Output == Result {
        let upstream = self
        return other
            .map { second in
                upstream.map { _ in second }
            }
            .switchToLatest()
            .eraseToAnyPublisher()
    }
}

// Использование в SwiftUI
struct LoginView: View {
    @StateObject private var viewModel = LoginViewModel()
    @State private var email = ""
    @State private var password = ""
    @State private var loginResult: LoginViewModel.LoginResult?
    @State private var isLoading = false

    private let emailSubject = PassthroughSubject<String, Never>()
    private let passwordSubject = PassthroughSubject<String, Never>()
    private let loginTapSubject = PassthroughSubject<Void, Never>()

    var body: some View {
        VStack(spacing: 20) {
            TextField("Email", text: $email)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .textContentType(.emailAddress)
                .autocapitalization(.none)
                .onChange(of: email) { _, newValue in
                    emailSubject.send(newValue)
                }

            SecureField("Password", text: $password)
                .textFieldStyle(RoundedBorderTextFieldStyle())
                .textContentType(.password)
                .onChange(of: password) { _, newValue in
                    passwordSubject.send(newValue)
                }

            Button("Login") {
                loginTapSubject.send()
            }
            .disabled(isLoading)

            if isLoading {
                ProgressView()
            }

            if case .failure(let error) = loginResult {
                Text(error.localizedDescription)
                    .foregroundColor(.red)
            }
        }
        .padding()
        .onAppear {
            let input = LoginViewModel.Input(
                emailText: emailSubject.eraseToAnyPublisher(),
                passwordText: passwordSubject.eraseToAnyPublisher(),
                loginTap: loginTapSubject.eraseToAnyPublisher()
            )

            let output = viewModel.transform(input: input)

            output.isLoading
                .assign(to: &$isLoading)

            output.loginResult
                .assign(to: &$loginResult)
        }
    }
}
```

### 6. ViewModel с async/await

**Описание**: Современный подход к асинхронным операциям в ViewModels с использованием Swift Concurrency (async/await, Task, MainActor).

**Преимущества**:
- Линейный, читаемый код
- Структурированная concurrency
- Автоматическая отмена через Task
- Type-safe error handling

```swift
import SwiftUI

@MainActor
class ProductListViewModel: ObservableObject {
    struct Product: Identifiable, Codable {
        let id: String
        let name: String
        let price: Double
        let imageURL: URL
    }

    enum LoadingState {
        case idle
        case loading
        case success([Product])
        case failure(Error)
    }

    @Published var loadingState: LoadingState = .idle
    @Published var searchQuery: String = ""

    private let productService: ProductServiceProtocol
    private var searchTask: Task<Void, Never>?

    init(productService: ProductServiceProtocol = ProductService()) {
        self.productService = productService
    }

    // Базовая загрузка данных
    func loadProducts() async {
        loadingState = .loading

        do {
            let products = try await productService.fetchProducts()
            loadingState = .success(products)
        } catch {
            loadingState = .failure(error)
        }
    }

    // Поиск с debounce и cancellation
    func searchProducts(query: String) {
        // Отменяем предыдущий поиск
        searchTask?.cancel()

        searchTask = Task {
            // Debounce
            try? await Task.sleep(for: .milliseconds(500))

            guard !Task.isCancelled else { return }

            loadingState = .loading

            do {
                let products = try await productService.search(query: query)

                guard !Task.isCancelled else { return }

                loadingState = .success(products)
            } catch {
                guard !Task.isCancelled else { return }
                loadingState = .failure(error)
            }
        }
    }

    // Параллельная загрузка нескольких ресурсов
    func loadProductDetails(productId: String) async throws -> (Product, [Review], [Product]) {
        async let product = productService.fetchProduct(id: productId)
        async let reviews = productService.fetchReviews(productId: productId)
        async let recommendations = productService.fetchRecommendations(productId: productId)

        // Все три запроса выполняются параллельно
        return try await (product, reviews, recommendations)
    }

    // Retry logic с exponential backoff
    func loadWithRetry(maxRetries: Int = 3) async {
        var retryCount = 0
        var lastError: Error?

        while retryCount < maxRetries {
            do {
                loadingState = .loading
                let products = try await productService.fetchProducts()
                loadingState = .success(products)
                return
            } catch {
                lastError = error
                retryCount += 1

                if retryCount < maxRetries {
                    let delay = TimeInterval(pow(2.0, Double(retryCount)))
                    try? await Task.sleep(for: .seconds(delay))
                }
            }
        }

        if let error = lastError {
            loadingState = .failure(error)
        }
    }
}

// ViewModel с TaskGroup для пакетных операций
@MainActor
class BatchUploadViewModel: ObservableObject {
    struct UploadItem: Identifiable {
        let id: UUID
        let filename: String
        var progress: Double
        var status: UploadStatus
    }

    enum UploadStatus {
        case pending
        case uploading
        case completed
        case failed(Error)
    }

    @Published var items: [UploadItem] = []
    @Published var overallProgress: Double = 0

    private let uploadService: UploadServiceProtocol

    init(uploadService: UploadServiceProtocol = UploadService()) {
        self.uploadService = uploadService
    }

    func uploadFiles(_ files: [URL]) async {
        items = files.map { url in
            UploadItem(
                id: UUID(),
                filename: url.lastPathComponent,
                progress: 0,
                status: .pending
            )
        }

        await withTaskGroup(of: (UUID, UploadStatus, Double).self) { group in
            for (index, file) in files.enumerated() {
                let itemId = items[index].id

                group.addTask {
                    do {
                        let progress = try await self.uploadService.upload(
                            file: file,
                            onProgress: { [weak self] progress in
                                Task { @MainActor in
                                    self?.updateProgress(itemId: itemId, progress: progress)
                                }
                            }
                        )
                        return (itemId, .completed, progress)
                    } catch {
                        return (itemId, .failed(error), 0)
                    }
                }
            }

            // Собираем результаты по мере завершения
            for await (itemId, status, progress) in group {
                updateItem(id: itemId, status: status, progress: progress)
                updateOverallProgress()
            }
        }
    }

    private func updateProgress(itemId: UUID, progress: Double) {
        guard let index = items.firstIndex(where: { $0.id == itemId }) else { return }
        items[index].progress = progress
        items[index].status = .uploading
        updateOverallProgress()
    }

    private func updateItem(id: UUID, status: UploadStatus, progress: Double) {
        guard let index = items.firstIndex(where: { $0.id == id }) else { return }
        items[index].status = status
        items[index].progress = progress
    }

    private func updateOverallProgress() {
        let totalProgress = items.reduce(0.0) { $0 + $1.progress }
        overallProgress = totalProgress / Double(items.count)
    }
}

// Использование в View
struct ProductListView: View {
    @StateObject private var viewModel = ProductListViewModel()

    var body: some View {
        Group {
            switch viewModel.loadingState {
            case .idle:
                Text("Pull to refresh")
            case .loading:
                ProgressView()
            case .success(let products):
                List(products) { product in
                    ProductRow(product: product)
                }
            case .failure(let error):
                VStack {
                    Text("Error: \(error.localizedDescription)")
                    Button("Retry") {
                        Task {
                            await viewModel.loadWithRetry()
                        }
                    }
                }
            }
        }
        .task {
            await viewModel.loadProducts()
        }
        .searchable(text: $viewModel.searchQuery)
        .onChange(of: viewModel.searchQuery) { _, newValue in
            viewModel.searchProducts(query: newValue)
        }
    }
}
```

### 7. State Machines в ViewModels

**Описание**: Использование конечных автоматов (state machines) для управления сложными состояниями и переходами в ViewModels. Обеспечивает предсказуемость и устраняет invalid states.

**Когда использовать**:
- Многоэтапные процессы (onboarding, checkout)
- Сложные загрузочные состояния
- Бизнес-процессы с четкими переходами

```swift
import SwiftUI

@MainActor
class CheckoutViewModel: ObservableObject {
    // Все возможные состояния checkout процесса
    enum State: Equatable {
        case idle
        case validatingCart
        case cartValid(items: [CartItem])
        case cartInvalid(reason: String)
        case processingPayment(items: [CartItem])
        case paymentAuthorizing
        case paymentSuccess(orderId: String)
        case paymentFailed(error: PaymentError)
        case completed(orderId: String)

        static func == (lhs: State, rhs: State) -> Bool {
            switch (lhs, rhs) {
            case (.idle, .idle),
                 (.validatingCart, .validatingCart),
                 (.paymentAuthorizing, .paymentAuthorizing):
                return true
            case (.cartValid(let l), .cartValid(let r)):
                return l.map(\.id) == r.map(\.id)
            case (.completed(let l), .completed(let r)),
                 (.paymentSuccess(let l), .paymentSuccess(let r)):
                return l == r
            default:
                return false
            }
        }
    }

    // События (triggers для переходов)
    enum Event {
        case startCheckout
        case cartValidated([CartItem])
        case cartValidationFailed(String)
        case initiatePayment
        case paymentAuthorized
        case paymentCompleted(orderId: String)
        case paymentRejected(PaymentError)
        case reset
    }

    struct CartItem: Identifiable {
        let id: String
        let name: String
        let price: Double
    }

    enum PaymentError: Error {
        case insufficientFunds
        case invalidCard
        case networkError
        case unknown
    }

    @Published private(set) var state: State = .idle

    private let cartService: CartServiceProtocol
    private let paymentService: PaymentServiceProtocol

    init(
        cartService: CartServiceProtocol = CartService(),
        paymentService: PaymentServiceProtocol = PaymentService()
    ) {
        self.cartService = cartService
        self.paymentService = paymentService
    }

    // Единая точка для всех переходов состояний
    func handle(event: Event) {
        let newState = reduce(currentState: state, event: event)

        guard newState != state else { return }

        state = newState
        performSideEffects(for: newState)
    }

    // Reducer - чистая функция для вычисления следующего состояния
    private func reduce(currentState: State, event: Event) -> State {
        switch (currentState, event) {
        // Idle -> Validating
        case (.idle, .startCheckout):
            return .validatingCart

        // Validating -> Valid/Invalid
        case (.validatingCart, .cartValidated(let items)):
            return .cartValid(items: items)
        case (.validatingCart, .cartValidationFailed(let reason)):
            return .cartInvalid(reason: reason)

        // Valid -> Processing
        case (.cartValid(let items), .initiatePayment):
            return .processingPayment(items: items)

        // Processing -> Authorizing
        case (.processingPayment, .paymentAuthorized):
            return .paymentAuthorizing

        // Authorizing -> Success/Failed
        case (.paymentAuthorizing, .paymentCompleted(let orderId)):
            return .paymentSuccess(orderId: orderId)
        case (.paymentAuthorizing, .paymentRejected(let error)):
            return .paymentFailed(error: error)

        // Success -> Completed
        case (.paymentSuccess(let orderId), _):
            return .completed(orderId: orderId)

        // Reset from any state
        case (_, .reset):
            return .idle

        // Invalid transitions - stay in current state
        default:
            print("Invalid transition from \(currentState) with event \(event)")
            return currentState
        }
    }

    // Side effects для каждого состояния
    private func performSideEffects(for state: State) {
        switch state {
        case .validatingCart:
            Task {
                do {
                    let items = try await cartService.validateCart()
                    handle(event: .cartValidated(items))
                } catch {
                    handle(event: .cartValidationFailed(error.localizedDescription))
                }
            }

        case .processingPayment(let items):
            Task {
                do {
                    try await paymentService.authorize(items: items)
                    handle(event: .paymentAuthorized)
                } catch let error as PaymentError {
                    handle(event: .paymentRejected(error))
                } catch {
                    handle(event: .paymentRejected(.unknown))
                }
            }

        case .paymentAuthorizing:
            Task {
                do {
                    let orderId = try await paymentService.completePayment()
                    handle(event: .paymentCompleted(orderId: orderId))
                } catch let error as PaymentError {
                    handle(event: .paymentRejected(error))
                } catch {
                    handle(event: .paymentRejected(.unknown))
                }
            }

        default:
            break
        }
    }

    // Helper properties для UI
    var canProceedToPayment: Bool {
        if case .cartValid = state {
            return true
        }
        return false
    }

    var isProcessing: Bool {
        switch state {
        case .validatingCart, .processingPayment, .paymentAuthorizing:
            return true
        default:
            return false
        }
    }
}

// View с type-safe state handling
struct CheckoutView: View {
    @StateObject private var viewModel = CheckoutViewModel()

    var body: some View {
        VStack(spacing: 20) {
            stateView
        }
        .padding()
        .onAppear {
            viewModel.handle(event: .startCheckout)
        }
    }

    @ViewBuilder
    private var stateView: some View {
        switch viewModel.state {
        case .idle:
            Text("Ready to checkout")

        case .validatingCart:
            ProgressView("Validating cart...")

        case .cartValid(let items):
            VStack {
                Text("Cart validated!")
                ForEach(items) { item in
                    Text("\(item.name): $\(item.price)")
                }
                Button("Proceed to Payment") {
                    viewModel.handle(event: .initiatePayment)
                }
            }

        case .cartInvalid(let reason):
            VStack {
                Text("Cart validation failed")
                    .foregroundColor(.red)
                Text(reason)
                    .font(.caption)
                Button("Try Again") {
                    viewModel.handle(event: .reset)
                }
            }

        case .processingPayment:
            ProgressView("Processing payment...")

        case .paymentAuthorizing:
            ProgressView("Authorizing payment...")

        case .paymentSuccess(let orderId):
            VStack {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.green)
                    .font(.system(size: 60))
                Text("Payment successful!")
                Text("Order ID: \(orderId)")
                    .font(.caption)
            }

        case .paymentFailed(let error):
            VStack {
                Image(systemName: "xmark.circle.fill")
                    .foregroundColor(.red)
                    .font(.system(size: 60))
                Text("Payment failed")
                Text(error.localizedDescription)
                    .font(.caption)
                Button("Try Again") {
                    viewModel.handle(event: .reset)
                }
            }

        case .completed(let orderId):
            VStack {
                Text("Order completed!")
                Text("Order ID: \(orderId)")
                Button("Start New Order") {
                    viewModel.handle(event: .reset)
                }
            }
        }
    }
}
```

### 8. Protocol-based ViewModels для тестирования

**Описание**: Использование protocols для определения интерфейса ViewModel, что упрощает тестирование через dependency injection и mock objects.

**Преимущества**:
- Легкое unit-тестирование
- Возможность создания preview providers
- Соответствие SOLID principles
- Гибкость в реализации

```swift
import SwiftUI
import Combine

// MARK: - Protocol Definition

protocol UserProfileViewModelProtocol: ObservableObject {
    var username: String { get set }
    var email: String { get set }
    var avatarURL: URL? { get set }
    var isLoading: Bool { get }
    var errorMessage: String? { get }

    func loadProfile() async
    func updateProfile(name: String, email: String) async throws
    func uploadAvatar(_ image: Data) async throws
}

// MARK: - Production Implementation

@MainActor
class UserProfileViewModel: UserProfileViewModelProtocol {
    @Published var username: String = ""
    @Published var email: String = ""
    @Published var avatarURL: URL?
    @Published private(set) var isLoading: Bool = false
    @Published private(set) var errorMessage: String?

    private let userService: UserServiceProtocol
    private let imageService: ImageServiceProtocol

    init(
        userService: UserServiceProtocol = UserService(),
        imageService: ImageServiceProtocol = ImageService()
    ) {
        self.userService = userService
        self.imageService = imageService
    }

    func loadProfile() async {
        isLoading = true
        errorMessage = nil

        do {
            let user = try await userService.fetchCurrentUser()
            username = user.name
            email = user.email
            avatarURL = user.avatarURL
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }

    func updateProfile(name: String, email: String) async throws {
        isLoading = true
        defer { isLoading = false }

        try await userService.updateProfile(name: name, email: email)
        username = name
        self.email = email
    }

    func uploadAvatar(_ image: Data) async throws {
        isLoading = true
        defer { isLoading = false }

        let url = try await imageService.upload(image)
        avatarURL = url
    }
}

// MARK: - Mock для тестирования

@MainActor
class MockUserProfileViewModel: UserProfileViewModelProtocol {
    @Published var username: String = ""
    @Published var email: String = ""
    @Published var avatarURL: URL?
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?

    var loadProfileCalled = false
    var updateProfileCalled = false
    var uploadAvatarCalled = false

    var shouldFailLoad = false
    var shouldFailUpdate = false

    func loadProfile() async {
        loadProfileCalled = true
        isLoading = true

        try? await Task.sleep(for: .seconds(1))

        if shouldFailLoad {
            errorMessage = "Failed to load profile"
        } else {
            username = "Test User"
            email = "test@example.com"
            avatarURL = URL(string: "https://example.com/avatar.jpg")
        }

        isLoading = false
    }

    func updateProfile(name: String, email: String) async throws {
        updateProfileCalled = true
        isLoading = true

        try await Task.sleep(for: .seconds(1))

        if shouldFailUpdate {
            throw NSError(domain: "Test", code: -1)
        }

        username = name
        self.email = email
        isLoading = false
    }

    func uploadAvatar(_ image: Data) async throws {
        uploadAvatarCalled = true
        isLoading = true

        try await Task.sleep(for: .seconds(1))

        avatarURL = URL(string: "https://example.com/new-avatar.jpg")
        isLoading = false
    }
}

// MARK: - Generic View с protocol

struct UserProfileView<ViewModel: UserProfileViewModelProtocol>: View {
    @ObservedObject var viewModel: ViewModel
    @State private var editedName = ""
    @State private var editedEmail = ""
    @State private var isEditing = false

    var body: some View {
        VStack(spacing: 20) {
            if viewModel.isLoading {
                ProgressView()
            } else {
                if let avatarURL = viewModel.avatarURL {
                    AsyncImage(url: avatarURL) { image in
                        image
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                    } placeholder: {
                        ProgressView()
                    }
                    .frame(width: 100, height: 100)
                    .clipShape(Circle())
                }

                if isEditing {
                    TextField("Name", text: $editedName)
                    TextField("Email", text: $editedEmail)

                    Button("Save") {
                        Task {
                            try? await viewModel.updateProfile(
                                name: editedName,
                                email: editedEmail
                            )
                            isEditing = false
                        }
                    }
                } else {
                    Text(viewModel.username)
                        .font(.headline)
                    Text(viewModel.email)
                        .font(.subheadline)

                    Button("Edit") {
                        editedName = viewModel.username
                        editedEmail = viewModel.email
                        isEditing = true
                    }
                }

                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                }
            }
        }
        .padding()
        .task {
            await viewModel.loadProfile()
        }
    }
}

// MARK: - Unit Tests

import XCTest

@MainActor
class UserProfileViewModelTests: XCTestCase {
    var sut: MockUserProfileViewModel!

    override func setUp() {
        super.setUp()
        sut = MockUserProfileViewModel()
    }

    override func tearDown() {
        sut = nil
        super.tearDown()
    }

    func testLoadProfileSuccess() async {
        // Given
        sut.shouldFailLoad = false

        // When
        await sut.loadProfile()

        // Then
        XCTAssertTrue(sut.loadProfileCalled)
        XCTAssertEqual(sut.username, "Test User")
        XCTAssertEqual(sut.email, "test@example.com")
        XCTAssertNil(sut.errorMessage)
        XCTAssertFalse(sut.isLoading)
    }

    func testLoadProfileFailure() async {
        // Given
        sut.shouldFailLoad = true

        // When
        await sut.loadProfile()

        // Then
        XCTAssertTrue(sut.loadProfileCalled)
        XCTAssertNotNil(sut.errorMessage)
        XCTAssertFalse(sut.isLoading)
    }

    func testUpdateProfile() async throws {
        // Given
        let newName = "Updated Name"
        let newEmail = "updated@example.com"

        // When
        try await sut.updateProfile(name: newName, email: newEmail)

        // Then
        XCTAssertTrue(sut.updateProfileCalled)
        XCTAssertEqual(sut.username, newName)
        XCTAssertEqual(sut.email, newEmail)
    }
}

// MARK: - Preview Provider

#Preview("Success State") {
    let viewModel = MockUserProfileViewModel()
    return UserProfileView(viewModel: viewModel)
        .task {
            await viewModel.loadProfile()
        }
}

#Preview("Error State") {
    let viewModel = MockUserProfileViewModel()
    viewModel.shouldFailLoad = true
    return UserProfileView(viewModel: viewModel)
        .task {
            await viewModel.loadProfile()
        }
}

#Preview("Loading State") {
    let viewModel = MockUserProfileViewModel()
    viewModel.isLoading = true
    return UserProfileView(viewModel: viewModel)
}
```

### 9. ViewModel Scoping и Lifecycle

**Описание**: Управление жизненным циклом ViewModels и правильное использование property wrappers (@StateObject, @ObservedObject, @EnvironmentObject) для контроля scope и ownership.

**Property Wrappers**:
- @StateObject: View владеет ViewModel (создание)
- @ObservedObject: View наблюдает за ViewModel (передача)
- @EnvironmentObject: Глобальный доступ к ViewModel

```swift
import SwiftUI

// MARK: - Root Level ViewModel (App-wide state)

@MainActor
class AppViewModel: ObservableObject {
    @Published var isAuthenticated = false
    @Published var currentUser: User?
    @Published var theme: Theme = .light

    struct User {
        let id: String
        let name: String
        let email: String
    }

    enum Theme {
        case light, dark
    }

    func login(email: String, password: String) async throws {
        // Login logic
        isAuthenticated = true
        currentUser = User(id: "123", name: "John", email: email)
    }

    func logout() {
        isAuthenticated = false
        currentUser = nil
    }
}

// MARK: - Screen Level ViewModel

@MainActor
class HomeViewModel: ObservableObject {
    @Published var posts: [Post] = []
    @Published var isLoading = false

    struct Post: Identifiable {
        let id: String
        let title: String
        let content: String
    }

    private let postService: PostServiceProtocol

    init(postService: PostServiceProtocol = PostService()) {
        self.postService = postService
        print("HomeViewModel initialized")
    }

    deinit {
        print("HomeViewModel deinitialized")
    }

    func loadPosts() async {
        isLoading = true
        defer { isLoading = false }

        do {
            posts = try await postService.fetchPosts()
        } catch {
            print("Failed to load posts: \(error)")
        }
    }
}

// MARK: - Component Level ViewModel

@MainActor
class PostCellViewModel: ObservableObject {
    @Published var isLiked = false
    @Published var likeCount = 0

    private let postId: String
    private let likeService: LikeServiceProtocol

    init(postId: String, likeService: LikeServiceProtocol = LikeService()) {
        self.postId = postId
        self.likeService = likeService
    }

    func toggleLike() async {
        isLiked.toggle()
        likeCount += isLiked ? 1 : -1

        do {
            if isLiked {
                try await likeService.like(postId: postId)
            } else {
                try await likeService.unlike(postId: postId)
            }
        } catch {
            // Revert on error
            isLiked.toggle()
            likeCount += isLiked ? 1 : -1
        }
    }
}

// MARK: - App Structure с правильным scoping

@main
struct MyApp: App {
    // App-level: используем @StateObject для создания
    @StateObject private var appViewModel = AppViewModel()

    var body: some Scene {
        WindowGroup {
            if appViewModel.isAuthenticated {
                MainTabView()
                    .environmentObject(appViewModel) // Передаем в environment
            } else {
                LoginView()
                    .environmentObject(appViewModel)
            }
        }
    }
}

struct MainTabView: View {
    // Access app-level ViewModel через @EnvironmentObject
    @EnvironmentObject private var appViewModel: AppViewModel

    var body: some View {
        TabView {
            HomeView()
                .tabItem { Label("Home", systemImage: "house") }

            ProfileView()
                .tabItem { Label("Profile", systemImage: "person") }
        }
    }
}

struct HomeView: View {
    // Screen-level: View владеет ViewModel
    @StateObject private var viewModel = HomeViewModel()

    var body: some View {
        NavigationStack {
            List(viewModel.posts) { post in
                NavigationLink(value: post) {
                    // Передаем ViewModel в дочерний компонент
                    PostRowView(post: post)
                }
            }
            .navigationDestination(for: HomeViewModel.Post.self) { post in
                PostDetailView(post: post)
            }
            .task {
                await viewModel.loadPosts()
            }
        }
    }
}

struct PostRowView: View {
    let post: HomeViewModel.Post

    // Component-level: создаем для каждой ячейки
    @StateObject private var viewModel: PostCellViewModel

    init(post: HomeViewModel.Post) {
        self.post = post
        // ВАЖНО: инициализация @StateObject через init
        _viewModel = StateObject(wrappedValue: PostCellViewModel(postId: post.id))
    }

    var body: some View {
        HStack {
            VStack(alignment: .leading) {
                Text(post.title)
                    .font(.headline)
                Text(post.content)
                    .font(.body)
            }

            Spacer()

            Button {
                Task {
                    await viewModel.toggleLike()
                }
            } label: {
                Image(systemName: viewModel.isLiked ? "heart.fill" : "heart")
                    .foregroundColor(viewModel.isLiked ? .red : .gray)
                Text("\(viewModel.likeCount)")
            }
        }
    }
}

// MARK: - Передача ViewModel через Navigation

struct PostDetailView: View {
    let post: HomeViewModel.Post

    // Screen-level ViewModel для детального экрана
    @StateObject private var viewModel: PostDetailViewModel

    init(post: HomeViewModel.Post) {
        self.post = post
        _viewModel = StateObject(wrappedValue: PostDetailViewModel(postId: post.id))
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text(post.title)
                    .font(.largeTitle)

                Text(post.content)
                    .font(.body)

                if viewModel.isLoading {
                    ProgressView()
                } else {
                    CommentsSection(comments: viewModel.comments)
                }
            }
            .padding()
        }
        .task {
            await viewModel.loadComments()
        }
    }
}

@MainActor
class PostDetailViewModel: ObservableObject {
    @Published var comments: [Comment] = []
    @Published var isLoading = false

    struct Comment: Identifiable {
        let id: String
        let text: String
    }

    private let postId: String

    init(postId: String) {
        self.postId = postId
        print("PostDetailViewModel initialized for post: \(postId)")
    }

    deinit {
        print("PostDetailViewModel deinitialized")
    }

    func loadComments() async {
        isLoading = true
        defer { isLoading = false }

        // Load comments logic
    }
}

struct CommentsSection: View {
    let comments: [PostDetailViewModel.Comment]

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            Text("Comments")
                .font(.headline)

            ForEach(comments) { comment in
                Text(comment.text)
                    .padding()
                    .background(Color.gray.opacity(0.1))
                    .cornerRadius(8)
            }
        }
    }
}

// MARK: - Child View с @ObservedObject (не владеет)

struct UserAvatarView: View {
    // Используем @ObservedObject, потому что родитель передает ViewModel
    @ObservedObject var viewModel: UserAvatarViewModel

    var body: some View {
        AsyncImage(url: viewModel.avatarURL) { image in
            image
                .resizable()
                .aspectRatio(contentMode: .fill)
        } placeholder: {
            ProgressView()
        }
        .frame(width: 50, height: 50)
        .clipShape(Circle())
    }
}

@MainActor
class UserAvatarViewModel: ObservableObject {
    @Published var avatarURL: URL?

    init(userId: String) {
        // Load avatar
    }
}

struct ProfileView: View {
    @EnvironmentObject private var appViewModel: AppViewModel
    // Владелец ViewModel для аватара
    @StateObject private var avatarViewModel: UserAvatarViewModel

    init() {
        // НЕЛЬЗЯ использовать appViewModel здесь - он еще не доступен
        // Поэтому используем onAppear или передаем userId через другой путь
        _avatarViewModel = StateObject(wrappedValue: UserAvatarViewModel(userId: "temp"))
    }

    var body: some View {
        VStack {
            // Передаем ViewModel как @ObservedObject
            UserAvatarView(viewModel: avatarViewModel)

            if let user = appViewModel.currentUser {
                Text(user.name)
                    .font(.headline)
                Text(user.email)
                    .font(.subheadline)
            }

            Button("Logout") {
                appViewModel.logout()
            }
        }
    }
}
```

### 10. ViewModelProvider Patterns

**Описание**: Продвинутые паттерны для создания, кеширования и предоставления ViewModels через dependency injection и factory patterns.

**Применение**:
- Централизованное управление зависимостями
- Тестирование с mock dependencies
- Кеширование ViewModels для performance

```swift
import SwiftUI

// MARK: - Dependency Container

@MainActor
class DependencyContainer {
    static let shared = DependencyContainer()

    // Services
    private(set) lazy var authService: AuthServiceProtocol = AuthService()
    private(set) lazy var userService: UserServiceProtocol = UserService()
    private(set) lazy var postService: PostServiceProtocol = PostService()

    // ViewModel factory methods
    func makeLoginViewModel() -> LoginViewModel {
        LoginViewModel(authService: authService)
    }

    func makeHomeViewModel() -> HomeViewModel {
        HomeViewModel(postService: postService, userService: userService)
    }

    func makeProfileViewModel(userId: String) -> ProfileViewModel {
        ProfileViewModel(userId: userId, userService: userService)
    }

    // Mock container для тестов и previews
    static func mock() -> DependencyContainer {
        let container = DependencyContainer()
        container.authService = MockAuthService()
        container.userService = MockUserService()
        container.postService = MockPostService()
        return container
    }

    private init() {}
}

// MARK: - Environment Key для Dependency Injection

struct DependencyContainerKey: EnvironmentKey {
    static let defaultValue: DependencyContainer = .shared
}

extension EnvironmentValues {
    var dependencies: DependencyContainer {
        get { self[DependencyContainerKey.self] }
        set { self[DependencyContainerKey.self] = newValue }
    }
}

// MARK: - ViewModelProvider Protocol

protocol ViewModelProvider {
    associatedtype ViewModel: ObservableObject
    func makeViewModel() -> ViewModel
}

// MARK: - Generic View с Provider

struct ProviderView<Provider: ViewModelProvider, Content: View>: View {
    @StateObject private var viewModel: Provider.ViewModel
    private let content: (Provider.ViewModel) -> Content

    init(
        provider: Provider,
        @ViewBuilder content: @escaping (Provider.ViewModel) -> Content
    ) {
        _viewModel = StateObject(wrappedValue: provider.makeViewModel())
        self.content = content
    }

    var body: some View {
        content(viewModel)
    }
}

// MARK: - Concrete Provider Implementation

struct HomeViewProvider: ViewModelProvider {
    let dependencies: DependencyContainer

    func makeViewModel() -> HomeViewModel {
        dependencies.makeHomeViewModel()
    }
}

@MainActor
class HomeViewModel: ObservableObject {
    @Published var posts: [Post] = []

    struct Post: Identifiable {
        let id: String
        let title: String
    }

    private let postService: PostServiceProtocol
    private let userService: UserServiceProtocol

    init(postService: PostServiceProtocol, userService: UserServiceProtocol) {
        self.postService = postService
        self.userService = userService
    }

    func loadPosts() async {
        // Load logic
    }
}

// MARK: - Usage в View

struct HomeView: View {
    @Environment(\.dependencies) private var dependencies

    var body: some View {
        ProviderView(provider: HomeViewProvider(dependencies: dependencies)) { viewModel in
            List(viewModel.posts) { post in
                Text(post.title)
            }
            .task {
                await viewModel.loadPosts()
            }
        }
    }
}

// MARK: - Cached ViewModel Provider

@MainActor
class CachedViewModelProvider {
    static let shared = CachedViewModelProvider()

    private var cache: [String: Any] = [:]

    func viewModel<T: ObservableObject>(
        key: String,
        factory: () -> T
    ) -> T {
        if let cached = cache[key] as? T {
            return cached
        }

        let newViewModel = factory()
        cache[key] = newViewModel
        return newViewModel
    }

    func clearCache() {
        cache.removeAll()
    }

    func removeViewModel(key: String) {
        cache.removeValue(forKey: key)
    }

    private init() {}
}

// MARK: - Cached ViewModel View Modifier

struct CachedViewModel<ViewModel: ObservableObject>: ViewModifier {
    let key: String
    let factory: () -> ViewModel

    @StateObject private var viewModel: ViewModel

    init(key: String, factory: @escaping () -> ViewModel) {
        self.key = key
        self.factory = factory
        _viewModel = StateObject(wrappedValue: CachedViewModelProvider.shared.viewModel(
            key: key,
            factory: factory
        ))
    }

    func body(content: Content) -> some View {
        content
            .environmentObject(viewModel)
    }
}

extension View {
    func cachedViewModel<ViewModel: ObservableObject>(
        key: String,
        factory: @escaping () -> ViewModel
    ) -> some View {
        modifier(CachedViewModel(key: key, factory: factory))
    }
}

// MARK: - Example Usage

struct UserProfileView: View {
    let userId: String
    @EnvironmentObject var viewModel: ProfileViewModel

    var body: some View {
        VStack {
            Text(viewModel.username)
        }
        .task {
            await viewModel.loadProfile()
        }
    }
}

struct ProfileContainerView: View {
    let userId: String
    @Environment(\.dependencies) private var dependencies

    var body: some View {
        UserProfileView(userId: userId)
            .cachedViewModel(key: "profile_\(userId)") {
                dependencies.makeProfileViewModel(userId: userId)
            }
    }
}

@MainActor
class ProfileViewModel: ObservableObject {
    @Published var username: String = ""

    private let userId: String
    private let userService: UserServiceProtocol

    init(userId: String, userService: UserServiceProtocol) {
        self.userId = userId
        self.userService = userService
    }

    func loadProfile() async {
        // Load logic
    }
}

// MARK: - App Setup с DI

@main
struct MyApp: App {
    // Production container
    let dependencies = DependencyContainer.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.dependencies, dependencies)
        }
    }
}

// MARK: - Preview с Mock Container

#Preview {
    HomeView()
        .environment(\.dependencies, .mock())
}

// MARK: - Service Protocols

protocol AuthServiceProtocol {
    func login(email: String, password: String) async throws
}

protocol UserServiceProtocol {
    func fetchUser(id: String) async throws -> User
}

protocol PostServiceProtocol {
    func fetchPosts() async throws -> [HomeViewModel.Post]
}

struct User {
    let id: String
    let name: String
}

// MARK: - Mock Services

class MockAuthService: AuthServiceProtocol {
    func login(email: String, password: String) async throws {}
}

class MockUserService: UserServiceProtocol {
    func fetchUser(id: String) async throws -> User {
        User(id: id, name: "Mock User")
    }
}

class MockPostService: PostServiceProtocol {
    func fetchPosts() async throws -> [HomeViewModel.Post] {
        [
            HomeViewModel.Post(id: "1", title: "Mock Post 1"),
            HomeViewModel.Post(id: "2", title: "Mock Post 2")
        ]
    }
}

// Real implementations
class AuthService: AuthServiceProtocol {
    func login(email: String, password: String) async throws {}
}

class UserService: UserServiceProtocol {
    func fetchUser(id: String) async throws -> User {
        User(id: id, name: "Real User")
    }
}

class PostService: PostServiceProtocol {
    func fetchPosts() async throws -> [HomeViewModel.Post] { [] }
}

@MainActor
class LoginViewModel: ObservableObject {
    private let authService: AuthServiceProtocol

    init(authService: AuthServiceProtocol) {
        self.authService = authService
    }
}
```

## 6 типичных ошибок

### Ошибка 1: Неправильное использование @StateObject vs @ObservedObject

**Проблема**: Использование @ObservedObject там, где нужен @StateObject приводит к пересозданию ViewModel при каждой перерисовке View.

❌ **Неправильно**:
```swift
struct ContentView: View {
    // ViewModel будет пересоздаваться при каждом обновлении View!
    @ObservedObject var viewModel = ContentViewModel()

    var body: some View {
        Text(viewModel.title)
    }
}
```

✅ **Правильно**:
```swift
struct ContentView: View {
    // View владеет lifecycle ViewModel
    @StateObject private var viewModel = ContentViewModel()

    var body: some View {
        Text(viewModel.title)
    }
}

// ИЛИ используйте @ObservedObject когда ViewModel передается извне
struct DetailView: View {
    @ObservedObject var viewModel: DetailViewModel

    init(viewModel: DetailViewModel) {
        self.viewModel = viewModel
    }

    var body: some View {
        Text(viewModel.content)
    }
}

struct ParentView: View {
    @StateObject private var detailViewModel = DetailViewModel()

    var body: some View {
        DetailView(viewModel: detailViewModel)
    }
}
```

### Ошибка 2: Забытая main thread изоляция для UI updates

**Проблема**: Обновление @Published свойств из background thread вызывает runtime warnings и потенциальные crashes.

❌ **Неправильно**:
```swift
class DataViewModel: ObservableObject {
    @Published var data: [String] = []

    func loadData() {
        Task {
            let result = try await fetchData() // background thread
            // UI UPDATE НЕ НА MAIN THREAD!
            self.data = result
        }
    }
}
```

✅ **Правильно**:
```swift
@MainActor
class DataViewModel: ObservableObject {
    @Published var data: [String] = []

    // Весь класс на MainActor - автоматическая изоляция
    func loadData() async {
        let result = try await fetchData()
        data = result // гарантированно на main thread
    }
}

// ИЛИ явное переключение на main thread
class DataViewModel: ObservableObject {
    @Published var data: [String] = []

    func loadData() {
        Task {
            let result = try await fetchData()

            await MainActor.run {
                self.data = result
            }
        }
    }
}
```

### Ошибка 3: Memory leaks через retain cycles

**Проблема**: Strong references в closures создают retain cycles, предотвращающие деинициализацию ViewModel.

❌ **Неправильно**:
```swift
class SearchViewModel: ObservableObject {
    @Published var results: [String] = []
    private var cancellables = Set<AnyCancellable>()

    func setupSearch() {
        $searchQuery
            .debounce(for: .seconds(0.5), scheduler: RunLoop.main)
            .sink { query in
                // RETAIN CYCLE! Strong reference на self
                self.performSearch(query)
            }
            .store(in: &cancellables)
    }
}
```

✅ **Правильно**:
```swift
class SearchViewModel: ObservableObject {
    @Published var searchQuery: String = ""
    @Published var results: [String] = []
    private var cancellables = Set<AnyCancellable>()

    func setupSearch() {
        $searchQuery
            .debounce(for: .seconds(0.5), scheduler: RunLoop.main)
            .sink { [weak self] query in
                // Используем weak self
                self?.performSearch(query)
            }
            .store(in: &cancellables)
    }

    private func performSearch(_ query: String) {
        // Search logic
    }
}

// ИЛИ используйте unowned если уверены что self не будет nil
class TimerViewModel: ObservableObject {
    @Published var counter = 0
    private var cancellables = Set<AnyCancellable>()

    func startTimer() {
        Timer.publish(every: 1, on: .main, in: .common)
            .autoconnect()
            .sink { [unowned self] _ in
                // unowned если Timer всегда отменяется до deinit
                self.counter += 1
            }
            .store(in: &cancellables)
    }
}
```

### Ошибка 4: Не отменяются Task при деинициализации

**Проблема**: Незаконченные Task продолжают выполняться после того, как View исчез, вызывая ненужные обновления и возможные crashes.

❌ **Неправильно**:
```swift
@MainActor
class ImageListViewModel: ObservableObject {
    @Published var images: [UIImage] = []

    func loadImages() {
        Task {
            for i in 1...100 {
                // Если View закрыта, Task продолжает загружать изображения!
                let image = try await downloadImage(id: i)
                images.append(image)
            }
        }
    }
}
```

✅ **Правильно**:
```swift
@MainActor
class ImageListViewModel: ObservableObject {
    @Published var images: [UIImage] = []
    private var loadTask: Task<Void, Never>?

    func loadImages() {
        // Отменяем предыдущий Task
        loadTask?.cancel()

        loadTask = Task {
            for i in 1...100 {
                // Проверяем cancellation
                if Task.isCancelled { break }

                do {
                    let image = try await downloadImage(id: i)

                    if Task.isCancelled { break }

                    images.append(image)
                } catch {
                    break
                }
            }
        }
    }

    deinit {
        loadTask?.cancel()
    }
}

// ИЛИ используйте .task modifier в View
struct ImageListView: View {
    @StateObject private var viewModel = ImageListViewModel()

    var body: some View {
        List(viewModel.images, id: \.self) { image in
            Image(uiImage: image)
        }
        .task {
            // Автоматическая отмена при disappear
            await viewModel.loadImages()
        }
    }
}

@MainActor
class ImageListViewModel: ObservableObject {
    @Published var images: [UIImage] = []

    func loadImages() async {
        for i in 1...100 {
            if Task.isCancelled { break }

            do {
                let image = try await downloadImage(id: i)
                images.append(image)
            } catch {
                break
            }
        }
    }
}
```

### Ошибка 5: Излишне детализированные @Published свойства

**Проблема**: Каждое изменение @Published свойства триггерит перерисовку всей View, даже если изменилась только одна часть состояния.

❌ **Неправильно**:
```swift
class FormViewModel: ObservableObject {
    // Каждое изменение любого поля перерисовывает всю форму
    @Published var firstName: String = ""
    @Published var lastName: String = ""
    @Published var email: String = ""
    @Published var phone: String = ""
    @Published var address: String = ""
    @Published var city: String = ""
    @Published var zipCode: String = ""
    // ... 20 полей
}

struct FormView: View {
    @StateObject var viewModel = FormViewModel()

    var body: some View {
        // Вся форма перерисовывается при изменении любого поля!
        Form {
            TextField("First Name", text: $viewModel.firstName)
            TextField("Last Name", text: $viewModel.lastName)
            TextField("Email", text: $viewModel.email)
            // ... 20 полей
        }
    }
}
```

✅ **Правильно**:
```swift
// Подход 1: Группировка в структуры
class FormViewModel: ObservableObject {
    struct PersonalInfo {
        var firstName: String = ""
        var lastName: String = ""
        var email: String = ""
    }

    struct AddressInfo {
        var address: String = ""
        var city: String = ""
        var zipCode: String = ""
    }

    @Published var personalInfo = PersonalInfo()
    @Published var addressInfo = AddressInfo()
}

// Подход 2: Использование @Observable (iOS 17+)
@Observable
class FormViewModel {
    var firstName: String = ""
    var lastName: String = ""
    var email: String = ""

    // Только Views, использующие конкретное свойство, обновятся
}

// Подход 3: Local State для frequently changing values
struct FormView: View {
    @StateObject var viewModel = FormViewModel()

    // Local state для input
    @State private var firstNameInput = ""
    @State private var lastNameInput = ""

    var body: some View {
        Form {
            TextField("First Name", text: $firstNameInput)
                .onChange(of: firstNameInput) { _, newValue in
                    // Debounced update к ViewModel
                    updateFirstName(newValue)
                }

            Button("Submit") {
                viewModel.submit(
                    firstName: firstNameInput,
                    lastName: lastNameInput
                )
            }
        }
    }

    private func updateFirstName(_ value: String) {
        // Debounce logic
    }
}
```

### Ошибка 6: Бизнес-логика в View вместо ViewModel

**Проблема**: Размещение бизнес-логики напрямую в View делает код нетестируемым и нарушает separation of concerns.

❌ **Неправильно**:
```swift
struct ProductListView: View {
    @State private var products: [Product] = []
    @State private var filteredProducts: [Product] = []
    @State private var searchText = ""
    @State private var selectedCategory: Category?
    @State private var sortOrder: SortOrder = .nameAscending

    var body: some View {
        List(filteredProducts) { product in
            ProductRow(product: product)
        }
        .searchable(text: $searchText)
        .onChange(of: searchText) { _, newValue in
            // БИЗНЕС-ЛОГИКА В VIEW!
            filteredProducts = products.filter { product in
                product.name.localizedCaseInsensitiveContains(newValue)
            }

            if let category = selectedCategory {
                filteredProducts = filteredProducts.filter {
                    $0.category == category
                }
            }

            filteredProducts.sort {
                switch sortOrder {
                case .nameAscending:
                    return $0.name < $1.name
                case .nameDescending:
                    return $0.name > $1.name
                case .priceAscending:
                    return $0.price < $1.price
                case .priceDescending:
                    return $0.price > $1.price
                }
            }
        }
        .task {
            // API CALL В VIEW!
            do {
                let response = try await URLSession.shared.data(
                    from: URL(string: "https://api.example.com/products")!
                )
                products = try JSONDecoder().decode([Product].self, from: response.0)
            } catch {
                print(error)
            }
        }
    }
}
```

✅ **Правильно**:
```swift
@MainActor
class ProductListViewModel: ObservableObject {
    @Published var products: [Product] = []
    @Published var searchText = ""
    @Published var selectedCategory: Category?
    @Published var sortOrder: SortOrder = .nameAscending

    // Computed property для filtered/sorted результатов
    var displayedProducts: [Product] {
        var result = products

        // Filter by search
        if !searchText.isEmpty {
            result = result.filter {
                $0.name.localizedCaseInsensitiveContains(searchText)
            }
        }

        // Filter by category
        if let category = selectedCategory {
            result = result.filter { $0.category == category }
        }

        // Sort
        result.sort { lhs, rhs in
            switch sortOrder {
            case .nameAscending:
                return lhs.name < rhs.name
            case .nameDescending:
                return lhs.name > rhs.name
            case .priceAscending:
                return lhs.price < rhs.price
            case .priceDescending:
                return lhs.price > rhs.price
            }
        }

        return result
    }

    private let productService: ProductServiceProtocol

    init(productService: ProductServiceProtocol = ProductService()) {
        self.productService = productService
    }

    func loadProducts() async {
        do {
            products = try await productService.fetchProducts()
        } catch {
            // Proper error handling
            print("Failed to load products: \(error)")
        }
    }
}

struct ProductListView: View {
    @StateObject private var viewModel = ProductListViewModel()

    var body: some View {
        List(viewModel.displayedProducts) { product in
            ProductRow(product: product)
        }
        .searchable(text: $viewModel.searchText)
        .toolbar {
            Picker("Category", selection: $viewModel.selectedCategory) {
                // Category options
            }

            Picker("Sort", selection: $viewModel.sortOrder) {
                // Sort options
            }
        }
        .task {
            await viewModel.loadProducts()
        }
    }
}

// Легко тестируется
class ProductListViewModelTests: XCTestCase {
    @MainActor
    func testFilterBySearchText() async {
        let mockService = MockProductService()
        let viewModel = ProductListViewModel(productService: mockService)

        await viewModel.loadProducts()
        viewModel.searchText = "iPhone"

        XCTAssertTrue(viewModel.displayedProducts.allSatisfy {
            $0.name.contains("iPhone")
        })
    }
}

struct Product: Identifiable {
    let id: String
    let name: String
    let price: Double
    let category: Category
}

enum Category {
    case electronics, clothing
}

enum SortOrder {
    case nameAscending, nameDescending, priceAscending, priceDescending
}

protocol ProductServiceProtocol {
    func fetchProducts() async throws -> [Product]
}

class ProductService: ProductServiceProtocol {
    func fetchProducts() async throws -> [Product] {
        []
    }
}

class MockProductService: ProductServiceProtocol {
    func fetchProducts() async throws -> [Product] {
        []
    }
}

struct ProductRow: View {
    let product: Product
    var body: some View { Text(product.name) }
}
```

## Related Notes

- [[android-viewmodel-internals]] - Сравнение с Android ViewModel архитектурой
- [[swiftui-state-management]] - Управление состоянием в SwiftUI
- [[combine-framework-patterns]] - Reactive programming с Combine
- [[swift-concurrency-async-await]] - Modern concurrency в Swift
- [[mvvm-architecture-ios]] - MVVM архитектурный паттерн
- [[dependency-injection-ios]] - DI patterns для iOS
