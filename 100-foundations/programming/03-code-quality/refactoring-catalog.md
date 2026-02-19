---
title: "Каталог рефакторингов: техники улучшения кода"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/refactoring
  - topic/kotlin
related:
  - "[[code-smells]]"
  - "[[legacy-code-strategies]]"
  - "[[clean-code]]"
  - "[[solid-principles]]"
---

# Каталог рефакторингов: техники улучшения кода

68 рефакторингов в первом издании Фаулера, 61 остался + 17 новых во втором. Запоминать все не нужно --- достаточно освоить 10 ключевых техник, чтобы закрыть 90% повседневных задач. Каждая техника --- механическая трансформация: проблема видна, шаги определены, тесты подтверждают, что поведение не изменилось. В Kotlin многие рефакторинги проще благодаря `data class`, `sealed class`, extension-функциям, именованным параметрам и null-safety.

Формат: **Проблема** --- **До (Kotlin)** --- **После (Kotlin)** --- **Когда применять**.

---

## Фундаментальное правило

```
┌──────────────────────────────────────────────────────────────────────┐
│                   РЕФАКТОРИНГ = НЕ МЕНЯТЬ ПОВЕДЕНИЕ                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   1. Тесты зелёные              (есть safety net)                   │
│   2. Одно маленькое изменение   (атомарный шаг)                     │
│   3. Тесты зелёные              (поведение сохранено)               │
│   4. Коммит                     (точка отката)                      │
│   5. Повторить                                                       │
│                                                                      │
│   Нет тестов? → Сначала characterization tests (см. legacy-code)    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 1. Extract Function

**Проблема:** метод делает слишком много, есть блоки кода с комментарием-заголовком.

```kotlin
// ДО: монолитный метод
class InvoiceService(private val taxRates: TaxRates) {

    fun generateInvoice(order: Order): Invoice {
        // validate
        require(order.items.isNotEmpty()) { "Empty order" }
        order.items.forEach { item ->
            require(item.quantity > 0) { "Invalid quantity for ${item.name}" }
            require(item.price > BigDecimal.ZERO) { "Invalid price for ${item.name}" }
        }

        // calculate line totals
        val lines = order.items.map { item ->
            val subtotal = item.price * item.quantity.toBigDecimal()
            val tax = subtotal * taxRates.rateFor(item.category)
            InvoiceLine(item.name, item.quantity, item.price, subtotal, tax)
        }

        // calculate totals
        val subtotal = lines.sumOf { it.subtotal }
        val totalTax = lines.sumOf { it.tax }
        val total = subtotal + totalTax

        return Invoice(order.id, lines, subtotal, totalTax, total)
    }
}
```

```kotlin
// ПОСЛЕ: каждая функция делает одно
class InvoiceService(private val taxRates: TaxRates) {

    fun generateInvoice(order: Order): Invoice {
        validateOrder(order)
        val lines = calculateLines(order)
        return buildInvoice(order.id, lines)
    }

    private fun validateOrder(order: Order) {
        require(order.items.isNotEmpty()) { "Empty order" }
        order.items.forEach { item ->
            require(item.quantity > 0) { "Invalid quantity for ${item.name}" }
            require(item.price > BigDecimal.ZERO) { "Invalid price for ${item.name}" }
        }
    }

    private fun calculateLines(order: Order): List<InvoiceLine> =
        order.items.map { item ->
            val subtotal = item.price * item.quantity.toBigDecimal()
            val tax = subtotal * taxRates.rateFor(item.category)
            InvoiceLine(item.name, item.quantity, item.price, subtotal, tax)
        }

    private fun buildInvoice(orderId: String, lines: List<InvoiceLine>): Invoice {
        val subtotal = lines.sumOf { it.subtotal }
        val totalTax = lines.sumOf { it.tax }
        return Invoice(orderId, lines, subtotal, totalTax, subtotal + totalTax)
    }
}
```

**Когда:** комментарий-заголовок ("// validate", "// calculate"), метод > 20 строк, логика может переиспользоваться.

> [!info] Kotlin-нюанс
> В Kotlin функции могут быть top-level (не обязаны быть в классе). Если извлечённая функция не зависит от состояния класса --- сделайте её top-level или extension. IDE: **Ctrl+Alt+M** / **Cmd+Option+M**.

---

## 2. Replace Conditional with Polymorphism

**Проблема:** `when`/`if-else` по типу дублируется в нескольких местах.

```kotlin
// ДО: when по строковому типу в нескольких функциях
fun calculatePay(employee: Employee): BigDecimal = when (employee.type) {
    "engineer" -> employee.baseSalary
    "salesman" -> employee.baseSalary + employee.commission
    "manager" -> employee.baseSalary + employee.bonus
    else -> throw IllegalArgumentException("Unknown type: ${employee.type}")
}

fun getVacationDays(employee: Employee): Int = when (employee.type) {
    "engineer" -> 21
    "salesman" -> 18
    "manager" -> 28
    else -> throw IllegalArgumentException("Unknown type: ${employee.type}")
}
```

```kotlin
// ПОСЛЕ: sealed class — каждый тип знает своё поведение
sealed class Employee(
    val name: String,
    val baseSalary: BigDecimal
) {
    abstract fun calculatePay(): BigDecimal
    abstract val vacationDays: Int

    class Engineer(name: String, baseSalary: BigDecimal) :
        Employee(name, baseSalary) {
        override fun calculatePay() = baseSalary
        override val vacationDays = 21
    }

    class Salesman(
        name: String,
        baseSalary: BigDecimal,
        val commission: BigDecimal
    ) : Employee(name, baseSalary) {
        override fun calculatePay() = baseSalary + commission
        override val vacationDays = 18
    }

    class Manager(
        name: String,
        baseSalary: BigDecimal,
        val bonus: BigDecimal
    ) : Employee(name, baseSalary) {
        override fun calculatePay() = baseSalary + bonus
        override val vacationDays = 28
    }
}

// Использование — when для специфической логики, exhaustive check
fun formatPaySlip(employee: Employee): String = when (employee) {
    is Employee.Engineer -> "Engineer: ${employee.calculatePay()}"
    is Employee.Salesman -> "Salesman: ${employee.calculatePay()} (incl. commission)"
    is Employee.Manager -> "Manager: ${employee.calculatePay()} (incl. bonus)"
}
```

**Когда:** один и тот же `when`/`if-else` встречается > 2 раз, добавление нового типа требует правок в нескольких местах.

> [!info] Kotlin-нюанс
> `sealed class` + `when` без `else` --- компилятор гарантирует exhaustive check. Новый подтип → ошибка компиляции. Smart cast внутри `when`: после `is Employee.Salesman` доступ к `commission` без приведения типа.

---

## 3. Introduce Parameter Object

**Проблема:** несколько связанных параметров всегда передаются вместе.

```kotlin
// ДО: Date Clumps — start/end повсюду
fun amountInvoiced(start: LocalDate, end: LocalDate): BigDecimal = TODO()
fun amountReceived(start: LocalDate, end: LocalDate): BigDecimal = TODO()
fun amountOverdue(start: LocalDate, end: LocalDate): BigDecimal = TODO()
```

```kotlin
// ПОСЛЕ: data class как Parameter Object
data class DateRange(
    val start: LocalDate,
    val end: LocalDate
) {
    init {
        require(!start.isAfter(end)) { "Start $start is after end $end" }
    }

    fun contains(date: LocalDate): Boolean = date in start..end

    fun overlaps(other: DateRange): Boolean =
        start <= other.end && other.start <= end

    val days: Long get() = ChronoUnit.DAYS.between(start, end)
}

fun amountInvoiced(range: DateRange): BigDecimal = TODO()
fun amountReceived(range: DateRange): BigDecimal = TODO()
fun amountOverdue(range: DateRange): BigDecimal = TODO()

// Бонус: DateRange притягивает к себе поведение (contains, overlaps, days).
// Parameter Object часто становится полноценным доменным классом.
```

**Когда:** > 2 параметра передаются вместе в > 2 функции. Группа параметров представляет единую концепцию.

> [!info] Kotlin-нюанс
> `data class` даёт `equals()`, `hashCode()`, `toString()`, `copy()`, destructuring бесплатно. Порог создания Parameter Object в Kotlin минимален --- 3 строки. В Java то же самое --- 30+ строк.

---

## 4. Replace Magic Number with Constant

**Проблема:** литералы в коде без объяснения смысла.

```kotlin
// ДО: что значит 9.81? 8? 128?
fun calculatePotentialEnergy(mass: Double, height: Double): Double =
    mass * 9.81 * height

fun isValidPassword(password: String): Boolean =
    password.length in 8..128
```

```kotlin
// ПОСЛЕ: const val и enum class
private const val GRAVITATIONAL_ACCELERATION = 9.81 // m/s²

object PasswordPolicy {
    const val MIN_LENGTH = 8
    const val MAX_LENGTH = 128
    const val MIN_UPPERCASE = 1
    const val MIN_DIGITS = 1
}

fun calculatePotentialEnergy(mass: Double, height: Double): Double =
    mass * GRAVITATIONAL_ACCELERATION * height

fun isValidPassword(password: String): Boolean =
    password.length in PasswordPolicy.MIN_LENGTH..PasswordPolicy.MAX_LENGTH

// Для связанных констант — enum:
enum class HttpStatus(val code: Int) {
    OK(200),
    NOT_FOUND(404),
    INTERNAL_ERROR(500);

    val isSuccess: Boolean get() = code in 200..299
}
```

**Когда:** число/строка используется больше одного раза, или значение неочевидно.

> [!info] Kotlin-нюанс
> `const val` --- настоящая compile-time константа (только примитивы и `String`). Для непримитивов используйте `val` в `companion object` или top-level. `enum class` с параметрами --- идиоматичный Kotlin для группы связанных констант.

---

## 5. Move Method (to Extension Function)

**Проблема:** метод больше работает с чужим классом, чем со своим (Feature Envy).

```kotlin
// ДО: OrderPrinter завидует данным Order
class OrderPrinter {
    fun formatOrder(order: Order): String {
        val lines = order.items.joinToString("\n") { item ->
            "  ${item.name} x${item.quantity} = $${item.subtotal()}"
        }
        val total = order.items.sumOf { it.subtotal() }
        return """
            |Order #${order.id}
            |Customer: ${order.customer.name}
            |$lines
            |Total: $$total
        """.trimMargin()
    }
}
```

```kotlin
// ПОСЛЕ, вариант 1: метод внутри класса
class Order(
    val id: String,
    val customer: Customer,
    val items: List<OrderItem>
) {
    fun format(): String {
        val lines = items.joinToString("\n") { "  ${it.name} x${it.quantity} = $${it.subtotal()}" }
        val total = items.sumOf { it.subtotal() }
        return """
            |Order #$id
            |Customer: ${customer.name}
            |$lines
            |Total: $$total
        """.trimMargin()
    }
}
```

```kotlin
// ПОСЛЕ, вариант 2: extension-функция (не раздуваем Order)
// Файл: OrderFormatting.kt
fun Order.format(): String {
    val lines = items.joinToString("\n") { "  ${it.name} x${it.quantity} = $${it.subtotal()}" }
    val total = items.sumOf { it.subtotal() }
    return """
        |Order #$id
        |Customer: ${customer.name}
        |$lines
        |Total: $$total
    """.trimMargin()
}

// Использование:
val text = order.format() // читается как метод Order
```

**Когда:** метод обращается к полям/методам другого класса больше, чем к своим. Выбор между методом класса и extension: если логика --- core domain → метод; если presentation/utility → extension.

> [!info] Kotlin-нюанс
> Extension-функции в Kotlin --- мощный инструмент Move Method: логика выглядит как метод класса, но живёт в отдельном файле. Правило: extension должна работать через **публичный API** класса. IDE: **F6** (Move).

---

## 6. Replace Temp with Query

**Проблема:** временная переменная хранит результат вычисления, используемый один раз.

```kotlin
// ДО: temp variable
fun calculateTotal(order: Order): BigDecimal {
    val basePrice = order.quantity.toBigDecimal() * order.itemPrice
    return if (basePrice > 1000.toBigDecimal()) {
        basePrice * 0.95.toBigDecimal()
    } else {
        basePrice * 0.98.toBigDecimal()
    }
}
```

```kotlin
// ПОСЛЕ: computed property / функция
class Order(
    val quantity: Int,
    val itemPrice: BigDecimal
) {
    val basePrice: BigDecimal
        get() = quantity.toBigDecimal() * itemPrice

    fun calculateTotal(): BigDecimal =
        if (basePrice > 1000.toBigDecimal()) {
            basePrice * 0.95.toBigDecimal()
        } else {
            basePrice * 0.98.toBigDecimal()
        }
}
```

**Когда:** temp-переменная используется для промежуточного вычисления, которое имеет бизнес-смысл. Не применять для дорогих вычислений (вызовется каждый раз).

> [!info] Kotlin-нюанс
> Computed property (`val x: T get() = ...`) --- идиоматичный способ заменить temp. Для дорогих вычислений --- `by lazy { ... }` (кэширует результат). Для часто меняющихся --- оставьте `val` в теле функции.

---

## 7. Decompose Conditional

**Проблема:** сложное условие трудно читать.

```kotlin
// ДО: что проверяет условие?
fun getCharge(date: LocalDate, quantity: Int): BigDecimal {
    return if (date.isBefore(SUMMER_START) || date.isAfter(SUMMER_END)) {
        quantity.toBigDecimal() * WINTER_RATE + WINTER_SERVICE_CHARGE
    } else {
        quantity.toBigDecimal() * SUMMER_RATE
    }
}
```

```kotlin
// ПОСЛЕ: условие и ветки извлечены в функции с говорящими именами
fun getCharge(date: LocalDate, quantity: Int): BigDecimal =
    if (isSummer(date)) summerCharge(quantity) else winterCharge(quantity)

private fun isSummer(date: LocalDate): Boolean =
    date in SUMMER_START..SUMMER_END

private fun summerCharge(quantity: Int): BigDecimal =
    quantity.toBigDecimal() * SUMMER_RATE

private fun winterCharge(quantity: Int): BigDecimal =
    quantity.toBigDecimal() * WINTER_RATE + WINTER_SERVICE_CHARGE
```

```kotlin
// Kotlin when — ещё лучше для нескольких условий:
fun getCharge(date: LocalDate, quantity: Int): BigDecimal = when {
    isSummer(date) -> summerCharge(quantity)
    isHolidaySeason(date) -> holidayCharge(quantity)
    else -> standardCharge(quantity)
}
```

**Когда:** условие `if` занимает > 1 строки, ветки содержат бизнес-логику.

---

## 8. Replace Type Code with Sealed Class

**Проблема:** строка или число определяет "тип", поведение выбирается через `when`.

```kotlin
// ДО: type code как строка
data class Notification(
    val type: String, // "email", "sms", "push"
    val recipient: String,
    val message: String
)

fun send(notification: Notification) = when (notification.type) {
    "email" -> sendEmail(notification.recipient, notification.message)
    "sms" -> sendSms(notification.recipient, notification.message)
    "push" -> sendPush(notification.recipient, notification.message)
    else -> throw IllegalArgumentException("Unknown type: ${notification.type}")
}
```

```kotlin
// ПОСЛЕ: sealed class — каждый тип несёт свои данные
sealed class Notification {
    abstract val message: String

    data class Email(
        val to: String,
        val subject: String,
        override val message: String
    ) : Notification()

    data class Sms(
        val phoneNumber: String,
        override val message: String
    ) : Notification()

    data class Push(
        val deviceToken: String,
        val title: String,
        override val message: String
    ) : Notification()
}

fun send(notification: Notification) = when (notification) {
    is Notification.Email -> sendEmail(notification.to, notification.subject, notification.message)
    is Notification.Sms -> sendSms(notification.phoneNumber, notification.message)
    is Notification.Push -> sendPush(notification.deviceToken, notification.title, notification.message)
    // exhaustive — нет else, компилятор проверяет полноту
}
```

**Когда:** строковый/числовой "тип" определяет поведение через `when`. Разные "типы" несут разные данные.

---

## 9. Introduce Null Object / Use Kotlin Null-Safety

**Проблема:** проверки на `null` разбросаны по коду, забытая проверка --- NPE.

```kotlin
// ДО (Java-стиль): null-проверки повсюду
fun getDiscount(customer: Customer?): BigDecimal {
    if (customer == null) return BigDecimal.ZERO
    if (customer.loyaltyProgram == null) return BigDecimal.ZERO
    return customer.loyaltyProgram.discountRate
}

fun greet(customer: Customer?): String {
    if (customer == null) return "Welcome, guest!"
    return "Welcome back, ${customer.name}!"
}
```

```kotlin
// ПОСЛЕ, вариант 1: Kotlin null-safety операторы
fun getDiscount(customer: Customer?): BigDecimal =
    customer?.loyaltyProgram?.discountRate ?: BigDecimal.ZERO

fun greet(customer: Customer?): String =
    customer?.let { "Welcome back, ${it.name}!" } ?: "Welcome, guest!"
```

```kotlin
// ПОСЛЕ, вариант 2: Sealed class с Empty-вариантом (Null Object pattern)
sealed class Customer {
    abstract val name: String
    abstract fun getDiscount(): BigDecimal
    abstract fun greet(): String

    data class Registered(
        override val name: String,
        val loyaltyProgram: LoyaltyProgram?
    ) : Customer() {
        override fun getDiscount() = loyaltyProgram?.discountRate ?: BigDecimal.ZERO
        override fun greet() = "Welcome back, $name!"
    }

    data object Guest : Customer() {
        override val name = "Guest"
        override fun getDiscount() = BigDecimal.ZERO
        override fun greet() = "Welcome, guest!"
    }
}

// Нет null-проверок — полиморфизм делает всё
val message = customer.greet()
```

**Когда:** `?.` / `?:` повторяется > 3 раз для одного типа. Null Object --- когда "отсутствие" имеет определённое поведение (Guest, EmptyList, NullLogger).

> [!info] Kotlin-нюанс
> Kotlin null-safety (`?.`, `?:`, `!!`, `let`, `takeIf`) покрывает 80% случаев. Sealed class с Null Object --- для оставшихся 20%, когда "ничего" имеет бизнес-поведение.

---

## 10. Replace Constructor with Factory Method

**Проблема:** конструктор не может иметь говорящее имя, нужна логика выбора типа при создании.

```kotlin
// ДО: конструктор не объясняет намерение
val coord1 = Coordinate(37.7749, -122.4194)   // это что? x,y? lat,lon?
val coord2 = Coordinate(0.6593, -2.1366)       // а это?
```

```kotlin
// ПОСЛЕ: companion object с фабричными методами
data class Coordinate private constructor(
    val latitude: Double,
    val longitude: Double
) {
    companion object {
        fun fromDegrees(lat: Double, lon: Double): Coordinate {
            require(lat in -90.0..90.0) { "Latitude must be in [-90, 90]" }
            require(lon in -180.0..180.0) { "Longitude must be in [-180, 180]" }
            return Coordinate(lat, lon)
        }

        fun fromRadians(latRad: Double, lonRad: Double): Coordinate =
            Coordinate(
                latitude = Math.toDegrees(latRad),
                longitude = Math.toDegrees(lonRad)
            )

        fun parse(text: String): Coordinate {
            val (lat, lon) = text.split(",").map { it.trim().toDouble() }
            return fromDegrees(lat, lon)
        }
    }
}

// Использование — намерение кристально ясно
val sanFrancisco = Coordinate.fromDegrees(37.7749, -122.4194)
val fromApi = Coordinate.parse("37.7749, -122.4194")
```

**Когда:** несколько способов создания объекта, нужна валидация при создании, имя конструктора не объясняет намерение.

> [!info] Kotlin-нюанс
> `companion object` --- идиоматичный Kotlin для фабрик. `private constructor` + фабричные методы гарантируют валидный объект. Для Java-interop добавьте `@JvmStatic`: `@JvmStatic fun fromDegrees(...)`.

---

## Дополнительные техники

### Extract Variable

```kotlin
// ДО
if (platform.toUpperCase().contains("MAC") &&
    browser.toUpperCase().contains("SAFARI") &&
    wasInitialized && resize > 0) { ... }

// ПОСЛЕ
val isMacOS = platform.uppercase().contains("MAC")
val isSafari = browser.uppercase().contains("SAFARI")
val isReadyToResize = wasInitialized && resize > 0

if (isMacOS && isSafari && isReadyToResize) { ... }
```

IDE: **Ctrl+Alt+V** / **Cmd+Option+V**.

---

### Inline Function

Обратный к Extract Function --- когда метод-обёртка не добавляет ясности.

```kotlin
// ДО: метод делает ровно то, что написано в его теле
fun isMoreThanFiveLateDeliveries(driver: Driver): Boolean =
    driver.numberOfLateDeliveries > 5

fun rating(driver: Driver): Int =
    if (isMoreThanFiveLateDeliveries(driver)) 2 else 1

// ПОСЛЕ: inline — код читается лучше без обёртки
fun rating(driver: Driver): Int =
    if (driver.numberOfLateDeliveries > 5) 2 else 1
```

IDE: **Ctrl+Alt+N** / **Cmd+Option+N**.

---

### Replace Loop with Pipeline

```kotlin
// ДО: императивный цикл
fun getActiveUserEmails(users: List<User>): List<String> {
    val result = mutableListOf<String>()
    for (user in users) {
        if (user.isActive) {
            val email = user.email.lowercase()
            if (email.isNotBlank()) {
                result.add(email)
            }
        }
    }
    return result
}

// ПОСЛЕ: функциональный pipeline
fun getActiveUserEmails(users: List<User>): List<String> =
    users.filter { it.isActive }
        .map { it.email.lowercase() }
        .filter { it.isNotBlank() }
```

> [!info] Kotlin-нюанс
> Для больших коллекций используйте `asSequence()` для ленивых вычислений:
> ```kotlin
> users.asSequence()
>     .filter { it.isActive }
>     .map { it.email.lowercase() }
>     .filter { it.isNotBlank() }
>     .toList()
> ```

---

### Substitute Algorithm

```kotlin
// ДО: ручной поиск
fun findPerson(people: List<String>): String {
    for (person in people) {
        if (person == "Don") return "Don"
        if (person == "John") return "John"
        if (person == "Kent") return "Kent"
    }
    return ""
}

// ПОСЛЕ: стандартная библиотека
fun findPerson(people: List<String>): String {
    val candidates = setOf("Don", "John", "Kent")
    return people.firstOrNull { it in candidates } ?: ""
}
```

---

## IDE-рефакторинги: IntelliJ IDEA / Android Studio

### Горячие клавиши (macOS / Windows)

| Рефакторинг | macOS | Windows/Linux |
|-------------|-------|---------------|
| **Refactor This** (меню) | Ctrl+T | Ctrl+Alt+Shift+T |
| **Rename** | Shift+F6 | Shift+F6 |
| **Extract Method** | Cmd+Option+M | Ctrl+Alt+M |
| **Extract Variable** | Cmd+Option+V | Ctrl+Alt+V |
| **Extract Constant** | Cmd+Option+C | Ctrl+Alt+C |
| **Extract Parameter** | Cmd+Option+P | Ctrl+Alt+P |
| **Inline** | Cmd+Option+N | Ctrl+Alt+N |
| **Move** | F6 | F6 |
| **Change Signature** | Cmd+F6 | Ctrl+F6 |
| **Safe Delete** | Cmd+Delete | Alt+Delete |

### Workflow: использование IDE для безопасного рефакторинга

```
1. Выделить блок кода
2. Ctrl+T → выбрать рефакторинг
3. IDE показывает preview — проверить
4. Apply
5. Run tests (Ctrl+Shift+F10)
6. Commit (Ctrl+K)
```

> [!info] Kotlin-нюанс
> IntelliJ IDEA имеет специфичные для Kotlin рефакторинги:
> - **Convert to expression body** (однострочные функции)
> - **Convert to data class**
> - **Convert Java to Kotlin** (Ctrl+Alt+Shift+K / Cmd+Option+Shift+K)
> - **Add names to call arguments** (именованные параметры)
> - **Convert to scope function** (`let`, `apply`, `run`)

---

## Порядок применения рефакторингов

```
┌──────────────────────────────────────────────────────────────────────┐
│               ПОРЯДОК: от безопасного к рискованному                 │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  УРОВЕНЬ 1: Косметика (низкий риск)                                 │
│  ├── Rename (переменные, методы, классы)                            │
│  ├── Extract Variable                                                │
│  └── Replace Magic Number with Constant                             │
│                                                                      │
│  УРОВЕНЬ 2: Структура метода (средний риск)                         │
│  ├── Extract Function                                                │
│  ├── Inline Function                                                 │
│  ├── Replace Temp with Query                                        │
│  └── Decompose Conditional                                          │
│                                                                      │
│  УРОВЕНЬ 3: Структура класса (высокий риск)                         │
│  ├── Move Method                                                     │
│  ├── Extract Class / Introduce Parameter Object                     │
│  ├── Replace Type Code with sealed class                            │
│  └── Replace Conditional with Polymorphism                          │
│                                                                      │
│  УРОВЕНЬ 4: Архитектура (требует planning)                          │
│  ├── Replace Constructor with Factory Method                        │
│  ├── Introduce Null Object                                          │
│  └── Hide Delegate / Remove Middle Man                              │
│                                                                      │
│  ПРАВИЛО: Начинай с уровня 1. Каждый шаг — коммит.                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Сводная таблица: рефакторинг vs запах

| Рефакторинг | Какой запах лечит | IDE shortcut |
|-------------|-------------------|-------------|
| Extract Function | Long Method | Ctrl+Alt+M |
| Replace Conditional with Polymorphism | Switch Statements | --- |
| Introduce Parameter Object | Long Param List, Data Clumps | --- |
| Replace Magic Number | Magic Number | Ctrl+Alt+C |
| Move Method (Extension) | Feature Envy | F6 |
| Replace Temp with Query | Temp variable | Ctrl+Alt+V |
| Decompose Conditional | Complex Conditional | --- |
| Replace Type Code with sealed class | Type code | --- |
| Introduce Null Object | Null checks | --- |
| Replace Constructor with Factory | Complex construction | --- |
| Extract Variable | Complex expression | Ctrl+Alt+V |
| Inline Function | Unnecessary delegation | Ctrl+Alt+N |
| Replace Loop with Pipeline | Imperative loop | --- |

---

## Проверь себя

<details>
<summary>1. В чём разница между Extract Function и Extract Variable?</summary>

**Ответ:**

**Extract Function:** выделяет блок кода в новую функцию. Результат --- новая функция + вызов вместо блока. Применять когда блок имеет самостоятельный смысл и может переиспользоваться.

**Extract Variable:** выделяет часть выражения в именованную переменную. Результат --- та же функция, но сложное выражение заменено переменной с говорящим именем. Применять когда выражение сложное, но недостаточно большое для отдельной функции.

Часто: сначала Extract Variable, затем, если переменная используется в нескольких методах --- Extract Function.

</details>

<details>
<summary>2. Когда Move Method → extension function, а когда → метод класса?</summary>

**Ответ:**

**Метод класса:** логика --- core domain (бизнес-правило, инвариант). Пример: `Order.calculateTotal()`.

**Extension function:** логика --- presentation, formatting, mapping, utility. Пример: `Order.toDto()`, `Order.format()`.

Правило: extension должна работать через публичный API класса. Если extension обращается к > 3 полям через геттеры --- это кандидат на Move внутрь класса.

</details>

<details>
<summary>3. Почему Replace Temp with Query может быть опасным?</summary>

**Ответ:**

Query (computed property / функция) вызывается **каждый раз** при обращении. Если вычисление дорогое (запрос к БД, сложный расчёт) --- замена temp на query вызовет проблемы с производительностью.

Решения в Kotlin:
- `by lazy { ... }` --- кэшировать при первом вызове (для immutable данных)
- `val` в теле функции --- оставить temp (для дорогих вычислений)
- Профилировать перед и после рефакторинга

</details>

<details>
<summary>4. Зачем private constructor + companion object factory, если можно просто конструктор?</summary>

**Ответ:**

1. **Говорящее имя:** `Coordinate.fromDegrees()` vs `Coordinate(37.7, -122.4)` --- что яснее?
2. **Валидация с ясной ошибкой:** фабрика может проверить аргументы до создания объекта.
3. **Кэширование:** фабрика может вернуть существующий объект (flyweight).
4. **Полиморфизм:** фабрика может вернуть подтип (`Connection.create()` → `PooledConnection` или `DirectConnection`).
5. **Java-interop:** `@JvmStatic` делает фабрику вызываемой как `Coordinate.fromDegrees()` из Java.

</details>

<details>
<summary>5. Какой порядок рефакторинга для метода в 200 строк?</summary>

**Ответ:**

1. Написать characterization tests (если нет тестов).
2. **Rename** переменные (уровень 1: безопасно, IDE делает автоматически).
3. **Extract Variable** для сложных выражений (уровень 1).
4. **Replace Magic Number** с константами (уровень 1).
5. **Decompose Conditional** --- извлечь условия в функции (уровень 2).
6. **Extract Function** --- по блокам, начиная с самых независимых (уровень 2).
7. **Introduce Parameter Object** --- если есть Data Clumps (уровень 3).
8. **Extract Class** --- если блоки группируются по данным (уровень 3).
9. Каждый шаг → тест → коммит.

</details>

---

## Ключевые карточки

Что такое Extract Function и когда его применять?
?
Выделение блока кода в отдельную функцию. Применять: метод > 20 строк, комментарий-заголовок ("// validate"), блок может переиспользоваться. В Kotlin: можно извлечь в top-level функцию, extension или private method. IDE: Ctrl+Alt+M. Ключ: имя функции должно объяснять "зачем", а не "как".

Как Replace Conditional with Polymorphism работает в Kotlin?
?
`when` по типу/строке → sealed class с подтипами. Каждый подтип реализует своё поведение через override. `when` без `else` --- exhaustive: новый подтип → ошибка компиляции. Smart cast: после `is Subtype` доступ к полям без приведения. Применять когда один `when` дублируется > 2 раз.

Чем Parameter Object отличается от обычного data class?
?
Parameter Object --- `data class`, созданный для замены группы параметров, которые всегда передаются вместе. Со временем Parameter Object притягивает поведение: `DateRange` получает `contains()`, `overlaps()`, `days`. Это эволюция: Data Clumps → Parameter Object → Domain Object.

Когда использовать companion object factory вместо конструктора?
?
Когда нужно: говорящее имя (`fromDegrees` vs конструктор), валидация до создания, несколько способов создания, кэширование (flyweight), возврат подтипа. В Kotlin: `companion object` + `private constructor`. Для Java-interop: `@JvmStatic`.

Какой порядок применения рефакторингов?
?
От безопасного к рискованному: 1) Rename, Extract Variable, Replace Magic Number (косметика). 2) Extract Function, Decompose Conditional (структура метода). 3) Move Method, Extract Class, sealed class (структура класса). 4) Factory Method, Null Object (архитектура). Каждый шаг → тест → коммит.

Чем Replace Temp with Query отличается от Extract Variable?
?
Extract Variable: сложное выражение → именованная переменная (вычисляется один раз). Replace Temp with Query: temp → computed property или функция (вычисляется каждый раз). Опасность: query может быть дорогим. Решение в Kotlin: `by lazy {}` для кэширования, оставить `val` для дорогих вычислений.

Как Replace Loop with Pipeline выглядит в Kotlin?
?
Императивный цикл с if/mutableList → цепочка `filter`/`map`/`flatMap`/`groupBy`. Для больших коллекций: `asSequence()` для ленивых вычислений. Правило: pipeline из > 5 шагов → Extract Function для промежуточных этапов.

Какие IDE-рефакторинги специфичны для Kotlin?
?
Convert to expression body, Convert to data class, Convert Java to Kotlin (Cmd+Option+Shift+K), Add names to call arguments, Convert to scope function (let/apply/run). IntelliJ IDEA Refactor This: Ctrl+T (macOS) / Ctrl+Alt+Shift+T (Windows).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[code-smells]] | Распознать запахи, которые эти техники лечат |
| Углубиться | [[legacy-code-strategies]] | Рефакторинг legacy-кода --- особый случай |
| Смежная тема | [[clean-code]] | Принципы, которые направляют рефакторинг |
| Практика | [[design-patterns-overview]] | Паттерны как цель рефакторинга |

---

## Источники

- Fowler M. "Refactoring: Improving the Design of Existing Code" (2nd ed., 2018) --- 61 + 17 рефакторингов с примерами
- [Refactoring Catalog — refactoring.com](https://refactoring.com/catalog/) --- онлайн-каталог с фильтрами
- [Refactoring Guru](https://refactoring.guru/refactoring/techniques) --- визуальные примеры рефакторингов
- Martin R.C. "Clean Code" (2008) --- принципы, направляющие рефакторинг
- Moskala M. "Effective Kotlin" (2nd ed., 2022) --- идиоматичный Kotlin
- [IntelliJ IDEA — Extract Method](https://www.jetbrains.com/help/idea/extract-method.html) --- документация IDE
- [Baeldung — Refactoring in Kotlin](https://www.baeldung.com/kotlin/code-smells-recognize-mitigate) --- практический гайд
- [CodeSignal — Refactoring in Kotlin](https://codesignal.com/learn/courses/advanced-built-in-data-structures-and-their-usage-6/lessons/refactoring-in-kotlin-extract-rename-and-substitute-techniques) --- Extract, Rename, Substitute

---

*Проверено: 2026-02-19*
