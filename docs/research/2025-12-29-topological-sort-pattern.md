# Research Report: Topological Sort Pattern (2024-2025)

**Date:** 2025-12-29
**Sources:** 20+

## Executive Summary

Topological sort orders vertices in DAG such that for every edge u→v, u comes before v. Two approaches: DFS-based (reverse postorder) and Kahn's algorithm (BFS with indegrees).

## Key Insights

> "Calculate indegree of each node. Add nodes with indegree 0 to queue. Process and decrement neighbors' indegrees." — [GeeksforGeeks](https://www.geeksforgeeks.org/topological-sorting-indegree-based-solution/)

> "If number of nodes in final order < total nodes, cycle exists." — [LeetCode Guide](https://leetcode.com/discuss/post/6136469/Guide-How-to-identify-and-solve-topological-sort-questions/)

## LeetCode Problems
- 207. Course Schedule
- 210. Course Schedule II
- 269. Alien Dictionary
- 310. Minimum Height Trees
- 802. Find Eventual Safe States
