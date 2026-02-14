---
title: "Алгоритмические паттерны: карта паттернов решения задач"
created: 2026-01-09
modified: 2026-02-13
type: overview
status: published
confidence: high
tags:
  - topic/cs-fundamentals
  - type/overview
  - level/intermediate
  - pattern
  - interview
related:
  - "[[cs-fundamentals-overview]]"
  - "[[problem-solving-framework]]"
  - "[[big-o-complexity]]"
reading_time: 17
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Algorithmic Patterns: карта паттернов решения задач

> **TL;DR:** Алгоритмические паттерны — это переиспользуемые стратегии решения целых классов задач. Вместо изучения 1000 отдельных задач, изучи 15-20 паттернов и применяй их. Two Pointers, Sliding Window, Binary Search, DFS/BFS, Dynamic Programming — это "vocabulary" для алгоритмического мышления.

---

## Зачем изучать паттерны?

```
БЕЗ ПАТТЕРНОВ:
  1000 задач × уникальное решение = хаос в голове

С ПАТТЕРНАМИ:
  1000 задач = 15-20 паттернов × вариации

  "О, это же Two Pointers!" → знаю как решать
  "Это Sliding Window вариация!" → знаю подход
```

---

## Quick Navigation

| Вопрос | Куда идти |
|--------|-----------|
| Работа с отсортированным массивом? | [[binary-search-pattern]] |
| Два указателя в массиве? | [[two-pointers-pattern]] |
| Цикл в linked list? | [[fast-slow-pointers-pattern]] |
| Подмассив/подстрока фиксированного размера? | [[sliding-window-pattern]] |
| Массив чисел [1,n], missing/duplicate? | [[cyclic-sort-pattern]] |
| Оптимальное решение с выбором? | [[dp-patterns]] |
| Обход графа/дерева? | [[dfs-bfs-patterns]] |
| Комбинации/перестановки? | [[backtracking-pattern]] |
| Поиск k-го элемента? Top K? | [[top-k-elements-pattern]] |
| Median в потоке данных? | [[two-heaps-pattern]] |
| Merge K sorted lists? | [[k-way-merge-pattern]] |
| Pattern matching в строке? | [[string-algorithms-advanced]] |
| Все палиндромные подстроки? | [[string-algorithms-advanced]] |

---

## Learning Path: от новичка до эксперта

```
                    УРОВЕНЬ 1: Основы
                    ┌─────────────────┐
                    │  Two Pointers   │
                    │  Binary Search  │
                    │  Hash Map       │
                    └────────┬────────┘
                             │
                    УРОВЕНЬ 2: Средний
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐     ┌──────▼──────┐    ┌──────▼──────┐
    │  Sliding  │     │    DFS/BFS  │    │   Sorting   │
    │  Window   │     │   Recursion │    │   Patterns  │
    └─────┬─────┘     └──────┬──────┘    └──────┬──────┘
          │                  │                  │
                    УРОВЕНЬ 3: Продвинутый
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐     ┌──────▼──────┐    ┌──────▼──────┐
    │  Dynamic  │     │ Backtracking│    │   Greedy    │
    │Programming│     │             │    │             │
    └─────┬─────┘     └──────┬──────┘    └──────┬──────┘
          │                  │                  │
                    УРОВЕНЬ 4: Эксперт
                    ┌─────────────────┐
                    │  Union-Find     │
                    │  Trie           │
                    │  Segment Tree   │
                    │  Advanced DP    │
                    └─────────────────┘
```

### Рекомендуемый порядок изучения

| # | Паттерн | Сложность | Частота на интервью | Время на изучение |
|---|---------|-----------|---------------------|-------------------|
| 1 | [[two-pointers-pattern]] | Easy | ⭐⭐⭐⭐⭐ | 2-3 дня |
| 2 | [[binary-search-pattern]] | Easy-Medium | ⭐⭐⭐⭐⭐ | 3-4 дня |
| 3 | [[sliding-window-pattern]] | Medium | ⭐⭐⭐⭐⭐ | 3-4 дня |
| 4 | [[hash-map-patterns]] | Easy | ⭐⭐⭐⭐⭐ | 2-3 дня |
| 5 | [[graph-traversal-patterns]] | Medium | ⭐⭐⭐⭐ | 5-7 дней |
| 6 | [[dynamic-programming-patterns]] | Hard | ⭐⭐⭐⭐ | 2-3 недели |
| 7 | [[backtracking-pattern]] | Medium | ⭐⭐⭐ | 4-5 дней |
| 8 | [[heap-pattern]] | Medium | ⭐⭐⭐ | 3-4 дня |
| 9 | [[union-find-pattern]] | Medium-Hard | ⭐⭐ | 3-4 дня |
| 10 | [[trie-pattern]] | Medium | ⭐⭐ | 2-3 дня |

---

## Все паттерны по категориям

### Arrays & Strings

| Паттерн | Когда использовать | Сложность | Статья |
|---------|-------------------|-----------|--------|
| **Two Pointers** | Пары в отсортированном массиве, палиндромы | O(n) | [[two-pointers-pattern]] |
| **Fast & Slow Pointers** | Циклы в списках, middle element, happy number | O(n) | [[fast-slow-pointers-pattern]] |
| **Sliding Window** | Подмассивы, подстроки, максимумы в окне | O(n) | [[sliding-window-pattern]] |
| **Binary Search** | Поиск в отсортированном, границы | O(log n) | [[binary-search-pattern]] |
| **Cyclic Sort** | Массивы с числами [1,n], missing/duplicate | O(n) | [[cyclic-sort-pattern]] |
| **Prefix Sum** | Сумма на отрезке, частотные запросы | O(1) query | [[prefix-sum-pattern]] |
| **Kadane's Algorithm** | Максимальный подмассив | O(n) | [[kadanes-algorithm]] |

### Hash-based

| Паттерн | Когда использовать | Сложность | Статья |
|---------|-------------------|-----------|--------|
| **Hash Map Counting** | Частоты, анаграммы, duplicates | O(n) | [[hash-map-patterns]] |
| **Two Sum Pattern** | Поиск пары с заданной суммой | O(n) | [[two-sum-variations]] |
| **Group By Key** | Группировка элементов | O(n) | [[hash-map-patterns]] |

### Trees & Graphs

| Паттерн | Когда использовать | Сложность | Статья |
|---------|-------------------|-----------|--------|
| **DFS (Depth-First)** | Все пути, существование пути | O(V+E) | [[graph-traversal-patterns]] |
| **BFS (Breadth-First)** | Кратчайший путь, уровни | O(V+E) | [[graph-traversal-patterns]] |
| **Tree Traversal** | Inorder, preorder, postorder | O(n) | [[tree-traversal-patterns]] |
| **Binary Search Tree** | Поиск, вставка, удаление | O(log n) | [[bst-patterns]] |

### Recursion & Backtracking

| Паттерн | Когда использовать | Сложность | Статья |
|---------|-------------------|-----------|--------|
| **Backtracking** | Комбинации, перестановки, Sudoku | Exp | [[backtracking-pattern]] |
| **Divide & Conquer** | Merge sort, quick sort | O(n log n) | [[divide-conquer-pattern]] |
| **Memoization** | Перекрывающиеся подзадачи | Varies | [[dynamic-programming-patterns]] |

### Dynamic Programming

| Паттерн | Когда использовать | Пример | Статья |
|---------|-------------------|--------|--------|
| **0/1 Knapsack** | Выбор с ограничением | Рюкзак, subset sum | [[dp-knapsack]] |
| **Unbounded Knapsack** | Неограниченный выбор | Coin change | [[dp-unbounded]] |
| **LCS/LIS** | Подпоследовательности | Longest common | [[dp-sequences]] |
| **Grid DP** | Пути в матрице | Unique paths | [[dp-grid]] |
| **Interval DP** | Интервалы, скобки | Matrix chain | [[dp-intervals]] |

### Heaps & Priority Queues

| Паттерн | Когда использовать | Сложность | Статья |
|---------|-------------------|-----------|--------|
| **Top K Elements** | K largest/smallest, K frequent | O(n log k) | [[top-k-elements-pattern]] |
| **Two Heaps** | Median в потоке, балансировка | O(log n) | [[two-heaps-pattern]] |
| **K-way Merge** | Merge K sorted lists/arrays | O(N log K) | [[k-way-merge-pattern]] |

### Strings Advanced

| Паттерн | Когда использовать | Сложность | Статья |
|---------|-------------------|-----------|--------|
| **KMP / Z-function** | Pattern matching | O(n+m) | [[string-algorithms-advanced]] |
| **Rabin-Karp** | Rolling hash, multiple patterns | O(n) avg | [[string-algorithms-advanced]] |
| **Aho-Corasick** | Multi-pattern matching | O(n+m+z) | [[string-algorithms-advanced]] |
| **Suffix Array** | All substrings, LCP | O(n log n) | [[string-algorithms-advanced]] |
| **Manacher** | Palindromic substrings | O(n) | [[string-algorithms-advanced]] |

### Advanced

| Паттерн | Когда использовать | Сложность | Статья |
|---------|-------------------|-----------|--------|
| **Union-Find** | Связные компоненты, циклы | O(α(n)) | [[union-find-pattern]] |
| **Trie** | Prefix search, autocomplete | O(m) | [[trie-pattern]] |
| **Segment Tree** | Range queries, updates | O(log n) | [[segment-tree]] |
| **Monotonic Stack** | Next greater element | O(n) | [[monotonic-stack-pattern]] |
| **Topological Sort** | Зависимости, порядок | O(V+E) | [[topological-sort-pattern]] |
| **Meet in the Middle** | Экспоненциальный поиск, разделение | O(2^(n/2)) | [[meet-in-the-middle]] |
| **Intervals** | Merge, insert, intersection | O(n log n) | [[intervals-pattern]] |
| **Bit Manipulation** | XOR tricks, bit masks | O(n) | [[bit-manipulation]] |

---

## Как выбрать паттерн?

```
                        ┌─────────────────────┐
                        │   Что дано?         │
                        └──────────┬──────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
   ┌────▼────┐               ┌─────▼─────┐              ┌─────▼─────┐
   │ Массив  │               │   Граф    │              │  Строка   │
   └────┬────┘               └─────┬─────┘              └─────┬─────┘
        │                          │                          │
   Отсортирован?              Направленный?             Подстрока?
        │                          │                          │
   ┌────┴────┐               ┌─────┴─────┐              ┌─────┴─────┐
   │         │               │           │              │           │
   Да       Нет             Да         Нет         Фиксир.     Любая
   │         │               │           │          размер
   │         │               │           │              │
Binary    Sliding        Topological  Union-Find    Sliding    Two
Search    Window            Sort                    Window   Pointers
Two       Hash Map                                           или DP
Pointers
```

### Признаки паттернов

| Ключевые слова в задаче | Вероятный паттерн |
|------------------------|-------------------|
| "Отсортированный массив", "найти пару" | Two Pointers, Binary Search |
| "Подмассив размера k", "максимум в окне" | Sliding Window |
| "Все комбинации", "все перестановки" | Backtracking |
| "Кратчайший путь", "минимум шагов" | BFS |
| "Существует ли путь", "все пути" | DFS |
| "Оптимальный выбор", "максимальная прибыль" | Dynamic Programming |
| "Top K", "K-й по величине" | Heap |
| "Группы", "связные компоненты" | Union-Find |
| "Prefix", "autocomplete" | Trie |

---

## Интуиция: выбор паттерна

### 1. Two Pointers vs Sliding Window

```
TWO POINTERS:
- Указатели движутся НАВСТРЕЧУ друг другу
- Или один быстрее другого (fast/slow)
- Задачи: пары, палиндромы, сортировка

SLIDING WINDOW:
- Указатели движутся В ОДНУ сторону
- Окно расширяется/сужается
- Задачи: подмассивы, подстроки, максимумы
```

### 2. DFS vs BFS

```
DFS (Depth-First):
- Идём ВГЛУБЬ, потом возвращаемся
- Используй когда: нужны ВСЕ пути, проверка существования
- Stack / Рекурсия

BFS (Breadth-First):
- Идём ПО УРОВНЯМ
- Используй когда: КРАТЧАЙШИЙ путь, расстояние
- Queue
```

### 3. Greedy vs DP

```
GREEDY:
- Локально оптимальный выбор
- Работает когда: жадный выбор ведёт к глобальному оптимуму
- Пример: Activity Selection

DYNAMIC PROGRAMMING:
- Рассматриваем ВСЕ варианты
- Работает когда: перекрывающиеся подзадачи
- Пример: Knapsack, LCS
```

---

## Связи с другими разделами

- [[cs-fundamentals-overview]] — главная карта CS
- [[problem-solving-framework]] — методология решения задач
- [[big-o-complexity]] — анализ сложности
- [[data-structures]] — структуры данных
- [[competitive-programming-overview]] — соревновательное программирование
- [[coding-challenges]] — подготовка к интервью

---

## Ресурсы для практики

| Ресурс | Что даёт | Уровень |
|--------|----------|---------|
| [LeetCode Patterns](https://leetcode.com/explore/) | Задачи по паттернам | All |
| [NeetCode 150](https://neetcode.io/) | Curated список | Medium |
| [Grokking the Coding Interview](https://designgurus.org/course/grokking-the-coding-interview) | Паттерны с объяснениями | Medium |
| [Codeforces](https://codeforces.com/) | Competitive programming | Hard |

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего паттернов | 30+ |
| Категорий | 8 |
| Последнее обновление | 2026-02-08 |


---

## Проверь себя

> [!question]- Почему изучение 15-20 паттернов эффективнее, чем заучивание 1000 отдельных задач?
> Паттерны обобщают стратегии решения целых классов задач. Одним паттерном (например, Two Pointers) можно решить десятки задач. Мозг лучше запоминает структурированные категории, чем отдельные решения. Transfer of learning: понимание паттерна позволяет решать незнакомые задачи.

> [!question]- Как определить, какой паттерн применить к незнакомой задаче?
> Анализ входных данных: отсортированный массив -> Binary Search / Two Pointers. Тип запроса: подмассив/подстрока -> Sliding Window. Зависимости -> Topological Sort. Связные компоненты -> Union-Find / BFS/DFS. Оптимальный выбор -> DP / Greedy. Ограничения N подсказывают допустимую сложность.

> [!question]- Почему некоторые задачи решаются несколькими паттернами, и как выбрать лучший?
> Разные паттерны дают разные trade-offs по времени и памяти. Пример: поиск пары с суммой K решается Two Pointers (O(n log n) + sort) или HashMap (O(n) время, O(n) память). Выбор зависит от ограничений задачи: если массив уже отсортирован, Two Pointers лучше; если нужна минимальная сложность, HashMap.

## Ключевые карточки

Какие 5 самых частых паттернов на интервью?
?
1) Two Pointers / Sliding Window — 20-25% задач. 2) DFS/BFS — 25% задач. 3) Binary Search — 10-15%. 4) Dynamic Programming — 15-20%. 5) Hash Map паттерны — 15%. Эти 5 покрывают 80%+ задач на FAANG интервью.

Как связаны Two Pointers и Sliding Window?
?
Sliding Window — подтип Two Pointers (Same Direction). Оба используют два указателя на массив. Различие: Two Pointers движутся независимо (opposite/same), Sliding Window поддерживает непрерывное окно с инвариантом. Sliding Window = Two Pointers + состояние окна.

Когда использовать DFS vs BFS?
?
DFS: полный обход, cycle detection, path finding, backtracking, topological sort. BFS: shortest path в невзвешенном графе, level-order traversal, multi-source propagation. BFS гарантирует кратчайший путь, DFS — нет.

Что такое Monotonic Stack и когда его применять?
?
Стек с монотонным свойством (элементы всегда возрастают или убывают). Решает 'Next Greater/Smaller Element' за O(n). Применение: гистограммы, температуры, цены акций — любая задача где нужен ближайший больший/меньший.

В чём разница между Greedy и DP подходами?
?
Greedy: локально оптимальный выбор на каждом шаге, надеясь на глобальный оптимум. DP: рассматривает все варианты через подзадачи. Greedy работает при greedy choice property (доказуемо). DP — когда greedy не гарантирует оптимум, но есть optimal substructure.

## Куда дальше

| Тип | Ссылка | Зачем |
|-----|--------|-------|
| Следующий шаг | [[patterns/two-pointers-pattern]] | Начать с Two Pointers |
| Углубиться | [[patterns/dp-patterns]] | DP паттерны для сложных задач |
| Смежная тема | [[problem-solving-framework]] | Фреймворк решения задач |
| Обзор | [[cs-fundamentals-overview]] | Вернуться к карте раздела |


---

*Проверено: 2026-02-08*

---

[[cs-fundamentals-overview|← CS Fundamentals]] | [[two-pointers-pattern|Two Pointers →]]
