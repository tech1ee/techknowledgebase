---
title: "Research Report: Big O Notation & Complexity Analysis"
created: 2025-12-29
modified: 2025-12-29
type: concept
status: draft
tags:
  - topic/cs-fundamentals
  - topic/algorithms
---

# Research Report: Big O Notation & Complexity Analysis

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Big O notation — математический инструмент для описания верхней границы роста функции. В computer science используется для анализа временной и пространственной сложности алгоритмов. Формальное определение: f(n) = O(g(n)) если существуют константы c > 0 и k ≥ 0 такие, что f(n) ≤ c·g(n) для всех n ≥ k. Ключевое понимание: Big O описывает КАК алгоритм масштабируется, а не точное время выполнения.

---

## Key Findings

### 1. Formal Mathematical Definition

**Big O (Upper Bound):**
f(n) = O(g(n)) ⟺ ∃c > 0, ∃k ≥ 0: |f(n)| ≤ c·|g(n)| ∀n ≥ k

**Big Omega (Lower Bound):**
f(n) = Ω(g(n)) ⟺ ∃c > 0, ∃k ≥ 0: f(n) ≥ c·g(n) ∀n ≥ k

**Big Theta (Tight Bound):**
f(n) = Θ(g(n)) ⟺ f(n) = O(g(n)) AND f(n) = Ω(g(n))

### 2. Three Notations Comparison

| Notation | Bound Type | Use Case | Example |
|----------|------------|----------|---------|
| O (Big O) | Upper (worst) | Most common | Linear search O(n) |
| Ω (Omega) | Lower (best) | Theoretical | Binary search Ω(1) |
| Θ (Theta) | Tight (exact) | When both bounds equal | Merge sort Θ(n log n) |

### 3. Common Time Complexities

| Complexity | Name | Example | n=1000 |
|------------|------|---------|--------|
| O(1) | Constant | Array access | 1 |
| O(log n) | Logarithmic | Binary search | 10 |
| O(n) | Linear | Linear search | 1,000 |
| O(n log n) | Linearithmic | Merge sort | 10,000 |
| O(n²) | Quadratic | Bubble sort | 1,000,000 |
| O(2^n) | Exponential | Fibonacci naive | 10^301 |
| O(n!) | Factorial | Permutations | ∞ |

### 4. Amortized Analysis

**Definition:** Average cost per operation over a sequence of operations.

**Classic Example: Dynamic Array (ArrayList)**
- Single append: O(1) average, O(n) worst (when resize needed)
- Amortized append: O(1) because expensive resizes are rare
- Proof: m appends cost m (appends) + 2m (copies) = 3m → 3 per operation

**Three Methods:**
1. Aggregate Method — total cost / number of operations
2. Accounting Method — pay "credits" ahead of expensive operations
3. Potential Method — track "potential energy" of data structure

### 5. Master Theorem

For recurrences T(n) = aT(n/b) + f(n):

**Case 1:** If f(n) = O(n^(log_b(a) - ε)), then T(n) = Θ(n^(log_b(a)))
**Case 2:** If f(n) = Θ(n^(log_b(a))), then T(n) = Θ(n^(log_b(a)) · log n)
**Case 3:** If f(n) = Ω(n^(log_b(a) + ε)), then T(n) = Θ(f(n))

**Examples:**
- Merge Sort: T(n) = 2T(n/2) + O(n) → Case 2 → O(n log n)
- Binary Search: T(n) = T(n/2) + O(1) → Case 2 → O(log n)

### 6. Rules for Calculating Big O

1. **Drop Constants:** O(2n) = O(n)
2. **Drop Lower Terms:** O(n² + n) = O(n²)
3. **Different Inputs:** O(a + b), not O(n)
4. **Nested Loops:** Multiply → O(n × m)
5. **Sequential Operations:** Add → O(n + m)

### 7. Data Structure Complexities

| Structure | Access | Search | Insert | Delete |
|-----------|--------|--------|--------|--------|
| Array | O(1) | O(n) | O(n) | O(n) |
| LinkedList | O(n) | O(n) | O(1) | O(1) |
| Stack/Queue | O(n) | O(n) | O(1) | O(1) |
| HashMap | N/A | O(1)* | O(1)* | O(1)* |
| BST | O(log n)* | O(log n)* | O(log n)* | O(log n)* |
| AVL/RB Tree | O(log n) | O(log n) | O(log n) | O(log n) |

*average case, worst case may differ

### 8. Sorting Algorithm Complexities

| Algorithm | Best | Average | Worst | Space | Stable |
|-----------|------|---------|-------|-------|--------|
| Quick Sort | O(n log n) | O(n log n) | O(n²) | O(log n) | No |
| Merge Sort | O(n log n) | O(n log n) | O(n log n) | O(n) | Yes |
| Heap Sort | O(n log n) | O(n log n) | O(n log n) | O(1) | No |
| Tim Sort | O(n) | O(n log n) | O(n log n) | O(n) | Yes |
| Insertion Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |
| Bubble Sort | O(n) | O(n²) | O(n²) | O(1) | Yes |

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Wikipedia - Big O notation](https://en.wikipedia.org/wiki/Big_O_notation) | Reference | 0.95 |
| 2 | [GeeksforGeeks Big O Tutorial](https://www.geeksforgeeks.org/dsa/analysis-algorithms-big-o-analysis/) | Tutorial | 0.90 |
| 3 | [bigocheatsheet.com](https://www.bigocheatsheet.com/) | Cheat Sheet | 0.90 |
| 4 | [Interview Cake - Big O](https://www.interviewcake.com/article/java/big-o-notation-time-and-space-complexity) | Tutorial | 0.90 |
| 5 | [MIT Big O PDF](https://web.mit.edu/16.070/www/lecture/big_o.pdf) | Academic | 0.95 |
| 6 | [Mathematics LibreTexts](https://math.libretexts.org/) | Academic | 0.95 |
| 7 | [Stanford CS161 Lecture](https://web.stanford.edu/class/archive/cs/cs161/cs161.1168/lecture3.pdf) | Academic | 0.95 |
| 8 | [CMU Amortized Analysis](https://www.cs.cmu.edu/~15451-f22/lectures/lec03-amortized.pdf) | Academic | 0.95 |
| 9 | [Programiz Master Theorem](https://www.programiz.com/dsa/master-theorem) | Tutorial | 0.85 |
| 10 | [Cornell Amortized Analysis](https://www.cs.cornell.edu/courses/cs3110/2011sp/Lectures/lec20-amortized/amortized.htm) | Academic | 0.95 |

---

*Generated: 2025-12-29*
