---
title: "Эволюция архитектуры iOS-приложений"
created: 2026-01-11
modified: 2026-01-11
type: overview
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/architecture
  - type/overview
  - level/intermediate
related:
  - "[[android-architecture-evolution]]"
  - "[[ios-architecture-patterns]]"
---

# Эволюция архитектуры iOS приложений

## TL;DR

История iOS архитектуры от простого MVC (2008) к современным декларативным подходам с SwiftUI и Observation framework (2025). Основные проблемы: Massive View Controller, управление состоянием, тестируемость. Решения эволюционировали от MVP/MVVM через VIPER к SwiftUI + TCA и @Observable. Выбор архитектуры зависит от размера команды, сложности приложения и необходимости поддержки UIKit.

---

## Временная шкала эволюции

```
2008        2010          2012-14      2015         2017         2019         2021         2023-25
 |           |              |           |            |            |            |            |
MVC      Проблема       MVP/MVVM    Reactive    Enterprise   SwiftUI     TCA v1.0   Observation
"Cocoa    Massive         Clean    ReactiveCocoa  VIPER      Paradigm    Gaining    @Observable
 MVC"   ViewController   Swift      + RxSwift    Explosion    Shift     Traction    Framework
 |           |              |           |            |            |            |            |
 └───────────┴──────────────┴───────────┴────────────┴────────────┴────────────┴────────────┘

             UIKit Era                                          SwiftUI Era
             ├──────────────────────────────────────────────────┤
             Focus: Separating concerns                         Focus: State management
             Challenge: View Controller complexity              Challenge: Unidirectional flow
```

---

## 2008: MVC "The Apple Way"

### Контекст
- iOS SDK 2.0, Objective-C единственный язык
- Apple продвигает традиционный MVC с UIViewController
- Малые приложения, простая бизнес-логика

### Характеристики
```
Model ←→ Controller ←→ View
```

- **Model**: Данные + бизнес-логика
- **View**: UIView, отображение
- **Controller**: UIViewController, посредник между Model и View

### Проблема
View Controller знает о View и Model, становится "God Object"

---

## 2010: Massive View Controller Problem

### Суть проблемы
UIViewController аккумулирует ответственность:
- View lifecycle (viewDidLoad, viewWillAppear)
- Networking и data fetching
- Business logic
- Navigation
- Delegates и data sources
- Анимации и transitions

### Типичные симптомы
- Файлы > 1000 строк кода
- Невозможность unit testing
- Сложность переиспользования
- Tight coupling между компонентами

---

## 2012-2014: MVP Adoption

### Архитектура
```
View ←→ Presenter ←→ Model
```

### Основная идея
- **View**: Пассивная, только отображение (UIViewController + UIView)
- **Presenter**: Вся логика презентации, готовит данные для View
- **Model**: Бизнес-логика и данные

### Преимущества
- Presenter тестируется без UI
- View становится "dumb", легко заменяется
- Четкое разделение ответственности

---

## 2015: MVVM + ReactiveCocoa

### Контекст
- Swift 2.0 набирает популярность
- ReactiveCocoa портирован на Swift
- Functional Reactive Programming входит в моду

### Архитектура
```
View ←──bindings──→ ViewModel ←→ Model
```

### Ключевые концепции
- **Data Binding**: View автоматически обновляется при изменении ViewModel
- **Reactive Streams**: SignalProducer, Signal для асинхронных операций
- **Command Pattern**: Инкапсуляция действий пользователя

### Преимущества
- Декларативный подход к UI обновлениям
- Отличная тестируемость ViewModel
- Reduction of boilerplate code

---

## 2017: VIPER for Enterprise

### Контекст
- Крупные enterprise приложения
- Большие команды разработчиков
- Необходимость четкого разделения модулей

### Архитектура
```
View ←→ Presenter ←→ Interactor
         ↓              ↓
      Router        Entities
```

**V** - View (отображение)
**I** - Interactor (бизнес-логика)
**P** - Presenter (логика презентации)
**E** - Entity (модели данных)
**R** - Router (навигация)

### Проблемы
- Overhead для малых/средних проектов
- Множество протоколов и файлов
- Steep learning curve
- Boilerplate код

---

## 2019: SwiftUI Changes Paradigm

### Революция
- Декларативный синтаксис UI
- State-driven architecture
- Встроенная реактивность
- Автоматический data binding

### Новые концепции
```swift
@State          // Локальное состояние View
@Binding        // Two-way binding
@ObservedObject // Reference type, внешнее состояние
@StateObject    // Владение ObservableObject
@EnvironmentObject // Dependency injection
```

### Архитектурный сдвиг
```
Old: View ← updates ← ViewModel
New: View = f(State)
```

View автоматически пересчитывается при изменении State

---

## 2021: TCA (The Composable Architecture)

### Контекст
- Point-Free представляет унификацию подхода
- Вдохновлено Redux и Elm Architecture
- Решает проблемы состояния в SwiftUI

### Основные компоненты
```swift
struct State { }        // Состояние приложения
enum Action { }         // Действия пользователя/системы
struct Environment { }  // Зависимости (API, DB)
let reducer: Reducer    // (State, Action) -> State
```

### Принципы
- **Single Source of Truth**: Одно дерево состояния
- **Unidirectional Data Flow**: Action → Reducer → State → View
- **Composition**: Малые reducers комбинируются
- **Side Effects**: Управляемые через Effect

### Преимущества
- Полностью предсказуемое состояние
- Отличная тестируемость
- Time-travel debugging
- Модульность

### Недостатки
- Сложность для простых приложений
- Performance overhead для больших State
- Steep learning curve

---

## 2023-2025: Observation Framework

### iOS 17+ нововведения
Apple представляет встроенный **Observation framework**

### @Observable макрос
```swift
@Observable
class UserProfileViewModel {
    var name: String = ""
    var email: String = ""
    var isLoading: Bool = false
}
```

### Преимущества над ObservableObject
- Автоматическое отслеживание изменений
- Нет необходимости в `@Published`
- Лучшая производительность (granular updates)
- Совместимость с Swift Concurrency

### Архитектурный паттерн
```
View observes @Observable Model
     ↓
SwiftUI automatically updates on changes
```

---

## Сравнительная таблица

| Архитектура | Год  | Тестируемость | Сложность | Use Case                    |
|-------------|------|---------------|-----------|----------------------------|
| MVC         | 2008 | Низкая        | Низкая    | Простые приложения         |
| MVP         | 2012 | Высокая       | Средняя   | UIKit приложения           |
| MVVM        | 2015 | Высокая       | Средняя   | UIKit с binding            |
| VIPER       | 2017 | Очень высокая | Высокая   | Enterprise проекты         |
| SwiftUI     | 2019 | Средняя       | Низкая    | Новые iOS 13+ проекты      |
| TCA         | 2021 | Очень высокая | Высокая   | Сложное state management   |
| @Observable | 2023 | Высокая       | Низкая    | iOS 17+ SwiftUI проекты    |

---

## 6 типичных ошибок при выборе архитектуры

### 1. Использование VIPER для малого проекта

❌ **Неправильно: Over-engineering**
```swift
// Для простого экрана списка создаётся 6 файлов:
TodoListView.swift
TodoListInteractor.swift
TodoListPresenter.swift
TodoListEntity.swift
TodoListRouter.swift
TodoListProtocols.swift

// Протоколов больше чем логики
protocol TodoListViewProtocol: AnyObject {
    func showTodos(_ todos: [TodoViewModel])
}
protocol TodoListPresenterProtocol: AnyObject {
    func viewDidLoad()
    func didSelectTodo(at index: Int)
}
// ... ещё 10 протоколов
```

✅ **Правильно: SwiftUI MVVM**
```swift
// Один файл для простого списка
@Observable
class TodoListViewModel {
    var todos: [Todo] = []

    func loadTodos() async {
        todos = await todoService.fetchTodos()
    }
}

struct TodoListView: View {
    @State private var viewModel = TodoListViewModel()

    var body: some View {
        List(viewModel.todos) { todo in
            Text(todo.title)
        }
        .task { await viewModel.loadTodos() }
    }
}
```

---

### 2. Massive View Controller в SwiftUI эпоху

❌ **Неправильно: Переносим UIKit привычки**
```swift
struct ProductDetailView: View {
    @State private var product: Product?
    @State private var reviews: [Review] = []
    @State private var relatedProducts: [Product] = []
    @State private var isLoading = false
    @State private var error: Error?

    var body: some View {
        ScrollView {
            // 500+ строк View кода с логикой
            if let product = product {
                VStack {
                    // Networking прямо в View
                    Button("Load Reviews") {
                        Task {
                            isLoading = true
                            do {
                                let url = URL(string: "https://api.com/reviews")!
                                let (data, _) = try await URLSession.shared.data(from: url)
                                reviews = try JSONDecoder().decode([Review].self, from: data)
                            } catch {
                                self.error = error
                            }
                            isLoading = false
                        }
                    }
                    // Business logic в View
                    Text(calculateDiscountPercentage())
                }
            }
        }
    }

    private func calculateDiscountPercentage() -> String {
        // Сложная бизнес-логика
        return "20%"
    }
}
```

✅ **Правильно: View + ViewModel разделение**
```swift
@Observable
class ProductDetailViewModel {
    var product: Product?
    var reviews: [Review] = []
    var relatedProducts: [Product] = []
    var isLoading = false
    var error: Error?

    private let productService: ProductService

    init(productService: ProductService = .shared) {
        self.productService = productService
    }

    func loadData() async {
        isLoading = true
        defer { isLoading = false }

        do {
            async let productTask = productService.fetchProduct()
            async let reviewsTask = productService.fetchReviews()
            async let relatedTask = productService.fetchRelated()

            (product, reviews, relatedProducts) = try await (productTask, reviewsTask, relatedTask)
        } catch {
            self.error = error
        }
    }

    var discountPercentage: String {
        guard let product = product else { return "" }
        let discount = (product.originalPrice - product.price) / product.originalPrice * 100
        return String(format: "%.0f%%", discount)
    }
}

struct ProductDetailView: View {
    @State private var viewModel = ProductDetailViewModel()

    var body: some View {
        ScrollView {
            if let product = viewModel.product {
                VStack {
                    ProductHeaderView(product: product)
                    Text("Discount: \(viewModel.discountPercentage)")
                    ReviewsListView(reviews: viewModel.reviews)
                    RelatedProductsView(products: viewModel.relatedProducts)
                }
            }
        }
        .task { await viewModel.loadData() }
        .overlay {
            if viewModel.isLoading {
                ProgressView()
            }
        }
    }
}
```

---

### 3. Игнорирование @Observable в iOS 17+

❌ **Неправильно: Старый ObservableObject с @Published**
```swift
class SettingsViewModel: ObservableObject {
    @Published var username: String = ""
    @Published var email: String = ""
    @Published var notifications: Bool = true
    @Published var darkMode: Bool = false
    @Published var fontSize: Double = 14.0

    // Каждое изменение триггерит полный re-render View
    func updateSettings() {
        // Даже если изменилось только username,
        // всё View перерисовывается
        objectWillChange.send()
    }
}

struct SettingsView: View {
    @StateObject private var viewModel = SettingsViewModel()

    var body: some View {
        Form {
            TextField("Username", text: $viewModel.username)
            TextField("Email", text: $viewModel.email)
            Toggle("Notifications", isOn: $viewModel.notifications)
            Toggle("Dark Mode", isOn: $viewModel.darkMode)
            Slider(value: $viewModel.fontSize, in: 10...24)
        }
    }
}
```

✅ **Правильно: @Observable с granular updates**
```swift
@Observable
class SettingsViewModel {
    var username: String = ""
    var email: String = ""
    var notifications: Bool = true
    var darkMode: Bool = false
    var fontSize: Double = 14.0

    // Observation framework автоматически отслеживает
    // какие свойства используются в каждом View
    // и обновляет только затронутые части
}

struct SettingsView: View {
    @State private var viewModel = SettingsViewModel()

    var body: some View {
        Form {
            // Только TextField для username перерисуется при изменении username
            TextField("Username", text: $viewModel.username)

            // Email TextField независим от username
            TextField("Email", text: $viewModel.email)

            Toggle("Notifications", isOn: $viewModel.notifications)
            Toggle("Dark Mode", isOn: $viewModel.darkMode)
            Slider(value: $viewModel.fontSize, in: 10...24)
        }
    }
}

// Более эффективный performance профиль:
// - Меньше re-renders
- Автоматический dependency tracking
// - Нет необходимости в @Published
```

---

### 4. Смешивание бизнес-логики и UI логики

❌ **Неправильно: Business rules в View**
```swift
struct CheckoutView: View {
    @State private var cartItems: [CartItem] = []
    @State private var promoCode: String = ""
    @State private var total: Double = 0

    var body: some View {
        VStack {
            ForEach(cartItems) { item in
                Text(item.name)
            }

            TextField("Promo Code", text: $promoCode)

            Button("Apply") {
                // Бизнес-логика прямо в View
                if promoCode == "SAVE20" {
                    total = cartItems.reduce(0) { $0 + $1.price } * 0.8
                } else if promoCode == "FREESHIP" {
                    let subtotal = cartItems.reduce(0) { $0 + $1.price }
                    total = subtotal
                } else if cartItems.count > 5 {
                    // Bulk discount logic
                    total = cartItems.reduce(0) { $0 + $1.price } * 0.9
                }

                // Tax calculation
                let taxRate = 0.13
                total += total * taxRate
            }

            Text("Total: $\(total, specifier: "%.2f")")
        }
    }
}
```

✅ **Правильно: Business logic в отдельном слое**
```swift
struct CheckoutCalculator {
    func calculateTotal(
        items: [CartItem],
        promoCode: String?
    ) -> CheckoutSummary {
        let subtotal = items.reduce(0) { $0 + $1.price }

        // Business rules инкапсулированы
        let discount = calculateDiscount(
            subtotal: subtotal,
            itemCount: items.count,
            promoCode: promoCode
        )

        let discountedTotal = subtotal - discount
        let tax = discountedTotal * 0.13
        let total = discountedTotal + tax

        return CheckoutSummary(
            subtotal: subtotal,
            discount: discount,
            tax: tax,
            total: total
        )
    }

    private func calculateDiscount(
        subtotal: Double,
        itemCount: Int,
        promoCode: String?
    ) -> Double {
        // Централизованная логика промо-кодов
        if promoCode == "SAVE20" {
            return subtotal * 0.2
        } else if promoCode == "FREESHIP" {
            return 5.99
        } else if itemCount > 5 {
            return subtotal * 0.1
        }
        return 0
    }
}

@Observable
class CheckoutViewModel {
    var cartItems: [CartItem] = []
    var promoCode: String = ""
    var summary: CheckoutSummary?

    private let calculator = CheckoutCalculator()

    func recalculate() {
        summary = calculator.calculateTotal(
            items: cartItems,
            promoCode: promoCode.isEmpty ? nil : promoCode
        )
    }
}

struct CheckoutView: View {
    @State private var viewModel = CheckoutViewModel()

    var body: some View {
        VStack {
            ForEach(viewModel.cartItems) { item in
                Text(item.name)
            }

            TextField("Promo Code", text: $viewModel.promoCode)
                .onChange(of: viewModel.promoCode) {
                    viewModel.recalculate()
                }

            if let summary = viewModel.summary {
                VStack(alignment: .leading) {
                    Text("Subtotal: $\(summary.subtotal, specifier: "%.2f")")
                    Text("Discount: -$\(summary.discount, specifier: "%.2f")")
                    Text("Tax: $\(summary.tax, specifier: "%.2f")")
                    Text("Total: $\(summary.total, specifier: "%.2f")")
                        .bold()
                }
            }
        }
    }
}
```

---

### 5. Отсутствие separation of concerns в networking

❌ **Неправильно: URLSession прямо в ViewModel**
```swift
@Observable
class UserProfileViewModel {
    var user: User?
    var error: String?

    func loadProfile() async {
        // Жёстко зашитый URL и логика парсинга
        let url = URL(string: "https://api.example.com/user/profile")!

        do {
            let (data, response) = try await URLSession.shared.data(from: url)

            guard let httpResponse = response as? HTTPURLResponse,
                  httpResponse.statusCode == 200 else {
                error = "Invalid response"
                return
            }

            // Парсинг прямо в ViewModel
            user = try JSONDecoder().decode(User.self, from: data)
        } catch {
            self.error = error.localizedDescription
        }
    }

    func updateBio(_ newBio: String) async {
        // Дублирование networking кода
        let url = URL(string: "https://api.example.com/user/bio")!
        var request = URLRequest(url: url)
        request.httpMethod = "PUT"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        // ...ещё 20 строк boilerplate
    }
}
```

✅ **Правильно: Repository pattern с dependency injection**
```swift
// Domain Layer - чистые модели и протоколы
protocol UserRepository {
    func fetchProfile() async throws -> User
    func updateBio(_ bio: String) async throws -> User
}

// Data Layer - конкретная имплементация
class APIUserRepository: UserRepository {
    private let networkClient: NetworkClient

    init(networkClient: NetworkClient = .shared) {
        self.networkClient = networkClient
    }

    func fetchProfile() async throws -> User {
        try await networkClient.request(
            endpoint: .userProfile,
            method: .get
        )
    }

    func updateBio(_ bio: String) async throws -> User {
        try await networkClient.request(
            endpoint: .userBio,
            method: .put,
            body: ["bio": bio]
        )
    }
}

// Presentation Layer - ViewModel зависит только от протокола
@Observable
class UserProfileViewModel {
    var user: User?
    var error: String?

    private let repository: UserRepository

    init(repository: UserRepository = APIUserRepository()) {
        self.repository = repository
    }

    func loadProfile() async {
        do {
            user = try await repository.fetchProfile()
        } catch {
            self.error = error.localizedDescription
        }
    }

    func updateBio(_ newBio: String) async {
        do {
            user = try await repository.updateBio(newBio)
        } catch {
            self.error = error.localizedDescription
        }
    }
}

// View остаётся неизменной, но легко тестируется
struct UserProfileView: View {
    @State private var viewModel = UserProfileViewModel()

    var body: some View {
        // ...
    }
}

// Unit тесты с mock repository
class MockUserRepository: UserRepository {
    var mockUser: User?
    var shouldThrowError = false

    func fetchProfile() async throws -> User {
        if shouldThrowError {
            throw URLError(.badServerResponse)
        }
        return mockUser ?? User.sample
    }

    func updateBio(_ bio: String) async throws -> User {
        var user = mockUser ?? User.sample
        user.bio = bio
        return user
    }
}
```

---

### 6. Неправильное управление navigation в SwiftUI

❌ **Неправильно: Navigation state в каждом View**
```swift
struct HomeView: View {
    @State private var showProfile = false
    @State private var showSettings = false
    @State private var selectedProduct: Product?
    @State private var showProductDetail = false

    var body: some View {
        NavigationStack {
            VStack {
                Button("Profile") {
                    showProfile = true
                }
                .sheet(isPresented: $showProfile) {
                    ProfileView()
                }

                Button("Settings") {
                    showSettings = true
                }
                .sheet(isPresented: $showSettings) {
                    SettingsView()
                }

                // Navigation logic размазана по View
                ForEach(products) { product in
                    Button(product.name) {
                        selectedProduct = product
                        showProductDetail = true
                    }
                }
            }
            .sheet(isPresented: $showProductDetail) {
                if let product = selectedProduct {
                    ProductDetailView(product: product)
                }
            }
        }
    }
}
```

✅ **Правильно: Coordinator pattern с enum routes**
```swift
// Определяем все возможные navigation routes
enum AppRoute: Hashable {
    case profile
    case settings
    case productDetail(Product)
    case checkout(items: [CartItem])
}

// Координатор управляет navigation state
@Observable
class NavigationCoordinator {
    var path: [AppRoute] = []
    var presentedSheet: AppRoute?

    func push(_ route: AppRoute) {
        path.append(route)
    }

    func present(_ route: AppRoute) {
        presentedSheet = route
    }

    func pop() {
        _ = path.popLast()
    }

    func popToRoot() {
        path.removeAll()
    }

    func dismiss() {
        presentedSheet = nil
    }
}

// Root View настраивает navigation
struct AppRootView: View {
    @State private var coordinator = NavigationCoordinator()

    var body: some View {
        NavigationStack(path: $coordinator.path) {
            HomeView()
                .navigationDestination(for: AppRoute.self) { route in
                    destinationView(for: route)
                }
                .sheet(item: $coordinator.presentedSheet) { route in
                    destinationView(for: route)
                }
        }
        .environment(coordinator)
    }

    @ViewBuilder
    private func destinationView(for route: AppRoute) -> some View {
        switch route {
        case .profile:
            ProfileView()
        case .settings:
            SettingsView()
        case .productDetail(let product):
            ProductDetailView(product: product)
        case .checkout(let items):
            CheckoutView(items: items)
        }
    }
}

// Views используют coordinator из environment
struct HomeView: View {
    @Environment(NavigationCoordinator.self) private var coordinator

    var body: some View {
        VStack {
            Button("Profile") {
                coordinator.present(.profile)
            }

            Button("Settings") {
                coordinator.push(.settings)
            }

            ForEach(products) { product in
                Button(product.name) {
                    coordinator.push(.productDetail(product))
                }
            }
        }
    }
}

// Преимущества:
// ✅ Centralized navigation logic
// ✅ Deep linking support (восстановление path из URL)
// ✅ Легко тестировать navigation flows
// ✅ Type-safe routes
```

---

## Decision Tree: Выбор архитектуры для нового проекта

```
Начинаем новый iOS проект
         |
         ├─ Minimum iOS version?
         │
         ├─ iOS 17+ ?
         │   └─ YES → SwiftUI + @Observable
         │       ├─ Простое приложение (1-5 экранов)
         │       │   └─ SwiftUI + View Models
         │       │
         │       ├─ Среднее (5-20 экранов)
         │       │   └─ SwiftUI + MVVM + Coordinator
         │       │
         │       └─ Сложное state management
         │           └─ TCA (The Composable Architecture)
         │
         ├─ iOS 13-16 ?
         │   └─ YES → SwiftUI + ObservableObject
         │       └─ Или UIKit + MVVM
         │
         └─ iOS 11-12 ?
             └─ YES → UIKit only
                 ├─ Малый проект → MVVM
                 ├─ Средний → MVVM + Coordinator
                 └─ Enterprise → VIPER (если команда > 10)
```

### Критерии выбора

**SwiftUI + @Observable (iOS 17+)**
- ✅ Новые проекты без legacy code
- ✅ Команда знает Swift Concurrency
- ✅ Не требуется сложная UIKit интеграция
- ❌ Нужна поддержка iOS < 17

**SwiftUI + TCA**
- ✅ Сложное state management (финансы, соцсети)
- ✅ Требуется time-travel debugging
- ✅ Большая команда, нужна consistency
- ❌ Малый проект (overkill)
- ❌ Performance critical (игры)

**UIKit + MVVM**
- ✅ Существующий UIKit проект
- ✅ Команда не готова к SwiftUI
- ✅ Нужен полный контроль над UI
- ✅ Performance critical UI

**VIPER**
- ✅ Enterprise проект, команда > 10 разработчиков
- ✅ Чёткое разделение модулей необходимо
- ❌ Малые/средние проекты
- ❌ Быстрая разработка MVP

---

## Миграционные стратегии

### UIKit → SwiftUI

```swift
// Этап 1: Обернуть UIViewController в SwiftUI
struct LegacyViewControllerWrapper: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> SomeLegacyVC {
        SomeLegacyVC()
    }

    func updateUIViewController(_ uiViewController: SomeLegacyVC, context: Context) {
        // Update if needed
    }
}

// Этап 2: Новые экраны на SwiftUI
struct NewFeatureView: View {
    var body: some View {
        // Pure SwiftUI
    }
}

// Этап 3: Постепенно переписывать legacy экраны
```

### ObservableObject → @Observable

```swift
// Было
class OldViewModel: ObservableObject {
    @Published var title: String = ""
    @Published var count: Int = 0
}

// Стало (iOS 17+)
@Observable
class NewViewModel {
    var title: String = ""
    var count: Int = 0
}

// Views автоматически совместимы!
struct MyView: View {
    @State private var viewModel = NewViewModel()
    // Работает одинаково
}
```

---

## Рекомендации на 2025-2026

### Для новых проектов
1. **SwiftUI-first подход** если minimum iOS 15+
2. **@Observable вместо ObservableObject** для iOS 17+
3. **Swift Concurrency (async/await)** вместо Combine
4. **Coordinator pattern** для navigation
5. **Repository pattern** для data layer

### Для legacy проектов
1. Новые фичи на SwiftUI, оборачивать в UIHostingController
2. Рефакторинг Massive View Controllers → MVVM
3. Миграция на async/await постепенно
4. Модуляризация через Swift Package Manager

### Универсальные принципы
- **Separation of concerns** всегда актуально
- **Dependency injection** для тестируемости
- **Protocol-oriented programming** для гибкости
- **Composition over inheritance**
- **Unidirectional data flow** упрощает debugging

---

## Полезные ссылки

- [Apple Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [Swift Evolution](https://github.com/apple/swift-evolution)
- [Point-Free TCA](https://github.com/pointfreeco/swift-composable-architecture)
- [Observation Framework WWDC23](https://developer.apple.com/wwdc23/10149)

## Related Notes
- [[android-architecture-evolution]] - сравнение с Android подходами
- [[swiftui-performance-optimization]] - оптимизация SwiftUI
- [[ios-testing-strategies]] - тестирование разных архитектур
- [[dependency-injection-patterns]] - DI в iOS
