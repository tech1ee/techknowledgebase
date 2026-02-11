---
title: "Kotlin: Основы языка"
created: 2025-11-25
modified: 2026-01-03
tags:
  - topic/jvm
  - basics
  - null-safety
  - type/concept
  - level/beginner
aliases:
  - Kotlin Basics
  - Основы Kotlin
status: published
related:
  - "[[kotlin-oop]]"
  - "[[kotlin-functional]]"
  - "[[kmp-getting-started]]"
---

# Kotlin: Основы языка

> **TL;DR:** Kotlin — современный JVM-язык от JetBrains, официальный язык Android с 2019. Null-safety на уровне типов: `String` ≠ `String?`, NullPointerException ловится при компиляции. Data class заменяет 50 строк Java boilerplate. `when` exhaustive для sealed classes. 70% топ-1000 Android-приложений на Kotlin, Google Docs iOS переписан на Kotlin Multiplatform.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Основы программирования | Переменные, функции, классы | Любой курс по Java/JavaScript |
| Как работает JVM | Понимать bytecode, interop с Java | [[jvm-basics-history]] |
| ООП концепции | Классы, наследование, интерфейсы | [[kotlin-oop]] |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Null-safety** | Защита от NullPointerException на уровне компиляции | Замок на двери — компилятор не даст войти без ключа (проверки) |
| **Type inference** | Автоматический вывод типа компилятором | Бариста понимает "как обычно" без уточнения |
| **Smart cast** | Автоматическое приведение типа после проверки | Охранник помнит ваше лицо после первой проверки |
| **Data class** | Класс для хранения данных с auto-generated методами | Конверт с обратным адресом — всё что нужно уже есть |
| **Extension function** | Добавление метода к существующему классу без наследования | Переводчик между вами и иностранцем |
| **Sealed class** | Ограниченный набор подтипов, известных в compile-time | Меню в ресторане — только фиксированные варианты |
| **Expression** | Конструкция, возвращающая значение (`if`, `when`) | Вопрос, на который всегда есть ответ |
| **Elvis operator `?:`** | Возврат значения по умолчанию при null | План Б — если основной не сработал |

---

Kotlin — язык для JVM от JetBrains, официальный язык Android-разработки с 2019 года. Null-safety на уровне системы типов: `String` никогда не null, `String?` — может быть, и компилятор заставляет обрабатывать оба случая. NullPointerException ловится при компиляции, не в runtime.

Представьте аптечный склад, где каждое лекарство имеет ячейку. В Java любая ячейка может быть пустой — и вы узнаете об этом, только когда протянете руку и ничего не найдёте. В Kotlin ячейки двух видов: обычные (гарантированно с лекарством) и помеченные знаком «?» (может быть пустой). Прежде чем взять что-то из помеченной ячейки, вы обязаны проверить — иначе система просто не позволит вам протянуть руку. Это и есть null-safety на уровне типов.

Другая полезная аналогия — ресторанное меню. В Java `switch` — это фиксированное меню: только определённые категории блюд (примитивы, enum, строки). В Kotlin `when` — это меню без ограничений: можно выбирать по типу блюда (`is`), по диапазону цен (`in 10..50`), по нескольким критериям одновременно — и если меню фиксировано (sealed class), официант (компилятор) проверит, что вы рассмотрели все варианты.

Data class заменяет ~50 строк Java boilerplate (getters, setters, equals, hashCode, toString). `val` вместо `final String`, `when` вместо ограниченного switch с exhaustiveness checking. Extension functions позволяют добавлять методы к существующим классам без наследования. Полная интероперабельность с Java: можно вызывать Kotlin из Java и наоборот.

---

## История Kotlin: от проекта JetBrains до стандарта Android

### Почему JetBrains создали Kotlin?

JetBrains — компания, создавшая IntelliJ IDEA, PyCharm, WebStorm и другие IDE. Они писали эти продукты на Java и столкнулись с её ограничениями: многословность, отсутствие null-safety, устаревший синтаксис.

**Почему не Scala?** Дмитрий Жемеров (JetBrains lead) говорил, что Scala имела нужные фичи, но критически медленно компилировалась. Для IDE-разработки это было неприемлемо.

**Цели Kotlin:**
- Компилироваться так же быстро, как Java
- Быть проще Scala, но мощнее Java
- 100% совместимость с Java — использовать существующие библиотеки
- Постепенная миграция — можно переписывать по одному файлу

### Хронология

```
┌─────────────────────────────────────────────────────────────────┐
│                    ИСТОРИЯ KOTLIN                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  2010: JetBrains начинает разработку "Project Kotlin"           │
│  ─────────────────────────────────────────────────              │
│  Название — от острова Котлин в Финском заливе                  │
│  (как Java названа в честь острова Ява)                         │
│                                                                 │
│  Июль 2011: Публичный анонс                                     │
│  ─────────────────────────────                                  │
│  JetBrains представляет Kotlin как "pragmatic" альтернативу     │
│  Java для JVM                                                   │
│                                                                 │
│  Февраль 2012: Open Source                                      │
│  ────────────────────────────                                   │
│  Код открыт под лицензией Apache 2.0                            │
│                                                                 │
│  Февраль 2016: Kotlin 1.0                                       │
│  ────────────────────────────                                   │
│  Первый стабильный релиз                                        │
│  JetBrains обещает backward compatibility                       │
│                                                                 │
│  Май 2017: Google I/O — официальная поддержка Android           │
│  ──────────────────────────────────────────────────             │
│  Kotlin становится третьим официальным языком Android           │
│  (после Java и C++)                                             │
│  Android Studio 3.0 включает Kotlin "из коробки"                │
│                                                                 │
│  Ноябрь 2017: Kotlin 1.2 + Multiplatform (experimental)         │
│  ──────────────────────────────────────────────────             │
│  Первая KotlinConf в Сан-Франциско                              │
│                                                                 │
│  2018: Самый быстрорастущий язык на GitHub                      │
│  ──────────────────────────────────────────                     │
│  +260% разработчиков за год                                     │
│  Google выпускает Android KTX                                   │
│                                                                 │
│  Май 2019: Google объявляет "Kotlin-first"                      │
│  ──────────────────────────────────────────                     │
│  Kotlin становится ПРЕДПОЧТИТЕЛЬНЫМ языком для Android          │
│  Новые API и примеры — сначала на Kotlin                        │
│                                                                 │
│  2020-2024: Доминирование в Android                             │
│  ──────────────────────────────────                             │
│  70% топ-1000 приложений в Play Store на Kotlin                 │
│  60 приложений Google (Maps, Drive) на Kotlin                   │
│  Kotlin Multiplatform становится Stable (2023)                  │
│  Compose Multiplatform для iOS (2024)                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему Google выбрал Kotlin?

1. **Java lawsuits** — Oracle судился с Google из-за использования Java API в Android. Kotlin — независимый язык.

2. **Современность** — Java медленно развивалась (Java 8 вышла в 2014, Android долго не поддерживал её полностью). Kotlin имел все современные фичи сразу.

3. **Популярность среди разработчиков** — к 2017 году многие Android-разработчики уже использовали Kotlin неофициально.

4. **Безопасность** — null-safety сокращает количество crashes в production.

---

## Ключевые отличия от Java

| Kotlin | Java |
|--------|------|
| `val name = "John"` | `final String name = "John";` |
| `var count = 0` | `int count = 0;` |
| `String?` (nullable) | Любой тип может быть null |
| `"Hello, $name"` | `"Hello, " + name` |
| `when (x) { ... }` | `switch (x) { ... }` |
| Нет checked exceptions | `throws IOException` везде |

---

## Переменные

### val vs var

```kotlin
// val — read-only reference (нельзя переприсвоить)
val name: String = "John"
name = "Jane"  // ❌ Ошибка компиляции

// var — mutable reference (можно переприсвоить)
var age: Int = 30
age = 31  // ✅ OK

// Type inference — компилятор сам определяет тип
val city = "New York"  // Компилятор выводит String
val count = 42         // Компилятор выводит Int
```

**Важное уточнение:** `val` ≠ immutable. Официальная документация Kotlin называет `val` "read-only", не "immutable". Разница критична:

```kotlin
val list = mutableListOf(1, 2, 3)
list.add(4)  // ✅ OK! Ссылка та же, содержимое изменилось
list = mutableListOf(5, 6)  // ❌ Ошибка: нельзя переприсвоить

// Для настоящей immutability нужны immutable коллекции:
val immutableList = listOf(1, 2, 3)
// immutableList.add(4)  // ❌ Метода add() просто нет
```

### Почему val предпочтительнее var

**Предсказуемость при чтении кода.** Когда переменная объявлена как `val`, вы знаете, что ссылка не изменится до конца scope. При дебаге не нужно искать все места, где переменная могла быть переприсвоена.

```kotlin
// var — нужно проверить весь код между объявлением и использованием
var config = loadConfig()
// ... 50 строк кода ...
// Какой config здесь? Мог измениться где угодно выше.

// val — ссылка гарантированно та же
val config = loadConfig()
// ... 50 строк кода ...
// config точно тот же объект, что был загружен.
```

**Упрощение многопоточного кода.** Mutable состояние в многопоточной среде — источник race conditions. Когда один поток читает переменную, другой может её изменить. С `val` эта проблема частично решена: ссылка не изменится. Для полной thread-safety нужны ещё и immutable объекты.

```kotlin
// var в многопоточности — потенциальный баг
var sharedConfig: Config? = null
// Поток A: if (sharedConfig != null) { use(sharedConfig!!) }
// Поток B: sharedConfig = null
// Поток A падает с NPE между проверкой и использованием

// val устраняет одну категорию проблем
val sharedConfig = loadConfig()  // Ссылка не изменится
```

**Совместимость с функциональным стилем.** Kotlin Collections API (`map`, `filter`, `fold`) построен на принципе: каждая операция возвращает новую коллекцию, не изменяя исходную. Это позволяет строить цепочки преобразований без побочных эффектов.

```kotlin
// Императивный стиль (mutable):
val numbers = mutableListOf(1, 2, 3, 4, 5)
val result = mutableListOf<Int>()
for (n in numbers) {
    if (n % 2 == 0) {
        result.add(n * 2)
    }
}

// Функциональный стиль (immutable):
val numbers = listOf(1, 2, 3, 4, 5)
val result = numbers
    .filter { it % 2 == 0 }  // Новый список [2, 4]
    .map { it * 2 }          // Новый список [4, 8]
// Оригинальный numbers не изменён
```

Функциональный стиль компактнее, легче тестируется (нет скрытого состояния), и проще распараллеливается.

### Типы данных

Kotlin поддерживает стандартные числовые типы, но все они являются классами, а не примитивами в Java-смысле. Компилятор автоматически использует примитивные типы JVM (`int`, `long`) для производительности там, где это возможно.

```kotlin
// Числовые типы
val byte: Byte = 127
val short: Short = 32767
val int: Int = 2_147_483_647      // Подчеркивания для читабельности
val long: Long = 9_000_000_000L   // L суффикс для Long
val float: Float = 3.14F          // F суффикс для Float
val double: Double = 3.14159
```

Строки поддерживают интерполяцию и многострочный формат через тройные кавычки. `Unit` — аналог `void` в Java, но является полноценным типом с единственным значением (можно использовать в generics).

```kotlin
// Символы, строки и логический тип
val char: Char = 'A'
val string: String = "Hello"
val multiline = """
    This is multiline string
""".trimIndent()
val isActive: Boolean = true

// Unit — можно опустить в сигнатуре
fun logMessage(msg: String) { println(msg) }
```

---

## 2. Null Safety

### Nullable vs Non-nullable типы

В Kotlin типы делятся на nullable и non-nullable. По умолчанию переменная не может содержать null — для этого нужно явно добавить `?` к типу.

```kotlin
// Non-nullable по умолчанию
var name: String = "John"
name = null  // ❌ Ошибка компиляции

// Nullable тип — добавляем ?
var nullableName: String? = "John"
nullableName = null  // ✅ OK
```

Компилятор предлагает несколько способов безопасной работы с nullable-типами. Каждый подходит для разных ситуаций: safe call для цепочек, Elvis для значений по умолчанию, явная проверка для блоков логики.

```kotlin
fun printLength(text: String?) {
    println(text?.length)            // Safe call: null если text == null
    val length = text?.length ?: 0   // Elvis: 0 если null
    if (text != null) {
        println(text.length)         // Smart cast: text теперь String
    }
    println(text!!.length)           // Принудительный вызов (NPE если null!)
}
```

### Safe calls и Elvis operator

```kotlin
// Цепочка safe calls
val country = user?.address?.city?.country

// Elvis operator с выражением
val name = user?.name ?: return  // Early return если null
val email = user?.email ?: throw IllegalStateException("Email required")

// Комбинирование
val displayName = user?.profile?.displayName
    ?: user?.email
    ?: "Anonymous"
```

### let для обработки nullable

```kotlin
val email: String? = getEmail()

// Без let
if (email != null) {
    sendEmail(email)
}

// С let (idiomatic Kotlin)
email?.let {
    sendEmail(it)  // it — не-nullable String внутри блока
}

// let с несколькими значениями
val name: String? = getName()
val age: Int? = getAge()

if (name != null && age != null) {
    createUser(name, age)
}

// Более идиоматично (Kotlin 1.9+)
if (name != null && age != null) {
    createUser(name, age)  // Smart cast работает
}
```

---

## 3. Функции

### Объявление функций

```kotlin
// Базовый синтаксис
fun greet(name: String): String {
    return "Hello, $name!"
}

// Expression body (для однострочных функций)
fun greet2(name: String): String = "Hello, $name!"

// Type inference для return type
fun greet3(name: String) = "Hello, $name!"

// Unit return type можно опустить
fun logMessage(message: String) {
    println(message)
}

// Параметры по умолчанию
fun createUser(
    name: String,
    age: Int = 18,
    country: String = "USA"
): User {
    return User(name, age, country)
}

// Использование
createUser("John")                    // age=18, country="USA"
createUser("Jane", 25)                // country="USA"
createUser("Bob", country = "UK")     // age=18, country="UK"
```

### Named arguments

```kotlin
// Без named arguments (трудно понять что это)
sendEmail("user@example.com", "Hello", true, 5, false)

// С named arguments (self-documenting)
sendEmail(
    to = "user@example.com",
    subject = "Hello",
    isHtml = true,
    priority = 5,
    trackOpens = false
)

// Можно комбинировать positional и named
sendEmail("user@example.com", "Hello", priority = 5)
```

**Улучшает читабельность.** При чтении `sendEmail("user@example.com", "Hello", true, 5, false)` невозможно понять, что означают `true`, `5`, `false` без заглядывания в сигнатуру функции. С named arguments код самодокументируется — значение каждого параметра очевидно.

**Защита от ошибок при рефакторинге.** Представьте, что функция изменилась: параметры `isHtml` и `trackOpens` поменяли местами. При позиционных аргументах код продолжит компилироваться (оба `Boolean`), но поведение изменится. С named arguments компилятор поймает ошибку, если имя параметра изменилось.

```kotlin
// Было: sendEmail(..., isHtml: Boolean, trackOpens: Boolean)
// Стало: sendEmail(..., trackOpens: Boolean, isHtml: Boolean)

// Позиционные аргументы — тихо сломается
sendEmail("...", "...", true, false)  // Компилируется, но работает неправильно

// Named arguments — ошибка компиляции при изменении имён
sendEmail(..., isHtml = true, trackOpens = false)  // Порядок не важен
```

**Не нужно помнить порядок параметров.** Функции с 5+ параметрами одного типа — кошмар без named arguments. `createRect(10, 20, 30, 40)` — это width-height-x-y или x-y-width-height? С именованными аргументами вопрос не возникает.

### Varargs

```kotlin
fun sum(vararg numbers: Int): Int {
    return numbers.sum()
}

sum(1, 2, 3)           // 6
sum(1, 2, 3, 4, 5)     // 15

// Spread operator для передачи массива
val nums = intArrayOf(1, 2, 3)
sum(*nums)  // * — spread operator
```

### Локальные функции

```kotlin
fun processUser(user: User) {
    // Локальная функция внутри другой функции
    fun validate() {
        if (user.name.isEmpty()) throw IllegalArgumentException("Name required")
        if (user.age < 0) throw IllegalArgumentException("Invalid age")
    }

    validate()  // Используем локальную функцию

    // ... остальная логика
}
```

**Скрывает implementation details.** В Java вспомогательная функция валидации была бы приватным методом класса, видимым всему классу. Локальная функция видна только внутри `processUser` — это минимальный scope. Никто другой не вызовет `validate()` случайно.

**Доступ к переменным внешней функции.** Локальная функция автоматически замыкается на переменные внешней функции (closure). В примере `validate()` использует `user` без явной передачи параметра. В Java это потребовало бы передать `user` как аргумент или сделать его полем класса.

**Избегает дублирования без создания отдельного метода.** Если валидация нужна в двух местах внутри одной функции, но нигде больше — локальная функция идеальна. Создавать для этого отдельный приватный метод класса — overhead.

---

## 4. Управляющие конструкции

### if как выражение

```kotlin
// if — это выражение, возвращает значение
val max = if (a > b) a else b

val status = if (user.isActive) {
    "Active"
} else if (user.isSuspended) {
    "Suspended"
} else {
    "Inactive"
}

// Ternary operator не нужен!
// Java: String result = condition ? "yes" : "no";
val result = if (condition) "yes" else "no"
```

### when (замена switch)

```kotlin
// when с single value
fun describe(x: Any): String = when (x) {
    1 -> "One"
    2, 3 -> "Two or Three"
    in 4..10 -> "Between 4 and 10"
    is String -> "String of length ${x.length}"  // Smart cast!
    else -> "Unknown"
}

// when без аргумента (как if-else chain)
val score = 85
val grade = when {
    score >= 90 -> "A"
    score >= 80 -> "B"
    score >= 70 -> "C"
    score >= 60 -> "D"
    else -> "F"
}

// when exhaustive (важно для sealed classes)
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
}

fun handle(result: Result) = when (result) {
    is Result.Success -> println(result.data)
    is Result.Error -> println("Error: ${result.message}")
    Result.Loading -> println("Loading...")
    // else не нужен! Компилятор проверяет exhaustiveness
}
```

**Работает с любыми типами.** Java `switch` до версии 21 работал только с примитивами, enum и строками. Kotlin `when` принимает любой тип и поддерживает type checks (`is`), ranges (`in 1..10`), и множественные значения (`1, 2, 3 ->`).

**Exhaustiveness checking для sealed classes.** Когда `when` используется с sealed class, компилятор проверяет, что обработаны все возможные подтипы. Если добавить новый подтип `Result` и забыть обработать его в `when` — код не скомпилируется. Это ловит баги на этапе компиляции, а не в runtime.

```kotlin
// Добавили новый подтип
sealed class Result {
    data class Success(val data: String) : Result()
    data class Error(val message: String) : Result()
    object Loading : Result()
    object Cancelled : Result()  // Новый!
}

fun handle(result: Result) = when (result) {
    is Result.Success -> ...
    is Result.Error -> ...
    Result.Loading -> ...
    // ❌ Ошибка компиляции: 'when' expression must be exhaustive,
    // add necessary 'Cancelled' branch or 'else' branch instead
}
```

**Возвращает значение.** `when` — это выражение, не statement. Можно присвоить результат переменной: `val grade = when { ... }`. В Java для этого пришлось бы объявлять переменную до switch и присваивать в каждой ветке.

### Циклы

```kotlin
// for с ranges
for (i in 1..5) {
    println(i)  // 1, 2, 3, 4, 5
}

for (i in 1 until 5) {
    println(i)  // 1, 2, 3, 4 (без 5)
}

for (i in 5 downTo 1) {
    println(i)  // 5, 4, 3, 2, 1
}

for (i in 1..10 step 2) {
    println(i)  // 1, 3, 5, 7, 9
}

// for с коллекциями
val names = listOf("Alice", "Bob", "Charlie")
for (name in names) {
    println(name)
}

// С индексом
for ((index, name) in names.withIndex()) {
    println("$index: $name")
}

// while и do-while как в Java
while (condition) {
    // ...
}

do {
    // ...
} while (condition)
```

### Ranges

```kotlin
// Closed range (включает оба конца)
val range1 = 1..10        // 1, 2, ..., 10
val range2 = 'a'..'z'     // все буквы

// Half-open range
val range3 = 1 until 10   // 1, 2, ..., 9

// Проверка вхождения
if (age in 18..65) {
    println("Working age")
}

if (char !in 'a'..'z') {
    println("Not a lowercase letter")
}

// Ranges с коллекциями
val list = listOf(1, 2, 3, 4, 5)
println(list[0..2])  // [1, 2, 3]
```

---

## 5. String templates

```kotlin
val name = "John"
val age = 30

// Простая интерполяция
val greeting = "Hello, $name!"

// Выражения в ${}
val message = "Hello, ${name.uppercase()}!"
val info = "Next year you'll be ${age + 1}"

// Многострочные строки
val html = """
    <html>
        <body>
            <h1>Hello, $name!</h1>
            <p>Age: $age</p>
        </body>
    </html>
""".trimIndent()

// $ в строке
val price = """${'$'}9.99"""  // "$9.99"

// Raw strings без экранирования
val regex = """\\d{3}-\\d{2}-\\d{4}"""  // Java
val regex2 = """\d{3}-\d{2}-\d{4}"""    // Kotlin (raw string)
```

---

## 6. Equality

```kotlin
// Structural equality (==) — вызывает equals()
val a = "hello"
val b = "hello"
println(a == b)  // true

// Referential equality (===) — сравнивает ссылки
println(a === b)  // может быть true из-за string interning

val list1 = listOf(1, 2, 3)
val list2 = listOf(1, 2, 3)
println(list1 == list2)   // true (equals)
println(list1 === list2)  // false (разные объекты)

// Для nullable
val x: String? = null
println(x == null)   // true (безопасно)
println(x === null)  // true
```

**Java vs Kotlin:**
```java
// Java
if (str1 != null && str1.equals(str2)) { ... }

// Kotlin
if (str1 == str2) { ... }  // Автоматическая null-проверка!
```

---

## 7. Кастинг и проверка типов

### is и smart casts

```kotlin
fun describe(obj: Any): String {
    // is — аналог instanceof
    if (obj is String) {
        // Smart cast: obj автоматически String внутри блока
        return "String of length ${obj.length}"
    }

    if (obj is Int) {
        return "Int with value $obj"
    }

    return "Unknown type"
}

// Отрицание
if (obj !is String) {
    return "Not a string"
}

// Smart cast в when
fun process(value: Any) = when (value) {
    is String -> value.length        // value — String
    is Int -> value * 2              // value — Int
    is List<*> -> value.size         // value — List
    else -> -1
}
```

### Явное приведение типов

```kotlin
// as — unsafe cast (может выбросить ClassCastException)
val str: String = obj as String

// as? — safe cast (вернет null при неудаче)
val str: String? = obj as? String

// Паттерн с Elvis
val str: String = obj as? String ?: ""
val length = (obj as? String)?.length ?: 0
```

---

## 8. Операторы

### Стандартные операторы

```kotlin
// Арифметические
val sum = a + b
val diff = a - b
val prod = a * b
val quot = a / b
val rem = a % b

// Инкремент/декремент
var x = 0
x++  // postfix
++x  // prefix

// Compound assignment
x += 5
x -= 3
x *= 2
x /= 4
x %= 3

// Логические
val and = a && b
val or = a || b
val not = !a

// Сравнение
a == b   // equals
a != b
a < b
a > b
a <= b
a >= b
```

### in и ranges

```kotlin
// in с range
if (age in 18..65) { ... }

// in с коллекцией
if (item in list) { ... }

// !in
if (item !in list) { ... }
```

---

## 9. Exceptions

```kotlin
// Все exceptions — unchecked (нет checked exceptions!)
fun readFile(path: String): String {
    // Можем бросить IOException без throws в сигнатуре
    throw IOException("File not found")
}

// try-catch как выражение
val number = try {
    input.toInt()
} catch (e: NumberFormatException) {
    0  // default value
}

// finally
try {
    riskyOperation()
} catch (e: Exception) {
    handleError(e)
} finally {
    cleanup()
}

// Nothing type для функций, которые никогда не возвращаются
fun fail(message: String): Nothing {
    throw IllegalStateException(message)
}

val name = getName() ?: fail("Name required")  // Smart cast после fail
```

---

## 10. Packages и imports

```kotlin
// Объявление package
package com.example.myapp

// Импорты
import java.util.Date
import kotlin.collections.*
import com.example.utils.format as formatUtil  // Алиас

// Wildcard import
import kotlin.math.*

// Import функций верхнего уровня
import com.example.utils.validateEmail

// Visibility modifiers
public class User         // По умолчанию public
internal class Config     // Видимо только в модуле
private class Helper      // Видимо только в файле

// Top-level функции и свойства
fun topLevelFunction() { }
val TOP_LEVEL_CONST = 42
```

---

## Сравнение с Java

| Фича | Kotlin | Java |
|------|--------|------|
| Null safety | Compile-time | Runtime (NPE) |
| Type inference | `val x = 5` | `var x = 5` (Java 10+) |
| String templates | `"Hello, $name"` | `"Hello, " + name` |
| Smart casts | Автоматически | Требует явный cast |
| Semicolons | Опциональны | Обязательны |
| Default parameters | ✅ | ❌ |
| Named arguments | ✅ | ❌ |
| Top-level functions | ✅ | ❌ (только static в классах) |
| When expression | Exhaustive | switch (ограниченный) |
| Checked exceptions | Нет | Есть |

---

## Чеклист для начинающих

- [ ] Используй `val` везде где возможно
- [ ] Избегай `!!` (null assertion), используй `?.` и `?:`
- [ ] Предпочитай expression body для простых функций
- [ ] Используй named arguments для функций с > 3 параметрами
- [ ] Используй `when` вместо длинных if-else цепочек
- [ ] Применяй string templates вместо конкатенации
- [ ] Используй ranges для числовых проверок (`age in 18..65`)
- [ ] Предпочитай `==` вместо `.equals()`
- [ ] Используй smart casts после проверок `is`
- [ ] Пиши idiomatic Kotlin: лаконично, но читабельно

---

## Куда дальше

**Следующий шаг после основ:**
→ [[kotlin-oop]] — классы, data class, sealed class, наследование. Без этого не напишешь реальное приложение.

**Углубление в язык:**
→ [[kotlin-collections]] — работа с коллекциями (map, filter, fold). Kotlin-способ писать код.
→ [[kotlin-functional]] — лямбды, higher-order functions. Понимание этого откроет идиоматичный Kotlin.

**Контекст и сравнение:**
→ [[java-modern-features]] — что Java 21 взяла из Kotlin и чем отличается.
→ [[jvm-basics-history]] — как Kotlin компилируется в байткод и работает на JVM.

---

## Кто использует и реальные примеры

| Компания | Как используют Kotlin | Результаты |
|----------|----------------------|------------|
| **Google** | 60+ собственных приложений (Maps, Drive, Photos), Docs iOS на KMP | Kotlin-first с 2019, все новые API на Kotlin |
| **Netflix** | Prodicle — production management для съёмок | Kotlin Multiplatform для iOS/Android |
| **McDonald's** | Unified mobile app для всех платформ | Меньше crashes, единая команда вместо двух |
| **Pinterest** | Android приложение, 1.5M строк кода | Переход с Java занял 2 года, 50% меньше crashes |
| **Uber** | Rider/Driver apps, backend services | Kotlin + Coroutines для async операций |
| **Trello** | Android приложение полностью на Kotlin | Сократили codebase на 40% |

### Статистика Kotlin (2025)

```
Adoption:
- 70% топ-1000 Android-приложений на Kotlin
- 18% разработчиков используют Kotlin Multiplatform (рост с 7% в 2024)
- 20,000+ компаний используют KMP в production

Почему переходят:
- NullPointerException crashes: -50% после перехода (Pinterest)
- Boilerplate code: -40% меньше строк (Trello)
- Developer happiness: 95% не хотят возвращаться к Java (JetBrains Survey)
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Kotlin — обёртка над Java" | Kotlin — отдельный язык со своим компилятором. Компилируется в JVM bytecode, JavaScript, Native. Не зависит от Java runtime |
| "val = const" | val означает read-only reference, не immutability. val list = mutableListOf() — list нельзя переназначить, но содержимое можно менять |
| "Kotlin медленнее Java" | После JIT компиляции производительность идентична — одинаковый bytecode. Kotlin overhead — только в compile time |
| "String templates = конкатенация" | Templates компилируются в StringBuilder — эффективнее многократной конкатенации строк |
| "when — это switch" | when — expression (возвращает значение), поддерживает любые типы и условия, не только enum/int как switch |
| "Null safety решает все NPE" | Null safety работает только с Kotlin кодом. Java interop через platform types (!) может вызвать NPE |
| "Smart cast работает везде" | Smart cast не работает для var (может измениться), для properties с custom getter, для internal-scope из других модулей |
| "Data class автоматически immutable" | Data class генерирует copy(), equals(), hashCode(), но не запрещает var properties. Immutability — ответственность разработчика |
| "== проверяет ссылки в Kotlin" | == в Kotlin вызывает equals() (structural equality). Для ссылок используйте === (referential equality) |
| "Kotlin только для Android" | Kotlin используется в backend (Spring, Ktor), multiplatform (iOS, web), scripting. Android — лишь один из use cases |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin Basics |
|--------------|---------------------------|
| **Type Inference** | Компилятор выводит типы переменных: val x = 5 → Int. Hindley-Milner style inference |
| **Null Safety (Option Types)** | String? моделирует "может отсутствовать". Compile-time enforcement vs runtime NPE |
| **Expression vs Statement** | when, if, try — expressions возвращающие значение. Функциональный стиль программирования |
| **Pattern Matching** | when с is проверками и smart casts. Destructuring для data classes |
| **Algebraic Data Types** | Sealed class = Sum type (один из вариантов). Data class = Product type (комбинация полей) |
| **String Interpolation** | "Hello, $name" — template expressions компилируются в StringBuilder |
| **Range Types** | 1..10, 'a'..'z' — диапазоны как first-class objects. Используются в for loops и contains checks |
| **Named & Default Arguments** | Уменьшают необходимость в overloading. Частичное применение функций |
| **Unit Type** | Unit — тип с единственным значением. Отличается от void — можно использовать в generics |
| **Nothing Type** | Bottom type — subtype всех типов. Функции, которые никогда не возвращают (throw, infinite loop) |

---

## Связь с другими темами

**[[kotlin-oop]]** — основы языка (val/var, null-safety, data classes) создают фундамент для объектно-ориентированного программирования в Kotlin. Data classes, sealed classes и object declarations — расширения базового синтаксиса для моделирования предметной области. Без освоения basics невозможно понять, почему Kotlin OOP отличается от Java OOP. Изучите основы синтаксиса, затем переходите к ООП-паттернам.

**[[kotlin-functional]]** — Kotlin с самого начала проектировался как мультипарадигменный язык: лямбды, higher-order functions и expression-based конструкции (if, when как expressions) встроены в базовый синтаксис. Функциональное программирование расширяет basics: scope functions (let, apply, run) строятся на лямбдах, collection operators (map, filter) — на higher-order functions. Рекомендуется изучать functional после basics как естественное продолжение.

**[[kmp-getting-started]]** — Kotlin Multiplatform позволяет использовать один язык для Android, iOS, Desktop и Web. Все базовые конструкции Kotlin (null-safety, data classes, coroutines) работают одинаково на всех платформах. Понимание basics необходимо перед изучением KMP, потому что мультиплатформенный код — это обычный Kotlin с expect/actual декларациями для платформенных различий.

---

## Источники и дальнейшее чтение

- Jemerov D., Isakova S. (2024). *Kotlin in Action, 2nd Edition.* — каноническая книга от создателей языка. Подробное объяснение каждой конструкции Kotlin с точки зрения перехода с Java: val/var, null-safety, type inference, control flow.
- Moskala M. (2024). *Effective Kotlin.* — best practices и идиоматичный код. Объясняет, почему предпочитать val, когда использовать smart casts и как избегать типичных ошибок новичков.
- Vermeulen D. (2019). *Head First Kotlin.* — визуальный формат для начинающих. Хорошо подходит как первое знакомство с языком благодаря иллюстрациям и пошаговым примерам.

---

*Проверено: 2026-01-09 | Источники: Kotlin docs, JetBrains surveys, Google I/O 2024 — Педагогический контент проверен*
