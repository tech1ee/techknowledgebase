---
title: "Тестирование: Unit, Integration, UI тесты"
created: 2025-12-17
modified: 2026-02-13
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/testing
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-architecture-patterns]]"
  - "[[android-dependency-injection]]"
  - "[[kotlin-coroutines]]"
cs-foundations: [test-pyramid, test-doubles, test-isolation, determinism]
prerequisites:
  - "[[android-overview]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-architecture-patterns]]"
reading_time: 31
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Тестирование: Unit, Integration, UI тесты

Тестирование в Android делится на три уровня: **Unit тесты** (логика без Android), **Integration тесты** (взаимодействие компонентов), **UI тесты** (реальное устройство/эмулятор). Правильная архитектура (MVVM, Clean) делает код тестируемым.

> **Prerequisites:**
> - [[android-architecture-patterns]] — тестируемая архитектура (MVVM, Clean) необходима для изоляции компонентов
> - [[android-dependency-injection]] — подмена зависимостей через DI для изоляции тестов
> - Базовое понимание unit testing (JUnit) — фреймворк для запуска тестов

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Unit Test** | Тест одного класса в изоляции |
| **Integration Test** | Тест взаимодействия нескольких компонентов |
| **UI Test** | Тест пользовательского интерфейса |
| **Mock** | Подменный объект с запрограммированным поведением |
| **Stub** | Простая заглушка с фиксированными ответами |
| **Fake** | Упрощённая рабочая реализация для тестов |
| **Test Double** | Общий термин для Mock/Stub/Fake |
| **Instrumented Test** | Тест на устройстве/эмуляторе |
| **Local Test** | Тест на JVM без Android |

---

## Почему тестировать важно?

### Проблема: "работает на моём устройстве"

```kotlin
// ❌ Код, который сложно протестировать
class UserViewModel : ViewModel() {

    private val api = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .build()
        .create(ApiService::class.java)

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val users = api.getUsers()  // Реальный API
                _users.value = users
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
}

// Как протестировать?
// - Нужен реальный сервер
// - Нужен интернет
// - Тест медленный и нестабильный
```

### Что можно протестировать без правильной архитектуры

| Компонент | Без DI | С DI |
|-----------|--------|------|
| ViewModel с API | Невозможно без сервера | Mock API, проверяем логику |
| Repository с DB | Нужен эмулятор | In-memory DB или mock |
| UseCase с Repository | Тянем всю цепочку | Mock repository |
| Бизнес-логика в Activity | Нужен UI | Вынести в ViewModel |

### Правильная архитектура = тестируемость

```kotlin
// ✅ Тестируемый код с DI
class UserViewModel(
    private val repository: UserRepository  // Инжектируется
) : ViewModel() {

    fun loadUsers() {
        viewModelScope.launch {
            repository.getUsers()
                .onSuccess { users -> _users.value = users }
                .onFailure { e -> _error.value = e.message }
        }
    }
}

// Тест — без сервера, без интернета, быстрый
@Test
fun `loadUsers shows error when repository fails`() = runTest {
    // Arrange
    val mockRepository = mockk<UserRepository> {
        coEvery { getUsers() } returns Result.failure(IOException("Network error"))
    }
    val viewModel = UserViewModel(mockRepository)

    // Act
    viewModel.loadUsers()

    // Assert
    assertEquals("Network error", viewModel.error.value)
}
```

---

## Структура тестов в проекте

```
app/
├── src/
│   ├── main/                    # Основной код
│   │   └── java/com/example/
│   │
│   ├── test/                    # Unit тесты (JVM)
│   │   └── java/com/example/
│   │       ├── viewmodel/
│   │       │   └── UserViewModelTest.kt
│   │       └── repository/
│   │           └── UserRepositoryTest.kt
│   │
│   └── androidTest/             # Instrumented тесты (устройство)
│       └── java/com/example/
│           ├── ui/
│           │   └── UserScreenTest.kt
│           └── database/
│               └── UserDaoTest.kt
```

---

## Unit тесты

### Настройка

```kotlin
// build.gradle.kts
dependencies {
    // JUnit 5
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.0")

    // MockK для Kotlin
    testImplementation("io.mockk:mockk:1.13.8")

    // Coroutines test
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")

    // Turbine для Flow тестирования
    testImplementation("app.cash.turbine:turbine:1.0.0")
}

tasks.withType<Test> {
    useJUnitPlatform()
}
```

### Тестирование ViewModel

```kotlin
class UserViewModelTest {

    // Заменяем Main dispatcher на Test
    @OptIn(ExperimentalCoroutinesApi::class)
    @BeforeEach
    fun setup() {
        Dispatchers.setMain(UnconfinedTestDispatcher())
    }

    @AfterEach
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `loadUsers updates state with users on success`() = runTest {
        // Arrange
        val testUsers = listOf(User(1, "Alice"), User(2, "Bob"))
        val mockRepository = mockk<UserRepository> {
            coEvery { getUsers() } returns Result.success(testUsers)
        }
        val viewModel = UserViewModel(mockRepository)

        // Act
        viewModel.loadUsers()

        // Assert
        assertEquals(testUsers, viewModel.users.value)
        assertEquals(false, viewModel.isLoading.value)
        assertNull(viewModel.error.value)
    }

    @Test
    fun `loadUsers shows loading state`() = runTest {
        // Arrange
        val mockRepository = mockk<UserRepository> {
            coEvery { getUsers() } coAnswers {
                delay(100)  // Симулируем задержку
                Result.success(emptyList())
            }
        }
        val viewModel = UserViewModel(mockRepository)

        // Assert — loading должен быть true в процессе
        viewModel.users.test {
            viewModel.loadUsers()

            // Проверяем последовательность состояний
            assertEquals(true, viewModel.isLoading.value)
            awaitItem()  // Ждём результат
            assertEquals(false, viewModel.isLoading.value)
        }
    }

    @Test
    fun `deleteUser calls repository and reloads`() = runTest {
        // Arrange
        val mockRepository = mockk<UserRepository> {
            coEvery { deleteUser(any()) } returns Result.success(Unit)
            coEvery { getUsers() } returns Result.success(emptyList())
        }
        val viewModel = UserViewModel(mockRepository)

        // Act
        viewModel.deleteUser(User(1, "Alice"))

        // Assert
        coVerify(exactly = 1) { mockRepository.deleteUser(User(1, "Alice")) }
        coVerify(exactly = 1) { mockRepository.getUsers() }  // Reload после удаления
    }
}
```

### Тестирование Repository

```kotlin
class UserRepositoryTest {

    private lateinit var repository: UserRepository
    private val mockApi = mockk<ApiService>()
    private val mockDao = mockk<UserDao>(relaxed = true)

    @BeforeEach
    fun setup() {
        repository = UserRepository(mockApi, mockDao)
    }

    @Test
    fun `getUsers returns from API and caches in DB`() = runTest {
        // Arrange
        val apiUsers = listOf(User(1, "Alice"))
        coEvery { mockApi.getUsers() } returns apiUsers

        // Act
        val result = repository.getUsers()

        // Assert
        assertEquals(Result.success(apiUsers), result)
        coVerify { mockDao.insertAll(apiUsers) }  // Проверяем кэширование
    }

    @Test
    fun `getUsers returns from cache when API fails`() = runTest {
        // Arrange
        val cachedUsers = listOf(User(1, "Cached"))
        coEvery { mockApi.getUsers() } throws IOException("No network")
        coEvery { mockDao.getAll() } returns cachedUsers

        // Act
        val result = repository.getUsers()

        // Assert
        assertEquals(Result.success(cachedUsers), result)
    }

    @Test
    fun `getUsers returns error when both API and cache fail`() = runTest {
        // Arrange
        coEvery { mockApi.getUsers() } throws IOException("No network")
        coEvery { mockDao.getAll() } returns emptyList()

        // Act
        val result = repository.getUsers()

        // Assert
        assertTrue(result.isFailure)
    }
}
```

### Тестирование Flow

```kotlin
class UserFlowTest {

    @Test
    fun `search emits results after debounce`() = runTest {
        val repository = mockk<UserRepository> {
            coEvery { search("al") } returns listOf(User(1, "Alice"))
        }
        val viewModel = SearchViewModel(repository)

        viewModel.searchResults.test {
            // Initial empty state
            assertEquals(emptyList<User>(), awaitItem())

            // Type search query
            viewModel.onSearchQueryChanged("al")

            // Wait for debounce (300ms in viewModel)
            advanceTimeBy(300)

            // Should emit results
            assertEquals(listOf(User(1, "Alice")), awaitItem())

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

## Instrumented тесты (Android)

### Тестирование Room DAO

```kotlin
// androidTest/
@RunWith(AndroidJUnit4::class)
class UserDaoTest {

    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        // In-memory database — удаляется после теста
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).build()
        userDao = database.userDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    @Test
    fun insertAndRetrieveUser() = runTest {
        // Arrange
        val user = User(1, "Alice", "alice@example.com")

        // Act
        userDao.insert(user)
        val retrieved = userDao.getById(1)

        // Assert
        assertEquals(user, retrieved)
    }

    @Test
    fun deleteUser() = runTest {
        // Arrange
        val user = User(1, "Alice", "alice@example.com")
        userDao.insert(user)

        // Act
        userDao.delete(user)
        val retrieved = userDao.getById(1)

        // Assert
        assertNull(retrieved)
    }

    @Test
    fun observeUsers_emitsOnChange() = runTest {
        userDao.observeAll().test {
            // Initial state
            assertEquals(emptyList<User>(), awaitItem())

            // Insert
            userDao.insert(User(1, "Alice", "alice@example.com"))
            assertEquals(1, awaitItem().size)

            // Insert another
            userDao.insert(User(2, "Bob", "bob@example.com"))
            assertEquals(2, awaitItem().size)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### UI тесты с Espresso

```kotlin
// androidTest/
@RunWith(AndroidJUnit4::class)
@HiltAndroidTest
class UserListScreenTest {

    @get:Rule
    var hiltRule = HiltAndroidRule(this)

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun displayUserList() {
        // Проверяем что список отображается
        onView(withId(R.id.userRecyclerView))
            .check(matches(isDisplayed()))
    }

    @Test
    fun clickOnUser_navigatesToDetail() {
        // Кликаем на первый элемент
        onView(withId(R.id.userRecyclerView))
            .perform(RecyclerViewActions.actionOnItemAtPosition<UserViewHolder>(0, click()))

        // Проверяем что перешли на Detail экран
        onView(withId(R.id.detailTitle))
            .check(matches(isDisplayed()))
    }

    @Test
    fun searchUsers_filtersResults() {
        // Вводим поисковый запрос
        onView(withId(R.id.searchEditText))
            .perform(typeText("Alice"), closeSoftKeyboard())

        // Проверяем что отфильтровано
        onView(withText("Alice"))
            .check(matches(isDisplayed()))

        onView(withText("Bob"))
            .check(doesNotExist())
    }
}
```

### UI тесты с Compose

```kotlin
@RunWith(AndroidJUnit4::class)
class UserListComposeTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun userList_displaysUsers() {
        // Arrange
        val users = listOf(User(1, "Alice"), User(2, "Bob"))

        // Act
        composeTestRule.setContent {
            UserListScreen(users = users)
        }

        // Assert
        composeTestRule.onNodeWithText("Alice").assertIsDisplayed()
        composeTestRule.onNodeWithText("Bob").assertIsDisplayed()
    }

    @Test
    fun userList_clickCallsCallback() {
        // Arrange
        var clickedUser: User? = null
        val users = listOf(User(1, "Alice"))

        composeTestRule.setContent {
            UserListScreen(
                users = users,
                onUserClick = { clickedUser = it }
            )
        }

        // Act
        composeTestRule.onNodeWithText("Alice").performClick()

        // Assert
        assertEquals(User(1, "Alice"), clickedUser)
    }

    @Test
    fun loadingState_showsProgressIndicator() {
        composeTestRule.setContent {
            UserListScreen(isLoading = true, users = emptyList())
        }

        composeTestRule.onNodeWithTag("loading_indicator").assertIsDisplayed()
    }
}
```

---

## Тестовая пирамида

```
┌─────────────────────────────────────────────────────────────────┐
│                   ТЕСТОВАЯ ПИРАМИДА                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                        /\                                        │
│                       /  \       UI Tests                       │
│                      / UI \      ~10% тестов                    │
│                     /      \     Медленные, нестабильные        │
│                    /────────\                                    │
│                   /          \                                   │
│                  / Integration\  Integration Tests              │
│                 /              \ ~20% тестов                    │
│                /────────────────\                                │
│               /                  \                               │
│              /      Unit          \ Unit Tests                  │
│             /                      \ ~70% тестов                │
│            /________________________\ Быстрые, стабильные       │
│                                                                 │
│  Unit: ViewModel, Repository, UseCase, Utils                    │
│  Integration: Room DAO, Repository + Cache                      │
│  UI: Критические user flows                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Когда какой тип теста

### Decision Matrix

| Сценарий | Тип теста | Почему | Пример |
|----------|-----------|--------|--------|
| **Unit Tests** |
| Изолированная логика | Unit | Быстро, нет зависимостей | Валидация email, расчеты |
| ViewModel бизнес-логика | Unit | Проверка состояний | `loadUsers()` обновляет state |
| UseCase / Domain layer | Unit | Чистая логика без Android | `GetUserByIdUseCase` |
| Utils / Extensions | Unit | Детерминированные функции | `formatDate()`, `parseJson()` |
| Repository логика | Unit | С mock API/DB | Кэширование, error handling |
| **Integration Tests** |
| Room DAO | Integration | Нужна реальная база | SQL запросы, миграции |
| Repository + Cache | Integration | Взаимодействие слоёв | Fallback на кэш при ошибке API |
| Несколько компонентов | Integration | Реальные зависимости | `UserRepository + UserDao` |
| SharedPreferences | Integration | Android Framework API | Сохранение настроек |
| **UI Tests (Espresso)** |
| Критический user flow | UI | End-to-end проверка | Логин → Список → Детали |
| Навигация между экранами | UI | Реальная навигация | Bottom nav, back stack |
| Взаимодействие с UI | UI | Клики, свайпы, ввод текста | Форма регистрации |
| Permissions, system dialogs | UI | Системные компоненты | Запрос камеры |
| **End-to-End Tests** |
| Критический бизнес-процесс | E2E | Вся система + backend | Оформление заказа |
| Multi-module flows | E2E | Интеграция модулей | Payment → Order → Notification |

### Правила выбора

```kotlin
// ❌ НЕ пишем UI тест для логики
@Test
fun checkEmailValidation() {  // Должен быть Unit test
    onView(withId(R.id.email)).perform(typeText("invalid"))
    onView(withId(R.id.error)).check(matches(withText("Invalid email")))
}

// ✅ Unit test для логики
@Test
fun `validateEmail returns false for invalid email`() {
    assertFalse(EmailValidator.isValid("invalid"))
}

// ✅ UI test для критического flow
@Test
fun `user can complete registration flow`() {
    onView(withId(R.id.email)).perform(typeText("test@example.com"))
    onView(withId(R.id.password)).perform(typeText("password123"))
    onView(withId(R.id.register)).perform(click())
    onView(withText("Welcome")).check(matches(isDisplayed()))
}
```

### Аннотации размера тестов

```kotlin
// @SmallTest: < 200ms, JVM, без I/O
@SmallTest
@Test
fun `validateEmail returns false for empty string`() { }

// @MediumTest: < 1s, может быть I/O (DB, file)
@MediumTest
@Test
fun `userDao inserts and retrieves user`() { }

// @LargeTest: > 1s, UI, сеть, эмулятор
@LargeTest
@Test
fun `complete registration flow`() { }
```

**Когда использовать:**
- `@SmallTest`: Unit тесты (70% coverage goal)
- `@MediumTest`: Integration тесты (20% coverage goal)
- `@LargeTest`: UI/E2E тесты (10% coverage goal)

**Зачем нужны:**
- CI может запускать только `@SmallTest` на каждый commit (быстрая обратная связь)
- `@MediumTest` и `@LargeTest` — на pre-merge или nightly builds
- Помогает оптимизировать время выполнения тестов

---

## Лучшие практики

### Naming Convention

```kotlin
// Формат: method_condition_expectedResult
@Test
fun `loadUsers returns empty list when no users exist`() { }

@Test
fun `deleteUser shows error when network fails`() { }

@Test
fun `search filters results by name`() { }
```

### Arrange-Act-Assert (AAA)

```kotlin
@Test
fun `example of AAA pattern`() = runTest {
    // Arrange — подготовка
    val mockRepo = mockk<UserRepository>()
    coEvery { mockRepo.getUsers() } returns Result.success(testUsers)
    val viewModel = UserViewModel(mockRepo)

    // Act — действие
    viewModel.loadUsers()

    // Assert — проверка
    assertEquals(testUsers, viewModel.users.value)
}
```

### Fake vs Mock

```kotlin
// Fake — упрощённая рабочая реализация
class FakeUserRepository : UserRepository {
    private val users = mutableListOf<User>()

    override suspend fun getUsers() = Result.success(users.toList())

    override suspend fun addUser(user: User) {
        users.add(user)
    }
}

// Mock — запрограммированные ответы
val mockRepo = mockk<UserRepository> {
    coEvery { getUsers() } returns Result.success(listOf(User(1, "Test")))
}

// Когда что использовать:
// Fake: сложные сценарии, много взаимодействий
// Mock: простые тесты, проверка вызовов
```

---

## Чеклист

```
□ Unit тесты для ViewModel, Repository, UseCase
□ Instrumented тесты для Room DAO
□ UI тесты для критических user flows
□ Все зависимости инжектируются (testable)
□ Используем TestDispatcher для coroutines
□ Используем Turbine для Flow тестов
□ AAA pattern в каждом тесте
□ Понятные имена тестов
□ CI запускает тесты на каждый PR
□ Аннотации @SmallTest/@MediumTest/@LargeTest
□ Соблюдение тестовой пирамиды (70/20/10)
```

---

## Связь с другими темами

### [[android-architecture-patterns]]
Тестируемость кода напрямую зависит от архитектуры. MVVM и Clean Architecture обеспечивают разделение ответственности, позволяя тестировать ViewModel, UseCase и Repository изолированно. Без правильной архитектуры unit-тесты превращаются в integration-тесты с множеством зависимостей. Изучите архитектурные паттерны до погружения в тестирование — это объяснит, почему код структурируется определённым образом.

### [[android-dependency-injection]]
DI (Hilt, Koin, Dagger) — фундамент тестируемости: позволяет подменять реальные зависимости на mock/fake/stub в тестах. Hilt предоставляет @TestInstallIn для замены модулей, @UninstallModules для удаления production модулей. Без DI подмена зависимостей требует рефакторинга конструкторов и ручного управления графом объектов. Понимание DI критично для написания изолированных unit-тестов.

### [[android-overview]]
Карта Android раздела показывает, где тестирование вписывается в общую экосистему. Тестирование затрагивает все слои: UI (Espresso, Compose Testing), логику (JUnit, MockK), данные (Room in-memory DB), сеть (MockWebServer). Понимание архитектуры платформы помогает выбрать правильный тип теста для каждого компонента.

### [[kotlin-coroutines]]
Тестирование suspend-функций и Flow требует специальных инструментов: TestDispatcher для контроля времени, runTest для запуска корутин в тестах, Turbine для тестирования Flow emissions. Без понимания корутин невозможно написать детерминированные тесты для асинхронного кода. Рекомендуется изучить корутины перед тестированием асинхронной логики.

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "100% code coverage = качество" | Coverage показывает что код запускался, не что он правильный. Тест без assertions = 100% coverage, 0% value. Качество assertions важнее количества |
| "Unit tests = медленные" | Unit tests без Android dependencies = миллисекунды. Медленность от Robolectric/Instrumented setup. Proper isolation = скорость |
| "Robolectric тестирует реальное поведение" | Robolectric эмулирует Android SDK, не реальное устройство. Для UI rendering, hardware features нужны device tests. Знай ограничения |
| "Mockito/MockK для всего" | Mocks проверяют взаимодействия, не поведение. Fakes = рабочие реализации, лучше для тестирования логики. Mocks для verification |
| "Flaky tests неизбежны" | Flakiness = симптом. Причины: race conditions, shared state, animation timing. Правильная изоляция устраняет flakiness |
| "UI tests покрывают всё" | UI tests медленные, flaky, хрупкие. Тестовая пирамида: 70% unit, 20% integration, 10% UI. UI tests для критических flows |
| "TDD не работает для Android" | TDD работает отлично для ViewModel, UseCase, Repository. UI layer сложнее, но Compose делает проще. Начни с domain layer |
| "Instrumented tests только на CI" | Instrumented tests локально важны для быстрого feedback. Emulator в Android Studio быстрый. CI для matrix testing |
| "Тесты замедляют разработку" | Краткосрочно да, долгосрочно нет. Регрессии без тестов стоят дороже. ROI положительный после нескольких месяцев |
| "Compose UI тесты = Espresso" | Compose имеет свой testing API: ComposeTestRule, onNode(), performClick(). Espresso для View-based. Не смешивать без необходимости |

---

## CS-фундамент

| CS-концепция | Как применяется в Testing |
|--------------|---------------------------|
| **Test Pyramid** | Unit (fast, many) → Integration (medium) → E2E (slow, few). Инверсия пирамиды = проблемы с maintenance |
| **Test Doubles** | Dummy, Stub, Fake, Mock, Spy. Каждый для своей цели. Fake для state verification, Mock для behavior verification |
| **Dependency Injection** | Enables testability. Подмена dependencies на test doubles. Hilt @TestInstallIn для test modules |
| **Isolation** | Каждый тест независим. No shared mutable state. Fresh setup для каждого теста. Parallel execution safe |
| **AAA Pattern** | Arrange (setup) → Act (execute) → Assert (verify). Чёткая структура теста. Читаемость и maintainability |
| **Property-Based Testing** | Генерация случайных inputs. Проверка invariants. Находит edge cases автоматически. Kotest property testing |
| **Contract Testing** | API контракты между модулями. Consumer-driven contracts. Обнаружение breaking changes |
| **Flakiness Detection** | Statistical analysis test results. Retry + tracking failure rate. Quarantine flaky tests |
| **Test Coverage** | Line, branch, mutation coverage. Mutation testing = inject bugs, verify tests catch. Качество > количество |
| **Continuous Testing** | Tests на каждый commit. Fast feedback loop. CI integration. Shift-left testing |

---

## Источники

- [Test Apps on Android - Android Developers](https://developer.android.com/training/testing) — официальная документация
- [Test Your ViewModel - Android Developers](https://developer.android.com/topic/libraries/architecture/viewmodel/viewmodel-testing) — тестирование ViewModel
- [Testing Kotlin Coroutines - Android Developers](https://developer.android.com/kotlin/coroutines/test) — тестирование coroutines
- [Espresso - Android Developers](https://developer.android.com/training/testing/espresso) — UI тесты

## Источники и дальнейшее чтение

- **Phillips B. et al. (2022). Android Programming: The Big Nerd Ranch Guide.** — Практическое введение в тестирование Android-приложений: unit-тесты с JUnit, UI-тесты с Espresso, тестирование ViewModel и Repository. Хороший старт для построения тестовой пирамиды.
- **Bloch J. (2018). Effective Java.** — Принципы проектирования тестируемого кода: immutability, dependency injection, separation of concerns. Хотя книга на Java, паттерны универсальны и формируют мышление для написания кода, который легко покрыть тестами.
- **Moskala M. (2022). Kotlin Coroutines Deep Dive.** — Глава о тестировании корутин: TestDispatcher, runTest, Turbine для Flow. Незаменимый ресурс для тестирования асинхронного кода в Android.

---

---

## Проверь себя

> [!question]- Почему пирамида тестирования (unit > integration > UI) важна для Android?
> Unit тесты: быстрые (~ms), надежные, дешевые. UI тесты: медленные (~sec), flaky, дорогие (эмулятор). Оптимальное соотношение: 70% unit, 20% integration, 10% UI. Перевернутая пирамида (много UI тестов) = медленный CI, flaky builds, дорогая поддержка. Unit тесты ловят 80% багов за 20% стоимости.

> [!question]- Сценарий: UI тест проходит локально, но падает в CI. Что проверить?
> 1) Timing: добавить IdlingResource для async операций. 2) Анимации: отключить в developer options (window/transition/animator duration = 0). 3) Locale/timezone: CI может иметь другие settings. 4) Screen size: CI эмулятор может иметь другой размер. 5) Network: mock API в UI тестах. 6) Flaky detection: retry + report flaky rate.


---

## Ключевые карточки

Какие типы тестов в Android?
?
Unit (JVM, без Android): JUnit, MockK, Turbine. Integration (partial Android): Robolectric. Instrumented (device/emulator): Espresso (UI), UIAutomator (system UI). Screenshot: Paparazzi (JVM), shot. Для Compose: ComposeTestRule.

Что такое MockK?
?
Mocking library для Kotlin. every { mock.getUser() } returns user. coEvery для suspend. verify { mock.save(any()) }. Relaxed mocks: mockk(relaxed = true). Поддерживает coroutines, extension functions. Альтернатива Mockito для Kotlin.

Что такое Turbine?
?
Testing library для Kotlin Flow. turbineScope { flow.test { assertEquals(expected, awaitItem()); awaitComplete() } }. Проверяет emissions, errors, completion. Timeout для async operations. Стандарт для тестирования Flow.

Что такое Robolectric?
?
Android framework на JVM: тесты с Context, SharedPreferences, SQLite без эмулятора. Быстрее instrumented тестов (10-100x). Ограничения: не все API поддержаны, визуальные тесты невозможны. Хорош для integration тестов.

Как тестировать Compose UI?
?
composeTestRule.setContent { MyScreen() }. onNodeWithText('Login').performClick(). onNodeWithTag('list').assertIsDisplayed(). Semantics-based: нет привязки к implementation. assertCountEquals() для списков. printToLog() для debug.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-performance-profiling]] | Профилирование производительности |
| Углубиться | [[android-ci-cd]] | Тестирование как часть CI/CD |
| Смежная тема | [[ios-testing]] | Тестирование в iOS: XCTest и UI Testing |
| Обзор | [[android-overview]] | Вернуться к карте раздела |


*Проверено: 2026-01-09 | На основе официальной документации Android*

