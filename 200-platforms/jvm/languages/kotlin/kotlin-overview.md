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
reading_time: 5
difficulty: 2
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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
- [[solid-principles]] — SOLID принципы в Kotlin
- [[design-patterns-overview]] — Паттерны GoF в Kotlin идиоматике

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

---

## Проверь себя

> [!question]- Почему Kotlin null safety не гарантирует полное отсутствие NullPointerException в проекте?
> Kotlin null safety переносит проверки на уровень компилятора, но NPE все ещё возможен в нескольких случаях: (1) использование оператора `!!` — принудительный unwrap nullable типа; (2) interop с Java-кодом, где типы приходят как platform types без информации о nullable; (3) некорректная инициализация (`lateinit var` до присваивания). Null safety — это инструмент снижения риска, а не абсолютная гарантия.

> [!question]- Команда из 5 Java-разработчиков начинает новый Android-проект. Аргументируйте выбор между Kotlin и Java, учитывая кривую обучения и долгосрочные последствия.
> Kotlin предпочтителен: (1) он официальный язык Android с 2017, новые Android API и Jetpack Compose написаны на Kotlin; (2) 100% interop с Java позволяет команде мигрировать постепенно, используя существующие знания; (3) null safety и data class сократят количество багов и boilerplate уже в первые недели; (4) кривая обучения для Java-разработчиков минимальна — синтаксис во многом интуитивен. Единственный аргумент за Java — если проект краткосрочный и команда категорически не готова вкладываться в обучение.

> [!question]- Coroutines часто сравнивают с потоками (threads). Объясните, в чём принципиальное архитектурное отличие, и почему можно запустить 100 000 coroutines, но не 100 000 потоков.
> Потоки — ресурсы ОС, каждый занимает ~1 МБ стека и требует контекстного переключения на уровне ядра. Coroutines — абстракция уровня языка, реализованная через continuation-passing style: компилятор преобразует `suspend`-функции в state machine. При suspension coroutine не блокирует поток, а сохраняет состояние и освобождает его для другой работы. Поэтому тысячи coroutines могут исполняться на нескольких потоках из пула, без overhead на создание и переключение потоков ОС.

> [!question]- В таблице "Kotlin vs Java" указано, что extension functions заменяют utility classes. Какое ограничение у extension functions делает это сравнение не совсем точным?
> Extension functions — синтаксический сахар: они компилируются в обычные статические методы, где первый параметр — объект-получатель. Это значит, что (1) они не имеют доступа к `private`/`protected` членам класса; (2) они разрешаются статически (по типу переменной, а не объекта), поэтому не поддерживают полиморфизм; (3) они не могут переопределить существующие методы класса. Extension functions удобнее utility classes по читаемости и discoverability, но это не полноценное расширение класса.

---

## Ключевые карточки

Что означает тип `String?` в Kotlin и чем он отличается от `String`?
?
`String?` — nullable тип, который может содержать `null` или строку. `String` — non-null тип, компилятор гарантирует, что значение никогда не будет `null`. Это реализация null safety на уровне системы типов.

Как coroutines реализованы под капотом в Kotlin?
?
Компилятор преобразует `suspend`-функции в state machine с использованием Continuation-Passing Style (CPS). Каждая точка приостановки становится состоянием в конечном автомате. При suspension сохраняется continuation-объект, а поток освобождается для другой работы.

Почему Kotlin компилируется с такой же производительностью, как Java?
?
Kotlin компилируется в тот же JVM bytecode, что и Java. Более того, `inline`-функции устраняют overhead от лямбд, раскрывая их тело прямо в месте вызова, что может дать даже лучшую производительность.

Что такое `data class` и какие методы генерирует компилятор?
?
`data class` — класс для хранения данных. Компилятор автоматически генерирует `equals()`, `hashCode()`, `toString()`, `copy()` и `componentN()` функции для деструктуризации. Заменяет десятки строк Java boilerplate одной строкой.

В чём разница между `val` и `var` и как это связано с функциональным программированием?
?
`val` — неизменяемая ссылка (аналог `final` в Java), `var` — изменяемая. Предпочтение `val` продвигает иммутабельность — ключевой принцип ФП, который уменьшает количество побочных эффектов и делает код предсказуемее в многопоточной среде.

Что такое sealed class и какую проблему он решает?
?
`sealed class` — класс с ограниченной иерархией наследников, все подклассы известны на этапе компиляции. Решает проблему exhaustive `when`-выражений: компилятор проверяет, что обработаны все варианты, и выдаёт ошибку при пропуске. Альтернатива enum с возможностью хранить данные разных типов.

Что означает 100% interop между Kotlin и Java?
?
Kotlin-код может вызывать любой Java-код напрямую, и наоборот. Оба языка компилируются в JVM bytecode и могут сосуществовать в одном проекте, файлы обоих языков видят друг друга. Это позволяет мигрировать постепенно, файл за файлом.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Первый шаг | [[kotlin-basics]] | Синтаксис, null safety, data class, when — фундамент языка |
| Асинхронность | [[kotlin-coroutines]] | Structured concurrency, suspend-функции, Dispatchers |
| Reactive потоки | [[kotlin-flow]] | StateFlow, SharedFlow — реактивное программирование поверх coroutines |
| Мультиплатформа | [[kmp-overview]] | Kotlin Multiplatform — один код для Android, iOS, Desktop, Web |
| JVM под капотом | [[jvm-overview]] | Bytecode, GC, JIT — понимание среды исполнения Kotlin |
| Система типов (CS) | [[type-systems-fundamentals]] | Теория типов — почему nullable types работают как Algebraic Data Types |
| Android UI | [[android-compose]] | Jetpack Compose — декларативный UI на Kotlin DSL |
