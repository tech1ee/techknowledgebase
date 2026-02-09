# Research Report: Advanced Trees (AVL, Red-Black) (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Self-balancing BST гарантируют O(log n) для всех операций. **AVL**: строже сбалансирован (height ≤ 1.44 log n), лучше для поиска. **Red-Black**: меньше ротаций, лучше для insert/delete. Red-Black используется в std::map (C++), TreeMap (Java).

## Key Insights

> "AVL trees typically have a lower height (1.44 log n) compared to Red-Black trees (2 log n)." — [AlgoCademy](https://algocademy.com/blog/balancing-trees-avl-vs-red-black-trees/)

> "If your application involves many frequent insertions and deletions, then Red Black trees should be preferred." — [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/self-balancing-binary-search-trees/)

> "Red Black tree is more commonly implemented in language libraries like map in C++, TreeMap in Java." — [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/self-balancing-binary-search-trees/)

## Comparison

| Feature | AVL Tree | Red-Black Tree |
|---------|----------|----------------|
| Balance Factor | Height diff ≤ 1 | Color rules |
| Height | ≤ 1.44 log n | ≤ 2 log n |
| Insert rotations | Up to 2 | Up to 2 |
| Delete rotations | Up to O(log n) | Up to 3 |
| Best for | Read-heavy | Write-heavy |
| Used in | Databases | Language libraries |

## AVL Rotations

- LL (Left-Left): Single right rotation
- RR (Right-Right): Single left rotation
- LR (Left-Right): Left then right rotation
- RL (Right-Left): Right then left rotation

## Red-Black Properties

1. Every node is red or black
2. Root is always black
3. Every leaf (NIL) is black
4. Red node has only black children
5. All paths have same black node count

## Sources

| # | Source | Type | Key Contribution |
|---|--------|------|------------------|
| 1 | [GeeksforGeeks](https://www.geeksforgeeks.org/dsa/introduction-to-avl-tree/) | Tutorial | AVL implementation |
| 2 | [AlgoCademy](https://algocademy.com/blog/balancing-trees-avl-vs-red-black-trees/) | Blog | Comparison |
| 3 | [CP-Algorithms](https://cp-algorithms.com) | Reference | Formal analysis |
| 4 | [Interview Kickstart](https://interviewkickstart.com/blogs/learn/data-structures-and-algorithms-avl-trees) | Course | Interview prep |
