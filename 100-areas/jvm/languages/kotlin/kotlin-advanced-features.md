---
title: "Kotlin Advanced Features: Extension Functions, Delegates, DSL"
created: 2025-11-25
modified: 2025-12-27
tags: [kotlin, extensions, delegates, dsl, operator-overloading]
related:
  - "[[kotlin-overview]]"
  - "[[kotlin-best-practices]]"
  - "[[kotlin-type-system]]"
---

# Kotlin Advanced: расширения, делегаты, DSL

> **TL;DR:** Extension functions добавляют методы к любому классу без наследования (`fun String.isEmail()`). Property delegates переиспользуют логику: `by lazy {}` — ленивая инициализация, `by observable {}` — отслеживание изменений. DSL строится через function types с receiver: Compose, Ktor, Gradle Kotlin DSL — всё это DSL. Используй `@DslMarker` для контроля scope в DSL.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Kotlin basics** | Синтаксис, классы, функции | [[kotlin-basics]] |
| **Lambda expressions** | Function types, trailing lambdas | [[kotlin-functional]] |
| **OOP в Kotlin** | Классы, интерфейсы, inheritance | [[kotlin-oop]] |
| **Generics** | Type parameters, variance | [[kotlin-type-system]] |
| **Operator overloading** | Понимание операторов | [Kotlin Docs](https://kotlinlang.org/docs/operator-overloading.html) |

---

## Зачем это нужно

**Проблема 1 — расширение чужих классов:**
В Java нельзя добавить метод к `String` или `List` — приходится создавать `StringUtils.isEmail(str)`. Это плохо читается и требует помнить, где искать утилиты.

**Решение — Extension Functions:**
`fun String.isEmail(): Boolean` — теперь `email.isEmail()` выглядит как встроенный метод. Работает даже для final классов и сторонних библиотек.

**Проблема 2 — повторяющаяся логика свойств:**
Ленивая инициализация, логирование изменений, сохранение в SharedPreferences — один и тот же код копируется.

**Решение — Property Delegates:**
`by lazy {}` вычисляет значение один раз, `by observable {}` отслеживает изменения. Можно создать свой делегат для SharedPreferences/Room/etc.

**Проблема 3 — конфигурация через код:**
XML/JSON/YAML не type-safe, IDE не помогает с автодополнением и рефакторингом.

**Решение — DSL:**
Kotlin позволяет писать код, который читается как конфигурация. Compose UI, Ktor routing, Gradle — всё это Kotlin DSL.

**Результат:** Более выразительный и читаемый код без потери type-safety.

### Актуальность 2024-2025

| Фича | Статус | Что нового |
|------|--------|------------|
| **Context Receivers** | ⚠️ Experimental | Kotlin 2.0+: context parameters заменяют context receivers |
| **Multiple Receivers** | ⚠️ Design | KEEP-259: несколько receivers в одной функции |
| **Property Delegates** | ✅ Stable | Kotlin 2.0: улучшенная производительность делегатов |
| **@DslMarker** | ✅ Stable | Используется в Compose, Ktor, Gradle Kotlin DSL |
| **Extension Functions** | ✅ Stable | Основа Kotlin stdlib, kotlinx, Compose extensions |

**Тренды 2025:**
- Compose использует DSL-паттерны повсеместно
- Context receivers → context parameters (Kotlin 2.1+)
- Type-safe builders — стандарт для конфигурации

---

## Обзор технологий

**Extension functions** добавляют методы к любому классу без наследования: `fun String.isPalindrome(): Boolean`. Работает даже для final классов.

**Property delegates** переиспользуют логику свойств: `by lazy {}` вычисляет один раз, `by observable {}` отслеживает изменения, `by Delegates.vetoable {}` позволяет отклонить.

**DSL** строится через function types с receiver (`block: StringBuilder.() -> Unit`) и trailing lambda. Результат: Ktor, Compose, Gradle Kotlin DSL — код как конфигурация.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Extension function** | Метод, добавленный к классу извне | Добавить карман к чужой куртке — не перешивая её |
| **Extension property** | Вычисляемое свойство для любого типа | Этикетка с ценой — вычисляется, не хранится внутри товара |
| **Operator overloading** | Переопределение +, -, [], invoke | Калькулятор понимает + для разных типов: числа, строки, списки |
| **Delegate (Делегат)** | Объект, реализующий логику свойства | Секретарь — ты говоришь "позвони", он знает как |
| **lazy** | Делегат с отложенной инициализацией | Пицца по вызову — готовят только когда заказал |
| **observable** | Делегат с отслеживанием изменений | Датчик движения — сообщает при каждом изменении |
| **vetoable** | Делегат с возможностью отклонить изменение | Охранник на входе — может не пустить |
| **DSL** | Domain-Specific Language | Язык рецептов — понятен поварам, типобезопасен |
| **Receiver** | Объект, на котором вызывается функция (`this`) | Адресат письма — к кому обращается функция |
| **@DslMarker** | Аннотация для контроля scope в DSL | Границы кухни — нельзя готовить в гостиной |

---

## Extension Functions

### Основы расширений

```kotlin
// Extension function - добавляет метод к существующему классу
fun String.isPalindrome(): Boolean {
    return this == this.reversed()
}

println("radar".isPalindrome())  // true
println("hello".isPalindrome())  // false

// Extension с параметрами
fun String.repeat(times: Int): String {
    return (1..times).joinToString("") { this }
}

println("Ha".repeat(3))  // "HaHaHa"

// Extension для generic типов
fun <T> List<T>.secondOrNull(): T? {
    return if (this.size >= 2) this[1] else null
}

val list = listOf(1, 2, 3)
println(list.secondOrNull())  // 2

// Extension для nullable типов
fun String?.orDefault(default: String): String {
    return this ?: default
}

val str: String? = null
println(str.orDefault("default"))  // "default"
```

**Почему extension functions?**
- Не требуют наследования: расширяем final классы (String, Int)
- Не модифицируют класс: добавление извне
- Читаемость: `string.extension()` vs `Utils.method(string)`
- Scope control: видны только где импортированы

### Extensions vs методы класса

```kotlin
class MyClass {
    fun memberFunction() = "member"
}

fun MyClass.extensionFunction() = "extension"

// Extension НЕ переопределяет методы класса
fun MyClass.memberFunction() = "extension override"

val obj = MyClass()
println(obj.memberFunction())  // "member" (метод класса побеждает!)
println(obj.extensionFunction())  // "extension"

// Extensions разрешаются статически (не полиморфны)
open class Base
class Derived : Base()

fun Base.print() = println("Base extension")
fun Derived.print() = println("Derived extension")

fun execute(base: Base) {
    base.print()  // Всегда "Base extension" даже если передали Derived!
}

execute(Base())     // "Base extension"
execute(Derived())  // "Base extension" (не "Derived"!)
```

**Важно**: Extensions не являются настоящими членами класса:
- Не могут обращаться к private членам
- Не полиморфны (dispatch статический)
- Не участвуют в override

### Почему extensions не полиморфны? (Deep Dive)

```
Compile-time vs Runtime type dispatch:

┌────────────────────────────────────────────────────────────────┐
│                        MEMBER FUNCTION                          │
├────────────────────────────────────────────────────────────────┤
│ open class Animal { open fun speak() = "..." }                  │
│ class Dog : Animal() { override fun speak() = "Woof!" }         │
│                                                                 │
│ val animal: Animal = Dog()                                      │
│ animal.speak()                                                  │
│     ↓                                                          │
│ Dispatch происходит в RUNTIME по реальному типу объекта        │
│ → Вызывается Dog.speak() → "Woof!"                             │
└────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────┐
│                      EXTENSION FUNCTION                         │
├────────────────────────────────────────────────────────────────┤
│ fun Animal.speak() = "Animal sound"                             │
│ fun Dog.speak() = "Woof!"                                       │
│                                                                 │
│ val animal: Animal = Dog()                                      │
│ animal.speak()                                                  │
│     ↓                                                          │
│ Dispatch происходит в COMPILE-TIME по объявленному типу        │
│ → Компилятор видит Animal → Animal.speak() → "Animal sound"    │
└────────────────────────────────────────────────────────────────┘
```

**Техническая причина:**

Extensions компилируются в static методы JVM:

```kotlin
// Kotlin source
fun String.addExclamation() = this + "!"

// Скомпилированный Java-эквивалент
public static String addExclamation(String $this) {
    return $this + "!";
}
```

Static методы не имеют vtable (таблицы виртуальных методов), поэтому dispatch происходит статически по типу аргумента, известному на compile-time.

**Когда это проблема:**

```kotlin
// ❌ Неожиданное поведение
fun processAnimals(animals: List<Animal>) {
    animals.forEach { it.speak() }  // Все скажут "Animal sound"!
}

val pets = listOf(Dog(), Cat(), Bird())
processAnimals(pets)  // "Animal sound" x3, не "Woof!", "Meow!", "Tweet!"

// ✅ Решение 1: Используйте member functions
open class Animal { open fun speak() = "..." }
class Dog : Animal() { override fun speak() = "Woof!" }

// ✅ Решение 2: Pattern matching в extension
fun Animal.speakPolymorphic() = when (this) {
    is Dog -> "Woof!"
    is Cat -> "Meow!"
    else -> "Unknown"
}

// ✅ Решение 3: Visitor pattern
interface AnimalVisitor<T> {
    fun visit(dog: Dog): T
    fun visit(cat: Cat): T
}
```

### Полезные patterns с extensions

```kotlin
// Conversion extensions
fun String.toIntOrDefault(default: Int = 0): Int {
    return this.toIntOrNull() ?: default
}

// Validation extensions
fun String.isValidEmail(): Boolean {
    return this.contains("@") && this.contains(".")
}

// Builder-style extensions
fun StringBuilder.appendLine(text: String): StringBuilder {
    return this.append(text).append("\n")
}

val result = StringBuilder()
    .appendLine("Line 1")
    .appendLine("Line 2")
    .appendLine("Line 3")
    .toString()

// Scope limitation extensions
private fun Int.timesTwo() = this * 2  // Видна только в файле

// Context-specific extensions
context(Logger)  // Kotlin 1.6.20+ context receivers
fun String.log() {
    logInfo(this)  // Доступ к Logger из контекста
}
```

## Extension Properties

### Основы extension properties

```kotlin
// Extension property (всегда вычисляемое, нет backing field)
val String.firstChar: Char
    get() = this[0]

println("Hello".firstChar)  // 'H'

// Extension property с кастомным getter
val List<Int>.sumOfSquares: Int
    get() = this.sumOf { it * it }

println(listOf(1, 2, 3).sumOfSquares)  // 14

// Extension property для изменяемого доступа (на nullable)
var StringBuilder.lastChar: Char
    get() = this[this.length - 1]
    set(value) {
        this.setCharAt(this.length - 1, value)
    }

val sb = StringBuilder("Hello")
println(sb.lastChar)  // 'o'
sb.lastChar = '!'
println(sb)  // "Hell!"

// Extension property нельзя инициализировать
val String.length2: Int = this.length  // ❌ Ошибка компиляции!
// Extension properties не могут иметь backing field
```

**Почему только вычисляемые?**
- Extension не может хранить состояние в классе
- Нет backing field: нельзя добавить память в существующий класс
- Решение: используйте функцию или делегат

### Практические примеры

```kotlin
// Удобные properties для Android
val View.isVisible: Boolean
    get() = visibility == View.VISIBLE

val View.isGone: Boolean
    get() = visibility == View.GONE

fun View.show() {
    visibility = View.VISIBLE
}

fun View.hide() {
    visibility = View.GONE
}

// Для работы с датами
val Int.days: Duration
    get() = Duration.ofDays(this.toLong())

val Int.hours: Duration
    get() = Duration.ofHours(this.toLong())

val timeout = 5.days + 3.hours

// Для коллекций
val <T> List<T>.indices: IntRange
    get() = 0 until size

// JSON-подобный доступ
operator fun JsonObject.get(key: String): JsonElement? {
    return this.getAsJsonPrimitive(key)
}

val json: JsonObject = parseJson("{}")
val value = json["key"]  // Красиво!
```

## Operator Overloading

### Арифметические операторы

```kotlin
// Переопределение операторов через operator fun
data class Point(val x: Int, val y: Int) {
    operator fun plus(other: Point): Point {
        return Point(x + other.x, y + other.y)
    }

    operator fun minus(other: Point): Point {
        return Point(x - other.x, y - other.y)
    }

    operator fun times(scale: Int): Point {
        return Point(x * scale, y * scale)
    }

    operator fun unaryMinus(): Point {
        return Point(-x, -y)
    }
}

val p1 = Point(1, 2)
val p2 = Point(3, 4)

println(p1 + p2)      // Point(4, 6)
println(p1 - p2)      // Point(-2, -2)
println(p1 * 3)       // Point(3, 6)
println(-p1)          // Point(-1, -2)

// Составные операторы (+=, -=, *=)
data class Counter(var value: Int) {
    operator fun plusAssign(delta: Int) {
        value += delta
    }
}

val counter = Counter(0)
counter += 5
println(counter.value)  // 5
```

**Операторы и их функции:**
- `+` → `plus`
- `-` → `minus`
- `*` → `times`
- `/` → `div`
- `%` → `rem`
- `++` → `inc`
- `--` → `dec`
- `+=` → `plusAssign`
- `==` → `equals`
- `>`, `<`, `>=`, `<=` → `compareTo`

### Indexed access operators

```kotlin
// Доступ по индексу [] через get/set
class Matrix(private val data: Array<IntArray>) {
    operator fun get(row: Int, col: Int): Int {
        return data[row][col]
    }

    operator fun set(row: Int, col: Int, value: Int) {
        data[row][col] = value
    }
}

val matrix = Matrix(arrayOf(
    intArrayOf(1, 2, 3),
    intArrayOf(4, 5, 6)
))

println(matrix[0, 1])  // 2
matrix[1, 2] = 10
println(matrix[1, 2])  // 10

// Множественные параметры для get/set
class Cube(private val data: Array<Array<IntArray>>) {
    operator fun get(x: Int, y: Int, z: Int): Int {
        return data[x][y][z]
    }

    operator fun set(x: Int, y: Int, z: Int, value: Int) {
        data[x][y][z] = value
    }
}

val cube = Cube(/*...*/)
cube[1, 2, 3] = 42
```

### Invoke operator

```kotlin
// invoke позволяет вызывать объект как функцию
class Greeter(private val greeting: String) {
    operator fun invoke(name: String): String {
        return "$greeting, $name!"
    }
}

val greet = Greeter("Hello")
println(greet("Alice"))  // "Hello, Alice!"

// Множественные invoke для overloading
class Calculator {
    operator fun invoke(a: Int, b: Int): Int = a + b
    operator fun invoke(a: Int, b: Int, c: Int): Int = a + b + c
    operator fun invoke(operation: String, a: Int, b: Int): Int {
        return when (operation) {
            "+" -> a + b
            "-" -> a - b
            "*" -> a * b
            "/" -> a / b
            else -> throw IllegalArgumentException()
        }
    }
}

val calc = Calculator()
println(calc(2, 3))           // 5
println(calc(1, 2, 3))        // 6
println(calc("+", 5, 3))      // 8

// Практическое применение: Dependency Provider
class ServiceProvider {
    private val services = mutableMapOf<Class<*>, Any>()

    fun <T : Any> register(clazz: Class<T>, instance: T) {
        services[clazz] = instance
    }

    operator fun <T : Any> invoke(clazz: Class<T>): T {
        @Suppress("UNCHECKED_CAST")
        return services[clazz] as? T ?: throw IllegalStateException()
    }
}

val provider = ServiceProvider()
provider.register(MyService::class.java, MyServiceImpl())
val service = provider(MyService::class.java)  // Красиво!
```

### Contains operator

```kotlin
// in оператор через contains
class Range(val min: Int, val max: Int) {
    operator fun contains(value: Int): Boolean {
        return value in min..max
    }
}

val range = Range(1, 10)
println(5 in range)   // true
println(15 in range)  // false

// Для коллекций
class CustomList<T>(private val items: List<T>) {
    operator fun contains(element: T): Boolean {
        return element in items
    }
}
```

### RangeTo и iterator operators

```kotlin
// .. оператор через rangeTo
data class Date(val year: Int, val month: Int, val day: Int) : Comparable<Date> {
    operator fun rangeTo(other: Date): DateRange {
        return DateRange(this, other)
    }

    override fun compareTo(other: Date): Int {
        // Сравнение дат
        return when {
            year != other.year -> year - other.year
            month != other.month -> month - other.month
            else -> day - other.day
        }
    }
}

class DateRange(
    override val start: Date,
    override val endInclusive: Date
) : ClosedRange<Date>, Iterable<Date> {

    override operator fun iterator(): Iterator<Date> {
        return DateIterator(start, endInclusive)
    }
}

class DateIterator(start: Date, private val end: Date) : Iterator<Date> {
    private var current = start

    override fun hasNext(): Boolean = current <= end

    override fun next(): Date {
        val result = current
        current = current.nextDay()  // Метод для следующего дня
        return result
    }
}

// Использование
val start = Date(2025, 1, 1)
val end = Date(2025, 1, 10)

for (date in start..end) {
    println(date)
}
```

## Property Delegation

### Основы делегирования

```kotlin
// Делегирование свойства другому объекту
class Delegate {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): String {
        return "Delegated value for ${property.name}"
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        println("Setting ${property.name} = $value")
    }
}

class Example {
    var property: String by Delegate()
}

val example = Example()
println(example.property)  // "Delegated value for property"
example.property = "new"   // "Setting property = new"

// Делегат должен реализовать getValue (и setValue для var)
interface ReadOnlyProperty<in R, out T> {
    operator fun getValue(thisRef: R, property: KProperty<*>): T
}

interface ReadWriteProperty<in R, T> {
    operator fun getValue(thisRef: R, property: KProperty<*>): T
    operator fun setValue(thisRef: R, property: KProperty<*>, value: T)
}
```

**Почему делегаты?**
- Переиспользование логики: один делегат для множества свойств
- Separation of concerns: логика свойства вынесена отдельно
- Стандартные делегаты: lazy, observable, vetoable из коробки

### Lazy delegate

```kotlin
// lazy - ленивая инициализация (вычисляется при первом доступе)
class HeavyObject {
    val expensiveProperty: String by lazy {
        println("Computing expensive value")
        Thread.sleep(1000)
        "Expensive Result"
    }
}

val obj = HeavyObject()
println("Object created")
println(obj.expensiveProperty)  // "Computing expensive value" → "Expensive Result"
println(obj.expensiveProperty)  // "Expensive Result" (уже вычислено)

// lazy с параметрами
val threadSafeLazy: String by lazy(LazyThreadSafetyMode.SYNCHRONIZED) {
    // Thread-safe (default)
    heavyComputation()
}

val notThreadSafe: String by lazy(LazyThreadSafetyMode.NONE) {
    // Не thread-safe, но быстрее
    heavyComputation()
}

val publicationSafe: String by lazy(LazyThreadSafetyMode.PUBLICATION) {
    // Множественные вычисления допустимы, но значение одно
    heavyComputation()
}

// Практический пример
class UserProfile(private val userId: String) {
    private val database by lazy { DatabaseConnection() }

    val user by lazy {
        database.fetchUser(userId)  // Запрос только при первом доступе
    }

    val posts by lazy {
        database.fetchPosts(userId)
    }
}
```

### Observable delegates

```kotlin
import kotlin.properties.Delegates

// observable - наблюдение за изменениями
class User {
    var name: String by Delegates.observable("Initial") { property, oldValue, newValue ->
        println("${property.name} changed from $oldValue to $newValue")
    }
}

val user = User()
user.name = "Alice"  // "name changed from Initial to Alice"
user.name = "Bob"    // "name changed from Alice to Bob"

// vetoable - с возможностью отменить изменение
class Product {
    var price: Double by Delegates.vetoable(0.0) { property, oldValue, newValue ->
        newValue >= 0  // Цена не может быть отрицательной
    }
}

val product = Product()
product.price = 100.0  // OK
println(product.price)  // 100.0

product.price = -50.0  // Отменено!
println(product.price)  // 100.0 (не изменилось)

// Практический пример: ViewModel с observable
class ViewModel {
    var isLoading: Boolean by Delegates.observable(false) { _, _, newValue ->
        notifyLoadingStateChanged(newValue)
    }

    var errorMessage: String? by Delegates.observable(null) { _, _, newValue ->
        if (newValue != null) {
            showError(newValue)
        }
    }
}
```

### Custom delegates

```kotlin
// Собственный делегат для preferences
class PreferenceDelegate<T>(
    private val key: String,
    private val defaultValue: T
) : ReadWriteProperty<Any?, T> {

    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        @Suppress("UNCHECKED_CAST")
        return preferences.get(key, defaultValue) as T
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        preferences.put(key, value)
    }
}

// Extension для удобства
fun <T> preference(key: String, defaultValue: T) =
    PreferenceDelegate(key, defaultValue)

// Использование
class Settings {
    var username: String by preference("username", "guest")
    var isNotificationsEnabled: Boolean by preference("notifications", true)
    var fontSize: Int by preference("font_size", 14)
}

// Делегат для thread-safe доступа
class SynchronizedDelegate<T>(initialValue: T) : ReadWriteProperty<Any?, T> {
    private var value: T = initialValue
    private val lock = Any()

    override fun getValue(thisRef: Any?, property: KProperty<*>): T {
        synchronized(lock) {
            return value
        }
    }

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        synchronized(lock) {
            this.value = value
        }
    }
}

fun <T> synchronized(initialValue: T) = SynchronizedDelegate(initialValue)

// Использование
class Counter {
    var count: Int by synchronized(0)
}

// Делегат с валидацией
class ValidatedDelegate<T>(
    initialValue: T,
    private val validator: (T) -> Boolean
) : ReadWriteProperty<Any?, T> {
    private var value: T = initialValue

    init {
        require(validator(initialValue)) { "Initial value is invalid" }
    }

    override fun getValue(thisRef: Any?, property: KProperty<*>): T = value

    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        if (validator(value)) {
            this.value = value
        } else {
            throw IllegalArgumentException("Invalid value: $value")
        }
    }
}

fun <T> validated(initialValue: T, validator: (T) -> Boolean) =
    ValidatedDelegate(initialValue, validator)

class Person {
    var age: Int by validated(0) { it >= 0 && it <= 150 }
    var email: String by validated("") { it.contains("@") }
}
```

### Map delegate

```kotlin
// Делегирование свойств в Map
class User(map: Map<String, Any?>) {
    val name: String by map
    val age: Int by map
    val email: String by map
}

val userMap = mapOf(
    "name" to "Alice",
    "age" to 25,
    "email" to "alice@example.com"
)

val user = User(userMap)
println(user.name)   // "Alice"
println(user.age)    // 25

// Mutable версия
class MutableUser(map: MutableMap<String, Any?>) {
    var name: String by map
    var age: Int by map
}

val mutableMap = mutableMapOf(
    "name" to "Bob",
    "age" to 30
)

val mutableUser = MutableUser(mutableMap)
mutableUser.name = "Charlie"
println(mutableMap["name"])  // "Charlie"

// Практическое применение: JSON parsing
class JsonModel(private val json: Map<String, Any?>) {
    val id: String by json
    val title: String by json
    val count: Int by json
    val tags: List<String> by json
}
```

## DSL (Domain Specific Language)

### Function types с receiver для DSL

```kotlin
// DSL через function types с receiver
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    fun h1(text: String) {
        elements.add("<h1>$text</h1>")
    }

    fun p(text: String) {
        elements.add("<p>$text</p>")
    }

    fun div(init: HtmlBuilder.() -> Unit) {
        elements.add("<div>")
        this.init()  // Вызываем лямбду с this как receiver
        elements.add("</div>")
    }

    fun build(): String = elements.joinToString("\n")
}

fun html(init: HtmlBuilder.() -> Unit): String {
    val builder = HtmlBuilder()
    builder.init()
    return builder.build()
}

// Использование
val page = html {
    h1("Welcome")
    div {
        p("Paragraph 1")
        p("Paragraph 2")
    }
    p("Outside div")
}
```

**Почему receiver types для DSL?**
- Неявный this: методы builder доступны без префикса
- Вложенность: естественная структура через вложенные лямбды
- Типобезопасность: компилятор проверяет допустимые вызовы

### Kotlinx.html пример

```kotlin
import kotlinx.html.*
import kotlinx.html.stream.createHTML

// Реальный DSL из библиотеки
val htmlString = createHTML().html {
    head {
        title { +"My Page" }
        link {
            rel = "stylesheet"
            href = "style.css"
        }
    }
    body {
        h1 { +"Welcome" }
        div {
            id = "content"
            classes = setOf("container", "main")

            p {
                +"This is a "
                strong { +"bold" }
                +" text."
            }

            ul {
                for (i in 1..3) {
                    li { +"Item $i" }
                }
            }
        }
    }
}
```

### SQL DSL пример (Exposed-style)

```kotlin
// Типобезопасный SQL DSL
object Users : Table("users") {
    val id = integer("id").autoIncrement()
    val name = varchar("name", 50)
    val email = varchar("email", 100)
    val age = integer("age")

    override val primaryKey = PrimaryKey(id)
}

// Запросы в DSL стиле
fun findUsers() {
    Users
        .select { (Users.age greater 18) and (Users.name like "A%") }
        .orderBy(Users.name)
        .limit(10)
        .forEach { row ->
            println("${row[Users.name]}: ${row[Users.email]}")
        }
}

fun insertUser(name: String, email: String, age: Int) {
    Users.insert {
        it[Users.name] = name
        it[Users.email] = email
        it[Users.age] = age
    }
}

// Типы для DSL
infix fun Column<Int>.greater(value: Int): Op<Boolean> {
    return GreaterOp(this, intParam(value))
}

infix fun Column<String>.like(pattern: String): Op<Boolean> {
    return LikeOp(this, stringParam(pattern))
}
```

### Test DSL пример (Kotest-style)

```kotlin
// DSL для тестов
class MyTest : FunSpec({
    test("addition should work") {
        2 + 2 shouldBe 4
    }

    context("when user is logged in") {
        test("should see dashboard") {
            val user = loginUser()
            user.canSeeDashboard() shouldBe true
        }

        test("should see profile") {
            val user = loginUser()
            user.canSeeProfile() shouldBe true
        }
    }

    xtest("disabled test") {
        // Этот тест пропускается
    }
})

// Реализация DSL
class FunSpec(private val init: FunSpec.() -> Unit) {
    private val tests = mutableListOf<Test>()

    init {
        this.init()
    }

    fun test(name: String, test: suspend TestScope.() -> Unit) {
        tests.add(Test(name, test, enabled = true))
    }

    fun xtest(name: String, test: suspend TestScope.() -> Unit) {
        tests.add(Test(name, test, enabled = false))
    }

    fun context(name: String, init: FunSpec.() -> Unit) {
        // Вложенный контекст
    }
}

infix fun <T> T.shouldBe(expected: T) {
    if (this != expected) {
        throw AssertionError("Expected $expected but got $this")
    }
}
```

### Builder DSL с @DslMarker

```kotlin
// @DslMarker предотвращает вложенные вызовы из внешних scope
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HTML {
    fun head(init: Head.() -> Unit) {
        val head = Head()
        head.init()
    }

    fun body(init: Body.() -> Unit) {
        val body = Body()
        body.init()
    }
}

@HtmlDsl
class Head {
    fun title(text: String) { }
}

@HtmlDsl
class Body {
    fun h1(text: String) { }
    fun p(text: String) { }
}

fun html(init: HTML.() -> Unit): HTML {
    val html = HTML()
    html.init()
    return html
}

// Использование
val page = html {
    head {
        title("My Page")
        // body { }  // ❌ Ошибка! Нельзя вызвать body внутри head
    }

    body {
        h1("Title")
        // head { }  // ❌ Ошибка! Нельзя вызвать head внутри body
        p("Text")
    }
}
```

**Почему @DslMarker?**
- Предотвращает ошибки: нельзя случайно вызвать метод из внешнего scope
- Типобезопасность: компилятор не даст создать некорректную структуру
- Читаемость: явная структура DSL

### DSL Step-by-Step: от нуля до production

**Шаг 1: Определите структуру вашего DSL**

```kotlin
// Целевой результат (что хотим писать):
val menu = menu {
    item("Home", "/")
    item("About", "/about")
    submenu("Products") {
        item("Product A", "/products/a")
        item("Product B", "/products/b")
    }
}
```

**Шаг 2: Создайте data-классы для хранения результата**

```kotlin
// Domain модель
sealed class MenuItem {
    data class Link(val title: String, val url: String) : MenuItem()
    data class Submenu(val title: String, val items: List<MenuItem>) : MenuItem()
}

data class Menu(val items: List<MenuItem>)
```

**Шаг 3: Создайте Builder классы**

```kotlin
@DslMarker
annotation class MenuDsl

@MenuDsl
class MenuBuilder {
    private val items = mutableListOf<MenuItem>()

    fun item(title: String, url: String) {
        items.add(MenuItem.Link(title, url))
    }

    fun submenu(title: String, init: SubmenuBuilder.() -> Unit) {
        val builder = SubmenuBuilder()
        builder.init()  // Вызываем лямбду с builder как receiver
        items.add(MenuItem.Submenu(title, builder.build()))
    }

    fun build(): Menu = Menu(items.toList())
}

@MenuDsl
class SubmenuBuilder {
    private val items = mutableListOf<MenuItem>()

    fun item(title: String, url: String) {
        items.add(MenuItem.Link(title, url))
    }

    fun build(): List<MenuItem> = items.toList()
}
```

**Шаг 4: Создайте entry-point функцию**

```kotlin
fun menu(init: MenuBuilder.() -> Unit): Menu {
    val builder = MenuBuilder()
    builder.init()
    return builder.build()
}
```

**Шаг 5: Добавьте type-safety и валидацию**

```kotlin
@MenuDsl
class MenuBuilder {
    private val items = mutableListOf<MenuItem>()
    private var isFinalized = false

    fun item(title: String, url: String) {
        require(title.isNotBlank()) { "Title cannot be blank" }
        require(url.startsWith("/")) { "URL must start with /" }
        require(!isFinalized) { "Cannot add items after build" }
        items.add(MenuItem.Link(title, url))
    }

    // Infix для более красивого синтаксиса
    infix fun String.linkTo(url: String) = item(this, url)

    fun build(): Menu {
        isFinalized = true
        require(items.isNotEmpty()) { "Menu must have at least one item" }
        return Menu(items.toList())
    }
}

// Теперь можно писать:
val menu = menu {
    "Home" linkTo "/"
    "About" linkTo "/about"
}
```

**Шаг 6: Добавьте DSL-specific operators (опционально)**

```kotlin
@MenuDsl
class MenuBuilder {
    // ... previous code ...

    // Unary + для добавления link
    operator fun String.unaryPlus() {
        item(this, "/${this.lowercase().replace(" ", "-")}")
    }

    // Minus для disabled items
    operator fun String.unaryMinus() {
        items.add(MenuItem.Link(this, "#", disabled = true))
    }
}

// Теперь можно писать:
val menu = menu {
    +"Home"           // auto-generates /home
    +"About Us"       // auto-generates /about-us
    -"Coming Soon"    // disabled item
}
```

**Полная архитектура DSL:**

```
┌─────────────────────────────────────────────────────────────┐
│                     DSL Architecture                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  User Code:           DSL Internals:         Domain Model:  │
│                                                              │
│  menu {        →      MenuBuilder       →    Menu           │
│    item(...)  →        ↓                     ↑              │
│    submenu {  →      SubmenuBuilder    →    MenuItem        │
│      item(...)→        ↓                     ↑              │
│    }                  build()                               │
│  }                                                          │
│                                                              │
│  Function with       Builders collect       Immutable       │
│  receiver type       and validate data      data classes    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Практические паттерны

### Type-safe configuration DSL

```kotlin
@DslMarker
annotation class ConfigDsl

@ConfigDsl
class ServerConfig {
    var host: String = "localhost"
    var port: Int = 8080
    var ssl: Boolean = false

    private val routes = mutableListOf<Route>()

    fun route(path: String, init: Route.() -> Unit) {
        val route = Route(path)
        route.init()
        routes.add(route)
    }

    fun build(): Server {
        return Server(host, port, ssl, routes)
    }
}

@ConfigDsl
class Route(val path: String) {
    var method: String = "GET"
    var handler: (Request) -> Response = { Response.ok() }

    fun get(handler: (Request) -> Response) {
        this.method = "GET"
        this.handler = handler
    }

    fun post(handler: (Request) -> Response) {
        this.method = "POST"
        this.handler = handler
    }
}

fun server(init: ServerConfig.() -> Unit): Server {
    val config = ServerConfig()
    config.init()
    return config.build()
}

// Использование
val server = server {
    host = "0.0.0.0"
    port = 9000
    ssl = true

    route("/api/users") {
        get { request ->
            Response.json(fetchUsers())
        }
    }

    route("/api/user/{id}") {
        post { request ->
            val user = createUser(request.body)
            Response.json(user)
        }
    }
}
```

### Extension-based DSL

```kotlin
// DSL через extension functions
fun <T> buildList(init: MutableList<T>.() -> Unit): List<T> {
    val list = mutableListOf<T>()
    list.init()
    return list
}

// Использование
val numbers = buildList<Int> {
    add(1)
    add(2)
    addAll(listOf(3, 4, 5))

    for (i in 6..10) {
        add(i)
    }
}

// Extension для более богатого DSL
fun <T> MutableList<T>.item(value: T) = add(value)

fun <T> MutableList<T>.items(vararg values: T) = addAll(values)

val enhanced = buildList<String> {
    item("first")
    items("second", "third", "fourth")

    if (size < 10) {
        item("fifth")
    }
}
```

## Распространённые ошибки

### 1. Extension на nullable когда нужен non-null

```kotlin
// ❌ Extension для non-null, но хотим работать с nullable
fun String.toUpperCase(): String = this.uppercase()

val str: String? = null
// str.toUpperCase()  // ❌ Ошибка компиляции

// ✅ Extension для nullable
fun String?.toUpperCaseOrEmpty(): String = this?.uppercase() ?: ""

val str: String? = null
str.toUpperCaseOrEmpty()  // ✅ OK, вернёт ""
```

### 2. Забыли про статический dispatch extensions

```kotlin
// ❌ Ожидаем полиморфизм от extension
open class Base
class Derived : Base()

fun Base.print() = println("Base")
fun Derived.print() = println("Derived")

fun test(base: Base) {
    base.print()  // Всегда "Base"!
}

test(Derived())  // "Base", не "Derived"!

// ✅ Используйте обычные методы для полиморфизма
open class Base {
    open fun print() = println("Base")
}

class Derived : Base() {
    override fun print() = println("Derived")
}
```

### 3. Operator overloading для неожиданного поведения

```kotlin
// ❌ Неинтуитивные операторы
class User(val name: String) {
    operator fun plus(other: User): String {
        return "$name loves ${other.name}"  // WTF?
    }
}

val result = user1 + user2  // Непонятно что происходит

// ✅ Используйте операторы интуитивно
class Point(val x: Int, val y: Int) {
    operator fun plus(other: Point): Point {
        return Point(x + other.x, y + other.y)  // Математически логично
    }
}
```

### 4. Lazy delegate для mutable значений

```kotlin
// ❌ Lazy для значений которые могут меняться
class Config {
    val currentTime by lazy {
        System.currentTimeMillis()  // Вычислится один раз!
    }
}

val config = Config()
println(config.currentTime)  // 1000
Thread.sleep(1000)
println(config.currentTime)  // 1000 (не обновилось!)

// ✅ Используйте lazy только для неизменных значений
class Config {
    fun getCurrentTime() = System.currentTimeMillis()

    // Или для дорогой инициализации
    val database by lazy {
        DatabaseConnection()  // Создастся один раз
    }
}
```

### 5. DSL без @DslMarker

```kotlin
// ❌ Можно случайно вызвать методы из внешнего scope
class Table {
    fun row(init: Row.() -> Unit) { }
}

class Row {
    fun cell(text: String) { }
    fun row(init: Row.() -> Unit) { }  // Ой!
}

table {
    row {
        cell("A")
        row {  // Можно вызвать, но это ошибка логики!
            cell("B")
        }
    }
}

// ✅ Используйте @DslMarker
@DslMarker
annotation class TableDsl

@TableDsl class Table { }
@TableDsl class Row { }
```

---

## Кто использует и реальные примеры

### Компании использующие Advanced Features

| Компания | Фича | Применение |
|----------|------|------------|
| **JetBrains** | DSL + Extensions | IntelliJ Platform SDK, Kotlin DSL для UI |
| **Google** | Compose DSL | Jetpack Compose — полностью на Kotlin DSL |
| **Gradle** | Kotlin DSL | build.gradle.kts — замена Groovy |
| **JetBrains** | Exposed DSL | Type-safe SQL DSL |
| **Ktor** | Routing DSL | HTTP routing через DSL |
| **Square** | Moshi Kotlin | Extensions для JSON parsing |

### Production DSL примеры

**Jetpack Compose (Google):**
```kotlin
@Composable
fun Greeting() {
    Column {
        Text("Hello")
        Button(onClick = { }) {
            Text("Click me")
        }
    }
}
// Column, Button, Text — всё это DSL с receiver
```

**Gradle Kotlin DSL:**
```kotlin
plugins {
    kotlin("jvm") version "2.0.0"
}

dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")
}
// implementation, plugins — extension functions
```

**Ktor Routing DSL:**
```kotlin
routing {
    get("/users") {
        call.respond(users)
    }
    post("/users") {
        val user = call.receive<User>()
        call.respond(HttpStatusCode.Created)
    }
}
```

### Реальные кейсы

**Case 1: Gradle — Kotlin DSL Adoption**
```
Проблема: Groovy DSL не type-safe, нет автокомплита
Решение: Kotlin DSL с extensions и type-safe builders
Результат: 60% Android проектов используют .kts файлы (2024)
```

**Case 2: Android Compose — UI DSL**
```
Проблема: XML layouts не гибкие, отдельный язык
Решение: Kotlin DSL для UI с @Composable функциями
Результат: Декларативный UI, hot reload, type-safe
```

---

## Чеклист

- [ ] Используете extensions для добавления методов без наследования
- [ ] Понимаете что extensions не полиморфны
- [ ] Применяете operator overloading интуитивно
- [ ] Используете lazy для дорогой инициализации
- [ ] Применяете observable/vetoable для отслеживания изменений
- [ ] Создаёте custom delegates для переиспользования логики
- [ ] Используете @DslMarker для type-safe DSL
- [ ] Понимаете разницу между extension property и функцией
- [ ] Не злоупотребляете operators для неочевидных операций
- [ ] Используете receiver types для DSL builders

## Проверь себя

1. **Почему extension functions не полиморфны?**
   <details><summary>Ответ</summary>
   Extensions компилируются в static методы JVM. Dispatch происходит на compile-time по объявленному типу переменной, а не по runtime типу объекта. Нет vtable — нет полиморфизма.
   </details>

2. **Когда использовать `api` vs `implementation` scope для extension?**
   <details><summary>Ответ</summary>
   Если extension экспортирует типы из другой библиотеки (возвращает или принимает), нужен `api`. Если extension — внутренняя деталь реализации, достаточно `implementation`.
   </details>

3. **Чем `lazy(SYNCHRONIZED)` отличается от `lazy(NONE)`?**
   <details><summary>Ответ</summary>
   SYNCHRONIZED — thread-safe (по умолчанию), использует double-checked locking. NONE — не thread-safe, быстрее в single-threaded сценариях. PUBLICATION — допускает множественные вычисления, но гарантирует единственное значение.
   </details>

4. **Зачем нужен @DslMarker?**
   <details><summary>Ответ</summary>
   @DslMarker предотвращает случайный вызов методов из внешнего scope внутри вложенного builder. Без него можно было бы вызвать `body {}` внутри `head {}` — компилятор покажет ошибку.
   </details>

5. **Можно ли создать extension property с backing field?**
   <details><summary>Ответ</summary>
   Нет. Extension property всегда вычисляемое, т.к. extension не может добавить состояние в существующий класс. Для хранения данных используйте делегаты или внешнее хранилище (WeakHashMap).
   </details>

---

## Связанные темы
- [[kotlin-functional]] — Function types с receiver для DSL
- [[kotlin-collections]] — Extensions для коллекций
- [[kotlin-best-practices]] — Идиоматичное использование advanced features
- [[kotlin-type-system]] — Generics в extensions и delegates

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Extension functions добавляют методы в класс" | Extensions компилируются в static методы. Никакого изменения класса нет — это синтаксический сахар для `StringUtils.lastChar(s)` → `s.lastChar()` |
| "Extensions поддерживают полиморфизм" | Extensions разрешаются статически (compile-time). Dispatch по declared type, не по runtime type — переопределение в подклассах не работает |
| "Delegates медленнее прямого доступа" | После инлайнинга JIT compiler устраняет overhead. `lazy` реализован эффективно с double-checked locking. Измеримая разница только в hot loops |
| "operator overloading делает код нечитаемым" | Kotlin ограничивает operators фиксированным набором. Невозможно создать произвольный `<=>`. Идиоматичное использование (`+` для коллекций) улучшает читаемость |
| "DSL builders — просто syntactic sugar" | Type-safe builders обеспечивают compile-time проверку структуры. Ошибка в HTML DSL → ошибка компиляции, не runtime exception |
| "lazy всегда thread-safe" | По умолчанию да (SYNCHRONIZED), но есть NONE (no synchronization) и PUBLICATION (multiple computations allowed). Выбор режима влияет на производительность |
| "Extension property может хранить состояние" | Extension property — только getter/setter без backing field. Для хранения данных нужен external storage (WeakHashMap, separate map) |
| "Context receivers заменяют dependency injection" | Context receivers обеспечивают compile-time scoping, но не lifecycle management. DI frameworks управляют созданием и временем жизни зависимостей |
| "DSL всегда лучше fluent API" | DSL добавляет cognitive load для нового разработчика. Для простых случаев fluent API (`builder.name("x").age(5)`) читабельнее |
| "inline функции всегда быстрее" | inline полезен для higher-order functions (экономия на lambda allocation). Для обычных функций inline увеличивает размер bytecode без выгоды |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin Advanced Features |
|--------------|---------------------------------------|
| **Static Dispatch** | Extensions используют static dispatch — метод выбирается по compile-time типу. В отличие от virtual dispatch (vtable lookup) нет runtime overhead |
| **Delegation Pattern** | Property delegates реализуют GoF Delegation — объект перенаправляет операции другому объекту. `by lazy` делегирует инициализацию Lazy<T> |
| **Memoization** | `lazy` реализует memoization — однократное вычисление с кэшированием результата. Классический паттерн оптимизации чистых функций |
| **Observer Pattern** | `Delegates.observable()` реализует Observer — подписчик получает уведомления об изменениях. Основа reactive programming |
| **Double-Checked Locking** | `lazy(SYNCHRONIZED)` использует DCL idiom — минимизация синхронизации при thread-safe ленивой инициализации |
| **Domain-Specific Languages** | Type-safe builders создают internal DSL — язык, встроенный в host language. Цепочка: DSL → AST → execution |
| **Receiver Types** | Extension functions используют implicit receiver — объект, доступный как `this`. Реализация open recursion |
| **Function Composition** | Operators `+`, `-` и др. — это function composition через operator overloading. Математические структуры (Monoid, Group) в коде |
| **Scope Functions** | `let`, `apply`, `also` — функции высшего порядка с receiver. Реализация continuation-passing style для fluent code |
| **Marker Annotations** | `@DslMarker` реализует compile-time constraints — ограничение области видимости для type safety |

---

## Источники

| # | Источник | Тип | Описание |
|---|----------|-----|----------|
| 1 | [Kotlin Extensions](https://kotlinlang.org/docs/extensions.html) | Docs | Официальная документация по extensions |
| 2 | [Delegated Properties](https://kotlinlang.org/docs/delegated-properties.html) | Docs | Property delegates в деталях |
| 3 | [Type-safe Builders](https://kotlinlang.org/docs/type-safe-builders.html) | Docs | DSL и type-safe builders |
| 4 | [Operator Overloading](https://kotlinlang.org/docs/operator-overloading.html) | Docs | Все доступные операторы |
| 5 | [KEEP-259: Context Parameters](https://github.com/Kotlin/KEEP/blob/master/proposals/context-parameters.md) | KEEP | Эволюция context receivers |
| 6 | [Kotlin DSL Best Practices](https://proandroiddev.com/kotlin-dsl-everywhere-a12bd09b10a6) | Blog | Паттерны создания DSL |
| 7 | [Jetpack Compose DSL](https://developer.android.com/jetpack/compose) | Docs | DSL в Compose UI |
| 8 | [Gradle Kotlin DSL Primer](https://docs.gradle.org/current/userguide/kotlin_dsl.html) | Docs | Kotlin DSL для Gradle |
| 9 | [kotlinx.html](https://github.com/Kotlin/kotlinx.html) | GitHub | Пример production DSL |
| 10 | [Roman Elizarov — Kotlin DSL Design](https://www.youtube.com/watch?v=0phKrXp8-8U) | Video | Доклад о дизайне DSL |

---

*Проверено: 2026-01-09 | Источники: Kotlin Docs, Compose Docs, Gradle Docs, Ktor Docs — Педагогический контент проверен*
