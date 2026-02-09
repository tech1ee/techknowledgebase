# Research Report: Fenwick Tree / BIT (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Fenwick Tree (Binary Indexed Tree) — структура для prefix sum queries и point updates за O(log n). Проще segment tree, меньше памяти (n vs 4n), быстрее константы. Основан на LSB (least significant bit) арифметике.

## Key Insights

> "Binary indexed trees require less space and are very easy to implement (total code not more than 8-10 lines)." — [HackerEarth](https://www.hackerearth.com/practice/notes/binary-indexed-tree-or-fenwick-tree/)

> "Compared to segment tree, BIT is simpler, uses less memory, and has faster constant factors for point update / prefix sum." — [CP-Algorithms](https://cp-algorithms.com/data_structures/fenwick.html)

> "Range query [l,r] = sum(r) - sum(l-1)." — [LeetCode](https://leetcode.com/discuss/post/1093346/introduction-to-fenwick-treebinary-indexed-treebit/)

## Operations

| Operation | Complexity |
|-----------|------------|
| Build | O(n) or O(n log n) |
| Point Update | O(log n) |
| Prefix Sum | O(log n) |
| Range Sum | O(log n) |
| Space | O(n) |

## Key Formulas

```
LSB(i) = i & (-i)

Update: while i <= n: tree[i] += delta; i += LSB(i)
Query:  while i > 0: sum += tree[i]; i -= LSB(i)
```

## Fenwick vs Segment Tree

| Feature | Fenwick | Segment Tree |
|---------|---------|--------------|
| Space | O(n) | O(4n) |
| Code complexity | Simple | Complex |
| Range update | Tricky | With lazy prop |
| Non-commutative | No | Yes |
| 2D extension | Easy | Possible |

## Applications

- Prefix sums
- Inversion counting
- Dynamic order statistics
- 2D range sums

## Sources

| # | Source | Type | Key Contribution |
|---|--------|------|------------------|
| 1 | [CP-Algorithms](https://cp-algorithms.com/data_structures/fenwick.html) | Reference | Complete guide |
| 2 | [HackerEarth](https://www.hackerearth.com/practice/notes/binary-indexed-tree-or-fenwick-tree/) | Tutorial | Implementation |
| 3 | [AlgoCademy](https://algocademy.com/blog/mastering-fenwick-trees-binary-indexed-trees-for-efficient-range-queries/) | Guide | Interview prep |
| 4 | [Wikipedia](https://en.wikipedia.org/wiki/Fenwick_tree) | Reference | Theory |
