---
title: "Variance: ковариантность и контравариантность"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/advanced
related:
  - "[[generics-parametric-polymorphism]]"
  - "[[type-erasure-reification]]"
prerequisites:
  - "[[type-systems-fundamentals]]"
  - "[[generics-parametric-polymorphism]]"
---

# Variance: ковариантность и контравариантность

> **TL;DR:** Variance определяет, как наследование типов влияет на generic типы. Covariance (`out`): `List<Dog>` IS-A `List<Animal>` — только чтение. Contravariance (`in`): `Comparator<Animal>` IS-A `Comparator<Dog>` — только запись. PECS: Producer-Extends, Consumer-Super. Kotlin использует declaration-site variance, Java — use-site wildcards.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Generics** | Основы параметризованных типов | [[generics-parametric-polymorphism]] |
| **Type Systems** | Понимание типизации | [[type-systems-fundamentals]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Variance** | Как наследование "передаётся" через generic | Наследуется ли статус VIP при входе в разные залы? |
| **Covariant** | Сохраняет направление наследования | Дети знаменитостей тоже знамениты |
| **Contravariant** | Инвертирует направление | Врач для взрослых может лечить и детей |
| **Invariant** | Наследование не передаётся | Билет на имя — только для владельца |

---

## ПОЧЕМУ variance важна

### Проблема: кажется логичным, но опасно

```kotlin
open class Animal
class Dog : Animal()
class Cat : Animal()

// Dog IS-A Animal — это мы знаем
val dog: Animal = Dog()  // OK

// Но...
val dogs: MutableList<Dog> = mutableListOf(Dog())
val animals: MutableList<Animal> = dogs  // Можно?
```

Интуитивно кажется: если `Dog` IS-A `Animal`, то `List<Dog>` IS-A `List<Animal>`.

**Но это опасно!**

```kotlin
// Если бы это компилировалось:
val dogs: MutableList<Dog> = mutableListOf(Dog())
val animals: MutableList<Animal> = dogs  // Представим, что OK

animals.add(Cat())  // Добавили кота в "список животных"

val dog: Dog = dogs[0]  // Но dogs[0] теперь Cat!
// → ClassCastException!
```

### Проблема в том, что MutableList позволяет и читать, и писать

Когда тип используется **только для чтения** — covariance безопасна.
Когда тип используется **только для записи** — contravariance безопасна.
Когда **и то, и другое** — только invariance.

---

## ЧТО такое три вида Variance

### Визуальное объяснение

```
┌─────────────────────────────────────────────────────────────┐
│                    ТРИ ВИДА VARIANCE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Наследование типов:                                       │
│   Dog ────────────→ Animal (Dog IS-A Animal)               │
│                                                             │
│   COVARIANT (out):                                          │
│   Producer<Dog> → Producer<Animal>  (то же направление)    │
│   "Производитель собак — производитель животных"           │
│                                                             │
│   CONTRAVARIANT (in):                                       │
│   Consumer<Animal> → Consumer<Dog>  (обратное направление) │
│   "Потребитель животных — потребитель собак"               │
│                                                             │
│   INVARIANT:                                                │
│   Box<Dog> ≠ Box<Animal>  (нет отношения)                  │
│   "Коробка для собак — не коробка для животных"            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Covariance (out) — направление сохраняется

```kotlin
interface Producer<out T> {
    fun produce(): T  // T только возвращается
}

val dogProducer: Producer<Dog> = object : Producer<Dog> {
    override fun produce() = Dog()
}

// Dog IS-A Animal → Producer<Dog> IS-A Producer<Animal>
val animalProducer: Producer<Animal> = dogProducer  // OK!

val animal: Animal = animalProducer.produce()  // Безопасно: вернёт Dog
```

**Почему безопасно:** Мы ожидаем `Animal`, получаем `Dog`. `Dog` IS-A `Animal` — всё OK.

### Contravariance (in) — направление инвертируется

```kotlin
interface Consumer<in T> {
    fun consume(item: T)  // T только принимается
}

val animalConsumer: Consumer<Animal> = object : Consumer<Animal> {
    override fun consume(item: Animal) { println(item) }
}

// Animal IS-A суперtype Dog → Consumer<Animal> IS-A Consumer<Dog>
val dogConsumer: Consumer<Dog> = animalConsumer  // OK!

dogConsumer.consume(Dog())  // Безопасно: Animal consumer примет Dog
```

**Почему безопасно:** Мы передаём `Dog`, consumer ожидает `Animal`. `Dog` IS-A `Animal` — всё OK.

### Invariance — нет отношения

```kotlin
class MutableBox<T>(var value: T)  // И чтение, и запись

val dogBox: MutableBox<Dog> = MutableBox(Dog())
// val animalBox: MutableBox<Animal> = dogBox  // Error!

// Если бы было OK:
// animalBox.value = Cat()  // Записали Cat
// val dog: Dog = dogBox.value  // Читаем Cat как Dog — crash!
```

---

## PECS: Producer-Extends, Consumer-Super

### Мнемоника Joshua Bloch

> "PECS: Producer Extends, Consumer Super"
>
> — Joshua Bloch, Effective Java

**Producer** — мы **читаем** из него → `extends` (Java) / `out` (Kotlin)
**Consumer** — мы **пишем** в него → `super` (Java) / `in` (Kotlin)

### Пример: Collections.copy

```java
// Java
public static <T> void copy(
    List<? super T> dest,      // Consumer: пишем в dest
    List<? extends T> src      // Producer: читаем из src
) {
    for (T item : src) {
        dest.add(item);
    }
}
```

```kotlin
// Kotlin
fun <T> copy(
    dest: MutableList<in T>,   // Consumer: пишем
    src: List<out T>           // Producer: читаем
) {
    for (item in src) {
        dest.add(item)
    }
}
```

### Таблица решений

| Что делаем с типом? | Java Wildcard | Kotlin | Variance |
|---------------------|---------------|--------|----------|
| Только читаем | `? extends T` | `out T` | Covariant |
| Только пишем | `? super T` | `in T` | Contravariant |
| И то, и другое | `T` | `T` | Invariant |

---

## Kotlin: Declaration-site vs Use-site

### Declaration-site Variance (Kotlin)

Variance объявляется **один раз** при определении типа:

```kotlin
// Объявили: T только для чтения
interface Source<out T> {
    fun next(): T
}

// Теперь ВЕЗДЕ Source covariant
fun demo(dogs: Source<Dog>) {
    val animals: Source<Animal> = dogs  // Работает без wildcards
}
```

### Use-site Variance (Java)

Variance указывается **каждый раз** при использовании:

```java
// Каждый раз пишем wildcard
void demo(List<? extends Animal> animals) { ... }
void another(List<? extends Animal> animals) { ... }
// Надоедает!
```

### Преимущество Kotlin

Declaration-site variance уменьшает boilerplate. Один раз объявил — везде работает.

---

## Позиции типа: in vs out

### Out-position (возвращаемое значение)

```kotlin
interface Source<out T> {
    fun produce(): T           // OK: T в out-position
    // fun consume(item: T)    // Error: T в in-position
}
```

### In-position (параметр)

```kotlin
interface Sink<in T> {
    fun consume(item: T)       // OK: T в in-position
    // fun produce(): T        // Error: T в out-position
}
```

### Почему такие ограничения?

```
┌─────────────────────────────────────────────────────────────┐
│               ПОЧЕМУ ОГРАНИЧЕНИЯ ПОЗИЦИЙ                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   COVARIANT (out T):                                        │
│   Producer<Dog> → Producer<Animal>                          │
│                                                             │
│   Если produce(): T                                         │
│   Producer<Dog>.produce() возвращает Dog                    │
│   Dog IS-A Animal → безопасно присвоить Animal             │
│   ✓ OK                                                      │
│                                                             │
│   Если consume(T):                                          │
│   Producer<Animal>.consume(Cat)                             │
│   Но Producer<Dog> не может принять Cat!                   │
│   ✗ ОПАСНО                                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Star Projection: `*`

### Когда тип неизвестен

```kotlin
fun printAll(list: List<*>) {
    for (item in list) {
        println(item)  // item: Any?
    }
}

printAll(listOf("a", "b"))
printAll(listOf(1, 2, 3))
printAll(listOf(User("Alice")))
```

### Star vs Raw Types

| Aspect | Kotlin `*` | Java Raw Types |
|--------|------------|----------------|
| Чтение | `Any?` | `Object` |
| Запись | Нельзя (кроме null) | Можно (unsafe!) |
| Безопасность | Type-safe | Unchecked warnings |

```kotlin
val list: MutableList<*> = mutableListOf("a", "b")

val first: Any? = list.first()  // OK: читаем как Any?
// list.add("c")  // Error: нельзя писать
list.add(null)  // OK: null можно
```

---

## Реальные примеры в Kotlin

### List vs MutableList

```kotlin
// List — covariant (out T)
interface List<out E> : Collection<E> {
    operator fun get(index: Int): E  // Только чтение
}

val dogs: List<Dog> = listOf(Dog())
val animals: List<Animal> = dogs  // OK: covariant

// MutableList — invariant (T)
interface MutableList<E> : List<E>, MutableCollection<E> {
    fun add(element: E): Boolean  // Запись
    operator fun get(index: Int): E  // Чтение
}

val mutableDogs: MutableList<Dog> = mutableListOf(Dog())
// val mutableAnimals: MutableList<Animal> = mutableDogs  // Error!
```

### Comparable — contravariant

```kotlin
interface Comparable<in T> {
    fun compareTo(other: T): Int
}

val animalComparator: Comparable<Animal> = ...
val dogComparator: Comparable<Dog> = animalComparator  // OK

// Comparator для Animal может сравнивать и Dog
```

---

## Подводные камни

### Когда НЕ использовать variance

**Нужно и читать, и писать:**
```kotlin
class Cache<T> {
    fun get(key: String): T = ...
    fun put(key: String, value: T) = ...
}
// Invariant — единственный вариант
```

### Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| `out` для mutable | Compile error | Invariant или разделить interfaces |
| `in` для return type | Compile error | Использовать `out` |
| Путаница in/out | Type mismatch | PECS: читаем=out, пишем=in |
| Star projection везде | Потеря type info | Использовать конкретные типы |

### Мифы и заблуждения

**Миф:** "`List<Dog>` IS-A `List<Animal>` всегда"
**Реальность:** Только для read-only `List<out T>`. Для `MutableList<T>` — нет.

**Миф:** "Variance — это про наследование"
**Реальность:** Variance — про то, как наследование **передаётся** через generics.

---

## Куда дальше

**Если здесь впервые:**
→ Попрактикуйся с `out` и `in` на простых интерфейсах

**Если понял и хочешь глубже:**
→ [[type-erasure-reification]] — что происходит с типами в runtime

**Практическое применение:**
→ Kotlin Collections API активно использует variance

---

## Связь с другими темами

### [[generics-parametric-polymorphism]]
Variance — это ответ на вопрос "как subtyping взаимодействует с generics". Без понимания type parameters, generic классов и интерфейсов нет смысла говорить о ковариантности и контравариантности. Generics определяют контейнер (`Box<T>`), а variance определяет, можно ли присвоить `Box<Dog>` переменной типа `Box<Animal>`. Это два неразрывно связанных аспекта системы типов.

### [[type-erasure-reification]]
Type erasure влияет на то, как variance работает в runtime. На JVM `List<Dog>` и `List<Animal>` после erasure неотличимы, поэтому variance constraints (`out`, `in`) проверяются исключительно компилятором. Понимание erasure объясняет, почему Kotlin разделяет `List<out T>` (read-only, covariant) и `MutableList<T>` (invariant): компилятор должен гарантировать безопасность, которую runtime не может обеспечить.

---

## Источники и дальнейшее чтение

- Pierce B. (2002). *Types and Programming Languages (TAPL)*. — формальное определение variance через правила subtyping для функциональных типов и generic конструкторов
- Cardelli L., Wegner P. (1985). *On Understanding Types, Data Abstraction, and Polymorphism*. — классическая систематизация полиморфизма, включая subtype polymorphism, на котором основана variance
- Bloch J. (2018). *Effective Java*, 3rd ed. — Item 31 "Use bounded wildcards to increase API flexibility" — практическое объяснение PECS и его применения
- [TypeAlias: Illustrated Guide to Variance](https://typealias.com/guides/illustrated-guide-covariance-contravariance/) — лучшая визуализация
- [Kotlin Docs: Generics](https://kotlinlang.org/docs/generics.html) — official reference

---

*Проверено: 2026-01-09*
