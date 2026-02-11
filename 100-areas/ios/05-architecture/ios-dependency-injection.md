---
title: "Dependency Injection в iOS"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/dependency-injection
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-dependency-injection]]"
  - "[[ios-architecture-patterns]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-architecture-patterns]]"
---

# iOS Dependency Injection

## TL;DR

Dependency Injection (DI) в iOS — это паттерн, позволяющий передавать зависимости объектам извне вместо их создания внутри. От простого constructor injection до мощных фреймворков (Swinject, Needle), от property wrappers до SwiftUI Environment — выбор зависит от масштаба проекта. DI критически важен для тестирования, модульности и соблюдения SOLID принципов.

## Аналогии

**Ресторан и поставки**: Представьте ресторан (ваш класс). Вместо того чтобы повар выращивал овощи и разводил скот (создавал зависимости внутри), ресторан получает продукты от поставщиков (dependency injection). Это позволяет легко менять поставщиков (mock для тестов) и не зависеть от конкретной фермы.

**Электроприбор и розетка**: Ваш iPhone не содержит электростанцию внутри — он получает энергию через зарядное устройство (интерфейс). Вы можете подключить его к любому источнику питания, соответствующему спецификации (протоколу).

**Актёр и реквизит**: Актёр не создаёт реквизит на сцене — ему передают нужные предметы. Это позволяет использовать разный реквизит для разных постановок (разные реализации зависимостей).

## Диаграммы

### Архитектура DI в iOS приложении

```
┌─────────────────────────────────────────────────────────┐
│                    iOS Application                       │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   View/UI    │────────>│  ViewModel   │             │
│  │  (SwiftUI)   │         │              │             │
│  └──────────────┘         └──────┬───────┘             │
│         │                        │                      │
│         │ @Environment           │ Constructor          │
│         │ @EnvironmentObject     │ Injection            │
│         │                        │                      │
│         v                        v                      │
│  ┌──────────────────────────────────────┐              │
│  │       Dependency Container           │              │
│  │  (Swinject/Needle/Custom)            │              │
│  └──────────────┬───────────────────────┘              │
│                 │                                       │
│                 │ Resolves & Injects                    │
│                 v                                       │
│  ┌──────────────────────────────────────┐              │
│  │          Services Layer              │              │
│  │  ┌────────────┐  ┌────────────┐     │              │
│  │  │  Network   │  │  Storage   │     │              │
│  │  │  Service   │  │  Service   │     │              │
│  │  └────────────┘  └────────────┘     │              │
│  │  ┌────────────┐  ┌────────────┐     │              │
│  │  │   Auth     │  │ Analytics  │     │              │
│  │  │  Service   │  │  Service   │     │              │
│  │  └────────────┘  └────────────┘     │              │
│  └──────────────────────────────────────┘              │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### DI Patterns Comparison

```
┌──────────────────┬─────────────┬──────────────┬─────────────┐
│   Pattern        │ Complexity  │  Type Safety │  Use Case   │
├──────────────────┼─────────────┼──────────────┼─────────────┤
│ Constructor DI   │     ★☆☆     │     ★★★      │   Small     │
│ Property DI      │     ★☆☆     │     ★★☆      │   Small     │
│ Method DI        │     ★☆☆     │     ★★★      │   Specific  │
│ @Environment     │     ★★☆     │     ★★★      │   SwiftUI   │
│ Property Wrapper │     ★★☆     │     ★★☆      │   Medium    │
│ Swinject         │     ★★★     │     ★★☆      │   Large     │
│ Needle           │     ★★★     │     ★★★      │   Large     │
│ Service Locator  │     ★☆☆     │     ★☆☆      │   Avoid!    │
└──────────────────┴─────────────┴──────────────┴─────────────┘
```

### Dependency Resolution Flow

```
App Launch
    │
    ├─> Create DI Container
    │   │
    │   ├─> Register Services
    │   │   ├─> Singleton instances
    │   │   ├─> Transient instances
    │   │   └─> Factory closures
    │   │
    │   └─> Build dependency graph
    │
    ├─> Resolve Root Dependencies
    │   │
    │   └─> Inject into ViewModels/Services
    │
    └─> App Ready
        │
        ├─> Runtime Resolution
        │   ├─> View needs ViewModel
        │   ├─> Container resolves
        │   └─> Injects dependencies
        │
        └─> Testing
            ├─> Override registrations
            ├─> Inject mocks
            └─> Run tests
```

## 1. Ручная Dependency Injection

### Constructor Injection (рекомендуется)

```swift
// Protocol для абстракции
protocol NetworkService {
    func fetchData() async throws -> Data
}

protocol StorageService {
    func save(_ data: Data) throws
    func load() throws -> Data
}

// Реализации
final class URLSessionNetworkService: NetworkService {
    func fetchData() async throws -> Data {
        let (data, _) = try await URLSession.shared.data(from: URL(string: "https://api.example.com")!)
        return data
    }
}

final class UserDefaultsStorageService: StorageService {
    private let key = "cached_data"

    func save(_ data: Data) throws {
        UserDefaults.standard.set(data, forKey: key)
    }

    func load() throws -> Data {
        guard let data = UserDefaults.standard.data(forKey: key) else {
            throw StorageError.notFound
        }
        return data
    }
}

// ViewModel с constructor injection
final class DataViewModel: ObservableObject {
    @Published var data: String = ""
    @Published var isLoading = false

    private let networkService: NetworkService
    private let storageService: StorageService

    // ✅ Зависимости передаются через конструктор
    init(
        networkService: NetworkService,
        storageService: StorageService
    ) {
        self.networkService = networkService
        self.storageService = storageService
    }

    func loadData() async {
        isLoading = true
        defer { isLoading = false }

        do {
            // Сначала пробуем загрузить из кэша
            if let cached = try? storageService.load() {
                data = String(data: cached, encoding: .utf8) ?? ""
                return
            }

            // Загружаем из сети
            let fetchedData = try await networkService.fetchData()
            try storageService.save(fetchedData)
            data = String(data: fetchedData, encoding: .utf8) ?? ""
        } catch {
            print("Error: \(error)")
        }
    }
}
```

### Method Injection

```swift
final class ReportGenerator {
    func generateReport(
        data: [String],
        formatter: ReportFormatter  // ✅ Зависимость передаётся в метод
    ) -> String {
        return formatter.format(data)
    }
}

protocol ReportFormatter {
    func format(_ data: [String]) -> String
}

struct PDFReportFormatter: ReportFormatter {
    func format(_ data: [String]) -> String {
        "PDF: \(data.joined(separator: "\n"))"
    }
}

struct HTMLReportFormatter: ReportFormatter {
    func format(_ data: [String]) -> String {
        "<html><body>\(data.joined(separator: "<br>"))</body></html>"
    }
}

// Использование
let generator = ReportGenerator()
let pdfReport = generator.generateReport(data: ["Line 1", "Line 2"], formatter: PDFReportFormatter())
let htmlReport = generator.generateReport(data: ["Line 1", "Line 2"], formatter: HTMLReportFormatter())
```

### Property Injection (не рекомендуется для обязательных зависимостей)

```swift
final class LegacyViewController: UIViewController {
    // ❌ Опасно: зависимость может быть nil
    var dataService: DataService?

    override func viewDidLoad() {
        super.viewDidLoad()
        // Может привести к краху приложения
        dataService?.loadData()
    }
}

// ✅ Лучше использовать constructor injection
final class ModernViewController: UIViewController {
    private let dataService: DataService

    init(dataService: DataService) {
        self.dataService = dataService
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("Use init(dataService:)")
    }
}
```

## 2. Property Wrapper DI (@Inject Pattern)

```swift
// Простой DI Container
final class DIContainer {
    static let shared = DIContainer()
    private var services: [String: Any] = [:]

    func register<T>(_ type: T.Type, factory: @escaping () -> T) {
        let key = String(describing: type)
        services[key] = factory
    }

    func resolve<T>(_ type: T.Type) -> T {
        let key = String(describing: type)
        guard let factory = services[key] as? () -> T else {
            fatalError("Service \(key) not registered")
        }
        return factory()
    }
}

// Property Wrapper для инъекции
@propertyWrapper
struct Inject<T> {
    private var service: T?

    var wrappedValue: T {
        mutating get {
            if service == nil {
                service = DIContainer.shared.resolve(T.self)
            }
            return service!
        }
    }

    init() {}
}

// Использование
final class UserViewModel: ObservableObject {
    @Inject private var authService: AuthService
    @Inject private var analyticsService: AnalyticsService

    func login(email: String, password: String) async throws {
        try await authService.login(email: email, password: password)
        analyticsService.track(event: "user_logged_in")
    }
}

// Регистрация в AppDelegate или @main
@main
struct MyApp: App {
    init() {
        setupDependencies()
    }

    private func setupDependencies() {
        DIContainer.shared.register(AuthService.self) {
            FirebaseAuthService()
        }
        DIContainer.shared.register(AnalyticsService.self) {
            MixpanelAnalyticsService()
        }
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

## 3. Swinject Framework

```swift
import Swinject

// Создание контейнера
let container = Container()

// Регистрация зависимостей
container.register(NetworkService.self) { _ in
    URLSessionNetworkService()
}.inObjectScope(.container)  // Singleton

container.register(StorageService.self) { _ in
    UserDefaultsStorageService()
}.inObjectScope(.transient)  // Новый экземпляр каждый раз

container.register(DataViewModel.self) { resolver in
    DataViewModel(
        networkService: resolver.resolve(NetworkService.self)!,
        storageService: resolver.resolve(StorageService.self)!
    )
}

// Регистрация с параметрами
container.register(UserProfileViewModel.self) { (resolver, userId: String) in
    UserProfileViewModel(
        userId: userId,
        networkService: resolver.resolve(NetworkService.self)!
    )
}

// Использование
let viewModel = container.resolve(DataViewModel.self)!
let profileVM = container.resolve(UserProfileViewModel.self, argument: "user123")!

// Assembly для модульной регистрации
final class ServiceAssembly: Assembly {
    func assemble(container: Container) {
        container.register(NetworkService.self) { _ in
            URLSessionNetworkService()
        }.inObjectScope(.container)

        container.register(StorageService.self) { _ in
            UserDefaultsStorageService()
        }
    }
}

final class ViewModelAssembly: Assembly {
    func assemble(container: Container) {
        container.register(DataViewModel.self) { resolver in
            DataViewModel(
                networkService: resolver.resolve(NetworkService.self)!,
                storageService: resolver.resolve(StorageService.self)!
            )
        }
    }
}

// Использование Assemblies
let assembler = Assembler([
    ServiceAssembly(),
    ViewModelAssembly()
])

let viewModel = assembler.resolver.resolve(DataViewModel.self)!
```

## 4. Needle Framework (Uber)

```swift
import NeedleFoundation

// Root Component
final class RootComponent: BootstrapComponent {
    var networkService: NetworkService {
        return shared {
            URLSessionNetworkService()
        }
    }

    var storageService: StorageService {
        return shared {
            UserDefaultsStorageService()
        }
    }
}

// Feature Component
protocol DataDependency: Dependency {
    var networkService: NetworkService { get }
    var storageService: StorageService { get }
}

final class DataComponent: Component<DataDependency> {
    var viewModel: DataViewModel {
        return DataViewModel(
            networkService: dependency.networkService,
            storageService: dependency.storageService
        )
    }
}

// Использование в SwiftUI
@main
struct MyApp: App {
    init() {
        registerProviderFactories()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}

struct ContentView: View {
    private let component = RootComponent()

    var body: some View {
        let dataComponent = component.dataComponent
        DataView(viewModel: dataComponent.viewModel)
    }
}

// Needle генерирует код через build phase script
// needle generate Sources/App NeedleGenerated.swift
```

## 5. Factory Pattern для DI

```swift
// Factory для создания зависимостей
enum ServiceFactory {
    static func makeNetworkService() -> NetworkService {
        #if DEBUG
        if ProcessInfo.processInfo.environment["UI_TESTING"] == "1" {
            return MockNetworkService()
        }
        #endif
        return URLSessionNetworkService()
    }

    static func makeStorageService() -> StorageService {
        #if DEBUG
        if ProcessInfo.processInfo.environment["UI_TESTING"] == "1" {
            return InMemoryStorageService()
        }
        #endif
        return UserDefaultsStorageService()
    }

    static func makeDataViewModel() -> DataViewModel {
        DataViewModel(
            networkService: makeNetworkService(),
            storageService: makeStorageService()
        )
    }
}

// Использование
let viewModel = ServiceFactory.makeDataViewModel()

// Abstract Factory для семейства связанных объектов
protocol ServiceFactoryProtocol {
    func makeNetworkService() -> NetworkService
    func makeStorageService() -> StorageService
}

struct ProductionServiceFactory: ServiceFactoryProtocol {
    func makeNetworkService() -> NetworkService {
        URLSessionNetworkService()
    }

    func makeStorageService() -> StorageService {
        UserDefaultsStorageService()
    }
}

struct TestServiceFactory: ServiceFactoryProtocol {
    func makeNetworkService() -> NetworkService {
        MockNetworkService()
    }

    func makeStorageService() -> StorageService {
        InMemoryStorageService()
    }
}

// Композиция фабрик
final class AppFactory {
    private let serviceFactory: ServiceFactoryProtocol

    init(serviceFactory: ServiceFactoryProtocol) {
        self.serviceFactory = serviceFactory
    }

    func makeDataViewModel() -> DataViewModel {
        DataViewModel(
            networkService: serviceFactory.makeNetworkService(),
            storageService: serviceFactory.makeStorageService()
        )
    }
}
```

## 6. SwiftUI @Environment для DI

```swift
// Создание Environment Key
struct NetworkServiceKey: EnvironmentKey {
    static let defaultValue: NetworkService = URLSessionNetworkService()
}

struct StorageServiceKey: EnvironmentKey {
    static let defaultValue: StorageService = UserDefaultsStorageService()
}

// Расширение EnvironmentValues
extension EnvironmentValues {
    var networkService: NetworkService {
        get { self[NetworkServiceKey.self] }
        set { self[NetworkServiceKey.self] = newValue }
    }

    var storageService: StorageService {
        get { self[StorageServiceKey.self] }
        set { self[StorageServiceKey.self] = newValue }
    }
}

// Использование в View
struct DataView: View {
    @Environment(\.networkService) private var networkService
    @Environment(\.storageService) private var storageService
    @State private var data: String = ""

    var body: some View {
        VStack {
            Text(data)
            Button("Load Data") {
                Task {
                    do {
                        let fetchedData = try await networkService.fetchData()
                        data = String(data: fetchedData, encoding: .utf8) ?? ""
                        try storageService.save(fetchedData)
                    } catch {
                        print("Error: \(error)")
                    }
                }
            }
        }
    }
}

// Инъекция зависимостей в приложении
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.networkService, URLSessionNetworkService())
                .environment(\.storageService, UserDefaultsStorageService())
        }
    }
}

// Для тестирования или previews
struct DataView_Previews: PreviewProvider {
    static var previews: some View {
        DataView()
            .environment(\.networkService, MockNetworkService())
            .environment(\.storageService, InMemoryStorageService())
    }
}
```

## 7. @EnvironmentObject как DI Container

```swift
// Service Container как ObservableObject
final class ServiceContainer: ObservableObject {
    let networkService: NetworkService
    let storageService: StorageService
    let authService: AuthService
    let analyticsService: AnalyticsService

    init(
        networkService: NetworkService = URLSessionNetworkService(),
        storageService: StorageService = UserDefaultsStorageService(),
        authService: AuthService = FirebaseAuthService(),
        analyticsService: AnalyticsService = MixpanelAnalyticsService()
    ) {
        self.networkService = networkService
        self.storageService = storageService
        self.authService = authService
        self.analyticsService = analyticsService
    }

    // Для тестирования
    static var mock: ServiceContainer {
        ServiceContainer(
            networkService: MockNetworkService(),
            storageService: InMemoryStorageService(),
            authService: MockAuthService(),
            analyticsService: MockAnalyticsService()
        )
    }
}

// Использование в View
struct ContentView: View {
    @EnvironmentObject private var services: ServiceContainer
    @StateObject private var viewModel: DataViewModel

    init() {
        // ⚠️ Не можем использовать @EnvironmentObject в init
        // Используем wrapper для lazy initialization
        _viewModel = StateObject(wrappedValue: DataViewModel(
            networkService: URLSessionNetworkService(),
            storageService: UserDefaultsStorageService()
        ))
    }

    var body: some View {
        VStack {
            Text("Content")
        }
        .onAppear {
            // Доступ к services после инициализации
            viewModel.updateServices(
                network: services.networkService,
                storage: services.storageService
            )
        }
    }
}

// Лучший подход: View без ViewModel в init
struct ImprovedContentView: View {
    @EnvironmentObject private var services: ServiceContainer

    var body: some View {
        let viewModel = DataViewModel(
            networkService: services.networkService,
            storageService: services.storageService
        )

        DataDetailView(viewModel: viewModel)
    }
}

// В App
@main
struct MyApp: App {
    @StateObject private var services = ServiceContainer()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(services)
        }
    }
}

// Previews
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(ServiceContainer.mock)
    }
}
```

## 8. Service Locator (Anti-Pattern)

```swift
// ❌ Service Locator - избегайте этого паттерна
final class ServiceLocator {
    static let shared = ServiceLocator()

    private var services: [String: Any] = [:]

    private init() {}

    func register<T>(_ type: T.Type, service: T) {
        let key = String(describing: type)
        services[key] = service
    }

    func get<T>(_ type: T.Type) -> T? {
        let key = String(describing: type)
        return services[key] as? T
    }
}

// ❌ Проблемы Service Locator
final class BadViewModel: ObservableObject {
    func loadData() {
        // ❌ Скрытая зависимость - не видна в сигнатуре класса
        guard let networkService = ServiceLocator.shared.get(NetworkService.self) else {
            fatalError("NetworkService not registered")
        }

        // ❌ Runtime ошибки вместо compile-time
        // ❌ Сложно тестировать - глобальное состояние
        // ❌ Нарушает принцип Inversion of Control
    }
}

// ✅ Правильный подход - явная инъекция зависимостей
final class GoodViewModel: ObservableObject {
    private let networkService: NetworkService

    // ✅ Зависимость явная и видна в сигнатуре
    init(networkService: NetworkService) {
        self.networkService = networkService
    }

    // ✅ Compile-time безопасность
    // ✅ Легко тестировать
    // ✅ Следует принципам SOLID
}

// Когда Service Locator допустим (очень редко):
// 1. Legacy код, который невозможно рефакторить
// 2. Framework constraints (UIViewController от Storyboard)
// 3. Миграция от старой архитектуры

// ✅ Если необходимо, используйте в связке с явной DI
final class HybridViewController: UIViewController {
    // ✅ Инъекция через property после создания из Storyboard
    var viewModel: ViewModel!

    override func viewDidLoad() {
        super.viewDidLoad()
        // Fallback на Service Locator только если не инъектировано
        if viewModel == nil {
            viewModel = ServiceLocator.shared.get(ViewModel.self)
        }
    }
}
```

## 9. DI в Preview Providers

```swift
// Mock реализации для Previews
final class MockNetworkService: NetworkService {
    var mockData: Data = Data()
    var shouldThrowError = false

    func fetchData() async throws -> Data {
        if shouldThrowError {
            throw NetworkError.serverError
        }
        return mockData
    }
}

final class InMemoryStorageService: StorageService {
    private var storage: Data?

    func save(_ data: Data) throws {
        storage = data
    }

    func load() throws -> Data {
        guard let data = storage else {
            throw StorageError.notFound
        }
        return data
    }
}

// Preview с разными состояниями
struct DataView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            // Успешная загрузка
            DataView(viewModel: makeViewModel(with: "Success"))
                .previewDisplayName("Success State")

            // Загрузка
            DataView(viewModel: makeLoadingViewModel())
                .previewDisplayName("Loading State")

            // Ошибка
            DataView(viewModel: makeErrorViewModel())
                .previewDisplayName("Error State")

            // Пустое состояние
            DataView(viewModel: makeEmptyViewModel())
                .previewDisplayName("Empty State")
        }
    }

    static func makeViewModel(with data: String) -> DataViewModel {
        let mockNetwork = MockNetworkService()
        mockNetwork.mockData = data.data(using: .utf8)!

        return DataViewModel(
            networkService: mockNetwork,
            storageService: InMemoryStorageService()
        )
    }

    static func makeLoadingViewModel() -> DataViewModel {
        let viewModel = makeViewModel(with: "")
        Task {
            await viewModel.loadData()
        }
        return viewModel
    }

    static func makeErrorViewModel() -> DataViewModel {
        let mockNetwork = MockNetworkService()
        mockNetwork.shouldThrowError = true

        return DataViewModel(
            networkService: mockNetwork,
            storageService: InMemoryStorageService()
        )
    }

    static func makeEmptyViewModel() -> DataViewModel {
        makeViewModel(with: "")
    }
}

// Preview с @Environment
struct EnvironmentDataView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            DataView()
                .environment(\.networkService, makeMockNetworkService(data: "Success"))
                .previewDisplayName("Success")

            DataView()
                .environment(\.networkService, makeMockNetworkService(shouldFail: true))
                .previewDisplayName("Error")
        }
    }

    static func makeMockNetworkService(data: String = "", shouldFail: Bool = false) -> NetworkService {
        let mock = MockNetworkService()
        mock.mockData = data.data(using: .utf8) ?? Data()
        mock.shouldThrowError = shouldFail
        return mock
    }
}

// Preview с @EnvironmentObject
struct EnvironmentObjectView_Previews: PreviewProvider {
    static var previews: some View {
        ImprovedContentView()
            .environmentObject(makePreviewServices())
    }

    static func makePreviewServices() -> ServiceContainer {
        ServiceContainer(
            networkService: MockNetworkService(),
            storageService: InMemoryStorageService(),
            authService: MockAuthService(),
            analyticsService: MockAnalyticsService()
        )
    }
}
```

## 10. Тестирование с Mock Injection

```swift
import XCTest
@testable import MyApp

// Mock implementations
final class MockNetworkService: NetworkService {
    var fetchDataCalled = false
    var fetchDataCallCount = 0
    var mockResult: Result<Data, Error> = .success(Data())

    func fetchData() async throws -> Data {
        fetchDataCalled = true
        fetchDataCallCount += 1

        switch mockResult {
        case .success(let data):
            return data
        case .failure(let error):
            throw error
        }
    }
}

final class MockStorageService: StorageService {
    var saveCalled = false
    var loadCalled = false
    var savedData: Data?
    var mockLoadResult: Result<Data, Error> = .failure(StorageError.notFound)

    func save(_ data: Data) throws {
        saveCalled = true
        savedData = data
    }

    func load() throws -> Data {
        loadCalled = true
        return try mockLoadResult.get()
    }
}

// Unit Tests
final class DataViewModelTests: XCTestCase {
    var sut: DataViewModel!
    var mockNetwork: MockNetworkService!
    var mockStorage: MockStorageService!

    override func setUp() {
        super.setUp()
        mockNetwork = MockNetworkService()
        mockStorage = MockStorageService()
        sut = DataViewModel(
            networkService: mockNetwork,
            storageService: mockStorage
        )
    }

    override func tearDown() {
        sut = nil
        mockNetwork = nil
        mockStorage = nil
        super.tearDown()
    }

    func testLoadData_WhenCacheExists_LoadsFromCache() async throws {
        // Arrange
        let cachedData = "Cached".data(using: .utf8)!
        mockStorage.mockLoadResult = .success(cachedData)

        // Act
        await sut.loadData()

        // Assert
        XCTAssertTrue(mockStorage.loadCalled)
        XCTAssertFalse(mockNetwork.fetchDataCalled)
        XCTAssertEqual(sut.data, "Cached")
    }

    func testLoadData_WhenNoCacheExists_FetchesFromNetwork() async throws {
        // Arrange
        let networkData = "Network".data(using: .utf8)!
        mockNetwork.mockResult = .success(networkData)
        mockStorage.mockLoadResult = .failure(StorageError.notFound)

        // Act
        await sut.loadData()

        // Assert
        XCTAssertTrue(mockNetwork.fetchDataCalled)
        XCTAssertTrue(mockStorage.saveCalled)
        XCTAssertEqual(sut.data, "Network")
        XCTAssertEqual(mockStorage.savedData, networkData)
    }

    func testLoadData_WhenNetworkFails_HandlesError() async throws {
        // Arrange
        mockNetwork.mockResult = .failure(NetworkError.serverError)
        mockStorage.mockLoadResult = .failure(StorageError.notFound)

        // Act
        await sut.loadData()

        // Assert
        XCTAssertTrue(mockNetwork.fetchDataCalled)
        XCTAssertFalse(mockStorage.saveCalled)
        XCTAssertTrue(sut.data.isEmpty)
    }

    func testLoadData_SetsLoadingState() async {
        // Arrange
        mockNetwork.mockResult = .success(Data())

        // Act
        let expectation = expectation(description: "Loading state")
        Task {
            XCTAssertTrue(sut.isLoading)
            await sut.loadData()
            XCTAssertFalse(sut.isLoading)
            expectation.fulfill()
        }

        // Assert
        await fulfillment(of: [expectation], timeout: 1)
    }
}

// Integration Tests с реальным DI Container
final class DIContainerIntegrationTests: XCTestCase {
    var container: Container!

    override func setUp() {
        super.setUp()
        container = Container()

        // Регистрируем моки вместо реальных сервисов
        container.register(NetworkService.self) { _ in
            MockNetworkService()
        }

        container.register(StorageService.self) { _ in
            MockStorageService()
        }

        container.register(DataViewModel.self) { resolver in
            DataViewModel(
                networkService: resolver.resolve(NetworkService.self)!,
                storageService: resolver.resolve(StorageService.self)!
            )
        }
    }

    func testContainerResolvesViewModel() {
        // Act
        let viewModel = container.resolve(DataViewModel.self)

        // Assert
        XCTAssertNotNil(viewModel)
    }

    func testContainerInjectsMockDependencies() {
        // Act
        let viewModel = container.resolve(DataViewModel.self)!

        // Assert - проверяем что инъектированы моки
        let mirror = Mirror(reflecting: viewModel)
        let networkService = mirror.children.first { $0.label == "networkService" }?.value
        XCTAssertTrue(networkService is MockNetworkService)
    }
}

// UI Tests с Environment injection
final class DataViewUITests: XCTestCase {
    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchEnvironment = ["UI_TESTING": "1"]
        app.launch()
    }

    func testDataView_LoadsAndDisplaysData() {
        // Arrange - app автоматически использует моки через Environment

        // Act
        app.buttons["Load Data"].tap()

        // Assert
        XCTAssertTrue(app.staticTexts["Mock Data"].waitForExistence(timeout: 2))
    }
}

// Test Helpers
enum TestDIContainer {
    static func makeTestViewModel(
        networkResult: Result<Data, Error> = .success(Data()),
        storageResult: Result<Data, Error> = .failure(StorageError.notFound)
    ) -> DataViewModel {
        let mockNetwork = MockNetworkService()
        mockNetwork.mockResult = networkResult

        let mockStorage = MockStorageService()
        mockStorage.mockLoadResult = storageResult

        return DataViewModel(
            networkService: mockNetwork,
            storageService: mockStorage
        )
    }
}
```

## 6 Типичных Ошибок

### Ошибка 1: Создание зависимостей внутри класса

❌ **Неправильно:**
```swift
final class UserViewModel: ObservableObject {
    private let networkService = URLSessionNetworkService()  // ❌ Жёсткая связь
    private let storage = UserDefaultsStorageService()       // ❌ Невозможно тестировать

    func loadUser() async {
        // Невозможно заменить на mock
        let data = try? await networkService.fetchUser()
    }
}

// Тест будет делать реальные сетевые запросы!
func testLoadUser() async {
    let viewModel = UserViewModel()  // ❌ Использует реальные сервисы
    await viewModel.loadUser()
}
```

✅ **Правильно:**
```swift
final class UserViewModel: ObservableObject {
    private let networkService: NetworkService      // ✅ Protocol
    private let storage: StorageService             // ✅ Protocol

    init(networkService: NetworkService, storage: StorageService) {
        self.networkService = networkService        // ✅ Инъекция через конструктор
        self.storage = storage
    }

    func loadUser() async {
        let data = try? await networkService.fetchUser()
    }
}

// Тест использует моки
func testLoadUser() async {
    let mockNetwork = MockNetworkService()
    let mockStorage = MockStorageService()
    let viewModel = UserViewModel(
        networkService: mockNetwork,               // ✅ Контроль над зависимостями
        storage: mockStorage
    )
    await viewModel.loadUser()
}
```

### Ошибка 2: Использование Service Locator вместо DI

❌ **Неправильно:**
```swift
final class ServiceLocator {
    static let shared = ServiceLocator()
    private var services: [String: Any] = [:]

    func get<T>(_ type: T.Type) -> T? {
        services[String(describing: type)] as? T
    }
}

final class CheckoutViewModel: ObservableObject {
    func processPayment() {
        // ❌ Скрытая зависимость
        let paymentService = ServiceLocator.shared.get(PaymentService.self)
        // ❌ Runtime ошибка если не зарегистрирован
        paymentService?.processPayment()
        // ❌ Сложно понять зависимости класса
    }
}
```

✅ **Правильно:**
```swift
protocol PaymentService {
    func processPayment() async throws
}

final class CheckoutViewModel: ObservableObject {
    private let paymentService: PaymentService  // ✅ Явная зависимость
    private let analyticsService: AnalyticsService

    // ✅ Все зависимости видны в конструкторе
    init(
        paymentService: PaymentService,
        analyticsService: AnalyticsService
    ) {
        self.paymentService = paymentService
        self.analyticsService = analyticsService
    }

    func processPayment() async throws {
        try await paymentService.processPayment()  // ✅ Compile-time безопасность
        analyticsService.track(event: "payment_processed")
    }
}
```

### Ошибка 3: Force unwrapping при резолве зависимостей

❌ **Неправильно:**
```swift
let container = Container()

// Регистрация
container.register(NetworkService.self) { _ in
    URLSessionNetworkService()
}

// ❌ Force unwrap может привести к крашу
let viewModel = DataViewModel(
    networkService: container.resolve(NetworkService.self)!,  // ❌ Опасно
    storageService: container.resolve(StorageService.self)!   // ❌ Не зарегистрирован!
)
// 💥 Краш приложения
```

✅ **Правильно:**
```swift
let container = Container()

// ✅ Регистрируем все необходимые зависимости
container.register(NetworkService.self) { _ in
    URLSessionNetworkService()
}

container.register(StorageService.self) { _ in
    UserDefaultsStorageService()
}

// ✅ Безопасный резолв с обработкой ошибок
func makeDataViewModel(from container: Container) -> DataViewModel? {
    guard let networkService = container.resolve(NetworkService.self),
          let storageService = container.resolve(StorageService.self) else {
        assertionFailure("Required services not registered")
        return nil
    }

    return DataViewModel(
        networkService: networkService,
        storageService: storageService
    )
}

// ✅ Ещё лучше - регистрировать сам ViewModel
container.register(DataViewModel.self) { resolver in
    guard let network = resolver.resolve(NetworkService.self),
          let storage = resolver.resolve(StorageService.self) else {
        fatalError("Dependencies not registered")  // ✅ Fail fast при старте
    }
    return DataViewModel(networkService: network, storageService: storage)
}

// Проверка при старте приложения
func validateDependencies() {
    _ = container.resolve(DataViewModel.self)  // ✅ Проверка при запуске
}
```

### Ошибка 4: Смешивание concerns в DI Container

❌ **Неправильно:**
```swift
final class DIContainer {
    static let shared = DIContainer()

    // ❌ Контейнер знает о бизнес-логике
    func getUserViewModel(userId: String) -> UserViewModel {
        let network = URLSessionNetworkService()
        let storage = UserDefaultsStorageService()

        // ❌ Бизнес-логика в контейнере
        if userId.isEmpty {
            return UserViewModel(
                networkService: MockNetworkService(),
                storageService: storage
            )
        }

        // ❌ Условная логика усложняет тестирование
        let isProduction = ProcessInfo.processInfo.environment["ENV"] == "production"
        if isProduction {
            return UserViewModel(
                networkService: network,
                storageService: storage
            )
        } else {
            return UserViewModel(
                networkService: DebugNetworkService(),
                storageService: storage
            )
        }
    }
}
```

✅ **Правильно:**
```swift
// ✅ Контейнер только регистрирует и резолвит
final class DIContainer {
    private let container = Container()

    init(configuration: AppConfiguration) {
        registerServices(for: configuration)
    }

    // ✅ Простая регистрация без бизнес-логики
    private func registerServices(for config: AppConfiguration) {
        container.register(NetworkService.self) { _ in
            config.isProduction
                ? URLSessionNetworkService()
                : DebugNetworkService()
        }.inObjectScope(.container)

        container.register(StorageService.self) { _ in
            UserDefaultsStorageService()
        }

        container.register(UserViewModel.self) { (resolver, userId: String) in
            guard let network = resolver.resolve(NetworkService.self),
                  let storage = resolver.resolve(StorageService.self) else {
                fatalError("Services not registered")
            }
            return UserViewModel(
                userId: userId,                    // ✅ Параметр передаётся явно
                networkService: network,
                storageService: storage
            )
        }
    }

    func resolve<T>(_ type: T.Type) -> T? {
        container.resolve(type)
    }

    func resolve<T, Arg>(_ type: T.Type, argument: Arg) -> T? {
        container.resolve(type, argument: argument)
    }
}

// ✅ Бизнес-логика в нужном месте
final class UserCoordinator {
    private let container: DIContainer

    func showUserProfile(userId: String) {
        guard !userId.isEmpty else {
            showError("Invalid user ID")
            return
        }

        // ✅ Логика валидации в координаторе
        guard let viewModel = container.resolve(UserViewModel.self, argument: userId) else {
            showError("Failed to create view model")
            return
        }

        navigationController.pushViewController(
            UserViewController(viewModel: viewModel),
            animated: true
        )
    }
}
```

### Ошибка 5: Циклические зависимости

❌ **Неправильно:**
```swift
// ❌ Циклическая зависимость
final class UserService {
    private let orderService: OrderService

    init(orderService: OrderService) {
        self.orderService = orderService
    }

    func getUserOrders() -> [Order] {
        orderService.getOrdersForUser(self)  // ❌ Цикл
    }
}

final class OrderService {
    private let userService: UserService

    init(userService: UserService) {
        self.userService = userService       // ❌ Цикл
    }

    func getOrdersForUser(_ user: UserService) -> [Order] {
        userService.getUserOrders()          // ❌ Бесконечная рекурсия
    }
}

// 💥 Невозможно создать ни один из сервисов
let orderService = OrderService(userService: ???)  // Нужен UserService
let userService = UserService(orderService: ???)   // Нужен OrderService
```

✅ **Правильно:**
```swift
// ✅ Решение 1: Введение абстракции
protocol UserRepository {
    func getUser(id: String) -> User?
}

protocol OrderRepository {
    func getOrders(userId: String) -> [Order]
}

final class UserService: UserRepository {
    private let orderRepository: OrderRepository  // ✅ Зависит от абстракции

    init(orderRepository: OrderRepository) {
        self.orderRepository = orderRepository
    }

    func getUser(id: String) -> User? {
        // Получаем пользователя
        let user = User(id: id)
        return user
    }

    func getUserWithOrders(id: String) -> (User, [Order])? {
        guard let user = getUser(id: id) else { return nil }
        let orders = orderRepository.getOrders(userId: id)
        return (user, orders)
    }
}

final class OrderService: OrderRepository {
    private let userRepository: UserRepository    // ✅ Зависит от абстракции

    init(userRepository: UserRepository) {
        self.userRepository = userRepository
    }

    func getOrders(userId: String) -> [Order] {
        guard let user = userRepository.getUser(id: userId) else {
            return []
        }
        return [Order(id: "1", userId: user.id)]
    }
}

// ✅ Решение 2: Объединение в один сервис
final class UserOrderService {
    private let networkService: NetworkService
    private let storageService: StorageService

    init(networkService: NetworkService, storageService: StorageService) {
        self.networkService = networkService
        self.storageService = storageService
    }

    func getUserWithOrders(userId: String) async throws -> (User, [Order]) {
        async let user = fetchUser(userId: userId)
        async let orders = fetchOrders(userId: userId)
        return try await (user, orders)
    }

    private func fetchUser(userId: String) async throws -> User {
        // Fetch user
        User(id: userId)
    }

    private func fetchOrders(userId: String) async throws -> [Order] {
        // Fetch orders
        [Order(id: "1", userId: userId)]
    }
}

// ✅ Решение 3: Event-based communication
final class UserServiceEventBased {
    private let eventBus: EventBus

    init(eventBus: EventBus) {
        self.eventBus = eventBus
    }

    func createUser(_ user: User) {
        // Save user
        eventBus.publish(UserCreatedEvent(user: user))  // ✅ Нет прямой зависимости
    }
}

final class OrderServiceEventBased {
    private let eventBus: EventBus

    init(eventBus: EventBus) {
        self.eventBus = eventBus
        eventBus.subscribe(UserCreatedEvent.self, handler: handleUserCreated)
    }

    private func handleUserCreated(_ event: UserCreatedEvent) {
        // Create welcome order
    }
}
```

### Ошибка 6: Неправильный scope management

❌ **Неправильно:**
```swift
let container = Container()

// ❌ NetworkService создаётся каждый раз (transient)
container.register(NetworkService.self) { _ in
    URLSessionNetworkService()  // ❌ Новый экземпляр при каждом resolve
}

// ❌ UserDefaultsStorageService тоже transient
container.register(StorageService.self) { _ in
    UserDefaultsStorageService()  // ❌ Множественные экземпляры
}

// Проблема: разные ViewModels получат разные экземпляры сервисов
let vm1 = DataViewModel(
    networkService: container.resolve(NetworkService.self)!,
    storageService: container.resolve(StorageService.self)!
)

let vm2 = DataViewModel(
    networkService: container.resolve(NetworkService.self)!,  // ❌ Другой экземпляр
    storageService: container.resolve(StorageService.self)!   // ❌ Другой экземпляр
)

// ❌ Состояние не разделяется между ViewModels
// ❌ Лишнее потребление памяти
// ❌ Невозможность кеширования внутри сервисов
```

✅ **Правильно:**
```swift
let container = Container()

// ✅ Singleton для stateless сервисов
container.register(NetworkService.self) { _ in
    URLSessionNetworkService()
}.inObjectScope(.container)  // ✅ Один экземпляр на весь контейнер

// ✅ Singleton для сервисов с разделяемым состоянием
container.register(StorageService.self) { _ in
    UserDefaultsStorageService()
}.inObjectScope(.container)  // ✅ Разделяем кеш между ViewModels

// ✅ Singleton для дорогих в создании объектов
container.register(DatabaseService.self) { _ in
    RealmDatabaseService()
}.inObjectScope(.container)  // ✅ Создаём один раз

// ✅ Transient для ViewModels (каждый раз новый)
container.register(DataViewModel.self) { resolver in
    DataViewModel(
        networkService: resolver.resolve(NetworkService.self)!,
        storageService: resolver.resolve(StorageService.self)!
    )
}  // По умолчанию transient - правильно для ViewModels

// ✅ Graph scope для иерархических зависимостей
container.register(UserSession.self) { _ in
    UserSession()
}.inObjectScope(.graph)  // ✅ Один экземпляр в графе зависимостей

// Теперь ViewModels разделяют сервисы
let vm1 = container.resolve(DataViewModel.self)!
let vm2 = container.resolve(DataViewModel.self)!
// ✅ vm1 и vm2 используют одни и те же экземпляры сервисов
// ✅ Эффективное использование памяти
// ✅ Разделяемое состояние кеша

// ✅ Документируем scope для каждого сервиса
enum ServiceScope {
    // Singleton: URLSession, UserDefaults, Database
    case singleton
    // Transient: ViewModels, UseCases
    case transient
    // Graph: Session-scoped objects
    case graph
}
```

## Рекомендации по выбору подхода

### Для малых проектов (1-2 разработчика, <10 экранов)
```swift
// ✅ Используйте простой manual DI
// ✅ Constructor injection
// ✅ SwiftUI @Environment для глобальных сервисов

@main
struct SmallApp: App {
    private let networkService = URLSessionNetworkService()
    private let storageService = UserDefaultsStorageService()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.networkService, networkService)
                .environment(\.storageService, storageService)
        }
    }
}
```

### Для средних проектов (3-5 разработчиков, 10-50 экранов)
```swift
// ✅ Используйте @EnvironmentObject container
// ✅ Property wrappers для convenience
// ✅ Factory pattern для сложных объектов

final class ServiceContainer: ObservableObject {
    let network: NetworkService
    let storage: StorageService
    let auth: AuthService

    init() {
        self.network = URLSessionNetworkService()
        self.storage = UserDefaultsStorageService()
        self.auth = FirebaseAuthService()
    }
}

@main
struct MediumApp: App {
    @StateObject private var services = ServiceContainer()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(services)
        }
    }
}
```

### Для крупных проектов (5+ разработчиков, 50+ экранов, модульная архитектура)
```swift
// ✅ Используйте Swinject или Needle
// ✅ Assembly pattern для модульной регистрации
// ✅ Compile-time DI с Needle для больших команд

// Swinject для динамичности
let assembler = Assembler([
    NetworkAssembly(),
    StorageAssembly(),
    AuthAssembly(),
    FeatureAAssembly(),
    FeatureBAssembly()
])

// Needle для type safety и производительности
registerProviderFactories()
let rootComponent = RootComponent()

@main
struct LargeApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView(component: rootComponent)
        }
    }
}
```

## Связь с другими темами

**[[android-dependency-injection]]** — Android предлагает зрелую экосистему DI-фреймворков (Dagger/Hilt с compile-time генерацией, Koin с DSL), в то время как iOS-мир более фрагментирован (Swinject, Needle, ручной DI). Сравнение подходов позволяет оценить trade-offs между runtime и compile-time DI, а также перенять лучшие практики между платформами. Особенно ценно для KMP-проектов, где shared-модуль требует единого подхода к инъекции зависимостей. Рекомендуется изучать параллельно с iOS DI.

**[[ios-architecture-patterns]]** — DI является фундаментальным строительным блоком любой архитектуры (MVVM, Clean Architecture, VIPER). Без понимания DI невозможно правильно реализовать разделение ответственности между слоями и обеспечить тестируемость компонентов. Архитектурные паттерны определяют ГДЕ и КАК инъектировать зависимости, а DI обеспечивает механизм. Рекомендуется сначала изучить архитектурные паттерны, затем углубиться в DI.

**[[ios-modularization]]** — модуляризация приложения невозможна без продуманной системы DI, поскольку модули должны получать свои зависимости извне, не зная о конкретных реализациях в других модулях. Interface-модули в SPM играют роль контрактов, а DI-контейнер в App Target связывает всё воедино. Понимание обеих тем критично для масштабирования проекта и команды.

---

## Источники и дальнейшее чтение

### Книги
- Keur C., Hillegass A. (2020). *iOS Programming: Big Nerd Ranch Guide.* — содержит практические примеры constructor injection и разделения ответственности в контексте реальных iOS-приложений; отличная база для понимания зачем нужен DI.
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — объясняет протокол-ориентированное программирование и паттерны абстрагирования зависимостей через протоколы, что является основой DI в Swift.
- Eidhof C. et al. (2019). *Advanced Swift.* — глубокое погружение в систему типов Swift, generics и protocol-oriented programming, которые активно используются при построении DI-контейнеров.

### Ресурсы
- [Swinject Documentation](https://github.com/Swinject/Swinject)
- [Needle by Uber](https://github.com/uber/needle)
- [Swift by Sundell: Dependency Injection](https://www.swiftbysundell.com/articles/dependency-injection-in-swift/)
- [Point-Free: Dependencies](https://www.pointfree.co/collections/dependencies)
