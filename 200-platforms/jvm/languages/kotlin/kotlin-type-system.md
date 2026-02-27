---
title: "Kotlin Type System: Generics, Variance, Reified Types"
created: 2025-11-25
modified: 2026-02-13
tags:
  - topic/jvm
  - generics
  - variance
  - type-system
  - contracts
  - reified
  - type/concept
  - level/intermediate
reading_time: 27
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[kotlin-basics]]"
  - "[[kotlin-oop]]"
  - "[[kotlin-functional]]"
related:
  - "[[kotlin-collections]]"
  - "[[kotlin-advanced-features]]"
  - "[[kotlin-functional]]"
  - "[[kotlin-best-practices]]"
status: published
---

# Kotlin Type System: Generics и Variance

> **TL;DR:** Kotlin решает type erasure через `reified` типы в inline функциях. Variance определяет подстановку: `out T` (covariance) — читаем, `List<Dog>` → `List<Animal>`. `in T` (contravariance) — пишем, `Comparator<Animal>` → `Comparator<Dog>`. Contracts (`@OptIn(ExperimentalContracts::class)`) информируют компилятор о гарантиях для smart casts.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Kotlin basics** | Синтаксис, null-safety | [[kotlin-basics]] |
| **OOP concepts** | Наследование, полиморфизм | [[kotlin-oop]] |
| **Java Generics** | Понимание type erasure | [Oracle Tutorial](https://docs.oracle.com/javase/tutorial/java/generics/) |
| **Collections** | List, Set, Map variance | [[kotlin-collections]] |
| **Functional types** | Lambda, function types | [[kotlin-functional]] |

---

## Зачем это нужно

### Проблема: Type Safety vs Гибкость

| Проблема | Пример |
|----------|--------|
| **Type Erasure** | `List<String>` и `List<Int>` неразличимы в runtime |
| **Безопасная подстановка** | Можно ли передать `List<Dog>` вместо `List<Animal>`? |
| **Проверка типа в runtime** | `value is T` не работает с generics |
| **Smart Casts не работают** | После `if (x is String)` компилятор "забывает" тип |

### Что даёт понимание Type System

```
Без понимания:                     С пониманием:
┌──────────────────┐               ┌──────────────────┐
│ as? везде        │               │ Smart Casts      │
│ ClassCastException│              │ Type-safe APIs   │
│ List<*> хаос     │               │ Variance in/out  │
│ Generics = магия │               │ Reified types    │
└──────────────────┘               └──────────────────┘
```

### Ключевые концепции Kotlin Type System

1. **Null Safety** — два типа: `String` и `String?`
2. **Smart Casts** — автоматическое приведение после проверки типа
3. **Variance** — `in T` (contravariance), `out T` (covariance)
4. **Reified Types** — сохранение типа в runtime через inline
5. **Contracts** — подсказки компилятору для smart casts

### Актуальность 2024-2025

| Фича | Статус | Что нового |
|------|--------|------------|
| **K2 Compiler** | ✅ Kotlin 2.0+ | Улучшенный type inference, быстрее smart casts |
| **Contracts** | ⚠️ Experimental | @OptIn(ExperimentalContracts::class) всё ещё нужен |
| **Context Parameters** | ⚠️ Preview | KEEP-259: замена context receivers |
| **Value classes** | ✅ Stable | `@JvmInline value class` для type-safe wrappers |
| **Definite assignment** | ✅ K2 | Лучший анализ инициализации val |

**Тренды 2025:**
- K2 compiler — значительно улучшенный type inference
- Smart casts работают в большем количестве случаев
- Value classes для zero-overhead type safety

---

## Теоретические основы: формальный базис системы типов

### Subtyping Theory (Liskov, 1987; Cardelli, 1984)

> **Subtyping** — отношение между типами: `A <: B` означает, что значение типа A можно использовать везде, где ожидается B. Kotlin реализует **nominal subtyping**: `class Dog : Animal()` создаёт `Dog <: Animal`.

**Liskov Substitution Principle** (1987) формализует: если `S <: T`, то объекты типа T можно заменить на объекты типа S без нарушения корректности программы.

### Variance: Covariance и Contravariance

> **Variance** определяет, как subtyping типовых параметров влияет на subtyping параметризованных типов. Формально (Cardelli & Wegner, 1985):

| Variance | Определение | Kotlin | Позиция параметра |
|----------|-------------|--------|-------------------|
| **Covariance** | `A <: B ⇒ F<A> <: F<B>` | `out T` | Только в return (output) |
| **Contravariance** | `A <: B ⇒ F<B> <: F<A>` | `in T` | Только в параметрах (input) |
| **Invariance** | Ни то, ни другое | `T` (default) | Любая позиция |

Это PECS (Producer Extends, Consumer Super) из Java, формализованное на уровне declaration-site.

### Nothing как Bottom Type

> **Bottom type** (⊥) — тип, являющийся подтипом **всех** типов: `∀T. Nothing <: T`. В теории типов это **initial object** в категории типов.

Kotlin `Nothing`:
- `throw` имеет тип `Nothing` (функция, которая никогда не возвращает)
- `emptyList<Nothing>()` можно присвоить `List<любой_тип>` (благодаря covariance `out T`)
- `Nothing?` содержит единственное значение `null` — это **unit type** для nullable hierarchy

Dual: `Any` — **top type** (⊤): `∀T. T <: Any`.

### Type Erasure и Reification

> **Type erasure** — стирание типовых параметров при компиляции (JVM limitation из Java 5, 2004). Формально: `∀T. List<T>` компилируется в `List` (raw type). Следствие: `is List<String>` невозможно в runtime.

Kotlin `reified` — **partial workaround** через inline functions: компилятор подставляет конкретный тип в call site, сохраняя типовую информацию. Ограничение: работает только в inline functions, т.к. требует доступа к конкретному типу на этапе компиляции.

> **Связь**: Subtyping → [[functional-programming]], Variance → [[kotlin-collections]], Bottom type → [[kotlin-coroutines]] (Nothing в suspend)

---

## TL;DR

Java стирает generic типы в runtime (type erasure) — `List<String>` и `List<Int>` становятся одинаковыми `List`. Kotlin решает это через `reified` типы в inline функциях: `inline fun <reified T> parse(): T` сохраняет тип T в runtime, позволяя проверки `is T` и получение `T::class.java`.

Variance определяет, когда `List<Dog>` можно использовать вместо `List<Animal>`. Ковариантность (`out T`) — коллекция-производитель, можно только читать: `List<Dog>` подходит для `List<out Animal>`. Контравариантность (`in T`) — коллекция-потребитель, можно только добавлять: `Comparator<Animal>` подходит для `Comparator<in Dog>`. В Kotlin это объявляется на уровне интерфейса (declaration-site variance), а не на месте использования как в Java wildcards.

Аналогия из жизни: представьте автомат по продаже напитков. **Covariance (out)** — это торговый автомат. Автомат с яблочным соком (Producer<AppleJuice>) подходит как автомат с напитками (Producer<Drink>): вы только берёте из него, и яблочный сок — это напиток. **Contravariance (in)** — это мусорное ведро. Ведро для любого мусора (Consumer<Trash>) подходит как ведро для пластика (Consumer<Plastic>): вы только кладёте в него, и если оно принимает любой мусор, оно примет и пластик. **Invariance** — это почтовый ящик с ключом определённого размера. Только этот ключ подходит, никакие «похожие» не подойдут — потому что вы и кладёте, и забираете.

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Generics** | Параметризация типов `<T>` | Коробка с этикеткой — может хранить что угодно, но этикетка говорит что |
| **Variance** | Правила подстановки типов | Кто кому подходит — донор крови группы O подходит всем |
| **Covariance (out)** | Можно подставить подтип | Поставщик фруктов — если поставляет яблоки, подходит как поставщик фруктов |
| **Contravariance (in)** | Можно подставить супертип | Мусорный бак — бак для всего мусора принимает и пластик |
| **Invariance** | Только точный тип | Ключ от квартиры — только этот ключ, никакие похожие |
| **Type erasure** | Стирание типов в runtime | Коробка без этикетки — в runtime не знаем что внутри |
| **reified** | Сохранение типа в runtime | Коробка с встроенной этикеткой — inline вставляет тип |
| **Star projection** | `*` — неизвестный тип | Коробка "Осторожно, неизвестно" — читаем, но не пишем |
| **Contract** | Подсказка компилятору о гарантиях | Контракт "если вернул true, значит не null" |
| **Smart cast** | Автоматическое приведение после проверки | Если проверил паспорт — дальше помнишь имя |
| **Upper bound** | Ограничение сверху `T : Number` | Клуб "Только для числовых типов" |

---

## Generics

### Основы generic типов

```kotlin
// Generic класс
class Box<T>(val value: T) {
    fun get(): T = value
}

val intBox = Box(42)          // Box<Int>
val strBox = Box("Hello")     // Box<String>

println(intBox.get())         // 42
println(strBox.get())         // "Hello"

// Generic функция
fun <T> singletonList(item: T): List<T> {
    return listOf(item)
}

val list1 = singletonList(42)      // List<Int>
val list2 = singletonList("text")  // List<String>

// Множественные type parameters
class Pair<A, B>(val first: A, val second: B)

val pair = Pair(1, "one")  // Pair<Int, String>

// Generic с ограничениями (type bounds)
fun <T : Comparable<T>> max(a: T, b: T): T {
    return if (a > b) a else b
}

val maxInt = max(10, 20)        // OK: Int : Comparable<Int>
val maxStr = max("a", "z")      // OK: String : Comparable<String>
// val maxList = max(listOf(), listOf())  // ❌ Ошибка: List не Comparable

// Множественные bounds через where
fun <T> process(item: T) where T : CharSequence, T : Comparable<T> {
    println(item.length)        // CharSequence
    println(item.compareTo(""))  // Comparable
}

process("hello")  // String реализует оба интерфейса
```

**Почему generics?**
- Type safety: ошибки на этапе компиляции
- Переиспользование: один код для разных типов
- Избегаем приведений типов: нет `as`, нет ClassCastException

### Generic type erasure

```kotlin
// В runtime generic типы стираются
fun <T> checkType(value: Any): Boolean {
    // return value is T  // ❌ Ошибка: Cannot check for erased type
    return false
}

// Type erasure означает:
val list1 = listOf<Int>(1, 2, 3)
val list2 = listOf<String>("a", "b", "c")

// В runtime оба - просто List
println(list1::class)  // class java.util.Arrays$ArrayList
println(list2::class)  // class java.util.Arrays$ArrayList

// Невозможно создать массив generic типа
// val array = Array<T>(10) { ... }  // ❌ Ошибка

// Обход через reified (см. ниже) или Array<Any?>
inline fun <reified T> createArray(size: Int): Array<T?> {
    return arrayOfNulls<T>(size)
}
```

**Почему type erasure?**
- Java совместимость: JVM не поддерживает generics нативно
- Performance: нет overhead на runtime type checks
- Решение: reified types для inline функций

### Generic constraints в деталях

Upper bound ограничивает generic тип сверху. `T : Number` означает «T должен быть подтипом Number»:

```kotlin
class NumberBox<T : Number>(val value: T) {
    fun doubleValue(): Double = value.toDouble()
}

val intBox = NumberBox(42)      // OK: Int : Number
val doubleBox = NumberBox(3.14) // OK: Double : Number
// val strBox = NumberBox("42")    // ❌ Ошибка: String не Number
```

По умолчанию upper bound — `Any?` (T может быть nullable). Для non-null ограничения используйте `T : Any`:

```kotlin
class NonNullBox<T : Any>(val value: T)

val box = NonNullBox(42)     // OK
// val bad = NonNullBox(null)   // ❌ Ошибка
```

Множественные constraints задаются через `where`. Рекурсивные type bounds позволяют типу ссылаться на себя — классический паттерн для самотипизированных иерархий:

```kotlin
fun <T> process(item: T)
        where T : Comparable<T>,
              T : CharSequence {
    println(item.length)         // CharSequence
    println(item.compareTo(""))  // Comparable
}

interface Node<T : Node<T>> {   // Рекурсивный bound
    val children: List<T>
}
```

## Variance

### Declaration-site variance

```kotlin
// Invariant (по умолчанию) - нет variance
class InvariantBox<T>(var value: T)

val intBox: InvariantBox<Int> = InvariantBox(42)
// val anyBox: InvariantBox<Any> = intBox  // ❌ Ошибка!
// val numBox: InvariantBox<Number> = intBox  // ❌ Ошибка!

// Covariant (out) - только производит T, не потребляет
interface Producer<out T> {
    fun produce(): T
    // fun consume(value: T)  // ❌ Ошибка: T в in-позиции
}

class StringProducer : Producer<String> {
    override fun produce(): String = "Hello"
}

val strProducer: Producer<String> = StringProducer()
val anyProducer: Producer<Any> = strProducer  // ✅ OK: Producer<String> <: Producer<Any>

// Contravariant (in) - только потребляет T, не производит
interface Consumer<in T> {
    fun consume(value: T)
    // fun produce(): T  // ❌ Ошибка: T в out-позиции
}

class AnyConsumer : Consumer<Any> {
    override fun consume(value: Any) {
        println(value)
    }
}

val anyConsumer: Consumer<Any> = AnyConsumer()
val strConsumer: Consumer<String> = anyConsumer  // ✅ OK: Consumer<Any> <: Consumer<String>
```

**Почему variance нужен?**
- **Covariance (out)**: читать из generic контейнера безопасно
  - `List<String>` можно использовать как `List<Any>`
  - Можем только производить T, не можем добавлять
- **Contravariance (in)**: писать в generic контейнер безопасно
  - `Consumer<Any>` может потреблять любые String
  - Можем только потреблять T, не можем читать

### Практические примеры variance

```kotlin
// List<out T> - covariant, read-only
interface List<out T> {
    fun get(index: Int): T
    val size: Int
    // Нельзя добавлять: fun add(element: T)
}

val strings: List<String> = listOf("a", "b")
val anys: List<Any> = strings  // ✅ OK: только читаем

// MutableList<T> - invariant, можно читать и писать
interface MutableList<T> {
    fun get(index: Int): T
    fun add(element: T)
}

val mutableStrings: MutableList<String> = mutableListOf("a")
// val mutableAnys: MutableList<Any> = mutableStrings  // ❌ Ошибка!
// Если бы было OK:
// mutableAnys.add(42)  // Добавили Int в MutableList<String>!

// Comparator<in T> - contravariant
interface Comparator<in T> {
    fun compare(a: T, b: T): Int
}

val anyComparator: Comparator<Any> = Comparator { a, b ->
    a.hashCode() - b.hashCode()
}

val stringComparator: Comparator<String> = anyComparator  // ✅ OK
// anyComparator может сравнивать Any → может сравнивать String

// Function types variance
// (in) -> out
val stringToInt: (String) -> Int = { it.length }
val anyToInt: (Any) -> Int = stringToInt  // ✅ OK: String более специфичен
val stringToAny: (String) -> Any = stringToInt  // ✅ OK: Int более специфичен

// Правило PECS (Producer Extends, Consumer Super)
// Producer<out T> - производит T (extends в Java)
// Consumer<in T> - потребляет T (super в Java)
```

### Use-site variance (Type projections)

```kotlin
// Use-site variance - указываем variance при использовании
class Box<T>(var value: T)

fun copy(from: Box<out Any>, to: Box<in Any>) {
    to.value = from.value  // Читаем из 'out', пишем в 'in'
}

val intBox = Box(42)
val anyBox = Box<Any>("initial")

copy(intBox, anyBox)  // ✅ OK
println(anyBox.value)  // 42

// 'out' projection - можем только читать
fun readFrom(box: Box<out Number>) {
    val value: Number = box.value  // ✅ Читаем
    // box.value = 42  // ❌ Ошибка: нельзя писать
}

readFrom(Box<Int>(42))     // ✅ OK
readFrom(Box<Double>(3.14)) // ✅ OK

// 'in' projection - можем только писать
fun writeTo(box: Box<in Int>) {
    box.value = 42  // ✅ Пишем
    // val value: Int = box.value  // ❌ Ошибка: нельзя читать (может быть Any)
}

writeTo(Box<Int>(0))    // ✅ OK
writeTo(Box<Number>(0)) // ✅ OK
writeTo(Box<Any>(0))    // ✅ OK

// Star projection - unknown type
fun printBox(box: Box<*>) {
    println(box.value)  // Читаем как Any?
    // box.value = "anything"  // ❌ Ошибка: неизвестный тип
}

printBox(Box(42))
printBox(Box("hello"))
```

**Когда использовать какой projection:**
- `out T`: функция только читает из T
- `in T`: функция только пишет в T
- `*`: неизвестный тип, ограниченный доступ

### Когда НЕ использовать variance

```kotlin
// ❌ Не используйте variance для mutable данных
class MutableHolder<out T>(var value: T)  // Ошибка компиляции!
// Почему: если бы сработало, можно было бы записать неправильный тип

// ❌ Не используйте covariance, если нужно передавать T в методы
interface Repository<out T> {
    fun save(item: T)  // Ошибка: T в in-позиции
}
// Почему: covariance позволяет Repository<Dog> → Repository<Animal>
// Тогда save(animal) получит Animal, но Repository<Dog> ожидает Dog!

// ❌ Не используйте variance просто "на всякий случай"
class SimpleBox<T>(val value: T)  // OK: invariant
// Если не нужна подстановка типов, invariant проще и безопаснее

// ✅ Правильный выбор variance:

// 1. Только читаете? → out (covariant)
interface Reader<out T> {
    fun read(): T
}

// 2. Только пишете? → in (contravariant)
interface Writer<in T> {
    fun write(value: T)
}

// 3. И то, и другое? → invariant (default)
interface Storage<T> {
    fun read(): T
    fun write(value: T)
}
```

**Практические советы по variance:**

```
┌─────────────────────────────────────────────────────────────────┐
│                  DECISION TREE ДЛЯ VARIANCE                     │
└─────────────────────────────────────────────────────────────────┘

Используется ли T как возвращаемое значение (out-позиция)?
├── ДА → Используется ли T как параметр метода (in-позиция)?
│        ├── ДА → Invariant (по умолчанию)
│        │        Пример: MutableList<T>
│        │
│        └── НЕТ → Covariant (out T)
│                  Пример: List<out T>, Iterable<out T>
│
└── НЕТ → Используется ли T как параметр метода (in-позиция)?
          ├── ДА → Contravariant (in T)
          │        Пример: Comparator<in T>, Consumer<in T>
          │
          └── НЕТ → Зачем вам generic? 🤔
```

### Star projections в деталях

```kotlin
// Star projection эквиваленты
// Foo<*> эквивалентно:
// - Foo<out Any?> для Producer
// - Foo<in Nothing> для Consumer

interface Producer<out T> {
    fun produce(): T
}

fun useProducer(producer: Producer<*>) {
    val value: Any? = producer.produce()  // Producer<*> = Producer<out Any?>
}

interface Consumer<in T> {
    fun consume(value: T)
}

fun useConsumer(consumer: Consumer<*>) {
    // consumer.consume("value")  // ❌ Ошибка: Consumer<*> = Consumer<in Nothing>
    // Нельзя передать ничего (Nothing не имеет значений)
}

// Практический пример
class Container<T>(val items: List<T>) {
    fun getItem(index: Int): T = items[index]
}

fun printContainer(container: Container<*>) {
    // Не знаем точный тип, но можем читать как Any?
    for (i in 0 until container.items.size) {
        println(container.getItem(i))  // Any?
    }
}

printContainer(Container(listOf(1, 2, 3)))
printContainer(Container(listOf("a", "b", "c")))
```

## Reified Types

### Основы reified

```kotlin
// Обычные generic - type erasure
fun <T> isInstanceOf(value: Any): Boolean {
    // return value is T  // ❌ Ошибка: Cannot check for erased type
    return false
}

// inline + reified - тип сохраняется
inline fun <reified T> isInstanceOfReified(value: Any): Boolean {
    return value is T  // ✅ OK: T известен благодаря inline
}

println(isInstanceOfReified<String>("hello"))  // true
println(isInstanceOfReified<Int>("hello"))     // false

// Доступ к T::class
inline fun <reified T> getClassName(): String {
    return T::class.simpleName ?: "Unknown"
}

println(getClassName<String>())  // "String"
println(getClassName<List<Int>>())  // "List"
```

**Почему только для inline?** Обычная generic-функция компилируется один раз — в ней T стёрт (type erasure). Но inline-функция не существует как отдельный метод в bytecode: её тело копируется в каждое место вызова. В месте вызова конкретный тип T известен компилятору, поэтому он подставляет реальный тип вместо T. Если вы написали `isInstanceOfReified<String>(value)`, компилятор вставит `value is String` — никакого generic, просто конкретная проверка.

**Механизм работы.** Когда компилятор встречает вызов inline-функции с reified-параметром, он выполняет три шага: (1) копирует тело функции в место вызова, (2) заменяет все `T` на конкретный тип, (3) заменяет `T::class` на `String::class` (или другой конкретный KClass). Результат — в bytecode нет никаких generics, только конкретный код. Это означает, что каждый вызов с разным типом генерирует свою копию кода, что увеличивает размер bytecode, но даёт возможности, недоступные обычным generics.

**Ограничения подхода.** Reified работает только для inline-функций — это принципиальное ограничение, не техническое решение. Обычные функции нельзя сделать reified, потому что они компилируются один раз и вызываются через vtable. Также reified не решает проблему полностью: вложенные generic-типы (`List<String>`) теряют внутренний тип — `T::class` для `List<String>` вернёт `List`, а не `List<String>`. Для работы с параметризованными типами в runtime нужен TypeToken-паттерн (используется в Gson, Jackson).

### Практические примеры reified

Самый частый паттерн — фильтрация по типу. Стандартная библиотека Kotlin использует reified именно для этого:

```kotlin
inline fun <reified T> List<*>.filterIsInstance(): List<T> {
    val result = mutableListOf<T>()
    for (element in this) {
        if (element is T) result.add(element)
    }
    return result
}

val mixed: List<Any> = listOf(1, "two", 3.0, "four", 5)
val strings = mixed.filterIsInstance<String>()  // ["two", "four"]
```

Другой распространённый паттерн — JSON-парсинг, где reified избавляет от явной передачи `Class<T>`:

```kotlin
inline fun <reified T> String.fromJson(): T {
    return Gson().fromJson(this, T::class.java)
}

val user: User = jsonString.fromJson()  // Тип выводится!
```

Reified также полезен для dependency injection — ServiceLocator может выдавать сервисы по типу без явного указания класса:

```kotlin
class ServiceLocator {
    private val services = mutableMapOf<Class<*>, Any>()

    inline fun <reified T : Any> get(): T {
        @Suppress("UNCHECKED_CAST")
        return services[T::class.java] as? T
            ?: throw IllegalStateException("Not found: ${T::class.simpleName}")
    }
}

val service = locator.get<MyService>()  // Без Class<T>!
```

### Ограничения reified

```kotlin
// ✅ Можно:
inline fun <reified T> example1() {
    val clazz = T::class            // Получить KClass
    val instance = T::class.java    // Получить Java Class
    val check = value is T          // Type check
    val array = arrayOf<T>()        // Создать массив
}

// ❌ Нельзя:
inline fun <reified T> example2() {
    // val instance = T()  // ❌ Нельзя создать экземпляр
    // T.staticMethod()    // ❌ Нельзя вызвать static методы
}

// Обход для создания экземпляра
inline fun <reified T : Any> createInstance(): T {
    return T::class.java.getDeclaredConstructor().newInstance()
}

// Работает только если у T есть конструктор без параметров
val instance = createInstance<MyClass>()
```

## Type Projections и Wildcards

### Сравнение с Java wildcards

```kotlin
// Java: List<? extends Number>
// Kotlin: List<out Number>
fun sumOfList(numbers: List<out Number>): Double {
    return numbers.sumOf { it.toDouble() }
}

sumOfList(listOf(1, 2, 3))           // List<Int>
sumOfList(listOf(1.5, 2.5, 3.5))     // List<Double>

// Java: List<? super Integer>
// Kotlin: List<in Int>
fun addNumbers(list: MutableList<in Int>) {
    list.add(42)
}

val intList = mutableListOf<Int>()
val numberList = mutableListOf<Number>()
val anyList = mutableListOf<Any>()

addNumbers(intList)     // OK
addNumbers(numberList)  // OK
addNumbers(anyList)     // OK

// Java: List<?>
// Kotlin: List<*>
fun printList(list: List<*>) {
    for (item in list) {
        println(item)  // item: Any?
    }
}

printList(listOf(1, 2, 3))
printList(listOf("a", "b", "c"))
```

### Проецирование функциональных типов

```kotlin
// Function types тоже имеют variance
// (in) -> out

// Covariant return type
val intProducer: () -> Int = { 42 }
val numberProducer: () -> Number = intProducer  // ✅ OK: Int <: Number

// Contravariant parameter type
val numberConsumer: (Number) -> Unit = { println(it) }
val intConsumer: (Int) -> Unit = numberConsumer  // ✅ OK: Number :> Int

// Комбинация
val stringToInt: (String) -> Int = { it.length }
val anyToNumber: (Any) -> Number = stringToInt  // ✅ OK
// String <: Any (contravariant parameter)
// Int <: Number (covariant return)
```

## Contracts

### Основы contracts

```kotlin
import kotlin.contracts.*

// Contract информирует компилятор о гарантиях функции
fun String?.isNotNullOrEmpty(): Boolean {
    contract {
        returns(true) implies (this@isNotNullOrEmpty != null)
    }
    return this != null && this.isNotEmpty()
}

fun example(str: String?) {
    if (str.isNotNullOrEmpty()) {
        // Компилятор знает что str != null благодаря contract
        println(str.length)  // ✅ OK, нет ошибки "str might be null"
    }
}

// Contract для require
inline fun requirePositive(value: Int) {
    contract {
        returns() implies (value > 0)
    }
    require(value > 0) { "Value must be positive" }
}

fun calculate(x: Int) {
    requirePositive(x)
    // Компилятор знает что x > 0
}
```

**Почему contracts нужны?**
- Smart casts: компилятор понимает когда можно smart cast
- Null safety: компилятор знает когда значение не null
- Лучший анализ кода: меньше false positives

### Типы contracts

```kotlin
// returns() implies - условие выполнено если функция вернулась
fun String?.isNullOrEmpty(): Boolean {
    contract {
        returns(false) implies (this@isNullOrEmpty != null)
    }
    return this == null || this.isEmpty()
}

// returns() - функция всегда возвращается (не кидает исключение)
inline fun <R> run(block: () -> R): R {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    return block()
}

// callsInPlace - гарантирует что lambda вызовется
inline fun <T> T.also(block: (T) -> Unit): T {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    block(this)
    return this
}

// InvocationKind варианты:
// - EXACTLY_ONCE: ровно 1 раз
// - AT_MOST_ONCE: 0 или 1 раз
// - AT_LEAST_ONCE: 1 или более раз
// - UNKNOWN: неизвестно

// Практический пример
inline fun <T> T.applyIf(condition: Boolean, block: T.() -> Unit): T {
    contract {
        callsInPlace(block, InvocationKind.AT_MOST_ONCE)
    }
    if (condition) {
        block()
    }
    return this
}

val result = StringBuilder()
    .applyIf(true) {
        append("Hello")  // Вызовется
    }
    .applyIf(false) {
        append("World")  // Не вызовется
    }
```

### Ограничения contracts

```kotlin
// ✅ Contracts работают только для:
// - Top-level функций
// - Member functions
// - Extension functions

// ❌ НЕ работают для:
// - Local functions
// - Functions в анонимных объектах
// - Functional types

// Contracts должны быть первым выражением в функции
fun example(value: String?) {
    contract {
        returns() implies (value != null)
    }
    // Весь остальной код...
}

// ❌ Ошибка: contract должен быть первым
fun wrong(value: String?) {
    println("Some code")
    contract { }  // ❌ Ошибка компиляции
}
```

### Практические примеры contracts в реальном коде

```kotlin
// Пример 1: Валидация входных данных
@OptIn(ExperimentalContracts::class)
inline fun validateUser(user: User?): User {
    contract {
        returns() implies (user != null)
    }
    requireNotNull(user) { "User cannot be null" }
    require(user.name.isNotBlank()) { "User name cannot be blank" }
    require(user.age >= 0) { "User age must be non-negative" }
    return user
}

fun processUser(user: User?) {
    val validUser = validateUser(user)
    // После validateUser компилятор знает: validUser != null
    println(validUser.name)  // ✅ OK, smart cast работает
}

// Пример 2: Проверка состояния
@OptIn(ExperimentalContracts::class)
fun MutableList<*>.isNotEmpty(): Boolean {
    contract {
        returns(true) implies (this@isNotEmpty.size > 0)
    }
    return this.size > 0
}

// Пример 3: Synchronized block с гарантией вызова
@OptIn(ExperimentalContracts::class)
inline fun <T> synchronized(lock: Any, block: () -> T): T {
    contract {
        callsInPlace(block, InvocationKind.EXACTLY_ONCE)
    }
    // Теперь переменные внутри block могут быть val,
    // потому что компилятор знает: block вызовется ровно 1 раз
    synchronized(lock) {
        return block()
    }
}

fun example() {
    val value: String  // val, не инициализирован
    synchronized(this) {
        value = "initialized"  // ✅ OK: block вызовется ровно 1 раз
    }
    println(value)  // ✅ OK: компилятор знает, value инициализирован
}

// Пример 4: Either-style обработка ошибок
sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Failure(val error: Throwable) : Result<Nothing>()
}

@OptIn(ExperimentalContracts::class)
fun <T> Result<T>.isSuccess(): Boolean {
    contract {
        returns(true) implies (this@isSuccess is Result.Success)
    }
    return this is Result.Success
}

fun handleResult(result: Result<String>) {
    if (result.isSuccess()) {
        // Компилятор знает: result is Result.Success
        println(result.value)  // ✅ Smart cast работает
    }
}
```

**Когда использовать contracts:**
- Кастомные проверки, похожие на `require`/`check`/`requireNotNull`
- Wrapper функции вокруг стандартных scope functions
- DSL-билдеры, где lambda вызывается определённое число раз
- Валидация, после которой тип должен измениться (smart cast)

**Когда НЕ использовать contracts:**
- Для простых функций, где компилятор сам выведет типы
- Когда contract делает код сложнее для понимания
- В public API библиотек (contracts — experimental feature)

## Распространённые ошибки

### 1. Invariance когда нужна variance

```kotlin
// ❌ Invariant generic когда нужно читать
class Producer<T>(private val values: List<T>) {
    fun produce(): T = values.random()
}

// val anyProducer: Producer<Any> = Producer<String>(listOf("a"))  // ❌ Ошибка!

// ✅ Используйте covariance
class Producer<out T>(private val values: List<T>) {
    fun produce(): T = values.random()
}

val anyProducer: Producer<Any> = Producer<String>(listOf("a"))  // ✅ OK
```

### 2. Type erasure без reified

```kotlin
// ❌ Попытка type check без reified
fun <T> checkType(value: Any): Boolean {
    // return value is T  // ❌ Ошибка компиляции
    return false
}

// ✅ Используйте reified для inline функций
inline fun <reified T> checkType(value: Any): Boolean {
    return value is T  // ✅ OK
}
```

### 3. Неправильная variance

```kotlin
// ❌ Covariance для mutable структур
class MutableBox<out T>(var value: T)  // ❌ Ошибка: var в covariant позиции

// ✅ Invariance для mutable
class MutableBox<T>(var value: T)  // ✅ OK

// ✅ Или covariance для immutable
class ImmutableBox<out T>(val value: T)  // ✅ OK
```

### 4. Star projection без понимания

```kotlin
// ❌ Попытка записи в star projection
fun addToList(list: MutableList<*>) {
    // list.add("element")  // ❌ Ошибка: неизвестный тип
}

// ✅ Используйте конкретный projection
fun addToList(list: MutableList<in String>) {
    list.add("element")  // ✅ OK
}
```

### 5. Reified без inline

```kotlin
// ❌ reified без inline
fun <reified T> wrong() {  // ❌ Ошибка: reified только для inline
    // ...
}

// ✅ reified с inline
inline fun <reified T> correct() {  // ✅ OK
    // ...
}
```

---

## Кто использует и реальные примеры

### Компании использующие Type System Features

| Компания | Фича | Применение |
|----------|------|------------|
| **JetBrains** | Contracts | IntelliJ IDEA smart casts, Kotlin stdlib |
| **Google** | Variance | Jetpack Collections, immutable `List<out T>` |
| **Square** | Reified | Moshi JSON parsing, Retrofit type-safe API |
| **Netflix** | Generics + Variance | Type-safe DTOs, API boundaries |
| **Uber** | Smart Casts | Sealed class hierarchies для UI State |
| **Pinterest** | Contracts | Custom validation functions |

### Production паттерны

**Sealed Class + Smart Cast (Uber, Google):**
```kotlin
sealed class UiState<out T> {
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
    object Loading : UiState<Nothing>()
}

// Smart cast после when
fun handle(state: UiState<User>) {
    when (state) {
        is UiState.Success -> showUser(state.data) // T smart-casted to User
        is UiState.Error -> showError(state.message)
        UiState.Loading -> showLoading()
    }
}
```

**Reified + JSON (Square Moshi):**
```kotlin
inline fun <reified T> Moshi.fromJson(json: String): T? {
    return adapter(T::class.java).fromJson(json)
}

val user: User? = moshi.fromJson(jsonString) // Type inferred
```

### Реальные кейсы

**Case 1: Kotlin Stdlib — Variance Design**
```
Пример: List<out T> vs MutableList<T>
Причина: List только читается → covariant безопасен
MutableList читается и пишется → invariant необходим
Результат: List<String> присваивается в List<Any>
```

**Case 2: Square Retrofit — Reified Types**
```
Проблема: Type erasure не позволяет узнать T в runtime
Решение: inline + reified для Call<T> парсинга
Результат: Type-safe API без ручного указания Class<T>
```

---

## Чеклист

- [ ] Используете generics для type-safe переиспользования
- [ ] Понимаете разницу между covariance (out) и contravariance (in)
- [ ] Применяете PECS (Producer Extends, Consumer Super)
- [ ] Используете reified для type checks в inline функциях
- [ ] Понимаете type erasure и его ограничения
- [ ] Знаете когда использовать star projections
- [ ] Применяете type constraints для ограничения generic типов
- [ ] Используете contracts для улучшения smart casts
- [ ] Понимаете разницу между declaration-site и use-site variance
- [ ] Избегаете covariance для mutable структур
## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "String? и Optional<String> одинаковы" | Nullable types — compile-time only, zero overhead. Optional — wrapper object с allocation. Nullable idiomatic в Kotlin |
| "Smart casts работают везде" | Smart casts не работают для var (может измениться), custom getters (могут возвращать разное), properties из других модулей |
| "Type erasure — только проблема" | Type erasure обеспечивает backward compatibility с Java. reified inline — workaround для типов в runtime |
| "out T значит 'только output'" | out T (covariance) значит: T появляется только в output позициях методов. Можно читать T, нельзя принимать T как параметр |
| "Star projection = Any?" | * projection — unknown type. Box<*> эквивалентен Box<out Any?> для чтения, Box<in Nothing> для записи. Строже чем Any |
| "Variance влияет на runtime" | Variance — compile-time only. В bytecode нет out/in. JVM видит обычные generics с erasure |
| "reified можно использовать везде" | reified требует inline функцию. Inline вставляет код в call site, где конкретный тип известен компилятору |
| "Nothing — бесполезный тип" | Nothing — bottom type. Для функций, которые никогда не возвращают (throw, infinite loop). Subtype всех типов |
| "Contracts меняют поведение кода" | Contracts информируют компилятор о гарантиях. Они не enforcement — просто подсказка для smart casts |
| "Unit = void" | Unit — singleton object, реальный тип с одним значением. void — отсутствие типа. Unit можно использовать в generics |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin Type System |
|--------------|--------------------------------|
| **Type Soundness** | Nullable types гарантируют отсутствие NPE в compile-time (для чистого Kotlin кода). Type safety through types |
| **Variance** | Covariance (out), Contravariance (in), Invariance. Правила подтипирования для generic types |
| **PECS Principle** | Producer Extends (out), Consumer Super (in). Мнемоника для выбора variance |
| **Type Erasure** | Generic types стираются в runtime для JVM compatibility. Reified — compile-time workaround |
| **Bottom Type** | Nothing — subtype всех типов. Используется для функций, которые не возвращают нормально |
| **Union/Intersection Types** | Нет в Kotlin напрямую, но sealed classes + when = discriminated union. Multiple bounds = intersection |
| **Smart Casts (Flow Typing)** | После type check компилятор знает более точный тип. Информация о типе "течёт" по control flow |
| **Declaration-site vs Use-site Variance** | Declaration-site (class Producer<out T>) vs Use-site (fun copy(from: Array<out Any>)). Kotlin предпочитает declaration-site |
| **Type Inference** | Компилятор выводит типы без явного указания. Hindley-Milner based algorithm |
| **Contracts (Dependent Types lite)** | Contracts связывают входы с выходами/effects. Простая форма dependent types для smart casts |

---

## Связь с другими темами

[[kotlin-collections]] — Коллекции Kotlin (List, Set, Map) являются главным практическим примером variance: List<out T> — ковариантен (read-only), MutableList<T> — инвариантен (read-write). Понимание variance необходимо для осознания, почему List<String> можно присвоить в List<Any>, а MutableList<String> нельзя. Рекомендуется изучать коллекции и variance параллельно.

[[kotlin-advanced-features]] — Продвинутые фичи Kotlin (inline functions, extension functions, delegates) тесно связаны с системой типов: reified типы работают только в inline-функциях, extension functions разрешаются статически по compile-time типу, а delegated properties используют generic-контракты. Этот материал расширяет понимание того, как type system влияет на продвинутые конструкции языка.

[[kotlin-functional]] — Функциональные типы Kotlin ((A) -> B) имеют встроенную variance: параметры контравариантны (in), возвращаемое значение ковариантно (out). Это позволяет подставлять (Any) -> Int вместо (String) -> Number. Понимание variance в function types критически важно для проектирования type-safe callback API и DSL.

[[kotlin-best-practices]] — Best practices для generics включают правила выбора variance (PECS principle), ограничения на использование star projections, рекомендации по reified типам и contracts. Знание type system помогает следовать этим практикам осознанно, а не механически. Рекомендуется как справочник после освоения теории.

## Источники и дальнейшее чтение

### Теоретические основы

- Liskov B., Wing J. (1994). *A Behavioral Notion of Subtyping.* ACM TOPLAS. — Формальное определение Liskov Substitution Principle, основа subtyping в Kotlin.
- Cardelli L., Wegner P. (1985). *On Understanding Types, Data Abstraction, and Polymorphism.* Computing Surveys. — Формальное определение covariance/contravariance, теоретическая основа Kotlin `in`/`out`.
- Pierce B.C. (2002). *Types and Programming Languages.* MIT Press. — Каноническое введение в теорию типов: subtyping, polymorphism, type inference. Формальный фундамент для понимания любой системы типов.

### Практические руководства

- Jemerov D., Isakova S. (2017). *Kotlin in Action*. — Главы о generics и variance с подробным объяснением declaration-site vs use-site variance, сравнением с Java wildcards, и практическими примерами PECS.
- Moskala M. (2021). *Effective Kotlin*. — Best practices для работы с generic-типами, включая правила выбора variance, ограничения reified типов и рекомендации по contracts.
- Skeen J. (2019). *Kotlin Programming: The Big Nerd Ranch Guide*. — Доступное введение в систему типов Kotlin с пошаговыми примерами generics, variance и type projections.

---

## Дополнительные ресурсы

- [Generics: in, out, where](https://kotlinlang.org/docs/generics.html) — официальная документация Kotlin по generics и variance
- [Type System Specification](https://kotlinlang.org/spec/type-system.html) — формальная спецификация системы типов Kotlin

---

## Проверь себя

> [!question]- Почему List<Dog> можно присвоить List<Animal> (covariance), но MutableList<Dog> нельзя присвоить MutableList<Animal>?
> List<out T> объявлен как covariant — T используется только в out-позиции (возвращается из методов). Из List<Dog> можно читать Dog, который является Animal — это безопасно. MutableList<T> не является ни in, ни out (invariant), потому что T используется и в in-позиции (add(T)) и в out-позиции (get()). Если бы MutableList<Dog> можно было присвоить MutableList<Animal>, то через MutableList<Animal> можно было бы добавить Cat, что нарушило бы типобезопасность: MutableList<Dog> содержал бы Cat.

> [!question]- Сценарий: вам нужна функция, которая проверяет является ли объект экземпляром определённого типа. Почему нельзя написать fun <T> isType(obj: Any) = obj is T, и как это решить?
> Из-за type erasure generics стираются в runtime: компилятор не знает что такое T в runtime, поэтому obj is T невозможен. Решение: inline fun <reified T> isType(obj: Any) = obj is T. inline копирует тело функции в место вызова, reified сохраняет информацию о типе T в runtime. Это работает, потому что в каждом месте вызова T заменяется конкретным типом: isType<String>(obj) превращается в obj is String.

> [!question]- Почему в Kotlin Nothing является подтипом всех типов и как это используется на практике?
> Nothing — тип без экземпляров, означает "функция никогда не возвращает значение" (бросает исключение или бесконечный цикл). Как подтип всех типов позволяет: (1) throw Exception быть выражением любого типа: val x: Int = throw Error(); (2) emptyList() возвращать List<Nothing>, совместимый с любым List<T>; (3) Elvis operator с throw: val name = user?.name ?: throw NullPointerException(). Nothing? имеет единственное значение — null, поэтому null совместим с любым nullable типом.

---

## Ключевые карточки

Что означает out T (covariance) и in T (contravariance)?
?
out T (covariance): T используется только в output-позиции (return). List<out Animal> — можно подставить List<Dog>. Producer. in T (contravariance): T используется только в input-позиции (параметры). Comparator<in Animal> — можно подставить Comparator<Any>. Consumer. Мнемоника: PECS — Producer Extends, Consumer Super.

Что такое star projection (*) в Kotlin?
?
Star projection (*) означает "неизвестный тип". List<*> — список чего-то, но не знаю чего. Чтение: элементы как Any?. Запись: нельзя добавить ничего (кроме null). Аналог Java wildcard List<?>. Используется когда тип неважен: fun printSize(list: List<*>) = list.size.

Что такое type erasure и как reified его обходит?
?
Type erasure: generic типы стираются в bytecode. List<String> и List<Int> — одинаковый List в runtime. Нельзя проверить is List<String>. reified (только в inline функциях) сохраняет тип в runtime: inline fun <reified T> check(obj: Any) = obj is T. Работает потому что inline подставляет конкретный тип в каждом месте вызова.

Что такое Kotlin Contracts и зачем они нужны?
?
Contracts информируют компилятор о гарантиях функции для улучшения smart casts: contract { returns(true) implies (value is String) } позволяет smart cast после проверки. Пример: после require(x != null) компилятор знает что x non-null. Experimental API (@OptIn(ExperimentalContracts::class)). Используются в stdlib: require, check, isNullOrEmpty.

Как declaration-site variance отличается от use-site variance?
?
Declaration-site: out/in на уровне класса — interface List<out T>. Определяется один раз для всех использований. Use-site: out/in на уровне параметра — fun copy(from: Array<out Any>). Kotlin поддерживает оба. Java поддерживает только use-site (? extends T, ? super T). Declaration-site проще и безопаснее для API design.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубление | [[kotlin-advanced-features]] | Extensions, delegates, DSL — продвинутые фичи, использующие систему типов |
| Углубление | [[kotlin-collections]] | Variance на практике: List<out T> vs MutableList<T> в коллекциях |
| Связь | [[kotlin-functional]] | inline + reified — связь ФП и системы типов |
| Кросс-область | [[variance-covariance]] | Теоретические основы вариантности в CS: ковариантность и контравариантность |
| Навигация | [[jvm-overview]] | Вернуться к обзору JVM-тем |

---

*Проверено: 2026-01-09 | Источники: Kotlin Docs, Kotlin Spec, DroidCon, carrion.dev — Педагогический контент проверен*
