# Research Report: Dynamic Programming

**Date:** 2025-12-29
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Dynamic Programming (DP) — техника оптимизации рекурсивных решений через сохранение результатов подзадач (memoization) или построение снизу-вверх (tabulation). Ключевые свойства: overlapping subproblems и optimal substructure. 20 основных паттернов покрывают 90% задач: Fibonacci, Knapsack, LCS, LIS, Kadane, Grid DP, Interval DP, Bitmask DP и др. Space optimization через rolling array снижает O(n²) → O(n). Для FAANG критично понимание state design и transition формул.

---

## Key Findings

### 1. Two Approaches: Top-Down vs Bottom-Up

| Aspect | Top-Down (Memoization) | Bottom-Up (Tabulation) |
|--------|------------------------|------------------------|
| **Направление** | От главной задачи к базовым | От базовых к главной |
| **Реализация** | Рекурсия + кэш | Итеративно + таблица |
| **Stack Overflow** | Риск при большом input | Нет риска |
| **Когда лучше** | Не все подзадачи нужны | Нужны все подзадачи |
| **Space Optimization** | Сложно | Легко (rolling array) |
| **Performance** | Overhead рекурсии | Быстрее на константу |

### 2. State Design Framework

**4 шага проектирования состояния:**
1. **State (状态)** — какие параметры однозначно определяют подзадачу?
2. **Choices (选择)** — какие решения можно принять на каждом шаге?
3. **DP Array Meaning** — что именно хранится в dp[i] или dp[i][j]?
4. **Transition** — как связаны состояния между собой?

**Пример для Knapsack:**
- State: (index, remaining_weight)
- Choices: взять предмет или пропустить
- dp[i][w] = максимальная ценность с первыми i предметами и весом w
- Transition: dp[i][w] = max(dp[i-1][w], dp[i-1][w-weight[i]] + value[i])

### 3. Dimensions of DP

| Dimension | State Variables | Пример задачи |
|-----------|-----------------|---------------|
| **1D** | Один индекс (dp[i]) | Fibonacci, Climbing Stairs, House Robber |
| **2D** | Два индекса (dp[i][j]) | LCS, Knapsack, Grid Paths |
| **3D** | Три индекса (dp[i][j][k]) | Two robots, K coins in grid |

**Правило определения dimension:**
- Считаем количество изменяющихся параметров в рекурсии
- 1 параметр → 1D, 2 параметра → 2D, и т.д.

### 4. 20 Key DP Patterns

| # | Pattern | Key Insight | Example Problems |
|---|---------|-------------|------------------|
| 1 | **Fibonacci** | F(n) = F(n-1) + F(n-2) | Climbing Stairs, Min Cost Climbing |
| 2 | **Kadane's** | Max subarray ending at i | Maximum Subarray, Max Product |
| 3 | **0/1 Knapsack** | Take or skip each item once | Partition Equal Subset Sum, Target Sum |
| 4 | **Unbounded Knapsack** | Items can repeat | Coin Change, Perfect Squares |
| 5 | **LCS** | dp[i][j] = longest common of prefixes | Edit Distance, Shortest Supersequence |
| 6 | **LIS** | Longest increasing subsequence | Russian Doll, Number of LIS |
| 7 | **Palindromic Subsequence** | Same forwards/backwards | Longest Palindrome, Min Insertions |
| 8 | **Edit Distance** | Insert, delete, replace | Levenshtein, Min ASCII Delete |
| 9 | **Subset Sum** | Can we reach target sum? | Partition, Target Sum |
| 10 | **String Partition** | Split satisfying condition | Word Break, Palindrome Partition |
| 11 | **Catalan Numbers** | C(n) = Σ C(i)×C(n-1-i) | Unique BSTs, Valid Parentheses |
| 12 | **Matrix Chain** | Optimal operation order | Burst Balloons, Minimum Score |
| 13 | **Count Ways** | Number of paths/combinations | Decode Ways, Count Texts |
| 14 | **Grid DP** | 2D navigation | Unique Paths, Min Path Sum |
| 15 | **Tree DP** | Post-order traversal | House Robber III, Binary Tree Cameras |
| 16 | **Graph DP** | Optimal paths on graphs | Cheapest Flights K Stops |
| 17 | **Digit DP** | Count by digits | Numbers with Unique Digits |
| 18 | **Bitmask DP** | Subsets via bits | Shortest Path All Nodes, TSP |
| 19 | **Probability DP** | Expected values | Knight Probability, New 21 Game |
| 20 | **State Machine** | Transitions between states | Stock Buy/Sell with Cooldown |

### 5. Space Optimization (Rolling Array)

**Принцип:** если dp[i] зависит только от dp[i-1] (или dp[i-1] и dp[i-2]), храним только нужные строки.

**Техники:**
1. **Two variables**: O(n) → O(1) для Fibonacci-подобных
2. **Two rows**: O(n×m) → O(m) для 2D DP
3. **Single row with reverse**: для 0/1 Knapsack

**Важно для 0/1 Knapsack:**
- При 1D оптимизации итерируем **справа налево**
- Иначе перезаписываем значения до их использования

### 6. Common Classic Problems

| Problem | Time | Space | Pattern |
|---------|------|-------|---------|
| Fibonacci | O(n) | O(1) | Fibonacci |
| Climbing Stairs | O(n) | O(1) | Fibonacci |
| 0/1 Knapsack | O(n×W) | O(W) | Knapsack |
| Coin Change | O(n×amount) | O(amount) | Unbounded Knapsack |
| LCS | O(n×m) | O(min(n,m)) | LCS |
| LIS | O(n log n) | O(n) | LIS + Binary Search |
| Edit Distance | O(n×m) | O(m) | Edit Distance |
| Matrix Chain | O(n³) | O(n²) | Interval |
| Unique Paths | O(n×m) | O(m) | Grid |
| House Robber | O(n) | O(1) | Decision Making |

### 7. Advanced DP Optimizations

| Technique | When to Use | Complexity |
|-----------|-------------|------------|
| **Convex Hull Trick** | dp[i] = min(dp[j] + b[j]×a[i]) | O(n) → O(n log n) |
| **Divide & Conquer** | Монотонность opt[i] ≤ opt[i+1] | O(n²) → O(n log n) |
| **Knuth's** | Quadrangle inequality | O(n³) → O(n²) |
| **Li Chao Tree** | Dynamic CHT | O(n log n) |
| **SOS DP** | Sum over subsets | O(n×2^n) |

### 8. Interview Strategy

**5 шагов решения DP задачи:**
1. **Identify DP** — есть overlapping + optimal substructure?
2. **Define State** — что уникально идентифицирует подзадачу?
3. **Find Transition** — как связаны состояния?
4. **Base Cases** — каковы начальные значения?
5. **Implement** — memoization или tabulation?

**FAST Method (Simple Programmer):**
- **F**ind first solution (brute force recursive)
- **A**nalyze solution (identify repeated work)
- **S**ubproblems (cache them)
- **T**urn around (convert to bottom-up if needed)

### 9. Common Mistakes

| Mistake | Description | Fix |
|---------|-------------|-----|
| **Wrong state** | Недостаточно параметров | Добавить все изменяющиеся переменные |
| **Wrong transition** | Неправильная формула связи | Проверить на маленьких примерах |
| **Missing base case** | dp[0] не инициализирован | Всегда явно задавать base cases |
| **Off-by-one** | Индексы +1/-1 | Внимательно с 0-based/1-based |
| **Wrong iteration order** | Зависимость не соблюдена | DAG топологический порядок |
| **Premature optimization** | Сразу rolling array | Сначала полная таблица |

### 10. When to Use DP

**DP подходит когда:**
- Maximum/minimum optimization
- Counting number of ways
- Feasibility (can we reach?)
- Overlapping subproblems присутствуют
- Optimal substructure есть

**DP НЕ подходит когда:**
- Greedy даёт optimal (доказуемо)
- Нет overlapping (divide & conquer)
- Нужен конкретный path (не только значение)

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Tech Interview Handbook - DP](https://www.techinterviewhandbook.org/algorithms/dynamic-programming/) | Guide | 0.95 |
| 2 | [20 Patterns to Master DP - AlgoMaster](https://blog.algomaster.io/p/20-patterns-to-master-dynamic-programming) | Patterns | 0.95 |
| 3 | [GeeksforGeeks - Complete DP Guide](https://www.geeksforgeeks.org/complete-guide-to-dynamic-programming/) | Reference | 0.90 |
| 4 | [Labuladong - DP Framework](https://labuladong.online/algo/en/essential-technique/dynamic-programming-framework/) | Framework | 0.90 |
| 5 | [USACO Guide - Bitmask DP](https://usaco.guide/gold/dp-bitmasks) | Tutorial | 0.95 |
| 6 | [Stack Overflow - Beginner's Guide](https://stackoverflow.blog/2022/01/31/the-complete-beginners-guide-to-dynamic-programming/) | Tutorial | 0.90 |
| 7 | [Codeforces - DP Optimizations](https://codeforces.com/blog/entry/8219) | Advanced | 0.95 |
| 8 | [EnjoyAlgorithms - Top-Down vs Bottom-Up](https://www.enjoyalgorithms.com/blog/top-down-memoization-vs-bottom-up-tabulation/) | Comparison | 0.90 |
| 9 | [Educative - Grokking DP](https://www.designgurus.io/course/grokking-dynamic-programming) | Course | 0.90 |
| 10 | [AlgoMonster - DP Intro](https://algo.monster/problems/dynamic_programming_intro) | Tutorial | 0.90 |
| 11 | [MIT OCW - Lecture 16 DP](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/resources/lecture-16-dynamic-programming-part-2-lcs-lis-coins/) | Academic | 0.95 |
| 12 | [Wikipedia - Matrix Chain Multiplication](https://en.wikipedia.org/wiki/Matrix_chain_multiplication) | Reference | 0.95 |

---

*Generated: 2025-12-29*
