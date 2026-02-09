# Research Report: Generics and Parametric Polymorphism

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Generics (параметрический полиморфизм) — механизм абстрагирования от конкретных типов через type parameters. История: Girard/Reynolds 1972-74 (System F) → ML → Haskell → Java 5 (2004) → Kotlin. Java generics — invariant, требуют wildcards (extends/super). Kotlin — declaration-site variance (out/in), use-site (where), reified в inline. Type erasure на JVM: информация о типах теряется в runtime. Reified + inline обходят erasure. Bounds ограничивают type parameters. PECS: Producer-Extends, Consumer-Super.

## Key Findings

### 1. Что такое Parametric Polymorphism

**Определение:**
Способ определять типы или функции, generic по отношению к другим типам.

**Три вида polymorphism:**
- **Subtype (inclusion):** наследование классов
- **Ad-hoc:** перегрузка методов
- **Parametric:** generics

### 2. История: System F

**1972 — Jean-Yves Girard:**
- PhD thesis: "Interprétation fonctionnelle..."
- Polymorphic lambda calculus

**1974 — John Reynolds:**
- Независимое открытие
- Abstraction theorem

**System F формализует:**
- Параметрический полиморфизм
- Универсальная квантификация по типам
- Основа для ML, Haskell

**Эволюция в языках:**
- ML — 1973
- Haskell — 1990
- Java 5 — 2004
- Go — 2022

### 3. Kotlin Generics: синтаксис

**Generic class:**
```kotlin
class Box<T>(val value: T)
```

**Generic function:**
```kotlin
fun <T> singletonList(item: T): List<T> = listOf(item)
```

**Upper bound:**
```kotlin
fun <T : Comparable<T>> sort(list: List<T>)
```

**Multiple bounds (where):**
```kotlin
fun <T> copyWhenGreater(list: List<T>, threshold: T)
    where T : CharSequence, T : Comparable<T>
```

### 4. Variance в Kotlin

| Keyword | Variance | Аналог Java | Использование |
|---------|----------|-------------|---------------|
| `out` | Covariant | extends | Только чтение |
| `in` | Contravariant | super | Только запись |
| (nothing) | Invariant | — | Чтение и запись |

**Declaration-site variance:**
```kotlin
interface Source<out T> {
    fun next(): T  // OK: T в out-position
}
```

**Use-site variance:**
```kotlin
fun copy(from: Array<out Any>, to: Array<Any>) { ... }
```

### 5. Type Erasure

**Что это:**
JVM удаляет информацию о type parameters при компиляции.

**Последствия:**
- `List<String>` и `List<Int>` → одинаковый bytecode `List`
- Нельзя: `if (item is T)`, `T()`, `Array<T>()`
- Unchecked casts: `list as List<String>`

**Workaround: reified + inline:**
```kotlin
inline fun <reified T> isInstance(item: Any): Boolean {
    return item is T  // Работает!
}
```

### 6. PECS: Producer-Extends, Consumer-Super

**Joshua Bloch (Effective Java):**
- Producer: читаем из него → extends (out)
- Consumer: пишем в него → super (in)

```kotlin
fun copy(from: List<out Any>, to: MutableList<in Any>) {
    // from — producer (читаем)
    // to — consumer (пишем)
}
```

### 7. Star Projection

**Kotlin `*` vs Java raw types:**
- `List<*>` ≈ `List<out Any?>` — безопасное чтение
- Нельзя писать (кроме null)
- Безопаснее raw types

### 8. Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Raw types | Unchecked warnings, runtime errors | Всегда указывай type parameters |
| Ignore erasure | ClassCastException | Используй reified или tokens |
| Wrong variance | Compile errors или unsafe | PECS: out для чтения, in для записи |
| Unchecked cast | Runtime exception | Safe cast as?, проверки, reified |

### 9. Null Safety в Generics

**Default bound: Any?**
```kotlin
class Box<T>(val value: T)  // T может быть nullable
val box: Box<String?> = Box(null)
```

**Non-null bound:**
```kotlin
class Box<T : Any>(val value: T)  // T не nullable
val box: Box<String> = Box("hello")  // OK
val box: Box<String?> = ...  // Error!
```

## Community Sentiment

### Positive
- Kotlin variance (out/in) понятнее Java wildcards
- Reified решает проблему erasure
- Type inference уменьшает boilerplate
- Declaration-site variance удобнее use-site

### Negative
- Type erasure ограничивает возможности
- Variance сложна для понимания новичкам
- Star projection путает
- Reified работает только в inline

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Kotlin Docs: Generics](https://kotlinlang.org/docs/generics.html) | Official | ★★★★★ | Complete reference |
| [Wikipedia: System F](https://en.wikipedia.org/wiki/System_F) | Reference | ★★★★☆ | History, theory |
| [Baeldung: Kotlin Generics](https://www.baeldung.com/kotlin/generics) | Tutorial | ★★★★☆ | Practical examples |
| [TypeAlias: Generics](https://typealias.com/start/kotlin-generics/) | Tutorial | ★★★★★ | Visual explanations |
| [Oracle: Type Erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html) | Official | ★★★★☆ | Erasure mechanics |
| [DroidCon: Kotlin Generics](https://www.droidcon.com/2024/06/11/everything-about-generic-types-in-kotlin/) | Article | ★★★★☆ | Comprehensive overview |

## Research Methodology
- **Queries used:** 4 search queries
- **Sources found:** 30+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** System F history, Kotlin syntax, variance, erasure, reified

---

*Проверено: 2026-01-09*
