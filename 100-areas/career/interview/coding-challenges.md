---
title: "Coding Challenges 2025: LeetCode patterns и подготовка к интервью"
created: 2025-12-26
modified: 2025-12-26
type: deep-dive
status: published
confidence: high
tags:
  - topic/career
  - topic/interview
  - topic/algorithms
  - level/senior
related:
  - "[[interview-process]]"
  - "[[technical-interview]]"
---

# Coding Challenges: 12 паттернов, которые покрывают 87% задач

87% задач на FAANG-интервью построены на 10-12 базовых паттернах. Случайное решение 500 задач — путь к выгоранию. Системное изучение паттернов — путь к офферу. Two Pointers, Sliding Window, DFS/BFS, Binary Search — освой эти паттерны, и любая "новая" задача станет вариацией знакомой.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Базовые структуры** | Array, HashMap, LinkedList | CS basics |
| **Big O notation** | Оценка сложности | Algorithm basics |
| **Kotlin/Java** | Язык для решения | Практика |

### Для кого этот материал

| Уровень | Подходит? | Рекомендация |
|---------|-----------|--------------|
| **Junior** | ✅ Да | Начинай с Easy |
| **Middle** | ✅ Да | Medium фокус |
| **Senior** | ✅ Да | Medium/Hard паттерны |

### Терминология для новичков

> 💡 **Coding Interview** = решение алгоритмических задач за 45 минут. Не про знание всех алгоритмов, а про умение распознать паттерн и применить.

| Термин | Значение | Аналогия для новичка |
|--------|----------|---------------------|
| **DSA** | Data Structures & Algorithms | **Математика программирования** |
| **TC** | Time Complexity — O(n), O(log n) | **Сколько времени** — больше данных = дольше? |
| **SC** | Space Complexity | **Сколько памяти** |
| **Pattern** | Типовой подход к задаче | **Шаблон решения** |
| **Two Pointers** | Два указателя с разных концов | **Сжимаем границы** |
| **Sliding Window** | Скользящее окно | **Смотрим через рамку** |
| **Binary Search** | Бинарный поиск | **Делим пополам** |
| **DFS/BFS** | Обход графа/дерева | **В глубину / в ширину** |
| **Dynamic Programming** | Разбиение на подзадачи | **Запоминаем решения** |
| **Greedy** | Жадный алгоритм | **Бери лучшее сейчас** |

---

## Терминология

| Термин | Что это |
|--------|---------|
| **DSA** | Data Structures & Algorithms |
| **TC** | Time Complexity — сложность по времени |
| **SC** | Space Complexity — сложность по памяти |
| **Pattern** | Типовой подход к решению класса задач |

---

## Почему паттерны, а не задачи

```
Случайное решение:
500 задач × 30 мин = 250 часов
Результат: плохой recall под стрессом

Паттерны:
12 паттернов × 10 задач = 120 задач × 30 мин = 60 часов
Результат: любая задача → знакомый паттерн
```

Интервьюер не ожидает, что ты видел эту задачу. Он ожидает, что ты распознаешь паттерн и применишь правильный алгоритм.

---

## 12 ключевых паттернов

### 1. Two Pointers

**Когда применять:** Отсортированный массив, поиск пары, палиндромы

```kotlin
// Пример: Есть ли пара с суммой target в sorted array?
fun twoSum(nums: IntArray, target: Int): Boolean {
    var left = 0
    var right = nums.lastIndex

    while (left < right) {
        val sum = nums[left] + nums[right]
        when {
            sum == target -> return true
            sum < target -> left++
            else -> right--
        }
    }
    return false
}
// TC: O(n), SC: O(1)
```

**Типичные задачи:** Two Sum II, 3Sum, Container With Most Water

---

### 2. Sliding Window

**Когда применять:** Подстрока/подмассив с условием, фиксированный или динамический размер окна

```kotlin
// Пример: Максимальная сумма подмассива длины k
fun maxSumSubarray(nums: IntArray, k: Int): Int {
    var windowSum = nums.take(k).sum()
    var maxSum = windowSum

    for (i in k until nums.size) {
        windowSum += nums[i] - nums[i - k]  // slide window
        maxSum = maxOf(maxSum, windowSum)
    }
    return maxSum
}
// TC: O(n), SC: O(1)
```

**Типичные задачи:** Longest Substring Without Repeating Characters, Minimum Window Substring

---

### 3. Fast & Slow Pointers

**Когда применять:** Циклы в linked list, середина списка

```kotlin
// Пример: Есть ли цикл в linked list?
fun hasCycle(head: ListNode?): Boolean {
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next
        if (slow == fast) return true
    }
    return false
}
// TC: O(n), SC: O(1)
```

**Типичные задачи:** Linked List Cycle, Find Middle of Linked List, Happy Number

---

### 4. Binary Search

**Когда применять:** Отсортированные данные, поиск границы, минимизация/максимизация

```kotlin
// Пример: Поиск в rotated sorted array
fun search(nums: IntArray, target: Int): Int {
    var left = 0
    var right = nums.lastIndex

    while (left <= right) {
        val mid = left + (right - left) / 2
        if (nums[mid] == target) return mid

        // Определяем, какая половина отсортирована
        if (nums[left] <= nums[mid]) {
            if (target in nums[left] until nums[mid]) right = mid - 1
            else left = mid + 1
        } else {
            if (target in (nums[mid] + 1)..nums[right]) left = mid + 1
            else right = mid - 1
        }
    }
    return -1
}
// TC: O(log n), SC: O(1)
```

**Типичные задачи:** Search in Rotated Array, Find Peak Element, Koko Eating Bananas

---

### 5. DFS (Depth-First Search)

**Когда применять:** Деревья, графы, все пути, backtracking

```kotlin
// Пример: Все пути от root до leaf
fun binaryTreePaths(root: TreeNode?): List<String> {
    val result = mutableListOf<String>()

    fun dfs(node: TreeNode?, path: String) {
        if (node == null) return

        val newPath = if (path.isEmpty()) "${node.`val`}"
                      else "$path->${node.`val`}"

        if (node.left == null && node.right == null) {
            result.add(newPath)
            return
        }

        dfs(node.left, newPath)
        dfs(node.right, newPath)
    }

    dfs(root, "")
    return result
}
// TC: O(n), SC: O(h) где h — высота дерева
```

**Типичные задачи:** Path Sum, Number of Islands, Clone Graph

---

### 6. BFS (Breadth-First Search)

**Когда применять:** Кратчайший путь, уровни дерева, графы без весов

```kotlin
// Пример: Level order traversal
fun levelOrder(root: TreeNode?): List<List<Int>> {
    if (root == null) return emptyList()

    val result = mutableListOf<List<Int>>()
    val queue = ArrayDeque<TreeNode>()
    queue.add(root)

    while (queue.isNotEmpty()) {
        val level = mutableListOf<Int>()
        repeat(queue.size) {
            val node = queue.removeFirst()
            level.add(node.`val`)
            node.left?.let { queue.add(it) }
            node.right?.let { queue.add(it) }
        }
        result.add(level)
    }
    return result
}
// TC: O(n), SC: O(n)
```

**Типичные задачи:** Binary Tree Level Order, Rotting Oranges, Word Ladder

---

### 7. Merge Intervals

**Когда применять:** Перекрывающиеся интервалы, расписания

```kotlin
// Пример: Объединить перекрывающиеся интервалы
fun merge(intervals: Array<IntArray>): Array<IntArray> {
    if (intervals.isEmpty()) return emptyArray()

    intervals.sortBy { it[0] }
    val result = mutableListOf(intervals[0])

    for (i in 1 until intervals.size) {
        val last = result.last()
        val current = intervals[i]

        if (current[0] <= last[1]) {
            last[1] = maxOf(last[1], current[1])
        } else {
            result.add(current)
        }
    }
    return result.toTypedArray()
}
// TC: O(n log n), SC: O(n)
```

**Типичные задачи:** Merge Intervals, Insert Interval, Meeting Rooms II

---

### 8. Monotonic Stack

**Когда применять:** Next Greater Element, температуры, гистограммы

```kotlin
// Пример: Next Greater Element
fun nextGreaterElements(nums: IntArray): IntArray {
    val result = IntArray(nums.size) { -1 }
    val stack = ArrayDeque<Int>()  // индексы

    for (i in nums.indices) {
        while (stack.isNotEmpty() && nums[stack.last()] < nums[i]) {
            result[stack.removeLast()] = nums[i]
        }
        stack.add(i)
    }
    return result
}
// TC: O(n), SC: O(n)
```

**Типичные задачи:** Daily Temperatures, Largest Rectangle in Histogram

---

### 9. Topological Sort

**Когда применять:** Зависимости, порядок выполнения, DAG

```kotlin
// Пример: Course Schedule (можно ли закончить все курсы?)
fun canFinish(numCourses: Int, prerequisites: Array<IntArray>): Boolean {
    val graph = Array(numCourses) { mutableListOf<Int>() }
    val inDegree = IntArray(numCourses)

    for ((course, prereq) in prerequisites) {
        graph[prereq].add(course)
        inDegree[course]++
    }

    val queue = ArrayDeque<Int>()
    for (i in 0 until numCourses) {
        if (inDegree[i] == 0) queue.add(i)
    }

    var completed = 0
    while (queue.isNotEmpty()) {
        val course = queue.removeFirst()
        completed++
        for (next in graph[course]) {
            if (--inDegree[next] == 0) queue.add(next)
        }
    }
    return completed == numCourses
}
// TC: O(V + E), SC: O(V + E)
```

**Типичные задачи:** Course Schedule I/II, Alien Dictionary

---

### 10. Union-Find

**Когда применять:** Группы, компоненты связности, "друзья друзей"

```kotlin
class UnionFind(n: Int) {
    private val parent = IntArray(n) { it }
    private val rank = IntArray(n) { 0 }

    fun find(x: Int): Int {
        if (parent[x] != x) parent[x] = find(parent[x])  // path compression
        return parent[x]
    }

    fun union(x: Int, y: Int): Boolean {
        val px = find(x)
        val py = find(y)
        if (px == py) return false

        // union by rank
        when {
            rank[px] < rank[py] -> parent[px] = py
            rank[px] > rank[py] -> parent[py] = px
            else -> { parent[py] = px; rank[px]++ }
        }
        return true
    }
}
// TC: O(α(n)) ≈ O(1) per operation
```

**Типичные задачи:** Number of Provinces, Redundant Connection, Accounts Merge

---

### 11. Backtracking

**Когда применять:** Все комбинации, перестановки, Sudoku

```kotlin
// Пример: Все подмножества
fun subsets(nums: IntArray): List<List<Int>> {
    val result = mutableListOf<List<Int>>()

    fun backtrack(start: Int, current: MutableList<Int>) {
        result.add(current.toList())

        for (i in start until nums.size) {
            current.add(nums[i])
            backtrack(i + 1, current)
            current.removeAt(current.lastIndex)  // undo
        }
    }

    backtrack(0, mutableListOf())
    return result
}
// TC: O(n * 2^n), SC: O(n)
```

**Типичные задачи:** Subsets, Permutations, Combination Sum, N-Queens

---

### 12. Dynamic Programming

**Когда применять:** Оптимизация, подсчёт способов, overlapping subproblems

```kotlin
// Пример: Climbing Stairs (сколько способов)
fun climbStairs(n: Int): Int {
    if (n <= 2) return n
    var prev2 = 1
    var prev1 = 2

    for (i in 3..n) {
        val current = prev1 + prev2
        prev2 = prev1
        prev1 = current
    }
    return prev1
}
// TC: O(n), SC: O(1)
```

**Типичные задачи:** Longest Common Subsequence, Coin Change, House Robber

---

## Структуры данных: приоритет

| Структура | Частота | Ключевые операции |
|-----------|---------|-------------------|
| **Array** | Очень высокая | Index, iterate, sort |
| **HashMap** | Очень высокая | O(1) lookup, frequency |
| **HashSet** | Высокая | O(1) contains, unique |
| **Stack** | Высокая | LIFO, parentheses |
| **Queue** | Средняя | FIFO, BFS |
| **Heap** | Средняя | Top-K, median |
| **Tree** | Высокая | Traversal, BST |
| **Graph** | Средняя | DFS, BFS, shortest path |

---

## Ожидаемая сложность по уровням

| Уровень | Сложность задачи | Время решения | TC ожидание |
|---------|------------------|---------------|-------------|
| Junior | Easy | 20-30 мин | Любой working |
| Mid | Easy-Medium | 25-35 мин | Optimal для Easy |
| **Senior** | **Medium** | **30-40 мин** | **Optimal или near-optimal** |
| Staff | Medium-Hard | 35-45 мин | Optimal + trade-offs |

---

## План подготовки

### 3 месяца (оптимально)

```
Месяц 1: Основы (60 задач)
├── Неделя 1-2: Arrays, Strings, HashMaps (20 задач)
├── Неделя 3-4: Two Pointers, Sliding Window (20 задач)
└── Неделя 5-6: Binary Search, Sorting (20 задач)

Месяц 2: Деревья и графы (50 задач)
├── Неделя 1-2: Trees, DFS, BFS (25 задач)
└── Неделя 3-4: Graphs, Topological Sort (25 задач)

Месяц 3: Продвинутое + практика (40 задач)
├── Неделя 1-2: DP, Backtracking (20 задач)
├── Неделя 3: Heap, Stack patterns (10 задач)
└── Неделя 4: Mock interviews, review (10 задач)

Итого: 150 задач за 12 недель = ~2 задачи в день
```

### 1 месяц (интенсив)

```
NeetCode 150 или Blind 75

Неделя 1: Arrays, Hashing, Two Pointers (20 задач)
Неделя 2: Sliding Window, Stack, Binary Search (18 задач)
Неделя 3: Trees, Tries, Graphs (20 задач)
Неделя 4: DP, Greedy, Intervals (17 задач)

Темп: 3-4 задачи в день
```

---

## Как решать на интервью

### Структура ответа (45 минут)

```
0-5 мин:    Понять задачу, уточнить constraints
5-10 мин:   Проговорить approach, обсудить complexity
10-35 мин:  Написать код, комментируя
35-40 мин:  Протестировать на примерах
40-45 мин:  Обсудить оптимизации, edge cases
```

### Что говорить вслух

```
1. "Let me make sure I understand..."
   → Перефразируй задачу

2. "For the brute force, I would..."
   → Покажи, что понимаешь простое решение

3. "But we can optimize by using..."
   → Объясни паттерн

4. "The time complexity would be O(n) because..."
   → Обоснуй

5. "Let me trace through with example [1,2,3]..."
   → Протестируй
```

---

## Частые ошибки

```
❌ Сразу писать код без clarification
   → Всегда уточни: input size, sorted?, duplicates?

❌ Молчать во время решения
   → Думай вслух, интервьюер оценивает процесс

❌ Игнорировать edge cases
   → Пустой input, один элемент, все одинаковые

❌ Не тестировать на примерах
   → Пройдись по коду с конкретными значениями

❌ Паниковать при stuck
   → Скажи "Let me step back and think about this"
```

---

## Ресурсы

| Ресурс | Для чего | Ссылка |
|--------|----------|--------|
| NeetCode 150 | Структурированный roadmap | neetcode.io |
| Blind 75 | Минимальный набор | teamblind.com |
| LeetCode Patterns | Паттерны по категориям | seanprashad.com/leetcode-patterns |
| AlgoExpert | Видео объяснения | algoexpert.io |

---

## Куда дальше

→ [[interview-process]] — общий процесс интервью
→ [[technical-interview]] — детали технического раунда
→ [[system-design-android]] — design round

---

## Источники

- [Sean Prashad's LeetCode Patterns](https://seanprashad.com/leetcode-patterns/)
- [NeetCode](https://neetcode.io)
- [Design Gurus: Top LeetCode Patterns](https://www.designgurus.io/blog/top-lc-patterns)
- [Tech Interview Handbook](https://www.techinterviewhandbook.org)

---

*Обновлено: 2025-12-26*

---

*Проверено: 2026-01-09*
