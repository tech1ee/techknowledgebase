---
title: "Type Systems: теория и практика систем типов"
created: 2026-01-09
modified: 2026-02-19
type: concept
status: published
confidence: high
tags:
  - programming/types
  - cs-fundamentals/type-theory
  - topic/jvm
  - typescript
  - type/concept
  - level/intermediate
related:
  - "[[generics-parametric-polymorphism]]"
  - "[[variance-covariance]]"
  - "[[type-erasure-reification]]"
  - "[[kotlin-type-system]]"
  - "[[memory-safety-ownership]]"
prerequisites:
  - "[[data-structures-fundamentals]]"
reading_time: 15
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Type Systems: теория и практика систем типов

> **TL;DR:** Система типов — это набор правил, которые присваивают типы программным конструкциям. Статическая типизация ловит ошибки до запуска (Kotlin, TypeScript), динамическая — во время (Python, JavaScript). Сильная типизация запрещает неявные преобразования, слабая — разрешает. Выбор системы типов — это trade-off между безопасностью и гибкостью.

---

## Теоретические основы

> **Система типов** — формальная система, приписывающая типы программным конструкциям для предотвращения определённых классов ошибок на этапе компиляции или выполнения (Pierce, 2002).

### Формальное определение (Pierce, 2002)

> «A type system is a tractable syntactic method for proving the absence of certain program behaviors by classifying phrases according to the kinds of values they compute.»

### Две оси классификации

| | **Статическая** (compile-time) | **Динамическая** (runtime) |
|-|-------------------------------|---------------------------|
| **Сильная** | Kotlin, Rust, Haskell | Python, Ruby |
| **Слабая** | C (implicit casts) | JavaScript, PHP |

### Ключевые теоретические результаты

| Результат | Автор | Значение |
|-----------|-------|----------|
| **Typed λ-calculus** | Church (1940) | Типы предотвращают парадоксы в λ-исчислении |
| **Hindley-Milner** | Hindley (1969), Milner (1978) | Автоматический вывод типов (type inference) |
| **Curry-Howard** | Howard (1969) | Типы = логические утверждения, программы = доказательства |
| **Type soundness** | — | «Well-typed programs don't go wrong» (Milner) |

### Связь с другими CS-foundations

- [[type-systems-fundamentals]] — формальные основы (Church, Hindley-Milner, Curry-Howard)
- [[generics-parametric-polymorphism]] — параметрический полиморфизм (System F)
- [[variance-covariance]] — подтиповой полиморфизм и вариантность
- [[type-erasure-reification]] — реализация generics на JVM

---



### 1. Типы как контейнеры
```
Тип = форма контейнера

Int     → круглое отверстие   ⚫
String  → квадратное отверстие ⬛
Boolean → треугольное         🔺

Попытка засунуть круг в квадрат = ошибка типа
Компилятор = надзиратель, который НЕ ДАЁТ это сделать
```

### 2. Типы как контракты
```
Функция с сигнатурой:
  fun calculateTax(income: Double): Double

Это КОНТРАКТ:
- "Дай мне число (доход)"
- "Верну число (налог)"
- "Если дашь строку — работать НЕ БУДУ"

Контракт проверяется:
- Статически: при компиляции (Kotlin)
- Динамически: при выполнении (Python)
```

### 3. Статическая vs динамическая типизация
```
СТАТИЧЕСКАЯ (Kotlin, Java, TypeScript):
┌─────────────────────────────────────────┐
│  Код → Компилятор → Проверка типов → Бинарник │
│              ↓                         │
│         Ошибка тут!                    │
│     "Нельзя: String + Int"             │
└─────────────────────────────────────────┘
Ошибка ПЕРЕД запуском = дешёво исправить

ДИНАМИЧЕСКАЯ (Python, JavaScript):
┌─────────────────────────────────────────┐
│  Код → Интерпретатор → Выполнение      │
│                            ↓           │
│                    Runtime Error!      │
│              "TypeError: unsupported   │
│               operand type(s)"         │
└─────────────────────────────────────────┘
Ошибка В ПРОДАКШЕНЕ = дорого исправить
```

### 4. Сильная vs слабая типизация
```
СИЛЬНАЯ (Python, Kotlin):
  "5" + 3  →  TypeError! Нельзя складывать строку и число

СЛАБАЯ (JavaScript, PHP):
  "5" + 3  →  "53"   // Неявное преобразование 3 → "3"
  "5" - 3  →  2      // Неявное преобразование "5" → 5

Сильная = предсказуемо, но строже
Слабая = гибко, но неожиданные баги
```

### 5. Типы как документация
```
// БЕЗ типов (что это принимает? что возвращает?):
function process(data) { ... }

// С типами (самодокументирующийся код):
fun process(data: UserRequest): ProcessingResult

Типы = документация, которая ПРОВЕРЯЕТСЯ компилятором
```

---

## Ключевые концепции

### Спектр систем типов

```
         Слабая типизация          Сильная типизация
              ←────────────────────────────→

    JavaScript    PHP    Python    Kotlin    Haskell
         │         │        │         │          │
      Неявные   Частичные  Строгие  Строгие   Очень
    преобразов.  преобр.   проверки + null-   строгие
                                    safety   + чистота

         ←────────────────────────────→
    Динамическая типизация    Статическая типизация

    Python, JS, Ruby         Kotlin, Java, TypeScript,
                             Rust, Haskell
```

### Градации типизации

| Язык | Статическая/Динамическая | Сильная/Слабая | Особенности |
|------|--------------------------|----------------|-------------|
| **Kotlin** | Статическая | Сильная | Null safety, smart casts |
| **TypeScript** | Статическая | Сильная | Structural typing |
| **Java** | Статическая | Сильная | Type erasure для generics |
| **Python** | Динамическая | Сильная | Duck typing, type hints |
| **JavaScript** | Динамическая | Слабая | Coercion rules |
| **Rust** | Статическая | Сильная | Ownership + lifetimes |
| **Haskell** | Статическая | Сильная | Algebraic data types |

### Nominal vs Structural Typing

```kotlin
// NOMINAL TYPING (Kotlin, Java)
// Типы совместимы, если имеют ОДИНАКОВОЕ ИМЯ

class Dog { fun bark() {} }
class Robot { fun bark() {} }

fun makeNoise(dog: Dog) { dog.bark() }

val robot = Robot()
makeNoise(robot)  // ❌ ОШИБКА: Robot ≠ Dog
                  // Несмотря на одинаковые методы!
```

```typescript
// STRUCTURAL TYPING (TypeScript, Go interfaces)
// Типы совместимы, если имеют ОДИНАКОВУЮ СТРУКТУРУ

interface Barker { bark(): void }

class Dog { bark() { console.log("Woof") } }
class Robot { bark() { console.log("Beep") } }

function makeNoise(barker: Barker) { barker.bark() }

makeNoise(new Dog())    // ✅ OK
makeNoise(new Robot())  // ✅ OK — структура совпадает
```

### Type Inference (вывод типов)

```kotlin
// Явное указание типа:
val name: String = "Alice"

// Вывод типа (компилятор сам понимает):
val name = "Alice"  // Тип: String (выведен)

// Kotlin умеет выводить сложные типы:
val users = listOf(
    User("Alice", 25),
    User("Bob", 30)
)
// Тип: List<User> (выведен автоматически)

// Smart casts — ещё круче:
fun process(obj: Any) {
    if (obj is String) {
        // Компилятор ЗНАЕТ, что obj — String
        println(obj.length)  // Без явного cast!
    }
}
```

---

## Частые ошибки: 6 типичных проблем

### ❌ Ошибка 1: Игнорирование null safety

**Симптом:** `NullPointerException` в runtime

```kotlin
// ПЛОХО:
fun getUser(id: Int): User? {
    return database.find(id)  // Может вернуть null
}

val user = getUser(1)
println(user.name)  // ❌ Потенциальный NPE!

// ХОРОШО:
val user = getUser(1)
println(user?.name ?: "Unknown")  // ✅ Safe call + elvis
// Или:
user?.let { println(it.name) }    // ✅ Scope function
```

**Решение:** В Kotlin всегда используй `?` для nullable типов и safe calls.

---

### ❌ Ошибка 2: Type erasure сюрпризы

**Симптом:** `Cannot check for instance of erased type`

```kotlin
// ПЛОХО:
fun <T> processList(list: List<T>) {
    if (list is List<String>) {  // ❌ Ошибка компиляции!
        // Type erasure: в runtime нет информации о T
    }
}

// ХОРОШО — reified types:
inline fun <reified T> processList(list: List<*>) {
    val strings = list.filterIsInstance<T>()  // ✅ Работает
}
```

**Решение:** Используй `reified` с `inline` функциями для сохранения информации о типе.

---

### ❌ Ошибка 3: Злоупотребление Any/Object

**Симптом:** Потеря type safety, много cast-ов

```kotlin
// ПЛОХО:
fun process(data: Any): Any {
    return when (data) {
        is String -> data.uppercase()
        is Int -> data * 2
        else -> data
    }
}
val result = process("hello") as String  // Опасный cast!

// ХОРОШО — sealed class:
sealed class Input {
    data class Text(val value: String) : Input()
    data class Number(val value: Int) : Input()
}

fun process(input: Input): String = when (input) {
    is Input.Text -> input.value.uppercase()
    is Input.Number -> (input.value * 2).toString()
}  // ✅ Exhaustive, type-safe
```

**Решение:** Используй sealed classes вместо Any для закрытого набора типов.

---

### ❌ Ошибка 4: Неправильное понимание variance

**Симптом:** `Type mismatch: required List<Animal>, found List<Dog>`

```kotlin
// ПРОБЛЕМА:
open class Animal
class Dog : Animal()

fun feedAnimals(animals: MutableList<Animal>) {
    animals.add(Animal())  // Добавляем просто Animal
}

val dogs: MutableList<Dog> = mutableListOf(Dog())
feedAnimals(dogs)  // ❌ Ошибка! Почему?
// Потому что в список собак добавится НЕ собака!

// РЕШЕНИЕ — out variance (только чтение):
fun feedAnimals(animals: List<Animal>) {  // List неизменяемый
    animals.forEach { it.eat() }  // ✅ Только читаем
}
feedAnimals(dogs)  // ✅ Теперь работает!
```

**Решение:** Понимай разницу между `in` (contravariance), `out` (covariance) и invariance.

---

### ❌ Ошибка 5: Platform types в Kotlin/Java interop

**Симптом:** Неожиданные NPE при вызове Java кода

```kotlin
// Java код:
public class JavaClass {
    public String getName() { return null; }  // Может быть null!
}

// Kotlin код:
val name = JavaClass().name  // Тип: String! (platform type)
println(name.length)  // ❌ NPE в runtime!

// РЕШЕНИЕ — явная аннотация или проверка:
val name: String? = JavaClass().name  // ✅ Явно nullable
println(name?.length)
```

**Решение:** При работе с Java кодом явно указывай nullability.

---

### ❌ Ошибка 6: Неправильное использование generics

**Симптом:** Сложный нечитаемый код с множеством type параметров

```kotlin
// ПЛОХО — переусложнённые generics:
fun <T, R, E : Exception> process(
    input: T,
    transformer: (T) -> R,
    errorHandler: (E) -> R
): R where T : Comparable<T>, R : Serializable {
    // ...слишком сложно
}

// ХОРОШО — простой интерфейс:
interface Processor<T, R> {
    fun process(input: T): Result<R>
}

// Или typealias для читаемости:
typealias Transform<T, R> = (T) -> R
```

**Решение:** Если generics становятся сложными — упрости через интерфейсы или typealias.

---

## Ментальные модели: 5 способов думать о типах

### 1. Типы как множества значений

```
Int    = {..., -2, -1, 0, 1, 2, ...}
Boolean = {true, false}
String  = {"", "a", "ab", "abc", ...}  // бесконечное множество
Unit    = {Unit}                       // одно значение
Nothing = {}                           // пустое множество

Union types (TypeScript):
  string | number = все строки ∪ все числа

Intersection types:
  A & B = пересечение множеств A и B
```

### 2. Типы как контракты

```
Функция с типами — это контракт:

fun divide(a: Int, b: Int): Double

Контракт гарантирует:
- Входы: два целых числа
- Выход: число с плавающей точкой
- Если контракт нарушен — компилятор не пропустит

Stronger types = stronger contracts = fewer bugs
```

### 3. Иерархия типов Kotlin

```
                    Any
                     │
        ┌────────────┼────────────┐
        │            │            │
      Number       String      Boolean
        │
   ┌────┼────┐
   │    │    │
  Int  Long Double

                  Any?
                   │
        ┌──────────┼──────────┐
        │          │          │
       Any       Nothing?    ...
                   │
                Nothing

Nothing — подтип ВСЕХ типов (bottom type)
Any — супертип всех non-null типов
Any? — супертип ВСЕХ типов
```

### 4. Thinking in Types

```
Вместо:
  "Что делает эта функция?"

Думай:
  "Какие типы входят? Какие выходят?"

Пример:
  fun ??? : List<A> -> (A -> B) -> List<B>

  Единственная разумная реализация: map!

  Тип ОПРЕДЕЛЯЕТ поведение (parametricity)
```

### 5. Type-Driven Development

```
1. Сначала определи типы (контракт)
2. Потом имплементируй

// Шаг 1: Типы
sealed class PaymentResult {
    data class Success(val transactionId: String) : PaymentResult()
    data class Failure(val error: PaymentError) : PaymentResult()
}

enum class PaymentError {
    INSUFFICIENT_FUNDS,
    CARD_DECLINED,
    NETWORK_ERROR
}

// Шаг 2: Имплементация (типы направляют!)
fun processPayment(card: Card, amount: Money): PaymentResult {
    // Компилятор заставит обработать все случаи
}
```

---

## Практические рекомендации

### Выбор языка по типизации

| Сценарий | Рекомендация | Почему |
|----------|--------------|--------|
| **Большой проект, команда** | Статическая (Kotlin, TypeScript) | Типы = документация, рефакторинг безопасен |
| **Быстрый прототип** | Динамическая (Python) | Меньше boilerplate |
| **Критичная безопасность** | Rust, Haskell | Сильные гарантии на уровне типов |
| **Android** | Kotlin | Null safety спасает от 70% NPE |
| **Web Frontend** | TypeScript | Ловит ошибки до runtime |

### Best practices

```kotlin
// 1. Используй null safety на максимум
val name: String = getName() ?: throw IllegalStateException()

// 2. Sealed classes для закрытых иерархий
sealed class State { ... }

// 3. Typealias для читаемости
typealias UserId = String
typealias Email = String

// 4. Inline classes для type safety без overhead
@JvmInline value class UserId(val value: String)
@JvmInline value class OrderId(val value: String)

fun getUser(id: UserId): User  // Нельзя перепутать с OrderId!

// 5. Extension functions вместо utility classes
fun String.isValidEmail(): Boolean = this.contains("@")
```

---

## Числа, которые нужно знать

| Метрика | Значение | Источник |
|---------|----------|----------|
| NPE-related crashes в Android | 70% можно предотвратить с null safety | Google |
| Bugs от type errors | ~15% всех багов в динамических языках | Microsoft Research |
| Время на отладку type errors | В 2x меньше со статической типизацией | Airbnb (TypeScript migration) |
| TypeScript adoption | 78% JS проектов переходят на TS | State of JS 2024 |

## Связи

- [[generics-parametric-polymorphism]] — параметрический полиморфизм
- [[variance-covariance]] — ковариантность и контравариантность
- [[type-erasure-reification]] — стирание типов и reified
- [[kotlin-type-system]] — система типов Kotlin
- [[memory-safety-ownership]] — безопасность памяти через типы (Rust)
- [[functional-programming]] — типы в функциональном программировании

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Kotlin Type System](https://kotlinlang.org/docs/null-safety.html) | Docs | Null safety, smart casts |
| 2 | [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/) | Docs | Structural typing |
| 3 | [Types and Programming Languages (Pierce)](https://www.cis.upenn.edu/~bcpierce/tapl/) | Book | Теория типов |
| 4 | [Effective Kotlin — Type System](https://kt.academy/book/effectivekotlin) | Book | Практические паттерны |

---

---

## Проверь себя

> [!question]- Почему Python считается сильно типизированным, хотя он динамический? Чем "сильная" отличается от "статической"?
> Это два ортогональных измерения. Статическая/динамическая — КОГДА проверяются типы (при компиляции vs в runtime). Сильная/слабая — РАЗРЕШЕНЫ ЛИ неявные преобразования. Python динамический (проверки в runtime), но сильный: `"5" + 3` вызовет TypeError, а не неявную конвертацию. JavaScript динамический и слабый: `"5" + 3 = "53"`.

> [!question]- Почему `List<Dog>` можно передать в `fun feedAnimals(animals: List<Animal>)`, но нельзя в `fun feedAnimals(animals: MutableList<Animal>)`?
> List в Kotlin ковариантен (out) — только для чтения. Если передать List<Dog> как List<Animal>, из него можно безопасно читать Animal. MutableList инвариантен — поддерживает запись. Если бы MutableList<Dog> принимался как MutableList<Animal>, можно было бы добавить Cat в список собак, что нарушило бы type safety.

> [!question]- Сценарий: вы интегрируете Kotlin-код с Java-библиотекой, которая возвращает `String` без аннотаций. Какие проблемы могут возникнуть?
> Java-метод без @Nullable/@NotNull вернёт platform type (String!). Kotlin не знает, nullable он или нет. Если присвоить результат в `val name: String` (non-null) и Java вернёт null — NPE в runtime. Решение: явно указывать `val name: String? = javaMethod()` или добавить @Nullable аннотации на стороне Java.

> [!question]- Что такое nominal vs structural typing и почему TypeScript использует structural, а Kotlin — nominal?
> Nominal: типы совместимы по имени (Dog и Robot с одинаковыми методами несовместимы). Structural: совместимы по структуре (если у Robot есть bark(), он подходит как Barker). TypeScript — structural, потому что работает поверх JavaScript без классов-в-рантайме. Kotlin — nominal, потому что JVM использует именованные типы с metadata.

---

## Ключевые карточки

Чем статическая типизация отличается от динамической?
?
Статическая проверяет типы при компиляции (Kotlin, Java, TypeScript) — ошибки обнаруживаются до запуска. Динамическая проверяет в runtime (Python, JavaScript) — ошибки возникают при выполнении. Статическая = дешевле исправлять, динамическая = меньше boilerplate.

Что такое type inference?
?
Способность компилятора автоматически выводить типы без явного указания. В Kotlin: `val name = "Alice"` — компилятор выводит тип String. Уменьшает verbosity при сохранении type safety.

Что такое Nothing в Kotlin и зачем он нужен?
?
Nothing — bottom type, подтип ВСЕХ типов, с пустым множеством значений (ни одного экземпляра). Используется для функций, которые никогда не возвращают значение (throw, бесконечный цикл). Позволяет type-safe выражения: `val x: String = error("fail")` — компилируется, т.к. Nothing подтип String.

Чем отличается type erasure от reified generics?
?
Type erasure: информация о generic-параметре стирается в runtime (Java, Kotlin). `List<String>` и `List<Int>` неразличимы. Reified (Kotlin inline fun): информация сохраняется в runtime, можно делать `is T` проверки. Работает только с inline-функциями.

Что такое variance (in/out/invariant) в Kotlin?
?
Out (covariance): только для чтения, `List<Dog>` подтип `List<Animal>`. In (contravariance): только для записи, `Comparable<Animal>` подтип `Comparable<Dog>`. Invariant: ни то ни другое, `MutableList<Dog>` НЕ подтип `MutableList<Animal>`.

Какие преимущества даёт inline class (value class) в Kotlin?
?
Type safety без runtime overhead: `@JvmInline value class UserId(val value: String)` и `OrderId(val value: String)` — разные типы на уровне компиляции, но в runtime это просто String. Невозможно случайно передать OrderId вместо UserId.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[generics-parametric-polymorphism]] | Углубление в generics и параметрический полиморфизм |
| Углубиться | [[variance-covariance]] | Детальное объяснение ковариантности и контравариантности |
| Смежная тема | [[memory-safety-ownership]] | Как Rust использует типы для гарантий безопасности памяти |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

*Проверено: 2026-01-09*

---

[[programming-overview|← Programming Overview]] | [[generics-parametric-polymorphism|Generics →]]