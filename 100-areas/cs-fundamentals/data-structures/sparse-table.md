---
title: "Разреженная таблица (Sparse Table)"
created: 2026-02-09
modified: 2026-02-10
type: deep-dive
status: published
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/advanced
related:
  - "[[segment-tree]]"
  - "[[fenwick-tree]]"
prerequisites:
  - "[[arrays-strings]]"
  - "[[big-o-complexity]]"
  - "[[bit-manipulation]]"
---

# Sparse Table

## TL;DR

Sparse Table — структура для **статических** Range Minimum Query (RMQ) за O(1). Preprocessing O(n log n), space O(n log n). Работает **только для idempotent операций** (min, max, GCD, AND, OR). Для sum/dynamic updates используй Segment Tree. Название "Sparse" — храним O(n log n) диапазонов вместо O(n²).

---

## Интуиция

### Аналогия 1: Таблица рекордов по дистанциям

```
ОЛИМПИЙСКИЕ РЕКОРДЫ:
Храним лучший результат для каждой "круглой" дистанции:

   1м   2м   4м   8м   16м  ...
   ↓    ↓    ↓    ↓    ↓
  [A]  [B]  [C]  [D]  [E]

"Кто лучший на дистанции 5-11м?"
→ Накрыть двумя "степенями двойки": [5-8] и [8-11] (перекрываются!)
→ Для min/max перекрытие не проблема: min(min(a,b), min(b,c)) = min(a,b,c)
→ O(1) ответ!
```

### Аналогия 2: Idempotent = "повторение не вредит"

```
IDEMPOTENT ОПЕРАЦИИ (подходят для Sparse Table):
min(5, 5) = 5       ← повтор элемента не меняет результат
max(3, 3) = 3
gcd(6, 6) = 6
AND, OR аналогично

НЕ IDEMPOTENT (НЕ подходят):
sum(5, 5) = 10      ← повтор удваивает!
count, XOR и т.д.

Перекрытие диапазонов работает ТОЛЬКО для idempotent!
```

---

## Частые ошибки

### Ошибка 1: Использование для суммы

**СИМПТОМ:** Ответы в 2 раза больше чем нужно

```kotlin
// НЕПРАВИЛЬНО: sum — не idempotent!
val ans = table[l][k] + table[r - (1 shl k) + 1][k]  // элементы посчитаны дважды!

// ПРАВИЛЬНО: для суммы используй Segment Tree или Fenwick Tree
```

### Ошибка 2: Неправильный расчёт k для длины отрезка

**СИМПТОМ:** Диапазоны не покрывают весь отрезок

```kotlin
// НЕПРАВИЛЬНО: k для длины len
val k = log2(len)  // k=2 для len=5, но 2^2=4 < 5!

// ПРАВИЛЬНО: floor(log2(len)) и два перекрывающихся диапазона
val k = 31 - Integer.numberOfLeadingZeros(len)
return min(table[l][k], table[r - (1 shl k) + 1][k])
```

### Ошибка 3: Попытка update в Sparse Table

**СИМПТОМ:** Неверные ответы после изменения

```kotlin
// НЕПРАВИЛЬНО: Sparse Table — статическая структура!
arr[5] = 100
// Все table[i][j], покрывающие индекс 5, устарели

// ПРАВИЛЬНО: Перестроить с нуля O(n log n) или использовать Segment Tree
```

---

## Ментальные модели

### Модель 1: "2^k покрывает всё"

```
ЛЮБОЙ ОТРЕЗОК [l, r] покрывается ДВУМЯ диапазонами длины 2^k:

Длина = r - l + 1 = 7
k = floor(log2(7)) = 2  →  2^k = 4

[l ... l+3]  и  [r-3 ... r]
   └──4──┘         └──4──┘
        └─пересечение─┘

Пересечение OK для min/max/GCD (idempotent)
```

### Модель 2: "Препроцессинг vs Query tradeoff"

```
                Preprocessing    Query    Space
Наивно              O(1)         O(n)     O(n)
Все пары         O(n²)          O(1)     O(n²)
Sparse Table   O(n log n)       O(1)   O(n log n)  ← оптимальный баланс!
Segment Tree     O(n)         O(log n)   O(n)

Sparse Table: "потратим память и время на подготовку,
              чтобы каждый запрос был O(1)"
```

---

## Идемпотентность: ключевое свойство

Sparse Table работает за O(1) благодаря одному математическому свойству: **идемпотентности** операции. Это слово звучит сложно, но идея простая.

Операция f идемпотентна, если f(x, x) = x. Применение операции к элементу с самим собой не меняет результат. Минимум: min(5, 5) = 5. Максимум: max(3, 3) = 3. GCD: gcd(12, 12) = 12. Логическое AND: 1 AND 1 = 1. Всё это идемпотентные операции.

Почему это важно? Потому что Sparse Table покрывает отрезок [l, r] ДВУМЯ перекрывающимися блоками. Элементы в перекрытии учитываются дважды. Если операция идемпотентна, двойной учёт не искажает результат: min(min(A), min(B)) = min(A U B), даже если A и B пересекаются.

Аналогия из жизни: если вы спрашиваете "Кто самый высокий человек в комнатах А и Б?", то неважно, что некоторые люди находятся в обеих комнатах (стоят в дверном проёме). Самый высокий -- это самый высокий, хоть посчитайте его трижды. Но если вы спрашиваете "Сколько людей в комнатах А и Б?", люди в проёме будут посчитаны дважды -- и ответ будет неправильным. Подсчёт (сумма) -- не идемпотентная операция.

```
ИДЕМПОТЕНТНЫЕ (подходят для O(1) query):

min(5, 5) = 5       ← повтор не меняет результат
max(3, 3) = 3
gcd(6, 6) = 6
AND, OR

НЕ ИДЕМПОТЕНТНЫЕ (только O(log n) query):

sum(5, 5) = 10 != 5  ← повтор удваивает!
product(3, 3) = 9 != 3
XOR(5, 5) = 0 != 5
count
```

> **Ключевая идея:** O(1) query в Sparse Table -- не магия. Это следствие математического свойства идемпотентности. Для неидемпотентных операций Sparse Table тоже работает, но с O(log n) query (используя непересекающиеся блоки), что лишает его преимущества над Segment Tree.

---

## Зачем это нужно?

### Проблема: миллион запросов минимума

```
Дан массив из 10^6 элементов.
Нужно ответить на 10^6 запросов: "минимум на отрезке [l, r]?"

Наивно: O(n) на запрос → 10^12 операций = TLE

Нужно: O(1) на запрос!
```

**Сравнение подходов:**

| Подход | Build | Query | Update | Space |
|--------|-------|-------|--------|-------|
| Naive | O(1) | O(n) | O(1) | O(n) |
| Prefix (только sum) | O(n) | O(1) | O(n) | O(n) |
| Segment Tree | O(n) | O(log n) | O(log n) | O(4n) |
| **Sparse Table** | **O(n log n)** | **O(1)** | **❌** | **O(n log n)** |

**Когда использовать Sparse Table:**
- Массив **статический** (без изменений)
- Много запросов (10^5+)
- Операция **idempotent** (min, max, GCD, OR, AND)

---

## Что это такое?

### Для 5-летнего

```
Представь книгу с 100 страницами.

Вместо того чтобы каждый раз искать самую интересную
картинку с страницы 17 до 45...

Мы заранее записали:
- "Лучшая картинка на страницах 1-2"
- "Лучшая картинка на страницах 1-4"
- "Лучшая картинка на страницах 1-8"
- ...

Теперь для любого диапазона мы смотрим
в 2 наши записи и сразу знаем ответ!
```

### Формально

**Sparse Table** — структура данных, хранящая предвычисленные ответы для всех диапазонов длины степени двойки.

```
st[k][i] = f(arr[i], arr[i+1], ..., arr[i + 2^k - 1])

где f — ассоциативная операция (min, max, GCD, etc.)
```

### Ключевая идея

Любой отрезок [l, r] можно покрыть **двумя** перекрывающимися отрезками длины 2^k:

```
Отрезок [2, 9] (длина 8):

arr: [a, b, c, d, e, f, g, h, i, j]
idx:  0  1  2  3  4  5  6  7  8  9

k = floor(log2(9 - 2 + 1)) = floor(log2(8)) = 3
2^k = 8

Отрезок 1: st[3][2] = min(arr[2..9])  // начало с индекса 2
Отрезок 2: st[3][2] = min(arr[2..9])  // r - 2^k + 1 = 9 - 8 + 1 = 2

В этом случае оба совпадают (идеальное покрытие)
```

```
Отрезок [2, 10] (длина 9):

k = floor(log2(9)) = 3
2^k = 8

Отрезок 1: st[3][2] = min(arr[2..9])   // [2, 9]
Отрезок 2: st[3][3] = min(arr[3..10])  // [3, 10]

         [2, 3, 4, 5, 6, 7, 8, 9]      ← Отрезок 1
               [3, 4, 5, 6, 7, 8, 9, 10] ← Отрезок 2
         └─────────────────────────┘
              Покрывают [2, 10]

Пересечение [3, 9] — но для min это не важно!
min(min(A), min(B)) = min(A ∪ B) (idempotent свойство)
```

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **RMQ** | Range Minimum Query — запрос минимума на отрезке |
| **Idempotent** | f(x, x) = x. Примеры: min, max, GCD, OR, AND |
| **Non-idempotent** | f(x, x) ≠ x. Примеры: sum, product, XOR |
| **Sparse** | "Разреженный" — храним O(n log n) вместо O(n²) |
| **st[k][i]** | Ответ для диапазона [i, i + 2^k - 1] |
| **Log table** | Предвычисленный floor(log2(i)) для O(1) доступа |

---

## Как это работает?

### Структура хранения

```
Массив: [3, 1, 4, 1, 5, 9, 2, 6]
Индексы: 0  1  2  3  4  5  6  7

st[k][i] = min(arr[i..i+2^k-1])

k=0 (длина 1):
st[0] = [3, 1, 4, 1, 5, 9, 2, 6]
         ↑  ↑  ↑  ↑  ↑  ↑  ↑  ↑
         отдельные элементы

k=1 (длина 2):
st[1][0] = min(3,1) = 1    [0,1]
st[1][1] = min(1,4) = 1    [1,2]
st[1][2] = min(4,1) = 1    [2,3]
st[1][3] = min(1,5) = 1    [3,4]
st[1][4] = min(5,9) = 5    [4,5]
st[1][5] = min(9,2) = 2    [5,6]
st[1][6] = min(2,6) = 2    [6,7]

k=2 (длина 4):
st[2][0] = min(st[1][0], st[1][2]) = min(1,1) = 1  [0,3]
st[2][1] = min(st[1][1], st[1][3]) = min(1,1) = 1  [1,4]
st[2][2] = min(st[1][2], st[1][4]) = min(1,5) = 1  [2,5]
st[2][3] = min(st[1][3], st[1][5]) = min(1,2) = 1  [3,6]
st[2][4] = min(st[1][4], st[1][6]) = min(5,2) = 2  [4,7]

k=3 (длина 8):
st[3][0] = min(st[2][0], st[2][4]) = min(1,2) = 1  [0,7]
```

### Визуализация покрытия

```
Массив: [3, 1, 4, 1, 5, 9, 2, 6]
         0  1  2  3  4  5  6  7

k=3: |────────────────────────|  st[3][0] = весь массив
k=2: |──────────|  |──────────|  st[2][0], st[2][4]
k=1: |────|  |────|  |────|  |────|  4 блока по 2
k=0: |  |  |  |  |  |  |  |  |  отдельные элементы

Query [2, 6]:
k = floor(log2(6-2+1)) = floor(log2(5)) = 2
2^k = 4

Left block:  st[2][2] = min(arr[2..5]) = 1
Right block: st[2][3] = min(arr[3..6]) = 1

         [4, 1, 5, 9]          ← st[2][2], [2,5]
            [1, 5, 9, 2]       ← st[2][3], [3,6]
         └──────────────┘
            Ответ: min(1, 1) = 1
```

### Рекуррентное соотношение

```
База:
st[0][i] = arr[i]  (диапазон длины 1)

Переход:
st[k][i] = f(st[k-1][i], st[k-1][i + 2^(k-1)])

           [i, i+2^k-1] = [i, i+2^(k-1)-1] ∪ [i+2^(k-1), i+2^k-1]

WHY: Диапазон длины 2^k состоит из двух диапазонов длины 2^(k-1)
```

---

## Сложность операций

| Операция | Сложность | Объяснение |
|----------|-----------|------------|
| Build | O(n log n) | n элементов × log n уровней |
| Query (idempotent) | O(1) | 2 lookup + 1 operation |
| Query (non-idempotent) | O(log n) | Суммируем непересекающиеся блоки |
| Space | O(n log n) | Таблица n × log n |
| Update | ❌ | Не поддерживается |

### Почему O(1) Query?

```
1. Вычислить k = floor(log2(r - l + 1))  — O(1) с предвычислением
2. Получить st[k][l]                      — O(1) array access
3. Получить st[k][r - 2^k + 1]            — O(1) array access
4. Применить f(a, b)                      — O(1) operation

Итого: O(1)
```

---

## Реализация (Kotlin)

### Базовая реализация (RMQ)

```kotlin
class SparseTable(private val arr: IntArray) {
    /**
     * РАЗМЕРНОСТЬ ТАБЛИЦЫ
     *
     * K — количество уровней (от 0 до K-1)
     * Нужно хранить диапазоны длины 1, 2, 4, 8, ... до n
     *
     * Максимальный k такой, что 2^k ≤ n:
     *   k = floor(log2(n))
     *
     * 32 - numberOfLeadingZeros(n) = ceil(log2(n)) + 1
     * Это даёт нам достаточно уровней с запасом
     *
     * ПРИМЕР: n = 8
     * numberOfLeadingZeros(8) = 28 (в 32-битном int)
     * K = 32 - 28 = 4
     * Уровни: k=0 (длина 1), k=1 (длина 2), k=2 (длина 4), k=3 (длина 8)
     */
    private val n = arr.size
    private val K = 32 - Integer.numberOfLeadingZeros(n)

    /**
     * ОСНОВНАЯ ТАБЛИЦА
     *
     * st[k][i] — минимум на отрезке [i, i + 2^k - 1]
     *
     * Размер: K уровней × n элементов = O(n log n)
     *
     * ПРИМЕР: arr = [3, 1, 4, 1, 5]
     * st[0] = [3, 1, 4, 1, 5]  — отдельные элементы
     * st[1] = [1, 1, 1, 1, -]  — пары: min(3,1), min(1,4), min(4,1), min(1,5)
     * st[2] = [1, 1, 1, -, -]  — четвёрки: min(3,1,4,1), min(1,4,1,5)
     */
    private val st = Array(K) { IntArray(n) }

    /**
     * ТАБЛИЦА ЛОГАРИФМОВ
     *
     * log[i] = floor(log2(i))
     *
     * Нужно для O(1) вычисления k в query:
     * k = floor(log2(r - l + 1)) = log[r - l + 1]
     *
     * Без предвычисления: каждый query требовал бы O(log n)
     * С предвычислением: O(1) lookup
     */
    private val log = IntArray(n + 1)

    init {
        build()
    }

    private fun build() {
        /**
         * ШАГ 1: Предвычисление логарифмов
         *
         * log[i] = floor(log2(i)) — целая часть двоичного логарифма
         *
         * Рекуррентное соотношение:
         *   log[i] = log[i/2] + 1
         *
         * Почему это работает?
         *   log2(i) = log2(i/2) + 1
         *   Деление на 2 = сдвиг вправо = уменьшение log на 1
         *
         * ПРИМЕР:
         *   log[1] = 0  (2^0 = 1)
         *   log[2] = log[1] + 1 = 1  (2^1 = 2)
         *   log[3] = log[1] + 1 = 1  (2^1 ≤ 3 < 2^2)
         *   log[4] = log[2] + 1 = 2  (2^2 = 4)
         */
        log[1] = 0
        for (i in 2..n) {
            log[i] = log[i / 2] + 1
        }

        /**
         * ШАГ 2: База — диапазоны длины 1
         *
         * st[0][i] = min(arr[i..i]) = arr[i]
         *
         * Это единственный уровень, который берём напрямую из arr
         */
        for (i in 0 until n) {
            st[0][i] = arr[i]
        }

        /**
         * ШАГ 3: Заполняем таблицу снизу вверх
         *
         * Для каждого уровня k (длина 2^k) используем уровень k-1 (длина 2^(k-1))
         *
         * Рекуррентное соотношение:
         *   st[k][i] = min(st[k-1][i], st[k-1][i + 2^(k-1)])
         *
         *   [i, i+2^k-1] = [i, i+2^(k-1)-1] ∪ [i+2^(k-1), i+2^k-1]
         *      длина 2^k     левая половина     правая половина
         *
         * ПРИМЕР: k=2, i=0 (диапазон [0,3] длины 4)
         *   st[2][0] = min(st[1][0], st[1][2])
         *            = min(min(arr[0],arr[1]), min(arr[2],arr[3]))
         *            = min([0,1], [2,3])
         *            = min([0,3])
         */
        for (k in 1 until K) {
            /**
             * Ограничение на i:
             * Нужно чтобы диапазон [i, i+2^k-1] не выходил за границы
             * i + 2^k - 1 < n  →  i < n - 2^k + 1
             *
             * ПРИМЕР: n=8, k=3 (длина 8)
             * lastIndex = 8 - 8 + 1 = 1
             * Только i=0 валиден (диапазон [0,7])
             */
            val lastIndex = n - (1 shl k) + 1
            for (i in 0 until lastIndex) {
                // Объединяем две половинки предыдущего уровня
                st[k][i] = minOf(st[k - 1][i], st[k - 1][i + (1 shl (k - 1))])
            }
        }
    }

    /**
     * O(1) QUERY — главное преимущество Sparse Table!
     *
     * Работает только для IDEMPOTENT операций (min, max, GCD, AND, OR)
     *
     * Idempotent означает: f(x, x) = x
     * Поэтому: min(min(A), min(B)) = min(A ∪ B), даже если A и B пересекаются
     */
    fun query(l: Int, r: Int): Int {
        /**
         * Находим k — максимальную степень 2, которая влезает в [l, r]
         *
         * k = floor(log2(r - l + 1))
         *
         * ПРИМЕР: l=2, r=9 (длина 8)
         * k = log[8] = 3
         * 2^3 = 8 — ровно вмещается
         *
         * ПРИМЕР: l=2, r=10 (длина 9)
         * k = log[9] = 3
         * 2^3 = 8 — меньше 9, но это ОК (используем 2 блока)
         */
        val k = log[r - l + 1]

        /**
         * Покрываем [l, r] двумя блоками длины 2^k:
         *
         * Блок 1: [l, l + 2^k - 1]     — st[k][l]
         * Блок 2: [r - 2^k + 1, r]     — st[k][r - 2^k + 1]
         *
         * ПРИМЕР: l=2, r=10, k=3, 2^k=8
         * Блок 1: [2, 9]   — st[3][2]
         * Блок 2: [3, 10]  — st[3][3]
         *
         *      [2, 3, 4, 5, 6, 7, 8, 9]     ← Блок 1
         *         [3, 4, 5, 6, 7, 8, 9, 10] ← Блок 2
         *      └──────────────────────────┘
         *                [2, 10] — покрыт!
         *
         * Блоки пересекаются на [3, 9], но для min это НЕ ВАЖНО:
         * min(min(A), min(B)) = min(A ∪ B)
         */
        return minOf(st[k][l], st[k][r - (1 shl k) + 1])
    }
}
```

### Обобщённая реализация

```kotlin
/**
 * ОБОБЩЁННАЯ SPARSE TABLE
 *
 * Параметризована типом T и операцией combine
 *
 * ВАЖНО: Операция ДОЛЖНА быть IDEMPOTENT!
 * ─────────────────────────────────────────
 * Idempotent: f(x, x) = x
 *
 * ✅ ПОДХОДЯТ:
 * - min(x, x) = x
 * - max(x, x) = x
 * - gcd(x, x) = x
 * - x AND x = x
 * - x OR x = x
 *
 * ❌ НЕ ПОДХОДЯТ:
 * - sum: x + x = 2x ≠ x
 * - product: x × x = x² ≠ x
 * - xor: x XOR x = 0 ≠ x (обычно)
 *
 * Для non-idempotent операций используй O(log n) query
 */
class GenericSparseTable<T>(
    private val arr: Array<T>,
    private val combine: (T, T) -> T
) {
    private val n = arr.size
    private val K = 32 - Integer.numberOfLeadingZeros(n)

    @Suppress("UNCHECKED_CAST")
    private val st = Array(K) { arrayOfNulls<Any>(n) as Array<T?> }
    private val log = IntArray(n + 1)

    init {
        // Предвычисление логарифмов
        log[1] = 0
        for (i in 2..n) {
            log[i] = log[i / 2] + 1
        }

        // База
        for (i in 0 until n) {
            st[0][i] = arr[i]
        }

        // Заполнение таблицы
        for (k in 1 until K) {
            for (i in 0..n - (1 shl k)) {
                st[k][i] = combine(st[k - 1][i]!!, st[k - 1][i + (1 shl (k - 1))]!!)
            }
        }
    }

    fun query(l: Int, r: Int): T {
        val k = log[r - l + 1]
        return combine(st[k][l]!!, st[k][r - (1 shl k) + 1]!!)
    }
}

// Использование:
val minTable = GenericSparseTable(arr) { a, b -> minOf(a, b) }
val maxTable = GenericSparseTable(arr) { a, b -> maxOf(a, b) }
val gcdTable = GenericSparseTable(arr) { a, b -> gcd(a, b) }
```

### Java реализация

```java
class SparseTable {
    private int[][] st;
    private int[] log;
    private int n, K;

    public SparseTable(int[] arr) {
        n = arr.length;
        K = Integer.SIZE - Integer.numberOfLeadingZeros(n);
        st = new int[K][n];
        log = new int[n + 1];

        // Предвычисляем логарифмы: log[i] = floor(log2(i))
        log[1] = 0;
        for (int i = 2; i <= n; i++) {
            log[i] = log[i / 2] + 1;
        }

        // База — копируем исходный массив (диапазоны длины 1)
        System.arraycopy(arr, 0, st[0], 0, n);

        // Заполняем таблицу снизу вверх (уровень k использует k-1)
        for (int k = 1; k < K; k++) {
            for (int i = 0; i + (1 << k) <= n; i++) {
                st[k][i] = Math.min(st[k - 1][i], st[k - 1][i + (1 << (k - 1))]);
            }
        }
    }

    public int query(int l, int r) {
        int k = log[r - l + 1];
        return Math.min(st[k][l], st[k][r - (1 << k) + 1]);
    }
}
```

### Python реализация

```python
import math

class SparseTable:
    def __init__(self, arr):
        self.n = len(arr)
        # WHY: K = количество уровней
        self.K = self.n.bit_length()

        # WHY: Предвычисляем логарифмы
        self.log = [0] * (self.n + 1)
        for i in range(2, self.n + 1):
            self.log[i] = self.log[i // 2] + 1

        # WHY: Строим таблицу
        self.st = [[0] * self.n for _ in range(self.K)]
        self.st[0] = arr[:]

        for k in range(1, self.K):
            for i in range(self.n - (1 << k) + 1):
                self.st[k][i] = min(
                    self.st[k - 1][i],
                    self.st[k - 1][i + (1 << (k - 1))]
                )

    def query(self, l, r):
        """O(1) range minimum query"""
        k = self.log[r - l + 1]
        return min(self.st[k][l], self.st[k][r - (1 << k) + 1])
```

---

## Non-Idempotent Operations (Sum)

Для операций типа sum нельзя использовать перекрытие. Нужно разбить на **непересекающиеся** блоки.

```kotlin
class SparseTableSum(private val arr: LongArray) {
    private val n = arr.size
    private val K = 32 - Integer.numberOfLeadingZeros(n)
    private val st = Array(K) { LongArray(n) }
    private val log = IntArray(n + 1)

    init {
        log[1] = 0
        for (i in 2..n) log[i] = log[i / 2] + 1

        for (i in 0 until n) st[0][i] = arr[i]

        for (k in 1 until K) {
            for (i in 0..n - (1 shl k)) {
                st[k][i] = st[k - 1][i] + st[k - 1][i + (1 shl (k - 1))]
            }
        }
    }

    /**
     * O(log n) QUERY для non-idempotent операций (sum)
     *
     * Для суммы НЕЛЬЗЯ использовать перекрывающиеся блоки:
     *   sum(A) + sum(B) ≠ sum(A ∪ B), если A ∩ B ≠ ∅
     *
     * Поэтому разбиваем на НЕПЕРЕСЕКАЮЩИЕСЯ блоки степеней двойки
     *
     * ПРИМЕР: query(2, 10), длина = 9 = 8 + 1 = 2³ + 2⁰
     * Блок 1: [2, 9]  — st[3][2], длина 8
     * Блок 2: [10, 10] — st[0][10], длина 1
     * Ответ = st[3][2] + st[0][10]
     */
    fun query(l: Int, r: Int): Long {
        var sum = 0L
        var left = l
        var right = r

        /**
         * Жадно выбираем максимальные степени двойки
         *
         * На каждой итерации:
         * 1. k = log[right - left + 1] — максимальная степень, влезающая в [left, right]
         * 2. Добавляем st[k][left] к сумме
         * 3. Сдвигаем left на 2^k
         *
         * Количество итераций = количество единиц в двоичном представлении (right - left + 1)
         * Максимум log(n) итераций
         */
        while (left <= right) {
            val k = log[right - left + 1]
            sum += st[k][left]
            left += (1 shl k)
        }

        return sum
    }
}
```

**Сложность для sum:** O(log n) на запрос — теряем преимущество над Segment Tree.

---

## Продвинутые техники

### 1. 2D Sparse Table

```kotlin
class SparseTable2D(private val matrix: Array<IntArray>) {
    private val n = matrix.size
    private val m = matrix[0].size
    private val logN = 32 - Integer.numberOfLeadingZeros(n)
    private val logM = 32 - Integer.numberOfLeadingZeros(m)

    /**
     * 4D-ТАБЛИЦА для 2D RMQ
     *
     * st[kx][ky][i][j] = min в прямоугольнике размера 2^kx × 2^ky,
     *                     начинающемся в ячейке (i, j)
     *
     * Прямоугольник: от (i, j) до (i + 2^kx - 1, j + 2^ky - 1)
     *
     * Размер: O(n × m × log(n) × log(m))
     *
     * ПРИМЕР: kx=1, ky=2, i=0, j=0
     * Прямоугольник 2×4: строки [0,1], столбцы [0,3]
     */
    private val st = Array(logN) { Array(logM) { Array(n) { IntArray(m) } } }

    init {
        // База: kx=0, ky=0
        for (i in 0 until n) {
            for (j in 0 until m) {
                st[0][0][i][j] = matrix[i][j]
            }
        }

        // Строим по строкам (ky)
        for (kx in 0 until logN) {
            for (ky in (if (kx == 0) 1 else 0) until logM) {
                for (i in 0..n - (1 shl kx)) {
                    for (j in 0..m - (1 shl ky)) {
                        st[kx][ky][i][j] = if (ky == 0) {
                            minOf(
                                st[kx - 1][0][i][j],
                                st[kx - 1][0][i + (1 shl (kx - 1))][j]
                            )
                        } else {
                            minOf(
                                st[kx][ky - 1][i][j],
                                st[kx][ky - 1][i][j + (1 shl (ky - 1))]
                            )
                        }
                    }
                }
            }
        }
    }

    /**
     * O(1) QUERY для прямоугольника [r1, c1] — [r2, c2]
     *
     * Идея та же, что и в 1D: покрываем 4-мя перекрывающимися прямоугольниками
     *
     * Каждая сторона покрывается двумя степенями двойки:
     * - По строкам: блоки [r1, r1+2^kx-1] и [r2-2^kx+1, r2]
     * - По столбцам: блоки [c1, c1+2^ky-1] и [c2-2^ky+1, c2]
     *
     * Итого 2×2 = 4 прямоугольника
     * Для min перекрытие не важно (idempotent)
     */
    fun query(r1: Int, c1: Int, r2: Int, c2: Int): Int {
        val kx = log(r2 - r1 + 1)
        val ky = log(c2 - c1 + 1)

        return minOf(
            minOf(
                st[kx][ky][r1][c1],
                st[kx][ky][r2 - (1 shl kx) + 1][c1]
            ),
            minOf(
                st[kx][ky][r1][c2 - (1 shl ky) + 1],
                st[kx][ky][r2 - (1 shl kx) + 1][c2 - (1 shl ky) + 1]
            )
        )
    }

    private fun log(x: Int) = 31 - Integer.numberOfLeadingZeros(x)
}
```

### 2. LCA с Sparse Table (Euler Tour + RMQ)

```kotlin
class LCAWithSparseTable(adj: List<List<Int>>, root: Int = 0) {
    private val n = adj.size
    private val euler = mutableListOf<Int>()      // Euler tour
    private val depth = mutableListOf<Int>()      // Глубина в Euler tour
    private val first = IntArray(n) { -1 }        // Первое вхождение в Euler

    private lateinit var st: Array<IntArray>
    private lateinit var log: IntArray

    init {
        /**
         * EULER TOUR — обход дерева с записью каждого посещения
         *
         * При DFS записываем вершину каждый раз, когда её посещаем:
         * - При первом входе
         * - При возврате из каждого ребёнка
         *
         * ПРИМЕР для дерева:
         *       0
         *      / \
         *     1   2
         *    /
         *   3
         *
         * Euler tour: [0, 1, 3, 1, 0, 2, 0]
         * Глубины:    [0, 1, 2, 1, 0, 1, 0]
         *
         * LCA(3, 2) = вершина с минимальной глубиной между first[3]=2 и first[2]=5
         * В диапазоне [2,5]: [3,1,0,2] с глубинами [2,1,0,1]
         * Минимальная глубина 0 → вершина 0 = LCA(3, 2)
         */
        dfs(adj, root, 0)
        buildSparseTable()
    }

    private fun dfs(adj: List<List<Int>>, v: Int, d: Int) {
        first[v] = euler.size
        euler.add(v)
        depth.add(d)

        for (u in adj[v]) {
            if (first[u] == -1) {
                dfs(adj, u, d + 1)
                euler.add(v)
                depth.add(d)
            }
        }
    }

    private fun buildSparseTable() {
        val m = euler.size
        val K = 32 - Integer.numberOfLeadingZeros(m)

        log = IntArray(m + 1)
        for (i in 2..m) log[i] = log[i / 2] + 1

        /**
         * ОСОБЕННОСТЬ: храним ИНДЕКСЫ, а не глубины!
         *
         * st[k][i] = индекс в euler с минимальной глубиной в диапазоне [i, i+2^k-1]
         *
         * Почему индексы, а не глубины?
         * - Нам нужно вернуть ВЕРШИНУ, а не глубину
         * - euler[st[k][i]] — вершина с минимальной глубиной
         * - depth[st[k][i]] — её глубина
         *
         * База: st[0][i] = i (сам элемент — минимум на отрезке длины 1)
         */
        st = Array(K) { IntArray(m) }
        for (i in 0 until m) st[0][i] = i

        for (k in 1 until K) {
            for (i in 0..m - (1 shl k)) {
                val left = st[k - 1][i]
                val right = st[k - 1][i + (1 shl (k - 1))]
                st[k][i] = if (depth[left] <= depth[right]) left else right
            }
        }
    }

    /**
     * LCA(u, v) — наименьший общий предок
     *
     * КЛЮЧЕВОЕ НАБЛЮДЕНИЕ:
     * ─────────────────────
     * В Euler tour между первым вхождением u и первым вхождением v
     * содержатся ВСЕ вершины на пути от u до v через LCA
     *
     * LCA — это вершина с МИНИМАЛЬНОЙ ГЛУБИНОЙ в этом диапазоне!
     *
     * ПРИМЕР: LCA(3, 2) в дереве выше
     * first[3] = 2, first[2] = 5
     * Euler[2..5] = [3, 1, 0, 2]
     * Depths     = [2, 1, 0, 1]
     * Минимум глубины 0 в позиции 4 → euler[4] = 0
     * LCA(3, 2) = 0 ✓
     */
    fun lca(u: Int, v: Int): Int {
        var l = first[u]
        var r = first[v]
        if (l > r) { val t = l; l = r; r = t }

        val k = log[r - l + 1]
        val left = st[k][l]
        val right = st[k][r - (1 shl k) + 1]

        return euler[if (depth[left] <= depth[right]) left else right]
    }
}
```

### 3. O(n) построение с помощью ±1 RMQ

Для LCA глубины соседних элементов в Euler tour отличаются на ±1.

```
Идея:
1. Разбить массив на блоки размера log(n)/2
2. Для каждого типа блока предвычислить все RMQ
3. Между блоками — обычный Sparse Table

Типов блоков: 2^(log(n)/2) = √n
Запросы внутри блока: O(1) через precomputed
Запросы между блоками: O(1) через Sparse Table

Итого: O(n) построение, O(1) запрос
```

```kotlin
// Simplified: используется в продвинутых задачах
// Обычно достаточно O(n log n) построения
```

---

## Распространённые ошибки

### 1. Использование для non-idempotent операций

```kotlin
// ❌ НЕПРАВИЛЬНО: sum не idempotent!
fun querySum(l: Int, r: Int): Int {
    val k = log[r - l + 1]
    // sum(A) + sum(B) ≠ sum(A ∪ B) если A и B пересекаются!
    return st[k][l] + st[k][r - (1 shl k) + 1]  // WRONG!
}

// ✅ ПРАВИЛЬНО: для sum используй непересекающиеся блоки
fun querySumCorrect(l: Int, r: Int): Long {
    var sum = 0L
    var left = l
    while (left <= r) {
        val k = log[r - left + 1]
        sum += st[k][left]
        left += (1 shl k)
    }
    return sum
}
```

### 2. Неправильный расчёт границ

```kotlin
// ❌ НЕПРАВИЛЬНО: выход за границы массива
for (k in 1 until K) {
    for (i in 0 until n) {  // i + 2^k может выйти за n!
        st[k][i] = minOf(st[k-1][i], st[k-1][i + (1 shl (k-1))])
    }
}

// ✅ ПРАВИЛЬНО: проверяем границу
for (k in 1 until K) {
    for (i in 0..n - (1 shl k)) {  // i + 2^k - 1 < n
        st[k][i] = minOf(st[k-1][i], st[k-1][i + (1 shl (k-1))])
    }
}
```

### 3. Неправильный log

```kotlin
// ❌ НЕПРАВИЛЬНО: log[0] может быть использован
log[0] = 0  // Проблема: log(0) не определён

// ✅ ПРАВИЛЬНО: начинаем с 1
log[1] = 0
for (i in 2..n) {
    log[i] = log[i / 2] + 1
}
// И проверяем l <= r перед query
```

### 4. Забыть про 1-indexed

```kotlin
// ❌ НЕПРАВИЛЬНО: смешение 0-indexed и 1-indexed
fun query(l: Int, r: Int): Int {  // l, r — 1-indexed от пользователя
    val k = log[r - l + 1]
    return minOf(st[k][l], st[k][r - (1 shl k) + 1])  // но st 0-indexed!
}

// ✅ ПРАВИЛЬНО: конвертируем
fun query(l: Int, r: Int): Int {
    val left = l - 1  // convert to 0-indexed
    val right = r - 1
    val k = log[right - left + 1]
    return minOf(st[k][left], st[k][right - (1 shl k) + 1])
}
```

### 5. Overflow при вычислении степени 2

```kotlin
// ❌ НЕПРАВИЛЬНО: 1 << 31 = отрицательное число
val power = 1 shl k  // если k >= 31, проблема

// ✅ ПРАВИЛЬНО: используй Long для больших k
val power = 1L shl k
```

---

## Когда использовать

### Sparse Table лучше когда:

| Критерий | Почему |
|----------|--------|
| Статический массив | Нет updates |
| Много запросов | O(1) vs O(log n) |
| Idempotent операция | min, max, GCD, AND, OR |
| Память не критична | O(n log n) допустимо |

### Альтернативы

| Ситуация | Используй |
|----------|-----------|
| Нужны updates | Segment Tree |
| Мало памяти | Segment Tree (O(4n)) |
| Non-idempotent | Segment Tree или Fenwick |
| Range update | Segment Tree + Lazy |
| Online построение | Segment Tree |

### Сравнение производительности

```
n = 10^6, q = 10^6 запросов

           |  Build  |  Query  |  Total  | Memory
-----------|---------|---------|---------|--------
Sparse     | 20ms    | 200ms   | 220ms   | 80MB
Segment    | 15ms    | 800ms   | 815ms   | 32MB

Вывод: Sparse Table ~4x быстрее на запросах,
       но потребляет ~2.5x больше памяти
```

---

## Практика

### Концептуальные вопросы

1. **Почему называется "Sparse"?**

   Храним O(n log n) предвычисленных ответов вместо O(n²) всех возможных диапазонов. "Разреженное" хранение.

2. **Почему O(1) только для idempotent?**

   Используем два перекрывающихся блока. Для min: min(min(A), min(B)) = min(A ∪ B). Для sum: sum(A) + sum(B) ≠ sum(A ∪ B) из-за пересечения.

3. **Как адаптировать для max?**

   Заменить `minOf` на `maxOf`. Для GCD: `gcd(a, b)`. Операция должна быть idempotent и ассоциативной.

4. **Почему log[i] = log[i/2] + 1?**

   log₂(i) = log₂(i/2) + 1. Целочисленное деление на 2 = уменьшение логарифма на 1.

### LeetCode задачи

| # | Название | Сложность | Паттерн |
|---|----------|-----------|---------|
| 239 | Sliding Window Maximum | Hard | RMQ |
| 1235 | Maximum Profit in Job Scheduling | Hard | DP + RMQ |
| 2407 | Longest Increasing Subsequence II | Hard | Segment Tree / Sparse |
| 1483 | Kth Ancestor of a Tree Node | Hard | Binary Lifting |

### Задача: LeetCode 239. Sliding Window Maximum

```kotlin
fun maxSlidingWindow(nums: IntArray, k: Int): IntArray {
    val n = nums.size
    if (n == 0) return intArrayOf()

    // Build sparse table for max
    val K = 32 - Integer.numberOfLeadingZeros(n)
    val st = Array(K) { IntArray(n) }
    val log = IntArray(n + 1)

    log[1] = 0
    for (i in 2..n) log[i] = log[i / 2] + 1

    for (i in 0 until n) st[0][i] = nums[i]

    for (j in 1 until K) {
        for (i in 0..n - (1 shl j)) {
            st[j][i] = maxOf(st[j-1][i], st[j-1][i + (1 shl (j-1))])
        }
    }

    // Query for each window
    val result = IntArray(n - k + 1)
    val level = log[k]

    for (i in 0..n - k) {
        result[i] = maxOf(st[level][i], st[level][i + k - (1 shl level)])
    }

    return result
}
```

---

## Sparse Table vs Segment Tree: когда что выбрать

Sparse Table и Segment Tree решают похожие задачи, но их сильные стороны различны. Выбор зависит от конкретной ситуации.

**Sparse Table побеждает когда:**

Массив статический (не меняется после построения), запросов очень много (10^6+), и операция идемпотентна. В этом случае O(1) query -- абсолютное преимущество. На практике Sparse Table в 3-5 раз быстрее Segment Tree на запросах, потому что не требует рекурсии или обхода дерева -- просто два обращения к массиву и одна операция.

**Segment Tree побеждает когда:**

Нужны обновления (Sparse Table не поддерживает их вообще). Также Segment Tree экономнее по памяти: O(4n) против O(n log n). Для n = 10^6: Segment Tree = 16 МБ, Sparse Table = 80 МБ (при 4 байтах на int). На соревнованиях с ограничением памяти 256 МБ это может быть критично.

**Неочевидный случай: O(1) RMQ с O(n) препроцессингом.** Алгоритм Бендера-Фарах-Колтон (2000) комбинирует Sparse Table с блочной декомпозицией, достигая O(n) построения и O(1) запроса. Это теоретически оптимально, но на практике редко используется из-за сложности реализации и большого constant factor.

---

### LCA через Sparse Table: связь между задачами

Одно из самых красивых применений Sparse Table -- решение задачи LCA (Lowest Common Ancestor, наименьший общий предок) в дереве. Казалось бы, LCA и RMQ -- совершенно разные задачи. Но Бендер и Фарах-Колтон показали, что LCA СВОДИТСЯ к RMQ.

Идея такова. Обходим дерево в DFS, записывая каждую вершину при посещении (Euler tour). Для вершин u и v их LCA -- это вершина с МИНИМАЛЬНОЙ ГЛУБИНОЙ между первым вхождением u и первым вхождением v в Euler tour.

Почему это работает? Euler tour проходит через все вершины на пути от u до v. LCA -- самая "высокая" (с минимальной глубиной) вершина на этом пути. Она обязательно встретится между позициями u и v в Euler tour.

```
ДЕРЕВО:                    EULER TOUR:
      0                    Вершины: [0, 1, 3, 1, 4, 1, 0, 2, 5, 2, 0]
     / \                   Глубины: [0, 1, 2, 1, 2, 1, 0, 1, 2, 1, 0]
    1   2                  Позиции:  0  1  2  3  4  5  6  7  8  9  10
   / \   \
  3   4   5                LCA(3, 4):
                             first[3] = 2, first[4] = 4
                             Диапазон [2, 4]: глубины [2, 1, 2]
                             Минимальная глубина = 1 → вершина 1
                             LCA(3, 4) = 1 ✓

                           LCA(3, 5):
                             first[3] = 2, first[5] = 8
                             Диапазон [2, 8]: глубины [2, 1, 2, 1, 0, 1, 2]
                             Минимальная глубина = 0 → вершина 0
                             LCA(3, 5) = 0 ✓
```

Построив Sparse Table над массивом глубин, мы получаем LCA за O(1) с O(n log n) предобработкой. Это одно из самых элегантных сведений в алгоритмике: задача на деревьях решена через задачу на массивах.

---

## Связь с другими темами

**[[segment-tree]]** -- Segment Tree решает более общую задачу: range queries + updates. Sparse Table -- специализированный инструмент для статических данных. Если данные не меняются и операция идемпотентна, Sparse Table быстрее. Во всех остальных случаях -- Segment Tree.

**[[fenwick-tree]]** -- Fenwick Tree эффективен для prefix sum + point update, но не даёт O(1) для RMQ. Для подсчёта суммы на статическом массиве лучше всего подходят обычные prefix sums (O(1) query, O(n) build). Sparse Table нужен именно для min/max/GCD.

**[[trees-binary]]** -- Алгоритм LCA через Euler tour + Sparse Table превращает задачу на деревьях в задачу на массивах. Это фундаментальная связь, которая используется во многих продвинутых алгоритмах (Heavy-Light Decomposition, центроидная декомпозиция).

---

## Источники и дальнейшее чтение

- **Bender, M. & Farach-Colton, M. (2000). The LCA Problem Revisited.** -- Оригинальная статья, показавшая сведение LCA к RMQ и алгоритм O(n) построения для +-1 RMQ. Фундаментальная работа в области алгоритмов на деревьях.

- **Cormen, T. et al. (2009). Introduction to Algorithms (CLRS).** -- Хотя CLRS не описывает Sparse Table напрямую, главы о динамическом программировании и amortized analysis дают теоретическую базу для понимания препроцессинга.

- **Halim, S. (2013). Competitive Programming 3, Chapter 2.4.** -- Практическое руководство по Sparse Table в контексте олимпиадного программирования. Включает примеры задач и сравнение с альтернативами.

- **CP-Algorithms (cp-algorithms.com/data_structures/sparse-table.html).** -- Полное руководство с реализациями на C++ и разбором всех вариантов (idempotent/non-idempotent, 2D, LCA).

---

*Последнее обновление: 2026-02-10 -- Добавлена глубокая теория идемпотентности (почему именно она даёт O(1)), сравнение с Segment Tree (когда какой выбирать), LCA через Sparse Table (сведение задачи на дереве к RMQ)*
