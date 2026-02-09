---
title: "Дерево Фенвика (Binary Indexed Tree)"
created: 2026-02-09
modified: 2026-02-09
type: deep-dive
status: published
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/advanced
related:
  - "[[segment-tree]]"
  - "[[sparse-table]]"
---

# Fenwick Tree (Binary Indexed Tree)

## TL;DR

Fenwick Tree (BIT) — структура для prefix sum queries и point updates за O(log n). **Проще и быстрее** Segment Tree для этих задач. Использует LSB (least significant bit) арифметику. Требует только O(n) памяти. Код: 8-10 строк.

---

## Интуиция

### Аналогия 1: BIT как многоуровневая агрегация

```
БИБЛИОТЕКА С МНОГОУРОВНЕВЫМИ КАТАЛОГАМИ:

Уровень 3 (8 книг):  [████████] Каталог всех книг 1-8
Уровень 2 (4 книги): [████]     Каталоги 1-4, 5-8
Уровень 1 (2 книги): [██]       Каталоги 1-2, 3-4, 5-6, 7-8
Уровень 0 (1 книга): [█]        Отдельные книги

"Сколько книг с 1 по 6?"
→ Берём: каталог[1-4] + каталог[5-6] = 2 обращения = O(log n)

Fenwick Tree делает то же самое с помощью LSB-арифметики!
```

### Аналогия 2: LSB как "шаг назад"

```
ВЫЧИСЛЕНИЕ СУММЫ [1..i]:
i = 11 = 1011₂

Шаг 1: bit[11] (элементы 11)      LSB(11)=1, 11-1=10
Шаг 2: bit[10] (элементы 9-10)    LSB(10)=2, 10-2=8
Шаг 3: bit[8]  (элементы 1-8)     LSB(8)=8, 8-8=0
Готово!

Каждый шаг "отщипывает" LSB → O(log n) шагов
```

---

## Частые ошибки

### Ошибка 1: 0-indexed вместо 1-indexed

**СИМПТОМ:** Бесконечный цикл или неверные суммы

```kotlin
// НЕПРАВИЛЬНО: bit[0] нарушает LSB логику
for (i in index downTo 0) { ... }  // LSB(0) = 0 → бесконечный цикл!

// ПРАВИЛЬНО: 1-indexed массив
for (i in index downTo 1 step { i - (i and -i) }) { ... }
```

### Ошибка 2: Range sum через два prefix sum без +1

**СИМПТОМ:** Ответ меньше на один элемент

```kotlin
// НЕПРАВИЛЬНО:
fun rangeSum(l: Int, r: Int) = prefixSum(r) - prefixSum(l)  // l не включён!

// ПРАВИЛЬНО:
fun rangeSum(l: Int, r: Int) = prefixSum(r) - prefixSum(l - 1)  // [l, r]
```

### Ошибка 3: Update вместо Add

**СИМПТОМ:** Сумма содержит старые значения

```kotlin
// НЕПРАВИЛЬНО: "установить arr[i] = val"
fun set(i: Int, val: Int) = add(i, val)  // добавляет, не заменяет!

// ПРАВИЛЬНО: сначала вычесть старое
fun set(i: Int, val: Int) {
    val diff = val - arr[i]
    arr[i] = val
    add(i, diff)
}
```

---

## Ментальные модели

### Модель 1: "LSB определяет ответственность"

```
ИНДЕКС → ДИАПАЗОН ОТВЕТСТВЕННОСТИ:

i      двоичн.   LSB    отвечает за
1      0001      1      [1, 1]
2      0010      2      [1, 2]
3      0011      1      [3, 3]
4      0100      4      [1, 4]
5      0101      1      [5, 5]
6      0110      2      [5, 6]
7      0111      1      [7, 7]
8      1000      8      [1, 8]

ПРАВИЛО: bit[i] хранит сумму arr[i - LSB(i) + 1 ... i]
```

### Модель 2: "Query идёт влево, Update идёт вправо"

```
QUERY: sum[1..i] — двигаемся НАЗАД по LSB
i -= i & -i  (отрезаем LSB)

UPDATE: add(i, delta) — двигаемся ВПЕРЁД по LSB
i += i & -i  (добавляем LSB)

Почему? Query собирает непересекающиеся диапазоны.
Update обновляет все диапазоны, содержащие i.
```

---

## Зачем это нужно?

**Проблема:**

| Подход | Prefix Sum | Point Update |
|--------|------------|--------------|
| Array | O(n) | O(1) |
| Prefix Array | O(1) | O(n) |
| Segment Tree | O(log n) | O(log n) |
| **Fenwick Tree** | **O(log n)** | **O(log n)** |

Fenwick Tree = Segment Tree производительность + простота кода.

---

## Что это такое?

### Идея

Каждый индекс i отвечает за диапазон элементов, размер которого определяется LSB(i).

```
LSB(i) = i & (-i)  // Наименьший установленный бит

i = 12 = 1100₂
LSB(12) = 0100₂ = 4

Индекс 12 отвечает за 4 элемента: [9, 10, 11, 12]
```

### Структура

```
Массив: [3, 2, -1, 6, 5, 4, -3, 3, 7, 2, 3, -2]
Индексы: 1  2   3  4  5  6   7  8  9 10 11  12 (1-indexed)

BIT[i] хранит сумму arr[i - LSB(i) + 1 ... i]

BIT[1] = arr[1]           = 3      (LSB=1, диапазон [1,1])
BIT[2] = arr[1] + arr[2]  = 5      (LSB=2, диапазон [1,2])
BIT[3] = arr[3]           = -1     (LSB=1, диапазон [3,3])
BIT[4] = arr[1..4]        = 10     (LSB=4, диапазон [1,4])
BIT[5] = arr[5]           = 5      (LSB=1, диапазон [5,5])
BIT[6] = arr[5] + arr[6]  = 9      (LSB=2, диапазон [5,6])
BIT[7] = arr[7]           = -3     (LSB=1, диапазон [7,7])
BIT[8] = arr[1..8]        = 19     (LSB=8, диапазон [1,8])
...
```

### Визуализация

```
              BIT[8] = sum[1..8]
             /                  \
    BIT[4]=sum[1..4]       BIT[6]=sum[5..6]  BIT[7]=arr[7]
      /      \                 /      \
BIT[2]     BIT[3]       BIT[5]     BIT[6]
 sum[1..2]  arr[3]       arr[5]    sum[5..6]
  /   \
BIT[1] BIT[2]
arr[1] sum[1..2]
```

---

## Реализация (Kotlin)

```kotlin
/**
 * FENWICK TREE (Binary Indexed Tree / BIT)
 *
 * Структура данных для:
 * - Point update: O(log n)
 * - Prefix sum query: O(log n)
 *
 * Проще чем Segment Tree, но поддерживает только ассоциативные операции
 * с обратным элементом (сумма, XOR).
 */
class FenwickTree(private val n: Int) {
    // ВАЖНО: используем 1-based индексацию!
    // При 1-based арифметика LSB работает корректно.
    // tree[0] не используется, поэтому size = n + 1
    private val tree = LongArray(n + 1)

    /**
     * LSB (Least Significant Bit) — ключ к магии Fenwick Tree
     *
     * LSB(i) = i & (-i) = самый младший установленный бит
     * Примеры: LSB(12) = LSB(1100₂) = 4 = 100₂
     *          LSB(6) = LSB(110₂) = 2 = 10₂
     *          LSB(8) = LSB(1000₂) = 8 = 1000₂
     *
     * LSB определяет "размер ответственного диапазона" узла
     */
    private fun lsb(i: Int): Int = i and (-i)

    /**
     * POINT UPDATE — добавить delta к arr[i]
     *
     * Обновляем все узлы, которые "отвечают" за индекс i.
     * i += LSB(i) — переход к следующему "родительскому" узлу.
     */
    fun update(i: Int, delta: Long) {
        var idx = i
        while (idx <= n) {
            tree[idx] += delta
            idx += lsb(idx)  // К следующему узлу выше
        }
    }

    /**
     * PREFIX SUM — сумма arr[1..i]
     *
     * Собираем сумму по "пути к корню".
     * i -= LSB(i) — переход к предыдущему непересекающемуся диапазону.
     */
    fun prefixSum(i: Int): Long {
        var sum = 0L
        var idx = i
        while (idx > 0) {
            sum += tree[idx]
            idx -= lsb(idx)  // К предыдущему диапазону
        }
        return sum
    }

    /**
     * RANGE SUM — сумма arr[l..r]
     *
     * Формула: sum(l, r) = prefix(r) - prefix(l-1)
     */
    fun rangeSum(l: Int, r: Int): Long {
        return prefixSum(r) - prefixSum(l - 1)
    }

    /**
     * BUILD — инициализация из массива за O(n)
     *
     * Вместо n вызовов update (O(n log n)) используем
     * свойство: каждый узел влияет на своего родителя.
     */
    fun build(arr: IntArray) {
        for (i in 1..n) {
            tree[i] += arr[i - 1].toLong()
            val parent = i + lsb(i)
            if (parent <= n) {
                tree[parent] += tree[i]
            }
        }
    }
}
```

### Использование

```kotlin
val arr = intArrayOf(3, 2, -1, 6, 5, 4)
val bit = FenwickTree(arr.size)
bit.build(arr)

println(bit.prefixSum(4))    // 3 + 2 + (-1) + 6 = 10
println(bit.rangeSum(2, 5))  // 2 + (-1) + 6 + 5 = 12

bit.update(3, 5)             // arr[3] += 5 → arr[3] = 4
println(bit.rangeSum(2, 5))  // 2 + 4 + 6 + 5 = 17
```

---

## Как работает LSB арифметика

### Prefix Sum Query

```
Query: prefixSum(7)

i = 7 = 0111₂, LSB = 1 → sum += tree[7], i = 6
i = 6 = 0110₂, LSB = 2 → sum += tree[6], i = 4
i = 4 = 0100₂, LSB = 4 → sum += tree[4], i = 0
STOP

Визуально:
    [1, 2, 3, 4, 5, 6, 7]
     ├──────────┤         tree[4] = sum[1..4]
                 ├──┤     tree[6] = sum[5..6]
                     ├┤   tree[7] = arr[7]

prefixSum(7) = tree[4] + tree[6] + tree[7]
```

### Point Update

```
Update: update(3, +5)

i = 3 = 0011₂, LSB = 1 → tree[3] += 5, i = 4
i = 4 = 0100₂, LSB = 4 → tree[4] += 5, i = 8
i = 8 = 1000₂, LSB = 8 → tree[8] += 5, i = 16
STOP (16 > n)

Обновляем все узлы, которые включают индекс 3:
tree[3], tree[4], tree[8], ...
```

---

## Расширенные операции

### Range Update + Point Query

```kotlin
/**
 * Range Update + Point Query
 *
 * Идея: храним "разностный массив".
 * Если нужно добавить delta к [l..r]:
 * - diff[l] += delta (начинаем добавлять)
 * - diff[r+1] -= delta (перестаём добавлять)
 *
 * Значение arr[i] = сумма diff[1..i] = prefix sum!
 */
class FenwickTreeRangeUpdate(private val n: Int) {
    private val tree = LongArray(n + 1)

    // Добавить delta к диапазону [l..r]
    fun rangeUpdate(l: Int, r: Int, delta: Long) {
        update(l, delta)       // +delta начиная с l
        update(r + 1, -delta)  // Отменяем после r
    }

    // Значение arr[i] = prefix sum разностного массива
    fun pointQuery(i: Int): Long = prefixSum(i)

    private fun update(i: Int, delta: Long) { /* как выше */ }
    private fun prefixSum(i: Int): Long { /* как выше */ }
}
```

### Range Update + Range Query

```kotlin
/**
 * Range Update + Range Query — требует 2 BIT!
 *
 * Математически сложнее. Используем формулу:
 * prefix(i) = bit1[i] * i - bit2[i]
 *
 * Где bit1 и bit2 — два отдельных Fenwick Tree.
 */
class FenwickTreeRangeUpdateRangeQuery(private val n: Int) {
    private val bit1 = LongArray(n + 1)
    private val bit2 = LongArray(n + 1)

    fun rangeUpdate(l: Int, r: Int, delta: Long) {
        add(bit1, l, delta)
        add(bit1, r + 1, -delta)
        add(bit2, l, delta * (l - 1))
        add(bit2, r + 1, -delta * r)
    }

    fun prefixSum(i: Int): Long {
        return sum(bit1, i) * i - sum(bit2, i)
    }

    fun rangeSum(l: Int, r: Int): Long {
        return prefixSum(r) - prefixSum(l - 1)
    }

    private fun add(tree: LongArray, i: Int, delta: Long) { /* ... */ }
    private fun sum(tree: LongArray, i: Int): Long { /* ... */ }
}
```

### 2D Fenwick Tree

```kotlin
class FenwickTree2D(private val n: Int, private val m: Int) {
    private val tree = Array(n + 1) { LongArray(m + 1) }

    /**
     * POINT UPDATE в 2D — добавить delta к ячейке (x, y)
     *
     * Работает как два вложенных 1D Fenwick Tree:
     * - Внешний цикл: идём по строкам (i += LSB(i))
     * - Внутренний цикл: идём по столбцам (j += LSB(j))
     *
     * Пример update(3, 2, +5) в матрице 4x4:
     * Обновляем: tree[3][2], tree[3][4], tree[4][2], tree[4][4]
     *
     * Визуально (X = обновлённые ячейки):
     *     1   2   3   4
     * 1   .   .   .   .
     * 2   .   .   .   .
     * 3   .   X   .   X  ← i=3: j=2,4
     * 4   .   X   .   X  ← i=4: j=2,4
     */
    fun update(x: Int, y: Int, delta: Long) {
        var i = x
        while (i <= n) {
            var j = y
            while (j <= m) {
                tree[i][j] += delta
                j += j and (-j)  // К следующему столбцу
            }
            i += i and (-i)  // К следующей строке
        }
    }

    /**
     * PREFIX SUM в 2D — сумма прямоугольника [1,1]..[x,y]
     *
     * Аналогично update, но в обратном направлении:
     * - Внешний цикл: идём к началу по строкам (i -= LSB(i))
     * - Внутренний цикл: идём к началу по столбцам (j -= LSB(j))
     *
     * Пример prefixSum(3, 3):
     * Собираем: tree[3][3] + tree[3][2] + tree[2][3] + tree[2][2]
     *
     * Каждый tree[i][j] хранит сумму прямоугольника, размер которого
     * определяется LSB(i) × LSB(j)
     */
    fun prefixSum(x: Int, y: Int): Long {
        var sum = 0L
        var i = x
        while (i > 0) {
            var j = y
            while (j > 0) {
                sum += tree[i][j]
                j -= j and (-j)  // К предыдущему столбцу
            }
            i -= i and (-i)  // К предыдущей строке
        }
        return sum
    }

    /**
     * RANGE SUM в 2D — сумма прямоугольника [x1,y1]..[x2,y2]
     *
     * Используем принцип включения-исключения (Inclusion-Exclusion):
     *
     * ┌─────────────┬─────┐
     * │      A      │  B  │
     * ├─────────────┼─────┤ y1-1
     * │      C      │  D  │
     * └─────────────┴─────┘
     *              x1-1   x2
     *
     * Нам нужен D = весь прямоугольник - A - B - C + пересечение A∩B∩C
     *
     * Формула: sum(x1,y1,x2,y2) =
     *   prefix(x2,y2)       — весь прямоугольник до (x2,y2)
     * - prefix(x1-1,y2)     — убираем левую часть
     * - prefix(x2,y1-1)     — убираем верхнюю часть
     * + prefix(x1-1,y1-1)   — добавляем обратно (вычли дважды)
     */
    fun rangeSum(x1: Int, y1: Int, x2: Int, y2: Int): Long {
        return prefixSum(x2, y2) -
               prefixSum(x1 - 1, y2) -
               prefixSum(x2, y1 - 1) +
               prefixSum(x1 - 1, y1 - 1)
    }
}
```

---

## Сложность операций

| Операция | Сложность |
|----------|-----------|
| Build | O(n) |
| Point Update | O(log n) |
| Prefix Sum | O(log n) |
| Range Sum | O(log n) |
| Range Update | O(log n) |
| Space | O(n) |

---

## Fenwick vs Segment Tree

| Критерий | Fenwick | Segment Tree |
|----------|---------|--------------|
| Space | O(n) | O(4n) |
| Code | 8-10 lines | 50+ lines |
| Constant factor | Меньше | Больше |
| Range Update | С 2 BIT | Lazy propagation |
| Non-commutative | ❌ | ✓ |
| Min/Max | Сложно | Легко |

### Когда использовать

```
Fenwick Tree:
✓ Prefix sum + point update
✓ Нужен простой код
✓ Важна скорость и память

Segment Tree:
✓ Нужны non-commutative операции
✓ Range min/max queries
✓ Сложная lazy propagation
```

---

## Применения

### 1. Inversion Count

```kotlin
/**
 * ПОДСЧЁТ ИНВЕРСИЙ — количество пар (i, j) где i < j, но arr[i] > arr[j]
 *
 * Идея: используем BIT как "счётчик встреченных элементов".
 * Идём справа налево и для каждого элемента считаем,
 * сколько МЕНЬШИХ элементов мы уже видели справа.
 *
 * Пример: arr = [3, 1, 2]
 * Инверсии: (3,1), (3,2) = 2
 *
 * ПОШАГОВЫЙ ПРИМЕР:
 * arr = [3, 1, 2], ranks = [3, 1, 2] (после сжатия)
 *
 * i=2: rank=2, prefixSum(1)=0, update(2,1) → inversions=0
 *      BIT теперь знает: элемент с рангом 2 встретился
 *
 * i=1: rank=1, prefixSum(0)=0, update(1,1) → inversions=0
 *      BIT теперь знает: ранги 1 и 2 встретились
 *
 * i=0: rank=3, prefixSum(2)=2, update(3,1) → inversions=2
 *      Справа от 3 есть 2 меньших элемента (ранги 1 и 2)
 *
 * Ответ: 2 инверсии
 */
fun countInversions(arr: IntArray): Long {
    val n = arr.size
    val bit = FenwickTree(n)
    var inversions = 0L

    // COORDINATE COMPRESSION (сжатие координат)
    // Зачем? Значения могут быть до 10^9, но нам нужны индексы для BIT
    // Сжимаем: [1000000, 1, 500] → [3, 1, 2] (ранги в отсортированном порядке)
    // Теперь значения 1..n можно использовать как индексы BIT!
    val sorted = arr.sorted()
    val rank = arr.map { sorted.binarySearch(it) + 1 }

    // Идём СПРАВА НАЛЕВО — так мы накапливаем информацию о "будущих" элементах
    // Когда смотрим на arr[i], в BIT уже записаны все элементы справа от i
    for (i in n - 1 downTo 0) {
        // prefixSum(rank[i] - 1) = сколько элементов с рангом < rank[i]
        // уже встретилось справа? Это и есть инверсии для arr[i]!
        inversions += bit.prefixSum(rank[i] - 1)
        // Помечаем: элемент с данным рангом встретился
        bit.update(rank[i], 1)
    }

    return inversions
}
```

### 2. Dynamic Order Statistics

```kotlin
// k-th smallest element с updates
fun kthSmallest(bit: FenwickTree, k: Int, maxVal: Int): Int {
    var lo = 1
    var hi = maxVal

    while (lo < hi) {
        val mid = (lo + hi) / 2
        if (bit.prefixSum(mid) >= k) {
            hi = mid
        } else {
            lo = mid + 1
        }
    }

    return lo
}
```

---

## Распространённые ошибки

### 1. 0-indexed vs 1-indexed

```kotlin
// ❌ НЕПРАВИЛЬНО: 0-indexed ломает LSB
bit.update(0, delta)  // i & (-i) для 0 = 0 → бесконечный цикл!

// ✅ ПРАВИЛЬНО: 1-indexed
bit.update(i + 1, delta)  // сдвигаем индексы
```

### 2. Забыть про r+1 в range update

```kotlin
// ❌ НЕПРАВИЛЬНО: добавляем только в l
fun rangeUpdate(l: Int, r: Int, delta: Long) {
    update(l, delta)  // delta влияет на все элементы после l!
}

// ✅ ПРАВИЛЬНО: отменяем после r
fun rangeUpdate(l: Int, r: Int, delta: Long) {
    update(l, delta)
    // update(l, delta) добавляет delta ко ВСЕМ элементам начиная с l
    // Чтобы эффект был только на [l..r], "отменяем" его после r
    // update(r+1, -delta) вычитает delta начиная с r+1
    // Итого: элементы [l..r] получают +delta, остальные — ничего
    update(r + 1, -delta)
}
```

### 3. Overflow при большом n

```kotlin
// ❌ НЕПРАВИЛЬНО: Int может переполниться
private val tree = IntArray(n + 1)

// ✅ ПРАВИЛЬНО: Long для суммы
private val tree = LongArray(n + 1)
```

---

## Практика

### LeetCode задачи

| # | Название | Сложность | Тип |
|---|----------|-----------|-----|
| 307 | Range Sum Query - Mutable | Medium | Basic BIT |
| 315 | Count of Smaller Numbers After Self | Hard | BIT + coordinate compression |
| 327 | Count of Range Sum | Hard | BIT + merge sort |
| 493 | Reverse Pairs | Hard | BIT |
| 1649 | Create Sorted Array | Hard | BIT |

### Порядок изучения

```
1. 307. Range Sum Query - Mutable — базовый BIT
2. 315. Count of Smaller Numbers — inversion counting
3. 493. Reverse Pairs — modified inversions
4. 2D BIT problems — range sum in matrix
```

---

## Связанные темы

### Prerequisites
- Bit Manipulation (LSB)
- Prefix Sums

### Unlocks
- 2D Fenwick Tree
- Offline algorithms (answer queries in different order)
- Wavelet Trees

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [CP-Algorithms](https://cp-algorithms.com/data_structures/fenwick.html) | Reference | Complete guide |
| 2 | [HackerEarth](https://www.hackerearth.com/practice/notes/binary-indexed-tree-or-fenwick-tree/) | Tutorial | Visualization |
| 3 | [Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree) | Reference | Original paper |
| 4 | [TopCoder](https://www.topcoder.com/thrive/articles/Binary%20Indexed%20Trees) | Tutorial | Applications |

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции: 2 аналогии (многоуровневая агрегация, LSB как шаг назад), 3 типичные ошибки (0-indexed, range sum, update vs add), 2 ментальные модели (LSB определяет ответственность, query влево/update вправо)*
