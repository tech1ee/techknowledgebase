# Research Log

| Date | Topic | Sources | Key Findings | Report |
|------|-------|---------|--------------|--------|
| 2025-12-30 | Database Internals | 20+ | B+Tree (99% DBs), LSM-Tree (write-heavy), WAL, MVCC (PostgreSQL xmin/xmax), ARIES recovery, Buffer Pool, Isolation levels, Locking, Query Optimizer | [report](./2025-12-30-database-internals.md) |
| 2025-12-30 | AI/ML Databases | 22+ | Vector DBs (Pinecone, Milvus, Qdrant, Weaviate, Chroma), FAISS, pgvector, HNSW/IVF algorithms, embeddings, chunking strategies, hybrid search | [report](./2025-12-30-aiml-databases.md) |
| 2025-12-30 | Mobile Databases | 20+ | SQLite internals, Room KMP, SQLDelight, Realm deprecated, PowerSync, ObjectBox, offline-first | [report](./2025-12-30-mobile-databases.md) |
| 2025-12-30 | NoSQL Databases | 20+ | MongoDB, Redis, Cassandra, DynamoDB, Neo4j, ACID vs BASE, sharding/replication, design patterns | [report](./2025-12-30-nosql-databases.md) |
| 2025-12-30 | SQL Databases | 20+ | PostgreSQL vs MySQL vs SQLite, JSONB, Window Functions, CTEs, WAL mode, VACUUM, EXPLAIN ANALYZE, Replication | [report](./2025-12-30-sql-databases.md) |
| 2025-12-30 | Database Fundamentals | 21+ | ACID properties, SQL vs NoSQL, indexing B-Tree O(log n), normalization 3NF, CAP theorem, CRUD operations | [report](./2025-12-30-database-fundamentals.md) |
| 2025-12-29 | Mock Interview Guide | 20+ | 1 mock/week, think aloud, STAR method, Pramp/Interviewing.io, whiteboard practice | [report](./2025-12-29-mock-interview-guide.md) |
| 2025-12-29 | Common Mistakes | 20+ | 25% rejections on complexity, edge cases, off-by-one, UMPIRE method prevention | [report](./2025-12-29-common-mistakes.md) |
| 2025-12-29 | LeetCode Roadmap | 20+ | Blind 75 (4-6 wks), NeetCode 150 (8+ wks), UMPIRE method, spaced repetition | [report](./2025-12-29-leetcode-roadmap.md) |
| 2025-12-29 | Meet in the Middle | 20+ | O(2^(n/2) × n) для n≤40, subset sum, 4SUM, bidirectional BFS | [report](./2025-12-29-meet-in-the-middle.md) |
| 2025-12-29 | Bit Manipulation | 20+ | XOR для уникальных, n&(n-1) tricks, bitmask DP, Brian Kernighan | [report](./2025-12-29-bit-manipulation.md) |
| 2025-12-29 | Union-Find Pattern | 20+ | Path compression + union by rank, O(α(n)) ≈ O(1), Kruskal MST | [report](./2025-12-29-union-find-pattern.md) |
| 2025-12-29 | Topological Sort | 20+ | Kahn's BFS + DFS postorder, cycle detection, Course Schedule | [report](./2025-12-29-topological-sort-pattern.md) |
| 2025-12-29 | Monotonic Stack | 20+ | Next Greater/Smaller O(n), Largest Rectangle, Trapping Rain Water | [report](./2025-12-29-monotonic-stack-pattern.md) |
| 2025-12-29 | Intervals Pattern | 20+ | Sort by start + merge, Meeting Rooms II, sweep line | [report](./2025-12-29-intervals-pattern.md) |
| 2025-12-29 | DP Patterns | 25+ | Fibonacci, 0/1 Knapsack, Unbounded Knapsack, LCS, LIS, Grid DP, Top-down vs Bottom-up | [report](./2025-12-29-dp-patterns.md) |
| 2025-12-29 | DFS & BFS Patterns | 25+ | Tree traversals, Shortest path BFS, Cycle detection DFS, Multi-source BFS, Grid problems | [report](./2025-12-29-dfs-bfs-patterns.md) |
| 2025-12-29 | Binary Search Pattern | 25+ | Boundary Finding, BS on Answer (minimize/maximize), Rotated Arrays, Peak Element | [report](./2025-12-29-binary-search-pattern.md) |
| 2025-12-29 | Sliding Window Pattern | 25+ | Fixed/Variable-size, Monotonic Deque O(n) for max/min, Longest Substring, Minimum Window | [report](./2025-12-29-sliding-window-pattern.md) |
| 2025-12-29 | Two Pointers Pattern | 25+ | Opposite/Same/Fast-Slow directions, O(n²)→O(n), Two Sum II, 3Sum, Container Water, Floyd's Cycle | [report](./2025-12-29-two-pointers-pattern.md) |
| 2025-12-29 | Backtracking | 25+ | Choose/Explore/Unchoose pattern, 9 variations, pruning techniques, Subsets/Permutations/Combinations, N-Queens | [report](./2025-12-29-backtracking.md) |
| 2025-12-29 | Greedy Algorithms | 25+ | Greedy choice property, Exchange Argument proof, Activity Selection, Fractional Knapsack, interval patterns | [report](./2025-12-29-greedy-algorithms.md) |
| 2025-12-29 | Searching Algorithms | 25+ | Binary Search O(log n), Lower/Upper Bound, Binary Search on Answer pattern, modified BS for rotated arrays | [report](./2025-12-29-searching-algorithms.md) |
| 2025-12-29 | Sorting Algorithms | 30+ | QuickSort/MergeSort/HeapSort O(n log n), TimSort hybrid for Python/Java, Counting/Radix O(n), stability vs space trade-offs | [report](./2025-12-29-sorting-algorithms.md) |
| 2025-12-29 | Trie (Prefix Tree) | 25+ | All ops O(m), prefix search ideal, autocomplete, array[26] vs HashMap | [report](./2025-12-29-trie-prefix-tree.md) |
| 2025-12-29 | Heaps & Priority Queues | 25+ | Insert/Delete O(log n), Peek O(1), Build O(n), Top K pattern, Two Heaps for median | [report](./2025-12-29-heaps-priority-queues.md) |
| 2025-12-29 | Graphs Data Structure | 30+ | Adjacency List vs Matrix, BFS/DFS O(V+E), Union-Find near-constant, iterative DFS for large graphs | [report](./2025-12-29-graphs-data-structure.md) |
| 2025-12-29 | Binary Trees & BST | 25+ | BST O(log n) balanced, 4 traversals, Morris O(1) space, common interview patterns | [report](./2025-12-29-binary-trees-bst.md) |
| 2025-12-29 | Mobile AI Production Patterns | 30+ | Hybrid cloud+edge architecture, OTA model updates, KV-cache optimization, federated learning, A/B testing models | [report](./2025-12-29-mobile-ai-production.md) |
| 2025-12-29 | Mobile Models & Quantization | 30+ | Gemma 3n (2-4GB), Llama 3.2 Q4 (56% size reduction), GGUF Q4_K_M best for mobile, on-device LoRA | [report](./2025-12-29-mobile-models-quantization.md) |
| 2025-12-29 | Mobile NPU Acceleration | 25+ | Apple ANE 35 TOPS, Snapdragon Hexagon 73 TOPS, NPU 35-70% less power than GPU, NNAPI deprecated | [report](./2025-12-29-mobile-npu-acceleration.md) |
| 2025-12-29 | Mobile AI SDKs | 30+ | LiteRT (TFLite rebranded), ExecuTorch 1.0, CoreML, ONNX Runtime Mobile, MediaPipe | [report](./2025-12-29-mobile-ai-sdks.md) |
| 2025-12-26 | Android Performance Profiling | 25+ | Android Studio Profiler, Perfetto, LeakCanary, Baseline Profiles, Macrobenchmark, R8 | [report](./2025-12-26-android-performance-profiling.md) |
| 2025-12-26 | Jetpack Compose Internals | 25+ | Compiler Plugin, Slot Table, Three Phases, Snapshot System, Stability, Side Effects, Modifier Chain | [report](./2025-12-26-android-compose-internals.md) |
| 2025-12-25 | Android View Rendering Pipeline | 25+ | Choreographer, VSYNC, RenderThread, Display Lists, hardware layers, overdraw, Profile GPU Rendering | [report](./2025-12-25-android-view-rendering-pipeline.md) |
| 2025-12-25 | Android Touch Handling | 25+ | onInterceptTouchEvent, MotionEvent, multi-touch pointer IDs, GestureDetector, VelocityTracker, nested scrolling | [report](./2025-12-25-android-touch-handling.md) |
| 2025-12-25 | Android Canvas Drawing | 25+ | Canvas/Paint, Shaders, PorterDuff, hardware accel limits, performance optimization | [report](./2025-12-25-android-canvas-drawing.md) |
| 2025-12-25 | Android View Measurement | 28+ | MeasureSpec modes, setMeasuredDimension, measureChild vs measureChildWithMargins, double taxation, performance | [report](./2025-12-25-android-view-measurement.md) |
| 2025-12-25 | Android Custom Views | 25+ | Constructors, lifecycle, invalidate/requestLayout, accessibility, memory leaks | [report](./2025-12-25-android-custom-views.md) |
