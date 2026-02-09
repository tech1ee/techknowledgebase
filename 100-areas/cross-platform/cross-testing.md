---
title: "Cross-Platform: Testing — XCTest vs JUnit"
created: 2026-01-11
type: comparison
tags: [cross-platform, testing, xctest, junit]
---

# Cross-Platform Testing: XCTest vs JUnit

## TL;DR

| Аспект | iOS (XCTest) | Android (JUnit) |
|--------|--------------|-----------------|
| **Фреймворк** | XCTest (встроен в Xcode) | JUnit 4/5 + AndroidX Test |
| **Запуск тестов** | Cmd+U в Xcode | `./gradlew test` |
| **Assertions** | `XCTAssert*` | `assertEquals`, `assertThat` |
| **Mocking** | Protocol-based / ручной | Mockk, Mockito |
| **UI-тесты** | XCUITest | Espresso, Compose Testing |
| **Async-тесты** | `async/await`, expectations | Coroutines, `runTest` |
| **Параллелизм** | Xcode Parallel Testing | Gradle parallel execution |
| **Code Coverage** | Xcode Coverage | JaCoCo |
| **Snapshot-тесты** | swift-snapshot-testing | Paparazzi, Shot |
| **KMP** | kotlin.test + XCTest runner | kotlin.test + JUnit runner |

---

## 1. Unit Testing: XCTest vs JUnit/JUnit5

### Базовая структура теста

```swift
// iOS — XCTest
import XCTest
@testable import MyApp

final class UserServiceTests: XCTestCase {

    var sut: UserService!  // System Under Test

    override func setUp() {
        super.setUp()
        sut = UserService()
    }

    override func tearDown() {
        sut = nil
        super.tearDown()
    }

    func testFetchUser_WithValidId_ReturnsUser() {
        // Given
        let userId = "123"

        // When
        let user = sut.fetchUser(id: userId)

        // Then
        XCTAssertNotNil(user)
        XCTAssertEqual(user?.id, userId)
        XCTAssertEqual(user?.name, "John")
    }

    func testFetchUser_WithInvalidId_ReturnsNil() {
        // Given
        let userId = "invalid"

        // When
        let user = sut.fetchUser(id: userId)

        // Then
        XCTAssertNil(user)
    }
}
```

```kotlin
// Android — JUnit 5
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.*

class UserServiceTests {

    private lateinit var sut: UserService  // System Under Test

    @BeforeEach
    fun setUp() {
        sut = UserService()
    }

    @AfterEach
    fun tearDown() {
        // cleanup если нужно
    }

    @Test
    fun `fetchUser with valid id returns user`() {
        // Given
        val userId = "123"

        // When
        val user = sut.fetchUser(id = userId)

        // Then
        assertNotNull(user)
        assertEquals(userId, user?.id)
        assertEquals("John", user?.name)
    }

    @Test
    fun `fetchUser with invalid id returns null`() {
        // Given
        val userId = "invalid"

        // When
        val user = sut.fetchUser(id = userId)

        // Then
        assertNull(user)
    }
}
```

### Assertions: сравнение

```swift
// iOS — XCTest Assertions
XCTAssertTrue(condition)
XCTAssertFalse(condition)
XCTAssertNil(optional)
XCTAssertNotNil(optional)
XCTAssertEqual(a, b)
XCTAssertNotEqual(a, b)
XCTAssertGreaterThan(a, b)
XCTAssertLessThan(a, b)
XCTAssertThrowsError(try throwingFunc())
XCTFail("Причина провала")

// С сообщением
XCTAssertEqual(result, expected, "Результат должен быть \(expected)")

// Точность для Float/Double
XCTAssertEqual(3.14159, Double.pi, accuracy: 0.001)
```

```kotlin
// Android — JUnit 5 Assertions
assertTrue(condition)
assertFalse(condition)
assertNull(optional)
assertNotNull(optional)
assertEquals(expected, actual)  // Порядок важен!
assertNotEquals(unexpected, actual)
assertTrue(a > b)
assertTrue(a < b)
assertThrows<IllegalArgumentException> { throwingFunc() }
fail("Причина провала")

// С сообщением
assertEquals(expected, result) { "Результат должен быть $expected" }

// Точность для Float/Double
assertEquals(3.14159, Math.PI, 0.001)

// AssertJ / Truth (более читаемые)
assertThat(result).isEqualTo(expected)
assertThat(list).hasSize(3).contains("item")
```

### Асинхронные тесты

```swift
// iOS — async/await (современный подход)
func testAsyncFetchUser() async throws {
    // Given
    let userId = "123"

    // When
    let user = try await sut.fetchUserAsync(id: userId)

    // Then
    XCTAssertEqual(user.name, "John")
}

// iOS — XCTestExpectation (legacy подход)
func testFetchUserWithCallback() {
    // Given
    let expectation = expectation(description: "User fetched")
    var fetchedUser: User?

    // When
    sut.fetchUser(id: "123") { user in
        fetchedUser = user
        expectation.fulfill()
    }

    // Then
    wait(for: [expectation], timeout: 5.0)
    XCTAssertNotNil(fetchedUser)
}
```

```kotlin
// Android — Coroutines с runTest
@Test
fun `async fetch user returns correct user`() = runTest {
    // Given
    val userId = "123"

    // When
    val user = sut.fetchUserAsync(id = userId)

    // Then
    assertEquals("John", user.name)
}

// Android — с TestDispatcher для контроля времени
@Test
fun `delayed operation completes after delay`() = runTest {
    val result = async { sut.delayedOperation() }

    // Промотать время
    advanceTimeBy(1000)

    assertTrue(result.isCompleted)
}
```

---

## 2. Mocking: Protocol-based vs Mockk/Mockito

### iOS: Protocol-based Mocking

```swift
// Протокол для зависимости
protocol UserRepository {
    func getUser(id: String) async throws -> User
    func saveUser(_ user: User) async throws
}

// Mock-реализация
final class MockUserRepository: UserRepository {

    // Tracking вызовов
    var getUserCallCount = 0
    var getUserLastId: String?
    var saveUserCallCount = 0
    var savedUsers: [User] = []

    // Stubbed responses
    var getUserResult: Result<User, Error> = .success(User(id: "1", name: "Test"))

    func getUser(id: String) async throws -> User {
        getUserCallCount += 1
        getUserLastId = id
        return try getUserResult.get()
    }

    func saveUser(_ user: User) async throws {
        saveUserCallCount += 1
        savedUsers.append(user)
    }
}

// Использование в тесте
final class UserViewModelTests: XCTestCase {

    var sut: UserViewModel!
    var mockRepository: MockUserRepository!

    override func setUp() {
        super.setUp()
        mockRepository = MockUserRepository()
        sut = UserViewModel(repository: mockRepository)
    }

    func testLoadUser_CallsRepository() async {
        // Given
        let expectedUser = User(id: "123", name: "John")
        mockRepository.getUserResult = .success(expectedUser)

        // When
        await sut.loadUser(id: "123")

        // Then
        XCTAssertEqual(mockRepository.getUserCallCount, 1)
        XCTAssertEqual(mockRepository.getUserLastId, "123")
        XCTAssertEqual(sut.user, expectedUser)
    }

    func testLoadUser_WhenError_SetsErrorState() async {
        // Given
        mockRepository.getUserResult = .failure(NetworkError.notFound)

        // When
        await sut.loadUser(id: "invalid")

        // Then
        XCTAssertNotNil(sut.error)
        XCTAssertNil(sut.user)
    }
}
```

### Android: Mockk

```kotlin
// Интерфейс для зависимости
interface UserRepository {
    suspend fun getUser(id: String): User
    suspend fun saveUser(user: User)
}

// Тест с Mockk
class UserViewModelTests {

    private lateinit var sut: UserViewModel
    private val mockRepository: UserRepository = mockk()

    @BeforeEach
    fun setUp() {
        sut = UserViewModel(repository = mockRepository)
    }

    @Test
    fun `loadUser calls repository`() = runTest {
        // Given
        val expectedUser = User(id = "123", name = "John")
        coEvery { mockRepository.getUser("123") } returns expectedUser

        // When
        sut.loadUser(id = "123")

        // Then
        coVerify(exactly = 1) { mockRepository.getUser("123") }
        assertEquals(expectedUser, sut.user.value)
    }

    @Test
    fun `loadUser when error sets error state`() = runTest {
        // Given
        coEvery { mockRepository.getUser(any()) } throws NotFoundException()

        // When
        sut.loadUser(id = "invalid")

        // Then
        assertNotNull(sut.error.value)
        assertNull(sut.user.value)
    }

    @Test
    fun `saveUser captures correct argument`() = runTest {
        // Given
        val slot = slot<User>()
        coEvery { mockRepository.saveUser(capture(slot)) } just Runs

        val user = User(id = "1", name = "New User")

        // When
        sut.saveUser(user)

        // Then
        assertEquals("New User", slot.captured.name)
    }
}
```

### Android: Mockito (альтернатива)

```kotlin
// Тест с Mockito
@ExtendWith(MockitoExtension::class)
class UserViewModelMockitoTests {

    @Mock
    private lateinit var mockRepository: UserRepository

    @InjectMocks
    private lateinit var sut: UserViewModel

    @Test
    fun `loadUser calls repository`() = runTest {
        // Given
        val expectedUser = User(id = "123", name = "John")
        whenever(mockRepository.getUser("123")).thenReturn(expectedUser)

        // When
        sut.loadUser(id = "123")

        // Then
        verify(mockRepository, times(1)).getUser("123")
        assertEquals(expectedUser, sut.user.value)
    }
}
```

---

## 3. UI Testing: XCUITest vs Espresso/Compose Testing

### XCUITest (iOS)

```swift
// UI-тест для экрана логина
final class LoginUITests: XCTestCase {

    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--uitesting"]
        app.launch()
    }

    func testSuccessfulLogin() {
        // Given — находим элементы
        let emailField = app.textFields["emailTextField"]
        let passwordField = app.secureTextFields["passwordTextField"]
        let loginButton = app.buttons["loginButton"]

        // When — вводим данные
        emailField.tap()
        emailField.typeText("user@example.com")

        passwordField.tap()
        passwordField.typeText("password123")

        loginButton.tap()

        // Then — проверяем результат
        let homeScreen = app.otherElements["homeScreen"]
        XCTAssertTrue(homeScreen.waitForExistence(timeout: 5))
    }

    func testLoginValidation_EmptyEmail_ShowsError() {
        // Given
        let passwordField = app.secureTextFields["passwordTextField"]
        let loginButton = app.buttons["loginButton"]

        // When
        passwordField.tap()
        passwordField.typeText("password123")
        loginButton.tap()

        // Then
        let errorLabel = app.staticTexts["errorLabel"]
        XCTAssertTrue(errorLabel.waitForExistence(timeout: 2))
        XCTAssertEqual(errorLabel.label, "Email обязателен")
    }
}
```

### Espresso (Android Views)

```kotlin
// UI-тест для экрана логина с Espresso
@RunWith(AndroidJUnit4::class)
class LoginUITests {

    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun successfulLogin_navigatesToHome() {
        // Given & When — вводим данные
        onView(withId(R.id.emailTextField))
            .perform(typeText("user@example.com"), closeSoftKeyboard())

        onView(withId(R.id.passwordTextField))
            .perform(typeText("password123"), closeSoftKeyboard())

        onView(withId(R.id.loginButton))
            .perform(click())

        // Then — проверяем результат
        onView(withId(R.id.homeScreen))
            .check(matches(isDisplayed()))
    }

    @Test
    fun loginValidation_emptyEmail_showsError() {
        // Given & When
        onView(withId(R.id.passwordTextField))
            .perform(typeText("password123"), closeSoftKeyboard())

        onView(withId(R.id.loginButton))
            .perform(click())

        // Then
        onView(withId(R.id.errorLabel))
            .check(matches(isDisplayed()))
            .check(matches(withText("Email обязателен")))
    }
}
```

### Compose Testing (Android Compose)

```kotlin
// UI-тест для Compose
class LoginComposeTests {

    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun successfulLogin_navigatesToHome() {
        // Given
        var navigatedToHome = false

        composeRule.setContent {
            LoginScreen(
                onLoginSuccess = { navigatedToHome = true }
            )
        }

        // When
        composeRule
            .onNodeWithTag("emailTextField")
            .performTextInput("user@example.com")

        composeRule
            .onNodeWithTag("passwordTextField")
            .performTextInput("password123")

        composeRule
            .onNodeWithTag("loginButton")
            .performClick()

        // Then
        composeRule.waitUntil(timeoutMillis = 5000) {
            navigatedToHome
        }
        assertTrue(navigatedToHome)
    }

    @Test
    fun loginValidation_emptyEmail_showsError() {
        // Given
        composeRule.setContent {
            LoginScreen(onLoginSuccess = {})
        }

        // When
        composeRule
            .onNodeWithTag("passwordTextField")
            .performTextInput("password123")

        composeRule
            .onNodeWithTag("loginButton")
            .performClick()

        // Then
        composeRule
            .onNodeWithText("Email обязателен")
            .assertIsDisplayed()
    }
}
```

---

## 4. KMP Testing с kotlin.test

```kotlin
// commonTest — общие тесты для всех платформ
// src/commonTest/kotlin/UserServiceTests.kt

import kotlin.test.*

class UserServiceTests {

    private lateinit var sut: UserService

    @BeforeTest
    fun setUp() {
        sut = UserService()
    }

    @AfterTest
    fun tearDown() {
        // cleanup
    }

    @Test
    fun fetchUser_withValidId_returnsUser() {
        // Given
        val userId = "123"

        // When
        val user = sut.fetchUser(id = userId)

        // Then
        assertNotNull(user)
        assertEquals(userId, user.id)
        assertEquals("John", user.name)
    }

    @Test
    fun fetchUser_withInvalidId_returnsNull() {
        // Given
        val userId = "invalid"

        // When
        val user = sut.fetchUser(id = userId)

        // Then
        assertNull(user)
    }

    @Test
    fun parseJson_withInvalidJson_throwsException() {
        assertFailsWith<JsonParseException> {
            sut.parseJson("invalid json")
        }
    }
}

// Асинхронные тесты в KMP
class AsyncUserServiceTests {

    @Test
    fun fetchUserAsync_returnsUser() = runTest {
        // Given
        val sut = UserService()

        // When
        val user = sut.fetchUserAsync(id = "123")

        // Then
        assertEquals("John", user.name)
    }
}
```

### Platform-specific тесты

```kotlin
// iosTest — тесты специфичные для iOS
// src/iosTest/kotlin/IOSSpecificTests.kt

import kotlin.test.*
import platform.Foundation.NSUserDefaults

class IOSStorageTests {

    @Test
    fun nsUserDefaults_savesAndRetrievesValue() {
        // Given
        val defaults = NSUserDefaults.standardUserDefaults

        // When
        defaults.setObject("test_value", forKey = "test_key")

        // Then
        val retrieved = defaults.stringForKey("test_key")
        assertEquals("test_value", retrieved)
    }
}

// androidTest — тесты специфичные для Android
// src/androidTest/kotlin/AndroidSpecificTests.kt

import kotlin.test.*
import android.content.Context
import androidx.test.core.app.ApplicationProvider

class AndroidStorageTests {

    @Test
    fun sharedPreferences_savesAndRetrievesValue() {
        // Given
        val context = ApplicationProvider.getApplicationContext<Context>()
        val prefs = context.getSharedPreferences("test", Context.MODE_PRIVATE)

        // When
        prefs.edit().putString("test_key", "test_value").apply()

        // Then
        val retrieved = prefs.getString("test_key", null)
        assertEquals("test_value", retrieved)
    }
}
```

---

## 5. Шесть распространённых ошибок

### Ошибка 1: Тестирование реализации вместо поведения

```swift
// ПЛОХО — тестируем внутреннюю реализацию
func testLoadUsers_CallsAPIClient() {
    viewModel.loadUsers()
    XCTAssertEqual(mockAPIClient.getCallCount, 1)  // Хрупкий тест
}

// ХОРОШО — тестируем поведение
func testLoadUsers_DisplaysUserList() async {
    mockRepository.users = [User(name: "John")]
    await viewModel.loadUsers()
    XCTAssertEqual(viewModel.users.count, 1)
    XCTAssertEqual(viewModel.users.first?.name, "John")
}
```

### Ошибка 2: Отсутствие изоляции тестов

```kotlin
// ПЛОХО — тесты зависят друг от друга
class BadTests {
    companion object {
        var sharedState = 0  // Общее состояние
    }

    @Test
    fun test1() {
        sharedState = 1
        assertEquals(1, sharedState)
    }

    @Test
    fun test2() {
        // Зависит от порядка выполнения!
        assertEquals(1, sharedState)  // Может упасть
    }
}

// ХОРОШО — каждый тест изолирован
class GoodTests {
    private var state = 0

    @BeforeEach
    fun setUp() {
        state = 0  // Сброс перед каждым тестом
    }

    @Test
    fun test1() {
        state = 1
        assertEquals(1, state)
    }

    @Test
    fun test2() {
        assertEquals(0, state)  // Всегда предсказуемо
    }
}
```

### Ошибка 3: Flaky async-тесты

```swift
// ПЛОХО — ненадёжный таймаут
func testAsyncOperation() {
    viewModel.loadData()
    Thread.sleep(forTimeInterval: 2.0)  // Может быть недостаточно
    XCTAssertNotNil(viewModel.data)
}

// ХОРОШО — явное ожидание
func testAsyncOperation() async {
    await viewModel.loadData()
    XCTAssertNotNil(viewModel.data)
}

// Или с expectation
func testAsyncOperation() {
    let expectation = expectation(description: "Data loaded")
    viewModel.$data
        .dropFirst()
        .sink { _ in expectation.fulfill() }
        .store(in: &cancellables)

    viewModel.loadData()
    wait(for: [expectation], timeout: 5.0)
}
```

### Ошибка 4: Слишком много assertions в одном тесте

```kotlin
// ПЛОХО — много assertions, непонятно что упало
@Test
fun testUserCreation() {
    val user = createUser()
    assertEquals("John", user.name)
    assertEquals("john@email.com", user.email)
    assertEquals(25, user.age)
    assertTrue(user.isActive)
    assertNotNull(user.createdAt)
    assertEquals(0, user.posts.size)
}

// ХОРОШО — отдельные тесты для каждого аспекта
@Test
fun `createUser sets correct name`() {
    val user = createUser()
    assertEquals("John", user.name)
}

@Test
fun `createUser sets default active status`() {
    val user = createUser()
    assertTrue(user.isActive)
}

@Test
fun `createUser initializes empty posts`() {
    val user = createUser()
    assertTrue(user.posts.isEmpty())
}
```

### Ошибка 5: Тестирование приватных методов напрямую

```swift
// ПЛОХО — пытаемся тестировать приватный метод
// Это даже не скомпилируется в Swift
// let result = viewModel.privateHelperMethod()

// ХОРОШО — тестируем через публичный API
func testCalculateTotal_AppliesDiscount() {
    // privateCalculateDiscount вызывается внутри
    let total = viewModel.calculateTotal(items: items, hasPromo: true)
    XCTAssertEqual(total, 90.0)  // 10% скидка применена
}
```

### Ошибка 6: Игнорирование edge cases

```kotlin
// ПЛОХО — только happy path
@Test
fun `divide returns correct result`() {
    assertEquals(2.0, calculator.divide(4.0, 2.0))
}

// ХОРОШО — покрываем edge cases
@Test
fun `divide returns correct result`() {
    assertEquals(2.0, calculator.divide(4.0, 2.0))
}

@Test
fun `divide by zero throws exception`() {
    assertThrows<ArithmeticException> {
        calculator.divide(4.0, 0.0)
    }
}

@Test
fun `divide with negative numbers`() {
    assertEquals(-2.0, calculator.divide(-4.0, 2.0))
}

@Test
fun `divide zero by number returns zero`() {
    assertEquals(0.0, calculator.divide(0.0, 5.0))
}
```

---

## 6. Три ментальные модели

### Модель 1: Пирамида тестирования

```
                    /\
                   /  \
                  / E2E \        ← Мало, медленные, дорогие
                 /--------\
                /Integration\    ← Средне
               /--------------\
              /     Unit       \  ← Много, быстрые, дешёвые
             /------------------\
```

**Правило**: 70% Unit, 20% Integration, 10% E2E

```swift
// Unit — тестирует один компонент в изоляции
func testUserValidator_ValidEmail_ReturnsTrue() {
    let validator = UserValidator()
    XCTAssertTrue(validator.isValidEmail("test@example.com"))
}

// Integration — тестирует взаимодействие компонентов
func testUserService_SavesAndFetches() async {
    let service = UserService(database: realDatabase)
    await service.save(user)
    let fetched = await service.fetch(id: user.id)
    XCTAssertEqual(fetched, user)
}

// E2E — тестирует весь flow от UI до базы
func testRegistrationFlow() {
    // Полный сценарий регистрации через UI
}
```

### Модель 2: Given-When-Then (AAA)

```
┌─────────────────────────────────────┐
│  GIVEN (Arrange)                    │
│  Подготовка состояния и данных      │
├─────────────────────────────────────┤
│  WHEN (Act)                         │
│  Выполнение тестируемого действия   │
├─────────────────────────────────────┤
│  THEN (Assert)                      │
│  Проверка результата                │
└─────────────────────────────────────┘
```

```kotlin
@Test
fun `transfer money updates both accounts`() {
    // GIVEN — начальное состояние
    val sourceAccount = Account(balance = 1000.0)
    val targetAccount = Account(balance = 500.0)
    val transferService = TransferService()

    // WHEN — действие
    transferService.transfer(
        from = sourceAccount,
        to = targetAccount,
        amount = 200.0
    )

    // THEN — проверка
    assertEquals(800.0, sourceAccount.balance)
    assertEquals(700.0, targetAccount.balance)
}
```

### Модель 3: Test Doubles (типы подмен)

```
┌──────────────┬─────────────────────────────────────────┐
│ Dummy        │ Заглушка без логики                     │
│              │ val dummy = User(id = "", name = "")    │
├──────────────┼─────────────────────────────────────────┤
│ Stub         │ Возвращает заготовленные данные        │
│              │ every { repo.getUser() } returns user  │
├──────────────┼─────────────────────────────────────────┤
│ Spy          │ Обёртка с отслеживанием вызовов        │
│              │ verify { repo.save(any()) }            │
├──────────────┼─────────────────────────────────────────┤
│ Mock         │ Stub + Spy + expectations              │
│              │ coEvery + coVerify                      │
├──────────────┼─────────────────────────────────────────┤
│ Fake         │ Рабочая упрощённая реализация          │
│              │ InMemoryDatabase вместо SQLite         │
└──────────────┴─────────────────────────────────────────┘
```

```swift
// Fake — полностью рабочая, но упрощённая реализация
final class FakeUserRepository: UserRepository {
    private var storage: [String: User] = [:]

    func save(_ user: User) async {
        storage[user.id] = user
    }

    func fetch(id: String) async -> User? {
        return storage[id]
    }

    func delete(id: String) async {
        storage.removeValue(forKey: id)
    }
}

// Использование Fake в тестах
func testUserService_WithFakeRepository() async {
    let fakeRepo = FakeUserRepository()
    let service = UserService(repository: fakeRepo)

    // Тест работает с реальной логикой, но без базы данных
    await service.createUser(name: "John")
    let users = await service.getAllUsers()
    XCTAssertEqual(users.count, 1)
}
```

---

## 7. Quiz

### Вопрос 1
Какой тип Test Double следует использовать, когда нужно проверить, что метод был вызван с определёнными аргументами?

A) Dummy
B) Stub
C) Mock/Spy
D) Fake

<details>
<summary>Ответ</summary>

**C) Mock/Spy**

Mock и Spy позволяют отслеживать вызовы методов и проверять их аргументы:
```kotlin
coVerify { repository.save(match { it.name == "John" }) }
```
</details>

---

### Вопрос 2
Что неправильно в этом тесте?

```swift
func testUserList() {
    viewModel.loadUsers()
    sleep(3)
    XCTAssertEqual(viewModel.users.count, 5)
}
```

A) Нельзя использовать sleep в тестах
B) Тест flaky — результат непредсказуем
C) Не используется Given-When-Then
D) Слишком мало assertions

<details>
<summary>Ответ</summary>

**B) Тест flaky — результат непредсказуем**

`sleep(3)` не гарантирует, что асинхронная операция завершится за это время. Правильно использовать `async/await` или `XCTestExpectation`:
```swift
func testUserList() async {
    await viewModel.loadUsers()
    XCTAssertEqual(viewModel.users.count, 5)
}
```
</details>

---

### Вопрос 3
Согласно пирамиде тестирования, какое соотношение тестов оптимально?

A) 70% E2E, 20% Integration, 10% Unit
B) 33% каждого типа
C) 70% Unit, 20% Integration, 10% E2E
D) 50% Unit, 50% E2E

<details>
<summary>Ответ</summary>

**C) 70% Unit, 20% Integration, 10% E2E**

Unit-тесты быстрые, дешёвые и стабильные — их должно быть больше всего. E2E тесты медленные и хрупкие — их должно быть минимум, только для критичных сценариев.
</details>

---

## 8. Связанные заметки

- [[ios-testing]] — детали XCTest, snapshot-тестирование, TDD в iOS
- [[android-testing]] — JUnit, Mockk, Espresso, Robolectric
- [[cross-architecture]] — архитектурные паттерны и их тестируемость
- [[cross-async]] — асинхронность и её тестирование
- [[cross-di]] — DI и его роль в тестировании

---

## Ресурсы

- [XCTest Documentation](https://developer.apple.com/documentation/xctest)
- [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/)
- [Mockk Documentation](https://mockk.io/)
- [Espresso Testing](https://developer.android.com/training/testing/espresso)
- [Compose Testing](https://developer.android.com/jetpack/compose/testing)
- [kotlin.test](https://kotlinlang.org/api/latest/kotlin.test/)
