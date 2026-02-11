---
title: "CS Fundamentals: путь обучения"
created: 2026-02-10
modified: 2026-02-10
type: guide
tags:
  - topic/cs-fundamentals
  - type/guide
  - navigation
---

# CS Fundamentals: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

---

## Уровень 1: Основы (Beginner)
> Цель: Понять Big O, базовые структуры данных, основы рекурсии и научиться писать первый алгоритмический код
> Время: ~4 недели

1. [[cs-fundamentals-overview]] — обзор раздела и навигация по уровням
2. [[big-o-complexity]] — полное руководство по анализу сложности алгоритмов
3. [[problem-solving-framework]] — UMPIRE метод и метод Полья для решения задач
4. [[code-explained-from-zero]] — код с объяснением каждой строки для начинающих (Kotlin)
5. [[arrays-strings]] — фундамент: непрерывная память, cache locality, random access
6. [[linked-lists]] — узлы и указатели, singly/doubly/circular, fast-slow pointers
7. [[stacks-queues]] — LIFO и FIFO, deque, monotonic stack
8. [[hash-tables]] — хеш-функции, коллизии, O(1) lookup
9. [[trees-binary]] — бинарные деревья и BST, обходы (DFS/BFS), балансировка
10. [[heaps-priority-queues]] — min/max heap, sift up/down, top-k pattern
11. [[graphs]] — представления графов, обходы, компоненты связности
12. [[recursion-fundamentals]] — рекурсия от нуля: call stack, base case, tail call optimization
13. [[sorting-algorithms]] — все виды сортировок: comparison-based и linear-time
14. [[searching-algorithms]] — binary search, lower/upper bound, search on answer

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить основные алгоритмические паттерны и подготовиться к coding интервью
> Время: ~6 недель
> Prerequisites: Level 1

### Алгоритмы
15. [[divide-and-conquer]] — разбиение задачи на подзадачи, Master Theorem
16. [[greedy-algorithms]] — локально оптимальные решения, greedy choice property
17. [[dynamic-programming]] — overlapping subproblems, memoization, tabulation
18. [[backtracking]] — полный перебор с отсечением, constraint satisfaction
19. [[graph-algorithms]] — BFS, DFS, Dijkstra и базовые графовые алгоритмы
20. [[string-algorithms]] — KMP, Rabin-Karp, Z-function для pattern matching

### Паттерны
21. [[patterns-overview]] — карта всех паттернов с навигацией по типу задачи
22. [[two-pointers-pattern]] — два указателя для задач на отсортированные массивы и пары
23. [[sliding-window-pattern]] — скользящее окно для подмассивов/подстрок
24. [[fast-slow-pointers-pattern]] — Floyd's Algorithm для поиска циклов
25. [[binary-search-pattern]] — бинарный поиск и его вариации (search on answer)
26. [[cyclic-sort-pattern]] — сортировка на месте для массивов чисел [1,n]
27. [[intervals-pattern]] — merge, insert, intersection для задач на интервалы
28. [[dfs-bfs-patterns]] — паттерны обхода деревьев и графов
29. [[dp-patterns]] — паттерны DP: knapsack, LCS, LIS
30. [[top-k-elements-pattern]] — поиск k-го элемента и Top K через heap
31. [[two-heaps-pattern]] — median в потоке данных через два heap
32. [[k-way-merge-pattern]] — слияние K отсортированных списков
33. [[topological-sort-pattern]] — порядок зависимостей в DAG (Kahn's BFS, DFS)
34. [[monotonic-stack-pattern]] — next greater/smaller element за O(n)
35. [[union-find-pattern]] — Disjoint Set Union для компонент связности
36. [[bit-manipulation]] — побитовые операции, XOR трюки, подмножества через маски

### Интервью
37. [[leetcode-roadmap]] — Blind 75, NeetCode 150, стратегия и spaced repetition
38. [[common-mistakes]] — топ-5 ошибок на coding интервью и как их избежать
39. [[mock-interview-guide]] — подготовка к mock интервью, платформы, чек-листы

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Освоить продвинутые алгоритмы, сложные графовые задачи, строковые алгоритмы и продвинутые структуры данных
> Время: ~4 недели
> Prerequisites: Level 2

### Продвинутые структуры данных
40. [[trees-advanced]] — AVL и Red-Black деревья, self-balancing с гарантией O(log n)
41. [[tries]] — префиксное дерево для работы со строками и автодополнением
42. [[segment-tree]] — range queries и updates за O(log n), lazy propagation
43. [[fenwick-tree]] — Binary Indexed Tree для prefix sum за O(log n)
44. [[sparse-table]] — статические Range Minimum Query за O(1)

### Продвинутые алгоритмы
45. [[code-explained-advanced]] — продвинутый код с пошаговым разбором
46. [[graph-advanced]] — Floyd-Warshall, Bellman-Ford, A*, bidirectional search
47. [[shortest-paths]] — Dijkstra, Bellman-Ford, Floyd-Warshall, 0-1 BFS
48. [[minimum-spanning-tree]] — Kruskal, Prim, Boruvka, Cut Property
49. [[string-advanced]] — Suffix Array, Aho-Corasick, Manacher, Suffix Automaton
50. [[string-algorithms-advanced]] — продвинутые строковые паттерны (KMP, Z-function, hashing)
51. [[meet-in-the-middle]] — разделение пополам для сокращения перебора

---

## Уровень 4: Экспертиза (Expert)
> Цель: Competitive programming, олимпиадные алгоритмы, сложные оптимизации DP и теория чисел
> Время: ~4 недели
> Prerequisites: Level 3

52. [[dp-optimization]] — Convex Hull Trick, D&C optimization, SOS DP, Matrix Exponentiation
53. [[network-flow]] — Ford-Fulkerson, Edmonds-Karp, Dinic, Max-Flow = Min-Cut
54. [[combinatorics]] — nCr, Lucas theorem, Catalan numbers, Inclusion-Exclusion
55. [[number-theory]] — GCD, modular exponentiation, Sieve, Chinese Remainder Theorem
56. [[computational-geometry]] — выпуклая оболочка, пересечения отрезков, площади
57. [[persistent-structures]] — версионные структуры данных с path copying

### Competitive Programming
58. [[competitive-programming-overview]] — обзор CP: платформы, рейтинги, подготовка
59. [[problem-classification]] — классификация задач по constraints и ключевым словам
60. [[contest-strategy]] — стратегия контеста: time allocation, pivot strategy, психология
61. [[implementation-tips]] — Fast I/O, templates, debugging tricks для CP

### Мета
62. [[learning-path]] — оригинальный учебный план по CS Fundamentals
