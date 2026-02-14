---
title: "Паттерн двух куч (Two Heaps)"
created: 2026-02-08
modified: 2026-02-13
type: deep-dive
status: published
difficulty: intermediate
confidence: high
cs-foundations:
  - heap-operations
  - median-computation
  - streaming-algorithms
  - data-partitioning
  - balanced-structures
prerequisites:
  - "[[heaps-priority-queues]]"
  - "[[big-o-complexity]]"
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/intermediate
  - pattern
  - interview
related:
  - "[[heaps-priority-queues]]"
  - "[[k-way-merge-pattern]]"
  - "[[top-k-elements-pattern]]"
  - "[[sliding-window-pattern]]"
reading_time: 51
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Two Heaps Pattern

## TL;DR

Two Heaps — паттерн для поддержания **медианы** потока данных или **оптимальных выборов** с двух сторон. Использует **Max-Heap для нижней половины** и **Min-Heap для верхней половины**. Медиана = вершина Max-Heap (нечётное количество) или среднее вершин обеих куч (чётное). **Сложность:** добавление O(log n), получение медианы O(1). Ключевые задачи: Find Median from Data Stream, Sliding Window Median, IPO (Maximize Capital).

---

## Часть 1: Интуиция без кода

> **Цель:** понять ИДЕЮ Two Heaps до любого кода.

### Ты уже знаешь этот паттерн

Этот паттерн встречается в повседневной жизни:

| Ситуация | Как это работает | Паттерн |
|----------|------------------|---------|
| **Балансирование весов** | Половина грузов слева, половина справа | Two equal halves |
| **Медианная зарплата** | 50% зарабатывает меньше, 50% больше | Median tracking |
| **Выбор проекта** | Нужен доступный (min cost) с max profit | Two criteria |
| **Разделение класса** | Половина отличников, половина остальных | Partitioning |

### Аналогия 1: Балансирование качелей

```
Представь качели с грузами на обеих сторонах:

         ЛЕВАЯ                  ПРАВАЯ
       (меньшие)               (большие)
    ┌───────────┐           ┌───────────┐
    │ 1  3  5   │     ⚖     │   7  9    │
    └───────────┘           └───────────┘
        MAX = 5                 MIN = 7

Медиана = (5 + 7) / 2 = 6

ПРАВИЛА:
1. Левая сторона держит МЕНЬШИЕ числа (Max-Heap — знаем максимум)
2. Правая сторона держит БОЛЬШИЕ числа (Min-Heap — знаем минимум)
3. Размеры отличаются максимум на 1

Добавляем число 4:
  4 < 5 (max левой) → кладём влево
  Левая: [1, 3, 4, 5], Правая: [7, 9]
  Левая на 2 больше → ПЕРЕБАЛАНСИРОВКА!
  Перемещаем 5 вправо:
  Левая: [1, 3, 4], Правая: [5, 7, 9]

  Медиана = 5 (вершина правой, т.к. нечётное количество)
```

### Аналогия 2: Разделение класса по успеваемости

```
Класс из 10 учеников, нужно найти "среднего" ученика.

Оценки (случайный порядок): 85, 72, 91, 65, 78, 88, 70, 95, 82, 76

НАИВНЫЙ СПОСОБ:
  Отсортируй все: [65, 70, 72, 76, 78, 82, 85, 88, 91, 95]
  Медиана = (78 + 82) / 2 = 80
  Каждое добавление: O(n log n) на сортировку!

TWO HEAPS:
  Нижняя половина (Max-Heap): [65, 70, 72, 76, 78] → MAX = 78
  Верхняя половина (Min-Heap): [82, 85, 88, 91, 95] → MIN = 82
  Медиана = (78 + 82) / 2 = 80
  Добавление нового ученика: O(log n)!

Приходит новый ученик с оценкой 80:
  80 > 78 (max нижней) → кладём в верхнюю
  Нижняя: [65, 70, 72, 76, 78] (5 элементов)
  Верхняя: [80, 82, 85, 88, 91, 95] (6 элементов)

  Разница > 1 → перебалансировка!
  Перемещаем 80 в нижнюю:
  Нижняя: [65, 70, 72, 76, 78, 80] → MAX = 80
  Верхняя: [82, 85, 88, 91, 95] → MIN = 82

  Медиана = (80 + 82) / 2 = 81
```

### Аналогия 3: Выбор проекта (IPO)

```
Инвестор с начальным капиталом 0. Проекты:

Проект | Капитал (нужен) | Прибыль
-------|-----------------|--------
   A   |       0         |    1
   B   |       1         |    2
   C   |       2         |    3

Можно выбрать 2 проекта. Как максимизировать прибыль?

ИДЕЯ: Два heap'а!
  Min-Heap по капиталу: все проекты, отсортированные по требуемому капиталу
  Max-Heap по прибыли: проекты, которые МОЖЕМ выполнить

Шаг 1: Капитал = 0
  Доступные проекты: только A (нужен капитал 0)
  Max-Heap по прибыли: [A(1)]
  Выбираем A → прибыль 1
  Капитал = 0 + 1 = 1

Шаг 2: Капитал = 1
  Доступные: A уже взят, B (нужен 1) — добавляем в Max-Heap
  Max-Heap: [B(2)]
  Выбираем B → прибыль 2
  Капитал = 1 + 2 = 3

Итого: максимальный капитал = 3
```

### Главный инсайт: Почему два heap'а?

```
┌─────────────────────────────────────────────────────────────────┐
│                    КЛЮЧЕВОЕ НАБЛЮДЕНИЕ                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ЗАДАЧА: Поддерживать медиану потока чисел                      │
│                                                                 │
│  НАИВНО: Хранить отсортированный массив                         │
│          Добавление: O(n) (вставка в отсортированный)           │
│          Медиана: O(1) (середина массива)                       │
│                                                                 │
│  TWO HEAPS:                                                     │
│          Добавление: O(log n) (вставка в heap)                  │
│          Медиана: O(1) (вершины heap'ов)                        │
│                                                                 │
│  ПОЧЕМУ РАБОТАЕТ:                                               │
│                                                                 │
│  Max-Heap (левая половина)  |  Min-Heap (правая половина)       │
│  Хранит МЕНЬШИЕ числа       |  Хранит БОЛЬШИЕ числа             │
│  MAX на вершине             |  MIN на вершине                   │
│                                                                 │
│         [меньшие]           |         [большие]                 │
│      ...  <  MAX      ≤     |    ≤     MIN  <  ...              │
│                        ↑    |    ↑                              │
│                        МЕДИАНА                                  │
│                                                                 │
│  Медиана = MAX (если нечётное) или (MAX + MIN) / 2              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Часть 2: Почему Two Heaps бывает сложен?

> **Цель:** понять типичные трудности и как их избежать.

### Типичные трудности

#### 1. Куда добавлять новый элемент?

```kotlin
// ПРАВИЛО:
// Если num <= maxHeap.peek() → в maxHeap (левая половина)
// Иначе → в minHeap (правая половина)

fun addNum(num: Int) {
    // Сначала всегда пробуем в maxHeap
    if (maxHeap.isEmpty() || num <= maxHeap.peek()) {
        maxHeap.offer(num)
    } else {
        minHeap.offer(num)
    }

    // Затем балансируем
    rebalance()
}

// ОШИБКА — добавлять без логики:
// maxHeap.offer(num)  // Нарушит свойство разделения!
```

#### 2. Когда и как балансировать?

```kotlin
// ИНВАРИАНТ:
// |maxHeap.size - minHeap.size| <= 1
// maxHeap.size >= minHeap.size (или равны)

fun rebalance() {
    // maxHeap переполнен
    if (maxHeap.size > minHeap.size + 1) {
        minHeap.offer(maxHeap.poll())
    }
    // minHeap переполнен
    else if (minHeap.size > maxHeap.size) {
        maxHeap.offer(minHeap.poll())
    }
}

// ОШИБКА — забыть балансировку:
// Размеры могут разойтись на 2+, медиана будет неверной!
```

#### 3. Как вычислить медиану?

```kotlin
fun findMedian(): Double {
    return when {
        // Нечётное количество → медиана в maxHeap
        maxHeap.size > minHeap.size -> maxHeap.peek().toDouble()

        // Чётное количество → среднее вершин
        else -> (maxHeap.peek() + minHeap.peek()) / 2.0
    }
}

// ОШИБКА — забыть про .toDouble():
// (3 + 4) / 2 = 3 (integer division!)
// (3 + 4) / 2.0 = 3.5 (правильно)
```

#### 4. Удаление элемента (Sliding Window Median)

```kotlin
// ПРОБЛЕМА: Heap не поддерживает удаление произвольного элемента!

// РЕШЕНИЕ: Lazy deletion (отложенное удаление)
// Храним HashMap<Int, Int> с количеством "удалённых" элементов
// При poll() проверяем, не был ли элемент "удалён"

val toRemove = mutableMapOf<Int, Int>()

fun remove(num: Int) {
    toRemove[num] = toRemove.getOrDefault(num, 0) + 1
}

fun prune(heap: PriorityQueue<Int>) {
    while (heap.isNotEmpty() && toRemove.getOrDefault(heap.peek(), 0) > 0) {
        val top = heap.poll()
        toRemove[top] = toRemove[top]!! - 1
    }
}
```

### Что отличает новичка от эксперта

| Новичок | Эксперт |
|---------|---------|
| Добавляет в случайный heap | Сравнивает с maxHeap.peek() |
| Забывает балансировку | Всегда вызывает rebalance() |
| Integer division при медиане | Использует .toDouble() или 2.0 |
| Не знает про lazy deletion | Применяет HashMap для удалений |
| Путает Max и Min heaps | Знает: Max для меньших, Min для больших |

---

## Часть 3: Ментальные модели для Two Heaps

> **Цель:** дать разные способы ДУМАТЬ о паттерне.

### Модель 1: "Разделение на две половины"

**Идея:** Всегда держи данные разделёнными на две половины, где максимум левой ≤ минимума правой.

```
┌─────────────────────────────────────────────────────────────────┐
│                    РАЗДЕЛЕНИЕ НА ПОЛОВИНЫ                       │
│                                                                 │
│   Все числа: 1, 3, 5, 7, 9, 11                                 │
│                                                                 │
│   ЛЕВАЯ (Max-Heap)        ПРАВАЯ (Min-Heap)                    │
│   ┌─────────────┐         ┌─────────────┐                      │
│   │  1, 3, 5    │         │  7, 9, 11   │                      │
│   │   MAX = 5   │    ≤    │   MIN = 7   │                      │
│   └─────────────┘         └─────────────┘                      │
│                                                                 │
│   Медиана = (5 + 7) / 2 = 6                                    │
│                                                                 │
│   ИНВАРИАНТЫ:                                                  │
│   1. maxHeap.peek() ≤ minHeap.peek()                           │
│   2. |sizes| ≤ 1                                               │
│   3. maxHeap.size ≥ minHeap.size                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Модель 2: "Фильтр двух критериев"

**Идея:** Два heap'а для разных критериев оптимизации.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ФИЛЬТР ДВУХ КРИТЕРИЕВ (IPO)                  │
│                                                                 │
│   Проекты: (capital, profit)                                   │
│   (0, 1), (1, 2), (1, 3), (2, 4)                               │
│                                                                 │
│   Min-Heap (по capital)      Max-Heap (по profit)              │
│   ┌─────────────────┐        ┌─────────────────┐               │
│   │ Все проекты     │   →    │ Доступные       │               │
│   │ sorted by       │   →    │ проекты sorted  │               │
│   │ капиталу        │   →    │ by прибыли      │               │
│   └─────────────────┘        └─────────────────┘               │
│                                                                 │
│   Алгоритм:                                                    │
│   1. Перемести все доступные (capital ≤ current) в Max-Heap    │
│   2. Выбери проект с max profit                                │
│   3. Обнови текущий капитал                                    │
│   4. Повтори k раз                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Модель 3: "Скользящее окно с двумя heap'ами"

**Идея:** Поддержание медианы в скользящем окне.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SLIDING WINDOW MEDIAN                        │
│                                                                 │
│   Массив: [1, 3, -1, -3, 5, 3, 6, 7], окно k=3                 │
│                                                                 │
│   Окно [1, 3, -1]:                                             │
│     MaxHeap: [-1, 1]  →  max = 1                               │
│     MinHeap: [3]      →  min = 3                               │
│     Медиана = 1                                                │
│                                                                 │
│   Сдвиг: удаляем 1, добавляем -3                               │
│   Окно [3, -1, -3]:                                            │
│     Lazy delete: помечаем 1 как удалённый                      │
│     Добавляем -3 в MaxHeap                                     │
│     Перебалансируем...                                         │
│     Медиана = -1                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Зачем это нужно?

**Реальная проблема:**

Поток данных о ценах акций — 1 миллион значений в секунду. Нужно в реальном времени показывать медиану.

- **Сортировка:** O(n log n) на каждое значение = невозможно
- **Two Heaps:** O(log n) на добавление = 1 миллион за секунду!

**Где используется:**

| Область | Применение | Пример |
|---------|------------|--------|
| **Финансы** | Real-time медиана цен | Trading platforms |
| **Streaming** | Медиана метрик | Prometheus, Datadog |
| **Рекомендации** | Медианный рейтинг | Netflix, Spotify |
| **Игры** | Matchmaking по скиллу | ELO rating systems |
| **Аналитика** | Percentile вычисления | P50, P90 latency |

**Статистика:**
- Входит в "Grokking the Coding Interview" как Pattern #9
- Amazon задаёт этот паттерн очень часто
- LeetCode: 10+ задач

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Heap / Priority Queue** | Основная структура | [[heaps-priority-queues]] |
| **Max-Heap vs Min-Heap** | Понимание направления | [[heaps-priority-queues]] |
| **Big O нотация** | Понимание O(log n) | [[big-o-complexity]] |
| **Медиана** | Что это и зачем нужна | Базовая статистика |

---

## Что это такое?

### Объяснение для 5-летнего

Представь, что ты играешь с друзьями и хочешь всегда знать, кто "средний" по росту.

У тебя две команды:
- Команда "Малыши" — там самый высокий стоит впереди
- Команда "Гиганты" — там самый низкий стоит впереди

Когда приходит новый друг:
1. Сравни его с высоким из "Малышей"
2. Если он меньше — иди в "Малыши"
3. Если больше — иди в "Гиганты"
4. Следи, чтобы команды были примерно равные!

"Средний" — это либо высокий "Малыш", либо среднее между ним и низким "Гигантом".

```
Малыши: 🧒🧒🧒     Гиганты: 🧑🧑
        ↑ самый              ↑ самый
          высокий              низкий

Средний = между ними!
```

### Формальное определение

**Two Heaps** — паттерн для эффективного вычисления медианы или решения задач оптимизации с двумя критериями, использующий Max-Heap для нижней половины данных и Min-Heap для верхней половины.

**Ключевые свойства:**
- **Max-Heap:** хранит меньшую половину, максимум на вершине
- **Min-Heap:** хранит большую половину, минимум на вершине
- **Инвариант:** max(MaxHeap) ≤ min(MinHeap)
- **Баланс:** размеры отличаются максимум на 1

**Варианты задач:**

```
1. Find Median from Data Stream
   Поток чисел → медиана в любой момент

2. Sliding Window Median
   Массив + размер окна → медианы для каждой позиции

3. IPO / Maximize Capital
   Проекты (capital, profit) → максимальный капитал после k проектов

4. Find Right Interval
   Интервалы → для каждого найти "правый" (начало ≥ конца текущего)
```

---

## Терминология

| Термин | Определение | Пример |
|--------|-------------|--------|
| **Max-Heap** | Куча, где максимум на вершине | Для нижней половины |
| **Min-Heap** | Куча, где минимум на вершине | Для верхней половины |
| **Median** | Центральное значение отсортированных данных | Для [1,3,5] → 3 |
| **Rebalance** | Выравнивание размеров heap'ов | Перемещение элементов |
| **Lazy Deletion** | Отложенное удаление | Пометка + удаление при poll |
| **Streaming** | Обработка данных по мере поступления | Real-time analytics |

---

## Как это работает?

### Задача 1: Find Median from Data Stream

```
Поток: 1, 5, 2, 10, 3

После добавления 1:
  MaxHeap: [1]        MinHeap: []
  Медиана: 1

После добавления 5:
  5 > 1 → в MinHeap
  MaxHeap: [1]        MinHeap: [5]
  Медиана: (1 + 5) / 2 = 3.0

После добавления 2:
  2 > 1 → в MinHeap
  MaxHeap: [1]        MinHeap: [2, 5]
  MinHeap > MaxHeap → перебалансировка
  MaxHeap: [1, 2]     MinHeap: [5]
  Медиана: 2

После добавления 10:
  10 > 2 → в MinHeap
  MaxHeap: [1, 2]     MinHeap: [5, 10]
  Медиана: (2 + 5) / 2 = 3.5

После добавления 3:
  3 > 2 → в MinHeap
  MaxHeap: [1, 2]     MinHeap: [3, 5, 10]
  MinHeap > MaxHeap → перебалансировка
  MaxHeap: [1, 2, 3]  MinHeap: [5, 10]
  Медиана: 3
```

### Задача 2: Sliding Window Median

```
Массив: [1, 3, -1, -3, 5, 3, 6, 7], k = 3

Окно [1, 3, -1]:
  Sorted: [-1, 1, 3]
  MaxHeap: [-1, 1]  MinHeap: [3]
  Медиана: 1

Сдвиг → удаляем 1, добавляем -3
Окно [3, -1, -3]:
  Lazy delete: 1 помечен
  Добавляем -3 в MaxHeap
  MaxHeap: [-3, -1, (1)*]  MinHeap: [3]
  (* помечен как удалённый)
  После prune и rebalance:
  Медиана: -1

...и так далее

Результат: [1, -1, -1, 3, 5, 6]
```

### Задача 3: IPO (Maximize Capital)

```
k = 2 проекта, начальный капитал W = 0
Проекты: profits = [1, 2, 3], capital = [0, 1, 1]

Шаг 0: W = 0
  Min-Heap по capital: [(0,1), (1,2), (1,3)]
  Доступные (capital ≤ 0): (0,1)
  Max-Heap по profit: [(1)]
  Выбираем проект с profit=1
  W = 0 + 1 = 1

Шаг 1: W = 1
  Доступные (capital ≤ 1): (1,2), (1,3) → добавляем в Max-Heap
  Max-Heap: [(3), (2)]
  Выбираем проект с profit=3
  W = 1 + 3 = 4

Результат: W = 4
```

---

## Сложность операций

| Операция | Время | Примечание |
|----------|-------|------------|
| addNum() | O(log n) | Вставка + балансировка |
| findMedian() | O(1) | Вершины heap'ов |
| removeNum() | O(log n)* | *С lazy deletion |
| Sliding Window Median | O(n log k) | n позиций, k размер окна |

**Сравнение с альтернативами:**

| Подход | Добавление | Медиана | Память |
|--------|------------|---------|--------|
| Сортированный массив | O(n) | O(1) | O(n) |
| **Two Heaps** | O(log n) | O(1) | O(n) |
| Balanced BST | O(log n) | O(log n) | O(n) |

---

## Реализация

### Kotlin

```kotlin
import java.util.PriorityQueue

// ═══════════════════════════════════════════════════════════════════════════
// MEDIAN FINDER (LeetCode 295)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Поддерживает медиану потока чисел.
 *
 * ИДЕЯ: Max-Heap для нижней половины, Min-Heap для верхней.
 *       Медиана = вершина Max-Heap (нечётное) или среднее вершин (чётное).
 */
class MedianFinder {
    // Max-Heap для нижней половины (меньшие числа)
    private val maxHeap = PriorityQueue<Int>(reverseOrder())

    // Min-Heap для верхней половины (большие числа)
    private val minHeap = PriorityQueue<Int>()

    /**
     * Добавляет число в структуру.
     * Время: O(log n)
     */
    fun addNum(num: Int) {
        // Решаем, куда добавить
        if (maxHeap.isEmpty() || num <= maxHeap.peek()) {
            maxHeap.offer(num)
        } else {
            minHeap.offer(num)
        }

        // Балансируем heap'ы
        rebalance()
    }

    /**
     * Возвращает текущую медиану.
     * Время: O(1)
     */
    fun findMedian(): Double {
        return when {
            maxHeap.size > minHeap.size -> maxHeap.peek().toDouble()
            else -> (maxHeap.peek() + minHeap.peek()) / 2.0
        }
    }

    /**
     * Балансирует heap'ы так, чтобы:
     * - maxHeap.size == minHeap.size или maxHeap.size == minHeap.size + 1
     */
    private fun rebalance() {
        if (maxHeap.size > minHeap.size + 1) {
            minHeap.offer(maxHeap.poll())
        } else if (minHeap.size > maxHeap.size) {
            maxHeap.offer(minHeap.poll())
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// SLIDING WINDOW MEDIAN (LeetCode 480)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Возвращает медианы для каждой позиции скользящего окна.
 *
 * ИДЕЯ: Two Heaps + Lazy Deletion.
 *       Помечаем элементы для удаления, удаляем при poll().
 */
fun medianSlidingWindow(nums: IntArray, k: Int): DoubleArray {
    val maxHeap = PriorityQueue<Int>(reverseOrder())
    val minHeap = PriorityQueue<Int>()
    val toRemove = mutableMapOf<Int, Int>()  // Lazy deletion
    val result = DoubleArray(nums.size - k + 1)

    // Инициализация первого окна
    for (i in 0 until k) {
        maxHeap.offer(nums[i])
    }
    // Перебалансировка: половина в minHeap
    repeat(k / 2) {
        minHeap.offer(maxHeap.poll())
    }

    result[0] = getMedian(maxHeap, minHeap, k)

    for (i in k until nums.size) {
        val outNum = nums[i - k]  // Удаляем из окна
        val inNum = nums[i]       // Добавляем в окно

        // Помечаем для удаления
        toRemove[outNum] = toRemove.getOrDefault(outNum, 0) + 1
        var balance = if (outNum <= maxHeap.peek()) -1 else 1

        // Добавляем новый элемент
        if (maxHeap.isNotEmpty() && inNum <= maxHeap.peek()) {
            maxHeap.offer(inNum)
            balance++
        } else {
            minHeap.offer(inNum)
            balance--
        }

        // Перебалансировка
        if (balance > 0) {
            maxHeap.offer(minHeap.poll())
        } else if (balance < 0) {
            minHeap.offer(maxHeap.poll())
        }

        // Очистка удалённых элементов с вершин
        prune(maxHeap, toRemove)
        prune(minHeap, toRemove)

        result[i - k + 1] = getMedian(maxHeap, minHeap, k)
    }

    return result
}

private fun prune(heap: PriorityQueue<Int>, toRemove: MutableMap<Int, Int>) {
    while (heap.isNotEmpty() && toRemove.getOrDefault(heap.peek(), 0) > 0) {
        val top = heap.poll()
        toRemove[top] = toRemove[top]!! - 1
    }
}

private fun getMedian(maxHeap: PriorityQueue<Int>, minHeap: PriorityQueue<Int>, k: Int): Double {
    return if (k % 2 == 1) {
        maxHeap.peek().toDouble()
    } else {
        (maxHeap.peek().toLong() + minHeap.peek().toLong()) / 2.0
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// IPO - MAXIMIZE CAPITAL (LeetCode 502)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Максимизирует капитал после k проектов.
 *
 * ИДЕЯ: Min-Heap по capital, Max-Heap по profit.
 *       На каждом шаге: добавь доступные проекты, выбери с max profit.
 */
fun findMaximizedCapital(k: Int, w: Int, profits: IntArray, capital: IntArray): Int {
    val n = profits.size

    // Min-Heap: проекты по требуемому капиталу
    val capitalHeap = PriorityQueue<Int>(compareBy { capital[it] })
    for (i in 0 until n) {
        capitalHeap.offer(i)
    }

    // Max-Heap: доступные проекты по прибыли
    val profitHeap = PriorityQueue<Int>(compareByDescending { profits[it] })

    var currentCapital = w

    repeat(k) {
        // Перемещаем доступные проекты в profitHeap
        while (capitalHeap.isNotEmpty() && capital[capitalHeap.peek()] <= currentCapital) {
            profitHeap.offer(capitalHeap.poll())
        }

        // Если нет доступных проектов — выходим
        if (profitHeap.isEmpty()) return currentCapital

        // Выбираем проект с максимальной прибылью
        currentCapital += profits[profitHeap.poll()]
    }

    return currentCapital
}

// ═══════════════════════════════════════════════════════════════════════════
// FIND RIGHT INTERVAL (LeetCode 436)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Для каждого интервала находит "правый" (start ≥ end текущего).
 *
 * ИДЕЯ: Max-Heap по end, Min-Heap по start.
 */
fun findRightInterval(intervals: Array<IntArray>): IntArray {
    val n = intervals.size
    val result = IntArray(n) { -1 }

    // Max-Heap по end (индексы)
    val endHeap = PriorityQueue<Int>(compareByDescending { intervals[it][1] })
    // Min-Heap по start (индексы)
    val startHeap = PriorityQueue<Int>(compareBy { intervals[it][0] })

    for (i in 0 until n) {
        endHeap.offer(i)
        startHeap.offer(i)
    }

    while (endHeap.isNotEmpty() && startHeap.isNotEmpty()) {
        val endIdx = endHeap.peek()
        val endVal = intervals[endIdx][1]

        // Найди минимальный start >= endVal
        while (startHeap.isNotEmpty() && intervals[startHeap.peek()][0] < endVal) {
            startHeap.poll()
        }

        if (startHeap.isNotEmpty()) {
            result[endIdx] = startHeap.peek()
        }

        endHeap.poll()
    }

    return result
}
```

### Python

```python
import heapq
from typing import List

# ═══════════════════════════════════════════════════════════════════════════
# MEDIAN FINDER (LeetCode 295)
# ═══════════════════════════════════════════════════════════════════════════

class MedianFinder:
    """
    Поддерживает медиану потока чисел.

    Max-Heap (нижняя половина): используем отрицательные числа
    Min-Heap (верхняя половина): обычный heapq
    """

    def __init__(self):
        self.max_heap = []  # Отрицательные для симуляции max-heap
        self.min_heap = []

    def addNum(self, num: int) -> None:
        """Добавляет число. O(log n)"""
        # Добавляем в max_heap или min_heap
        if not self.max_heap or num <= -self.max_heap[0]:
            heapq.heappush(self.max_heap, -num)
        else:
            heapq.heappush(self.min_heap, num)

        # Балансируем
        self._rebalance()

    def findMedian(self) -> float:
        """Возвращает медиану. O(1)"""
        if len(self.max_heap) > len(self.min_heap):
            return -self.max_heap[0]
        return (-self.max_heap[0] + self.min_heap[0]) / 2.0

    def _rebalance(self) -> None:
        if len(self.max_heap) > len(self.min_heap) + 1:
            heapq.heappush(self.min_heap, -heapq.heappop(self.max_heap))
        elif len(self.min_heap) > len(self.max_heap):
            heapq.heappush(self.max_heap, -heapq.heappop(self.min_heap))


# ═══════════════════════════════════════════════════════════════════════════
# SLIDING WINDOW MEDIAN (LeetCode 480)
# ═══════════════════════════════════════════════════════════════════════════

def medianSlidingWindow(nums: List[int], k: int) -> List[float]:
    """
    Медианы скользящего окна с lazy deletion.
    """
    from collections import defaultdict

    max_heap = []  # Отрицательные числа
    min_heap = []
    to_remove = defaultdict(int)
    result = []

    def add(num):
        if not max_heap or num <= -max_heap[0]:
            heapq.heappush(max_heap, -num)
        else:
            heapq.heappush(min_heap, num)

    def rebalance():
        while len(max_heap) > len(min_heap) + 1:
            heapq.heappush(min_heap, -heapq.heappop(max_heap))
        while len(min_heap) > len(max_heap):
            heapq.heappush(max_heap, -heapq.heappop(min_heap))

    def prune(heap, is_max=False):
        while heap:
            val = -heap[0] if is_max else heap[0]
            if to_remove[val] > 0:
                to_remove[val] -= 1
                heapq.heappop(heap)
            else:
                break

    def get_median():
        if k % 2 == 1:
            return float(-max_heap[0])
        return (-max_heap[0] + min_heap[0]) / 2.0

    # Инициализация первого окна
    for i in range(k):
        add(nums[i])
    rebalance()
    result.append(get_median())

    # Скользящее окно
    for i in range(k, len(nums)):
        out_num = nums[i - k]
        in_num = nums[i]

        # Помечаем для удаления
        to_remove[out_num] += 1

        # Добавляем новый
        add(in_num)
        rebalance()

        # Очищаем
        prune(max_heap, is_max=True)
        prune(min_heap, is_max=False)
        rebalance()

        result.append(get_median())

    return result


# ═══════════════════════════════════════════════════════════════════════════
# IPO - MAXIMIZE CAPITAL (LeetCode 502)
# ═══════════════════════════════════════════════════════════════════════════

def findMaximizedCapital(k: int, w: int, profits: List[int], capital: List[int]) -> int:
    """
    Максимизирует капитал после k проектов.
    """
    n = len(profits)

    # (capital, index) для min-heap
    cap_heap = [(capital[i], i) for i in range(n)]
    heapq.heapify(cap_heap)

    # Max-heap по profit (отрицательные)
    profit_heap = []

    current_capital = w

    for _ in range(k):
        # Перемещаем доступные проекты
        while cap_heap and cap_heap[0][0] <= current_capital:
            _, idx = heapq.heappop(cap_heap)
            heapq.heappush(profit_heap, -profits[idx])

        if not profit_heap:
            break

        current_capital += -heapq.heappop(profit_heap)

    return current_capital
```

---

## Когда применять Two Heaps?

### Сигналы для распознавания

```
Используй Two Heaps, если:

✅ "Найти медиану потока/окна"
✅ "Поддерживать баланс двух половин"
✅ "Оптимизация по двум критериям" (min одного, max другого)
✅ "Streaming данные с real-time статистикой"
✅ "Sliding window + медиана/percentile"

НЕ используй Two Heaps, если:

❌ Нужен только min или только max → одна куча
❌ Top K элементов → один heap размера K
❌ Merge K списков → K-way merge
❌ Статические данные → просто отсортируй
```

### Шаблон решения

```
1. СОЗДАЙ два heap'а:
   maxHeap (нижняя половина, меньшие)
   minHeap (верхняя половина, большие)

2. ДОБАВЛЕНИЕ:
   if num <= maxHeap.peek():
       maxHeap.add(num)
   else:
       minHeap.add(num)
   rebalance()

3. БАЛАНСИРОВКА:
   if maxHeap.size > minHeap.size + 1:
       minHeap.add(maxHeap.poll())
   if minHeap.size > maxHeap.size:
       maxHeap.add(minHeap.poll())

4. МЕДИАНА:
   if maxHeap.size > minHeap.size:
       return maxHeap.peek()
   else:
       return (maxHeap.peek() + minHeap.peek()) / 2.0
```

---

## Частые ошибки и как их избежать

### Ошибка 1: Integer division при вычислении медианы

```kotlin
// НЕПРАВИЛЬНО:
return (maxHeap.peek() + minHeap.peek()) / 2  // Integer!

// ПРАВИЛЬНО:
return (maxHeap.peek() + minHeap.peek()) / 2.0  // Double
```

### Ошибка 2: Неправильный порядок сравнения

```kotlin
// НЕПРАВИЛЬНО:
if (num < maxHeap.peek()) ...  // Равные идут куда?

// ПРАВИЛЬНО:
if (num <= maxHeap.peek()) ...  // Равные идут в maxHeap
```

### Ошибка 3: Забыть балансировку

```kotlin
// НЕПРАВИЛЬНО:
fun addNum(num: Int) {
    if (num <= maxHeap.peek()) maxHeap.offer(num)
    else minHeap.offer(num)
    // Где rebalance?!
}

// ПРАВИЛЬНО:
fun addNum(num: Int) {
    ...
    rebalance()  // ОБЯЗАТЕЛЬНО!
}
```

---

## Связанные паттерны

| Паттерн | Связь | Когда использовать вместо Two Heaps |
|---------|-------|-----------------------------------|
| [[top-k-elements-pattern]] | Один heap | Когда нужен только top K |
| [[k-way-merge-pattern]] | Множество heap'ов | Merge K sorted lists |
| [[sliding-window-pattern]] | Оба для окна | Когда не нужна медиана |
| [[heaps-priority-queues]] | Базовая структура | Изучение heap |

---

## Практические задачи

### Уровень: Сложный

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 295 | [Find Median from Data Stream](https://leetcode.com/problems/find-median-from-data-stream/) | Базовый Two Heaps |
| 480 | [Sliding Window Median](https://leetcode.com/problems/sliding-window-median/) | Two Heaps + Lazy Deletion |
| 502 | [IPO](https://leetcode.com/problems/ipo/) | Min-Heap по capital, Max по profit |
| 436 | [Find Right Interval](https://leetcode.com/problems/find-right-interval/) | Max-Heap по end, Min по start |

---

## Мифы и реальность

### Миф 1: "Можно использовать один отсортированный массив"

**Реальность:**
- Массив: O(n) на вставку
- Two Heaps: O(log n) на вставку

Для 1 миллиона элементов: 1 миллион vs 20 операций!

### Миф 2: "Max-Heap хранит большие числа"

**Реальность:** Наоборот!
- Max-Heap → **меньшие** числа (хотим знать MAX среди них)
- Min-Heap → **большие** числа (хотим знать MIN среди них)

### Миф 3: "Python heapq поддерживает max-heap"

**Реальность:** Python heapq — только min-heap.
Для max-heap: храни отрицательные числа (`-num`).

---

## Ключевые выводы

```
┌─────────────────────────────────────────────────────────────────┐
│                       TWO HEAPS PATTERN                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  КОГДА:                                                         │
│  • Медиана потока/окна                                          │
│  • Оптимизация по двум критериям                                │
│  • Real-time статистика                                         │
│                                                                 │
│  КАК:                                                           │
│  • Max-Heap для меньшей половины                                │
│  • Min-Heap для большей половины                                │
│  • Балансируй: |sizes| ≤ 1                                      │
│  • Медиана = peek(max) или avg(peek(max), peek(min))            │
│                                                                 │
│  СЛОЖНОСТЬ:                                                     │
│  • Добавление: O(log n)                                         │
│  • Медиана: O(1)                                                │
│                                                                 │
│  КЛЮЧЕВЫЕ ИНВАРИАНТЫ:                                           │
│  • max(MaxHeap) ≤ min(MinHeap)                                  │
│  • maxHeap.size ≥ minHeap.size                                  │
│  • |sizes| ≤ 1                                                  │
│                                                                 │
│  ПРОВЕРКА ПОНИМАНИЯ:                                            │
│  • Почему Max-Heap для МЕНЬШИХ чисел?                           │
│  • Как обработать удаление (sliding window)?                    │
│  • Почему / 2.0, а не / 2?                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Связь с другими темами

### [[heaps-priority-queues]]
Two Heaps полностью построен на двух heap: Max-Heap для нижней половины и Min-Heap для верхней. Понимание heap operations (insert, extract, peek) и свойства heap order — обязательное условие для реализации паттерна. Ключевой момент: Max-Heap даёт доступ к максимуму нижней половины за O(1), Min-Heap — к минимуму верхней за O(1), что позволяет вычислять медиану мгновенно. Без Heaps & Priority Queues невозможно понять, почему балансировка двух куч гарантирует корректность.

### [[k-way-merge-pattern]]
K-way Merge и Two Heaps — оба используют heap для потоковой обработки данных, но с разными целями. K-way Merge объединяет K отсортированных потоков в один, а Two Heaps разделяет один поток на две упорядоченные половины. Оба паттерна демонстрируют, как heap превращает задачи, требующие полной сортировки, в задачи с partial ordering за O(log n) на элемент.

### [[top-k-elements-pattern]]
Top K Elements и Two Heaps — «братья-близнецы» среди heap-паттернов. Top K ищет K экстремальных элементов с помощью одного heap размера K, а Two Heaps поддерживает медиану с помощью двух heap. Освоив один из паттернов, второй изучается значительно быстрее, так как механика работы с heap идентична. На интервью важно уметь различать, какой паттерн применим к конкретной задаче.

### [[sliding-window-pattern]]
Sliding Window Median — задача на стыке паттернов Two Heaps и Sliding Window. Окно фиксированного размера скользит по массиву, и для каждой позиции нужна медиана элементов в окне. Two Heaps обеспечивает добавление и получение медианы за O(log n), а Sliding Window определяет, какие элементы добавлять и удалять. Эта комбинация паттернов — одна из самых сложных задач на интервью (LeetCode Hard).

---


---

## Проверь себя

> [!question]- Почему для нахождения медианы потока нужны именно Max-Heap и Min-Heap, а не один Heap?
> Медиана = средний элемент. Max-Heap хранит нижнюю половину (вершина = наибольший из нижних), Min-Heap — верхнюю (вершина = наименьший из верхних). Медиана = вершина Max-Heap (нечётное) или среднее вершин. Один Heap даёт только min или max, не середину. Два Heap: O(log n) add, O(1) median.

> [!question]- Как поддерживать баланс между двумя Heaps при добавлении элементов?
> Правило: |size(maxHeap) - size(minHeap)| <= 1. Алгоритм: 1) Добавить в maxHeap. 2) Переместить top maxHeap в minHeap (балансировка). 3) Если minHeap больше — переместить top обратно. Это гарантирует: maxHeap.size >= minHeap.size и все элементы maxHeap <= все элементы minHeap.

> [!question]- Задача Sliding Window Median: почему Two Heaps сложнее, чем для потока?
> Нужно удалять элементы выходящие из окна. Heap не поддерживает эффективное удаление по значению. Решение: lazy deletion — помечаем удалённые, удаляем при extract. Или используем TreeMap/SortedList с O(log n) удалением. Балансировка усложняется: нужно отслеживать 'виртуальный' размер.

## Ключевые карточки

Как Two Heaps находит медиану потока?
?
Max-Heap (нижняя половина), Min-Heap (верхняя). Инвариант: maxHeap.top <= minHeap.top, размеры отличаются не более чем на 1. Медиана: если размеры равны — (maxHeap.top + minHeap.top) / 2. Иначе — top большего heap. O(log n) add, O(1) get median.

Какие задачи решает Two Heaps?
?
1) Find Median from Data Stream (295). 2) Sliding Window Median (480). 3) IPO / Maximize Capital. 4) Next Interval. 5) Любая задача где нужно разделить данные на две 'половины' с быстрым доступом к границе.

Чем Two Heaps лучше сортированного массива для медианы?
?
Sorted array: insert O(n) (сдвиг), median O(1). Two Heaps: insert O(log n), median O(1). Для потока из N элементов: sorted array O(n^2) суммарно, Two Heaps O(n log n). Balanced BST (TreeMap) тоже O(log n), но сложнее в реализации.

Как решить задачу IPO с Two Heaps?
?
Даны проекты: (capital, profit). Начальный капитал W, выбрать K проектов для максимизации. Max-Heap по profit, Min-Heap по capital. Берём из Min-Heap все проекты с capital <= W, кладём в Max-Heap. Извлекаем лучший profit. Повторяем K раз.

Что такое Lazy Deletion в Heap?
?
Помечаем элемент как удалённый (HashMap counts), но не удаляем из heap. При extract: если top помечен — удаляем и берём следующий. Позволяет 'удалять' из heap за O(1), с amortized cost на extract. Критично для Sliding Window Median.

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[patterns/monotonic-stack-pattern]] | Monotonic Stack для Next Greater |
| Углубиться | [[data-structures/heaps-priority-queues]] | Heap реализация подробно |
| Смежная тема | [[patterns/top-k-elements-pattern]] | Top K через Heap |
| Обзор | [[patterns/patterns-overview]] | Вернуться к карте паттернов |


## Источники и дальнейшее чтение

- Cormen, Leiserson, Rivest & Stein (2009). *Introduction to Algorithms (CLRS).* — глава 6 (Heapsort) и глава 9 (Medians and Order Statistics): теоретическая основа для heap operations и алгоритмов поиска медианы; формальный анализ сложности
- Sedgewick & Wayne (2011). *Algorithms.* — реализация MaxPQ и MinPQ на Java; раздел о priority queues с визуализациями, формирующими интуицию для двух-heap структуры
- Skiena (2020). *The Algorithm Design Manual.* — практические применения median maintenance в streaming-системах; раздел о выборе структуры данных под задачу помогает понять, когда Two Heaps оптимален
