---
title: "Research Report: Stacks & Queues"
created: 2025-12-29
modified: 2025-12-29
type: concept
status: draft
tags:
  - topic/cs-fundamentals
  - topic/data-structures
---

# Research Report: Stacks & Queues

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Stack (LIFO) и Queue (FIFO) — базовые структуры данных с O(1) операциями push/pop и enqueue/dequeue. Stack: function calls, undo, DFS, expression evaluation. Queue: BFS, task scheduling, buffers. Monotonic Stack — мощный паттерн для "next greater/smaller" задач, превращает O(n²) в O(n). Deque — двусторонняя очередь для sliding window maximum. Priority Queue — на основе heap для Dijkstra, Top-K.

---

## Key Findings

### 1. Stack vs Queue

| Feature | Stack (LIFO) | Queue (FIFO) |
|---------|--------------|--------------|
| Principle | Last In, First Out | First In, First Out |
| Insert | Push (top) | Enqueue (rear) |
| Remove | Pop (top) | Dequeue (front) |
| Use Cases | Undo, DFS, call stack | BFS, scheduling, buffers |
| Analogy | Стопка тарелок | Очередь в магазине |

### 2. Time Complexity

| Operation | Stack | Queue | Deque | Priority Queue |
|-----------|-------|-------|-------|----------------|
| Push/Enqueue | O(1) | O(1) | O(1) | O(log n) |
| Pop/Dequeue | O(1) | O(1) | O(1) | O(log n) |
| Peek | O(1) | O(1) | O(1) | O(1) |
| Search | O(n) | O(n) | O(n) | O(n) |

### 3. Monotonic Stack Pattern

**Типы:**
- Monotonic Decreasing: next greater element
- Monotonic Increasing: next smaller element

**Применения:**
- Next Greater Element
- Daily Temperatures
- Largest Rectangle in Histogram
- Stock Span Problem
- Trapping Rain Water

**Complexity:** O(n) time, O(n) space

### 4. Classic Interview Problems

| Problem | Pattern | Structure |
|---------|---------|-----------|
| Valid Parentheses | Matching | Stack |
| Min Stack | Design | Stack + auxiliary |
| Implement Queue using Stacks | Design | Two stacks |
| Implement Stack using Queues | Design | One/Two queues |
| Next Greater Element | Monotonic | Stack |
| Largest Rectangle | Monotonic | Stack |
| Sliding Window Maximum | Monotonic | Deque |
| Daily Temperatures | Monotonic | Stack |

### 5. Implementation Approaches

**Queue using Two Stacks:**
- Stack1 для push, Stack2 для pop
- Lazy transfer: перемещаем из Stack1 в Stack2 только когда Stack2 пуст
- Amortized O(1) для всех операций

**Stack using One Queue:**
- После каждого push, ротируем очередь
- Новый элемент оказывается в начале
- Push O(n), Pop O(1)

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Tech Interview Handbook - Stack](https://www.techinterviewhandbook.org/algorithms/stack/) | Guide | 0.95 |
| 2 | [Hello Interview - Monotonic Stack](https://www.hellointerview.com/learn/code/stack/monotonic-stack) | Tutorial | 0.90 |
| 3 | [Labuladong - Monotonic Stack Template](https://labuladong.online/algo/en/data-structure/monotonic-stack/) | Template | 0.90 |
| 4 | [GeeksforGeeks - Stack vs Queue](https://www.geeksforgeeks.org/dsa/difference-between-stack-and-queue-data-structures/) | Comparison | 0.90 |
| 5 | [Wikipedia - Deque](https://en.wikipedia.org/wiki/Double-ended_queue) | Reference | 0.95 |
| 6 | [LeetCode - Implement Queue using Stacks](https://leetcode.com/problems/implement-queue-using-stacks/) | Problem | 0.95 |

---

*Generated: 2025-12-29*
