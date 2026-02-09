# Research Report: Persistent Data Structures (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Persistent структуры сохраняют все версии при модификации. **Structural sharing** — переиспользование неизменённых частей. Используются в Git, Redux, функциональных языках. Path copying даёт O(log n) overhead на операцию.

## Key Insights

> "A persistent data structure always preserves the previous version when modified. Effectively immutable." — [Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure)

> "When modification occurs, only affected parts are copied, rest remains shared (structural sharing)." — [SoftwareMill](https://softwaremill.com/persistent-data-structures-in-functional-programming/)

> "Safe sharing across threads without locks, avoiding race conditions." — [Medium](https://medium.com/@luizgabriel.info/functional-programming-and-immutable-data-structures-03e2b87e82cc)

## Types of Persistence

| Type | Access | Modify |
|------|--------|--------|
| Partial | All versions | Only newest |
| Full | All versions | All versions |
| Confluent | All versions | All versions + merge |

## Techniques

### Path Copying
```
Copy only path from root to modified node
Reuse all other nodes
O(log n) extra space per update
```

### Fat Nodes
```
Store all versions in each node
Each node has version → value map
O(1) space per update, O(log m) query (m = updates)
```

### Structural Sharing (Immutable)
```
Old:  [A] → [B] → [C]
                    ↘
New:  [A] → [B'] → [D]

B' points to new D, original C unchanged
```

## Persistent Segment Tree

```
Each update creates new path from root
Old and new trees share unchanged subtrees
O(log n) time, O(log n) space per update
Supports queries on any version
```

## Applications

- Git version control
- Undo/Redo functionality
- Database snapshots
- Functional programming (Clojure, Haskell)
- React/Redux state management

## Sources

| # | Source | Type | Key Contribution |
|---|--------|------|------------------|
| 1 | [Wikipedia](https://en.wikipedia.org/wiki/Persistent_data_structure) | Reference | Theory |
| 2 | [SoftwareMill](https://softwaremill.com/persistent-data-structures-in-functional-programming/) | Blog | FP context |
| 3 | [Arpit Bhayani](https://arpitbhayani.me/blogs/persistent-data-structures-introduction/) | Blog | Implementation |
| 4 | [Medium](https://configr.medium.com/unlocking-the-power-of-persistent-data-structures-f691624e8a7f) | Blog | Applications |
