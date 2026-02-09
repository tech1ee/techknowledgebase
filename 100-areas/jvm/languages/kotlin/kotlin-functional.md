---
title: "Kotlin Functional Programming: Lambdas, Higher-Order Functions, Scope Functions"
created: 2025-11-25
modified: 2026-01-03
tags: [kotlin, functional-programming, lambdas, higher-order-functions, scope-functions]
---

# Kotlin ФП: лямбды, scope functions, inline

> **TL;DR:** Функции в Kotlin — first-class citizens. Scope functions: `let` для null-safety (возвращает результат), `apply` для конфигурации (возвращает объект). `inline` устраняет overhead лямбд (объект в heap → inline код). `reified` сохраняет generic тип в runtime. Trailing lambda `list.map { it * 2 }` делает DSL естественным. Arrow-kt для full FP: Either, IO, validated.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin basics | Синтаксис, типы, null-safety | [[kotlin-basics]] |
| ООП основы | Классы, интерфейсы | [[kotlin-oop]] |
| Функции как концепция | Что такое функция, параметры, return | Любой учебник программирования |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Лямбда** | Анонимная функция `{ x -> x * 2 }` | Записка с инструкцией вместо названия рецепта |
| **Higher-order function** | Принимает или возвращает функции | Фабрика, выпускающая другие фабрики |
| **Замыкание (Closure)** | Лямбда, захватывающая внешние переменные | Фотография с контекстом момента |
| **Trailing lambda** | Лямбда вынесенная за скобки вызова | Постскриптум к письму |
| **Scope function** | let, apply, run, also, with | Разные способы работы с одним объектом |
| **Receiver** | Объект, на котором вызывается функция (this) | Получатель письма |
| **inline** | Вставка тела функции в место вызова | Копи-паста кода компилятором |
| **reified** | Сохранение типа generic в runtime | Конверт, который помнит свой тип |
| **Non-local return** | Return из внешней функции внутри лямбды | Выход из здания, а не из комнаты |

---

Функции в Kotlin — first-class citizens: передаются как параметры, возвращаются из функций, хранятся в переменных. Лямбды с замыканиями `{ x -> x * 2 }`, trailing lambda синтаксис делает DSL естественным. Scope functions (let, apply, run, also, with) — пять способов работать с объектом в разном контексте.

`let` для null-safety и трансформации (возвращает результат лямбды), `apply` для конфигурации объекта (возвращает сам объект). Inline функции устраняют overhead анонимных классов — без inline каждая лямбда = объект в heap. `reified` сохраняет generic типы в runtime: `inline fun <reified T> parse(): T` — невозможно в Java из-за type erasure.

---

## Лямбда-выражения

### Синтаксис лямбд

```kotlin
// Полный синтаксис
val sum1: (Int, Int) -> Int = { a: Int, b: Int -> a + b }

// Типы можно опустить (выводятся из контекста)
val sum2: (Int, Int) -> Int = { a, b -> a + b }

// Если лямбда принимает один параметр, можно использовать 'it'
val double: (Int) -> Int = { it * 2 }

// Явное указание параметра для читаемости
val double2: (Int) -> Int = { n -> n * 2 }

// Лямбда без параметров
val greet: () -> String = { "Hello!" }

// Многострочные лямбды (последнее выражение = результат)
val calculate: (Int, Int) -> Int = { a, b ->
    val sum = a + b
    val product = a * b
    sum + product  // Возвращается
}

// Деструктуризация в параметрах
val pairs = listOf(Pair(1, "a"), Pair(2, "b"))
pairs.forEach { (number, letter) ->
    println("$number: $letter")
}
```

**Почему такой синтаксис?**
- Компактность: меньше boilerplate чем анонимные классы в Java
- Выведение типов: компилятор знает типы из контекста
- `it` для одного параметра: ещё компактнее, но может быть менее читаемым

### Замыкания (Closures)

```kotlin
fun makeCounter(): () -> Int {
    var count = 0
    // Лямбда захватывает переменную count
    return { ++count }
}

val counter = makeCounter()
println(counter())  // 1
println(counter())  // 2
println(counter())  // 3

// Модификация внешних переменных (в отличие от Java!)
fun processItems(items: List<String>) {
    var processedCount = 0
    items.forEach {
        // Можем менять внешнюю переменную
        processedCount++
        println("Processed: $it")
    }
    println("Total processed: $processedCount")
}
```

**Почему можно менять переменные?**
- Kotlin не требует `final` как Java
- Переменные оборачиваются в Ref объекты под капотом
- Удобнее, но будьте осторожны с многопоточностью!

### Trailing Lambda Syntax

```kotlin
// Если последний параметр — функция, её можно вынести за скобки
fun repeat(times: Int, action: (Int) -> Unit) {
    for (i in 0 until times) {
        action(i)
    }
}

// Обычный вызов
repeat(3, { index -> println("Iteration $index") })

// Trailing lambda
repeat(3) { index ->
    println("Iteration $index")
}

// Если функция — единственный параметр, скобки можно убрать
fun runAction(action: () -> Unit) {
    action()
}

runAction { println("Hello!") }

// Множественные trailing lambdas (Kotlin 1.7+)
fun measureTime(
    action: () -> Unit,
    onComplete: (Long) -> Unit
) {
    val start = System.currentTimeMillis()
    action()
    val duration = System.currentTimeMillis() - start
    onComplete(duration)
}

measureTime(
    action = { heavyOperation() },
    onComplete = { time -> println("Took ${time}ms") }
)
```

**Почему trailing lambda?**
- Читаемость: похоже на встроенные конструкции языка (if, while)
- DSL: позволяет создавать выразительные domain-specific языки
- Стандарт Kotlin: все collection операции используют это

## Higher-Order Functions

### Функции принимающие функции

```kotlin
// Функция принимающая другую функцию
fun calculate(x: Int, y: Int, operation: (Int, Int) -> Int): Int {
    return operation(x, y)
}

val sum = calculate(5, 3) { a, b -> a + b }      // 8
val product = calculate(5, 3) { a, b -> a * b }  // 15

// Множественные функциональные параметры
fun processString(
    str: String,
    validate: (String) -> Boolean,
    transform: (String) -> String,
    onError: (String) -> Unit
): String? {
    return if (validate(str)) {
        transform(str)
    } else {
        onError("Invalid string: $str")
        null
    }
}

val result = processString(
    str = "hello",
    validate = { it.isNotEmpty() },
    transform = { it.uppercase() },
    onError = { error -> println(error) }
)  // "HELLO"
```

### Функции возвращающие функции

```kotlin
// Возврат функции
fun makeMultiplier(factor: Int): (Int) -> Int {
    return { number -> number * factor }
}

val triple = makeMultiplier(3)
println(triple(4))  // 12
println(triple(5))  // 15

// Фабрика валидаторов
fun makeValidator(
    minLength: Int,
    maxLength: Int
): (String) -> Boolean {
    return { text ->
        text.length in minLength..maxLength
    }
}

val usernameValidator = makeValidator(3, 20)
println(usernameValidator("abc"))    // true
println(usernameValidator("ab"))     // false

// Композиция функций
fun <T, R, U> compose(
    f: (R) -> U,
    g: (T) -> R
): (T) -> U {
    return { x -> f(g(x)) }
}

val addOne: (Int) -> Int = { it + 1 }
val double: (Int) -> Int = { it * 2 }

val addOneThenDouble = compose(double, addOne)
println(addOneThenDouble(5))  // (5 + 1) * 2 = 12
```

**Почему возвращать функции?**
- Создание специализированных версий функций
- Карринг и частичное применение
- Построение функциональных конвейеров

### Функциональные типы как параметры классов

```kotlin
class EventHandler<T>(
    private val validator: (T) -> Boolean,
    private val processor: (T) -> Unit,
    private val errorHandler: (Exception) -> Unit = { e -> println("Error: $e") }
) {
    fun handle(event: T) {
        try {
            if (validator(event)) {
                processor(event)
            } else {
                errorHandler(IllegalArgumentException("Invalid event"))
            }
        } catch (e: Exception) {
            errorHandler(e)
        }
    }
}

// Использование
val handler = EventHandler<String>(
    validator = { it.isNotBlank() },
    processor = { println("Processing: $it") },
    errorHandler = { println("ERROR: ${it.message}") }
)

handler.handle("valid")   // Processing: valid
handler.handle("")        // ERROR: Invalid event
```

## Function Types

### Объявление типов функций

```kotlin
// Базовый синтаксис: (параметры) -> результат
val func1: (Int) -> String = { it.toString() }
val func2: (Int, Int) -> Int = { a, b -> a + b }
val func3: () -> Unit = { println("Hello") }

// Nullable функции
val nullableFunc: ((Int) -> Int)? = null
if (nullableFunc != null) {
    nullableFunc(5)
}
// Или через safe call
nullableFunc?.invoke(5)

// Функции возвращающие nullable
val funcReturnsNull: (String) -> Int? = { it.toIntOrNull() }

// Функции принимающие nullable параметры
val funcTakesNull: (String?) -> Int = { it?.length ?: 0 }

// Функции высшего порядка как типы
val highOrder: ((Int) -> Int) -> Int = { f -> f(10) }
val result = highOrder { it * 2 }  // 20
```

### Function types с receiver

```kotlin
// Тип функции с receiver: Type.(params) -> Result
// Внутри такой функции 'this' = экземпляр Type

val append: String.(String) -> String = { this + it }
val result = "Hello".append(" World")  // "Hello World"

// Эквивалентно обычной функции с первым параметром
val appendRegular: (String, String) -> String = { a, b -> a + b }

// Практический пример: DSL builder
class HtmlBuilder {
    private val elements = mutableListOf<String>()

    fun addElement(text: String) {
        elements.add(text)
    }

    override fun toString() = elements.joinToString("\n")
}

fun html(init: HtmlBuilder.() -> Unit): String {
    val builder = HtmlBuilder()
    builder.init()  // Вызываем функцию с builder как receiver
    return builder.toString()
}

val page = html {
    addElement("<html>")
    addElement("<body>Hello</body>")
    addElement("</html>")
}
```

**Почему receiver types?**
- DSL: позволяют создавать выразительные API (kotlinx.html, Ktor, Compose)
- Неявный this: внутри лямбды доступны методы receiver типа
- Читаемость: код выглядит как встроенная конструкция языка

### Invoke operator

```kotlin
// Любой класс может стать "вызываемым" через operator invoke
class Greeter(private val greeting: String) {
    operator fun invoke(name: String) = "$greeting, $name!"
}

val greet = Greeter("Hello")
println(greet("Alice"))  // "Hello, Alice!"
println(greet("Bob"))    // "Hello, Bob!"

// Множественные invoke для разных сигнатур
class Calculator {
    operator fun invoke(a: Int, b: Int): Int = a + b
    operator fun invoke(a: Int, b: Int, c: Int): Int = a + b + c
}

val calc = Calculator()
println(calc(2, 3))      // 5
println(calc(2, 3, 4))   // 9
```

## Scope Functions

> Функции для работы с контекстом объекта: let, apply, run, also, with

### Сравнительная таблица

| Функция | Контекст  | Возврат     | Использование                          |
|---------|-----------|-------------|----------------------------------------|
| let     | it        | результат λ | null-safety, трансформация             |
| apply   | this      | this        | конфигурация объекта                   |
| run     | this      | результат λ | выполнение блока + трансформация       |
| also    | it        | this        | побочные действия (логи)               |
| with    | this      | результат λ | группировка вызовов без extension      |

### let - трансформация с it

```kotlin
// Основное использование: null-safety
val name: String? = getNullableName()
name?.let { nonNullName ->
    println("Name length: ${nonNullName.length}")
    saveToDatabase(nonNullName)
}
// Если name == null, блок не выполнится

// Трансформация и использование результата
val length = name?.let { it.length } ?: 0

// Ограничение scope переменной
val result = computeValue().let { value ->
    // value доступна только здесь
    validate(value)
    transform(value)
}

// Цепочка вызовов
val result = fetchData()
    ?.let { parseJson(it) }
    ?.let { validateModel(it) }
    ?.let { saveToDatabase(it) }

// Альтернатива вложенным if
val user: User? = getUser()
val profile: Profile? = getProfile()
val settings: Settings? = getSettings()

user?.let { u ->
    profile?.let { p ->
        settings?.let { s ->
            processUserData(u, p, s)
        }
    }
}
```

**Почему let?**
- Null-safety: избегаем `!!` и явных проверок
- Ограничение scope: временная переменная не "загрязняет" внешний scope
- Читаемость: явное "если есть значение, сделай с ним что-то"

### apply - конфигурация с this

```kotlin
// Основное использование: конфигурация объекта
val person = Person().apply {
    name = "Alice"        // this.name
    age = 30
    email = "alice@example.com"
}
// Возвращает сам объект (person)

// Вместо builder pattern
class RequestBuilder {
    var url: String = ""
    var method: String = "GET"
    var headers: Map<String, String> = emptyMap()
    var body: String? = null

    fun build(): Request = Request(url, method, headers, body)
}

val request = RequestBuilder().apply {
    url = "https://api.example.com"
    method = "POST"
    headers = mapOf("Content-Type" to "application/json")
    body = """{"key": "value"}"""
}.build()

// Инициализация View в Android
val textView = TextView(context).apply {
    text = "Hello"
    textSize = 20f
    setTextColor(Color.BLACK)
}

// Intent configuration
val intent = Intent(context, MainActivity::class.java).apply {
    putExtra("key", "value")
    flags = Intent.FLAG_ACTIVITY_NEW_TASK
}
```

**Почему apply?**
- Возвращает объект: можно использовать сразу после создания
- this как receiver: не нужно повторять имя переменной
- Читаемость: группирует связанную конфигурацию

### run - выполнение блока с this

```kotlin
// Выполнение блока кода и возврат результата
val hexColor = "#FF5733"
val color = hexColor.run {
    val r = substring(1, 3).toInt(16)
    val g = substring(3, 5).toInt(16)
    val b = substring(5, 7).toInt(16)
    Color.rgb(r, g, b)  // Возвращается
}

// Группировка операций над объектом
val result = service.run {
    connect()
    authenticate()
    fetchData()
    disconnect()
}

// Как альтернатива let когда нужен this
val name: String? = getName()
val result = name?.run {
    // this = name (String)
    uppercase().take(10)
}

// Комбинация локальных вычислений
val result = run {
    val a = fetchA()
    val b = fetchB()
    val c = fetchC()
    combine(a, b, c)
}
```

**Почему run?**
- Возвращает результат: для трансформаций
- this как receiver: удобно для цепочек вызовов методов
- Группировка: изолирует блок вычислений

### also - побочные действия с it

```kotlin
// Основное использование: логирование и отладка
val numbers = mutableListOf(1, 2, 3)
    .also { println("Initial list: $it") }
    .apply { add(4) }
    .also { println("After adding: $it") }
// Возвращает сам объект

// Дополнительные действия в цепочке
val user = createUser("Alice")
    .also { log("User created: ${it.name}") }
    .also { sendWelcomeEmail(it) }
    .also { saveToDatabase(it) }

// Валидация без прерывания цепочки
val result = fetchData()
    .also { require(it.isNotEmpty()) { "Data is empty" } }
    .map { transform(it) }
    .also { println("Transformed: $it") }

// Отладка в цепочках
val result = (1..10)
    .filter { it % 2 == 0 }
    .also { println("After filter: $it") }
    .map { it * it }
    .also { println("After map: $it") }
    .sum()
```

**Почему also?**
- Возвращает объект: не прерывает цепочку вызовов
- it вместо this: явно показывает что работаем с объектом как с параметром
- Побочные эффекты: для логов, валидации, метрик без изменения потока данных

### with - группировка вызовов

```kotlin
// НЕ extension function, а обычная функция
val result = with(someObject) {
    // this = someObject
    doSomething()
    doSomethingElse()
    calculateResult()  // Возвращается
}

// Множественные операции над объектом
class Canvas {
    fun drawCircle() { println("Circle") }
    fun drawSquare() { println("Square") }
    fun drawTriangle() { println("Triangle") }
}

val canvas = Canvas()
with(canvas) {
    drawCircle()
    drawSquare()
    drawTriangle()
}

// Группировка вызовов без создания лишних переменных
fun printUserInfo(user: User) {
    with(user) {
        println("Name: $name")
        println("Age: $age")
        println("Email: $email")
        println("Status: ${if (isActive) "Active" else "Inactive"}")
    }
}

// Работа с companion object
with(MyClass.Companion) {
    val a = createInstance()
    val b = factoryMethod()
}
```

**Почему with?**
- Не extension: используется когда нет смысла вызывать на объекте
- Группировка: избегаем повторения имени переменной
- Читаемость: все операции явно относятся к одному объекту

### takeIf / takeUnless - условное использование

```kotlin
// takeIf - вернуть объект если условие true, иначе null
val positiveNumber = number.takeIf { it > 0 }
// Эквивалентно: if (number > 0) number else null

// takeUnless - вернуть объект если условие false, иначе null
val nonZero = number.takeUnless { it == 0 }

// Практические примеры
val validEmail = email
    .takeIf { it.contains("@") }
    ?.takeIf { it.length >= 5 }
    ?: "invalid@example.com"

// В цепочках обработки
fun processFile(file: File): String? {
    return file
        .takeIf { it.exists() }
        ?.takeIf { it.canRead() }
        ?.takeUnless { it.length() > MAX_SIZE }
        ?.readText()
}

// Вместо if-else для присваивания
val message = response.takeIf { it.isSuccessful }
    ?.body()
    ?.string()
    ?: "Error"
```

### Когда использовать какую scope function

```kotlin
// ✅ let - null-safety и трансформация
nullableValue?.let { processNonNull(it) }

// ✅ apply - конфигурация объекта
val person = Person().apply {
    name = "Alice"
    age = 30
}

// ✅ run - блок вычислений с результатом
val result = connection.run {
    connect()
    sendData()
    disconnect()
}

// ✅ also - логирование и побочные эффекты
val data = fetchData()
    .also { log("Fetched: $it") }
    .process()

// ✅ with - группировка операций
with(canvas) {
    drawCircle()
    drawRectangle()
}

// ❌ Избегайте вложенности
// Плохо:
value?.let { v1 ->
    v1.property?.let { v2 ->
        v2.method()?.let { v3 ->
            // Слишком вложено!
        }
    }
}

// Хорошо:
value
    ?.property
    ?.method()
    ?.let { processResult(it) }
```

## Inline Functions

### Почему inline нужен?

```kotlin
// Обычная функция с лямбдой
fun normalFunction(action: () -> Unit) {
    action()
}

// Компилируется в:
// 1. Создаётся Function object для лямбды
// 2. Вызов через Function.invoke()
// Overhead: allocation + virtual call

// Inline функция
inline fun inlineFunction(action: () -> Unit) {
    action()
}

// Компилируется в:
// Код лямбды вставляется прямо в место вызова
// Никакого Function object, никаких виртуальных вызовов
```

**Когда inline даёт выгоду:**
- Функция принимает лямбду как параметр
- Функция вызывается часто (горячий путь)
- Лямбда маленькая и простая

### Пример inline оптимизации

```kotlin
// Без inline
fun measureTime(action: () -> Unit): Long {
    val start = System.nanoTime()
    action()
    return System.nanoTime() - start
}

val time = measureTime {
    // Создаётся Function object
    heavyComputation()
}

// С inline
inline fun measureTimeInline(action: () -> Unit): Long {
    val start = System.nanoTime()
    action()  // Код лямбды вставлен здесь
    return System.nanoTime() - start
}

val time = measureTimeInline {
    // Никакого Function object
    // Код вставлен напрямую:
    // val start = System.nanoTime()
    // heavyComputation()
    // return System.nanoTime() - start
}
```

### noinline - отключение inline для параметра

```kotlin
// Не все параметры можно inline-ить
inline fun processData(
    data: List<Int>,
    inlinePredicate: (Int) -> Boolean,
    noinline logger: (String) -> Unit  // Не inline
) {
    logger("Starting processing")
    // Можем сохранить noinline функцию в переменную
    val savedLogger = logger
    data.filter(inlinePredicate).forEach {
        savedLogger("Processing $it")
    }
}
```

**Когда нужен noinline?**
- Функциональный параметр сохраняется в переменную
- Функциональный параметр передаётся в не-inline функцию
- Нужно передать лямбду как объект

### crossinline - запрет non-local returns

```kotlin
// Проблема: inline позволяет non-local return
inline fun runAction(action: () -> Unit) {
    action()
}

fun test() {
    runAction {
        return  // Вернётся из test(), не из лямбды!
    }
    println("Never printed")
}

// Решение: crossinline запрещает non-local return
inline fun runActionSafely(crossinline action: () -> Unit) {
    action()
}

fun test2() {
    runActionSafely {
        // return  // Ошибка компиляции!
        return@runActionSafely  // OK, локальный return
    }
    println("Will be printed")
}

// Практический пример: вызов из другого контекста
inline fun runAsync(crossinline action: () -> Unit) {
    Thread {
        // Без crossinline был бы non-local return из Thread!
        action()
    }.start()
}
```

**Когда нужен crossinline?**
- Лямбда вызывается в другом контексте (другой поток, другая функция)
- Хотим запретить non-local returns для безопасности

### reified - работа с generic типами

```kotlin
// Обычные generic стираются в runtime
fun <T> isInstance(value: Any): Boolean {
    // return value is T  // ❌ Ошибка: Cannot check for instance of erased type
    return false
}

// reified сохраняет тип в runtime (только для inline!)
inline fun <reified T> isInstanceReified(value: Any): Boolean {
    return value is T  // ✅ OK!
}

val result1 = isInstanceReified<String>("hello")  // true
val result2 = isInstanceReified<Int>("hello")     // false

// Практические примеры
inline fun <reified T> List<*>.filterIsInstance(): List<T> {
    val result = mutableListOf<T>()
    for (item in this) {
        if (item is T) {
            result.add(item)
        }
    }
    return result
}

val mixed: List<Any> = listOf(1, "two", 3, "four", 5)
val strings = mixed.filterIsInstance<String>()  // ["two", "four"]

// JSON парсинг с reified
inline fun <reified T> String.fromJson(): T {
    return Gson().fromJson(this, T::class.java)
}

val user: User = jsonString.fromJson()  // Тип выведен автоматически!
```

**Почему reified только для inline?**
- Inline вставляет код на место вызова
- В месте вызова тип T известен
- Компилятор подставляет конкретный тип вместо T

## Практические паттерны

### Strategy Pattern через лямбды

```kotlin
// Вместо классов стратегий
interface PaymentStrategy {
    fun pay(amount: Double)
}

class CreditCard : PaymentStrategy {
    override fun pay(amount: Double) { /* ... */ }
}

// Используем функциональные типы
class Checkout(
    private val paymentMethod: (Double) -> Unit
) {
    fun processPayment(amount: Double) {
        paymentMethod(amount)
    }
}

val checkout = Checkout { amount ->
    println("Paying $$amount with credit card")
}
```

### Callback Hell → Функциональные цепочки

```kotlin
// ❌ Callback hell
fetchUser(userId,
    onSuccess = { user ->
        fetchProfile(user.profileId,
            onSuccess = { profile ->
                fetchSettings(profile.settingsId,
                    onSuccess = { settings ->
                        updateUI(user, profile, settings)
                    },
                    onError = { error -> handleError(error) }
                )
            },
            onError = { error -> handleError(error) }
        )
    },
    onError = { error -> handleError(error) }
)

// ✅ Используйте Result type + функциональные операции
fun fetchUserData(userId: String): Result<UserData> = runCatching {
    val user = fetchUser(userId).getOrThrow()
    val profile = fetchProfile(user.profileId).getOrThrow()
    val settings = fetchSettings(profile.settingsId).getOrThrow()
    UserData(user, profile, settings)
}

fetchUserData(userId)
    .onSuccess { updateUI(it) }
    .onFailure { handleError(it) }
```

### DSL Builders

```kotlin
// HTML DSL
class HtmlElement(private val tag: String) {
    private val children = mutableListOf<HtmlElement>()
    private val attributes = mutableMapOf<String, String>()
    var text: String = ""

    fun attr(name: String, value: String) {
        attributes[name] = value
    }

    fun element(tag: String, init: HtmlElement.() -> Unit): HtmlElement {
        val child = HtmlElement(tag)
        child.init()
        children.add(child)
        return child
    }

    override fun toString(): String {
        val attrs = attributes.entries.joinToString(" ") { """${it.key}="${it.value}"""" }
        val attrsStr = if (attrs.isNotEmpty()) " $attrs" else ""
        val childrenStr = children.joinToString("")
        val content = if (text.isNotEmpty()) text else childrenStr
        return "<$tag$attrsStr>$content</$tag>"
    }
}

fun html(init: HtmlElement.() -> Unit): HtmlElement {
    val root = HtmlElement("html")
    root.init()
    return root
}

fun HtmlElement.head(init: HtmlElement.() -> Unit) = element("head", init)
fun HtmlElement.body(init: HtmlElement.() -> Unit) = element("body", init)
fun HtmlElement.div(init: HtmlElement.() -> Unit) = element("div", init)
fun HtmlElement.p(init: HtmlElement.() -> Unit) = element("p", init)

// Использование
val page = html {
    head {
        element("title") { text = "My Page" }
    }
    body {
        div {
            attr("class", "container")
            p { text = "Hello, World!" }
            p { text = "Welcome to DSL" }
        }
    }
}

println(page)
// <html><head><title>My Page</title></head><body><div class="container"><p>Hello, World!</p><p>Welcome to DSL</p></div></body></html>
```

## Распространённые ошибки

### 1. Злоупотребление scope functions

```kotlin
// ❌ Нечитаемая вложенность
person?.let { p ->
    p.address?.let { a ->
        a.city?.let { c ->
            c.name.uppercase()
        }
    }
}

// ✅ Используйте safe calls
person?.address?.city?.name?.uppercase()

// ❌ Использование scope function "просто так"
val name = user.let { it.name }

// ✅ Просто обращайтесь к свойству
val name = user.name
```

### 2. Неправильный выбор scope function

```kotlin
// ❌ apply возвращает объект, но мы используем результат лямбды
val length = "hello".apply {
    length  // Игнорируется!
}  // length = "hello", не 5!

// ✅ Используйте run
val length = "hello".run {
    length  // Возвращается
}  // length = 5

// ❌ let когда нужен this
name?.let {
    it.uppercase() + it.lowercase()  // Повторяем it
}

// ✅ run когда нужно несколько обращений
name?.run {
    uppercase() + lowercase()  // this неявно
}
```

### 3. Non-local returns

```kotlin
// ❌ Неожиданный return из функции
fun processItems(items: List<String>) {
    items.forEach {
        if (it.isEmpty()) {
            return  // Вернётся из processItems, не из forEach!
        }
        println(it)
    }
    println("Done")  // Может не выполниться!
}

// ✅ Локальный return
fun processItems(items: List<String>) {
    items.forEach {
        if (it.isEmpty()) {
            return@forEach  // Вернётся из лямбды
        }
        println(it)
    }
    println("Done")  // Всегда выполнится
}
```

### 4. Излишний inline

```kotlin
// ❌ Inline для больших функций
inline fun processLargeData(data: ByteArray, processor: (Byte) -> Unit) {
    // 100 строк кода
    // Этот код будет копироваться в каждое место вызова!
}

// ✅ inline только для маленьких функций
fun processLargeData(data: ByteArray, processor: (Byte) -> Unit) {
    // Оставьте как обычную функцию
}
```

## Чеклист

- [ ] Используете trailing lambda syntax для читаемости
- [ ] Понимаете разницу между scope functions (let/apply/run/also/with)
- [ ] Избегаете глубокой вложенности scope functions
- [ ] Применяете inline для функций высшего порядка в горячих путях
- [ ] Используете reified для работы с generic типами в runtime
- [ ] Понимаете когда нужен noinline и crossinline
- [ ] Знаете о non-local returns и контролируете их
- [ ] Применяете функциональные типы вместо интерфейсов с одним методом
- [ ] Используете лямбды для замыканий и функциональных паттернов
- [ ] Не злоупотребляете scope functions там где можно обойтись без них

## Куда дальше

**Применение на практике:**
→ [[kotlin-collections]] — map, filter, fold — всё это лямбды и higher-order functions. После этого материала коллекции станут понятнее.

**Углубление:**
→ [[kotlin-advanced-features]] — extension functions и DSL builders. Следующий уровень использования лямбд.
→ [[kotlin-coroutines]] — suspend functions — это тоже функции высшего порядка, только с особым контекстом.

**Практики и стиль:**
→ [[kotlin-best-practices]] — когда использовать scope functions, а когда не стоит. Идиоматичный Kotlin.

---

## Кто использует и реальные примеры

| Компания | Как используют ФП в Kotlin | Результаты |
|----------|---------------------------|------------|
| **JetBrains** | DSL builders в IntelliJ, Kotlin Gradle DSL | Декларативный конфиг вместо XML |
| **Gradle** | Kotlin DSL для build scripts | type-safe builds, IDE autocomplete |
| **Ktor** | Functional routing DSL | Лаконичные API definition |
| **Spring** | Kotlin DSL для bean configuration | Router functions без annotations |
| **Arrow-kt** | Full FP library: Either, IO, Validated | Enterprise FP patterns |

### DSL в production

```
Пример 1: Gradle Kotlin DSL
───────────────────────────
// Вместо Groovy:
// dependencies {
//     implementation 'org.example:lib:1.0'
// }

// Kotlin DSL (type-safe):
dependencies {
    implementation("org.example:lib:1.0")  // IDE autocomplete!
}

Пример 2: Ktor Routing
──────────────────────
routing {
    get("/users") {
        call.respond(userService.getAll())
    }
    post("/users") {
        val user = call.receive<User>()
        call.respond(userService.create(user))
    }
}

Пример 3: Spring Functional Beans
─────────────────────────────────
beans {
    bean<UserRepository>()
    bean<UserService>()
    bean {
        UserController(ref())  // type-safe references
    }
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Лямбды всегда создают объекты" | inline функции исключают allocation лямбды. Код вставляется напрямую в call site. Без inline — да, создаётся Function object |
| "FP медленнее императивного кода" | После инлайнинга и JIT оптимизаций разница минимальна. Для hot paths с inline — идентичная производительность |
| "Scope functions взаимозаменяемы" | let/run возвращают результат блока. apply/also возвращают receiver. this vs it receiver. Разные use cases |
| "Higher-order functions = ФП" | HOF — инструмент ФП. Настоящее ФП включает immutability, pure functions, composition, referential transparency |
| "Arrow-kt нужен для ФП в Kotlin" | Базовое ФП (lambdas, HOF, immutability) встроено в Kotlin. Arrow нужен для advanced patterns (Either, IO, Validated) |
| "with всегда лучше let/run" | with не null-safe (нет ?.with). Для nullable используйте let. with для non-null setup |
| "Каррирование полезно везде" | Currying в Kotlin неидиоматичен — нет автоматического каррирования. Default parameters обычно лучше |
| "Pure functions не имеют side effects" | Pure functions не имеют OBSERVABLE side effects. Logging, caching внутри функции могут быть acceptable |
| "crossinline и noinline — одно и то же" | crossinline запрещает non-local returns, но код инлайнится. noinline вообще не инлайнит лямбду |
| "Function types — только для callbacks" | Function types используются для strategy pattern, composition, partial application, DSL builders |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin Functional |
|--------------|-------------------------------|
| **Lambda Calculus** | Лямбды — анонимные функции из λ-исчисления. { x -> x + 1 } = λx.x+1 |
| **Higher-Order Functions** | Функции, принимающие/возвращающие функции. map, filter, fold — классические HOF |
| **Closure** | Лямбда захватывает переменные из окружающего scope. Captured variables живут дольше scope |
| **Function Composition** | f.andThen(g) = g(f(x)). Построение сложных функций из простых |
| **Partial Application** | Фиксация части аргументов: add(1, _) → increment. Достигается через closure или extension |
| **Pure Functions** | Детерминистичный output, нет side effects. Тестируемость, parallelization, memoization |
| **Referential Transparency** | Expression можно заменить на результат без изменения поведения. Основа функционального рефакторинга |
| **Tail Call Optimization** | tailrec в Kotlin оптимизирует рекурсию в цикл. Избегает StackOverflow для глубокой рекурсии |
| **Monadic Operations** | flatMap/map — операции над контейнерами (List, Sequence, Optional). Композиция эффектов |
| **Immutability** | val + immutable collections. Упрощает reasoning, enables safe sharing |

---

## Рекомендуемые источники

### Официальная документация
- [Kotlin Lambdas](https://kotlinlang.org/docs/lambdas.html) — официальный гайд
- [Scope Functions](https://kotlinlang.org/docs/scope-functions.html) — let, apply, run, also, with
- [Inline Functions](https://kotlinlang.org/docs/inline-functions.html) — inline, reified, crossinline

### Книги
- **"Kotlin in Action"** (2nd ed) — глава о функциональном программировании
- **"Effective Kotlin"** — best practices для лямбд и scope functions
- **"Functional Programming in Kotlin"** — Arrow-kt и продвинутые паттерны

### Видео
- [Kotlin Vocabulary](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc_T0fSZc9obnmnWcjvmJdw_) — Google, scope functions
- [KotlinConf talks on FP](https://www.youtube.com/results?search_query=kotlinconf+functional+programming) — продвинутые темы

### Библиотеки
- [Arrow-kt](https://arrow-kt.io/) — функциональная библиотека (Either, IO, Validated)
- [Kotlin Gradle DSL](https://docs.gradle.org/current/userguide/kotlin_dsl.html) — пример production DSL

---

*Проверено: 2026-01-09 | Источники: Kotlin docs, Arrow-kt, Gradle documentation — Педагогический контент проверен*
