---
title: "Ktor Client в Kotlin Multiplatform: сетевой слой на всех платформах"
created: 2026-01-03
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - ktor
  - topic/networking
  - "http"
  - api
  - type/concept
  - level/intermediate
related:
  - "[[kmp-overview]]"
  - "[[kmp-architecture-patterns]]"
  - "[[kmp-di-patterns]]"
prerequisites:
  - "[[kmp-getting-started]]"
  - "[[kmp-kotlinx-libraries]]"
  - "[[kotlin-coroutines]]"
cs-foundations:
  - "[[http-protocol-fundamentals]]"
  - "[[async-io-models]]"
  - "[[connection-pooling]]"
  - "[[retry-strategies]]"
status: published
reading_time: 49
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Ktor Client в Kotlin Multiplatform

> **TL;DR:** Ktor Client — официальный HTTP-клиент для KMP, работает на JVM, Android, iOS, Web (JS/Wasm), Desktop. Версия 3.3.x использует kotlinx-io, поддерживает HTTP/2, WebSockets, kotlinx.serialization. Engines: OkHttp (Android), Darwin (iOS), CIO (кросс-платформенный). MockEngine для тестов. Plugins: ContentNegotiation, Auth, HttpTimeout, Logging.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить | CS-фундамент |
|------|-------------|-------------|--------------|
| Kotlin Coroutines | Ktor async-first | [[kotlin-coroutines]] | [[async-io-models]] |
| HTTP основы | REST, status codes | MDN Web Docs | [[http-protocol-fundamentals]] |
| kotlinx.serialization | JSON parsing | [[kmp-kotlinx-libraries]] | [[serialization-theory]] |
| KMP структура | Source sets | [[kmp-project-structure]] | — |
| Сетевые концепции | Pooling, retry | — | [[connection-pooling]], [[retry-strategies]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Engine** | Платформо-специфичная реализация HTTP | Двигатель в автомобиле — разные для бензина и электричества, но машина едет одинаково |
| **Plugin** | Расширение функциональности клиента | Аксессуары для камеры — фильтры, вспышка добавляют возможности |
| **ContentNegotiation** | Автоматическая сериализация/десериализация | Переводчик между форматами — JSON в объект и обратно |
| **MockEngine** | Тестовый движок без сети | Тренажёр для пилотов — симулирует полёт без настоящего самолёта |
| **Interceptor** | Перехватчик запросов/ответов | Таможня — проверяет всё, что проходит через границу |

---

## Почему Ktor? Теоретические основы

### HTTP-клиент как абстракция над сетью

HTTP-клиент решает фундаментальную проблему: **приложение должно общаться с сетью, но не должно зависеть от её деталей**. Это проявление принципа **Separation of Concerns** — бизнес-логика не знает о TCP-сокетах, TLS-хендшейках и DNS-резолюции.

```
┌─────────────────────────────────────────────────────────────────┐
│                    УРОВНИ АБСТРАКЦИИ HTTP-КЛИЕНТА               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Application Layer (ваш код)                                   │
│   ├── "Получить пользователя с ID=123"                         │
│   └── Работает с доменными объектами (User, Order)              │
│                           ↓                                     │
│   HTTP Layer (Ktor Client)                                      │
│   ├── GET /api/users/123                                        │
│   ├── Headers, Auth, Content-Type                               │
│   └── Сериализация/десериализация                               │
│                           ↓                                     │
│   Transport Layer (Engine)                                      │
│   ├── Connection pooling                                        │
│   ├── TLS negotiation                                           │
│   └── HTTP/1.1 или HTTP/2 framing                               │
│                           ↓                                     │
│   OS Layer (Socket)                                             │
│   └── TCP/IP, DNS                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Async I/O: почему Ktor использует корутины

Сетевой I/O — это операция ожидания. Когда приложение отправляет запрос, большую часть времени оно **ждёт ответа от сервера**, а не вычисляет. Традиционный подход — blocking I/O — занимает поток на всё время ожидания:

```
Blocking I/O (один запрос = один заблокированный поток):
Thread-1: |===WAIT===========================|  → 100ms ожидания
Thread-2: |===WAIT===========================|  → 100ms ожидания
Thread-3: |===WAIT===========================|  → 100ms ожидания
Итого: 3 потока заняты, но не работают

Non-blocking I/O (Ktor + Coroutines):
Thread-1: |REQ1|suspend|REQ2|suspend|REQ3|... → один поток, много запросов
          Корутины переключаются, пока ждут сеть
```

**Ktor построен на kotlinx-io** (начиная с версии 3.0), который использует **suspend-функции** для всех I/O операций. Это даёт:
- **Эффективность**: тысячи concurrent запросов на нескольких потоках
- **Простоту**: код выглядит синхронным, но работает асинхронно
- **Cancellation**: можно отменить запрос, и ресурсы освободятся

### Engine Pattern: стратегия для платформ

Ktor использует паттерн **Strategy** для HTTP-движков. Один и тот же код использует разные реализации в зависимости от платформы:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ENGINE STRATEGY PATTERN                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   HttpClient (Context)                                          │
│       │                                                         │
│       ├── uses ──→ HttpClientEngine (Strategy Interface)        │
│       │                    │                                    │
│       │            ┌───────┴───────┬───────────┬──────────┐    │
│       │            ↓               ↓           ↓          ↓    │
│       │         OkHttp         Darwin        CIO         Js    │
│       │        (Android)       (iOS)      (Native)    (Browser)│
│       │            │               │           │          │    │
│       │         OkHttp3        URLSession  Coroutine   Fetch   │
│       │         library        Foundation    I/O        API    │
│       │                                                         │
│   Преимущество: ваш код не меняется при смене платформы         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Connection Pooling: почему один клиент на приложение

Создание TCP-соединения — дорогая операция (DNS → TCP handshake → TLS handshake). **Connection pooling** переиспользует соединения:

```
Без pooling (новый клиент на каждый запрос):
Request 1: [DNS][TCP][TLS][HTTP] → ~200ms overhead
Request 2: [DNS][TCP][TLS][HTTP] → ~200ms overhead
Request 3: [DNS][TCP][TLS][HTTP] → ~200ms overhead

С pooling (один HttpClient):
Request 1: [DNS][TCP][TLS][HTTP] → ~200ms (первый раз)
Request 2:              [HTTP]   → ~20ms  (соединение уже есть!)
Request 3:              [HTTP]   → ~20ms
```

**Правило: один HttpClient на приложение** — это не просто best practice, это архитектурное требование для производительности.

### kotlinx-io: революция производительности в Ktor 3.0

До версии 3.0 Ktor использовал собственную I/O библиотеку. В 3.0 перешли на **kotlinx-io** (основанную на Okio от Square):

| Метрика | Ktor 2.x | Ktor 3.x | Улучшение |
|---------|----------|----------|-----------|
| Throughput (большие файлы) | Baseline | +90% | Меньше копирования байтов |
| Memory allocation | Baseline | -40% | Переиспользование буферов |
| Native performance | Baseline | +60% | Platform-specific оптимизации |

**Почему такое улучшение?** kotlinx-io использует:
- **Buffer segments** — переиспользуемые куски памяти
- **Zero-copy** где возможно — данные не копируются между буферами
- **Platform-native** операции для iOS, Android, Desktop

---

## Ktor 3.x: что нового

### Ключевые изменения в Ktor 3.0+

```
┌─────────────────────────────────────────────────────────────┐
│                     KTOR 3.x CHANGES                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   🆕 kotlinx-io library (based on Okio)                    │
│      • Улучшенная производительность IO                     │
│      • Multiplatform file handling                          │
│      • Compression support                                  │
│                                                             │
│   🌐 WebAssembly Support                                   │
│      • Kotlin/Wasm target (Alpha)                          │
│      • Browser-based Kotlin apps                            │
│                                                             │
│   🔒 Improved Type Safety                                  │
│      • AttributeKey by identity                            │
│      • Exact type matching                                  │
│                                                             │
│   📡 WebRTC Client (3.3.0+)                                │
│      • Experimental peer-to-peer                            │
│      • Real-time communication                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Текущая версия:** `3.3.3` (январь 2026)

---

## Engines по платформам

### Обзор доступных engines

| Engine | Платформы | HTTP/2 | WebSockets | Особенности |
|--------|-----------|--------|------------|-------------|
| **OkHttp** | Android, JVM | ✅ | ✅ | Популярный, отлично для Android |
| **Darwin** | iOS, macOS, tvOS, watchOS | ✅ | ✅ | NSURLSession под капотом |
| **CIO** | All (JVM, Android, Native, JS, Wasm) | ❌ | ✅ | Coroutine-based, no dependencies |
| **Apache5** | JVM | ✅ | ❌ | Enterprise-grade |
| **Java** | JVM (Java 11+) | ✅ | ✅ | HttpClient из Java |
| **Js** | Browser, Node.js | ✅ | ✅ | Fetch API |
| **Curl** | Linux, macOS, Windows | ✅ | ❌ | libcurl |
| **WinHttp** | Windows | ✅ | ❌ | Windows native |

### Рекомендации по выбору

```kotlin
// Вариант 1: Platform-specific engines (РЕКОМЕНДУЕТСЯ)
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("io.ktor:ktor-client-core:3.3.3")
            implementation("io.ktor:ktor-client-content-negotiation:3.3.3")
            implementation("io.ktor:ktor-serialization-kotlinx-json:3.3.3")
        }
        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:3.3.3")
        }
        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:3.3.3")
        }
        jvmMain.dependencies {
            implementation("io.ktor:ktor-client-java:3.3.3")
        }
        jsMain.dependencies {
            implementation("io.ktor:ktor-client-js:3.3.3")
        }
    }
}

// Вариант 2: CIO везде (простота, но без HTTP/2)
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("io.ktor:ktor-client-cio:3.3.3")
        }
    }
}
```

---

## Настройка HttpClient

### Базовая конфигурация

```kotlin
// commonMain/kotlin/network/HttpClientFactory.kt

// expect/actual pattern для создания клиента
expect fun createPlatformHttpClient(): HttpClient

// Общая конфигурация
fun createHttpClient(): HttpClient = createPlatformHttpClient().config {
    // JSON serialization
    install(ContentNegotiation) {
        json(Json {
            prettyPrint = true
            isLenient = true
            ignoreUnknownKeys = true  // Не падать на неизвестных полях
            coerceInputValues = true  // null → default value
            encodeDefaults = false    // Не отправлять default values
        })
    }

    // Timeouts
    install(HttpTimeout) {
        requestTimeoutMillis = 30_000
        connectTimeoutMillis = 15_000
        socketTimeoutMillis = 30_000
    }

    // Logging (только для debug)
    install(Logging) {
        logger = Logger.DEFAULT
        level = LogLevel.HEADERS  // BODY только для отладки!
    }

    // Default request configuration
    defaultRequest {
        url("https://api.example.com/v1/")
        header(HttpHeaders.ContentType, ContentType.Application.Json)
    }

    // Response validation
    expectSuccess = true  // Throw on non-2xx
}
```

### Platform-specific implementations

```kotlin
// androidMain/kotlin/network/HttpClientFactory.android.kt
actual fun createPlatformHttpClient(): HttpClient = HttpClient(OkHttp) {
    engine {
        config {
            retryOnConnectionFailure(true)
            connectTimeout(15, TimeUnit.SECONDS)
        }
        // Можно добавить OkHttp Interceptors
        addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("X-Platform", "Android")
                .build()
            chain.proceed(request)
        }
    }
}

// iosMain/kotlin/network/HttpClientFactory.ios.kt
actual fun createPlatformHttpClient(): HttpClient = HttpClient(Darwin) {
    engine {
        configureRequest {
            setAllowsCellularAccess(true)
        }
        configureSession {
            // NSURLSessionConfiguration
        }
    }
}

// jvmMain/kotlin/network/HttpClientFactory.jvm.kt
actual fun createPlatformHttpClient(): HttpClient = HttpClient(Java) {
    engine {
        // Java HttpClient configuration
        threadsCount = 4
        pipelining = true
    }
}
```

---

## Работа с API

### Типичные запросы

```kotlin
// commonMain/kotlin/network/ApiService.kt
class ApiService(private val client: HttpClient) {

    private val baseUrl = "https://api.example.com/v1"

    // GET запрос
    suspend fun getUsers(): List<User> {
        return client.get("$baseUrl/users").body()
    }

    // GET с параметрами
    suspend fun getUserById(id: String): User {
        return client.get("$baseUrl/users/$id").body()
    }

    // GET с query parameters
    suspend fun searchUsers(query: String, page: Int = 1): PaginatedResponse<User> {
        return client.get("$baseUrl/users") {
            parameter("q", query)
            parameter("page", page)
            parameter("limit", 20)
        }.body()
    }

    // POST запрос
    suspend fun createUser(request: CreateUserRequest): User {
        return client.post("$baseUrl/users") {
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
    }

    // PUT запрос
    suspend fun updateUser(id: String, request: UpdateUserRequest): User {
        return client.put("$baseUrl/users/$id") {
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
    }

    // DELETE запрос
    suspend fun deleteUser(id: String) {
        client.delete("$baseUrl/users/$id")
    }

    // Multipart/form-data (upload)
    suspend fun uploadAvatar(userId: String, imageBytes: ByteArray): UploadResponse {
        return client.submitFormWithBinaryData(
            url = "$baseUrl/users/$userId/avatar",
            formData = formData {
                append("file", imageBytes, Headers.build {
                    append(HttpHeaders.ContentType, "image/jpeg")
                    append(HttpHeaders.ContentDisposition, "filename=\"avatar.jpg\"")
                })
            }
        ).body()
    }
}

// Data classes
@Serializable
data class User(
    val id: String,
    val name: String,
    val email: String,
    @SerialName("created_at")
    val createdAt: String
)

@Serializable
data class CreateUserRequest(
    val name: String,
    val email: String,
    val password: String
)

@Serializable
data class PaginatedResponse<T>(
    val data: List<T>,
    val page: Int,
    val totalPages: Int,
    val totalItems: Int
)
```

---

## Обработка ошибок

### Стратегия с Result wrapper

```kotlin
// commonMain/kotlin/network/ApiResult.kt
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val exception: ApiException) : ApiResult<Nothing>()
}

sealed class ApiException(message: String, cause: Throwable? = null) : Exception(message, cause) {
    class NetworkError(cause: Throwable) : ApiException("Network error", cause)
    class ServerError(val code: Int, message: String) : ApiException("Server error: $code - $message")
    class ClientError(val code: Int, message: String) : ApiException("Client error: $code - $message")
    class UnauthorizedError : ApiException("Unauthorized")
    class ParseError(cause: Throwable) : ApiException("Parse error", cause)
    class UnknownError(cause: Throwable) : ApiException("Unknown error", cause)
}

// Extension для безопасных вызовов
suspend inline fun <reified T> safeApiCall(
    crossinline block: suspend () -> T
): ApiResult<T> {
    return try {
        ApiResult.Success(block())
    } catch (e: RedirectResponseException) {
        ApiResult.Error(ApiException.ServerError(e.response.status.value, "Redirect"))
    } catch (e: ClientRequestException) {
        when (e.response.status.value) {
            401 -> ApiResult.Error(ApiException.UnauthorizedError())
            else -> ApiResult.Error(ApiException.ClientError(
                e.response.status.value,
                e.response.bodyAsText()
            ))
        }
    } catch (e: ServerResponseException) {
        ApiResult.Error(ApiException.ServerError(
            e.response.status.value,
            e.response.bodyAsText()
        ))
    } catch (e: HttpRequestTimeoutException) {
        ApiResult.Error(ApiException.NetworkError(e))
    } catch (e: SerializationException) {
        ApiResult.Error(ApiException.ParseError(e))
    } catch (e: Exception) {
        ApiResult.Error(ApiException.UnknownError(e))
    }
}

// Использование
class UserRepository(private val api: ApiService) {
    suspend fun getUsers(): ApiResult<List<User>> = safeApiCall {
        api.getUsers()
    }
}
```

### HttpResponseValidator для централизованной обработки

```kotlin
fun createHttpClient() = HttpClient(CIO) {
    install(ContentNegotiation) {
        json()
    }

    expectSuccess = true

    HttpResponseValidator {
        validateResponse { response ->
            val statusCode = response.status.value

            when (statusCode) {
                in 300..399 -> throw RedirectResponseException(response, "Redirect")
                401 -> throw UnauthorizedException()
                403 -> throw ForbiddenException()
                404 -> throw NotFoundException()
                in 400..499 -> {
                    val body = response.bodyAsText()
                    throw ClientRequestException(response, body)
                }
                in 500..599 -> {
                    val body = response.bodyAsText()
                    throw ServerResponseException(response, body)
                }
            }
        }

        handleResponseExceptionWithRequest { exception, request ->
            // Log or transform exceptions
            println("Request to ${request.url} failed: ${exception.message}")
            throw exception
        }
    }
}
```

---

## Аутентификация

### Bearer Token с автообновлением

```kotlin
// commonMain/kotlin/network/AuthenticatedClient.kt
class TokenStorage {
    private var accessToken: String? = null
    private var refreshToken: String? = null

    fun getTokens(): BearerTokens? {
        val access = accessToken ?: return null
        val refresh = refreshToken ?: return null
        return BearerTokens(access, refresh)
    }

    fun saveTokens(access: String, refresh: String) {
        accessToken = access
        refreshToken = refresh
    }

    fun clear() {
        accessToken = null
        refreshToken = null
    }
}

fun createAuthenticatedClient(tokenStorage: TokenStorage): HttpClient {
    return HttpClient(CIO) {
        install(ContentNegotiation) {
            json()
        }

        install(Auth) {
            bearer {
                // Загрузка токенов при старте
                loadTokens {
                    tokenStorage.getTokens()
                }

                // Автоматическое обновление при 401
                refreshTokens {
                    val refreshToken = oldTokens?.refreshToken
                        ?: return@refreshTokens null

                    // Запрос на обновление токена
                    val response: TokenResponse = client.post("https://api.example.com/auth/refresh") {
                        contentType(ContentType.Application.Json)
                        setBody(RefreshRequest(refreshToken))
                    }.body()

                    // Сохранение новых токенов
                    tokenStorage.saveTokens(response.accessToken, response.refreshToken)

                    BearerTokens(response.accessToken, response.refreshToken)
                }

                // Отправлять токен сразу (без ожидания 401)
                sendWithoutRequest { request ->
                    request.url.host == "api.example.com"
                }
            }
        }
    }
}

@Serializable
data class TokenResponse(
    @SerialName("access_token")
    val accessToken: String,
    @SerialName("refresh_token")
    val refreshToken: String
)

@Serializable
data class RefreshRequest(
    @SerialName("refresh_token")
    val refreshToken: String
)
```

### API Key Authentication

```kotlin
fun createApiKeyClient(apiKey: String): HttpClient {
    return HttpClient(CIO) {
        defaultRequest {
            header("X-API-Key", apiKey)
        }
    }
}
```

---

## Retry и HttpSend

### Автоматический retry с exponential backoff

```kotlin
fun createRetryClient(): HttpClient {
    return HttpClient(CIO) {
        install(HttpRequestRetry) {
            maxRetries = 3

            // Exponential backoff
            exponentialDelay(base = 2.0, maxDelayMs = 30_000)

            // Retry только для определённых ошибок
            retryOnExceptionIf { _, cause ->
                cause is HttpRequestTimeoutException ||
                cause is ConnectTimeoutException ||
                cause is SocketTimeoutException
            }

            // Retry на 5xx ошибки
            retryOnServerErrors(maxRetries = 3)

            // Retry на 429 (rate limit)
            retryIf { _, response ->
                response.status == HttpStatusCode.TooManyRequests
            }

            // Callback перед retry
            modifyRequest { request ->
                request.headers.append("X-Retry-Count", retryCount.toString())
            }
        }
    }
}
```

### Custom interceptor с HttpSend

```kotlin
fun createInterceptorClient(): HttpClient {
    val client = HttpClient(CIO)

    client.plugin(HttpSend).intercept { request ->
        val startTime = System.currentTimeMillis()

        // Выполнить запрос
        val call = execute(request)

        val duration = System.currentTimeMillis() - startTime
        println("${request.method.value} ${request.url} completed in ${duration}ms")

        // Можно модифицировать или retry
        if (call.response.status == HttpStatusCode.ServiceUnavailable) {
            println("Service unavailable, retrying...")
            delay(1000)
            execute(request)  // Retry
        } else {
            call
        }
    }

    return client
}
```

---

## Тестирование с MockEngine

### Базовое тестирование

```kotlin
// commonTest/kotlin/network/ApiServiceTest.kt
class ApiServiceTest {

    @Test
    fun `getUsers returns list of users`() = runTest {
        // Arrange
        val mockEngine = MockEngine { request ->
            when (request.url.encodedPath) {
                "/users" -> respond(
                    content = ByteReadChannel("""
                        [
                            {"id": "1", "name": "John", "email": "john@example.com", "created_at": "2024-01-01"},
                            {"id": "2", "name": "Jane", "email": "jane@example.com", "created_at": "2024-01-02"}
                        ]
                    """.trimIndent()),
                    status = HttpStatusCode.OK,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
                else -> respondError(HttpStatusCode.NotFound)
            }
        }

        val client = HttpClient(mockEngine) {
            install(ContentNegotiation) {
                json()
            }
        }
        val api = ApiService(client)

        // Act
        val users = api.getUsers()

        // Assert
        assertEquals(2, users.size)
        assertEquals("John", users[0].name)
    }

    @Test
    fun `getUsers handles error response`() = runTest {
        val mockEngine = MockEngine {
            respond(
                content = ByteReadChannel("""{"error": "Server error"}"""),
                status = HttpStatusCode.InternalServerError,
                headers = headersOf(HttpHeaders.ContentType, "application/json")
            )
        }

        val client = HttpClient(mockEngine) {
            install(ContentNegotiation) { json() }
            expectSuccess = true
        }
        val api = ApiService(client)

        // Assert exception
        assertFailsWith<ServerResponseException> {
            api.getUsers()
        }
    }
}
```

### Routing by URL

```kotlin
class MockApiEngine {
    fun create(): MockEngine = MockEngine { request ->
        val path = request.url.encodedPath
        val method = request.method

        when {
            method == HttpMethod.Get && path == "/users" -> {
                respondOk(usersJson)
            }
            method == HttpMethod.Get && path.startsWith("/users/") -> {
                val id = path.substringAfterLast("/")
                respondOk(userJson(id))
            }
            method == HttpMethod.Post && path == "/users" -> {
                respond(
                    content = ByteReadChannel(createdUserJson),
                    status = HttpStatusCode.Created,
                    headers = headersOf(HttpHeaders.ContentType, "application/json")
                )
            }
            method == HttpMethod.Delete && path.startsWith("/users/") -> {
                respond("", HttpStatusCode.NoContent)
            }
            else -> respondError(HttpStatusCode.NotFound)
        }
    }

    private fun respondOk(content: String) = respond(
        content = ByteReadChannel(content),
        status = HttpStatusCode.OK,
        headers = headersOf(HttpHeaders.ContentType, "application/json")
    )

    companion object {
        private val usersJson = """[{"id":"1","name":"John","email":"john@example.com","created_at":"2024-01-01"}]"""
        private fun userJson(id: String) = """{"id":"$id","name":"User $id","email":"user$id@example.com","created_at":"2024-01-01"}"""
        private val createdUserJson = """{"id":"new-id","name":"New User","email":"new@example.com","created_at":"2024-01-03"}"""
    }
}
```

---

## WebSockets

### Настройка WebSocket клиента

```kotlin
// Зависимости
// implementation("io.ktor:ktor-client-websockets:3.3.3")

fun createWebSocketClient(): HttpClient {
    return HttpClient(CIO) {
        install(WebSockets) {
            pingIntervalMillis = 20_000
            maxFrameSize = Long.MAX_VALUE
        }
    }
}

// Использование
class ChatService(private val client: HttpClient) {

    suspend fun connectToChat(
        roomId: String,
        onMessage: (ChatMessage) -> Unit,
        onError: (Throwable) -> Unit
    ) {
        try {
            client.webSocket("wss://chat.example.com/rooms/$roomId") {
                // Отправка сообщений
                launch {
                    // Можно отправлять из другого места через Channel
                }

                // Получение сообщений
                for (frame in incoming) {
                    when (frame) {
                        is Frame.Text -> {
                            val text = frame.readText()
                            val message = Json.decodeFromString<ChatMessage>(text)
                            onMessage(message)
                        }
                        is Frame.Close -> {
                            println("Connection closed: ${closeReason.await()}")
                            break
                        }
                        else -> {}
                    }
                }
            }
        } catch (e: Exception) {
            onError(e)
        }
    }

    // С serialization
    suspend fun connectWithSerialization(roomId: String) {
        val client = HttpClient(CIO) {
            install(WebSockets) {
                contentConverter = KotlinxWebsocketSerializationConverter(Json)
            }
        }

        client.webSocket("wss://chat.example.com/rooms/$roomId") {
            // Типизированная отправка
            sendSerialized(ChatMessage("user1", "Hello!"))

            // Типизированное получение
            val message: ChatMessage = receiveDeserialized()
        }
    }
}

@Serializable
data class ChatMessage(
    val userId: String,
    val content: String,
    val timestamp: Long = System.currentTimeMillis()
)
```

---

## Кэширование

### Встроенный HttpCache (in-memory)

```kotlin
fun createCachingClient(): HttpClient {
    return HttpClient(CIO) {
        install(HttpCache)  // In-memory cache
    }
}
```

### Persistent cache с Kachetor

```kotlin
// Зависимость: implementation("io.github.nicepay:kachetor:1.0.0")

// Kachetor добавляет persistent caching для KMP
// Использует SQLDelight для хранения на всех платформах
```

### ETag и conditional requests

```kotlin
class ConditionalRequestClient(private val client: HttpClient) {
    private val etagCache = mutableMapOf<String, String>()

    suspend fun getWithEtag(url: String): HttpResponse {
        val etag = etagCache[url]

        return client.get(url) {
            if (etag != null) {
                header(HttpHeaders.IfNoneMatch, etag)
            }
        }.also { response ->
            // Сохранить ETag
            response.headers[HttpHeaders.ETag]?.let { newEtag ->
                etagCache[url] = newEtag
            }
        }
    }
}
```

---

## Архитектура сетевого слоя

### Чистая архитектура с Ktor

```
┌─────────────────────────────────────────────────────────────┐
│                    NETWORK LAYER ARCHITECTURE               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   UI Layer                                                  │
│   ├── ViewModel/Presenter                                   │
│   └── Uses ApiResult<T>                                     │
│                                                             │
│   Domain Layer                                              │
│   ├── Repository interfaces                                 │
│   ├── UseCases                                              │
│   └── Domain models                                         │
│                                                             │
│   Data Layer                                                │
│   ├── RepositoryImpl                                        │
│   ├── DataSource interfaces                                 │
│   └── ApiService (Ktor calls)                               │
│                                                             │
│   Network Layer                                             │
│   ├── HttpClientFactory (expect/actual)                     │
│   ├── ApiResult wrapper                                     │
│   ├── DTOs (@Serializable)                                  │
│   └── Mappers (DTO → Domain)                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Пример организации кода

```kotlin
// network/
//   ├── HttpClientFactory.kt         // expect/actual для engines
//   ├── ApiService.kt                // API calls
//   ├── ApiResult.kt                 // Result wrapper
//   ├── dto/
//   │   ├── UserDto.kt
//   │   └── ResponseDto.kt
//   └── mappers/
//       └── UserMapper.kt

// data/
//   ├── UserRepositoryImpl.kt
//   └── UserRemoteDataSource.kt

// domain/
//   ├── UserRepository.kt (interface)
//   └── User.kt (domain model)
```

---

## Best Practices

### Checklist

| Практика | Описание |
|----------|----------|
| ✅ Один HttpClient | Переиспользуйте, не создавайте на каждый запрос |
| ✅ expect/actual для engines | Оптимальный engine для каждой платформы |
| ✅ ContentNegotiation | JSON автоматически |
| ✅ HttpTimeout | Всегда устанавливайте таймауты |
| ✅ expectSuccess = true | Бросать исключения на non-2xx |
| ✅ ignoreUnknownKeys = true | Не падать на новых полях от API |
| ✅ MockEngine для тестов | Быстрые unit-тесты без сети |
| ⚠️ Logging.BODY | Только для отладки, не в production |
| ⚠️ HttpCache | Только in-memory, для persistent нужен Kachetor |

### Производительность

```kotlin
// ❌ Плохо: новый клиент на каждый запрос
suspend fun badGetUsers(): List<User> {
    val client = HttpClient(CIO)  // Создаётся каждый раз!
    return client.get("/users").body()
}

// ✅ Хорошо: один клиент на приложение
class ApiService(private val client: HttpClient) {  // Inject once
    suspend fun getUsers(): List<User> = client.get("/users").body()
}

// ✅ Хорошо: close() при завершении
class AppLifecycle(private val client: HttpClient) {
    fun onDestroy() {
        client.close()
    }
}
```

---

## Миграция с Retrofit

### Сравнение API

| Retrofit | Ktor |
|----------|------|
| `@GET("users")` | `client.get("/users")` |
| `@POST("users") @Body` | `client.post("/users") { setBody(...) }` |
| `@Query("page")` | `parameter("page", value)` |
| `@Path("id")` | String interpolation в URL |
| `OkHttpClient.Builder()` | `HttpClient(OkHttp) { engine { ... } }` |
| `GsonConverterFactory` | `ContentNegotiation { json() }` |
| Interface + suspend | Direct suspend functions |

### Пример миграции

```kotlin
// Retrofit
interface UserApi {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User

    @POST("users")
    suspend fun createUser(@Body request: CreateUserRequest): User
}

// Ktor
class UserApi(private val client: HttpClient) {
    suspend fun getUser(id: String): User =
        client.get("users/$id").body()

    suspend fun createUser(request: CreateUserRequest): User =
        client.post("users") {
            contentType(ContentType.Application.Json)
            setBody(request)
        }.body()
}
```

---

## Кто использует

| Компания | Применение | Результат |
|----------|------------|-----------|
| **Netflix** | Mobile networking layer | 60% shared code |
| **McDonald's** | Global app API | Unified API client |
| **Cash App** | Fintech API layer | Cross-platform consistency |
| **Philips** | Healthcare APIs | Shared network logic |

---

## Мифы и заблуждения

### Миф 1: "Ktor медленнее Retrofit"

**Реальность:** Ktor 3.0+ с kotlinx-io показывает производительность **на уровне или выше** Retrofit/OkHttp для большинства сценариев. 90%+ улучшение throughput делает Ktor конкурентоспособным даже для data-intensive приложений.

**Правда:** Retrofit имеет преимущество в экосистеме Android (interceptors, интеграции), но для KMP Ktor — единственный официально поддерживаемый вариант.

### Миф 2: "CIO engine подходит для всего"

**Реальность:** CIO (Coroutine I/O) универсален, но **не поддерживает HTTP/2**. Для production рекомендуется:
- Android → OkHttp (HTTP/2, проверенный в бою)
- iOS → Darwin (интеграция с системой, HTTP/2)
- JVM backend → Java или Apache5

**Когда CIO подходит:** прототипы, тесты, простые API без HTTP/2 требований.

### Миф 3: "Можно создавать HttpClient на каждый запрос"

**Реальность:** Категорически нет. Каждый `HttpClient()` создаёт новый connection pool. Это:
- Отключает connection reuse
- Создаёт overhead на каждый запрос (DNS, TCP, TLS)
- Может исчерпать file descriptors

**Правильно:** один `HttpClient` на приложение, inject через DI, вызывать `client.close()` при завершении.

### Миф 4: "expectSuccess = true опасен"

**Реальность:** Это **рекомендуемый** подход. Без него:
- Нужно вручную проверять status code каждого ответа
- Легко пропустить ошибку и парсить error body как success
- Код становится verbose

**С expectSuccess:** 4xx/5xx бросают исключения → можно обрабатывать централизованно в `safeApiCall` wrapper.

### Миф 5: "WebSockets в Ktor нестабильны"

**Реальность:** WebSockets стабильны с Ktor 2.0+. Проблемы обычно связаны с:
- Неправильной обработкой reconnection (нужна своя логика)
- Забытым `pingIntervalMillis` (сервер закрывает idle соединения)
- Отсутствием error handling в `for (frame in incoming)`

**Совет:** используйте обёртку с exponential backoff для reconnection.

### Миф 6: "Для iOS нужен другой сетевой код"

**Реальность:** Весь Ktor код в `commonMain` работает на iOS идентично Android/JVM. Darwin engine использует `NSURLSession` под капотом, но API полностью унифицирован.

**Единственное отличие:** `expect/actual` для engine creation — и даже это опционально с CIO.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [ktor.io/docs/client](https://ktor.io/docs/client.html) | Official | Документация Ktor Client |
| [Ktor 3.0 Release](https://blog.jetbrains.com/kotlin/2024/10/ktor-3-0/) | Blog | Что нового в 3.0 |
| [Migration Guide](https://ktor.io/docs/migrating-3.html) | Official | Миграция с 2.x |
| [ktor-samples](https://github.com/ktorio/ktor-samples) | GitHub | Примеры кода |
| [KMP with Ktor Tutorial](https://kotlinlang.org/docs/multiplatform/multiplatform-ktor-sqldelight.html) | Official | Туториал KMP + Ktor |

### CS-фундамент

| Концепция | Связь с Ktor | Где углубить |
|-----------|--------------|--------------|
| [[http-protocol-fundamentals]] | REST, status codes, headers | RFC 7230-7235 |
| [[async-io-models]] | Suspend functions, non-blocking I/O | kotlinx-io internals |
| [[connection-pooling]] | HttpClient reuse, keep-alive | OkHttp Connection Pool |
| [[retry-strategies]] | Exponential backoff, jitter | AWS architecture blog |
| [[serialization-theory]] | ContentNegotiation, JSON | kotlinx.serialization docs |

---

## Связь с другими темами

- **[[kmp-overview]]** — Ktor Client является официально рекомендованным HTTP-клиентом для KMP-проектов. Понимание общей архитектуры KMP — source sets, expect/actual, target-специфичных зависимостей — необходимо для правильной настройки engine-ов (OkHttp для Android, Darwin для iOS) и организации сетевого слоя в multiplatform-проекте.

- **[[kmp-architecture-patterns]]** — Ktor вписывается в чистую архитектуру KMP как инфраструктурный слой: HttpClientFactory через expect/actual, ApiService в data layer, DTOs с @Serializable и mappers в domain. Знание архитектурных паттернов KMP позволяет правильно организовать сетевой код, разделить ответственность между слоями и обеспечить тестируемость через MockEngine.

- **[[kmp-di-patterns]]** — HttpClient должен создаваться один раз и инжектироваться через DI (Koin, kotlin-inject) во все сервисы. Неправильное управление жизненным циклом клиента — создание нового HttpClient на каждый запрос — приводит к потере connection pooling и деградации производительности. DI-паттерны обеспечивают единый экземпляр и правильное закрытие ресурсов.

## Источники и дальнейшее чтение

- **Moskala M. (2022).** *Kotlin Coroutines: Deep Dive.* — Ktor полностью построен на корутинах: все I/O операции используют suspend-функции, а Flow применяется для WebSocket-стримов. Книга раскрывает механику structured concurrency и cancellation, критичные для понимания поведения Ktor при отмене запросов и таймаутах.

- **Martin R. (2017).** *Clean Architecture.* — Принципы разделения слоёв и инверсии зависимостей напрямую применяются к организации сетевого кода в KMP: Repository pattern, DTO → Domain mapping и абстракция HttpClient через интерфейсы.

- **Moskala M. (2021).** *Effective Kotlin.* — Практические паттерны Kotlin, включая правильную обработку ошибок через sealed classes (ApiResult), использование inline-функций (safeApiCall) и работу с nullable типами, что составляет основу robust сетевого слоя.

---

## Проверь себя

> [!question]- Почему Ktor использует разные HTTP engines на разных платформах вместо одного универсального?
> Каждая платформа имеет оптимизированный HTTP stack: OkHttp на Android (connection pooling, HTTP/2), Darwin/NSURLSession на iOS (ATS compliance, background sessions), CIO на JVM (корутины). Использование нативных engines обеспечивает лучшую производительность и совместимость.

> [!question]- Как тестировать сетевые запросы в KMP без реального сервера?
> Использовать MockEngine из Ktor: он позволяет задавать fake-ответы для HTTP-запросов в commonTest. MockEngine подменяет реальный engine и возвращает предопределённые responses, что делает тесты быстрыми и детерминированными.

> [!question]- Почему content negotiation в Ktor настраивается через plugin, а не встроена по умолчанию?
> Ktor следует принципу composition over inheritance: каждая функциональность -- отдельный plugin (ContentNegotiation, Auth, Logging). Это позволяет включать только необходимое, минимизируя размер бинарника. Особенно важно для mobile, где размер APK/IPA критичен.

---

## Ключевые карточки

Как Ktor Client организован в KMP?
?
Core API (HttpClient, request builders, plugins) в commonMain. Engine -- platform-specific: OkHttp для Android, Darwin для iOS, CIO для JVM. ContentNegotiation + kotlinx-serialization для JSON.

Какие HTTP engines поддерживает Ktor в KMP?
?
OkHttp (Android), Darwin/NSURLSession (iOS), CIO (JVM coroutine-based), Js (JavaScript), WinHttp (Windows Native). Каждый engine оптимизирован для своей платформы.

Как настроить authentication в Ktor KMP?
?
Через Auth plugin: Bearer token (access + refresh), Basic, Digest. Token refresh -- автоматический через refreshTokens callback. Конфигурация в commonMain, хранение токенов -- через expect/actual (Keychain/EncryptedSharedPreferences).

Что такое MockEngine и как его использовать?
?
Тестовый HTTP engine, возвращающий предопределённые ответы. Создаётся с respond handler, проверяет URL, headers, body запроса. Размещается в commonTest для кросс-платформенного тестирования сетевого слоя.

Как обрабатывать ошибки сети в Ktor KMP?
?
Через HttpResponseValidator plugin для проверки status codes, try-catch для network exceptions, retry logic через custom plugin или kotlinx-coroutines retry. Важно различать ConnectTimeoutException, SocketTimeoutException и ResponseException.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-sqldelight-database]] | Локальное хранение данных, полученных через Ktor |
| Углубиться | [[kmp-integration-testing]] | Тестирование Ktor с MockEngine |
| Смежная тема | [[kmp-kotlinx-libraries]] | kotlinx-serialization для JSON parsing |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Ktor 3.3.3, Kotlin 2.1.21*
