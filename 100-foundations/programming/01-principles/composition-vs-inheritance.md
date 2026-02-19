---
title: "Композиция vs Наследование: когда что выбирать"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/oop
  - topic/kotlin
related:
  - "[[oop-fundamentals]]"
  - "[[solid-principles]]"
  - "[[coupling-cohesion]]"
  - "[[decorator-pattern]]"
  - "[[kotlin-oop]]"
  - "[[kotlin-advanced-features]]"
---

# Композиция vs Наследование: когда что выбирать

Джо Армстронг, создатель Erlang, сформулировал проблему так: "Вы хотели банан, но получили гориллу, которая держит банан, и все джунгли в придачу." `Stack` в Java наследует `Vector` -- а значит, можно вызвать `add(index, element)` на стеке. `Properties` наследует `Hashtable` -- и принимает любые объекты, хотя работает только со строками. Эти ошибки из стандартной библиотеки Java живут десятилетиями, потому что сломать обратную совместимость нельзя. Kotlin учёл этот урок: классы `final` по умолчанию, а делегирование через `by` встроено в язык.

---

## Историческая справка

Идея "предпочитай композицию наследованию" не нова:

| Год | Источник | Вклад |
|-----|----------|-------|
| **1994** | GoF "Design Patterns" | "Favor object composition over class inheritance" -- принцип #2 |
| **2001** | Bloch "Effective Java" | Item 18: "Favor composition over inheritance" с примером `InstrumentedHashSet` |
| **2004** | Армстронг (Erlang) | "Gorilla-Banana" метафора -- проблема транзитивных зависимостей |
| **2016** | Kotlin 1.0 | Классы `final` по умолчанию + делегирование `by` на уровне языка |
| **2017** | Москала "Effective Kotlin" | Item 36: "Prefer composition over inheritance" с Kotlin-примерами |

GoF в 1994 году предупреждали: наследование реализации нарушает инкапсуляцию, потому что подкласс зависит от деталей реализации родителя. 30 лет спустя Kotlin сделал этот принцип частью синтаксиса.

---

## Проблема: Fragile Base Class

**Fragile Base Class Problem** -- фундаментальная проблема наследования реализации. Безобидное изменение в базовом классе ломает наследников, которые зависят от деталей реализации.

### Классический пример Bloch (Item 18)

```kotlin
// ❌ Наследование от HashSet -- классическая ошибка
open class InstrumentedHashSet<E> : HashSet<E>() {
    var addCount = 0
        private set

    override fun add(element: E): Boolean {
        addCount++
        return super.add(element)
    }

    override fun addAll(elements: Collection<E>): Boolean {
        addCount += elements.size
        return super.addAll(elements) // 💥 Проблема!
    }
}

val set = InstrumentedHashSet<String>()
set.addAll(listOf("A", "B", "C"))
println(set.addCount) // Ожидаем 3, получаем 6!
```

**Почему 6?** Внутри `HashSet.addAll()` вызывает `add()` для каждого элемента. Наш `addAll()` прибавляет 3, затем `super.addAll()` трижды вызывает наш переопределённый `add()`, который прибавляет ещё 3. Итого: 6.

Это и есть **Fragile Base Class**: мы зависим от внутренней реализации `HashSet`, которая может измениться в любой версии JDK.

### Ещё хуже: скрытая ловушка

```kotlin
// ❌ Родитель добавляет новый метод в следующей версии
open class BaseCollection<E> {
    open fun add(element: E) { /* ... */ }
    // В версии 2.0 добавили:
    // open fun addChecked(element: E): Boolean { ... }
}

// Наш подкласс случайно имеет метод с тем же именем,
// но ДРУГОЙ семантикой
class MyCollection<E> : BaseCollection<E>() {
    // Раньше это был наш метод, теперь он "переопределяет" базовый!
    fun addChecked(element: E): Boolean {
        // Наша логика, несовместимая с контрактом родителя
        return true
    }
}
```

> [!info] Kotlin-нюанс
> Kotlin защищает от этой проблемы: если в базовом классе появляется метод с сигнатурой, совпадающей с методом наследника, компилятор **требует** явно указать `override`. Без `override` код не скомпилируется. В Java такой метод молча "переопределит" родительский.

---

## Наследование в Kotlin: осознанный выбор

### final по умолчанию -- революционное решение

```kotlin
class User(val name: String)  // final! Нельзя наследовать

// Для наследования нужен явный opt-in:
open class Animal(val name: String) {
    open fun speak() = "..."        // Явно разрешили override
    fun breathe() = "Дышу"          // final метод -- нельзя override
}

class Dog(name: String) : Animal(name) {
    override fun speak() = "Гав!"
    // override fun breathe() = ...  // ❌ Ошибка компиляции!
}
```

Блох в "Effective Java" (Item 17) рекомендует: "Design and document for inheritance, or prohibit it." Kotlin следует этому: чтобы разрешить наследование, автор класса должен **осознанно** пометить его `open`, продумать контракт и задокументировать поведение.

```
    Java:  class = open by default     ← Нужно явно закрывать (final)
    Kotlin: class = final by default   ← Нужно явно открывать (open)

    Java-подход: "Всё открыто, пока не закроешь"
    Kotlin-подход: "Всё закрыто, пока не откроешь"
```

### sealed class: контролируемая иерархия

Когда наследование **нужно**, но набор наследников должен быть **фиксированным**:

```kotlin
sealed class PaymentResult {
    data class Success(val transactionId: String, val amount: Double) : PaymentResult()
    data class Declined(val reason: String) : PaymentResult()
    data class Error(val exception: Throwable) : PaymentResult()
    data object Processing : PaymentResult()
}

fun handlePayment(result: PaymentResult): String = when (result) {
    is PaymentResult.Success    -> "Оплачено: ${result.amount}₽"
    is PaymentResult.Declined   -> "Отклонено: ${result.reason}"
    is PaymentResult.Error      -> "Ошибка: ${result.exception.message}"
    PaymentResult.Processing    -> "Обработка..."
    // else не нужен -- компилятор знает все варианты!
}
```

> [!info] Kotlin-нюанс
> `sealed class` -- это **алгебраический тип** (Sum Type). Компилятор проверяет exhaustiveness в `when`: добавили новый подтип -- все `when`-выражения, где не обработан новый вариант, перестанут компилироваться. Это наследование, но **безопасное**: иерархия закрыта, контракт гарантирован.

### abstract class: шаблонный метод

Когда нужна **общая логика** с точками расширения:

```kotlin
abstract class DataProcessor<T> {
    // Template Method: фиксированный алгоритм
    fun process(input: String): T {
        validate(input)
        val parsed = parse(input)
        val result = transform(parsed)
        log(result)
        return result
    }

    protected open fun validate(input: String) {
        require(input.isNotBlank()) { "Input must not be blank" }
    }

    protected abstract fun parse(input: String): T
    protected abstract fun transform(parsed: T): T

    private fun log(result: T) {
        println("Processed: $result")
    }
}

class JsonProcessor : DataProcessor<Map<String, Any>>() {
    override fun parse(input: String): Map<String, Any> = TODO("JSON parsing")
    override fun transform(parsed: Map<String, Any>) = parsed.filterKeys { it != "internal" }
}
```

---

## Композиция в Kotlin: сила делегирования

### Решение проблемы Bloch через композицию

```kotlin
// ✅ Композиция вместо наследования
class InstrumentedSet<E>(
    private val inner: MutableSet<E> = mutableSetOf()
) : MutableSet<E> by inner {

    var addCount = 0
        private set

    override fun add(element: E): Boolean {
        addCount++
        return inner.add(element)
    }

    override fun addAll(elements: Collection<E>): Boolean {
        addCount += elements.size
        return inner.addAll(elements) // Вызывает inner.addAll, НЕ наш add!
    }
}

val set = InstrumentedSet<String>()
set.addAll(listOf("A", "B", "C"))
println(set.addCount) // ✅ 3 -- корректно!
```

**Ключевое отличие:** `inner.addAll()` вызывает `inner.add()` -- метод самого `inner`, а не наш переопределённый. Мы больше не зависим от деталей реализации `HashSet`.

> [!info] Kotlin-нюанс
> Ключевое слово `by` генерирует все методы `MutableSet` с делегированием к `inner` **на этапе компиляции**. Это не рефлексия, не proxy -- прямые вызовы. Zero runtime overhead. В Java для аналогичного решения нужно вручную написать ~20 методов-делегатов (forwarding methods).

---

## Kotlin `by` делегирование: deep dive

### Делегирование классов (Class Delegation)

```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String)
    fun setLevel(level: Int)
}

class ConsoleLogger : Logger {
    override fun log(message: String) = println("[LOG] $message")
    override fun error(message: String) = System.err.println("[ERR] $message")
    override fun setLevel(level: Int) = println("Level set to $level")
}

// Декоратор: добавляем timestamp без наследования
class TimestampLogger(
    private val delegate: Logger
) : Logger by delegate {
    // Переопределяем только то, что нужно
    override fun log(message: String) {
        delegate.log("[${System.currentTimeMillis()}] $message")
    }
    // error() и setLevel() автоматически делегируются!
}

// Множественное делегирование: один класс, несколько интерфейсов
interface Closeable {
    fun close()
}

class ManagedLogger(
    logger: Logger,
    closeable: Closeable
) : Logger by logger, Closeable by closeable
// Все методы Logger → logger, метод close() → closeable
```

### Что генерирует компилятор

```kotlin
// Вы пишете:
class TimestampLogger(private val delegate: Logger) : Logger by delegate {
    override fun log(message: String) { /* ... */ }
}

// Компилятор генерирует:
class TimestampLogger(private val delegate: Logger) : Logger {
    override fun log(message: String) { /* ваш код */ }
    override fun error(message: String) = delegate.error(message)  // ← сгенерировано
    override fun setLevel(level: Int) = delegate.setLevel(level)   // ← сгенерировано
}
```

### Делегирование свойств (Property Delegation)

Kotlin позволяет делегировать не только интерфейсы, но и отдельные свойства:

```kotlin
import kotlin.properties.Delegates

class UserSettings {
    // lazy -- вычисляется один раз при первом доступе (thread-safe)
    val config: Map<String, String> by lazy {
        println("Загрузка конфига...")
        loadConfigFromDisk() // Дорогая операция
    }

    // observable -- уведомляет при изменении
    var theme: String by Delegates.observable("light") { prop, old, new ->
        println("Тема изменена: $old → $new")
        applyTheme(new)
    }

    // vetoable -- может отклонить изменение
    var fontSize: Int by Delegates.vetoable(14) { _, _, new ->
        new in 8..72 // Разрешаем только размеры от 8 до 72
    }

    // Делегирование к Map -- свойства из словаря
    class User(properties: Map<String, Any?>) {
        val name: String by properties
        val age: Int by properties
        val email: String by properties
    }
}

// Использование Map delegation
val user = UserSettings.User(
    mapOf("name" to "Алиса", "age" to 28, "email" to "alice@example.com")
)
println(user.name)  // "Алиса"
println(user.age)   // 28
```

### Пользовательский делегат

```kotlin
import kotlin.reflect.KProperty

// Делегат с валидацией
class Trimmed {
    private var value: String = ""

    operator fun getValue(thisRef: Any?, property: KProperty<*>): String = value

    operator fun setValue(thisRef: Any?, property: KProperty<*>, newValue: String) {
        value = newValue.trim()
    }
}

// Делегат с логированием
class Logged<T>(private var value: T) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): T {
        println("Чтение ${property.name}: $value")
        return value
    }

    operator fun setValue(thisRef: Any?, property: KProperty<*>, newValue: T) {
        println("Запись ${property.name}: $value → $newValue")
        value = newValue
    }
}

class RegistrationForm {
    var username: String by Trimmed()       // Автоматический trim
    var email: String by Trimmed()
    var debugValue: Int by Logged(0)        // Логирование доступа
}

val form = RegistrationForm()
form.username = "  Алиса  "
println(form.username) // "Алиса" -- пробелы убраны автоматически
```

---

## Когда что выбирать: Decision Framework

```
                 Нужно повторно использовать поведение?
                              │
                    ┌─────────┴─────────┐
                    │                   │
                   ДА                  НЕТ → Не наследуй, не компонуй
                    │
             Это "is-a" отношение?
            (Circle IS-A Shape?)
                    │
          ┌─────────┴─────────┐
          │                   │
         ДА                  НЕТ → Композиция
          │                        (has-a, uses-a)
     Ты контролируешь
     базовый класс?
          │
    ┌─────┴─────┐
    │           │
   ДА          НЕТ → Композиция
    │                 (нельзя гарантировать
    │                  стабильность контракта)
    │
  Набор наследников
  известен заранее?
    │
  ┌─┴────────┐
  │          │
 ДА         НЕТ → abstract class + open
  │               (Template Method)
  │
sealed class
```

### Когда наследование ПРАВИЛЬНО

| Сценарий | Почему наследование | Kotlin-инструмент |
|----------|--------------------|--------------------|
| Закрытая иерархия состояний | Все варианты известны, exhaustive when | `sealed class` / `sealed interface` |
| Шаблонный метод | Общий алгоритм + точки расширения | `abstract class` |
| Фреймворк требует | Activity, Fragment, ViewModel | `open class` (framework contract) |
| Истинное "is-a" | Circle IS-A Shape (Liskov) | `open class` + `override` |

### Когда композиция ПРАВИЛЬНО

| Сценарий | Почему композиция | Kotlin-инструмент |
|----------|-------------------|--------------------|
| "has-a" отношение | Car HAS-A Engine, не IS-A Engine | Поле + `by` делегирование |
| Добавление поведения | Logging, caching, retry | Decorator через `by` |
| Динамическая смена | Стратегия меняется в runtime | Interface + injection |
| Множественное "наследование" | Нужны возможности нескольких классов | Multiple `by` delegation |
| Нет контроля над базовым | Сторонняя библиотека | Wrapper через `by` |

---

## Before/After: рефакторинг наследования в композицию

### Пример 1: Логирование через наследование

```kotlin
// ❌ BEFORE: Наследование для переиспользования логирования
abstract class BaseRepository {
    protected fun logQuery(query: String) {
        println("[${this::class.simpleName}] Query: $query")
    }

    protected fun logError(error: Throwable) {
        System.err.println("[${this::class.simpleName}] Error: ${error.message}")
    }
}

class UserRepository : BaseRepository() {
    fun findById(id: Long): User? {
        logQuery("SELECT * FROM users WHERE id = $id")
        // ...
        return null
    }
}

class OrderRepository : BaseRepository() {
    fun findByUserId(userId: Long): List<Order> {
        logQuery("SELECT * FROM orders WHERE user_id = $userId")
        // ...
        return emptyList()
    }
}
// Проблемы:
// 1. UserRepository IS-A BaseRepository? Нет! Он ИСПОЛЬЗУЕТ логирование
// 2. Одиночное наследование: нельзя наследовать ещё и BaseCache
// 3. Все репозитории тащат логирование, даже если не нужно
```

```kotlin
// ✅ AFTER: Композиция через интерфейс + делегирование
interface RepositoryLogger {
    fun logQuery(source: String, query: String)
    fun logError(source: String, error: Throwable)
}

class ConsoleRepositoryLogger : RepositoryLogger {
    override fun logQuery(source: String, query: String) {
        println("[$source] Query: $query")
    }
    override fun logError(source: String, error: Throwable) {
        System.err.println("[$source] Error: ${error.message}")
    }
}

class UserRepository(
    private val logger: RepositoryLogger
) {
    fun findById(id: Long): User? {
        logger.logQuery("UserRepository", "SELECT * FROM users WHERE id = $id")
        return null
    }
}

// Легко подменить в тестах:
class FakeLogger : RepositoryLogger {
    val queries = mutableListOf<String>()
    override fun logQuery(source: String, query: String) { queries.add(query) }
    override fun logError(source: String, error: Throwable) {}
}
```

### Пример 2: Android ViewModel с делегированием

```kotlin
// ❌ BEFORE: Базовый ViewModel со всем подряд
abstract class BaseViewModel : ViewModel() {
    protected val _loading = MutableStateFlow(false)
    val loading: StateFlow<Boolean> = _loading.asStateFlow()

    protected val _error = MutableSharedFlow<String>()
    val error: SharedFlow<String> = _error.asSharedFlow()

    protected fun launchSafe(block: suspend () -> Unit) {
        viewModelScope.launch {
            try {
                _loading.value = true
                block()
            } catch (e: Exception) {
                _error.emit(e.message ?: "Unknown error")
            } finally {
                _loading.value = false
            }
        }
    }
}

// Каждый ViewModel наследует ВСЁ, даже если не нужно:
class ProfileViewModel : BaseViewModel() { /* ... */ }
class SettingsViewModel : BaseViewModel() { /* ... */ }
```

```kotlin
// ✅ AFTER: Композиция через делегирование
interface LoadingState {
    val loading: StateFlow<Boolean>
    fun setLoading(isLoading: Boolean)
}

class LoadingStateImpl : LoadingState {
    private val _loading = MutableStateFlow(false)
    override val loading: StateFlow<Boolean> = _loading.asStateFlow()
    override fun setLoading(isLoading: Boolean) { _loading.value = isLoading }
}

interface ErrorHandler {
    val errors: SharedFlow<String>
    suspend fun emitError(message: String)
}

class ErrorHandlerImpl : ErrorHandler {
    private val _errors = MutableSharedFlow<String>()
    override val errors: SharedFlow<String> = _errors.asSharedFlow()
    override suspend fun emitError(message: String) { _errors.emit(message) }
}

// ViewModel берёт только то, что нужно:
class ProfileViewModel(
    loadingState: LoadingState = LoadingStateImpl(),
    errorHandler: ErrorHandler = ErrorHandlerImpl()
) : ViewModel(),
    LoadingState by loadingState,
    ErrorHandler by errorHandler {

    fun loadProfile(userId: String) {
        viewModelScope.launch {
            setLoading(true)
            try {
                // загрузка профиля
            } catch (e: Exception) {
                emitError(e.message ?: "Ошибка загрузки")
            } finally {
                setLoading(false)
            }
        }
    }
}

// SettingsViewModel может взять только LoadingState, без ErrorHandler
class SettingsViewModel(
    loadingState: LoadingState = LoadingStateImpl()
) : ViewModel(), LoadingState by loadingState { /* ... */ }
```

### Пример 3: UseCase-композиция в Clean Architecture

```kotlin
// Каждый UseCase -- маленький, тестируемый, композируемый
interface UseCase<in P, out R> {
    suspend operator fun invoke(params: P): Result<R>
}

class ValidateEmailUseCase : UseCase<String, Boolean> {
    override suspend fun invoke(params: String): Result<Boolean> {
        return Result.success(params.contains("@") && params.contains("."))
    }
}

class CreateUserUseCase(
    private val validateEmail: ValidateEmailUseCase,
    private val userRepository: UserRepository,
    private val notificationService: NotificationService
) : UseCase<CreateUserParams, User> {

    override suspend fun invoke(params: CreateUserParams): Result<User> {
        // Композиция: каждый шаг -- отдельный UseCase или сервис
        val isValid = validateEmail(params.email).getOrElse { return Result.failure(it) }
        if (!isValid) return Result.failure(InvalidEmailException(params.email))

        val user = userRepository.create(params)
        notificationService.sendWelcome(user)
        return Result.success(user)
    }
}

data class CreateUserParams(val name: String, val email: String)
```

---

## Паттерны проектирования: наследование vs композиция

| Паттерн | Наследование (GoF) | Композиция (Kotlin) |
|---------|--------------------|--------------------|
| **Decorator** | `class LoggingList extends ListDecorator` | `class LoggingList(list: List) : List by list` |
| **Strategy** | `abstract class Sorter` + подклассы | `fun sort(comparator: (T, T) -> Int)` |
| **Template Method** | `abstract class` + `override` | `abstract class` (здесь наследование уместно) |
| **Observer** | `extends Observable` | `Delegates.observable {}` или `Flow` |
| **Adapter** | `class Adapter extends Target` | `class Adapter(adaptee: Adaptee) : Target by ...` |
| **Proxy** | `class Proxy extends RealSubject` | `class Proxy(real: Subject) : Subject by real` |

---

## Подводные камни

### 1. Делегат не видит переопределённых методов

```kotlin
interface Printer {
    fun printHeader()
    fun printBody()
    fun printAll() {
        printHeader()
        printBody()
    }
}

class DefaultPrinter : Printer {
    override fun printHeader() = println("=== Header ===")
    override fun printBody() = println("Body content")
}

class CustomPrinter(printer: Printer) : Printer by printer {
    override fun printHeader() = println("*** Custom Header ***")
}

val custom = CustomPrinter(DefaultPrinter())
custom.printAll()
// Выведет:
// === Header ===     ← НЕ "*** Custom Header ***"!
// Body content
```

**Почему?** `printAll()` делегирован `DefaultPrinter`, и внутри `DefaultPrinter.printAll()` вызывается `DefaultPrinter.printHeader()`, а не `CustomPrinter.printHeader()`. Делегат не знает о переопределениях в обёртке.

**Решение:** Переопределите `printAll()` тоже:

```kotlin
class CustomPrinter(private val printer: Printer) : Printer by printer {
    override fun printHeader() = println("*** Custom Header ***")
    override fun printAll() {
        printHeader()   // Наш метод
        printer.printBody()
    }
}
```

### 2. Наследование sealed class -- не от хорошей жизни

```kotlin
// ❌ Sealed class как замена enum -- overkill
sealed class Color {
    data object Red : Color()
    data object Green : Color()
    data object Blue : Color()
}
// Если все варианты одинаковой структуры → используй enum class

// ✅ Sealed class -- когда структура РАЗНАЯ
sealed class Shape {
    data class Circle(val radius: Double) : Shape()
    data class Rectangle(val width: Double, val height: Double) : Shape()
    data class Triangle(val a: Double, val b: Double, val c: Double) : Shape()
}
```

### 3. `by` не работает с абстрактными классами

```kotlin
// ❌ Нельзя:
// class MyList(list: AbstractList<Int>) : AbstractList<Int> by list

// ✅ Можно только с интерфейсами:
class MyList(list: MutableList<Int>) : MutableList<Int> by list
```

### 4. Утечка мутабельного состояния

```kotlin
// ❌ Делегат мутабелен -- внешний код может его изменить
val list = mutableListOf(1, 2, 3)
val instrumentedList = InstrumentedSet(list)
list.add(4) // Обходим InstrumentedSet! addCount не увеличился

// ✅ Защитная копия
class InstrumentedSet<E>(
    innerSet: MutableSet<E>
) : MutableSet<E> by innerSet.toMutableSet() // Копия!
```

---

## Сравнение: наследование vs композиция vs делегирование

```
┌─────────────────────┬────────────────────┬────────────────────┬────────────────────┐
│   Критерий          │   Наследование     │   Композиция       │   by-делегирование │
├─────────────────────┼────────────────────┼────────────────────┼────────────────────┤
│ Связность           │ Тесная             │ Слабая             │ Слабая             │
│ Полиморфизм         │ Да (is-a)          │ Нет (has-a)        │ Да (реализует      │
│                     │                    │                    │ интерфейс)         │
│ Множественное       │ Нет (1 класс)      │ Да (N полей)       │ Да (N интерфейсов) │
│ Runtime-замена      │ Нет                │ Да                 │ Нет*               │
│ Boilerplate         │ Минимум            │ Много              │ Минимум            │
│ Доступ к protected  │ Да                 │ Нет                │ Нет                │
│ Fragile Base Class  │ Подвержено         │ Защищено           │ Защищено           │
│ Overhead            │ Нулевой            │ Зависит            │ Нулевой            │
└─────────────────────┴────────────────────┴────────────────────┴────────────────────┘

* Делегат фиксируется в конструкторе, но можно обойти через var:
  class Proxy(var delegate: Logger) : Logger by delegate  // ❌ Не работает!
  // by захватывает delegate в момент создания, замена var не повлияет
```

---

## Проверь себя

> [!question]- 1. Почему `Stack extends Vector` в Java -- ошибка дизайна? Как бы вы сделали Stack в Kotlin?
> Stack НЕ является Vector. Stack поддерживает LIFO (push/pop/peek), а Vector -- произвольный доступ по индексу. Наследование от Vector даёт Stack-у методы `add(index, element)`, `remove(index)`, `get(index)` -- все нарушают контракт LIFO. В Kotlin: `class Stack<T>(private val list: MutableList<T> = mutableListOf())` с методами `push()`, `pop()`, `peek()`. Не реализуем `MutableList`, не наследуем -- просто используем внутренне.

> [!question]- 2. Чем делегирование `by` отличается от наследования с точки зрения вызова методов? В чём подводный камень?
> При наследовании, если базовый метод `A()` вызывает виртуальный метод `B()`, и подкласс переопределяет `B()`, то `A()` вызовет переопределённый `B()`. При делегировании `by`, если делегат вызывает `B()` из `A()`, он вызывает **свой** `B()`, а не переопределённый в обёртке. Обёртка "не видна" делегату. Подводный камень: если вы переопределяете `B()` в обёртке, а делегат внутренне вызывает `B()` из другого метода -- ваше переопределение будет проигнорировано.

> [!question]- 3. Когда sealed class -- правильный выбор для наследования, а когда это overkill?
> `sealed class` правилен когда: (1) набор вариантов фиксирован и полностью известен в compile-time; (2) каждый вариант несёт разную структуру данных; (3) нужен exhaustive `when`. Overkill когда: (1) все варианты имеют одинаковые поля → `enum class`; (2) набор должен расширяться внешними модулями → обычный `interface` или `abstract class`; (3) один вариант → обычный `data class`.

> [!question]- 4. Как бы вы переписали код, где 5 ViewModel наследуют BaseViewModel с 300 строками общей логики?
> Выделить отдельные аспекты BaseViewModel в интерфейсы: `LoadingState`, `ErrorHandler`, `NavigationHandler`, `AnalyticsTracker`. Для каждого создать реализацию. Каждый ViewModel берёт только нужные интерфейсы через `by`-делегирование. Например: `class ProfileViewModel : ViewModel(), LoadingState by LoadingStateImpl(), ErrorHandler by ErrorHandlerImpl()`. Результат: каждый ViewModel декларирует свои зависимости, нет мёртвого кода, каждый аспект тестируется отдельно.

---

## Ключевые карточки

Что такое Fragile Base Class Problem?
?
Изменение базового класса ломает наследников, которые зависят от деталей реализации. Пример: `HashSet.addAll()` вызывает `add()` внутри -- переопределение `add()` в наследнике неожиданно удваивает счётчик. Решение: композиция вместо наследования -- обёртка делегирует вызовы, не зависит от внутренней реализации.

Почему Kotlin делает классы final по умолчанию?
?
Следует принципу Bloch (Effective Java Item 17): "Design and document for inheritance, or prohibit it." Большинство классов не спроектированы для наследования. `final` по умолчанию заставляет автора осознанно открывать класс через `open`, продумывая контракт. Предотвращает Fragile Base Class Problem.

Как работает `by`-делегирование классов в Kotlin?
?
`class Wrapper(delegate: Interface) : Interface by delegate` -- компилятор генерирует все методы Interface с перенаправлением к delegate. Не рефлексия -- прямые вызовы в байткоде. Можно переопределить отдельные методы. Ограничение: работает только с интерфейсами, не с абстрактными классами.

В чём разница между `lazy`, `observable` и `vetoable` делегатами?
?
`by lazy { }` -- значение вычисляется один раз при первом доступе, потокобезопасно. `by Delegates.observable(initial) { _, old, new -> }` -- callback после каждого изменения значения. `by Delegates.vetoable(initial) { _, old, new -> boolean }` -- callback может отклонить изменение, вернув false.

Когда наследование предпочтительнее композиции?
?
(1) Sealed class для закрытых иерархий с exhaustive when. (2) Abstract class для Template Method -- фиксированный алгоритм с переопределяемыми шагами. (3) Framework requirements -- Activity, Fragment, ViewModel. (4) Истинное is-a с гарантией Liskov Substitution Principle. Во всех остальных случаях -- композиция.

Что такое Gorilla-Banana Problem?
?
Метафора Джо Армстронга: при наследовании вы получаете не только нужный метод ("банан"), но и весь класс ("гориллу") со всеми его зависимостями ("джунглями"). Наследование Stack от Vector даёт Stack все методы Vector, нарушая LIFO-контракт. Композиция берёт только нужное.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Фундамент | [[coupling-cohesion]] | Композиция снижает coupling -- разобраться почему |
| Фундамент | [[solid-principles]] | LSP и OCP определяют границы наследования |
| Паттерны | [[decorator-pattern]] | Главный паттерн, упрощённый через `by` |
| Паттерны | [[design-patterns-overview]] | Как GoF-паттерны меняются в Kotlin |
| Kotlin | [[kotlin-oop]] | Подробно о sealed class, data class, companion |
| Kotlin | [[kotlin-advanced-features]] | Extension functions, inline, reified |
| Практика | [[oop-fundamentals]] | Основы ООП: инкапсуляция, полиморфизм, абстракция |

---

## Источники

- Gamma E., Helm R., Johnson R., Vlissides J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software*. -- Принцип "Favor object composition over class inheritance", паттерны Decorator, Strategy, Proxy.
- Bloch J. (2018). *Effective Java, 3rd Edition*. -- Item 18: "Favor composition over inheritance"; Item 17: "Design and document for inheritance, or prohibit it". Пример `InstrumentedHashSet`.
- Москала М. (2021). *Effective Kotlin*. -- Item 36: "Prefer composition over inheritance". Kotlin-специфичные примеры с `by`-делегированием.
- Martin R. (2017). *Clean Architecture*. -- Принципы компонентного дизайна, направление зависимостей, Dependency Rule.
- [Kotlin Documentation: Delegation](https://kotlinlang.org/docs/delegation.html) -- Официальная документация по class delegation.
- [Kotlin Documentation: Delegated Properties](https://kotlinlang.org/docs/delegated-properties.html) -- lazy, observable, vetoable, map delegation.
- [Composition over Inheritance -- Wikipedia](https://en.wikipedia.org/wiki/Composition_over_inheritance) -- Обзор принципа, исторические ссылки.
- [Fragile Base Class -- Wikipedia](https://en.wikipedia.org/wiki/Fragile_base_class) -- Описание проблемы, примеры, решения.

---

*Проверено: 2026-02-19 | Источники: Effective Java, GoF, Effective Kotlin, Kotlin Docs, Wikipedia*
