---
title: "Research Report: Arrays & Strings Data Structures"
created: 2025-12-29
modified: 2025-12-29
type: concept
status: draft
tags:
  - topic/cs-fundamentals
  - topic/data-structures
---

# Research Report: Arrays & Strings Data Structures

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Arrays и Strings — самые частые структуры данных на интервью. Array хранит элементы в contiguous memory с O(1) доступом по индексу. String в большинстве языков immutable. Ключевые техники: Two Pointers (O(n) вместо O(n²)), Sliding Window (subarray/substring проблемы), In-place modification. Mastery этих структур критичен для успеха на интервью.

---

## Key Findings

### 1. Array Fundamentals

**Time Complexity:**
| Operation | Complexity |
|-----------|------------|
| Access by index | O(1) |
| Search (unsorted) | O(n) |
| Search (sorted) | O(log n) |
| Insert/Delete (middle) | O(n) |
| Insert/Delete (end) | O(1) amortized |

**Static vs Dynamic:**
- Static: fixed size, contiguous memory
- Dynamic: grows automatically (doubling strategy)
- ArrayList (Java), List (Python), MutableList (Kotlin)

### 2. String Immutability

| Language | String Mutable? | Mutable Alternative |
|----------|-----------------|---------------------|
| Java | No | StringBuilder, StringBuffer |
| Kotlin | No | StringBuilder |
| Python | No | list of chars, join() |
| JavaScript | No | Array methods |
| C/C++ | Yes (char[]) | std::string |

**Performance:**
- String concatenation в loop = O(n²)
- StringBuilder = O(n)
- Всегда использовать StringBuilder для частых модификаций

### 3. Two Pointers Technique

**Patterns:**
1. Opposite direction (start + end → middle)
2. Same direction (slow + fast)
3. Two arrays (one pointer per array)

**When to use:**
- Sorted array problems
- Palindrome checking
- Finding pairs with sum
- In-place operations

**Complexity:** O(n) instead of O(n²)

### 4. Sliding Window Technique

**Types:**
1. Fixed size window (e.g., max sum of k elements)
2. Variable size window (e.g., minimum subarray with sum >= target)

**Template:**
```
left = 0
for right in range(len(arr)):
    # expand window
    while (window invalid):
        # shrink from left
        left += 1
    # update answer
```

**When sliding window doesn't work:**
- When adding element can increase OR decrease state
- Subarray sum with negative numbers (use HashMap instead)

### 5. Array Interview Techniques

1. **Precomputation:** Prefix/suffix sums
2. **Array as Hash Table:** Use array index as key
3. **In-place modification:** Save space
4. **Multiple passes:** Still O(n)
5. **Sort first:** If order doesn't matter

### 6. String Algorithms

**Pattern Matching:**
| Algorithm | Time | Use Case |
|-----------|------|----------|
| Naive | O(n×m) | Simple cases |
| KMP | O(n+m) | Optimal single pattern |
| Rabin-Karp | O(n+m) avg | Multiple patterns |
| Boyer-Moore | O(n/m) best | Long patterns |

**Anagram Detection:**
- Sort and compare: O(n log n)
- Frequency count: O(n)
- Prime multiplication: O(n), O(1) space

### 7. Corner Cases

**Array:**
- Empty array
- Single element
- All duplicates
- Negative numbers
- Integer overflow on sum

**String:**
- Empty string
- Single character
- All same characters
- Unicode / special characters
- Case sensitivity

### 8. Common Problems by Pattern

**Two Pointers:**
- Two Sum II (sorted)
- 3Sum
- Container With Most Water
- Remove Duplicates

**Sliding Window:**
- Maximum Subarray
- Longest Substring Without Repeating
- Minimum Size Subarray Sum

**In-place:**
- Rotate Array
- Move Zeros
- Dutch National Flag

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Tech Interview Handbook - Array](https://www.techinterviewhandbook.org/algorithms/array/) | Guide | 0.95 |
| 2 | [Tech Interview Handbook - String](https://www.techinterviewhandbook.org/algorithms/string/) | Guide | 0.95 |
| 3 | [GeeksforGeeks - Two Pointers](https://www.geeksforgeeks.org/dsa/two-pointers-technique/) | Tutorial | 0.90 |
| 4 | [GeeksforGeeks - Sliding Window](https://www.geeksforgeeks.org/dsa/window-sliding-technique/) | Tutorial | 0.90 |
| 5 | [Interview Cake - Array](https://www.interviewcake.com/concept/java/array) | Guide | 0.90 |
| 6 | [USACO Guide - Two Pointers](https://usaco.guide/silver/two-pointers) | Tutorial | 0.90 |
| 7 | [Labuladong - Sliding Window](https://labuladong.online/algo/en/essential-technique/sliding-window-framework/) | Template | 0.85 |
| 8 | [DigitalOcean - String vs StringBuilder](https://www.digitalocean.com/community/tutorials/string-vs-stringbuffer-vs-stringbuilder) | Tutorial | 0.85 |

---

*Generated: 2025-12-29*
