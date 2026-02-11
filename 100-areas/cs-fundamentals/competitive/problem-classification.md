---
title: "Классификация задач по ограничениям"
created: 2026-02-09
modified: 2026-02-09
type: reference
status: published
tags:
  - topic/cs-fundamentals
  - type/reference
  - level/intermediate
related:
  - "[[competitive-programming-overview]]"
  - "[[contest-strategy]]"
  - "[[patterns-overview]]"
prerequisites:
  - "[[big-o-complexity]]"
  - "[[arrays-strings]]"
---

# Problem Classification

## TL;DR

Классификация задач — ключ к быстрому решению. Смотри на **ограничения N** (определяет сложность алгоритма), **ключевые слова** (подсказывают тип), **структуру данных** (граф/строка/массив). N ≤ 20 → перебор, N ≤ 10^5 → O(N log N), N ≤ 10^9 → математика.

---

## Интуиция

### Аналогия 1: Constraints как диагноз врача

```
ВРАЧ СТАВИТ ДИАГНОЗ ПО СИМПТОМАМ:

Симптомы:               Диагноз:
• Температура 39°       → Вирус
• Боль в горле          → Ангина
• Кашель + хрипы        → Бронхит

Constraints в задаче = симптомы:
• N ≤ 20               → Перебор/bitmask DP
• N ≤ 10^5, запросы   → Segment Tree
• "Кратчайший путь"    → BFS/Dijkstra

Не угадывай алгоритм — ДИАГНОСТИРУЙ его!
```

### Аналогия 2: Паттерны как жанры кино

```
ЖАНР ФИЛЬМА ОПРЕДЕЛЯЕТ ОЖИДАНИЯ:

Название "Крик в ночи"   → Хоррор → будут скримеры
Название "Любовь в Париже" → Ромком → happy end

Слова в условии:
"Минимальное количество" → Greedy или DP
"Все возможные"          → Перебор/backtracking
"Связные компоненты"     → DFS/DSU
"Подотрезок с макс суммой" → Sliding window/Kadane

Ключевые слова = жанр задачи.
```

---

## Частые ошибки

### Ошибка 1: Игнорировать ограничения

**СИМПТОМ:** Написал O(N²), получил TLE при N = 10^5

```
ЧЕКЛИСТ ПЕРЕД КОДИНГОМ:
□ Какое N?
□ Какая сложность допустима?
□ Мой алгоритм укладывается?

N = 10^5 → O(N²) = 10^10 операций → TLE!
Нужен O(N log N) максимум.
```

**РЕШЕНИЕ:** Первым делом — ограничения, потом алгоритм.

### Ошибка 2: Не распознать стандартный паттерн

**СИМПТОМ:** Изобретаешь велосипед, когда есть готовое решение

```
СТАНДАРТНЫЕ ПАТТЕРНЫ:
"Минимум в окне"          → Monotonic Deque
"K-й элемент"             → QuickSelect / Heap
"Количество пар с суммой" → Two Pointers / HashMap
"Циклы в графе"           → DFS с цветами

Не изобретай — узнавай!
```

**РЕШЕНИЕ:** Изучи 15-20 основных паттернов наизусть.

### Ошибка 3: Путать похожие типы задач

**СИМПТОМ:** Применил Dijkstra где нужен BFS (или наоборот)

```
КОГДА ЧТО:

BFS: невзвешенный граф, кратчайший путь
Dijkstra: взвешенный граф, положительные веса
Bellman-Ford: есть отрицательные веса
Floyd-Warshall: все пары кратчайших путей

0-1 BFS: веса только 0 и 1 (быстрее Dijkstra!)
```

**РЕШЕНИЕ:** Таблица "тип задачи → алгоритм" в голове.

---

## Ментальные модели

### Модель 1: "N определяет всё"

```
ТАБЛИЦА РЕШЕНИЙ:

N ≤ 10      → O(N!)      Полный перебор перестановок
N ≤ 20      → O(2^N)     Bitmask DP, meet-in-middle
N ≤ 500     → O(N³)      Floyd-Warshall, matrix
N ≤ 5000    → O(N²)      Простой DP
N ≤ 10^5   → O(N log N) Сортировка, binary search
N ≤ 10^6   → O(N)       Линейные алгоритмы
N ≤ 10^9   → O(log N)   Бинпоиск по ответу, math
N ≤ 10^18  → O(1)       Формула!

Запомни эту таблицу — она работает в 90% задач.
```

### Модель 2: "Тип данных → Структура данных"

```
ЧТО ДАНО → ЧТО ИСПОЛЬЗОВАТЬ:

Массив + range queries     → Segment Tree / BIT
Множество + объединение    → DSU
Граф + компоненты          → DFS / DSU
Строка + подстроки         → Hashing / Trie / SA
Последовательность + LIS   → Binary Search + DP
Точки на плоскости         → Geometry / Sweep Line

Структура входных данных подсказывает решение!
```

---

## 1. Обзор

### Зачем классифицировать задачи

```
1. Быстрее распознавать паттерны
2. Знать какой алгоритм применять
3. Оценивать сложность решения по ограничениям
4. Понимать что изучать дальше
```

### Основные категории

Типичные задачи competitive programming принадлежат к:
- **Ad-hoc / Implementation** — уникальные, без стандартного алгоритма
- **Math / Number Theory** — математика, простые числа, НОД
- **Greedy** — жадные алгоритмы
- **Dynamic Programming** — оптимальная подструктура
- **Graphs** — пути, циклы, деревья
- **Data Structures** — сегментные деревья, DSU
- **Strings** — хеширование, суффиксные структуры
- **Geometry** — точки, многоугольники, выпуклые оболочки
- **Game Theory** — ним, sprague-grundy
- **Constructive Algorithms** — построение ответа

---

## 2. Определение типа по ограничениям

### Главное правило

```
Большинство систем позволяют ~10^8 операций в секунду.
Время ограничено 1-2 секундами → ~10^8 - 2×10^8 операций максимум.
```

### Таблица соответствия

| Ограничение N | Допустимая сложность | Типичные алгоритмы |
|---------------|---------------------|-------------------|
| N ≤ 10 | O(N!) | Полный перебор перестановок |
| N ≤ 15-20 | O(2^N), O(N × 2^N) | Bitmask DP, meet-in-the-middle |
| N ≤ 20-25 | O(2^N) | Перебор подмножеств |
| N ≤ 50 | O(N^4) | Редко, но возможно |
| N ≤ 100 | O(N³) | Floyd-Warshall, матрицы |
| N ≤ 500 | O(N³) | Matrix mult, cubic DP |
| N ≤ 1000 | O(N²) | Простые DP, brute force |
| N ≤ 5000 | O(N²) | Более оптимизированные O(N²) |
| N ≤ 10^5 | O(N log N), O(N√N) | Sorting, binary search, segment tree |
| N ≤ 10^6 | O(N), O(N log N) | Linear algorithms, counting |
| N ≤ 10^7 | O(N) | Только линейные |
| N ≤ 10^9 | O(log N), O(√N) | Binary search, math formulas |
| N ≤ 10^18 | O(log N), O(1) | Math, binary exponentiation |

### Примеры применения

```kotlin
// Пример 1: N ≤ 20
// Ограничение намекает на bitmask DP или перебор подмножеств

fun solve(n: Int, arr: IntArray): Int {
    // O(2^n × n) — допустимо для n ≤ 20
    val dp = IntArray(1 shl n) { Int.MAX_VALUE }
    dp[0] = 0

    for (mask in 0 until (1 shl n)) {
        for (i in 0 until n) {
            if (mask and (1 shl i) == 0) {
                // переход
            }
        }
    }
    return dp[(1 shl n) - 1]
}

// Пример 2: N ≤ 10^5
// Думаем о O(N log N) — sorting, binary search, segment tree

fun solve(n: Int, arr: IntArray): Long {
    arr.sort()  // O(N log N)
    // ... какая-то логика O(N)
    return answer
}

// Пример 3: N ≤ 10^9
// Нужен O(log N) или O(1) — binary search или математика

fun solve(n: Long): Long {
    // Binary search по ответу
    var lo = 0L
    var hi = n
    while (lo < hi) {
        val mid = (lo + hi + 1) / 2
        if (check(mid)) lo = mid
        else hi = mid - 1
    }
    return lo
}
```

---

## 3. Классификация по тегам

### Статистика Codeforces (топ-20 тегов)

| # | Тег | Кол-во задач | Типичная сложность |
|---|-----|-------------|-------------------|
| 1 | implementation | 2000+ | 800-1400 |
| 2 | math | 1800+ | 800-2000 |
| 3 | greedy | 1500+ | 900-1600 |
| 4 | dp | 1400+ | 1200-2400 |
| 5 | constructive algorithms | 849 | 1000-1800 |
| 6 | brute force | 800+ | 800-1400 |
| 7 | data structures | 700+ | 1400-2400 |
| 8 | graphs | 663 | 1400-2200 |
| 9 | sortings | 598 | 900-1400 |
| 10 | binary search | 577 | 1200-1800 |
| 11 | dfs and similar | 564 | 1200-1800 |
| 12 | trees | 482 | 1400-2200 |
| 13 | strings | 458 | 1200-2000 |
| 14 | number theory | 409 | 1200-2000 |
| 15 | combinatorics | 340 | 1400-2200 |
| 16 | geometry | 276 | 1600-2400 |
| 17 | bitmasks | 270 | 1400-2000 |
| 18 | two pointers | 268 | 1200-1600 |
| 19 | dsu | 204 | 1400-1800 |
| 20 | shortest paths | 159 | 1400-2000 |

### Распределение по сложности

```
Рейтинг 800-1200 (A-B задачи Div.2):
- implementation, brute force
- math (базовые)
- greedy (простые)
- sortings

Рейтинг 1200-1600 (C-D задачи):
- dp (классические)
- binary search
- two pointers
- dfs/bfs
- number theory

Рейтинг 1600-2000 (D-E задачи):
- advanced dp
- segment tree, BIT
- graphs (продвинутые)
- strings (KMP, Z-function)
- combinatorics

Рейтинг 2000+ (E-F задачи):
- flows
- FFT/NTT
- suffix structures
- advanced geometry
- матрицы
```

---

## 4. Распознавание паттернов

### По ключевым словам в условии

| Ключевые слова | Вероятный тип |
|---------------|--------------|
| "minimum/maximum cost" | DP или Greedy |
| "number of ways" | DP (counting) или Combinatorics |
| "shortest path" | BFS/Dijkstra |
| "connected components" | DFS/DSU |
| "substring/subsequence" | String DP или алгоритмы |
| "divisibility, GCD" | Number Theory |
| "permutation" | Counting/Combinatorics |
| "tree structure" | Tree DP, DFS |
| "range queries" | Segment Tree, BIT |
| "game, first/second player wins" | Game Theory |
| "convex polygon" | Geometry |
| "matching" | Bipartite Matching/Flow |

### По структуре входных данных

```kotlin
// 1. Массив с запросами update/query → Segment Tree или BIT
// Input: n, q — размер массива и число запросов
// n, q ≤ 10^5 — segment tree

// 2. Граф с весами рёбер → Shortest Path
// Input: n, m — вершины, рёбра
// Если веса неотрицательные → Dijkstra
// Если есть отрицательные → Bellman-Ford

// 3. Дерево → Tree DP или DFS
// Input: n вершин, n-1 рёбер

// 4. Строки → String Algorithms
// |s| ≤ 10^6 → линейные алгоритмы (Z, KMP)
// Множество строк с общей длиной ≤ 10^5 → Aho-Corasick или хеширование

// 5. Матрица n×m → 2D DP или BFS
// n, m ≤ 1000 → O(n×m) или O(n×m×log)
```

### Типичные constraint patterns

| Constraints | Вероятный подход |
|-------------|-----------------|
| N ≤ 20, find subset | Bitmask DP |
| N ≤ 40, find subset | Meet in the middle |
| N ≤ 10^5, pairs (i,j) | Two pointers / Binary search |
| N ≤ 10^5, range queries | Segment Tree / BIT |
| N, M ≤ 10^5, graph | O(N + M) graph traversal |
| N ≤ 10^9, K ≤ 10^5 | Binary search + simulation |
| Sum of N ≤ 10^5 across tests | Total complexity matters |

---

## 5. Детальная классификация

### Ad-Hoc / Implementation

```
Признаки:
- Нет стандартного алгоритма
- Нужно аккуратно реализовать условие
- Часто много edge cases

Подходы:
1. Внимательно прочитать условие
2. Выписать примеры
3. Найти паттерн
4. Аккуратно закодить

Примеры:
- Симуляция процесса
- Работа со строками/массивами
- Математические преобразования
```

### Greedy

```
Признаки:
- "Минимизировать/максимизировать"
- Локальный оптимум → глобальный оптимум
- Часто связано с сортировкой

Типичные стратегии:
1. Сортировка и жадный выбор
2. Приоритетная очередь
3. Обмен (exchange argument)

Примеры:
- Activity Selection
- Fractional Knapsack
- Huffman Coding
- Interval Scheduling
```

### Dynamic Programming

```
Признаки:
- "Number of ways"
- "Minimum cost to reach"
- Optimal substructure
- Overlapping subproblems

Подтипы:
1. Linear DP: dp[i] — оптимальное для первых i элементов
2. Interval DP: dp[l][r] — оптимальное для отрезка [l, r]
3. Knapsack: dp[i][w] — с первыми i предметами и capacity w
4. Bitmask DP: dp[mask] — для подмножества mask
5. Digit DP: dp[pos][tight][state] — числа до N
6. Tree DP: dp[v] — для поддерева вершины v
7. DP on DAG: топологический порядок + DP

Оптимизации:
- Convex Hull Trick
- Divide & Conquer DP
- SOS DP
- Matrix Exponentiation
```

### Graphs

```
Подкатегории:

1. Traversal (обход):
   - DFS, BFS
   - Топологическая сортировка
   - Поиск циклов

2. Shortest Paths:
   - BFS (невзвешенный)
   - Dijkstra (неотрицательные веса)
   - Bellman-Ford (отрицательные веса)
   - Floyd-Warshall (все пары)

3. MST:
   - Kruskal + DSU
   - Prim

4. Connectivity:
   - Компоненты связности
   - Мосты и точки сочленения
   - SCC (Kosaraju, Tarjan)

5. Trees:
   - LCA
   - Tree DP
   - Centroid Decomposition
   - HLD

6. Flows & Matching:
   - Ford-Fulkerson / Dinic
   - Bipartite Matching
   - Min-Cost Max-Flow
```

### Strings

```
Подкатегории:

1. Базовые:
   - KMP (pattern matching)
   - Z-function
   - Rabin-Karp (hashing)

2. Продвинутые:
   - Suffix Array
   - Suffix Automaton
   - Aho-Corasick (multiple patterns)
   - Manacher (palindromes)

3. DP на строках:
   - LCS, Edit Distance
   - Distinct Subsequences

Паттерны ограничений:
- |s| ≤ 10^6 → O(N) алгоритмы
- |s| ≤ 10^5, много запросов → предподсчёт
- Много строк, Σ|s| ≤ 10^5 → Trie или Aho-Corasick
```

### Number Theory

```
Подкатегории:

1. Divisibility:
   - GCD, LCM
   - Делители

2. Primes:
   - Sieve of Eratosthenes
   - Prime factorization
   - Primality tests

3. Modular Arithmetic:
   - Modular inverse
   - Chinese Remainder Theorem
   - Fermat's little theorem

4. Combinatorics:
   - Factorial, nCr
   - Lucas theorem
   - Catalan numbers

Паттерны:
- N ≤ 10^6 → Sieve
- N ≤ 10^9 → Prime check O(√N)
- N ≤ 10^18 → Miller-Rabin
```

### Data Structures

```
Подкатегории:

1. Basic:
   - Stack, Queue, Deque
   - Priority Queue (Heap)
   - Set, Map

2. Trees:
   - Segment Tree
   - Fenwick Tree (BIT)
   - Sparse Table (RMQ)

3. Advanced:
   - Treap / Splay Tree
   - Persistent Structures
   - Link-Cut Tree

4. Union-Find:
   - DSU with ranks/sizes
   - Path compression

Паттерны ограничений:
- Range queries + updates → Segment Tree
- Range queries only → Sparse Table
- Prefix queries → BIT
- Dynamic connectivity → DSU
```

---

## 6. Матрица "Задача → Алгоритм"

### Quick Reference

| Задача | Первый подход | Альтернатива |
|--------|--------------|-------------|
| Найти сумму на отрезке с изменениями | Segment Tree | BIT |
| Найти k-й элемент | Binary Search | Order Statistics Tree |
| Кратчайший путь без весов | BFS | - |
| Кратчайший путь с весами ≥ 0 | Dijkstra | - |
| Все кратчайшие пути | Floyd-Warshall | Dijkstra N раз |
| Число способов достичь | DP | Combinatorics |
| Минимальная стоимость пути | DP | Dijkstra (если граф) |
| Проверить подстроку | KMP | Hashing |
| Множество паттернов | Aho-Corasick | Trie + DFS |
| LCA | Binary Lifting | HLD |
| Merge intervals | Sorting + Sweep | - |
| Max в sliding window | Deque | Segment Tree |

---

## 7. Checklist распознавания

### Алгоритм анализа задачи

```
1. ПРОЧИТАТЬ условие внимательно
   □ Что дано?
   □ Что найти?
   □ Какие ограничения?

2. ОПРЕДЕЛИТЬ ограничения
   □ N ≤ ? → какая сложность допустима?
   □ Есть ли time limit hints?

3. НАЙТИ ключевые слова
   □ "Minimum/Maximum" → DP/Greedy
   □ "Number of ways" → DP/Combinatorics
   □ "Shortest" → BFS/Dijkstra
   □ "Connected" → DFS/DSU
   □ "Substring" → String algorithms

4. ОПРЕДЕЛИТЬ структуру
   □ Массив → Sorting/DP/Two pointers
   □ Граф → Traversal/Shortest path
   □ Дерево → Tree DP/DFS
   □ Строка → String algorithms
   □ Сетка → BFS/DP

5. ВСПОМНИТЬ похожие задачи
   □ Решал ли я подобное?
   □ Какой алгоритм применял?

6. ПРОВЕРИТЬ гипотезу
   □ Подходит ли сложность?
   □ Работает ли на примерах?
```

---

## 8. Типичные комбинации

### Частые сочетания тегов

```
1. DP + Graphs = DP on DAG или Tree DP
2. Binary Search + Greedy = Binary Search по ответу
3. Math + DP = Combinatorics DP
4. Graphs + DSU = Connectivity задачи
5. Strings + DP = LCS, Edit Distance
6. Data Structures + Graphs = Online queries на графе
7. Geometry + Sorting = Sweep Line
8. Bitmasks + DP = Subset DP
```

### Примеры задач по комбинациям

```kotlin
// DP + Binary Search: найти LIS за O(N log N)
fun lis(arr: IntArray): Int {
    val dp = mutableListOf<Int>()
    for (x in arr) {
        val pos = dp.binarySearch(x).let { if (it < 0) -it - 1 else it }
        if (pos == dp.size) dp.add(x)
        else dp[pos] = x
    }
    return dp.size
}

// Graphs + DP: кратчайший путь = BFS/Dijkstra + релаксация
// Это по сути DP на DAG (после топсорта по расстоянию)

// Bitmask + DP: TSP
fun tsp(dist: Array<IntArray>): Int {
    val n = dist.size
    val dp = Array(1 shl n) { IntArray(n) { Int.MAX_VALUE / 2 } }
    dp[1][0] = 0

    for (mask in 1 until (1 shl n)) {
        for (last in 0 until n) {
            if (mask and (1 shl last) == 0) continue
            for (next in 0 until n) {
                if (mask and (1 shl next) != 0) continue
                val newMask = mask or (1 shl next)
                dp[newMask][next] = minOf(
                    dp[newMask][next],
                    dp[mask][last] + dist[last][next]
                )
            }
        }
    }

    return (0 until n).minOf { dp[(1 shl n) - 1][it] + dist[it][0] }
}
```

---

## 9. Roadmap изучения по категориям

### Уровень 1: Базовый (800-1200)

```
□ Implementation basics
□ Math: GCD, primes, divisibility
□ Sorting + simple greedy
□ Brute force
□ Basic recursion
□ Prefix sums
□ Two pointers basics
```

### Уровень 2: Intermediate (1200-1600)

```
□ Binary search
□ Basic DP (1D, 2D)
□ DFS/BFS
□ Graphs basics
□ DSU
□ Basic number theory
□ String basics (hashing)
□ Stack/Queue applications
```

### Уровень 3: Advanced (1600-2000)

```
□ Segment Tree, BIT
□ Advanced DP (bitmask, digit DP)
□ Trees (LCA, tree DP)
□ Advanced graphs (Dijkstra, Floyd)
□ String algorithms (KMP, Z)
□ Combinatorics (nCr mod p)
□ Geometry basics
□ Game theory basics
```

### Уровень 4: Expert (2000+)

```
□ Segment Tree with lazy propagation
□ DP optimizations (CHT, D&C)
□ Advanced strings (SA, SAM)
□ Flows and matching
□ FFT/NTT
□ Advanced geometry
□ Centroid decomposition
□ HLD
□ Persistent structures
```

---

## 10. Ресурсы по категориям

### Проблемсеты по темам

| Ресурс | Описание |
|--------|----------|
| [CSES Problem Set](https://cses.fi/problemset/) | 300 задач по категориям |
| [USACO Guide](https://usaco.guide/) | Структурированный курс |
| [Codeforces Problemset](https://codeforces.com/problemset) | Фильтр по тегам |
| [AtCoder Problems](https://kenkoooo.com/atcoder/) | Статистика и фильтры |
| [A2OJ Ladders](https://earthshakira.github.io/a2oj-clientside/server/Ladder.html) | Лестницы по рейтингу |

### Справочники

| Ресурс | Тема |
|--------|------|
| [CP-Algorithms](https://cp-algorithms.com/) | Все алгоритмы |
| [USACO Training](https://train.usaco.org/) | Базовые концепции |
| [Competitive Programmer's Handbook](https://cses.fi/book/) | Бесплатная книга |
| [Algorithms for CP](https://blog.shahjalalshohag.com/) | Продвинутые темы |

---

## 11. Резюме

### Главные принципы

```
1. Ограничения определяют сложность
   N ≤ 10^5 → O(N log N) или лучше

2. Ключевые слова указывают на категорию
   "Minimum cost" → DP или Greedy

3. Структура данных намекает на алгоритм
   Дерево → Tree DP, DFS
   Граф → Paths, Connectivity

4. Похожие задачи используют похожие подходы
   Веди журнал решённых задач

5. Практика — ключ к распознаванию
   Чем больше решаешь, тем быстрее видишь паттерны
```

### Quick Reference Card

```
N ≤ 20      → Bitmask DP, 2^N
N ≤ 100     → O(N³)
N ≤ 1000    → O(N²)
N ≤ 10^5    → O(N log N)
N ≤ 10^6    → O(N)
N ≤ 10^9    → O(log N), O(√N)

"минимум/максимум" → DP / Greedy
"число способов"   → DP counting
"кратчайший путь"  → BFS / Dijkstra
"подстрока"        → String algos
"связность"        → DFS / DSU
"запросы [l,r]"    → Segment Tree
"делимость"        → Number theory
"игра"             → Game theory
```

---

## Связь с другими темами

**[[competitive-programming-overview]]** — Классификация задач — это систематизация знаний, описанных в обзоре CP. Overview даёт понимание экосистемы соревнований: платформы, форматы, рейтинги. Классификация же создаёт внутреннюю «базу данных» паттернов: увидел N ≤ 20 — думай bitmask DP, увидел «кратчайший путь» — думай BFS/Dijkstra. Без этой классификации знание алгоритмов остаётся пассивным — знаешь, но не можешь применить в нужный момент на контесте.

**[[contest-strategy]]** — Классификация задач и стратегия контеста работают в паре. Стратегия говорит: «просканируй все задачи в первые 10 минут и выбери с лучшим ROI». Но для оценки ROI нужно быстро классифицировать задачу: определить тип по ограничениям и ключевым словам, оценить сложность реализации. Чем лучше развит навык классификации, тем точнее стратегический выбор — какую задачу решать первой, а какую пропустить.

**[[patterns-overview]]** — Классификация задач и паттерны решения дополняют друг друга. Если patterns-overview описывает конкретные техники (two pointers, sliding window, backtracking), то классификация задач — это метанавык распознавания, какой паттерн применить. Таблица «ключевые слова условия -> вероятный тип задачи» — это по сути маппинг из условия задачи на конкретный паттерн. Без классификации паттерны остаются разрозненными инструментами; классификация превращает их в систему.

---

## Источники и дальнейшее чтение

### Книги

- **Halim, Halim (2013). "Competitive Programming 3."** — Содержит наиболее полную классификацию задач по категориям с привязкой к конкретным задачам UVa Online Judge. Каждая глава организована по типу задач (Complete Search, Divide & Conquer, Greedy, DP, Graph и т.д.) с подкатегориями и подсказками по распознаванию.
- **Laaksonen (2017). "Guide to Competitive Programming."** — Современное руководство на основе CSES problem set, где задачи систематизированы по темам с нарастающей сложностью. Особенно полезна для построения собственной «карты» алгоритмов и понимания, какие техники относятся к какому уровню.
- **Cormen, Leiserson, Rivest, Stein (2009). "Introduction to Algorithms" (CLRS).** — Фундаментальный справочник по алгоритмам, который даёт глубокое понимание каждой категории: доказательства корректности, анализ сложности, варианты. Без этой теоретической базы классификация остаётся поверхностной — CLRS объясняет, почему каждый алгоритм работает и когда он применим.

---

*Последнее обновление: 2026-01-09 — Добавлены педагогические секции (интуиция, частые ошибки, ментальные модели)*
