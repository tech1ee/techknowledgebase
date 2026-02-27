---
title: "CS Fundamentals: Алгоритмы и Структуры Данных"
created: 2025-12-29
modified: 2026-02-13
type: overview
status: published
confidence: high
tags:
  - topic/cs-fundamentals
  - type/overview
  - level/beginner
  - interview
related:
  - "[[coding-challenges]]"
  - "[[technical-interview]]"
  - "[[programming-overview]]"
reading_time: 13
difficulty: 2
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# CS Fundamentals: от нуля до FAANG интервью

87% задач на технических интервью построены на 10-12 базовых паттернах. Случайное решение 500 задач — путь к выгоранию. Системное изучение паттернов — путь к офферу. Этот раздел построен по принципу: **сначала понимание, потом практика**.

---

## Теоретические основы

> **Computer Science Fundamentals** — область информатики, изучающая абстрактные структуры данных, алгоритмы их обработки и методы анализа эффективности вычислений. Фундамент подготовки к техническим интервью и соревновательному программированию.

### Карта раздела

| Область | Ключевые темы | Основоположники |
|---------|---------------|-----------------|
| **Структуры данных** | Массивы, деревья, графы, хеш-таблицы | Кнут (1968), Тарьян (1975) |
| **Алгоритмы** | Сортировка, поиск, графовые, DP | Дейкстра (1959), Кормен и др. (1990) |
| **Паттерны решения** | Two Pointers, Sliding Window, BFS/DFS | Систематизация NeetCode, Blind 75 |
| **Анализ сложности** | Big O, амортизация, Master Theorem | Бахман (1894), Кнут (1976) |
| **Competitive Programming** | CF, ICPC, IOI | Халим (2010), CP-Algorithms |

### Исторический контекст

- **1945** — Джон фон Нейман: алгоритм сортировки слиянием (merge sort)
- **1956** — Крускал: алгоритм минимального остовного дерева
- **1959** — Дейкстра: алгоритм кратчайших путей
- **1962** — Хоар: алгоритм быстрой сортировки (quicksort)
- **1968** — Кнут: "The Art of Computer Programming" — систематизация алгоритмов
- **1990** — Кормен, Лейзерсон, Ривест: CLRS — стандартный учебник

### Связи

- [[big-o-complexity]] — математический аппарат для анализа алгоритмов
- [[problem-solving-framework]] — методология решения задач (UMPIRE)
- [[coding-challenges]] — применение паттернов на практике
- [[programming-overview]] — принципы проектирования и паттерны кода

---

## Как пользоваться этим разделом

> **Важно:** Каждый материал построен по [[_meta/template-deep-dive|шаблону обучения]]:
> ЗАЧЕМ → ЧТО (аналогия) → КАК (визуализация) → КОД
>
> Полный путь обучения: [[_meta/learning-path|Learning Path]]

```
ПУТЬ ОБУЧЕНИЯ:

Уровень 0: Никогда не писал код
└── Выбери язык → Изучи синтаксис → Вернись сюда

Уровень 1: Знаю основы программирования (2-4 недели)
└── [[big-o-complexity]] → [[problem-solving-framework]] → [[data-structures/arrays-strings]]

Уровень 2: Понимаю базовые структуры данных (4-8 недель)
└── data-structures/* → algorithms/* (сортировка, поиск)

Уровень 3: Готовлюсь к интервью (8-12 недель)
└── patterns/* → interview-prep/* → 150 задач на LeetCode

Уровень 4: Competitive Programming (ongoing)
└── competitive/* → advanced algorithms
```

---

## Терминология

| Термин | Что это |
|--------|---------|
| **DSA** | Data Structures & Algorithms — структуры данных и алгоритмы |
| **TC** | Time Complexity — временная сложность |
| **SC** | Space Complexity — пространственная сложность |
| **Big O** | Нотация для описания верхней границы сложности |
| **Pattern** | Типовой подход к решению класса задач |
| **DP** | Dynamic Programming — динамическое программирование |
| **BFS/DFS** | Breadth/Depth-First Search — обход в ширину/глубину |

---

## Структура раздела

### Foundation — Основы (P0)

| Материал | Описание | Приоритет |
|----------|----------|-----------|
| [[big-o-complexity]] | Анализ сложности: Big O, Omega, Theta | P0 |
| [[problem-solving-framework]] | UMPIRE: как подходить к задачам | P0 |
| [[algorithms/recursion-fundamentals]] | Рекурсия, call stack, memoization | P0 |

---

### Data Structures — Структуры Данных

```
ПРИОРИТЕТ ИЗУЧЕНИЯ:

HIGH (интервью спрашивают всегда):
├── [[data-structures/arrays-strings]]      # Массивы и строки
├── [[data-structures/hash-tables]]         # Хэш-таблицы
├── [[data-structures/trees-binary]]        # Бинарные деревья, BST
└── [[data-structures/graphs]]              # Графы

MID (часто на интервью):
├── [[data-structures/linked-lists]]        # Связные списки
├── [[data-structures/stacks-queues]]       # Стеки и очереди
├── [[data-structures/heaps-priority-queues]] # Кучи
└── [[data-structures/tries]]               # Префиксные деревья

ADVANCED (competitive programming):
├── [[data-structures/trees-advanced]]      # AVL, Red-Black, B-Tree
├── [[data-structures/segment-tree]]        # Segment Tree
├── [[data-structures/fenwick-tree]]        # Binary Indexed Tree
├── [[data-structures/sparse-table]]        # RMQ
└── [[data-structures/persistent-structures]] # Персистентные структуры
```

---

### Algorithms — Алгоритмы

```
CORE ALGORITHMS:
├── [[algorithms/sorting-algorithms]]       # Quick, Merge, Heap Sort
├── [[algorithms/searching-algorithms]]     # Binary Search variations
├── [[algorithms/graph-algorithms]]         # BFS, DFS, Dijkstra
├── [[algorithms/dynamic-programming]]      # DP patterns
├── [[algorithms/greedy-algorithms]]        # Greedy approach
└── [[algorithms/backtracking]]             # Permutations, combinations

ADVANCED ALGORITHMS:
├── [[algorithms/graph-advanced]]           # Floyd-Warshall, A*
├── [[algorithms/minimum-spanning-tree]]    # Kruskal, Prim
├── [[algorithms/shortest-paths]]           # All shortest path algorithms
├── [[algorithms/divide-and-conquer]]       # Master theorem
├── [[algorithms/string-algorithms]]        # KMP, Rabin-Karp
├── [[algorithms/string-advanced]]          # Suffix Array, Aho-Corasick
├── [[algorithms/number-theory]]            # GCD, Primes, Modular
├── [[algorithms/combinatorics]]            # C(n,k), inclusion-exclusion
├── [[algorithms/network-flow]]             # Max flow, min cut
├── [[algorithms/dp-optimization]]          # Convex hull trick
└── [[algorithms/computational-geometry]]   # Convex hull, intersections
```

---

### Patterns — Паттерны решения задач

| Pattern | Когда использовать | Сложность |
|---------|-------------------|-----------|
| [[patterns/two-pointers-pattern]] | Sorted array, pairs, palindromes | O(n) |
| [[patterns/sliding-window-pattern]] | Subarray/substring с условием | O(n) |
| [[patterns/binary-search-pattern]] | Sorted data, boundary finding | O(log n) |
| [[patterns/dfs-bfs-patterns]] | Trees, graphs, all paths | O(V+E) |
| [[patterns/intervals-pattern]] | Overlapping intervals, scheduling | O(n log n) |
| [[patterns/monotonic-stack-pattern]] | Next greater element, histograms | O(n) |
| [[patterns/topological-sort-pattern]] | Dependencies, DAG | O(V+E) |
| [[patterns/union-find-pattern]] | Connected components, disjoint sets | O(α(n)) |
| [[patterns/dp-patterns]] | Optimization, counting ways | varies |
| [[patterns/bit-manipulation]] | XOR tricks, bitmasks | O(1)-O(n) |
| [[patterns/meet-in-the-middle]] | Large search space reduction | O(2^(n/2)) |

---

### Competitive Programming

| Материал | Описание |
|----------|----------|
| [[competitive/competitive-programming-overview]] | Codeforces, ICPC, IOI overview |
| [[competitive/contest-strategy]] | Time management, debugging |
| [[competitive/implementation-tips]] | Fast I/O, templates |
| [[competitive/problem-classification]] | CF tags, problem types |

---

### Interview Preparation

| Материал | Описание |
|----------|----------|
| [[interview-prep/leetcode-roadmap]] | NeetCode 150, Blind 75, study plans |
| [[interview-prep/common-mistakes]] | Anti-patterns, debugging |
| [[interview-prep/mock-interview-guide]] | Practice, timing, communication |

---

## Big O Cheat Sheet

```
ВРЕМЕННАЯ СЛОЖНОСТЬ (от лучшей к худшей):

O(1)        Constant      Доступ к элементу массива, HashMap get
O(log n)    Logarithmic   Binary Search
O(n)        Linear        Один проход по массиву
O(n log n)  Linearithmic  Эффективная сортировка (Merge, Quick avg)
O(n²)       Quadratic     Вложенные циклы, Bubble Sort
O(n³)       Cubic         Тройные вложенные циклы
O(2^n)      Exponential   Рекурсия без мемоизации, subsets
O(n!)       Factorial     Все перестановки

ПРИМЕР ДЛЯ n = 1,000,000:
O(1)        = 1 операция
O(log n)    = 20 операций
O(n)        = 1,000,000 операций
O(n log n)  = 20,000,000 операций
O(n²)       = 1,000,000,000,000 операций (💀 не влезет)
```

---

## Roadmap подготовки

### 30 дней (интенсив)

```
Неделя 1: Основы
├── Big O notation
├── Arrays, Strings, HashMaps
└── 15 Easy задач

Неделя 2: Core Patterns
├── Two Pointers, Sliding Window
├── Binary Search
└── 20 Medium задач

Неделя 3: Trees & Graphs
├── BFS, DFS
├── Binary Trees
└── 15 Medium задач

Неделя 4: Advanced + Mock
├── DP basics
├── Backtracking
├── Mock interviews
└── 10 Medium задач

Итого: 60 задач, Blind 75 focus
```

### 3 месяца (оптимально)

```
Месяц 1: Data Structures (60 задач)
├── Недели 1-2: Arrays, Strings, HashMaps
├── Недели 3-4: LinkedList, Stack, Queue
└── Недели 5-6: Trees, Binary Search

Месяц 2: Algorithms (50 задач)
├── Недели 1-2: BFS, DFS, Graphs
├── Недели 3-4: Sorting, Searching
└── Недели 5-6: Greedy, Backtracking

Месяц 3: Advanced + Practice (40 задач)
├── Недели 1-2: Dynamic Programming
├── Неделя 3: Heap, Trie, Advanced
└── Неделя 4: Mock interviews, review

Итого: 150 задач = NeetCode 150
```

---

## Ключевые ресурсы

| Ресурс | Тип | Для чего |
|--------|-----|----------|
| [NeetCode.io](https://neetcode.io/) | Platform | Curated problems + videos |
| [LeetCode](https://leetcode.com/) | Platform | Practice |
| [Tech Interview Handbook](https://www.techinterviewhandbook.org/) | Guide | Patterns, tips |
| [roadmap.sh/datastructures-and-algorithms](https://roadmap.sh/datastructures-and-algorithms) | Roadmap | Learning path |
| [Blind 75](https://neetcode.io/practice?tab=blind75) | List | Essential problems |
| [Codeforces](https://codeforces.com/) | Platform | Competitive programming |

---

## Прогресс изучения

```
SELF-ASSESSMENT CHECKLIST:

FOUNDATION:
□ Понимаю Big O notation
□ Могу объяснить разницу O(n) vs O(n²)
□ Знаю когда использовать какую структуру данных

DATA STRUCTURES:
□ Array — реализация, операции, сложность
□ LinkedList — singly, doubly, operations
□ Stack/Queue — LIFO/FIFO, применения
□ HashTable — collision resolution, load factor
□ Tree — traversals, BST operations
□ Graph — representations, BFS/DFS
□ Heap — heapify, priority queue

ALGORITHMS:
□ Sorting — Quick, Merge, Heap, когда какой
□ Binary Search — все вариации
□ Graph — BFS, DFS, Dijkstra
□ DP — top-down vs bottom-up

PATTERNS:
□ Two Pointers — могу применить
□ Sliding Window — fixed и dynamic
□ Binary Search on Answer
□ Backtracking template
□ DP patterns (Fibonacci, Knapsack, LCS)

INTERVIEW READY:
□ Решил 100+ задач
□ Medium за 25-30 минут
□ Могу объяснить решение вслух
□ Прошёл 3+ mock interviews
```

---

## Связи с другими разделами

```
CS FUNDAMENTALS
│
├── → [[coding-challenges]] — 12 паттернов для интервью (краткий обзор)
├── → [[technical-interview]] — процесс технического интервью
├── → [[system-design-android]] — Mobile System Design
│
└── PROGRAMMING
    ├── → [[solid-principles]] — принципы чистого кода
    ├── → [[design-patterns-overview]] — паттерны проектирования
    └── → [[testing-fundamentals]] — тестирование
```

---

## Источники

### Теоретические основы

- Knuth D.E. (1968–). *The Art of Computer Programming, Vols. 1–4*. — фундаментальный труд по алгоритмам и структурам данных, определивший стандарты анализа сложности
- Cormen T., Leiserson C., Rivest R., Stein C. (2009). *Introduction to Algorithms (CLRS), 3rd ed.* — стандартный учебник по алгоритмам, используемый в MIT и большинстве университетов мира
- Sedgewick R., Wayne K. (2011). *Algorithms, 4th ed.* — практико-ориентированный учебник с реализациями на Java

### Практические руководства

- [roadmap.sh DSA](https://roadmap.sh/datastructures-and-algorithms) — Complete learning path
- [Tech Interview Handbook](https://www.techinterviewhandbook.org/) — Patterns, priorities
- [NeetCode.io](https://neetcode.io/) — Curated 150 problems
- [GeeksforGeeks DSA](https://www.geeksforgeeks.org/dsa/) — Comprehensive reference

---

---

## Проверь себя

> [!question]- Почему системное изучение 10-12 паттернов эффективнее решения 500 случайных задач?
> Паттерны покрывают 87% задач на интервью, формируя структурированное понимание подходов. Случайное решение не строит связей между задачами и приводит к выгоранию без системного роста навыков.

> [!question]- Тебе предстоит интервью через 30 дней. Какой путь обучения из этого раздела ты выберешь и почему?
> Оптимален 30-дневный интенсив: неделя 1 на основы (Big O, Arrays, HashMaps), недели 2-3 на core patterns (Two Pointers, Sliding Window, BFS/DFS), неделя 4 на DP и mock interviews. Этот путь фокусируется на самых частых темах интервью и даёт 60 задач уровня Blind 75.

> [!question]- В чём разница между уровнем 3 (подготовка к интервью) и уровнем 4 (competitive programming)?
> Уровень 3 фокусируется на паттернах и практике 150 задач для прохождения реальных интервью. Уровень 4 включает advanced алгоритмы (Segment Tree, Network Flow), которые выходят за рамки типичного интервью и нужны для соревнований.

> [!question]- Почему раздел структурирован по принципу "сначала понимание, потом практика", а не наоборот?
> Без понимания паттернов практика превращается в бессистемное запоминание решений. Понимание позволяет адаптировать известный подход к незнакомой задаче, что критично на интервью, где задачи часто модифицированы.

---

## Ключевые карточки

DSA расшифровывается как?
?
Data Structures & Algorithms — структуры данных и алгоритмы. Основа технических интервью и эффективного программирования.

Что такое Big O?
?
Нотация для описания верхней границы сложности алгоритма. Показывает, как масштабируется время или память при росте входных данных.

Какие структуры данных имеют HIGH приоритет для интервью?
?
Arrays/Strings, Hash Tables, Binary Trees (BST) и Graphs. Эти структуры спрашивают на интервью практически всегда.

Сколько задач нужно решить для подготовки к интервью за 3 месяца?
?
150 задач (NeetCode 150): 60 задач на Data Structures, 50 на Algorithms, 40 на Advanced + Practice.

Что такое pattern в контексте DSA?
?
Типовой подход к решению целого класса задач. Например, Two Pointers для sorted arrays или Sliding Window для subarray задач.

Какие основные паттерны решения задач существуют?
?
Two Pointers, Sliding Window, Binary Search, DFS/BFS, Intervals, Monotonic Stack, Topological Sort, Union-Find, DP Patterns, Bit Manipulation.

Что означает P0 приоритет в разделе Foundation?
?
Наивысший приоритет изучения. Big O, Problem-Solving Framework и Recursion — фундамент, без которого невозможно изучать остальные темы.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[big-o-complexity]] | Изучить анализ сложности алгоритмов |
| Углубиться | [[problem-solving-framework]] | Освоить UMPIRE фреймворк решения задач |
| Смежная тема | [[coding-challenges]] | Практика 12 паттернов для интервью |
| Обзор | [[cs-fundamentals-overview]] | Вернуться к карте раздела |

*Последнее обновление: 2026-02-13 — Проверено, соответствует педагогическому стандарту*

---

[[_career-moc|← Career MOC]] | [[coding-challenges|Coding Challenges →]]
