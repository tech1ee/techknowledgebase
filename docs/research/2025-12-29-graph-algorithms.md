# Research Report: Graph Algorithms

**Date:** 2025-12-29
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Graph algorithms — фундамент для решения задач о связности, путях и зависимостях. BFS и DFS — базовые алгоритмы обхода с O(V+E) сложностью. BFS находит кратчайший путь в невзвешенных графах, DFS оптимален для задач на полный обход (cycle detection, topological sort). Dijkstra для взвешенных графов без отрицательных рёбер. Представление: adjacency list для sparse графов, matrix для dense.

---

## Key Findings

### 1. Graph Representations

| Representation | Space | Edge Check | Neighbors | Best For |
|----------------|-------|------------|-----------|----------|
| Adjacency Matrix | O(V²) | O(1) | O(V) | Dense graphs |
| Adjacency List | O(V+E) | O(degree) | O(degree) | Sparse graphs |
| Hash of Hashes | O(V+E) | O(1) avg | O(degree) | Interviews |

**Rule of thumb:**
- E close to V² → matrix
- E close to V → list

### 2. BFS (Breadth-First Search)

**Характеристики:**
- Использует Queue
- Обходит level by level
- Находит shortest path в unweighted graphs
- Time: O(V+E), Space: O(V)

**Use cases:**
- Shortest path (unweighted)
- Level order traversal
- Bipartite check
- Connected components

### 3. DFS (Depth-First Search)

**Характеристики:**
- Использует Stack (или recursion)
- Идёт максимально глубоко перед backtrack
- Time: O(V+E), Space: O(V)

**Use cases:**
- Cycle detection
- Topological sort
- Connected components
- Path finding
- Backtracking problems

### 4. Dijkstra's Algorithm

**Доказательство корректности:**
- Proof by contradiction: если d[u] ≠ δ(s,u), то существует вершина с меньшим distance, что противоречит выбору из priority queue
- Требует: non-negative edge weights
- Time: O((V+E) log V) with binary heap

**Почему не работает с отрицательными рёбрами:**
- Relaxation может уменьшить distance уже processed вершины
- Greedy выбор становится некорректным

### 5. Cycle Detection

**Undirected Graph:**
- DFS + parent tracking
- Если сосед visited AND не parent → cycle
- Union-Find также работает

**Directed Graph:**
- DFS + recursion stack
- Три цвета: white (unvisited), gray (in progress), black (done)
- Если встретили gray → cycle

### 6. Topological Sort

**Два подхода:**

| Approach | Method | Cycle Detection |
|----------|--------|-----------------|
| Kahn's | BFS + indegree | result.size < V |
| DFS | Post-order reverse | back edge found |

**Применение:**
- Build systems (Make, Gradle)
- Course scheduling
- Task dependencies

### 7. Common Interview Problems

| Problem | Algorithm | Key Insight |
|---------|-----------|-------------|
| Number of Islands | DFS/BFS | Grid as graph |
| Course Schedule | Topological/Cycle | Detect cycle |
| Clone Graph | DFS + HashMap | Track visited |
| Word Ladder | BFS | Shortest path |
| Pacific Atlantic Water | Multi-source BFS | Start from edges |

### 8. Corner Cases

- Empty graph
- Single node
- Disconnected components
- Self-loops
- Parallel edges
- Directed vs undirected

---

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [Tech Interview Handbook - Graph](https://www.techinterviewhandbook.org/algorithms/graph/) | Guide | 0.95 |
| 2 | [GeeksforGeeks - BFS](https://www.geeksforgeeks.org/dsa/breadth-first-search-or-bfs-for-a-graph/) | Tutorial | 0.90 |
| 3 | [Wikipedia - Dijkstra](https://en.wikipedia.org/wiki/Dijkstra's_algorithm) | Reference | 0.95 |
| 4 | [CP-Algorithms - Cycle Detection](https://cp-algorithms.com/graph/finding-cycle.html) | Tutorial | 0.90 |
| 5 | [GeeksforGeeks - Topological Sort](https://www.geeksforgeeks.org/dsa/topological-sorting-indegree-based-solution/) | Tutorial | 0.90 |
| 6 | [USACO Guide - Toposort](https://usaco.guide/gold/toposort) | Tutorial | 0.90 |
| 7 | [UC Davis - Dijkstra Proof](https://www.cs.ucdavis.edu/~bai/ECS122A/Notes/ShortPathProof.pdf) | Academic | 0.95 |

---

*Generated: 2025-12-29*
