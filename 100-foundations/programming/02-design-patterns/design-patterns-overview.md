---
title: "Design Patterns: классификация и выбор паттернов"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/design-patterns
  - topic/kotlin
related:
  - "[[singleton-pattern]]"
  - "[[factory-pattern]]"
  - "[[builder-pattern]]"
  - "[[strategy-pattern]]"
  - "[[observer-pattern]]"
  - "[[decorator-pattern]]"
  - "[[adapter-pattern]]"
  - "[[state-pattern]]"
  - "[[solid-principles]]"
  - "[[oop-fundamentals]]"
---

# Design Patterns: классификация и выбор паттернов

В 1977 году архитектор Кристофер Александр написал книгу "A Pattern Language" --- каталог повторяющихся решений для проектирования зданий и городов. Семнадцать лет спустя четыре программиста (Gamma, Helm, Johnson, Vlissides --- "Банда четырёх") перенесли эту идею в разработку ПО и выпустили "Design Patterns: Elements of Reusable Object-Oriented Software" (1994). Книга описала 23 паттерна, но главная мысль была проще: **не изобретай решения заново --- документируй то, что уже работает**. Сегодня половина этих паттернов встроена в языки вроде Kotlin, а вторая половина по-прежнему спасает от спагетти-кода. Разберёмся, какие стоит знать, а какие давно заменены фичами языка.

---

## Три категории GoF

Все 23 паттерна GoF делятся на три группы по типу задачи, которую они решают:

```
┌──────────────────────────────────────────────────────────────────────┐
│                         DESIGN PATTERNS (GoF)                        │
├──────────────────────┬──────────────────────┬────────────────────────┤
│     CREATIONAL       │     STRUCTURAL       │      BEHAVIORAL        │
│  (Создание объектов) │ (Структура/Композиц.)│  (Взаимодействие)      │
├──────────────────────┼──────────────────────┼────────────────────────┤
│ Singleton            │ Adapter              │ Strategy               │
│ Factory Method       │ Decorator            │ Observer               │
│ Abstract Factory     │ Facade               │ State                  │
│ Builder              │ Composite            │ Command                │
│ Prototype            │ Proxy                │ Iterator               │
│                      │ Bridge               │ Template Method        │
│                      │ Flyweight            │ Mediator               │
│                      │                      │ Memento                │
│                      │                      │ Visitor                │
│                      │                      │ Chain of Responsibility│
│                      │                      │ Interpreter            │
├──────────────────────┼──────────────────────┼────────────────────────┤
│ КАК создавать        │ КАК собирать         │ КАК объекты            │
│ объекты?             │ объекты вместе?      │ общаются?              │
└──────────────────────┴──────────────────────┴────────────────────────┘
```

| Категория | Фокус | Ключевой принцип |
|-----------|-------|------------------|
| **Creational** | Механизмы создания объектов | Отделить создание от использования |
| **Structural** | Сборка объектов в более крупные структуры | Композиция вместо наследования |
| **Behavioral** | Алгоритмы и распределение ответственности | Слабая связанность (loose coupling) |

---

## Структура описания паттерна

GoF ввели формальный шаблон описания --- это не просто "рецепт", а инженерная спецификация:

| Секция | Что описывает | Зачем читать |
|--------|---------------|--------------|
| **Intent** | Зачем паттерн существует | Понять, решает ли он вашу проблему |
| **Motivation** | Конкретный сценарий | Увидеть паттерн в контексте |
| **Applicability** | Когда применять | Избежать cargo cult |
| **Participants** | Роли компонентов | Не пропустить ключевую часть |
| **Consequences** | Trade-offs | Осознанный выбор |

> "Design patterns should not be applied indiscriminately. Often they achieve flexibility and variability by introducing additional levels of indirection, and that can complicate a design and/or cost you some performance." --- GoF Book

---

## Kotlin делает паттерны ненужными

Многие GoF-паттерны были решением ограничений C++ и Java. Kotlin (как и другие современные языки) встраивает эти решения прямо в синтаксис:

| GoF-паттерн | Kotlin-замена | Почему паттерн не нужен |
|-------------|---------------|------------------------|
| **Singleton** | `object` | Потокобезопасный singleton в одну строку |
| **Builder** | Named/default parameters | `User(name = "Alice", age = 30)` --- нет нужды в fluent builder |
| **Strategy** | Higher-order functions | `fun sort(comparator: (Int, Int) -> Int)` --- лямбда вместо класса |
| **Iterator** | `Sequence`, extension functions | `list.filter { }.map { }` --- итерирование встроено |
| **Decorator** | Extension functions, delegation `by` | `fun String.encrypt()` добавляет поведение без обёрток |
| **Prototype** | `data class` + `copy()` | `user.copy(name = "Bob")` --- клонирование из коробки |
| **Observer** | `Flow`, `StateFlow`, `LiveData` | Реактивные потоки заменяют ручное управление подписками |
| **Template Method** | Higher-order functions | Передать лямбду вместо наследования и override |
| **Command** | Лямбда / `fun interface` | `val command: () -> Unit = { save() }` |
| **Factory Method** | `companion object` | `User.fromEmail("a@b.com")` --- без отдельного класса |

> [!info] Kotlin-нюанс
> Питер Норвиг ещё в 1996 году показал, что 16 из 23 GoF-паттернов становятся тривиальными или ненужными в языках с first-class функциями. Kotlin --- именно такой язык: лямбды, extension functions и delegation `by` убирают большинство boilerplate-кода.

### Пример: Strategy --- класс vs лямбда

```kotlin
// Java-стиль: Strategy через интерфейс и классы
interface DiscountStrategy {
    fun apply(price: Double): Double
}

class PremiumDiscount : DiscountStrategy {
    override fun apply(price: Double) = price * 0.9
}

class RegularDiscount : DiscountStrategy {
    override fun apply(price: Double) = price * 0.95
}

fun calculate(price: Double, strategy: DiscountStrategy) =
    strategy.apply(price)

val result = calculate(100.0, PremiumDiscount()) // 3 класса, 15 строк

// ─── Kotlin-идиоматичный стиль ─────────────────────────────
// Strategy = просто лямбда. Никаких классов.
fun calculate(price: Double, discount: (Double) -> Double) =
    discount(price)

val result = calculate(100.0) { it * 0.9 } // 2 строки, тот же результат
```

### Пример: Builder --- класс vs named parameters

```kotlin
// Java-стиль Builder
class HttpRequest private constructor(
    val url: String,
    val method: String,
    val headers: Map<String, String>,
    val timeout: Int
) {
    class Builder {
        private var url: String = ""
        private var method: String = "GET"
        private var headers: MutableMap<String, String> = mutableMapOf()
        private var timeout: Int = 30_000

        fun url(url: String) = apply { this.url = url }
        fun method(method: String) = apply { this.method = method }
        fun header(key: String, value: String) = apply { headers[key] = value }
        fun timeout(timeout: Int) = apply { this.timeout = timeout }
        fun build() = HttpRequest(url, method, headers, timeout)
    }
}

val request = HttpRequest.Builder()
    .url("https://api.example.com")
    .method("POST")
    .header("Authorization", "Bearer token")
    .timeout(5_000)
    .build()

// ─── Kotlin-идиоматичный стиль ─────────────────────────────
// Named + default parameters. Builder не нужен.
data class HttpRequest(
    val url: String,
    val method: String = "GET",
    val headers: Map<String, String> = emptyMap(),
    val timeout: Int = 30_000
)

val request = HttpRequest(
    url = "https://api.example.com",
    method = "POST",
    headers = mapOf("Authorization" to "Bearer token"),
    timeout = 5_000
)
```

---

## Какие паттерны по-прежнему актуальны

Не все паттерны стали ненужными. Часть из них решает архитектурные задачи, которые не зависят от языка:

| Паттерн | Почему актуален | Kotlin-особенность |
|---------|-----------------|-------------------|
| **Factory** | Создание объектов с логикой выбора типа | `sealed class` + `companion object` |
| **Adapter** | Интеграция несовместимых API | Extension functions |
| **Decorator** | Цепочка обработки (middleware) | Delegation `by` |
| **Observer** | Event-driven архитектура | `Flow`, `Channel` |
| **State** | Конечные автоматы | `sealed class` + `when` |
| **Facade** | Упрощение сложного API | Top-level functions, DSL |
| **Proxy** | Кэширование, логирование, доступ | Delegated properties |

---

## Когда паттерны помогают, а когда вредят

### Паттерн помогает, если:

1. **Есть реальная проблема** --- код дублируется, связанность растёт, изменения каскадом ломают систему
2. **Паттерн решает именно эту проблему** --- не "похожую", а конкретно эту
3. **Код с паттерном проще**, чем без него (не всегда!)
4. **Команда понимает паттерн** --- иначе код станет загадкой

### Паттерн вредит, если:

1. **Применяется "на всякий случай"** --- YAGNI (You Ain't Gonna Need It)
2. **Решает несуществующую проблему** --- Factory для единственного типа
3. **Усложняет простой код** --- 5 классов вместо одной функции
4. **Используется ради собеседования** --- "покажу что знаю паттерны"

```
Правило трёх:
Если проблема встретилась 1 раз → решай напрямую
Если 2 раза → задумайся
Если 3 раза → вероятно, нужен паттерн

Преждевременная абстракция хуже дублирования.
```

---

## Антипаттерны использования паттернов

### 1. Cargo Cult Programming

Применение паттерна "потому что так правильно", без понимания зачем:

```kotlin
// Cargo Cult: Factory для одного типа
class UserFactory {
    fun create(name: String) = User(name) // Зачем?
}

// Достаточно:
val user = User(name)
```

### 2. Golden Hammer

Один любимый паттерн для всех задач:

```kotlin
// "Всё решаю через Observer!"
// Результат: 47 подписок, никто не знает
// откуда прилетает событие, отладка невозможна
```

### 3. Pattern-itis (Паттерн-мания)

```
God Object Singleton          → Singleton на 2000 строк
Factory Factory Factory       → Фабрика создаёт фабрику, создающую фабрику
AbstractSingletonProxyFactoryBean → Реальный класс в Spring
```

### 4. Premature Abstraction

```kotlin
// Проект на 3 месяца, 1 разработчик:
// "Давай сразу заложим Factory + Strategy + Observer + DI!"
// Через месяц: 40 файлов, 200 строк бизнес-логики

// Лучше: напиши просто, отрефактори когда понадобится
```

---

## Гайд по выбору паттерна

```
ПРОБЛЕМА                               ПАТТЕРН
───────────────────────────────────────────────────────────────
Тип объекта определяется в runtime   → Factory Method
Семейство связанных объектов         → Abstract Factory
Много параметров при создании        → Builder (или named params)
Один экземпляр на приложение         → Singleton (object / DI scope)
Клонирование объекта                 → Prototype (copy())

Несовместимый API                    → Adapter
Добавить поведение динамически       → Decorator
Упростить сложный интерфейс          → Facade
Одинаковая работа с частью и целым   → Composite
Контроль доступа к объекту           → Proxy

Выбор алгоритма в runtime            → Strategy (или лямбда)
Реакция на событие                   → Observer (или Flow)
Объект с состояниями и переходами    → State (sealed class)
Отмена операций                      → Command + Memento
Обход коллекции                      → Iterator (Sequence)
───────────────────────────────────────────────────────────────
```

> [!info] Kotlin-нюанс
> Перед тем как реализовывать GoF-паттерн, проверьте: нет ли в Kotlin встроенной фичи, которая решает задачу? `object`, `sealed class`, `by`, extension functions, higher-order functions, `lazy {}` и корутины покрывают большинство сценариев без дополнительных абстракций.

---

## Паттерны в пакете

Этот пакет содержит детальные разборы ключевых паттернов с Kotlin-примерами:

| Файл | Паттерн | Категория |
|------|---------|-----------|
| [[singleton-pattern]] | Singleton | Creational |
| [[factory-pattern]] | Factory Method + Abstract Factory | Creational |
| [[builder-pattern]] | Builder | Creational |
| [[strategy-pattern]] | Strategy | Behavioral |
| [[observer-pattern]] | Observer | Behavioral |
| [[decorator-pattern]] | Decorator | Structural |
| [[adapter-pattern]] | Adapter | Structural |
| [[state-pattern]] | State | Behavioral |

---

## Проверь себя

> [!question]- Какие три категории GoF-паттернов существуют и за что отвечает каждая?
> **Creational** (порождающие) --- механизмы создания объектов: Factory, Builder, Singleton, Prototype. **Structural** (структурные) --- сборка объектов в крупные структуры: Adapter, Decorator, Facade, Composite, Proxy. **Behavioral** (поведенческие) --- алгоритмы и коммуникация объектов: Strategy, Observer, State, Command, Iterator.

> [!question]- Почему Kotlin делает многие GoF-паттерны ненужными? Приведите 3 примера.
> Kotlin встраивает решения в синтаксис: (1) **Singleton** заменяется `object` --- потокобезопасный singleton в одну строку. (2) **Builder** заменяется named/default parameters --- `User(name = "Alice", age = 30)`. (3) **Strategy** заменяется higher-order functions --- `fun sort(comparator: (Int, Int) -> Int)`, лямбда вместо класса. Также: Iterator -> Sequence, Prototype -> `data class.copy()`, Decorator -> delegation `by`.

> [!question]- Что такое "правило трёх" при выборе паттерна?
> Если проблема встретилась 1 раз --- решай напрямую. 2 раза --- задумайся. 3 раза --- вероятно, нужен паттерн. Преждевременная абстракция хуже дублирования. Паттерн оправдан когда решает **реальную** повторяющуюся проблему, а не гипотетическую.

> [!question]- Назовите три антипаттерна использования паттернов.
> (1) **Cargo Cult** --- применение без понимания зачем (Factory для `new User(name)`). (2) **Golden Hammer** --- один паттерн для всех задач ("всё решаю через Observer"). (3) **Pattern-itis** --- чрезмерное наслаивание абстракций (Factory Factory Factory, AbstractSingletonProxyFactoryBean).

---

## Ключевые карточки

Какие три категории GoF-паттернов и сколько паттернов в каждой?
?
Creational (5): Singleton, Factory Method, Abstract Factory, Builder, Prototype. Structural (7): Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy. Behavioral (11): Strategy, Observer, Command, State, Iterator, Template Method, Mediator, Memento, Visitor, Chain of Responsibility, Interpreter. Итого 23 паттерна.

Откуда появились GoF-паттерны?
?
Вдохновлены книгой архитектора Кристофера Александра "A Pattern Language" (1977) о повторяющихся решениях в строительстве. В 1994 году Gamma, Helm, Johnson, Vlissides ("Банда четырёх") перенесли идею в программирование, выпустив "Design Patterns". Они не изобретали паттерны --- а каталогизировали решения, которые уже работали в индустрии.

Какие GoF-паттерны Kotlin заменяет фичами языка?
?
Singleton -> `object`, Builder -> named/default params, Strategy -> лямбды и HOF, Iterator -> `Sequence` + extensions, Decorator -> delegation `by` + extensions, Prototype -> `data class.copy()`, Observer -> `Flow`/`StateFlow`, Template Method -> HOF, Command -> лямбды / `fun interface`, Factory Method -> `companion object`.

Что такое Cargo Cult Programming в контексте паттернов?
?
Применение паттерна "потому что так правильно" без понимания проблемы, которую он решает. Пример: создание `UserFactory` с единственным методом `create(name) = User(name)`, который просто оборачивает конструктор. Признак: если код проще без паттерна --- паттерн не нужен.

Когда паттерн оправдан, а когда нет?
?
Оправдан: есть реальная повторяющаяся проблема, паттерн решает именно её, код с паттерном проще. Не оправдан: проблема гипотетическая (YAGNI), паттерн усложняет простой код, используется ради демонстрации знаний. Правило трёх: 1 раз --- напрямую, 2 раза --- задумайся, 3 раза --- вероятно нужен паттерн.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Creational | [[singleton-pattern]] | `object`, когда singleton оправдан, а когда --- антипаттерн |
| Creational | [[factory-pattern]] | `companion object`, `sealed class`, `operator fun invoke()` |
| Creational | [[builder-pattern]] | DSL-builders, когда named params недостаточно |
| Behavioral | [[strategy-pattern]] | Лямбды vs классы, HOF в Kotlin |
| Behavioral | [[observer-pattern]] | `Flow`, `StateFlow`, реактивные паттерны |
| Structural | [[decorator-pattern]] | Delegation `by`, extension functions |
| Structural | [[adapter-pattern]] | Extension functions как адаптеры |
| Behavioral | [[state-pattern]] | `sealed class` + `when` для конечных автоматов |
| Фундамент | [[solid-principles]] | SOLID --- теоретическая база, на которой стоят все паттерны |
| Kotlin | [[kotlin-oop]] | Как ООП-фичи Kotlin связаны с паттернами |
| Android | [[android-architecture-patterns]] | Применение паттернов в Android-архитектуре |

---

## Источники

- Gamma E., Helm R., Johnson R., Vlissides J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software* --- оригинальная книга GoF, описавшая 23 паттерна
- Alexander C. (1977). *A Pattern Language: Towns, Buildings, Construction* --- архитектурная книга, вдохновившая GoF
- Moskala M. (2021). *Effective Kotlin* --- Item 30-32: почему в Kotlin factory functions лучше конструкторов и когда паттерны не нужны
- Bloch J. (2018). *Effective Java*, 3rd ed. --- Item 1: Static factory methods; Item 2: Builder pattern
- Nystrom R. (2014). *Game Programming Patterns* --- прагматичный подход к паттернам без dogma
- [Refactoring Guru: Design Patterns](https://refactoring.guru/design-patterns) --- лучший визуальный справочник
- [Norvig P. (1996). Design Patterns in Dynamic Languages](https://norvig.com/design-patterns/) --- 16 из 23 паттернов упрощаются в языках с first-class функциями
- [Have Software Design Patterns Become Obsolete?](https://leakka.com/2024/04/11/have-software-design-patterns-become-obsolete/) --- современная перспектива (2024)
- [GoF Patterns: Still Relevant in 2025?](https://medium.com/@freddy.dordoni/the-gang-of-four-gave-us-23-design-patterns-are-they-still-relevant-in-2025-f2e999c384c0) --- обзор актуальности
- [Kotlin Design Patterns](https://reflectoring.io/kotlin-design-patterns/) --- паттерны в идиоматичном Kotlin

---

*Проверено: 2026-02-19*
