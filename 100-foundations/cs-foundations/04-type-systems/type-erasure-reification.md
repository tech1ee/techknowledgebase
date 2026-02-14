---
title: "Type Erasure и Reification: что происходит с типами в runtime"
created: 2026-01-04
modified: 2026-02-13
type: deep-dive
reading_time: 15
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/cs-foundations
  - type/deep-dive
  - level/advanced
related:
  - "[[generics-parametric-polymorphism]]"
  - "[[variance-covariance]]"
  - "[[bytecode-virtual-machines]]"
prerequisites:
  - "[[generics-parametric-polymorphism]]"
  - "[[bytecode-virtual-machines]]"
---

# Type Erasure и Reification: что происходит с типами в runtime

> **TL;DR:** Type erasure — JVM стирает информацию о generic типах при компиляции. `List<String>` и `List<Int>` в runtime неотличимы. Нельзя: `is T`, `T::class`, `new T()`. Kotlin решает через `inline fun <reified T>`: компилятор инлайнит код и подставляет конкретный тип до erasure. Reified работает только с inline и недоступен из Java.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Generics** | Параметризованные типы | [[generics-parametric-polymorphism]] |
| **Bytecode и JVM** | Как работает JVM | [[bytecode-virtual-machines]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Type Erasure** | Удаление информации о типах при компиляции | Этикетки срываются с коробок на складе |
| **Reification** | Сохранение информации о типах в runtime | Несъёмные этикетки |
| **Inline function** | Функция, чьё тело встраивается в место вызова | Копипаста от компилятора |
| **Reified** | Маркер для сохранения типа в inline функции | "Не срывать этикетку!" |

---

## ПОЧЕМУ существует Type Erasure

### История: Java 5 и backwards compatibility

**2004:** Java добавила generics в версии 5. Но Java существовала с 1995 года — миллионы строк кода уже работали.

**Проблема:**
- Старый код (Java 1.4) не знает о generics
- Новый код (Java 5+) использует generics
- Они должны работать вместе

**Решение:** Type Erasure
- Generics существуют только на уровне **компилятора**
- После компиляции — обычный bytecode без типов
- JVM не изменилась → старый код работает

### Как это работает

```
┌─────────────────────────────────────────────────────────────┐
│                    TYPE ERASURE                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ИСХОДНЫЙ КОД (Kotlin/Java):                               │
│   List<String> names = listOf("Alice", "Bob")               │
│   List<Int> numbers = listOf(1, 2, 3)                       │
│                                                             │
│                    ↓ КОМПИЛЯЦИЯ                             │
│                                                             │
│   BYTECODE (JVM):                                           │
│   List names = listOf("Alice", "Bob")                       │
│   List numbers = listOf(1, 2, 3)                            │
│                                                             │
│   Типы СТЁРТЫ! List<String> = List<Int> = List             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Что делает компилятор

1. **Заменяет type parameters** на bounds (или `Object`)
2. **Вставляет casts** где нужно для type safety
3. **Генерирует bridge methods** для полиморфизма

```kotlin
// Исходный код
class Box<T>(val value: T)
val box: Box<String> = Box("hello")
val s: String = box.value

// После erasure (псевдокод)
class Box(val value: Any)
val box: Box = Box("hello")
val s: String = box.value as String  // Cast добавлен!
```

---

## Ограничения Type Erasure

### Что НЕЛЬЗЯ делать с T

```kotlin
fun <T> demo(value: Any) {
    // ❌ Error: Cannot check for instance of erased type T
    if (value is T) { ... }

    // ❌ Error: Cannot use T as reified type parameter
    val clazz = T::class

    // ❌ Error: Cannot create instance of type parameter
    val instance = T()
}
```

### Почему нельзя

В runtime **T не существует**. JVM не знает, что такое T — это информация была стёрта при компиляции.

```
┌─────────────────────────────────────────────────────────────┐
│                 ПОЧЕМУ НЕЛЬЗЯ is T                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   fun <T> check(value: Any): Boolean {                      │
│       return value is T   // ← Что такое T?                │
│   }                                                         │
│                                                             │
│   check<String>("hello")  // T = String                     │
│   check<Int>("hello")     // T = Int                        │
│                                                             │
│   В RUNTIME:                                                │
│   fun check(value: Any): Boolean {                          │
│       return value is ???  // T стёрт!                     │
│   }                                                         │
│                                                             │
│   JVM не знает, был ли T = String или T = Int              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Перегрузка по generic типу

```kotlin
// ❌ Error: Platform declaration clash
fun process(list: List<String>) { ... }
fun process(list: List<Int>) { ... }

// После erasure обе функции имеют сигнатуру:
// fun process(list: List) { ... }
// Коллизия!
```

---

## Kotlin Reified: решение проблемы

### Как работает reified

**Ключевая идея:** Если компилятор **подставит код функции в место вызова**, он может подставить и **конкретный тип**.

```kotlin
inline fun <reified T> isInstance(value: Any): Boolean {
    return value is T  // Работает!
}

// Вызов:
isInstance<String>("hello")

// Компилятор генерирует (inline подстановка):
"hello" is String  // T заменён на String ДО erasure!
```

### Визуализация

```
┌─────────────────────────────────────────────────────────────┐
│                REIFIED + INLINE                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ОБЪЯВЛЕНИЕ:                                               │
│   inline fun <reified T> isInstance(value: Any): Boolean {  │
│       return value is T                                     │
│   }                                                         │
│                                                             │
│   ВЫЗОВ:                                                    │
│   val result = isInstance<String>("hello")                  │
│                                                             │
│                    ↓ INLINE ПОДСТАНОВКА                     │
│                                                             │
│   val result = "hello" is String  // T → String            │
│                                                             │
│                    ↓ КОМПИЛЯЦИЯ                             │
│                                                             │
│   BYTECODE: instanceof String                               │
│   Никакого erasure — тип уже подставлен!                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Что можно с reified

```kotlin
inline fun <reified T> demo(value: Any) {
    // ✅ Проверка типа
    if (value is T) { println("It's T!") }

    // ✅ Получить класс
    val clazz = T::class

    // ✅ Получить Java class
    val javaClass = T::class.java

    // ✅ Использовать в when
    when (T::class) {
        String::class -> println("String")
        Int::class -> println("Int")
    }
}
```

---

## Практические примеры

### filterIsInstance

```kotlin
// Стандартная библиотека Kotlin
public inline fun <reified R> Iterable<*>.filterIsInstance(): List<R> {
    return filterIsInstanceTo(ArrayList<R>())
}

// Использование
val mixed: List<Any> = listOf(1, "hello", 2, "world")
val strings: List<String> = mixed.filterIsInstance<String>()
// ["hello", "world"]
```

### JSON Deserialization

```kotlin
// Без reified
fun <T> fromJson(json: String, clazz: Class<T>): T {
    return gson.fromJson(json, clazz)
}
fromJson(json, User::class.java)  // Нужно передавать класс

// С reified
inline fun <reified T> fromJson(json: String): T {
    return gson.fromJson(json, T::class.java)
}
fromJson<User>(json)  // Класс выводится из T
```

### Android Intent Extras

```kotlin
// Без reified
fun <T : Parcelable> Intent.getParcelableExtraCompat(key: String, clazz: Class<T>): T? {
    return if (Build.VERSION.SDK_INT >= 33) {
        getParcelableExtra(key, clazz)
    } else {
        @Suppress("DEPRECATION")
        getParcelableExtra(key)
    }
}

// С reified
inline fun <reified T : Parcelable> Intent.getParcelableExtraCompat(key: String): T? {
    return if (Build.VERSION.SDK_INT >= 33) {
        getParcelableExtra(key, T::class.java)
    } else {
        @Suppress("DEPRECATION")
        getParcelableExtra(key)
    }
}

// Использование
val user = intent.getParcelableExtraCompat<User>("user_key")
```

---

## Ограничения Reified

### Только с inline

```kotlin
// ❌ Error: Cannot use 'reified' without 'inline'
fun <reified T> notInline(): T { ... }

// ✅ OK
inline fun <reified T> isInline(): T { ... }
```

### Недоступен из Java

```kotlin
// Kotlin
inline fun <reified T> kotlinOnly() { ... }

// Java
// ❌ Нельзя вызвать — Java не поддерживает inline
```

### Тип должен быть известен при вызове

```kotlin
inline fun <reified T> create(): T { ... }

fun <U> wrapper(): U {
    // ❌ Error: Cannot use 'U' as reified type parameter
    return create<U>()
}

// U — generic параметр wrapper(), неизвестен при вызове create()
```

---

## Workarounds без Reified

### Передать Class<T>

```kotlin
fun <T> create(clazz: Class<T>): T {
    return clazz.getDeclaredConstructor().newInstance()
}

val user = create(User::class.java)
```

### TypeToken (Gson pattern)

```kotlin
// Анонимный класс сохраняет type info
val type = object : TypeToken<List<User>>() {}.type
val users: List<User> = gson.fromJson(json, type)
```

### Reflection (ограниченно)

```kotlin
// Работает для parameterized types в сигнатурах
class UserRepository : Repository<User, Long>

// Можно получить User через reflection
val typeArg = UserRepository::class.supertypes
    .first().arguments.first().type
```

---

## Подводные камни

### Распространённые ошибки

| Ошибка | Последствие | Решение |
|--------|-------------|---------|
| Забыть inline | Compile error | Добавить inline |
| Вызывать из Java | Недоступно | Предоставить non-inline overload |
| Передать generic T | Compile error | T должен быть конкретным |
| Unchecked cast | Runtime exception | Использовать reified или проверки |

### Мифы и заблуждения

**Миф:** "Reified сохраняет типы в bytecode"
**Реальность:** Reified работает через inline — тип подставляется ДО генерации bytecode.

**Миф:** "Можно использовать reified везде"
**Реальность:** Только в inline функциях, только когда тип известен при вызове.

**Миф:** "Type erasure — баг Java"
**Реальность:** Это design decision для backwards compatibility. Trade-off, не баг.

---

## Куда дальше

**Если здесь впервые:**
→ Попрактикуйся с `inline fun <reified T>`

**Если понял и хочешь глубже:**
→ [[bytecode-virtual-machines]] — как JVM обрабатывает bytecode

**Практическое применение:**
→ KMP: как erasure влияет на interop с платформами

---

## Связь с другими темами

### [[generics-parametric-polymorphism]]
Type erasure — это прямое следствие реализации generics на JVM. Без понимания того, как работают type parameters, upper bounds и generic functions, невозможно осознать, что именно стирается при компиляции и почему. Generics дают теоретический фундамент, а type erasure показывает практические ограничения этого фундамента на конкретной платформе.

### [[variance-covariance]]
Variance и type erasure пересекаются в вопросах runtime-проверок типов. Когда `List<String>` и `List<Int>` неотличимы в runtime, variance constraints (`out`, `in`) становятся единственной гарантией type safety — они работают на уровне компилятора, компенсируя отсутствие runtime-информации. Понимание обоих механизмов необходимо для написания безопасного generic-кода.

### [[bytecode-virtual-machines]]
Type erasure — это архитектурное решение JVM. Понимание того, как JVM обрабатывает bytecode, объясняет, почему erasure был необходим: JVM не различает `Ljava/util/List;` с разными type arguments на уровне bytecode. Знание структуры bytecode помогает понять, как bridge methods и casts вставляются компилятором для обеспечения type safety после стирания типов.

---

## Источники и дальнейшее чтение

- Pierce B. (2002). *Types and Programming Languages (TAPL)*. — теоретическая основа type erasure: erasure semantics и параметричность, объясняющие, почему стирание типов сохраняет корректность
- Bloch J. (2018). *Effective Java*, 3rd ed. — Item 26-33 детально описывают практические последствия type erasure, включая unchecked warnings, type tokens и super type tokens
- Bracha G. (2004). *Generics in the Java Programming Language*. — tutorial от одного из авторов Java Generics, объясняющий design decisions за type erasure
- [Android Developers: Reification of the Erased](https://medium.com/androiddevelopers/reification-of-the-erased-41e246725d2c) — отличное объяснение
- [Oracle: Type Erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html) — официальная документация

---

## Проверь себя

> [!question]- Ты получаешь ClassCastException при касте List<Any> в List<String> на JVM, хотя код компилируется с unchecked cast warning. Почему компилятор не может предотвратить эту ошибку?
> Из-за type erasure: в runtime List<Any> и List<String> — оба просто List. JVM не хранит информацию о generic-параметре. Компилятор выдаёт warning, но не ошибку, потому что технически cast возможен (если list действительно содержит строки). ClassCastException произойдёт позже, при извлечении элемента и попытке использования как String. Это "heap pollution" — generic-контейнер содержит объекты неправильного типа.

> [!question]- Почему Kotlin/Native сохраняет generic-типы в runtime, а JVM — нет? И как это влияет на KMP-код?
> JVM стирает generic-типы для обратной совместимости с pre-generics Java (до 1.5). Kotlin/Native компилирует через LLVM в native binary без ограничений JVM — может сохранять type information. Для KMP: код с `is T` проверками работает на Native, но не на JVM без reified. Кросс-платформенный код должен использовать `inline reified` или передавать KClass<T> параметром для гарантированной работы на всех платформах.

> [!question]- Как inline reified обходит type erasure и какое ограничение это создаёт?
> inline reified встраивает тело функции в каждый call site, подставляя конкретный тип вместо T. В bytecode нет generic-параметра — он заменён конкретным типом (String, Int и т.д.). Ограничение: работает только с inline-функциями, потому что для не-inline функции существует один bytecode для всех вызовов — некуда подставить конкретный тип. Также inline увеличивает размер bytecode при множественных call sites.

---

## Ключевые карточки

Что такое type erasure и почему оно существует на JVM?
?
Type erasure — стирание информации о generic-типах при компиляции. List<Int> становится просто List в bytecode. Причина: обратная совместимость. Java добавила generics в версии 5 (2004), но JVM не могла сломать существующий bytecode pre-generics классов. Решение: сделать generics чисто compile-time механизмом, стирая типы для runtime.

---

Что такое reification и какие языки её поддерживают?
?
Reification — сохранение generic-типов в runtime. C# (.NET) — полная reification (List<int> и List<string> — разные типы в runtime). Kotlin — частичная через inline reified. Java/JVM — type erasure, нет reification. Kotlin/Native — типы сохраняются. Reification позволяет: `is T` проверки, T::class, создание Array<T>.

---

Как работает star projection (*) в Kotlin и зачем нужна?
?
`List<*>` — "List с неизвестным типом". Аналог Java `List<?>`. Нельзя добавлять элементы (тип неизвестен), но можно читать как Any?. Используется когда конкретный тип не важен: fun printSize(list: List<*>) — не зависит от типа элементов. Star projection — безопасная альтернатива raw types.

---

Что такое heap pollution?
?
Heap pollution — ситуация, когда generic-контейнер содержит объекты неправильного типа из-за unchecked casts. Пример: List<String> через unchecked cast содержит Int. Обнаруживается только при извлечении элемента — ClassCastException в неожиданном месте. Возможно из-за type erasure: runtime не проверяет generic-типы при добавлении.

---

Чем отличается подход к generics на JVM, .NET и Kotlin/Native?
?
JVM (Java/Kotlin): type erasure — generics стираются, List<Int> = List в runtime. .NET (C#): full reification — List<int> и List<string> разные типы, разный machine code. Kotlin/Native: типы сохраняются через LLVM, нет ограничений JVM. Для KMP: использовать inline reified для кросс-платформенной совместимости.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[variance-covariance]] | Как variance взаимодействует с type erasure в Kotlin |
| Углубиться | [[bytecode-virtual-machines]] | Понять JVM bytecode, где generics стираются |
| Смежная тема | [[generics-parametric-polymorphism]] | Вернуться к основам generics |
| Обзор | [[cs-foundations-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-02-13*
