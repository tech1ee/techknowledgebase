---
title: "Код с объяснением каждой детали (с нуля)"
created: 2026-02-09
modified: 2026-02-09
type: tutorial
status: published
tags:
  - topic/cs-fundamentals
  - type/tutorial
  - level/beginner
related:
  - "[[code-explained-advanced]]"
  - "[[arrays-strings]]"
  - "[[recursion-fundamentals]]"
---

# Код с объяснением каждой детали (с нуля)

## Введение

Этот документ объясняет КАЖДУЮ строку кода так, чтобы человек без опыта мог понять что происходит. Мы начнём с самых базовых концепций и постепенно перейдём к сложным алгоритмам.

---

# ЧАСТЬ 1: БАЗОВЫЕ КОНЦЕПЦИИ

## 1.1 Что такое переменные и типы данных

```kotlin
// ПЕРЕМЕННАЯ — это "коробка" для хранения данных
// val = неизменяемая (нельзя изменить после создания)
// var = изменяемая (можно изменять)

val name = "Алиса"     // Строка (текст) — нельзя изменить
var age = 25           // Целое число — можно изменить
age = 26               // Теперь age = 26

// ТИПЫ ДАННЫХ (что можно хранить):
val number: Int = 42           // Целое число от -2 млрд до +2 млрд
val bigNumber: Long = 10000000000L  // Большое целое число (до ~9 квинтиллионов)
val decimal: Double = 3.14     // Дробное число
val flag: Boolean = true       // true (да) или false (нет)
val letter: Char = 'A'         // Один символ
val text: String = "Привет"    // Строка (много символов)
```

**Почему это важно:**
- `Int` может хранить числа до ~2 миллиардов
- Если числа больше — используем `Long`
- Если результат вычислений может превысить Int — сразу используем Long

---

## 1.2 Что такое массив (Array)

```kotlin
// МАССИВ — это список элементов, к которым можно обращаться по номеру (индексу)
// Индексы начинаются с 0!

val numbers = intArrayOf(10, 20, 30, 40, 50)
//            индекс:     0   1   2   3   4

// Как читать этот код:
// intArrayOf(...) — создаёт массив целых чисел
// numbers[0] = 10 (первый элемент)
// numbers[1] = 20 (второй элемент)
// numbers[4] = 50 (пятый элемент, последний)

// Получить элемент по индексу:
val first = numbers[0]   // first = 10
val third = numbers[2]   // third = 30

// Изменить элемент:
numbers[0] = 100         // Теперь массив: [100, 20, 30, 40, 50]

// Размер массива:
val size = numbers.size  // size = 5

// Создать массив заданного размера, заполненный нулями:
val zeros = IntArray(10)  // [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

// Создать массив с формулой:
val squares = IntArray(5) { index -> index * index }
// { index -> index * index } — это "лямбда-функция"
// Для каждого индекса вычисляется index * index
// Результат: [0, 1, 4, 9, 16]
// index=0: 0*0=0
// index=1: 1*1=1
// index=2: 2*2=4
// index=3: 3*3=9
// index=4: 4*4=16
```

---

## 1.3 Циклы — как перебирать элементы

```kotlin
// ЦИКЛ FOR — повторяет действие несколько раз

// Способ 1: перебрать числа от 0 до 4
for (i in 0..4) {
    println(i)  // Выведет: 0, 1, 2, 3, 4
}
// 0..4 означает "от 0 до 4 включительно"

// Способ 2: перебрать числа от 0 до 4 (не включая 4)
for (i in 0 until 4) {
    println(i)  // Выведет: 0, 1, 2, 3
}
// until означает "до, но не включая"

// Способ 3: перебрать все элементы массива
val arr = intArrayOf(10, 20, 30)
for (element in arr) {
    println(element)  // Выведет: 10, 20, 30
}

// Способ 4: перебрать индексы массива
for (i in arr.indices) {
    println("Индекс $i содержит ${arr[i]}")
}
// Выведет:
// Индекс 0 содержит 10
// Индекс 1 содержит 20
// Индекс 2 содержит 30

// ЦИКЛ WHILE — повторяет пока условие истинно
var count = 0
while (count < 3) {
    println(count)  // Выведет: 0, 1, 2
    count++         // count = count + 1
}
```

---

## 1.4 Условия — принятие решений

```kotlin
// IF-ELSE — выполняет код в зависимости от условия

val age = 18

if (age >= 18) {
    println("Совершеннолетний")
} else {
    println("Несовершеннолетний")
}

// Операторы сравнения:
// ==  равно
// !=  не равно
// <   меньше
// >   больше
// <=  меньше или равно
// >=  больше или равно

// Логические операторы:
// &&  И (оба условия должны быть true)
// ||  ИЛИ (хотя бы одно условие true)
// !   НЕ (инвертирует true<->false)

val x = 5
if (x > 0 && x < 10) {
    println("x между 0 и 10")
}

// WHEN — выбор из нескольких вариантов (как switch)
val grade = 'A'
when (grade) {
    'A' -> println("Отлично")
    'B' -> println("Хорошо")
    'C' -> println("Удовлетворительно")
    else -> println("Неизвестная оценка")
}
```

---

## 1.5 Функции — переиспользуемый код

```kotlin
// ФУНКЦИЯ — блок кода, который можно вызывать по имени

// Простая функция без параметров и возврата:
fun sayHello() {
    println("Привет!")
}
sayHello()  // Вызов функции

// Функция с параметрами:
fun greet(name: String) {
    println("Привет, $name!")
}
greet("Алиса")  // Выведет: Привет, Алиса!

// Функция с возвратом значения:
fun add(a: Int, b: Int): Int {
    return a + b  // Возвращает результат
}
val sum = add(3, 5)  // sum = 8

// Короткая запись для простых функций:
fun multiply(a: Int, b: Int) = a * b  // То же что return a * b

// Функция с значением по умолчанию:
fun power(base: Int, exponent: Int = 2): Int {
    var result = 1
    for (i in 1..exponent) {
        result *= base
    }
    return result
}
power(3)     // = 9 (3^2, exponent по умолчанию = 2)
power(3, 3)  // = 27 (3^3)
```

---

# ЧАСТЬ 2: БАЗОВЫЕ АЛГОРИТМЫ

## 2.1 Поиск максимума в массиве

```kotlin
/**
 * Задача: найти максимальный элемент в массиве
 *
 * Идея: проходим по всем элементам, запоминаем наибольший
 *
 * Временная сложность: O(n) — проходим по каждому элементу один раз
 */
fun findMax(arr: IntArray): Int {
    // Шаг 1: Проверка на пустой массив
    // Если массив пуст, бросаем ошибку (иначе не с чем сравнивать)
    if (arr.isEmpty()) {
        throw IllegalArgumentException("Массив не может быть пустым")
    }

    // Шаг 2: Берём первый элемент как начальный максимум
    // Почему первый? Потому что он точно есть (массив не пустой)
    var max = arr[0]

    // Шаг 3: Проходим по остальным элементам
    // Начинаем с индекса 1, потому что индекс 0 уже учтён в max
    for (i in 1 until arr.size) {
        // Шаг 4: Если текущий элемент больше max, обновляем max
        if (arr[i] > max) {
            max = arr[i]
        }
    }

    // Шаг 5: Возвращаем найденный максимум
    return max
}

// ПОШАГОВЫЙ ПРИМЕР:
// arr = [3, 7, 2, 9, 1]
//
// Начало: max = 3 (первый элемент)
//
// i=1: arr[1]=7, 7 > 3? ДА → max = 7
// i=2: arr[2]=2, 2 > 7? НЕТ → max = 7 (без изменений)
// i=3: arr[3]=9, 9 > 7? ДА → max = 9
// i=4: arr[4]=1, 1 > 9? НЕТ → max = 9
//
// Результат: 9
```

---

## 2.2 Линейный поиск (Linear Search)

```kotlin
/**
 * Задача: найти индекс элемента target в массиве
 *
 * Идея: проверяем каждый элемент по очереди
 *
 * Временная сложность: O(n) — в худшем случае проверим все элементы
 */
fun linearSearch(arr: IntArray, target: Int): Int {
    // Проходим по каждому индексу
    for (i in arr.indices) {
        // Если нашли искомый элемент, возвращаем его индекс
        if (arr[i] == target) {
            return i  // Нашли! Выходим из функции
        }
    }
    // Если дошли сюда — элемент не найден
    return -1  // -1 означает "не найдено"
}

// ПОШАГОВЫЙ ПРИМЕР:
// arr = [4, 2, 7, 1, 9], target = 7
//
// i=0: arr[0]=4, 4 == 7? НЕТ → продолжаем
// i=1: arr[1]=2, 2 == 7? НЕТ → продолжаем
// i=2: arr[2]=7, 7 == 7? ДА → return 2
//
// Результат: 2 (индекс элемента 7)
```

---

## 2.3 Бинарный поиск (Binary Search) — ВАЖНО!

```kotlin
/**
 * Задача: найти элемент в ОТСОРТИРОВАННОМ массиве
 *
 * Идея: каждый раз отбрасываем половину массива
 * 1. Смотрим на средний элемент
 * 2. Если он = target → нашли!
 * 3. Если он > target → ищем в левой половине
 * 4. Если он < target → ищем в правой половине
 *
 * Временная сложность: O(log n) — очень быстро!
 * Для 1 миллиона элементов: ~20 сравнений вместо 1 миллиона
 */
fun binarySearch(arr: IntArray, target: Int): Int {
    // left и right — границы области поиска
    var left = 0              // Левая граница (начало массива)
    var right = arr.size - 1  // Правая граница (конец массива)

    // Пока область поиска не пуста
    while (left <= right) {
        // Находим средний индекс
        // (left + right) / 2 может переполниться, поэтому так:
        val mid = left + (right - left) / 2

        when {
            // Случай 1: нашли искомый элемент
            arr[mid] == target -> return mid

            // Случай 2: средний элемент больше target
            // Значит target находится СЛЕВА от mid
            arr[mid] > target -> right = mid - 1

            // Случай 3: средний элемент меньше target
            // Значит target находится СПРАВА от mid
            else -> left = mid + 1
        }
    }

    // Элемент не найден
    return -1
}

// ПОШАГОВЫЙ ПРИМЕР:
// arr = [1, 3, 5, 7, 9, 11, 13], target = 7
//        0  1  2  3  4  5   6
//
// Шаг 1: left=0, right=6
//        mid = 0 + (6-0)/2 = 3
//        arr[3] = 7
//        7 == 7? ДА → return 3
//
// Результат: 3

// ПРИМЕР когда элемент НЕ в середине:
// arr = [1, 3, 5, 7, 9, 11, 13], target = 11
//
// Шаг 1: left=0, right=6, mid=3
//        arr[3]=7, 7 < 11 → left = 4
//
// Шаг 2: left=4, right=6, mid=5
//        arr[5]=11, 11 == 11? ДА → return 5
```

---

## 2.4 Сортировка пузырьком (Bubble Sort)

```kotlin
/**
 * Задача: отсортировать массив по возрастанию
 *
 * Идея: многократно проходим по массиву,
 *       меняя местами соседние элементы если они в неправильном порядке.
 *       Большие элементы "всплывают" в конец как пузырьки.
 *
 * Временная сложность: O(n²) — медленно для больших массивов
 */
fun bubbleSort(arr: IntArray) {
    val n = arr.size

    // Внешний цикл: сколько раз пройдём по массиву
    // После i-го прохода, i последних элементов уже на месте
    for (i in 0 until n - 1) {

        // Внутренний цикл: проход по массиву
        // n - 1 - i: не проверяем уже отсортированные элементы в конце
        for (j in 0 until n - 1 - i) {

            // Если текущий элемент больше следующего — меняем местами
            if (arr[j] > arr[j + 1]) {
                // Обмен значениями (swap)
                val temp = arr[j]      // Сохраняем arr[j] во временную переменную
                arr[j] = arr[j + 1]    // Записываем arr[j+1] в arr[j]
                arr[j + 1] = temp      // Записываем сохранённое значение в arr[j+1]
            }
        }
    }
}

// ПОШАГОВЫЙ ПРИМЕР:
// arr = [5, 3, 8, 1, 2]
//
// === Проход 1 (i=0) ===
// j=0: [5,3,8,1,2] → 5>3? ДА → swap → [3,5,8,1,2]
// j=1: [3,5,8,1,2] → 5>8? НЕТ
// j=2: [3,5,8,1,2] → 8>1? ДА → swap → [3,5,1,8,2]
// j=3: [3,5,1,8,2] → 8>2? ДА → swap → [3,5,1,2,8]
// После прохода 1: [3,5,1,2,8] — 8 на своём месте!
//
// === Проход 2 (i=1) ===
// j=0: 3>5? НЕТ
// j=1: 5>1? ДА → swap → [3,1,5,2,8]
// j=2: 5>2? ДА → swap → [3,1,2,5,8]
// После прохода 2: [3,1,2,5,8] — 5,8 на местах
//
// === Проход 3 (i=2) ===
// j=0: 3>1? ДА → swap → [1,3,2,5,8]
// j=1: 3>2? ДА → swap → [1,2,3,5,8]
// После прохода 3: [1,2,3,5,8] — отсортировано!
```

---

## 2.5 Сортировка слиянием (Merge Sort) — Divide & Conquer

```kotlin
/**
 * Задача: отсортировать массив
 *
 * Идея (Divide & Conquer — разделяй и властвуй):
 * 1. РАЗДЕЛЯЙ: Делим массив пополам
 * 2. Рекурсивно сортируем обе половины
 * 3. ВЛАСТВУЙ: Сливаем две отсортированные половины в одну
 *
 * Временная сложность: O(n log n) — быстро!
 */
fun mergeSort(arr: IntArray): IntArray {
    // Базовый случай: массив из 0 или 1 элемента уже отсортирован
    if (arr.size <= 1) return arr

    // Шаг 1: Делим массив пополам
    val mid = arr.size / 2

    // arr.sliceArray создаёт новый массив из части исходного
    val left = arr.sliceArray(0 until mid)     // Левая половина
    val right = arr.sliceArray(mid until arr.size)  // Правая половина

    // Шаг 2: Рекурсивно сортируем обе половины
    val sortedLeft = mergeSort(left)
    val sortedRight = mergeSort(right)

    // Шаг 3: Сливаем отсортированные половины
    return merge(sortedLeft, sortedRight)
}

/**
 * Функция слияния двух отсортированных массивов
 */
fun merge(left: IntArray, right: IntArray): IntArray {
    // Результирующий массив
    val result = IntArray(left.size + right.size)

    // Указатели на текущие элементы в left и right
    var i = 0  // Указатель для left
    var j = 0  // Указатель для right
    var k = 0  // Указатель для result

    // Пока есть элементы в обоих массивах
    while (i < left.size && j < right.size) {
        // Берём меньший элемент и кладём в result
        if (left[i] <= right[j]) {
            result[k] = left[i]
            i++  // Двигаем указатель left
        } else {
            result[k] = right[j]
            j++  // Двигаем указатель right
        }
        k++  // Двигаем указатель result
    }

    // Копируем оставшиеся элементы из left (если есть)
    while (i < left.size) {
        result[k] = left[i]
        i++
        k++
    }

    // Копируем оставшиеся элементы из right (если есть)
    while (j < right.size) {
        result[k] = right[j]
        j++
        k++
    }

    return result
}

// ПОШАГОВЫЙ ПРИМЕР:
// arr = [38, 27, 43, 3]
//
// mergeSort([38, 27, 43, 3]):
//   Делим: left=[38,27], right=[43,3]
//
//   mergeSort([38, 27]):
//     Делим: left=[38], right=[27]
//     mergeSort([38]) → [38] (базовый случай)
//     mergeSort([27]) → [27] (базовый случай)
//     merge([38], [27]) → [27, 38]
//
//   mergeSort([43, 3]):
//     Делим: left=[43], right=[3]
//     mergeSort([43]) → [43]
//     mergeSort([3]) → [3]
//     merge([43], [3]) → [3, 43]
//
//   merge([27,38], [3,43]):
//     i=0, j=0: 27 vs 3 → берём 3 → [3,_,_,_]
//     i=0, j=1: 27 vs 43 → берём 27 → [3,27,_,_]
//     i=1, j=1: 38 vs 43 → берём 38 → [3,27,38,_]
//     оставшийся 43 → [3,27,38,43]
//
// Результат: [3, 27, 38, 43]
```

---

# ЧАСТЬ 3: СТРУКТУРЫ ДАННЫХ

## 3.1 Стек (Stack) — LIFO

```kotlin
/**
 * СТЕК — структура данных "последний вошёл — первый вышел" (LIFO)
 *
 * Представьте стопку тарелок:
 * - Новую тарелку кладём СВЕРХУ (push)
 * - Берём тарелку тоже СВЕРХУ (pop)
 *
 * Операции:
 * - push(x): добавить элемент на вершину
 * - pop(): удалить и вернуть элемент с вершины
 * - peek(): посмотреть верхний элемент (не удаляя)
 * - isEmpty(): пустой ли стек?
 */
class Stack<T> {
    // Используем MutableList для хранения элементов
    // Последний элемент списка = вершина стека
    private val items = mutableListOf<T>()

    // Добавить элемент на вершину
    fun push(item: T) {
        items.add(item)  // Добавляем в конец списка
    }

    // Удалить и вернуть элемент с вершины
    fun pop(): T {
        if (isEmpty()) {
            throw NoSuchElementException("Стек пуст")
        }
        return items.removeAt(items.size - 1)  // Удаляем последний
    }

    // Посмотреть верхний элемент (без удаления)
    fun peek(): T {
        if (isEmpty()) {
            throw NoSuchElementException("Стек пуст")
        }
        return items.last()  // Возвращаем последний
    }

    // Проверить, пуст ли стек
    fun isEmpty() = items.isEmpty()

    // Размер стека
    fun size() = items.size
}

// ПРИМЕР ИСПОЛЬЗОВАНИЯ:
val stack = Stack<Int>()
stack.push(1)   // Стек: [1]
stack.push(2)   // Стек: [1, 2]
stack.push(3)   // Стек: [1, 2, 3]

println(stack.peek())  // 3 (верхний элемент)
println(stack.pop())   // 3 (удалили верхний)
// Стек теперь: [1, 2]
println(stack.pop())   // 2
println(stack.pop())   // 1
// Стек теперь пуст

// ПРИМЕНЕНИЕ: Проверка сбалансированности скобок
fun isBalanced(s: String): Boolean {
    val stack = Stack<Char>()

    for (char in s) {
        when (char) {
            '(', '[', '{' -> stack.push(char)  // Открывающая → в стек
            ')' -> {
                if (stack.isEmpty() || stack.pop() != '(') return false
            }
            ']' -> {
                if (stack.isEmpty() || stack.pop() != '[') return false
            }
            '}' -> {
                if (stack.isEmpty() || stack.pop() != '{') return false
            }
        }
    }

    return stack.isEmpty()  // Стек должен быть пуст в конце
}

// isBalanced("({[]})") → true
// isBalanced("([)]") → false
// isBalanced("((") → false
```

---

## 3.2 Очередь (Queue) — FIFO

```kotlin
/**
 * ОЧЕРЕДЬ — структура данных "первый вошёл — первый вышел" (FIFO)
 *
 * Как очередь в магазине:
 * - Новый человек встаёт В КОНЕЦ (enqueue)
 * - Обслуживают того, кто С НАЧАЛА (dequeue)
 *
 * Операции:
 * - enqueue(x): добавить в конец
 * - dequeue(): удалить и вернуть элемент с начала
 * - peek(): посмотреть первый элемент
 * - isEmpty(): пуста ли очередь?
 */
class Queue<T> {
    private val items = mutableListOf<T>()

    // Добавить в конец очереди
    fun enqueue(item: T) {
        items.add(item)
    }

    // Удалить и вернуть первый элемент
    fun dequeue(): T {
        if (isEmpty()) {
            throw NoSuchElementException("Очередь пуста")
        }
        return items.removeAt(0)  // Удаляем первый элемент
    }

    // Посмотреть первый элемент
    fun peek(): T {
        if (isEmpty()) {
            throw NoSuchElementException("Очередь пуста")
        }
        return items.first()
    }

    fun isEmpty() = items.isEmpty()
    fun size() = items.size
}

// ПРИМЕР:
val queue = Queue<Int>()
queue.enqueue(1)   // Очередь: [1]
queue.enqueue(2)   // Очередь: [1, 2]
queue.enqueue(3)   // Очередь: [1, 2, 3]

println(queue.dequeue())  // 1 (первый вышел первым)
// Очередь теперь: [2, 3]
println(queue.dequeue())  // 2
// Очередь теперь: [3]
```

---

## 3.3 Связный список (Linked List)

```kotlin
/**
 * СВЯЗНЫЙ СПИСОК — цепочка узлов, каждый узел содержит:
 * 1. Значение (data)
 * 2. Ссылку на следующий узел (next)
 *
 * Преимущества:
 * - Вставка/удаление в начало за O(1)
 * - Динамический размер
 *
 * Недостатки:
 * - Доступ по индексу за O(n) (нет random access)
 */

// Узел списка
class Node<T>(
    var data: T,           // Значение
    var next: Node<T>? = null  // Ссылка на следующий (null если последний)
)

// Связный список
class LinkedList<T> {
    private var head: Node<T>? = null  // Голова списка (первый элемент)
    private var size = 0

    // Добавить в начало — O(1)
    fun addFirst(data: T) {
        // Создаём новый узел, его next указывает на текущую голову
        val newNode = Node(data, head)
        // Новый узел становится головой
        head = newNode
        size++
    }

    // Добавить в конец — O(n) (нужно дойти до конца)
    fun addLast(data: T) {
        val newNode = Node(data)

        if (head == null) {
            // Список пуст — новый узел становится головой
            head = newNode
        } else {
            // Ищем последний узел
            var current = head
            while (current?.next != null) {
                current = current.next
            }
            // Присоединяем новый узел
            current?.next = newNode
        }
        size++
    }

    // Удалить первый элемент — O(1)
    fun removeFirst(): T? {
        if (head == null) return null

        val data = head!!.data
        head = head!!.next  // Голова теперь указывает на второй элемент
        size--
        return data
    }

    // Найти элемент по значению — O(n)
    fun find(data: T): Node<T>? {
        var current = head
        while (current != null) {
            if (current.data == data) return current
            current = current.next
        }
        return null
    }

    // Вывести все элементы
    fun printAll() {
        var current = head
        while (current != null) {
            print("${current.data} -> ")
            current = current.next
        }
        println("null")
    }
}

// ПРИМЕР:
val list = LinkedList<Int>()
list.addFirst(3)   // 3 -> null
list.addFirst(2)   // 2 -> 3 -> null
list.addFirst(1)   // 1 -> 2 -> 3 -> null
list.addLast(4)    // 1 -> 2 -> 3 -> 4 -> null

list.printAll()    // 1 -> 2 -> 3 -> 4 -> null

list.removeFirst() // 2 -> 3 -> 4 -> null
```

---

# ЧАСТЬ 4: РЕКУРСИЯ И ДИНАМИЧЕСКОЕ ПРОГРАММИРОВАНИЕ

## 4.1 Что такое рекурсия

```kotlin
/**
 * РЕКУРСИЯ — функция, которая вызывает сама себя
 *
 * Обязательные компоненты:
 * 1. Базовый случай — когда остановиться
 * 2. Рекурсивный случай — вызов самой себя с упрощённой задачей
 */

// Пример 1: Факториал (n! = n × (n-1) × (n-2) × ... × 1)
// 5! = 5 × 4 × 3 × 2 × 1 = 120

fun factorial(n: Int): Long {
    // БАЗОВЫЙ СЛУЧАЙ: факториал 0 и 1 равен 1
    if (n <= 1) return 1L

    // РЕКУРСИВНЫЙ СЛУЧАЙ: n! = n × (n-1)!
    return n * factorial(n - 1)
}

// КАК ЭТО РАБОТАЕТ (для n=4):
// factorial(4)
//   → 4 * factorial(3)
//       → 3 * factorial(2)
//           → 2 * factorial(1)
//               → 1 (базовый случай)
//           ← 2 * 1 = 2
//       ← 3 * 2 = 6
//   ← 4 * 6 = 24
// Результат: 24


// Пример 2: Числа Фибоначчи
// F(0)=0, F(1)=1, F(n) = F(n-1) + F(n-2)
// 0, 1, 1, 2, 3, 5, 8, 13, 21, ...

fun fibonacci(n: Int): Long {
    // БАЗОВЫЕ СЛУЧАИ
    if (n == 0) return 0
    if (n == 1) return 1

    // РЕКУРСИВНЫЙ СЛУЧАЙ
    return fibonacci(n - 1) + fibonacci(n - 2)
}

// ПРОБЛЕМА: эта реализация медленная!
// fibonacci(5) вызывает fibonacci(4) и fibonacci(3)
// fibonacci(4) вызывает fibonacci(3) и fibonacci(2)
// fibonacci(3) считается ДВАЖДЫ!
//
// Решение: МЕМОИЗАЦИЯ или ДИНАМИЧЕСКОЕ ПРОГРАММИРОВАНИЕ
```

---

## 4.2 Динамическое программирование (DP) — основы

```kotlin
/**
 * ДИНАМИЧЕСКОЕ ПРОГРАММИРОВАНИЕ — метод решения задач через:
 * 1. Разбиение на подзадачи
 * 2. Сохранение результатов подзадач (чтобы не считать дважды)
 * 3. Использование сохранённых результатов
 *
 * Два подхода:
 * - Top-down (сверху вниз) + мемоизация
 * - Bottom-up (снизу вверх) + таблица
 */

// Фибоначчи с мемоизацией (Top-down)
fun fibonacciMemo(n: Int, memo: MutableMap<Int, Long> = mutableMapOf()): Long {
    // Проверяем, есть ли уже вычисленное значение
    if (n in memo) return memo[n]!!

    // Базовые случаи
    if (n <= 1) return n.toLong()

    // Вычисляем и СОХРАНЯЕМ результат
    val result = fibonacciMemo(n - 1, memo) + fibonacciMemo(n - 2, memo)
    memo[n] = result

    return result
}


// Фибоначчи с таблицей (Bottom-up) — РЕКОМЕНДУЕТСЯ
fun fibonacciDP(n: Int): Long {
    if (n <= 1) return n.toLong()

    // Создаём массив для хранения результатов
    val dp = LongArray(n + 1)

    // Базовые случаи
    dp[0] = 0
    dp[1] = 1

    // Заполняем таблицу снизу вверх
    for (i in 2..n) {
        dp[i] = dp[i - 1] + dp[i - 2]
    }

    return dp[n]
}

// ПОШАГОВЫЙ ПРИМЕР для n=6:
// dp = [0, 0, 0, 0, 0, 0, 0]  (начальное состояние)
// dp = [0, 1, 0, 0, 0, 0, 0]  (базовые случаи)
//
// i=2: dp[2] = dp[1] + dp[0] = 1 + 0 = 1  → [0, 1, 1, 0, 0, 0, 0]
// i=3: dp[3] = dp[2] + dp[1] = 1 + 1 = 2  → [0, 1, 1, 2, 0, 0, 0]
// i=4: dp[4] = dp[3] + dp[2] = 2 + 1 = 3  → [0, 1, 1, 2, 3, 0, 0]
// i=5: dp[5] = dp[4] + dp[3] = 3 + 2 = 5  → [0, 1, 1, 2, 3, 5, 0]
// i=6: dp[6] = dp[5] + dp[4] = 5 + 3 = 8  → [0, 1, 1, 2, 3, 5, 8]
//
// Результат: dp[6] = 8


// Оптимизация по памяти: O(1) вместо O(n)
fun fibonacciOptimized(n: Int): Long {
    if (n <= 1) return n.toLong()

    var prev2 = 0L  // F(i-2)
    var prev1 = 1L  // F(i-1)

    for (i in 2..n) {
        val current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    }

    return prev1
}
```

---

## 4.3 Классическая DP задача: Рюкзак (Knapsack)

```kotlin
/**
 * ЗАДАЧА О РЮКЗАКЕ:
 * Есть N предметов, каждый с весом weight[i] и ценностью value[i].
 * Рюкзак вмещает максимум W единиц веса.
 * Найти максимальную суммарную ценность, которую можно унести.
 *
 * Пример:
 * Предметы: [(вес=1, ценность=6), (вес=2, ценность=10), (вес=3, ценность=12)]
 * Вместимость: W=5
 * Ответ: 22 (берём предметы 1 и 3: вес=1+3=4≤5, ценность=6+12=18)
 *        Или предметы 2 и 3: вес=2+3=5≤5, ценность=10+12=22 ✓
 */
fun knapsack(weights: IntArray, values: IntArray, capacity: Int): Int {
    val n = weights.size

    // dp[i][w] = максимальная ценность, которую можно получить
    //            используя первые i предметов
    //            с рюкзаком вместимостью w
    val dp = Array(n + 1) { IntArray(capacity + 1) }

    // Заполняем таблицу
    for (i in 1..n) {
        for (w in 0..capacity) {
            // Вариант 1: НЕ берём предмет i
            // Тогда результат такой же, как без этого предмета
            dp[i][w] = dp[i - 1][w]

            // Вариант 2: Берём предмет i (если он влезает)
            val itemWeight = weights[i - 1]  // Вес текущего предмета
            val itemValue = values[i - 1]    // Ценность текущего предмета

            if (itemWeight <= w) {
                // Если берём предмет, добавляем его ценность
                // и смотрим что можно добавить с оставшимся местом
                val takeItem = dp[i - 1][w - itemWeight] + itemValue

                // Выбираем лучший вариант
                dp[i][w] = maxOf(dp[i][w], takeItem)
            }
        }
    }

    return dp[n][capacity]
}

// ПОШАГОВЫЙ ПРИМЕР:
// weights = [1, 2, 3], values = [6, 10, 12], capacity = 5
//
// Таблица dp (строки = предметы, столбцы = вместимость):
//
//        w=0  w=1  w=2  w=3  w=4  w=5
// i=0     0    0    0    0    0    0   (нет предметов)
// i=1     0    6    6    6    6    6   (только предмет 1: вес=1, ценность=6)
// i=2     0    6   10   16   16   16   (предметы 1,2)
// i=3     0    6   10   16   18   22   (все предметы)
//
// Ответ: dp[3][5] = 22
```

---

# ЧАСТЬ 5: ГРАФЫ

## 5.1 Что такое граф

```kotlin
/**
 * ГРАФ — это набор вершин (узлов) и рёбер (связей между вершинами)
 *
 * Примеры из жизни:
 * - Карта городов: города = вершины, дороги = рёбра
 * - Социальная сеть: люди = вершины, дружба = рёбра
 * - Веб-страницы: страницы = вершины, ссылки = рёбра
 *
 * Типы графов:
 * - Ориентированный: рёбра имеют направление (A→B ≠ B→A)
 * - Неориентированный: рёбра двусторонние (A-B = B-A)
 * - Взвешенный: рёбра имеют вес (расстояние, стоимость)
 */

// ПРЕДСТАВЛЕНИЕ ГРАФА

// Способ 1: Список смежности (adjacency list) — РЕКОМЕНДУЕТСЯ
// Для каждой вершины храним список соседей
// Память: O(V + E), где V = вершины, E = рёбра

// Пример графа:
//   0 --- 1
//   |     |
//   2 --- 3

// Представление:
// 0: [1, 2]     — вершина 0 соединена с 1 и 2
// 1: [0, 3]     — вершина 1 соединена с 0 и 3
// 2: [0, 3]     — вершина 2 соединена с 0 и 3
// 3: [1, 2]     — вершина 3 соединена с 1 и 2

fun createGraph(n: Int, edges: List<Pair<Int, Int>>): Array<MutableList<Int>> {
    // Создаём массив из n пустых списков
    val graph = Array(n) { mutableListOf<Int>() }

    // Добавляем рёбра
    for ((u, v) in edges) {
        graph[u].add(v)  // Ребро u → v
        graph[v].add(u)  // Ребро v → u (для неориентированного графа)
    }

    return graph
}

// Использование:
val n = 4
val edges = listOf(Pair(0, 1), Pair(0, 2), Pair(1, 3), Pair(2, 3))
val graph = createGraph(n, edges)
// graph[0] = [1, 2]
// graph[1] = [0, 3]
// graph[2] = [0, 3]
// graph[3] = [1, 2]


// Способ 2: Матрица смежности (adjacency matrix)
// matrix[i][j] = 1 если есть ребро между i и j, иначе 0
// Память: O(V²) — много для больших графов с малым числом рёбер

fun createAdjMatrix(n: Int, edges: List<Pair<Int, Int>>): Array<IntArray> {
    val matrix = Array(n) { IntArray(n) }

    for ((u, v) in edges) {
        matrix[u][v] = 1
        matrix[v][u] = 1
    }

    return matrix
}
```

---

## 5.2 Обход графа в глубину (DFS)

```kotlin
/**
 * DFS (Depth-First Search) — обход в глубину
 *
 * Идея: идём как можно глубже, пока можем, потом возвращаемся
 *
 * Аналогия: исследование лабиринта — идём по коридору до тупика,
 *           потом возвращаемся и пробуем другой путь
 *
 * Применение:
 * - Поиск пути
 * - Проверка связности
 * - Топологическая сортировка
 * - Поиск циклов
 */

// DFS рекурсивный
fun dfs(graph: Array<MutableList<Int>>, start: Int, visited: BooleanArray) {
    // Помечаем текущую вершину как посещённую
    visited[start] = true
    println("Посетили вершину $start")

    // Проходим по всем соседям
    for (neighbor in graph[start]) {
        // Если сосед ещё не посещён — идём в него
        if (!visited[neighbor]) {
            dfs(graph, neighbor, visited)
        }
    }
}

// Использование:
// val visited = BooleanArray(n)
// dfs(graph, 0, visited)

// ПОШАГОВЫЙ ПРИМЕР для графа:
//   0 --- 1
//   |     |
//   2 --- 3
//
// Начинаем с вершины 0:
// dfs(0): visited[0]=true, соседи=[1,2]
//   → dfs(1): visited[1]=true, соседи=[0,3]
//       0 уже посещён (пропускаем)
//       → dfs(3): visited[3]=true, соседи=[1,2]
//           1 уже посещён (пропускаем)
//           → dfs(2): visited[2]=true, соседи=[0,3]
//               0 уже посещён (пропускаем)
//               3 уже посещён (пропускаем)
//           ← возврат из 2
//       ← возврат из 3
//   ← возврат из 1
//   2 уже посещён (пропускаем)
// ← возврат из 0
//
// Порядок посещения: 0 → 1 → 3 → 2


// DFS итеративный (с использованием стека)
fun dfsIterative(graph: Array<MutableList<Int>>, start: Int): List<Int> {
    val visited = BooleanArray(graph.size)
    val result = mutableListOf<Int>()
    val stack = ArrayDeque<Int>()

    stack.addLast(start)

    while (stack.isNotEmpty()) {
        val current = stack.removeLast()

        if (visited[current]) continue
        visited[current] = true
        result.add(current)

        // Добавляем соседей в стек (в обратном порядке для того же порядка что рекурсия)
        for (neighbor in graph[current].reversed()) {
            if (!visited[neighbor]) {
                stack.addLast(neighbor)
            }
        }
    }

    return result
}
```

---

## 5.3 Обход графа в ширину (BFS)

```kotlin
/**
 * BFS (Breadth-First Search) — обход в ширину
 *
 * Идея: сначала посещаем всех соседей, потом соседей соседей и т.д.
 *       Как волна, расходящаяся от камня, брошенного в воду.
 *
 * Использует ОЧЕРЕДЬ (FIFO)
 *
 * Применение:
 * - Кратчайший путь в невзвешенном графе
 * - Уровни в дереве
 * - Поиск ближайшего объекта
 */

fun bfs(graph: Array<MutableList<Int>>, start: Int): List<Int> {
    val visited = BooleanArray(graph.size)
    val result = mutableListOf<Int>()
    val queue = ArrayDeque<Int>()

    // Начинаем с начальной вершины
    queue.addLast(start)
    visited[start] = true

    while (queue.isNotEmpty()) {
        // Берём вершину из начала очереди
        val current = queue.removeFirst()
        result.add(current)

        // Добавляем всех непосещённых соседей в конец очереди
        for (neighbor in graph[current]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.addLast(neighbor)
            }
        }
    }

    return result
}

// ПОШАГОВЫЙ ПРИМЕР для графа:
//   0 --- 1
//   |     |
//   2 --- 3
//
// Начинаем с вершины 0:
//
// Шаг 1: queue=[0], visited=[T,F,F,F]
//        current=0, добавляем соседей 1,2
//        queue=[1,2], result=[0]
//
// Шаг 2: queue=[1,2], visited=[T,T,T,F]
//        current=1, добавляем сосед 3 (0 уже посещён)
//        queue=[2,3], result=[0,1]
//
// Шаг 3: queue=[2,3], visited=[T,T,T,T]
//        current=2, сосед 3 добавляем (0 уже посещён)
//        Но 3 уже в очереди! (visited[3]=true после предыдущего шага)
//        queue=[3], result=[0,1,2]
//
// Шаг 4: queue=[3], visited=[T,T,T,T]
//        current=3, все соседи уже посещены
//        queue=[], result=[0,1,2,3]
//
// Порядок посещения: 0 → 1 → 2 → 3 (по уровням)


// Кратчайший путь в невзвешенном графе
fun shortestPath(graph: Array<MutableList<Int>>, start: Int, end: Int): List<Int> {
    val visited = BooleanArray(graph.size)
    val parent = IntArray(graph.size) { -1 }  // Для восстановления пути
    val queue = ArrayDeque<Int>()

    queue.addLast(start)
    visited[start] = true

    while (queue.isNotEmpty()) {
        val current = queue.removeFirst()

        if (current == end) {
            // Нашли! Восстанавливаем путь
            val path = mutableListOf<Int>()
            var node = end
            while (node != -1) {
                path.add(0, node)  // Добавляем в начало
                node = parent[node]
            }
            return path
        }

        for (neighbor in graph[current]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                parent[neighbor] = current  // Запоминаем откуда пришли
                queue.addLast(neighbor)
            }
        }
    }

    return emptyList()  // Путь не найден
}
```

---

## 5.4 Алгоритм Дейкстры (кратчайший путь во взвешенном графе)

```kotlin
/**
 * Алгоритм ДЕЙКСТРЫ — находит кратчайшие пути от одной вершины до всех остальных
 *                     во взвешенном графе с НЕОТРИЦАТЕЛЬНЫМИ весами
 *
 * Идея:
 * 1. Начинаем с расстояния 0 до начальной вершины, ∞ до остальных
 * 2. Выбираем непосещённую вершину с минимальным расстоянием
 * 3. Обновляем расстояния до её соседей
 * 4. Повторяем пока не обработаем все вершины
 *
 * Временная сложность: O((V + E) log V) с приоритетной очередью
 */

// Ребро с весом
data class Edge(val to: Int, val weight: Int)

fun dijkstra(graph: Array<MutableList<Edge>>, start: Int): IntArray {
    val n = graph.size

    // dist[v] = кратчайшее расстояние от start до v
    val dist = IntArray(n) { Int.MAX_VALUE }
    dist[start] = 0

    // Приоритетная очередь: пары (расстояние, вершина)
    // Сортирует по расстоянию — минимальное первым
    val pq = java.util.PriorityQueue<Pair<Int, Int>>(compareBy { it.first })
    pq.add(Pair(0, start))

    while (pq.isNotEmpty()) {
        // Берём вершину с минимальным расстоянием
        val (d, u) = pq.poll()

        // Если уже нашли более короткий путь — пропускаем
        if (d > dist[u]) continue

        // Обновляем расстояния до соседей
        for (edge in graph[u]) {
            val v = edge.to
            val newDist = dist[u] + edge.weight

            // Если нашли более короткий путь
            if (newDist < dist[v]) {
                dist[v] = newDist
                pq.add(Pair(newDist, v))
            }
        }
    }

    return dist
}

// ПОШАГОВЫЙ ПРИМЕР:
// Граф:
//     1
//  0 ----→ 1
//  |       |
// 4|       |2
//  ↓       ↓
//  2 ----→ 3
//     1
//
// graph[0] = [(to=1, w=1), (to=2, w=4)]
// graph[1] = [(to=3, w=2)]
// graph[2] = [(to=3, w=1)]
// graph[3] = []
//
// Начинаем с вершины 0:
// dist = [0, ∞, ∞, ∞], pq = [(0,0)]
//
// Шаг 1: Берём (0,0), обрабатываем вершину 0
//   Сосед 1: dist[1] = min(∞, 0+1) = 1, pq += (1,1)
//   Сосед 2: dist[2] = min(∞, 0+4) = 4, pq += (4,2)
//   dist = [0, 1, 4, ∞], pq = [(1,1), (4,2)]
//
// Шаг 2: Берём (1,1), обрабатываем вершину 1
//   Сосед 3: dist[3] = min(∞, 1+2) = 3, pq += (3,3)
//   dist = [0, 1, 4, 3], pq = [(3,3), (4,2)]
//
// Шаг 3: Берём (3,3), обрабатываем вершину 3
//   Нет соседей
//   dist = [0, 1, 4, 3], pq = [(4,2)]
//
// Шаг 4: Берём (4,2), обрабатываем вершину 2
//   Сосед 3: dist[3] = min(3, 4+1) = 3 (не обновляем, уже лучше)
//   dist = [0, 1, 4, 3]
//
// Результат: dist = [0, 1, 4, 3]
// От 0 до 1: 1, от 0 до 2: 4, от 0 до 3: 3
```

---

# ЧАСТЬ 6: ПРОДВИНУТЫЕ СТРУКТУРЫ ДАННЫХ

## 6.1 Дерево отрезков (Segment Tree)

```kotlin
/**
 * ДЕРЕВО ОТРЕЗКОВ (Segment Tree) — структура данных для:
 * 1. Range queries (запросы на отрезке): сумма, минимум, максимум и т.д.
 * 2. Point/Range updates: изменение элементов
 *
 * Временная сложность:
 * - Построение: O(n)
 * - Запрос/обновление: O(log n)
 *
 * Идея: строим бинарное дерево, где каждый узел хранит информацию
 *       о своём отрезке массива
 */

class SegmentTree(private val arr: IntArray) {
    private val n = arr.size
    // Размер дерева: 4*n достаточно для любого n
    private val tree = IntArray(4 * n)

    init {
        // Строим дерево
        build(0, 0, n - 1)
    }

    /**
     * Строит дерево рекурсивно
     *
     * @param v - индекс текущего узла в массиве tree
     * @param tl - левая граница отрезка, за который отвечает узел
     * @param tr - правая граница отрезка
     */
    private fun build(v: Int, tl: Int, tr: Int) {
        // БАЗОВЫЙ СЛУЧАЙ: отрезок из одного элемента
        if (tl == tr) {
            tree[v] = arr[tl]
            return
        }

        // РЕКУРСИВНЫЙ СЛУЧАЙ: делим отрезок пополам
        val tm = (tl + tr) / 2

        // Левый ребёнок: узел 2*v+1, отвечает за [tl, tm]
        build(2 * v + 1, tl, tm)

        // Правый ребёнок: узел 2*v+2, отвечает за [tm+1, tr]
        build(2 * v + 2, tm + 1, tr)

        // Значение в текущем узле = сумма детей
        tree[v] = tree[2 * v + 1] + tree[2 * v + 2]
    }

    /**
     * Запрос суммы на отрезке [l, r]
     */
    fun query(l: Int, r: Int): Int {
        return query(0, 0, n - 1, l, r)
    }

    private fun query(v: Int, tl: Int, tr: Int, l: Int, r: Int): Int {
        // СЛУЧАЙ 1: отрезок [l,r] не пересекается с [tl,tr]
        if (l > tr || r < tl) {
            return 0  // Нейтральный элемент для суммы
        }

        // СЛУЧАЙ 2: отрезок [tl,tr] полностью внутри [l,r]
        if (l <= tl && tr <= r) {
            return tree[v]
        }

        // СЛУЧАЙ 3: частичное пересечение — спрашиваем детей
        val tm = (tl + tr) / 2
        val leftSum = query(2 * v + 1, tl, tm, l, r)
        val rightSum = query(2 * v + 2, tm + 1, tr, l, r)

        return leftSum + rightSum
    }

    /**
     * Обновление: arr[pos] = value
     */
    fun update(pos: Int, value: Int) {
        update(0, 0, n - 1, pos, value)
    }

    private fun update(v: Int, tl: Int, tr: Int, pos: Int, value: Int) {
        // БАЗОВЫЙ СЛУЧАЙ: дошли до листа
        if (tl == tr) {
            tree[v] = value
            return
        }

        // Определяем, в какого ребёнка идти
        val tm = (tl + tr) / 2

        if (pos <= tm) {
            // pos в левой половине
            update(2 * v + 1, tl, tm, pos, value)
        } else {
            // pos в правой половине
            update(2 * v + 2, tm + 1, tr, pos, value)
        }

        // Пересчитываем значение узла
        tree[v] = tree[2 * v + 1] + tree[2 * v + 2]
    }
}

// ВИЗУАЛИЗАЦИЯ для arr = [1, 3, 5, 7, 9, 11]
//
//                    [36]              <- сумма всего массива
//                   /    \
//              [9]          [27]       <- суммы половин
//             /   \        /    \
//          [4]   [5]    [16]   [11]    <- суммы четвертей
//         / \           /  \
//       [1] [3]       [7]  [9]         <- отдельные элементы
//
// query(1, 4) = сумма arr[1..4] = 3+5+7+9 = 24
// update(2, 10) → arr[2]=10, пересчитываем путь до корня
```

---

## 6.2 Система непересекающихся множеств (DSU)

```kotlin
/**
 * DSU (Disjoint Set Union) / Union-Find
 *
 * Поддерживает множества элементов и две операции:
 * 1. find(x) — найти представителя множества, содержащего x
 * 2. union(x, y) — объединить множества, содержащие x и y
 *
 * Применение:
 * - Проверка связности графа
 * - Алгоритм Краскала (MST)
 * - Группировка элементов
 *
 * Временная сложность: O(α(n)) ≈ O(1) на операцию
 * α(n) — обратная функция Аккермана, растёт очень медленно
 */

class DSU(n: Int) {
    // parent[i] = родитель элемента i (или сам i, если он корень)
    private val parent = IntArray(n) { it }  // Изначально каждый сам себе родитель

    // rank[i] = "ранг" дерева с корнем i (для балансировки)
    private val rank = IntArray(n) { 0 }

    /**
     * Найти представителя (корень) множества, содержащего x
     *
     * СЖАТИЕ ПУТЕЙ: при поиске корня, все пройденные элементы
     * напрямую подвешиваются к корню — ускоряет будущие запросы
     */
    fun find(x: Int): Int {
        if (parent[x] != x) {
            // x не корень — ищем корень рекурсивно
            parent[x] = find(parent[x])  // Сжатие пути
        }
        return parent[x]
    }

    /**
     * Объединить множества, содержащие x и y
     *
     * ОБЪЕДИНЕНИЕ ПО РАНГУ: меньшее дерево подвешиваем к большему
     * Это сохраняет дерево плоским
     *
     * @return true если множества были разными и объединены
     */
    fun union(x: Int, y: Int): Boolean {
        val px = find(x)  // Корень множества x
        val py = find(y)  // Корень множества y

        // Уже в одном множестве
        if (px == py) return false

        // Подвешиваем дерево с меньшим рангом к дереву с большим
        when {
            rank[px] < rank[py] -> parent[px] = py
            rank[px] > rank[py] -> parent[py] = px
            else -> {
                // Ранги равны — выбираем произвольно и увеличиваем ранг
                parent[py] = px
                rank[px]++
            }
        }
        return true
    }

    /**
     * Проверить, находятся ли x и y в одном множестве
     */
    fun connected(x: Int, y: Int): Boolean {
        return find(x) == find(y)
    }
}

// ПОШАГОВЫЙ ПРИМЕР:
// n = 5 (элементы 0, 1, 2, 3, 4)
// Начало: каждый в своём множестве
// parent = [0, 1, 2, 3, 4]
// rank   = [0, 0, 0, 0, 0]
//
// union(0, 1):
//   find(0) = 0, find(1) = 1
//   rank[0] == rank[1] → parent[1] = 0, rank[0]++
//   parent = [0, 0, 2, 3, 4]
//   rank   = [1, 0, 0, 0, 0]
//
//   Визуально:
//   0       2  3  4
//   |
//   1
//
// union(2, 3):
//   find(2) = 2, find(3) = 3
//   parent[3] = 2, rank[2]++
//   parent = [0, 0, 2, 2, 4]
//
//   Визуально:
//   0    2    4
//   |    |
//   1    3
//
// union(0, 3):
//   find(0) = 0, find(3) = 2
//   rank[0] == rank[2] → parent[2] = 0, rank[0]++
//   parent = [0, 0, 0, 2, 4]
//
//   Визуально:
//     0       4
//    / \
//   1   2
//       |
//       3
//
// connected(1, 3)?
//   find(1) = 0, find(3) = 0 (через 2)
//   0 == 0 → true, они в одном множестве!
```

---

# ЧАСТЬ 7: ПОЛЕЗНЫЕ ПАТТЕРНЫ

## 7.1 Два указателя (Two Pointers)

```kotlin
/**
 * ДВА УКАЗАТЕЛЯ — техника для обработки массивов с линейной сложностью
 *
 * Идея: два указателя движутся по массиву, но не произвольно,
 *       а монотонно (только вперёд или с разных концов к центру)
 *
 * Применение:
 * - Поиск пары с заданной суммой в отсортированном массиве
 * - Удаление дубликатов
 * - Слияние отсортированных массивов
 */

// Задача: найти пару чисел с суммой target в ОТСОРТИРОВАННОМ массиве
fun twoSum(arr: IntArray, target: Int): Pair<Int, Int>? {
    var left = 0
    var right = arr.size - 1

    while (left < right) {
        val sum = arr[left] + arr[right]

        when {
            sum == target -> return Pair(left, right)
            sum < target -> left++   // Нужна сумма больше — двигаем left
            else -> right--          // Нужна сумма меньше — двигаем right
        }
    }

    return null  // Не нашли
}

// ПОШАГОВЫЙ ПРИМЕР:
// arr = [1, 2, 4, 6, 8, 9], target = 10
//
// left=0, right=5: arr[0]+arr[5] = 1+9 = 10 == target → найдено!
//
// Другой пример: target = 12
// left=0, right=5: 1+9 = 10 < 12 → left++
// left=1, right=5: 2+9 = 11 < 12 → left++
// left=2, right=5: 4+9 = 13 > 12 → right--
// left=2, right=4: 4+8 = 12 == target → найдено!
```

---

## 7.2 Скользящее окно (Sliding Window)

```kotlin
/**
 * СКОЛЬЗЯЩЕЕ ОКНО — техника для обработки подмассивов фиксированного
 *                   или переменного размера
 *
 * Идея: поддерживаем "окно" — непрерывный подмассив,
 *       двигаем его границы и обновляем агрегат (сумму, макс и т.д.)
 */

// Задача: найти максимальную сумму подмассива длины k
fun maxSumSubarray(arr: IntArray, k: Int): Int {
    if (arr.size < k) return 0

    // Вычисляем сумму первого окна
    var windowSum = 0
    for (i in 0 until k) {
        windowSum += arr[i]
    }

    var maxSum = windowSum

    // Двигаем окно вправо
    for (i in k until arr.size) {
        // Добавляем новый элемент справа
        windowSum += arr[i]
        // Убираем старый элемент слева
        windowSum -= arr[i - k]

        maxSum = maxOf(maxSum, windowSum)
    }

    return maxSum
}

// ПОШАГОВЫЙ ПРИМЕР:
// arr = [2, 1, 5, 1, 3, 2], k = 3
//
// Первое окно [2, 1, 5]: sum = 8, maxSum = 8
//
// Сдвиг 1: [1, 5, 1]
//   windowSum = 8 + 1 - 2 = 7
//   maxSum = max(8, 7) = 8
//
// Сдвиг 2: [5, 1, 3]
//   windowSum = 7 + 3 - 1 = 9
//   maxSum = max(8, 9) = 9
//
// Сдвиг 3: [1, 3, 2]
//   windowSum = 9 + 2 - 5 = 6
//   maxSum = max(9, 6) = 9
//
// Результат: 9


// Задача со скользящим окном переменного размера:
// Найти минимальную длину подмассива с суммой >= target
fun minSubArrayLen(target: Int, arr: IntArray): Int {
    var left = 0
    var sum = 0
    var minLen = Int.MAX_VALUE

    for (right in arr.indices) {
        // Расширяем окно вправо
        sum += arr[right]

        // Сжимаем окно слева, пока сумма >= target
        while (sum >= target) {
            minLen = minOf(minLen, right - left + 1)
            sum -= arr[left]
            left++
        }
    }

    return if (minLen == Int.MAX_VALUE) 0 else minLen
}
```

---

## 7.3 Префиксные суммы (Prefix Sum)

```kotlin
/**
 * ПРЕФИКСНЫЕ СУММЫ — предподсчёт для быстрых range sum queries
 *
 * prefix[i] = сумма arr[0] + arr[1] + ... + arr[i-1]
 *
 * Сумма на отрезке [l, r] = prefix[r+1] - prefix[l]
 *
 * Временная сложность:
 * - Предподсчёт: O(n)
 * - Запрос: O(1)
 */

fun buildPrefixSum(arr: IntArray): LongArray {
    val n = arr.size
    // prefix[0] = 0, prefix[1] = arr[0], prefix[2] = arr[0]+arr[1], ...
    val prefix = LongArray(n + 1)

    for (i in arr.indices) {
        prefix[i + 1] = prefix[i] + arr[i]
    }

    return prefix
}

// Сумма на отрезке [l, r] (включительно)
fun rangeSum(prefix: LongArray, l: Int, r: Int): Long {
    return prefix[r + 1] - prefix[l]
}

// ПРИМЕР:
// arr    = [3, 1, 4, 1, 5, 9, 2, 6]
// prefix = [0, 3, 4, 8, 9, 14, 23, 25, 31]
//
// Сумма [2, 5] = prefix[6] - prefix[2] = 23 - 4 = 19
// Проверка: arr[2]+arr[3]+arr[4]+arr[5] = 4+1+5+9 = 19 ✓


// 2D Prefix Sum (для матриц)
fun build2DPrefixSum(matrix: Array<IntArray>): Array<LongArray> {
    val n = matrix.size
    val m = matrix[0].size
    val prefix = Array(n + 1) { LongArray(m + 1) }

    for (i in 1..n) {
        for (j in 1..m) {
            prefix[i][j] = matrix[i-1][j-1].toLong() +
                           prefix[i-1][j] +
                           prefix[i][j-1] -
                           prefix[i-1][j-1]
        }
    }

    return prefix
}

// Сумма в прямоугольнике (r1,c1) - (r2,c2)
fun rectSum(prefix: Array<LongArray>, r1: Int, c1: Int, r2: Int, c2: Int): Long {
    return prefix[r2+1][c2+1] -
           prefix[r1][c2+1] -
           prefix[r2+1][c1] +
           prefix[r1][c1]
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Нужно знать много алгоритмов" | Для начала достаточно **10-15 базовых техник**. Остальное строится на них |
| "Быстрый код = правильный код" | Сначала **корректность**, потом оптимизация. Premature optimization — корень зла |
| "Рекурсия медленная" | Рекурсия может быть **быстрее** итерации (DFS на стеке vs explicit stack). JIT оптимизирует |
| "Brute force — плохо" | Brute force — **первый шаг**. Даёт правильный ответ для проверки оптимизированного решения |
| "Нужно сразу писать оптимально" | Начни с **простого решения**, оптимизируй только если TLE. Часто простое работает |

---

## CS-фундамент

| CS-концепция | Применение в алгоритмах |
|--------------|------------------------|
| **Big O Notation** | n≤10⁵ → O(n log n) OK, n≤10⁷ → O(n) нужен. Оценка feasibility |
| **Recursion** | База + рекуррентное соотношение. Мышление сверху вниз (top-down) |
| **Iteration** | Явные циклы. Мышление снизу вверх (bottom-up). Часто эффективнее по памяти |
| **Data Structures** | Array O(1) access, HashMap O(1) avg lookup, Heap O(log n) extract-min |
| **Problem Decomposition** | Разбиение задачи на подзадачи. Ключ к решению complex problems |

---

# ЗАКЛЮЧЕНИЕ

## Что дальше?

1. **Практика** — решайте задачи на Codeforces, LeetCode, CSES
2. **Углубление** — изучайте advanced темы (Segment Tree с lazy, Flows, FFT)
3. **Upsolving** — разбирайте задачи после контестов
4. **Шаблоны** — подготовьте свои templates для контестов

## Ключевые сложности для запоминания

| Алгоритм | Время | Пространство |
|----------|-------|--------------|
| Binary Search | O(log n) | O(1) |
| Merge Sort | O(n log n) | O(n) |
| DFS/BFS | O(V + E) | O(V) |
| Dijkstra | O((V+E) log V) | O(V) |
| Segment Tree | O(log n) query | O(n) |
| DSU | O(α(n)) ≈ O(1) | O(n) |
| Two Pointers | O(n) | O(1) |
| Prefix Sum | O(1) query | O(n) |

## Главные принципы

1. **Понимай, не заучивай** — понимание > запоминание
2. **Начинай с простого** — сначала brute force, потом оптимизация
3. **Проверяй на примерах** — трейси алгоритм вручную
4. **Тестируй edge cases** — n=0, n=1, максимальные значения
5. **Не бойся ошибок** — они часть обучения

---

*Последнее обновление: 2026-01-09 — Проверено, соответствует педагогическому стандарту*
