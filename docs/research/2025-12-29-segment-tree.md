# Research Report: Segment Tree (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Segment Tree — структура для range queries и point updates за O(log n). **Lazy propagation** позволяет range updates за O(log n). Используется для sum, min, max, GCD на отрезках. Требует 4n памяти.

## Key Insights

> "Each query has the complexity O(log n), which is small enough for most use-cases (e.g., log₂ 10⁹ ≈ 30)." — [CP-Algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)

> "Lazy propagation: Don't update a node until needed. Range updates in O(log n) instead of O(n log n)." — [HackerEarth](https://www.hackerearth.com/practice/notes/segment-tree-and-lazy-propagation/)

> "Before traversing to a child vertex, we call push and propagate the value to both children." — [CP-Algorithms](https://cp-algorithms.com/data_structures/segment_tree.html)

## Operations

| Operation | Without Lazy | With Lazy |
|-----------|--------------|-----------|
| Build | O(n) | O(n) |
| Point Update | O(log n) | O(log n) |
| Range Update | O(n log n) | O(log n) |
| Range Query | O(log n) | O(log n) |
| Space | O(4n) | O(4n) |

## Lazy Propagation Steps

1. Store pending updates in lazy[] array
2. Before query/update, push pending values to children
3. Mark children as lazy
4. Clear current node's lazy flag

## Applications

- Range sum/min/max queries
- Range add/set updates
- Counting inversions
- 2D range queries
- Merge sort tree

## Sources

| # | Source | Type | Key Contribution |
|---|--------|------|------------------|
| 1 | [CP-Algorithms](https://cp-algorithms.com/data_structures/segment_tree.html) | Reference | Complete guide |
| 2 | [Codeforces](https://codeforces.com/blog/entry/18051) | Blog | Efficient impl |
| 3 | [AlgoCademy](https://algocademy.com/blog/mastering-segment-trees-a-comprehensive-guide-for-coding-interviews/) | Guide | Interview prep |
| 4 | [HackerEarth](https://www.hackerearth.com/practice/notes/segment-tree-and-lazy-propagation/) | Tutorial | Lazy propagation |
