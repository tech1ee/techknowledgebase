---
title: "Functional Programming: Pure Functions, Immutability, Composition"
created: 2025-12-22
modified: 2026-02-19
type: deep-dive
status: draft
confidence: high
tags:
  - topic/programming
  - deep-dive/paradigms
  - functional
  - fp
  - immutability
  - composition
  - level/intermediate
related:
  - "[[programming-overview]]"
  - "[[solid-principles]]"
  - "[[design-patterns-overview]]"
prerequisites:
  - "[[solid-principles]]"
  - "[[type-systems-theory]]"
reading_time: 25
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Functional Programming: Pure Functions, Immutability, Composition

> FP --- это не "только функции". Это способ думать о программах как о композиции трансформаций данных.

---

## Исторический контекст

Функциональное программирование уходит корнями в лямбда-исчисление Алонзо Чёрча (1936) --- формальную систему для описания вычислений через функции. Первым практическим языком стал **Lisp** (John McCarthy, 1958), созданный для задач искусственного интеллекта в MIT. Lisp ввёл концепции first-class functions, рекурсии как основного механизма управления, и garbage collection.

В 1973 году Robin Milner создал язык **ML** (Meta Language) в Эдинбургском университете, который привнёс статическую типизацию с type inference --- компилятор сам выводит типы без явных аннотаций. ML породил целое семейство языков: Standard ML, OCaml, F#.

В 1990 году комитет исследователей опубликовал спецификацию **Haskell** --- чисто функционального языка с ленивыми вычислениями (lazy evaluation). Haskell стал "лабораторией" для исследования монад, type classes и других абстракций, которые позже проникли в mainstream-языки.

Влияние FP на современные языки огромно: лямбда-выражения появились в Java 8 (2014), C++ 11 (2011), Kotlin (2016). Концепции map/filter/reduce, pattern matching, immutable data classes стали стандартными инструментами даже в объектно-ориентированных языках. Rust (2015) построил всю систему ownership на идеях из ML и Haskell. Kotlin изначально проектировался с мощной поддержкой FP: lambda-литералы, extension functions, `inline`-функции с reified generics, `Sequence` для lazy evaluation и null-safety как встроенный `Maybe`-тип.

---

## TL;DR

- **Pure functions** --- нет side effects, всегда одинаковый результат для одинаковых аргументов
- **Immutability** --- данные не изменяются после создания
- **Composition** --- сложные функции из простых
- **Higher-order functions** --- функции как first-class citizens
- **Sequences** --- ленивые вычисления для эффективной обработки коллекций
- **Scope functions** --- идиоматичная композиция через `let`, `run`, `apply`, `also`, `with`

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Pure function** | Нет side effects, deterministic |
| **Side effect** | Изменение внешнего state, I/O |
| **Immutable** | Не изменяемый после создания |
| **Higher-order function** | Принимает или возвращает функцию |
| **First-class function** | Функция как значение |
| **Closure** | Функция + captured environment |
| **Referential transparency** | Можно заменить вызов на результат |
| **Monad** | Контейнер для последовательных вычислений |
| **Inline function** | Функция, тело которой подставляется в место вызова компилятором |
| **Reified generic** | Доступ к информации о типе в runtime через inline |
| **Sequence** | Ленивая коллекция --- элементы вычисляются по требованию |
| **Scope function** | `let`, `run`, `with`, `apply`, `also` --- функции контекста |
| **Either** | Контейнер "или ошибка, или результат" (Arrow library) |

---

## Pure Functions

```
+----------------------------------------------------------------------------+
|                        PURE vs IMPURE FUNCTIONS                            |
+----------------------------------------------------------------------------+
|                                                                            |
|  PURE FUNCTION                                                             |
|  +----------------------------------------------------------------------+  |
|  |                                                                      |  |
|  |    Input -----> +----------+ -----> Output                           |  |
|  |                 | Function |                                         |  |
|  |    Input -----> +----------+ -----> Output                           |  |
|  |                                                                      |  |
|  |  * Same input -> same output (always)                                |  |
|  |  * No side effects                                                   |  |
|  |  * No external state access                                          |  |
|  |  * Easy to test, reason about, parallelize                           |  |
|  |                                                                      |  |
|  |  Examples:                                                           |  |
|  |  * Math functions: add(a, b), sqrt(x)                                |  |
|  |  * String manipulation: toUpperCase(s)                               |  |
|  |  * Data transformation: map, filter, reduce                          |  |
|  |                                                                      |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|  IMPURE FUNCTION                                                           |
|  +----------------------------------------------------------------------+  |
|  |                                                                      |  |
|  |                  +-----------+                                       |  |
|  |  External <----> |  Function | <----> External                      |  |
|  |  State           |           |        I/O                            |  |
|  |                  +-----------+                                       |  |
|  |    Input ----------->| ^-----------> Output                          |  |
|  |                      | |                                             |  |
|  |                      v |                                             |  |
|  |                  Side Effects                                        |  |
|  |                                                                      |  |
|  |  * Result depends on external state                                  |  |
|  |  * May modify external state                                         |  |
|  |  * Hard to test, reason about                                        |  |
|  |                                                                      |  |
|  |  Examples:                                                           |  |
|  |  * getCurrentTime(), random()                                        |  |
|  |  * Database read/write                                               |  |
|  |  * HTTP requests                                                     |  |
|  |  * Console log                                                       |  |
|  |                                                                      |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Примеры кода

```kotlin
// ---- Impure: зависит от внешнего состояния ----

var total = 0

fun addToTotal(x: Int): Int {
    total += x          // Side effect: изменяет внешнее состояние
    return total
}

// ---- Impure: недетерминированная ----

fun getRandomGreeting(): String {
    val greetings = listOf("Hello", "Hi", "Hey")
    return greetings.random()   // Разный результат каждый раз
}

// ---- Pure: same input -> same output ----

fun add(a: Int, b: Int): Int = a + b

// ---- Pure: нет side effects ----

fun greet(name: String, greeting: String = "Hello"): String =
    "$greeting, $name!"

// ---- Pure: трансформация данных ----

data class Item(val name: String, val price: Double)

fun calculateTotal(items: List<Item>): Double =
    items.sumOf { it.price }

// ---- Pure: возвращает новый список вместо мутации ----

// Impure: модифицирует входные данные
fun addItemBad(list: MutableList<String>, item: String) {
    list.add(item)  // Side effect!
}

// Pure: возвращает новый список
fun addItem(list: List<String>, item: String): List<String> =
    list + item
```

### Разделение pure и impure кода

Ключевая идея FP --- вытеснять side effects на границы системы, оставляя ядро чистым:

```kotlin
// ---- Ядро: pure functions ----

data class User(val name: String, val email: String)
data class ValidationError(val field: String, val message: String)

fun validateEmail(email: String): List<ValidationError> =
    if ("@" !in email) listOf(ValidationError("email", "Invalid email"))
    else emptyList()

fun validateUser(user: User): List<ValidationError> =
    validateEmail(user.email) +
    if (user.name.isBlank()) listOf(ValidationError("name", "Name required"))
    else emptyList()

// ---- Граница: impure shell ----

suspend fun registerUser(user: User, repo: UserRepository): Result<User> {
    val errors = validateUser(user)         // Pure
    if (errors.isNotEmpty()) {
        return Result.failure(                // Pure
            IllegalArgumentException(errors.joinToString { it.message })
        )
    }
    return runCatching { repo.save(user) }  // Impure: I/O
}
```

---

## Immutability

```
+----------------------------------------------------------------------------+
|                         IMMUTABILITY                                       |
+----------------------------------------------------------------------------+
|                                                                            |
|  MUTABLE (dangerous)                                                       |
|  +----------------------------------------------------------------------+  |
|  |                                                                      |  |
|  |  list = [1, 2, 3]                                                    |  |
|  |         |                                                            |  |
|  |         v                                                            |  |
|  |  +-----------+      list.add(4)                                      |  |
|  |  | 1, 2, 3   |  ---------------------->  +---------------+           |  |
|  |  +-----------+       (mutated!)          | 1, 2, 3, 4    |           |  |
|  |                                          +---------------+           |  |
|  |                                                                      |  |
|  |  Problems:                                                           |  |
|  |  * Shared state bugs                                                 |  |
|  |  * Hard to track changes                                             |  |
|  |  * Thread safety issues                                              |  |
|  |  * Defensive copying needed                                          |  |
|  |                                                                      |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|  IMMUTABLE (safe)                                                          |
|  +----------------------------------------------------------------------+  |
|  |                                                                      |  |
|  |  list = [1, 2, 3]                                                    |  |
|  |         |                                                            |  |
|  |         v                                                            |  |
|  |  +-----------+      newList = list + [4]                             |  |
|  |  | 1, 2, 3   |  ---------------------------->  (unchanged!)          |  |
|  |  +-----------+                                                       |  |
|  |                                          +---------------+           |  |
|  |                         (new)            | 1, 2, 3, 4    |           |  |
|  |                                          +---------------+           |  |
|  |                                                                      |  |
|  |  Benefits:                                                           |  |
|  |  * Thread safe by default                                            |  |
|  |  * No unexpected mutations                                           |  |
|  |  * Easy to reason about                                              |  |
|  |  * Time travel / undo easy                                           |  |
|  |                                                                      |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Примеры кода

```kotlin
// ---- Kotlin: val по умолчанию, List вместо MutableList ----

val numbers: List<Int> = listOf(1, 2, 3)    // Immutable
val newNumbers = numbers + 4                  // Новый список: [1, 2, 3, 4]
// numbers по-прежнему [1, 2, 3]

// ---- Data classes с copy ----

data class User(val name: String, val age: Int)

val user = User("Alice", 30)
val updatedUser = user.copy(age = 31)   // Новый экземпляр
// user остаётся User("Alice", 30)

// ---- Sealed class для immutable иерархий ----

sealed class Shape {
    data class Circle(val radius: Double) : Shape()
    data class Rectangle(val width: Double, val height: Double) : Shape()
    data object Empty : Shape()
}

fun area(shape: Shape): Double = when (shape) {
    is Shape.Circle -> Math.PI * shape.radius * shape.radius
    is Shape.Rectangle -> shape.width * shape.height
    Shape.Empty -> 0.0
}

// ---- Persistent collections (эффективные immutable) ----
// kotlinx.collections.immutable

// import kotlinx.collections.immutable.*

// val persistentList = persistentListOf(1, 2, 3)
// val newList = persistentList.add(4)   // Structural sharing: O(log N)
// persistentList по-прежнему [1, 2, 3]
```

### Когда мутабельность допустима

```kotlin
// ---- Локальная мутабельность внутри pure функции ----

fun processItems(items: List<String>): List<String> {
    // Внутри функции мутабельность OK:
    // она не "утекает" наружу
    val result = mutableListOf<String>()
    for (item in items) {
        if (item.isNotBlank()) {
            result.add(item.trim().uppercase())
        }
    }
    return result   // Снаружи --- immutable List
}

// ---- Более идиоматичный вариант: ----

fun processItemsIdiomatic(items: List<String>): List<String> =
    items.filter { it.isNotBlank() }
         .map { it.trim().uppercase() }

// ---- buildList для чистого создания коллекций ----

fun createReport(data: List<Record>): List<String> = buildList {
    add("=== Report ===")
    for (record in data) {
        add("${record.name}: ${record.value}")
    }
    add("=== End ===")
}
```

---

## Higher-Order Functions

```kotlin
// ---- Higher-order: принимает функцию как аргумент ----

fun <T> applyTwice(value: T, f: (T) -> T): T = f(f(value))

val result = applyTwice(5) { it + 1 }   // 7

// ---- Higher-order: возвращает функцию (closure) ----

fun multiplier(factor: Int): (Int) -> Int = { x -> x * factor }

val double = multiplier(2)
val triple = multiplier(3)

println(double(5))   // 10
println(triple(5))   // 15

// ---- Стандартные higher-order функции Kotlin ----

val numbers = listOf(1, 2, 3, 4, 5)

// map: трансформировать каждый элемент
val squared = numbers.map { it * it }          // [1, 4, 9, 16, 25]

// filter: оставить элементы по предикату
val evens = numbers.filter { it % 2 == 0 }    // [2, 4]

// reduce: свернуть все элементы в одно значение
val sum = numbers.reduce { acc, n -> acc + n } // 15

// fold: reduce с начальным значением
val product = numbers.fold(1) { acc, n -> acc * n }  // 120

// flatMap: развернуть вложенные коллекции
val nested = listOf(listOf(1, 2), listOf(3, 4))
val flat = nested.flatMap { it }               // [1, 2, 3, 4]

// groupBy: группировка
data class Person(val name: String, val city: String)

val people = listOf(
    Person("Alice", "Moscow"),
    Person("Bob", "SPb"),
    Person("Charlie", "Moscow"),
)

val byCity = people.groupBy { it.city }
// {Moscow=[Alice, Charlie], SPb=[Bob]}

// associate: создание Map из списка
val nameToCity = people.associate { it.name to it.city }
// {Alice=Moscow, Bob=SPb, Charlie=Moscow}
```

### Написание собственных higher-order функций

```kotlin
// ---- Retry с функциональной стратегией ----

fun <T> retry(
    times: Int,
    delay: Long = 1000L,
    shouldRetry: (Exception) -> Boolean = { true },
    block: () -> T
): T {
    var lastException: Exception? = null
    repeat(times) { attempt ->
        try {
            return block()
        } catch (e: Exception) {
            lastException = e
            if (!shouldRetry(e) || attempt == times - 1) throw e
            Thread.sleep(delay * (attempt + 1))  // linear backoff
        }
    }
    throw lastException!!
}

// Использование:
val data = retry(times = 3, shouldRetry = { it is java.io.IOException }) {
    fetchFromNetwork("https://api.example.com/data")
}
```

---

## Function Composition

```
+----------------------------------------------------------------------------+
|                     FUNCTION COMPOSITION                                   |
+----------------------------------------------------------------------------+
|                                                                            |
|  Building complex functions from simple ones                               |
|                                                                            |
|  f(x) = x + 1                                                             |
|  g(x) = x * 2                                                             |
|  h(x) = x * x                                                             |
|                                                                            |
|  Composition: (h . g . f)(x) = h(g(f(x)))                                 |
|                                                                            |
|  Example: x = 3                                                            |
|  +-----+     +-----+     +-----+     +-----+                              |
|  |  3  | --> | f   | --> | g   | --> | h   | -->  64                       |
|  |     |     | +1  |     | *2  |     | ^2  |                               |
|  +-----+     +-----+     +-----+     +-----+                              |
|                  4           8          64                                  |
|                                                                            |
|  Benefits:                                                                 |
|  * Reusable small functions                                                |
|  * Easy to test individually                                               |
|  * Clear data flow                                                         |
|  * Declarative style                                                       |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Композиция в Kotlin

```kotlin
// ---- Базовая композиция через оператор ----

infix fun <A, B, C> ((B) -> C).compose(other: (A) -> B): (A) -> C =
    { a -> this(other(a)) }

infix fun <A, B, C> ((A) -> B).andThen(other: (B) -> C): (A) -> C =
    { a -> other(this(a)) }

val addOne: (Int) -> Int = { it + 1 }
val double: (Int) -> Int = { it * 2 }
val square: (Int) -> Int = { it * it }

// compose: справа налево (математическая нотация)
val composed = square compose double compose addOne
println(composed(3))  // square(double(addOne(3))) = square(8) = 64

// andThen: слева направо (pipeline, более интуитивно)
val piped = addOne andThen double andThen square
println(piped(3))     // square(double(addOne(3))) = 64

// ---- Method chaining: тот же принцип в коллекциях ----

data class Order(val items: List<Item>, val userId: String)

fun processOrders(orders: List<Order>): Map<String, Double> =
    orders
        .filter { it.items.isNotEmpty() }
        .groupBy { it.userId }
        .mapValues { (_, userOrders) ->
            userOrders.flatMap { it.items }.sumOf { it.price }
        }
```

### Currying и Partial Application

```kotlin
// ---- Currying: разбиение многоаргументной функции ----

fun <A, B, C> ((A, B) -> C).curried(): (A) -> (B) -> C =
    { a -> { b -> this(a, b) } }

val add: (Int, Int) -> Int = { a, b -> a + b }
val curriedAdd = add.curried()

val add5 = curriedAdd(5)      // Partial application
println(add5(3))               // 8

// ---- Практичный пример: настраиваемый форматтер ----

fun formatter(prefix: String): (String) -> (Any) -> String =
    { tag -> { value -> "$prefix [$tag] $value" } }

val logFormatter = formatter("LOG")
val errorLog = logFormatter("ERROR")
val infoLog = logFormatter("INFO")

println(errorLog("File not found"))    // LOG [ERROR] File not found
println(infoLog("Server started"))     // LOG [INFO] Server started
```

---

## Common FP Patterns

### Map, Filter, Reduce --- декларативная обработка данных

```kotlin
data class User(
    val name: String,
    val age: Int,
    val isActive: Boolean,
)

val users = listOf(
    User("Alice", 25, true),
    User("Bob", 30, false),
    User("Charlie", 35, true),
    User("Diana", 17, true),
)

// Имена активных совершеннолетних пользователей
val result: List<String> = users
    .filter { it.isActive }
    .filter { it.age >= 18 }
    .map { it.name }
// [Alice, Charlie]

// Средний возраст активных
val avgAge: Double = users
    .filter { it.isActive }
    .map { it.age }
    .average()

// Группировка: активные vs неактивные
val partitioned: Map<Boolean, List<User>> =
    users.groupBy { it.isActive }

// Partition --- специальный случай для двух групп
val (active, inactive) = users.partition { it.isActive }
```

### Option/Maybe --- null safety как встроенный FP

В отличие от языков, требующих библиотечный `Maybe`/`Option` тип, в Kotlin null-safety встроена в систему типов:

```kotlin
data class Address(val city: String?, val zip: String?)
data class UserProfile(val name: String, val address: Address?)

fun getCity(user: UserProfile?): String =
    user?.address?.city ?: "Unknown"

// ---- Safe call chain через let ----

fun processUserCity(user: UserProfile?) {
    user?.address?.city?.let { city ->
        println("User lives in $city")
    }
}

// ---- Цепочка трансформаций с null-safety ----

fun formatAddress(user: UserProfile?): String? =
    user?.address?.let { address ->
        val city = address.city ?: return@let null
        val zip = address.zip ?: return@let null
        "$city, $zip"
    }

// ---- Null-safe коллекции ----

val names: List<String?> = listOf("Alice", null, "Bob", null, "Charlie")

val validNames: List<String> = names.filterNotNull()     // [Alice, Bob, Charlie]
val firstValid: String = names.firstNotNullOf { it }      // Alice
val firstValidOrNull: String? = names.firstNotNullOfOrNull { it }
```

### Result --- функциональная обработка ошибок

```kotlin
// ---- Kotlin Result для функциональной обработки ошибок ----

fun parseAge(input: String): Result<Int> = runCatching {
    val age = input.toInt()
    require(age in 0..150) { "Age must be between 0 and 150" }
    age
}

fun processInput(input: String): String =
    parseAge(input)
        .map { age -> "Age: $age" }
        .recover { error -> "Error: ${error.message}" }
        .getOrDefault("Unknown")

// ---- Цепочка Result ----

data class Config(val host: String, val port: Int)

fun readHost(): Result<String> = runCatching { System.getenv("HOST") ?: error("HOST not set") }
fun readPort(): Result<Int> = runCatching { System.getenv("PORT")?.toInt() ?: error("PORT not set") }

fun loadConfig(): Result<Config> =
    readHost().mapCatching { host ->
        val port = readPort().getOrThrow()
        Config(host, port)
    }
```

---

## Kotlin Sequences: ленивые вычисления

Sequences --- ленивые коллекции Kotlin. В отличие от обычных коллекций, которые создают промежуточные списки на каждом шаге, Sequence вычисляет элементы по одному по мере необходимости.

```
+----------------------------------------------------------------------------+
|              COLLECTIONS (eager) vs SEQUENCES (lazy)                       |
+----------------------------------------------------------------------------+
|                                                                            |
|  COLLECTIONS: все элементы, шаг за шагом                                   |
|                                                                            |
|  [1, 2, 3, 4, 5]                                                          |
|       |                                                                    |
|       v  filter { it > 2 }   -- создаёт промежуточный List                |
|  [3, 4, 5]                                                                 |
|       |                                                                    |
|       v  map { it * 10 }     -- создаёт ещё один промежуточный List       |
|  [30, 40, 50]                                                              |
|       |                                                                    |
|       v  first()                                                           |
|  30                                                                        |
|                                                                            |
|  Итого: обработано 5 + 3 = 8 операций, создано 2 промежуточных списка     |
|                                                                            |
|  -----                                                                     |
|                                                                            |
|  SEQUENCES: по одному элементу, весь pipeline                              |
|                                                                            |
|  1 -> filter(1 > 2)? NO  -> skip                                          |
|  2 -> filter(2 > 2)? NO  -> skip                                          |
|  3 -> filter(3 > 2)? YES -> map(3 * 10) = 30 -> first()? YES -> STOP!    |
|                                                                            |
|  Итого: обработано 3 элемента, 0 промежуточных списков                    |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Базовое использование

```kotlin
// ---- Eager: создаёт промежуточные коллекции ----

val result = (1..1_000_000)
    .filter { it % 2 == 0 }       // List из 500_000 элементов
    .map { it * it }                // Ещё один List из 500_000
    .take(10)                       // Ещё один List из 10
    .toList()

// ---- Lazy: ноль промежуточных коллекций ----

val resultLazy = (1..1_000_000)
    .asSequence()                   // Переключаемся на Sequence
    .filter { it % 2 == 0 }        // Ленивая операция
    .map { it * it }                // Ленивая операция
    .take(10)                       // Ленивая операция
    .toList()                       // Terminal: запускает вычисление

// ---- Бесконечные последовательности ----

val fibonacci: Sequence<Long> = sequence {
    var a = 0L
    var b = 1L
    while (true) {
        yield(a)
        val next = a + b
        a = b
        b = next
    }
}

val first20Fib = fibonacci.take(20).toList()
// [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181]

// ---- Генерация данных ----

val randomPasswords: Sequence<String> = generateSequence {
    (1..12)
        .map { ('a'..'z').random() }
        .joinToString("")
}

val passwords = randomPasswords.take(5).toList()
```

### Когда использовать Sequence, а когда Collection

```kotlin
// ---- Collection: малый объём, одна операция ----
val names = listOf("Alice", "Bob", "Charlie")
val upper = names.map { it.uppercase() }  // Collection --- OK

// ---- Sequence: большой объём, цепочка операций ----
val logLines: List<String> = readLogFile()  // 1_000_000 строк

val errors = logLines
    .asSequence()
    .filter { "ERROR" in it }
    .map { parseLogEntry(it) }
    .filter { it.timestamp > cutoffDate }
    .sortedByDescending { it.severity }    // NB: sortedBy --- terminal-like
    .take(100)
    .toList()

// ---- Правило: asSequence() когда ----
// 1. Коллекция > ~1000 элементов
// 2. Цепочка из 2+ операций (filter + map + ...)
// 3. Нужен early termination (first, take, any, none)
// 4. Бесконечные или очень большие источники данных
```

---

## Scope Functions для FP-композиции

Scope functions --- идиоматичный инструмент Kotlin для функционального стиля: объект-контекст доступен через `it` или `this`, а результат --- либо сам объект, либо результат лямбды.

```
+----------------------------------------------------------------------------+
|                     SCOPE FUNCTIONS                                        |
+----------------------------------------------------------------------------+
|                                                                            |
|  Function   | Object ref | Return value | Use case                        |
|  -----------|------------|--------------|----------------------------       |
|  let        | it         | Lambda result| Null-safety, transform          |
|  run        | this       | Lambda result| Object config + compute         |
|  with       | this       | Lambda result| Grouping calls on object        |
|  apply      | this       | Object (this)| Object configuration            |
|  also       | it         | Object (it)  | Side effects (logging, debug)   |
|                                                                            |
+----------------------------------------------------------------------------+
```

```kotlin
// ---- let: null-safe трансформация ----

val length: Int? = readLine()?.let { input ->
    println("Processing: $input")
    input.trim().length
}

// ---- let: сужение scope переменной ----

val mapped = listOf(1, 2, 3).first().let { first ->
    "First element is $first"
}

// ---- run: конфигурация + вычисление ----

val result = StringBuilder().run {
    append("Hello")
    append(", ")
    append("World")
    toString()
}  // "Hello, World"

// ---- with: группировка вызовов (не extension) ----

data class Report(var title: String = "", var body: String = "", var footer: String = "")

val report = Report()
with(report) {
    title = "Monthly Report"
    body = "Revenue increased by 15%"
    footer = "Generated at ${java.time.LocalDate.now()}"
}

// ---- apply: конфигурация объекта, возвращает сам объект ----

data class ServerConfig(
    var host: String = "",
    var port: Int = 0,
    var maxConnections: Int = 100,
)

val config = ServerConfig().apply {
    host = "localhost"
    port = 8080
    maxConnections = 500
}

// ---- also: side effects без изменения цепочки ----

val processedUsers = users
    .filter { it.isActive }
    .also { println("Active users: ${it.size}") }   // Логирование
    .map { it.name.uppercase() }
    .also { println("Processed names: $it") }         // Отладка

// ---- Композиция scope functions ----

fun createUser(name: String, email: String): User? =
    User(name, email)
        .takeIf { it.email.contains("@") }
        ?.also { println("Created user: ${it.name}") }

// ---- takeIf / takeUnless --- функциональные фильтры ----

val validAge: Int? = readLine()
    ?.toIntOrNull()
    ?.takeIf { it in 0..150 }

val nonBlankName: String? = name.takeUnless { it.isBlank() }
```

---

## Inline Functions и Reified Generics

`inline` --- ключевой механизм Kotlin для FP без overhead. Компилятор подставляет тело inline-функции в место вызова, устраняя создание объекта-лямбды.

### inline: зачем нужен

```kotlin
// ---- Без inline: каждый вызов создаёт объект Function ----

fun <T> measureTime(block: () -> T): T {
    val start = System.nanoTime()
    val result = block()         // block --- это объект Function0<T>
    println("Took ${System.nanoTime() - start}ns")
    return result
}

// ---- С inline: лямбда подставляется в место вызова ----

inline fun <T> measureTimeInline(block: () -> T): T {
    val start = System.nanoTime()
    val result = block()         // Код лямбды подставляется сюда
    println("Took ${System.nanoTime() - start}ns")
    return result
}

// Вызов:
val data = measureTimeInline {
    loadFromDatabase()
}
// Компилятор превращает в:
// val start = System.nanoTime()
// val data = loadFromDatabase()
// println("Took ${System.nanoTime() - start}ns")
```

### noinline и crossinline

```kotlin
inline fun execute(
    action: () -> Unit,                // Будет заинлайнена
    noinline callback: () -> Unit,     // НЕ будет заинлайнена (можно сохранить в переменную)
    crossinline transform: () -> String // Будет заинлайнена, но нельзя делать non-local return
) {
    action()

    // noinline: можно передать как объект
    val savedCallback = callback
    savedCallback()

    // crossinline: можно вызывать из другого lambda-контекста
    val wrapper = Runnable { println(transform()) }
    wrapper.run()
}

// ---- Практический пример: inline с non-local return ----

inline fun <T> List<T>.firstOrError(predicate: (T) -> Boolean): T {
    for (item in this) {
        if (predicate(item)) return item   // Non-local return из вызывающей функции!
    }
    throw NoSuchElementException("No matching element")
}
```

### Reified generics: доступ к типу в runtime

```kotlin
// ---- Без reified: type erasure, нужен Class<T> параметр ----

fun <T> parseJson(json: String, clazz: Class<T>): T =
    gson.fromJson(json, clazz)

val user = parseJson(jsonStr, User::class.java)  // Громоздко

// ---- С reified: тип доступен в runtime ----

inline fun <reified T> parseJson(json: String): T =
    gson.fromJson(json, T::class.java)

val user: User = parseJson(jsonStr)  // Чисто и типобезопасно

// ---- Reified: type-safe коллекции ----

inline fun <reified T> List<*>.filterByType(): List<T> =
    filterIsInstance<T>()

val mixed: List<Any> = listOf(1, "hello", 2.0, "world", 3)
val strings: List<String> = mixed.filterByType()   // [hello, world]
val ints: List<Int> = mixed.filterByType()          // [1, 3]

// ---- Reified: type-safe навигация (Android-пример) ----

inline fun <reified T : Activity> Context.startActivity(
    configIntent: Intent.() -> Unit = {}
) {
    val intent = Intent(this, T::class.java).apply(configIntent)
    startActivity(intent)
}

// Использование:
// startActivity<DetailActivity> { putExtra("id", 42) }
```

---

## Arrow: FP-библиотека для Kotlin

Arrow --- зрелая библиотека типизированного функционального программирования для Kotlin. Она предоставляет типы данных (`Either`, `Nel`, `Ior`) и операторы, дополняющие стандартную библиотеку.

### Either: функциональная обработка ошибок

```kotlin
import arrow.core.Either
import arrow.core.left
import arrow.core.right
import arrow.core.raise.either
import arrow.core.raise.ensure

// ---- Either вместо exceptions ----

sealed class AppError {
    data class NotFound(val id: String) : AppError()
    data class ValidationFailed(val message: String) : AppError()
    data class NetworkError(val cause: Throwable) : AppError()
}

fun findUser(id: String): Either<AppError, User> =
    if (id.isNotBlank()) {
        User(id, "Alice").right()
    } else {
        AppError.ValidationFailed("ID cannot be blank").left()
    }

fun getAddress(user: User): Either<AppError, Address> =
    user.address?.right()
        ?: AppError.NotFound("Address for ${user.name}").left()

// ---- Цепочка через flatMap ----

fun getUserCity(id: String): Either<AppError, String> =
    findUser(id)
        .flatMap { user -> getAddress(user) }
        .map { address -> address.city ?: "Unknown" }

// ---- Either DSL (Raise) --- более читаемый стиль ----

fun getUserCityDsl(id: String): Either<AppError, String> = either {
    val user = findUser(id).bind()
    val address = getAddress(user).bind()
    ensure(address.city != null) { AppError.NotFound("City") }
    address.city
}

// ---- Обработка результата ----

fun displayCity(id: String) {
    when (val result = getUserCity(id)) {
        is Either.Left -> println("Error: ${result.value}")
        is Either.Right -> println("City: ${result.value}")
    }

    // Или через fold:
    getUserCity(id).fold(
        ifLeft = { error -> println("Error: $error") },
        ifRight = { city -> println("City: $city") }
    )
}
```

### Nel (NonEmptyList): валидация с накоплением ошибок

```kotlin
import arrow.core.NonEmptyList
import arrow.core.raise.either
import arrow.core.raise.zipOrAccumulate

data class ValidatedUser(val name: String, val email: String, val age: Int)

fun validateName(name: String): Either<String, String> = either {
    ensure(name.isNotBlank()) { "Name is required" }
    ensure(name.length >= 2) { "Name too short" }
    name
}

fun validateEmail(email: String): Either<String, String> = either {
    ensure("@" in email) { "Invalid email" }
    email
}

fun validateAge(age: Int): Either<String, Int> = either {
    ensure(age in 0..150) { "Invalid age" }
    age
}

// Накопление всех ошибок, а не только первой
fun validateUser(
    name: String,
    email: String,
    age: Int
): Either<NonEmptyList<String>, ValidatedUser> = either {
    zipOrAccumulate(
        { validateName(name).bind() },
        { validateEmail(email).bind() },
        { validateAge(age).bind() },
    ) { validName, validEmail, validAge ->
        ValidatedUser(validName, validEmail, validAge)
    }
}
```

---

## Мифы и заблуждения

**Миф:** FP --- это только для академических языков вроде Haskell.

**Реальность:** Kotlin, Scala, Swift, TypeScript --- все mainstream-языки активно используют FP-паттерны. `map`/`filter`/`reduce` давно стали стандартом. Kotlin изначально спроектирован как мультипарадигменный язык с сильной FP-поддержкой.

**Миф:** Immutability медленная, потому что всё время копируешь данные.

**Реальность:** Persistent data structures используют structural sharing --- общие части не копируются. На практике разница в производительности минимальна, а бонусы thread-safety и предсказуемости огромны. Библиотека `kotlinx.collections.immutable` предоставляет эффективные persistent коллекции.

**Миф:** `inline` нужно ставить везде для производительности.

**Реальность:** `inline` увеличивает размер байткода (code bloat). Используйте его для функций с lambda-параметрами, scope functions, и для `reified` generics. Для обычных функций `inline` не даёт выигрыша и может навредить.

**Миф:** Sequence всегда быстрее Collection.

**Реальность:** Для малых коллекций и одиночных операций Collection быстрее из-за overhead ленивой инфраструктуры. Sequence выигрывает при больших данных (1000+ элементов) с цепочкой из 2+ операций, а также при early termination (`first`, `take`).

---

## Проверь себя

<details>
<summary>1. Почему pure functions легче тестировать?</summary>

**Ответ:**

**Pure functions:**
- Нет setup/teardown (no mocks needed)
- Deterministic: same input -> same output
- No hidden dependencies
- Можно тестировать в изоляции

```kotlin
// Pure: тестировать тривиально
fun calculateDiscount(price: Double, percent: Double): Double =
    price * (1 - percent / 100)

@Test
fun `discount calculated correctly`() {
    assertEquals(90.0, calculateDiscount(100.0, 10.0))
    assertEquals(100.0, calculateDiscount(200.0, 50.0))
}

// Impure: нужен мок
class OrderService(private val repo: OrderRepository) {
    fun getUserDiscount(userId: String): Double {
        val user = repo.findById(userId)   // Зависимость от внешней системы
        return user.discountPercent
    }
}

@Test
fun `impure needs mock`() {
    val mockRepo = mockk<OrderRepository>()
    every { mockRepo.findById("1") } returns User(discountPercent = 10.0)
    // ... сложный setup
}
```

</details>

<details>
<summary>2. Когда immutability --- плохая идея?</summary>

**Ответ:**

**Когда НЕ использовать:**

1. **Performance-critical внутренние циклы:**
   ```kotlin
   // Медленно: создаёт новый список на каждой итерации
   var result = emptyList<String>()
   for (item in items) {
       result = result + process(item)  // O(n) копирование на каждом шаге
   }

   // Быстро: локальная мутабельность
   val result = buildList {
       for (item in items) {
           add(process(item))
       }
   }
   ```

2. **Большие структуры данных** без persistent data structures

3. **Low-level код:** буферы, byte arrays, direct memory

**Best practice:** Immutable по умолчанию, mutable только когда профилирование показало необходимость.

</details>

<details>
<summary>3. Что такое referential transparency?</summary>

**Ответ:**

**Referential transparency** = можно заменить вызов функции на её результат без изменения поведения программы.

```kotlin
// Referentially transparent
fun add(a: Int, b: Int): Int = a + b

val x = add(2, 3) + add(2, 3)
// Можно заменить на:
val x2 = 5 + 5  // Эквивалентно

// НЕ referentially transparent
var count = 0
fun increment(): Int {
    count++
    return count
}

val y = increment() + increment()  // = 1 + 2 = 3
val y2 = 1 + 1  // = 2, НЕ эквивалентно!
```

**Benefit:** Позволяет компилятору оптимизировать, рассуждать о коде, кэшировать результаты.

</details>

<details>
<summary>4. Что такое Monad простыми словами?</summary>

**Ответ:**

**Monad** = паттерн для цепочки операций с "контейнером".

**Интуиция:**
- Box с значением внутри
- `map`: применить функцию к содержимому
- `flatMap`: применить функцию, которая возвращает такой же box

**Примеры в Kotlin:**
- `Result<T>`: контейнер "успех или ошибка"
- `List<T>`: контейнер с множеством значений
- `Flow<T>`: контейнер с асинхронным потоком значений
- `Either<E, A>` (Arrow): "ошибка типа E или результат типа A"
- `Nullable (T?)`: встроенный Maybe-тип

```kotlin
// Result как monad
val city: Result<String> = findUser(1)       // Result<User>
    .mapCatching { findAddress(it) }          // Result<Address>
    .map { it.city }                           // Result<String>
    .recover { "Unknown" }                     // Result<String>

// Kotlin nullable как monad (без обёртки)
val city2: String = findUserOrNull(1)         // User?
    ?.address                                  // Address?
    ?.city                                     // String?
    ?: "Unknown"                               // String
```

</details>

<details>
<summary>5. Когда использовать Sequence, а когда Collection?</summary>

**Ответ:**

| Критерий | Collection | Sequence |
|----------|-----------|----------|
| Размер данных | < 1000 элементов | > 1000 элементов |
| Число операций | 1 операция | 2+ в цепочке |
| Early termination | Не нужен | `first`, `take`, `any` |
| Бесконечные данные | Невозможно | `generateSequence`, `sequence {}` |
| Отладка | Легче (видны промежуточные) | Сложнее (ленивые) |

```kotlin
// Collection: маленький список, одна операция
val names = users.map { it.name }

// Sequence: большой файл, цепочка + first
val firstError = logLines.asSequence()
    .filter { "ERROR" in it }
    .map { parseLogEntry(it) }
    .firstOrNull { it.severity == Severity.CRITICAL }
```

</details>

<details>
<summary>6. Чем inline fun отличается от обычной fun для FP?</summary>

**Ответ:**

**Обычная функция с lambda-параметром:**
- Компилятор создаёт объект `Function` для каждой лямбды
- Вызов через `invoke()` --- виртуальный вызов
- Лямбда не может делать non-local return

**inline функция:**
- Тело функции и лямбды подставляется в место вызова
- Нет объекта Function, нет виртуального вызова
- Лямбда может делать non-local return
- С `reified` --- доступ к типу в runtime

```kotlin
// Без inline: создаётся объект Function1 при каждом вызове
fun transform(list: List<Int>, f: (Int) -> Int): List<Int> = list.map(f)

// С inline: код лямбды подставляется
inline fun transformInline(list: List<Int>, f: (Int) -> Int): List<Int> = list.map(f)
```

Все стандартные scope functions (`let`, `run`, `apply`, `also`, `with`), а также `map`, `filter`, `forEach` в stdlib --- `inline`.

</details>

---

## Практическое применение

1. **Начните с `val`:** переключите мышление на "данные не меняются". Используйте `var` только когда это действительно необходимо
2. **Разделяйте pure и impure:** ядро логики --- pure functions, side effects --- на границах (I/O, UI, network)
3. **Используйте `Sequence` для больших данных:** `asSequence()` перед цепочкой `filter`/`map`/`take`
4. **Scope functions по назначению:** `apply` --- конфигурация, `let` --- null-safety и трансформация, `also` --- логирование
5. **Arrow для сложного error handling:** `Either` вместо exceptions в domain-логике, `zipOrAccumulate` для валидации

---

## Связи

**[[programming-overview]]** --- Functional programming является одной из ключевых парадигм программирования наряду с императивной и объектно-ориентированной. Понимание FP расширяет "инструментарий мышления" разработчика: даже если основной язык --- OOP, функциональные приёмы (pure functions, immutability, composition) делают код чище и предсказуемее.

**[[solid-principles]]** --- Принципы чистого кода и FP взаимно усиливают друг друга. Single Responsibility (SRP) естественно вытекает из pure functions --- каждая функция делает ровно одно. Open/Closed Principle реализуется через composition: расширяем поведение, комбинируя функции. Dependency Inversion в FP выражается через higher-order functions --- вместо наследования передаём стратегию как аргумент.

**[[design-patterns-overview]]** --- Многие GoF-паттерны в FP становятся тривиальными или исчезают вовсе. Strategy Pattern --- это higher-order function. Observer Pattern заменяется reactive streams (`Flow`). Decorator --- это function composition. Template Method --- higher-order function с lambda-"дырками".

**[[concurrency-fundamentals]]** --- Immutability и pure functions устраняют race conditions по определению: если данные нельзя изменить, нет конфликтов при параллельном доступе. Functional подход к concurrency --- основа Kotlin coroutines и Flow.

---

## Источники

Abelson H., Sussman G.J. (1996). *"Structure and Interpretation of Computer Programs."* --- Фундаментальный учебник MIT по программированию через призму Lisp. Учит думать о вычислениях как о композиции абстракций; формирует "функциональное мышление" с нуля.

Hughes J. (1989). *"Why Functional Programming Matters."* --- Классический paper, объясняющий почему FP важен для модульности. Higher-order functions и lazy evaluation как инструменты композиции.

Chiusano P., Bjarnason R. (2014). *"Functional Programming in Scala."* --- "Red Book", практическое введение в FP. Пошагово строит абстракции от pure functions до монад; отлично подходит для разработчиков с OOP-фоном.

Normand E. (2021). *"Grokking Simplicity."* --- Практическое руководство по применению FP-принципов в повседневной разработке. Фокус на разделение actions, calculations и data.

Vermeulen M. et al. (2024). *"Functional Programming in Kotlin."* --- Адаптация "Red Book" для Kotlin. Охватывает Arrow, Either, IO и typed FP в контексте Kotlin-экосистемы.

- [Kotlin Lambdas and Higher-Order Functions](https://kotlinlang.org/docs/lambdas.html) --- официальная документация по лямбдам и higher-order functions
- [Kotlin Sequences](https://kotlinlang.org/docs/sequences.html) --- ленивые коллекции, API, когда использовать
- [Kotlin Inline Functions](https://kotlinlang.org/docs/inline-functions.html) --- inline, noinline, crossinline, reified
- [Arrow-kt.io](https://arrow-kt.io/) --- FP-библиотека для Kotlin: Either, Raise DSL, Optics
- [Effective Kotlin: Prefer Sequences](https://kt.academy/article/ek-sequence) --- Marcin Moskala о Sequence vs Collection с бенчмарками

---

---

## Ключевые карточки

Что такое pure function и какие два свойства она гарантирует?
?
1) Детерминизм: для одинаковых входов всегда возвращает одинаковый результат. 2) Отсутствие side effects: не изменяет внешнее состояние, не делает I/O. Примеры: `add(a, b)`, `String.uppercase()`. Контрпримеры: `System.currentTimeMillis()`, `Random.nextInt()`.

Что такое referential transparency?
?
Свойство выражения, позволяющее заменить вызов функции на её результат без изменения поведения программы. Пример: `add(2, 3)` можно заменить на `5` везде. Нарушается при side effects.

Почему immutable данные thread-safe по умолчанию?
?
Если данные нельзя изменить после создания, невозможна ситуация, когда один поток пишет, а другой одновременно читает (race condition). Нет необходимости в блокировках и синхронизации. Любое "изменение" создаёт новый объект через `copy()`.

Что такое higher-order function?
?
Функция, которая принимает другую функцию как аргумент и/или возвращает функцию как результат. Примеры: `map`, `filter`, `reduce`, `let`, `apply`. Позволяет параметризовать поведение: вместо наследования передаём стратегию как lambda.

Что такое closure и что она "захватывает"?
?
Closure --- функция вместе с captured environment (лексической средой, в которой была создана). Захватывает переменные из внешнего scope. Пример: `fun multiplier(factor: Int): (Int) -> Int = { x -> x * factor }` --- `factor` захвачен из внешней функции.

Что такое Monad простыми словами?
?
Паттерн для цепочки операций с "контейнером": box с значением, `map` для трансформации содержимого, `flatMap` для цепочки операций, возвращающих такой же box. В Kotlin: `Result<T>`, `List<T>`, `Flow<T>`, `Either<E, A>` (Arrow), nullable `T?`.

Когда Sequence выгоднее Collection?
?
При больших данных (1000+ элементов) с цепочкой из 2+ операций, при early termination (`first`, `take`, `any`), и для бесконечных последовательностей. Для малых коллекций и одиночных операций Collection быстрее из-за overhead ленивой инфраструктуры.

Зачем нужен inline для FP-функций в Kotlin?
?
`inline` устраняет overhead лямбд: нет создания объекта `Function`, нет виртуального вызова `invoke()`. Позволяет non-local return из лямбды. С `reified` --- доступ к типу в runtime. Все stdlib scope functions и коллекционные операторы --- `inline`.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[error-handling]] | Result/Either типы из FP для обработки ошибок |
| Углубиться | [[kotlin-functional]] | Практическое применение FP в Kotlin: lambdas, sequences, scope functions |
| Смежная тема | [[concurrency-fundamentals]] | Immutability и pure functions устраняют race conditions |
| Android | [[android-mvi-deep-dive]] | Reducer как pure function в MVI-архитектуре |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

*Проверено: 2026-02-19*
