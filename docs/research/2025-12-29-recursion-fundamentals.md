# Research Report: Recursion Fundamentals

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Рекурсия — техника программирования, где функция вызывает саму себя для решения подзадач. Ключевые компоненты: base case (условие остановки) и recursive case (вызов себя). Call stack хранит контекст каждого вызова. Tail recursion позволяет компилятору оптимизировать рекурсию до итерации. Memoization превращает экспоненциальную сложность в линейную, связывая рекурсию с Dynamic Programming.

---

## Key Findings

### 1. Core Components of Recursion

**Base Case:**
- Условие остановки рекурсии
- Без base case → infinite recursion → stack overflow
- Количество base cases должно соответствовать глубине recursive calls

**Recursive Case:**
- Разбивает задачу на меньшие подзадачи
- Вызывает функцию с изменёнными параметрами
- Должен приближаться к base case

### 2. Call Stack Mechanics

```
LIFO (Last-In-First-Out):

factorial(4) вызывает:
  factorial(3) вызывает:
    factorial(2) вызывает:
      factorial(1) возвращает 1
    возвращает 2 * 1 = 2
  возвращает 3 * 2 = 6
возвращает 4 * 6 = 24
```

- Каждый вызов создаёт stack frame
- Stack frame содержит: return address, arguments, local variables
- Stack растёт вниз до base case, затем "раскручивается" обратно

### 3. Types of Recursion

| Type | Description | Example |
|------|-------------|---------|
| Linear | Один recursive call | Factorial |
| Binary | Два recursive calls | Fibonacci, Tree traversal |
| Tail | Recursive call последний | Optimized factorial |
| Mutual | Функции вызывают друг друга | isEven/isOdd |

### 4. Tail Recursion Optimization (TCO)

**Как работает:**
- Compiler заменяет `call + ret` на `jmp`
- Stack frame переиспользуется вместо создания нового
- Рекурсия превращается в цикл

**Поддержка компиляторами:**
- GCC, Clang, Intel: `-foptimize-sibling-calls`
- Scala, Kotlin: `tailrec` keyword
- Python, Java: НЕ поддерживают TCO
- JavaScript: Поддержка в ES6, но не во всех браузерах

### 5. Memoization & Dynamic Programming Connection

```
СВЯЗЬ:

Recursion (naive)
    ↓ добавляем кэширование
Recursion + Memoization = Top-Down DP
    ↓ переписываем итеративно
Bottom-Up DP (табуляция)
```

**Fibonacci пример:**
- Naive recursion: O(2^n) time, O(n) space
- With memoization: O(n) time, O(n) space
- Bottom-up DP: O(n) time, O(1) space possible

### 6. Time & Space Complexity Analysis

**Time Complexity:**
- Зависит от количества вызовов × работа на вызов
- Recurrence relation: T(n) = aT(n/b) + O(n^k)
- Master theorem для divide-and-conquer

**Space Complexity:**
- Определяется максимальной глубиной стека
- Вызовы не одновременны → space = max depth
- Fibonacci: O(n) space несмотря на 2 вызова

### 7. Common Recursion Patterns

| Pattern | Use Case | Examples |
|---------|----------|----------|
| Divide & Conquer | Split, solve, combine | Merge Sort, Quick Sort |
| Tree Traversal | Process all nodes | In-order, Pre-order, Post-order |
| Backtracking | Generate all solutions | Permutations, N-Queens |
| Memoized | Overlapping subproblems | Fibonacci, Coin Change |

### 8. Preventing Stack Overflow

1. **Proper base case** — обязательно
2. **Tail recursion** — если язык поддерживает
3. **Limit depth** — параметр для отслеживания глубины
4. **Memoization** — уменьшает количество вызовов
5. **Convert to iteration** — explicit stack

### 9. Recursion vs Iteration

| Aspect | Recursion | Iteration |
|--------|-----------|-----------|
| Speed | Slower (overhead) | Faster |
| Memory | O(n) stack | O(1) possible |
| Readability | Often cleaner | Can be complex |
| Best for | Trees, graphs, D&C | Simple loops |
| Risk | Stack overflow | Infinite loop |

**Исключение:** Recursive exponentiation может быть быстрее итеративного (23 операции vs 1000 для 3^1000).

### 10. Interview Tips

**Must-know problems:**
- Factorial, Fibonacci
- Tree traversals (in-order, pre-order, post-order)
- Binary search
- Merge sort
- Generate parentheses
- Subsets, Permutations, Combinations

**Corner cases:**
- n = 0
- n = 1
- Large n (stack overflow risk)
- Empty input

---

## Community Sentiment

### Positive
- "Recursion makes tree problems intuitive"
- "Memoization is the key to understanding DP"
- "Visualization tools (VisuAlgo) help tremendously"

### Negative / Concerns
- "Stack overflow in production is dangerous"
- "Python's 1000 limit is frustrating"
- "TCO support is inconsistent across languages"

### Neutral
- "Choice between recursion and iteration depends on problem"
- "Always consider converting to iteration for performance-critical code"

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Tech Interview Handbook - Recursion](https://www.techinterviewhandbook.org/algorithms/recursion/) | Guide | 0.95 |
| 2 | [VisuAlgo - Recursion Tree](https://visualgo.net/en/recursion) | Tool | 0.90 |
| 3 | [Launch School - Call Stack](https://launchschool.com/books/advanced_dsa/read/exploring_call_stack) | Tutorial | 0.90 |
| 4 | [Wikipedia - Tail Call](https://en.wikipedia.org/wiki/Tail_call) | Reference | 0.95 |
| 5 | [GeeksforGeeks - Tail Recursion](https://www.geeksforgeeks.org/dsa/tail-recursion/) | Tutorial | 0.85 |
| 6 | [Interview Cake - Memoization](https://www.interviewcake.com/concept/java/memoization) | Guide | 0.90 |
| 7 | [AlgoCademy - Recursive vs Iterative](https://algocademy.com/blog/recursive-vs-iterative-algorithms-pros-and-cons/) | Article | 0.85 |
| 8 | [YourBasic - Master Theorem](https://yourbasic.org/algorithms/time-complexity-recursive-functions/) | Tutorial | 0.85 |
| 9 | [QuanticDev - Recursion Visualization](https://quanticdev.com/algorithms/primitives/recursion-visualization/) | Tool | 0.85 |
| 10 | [EnjoyAlgorithms - Time Complexity](https://www.enjoyalgorithms.com/blog/time-complexity-analysis-of-recursion-in-programming/) | Tutorial | 0.85 |

---

*Generated: 2025-12-29*
