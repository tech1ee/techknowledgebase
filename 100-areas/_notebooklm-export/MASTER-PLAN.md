# NotebookLM Export Master Plan

## Исследование NotebookLM (Январь 2026)

### Критические лимиты

| Параметр | Free | Plus |
|----------|------|------|
| Notebooks | 100 | 500 |
| Sources/notebook | **50** | 300 |
| Words/source (upload) | 500,000 | 500,000 |
| **Words/source (Audio Overview)** | **10,000** | **10,000** |
| Audio Overviews/day | 3 | 20 |
| Audio length | 5-20 min | 5-20 min |

**КРИТИЧНО:** Audio Overview обрабатывает только первые **10,000 слов** каждого source!

### Оптимальная структура файла

```
Идеальный размер: 5,000-10,000 слов
Формат: Только prose (текст)
Структура: H1 > H2 > H3
Начало: Executive Summary
Содержание: Bullet points для ключевых концептов
Конец: Transition к следующей теме
```

### Что работает для Audio Overview

✅ Чистый prose-текст с объяснениями
✅ Аналогии и метафоры
✅ "Почему" объяснения, история решений
✅ Концептуальные связи между темами
✅ Примеры из реального мира
✅ Q&A формат (вопрос-ответ)

### Что НЕ работает

❌ Код (игнорируется или плохо озвучивается)
❌ ASCII диаграммы
❌ Markdown таблицы
❌ Wikilinks [[...]]
❌ YAML frontmatter
❌ Технический жаргон без объяснений

---

## Исходная база знаний

**Всего:** 391 файл, 1,567,574 слова (~1.57M)

### Распределение по темам

| Область | Файлов | Слов | Target files (7K each) |
|---------|--------|------|------------------------|
| iOS Development | 45 | 252,495 | **36** |
| Android Development | 46 | 195,230 | **28** |
| Cross-Platform | 24 | 95,000 | **14** |
| CS Fundamentals | 89 | 310,000 | **44** |
| Backend/Infra | 76 | 298,000 | **43** |
| AI/ML | 42 | 188,000 | **27** |
| Career | 36 | 72,000 | **10** |
| Architecture | 33 | 48,000 | **7** |
| **TOTAL** | **391** | **1,567,574** | **209** |

---

## Детальный план: 8 Notebooks

### Notebook 1: iOS Development (36 files)

**Цель:** Полное понимание iOS разработки для Senior инженера

#### Файлы:

##### Memory & ARC (4 files)
1. `ios-memory-fundamentals.md` - ARC basics, reference counting, memory layout (7K)
2. `ios-retain-cycles.md` - Retain cycles, weak/unowned, capture lists (7K)
3. `ios-memory-debugging.md` - Instruments, Leaks, Allocations profiling (7K)
4. `ios-memory-optimization.md` - Autorelease pools, image caching, large data (7K)

##### App Lifecycle (3 files)
5. `ios-app-lifecycle.md` - App states, background modes, scene lifecycle (7K)
6. `ios-viewcontroller-lifecycle.md` - VC lifecycle, view loading, transitions (7K)
7. `ios-process-fundamentals.md` - Darwin/XNU, Mach-O, process structure (7K)

##### UI Frameworks (5 files)
8. `ios-swiftui-fundamentals.md` - Declarative UI, View protocol, body (7K)
9. `ios-swiftui-state.md` - @State, @Binding, @ObservedObject, @StateObject (7K)
10. `ios-uikit-fundamentals.md` - UIView, responder chain, Auto Layout (7K)
11. `ios-swiftui-vs-uikit.md` - When to use which, interop, migration (7K)
12. `ios-custom-views.md` - Drawing, Core Graphics, animations (7K)

##### Concurrency (4 files)
13. `ios-gcd-fundamentals.md` - Queues, sync/async, barriers, groups (7K)
14. `ios-async-await.md` - Swift concurrency, actors, structured concurrency (7K)
15. `ios-combine.md` - Publishers, subscribers, operators, schedulers (7K)
16. `ios-concurrency-mistakes.md` - Race conditions, deadlocks, debugging (7K)

##### Architecture (4 files)
17. `ios-architecture-patterns.md` - MVC, MVVM, VIPER, Clean Architecture (7K)
18. `ios-dependency-injection.md` - DI patterns, containers, testing (7K)
19. `ios-state-management.md` - State patterns, Redux-like, TCA (7K)
20. `ios-modularization.md` - Modules, frameworks, SPM, microfeatures (7K)

##### Data & Networking (4 files)
21. `ios-data-persistence.md` - UserDefaults, Keychain, file system (7K)
22. `ios-core-data.md` - Core Data stack, contexts, migrations (7K)
23. `ios-swiftdata.md` - SwiftData, @Model, queries (7K)
24. `ios-networking.md` - URLSession, REST, GraphQL, caching (7K)

##### Performance (3 files)
25. `ios-performance-profiling.md` - Instruments, Time Profiler, energy (7K)
26. `ios-scroll-performance.md` - Table/collection optimization, prefetching (7K)
27. `ios-rendering-pipeline.md` - Core Animation, off-screen rendering (7K)

##### Build & Distribution (4 files)
28. `ios-xcode-fundamentals.md` - Xcode workflow, schemes, configurations (7K)
29. `ios-build-system.md` - Compilation, linking, Swift compiler (7K)
30. `ios-code-signing.md` - Certificates, provisioning, entitlements (7K)
31. `ios-ci-cd.md` - Fastlane, Xcode Cloud, GitHub Actions (7K)

##### Testing & Quality (3 files)
32. `ios-testing-fundamentals.md` - XCTest, unit tests, mocking (7K)
33. `ios-ui-testing.md` - XCUITest, snapshot tests, accessibility (7K)
34. `ios-debugging.md` - LLDB, breakpoints, view debugging (7K)

##### Modern iOS (2 files)
35. `ios-swift-evolution.md` - Swift 5.x features, async/await, macros (7K)
36. `ios-market-trends-2026.md` - visionOS, AI integration, SwiftUI 6 (7K)

---

### Notebook 2: Android Development (28 files)

**Цель:** Полное понимание Android разработки для Senior инженера

#### Файлы:

##### Memory & GC (3 files)
1. `android-memory-gc.md` - ART, GC algorithms, generational collection (7K)
2. `android-memory-leaks.md` - Common leaks, detection, tools (7K)
3. `android-memory-optimization.md` - Bitmap handling, caching strategies (7K)

##### Lifecycle & Components (4 files)
4. `android-activity-lifecycle.md` - Activity states, config changes (7K)
5. `android-fragment-lifecycle.md` - Fragment lifecycle, back stack (7K)
6. `android-app-components.md` - Services, BroadcastReceivers, ContentProviders (7K)
7. `android-process-lifecycle.md` - Process priority, LMK, foreground services (7K)

##### UI Frameworks (5 files)
8. `android-compose-fundamentals.md` - Composable functions, recomposition (7K)
9. `android-compose-state.md` - remember, State, derivedStateOf (7K)
10. `android-views-fundamentals.md` - View system, measure/layout/draw (7K)
11. `android-compose-vs-views.md` - When to use which, interop (7K)
12. `android-custom-views.md` - Canvas, Paint, custom drawing (7K)

##### Concurrency (4 files)
13. `android-coroutines-fundamentals.md` - Suspend functions, dispatchers (7K)
14. `android-flow.md` - StateFlow, SharedFlow, operators (7K)
15. `android-coroutines-advanced.md` - Structured concurrency, exceptions (7K)
16. `android-threading-legacy.md` - Handlers, Loopers, ExecutorService (7K)

##### Architecture (3 files)
17. `android-architecture-patterns.md` - MVI, MVVM, Clean Architecture (7K)
18. `android-dependency-injection.md` - Hilt, Koin, manual DI (7K)
19. `android-modularization.md` - Multi-module, feature modules, navigation (7K)

##### Data & Networking (3 files)
20. `android-data-persistence.md` - Room, DataStore, SharedPreferences (7K)
21. `android-networking.md` - Retrofit, OkHttp, Ktor (7K)
22. `android-repository-pattern.md` - Repository, offline-first, caching (7K)

##### Build & Distribution (3 files)
23. `android-gradle-fundamentals.md` - Gradle, Kotlin DSL, dependencies (7K)
24. `android-build-variants.md` - Flavors, build types, signing (7K)
25. `android-ci-cd.md` - GitHub Actions, Play Console, release (7K)

##### Testing & Quality (2 files)
26. `android-testing.md` - JUnit, Espresso, Compose testing (7K)
27. `android-debugging.md` - Android Studio profiler, ADB (7K)

##### Modern Android (1 file)
28. `android-market-trends-2026.md` - Kotlin 2.x, Compose Multiplatform (7K)

---

### Notebook 3: Cross-Platform Development (14 files)

**Цель:** Сравнение iOS и Android, KMP, кросс-платформенная разработка

#### Файлы:

##### Philosophy (2 files)
1. `platform-philosophy.md` - iOS determinism vs Android flexibility (7K)
2. `platform-decision-guide.md` - Native vs Cross-platform decision matrix (7K)

##### Memory Comparison (2 files)
3. `platform-memory-comparison.md` - ARC vs GC deep comparison (7K)
4. `platform-memory-practical.md` - Porting memory patterns between platforms (7K)

##### Lifecycle Comparison (2 files)
5. `platform-lifecycle-comparison.md` - VC vs Activity/Fragment (7K)
6. `platform-navigation.md` - Navigation patterns comparison (7K)

##### UI Comparison (2 files)
7. `platform-ui-declarative.md` - SwiftUI vs Compose deep comparison (7K)
8. `platform-ui-imperative.md` - UIKit vs Views comparison (7K)

##### Async Comparison (2 files)
9. `platform-async-modern.md` - Swift async/await vs Kotlin coroutines (7K)
10. `platform-async-reactive.md` - Combine vs Flow comparison (7K)

##### KMP/Kotlin Multiplatform (4 files)
11. `kmp-fundamentals.md` - expect/actual, shared code architecture (7K)
12. `kmp-ios-interop.md` - SKIE, Swift interop, CocoaPods (7K)
13. `kmp-compose-multiplatform.md` - Compose for iOS, desktop, web (7K)
14. `kmp-architecture.md` - Clean Architecture for KMP projects (7K)

---

### Notebook 4: CS Theory & Fundamentals (44 files)

**Цель:** Глубокие знания computer science для интервью и работы

#### Файлы:

##### Algorithms - Sorting & Searching (4 files)
1. `algo-sorting-basic.md` - Bubble, Selection, Insertion sort (7K)
2. `algo-sorting-efficient.md` - QuickSort, MergeSort, HeapSort (7K)
3. `algo-searching.md` - Binary search, interpolation, exponential (7K)
4. `algo-complexity.md` - Big O, time/space complexity analysis (7K)

##### Algorithms - Patterns (6 files)
5. `algo-two-pointers.md` - Two pointers, sliding window (7K)
6. `algo-binary-search-advanced.md` - Binary search variations (7K)
7. `algo-recursion.md` - Recursion, backtracking, memoization (7K)
8. `algo-dynamic-programming.md` - DP fundamentals, patterns (7K)
9. `algo-greedy.md` - Greedy algorithms, when to use (7K)
10. `algo-divide-conquer.md` - Divide and conquer patterns (7K)

##### Data Structures - Linear (5 files)
11. `ds-arrays.md` - Arrays, dynamic arrays, operations (7K)
12. `ds-linked-lists.md` - Singly, doubly, circular linked lists (7K)
13. `ds-stacks-queues.md` - Stack, queue, deque implementations (7K)
14. `ds-strings.md` - String algorithms, pattern matching (7K)
15. `ds-hash-tables.md` - Hashing, collision resolution, HashMaps (7K)

##### Data Structures - Trees (5 files)
16. `ds-binary-trees.md` - Binary tree traversals, properties (7K)
17. `ds-bst.md` - BST operations, balancing concept (7K)
18. `ds-balanced-trees.md` - AVL, Red-Black trees (7K)
19. `ds-heaps.md` - Binary heap, priority queue (7K)
20. `ds-tries.md` - Trie, prefix trees, autocomplete (7K)

##### Data Structures - Graphs (4 files)
21. `ds-graphs-fundamentals.md` - Graph representations, terminology (7K)
22. `ds-graph-traversal.md` - BFS, DFS, applications (7K)
23. `ds-shortest-path.md` - Dijkstra, Bellman-Ford, Floyd-Warshall (7K)
24. `ds-graph-advanced.md` - Topological sort, MST, Union-Find (7K)

##### Design Patterns (6 files)
25. `patterns-creational.md` - Singleton, Factory, Builder, Prototype (7K)
26. `patterns-structural.md` - Adapter, Decorator, Facade, Proxy (7K)
27. `patterns-behavioral.md` - Observer, Strategy, Command, State (7K)
28. `patterns-concurrency.md` - Thread pool, Producer-Consumer (7K)
29. `patterns-functional.md` - Monad, Functor, functional patterns (7K)
30. `patterns-mobile.md` - Repository, Coordinator, DI patterns (7K)

##### Operating Systems (6 files)
31. `os-processes-threads.md` - Process vs thread, creation, states (7K)
32. `os-memory-management.md` - Virtual memory, paging, segmentation (7K)
33. `os-scheduling.md` - CPU scheduling algorithms (7K)
34. `os-synchronization.md` - Mutex, semaphore, deadlocks (7K)
35. `os-file-systems.md` - File system concepts, inodes (7K)
36. `os-io.md` - I/O models, blocking, non-blocking, async (7K)

##### Computer Architecture (4 files)
37. `arch-cpu.md` - CPU architecture, pipelines, caches (7K)
38. `arch-memory-hierarchy.md` - L1/L2/L3 cache, RAM, storage (7K)
39. `arch-compilation.md` - Compilation, linking, runtime (7K)
40. `arch-networking-basics.md` - OSI model, TCP/IP fundamentals (7K)

##### Math for CS (4 files)
41. `math-discrete.md` - Sets, relations, functions, logic (7K)
42. `math-probability.md` - Probability, expected value, distributions (7K)
43. `math-combinatorics.md` - Permutations, combinations, counting (7K)
44. `math-number-theory.md` - Primes, GCD, modular arithmetic (7K)

---

### Notebook 5: Backend & Infrastructure (43 files)

**Цель:** Backend разработка, databases, DevOps для full-stack понимания

#### Файлы:

##### JVM & Kotlin (5 files)
1. `jvm-fundamentals.md` - JVM architecture, bytecode, class loading (7K)
2. `jvm-memory.md` - Heap, stack, GC algorithms (7K)
3. `jvm-concurrency.md` - Threads, executors, virtual threads (7K)
4. `kotlin-advanced.md` - Kotlin features, coroutines internals (7K)
5. `kotlin-multiplatform.md` - KMP architecture, expect/actual (7K)

##### Databases - SQL (6 files)
6. `db-relational-fundamentals.md` - Relational model, normalization (7K)
7. `db-sql-queries.md` - SQL syntax, joins, aggregations (7K)
8. `db-indexing.md` - Index types, B-trees, query optimization (7K)
9. `db-transactions.md` - ACID, isolation levels, locking (7K)
10. `db-postgresql.md` - PostgreSQL specifics, advanced features (7K)
11. `db-mysql.md` - MySQL specifics, InnoDB, replication (7K)

##### Databases - NoSQL (4 files)
12. `db-nosql-overview.md` - NoSQL categories, use cases (7K)
13. `db-mongodb.md` - Document databases, MongoDB (7K)
14. `db-redis.md` - In-memory stores, caching strategies (7K)
15. `db-cassandra.md` - Wide-column stores, distributed DBs (7K)

##### Databases - Advanced (3 files)
16. `db-replication.md` - Master-slave, multi-master, consensus (7K)
17. `db-sharding.md` - Horizontal scaling, partition strategies (7K)
18. `db-migrations.md` - Schema migrations, zero-downtime (7K)

##### Networking (5 files)
19. `net-tcp-ip.md` - TCP/IP stack, sockets, connections (7K)
20. `net-http.md` - HTTP/1.1, HTTP/2, HTTP/3, QUIC (7K)
21. `net-rest-api.md` - REST principles, API design (7K)
22. `net-graphql.md` - GraphQL fundamentals, vs REST (7K)
23. `net-grpc.md` - gRPC, Protocol Buffers, streaming (7K)

##### DevOps - Containers (4 files)
24. `devops-docker.md` - Docker fundamentals, images, containers (7K)
25. `devops-dockerfile.md` - Dockerfile best practices, multi-stage (7K)
26. `devops-kubernetes-basics.md` - K8s concepts, pods, services (7K)
27. `devops-kubernetes-advanced.md` - Deployments, StatefulSets, Helm (7K)

##### DevOps - CI/CD (4 files)
28. `devops-ci-fundamentals.md` - CI concepts, pipelines, testing (7K)
29. `devops-cd-fundamentals.md` - CD, deployment strategies (7K)
30. `devops-github-actions.md` - GitHub Actions, workflows (7K)
31. `devops-gitops.md` - GitOps, ArgoCD, Flux (7K)

##### Cloud (5 files)
32. `cloud-fundamentals.md` - IaaS, PaaS, SaaS concepts (7K)
33. `cloud-aws-core.md` - AWS core services overview (7K)
34. `cloud-gcp-core.md` - GCP core services overview (7K)
35. `cloud-serverless.md` - Lambda, Cloud Functions, serverless patterns (7K)
36. `cloud-infrastructure-as-code.md` - Terraform, Pulumi fundamentals (7K)

##### Observability (4 files)
37. `observability-logging.md` - Logging best practices, ELK (7K)
38. `observability-metrics.md` - Metrics, Prometheus, Grafana (7K)
39. `observability-tracing.md` - Distributed tracing, OpenTelemetry (7K)
40. `observability-alerting.md` - Alerting strategies, on-call (7K)

##### Security (3 files)
41. `security-auth.md` - Authentication, OAuth2, JWT (7K)
42. `security-web.md` - OWASP top 10, XSS, CSRF, SQLi (7K)
43. `security-infrastructure.md` - TLS, certificates, secrets management (7K)

---

### Notebook 6: AI/ML & LLM (27 files)

**Цель:** AI/ML для мобильных разработчиков, LLM интеграция

#### Файлы:

##### ML Fundamentals (5 files)
1. `ml-basics.md` - ML concepts, supervised/unsupervised (7K)
2. `ml-algorithms.md` - Common algorithms explained (7K)
3. `ml-neural-networks.md` - Neural network fundamentals (7K)
4. `ml-deep-learning.md` - CNN, RNN, Transformers basics (7K)
5. `ml-evaluation.md` - Metrics, validation, overfitting (7K)

##### LLM & Transformers (5 files)
6. `llm-fundamentals.md` - How LLMs work, attention mechanism (7K)
7. `llm-prompting.md` - Prompt engineering, techniques (7K)
8. `llm-fine-tuning.md` - Fine-tuning, LoRA, PEFT (7K)
9. `llm-inference.md` - Inference optimization, quantization (7K)
10. `llm-evaluation.md` - LLM evaluation, benchmarks (7K)

##### RAG & Vector Databases (4 files)
11. `rag-fundamentals.md` - RAG architecture, components (7K)
12. `rag-embeddings.md` - Embeddings, similarity search (7K)
13. `rag-vector-databases.md` - Pinecone, Chroma, pgvector (7K)
14. `rag-advanced.md` - Hybrid search, reranking, chunking (7K)

##### AI Agents (4 files)
15. `agents-fundamentals.md` - Agent architecture, reasoning (7K)
16. `agents-tools.md` - Tool use, function calling (7K)
17. `agents-memory.md` - Memory systems, context management (7K)
18. `agents-orchestration.md` - Multi-agent systems, orchestration (7K)

##### AI Integration (5 files)
19. `ai-integration-mobile.md` - On-device ML, Core ML, ML Kit (7K)
20. `ai-integration-apis.md` - OpenAI, Anthropic, Google AI APIs (7K)
21. `ai-integration-langchain.md` - LangChain fundamentals (7K)
22. `ai-integration-llamaindex.md` - LlamaIndex for data (7K)
23. `ai-integration-best-practices.md` - Production AI patterns (7K)

##### AI Engineering (4 files)
24. `ai-mlops.md` - MLOps fundamentals, pipelines (7K)
25. `ai-deployment.md` - Model deployment, serving (7K)
26. `ai-monitoring.md` - AI system monitoring, drift (7K)
27. `ai-ethics.md` - AI ethics, responsible AI (7K)

---

### Notebook 7: Career & Interview (10 files)

**Цель:** Подготовка к интервью, карьерный рост

#### Файлы:

##### Interview Preparation (4 files)
1. `interview-process.md` - Interview types, what to expect (7K)
2. `interview-coding.md` - Coding interview strategies (7K)
3. `interview-system-design.md` - System design approach (7K)
4. `interview-behavioral.md` - STAR method, common questions (7K)

##### Job Search (3 files)
5. `job-search-strategy.md` - Job search strategy 2026 (7K)
6. `job-search-resume.md` - Resume optimization, ATS (7K)
7. `job-search-networking.md` - Networking, LinkedIn, referrals (7K)

##### Career Growth (3 files)
8. `career-growth-path.md` - IC vs Management track (7K)
9. `career-soft-skills.md` - Communication, leadership (7K)
10. `career-negotiation.md` - Salary negotiation tactics (7K)

---

### Notebook 8: Architecture & System Design (7 files)

**Цель:** Архитектура систем, system design для интервью

#### Файлы:

##### System Design (4 files)
1. `sysdesign-fundamentals.md` - Scalability, availability, consistency (7K)
2. `sysdesign-patterns.md` - Common patterns, microservices (7K)
3. `sysdesign-case-studies.md` - Twitter, Instagram, Uber design (7K)
4. `sysdesign-mobile.md` - Mobile system design specifics (7K)

##### API Design (2 files)
5. `api-design-principles.md` - API design best practices (7K)
6. `api-versioning.md` - Versioning, deprecation, evolution (7K)

##### Distributed Systems (1 file)
7. `distributed-fundamentals.md` - CAP theorem, consensus, consistency (7K)

---

## Итого

| Notebook | Files | Words |
|----------|-------|-------|
| 1. iOS Development | 36 | 252K |
| 2. Android Development | 28 | 196K |
| 3. Cross-Platform | 14 | 98K |
| 4. CS Theory | 44 | 308K |
| 5. Backend & Infra | 43 | 301K |
| 6. AI/ML & LLM | 27 | 189K |
| 7. Career & Interview | 10 | 70K |
| 8. Architecture | 7 | 49K |
| **TOTAL** | **209** | **1,463K** |

---

## Правила создания файлов

### Формат каждого файла

```markdown
# [Topic Title]

## Executive Summary

[2-3 параграфа: что это, зачем нужно, ключевые концепты]

## [Main Section 1]

### [Subsection 1.1]
[Prose explanation with analogies]

### [Subsection 1.2]
[Prose explanation with examples]

## [Main Section 2]
...

## Common Mistakes and How to Avoid Them

[Prose about typical errors]

## Real-World Applications

[Examples from production systems]

## Key Takeaways

- [Point 1]
- [Point 2]
- [Point 3]

## What to Learn Next

[Transition to related topics]
```

### Требования к контенту

1. **Только prose** - никакого кода, диаграмм, таблиц
2. **Аналогии** - каждый сложный концепт объяснять через аналогию
3. **"Почему"** - объяснять не только "что", но и "почему"
4. **История** - откуда взялся концепт, как эволюционировал
5. **Реальные примеры** - Apple, Google, Netflix, etc.
6. **Связи** - как тема связана с другими
7. **5,000-10,000 слов** - оптимально для Audio Overview

---

## План выполнения

### Phase 1: iOS + Android (64 files)
- Notebook 1: iOS Development (36 files)
- Notebook 2: Android Development (28 files)

### Phase 2: Cross-Platform + CS Theory (58 files)
- Notebook 3: Cross-Platform (14 files)
- Notebook 4: CS Theory (44 files)

### Phase 3: Backend + AI/ML (70 files)
- Notebook 5: Backend & Infra (43 files)
- Notebook 6: AI/ML & LLM (27 files)

### Phase 4: Career + Architecture (17 files)
- Notebook 7: Career & Interview (10 files)
- Notebook 8: Architecture (7 files)

---

## Sources

- [NotebookLM Limits Explained](https://medium.com/ai-quick-tips/notebooklm-limits-explained-free-vs-pro-what-you-actually-get-1625db4ac6dc)
- [NotebookLM Complete Guide](https://medium.com/@shivashanker7337/notebooklm-the-complete-guide-updated-october-2025-1c9ebf5c14f6)
- [Google NotebookLM Help](https://support.google.com/notebooklm/answer/16269187?hl=en)
- [8 Expert Tips for NotebookLM](https://blog.google/technology/ai/notebooklm-beginner-tips/)
- [Audio Overview Guide](https://support.google.com/notebooklm/answer/16212820?hl=en)
