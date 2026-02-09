---
title: "Research Report: Database Internals"
created: 2025-12-30
modified: 2025-12-30
type: reference
status: draft
tags:
  - topic/databases
---

# Research Report: Database Internals

**Date:** 2025-12-30
**Sources Evaluated:** 20+
**Research Depth:** Deep (comprehensive multi-source analysis)

## Executive Summary

Database internals — фундаментальные механизмы работы СУБД: хранение, индексация, транзакции, восстановление. **B+Tree** — основа индексов в 99% RDBMS (O(log n) операции, все данные в листьях). **LSM-Tree** — для write-heavy NoSQL (Cassandra, RocksDB): sequential writes, compaction для оптимизации. **WAL (Write-Ahead Log)** — гарантия durability: логируем до записи, recovery через REDO/UNDO. **MVCC** — конкурентность без блокировок (PostgreSQL хранит версии в heap, требует VACUUM). Isolation levels: READ COMMITTED → SERIALIZABLE (trade-off: consistency vs concurrency). ARIES — стандарт recovery (Analysis → Redo → Undo). Buffer Pool управляет страницами в памяти (LRU/LRU-K). Write/Read amplification — ключевые метрики LSM-деревьев.

---

## Key Findings

### 1. B-Tree и B+Tree [HIGH CONFIDENCE]

**B-Tree:**
- Сбалансированное дерево для sorted data
- Узлы содержат ключи и указатели на детей
- O(log n) для search, insert, delete
- Fanout минимизирует disk seeks

**B+Tree (используется в 99% баз):**
- Данные ТОЛЬКО в листовых узлах
- Внутренние узлы = только ключи-разделители
- Листья связаны в linked list → быстрые range queries
- MySQL InnoDB, PostgreSQL, SQLite используют B+Tree

**Почему B+Tree лучше для БД:**
- Больше ключей в узле (нет данных во внутренних)
- Меньше высота дерева
- Лучше для sequential access

**Параметры:**
- Page size: 4KB-16KB (типично)
- Fanout: 100-500 keys per node

### 2. LSM-Tree (Log-Structured Merge Tree) [HIGH CONFIDENCE]

**Архитектура:**
```
Write → MemTable (RAM) → Immutable MemTable → SSTable (disk)
                                                    ↓
                                              Compaction
                                                    ↓
                                          Level 0 → Level N
```

**Компоненты:**
- **MemTable:** In-memory buffer (Skip List)
- **SSTable:** Sorted String Table на диске
- **WAL:** Write-ahead log для durability
- **Bloom Filter:** Быстрая проверка существования ключа

**Compaction Strategies:**
| Strategy | Write Amp | Read Amp | Space Amp |
|----------|-----------|----------|-----------|
| Size-Tiered | Low | High | High |
| Leveled | High | Low | Low |
| Incremental | Medium | Medium | Medium |

**Используется в:** Cassandra, RocksDB, LevelDB, ScyllaDB, DynamoDB

### 3. Write-Ahead Log (WAL) [HIGH CONFIDENCE]

**Принцип:**
1. Записываем изменения в лог
2. Лог сбрасывается на диск (fsync)
3. Только потом применяем к данным

**Гарантии:**
- Durability (D в ACID)
- Crash recovery
- Point-in-time recovery

**Типы записей:**
- UNDO record: before image
- REDO record: after image
- UNDO-REDO: both

**Checkpoint:**
- Периодическая синхронизация dirty pages на диск
- Fuzzy checkpoint: не блокирует транзакции
- Сокращает время recovery

### 4. MVCC (Multi-Version Concurrency Control) [HIGH CONFIDENCE]

**Принцип:**
- Каждая транзакция видит snapshot данных
- UPDATE создаёт новую версию строки
- Старые версии сохраняются для active transactions
- Readers don't block writers, writers don't block readers

**PostgreSQL MVCC:**
- Версии хранятся в heap table
- xmin/xmax — transaction IDs
- Dead tuples требуют VACUUM

**Oracle/MySQL MVCC:**
- Версии хранятся в undo log
- Более эффективно по памяти

**Проблема PostgreSQL:**
- Bloat (накопление dead tuples)
- VACUUM необходим для очистки
- VACUUM FULL блокирует таблицу

### 5. Isolation Levels [HIGH CONFIDENCE]

| Level | Dirty Read | Non-Repeatable | Phantom | Write Skew |
|-------|------------|----------------|---------|------------|
| READ UNCOMMITTED | Да | Да | Да | Да |
| READ COMMITTED | Нет | Да | Да | Да |
| REPEATABLE READ | Нет | Нет | Да | Да |
| SNAPSHOT | Нет | Нет | Нет | Да |
| SERIALIZABLE | Нет | Нет | Нет | Нет |

**Snapshot Isolation vs Serializable:**
- SI: write sets не пересекаются → commit
- Serializable: read sets тоже проверяются
- SI допускает write skew anomaly

**PostgreSQL SSI:**
- Serializable Snapshot Isolation
- Детектирует serialization anomalies
- Меньше блокировок чем traditional serializable

### 6. Buffer Pool [HIGH CONFIDENCE]

**Назначение:**
- Кэширование страниц в RAM
- Минимизация disk I/O
- Управление dirty pages

**Ключевые концепции:**
- **Page:** 4KB-16KB логических данных
- **Frame:** Слот в памяти для страницы
- **Pin Count:** Кол-во активных ссылок
- **Dirty Bit:** Страница изменена

**Eviction Policies:**
- LRU (Least Recently Used)
- LRU-K: K последних доступов
- Clock: аппроксимация LRU
- 2Q: hot/cold queues

**Рекомендации:**
- MySQL: 80% RAM для buffer pool
- PostgreSQL: shared_buffers = 25% RAM

### 7. Locking and Deadlocks [HIGH CONFIDENCE]

**Типы блокировок:**
- Shared (S): для чтения
- Exclusive (X): для записи
- Update (U): промежуточная (read → update)
- Intent (I): намерение блокировать детей

**Гранулярность:**
- Row-level: максимум concurrency
- Page-level: компромисс
- Table-level: минимум overhead

**Предотвращение deadlock:**
- Consistent access order
- Row-versioning (MVCC)
- UPDLOCK hint
- Timeout + retry
- Reduce transaction duration

### 8. Indexes: Clustered vs Non-Clustered [HIGH CONFIDENCE]

**Clustered Index:**
- Определяет физический порядок данных
- Один на таблицу
- Обычно = PRIMARY KEY
- Leaf nodes содержат данные

**Non-Clustered Index:**
- Отдельная структура
- Можно много на таблицу
- Leaf nodes содержат указатели на данные
- Требует дополнительный lookup

**Hash Index vs B-Tree:**
| Критерий | Hash | B-Tree |
|----------|------|--------|
| Equality | O(1) | O(log n) |
| Range | ✗ | ✓ |
| ORDER BY | ✗ | ✓ |
| Partial key | ✗ | ✓ |

**Рекомендация:** B-Tree по умолчанию, Hash только для exact-match critical

### 9. Query Optimizer [HIGH CONFIDENCE]

**Cost-Based Optimizer (CBO):**
1. Query Analysis (parsing)
2. Execution Plan Generation
3. Cost Estimation (CPU, I/O)
4. Optimal Plan Selection

**Статистики:**
- Histograms: распределение значений
- Cardinality: количество уникальных значений
- Selectivity: доля выбранных строк

**Проблемы:**
- Устаревшая статистика
- Неточные cardinality estimates
- Join ordering (exponential)

**2024 Research:**
- Machine Learning для cost estimation
- Learned query optimizers
- Execution plan features

### 10. ARIES Recovery Algorithm [HIGH CONFIDENCE]

**Три принципа:**
1. Write-Ahead Logging
2. Repeating History during Redo
3. Logging changes during Undo

**Три фазы:**
1. **Analysis:** Построение Transaction Table и Dirty Page Table
2. **Redo:** Повтор всех операций с самого раннего LSN
3. **Undo:** Откат незавершённых транзакций

**Compensation Log Records (CLR):**
- Логирует undo-операции
- undoNextLSN для skip already undone
- CLR никогда не откатываются

**STEAL/NO-FORCE:**
- STEAL: dirty pages могут писаться до commit
- NO-FORCE: commit не требует flush
- Требует UNDO + REDO capabilities

### 11. Read/Write Amplification [HIGH CONFIDENCE]

**Write Amplification:**
- Соотношение физических записей к логическим
- LSM-Tree: до 50x в худшем случае
- Причина: compaction переписывает данные

**Read Amplification:**
- Количество SSTable для одного read
- LSM-Tree: нужно проверить несколько уровней
- Bloom filters снижают read amp

**Mitigation:**
- Key-value separation (50% снижение write amp)
- Tiered compaction (меньше write, больше read amp)
- Bloom filters (99%+ false-negative rate)

### 12. Bloom Filters [HIGH CONFIDENCE]

**Что это:**
- Probabilistic data structure
- Быстрая проверка "possibly in set" или "definitely not"
- Space-efficient: ~10 bits per element

**False Positive Rate:**
- 1% error: ~9.6 bits per element
- 0.1% error: ~14.4 bits per element
- Уменьшение на 10x = +4.8 bits

**Использование в БД:**
- LSM-Tree: проверка перед чтением SSTable
- Cassandra: per-SSTable bloom filters
- RocksDB: configurable per-table

### 13. Column Store vs Row Store [HIGH CONFIDENCE]

**Row Store (OLTP):**
- Строки хранятся последовательно
- Быстрый доступ к полной записи
- INSERT/UPDATE/DELETE эффективны
- MySQL, PostgreSQL, Oracle

**Column Store (OLAP):**
- Столбцы хранятся последовательно
- Отличная компрессия (однотипные данные)
- Быстрые агрегации (SUM, AVG, COUNT)
- Redshift, BigQuery, ClickHouse

**Trade-offs:**
| Операция | Row | Column |
|----------|-----|--------|
| SELECT * | ✓✓ | ✗ |
| SELECT col1, col2 | ✓ | ✓✓ |
| Aggregations | ✓ | ✓✓ |
| INSERT | ✓✓ | ✗ |

### 14. Two-Phase Commit (2PC) [HIGH CONFIDENCE]

**Фазы:**
1. **Prepare:** Coordinator → всем участникам "готовы?"
2. **Commit:** Если все "да" → commit, иначе abort

**Проблемы:**
- Blocking: если coordinator упадёт
- All-or-nothing: один node недоступен → все ждут

**Альтернативы:**
- 3PC (Three-Phase Commit)
- Paxos/Raft + 2PC для fault tolerance
- SAGA pattern для long transactions

### 15. PostgreSQL VACUUM [HIGH CONFIDENCE]

**Зачем:**
- MVCC создаёт dead tuples (old versions)
- VACUUM освобождает место
- Обновляет visibility map и statistics

**Типы:**
- VACUUM: освобождает место для reuse
- VACUUM FULL: перестраивает таблицу, возвращает место ОС (блокирует!)
- ANALYZE: обновляет статистики

**Autovacuum tuning:**
```sql
ALTER TABLE t SET (
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_scale_factor = 0.05
);
```

**Альтернативы VACUUM FULL:**
- pg_repack (online)
- pg_squeeze

---

## Community Sentiment

### B-Tree/B+Tree
**Positive:**
- "Proven technology, 40+ years"
- "Excellent for mixed workloads"
- "Universal support"

**Negative:**
- "Random I/O intensive"
- "Write amplification"

### LSM-Tree
**Positive:**
- "Great write throughput"
- "Sequential I/O"
- "Compaction is predictable"

**Negative:**
- "Read amplification can be high"
- "Space amplification with tiered"
- "Compaction can cause latency spikes"

### MVCC/PostgreSQL
**Positive:**
- "No read locks, great concurrency"
- "Well-understood"

**Negative:**
- "Bloat is real problem"
- "VACUUM can be resource-intensive"
- "Transaction ID wraparound risk"

---

## Recommendations

### When to Use B+Tree Index
- OLTP workloads
- Mixed read/write
- Range queries needed
- ORDER BY operations

### When to Use LSM-Tree
- Write-heavy workloads
- Time-series data
- Log data
- Append-mostly patterns

### When to Use Hash Index
- 100% equality lookups
- Performance-critical exact match
- No range queries ever

### Isolation Level Selection
- **READ COMMITTED:** Default, good for most OLTP
- **REPEATABLE READ:** Need consistent reads in transaction
- **SERIALIZABLE:** Financial/critical consistency

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [PlanetScale B-trees](https://planetscale.com/blog/btrees-and-database-indexes) | Tech Blog | 0.90 | B-tree internals |
| 2 | [Wikipedia LSM-Tree](https://en.wikipedia.org/wiki/Log-structured_merge-tree) | Reference | 0.85 | LSM-tree overview |
| 3 | [PostgreSQL WAL Docs](https://www.postgresql.org/docs/current/wal-intro.html) | Official | 0.95 | WAL documentation |
| 4 | [PostgreSQL MVCC](https://www.postgresql.org/docs/current/mvcc-intro.html) | Official | 0.95 | MVCC overview |
| 5 | [CMU 15-445 Buffer Pool](https://15445.courses.cs.cmu.edu/fall2024/notes/06-bufferpool.pdf) | Academic | 0.95 | Buffer management |
| 6 | [ScyllaDB Compaction](https://university.scylladb.com/courses/scylla-operations/lessons/compaction-strategies/) | Official | 0.90 | Compaction strategies |
| 7 | [SQL Server Isolation](https://learn.microsoft.com/en-us/sql/t-sql/statements/set-transaction-isolation-level-transact-sql) | Official | 0.95 | Isolation levels |
| 8 | [SQL Server Locking](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-deadlocks-guide) | Official | 0.95 | Deadlocks |
| 9 | [MS Clustered Index](https://learn.microsoft.com/en-us/sql/relational-databases/indexes/clustered-and-nonclustered-indexes-described) | Official | 0.95 | Index types |
| 10 | [CelerData CBO](https://celerdata.com/glossary/cost-based-optimizer) | Tech Blog | 0.85 | Query optimizer |
| 11 | [MySQL Checkpoint](https://dev.mysql.com/doc/refman/8.0/en/innodb-checkpoints.html) | Official | 0.95 | Checkpointing |
| 12 | [SQLpipe Hash vs B-tree](https://www.sqlpipe.com/blog/b-tree-vs-hash-index-and-when-to-use-them) | Tech Blog | 0.85 | Index comparison |
| 13 | [Medium Write Amp](https://gifted-dl.medium.com/deep-dive-on-read-write-and-space-amplification-in-ssds-and-lsm-storage-engines-and-what-makes-4a1e15fc6f0e) | Tech Blog | 0.80 | Amplification |
| 14 | [Bloom Filter Tutorial](http://llimllib.github.io/bloomfilter-tutorial/) | Educational | 0.85 | Bloom filters |
| 15 | [CMU ARIES](https://15445.courses.cs.cmu.edu/spring2024/notes/21-recovery.pdf) | Academic | 0.95 | ARIES recovery |
| 16 | [ClickHouse Column Store](https://clickhouse.com/resources/engineering/what-is-columnar-database) | Official | 0.90 | Column stores |
| 17 | [TikV 2PC](https://tikv.org/deep-dive/distributed-transaction/distributed-algorithms/) | Official | 0.90 | 2PC protocol |
| 18 | [Percona VACUUM](https://www.percona.com/blog/basic-understanding-bloat-vacuum-postgresql-mvcc/) | Tech Blog | 0.85 | VACUUM internals |
| 19 | [VLDB Cardinality](https://www.vldb.org/pvldb/vol15/p752-zhu.pdf) | Academic | 0.90 | Cardinality estimation |
| 20 | [Vlad Mihalcea MVCC](https://vladmihalcea.com/how-does-mvcc-multi-version-concurrency-control-work/) | Expert Blog | 0.90 | MVCC comparison |

---

## Research Methodology

- **Queries used:** 20 search queries covering B-tree, LSM-tree, WAL, MVCC, isolation, locking, indexes, optimizer, recovery, amplification, bloom filters, column stores, 2PC, vacuum
- **Source types:** Official documentation, academic papers (CMU), tech blogs, vendor docs
- **Coverage:** Storage engines, indexing, transactions, recovery, query processing
- **Key references:** CMU 15-445 Database Systems (2024), Database Internals by Alex Petrov
