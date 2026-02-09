---
title: "KMP Integration Testing"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, testing, integration, ktor, sqldelight]
cs-foundations:
  - "[[integration-testing-theory]]"
  - "[[test-doubles-patterns]]"
  - "[[database-testing-strategies]]"
  - "[[http-mocking-patterns]]"
  - "[[test-isolation-principles]]"
related: [[kmp-testing-strategies]], [[kmp-unit-testing]], [[kmp-ktor-networking]], [[kmp-sqldelight-database]]
---

# KMP Integration Testing

> **TL;DR:** Integration тесты в KMP проверяют взаимодействие между слоями: API (Ktor MockEngine), Database (SQLDelight in-memory drivers), Repository + DataSource. Используй in-memory SQLite драйверы для каждой платформы, MockEngine для сетевых запросов. Fakes предпочтительнее mocks из-за ограничений Native. Тесты в commonTest + platform-specific драйверы через expect/actual.

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Unit Testing в KMP | Основа для integration тестов | [[kmp-unit-testing]] |
| Ktor Client | Понимать что тестируем | [[kmp-ktor-networking]] |
| SQLDelight | Понимать что тестируем | [[kmp-sqldelight-database]] |
| kotlin.test | Базовые assertions | kotlin.test docs |
| runTest | Тестирование корутин | kotlinx-coroutines-test |
| Integration Testing Theory | Границы интеграции | [[integration-testing-theory]] |
| Test Doubles | Fake vs Mock vs Stub | [[test-doubles-patterns]] |
| Database Testing | In-memory strategies | [[database-testing-strategies]] |

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| Integration Test | Тест взаимодействия компонентов | Проверка что руль, педали и двигатель работают вместе |
| MockEngine | Fake HTTP engine для Ktor | Симулятор полетов вместо реального самолета |
| In-Memory Database | База данных в RAM | Доска для заметок которую стирают после каждой встречи |
| Test Double | Замена реального компонента | Дублер актера для трюков |
| Fake | Рабочая упрощенная реализация | Тренировочный dummy вместо реального противника |
| Stub | Возвращает захардкоженные данные | Автоответчик с записанным сообщением |

---

## Почему интеграционные тесты отличаются от unit?

### CS-фундамент: Contract Testing и Seams

**Integration Test проверяет контракт между компонентами:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Unit Test                                                       │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│   ┌─────────────┐                                               │
│   │   Class A   │  ← Test verifies A's internal logic           │
│   └─────────────┘                                               │
│         │                                                       │
│         ▼                                                       │
│   [ Fake/Stub ]  ← Dependencies mocked                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Integration Test                                                │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│   ┌─────────────┐    contract    ┌─────────────┐               │
│   │   Class A   │ ◄────────────► │   Class B   │               │
│   └─────────────┘                └─────────────┘               │
│                                        │                        │
│                    Test verifies ──────┘                        │
│                    interaction contract                         │
└─────────────────────────────────────────────────────────────────┘
```

**Seams (швы)** — точки в коде, где можно заменить реальную реализацию на тестовую:

| Seam Type | KMP Example | When to Use |
|-----------|-------------|-------------|
| **Constructor** | `Repository(ApiClient, Database)` | Most common, DI-friendly |
| **Interface** | `interface ApiClient` | Enables Fake implementation |
| **Engine** | `HttpClient(MockEngine)` | Ktor-specific |
| **Driver** | `Database(SqlDriver)` | SQLDelight-specific |

### Почему MockEngine, а не реальный сервер?

```
┌─────────────────────────────────────────────────────────────────┐
│ Real Server Testing                                             │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│   Test ──► HttpClient ──► Internet ──► Server ──► Database      │
│                                                                 │
│   Problems:                                                     │
│   • Slow (network latency)                                      │
│   • Flaky (server down, network issues)                         │
│   • Non-deterministic (data changes)                            │
│   • Can't test error scenarios easily                           │
│   • CI requires infrastructure                                  │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ MockEngine Testing                                              │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│   Test ──► HttpClient ──► MockEngine (in-process)               │
│                                                                 │
│   Benefits:                                                     │
│   • Fast (no network)                                           │
│   • Deterministic (controlled responses)                        │
│   • Error scenarios easy (`HttpStatusCode.InternalServerError`) │
│   • Verifiable (`requestHistory`)                               │
│   • Works offline                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Почему In-Memory Database?

**Принцип: каждый тест должен быть изолирован**

```
┌─────────────────────────────────────────────────────────────────┐
│ Shared File Database (Anti-pattern)                             │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│   Test1: INSERT user → Test2: SELECT users → Gets Test1 data!   │
│                                                                 │
│   Problems:                                                     │
│   • Tests depend on execution order                             │
│   • Parallel tests corrupt data                                 │
│   • Cleanup is error-prone                                      │
│   • State leaks between tests                                   │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ In-Memory Per-Test Database (Best Practice)                     │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│   @BeforeTest: driver = createInMemorySqlDriver()               │
│   Test1: [isolated DB] → Test2: [isolated DB]                   │
│   @AfterTest: driver.close()                                    │
│                                                                 │
│   Benefits:                                                     │
│   • Complete isolation                                          │
│   • Fast (RAM > disk)                                           │
│   • Automatic cleanup (GC)                                      │
│   • Parallel-safe                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Test Doubles Taxonomy (Gerard Meszaros)

```
┌─────────────────────────────────────────────────────────────────┐
│ TEST DOUBLES                                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   DUMMY        │ Passed but never used                          │
│   ────────────────────────────────────────────────────────────  │
│   fun save(user: User, logger: Logger)                          │
│   // logger is dummy if never called                            │
│                                                                 │
│   STUB         │ Returns canned answers                         │
│   ────────────────────────────────────────────────────────────  │
│   every { repo.getUser("1") } returns User("John")              │
│   // Always returns same thing                                  │
│                                                                 │
│   FAKE         │ Working implementation with shortcuts          │
│   ────────────────────────────────────────────────────────────  │
│   class FakeRepository { private val map = mutableMapOf() }     │
│   // Real logic, but in-memory instead of DB                    │
│                                                                 │
│   MOCK         │ Pre-programmed with expectations               │
│   ────────────────────────────────────────────────────────────  │
│   verify { repo.save(user) }                                    │
│   // Verifies interaction happened                              │
│                                                                 │
│   SPY          │ Real object with recording                     │
│   ────────────────────────────────────────────────────────────  │
│   val spy = spyk(RealService())                                 │
│   // Uses real impl but tracks calls                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**В KMP рекомендуется FAKE:**
- Работает на всех платформах (нет reflection)
- Простой и понятный код
- Легко отлаживать
- Документирует ожидаемое поведение

### Integration Test Boundaries в KMP

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                     REAL (production code)                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                         │   │
│   │   ViewModel → UseCase → Repository → DataSources        │   │
│   │                                                         │   │
│   └────────────────────┬────────────────────────────────────┘   │
│                        │                                        │
│              ┌─────────┴──────────┐                            │
│              ▼                    ▼                            │
│   ┌──────────────────┐  ┌──────────────────┐                   │
│   │    MockEngine    │  │   In-Memory DB   │                   │
│   │  (controlled)    │  │   (isolated)     │                   │
│   └──────────────────┘  └──────────────────┘                   │
│                                                                 │
│                     TEST DOUBLES (seams)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Coverage target для Integration тестов: 60-70%**

---

## Уровни интеграции в KMP

```
┌─────────────────────────────────────────────────────────────┐
│                    Integration Test Scope                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  ViewModel  │───▶│  UseCase    │───▶│ Repository  │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                              │              │
│                          ┌───────────────────┼──────────┐  │
│                          ▼                   ▼          │  │
│                   ┌─────────────┐    ┌─────────────┐   │  │
│                   │ RemoteSource│    │ LocalSource │   │  │
│                   │ (Ktor Mock) │    │ (SQLDelight)│   │  │
│                   └─────────────┘    └─────────────┘   │  │
│                          │                   │          │  │
│                          ▼                   ▼          │  │
│                   ┌─────────────┐    ┌─────────────┐   │  │
│                   │ MockEngine  │    │ In-Memory DB│   │  │
│                   └─────────────┘    └─────────────┘   │  │
│                                                         │  │
└─────────────────────────────────────────────────────────────┘
```

## Setup: build.gradle.kts

```kotlin
// shared/build.gradle.kts
kotlin {
    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation("io.ktor:ktor-client-core:3.1.0")
                implementation("app.cash.sqldelight:runtime:2.2.1")
            }
        }

        val commonTest by getting {
            dependencies {
                implementation(kotlin("test"))
                implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.10.2")

                // Ktor MockEngine
                implementation("io.ktor:ktor-client-mock:3.1.0")

                // Assertions
                implementation("io.kotest:kotest-assertions-core:5.9.1")

                // Flow testing
                implementation("app.cash.turbine:turbine:1.2.0")
            }
        }

        val androidUnitTest by getting {
            dependencies {
                // In-memory SQLite для Android
                implementation("app.cash.sqldelight:sqlite-driver:2.2.1")
            }
        }

        val iosTest by getting {
            dependencies {
                // Native driver включен по умолчанию
            }
        }

        // Для JVM/Desktop
        val jvmTest by getting {
            dependencies {
                implementation("app.cash.sqldelight:sqlite-driver:2.2.1")
            }
        }
    }
}
```

## SQLDelight: In-Memory Database

### expect/actual для драйверов

```kotlin
// commonTest/kotlin/TestDatabaseDriver.kt
expect fun createInMemorySqlDriver(): SqlDriver

// androidUnitTest/kotlin/TestDatabaseDriver.android.kt
actual fun createInMemorySqlDriver(): SqlDriver {
    val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
    AppDatabase.Schema.create(driver)
    return driver
}

// iosTest/kotlin/TestDatabaseDriver.ios.kt
private var testDbIndex = 0

actual fun createInMemorySqlDriver(): SqlDriver {
    testDbIndex++
    return NativeSqliteDriver(
        DatabaseConfiguration(
            name = "test-$testDbIndex.db",
            version = AppDatabase.Schema.version.toInt(),
            inMemory = true,
            create = { connection ->
                wrapConnection(connection) { AppDatabase.Schema.create(it) }
            },
            upgrade = { connection, oldVersion, newVersion ->
                wrapConnection(connection) {
                    AppDatabase.Schema.migrate(it, oldVersion.toLong(), newVersion.toLong())
                }
            }
        )
    )
}

// jvmTest/kotlin/TestDatabaseDriver.jvm.kt
actual fun createInMemorySqlDriver(): SqlDriver {
    val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
    AppDatabase.Schema.create(driver)
    return driver
}
```

### Тестирование Database Layer

```kotlin
// commonTest/kotlin/database/UserDatabaseTest.kt
class UserDatabaseTest {
    private lateinit var driver: SqlDriver
    private lateinit var database: AppDatabase
    private lateinit var queries: UserQueries

    @BeforeTest
    fun setup() {
        driver = createInMemorySqlDriver()
        database = AppDatabase(driver)
        queries = database.userQueries
    }

    @AfterTest
    fun tearDown() {
        driver.close()
    }

    @Test
    fun `insert and select user`() {
        // Given
        val user = User(id = 1, name = "John", email = "john@test.com")

        // When
        queries.insertUser(user.id, user.name, user.email)
        val result = queries.selectById(1).executeAsOne()

        // Then
        result.name shouldBe "John"
        result.email shouldBe "john@test.com"
    }

    @Test
    fun `selectAll returns all users`() = runTest {
        // Given
        queries.insertUser(1, "Alice", "alice@test.com")
        queries.insertUser(2, "Bob", "bob@test.com")

        // When
        val users = queries.selectAll().executeAsList()

        // Then
        users shouldHaveSize 2
        users.map { it.name } shouldContainExactlyInAnyOrder listOf("Alice", "Bob")
    }

    @Test
    fun `update user modifies existing record`() {
        // Given
        queries.insertUser(1, "John", "old@test.com")

        // When
        queries.updateEmail(email = "new@test.com", id = 1)
        val result = queries.selectById(1).executeAsOne()

        // Then
        result.email shouldBe "new@test.com"
    }

    @Test
    fun `delete removes user`() {
        // Given
        queries.insertUser(1, "John", "john@test.com")

        // When
        queries.deleteById(1)
        val result = queries.selectById(1).executeAsOneOrNull()

        // Then
        result.shouldBeNull()
    }
}
```

### Тестирование Flow из SQLDelight

```kotlin
// commonTest/kotlin/database/UserFlowTest.kt
class UserFlowTest {
    private lateinit var driver: SqlDriver
    private lateinit var queries: UserQueries

    @BeforeTest
    fun setup() {
        driver = createInMemorySqlDriver()
        queries = AppDatabase(driver).userQueries
    }

    @AfterTest
    fun tearDown() {
        driver.close()
    }

    @Test
    fun `selectAllAsFlow emits on changes`() = runTest {
        queries.selectAllAsFlow()
            .asFlow()
            .mapToList(Dispatchers.Default)
            .test {
                // Initially empty
                awaitItem() shouldHaveSize 0

                // Insert user
                queries.insertUser(1, "Alice", "alice@test.com")
                awaitItem() shouldHaveSize 1

                // Insert another
                queries.insertUser(2, "Bob", "bob@test.com")
                val users = awaitItem()
                users shouldHaveSize 2

                cancelAndIgnoreRemainingEvents()
            }
    }
}
```

## Ktor MockEngine

### Базовый Setup

```kotlin
// commonTest/kotlin/network/MockEngineFactory.kt
object MockEngineFactory {

    fun createSuccessEngine(
        responseBody: String,
        statusCode: HttpStatusCode = HttpStatusCode.OK,
        contentType: String = "application/json"
    ): MockEngine {
        return MockEngine { request ->
            respond(
                content = ByteReadChannel(responseBody),
                status = statusCode,
                headers = headersOf(
                    HttpHeaders.ContentType to listOf(contentType)
                )
            )
        }
    }

    fun createErrorEngine(
        statusCode: HttpStatusCode,
        errorBody: String = """{"error": "Something went wrong"}"""
    ): MockEngine {
        return MockEngine { request ->
            respond(
                content = ByteReadChannel(errorBody),
                status = statusCode,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }
    }

    fun createRoutingEngine(
        routes: Map<String, MockResponse>
    ): MockEngine {
        return MockEngine { request ->
            val path = request.url.encodedPath
            val mockResponse = routes[path] ?: MockResponse(
                body = """{"error": "Not found: $path"}""",
                status = HttpStatusCode.NotFound
            )

            respond(
                content = ByteReadChannel(mockResponse.body),
                status = mockResponse.status,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }
    }
}

data class MockResponse(
    val body: String,
    val status: HttpStatusCode = HttpStatusCode.OK
)
```

### Тестирование API Client

```kotlin
// commonTest/kotlin/network/UserApiClientTest.kt
class UserApiClientTest {

    @Test
    fun `getUsers returns list on success`() = runTest {
        // Given
        val mockEngine = MockEngineFactory.createSuccessEngine(
            responseBody = """
                [
                    {"id": 1, "name": "Alice", "email": "alice@test.com"},
                    {"id": 2, "name": "Bob", "email": "bob@test.com"}
                ]
            """.trimIndent()
        )

        val client = HttpClient(mockEngine) {
            install(ContentNegotiation) {
                json(Json { ignoreUnknownKeys = true })
            }
        }

        val apiClient = UserApiClient(client)

        // When
        val result = apiClient.getUsers()

        // Then
        result.shouldBeSuccess()
        result.getOrThrow() shouldHaveSize 2
        result.getOrThrow().first().name shouldBe "Alice"
    }

    @Test
    fun `getUsers returns error on failure`() = runTest {
        // Given
        val mockEngine = MockEngineFactory.createErrorEngine(
            statusCode = HttpStatusCode.InternalServerError
        )

        val client = HttpClient(mockEngine) {
            install(ContentNegotiation) {
                json()
            }
        }

        val apiClient = UserApiClient(client)

        // When
        val result = apiClient.getUsers()

        // Then
        result.shouldBeFailure()
    }

    @Test
    fun `request contains correct headers`() = runTest {
        // Given
        var capturedRequest: HttpRequestData? = null

        val mockEngine = MockEngine { request ->
            capturedRequest = request
            respond(
                content = ByteReadChannel("[]"),
                status = HttpStatusCode.OK,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }

        val client = HttpClient(mockEngine) {
            install(ContentNegotiation) { json() }
            defaultRequest {
                header("Authorization", "Bearer token123")
            }
        }

        val apiClient = UserApiClient(client)

        // When
        apiClient.getUsers()

        // Then
        capturedRequest.shouldNotBeNull()
        capturedRequest!!.headers["Authorization"] shouldBe "Bearer token123"
    }
}
```

### Dynamic Routing Mock

```kotlin
// commonTest/kotlin/network/DynamicMockEngineTest.kt
class DynamicMockEngineTest {

    @Test
    fun `routes to correct responses based on path`() = runTest {
        // Given
        val mockEngine = MockEngine { request ->
            val path = request.url.encodedPath
            val query = request.url.parameters["id"]

            when {
                path == "/users" && query == null -> respond(
                    content = ByteReadChannel("""[{"id": 1, "name": "All Users"}]"""),
                    status = HttpStatusCode.OK,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
                path == "/users" && query == "1" -> respond(
                    content = ByteReadChannel("""{"id": 1, "name": "User One"}"""),
                    status = HttpStatusCode.OK,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
                path == "/posts" -> respond(
                    content = ByteReadChannel("""[{"id": 1, "title": "First Post"}]"""),
                    status = HttpStatusCode.OK,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
                else -> respond(
                    content = ByteReadChannel("""{"error": "Not found"}"""),
                    status = HttpStatusCode.NotFound,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
            }
        }

        val client = HttpClient(mockEngine) {
            install(ContentNegotiation) { json() }
        }

        // When/Then - All users
        val allUsers: List<User> = client.get("/users").body()
        allUsers shouldHaveSize 1
        allUsers.first().name shouldBe "All Users"

        // When/Then - Single user
        val user: User = client.get("/users") {
            parameter("id", "1")
        }.body()
        user.name shouldBe "User One"
    }
}
```

### Request History Verification

```kotlin
// commonTest/kotlin/network/RequestVerificationTest.kt
class RequestVerificationTest {

    @Test
    fun `verifies request was made with correct parameters`() = runTest {
        // Given
        val mockEngine = MockEngine { request ->
            respond(
                content = ByteReadChannel("{}"),
                status = HttpStatusCode.OK,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }

        val client = HttpClient(mockEngine)

        // When
        client.post("/users") {
            contentType(ContentType.Application.Json)
            setBody("""{"name": "Alice", "email": "alice@test.com"}""")
        }

        // Then
        mockEngine.requestHistory shouldHaveSize 1

        val request = mockEngine.requestHistory.first()
        request.url.encodedPath shouldBe "/users"
        request.method shouldBe HttpMethod.Post
        request.headers[HttpHeaders.ContentType] shouldContain "application/json"
    }

    @Test
    fun `verifies no requests made on validation failure`() = runTest {
        // Given
        val mockEngine = MockEngine { request ->
            respond(content = ByteReadChannel("{}"), status = HttpStatusCode.OK)
        }

        val client = HttpClient(mockEngine)
        val service = UserService(client)

        // When - invalid email should not make request
        val result = service.createUser(name = "", email = "invalid")

        // Then
        result.shouldBeFailure()
        mockEngine.requestHistory.shouldBeEmpty()
    }
}
```

## Repository Integration Tests

### Full Stack Repository Test

```kotlin
// commonTest/kotlin/repository/UserRepositoryIntegrationTest.kt
class UserRepositoryIntegrationTest {
    private lateinit var driver: SqlDriver
    private lateinit var database: AppDatabase
    private lateinit var mockEngine: MockEngine
    private lateinit var httpClient: HttpClient
    private lateinit var repository: UserRepository

    @BeforeTest
    fun setup() {
        // Database setup
        driver = createInMemorySqlDriver()
        database = AppDatabase(driver)

        // Network setup with default success response
        mockEngine = MockEngine { request ->
            respond(
                content = ByteReadChannel("""
                    [
                        {"id": 1, "name": "Remote User", "email": "remote@test.com"}
                    ]
                """.trimIndent()),
                status = HttpStatusCode.OK,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }

        httpClient = HttpClient(mockEngine) {
            install(ContentNegotiation) { json() }
        }

        // Repository with real implementations
        val remoteDataSource = UserRemoteDataSource(httpClient)
        val localDataSource = UserLocalDataSource(database.userQueries)

        repository = UserRepositoryImpl(
            remoteDataSource = remoteDataSource,
            localDataSource = localDataSource
        )
    }

    @AfterTest
    fun tearDown() {
        driver.close()
        httpClient.close()
    }

    @Test
    fun `getUsers fetches from network and caches locally`() = runTest {
        // Given - empty database
        database.userQueries.selectAll().executeAsList().shouldBeEmpty()

        // When
        val result = repository.getUsers(forceRefresh = true)

        // Then - returns from network
        result.shouldBeSuccess()
        result.getOrThrow() shouldHaveSize 1
        result.getOrThrow().first().name shouldBe "Remote User"

        // And - cached in database
        val cached = database.userQueries.selectAll().executeAsList()
        cached shouldHaveSize 1
        cached.first().name shouldBe "Remote User"
    }

    @Test
    fun `getUsers returns cached data when network fails`() = runTest {
        // Given - pre-populated cache
        database.userQueries.insertUser(1, "Cached User", "cached@test.com")

        // And - network fails
        mockEngine = MockEngine { request ->
            respond(
                content = ByteReadChannel("""{"error": "Server down"}"""),
                status = HttpStatusCode.InternalServerError
            )
        }

        httpClient = HttpClient(mockEngine) {
            install(ContentNegotiation) { json() }
        }

        val remoteDataSource = UserRemoteDataSource(httpClient)
        val localDataSource = UserLocalDataSource(database.userQueries)
        repository = UserRepositoryImpl(remoteDataSource, localDataSource)

        // When
        val result = repository.getUsers(forceRefresh = false)

        // Then - returns cached data
        result.shouldBeSuccess()
        result.getOrThrow().first().name shouldBe "Cached User"
    }
}
```

### Repository with Flow

```kotlin
// commonTest/kotlin/repository/UserRepositoryFlowTest.kt
class UserRepositoryFlowTest {
    private lateinit var driver: SqlDriver
    private lateinit var database: AppDatabase
    private lateinit var repository: UserRepository

    @BeforeTest
    fun setup() {
        driver = createInMemorySqlDriver()
        database = AppDatabase(driver)

        // Fake remote that we can control
        val fakeRemote = FakeUserRemoteDataSource()
        val localDataSource = UserLocalDataSource(database.userQueries)

        repository = UserRepositoryImpl(fakeRemote, localDataSource)
    }

    @AfterTest
    fun tearDown() {
        driver.close()
    }

    @Test
    fun `observeUsers emits updates when data changes`() = runTest {
        repository.observeUsers().test {
            // Initially empty
            awaitItem().shouldBeEmpty()

            // Simulate sync from remote
            database.userQueries.insertUser(1, "New User", "new@test.com")

            // Should emit updated list
            val updated = awaitItem()
            updated shouldHaveSize 1
            updated.first().name shouldBe "New User"

            // Add another user
            database.userQueries.insertUser(2, "Another User", "another@test.com")
            awaitItem() shouldHaveSize 2

            cancelAndIgnoreRemainingEvents()
        }
    }
}

// Fake implementation for controlled testing
class FakeUserRemoteDataSource : UserRemoteDataSource {
    var usersToReturn: List<User> = emptyList()
    var shouldFail: Boolean = false
    var failureException: Exception = Exception("Network error")

    override suspend fun getUsers(): Result<List<User>> {
        return if (shouldFail) {
            Result.failure(failureException)
        } else {
            Result.success(usersToReturn)
        }
    }
}
```

## Use Case Integration Tests

```kotlin
// commonTest/kotlin/usecase/SyncUsersUseCaseTest.kt
class SyncUsersUseCaseTest {
    private lateinit var driver: SqlDriver
    private lateinit var mockEngine: MockEngine
    private lateinit var useCase: SyncUsersUseCase

    @BeforeTest
    fun setup() {
        driver = createInMemorySqlDriver()
        val database = AppDatabase(driver)

        mockEngine = MockEngine { request ->
            respond(
                content = ByteReadChannel("""
                    [
                        {"id": 1, "name": "User 1", "email": "user1@test.com"},
                        {"id": 2, "name": "User 2", "email": "user2@test.com"}
                    ]
                """.trimIndent()),
                status = HttpStatusCode.OK,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }

        val client = HttpClient(mockEngine) {
            install(ContentNegotiation) { json() }
        }

        val repository = UserRepositoryImpl(
            remoteDataSource = UserRemoteDataSource(client),
            localDataSource = UserLocalDataSource(database.userQueries)
        )

        useCase = SyncUsersUseCase(repository)
    }

    @AfterTest
    fun tearDown() {
        driver.close()
    }

    @Test
    fun `invoke syncs users from remote to local`() = runTest {
        // When
        val result = useCase()

        // Then
        result.shouldBeSuccess()
        result.getOrThrow() shouldBe 2 // synced count

        // Verify network was called
        mockEngine.requestHistory shouldHaveSize 1
    }

    @Test
    fun `invoke handles partial sync on error`() = runTest {
        // Given - first call succeeds, second fails
        var callCount = 0
        mockEngine = MockEngine { request ->
            callCount++
            if (callCount == 1) {
                respond(
                    content = ByteReadChannel("""[{"id": 1, "name": "User 1", "email": "u1@test.com"}]"""),
                    status = HttpStatusCode.OK,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
            } else {
                respond(
                    content = ByteReadChannel("""{"error": "fail"}"""),
                    status = HttpStatusCode.InternalServerError
                )
            }
        }

        // Rebuild with new engine...
        // ... (setup code)

        // Test partial sync behavior
    }
}
```

## Fakes vs Mocks: Recommended Pattern

```kotlin
// commonTest/kotlin/fakes/FakeUserRepository.kt

/**
 * Fake implementation for testing.
 *
 * Why Fakes over Mocks in KMP:
 * 1. MockK doesn't work on Kotlin/Native
 * 2. Fakes are simpler and more predictable
 * 3. No runtime reflection needed
 * 4. Works identically on all platforms
 */
class FakeUserRepository : UserRepository {

    // Control test behavior
    private val users = mutableListOf<User>()
    private val _usersFlow = MutableStateFlow<List<User>>(emptyList())

    var shouldFailOnGet = false
    var shouldFailOnSave = false
    var getCallCount = 0
        private set
    var saveCallCount = 0
        private set

    // Implement interface
    override suspend fun getUsers(forceRefresh: Boolean): Result<List<User>> {
        getCallCount++
        return if (shouldFailOnGet) {
            Result.failure(Exception("Fake failure"))
        } else {
            Result.success(users.toList())
        }
    }

    override suspend fun saveUser(user: User): Result<Unit> {
        saveCallCount++
        return if (shouldFailOnSave) {
            Result.failure(Exception("Fake save failure"))
        } else {
            users.add(user)
            _usersFlow.value = users.toList()
            Result.success(Unit)
        }
    }

    override fun observeUsers(): Flow<List<User>> = _usersFlow.asStateFlow()

    // Test helpers
    fun givenUsers(vararg testUsers: User) {
        users.clear()
        users.addAll(testUsers)
        _usersFlow.value = users.toList()
    }

    fun reset() {
        users.clear()
        _usersFlow.value = emptyList()
        shouldFailOnGet = false
        shouldFailOnSave = false
        getCallCount = 0
        saveCallCount = 0
    }
}
```

### Using Fake in Tests

```kotlin
// commonTest/kotlin/viewmodel/UserListViewModelTest.kt
class UserListViewModelTest {
    private val fakeRepository = FakeUserRepository()
    private lateinit var viewModel: UserListViewModel

    @BeforeTest
    fun setup() {
        fakeRepository.reset()
        viewModel = UserListViewModel(fakeRepository)
    }

    @Test
    fun `loadUsers shows success state`() = runTest {
        // Given
        fakeRepository.givenUsers(
            User(1, "Alice", "alice@test.com"),
            User(2, "Bob", "bob@test.com")
        )

        // When
        viewModel.loadUsers()
        advanceUntilIdle()

        // Then
        viewModel.uiState.value shouldBe UserListUiState.Success(
            users = listOf(
                User(1, "Alice", "alice@test.com"),
                User(2, "Bob", "bob@test.com")
            )
        )
        fakeRepository.getCallCount shouldBe 1
    }

    @Test
    fun `loadUsers shows error state on failure`() = runTest {
        // Given
        fakeRepository.shouldFailOnGet = true

        // When
        viewModel.loadUsers()
        advanceUntilIdle()

        // Then
        viewModel.uiState.value.shouldBeInstanceOf<UserListUiState.Error>()
    }
}
```

## Testcontainers (JVM Only)

Для JVM-таргета можно использовать Testcontainers:

```kotlin
// jvmTest/kotlin/integration/PostgresIntegrationTest.kt
@Testcontainers
class PostgresIntegrationTest {

    companion object {
        @Container
        val postgres = PostgreSQLContainer<Nothing>("postgres:15").apply {
            withDatabaseName("testdb")
            withUsername("test")
            withPassword("test")
        }
    }

    private lateinit var driver: SqlDriver

    @BeforeTest
    fun setup() {
        driver = JdbcSqliteDriver(postgres.jdbcUrl).apply {
            AppDatabase.Schema.create(this)
        }
    }

    @Test
    fun `test with real PostgreSQL`() = runTest {
        val queries = AppDatabase(driver).userQueries

        queries.insertUser(1, "Test User", "test@example.com")

        val user = queries.selectById(1).executeAsOne()
        user.name shouldBe "Test User"
    }
}
```

## CI/CD Integration

### GitHub Actions для Integration Tests

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  push:
    branches: [main]
  pull_request:

jobs:
  integration-tests:
    runs-on: macos-latest  # Required for iOS tests

    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Run Common Integration Tests
        run: ./gradlew :shared:jvmTest

      - name: Run Android Integration Tests
        run: ./gradlew :shared:testDebugUnitTest

      - name: Run iOS Integration Tests
        run: ./gradlew :shared:iosSimulatorArm64Test

      - name: Upload Test Reports
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-reports
          path: |
            **/build/reports/tests/
            **/build/test-results/
```

## Best Practices Checklist

| Practice | Why | Example |
|----------|-----|---------|
| In-memory DB per test | Изоляция, предсказуемость | `createInMemorySqlDriver()` |
| Unique DB names on iOS | Prevent reuse between tests | `"test-$index.db"` |
| Reset fakes in @BeforeTest | Clean state | `fakeRepository.reset()` |
| Use expect/actual for drivers | Platform abstraction | `expect fun createInMemorySqlDriver()` |
| Prefer Fakes over Mocks | KMP compatibility | `FakeUserRepository` |
| Test error paths | Robustness | `shouldFailOnGet = true` |
| Verify request history | Ensure API called | `mockEngine.requestHistory` |
| Close resources in @AfterTest | Prevent leaks | `driver.close()` |
| Use Turbine for Flow | Cleaner assertions | `flow.test { awaitItem() }` |

## Кто использует и реальные примеры

| Компания | Контекст | Паттерн |
|----------|----------|---------|
| Cash App | SQLDelight автор | In-memory testing patterns |
| McDonald's | Payment validation | Shared integration tests |
| Netflix | Data sync | MockEngine + real DB tests |
| Philips | IoT devices | Cross-platform integration |

## Troubleshooting

| Проблема | Причина | Решение |
|----------|---------|---------|
| iOS test reuses DB | Same in-memory name | Use unique index per test |
| JdbcSqliteDriver not found | Missing dependency | Add sqlite-driver to androidUnitTest |
| MockEngine not responding | Wrong path match | Log request.url.encodedPath |
| Flow test timeout | Missing emissions | Use advanceUntilIdle() |
| Test flaky | Shared state | Reset fakes in @BeforeTest |

## Мифы и заблуждения

### Миф 1: "Integration тесты медленные, их нужно меньше"

**Реальность:** С in-memory database и MockEngine integration тесты выполняются за **миллисекунды**. Медленные — только тесты с реальными серверами и эмуляторами. При правильной настройке integration тесты лишь немного медленнее unit тестов.

### Миф 2: "MockEngine тестирует только happy path"

**Реальность:** MockEngine позволяет тестировать **любой HTTP сценарий**: таймауты, 5xx ошибки, невалидный JSON, network errors. `requestHistory` позволяет верифицировать что запросы отправлены правильно.

### Миф 3: "На iOS нужен другой подход к тестированию DB"

**Реальность:** SQLDelight in-memory работает **идентично** на всех платформах. Нужен только platform-specific driver через expect/actual. Тесты в commonTest запускаются на всех платформах без изменений.

### Миф 4: "Fakes — это упрощённые тесты"

**Реальность:** Fakes — это **рекомендуемый подход** в KMP из-за отсутствия reflection на Native. Fakes проще отлаживать, они документируют ожидаемое поведение и работают везде. MockK/Mockito невозможны на Kotlin/Native.

### Миф 5: "Нужен реальный сервер для тестирования API"

**Реальность:** MockEngine покрывает **99% сценариев**. Реальный сервер нужен только для e2e smoke tests. Contract testing через MockEngine быстрее, стабильнее и воспроизводимее.

### Миф 6: "Testcontainers работают в KMP"

**Реальность:** Testcontainers — **только JVM**. Для multiplatform тестирования используйте in-memory драйверы. Testcontainers полезны для jvmTest, но не для commonTest.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Ktor Client Testing](https://ktor.io/docs/client-testing.html) | Official | MockEngine documentation |
| [SQLDelight Testing](https://sqldelight.github.io/sqldelight/) | Official | In-memory drivers |
| [SQLDelight In-Memory Testing](https://akjaw.com/kotlin-multiplatform-testing-sqldelight-integration-ios-android/) | Blog | Platform-specific setup |
| [Ktor MockEngine Patterns](https://akjaw.com/using-ktor-client-mock-engine-for-integration-and-ui-tests/) | Blog | Advanced MockEngine |
| [KMP Testing Guide 2025](https://www.kmpship.app/blog/kotlin-multiplatform-testing-guide-2025) | Blog | Production practices |
| [Kotest + Testcontainers](https://kotest.io/docs/extensions/test_containers.html) | Official | JVM-only containers |

### CS-фундамент

| Тема | Применение в KMP | Где изучить |
|------|------------------|-------------|
| Contract Testing | MockEngine, API verification | Martin Fowler articles |
| Seams | expect/actual, DI, Engine injection | Michael Feathers "Working with Legacy Code" |
| Test Doubles | Fake vs Mock vs Stub taxonomy | Gerard Meszaros "xUnit Test Patterns" |
| Test Isolation | In-memory DB, per-test state | ISTQB Foundation |
| Integration Testing | Component interaction verification | Continuous Delivery book |

---
*Проверено: 2026-01-09 | SQLDelight 2.2.1, Ktor 3.1.0, kotlin.test 2.1.21*
