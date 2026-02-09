---
title: "Generics: параметрический полиморфизм"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, type-systems, generics, polymorphism, kotlin]
related:
  - "[[type-systems-fundamentals]]"
  - "[[variance-covariance]]"
  - "[[type-erasure-reification]]"
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

## Источники

- [Kotlin Docs: Generics](https://kotlinlang.org/docs/generics.html) — official reference
- [Wikipedia: System F](https://en.wikipedia.org/wiki/System_F) — теоретические основы
- [TypeAlias: Kotlin Generics](https://typealias.com/start/kotlin-generics/) — visual guide
- [Baeldung: Kotlin Generics](https://www.baeldung.com/kotlin/generics) — practical examples

---

*Проверено: 2026-01-09*
