---
title: "Cross-Platform: Networking — URLSession vs Retrofit"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - topic/networking
  - urlsession
  - retrofit
  - type/comparison
  - level/intermediate
reading_time: 57
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-concurrency-modern]]"
related:
  - "[[android-networking]]"
  - "[[ios-networking]]"
  - "[[network-http-evolution]]"
---

# Cross-Platform Networking: URLSession vs Retrofit

## TL;DR

| Аспект | URLSession (iOS) | OkHttp/Retrofit (Android) |
|--------|------------------|---------------------------|
| **Уровень абстракции** | Низкий (URLSession) + высокий (async/await) | Низкий (OkHttp) + высокий (Retrofit) |
| **HTTP-клиент** | Встроенный URLSession | OkHttp (сторонняя библиотека) |
| **REST-обёртка** | Нет стандартной | Retrofit |
| **Сериализация** | Codable (встроенный) | kotlinx.serialization / Gson / Moshi |
| **Асинхронность** | async/await, Combine | Coroutines, RxJava, Flow |
| **Интерцепторы** | URLProtocol (сложно) | OkHttp Interceptors (просто) |
| **Кэширование** | URLCache | OkHttp Cache |
| **Мок-тестирование** | URLProtocol | MockWebServer |
| **Конфигурация** | URLSessionConfiguration | OkHttpClient.Builder |
| **Multipart** | Ручная сборка | RequestBody.Part |
| **WebSocket** | URLSessionWebSocketTask | OkHttp WebSocket |
| **KMP решение** | — | Ktor Client |

---

## 1. Архитектура сетевого стека

### iOS: URLSession

```
┌─────────────────────────────────────────────┐
│              Ваш код                        │
├─────────────────────────────────────────────┤
│         async/await или Combine             │
├─────────────────────────────────────────────┤
│             URLSession                      │
│  ┌─────────────────────────────────────┐   │
│  │     URLSessionConfiguration         │   │
│  │  - default / ephemeral / background │   │
│  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│             URLCache                        │
├─────────────────────────────────────────────┤
│           URLProtocol                       │
│        (кастомная обработка)                │
├─────────────────────────────────────────────┤
│      CFNetwork / Network.framework          │
└─────────────────────────────────────────────┘
```

### Android: OkHttp + Retrofit

```
┌─────────────────────────────────────────────┐
│              Ваш код                        │
├─────────────────────────────────────────────┤
│             Retrofit                        │
│     (декларативный API-интерфейс)           │
├─────────────────────────────────────────────┤
│        Converter (Gson/Moshi/etc)           │
├─────────────────────────────────────────────┤
│             OkHttp                          │
│  ┌─────────────────────────────────────┐   │
│  │         Interceptors                │   │
│  │   - Application Interceptors        │   │
│  │   - Network Interceptors            │   │
│  └─────────────────────────────────────┘   │
├─────────────────────────────────────────────┤
│          OkHttp Cache                       │
├─────────────────────────────────────────────┤
│       HttpURLConnection / Socket            │
└─────────────────────────────────────────────┘
```

### Ключевые различия в архитектуре

| Концепция | iOS | Android |
|-----------|-----|---------|
| Встроенный HTTP | URLSession (system) | HttpURLConnection (устаревший) |
| Современный HTTP | URLSession | OkHttp (сторонний, но стандарт де-факто) |
| REST-абстракция | Нет (пишем сами) | Retrofit |
| Модификация запросов | URLProtocol (сложно) | Interceptors (просто) |

---

## 2. Создание запросов (Request Building)

### Swift: URLRequest

```swift
// Базовый GET-запрос
func fetchUsers() async throws -> [User] {
    let url = URL(string: "https://api.example.com/users")!
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          (200...299).contains(httpResponse.statusCode) else {
        throw NetworkError.invalidResponse
    }

    return try JSONDecoder().decode([User].self, from: data)
}

// POST-запрос с телом
func createUser(_ user: CreateUserRequest) async throws -> User {
    var request = URLRequest(url: URL(string: "https://api.example.com/users")!)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.httpBody = try JSONEncoder().encode(user)

    let (data, response) = try await URLSession.shared.data(for: request)

    guard let httpResponse = response as? HTTPURLResponse,
          (200...299).contains(httpResponse.statusCode) else {
        throw NetworkError.invalidResponse
    }

    return try JSONDecoder().decode(User.self, from: data)
}

// Запрос с query-параметрами
func searchUsers(query: String, page: Int) async throws -> UsersResponse {
    var components = URLComponents(string: "https://api.example.com/users/search")!
    components.queryItems = [
        URLQueryItem(name: "q", value: query),
        URLQueryItem(name: "page", value: String(page)),
        URLQueryItem(name: "limit", value: "20")
    ]

    let (data, _) = try await URLSession.shared.data(from: components.url!)
    return try JSONDecoder().decode(UsersResponse.self, from: data)
}
```

### Kotlin: Retrofit

```kotlin
// Декларативный интерфейс API
interface UserApi {
    @GET("users")
    suspend fun getUsers(): List<User>

    @POST("users")
    suspend fun createUser(@Body user: CreateUserRequest): User

    @GET("users/search")
    suspend fun searchUsers(
        @Query("q") query: String,
        @Query("page") page: Int,
        @Query("limit") limit: Int = 20
    ): UsersResponse

    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User

    @PUT("users/{id}")
    suspend fun updateUser(
        @Path("id") userId: String,
        @Body user: UpdateUserRequest
    ): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") userId: String)

    @Multipart
    @POST("users/{id}/avatar")
    suspend fun uploadAvatar(
        @Path("id") userId: String,
        @Part avatar: MultipartBody.Part
    ): AvatarResponse
}

// Создание Retrofit-клиента
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)
    .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
    .build()

val userApi = retrofit.create<UserApi>()

// Использование
suspend fun loadUsers() {
    val users = userApi.getUsers()
    val searchResult = userApi.searchUsers("John", page = 1)
}
```

### Сравнение подходов к Request Building

```swift
// Swift: императивный подход — собираем запрос вручную
func updateUser(id: String, request: UpdateUserRequest) async throws -> User {
    var urlRequest = URLRequest(url: URL(string: "https://api.example.com/users/\(id)")!)
    urlRequest.httpMethod = "PUT"
    urlRequest.setValue("application/json", forHTTPHeaderField: "Content-Type")
    urlRequest.httpBody = try JSONEncoder().encode(request)

    let (data, _) = try await URLSession.shared.data(for: urlRequest)
    return try JSONDecoder().decode(User.self, from: data)
}
```

```kotlin
// Kotlin: декларативный подход — аннотации описывают контракт
@PUT("users/{id}")
suspend fun updateUser(
    @Path("id") userId: String,
    @Body user: UpdateUserRequest
): User
```

---

## 3. Обработка ответов и сериализация

### Swift: Codable

```swift
// Модели с Codable
struct User: Codable {
    let id: String
    let email: String
    let displayName: String
    let createdAt: Date
    let profile: UserProfile?

    enum CodingKeys: String, CodingKey {
        case id
        case email
        case displayName = "display_name"
        case createdAt = "created_at"
        case profile
    }
}

struct UserProfile: Codable {
    let bio: String?
    let avatarUrl: URL?
    let socialLinks: [String: String]

    enum CodingKeys: String, CodingKey {
        case bio
        case avatarUrl = "avatar_url"
        case socialLinks = "social_links"
    }
}

// Настройка JSONDecoder
extension JSONDecoder {
    static let apiDecoder: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()
}

// Generic-функция для декодирования
func fetch<T: Decodable>(_ type: T.Type, from url: URL) async throws -> T {
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse else {
        throw NetworkError.invalidResponse
    }

    switch httpResponse.statusCode {
    case 200...299:
        return try JSONDecoder.apiDecoder.decode(T.self, from: data)
    case 401:
        throw NetworkError.unauthorized
    case 404:
        throw NetworkError.notFound
    case 500...599:
        throw NetworkError.serverError(httpResponse.statusCode)
    default:
        throw NetworkError.unknown(httpResponse.statusCode)
    }
}
```

### Kotlin: kotlinx.serialization

```kotlin
// Модели с kotlinx.serialization
@Serializable
data class User(
    val id: String,
    val email: String,
    @SerialName("display_name")
    val displayName: String,
    @Serializable(with = InstantSerializer::class)
    @SerialName("created_at")
    val createdAt: Instant,
    val profile: UserProfile? = null
)

@Serializable
data class UserProfile(
    val bio: String? = null,
    @SerialName("avatar_url")
    val avatarUrl: String? = null,
    @SerialName("social_links")
    val socialLinks: Map<String, String> = emptyMap()
)

// Кастомный сериализатор для Instant
object InstantSerializer : KSerializer<Instant> {
    override val descriptor = PrimitiveSerialDescriptor("Instant", PrimitiveKind.STRING)

    override fun serialize(encoder: Encoder, value: Instant) {
        encoder.encodeString(value.toString())
    }

    override fun deserialize(decoder: Decoder): Instant {
        return Instant.parse(decoder.decodeString())
    }
}

// Настройка Json
val json = Json {
    ignoreUnknownKeys = true
    isLenient = true
    encodeDefaults = false
    coerceInputValues = true
}

// Retrofit с kotlinx.serialization
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
    .build()
```

### Сравнение Codable vs kotlinx.serialization

| Аспект | Codable (Swift) | kotlinx.serialization (Kotlin) |
|--------|-----------------|--------------------------------|
| Встроенный в язык | Да | Плагин компилятора |
| Рефлексия | Нет | Нет (compile-time) |
| Кастомные ключи | CodingKeys enum | @SerialName |
| Дефолтные значения | init(from:) | Параметры по умолчанию |
| Вложенные объекты | Автоматически | Автоматически |
| Полиморфизм | Ручная реализация | @Polymorphic, sealed class |
| Производительность | Отличная | Отличная |

---

## 4. Обработка ошибок (Error Handling)

### Swift: комплексная обработка

```swift
// Иерархия ошибок
enum NetworkError: Error, LocalizedError {
    case invalidURL
    case noConnection
    case timeout
    case invalidResponse
    case unauthorized
    case forbidden
    case notFound
    case serverError(Int)
    case decodingError(Error)
    case apiError(APIError)
    case unknown(Error)

    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Некорректный URL"
        case .noConnection:
            return "Нет подключения к интернету"
        case .timeout:
            return "Превышено время ожидания"
        case .invalidResponse:
            return "Некорректный ответ сервера"
        case .unauthorized:
            return "Требуется авторизация"
        case .forbidden:
            return "Доступ запрещён"
        case .notFound:
            return "Ресурс не найден"
        case .serverError(let code):
            return "Ошибка сервера: \(code)"
        case .decodingError(let error):
            return "Ошибка декодирования: \(error.localizedDescription)"
        case .apiError(let error):
            return error.message
        case .unknown(let error):
            return "Неизвестная ошибка: \(error.localizedDescription)"
        }
    }
}

struct APIError: Codable {
    let code: String
    let message: String
    let details: [String: String]?
}

// Сетевой клиент с обработкой ошибок
final class NetworkClient {
    private let session: URLSession
    private let decoder: JSONDecoder

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        let request = try endpoint.urlRequest()

        let data: Data
        let response: URLResponse

        do {
            (data, response) = try await session.data(for: request)
        } catch let error as URLError {
            throw mapURLError(error)
        }

        guard let httpResponse = response as? HTTPURLResponse else {
            throw NetworkError.invalidResponse
        }

        try validateResponse(httpResponse, data: data)

        do {
            return try decoder.decode(T.self, from: data)
        } catch {
            throw NetworkError.decodingError(error)
        }
    }

    private func mapURLError(_ error: URLError) -> NetworkError {
        switch error.code {
        case .notConnectedToInternet, .networkConnectionLost:
            return .noConnection
        case .timedOut:
            return .timeout
        default:
            return .unknown(error)
        }
    }

    private func validateResponse(_ response: HTTPURLResponse, data: Data) throws {
        switch response.statusCode {
        case 200...299:
            return
        case 401:
            throw NetworkError.unauthorized
        case 403:
            throw NetworkError.forbidden
        case 404:
            throw NetworkError.notFound
        case 400...499:
            if let apiError = try? decoder.decode(APIError.self, from: data) {
                throw NetworkError.apiError(apiError)
            }
            throw NetworkError.unknown(NSError(domain: "", code: response.statusCode))
        case 500...599:
            throw NetworkError.serverError(response.statusCode)
        default:
            throw NetworkError.invalidResponse
        }
    }
}
```

### Kotlin: Result и sealed class

```kotlin
// Sealed class для результата
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: NetworkException) : NetworkResult<Nothing>()
}

// Иерархия исключений
sealed class NetworkException : Exception() {
    object NoConnection : NetworkException()
    object Timeout : NetworkException()
    object Unauthorized : NetworkException()
    object Forbidden : NetworkException()
    object NotFound : NetworkException()
    data class ServerError(val code: Int) : NetworkException()
    data class ApiError(val error: ApiErrorResponse) : NetworkException()
    data class Unknown(override val cause: Throwable) : NetworkException()
}

@Serializable
data class ApiErrorResponse(
    val code: String,
    val message: String,
    val details: Map<String, String>? = null
)

// Repository с обработкой ошибок
class UserRepository(
    private val api: UserApi,
    private val json: Json
) {
    suspend fun getUsers(): NetworkResult<List<User>> {
        return safeApiCall { api.getUsers() }
    }

    private suspend fun <T> safeApiCall(
        call: suspend () -> T
    ): NetworkResult<T> {
        return try {
            NetworkResult.Success(call())
        } catch (e: Exception) {
            NetworkResult.Error(mapException(e))
        }
    }

    private fun mapException(e: Exception): NetworkException {
        return when (e) {
            is HttpException -> mapHttpException(e)
            is IOException -> {
                when {
                    e.message?.contains("timeout", ignoreCase = true) == true ->
                        NetworkException.Timeout
                    else -> NetworkException.NoConnection
                }
            }
            else -> NetworkException.Unknown(e)
        }
    }

    private fun mapHttpException(e: HttpException): NetworkException {
        return when (e.code()) {
            401 -> NetworkException.Unauthorized
            403 -> NetworkException.Forbidden
            404 -> NetworkException.NotFound
            in 500..599 -> NetworkException.ServerError(e.code())
            else -> {
                val errorBody = e.response()?.errorBody()?.string()
                if (errorBody != null) {
                    try {
                        val apiError = json.decodeFromString<ApiErrorResponse>(errorBody)
                        NetworkException.ApiError(apiError)
                    } catch (_: Exception) {
                        NetworkException.Unknown(e)
                    }
                } else {
                    NetworkException.Unknown(e)
                }
            }
        }
    }
}

// Использование в ViewModel
class UsersViewModel(private val repository: UserRepository) : ViewModel() {
    private val _state = MutableStateFlow<UsersState>(UsersState.Loading)
    val state: StateFlow<UsersState> = _state.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _state.value = UsersState.Loading

            when (val result = repository.getUsers()) {
                is NetworkResult.Success -> {
                    _state.value = UsersState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _state.value = UsersState.Error(
                        message = mapErrorMessage(result.exception)
                    )
                }
            }
        }
    }

    private fun mapErrorMessage(e: NetworkException): String {
        return when (e) {
            is NetworkException.NoConnection -> "Нет подключения к интернету"
            is NetworkException.Timeout -> "Превышено время ожидания"
            is NetworkException.Unauthorized -> "Требуется авторизация"
            is NetworkException.Forbidden -> "Доступ запрещён"
            is NetworkException.NotFound -> "Данные не найдены"
            is NetworkException.ServerError -> "Ошибка сервера: ${e.code}"
            is NetworkException.ApiError -> e.error.message
            is NetworkException.Unknown -> "Неизвестная ошибка"
        }
    }
}
```

---

## 5. Интерцепторы и модификация запросов

### Swift: URLProtocol (сложный способ)

```swift
// Кастомный URLProtocol для логирования
class LoggingURLProtocol: URLProtocol {
    private static let handledKey = "LoggingURLProtocolHandled"

    override class func canInit(with request: URLRequest) -> Bool {
        guard URLProtocol.property(
            forKey: handledKey,
            in: request
        ) == nil else {
            return false
        }
        return true
    }

    override class func canonicalRequest(for request: URLRequest) -> URLRequest {
        return request
    }

    override func startLoading() {
        guard let mutableRequest = (request as NSURLRequest).mutableCopy() as? NSMutableURLRequest else {
            return
        }

        URLProtocol.setProperty(true, forKey: Self.handledKey, in: mutableRequest)

        // Логируем запрос
        logRequest(mutableRequest as URLRequest)

        let task = URLSession.shared.dataTask(with: mutableRequest as URLRequest) { data, response, error in
            if let error = error {
                self.client?.urlProtocol(self, didFailWithError: error)
                return
            }

            if let response = response {
                self.logResponse(response, data: data)
                self.client?.urlProtocol(self, didReceive: response, cacheStoragePolicy: .allowed)
            }

            if let data = data {
                self.client?.urlProtocol(self, didLoad: data)
            }

            self.client?.urlProtocolDidFinishLoading(self)
        }
        task.resume()
    }

    override func stopLoading() {}

    private func logRequest(_ request: URLRequest) {
        print("➡️ \(request.httpMethod ?? "GET") \(request.url?.absoluteString ?? "")")
        request.allHTTPHeaderFields?.forEach { print("   \($0): \($1)") }
    }

    private func logResponse(_ response: URLResponse, data: Data?) {
        guard let httpResponse = response as? HTTPURLResponse else { return }
        print("⬅️ \(httpResponse.statusCode) \(response.url?.absoluteString ?? "")")
    }
}

// Более простой подход: обёртка над URLSession
final class APIClient {
    private let session: URLSession
    private var authToken: String?

    func request<T: Decodable>(_ endpoint: Endpoint) async throws -> T {
        var request = try endpoint.urlRequest()

        // Добавляем заголовки ко всем запросам
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("iOS/1.0", forHTTPHeaderField: "User-Agent")

        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        // Логирование
        logRequest(request)

        let (data, response) = try await session.data(for: request)

        // Логирование ответа
        logResponse(response, data: data)

        return try JSONDecoder.apiDecoder.decode(T.self, from: data)
    }
}
```

### Kotlin: OkHttp Interceptors (простой способ)

```kotlin
// Interceptor для логирования
class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()

        val startTime = System.nanoTime()
        println("➡️ ${request.method} ${request.url}")
        request.headers.forEach { (name, value) ->
            println("   $name: $value")
        }

        val response = chain.proceed(request)

        val duration = (System.nanoTime() - startTime) / 1_000_000
        println("⬅️ ${response.code} ${request.url} (${duration}ms)")

        return response
    }
}

// Interceptor для авторизации
class AuthInterceptor(
    private val tokenProvider: TokenProvider
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()

        val token = tokenProvider.getToken()
        if (token == null) {
            return chain.proceed(originalRequest)
        }

        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()

        return chain.proceed(authenticatedRequest)
    }
}

// Interceptor для повторных попыток
class RetryInterceptor(
    private val maxRetries: Int = 3
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        var response: Response? = null
        var exception: IOException? = null

        repeat(maxRetries) { attempt ->
            try {
                response?.close()
                response = chain.proceed(request)

                if (response!!.isSuccessful) {
                    return response!!
                }

                // Retry on 5xx errors
                if (response!!.code in 500..599 && attempt < maxRetries - 1) {
                    Thread.sleep(1000L * (attempt + 1)) // Exponential backoff
                    return@repeat
                }

                return response!!
            } catch (e: IOException) {
                exception = e
                if (attempt < maxRetries - 1) {
                    Thread.sleep(1000L * (attempt + 1))
                }
            }
        }

        throw exception ?: IOException("Unknown error")
    }
}

// Authenticator для обновления токена
class TokenAuthenticator(
    private val tokenManager: TokenManager
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        // Не пытаемся обновить, если уже пробовали
        if (response.request.header("X-Retry-Auth") != null) {
            return null
        }

        synchronized(this) {
            val newToken = tokenManager.refreshToken() ?: return null

            return response.request.newBuilder()
                .header("Authorization", "Bearer $newToken")
                .header("X-Retry-Auth", "true")
                .build()
        }
    }
}

// Собираем OkHttpClient
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(LoggingInterceptor())
    .addInterceptor(AuthInterceptor(tokenProvider))
    .addInterceptor(RetryInterceptor())
    .authenticator(TokenAuthenticator(tokenManager))
    .connectTimeout(30, TimeUnit.SECONDS)
    .readTimeout(30, TimeUnit.SECONDS)
    .cache(Cache(cacheDir, 10 * 1024 * 1024)) // 10 MB
    .build()
```

---

## 6. KMP: Ktor для кроссплатформенного networking

### Общая архитектура Ktor

```
┌─────────────────────────────────────────────┐
│            Общий код (commonMain)           │
│  ┌───────────────────────────────────────┐  │
│  │           Ktor HttpClient             │  │
│  │  - Конфигурация                       │  │
│  │  - Плагины (Auth, Logging, etc)       │  │
│  │  - API-интерфейсы                     │  │
│  └───────────────────────────────────────┘  │
├─────────────────────────────────────────────┤
│  iosMain          │         androidMain     │
│  ┌─────────────┐  │  ┌───────────────────┐  │
│  │ Darwin      │  │  │ OkHttp / Android  │  │
│  │ Engine      │  │  │ Engine            │  │
│  └─────────────┘  │  └───────────────────┘  │
└─────────────────────────────────────────────┘
```

### Общий код (commonMain)

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("io.ktor:ktor-client-core:2.3.7")
            implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
            implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")
            implementation("io.ktor:ktor-client-auth:2.3.7")
            implementation("io.ktor:ktor-client-logging:2.3.7")
        }

        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:2.3.7")
        }

        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:2.3.7")
        }
    }
}

// ApiClient.kt (commonMain)
class ApiClient(engine: HttpClientEngine) {
    private val client = HttpClient(engine) {
        install(ContentNegotiation) {
            json(Json {
                ignoreUnknownKeys = true
                isLenient = true
                encodeDefaults = false
            })
        }

        install(Logging) {
            logger = object : Logger {
                override fun log(message: String) {
                    println("HTTP: $message")
                }
            }
            level = LogLevel.HEADERS
        }

        install(Auth) {
            bearer {
                loadTokens {
                    BearerTokens(
                        accessToken = tokenStorage.getAccessToken() ?: "",
                        refreshToken = tokenStorage.getRefreshToken() ?: ""
                    )
                }

                refreshTokens {
                    val response = client.post("auth/refresh") {
                        setBody(RefreshRequest(oldTokens?.refreshToken ?: ""))
                    }.body<TokenResponse>()

                    tokenStorage.saveTokens(response.accessToken, response.refreshToken)

                    BearerTokens(response.accessToken, response.refreshToken)
                }
            }
        }

        install(HttpTimeout) {
            requestTimeoutMillis = 30_000
            connectTimeoutMillis = 10_000
        }

        defaultRequest {
            url("https://api.example.com/")
            contentType(ContentType.Application.Json)
        }
    }

    // API методы
    suspend fun getUsers(): List<User> {
        return client.get("users").body()
    }

    suspend fun createUser(request: CreateUserRequest): User {
        return client.post("users") {
            setBody(request)
        }.body()
    }

    suspend fun updateUser(id: String, request: UpdateUserRequest): User {
        return client.put("users/$id") {
            setBody(request)
        }.body()
    }

    suspend fun deleteUser(id: String) {
        client.delete("users/$id")
    }

    suspend fun uploadAvatar(userId: String, imageBytes: ByteArray): AvatarResponse {
        return client.submitFormWithBinaryData(
            url = "users/$userId/avatar",
            formData = formData {
                append("avatar", imageBytes, Headers.build {
                    append(HttpHeaders.ContentType, "image/jpeg")
                    append(HttpHeaders.ContentDisposition, "filename=avatar.jpg")
                })
            }
        ).body()
    }
}

// Модели (commonMain)
@Serializable
data class User(
    val id: String,
    val email: String,
    @SerialName("display_name")
    val displayName: String,
    @SerialName("created_at")
    val createdAt: String,
    val profile: UserProfile? = null
)

@Serializable
data class CreateUserRequest(
    val email: String,
    @SerialName("display_name")
    val displayName: String,
    val password: String
)
```

### Платформенные реализации

```kotlin
// androidMain
actual fun createHttpEngine(): HttpClientEngine {
    return OkHttp.create {
        config {
            connectTimeout(30, TimeUnit.SECONDS)
            readTimeout(30, TimeUnit.SECONDS)
        }

        addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .header("X-Platform", "Android")
                .build()
            chain.proceed(request)
        }
    }
}

// iosMain
actual fun createHttpEngine(): HttpClientEngine {
    return Darwin.create {
        configureRequest {
            setAllowsCellularAccess(true)
        }

        configureSession {
            // URLSessionConfiguration
        }
    }
}
```

### Обработка ошибок в Ktor

```kotlin
// commonMain
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val exception: ApiException) : ApiResult<Nothing>()
}

sealed class ApiException : Exception() {
    object NetworkError : ApiException()
    object Timeout : ApiException()
    data class HttpError(val code: Int, val message: String) : ApiException()
    data class ServerError(val error: ApiErrorResponse) : ApiException()
    object Unknown : ApiException()
}

// Extension для безопасных вызовов
suspend inline fun <reified T> HttpClient.safeGet(
    urlString: String,
    block: HttpRequestBuilder.() -> Unit = {}
): ApiResult<T> {
    return safeApiCall {
        get(urlString, block).body()
    }
}

suspend inline fun <T> safeApiCall(
    crossinline call: suspend () -> T
): ApiResult<T> {
    return try {
        ApiResult.Success(call())
    } catch (e: Exception) {
        ApiResult.Error(mapException(e))
    }
}

fun mapException(e: Exception): ApiException {
    return when (e) {
        is ClientRequestException -> {
            when (e.response.status.value) {
                401 -> ApiException.HttpError(401, "Unauthorized")
                403 -> ApiException.HttpError(403, "Forbidden")
                404 -> ApiException.HttpError(404, "Not Found")
                else -> ApiException.HttpError(e.response.status.value, e.message ?: "")
            }
        }
        is ServerResponseException -> {
            ApiException.HttpError(e.response.status.value, "Server Error")
        }
        is HttpRequestTimeoutException -> ApiException.Timeout
        is IOException -> ApiException.NetworkError
        else -> ApiException.Unknown
    }
}
```

---

## 7. Шесть типичных ошибок

### Ошибка 1: Игнорирование отмены запросов

```swift
// ❌ ПЛОХО: запрос продолжается после ухода с экрана
class BadViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()
        Task {
            let users = try await api.fetchUsers()
            tableView.reloadData() // Может вызваться после dealloc!
        }
    }
}

// ✅ ХОРОШО: запрос отменяется при уходе с экрана
class GoodViewController: UIViewController {
    private var loadTask: Task<Void, Never>?

    override func viewDidLoad() {
        super.viewDidLoad()
        loadTask = Task {
            do {
                let users = try await api.fetchUsers()
                guard !Task.isCancelled else { return }
                tableView.reloadData()
            } catch {
                // handle error
            }
        }
    }

    override func viewDidDisappear(_ animated: Bool) {
        super.viewDidDisappear(animated)
        loadTask?.cancel()
    }
}
```

```kotlin
// ❌ ПЛОХО: использование GlobalScope
class BadViewModel : ViewModel() {
    fun loadUsers() {
        GlobalScope.launch { // Утечка! Не отменится при уничтожении ViewModel
            val users = api.getUsers()
            _state.value = users
        }
    }
}

// ✅ ХОРОШО: использование viewModelScope
class GoodViewModel : ViewModel() {
    fun loadUsers() {
        viewModelScope.launch { // Автоматически отменится
            val users = api.getUsers()
            _state.value = users
        }
    }
}
```

### Ошибка 2: Блокирование главного потока

```swift
// ❌ ПЛОХО: синхронный вызов на main thread
func loadDataBad() {
    let data = try! Data(contentsOf: url) // Блокирует UI!
    process(data)
}

// ✅ ХОРОШО: асинхронный вызов
func loadDataGood() async {
    let (data, _) = try await URLSession.shared.data(from: url)
    await MainActor.run {
        process(data)
    }
}
```

```kotlin
// ❌ ПЛОХО: сетевой вызов на Main dispatcher
fun loadDataBad() {
    lifecycleScope.launch { // По умолчанию Main!
        val response = URL(url).readText() // NetworkOnMainThreadException!
    }
}

// ✅ ХОРОШО: IO dispatcher для сети
fun loadDataGood() {
    lifecycleScope.launch {
        val data = withContext(Dispatchers.IO) {
            api.fetchData()
        }
        updateUI(data) // Обратно на Main
    }
}
```

### Ошибка 3: Отсутствие обработки ошибок сериализации

```swift
// ❌ ПЛОХО: force unwrap
let user = try! JSONDecoder().decode(User.self, from: data)

// ✅ ХОРОШО: правильная обработка
do {
    let user = try JSONDecoder().decode(User.self, from: data)
    handleSuccess(user)
} catch let DecodingError.keyNotFound(key, context) {
    print("Отсутствует ключ '\(key.stringValue)': \(context.debugDescription)")
} catch let DecodingError.typeMismatch(type, context) {
    print("Неверный тип \(type): \(context.debugDescription)")
} catch {
    print("Ошибка декодирования: \(error)")
}
```

```kotlin
// ❌ ПЛОХО: игнорирование SerializationException
val user = json.decodeFromString<User>(jsonString) // Может упасть!

// ✅ ХОРОШО: обработка ошибок
try {
    val user = json.decodeFromString<User>(jsonString)
    handleSuccess(user)
} catch (e: SerializationException) {
    handleError("Ошибка парсинга: ${e.message}")
} catch (e: IllegalArgumentException) {
    handleError("Некорректные данные: ${e.message}")
}
```

### Ошибка 4: Хардкод URL и отсутствие конфигурации

```swift
// ❌ ПЛОХО: захардкоженные URL
let url = URL(string: "https://api.production.com/users")!

// ✅ ХОРОШО: конфигурируемый base URL
enum Environment {
    case development, staging, production

    var baseURL: URL {
        switch self {
        case .development: return URL(string: "https://dev-api.example.com")!
        case .staging: return URL(string: "https://staging-api.example.com")!
        case .production: return URL(string: "https://api.example.com")!
        }
    }
}

class APIConfig {
    static let current: Environment = {
        #if DEBUG
        return .development
        #else
        return .production
        #endif
    }()
}
```

```kotlin
// ❌ ПЛОХО
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.production.com/")
    .build()

// ✅ ХОРОШО
object ApiConfig {
    val baseUrl: String = when (BuildConfig.BUILD_TYPE) {
        "debug" -> "https://dev-api.example.com/"
        "staging" -> "https://staging-api.example.com/"
        else -> "https://api.example.com/"
    }
}

val retrofit = Retrofit.Builder()
    .baseUrl(ApiConfig.baseUrl)
    .build()
```

### Ошибка 5: Отсутствие retry-логики

```swift
// ❌ ПЛОХО: один запрос, один шанс
func fetchData() async throws -> Data {
    return try await URLSession.shared.data(from: url).0
}

// ✅ ХОРОШО: retry с exponential backoff
func fetchDataWithRetry(
    maxAttempts: Int = 3,
    initialDelay: TimeInterval = 1.0
) async throws -> Data {
    var lastError: Error?

    for attempt in 0..<maxAttempts {
        do {
            return try await URLSession.shared.data(from: url).0
        } catch {
            lastError = error

            // Не повторяем при отмене или клиентских ошибках
            if Task.isCancelled { throw error }
            if let urlError = error as? URLError,
               urlError.code == .cancelled { throw error }

            let delay = initialDelay * pow(2.0, Double(attempt))
            try await Task.sleep(nanoseconds: UInt64(delay * 1_000_000_000))
        }
    }

    throw lastError ?? NetworkError.unknown
}
```

### Ошибка 6: Неправильное кэширование

```swift
// ❌ ПЛОХО: кэширование без контроля
// URLSession кэширует всё подряд по умолчанию

// ✅ ХОРОШО: контролируемое кэширование
let config = URLSessionConfiguration.default
config.urlCache = URLCache(
    memoryCapacity: 50 * 1024 * 1024,  // 50 MB
    diskCapacity: 100 * 1024 * 1024     // 100 MB
)
config.requestCachePolicy = .returnCacheDataElseLoad

// Для конкретного запроса
var request = URLRequest(url: url)
request.cachePolicy = .reloadIgnoringLocalCacheData // Не кэшировать
```

```kotlin
// ❌ ПЛОХО: кэш без ограничений и очистки

// ✅ ХОРОШО: настроенный кэш
val cache = Cache(
    directory = context.cacheDir.resolve("http_cache"),
    maxSize = 50L * 1024 * 1024 // 50 MB
)

val client = OkHttpClient.Builder()
    .cache(cache)
    .addNetworkInterceptor { chain ->
        val response = chain.proceed(chain.request())
        val cacheControl = CacheControl.Builder()
            .maxAge(10, TimeUnit.MINUTES)
            .build()
        response.newBuilder()
            .header("Cache-Control", cacheControl.toString())
            .build()
    }
    .build()
```

---

## 8. Три ментальные модели

### Модель 1: "Слоёный пирог" (Layered Cake)

```
Представьте сетевой стек как слоёный торт:

iOS:                              Android:
┌─────────────────────┐          ┌─────────────────────┐
│   Ваш код (ViewModel)│          │   Ваш код (ViewModel)│
├─────────────────────┤          ├─────────────────────┤
│   Repository        │          │   Repository        │
├─────────────────────┤          ├─────────────────────┤
│   APIClient         │          │   Retrofit          │
├─────────────────────┤          ├─────────────────────┤
│   URLSession        │          │   OkHttp            │
├─────────────────────┤          ├─────────────────────┤
│   CFNetwork         │          │   Socket            │
└─────────────────────┘          └─────────────────────┘

Каждый слой:
- Имеет одну ответственность
- Зависит только от слоя ниже
- Можно заменить независимо от других
- Тестируется отдельно

Правило: чем выше слой, тем проще его мокать для тестов.
```

### Модель 2: "Конвейер запросов" (Request Pipeline)

```
Запрос проходит через конвейер модификаций:

         ┌─────────┐
         │ Request │
         └────┬────┘
              ▼
    ┌─────────────────┐
    │ Add Auth Header │  ← Interceptor 1
    └────────┬────────┘
              ▼
    ┌─────────────────┐
    │ Add Logging     │  ← Interceptor 2
    └────────┬────────┘
              ▼
    ┌─────────────────┐
    │ Add Cache       │  ← Interceptor 3
    └────────┬────────┘
              ▼
         ┌─────────┐
         │ Network │
         └────┬────┘
              ▼
         ┌──────────┐
         │ Response │
         └────┬─────┘
              ▼
    ┌─────────────────┐
    │ Parse JSON      │  ← Reverse
    └────────┬────────┘
              ▼
    ┌─────────────────┐
    │ Handle Errors   │
    └────────┬────────┘
              ▼
         ┌────────┐
         │ Result │
         └────────┘

iOS: URLProtocol — сложная вставка в конвейер
Android: OkHttp Interceptors — простое добавление звеньев
```

### Модель 3: "Контракт и реализация" (Contract-First)

```
Retrofit использует контрактный подход:

КОНТРАКТ (интерфейс):
┌──────────────────────────────────────────┐
│ interface UserApi {                       │
│     @GET("users")                         │
│     suspend fun getUsers(): List<User>    │
│ }                                         │
└──────────────────────────────────────────┘
              │
              ▼ Retrofit генерирует
┌──────────────────────────────────────────┐
│         РЕАЛИЗАЦИЯ                        │
│  - Создание Request                       │
│  - Вызов OkHttp                          │
│  - Парсинг Response                       │
│  - Обработка ошибок                       │
└──────────────────────────────────────────┘

URLSession использует императивный подход:
┌──────────────────────────────────────────┐
│ func getUsers() async throws -> [User] { │
│     var request = URLRequest(url: ...)   │ ← Вручную
│     request.httpMethod = "GET"           │ ← Вручную
│     let (data, _) = try await ...        │ ← Вручную
│     return try decode(data)              │ ← Вручную
│ }                                         │
└──────────────────────────────────────────┘

Контрактный подход:
✅ Меньше кода
✅ Единообразие
✅ Автогенерация

Императивный подход:
✅ Полный контроль
✅ Гибкость
✅ Нет "магии"
```

---

## 9. Quiz: проверь понимание

### Вопрос 1: Interceptors vs URLProtocol

Почему в Android добавить логирование запросов проще, чем в iOS?

<details>
<summary>Ответ</summary>

**OkHttp Interceptors** — это цепочка обработчиков, где каждый может модифицировать запрос/ответ. Добавление нового — одна строка:

```kotlin
client.addInterceptor(LoggingInterceptor())
```

**URLProtocol** в iOS требует:
1. Создать подкласс URLProtocol
2. Реализовать canInit, startLoading, stopLoading
3. Зарегистрировать протокол
4. Избежать бесконечной рекурсии (пометить обработанные запросы)

Это фундаментальное архитектурное различие: OkHttp проектировался с учётом расширяемости, URLSession — нет.

</details>

### Вопрос 2: Почему Ktor использует разные engine?

Зачем Ktor нужны разные engine для iOS (Darwin) и Android (OkHttp)?

<details>
<summary>Ответ</summary>

Kotlin Multiplatform компилируется в **нативный код** для каждой платформы:
- iOS: компилируется в native binary через Kotlin/Native
- Android: компилируется в JVM bytecode

**Darwin engine** использует нативный URLSession iOS — это:
- Интеграция с системой (VPN, прокси, сертификаты)
- Оптимальная производительность
- Поддержка App Transport Security

**OkHttp engine** на Android:
- Проверенная библиотека с огромным сообществом
- HTTP/2 поддержка
- Connection pooling
- Прозрачное сжатие

Ktor абстрагирует различия, давая единый API.

</details>

### Вопрос 3: Codable vs kotlinx.serialization

В чём ключевое отличие Codable от kotlinx.serialization в плане реализации?

<details>
<summary>Ответ</summary>

**Codable** — протокол языка Swift:
- Компилятор автоматически синтезирует реализацию
- Часть стандартной библиотеки
- Работает "из коробки" без зависимостей

**kotlinx.serialization** — плагин компилятора:
- Требует подключения Gradle-плагина
- Генерирует код сериализации на этапе компиляции
- Отдельная библиотека от JetBrains

Оба решения:
- НЕ используют рефлексию (compile-time)
- Поддерживают кастомизацию
- Высокопроизводительны

Практическое различие: kotlinx.serialization лучше работает с Kotlin Multiplatform и поддерживает больше форматов (JSON, Protobuf, CBOR).

</details>

---

## 10. Связанные заметки

- [[ios-networking]] — Детальный разбор URLSession, Combine, async/await для сетевых запросов
- [[android-networking]] — OkHttp, Retrofit, корутины и Flow для Android

---

## Ссылки

- [Apple URLSession Documentation](https://developer.apple.com/documentation/foundation/urlsession)
- [OkHttp](https://square.github.io/okhttp/)
- [Retrofit](https://square.github.io/retrofit/)
- [Ktor Client](https://ktor.io/docs/client.html)
- [kotlinx.serialization](https://github.com/Kotlin/kotlinx.serialization)

---

## Связь с другими темами

**[[android-networking]]** — OkHttp и Retrofit являются де-факто стандартом для сетевых запросов на Android. Заметка подробно разбирает interceptors, connection pooling, certificate pinning и интеграцию с Coroutines/Flow. Понимание архитектуры OkHttp (цепочка interceptors) помогает оценить, почему Ktor Client на Android использует OkHttp как engine и какие возможности это открывает.

**[[ios-networking]]** — URLSession — это мощный, но низкоуровневый API, который Apple предоставляет «из коробки». Заметка раскрывает URLSessionConfiguration, background downloads, URLProtocol для мокирования и интеграцию с async/await и Combine. Сравнение с Android в текущем файле показывает, что iOS не имеет стандартного аналога Retrofit, что приводит к использованию сторонних решений (Alamofire, Moya) или ручных абстракций.

**[[network-http-evolution]]** — Эволюция HTTP (1.0 → 1.1 → 2 → 3/QUIC) одинаково затрагивает обе платформы, но поддержка различается. Заметка объясняет multiplexing, server push и header compression, что помогает понять, почему HTTP/2 на iOS (через URLSession) и Android (через OkHttp) может демонстрировать разную производительность. Это фундаментальное знание для оптимизации сетевого слоя в кросс-платформенных приложениях.

---

## Источники и дальнейшее чтение

- **Meier R. (2022). *Professional Android*.** — Описывает сетевой стек Android: OkHttp, Retrofit, WorkManager для фоновых загрузок и best practices для работы с REST API. Помогает понять, как Android-подход к networking отличается от iOS.
- **Neuburg M. (2023). *iOS Programming Fundamentals*.** — Раскрывает URLSession, URLRequest, JSON-декодирование через Codable и async/await для сетевых запросов. Даёт фундамент для понимания iOS-подхода к networking.
- **Moskala M. (2021). *Effective Kotlin*.** — Содержит рекомендации по работе с корутинами, Flow и обработке ошибок, что напрямую применяется при проектировании сетевого слоя в Ktor Client для KMP-приложений.

---

## Проверь себя

> [!question]- Почему iOS не имеет стандартного аналога Retrofit, и как это влияет на архитектуру сетевого слоя?
> URLSession -- низкоуровневый API: настройка request, получение response, обработка ошибок. Apple не предоставляет декларативного API для определения endpoints (как Retrofit с аннотациями @GET/@POST). Следствие: iOS-разработчики либо пишут свой network layer (protocol + extensions), либо используют Alamofire/Moya. В KMP-проектах Ktor Client решает эту проблему, предоставляя единый API для обеих платформ с platform-specific engines (URLSession на iOS, OkHttp на Android).

> [!question]- Сценарий: приложение делает 10 параллельных API-запросов при загрузке экрана. На медленном соединении это вызывает timeout. Как оптимизировать?
> Проблемы: 1) connection limit (iOS: 6 per host, Android/OkHttp: 5 per host) -- избыточные запросы ждут в очереди, 2) каждый запрос = handshake overhead. Оптимизации: 1) HTTP/2 multiplexing -- все запросы через одно соединение, 2) batch API endpoint -- объединить 10 запросов в один, 3) приоритезация -- критические запросы первыми, декоративные ленивые, 4) кэширование -- Cache-Control headers, conditional requests (ETag/If-None-Match), 5) GraphQL -- один запрос с точно нужными данными.

> [!question]- Почему certificate pinning важен для мобильных приложений и как реализация отличается на iOS и Android?
> Certificate pinning предотвращает MITM-атаки: приложение доверяет только конкретному сертификату/public key, а не всей chain. Без pinning: любой CA-signed сертификат будет принят (корпоративный proxy может перехватить). iOS: URLSessionDelegate с didReceiveChallenge, сравнение SecTrust с pinned certificate. Android: OkHttp CertificatePinner или Network Security Config (XML). KMP: Ktor конфигурация engine-specific (OkHttp pinner на Android, URLSession delegate на iOS). Ограничение: при ротации сертификатов нужно обновлять приложение.

> [!question]- Как Ktor Client решает проблему разных сетевых стеков на iOS и Android в KMP?
> Ktor Client: единый API в commonMain (HttpClient, request builders, serialization). Platform engines: CIO (Kotlin coroutines, any platform), OkHttp (Android, connection pooling), Darwin (iOS, NSURLSession). Engine абстрагирует: TLS, connection management, HTTP/2 support. Serialization: kotlinx.serialization в commonMain. Interceptors: Ktor plugins (Logging, Auth, ContentNegotiation) работают на всех платформах. Trade-off: менее гибкий, чем нативные APIs (нет доступа к OkHttp interceptors из commonMain).

---

## Ключевые карточки

Чем URLSession (iOS) отличается от OkHttp/Retrofit (Android)?
?
URLSession: системный API, async (delegate/completion handler/async-await), URLSessionConfiguration (default/ephemeral/background), URLProtocol для intercepting. OkHttp: interceptor chain, connection pooling, HTTP/2, transparent compression. Retrofit: декларативные endpoints через interface + annotations. iOS не имеет Retrofit-аналога из коробки -- URLSession ближе к OkHttp по уровню абстракции.

Как работает Ktor Client в KMP-проектах?
?
commonMain: HttpClient с plugins (ContentNegotiation, Auth, Logging), request через get/post DSL, kotlinx.serialization для JSON. Platform engines: OkHttp (Android), Darwin (iOS NSURLSession), CIO (pure Kotlin). Конфигурация engine-specific: timeouts, SSL, proxy. Единый API для всех платформ с platform-optimized networking.

Что такое certificate pinning и зачем он нужен?
?
Certificate pinning -- привязка приложения к конкретному серверному сертификату/public key. Предотвращает MITM-атаки через rogue CA certificates. iOS: URLAuthenticationChallenge в delegate. Android: OkHttp CertificatePinner или Network Security Config. Важно: pin public key (не certificate), чтобы ротация сертификата не требовала обновления приложения.

Какие стратегии кэширования HTTP-ответов используются на мобильных платформах?
?
iOS: URLCache (disk + memory), URLSession автоматически использует Cache-Control headers. Android: OkHttp Cache (disk), Interceptor для custom caching. Обе: ETag/If-None-Match для conditional requests (304 Not Modified). Offline-first: кэш в БД (Room/Core Data) + network request для обновления. KMP: Ktor client caching plugin или manual cache в SQLDelight.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-data-persistence]] | Persistence -- хранение данных, полученных по сети |
| Углубиться | [[android-networking]] | OkHttp, Retrofit, interceptors из раздела Android |
| Смежная тема | [[network-http-evolution]] | HTTP/1.1 -> HTTP/2 -> HTTP/3 из раздела Networking |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |
