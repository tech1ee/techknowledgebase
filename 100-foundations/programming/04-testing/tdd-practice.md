---
title: "TDD: разработка через тестирование"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/testing
  - topic/tdd
  - topic/kotlin
related:
  - "[[testing-fundamentals]]"
  - "[[mocking-strategies]]"
  - "[[solid-principles]]"
  - "[[kotlin-testing]]"
---

# TDD: разработка через тестирование

"Сначала тест, потом код" --- звучит как совет из книжки. На практике TDD --- это не про тесты. Это про дизайн. Когда ты пишешь тест до кода, ты вынужден продумать API класса, определить зависимости и зафиксировать ожидаемое поведение --- ещё до того, как напишешь первую строку реализации.

---

## Краткая история

**1999** --- Кент Бек формализует TDD в рамках Extreme Programming (XP) на проекте Chrysler C3 в Детройте.

**2002** --- выходит книга "Test-Driven Development: By Example" --- библия TDD. Бек демонстрирует подход на двух примерах: мультивалютная арифметика и xUnit-фреймворк, написанный через TDD.

**2004** --- Стив Фримен и Нат Прайс развивают идею в "Лондонскую школу" TDD (mock-first, outside-in). Их книга "Growing Object-Oriented Software, Guided by Tests" (2009) --- второй обязательный источник.

**Сегодня** --- TDD не умер и не стал обязательным. Это инструмент: мощный для бизнес-логики и алгоритмов, избыточный для CRUD и UI.

---

## Цикл Red-Green-Refactor

```
┌─────────────────────────────────────────────────┐
│                                                 │
│    ┌───────┐      ┌───────┐      ┌──────────┐  │
│    │  RED  │─────▶│ GREEN │─────▶│ REFACTOR │  │
│    │       │      │       │      │          │  │
│    │Пишем  │      │Пишем  │      │Улучшаем  │  │
│    │тест   │      │мини-  │      │код       │  │
│    │(пада- │      │мальный│      │(тесты    │  │
│    │ет)    │      │код    │      │проходят) │  │
│    └───────┘      └───────┘      └──────────┘  │
│        ▲                              │         │
│        └──────────────────────────────┘         │
│                                                 │
└─────────────────────────────────────────────────┘
```

**RED** --- пишем тест для несуществующего поведения. Тест должен упасть. Если он проходит --- что-то не так.

**GREEN** --- пишем **минимальный** код, чтобы тест прошёл. Не красивый, не оптимальный --- просто рабочий. Даже захардкоженное значение допустимо.

**REFACTOR** --- улучшаем код при проходящих тестах. Убираем дублирование, выделяем абстракции, переименовываем. Тесты --- страховка.

---

## Три закона TDD (Robert C. Martin)

1. **Нельзя** писать продакшен-код, пока нет падающего теста
2. **Нельзя** написать больше теста, чем достаточно для одного падения (даже ошибка компиляции --- это падение)
3. **Нельзя** написать больше продакшен-кода, чем достаточно для прохождения текущего теста

Эти три закона создают **микроцикл**: тест → код → тест → код. Шаги крошечные --- 30 секунд на итерацию.

---

## TDD на практике: строим Stack пошагово

Построим типобезопасный `Stack<T>` через TDD. Каждый шаг --- один цикл Red-Green-Refactor.

### Шаг 1: пустой стек (RED → GREEN)

```kotlin
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class StackTest {

    @Test
    fun `newly created stack should be empty`() {
        val stack = Stack<Int>()
        assertTrue(stack.isEmpty())
    }
}
```

Тест падает: `Stack` не существует. Пишем минимум:

```kotlin
class Stack<T> {
    fun isEmpty(): Boolean = true
}
```

Тест проходит. Рефакторить нечего --- идём дальше.

### Шаг 2: push делает стек непустым (RED → GREEN)

```kotlin
@Test
fun `stack with one element should not be empty`() {
    val stack = Stack<Int>()
    stack.push(42)
    assertFalse(stack.isEmpty())
}
```

Падает --- нет метода `push`. Минимальный код:

```kotlin
class Stack<T> {
    private var size = 0

    fun isEmpty(): Boolean = size == 0

    fun push(element: T) {
        size++
    }
}
```

### Шаг 3: pop возвращает последний элемент (RED → GREEN)

```kotlin
@Test
fun `pop should return the last pushed element`() {
    val stack = Stack<Int>()
    stack.push(42)
    assertEquals(42, stack.pop())
}
```

Минимальный код:

```kotlin
class Stack<T> {
    private val elements = mutableListOf<T>()

    fun isEmpty(): Boolean = elements.isEmpty()

    fun push(element: T) {
        elements.add(element)
    }

    fun pop(): T {
        return elements.removeLast()
    }
}
```

### Шаг 4: pop на пустом стеке бросает исключение (RED → GREEN)

```kotlin
@Test
fun `pop on empty stack should throw EmptyStackException`() {
    val stack = Stack<Int>()
    assertThrows<EmptyStackException> {
        stack.pop()
    }
}
```

```kotlin
class EmptyStackException : RuntimeException("Stack is empty")

class Stack<T> {
    private val elements = mutableListOf<T>()

    fun isEmpty(): Boolean = elements.isEmpty()

    fun push(element: T) {
        elements.add(element)
    }

    fun pop(): T {
        if (elements.isEmpty()) throw EmptyStackException()
        return elements.removeLast()
    }
}
```

### Шаг 5: LIFO-порядок (RED → GREEN)

```kotlin
@Test
fun `pop should return elements in LIFO order`() {
    val stack = Stack<Int>()
    stack.push(1)
    stack.push(2)
    stack.push(3)

    assertEquals(3, stack.pop())
    assertEquals(2, stack.pop())
    assertEquals(1, stack.pop())
    assertTrue(stack.isEmpty())
}
```

Тест проходит без изменений --- `removeLast()` уже обеспечивает LIFO!

### Шаг 6: REFACTOR --- добавляем peek и size

Все тесты проходят. Можно улучшить API:

```kotlin
class Stack<T> {
    private val elements = mutableListOf<T>()

    val size: Int get() = elements.size

    fun isEmpty(): Boolean = elements.isEmpty()

    fun push(element: T) {
        elements.add(element)
    }

    fun pop(): T {
        if (isEmpty()) throw EmptyStackException()
        return elements.removeLast()
    }

    fun peek(): T {
        if (isEmpty()) throw EmptyStackException()
        return elements.last()
    }
}
```

И тесты для новых методов:

```kotlin
@Test
fun `peek should return top element without removing it`() {
    val stack = Stack<Int>()
    stack.push(42)

    assertEquals(42, stack.peek())
    assertEquals(1, stack.size)   // элемент на месте
}

@Test
fun `size should reflect number of elements`() {
    val stack = Stack<Int>()
    assertEquals(0, stack.size)
    stack.push(1)
    assertEquals(1, stack.size)
    stack.push(2)
    assertEquals(2, stack.size)
    stack.pop()
    assertEquals(1, stack.size)
}
```

> [!info] Kotlin-нюанс
> Обрати внимание: мы не проектировали `Stack` заранее. TDD вынудил нас двигаться маленькими шагами --- и дизайн "вырос" из тестов. `data class`, `mutableListOf`, `removeLast()` --- всё идиоматический Kotlin.

---

## Outside-In vs Inside-Out TDD

### Inside-Out (Detroit/Chicago School)

Начинаем с доменных объектов, двигаемся наружу к API. **Моки минимальны** --- используем реальные объекты или фейки.

```
Domain Models → Services → Controllers → API

Плюсы:
  + Минимум моков --- тесты стабильнее при рефакторинге
  + Дизайн "вырастает" снизу вверх
  + Проще начать --- не нужно продумывать весь API заранее

Минусы:
  - Можно написать много кода, который потом не нужен
  - Интеграция компонентов может преподнести сюрпризы
```

```kotlin
// Inside-Out: начинаем с доменной модели
class MoneyTest {

    @Test
    fun `should add two amounts in same currency`() {
        val a = Money(100, Currency.RUB)
        val b = Money(200, Currency.RUB)
        assertEquals(Money(300, Currency.RUB), a + b)
    }

    @Test
    fun `should throw when adding different currencies`() {
        val rub = Money(100, Currency.RUB)
        val usd = Money(50, Currency.USD)
        assertThrows<CurrencyMismatchException> { rub + usd }
    }
}

// Потом переходим к сервису
class PaymentServiceTest {

    @Test
    fun `should calculate total from order items`() {
        val items = listOf(
            OrderItem(price = Money(100, Currency.RUB), quantity = 2),
            OrderItem(price = Money(50, Currency.RUB), quantity = 3)
        )
        val service = PaymentService()
        assertEquals(Money(350, Currency.RUB), service.calculateTotal(items))
    }
}
```

### Outside-In (London School)

Начинаем с acceptance test на верхнем уровне, спускаемся вниз. **Моки активно используются** для ещё не написанных зависимостей.

```
Acceptance Test → Controller → Service → Repository

Плюсы:
  + Чёткое понимание конечного API с самого начала
  + Не пишем лишнего --- каждый модуль нужен acceptance тесту
  + Хорошо для командной работы (API-контракт определён рано)

Минусы:
  - Много моков --- тесты хрупкие при рефакторинге
  - Требует дисциплины --- легко скатиться в тестирование моков
```

```kotlin
// Outside-In: начинаем с верхнего уровня
class PlaceOrderUseCaseTest {

    private val orderRepository = mockk<OrderRepository>()
    private val paymentGateway = mockk<PaymentGateway>()
    private val notifier = mockk<OrderNotifier>()
    private val useCase = PlaceOrderUseCase(orderRepository, paymentGateway, notifier)

    @Test
    fun `should place order, charge payment, and notify`() {
        // Arrange
        val order = TestOrders.standard()
        every { paymentGateway.charge(any()) } returns PaymentResult.Success
        every { orderRepository.save(any()) } returns order
        every { notifier.notify(any()) } just Runs

        // Act
        val result = useCase.execute(order)

        // Assert
        assertTrue(result.isSuccess)
        verifyOrder {
            orderRepository.save(any())
            paymentGateway.charge(any())
            notifier.notify(any())
        }
    }
}
```

### Какой стиль выбрать?

| Критерий | Inside-Out | Outside-In |
|----------|-----------|------------|
| Начальная точка | Доменная модель | Acceptance test |
| Моки | Минимум (фейки) | Активно |
| Дизайн | Вырастает снизу | Определяется сверху |
| Хрупкость тестов | Низкая | Средняя/высокая |
| Лучше для | Алгоритмы, доменная логика | API-first, микросервисы |

**На практике:** большинство опытных разработчиков комбинируют оба подхода. Inside-Out для доменной логики, Outside-In для API и use cases.

---

## Когда применять TDD

```
TDD РАБОТАЕТ ОТЛИЧНО:                  TDD ИЗБЫТОЧЕН:
─────────────────────                   ────────────────
+ Бизнес-логика                        - Простой CRUD
+ Алгоритмы и расчёты                  - UI-код (лучше snapshot тесты)
+ Сложные state machines               - Glue code / конфигурация
+ Валидация и правила                  - Прототипирование (требования
+ Критичный код (платежи, security)      меняются быстрее кода)
+ Код с чёткими требованиями           - Exploratory work
+ Парное программирование (ping-pong)  - Код, зависящий от внешних API
```

---

## Практический TDD в Kotlin

### Kotest BehaviorSpec для BDD-стиля

```kotlin
import io.kotest.core.spec.style.BehaviorSpec
import io.kotest.matchers.shouldBe
import io.kotest.assertions.throwables.shouldThrow

class PasswordValidatorSpec : BehaviorSpec({

    val validator = PasswordValidator()

    given("пароль короче 8 символов") {
        val password = "short"

        `when`("валидируем") {
            val result = validator.validate(password)

            then("результат невалидный") {
                result.isValid shouldBe false
            }
            then("ошибка содержит информацию о длине") {
                result.errors shouldContain "Пароль должен быть не короче 8 символов"
            }
        }
    }

    given("пароль без заглавных букв") {
        val password = "alllowercase1"

        `when`("валидируем") {
            val result = validator.validate(password)

            then("результат невалидный") {
                result.isValid shouldBe false
            }
            then("ошибка содержит информацию о заглавных буквах") {
                result.errors shouldContain "Пароль должен содержать заглавную букву"
            }
        }
    }

    given("надёжный пароль") {
        val password = "Str0ngP@ssword"

        `when`("валидируем") {
            val result = validator.validate(password)

            then("результат валидный") {
                result.isValid shouldBe true
                result.errors shouldBe emptyList()
            }
        }
    }
})
```

Реализация, "выросшая" из тестов:

```kotlin
data class ValidationResult(
    val isValid: Boolean,
    val errors: List<String>
)

class PasswordValidator {

    private data class Rule(
        val check: (String) -> Boolean,
        val message: String
    )

    private val rules = listOf(
        Rule({ it.length >= 8 }, "Пароль должен быть не короче 8 символов"),
        Rule({ it.any { c -> c.isUpperCase() } }, "Пароль должен содержать заглавную букву"),
        Rule({ it.any { c -> c.isDigit() } }, "Пароль должен содержать цифру"),
        Rule({ it.any { c -> !c.isLetterOrDigit() } }, "Пароль должен содержать спецсимвол"),
    )

    fun validate(password: String): ValidationResult {
        val errors = rules
            .filter { !it.check(password) }
            .map { it.message }

        return ValidationResult(
            isValid = errors.isEmpty(),
            errors = errors
        )
    }
}
```

> [!info] Kotlin-нюанс
> `data class Rule` вместо interface + классы. Kotlin поощряет лёгкие структуры. TDD привёл нас к чистому дизайну: `List<Rule>` с `filter/map` --- идиоматический Kotlin, никаких `if-else` цепочек.

### Property-based testing: находим edge cases автоматически

Вместо перебора конкретных значений --- описываем **свойство**, которое должно выполняться для любого входа. Kotest генерирует сотни (по умолчанию 1000) случайных значений, включая edge cases (0, -1, Int.MAX_VALUE, пустые строки).

```kotlin
import io.kotest.core.spec.style.FunSpec
import io.kotest.property.forAll
import io.kotest.property.Arb
import io.kotest.property.arbitrary.int
import io.kotest.property.arbitrary.positiveInt
import io.kotest.matchers.shouldBe
import io.kotest.matchers.ints.shouldBeGreaterThanOrEqual

class MathPropertiesSpec : FunSpec({

    test("сложение коммутативно") {
        forAll(Arb.int(), Arb.int()) { a, b ->
            a + b == b + a
        }
    }

    test("абсолютное значение всегда >= 0") {
        forAll(Arb.int()) { n ->
            kotlin.math.abs(n.toLong()) >= 0  // toLong для Int.MIN_VALUE
        }
    }

    test("reverse строки дважды возвращает оригинал") {
        forAll(Arb.string()) { s ->
            s.reversed().reversed() == s
        }
    }
})
```

Пример посерьёзнее --- тестируем бизнес-логику:

```kotlin
import io.kotest.core.spec.style.FunSpec
import io.kotest.property.forAll
import io.kotest.property.Arb
import io.kotest.property.arbitrary.int
import io.kotest.property.arbitrary.double
import io.kotest.matchers.doubles.shouldBeGreaterThanOrEqual
import io.kotest.matchers.doubles.shouldBeLessThanOrEqual

class DiscountPropertySpec : FunSpec({

    test("скидка всегда уменьшает или сохраняет цену") {
        forAll(
            Arb.double(1.0..10000.0),    // цена
            Arb.int(0..100)               // процент скидки
        ) { price, discount ->
            val result = calculateDiscount(price, discount)
            result <= price && result >= 0.0
        }
    }

    test("0% скидка не меняет цену") {
        forAll(Arb.double(1.0..10000.0)) { price ->
            calculateDiscount(price, 0) == price
        }
    }

    test("100% скидка даёт 0") {
        forAll(Arb.double(1.0..10000.0)) { price ->
            calculateDiscount(price, 100) == 0.0
        }
    }
})
```

> [!info] Kotlin-нюанс
> Kotest `Arb` (arbitrary) --- генераторы случайных значений. Встроенные edge cases: для `Arb.int()` всегда включает 0, -1, Int.MAX_VALUE, Int.MIN_VALUE. Для `Arb.string()` --- пустую строку и строку из одного символа. Это находит баги, которые ты бы не написал руками.

### @ParameterizedTest с @CsvSource

Когда property-based testing избыточен, а один `@Test` недостаточен --- data-driven тесты:

```kotlin
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.CsvSource
import org.junit.jupiter.params.provider.MethodSource
import kotlin.test.assertEquals

class FizzBuzzTest {

    @ParameterizedTest(name = "FizzBuzz({0}) = {1}")
    @CsvSource(
        "1, 1",
        "2, 2",
        "3, Fizz",
        "5, Buzz",
        "6, Fizz",
        "10, Buzz",
        "15, FizzBuzz",
        "30, FizzBuzz"
    )
    fun `should return correct FizzBuzz result`(input: Int, expected: String) {
        assertEquals(expected, fizzBuzz(input))
    }

    // Для сложных данных --- @MethodSource
    companion object {
        @JvmStatic
        fun edgeCases() = listOf(
            arguments(0, "FizzBuzz"),
            arguments(-3, "Fizz"),
            arguments(-5, "Buzz"),
            arguments(Int.MAX_VALUE, (Int.MAX_VALUE).toString())
        )
    }

    @ParameterizedTest(name = "edge case: FizzBuzz({0}) = {1}")
    @MethodSource("edgeCases")
    fun `should handle edge cases`(input: Int, expected: String) {
        assertEquals(expected, fizzBuzz(input))
    }
}
```

> [!info] Kotlin-нюанс
> `@MethodSource` требует `@JvmStatic` в `companion object` --- ограничение JUnit 5. В Kotlin нет `static`, поэтому `companion object` + `@JvmStatic` --- обязательная комбинация для параметризованных тестов с `@MethodSource`.

---

## Типичные ошибки в TDD

### 1. Тестируем реализацию, а не поведение

```kotlin
// Плохо: привязка к внутренней реализации
@Test
fun `should call repository save exactly once`() {
    service.createUser(request)
    verify(exactly = 1) { repository.save(any()) }
    // Если завтра save заменим на batch insert --- тест сломается
}

// Хорошо: проверяем результат
@Test
fun `should persist user and return it`() {
    val result = service.createUser(request)

    assertEquals("test@example.com", result.email)
    assertTrue(repository.exists("test@example.com"))
}
```

### 2. Слишком большие шаги

```kotlin
// Плохо: сразу пишем тест на весь сценарий
@Test
fun `should register user, hash password, send email, and create session`() {
    // 4 проверки = 4 причины для падения = непонятно, что сломалось
}

// Хорошо: один тест --- одно поведение
@Test
fun `should hash password before saving`() { ... }

@Test
fun `should send welcome email after registration`() { ... }

@Test
fun `should create session for new user`() { ... }
```

### 3. Слишком много моков

```kotlin
// Код-запах: 5+ моков = проблема в дизайне
@Test
fun `should process order`() {
    val repo = mockk<OrderRepository>()
    val payment = mockk<PaymentGateway>()
    val inventory = mockk<InventoryService>()
    val notifier = mockk<NotificationService>()
    val logger = mockk<Logger>()
    val metrics = mockk<MetricsCollector>()
    // 6 моков = класс делает слишком много
    // Решение: разбить на меньшие классы
}
```

### 4. Тестируем private-методы

```kotlin
// Плохо: лезем в приватные детали
@Test
fun `should format phone number correctly`() {
    // Пытаемся через reflection вызвать private formatPhone()
    val method = UserService::class.java
        .getDeclaredMethod("formatPhone", String::class.java)
    method.isAccessible = true
    // ...
}

// Хорошо: тестируем через публичный API
@Test
fun `should save user with formatted phone`() {
    val result = service.createUser(
        CreateUserRequest(phone = "89161234567")
    )
    assertEquals("+7 (916) 123-45-67", result.phone)
}
```

### 5. Медленные тесты

```kotlin
// Плохо: Thread.sleep в тесте
@Test
fun `should expire session after timeout`() {
    val session = sessionService.create()
    Thread.sleep(5000)  // 5 секунд на один тест!
    assertTrue(session.isExpired())
}

// Хорошо: абстрагируем время
@Test
fun `should expire session after timeout`() {
    val clock = FakeClock(Instant.parse("2026-01-01T00:00:00Z"))
    val session = sessionService.create(clock)

    clock.advance(Duration.ofMinutes(31))

    assertTrue(session.isExpired())  // Мгновенно!
}
```

---

## TDD и архитектура

TDD --- не только про тесты. Код, который сложно тестировать, обычно плохо спроектирован. TDD вынуждает:

**Dependency Injection** --- если зависимости создаются внутри класса, их не подменить в тесте. TDD заставляет передавать зависимости через конструктор.

```kotlin
// До TDD: зависимость захардкожена
class OrderService {
    private val repo = PostgresOrderRepository()  // Как тестировать?
    private val mailer = SmtpMailer()              // Нужен SMTP-сервер!
}

// После TDD: зависимости инжектируются
class OrderService(
    private val repo: OrderRepository,    // Interface
    private val mailer: Mailer            // Interface
)
```

**Маленькие функции** --- сложно написать тест для метода на 200 строк. TDD приводит к коротким, сфокусированным функциям.

**Чёткие интерфейсы** --- моки работают через интерфейсы. TDD заставляет определять контракты до реализации.

**Single Responsibility** --- если у теста 10 arrange-строк и 5 assert-ов, класс делает слишком много.

---

## Ping-Pong TDD (парное программирование)

Один разработчик пишет тест (RED), другой --- минимальный код (GREEN). Потом меняются ролями. Отличный способ:
- Проверить, что тест действительно проверяет нужное
- Обмениваться знаниями о кодовой базе
- Писать тесты, которые трудно обойти "хаком"

```
Разработчик A: пишет тест → push
Разработчик B: пишет код → рефакторит → пишет следующий тест → push
Разработчик A: пишет код → рефакторит → пишет следующий тест → push
...
```

---

## Проверь себя

<details>
<summary>1. Что означают три фазы Red-Green-Refactor?</summary>

**RED:** пишем тест, который падает (поведение ещё не реализовано). Если тест сразу проходит --- он бесполезен или проверяет не то.

**GREEN:** пишем минимальный код для прохождения теста. Не оптимальный, не красивый --- просто рабочий. Даже захардкоженное значение допустимо.

**REFACTOR:** улучшаем код при проходящих тестах. Убираем дублирование, переименовываем, выделяем абстракции. Тесты --- страховка, что ничего не сломалось.
</details>

<details>
<summary>2. В чём разница между Inside-Out и Outside-In TDD?</summary>

**Inside-Out (Detroit/Chicago):** начинаем с доменных моделей, двигаемся к API. Минимум моков, используем реальные объекты и фейки. Дизайн "вырастает" снизу.

**Outside-In (London):** начинаем с acceptance test на верхнем уровне. Активно используем моки для ещё не написанных зависимостей. Дизайн определяется сверху.

На практике комбинируют: Inside-Out для домена, Outside-In для use cases и API.
</details>

<details>
<summary>3. Когда TDD не стоит применять?</summary>

TDD избыточен для: простого CRUD без логики, UI-кода (лучше snapshot/visual тесты), прототипирования (требования меняются быстрее кода), glue code / конфигурации, exploratory work. TDD силён там, где требования чёткие, а логика сложная: алгоритмы, валидация, бизнес-правила, state machines.
</details>

<details>
<summary>4. Что такое property-based testing и чем он лучше example-based?</summary>

**Example-based:** конкретные входы и выходы (`add(2, 3) == 5`). Покрывает только придуманные случаи.

**Property-based:** описываем свойство, которое должно выполняться для любого входа (`forAll { a, b -> add(a, b) == add(b, a) }`). Kotest генерирует 1000+ случайных значений включая edge cases (0, -1, MAX_VALUE). Находит баги, которые ты бы не придумал.
</details>

<details>
<summary>5. Почему "слишком много моков" --- сигнал о проблемах дизайна?</summary>

Если для теста нужно 5+ моков --- класс имеет слишком много зависимостей. Это нарушение Single Responsibility Principle. Решение: разбить класс на меньшие, каждый с 1--2 зависимостями. TDD выявляет эту проблему естественным образом: сложный arrange = сложный класс.
</details>

---

## Ключевые карточки

**Что такое TDD (Red-Green-Refactor)?**
?
1) RED: написать падающий тест. 2) GREEN: написать минимальный код для прохождения. 3) REFACTOR: улучшить код при проходящих тестах. Микроцикл ~30 секунд. Сначала тест, потом код --- не наоборот.

**Три закона TDD (Uncle Bob)?**
?
1) Нельзя писать продакшен-код без падающего теста. 2) Нельзя написать больше теста, чем достаточно для одного падения. 3) Нельзя написать больше кода, чем достаточно для прохождения теста. Результат: микроитерации по 30 секунд.

**Inside-Out vs Outside-In TDD?**
?
Inside-Out (Detroit): от доменных моделей наружу, минимум моков, дизайн "вырастает". Outside-In (London): от acceptance test вглубь, активные моки, дизайн определяется сверху. На практике комбинируют оба подхода.

**Когда TDD полезен, а когда нет?**
?
Полезен: бизнес-логика, алгоритмы, валидация, state machines, критичный код. Не полезен: простой CRUD, UI, прототипы, glue code, exploratory work. Ключ: TDD --- для сложной логики с чёткими требованиями.

**Что такое property-based testing?**
?
Описываем свойство, которое должно выполняться для любого входа. Kotest `forAll(Arb.int()) { ... }` генерирует 1000 случайных значений + edge cases (0, -1, MAX_VALUE). Находит баги, которые ты бы не написал в example-based тестах.

**Почему TDD улучшает архитектуру?**
?
TDD вынуждает: Dependency Injection (зависимости через конструктор), маленькие функции (сложно тестировать 200-строчный метод), чёткие интерфейсы (моки через interface), Single Responsibility (10 arrange-строк = класс делает слишком много).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Предыдущий шаг | [[testing-fundamentals]] | Основы: пирамида, типы тестов, организация |
| Следующий шаг | [[mocking-strategies]] | MockK, фейки, стратегии подмены зависимостей |
| Практика | [[refactoring-catalog]] | Безопасный рефакторинг через TDD |
| Углубиться | [[solid-principles]] | SOLID --- принципы, которые TDD помогает соблюдать |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Kent Beck: Test-Driven Development: By Example (2002)](https://www.oreilly.com/library/view/test-driven-development/0321146530/) | Book | Библия TDD, оригинальный Red-Green-Refactor |
| 2 | [Steve Freeman, Nat Pryce: Growing Object-Oriented Software, Guided by Tests (2009)](https://www.growing-object-oriented-software.com/) | Book | London School TDD, Outside-In подход |
| 3 | Москала М. "Effective Kotlin" (2024) | Book | Kotlin-идиомы и тестирование |
| 4 | [JetBrains: TDD with Kotlin Tutorial](https://www.jetbrains.com/help/idea/tdd-with-kotlin.html) | Tutorial | Практический TDD в IntelliJ IDEA |
| 5 | [Kotest: Testing Styles](https://kotest.io/docs/framework/testing-styles.html) | Docs | BehaviorSpec и другие стили |
| 6 | [Kotest: Property-based Testing](https://kotest.io/docs/proptest/property-based-testing.html) | Docs | forAll, Arb, генераторы |
| 7 | [Robert C. Martin: The Three Laws of TDD](http://butunclebob.com/ArticleS.UncleBob.TheThreeRulesOfTdd) | Article | Три закона TDD |
| 8 | [Martin Fowler: Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html) | Article | Классика о London vs Detroit school |
| 9 | [Alexander Obregon: Kotlin and TDD --- A Beginner's Guide](https://medium.com/@AlexanderObregon/kotlin-and-tdd-a-beginners-guide-to-test-driven-development-with-kotlin-486e9853b712) | Article | Практическое введение в TDD на Kotlin |

---

*Последнее обновление: 2026-02-19*
