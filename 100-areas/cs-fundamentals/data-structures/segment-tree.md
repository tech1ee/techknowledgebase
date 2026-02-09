# Segment Tree

## TL;DR

Segment Tree — структура для range queries и updates за O(log n). Поддерживает sum, min, max, GCD на отрезках. **Lazy propagation** позволяет range updates за O(log n). Требует 4n памяти. Мощнее Fenwick Tree, но сложнее в реализации.

---

## Интуиция

### Аналогия 1: Segment Tree как менеджеры в компании

```
ОРГАНИЗАЦИОННАЯ СТРУКТУРА = SEGMENT TREE:

CEO знает общую выручку компании
       │
  ┌────┴────┐
  ▼         ▼
VP West   VP East     ← знают выручку своих регионов
  │         │
┌─┴─┐     ┌─┴─┐
▼   ▼     ▼   ▼
A   B     C   D       ← менеджеры знают выручку отделов (листья)

"Какая выручка на западе?" → Спроси VP West (O(1), уже агрегировано)
"Какая выручка в B и C?" → Спроси VP West + VP East частично (O(log n))
"Отдел B вырос на 10%" → Обнови B → VP West → CEO (O(log n))
```

**Ключевая идея:** Каждый "менеджер" хранит агрегат своих подчинённых. Не нужно опрашивать всех — достаточно спросить нужных менеджеров.

### Аналогия 2: Дерево как кэш для отрезков

```
ЗАДАЧА: Сумма на [l, r] из 10^6 элементов, 10^6 запросов

БЕЗ КЭША (массив):
Каждый запрос = пройти все элементы [l..r] = O(n)
Итого: O(n × q) = 10^12 операций = TLE

С КЭШОМ (Segment Tree):
Предвычисляем суммы для всех "круглых" отрезков
[0,7], [0,3], [4,7], [0,1], [2,3], [4,5], [6,7], ...

Запрос [2,5] = [2,3] + [4,5] = 2 кэшированных значения
Итого: O(log n) на запрос
```

---

## Частые ошибки

### Ошибка 1: Неправильный размер массива tree

**СИМПТОМ:** Index out of bounds при построении дерева

```kotlin
// НЕПРАВИЛЬНО: размер = 2*n
val tree = IntArray(2 * n)  // ArrayIndexOutOfBoundsException!

// ПРАВИЛЬНО: размер = 4*n
val tree = IntArray(4 * n)  // Гарантированно хватит
```

**Почему 4n?** Для n не степени 2 индексация "2*i+1, 2*i+2" может требовать до 4n узлов.

### Ошибка 2: Забыть про lazy propagation при range update

**СИМПТОМ:** O(n log n) вместо O(log n) на range update

```kotlin
// НЕПРАВИЛЬНО: обновляем каждый элемент отдельно
fun rangeAdd(l: Int, r: Int, value: Int) {
    for (i in l..r) update(i, value)  // O(n log n)!
}

// ПРАВИЛЬНО: lazy propagation
fun rangeAdd(l: Int, r: Int, value: Int) {
    lazy[node] += value  // отложенное обновление
    pushDown(node)       // протолкнуть при необходимости
}
```

### Ошибка 3: Неправильная граница mid в query/update

**СИМПТОМ:** Неверные ответы на запросы

```kotlin
// НЕПРАВИЛЬНО: путаница с границами
if (queryEnd <= mid) return query(leftChild, start, mid, ...)
if (queryStart >= mid) return query(rightChild, mid, end, ...)  // mid включён дважды!

// ПРАВИЛЬНО: mid идёт в левого ребёнка
if (queryEnd <= mid) return query(leftChild, start, mid, ...)
if (queryStart > mid) return query(rightChild, mid + 1, end, ...)
```

---

## Ментальные модели

### Модель 1: "Разделяй отрезок пополам"

```
ПРИНЦИП: Любой отрезок можно покрыть O(log n) "каноническими" отрезками

Запрос [2, 6] в дереве для [0, 7]:
             [0,7]
           /       \
       [0,3]       [4,7]
       /   \       /   \
    [0,1] [2,3] [4,5] [6,7]

[2,6] = [2,3] + [4,5] + [6,6]
      = 2 + 2 + 1 = 5 узлов максимум (на практике меньше)

ПРАВИЛО: Максимум 4 узла на уровень, O(log n) уровней = O(log n) узлов
```

### Модель 2: "Операция должна быть ассоциативной"

```
ДЛЯ SEGMENT TREE ПОДХОДЯТ:

✓ Сумма:     (a + b) + c = a + (b + c)
✓ Минимум:   min(min(a,b), c) = min(a, min(b,c))
✓ Максимум:  max(max(a,b), c) = max(a, max(b,c))
✓ GCD:       gcd(gcd(a,b), c) = gcd(a, gcd(b,c))
✓ XOR:       (a ^ b) ^ c = a ^ (b ^ c)

НЕ ПОДХОДЯТ:

✗ Среднее:   avg(avg(a,b), c) ≠ avg(a, avg(b,c))
✗ Медиана:   нет ассоциативности
```

---

## Зачем это нужно?

**Проблема:**

Массив из 10^6 элементов. 10^6 запросов: "сумма на отрезке [l, r]" и "увеличить элемент i на x".

| Подход | Range Sum | Point Update | Total |
|--------|-----------|--------------|-------|
| Array | O(n) | O(1) | O(n × q) = TLE |
| Prefix Sum | O(1) | O(n) | O(n × q) = TLE |
| Segment Tree | O(log n) | O(log n) | O(q log n) ✓ |

---

## Что это такое?

### Структура

```
Массив: [1, 3, 5, 7, 9, 11]

Segment Tree (сумма):
                 36[0,5]
                /       \
           9[0,2]        27[3,5]
          /     \        /      \
       4[0,1]  5[2,2]  16[3,4]  11[5,5]
       /   \           /    \
    1[0,0] 3[1,1]   7[3,3] 9[4,4]

Каждый узел хранит результат операции для своего отрезка
```

### Свойства

- **Бинарное дерево**: каждый узел имеет 0 или 2 детей
- **Листья**: отдельные элементы массива
- **Внутренние узлы**: агрегация детей (sum, min, max)
- **Высота**: O(log n)
- **Размер**: до 4n узлов

---

## Реализация (без Lazy)

### Базовый Segment Tree (Kotlin) — с подробным объяснением

```kotlin
class SegmentTree(private val arr: IntArray) {
    // n — размер исходного массива
    private val n = arr.size

    // tree — массив, хранящий дерево отрезков
    // ПОЧЕМУ 4n? Дерево отрезков — это полное бинарное дерево.
    // Для массива размера n (не степень 2) нужно до 4n узлов.
    // Пример: n=6 → нужно ~11 узлов, но индексация требует до 24
    private val tree = IntArray(4 * n)

    // При создании объекта сразу строим дерево
    // Начинаем с корня (узел 0), который отвечает за весь отрезок [0, n-1]
    init {
        build(0, 0, n - 1)
    }

    /**
     * Рекурсивное построение дерева
     *
     * @param node — индекс текущего узла в массиве tree
     * @param start, end — отрезок исходного массива, за который отвечает этот узел
     *
     * Идея: строим дерево "снизу вверх"
     * 1. Дойти до листьев (start == end)
     * 2. В листьях записать элементы массива
     * 3. Внутренние узлы = сумма детей
     */
    private fun build(node: Int, start: Int, end: Int) {
        // БАЗА РЕКУРСИИ: дошли до листа
        // Лист отвечает за один элемент массива (start == end)
        if (start == end) {
            // Копируем значение из исходного массива
            tree[node] = arr[start]
        } else {
            // РЕКУРСИВНЫЙ СЛУЧАЙ: внутренний узел

            // Находим середину отрезка
            val mid = (start + end) / 2

            // Вычисляем индексы детей в массиве tree
            // Для узла с индексом node:
            //   левый ребёнок = 2*node + 1
            //   правый ребёнок = 2*node + 2
            val leftChild = 2 * node + 1
            val rightChild = 2 * node + 2

            // Рекурсивно строим левое поддерево [start, mid]
            build(leftChild, start, mid)
            // Рекурсивно строим правое поддерево [mid+1, end]
            build(rightChild, mid + 1, end)

            // После построения детей вычисляем значение родителя
            // Для суммы: родитель = левый + правый
            tree[node] = tree[leftChild] + tree[rightChild]
        }
    }

    /**
     * Обновление одного элемента (Point Update)
     *
     * @param idx — индекс изменяемого элемента в исходном массиве
     * @param value — новое значение
     *
     * Сложность: O(log n) — спускаемся от корня к листу
     */
    fun update(idx: Int, value: Int) {
        // Запускаем рекурсию от корня
        update(0, 0, n - 1, idx, value)
    }

    private fun update(node: Int, start: Int, end: Int, idx: Int, value: Int) {
        // БАЗА: нашли лист с нужным элементом
        if (start == end) {
            // Обновляем значение в исходном массиве (опционально)
            arr[idx] = value
            // Обновляем значение в дереве
            tree[node] = value
        } else {
            // РЕКУРСИЯ: определяем, в каком поддереве находится idx

            val mid = (start + end) / 2
            val leftChild = 2 * node + 1
            val rightChild = 2 * node + 2

            // Если idx <= mid — идём влево, иначе вправо
            // Важно: идём ТОЛЬКО В ОДНО поддерево (не в оба!)
            if (idx <= mid) {
                // idx в левой половине [start, mid]
                update(leftChild, start, mid, idx, value)
            } else {
                // idx в правой половине [mid+1, end]
                update(rightChild, mid + 1, end, idx, value)
            }

            // После обновления ребёнка ПЕРЕСЧИТЫВАЕМ родителя
            // Это критически важно! Иначе дерево станет невалидным.
            tree[node] = tree[leftChild] + tree[rightChild]
        }
    }

    /**
     * Запрос суммы на отрезке [l, r]
     *
     * @param l, r — границы запроса (включительно)
     * @return сумма элементов arr[l] + arr[l+1] + ... + arr[r]
     *
     * Сложность: O(log n) — посещаем O(log n) узлов
     */
    fun query(l: Int, r: Int): Int {
        return query(0, 0, n - 1, l, r)
    }

    private fun query(node: Int, start: Int, end: Int, l: Int, r: Int): Int {
        // СЛУЧАЙ 1: Текущий отрезок [start, end] ПОЛНОСТЬЮ ВНЕ запроса [l, r]
        // Примеры: запрос [3,5], текущий [0,2] или запрос [0,2], текущий [4,6]
        if (r < start || end < l) {
            // Возвращаем НЕЙТРАЛЬНЫЙ элемент
            // Для суммы нейтральный = 0 (не влияет на результат)
            return 0
        }

        // СЛУЧАЙ 2: Текущий отрезок ПОЛНОСТЬЮ ВНУТРИ запроса
        // Условие: l <= start && end <= r
        // Пример: запрос [1,5], текущий [2,3] — [2,3] целиком внутри [1,5]
        if (l <= start && end <= r) {
            // Возвращаем готовый результат для этого отрезка
            // Не нужно спускаться к детям!
            return tree[node]
        }

        // СЛУЧАЙ 3: Частичное пересечение
        // Часть отрезка внутри запроса, часть снаружи
        // Нужно спуститься к обоим детям и объединить результаты
        val mid = (start + end) / 2
        val leftResult = query(2 * node + 1, start, mid, l, r)
        val rightResult = query(2 * node + 2, mid + 1, end, l, r)

        // Объединяем результаты (для суммы — складываем)
        return leftResult + rightResult
    }
}

// ПОШАГОВЫЙ ПРИМЕР для arr = [1, 3, 5, 7]:
//
// После build():
//                   16 [0,3]        ← корень: сумма всего массива
//                  /       \
//             4 [0,1]      12 [2,3]
//             /    \        /     \
//          1[0]   3[1]   5[2]   7[3]  ← листья = элементы массива
//
// query(1, 2):
//   Узел [0,3]: частичное пересечение → спускаемся
//   Узел [0,1]: частичное пересечение → спускаемся
//     Узел [0]: вне запроса → return 0
//     Узел [1]: внутри запроса → return 3
//   Узел [2,3]: частичное пересечение → спускаемся
//     Узел [2]: внутри запроса → return 5
//     Узел [3]: вне запроса → return 0
//   Результат: 0 + 3 + 5 + 0 = 8
//
// update(1, 10):  // меняем arr[1] с 3 на 10
//   Спускаемся: [0,3] → [0,1] → [1]
//   tree[лист 1] = 10
//   Поднимаемся и пересчитываем:
//     tree[0,1] = 1 + 10 = 11
//     tree[0,3] = 11 + 12 = 23
```

### Использование

```kotlin
val arr = intArrayOf(1, 3, 5, 7, 9, 11)
val st = SegmentTree(arr)

println(st.query(1, 3))  // 3 + 5 + 7 = 15
st.update(2, 10)         // arr[2] = 10
println(st.query(1, 3))  // 3 + 10 + 7 = 20
```

---

## Lazy Propagation

### Проблема

Range update [l, r] += x без lazy: O(n log n)
```
Нужно обновить каждый элемент индивидуально
10^6 updates × log n = TLE
```

### Решение: Lazy Propagation

```
Идея: откладываем обновления
Записываем "pending update" в узле
Применяем только когда спускаемся в детей
```

### Реализация с Lazy (Kotlin) — с подробным объяснением

```kotlin
class LazySegmentTree(private val arr: IntArray) {
    private val n = arr.size

    // tree — значения узлов (как в обычном Segment Tree)
    private val tree = LongArray(4 * n)

    // lazy — массив "отложенных обновлений"
    // lazy[node] хранит значение, которое НУЖНО ДОБАВИТЬ ко всем элементам
    // в поддереве этого узла, но мы ещё не сделали это
    // Идея: вместо обновления каждого листа, записываем "долг"
    private val lazy = LongArray(4 * n)

    init {
        build(0, 0, n - 1)
    }

    // build() такой же как в обычном Segment Tree
    private fun build(node: Int, start: Int, end: Int) {
        if (start == end) {
            tree[node] = arr[start].toLong()
        } else {
            val mid = (start + end) / 2
            build(2 * node + 1, start, mid)
            build(2 * node + 2, mid + 1, end)
            tree[node] = tree[2 * node + 1] + tree[2 * node + 2]
        }
    }

    /**
     * Проталкивание отложенного обновления вниз к детям
     *
     * Эта функция КРИТИЧЕСКИ ВАЖНА для Lazy Propagation!
     * Вызывается перед любым спуском к детям.
     *
     * Идея: если у узла есть "долг" (lazy != 0), мы:
     * 1. Применяем долг к самому узлу
     * 2. Передаём долг детям
     * 3. Обнуляем долг узла
     */
    private fun pushDown(node: Int, start: Int, end: Int) {
        // Если нет отложенного обновления — ничего не делаем
        if (lazy[node] != 0L) {
            // ШАГ 1: Применяем lazy к значению текущего узла
            // Узел отвечает за (end - start + 1) элементов
            // Если каждый элемент увеличился на lazy[node],
            // то сумма увеличилась на lazy[node] * количество элементов
            tree[node] += lazy[node] * (end - start + 1)

            // ШАГ 2: Если это не лист — передаём долг детям
            if (start != end) {
                // Левый и правый дети получают тот же "долг"
                // Их обновления применятся когда мы спустимся к ним
                lazy[2 * node + 1] += lazy[node]
                lazy[2 * node + 2] += lazy[node]
            }

            // ШАГ 3: Обнуляем долг текущего узла
            // Мы "погасили" его, применив к значению и передав детям
            lazy[node] = 0
        }
    }

    /**
     * Range Update: добавить value ко всем элементам в [l, r]
     *
     * БЕЗ lazy propagation: O(n log n) — нужно обновить каждый лист
     * С lazy propagation: O(log n) — записываем "долг" и уходим
     */
    fun rangeUpdate(l: Int, r: Int, value: Long) {
        rangeUpdate(0, 0, n - 1, l, r, value)
    }

    private fun rangeUpdate(node: Int, start: Int, end: Int, l: Int, r: Int, value: Long) {
        // ВАЖНО: сначала применяем отложенные обновления!
        // Иначе мы можем перезаписать старый "долг"
        pushDown(node, start, end)

        // СЛУЧАЙ 1: Отрезок вне запроса
        if (r < start || end < l) return

        // СЛУЧАЙ 2: Отрезок полностью внутри запроса
        if (l <= start && end <= r) {
            // Вместо спуска к каждому листу — записываем "долг"
            // Это КЛЮЧЕВАЯ оптимизация!
            lazy[node] += value
            // Сразу применяем, чтобы tree[node] был актуален
            pushDown(node, start, end)
            return
        }

        // СЛУЧАЙ 3: Частичное пересечение — спускаемся к детям
        val mid = (start + end) / 2
        rangeUpdate(2 * node + 1, start, mid, l, r, value)
        rangeUpdate(2 * node + 2, mid + 1, end, l, r, value)

        // Пересчитываем значение узла после обновления детей
        tree[node] = tree[2 * node + 1] + tree[2 * node + 2]
    }

    /**
     * Range Query: сумма на отрезке [l, r]
     */
    fun query(l: Int, r: Int): Long {
        return query(0, 0, n - 1, l, r)
    }

    private fun query(node: Int, start: Int, end: Int, l: Int, r: Int): Long {
        // КРИТИЧЕСКИ ВАЖНО: применить lazy ПЕРЕД чтением!
        // Иначе tree[node] может содержать устаревшее значение
        pushDown(node, start, end)

        if (r < start || end < l) return 0

        if (l <= start && end <= r) return tree[node]

        val mid = (start + end) / 2
        return query(2 * node + 1, start, mid, l, r) +
               query(2 * node + 2, mid + 1, end, l, r)
    }
}

// ПОШАГОВЫЙ ПРИМЕР Lazy Propagation:
//
// arr = [1, 2, 3, 4], дерево построено
//
// rangeUpdate(0, 2, +5):  // добавить 5 к arr[0], arr[1], arr[2]
//
//   Узел [0,3]: частичное пересечение
//     pushDown (lazy=0, ничего не делаем)
//     Спускаемся к детям
//
//   Узел [0,1]: ПОЛНОСТЬЮ ВНУТРИ [0,2]
//     lazy[0,1] = 5
//     pushDown: tree[0,1] += 5 * 2 = 10
//     Передаём lazy детям: lazy[0] = 5, lazy[1] = 5
//     lazy[0,1] = 0
//     return  // НЕ спускаемся дальше!
//
//   Узел [2,3]: частичное пересечение
//     Узел [2]: внутри → lazy[2] = 5, tree[2] += 5
//     Узел [3]: вне → return
//
// query(1, 1):  // запрос одного элемента
//   Узел [0,3]: pushDown (lazy=0)
//   Узел [0,1]: pushDown → СЕЙЧАС применяем lazy[0,1]=5 к детям!
//     tree[0] += 5, tree[1] += 5
//   Узел [1]: возвращаем tree[1] = 2 + 5 = 7 ✓
```

---

## Варианты Segment Tree

### Range Min Query (RMQ)

```kotlin
// Для минимума меняем ТОЛЬКО две вещи:
// 1. Агрегирующую функцию: + → minOf
// 2. Нейтральный элемент: 0 → Int.MAX_VALUE

private fun build(node: Int, start: Int, end: Int) {
    if (start == end) {
        tree[node] = arr[start]
    } else {
        val mid = (start + end) / 2
        build(2 * node + 1, start, mid)
        build(2 * node + 2, mid + 1, end)
        // Родитель = МИНИМУМ из детей (а не сумма!)
        tree[node] = minOf(tree[2 * node + 1], tree[2 * node + 2])
    }
}

private fun query(...): Int {
    // Для отрезков ВНЕ запроса возвращаем НЕЙТРАЛЬНЫЙ элемент
    // Для минимума нейтральный = MAX_VALUE (не влияет на результат)
    // minOf(x, MAX_VALUE) = x
    if (r < start || end < l) return Int.MAX_VALUE

    if (l <= start && end <= r) return tree[node]
    // ...
    // Объединяем результаты детей через minOf
    return minOf(leftResult, rightResult)
}
```

### Range GCD

```kotlin
// Для НОД (наибольший общий делитель):
// gcd(a, b) — рекурсивный алгоритм Евклида
private fun gcd(a: Int, b: Int): Int = if (b == 0) a else gcd(b, a % b)

// Агрегирующая функция — gcd вместо sum/min
tree[node] = gcd(tree[leftChild], tree[rightChild])

// Нейтральный элемент для GCD = 0
// Потому что gcd(x, 0) = x для любого x
```

### 2D Segment Tree

```kotlin
// Двумерное дерево отрезков — для матриц
// Каждый узел внешнего дерева содержит ЦЕЛОЕ внутреннее дерево
//
// Структура: дерево деревьев
// Внешнее дерево: по строкам
// Внутренние деревья: по столбцам
//
// Применение: сумма/минимум в прямоугольнике (x1,y1)-(x2,y2)

class SegmentTree2D(private val matrix: Array<IntArray>) {
    // Сложность построения: O(n × m)
    // Сложность запроса: O(log n × log m)
    // Сложность обновления: O(log n × log m)
    // Память: O(4n × 4m) = O(16nm)
}
```

---

## Сложность операций

| Операция | Без Lazy | С Lazy |
|----------|----------|--------|
| Build | O(n) | O(n) |
| Point Update | O(log n) | O(log n) |
| Range Update | O(n log n) | O(log n) |
| Range Query | O(log n) | O(log n) |
| Space | O(4n) | O(4n) |

---

## Segment Tree vs Alternatives

| Критерий | Segment Tree | Fenwick Tree | Sparse Table |
|----------|--------------|--------------|--------------|
| Range Sum | O(log n) | O(log n) | O(log n) |
| Range Min | O(log n) | Сложно | O(1) |
| Point Update | O(log n) | O(log n) | ❌ |
| Range Update | O(log n) lazy | O(log n) | ❌ |
| Space | O(4n) | O(n) | O(n log n) |
| Код | Сложный | Простой | Средний |

### Когда что использовать

```
Segment Tree:
✓ Range queries + updates
✓ Нужна lazy propagation
✓ Разные типы запросов (sum, min, max)

Fenwick Tree:
✓ Только prefix sum / point update
✓ Нужен простой код
✓ Меньше памяти

Sparse Table:
✓ Только queries (нет updates)
✓ Нужен O(1) query
✓ Idempotent операции (min, max, GCD)
```

---

## Распространённые ошибки

### 1. Неправильный размер массива

```kotlin
// ❌ НЕПРАВИЛЬНО: может не хватить места
val tree = IntArray(2 * n)

// ✅ ПРАВИЛЬНО: 4n гарантированно достаточно
val tree = IntArray(4 * n)
```

### 2. Забыть pushDown в query

```kotlin
// ❌ НЕПРАВИЛЬНО: не применяем pending updates
private fun query(node: Int, ...): Long {
    if (l <= start && end <= r) return tree[node]  // Может вернуть устаревшие данные!
    // ...
}

// ✅ ПРАВИЛЬНО: сначала pushDown
private fun query(node: Int, ...): Long {
    // Применяем отложенные обновления перед чтением!
    // Без этого tree[node] может содержать устаревшее значение
    pushDown(node, start, end)
    if (l <= start && end <= r) return tree[node]
    // ...
}
```

### 3. Неправильный нейтральный элемент

```kotlin
// ❌ НЕПРАВИЛЬНО: 0 не нейтральный для min
if (r < start || end < l) return 0

// ✅ ПРАВИЛЬНО:
// Для sum: return 0
// Для min: return Int.MAX_VALUE
// Для max: return Int.MIN_VALUE
// Для GCD: return 0 (gcd(x, 0) = x)
```

---

## Практика

### LeetCode задачи

| # | Название | Сложность | Тип |
|---|----------|-----------|-----|
| 307 | Range Sum Query - Mutable | Medium | Basic ST |
| 315 | Count of Smaller Numbers After Self | Hard | ST + coordinate compression |
| 327 | Count of Range Sum | Hard | ST + merge sort |
| 699 | Falling Squares | Hard | Lazy propagation |
| 732 | My Calendar III | Hard | Sweep line + ST |

### Порядок изучения

```
1. 307. Range Sum Query - Mutable — базовый segment tree
2. 303. Range Sum Query - Immutable — понять разницу с prefix sum
3. 315. Count of Smaller — ST с coordinate compression
4. 699. Falling Squares — lazy propagation
```

---

## Связанные темы

### Prerequisites
- Arrays, Recursion
- Divide and Conquer
- Trees basics

### Unlocks
- Persistent Segment Tree
- 2D Segment Tree
- Merge Sort Tree
- Implicit Segment Tree

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [CP-Algorithms](https://cp-algorithms.com/data_structures/segment_tree.html) | Reference | Complete guide |
| 2 | [Codeforces](https://codeforces.com/blog/entry/18051) | Blog | Efficient impl |
| 3 | [AlgoCademy](https://algocademy.com/blog/mastering-segment-trees-a-comprehensive-guide-for-coding-interviews/) | Guide | Interview prep |
| 4 | [HackerEarth](https://www.hackerearth.com/practice/notes/segment-tree-and-lazy-propagation/) | Tutorial | Lazy propagation |

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции: 2 аналогии (менеджеры в компании, кэш отрезков), 3 типичные ошибки (размер 4n, lazy propagation, границы mid), 2 ментальные модели (разделяй пополам, ассоциативность)*
