---
title: "Тестирование iOS-приложений"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/testing
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-testing]]"
  - "[[ios-architecture-patterns]]"
---

# iOS Testing

## TL;DR

iOS testing ecosystem построен на XCTest framework от Apple. Включает unit testing для бизнес-логики, UI testing для автоматизации интерфейса, performance testing для измерения производительности, и snapshot testing для визуальной регрессии. Современные подходы используют async/await для асинхронного кода, dependency injection для мокирования, accessibility identifiers для UI тестов, и CI/CD интеграцию для автоматического запуска тестов.

## Аналогии

### Testing Pyramid как строительство здания
```
        /\        Unit Tests (70-80%)
       /  \       - Фундамент здания
      /____\      - Быстрые, дешевые, много
     /      \     Integration Tests (15-20%)
    /________\    - Несущие стены
   /          \   - Средняя скорость
  /____________\  UI Tests (5-10%)
                  - Фасад здания
                  - Медленные, дорогие, мало
```

### Mock vs Stub как дублеры в кино
- **Stub**: Дублер для статичных сцен (возвращает фиксированные данные)
- **Mock**: Дублер с проверкой действий (verify что методы вызваны правильно)
- **Fake**: Упрощенная версия актера (работающая реализация, но не production)

## Диаграммы

### XCTest Framework Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    XCTest Framework                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  XCTestCase  │  │ XCTestSuite  │  │XCTestObserver│  │
│  │              │  │              │  │              │  │
│  │ - setUp()    │  │ - Test       │  │ - Reports    │  │
│  │ - tearDown() │  │   Collection │  │ - Logging    │  │
│  │ - test*()    │  │              │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│                                                          │
├──────────────┬──────────────┬──────────────┬───────────┤
│              │              │              │           │
│  Unit Tests  │  UI Tests    │ Performance  │ Snapshot  │
│  XCTestCase  │ XCUITest     │ measure()    │ Testing   │
│              │              │              │           │
└──────────────┴──────────────┴──────────────┴───────────┘
```

### Test Execution Flow
```
Test Run Started
       ↓
┌──────────────────┐
│   setUpWithError │  ← Выполняется один раз для класса
└────────┬─────────┘
         ↓
    ┌────────┐
    │ setUp  │  ← Перед каждым тестом
    └────┬───┘
         ↓
    ┌─────────┐
    │ test*() │  ← Конкретный тест
    └────┬────┘
         ↓
    ┌──────────┐
    │ tearDown │  ← После каждого теста
    └────┬─────┘
         ↓
    [Повтор для каждого теста]
         ↓
┌────────────────────┐
│tearDownWithError   │  ← После всех тестов
└────────────────────┘
```

### Dependency Injection для тестирования
```
┌─────────────────────────────────────────┐
│           Production Code               │
│                                         │
│  ViewModel → Protocol ← Real Repository │
│                              ↓          │
│                         Network/CoreData│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│             Test Code                   │
│                                         │
│  ViewModel → Protocol ← Mock Repository │
│                              ↓          │
│                         Predefined Data │
└─────────────────────────────────────────┘
```

## XCTest Framework Overview

XCTest - встроенный testing framework от Apple для iOS, macOS, watchOS, и tvOS приложений.

```swift
import XCTest
@testable import MyApp // Доступ к internal типам

final class MyAppTests: XCTestCase {

    // MARK: - Lifecycle

    override func setUpWithError() throws {
        // Выполняется один раз перед всеми тестами
        try super.setUpWithError()
        continueAfterFailure = false
    }

    override func tearDownWithError() throws {
        // Выполняется один раз после всех тестов
        try super.tearDownWithError()
    }

    override func setUp() {
        // Выполняется перед каждым тестом
        super.setUp()
    }

    override func tearDown() {
        // Выполняется после каждого теста
        super.tearDown()
    }

    // MARK: - Tests

    func testExample() {
        // Arrange - подготовка
        let value = 5

        // Act - действие
        let result = value * 2

        // Assert - проверка
        XCTAssertEqual(result, 10)
    }
}
```

## Unit Tests: XCTestCase и Assertions

### Основные Assertions

```swift
import XCTest

final class AssertionTests: XCTestCase {

    func testAssertions() {
        // Equality
        XCTAssertEqual(2 + 2, 4)
        XCTAssertNotEqual(2 + 2, 5)

        // Boolean
        XCTAssertTrue(5 > 3)
        XCTAssertFalse(5 < 3)

        // Nil checking
        let value: String? = "test"
        XCTAssertNotNil(value)
        XCTAssertNil(nil)

        // Floating point comparison
        XCTAssertEqual(0.1 + 0.2, 0.3, accuracy: 0.0001)

        // Error throwing
        XCTAssertThrowsError(try throwingFunction())
        XCTAssertNoThrow(try nonThrowingFunction())

        // Type checking
        let object: Any = "String"
        XCTAssertTrue(object is String)

        // Always fail
        // XCTFail("This test should fail")
    }

    // Custom messages
    func testWithMessage() {
        let user = User(name: "")
        XCTAssertFalse(
            user.name.isEmpty,
            "User name should not be empty"
        )
    }
}
```

### Практический пример: Testing ViewModel

```swift
// MARK: - Production Code

final class LoginViewModel: ObservableObject {
    @Published var email: String = ""
    @Published var password: String = ""
    @Published var isLoading: Bool = false
    @Published var errorMessage: String?
    @Published var isLoggedIn: Bool = false

    private let authService: AuthServiceProtocol

    init(authService: AuthServiceProtocol = AuthService()) {
        self.authService = authService
    }

    var isFormValid: Bool {
        !email.isEmpty &&
        email.contains("@") &&
        password.count >= 6
    }

    @MainActor
    func login() async {
        guard isFormValid else {
            errorMessage = "Invalid credentials"
            return
        }

        isLoading = true
        errorMessage = nil

        do {
            try await authService.login(email: email, password: password)
            isLoggedIn = true
        } catch {
            errorMessage = error.localizedDescription
        }

        isLoading = false
    }
}

// MARK: - Test Code

final class LoginViewModelTests: XCTestCase {

    var sut: LoginViewModel!
    var mockAuthService: MockAuthService!

    override func setUp() {
        super.setUp()
        mockAuthService = MockAuthService()
        sut = LoginViewModel(authService: mockAuthService)
    }

    override func tearDown() {
        sut = nil
        mockAuthService = nil
        super.tearDown()
    }

    // MARK: - Form Validation Tests

    func testFormIsInvalidWhenEmailIsEmpty() {
        // Arrange
        sut.email = ""
        sut.password = "password123"

        // Act & Assert
        XCTAssertFalse(sut.isFormValid)
    }

    func testFormIsInvalidWhenEmailHasNoAtSign() {
        // Arrange
        sut.email = "invalidemail.com"
        sut.password = "password123"

        // Act & Assert
        XCTAssertFalse(sut.isFormValid)
    }

    func testFormIsInvalidWhenPasswordIsTooShort() {
        // Arrange
        sut.email = "user@example.com"
        sut.password = "12345"

        // Act & Assert
        XCTAssertFalse(sut.isFormValid)
    }

    func testFormIsValidWhenFieldsAreCorrect() {
        // Arrange
        sut.email = "user@example.com"
        sut.password = "password123"

        // Act & Assert
        XCTAssertTrue(sut.isFormValid)
    }

    // MARK: - Login Tests

    func testLoginSuccessUpdatesState() async {
        // Arrange
        sut.email = "user@example.com"
        sut.password = "password123"
        mockAuthService.shouldSucceed = true

        // Act
        await sut.login()

        // Assert
        XCTAssertTrue(sut.isLoggedIn)
        XCTAssertFalse(sut.isLoading)
        XCTAssertNil(sut.errorMessage)
        XCTAssertTrue(mockAuthService.loginCalled)
    }

    func testLoginFailureShowsError() async {
        // Arrange
        sut.email = "user@example.com"
        sut.password = "wrongpassword"
        mockAuthService.shouldSucceed = false

        // Act
        await sut.login()

        // Assert
        XCTAssertFalse(sut.isLoggedIn)
        XCTAssertFalse(sut.isLoading)
        XCTAssertNotNil(sut.errorMessage)
        XCTAssertEqual(sut.errorMessage, "Invalid credentials")
    }
}
```

## Testing Async Code

### XCTestExpectation (старый подход)

```swift
final class ExpectationTests: XCTestCase {

    func testAsyncFunctionWithExpectation() {
        // Arrange
        let expectation = expectation(description: "Network call")
        let service = NetworkService()
        var result: String?

        // Act
        service.fetchData { data in
            result = data
            expectation.fulfill()
        }

        // Assert
        waitForExpectations(timeout: 5.0)
        XCTAssertNotNil(result)
    }

    func testMultipleExpectations() {
        let firstExpectation = expectation(description: "First call")
        let secondExpectation = expectation(description: "Second call")

        firstExpectation.expectedFulfillmentCount = 2

        DispatchQueue.main.async {
            firstExpectation.fulfill()
        }

        DispatchQueue.main.async {
            firstExpectation.fulfill()
            secondExpectation.fulfill()
        }

        wait(for: [firstExpectation, secondExpectation], timeout: 3.0)
    }
}
```

### Async/Await (современный подход)

```swift
final class AsyncAwaitTests: XCTestCase {

    func testAsyncFunction() async throws {
        // Arrange
        let service = NetworkService()

        // Act
        let result = try await service.fetchData()

        // Assert
        XCTAssertFalse(result.isEmpty)
        XCTAssertEqual(result.count, 10)
    }

    func testAsyncThrowingFunction() async {
        // Arrange
        let service = NetworkService()

        // Act & Assert
        do {
            _ = try await service.fetchDataThatThrows()
            XCTFail("Should have thrown an error")
        } catch NetworkError.unauthorized {
            // Expected error
        } catch {
            XCTFail("Wrong error type: \(error)")
        }
    }

    func testMainActorFunction() async {
        // Arrange
        let viewModel = MainViewModel()

        // Act
        await viewModel.loadData()

        // Assert
        await MainActor.run {
            XCTAssertTrue(viewModel.isLoaded)
            XCTAssertFalse(viewModel.items.isEmpty)
        }
    }
}
```

## Mocking и Stubbing

### Protocol-Based Dependency Injection

```swift
// MARK: - Protocol

protocol AuthServiceProtocol {
    func login(email: String, password: String) async throws
    func logout() async
    func isAuthenticated() -> Bool
}

// MARK: - Real Implementation

final class AuthService: AuthServiceProtocol {
    func login(email: String, password: String) async throws {
        // Real network call
        try await URLSession.shared.data(from: URL(string: "api/login")!)
    }

    func logout() async {
        // Real logout logic
    }

    func isAuthenticated() -> Bool {
        // Real authentication check
        return UserDefaults.standard.bool(forKey: "isLoggedIn")
    }
}

// MARK: - Mock Implementation

final class MockAuthService: AuthServiceProtocol {
    var loginCalled = false
    var logoutCalled = false
    var shouldSucceed = true
    var loginCallCount = 0

    private(set) var lastEmail: String?
    private(set) var lastPassword: String?

    func login(email: String, password: String) async throws {
        loginCalled = true
        loginCallCount += 1
        lastEmail = email
        lastPassword = password

        if !shouldSucceed {
            throw AuthError.invalidCredentials
        }
    }

    func logout() async {
        logoutCalled = true
    }

    func isAuthenticated() -> Bool {
        return shouldSucceed
    }
}

enum AuthError: Error {
    case invalidCredentials
    case networkError
}
```

### Практический пример: Testing Repository

```swift
// MARK: - Repository Protocol

protocol UserRepositoryProtocol {
    func fetchUsers() async throws -> [User]
    func fetchUser(id: String) async throws -> User
    func createUser(_ user: User) async throws
    func deleteUser(id: String) async throws
}

// MARK: - Production Repository

final class UserRepository: UserRepositoryProtocol {
    private let networkService: NetworkServiceProtocol
    private let cacheService: CacheServiceProtocol

    init(
        networkService: NetworkServiceProtocol,
        cacheService: CacheServiceProtocol
    ) {
        self.networkService = networkService
        self.cacheService = cacheService
    }

    func fetchUsers() async throws -> [User] {
        // Try cache first
        if let cached = cacheService.getUsers() {
            return cached
        }

        // Fetch from network
        let users = try await networkService.fetchUsers()
        cacheService.saveUsers(users)
        return users
    }

    func fetchUser(id: String) async throws -> User {
        try await networkService.fetchUser(id: id)
    }

    func createUser(_ user: User) async throws {
        try await networkService.createUser(user)
        cacheService.invalidateUsers()
    }

    func deleteUser(id: String) async throws {
        try await networkService.deleteUser(id: id)
        cacheService.invalidateUsers()
    }
}

// MARK: - Mock Repository

final class MockUserRepository: UserRepositoryProtocol {
    var users: [User] = []
    var shouldThrowError = false
    var fetchUsersCalled = false
    var createUserCalled = false

    func fetchUsers() async throws -> [User] {
        fetchUsersCalled = true

        if shouldThrowError {
            throw NetworkError.serverError
        }

        return users
    }

    func fetchUser(id: String) async throws -> User {
        if shouldThrowError {
            throw NetworkError.notFound
        }

        guard let user = users.first(where: { $0.id == id }) else {
            throw NetworkError.notFound
        }

        return user
    }

    func createUser(_ user: User) async throws {
        createUserCalled = true

        if shouldThrowError {
            throw NetworkError.serverError
        }

        users.append(user)
    }

    func deleteUser(id: String) async throws {
        if shouldThrowError {
            throw NetworkError.serverError
        }

        users.removeAll { $0.id == id }
    }
}

// MARK: - Repository Tests

final class UserRepositoryTests: XCTestCase {

    var sut: UserRepository!
    var mockNetwork: MockNetworkService!
    var mockCache: MockCacheService!

    override func setUp() {
        super.setUp()
        mockNetwork = MockNetworkService()
        mockCache = MockCacheService()
        sut = UserRepository(
            networkService: mockNetwork,
            cacheService: mockCache
        )
    }

    override func tearDown() {
        sut = nil
        mockNetwork = nil
        mockCache = nil
        super.tearDown()
    }

    func testFetchUsersReturnsCachedData() async throws {
        // Arrange
        let cachedUsers = [
            User(id: "1", name: "Cached User")
        ]
        mockCache.cachedUsers = cachedUsers

        // Act
        let result = try await sut.fetchUsers()

        // Assert
        XCTAssertEqual(result.count, 1)
        XCTAssertEqual(result.first?.name, "Cached User")
        XCTAssertFalse(mockNetwork.fetchUsersCalled,
                       "Should not call network when cache exists")
    }

    func testFetchUsersFetchesFromNetworkWhenCacheEmpty() async throws {
        // Arrange
        mockCache.cachedUsers = nil
        mockNetwork.users = [
            User(id: "1", name: "Network User")
        ]

        // Act
        let result = try await sut.fetchUsers()

        // Assert
        XCTAssertTrue(mockNetwork.fetchUsersCalled)
        XCTAssertTrue(mockCache.saveUsersCalled)
        XCTAssertEqual(result.count, 1)
        XCTAssertEqual(result.first?.name, "Network User")
    }

    func testCreateUserInvalidatesCache() async throws {
        // Arrange
        let newUser = User(id: "2", name: "New User")

        // Act
        try await sut.createUser(newUser)

        // Assert
        XCTAssertTrue(mockNetwork.createUserCalled)
        XCTAssertTrue(mockCache.invalidateCalled)
    }
}
```

## UI Tests: XCUIApplication и XCUIElement

### Основы UI Testing

```swift
import XCTest

final class LoginUITests: XCTestCase {

    var app: XCUIApplication!

    override func setUp() {
        super.setUp()

        continueAfterFailure = false

        app = XCUIApplication()
        app.launchArguments = ["UI-Testing"]
        app.launch()
    }

    override func tearDown() {
        app = nil
        super.tearDown()
    }

    func testLoginFlow() {
        // Find elements
        let emailField = app.textFields["emailTextField"]
        let passwordField = app.secureTextFields["passwordTextField"]
        let loginButton = app.buttons["loginButton"]

        // Check initial state
        XCTAssertTrue(emailField.exists)
        XCTAssertTrue(passwordField.exists)
        XCTAssertTrue(loginButton.exists)
        XCTAssertFalse(loginButton.isEnabled)

        // Enter credentials
        emailField.tap()
        emailField.typeText("user@example.com")

        passwordField.tap()
        passwordField.typeText("password123")

        // Verify button is enabled
        XCTAssertTrue(loginButton.isEnabled)

        // Tap login
        loginButton.tap()

        // Verify navigation
        let welcomeLabel = app.staticTexts["Welcome"]
        XCTAssertTrue(welcomeLabel.waitForExistence(timeout: 5))
    }

    func testInvalidLoginShowsError() {
        // Arrange
        let emailField = app.textFields["emailTextField"]
        let passwordField = app.secureTextFields["passwordTextField"]
        let loginButton = app.buttons["loginButton"]

        // Act
        emailField.tap()
        emailField.typeText("invalid@example.com")

        passwordField.tap()
        passwordField.typeText("wrong")

        loginButton.tap()

        // Assert
        let errorAlert = app.alerts["Error"]
        XCTAssertTrue(errorAlert.waitForExistence(timeout: 3))

        let errorMessage = errorAlert.staticTexts["Invalid credentials"]
        XCTAssertTrue(errorMessage.exists)

        errorAlert.buttons["OK"].tap()
    }
}
```

### XCUIElement Query Methods

```swift
final class ElementQueryTests: XCTestCase {

    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        app = XCUIApplication()
        app.launch()
    }

    func testFindingElements() {
        // By type
        let buttons = app.buttons
        let textFields = app.textFields
        let images = app.images
        let staticTexts = app.staticTexts

        // By identifier
        let loginButton = app.buttons["loginButton"]

        // By label
        let submitButton = app.buttons["Submit"]

        // By predicate
        let enabledButtons = app.buttons.matching(
            NSPredicate(format: "isEnabled == true")
        )

        // First matching element
        let firstButton = app.buttons.firstMatch

        // Element at index
        let secondButton = app.buttons.element(boundBy: 1)

        // Check existence
        XCTAssertTrue(loginButton.exists)

        // Count
        XCTAssertEqual(buttons.count, 5)
    }

    func testElementInteractions() {
        let button = app.buttons["testButton"]
        let textField = app.textFields["testField"]
        let slider = app.sliders["volumeSlider"]

        // Tap
        button.tap()

        // Double tap
        button.doubleTap()

        // Long press
        button.press(forDuration: 2.0)

        // Type text
        textField.tap()
        textField.typeText("Hello, World!")

        // Clear text
        textField.tap()
        textField.clearText()

        // Adjust slider
        slider.adjust(toNormalizedSliderPosition: 0.75)

        // Swipe
        app.swipeUp()
        app.swipeDown()
        app.swipeLeft()
        app.swipeRight()
    }

    func testWaitingForElements() {
        let loadingSpinner = app.activityIndicators["loadingSpinner"]
        let contentView = app.otherElements["contentView"]

        // Wait for existence
        XCTAssertTrue(loadingSpinner.waitForExistence(timeout: 2))

        // Wait for disappearance
        let disappeared = !loadingSpinner.waitForExistence(timeout: 5)
        XCTAssertTrue(disappeared)

        // Verify content appeared
        XCTAssertTrue(contentView.waitForExistence(timeout: 3))
    }
}

// Extension helper
extension XCUIElement {
    func clearText() {
        guard let stringValue = self.value as? String else {
            return
        }

        let deleteString = String(repeating: XCUIKeyboardKey.delete.rawValue,
                                 count: stringValue.count)
        typeText(deleteString)
    }
}
```

## Accessibility Identifiers для UI Tests

### Добавление Accessibility Identifiers

```swift
// MARK: - SwiftUI View

struct LoginView: View {
    @State private var email = ""
    @State private var password = ""

    var body: some View {
        VStack(spacing: 20) {
            TextField("Email", text: $email)
                .accessibilityIdentifier("emailTextField")
                .textContentType(.emailAddress)
                .autocapitalization(.none)

            SecureField("Password", text: $password)
                .accessibilityIdentifier("passwordTextField")
                .textContentType(.password)

            Button("Login") {
                login()
            }
            .accessibilityIdentifier("loginButton")
            .disabled(email.isEmpty || password.isEmpty)

            if isLoading {
                ProgressView()
                    .accessibilityIdentifier("loadingSpinner")
            }
        }
        .padding()
        .accessibilityIdentifier("loginView")
    }
}

// MARK: - UIKit View

final class LoginViewController: UIViewController {

    private let emailTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Email"
        textField.accessibilityIdentifier = "emailTextField"
        return textField
    }()

    private let passwordTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "Password"
        textField.isSecureTextEntry = true
        textField.accessibilityIdentifier = "passwordTextField"
        return textField
    }()

    private let loginButton: UIButton = {
        let button = UIButton()
        button.setTitle("Login", for: .normal)
        button.accessibilityIdentifier = "loginButton"
        return button
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.accessibilityIdentifier = "loginViewController"
    }
}
```

### Практический пример: Полный UI Test Flow

```swift
final class UserProfileUITests: XCTestCase {

    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false

        app = XCUIApplication()

        // Launch arguments для тестового окружения
        app.launchArguments = [
            "-UITesting",
            "-DisableAnimations"
        ]

        // Environment variables для мок данных
        app.launchEnvironment = [
            "USE_MOCK_DATA": "1",
            "MOCK_USER_ID": "test-user-123"
        ]

        app.launch()
    }

    func testCompleteUserProfileEditFlow() {
        // 1. Navigate to profile
        let tabBar = app.tabBars.firstMatch
        let profileTab = tabBar.buttons["Profile"]
        XCTAssertTrue(profileTab.waitForExistence(timeout: 2))
        profileTab.tap()

        // 2. Verify profile loaded
        let profileView = app.scrollViews["profileScrollView"]
        XCTAssertTrue(profileView.waitForExistence(timeout: 3))

        let nameLabel = app.staticTexts["userNameLabel"]
        XCTAssertEqual(nameLabel.label, "John Doe")

        // 3. Open edit mode
        let editButton = app.buttons["editProfileButton"]
        editButton.tap()

        // 4. Edit name
        let nameField = app.textFields["nameTextField"]
        XCTAssertTrue(nameField.waitForExistence(timeout: 1))

        nameField.tap()
        nameField.clearAndType("Jane Smith")

        // 5. Edit bio
        let bioTextView = app.textViews["bioTextView"]
        bioTextView.tap()
        bioTextView.clearAndType("iOS Developer | Swift Enthusiast")

        // 6. Change avatar
        let avatarButton = app.buttons["changeAvatarButton"]
        avatarButton.tap()

        let photoLibraryOption = app.buttons["Photo Library"]
        photoLibraryOption.tap()

        // Select first photo
        let firstPhoto = app.images.firstMatch
        if firstPhoto.waitForExistence(timeout: 3) {
            firstPhoto.tap()
        }

        // 7. Save changes
        let saveButton = app.buttons["saveButton"]
        XCTAssertTrue(saveButton.isEnabled)
        saveButton.tap()

        // 8. Verify save completed
        let successAlert = app.alerts["Success"]
        XCTAssertTrue(successAlert.waitForExistence(timeout: 5))
        successAlert.buttons["OK"].tap()

        // 9. Verify changes persisted
        XCTAssertEqual(nameLabel.label, "Jane Smith")

        let bioLabel = app.staticTexts["userBioLabel"]
        XCTAssertEqual(bioLabel.label, "iOS Developer | Swift Enthusiast")
    }

    func testValidationErrorsInProfileEdit() {
        // Navigate to edit mode
        app.tabBars.buttons["Profile"].tap()
        app.buttons["editProfileButton"].tap()

        // Try to save with empty name
        let nameField = app.textFields["nameTextField"]
        nameField.tap()
        nameField.clearText()

        let saveButton = app.buttons["saveButton"]
        saveButton.tap()

        // Verify error message
        let errorLabel = app.staticTexts["nameErrorLabel"]
        XCTAssertTrue(errorLabel.exists)
        XCTAssertEqual(errorLabel.label, "Name cannot be empty")

        // Save button should be disabled
        XCTAssertFalse(saveButton.isEnabled)
    }
}

// MARK: - Helper Extensions

extension XCUIElement {
    func clearAndType(_ text: String) {
        tap()
        clearText()
        typeText(text)
    }
}
```

## Performance Tests

### Measure Block Testing

```swift
import XCTest

final class PerformanceTests: XCTestCase {

    func testSortingPerformance() {
        let array = (1...10000).map { _ in Int.random(in: 1...1000) }

        measure {
            _ = array.sorted()
        }

        // Базовый результат сохраняется
        // Xcode предупредит о регрессии производительности
    }

    func testDatabaseQueryPerformance() {
        let context = CoreDataStack.shared.viewContext

        measure {
            let request = User.fetchRequest()
            request.predicate = NSPredicate(format: "age > %d", 18)
            request.sortDescriptors = [NSSortDescriptor(key: "name", ascending: true)]

            do {
                _ = try context.fetch(request)
            } catch {
                XCTFail("Fetch failed: \(error)")
            }
        }
    }

    func testImageDecodingPerformance() {
        guard let imageURL = Bundle.main.url(forResource: "large-image", withExtension: "jpg"),
              let imageData = try? Data(contentsOf: imageURL) else {
            XCTFail("Could not load test image")
            return
        }

        measure {
            _ = UIImage(data: imageData)
        }
    }
}
```

### Metrics-Based Performance Testing

```swift
final class MetricsPerformanceTests: XCTestCase {

    func testViewModelPerformance() {
        let viewModel = ProductListViewModel()

        let options = XCTMeasureOptions()
        options.iterationCount = 10

        measure(
            metrics: [
                XCTClockMetric(),        // Execution time
                XCTCPUMetric(),          // CPU usage
                XCTMemoryMetric(),       // Memory usage
                XCTStorageMetric()       // Disk I/O
            ],
            options: options
        ) {
            viewModel.loadProducts()
        }
    }

    func testUIRenderingPerformance() {
        let metrics: [XCTMetric] = [
            XCTOSSignpostMetric.applicationLaunch,
            XCTClockMetric(),
            XCTMemoryMetric()
        ]

        let options = XCTMeasureOptions()
        options.invocationOptions = [.manuallyStop]

        measure(metrics: metrics, options: options) {
            let app = XCUIApplication()
            app.launch()

            // Wait for UI to settle
            _ = app.tables.firstMatch.waitForExistence(timeout: 5)

            stopMeasuring()
        }
    }
}
```

## Code Coverage

### Настройка Code Coverage

```swift
// 1. В Xcode: Product > Scheme > Edit Scheme
// 2. Test tab > Options > Code Coverage ✓
// 3. Выбрать targets для coverage

// Просмотр результатов:
// Report Navigator (⌘9) > Coverage tab
```

### Практические рекомендации

```swift
final class CoverageExampleTests: XCTestCase {

    // Хорошее покрытие - тестируем все пути
    func testCalculatorAddition() {
        let calculator = Calculator()

        // Positive numbers
        XCTAssertEqual(calculator.add(2, 3), 5)

        // Negative numbers
        XCTAssertEqual(calculator.add(-2, -3), -5)

        // Mixed
        XCTAssertEqual(calculator.add(-2, 5), 3)

        // Zero
        XCTAssertEqual(calculator.add(0, 0), 0)

        // Large numbers
        XCTAssertEqual(calculator.add(1_000_000, 2_000_000), 3_000_000)
    }

    // Тестируем edge cases
    func testDivisionEdgeCases() {
        let calculator = Calculator()

        // Normal division
        XCTAssertEqual(calculator.divide(10, 2), 5)

        // Division by zero
        XCTAssertThrowsError(try calculator.divide(10, 0)) { error in
            XCTAssertEqual(error as? CalculatorError, .divisionByZero)
        }

        // Negative division
        XCTAssertEqual(calculator.divide(-10, 2), -5)
    }
}

// Code Coverage Targets:
// - Unit Tests: 80-90%
// - ViewModels: 90-100%
// - UI Tests: 60-70%
// - Total Project: 70-80%
```

## Test Plans и Configurations

### Creating Test Plan

```swift
// File > New > File > Test Plan
// MyApp.xctestplan

/*
{
  "configurations": [
    {
      "name": "Development",
      "options": {
        "environmentVariableEntries": [
          {
            "key": "API_URL",
            "value": "https://dev.api.example.com"
          }
        ],
        "commandLineArgumentEntries": [
          {
            "argument": "-UITesting"
          }
        ]
      }
    },
    {
      "name": "Production",
      "options": {
        "environmentVariableEntries": [
          {
            "key": "API_URL",
            "value": "https://api.example.com"
          }
        ]
      }
    }
  ],
  "defaultOptions": {
    "codeCoverage": true,
    "targetForVariableExpansion": {
      "containerPath": "MyApp.app",
      "identifier": "com.example.MyApp"
    }
  },
  "testTargets": [
    {
      "target": {
        "containerPath": "MyAppTests",
        "identifier": "MyAppTests"
      }
    }
  ],
  "version": 1
}
*/
```

### Using Test Configurations

```swift
final class ConfigurationAwareTests: XCTestCase {

    var apiURL: String!

    override func setUp() {
        super.setUp()

        // Read from environment
        apiURL = ProcessInfo.processInfo.environment["API_URL"]
            ?? "https://default.api.example.com"
    }

    func testAPIConnection() {
        let service = NetworkService(baseURL: apiURL)

        // Test will use different URLs based on configuration
        XCTAssertNotNil(service.baseURL)
    }
}

// Launch arguments detection
extension XCTestCase {
    var isUITesting: Bool {
        ProcessInfo.processInfo.arguments.contains("-UITesting")
    }

    var shouldUseMockData: Bool {
        ProcessInfo.processInfo.environment["USE_MOCK_DATA"] == "1"
    }
}
```

## Testing Combine Publishers

### Publisher Testing Patterns

```swift
import Combine
import XCTest

final class CombineTests: XCTestCase {

    var cancellables: Set<AnyCancellable>!

    override func setUp() {
        super.setUp()
        cancellables = []
    }

    override func tearDown() {
        cancellables = nil
        super.tearDown()
    }

    // MARK: - Basic Publisher Testing

    func testSimplePublisher() {
        // Arrange
        let expectation = expectation(description: "Publisher emits value")
        let publisher = Just(42)
        var receivedValue: Int?

        // Act
        publisher
            .sink { value in
                receivedValue = value
                expectation.fulfill()
            }
            .store(in: &cancellables)

        // Assert
        waitForExpectations(timeout: 1.0)
        XCTAssertEqual(receivedValue, 42)
    }

    func testPublisherWithError() {
        // Arrange
        let expectation = expectation(description: "Publisher emits error")
        let publisher = Fail<Int, NetworkError>(error: .serverError)
        var receivedError: NetworkError?

        // Act
        publisher
            .sink(
                receiveCompletion: { completion in
                    if case .failure(let error) = completion {
                        receivedError = error
                        expectation.fulfill()
                    }
                },
                receiveValue: { _ in }
            )
            .store(in: &cancellables)

        // Assert
        waitForExpectations(timeout: 1.0)
        XCTAssertEqual(receivedError, .serverError)
    }

    // MARK: - ViewModel with Combine

    func testViewModelPublisher() {
        // Arrange
        let expectation = expectation(description: "ViewModel updates state")
        expectation.expectedFulfillmentCount = 2 // Initial + Updated

        let mockRepository = MockUserRepository()
        mockRepository.users = [User(id: "1", name: "Test User")]

        let viewModel = UserListViewModel(repository: mockRepository)
        var stateChanges: [UserListViewModel.State] = []

        // Act
        viewModel.$state
            .sink { state in
                stateChanges.append(state)
                expectation.fulfill()
            }
            .store(in: &cancellables)

        Task {
            await viewModel.loadUsers()
        }

        // Assert
        waitForExpectations(timeout: 2.0)
        XCTAssertEqual(stateChanges.count, 2)
        XCTAssertEqual(stateChanges[0], .idle)

        if case .loaded(let users) = stateChanges[1] {
            XCTAssertEqual(users.count, 1)
            XCTAssertEqual(users.first?.name, "Test User")
        } else {
            XCTFail("Expected loaded state")
        }
    }

    // MARK: - Testing Operators

    func testMapOperator() {
        // Arrange
        let expectation = expectation(description: "Map transforms value")
        let publisher = Just(5)
        var result: Int?

        // Act
        publisher
            .map { $0 * 2 }
            .sink { value in
                result = value
                expectation.fulfill()
            }
            .store(in: &cancellables)

        // Assert
        waitForExpectations(timeout: 1.0)
        XCTAssertEqual(result, 10)
    }

    func testDebounce() {
        // Arrange
        let expectation = expectation(description: "Debounce delays emission")
        let subject = PassthroughSubject<String, Never>()
        var receivedValues: [String] = []

        // Act
        subject
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .sink { value in
                receivedValues.append(value)
                if receivedValues.count == 1 {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        subject.send("a")
        subject.send("ab")
        subject.send("abc")  // Only this should be received

        // Assert
        waitForExpectations(timeout: 1.0)
        XCTAssertEqual(receivedValues, ["abc"])
    }

    func testCombineLatest() {
        // Arrange
        let expectation = expectation(description: "CombineLatest merges publishers")
        let publisher1 = CurrentValueSubject<Int, Never>(0)
        let publisher2 = CurrentValueSubject<String, Never>("")
        var results: [(Int, String)] = []

        // Act
        Publishers.CombineLatest(publisher1, publisher2)
            .dropFirst() // Skip initial (0, "")
            .sink { value in
                results.append(value)
                if results.count == 2 {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        publisher1.send(1)
        publisher2.send("a")

        // Assert
        waitForExpectations(timeout: 1.0)
        XCTAssertEqual(results.count, 2)
        XCTAssertEqual(results[0].0, 1)
        XCTAssertEqual(results[1].1, "a")
    }
}
```

### Practical Example: Search ViewModel Testing

```swift
final class SearchViewModel: ObservableObject {
    @Published var searchQuery: String = ""
    @Published var searchResults: [Product] = []
    @Published var isLoading: Bool = false

    private let repository: ProductRepositoryProtocol
    private var cancellables = Set<AnyCancellable>()

    init(repository: ProductRepositoryProtocol) {
        self.repository = repository
        setupSearchBinding()
    }

    private func setupSearchBinding() {
        $searchQuery
            .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
            .removeDuplicates()
            .map { $0.trimmingCharacters(in: .whitespaces) }
            .filter { !$0.isEmpty }
            .sink { [weak self] query in
                Task {
                    await self?.performSearch(query: query)
                }
            }
            .store(in: &cancellables)
    }

    @MainActor
    private func performSearch(query: String) async {
        isLoading = true

        do {
            searchResults = try await repository.searchProducts(query: query)
        } catch {
            searchResults = []
        }

        isLoading = false
    }
}

final class SearchViewModelTests: XCTestCase {

    var sut: SearchViewModel!
    var mockRepository: MockProductRepository!
    var cancellables: Set<AnyCancellable>!

    override func setUp() {
        super.setUp()
        mockRepository = MockProductRepository()
        sut = SearchViewModel(repository: mockRepository)
        cancellables = []
    }

    override func tearDown() {
        sut = nil
        mockRepository = nil
        cancellables = nil
        super.tearDown()
    }

    func testSearchQueryDebounce() async {
        // Arrange
        let expectation = expectation(description: "Search debounced")
        mockRepository.products = [Product(id: "1", name: "iPhone")]

        var searchCount = 0

        sut.$isLoading
            .dropFirst()
            .sink { isLoading in
                if isLoading {
                    searchCount += 1
                }

                if !isLoading && searchCount == 1 {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        // Act - Type quickly
        sut.searchQuery = "i"
        try? await Task.sleep(nanoseconds: 100_000_000) // 100ms

        sut.searchQuery = "iP"
        try? await Task.sleep(nanoseconds: 100_000_000)

        sut.searchQuery = "iPh"
        try? await Task.sleep(nanoseconds: 100_000_000)

        sut.searchQuery = "iPhon"
        try? await Task.sleep(nanoseconds: 100_000_000)

        sut.searchQuery = "iPhone"

        // Assert
        await fulfillment(of: [expectation], timeout: 2.0)
        XCTAssertEqual(searchCount, 1, "Should only search once after debounce")
        XCTAssertEqual(sut.searchResults.count, 1)
    }

    func testEmptyQueryDoesNotSearch() async {
        // Arrange
        mockRepository.products = [Product(id: "1", name: "iPhone")]

        // Act
        sut.searchQuery = ""
        try? await Task.sleep(nanoseconds: 500_000_000) // 500ms

        // Assert
        XCTAssertFalse(mockRepository.searchCalled)
        XCTAssertTrue(sut.searchResults.isEmpty)
    }
}
```

## Testing SwiftUI Views

### ViewInspector Library

```swift
// Add to Package.swift
// .package(url: "https://github.com/nalexn/ViewInspector.git", from: "0.9.0")

import SwiftUI
import ViewInspector
import XCTest

final class SwiftUIViewTests: XCTestCase {

    func testButtonExists() throws {
        let view = ContentView()

        let button = try view.inspect().find(button: "Tap Me")
        XCTAssertNotNil(button)
    }

    func testButtonTap() throws {
        var tapped = false

        let view = Button("Tap") {
            tapped = true
        }

        try view.inspect().button().tap()

        XCTAssertTrue(tapped)
    }

    func testTextFieldValue() throws {
        @State var text = "Initial"

        let view = TextField("Enter text", text: $text)

        let textField = try view.inspect().textField()
        XCTAssertEqual(try textField.input(), "Initial")

        try textField.setInput("Updated")
        XCTAssertEqual(text, "Updated")
    }

    func testListContent() throws {
        let items = ["Item 1", "Item 2", "Item 3"]

        let view = List(items, id: \.self) { item in
            Text(item)
        }

        let list = try view.inspect().list()
        XCTAssertEqual(try list.count(), 3)

        let firstItem = try list.text(0).string()
        XCTAssertEqual(firstItem, "Item 1")
    }
}
```

### Testing View State

```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")
                .accessibilityIdentifier("countLabel")

            Button("Increment") {
                count += 1
            }
            .accessibilityIdentifier("incrementButton")
        }
    }
}

final class CounterViewTests: XCTestCase {

    func testInitialState() throws {
        let view = CounterView()

        let text = try view.inspect().find(text: "Count: 0")
        XCTAssertNotNil(text)
    }

    func testIncrementButton() throws {
        let view = CounterView()

        let button = try view.inspect().find(button: "Increment")

        try button.tap()

        // State updated
        let updatedText = try view.inspect().find(text: "Count: 1")
        XCTAssertNotNil(updatedText)
    }
}
```

## Snapshot Testing

### SnapshotTesting Library

```swift
// Add to Package.swift
// .package(url: "https://github.com/pointfreeco/swift-snapshot-testing.git", from: "1.15.0")

import SnapshotTesting
import SwiftUI
import XCTest

final class SnapshotTests: XCTestCase {

    func testLoginViewSnapshot() {
        let view = LoginView()
            .frame(width: 375, height: 812) // iPhone size

        let vc = UIHostingController(rootView: view)

        assertSnapshot(matching: vc, as: .image)

        // First run: записывает snapshot
        // Subsequent runs: сравнивает с записанным
    }

    func testButtonStates() {
        let normalButton = Button("Normal") {}
        let disabledButton = Button("Disabled") {}
            .disabled(true)

        assertSnapshot(
            matching: UIHostingController(rootView: normalButton),
            as: .image(on: .iPhoneX)
        )

        assertSnapshot(
            matching: UIHostingController(rootView: disabledButton),
            as: .image(on: .iPhoneX)
        )
    }

    func testDarkModeSnapshot() {
        let view = ProfileView()

        let lightVC = UIHostingController(rootView: view)
        let darkVC = UIHostingController(rootView: view)
        darkVC.overrideUserInterfaceStyle = .dark

        assertSnapshot(matching: lightVC, as: .image, named: "light")
        assertSnapshot(matching: darkVC, as: .image, named: "dark")
    }

    func testAccessibilitySnapshot() {
        let view = ArticleView()

        let smallTextVC = UIHostingController(rootView: view)
        let largeTextVC = UIHostingController(rootView: view)
        largeTextVC.view.traitCollection

        assertSnapshot(
            matching: smallTextVC,
            as: .image(traits: .init(preferredContentSizeCategory: .medium))
        )

        assertSnapshot(
            matching: largeTextVC,
            as: .image(traits: .init(preferredContentSizeCategory: .accessibilityExtraLarge))
        )
    }
}
```

## CI Integration

### Xcode Cloud Configuration

```yaml
# ci_workflows/main.yml
version: 1
workflows:
  tests:
    name: Run Tests
    actions:
      - name: Test
        scheme: MyApp
        platform: iOS
        destination: iPhone 15 Pro
    environment:
      xcode: 16.0
    start_conditions:
      - type: pull_request
      - type: push
        branches:
          - main
          - develop
    post_actions:
      - name: Upload Coverage
        script: scripts/upload_coverage.sh
```

### GitHub Actions

```yaml
# .github/workflows/ios-tests.yml
name: iOS Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: macos-14

    steps:
    - uses: actions/checkout@v4

    - name: Select Xcode
      run: sudo xcode-select -s /Applications/Xcode_16.0.app

    - name: Show Xcode version
      run: xcodebuild -version

    - name: Run Unit Tests
      run: |
        xcodebuild test \
          -scheme MyApp \
          -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=17.0' \
          -enableCodeCoverage YES \
          -resultBundlePath TestResults

    - name: Run UI Tests
      run: |
        xcodebuild test \
          -scheme MyAppUITests \
          -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=17.0' \
          -resultBundlePath UITestResults

    - name: Upload Coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./TestResults/coverage.xml
        fail_ci_if_error: true

    - name: Upload Test Results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results
        path: |
          TestResults
          UITestResults
```

### Fastlane Integration

```ruby
# fastlane/Fastfile

default_platform(:ios)

platform :ios do

  desc "Run all tests"
  lane :test do
    run_tests(
      scheme: "MyApp",
      devices: ["iPhone 15 Pro"],
      clean: true,
      code_coverage: true,
      output_directory: "./test_output",
      output_types: "html,junit"
    )
  end

  desc "Run unit tests only"
  lane :test_unit do
    scan(
      scheme: "MyApp",
      skip_testing: [
        "MyAppUITests"
      ],
      code_coverage: true
    )
  end

  desc "Run UI tests only"
  lane :test_ui do
    scan(
      scheme: "MyApp",
      only_testing: [
        "MyAppUITests"
      ]
    )
  end

  desc "Generate coverage report"
  lane :coverage do
    slather(
      scheme: "MyApp",
      workspace: "MyApp.xcworkspace",
      html: true,
      output_directory: "./coverage",
      ignore: [
        "Pods/*",
        "MyAppTests/*",
        "MyAppUITests/*"
      ]
    )
  end
end
```

## 6 типичных ошибок

### 1. Тестирование implementation details вместо behavior

```swift
// ❌ Плохо - тестируем внутреннюю реализацию
func testViewModelCallsRepository() async {
    let mockRepo = MockRepository()
    let viewModel = ViewModel(repository: mockRepo)

    await viewModel.loadData()

    XCTAssertTrue(mockRepo.fetchCalled)  // Хрупкий тест
    XCTAssertEqual(mockRepo.callCount, 1)  // Детали реализации
}

// ✅ Хорошо - тестируем поведение
func testViewModelLoadsDataSuccessfully() async {
    let mockRepo = MockRepository()
    mockRepo.data = [Item(id: "1", name: "Test")]
    let viewModel = ViewModel(repository: mockRepo)

    await viewModel.loadData()

    XCTAssertEqual(viewModel.items.count, 1)
    XCTAssertEqual(viewModel.items.first?.name, "Test")
    XCTAssertFalse(viewModel.isLoading)
    XCTAssertNil(viewModel.error)
}
```

### 2. Неправильное использование async/await в тестах

```swift
// ❌ Плохо - забыли await
func testAsyncFunction() {
    let service = NetworkService()

    service.fetchData()  // Тест завершится до выполнения

    XCTAssertFalse(service.data.isEmpty)  // Всегда fails
}

// ❌ Плохо - используем старый подход с expectations
func testWithExpectation() {
    let expectation = expectation(description: "Fetch")
    let service = NetworkService()

    Task {
        await service.fetchData()
        expectation.fulfill()
    }

    waitForExpectations(timeout: 5)
    // data может быть недоступна здесь
}

// ✅ Хорошо - правильный async test
func testAsyncFunctionCorrectly() async throws {
    let service = NetworkService()

    try await service.fetchData()

    XCTAssertFalse(service.data.isEmpty)
    XCTAssertGreaterThan(service.data.count, 0)
}

// ✅ Хорошо - тестируем MainActor
func testMainActorFunction() async {
    let viewModel = ViewModel()

    await viewModel.loadData()

    await MainActor.run {
        XCTAssertTrue(viewModel.isLoaded)
        XCTAssertFalse(viewModel.items.isEmpty)
    }
}
```

### 3. Отсутствие изоляции между тестами

```swift
// ❌ Плохо - shared state между тестами
final class BadTests: XCTestCase {
    let viewModel = ViewModel()  // Переиспользуется!

    func testFirstFeature() {
        viewModel.value = 5
        XCTAssertEqual(viewModel.value, 5)
    }

    func testSecondFeature() {
        // value может быть 5 из предыдущего теста!
        XCTAssertEqual(viewModel.value, 0)  // Flaky test
    }
}

// ✅ Хорошо - чистый state для каждого теста
final class GoodTests: XCTestCase {
    var viewModel: ViewModel!

    override func setUp() {
        super.setUp()
        viewModel = ViewModel()  // Новый экземпляр каждый раз
    }

    override func tearDown() {
        viewModel = nil  // Cleanup
        super.tearDown()
    }

    func testFirstFeature() {
        viewModel.value = 5
        XCTAssertEqual(viewModel.value, 5)
    }

    func testSecondFeature() {
        XCTAssertEqual(viewModel.value, 0)  // Всегда проходит
    }
}
```

### 4. Хрупкие UI тесты без accessibility identifiers

```swift
// ❌ Плохо - тесты ломаются при изменении текста
func testLoginButtonByText() {
    let app = XCUIApplication()
    app.launch()

    let button = app.buttons["Log In"]  // Сломается при изменении на "Sign In"
    button.tap()
}

// ❌ Плохо - зависимость от порядка элементов
func testFirstButton() {
    let app = XCUIApplication()
    app.launch()

    let button = app.buttons.element(boundBy: 0)  // Хрупкий
    button.tap()
}

// ✅ Хорошо - стабильные identifiers
func testLoginButtonByIdentifier() {
    let app = XCUIApplication()
    app.launch()

    let button = app.buttons["loginButton"]  // Не зависит от текста
    XCTAssertTrue(button.exists)
    button.tap()
}

// ✅ Хорошо - semantic identifiers
struct LoginView: View {
    var body: some View {
        VStack {
            TextField("Email", text: $email)
                .accessibilityIdentifier("emailTextField")

            SecureField("Password", text: $password)
                .accessibilityIdentifier("passwordTextField")

            Button(loginButtonTitle) {  // Текст может меняться
                login()
            }
            .accessibilityIdentifier("loginButton")  // ID стабилен
        }
    }
}
```

### 5. Недостаточное покрытие error cases

```swift
// ❌ Плохо - только happy path
func testDataLoading() async {
    let viewModel = ViewModel()

    await viewModel.loadData()

    XCTAssertFalse(viewModel.items.isEmpty)
}

// ✅ Хорошо - все сценарии
final class ComprehensiveTests: XCTestCase {

    var sut: ViewModel!
    var mockRepository: MockRepository!

    override func setUp() {
        super.setUp()
        mockRepository = MockRepository()
        sut = ViewModel(repository: mockRepository)
    }

    func testSuccessfulDataLoading() async {
        // Arrange
        mockRepository.data = [Item(id: "1", name: "Test")]

        // Act
        await sut.loadData()

        // Assert
        XCTAssertEqual(sut.items.count, 1)
        XCTAssertFalse(sut.isLoading)
        XCTAssertNil(sut.error)
    }

    func testNetworkError() async {
        // Arrange
        mockRepository.shouldFail = true
        mockRepository.error = .networkError

        // Act
        await sut.loadData()

        // Assert
        XCTAssertTrue(sut.items.isEmpty)
        XCTAssertNotNil(sut.error)
        XCTAssertEqual(sut.error as? NetworkError, .networkError)
    }

    func testEmptyResponse() async {
        // Arrange
        mockRepository.data = []

        // Act
        await sut.loadData()

        // Assert
        XCTAssertTrue(sut.items.isEmpty)
        XCTAssertTrue(sut.showEmptyState)
    }

    func testUnauthorizedError() async {
        // Arrange
        mockRepository.shouldFail = true
        mockRepository.error = .unauthorized

        // Act
        await sut.loadData()

        // Assert
        XCTAssertTrue(sut.shouldShowLogin)
    }
}
```

### 6. Медленные тесты из-за реальных зависимостей

```swift
// ❌ Плохо - реальный network, database, UserDefaults
final class SlowTests: XCTestCase {

    func testUserProfile() async {
        let service = NetworkService()  // Реальная сеть!

        let user = try? await service.fetchUser(id: "123")

        XCTAssertNotNil(user)
    }

    func testDataPersistence() {
        let manager = CoreDataManager()  // Реальная база!

        manager.save(user: User(name: "Test"))

        let users = manager.fetchUsers()
        XCTAssertEqual(users.count, 1)
    }
}

// ✅ Хорошо - моки и in-memory зависимости
final class FastTests: XCTestCase {

    var mockNetwork: MockNetworkService!
    var inMemoryContext: NSManagedObjectContext!

    override func setUp() {
        super.setUp()

        // Mock network
        mockNetwork = MockNetworkService()

        // In-memory Core Data
        let container = NSPersistentContainer(
            name: "Model",
            managedObjectModel: NSManagedObjectModel()
        )

        let description = NSPersistentStoreDescription()
        description.type = NSInMemoryStoreType
        container.persistentStoreDescriptions = [description]

        container.loadPersistentStores { _, error in
            XCTAssertNil(error)
        }

        inMemoryContext = container.viewContext
    }

    func testUserProfileFast() async {
        // Arrange
        mockNetwork.user = User(id: "123", name: "Test")
        let service = UserService(network: mockNetwork)

        // Act
        let user = try? await service.fetchUser(id: "123")

        // Assert
        XCTAssertEqual(user?.name, "Test")
    }

    func testDataPersistenceFast() {
        // Arrange
        let manager = CoreDataManager(context: inMemoryContext)

        // Act
        manager.save(user: User(name: "Test"))
        let users = manager.fetchUsers()

        // Assert
        XCTAssertEqual(users.count, 1)
        XCTAssertEqual(users.first?.name, "Test")
    }

    override func tearDown() {
        // Clean in-memory database
        let fetchRequest: NSFetchRequest<NSFetchRequestResult> =
            NSFetchRequest(entityName: "User")
        let deleteRequest = NSBatchDeleteRequest(fetchRequest: fetchRequest)

        try? inMemoryContext.execute(deleteRequest)

        mockNetwork = nil
        inMemoryContext = nil
        super.tearDown()
    }
}
```

## Связанные материалы

- [[android-testing]] - Testing в Android разработке
- [[swiftui]] - SwiftUI фреймворк
- [[combine]] - Reactive programming с Combine
- [[dependency-injection]] - Паттерны dependency injection
- [[tdd]] - Test-Driven Development
- [[ci-cd]] - Continuous Integration/Deployment
