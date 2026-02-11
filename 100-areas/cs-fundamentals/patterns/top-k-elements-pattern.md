---
title: "Паттерн Top K элементов"
created: 2026-02-08
modified: 2026-02-08
type: deep-dive
status: published
difficulty: intermediate
confidence: high
cs-foundations:
  - heap-operations
  - quickselect-algorithm
  - partial-sorting
  - frequency-counting
  - selection-algorithms
prerequisites:
  - "[[heaps-priority-queues]]"
  - "[[sorting-algorithms]]"
  - "[[hash-tables]]"
tags:
  - topic/cs-fundamentals
  - type/deep-dive
  - level/intermediate
  - pattern
  - interview
related:
  - "[[heaps-priority-queues]]"
  - "[[two-heaps-pattern]]"
  - "[[k-way-merge-pattern]]"
  - "[[hash-tables]]"
---

# Top K Elements Pattern

## TL;DR

Top K Elements — паттерн для нахождения K наибольших, наименьших или наиболее частых элементов. Три основных подхода: **Сортировка O(n log n)**, **Heap O(n log k)**, **QuickSelect O(n) average**. Ключевой инсайт: для K наибольших используй **Min-Heap размера K** (минимум отсекается первым). Классические задачи: Kth Largest, Top K Frequent, K Closest Points. Один из самых частых паттернов на интервью!

---

## Часть 1: Интуиция без кода

> **Цель:** понять ИДЕЮ Top K Elements до любого кода.

### Ты уже знаешь этот паттерн

Этот паттерн встречается в повседневной жизни:

| Ситуация | Как это работает | Паттерн |
|----------|------------------|---------|
| **Топ-10 песен** | Самые популярные треки | Top K by frequency |
| **Лидерборд в игре** | Топ-100 игроков | Top K by score |
| **Ближайшие рестораны** | K ближайших к тебе | K smallest by distance |
| **Рейтинг фильмов** | Топ-250 IMDb | Top K by rating |

### Аналогия 1: Выбор лучших спортсменов

```
Отбор на Олимпиаду: нужны 3 лучших бегуна из 1000.

СПОСОБ 1 — Отсортировать всех:
  Засечь время всех 1000 бегунов
  Отсортировать по времени
  Взять первых 3
  → O(n log n) = 1000 × 10 = 10,000 операций

СПОСОБ 2 — Держать "тройку лидеров" (Heap):
  Начни с первых 3 бегунов → это текущие лидеры
  Для каждого следующего бегуна:
    Сравни с ХУДШИМ из тройки (Min-Heap!)
    Если новый лучше — заменяй
  → O(n log k) = 1000 × log(3) = 1,600 операций

  Почему Min-Heap? Нас интересует ХУДШИЙ из лидеров,
  чтобы знать, кого можно заменить!

СПОСОБ 3 — QuickSelect:
  Partition массив как в QuickSort
  Но рекурсия ТОЛЬКО в нужную половину
  → O(n) average = 1000 операций
```

### Аналогия 2: Конкурс "Голос"

```
100 участников, нужны топ-5.

     ┌─────────────────────────────────────────────┐
     │              ВСЕ УЧАСТНИКИ                  │
     │   🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤🎤    │
     └─────────────────────────────────────────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │    Min-Heap (size 5)  │
              │   ┌───┐               │
              │   │ 5 │ ← MIN (худший)│
              │   ├───┤               │
              │   │7│8│               │
              │   ├───┤               │
              │   │9│10│              │
              │   └───┘               │
              └───────────────────────┘

Новый участник с баллом 6:
  6 > 5 (min)? ДА!
  Удаляем 5, добавляем 6
  Heap: [6, 7, 8, 9, 10]

Новый участник с баллом 4:
  4 > 6 (min)? НЕТ.
  Не добавляем.

В конце: топ-5 в heap!
```

### Аналогия 3: K ближайших ресторанов

```
Ты в точке (0, 0). 1000 ресторанов на карте.
Найти 3 ближайших.

ХИТРОСТЬ: Используем Max-Heap размера K!

Почему Max-Heap? Мы ищем БЛИЖАЙШИХ (минимальные расстояния).
Храним K кандидатов, и САМЫЙ ДАЛЬНИЙ из них — на вершине.
Если новый ближе — выбрасываем дальний.

     Max-Heap (size 3): [distance]
     ┌───────────────────────────┐
     │       MAX = 15km         │ ← самый дальний кандидат
     │      /        \          │
     │   10km       12km        │
     └───────────────────────────┘

Новый ресторан на расстоянии 8km:
  8 < 15? ДА!
  Удаляем 15, добавляем 8
  Heap: [12, 10, 8]

В конце: 3 ближайших ресторана!
```

### Главный инсайт: Какой heap для чего?

```
┌─────────────────────────────────────────────────────────────────┐
│                    ВЫБОР ТИПА HEAP                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ИЩЕШЬ K НАИБОЛЬШИХ?  →  Min-Heap размера K                     │
│    Почему? Храним K кандидатов.                                 │
│    На вершине — МИНИМУМ (самый слабый кандидат).                │
│    Новый элемент > min? Заменяем min.                           │
│    В конце: все K элементов в heap — это топ K!                 │
│                                                                 │
│  ИЩЕШЬ K НАИМЕНЬШИХ?  →  Max-Heap размера K                     │
│    Почему? Храним K кандидатов.                                 │
│    На вершине — МАКСИМУМ (самый слабый кандидат).               │
│    Новый элемент < max? Заменяем max.                           │
│    В конце: все K элементов в heap — это топ K!                 │
│                                                                 │
│  ПАРАДОКС: Для K наибольших нужен MIN-Heap!                     │
│           Для K наименьших нужен MAX-Heap!                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Часть 2: Почему Top K бывает сложен?

> **Цель:** понять типичные трудности и как их избежать.

### Три основных подхода

| Подход | Время | Память | Когда использовать |
|--------|-------|--------|-------------------|
| **Сортировка** | O(n log n) | O(1) или O(n) | Нужны все элементы отсортированы |
| **Heap** | O(n log k) | O(k) | k << n, streaming |
| **QuickSelect** | O(n) avg, O(n²) worst | O(1) | Только kth элемент |

### Типичные трудности

#### 1. Перепутать Min и Max Heap

```kotlin
// ЗАДАЧА: K наибольших элементов

// НЕПРАВИЛЬНО — Max-Heap:
val maxHeap = PriorityQueue<Int>(reverseOrder())
// Если добавляем все n элементов, heap растёт до O(n)!
// И мы храним БОЛЬШИЕ, а надо отсекать МАЛЫЕ.

// ПРАВИЛЬНО — Min-Heap размера K:
val minHeap = PriorityQueue<Int>()  // Default = min-heap
for (num in nums) {
    minHeap.offer(num)
    if (minHeap.size > k) {
        minHeap.poll()  // Удаляем минимум (он точно не в топ-k)
    }
}
// В heap остались K наибольших!
```

#### 2. Top K Frequent — не забыть подсчёт частот

```kotlin
// ЗАДАЧА: K самых частых элементов

// ШАГ 1: Подсчитай частоты
val freq = mutableMapOf<Int, Int>()
for (num in nums) {
    freq[num] = freq.getOrDefault(num, 0) + 1
}

// ШАГ 2: Min-Heap по частоте, размер K
val heap = PriorityQueue<Int>(compareBy { freq[it] })
for (key in freq.keys) {
    heap.offer(key)
    if (heap.size > k) {
        heap.poll()
    }
}
```

#### 3. QuickSelect — обработка границ

```kotlin
// ОШИБКА: Бесконечная рекурсия при неправильном partition
fun quickSelect(nums: IntArray, left: Int, right: Int, k: Int): Int {
    if (left == right) return nums[left]  // Base case!

    val pivotIndex = partition(nums, left, right)

    return when {
        pivotIndex == k -> nums[k]
        pivotIndex > k -> quickSelect(nums, left, pivotIndex - 1, k)
        else -> quickSelect(nums, pivotIndex + 1, right, k)
    }
}
```

#### 4. K Closest Points — правильный comparator

```kotlin
// ЗАДАЧА: K ближайших точек к origin (0, 0)

// НЕПРАВИЛЬНО — сравнивать точки напрямую
val heap = PriorityQueue<IntArray>()  // Не скомпилируется!

// ПРАВИЛЬНО — сравнивать по расстоянию
val heap = PriorityQueue<IntArray>(
    compareByDescending { it[0] * it[0] + it[1] * it[1] }  // Max-heap по distance²
)

// Почему Max-Heap? Ищем K наименьших расстояний!
// На вершине — САМЫЙ ДАЛЬНИЙ кандидат, его выбрасываем если найдём ближе.
```

### Что отличает новичка от эксперта

| Новичок | Эксперт |
|---------|---------|
| Max-Heap для K наибольших | Min-Heap размера K |
| Сортирует всё для K элементов | Использует heap или QuickSelect |
| Забывает подсчёт частот | Сначала HashMap, потом heap |
| Сравнивает без sqrt для расстояний | Использует distance² (быстрее) |
| Не знает QuickSelect | Знает три подхода и когда какой |

---

## Часть 3: Ментальные модели для Top K

### Модель 1: "Отсечение лишних"

**Идея:** Heap размера K автоматически отсекает элементы, не входящие в топ.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ОТСЕЧЕНИЕ ЛИШНИХ                             │
│                                                                 │
│   Задача: Top 3 наибольших из [5, 3, 8, 1, 9, 2, 7]            │
│                                                                 │
│   Min-Heap (max size = 3):                                     │
│                                                                 │
│   Add 5: [5]                                                   │
│   Add 3: [3, 5]                                                │
│   Add 8: [3, 5, 8]        ← heap полон                         │
│   Add 1: 1 < 3? Не добавляем                                   │
│   Add 9: 9 > 3? Удаляем 3, [5, 8, 9]                          │
│   Add 2: 2 < 5? Не добавляем                                   │
│   Add 7: 7 > 5? Удаляем 5, [7, 8, 9]                          │
│                                                                 │
│   Результат: [7, 8, 9] — топ 3!                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Модель 2: "Partition и выбор"

**Идея:** QuickSelect — partition делит массив, выбираем нужную часть.

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUICKSELECT                                  │
│                                                                 │
│   Задача: 3-й наибольший из [5, 3, 8, 1, 9, 2, 7]              │
│           (индекс n-k = 7-3 = 4 в отсортированном)             │
│                                                                 │
│   Partition 1: pivot = 7                                       │
│   [5, 3, 1, 2] < 7 < [8, 9]                                    │
│              ↓                                                  │
│   [5, 3, 1, 2, 7, 8, 9]                                        │
│               ↑ pivot at index 4                                │
│                                                                 │
│   k = 4, pivot at 4 → НАЙДЕНО! Ответ = 7                       │
│                                                                 │
│   Сложность: O(n) average (без сортировки!)                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Модель 3: "Bucket Sort для частот"

**Идея:** Для Top K Frequent можно использовать bucket sort O(n).

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUCKET SORT FOR FREQUENCY                    │
│                                                                 │
│   Задача: Top 2 frequent из [1, 1, 1, 2, 2, 3]                 │
│                                                                 │
│   Шаг 1: Подсчитай частоты                                     │
│   freq = {1: 3, 2: 2, 3: 1}                                    │
│                                                                 │
│   Шаг 2: Buckets по частоте (index = частота)                  │
│   buckets[1] = [3]      (частота 1)                            │
│   buckets[2] = [2]      (частота 2)                            │
│   buckets[3] = [1]      (частота 3)                            │
│                                                                 │
│   Шаг 3: Собери с конца (от высоких частот)                    │
│   bucket[3] → 1, bucket[2] → 2                                 │
│                                                                 │
│   Результат: [1, 2] — топ 2 по частоте!                        │
│   Сложность: O(n)!                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Зачем это нужно?

**Реальная проблема:**

У тебя 1 миллиард пользователей. Нужно показать топ-100 по активности.

- **Сортировка:** O(n log n) = 30 миллиардов операций
- **Heap размера 100:** O(n log k) = 7 миллиардов операций (в 4 раза быстрее!)

**Где используется:**

| Область | Применение | Пример |
|---------|------------|--------|
| **Рекомендации** | Топ-N похожих | Netflix, Spotify |
| **Поиск** | Топ результатов | Google, Elasticsearch |
| **Игры** | Лидерборды | Steam, Xbox Live |
| **Мониторинг** | Топ ошибок | Sentry, Datadog |
| **Финансы** | Топ акций | Trading platforms |
| **Геолокация** | Ближайшие точки | Google Maps, Uber |

**Статистика:**
- Входит в "Grokking the Coding Interview" как Pattern #13
- Один из TOP-5 самых частых паттернов на интервью
- LeetCode: 30+ задач

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Heap / Priority Queue** | Основная структура | [[heaps-priority-queues]] |
| **Hash Map** | Подсчёт частот | [[hash-tables]] |
| **QuickSort** | Понимание partition | [[sorting-algorithms]] |
| **Big O нотация** | Сравнение подходов | [[big-o-complexity]] |

---

## Что это такое?

### Объяснение для 5-летнего

Представь, что ты выбираешь 3 лучших торта на конкурсе из 100 тортов.

Глупый способ: попробуй все 100, запомни оценки, отсортируй, возьми топ-3.

Умный способ: держи в голове "тройку лидеров". Когда пробуешь новый торт:
- Если он лучше ХУДШЕГО из тройки — заменяй!
- Если хуже — забудь про него.

В конце у тебя топ-3, и ты попробовал каждый торт только 1 раз!

```
Тройка лидеров: [7, 8, 9]
                 ↑ худший

Новый торт: 10 > 7? ДА! Заменяем!
Тройка: [8, 9, 10]

Новый торт: 6 > 8? НЕТ. Пропускаем.
```

### Формальное определение

**Top K Elements** — паттерн для эффективного нахождения K наибольших, наименьших или наиболее частых элементов в коллекции, используя heap, quickselect или bucket sort.

**Ключевые свойства:**
- **Частичная сортировка:** не нужно сортировать всё
- **Heap размера K:** автоматически отсекает лишние
- **QuickSelect:** O(n) average для kth элемента
- **Bucket Sort:** O(n) для Top K Frequent

**Варианты задач:**

```
1. Kth Largest/Smallest Element
   Найти k-й по величине элемент

2. Top K Largest/Smallest
   Найти K наибольших/наименьших элементов

3. Top K Frequent
   Найти K самых частых элементов

4. K Closest Points
   Найти K ближайших точек к origin

5. Sort Characters by Frequency
   Отсортировать символы по частоте

6. Kth Largest in Stream
   Поддерживать k-й наибольший в потоке
```

---

## Терминология

| Термин | Определение | Пример |
|--------|-------------|--------|
| **Top K** | K элементов с наибольшим значением | Топ-10 результатов |
| **Kth Largest** | Элемент на k-й позиции сверху | 3-й наибольший |
| **Min-Heap** | Куча с минимумом на вершине | Для K наибольших |
| **Max-Heap** | Куча с максимумом на вершине | Для K наименьших |
| **QuickSelect** | O(n) алгоритм для kth элемента | Вариация QuickSort |
| **Frequency** | Частота появления элемента | {a: 3, b: 2} |
| **Bucket Sort** | Сортировка по "корзинам" | O(n) для частот |

---

## Как это работает?

### Задача 1: Kth Largest Element

```
Вход: nums = [3, 2, 1, 5, 6, 4], k = 2
Выход: 5 (2-й наибольший)

Подход 1: Min-Heap размера K

  Проходим по массиву, поддерживая heap размера k:

  Add 3: heap = [3]
  Add 2: heap = [2, 3]      (size = k, heap полон)
  Add 1: 1 < 2? Не добавляем
  Add 5: 5 > 2? Удаляем 2, heap = [3, 5]
  Add 6: 6 > 3? Удаляем 3, heap = [5, 6]
  Add 4: 4 < 5? Не добавляем

  Ответ: heap.peek() = 5

Подход 2: QuickSelect

  k-й наибольший = (n-k)-й индекс в отсортированном = индекс 4

  Partition с pivot = 4:
  [3, 2, 1] < 4 < [5, 6]
  [3, 2, 1, 4, 5, 6]
           ↑ pivot at index 3

  3 < 4, рекурсия вправо
  Partition [5, 6], pivot = 6:
  [5] < 6
  pivot at index 5, но нам нужен 4

  Рекурсия влево...
  Ответ: 5
```

### Задача 2: Top K Frequent Elements

```
Вход: nums = [1, 1, 1, 2, 2, 3], k = 2
Выход: [1, 2] (два самых частых)

Шаг 1: Подсчёт частот
  freq = {1: 3, 2: 2, 3: 1}

Шаг 2: Min-Heap по частоте, размер K

  Add (1, freq=3): heap = [(1, 3)]
  Add (2, freq=2): heap = [(2, 2), (1, 3)]  (size = k)
  Add (3, freq=1): 1 < 2? Не добавляем

  Результат: [1, 2]

Альтернатива: Bucket Sort

  buckets по частоте:
  bucket[1] = [3]
  bucket[2] = [2]
  bucket[3] = [1]

  Собираем с конца: [1, 2]
```

### Задача 3: K Closest Points to Origin

```
Вход: points = [[1,3], [-2,2], [5,-1]], k = 2
Выход: [[1,3], [-2,2]] (два ближайших к (0,0))

Расстояния²: [10, 8, 26]

Max-Heap по расстоянию, размер K:

  Add [1,3] (d²=10): heap = [[1,3]]
  Add [-2,2] (d²=8): heap = [[-2,2], [1,3]]
                             max = [1,3] с d²=10
  Add [5,-1] (d²=26): 26 > 10? Не добавляем (дальше чем max)

  Результат: [[-2,2], [1,3]]

ВАЖНО: Max-Heap, потому что ищем K НАИМЕНЬШИХ!
```

### Задача 4: Kth Largest in Stream

```
Вход: k = 3, stream = [4, 5, 8, 2, 3, ...]
После добавления: возвращай 3-й наибольший

  Init: []
  Add 4: [4] → return null (< k элементов)
  Add 5: [4, 5] → return null
  Add 8: [4, 5, 8] → return 4 (3-й наибольший)
  Add 2: [4, 5, 8] (2 < 4, не добавляем) → return 4
  Add 3: [4, 5, 8] (3 < 4, не добавляем) → return 4
  Add 10: [5, 8, 10] (10 > 4, добавляем, удаляем 4) → return 5

Структура: Min-Heap размера K
  peek() всегда = K-й наибольший!
```

---

## Сложность операций

| Подход | Время | Память | Когда использовать |
|--------|-------|--------|-------------------|
| Сортировка | O(n log n) | O(1) | Нужен весь отсортированный массив |
| Min-Heap (size K) | O(n log k) | O(k) | k << n, streaming |
| QuickSelect | O(n) avg | O(1) | Только kth элемент, можно изменять массив |
| Bucket Sort | O(n) | O(n) | Top K Frequent |

**Сравнение для n = 1,000,000, k = 100:**

| Подход | Операций | Победитель |
|--------|----------|------------|
| Сортировка | 20,000,000 | |
| Heap | 700,000 | ✓ Для streaming |
| QuickSelect | 1,000,000 | ✓ Для одного запроса |

---

## Реализация

### Kotlin

```kotlin
import java.util.PriorityQueue

// ═══════════════════════════════════════════════════════════════════════════
// KTH LARGEST ELEMENT (LeetCode 215)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Подход 1: Min-Heap размера K
 * Время: O(n log k), Память: O(k)
 */
fun findKthLargestHeap(nums: IntArray, k: Int): Int {
    val minHeap = PriorityQueue<Int>()

    for (num in nums) {
        minHeap.offer(num)
        if (minHeap.size > k) {
            minHeap.poll()  // Удаляем минимум
        }
    }

    return minHeap.peek()  // k-й наибольший = минимум в heap
}

/**
 * Подход 2: QuickSelect
 * Время: O(n) average, O(n²) worst, Память: O(1)
 */
fun findKthLargestQuickSelect(nums: IntArray, k: Int): Int {
    val targetIndex = nums.size - k  // k-й наибольший = (n-k)-й индекс

    fun partition(left: Int, right: Int): Int {
        val pivot = nums[right]
        var i = left

        for (j in left until right) {
            if (nums[j] <= pivot) {
                nums.swap(i, j)
                i++
            }
        }
        nums.swap(i, right)
        return i
    }

    var left = 0
    var right = nums.lastIndex

    while (left <= right) {
        val pivotIndex = partition(left, right)

        when {
            pivotIndex == targetIndex -> return nums[pivotIndex]
            pivotIndex < targetIndex -> left = pivotIndex + 1
            else -> right = pivotIndex - 1
        }
    }

    return -1  // Не должно случиться
}

private fun IntArray.swap(i: Int, j: Int) {
    val temp = this[i]
    this[i] = this[j]
    this[j] = temp
}

// ═══════════════════════════════════════════════════════════════════════════
// TOP K FREQUENT ELEMENTS (LeetCode 347)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Подход 1: Heap
 * Время: O(n log k), Память: O(n)
 */
fun topKFrequentHeap(nums: IntArray, k: Int): IntArray {
    // Шаг 1: Подсчёт частот
    val freq = mutableMapOf<Int, Int>()
    for (num in nums) {
        freq[num] = freq.getOrDefault(num, 0) + 1
    }

    // Шаг 2: Min-Heap по частоте
    val heap = PriorityQueue<Int>(compareBy { freq[it] })

    for (key in freq.keys) {
        heap.offer(key)
        if (heap.size > k) {
            heap.poll()
        }
    }

    return heap.toIntArray()
}

/**
 * Подход 2: Bucket Sort
 * Время: O(n), Память: O(n)
 */
fun topKFrequentBucket(nums: IntArray, k: Int): IntArray {
    // Шаг 1: Подсчёт частот
    val freq = mutableMapOf<Int, Int>()
    for (num in nums) {
        freq[num] = freq.getOrDefault(num, 0) + 1
    }

    // Шаг 2: Bucket по частоте (index = частота)
    val buckets = Array(nums.size + 1) { mutableListOf<Int>() }
    for ((num, count) in freq) {
        buckets[count].add(num)
    }

    // Шаг 3: Собираем с конца
    val result = mutableListOf<Int>()
    for (i in buckets.lastIndex downTo 0) {
        for (num in buckets[i]) {
            result.add(num)
            if (result.size == k) return result.toIntArray()
        }
    }

    return result.toIntArray()
}

// ═══════════════════════════════════════════════════════════════════════════
// K CLOSEST POINTS TO ORIGIN (LeetCode 973)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Max-Heap по расстоянию, размер K
 * Время: O(n log k), Память: O(k)
 */
fun kClosest(points: Array<IntArray>, k: Int): Array<IntArray> {
    // Max-Heap: на вершине САМЫЙ ДАЛЬНИЙ кандидат
    val maxHeap = PriorityQueue<IntArray>(
        compareByDescending { it[0] * it[0] + it[1] * it[1] }
    )

    for (point in points) {
        maxHeap.offer(point)
        if (maxHeap.size > k) {
            maxHeap.poll()  // Удаляем самый дальний
        }
    }

    return maxHeap.toTypedArray()
}

// ═══════════════════════════════════════════════════════════════════════════
// KTH LARGEST IN STREAM (LeetCode 703)
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Min-Heap размера K для streaming
 */
class KthLargest(private val k: Int, nums: IntArray) {
    private val minHeap = PriorityQueue<Int>()

    init {
        for (num in nums) {
            add(num)
        }
    }

    fun add(`val`: Int): Int {
        minHeap.offer(`val`)
        if (minHeap.size > k) {
            minHeap.poll()
        }
        return minHeap.peek()
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// SORT CHARACTERS BY FREQUENCY (LeetCode 451)
// ═══════════════════════════════════════════════════════════════════════════

fun frequencySort(s: String): String {
    // Подсчёт частот
    val freq = mutableMapOf<Char, Int>()
    for (c in s) {
        freq[c] = freq.getOrDefault(c, 0) + 1
    }

    // Max-Heap по частоте
    val maxHeap = PriorityQueue<Char>(compareByDescending { freq[it] })
    maxHeap.addAll(freq.keys)

    // Построение результата
    val result = StringBuilder()
    while (maxHeap.isNotEmpty()) {
        val c = maxHeap.poll()
        repeat(freq[c]!!) { result.append(c) }
    }

    return result.toString()
}

// ═══════════════════════════════════════════════════════════════════════════
// REORGANIZE STRING (LeetCode 767)
// ═══════════════════════════════════════════════════════════════════════════

fun reorganizeString(s: String): String {
    val freq = mutableMapOf<Char, Int>()
    for (c in s) {
        freq[c] = freq.getOrDefault(c, 0) + 1
    }

    // Max-Heap по частоте
    val maxHeap = PriorityQueue<Char>(compareByDescending { freq[it] })
    maxHeap.addAll(freq.keys)

    val result = StringBuilder()
    var prev: Char? = null

    while (maxHeap.isNotEmpty()) {
        val current = maxHeap.poll()
        result.append(current)
        freq[current] = freq[current]!! - 1

        // Возвращаем предыдущий символ, если ещё есть
        if (prev != null && freq[prev]!! > 0) {
            maxHeap.offer(prev)
        }

        prev = current
    }

    return if (result.length == s.length) result.toString() else ""
}
```

### Python

```python
import heapq
from collections import Counter
from typing import List

# ═══════════════════════════════════════════════════════════════════════════
# KTH LARGEST ELEMENT (LeetCode 215)
# ═══════════════════════════════════════════════════════════════════════════

def findKthLargest_heap(nums: List[int], k: int) -> int:
    """
    Min-Heap размера K.
    Время: O(n log k), Память: O(k)
    """
    heap = []

    for num in nums:
        heapq.heappush(heap, num)
        if len(heap) > k:
            heapq.heappop(heap)

    return heap[0]


def findKthLargest_quickselect(nums: List[int], k: int) -> int:
    """
    QuickSelect.
    Время: O(n) average, Память: O(1)
    """
    target = len(nums) - k

    def partition(left: int, right: int) -> int:
        pivot = nums[right]
        i = left

        for j in range(left, right):
            if nums[j] <= pivot:
                nums[i], nums[j] = nums[j], nums[i]
                i += 1

        nums[i], nums[right] = nums[right], nums[i]
        return i

    left, right = 0, len(nums) - 1

    while left <= right:
        pivot_idx = partition(left, right)

        if pivot_idx == target:
            return nums[pivot_idx]
        elif pivot_idx < target:
            left = pivot_idx + 1
        else:
            right = pivot_idx - 1

    return -1


# ═══════════════════════════════════════════════════════════════════════════
# TOP K FREQUENT ELEMENTS (LeetCode 347)
# ═══════════════════════════════════════════════════════════════════════════

def topKFrequent_heap(nums: List[int], k: int) -> List[int]:
    """
    Heap подход.
    Время: O(n log k)
    """
    freq = Counter(nums)
    heap = []

    for num, count in freq.items():
        heapq.heappush(heap, (count, num))
        if len(heap) > k:
            heapq.heappop(heap)

    return [num for count, num in heap]


def topKFrequent_bucket(nums: List[int], k: int) -> List[int]:
    """
    Bucket Sort.
    Время: O(n)
    """
    freq = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]

    for num, count in freq.items():
        buckets[count].append(num)

    result = []
    for i in range(len(buckets) - 1, -1, -1):
        for num in buckets[i]:
            result.append(num)
            if len(result) == k:
                return result

    return result


# ═══════════════════════════════════════════════════════════════════════════
# K CLOSEST POINTS TO ORIGIN (LeetCode 973)
# ═══════════════════════════════════════════════════════════════════════════

def kClosest(points: List[List[int]], k: int) -> List[List[int]]:
    """
    Max-Heap (через отрицательные расстояния).
    Время: O(n log k)
    """
    heap = []

    for x, y in points:
        dist = -(x * x + y * y)  # Отрицательное для max-heap
        heapq.heappush(heap, (dist, [x, y]))
        if len(heap) > k:
            heapq.heappop(heap)

    return [point for dist, point in heap]


# ═══════════════════════════════════════════════════════════════════════════
# KTH LARGEST IN STREAM (LeetCode 703)
# ═══════════════════════════════════════════════════════════════════════════

class KthLargest:
    """Min-Heap размера K для streaming."""

    def __init__(self, k: int, nums: List[int]):
        self.k = k
        self.heap = []

        for num in nums:
            self.add(num)

    def add(self, val: int) -> int:
        heapq.heappush(self.heap, val)
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)
        return self.heap[0]


# ═══════════════════════════════════════════════════════════════════════════
# SORT CHARACTERS BY FREQUENCY (LeetCode 451)
# ═══════════════════════════════════════════════════════════════════════════

def frequencySort(s: str) -> str:
    """Сортировка символов по частоте."""
    freq = Counter(s)

    # Max-Heap (отрицательные частоты)
    heap = [(-count, char) for char, count in freq.items()]
    heapq.heapify(heap)

    result = []
    while heap:
        count, char = heapq.heappop(heap)
        result.append(char * (-count))

    return ''.join(result)
```

---

## Когда применять Top K?

### Сигналы для распознавания

```
Используй Top K Elements, если:

✅ "Найти K наибольших/наименьших"
✅ "K-й наибольший/наименьший элемент"
✅ "K самых частых"
✅ "K ближайших точек"
✅ "Сортировка по частоте"
✅ "Лидерборд / рейтинг"
✅ "Streaming данные, нужен top K"

НЕ используй Top K, если:

❌ Нужна медиана → Two Heaps
❌ Merge K sorted lists → K-way Merge
❌ Нужен весь отсортированный массив → просто сортируй
```

### Выбор подхода

```
                    Какая задача?
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    k << n?         k ≈ n?          Streaming?
         │               │               │
         ↓               ↓               ↓
    Heap или         Сортируй        Heap
    QuickSelect                     размера K

                    Нужен только
                    kth элемент?
                         │
                  ┌──────┴──────┐
                  │             │
              Можно           Нельзя
              изменять        изменять
              массив?         массив?
                  │             │
                  ↓             ↓
             QuickSelect      Heap
```

---

## Частые ошибки и как их избежать

### Ошибка 1: Max-Heap для K наибольших

```kotlin
// НЕПРАВИЛЬНО:
val maxHeap = PriorityQueue<Int>(reverseOrder())
// Heap растёт до O(n)!

// ПРАВИЛЬНО:
val minHeap = PriorityQueue<Int>()  // size = K
```

### Ошибка 2: Забыть ограничить размер heap

```kotlin
// НЕПРАВИЛЬНО:
for (num in nums) {
    heap.offer(num)
    // Heap растёт до n элементов!
}

// ПРАВИЛЬНО:
for (num in nums) {
    heap.offer(num)
    if (heap.size > k) heap.poll()
}
```

### Ошибка 3: sqrt для расстояний

```kotlin
// НЕПРАВИЛЬНО (медленно):
val dist = sqrt((x*x + y*y).toDouble())

// ПРАВИЛЬНО (быстрее, достаточно для сравнения):
val distSquared = x*x + y*y
```

---

## Связанные паттерны

| Паттерн | Связь | Когда использовать вместо Top K |
|---------|-------|--------------------------------|
| [[two-heaps-pattern]] | Оба используют heap | Медиана |
| [[k-way-merge-pattern]] | Оба для K списков | Merge K sorted |
| [[sorting-algorithms]] | Альтернатива | Нужен весь массив |
| [[hash-tables]] | Для подсчёта частот | Часть решения |

---

## Практические задачи

### Уровень: Лёгкий

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 703 | [Kth Largest Element in Stream](https://leetcode.com/problems/kth-largest-element-in-a-stream/) | Min-Heap для streaming |

### Уровень: Средний

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 215 | [Kth Largest Element](https://leetcode.com/problems/kth-largest-element-in-an-array/) | Heap или QuickSelect |
| 347 | [Top K Frequent Elements](https://leetcode.com/problems/top-k-frequent-elements/) | Freq Map + Heap |
| 973 | [K Closest Points](https://leetcode.com/problems/k-closest-points-to-origin/) | Max-Heap |
| 451 | [Sort Characters by Frequency](https://leetcode.com/problems/sort-characters-by-frequency/) | Freq + Max-Heap |
| 692 | [Top K Frequent Words](https://leetcode.com/problems/top-k-frequent-words/) | Custom comparator |
| 767 | [Reorganize String](https://leetcode.com/problems/reorganize-string/) | Greedy + Heap |

### Уровень: Сложный

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 658 | [Find K Closest Elements](https://leetcode.com/problems/find-k-closest-elements/) | Binary Search |
| 895 | [Maximum Frequency Stack](https://leetcode.com/problems/maximum-frequency-stack/) | Freq Map + Stack |

---

## Мифы и реальность

### Миф 1: "Всегда используй Max-Heap для K наибольших"

**Реальность:** Max-Heap вырастет до O(n). Используй Min-Heap размера K!

### Миф 2: "QuickSelect всегда лучше Heap"

**Реальность:**
- QuickSelect: O(n) average, но O(n²) worst case
- Heap: гарантированный O(n log k)
- Для streaming: только Heap

### Миф 3: "Bucket Sort работает только для частот"

**Реальность:** Bucket Sort работает для любых значений в известном диапазоне, но особенно эффективен для частот, так как диапазон ограничен n.

---

## Ключевые выводы

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOP K ELEMENTS PATTERN                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  КОГДА:                                                         │
│  • K наибольших/наименьших                                      │
│  • K самых частых                                               │
│  • K ближайших                                                  │
│  • Streaming top K                                              │
│                                                                 │
│  КАК:                                                           │
│  • K наибольших → Min-Heap размера K                            │
│  • K наименьших → Max-Heap размера K                            │
│  • Только kth → QuickSelect O(n)                                │
│  • K frequent → HashMap + Heap или Bucket Sort                  │
│                                                                 │
│  СЛОЖНОСТЬ:                                                     │
│  • Heap: O(n log k) time, O(k) space                            │
│  • QuickSelect: O(n) avg time, O(1) space                       │
│  • Bucket Sort: O(n) time, O(n) space                           │
│                                                                 │
│  КЛЮЧЕВОЙ ПАРАДОКС:                                             │
│  • Для K НАИБОЛЬШИХ → MIN-Heap!                                 │
│  • Для K НАИМЕНЬШИХ → MAX-Heap!                                 │
│                                                                 │
│  ПРОВЕРКА ПОНИМАНИЯ:                                            │
│  • Почему Min-Heap для K наибольших?                            │
│  • Когда использовать QuickSelect vs Heap?                      │
│  • Как применить Bucket Sort для Top K Frequent?                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Связь с другими темами

### [[heaps-priority-queues]]
Heap — основной инструмент паттерна Top K Elements. Min-Heap размера K позволяет находить K наибольших элементов за O(n log k), поддерживая инвариант: вершина heap — минимальный среди K кандидатов. Без понимания операций heap (insert, extractMin, peek) и свойства partial ordering невозможно реализовать паттерн эффективно. Heaps & Priority Queues объясняют, почему для K наибольших используется именно Min-Heap (а не Max-Heap) — это один из самых контринтуитивных моментов паттерна.

### [[two-heaps-pattern]]
Two Heaps — родственный паттерн, который использует пару heap для разделения данных на две половины. Если Top K находит K экстремальных элементов, то Two Heaps поддерживает медиану, разделяя все элементы на «меньшую» и «большую» половины. Оба паттерна показывают, как heap позволяет эффективно работать с потоковыми данными, не храня все элементы отсортированными.

### [[k-way-merge-pattern]]
K-way Merge и Top K Elements — два паттерна, построенных на heap размера K, но решающих разные классы задач. Top K работает с одним неупорядоченным набором, а K-way Merge — с K упорядоченными потоками. Объединяет их общая механика: heap хранит K элементов и за O(log K) поддерживает порядок. Понимание обоих паттернов формирует общую картину применения heap в алгоритмических задачах.

### [[hash-tables]]
Hash-таблицы часто используются совместно с Top K Elements для подсчёта частот. Классическая задача Top K Frequent Elements решается в два шага: HashMap для подсчёта частот за O(n), затем Min-Heap размера K для нахождения K наиболее частых за O(n log k). Без знания hash-таблиц невозможно эффективно преобразовать исходные данные в формат, пригодный для heap-обработки.

---

## Источники и дальнейшее чтение

- Cormen, Leiserson, Rivest & Stein (2009). *Introduction to Algorithms (CLRS).* — глава 9 (Medians and Order Statistics): формальный анализ selection algorithms, включая QuickSelect с доказательством ожидаемого O(n); теоретическая основа для выбора K-го элемента
- Blum, Floyd, Pratt, Rivest & Tarjan (1973). *Time bounds for selection.* — оригинальная статья, доказывающая существование детерминированного O(n) алгоритма выбора (Median of Medians); фундаментальный результат теории алгоритмов
- Skiena (2020). *The Algorithm Design Manual.* — практические рекомендации по выбору между сортировкой, heap и QuickSelect для задач Top K; раздел «War Stories» с реальными примерами применения
