---
title: "Research Report: Union-Find Pattern"
created: 2025-12-29
modified: 2025-12-29
type: concept
status: draft
tags:
  - topic/cs-fundamentals
  - topic/algorithms
---

# Research Report: Union-Find Pattern (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Union-Find (Disjoint Set Union) tracks connected components with near-constant time operations. Two key optimizations: **path compression** (flatten tree during find) and **union by rank** (attach smaller tree under larger). Time: O(α(n)) amortized per operation.

## Key Insights

> "Path compression shortens paths for visited nodes. The visited nodes are attached directly to the representative." — [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/union-by-rank-and-path-compression-in-union-find-algorithm/)

> "Time complexity O(α(n)), Inverse Ackermann, nearly constant time, because of path compression and union by rank optimization." — [CP-Algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html)

> "Union-Find is commonly used to implement Kruskal's Algorithm for Minimum Spanning Tree." — [TutorialHorizon](https://tutorialhorizon.com/algorithms/disjoint-set-union-find-algorithm-union-by-rank-and-path-compression/)

## Core Operations

| Operation | Description | Complexity |
|-----------|-------------|------------|
| makeSet(x) | Create set with single element x | O(1) |
| find(x) | Find representative of x's set | O(α(n)) |
| union(x, y) | Merge sets containing x and y | O(α(n)) |

## Optimizations

### Path Compression
```
find(x):
  if parent[x] != x:
    parent[x] = find(parent[x])  // Point directly to root
  return parent[x]
```

### Union by Rank
```
union(x, y):
  rootX, rootY = find(x), find(y)
  if rank[rootX] < rank[rootY]:
    parent[rootX] = rootY
  else if rank[rootX] > rank[rootY]:
    parent[rootY] = rootX
  else:
    parent[rootY] = rootX
    rank[rootX]++
```

## LeetCode Problems
- 200. Number of Islands
- 547. Number of Provinces
- 684. Redundant Connection
- 721. Accounts Merge
- 1319. Number of Operations to Make Network Connected
- 128. Longest Consecutive Sequence
- 990. Satisfiability of Equality Equations

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/union-by-rank-and-path-compression-in-union-find-algorithm/) | Tutorial | 0.90 | Optimizations |
| 2 | [CP-Algorithms](https://cp-algorithms.com/data_structures/disjoint_set_union.html) | Reference | 0.95 | Formal analysis |
| 3 | [TakeUForward](https://takeuforward.org/data-structure/disjoint-set-union-by-rank-union-by-size-path-compression-g-46) | Tutorial | 0.85 | Video guide |
| 4 | [HackerEarth](https://www.hackerearth.com/practice/notes/disjoint-set-union-union-find/) | Tutorial | 0.85 | Practice problems |
| 5 | [Medium](https://medium.com/@harshits337/disjoint-set-unions-by-rank-and-path-compression-3a7b3946f550) | Blog | 0.75 | Examples |
