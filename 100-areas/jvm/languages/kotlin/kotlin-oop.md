---
title: "Kotlin: Объектно-ориентированное программирование"
created: 2025-11-25
modified: 2026-01-03
tags:
  - kotlin
  - oop
  - classes
aliases:
  - Kotlin OOP
  - Kotlin Classes
---

# Kotlin ООП: классы без boilerplate

> **TL;DR:** Data class заменяет 50 строк Java POJO: `data class User(val name: String)` — equals, hashCode, toString, copy автоматически. Sealed class — закрытая иерархия, when проверяет все варианты в compile-time. Value class — type-safe обёртка без runtime overhead. Delegation `by` вместо наследования: `class Printer(writer: Writer) : Writer by writer`.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin basics | Синтаксис, типы, null-safety | [[kotlin-basics]] |
| ООП концепции | Классы, наследование, интерфейсы | Любой ООП курс |
| Java ООП (опционально) | Сравнить с Kotlin подходом | Java docs |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Data class** | Класс для данных с автогенерацией методов | Готовая форма документа — заполнил поля и готово |
| **Sealed class** | Закрытая иерархия с известными наследниками | Меню в ресторане — только фиксированные блюда |
| **Value class** | Type-safe обёртка без runtime overhead | Именной бейдж — не путаем кого как зовут |
| **Companion object** | Статические методы и свойства класса | Секретарь, который отвечает за весь офис |
| **Primary constructor** | Конструктор в заголовке класса | Главный вход в здание |
| **Property** | Поле + getter/setter | Умный замок — контролирует доступ к комнате |
| **Backing field** | Внутреннее поле свойства | Настоящий ключ, спрятанный внутри замка |
| **Delegation `by`** | Делегирование реализации другому объекту | Субподрядчик — делает работу за вас |

---

В Java стандартный POJO с equals, hashCode, toString, getters/setters занимает 50-100 строк. В Kotlin: `data class User(val name: String, val age: Int)` — одна строка, всё генерируется автоматически.

Data class решает проблему boilerplate: equals сравнивает по полям, copy создаёт изменённую копию (immutability), destructuring (`val (name, age) = user`) упрощает работу с данными. Sealed class — закрытая иерархия, где компилятор проверяет обработку всех вариантов в when-выражении: добавили новый подкласс — код не скомпилируется пока не добавите обработку. Value class — type-safe обёртка примитивов (`UserId`, `Email`) без runtime overhead: компилируется в обычный Long или String, но защищает от перепутывания параметров.

---

## 1. Классы: Основы

### Простейший класс

```kotlin
// Primary constructor прямо в объявлении
class User(val name: String, val age: Int)

// Использование
val user = User("John", 30)
println(user.name)  // John
println(user.age)   // 30

// Эквивалент в Java:
// public class User {
//     private final String name;
//     private final int age;
//     public User(String name, int age) { ... }
//     public String getName() { ... }
//     public int getAge() { ... }
// }
```

### Constructor: Primary и Secondary

```kotlin
// Primary constructor
class Person(val name: String, val age: Int) {

    // Init block — код инициализации
    init {
        require(age >= 0) { "Age must be non-negative" }
        println("Person created: $name")
    }

    // Secondary constructor (делегирует в primary)
    constructor(name: String) : this(name, 18) {
        println("Using default age")
    }
}

// Использование
val person1 = Person("Alice", 25)  // Primary
val person2 = Person("Bob")        // Secondary
```

### Properties

```kotlin
class Rectangle(
    val width: Int,   // val — только getter
    var height: Int   // var — getter + setter
) {
    // Computed property
    val area: Int
        get() = width * height

    // Computed property с backing field
    var perimeter: Int = 0
        get() = 2 * (width + height)
        private set  // Setter private

    // Custom getter/setter
    var name: String = ""
        get() = field.uppercase()  // field — backing field
        set(value) {
            field = value.trim()
        }

    // Late-initialized property
    lateinit var description: String

    // Lazy property
    val expensiveValue: String by lazy {
        println("Computing...")
        "Expensive result"
    }
}
```

**Backing field (`field`):**
- Автоматически создается если используется в getter/setter
- Прямой доступ только из accessor'ов

---

## 2. Data Classes

### Автогенерация методов

```kotlin
// Data class — автоматически генерирует:
// - equals() / hashCode()
// - toString()
// - copy()
// - componentN() для destructuring
data class User(
    val id: Long,
    val name: String,
    val email: String
)

val user1 = User(1, "Alice", "alice@example.com")
val user2 = User(1, "Alice", "alice@example.com")

// equals() работает на основе свойств
println(user1 == user2)  // true

// toString()
println(user1)  // User(id=1, name=Alice, email=alice@example.com)

// copy() — immutable updates
val user3 = user1.copy(email = "newemail@example.com")

// Destructuring
val (id, name, email) = user1
println("ID: $id, Name: $name")
```

### copy() — immutable updates

```kotlin
data class Person(val name: String, val age: Int, val city: String)

val person = Person("John", 30, "NYC")

// Изменяем только одно поле
val olderPerson = person.copy(age = 31)

// Изменяем несколько
val movedPerson = person.copy(city = "LA", age = 31)

// Оригинал не изменился
println(person)      // Person(name=John, age=30, city=NYC)
println(olderPerson) // Person(name=John, age=31, city=NYC)
```

**Почему это важно:**
- Immutability — безопасность в многопоточности
- Функциональный стиль программирования
- Легко работать с Collections

### Destructuring declarations

```kotlin
data class Result(val success: Boolean, val data: String, val error: String?)

fun processData(): Result {
    return Result(true, "Data", null)
}

// Destructuring
val (success, data, error) = processData()
if (success) {
    println(data)
}

// Можно пропускать компоненты с _
val (_, data2, _) = processData()

// С коллекциями
val (first, second) = listOf(1, 2, 3)  // first=1, second=2
```

### Ограничения data classes

```kotlin
// ❌ Нельзя:
// - Наследоваться от других классов (кроме интерфейсов)
// - open, abstract, sealed, inner

// ✅ Можно:
data class User(val name: String) {
    var age: Int = 0  // Дополнительные свойства (не в constructor)

    init {
        // Init blocks
    }

    fun greet() = "Hello, $name"  // Методы
}

// Реализация интерфейсов
interface Named {
    val name: String
}

data class Person(override val name: String, val age: Int) : Named
```

---

## 3. Sealed Classes

### Закрытые иерархии

```kotlin
// Sealed class — все наследники известны на этапе компиляции
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String, val code: Int) : Result()
    data object Loading : Result()  // Data object для singleton
}

// Exhaustive when — компилятор проверяет полноту
fun handle(result: Result): String = when (result) {
    is Result.Success -> "Data: ${result.data}"
    is Result.Error -> "Error ${result.code}: ${result.message}"
    Result.Loading -> "Loading..."
    // else не нужен! Компилятор знает все варианты
}
```

**Почему sealed classes:**
- Exhaustiveness checking в `when`
- Type-safe alternative для enums
- Идеально для state machines

### Sealed classes vs Enums

```kotlin
// Enum — ограниченный набор, одинаковые поля
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF)
}

// Sealed — разные типы для разных случаев
sealed class NetworkResult {
    data class Success(val data: ByteArray, val headers: Map<String, String>) : NetworkResult()
    data class Error(val code: Int, val message: String, val exception: Throwable?) : NetworkResult()
    data object NotConnected : NetworkResult()
}
```

### Sealed interfaces (Kotlin 1.5+)

```kotlin
sealed interface UiState

data class Loading(val progress: Int) : UiState
data class Content(val items: List<String>) : UiState
data class Error(val message: String) : UiState

// Можно реализовывать несколько sealed interfaces
sealed interface Action
sealed interface Undoable

data class DeleteAction(val id: String) : Action, Undoable
```

---

## 4. Value Classes (Inline Classes)

### Zero-overhead обертки

```kotlin
// Value class — обертка без runtime overhead
@JvmInline
value class UserId(val value: Long)

@JvmInline
value class Email(val value: String) {
    init {
        require(value.contains("@")) { "Invalid email" }
    }
}

// Type-safety
fun getUser(userId: UserId): User { ... }
fun sendEmail(email: Email) { ... }

val userId = UserId(123)
val email = Email("user@example.com")

getUser(userId)        // ✅ OK
// getUser(123)        // ❌ Type mismatch
sendEmail(email)       // ✅ OK
// sendEmail("text")   // ❌ Type mismatch
```

**Компиляция:**
```kotlin
// Kotlin
fun process(id: UserId) { ... }

// Скомпилируется в (эквивалентно):
// fun process(id: Long) { ... }
```

**Зачем:**
- Type-safety без performance cost
- Защита от перепутывания примитивов
- Self-documenting code

### Ограничения

```kotlin
// Value class должен иметь:
// - Ровно одно свойство в primary constructor
// - Быть final (не open)

// ✅ OK
@JvmInline
value class Password(val value: String)

// ❌ Нельзя
// @JvmInline
// value class Person(val name: String, val age: Int)  // Больше 1 свойства
```

---

## 5. Object Declarations

### Singleton

```kotlin
// Object — singleton из коробки
object Database {
    private val connections = mutableListOf<Connection>()

    fun connect() {
        connections.add(Connection())
    }

    fun disconnect() {
        connections.clear()
    }
}

// Использование
Database.connect()
Database.disconnect()
```

**Ленивая инициализация:**
Object создается при первом обращении (thread-safe).

### Object expressions (анонимные классы)

```kotlin
// Эквивалент anonymous class в Java
val clickListener = object : View.OnClickListener {
    override fun onClick(v: View) {
        println("Clicked!")
    }
}

// С доступом к внешним переменным
fun setupButton(button: Button, counter: Int) {
    button.setOnClickListener(object : View.OnClickListener {
        override fun onClick(v: View) {
            println("Clicked $counter times")
        }
    })
}

// SAM conversion для Java интерфейсов (короче)
button.setOnClickListener { v ->
    println("Clicked!")
}
```

---

## 6. Companion Objects

### Замена static

```kotlin
class MyClass {
    // Companion object — аналог static в Java
    companion object {
        const val MAX_COUNT = 100  // compile-time constant

        fun create(): MyClass {
            return MyClass()
        }

        @JvmStatic  // Для Java interop
        fun staticMethod() {
            println("Static method")
        }
    }
}

// Использование
MyClass.create()
MyClass.MAX_COUNT
MyClass.staticMethod()
```

### Factory methods

```kotlin
class User private constructor(val name: String, val email: String) {

    companion object {
        fun fromEmail(email: String): User {
            val name = email.substringBefore("@")
            return User(name, email)
        }

        fun guest(): User {
            return User("Guest", "guest@example.com")
        }
    }
}

// Использование
val user1 = User.fromEmail("alice@example.com")
val user2 = User.guest()
```

### Именованные companion objects

```kotlin
class MyClass {
    companion object Factory {
        fun create() = MyClass()
    }
}

// Можно использовать с именем или без
MyClass.create()
MyClass.Factory.create()
```

---

## 7. Наследование

### open классы

```kotlin
// По умолчанию классы final! Нужно open для наследования
open class Animal(val name: String) {
    open fun makeSound() {
        println("Some sound")
    }

    // final методы нельзя override
    fun sleep() {
        println("Zzz...")
    }
}

class Dog(name: String) : Animal(name) {
    override fun makeSound() {
        println("Woof!")
    }

    // Нельзя override sleep() — он final
}

// Использование
val dog = Dog("Rex")
dog.makeSound()  // Woof!
dog.sleep()      // Zzz...
```

**Почему final by default:**
- Explicit is better than implicit
- Fragile base class problem
- Consistent with Effective Java

### Abstract классы

```kotlin
abstract class Shape {
    abstract val area: Double
    abstract fun draw()

    // Конкретные методы можно
    fun describe() {
        println("Shape with area $area")
    }
}

class Circle(val radius: Double) : Shape() {
    override val area: Double
        get() = Math.PI * radius * radius

    override fun draw() {
        println("Drawing circle")
    }
}
```

### Интерфейсы

```kotlin
interface Clickable {
    fun click()  // Abstract по умолчанию

    // Методы с реализацией (default methods)
    fun showOff() {
        println("I'm clickable!")
    }
}

interface Focusable {
    fun focus()

    fun showOff() {
        println("I'm focusable!")
    }
}

// Реализация нескольких интерфейсов
class Button : Clickable, Focusable {
    override fun click() {
        println("Button clicked")
    }

    override fun focus() {
        println("Button focused")
    }

    // Конфликт — нужно явно выбрать
    override fun showOff() {
        super<Clickable>.showOff()
        super<Focusable>.showOff()
    }
}
```

### Visibility modifiers

```kotlin
// Классы
public class Public         // Везде (default)
internal class Internal     // В модуле
private class Private       // В файле

// Члены класса
class MyClass {
    public val a = 1        // Везде (default)
    internal val b = 2      // В модуле
    protected val c = 3     // В подклассах
    private val d = 4       // Только в классе
}
```

---

## 8. Nested и Inner классы

### Nested class (static by default)

```kotlin
class Outer {
    private val bar = 1

    // Nested class — статический контекст
    class Nested {
        fun foo() = 2
        // Нет доступа к bar
    }
}

val nested = Outer.Nested()
println(nested.foo())  // 2
```

### Inner class

```kotlin
class Outer {
    private val bar = 1

    // Inner class — доступ к outer instance
    inner class Inner {
        fun foo() = bar  // ✅ Доступ к bar

        fun getOuter() = this@Outer  // Ссылка на outer
    }
}

val outer = Outer()
val inner = outer.Inner()
println(inner.foo())  // 1
```

**Kotlin vs Java:**
```java
// Java
class Outer {
    class Nested {}      // Non-static (inner)
    static class Static {}  // Static
}

// Kotlin
class Outer {
    class Nested {}      // Static by default
    inner class Inner {} // Non-static
}
```

---

## 9. Enum Classes

```kotlin
enum class Direction {
    NORTH, SOUTH, EAST, WEST
}

// С параметрами
enum class Color(val rgb: Int) {
    RED(0xFF0000),
    GREEN(0x00FF00),
    BLUE(0x0000FF);  // ; обязательна если есть методы

    fun toHex() = "#${rgb.toString(16).padStart(6, '0')}"
}

// С методами и свойствами
enum class ProtocolState {
    WAITING {
        override fun signal() = TALKING
    },
    TALKING {
        override fun signal() = WAITING
    };

    abstract fun signal(): ProtocolState
}

// Использование
val direction = Direction.NORTH
val color = Color.RED
println(color.toHex())  // #ff0000

// Все enum имеют
color.name        // "RED"
color.ordinal     // 0
Direction.values()         // Array<Direction>
Direction.valueOf("NORTH") // Direction.NORTH
```

---

## 10. Type Aliases

```kotlin
// Упрощение сложных типов
typealias UserMap = Map<String, User>
typealias Handler = (String, Int) -> Unit
typealias Predicate<T> = (T) -> Boolean

// Использование
val users: UserMap = mapOf()
val handler: Handler = { msg, code -> println("$msg: $code") }
val isEven: Predicate<Int> = { it % 2 == 0 }

// Для nested classes
class A {
    inner class Inner
}

class B {
    inner class Inner
}

typealias AInner = A.Inner
typealias BInner = B.Inner
```

---

## Сравнение с Java

| Фича | Kotlin | Java |
|------|--------|------|
| Data class | 1 строка | Lombok или Records (Java 16+) |
| Sealed class | Native | Sealed classes (Java 17+) |
| Singleton | `object` | Manual implementation |
| Static | `companion object` | `static` |
| Inline classes | `@JvmInline value class` | Нет (Project Valhalla future) |
| Properties | Автоматически | Manual getter/setter |
| Final by default | Да | Нет |
| Primary constructor | В объявлении | Отдельный constructor |

---

## Чеклист

- [ ] Используй data classes для DTO/models
- [ ] Используй sealed classes для состояний и результатов
- [ ] Избегай inheritance где возможно (composition over inheritance)
- [ ] Используй value classes для type-safe primitives
- [ ] Предпочитай `val` вместо `var` в data classes
- [ ] Используй companion object для factory methods
- [ ] Делай классы final (не open) unless inheritance required
- [ ] Используй `object` для singleton
- [ ] Применяй destructuring с data classes
- [ ] Используй sealed classes вместо enum если нужны разные поля

---

## Куда дальше

**Если здесь впервые:**
→ [[kotlin-basics]] — синтаксис и базовые типы. Без этого примеры непонятны.

**Углубление:**
→ [[kotlin-advanced-features]] — extensions, delegates, inline functions. Следующий уровень после ООП.
→ [[kotlin-type-system]] — generics, variance, reified. Продвинутая работа с типами.

**Практическое применение:**
→ [[design-patterns]] — как паттерны GoF реализуются в Kotlin (часто проще чем в Java).
→ [[clean-code-solid]] — SOLID принципы и как Kotlin помогает им следовать.

---

## Кто использует и реальные примеры

| Компания | Паттерны OOP в Kotlin | Результаты |
|----------|----------------------|------------|
| **Google** | Sealed classes для UI state в Compose | Exhaustive when, type-safe states |
| **Netflix** | Data classes для API models | JSON serialization из коробки |
| **Square** | Value classes для типов (UserId, Amount) | Type-safe API без runtime overhead |
| **JetBrains** | Delegation patterns в IDE | Composition over inheritance |
| **Uber** | Sealed classes для Result types | Единообразная обработка ошибок |

### Паттерны в production

```
Паттерн 1: Sealed class для UI State
────────────────────────────────────
sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}

// Exhaustive when:
when (state) {
    is UiState.Loading -> showSpinner()
    is UiState.Success -> showData(state.data)
    is UiState.Error -> showError(state.message)
    // Компилятор проверит все варианты!
}

Паттерн 2: Value class для type-safety
──────────────────────────────────────
@JvmInline
value class UserId(val value: Long)

@JvmInline
value class OrderId(val value: Long)

fun getUser(id: UserId): User  // Нельзя случайно передать OrderId!
fun getOrder(id: OrderId): Order

// В runtime: обычный Long, без boxing

Паттерн 3: Delegation вместо наследования
────────────────────────────────────────
interface Printer { fun print(message: String) }

class ConsolePrinter : Printer {
    override fun print(message: String) = println(message)
}

class TimestampPrinter(
    private val printer: Printer
) : Printer by printer {
    override fun print(message: String) {
        printer.print("[${System.currentTimeMillis()}] $message")
    }
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Kotlin классы open по умолчанию" | Классы final по умолчанию. Нужно явно указать `open` для наследования. Это by design — composition over inheritance |
| "data class автоматически immutable" | data class генерирует методы, но не запрещает var. Для immutability используйте val properties |
| "companion object = static" | Companion — реальный объект в runtime. @JvmStatic нужен для true static в bytecode. Companion можно наследовать |
| "sealed class = enum с данными" | Sealed classes — это controlled inheritance. Подклассы могут иметь разные поля и логику. Enum — фиксированные значения |
| "value class = typedef" | value class создаёт новый тип с compile-time проверкой. typedef просто alias. Value class может иметь методы |
| "object = singleton" | object — lazy singleton (инициализируется при первом доступе). Thread-safe initialization гарантирована JVM |
| "init блок = конструктор" | init — часть primary constructor. Выполняется после property initialization. Secondary constructors вызывают primary |
| "delegation медленнее наследования" | `by` компилируется в прямые вызовы делегата. После JIT inlining — идентичная производительность |
| "abstract class устарел" | Abstract class нужен когда требуется state или non-abstract методы. Interface с default методами — альтернатива для stateless |
| "equals/hashCode автоматически корректны в data class" | Автогенерация учитывает только primary constructor properties. Свойства в body класса игнорируются |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin OOP |
|--------------|------------------------|
| **Algebraic Data Types** | sealed class = Sum type (A | B | C). data class = Product type (A × B × C). Основа type-safe modeling |
| **Value Types** | value class реализует value semantics — identity через содержимое, не ссылку. Inline в runtime |
| **Composition over Inheritance** | Classes final by default. Delegation (`by`) как first-class feature. GoF principle в языке |
| **Singleton Pattern** | object keyword реализует thread-safe lazy singleton. JVM гарантирует единственность |
| **Delegation Pattern** | `class A : B by impl` — A делегирует B методы объекту impl. GoF Delegation встроен в язык |
| **Factory Method** | companion object factory methods. Альтернатива конструкторам с более выразительными именами |
| **Discriminated Union** | sealed class + when = type-safe handling всех вариантов. Exhaustive checking компилятором |
| **Prototype Pattern** | data class copy() создаёт копию с возможностью изменения отдельных полей |
| **Template Method** | abstract class с частичной реализацией. Subclass реализует только abstract методы |
| **Liskov Substitution** | Final by default предотвращает нарушение LSP. Наследование — осознанный выбор |

---

## Рекомендуемые источники

### Официальная документация
- [Classes and Objects](https://kotlinlang.org/docs/classes.html) — официальный гайд
- [Data Classes](https://kotlinlang.org/docs/data-classes.html) — data class deep dive
- [Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html) — sealed class patterns

### Книги
- **"Kotlin in Action"** (2nd ed) — глава о классах и объектах
- **"Effective Kotlin"** — best practices для OOP
- **"Head First Design Patterns"** — паттерны GoF (многие проще в Kotlin)

### Видео
- [Kotlin Vocabulary](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc_T0fSZc9obnmnWcjvmJdw_) — Google, data class, sealed class
- [KotlinConf talks on OOP](https://www.youtube.com/results?search_query=kotlinconf+sealed+class) — продвинутые паттерны

---

*Проверено: 2026-01-09 | Источники: Kotlin docs, Effective Kotlin, Google Android team — Педагогический контент проверен*
