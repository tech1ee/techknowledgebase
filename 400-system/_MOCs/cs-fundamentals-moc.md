---
title: "CS Fundamentals MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/cs-fundamentals
  - type/moc
  - navigation
---
# CS Fundamentals MOC

> Алгоритмы, структуры данных и паттерны решения задач — от нуля до FAANG интервью и competitive programming.

---

## Рекомендуемый путь изучения

1. **Основы** — [[big-o-complexity]] → [[problem-solving-framework]] → [[code-explained-from-zero]]
2. **Структуры данных** — [[arrays-strings]] → [[linked-lists]] → [[stacks-queues]] → [[hash-tables]] → [[trees-binary]] → [[heaps-priority-queues]] → [[graphs]]
3. **Базовые алгоритмы** — [[recursion-fundamentals]] → [[sorting-algorithms]] → [[searching-algorithms]] → [[divide-and-conquer]] → [[greedy-algorithms]]
4. **Продвинутые алгоритмы** — [[dynamic-programming]] → [[backtracking]] → [[graph-algorithms]] → [[string-algorithms]]
5. **Паттерны** — [[patterns-overview]] → [[two-pointers-pattern]] → [[sliding-window-pattern]] → [[binary-search-pattern]] → [[dfs-bfs-patterns]] → [[dp-patterns]]
6. **Интервью** — [[leetcode-roadmap]] → [[common-mistakes]] → [[mock-interview-guide]]
7. **Competitive** — [[competitive-programming-overview]] → [[problem-classification]] → [[contest-strategy]] → [[implementation-tips]]

## Статьи по категориям

### Основы и навигация
- [[cs-fundamentals-overview]] — обзор раздела и навигация по уровням (от нуля до competitive)
- [[big-o-complexity]] — полное руководство по анализу сложности алгоритмов
- [[problem-solving-framework]] — UMPIRE метод и метод Полья для решения алгоритмических задач
- [[code-explained-from-zero]] — код с объяснением каждой строки для начинающих (Kotlin)
- [[code-explained-advanced]] — продвинутые алгоритмы с пошаговым разбором (string hashing, DP)

### Data Structures
- [[arrays-strings]] — фундамент: непрерывная память, cache locality, random access
- [[linked-lists]] — узлы и указатели, singly/doubly/circular, fast-slow pointers
- [[stacks-queues]] — LIFO и FIFO, deque, monotonic stack
- [[hash-tables]] — хеш-функции, коллизии, O(1) lookup
- [[trees-binary]] — бинарные деревья и BST, обходы (DFS/BFS), балансировка
- [[trees-advanced]] — AVL и Red-Black деревья, self-balancing с гарантией O(log n)
- [[heaps-priority-queues]] — min/max heap, sift up/down, top-k pattern
- [[graphs]] — представления графов, обходы, компоненты связности
- [[tries]] — префиксное дерево для работы со строками и автодополнением
- [[segment-tree]] — range queries и updates за O(log n), lazy propagation
- [[fenwick-tree]] — Binary Indexed Tree для prefix sum за O(log n), компактнее segment tree
- [[sparse-table]] — статические Range Minimum Query за O(1), preprocessing O(n log n)
- [[persistent-structures]] — версионные структуры данных с path copying и structural sharing

### Algorithms
- [[recursion-fundamentals]] — рекурсия от нуля: call stack, base case, tail call optimization
- [[sorting-algorithms]] — все виды сортировок: comparison-based и linear-time
- [[searching-algorithms]] — binary search, lower/upper bound, search on answer
- [[divide-and-conquer]] — разбиение задачи на подзадачи, Master Theorem
- [[dynamic-programming]] — overlapping subproblems, memoization, tabulation
- [[dp-optimization]] — Convex Hull Trick, D&C optimization, SOS DP, Matrix Exponentiation
- [[greedy-algorithms]] — локально оптимальные решения, greedy choice property
- [[backtracking]] — полный перебор с отсечением, constraint satisfaction
- [[graph-algorithms]] — BFS, DFS, Dijkstra и базовые графовые алгоритмы
- [[graph-advanced]] — Floyd-Warshall, Bellman-Ford, A*, bidirectional search
- [[shortest-paths]] — Dijkstra, Bellman-Ford, Floyd-Warshall, 0-1 BFS
- [[minimum-spanning-tree]] — Kruskal, Prim, Boruvka, Cut Property и Cycle Property
- [[network-flow]] — Ford-Fulkerson, Edmonds-Karp, Dinic, Max-Flow = Min-Cut
- [[string-algorithms]] — KMP, Rabin-Karp, Z-function для pattern matching
- [[string-advanced]] — Suffix Array, Aho-Corasick, Manacher, Suffix Automaton
- [[combinatorics]] — nCr, Lucas theorem, Catalan numbers, Inclusion-Exclusion
- [[number-theory]] — GCD, modular exponentiation, Sieve, Chinese Remainder Theorem
- [[computational-geometry]] — выпуклая оболочка, пересечения отрезков, площади

### Algorithmic Patterns
- [[patterns-overview]] — карта всех паттернов с навигацией по типу задачи
- [[two-pointers-pattern]] — два указателя для задач на отсортированные массивы и пары
- [[sliding-window-pattern]] — скользящее окно для подмассивов/подстрок фиксированного размера
- [[fast-slow-pointers-pattern]] — Floyd's Algorithm для поиска циклов в linked list
- [[binary-search-pattern]] — бинарный поиск и его вариации (search on answer)
- [[cyclic-sort-pattern]] — сортировка на месте для массивов чисел [1,n]
- [[intervals-pattern]] — merge, insert, intersection для задач на интервалы
- [[dfs-bfs-patterns]] — паттерны обхода деревьев и графов
- [[dp-patterns]] — паттерны динамического программирования (knapsack, LCS, LIS)
- [[top-k-elements-pattern]] — поиск k-го элемента и Top K через heap
- [[two-heaps-pattern]] — median в потоке данных через два heap
- [[k-way-merge-pattern]] — слияние K отсортированных списков
- [[topological-sort-pattern]] — порядок зависимостей в DAG (Kahn's BFS, DFS)
- [[monotonic-stack-pattern]] — next greater/smaller element за O(n)
- [[union-find-pattern]] — Disjoint Set Union для компонент связности
- [[bit-manipulation]] — побитовые операции, XOR трюки, подмножества через маски
- [[meet-in-the-middle]] — разделение пополам для сокращения перебора с 2^n до 2^(n/2)
- [[string-algorithms-advanced]] — продвинутые строковые паттерны (KMP, Z-function, hashing)

### Interview Prep
- [[leetcode-roadmap]] — Blind 75, NeetCode 150, стратегия и spaced repetition
- [[common-mistakes]] — топ-5 ошибок на coding интервью и как их избежать
- [[mock-interview-guide]] — подготовка к mock интервью, платформы, чек-листы

### Competitive Programming
- [[competitive-programming-overview]] — обзор CP: платформы, рейтинги, подготовка
- [[problem-classification]] — классификация задач по constraints и ключевым словам
- [[contest-strategy]] — стратегия контеста: time allocation, pivot strategy, психология
- [[implementation-tips]] — Fast I/O, templates, debugging tricks для CP

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| Big O | Асимптотический анализ сложности алгоритма | [[big-o-complexity]] |
| Two Pointers | Два указателя сужают пространство поиска | [[two-pointers-pattern]] |
| Sliding Window | Окно скользит по массиву, поддерживая инвариант | [[sliding-window-pattern]] |
| Binary Search | Деление пополам на монотонном предикате | [[binary-search-pattern]] |
| DFS/BFS | Обход в глубину (стек) и ширину (очередь) | [[dfs-bfs-patterns]] |
| Dynamic Programming | Разбиение на подзадачи с запоминанием результатов | [[dynamic-programming]] |
| Greedy | Локально оптимальный выбор = глобальный оптимум | [[greedy-algorithms]] |
| Union-Find | Объединение множеств и проверка связности за ~O(1) | [[union-find-pattern]] |
| Topological Sort | Линейный порядок вершин DAG по зависимостям | [[topological-sort-pattern]] |
| Segment Tree | Range queries и updates за O(log n) | [[segment-tree]] |

## Связанные области

- [[programming-moc]] — языки программирования и парадигмы
- [[cs-foundations-moc]] — фундамент CS: память, компиляция, конкурентность, типы
