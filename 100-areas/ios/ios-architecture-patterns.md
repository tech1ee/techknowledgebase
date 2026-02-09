---
title: "Архитектурные паттерны iOS"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/architecture
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-architecture-patterns]]"
  - "[[ios-overview]]"
---

# iOS Architecture Patterns

## TL;DR

Архитектурные паттерны iOS определяют структуру приложения и распределение ответственности между компонентами. От простого MVC (Model-View-Controller) до сложных VIPER и TCA (The Composable Architecture) — выбор зависит от размера команды, сложности приложения и требований к тестируемости. MVVM стал де-факто стандартом для SwiftUI благодаря нативной поддержке реактивности через Combine и @Published. Clean Architecture обеспечивает максимальную независимость слоев, а TCA предлагает функциональный подход с однонаправленным потоком данных.

## Аналогии

### MVC — это кухня небольшого ресторана
Шеф-повар (Controller) принимает заказы, готовит блюда (Model) и сервирует их на тарелки (View). Когда ресторан маленький — все работает. Но при масштабировании шеф перегружен: он и заказы принимает, и готовит, и моет посуду. Получается "Massive View Controller".

### MVVM — это ресторан с су-шефом
Су-шеф (ViewModel) готовит ингредиенты и полуфабрикаты, а официант (View) только подает готовые блюда. Шеф-повар (Controller) больше не перегружен, а кухня работает эффективнее благодаря четкому разделению обязанностей.

### VIPER — это сетевой ресторан с корпоративными стандартами
У каждого сотрудника строго определенная роль: менеджер зала (Router), администратор (Presenter), повар (Interactor), кладовщик (Entity), официант (View). Много бюрократии, но система масштабируется и легко добавлять новые филиалы.

### Clean Architecture — это слоеный пирог
Каждый слой (Domain, Data, Presentation) независим и может быть заменен без влияния на другие. Начинка (бизнес-логика) не знает о глазури (UI) и может существовать отдельно.

### TCA — это конвейер на фабрике
Все действия (Actions) движутся в одном направлении через редьюсер (Reducer), который изменяет состояние (State). Предсказуемо, тестируемо, но требует понимания функционального программирования.

## Диаграммы

```
┌─────────────────────────────────────────────────────────────┐
│                         MVC Pattern                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│         ┌──────────┐         ┌───────────────┐              │
│         │  Model   │◄────────│  Controller   │              │
│         └────┬─────┘         └───────┬───────┘              │
│              │                       │                       │
│              │ notify                │ updates               │
│              │                       │                       │
│              ▼                       ▼                       │
│         ┌──────────────────────────────┐                    │
│         │           View               │                    │
│         └──────────────────────────────┘                    │
│                                                              │
│  Проблема: Controller знает обо всем, тестирование сложное  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                        MVVM Pattern                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│    ┌──────────┐         ┌──────────┐         ┌──────────┐   │
│    │  Model   │◄────────│ViewModel │◄────────│   View   │   │
│    └──────────┘         └────┬─────┘         └──────────┘   │
│                              │                               │
│                              │ Data Binding                  │
│                              │ (@Published, Combine)         │
│                              ▼                               │
│                   Reactive Updates (SwiftUI)                 │
│                                                              │
│  Преимущество: ViewModel тестируется изолированно от UI     │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                       VIPER Pattern                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐      ┌───────────┐      ┌──────────────┐     │
│  │   View   │◄────►│ Presenter │◄────►│  Interactor  │     │
│  └────┬─────┘      └─────┬─────┘      └──────┬───────┘     │
│       │                  │                    │             │
│       │                  │                    ▼             │
│       │                  │              ┌──────────┐        │
│       │                  │              │  Entity  │        │
│       │                  │              └──────────┘        │
│       │                  │                                  │
│       │            ┌─────▼──────┐                           │
│       └───────────►│   Router   │                           │
│                    └────────────┘                           │
│                                                              │
│  Модульность: каждый компонент с одной ответственностью    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Clean Architecture                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Presentation Layer                     │    │
│  │         (SwiftUI Views, ViewModels)                 │    │
│  └────────────────────┬────────────────────────────────┘    │
│                       │ depends on                          │
│                       ▼                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │               Domain Layer                          │    │
│  │      (Use Cases, Entities, Protocols)               │    │
│  └────────────────────▲────────────────────────────────┘    │
│                       │ implements                          │
│                       │                                     │
│  ┌─────────────────────────────────────────────────────┐    │
│  │                Data Layer                           │    │
│  │    (Repositories, Network, Core Data, APIs)         │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  Dependency Rule: внешние слои зависят от внутренних        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│            TCA (The Composable Architecture)                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│                    ┌──────────────┐                          │
│                    │     View     │                          │
│                    └──────┬───────┘                          │
│                           │ sends                            │
│                           ▼                                  │
│                    ┌──────────────┐                          │
│                    │    Action    │                          │
│                    └──────┬───────┘                          │
│                           │                                  │
│                           ▼                                  │
│    ┌──────────────────────────────────────────┐             │
│    │              Reducer                     │             │
│    │  (State, Action) -> (State, Effect)     │             │
│    └──────────────────┬───────────────────────┘             │
│                       │ updates                             │
│                       ▼                                     │
│                ┌──────────────┐                             │
│                │    State     │                             │
│                └──────┬───────┘                             │
│                       │ renders                             │
│                       ▼                                     │
│                ┌──────────────┐                             │
│                │     View     │                             │
│                └──────────────┘                             │
│                                                              │
│  Unidirectional Data Flow: предсказуемость + тестируемость │
└─────────────────────────────────────────────────────────────┘
```

## 1. MVC (Model-View-Controller)

### Описание

MVC — классический паттерн Apple, используемый с первых версий iOS. Model хранит данные и бизнес-логику, View отображает UI, Controller координирует взаимодействие. Проблема: Controller часто становится "Massive View Controller", содержащим всю логику приложения.

### SwiftUI пример (адаптированный MVC)

```swift
// Model
struct User: Identifiable {
    let id: UUID
    var name: String
    var email: String

    func isValidEmail() -> Bool {
        email.contains("@") && email.contains(".")
    }
}

// View
struct UserProfileView: View {
    @StateObject private var controller = UserProfileController()

    var body: some View {
        VStack(spacing: 20) {
            TextField("Name", text: $controller.user.name)
                .textFieldStyle(.roundedBorder)

            TextField("Email", text: $controller.user.email)
                .textFieldStyle(.roundedBorder)

            Button("Save") {
                controller.saveUser()
            }
            .disabled(!controller.isValid)

            if controller.isLoading {
                ProgressView()
            }
        }
        .padding()
        .alert("Error", isPresented: $controller.showError) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(controller.errorMessage)
        }
    }
}

// Controller
class UserProfileController: ObservableObject {
    @Published var user: User
    @Published var isLoading = false
    @Published var showError = false
    @Published var errorMessage = ""

    private let userService: UserService

    var isValid: Bool {
        !user.name.isEmpty && user.isValidEmail()
    }

    init(userService: UserService = UserService()) {
        self.userService = userService
        self.user = User(id: UUID(), name: "", email: "")
    }

    func saveUser() {
        isLoading = true

        Task { @MainActor in
            do {
                try await userService.save(user)
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                showError = true
                isLoading = false
            }
        }
    }
}

// Service (часть Model слоя)
class UserService {
    func save(_ user: User) async throws {
        // Network request simulation
        try await Task.sleep(nanoseconds: 1_000_000_000)
        // throw URLError(.badServerResponse) // для теста ошибки
    }
}
```

### UIKit пример (классический MVC)

```swift
// Model
struct Product {
    let id: String
    var title: String
    var price: Double
    var imageURL: URL?
}

// View Controller (массивный контроллер - антипаттерн)
class ProductListViewController: UIViewController {
    private let tableView = UITableView()
    private var products: [Product] = []
    private var isLoading = false

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadProducts()
    }

    private func setupUI() {
        view.addSubview(tableView)
        tableView.frame = view.bounds
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(ProductCell.self, forCellReuseIdentifier: "ProductCell")
    }

    private func loadProducts() {
        isLoading = true

        // Все в одном месте: сетевой запрос, парсинг, обновление UI
        URLSession.shared.dataTask(with: URL(string: "https://api.example.com/products")!) { [weak self] data, response, error in
            guard let self = self else { return }

            DispatchQueue.main.async {
                self.isLoading = false

                if let error = error {
                    self.showError(error.localizedDescription)
                    return
                }

                guard let data = data else { return }

                do {
                    self.products = try JSONDecoder().decode([Product].self, from: data)
                    self.tableView.reloadData()
                } catch {
                    self.showError("Failed to parse products")
                }
            }
        }.resume()
    }

    private func showError(_ message: String) {
        let alert = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - Table View Delegate & DataSource (тоже в контроллере!)
extension ProductListViewController: UITableViewDelegate, UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        products.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ProductCell", for: indexPath) as! ProductCell
        cell.configure(with: products[indexPath.row])
        return cell
    }

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        let product = products[indexPath.row]
        let detailVC = ProductDetailViewController(product: product)
        navigationController?.pushViewController(detailVC, animated: true)
    }
}

class ProductCell: UITableViewCell {
    func configure(with product: Product) {
        textLabel?.text = product.title
        detailTextLabel?.text = "$\(product.price)"
    }
}
```

### Когда использовать

- Простые приложения с минимальной бизнес-логикой
- Прототипы и MVP проекты
- Legacy код, который невозможно переписать
- Небольшие экраны с простым UI

## 2. MVP (Model-View-Presenter)

### Описание

MVP решает проблему Massive View Controller, перенося логику в Presenter. View становится пассивным и только отображает данные, которые ей передает Presenter. В отличие от MVVM, здесь нет data binding — Presenter явно вызывает методы View.

### SwiftUI пример

```swift
// Model
struct Article {
    let id: UUID
    let title: String
    let content: String
    let publishedAt: Date
}

// View Protocol (контракт между View и Presenter)
protocol ArticleViewProtocol: AnyObject {
    func displayArticles(_ viewModels: [ArticleViewModel])
    func displayLoading(_ isLoading: Bool)
    func displayError(_ message: String)
}

// View Model (presentation model, не путать с MVVM ViewModel)
struct ArticleViewModel: Identifiable {
    let id: UUID
    let title: String
    let summary: String
    let formattedDate: String
}

// Presenter
class ArticlePresenter {
    weak var view: ArticleViewProtocol?
    private let articleService: ArticleServiceProtocol

    init(articleService: ArticleServiceProtocol = ArticleService()) {
        self.articleService = articleService
    }

    func viewDidLoad() {
        loadArticles()
    }

    func refreshArticles() {
        loadArticles()
    }

    private func loadArticles() {
        view?.displayLoading(true)

        Task { @MainActor in
            do {
                let articles = try await articleService.fetchArticles()
                let viewModels = articles.map { article in
                    ArticleViewModel(
                        id: article.id,
                        title: article.title,
                        summary: String(article.content.prefix(100)),
                        formattedDate: formatDate(article.publishedAt)
                    )
                }
                view?.displayArticles(viewModels)
                view?.displayLoading(false)
            } catch {
                view?.displayError(error.localizedDescription)
                view?.displayLoading(false)
            }
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        return formatter.string(from: date)
    }
}

// SwiftUI View (implements protocol через ObservableObject wrapper)
class ArticleViewState: ObservableObject, ArticleViewProtocol {
    @Published var articles: [ArticleViewModel] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    let presenter: ArticlePresenter

    init(presenter: ArticlePresenter = ArticlePresenter()) {
        self.presenter = presenter
        presenter.view = self
    }

    func displayArticles(_ viewModels: [ArticleViewModel]) {
        articles = viewModels
    }

    func displayLoading(_ isLoading: Bool) {
        self.isLoading = isLoading
    }

    func displayError(_ message: String) {
        errorMessage = message
    }
}

struct ArticleListView: View {
    @StateObject private var viewState = ArticleViewState()

    var body: some View {
        NavigationView {
            ZStack {
                if viewState.isLoading {
                    ProgressView()
                } else {
                    List(viewState.articles) { article in
                        VStack(alignment: .leading, spacing: 8) {
                            Text(article.title)
                                .font(.headline)
                            Text(article.summary)
                                .font(.subheadline)
                                .foregroundColor(.secondary)
                            Text(article.formattedDate)
                                .font(.caption)
                                .foregroundColor(.gray)
                        }
                    }
                }
            }
            .navigationTitle("Articles")
            .toolbar {
                Button("Refresh") {
                    viewState.presenter.refreshArticles()
                }
            }
            .onAppear {
                viewState.presenter.viewDidLoad()
            }
            .alert("Error", isPresented: .constant(viewState.errorMessage != nil)) {
                Button("OK") { viewState.errorMessage = nil }
            } message: {
                if let error = viewState.errorMessage {
                    Text(error)
                }
            }
        }
    }
}

// Service
protocol ArticleServiceProtocol {
    func fetchArticles() async throws -> [Article]
}

class ArticleService: ArticleServiceProtocol {
    func fetchArticles() async throws -> [Article] {
        try await Task.sleep(nanoseconds: 1_000_000_000)
        return [
            Article(id: UUID(), title: "iOS 18 Features", content: "Explore the latest features in iOS 18 including enhanced widgets and...", publishedAt: Date()),
            Article(id: UUID(), title: "SwiftUI Best Practices", content: "Learn how to build performant SwiftUI applications with these proven patterns...", publishedAt: Date().addingTimeInterval(-86400))
        ]
    }
}
```

### UIKit пример (классический MVP)

```swift
// Model
struct Task {
    let id: String
    var title: String
    var isCompleted: Bool
}

// View Protocol
protocol TaskListViewProtocol: AnyObject {
    func showTasks(_ tasks: [Task])
    func showLoading()
    func hideLoading()
    func showError(_ message: String)
}

// Presenter
class TaskListPresenter {
    weak var view: TaskListViewProtocol?
    private var tasks: [Task] = []
    private let taskService: TaskServiceProtocol

    init(taskService: TaskServiceProtocol = TaskService()) {
        self.taskService = taskService
    }

    func viewDidLoad() {
        loadTasks()
    }

    func didSelectTask(at index: Int) {
        tasks[index].isCompleted.toggle()
        view?.showTasks(tasks)

        Task {
            try? await taskService.updateTask(tasks[index])
        }
    }

    func didTapAddTask(title: String) {
        let newTask = Task(id: UUID().uuidString, title: title, isCompleted: false)
        tasks.append(newTask)
        view?.showTasks(tasks)

        Task {
            try? await taskService.createTask(newTask)
        }
    }

    private func loadTasks() {
        view?.showLoading()

        Task { @MainActor in
            do {
                tasks = try await taskService.fetchTasks()
                view?.showTasks(tasks)
                view?.hideLoading()
            } catch {
                view?.showError(error.localizedDescription)
                view?.hideLoading()
            }
        }
    }
}

// View Controller (passive view)
class TaskListViewController: UIViewController, TaskListViewProtocol {
    private let tableView = UITableView()
    private let activityIndicator = UIActivityIndicatorView(style: .large)
    private var tasks: [Task] = []

    let presenter: TaskListPresenter

    init(presenter: TaskListPresenter = TaskListPresenter()) {
        self.presenter = presenter
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        presenter.view = self
        presenter.viewDidLoad()
    }

    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Tasks"

        view.addSubview(tableView)
        view.addSubview(activityIndicator)

        tableView.frame = view.bounds
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(UITableViewCell.self, forCellReuseIdentifier: "TaskCell")

        activityIndicator.center = view.center

        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .add,
            target: self,
            action: #selector(addTaskTapped)
        )
    }

    @objc private func addTaskTapped() {
        let alert = UIAlertController(title: "New Task", message: nil, preferredStyle: .alert)
        alert.addTextField { textField in
            textField.placeholder = "Task title"
        }
        alert.addAction(UIAlertAction(title: "Cancel", style: .cancel))
        alert.addAction(UIAlertAction(title: "Add", style: .default) { [weak self, weak alert] _ in
            guard let title = alert?.textFields?.first?.text, !title.isEmpty else { return }
            self?.presenter.didTapAddTask(title: title)
        })
        present(alert, animated: true)
    }

    // MARK: - TaskListViewProtocol

    func showTasks(_ tasks: [Task]) {
        self.tasks = tasks
        tableView.reloadData()
    }

    func showLoading() {
        activityIndicator.startAnimating()
        tableView.isHidden = true
    }

    func hideLoading() {
        activityIndicator.stopAnimating()
        tableView.isHidden = false
    }

    func showError(_ message: String) {
        let alert = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - UITableViewDelegate & DataSource
extension TaskListViewController: UITableViewDelegate, UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        tasks.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "TaskCell", for: indexPath)
        let task = tasks[indexPath.row]

        var config = cell.defaultContentConfiguration()
        config.text = task.title
        cell.contentConfiguration = config
        cell.accessoryType = task.isCompleted ? .checkmark : .none

        return cell
    }

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        presenter.didSelectTask(at: indexPath.row)
    }
}

// Service
protocol TaskServiceProtocol {
    func fetchTasks() async throws -> [Task]
    func createTask(_ task: Task) async throws
    func updateTask(_ task: Task) async throws
}

class TaskService: TaskServiceProtocol {
    func fetchTasks() async throws -> [Task] {
        try await Task.sleep(nanoseconds: 500_000_000)
        return [
            Task(id: "1", title: "Review PR", isCompleted: false),
            Task(id: "2", title: "Write unit tests", isCompleted: true)
        ]
    }

    func createTask(_ task: Task) async throws {
        try await Task.sleep(nanoseconds: 200_000_000)
    }

    func updateTask(_ task: Task) async throws {
        try await Task.sleep(nanoseconds: 200_000_000)
    }
}
```

### Когда использовать

- UIKit приложения, где нужна максимальная тестируемость
- Проекты с четкой спецификацией UI поведения
- Команды, предпочитающие явные контракты (protocols)
- Когда нужен полный контроль над View обновлениями

## 3. MVVM (Model-View-ViewModel)

### Описание

MVVM — стандарт для SwiftUI приложений. ViewModel содержит presentation логику и предоставляет данные для View через data binding (@Published, Combine). View автоматически обновляется при изменении ViewModel. Идеальное сочетание с декларативным UI SwiftUI.

### SwiftUI пример (современный MVVM)

```swift
// Model
struct Weather: Codable {
    let temperature: Double
    let condition: String
    let humidity: Int
    let cityName: String
}

// ViewModel
@MainActor
class WeatherViewModel: ObservableObject {
    // Published properties - автоматический data binding
    @Published var temperature: String = "--"
    @Published var condition: String = "Loading..."
    @Published var humidity: String = "--"
    @Published var cityName: String = ""
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let weatherService: WeatherServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    init(weatherService: WeatherServiceProtocol = WeatherService()) {
        self.weatherService = weatherService
    }

    // Input (user actions)
    func fetchWeather(for city: String) {
        guard !city.isEmpty else { return }

        isLoading = true
        errorMessage = nil

        Task {
            do {
                let weather = try await weatherService.fetchWeather(for: city)
                updateUI(with: weather)
                isLoading = false
            } catch {
                errorMessage = "Failed to load weather: \(error.localizedDescription)"
                isLoading = false
            }
        }
    }

    func refresh() {
        guard !cityName.isEmpty else { return }
        fetchWeather(for: cityName)
    }

    // Private helpers
    private func updateUI(with weather: Weather) {
        temperature = String(format: "%.1f°C", weather.temperature)
        condition = weather.condition
        humidity = "\(weather.humidity)%"
        cityName = weather.cityName
    }
}

// View (декларативный SwiftUI)
struct WeatherView: View {
    @StateObject private var viewModel = WeatherViewModel()
    @State private var searchText = ""

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Search bar
                HStack {
                    TextField("Enter city name", text: $searchText)
                        .textFieldStyle(.roundedBorder)
                        .autocapitalization(.words)

                    Button("Search") {
                        viewModel.fetchWeather(for: searchText)
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(searchText.isEmpty || viewModel.isLoading)
                }
                .padding()

                // Weather content
                if viewModel.isLoading {
                    ProgressView()
                        .scaleEffect(1.5)
                } else if let error = viewModel.errorMessage {
                    VStack {
                        Image(systemName: "exclamationmark.triangle")
                            .font(.system(size: 50))
                            .foregroundColor(.orange)
                        Text(error)
                            .foregroundColor(.secondary)
                            .multilineTextAlignment(.center)
                    }
                } else if !viewModel.cityName.isEmpty {
                    weatherContent
                }

                Spacer()
            }
            .navigationTitle("Weather")
            .toolbar {
                Button(action: viewModel.refresh) {
                    Image(systemName: "arrow.clockwise")
                }
                .disabled(viewModel.isLoading || viewModel.cityName.isEmpty)
            }
        }
    }

    private var weatherContent: some View {
        VStack(spacing: 16) {
            Text(viewModel.cityName)
                .font(.largeTitle)
                .fontWeight(.bold)

            Text(viewModel.temperature)
                .font(.system(size: 72, weight: .thin))

            Text(viewModel.condition)
                .font(.title2)
                .foregroundColor(.secondary)

            HStack {
                Label("Humidity", systemImage: "drop.fill")
                Text(viewModel.humidity)
            }
            .font(.title3)
            .foregroundColor(.blue)
        }
        .padding()
        .background(
            RoundedRectangle(cornerRadius: 20)
                .fill(Color(.systemBackground))
                .shadow(radius: 10)
        )
        .padding()
    }
}

// Service
protocol WeatherServiceProtocol {
    func fetchWeather(for city: String) async throws -> Weather
}

class WeatherService: WeatherServiceProtocol {
    func fetchWeather(for city: String) async throws -> Weather {
        // Simulate network delay
        try await Task.sleep(nanoseconds: 1_000_000_000)

        // Mock data
        return Weather(
            temperature: Double.random(in: -10...35),
            condition: ["Sunny", "Cloudy", "Rainy", "Snowy"].randomElement()!,
            humidity: Int.random(in: 30...90),
            cityName: city
        )
    }
}
```

### UIKit пример (MVVM с Combine)

```swift
import Combine
import UIKit

// Model
struct LoginCredentials {
    var username: String
    var password: String
}

struct LoginResponse {
    let token: String
    let userId: String
}

// ViewModel
class LoginViewModel {
    // Input
    let usernameSubject = CurrentValueSubject<String, Never>("")
    let passwordSubject = CurrentValueSubject<String, Never>("")
    let loginTapSubject = PassthroughSubject<Void, Never>()

    // Output
    let isLoginButtonEnabled: AnyPublisher<Bool, Never>
    let isLoading: AnyPublisher<Bool, Never>
    let loginResult: AnyPublisher<Result<LoginResponse, Error>, Never>

    private let authService: AuthServiceProtocol
    private var cancellables = Set<AnyCancellable>()

    init(authService: AuthServiceProtocol = AuthService()) {
        self.authService = authService

        // Validation logic
        isLoginButtonEnabled = Publishers.CombineLatest(
            usernameSubject,
            passwordSubject
        )
        .map { username, password in
            username.count >= 3 && password.count >= 6
        }
        .eraseToAnyPublisher()

        let loadingSubject = PassthroughSubject<Bool, Never>()
        isLoading = loadingSubject.eraseToAnyPublisher()

        // Login flow
        let resultSubject = PassthroughSubject<Result<LoginResponse, Error>, Never>()
        loginResult = resultSubject.eraseToAnyPublisher()

        loginTapSubject
            .handleEvents(receiveOutput: { _ in
                loadingSubject.send(true)
            })
            .map { [weak self] _ -> LoginCredentials in
                guard let self = self else {
                    return LoginCredentials(username: "", password: "")
                }
                return LoginCredentials(
                    username: self.usernameSubject.value,
                    password: self.passwordSubject.value
                )
            }
            .flatMap { credentials in
                Future<LoginResponse, Error> { promise in
                    Task {
                        do {
                            let response = try await authService.login(credentials)
                            promise(.success(response))
                        } catch {
                            promise(.failure(error))
                        }
                    }
                }
            }
            .receive(on: DispatchQueue.main)
            .handleEvents(receiveOutput: { _ in
                loadingSubject.send(false)
            }, receiveCompletion: { _ in
                loadingSubject.send(false)
            })
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        resultSubject.send(.failure(error))
                    }
                },
                receiveValue: { response in
                    resultSubject.send(.success(response))
                }
            )
            .store(in: &cancellables)
    }
}

// View Controller
class LoginViewController: UIViewController {
    private let usernameTextField = UITextField()
    private let passwordTextField = UITextField()
    private let loginButton = UIButton(type: .system)
    private let activityIndicator = UIActivityIndicatorView(style: .medium)

    private let viewModel = LoginViewModel()
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        bindViewModel()
    }

    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Login"

        let stackView = UIStackView(arrangedSubviews: [
            usernameTextField,
            passwordTextField,
            loginButton,
            activityIndicator
        ])
        stackView.axis = .vertical
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false

        view.addSubview(stackView)

        NSLayoutConstraint.activate([
            stackView.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            stackView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 40),
            stackView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -40)
        ])

        usernameTextField.placeholder = "Username"
        usernameTextField.borderStyle = .roundedRect
        usernameTextField.autocapitalizationType = .none

        passwordTextField.placeholder = "Password"
        passwordTextField.borderStyle = .roundedRect
        passwordTextField.isSecureTextEntry = true

        loginButton.setTitle("Login", for: .normal)
        loginButton.titleLabel?.font = .boldSystemFont(ofSize: 18)
    }

    private func bindViewModel() {
        // Bind text fields to ViewModel
        usernameTextField.textPublisher
            .sink { [weak viewModel] text in
                viewModel?.usernameSubject.send(text ?? "")
            }
            .store(in: &cancellables)

        passwordTextField.textPublisher
            .sink { [weak viewModel] text in
                viewModel?.passwordSubject.send(text ?? "")
            }
            .store(in: &cancellables)

        // Bind button tap to ViewModel
        loginButton.tapPublisher
            .sink { [weak viewModel] in
                viewModel?.loginTapSubject.send()
            }
            .store(in: &cancellables)

        // Bind ViewModel outputs to UI
        viewModel.isLoginButtonEnabled
            .assign(to: \.isEnabled, on: loginButton)
            .store(in: &cancellables)

        viewModel.isLoading
            .sink { [weak self] isLoading in
                if isLoading {
                    self?.activityIndicator.startAnimating()
                    self?.loginButton.isEnabled = false
                } else {
                    self?.activityIndicator.stopAnimating()
                }
            }
            .store(in: &cancellables)

        viewModel.loginResult
            .sink { [weak self] result in
                switch result {
                case .success(let response):
                    self?.showSuccess(userId: response.userId)
                case .failure(let error):
                    self?.showError(error.localizedDescription)
                }
            }
            .store(in: &cancellables)
    }

    private func showSuccess(userId: String) {
        let alert = UIAlertController(
            title: "Success",
            message: "Logged in as user: \(userId)",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }

    private func showError(_ message: String) {
        let alert = UIAlertController(
            title: "Login Failed",
            message: message,
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// Combine extensions
extension UITextField {
    var textPublisher: AnyPublisher<String?, Never> {
        NotificationCenter.default
            .publisher(for: UITextField.textDidChangeNotification, object: self)
            .map { ($0.object as? UITextField)?.text }
            .eraseToAnyPublisher()
    }
}

extension UIButton {
    var tapPublisher: AnyPublisher<Void, Never> {
        controlEventPublisher(for: .touchUpInside)
    }

    private func controlEventPublisher(for event: UIControl.Event) -> AnyPublisher<Void, Never> {
        Publishers.ControlEvent(control: self, event: event)
            .eraseToAnyPublisher()
    }
}

extension Publishers {
    struct ControlEvent: Publisher {
        typealias Output = Void
        typealias Failure = Never

        let control: UIControl
        let event: UIControl.Event

        func receive<S>(subscriber: S) where S: Subscriber, S.Failure == Failure, S.Input == Output {
            let subscription = Subscription(subscriber: subscriber, control: control, event: event)
            subscriber.receive(subscription: subscription)
        }
    }
}

extension Publishers.ControlEvent {
    class Subscription<S: Subscriber>: Combine.Subscription where S.Input == Void, S.Failure == Never {
        private var subscriber: S?
        private let control: UIControl

        init(subscriber: S, control: UIControl, event: UIControl.Event) {
            self.subscriber = subscriber
            self.control = control
            control.addTarget(self, action: #selector(handleEvent), for: event)
        }

        @objc private func handleEvent() {
            _ = subscriber?.receive()
        }

        func request(_ demand: Subscribers.Demand) {}

        func cancel() {
            subscriber = nil
        }
    }
}

// Service
protocol AuthServiceProtocol {
    func login(_ credentials: LoginCredentials) async throws -> LoginResponse
}

class AuthService: AuthServiceProtocol {
    func login(_ credentials: LoginCredentials) async throws -> LoginResponse {
        try await Task.sleep(nanoseconds: 1_500_000_000)

        guard credentials.username == "demo" && credentials.password == "password" else {
            throw NSError(domain: "AuthError", code: 401, userInfo: [
                NSLocalizedDescriptionKey: "Invalid credentials"
            ])
        }

        return LoginResponse(token: "mock-token-123", userId: "user-456")
    }
}
```

### Когда использовать

- SwiftUI приложения (нативная поддержка data binding)
- Проекты с реактивным программированием (Combine, RxSwift)
- Средние и крупные приложения с complex UI
- Команды с опытом в MVVM паттерне
- Когда нужна высокая тестируемость ViewModel без UI

## 4. VIPER (View-Interactor-Presenter-Entity-Router)

### Описание

VIPER — модульная архитектура для enterprise приложений. Каждый компонент имеет одну ответственность: View (UI), Interactor (бизнес-логика), Presenter (presentation логика), Entity (модели), Router (навигация). Подходит для больших команд и сложных проектов.

### SwiftUI пример (адаптированный VIPER)

```swift
// MARK: - Entity
struct Note: Identifiable {
    let id: UUID
    var title: String
    var content: String
    var createdAt: Date
}

// MARK: - Interactor
protocol NoteListInteractorProtocol {
    func fetchNotes() async throws -> [Note]
    func deleteNote(id: UUID) async throws
    func createNote(title: String, content: String) async throws -> Note
}

class NoteListInteractor: NoteListInteractorProtocol {
    private let noteService: NoteServiceProtocol

    init(noteService: NoteServiceProtocol = NoteService()) {
        self.noteService = noteService
    }

    func fetchNotes() async throws -> [Note] {
        try await noteService.fetchNotes()
    }

    func deleteNote(id: UUID) async throws {
        try await noteService.deleteNote(id: id)
    }

    func createNote(title: String, content: String) async throws -> Note {
        let note = Note(
            id: UUID(),
            title: title,
            content: content,
            createdAt: Date()
        )
        try await noteService.saveNote(note)
        return note
    }
}

// MARK: - Presenter
@MainActor
class NoteListPresenter: ObservableObject {
    @Published var notes: [NoteViewModel] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let interactor: NoteListInteractorProtocol
    private let router: NoteListRouterProtocol

    init(
        interactor: NoteListInteractorProtocol = NoteListInteractor(),
        router: NoteListRouterProtocol = NoteListRouter()
    ) {
        self.interactor = interactor
        self.router = router
    }

    // User actions
    func viewDidAppear() {
        Task {
            await loadNotes()
        }
    }

    func didTapAddNote(title: String, content: String) {
        Task {
            isLoading = true
            do {
                let note = try await interactor.createNote(title: title, content: content)
                await loadNotes()
            } catch {
                errorMessage = "Failed to create note: \(error.localizedDescription)"
            }
            isLoading = false
        }
    }

    func didTapDeleteNote(id: UUID) {
        Task {
            do {
                try await interactor.deleteNote(id: id)
                notes.removeAll { $0.id == id }
            } catch {
                errorMessage = "Failed to delete note: \(error.localizedDescription)"
            }
        }
    }

    func didSelectNote(id: UUID) {
        guard let note = notes.first(where: { $0.id == id }) else { return }
        router.navigateToNoteDetail(noteId: id)
    }

    // Private
    private func loadNotes() async {
        isLoading = true
        do {
            let fetchedNotes = try await interactor.fetchNotes()
            notes = fetchedNotes.map { note in
                NoteViewModel(
                    id: note.id,
                    title: note.title,
                    preview: String(note.content.prefix(100)),
                    formattedDate: formatDate(note.createdAt)
                )
            }
        } catch {
            errorMessage = "Failed to load notes: \(error.localizedDescription)"
        }
        isLoading = false
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        return formatter.localizedString(for: date, relativeTo: Date())
    }
}

// View Model (presentation model)
struct NoteViewModel: Identifiable {
    let id: UUID
    let title: String
    let preview: String
    let formattedDate: String
}

// MARK: - Router
protocol NoteListRouterProtocol {
    func navigateToNoteDetail(noteId: UUID)
    func navigateToAddNote()
}

class NoteListRouter: NoteListRouterProtocol {
    weak var viewController: UIViewController?

    func navigateToNoteDetail(noteId: UUID) {
        // В SwiftUI это будет через NavigationLink или programmatic navigation
        print("Navigate to note detail: \(noteId)")
    }

    func navigateToAddNote() {
        print("Navigate to add note screen")
    }
}

// MARK: - View
struct NoteListView: View {
    @StateObject private var presenter = NoteListPresenter()
    @State private var showAddNote = false
    @State private var newNoteTitle = ""
    @State private var newNoteContent = ""

    var body: some View {
        NavigationView {
            ZStack {
                if presenter.isLoading && presenter.notes.isEmpty {
                    ProgressView()
                } else {
                    notesList
                }
            }
            .navigationTitle("Notes")
            .toolbar {
                Button(action: { showAddNote = true }) {
                    Image(systemName: "plus")
                }
            }
            .sheet(isPresented: $showAddNote) {
                addNoteSheet
            }
            .alert("Error", isPresented: .constant(presenter.errorMessage != nil)) {
                Button("OK") { presenter.errorMessage = nil }
            } message: {
                if let error = presenter.errorMessage {
                    Text(error)
                }
            }
            .onAppear {
                presenter.viewDidAppear()
            }
        }
    }

    private var notesList: some View {
        List {
            ForEach(presenter.notes) { note in
                Button(action: { presenter.didSelectNote(id: note.id) }) {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(note.title)
                            .font(.headline)
                        Text(note.preview)
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                            .lineLimit(2)
                        Text(note.formattedDate)
                            .font(.caption)
                            .foregroundColor(.gray)
                    }
                    .padding(.vertical, 4)
                }
                .buttonStyle(.plain)
            }
            .onDelete { indexSet in
                indexSet.forEach { index in
                    presenter.didTapDeleteNote(id: presenter.notes[index].id)
                }
            }
        }
        .refreshable {
            presenter.viewDidAppear()
        }
    }

    private var addNoteSheet: some View {
        NavigationView {
            Form {
                TextField("Title", text: $newNoteTitle)
                TextEditor(text: $newNoteContent)
                    .frame(height: 200)
            }
            .navigationTitle("New Note")
            .navigationBarItems(
                leading: Button("Cancel") {
                    showAddNote = false
                    resetForm()
                },
                trailing: Button("Save") {
                    presenter.didTapAddNote(title: newNoteTitle, content: newNoteContent)
                    showAddNote = false
                    resetForm()
                }
                .disabled(newNoteTitle.isEmpty)
            )
        }
    }

    private func resetForm() {
        newNoteTitle = ""
        newNoteContent = ""
    }
}

// MARK: - Service
protocol NoteServiceProtocol {
    func fetchNotes() async throws -> [Note]
    func saveNote(_ note: Note) async throws
    func deleteNote(id: UUID) async throws
}

class NoteService: NoteServiceProtocol {
    private var notes: [Note] = [
        Note(id: UUID(), title: "Welcome", content: "Welcome to VIPER architecture example", createdAt: Date().addingTimeInterval(-3600)),
        Note(id: UUID(), title: "iOS Development", content: "Building scalable iOS apps with clean architecture", createdAt: Date())
    ]

    func fetchNotes() async throws -> [Note] {
        try await Task.sleep(nanoseconds: 500_000_000)
        return notes.sorted { $0.createdAt > $1.createdAt }
    }

    func saveNote(_ note: Note) async throws {
        try await Task.sleep(nanoseconds: 300_000_000)
        notes.append(note)
    }

    func deleteNote(id: UUID) async throws {
        try await Task.sleep(nanoseconds: 200_000_000)
        notes.removeAll { $0.id == id }
    }
}

// MARK: - Module Builder (опционально, для dependency injection)
class NoteListModule {
    static func build() -> some View {
        let interactor = NoteListInteractor()
        let router = NoteListRouter()
        let presenter = NoteListPresenter(interactor: interactor, router: router)
        return NoteListView(presenter: presenter)
    }
}
```

### UIKit пример (классический VIPER)

```swift
// MARK: - Entity
struct Product {
    let id: String
    let name: String
    let price: Double
    let imageURL: URL?
    let description: String
}

// MARK: - View Protocol
protocol ProductListViewProtocol: AnyObject {
    func displayProducts(_ viewModels: [ProductViewModel])
    func displayLoading(_ isLoading: Bool)
    func displayError(_ message: String)
}

// MARK: - Presenter Protocol
protocol ProductListPresenterProtocol {
    func viewDidLoad()
    func didSelectProduct(at index: Int)
    func didTapRefresh()
}

// MARK: - Interactor Protocol
protocol ProductListInteractorProtocol {
    func fetchProducts() async throws -> [Product]
}

// MARK: - Router Protocol
protocol ProductListRouterProtocol {
    func navigateToProductDetail(product: Product)
}

// MARK: - Interactor
class ProductListInteractor: ProductListInteractorProtocol {
    private let productService: ProductServiceProtocol

    init(productService: ProductServiceProtocol = ProductService()) {
        self.productService = productService
    }

    func fetchProducts() async throws -> [Product] {
        try await productService.fetchProducts()
    }
}

// MARK: - Presenter
class ProductListPresenter: ProductListPresenterProtocol {
    weak var view: ProductListViewProtocol?
    private let interactor: ProductListInteractorProtocol
    private let router: ProductListRouterProtocol

    private var products: [Product] = []

    init(
        interactor: ProductListInteractorProtocol,
        router: ProductListRouterProtocol
    ) {
        self.interactor = interactor
        self.router = router
    }

    func viewDidLoad() {
        loadProducts()
    }

    func didSelectProduct(at index: Int) {
        guard index < products.count else { return }
        router.navigateToProductDetail(product: products[index])
    }

    func didTapRefresh() {
        loadProducts()
    }

    private func loadProducts() {
        view?.displayLoading(true)

        Task { @MainActor in
            do {
                products = try await interactor.fetchProducts()
                let viewModels = products.map { product in
                    ProductViewModel(
                        name: product.name,
                        price: "$\(String(format: "%.2f", product.price))",
                        imageURL: product.imageURL
                    )
                }
                view?.displayProducts(viewModels)
                view?.displayLoading(false)
            } catch {
                view?.displayError(error.localizedDescription)
                view?.displayLoading(false)
            }
        }
    }
}

// MARK: - View Model
struct ProductViewModel {
    let name: String
    let price: String
    let imageURL: URL?
}

// MARK: - Router
class ProductListRouter: ProductListRouterProtocol {
    weak var viewController: UIViewController?

    func navigateToProductDetail(product: Product) {
        let detailModule = ProductDetailModule.build(product: product)
        viewController?.navigationController?.pushViewController(detailModule, animated: true)
    }
}

// MARK: - View Controller
class ProductListViewController: UIViewController, ProductListViewProtocol {
    private let tableView = UITableView()
    private let activityIndicator = UIActivityIndicatorView(style: .large)
    private var productViewModels: [ProductViewModel] = []

    var presenter: ProductListPresenterProtocol!

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        presenter.viewDidLoad()
    }

    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "Products"

        view.addSubview(tableView)
        view.addSubview(activityIndicator)

        tableView.frame = view.bounds
        tableView.delegate = self
        tableView.dataSource = self
        tableView.register(ProductCell.self, forCellReuseIdentifier: "ProductCell")

        activityIndicator.center = view.center

        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .refresh,
            target: self,
            action: #selector(refreshTapped)
        )
    }

    @objc private func refreshTapped() {
        presenter.didTapRefresh()
    }

    // MARK: - ProductListViewProtocol

    func displayProducts(_ viewModels: [ProductViewModel]) {
        productViewModels = viewModels
        tableView.reloadData()
    }

    func displayLoading(_ isLoading: Bool) {
        if isLoading {
            activityIndicator.startAnimating()
            tableView.isHidden = true
        } else {
            activityIndicator.stopAnimating()
            tableView.isHidden = false
        }
    }

    func displayError(_ message: String) {
        let alert = UIAlertController(title: "Error", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "OK", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - UITableViewDelegate & DataSource
extension ProductListViewController: UITableViewDelegate, UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        productViewModels.count
    }

    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "ProductCell", for: indexPath) as! ProductCell
        cell.configure(with: productViewModels[indexPath.row])
        return cell
    }

    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        presenter.didSelectProduct(at: indexPath.row)
    }
}

// MARK: - Product Cell
class ProductCell: UITableViewCell {
    func configure(with viewModel: ProductViewModel) {
        var config = defaultContentConfiguration()
        config.text = viewModel.name
        config.secondaryText = viewModel.price
        contentConfiguration = config
    }
}

// MARK: - Module Builder
class ProductListModule {
    static func build() -> UIViewController {
        let interactor = ProductListInteractor()
        let router = ProductListRouter()
        let presenter = ProductListPresenter(interactor: interactor, router: router)
        let viewController = ProductListViewController()

        viewController.presenter = presenter
        presenter.view = viewController
        router.viewController = viewController

        return viewController
    }
}

// MARK: - Product Detail Module (заглушка)
class ProductDetailModule {
    static func build(product: Product) -> UIViewController {
        let vc = UIViewController()
        vc.view.backgroundColor = .systemBackground
        vc.title = product.name
        return vc
    }
}

// MARK: - Service
protocol ProductServiceProtocol {
    func fetchProducts() async throws -> [Product]
}

class ProductService: ProductServiceProtocol {
    func fetchProducts() async throws -> [Product] {
        try await Task.sleep(nanoseconds: 800_000_000)
        return [
            Product(id: "1", name: "iPhone 15 Pro", price: 999.99, imageURL: nil, description: "Latest iPhone"),
            Product(id: "2", name: "MacBook Pro M3", price: 1999.99, imageURL: nil, description: "Powerful laptop"),
            Product(id: "3", name: "AirPods Pro", price: 249.99, imageURL: nil, description: "Wireless earbuds")
        ]
    }
}
```

### Когда использовать

- Крупные enterprise приложения с большим количеством экранов
- Команды из 5+ разработчиков
- Проекты с высокими требованиями к модульности
- Когда нужна максимальная тестируемость всех компонентов
- Приложения с complex навигацией и бизнес-логикой

## 5. Clean Architecture

### Описание

Clean Architecture делит приложение на независимые слои: Presentation (UI), Domain (бизнес-логика), Data (источники данных). Каждый слой зависит только от внутреннего слоя. Domain Layer не знает о UI и базах данных — только о Use Cases и Entities.

### SwiftUI пример (трехслойная Clean Architecture)

```swift
// MARK: - Domain Layer (независимый от фреймворков)

// Entity
struct Book: Identifiable, Equatable {
    let id: UUID
    let title: String
    let author: String
    let isbn: String
    var isFavorite: Bool
}

// Repository Protocol (зависимость инвертирована)
protocol BookRepositoryProtocol {
    func fetchBooks() async throws -> [Book]
    func saveBook(_ book: Book) async throws
    func toggleFavorite(bookId: UUID) async throws
}

// Use Case
protocol FetchBooksUseCaseProtocol {
    func execute() async throws -> [Book]
}

class FetchBooksUseCase: FetchBooksUseCaseProtocol {
    private let repository: BookRepositoryProtocol

    init(repository: BookRepositoryProtocol) {
        self.repository = repository
    }

    func execute() async throws -> [Book] {
        let books = try await repository.fetchBooks()
        // Бизнес-логика: сортировка по избранным
        return books.sorted { $0.isFavorite && !$1.isFavorite }
    }
}

protocol ToggleFavoriteUseCaseProtocol {
    func execute(bookId: UUID) async throws
}

class ToggleFavoriteUseCase: ToggleFavoriteUseCaseProtocol {
    private let repository: BookRepositoryProtocol

    init(repository: BookRepositoryProtocol) {
        self.repository = repository
    }

    func execute(bookId: UUID) async throws {
        try await repository.toggleFavorite(bookId: bookId)
    }
}

// MARK: - Data Layer (реализация инфраструктуры)

// Repository Implementation
class BookRepository: BookRepositoryProtocol {
    private let networkDataSource: NetworkDataSourceProtocol
    private let localDataSource: LocalDataSourceProtocol

    init(
        networkDataSource: NetworkDataSourceProtocol = NetworkDataSource(),
        localDataSource: LocalDataSourceProtocol = LocalDataSource()
    ) {
        self.networkDataSource = networkDataSource
        self.localDataSource = localDataSource
    }

    func fetchBooks() async throws -> [Book] {
        // Попытка загрузить из кэша
        if let cachedBooks = try? await localDataSource.getBooks(), !cachedBooks.isEmpty {
            return cachedBooks
        }

        // Загрузка из сети
        let books = try await networkDataSource.fetchBooks()

        // Сохранение в кэш
        try? await localDataSource.saveBooks(books)

        return books
    }

    func saveBook(_ book: Book) async throws {
        try await networkDataSource.createBook(book)
        try await localDataSource.saveBook(book)
    }

    func toggleFavorite(bookId: UUID) async throws {
        try await localDataSource.toggleFavorite(bookId: bookId)
    }
}

// Network Data Source
protocol NetworkDataSourceProtocol {
    func fetchBooks() async throws -> [Book]
    func createBook(_ book: Book) async throws
}

class NetworkDataSource: NetworkDataSourceProtocol {
    func fetchBooks() async throws -> [Book] {
        try await Task.sleep(nanoseconds: 1_000_000_000)
        return [
            Book(id: UUID(), title: "Clean Architecture", author: "Robert Martin", isbn: "978-0134494166", isFavorite: false),
            Book(id: UUID(), title: "Swift Programming", author: "Apple Inc.", isbn: "978-0135264423", isFavorite: true)
        ]
    }

    func createBook(_ book: Book) async throws {
        try await Task.sleep(nanoseconds: 500_000_000)
    }
}

// Local Data Source (Core Data, UserDefaults, etc.)
protocol LocalDataSourceProtocol {
    func getBooks() async throws -> [Book]
    func saveBooks(_ books: [Book]) async throws
    func saveBook(_ book: Book) async throws
    func toggleFavorite(bookId: UUID) async throws
}

class LocalDataSource: LocalDataSourceProtocol {
    private var cachedBooks: [Book] = []

    func getBooks() async throws -> [Book] {
        cachedBooks
    }

    func saveBooks(_ books: [Book]) async throws {
        cachedBooks = books
    }

    func saveBook(_ book: Book) async throws {
        if let index = cachedBooks.firstIndex(where: { $0.id == book.id }) {
            cachedBooks[index] = book
        } else {
            cachedBooks.append(book)
        }
    }

    func toggleFavorite(bookId: UUID) async throws {
        guard let index = cachedBooks.firstIndex(where: { $0.id == bookId }) else { return }
        cachedBooks[index].isFavorite.toggle()
    }
}

// MARK: - Presentation Layer (SwiftUI + ViewModel)

@MainActor
class BookListViewModel: ObservableObject {
    @Published var books: [Book] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let fetchBooksUseCase: FetchBooksUseCaseProtocol
    private let toggleFavoriteUseCase: ToggleFavoriteUseCaseProtocol

    init(
        fetchBooksUseCase: FetchBooksUseCaseProtocol,
        toggleFavoriteUseCase: ToggleFavoriteUseCaseProtocol
    ) {
        self.fetchBooksUseCase = fetchBooksUseCase
        self.toggleFavoriteUseCase = toggleFavoriteUseCase
    }

    func loadBooks() {
        isLoading = true

        Task {
            do {
                books = try await fetchBooksUseCase.execute()
                isLoading = false
            } catch {
                errorMessage = error.localizedDescription
                isLoading = false
            }
        }
    }

    func toggleFavorite(_ book: Book) {
        Task {
            do {
                try await toggleFavoriteUseCase.execute(bookId: book.id)
                // Обновить локально для instant UI feedback
                if let index = books.firstIndex(where: { $0.id == book.id }) {
                    books[index].isFavorite.toggle()
                }
            } catch {
                errorMessage = "Failed to toggle favorite"
            }
        }
    }
}

// SwiftUI View
struct BookListView: View {
    @StateObject private var viewModel: BookListViewModel

    init(viewModel: BookListViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }

    var body: some View {
        NavigationView {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                } else {
                    bookList
                }
            }
            .navigationTitle("Books")
            .onAppear {
                viewModel.loadBooks()
            }
            .alert("Error", isPresented: .constant(viewModel.errorMessage != nil)) {
                Button("OK") { viewModel.errorMessage = nil }
            } message: {
                if let error = viewModel.errorMessage {
                    Text(error)
                }
            }
        }
    }

    private var bookList: some View {
        List(viewModel.books) { book in
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text(book.title)
                        .font(.headline)
                    Text(book.author)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                    Text("ISBN: \(book.isbn)")
                        .font(.caption)
                        .foregroundColor(.gray)
                }

                Spacer()

                Button(action: { viewModel.toggleFavorite(book) }) {
                    Image(systemName: book.isFavorite ? "star.fill" : "star")
                        .foregroundColor(book.isFavorite ? .yellow : .gray)
                }
                .buttonStyle(.plain)
            }
            .padding(.vertical, 4)
        }
    }
}

// MARK: - Dependency Injection Container

class AppDIContainer {
    // Data Layer
    lazy var networkDataSource: NetworkDataSourceProtocol = NetworkDataSource()
    lazy var localDataSource: LocalDataSourceProtocol = LocalDataSource()
    lazy var bookRepository: BookRepositoryProtocol = BookRepository(
        networkDataSource: networkDataSource,
        localDataSource: localDataSource
    )

    // Domain Layer
    lazy var fetchBooksUseCase: FetchBooksUseCaseProtocol = FetchBooksUseCase(
        repository: bookRepository
    )
    lazy var toggleFavoriteUseCase: ToggleFavoriteUseCaseProtocol = ToggleFavoriteUseCase(
        repository: bookRepository
    )

    // Presentation Layer
    @MainActor
    func makeBookListViewModel() -> BookListViewModel {
        BookListViewModel(
            fetchBooksUseCase: fetchBooksUseCase,
            toggleFavoriteUseCase: toggleFavoriteUseCase
        )
    }
}

// App Entry Point
@main
struct CleanArchitectureApp: App {
    private let container = AppDIContainer()

    var body: some Scene {
        WindowGroup {
            BookListView(viewModel: container.makeBookListViewModel())
        }
    }
}
```

### Когда использовать

- Большие приложения с долгим lifecycle (5+ лет)
- Проекты с частой сменой требований к бизнес-логике
- Когда нужна независимость от фреймворков (легкая миграция UIKit → SwiftUI)
- Microservices architecture на мобильной стороне
- Приложения с множественными источниками данных (API, Core Data, CloudKit)

## 6. TCA (The Composable Architecture)

### Описание

TCA от Point-Free — функциональная архитектура с унидиректональным потоком данных. State (состояние) + Action (действие) → Reducer (редьюсер) → новое State. Композиция маленьких редьюсеров в большие, встроенная поддержка Side Effects, time-travel debugging.

### SwiftUI пример (TCA)

```swift
import ComposableArchitecture
import SwiftUI

// MARK: - Feature Domain

@Reducer
struct CounterFeature {
    // State - единственный источник истины
    @ObservableState
    struct State: Equatable {
        var count = 0
        var factText: String?
        var isLoadingFact = false
    }

    // Action - все возможные действия
    enum Action {
        case incrementButtonTapped
        case decrementButtonTapped
        case factButtonTapped
        case factResponse(Result<String, Error>)
    }

    // Dependencies
    @Dependency(\.numberFact) var numberFact

    // Reducer - чистая функция (State, Action) -> State
    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .incrementButtonTapped:
                state.count += 1
                state.factText = nil
                return .none

            case .decrementButtonTapped:
                state.count -= 1
                state.factText = nil
                return .none

            case .factButtonTapped:
                state.isLoadingFact = true
                state.factText = nil

                // Effect (Side Effect) - асинхронные операции
                return .run { [count = state.count] send in
                    do {
                        let fact = try await numberFact.fetch(count)
                        await send(.factResponse(.success(fact)))
                    } catch {
                        await send(.factResponse(.failure(error)))
                    }
                }

            case .factResponse(.success(let fact)):
                state.isLoadingFact = false
                state.factText = fact
                return .none

            case .factResponse(.failure):
                state.isLoadingFact = false
                state.factText = "Failed to load fact"
                return .none
            }
        }
    }
}

// MARK: - View

struct CounterView: View {
    let store: StoreOf<CounterFeature>

    var body: some View {
        VStack(spacing: 20) {
            Text("\(store.count)")
                .font(.system(size: 80, weight: .bold))

            HStack(spacing: 20) {
                Button("-") {
                    store.send(.decrementButtonTapped)
                }
                .buttonStyle(.borderedProminent)
                .tint(.red)
                .font(.title)

                Button("+") {
                    store.send(.incrementButtonTapped)
                }
                .buttonStyle(.borderedProminent)
                .tint(.green)
                .font(.title)
            }

            Button("Get Number Fact") {
                store.send(.factButtonTapped)
            }
            .buttonStyle(.bordered)
            .disabled(store.isLoadingFact)

            if store.isLoadingFact {
                ProgressView()
            } else if let factText = store.factText {
                Text(factText)
                    .font(.body)
                    .multilineTextAlignment(.center)
                    .padding()
                    .background(
                        RoundedRectangle(cornerRadius: 10)
                            .fill(Color(.systemGray6))
                    )
            }
        }
        .padding()
    }
}

// MARK: - Dependencies

struct NumberFactClient {
    var fetch: @Sendable (Int) async throws -> String
}

extension NumberFactClient: DependencyKey {
    static let liveValue = Self { number in
        let url = URL(string: "http://numbersapi.com/\(number)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return String(decoding: data, as: UTF8.self)
    }
}

extension DependencyValues {
    var numberFact: NumberFactClient {
        get { self[NumberFactClient.self] }
        set { self[NumberFactClient.self] = newValue }
    }
}

// MARK: - Preview

#Preview {
    CounterView(
        store: Store(initialState: CounterFeature.State()) {
            CounterFeature()
        }
    )
}

// MARK: - Композиция нескольких фич

@Reducer
struct AppFeature {
    @ObservableState
    struct State: Equatable {
        var counter = CounterFeature.State()
        var todoList = TodoListFeature.State()
        var selectedTab: Tab = .counter

        enum Tab {
            case counter
            case todos
        }
    }

    enum Action {
        case counter(CounterFeature.Action)
        case todoList(TodoListFeature.Action)
        case tabSelected(State.Tab)
    }

    var body: some ReducerOf<Self> {
        Scope(state: \.counter, action: \.counter) {
            CounterFeature()
        }

        Scope(state: \.todoList, action: \.todoList) {
            TodoListFeature()
        }

        Reduce { state, action in
            switch action {
            case .tabSelected(let tab):
                state.selectedTab = tab
                return .none

            case .counter, .todoList:
                return .none
            }
        }
    }
}

// MARK: - Todo List Feature Example

@Reducer
struct TodoListFeature {
    @ObservableState
    struct State: Equatable {
        var todos: IdentifiedArrayOf<Todo> = []
        var newTodoTitle = ""
    }

    enum Action: BindableAction {
        case addButtonTapped
        case deleteButtonTapped(id: Todo.ID)
        case toggleTodoTapped(id: Todo.ID)
        case binding(BindingAction<State>)
    }

    var body: some ReducerOf<Self> {
        BindingReducer()

        Reduce { state, action in
            switch action {
            case .addButtonTapped:
                guard !state.newTodoTitle.isEmpty else { return .none }
                state.todos.append(
                    Todo(id: UUID(), title: state.newTodoTitle, isCompleted: false)
                )
                state.newTodoTitle = ""
                return .none

            case .deleteButtonTapped(let id):
                state.todos.remove(id: id)
                return .none

            case .toggleTodoTapped(let id):
                state.todos[id: id]?.isCompleted.toggle()
                return .none

            case .binding:
                return .none
            }
        }
    }
}

struct Todo: Equatable, Identifiable {
    let id: UUID
    var title: String
    var isCompleted: Bool
}

struct TodoListView: View {
    @Bindable var store: StoreOf<TodoListFeature>

    var body: some View {
        List {
            Section {
                HStack {
                    TextField("New todo", text: $store.newTodoTitle)
                    Button("Add") {
                        store.send(.addButtonTapped)
                    }
                    .disabled(store.newTodoTitle.isEmpty)
                }
            }

            Section {
                ForEach(store.todos) { todo in
                    HStack {
                        Button(action: { store.send(.toggleTodoTapped(id: todo.id)) }) {
                            Image(systemName: todo.isCompleted ? "checkmark.circle.fill" : "circle")
                                .foregroundColor(todo.isCompleted ? .green : .gray)
                        }
                        .buttonStyle(.plain)

                        Text(todo.title)
                            .strikethrough(todo.isCompleted)
                            .foregroundColor(todo.isCompleted ? .gray : .primary)
                    }
                }
                .onDelete { indexSet in
                    indexSet.forEach { index in
                        store.send(.deleteButtonTapped(id: store.todos[index].id))
                    }
                }
            }
        }
    }
}

// MARK: - App Entry with TCA

struct TCAExampleApp: View {
    let store = Store(initialState: AppFeature.State()) {
        AppFeature()
    }

    var body: some View {
        TabView(selection: $store.selectedTab.sending(\.tabSelected)) {
            CounterView(store: store.scope(state: \.counter, action: \.counter))
                .tabItem {
                    Label("Counter", systemImage: "number")
                }
                .tag(AppFeature.State.Tab.counter)

            TodoListView(store: store.scope(state: \.todoList, action: \.todoList))
                .tabItem {
                    Label("Todos", systemImage: "list.bullet")
                }
                .tag(AppFeature.State.Tab.todos)
        }
    }
}
```

### Когда использовать

- Проекты, где критична предсказуемость состояния
- Приложения с complex state management (multiple screens sharing state)
- Команды с опытом в функциональном программировании
- Когда нужен time-travel debugging и полное тестирование
- Проекты Point-Free subscribers или фанаты Redux/Elm architecture

## Сравнительная таблица

| Критерий | MVC | MVP | MVVM | VIPER | Clean Architecture | TCA |
|----------|-----|-----|------|-------|-------------------|-----|
| **Сложность** | Низкая | Средняя | Средняя | Высокая | Очень высокая | Высокая |
| **Тестируемость** | Низкая | Высокая | Высокая | Очень высокая | Очень высокая | Максимальная |
| **Scalability** | Низкая | Средняя | Высокая | Очень высокая | Максимальная | Высокая |
| **Boilerplate код** | Минимум | Средний | Средний | Много | Очень много | Средний |
| **SwiftUI support** | Адаптация | Адаптация | Нативный | Адаптация | Хорошая | Нативный |
| **UIKit support** | Нативный | Отличный | Хороший | Отличный | Отличный | Средний |
| **Навигация** | В Controller | В Presenter | В ViewModel | Router | В слое Presentation | В Reducer |
| **Data binding** | Ручной | Ручной | Автоматический | Ручной | Зависит от слоя | Автоматический |
| **Кривая обучения** | Плоская | Средняя | Средняя | Крутая | Очень крутая | Крутая |
| **Размер команды** | 1-2 | 2-4 | 2-6 | 5+ | 5+ | 3-8 |
| **Срок проекта** | Недели | Месяцы | Месяцы-годы | Годы | Годы | Месяцы-годы |
| **Модульность** | Низкая | Средняя | Средняя | Очень высокая | Максимальная | Высокая |
| **Dependency Injection** | Слабая | Средняя | Средняя | Сильная | Очень сильная | Встроенная |

## Когда использовать каждый паттерн

### MVC

**Используйте когда:**
- Прототипирование или MVP продукта
- Простое приложение с 3-5 экранами
- Solo-разработка или очень маленькая команда
- Tight дедлайны и приоритет — скорость разработки
- Legacy проект, который нельзя переписывать

**Не используйте когда:**
- Приложение будет масштабироваться
- Нужна высокая тестируемость
- Команда больше 2-3 человек
- Проект на несколько лет

### MVP

**Используйте когда:**
- UIKit приложение с требованиями к тестируемости
- Нужна пассивная View для полного контроля UI
- Команда предпочитает protocol-oriented подход
- Четкая спецификация поведения UI

**Не используйте когда:**
- SwiftUI проект (MVVM лучше подходит)
- Нужна реактивность и data binding
- Команда не знакома с паттерном

### MVVM

**Используйте когда:**
- SwiftUI приложение (практически всегда)
- Нужен баланс между простотой и тестируемостью
- Команда знакома с Combine или RxSwift
- Средние и крупные проекты (10-50 экранов)
- Реактивное программирование — приоритет

**Не используйте когда:**
- Очень простое приложение (MVC достаточно)
- Нужна максимальная модульность (используйте VIPER/Clean)

### VIPER

**Используйте когда:**
- Enterprise приложение с 50+ экранами
- Большая команда (5+ разработчиков)
- Высокие требования к модульности и переиспользованию
- Complex навигация между модулями
- Долгосрочный проект с частыми изменениями

**Не используйте когда:**
- Маленький проект или прототип
- Команда меньше 3-4 человек
- Tight дедлайны (много boilerplate кода)
- Простая навигация

### Clean Architecture

**Используйте когда:**
- Проект с lifecycle 5+ лет
- Приложение с множественными источниками данных
- Планируется миграция между фреймворками (UIKit → SwiftUI)
- Бизнес-логика часто меняется
- Microservices на мобильной стороне
- Нужна полная независимость от инфраструктуры

**Не используйте когда:**
- Стартап с неясными требованиями
- Быстрое прототипирование
- Проект меньше года
- Команда без опыта в Clean Architecture

### TCA

**Используйте когда:**
- SwiftUI проект с complex state management
- Команда знакома с функциональным программированием
- Нужна максимальная предсказуемость состояния
- Time-travel debugging критичен
- Множественные экраны sharing state
- Проект Point-Free subscribers

**Не используйте когда:**
- Команда не знакома с Redux/Elm architecture
- UIKit проект
- Нужна минимальная кривая обучения
- Простое приложение без сложного state

## 6 типичных ошибок

### Ошибка 1: Massive View Controller в MVC

❌ **Неправильно:**

```swift
class ProductViewController: UIViewController {
    private var products: [Product] = []

    override func viewDidLoad() {
        super.viewDidLoad()

        // UI setup прямо здесь
        tableView.backgroundColor = .white
        tableView.register(ProductCell.self, forCellReuseIdentifier: "cell")

        // Сетевой запрос прямо в контроллере
        URLSession.shared.dataTask(with: URL(string: "https://api.example.com/products")!) { data, _, error in
            guard let data = data else { return }

            // JSON парсинг прямо здесь
            if let json = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]] {
                self.products = json.compactMap { dict in
                    guard let id = dict["id"] as? String,
                          let name = dict["name"] as? String else { return nil }
                    return Product(id: id, name: name)
                }

                // Вычисления и форматирование прямо здесь
                self.products = self.products.filter { $0.name.count > 3 }
                    .sorted { $0.name < $1.name }

                DispatchQueue.main.async {
                    self.tableView.reloadData()
                }
            }
        }.resume()
    }

    // Table view delegate/dataSource тоже здесь
    // Navigation логика тоже здесь
    // Validation логика тоже здесь
    // Analytics тоже здесь
}
```

✅ **Правильно (с выделением слоев):**

```swift
// Service Layer
class ProductService {
    func fetchProducts() async throws -> [Product] {
        let (data, _) = try await URLSession.shared.data(from: URL(string: "https://api.example.com/products")!)
        return try JSONDecoder().decode([Product].self, from: data)
    }
}

// ViewModel/Presenter Layer
class ProductViewModel {
    private let service: ProductService

    func loadProducts() async throws -> [ProductDisplayModel] {
        let products = try await service.fetchProducts()
        return products
            .filter { $0.name.count > 3 }
            .sorted { $0.name < $1.name }
            .map { ProductDisplayModel(id: $0.id, displayName: $0.name.uppercased()) }
    }
}

// View Controller (тонкий слой)
class ProductViewController: UIViewController {
    private let viewModel: ProductViewModel
    private var displayModels: [ProductDisplayModel] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadData()
    }

    private func loadData() {
        Task {
            do {
                displayModels = try await viewModel.loadProducts()
                tableView.reloadData()
            } catch {
                showError(error)
            }
        }
    }
}
```

### Ошибка 2: ViewModel зависит от UIKit

❌ **Неправильно:**

```swift
import UIKit

class UserProfileViewModel: ObservableObject {
    @Published var nameText: String = ""

    // ViewModel не должен знать о UIKit!
    func getNameColor() -> UIColor {
        nameText.isEmpty ? .red : .green
    }

    // ViewModel не должен показывать UI!
    func showSuccessAlert(on viewController: UIViewController) {
        let alert = UIAlertController(title: "Success", message: nil, preferredStyle: .alert)
        viewController.present(alert, animated: true)
    }

    // ViewModel не должен знать о UIImage!
    func getAvatarImage() -> UIImage? {
        UIImage(named: "avatar")
    }
}
```

✅ **Правильно (Platform-agnostic ViewModel):**

```swift
import Foundation
import SwiftUI // Только для SwiftUI проектов, или вообще без UI imports

class UserProfileViewModel: ObservableObject {
    @Published var nameText: String = ""
    @Published var nameValidationState: ValidationState = .valid
    @Published var showSuccessMessage = false
    @Published var avatarURL: URL?

    enum ValidationState {
        case valid
        case invalid

        // View сама решает, какой цвет использовать
        var isValid: Bool {
            switch self {
            case .valid: return true
            case .invalid: return false
            }
        }
    }

    func validateName() {
        nameValidationState = nameText.isEmpty ? .invalid : .valid
    }

    func saveProfile() async {
        // После сохранения установить флаг
        showSuccessMessage = true
    }
}

// View обрабатывает UI presentation
struct UserProfileView: View {
    @StateObject var viewModel = UserProfileViewModel()

    var body: some View {
        TextField("Name", text: $viewModel.nameText)
            .foregroundColor(viewModel.nameValidationState.isValid ? .green : .red)
            .alert("Success", isPresented: $viewModel.showSuccessMessage) {
                Button("OK", role: .cancel) { }
            }
    }
}
```

### Ошибка 3: Нарушение Dependency Rule в Clean Architecture

❌ **Неправильно:**

```swift
// Domain Layer
class FetchUserUseCase {
    // Domain зависит от Data Layer - WRONG!
    private let apiClient = APIClient()
    private let database = CoreDataManager()

    func execute() async throws -> User {
        // Domain знает об implementation details - WRONG!
        let userData = try await apiClient.get(endpoint: "/user")
        let user = User(json: userData)
        try database.save(user)
        return user
    }
}

// Presentation Layer
class UserViewModel {
    // ViewModel знает о конкретной реализации Use Case - плохая практика
    private let useCase = FetchUserUseCase()

    func loadUser() {
        Task {
            let user = try await useCase.execute()
            // ...
        }
    }
}
```

✅ **Правильно (правильные зависимости через protocols):**

```swift
// Domain Layer (protocols, не зависит ни от чего)
protocol UserRepositoryProtocol {
    func fetchUser() async throws -> User
    func saveUser(_ user: User) async throws
}

protocol FetchUserUseCaseProtocol {
    func execute() async throws -> User
}

class FetchUserUseCase: FetchUserUseCaseProtocol {
    // Зависимость через protocol (инверсия зависимости)
    private let repository: UserRepositoryProtocol

    init(repository: UserRepositoryProtocol) {
        self.repository = repository
    }

    func execute() async throws -> User {
        let user = try await repository.fetchUser()
        try await repository.saveUser(user) // кэширование
        return user
    }
}

// Data Layer (реализует protocol из Domain)
class UserRepository: UserRepositoryProtocol {
    private let apiClient: APIClientProtocol
    private let database: DatabaseProtocol

    init(apiClient: APIClientProtocol, database: DatabaseProtocol) {
        self.apiClient = apiClient
        self.database = database
    }

    func fetchUser() async throws -> User {
        try await apiClient.get(endpoint: "/user")
    }

    func saveUser(_ user: User) async throws {
        try await database.save(user)
    }
}

// Presentation Layer
class UserViewModel {
    // Зависимость через protocol
    private let fetchUserUseCase: FetchUserUseCaseProtocol

    init(fetchUserUseCase: FetchUserUseCaseProtocol) {
        self.fetchUserUseCase = fetchUserUseCase
    }

    func loadUser() {
        Task {
            let user = try await fetchUserUseCase.execute()
            // ...
        }
    }
}

// DI Container собирает все зависимости
class AppDIContainer {
    func makeUserViewModel() -> UserViewModel {
        let apiClient = APIClient()
        let database = CoreDataManager()
        let repository = UserRepository(apiClient: apiClient, database: database)
        let useCase = FetchUserUseCase(repository: repository)
        return UserViewModel(fetchUserUseCase: useCase)
    }
}
```

### Ошибка 4: View логика в VIPER Presenter

❌ **Неправильно:**

```swift
// Presenter содержит view-specific логику
class ArticlePresenter {
    weak var view: ArticleViewProtocol?

    func didTapLikeButton() {
        // Presenter не должен знать о конкретном UI!
        view?.setLikeButtonColor(.red)
        view?.setLikeButtonImage(UIImage(named: "heart.fill"))
        view?.animateLikeButton(duration: 0.3)

        // Presenter решает как отображать UI - WRONG!
        if article.likes > 100 {
            view?.showBigLikeAnimation()
        } else {
            view?.showSmallLikeAnimation()
        }
    }
}

protocol ArticleViewProtocol: AnyObject {
    func setLikeButtonColor(_ color: UIColor)
    func setLikeButtonImage(_ image: UIImage?)
    func animateLikeButton(duration: TimeInterval)
    func showBigLikeAnimation()
    func showSmallLikeAnimation()
}
```

✅ **Правильно (Presenter передает данные, View решает как отображать):**

```swift
// Presenter передает presentation state
class ArticlePresenter {
    weak var view: ArticleViewProtocol?
    private let interactor: ArticleInteractorProtocol

    func didTapLikeButton() {
        // Presenter обновляет state через Interactor
        interactor.toggleLike { [weak self] result in
            switch result {
            case .success(let article):
                // Presenter передает данные для отображения
                self?.view?.displayLikeState(
                    isLiked: article.isLiked,
                    likesCount: article.likes
                )
            case .failure(let error):
                self?.view?.displayError(error.localizedDescription)
            }
        }
    }
}

// Простой protocol с presentation model
protocol ArticleViewProtocol: AnyObject {
    func displayLikeState(isLiked: Bool, likesCount: Int)
    func displayError(_ message: String)
}

// View сама решает как отобразить
class ArticleViewController: UIViewController, ArticleViewProtocol {
    @IBOutlet weak var likeButton: UIButton!
    @IBOutlet weak var likesLabel: UILabel!

    func displayLikeState(isLiked: Bool, likesCount: Int) {
        // View решает детали UI
        let imageName = isLiked ? "heart.fill" : "heart"
        let color: UIColor = isLiked ? .systemRed : .systemGray

        likeButton.setImage(UIImage(systemName: imageName), for: .normal)
        likeButton.tintColor = color
        likesLabel.text = "\(likesCount)"

        // View решает когда и как анимировать
        if isLiked && likesCount > 100 {
            animateLikeButtonBig()
        } else if isLiked {
            animateLikeButtonSmall()
        }
    }

    private func animateLikeButtonBig() {
        UIView.animate(withDuration: 0.5, delay: 0, usingSpringWithDamping: 0.5, initialSpringVelocity: 0.8) {
            self.likeButton.transform = CGAffineTransform(scaleX: 1.3, y: 1.3)
        } completion: { _ in
            self.likeButton.transform = .identity
        }
    }

    private func animateLikeButtonSmall() {
        UIView.animate(withDuration: 0.2) {
            self.likeButton.transform = CGAffineTransform(scaleX: 1.1, y: 1.1)
        } completion: { _ in
            self.likeButton.transform = .identity
        }
    }
}
```

### Ошибка 5: Нетестируемый ViewModel из-за жестких зависимостей

❌ **Неправильно:**

```swift
class WeatherViewModel: ObservableObject {
    @Published var temperature: String = ""

    // Жесткая зависимость от конкретной реализации
    private let service = WeatherService()

    func loadWeather() {
        Task {
            // Нельзя протестировать без реального API запроса
            let weather = try await service.fetchWeather()
            temperature = "\(weather.temp)°C"
        }
    }
}

// Невозможно написать unit тест без реального API
class WeatherViewModelTests: XCTestCase {
    func testLoadWeather() async throws {
        let viewModel = WeatherViewModel()

        // Проблема: вызывает реальный API!
        await viewModel.loadWeather()

        // Тест нестабильный (зависит от сети)
        XCTAssertNotEqual(viewModel.temperature, "")
    }
}
```

✅ **Правильно (Dependency Injection для тестируемости):**

```swift
// Protocol для инверсии зависимости
protocol WeatherServiceProtocol {
    func fetchWeather() async throws -> Weather
}

class WeatherViewModel: ObservableObject {
    @Published var temperature: String = ""

    // Зависимость через protocol
    private let service: WeatherServiceProtocol

    // Dependency Injection через initializer
    init(service: WeatherServiceProtocol = WeatherService()) {
        self.service = service
    }

    func loadWeather() {
        Task {
            do {
                let weather = try await service.fetchWeather()
                await MainActor.run {
                    temperature = "\(weather.temp)°C"
                }
            } catch {
                await MainActor.run {
                    temperature = "Error"
                }
            }
        }
    }
}

// Production implementation
class WeatherService: WeatherServiceProtocol {
    func fetchWeather() async throws -> Weather {
        // Реальный API запрос
        let (data, _) = try await URLSession.shared.data(from: URL(string: "https://api.weather.com")!)
        return try JSONDecoder().decode(Weather.self, from: data)
    }
}

// Mock для тестирования
class MockWeatherService: WeatherServiceProtocol {
    var weatherToReturn: Weather?
    var errorToThrow: Error?

    func fetchWeather() async throws -> Weather {
        if let error = errorToThrow {
            throw error
        }
        return weatherToReturn ?? Weather(temp: 25, condition: "Sunny")
    }
}

// Теперь можно писать быстрые и стабильные тесты
class WeatherViewModelTests: XCTestCase {
    @MainActor
    func testLoadWeatherSuccess() async throws {
        // Arrange
        let mockService = MockWeatherService()
        mockService.weatherToReturn = Weather(temp: 30, condition: "Hot")
        let viewModel = WeatherViewModel(service: mockService)

        // Act
        await viewModel.loadWeather()

        // Assert
        XCTAssertEqual(viewModel.temperature, "30°C")
    }

    @MainActor
    func testLoadWeatherFailure() async throws {
        // Arrange
        let mockService = MockWeatherService()
        mockService.errorToThrow = URLError(.notConnectedToInternet)
        let viewModel = WeatherViewModel(service: mockService)

        // Act
        await viewModel.loadWeather()

        // Assert
        XCTAssertEqual(viewModel.temperature, "Error")
    }
}
```

### Ошибка 6: Отсутствие разделения concerns в TCA Reducer

❌ **Неправильно:**

```swift
@Reducer
struct AppFeature {
    struct State {
        // Все состояние в одном месте - монолит
        var userName: String = ""
        var userEmail: String = ""
        var isUserLoggedIn = false
        var products: [Product] = []
        var cart: [CartItem] = []
        var selectedProductId: String?
        var isLoadingProducts = false
        var isLoadingCart = false
    }

    enum Action {
        // Все actions в одном месте - сложно поддерживать
        case userNameChanged(String)
        case userEmailChanged(String)
        case loginButtonTapped
        case loginResponse(Result<User, Error>)
        case fetchProducts
        case productsResponse([Product])
        case productTapped(String)
        case addToCart(Product)
        case removeFromCart(String)
        case checkoutTapped
    }

    // Огромный reducer с множественной ответственностью
    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .userNameChanged(let name):
                state.userName = name
                return .none
            case .loginButtonTapped:
                // Login логика
                return .none
            case .fetchProducts:
                // Products логика
                return .none
            case .addToCart(let product):
                // Cart логика
                return .none
            // ... еще 20 cases
            }
        }
    }
}
```

✅ **Правильно (композиция модульных reducers):**

```swift
// Модульные фичи с четким разделением

@Reducer
struct UserFeature {
    @ObservableState
    struct State: Equatable {
        var userName: String = ""
        var userEmail: String = ""
        var isLoggedIn = false
    }

    enum Action {
        case userNameChanged(String)
        case userEmailChanged(String)
        case loginButtonTapped
        case loginResponse(Result<User, Error>)
    }

    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .userNameChanged(let name):
                state.userName = name
                return .none

            case .loginButtonTapped:
                return .run { send in
                    // Login logic
                }

            case .loginResponse(.success):
                state.isLoggedIn = true
                return .none

            case .loginResponse(.failure):
                return .none

            case .userEmailChanged(let email):
                state.userEmail = email
                return .none
            }
        }
    }
}

@Reducer
struct ProductListFeature {
    @ObservableState
    struct State: Equatable {
        var products: [Product] = []
        var selectedProductId: String?
        var isLoading = false
    }

    enum Action {
        case fetchProducts
        case productsResponse([Product])
        case productTapped(String)
    }

    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .fetchProducts:
                state.isLoading = true
                return .run { send in
                    // Fetch logic
                }

            case .productsResponse(let products):
                state.products = products
                state.isLoading = false
                return .none

            case .productTapped(let id):
                state.selectedProductId = id
                return .none
            }
        }
    }
}

@Reducer
struct CartFeature {
    @ObservableState
    struct State: Equatable {
        var items: [CartItem] = []
        var isLoading = false
    }

    enum Action {
        case addItem(Product)
        case removeItem(String)
        case checkoutTapped
    }

    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .addItem(let product):
                state.items.append(CartItem(product: product))
                return .none

            case .removeItem(let id):
                state.items.removeAll { $0.id == id }
                return .none

            case .checkoutTapped:
                return .run { send in
                    // Checkout logic
                }
            }
        }
    }
}

// Композиция в root reducer
@Reducer
struct AppFeature {
    @ObservableState
    struct State: Equatable {
        var user = UserFeature.State()
        var productList = ProductListFeature.State()
        var cart = CartFeature.State()
    }

    enum Action {
        case user(UserFeature.Action)
        case productList(ProductListFeature.Action)
        case cart(CartFeature.Action)
    }

    var body: some ReducerOf<Self> {
        // Композиция независимых reducers
        Scope(state: \.user, action: \.user) {
            UserFeature()
        }

        Scope(state: \.productList, action: \.productList) {
            ProductListFeature()
        }

        Scope(state: \.cart, action: \.cart) {
            CartFeature()
        }

        // Root reducer для кросс-фича взаимодействий
        Reduce { state, action in
            switch action {
            case .productList(.productTapped(let productId)):
                // Можно реагировать на actions из других фич
                print("Product \(productId) selected")
                return .none

            case .user(.loginResponse(.success)):
                // После логина загрузить продукты
                return .send(.productList(.fetchProducts))

            default:
                return .none
            }
        }
    }
}

// View с четким scope для каждой фичи
struct AppView: View {
    let store: StoreOf<AppFeature>

    var body: some View {
        TabView {
            ProductListView(
                store: store.scope(state: \.productList, action: \.productList)
            )
            .tabItem { Label("Products", systemImage: "list.bullet") }

            CartView(
                store: store.scope(state: \.cart, action: \.cart)
            )
            .tabItem { Label("Cart", systemImage: "cart") }

            UserProfileView(
                store: store.scope(state: \.user, action: \.user)
            )
            .tabItem { Label("Profile", systemImage: "person") }
        }
    }
}
```

---

## Связанные материалы

- [[android-architecture-patterns]] — сравнение с Android подходами (MVI, Clean Architecture)
- [[swiftui-state-management]] — @State, @StateObject, @ObservedObject, @EnvironmentObject
- [[combine-framework]] — реактивное программирование для MVVM
- [[dependency-injection-ios]] — Swinject, Factory, manual DI
- [[unit-testing-ios]] — тестирование различных архитектурных слоев
- [[coordinator-pattern]] — паттерн навигации для UIKit и SwiftUI

## Дополнительные ресурсы

- [Apple WWDC: Data Flow Through SwiftUI](https://developer.apple.com/videos/play/wwdc2019/226/)
- [Point-Free: The Composable Architecture](https://www.pointfree.co/collections/composable-architecture)
- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [VIPER iOS Architecture Pattern](https://www.objc.io/issues/13-architecture/viper/)
- [Advanced iOS App Architecture (книга)](https://www.raywenderlich.com/books/advanced-ios-app-architecture)
