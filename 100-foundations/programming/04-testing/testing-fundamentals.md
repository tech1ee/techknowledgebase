---
title: "Основы тестирования: пирамида, типы и организация тестов"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/testing
  - topic/kotlin
related:
  - "[[tdd-practice]]"
  - "[[mocking-strategies]]"
  - "[[solid-principles]]"
  - "[[kotlin-testing]]"
  - "[[android-testing]]"
---

# Основы тестирования: пирамида, типы и организация тестов

Код без тестов --- мина замедленного действия. Рефакторинг превращается в русскую рулетку, деплой в пятницу --- в приключение на выходные, а фраза "работает на моей машине" --- в мем на ретро. Тесты --- не бюрократия, а страховой полис: 10 минут на написание теста экономят 10 часов на поиск бага в продакшене.

---

## Зачем тестировать

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| "Работает на моей машине" | Нет проверки в изолированном окружении | Баги в проде, ночные алерты |
| "Страшно менять код" | Нет уверенности, что изменение ничего не сломает | Technical debt растёт, код "костенеет" |
| "Релизили неделю, ловили баги" | Ручное тестирование, QA-боттлнек | Медленный time-to-market |
| "Рефакторинг невозможен" | Нет safety net | Legacy-код навсегда |

**Тесты дают:**
- **Уверенность** --- можно менять код и тут же проверить, что ничего не сломалось
- **Документацию** --- тест описывает ожидаемое поведение лучше комментария
- **Дизайн** --- код, который сложно тестировать, обычно плохо спроектирован
- **Скорость** --- автоматическая проверка за секунды вместо ручного прогона за часы

---

## Пирамида тестирования

```
                    /\
                   /  \
                  / E2E \         Медленные, хрупкие
                 /  ~10% \        Проверяют всю систему
                /----------\
               /            \
              / Integration  \    Средняя скорость
             /     ~20%       \   Проверяют связи компонентов
            /------------------\
           /                    \
          /     Unit Tests       \  Быстрые, стабильные
         /        ~70%            \ Проверяют логику изолированно
        /--------------------------\
```

**Время выполнения на 1000 тестов:**

| Уровень | Один тест | 1000 тестов | Стоимость поддержки |
|---------|-----------|-------------|---------------------|
| Unit | 1--50 мс | ~10 секунд | Низкая |
| Integration | 100--500 мс | 1--2 минуты | Средняя |
| E2E | 5--30 секунд | 5--30 минут | Высокая |

### Критика пирамиды: альтернативные модели

Классическая пирамида Мартина Фаулера --- не единственная модель. С развитием инструментов появились альтернативы:

**Testing Trophy** (Kent C. Dodds) --- ставит интеграционные тесты в центр. Логика: unit-тесты проверяют изолированные куски, но настоящие баги живут на стыках. Больше интеграционных тестов = больше уверенности.

```
         Static Analysis    (линтеры, типы)
        ┌──────────────────┐
        │   Unit Tests     │  Маленькая база
        ├──────────────────┤
        │  Integration     │  ← Основной фокус
        │    Tests         │
        ├──────────────────┤
        │   E2E Tests      │  Несколько critical paths
        └──────────────────┘
```

**Testing Diamond** --- равный вес unit и integration, минимум E2E. Хорошо подходит для микросервисов, где интеграция между сервисами критична.

**Что выбрать?** Пирамида --- отличная отправная точка. Для backend с множеством интеграций --- сдвигайтесь к ромбу. Для frontend --- к трофею. Главное --- не форма, а принцип: **чем ниже уровень, тем быстрее и стабильнее тесты**.

> [!info] Kotlin-нюанс
> В Kotlin-экосистеме пирамида по-прежнему актуальна: JUnit 5 для unit/integration, Kotest для property-based, а платформенные инструменты (Espresso, Compose Testing) --- для E2E на Android.

---

## Unit Tests: фундамент

Unit-тест проверяет **одну единицу логики в изоляции**: функцию, метод, класс. Зависимости заменяются дублёрами (моки, стабы, фейки).

**Свойства хорошего unit-теста:**
- **Быстрый** --- миллисекунды
- **Изолированный** --- не зависит от БД, сети, файлов
- **Детерминированный** --- всегда один результат
- **Самодокументирующий** --- имя теста объясняет, что проверяем

### Чистая функция --- идеальный кандидат

```kotlin
fun calculateDiscount(price: Double, discountPercent: Int): Double {
    require(discountPercent in 0..100) { "Скидка должна быть от 0 до 100%" }
    return price * (1 - discountPercent / 100.0)
}
```

```kotlin
import org.junit.jupiter.api.Nested
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import kotlin.test.assertEquals

@DisplayName("calculateDiscount")
class CalculateDiscountTest {

    @Nested
    @DisplayName("корректные значения")
    inner class ValidInputs {

        @Test
        fun `should apply 20% discount to 100`() {
            assertEquals(80.0, calculateDiscount(100.0, 20))
        }

        @Test
        fun `should return same price for zero discount`() {
            assertEquals(100.0, calculateDiscount(100.0, 0))
        }

        @Test
        fun `should return zero for 100% discount`() {
            assertEquals(0.0, calculateDiscount(100.0, 100))
        }

        @ParameterizedTest(name = "цена {0} со скидкой {1}% = {2}")
        @CsvSource(
            "100.0, 20, 80.0",
            "50.0,  10, 45.0",
            "200.0, 50, 100.0",
            "99.99, 10, 89.991"
        )
        fun `should calculate discount correctly`(
            price: Double,
            discount: Int,
            expected: Double
        ) {
            assertEquals(expected, calculateDiscount(price, discount), 0.01)
        }
    }

    @Nested
    @DisplayName("невалидные значения")
    inner class InvalidInputs {

        @Test
        fun `should throw on negative discount`() {
            assertThrows<IllegalArgumentException> {
                calculateDiscount(100.0, -10)
            }
        }

        @Test
        fun `should throw on discount over 100`() {
            assertThrows<IllegalArgumentException> {
                calculateDiscount(100.0, 150)
            }
        }
    }
}
```

> [!info] Kotlin-нюанс
> Имена тестов в обратных кавычках `` `should return empty when no items` `` --- идиоматический Kotlin. Читается как документация, не нужен `@DisplayName`. Работает в JUnit 5 из коробки.

### Assertion-библиотеки для Kotlin

**Kotest matchers** --- выразительные, цепочечные, Kotlin-first:

```kotlin
import io.kotest.matchers.shouldBe
import io.kotest.matchers.collections.shouldContainExactly
import io.kotest.matchers.string.shouldStartWith

@Test
fun `Kotest matchers example`() {
    val result = calculateDiscount(100.0, 20)

    result shouldBe 80.0                       // простое сравнение
    "Hello Kotlin".shouldStartWith("Hello")    // строковые матчеры
    listOf(1, 2, 3).shouldContainExactly(1, 2, 3) // коллекции
}
```

**Сравнение assertion-библиотек:**

| Библиотека | Стиль | Пример |
|------------|-------|--------|
| kotlin.test | Стандартный | `assertEquals(80.0, result)` |
| Kotest matchers | Infix, Kotlin-идиоматичный | `result shouldBe 80.0` |
| AssertJ | Цепочечный (Java-стиль) | `assertThat(result).isEqualTo(80.0)` |
| Strikt | Цепочечный (Kotlin-first) | `expectThat(result).isEqualTo(80.0)` |

---

## Integration Tests: проверка связей

Интеграционные тесты проверяют, что компоненты **корректно работают вместе**: класс + база данных, сервис + HTTP-клиент, несколько модулей.

### База данных: Room in-memory

```kotlin
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertNull

class UserDaoIntegrationTest {

    private lateinit var db: AppDatabase
    private lateinit var dao: UserDao

    @BeforeEach
    fun setup() {
        db = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).allowMainThreadQueries().build()
        dao = db.userDao()
    }

    @AfterEach
    fun teardown() {
        db.close()
    }

    @Test
    fun `should insert and retrieve user by id`() {
        // Arrange
        val user = UserEntity(id = 1, name = "Arman", email = "arman@example.com")

        // Act
        dao.insert(user)
        val found = dao.findById(1)

        // Assert
        assertEquals(user, found)
    }

    @Test
    fun `should return null for non-existent user`() {
        val found = dao.findById(999)
        assertNull(found)
    }
}
```

### Spring Boot + Testcontainers

```kotlin
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.web.client.TestRestTemplate
import org.springframework.http.HttpStatus
import org.testcontainers.containers.PostgreSQLContainer
import org.testcontainers.junit.jupiter.Container
import org.testcontainers.junit.jupiter.Testcontainers
import kotlin.test.assertEquals

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class UserApiIntegrationTest {

    companion object {
        @Container
        val postgres = PostgreSQLContainer("postgres:16-alpine").apply {
            withDatabaseName("testdb")
            withUsername("test")
            withPassword("test")
        }
    }

    @Autowired
    lateinit var restTemplate: TestRestTemplate

    @Autowired
    lateinit var userRepository: UserRepository

    @Test
    fun `POST users should create user and return 201`() {
        val request = CreateUserRequest(
            email = "new@user.com",
            name = "New User"
        )

        val response = restTemplate.postForEntity(
            "/api/users", request, UserResponse::class.java
        )

        assertEquals(HttpStatus.CREATED, response.statusCode)
        assertEquals("new@user.com", response.body?.email)

        // Проверяем, что реально сохранилось в БД
        val saved = userRepository.findByEmail("new@user.com")
        assertEquals("New User", saved?.name)
    }

    @Test
    fun `POST users should return 409 for duplicate email`() {
        val request = CreateUserRequest(email = "dupe@test.com", name = "First")
        restTemplate.postForEntity("/api/users", request, UserResponse::class.java)

        val duplicate = restTemplate.postForEntity(
            "/api/users", request, UserResponse::class.java
        )

        assertEquals(HttpStatus.CONFLICT, duplicate.statusCode)
    }
}
```

> [!info] Kotlin-нюанс
> `companion object` с `@Container` --- необходимость JUnit 5 Testcontainers. В Kotlin нет `static`, поэтому контейнер живёт в companion object. Альтернатива --- Kotest extensions для Testcontainers, где lifecycle управляется автоматически.

---

## E2E Tests: последняя линия обороны

E2E-тесты проверяют систему целиком --- от UI до базы данных. Они медленные, хрупкие, дорогие в поддержке. Но незаменимы для critical paths.

```
Тестируй E2E:
  - Critical paths: регистрация, оплата, логин
  - Happy paths основных фич
  - Smoke tests после деплоя

НЕ тестируй E2E:
  - Каждый edge case (для этого unit-тесты)
  - Все комбинации данных
  - Внутреннюю логику

Правило: если можно проверить на нижнем уровне --- проверяй там.
E2E = последняя линия обороны, не первая.
```

Подробности E2E для Android --- в [[android-testing]] (Espresso, Compose Testing Rule). Для backend --- Ktor `testApplication {}` или Spring `@SpringBootTest`.

---

## Организация тестов

### Паттерн AAA (Arrange-Act-Assert)

Три чётких фазы в каждом тесте:

```kotlin
class UserServiceTest {

    private val repository = FakeUserRepository()
    private val hasher = FakePasswordHasher()
    private val service = UserService(repository, hasher)

    @Test
    fun `should create user with hashed password`() {
        // Arrange --- подготовка данных
        val request = CreateUserRequest(
            email = "test@example.com",
            password = "secret123"
        )

        // Act --- выполнение действия
        val user = service.createUser(request)

        // Assert --- проверка результата
        assertEquals("test@example.com", user.email)
        assertTrue(hasher.wasCalledWith("secret123"))
        assertNotEquals("secret123", user.passwordHash)
    }
}
```

### Given-When-Then (BDD-стиль с Kotest)

```kotlin
import io.kotest.core.spec.style.BehaviorSpec
import io.kotest.matchers.shouldBe

class AccountSpec : BehaviorSpec({

    given("аккаунт с балансом 1000 рублей") {
        val account = Account(balance = 1000)

        `when`("пользователь снимает 400 рублей") {
            account.withdraw(400)

            then("баланс должен быть 600 рублей") {
                account.balance shouldBe 600
            }
        }

        `when`("пользователь пытается снять 1500 рублей") {
            then("должно выбросить InsufficientFundsException") {
                val exception = shouldThrow<InsufficientFundsException> {
                    account.withdraw(1500)
                }
                exception.message shouldBe "Недостаточно средств"
            }
        }
    }
})
```

> [!info] Kotlin-нюанс
> `when` --- зарезервированное слово в Kotlin. В Kotest BehaviorSpec используется `` `when` `` в обратных кавычках. Это единственный "неудобный" момент --- но BDD-читаемость того стоит.

### Naming conventions

Хорошие имена тестов --- документация, которая всегда актуальна:

```kotlin
// Паттерн: should_expectedResult_when_condition
@Test
fun `should return empty list when no items exist`() { ... }

@Test
fun `should throw IllegalArgumentException when email is invalid`() { ... }

@Test
fun `should send notification when order is placed`() { ... }

// Альтернатива: given_when_then в имени
@Test
fun `given empty cart, when adding item, then cart size is 1`() { ... }
```

**Плохие имена:**
```kotlin
@Test fun test1() { ... }                    // Что тестируем?
@Test fun testUserService() { ... }          // Что именно?
@Test fun `it works`() { ... }               // Что "works"?
```

### Test fixtures: фабрики и data class

```kotlin
// Вместо повторения создания объектов --- фабрика
object TestUsers {
    fun customer(
        id: Long = 1,
        name: String = "Test User",
        email: String = "test@example.com",
        role: Role = Role.CUSTOMER
    ) = User(id = id, name = name, email = email, role = role)

    fun admin(
        id: Long = 99,
        name: String = "Admin",
        email: String = "admin@example.com"
    ) = customer(id = id, name = name, email = email, role = Role.ADMIN)
}

// Использование в тестах
@Test
fun `should allow admin to delete users`() {
    val admin = TestUsers.admin()
    val target = TestUsers.customer(id = 42)

    val result = service.deleteUser(admin, target.id)

    assertTrue(result.isSuccess)
}

@Test
fun `should deny customer from deleting users`() {
    val customer = TestUsers.customer()
    val target = TestUsers.customer(id = 42)

    assertThrows<AccessDeniedException> {
        service.deleteUser(customer, target.id)
    }
}
```

> [!info] Kotlin-нюанс
> `data class` + параметры по умолчанию --- мощная комбинация для тестов. Создавай объект с дефолтами, переопределяй только то, что важно для конкретного теста. `object TestUsers` --- singleton-фабрика, доступная везде без инстанцирования.

### @BeforeEach и lifecycle

```kotlin
class OrderServiceTest {

    private lateinit var repository: FakeOrderRepository
    private lateinit var notifier: FakeNotifier
    private lateinit var service: OrderService

    @BeforeEach
    fun setup() {
        repository = FakeOrderRepository()
        notifier = FakeNotifier()
        service = OrderService(repository, notifier)
    }

    @Test
    fun `should save order to repository`() {
        service.placeOrder(TestOrders.standard())
        assertEquals(1, repository.savedOrders.size)
    }

    @Test
    fun `should send notification after order placed`() {
        service.placeOrder(TestOrders.standard())
        assertEquals(1, notifier.sentNotifications.size)
    }
}
```

---

## Что тестировать, а что нет

```
ТЕСТИРУЙ:
  + Бизнес-логику (расчёты, валидация, правила)
  + Edge cases (граничные значения, пустые списки, null)
  + Error handling (что происходит при ошибках)
  + Публичный API классов
  + Регрессии (найден баг → написан тест → фикс)
  + Чистые функции (вход → выход, без side effects)

НЕ ТЕСТИРУЙ:
  - Private методы напрямую (тестируй через публичный API)
  - Тривиальный код (data class, геттеры/сеттеры)
  - Сторонние библиотеки (их уже протестировали)
  - Реализацию (тестируй ПОВЕДЕНИЕ)
  - Конструкторы и конфигурацию
```

```kotlin
// Плохо: тестируем реализацию
@Test
fun `should use map to transform items`() {
    val spy = spyk(listOf(1, 2, 3))
    service.processItems(spy)
    verify { spy.map(any()) }  // Зачем? Внутренняя деталь
}

// Хорошо: тестируем поведение
@Test
fun `should double all prices`() {
    val result = service.processItems(listOf(
        Item("A", price = 10),
        Item("B", price = 20)
    ))

    assertEquals(listOf(20, 40), result.map { it.price })
}
```

---

## Kotlin-специфика в тестах

### @Nested inner class для группировки

```kotlin
@DisplayName("UserValidator")
class UserValidatorTest {

    private val validator = UserValidator()

    @Nested
    @DisplayName("валидация email")
    inner class EmailValidation {

        @Test
        fun `should accept valid email`() {
            assertTrue(validator.isValidEmail("user@example.com"))
        }

        @Test
        fun `should reject email without @`() {
            assertFalse(validator.isValidEmail("userexample.com"))
        }
    }

    @Nested
    @DisplayName("валидация пароля")
    inner class PasswordValidation {

        @Test
        fun `should reject password shorter than 8 chars`() {
            assertFalse(validator.isValidPassword("short"))
        }

        @Test
        fun `should accept strong password`() {
            assertTrue(validator.isValidPassword("Str0ngP@ss"))
        }
    }
}
```

### Extension functions для тестовых утилит

```kotlin
// Расширения для удобства в тестах
fun <T> Result<T>.shouldBeSuccess(): T {
    assertTrue(this.isSuccess, "Expected Success but got Failure: ${this.exceptionOrNull()}")
    return this.getOrThrow()
}

fun <T> Result<T>.shouldBeFailure(): Throwable {
    assertTrue(this.isFailure, "Expected Failure but got Success: ${this.getOrNull()}")
    return this.exceptionOrNull()!!
}

// Использование
@Test
fun `should return success for valid order`() {
    val result = service.placeOrder(TestOrders.valid())
    val order = result.shouldBeSuccess()
    assertEquals(OrderStatus.PLACED, order.status)
}

@Test
fun `should return failure for empty cart`() {
    val result = service.placeOrder(TestOrders.emptyCart())
    val error = result.shouldBeFailure()
    assertTrue(error is EmptyCartException)
}
```

### internal visibility для test-only кода

```kotlin
// Production code
class PaymentProcessor(
    private val gateway: PaymentGateway,
    private val logger: Logger
) {
    // Публичный API
    fun processPayment(order: Order): PaymentResult { ... }

    // Доступно только в том же модуле (и в тестах!)
    internal fun calculateFee(amount: Double): Double {
        return amount * 0.029 + 0.30 // 2.9% + $0.30
    }
}

// В тестах (тот же модуль) --- можно обращаться к internal
@Test
fun `should calculate fee as 2_9 percent plus 30 cents`() {
    val processor = PaymentProcessor(mockk(), mockk())
    assertEquals(3.20, processor.calculateFee(100.0), 0.01)
}
```

### Companion object как фабрика тестовых данных

```kotlin
data class Order(
    val id: String,
    val userId: String,
    val items: List<OrderItem>,
    val status: OrderStatus,
    val createdAt: Instant
) {
    companion object {
        // Фабрика для тестов --- удобнее отдельного object
        fun testOrder(
            id: String = "order-1",
            userId: String = "user-1",
            items: List<OrderItem> = listOf(OrderItem.testItem()),
            status: OrderStatus = OrderStatus.PENDING,
            createdAt: Instant = Instant.parse("2026-01-01T00:00:00Z")
        ) = Order(id, userId, items, status, createdAt)
    }
}

data class OrderItem(
    val productId: String,
    val quantity: Int,
    val price: Double
) {
    companion object {
        fun testItem(
            productId: String = "prod-1",
            quantity: Int = 1,
            price: Double = 29.99
        ) = OrderItem(productId, quantity, price)
    }
}

// Использование: минимум шума, максимум читаемости
@Test
fun `should calculate total for order`() {
    val order = Order.testOrder(
        items = listOf(
            OrderItem.testItem(price = 10.0, quantity = 2),
            OrderItem.testItem(price = 5.0, quantity = 3)
        )
    )
    assertEquals(35.0, order.total())
}
```

---

## Структура тестов в проекте

```
src/
├── main/kotlin/com/example/
│   ├── domain/
│   │   ├── User.kt
│   │   ├── Order.kt
│   │   └── OrderService.kt
│   ├── data/
│   │   ├── UserRepository.kt
│   │   └── OrderRepository.kt
│   └── api/
│       └── UserController.kt
│
├── test/kotlin/com/example/         ← Unit-тесты
│   ├── domain/
│   │   ├── UserTest.kt
│   │   ├── OrderTest.kt
│   │   └── OrderServiceTest.kt
│   ├── fixtures/
│   │   ├── TestUsers.kt             ← Фабрики тестовых данных
│   │   └── TestOrders.kt
│   └── fakes/
│       ├── FakeUserRepository.kt    ← Fake-реализации
│       └── FakeOrderRepository.kt
│
└── integrationTest/kotlin/com/example/  ← Integration-тесты
    ├── data/
    │   └── UserRepositoryIntegrationTest.kt
    └── api/
        └── UserControllerIntegrationTest.kt
```

**Gradle: разделение source sets:**

```kotlin
// build.gradle.kts
sourceSets {
    create("integrationTest") {
        kotlin.srcDir("src/integrationTest/kotlin")
        resources.srcDir("src/integrationTest/resources")
        compileClasspath += sourceSets.main.get().output + sourceSets.test.get().output
        runtimeClasspath += sourceSets.main.get().output + sourceSets.test.get().output
    }
}

tasks.register<Test>("integrationTest") {
    testClassesDirs = sourceSets["integrationTest"].output.classesDirs
    classpath = sourceSets["integrationTest"].runtimeClasspath
    useJUnitPlatform()
    shouldRunAfter(tasks.test)
}

dependencies {
    testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
    testImplementation("io.kotest:kotest-assertions-core:5.8.0")
    testImplementation("io.mockk:mockk:1.13.9")
    testImplementation("org.jetbrains.kotlin:kotlin-test")

    "integrationTestImplementation"("org.testcontainers:postgresql:1.19.3")
    "integrationTestImplementation"("org.testcontainers:junit-jupiter:1.19.3")
}
```

---

## Coverage: не гонись за 100%

```
Coverage показывает: какой код ВЫПОЛНЯЛСЯ при тестах.
Coverage НЕ показывает: какой код ПРОВЕРЯЛСЯ.

100% coverage + плохие assert-ы = ложная уверенность.
```

```kotlin
// 100% coverage, 0% пользы
fun divide(a: Int, b: Int): Int = a / b

@Test
fun `divides numbers`() {
    assertEquals(5, divide(10, 2))  // coverage: 100%
    // НЕ проверено: деление на ноль, отрицательные, overflow
}
```

**Разумные цели:**
- 80% line coverage как минимум
- Критичный код (платежи, авторизация): 90%+
- Новый код: обязательно покрыт тестами
- **Mutation testing** (PIT для JVM) --- проверяет качество тестов: меняет код и смотрит, падают ли тесты

---

## Подводные камни

### Хрупкие тесты (brittle tests)

```kotlin
// Плохо: зависит от порядка
@Test
fun `should return users`() {
    val users = service.getUsers()
    assertEquals("Alice", users[0].name)  // А если порядок изменится?
    assertEquals("Bob", users[1].name)
}

// Хорошо: проверяем наличие, не порядок
@Test
fun `should return all users`() {
    val names = service.getUsers().map { it.name }
    assertTrue(names.containsAll(listOf("Alice", "Bob")))
}
```

### Flaky tests

```
Flaky test --- тест, который то проходит, то падает.

Причины:
  - Shared state между тестами
  - Зависимость от порядка выполнения
  - Race conditions, timing issues
  - Внешние зависимости (сеть, файлы)

Решения:
  - Изолировать тесты (@BeforeEach создаёт свежий state)
  - Мокать внешние зависимости
  - Детерминированные данные (не Random без seed)
  - Explicit waits вместо Thread.sleep в E2E
  - Retry с логированием для анализа причин
```

### Тесты ради галочки

```kotlin
// Бесполезный тест
@Test
fun `test user`() {
    val user = User("test@example.com")
    assertNotNull(user)  // Что это доказывает?
}

// Полезный тест --- документация поведения
@Test
fun `should normalize email to lowercase`() {
    val user = User("Test@EXAMPLE.COM")
    assertEquals("test@example.com", user.email)
}
```

---

## Проверь себя

<details>
<summary>1. Почему пропорция 70/20/10 в пирамиде --- именно такая?</summary>

Unit (70%): быстрые (мс), стабильные, изолированные --- основа обратной связи. Integration (20%): проверяют связи между компонентами, медленнее (секунды), но ловят баги на стыках. E2E (10%): вся система целиком, медленные (минуты), хрупкие. Инвертированная пирамида (много E2E, мало unit) ведёт к медленным, нестабильным тестам и "страху менять код".
</details>

<details>
<summary>2. Чем Testing Trophy отличается от пирамиды?</summary>

Testing Trophy (Kent C. Dodds) ставит интеграционные тесты в центр, а не unit-тесты. Логика: реальные баги живут на стыках компонентов. Unit-тесты проверяют изолированные куски, но пропускают ошибки интеграции. Trophy также добавляет Static Analysis (типы, линтеры) как базовый уровень.
</details>

<details>
<summary>3. В чём разница между AAA и Given-When-Then?</summary>

AAA (Arrange-Act-Assert) --- структурный паттерн: подготовь данные, выполни действие, проверь результат. Given-When-Then --- BDD-стиль, фокус на поведении: "при условии X, когда происходит Y, тогда результат Z". По сути --- одно и то же, но GWT читается как спецификация. В Kotest GWT реализован через `BehaviorSpec`.
</details>

<details>
<summary>4. Почему нельзя тестировать private методы напрямую?</summary>

Private метод --- деталь реализации. Его можно изменить при рефакторинге без изменения поведения. Тест private метода привязывается к реализации, а не к поведению. Тестируй через публичный API: если private метод влияет на результат --- это будет видно через публичные методы. Если не влияет --- зачем он нужен?
</details>

<details>
<summary>5. Когда использовать @Nested inner class в JUnit 5?</summary>

`@Nested inner class` группирует связанные тесты. Используй для: разделения по сценариям (валидные/невалидные входы), разных состояний SUT, разных методов одного класса. `inner` обязателен в Kotlin --- иначе вложенный класс не имеет доступа к внешнему экземпляру, и JUnit не сможет его инстанцировать.
</details>

---

## Ключевые карточки

**Какие уровни в пирамиде тестирования и их пропорции?**
?
Unit (70%): быстрые (мс), изолированные, проверяют логику. Integration (20%): средняя скорость, проверяют связи компонентов. E2E (10%): медленные, хрупкие, проверяют всю систему. Чем ниже уровень --- тем быстрее и стабильнее.

**Что такое паттерн AAA?**
?
Arrange --- подготовка данных и зависимостей. Act --- выполнение тестируемого действия. Assert --- проверка результата. Чёткое разделение делает тесты читаемыми.

**Зачем в Kotlin использовать `@Nested inner class`?**
?
Группировка связанных тестов: валидные/невалидные входы, разные сценарии. `inner` обязателен --- JUnit 5 требует доступ к внешнему экземпляру. Вложенные классы создают читаемую иерархию в отчёте.

**Как именовать тесты в Kotlin?**
?
Обратные кавычки: `` `should return empty when no items exist` ``. Читается как документация. Паттерн: `should_expectedResult_when_condition`. Не нужен `@DisplayName`, работает в JUnit 5 из коробки.

**Зачем нужны test fixture фабрики?**
?
Объект-фабрика (`object TestUsers`) или companion object с параметрами по умолчанию. Тест создаёт объект одной строкой, переопределяя только значимые поля. Убирает дублирование, делает тесты читаемыми. `data class` + дефолты --- идеальная комбинация.

**Почему 100% coverage не гарантирует качество?**
?
Coverage показывает какой код выполнялся, не какой проверялся. `divide(10, 2)` даёт 100% coverage, но не проверяет деление на ноль. Mutation testing (PIT) --- настоящая проверка: меняет код и смотрит, падают ли тесты.

**Что такое Testing Trophy?**
?
Модель Kent C. Dodds: Static Analysis → Unit → **Integration** (фокус) → E2E. Ставит интеграционные тесты в центр, потому что реальные баги живут на стыках компонентов, а не внутри изолированных функций.

**Что такое flaky test и как бороться?**
?
Тест, который то проходит, то падает. Причины: shared state, timing issues, зависимость от порядка, внешние сервисы. Решения: изоляция через `@BeforeEach`, моки для внешних зависимостей, детерминированные данные, explicit waits вместо `Thread.sleep`.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[tdd-practice]] | TDD: пишем тест до кода, Red-Green-Refactor |
| Углубиться | [[mocking-strategies]] | MockK, фейки, стратегии подмены зависимостей |
| Практика | [[android-testing]] | Специфика тестирования Android-приложений |
| Android | [[android-mvvm-deep-dive]] | Тестирование ViewModel и UiState с Turbine |
| Android | [[android-mvi-deep-dive]] | Тестирование Reducer как pure function |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Martin Fowler: Test Pyramid](https://martinfowler.com/bliki/TestPyramid.html) | Article | Классическая модель пирамиды тестирования |
| 2 | [Kent Beck: Test-Driven Development by Example](https://www.oreilly.com/library/view/test-driven-development/0321146530/) | Book | Основы TDD и тестирования |
| 3 | Москала М. "Effective Kotlin" (2024) | Book | Kotlin-идиомы, включая тестирование |
| 4 | [JUnit 5 User Guide](https://junit.org/junit5/docs/current/user-guide/) | Docs | @Nested, @ParameterizedTest, lifecycle |
| 5 | [Kotest Framework](https://kotest.io/docs/quickstart/) | Docs | BehaviorSpec, matchers, property testing |
| 6 | [MockK Documentation](https://mockk.io/) | Docs | Kotlin-first мокирование |
| 7 | [Philipp Hauer: Best Practices for Unit Testing in Kotlin](https://phauer.com/2018/best-practices-unit-testing-kotlin/) | Article | Kotlin-специфичные паттерны тестирования |
| 8 | [Martin Fowler: On the Diverse And Fantastical Shapes of Testing](https://martinfowler.com/articles/2021-test-shapes.html) | Article | Пирамида vs Trophy vs Diamond |
| 9 | [Testcontainers](https://testcontainers.com/) | Docs | Интеграционное тестирование с контейнерами |
| 10 | [Baeldung: JUnit 5 vs Kotest](https://www.baeldung.com/kotlin/kotest-vs-junit-5) | Article | Сравнение фреймворков для Kotlin |

---

*Последнее обновление: 2026-02-19*
