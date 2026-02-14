---
title: "Kotlin Best Practices: Идиоматичный код и оптимизация"
created: 2025-11-25
modified: 2026-02-13
tags:
  - topic/jvm
  - best-practices
  - coding-conventions
  - performance
  - idioms
  - type/concept
  - level/intermediate
reading_time: 24
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[kotlin-basics]]"
  - "[[kotlin-oop]]"
  - "[[kotlin-functional]]"
related:
  - "[[kotlin-basics]]"
  - "[[kotlin-functional]]"
  - "[[kotlin-collections]]"
  - "[[kotlin-coroutines]]"
  - "[[kotlin-testing]]"
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

Kotlin следует общепринятым соглашениям: PascalCase для классов, camelCase для функций и свойств, UPPER_SNAKE_CASE для констант:

```kotlin
class UserRepository         // PascalCase
fun calculateTotal()         // camelCase
const val MAX_RETRY_COUNT = 3  // UPPER_SNAKE_CASE
package com.example.myapp    // lowercase
```

Избегайте венгерской нотации и `m`-префиксов из Java/Android. Boolean-свойства именуйте в вопросительной форме:

```kotlin
val name: String     // НЕ strName или mName
val isEmpty: Boolean // Вопросительная форма
val hasChildren: Boolean
val canEdit: Boolean
```

Для тестов используйте backtick-имена -- они читаются как спецификация поведения:

```kotlin
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

`val` по умолчанию -- главный принцип. Если значение не меняется после инициализации, используйте `val`:

```kotlin
var name = "Alice"  // Лишняя мутабельность
val name = "Alice"  // Правильно: val если не меняется

val list = mutableListOf<String>()
list.add("item")  // val для ссылки, мутабельность внутри
```

Когда значение зависит от условия -- используйте `if` или `when` как выражение вместо `var` с присвоением:

```kotlin
// Плохо: var + присвоение в ветках
var result: String
if (condition) { result = "A" } else { result = "B" }

// Хорошо: val + expression
val result = if (condition) "A" else "B"

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

Kotlin предлагает операции коллекций, заменяющие ручные циклы. `map` для трансформации, `filter` для фильтрации:

```kotlin
// Ручной цикл -> map
val names = users.map { it.name }

// Фильтрация с циклом -> filter
val adults = users.filter { it.age >= 18 }
```

`any`, `count`, `first`, `find` -- для поиска и проверок. Они делают код декларативным: описываете ЧТО нужно, а не КАК:

```kotlin
val found = users.any { it.name == "Alice" }
val count = users.count { it.age >= 18 }
val alice = users.find { it.name == "Alice" }
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

## Связь с другими темами

**[[kotlin-basics]]** — best practices строятся на знании основ: нельзя оценить идиоматичность кода, не зная базовых конструкций (val vs var, when, null-safety operators). Basics объясняют «что можно написать», best practices — «как писать правильно». Многие anti-patterns (использование `!!`, Java-style if-null) возникают от незнания базовых возможностей Kotlin. Рекомендуется освоить basics, затем изучать best practices для закрепления правильных привычек.

**[[kotlin-functional]]** — scope functions (let, apply, run, also, with), lambda expressions и higher-order functions — ключевая часть идиоматичного Kotlin. Best practices устанавливают правила их использования: одна scope function на выражение, `let` для null-safety, `apply` для конфигурации. Без понимания functional programming невозможно писать идиоматичный Kotlin, но без best practices — легко злоупотребить функциональными конструкциями.

**[[kotlin-collections]]** — операции с коллекциями (`map`, `filter`, `groupBy`, `associate`) — одна из самых частых задач в Kotlin-коде. Best practices определяют выбор между `List` и `Sequence` (lazy vs eager), immutable и mutable коллекциями, `forEach` и `for` циклом. Знание collections API и best practices их применения — маркер уровня Kotlin-разработчика на code review.

**[[kotlin-coroutines]]** — асинхронный код имеет собственный набор best practices: structured concurrency, правильный выбор dispatcher, обработка ошибок через SupervisorJob. Best practices для sequential и concurrent кода различаются фундаментально: в coroutines появляются cancellation, scope management и backpressure. Изучите coroutines basics, затем best practices для async-кода.

**[[kotlin-testing]]** — идиоматичный код легче тестировать: val-переменные предсказуемы, sealed classes позволяют exhaustive testing, extension functions изолированы. Best practices и testing взаимно усиливают друг друга: написание тестов помогает выявить неидиоматичный код, а идиоматичный код упрощает написание тестов.

---

## Источники и дальнейшее чтение

- Moskala M. (2024). *Effective Kotlin*. — Главная книга о Kotlin best practices: 60+ правил с объяснениями, от null-safety до coroutines. Аналог Effective Java для Kotlin-экосистемы.
- Jemerov D., Isakova S. (2024). *Kotlin in Action, 2nd Edition*. — Каноническая книга от создателей языка, объясняет design decisions и идиоматичные паттерны с позиции авторов языка.
- Bloch J. (2018). *Effective Java, 3rd Edition*. — Многие Java best practices применимы к Kotlin (immutability, defensive copies, API design). Помогает понять, какие Java-проблемы Kotlin решает на уровне языка.

---

## Проверь себя

> [!question]- Почему использование !! (not-null assertion) считается анти-паттерном и какие альтернативы существуют?
> !! бросает KotlinNullPointerException если значение null — это возвращает проблему Java-стиля NPE. Альтернативы: (1) safe call + Elvis: value?.property ?: defaultValue; (2) early return: val v = nullable ?: return; (3) let для nullable: nullable?.let { process(it) }; (4) require/check для предусловий: requireNotNull(value) { "Value must not be null" }; (5) refactoring для устранения nullable типа. Единственное допустимое использование !!: в тестах или когда контракт гарантирует non-null, но компилятор не может это вывести.

> [!question]- Сценарий: в code review вы видите: list.filter { it.isActive }.map { it.name }.first(). Какие проблемы вы бы указали?
> Проблемы: (1) first() бросает NoSuchElementException если список пуст — использовать firstOrNull() или first { predicate }; (2) создаются две промежуточные коллекции (после filter и после map) — для большого списка неэффективно; (3) обрабатывается весь список хотя нужен один элемент. Рефакторинг: list.firstOrNull { it.isActive }?.name или list.asSequence().filter { it.isActive }.map { it.name }.firstOrNull() — lazy evaluation, остановка после первого совпадения, без промежуточных аллокаций.

> [!question]- Когда стоит использовать scope functions (let, apply, run, also, with) и когда они ухудшают читаемость?
> Стоит: let для null-safety (nullable?.let { process(it) }), apply для конфигурации builder-объектов, also для side effects (логирование, validation), with для группировки операций на одном объекте. Ухудшают читаемость когда: (1) вложенные scope functions (let внутри apply внутри run) — сложно отследить this/it; (2) длинные лямбды внутри scope function (>5 строк); (3) бессмысленное использование (val name = "John".let { it } — нет пользы); (4) смешение scope functions без причины (apply + also на одном объекте). Правило: если scope function не делает код читабельнее — не используйте.

---

## Ключевые карточки

Какие пять главных правил идиоматичного Kotlin?
?
1) val по умолчанию — var только когда необходимо мутировать. 2) data class для моделей — не писать equals/hashCode/toString вручную. 3) when вместо if-else chains — особенно для sealed class/enum. 4) Expression body для коротких функций: fun double(x: Int) = x * 2. 5) Extension functions для utility вместо Utils-классов.

Какие распространённые анти-паттерны в Kotlin?
?
1) !! вместо safe call + Elvis. 2) var вместо val. 3) Пустой catch блок: catch(e: Exception) {}. 4) it в вложенных лямбдах (неясно какой it). 5) mutableListOf() когда хватит listOf(). 6) lateinit для nullable (лучше nullable type). 7) GlobalScope вместо structured concurrency. 8) .first() вместо .firstOrNull().

Когда использовать Sequence вместо обычных коллекций?
?
Sequence когда: (1) большой dataset (>10000 элементов); (2) цепочка 3+ операций (map/filter/take); (3) нужно раннее завершение (first, take). Обычные коллекции когда: (1) маленький dataset; (2) 1-2 операции; (3) нужен доступ по индексу; (4) результат используется повторно. Sequence не кэширует результат — каждый terminal оператор запускает pipeline заново.

Как правильно обрабатывать ошибки в Kotlin?
?
1) require() для входных параметров (бросает IllegalArgumentException). 2) check() для состояния объекта (IllegalStateException). 3) sealed class Result<T> { Success(data: T), Error(exception: Exception) } для бизнес-ошибок. 4) runCatching { } для оборачивания в Result. 5) Никогда: catch(e: Exception) без обработки. 6) Kotlin не имеет checked exceptions — но документируйте @Throws для Java interop.

Какие naming conventions в Kotlin?
?
camelCase для функций и свойств: val userName. PascalCase для классов и интерфейсов: class UserRepository. UPPER_SNAKE для констант: const val MAX_RETRIES. Пакеты в lowercase: com.example.data. Тестовые функции: backticks допустимы `should return user when id is valid`. Boolean свойства: isActive, hasPermission, canEdit.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубление | [[kotlin-testing]] | Testable код — как best practices влияют на тестируемость |
| Углубление | [[kotlin-advanced-features]] | Когда продвинутые фичи уместны, а когда избыточны |
| Связь | [[kotlin-coroutines]] | Structured concurrency и правильные паттерны async кода |
| Кросс-область | [[clean-code-solid]] | Общие принципы чистого кода, применимые в Kotlin |
| Навигация | [[jvm-overview]] | Вернуться к обзору JVM-тем |

---

*Проверено: 2026-01-09 | Источники: Kotlin Docs, Effective Kotlin, Android Style Guide, Square OSS — Педагогический контент проверен*
