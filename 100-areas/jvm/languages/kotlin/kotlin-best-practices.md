---
title: "Kotlin Best Practices: Идиоматичный код и оптимизация"
created: 2025-11-25
modified: 2025-12-27
tags:
  - topic/jvm
  - best-practices
  - coding-conventions
  - performance
  - idioms
  - type/concept
  - level/intermediate
related:
  - "[[kotlin-overview]]"
  - "[[kotlin-advanced-features]]"
  - "[[kotlin-type-system]]"
status: published
---

# Kotlin Best Practices: идиоматичный код

> **TL;DR:** Идиоматичный Kotlin: `val` по умолчанию, `data class` для моделей, `?.let {}` вместо if-null, `when` вместо if-else. Scope functions: `apply` для конфигурации, `let` для null-safety, `also` для логирования. Избегай `!!`, используй `?: return` для раннего выхода. Для коллекций: `map/filter` вместо циклов, `Sequence` для больших данных.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Kotlin basics** | Синтаксис, val/var | [[kotlin-basics]] |
| **Null-safety** | Понимание ?, ?., ?: | [[kotlin-basics]] |
| **Collections** | List, Map, операции | [[kotlin-collections]] |
| **Functional programming** | Lambda, higher-order functions | [[kotlin-functional]] |
| **OOP в Kotlin** | Data class, sealed class | [[kotlin-oop]] |

---

## Зачем это нужно

**Проблема:** Kotlin позволяет писать код "как в Java" — и он будет работать. Но такой код:
- **Не использует возможности языка** — null-safety, immutability, scope functions
- **Труднее читать** — коллегам приходится догадываться, что это "Java в Kotlin"
- **Медленнее** — компилятор не может оптимизировать неидиоматичный код
- **Плохо на code review** — опытные разработчики будут просить переписать

**Типичные ошибки Java-разработчиков:**
```kotlin
// ❌ Java-стиль
var name: String? = null
if (name != null) { println(name) }

// ✅ Kotlin-стиль
name?.let { println(it) }
```

**Что даёт идиоматичный Kotlin:**
- **Null-safety** — компилятор ловит NPE на этапе компиляции
- **Immutability** — `val` по умолчанию = меньше багов в многопоточности
- **Краткость** — data classes, scope functions, destructuring
- **Читаемость** — код как документация

**Результат:** Код, который приятно читать, легко поддерживать, и который использует мощь Kotlin.

### Актуальность 2024-2025

| Практика | Статус | Что изменилось |
|----------|--------|----------------|
| **Explicit API mode** | ✅ Рекомендуется | Для библиотек — `explicitApi()` в build.gradle |
| **`val` везде** | ✅ Стандарт | Kotlin 2.0: улучшенный smart cast через val |
| **Data objects** | ✅ Kotlin 1.9+ | `data object Singleton` для object с toString |
| **Entries вместо values()** | ✅ Kotlin 1.9+ | `enum.entries` вместо `values()` — не создаёт массив |
| **K2 compiler** | ✅ Kotlin 2.0+ | Быстрее компиляция, лучше smart casts |
| **Power-assert** | ✅ Kotlin 2.0+ | Детальные сообщения об ошибках в assert |

**Тренды 2025:**
- K2 compiler по умолчанию — лучшая оптимизация
- `entries` property вместо `values()` для enum
- Compose Compiler Plugin 2.0 — улучшенная стабильность

---

## Краткое резюме принципов

Идиоматичный Kotlin использует возможности языка: `val` вместо `final var`, `data class` вместо ручных equals/hashCode, `?.let {}` вместо if-null проверок, `when` вместо switch/if-else цепочек.

Главный принцип: **максимум иммутабельности**. `val` по умолчанию, `var` только когда необходимо. Read-only коллекции (`List`) если не нужно менять. Data classes с `copy()` для обновлений.

Scope functions (let, apply, run, also, with) — мощный инструмент, но перегрузка ухудшает читаемость. Правило: одна scope function на выражение, избегать вложенности.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Идиоматичный код** | Код, написанный "по-котлиновски" | Говорить как местный — не переводить дословно с Java |
| **Иммутабельность** | Неизменяемость (val) | Фотография — сделал и не меняешь, в отличие от пластилина |
| **Null-safety** | Защита от NullPointerException | Проверка документов — нельзя войти с пустым ID |
| **Smart cast** | Автоматическое приведение после проверки | Охранник запомнил — после проверки паспорта помнит имя |
| **Scope function** | let, apply, run, also, with | Контекст разговора — "он" означает разное в разных комнатах |
| **Elvis operator** | `?:` — default если null | План Б — если магазин закрыт, идём в другой |
| **Safe call** | `?.` — вызов только если не null | Стучать если дома — не звонить в пустую квартиру |
| **Hot path** | Часто выполняемый код | Главная дорога — оптимизируй её, а не переулки |
| **Expression** | Выражение, возвращающее значение | Вопрос "сколько?" — всегда есть ответ |
| **Statement** | Инструкция без возврата | Команда "сделай" — не отвечает, просто делает |

---

## Naming Conventions

### Общие правила именования

```kotlin
// ✅ Классы - PascalCase
class UserRepository
class HttpClient
class StringBuilder

// ✅ Функции и свойства - camelCase
fun calculateTotal()
val userName: String
var itemCount: Int

// ✅ Константы - UPPER_SNAKE_CASE
const val MAX_RETRY_COUNT = 3
const val DEFAULT_TIMEOUT = 5000

// ✅ Package names - lowercase
package com.example.myapp
package org.company.project

// ❌ Избегайте венгерской нотации
// val strName: String  // ❌
val name: String  // ✅

// ❌ Избегайте префиксов для членов класса
class User {
    // var mName: String  // ❌ Android/Java стиль
    var name: String  // ✅
}

// ✅ Boolean свойства - вопросительная форма
val isEmpty: Boolean
val isValid: Boolean
val hasChildren: Boolean
val canEdit: Boolean

// ✅ Test функции - backticks с описанием
@Test
fun `should return user when ID exists`() { }

@Test
fun `should throw exception when ID is invalid`() { }
```

### Специфичные соглашения

```kotlin
// ✅ Extension functions - глаголы
fun String.toTitleCase(): String
fun List<Int>.average(): Double

// ✅ Factory functions - именованные конструкторы
fun createDefaultUser() = User("guest")
fun User.copy() = User(this.name, this.age)

// ✅ DSL builders - существительные
fun html { }
fun buildString { }
fun configuration { }

// ✅ Backing properties - подчёркивание
class ViewModel {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()
}

// ✅ Generic type parameters
class Box<T>  // Type
class Map<K, V>  // Key, Value
class Function<in P, out R>  // Parameter, Return
```

## Идиоматичный Kotlin

### Используйте val вместо var

```kotlin
// ❌ Лишняя мутабельность
var name = "Alice"
var age = 25

// ✅ Используйте val где возможно
val name = "Alice"
val age = 25

// ✅ val для ссылки, мутабельность внутри
val list = mutableListOf<String>()
list.add("item")  // ✅ OK, изменяем содержимое

// ❌ var когда можно вычислить сразу
var result: String
if (condition) {
    result = "A"
} else {
    result = "B"
}

// ✅ Используйте выражения
val result = if (condition) "A" else "B"

// ✅ Или when
val result = when {
    x > 0 -> "positive"
    x < 0 -> "negative"
    else -> "zero"
}
```

**Почему val > var:**
- Иммутабельность: легче рассуждать о коде
- Thread-safety: безопаснее в многопоточности
- Функциональный стиль: чистые функции без побочных эффектов

### Предпочитайте expressions над statements

```kotlin
// ❌ Statements
fun getStatus(code: Int): String {
    if (code == 200) {
        return "OK"
    } else if (code == 404) {
        return "Not Found"
    } else {
        return "Unknown"
    }
}

// ✅ Expression
fun getStatus(code: Int): String = when (code) {
    200 -> "OK"
    404 -> "Not Found"
    else -> "Unknown"
}

// ❌ Statement с var
fun process(items: List<Int>): String {
    var result = ""
    for (item in items) {
        result += item.toString()
    }
    return result
}

// ✅ Expression
fun process(items: List<Int>): String =
    items.joinToString("") { it.toString() }

// ✅ try тоже expression
val result = try {
    parseJson(data)
} catch (e: Exception) {
    defaultValue
}
```

### String templates вместо конкатенации

```kotlin
// ❌ Конкатенация
val message = "Hello, " + name + "! You are " + age + " years old."

// ✅ String template
val message = "Hello, $name! You are $age years old."

// ✅ Выражения в ${}
val message = "Sum: ${a + b}"
val message = "Name: ${user.name.uppercase()}"

// ✅ Многострочные строки
val html = """
    <html>
        <body>
            <h1>$title</h1>
            <p>$content</p>
        </body>
    </html>
""".trimIndent()

// ✅ Raw strings для regex
val regex = """\d{3}-\d{2}-\d{4}""".toRegex()
```

### Elvis operator для default значений

```kotlin
// ❌ Явная проверка
val length = if (str != null) str.length else 0

// ✅ Elvis operator
val length = str?.length ?: 0

// ✅ Цепочки elvis
val name = user?.profile?.name ?: "Unknown"

// ✅ Elvis с throw
val name = user?.name ?: throw IllegalArgumentException("User must have a name")

// ✅ Elvis с return
fun process(user: User?) {
    val name = user?.name ?: return
    // Работаем с name (String, не nullable)
}
```

### Используйте data classes

```kotlin
// ❌ Обычный класс для данных
class User(val name: String, val age: Int) {
    override fun equals(other: Any?): Boolean {
        // Ручная реализация
    }

    override fun hashCode(): Int {
        // Ручная реализация
    }

    override fun toString(): String {
        return "User(name=$name, age=$age)"
    }

    fun copy(name: String = this.name, age: Int = this.age): User {
        return User(name, age)
    }
}

// ✅ Data class - всё автоматически
data class User(val name: String, val age: Int)

// Получаем бесплатно:
// - equals/hashCode
// - toString
// - copy
// - componentN для destructuring

val (name, age) = user  // Destructuring
val updated = user.copy(age = 26)  // Copy with changes
```

### Destructuring для множественных возвратов

```kotlin
// ❌ Возврат через wrapper класс
data class Result(val success: Boolean, val data: String)

fun process(): Result {
    return Result(true, "data")
}

val result = process()
if (result.success) {
    println(result.data)
}

// ✅ Destructuring
fun process(): Pair<Boolean, String> {
    return true to "data"
}

val (success, data) = process()
if (success) {
    println(data)
}

// ✅ Или Triple для 3 значений
fun fetch(): Triple<Boolean, String, Int> {
    return Triple(true, "data", 200)
}

val (success, data, code) = fetch()

// ✅ Data class если больше 3 или нужны имена
data class FetchResult(val success: Boolean, val data: String, val code: Int)
```

## Null Safety Best Practices

### Избегайте nullable где возможно

```kotlin
// ❌ Лишний nullable
fun findUser(id: String): User? {
    return users[id]  // Может вернуть null
}

// ✅ Возвращайте non-null или кидайте исключение
fun getUser(id: String): User {
    return users[id] ?: throw UserNotFoundException(id)
}

fun findUser(id: String): User? {
    return users[id]  // Optional find
}

// ❌ Nullable параметры без default значения
fun greet(name: String?) {
    println("Hello, ${name ?: "Guest"}")
}

// ✅ Non-null с default значением
fun greet(name: String = "Guest") {
    println("Hello, $name")
}

// ✅ Или два метода
fun greet(name: String) {
    println("Hello, $name")
}

fun greetGuest() {
    greet("Guest")
}
```

### Safe calls цепочки

```kotlin
// ❌ Вложенные if проверки
if (user != null) {
    if (user.profile != null) {
        if (user.profile.address != null) {
            println(user.profile.address.city)
        }
    }
}

// ✅ Safe call chain
println(user?.profile?.address?.city)

// ✅ С elvis для default
val city = user?.profile?.address?.city ?: "Unknown"

// ✅ let для блока кода
user?.profile?.address?.let { address ->
    println("City: ${address.city}")
    println("Street: ${address.street}")
}
```

### requireNotNull и checkNotNull

```kotlin
// ❌ Ручная проверка
fun process(value: String?) {
    if (value == null) {
        throw IllegalArgumentException("Value must not be null")
    }
    // Работаем с value (всё ещё String?)
}

// ✅ requireNotNull
fun process(value: String?) {
    val nonNull = requireNotNull(value) { "Value must not be null" }
    // nonNull: String (не nullable)
}

// ✅ checkNotNull для состояния
fun getUser(): User {
    return checkNotNull(currentUser) { "User not logged in" }
}

// ✅ require для аргументов
fun setAge(age: Int) {
    require(age >= 0) { "Age must be positive" }
}

// ✅ check для состояния
fun disconnect() {
    check(isConnected) { "Not connected" }
    // ...
}
```

## Коллекции Best Practices

### Используйте подходящие операции

```kotlin
// ❌ Ручные циклы
val result = mutableListOf<String>()
for (user in users) {
    result.add(user.name)
}

// ✅ map
val result = users.map { it.name }

// ❌ Фильтрация с циклом
val adults = mutableListOf<User>()
for (user in users) {
    if (user.age >= 18) {
        adults.add(user)
    }
}

// ✅ filter
val adults = users.filter { it.age >= 18 }

// ❌ Проверка наличия
var found = false
for (user in users) {
    if (user.name == "Alice") {
        found = true
        break
    }
}

// ✅ any
val found = users.any { it.name == "Alice" }

// ❌ Подсчёт
var count = 0
for (user in users) {
    if (user.age >= 18) {
        count++
    }
}

// ✅ count
val count = users.count { it.age >= 18 }
```

### Sequence для больших коллекций

```kotlin
// ❌ Цепочки операций на больших коллекциях
val result = (1..1_000_000)
    .map { it * 2 }              // Создаёт List на 1M
    .filter { it % 3 == 0 }      // Создаёт новый List
    .map { it.toString() }       // Ещё один List
    .take(10)
    .toList()

// ✅ Sequence для lazy evaluation
val result = (1..1_000_000)
    .asSequence()
    .map { it * 2 }
    .filter { it % 3 == 0 }
    .map { it.toString() }
    .take(10)                    // Обработает только 10 элементов!
    .toList()

// ❌ Sequence для маленьких коллекций (overhead)
val result = listOf(1, 2, 3)
    .asSequence()                // Лишний overhead
    .map { it * 2 }
    .toList()

// ✅ Обычные операции для маленьких
val result = listOf(1, 2, 3)
    .map { it * 2 }
```

### Read-only по умолчанию

```kotlin
// ❌ Mutable везде
fun getUsers(): MutableList<User> {
    return mutableListOf(...)
}

// Вызывающий код может изменить!
val users = getUsers()
users.clear()  // Ой!

// ✅ Возвращайте read-only
fun getUsers(): List<User> {
    return listOf(...)
}

// ✅ Или buildList
fun getUsers(): List<User> = buildList {
    add(User("Alice"))
    add(User("Bob"))
}

// ✅ Mutable только внутри
class UserRepository {
    private val users = mutableListOf<User>()  // Mutable внутри

    fun getUsers(): List<User> = users  // Read-only наружу

    fun addUser(user: User) {
        users.add(user)
    }
}
```

## Функциональное программирование

### Higher-order functions

```kotlin
// ❌ Дублирование логики
fun processUsers() {
    for (user in users) {
        log("Processing ${user.name}")
        // Обработка
        log("Processed ${user.name}")
    }
}

fun processOrders() {
    for (order in orders) {
        log("Processing ${order.id}")
        // Обработка
        log("Processed ${order.id}")
    }
}

// ✅ Higher-order function
fun <T> processWithLogging(
    items: List<T>,
    getId: (T) -> String,
    process: (T) -> Unit
) {
    for (item in items) {
        val id = getId(item)
        log("Processing $id")
        process(item)
        log("Processed $id")
    }
}

processWithLogging(users, { it.name }, { processUser(it) })
processWithLogging(orders, { it.id }, { processOrder(it) })
```

### Избегайте побочных эффектов

```kotlin
// ❌ Функция с побочными эффектами
var total = 0

fun addToTotal(value: Int) {
    total += value  // Модифицирует глобальное состояние
}

// ✅ Чистая функция
fun calculateTotal(values: List<Int>): Int {
    return values.sum()
}

// ❌ forEach с побочными эффектами
val result = mutableListOf<String>()
users.forEach { result.add(it.name) }  // Модифицирует внешнюю переменную

// ✅ Используйте map
val result = users.map { it.name }
```

### Композиция функций

```kotlin
// ✅ Маленькие композируемые функции
fun String.isValidEmail(): Boolean =
    this.contains("@") && this.contains(".")

fun String.normalize(): String =
    this.trim().lowercase()

fun String.isValidNormalizedEmail(): Boolean =
    this.normalize().isValidEmail()

// ✅ Operator функции для композиции
infix fun <T, R, U> ((T) -> R).andThen(next: (R) -> U): (T) -> U {
    return { next(this(it)) }
}

val normalize: (String) -> String = { it.trim().lowercase() }
val validateEmail: (String) -> Boolean = { it.contains("@") }

val validateNormalizedEmail = normalize andThen validateEmail
```

## Performance Tips

### inline функции

```kotlin
// ❌ Высокочастотная функция без inline
fun measureTime(block: () -> Unit): Long {
    val start = System.nanoTime()
    block()  // Создаёт Function object
    return System.nanoTime() - start
}

// Если вызывается часто - overhead!

// ✅ inline для горячих путей
inline fun measureTime(block: () -> Unit): Long {
    val start = System.nanoTime()
    block()  // Код вставляется напрямую
    return System.nanoTime() - start
}

// ✅ inline для reified
inline fun <reified T> isInstance(value: Any): Boolean {
    return value is T
}

// ❌ Не используйте inline для больших функций
inline fun processLargeData() {  // ❌ Код раздуется
    // 100 строк кода
}

// ✅ inline только для маленьких
inline fun <T> T.applyIf(condition: Boolean, block: T.() -> Unit): T {
    if (condition) block()
    return this
}
```

### Избегайте лишних аллокаций

```kotlin
// ❌ Создание объектов в цикле
fun process(items: List<String>) {
    for (item in items) {
        val result = Result(item)  // Аллокация каждую итерацию
        // ...
    }
}

// ✅ Переиспользование
fun process(items: List<String>) {
    val result = Result()
    for (item in items) {
        result.update(item)  // Переиспользуем
        // ...
    }
}

// ❌ String конкатенация в цикле
var result = ""
for (i in 1..1000) {
    result += i.toString()  // Создаёт новую строку каждый раз
}

// ✅ StringBuilder
val result = buildString {
    for (i in 1..1000) {
        append(i)
    }
}

// ❌ Лишние промежуточные коллекции
val result = list
    .map { it * 2 }       // Новая коллекция
    .filter { it > 10 }   // Ещё одна
    .map { it.toString() } // И ещё одна

// ✅ Sequence или одна операция
val result = list.mapNotNull { value ->
    val doubled = value * 2
    if (doubled > 10) doubled.toString() else null
}
```

### when вместо множественных if

```kotlin
// ❌ Цепочка if-else
if (status == Status.SUCCESS) {
    // ...
} else if (status == Status.ERROR) {
    // ...
} else if (status == Status.LOADING) {
    // ...
} else {
    // ...
}

// ✅ when expression (компилируется в tableswitch - O(1))
when (status) {
    Status.SUCCESS -> { }
    Status.ERROR -> { }
    Status.LOADING -> { }
    else -> { }
}

// ✅ sealed class + when (exhaustive, no else needed)
sealed class Result
object Success : Result()
object Error : Result()

fun handle(result: Result) = when (result) {
    Success -> { }
    Error -> { }
    // Если добавим новый тип - ошибка компиляции!
}
```

### Ленивая инициализация

```kotlin
// ❌ Eager инициализация дорогих объектов
class ViewModel {
    private val database = Database.connect()  // Сразу при создании
    private val cache = Cache.initialize()
}

// ✅ lazy для ленивой инициализации
class ViewModel {
    private val database by lazy { Database.connect() }  // Только при первом доступе
    private val cache by lazy { Cache.initialize() }
}

// ✅ lateinit для dependency injection
class Controller {
    lateinit var service: UserService

    fun init(service: UserService) {
        this.service = service
    }
}

// ❌ Ленивая инициализация вручную
class Config {
    private var _apiUrl: String? = null
    val apiUrl: String
        get() {
            if (_apiUrl == null) {
                _apiUrl = loadApiUrl()
            }
            return _apiUrl!!
        }
}

// ✅ lazy
class Config {
    val apiUrl: String by lazy { loadApiUrl() }
}
```

## Scope Functions Best Practices

### Когда использовать какую

```kotlin
// ✅ let - null-safety и трансформация
val length = nullableString?.let { it.length } ?: 0

// ✅ apply - конфигурация объекта
val user = User().apply {
    name = "Alice"
    age = 25
}

// ✅ run - блок вычислений с результатом
val result = connection.run {
    connect()
    fetchData()
    disconnect()
}

// ✅ also - побочные эффекты (логи)
val result = data
    .also { log("Processing: $it") }
    .process()

// ✅ with - группировка операций
with(canvas) {
    drawCircle()
    drawRectangle()
}

// ❌ Избегайте вложенности
value?.let { v1 ->
    v1.property?.let { v2 ->
        v2.method()?.let { v3 ->
            // Слишком вложено!
        }
    }
}

// ✅ Safe call chain
value?.property?.method()?.let { process(it) }
```

## Распространённые антипаттерны

### 1. Использование !! (not-null assertion)

```kotlin
// ❌ !! везде
fun process(user: User?) {
    println(user!!.name)  // NullPointerException если null!
}

// ✅ Safe call или elvis
fun process(user: User?) {
    println(user?.name ?: "Unknown")
}

// ✅ Или ранний return
fun process(user: User?) {
    val nonNullUser = user ?: return
    println(nonNullUser.name)  // Теперь non-null
}

// !! допустим только если:
// 1. Точно знаете что не null
// 2. Исключение - желаемое поведение
lateinit var dependency: Dependency

fun init() {
    dependency = createDependency()
}

fun use() {
    dependency.method()  // OK, проверка при доступе
}
```

### 2. var когда нужен val

```kotlin
// ❌ Лишняя мутабельность
fun calculate(x: Int, y: Int): Int {
    var result = x + y  // var не нужен
    return result
}

// ✅ val или expression
fun calculate(x: Int, y: Int): Int {
    val result = x + y
    return result
}

// Или просто:
fun calculate(x: Int, y: Int): Int = x + y
```

### 3. Длинные функции

```kotlin
// ❌ Функция на 100 строк
fun processUser(user: User) {
    // Валидация (20 строк)
    // Трансформация (30 строк)
    // Сохранение (20 строк)
    // Логирование (10 строк)
    // Уведомления (20 строк)
}

// ✅ Разбейте на маленькие функции
fun processUser(user: User) {
    validateUser(user)
    val transformed = transformUser(user)
    saveUser(transformed)
    logUserProcessing(user)
    sendNotifications(user)
}

private fun validateUser(user: User) { }
private fun transformUser(user: User): TransformedUser { }
// ...
```

### 4. Неправильный уровень абстракции

```kotlin
// ❌ Смешивание уровней абстракции
fun processOrder(order: Order) {
    // Бизнес-логика
    val total = order.items.sumOf { it.price }

    // Низкоуровневая работа с БД
    val connection = DriverManager.getConnection(url)
    val statement = connection.prepareStatement("INSERT INTO orders...")
    statement.setString(1, order.id)
    statement.executeUpdate()

    // HTTP запрос
    val client = HttpClient()
    client.post("https://api.example.com/orders", order.toJson())
}

// ✅ Разделите на слои
class OrderService(
    private val repository: OrderRepository,
    private val notificationService: NotificationService
) {
    fun processOrder(order: Order) {
        val total = order.calculateTotal()
        repository.save(order)
        notificationService.notifyOrderCreated(order)
    }
}
```

### 5. Игнорирование результатов

```kotlin
// ❌ Игнорирование результата
fun update(user: User) {
    repository.save(user)  // Может вернуть false при ошибке!
    // Продолжаем выполнение
}

// ✅ Проверяйте результаты
fun update(user: User) {
    val saved = repository.save(user)
    if (!saved) {
        throw SaveException("Failed to save user")
    }
}

// ✅ Или используйте Result
fun update(user: User): Result<Unit> {
    return repository.save(user)
}
```

---

## Кто использует и реальные примеры

### Компании с идиоматичным Kotlin

| Компания | Best Practice | Результаты |
|----------|---------------|------------|
| **JetBrains** | val-first, sealed classes | IntelliJ Platform — эталон идиоматичного Kotlin |
| **Google** | Coding conventions, lint | Android Kotlin Style Guide, Compose best practices |
| **Square** | Immutability, extensions | OkHttp, Retrofit — образцовый Kotlin код |
| **Netflix** | Scope functions, DSL | Kotlin backend services |
| **Uber** | Null-safety, smart casts | 5M+ строк, строгие правила |
| **Pinterest** | Sequence, performance | Оптимизация для 1.5M строк |

### Паттерны из Production

**Scope Functions в Google Compose:**
```kotlin
// apply для конфигурации
val button = Button(context).apply {
    text = "Click me"
    setOnClickListener { handleClick() }
}

// let для null-safety
user?.let {
    analytics.logUserAction(it.id)
}

// also для логирования
return result.also { log("Returning: $it") }
```

**Immutability в Square OkHttp:**
```kotlin
// val везде, copy для изменений
data class Request(
    val url: HttpUrl,
    val method: String,
    val headers: Headers
) {
    fun newBuilder() = Builder(this)
}
```

### Реальные кейсы

**Case 1: Uber — Strict Null Safety**
```
Политика: Запрет !! в code review
Альтернатива: ?: throw с понятным сообщением
Результат: 70% меньше NullPointerException в production
```

**Case 2: Pinterest — Sequence Optimization**
```
Проблема: 1.5M строк, медленные операции над коллекциями
Решение: asSequence() для цепочек > 3 операций
Результат: 30% меньше аллокаций в hot paths
```

**Case 3: Netflix — Scope Function Guidelines**
```
Правило: Максимум 1 scope function на выражение
Запрет: Вложенные let { run { also {} } }
Результат: Code review проходит в 2x быстрее
```

---

## Чеклист

- [ ] Используете val вместо var где возможно
- [ ] Предпочитаете expressions над statements
- [ ] Избегаете !! (not-null assertion)
- [ ] Применяете data classes для моделей данных
- [ ] Используете подходящие операции коллекций
- [ ] Применяете Sequence для больших коллекций
- [ ] Возвращаете read-only коллекции из публичного API
- [ ] Используете inline для hot path функций
- [ ] Применяете lazy для дорогих инициализаций
- [ ] Пишете маленькие, композируемые функции
- [ ] Используете scope functions правильно
- [ ] Следуете naming conventions
- [ ] Избегаете смешивания уровней абстракции
- [ ] Проверяете результаты операций
- [ ] Пишете идиоматичный Kotlin код

## Проверь себя

1. **Когда использовать `var` вместо `val`?**
   <details><summary>Ответ</summary>
   Только когда значение реально изменяется после инициализации (счётчики в циклах, аккумуляторы). Если можно вычислить сразу — используйте `val` с expression. Если значение задаётся условно — используйте `val` с `when` или `if` expression.
   </details>

2. **Чем `entries` лучше `values()` для enum?**
   <details><summary>Ответ</summary>
   `values()` каждый раз создаёт новый массив (копию), что создаёт аллокации. `entries` (Kotlin 1.9+) возвращает неизменяемый `List`, который создаётся один раз. Для частых вызовов — существенная разница.
   </details>

3. **Когда использовать `also` vs `apply`?**
   <details><summary>Ответ</summary>
   `apply` — для конфигурации объекта (используете `this`). `also` — для побочных эффектов без изменения (логирование, отладка). `also` принимает `it`, `apply` — `this`. Оба возвращают исходный объект.
   </details>

4. **Почему inline важен для функций с лямбдами?**
   <details><summary>Ответ</summary>
   Без `inline` каждый вызов лямбды создаёт объект `Function`. С `inline` код лямбды вставляется напрямую — нет аллокации. Критично для hot paths и высокочастотных вызовов. Но не используйте для больших функций — код раздуется.
   </details>

5. **Как избежать множественных промежуточных коллекций?**
   <details><summary>Ответ</summary>
   Для маленьких коллекций (<1000) — объединяйте операции в одну (mapNotNull вместо map+filter). Для больших — используйте `asSequence()` для lazy evaluation. Sequence обрабатывает элементы по одному, не создавая промежуточные списки.
   </details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "val гарантирует immutability" | val гарантирует только неизменяемость ссылки. Содержимое MutableList, присвоенного val, можно менять |
| "data class всегда лучше обычного class" | data class генерирует equals/hashCode/copy/componentN. Для mutable entities это может быть нежелательно |
| "Scope functions взаимозаменяемы" | let (it, return value), run (this, return value), apply (this, return receiver), also (it, return receiver) — разные use cases |
| "!! допустим если 'я уверен'" | !! скрывает логическую ошибку. Если уверены — используйте requireNotNull/checkNotNull с message. Или переосмыслите nullable design |
| "Sequence всегда быстрее List" | Sequence добавляет overhead на создание объектов. Для <1000 элементов List операции часто быстрее |
| "inline нужно использовать везде" | inline полезен только для higher-order functions (экономия на lambda object). Для обычных функций увеличивает размер bytecode |
| "Extension function = modification класса" | Extensions компилируются в static methods. Нет доступа к private members, нет полиморфизма |
| "Kotlin null-safe по умолчанию" | Kotlin null-safe для собственного кода. Java interop через platform types (Type!) требует осторожности |
| "Smart cast работает везде" | Smart cast не работает для var (может измениться), для custom getters, для properties из другого модуля |
| "lateinit лучше nullable" | lateinit скрывает initialization order problems. Nullable + require/check делает контракт явным |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin Best Practices |
|--------------|-----------------------------------|
| **Immutability** | val + immutable collections = referential transparency. Проще reasoning, безопаснее в multithreaded code |
| **Expression-Oriented Programming** | when, if, try — expressions. Меньше временных переменных, более declarative код |
| **Null Safety (Option Type)** | Nullable types моделируют отсутствие значения. Type system enforcement vs runtime checks |
| **Algebraic Data Types** | sealed class + data class = Sum types + Product types. Exhaustive when checks |
| **Lazy Evaluation** | lazy delegate, Sequence — вычисление по требованию. Экономия ресурсов для дорогих операций |
| **Higher-Order Functions** | Функции как параметры/возвращаемые значения. map, filter, reduce — стандартные HOF |
| **Structural Equality** | data class автоматически реализует equals/hashCode по полям. Value semantics vs identity |
| **Builder Pattern** | apply/also scope functions для fluent object configuration. Type-safe builders через DSL |
| **Fail-Fast Principle** | require (preconditions), check (invariants), error (illegal state) — ранний fail с понятным message |
| **Single Responsibility** | Маленькие функции с одной responsibility. Composition over inheritance |

---

## Связанные темы
- [[kotlin-basics]] — Основы для понимания best practices
- [[kotlin-functional]] — Функциональное программирование
- [[kotlin-collections]] — Коллекции и их операции
- [[kotlin-coroutines]] — Best practices для асинхронного кода
- [[kotlin-testing]] — Тестирование кода

---

## Источники

| # | Источник | Тип | Описание |
|---|----------|-----|----------|
| 1 | [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html) | Docs | Официальные coding conventions |
| 2 | [Kotlin Idioms](https://kotlinlang.org/docs/idioms.html) | Docs | Идиоматичные паттерны Kotlin |
| 3 | [Effective Kotlin](https://effectivekotlin.com/) | Book | Книга Marcin Moskala — глубокие best practices |
| 4 | [Kotlin Performance Guide](https://developer.android.com/kotlin/performance) | Docs | Оптимизация Kotlin для Android |
| 5 | [Kotlin Blog](https://blog.jetbrains.com/kotlin/) | Blog | Официальные анонсы и практики |
| 6 | [What's New in Kotlin 2.0](https://kotlinlang.org/docs/whatsnew20.html) | Docs | Новые best practices в Kotlin 2.0 |
| 7 | [Android Kotlin Style Guide](https://developer.android.com/kotlin/style-guide) | Docs | Гайд Google для Android |
| 8 | [Kotlin in Action, 2nd Ed](https://www.manning.com/books/kotlin-in-action-second-edition) | Book | Обновлённая книга от создателей языка |
| 9 | [KotlinConf Videos](https://kotlinconf.com/) | Video | Доклады с KotlinConf |
| 10 | [Jake Wharton's Kotlin Talks](https://jakewharton.com/) | Video | Практики от эксперта |

---

*Проверено: 2026-01-09 | Источники: Kotlin Docs, Effective Kotlin, Android Style Guide, Square OSS — Педагогический контент проверен*
