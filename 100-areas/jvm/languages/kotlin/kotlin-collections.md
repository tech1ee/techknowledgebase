---
title: "Kotlin Collections API: List, Set, Map и их операции"
created: 2025-11-25
modified: 2026-01-03
tags:
  - topic/jvm
  - collections
  - sequences
  - functional-programming
  - type/concept
  - level/intermediate
status: published
---

# Kotlin Collections: List, Set, Map

> **TL;DR:** Read-only (`List`) vs Mutable (`MutableList`) — API разделение, не true immutability. Sequences для больших данных: `list.asSequence().map{}.filter{}.toList()` — lazy, без промежуточных аллокаций, 10x меньше памяти на миллион элементов. Операторы: map (трансформация), filter (фильтрация), groupBy (группировка), fold (свёртка). `chunked`, `windowed`, `zip` для сложных преобразований.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin basics | Синтаксис, типы, null-safety | [[kotlin-basics]] |
| Лямбды и HOF | map, filter используют лямбды | [[kotlin-functional]] |
| Generics | Понимать `List<T>`, variance | [[kotlin-type-system]] |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Read-only** | Интерфейс только для чтения | Витрина магазина — смотришь, но не трогаешь |
| **Mutable** | Изменяемый интерфейс | Корзина покупок — можно добавлять/убирать |
| **Sequence** | Ленивая коллекция | Конвейер — обрабатывает по одному |
| **Промежуточная операция** | map, filter — откладывается | Заказ в очереди — ждёт выполнения |
| **Терминальная операция** | toList, sum — запускает | Кнопка "Оплатить" — всё срабатывает |
| **Fold** | Свёртка в одно значение | Подсчёт итога в чеке |
| **GroupBy** | Группировка по ключу | Сортировка почты по адресам |
| **Variance** | Ковариантность `out T` | Наследование "только для чтения" |

---

Kotlin разделяет коллекции на read-only (`List`, `Set`, `Map`) и mutable (`MutableList`, `MutableSet`, `MutableMap`). Read-only — это API без методов модификации, но не гарантия иммутабельности: если оригинал mutable, изменения видны через read-only ссылку.

Sequences — ленивые коллекции для больших данных. `list.map{}.filter{}.toList()` создаёт промежуточные списки на каждом шаге; `list.asSequence().map{}.filter{}.toList()` обрабатывает элементы по одному без промежуточных аллокаций. Для миллиона элементов Sequence экономит память в 10x. Операторы те же (map, filter, reduce), но момент вычисления разный: eager vs lazy.

---

## Иерархия коллекций Kotlin

### Основные интерфейсы

```kotlin
// Read-only интерфейсы (только чтение)
interface Iterable<out T>
interface Collection<out T> : Iterable<T>
interface List<out T> : Collection<T>
interface Set<out T> : Collection<T>
interface Map<K, out V>

// Mutable интерфейсы (изменяемые)
interface MutableIterable<out T> : Iterable<T>
interface MutableCollection<E> : Collection<E>, MutableIterable<E>
interface MutableList<E> : List<E>, MutableCollection<E>
interface MutableSet<E> : Set<E>, MutableCollection<E>
interface MutableMap<K, V> : Map<K, V>
```

**Почему два уровня?**
- Безопасность: явное различие между read-only и mutable API
- Ясность намерений: функция принимающая `List<T>` сигнализирует, что не будет модифицировать
- Variance: read-only интерфейсы ковариантны (`out T`), что даёт гибкость типов

### Read-only vs Immutable

```kotlin
fun main() {
    // Read-only ссылка
    val readOnlyList: List<String> = mutableListOf("a", "b", "c")

    // readOnlyList.add("d") // Ошибка компиляции

    // Но базовая коллекция может быть изменена!
    val mutableRef = readOnlyList as MutableList<String>
    mutableRef.add("d")

    println(readOnlyList) // [a, b, c, d] - данные изменились!

    // Истинная иммутабельность только через библиотеки типа kotlinx.collections.immutable
}
```

**Почему не истинная иммутабельность?**
- Java interop: Kotlin коллекции должны работать с Java
- Performance: избегаем копирования данных
- Практичность: большинство случаев покрывается read-only интерфейсами

## List - упорядоченная коллекция

### Создание списков

```kotlin
// Read-only списки
val list1 = listOf(1, 2, 3)                    // ArrayList под капотом
val list2 = emptyList<Int>()                   // Singleton EmptyList
val list3 = listOfNotNull(1, null, 3)         // [1, 3] - фильтрует null

// Mutable списки
val mutable1 = mutableListOf(1, 2, 3)         // ArrayList
val mutable2 = arrayListOf(1, 2, 3)           // Явно ArrayList
val mutable3 = ArrayList<Int>(capacity = 100)  // С начальной ёмкостью

// Билдер
val list4 = buildList {
    add(1)
    add(2)
    addAll(listOf(3, 4))
} // Возвращает read-only List
```

**Почему buildList?**
- Избегаем временных mutable переменных
- Чётко разделяем фазу построения и использования
- Оптимизация: компилятор знает, что результат read-only

### Доступ к элементам

```kotlin
val list = listOf("a", "b", "c", "d")

// Чтение по индексу
val first = list[0]                    // "a"
val second = list.get(1)               // "b"
val last = list[list.size - 1]         // "d"

// Безопасный доступ
val element = list.getOrNull(10)       // null вместо исключения
val element2 = list.getOrElse(10) { "default" }

// Функциональный доступ
val first2 = list.first()              // "a", исключение если пусто
val firstOrNull = list.firstOrNull()   // "a" или null
val last2 = list.last()

// С предикатом
val firstB = list.first { it.startsWith("b") }    // "b"
val firstC = list.firstOrNull { it.startsWith("z") } // null
```

**Почему множество вариантов?**
- Безопасность: getOrNull, firstOrNull не кидают исключения
- Читаемость: first() vs list[0] - intent яснее
- Производительность: getOrElse с лямбдой вычисляется только при необходимости

### Индексация и поиск

```kotlin
val list = listOf("apple", "banana", "cherry", "banana")

// Поиск индекса
val index1 = list.indexOf("banana")           // 1 (первое вхождение)
val index2 = list.lastIndexOf("banana")       // 3 (последнее)
val index3 = list.indexOf("orange")           // -1 (не найдено)

// Поиск с предикатом
val index4 = list.indexOfFirst { it.length > 5 }  // 1 ("banana")
val index5 = list.indexOfLast { it.length > 5 }   // 3
val index6 = list.indexOfFirst { it.startsWith("z") } // -1

// Проверка наличия
val contains = "banana" in list               // true
val contains2 = list.contains("orange")       // false
```

### Подсписки и диапазоны

```kotlin
val list = listOf(0, 1, 2, 3, 4, 5)

// Sublists
val sublist1 = list.subList(1, 4)             // [1, 2, 3] - end эксклюзивен
val sublist2 = list.slice(1..3)               // [1, 2, 3]
val sublist3 = list.slice(listOf(0, 2, 4))    // [0, 2, 4]

// Take и Drop
val firstThree = list.take(3)                 // [0, 1, 2]
val lastTwo = list.takeLast(2)                // [4, 5]
val withoutFirst = list.drop(2)               // [2, 3, 4, 5]
val withoutLast = list.dropLast(2)            // [0, 1, 2, 3]

// С предикатом
val taken = list.takeWhile { it < 3 }         // [0, 1, 2]
val dropped = list.dropWhile { it < 3 }       // [3, 4, 5]
```

**Почему subList возвращает view?**
- Производительность: не копирует данные
- Осторожно: изменения в mutable списке отразятся на view!

## Set - уникальные элементы

```kotlin
// Read-only sets
val set1 = setOf(1, 2, 3, 2)                  // [1, 2, 3] - дубликаты удалены
val set2 = emptySet<Int>()

// Mutable sets
val mutableSet = mutableSetOf(1, 2, 3)        // LinkedHashSet (сохраняет порядок)
val hashSet = hashSetOf(1, 2, 3)              // HashSet
val linkedSet = linkedSetOf(1, 2, 3)          // LinkedHashSet
val sortedSet = sortedSetOf(3, 1, 2)          // TreeSet - отсортирован [1, 2, 3]

// Операции над множествами
val set3 = setOf(1, 2, 3)
val set4 = setOf(2, 3, 4)

val union = set3 union set4                   // [1, 2, 3, 4]
val union2 = set3 + set4                      // То же самое

val intersect = set3 intersect set4           // [2, 3]
val subtract = set3 subtract set4             // [1]
val subtract2 = set3 - set4                   // [1]
```

**Почему LinkedHashSet по умолчанию?**
- Предсказуемый порядок: элементы в порядке добавления
- Приемлемая производительность: O(1) для основных операций
- Согласованность: List сохраняет порядок, Set тоже должен

### Когда использовать какой Set

```kotlin
// HashSet - максимальная производительность, порядок не важен
val visitors = hashSetOf<String>()
// O(1) add, contains, remove

// LinkedHashSet - нужен порядок вставки
val registrationQueue = linkedSetOf<User>()
// O(1) операции + порядок

// TreeSet - нужна сортировка
val sortedScores = sortedSetOf<Int>()
// O(log n) операции, всегда отсортирован
```

## Map - пары ключ-значение

### Создание карт

```kotlin
// Read-only maps
val map1 = mapOf("a" to 1, "b" to 2, "c" to 3)
val map2 = mapOf(Pair("a", 1), Pair("b", 2))  // То же самое
val map3 = emptyMap<String, Int>()

// Mutable maps
val mutableMap = mutableMapOf("a" to 1)        // LinkedHashMap
val hashMap = hashMapOf("a" to 1)              // HashMap
val linkedMap = linkedHashMapOf("a" to 1)      // LinkedHashMap
val sortedMap = sortedMapOf("c" to 3, "a" to 1) // TreeMap - ключи отсортированы

// Билдер
val map4 = buildMap {
    put("a", 1)
    put("b", 2)
    this["c"] = 3                              // Оператор set
}
```

### Доступ к элементам

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// Чтение
val value1 = map["a"]                          // 1 (может быть null)
val value2 = map.get("a")                      // 1
val value3 = map.getValue("a")                 // 1 (исключение если нет ключа)

// Безопасный доступ
val value4 = map.getOrDefault("z", 0)          // 0
val value5 = map.getOrElse("z") { 0 }          // 0
val value6 = map.getOrPut("z") { 0 }           // 0 (для mutable, добавляет если нет)

// Проверка наличия
val has = "a" in map                           // true
val has2 = map.containsKey("a")                // true
val has3 = map.containsValue(1)                // true
```

**Почему getValue vs get?**
- `get()` возвращает nullable тип - безопасно, но требует проверки
- `getValue()` кидает исключение - для случаев когда ключ ДОЛЖЕН существовать
- `getOrElse/getOrDefault` - для значений по умолчанию

### Итерация по картам

```kotlin
val map = mapOf("a" to 1, "b" to 2, "c" to 3)

// По записям
for ((key, value) in map) {
    println("$key -> $value")
}

// По ключам
for (key in map.keys) {
    println(key)
}

// По значениям
for (value in map.values) {
    println(value)
}

// Функциональный стиль
map.forEach { (key, value) ->
    println("$key -> $value")
}

map.forEach { entry ->
    println("${entry.key} -> ${entry.value}")
}
```

## Функциональные операции

### map - трансформация элементов

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// Простая трансформация
val doubled = numbers.map { it * 2 }           // [2, 4, 6, 8, 10]
val strings = numbers.map { "Number $it" }     // ["Number 1", "Number 2", ...]

// mapIndexed - с индексом
val indexed = numbers.mapIndexed { index, value ->
    "$index: $value"
}  // ["0: 1", "1: 2", ...]

// mapNotNull - отфильтровывает null
val parsed = listOf("1", "2", "abc", "4").mapNotNull { it.toIntOrNull() }
// [1, 2, 4]

// mapKeys/mapValues для Map
val map = mapOf("a" to 1, "b" to 2)
val upperKeys = map.mapKeys { (key, _) -> key.uppercase() }  // {A=1, B=2}
val doubledValues = map.mapValues { (_, value) -> value * 2 } // {a=2, b=4}
```

**Почему map создаёт новую коллекцию?**
- Иммутабельность данных: исходная коллекция не меняется
- Thread-safety: безопасно для многопоточности
- Функциональный стиль: чистые функции без побочных эффектов

### filter - фильтрация элементов

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6)

// Простая фильтрация
val evens = numbers.filter { it % 2 == 0 }     // [2, 4, 6]
val odds = numbers.filterNot { it % 2 == 0 }   // [1, 3, 5]

// filterIndexed - с индексом
val filtered = numbers.filterIndexed { index, value ->
    index % 2 == 0 && value > 2
}  // [3, 5] - элементы на чётных позициях > 2

// filterIsInstance - по типу
val mixed: List<Any> = listOf(1, "two", 3, "four")
val strings = mixed.filterIsInstance<String>()  // ["two", "four"]
val ints = mixed.filterIsInstance<Int>()        // [1, 3]

// filterNotNull
val nullable = listOf(1, null, 2, null, 3)
val notNull = nullable.filterNotNull()         // [1, 2, 3]
```

### flatMap - сплющивание вложенных коллекций

```kotlin
// flatMap = map + flatten
val nested = listOf(listOf(1, 2), listOf(3, 4), listOf(5))
val flattened = nested.flatten()               // [1, 2, 3, 4, 5]

// flatMap - трансформация с последующим flatten
val words = listOf("hello", "world")
val chars = words.flatMap { it.toList() }      // [h, e, l, l, o, w, o, r, l, d]

// Практический пример: получение всех файлов из директорий
data class Directory(val name: String, val files: List<String>)

val directories = listOf(
    Directory("src", listOf("Main.kt", "Utils.kt")),
    Directory("test", listOf("MainTest.kt"))
)

val allFiles = directories.flatMap { it.files }
// [Main.kt, Utils.kt, MainTest.kt]

// flatMapIndexed
val indexed = listOf("a", "b").flatMapIndexed { index, s ->
    List(index + 1) { s }
}  // [a, b, b]
```

**Почему flatMap нужен?**
- Работа с вложенными структурами: файлы в папках, комментарии в постах
- Избегаем ручного flatten: `list.map { ... }.flatten()`
- Монадический паттерн: часто используется в функциональном программировании

### fold и reduce - агрегация

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// fold - с начальным значением
val sum = numbers.fold(0) { acc, value -> acc + value }  // 15
val product = numbers.fold(1) { acc, value -> acc * value } // 120

// foldIndexed - с индексом
val indexed = numbers.foldIndexed(0) { index, acc, value ->
    acc + index * value
}  // 0*1 + 1*2 + 2*3 + 3*4 + 4*5 = 40

// foldRight - справа налево
val right = numbers.foldRight(0) { value, acc -> acc + value }  // 15

// reduce - без начального значения (использует первый элемент)
val sum2 = numbers.reduce { acc, value -> acc + value }  // 15
// Эквивалентно fold(numbers[0]) { ... } на numbers.drop(1)

// Практические примеры
data class Product(val name: String, val price: Double)

val cart = listOf(
    Product("Apple", 1.0),
    Product("Banana", 0.5),
    Product("Cherry", 2.0)
)

val totalPrice = cart.fold(0.0) { total, product ->
    total + product.price
}  // 3.5

val invoice = cart.fold("Invoice:\n") { invoice, product ->
    invoice + "- ${product.name}: $${product.price}\n"
}
```

**Почему fold vs reduce?**
- `fold` универсальнее: можно задать начальное значение и тип результата отличается от элементов
- `reduce` проще для простых агрегаций одного типа
- `fold` безопаснее: не кидает исключение на пустой коллекции

### groupBy - группировка элементов

```kotlin
data class Person(val name: String, val age: Int, val city: String)

val people = listOf(
    Person("Alice", 25, "London"),
    Person("Bob", 30, "Paris"),
    Person("Charlie", 25, "London"),
    Person("David", 30, "London")
)

// Группировка по одному ключу
val byAge = people.groupBy { it.age }
// {25=[Alice, Charlie], 30=[Bob, David]}

val byCity = people.groupBy { it.city }
// {London=[Alice, Charlie, David], Paris=[Bob]}

// groupBy с трансформацией значений
val namesByCity = people.groupBy(
    keySelector = { it.city },
    valueTransform = { it.name }
)
// {London=[Alice, Charlie, David], Paris=[Bob]}

// groupingBy для агрегаций
val countByCity = people.groupingBy { it.city }.eachCount()
// {London=3, Paris=1}

val sumAgeByCity = people.groupingBy { it.city }
    .fold(0) { acc, person -> acc + person.age }
// {London=80, Paris=30}

// partition - разделение на две группы
val (adults, young) = people.partition { it.age >= 30 }
// adults = [Bob, David], young = [Alice, Charlie]
```

**Почему groupBy возвращает Map<K, List<V>>?**
- Гибкость: можно работать с группами как с обычными списками
- Типобезопасность: тип ключа и значений явный
- Производительность: одним проходом создаёт все группы

### associate - создание Map

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// associate - полный контроль над парами
val squares = numbers.associate { it to it * it }
// {1=1, 2=4, 3=9, 4=16, 5=25}

// associateWith - генерация значений из ключей
val defaults = numbers.associateWith { 0 }
// {1=0, 2=0, 3=0, 4=0, 5=0}

// associateBy - генерация ключей из значений
data class User(val id: Int, val name: String)

val users = listOf(
    User(1, "Alice"),
    User(2, "Bob"),
    User(3, "Charlie")
)

val usersById = users.associateBy { it.id }
// {1=User(1, Alice), 2=User(2, Bob), 3=User(3, Charlie)}

// associateBy с трансформацией значения
val namesById = users.associateBy(
    keySelector = { it.id },
    valueTransform = { it.name }
)
// {1=Alice, 2=Bob, 3=Charlie}
```

### Цепочки операций

```kotlin
data class Order(val id: Int, val items: List<String>, val total: Double, val status: String)

val orders = listOf(
    Order(1, listOf("Apple", "Banana"), 5.5, "completed"),
    Order(2, listOf("Cherry"), 2.0, "pending"),
    Order(3, listOf("Apple", "Cherry", "Date"), 10.0, "completed"),
    Order(4, listOf("Banana"), 1.5, "cancelled")
)

// Комплексная обработка
val result = orders
    .filter { it.status == "completed" }              // Только завершённые
    .flatMap { it.items }                             // Все товары
    .groupingBy { it }                                // Группировка по товару
    .eachCount()                                      // Подсчёт количества
    .entries                                          // Entries для сортировки
    .sortedByDescending { it.value }                  // Сортировка по убыванию
    .take(3)                                          // Топ-3
    .associate { it.key to it.value }                 // Обратно в Map

// result = {Apple=2, Cherry=1, Banana=1}
```

**Почему цепочки эффективны?**
- Читаемость: каждый шаг выражает одну операцию
- Но осторожно: создают промежуточные коллекции на каждом шаге
- Для больших данных используйте Sequences!

## Sequences - ленивые вычисления

### Разница между Collection и Sequence

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8)

// Collection - eager evaluation
val resultList = numbers
    .filter {
        println("filter: $it")
        it % 2 == 0
    }
    .map {
        println("map: $it")
        it * it
    }
    .take(2)

// Output:
// filter: 1, filter: 2, filter: 3, ..., filter: 8  (все элементы)
// map: 2, map: 4, map: 6, map: 8                    (все чётные)
// Result: [4, 16]

// Sequence - lazy evaluation
val resultSeq = numbers.asSequence()
    .filter {
        println("filter: $it")
        it % 2 == 0
    }
    .map {
        println("map: $it")
        it * it
    }
    .take(2)
    .toList()

// Output:
// filter: 1, filter: 2, map: 2  (нашли первый)
// filter: 3, filter: 4, map: 4  (нашли второй)
// Result: [4, 16]
```

**Почему Sequence эффективнее?**
- **Ленивость**: операции выполняются только когда нужен результат (terminal operation)
- **По элементам**: обрабатывает один элемент через все операции, а не все элементы через одну
- **Нет промежуточных коллекций**: экономия памяти
- **Short-circuiting**: может остановиться раньше (take, first, any)

### Создание Sequences

```kotlin
// Из коллекции
val seq1 = listOf(1, 2, 3).asSequence()

// generateSequence - бесконечная последовательность
val naturalNumbers = generateSequence(1) { it + 1 }
val first10 = naturalNumbers.take(10).toList()     // [1, 2, ..., 10]

// Fibonacci
val fibonacci = generateSequence(Pair(0, 1)) { (a, b) -> Pair(b, a + b) }
    .map { it.first }
val first10Fib = fibonacci.take(10).toList()       // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

// sequence builder
val seq3 = sequence {
    yield(1)
    yieldAll(listOf(2, 3, 4))
    yieldAll(generateSequence(5) { it + 1 }.take(5))
}
// [1, 2, 3, 4, 5, 6, 7, 8, 9]
```

### Intermediate vs Terminal операции

```kotlin
val numbers = listOf(1, 2, 3, 4, 5)

// Intermediate операции (возвращают Sequence) - ленивые
val seq = numbers.asSequence()
    .filter { it % 2 == 0 }     // Не выполняется
    .map { it * it }            // Не выполняется

println("No computation yet!")

// Terminal операции - запускают вычисления
val list = seq.toList()         // Сейчас вычисляется: [4, 16]
val sum = seq.sum()             // Вычисляется снова: 20
val first = seq.first()         // Вычисляется снова: 4
```

**Важно**: Sequence можно использовать многократно, но вычисления будут каждый раз заново!

### Когда использовать Sequence

```kotlin
// ❌ НЕ используйте для маленьких коллекций
val small = listOf(1, 2, 3, 4, 5)
    .asSequence()                // Overhead превышает выгоду
    .map { it * 2 }
    .toList()

// ✅ Используйте для больших коллекций
val large = (1..1_000_000)
    .asSequence()                // Экономит память и время
    .filter { it % 2 == 0 }
    .map { it * it }
    .take(100)
    .toList()

// ✅ Используйте когда не нужны все элементы
val firstEven = (1..1_000_000)
    .asSequence()
    .filter { it % 2 == 0 }
    .first()                     // Останавливается на 2

// ✅ Используйте для бесконечных последовательностей
val infiniteSeq = generateSequence(0) { it + 1 }
    .filter { it % 2 == 0 }
    .take(10)
    .toList()

// ✅ Используйте для файлов и I/O
File("large.txt")
    .bufferedReader()
    .lineSequence()              // Читает построчно, не загружая весь файл
    .filter { it.isNotEmpty() }
    .map { it.trim() }
    .take(100)
    .toList()
```

**Правило большого пальца**:
- Коллекция < 100 элементов → Collection
- Коллекция > 100 элементов + много операций → Sequence
- Бесконечные данные или I/O → Sequence

## Отличия от Java Collections

### Разделение read-only и mutable

```kotlin
// Kotlin
val kotlinList: List<String> = listOf("a")      // Только чтение
val kotlinMutable: MutableList<String> = mutableListOf("a")

// Java - всегда mutable (кроме Collections.unmodifiable...)
List<String> javaList = new ArrayList<>();
javaList.add("a");                              // Всегда можно добавить
```

### Нет сюрпризов с null

```kotlin
// Kotlin - null должен быть явным
val list: List<String> = listOf("a", "b")
// val bad = list[0].length  // Всегда безопасно

val nullable: List<String?> = listOf("a", null)
// val len = nullable[0].length  // Ошибка компиляции
val len = nullable[0]?.length    // Надо проверить null

// Java - null может быть где угодно
List<String> javaList = Arrays.asList("a", null, "b");
int len = javaList.get(1).length();  // NullPointerException!
```

### Богатый функциональный API

```kotlin
// Kotlin - из коробки
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { it * 2 }
val evens = numbers.filter { it % 2 == 0 }
val sum = numbers.fold(0) { acc, n -> acc + n }

// Java - нужен Stream API (Java 8+)
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5);
List<Integer> doubled = numbers.stream()
    .map(n -> n * 2)
    .collect(Collectors.toList());
```

### Ковариантность

```kotlin
// Kotlin - read-only коллекции ковариантны
val strings: List<String> = listOf("a", "b")
val any: List<Any> = strings                    // ✅ OK

val mutableStrings: MutableList<String> = mutableListOf("a")
// val mutableAny: MutableList<Any> = mutableStrings  // ❌ Ошибка

// Java - коллекции инвариантны
List<String> javaStrings = Arrays.asList("a", "b");
// List<Object> javaObjects = javaStrings;  // ❌ Ошибка компиляции
```

## Практические паттерны

### Билдеры коллекций

```kotlin
// Вместо мутабельных переменных
fun getUsers(): List<User> {
    val users = mutableListOf<User>()
    users.add(User("Alice"))
    if (includeAdmin) {
        users.add(User("Admin"))
    }
    return users
}

// Используйте билдер
fun getUsers(): List<User> = buildList {
    add(User("Alice"))
    if (includeAdmin) {
        add(User("Admin"))
    }
}
```

### Преобразование null-безопасности

```kotlin
// Часто нужно из List<T?> получить List<T>
val nullable: List<String?> = listOf("a", null, "b", null, "c")

val notNull1 = nullable.filterNotNull()         // [a, b, c]
val notNull2 = nullable.mapNotNull { it }       // [a, b, c]

// С трансформацией
val lengths = nullable.mapNotNull { it?.length }  // [1, 1, 1]
```

### Работа с индексами

```kotlin
val items = listOf("a", "b", "c", "d")

// Когда нужен индекс
items.forEachIndexed { index, item ->
    println("$index: $item")
}

val indexed = items.mapIndexed { index, item ->
    "$index-$item"
}  // [0-a, 1-b, 2-c, 3-d]

// withIndex для for
for ((index, item) in items.withIndex()) {
    println("$index: $item")
}
```

### Chunking и Windowing

```kotlin
val numbers = listOf(1, 2, 3, 4, 5, 6, 7, 8)

// chunked - разбить на группы
val chunks = numbers.chunked(3)
// [[1, 2, 3], [4, 5, 6], [7, 8]]

val chunkSums = numbers.chunked(3) { it.sum() }
// [6, 15, 15]

// windowed - скользящее окно
val windows = numbers.windowed(3)
// [[1, 2, 3], [2, 3, 4], [3, 4, 5], ..., [6, 7, 8]]

val windowed = numbers.windowed(size = 3, step = 2, partialWindows = true)
// [[1, 2, 3], [3, 4, 5], [5, 6, 7], [7, 8]]

// zipWithNext - пары соседних элементов
val pairs = numbers.zipWithNext()
// [(1, 2), (2, 3), (3, 4), ..., (7, 8)]

val diffs = numbers.zipWithNext { a, b -> b - a }
// [1, 1, 1, 1, 1, 1, 1] - все разности = 1
```

## Распространённые ошибки

### 1. Изменение коллекции во время итерации

```kotlin
// ❌ ConcurrentModificationException
val list = mutableListOf(1, 2, 3, 4, 5)
for (item in list) {
    if (item % 2 == 0) {
        list.remove(item)       // ❌ Падает!
    }
}

// ✅ Используйте iterator.remove()
val iterator = list.iterator()
while (iterator.hasNext()) {
    if (iterator.next() % 2 == 0) {
        iterator.remove()       // ✅ OK
    }
}

// ✅ Или создайте новую коллекцию
val filtered = list.filter { it % 2 != 0 }

// ✅ Или removeAll/retainAll
list.removeAll { it % 2 == 0 }
```

### 2. Множественные вычисления Sequence

```kotlin
// ❌ Sequence вычисляется каждый раз заново
val seq = (1..1_000_000).asSequence()
    .filter { heavyComputation(it) }
    .map { anotherHeavyOp(it) }

val first = seq.first()         // Вычисления
val second = seq.take(2).last() // Вычисления снова!

// ✅ Материализуйте в List если нужно многократное использование
val materialized = seq.toList()
val first = materialized.first()
val second = materialized[1]
```

### 3. Read-only не значит immutable

```kotlin
// ❌ Ложная безопасность
fun processItems(items: List<String>) {
    // Думаем что items не изменится...
    val first = items.first()

    // Но кто-то другой может иметь mutable ссылку!
    // items может измениться в другом потоке
}

// ✅ Для истинной иммутабельности используйте библиотеки
// kotlinx.collections.immutable
val immutable = persistentListOf(1, 2, 3)
```

### 4. Неэффективные цепочки операций

```kotlin
// ❌ Неэффективно для больших коллекций
val result = (1..1_000_000)
    .map { it * 2 }              // Создаёт List на 1M элементов
    .filter { it % 3 == 0 }      // Создаёт новый List
    .map { it.toString() }       // Ещё один List
    .take(10)                    // Обработали миллион ради 10!

// ✅ Используйте Sequence
val result = (1..1_000_000).asSequence()
    .map { it * 2 }
    .filter { it % 3 == 0 }
    .map { it.toString() }
    .take(10)
    .toList()
```

## Чеклист

- [ ] Используете read-only интерфейсы (List, Set, Map) по умолчанию
- [ ] Понимаете разницу между read-only и immutable
- [ ] Применяете Sequence для больших коллекций (>100 элементов)
- [ ] Используете функциональные операции вместо циклов где уместно
- [ ] Избегаете изменения коллекций во время итерации
- [ ] Не используете Sequence многократно без материализации
- [ ] Знаете когда использовать HashSet vs LinkedHashSet vs TreeSet
- [ ] Применяете mapNotNull, filterNotNull для работы с nullable
- [ ] Используете buildList/buildMap/buildSet для построения коллекций
- [ ] Понимаете eager vs lazy evaluation

## Куда дальше

**Для глубокого понимания:**
→ [[kotlin-functional]] — лямбды и higher-order functions. Операторы коллекций — это именно они.
→ [[kotlin-advanced-features]] — extension functions позволяют добавлять свои операторы к коллекциям.

**Практика:**
→ [[kotlin-best-practices]] — когда использовать Sequence, когда Collection, типичные ошибки.

**Если здесь впервые:**
→ [[kotlin-basics]] — базовый синтаксис, без которого примеры будут непонятны.

---

## Кто использует и реальные примеры

| Компания | Паттерны Collections | Результаты |
|----------|---------------------|------------|
| **JetBrains** | Sequence для анализа кода в IDE | Lazy processing миллионов AST nodes |
| **Netflix** | Functional chains для data processing | Читаемые pipelines вместо циклов |
| **Square** | kotlinx.collections.immutable | Thread-safe состояние в Compose |
| **Google** | buildList для динамических списков | Clean Compose API |
| **Uber** | groupBy, associateBy для агрегации | Бизнес-логика в одну цепочку |

### Паттерны в production

```
Паттерн 1: Data Pipeline с Sequence
───────────────────────────────────
// Обработка миллионов записей без OOM
File("logs.txt")
    .bufferedReader()
    .lineSequence()                      // Lazy reading
    .filter { "ERROR" in it }
    .map { parseLogLine(it) }
    .groupingBy { it.errorType }
    .eachCount()
    .entries
    .sortedByDescending { it.value }
    .take(10)
    .forEach { println("${it.key}: ${it.value}") }

Паттерн 2: Immutable Collections для Compose
────────────────────────────────────────────
// kotlinx.collections.immutable
val items: ImmutableList<Item> = persistentListOf()

// Новый список без мутации
val newItems = items.add(newItem)

// Compose автоматически перерисовывает
@Composable
fun ItemList(items: ImmutableList<Item>) {
    // items гарантированно не меняются между render
}

Паттерн 3: Batch Processing с chunked
─────────────────────────────────────
// Отправка в API пачками по 100
users
    .chunked(100)
    .forEach { batch ->
        api.createUsers(batch)
    }
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "List в Kotlin всегда immutable" | List — read-only interface, но может ссылаться на mutable implementation. listOf() создаёт действительно immutable (kotlin.collections.EmptyList) |
| "Sequence всегда быстрее List" | Sequence добавляет overhead на создание объектов. Для маленьких коллекций (<1000) List chain может быть быстрее |
| "map+filter создаёт 2 промежуточных списка" | Да для List, но они могут быть оптимизированы JIT. Используйте Sequence для explicit lazy evaluation |
| "toList() создаёт копию" | Для Sequence — да, создаёт новый List. Для List — может вернуть тот же объект если он immutable |
| "MutableList можно безопасно expose как List" | Клиент может сделать cast обратно в MutableList и мутировать. Используйте .toList() для defensive copy |
| "groupBy и associateBy одинаковы" | groupBy создаёт Map<K, List<V>> — все элементы с одним ключом. associateBy создаёт Map<K, V> — только последний элемент |
| "flatMap — это просто map + flatten" | Технически да, но flatMap optimized. Не создаёт промежуточный List<List<T>> в памяти |
| "chunked и windowed одинаковы" | chunked создаёт непересекающиеся группы. windowed создаёт sliding window с возможным overlap |
| "forEach лучше for loop" | forEach создаёт lambda object (без inline). for loop — нулевой overhead. В hot paths предпочитайте for |
| "kotlinx.collections.immutable = Kotlin stdlib" | Это отдельная библиотека! Persistent collections (PersistentList, PersistentMap) не входят в stdlib |

---

## CS-фундамент

| CS-концепция | Применение в Kotlin Collections |
|--------------|--------------------------------|
| **Lazy Evaluation** | Sequence реализует lazy evaluation — операции выполняются только при terminal operation |
| **Persistent Data Structures** | kotlinx.collections.immutable использует structural sharing — копирование с переиспользованием частей |
| **Variance** | List<out T> covariant (producer). MutableList<T> invariant (producer + consumer). Правила PECS |
| **Higher-Order Functions** | map, filter, fold — HOF принимающие функции как аргументы. Основа функционального стиля |
| **Pipeline Pattern** | collection.filter{}.map{}.reduce{} — data transformation pipeline. Declarative style |
| **Memoization** | При преобразованиях создаются промежуточные коллекции — implicit memoization. Sequence избегает это |
| **Iterator Pattern** | Sequence реализует Iterator protocol — элементы по требованию, не все сразу в памяти |
| **Defensive Copy** | .toList(), .toMutableList() создают копии для защиты от внешних мутаций. Encapsulation |
| **Structural Sharing** | PersistentList при add() переиспользует большую часть старой структуры. O(log n) copy |
| **Reduction** | reduce, fold — свёртка коллекции в одно значение. Catamorphism в теории категорий |

---

## Рекомендуемые источники

### Официальная документация
- [Kotlin Collections](https://kotlinlang.org/docs/collections-overview.html) — полный гайд
- [Sequences](https://kotlinlang.org/docs/sequences.html) — lazy collections
- [Collection Operations](https://kotlinlang.org/docs/collection-operations.html) — все операторы

### Книги
- **"Kotlin in Action"** (2nd ed) — глава о коллекциях
- **"Effective Kotlin"** — best practices для коллекций
- **"Functional Programming in Kotlin"** — продвинутые паттерны

### Библиотеки
- [kotlinx.collections.immutable](https://github.com/Kotlin/kotlinx.collections.immutable) — persistent collections
- [Arrow-kt](https://arrow-kt.io/) — функциональные расширения

---

*Проверено: 2026-01-09 | Источники: Kotlin docs, Effective Kotlin, JetBrains examples — Педагогический контент проверен*
