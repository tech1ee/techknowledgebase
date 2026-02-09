---
title: "Type Erasure и Reification: что происходит с типами в runtime"
created: 2026-01-04
modified: 2026-01-04
type: deep-dive
tags: [cs-foundations, type-systems, type-erasure, reified, kotlin, jvm]
related:
  - "[[generics-parametric-polymorphism]]"
  - "[[variance-covariance]]"
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

## Источники

- [Android Developers: Reification of the Erased](https://medium.com/androiddevelopers/reification-of-the-erased-41e246725d2c) — отличное объяснение
- [Baeldung: Type Erasure in Java](https://www.baeldung.com/java-type-erasure) — Java perspective
- [Baeldung: Reified Functions in Kotlin](https://www.baeldung.com/kotlin/reified-functions) — практические примеры
- [Oracle: Type Erasure](https://docs.oracle.com/javase/tutorial/java/generics/erasure.html) — официальная документация

---

*Проверено: 2026-01-09*
