---
title: "Сеть: Retrofit, OkHttp, Ktor"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [http-protocol, tcp-ip, connection-pooling, serialization]
tags:
  - android
  - networking
  - retrofit
  - okhttp
  - ktor
related:
  - "[[android-overview]]"
  - "[[android-threading]]"
  - "[[android-architecture-patterns]]"
  - "[[android-rxjava]]"
  - "[[android-coroutines-mistakes]]"
  - "[[kotlin-coroutines]]"
  - "[[networking-overview]]"
  - "[[network-http-evolution]]"
  - "[[network-realtime-protocols]]"
  - "[[network-bluetooth]]"
  - "[[network-cellular]]"
  - "[[network-wireless-iot]]"
---

# Сеть: Retrofit, OkHttp, Ktor

Сетевые запросы в Android требуют асинхронного выполнения (Main Thread нельзя блокировать). **Retrofit** — declarative HTTP-клиент поверх **OkHttp**, который генерирует реализацию API по интерфейсу. **Ktor** — Kotlin-native альтернатива для multiplatform проектов.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android
> - [[android-threading]] — почему сеть нельзя в Main Thread
> - [[kotlin-coroutines]] — suspend функции для async запросов
> - Базовое понимание HTTP (методы, статусы, заголовки)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Retrofit** | Type-safe HTTP client для Android |
| **OkHttp** | HTTP client низкого уровня |
| **Interceptor** | Middleware для модификации запросов/ответов |
| **Converter** | Преобразование JSON ↔ объекты |
| **Ktor Client** | Kotlin-native HTTP client |

---

## Почему Retrofit, а не HttpURLConnection?

### Проблема: сетевые запросы вручную

```kotlin
// ❌ Работа с HttpURLConnection — типичный код
class ApiClient {

    fun getUsers(): List<User> {
        val url = URL("https://api.example.com/users")
        val connection = url.openConnection() as HttpURLConnection

        try {
            // Настройка соединения
            connection.requestMethod = "GET"
            connection.setRequestProperty("Accept", "application/json")
            connection.setRequestProperty("Authorization", "Bearer $token")
            connection.connectTimeout = 30000
            connection.readTimeout = 30000

            // Проверка ответа
            if (connection.responseCode != HttpURLConnection.HTTP_OK) {
                throw IOException("HTTP error: ${connection.responseCode}")
            }

            // Чтение ответа
            val reader = BufferedReader(InputStreamReader(connection.inputStream))
            val response = StringBuilder()
            var line: String?
            while (reader.readLine().also { line = it } != null) {
                response.append(line)
            }
            reader.close()

            // Парсинг JSON вручную
            val jsonArray = JSONArray(response.toString())
            val users = mutableListOf<User>()
            for (i in 0 until jsonArray.length()) {
                val obj = jsonArray.getJSONObject(i)
                users.add(User(
                    id = obj.getLong("id"),
                    name = obj.getString("name"),
                    email = obj.getString("email")
                ))
            }
            return users

        } finally {
            connection.disconnect()
        }
    }

    fun createUser(user: CreateUserRequest): User {
        val url = URL("https://api.example.com/users")
        val connection = url.openConnection() as HttpURLConnection

        try {
            connection.requestMethod = "POST"
            connection.setRequestProperty("Content-Type", "application/json")
            connection.setRequestProperty("Authorization", "Bearer $token")
            connection.doOutput = true

            // Сериализация вручную
            val jsonBody = JSONObject().apply {
                put("name", user.name)
                put("email", user.email)
            }.toString()

            // Отправка тела
            val outputStream = BufferedOutputStream(connection.outputStream)
            outputStream.write(jsonBody.toByteArray())
            outputStream.flush()
            outputStream.close()

            // ... обработка ответа (ещё 30 строк)
        } finally {
            connection.disconnect()
        }
    }

    // Для каждого endpoint — копипаста ~50 строк кода
    // 10 endpoints = 500 строк boilerplate
}
```

### Что не так с этим подходом

| Проблема | Описание |
|----------|----------|
| **Boilerplate** | ~50 строк на каждый endpoint |
| **Дублирование** | Headers, таймауты, обработка ошибок — везде одинаково |
| **Ручной парсинг JSON** | JSONObject/JSONArray — много кода, легко ошибиться |
| **Нет type-safety** | `getString("naem")` — опечатка = crash в runtime |
| **Сложно тестировать** | Нужен реальный сервер или мок всего HttpURLConnection |
| **Нет retry/caching** | Нужно писать самому |
| **Логирование** | Нужен отдельный код для debug |

### Как Retrofit решает эти проблемы

```kotlin
// ✅ Retrofit — декларативный подход

// Весь API описывается интерфейсом
interface ApiService {

    @GET("users")
    suspend fun getUsers(): List<User>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Long): User

    @POST("users")
    suspend fun createUser(@Body request: CreateUserRequest): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: Long)

    @GET("users")
    suspend fun searchUsers(
        @Query("q") query: String,
        @Query("page") page: Int = 1
    ): List<User>
}

// Data classes с автоматической сериализацией
@Serializable
data class User(
    val id: Long,
    val name: String,
    val email: String
)

// Использование — одна строка!
val users = apiService.getUsers()
```

### Визуальное сравнение

```
┌─────────────────────────────────────────────────────────────────┐
│                   HttpURLConnection                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Ваш код                                                        │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ - Создание URL                                           │   │
│  │ - Настройка connection                                   │   │
│  │ - Установка headers                                      │   │
│  │ - Установка таймаутов                                    │   │
│  │ - Обработка response code                                │   │
│  │ - Чтение InputStream                                     │   │
│  │ - Парсинг JSON                                           │   │
│  │ - Маппинг в объекты                                      │   │
│  │ - Обработка ошибок                                       │   │
│  │ - Закрытие соединения                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ~50 строк на каждый запрос                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        Retrofit                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Ваш код           Retrofit генерирует                          │
│  ┌──────────┐     ┌─────────────────────────────────────────┐  │
│  │ @GET     │────▶│ - URL построение                         │  │
│  │ @POST    │     │ - Headers (через interceptors)           │  │
│  │ @Body    │     │ - Serialization (через converters)       │  │
│  │ @Query   │     │ - Connection management                   │  │
│  └──────────┘     │ - Response parsing                        │  │
│                   │ - Error handling                           │  │
│  ~5 строк на      └─────────────────────────────────────────┘  │
│  endpoint                                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему OkHttp под капотом

Retrofit — это **декларативная обёртка** над OkHttp. OkHttp делает реальную работу:

| Компонент | Ответственность |
|-----------|-----------------|
| **Retrofit** | Превращает интерфейс в HTTP вызовы |
| **OkHttp** | Выполняет запросы, управляет соединениями |
| **Converter** | JSON ↔ объекты (kotlinx.serialization, Gson, Moshi) |
| **Interceptor** | Модификация запросов/ответов (auth, logging, retry) |

```kotlin
// Retrofit строит на OkHttp
val okHttpClient = OkHttpClient.Builder()
    .addInterceptor(authInterceptor)      // OkHttp feature
    .addInterceptor(loggingInterceptor)   // OkHttp feature
    .cache(cache)                          // OkHttp feature
    .build()

val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .client(okHttpClient)                  // Использует OkHttp
    .addConverterFactory(...)              // Retrofit feature
    .build()
```

### Почему не другие библиотеки?

| Библиотека | Плюсы | Минусы | Когда использовать |
|------------|-------|--------|-------------------|
| **Retrofit** | Декларативный, популярный, много расширений | Не multiplatform | Android-only проект |
| **Ktor Client** | Kotlin-native, multiplatform, coroutines | Меньше экосистема | KMM проект |
| **Volley** | Простой, от Google | Устаревший, меньше features | Legacy проекты |
| **OkHttp напрямую** | Полный контроль | Много boilerplate | Нестандартные протоколы |

### Недостатки Retrofit

1. **Compile-time код генерация:**
   - Требует annotation processor (kapt/ksp)
   - Увеличивает время сборки

2. **Не подходит для KMM:**
   - Android-only библиотека
   - Для multiplatform нужен Ktor

3. **Сложная отладка:**
   - Стектрейсы включают сгенерированный код
   - Нужен logging interceptor для debug

4. **Overhead для простых случаев:**
   - Один запрос? HttpURLConnection проще
   - Но кто делает приложение с одним запросом?

### Когда HttpURLConnection всё же лучше

- Библиотека/SDK без внешних зависимостей
- Критичный размер APK (каждый KB важен)
- Единственный простой запрос
- Нестандартный протокол (не REST)

---

## Retrofit: базовая настройка

### Dependencies

```kotlin
// build.gradle.kts
dependencies {
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-kotlinx-serialization:1.0.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")
    implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.6.2")
}
```

### Data classes

```kotlin
@Serializable
data class User(
    val id: Long,
    val name: String,
    val email: String,
    @SerialName("avatar_url")
    val avatarUrl: String? = null
)

@Serializable
data class CreateUserRequest(
    val name: String,
    val email: String
)

@Serializable
data class ApiResponse<T>(
    val data: T,
    val message: String? = null
)
```

### API Interface

```kotlin
interface ApiService {

    @GET("users")
    suspend fun getUsers(): List<User>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Long): User

    @GET("users")
    suspend fun searchUsers(
        @Query("q") query: String,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20
    ): List<User>

    @POST("users")
    suspend fun createUser(@Body request: CreateUserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(
        @Path("id") id: Long,
        @Body request: CreateUserRequest
    ): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: Long)

    @Multipart
    @POST("users/{id}/avatar")
    suspend fun uploadAvatar(
        @Path("id") id: Long,
        @Part file: MultipartBody.Part
    ): User

    @Headers("Cache-Control: max-age=300")
    @GET("config")
    suspend fun getConfig(): Config
}
```

### Retrofit Instance

```kotlin
object NetworkModule {

    private const val BASE_URL = "https://api.example.com/"

    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
    }

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor.Level.BODY
        } else {
            HttpLoggingInterceptor.Level.NONE
        }
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .addInterceptor(AuthInterceptor())
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
        .build()

    val apiService: ApiService = retrofit.create(ApiService::class.java)
}
```

---

## OkHttp Interceptors

### Auth Interceptor

```kotlin
class AuthInterceptor : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val token = TokenManager.getToken()

        val request = chain.request().newBuilder()
            .apply {
                if (token != null) {
                    addHeader("Authorization", "Bearer $token")
                }
                addHeader("Accept", "application/json")
                addHeader("X-App-Version", BuildConfig.VERSION_NAME)
            }
            .build()

        return chain.proceed(request)
    }
}
```

### Retry Interceptor

```kotlin
class RetryInterceptor(private val maxRetries: Int = 3) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var attempt = 0
        var lastException: IOException? = null

        while (attempt < maxRetries) {
            try {
                val response = chain.proceed(chain.request())
                if (response.isSuccessful || response.code !in 500..599) {
                    return response
                }
                response.close()
            } catch (e: IOException) {
                lastException = e
            }
            attempt++
            Thread.sleep(1000L * attempt)  // Exponential backoff
        }

        throw lastException ?: IOException("Max retries exceeded")
    }
}
```

### Cache Interceptor

```kotlin
// Offline cache
class CacheInterceptor(private val context: Context) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var request = chain.request()

        if (!isNetworkAvailable(context)) {
            request = request.newBuilder()
                .cacheControl(CacheControl.FORCE_CACHE)
                .build()
        }

        return chain.proceed(request)
    }

    private fun isNetworkAvailable(context: Context): Boolean {
        val connectivityManager = context
            .getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}

// Настройка кэша в OkHttp
val cache = Cache(
    directory = File(context.cacheDir, "http_cache"),
    maxSize = 10L * 1024 * 1024  // 10 MB
)

val client = OkHttpClient.Builder()
    .cache(cache)
    .addNetworkInterceptor(CacheInterceptor(context))
    .build()
```

---

## Обработка ошибок

### Sealed class для Result

```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val code: Int, val message: String) : NetworkResult<Nothing>()
    data class Exception(val e: Throwable) : NetworkResult<Nothing>()
}

suspend fun <T> safeApiCall(apiCall: suspend () -> T): NetworkResult<T> {
    return try {
        NetworkResult.Success(apiCall())
    } catch (e: HttpException) {
        NetworkResult.Error(e.code(), e.message())
    } catch (e: IOException) {
        NetworkResult.Exception(e)
    } catch (e: Exception) {
        NetworkResult.Exception(e)
    }
}

// Использование
class UserRepository(private val api: ApiService) {

    suspend fun getUsers(): NetworkResult<List<User>> {
        return safeApiCall { api.getUsers() }
    }
}

// В ViewModel
viewModelScope.launch {
    when (val result = repository.getUsers()) {
        is NetworkResult.Success -> _users.value = result.data
        is NetworkResult.Error -> _error.value = "Error ${result.code}: ${result.message}"
        is NetworkResult.Exception -> _error.value = "Network error: ${result.e.message}"
    }
}
```

---

## Ktor Client (multiplatform)

```kotlin
// build.gradle.kts
dependencies {
    implementation("io.ktor:ktor-client-core:2.3.7")
    implementation("io.ktor:ktor-client-android:2.3.7")  // или okhttp
    implementation("io.ktor:ktor-client-content-negotiation:2.3.7")
    implementation("io.ktor:ktor-serialization-kotlinx-json:2.3.7")
    implementation("io.ktor:ktor-client-logging:2.3.7")
}
```

```kotlin
val client = HttpClient(Android) {
    install(ContentNegotiation) {
        json(Json {
            ignoreUnknownKeys = true
            prettyPrint = true
        })
    }

    install(Logging) {
        level = LogLevel.BODY
    }

    defaultRequest {
        url("https://api.example.com/")
        header("Accept", "application/json")
    }
}

// Использование
suspend fun getUsers(): List<User> {
    return client.get("users").body()
}

suspend fun createUser(request: CreateUserRequest): User {
    return client.post("users") {
        contentType(ContentType.Application.Json)
        setBody(request)
    }.body()
}
```

---

## Подводные камни сетевых запросов

### NetworkOnMainThreadException

**Проблема:** Android запрещает сетевые операции в Main Thread (с API 11+).

```kotlin
// ❌ КРАХ приложения
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // StrictMode обнаружит это и бросит исключение
        val users = apiService.getUsers()  // NetworkOnMainThreadException!
    }
}
```

**Решение:** всегда используйте корутины или другие механизмы асинхронности.

```kotlin
// ✅ Правильно
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val users = apiService.getUsers()  // suspend функция в корутине
            // обновить UI
        }
    }
}
```

### SSL/TLS проблемы

**Certificate Pinning:** защита от Man-in-the-Middle атак.

```kotlin
// Проблема: приложение доверяет любому сертификату
// Решение: certificate pinning
val certificatePinner = CertificatePinner.Builder()
    .add("api.example.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=")
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

**Типичные ошибки:**
- `SSLHandshakeException` — неверный/истёкший сертификат
- `CertificateException` — проблемы с pinning
- Забыли обновить pin при смене сертификата на сервере

### Timeout handling

**Проблема:** без таймаутов приложение может зависнуть надолго.

```kotlin
// ❌ Таймауты по умолчанию могут быть слишком большими
val client = OkHttpClient()  // 10 секунд connect, 10 read, 10 write

// ✅ Настройте под свои нужды
val client = OkHttpClient.Builder()
    .connectTimeout(5, TimeUnit.SECONDS)     // Соединение с сервером
    .readTimeout(30, TimeUnit.SECONDS)       // Чтение ответа
    .writeTimeout(30, TimeUnit.SECONDS)      // Отправка данных
    .callTimeout(60, TimeUnit.SECONDS)       // Весь запрос целиком
    .build()
```

**Когда использовать разные таймауты:**
- `connectTimeout` — короткий (5-10s), если сервер недоступен
- `readTimeout` — длинный (30-60s) для больших ответов
- `writeTimeout` — длинный (30-60s) для загрузки файлов
- `callTimeout` — общий лимит на весь запрос

### Retry logic и exponential backoff

**Проблема:** одиночные запросы ненадёжны в нестабильной сети.

```kotlin
// ❌ Без retry — один сбой = провал
suspend fun getUsers(): List<User> {
    return api.getUsers()  // Если сеть упала на секунду — ошибка
}

// ✅ Retry с exponential backoff
suspend fun <T> retryWithBackoff(
    maxRetries: Int = 3,
    initialDelay: Long = 1000L,
    maxDelay: Long = 10000L,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay
    repeat(maxRetries - 1) { attempt ->
        try {
            return block()
        } catch (e: IOException) {
            // Логируем и ждём перед повтором
            Log.w("Network", "Attempt ${attempt + 1} failed, retrying in ${currentDelay}ms")
        }
        delay(currentDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelay)
    }
    return block()  // Последняя попытка без catch
}

// Использование
val users = retryWithBackoff { api.getUsers() }
```

**Exponential backoff:**
- Попытка 1: сразу
- Попытка 2: через 1 секунду
- Попытка 3: через 2 секунды
- Попытка 4: через 4 секунды
- Попытка 5: через 8 секунд

**Когда НЕ делать retry:**
- 4xx ошибки (клиентские ошибки) — retry бесполезен
- 401 Unauthorized — нужна ре-авторизация, а не retry
- POST запросы могут быть не идемпотентными

### Memory leaks при callback

**Проблема:** callback держит ссылку на Activity/Fragment.

```kotlin
// ❌ Memory leak через callback
class UserListActivity : AppCompatActivity() {

    private val api = ApiClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Callback держит ссылку на Activity
        api.getUsers(object : Callback<List<User>> {
            override fun onSuccess(users: List<User>) {
                // Если Activity уничтожена, но запрос ещё идёт — leak!
                updateUI(users)
            }
            override fun onError(e: Exception) {
                showError(e)
            }
        })
    }
}

// ✅ Используйте корутины с lifecycle-aware scope
class UserListActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // lifecycleScope автоматически отменяется при destroy
        lifecycleScope.launch {
            try {
                val users = api.getUsers()
                updateUI(users)
            } catch (e: Exception) {
                showError(e)
            }
        }
    }
}
```

**Правила:**
- Всегда используйте `lifecycleScope` / `viewModelScope`
- Никогда не храните callback как поле класса
- Отменяйте запросы в `onDestroy()` если используете Job

---

## Практические паттерны

### Repository с кэшированием

```kotlin
class UserRepository(
    private val api: ApiService,
    private val userDao: UserDao
) {
    // Стратегия: сначала кэш, потом сеть
    fun getUsers(): Flow<List<User>> = flow {
        // Сначала emit из кэша
        val cached = userDao.getAll()
        if (cached.isNotEmpty()) {
            emit(cached)
        }

        // Затем загрузить из сети
        try {
            val fresh = api.getUsers()
            userDao.insertAll(fresh)
            emit(fresh)
        } catch (e: Exception) {
            if (cached.isEmpty()) throw e
            // Если кэш есть, просто логируем ошибку
        }
    }
}
```

### Пагинация

```kotlin
class UserPagingSource(
    private val api: ApiService,
    private val query: String
) : PagingSource<Int, User>() {

    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> {
        val page = params.key ?: 1

        return try {
            val users = api.searchUsers(query, page, params.loadSize)
            LoadResult.Page(
                data = users,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (users.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, User>): Int? {
        return state.anchorPosition?.let { anchor ->
            state.closestPageToPosition(anchor)?.prevKey?.plus(1)
                ?: state.closestPageToPosition(anchor)?.nextKey?.minus(1)
        }
    }
}
```

---

## Чеклист

```
□ Все сетевые вызовы через suspend функции
□ Обработка ошибок (IOException, HttpException)
□ Logging interceptor только в DEBUG
□ Таймауты настроены (connect, read, write)
□ Auth token в interceptor, не в каждом запросе
□ Кэширование для offline support
□ Retry logic для transient errors
□ SSL pinning для production (опционально)
```

---

## Проверь себя

**1. Почему нельзя делать сетевые запросы в Main Thread?**

<details>
<summary>Показать ответ</summary>

Main Thread отвечает за отрисовку UI и обработку событий пользователя. Сетевые запросы могут занимать секунды или даже минуты (плохая связь, медленный сервер), что заморозит весь интерфейс. Android выбрасывает `NetworkOnMainThreadException` (с API 11+), чтобы предотвратить такие проблемы. Решение: используйте корутины (`suspend` функции), `WorkManager` или другие механизмы асинхронности.
</details>

---

**2. Что такое OkHttp Interceptor и зачем он нужен?**

<details>
<summary>Показать ответ</summary>

Interceptor — это middleware, который перехватывает HTTP запросы/ответы и может их модифицировать. Типичные применения:
- **AuthInterceptor** — добавляет токен авторизации ко всем запросам
- **LoggingInterceptor** — логирует запросы/ответы для отладки
- **CacheInterceptor** — управляет кэшированием
- **RetryInterceptor** — повторяет запросы при временных сбоях

Interceptor позволяет вынести общую логику (auth, logging) из бизнес-кода в одно место.
</details>

---

**3. Чем Retrofit отличается от OkHttp?**

<details>
<summary>Показать ответ</summary>

**OkHttp** — это HTTP-клиент низкого уровня, который выполняет реальные сетевые запросы, управляет соединениями, пулами потоков, кэшированием.

**Retrofit** — это декларативная обёртка над OkHttp, которая:
- Превращает интерфейсы с аннотациями в HTTP вызовы
- Автоматически сериализует/десериализует JSON в объекты
- Генерирует код на этапе компиляции
- Уменьшает boilerplate с ~50 строк до 5 на каждый endpoint

Retrofit **использует** OkHttp внутри, но добавляет type-safety и удобство.
</details>

---

**4. Как правильно обрабатывать ошибки сети?**

<details>
<summary>Показать ответ</summary>

Правильная обработка включает:

1. **Разделяйте типы ошибок:**
   - `IOException` — проблемы сети (нет интернета, timeout)
   - `HttpException` — HTTP ошибки (404, 500, etc.)
   - Другие исключения — парсинг, логика приложения

2. **Используйте sealed class для типобезопасности:**
   ```kotlin
   sealed class NetworkResult<out T> {
       data class Success<T>(val data: T) : NetworkResult<T>()
       data class Error(val code: Int, val message: String) : NetworkResult<Nothing>()
       data class Exception(val e: Throwable) : NetworkResult<Nothing>()
   }
   ```

3. **Не показывайте технические детали пользователю:**
   - `IOException` → "Проверьте подключение к интернету"
   - `500` → "Ошибка сервера, попробуйте позже"
   - `404` → "Данные не найдены"

4. **Используйте retry только для transient errors** (5xx, timeout), не для 4xx.
</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Retrofit = HTTP клиент" | Retrofit — type-safe wrapper над HTTP клиентом (OkHttp). Сам Retrofit не делает запросы. OkHttp — клиент, Retrofit — API декларация |
| "Ktor лучше для KMP" | Ktor — единственный вариант для pure KMP. Но Retrofit работает в shared module с expect/actual. Выбор зависит от проекта |
| "Call Adapter нужен только для RxJava" | Call Adapters для любых async абстракций: Flow, Deferred, Result, Either. Позволяют заменить Call<T> на нужный тип |
| "OkHttp Cache работает автоматически" | Cache работает только с правильными HTTP headers (Cache-Control, ETag). Сервер должен отправлять заголовки. Иначе кэш бесполезен |
| "Gson быстрее других" | Moshi и Kotlinx.serialization быстрее на Kotlin кодебазе. Kotlinx.serialization compile-time, работает с KMP. Gson — legacy выбор |
| "Interceptors для logging в production" | Logging interceptor в production = утечка данных в logcat. Используйте только в debug. Для production — crash reporting без sensitive data |
| "Timeout один для всех" | Разные операции — разные timeouts. Upload файла требует больший timeout чем GET. Настраивайте per-request через @Headers или новый OkHttpClient |
| "suspend fun автоматически background" | suspend делает функцию coroutine-compatible, не background. Dispatcher определяет thread. Retrofit suspend calls уже на IO, но своя логика требует withContext(IO) |
| "HTTP/2 всегда быстрее" | HTTP/2 быстрее для множественных concurrent запросов. Для одиночного запроса разница минимальна. Head-of-line blocking в HTTP/2 TCP — проблема для плохих сетей |
| "Retry нужен всегда" | Retry для idempotent операций (GET) безопасен. POST/PUT без idempotency key может создать дубликаты. 4xx ошибки (кроме 429) retry бесполезен |

---

## CS-фундамент

| CS-концепция | Как применяется в Networking |
|--------------|------------------------------|
| **HTTP Protocol** | Основа всей коммуникации. Request/Response модель. Methods (GET/POST/PUT/DELETE) определяют семантику. Status codes (2xx/4xx/5xx) — результат |
| **Connection Pooling** | OkHttp переиспользует TCP connections. Экономия на handshake. Keep-alive vs new connection. Pool size настраивается |
| **TLS/SSL** | HTTPS = HTTP over TLS. Certificate pinning защищает от MITM. OkHttp CertificatePinner для реализации |
| **Serialization** | Object ↔ JSON (или другой формат). Moshi/Gson/Kotlinx.serialization. Reflection vs code generation |
| **Caching** | HTTP Cache headers (Cache-Control, ETag, Last-Modified). Conditional requests (If-None-Match). Кэш на уровне HTTP, не application |
| **Async I/O** | Non-blocking I/O для network операций. Coroutines + Dispatchers.IO. Не блокируем Main thread |
| **Retry with Backoff** | Exponential backoff при ошибках. Jitter для избежания thundering herd. Circuit breaker pattern |
| **Content Negotiation** | Accept header определяет желаемый формат. Content-Type — формат отправки. JSON, XML, Protocol Buffers |
| **Interceptor Pattern** | Chain of Responsibility. Каждый interceptor может modify request/response. Logging, Auth, Retry — разные interceptors |
| **Type Safety** | Retrofit interface → compile-time safety. Moshi adapters → runtime safety. Ошибки парсинга явные |

---

## Связи

**Android раздел:**
→ [[android-overview]] — точка входа в экосистему Android, networking — часть архитектуры приложения
→ [[android-threading]] — сетевые запросы требуют фоновых потоков, здесь изучаются корутины для async операций
→ [[android-data-persistence]] — Room/DataStore для кэширования сетевых ответов, offline-first архитектура
→ [[android-architecture-patterns]] — Repository pattern объединяет сетевые и локальные источники данных

**Kotlin/JVM:**
→ [[kotlin-coroutines]] — `suspend` функции и Flow делают async запросы простыми и безопасными

**Networking:**
→ [[network-http-evolution]] — понимание HTTP/1.1 vs HTTP/2 vs HTTP/3 влияет на производительность OkHttp
→ [[api-design]] — REST vs GraphQL vs gRPC определяют выбор клиента (Retrofit для REST, Apollo для GraphQL)
→ [[networking-overview]] — фундаментальные концепции сетей (TCP/IP, DNS, TLS)
→ [[network-http-evolution]] — эволюция протокола HTTP и как она влияет на мобильные приложения
→ [[network-realtime-protocols]] — WebSocket/SSE для real-time функций (чаты, уведомления)
→ [[network-bluetooth]] — альтернативный канал связи для IoT устройств
→ [[network-cellular]] — понимание мобильных сетей (4G/5G) для оптимизации запросов
→ [[network-wireless-iot]] — протоколы для IoT интеграции в Android приложениях

---

## Источники

- [Retrofit Official Documentation - Square](https://square.github.io/retrofit/) — официальная документация Retrofit
- [OkHttp - Square](https://square.github.io/okhttp/) — официальная документация OkHttp
- [Ktor Client - Kotlin](https://ktor.io/docs/client.html) — документация Ktor Client
- [Android Networking Tutorial - Daily.dev](https://daily.dev/blog/retrofit-tutorial-for-android-beginners) — практический tutorial

---

*Проверено: 2026-01-09 | На основе официальной документации*
