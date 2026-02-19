---
title: "SOLID: пять принципов объектно-ориентированного проектирования"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
tags:
  - topic/programming
  - topic/oop
  - topic/solid
  - topic/kotlin
related:
  - "[[oop-fundamentals]]"
  - "[[clean-code]]"
  - "[[dry-kiss-yagni]]"
  - "[[coupling-cohesion]]"
  - "[[kotlin-oop]]"
  - "[[kotlin-best-practices]]"
  - "[[design-patterns-overview]]"
---

# SOLID: пять принципов объектно-ориентированного проектирования

В 2000 году Роберт Мартин (Uncle Bob) описал пять принципов дизайна классов. В 2004 году Майкл Фезерс сложил первые буквы в акроним SOLID. С тех пор эти принципы стали де-факто стандартом ООП-проектирования — и одновременно самым распространённым источником over-engineering. Проблема не в принципах: проблема в том, что их применяют механически, без понимания ЗАЧЕМ они существуют. Kotlin делает соблюдение SOLID проще, чем в Java: `final` by default поддерживает OCP, `sealed class` гарантирует LSP, `by` delegation реализует DIP на уровне языка.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Основы ООП | Классы, интерфейсы, наследование, полиморфизм | [[oop-fundamentals]] |
| Kotlin OOP | data class, sealed class, delegation, visibility | [[kotlin-oop]] |

---

## История и контекст

**Хронология:**

```
1988  Bertrand Meyer        — Open/Closed Principle (книга "Object-Oriented
                              Software Construction")
1987  Barbara Liskov        — Liskov Substitution Principle (доклад на OOPSLA)
1994  Liskov & Wing         — Формализация LSP ("A behavioral notion of subtyping")
1996  Robert C. Martin      — Переосмысление OCP через абстракции
2000  Robert C. Martin      — Статья "Design Principles and Design Patterns":
                              SRP, OCP, LSP, ISP, DIP собраны вместе
2003  Martin                — Книга "Agile Software Development"
2004  Michael Feathers      — Придумал акроним S.O.L.I.D.
2017  Martin                — "Clean Architecture" — SOLID на уровне компонентов
```

**Зачем создали SOLID:** Мартин заметил три "запаха дизайна":
- **Rigidity** (жёсткость) — маленькое изменение требует каскад правок
- **Fragility** (хрупкость) — исправление в одном месте ломает другое
- **Immobility** (неподвижность) — модуль нельзя переиспользовать в другом проекте

SOLID — ответ на эти проблемы. Не законы физики, а **эвристики для 80% случаев**.

> [!warning] Главная ошибка
> Слепое следование SOLID без понимания контекста ведёт к over-engineering. Каждый принцип — это trade-off. Понимание ПОЧЕМУ принцип существует важнее механического следования.

---

## Обзор пяти принципов

```
┌────┬────────────────────────────────────────────────────────────────────┐
│ S  │ Single Responsibility — один класс = одна причина для изменений   │
├────┼────────────────────────────────────────────────────────────────────┤
│ O  │ Open/Closed — открыт для расширения, закрыт для модификации       │
├────┼────────────────────────────────────────────────────────────────────┤
│ L  │ Liskov Substitution — подтип безопасно заменяет базовый тип       │
├────┼────────────────────────────────────────────────────────────────────┤
│ I  │ Interface Segregation — маленькие role-based интерфейсы            │
├────┼────────────────────────────────────────────────────────────────────┤
│ D  │ Dependency Inversion — зависеть от абстракций, не реализаций      │
└────┴────────────────────────────────────────────────────────────────────┘
```

---

## S — Single Responsibility Principle

### Определение

**Оригинал (Martin, 2000):** *"A class should have one, and only one, reason to change."*

**Уточнение (Martin, 2014):** *"This principle is about people. When changes are requested, those changes can only originate from a single person, or rather, a single tightly coupled group of people representing a single narrowly defined business function."*

**Простыми словами:** Один класс отвечает перед одним "актором" (стейкхолдером / командой / бизнес-функцией).

### Что ДЕЙСТВИТЕЛЬНО означает "одна причина"

```
"Причина изменения" ≠ "делает одну вещь"
"Причина изменения" = один Actor (стейкхолдер)

Пример: класс Employee в payroll-системе
┌──────────────────────────┐
│       Employee           │
├──────────────────────────┤
│ calculatePay()           │ ← меняет бухгалтерия
│ generateReport()         │ ← меняет менеджмент
│ save()                   │ ← меняет DBA
└──────────────────────────┘
   3 актора = 3 причины = нарушение SRP
```

### Нарушение и исправление в Kotlin

```kotlin
// НАРУШЕНИЕ SRP: 3 актора в одном классе
class Employee(
    val id: Long,
    val name: String,
    val hourlyRate: Double,
    val hoursWorked: Double
) {
    // Актор 1: бухгалтерия
    fun calculatePay(): Double {
        return hourlyRate * hoursWorked + calculateOvertime()
    }

    // Актор 2: менеджмент
    fun generateReport(): String {
        val hours = regularHours()  // Используется и в calculatePay!
        return "Employee $name worked $hours regular hours"
    }

    // Актор 3: DBA
    fun save() {
        val sql = "INSERT INTO employees VALUES ('$name', $hourlyRate)"
        // database.execute(sql)
    }

    // Общий метод — источник проблем!
    // Бухгалтерия попросит изменить расчёт → сломает отчёт менеджмента
    private fun regularHours(): Double = minOf(hoursWorked, 8.0)
    private fun calculateOvertime(): Double =
        if (hoursWorked > 8) (hoursWorked - 8) * hourlyRate * 1.5 else 0.0
}
```

```kotlin
// ИСПРАВЛЕНИЕ: разделение по акторам

// Данные — чистый data class без поведения
data class Employee(
    val id: Long,
    val name: String,
    val hourlyRate: Double,
    val hoursWorked: Double
)

// Актор: бухгалтерия
class PayCalculator {
    fun calculatePay(employee: Employee): Double {
        val regular = minOf(employee.hoursWorked, 8.0) * employee.hourlyRate
        val overtime = if (employee.hoursWorked > 8)
            (employee.hoursWorked - 8) * employee.hourlyRate * 1.5
        else 0.0
        return regular + overtime
    }
}

// Актор: менеджмент
class ReportGenerator {
    fun generateReport(employee: Employee): String {
        return "Employee ${employee.name} worked ${employee.hoursWorked}h"
    }
}

// Актор: DBA
class EmployeeRepository(private val db: Database) {
    fun save(employee: Employee) {
        db.execute(
            "INSERT INTO employees (name, rate) VALUES (?, ?)",
            employee.name, employee.hourlyRate
        )
    }

    fun findById(id: Long): Employee? = db.query("SELECT * FROM employees WHERE id = ?", id)
}
```

### SRP с `sealed class` — иерархия ответственностей

```kotlin
// Каждый вариант sealed class — одна ответственность
sealed class Notification {
    abstract fun send(): Boolean
    abstract fun preview(): String

    data class Email(
        val to: String,
        val subject: String,
        val body: String
    ) : Notification() {
        override fun send(): Boolean {
            // Только отправка email — ничего лишнего
            println("SMTP: $to — $subject")
            return true
        }
        override fun preview() = "Email → $to: $subject"
    }

    data class Push(
        val deviceToken: String,
        val title: String,
        val payload: Map<String, String>
    ) : Notification() {
        override fun send(): Boolean {
            println("FCM: $deviceToken — $title")
            return true
        }
        override fun preview() = "Push → $title"
    }
}
```

> [!info] Kotlin-нюанс: `data class` и SRP
> `data class` естественно следует SRP: его единственная ответственность — хранение данных. equals, hashCode, copy, toString генерируются автоматически. Бизнес-логику выносим в отдельные классы (`PayCalculator`, `ReportGenerator`), а `data class` остаётся чистым контейнером данных.

### Когда НЕ применять SRP

| Ситуация | Почему SRP вредит |
|----------|-------------------|
| Один разработчик на проекте | Один актор — одна причина изменений по определению |
| MVP / прототип | Разделение на 10 классов убьёт скорость без пользы |
| 3 тесно связанных метода | Искусственное разделение создаёт complexity без cohesion |
| Utility-класс | `StringUtils.capitalize()`, `StringUtils.trim()` — один актор, одна область |

---

## O — Open/Closed Principle

### Определение

**Оригинал (Meyer, 1988):** *"Software entities should be open for extension, but closed for modification."*

**Интерпретация Martin (1996):** Расширение через **абстракции и полиморфизм**, а не через наследование реализации.

**Простыми словами:** Добавление нового функционала не должно требовать изменения уже протестированного кода.

### Две интерпретации OCP

| Meyer (1988) | Martin (1996) |
|--------------|---------------|
| Расширение через наследование | Расширение через абстракции |
| `class ExtendedList extends ArrayList` | `interface PaymentHandler` + новые реализации |
| Tight coupling к базовому классу | Loose coupling через интерфейсы |
| **Устарело** | **Современный подход** |

### Kotlin: `final` by default как инструмент OCP

```kotlin
// Kotlin: классы закрыты для модификации по умолчанию (final)
// Это и есть OCP на уровне языка!

// Закрыт для модификации: PaymentProcessor не меняется при добавлении нового типа оплаты
class PaymentProcessor(
    private val handlers: List<PaymentHandler>
) {
    fun process(payment: Payment): PaymentResult {
        val handler = handlers.find { it.canHandle(payment) }
            ?: return PaymentResult.Error("Нет обработчика для ${payment.type}")
        return handler.process(payment)
    }
}

// Открыт для расширения: новый тип оплаты = новый класс
interface PaymentHandler {
    fun canHandle(payment: Payment): Boolean
    fun process(payment: Payment): PaymentResult
}

class CardPaymentHandler : PaymentHandler {
    override fun canHandle(payment: Payment) = payment.type == "card"
    override fun process(payment: Payment): PaymentResult {
        // Обработка карты
        return PaymentResult.Success(transactionId = "card-${payment.id}")
    }
}

class PayPalHandler : PaymentHandler {
    override fun canHandle(payment: Payment) = payment.type == "paypal"
    override fun process(payment: Payment): PaymentResult {
        return PaymentResult.Success(transactionId = "pp-${payment.id}")
    }
}

// Добавили крипто? Новый класс — PaymentProcessor НЕ меняется!
class CryptoHandler : PaymentHandler {
    override fun canHandle(payment: Payment) = payment.type == "crypto"
    override fun process(payment: Payment): PaymentResult {
        return PaymentResult.Success(transactionId = "btc-${payment.id}")
    }
}
```

### Extension functions — расширение без модификации

```kotlin
// Extension functions — идеальная реализация OCP:
// добавляем поведение к СУЩЕСТВУЮЩЕМУ классу без его изменения

// Класс из библиотеки — менять нельзя
data class Order(
    val items: List<OrderItem>,
    val discount: Double = 0.0
)

data class OrderItem(val name: String, val price: Double, val quantity: Int)

// Расширяем поведение Order без модификации исходного кода
fun Order.totalPrice(): Double =
    items.sumOf { it.price * it.quantity } * (1 - discount)

fun Order.itemCount(): Int =
    items.sumOf { it.quantity }

fun Order.summary(): String = buildString {
    appendLine("Заказ: ${itemCount()} товаров")
    items.forEach { appendLine("  - ${it.name}: ${it.price} x ${it.quantity}") }
    appendLine("Итого: ${"%.2f".format(totalPrice())} (скидка ${discount * 100}%)")
}

// Класс Order не изменён, но имеет новое поведение
val order = Order(
    items = listOf(
        OrderItem("Kotlin in Action", 49.99, 1),
        OrderItem("Effective Kotlin", 39.99, 2)
    ),
    discount = 0.1
)
println(order.summary())
```

> [!info] Kotlin-нюанс: Extension functions и OCP
> Extension functions — уникальный для Kotlin (и нескольких других языков) способ соблюдать OCP. В Java для добавления поведения к чужому классу нужен Utility-класс с static-методами (`Collections.sort(list)`). В Kotlin: `list.sorted()` — выглядит как метод класса, но класс не изменён. Это compile-time dispatch, не runtime — zero overhead.

### `sealed class` + `when` как OCP-инструмент

```kotlin
// sealed class — закрытая иерархия: OCP на уровне типов
sealed class FileExportFormat {
    data class Csv(val delimiter: Char = ',') : FileExportFormat()
    data class Json(val prettyPrint: Boolean = false) : FileExportFormat()
    data class Xml(val rootElement: String) : FileExportFormat()
}

class FileExporter {
    fun export(data: List<Map<String, Any>>, format: FileExportFormat): String =
        when (format) {
            is FileExportFormat.Csv -> exportCsv(data, format.delimiter)
            is FileExportFormat.Json -> exportJson(data, format.prettyPrint)
            is FileExportFormat.Xml -> exportXml(data, format.rootElement)
        }
    // Добавление нового формата = новый подкласс sealed class
    // + ошибка компиляции в when → невозможно забыть обработать

    private fun exportCsv(data: List<Map<String, Any>>, delimiter: Char): String = TODO()
    private fun exportJson(data: List<Map<String, Any>>, prettyPrint: Boolean): String = TODO()
    private fun exportXml(data: List<Map<String, Any>>, rootElement: String): String = TODO()
}
```

### Когда НЕ применять OCP

| Ситуация | Почему `if/when` лучше |
|----------|------------------------|
| 2-3 варианта навсегда | `when (direction) { NORTH, SOUTH, EAST, WEST }` проще интерфейса |
| Неизвестно где будет расширение | Преждевременная абстракция — гадание о будущем |
| Одноразовый скрипт | Добавлять extension points для скрипта на 50 строк — overengineering |
| Hot path в performance-critical коде | Виртуальные вызовы через интерфейс медленнее `when` |

---

## L — Liskov Substitution Principle

### Определение

**Оригинал (Liskov, 1987):** *"If for each object o1 of type S there is an object o2 of type T such that for all programs P defined in terms of T, the behavior of P is unchanged when o1 is substituted for o2, then S is a subtype of T."*

**Простыми словами:** Если функция работает с базовым типом, она должна корректно работать с ЛЮБЫМ его подтипом без сюрпризов.

### Behavioral Subtyping: правила контракта

```
Контракт базового типа включает:

1. Preconditions  — что ожидается на входе
   Подтип может ОСЛАБИТЬ (принимать больше)

2. Postconditions — что гарантируется на выходе
   Подтип может УСИЛИТЬ (гарантировать больше)

3. Invariants     — что всегда истинно
   Подтип НЕ МОЖЕТ нарушать
```

### Классический пример нарушения LSP

```kotlin
// НАРУШЕНИЕ LSP: Rectangle / Square
open class Rectangle(
    open var width: Double,
    open var height: Double
) {
    open fun area(): Double = width * height
}

class Square(side: Double) : Rectangle(side, side) {
    // Postcondition Rectangle: setWidth не меняет height
    // Square НАРУШАЕТ этот контракт!
    override var width: Double = side
        set(value) {
            field = value
            super.height = value  // Нарушение: height тоже меняется
        }

    override var height: Double = side
        set(value) {
            field = value
            super.width = value   // Нарушение: width тоже меняется
        }
}

// Код, который ломается из-за нарушения LSP
fun resizeRectangle(rect: Rectangle) {
    rect.width = 10.0
    rect.height = 5.0
    // Postcondition: area = 50.0
    check(rect.area() == 50.0) {
        "Ожидали 50.0, получили ${rect.area()}"
    }
    // С Rectangle: OK (50.0)
    // С Square: FAIL (25.0) — height перезаписал width!
}
```

### Правильное решение в Kotlin

```kotlin
// РЕШЕНИЕ 1: sealed class — замена наследования на union type
sealed class Shape {
    abstract fun area(): Double

    data class Rectangle(val width: Double, val height: Double) : Shape() {
        override fun area(): Double = width * height
    }

    data class Square(val side: Double) : Shape() {
        override fun area(): Double = side * side
    }

    data class Circle(val radius: Double) : Shape() {
        override fun area(): Double = Math.PI * radius * radius
    }
}

// Exhaustive when гарантирует обработку ВСЕХ подтипов
fun describe(shape: Shape): String = when (shape) {
    is Shape.Rectangle -> "Прямоугольник ${shape.width}x${shape.height}"
    is Shape.Square -> "Квадрат ${shape.side}"
    is Shape.Circle -> "Круг R=${shape.radius}"
    // Новый подтип → ошибка компиляции здесь
}
```

> [!info] Kotlin-нюанс: `sealed class` и LSP
> `sealed class` гарантирует LSP на уровне компилятора. Все подтипы известны compile-time, `when` проверяет exhaustiveness. Если подтип изменит поведение несовместимо — другие ветки `when` не затронуты, потому что каждая обрабатывает конкретный тип. Это фундаментально отличается от открытого наследования, где подтип может сломать код, ожидающий базовый тип.

### Нарушение LSP: `data class` equals/hashCode

```kotlin
// ЛОВУШКА: data class автогенерация может нарушить LSP

open class Account(val id: Long, open val balance: Long)

// data class наследует от open class — equals/hashCode сгенерированы
// только для полей primary constructor
data class PremiumAccount(
    override val balance: Long,
    val tier: String
) : Account(0, balance) {
    // id НЕ участвует в equals/hashCode!
    // Два PremiumAccount с разными id считаются равными
}

val a = PremiumAccount(1000, "Gold")
val b = PremiumAccount(1000, "Gold")
println(a == b) // true — хотя у них могут быть разные id!
// Нарушение LSP: Account.equals зависит от id, PremiumAccount — нет
```

```kotlin
// РЕШЕНИЕ: не наследовать data class от open class
// Используйте interface или composition

interface HasBalance {
    val balance: Long
}

data class RegularAccount(val id: Long, override val balance: Long) : HasBalance
data class PremiumAccount(val id: Long, override val balance: Long, val tier: String) : HasBalance

// Теперь equals/hashCode корректны для каждого класса отдельно
```

### Признаки нарушения LSP

| Признак | Почему это нарушение | Kotlin-альтернатива |
|---------|---------------------|---------------------|
| `is` / `instanceof` проверки | Клиент знает о конкретном подтипе | `sealed class` + `when` |
| `throw NotImplementedException` | Метод не поддерживается — контракт сломан | ISP: разделить интерфейс |
| Комментарий "не вызывать этот метод" | Документация вместо контракта | Убрать метод из интерфейса |
| Переопределение с пустым телом | Подтип не выполняет контракт | Выделить отдельный интерфейс |
| `override` меняет семантику | Postcondition нарушен | Composition вместо inheritance |

### Когда LSP можно ослабить

| Ситуация | Обоснование |
|----------|-------------|
| Adapter Pattern | Адаптер может частично реализовывать интерфейс, если это документировано |
| Legacy code | Лучше документировать ограничения, чем ломать API |
| Null Object Pattern | Объект-заглушка с пустыми методами — осознанное решение |

---

## I — Interface Segregation Principle

### Определение

**Оригинал (Martin):** *"Clients should not be forced to depend upon interfaces that they do not use."*

**История:** Мартин разработал ISP консультируя Xerox. Класс `Job` использовался для печати, сканирования, факса, степлера. Изменение метода для степлера перекомпилировало модуль принтера.

**Простыми словами:** Много специализированных интерфейсов лучше одного "жирного".

### Fat Interface — проблема

```kotlin
// НАРУШЕНИЕ ISP: один "жирный" интерфейс для всего
interface SmartDevice {
    fun print(document: String)
    fun scan(): ByteArray
    fun fax(document: String, number: String)
    fun copyDocument(document: String, copies: Int)
    fun connectWifi(ssid: String, password: String)
    fun sendEmail(to: String, subject: String, body: String)
}

// Простой принтер вынужден "реализовывать" всё
class SimplePrinter : SmartDevice {
    override fun print(document: String) = println("Printing: $document")

    // ISP нарушение: эти методы не нужны, но интерфейс заставляет
    override fun scan(): ByteArray = throw UnsupportedOperationException("Нет сканера")
    override fun fax(document: String, number: String) = throw UnsupportedOperationException()
    override fun copyDocument(document: String, copies: Int) = throw UnsupportedOperationException()
    override fun connectWifi(ssid: String, password: String) = throw UnsupportedOperationException()
    override fun sendEmail(to: String, subject: String, body: String) = throw UnsupportedOperationException()
    // 5 из 6 методов бросают исключение — явный red flag
}
```

### Исправление: role-based interfaces

```kotlin
// ИСПРАВЛЕНИЕ: интерфейсы по РОЛЯМ клиентов

interface Printer {
    fun print(document: String)
}

interface Scanner {
    fun scan(): ByteArray
}

interface Fax {
    fun fax(document: String, number: String)
}

interface NetworkCapable {
    fun connectWifi(ssid: String, password: String)
}

// Простой принтер — реализует только то, что умеет
class SimplePrinter : Printer {
    override fun print(document: String) = println("Printing: $document")
}

// МФУ — реализует несколько интерфейсов
class MultiFunctionDevice : Printer, Scanner, Fax, NetworkCapable {
    override fun print(document: String) = println("MFD Printing: $document")
    override fun scan(): ByteArray = byteArrayOf() // Реальное сканирование
    override fun fax(document: String, number: String) = println("Faxing to $number")
    override fun connectWifi(ssid: String, password: String) = println("Connected to $ssid")
}

// Клиент зависит только от нужного интерфейса
class DocumentService(private val printer: Printer) {
    // Не знает и не зависит от Scanner, Fax, NetworkCapable
    fun printReport(data: String) {
        printer.print("Report: $data")
    }
}
```

### Kotlin: интерфейсы с default-реализациями и ISP

```kotlin
// Kotlin интерфейсы с default implementations — мощный инструмент ISP

interface Identifiable {
    val id: String
}

interface Auditable {
    val createdAt: Long
    val updatedAt: Long

    // Default implementation — не нужно реализовывать в каждом классе
    fun auditLog(): String = "Created: $createdAt, Updated: $updatedAt"
}

interface Validatable {
    fun validate(): List<String>  // Возвращает список ошибок

    // Default: объект валиден если ошибок нет
    fun isValid(): Boolean = validate().isEmpty()
}

// Каждый класс берёт только нужные интерфейсы
data class User(
    override val id: String,
    override val createdAt: Long,
    override val updatedAt: Long,
    val email: String,
    val name: String
) : Identifiable, Auditable, Validatable {

    override fun validate(): List<String> = buildList {
        if (!email.contains("@")) add("Невалидный email")
        if (name.isBlank()) add("Имя не может быть пустым")
    }
}

data class Config(
    override val id: String,
    val key: String,
    val value: String
) : Identifiable {
    // Config не Auditable и не Validatable — и не обязан быть
}
```

### Kotlin: delegation `by` для селективной реализации интерфейса

```kotlin
// Delegation by — реализуем часть интерфейса через делегат

interface Repository<T> {
    fun findById(id: Long): T?
    fun findAll(): List<T>
    fun save(entity: T): T
    fun delete(id: Long): Boolean
}

// Read-only репозиторий — только чтение, без записи
interface ReadOnlyRepository<T> {
    fun findById(id: Long): T?
    fun findAll(): List<T>
}

class UserReadOnlyRepo(
    private val fullRepo: Repository<User>
) : ReadOnlyRepository<User> {
    override fun findById(id: Long): User? = fullRepo.findById(id)
    override fun findAll(): List<User> = fullRepo.findAll()
    // save() и delete() недоступны — ISP соблюдён
}

// Или через delegation — более идиоматично:
class CachedUserRepo(
    private val delegate: ReadOnlyRepository<User>,
    private val cache: MutableMap<Long, User> = mutableMapOf()
) : ReadOnlyRepository<User> by delegate {
    override fun findById(id: Long): User? {
        return cache.getOrPut(id) { delegate.findById(id) ?: return null }
    }
    // findAll() делегируется автоматически
}
```

> [!info] Kotlin-нюанс: property delegation `by` и ISP
> Kotlin `by` позволяет "собирать" класс из частей, как конструктор LEGO. Вместо реализации одного гигантского интерфейса вы делегируете разные части разным объектам: `class SmartDevice(printer: Printer, scanner: Scanner) : Printer by printer, Scanner by scanner`. Каждый делегат — специалист в своей области.

### Когда НЕ дробить интерфейсы

| Ситуация | Почему оставить один интерфейс |
|----------|-------------------------------|
| Все клиенты используют все методы | Нет "жирности" — интерфейс cohesive |
| 2-3 метода, логически связанных | Дробить `Iterator { hasNext(); next() }` — нелепо |
| CRUD-репозиторий для одной сущности | Один актор (DAL), одна ответственность |
| Rapid prototyping | Сначала работает, потом разделяем |

---

## D — Dependency Inversion Principle

### Определение

**Оригинал (Martin):**
1. *"High-level modules should not depend on low-level modules. Both should depend on abstractions."*
2. *"Abstractions should not depend on details. Details should depend on abstractions."*

**Что значит "инверсия":**

```
Без DIP:                          С DIP:

OrderService                      OrderService
     │                                 │
     │ зависит от                      │ зависит от
     ▼                                 ▼
PostgresDatabase              DatabasePort (interface)
                                       ▲
                                       │ реализует
                                  PostgresAdapter

Стрелка зависимости ИНВЕРТИРОВАНА:
деталь (PostgresAdapter) зависит от абстракции (DatabasePort),
а не наоборот.
```

### DIP ≠ Dependency Injection

| DIP (Принцип) | DI (Механизм) |
|----------------|----------------|
| Зависеть от абстракций | Передавать зависимости извне |
| Архитектурное решение | Техническая реализация |
| Можно соблюдать без DI-контейнера | Dagger, Koin, Hilt |

### Kotlin: Constructor Injection с `val`

```kotlin
// DIP через constructor injection — самый идиоматичный Kotlin-паттерн

// Абстракция: интерфейс, от которого зависит high-level модуль
interface UserRepository {
    suspend fun findById(id: Long): User?
    suspend fun save(user: User): User
    suspend fun delete(id: Long): Boolean
}

interface EmailService {
    suspend fun send(to: String, subject: String, body: String): Boolean
}

// High-level модуль: зависит от АБСТРАКЦИЙ через val-параметры конструктора
class UserRegistrationUseCase(
    private val userRepo: UserRepository,      // Абстракция, не PostgresRepo
    private val emailService: EmailService,    // Абстракция, не SmtpService
    private val logger: Logger                 // Абстракция, не ConsoleLogger
) {
    suspend fun register(name: String, email: String): Result<User> {
        logger.info("Регистрация пользователя: $email")

        // Проверка: пользователь уже существует?
        val existing = userRepo.findById(email.hashCode().toLong())
        if (existing != null) {
            return Result.failure(IllegalStateException("Пользователь уже существует"))
        }

        val user = User(
            id = System.currentTimeMillis(),
            name = name,
            email = email
        )

        val saved = userRepo.save(user)
        emailService.send(email, "Добро пожаловать!", "Привет, $name!")

        return Result.success(saved)
    }
}
```

### Low-level реализации: детали зависят от абстракций

```kotlin
// Реализация 1: PostgreSQL
class PostgresUserRepository(
    private val dataSource: DataSource
) : UserRepository {
    override suspend fun findById(id: Long): User? {
        // SQL-запрос к PostgreSQL
        return dataSource.connection.use { conn ->
            conn.prepareStatement("SELECT * FROM users WHERE id = ?").use { stmt ->
                stmt.setLong(1, id)
                val rs = stmt.executeQuery()
                if (rs.next()) User(rs.getLong("id"), rs.getString("name"), rs.getString("email"))
                else null
            }
        }
    }

    override suspend fun save(user: User): User { /* ... */ return user }
    override suspend fun delete(id: Long): Boolean { /* ... */ return true }
}

// Реализация 2: In-Memory (для тестов)
class InMemoryUserRepository : UserRepository {
    private val store = mutableMapOf<Long, User>()

    override suspend fun findById(id: Long): User? = store[id]
    override suspend fun save(user: User): User { store[user.id] = user; return user }
    override suspend fun delete(id: Long): Boolean = store.remove(id) != null
}

// Реализация 3: Firebase (для мобильного приложения)
class FirebaseUserRepository(
    private val firestore: FirebaseFirestore
) : UserRepository {
    override suspend fun findById(id: Long): User? {
        return firestore.collection("users").document(id.toString()).get().await()?.toObject()
    }
    override suspend fun save(user: User): User { /* ... */ return user }
    override suspend fun delete(id: Long): Boolean { /* ... */ return true }
}
```

### Сборка: выбор реализации в одном месте

```kotlin
// Production: PostgreSQL + SMTP
val productionUseCase = UserRegistrationUseCase(
    userRepo = PostgresUserRepository(dataSource),
    emailService = SmtpEmailService(smtpConfig),
    logger = Slf4jLogger(UserRegistrationUseCase::class)
)

// Тесты: In-Memory + Fake
val testUseCase = UserRegistrationUseCase(
    userRepo = InMemoryUserRepository(),
    emailService = FakeEmailService(),           // Не отправляет реальные письма
    logger = NoOpLogger()                        // Без логирования в тестах
)

// Мобильное приложение: Firebase + FCM
val mobileUseCase = UserRegistrationUseCase(
    userRepo = FirebaseUserRepository(firestore),
    emailService = FcmNotificationService(),
    logger = AndroidLogger("Registration")
)
```

### Kotlin: delegation `by` как DIP-паттерн

```kotlin
// Delegation by — DIP + Decorator в одном

interface Analytics {
    fun track(event: String, params: Map<String, Any>)
    fun setUser(userId: String)
}

class FirebaseAnalytics : Analytics {
    override fun track(event: String, params: Map<String, Any>) {
        println("Firebase: $event $params")
    }
    override fun setUser(userId: String) {
        println("Firebase user: $userId")
    }
}

// Декоратор через delegation: добавляем логирование без изменения Firebase
class DebugAnalytics(
    private val delegate: Analytics
) : Analytics by delegate {
    override fun track(event: String, params: Map<String, Any>) {
        println("DEBUG: Tracking '$event' with $params")
        delegate.track(event, params)
    }
    // setUser() автоматически делегируется
}

// Мультипровайдер: отправка аналитики в несколько систем
class CompositeAnalytics(
    private val providers: List<Analytics>
) : Analytics {
    override fun track(event: String, params: Map<String, Any>) {
        providers.forEach { it.track(event, params) }
    }
    override fun setUser(userId: String) {
        providers.forEach { it.setUser(userId) }
    }
}

// Использование: бизнес-код не знает о Firebase, Amplitude, etc.
val analytics: Analytics = CompositeAnalytics(
    listOf(
        DebugAnalytics(FirebaseAnalytics()),
        AmplitudeAnalytics(),
        MixpanelAnalytics()
    )
)
```

> [!info] Kotlin-нюанс: `val` constructor params и DIP
> В Kotlin зависимости объявляются как `val`-параметры конструктора: `class UseCase(private val repo: Repository)`. Это одновременно: (1) объявление зависимости, (2) проверка наличия в compile-time, (3) immutable reference (нельзя подменить после создания). В Java для этого нужны 3 отдельных шага: поле, конструктор, аннотация `@Inject`.

### Когда НЕ применять DIP

| Ситуация | Почему DIP вредит |
|----------|-------------------|
| Единственная реализация навсегда | Интерфейс для `JsonParser` когда других парсеров не будет — мёртвый код |
| Стабильные зависимости | `String`, `List`, `Math.random()` — не нужно абстрагировать |
| Маленький скрипт | Overhead абстракций превышает пользу |
| Интерфейс ради моков | Если можно тестировать без моков — не нужен интерфейс |

---

## SOLID как система: как принципы работают вместе

```
┌─────────────────────────────────────────────────────┐
│                Бизнес-требование                    │
│         "Добавить новый тип уведомлений"            │
└──────────────────────┬──────────────────────────────┘
                       │
         ┌─────────────┼─────────────────┐
         ▼             ▼                 ▼
   ┌─────────┐   ┌──────────┐   ┌────────────┐
   │   SRP   │   │   OCP    │   │    DIP     │
   │         │   │          │   │            │
   │ Новый   │   │ Старый   │   │ Зависим   │
   │ класс   │   │ код не   │   │ от интер- │
   │ для     │   │ меняется │   │ фейса     │
   │ одной   │   │          │   │ Notifier  │
   │ задачи  │   │          │   │            │
   └────┬────┘   └────┬─────┘   └─────┬──────┘
        │             │               │
        └──────┬──────┘               │
               ▼                      │
         ┌──────────┐                 │
         │   ISP    │                 │
         │          │─────────────────┘
         │ Только   │
         │ нужные   │
         │ методы   │
         └────┬─────┘
              │
              ▼
        ┌──────────┐
        │   LSP    │
        │          │
        │ Подтип   │
        │ работает │
        │ как      │
        │ базовый  │
        └──────────┘
```

### Пример: все пять принципов в одном контексте

```kotlin
// Контекст: система уведомлений в приложении

// --- ISP: маленькие интерфейсы по ролям ---
interface MessageSender {
    suspend fun send(to: String, content: String): Boolean
}

interface MessageFormatter {
    fun format(template: String, params: Map<String, String>): String
}

interface DeliveryTracker {
    fun trackDelivery(messageId: String): DeliveryStatus
}

// --- SRP: каждый класс — одна ответственность ---

// Только отправка email
class SmtpSender(private val config: SmtpConfig) : MessageSender {
    override suspend fun send(to: String, content: String): Boolean {
        // SMTP-логика
        return true
    }
}

// Только форматирование
class HtmlFormatter : MessageFormatter {
    override fun format(template: String, params: Map<String, String>): String {
        var result = template
        params.forEach { (key, value) -> result = result.replace("{{$key}}", value) }
        return "<html><body>$result</body></html>"
    }
}

// --- DIP: high-level зависит от абстракций ---
class NotificationUseCase(
    private val sender: MessageSender,       // Абстракция
    private val formatter: MessageFormatter  // Абстракция
) {
    suspend fun notify(
        recipient: String,
        template: String,
        params: Map<String, String>
    ): Boolean {
        val content = formatter.format(template, params)
        return sender.send(recipient, content)
    }
}

// --- OCP: новый канал = новый класс, старый код не меняется ---
class TelegramSender(private val botToken: String) : MessageSender {
    override suspend fun send(to: String, content: String): Boolean {
        // Telegram Bot API
        return true
    }
}

class MarkdownFormatter : MessageFormatter {
    override fun format(template: String, params: Map<String, String>): String {
        var result = template
        params.forEach { (key, value) -> result = result.replace("{{$key}}", "**$value**") }
        return result
    }
}

// --- LSP: любая реализация MessageSender безопасно подставляется ---
// NotificationUseCase работает одинаково с SmtpSender и TelegramSender

// Сборка: production
val emailNotifier = NotificationUseCase(
    sender = SmtpSender(smtpConfig),
    formatter = HtmlFormatter()
)

// Сборка: Telegram
val telegramNotifier = NotificationUseCase(
    sender = TelegramSender(botToken),
    formatter = MarkdownFormatter()
)
```

---

## Когда НЕ применять SOLID: overengineering

### Эвристика: когда SOLID оправдан

| Условие | SOLID? | Почему |
|---------|--------|--------|
| Проект > 6 месяцев | Да | Код будут читать и менять другие люди |
| Команда > 3 человек | Да | Разные акторы = разные причины изменений |
| Код меняется часто | Да | Инвестиция в гибкость окупится |
| MVP / хакатон | Нет | Скорость важнее архитектуры |
| Solo-проект / скрипт | По ситуации | Зависит от сложности и срока жизни |
| Код написан раз и забыт | Нет | Нет будущих изменений = нет пользы от SOLID |

### Антипаттерн: explosion of classes

```kotlin
// OVERENGINEERING: 5 классов для сложения двух чисел

interface MathOperation {
    fun execute(a: Int, b: Int): Int
}

class AdditionStrategy : MathOperation {
    override fun execute(a: Int, b: Int) = a + b
}

class CalculatorFactory {
    fun create(operation: String): MathOperation = when (operation) {
        "add" -> AdditionStrategy()
        else -> throw IllegalArgumentException()
    }
}

class Calculator(private val factory: CalculatorFactory) {
    fun calculate(operation: String, a: Int, b: Int): Int {
        return factory.create(operation).execute(a, b)
    }
}

// Использование (смотрите, какой overhead для a + b):
val result = Calculator(CalculatorFactory()).calculate("add", 2, 3)

// ПРОСТО:
fun add(a: Int, b: Int): Int = a + b
val result = add(2, 3)
```

### Мифы о SOLID

| Миф | Реальность |
|-----|-----------|
| "SOLID = всегда извлекать интерфейс" | Интерфейс нужен при >1 реализации или для тестирования |
| "SRP = один метод на класс" | SRP = один актор (стейкхолдер) на класс |
| "OCP = никогда не менять код" | OCP = минимизировать изменения в протестированном коде |
| "LSP — про синтаксис типов" | LSP — про **поведение** (behavioral subtyping) |
| "ISP = интерфейс по 1 методу" | ISP = интерфейсы по **ролям клиентов** |
| "DIP = всегда Dependency Injection" | DIP — принцип, DI — механизм. DIP можно без DI-контейнера |
| "SOLID применять всегда" | SOLID — эвристики для ~80% случаев, не догма |

### Google подход: "Rule of Three"

> *"Не создавай абстракцию, пока не увидишь три конкретных использования."*

1. Первый раз — пишем конкретный код
2. Второй раз — замечаем дублирование, но терпим
3. Третий раз — рефакторим, создаём абстракцию

Это предотвращает преждевременную абстракцию — самый частый источник overengineering.

---

## Реальные компании и SOLID

| Компания | Принцип | Применение | Результат |
|----------|---------|------------|-----------|
| **Netflix** | OCP + DIP | Стратегия загрузки контента через интерфейсы | Легко добавлять новые CDN без изменения core |
| **Uber** | SRP | Разделение ride-matching, pricing, payment | Независимые деплои, масштабирование |
| **Google** | ISP | Маленькие API в Android SDK | Меньше ненужных зависимостей в приложениях |
| **Square** | LSP | `sealed class` для Result types в Cash App | Type-safe обработка ошибок без сюрпризов |
| **JetBrains** | DIP + delegation | Plugin system в IntelliJ через интерфейсы | 5000+ плагинов без изменения ядра |

---

## CS-фундамент

| CS-концепция | Связь с SOLID |
|--------------|---------------|
| **Cohesion / Coupling** | SRP повышает cohesion (связность), ISP + DIP снижают coupling (зацепление) |
| **Behavioral Subtyping** | LSP = формальное определение правильного наследования (Liskov & Wing, 1994) |
| **Design by Contract** | LSP через preconditions, postconditions, invariants |
| **Algebraic Data Types** | Sealed class реализует sum types, гарантируя LSP через exhaustive matching |
| **Dependency Graph** | DIP инвертирует направление стрелок зависимостей в графе модулей |
| **Information Hiding** | ISP + инкапсуляция: клиент видит минимальный необходимый интерфейс |

---

## Проверь себя

> [!question]- Почему слепое следование "одна вещь на класс" может навредить проекту?
> SRP говорит не "одна вещь", а "одна причина для изменения" = один актор (стейкхолдер). Интерпретация "одна вещь" ведёт к explosion of classes: проект из 10 классов превращается в 100 микроклассов по 5 строк. Совокупная сложность (навигация, связи, именование) превышает сложность исходного кода. Правильный вопрос: "Сколько разных людей/команд попросят изменить этот класс?"

> [!question]- Как `sealed class` помогает соблюдать LSP, и чем это лучше обычного наследования?
> `sealed class` создаёт **закрытую** иерархию: все подтипы известны compile-time. Exhaustive `when` проверяет обработку всех вариантов. Каждый подтип обрабатывается **явно** в своей ветке — нет риска, что подтип нарушит postcondition базового типа. В отличие от открытого наследования, где подтип может появиться в другом модуле и сломать код, ожидающий базовый тип.

> [!question]- Чем DIP (принцип) отличается от DI (механизм)? Когда DIP не нужен?
> DIP — архитектурный принцип: high-level модули зависят от абстракций, а не конкретных реализаций. DI — техническая реализация: передача зависимостей через конструктор, фабрику, контейнер. DIP можно соблюдать без DI-контейнера. DIP не нужен, когда реализация единственная навсегда (`Math.random()`, `String`), или когда интерфейс создаётся только ради моков — можно тестировать без моков.

> [!question]- Вы делаете MVP за неделю. Какие принципы SOLID применить, а какие отложить?
> Применить: SRP на уровне функций (чтобы код читался) и DIP для внешних зависимостей (API, БД — чтобы упростить тестирование и смену провайдеров). Отложить: OCP (не нужны extension points для MVP), ISP (один интерфейс пока достаточно), строгий LSP (пока иерархий мало). Причина: MVP проверяет гипотезу, а не архитектуру. Если гипотеза провалится, идеальная архитектура не спасёт. Ключ: осознанный долг с планом рефакторинга.

> [!question]- Приведите пример, когда extension function в Kotlin реализует OCP лучше, чем наследование.
> Extension function добавляет поведение к существующему классу **без его модификации**: `fun Order.totalPrice(): Double = items.sumOf { it.price * it.quantity }`. Класс `Order` закрыт (final), но открыт для расширения через extension. В Java для этого нужен `OrderUtils.calculateTotal(order)` — менее читаемо и не discovery-friendly. Extension functions — compile-time dispatch, zero overhead.

---

## Ключевые карточки

Что такое SRP в точной формулировке Мартина и чем это отличается от "одна вещь на класс"?
?
SRP: "Класс должен иметь одну и только одну причину для изменения." Причина = актор (стейкхолдер), чьи бизнес-требования вызывают изменение. "Одна вещь" — неточная интерпретация, ведущая к explosion of classes. Правильный вопрос: "Кто попросит изменить этот класс?"

Чем отличается OCP Мейера (1988) от OCP Мартина (1996)?
?
Meyer: расширение через наследование реализации (tight coupling). Martin: расширение через абстракции и полиморфизм (интерфейсы). Современный подход Martin предпочтительнее. Kotlin поддерживает его: классы final by default, extension functions для расширения без модификации.

Что проверяет LSP — синтаксис или семантику?
?
Семантику (поведение). Компилятор проверяет синтаксическую совместимость типов, но LSP требует behavioral subtyping: подтип не должен нарушать preconditions (может ослабить), postconditions (может усилить) и invariants (не может нарушать) базового типа. Пример нарушения: Square.setWidth() меняет height.

Почему ISP о связях между клиентами, а не о размере интерфейса?
?
Fat interface создаёт inadvertent coupling: изменение метода для одного клиента вынуждает перекомпилировать другой клиент, который этот метод не использует. Правильное дробление — по ролям клиентов. Пример: Xerox Job class — изменение метода степлера перекомпилировало модуль принтера.

В чём разница DIP (принцип) и DI (механизм)?
?
DIP — архитектурный принцип: зависимости от абстракций, не реализаций. DI — техническая реализация: конструктор, фабрика, контейнер (Dagger/Koin/Hilt). DIP можно соблюдать без DI-контейнера. Kotlin: `class UseCase(private val repo: Repository)` — DIP через val-параметр конструктора.

Когда SOLID вредит проекту?
?
MVP/хакатон (скорость > архитектура), solo-проект (один актор), скрипт на 50 строк (overhead > пользы), единственная реализация навсегда (мёртвый интерфейс). Антипаттерн: explosion of classes — 5 классов для a + b. Правило: "Rule of Three" — абстракция после 3 конкретных использований.

Как extension functions в Kotlin реализуют OCP?
?
Extension function добавляет поведение к существующему классу без модификации: `fun Order.totalPrice()`. Класс остаётся final (закрыт), но расширяемый (открыт). Compile-time dispatch, zero overhead. В Java — utility class с static-методами (менее читаемо, нет auto-complete).

Как Kotlin поддерживает SOLID на уровне языка?
?
SRP: data class — чистый контейнер данных. OCP: final by default + extension functions. LSP: sealed class + exhaustive when. ISP: interfaces с default implementations + delegation by. DIP: val constructor params + delegation by. Каждый принцип имеет языковую поддержку.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Фундамент | [[oop-fundamentals]] | Четыре столпа ООП — основа для понимания SOLID |
| Углубление | [[coupling-cohesion]] | Cohesion и coupling — метрики, которые SOLID оптимизирует |
| Связь | [[design-patterns-overview]] | Паттерны GoF — конкретные реализации принципов SOLID |
| Связь | [[kotlin-oop]] | Kotlin OOP: data class, sealed class, delegation — инструменты SOLID |
| Практика | [[kotlin-best-practices]] | Идиоматичный Kotlin: как применять SOLID без overengineering |
| Связь | [[clean-code]] | Clean Code — дополнение к SOLID на уровне функций и именования |
| Android | [[android-architecture-patterns]] | SOLID как фундамент архитектурных решений Android |
| Android | [[android-clean-architecture]] | Clean Architecture построена на DIP и SRP |
| Навигация | [[programming-overview]] | Вернуться к карте раздела Programming |

---

## Источники

### Первоисточники

- Martin R.C. (2000). *Design Principles and Design Patterns*. — [Оригинальная статья](http://principles-wiki.net/collections:robert_c._martin_s_principle_collection), где SRP, OCP, LSP, ISP, DIP собраны вместе.
- Martin R.C. (2003). *Agile Software Development, Principles, Patterns, and Practices*. Prentice Hall. — Полное объяснение SOLID с примерами.
- Martin R.C. (2017). *Clean Architecture*. Prentice Hall. — SOLID на уровне компонентов и систем.
- Martin R.C. (2014). [The Single Responsibility Principle](https://blog.cleancoder.com/uncle-bob/2014/05/08/SingleReponsibilityPrinciple.html) — уточнение: "reason to change = actors".
- Martin R.C. (2014). [The Open Closed Principle](https://blog.cleancoder.com/uncle-bob/2014/05/12/TheOpenClosedPrinciple.html) — переосмысление OCP Мейера.
- Meyer B. (1988). *Object-Oriented Software Construction*. Prentice Hall. — Оригинальная формулировка OCP.
- Liskov B. (1987). *Data abstraction and hierarchy*. OOPSLA. — Оригинальная формулировка LSP.
- Liskov B., Wing J. (1994). *A behavioral notion of subtyping*. ACM TOPLAS. — Формализация LSP.

### Kotlin и SOLID

- Jemerov D., Isakova S. (2017). *Kotlin in Action*. Manning. — Классы, интерфейсы, sealed classes, delegation.
- Moskala M. (2021). *Effective Kotlin*. Kt. Academy. — Практические рекомендации по SOLID в Kotlin.
- Bloch J. (2018). *Effective Java*, 3rd ed. Addison-Wesley. — Items 17-19: наследование, интерфейсы, минимизация мутабельности.
- [Baeldung: SOLID Principles with Kotlin](https://www.baeldung.com/kotlin/solid-principles) — примеры каждого принципа на Kotlin.
- [Carrion.dev: SOLID with Kotlin Examples](https://carrion.dev/en/posts/solid-kotlin/) — практические примеры.
- [ProAndroidDev: Top 3 Android Use Cases for Every SOLID Principle](https://proandroiddev.com/top-3-android-use-cases-for-every-solid-principle-with-code-960eedcdbc3f) — SOLID в Android-разработке.

### Критика и альтернативные взгляды

- [SOLID as an antipattern](https://blog.spinthemoose.com/2012/12/17/solid-as-an-antipattern/) — когда SOLID вредит.
- [The Misunderstood SRP](https://www.softwareonthebrain.com/2022/01/the-misunderstood-single-responsibility.html) — разбор заблуждений о SRP.
- [DIP is a Tradeoff](https://naildrivin5.com/blog/2019/12/02/dependency-inversion-principle-is-a-tradeoff.html) — критика слепого применения DIP.
- [Should We Follow OCP?](https://thevaluable.dev/open-closed-principle-revisited/) — переосмысление OCP в современном контексте.
- [Stack Overflow Blog: Why SOLID Still Matters](https://stackoverflow.blog/2021/11/01/why-solid-principles-are-still-the-foundation-for-modern-software-architecture/) — защита SOLID в 2021.

---

*Проверено: 2026-02-19 | Источники: Clean Architecture, Effective Kotlin, Kotlin docs, Baeldung*