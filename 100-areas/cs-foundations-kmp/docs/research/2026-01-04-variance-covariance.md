# Research Report: Variance and Covariance

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Variance определяет, как наследование типов влияет на наследование generic типов. Covariance (`out`): `List<Dog>` IS-A `List<Animal>` — для чтения. Contravariance (`in`): `Comparator<Animal>` IS-A `Comparator<Dog>` — для записи. Invariance: нет отношения. PECS: Producer-Extends, Consumer-Super. Kotlin: declaration-site variance (out/in в объявлении), Java: use-site (wildcards при использовании). Liskov Substitution Principle связан с variance.

## Key Findings

### 1. Три вида Variance

| Variance | Kotlin | Java | Отношение |
|----------|--------|------|-----------|
| Covariant | `out T` | `? extends T` | Subtype → Subtype |
| Contravariant | `in T` | `? super T` | Subtype → Supertype |
| Invariant | `T` | `T` | Нет отношения |

### 2. PECS: Producer-Extends, Consumer-Super

**Joshua Bloch (Effective Java):**

> "For maximum flexibility, use wildcard types on input parameters that represent producers or consumers"

- **Producer:** Только читаем → `extends` / `out`
- **Consumer:** Только пишем → `super` / `in`
- **Оба:** Без wildcards, invariant

**Пример:**
```java
Collections.copy(List<? super T> dest, List<? extends T> src)
// src — producer (читаем), extends
// dest — consumer (пишем), super
```

### 3. Liskov Substitution Principle

**LSP:**
> "Если S subtype of T, то объекты T можно заменить на S без изменения поведения"

**Связь с variance:**
- Covariance return types
- Contravariance method arguments
- Нарушение LSP → unsafe код

### 4. Kotlin vs Java

**Java: Use-site variance:**
```java
void process(List<? extends Animal> animals) { ... }
```
Variance указывается при использовании.

**Kotlin: Declaration-site variance:**
```kotlin
interface Source<out T> {
    fun next(): T
}
```
Variance указывается в объявлении типа.

### 5. out = Covariance

```kotlin
interface Producer<out T> {
    fun produce(): T  // OK: T в out-position
    // fun consume(item: T)  // Error: T в in-position
}

val dogs: Producer<Dog> = ...
val animals: Producer<Animal> = dogs  // OK: covariant
```

### 6. in = Contravariance

```kotlin
interface Consumer<in T> {
    fun consume(item: T)  // OK: T в in-position
    // fun produce(): T  // Error: T в out-position
}

val animalConsumer: Consumer<Animal> = ...
val dogConsumer: Consumer<Dog> = animalConsumer  // OK: contravariant
```

### 7. Почему MutableList invariant

```kotlin
val dogs: MutableList<Dog> = mutableListOf(Dog())
val animals: MutableList<Animal> = dogs  // Error!

// Если бы было OK:
animals.add(Cat())  // Добавили Cat в List<Dog>!
val dog: Dog = dogs[0]  // ClassCastException: Cat cannot be cast to Dog
```

### 8. Star Projection

**Kotlin `*`:**
- `List<*>` ≈ `List<out Any?>`
- Можно читать как Any?
- Нельзя писать (безопасно)

**Безопаснее Java raw types.**

## Community Sentiment

### Positive
- Kotlin out/in интуитивнее Java wildcards
- Declaration-site variance уменьшает boilerplate
- PECS — полезная мнемоника

### Negative
- Variance сложна для понимания
- Путаница in/out поначалу
- Star projection неочевидна

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [TypeAlias: Illustrated Guide](https://typealias.com/guides/illustrated-guide-covariance-contravariance/) | Tutorial | ★★★★★ | Visual explanation |
| [Kotlin Docs: Generics](https://kotlinlang.org/docs/generics.html) | Official | ★★★★★ | Declaration-site variance |
| [Baeldung: PECS](https://www.baeldung.com/java-generics-pecs) | Tutorial | ★★★★☆ | PECS examples |
| [Kotlin Primer: Variance](https://www.kotlinprimer.com/classes-what-we-know-from-java/generics/covariance-contravariance-invariance/) | Tutorial | ★★★★☆ | Clear explanations |
| [Wikipedia: Type Variance](https://en.wikipedia.org/wiki/Covariance_and_contravariance_(computer_science)) | Reference | ★★★★☆ | Formal definitions |

## Research Methodology
- **Queries used:** 2 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **Focus areas:** PECS, Kotlin out/in, Liskov, Java wildcards

---

*Проверено: 2026-01-09*
