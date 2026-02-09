# Research Report: Type Systems Fundamentals

**Date:** 2026-01-04
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Type system — набор правил для присвоения типов конструкциям языка. Static typing проверяет типы при компиляции (Java, Kotlin), dynamic — при выполнении (Python, JS). Strong/weak — про строгость неявных преобразований (Python strong, JS weak). История: Russell (1908) → теория типов для избежания парадоксов, Church (1940) → simply typed lambda calculus, Hindley-Milner (1969-1978) → type inference для ML/Haskell. Nominal typing (Java) — по именам, structural (TypeScript/Go) — по структуре, duck (Python) — по поведению runtime. Kotlin: static + strong + nominal + null safety + smart casts.

## Key Findings

### 1. Static vs Dynamic Typing

**Static typing:**
- Типы проверяются при компиляции
- Ошибки типов предотвращают выполнение
- Языки: Java, C++, Kotlin, Haskell, Rust

**Dynamic typing:**
- Типы проверяются при выполнении
- Значения помечены тегами типов runtime
- Языки: Python, JavaScript, Ruby, PHP

**Преимущества static:**
- Ошибки ловятся раньше (до production)
- Лучшая производительность (compile-time optimization)
- Типы как документация

**Преимущества dynamic:**
- Быстрое прототипирование
- Меньше boilerplate
- Гибкость при изменениях

### 2. Strong vs Weak Typing

| Аспект | Strong | Weak |
|--------|--------|------|
| Неявные преобразования | Запрещены/минимальны | Разрешены |
| `"5" + 2` | Ошибка | `"52"` или `7` |
| Примеры | Python, Haskell | JavaScript, C |

**Важно:** Strong ≠ Static. Python — dynamic + strong. C — static + weak.

### 3. История Type Theory

**1908 — Bertrand Russell:**
- Ramified theory of types
- Решение Russell's paradox
- Иерархия типов

**1920-е — Ramsey, Chwistek:**
- Упрощение до Simple Type Theory
- Убрали vicious circle principle

**1936 — Alonzo Church:**
- Untyped lambda calculus
- Показан inconsistent (Kleene-Rosser paradox)

**1940 — Church:**
- Simply typed lambda calculus
- Основа для typed FP

**1958 — Curry, Feys:**
- Type inference для simply typed LC

**1969 — Hindley:**
- Доказал: алгоритм всегда выводит most general type

**1978 — Milner:**
- Algorithm W (независимо от Hindley)
- Основа для ML type system

### 4. Hindley-Milner Type System

**Ключевые свойства:**
- Complete type inference (без аннотаций)
- Principal types (самый общий тип)
- Parametric polymorphism
- Decidable type checking

**Языки:**
- ML, OCaml, Haskell
- Влияние на F#, Scala, Rust

**Sweet spot:** Баланс между выразительностью и простотой вывода типов.

### 5. Nominal vs Structural vs Duck Typing

| Аспект | Nominal | Structural | Duck |
|--------|---------|------------|------|
| Совместимость | По имени/наследованию | По структуре | По поведению |
| Проверка | Compile-time | Compile-time | Runtime |
| Языки | Java, C++, Kotlin | TypeScript, Go | Python, JS |

**Structural typing:** "Если у типа есть нужные поля и методы — он подходит"
**Duck typing:** "Если ходит как утка и крякает как утка — это утка"

### 6. Type Inference

**Что это:**
Автоматическое определение типов компилятором без explicit аннотаций.

**Примеры:**
```kotlin
val x = 42          // Int inferred
val list = listOf(1, 2, 3)  // List<Int> inferred
```

**Bidirectional inference (Kotlin):**
- Forward: из аргументов в результат
- Backward: из использования в параметры

### 7. Kotlin Type System Features

**Null Safety:**
- Два universes: nullable (`String?`) и non-nullable (`String`)
- NPE ловятся при компиляции
- Safe call `?.`, elvis `?:`, not-null assertion `!!`

**Smart Casts:**
- Flow-sensitive typing
- После `if (x is String)` — x автоматически String
- Работает только если compiler гарантирует неизменность

**Type Inference:**
- Local variable inference
- Generic type inference
- Bidirectional inference

**Safe Cast:**
- `as` — unsafe, throws ClassCastException
- `as?` — safe, returns null

### 8. Type Soundness

**Sound type system:** Гарантирует, что операции неправильные для типа не выполнятся.
- Haskell — sound
- C/C++ — unsound (можно обойти через cast)

**Progress + Preservation:** Если программа well-typed, она не застрянет в stuck state.

## Community Sentiment

### Positive
- Type inference снижает boilerplate
- Kotlin null safety избавляет от NPE
- TypeScript добавляет safety в JS
- Static typing критичен для больших команд

### Negative
- "Fighting with the type system"
- Type inference иногда unexpected
- Generics variance сложна
- Strict typing замедляет прототипирование

## Best Sources Found

| Source | Type | Quality | Key Value |
|--------|------|---------|-----------|
| [Wikipedia: Type System](https://en.wikipedia.org/wiki/Type_system) | Reference | ★★★★★ | Comprehensive overview |
| [CS331: Types Primer](https://www.cs.uaf.edu/~chappell/class/2025_spr/cs331/read/types_primer.html) | Academic | ★★★★★ | Clear definitions |
| [Baeldung: Static vs Dynamic](https://www.baeldung.com/cs/programming-types-comparison) | Tutorial | ★★★★☆ | Practical comparison |
| [Kotlin Docs: Null Safety](https://kotlinlang.org/docs/null-safety.html) | Official | ★★★★★ | Kotlin specifics |
| [Wikipedia: Hindley-Milner](https://en.wikipedia.org/wiki/Hindley%E2%80%93Milner_type_system) | Reference | ★★★★☆ | HM history |
| [Dan Luu: Empirical PL](https://danluu.com/empirical-pl/) | Research | ★★★★★ | Static vs dynamic research |
| [DEV: Nominal vs Structural](https://dev.to/awwsmm/whats-the-difference-between-nominal-structural-and-duck-typing-11f8) | Blog | ★★★★☆ | Clear comparison |

## Research Methodology
- **Queries used:** 6 search queries
- **Sources found:** 35+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** Static/dynamic, strong/weak, history, HM, Kotlin features

---

*Проверено: 2026-01-09*
