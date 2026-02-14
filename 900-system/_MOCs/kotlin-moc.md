---
title: "Kotlin MOC"
created: 2025-11-25
modified: 2025-11-25
type: moc
tags:
  - topic/kotlin
  - topic/jvm
  - type/moc
  - navigation
---

# Kotlin MOC

> Современный язык для JVM, Android, Multiplatform — от основ до профессионального уровня

---

## Путь обучения

Рекомендуемый порядок изучения:

```
1. [[kotlin-basics]]              — Синтаксис, типы, null-safety
         ↓
2. [[kotlin-oop]]                 — Классы, наследование, sealed/data classes
         ↓
3. [[kotlin-collections]]         — Collections API, sequences
         ↓
4. [[kotlin-functional]]          — Lambdas, scope functions
         ↓
5. [[kotlin-coroutines]]          — Асинхронность, structured concurrency
         ↓
6. [[kotlin-flow]]                — Reactive streams, StateFlow/SharedFlow
         ↓
6b. [[kotlin-channels]]           — Channels: межкорутинная коммуникация
         ↓
6c. [[kotlin-coroutines-internals]] — Как корутины работают внутри (CPS, state machine)
         ↓
7. [[kotlin-advanced-features]]   — Extensions, delegates, DSL
         ↓
8. [[kotlin-type-system]]         — Generics, variance, contracts
         ↓
9. [[kmp-overview|kotlin-multiplatform]]       — KMP, expect/actual, платформы
         ↓
10. [[kotlin-interop]]            — Java interop, платформенная интеграция
         ↓
11. [[kotlin-testing]]            — Testing patterns, моки
         ↓
12. [[kotlin-best-practices]]     — Style guide, архитектура
```

---

## Статьи по темам

### Основы (Beginner)
- [[kotlin-basics]] — Синтаксис, переменные, null-safety, функции, when
- [[kotlin-oop]] — Classes, data/sealed/value classes, наследование
- [[kotlin-collections]] — List/Set/Map, операции, sequences

### Функциональное программирование (Intermediate)
- [[kotlin-functional]] — Lambdas, higher-order functions, let/apply/run/also/with
- [[kotlin-collections]] — map, filter, fold, groupBy

### Асинхронность (Intermediate → Advanced)
- [[kotlin-coroutines]] — suspend, launch/async, CoroutineScope, structured concurrency
- [[kotlin-flow]] — Flow, StateFlow, SharedFlow, операторы, backpressure
- [[kotlin-channels]] — Channel: межкорутинная коммуникация, fan-out/fan-in, select
- [[kotlin-coroutines-internals]] — CPS, Continuation, state machine: как корутины работают внутри

### Продвинутые возможности (Advanced)
- [[kotlin-advanced-features]] — Extension functions, operator overloading, delegates, DSL
- [[kotlin-type-system]] — Generics, in/out variance, reified, contracts

### Multiplatform (Advanced)
- [[kmp-overview|kotlin-multiplatform]] — KMP architecture, expect/actual, targets (JVM/JS/Native/Wasm)
- [[kotlin-interop]] — Java interop, platform-specific APIs

### Качество кода (All levels)
- [[kotlin-testing]] — JUnit 5, MockK, Kotest, coroutines testing
- [[kotlin-best-practices]] — Coding conventions, архитектурные паттерны

---

## Ключевые концепции

| Концепция | Описание | Где подробнее |
|-----------|----------|---------------|
| Null Safety | Система типов предотвращает NPE | [[kotlin-basics]] |
| Data Classes | Автогенерация equals/hashCode/toString | [[kotlin-oop]] |
| Sealed Classes | Закрытые иерархии для исчерпывающих when | [[kotlin-oop]] |
| Extension Functions | Добавление методов к существующим типам | [[kotlin-advanced-features]] |
| Coroutines | Structured concurrency, async без callback hell | [[kotlin-coroutines]] |
| Flow | Reactive streams для асинхронных данных | [[kotlin-flow]] |
| Scope Functions | let/apply/run/also/with для контекста | [[kotlin-functional]] |
| Delegates | lazy, observable, custom delegation | [[kotlin-advanced-features]] |
| Inline Functions | Zero-overhead abstractions | [[kotlin-advanced-features]] |
| Reified Types | Доступ к generic типам в runtime | [[kotlin-type-system]] |
| DSL | Type-safe builders | [[kotlin-advanced-features]] |
| KMP | Один код для всех платформ | [[kmp-overview|kotlin-multiplatform]] |

---

## Связанные области

- [[jvm-languages-ecosystem]] — Kotlin в экосистеме JVM
- [[jvm-concurrency-overview|jvm-concurrency]] — Модель памяти JVM для корутин
- [[java-modern-features]] — Сравнение с Java 8-21
- [[design-patterns]] — Паттерны в Kotlin
- [[testing-strategies]] — Стратегии тестирования

---

## Применение Kotlin

**Android Development:**
- Официальный язык для Android (с 2019)
- Jetpack Compose — современный UI toolkit
- Kotlin Android Extensions (deprecated → View Binding)

**Backend:**
- Ktor — асинхронный веб-фреймворк
- Spring Boot — full Kotlin support
- Exposed — type-safe SQL DSL

**Multiplatform:**
- iOS apps через Kotlin/Native
- Web через Kotlin/JS или Kotlin/Wasm
- Desktop через Compose Multiplatform

**Data Science:**
- Kotlin Notebook (JetBrains)
- Integration с pandas, numpy

---

## Kotlin vs Java

| Аспект | Kotlin | Java |
|--------|--------|------|
| Null safety | Compile-time | Runtime (NPE) |
| Boilerplate | Минимальный | Verbose |
| Extension functions | ✅ | ❌ (Java 21+: extension methods ограничены) |
| Coroutines | Native | Project Loom (Java 21+) |
| Data classes | 1 строка | Lombok или Records (Java 16+) |
| Smart casts | Автоматически | Требует instanceof + cast |
| Default parameters | ✅ | ❌ (до Java 21) |
| Pattern matching | when exhaustive | switch (Java 21+) |

---

## Статус контента

| Статья | Статус | Уровень |
|--------|--------|---------|
| kotlin-basics | created | Beginner |
| kotlin-oop | created | Beginner |
| kotlin-collections | created | Beginner/Intermediate |
| kotlin-functional | created | Intermediate |
| kotlin-coroutines | created | Intermediate |
| kotlin-flow | created | Intermediate/Advanced |
| kotlin-advanced-features | created | Advanced |
| kotlin-type-system | created | Advanced |
| kotlin-multiplatform | created | Advanced |
| kotlin-interop | created | Intermediate |
| kotlin-testing | created | All levels |
| kotlin-best-practices | created | All levels |
| kotlin-channels | created | Intermediate/Advanced |
| kotlin-coroutines-internals | created | Advanced |

---

## Версии и roadmap

**Текущая стабильная:** Kotlin 2.1.0 (ноябрь 2024)
**Компилятор:** K2 (stable с версии 2.0)
**Roadmap 2025:**
- Kotlin/Wasm stable
- Kotlin-to-Swift export (1st public release)
- Compose Multiplatform для iOS stable

---

*Последнее обновление: 2025-11-25*
