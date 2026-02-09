---
title: "Kotlin Overview"
created: 2025-12-19
modified: 2025-12-19
type: moc
status: published
tags:
  - topic/jvm
  - type/moc
  - level/beginner
---

# Kotlin: Карта раздела

> Современный JVM язык — лаконичный, безопасный, прагматичный

---

## TL;DR

**Kotlin** — язык от JetBrains, 100% совместимый с Java. Null safety, extension functions, coroutines "из коробки". Официальный язык для Android (с 2017).

**Почему Kotlin:**
- **Меньше кода** — data class вместо 50 строк boilerplate
- **Null safety** — `NullPointerException` в compile-time, не в runtime
- **Coroutines** — async код выглядит как синхронный
- **Interop** — вызываешь Java из Kotlin и наоборот без проблем

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| **Новичок в Kotlin?** | [[kotlin-basics]] — синтаксис, null safety, data class |
| **Уже знаешь Java?** | [[kotlin-interop]] — отличия и совместимость |
| **Пишешь async код?** | [[kotlin-coroutines]] → [[kotlin-flow]] |
| **Изучаешь ФП?** | [[kotlin-functional]] — lambdas, higher-order functions |
| **Multiplatform?** | [[kotlin-multiplatform]] — один код для Android/iOS/Web |

---

## Путь обучения

```
Для новичков (0 → Junior):
┌──────────────────────────────────────────────────────────────┐
│ [[kotlin-basics]] → [[kotlin-oop]] → [[kotlin-collections]]  │
│      ↓                                                        │
│ [[kotlin-functional]] → [[kotlin-type-system]]               │
└──────────────────────────────────────────────────────────────┘

Для опытных (Junior → Middle):
┌──────────────────────────────────────────────────────────────┐
│ [[kotlin-coroutines]] → [[kotlin-flow]] → [[kotlin-testing]] │
│      ↓                                                        │
│ [[kotlin-best-practices]] → [[kotlin-advanced-features]]     │
└──────────────────────────────────────────────────────────────┘

Для Android разработчиков:
┌──────────────────────────────────────────────────────────────┐
│ [[kotlin-basics]] → [[kotlin-coroutines]] → [[android-compose]]
│      ↓                                                        │
│ [[kotlin-flow]] → [[android-architecture]]                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Статьи

### Основы языка

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[kotlin-basics]] | Синтаксис, null safety, data class, when | Junior |
| [[kotlin-oop]] | Классы, объекты, inheritance, delegation | Junior |
| [[kotlin-type-system]] | Generics, variance, reified types | Middle |
| [[kotlin-collections]] | List, Set, Map, Sequences | Junior |

### Функциональное программирование

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[kotlin-functional]] | Lambdas, HOF, inline functions | Middle |
| [[kotlin-advanced-features]] | DSL, contracts, context receivers | Senior |

### Асинхронность

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[kotlin-coroutines]] | Coroutines, Dispatchers, structured concurrency | Middle |
| [[kotlin-flow]] | Reactive streams, StateFlow, SharedFlow | Middle |

### Практика

| Статья | Описание | Уровень |
|--------|----------|---------|
| [[kotlin-best-practices]] | Идиомы, конвенции, common pitfalls | Middle |
| [[kotlin-testing]] | JUnit5, MockK, Kotest | Middle |
| [[kotlin-interop]] | Java ↔ Kotlin, аннотации совместимости | Middle |
| [[kotlin-multiplatform]] | KMP: один код для всех платформ | Senior |

---

## Kotlin vs Java: когда что использовать

| Критерий | Kotlin | Java |
|----------|--------|------|
| **Новый проект** | ✅ Рекомендуется | Только если legacy constraints |
| **Android** | ✅ Официальный язык | Устаревший подход |
| **Backend** | ✅ Spring Boot поддержка | Тоже хорошо |
| **Null safety** | ✅ Compile-time | Runtime (Optional) |
| **Boilerplate** | ✅ Минимум | Много |
| **Команда знает только Java** | Нужно обучение | ✅ Быстрый старт |

**Рекомендация:** Kotlin для новых проектов. Java для поддержки legacy или если команда не готова.

---

## Ключевые концепции

| Концепция | Kotlin | Java эквивалент |
|-----------|--------|-----------------|
| **Null safety** | `String?` vs `String` | `@Nullable`, `Optional<T>` |
| **Data class** | `data class User(val name: String)` | 50+ строк POJO |
| **Extension functions** | `fun String.hello() = "Hello, $this"` | Utility classes |
| **Coroutines** | `suspend fun`, `launch`, `async` | CompletableFuture, Reactor |
| **Sealed classes** | `sealed class Result` | Enum + instanceof |
| **Delegation** | `by lazy`, `by Delegates.observable` | Ручная реализация |

---

## Связи

### Связи внутри JVM раздела
- [[jvm-overview]] — JVM internals (bytecode, GC, JIT)
- [[java-modern-features]] — Java 8-21: что Kotlin делает по-другому
- [[jvm-concurrency-overview]] — как coroutines используют JVM threads

### Связи с Android
- [[android-overview]] — Kotlin для Android разработки
- [[android-compose]] — Jetpack Compose (Kotlin DSL для UI)
- [[android-coroutines]] — Coroutines в Android (lifecycle, viewModelScope)

### Связи с архитектурой
- [[clean-code-solid]] — SOLID принципы в Kotlin
- [[design-patterns]] — Паттерны GoF в Kotlin идиоматике

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Kotlin медленнее Java" | Kotlin компилируется в **тот же bytecode**. Performance идентична или лучше (inline functions) |
| "Kotlin = только Android" | Kotlin **Multiplatform** работает везде: JVM, JS, Native, WASM. Backend на Ktor набирает популярность |
| "Coroutines = новые threads" | Coroutines — **suspension points**, не threads. Тысячи coroutines на одном thread |
| "Null safety убирает NPE" | Null safety **переносит проверки** на compile time. `!!` и interop с Java всё ещё опасны |
| "Kotlin заменит Java" | Kotlin **дополняет** Java. 100% interop означает сосуществование в одном проекте |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin |
|--------------|---------------------|
| **Type System** | Nullable types как Algebraic Data Types. `String?` = `String | null` |
| **Functional Programming** | Lambdas, HOF, immutability (`val`), extension functions |
| **Coroutines** | Continuation-passing style под капотом. State machine в bytecode |
| **Null Safety** | Compile-time null checking. Option type без wrapper overhead |
| **DSL Construction** | Lambda with receiver, infix functions, operator overloading |

---

## Источники

- [Kotlin Official Documentation](https://kotlinlang.org/docs/) — официальная документация
- [Kotlin Koans](https://play.kotlinlang.org/koans/) — интерактивный туториал
- [Roman Elizarov talks](https://www.youtube.com/@RomanElizarov) — автор Kotlin Coroutines
- [Kotlin Style Guide](https://kotlinlang.org/docs/coding-conventions.html) — конвенции кодирования

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 12 |
| Последнее обновление | 2025-12-19 |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
