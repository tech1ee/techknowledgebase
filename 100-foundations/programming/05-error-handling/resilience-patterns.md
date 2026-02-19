---
title: "Resilience Patterns: устойчивость к сбоям"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/resilience
  - topic/kotlin
related:
  - "[[error-handling]]"
  - "[[kotlin-coroutines]]"
  - "[[android-networking]]"
  - "[[android-repository-pattern]]"
---

# Resilience Patterns: устойчивость к сбоям

Сеть ненадёжна. Сервисы падают. Базы данных тормозят под нагрузкой. В распределённых системах вопрос не «упадёт ли что-нибудь?», а «что делать, когда упадёт?». Один упавший микросервис может каскадом положить всю систему — если не встроить защиту.

Resilience patterns — набор проверенных паттернов, которые превращают хрупкую систему в антихрупкую: она не просто выживает при сбоях, а **деградирует gracefully** — снижает функциональность вместо полного отказа.

---

## Карта паттернов

```
┌─────────────────────────────────────────────────────────────────────┐
│                    RESILIENCE PATTERNS                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ЗАЩИТА ОТ КАСКАДНЫХ СБОЕВ                                         │
│  ├── Circuit Breaker  — размыкает цепь при серии отказов            │
│  ├── Bulkhead         — изолирует ресурсы друг от друга             │
│  └── Rate Limiter     — ограничивает поток запросов                 │
│                                                                     │
│  ВОССТАНОВЛЕНИЕ ПОСЛЕ СБОЯ                                         │
│  ├── Retry            — повторяет при transient-ошибках             │
│  ├── Timeout          — не ждёт вечно                               │
│  └── Fallback         — альтернативный ответ при сбое              │
│                                                                     │
│  КОМБИНИРОВАНИЕ                                                     │
│  └── Retry → Circuit Breaker → Timeout → Fallback                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Circuit Breaker

Электрический автомат-предохранитель: если ток (ошибки) превышает порог — цепь размыкается, ток (запросы) перестаёт течь. Через время пробуем включить обратно.

### Три состояния

```
         Успех          Порог ошибок          Таймаут
           │             достигнут             истёк
           │                │                   │
     ┌─────▼─────┐   ┌─────▼─────┐   ┌─────────▼────────┐
     │           │   │           │   │                   │
     │  CLOSED   │──►│   OPEN    │──►│    HALF-OPEN      │
     │ (норма)   │   │ (отказ)   │   │ (пробный запрос)  │
     │           │◄──│           │   │                   │
     └───────────┘   └───────────┘   └─────────┬─────────┘
           ▲                                     │
           │            Пробный запрос           │
           │               успешен               │
           └─────────────────────────────────────┘
                     Пробный запрос
                       неуспешен
                    ┌────────────────┐
                    │ → обратно OPEN │
                    └────────────────┘
```

- **CLOSED** — все запросы проходят. Счётчик ошибок ведётся. Если ошибок >= порога → OPEN.
- **OPEN** — все запросы **сразу** получают fallback. Без обращения к сервису. Через `recoveryTimeout` → HALF-OPEN.
- **HALF-OPEN** — пропускается **один** пробный запрос. Успех → CLOSED. Ошибка → обратно OPEN.

### Реализация на Kotlin с корутинами

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds
import kotlin.time.TimeSource

class CircuitBreaker(
    private val failureThreshold: Int = 5,
    private val recoveryTimeout: Duration = 30.seconds,
    private val name: String = "default"
) {
    sealed interface State {
        data object Closed : State
        data class Open(val since: TimeSource.Monotonic.ValueTimeMark) : State
        data object HalfOpen : State
    }

    private var state: State = State.Closed
    private var failureCount = 0
    private val mutex = Mutex()
    private val timeSource = TimeSource.Monotonic

    suspend fun <T> execute(block: suspend () -> T): T {
        // Проверяем состояние
        val currentState = mutex.withLock { checkState() }

        when (currentState) {
            is State.Open -> throw CircuitBreakerOpenException(name)
            else -> { /* proceed */ }
        }

        return try {
            val result = block()
            onSuccess()
            result
        } catch (e: Exception) {
            onFailure()
            throw e
        }
    }

    suspend fun <T> executeOrNull(block: suspend () -> T): T? =
        try { execute(block) }
        catch (e: CircuitBreakerOpenException) { null }

    private fun checkState(): State {
        val current = state
        if (current is State.Open) {
            val elapsed = current.since.elapsedNow()
            if (elapsed >= recoveryTimeout) {
                state = State.HalfOpen
                return State.HalfOpen
            }
        }
        return current
    }

    private suspend fun onSuccess() = mutex.withLock {
        failureCount = 0
        state = State.Closed
    }

    private suspend fun onFailure() = mutex.withLock {
        failureCount++
        if (failureCount >= failureThreshold) {
            state = State.Open(since = timeSource.markNow())
        }
    }
}

class CircuitBreakerOpenException(name: String) :
    RuntimeException("Circuit breaker '$name' is OPEN")
```

### Когда использовать

| Сценарий | Circuit Breaker нужен? |
|----------|----------------------|
| Вызов внешнего API | Да |
| Подключение к БД | Да |
| Чтение локального файла | Нет |
| Вызов in-process функции | Нет |
| Межсервисные gRPC-вызовы | Да |

> [!info] Kotlin-нюанс
> В реальных проектах используйте библиотеки: **Resilience4j** с Kotlin-расширениями (`circuitBreaker.executeSuspendFunction { }`) или **Arrow** (`CircuitBreaker`). Самописная реализация — для понимания принципа.

---

## Retry с Exponential Backoff

Retry — повторная попытка при transient-ошибках. Без backoff — это DDoS самого себя.

### Простой retry

```kotlin
suspend fun <T> retry(
    maxAttempts: Int = 3,
    block: suspend (attempt: Int) -> T
): T {
    var lastException: Exception? = null
    repeat(maxAttempts) { attempt ->
        try {
            return block(attempt)
        } catch (e: Exception) {
            lastException = e
        }
    }
    throw lastException!!
}

// Использование
val user = retry(maxAttempts = 3) { attempt ->
    println("Попытка ${attempt + 1}...")
    api.fetchUser(userId)
}
```

### Exponential Backoff с Jitter

```kotlin
import kotlinx.coroutines.delay
import kotlin.math.min
import kotlin.math.pow
import kotlin.random.Random
import kotlin.time.Duration
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds

suspend fun <T> retryWithBackoff(
    maxAttempts: Int = 3,
    baseDelay: Duration = 1.seconds,
    maxDelay: Duration = 60.seconds,
    factor: Double = 2.0,
    jitter: Boolean = true,
    retryOn: (Exception) -> Boolean = { true },
    block: suspend (attempt: Int) -> T
): T {
    var lastException: Exception? = null

    repeat(maxAttempts) { attempt ->
        try {
            return block(attempt)
        } catch (e: Exception) {
            lastException = e

            // Последняя попытка — не ждём
            if (attempt == maxAttempts - 1) throw e

            // Не retry для non-retryable ошибок
            if (!retryOn(e)) throw e

            // Вычисляем задержку
            val exponentialDelay = baseDelay * factor.pow(attempt.toDouble())
            val cappedDelay = minOf(exponentialDelay, maxDelay)

            // Jitter предотвращает thundering herd
            val actualDelay = if (jitter) {
                cappedDelay * (0.5 + Random.nextDouble() * 0.5)
            } else {
                cappedDelay
            }

            println("Попытка ${attempt + 1} не удалась: ${e.message}. " +
                    "Повтор через ${actualDelay.inWholeMilliseconds}ms...")
            delay(actualDelay)
        }
    }

    throw lastException!!
}
```

### Использование с фильтрацией ошибок

```kotlin
val response = retryWithBackoff(
    maxAttempts = 4,
    baseDelay = 500.milliseconds,
    maxDelay = 10.seconds,
    retryOn = { error ->
        when (error) {
            // Retry transient errors
            is java.io.IOException -> true
            is HttpException -> error.code in listOf(408, 429, 500, 502, 503, 504)
            // НЕ retry client errors — это наша вина
            else -> false
        }
    }
) { attempt ->
    logger.info { "Запрос к API (попытка ${attempt + 1})" }
    apiClient.fetchData(endpoint)
}
```

### Почему нужен Jitter

```
БЕЗ jitter (thundering herd):            С jitter (распределённые запросы):

  Сервис упал в T=0                       Сервис упал в T=0
  T=1s: ████████ 100 клиентов             T=0.5-1.5s: ██░░██░██░░█
  T=2s: ████████ 100 клиентов             T=1.0-3.0s: █░██░░█░██░░
  T=4s: ████████ 100 клиентов             T=2.0-6.0s: ░█░░██░█░░██
  → Сервис не успевает восстановиться     → Нагрузка распределена
```

> [!warning] Когда НЕ retry
> - **4xx ошибки** (кроме 408, 429) — это ошибки клиента, повтор не поможет
> - **Неидемпотентные операции** без idempotency key — рискуем создать дубликаты
> - **Бизнес-ошибки** (insufficient funds) — повтор не исправит баланс

---

## Timeout

Не ждать ответа вечно. В Kotlin корутинах — встроенная поддержка таймаутов.

### withTimeout и withTimeoutOrNull

```kotlin
import kotlinx.coroutines.withTimeout
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.time.Duration.Companion.seconds

// withTimeout — бросает TimeoutCancellationException
suspend fun fetchUserStrict(userId: String): User =
    withTimeout(5.seconds) {
        api.fetchUser(userId) // отменится если > 5 секунд
    }

// withTimeoutOrNull — возвращает null при таймауте
suspend fun fetchUserSafe(userId: String): User? =
    withTimeoutOrNull(5.seconds) {
        api.fetchUser(userId)
    }

// Использование: timeout + fallback
suspend fun getUserProfile(userId: String): UserProfile {
    val user = withTimeoutOrNull(3.seconds) {
        api.fetchUser(userId)
    } ?: cache.getUser(userId) // fallback на кеш
       ?: throw UserNotFoundException(userId)

    val avatar = withTimeoutOrNull(2.seconds) {
        imageService.downloadAvatar(user.avatarUrl)
    } // null если таймаут — покажем placeholder

    return UserProfile(user, avatar)
}
```

### Композиция таймаутов

```kotlin
// Общий таймаут на всю операцию + отдельные на каждый шаг
suspend fun placeOrder(request: OrderRequest): Order =
    withTimeout(10.seconds) { // общий лимит
        val inventory = withTimeout(3.seconds) {
            inventoryService.check(request.items)
        }

        val payment = withTimeout(5.seconds) {
            paymentService.charge(request.userId, request.total)
        }

        withTimeout(2.seconds) {
            orderService.create(request, inventory, payment)
        }
    }
```

### Ktor client: настройка таймаутов

```kotlin
import io.ktor.client.*
import io.ktor.client.plugins.*

val client = HttpClient {
    install(HttpTimeout) {
        // Таймаут на установление соединения
        connectTimeoutMillis = 5_000

        // Таймаут на получение ответа
        requestTimeoutMillis = 15_000

        // Таймаут между пакетами (socket timeout)
        socketTimeoutMillis = 10_000
    }
}

// Переопределение для конкретного запроса
val response = client.get("https://api.example.com/slow-endpoint") {
    timeout {
        requestTimeoutMillis = 60_000 // этот запрос может быть долгим
    }
}
```

> [!info] Kotlin-нюанс
> `withTimeout` бросает `TimeoutCancellationException` — подтип `CancellationException`. Это значит, что `runCatching` **перехватит** его и нарушит отмену корутины. Используйте `withTimeoutOrNull` или `try/catch` с явным типом.

---

## Fallback

Альтернативный ответ, когда основной источник недоступен. Цепочка стратегий: от лучшего к приемлемому.

```kotlin
// Цепочка fallback-стратегий
suspend fun getUserData(userId: String): UserData {
    // Стратегия 1: Real-time API
    val fromApi = runCatching { api.getUser(userId) }
    if (fromApi.isSuccess) return fromApi.getOrThrow()

    // Стратегия 2: Кеш
    val fromCache = cache.get("user:$userId")
    if (fromCache != null) {
        logger.warn { "API недоступен, используем кеш для $userId" }
        return fromCache
    }

    // Стратегия 3: Локальная БД
    val fromDb = database.findUser(userId)
    if (fromDb != null) {
        logger.warn { "API и кеш недоступны, используем БД для $userId" }
        return fromDb.toUserData()
    }

    // Стратегия 4: Default
    logger.error { "Все источники недоступны для $userId" }
    return UserData(id = userId, name = "Unknown", isFallback = true)
}
```

### Обобщённый Fallback

```kotlin
class FallbackChain<T>(
    private val strategies: List<suspend () -> T>
) {
    suspend fun execute(): T {
        val errors = mutableListOf<Throwable>()

        strategies.forEachIndexed { index, strategy ->
            try {
                val result = strategy()
                if (index > 0) {
                    logger.info { "Fallback стратегия #$index сработала" }
                }
                return result
            } catch (e: Exception) {
                errors.add(e)
                logger.warn { "Стратегия #$index не удалась: ${e.message}" }
            }
        }

        throw FallbackExhaustedException(
            "Все ${strategies.size} стратегий исчерпаны",
            errors
        )
    }
}

class FallbackExhaustedException(
    message: String,
    val causes: List<Throwable>
) : RuntimeException(message)

// Использование
suspend fun getProductPrice(productId: String): Price =
    FallbackChain(listOf(
        { priceApi.getPrice(productId) },           // real-time
        { priceCache.get(productId)!! },              // кеш
        { catalogDb.getLastKnownPrice(productId)!! }, // БД
        { Price.DEFAULT }                              // дефолт
    )).execute()
```

### Cache-then-network

Популярный паттерн в мобильных приложениях — показать данные из кеша мгновенно, обновить из сети в фоне:

```kotlin
fun getArticles(): Flow<Result<List<Article>>> = flow {
    // Шаг 1: мгновенно из кеша
    val cached = articleDao.getAll()
    if (cached.isNotEmpty()) {
        emit(Result.Success(cached))
    } else {
        emit(Result.Loading)
    }

    // Шаг 2: обновить из сети
    try {
        val fresh = api.fetchArticles()
        articleDao.replaceAll(fresh)
        emit(Result.Success(fresh))
    } catch (e: IOException) {
        if (cached.isEmpty()) {
            emit(Result.Error(AppError.NetworkError(0, "/articles", e)))
        }
        // Если кеш есть — молча используем его, только логируем
        logger.warn(e) { "Не удалось обновить статьи из сети" }
    }
}
```

---

## Bulkhead

Переборка в корпусе корабля: если один отсек затоплен, остальные остаются сухими. В коде: **изоляция ресурсов** — один упавший компонент не забирает все потоки/память.

### Semaphore — ограничение concurrency

```kotlin
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withPermit

class ApiClient(
    // Не больше 10 одновременных запросов к API
    private val semaphore: Semaphore = Semaphore(10)
) {
    suspend fun fetch(url: String): Response =
        semaphore.withPermit {
            // Максимум 10 корутин здесь одновременно
            httpClient.get(url)
        }
}

// Использование: 100 запросов, но максимум 10 одновременно
val results = urls.map { url ->
    async { apiClient.fetch(url) }
}.awaitAll()
```

### limitedParallelism — ограничение потоков

```kotlin
import kotlinx.coroutines.Dispatchers

// Выделяем ограниченный пул для тяжёлых операций
val heavyComputationDispatcher = Dispatchers.Default.limitedParallelism(2)
val databaseDispatcher = Dispatchers.IO.limitedParallelism(4)
val apiDispatcher = Dispatchers.IO.limitedParallelism(8)

// Каждый ресурс изолирован — проблемы с API не убьют БД
suspend fun complexOperation() = coroutineScope {
    val computed = async(heavyComputationDispatcher) {
        heavyComputation() // максимум 2 потока
    }

    val dbResult = async(databaseDispatcher) {
        database.query(sql) // максимум 4 потока
    }

    val apiResult = async(apiDispatcher) {
        api.fetch(url) // максимум 8 потоков
    }

    merge(computed.await(), dbResult.await(), apiResult.await())
}
```

> [!info] Kotlin-нюанс
> `Semaphore` ограничивает **количество корутин**, а `limitedParallelism` — **количество потоков**. Для I/O-bound задач (API, DB) обычно хватает `Semaphore`. Для CPU-bound (парсинг, шифрование) — `limitedParallelism`.

---

## Rate Limiter

Ограничение количества запросов за единицу времени. Защита от перегрузки downstream-сервиса.

### Token Bucket

```
┌────────────────────────────────────────────────┐
│              TOKEN BUCKET                       │
├────────────────────────────────────────────────┤
│                                                 │
│  Ведро вмещает N токенов (capacity = 10)       │
│  Каждые T мс добавляется 1 токен (refill)      │
│                                                 │
│  Запрос приходит:                               │
│  ├── Есть токен → забрать, пропустить          │
│  └── Нет токена → отклонить / подождать        │
│                                                 │
│  ┌──────────────────────────────────────┐      │
│  │ [●][●][●][●][●][○][○][○][○][○]     │      │
│  │  5 токенов доступно из 10            │      │
│  │  refill: 1 токен каждые 100ms        │      │
│  └──────────────────────────────────────┘      │
│                                                 │
└────────────────────────────────────────────────┘
```

### Реализация на Kotlin

```kotlin
import kotlinx.coroutines.delay
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.time.Duration
import kotlin.time.Duration.Companion.milliseconds
import kotlin.time.Duration.Companion.seconds
import kotlin.time.TimeSource

class RateLimiter(
    private val capacity: Int,
    private val refillRate: Duration // время между рефилами одного токена
) {
    private var tokens: Int = capacity
    private var lastRefillTime = TimeSource.Monotonic.markNow()
    private val mutex = Mutex()

    suspend fun acquire() {
        mutex.withLock {
            refill()
            if (tokens > 0) {
                tokens--
                return
            }
        }
        // Нет токенов — ждём
        delay(refillRate)
        acquire() // рекурсивно пробуем снова
    }

    suspend fun <T> execute(block: suspend () -> T): T {
        acquire()
        return block()
    }

    private fun refill() {
        val elapsed = lastRefillTime.elapsedNow()
        val newTokens = (elapsed / refillRate).toInt()
        if (newTokens > 0) {
            tokens = minOf(capacity, tokens + newTokens)
            lastRefillTime = TimeSource.Monotonic.markNow()
        }
    }
}

// Использование: максимум 10 запросов в секунду
val rateLimiter = RateLimiter(
    capacity = 10,
    refillRate = 100.milliseconds // 1 токен каждые 100ms = 10/сек
)

suspend fun callApi(endpoint: String): Response =
    rateLimiter.execute {
        httpClient.get(endpoint)
    }
```

---

## Комбинирование паттернов

В реальных системах паттерны комбинируются в пайплайн:

```
Request → [Rate Limiter] → [Retry + Backoff] → [Circuit Breaker] → [Timeout] → Service
                                                                         │
                                                                    [Fallback]
```

### Обобщённая resilient-функция

```kotlin
import kotlin.time.Duration
import kotlin.time.Duration.Companion.seconds

suspend fun <T> resilient(
    circuitBreaker: CircuitBreaker,
    maxRetries: Int = 3,
    timeout: Duration = 5.seconds,
    fallback: (suspend () -> T)? = null,
    retryOn: (Exception) -> Boolean = { it is java.io.IOException },
    block: suspend () -> T
): T {
    return try {
        circuitBreaker.execute {
            retryWithBackoff(
                maxAttempts = maxRetries,
                retryOn = retryOn
            ) {
                withTimeout(timeout) {
                    block()
                }
            }
        }
    } catch (e: CircuitBreakerOpenException) {
        // Circuit open — сразу fallback, без retry
        fallback?.invoke()
            ?: throw e
    } catch (e: Exception) {
        // Все retry исчерпаны
        fallback?.invoke()
            ?: throw e
    }
}

// Использование
val paymentCircuit = CircuitBreaker(
    failureThreshold = 5,
    recoveryTimeout = 30.seconds,
    name = "payment"
)

suspend fun processPayment(amount: BigDecimal): PaymentResult =
    resilient(
        circuitBreaker = paymentCircuit,
        maxRetries = 3,
        timeout = 10.seconds,
        fallback = { queueForLaterProcessing(amount) },
        retryOn = { it is IOException || (it is HttpException && it.code >= 500) }
    ) {
        paymentGateway.charge(amount)
    }
```

### Порядок имеет значение

```
✅ ПРАВИЛЬНО: Retry ВНУТРИ Circuit Breaker
   CB следит за общим числом ошибок. 3 retry-попытки = 3 ошибки для CB.
   После порога — CB размыкается, retry не происходят.

❌ НЕПРАВИЛЬНО: Retry СНАРУЖИ Circuit Breaker
   CB открыт → retry всё равно стучится → получает CircuitBreakerOpenException
   → retry пробует снова → опять CircuitBreakerOpenException → бессмысленно
```

---

## Resilience4j: промышленная библиотека

Resilience4j — библиотека для JVM с поддержкой Kotlin корутин.

### Подключение

```kotlin
// build.gradle.kts
dependencies {
    implementation("io.github.resilience4j:resilience4j-circuitbreaker:2.2.0")
    implementation("io.github.resilience4j:resilience4j-retry:2.2.0")
    implementation("io.github.resilience4j:resilience4j-kotlin:2.2.0")
    implementation("io.github.resilience4j:resilience4j-timelimiter:2.2.0")
}
```

### Использование с корутинами

```kotlin
import io.github.resilience4j.circuitbreaker.CircuitBreaker
import io.github.resilience4j.circuitbreaker.CircuitBreakerConfig
import io.github.resilience4j.kotlin.circuitbreaker.executeSuspendFunction
import io.github.resilience4j.kotlin.retry.executeSuspendFunction
import io.github.resilience4j.retry.Retry
import io.github.resilience4j.retry.RetryConfig
import java.time.Duration

// Конфигурация Circuit Breaker
val circuitBreakerConfig = CircuitBreakerConfig.custom()
    .failureRateThreshold(50f)         // 50% ошибок → OPEN
    .waitDurationInOpenState(Duration.ofSeconds(30))
    .slidingWindowSize(10)              // считаем по последним 10 вызовам
    .permittedNumberOfCallsInHalfOpenState(3)
    .build()

val circuitBreaker = CircuitBreaker.of("paymentService", circuitBreakerConfig)

// Конфигурация Retry
val retryConfig = RetryConfig.custom<Any>()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(500))
    .retryExceptions(IOException::class.java)
    .ignoreExceptions(ValidationException::class.java)
    .build()

val retry = Retry.of("paymentRetry", retryConfig)

// Kotlin-идиоматичное использование с suspend-функциями
suspend fun chargePayment(amount: BigDecimal): PaymentResult {
    return circuitBreaker.executeSuspendFunction {
        retry.executeSuspendFunction {
            paymentGateway.charge(amount) // suspend-функция
        }
    }
}
```

---

## Ktor client: встроенная resilience

Ktor HTTP-клиент имеет встроенные плагины для retry и timeout.

### Retry Plugin

```kotlin
import io.ktor.client.*
import io.ktor.client.plugins.*
import io.ktor.client.request.*

val client = HttpClient {
    install(HttpRequestRetry) {
        // Retry на серверные ошибки (5xx)
        retryOnServerErrors(maxRetries = 3)

        // Retry при таймауте
        retryOnException(maxRetries = 2, retryOnTimeout = true)

        // Exponential backoff
        exponentialDelay()

        // Кастомная логика
        modifyRequest { request ->
            request.headers.append("X-Retry-Count", retryCount.toString())
        }
    }

    install(HttpTimeout) {
        connectTimeoutMillis = 5_000
        requestTimeoutMillis = 15_000
        socketTimeoutMillis = 10_000
    }
}
```

### OkHttp Interceptor для retry

```kotlin
import okhttp3.Interceptor
import okhttp3.Response

class RetryInterceptor(
    private val maxRetries: Int = 3
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        var lastException: Exception? = null
        val request = chain.request()

        repeat(maxRetries) { attempt ->
            try {
                val response = chain.proceed(request)
                if (response.isSuccessful || response.code < 500) {
                    return response
                }
                // 5xx — retry
                response.close()
            } catch (e: java.io.IOException) {
                lastException = e
                if (attempt < maxRetries - 1) {
                    Thread.sleep(1000L * (attempt + 1)) // linear backoff
                }
            }
        }

        throw lastException ?: IOException("Retry exhausted")
    }
}

// Подключение
val client = OkHttpClient.Builder()
    .addInterceptor(RetryInterceptor(maxRetries = 3))
    .connectTimeout(5, TimeUnit.SECONDS)
    .readTimeout(15, TimeUnit.SECONDS)
    .build()
```

---

## Offline-first: Room + Flow

В мобильных приложениях «падение сети» — не edge case, а норма. Room + Flow реализуют паттерн offline-first:

```kotlin
class ArticleRepository(
    private val api: ArticleApi,
    private val dao: ArticleDao
) {
    // Single source of truth — база данных
    fun observeArticles(): Flow<List<Article>> = dao.observeAll()

    // Обновление из сети — side effect
    suspend fun refresh(): Result<Unit> = runCatching {
        val articles = api.fetchAll()
        dao.replaceAll(articles)
    }

    // Комбинация: наблюдаем БД + периодически обновляем из сети
    fun articlesWithRefresh(): Flow<UiState<List<Article>>> = flow {
        emit(UiState.Loading)

        // Мгновенно показываем из кеша
        val cached = dao.getAll()
        if (cached.isNotEmpty()) {
            emit(UiState.Success(cached))
        }

        // Обновляем из сети
        refresh().fold(
            onSuccess = {
                // dao.observeAll() автоматически пришлёт обновление
            },
            onFailure = { error ->
                if (cached.isEmpty()) {
                    emit(UiState.Error(error.message ?: "Network error"))
                }
                // Если кеш есть — молча используем его
            }
        )

        // Подписка на обновления из БД
        emitAll(dao.observeAll().map { UiState.Success(it) })
    }
}

sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}
```

---

## Мониторинг resilience

Паттерны бесполезны, если не отслеживать их поведение:

```kotlin
class InstrumentedCircuitBreaker(
    private val delegate: CircuitBreaker,
    private val metrics: MetricsCollector,
    private val name: String
) {
    suspend fun <T> execute(block: suspend () -> T): T {
        val startTime = System.nanoTime()
        return try {
            val result = delegate.execute(block)
            metrics.recordSuccess(name, System.nanoTime() - startTime)
            result
        } catch (e: CircuitBreakerOpenException) {
            metrics.recordCircuitOpen(name)
            throw e
        } catch (e: Exception) {
            metrics.recordFailure(name, e::class.simpleName ?: "Unknown")
            throw e
        }
    }
}

// Что мониторить:
// ├── circuit_breaker_state{name="payment"} — текущее состояние (0/1/2)
// ├── circuit_breaker_failures_total{name="payment"} — счётчик ошибок
// ├── retry_attempts_total{name="payment"} — сколько retry было
// ├── request_duration_seconds{name="payment"} — латенция
// └── fallback_invocations_total{name="payment"} — как часто fallback
```

---

## Проверь себя

<details>
<summary>1. Чем отличается Circuit Breaker от Retry?</summary>

**Ответ:**

**Retry** — повторяет единичный запрос при transient-ошибке (с exponential backoff). Работает на уровне одного запроса.

**Circuit Breaker** — отслеживает общее число ошибок за период. При достижении порога «размыкает цепь» — возвращает fallback **сразу**, без попыток обращения к сервису. Защищает downstream-сервис, давая ему время восстановиться.

Часто используются вместе: retry внутри circuit breaker.

</details>

<details>
<summary>2. Зачем нужен Jitter в exponential backoff?</summary>

**Ответ:**

Без jitter все клиенты, которые получили ошибку одновременно, будут retry ровно через 1с, 2с, 4с — **одновременно**. Это thundering herd — волна запросов, которая снова перегружает сервис.

Jitter добавляет случайность к задержке: один клиент подождёт 0.8с, другой 1.3с, третий 0.5с — нагрузка распределяется равномерно.

</details>

<details>
<summary>3. В чём разница между `withTimeout` и `withTimeoutOrNull`?</summary>

**Ответ:**

- `withTimeout(duration)` — бросает `TimeoutCancellationException` при истечении таймаута. Подходит когда таймаут — ошибка.
- `withTimeoutOrNull(duration)` — возвращает `null` при таймауте. Подходит для мягких сценариев с fallback.

Важно: `TimeoutCancellationException` — подтип `CancellationException`, поэтому `runCatching` его **перехватит** и нарушит structured concurrency.

</details>

<details>
<summary>4. Когда использовать `Semaphore`, а когда `limitedParallelism`?</summary>

**Ответ:**

- **`Semaphore`** — ограничивает количество **корутин**, одновременно выполняющих блок кода. Подходит для I/O-bound задач: API-вызовы, БД, файловые операции.
- **`limitedParallelism(n)`** — ограничивает количество **потоков** в диспетчере. Подходит для CPU-bound задач: парсинг, шифрование, обработка изображений.

</details>

<details>
<summary>5. Почему retry должен быть ВНУТРИ circuit breaker, а не снаружи?</summary>

**Ответ:**

Если retry внутри CB: 3 неудачных retry = 3 ошибки для circuit breaker. Когда CB открывается — retry прекращаются, сервис получает время на восстановление.

Если retry снаружи CB: когда CB открыт, retry получает `CircuitBreakerOpenException` и пытается снова — бессмысленно стучит в закрытую дверь. Тратит время и не даёт сервису восстановиться.

</details>

---

## Ключевые карточки

Какие три состояния у Circuit Breaker?
?
**Closed** (норма) → все запросы проходят, ошибки считаются. **Open** (отказ) → запросы сразу возвращают fallback. **Half-Open** (пробный) → пропускает один запрос: успех → Closed, ошибка → обратно Open.

Что такое exponential backoff и зачем jitter?
?
Задержка между retry растёт экспоненциально: 1с → 2с → 4с → 8с. Без jitter все клиенты retry одновременно (thundering herd). Jitter добавляет случайность: `delay * (0.5 + random * 0.5)` — распределяет нагрузку.

В чём разница Semaphore и limitedParallelism?
?
**Semaphore** — ограничивает количество **корутин** в блоке кода (`withPermit { }`). Для I/O-bound. **limitedParallelism(n)** — ограничивает количество **потоков** диспетчера. Для CPU-bound задач.

Как работает Token Bucket rate limiter?
?
Ведро на N токенов. Каждые T мс добавляется токен (до capacity). Запрос забирает 1 токен. Если токенов нет — запрос ждёт или отклоняется. Пример: capacity=10, refill=100ms → максимум 10 запросов/сек с возможностью burst.

Какой порядок комбинирования resilience-паттернов?
?
`Rate Limiter → Retry → Circuit Breaker → Timeout → Service → Fallback`. Retry **внутри** CB: неудачные retry считаются ошибками для CB. Когда CB открыт — retry не происходят, сразу fallback.

Что такое Bulkhead и зачем изолировать ресурсы?
?
Переборка корабля: затопление одного отсека не топит весь корабль. В коде: отдельный `Semaphore` / `limitedParallelism` для API, БД и вычислений. Если API тормозит — он забирает свои 8 потоков, а не все 64 из IO-пула.

Как Ktor client обеспечивает retry и timeout?
?
`HttpRequestRetry` плагин: `retryOnServerErrors(maxRetries)`, `exponentialDelay()`, `retryOnException(retryOnTimeout = true)`. `HttpTimeout` плагин: `connectTimeoutMillis`, `requestTimeoutMillis`, `socketTimeoutMillis`. Настройки можно переопределить для конкретного запроса.

Что такое offline-first и как его реализовать?
?
Single source of truth — локальная БД (Room). UI подписан на `Flow` из БД. Сеть обновляет БД в фоне. Если сеть недоступна — показываем кеш. Паттерн: `dao.observeAll()` + `api.fetch() → dao.replaceAll()`.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Основа | [[error-handling]] | Обработка ошибок: exceptions, Result, sealed errors |
| Углубиться | [[kotlin-coroutines]] | Structured concurrency, SupervisorJob, Flow |
| Практика | [[android-networking]] | Retrofit, Ktor client, OkHttp в реальных проектах |
| Архитектура | [[android-repository-pattern]] | Repository + offline-first на практике |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

## Источники

- Nygard M. — *Release It! Design and Deploy Production-Ready Software* (2nd ed., Pragmatic Bookshelf, 2018) — Circuit Breaker, Bulkhead, Steady State и другие паттерны стабильности
- Hanmer R. — *Patterns for Fault Tolerant Software* (Wiley, 2007) — академическая база resilience patterns
- [Resilience4j Documentation: Kotlin](https://resilience4j.readme.io/docs/getting-started-4) — Kotlin-расширения для CircuitBreaker, Retry, TimeLimiter
- [Arrow: Circuit Breaker](https://arrow-kt.io/learn/resilience/circuitbreaker/) — функциональная реализация CB в Arrow
- [Ktor: Retrying Failed Requests](https://ktor.io/docs/client-request-retry.html) — HttpRequestRetry plugin
- [Ktor: Timeout](https://ktor.io/docs/client-timeout.html) — HttpTimeout plugin с per-request override
- [kmp-resilient](https://github.com/santimattius/kmp-resilient) — KMP-библиотека resilience patterns для suspend-функций
- [kotlin-retry](https://github.com/michaelbull/kotlin-retry) — мультиплатформенная retry-библиотека
- [Kotlin Coroutines: Semaphore](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.sync/-semaphore/) — официальная документация
- [limitedParallelism](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/-coroutine-dispatcher/limited-parallelism.html) — ограничение потоков диспетчера
- [Microsoft: Transient Fault Handling](https://docs.microsoft.com/en-us/azure/architecture/best-practices/transient-faults) — best practices по обработке transient-ошибок в облаке
- [Codecentric: Resilience Design Patterns](https://www.codecentric.de/en/knowledge-hub/blog/resilience-design-patterns-retry-fallback-timeout-circuit-breaker) — обзор паттернов с диаграммами

---

*Проверено: 2026-02-19*
