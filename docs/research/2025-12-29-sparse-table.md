---
title: "Research Report: Sparse Table"
created: 2025-12-29
modified: 2025-12-29
type: concept
status: draft
tags:
  - topic/cs-fundamentals
  - topic/data-structures
---

# Research Report: Sparse Table (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Sparse Table — структура для **статических** Range Minimum Query за O(1). Preprocessing O(n log n), space O(n log n). Работает для idempotent операций (min, max, GCD). Для sum нужен segment tree.

## Key Insights

> "Sparse Tables enable O(1) queries after O(n log n) preprocessing." — [Brilliant](https://brilliant.org/wiki/sparse-table/)

> "The name 'Sparse' comes from storing O(n log n) ranges instead of O(n²)." — [Baeldung](https://www.baeldung.com/cs/sparse-tables)

> "For RMQ, we split range into two overlapping power-of-two ranges. Since min is idempotent, overlap doesn't matter." — [AlgoTree](https://www.algotree.org/algorithms/sparse_table/)

## Operations

| Operation | Complexity |
|-----------|------------|
| Build | O(n log n) |
| Query (idempotent) | O(1) |
| Query (non-idempotent) | O(log n) |
| Space | O(n log n) |
| Updates | Not supported |

## Build Recurrence

```
st[0][i] = arr[i]
st[k][i] = f(st[k-1][i], st[k-1][i + 2^(k-1)])
```

## O(1) Query (RMQ)

```
k = floor(log2(r - l + 1))
answer = min(st[k][l], st[k][r - 2^k + 1])
```

## Sparse Table vs Others

| Feature | Sparse Table | Segment Tree | Fenwick |
|---------|--------------|--------------|---------|
| Query | O(1) | O(log n) | O(log n) |
| Build | O(n log n) | O(n) | O(n) |
| Update | ❌ | O(log n) | O(log n) |
| Space | O(n log n) | O(4n) | O(n) |
| Use case | Static RMQ | Dynamic | Prefix sums |

## Advanced: O(n) Build

```
Divide array into blocks of size log(n)
Build sparse table over block minimums
Within-block queries: precomputed for all 2^log(n) patterns
```

## Sources

| # | Source | Type | Key Contribution |
|---|--------|------|------------------|
| 1 | [Codeforces](https://codeforces.com/blog/entry/78931) | Blog | O(n) construction |
| 2 | [Brilliant](https://brilliant.org/wiki/sparse-table/) | Wiki | Theory |
| 3 | [Baeldung](https://www.baeldung.com/cs/sparse-tables) | Tutorial | Implementation |
| 4 | [AlgoTree](https://www.algotree.org/algorithms/sparse_table/) | Reference | Examples |
