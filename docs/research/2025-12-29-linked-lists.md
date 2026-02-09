---
title: "Research Report: Linked Lists"
created: 2025-12-29
modified: 2025-12-29
type: concept
status: draft
tags:
  - topic/cs-fundamentals
  - topic/data-structures
---

# Research Report: Linked Lists

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Linked List — линейная структура данных с элементами в узлах, связанных указателями. Три типа: Singly (next), Doubly (prev+next), Circular (замкнутый). Преимущества над массивом: O(1) вставка/удаление в начале, динамический размер. Недостатки: O(n) доступ, overhead памяти на указатели. Ключевые техники для интервью: Fast/Slow pointers (Floyd's), Dummy/Sentinel nodes, In-place reversal.

---

## Key Findings

### 1. Types of Linked Lists

| Type | Structure | Use Case |
|------|-----------|----------|
| **Singly** | node → next | Stack, basic list operations |
| **Doubly** | prev ← node → next | Browser history, LRU cache |
| **Circular Singly** | last → first | Round-robin scheduling |
| **Circular Doubly** | prev ↔ next (ring) | Circular buffers, playlists |

### 2. Time Complexity Comparison

| Operation | Array | Linked List |
|-----------|-------|-------------|
| Access by index | O(1) | O(n) |
| Search | O(n) | O(n) |
| Insert at beginning | O(n) | O(1) |
| Insert at end | O(1)* | O(1)** |
| Insert at middle | O(n) | O(1)*** |
| Delete at beginning | O(n) | O(1) |
| Delete at end | O(1) | O(n) / O(1)**** |

*Amortized | **With tail pointer | ***After reaching position | ****O(1) for doubly

### 3. When to Use Linked List vs Array

**Use Linked List when:**
- Frequent insertions/deletions at beginning
- Unknown or dynamic size
- Implementing Stack, Queue, Deque
- Memory fragmentation acceptable

**Use Array when:**
- Random access needed
- Cache performance critical
- Memory efficiency important
- Size known in advance

### 4. Fast and Slow Pointers (Floyd's Algorithm)

**Technique:** Slow moves 1 step, fast moves 2 steps.

**Applications:**
1. **Cycle Detection** — if meet, cycle exists
2. **Find Middle** — when fast reaches end, slow is at middle
3. **Find Cycle Start** — after meeting, reset one to head, move both by 1
4. **Nth from End** — fast starts N ahead, when fast ends, slow is at Nth

### 5. Dummy/Sentinel Node Technique

**Benefits:**
- Eliminates edge cases (empty list, head operations)
- Uniform handling of all nodes
- Cleaner, less error-prone code
- Especially useful for: delete, merge, partition operations

**Pattern:**
```
dummy → node1 → node2 → ... → null
  ↑
result = dummy.next
```

### 6. In-Place Reversal

**Iterative (O(1) space):**
- Three pointers: prev, curr, next
- Reverse links one by one

**Recursive (O(n) space):**
- Base case: head is null or single node
- Recursive call on rest, adjust pointers on return

### 7. Common Interview Problems

| Problem | Technique | Complexity |
|---------|-----------|------------|
| Reverse List | In-place reversal | O(n) / O(1) |
| Detect Cycle | Fast/Slow | O(n) / O(1) |
| Find Middle | Fast/Slow | O(n) / O(1) |
| Merge Two Sorted | Dummy node | O(n+m) / O(1) |
| Merge K Sorted | Divide & Conquer / Heap | O(N log k) |
| Remove Nth from End | Two pointers with gap | O(n) / O(1) |
| Palindrome Check | Fast/Slow + Reverse half | O(n) / O(1) |
| Intersection Point | Length difference / Two pointers | O(n+m) / O(1) |

### 8. Corner Cases

- Empty list (null head)
- Single node
- Two nodes
- Cycle present
- Operations on head/tail
- Duplicate values

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Tech Interview Handbook - Linked List](https://www.techinterviewhandbook.org/algorithms/linked-list/) | Guide | 0.95 |
| 2 | [GeeksforGeeks - Two-Pointer Technique](https://www.geeksforgeeks.org/dsa/two-pointer-technique-in-a-linked-list/) | Tutorial | 0.90 |
| 3 | [AlgoCademy - Fast and Slow Pointers](https://algocademy.com/blog/fast-and-slow-pointers-a-powerful-technique-for-solving-linked-list-problems/) | Tutorial | 0.90 |
| 4 | [GeeksforGeeks - Linked List vs Array](https://www.geeksforgeeks.org/dsa/linked-list-vs-array/) | Comparison | 0.90 |
| 5 | [Wikipedia - Linked List](https://en.wikipedia.org/wiki/Linked_list) | Reference | 0.95 |
| 6 | [GeeksforGeeks - Reverse Linked List](https://www.geeksforgeeks.org/dsa/reverse-a-linked-list/) | Tutorial | 0.90 |
| 7 | [GeeksforGeeks - Merge K Sorted Lists](https://www.geeksforgeeks.org/dsa/merge-k-sorted-linked-lists/) | Tutorial | 0.90 |

---

*Generated: 2025-12-29*
