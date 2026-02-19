---
title: "Mocking: стратегии подмены зависимостей в тестах"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/testing
  - topic/kotlin
related:
  - "[[testing-fundamentals]]"
  - "[[tdd-practice]]"
  - "[[solid-principles]]"
  - "[[kotlin-testing]]"
  - "[[android-async-testing]]"
---

# Mocking: стратегии подмены зависимостей в тестах

У тебя есть сервис, который отправляет SMS. Ты хочешь проверить, что при регистрации пользователя SMS уходит. Поднимать SMS-шлюз в каждом тесте? Платить за каждое сообщение? Ждать ответа 3 секунды? Нет --- ты подменяешь зависимость дублёром. Но какой дублёр выбрать: mock, stub, fake, spy? И почему 80% проблем в тестах --- это "слишком много моков"?

---

## Таксономия тест-дублёров (Gerard Meszaros)

Жерар Мезарош в книге "xUnit Test Patterns" (2007) ввёл пять типов **test doubles** --- объектов, заменяющих реальные зависимости в тестах:

```
Test Double
├── Dummy     — заглушка-заполнитель, никогда не вызывается
├── Stub      — фиксированные ответы, без проверок вызовов
├── Mock      — запрограммированные ожидания + верификация вызовов
├── Spy       — обёртка реального объекта, записывает вызовы
└── Fake      — рабочая реализация, упрощённая для тестов
```

### Dummy --- заполнитель

Передаётся как параметр, но никогда не используется. Нужен, чтобы удовлетворить сигнатуру.

```kotlin
class DummyLogger : Logger {
    override fun log(message: String) { /* ничего */ }
    override fun error(message: String, throwable: Throwable) { /* ничего */ }
}

@Test
fun `should calculate total without logging`() {
    // Logger нужен конструктору, но в этом тесте не используется
    val service = PricingService(DummyLogger())
    assertEquals(150.0, service.calculateTotal(listOf(50.0, 100.0)))
}
```

### Stub --- фиксированные ответы

Возвращает заранее заданные значения. Не проверяет, как был вызван.

```kotlin
class StubUserRepository : UserRepository {
    override fun findById(id: Long): User? = User(
        id = id, name = "Stub User", email = "stub@test.com"
    )
    override fun findByEmail(email: String): User? = null
    override fun save(user: User): User = user
}

@Test
fun `should greet user by name`() {
    val repo = StubUserRepository()
    val service = GreetingService(repo)

    val greeting = service.greetUser(userId = 42)

    assertEquals("Привет, Stub User!", greeting)
}
```

### Mock --- ожидания + верификация

Запрограммирован на конкретные вызовы. Проверяет, **что** было вызвано, **сколько раз**, **с какими аргументами**.

```kotlin
@Test
fun `should send welcome email after registration`() {
    val emailService = mockk<EmailService>()
    every { emailService.send(any(), any(), any()) } just Runs

    val service = RegistrationService(emailService)
    service.register("user@example.com", "password123")

    verify(exactly = 1) {
        emailService.send(
            to = "user@example.com",
            subject = "Добро пожаловать!",
            body = any()
        )
    }
}
```

### Spy --- обёртка реального объекта

Работает как реальный объект, но записывает вызовы. Можно подменить отдельные методы.

```kotlin
@Test
fun `should log expensive operations`() {
    val realCalculator = PricingCalculator()
    val spy = spyk(realCalculator)

    val result = spy.calculate(100.0, 20)

    assertEquals(80.0, result)  // Реальный расчёт
    verify { spy.calculate(100.0, 20) }  // Вызов записан
}
```

### Fake --- упрощённая реализация

Работающая реализация, но непригодная для продакшена. Классический пример --- in-memory репозиторий.

```kotlin
class FakeUserRepository : UserRepository {
    private val users = mutableListOf<User>()
    private var nextId = 1L

    override fun save(user: User): User {
        val saved = user.copy(id = nextId++)
        users.add(saved)
        return saved
    }

    override fun findById(id: Long): User? =
        users.find { it.id == id }

    override fun findByEmail(email: String): User? =
        users.find { it.email == email }

    override fun findAll(): List<User> = users.toList()

    override fun delete(id: Long) {
        users.removeAll { it.id == id }
    }

    // Вспомогательный метод для тестов
    fun count(): Int = users.size
}
```

### Когда что использовать

| Тип | Когда | Пример |
|-----|-------|--------|
| **Dummy** | Параметр нужен, но не используется | Logger в тесте расчётов |
| **Stub** | Нужен фиксированный ответ | Репозиторий, всегда возвращающий одного юзера |
| **Mock** | Важно проверить вызов (behavior verification) | Отправка email, запись в аудит-лог |
| **Spy** | Нужен реальный объект + запись вызовов | Проверка, что кэш обращался к реальному источнику |
| **Fake** | Нужна работающая реализация без инфраструктуры | In-memory БД, FakeHttpClient |

> [!info] Kotlin-нюанс
> В Kotlin `data class` идеально подходит для фейков: `FakeUserRepository` с `MutableList<User>` --- полноценная in-memory реализация за 20 строк. А `object` вместо класса --- если фейк stateless.

---

## MockK: глубокое погружение

MockK --- мокирующая библиотека, написанная специально для Kotlin. Поддерживает корутины, extension functions, object singletons, inline classes.

### Базовые операции

```kotlin
import io.mockk.*
import io.mockk.junit5.MockKExtension
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.extension.ExtendWith

@ExtendWith(MockKExtension::class)
class OrderServiceTest {

    // Strict mock --- бросает исключение на незапрограммированный вызов
    private val repository = mockk<OrderRepository>()
    private val service = OrderService(repository)

    @Test
    fun `should save order to repository`() {
        val order = Order(id = "1", items = listOf("item-1"))

        every { repository.save(any()) } returns order

        val result = service.placeOrder(order)

        assertEquals(order, result)
        verify { repository.save(order) }
    }
}
```

### Relaxed mock --- значения по умолчанию

```kotlin
// Strict mock: незапрограммированный вызов → исключение
val strict = mockk<UserService>()
// strict.getUser(1)  → io.mockk.MockKException

// Relaxed mock: возвращает дефолты (0, "", false, emptyList, null)
val relaxed = mockk<UserService>(relaxed = true)
val user = relaxed.getUser(1)  // → null (для nullable) или дефолтный объект

// Relaxed unitFun: только Unit-функции автоматически проходят
val partial = mockk<NotificationService>(relaxUnitFun = true)
partial.notify("hello")  // OK, Unit-функция
// partial.getStatus()   // Всё ещё бросит MockKException
```

### every / returns / throws / answers

```kotlin
val repo = mockk<UserRepository>()

// Простой return
every { repo.findById(1) } returns User(1, "Alice")

// Возврат null
every { repo.findById(999) } returns null

// Бросить исключение
every { repo.findById(-1) } throws IllegalArgumentException("Invalid ID")

// Разные ответы при последовательных вызовах
every { repo.findById(1) } returnsMany listOf(
    User(1, "Alice"),
    User(1, "Alice Updated")
)

// Динамический ответ через answers
every { repo.save(any()) } answers {
    val input = firstArg<User>()
    input.copy(id = 42)  // "Сохраняем" с присвоенным ID
}

// Unit-функции
every { repo.delete(any()) } just Runs
```

### coEvery / coVerify для корутин

```kotlin
class UserViewModelTest {

    private val repository = mockk<UserRepository>()
    private val viewModel = UserViewModel(repository)

    @Test
    fun `should load user from repository`() = runTest {
        // coEvery для suspend-функций
        coEvery { repository.fetchUser(1) } returns User(1, "Alice")

        viewModel.loadUser(1)

        assertEquals("Alice", viewModel.userName.value)

        // coVerify для suspend-функций
        coVerify { repository.fetchUser(1) }
    }

    @Test
    fun `should handle network error`() = runTest {
        coEvery { repository.fetchUser(any()) } throws
            IOException("Network error")

        viewModel.loadUser(1)

        assertTrue(viewModel.error.value is NetworkError)
    }
}
```

> [!info] Kotlin-нюанс
> `coEvery` и `coVerify` --- обязательны для `suspend` функций. Обычные `every`/`verify` не работают с корутинами. Забыл `co`-префикс --- получишь невнятную ошибку в рантайме. Это самая частая ошибка новичков с MockK.

### slot() --- захват аргументов

```kotlin
@Test
fun `should save user with normalized email`() {
    val slot = slot<User>()
    every { repository.save(capture(slot)) } answers {
        slot.captured.copy(id = 1)
    }

    service.register("Test@EXAMPLE.COM", "password")

    val savedUser = slot.captured
    assertEquals("test@example.com", savedUser.email)  // Email нормализован
}

// Захват нескольких вызовов
@Test
fun `should save all items separately`() {
    val savedItems = mutableListOf<OrderItem>()
    every { repository.saveItem(capture(savedItems)) } just Runs

    service.processOrder(order)

    assertEquals(3, savedItems.size)
    assertEquals("item-1", savedItems[0].productId)
}
```

### spyk() --- частичное мокирование

```kotlin
@Test
fun `should use real method but mock expensive call`() {
    val service = spyk(OrderService(repository))

    // Реальные методы работают, но один --- подменяем
    every { service.calculateShipping(any()) } returns 0.0

    val total = service.calculateTotal(order)

    // calculateTotal вызвал реальный calculateSubtotal
    // но shipping = 0 (мок)
    assertEquals(100.0, total)
}
```

### mockkStatic() --- мокирование статических / top-level функций

```kotlin
// Мокирование top-level функции
@Test
fun `should use current time from system`() {
    mockkStatic(Instant::class)
    val fixedTime = Instant.parse("2026-01-01T00:00:00Z")
    every { Instant.now() } returns fixedTime

    val event = eventService.createEvent("Meeting")

    assertEquals(fixedTime, event.createdAt)

    unmockkStatic(Instant::class)  // Обязательно очистить!
}

// Мокирование extension function
@Test
fun `should mock extension function`() {
    mockkStatic("com.example.ExtensionsKt")  // Полное имя файла + Kt

    every { "test".toSlug() } returns "test-slug"

    assertEquals("test-slug", "test".toSlug())

    unmockkStatic("com.example.ExtensionsKt")
}
```

### mockkObject() --- мокирование Kotlin object

```kotlin
object Analytics {
    fun track(event: String, properties: Map<String, Any> = emptyMap()) {
        // Реальная отправка в аналитику
    }
}

@Test
fun `should track order placed event`() {
    mockkObject(Analytics)
    every { Analytics.track(any(), any()) } just Runs

    orderService.placeOrder(order)

    verify {
        Analytics.track(
            "order_placed",
            match { it["orderId"] == order.id }
        )
    }

    unmockkObject(Analytics)
}
```

> [!info] Kotlin-нюанс
> `mockkStatic` и `mockkObject` --- мощные, но опасные инструменты. Они изменяют глобальное состояние. Всегда вызывай `unmockkStatic` / `unmockkObject` в `@AfterEach` или используй `mockkStatic(...) { ... }` с блоком (автоматическая очистка). Иначе тесты начнут влиять друг на друга.

### Полная шпаргалка MockK

| Операция | Обычные функции | Suspend-функции |
|----------|-----------------|-----------------|
| Настройка поведения | `every { ... }` | `coEvery { ... }` |
| Верификация | `verify { ... }` | `coVerify { ... }` |
| Ответ | `returns`, `throws`, `answers` | то же самое |
| Захват аргумента | `slot<T>()`, `capture(slot)` | то же самое |
| Подсчёт вызовов | `verify(exactly = 2)` | `coVerify(exactly = 2)` |
| Порядок вызовов | `verifyOrder { ... }` | `coVerifyOrder { ... }` |
| Все вызовы проверены | `confirmVerified(mock)` | то же самое |
| Нет вызовов | `verify { mock wasNot Called }` | то же самое |

---

## Fake-реализации: когда фейк лучше мока

### Полноценный FakeUserRepository

```kotlin
class FakeUserRepository : UserRepository {

    private val store = mutableMapOf<Long, User>()
    private val sequence = AtomicLong(1)

    override suspend fun save(user: User): User {
        val saved = if (user.id == 0L) {
            user.copy(id = sequence.getAndIncrement())
        } else {
            user
        }
        store[saved.id] = saved
        return saved
    }

    override suspend fun findById(id: Long): User? = store[id]

    override suspend fun findByEmail(email: String): User? =
        store.values.find { it.email == email }

    override suspend fun findAll(): List<User> = store.values.toList()

    override suspend fun delete(id: Long) {
        store.remove(id)
    }

    // Утилиты для тестов
    fun count(): Int = store.size
    fun clear() = store.clear()
    fun contains(id: Long): Boolean = store.containsKey(id)
}
```

### Когда фейк лучше мока

```
ИСПОЛЬЗУЙ FAKE:                        ИСПОЛЬЗУЙ MOCK:
───────────────                         ──────────────
+ Сложное поведение (CRUD)              + Простая верификация вызова
+ Shared across many tests              + Одноразовый сценарий
+ Поведение зависит от состояния        + Нужно проверить "был ли вызван"
+ Не хочешь привязываться к реализации  + Нужно проверить аргументы
+ Тестируешь state (что сохранилось)    + Тестируешь behavior (что вызвали)
```

**Пример: фейк используется в 50 тестах**

```kotlin
// С моком: каждый тест настраивает every/returns
@Test
fun `test 1 of 50 with mock`() {
    every { repo.findById(1) } returns User(1, "Alice")
    every { repo.save(any()) } answers { firstArg() }
    // ... ещё 3 строки настройки
}

// С фейком: zero setup, просто работает
@Test
fun `test 1 of 50 with fake`() {
    repo.save(User(name = "Alice", email = "alice@test.com"))
    val result = service.getUserProfile(userId = 1)
    assertEquals("Alice", result.name)
}
```

### Fake для HTTP-клиента

```kotlin
class FakeHttpClient : HttpClient {

    private val responses = mutableMapOf<String, HttpResponse>()
    val requestLog = mutableListOf<HttpRequest>()

    fun stubResponse(url: String, response: HttpResponse) {
        responses[url] = response
    }

    override suspend fun get(url: String): HttpResponse {
        requestLog.add(HttpRequest(method = "GET", url = url))
        return responses[url]
            ?: HttpResponse(status = 404, body = "Not found")
    }

    override suspend fun post(url: String, body: String): HttpResponse {
        requestLog.add(HttpRequest(method = "POST", url = url, body = body))
        return responses[url]
            ?: HttpResponse(status = 404, body = "Not found")
    }
}

@Test
fun `should fetch user from API`() = runTest {
    val client = FakeHttpClient()
    client.stubResponse(
        "https://api.example.com/users/1",
        HttpResponse(status = 200, body = """{"id": 1, "name": "Alice"}""")
    )

    val service = UserApiService(client)
    val user = service.getUser(1)

    assertEquals("Alice", user.name)
    assertEquals(1, client.requestLog.size)
    assertEquals("GET", client.requestLog[0].method)
}
```

---

## DI для тестируемости

Dependency Injection --- фундамент тестируемого кода. Без DI подмена зависимостей невозможна (или требует грязных хаков вроде reflection).

### Конструктор --- главный инструмент

```kotlin
// Плохо: зависимость создаётся внутри
class OrderService {
    private val repo = PostgresOrderRepository()  // Как подменить?
    private val mailer = SmtpMailer()              // Нужен SMTP?!
}

// Хорошо: зависимости через конструктор
class OrderService(
    private val repo: OrderRepository,     // Interface
    private val mailer: Mailer             // Interface
) {
    fun placeOrder(order: Order): OrderResult {
        repo.save(order)
        mailer.send(order.userEmail, "Заказ оформлен")
        return OrderResult.Success(order.id)
    }
}

// В проде: реальные реализации
val service = OrderService(
    repo = PostgresOrderRepository(dataSource),
    mailer = SmtpMailer(smtpConfig)
)

// В тестах: фейки или моки
val service = OrderService(
    repo = FakeOrderRepository(),
    mailer = mockk(relaxUnitFun = true)
)
```

### Interface-based design

```kotlin
// Интерфейс --- контракт
interface PaymentGateway {
    suspend fun charge(amount: Money, card: CardToken): PaymentResult
    suspend fun refund(paymentId: String): RefundResult
}

// Продакшен-реализация
class StripePaymentGateway(
    private val client: StripeClient
) : PaymentGateway {
    override suspend fun charge(amount: Money, card: CardToken): PaymentResult {
        val response = client.createCharge(amount.cents, card.token)
        return PaymentResult.Success(response.id)
    }
    override suspend fun refund(paymentId: String): RefundResult { ... }
}

// Тестовая реализация
class FakePaymentGateway : PaymentGateway {
    val charges = mutableListOf<Pair<Money, CardToken>>()
    var shouldFail = false

    override suspend fun charge(amount: Money, card: CardToken): PaymentResult {
        if (shouldFail) return PaymentResult.Failure("Payment declined")
        charges.add(amount to card)
        return PaymentResult.Success("fake-payment-${charges.size}")
    }
    override suspend fun refund(paymentId: String): RefundResult {
        return RefundResult.Success
    }
}

// Тест с фейком
@Test
fun `should charge correct amount for order`() = runTest {
    val gateway = FakePaymentGateway()
    val service = CheckoutService(gateway)

    service.checkout(order)

    assertEquals(1, gateway.charges.size)
    assertEquals(Money(9999, Currency.RUB), gateway.charges[0].first)
}

// Тест с ошибкой оплаты
@Test
fun `should handle payment failure gracefully`() = runTest {
    val gateway = FakePaymentGateway().apply { shouldFail = true }
    val service = CheckoutService(gateway)

    val result = service.checkout(order)

    assertTrue(result is CheckoutResult.PaymentFailed)
}
```

---

## Мокирование Flow и корутин

### Мокирование Flow с MockK

```kotlin
interface NewsRepository {
    fun getNewsStream(): Flow<List<Article>>
    suspend fun refreshNews(): List<Article>
}

class NewsViewModelTest {

    private val repository = mockk<NewsRepository>()
    private lateinit var viewModel: NewsViewModel

    @Test
    fun `should collect articles from flow`() = runTest {
        // flowOf --- простейший мок для Flow
        every { repository.getNewsStream() } returns flowOf(
            listOf(Article("1", "Breaking News")),
            listOf(Article("1", "Breaking News"), Article("2", "Update"))
        )

        viewModel = NewsViewModel(repository)
        viewModel.startCollecting()

        advanceUntilIdle()

        assertEquals(2, viewModel.articles.value.size)
    }

    @Test
    fun `should handle flow error`() = runTest {
        // flow builder для сложных сценариев
        every { repository.getNewsStream() } returns flow {
            emit(listOf(Article("1", "News")))
            throw IOException("Connection lost")
        }

        viewModel = NewsViewModel(repository)
        viewModel.startCollecting()

        advanceUntilIdle()

        assertTrue(viewModel.error.value is ConnectionError)
    }

    @Test
    fun `should refresh news on pull-to-refresh`() = runTest {
        val freshArticles = listOf(Article("3", "Fresh"))
        every { repository.getNewsStream() } returns flowOf(emptyList())
        coEvery { repository.refreshNews() } returns freshArticles

        viewModel = NewsViewModel(repository)
        viewModel.refresh()

        advanceUntilIdle()

        coVerify { repository.refreshNews() }
    }
}
```

### data class для test data factories

```kotlin
// Фабрика тестовых данных --- одно место, вся конфигурация
object TestArticles {
    fun article(
        id: String = "article-1",
        title: String = "Test Article",
        content: String = "Lorem ipsum",
        author: String = "Test Author",
        publishedAt: Instant = Instant.parse("2026-01-01T00:00:00Z"),
        tags: List<String> = emptyList()
    ) = Article(
        id = id,
        title = title,
        content = content,
        author = author,
        publishedAt = publishedAt,
        tags = tags
    )

    fun breakingNews() = article(
        id = "breaking-1",
        title = "Breaking: Important Event",
        tags = listOf("breaking", "top")
    )

    fun archivedArticle() = article(
        id = "old-1",
        title = "Old News",
        publishedAt = Instant.parse("2020-01-01T00:00:00Z")
    )
}

// Использование
@Test
fun `should filter breaking news`() {
    val articles = listOf(
        TestArticles.breakingNews(),
        TestArticles.article(title = "Regular"),
        TestArticles.archivedArticle()
    )

    val result = newsFilter.filterBreaking(articles)

    assertEquals(1, result.size)
    assertEquals("Breaking: Important Event", result[0].title)
}
```

---

## Анти-паттерн: Over-Mocking

### Признаки

```
Тест ломается при рефакторинге, хотя поведение не изменилось
                               ↓
             Тестируется setup мока, а не реальное поведение
                               ↓
                5+ моков в одном тесте
                               ↓
           Тест читается как "verify that mock was called"
                               ↓
                  Over-mocking 🔴
```

### Пример: тест мока, а не кода

```kotlin
// ПЛОХО: 6 моков, тест проверяет вызовы, а не результат
@Test
fun `should process order`() {
    val repo = mockk<OrderRepository>()
    val payment = mockk<PaymentGateway>()
    val inventory = mockk<InventoryService>()
    val notifier = mockk<NotificationService>()
    val logger = mockk<Logger>()
    val metrics = mockk<MetricsCollector>()

    every { repo.save(any()) } returns mockOrder
    every { payment.charge(any()) } returns PaymentResult.Success
    every { inventory.reserve(any()) } returns true
    every { notifier.notify(any()) } just Runs
    every { logger.info(any()) } just Runs
    every { metrics.record(any()) } just Runs

    service.processOrder(order)

    // Тестируем что? Что моки были вызваны? Это тест МОКОВ, не КОДА.
    verify { repo.save(any()) }
    verify { payment.charge(any()) }
    verify { inventory.reserve(any()) }
    verify { notifier.notify(any()) }
}
```

### Решение: фейки + проверка состояния

```kotlin
// ХОРОШО: фейки, проверяем результат
@Test
fun `should process order and persist it`() {
    val repo = FakeOrderRepository()
    val payment = FakePaymentGateway()
    val service = OrderService(repo, payment)

    val result = service.processOrder(order)

    // Проверяем ПОВЕДЕНИЕ, не вызовы
    assertTrue(result.isSuccess)
    assertEquals(1, repo.count())
    assertEquals(OrderStatus.PAID, repo.findById(result.orderId)?.status)
    assertEquals(order.total, payment.charges.first().amount)
}
```

### Правило: количество моков --- индикатор качества дизайна

```
1-2 мока  → Нормально
3 мока    → Подумай, можно ли упростить
4+ моков  → Класс делает слишком много → разбей на меньшие

Решения:
  - Вынеси группу зависимостей в отдельный класс
  - Используй Facade для группировки
  - Замени моки фейками (одна реализация на все тесты)
  - Проверяй state, а не behavior (результат, а не вызовы)
```

---

## Kotlin-специфика: мокирование корутин

### Тестирование Flow-цепочек

```kotlin
@Test
fun `should transform and filter flow`() = runTest {
    val source = flowOf(1, 2, 3, 4, 5)

    val result = source
        .filter { it % 2 == 0 }
        .map { it * 10 }
        .toList()

    assertEquals(listOf(20, 40), result)
}

@Test
fun `should retry on transient error`() = runTest {
    var attempt = 0
    val unreliableFlow = flow {
        attempt++
        if (attempt < 3) throw IOException("Transient error")
        emit("success")
    }.retry(3) { it is IOException }

    val result = unreliableFlow.toList()

    assertEquals(listOf("success"), result)
    assertEquals(3, attempt)
}
```

### Мокирование object с mockkObject

```kotlin
object DateProvider {
    fun now(): LocalDate = LocalDate.now()
    fun today(): String = now().toString()
}

class SubscriptionService(private val repo: SubscriptionRepository) {

    fun isExpired(subscription: Subscription): Boolean {
        return subscription.expiresAt.isBefore(DateProvider.now())
    }
}

@Test
fun `should detect expired subscription`() {
    mockkObject(DateProvider)
    every { DateProvider.now() } returns LocalDate.of(2026, 3, 1)

    val subscription = Subscription(
        expiresAt = LocalDate.of(2026, 2, 15)  // Истекла 2 недели назад
    )

    assertTrue(service.isExpired(subscription))

    unmockkObject(DateProvider)
}
```

> [!info] Kotlin-нюанс
> Лучше: вместо `mockkObject(DateProvider)` передавать `Clock` через конструктор. Мокирование `object` --- глобальное состояние, потенциальный источник flaky-тестов. Используй `mockkObject` только для legacy-кода или сторонних библиотек, которые нельзя изменить.

---

## Рецепты: частые сценарии

### Мокирование suspend-функции с задержкой

```kotlin
@Test
fun `should show loading state while fetching`() = runTest {
    coEvery { repository.fetchData() } coAnswers {
        delay(1000)  // Имитация сетевого запроса
        listOf("item-1", "item-2")
    }

    viewModel.loadData()

    // Сразу после вызова --- loading
    assertTrue(viewModel.isLoading.value)

    advanceTimeBy(1001)

    // После задержки --- данные загружены
    assertFalse(viewModel.isLoading.value)
    assertEquals(2, viewModel.items.value.size)
}
```

### Верификация порядка вызовов

```kotlin
@Test
fun `should validate before saving`() {
    val validator = mockk<OrderValidator>()
    val repo = mockk<OrderRepository>()
    every { validator.validate(any()) } returns ValidationResult.Valid
    every { repo.save(any()) } returns order

    val service = OrderService(validator, repo)
    service.placeOrder(order)

    verifyOrder {
        validator.validate(order)  // Сначала валидация
        repo.save(order)           // Потом сохранение
    }
}
```

### Matcher для сложных аргументов

```kotlin
@Test
fun `should create audit log with correct details`() {
    val auditLog = mockk<AuditLog>(relaxUnitFun = true)
    val service = UserService(repo, auditLog)

    service.deleteUser(adminId = 1, targetId = 42)

    verify {
        auditLog.record(match { entry ->
            entry.action == "DELETE_USER" &&
            entry.performedBy == 1L &&
            entry.targetId == 42L &&
            entry.timestamp != null
        })
    }
}
```

---

## Проверь себя

<details>
<summary>1. Чем Mock отличается от Stub?</summary>

**Stub** --- фиксированные ответы, без проверки вызовов. Для state verification: "в каком состоянии система после действия?"

**Mock** --- запрограммированные ожидания + верификация. Для behavior verification: "какие методы были вызваны, с какими аргументами, сколько раз?"

Правило Мезароша: Stub для проверки результата (state), Mock для проверки взаимодействия (behavior).
</details>

<details>
<summary>2. Когда Fake лучше Mock?</summary>

Fake лучше когда: (1) сложное поведение с состоянием (CRUD-репозиторий), (2) дублёр используется в десятках тестов (один Fake вместо 50 настроек mock), (3) важно проверить состояние а не вызовы, (4) нужна реалистичная реализация (FakeHttpClient с логированием запросов). Mock лучше для одноразовых верификаций: "был ли вызван метод X с аргументом Y".
</details>

<details>
<summary>3. Зачем нужен coEvery вместо every?</summary>

`coEvery` --- для `suspend`-функций. Обычный `every` не может обработать корутину: он не запускает корутинный контекст. `coEvery` работает внутри корутины и корректно обрабатывает `suspend`. Аналогично: `coVerify` вместо `verify`, `coAnswers` вместо `answers`. Забыл `co`-префикс --- получишь ошибку "suspend function called outside of coroutine".
</details>

<details>
<summary>4. Почему over-mocking --- это анти-паттерн?</summary>

5+ моков = тест проверяет настройку моков, а не реальное поведение кода. Тесты ломаются при рефакторинге (хотя поведение не изменилось). Решения: заменить моки фейками, разбить класс на меньшие (SRP), проверять state вместо behavior. Количество моков --- индикатор качества дизайна: много зависимостей = класс делает слишком много.
</details>

<details>
<summary>5. Как замокировать Kotlin object?</summary>

`mockkObject(MyObject)` подменяет все методы singleton-объекта. Обязательно `unmockkObject(MyObject)` после теста (или `@AfterEach`), иначе мок "утечёт" в другие тесты. Лучшая практика: `mockkObject(MyObject) { ... }` с блоком --- автоматическая очистка. Но ещё лучше: передавать зависимости через конструктор вместо обращения к `object` напрямую.
</details>

---

## Ключевые карточки

**Пять типов test doubles (Meszaros)?**
?
Dummy: заполнитель, никогда не вызывается. Stub: фиксированные ответы, без проверки вызовов. Mock: запрограммированные ожидания + верификация. Spy: обёртка реального объекта, записывает вызовы. Fake: работающая упрощённая реализация (in-memory БД).

**MockK: every vs coEvery?**
?
`every { ... }` --- для обычных функций. `coEvery { ... }` --- для `suspend`-функций. `co`-префикс запускает корутинный контекст. Аналогично: `verify`/`coVerify`, `answers`/`coAnswers`. Забыл `co` для suspend --- ошибка в рантайме.

**Когда использовать Fake вместо Mock?**
?
Fake лучше при: сложном поведении (CRUD), использовании в десятках тестов, проверке state (что сохранилось). Mock лучше при: одноразовой верификации вызова, проверке аргументов, проверке порядка вызовов. Fake = state verification, Mock = behavior verification.

**Как захватить аргумент в MockK?**
?
`val slot = slot<User>()` + `every { repo.save(capture(slot)) }`. После вызова: `slot.captured` содержит переданный аргумент. Для нескольких вызовов: `mutableListOf<User>()` вместо `slot`. Полезно для проверки, что сервис трансформирует данные перед передачей.

**Что такое over-mocking и как бороться?**
?
5+ моков в тесте = тест проверяет настройку моков, не поведение. Ломается при рефакторинге. Решения: фейки вместо моков, разбить класс (SRP), проверять state вместо behavior, Facade для группировки зависимостей. Количество моков --- метрика качества дизайна.

**Как мокировать Kotlin object?**
?
`mockkObject(Analytics)` + `every { Analytics.track(...) }`. Обязательно `unmockkObject` в `@AfterEach`. Лучше: блок `mockkObject(Analytics) { ... }` с автоочисткой. Ещё лучше: DI через конструктор вместо прямого обращения к `object`.

**Как мокировать extension function?**
?
`mockkStatic("com.example.ExtensionsKt")` --- полное имя файла + суффикс `Kt`. Затем `every { "test".toSlug() } returns "..."`. Обязательно `unmockkStatic` после. Для extension внутри класса --- мокируется сам класс.

**MockK: relaxed vs strict mock?**
?
Strict (по умолчанию): незапрограммированный вызов бросает исключение. Безопаснее --- сразу видишь забытые настройки. Relaxed (`mockk(relaxed = true)`): возвращает дефолты (0, "", false, null). Удобнее, но может скрыть ошибки. `relaxUnitFun = true` --- компромисс: только Unit-функции проходят автоматически.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Предыдущий шаг | [[testing-fundamentals]] | Основы: пирамида, типы тестов, организация |
| Связанная тема | [[tdd-practice]] | TDD: Outside-In использует моки активно |
| Практика | [[android-async-testing]] | Тестирование корутин и Flow в Android |
| Углубиться | [[solid-principles]] | DI и интерфейсы --- основа тестируемости |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Gerard Meszaros: xUnit Test Patterns (2007)](http://xunitpatterns.com/) | Book | Таксономия test doubles: Dummy, Stub, Mock, Spy, Fake |
| 2 | [Martin Fowler: Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) | Article | State vs Behavior verification, классика |
| 3 | [Steve Freeman, Nat Pryce: Growing Object-Oriented Software, Guided by Tests](https://www.growing-object-oriented-software.com/) | Book | Mock-first подход, London School |
| 4 | [MockK Documentation](https://mockk.io/) | Docs | Официальная документация MockK |
| 5 | [MockK Guidebook: Coroutines](https://notwoods.github.io/mockk-guidebook/docs/mocking/coroutines/) | Guide | coEvery, coVerify для suspend-функций |
| 6 | [MockK Guidebook: Static & Object Mocking](https://notwoods.github.io/mockk-guidebook/docs/mocking/static/) | Guide | mockkStatic, mockkObject |
| 7 | Москала М. "Effective Kotlin" (2024) | Book | Kotlin-идиомы для тестируемого кода |
| 8 | [James Shore: Testing Without Mocks](https://www.jamesshore.com/v2/projects/nullables/testing-without-mocks) | Article | Альтернатива мокам: Nullables pattern |
| 9 | [Sandeep Kella: Mocking Suspend Functions with MockK](https://proandroiddev.com/mocking-suspend-functions-and-flows-with-mockk-part-4-of-5-49a266eeca1d) | Article | Практическое руководство по корутинам + MockK |
| 10 | [Baeldung: MockK for Kotlin](https://www.baeldung.com/kotlin/mockk) | Article | Полный обзор возможностей MockK |

---

*Последнее обновление: 2026-02-19*
