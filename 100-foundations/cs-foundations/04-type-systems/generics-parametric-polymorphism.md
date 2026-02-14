---
title: "Generics: параметрический полиморфизм"
created: 2026-01-04
modified: 2026-02-13
type: deep-dive
reading_time: 15
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/intermediate
related:
  - "[[type-systems-fundamentals]]"
  - "[[variance-covariance]]"
  - "[[type-erasure-reification]]"
prerequisites:
  - "[[type-systems-fundamentals]]"
---

# Generics: параметрический полиморфизм

> **TL;DR:** Generics позволяют писать код, абстрагированный от конкретного типа. `List<T>` работает с любым T. История: System F (1972) → ML → Java 5 → Kotlin. Kotlin: `out` (covariant), `in` (contravariant), `where` (multiple bounds), `reified` (обход type erasure). PECS: Producer-Extends, Consumer-Super.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Type Systems** | Основы типизации | [[type-systems-fundamentals]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Generic** | Тип с параметром типа | Коробка для любого товара |
| **Type Parameter** | Placeholder для конкретного типа | Слот "сюда положить Х" |
| **Upper Bound** | Ограничение "тип должен быть подтипом..." | "Только продукты питания" |
| **Reification** | Сохранение информации о типе в runtime | Этикетка на коробке |

---

## ПОЧЕМУ нужны generics

### Проблема: дублирование кода

Без generics пришлось бы писать отдельный класс для каждого типа:

```java
// Без generics — копипаста
class IntList {
    void add(int item) { ... }
    int get(int index) { ... }
}

class StringList {
    void add(String item) { ... }
    String get(int index) { ... }
}

class UserList {
    void add(User item) { ... }
    User get(int index) { ... }
}

// И так для каждого типа...
```

### Проблема: потеря type safety

Альтернатива — использовать `Object`:

```java
// Используем Object — теряем type safety
class ObjectList {
    void add(Object item) { ... }
    Object get(int index) { ... }
}

ObjectList list = new ObjectList();
list.add("hello");
list.add(42);  // Можно положить что угодно!

String s = (String) list.get(1);  // ClassCastException!
```

### Решение: generics

```kotlin
// Один generic класс для всех типов
class List<T> {
    fun add(item: T) { ... }
    fun get(index: Int): T { ... }
}

val strings: List<String> = List()
strings.add("hello")
strings.add(42)  // Compile error! Type mismatch

val s: String = strings.get(0)  // Без cast, type safe
```

---

## История: от System F до Kotlin

### 1972-1974: System F

Математики **Jean-Yves Girard** (1972) и **John Reynolds** (1974) независимо открыли **System F** — типизированное лямбда-исчисление с универсальной квантификацией по типам.

**System F формализует:**
- Функции, параметризованные типами
- Полиморфные типы
- Основа для functional languages

### 1973: ML

**Robin Milner** создал ML с автоматическим выводом типов (Hindley-Milner) и parametric polymorphism.

### 1990: Haskell

Haskell расширил System F с type classes, higher-kinded types и другими продвинутыми фичами.

### 2004: Java 5

Java добавила generics через **type erasure** — информация о типах стирается при компиляции. Это сохранило backward compatibility с pre-generics кодом.

### 2011: Kotlin

Kotlin улучшил generics:
- Declaration-site variance (`out`, `in`)
- Reified type parameters
- Упрощённый синтаксис

---

## КАК работают Generics

### Базовый синтаксис

**Generic class:**

```kotlin
class Box<T>(val value: T)

val stringBox = Box("hello")  // Box<String>
val intBox = Box(42)          // Box<Int>
```

**Generic function:**

```kotlin
fun <T> identity(item: T): T = item

val s = identity("hello")  // String
val n = identity(42)       // Int
```

### Type Parameter vs Type Argument

```
┌─────────────────────────────────────────────────────────────┐
│            TYPE PARAMETER vs TYPE ARGUMENT                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   class Box<T>       ← T — type PARAMETER (placeholder)    │
│                                                             │
│   val box: Box<String>  ← String — type ARGUMENT (concrete)│
│                                                             │
│   Аналогия:                                                │
│   fun greet(name: String)   ← name — parameter             │
│   greet("Alice")            ← "Alice" — argument           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Upper Bounds: ограничение типа

По умолчанию `T` может быть **любым** типом, включая `Any?`.

```kotlin
// T может быть чем угодно
fun <T> process(item: T) { ... }

// T должен быть Comparable
fun <T : Comparable<T>> sort(list: List<T>) {
    // Можем вызывать методы Comparable
    if (list[0] < list[1]) { ... }
}

sort(listOf(3, 1, 2))       // OK: Int is Comparable
sort(listOf(Object()))      // Error: Object is not Comparable
```

### Multiple Bounds: where clause

Когда нужно несколько ограничений:

```kotlin
fun <T> copyWhenGreater(list: List<T>, threshold: T): List<String>
    where T : CharSequence,
          T : Comparable<T> {
    return list.filter { it > threshold }.map { it.toString() }
}

// T должен быть И CharSequence, И Comparable
copyWhenGreater(listOf("abc", "xyz"), "def")  // OK
```

---

## Три вида полиморфизма

```
┌─────────────────────────────────────────────────────────────┐
│               ТРИ ВИДА ПОЛИМОРФИЗМА                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. SUBTYPE (Inclusion)                                    │
│      ────────────────────                                   │
│      Наследование: Dog is-a Animal                          │
│      fun pet(animal: Animal) { }                            │
│      pet(Dog())  // OK: Dog subtype of Animal              │
│                                                             │
│   2. AD-HOC (Overloading)                                   │
│      ────────────────────                                   │
│      Перегрузка методов с разными типами                   │
│      fun add(a: Int, b: Int): Int                          │
│      fun add(a: String, b: String): String                 │
│                                                             │
│   3. PARAMETRIC (Generics)                                  │
│      ────────────────────                                   │
│      Один код для любого типа                              │
│      fun <T> identity(item: T): T = item                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Variance: preview

> Подробно в [[variance-covariance]]

### Проблема invariance

```kotlin
open class Animal
class Dog : Animal()

val dogs: List<Dog> = listOf(Dog())
val animals: List<Animal> = dogs  // Работает?
```

Зависит от variance:
- **Invariant:** `MutableList<Dog>` НЕ является `MutableList<Animal>`
- **Covariant:** `List<Dog>` IS-A `List<Animal>` (read-only)

### Kotlin variance keywords

| Keyword | Название | Что можно | Пример |
|---------|----------|-----------|--------|
| `out T` | Covariant | Только читать T | `interface Producer<out T>` |
| `in T` | Contravariant | Только писать T | `interface Consumer<in T>` |
| — | Invariant | Читать и писать | `class MutableList<T>` |

---

## Reified: обход Type Erasure

> Подробно в [[type-erasure-reification]]

### Проблема

JVM стирает информацию о типах при компиляции:

```kotlin
fun <T> isInstance(item: Any): Boolean {
    return item is T  // Error: Cannot check for instance of erased type
}
```

### Решение: inline + reified

```kotlin
inline fun <reified T> isInstance(item: Any): Boolean {
    return item is T  // Работает!
}

isInstance<String>("hello")  // true
isInstance<Int>("hello")     // false
```

**Как работает:**
1. `inline` вставляет тело функции в место вызова
2. `reified` сохраняет информацию о типе
3. Компилятор подставляет конкретный тип

---

## Практические паттерны

### Generic Repository

```kotlin
interface Repository<T, ID> {
    fun findById(id: ID): T?
    fun save(entity: T): T
    fun delete(entity: T)
}

class UserRepository : Repository<User, Long> {
    override fun findById(id: Long): User? { ... }
    override fun save(entity: User): User { ... }
    override fun delete(entity: User) { ... }
}
```

### Generic Result/Either

```kotlin
sealed class Result<out T> {
    data class Success<T>(val value: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
}

fun <T> runCatching(block: () -> T): Result<T> =
    try {
        Result.Success(block())
    } catch (e: Throwable) {
        Result.Error(e)
    }
```

### Generic Factory

```kotlin
inline fun <reified T : ViewModel> Fragment.viewModel(): T {
    return ViewModelProvider(this)[T::class.java]
}

// Использование
val viewModel = viewModel<MyViewModel>()
```

---

## Подводные камни

### Null Safety с Generics

```kotlin
// T может быть nullable по умолчанию!
class Box<T>(val value: T)

val box: Box<String?> = Box(null)  // OK

// Если нужен non-null:
class SafeBox<T : Any>(val value: T)

val box: SafeBox<String?> = ...  // Error!
```

### Star Projection

```kotlin
// Когда тип неизвестен
val list: List<*> = listOf("a", 1, true)

// Можно читать как Any?
val first: Any? = list.first()

// Нельзя писать (кроме null)
// list.add(???)  — непонятно что можно добавить
```

### Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Raw types | Runtime exceptions | Всегда указывай type parameters |
| Игнорировать erasure | ClassCastException | Reified или type tokens |
| `T` без bound для non-null | Unexpected nulls | `T : Any` |
| Unchecked cast | Runtime crash | Safe cast `as?`, проверки |

---

## Куда дальше

**Если здесь впервые:**
→ Попрактикуйся создавать generic функции и классы

**Если понял и хочешь глубже:**
→ [[variance-covariance]] — ковариантность и контравариантность
→ [[type-erasure-reification]] — как обойти ограничения JVM

**Практическое применение:**
→ KMP: generics в expect/actual declarations

---

## Связь с другими темами

### [[type-systems-fundamentals]]
Generics — это расширение системы типов, называемое параметрическим полиморфизмом. Без понимания базовых концепций (subtyping, type inference, static vs dynamic typing) невозможно осознать, зачем нужны type parameters и как компилятор выводит конкретные типы. Знание Hindley-Milner алгоритма из теории типов объясняет, как Kotlin автоматически определяет T в `identity("hello")`.

### [[variance-covariance]]
Variance — это прямое следствие взаимодействия generics с subtyping. Когда `Dog` IS-A `Animal`, вопрос "является ли `List<Dog>` подтипом `List<Animal>`" — это вопрос variance. Понимание generics необходимо для изучения variance, а variance в свою очередь объясняет ограничения на позиции типов (`out` — только возврат, `in` — только параметр) и принцип PECS.

### [[type-erasure-reification]]
Type erasure — главное ограничение generics на JVM. Понимание того, как компилятор стирает информацию о типах для backward compatibility с Java 1.4, объясняет, почему `is T` невозможен и зачем Kotlin ввёл `reified`. Эта связь критична для KMP: на JVM работает erasure, на Native — типы сохраняются, что влияет на дизайн common-кода.

---

## Источники и дальнейшее чтение

- Pierce B. (2002). *Types and Programming Languages (TAPL)*. — фундаментальная работа по теории типов, включая System F и параметрический полиморфизм, которые лежат в основе generics
- Cardelli L., Wegner P. (1985). *On Understanding Types, Data Abstraction, and Polymorphism*. — классическая paper, систематизирующая виды полиморфизма (parametric, ad-hoc, subtype) и их взаимодействие
- Bloch J. (2018). *Effective Java*, 3rd ed. — главы 26-33 посвящены практике работы с generics, включая PECS, bounded wildcards и type tokens
- [Kotlin Docs: Generics](https://kotlinlang.org/docs/generics.html) — official reference
- [TypeAlias: Kotlin Generics](https://typealias.com/start/kotlin-generics/) — visual guide

---

## Проверь себя

> [!question]- Ты пишешь generic-функцию в KMP commonMain. Почему нельзя сделать `if (value is T)` без inline reified и как это обойти?
> На JVM generics подвергаются type erasure: в runtime T стирается до Any (или верхней границы). Компилятор не знает конкретный тип T, поэтому `is T` проверка невозможна. Решение: объявить функцию как `inline fun <reified T>` — тогда тело функции встраивается в call site, где конкретный тип известен. На Native type erasure нет, но для кросс-платформенного кода reified необходим. Альтернатива: передать KClass<T> параметром.

> [!question]- Почему generic-класс Box<T> не может создать new T() внутри себя, и как это решается?
> Из-за type erasure на JVM: в runtime T стёрт, JVM не знает, какой конструктор вызвать. Даже без erasure — T может быть интерфейсом или абстрактным классом без конструктора. Решения: (1) inline reified + T::class.java для создания через reflection. (2) Factory pattern: передать () -> T как параметр. (3) Abstract factory: создание делегируется вызывающему коду. Вариант 2 самый идиоматичный в Kotlin.

> [!question]- Чем upper bound constraint `<T : Comparable<T>>` отличается от `<T : Any>` и зачем он нужен?
> `<T : Any>` — T может быть любым non-null типом. `<T : Comparable<T>>` — T должен реализовать Comparable, то есть поддерживать сравнение. Это позволяет внутри функции вызывать compareTo() на объектах типа T. Без constraint компилятор не знает, что T умеет сравниваться, и запретит operации <, >, sorted(). Upper bound сужает множество допустимых типов, расширяя доступные операции.

---

## Ключевые карточки

Что такое параметрический полиморфизм (generics)?
?
Возможность написать код, параметризованный типом: List<T> работает с любым T, сохраняя type safety. Один код для разных типов, без потери проверки типов compile-time. Альтернатива — использование Any с runtime кастами (небезопасно) или дублирование кода для каждого типа.

---

Что такое type erasure для generics на JVM?
?
При компиляции JVM стирает информацию о generic-типах: List<Int> и List<String> становятся просто List. В runtime нельзя узнать параметр типа. Причина: обратная совместимость с pre-generics Java (до 1.5). Последствия: нельзя делать `is List<Int>`, нельзя создавать `new T()`, нельзя получить T.class без reified.

---

Как работает inline reified в Kotlin?
?
`inline fun <reified T>` — компилятор встраивает тело функции в каждый call site, подставляя конкретный тип вместо T. В результате в байткоде нет generic-параметра — он заменён конкретным типом. Это позволяет: `is T` проверки, T::class доступ, создание массивов Array<T>. Работает только с inline-функциями.

---

Что такое upper bound (верхняя граница) generic типа?
?
`<T : UpperBound>` — ограничение: T должен быть подтипом UpperBound. Примеры: `<T : Comparable<T>>` — T умеет сравниваться, `<T : Serializable>` — T сериализуем. Множественные bounds: `<T> where T : Comparable<T>, T : Serializable`. В Kotlin по умолчанию upper bound = Any?.

---

Чем generics отличаются от Any/Object?
?
Any/Object теряет информацию о типе: fun process(x: Any) принимает всё, но внутри нужен unsafe cast. Generics сохраняют тип: fun <T> process(x: T): T — компилятор гарантирует корректность без castов. Generics — compile-time safety, Any — runtime flexibility (и runtime crashes).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[variance-covariance]] | Понять ковариантность (out) и контравариантность (in) в Kotlin |
| Углубиться | [[type-erasure-reification]] | Как type erasure влияет на runtime и как reified это обходит |
| Смежная тема | [[type-systems-fundamentals]] | Вернуться к основам систем типов |
| Обзор | [[cs-foundations-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-02-13*
