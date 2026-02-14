---
title: "Database Internals: From Storage to Transactions"
type: guide
status: published
tags:
  - topic/databases
  - type/guide
  - level/advanced
related:
  - "[[databases-transactions-acid]]"
  - "[[os-file-systems]]"
  - "[[databases-fundamentals-complete]]"
modified: 2026-02-13
prerequisites:
  - "[[databases-transactions-acid]]"
  - "[[databases-fundamentals-complete]]"
  - "[[sql-databases-complete]]"
reading_time: 22
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Database Internals: From Storage to Transactions

> Глубокое погружение в механизмы работы баз данных

**Уровень:** Expert
**Время чтения:** 60 минут
**Последнее обновление:** 2025-12-30

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **SQL и реляционные БД** | Понимание что оптимизируем | [[sql-databases-complete]] |
| **Алгоритмы и структуры данных** | B-Tree, Hash Tables, Heaps | [[algorithms-fundamentals]] |
| **Операционные системы** | Файловые системы, память, I/O | [[operating-systems-basics]] |
| **Базовые транзакции** | ACID, isolation levels | [[databases-fundamentals-complete]] |

### Для кого этот материал

| Уровень | Что получите |
|---------|--------------|
| **Senior Backend** | Понимание почему одни запросы быстрые, другие медленные |
| **DBA** | Глубокое понимание tuning и troubleshooting |
| **Архитектор** | Выбор storage engine под workload |

---

## Терминология

> 💡 **Главная аналогия:**
>
> База данных = **библиотека с умным библиотекарем**. B-Tree = каталог. Buffer Pool = стол, где лежат часто читаемые книги. WAL = журнал "что выдали". MVCC = каждый читатель видит свою версию книги (копию на момент начала чтения).

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **Storage Engine** | Компонент, отвечающий за хранение данных | **Тип стеллажей** — металлические vs деревянные |
| **B-Tree / B+Tree** | Сбалансированное дерево для индексов | **Каталог библиотеки** — быстрый поиск по ключу |
| **LSM-Tree** | Log-Structured Merge Tree — append-only | **Записная книжка** — всегда пишем в конец, периодически переписываем |
| **Page** | Минимальная единица I/O (обычно 4-16KB) | **Страница в книге** — читаем/пишем целиком |
| **Buffer Pool** | Кэш страниц в RAM | **Рабочий стол** — часто нужные страницы под рукой |
| **WAL** | Write-Ahead Log — журнал перед записью | **Черновик** — сначала записал в журнал, потом в книгу |
| **MVCC** | Multi-Version Concurrency Control | **Фотокопия** — каждый читатель видит snapshot |
| **ARIES** | Алгоритм recovery: WAL + checkpoints | **Аварийное восстановление** — по журналу восстанавливаем состояние |
| **Vacuum/Compaction** | Очистка устаревших версий | **Уборка** — выбрасываем старые копии |
| **Row Store** | Хранение по строкам (OLTP) | **Картотека** — вся карточка клиента вместе |
| **Column Store** | Хранение по колонкам (OLAP) | **Реестр** — все даты рождения в одном списке |

---

## Содержание

1. [Storage Engines Overview](#storage-engines-overview)
2. [B-Tree и B+Tree](#b-tree-и-btree)
3. [LSM-Tree](#lsm-tree)
4. [Buffer Pool Management](#buffer-pool-management)
5. [Write-Ahead Log (WAL)](#write-ahead-log-wal)
6. [MVCC](#mvcc)
7. [Isolation Levels](#isolation-levels)
8. [Locking](#locking)
9. [Indexing](#indexing)
10. [Query Processing](#query-processing)
11. [Recovery (ARIES)](#recovery-aries)
12. [Distributed Transactions](#distributed-transactions)
13. [Performance Considerations](#performance-considerations)

---

## Storage Engines Overview

### Два подхода к хранению данных

```
┌─────────────────────────────────────────────────────────────────┐
│                    STORAGE ENGINE TYPES                         │
├────────────────────────────┬────────────────────────────────────┤
│         B-TREE             │           LSM-TREE                 │
│  (Page-oriented)           │  (Log-structured)                  │
├────────────────────────────┼────────────────────────────────────┤
│ • In-place updates         │ • Append-only writes               │
│ • Random I/O               │ • Sequential I/O                   │
│ • Good for mixed workloads │ • Great for write-heavy            │
│ • PostgreSQL, MySQL        │ • Cassandra, RocksDB               │
└────────────────────────────┴────────────────────────────────────┘
```

### Row Store vs Column Store

```
Row Store (OLTP):
┌────┬────────┬─────┬──────┐
│ ID │  Name  │ Age │ City │
├────┼────────┼─────┼──────┤
│ 1  │ Alice  │ 30  │ NYC  │ → Row 1 stored together
│ 2  │ Bob    │ 25  │ LA   │ → Row 2 stored together
│ 3  │ Carol  │ 35  │ SF   │ → Row 3 stored together
└────┴────────┴─────┴──────┘

Column Store (OLAP):
┌────┐ ┌────────┐ ┌─────┐ ┌──────┐
│ 1  │ │ Alice  │ │ 30  │ │ NYC  │
│ 2  │ │ Bob    │ │ 25  │ │ LA   │
│ 3  │ │ Carol  │ │ 35  │ │ SF   │
└────┘ └────────┘ └─────┘ └──────┘
  ID      Name      Age     City
  ↓        ↓         ↓       ↓
 Each column stored separately
```

**Trade-offs:**

| Операция | Row Store | Column Store |
|----------|-----------|--------------|
| SELECT * FROM t | Быстро | Медленно |
| SELECT col1 FROM t | Средне | Очень быстро |
| SUM(column) | Средне | Очень быстро |
| INSERT row | Быстро | Медленно |
| Compression | Слабая | Отличная |

---

## B-Tree и B+Tree

### B-Tree Структура

```
                    [50]                    ← Root
                   /    \
            [20, 35]    [70, 85]            ← Internal
           /   |   \    /   |   \
         [10] [25] [40] [60] [75] [90]      ← Leaves (B-Tree: данные везде)
```

**Свойства B-Tree:**
- Все листья на одной глубине (balanced)
- Минимум t-1 ключей в узле (кроме root)
- Максимум 2t-1 ключей в узле
- Fanout: количество детей = ключи + 1

### B+Tree Структура (99% баз данных)

```
                    [50]                    ← Root (только ключи)
                   /    \
            [20, 35]    [70, 85]            ← Internal (только ключи)
           /   |   \    /   |   \
         [10]→[25]→[40]→[60]→[75]→[90]      ← Leaves (данные + linked list)
          ↑         ↑         ↑
         Data      Data      Data
```

**Преимущества B+Tree:**
1. Все данные в листьях → больше ключей во внутренних узлах
2. Листья связаны → быстрые range scans
3. Меньше высота дерева
4. Более предсказуемая производительность

### Операции B+Tree

```python
# Search: O(log n)
def search(node, key):
    if node.is_leaf:
        return node.find(key)

    child = node.find_child_for(key)
    return search(child, key)

# Insert: O(log n)
def insert(node, key, value):
    leaf = find_leaf(node, key)
    leaf.insert(key, value)

    if leaf.is_overflow():
        split(leaf)  # May propagate up

# Delete: O(log n)
def delete(node, key):
    leaf = find_leaf(node, key)
    leaf.delete(key)

    if leaf.is_underflow():
        rebalance(leaf)  # Borrow or merge
```

### Page Layout

```
┌─────────────────────────────────────────────────────────┐
│                    PAGE (4KB-16KB)                       │
├─────────────────────────────────────────────────────────┤
│ Header: page_id, parent_id, prev_page, next_page        │
├─────────────────────────────────────────────────────────┤
│ Slot Array: [offset1, offset2, offset3, ...]            │
├─────────────────────────────────────────────────────────┤
│                                                         │
│                    Free Space                           │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ Tuple 3 | Tuple 2 | Tuple 1                            │
└─────────────────────────────────────────────────────────┘
```

---

## LSM-Tree

### Архитектура LSM-Tree

```
                    WRITE PATH
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│                     MemTable                            │
│                 (Skip List in RAM)                      │
│                    ~64MB                                │
└─────────────────────────────────────────────────────────┘
                        │ Flush when full
                        ▼
┌─────────────────────────────────────────────────────────┐
│                 Immutable MemTable                      │
│               (Writing to disk)                         │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ Level 0:  [SST] [SST] [SST] [SST]  (overlapping keys)  │
├─────────────────────────────────────────────────────────┤
│ Level 1:  [SST]  [SST]  [SST]      (non-overlapping)   │
├─────────────────────────────────────────────────────────┤
│ Level 2:  [SST] [SST] [SST] [SST] [SST] (10x size)     │
├─────────────────────────────────────────────────────────┤
│ Level N:  ... (each level 10x larger)                  │
└─────────────────────────────────────────────────────────┘
```

### SSTable (Sorted String Table)

```
┌─────────────────────────────────────────────────────────┐
│                      SSTable File                        │
├─────────────────────────────────────────────────────────┤
│  Data Blocks (sorted key-value pairs)                   │
│  ┌────────────────────────────────────────────────────┐ │
│  │ Block 1: [(k1,v1), (k2,v2), (k3,v3), ...]         │ │
│  │ Block 2: [(k10,v10), (k11,v11), ...]              │ │
│  │ Block N: [...]                                     │ │
│  └────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│  Index Block: [(k1, offset1), (k10, offset2), ...]     │
├─────────────────────────────────────────────────────────┤
│  Bloom Filter: [bits for probabilistic lookup]          │
├─────────────────────────────────────────────────────────┤
│  Footer: [metadata, offsets]                            │
└─────────────────────────────────────────────────────────┘
```

### Compaction Strategies

```
SIZE-TIERED COMPACTION:
Level 0: [1MB] [1MB] [1MB] [1MB] → Merge when 4 similar size
                    ↓
Level 1: [4MB] [4MB] [4MB] [4MB] → Merge when 4 similar size
                    ↓
Level 2: [16MB] ...

Pros: Low write amplification (~2-3x)
Cons: High space amplification (2x), read amplification


LEVELED COMPACTION:
Level 0: [SST] [SST] [SST] [SST]  (overlapping, merge all)
              ↓
Level 1: [SST] [SST] [SST] [SST] [SST]  (non-overlapping, 10MB each)
              ↓
Level 2: [SST] [SST] ... [SST]  (10x larger total)

Pros: Low read amplification, low space amplification (10%)
Cons: High write amplification (~10x)
```

### Read Path

```python
def read(key):
    # 1. Check MemTable
    if key in memtable:
        return memtable[key]

    # 2. Check Immutable MemTables
    for imm in immutable_memtables:
        if key in imm:
            return imm[key]

    # 3. Check SSTables (newest first)
    for level in levels:
        for sst in level.sstables_for_key(key):
            # Bloom filter check
            if not sst.bloom_filter.might_contain(key):
                continue

            # Binary search in SSTable
            if result := sst.get(key):
                return result

    return None  # Key not found
```

### Write Amplification

```
Write Amplification = Physical Writes / Logical Writes

LSM-Tree (Leveled):
- Data written to MemTable: 1x
- Flushed to Level 0: 1x
- Compacted L0 → L1: ~10x
- Compacted L1 → L2: ~10x
- ...
Total: up to 30-50x in worst case

Mitigation:
1. Key-value separation → 50% reduction
2. Tiered compaction → ~2-3x
3. Larger MemTable → fewer flushes
```

---

## Buffer Pool Management

### Buffer Pool Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                         BUFFER POOL                            │
│                    (e.g., 8GB RAM)                             │
├────────────────────────────────────────────────────────────────┤
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐       │
│  │Frame 0 │ │Frame 1 │ │Frame 2 │ │Frame 3 │ │Frame N │       │
│  │Page 42 │ │Page 17 │ │ Empty  │ │Page 99 │ │Page 55 │       │
│  │pin=2   │ │pin=0   │ │        │ │pin=1   │ │pin=0   │       │
│  │dirty=1 │ │dirty=0 │ │        │ │dirty=1 │ │dirty=0 │       │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘       │
├────────────────────────────────────────────────────────────────┤
│  Page Table: {page_id → frame_id}                              │
│  Free List: [2, ...]                                           │
└────────────────────────────────────────────────────────────────┘
```

### Page Table Entry

```c
struct PageTableEntry {
    page_id_t page_id;
    frame_id_t frame_id;
    int pin_count;        // Active references
    bool is_dirty;        // Modified since read
    timestamp_t last_access;
};
```

### Eviction Policies

```
LRU (Least Recently Used):
┌─────┬─────┬─────┬─────┬─────┐
│ MRU │     │     │     │ LRU │ ← Evict from here
└─────┴─────┴─────┴─────┴─────┘
  ↑
  New accesses go here

Problems:
- Sequential scan pollution (one scan evicts hot pages)
- Not cache-efficient

LRU-K:
- Track K most recent accesses per page
- Evict based on K-th access time
- K=2 commonly used

Clock (Second Chance):
┌─────┐
│  1  │ ← reference bit
│  0  │
│  1  │ ← clock hand
│  0  │ ← evict
│  1  │
└─────┘
```

### MySQL InnoDB Buffer Pool

```sql
-- Check buffer pool size
SHOW VARIABLES LIKE 'innodb_buffer_pool_size';

-- Recommended: 70-80% of RAM for dedicated server
SET GLOBAL innodb_buffer_pool_size = 8589934592;  -- 8GB

-- Check buffer pool stats
SHOW STATUS LIKE 'Innodb_buffer_pool%';
```

---

## Write-Ahead Log (WAL)

### WAL Principle

```
         BEFORE                          AFTER
    ┌────────────────┐             ┌────────────────┐
    │   User Data    │             │   User Data    │
    │                │             │                │
    │  (modified     │             │  (NOT YET      │
    │   in memory)   │             │   on disk)     │
    └────────────────┘             └────────────────┘
            │                              │
            │                              │
            ▼                              │
    ┌────────────────┐                     │
    │   WAL Log      │ ◄──────────────────┘
    │  (on disk)     │     Log FIRST, then data
    │                │
    │  DURABLE       │
    └────────────────┘
```

### WAL Record Types

```
UNDO-ONLY Record:
┌────────────────────────────────────────────────┐
│ LSN | TxnID | Type | PageID | Offset | Before │
└────────────────────────────────────────────────┘
Used for: Rollback

REDO-ONLY Record:
┌────────────────────────────────────────────────┐
│ LSN | TxnID | Type | PageID | Offset | After  │
└────────────────────────────────────────────────┘
Used for: Crash recovery

UNDO-REDO Record:
┌─────────────────────────────────────────────────────────┐
│ LSN | TxnID | Type | PageID | Offset | Before | After  │
└─────────────────────────────────────────────────────────┘
Used for: Both (most common)
```

### Log Sequence Number (LSN)

```
Every log record has unique LSN:

WAL: [LSN=1, ...] [LSN=2, ...] [LSN=3, ...] [LSN=4, ...]
                        ↑
                   flushedLSN (last durable)

Page: [pageLSN=3]  ← Last modification LSN

Rule: Page can be written to disk only if pageLSN <= flushedLSN
```

### Checkpoint

```
                    Active Transactions
                    ┌─────────────────┐
──────────────────┬─┴─────────────────┴─┬────────────────────
                  │                     │
             Checkpoint            Crash
                  │                     │
                  └── Recovery starts here (not from beginning)

Types:
1. Consistent Checkpoint: Pause all, flush all, resume (blocking)
2. Fuzzy Checkpoint: Flush incrementally while running (InnoDB)
3. Non-blocking Checkpoint: Copy-on-write dirty pages
```

---

## MVCC

### MVCC Concept

```
Transaction T1 (READ):              Transaction T2 (WRITE):
    │                                    │
    │  SELECT balance                    │  UPDATE balance = 200
    │  FROM accounts                     │  WHERE id = 1
    │  WHERE id = 1                      │
    │                                    │
    ▼                                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    MVCC Storage                              │
├─────────────────────────────────────────────────────────────┤
│  Row versions:                                              │
│  [id=1, balance=100, xmin=5, xmax=10]  ← old (for T1)      │
│  [id=1, balance=200, xmin=10, xmax=∞]  ← new (for T2)      │
└─────────────────────────────────────────────────────────────┘
                        │
                        ▼
              T1 sees balance=100 (consistent snapshot)
              T2 sees balance=200 (own changes)
```

### PostgreSQL MVCC

```
Tuple Header:
┌─────────────────────────────────────────────────────────────┐
│ xmin: transaction that created this version                │
│ xmax: transaction that deleted/updated (0 if active)       │
│ ctid: physical location of next version                    │
│ infomask: visibility hints                                 │
└─────────────────────────────────────────────────────────────┘

Visibility Check:
1. Is xmin committed? If not, invisible (unless own transaction)
2. Is xmax set and committed? If yes, invisible (deleted)
3. Is xmax my transaction? If yes, invisible (I deleted it)
```

### Dead Tuples and VACUUM

```
Before UPDATE:
┌─────────────────────────────────────────────────┐
│ [id=1, value='old', xmin=10, xmax=∞]  LIVE    │
└─────────────────────────────────────────────────┘

After UPDATE (Txn 20):
┌─────────────────────────────────────────────────┐
│ [id=1, value='old', xmin=10, xmax=20]  DEAD   │ ← Dead tuple
│ [id=1, value='new', xmin=20, xmax=∞]   LIVE   │
└─────────────────────────────────────────────────┘

After VACUUM:
┌─────────────────────────────────────────────────┐
│ [FREE SPACE]                                   │ ← Reclaimed
│ [id=1, value='new', xmin=20, xmax=∞]   LIVE   │
└─────────────────────────────────────────────────┘
```

### Autovacuum Tuning

```sql
-- Default: triggers at 50 + 20% dead tuples
-- For 1M row table: 50 + 200,000 = 200,050 dead tuples!

-- More aggressive per-table settings
ALTER TABLE high_update_table SET (
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_scale_factor = 0.05,  -- 5% instead of 20%
    autovacuum_analyze_threshold = 50,
    autovacuum_analyze_scale_factor = 0.02
);

-- Monitor bloat
SELECT schemaname, tablename,
       n_dead_tup, n_live_tup,
       round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

---

## Isolation Levels

### Anomalies

```
DIRTY READ:
T1: WRITE(x=10)
T2:                READ(x) → 10
T1: ABORT          ← T2 saw uncommitted data!

NON-REPEATABLE READ:
T1: READ(x) → 5
T2:                WRITE(x=10), COMMIT
T1: READ(x) → 10   ← Same query, different result!

PHANTOM READ:
T1: SELECT COUNT(*) WHERE age > 30 → 5
T2:                INSERT (age=35), COMMIT
T1: SELECT COUNT(*) WHERE age > 30 → 6  ← New row appeared!

WRITE SKEW:
T1: READ(doctor_count) → 2
T2: READ(doctor_count) → 2
T1: IF count > 1: DELETE doctor1
T2: IF count > 1: DELETE doctor2
Both commit → 0 doctors! (constraint violated)
```

### Isolation Levels Matrix

| Level | Dirty Read | Non-Repeatable | Phantom | Write Skew |
|-------|------------|----------------|---------|------------|
| READ UNCOMMITTED | Possible | Possible | Possible | Possible |
| READ COMMITTED | No | Possible | Possible | Possible |
| REPEATABLE READ | No | No | Possible* | Possible |
| SNAPSHOT | No | No | No | Possible |
| SERIALIZABLE | No | No | No | No |

*PostgreSQL's REPEATABLE READ is actually Snapshot Isolation (no phantoms)

### Implementation

```sql
-- PostgreSQL
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- Uses SSI (Serializable Snapshot Isolation)

-- MySQL
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- Uses gap locks to prevent phantoms

-- Check current level
SHOW TRANSACTION ISOLATION LEVEL;  -- PostgreSQL
SELECT @@transaction_isolation;    -- MySQL
```

---

## Locking

### Lock Types

```
SHARED (S) Lock:
┌─────────────────────────────────────────────────┐
│  Multiple transactions can hold S lock          │
│  Prevents X lock acquisition                    │
│  Used for: SELECT                               │
└─────────────────────────────────────────────────┘

EXCLUSIVE (X) Lock:
┌─────────────────────────────────────────────────┐
│  Only one transaction can hold X lock           │
│  Prevents both S and X locks                    │
│  Used for: INSERT, UPDATE, DELETE               │
└─────────────────────────────────────────────────┘

UPDATE (U) Lock:
┌─────────────────────────────────────────────────┐
│  Read now, write later                          │
│  Compatible with S, not with X or U             │
│  Prevents deadlock in update patterns           │
└─────────────────────────────────────────────────┘
```

### Lock Compatibility Matrix

|   | S | U | X |
|---|---|---|---|
| S | ✓ | ✓ | ✗ |
| U | ✓ | ✗ | ✗ |
| X | ✗ | ✗ | ✗ |

### Deadlock Detection

```
Deadlock:
T1: LOCK(A), wants LOCK(B)
         ↓
         Waits for T2
              ↓
T2: LOCK(B), wants LOCK(A)
         ↓
         Waits for T1
              ↓
         CYCLE DETECTED!

Resolution:
1. Choose victim (youngest, smallest, or random)
2. Abort victim transaction
3. Release locks
4. Victim retries
```

### Prevention Strategies

```python
# 1. Consistent lock ordering
def transfer(from_acct, to_acct, amount):
    # Always lock in ascending order
    first, second = sorted([from_acct, to_acct])

    with lock(first):
        with lock(second):
            # Transfer logic

# 2. Lock timeout
SET lock_timeout = '5s';

# 3. Reduce transaction scope
# Bad: Long transaction
BEGIN;
-- lots of work
SELECT * FROM big_table FOR UPDATE;
-- more work
COMMIT;

# Good: Short transaction
-- do preparation work outside transaction
BEGIN;
SELECT * FROM big_table FOR UPDATE;
-- minimal work
COMMIT;
```

---

## Indexing

### Index Types

```
B+TREE INDEX (default):
├── Equality: WHERE id = 5         ✓ O(log n)
├── Range: WHERE age BETWEEN 20 AND 30  ✓
├── Prefix: WHERE name LIKE 'John%'     ✓
├── ORDER BY                             ✓
└── MIN/MAX                              ✓

HASH INDEX:
├── Equality: WHERE id = 5         ✓ O(1)
├── Range: WHERE age BETWEEN 20 AND 30  ✗
├── ORDER BY                             ✗
└── Use case: Primary key exact lookups

GIN INDEX (Generalized Inverted):
├── Full-text search                     ✓
├── JSONB containment (@>)               ✓
├── Array operations                     ✓
└── Use case: Document search

GIST INDEX (Generalized Search Tree):
├── Geometric types                      ✓
├── Range types                          ✓
├── Full-text search                     ✓
└── Use case: PostGIS, nearest neighbor
```

### Clustered vs Non-Clustered

```
CLUSTERED INDEX:
┌─────────────────────────────────────────────────────────────┐
│ Index = Data (physically sorted by index key)               │
│                                                             │
│ Root → Internal → Leaf (contains actual rows)              │
│                                                             │
│ One per table (usually PRIMARY KEY)                         │
└─────────────────────────────────────────────────────────────┘

NON-CLUSTERED INDEX:
┌─────────────────────────────────────────────────────────────┐
│ Index → Pointer → Data                                      │
│                                                             │
│ Root → Internal → Leaf (contains pointers to rows)         │
│                                                             │
│ Many per table                                              │
└─────────────────────────────────────────────────────────────┘

Lookup cost:
- Clustered: 1 lookup (data in index)
- Non-clustered: 2 lookups (index + heap/clustered key)
```

### Covering Index

```sql
-- Query
SELECT email FROM users WHERE id = 5;

-- Non-covering index
CREATE INDEX idx_id ON users(id);
-- Lookup: idx_id → heap → email

-- Covering index (includes all needed columns)
CREATE INDEX idx_id_email ON users(id) INCLUDE (email);
-- Lookup: idx_id_email → done! (no heap access)
```

### Index Selectivity

```sql
-- High selectivity (good for indexing)
-- email: mostly unique values
CREATE INDEX idx_email ON users(email);

-- Low selectivity (often not useful)
-- gender: only 2-3 distinct values
CREATE INDEX idx_gender ON users(gender);  -- Often ignored by optimizer

-- Check selectivity
SELECT
    attname,
    n_distinct,
    most_common_vals
FROM pg_stats
WHERE tablename = 'users';
```

---

## Query Processing

### Query Processing Pipeline

```
SQL Query
    │
    ▼
┌────────────┐
│   Parser   │ → Syntax tree (AST)
└────────────┘
    │
    ▼
┌────────────┐
│  Analyzer  │ → Resolved names, types
└────────────┘
    │
    ▼
┌────────────┐
│  Rewriter  │ → Views expanded, rules applied
└────────────┘
    │
    ▼
┌────────────┐
│ Optimizer  │ → Execution plan (cheapest)
└────────────┘
    │
    ▼
┌────────────┐
│  Executor  │ → Results
└────────────┘
```

### Cost-Based Optimizer

```
Query: SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id
       WHERE c.country = 'USA'

Plan A: Nested Loop
  → Seq Scan on customers (filter: country='USA')
    → Index Scan on orders (customer_id)
Cost: 10000

Plan B: Hash Join
  → Hash (customers, filter: country='USA')
  → Seq Scan on orders
Cost: 5000  ← Winner!

Plan C: Merge Join
  → Sort (customers)
  → Sort (orders)
Cost: 15000
```

### EXPLAIN ANALYZE

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 42;

                                     QUERY PLAN
─────────────────────────────────────────────────────────────────────────────
 Index Scan using orders_customer_id_idx on orders
   (cost=0.43..8.45 rows=1 width=64)
   (actual time=0.023..0.024 rows=1 loops=1)
   Index Cond: (customer_id = 42)
   Buffers: shared hit=4
 Planning Time: 0.107 ms
 Execution Time: 0.040 ms

Key metrics:
- cost: estimated (startup..total)
- actual time: real execution (ms)
- rows: estimated vs actual
- Buffers: pages read (hit=cache, read=disk)
```

### Join Algorithms

```
NESTED LOOP JOIN:
for each row r1 in R1:
    for each row r2 in R2:
        if r1.key == r2.key:
            emit(r1, r2)

Cost: O(n × m)
Best when: inner table small or indexed


HASH JOIN:
# Build phase
for each row r2 in R2:
    hash_table[hash(r2.key)] = r2

# Probe phase
for each row r1 in R1:
    for each r2 in hash_table[hash(r1.key)]:
        if r1.key == r2.key:
            emit(r1, r2)

Cost: O(n + m)
Best when: fits in memory


MERGE JOIN:
# Both must be sorted
while not end of R1 or R2:
    if r1.key < r2.key:
        advance R1
    elif r1.key > r2.key:
        advance R2
    else:
        emit all matches
        advance both

Cost: O(n log n + m log m) or O(n + m) if pre-sorted
Best when: already sorted or ORDER BY needed
```

---

## Recovery (ARIES)

### ARIES Algorithm

```
                        CRASH!
                           │
 WAL: [──────────────────]─┤
      ↑                    ↑
 Checkpoint            Log end

RECOVERY PHASES:

1. ANALYSIS PHASE
   ┌────────────────────────────────────────────────────────┐
   │ Scan log from checkpoint to end                       │
   │ Build: - Active Transaction Table (ATT)               │
   │        - Dirty Page Table (DPT)                       │
   │ Output: Redo start point, transactions to undo        │
   └────────────────────────────────────────────────────────┘

2. REDO PHASE (History Repeating)
   ┌────────────────────────────────────────────────────────┐
   │ For each update record from redo start:               │
   │   if page dirty and pageLSN < recordLSN:              │
   │     REDO the operation                                │
   │                                                       │
   │ Goal: Bring database to crash state                   │
   └────────────────────────────────────────────────────────┘

3. UNDO PHASE (Atomicity)
   ┌────────────────────────────────────────────────────────┐
   │ For each active transaction (in ATT):                 │
   │   Walk back through log (using prevLSN)               │
   │   UNDO each operation                                 │
   │   Write CLR (Compensation Log Record)                 │
   │                                                       │
   │ Goal: Rollback uncommitted transactions               │
   └────────────────────────────────────────────────────────┘
```

### Compensation Log Record (CLR)

```
CLR Purpose:
- Records undo actions
- Has undoNextLSN pointing to next record to undo
- CLRs are NEVER undone (prevents infinite loops)

Example:
Original: [LSN=5, UPDATE A, prevLSN=3]
Undo:     [LSN=10, CLR(undo LSN=5), undoNextLSN=3]
          ↑                           ↑
        This operation         Skip to here if crash during undo
```

### STEAL/NO-FORCE

```
STEAL Policy (dirty pages CAN be flushed before commit):
+ Better buffer management
- Requires UNDO capability

NO-FORCE Policy (commit doesn't require flushing):
+ Faster commits
- Requires REDO capability

ARIES uses STEAL + NO-FORCE:
→ Needs both UNDO and REDO
→ Maximum flexibility
→ Best performance
```

---

## Distributed Transactions

### Two-Phase Commit (2PC)

```
            COORDINATOR
                │
        ┌───────┼───────┐
        │       │       │
        ▼       ▼       ▼
    PARTICIPANT PARTICIPANT PARTICIPANT
        A           B           C

PHASE 1: PREPARE
Coordinator → All: "Prepare to commit TX1"
A, B, C → Coordinator: "Ready" / "Abort"

PHASE 2: COMMIT
If all "Ready":
  Coordinator → All: "Commit"
  All → Coordinator: "Committed"
Else:
  Coordinator → All: "Abort"
  All → Coordinator: "Aborted"
```

### 2PC Problems

```
BLOCKING:
If coordinator crashes after PREPARE:
├── Participants holding locks
├── Can't commit or abort
└── Wait indefinitely

SOLUTION 1: 3PC (Three-Phase Commit)
├── Adds PRE-COMMIT phase
└── Reduces blocking window

SOLUTION 2: Paxos/Raft + 2PC
├── Replicated coordinator
├── Replicated participants
└── High availability

SOLUTION 3: SAGA Pattern
├── Local transactions + compensating actions
├── No global locks
└── Better for microservices
```

---

## Performance Considerations

### Amplification Metrics

```
Write Amplification (WA):
= Physical bytes written / Logical bytes written

LSM-Tree: 10-50x (leveled compaction)
B-Tree: 2-3x (in-place updates, but WAL + pages)

Read Amplification (RA):
= Physical reads / Logical reads

LSM-Tree: 1-10x (depends on levels)
B-Tree: 1-3x (index + data pages)

Space Amplification (SA):
= Physical space / Logical data size

LSM-Tree (tiered): 2x
LSM-Tree (leveled): 1.1x
B-Tree: ~2x (page utilization)
```

### Bloom Filter Optimization

```python
# False positive probability formula
# p = (1 - e^(-kn/m))^k
# Where:
#   m = number of bits
#   n = number of elements
#   k = number of hash functions

# Optimal k
k_optimal = (m/n) * ln(2)

# For 1% false positive rate:
# m/n ≈ 9.6 bits per element
# k ≈ 7 hash functions

# Example: 1M elements, 1% FP
bits_needed = 1_000_000 * 9.6  # ≈ 9.6 MB
```

### Performance Tuning Checklist

```
POSTGRESQL:
□ shared_buffers = 25% RAM
□ effective_cache_size = 75% RAM
□ work_mem = RAM / (max_connections * 4)
□ maintenance_work_mem = RAM / 8
□ random_page_cost = 1.1 for SSD
□ Enable huge pages

MYSQL:
□ innodb_buffer_pool_size = 70-80% RAM
□ innodb_log_file_size = 1-2GB
□ innodb_flush_log_at_trx_commit = 2 (if durability can be relaxed)
□ innodb_io_capacity = match your SSD IOPS

INDEXES:
□ Index frequently filtered columns
□ Use covering indexes for hot queries
□ Avoid over-indexing (slows writes)
□ Monitor unused indexes

QUERIES:
□ Use EXPLAIN ANALYZE
□ Avoid SELECT *
□ Batch inserts
□ Use prepared statements
```

---

## Полезные ресурсы

### Книги
- **Database Internals** by Alex Petrov — must-read
- **Designing Data-Intensive Applications** by Martin Kleppmann
- **Transaction Processing** by Jim Gray

### Курсы
- CMU 15-445 Database Systems (Andy Pavlo)
- Berkeley CS186 Introduction to Database Systems

### Документация
- [PostgreSQL Internals](https://www.postgresql.org/docs/current/internals.html)
- [MySQL InnoDB Architecture](https://dev.mysql.com/doc/refman/8.0/en/innodb-architecture.html)
- [SQLite File Format](https://sqlite.org/fileformat.html)

## Связь с другими темами

[[databases-transactions-acid]] — Транзакции и ACID-свойства рассматриваются на прикладном уровне, тогда как данный документ показывает их внутреннюю реализацию: WAL обеспечивает Durability и Atomicity, MVCC реализует Isolation, а ARIES-алгоритм гарантирует Recovery. Рекомендуется сначала освоить ACID на уровне использования, затем углубиться в механизмы через этот материал.

[[os-file-systems]] — Файловые системы ОС лежат в основе storage engine: страницы (pages) являются единицей I/O, fsync обеспечивает durability, а mmap используется для memory-mapped файлов. Понимание работы файловой системы помогает осознать, почему sequential I/O (LSM-Tree) быстрее random I/O (B-Tree) и как buffer pool оптимизирует доступ к данным.

[[databases-fundamentals-complete]] — Фундаментальные концепции баз данных (индексы, нормализация, типы запросов) описывают «что» делает СУБД, тогда как internals объясняют «как» это реализовано под капотом. Знание фундамента помогает задавать правильные вопросы: почему этот запрос медленный? почему нужен vacuum? почему isolation level влияет на производительность?

[[sql-databases-complete]] — Практическое использование PostgreSQL, MySQL и SQLite подкрепляется пониманием их internal-механизмов: почему EXPLAIN ANALYZE показывает определённый план, как работает connection pooling, почему partitioning ускоряет запросы. Этот материал даёт теоретическую базу для осознанной оптимизации SQL-запросов.

## Источники и дальнейшее чтение

- Petrov A. (2019). *Database Internals*. — Основной источник по теме: storage engines (B-Tree, LSM-Tree), buffer management, WAL, distributed transactions. Must-read для глубокого понимания работы СУБД.
- Kleppmann M. (2017). *Designing Data-Intensive Applications*. — Главы о storage и retrieval, репликации, партиционировании. Связывает internal-механизмы с архитектурными решениями для data-intensive систем.
- Garcia-Molina H., Ullman J.D., Widom J. (2008). *Database Systems: The Complete Book*. — Академический учебник с формальным описанием query processing, concurrency control (2PL, MVCC), recovery (ARIES). Необходим для глубокого понимания алгоритмов.

---

---

## Проверь себя

> [!question]- Почему B-Tree остаётся основной структурой данных для индексов в OLTP, несмотря на появление LSM-Tree?
> B-Tree оптимален для read-heavy нагрузок: поиск за O(log N) с предсказуемой latency, эффективные range scans благодаря linked leaf nodes. LSM-Tree лучше для write-heavy: writes идут в memtable (RAM), затем flush на диск как отсортированные SSTable. Но LSM-Tree требует compaction (read/write amplification) и reads могут проверять несколько уровней. OLTP-системы обычно read-heavy, поэтому B-Tree выигрывает.

> [!question]- Как WAL обеспечивает durability и atomicity одновременно?
> WAL записывает изменения в журнал ДО записи в data pages. При сбое: если WAL-запись есть, но data page не обновлена — redo (повторить). Если транзакция не была закоммичена — undo (откатить). Atomicity: незаконченная транзакция откатывается при recovery. Durability: закоммиченная транзакция всегда восстановима из WAL.

> [!question]- Почему MVCC лучше двухфазной блокировки (2PL) для типичных OLTP-нагрузок?
> 2PL блокирует строки при чтении и записи — readers блокируют writers и наоборот, throughput падает при конкуренции. MVCC позволяет читать старую версию строки без блокировки — readers никогда не ждут writers. Это критично для OLTP, где 80-95% операций — чтение. Цена MVCC: хранение нескольких версий и необходимость garbage collection (VACUUM).

> [!question]- Чем отличается Buffer Pool от кэша операционной системы?
> Buffer Pool — управляемый СУБД кэш страниц в RAM. СУБД знает паттерны доступа: pin pages для активных транзакций, clock/LRU replacement, prefetch для sequential scan. OS cache — generic, не знает семантики запросов. Поэтому PostgreSQL использует double buffering (свой buffer pool + OS cache), а MySQL/InnoDB отключает OS cache (O_DIRECT) для полного контроля.

---

## Ключевые карточки

Что такое B-Tree и как он ускоряет поиск?
?
Сбалансированное дерево, где все leaf nodes на одной глубине. Поиск за O(log N) — дерево глубиной 3-4 покрывает миллионы записей. Leaf nodes связаны в linked list для эффективных range scans. Стандартный индекс в PostgreSQL и MySQL.

Чем B-Tree отличается от LSM-Tree?
?
B-Tree: update-in-place, быстрое чтение, медленная запись (random I/O). LSM-Tree: append-only, быстрая запись (sequential I/O), read amplification из-за нескольких уровней + compaction. B-Tree — PostgreSQL, MySQL. LSM-Tree — Cassandra, RocksDB, LevelDB.

Что такое WAL (Write-Ahead Log)?
?
Журнал изменений, записываемый ДО изменения data pages. Обеспечивает durability (данные не потеряются при сбое) и atomicity (незаконченные транзакции откатываются при recovery). Основа PITR и streaming replication.

Что такое Buffer Pool Manager?
?
Компонент СУБД, управляющий кэшем страниц в RAM. Загружает pages с диска по требованию, использует replacement policy (LRU/Clock), управляет dirty pages (изменённые, но не сброшенные на диск). Ключевой для производительности — RAM vs Disk.

Как работает VACUUM в PostgreSQL?
?
MVCC создаёт мёртвые версии строк (deleted/updated). VACUUM отмечает их свободными для переиспользования. Autovacuum запускается автоматически. Без vacuum — table bloat (таблица растёт, запросы замедляются). VACUUM FULL — полная перезапись таблицы.

Что такое page (страница) в контексте СУБД?
?
Минимальная единица I/O между диском и памятью. PostgreSQL: 8 KB, MySQL: 16 KB. Страница содержит несколько строк. Один read = одна страница, даже если нужна одна строка. Поэтому sequential scan может быть быстрее, чем index scan для большой доли таблицы.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[databases-replication-sharding]] | Как internal-механизмы работают в распределённых системах |
| Углубиться | [[databases-transactions-acid]] | ACID-свойства на прикладном уровне |
| Смежная тема | [[os-file-systems]] | Файловые системы, fsync, I/O scheduling — основа storage engine |
| Смежная тема | [[os-memory-management]] | Виртуальная память, mmap, page cache |
| Обзор | [[databases-overview]] | Вернуться к карте раздела |

---

*Документ создан: 2025-12-30*
*На основе deep research (20+ источников)*
