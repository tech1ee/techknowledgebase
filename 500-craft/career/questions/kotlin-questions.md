---
title: "Kotlin Interview Questions 2025: 40+ вопросов с ответами"
created: 2025-12-26
modified: 2026-02-13
type: reference
status: published
confidence: high
tags:
  - topic/career
  - type/reference
  - level/intermediate
  - interview
related:
  - "[[android-questions]]"
  - "[[architecture-questions]]"
  - "[[technical-interview]]"
prerequisites:
  - "[[interview-process]]"
reading_time: 16
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Kotlin Interview Questions: от basics до advanced

Kotlin — default язык для Android с 2019. В 2025 году знание Kotlin обязательно: Coroutines, Flow, sealed classes, extension functions. Senior позиции требуют понимания под капотом: inline, reified, delegation. Этот справочник — 40+ вопросов разного уровня сложности.

---

## Basics

### В чём разница между val и var?

```kotlin
val name = "John"  // immutable reference (final в Java)
// name = "Jane"   // Compile error!

var age = 25       // mutable reference
age = 26           // OK

Важно: val гарантирует immutability REFERENCE, не object.

val list = mutableListOf(1, 2, 3)
list.add(4)  // OK! List mutable, reference immutable
```

### Что такое Null Safety в Kotlin?

```kotlin
// Nullable types
var name: String? = null     // может быть null
var age: String = "text"     // не может быть null

// Safe call
val length = name?.length    // null если name null

// Elvis operator
val len = name?.length ?: 0  // default если null

// Not-null assertion (опасно!)
val len = name!!.length      // throws NPE если null

// Smart cast
if (name != null) {
    println(name.length)     // автоматически cast к non-null
}
```

### Что такое Data Class?

```kotlin
data class User(val name: String, val age: Int)

// Автоматически генерирует:
// - equals() / hashCode()
// - toString() → "User(name=John, age=25)"
// - copy() → user.copy(name = "Jane")
// - componentN() → val (name, age) = user

// Требования:
// - Primary constructor должен иметь хотя бы 1 параметр
// - Параметры должны быть val или var
// - Не может быть abstract, open, sealed, inner
```

### В чём разница между == и ===?

```kotlin
val a = "hello"
val b = "hello"
val c = String("hello".toCharArray())

a == b   // true  — structural equality (equals())
a === b  // true  — referential equality (same object, string pool)
a == c   // true  — structural equality
a === c  // false — different objects
```

---

## OOP

### Что такое Sealed Class?

```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// Использование в when — exhaustive check
fun handle(result: Result<String>) = when (result) {
    is Result.Success -> println(result.data)
    is Result.Error -> println(result.message)
    is Result.Loading -> println("Loading...")
    // no else needed — compiler knows all cases
}

// Применение:
// - State management (MVI)
// - Network responses
// - Navigation events
```

### В чём разница между object и companion object?

```kotlin
// Object — Singleton
object DatabaseManager {
    fun connect() { }
}
DatabaseManager.connect()

// Companion Object — static-like members в class
class User {
    companion object {
        const val TABLE = "users"
        fun create(): User = User()
    }
}
User.TABLE
User.create()

// Companion может implement interface
class Factory {
    companion object : Serializable { }
}
```

### Что такое Extension Functions?

```kotlin
// Добавляем функцию к существующему классу
fun String.addExclamation() = "$this!"
"Hello".addExclamation()  // "Hello!"

// Extension property
val String.lastChar: Char
    get() = this[length - 1]

// Под капотом — static function:
// static String addExclamation(String $this) { ... }

// Ограничения:
// - Не могут access private members
// - Resolved статически (не polymorphic)
// - Member function wins если signature совпадает
```

### Что такое Delegation?

```kotlin
// Class delegation
interface Printer { fun print() }

class RealPrinter : Printer {
    override fun print() = println("Printing...")
}

class PrinterDelegate(printer: Printer) : Printer by printer
// Все методы Printer делегируются printer

// Property delegation
val lazyValue: String by lazy {
    println("Computed!")
    "Hello"
}
// Вычисляется только при первом доступе

// Built-in delegates:
// - lazy { } — lazy initialization
// - observable { } — react to changes
// - vetoable { } — validate before change
// - by map — read from Map
```

---

## Coroutines

### Что такое suspend function?

```kotlin
suspend fun fetchData(): Data {
    delay(1000)  // non-blocking wait
    return api.getData()
}

// Под капотом:
// - Компилируется в state machine
// - Continuation-Passing Style (CPS)
// - Может быть приостановлена и возобновлена

// Можно вызвать только из:
// - Другой suspend function
// - Coroutine scope (launch, async)

// Нельзя вызвать из обычной функции:
fun bad() {
    fetchData()  // Compile error!
}
```

### Что такое Dispatchers?

```kotlin
Dispatchers.Main      // UI thread (Android)
Dispatchers.IO        // Optimized for I/O (network, disk)
Dispatchers.Default   // CPU-intensive work
Dispatchers.Unconfined // Starts in caller thread

// Использование:
withContext(Dispatchers.IO) {
    val data = readFromFile()
}

// Default vs IO:
// Default: limited to CPU cores
// IO: can scale up to 64 threads (or core count if higher)
```

### Как работает Job и structured concurrency?

```kotlin
val job = scope.launch {
    // coroutine body
}

job.cancel()      // отмена
job.join()        // wait for completion
job.isActive      // проверка состояния

// Structured concurrency:
scope.launch {           // parent
    launch { task1() }   // child 1
    launch { task2() }   // child 2
}
// Если parent отменён → все children отменяются
// Если child throws → parent и siblings отменяются (обычный Job)
// Если child throws → только этот child fails (SupervisorJob)
```

### Что такое Flow?

```kotlin
// Cold stream — emits when collected
fun numbers(): Flow<Int> = flow {
    for (i in 1..3) {
        delay(100)
        emit(i)
    }
}

// Collecting
numbers().collect { value ->
    println(value)
}

// Operators
numbers()
    .filter { it > 1 }
    .map { it * 2 }
    .catch { e -> emit(-1) }
    .collect { println(it) }

// StateFlow vs SharedFlow
val state = MutableStateFlow(0)     // has initial value
val events = MutableSharedFlow<Event>()  // no initial value
```

### В чём разница между Flow, StateFlow и SharedFlow?

```kotlin
Flow (Cold):
├── Starts emission when collected
├── Each collector gets all values from start
├── Use for: database queries, API calls
└── val flow = flow { emit(1) }

StateFlow (Hot):
├── Always has current value
├── New collectors get current value immediately
├── distinctUntilChanged by default
├── Use for: UI state
└── val state = MutableStateFlow(initialValue)

SharedFlow (Hot):
├── Can have no initial value
├── Configurable replay buffer
├── Use for: events (navigation, snackbar)
└── val events = MutableSharedFlow<Event>(replay = 0)
```

---

## Advanced

### Что такое inline и reified?

```kotlin
// Inline function — body вставляется в call site
inline fun measure(block: () -> Unit) {
    val start = System.currentTimeMillis()
    block()
    println("Took ${System.currentTimeMillis() - start}ms")
}

// Без inline: lambda = object allocation
// С inline: no allocation, code copied

// Reified — сохраняет generic type в runtime
inline fun <reified T> isInstance(obj: Any): Boolean {
    return obj is T  // Possible because reified!
}

isInstance<String>("hello")  // true
isInstance<Int>("hello")     // false

// Без reified это невозможно (type erasure)
```

### Что такое Contracts?

```kotlin
import kotlin.contracts.*

fun require(condition: Boolean) {
    contract {
        returns() implies condition
    }
    if (!condition) throw IllegalArgumentException()
}

// Smart cast после require:
fun process(x: String?) {
    require(x != null)
    println(x.length)  // Smart cast работает!
}
```

### Как работает Kotlin under the hood?

```kotlin
// Data class
data class User(val name: String)
// → generates: equals, hashCode, toString, copy, componentN

// Extension function
fun String.exclaim() = "$this!"
// → static method: StringExtKt.exclaim(String)

// Object
object Singleton { }
// → class with private constructor + INSTANCE field

// Companion object
class X { companion object { } }
// → nested class X$Companion + static INSTANCE
```

---

## Collections

### В чём разница между List и MutableList?

```kotlin
val immutable: List<Int> = listOf(1, 2, 3)
// immutable.add(4)  // Compile error!

val mutable: MutableList<Int> = mutableListOf(1, 2, 3)
mutable.add(4)  // OK

// List — read-only VIEW (может быть backed by mutable)
val mList = mutableListOf(1, 2, 3)
val view: List<Int> = mList
mList.add(4)
println(view)  // [1, 2, 3, 4] — view reflects changes!

// True immutable:
val truly = listOf(1, 2, 3).toList()  // defensive copy
// Or use kotlinx.collections.immutable
```

### Какие collection operations ты используешь чаще всего?

```kotlin
val list = listOf(1, 2, 3, 4, 5)

// Transformation
list.map { it * 2 }           // [2, 4, 6, 8, 10]
list.filter { it > 2 }        // [3, 4, 5]
list.flatMap { listOf(it, it) } // [1, 1, 2, 2, ...]

// Aggregation
list.reduce { acc, n -> acc + n }  // 15
list.fold(10) { acc, n -> acc + n } // 25

// Grouping
list.groupBy { it % 2 }  // {1=[1,3,5], 0=[2,4]}
list.partition { it > 3 } // Pair([4,5], [1,2,3])

// Finding
list.find { it > 3 }      // 4 (first match or null)
list.first { it > 3 }     // 4 (throws if none)
list.any { it > 3 }       // true
list.all { it > 0 }       // true
```

### Sequences vs Collections

```kotlin
// Collection — eager evaluation
listOf(1, 2, 3, 4, 5)
    .map { println("map $it"); it * 2 }
    .filter { println("filter $it"); it > 4 }
    .first()
// Prints: map 1, map 2, map 3, map 4, map 5,
//         filter 2, filter 4, filter 6, filter 8, filter 10

// Sequence — lazy evaluation
listOf(1, 2, 3, 4, 5)
    .asSequence()
    .map { println("map $it"); it * 2 }
    .filter { println("filter $it"); it > 4 }
    .first()
// Prints: map 1, filter 2, map 2, filter 4, map 3, filter 6
// Stops as soon as first() found!

// Используй Sequence когда:
// - Large collections
// - Multiple intermediate operations
// - Early termination possible (first, find)
```

---

## Scope Functions

### let, run, with, apply, also — когда что?

```kotlin
// LET — null check + transformation
val length = name?.let { it.length }

// RUN — execute block on object
val result = service.run {
    connect()
    query()
}

// WITH — configure object (non-null)
with(config) {
    host = "localhost"
    port = 8080
}

// APPLY — configure and return same object
val user = User().apply {
    name = "John"
    age = 25
}

// ALSO — side effects, return same object
return user.also {
    logger.log("Created $it")
}

// Мнемоника:
// Return object: apply, also
// Return lambda result: let, run, with

// this vs it:
// this: run, with, apply
// it: let, also
```

---

## Quick Reference

| Concept | Java Equivalent | Kotlin |
|---------|-----------------|--------|
| Final variable | final String x | val x: String |
| Singleton | private constructor + getInstance | object X |
| Static method | static void foo() | companion object { fun foo() } |
| Optional | Optional<T> | T? (nullable type) |
| Anonymous class | new Interface() { } | object : Interface { } |
| Lambda | (x) -> x + 1 | { x -> x + 1 } или ::function |

---

## Связь с другими темами

- **[[android-questions]]** — Kotlin — язык Android-разработки, и на интервью вопросы по Kotlin и Android тесно переплетаются. Coroutines и Flow появляются и в Kotlin-раунде, и в Android-раунде. Глубокое владение Kotlin (inline, reified, contracts) даёт преимущество в обоих типах вопросов.

- **[[architecture-questions]]** — Архитектурные паттерны (MVI, Clean Architecture) реализуются на Kotlin, и знание языковых возможностей (sealed classes, delegation, extension functions) напрямую влияет на качество архитектурных решений. Интервьюеры оценивают, насколько идиоматично ты используешь Kotlin в архитектуре.

- **[[technical-interview]]** — Kotlin-вопросы — один из столпов технического раунда для Android-позиций. Понимание формата технического интервью помогает правильно расставить приоритеты: basics обязательны, advanced (contracts, context receivers) — для Staff+ позиций. Формат ответа так же важен, как содержание.

---

## Источники и дальнейшее чтение

- **McDowell G.L. (2015). Cracking the Coding Interview.** — Хотя примеры на Java, методология решения алгоритмических задач полностью применима к Kotlin. Главы о подходе к задачам, оптимизации решений и обсуждении trade-offs — универсальные навыки.

- **Xu A. (2020). System Design Interview.** — Kotlin используется не только для UI, но и для System Design решений (KMP, backend). Понимание системного дизайна помогает отвечать на вопросы о Kotlin в контексте больших систем, а не изолированных функций.

---

## Источники

- [InterviewBit: Kotlin Questions](https://www.interviewbit.com/kotlin-interview-questions/)
- [Hackr.io: 40 Kotlin Questions](https://hackr.io/blog/kotlin-interview-questions)
- [Curotec: 125 Android/Kotlin Questions](https://www.curotec.com/interview-questions/125-android-kotlin-interview-questions/)
- [Second Talent: 30 Advanced Kotlin](https://www.secondtalent.com/interview-guide/kotlin/)

---

## Куда дальше

### Углубить понимание Kotlin

**Coroutines и concurrency:**
→ [[kotlin-coroutines]] — suspend functions, Job, Dispatchers, structured concurrency
→ [[kotlin-flow]] — Flow operators, StateFlow, SharedFlow
→ [[jvm-concurrency-overview]] — как coroutines работают на уровне JVM

**Языковые возможности:**
→ [[kotlin-type-system]] — generics, variance (in/out), reified
→ [[kotlin-functional]] — lambdas, scope functions, DSL

### Связь с Android

→ [[android-questions]] — как Kotlin применяется в Android
→ [[architecture-questions]] — архитектурные паттерны с Kotlin

---

---

## Проверь себя

> [!question]- val гарантирует immutability reference, но не object. Приведи пример, где val list может измениться, и как обеспечить true immutability.
> val list = mutableListOf(1, 2, 3) — reference immutable (нельзя переназначить), но list.add(4) работает. True immutability: (1) listOf() — read-only view, но backing collection может быть mutable. (2) Defensive copy: listOf(1,2,3).toList(). (3) kotlinx.collections.immutable — настоящие persistent immutable collections. На интервью важно объяснить разницу между read-only view и true immutability.

> [!question]- Зачем нужны inline functions и reified generics? Приведи практический пример, невозможный без reified.
> inline: тело функции вставляется в call site, избегая allocation lambda-объекта. reified: сохраняет generic type в runtime (обходит type erasure JVM). Пример: inline fun <reified T> isInstance(obj: Any) = obj is T — без reified невозможна проверка is T, потому что T стирается в runtime. Практическое применение: Json.decodeFromString<MyClass>(json) — парсинг JSON с reified type.

> [!question]- Sequence vs Collection — когда sequence быстрее и когда нет?
> Sequence быстрее когда: (1) large collections, (2) multiple intermediate operations (map, filter), (3) early termination (first, find) — lazy evaluation останавливается при первом match. Collection быстрее когда: (1) small collections (overhead lazy evaluation не оправдан), (2) single operation, (3) нужен random access. Sequence обрабатывает element-by-element (vertical), Collection — operation-by-operation (horizontal).

> [!question]- Чем extension function отличается от member function внутри класса и какие ограничения есть?
> Extension function: (1) resolved статически (не polymorphic) — при вызове через base class используется extension base, не derived. (2) Не может access private members класса. (3) Если signature совпадает с member function — member wins. Под капотом — static function: fun String.exclaim() компилируется в StringExtKt.exclaim(String). Member function: полиморфная, доступ ко всему внутреннему состоянию.

---

## Ключевые карточки

val vs var — ключевая разница?
?
val: immutable reference (final в Java), нельзя переназначить. var: mutable reference. Важно: val гарантирует immutability reference, не object. val list = mutableListOf() — list.add() работает.

Sealed class — зачем нужна?
?
Ограниченная иерархия: все подклассы известны compile-time. when expression — exhaustive check (no else needed). Применение: state management (MVI), network responses (Success/Error/Loading), navigation events.

5 scope functions — когда какую?
?
let: null check + transformation (it, return lambda). run: execute block на объекте (this, return lambda). with: configure non-null объект (this, return lambda). apply: configure и вернуть объект (this, return object). also: side effects, вернуть объект (it, return object).

suspend function — что под капотом?
?
Компилируется в state machine через Continuation-Passing Style (CPS). Может быть приостановлена и возобновлена. Вызывается только из другой suspend function или coroutine scope. Под капотом: каждая suspend point — новое state в state machine.

Dispatchers — 4 вида?
?
Main: UI thread (Android). IO: оптимизирован для I/O (network, disk), до 64 threads. Default: CPU-intensive work, limited to CPU cores. Unconfined: стартует в caller thread, не переключается.

Flow vs StateFlow vs SharedFlow?
?
Flow (cold): emits при collection, каждый collector получает все values. StateFlow (hot): всегда имеет current value, distinctUntilChanged, для UI state. SharedFlow (hot): configurable replay, для events (navigation, snackbar).

Delegation в Kotlin — виды?
?
Class delegation: interface Printer by printer — делегирует все методы. Property delegation: by lazy (lazy init), by observable (react to changes), by vetoable (validate), by map (read from Map).

Kotlin under the hood — что генерируется?
?
data class: equals, hashCode, toString, copy, componentN. Extension: static method. object: class с private constructor + INSTANCE field. Companion object: nested class + static INSTANCE.

---

## Куда дальше

| Направление | Ссылка | Зачем |
|-------------|--------|-------|
| Следующий шаг | [[android-questions]] | Kotlin в контексте Android-интервью |
| Углубиться | [[kotlin-coroutines]] | Coroutine internals: Continuation, Dispatchers, Job hierarchy |
| Смежная тема | [[kotlin-type-system]] | Generics, variance (in/out), reified — глубже |
| Обзор | [[technical-interview]] | Формат технического раунда и приоритеты |

---

*Обновлено: 2026-02-13*

---

*Проверено: 2026-02-13*
