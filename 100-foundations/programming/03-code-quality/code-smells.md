---
title: "Code Smells: распознавание запахов кода"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/code-quality
  - topic/kotlin
related:
  - "[[refactoring-catalog]]"
  - "[[legacy-code-strategies]]"
  - "[[clean-code]]"
  - "[[solid-principles]]"
---

# Code Smells: распознавание запахов кода

Код компилируется, тесты зелёные, фича работает. Но через месяц каждое изменение занимает вдвое больше времени, а баги появляются в местах, которые никто не трогал. Проблема не в синтаксисе --- код **пахнет**. Термин придумал Кент Бек для книги Мартина Фаулера: code smell --- поверхностный признак, указывающий на глубокую проблему в дизайне. Запах --- не баг: программа работает. Но запах сигнализирует, что рефакторинг назрел.

Kotlin устраняет целые категории запахов на уровне языка: `data class` убивает Primitive Obsession, `sealed class` + `when` заменяет Switch Statements, а именованные параметры с дефолтами сокращают Long Parameter List до читаемого вызова.

---

## Классификация запахов

```
┌──────────────────────────────────────────────────────────────────────┐
│                     5 КАТЕГОРИЙ CODE SMELLS                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  BLOATERS             OO ABUSERS           CHANGE PREVENTERS        │
│  ─────────            ──────────           ─────────────────        │
│  Long Method          Switch Statements    Divergent Change         │
│  Large Class          Refused Bequest      Shotgun Surgery          │
│  Long Param List      Parallel Inheritance Parallel Inheritance     │
│  Primitive Obsession  Alt. Classes w/      (пересечение!)           │
│  Data Clumps            Diff. Interfaces                            │
│                                                                      │
│  COUPLERS             DISPENSABLES                                   │
│  ────────             ────────────                                   │
│  Feature Envy         Lazy Class                                     │
│  Inappropriate        Speculative                                    │
│    Intimacy             Generality                                   │
│  Message Chains       Dead Code                                      │
│  Middle Man           Comments (как костыль)                         │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Bloaters: раздутый код

### Long Method

**Признаки:** метод > 20 строк, несколько уровней абстракции, комментарии-разделители ("// validate", "// calculate").

```kotlin
// BAD: метод делает всё
class OrderProcessor(
    private val inventory: InventoryService,
    private val paymentGateway: PaymentGateway,
    private val emailService: EmailService,
    private val smsService: SmsService
) {
    fun processOrder(order: Order): OrderResult {
        // Validate order
        require(order.items.isNotEmpty()) { "Empty order" }
        requireNotNull(order.customer) { "No customer" }
        for (item in order.items) {
            require(item.quantity > 0) { "Invalid quantity" }
            require(inventory.hasStock(item.productId, item.quantity)) {
                "Insufficient stock for ${item.productId}"
            }
        }

        // Calculate totals
        val subtotal = order.items.sumOf { it.price * it.quantity }
        val tax = subtotal * 0.2.toBigDecimal()
        val shipping = if (subtotal < 50.toBigDecimal()) 5.99.toBigDecimal() else BigDecimal.ZERO
        val total = subtotal + tax + shipping

        // Apply discounts
        var finalTotal = total
        if (order.customer.isPremium) finalTotal *= 0.9.toBigDecimal()
        order.coupon?.let { finalTotal -= it.value }

        // Process payment
        val paymentResult = paymentGateway.charge(order.customer.paymentMethod, finalTotal)
        check(paymentResult.success) { paymentResult.error }

        // Update inventory
        order.items.forEach { inventory.decrease(it.productId, it.quantity) }

        // Send notifications
        emailService.sendConfirmation(order.customer.email, order)
        order.customer.phone?.let { smsService.sendConfirmation(it, order) }

        return OrderResult(orderId = order.id, total = finalTotal)
    }
}
```

```kotlin
// GOOD: каждый метод делает одно
class OrderProcessor(
    private val validator: OrderValidator,
    private val calculator: TotalsCalculator,
    private val discounter: DiscountApplier,
    private val paymentGateway: PaymentGateway,
    private val inventory: InventoryService,
    private val notifier: OrderNotifier
) {
    fun processOrder(order: Order): OrderResult {
        validator.validate(order)
        val totals = calculator.calculate(order)
        val finalTotal = discounter.apply(order, totals)
        paymentGateway.chargeOrThrow(order.customer.paymentMethod, finalTotal)
        inventory.decreaseAll(order.items)
        notifier.sendConfirmations(order)
        return OrderResult(orderId = order.id, total = finalTotal)
    }
}
```

> [!info] Kotlin-нюанс
> Scope-функции (`let`, `run`, `apply`, `also`, `with`) сжимают цепочки операций. Но 3+ вложенных scope-функции --- уже новый запах. Если `let` вложен в `run` вложенный в `also` --- извлеките метод.

**Почему опасно:** длинный метод трудно читать, невозможно переиспользовать, тяжело тестировать изолированно.

**Лечение в Kotlin:** Extract Function, scope-функции для коротких преобразований, extension-функции для выделения логики.

---

### Large Class

**Признаки:** > 200 строк, > 10 полей, класс изменяется по несвязанным причинам.

```kotlin
// BAD: God Object
class User(
    var name: String,
    var email: String,
    var passwordHash: String,
    var addressStreet: String,
    var addressCity: String,
    var addressZip: String,
    var cardNumber: String,
    var cardExpiry: String,
    var cardCvv: String,
    val orders: MutableList<Order> = mutableListOf(),
    val cartItems: MutableList<CartItem> = mutableListOf()
) {
    fun validateEmail(): Boolean = TODO()
    fun hashPassword(): String = TODO()
    fun formatAddress(): String = TODO()
    fun validateCard(): Boolean = TODO()
    fun chargeCard(amount: BigDecimal): PaymentResult = TODO()
    fun addToCart(item: CartItem): Unit = TODO()
    fun checkout(): Order = TODO()
}
```

```kotlin
// GOOD: разделение ответственностей через data class
data class User(
    val name: String,
    val email: Email,
    val passwordHash: String,
    val address: Address? = null,
    val paymentMethod: PaymentMethod? = null
)

@JvmInline
value class Email(val value: String) {
    init {
        require("@" in value && "." in value.substringAfter("@")) {
            "Invalid email: $value"
        }
    }
}

data class Address(
    val street: String,
    val city: String,
    val zipCode: String
) {
    fun format(): String = "$street, $city $zipCode"
}

data class PaymentMethod(
    val cardNumber: String,
    val expiry: String,
    val cvv: String
) {
    fun validate(): Boolean = TODO()
    fun charge(amount: BigDecimal): PaymentResult = TODO()
}
```

> [!info] Kotlin-нюанс
> `data class` автоматически генерирует `equals()`, `hashCode()`, `toString()`, `copy()`. Класс с 10 полями в Java --- 100+ строк бойлерплейта. В Kotlin --- 5 строк. Это снижает порог для Extract Class: создать новый value object дёшево.

---

### Long Parameter List

**Признаки:** > 3-4 параметра, параметры часто передаются вместе, трудно запомнить порядок.

```kotlin
// BAD: 7 параметров — невозможно запомнить порядок
fun createReport(
    title: String,
    startDate: LocalDate,
    endDate: LocalDate,
    format: String,
    includeCharts: Boolean,
    maxPages: Int,
    watermark: String?
): Report = TODO()

// Вызов: что есть что?
createReport("Q4", date1, date2, "PDF", true, 50, null)
```

```kotlin
// GOOD: data class как Parameter Object + именованные параметры
data class ReportConfig(
    val title: String,
    val dateRange: ClosedRange<LocalDate>,
    val format: ReportFormat = ReportFormat.PDF,
    val includeCharts: Boolean = true,
    val maxPages: Int = 100,
    val watermark: String? = null
)

enum class ReportFormat { PDF, HTML, CSV }

fun createReport(config: ReportConfig): Report = TODO()

// Вызов — читается как документация
createReport(
    ReportConfig(
        title = "Q4 Revenue",
        dateRange = LocalDate.of(2025, 10, 1)..LocalDate.of(2025, 12, 31),
        format = ReportFormat.PDF
    )
)
```

> [!info] Kotlin-нюанс
> Именованные параметры + значения по умолчанию устраняют 80% случаев Long Parameter List. Не нужен Builder: `data class` с дефолтами + именованный вызов дают ту же читаемость.

---

### Primitive Obsession

**Признаки:** `String` для email, `Int` для userId, `Double` для денег --- примитивы вместо типов предметной области.

```kotlin
// BAD: примитивы повсюду — компилятор не поможет
fun sendInvoice(email: String, amount: Double, currency: String) {
    // email = "not-an-email"? amount = -100.0? currency = "XXX"?
}

// Можно случайно перепутать аргументы!
sendInvoice("USD", 100.0, "john@example.com") // компилируется!
```

```kotlin
// GOOD: value class + типобезопасность с нулевым оверхедом
@JvmInline
value class Email(val value: String) {
    init { require("@" in value) { "Invalid email: $value" } }
}

@JvmInline
value class Money(val cents: Long) {
    operator fun plus(other: Money) = Money(cents + other.cents)
    operator fun times(factor: Int) = Money(cents * factor)
    fun format(): String = "$${cents / 100}.${"%02d".format(cents % 100)}"
}

enum class Currency { USD, EUR, RUB }

fun sendInvoice(email: Email, amount: Money, currency: Currency) { /* ... */ }

// Компилятор не позволит перепутать!
// sendInvoice(Money(10000), Email("john@example.com"), Currency.USD)  // ОШИБКА
sendInvoice(Email("john@example.com"), Money(10000), Currency.USD)     // ОК
```

> [!info] Kotlin-нюанс
> `value class` (inline class) --- обёртка с нулевым оверхедом в рантайме. В байткоде `Email` становится просто `String`, но компилятор проверяет типы. Это убивает Primitive Obsession без потери производительности.

---

### Data Clumps

**Признаки:** группа полей/параметров, которые всегда появляются вместе (street + city + zip, x + y + z).

```kotlin
// BAD: координаты размазаны по всему коду
fun distance(x1: Double, y1: Double, x2: Double, y2: Double): Double {
    return sqrt((x2 - x1).pow(2) + (y2 - y1).pow(2))
}

fun translate(x: Double, y: Double, dx: Double, dy: Double): Pair<Double, Double> {
    return Pair(x + dx, y + dy)
}
```

```kotlin
// GOOD: Data Clump → data class
data class Point(val x: Double, val y: Double) {
    fun distanceTo(other: Point): Double =
        sqrt((other.x - x).pow(2) + (other.y - y).pow(2))

    fun translate(dx: Double, dy: Double): Point =
        copy(x = x + dx, y = y + dy)

    operator fun plus(other: Point) = Point(x + other.x, y + other.y)
    operator fun minus(other: Point) = Point(x - other.x, y - other.y)
}
```

---

## OO Abusers: злоупотребление ООП

### Switch Statements

**Признаки:** одинаковый `when`/`if-else` по типу в нескольких местах, добавление нового типа требует правок в 5+ файлах.

```kotlin
// BAD: when-выражение дублируется в нескольких функциях
fun calculateShipping(type: String): BigDecimal = when (type) {
    "standard" -> 5.99.toBigDecimal()
    "express" -> 12.99.toBigDecimal()
    "overnight" -> 24.99.toBigDecimal()
    "international" -> 39.99.toBigDecimal()
    else -> throw IllegalArgumentException("Unknown: $type")
}

fun getDeliveryDays(type: String): Int = when (type) {
    "standard" -> 5
    "express" -> 2
    "overnight" -> 1
    "international" -> 14
    else -> throw IllegalArgumentException("Unknown: $type")
}

// Добавление нового типа → правки в КАЖДОЙ функции!
```

```kotlin
// GOOD: sealed class + when с проверкой полноты
sealed class ShippingMethod {
    abstract val cost: BigDecimal
    abstract val deliveryDays: Int
    abstract val label: String

    data object Standard : ShippingMethod() {
        override val cost = 5.99.toBigDecimal()
        override val deliveryDays = 5
        override val label = "Standard (5-7 days)"
    }

    data object Express : ShippingMethod() {
        override val cost = 12.99.toBigDecimal()
        override val deliveryDays = 2
        override val label = "Express (1-2 days)"
    }

    data object Overnight : ShippingMethod() {
        override val cost = 24.99.toBigDecimal()
        override val deliveryDays = 1
        override val label = "Overnight"
    }

    data class International(val country: String) : ShippingMethod() {
        override val cost = 39.99.toBigDecimal()
        override val deliveryDays = 14
        override val label = "International to $country"
    }
}

// when — exhaustive: компилятор заставит обработать все варианты
fun formatShipping(method: ShippingMethod): String = when (method) {
    is ShippingMethod.Standard -> "Free for orders over $50"
    is ShippingMethod.Express -> "Arrives in ${method.deliveryDays} days"
    is ShippingMethod.Overnight -> "Next business day"
    is ShippingMethod.International -> "Ships to ${method.country}"
    // Новый подтип → ошибка компиляции здесь — невозможно забыть!
}
```

> [!info] Kotlin-нюанс
> `sealed class` + `when` без `else` --- компилятор проверяет, что обработаны все варианты. Добавление нового подтипа вызывает ошибку компиляции во всех `when`-выражениях. Это Switch Statements на стероидах: запах превращается в фичу.

---

### Refused Bequest

**Признаки:** подкласс использует лишь малую часть унаследованного интерфейса, переопределяет методы пустыми реализациями.

```kotlin
// BAD: Duck наследует fly(), но пингвин не летает
open class Bird {
    open fun fly(): Unit = println("Flying!")
    open fun eat(): Unit = println("Eating")
}

class Penguin : Bird() {
    override fun fly() {
        throw UnsupportedOperationException("Penguins can't fly!")
    }
}
```

```kotlin
// GOOD: интерфейсы вместо наследования
interface Bird {
    fun eat()
}

interface Flyable {
    fun fly()
}

class Sparrow : Bird, Flyable {
    override fun eat() = println("Eating seeds")
    override fun fly() = println("Flying!")
}

class Penguin : Bird {
    override fun eat() = println("Eating fish")
    // Нет fly() — и не нужен
}
```

---

### Parallel Inheritance Hierarchies

**Признаки:** каждый раз при создании подкласса в одной иерархии приходится создавать подкласс в другой.

```kotlin
// BAD: Order → OrderSerializer, Invoice → InvoiceSerializer, ...
// Каждый новый документ требует новый сериализатор

// GOOD: обобщённый подход
interface Serializable {
    fun toJson(): String
}

// Или через sealed class + единый сериализатор
sealed class Document : Serializable {
    data class Order(val items: List<Item>) : Document() {
        override fun toJson(): String = /* ... */ ""
    }
    data class Invoice(val total: BigDecimal) : Document() {
        override fun toJson(): String = /* ... */ ""
    }
}
```

---

## Change Preventers: препятствия изменениям

### Divergent Change

**Признаки:** один класс изменяется по разным причинам (бизнес-логика, формат вывода, хранение).

```kotlin
// BAD: Report меняется при изменении расчётов, формата И хранения
class Report(private val data: List<DataPoint>) {
    fun calculateMetrics(): Metrics = Metrics(
        total = data.sumOf { it.value },
        average = data.map { it.value }.average()
    )

    fun renderHtml(): String =
        "<h1>Report</h1><p>Total: ${calculateMetrics().total}</p>"

    fun saveToDatabase(db: Database) {
        db.execute("INSERT INTO reports ...", calculateMetrics())
    }
}
```

```kotlin
// GOOD: каждый класс меняется по одной причине
class ReportCalculator {
    fun calculate(data: List<DataPoint>): Metrics = Metrics(
        total = data.sumOf { it.value },
        average = data.map { it.value }.average()
    )
}

class HtmlReportRenderer {
    fun render(metrics: Metrics): String =
        "<h1>Report</h1><p>Total: ${metrics.total}</p>"
}

class ReportRepository(private val db: Database) {
    fun save(metrics: Metrics) {
        db.execute("INSERT INTO reports ...", metrics)
    }
}
```

---

### Shotgun Surgery

**Признаки:** одно изменение требует правок в множестве классов. Противоположность Divergent Change.

```kotlin
// BAD: добавление нового поля "middleName" требует правок в:
// - User.kt
// - UserDto.kt
// - UserMapper.kt
// - UserValidator.kt
// - UserRepository.kt
// - UserController.kt
// - user_form.html

// GOOD: Move Method / Move Field — сконцентрировать связанную логику.
// Один маппер через extension-функцию:
fun User.toDto(): UserDto = UserDto(
    fullName = "$firstName $middleName $lastName".trim(),
    email = email.value
)
```

> [!info] Kotlin-нюанс
> Extension-функции позволяют добавить маппинг прямо к классу, не раздувая его. `User.toDto()` живёт в файле `UserMappings.kt` --- изменение формата затрагивает один файл.

---

## Couplers: сильная связанность

### Feature Envy

**Признаки:** метод обращается к данным другого класса больше, чем к своим.

```kotlin
// BAD: OrderPrinter завидует данным Order
class OrderPrinter {
    fun print(order: Order) {
        println("Customer: ${order.customer.name}")
        println("Address: ${order.customer.address.street}, " +
                "${order.customer.address.city}")
        val total = order.items.sumOf { it.price * it.quantity }
        println("Total: $${"%.2f".format(total)}")
    }
}
```

```kotlin
// GOOD: логика форматирования — в Order
class Order(
    val customer: Customer,
    val items: List<OrderItem>
) {
    fun calculateTotal(): BigDecimal =
        items.sumOf { it.subtotal() }

    fun formatForPrint(): String = buildString {
        appendLine("Customer: ${customer.name}")
        appendLine("Address: ${customer.address.format()}")
        appendLine("Total: $${"%.2f".format(calculateTotal())}")
    }
}

class OrderPrinter {
    fun print(order: Order) = println(order.formatForPrint())
}
```

> [!info] Kotlin-нюанс
> Extension-функции --- палка о двух концах. `Order.formatForPrint()` можно оформить как extension, чтобы не засорять сам `Order`. Но если extension вызывает 5 внутренних полей --- это Feature Envy, замаскированный под extension. Правило: extension должна работать через публичный API.

---

### Message Chains

**Признаки:** `a.getB().getC().getD().doSomething()` --- нарушение Law of Demeter.

```kotlin
// BAD: цепочка вызовов
fun getManagerName(employee: Employee): String =
    employee.department.manager.person.name

// GOOD: Hide Delegate — каждый уровень скрывает следующий
class Employee(private val department: Department) {
    fun getManagerName(): String = department.getManagerName()
}

class Department(private val manager: Manager) {
    fun getManagerName(): String = manager.name
}
```

---

### Middle Man

**Признаки:** класс делегирует > 50% своих методов другому объекту.

```kotlin
// BAD: TeamLead просто проксирует всё в Developer
class TeamLead(private val developer: Developer) {
    fun writeCode() = developer.writeCode()
    fun review() = developer.review()
    fun deploy() = developer.deploy()
    fun debug() = developer.debug()
}

// GOOD: убрать Middle Man — клиент работает напрямую
// Или оставить TeamLead только для того, что он реально добавляет:
class TeamLead(private val developer: Developer) {
    fun assignAndTrack(task: Task) {
        developer.writeCode(task)
        notifyManager(task)  // <- собственная логика
    }
}
```

---

## Dispensables: лишнее

### Lazy Class

**Признаки:** класс делает слишком мало, чтобы оправдать своё существование.

```kotlin
// BAD: класс-обёртка без добавленной ценности
class StringUtils {
    fun isEmpty(s: String): Boolean = s.isEmpty()
    fun trim(s: String): String = s.trim()
}

// В Kotlin это уже есть на String. Класс не нужен — удалите его.
```

---

### Speculative Generality

**Признаки:** абстракции "на будущее" (интерфейс с одной реализацией, паттерн Strategy когда достаточно лямбды).

```kotlin
// BAD: YAGNI — интерфейс + фабрика + стратегия для одного алгоритма
interface SortingStrategy {
    fun sort(items: List<Int>): List<Int>
}

class QuickSortStrategy : SortingStrategy {
    override fun sort(items: List<Int>): List<Int> = items.sorted()
}

class SortingStrategyFactory {
    fun create(type: String): SortingStrategy = when (type) {
        "quick" -> QuickSortStrategy()
        else -> throw IllegalArgumentException()
    }
}
```

```kotlin
// GOOD: в Kotlin лямбда заменяет Strategy с одним методом
fun processItems(
    items: List<Int>,
    sort: (List<Int>) -> List<Int> = List<Int>::sorted
): List<Int> = sort(items)

// Нужна другая сортировка? Передай лямбду:
processItems(items) { it.sortedDescending() }
```

> [!info] Kotlin-нюанс
> Functional types `(Input) -> Output` заменяют интерфейсы с одним методом. Не создавайте `interface Strategy { fun execute() }`, если `() -> Unit` достаточно. YAGNI --- ваш лучший друг.

---

### Dead Code

**Признаки:** неиспользуемые функции, недостижимые ветки, закомментированный код.

```kotlin
// BAD: мёртвый код накапливается
class UserService {
    fun getUser(id: Long): User = TODO()

    // "может пригодится" — не пригодится
    fun getUserByEmail(email: String): User = TODO()      // 0 вызовов
    fun getUserByPhone(phone: String): User = TODO()      // 0 вызовов

    // fun oldGetUser(id: Long): User = ...   // закомментировано год назад

    fun deleteUser(id: Long) {
        val user = getUser(id)
        if (false) {  // недостижимая ветка
            sendNotification(user)
        }
        // ...
    }
}

// GOOD: удалить. Git помнит всё. Нужно — восстановите из истории.
```

**Инструменты обнаружения:** IntelliJ IDEA подсвечивает серым, detekt правило `UnusedPrivateMember`.

---

### Comments как запах

**Признаки:** комментарий объясняет **что** делает код (вместо того, чтобы код был самодокументируемым).

```kotlin
// BAD: комментарий как дезодорант для плохого кода
// Check if employee is eligible for full benefits
if (employee.flags and HOURLY_FLAG > 0 && employee.age > 65) { ... }

// GOOD: код читается как текст
if (employee.isEligibleForFullBenefits()) { ... }

// Комментарии НУЖНЫ для: "почему" (не "что"), публичного API (KDoc), обходных путей
/**
 * Используем [LinkedHashMap] вместо [HashMap] потому что порядок вставки
 * важен для сериализации в JSON (API contract с мобильным клиентом).
 */
```

---

## Инструменты обнаружения

### detekt --- статический анализ для Kotlin

```kotlin
// build.gradle.kts
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.7"
}

detekt {
    config.setFrom("$projectDir/config/detekt/detekt.yml")
    buildUponDefaultConfig = true
}
```

Ключевые правила detekt для обнаружения запахов:

| Правило detekt | Запах | Порог по умолчанию |
|----------------|-------|-------------------|
| `LongMethod` | Long Method | 60 строк |
| `LargeClass` | Large Class | 600 строк |
| `LongParameterList` | Long Parameter List | 6 параметров |
| `TooManyFunctions` | Large Class (по поведению) | 11 функций |
| `ComplexCondition` | Complex Conditional | 4 условия |
| `NestedBlockDepth` | Глубокая вложенность | 4 уровня |
| `UnusedPrivateMember` | Dead Code | --- |
| `MagicNumber` | Magic Number | --- |

### SonarQube

Поддерживает Kotlin через плагин. Визуализирует технический долг, отслеживает тренды.

### IntelliJ IDEA Inspections

- **Analyze > Inspect Code** --- полный анализ проекта
- **Analyze > Code Cleanup** --- автоматическое исправление
- Серый текст --- неиспользуемый код
- Жёлтая подсветка --- потенциальные проблемы

---

## Сводная таблица: запах, Kotlin-лечение, инструмент

| Запах | Kotlin-лечение | Инструмент |
|-------|---------------|------------|
| Long Method | scope-функции, Extract Function | detekt `LongMethod` |
| Large Class | `data class`, Extract Class | detekt `LargeClass` |
| Long Parameter List | именованные параметры, дефолты, `data class` | detekt `LongParameterList` |
| Primitive Obsession | `value class`, `enum class` | --- |
| Data Clumps | `data class` | --- |
| Switch Statements | `sealed class` + `when` | detekt custom rule |
| Refused Bequest | интерфейсы, делегация (`by`) | --- |
| Divergent Change | Extract Class, SRP | --- |
| Shotgun Surgery | Move Method, extension functions | --- |
| Feature Envy | Move Method, extension (через public API) | --- |
| Message Chains | Hide Delegate | --- |
| Speculative Generality | лямбды вместо Strategy | detekt `TooManyFunctions` |
| Dead Code | удалить (Git помнит) | detekt `UnusedPrivateMember` |

---

## Проверь себя

<details>
<summary>1. Чем code smell отличается от бага?</summary>

**Ответ:**

**Баг** --- программа работает неправильно (неверный результат, падение). **Code smell** --- программа работает правильно, но её структура затрудняет изменения, понимание и тестирование. Запах --- индикатор проблем в дизайне, не в поведении. Запах приводит к багам косвенно: чем сложнее код, тем легче ошибиться при следующем изменении.

</details>

<details>
<summary>2. Какой запах решает `value class` в Kotlin и почему это лучше обычной обёртки?</summary>

**Ответ:**

`value class` решает **Primitive Obsession** --- использование примитивов (`String`, `Int`) вместо типов предметной области. В отличие от обычного класса-обёртки, `value class` имеет **нулевой оверхед в рантайме**: компилятор подставляет примитив, сохраняя проверку типов на этапе компиляции. `value class Email(val value: String)` в байткоде --- просто `String`, но нельзя передать `Email` туда, где ожидается `UserId`.

</details>

<details>
<summary>3. Почему `sealed class` + `when` лучше, чем `enum` + `when` + `else`?</summary>

**Ответ:**

1. **`sealed class`** поддерживает подтипы с разными данными (в отличие от enum).
2. **`when` без `else`** --- exhaustive: компилятор проверяет, что обработаны все подтипы.
3. При добавлении нового подтипа все `when`-выражения без `else` дадут **ошибку компиляции** --- невозможно забыть обработать новый случай.
4. `else` маскирует проблему: новый подтип тихо попадает в `else`-ветку.

</details>

<details>
<summary>4. Extension-функция лечит Feature Envy или маскирует его?</summary>

**Ответ:**

**Зависит от реализации.** Extension, работающая через **публичный API** класса --- лечит (логика рядом с данными без раздувания класса). Extension, обращающаяся к **5+ внутренним полям** через геттеры --- маскирует Feature Envy: по сути это метод, который должен быть внутри класса. Правило: если extension использует больше данных целевого класса, чем своих параметров --- это Move Method, а не extension.

</details>

<details>
<summary>5. Когда комментарий --- запах, а когда --- необходимость?</summary>

**Ответ:**

**Запах:** комментарий объясняет **что** делает код (→ переименуйте метод). **Необходимость:** комментарий объясняет **почему** код написан именно так (обходной путь, бизнес-правило, ссылка на тикет). Также нужны: KDoc для публичного API, TODO с номером задачи, предупреждения о неочевидном поведении.

</details>

---

## Ключевые карточки

Code smell --- что это и кто придумал термин?
?
Поверхностный признак, указывающий на глубокую проблему в дизайне кода. Термин придумал Кент Бек для книги Мартина Фаулера "Refactoring" (1999). Запах --- не баг: программа работает, но структура затрудняет изменения. Пять категорий: Bloaters, OO Abusers, Change Preventers, Couplers, Dispensables.

Как Kotlin `value class` решает Primitive Obsession?
?
`value class Email(val value: String)` --- обёртка с нулевым оверхедом. В байткоде компилятор подставляет примитив, но на этапе компиляции проверяет типы. Нельзя передать `Email` вместо `UserId`. Валидация в `init`-блоке. Стоимость создания нового типа --- 3 строки.

Как `sealed class` + `when` убивает Switch Statements?
?
1) `sealed class` ограничивает иерархию --- все подтипы известны компилятору. 2) `when` без `else` --- exhaustive: компилятор проверяет полноту. 3) Новый подтип → ошибка компиляции во всех `when`. 4) В отличие от enum, подтипы могут хранить разные данные (`data class International(val country: String)`).

Чем Divergent Change отличается от Shotgun Surgery?
?
Divergent Change: ОДИН класс меняется по РАЗНЫМ причинам (нарушение SRP). Shotgun Surgery: ОДНО изменение требует правок в МНОГИХ классах (разбросанная логика). Лечение противоположное: DC → Extract Class (разделить). SS → Move Method/Field (сконцентрировать).

Какие правила detekt обнаруживают запахи кода?
?
`LongMethod` (> 60 строк), `LargeClass` (> 600 строк), `LongParameterList` (> 6 параметров), `TooManyFunctions` (> 11), `ComplexCondition` (> 4 условий), `NestedBlockDepth` (> 4 уровней), `UnusedPrivateMember` (мёртвый код), `MagicNumber`. Пороги настраиваемые через `detekt.yml`.

Когда лямбда заменяет паттерн Strategy в Kotlin?
?
Когда интерфейс стратегии имеет один метод. `interface Strategy { fun execute(): Result }` → `(Input) -> Result`. Лямбда легче: нет файла, нет класса, нет фабрики. Создавать Strategy-интерфейс стоит, только если: реализации имеют состояние, нужна сериализация, или больше одного метода.

Что такое Feature Envy и как отличить лечение от маскировки?
?
Метод обращается к данным чужого класса больше, чем к своим. Лечение: Move Method (перенести к данным). Extension-функция лечит, если работает через публичный API. Extension маскирует Feature Envy, если обращается к 5+ внутренним полям --- тогда это должен быть метод класса.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[refactoring-catalog]] | Техники исправления обнаруженных запахов |
| Углубиться | [[legacy-code-strategies]] | Запахи в legacy-коде и стратегии работы с ними |
| Смежная тема | [[clean-code]] | Принципы чистого кода и SOLID |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

## Источники

- Fowler M. "Refactoring: Improving the Design of Existing Code" (2nd ed., 2018) --- каталог запахов и рефакторингов
- Martin R.C. "Clean Code" (2008) --- Chapter 17: Smells and Heuristics
- Moskala M. "Effective Kotlin" (2nd ed., 2022) --- Kotlin-идиомы для чистого кода
- [Refactoring Guru — Code Smells](https://refactoring.guru/refactoring/smells) --- визуальный каталог с примерами
- [Martin Fowler — bliki: CodeSmell](https://martinfowler.com/bliki/CodeSmell.html) --- определение термина
- [detekt — Complexity Rules](https://detekt.dev/docs/rules/complexity/) --- правила статического анализа для Kotlin
- [Baeldung — Identifying and Addressing Kotlin Code Smells](https://www.baeldung.com/kotlin/code-smells-recognize-mitigate) --- практический гайд
- [LogRocket — Identifying and Addressing Kotlin Code Smells](https://blog.logrocket.com/identifying-addressing-kotlin-code-smells/) --- примеры с Kotlin

---

*Проверено: 2026-02-19*
