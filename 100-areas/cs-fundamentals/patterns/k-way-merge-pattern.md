# K-way Merge Pattern

---
title: "K-way Merge Pattern"
created: 2026-02-08
updated: 2026-02-08
type: deep-dive
status: complete
difficulty: intermediate
confidence: high
cs-foundations:
  - heap-operations
  - merge-sort-concept
  - divide-and-conquer
  - priority-queue
  - external-sorting
  - streaming-algorithms
prerequisites:
  - "[[heaps-priority-queues]]"
  - "[[sorting-algorithms]]"
  - "[[linked-lists]]"
related:
  - "[[heaps-priority-queues]]"
  - "[[top-k-elements-pattern]]"
  - "[[two-heaps-pattern]]"
  - "[[sorting-algorithms]]"
tags:
  - pattern
  - k-way-merge
  - heap
  - priority-queue
  - sorting
  - interview
  - external-sort
---

## TL;DR

K-way Merge — паттерн для объединения K отсортированных последовательностей в одну отсортированную. Использует **Min-Heap** для эффективного поиска минимального элемента среди K списков. **Сложность: O(N log K)** время, O(K) память, где N — общее количество элементов. Ключевые задачи: Merge K Sorted Lists, Kth Smallest in Sorted Matrix, Smallest Range Covering K Lists. Паттерн критичен для **external sorting** (данные не помещаются в память).

---

## Часть 1: Интуиция без кода

> **Цель:** понять ИДЕЮ K-way Merge до любого кода. Если понимаешь эти аналогии — паттерн уже понятен.

### Ты уже знаешь этот паттерн

Этот паттерн встречается в повседневной жизни:

| Ситуация | Как это работает | Паттерн |
|----------|------------------|---------|
| **Очередь из нескольких касс** | Выбираешь кассу с самой короткой очередью | K-way selection |
| **Слияние колод карт** | Берёшь наименьшую карту из вершин нескольких стопок | K-way merge |
| **Турнирная сетка** | На каждом этапе сравниваешь победителей групп | Tournament tree |
| **Сортировка бумаг из разных отделов** | Каждый отдел прислал отсортированные документы | External merge |

### Аналогия 1: Слияние колод карт

Представь 4 отсортированные стопки карт на столе:

```
Стопка A:  [2, 5, 8, 12]     (сверху 2)
Стопка B:  [1, 4, 9]         (сверху 1)
Стопка C:  [3, 7, 10, 15]    (сверху 3)
Стопка D:  [6, 11]           (сверху 6)

Задача: собрать одну отсортированную стопку.

НАИВНЫЙ СПОСОБ:
  Каждый раз смотри ВСЕ верхние карты (4 сравнения)
  Выбери минимальную, положи в результат
  n карт × k стопок = O(n × k) сравнений

УМНЫЙ СПОСОБ (Min-Heap):
  Положи все верхние карты в кучу: {1, 2, 3, 6}
  Вытащи минимум (1) → результат: [1]
  Добавь следующую карту из стопки B (4): {2, 3, 4, 6}
  Вытащи минимум (2) → результат: [1, 2]
  ...

  Каждая операция с кучей = O(log k)
  n карт × O(log k) = O(n log k) сравнений!

ЭКОНОМИЯ:
  Для k=100 стопок и n=10000 карт:
  Наивный: 1,000,000 сравнений
  С кучей: 66,000 сравнений (в 15 раз быстрее!)
```

### Аналогия 2: Турнирная сетка

```
Представь турнир из 8 игроков, разбитых на 4 группы:

Группа A: Иванов лидирует
Группа B: Петров лидирует
Группа C: Сидоров лидирует
Группа D: Козлов лидирует

Кто сильнейший? Нужен турнир между лидерами!

       Финал
      ┌──┴──┐
    Semi1  Semi2
    ┌─┴─┐  ┌─┴─┐
    A   B  C   D

Min-Heap — это как такой турнир:
- Вершина = текущий минимум (победитель)
- Каждое извлечение = O(log k) сравнений
- Это НАМНОГО лучше, чем сравнивать всех со всеми!
```

### Аналогия 3: Внешняя сортировка

```
Проблема: Отсортировать 100 GB данных, имея 1 GB RAM.

Решение:
1. Раздели данные на 100 частей по 1 GB
2. Отсортируй каждую часть в памяти
3. Запиши 100 отсортированных файлов на диск
4. K-way merge: читай по чуть-чуть из каждого файла,
   выбирай минимум, пиши в результат

   ┌──────┐  ┌──────┐  ┌──────┐      ┌──────┐
   │File 1│  │File 2│  │File 3│ ...  │File K│
   └──┬───┘  └──┬───┘  └──┬───┘      └──┬───┘
      ↓         ↓         ↓             ↓
      └─────────┴─────────┴─────────────┘
                      ↓
                  Min-Heap
                      ↓
               ┌──────────┐
               │ Result   │
               └──────────┘

Это ЕДИНСТВЕННЫЙ способ сортировать big data!
```

### Главный инсайт: Почему heap, а не просто сравнение?

```
┌─────────────────────────────────────────────────────────────────┐
│                    КЛЮЧЕВОЕ НАБЛЮДЕНИЕ                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  НАИВНЫЙ ПОДХОД (линейный поиск минимума):                      │
│    Для каждого из N элементов:                                  │
│      Сравни K верхних элементов → найди минимум                 │
│    → N × K сравнений = O(NK)                                    │
│                                                                 │
│  K-WAY MERGE С HEAP:                                            │
│    Создай Min-Heap из K элементов                               │
│    Для каждого из N элементов:                                  │
│      Извлеки минимум из кучи → O(log K)                         │
│      Вставь следующий элемент → O(log K)                        │
│    → N × 2 × log K = O(N log K)                                 │
│                                                                 │
│  СРАВНЕНИЕ (для K=100, N=1000000):                              │
│    Наивный: 100,000,000 операций                                │
│    С heap:  13,000,000 операций (в 7.5 раз быстрее!)            │
│                                                                 │
│  ПОЧЕМУ HEAP РАБОТАЕТ:                                          │
│    - Heap поддерживает порядок "почти автоматически"            │
│    - Минимум ВСЕГДА на вершине                                  │
│    - После извлечения: восстановление за O(log K)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Часть 2: Почему K-way Merge бывает сложен?

> **Цель:** понять типичные трудности и как их избежать.

### Отличие от обычного Merge

**Главная путаница:** K-way Merge — это НЕ просто "merge из merge sort, повторённый K раз":

| Критерий | 2-way Merge | K-way Merge |
|----------|-------------|-------------|
| **Количество списков** | 2 | K (любое) |
| **Поиск минимума** | 1 сравнение | O(log K) с heap |
| **Структура данных** | Два указателя | Min-Heap |
| **Общая сложность** | O(n) | O(N log K) |

### Типичные трудности

#### 1. Как хранить элемент в heap — что кроме значения?

```
ПРОБЛЕМА: Вытащили минимум 3 из heap.
          Из какого списка он пришёл? Какой следующий?

РЕШЕНИЕ: Храни tuple (value, listIndex, elementIndex)

Пример:
  List 0: [1, 5, 9]
  List 1: [2, 4, 8]
  List 2: [3, 6, 7]

  Heap: [(1, 0, 0), (2, 1, 0), (3, 2, 0)]
             ↑         ↑         ↑
           value    listIdx   elemIdx

  Извлекаем (1, 0, 0) → добавляем в результат 1
  Следующий элемент из списка 0: (5, 0, 1)
  Heap: [(2, 1, 0), (3, 2, 0), (5, 0, 1)]
```

#### 2. Что делать, когда список закончился?

```kotlin
// ОШИБКА:
val next = lists[listIndex][elementIndex + 1]  // IndexOutOfBounds!

// ПРАВИЛЬНО:
if (elementIndex + 1 < lists[listIndex].size) {
    heap.add(Triple(
        lists[listIndex][elementIndex + 1],
        listIndex,
        elementIndex + 1
    ))
}
// Иначе просто не добавляем — список исчерпан
```

#### 3. Пустые списки в начале

```kotlin
// ОШИБКА:
lists.forEach { list ->
    heap.add(Triple(list[0], ...))  // Crash если list пустой!
}

// ПРАВИЛЬНО:
lists.forEachIndexed { index, list ->
    if (list.isNotEmpty()) {
        heap.add(Triple(list[0], index, 0))
    }
}
```

#### 4. Linked Lists vs Arrays

```
Для массивов:
  Доступ по индексу: O(1)
  Храним: (value, listIndex, elementIndex)

Для связных списков:
  Доступ по индексу: O(n) — НЕЛЬЗЯ!
  Храним: (value, nodeReference)
  Следующий = node.next

class HeapEntry(val value: Int, val node: ListNode)

// Для linked lists:
heap.add(HeapEntry(node.val, node))
// После извлечения:
if (entry.node.next != null) {
    heap.add(HeapEntry(entry.node.next.val, entry.node.next))
}
```

### Что отличает новичка от эксперта

| Новичок | Эксперт |
|---------|---------|
| Хранит только значение в heap | Хранит (value, listIndex, elementIndex) |
| Забывает про пустые списки | Проверяет isEmpty перед добавлением |
| Использует Array для linked lists | Хранит reference на node |
| Сливает списки попарно O(NK) | Использует heap O(N log K) |
| Не знает про external sorting | Понимает применение в big data |

---

## Часть 3: Ментальные модели для K-way Merge

> **Цель:** дать 3 разных способа ДУМАТЬ о паттерне.

### Модель 1: "Турнирное дерево"

**Идея:** Min-Heap как турнир — на вершине всегда "победитель" (минимум).

```
┌─────────────────────────────────────────────────────────────────┐
│                    ТУРНИРНОЕ ДЕРЕВО                             │
│                                                                 │
│   Списки: [2,5,8]  [1,4,9]  [3,7]  [6,11]                      │
│                                                                 │
│   Min-Heap (турнирное дерево):                                  │
│                                                                 │
│                   1 (победитель)                                │
│                 /   \                                           │
│                2     3                                          │
│               /                                                 │
│              6                                                  │
│                                                                 │
│   Извлекаем 1 → добавляем следующий из того же списка (4)       │
│                                                                 │
│                   2 (новый победитель)                          │
│                 /   \                                           │
│                4     3                                          │
│               /                                                 │
│              6                                                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Когда использовать:** Merge K Sorted Lists/Arrays.

### Модель 2: "Скользящее окно по K спискам"

**Идея:** Heap содержит "фронт" — по одному элементу из каждого активного списка.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ФРОНТ ИЗ K ЭЛЕМЕНТОВ                         │
│                                                                 │
│   List 0: [2, 5, 8, 12]                                        │
│            ↑                                                    │
│   List 1: [1, 4, 9]                                            │
│            ↑                                                    │
│   List 2: [3, 7, 10, 15]                                       │
│            ↑                                                    │
│                                                                 │
│   Фронт (heap): {1, 2, 3}                                      │
│                                                                 │
│   Минимум = 1 → результат [1]                                   │
│   Продвигаем указатель List 1:                                  │
│                                                                 │
│   List 0: [2, 5, 8, 12]                                        │
│            ↑                                                    │
│   List 1: [1, 4, 9]                                            │
│               ↑                                                 │
│   List 2: [3, 7, 10, 15]                                       │
│            ↑                                                    │
│                                                                 │
│   Фронт (heap): {2, 3, 4}                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Когда использовать:** Понимание, почему heap размера K, а не N.

### Модель 3: "Producer-Consumer с приоритетами"

**Идея:** K производителей (списков) и один потребитель (результат). Heap — диспетчер.

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCER-CONSUMER                            │
│                                                                 │
│   Producer 0 ──┐                                               │
│   Producer 1 ──┼──→ [  Min-Heap  ] ──→ Consumer (Result)       │
│   Producer 2 ──┘     (диспетчер)                               │
│                                                                 │
│   Диспетчер (heap):                                            │
│   - Всегда отдаёт наименьший элемент                           │
│   - После отдачи запрашивает следующий у того же producer      │
│   - Если producer исчерпан — не запрашивает                    │
│                                                                 │
│   Гарантия: Consumer получает элементы в отсортированном       │
│             порядке, даже если producers работают асинхронно!  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Когда использовать:** Stream processing, real-time systems.

### Как выбрать подход?

```
                    Какая задача?
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    Merge K         Kth smallest      Smallest
    sorted?         в матрице?        range?
         │               │               │
         ↓               ↓               ↓
    Модель 1:       Модель 2:       Модель 2 +
    "Турнир"        "Фронт"         доп. логика
```

---

## Зачем это нужно?

**Реальная проблема:**

У тебя 1000 отсортированных логов с разных серверов. Нужно объединить их в один отсортированный по времени.

- **Наивный подход:** сливать попарно = O(N × K) = медленно
- **K-way Merge:** O(N log K) = в 100 раз быстрее для K=1000!

**Где используется:**

| Область | Применение | Пример |
|---------|------------|--------|
| **Базы данных** | External merge sort | Сортировка таблиц больше RAM |
| **Big Data** | MapReduce merge phase | Hadoop, Spark |
| **Поисковые системы** | Merge posting lists | Elasticsearch, Lucene |
| **Логирование** | Объединение логов | Splunk, ELK stack |
| **Streaming** | Ordered event processing | Kafka, Flink |
| **Git** | Merge commits | Octopus merge strategy |

**Статистика:**
- Входит в "Grokking the Coding Interview" как Pattern #14
- LeetCode: 20+ задач с этим паттерном
- Критичен для System Design интервью (log aggregation, event sourcing)

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Heap / Priority Queue** | Основная структура паттерна | [[heaps-priority-queues]] |
| **Merge Sort** | Базовое понимание merge | [[sorting-algorithms]] |
| **Linked Lists** | Для Merge K Sorted Lists | [[linked-lists]] |
| **Big O нотация** | Понимание O(N log K) vs O(NK) | [[big-o-complexity]] |

---

## Что это такое?

### Объяснение для 5-летнего

Представь, что у тебя 5 коробок с карточками. В каждой коробке карточки лежат по порядку (от маленьких чисел к большим).

Тебе нужно собрать все карточки в одну большую стопку, тоже по порядку.

Как это сделать быстро?

1. Посмотри на верхнюю карточку в каждой коробке
2. Возьми самую маленькую, положи в результат
3. В той коробке, откуда взял, теперь видна следующая карточка
4. Повтори!

```
Коробки:     [2,5,8]  [1,4]  [3,7]
Верхние:        2       1      3
                        ↑
                    Минимум!

Результат: [1]

Коробки:     [2,5,8]  [4]    [3,7]
Верхние:        2      4       3
                ↑
            Минимум!

Результат: [1, 2]

...и так далее!
```

### Формальное определение

**K-way Merge** — алгоритмический паттерн для объединения K отсортированных последовательностей в одну отсортированную последовательность за время O(N log K), используя приоритетную очередь (Min-Heap) размера K.

**Ключевые свойства:**
- **K входных последовательностей:** массивы, списки, потоки
- **Все последовательности отсортированы:** иначе паттерн не применим
- **Min-Heap размера K:** хранит "фронт" — по элементу от каждого списка
- **Инвариант:** минимальный элемент всегда на вершине heap

**Варианты задач:**

```
1. Merge K Sorted Lists/Arrays
   Вход: K отсортированных списков
   Выход: один отсортированный список

2. Kth Smallest Element
   Вход: K отсортированных списков, число k
   Выход: k-й наименьший элемент среди всех

3. Smallest Range Covering K Lists
   Вход: K отсортированных списков
   Выход: минимальный диапазон [a, b], содержащий элемент из каждого списка

4. Find K Pairs with Smallest Sums
   Вход: два отсортированных массива, число k
   Выход: k пар с наименьшими суммами
```

---

## Терминология

| Термин | Определение | Пример |
|--------|-------------|--------|
| **K-way** | Количество входных последовательностей | K=5 означает 5 списков |
| **Min-Heap** | Куча, где минимум на вершине | Для поиска наименьшего |
| **Front element** | Текущий "головной" элемент списка | Первый необработанный |
| **Exhausted list** | Список, все элементы которого обработаны | Больше не участвует |
| **Heap entry** | Запись в куче (value, listIndex, elemIndex) | Для отслеживания источника |
| **External sort** | Сортировка данных, не помещающихся в RAM | Использует K-way merge |
| **Tournament tree** | Альтернатива heap для K-way merge | Быстрее на практике |

---

## Как это работает?

### Задача 1: Merge K Sorted Arrays

```
Вход: [[1,4,7], [2,5,8], [3,6,9]]
Выход: [1,2,3,4,5,6,7,8,9]

Алгоритм:

1. Инициализация:
   Создай Min-Heap
   Добавь первый элемент каждого списка: {(1,0,0), (2,1,0), (3,2,0)}

2. Основной цикл:
   Пока heap не пуст:
     - Извлеки минимум (value, listIdx, elemIdx)
     - Добавь value в результат
     - Если есть следующий элемент в списке listIdx:
         Добавь его в heap

Пошаговая симуляция:

Шаг 0: Heap = {(1,0,0), (2,1,0), (3,2,0)}
       Result = []

Шаг 1: Extract (1,0,0) → Result = [1]
       Add (4,0,1) → Heap = {(2,1,0), (3,2,0), (4,0,1)}

Шаг 2: Extract (2,1,0) → Result = [1,2]
       Add (5,1,1) → Heap = {(3,2,0), (4,0,1), (5,1,1)}

Шаг 3: Extract (3,2,0) → Result = [1,2,3]
       Add (6,2,1) → Heap = {(4,0,1), (5,1,1), (6,2,1)}

...

Шаг 9: Heap пуст, Result = [1,2,3,4,5,6,7,8,9]
```

### Задача 2: Merge K Sorted Linked Lists

```
Вход: list1: 1→4→5, list2: 1→3→4, list3: 2→6
Выход: 1→1→2→3→4→4→5→6

Алгоритм (отличия от массивов):

1. Храним в heap: (value, nodeReference)
   - НЕ индексы! Для linked list индексы бесполезны

2. Следующий элемент = node.next
   - Не нужен elementIndex

Пошаговая симуляция:

Шаг 0: Heap = {(1,node1), (1,node2), (2,node3)}
       Result = dummy → ?

Шаг 1: Extract (1,node1) → Result = dummy → 1
       node1.next = 4 → Add (4,node1.next)
       Heap = {(1,node2), (2,node3), (4,node1')}

Шаг 2: Extract (1,node2) → Result = dummy → 1 → 1
       node2.next = 3 → Add (3,node2.next)
       Heap = {(2,node3), (3,node2'), (4,node1')}

...
```

### Задача 3: Kth Smallest in Sorted Matrix

```
Вход: matrix = [[1,5,9],[10,11,13],[12,13,15]], k = 8
Выход: 13 (8-й наименьший элемент)

Интерпретация: каждая строка — отсортированный список!

Матрица:
    [1,  5,  9 ]
    [10, 11, 13]
    [12, 13, 15]

Строка 0: [1, 5, 9]
Строка 1: [10, 11, 13]
Строка 2: [12, 13, 15]

Алгоритм: K-way merge, но извлекаем только k элементов

Шаг 0: Heap = {(1,0,0), (10,1,0), (12,2,0)}
Шаг 1: Extract (1,0,0), count=1 → Add (5,0,1)
Шаг 2: Extract (5,0,1), count=2 → Add (9,0,2)
Шаг 3: Extract (9,0,2), count=3 → строка 0 исчерпана
Шаг 4: Extract (10,1,0), count=4 → Add (11,1,1)
Шаг 5: Extract (11,1,1), count=5 → Add (13,1,2)
Шаг 6: Extract (12,2,0), count=6 → Add (13,2,1)
Шаг 7: Extract (13,1,2), count=7 → строка 1 исчерпана
Шаг 8: Extract (13,2,1), count=8 → ОТВЕТ: 13
```

### Задача 4: Smallest Range Covering Elements from K Lists

```
Вход: lists = [[4,10,15,24,26], [0,9,12,20], [5,18,22,30]]
Найти: минимальный диапазон [a,b], содержащий элемент из каждого списка
Выход: [20,24] (содержит 24, 20, 22)

Идея:
1. Heap хранит "фронт" — текущий элемент от каждого списка
2. Отслеживай также МАКСИМУМ среди элементов в heap
3. Диапазон = [heap.min, currentMax]
4. Сужай диапазон, продвигая минимальный элемент

Алгоритм:

Шаг 0: Heap = {(0,1), (4,0), (5,2)}, max = 5
       Range = [0, 5], size = 5

Шаг 1: Extract (0,1), продвигаем список 1
       Add (9,1), max = max(5, 9) = 9
       Heap = {(4,0), (5,2), (9,1)}
       Range = [4, 9], size = 5

Шаг 2: Extract (4,0), продвигаем список 0
       Add (10,0), max = 10
       Heap = {(5,2), (9,1), (10,0)}
       Range = [5, 10], size = 5

... (продолжаем до нахождения минимального range)
```

---

## Сложность операций

| Операция | Время | Память | Примечание |
|----------|-------|--------|------------|
| Инициализация heap | O(K) | O(K) | K элементов изначально |
| Extract min | O(log K) | - | Heapify down |
| Insert | O(log K) | - | Heapify up |
| **Merge K списков** | O(N log K) | O(K) | N = сумма всех элементов |
| Kth smallest | O(K + k log K) | O(K) | Извлекаем k раз |

**Сравнение подходов:**

| Подход | Время | Память | Когда использовать |
|--------|-------|--------|-------------------|
| Попарное слияние | O(NK) | O(N) | K маленькое |
| Divide & Conquer | O(N log K) | O(log K) stack | Рекурсия допустима |
| **K-way Merge (heap)** | O(N log K) | O(K) | Стандартный выбор |
| Tournament tree | O(N log K) | O(K) | Оптимизация |

---

## Реализация

### Kotlin

```kotlin
// ═══════════════════════════════════════════════════════════════════════════
// MERGE K SORTED ARRAYS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Объединяет K отсортированных массивов в один.
 *
 * ИДЕЯ: Min-Heap хранит (value, listIndex, elementIndex).
 *       Извлекаем минимум, добавляем следующий из того же списка.
 *
 * Время: O(N log K), где N = сумма длин всех массивов
 * Память: O(K) для heap
 */
fun mergeKSortedArrays(lists: List<IntArray>): IntArray {
    if (lists.isEmpty()) return intArrayOf()

    // Heap хранит: (value, listIndex, elementIndex)
    val heap = PriorityQueue<Triple<Int, Int, Int>>(
        compareBy { it.first }
    )

    // Инициализация: добавляем первый элемент каждого непустого списка
    lists.forEachIndexed { listIndex, array ->
        if (array.isNotEmpty()) {
            heap.add(Triple(array[0], listIndex, 0))
        }
    }

    val result = mutableListOf<Int>()

    while (heap.isNotEmpty()) {
        val (value, listIndex, elemIndex) = heap.poll()
        result.add(value)

        // Если есть следующий элемент в этом списке — добавляем
        if (elemIndex + 1 < lists[listIndex].size) {
            heap.add(Triple(
                lists[listIndex][elemIndex + 1],
                listIndex,
                elemIndex + 1
            ))
        }
    }

    return result.toIntArray()
}

// ═══════════════════════════════════════════════════════════════════════════
// MERGE K SORTED LINKED LISTS
// ═══════════════════════════════════════════════════════════════════════════

class ListNode(var `val`: Int) {
    var next: ListNode? = null
}

/**
 * Объединяет K отсортированных связных списков.
 *
 * ИДЕЯ: Heap хранит (value, node). Следующий = node.next.
 *
 * Время: O(N log K)
 * Память: O(K)
 */
fun mergeKLists(lists: Array<ListNode?>): ListNode? {
    if (lists.isEmpty()) return null

    // Heap: сравниваем по значению узла
    val heap = PriorityQueue<ListNode>(compareBy { it.`val` })

    // Добавляем головы всех непустых списков
    lists.forEach { head ->
        head?.let { heap.add(it) }
    }

    val dummy = ListNode(0)
    var current = dummy

    while (heap.isNotEmpty()) {
        val node = heap.poll()
        current.next = node
        current = node

        // Добавляем следующий узел из того же списка
        node.next?.let { heap.add(it) }
    }

    return dummy.next
}

// ═══════════════════════════════════════════════════════════════════════════
// KTH SMALLEST IN SORTED MATRIX
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Находит k-й наименьший элемент в матрице, где строки и столбцы отсортированы.
 *
 * ИДЕЯ: Каждая строка — отсортированный список. K-way merge, извлекаем k раз.
 *
 * Время: O(min(K,N) + K log(min(K,N)))
 * Память: O(min(K,N))
 */
fun kthSmallest(matrix: Array<IntArray>, k: Int): Int {
    val n = matrix.size

    // Heap: (value, row, col)
    val heap = PriorityQueue<Triple<Int, Int, Int>>(
        compareBy { it.first }
    )

    // Добавляем первый элемент каждой строки (или первые k строк)
    for (row in 0 until minOf(n, k)) {
        heap.add(Triple(matrix[row][0], row, 0))
    }

    var count = 0
    var result = 0

    while (count < k) {
        val (value, row, col) = heap.poll()
        result = value
        count++

        // Добавляем следующий элемент из той же строки
        if (col + 1 < n) {
            heap.add(Triple(matrix[row][col + 1], row, col + 1))
        }
    }

    return result
}

// ═══════════════════════════════════════════════════════════════════════════
// SMALLEST RANGE COVERING K LISTS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Находит минимальный диапазон, содержащий элемент из каждого списка.
 *
 * ИДЕЯ: Heap + отслеживание максимума. Диапазон = [heap.min, currentMax].
 *       Сужаем, продвигая минимальный элемент.
 *
 * Время: O(N log K)
 * Память: O(K)
 */
fun smallestRange(lists: List<List<Int>>): IntArray {
    // Heap: (value, listIndex, elementIndex)
    val heap = PriorityQueue<Triple<Int, Int, Int>>(
        compareBy { it.first }
    )

    var currentMax = Int.MIN_VALUE

    // Инициализация
    lists.forEachIndexed { listIndex, list ->
        if (list.isNotEmpty()) {
            heap.add(Triple(list[0], listIndex, 0))
            currentMax = maxOf(currentMax, list[0])
        }
    }

    var rangeStart = 0
    var rangeEnd = Int.MAX_VALUE

    while (heap.size == lists.size) {  // Все списки представлены
        val (minValue, listIndex, elemIndex) = heap.poll()

        // Обновляем лучший диапазон
        if (currentMax - minValue < rangeEnd - rangeStart) {
            rangeStart = minValue
            rangeEnd = currentMax
        }

        // Продвигаем минимальный список
        if (elemIndex + 1 < lists[listIndex].size) {
            val nextValue = lists[listIndex][elemIndex + 1]
            heap.add(Triple(nextValue, listIndex, elemIndex + 1))
            currentMax = maxOf(currentMax, nextValue)
        } else {
            // Список исчерпан — выходим (не можем покрыть все списки)
            break
        }
    }

    return intArrayOf(rangeStart, rangeEnd)
}

// ═══════════════════════════════════════════════════════════════════════════
// FIND K PAIRS WITH SMALLEST SUMS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Находит k пар (nums1[i], nums2[j]) с наименьшими суммами.
 *
 * ИДЕЯ: Виртуальная матрица сумм. Каждая "строка" = nums1[i] + все nums2[j].
 *       K-way merge этих виртуальных строк.
 *
 * Время: O(K log K)
 * Память: O(K)
 */
fun kSmallestPairs(nums1: IntArray, nums2: IntArray, k: Int): List<List<Int>> {
    if (nums1.isEmpty() || nums2.isEmpty()) return emptyList()

    // Heap: (sum, i, j)
    val heap = PriorityQueue<Triple<Int, Int, Int>>(
        compareBy { it.first }
    )

    // Начинаем с первого элемента nums1 в паре с каждым из nums2
    // (оптимизация: только первые min(k, nums1.size) элементов)
    for (i in 0 until minOf(k, nums1.size)) {
        heap.add(Triple(nums1[i] + nums2[0], i, 0))
    }

    val result = mutableListOf<List<Int>>()

    while (result.size < k && heap.isNotEmpty()) {
        val (_, i, j) = heap.poll()
        result.add(listOf(nums1[i], nums2[j]))

        // Добавляем следующую пару из той же "строки"
        if (j + 1 < nums2.size) {
            heap.add(Triple(nums1[i] + nums2[j + 1], i, j + 1))
        }
    }

    return result
}
```

### Python

```python
import heapq
from typing import List, Optional

# ═══════════════════════════════════════════════════════════════════════════
# MERGE K SORTED ARRAYS
# ═══════════════════════════════════════════════════════════════════════════

def merge_k_sorted_arrays(lists: List[List[int]]) -> List[int]:
    """
    Объединяет K отсортированных списков.

    Время: O(N log K)
    Память: O(K)
    """
    heap = []  # (value, list_index, element_index)

    # Инициализация
    for list_idx, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], list_idx, 0))

    result = []

    while heap:
        value, list_idx, elem_idx = heapq.heappop(heap)
        result.append(value)

        # Добавляем следующий элемент из того же списка
        if elem_idx + 1 < len(lists[list_idx]):
            heapq.heappush(heap, (
                lists[list_idx][elem_idx + 1],
                list_idx,
                elem_idx + 1
            ))

    return result


# ═══════════════════════════════════════════════════════════════════════════
# MERGE K SORTED LINKED LISTS
# ═══════════════════════════════════════════════════════════════════════════

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

    def __lt__(self, other):
        return self.val < other.val  # Для сравнения в heap


def merge_k_lists(lists: List[Optional[ListNode]]) -> Optional[ListNode]:
    """
    Объединяет K отсортированных связных списков.

    Время: O(N log K)
    Память: O(K)
    """
    heap = []

    # Добавляем головы непустых списков
    for i, head in enumerate(lists):
        if head:
            heapq.heappush(heap, (head.val, i, head))

    dummy = ListNode(0)
    current = dummy

    while heap:
        val, idx, node = heapq.heappop(heap)
        current.next = node
        current = node

        if node.next:
            heapq.heappush(heap, (node.next.val, idx, node.next))

    return dummy.next


# ═══════════════════════════════════════════════════════════════════════════
# KTH SMALLEST IN SORTED MATRIX
# ═══════════════════════════════════════════════════════════════════════════

def kth_smallest(matrix: List[List[int]], k: int) -> int:
    """
    Находит k-й наименьший элемент в отсортированной матрице.

    Время: O(min(K,N) + K log(min(K,N)))
    Память: O(min(K,N))
    """
    n = len(matrix)
    heap = []  # (value, row, col)

    # Добавляем первый элемент каждой строки
    for row in range(min(n, k)):
        heapq.heappush(heap, (matrix[row][0], row, 0))

    result = 0
    for _ in range(k):
        result, row, col = heapq.heappop(heap)

        if col + 1 < n:
            heapq.heappush(heap, (matrix[row][col + 1], row, col + 1))

    return result


# ═══════════════════════════════════════════════════════════════════════════
# SMALLEST RANGE COVERING K LISTS
# ═══════════════════════════════════════════════════════════════════════════

def smallest_range(lists: List[List[int]]) -> List[int]:
    """
    Находит минимальный диапазон, покрывающий элемент из каждого списка.

    Время: O(N log K)
    Память: O(K)
    """
    heap = []  # (value, list_index, element_index)
    current_max = float('-inf')

    # Инициализация
    for list_idx, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], list_idx, 0))
            current_max = max(current_max, lst[0])

    range_start, range_end = 0, float('inf')

    while len(heap) == len(lists):
        min_value, list_idx, elem_idx = heapq.heappop(heap)

        # Обновляем лучший диапазон
        if current_max - min_value < range_end - range_start:
            range_start = min_value
            range_end = current_max

        # Продвигаем минимальный список
        if elem_idx + 1 < len(lists[list_idx]):
            next_value = lists[list_idx][elem_idx + 1]
            heapq.heappush(heap, (next_value, list_idx, elem_idx + 1))
            current_max = max(current_max, next_value)
        else:
            break  # Список исчерпан

    return [range_start, range_end]


# ═══════════════════════════════════════════════════════════════════════════
# FIND K PAIRS WITH SMALLEST SUMS
# ═══════════════════════════════════════════════════════════════════════════

def k_smallest_pairs(nums1: List[int], nums2: List[int], k: int) -> List[List[int]]:
    """
    Находит k пар с наименьшими суммами.

    Время: O(K log K)
    Память: O(K)
    """
    if not nums1 or not nums2:
        return []

    heap = []  # (sum, i, j)

    # Начинаем с первых элементов nums1
    for i in range(min(k, len(nums1))):
        heapq.heappush(heap, (nums1[i] + nums2[0], i, 0))

    result = []

    while len(result) < k and heap:
        _, i, j = heapq.heappop(heap)
        result.append([nums1[i], nums2[j]])

        if j + 1 < len(nums2):
            heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))

    return result
```

---

## Когда применять K-way Merge?

### Сигналы для распознавания

```
Используй K-way Merge, если:

✅ "Объединить K отсортированных..." (списки, массивы, потоки)
✅ "Найти k-й наименьший среди нескольких источников"
✅ "Минимальный диапазон, покрывающий все списки"
✅ "K пар с наименьшими суммами из двух массивов"
✅ "External sort" (данные не помещаются в память)
✅ "Merge phase" в MapReduce

НЕ используй K-way Merge, если:

❌ Данные НЕ отсортированы (сначала отсортируй или используй другой подход)
❌ Только 2 списка (достаточно простого two-pointer merge)
❌ Нужен случайный доступ (heap не поддерживает)
```

### Шаблон решения

```
1. СОЗДАЙ Min-Heap с custom comparator (по значению)

2. ИНИЦИАЛИЗИРУЙ:
   Для каждого списка i:
     Если list[i] не пуст:
       heap.add((list[i][0], i, 0))  // (value, listIndex, elemIndex)

3. ОСНОВНОЙ ЦИКЛ:
   Пока heap не пуст (и не достигли нужного k):
     (value, listIdx, elemIdx) = heap.poll()
     Обработай value (добавь в результат)

     Если elemIdx + 1 < list[listIdx].size:
       heap.add((list[listIdx][elemIdx + 1], listIdx, elemIdx + 1))

4. ВЕРНИ результат
```

---

## Частые ошибки и как их избежать

### Ошибка 1: Хранить только значение в heap

```kotlin
// НЕПРАВИЛЬНО:
heap.add(value)  // Откуда взять следующий элемент?!

// ПРАВИЛЬНО:
heap.add(Triple(value, listIndex, elementIndex))
```

### Ошибка 2: Не проверять пустые списки

```kotlin
// НЕПРАВИЛЬНО:
lists.forEachIndexed { i, list ->
    heap.add(Triple(list[0], i, 0))  // IndexOutOfBounds!
}

// ПРАВИЛЬНО:
lists.forEachIndexed { i, list ->
    if (list.isNotEmpty()) {
        heap.add(Triple(list[0], i, 0))
    }
}
```

### Ошибка 3: Использовать индексы для linked lists

```kotlin
// НЕПРАВИЛЬНО:
// Хранить (value, listIndex, elementIndex) для linked list
// Доступ list[elementIndex] = O(n)!

// ПРАВИЛЬНО:
// Хранить (value, nodeReference)
// Следующий = node.next, O(1)
```

### Ошибка 4: Попарное слияние вместо K-way

```kotlin
// НЕПРАВИЛЬНО (O(NK)):
var result = lists[0]
for (i in 1 until lists.size) {
    result = mergeTwoLists(result, lists[i])
}

// ПРАВИЛЬНО (O(N log K)):
// Использовать heap как показано выше
```

---

## Связанные паттерны

| Паттерн | Связь | Когда использовать вместо K-way |
|---------|-------|--------------------------------|
| [[top-k-elements-pattern]] | Оба используют heap | Когда нужны TOP k, а не merge |
| [[two-heaps-pattern]] | Оба используют heap | Медиана потока |
| [[sorting-algorithms]] | K-way — часть merge sort | Базовая сортировка |
| [[binary-search-pattern]] | Альтернатива для kth smallest | Когда нужен только ответ |

---

## Практические задачи

### Уровень: Средний

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 23 | [Merge k Sorted Lists](https://leetcode.com/problems/merge-k-sorted-lists/) | Базовый K-way merge |
| 378 | [Kth Smallest Element in Sorted Matrix](https://leetcode.com/problems/kth-smallest-element-in-a-sorted-matrix/) | Матрица как K списков |
| 373 | [Find K Pairs with Smallest Sums](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/) | Виртуальная матрица сумм |
| 786 | [K-th Smallest Prime Fraction](https://leetcode.com/problems/k-th-smallest-prime-fraction/) | Виртуальная матрица дробей |

### Уровень: Сложный

| # | Задача | Ключевая идея |
|---|--------|---------------|
| 632 | [Smallest Range Covering Elements from K Lists](https://leetcode.com/problems/smallest-range-covering-elements-from-k-lists/) | Heap + tracking max |
| 719 | [Find K-th Smallest Pair Distance](https://leetcode.com/problems/find-k-th-smallest-pair-distance/) | Binary search + counting |
| 774 | [Minimize Max Distance to Gas Station](https://leetcode.com/problems/minimize-max-distance-to-gas-station/) | Binary search |

---

## Мифы и реальность

### Миф 1: "Попарное слияние так же эффективно"

**Реальность:**
- Попарное: O(NK) — каждый элемент проходит через все K слияний
- K-way с heap: O(N log K) — каждый элемент участвует в log K операциях

Для K=1000 и N=1000000: 1 миллиард vs 20 миллионов операций!

### Миф 2: "Tournament tree лучше heap"

**Реальность:**
- Tournament tree быстрее на практике (меньше cache misses)
- Но heap проще в реализации
- Для интервью heap достаточен

### Миф 3: "K-way merge только для массивов"

**Реальность:**
Паттерн работает для любых отсортированных последовательностей:
- Массивы
- Связные списки
- Файлы на диске (external sort)
- Потоки данных (streaming)

### Миф 4: "Heap размера N нужен для merge"

**Реальность:**
Heap размера **K** достаточен!
- В heap всегда максимум K элементов (по одному от каждого списка)
- Это ключевое преимущество для external sorting

---

## Ключевые выводы

```
┌─────────────────────────────────────────────────────────────────┐
│                      K-WAY MERGE PATTERN                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  КОГДА:                                                         │
│  • K отсортированных списков → один отсортированный             │
│  • Kth smallest среди K источников                              │
│  • External sorting (данные > RAM)                              │
│                                                                 │
│  КАК:                                                           │
│  • Min-Heap размера K                                           │
│  • Храни (value, listIndex, elementIndex)                       │
│  • Извлекай min, добавляй next из того же списка                │
│                                                                 │
│  СЛОЖНОСТЬ:                                                     │
│  • Время: O(N log K)                                            │
│  • Память: O(K)                                                 │
│                                                                 │
│  КЛЮЧЕВАЯ ОПТИМИЗАЦИЯ:                                          │
│  • Heap позволяет найти min за O(log K), а не O(K)              │
│  • Для K=1000: в 150 раз быстрее наивного подхода!              │
│                                                                 │
│  ПРОВЕРКА ПОНИМАНИЯ:                                            │
│  • Почему heap размера K, а не N?                               │
│  • Как изменится код для linked lists vs arrays?                │
│  • Как применить к sorted matrix?                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```
