# DATABASE DOCUMENTATION PLAN
## Комплексный план документации по базам данных

**Создано:** 2025-12-30
**Цель:** Создать максимально подробную документацию по базам данных от основ до продвинутых тем

---

## Структура плана

```
📚 DATABASES DOCUMENTATION
├── 🟢 Level 1: FUNDAMENTALS (с нуля)
│   ├── databases-what-is-database.md          ← ЧТО ТАКОЕ БД
│   ├── databases-data-storage-evolution.md    ← ЭВОЛЮЦИЯ ХРАНЕНИЯ
│   ├── databases-types-overview.md            ← ОБЗОР ВСЕХ ТИПОВ
│   └── databases-core-concepts.md             ← БАЗОВЫЕ КОНЦЕПЦИИ
│
├── 🔵 Level 2: SQL DATABASES (глубокие гайды)
│   ├── databases-postgresql-complete.md       ← PostgreSQL
│   ├── databases-mysql-complete.md            ← MySQL
│   ├── databases-sqlite-complete.md           ← SQLite (важно для mobile!)
│   └── databases-sql-advanced-patterns.md     ← Продвинутый SQL
│
├── 🟣 Level 3: NoSQL DATABASES (каждый тип отдельно)
│   ├── databases-mongodb-complete.md          ← Document DB
│   ├── databases-redis-complete.md            ← Key-Value + Cache
│   ├── databases-cassandra-scylladb.md        ← Wide-Column
│   ├── databases-neo4j-graph.md               ← Graph DB
│   ├── databases-timeseries-influx-timescale.md  ← Time-Series
│   └── databases-clickhouse-olap.md           ← OLAP/Analytics
│
├── 📱 Level 4: MOBILE DATABASES
│   ├── databases-sqlite-mobile-internals.md   ← SQLite под капотом
│   ├── databases-room-advanced-guide.md       ← Room глубоко
│   ├── databases-realm-objectbox.md           ← Альтернативы Room
│   ├── databases-mobile-sync-strategies.md    ← Синхронизация
│   └── databases-mobile-migrations.md         ← Миграции в mobile
│
├── 🤖 Level 5: AI/ML DATABASES
│   ├── [EXISTS] vector-databases-guide.md     ← Уже есть!
│   ├── [EXISTS] embeddings-complete-guide.md  ← Уже есть!
│   ├── databases-faiss-internals.md           ← FAISS под капотом
│   ├── databases-chromadb-local-ai.md         ← ChromaDB для локального AI
│   ├── databases-pinecone-weaviate-qdrant.md  ← Cloud Vector DBs
│   └── databases-embedding-storage-strategies.md ← Стратегии хранения
│
├── ⚙️ Level 6: DATABASE INTERNALS
│   ├── databases-btree-lsmtree-internals.md   ← Структуры данных
│   ├── databases-wal-write-ahead-log.md       ← Write-Ahead Log
│   ├── databases-mvcc-concurrency.md          ← Многоверсионность
│   ├── databases-query-planning.md            ← Планировщик запросов
│   └── databases-storage-engines.md           ← Storage Engines (InnoDB, RocksDB)
│
└── ☁️ Level 7: CLOUD DATABASES
    ├── databases-aws-rds-aurora.md            ← AWS managed SQL
    ├── databases-aws-dynamodb-deep.md         ← DynamoDB глубоко
    ├── databases-gcp-spanner-firestore.md     ← Google Cloud
    └── databases-azure-cosmosdb.md            ← Azure
```

---

## LEVEL 1: FUNDAMENTALS (С НУЛЯ)

### 1.1 databases-what-is-database.md
**Цель:** Объяснить что такое база данных человеку без опыта

**Содержание:**
- Что такое данные и почему их нужно хранить
- Проблема: файлы vs база данных
- История баз данных (от файлов до современных систем)
- Зачем нужна структура данных
- CRUD операции на пальцах
- Аналогии с реальным миром (картотека, библиотека)

**Deep Research запрос:**
```
"database fundamentals for beginners 2024 2025"
"what is database explained simply"
"database vs file storage advantages"
"history of databases timeline"
```

**Связи:** → databases-types-overview.md, → databases-core-concepts.md

---

### 1.2 databases-data-storage-evolution.md
**Цель:** Показать эволюцию хранения данных

**Содержание:**
- Flat files (CSV, текстовые файлы)
- Иерархические базы данных (1960s)
- Сетевые базы данных (1970s)
- Реляционные базы данных (1970s-now)
- NoSQL революция (2000s)
- NewSQL и современные гибриды
- Будущее: AI-native databases

**Deep Research запрос:**
```
"evolution of databases history timeline"
"hierarchical vs relational database"
"NoSQL movement history reasons"
"NewSQL databases comparison"
```

---

### 1.3 databases-types-overview.md
**Цель:** Полный обзор ВСЕХ типов баз данных

**Содержание:**
- Классификация по модели данных:
  - Реляционные (SQL)
  - Документные
  - Key-Value
  - Колоночные
  - Графовые
  - Time-Series
  - Векторные
- Классификация по назначению:
  - OLTP vs OLAP
  - Embedded vs Client-Server
  - In-Memory vs Persistent
  - Cloud-Native vs Self-Hosted
- Сравнительная таблица с примерами
- Decision Tree: как выбрать тип БД

**Deep Research запрос:**
```
"database types comparison 2024 2025"
"OLTP vs OLAP explained"
"when to use document vs relational database"
"embedded databases comparison SQLite Realm"
```

---

### 1.4 databases-core-concepts.md
**Цель:** Базовые концепции, общие для всех БД

**Содержание:**
- Схема (Schema) и схемалесс (Schemaless)
- Таблицы, коллекции, документы
- Первичные и внешние ключи
- Индексы: зачем и как работают (упрощённо)
- Транзакции: атомарность на пальцах
- CRUD операции
- Соединения (Joins) концептуально
- Нормализация: зачем и когда
- CAP теорема простым языком

**Deep Research запрос:**
```
"database concepts for beginners"
"primary key foreign key explained"
"database normalization explained simply"
"CAP theorem simple explanation"
```

---

## LEVEL 2: SQL DATABASES

### 2.1 databases-postgresql-complete.md
**Цель:** Полное руководство по PostgreSQL

**Содержание:**
- История и философия PostgreSQL
- Установка и настройка
- Архитектура (процессы, память, storage)
- Типы данных (включая JSON, Arrays, Ranges)
- Индексы (B-Tree, Hash, GiST, GIN, BRIN)
- Расширения (PostGIS, pg_stat_statements, pgvector)
- Репликация и High Availability
- Партиционирование
- Оптимизация производительности
- PostgreSQL vs MySQL
- Best practices 2025

**Deep Research запрос:**
```
"PostgreSQL complete guide 2024 2025"
"PostgreSQL architecture internals"
"PostgreSQL vs MySQL differences 2025"
"PostgreSQL performance tuning best practices"
"PostgreSQL extensions useful"
```

**Связи:** → databases-sql-fundamentals.md, → databases-btree-lsmtree-internals.md

---

### 2.2 databases-mysql-complete.md
**Цель:** Полное руководство по MySQL

**Содержание:**
- История MySQL и MariaDB
- Архитектура (InnoDB, MyISAM, Memory)
- Типы данных и особенности
- Индексы и оптимизация
- Репликация (Master-Slave, Group Replication)
- MySQL 8.x новые фичи
- MySQL vs PostgreSQL: когда что выбрать
- Performance tuning
- Миграция с MySQL на PostgreSQL

**Deep Research запрос:**
```
"MySQL complete guide 2024 2025"
"MySQL 8 new features"
"InnoDB vs MyISAM differences"
"MySQL replication setup"
"MySQL to PostgreSQL migration"
```

---

### 2.3 databases-sqlite-complete.md
**Цель:** Полное руководство по SQLite (критично для mobile!)

**Содержание:**
- Что такое SQLite и почему это не "игрушечная" БД
- Архитектура (B-Tree, Pager, VFS)
- SQLite vs Client-Server databases
- Ограничения и когда НЕ использовать
- Типы данных (динамическая типизация!)
- Индексы и EXPLAIN QUERY PLAN
- Транзакции и WAL mode
- FTS5 (Full-Text Search)
- JSON support
- SQLite в mobile (Android, iOS)
- SQLite в Electron/Desktop
- SQLite в embedded systems
- Performance optimization
- Encryption (SQLCipher)

**Deep Research запрос:**
```
"SQLite complete guide 2024 2025"
"SQLite architecture internals B-Tree"
"SQLite WAL mode explained"
"SQLite vs PostgreSQL when to use"
"SQLite mobile best practices"
"SQLite FTS5 tutorial"
```

**Связи:** → databases-room-advanced-guide.md, → databases-mobile-sync-strategies.md

---

### 2.4 databases-sql-advanced-patterns.md
**Цель:** Продвинутые SQL паттерны

**Содержание:**
- Window Functions глубоко
- Common Table Expressions (CTE)
- Recursive queries
- Lateral joins
- JSON операции в SQL
- Full-Text Search
- Temporal tables
- Generated columns
- Partial indexes
- Anti-patterns и как их избегать

**Deep Research запрос:**
```
"advanced SQL patterns 2024 2025"
"SQL window functions tutorial"
"recursive CTE examples"
"SQL anti-patterns common mistakes"
```

---

## LEVEL 3: NoSQL DATABASES

### 3.1 databases-mongodb-complete.md
**Цель:** Полное руководство по MongoDB

**Содержание:**
- Document model: когда это лучше реляционного
- BSON и типы данных
- Схема дизайн: embedding vs referencing
- Индексы (single, compound, multikey, text, geospatial)
- Aggregation Pipeline
- Transactions (с версии 4.0)
- Репликация (Replica Sets)
- Шардинг
- MongoDB Atlas (cloud)
- MongoDB vs PostgreSQL (JSON)
- Performance tuning
- Mongoose (Node.js ODM)
- MongoDB Compass

**Deep Research запрос:**
```
"MongoDB complete guide 2024 2025"
"MongoDB schema design patterns"
"MongoDB aggregation pipeline tutorial"
"MongoDB vs PostgreSQL JSON comparison"
"MongoDB sharding explained"
```

---

### 3.2 databases-redis-complete.md
**Цель:** Полное руководство по Redis

**Содержание:**
- In-memory data structure store
- Data types (Strings, Lists, Sets, Sorted Sets, Hashes, Streams)
- Pub/Sub messaging
- Redis as cache (patterns)
- Redis as primary database
- Persistence (RDB, AOF)
- Clustering и Sentinel
- Redis Stack (JSON, Search, Graph, TimeSeries)
- Redis vs Memcached
- Performance и memory optimization
- Use cases: sessions, rate limiting, leaderboards
- Redis в Kotlin/Java (Jedis, Lettuce)

**Deep Research запрос:**
```
"Redis complete guide 2024 2025"
"Redis data structures explained"
"Redis caching patterns"
"Redis persistence RDB vs AOF"
"Redis vs Memcached comparison"
"Redis Stack features"
```

---

### 3.3 databases-cassandra-scylladb.md
**Цель:** Wide-column databases для высоких нагрузок

**Содержание:**
- Cassandra data model (partitions, clustering keys)
- Write-optimized architecture
- Eventual consistency
- CQL (Cassandra Query Language)
- Когда использовать Cassandra
- ScyllaDB: Cassandra на C++ (быстрее!)
- Сравнение с другими NoSQL
- Data modeling best practices
- Operations и monitoring

**Deep Research запрос:**
```
"Cassandra complete guide 2024 2025"
"Cassandra data modeling best practices"
"ScyllaDB vs Cassandra comparison"
"Cassandra use cases examples"
```

---

### 3.4 databases-neo4j-graph.md
**Цель:** Graph databases и Neo4j

**Содержание:**
- Что такое графовая БД и когда нужна
- Nodes, Relationships, Properties
- Cypher query language
- Graph algorithms (PageRank, Shortest Path, Community Detection)
- Neo4j Architecture
- Neo4j Aura (cloud)
- Use cases: social networks, fraud detection, recommendations
- Neo4j vs SQL для связанных данных
- Python и Java drivers

**Deep Research запрос:**
```
"Neo4j complete guide 2024 2025"
"graph database use cases examples"
"Cypher query language tutorial"
"Neo4j vs relational database when"
"graph algorithms Neo4j"
```

---

### 3.5 databases-timeseries-influx-timescale.md
**Цель:** Time-Series databases

**Содержание:**
- Что такое time-series данные
- Зачем специализированная БД
- InfluxDB (native time-series)
- TimescaleDB (PostgreSQL extension)
- QuestDB, ClickHouse для time-series
- Data retention policies
- Downsampling и aggregation
- Grafana integration
- Use cases: IoT, monitoring, финансы

**Deep Research запрос:**
```
"time series database guide 2024 2025"
"InfluxDB vs TimescaleDB comparison"
"time series data modeling"
"IoT database selection"
```

---

### 3.6 databases-clickhouse-olap.md
**Цель:** OLAP и аналитические базы

**Содержание:**
- OLAP vs OLTP
- Columnar storage explained
- ClickHouse architecture
- MergeTree engine family
- Distributed queries
- ClickHouse vs Snowflake vs BigQuery
- Data warehouse patterns
- ETL and data pipelines
- Real-time analytics

**Deep Research запрос:**
```
"ClickHouse complete guide 2024 2025"
"OLAP database comparison"
"columnar database explained"
"ClickHouse vs Snowflake"
```

---

## LEVEL 4: MOBILE DATABASES

### 4.1 databases-sqlite-mobile-internals.md
**Цель:** SQLite под капотом для mobile разработчиков

**Содержание:**
- Как SQLite работает в Android/iOS
- File format и page structure
- B-Tree implementation
- WAL mode для concurrency
- Memory management
- Threading и connections
- Typical performance numbers
- Debugging и profiling

**Deep Research запрос:**
```
"SQLite mobile internals 2024 2025"
"SQLite B-Tree implementation"
"SQLite WAL mode mobile"
"SQLite Android performance"
```

**Связи:** → android-data-persistence.md, → databases-room-advanced-guide.md

---

### 4.2 databases-room-advanced-guide.md
**Цель:** Room глубоко — продвинутые паттерны

**Содержание:**
- Room architecture (compile-time vs runtime)
- Complex queries с @RawQuery
- TypeConverters для custom types
- Embedded objects и Relations
- Database Views
- FTS (Full-Text Search) в Room
- Prepopulated databases
- Multi-process access
- Testing Room databases
- Room + Kotlin Flow
- Room + Paging 3
- Миграции: автоматические и ручные
- Room Inspector в Android Studio
- Common mistakes и solutions

**Deep Research запрос:**
```
"Room database advanced guide 2024 2025"
"Room Android best practices"
"Room database migration strategies"
"Room Kotlin Flow integration"
"Room testing strategies"
```

**Связи:** → android-data-persistence.md, → databases-mobile-migrations.md

---

### 4.3 databases-realm-objectbox.md
**Цель:** Альтернативы Room

**Содержание:**
- Realm: object-oriented database
- Realm vs Room comparison
- ObjectBox: fast embedded database
- ObjectBox architecture
- When to choose alternatives
- Cross-platform considerations (KMP)
- Migration from Room to Realm/ObjectBox

**Deep Research запрос:**
```
"Realm database Android guide 2024 2025"
"ObjectBox vs Room comparison"
"Realm vs SQLite performance"
"cross-platform mobile database"
```

---

### 4.4 databases-mobile-sync-strategies.md
**Цель:** Синхронизация данных в mobile

**Содержание:**
- Offline-first architecture
- Conflict resolution strategies
- Sync protocols (CRDTs, OT)
- Firebase Realtime Database
- Firebase Firestore
- Supabase
- Realm Sync
- Custom sync implementations
- Background sync on Android
- Best practices

**Deep Research запрос:**
```
"mobile database sync strategies 2024 2025"
"offline first mobile architecture"
"CRDT conflict resolution"
"Firebase vs Supabase comparison"
"Realm Sync tutorial"
```

---

### 4.5 databases-mobile-migrations.md
**Цель:** Миграции баз данных в mobile

**Содержание:**
- Why migrations are critical in mobile
- Room migration strategies
- Auto-migrations vs manual
- Fallback to destructive migration
- Testing migrations
- Rollback strategies
- Schema versioning best practices

**Deep Research запрос:**
```
"Room database migration guide 2024 2025"
"mobile database migration best practices"
"SQLite migration strategies"
```

---

## LEVEL 5: AI/ML DATABASES

### 5.1 databases-faiss-internals.md
**Цель:** FAISS под капотом

**Содержание:**
- What is FAISS (Facebook AI Similarity Search)
- Index types (Flat, IVF, HNSW, PQ)
- Memory vs accuracy trade-offs
- GPU acceleration
- FAISS vs other vector libraries
- Integration with LangChain
- Production deployment

**Deep Research запрос:**
```
"FAISS internals guide 2024 2025"
"FAISS index types comparison"
"FAISS GPU performance"
"FAISS vs Milvus comparison"
```

---

### 5.2 databases-chromadb-local-ai.md
**Цель:** ChromaDB для локального AI

**Содержание:**
- ChromaDB architecture
- Embedded vs client-server mode
- Integration with LangChain, LlamaIndex
- Persistence options
- ChromaDB для desktop apps
- ChromaDB для RAG
- Limitations и when to use alternatives

**Deep Research запрос:**
```
"ChromaDB complete guide 2024 2025"
"ChromaDB LangChain integration"
"ChromaDB vs Pinecone comparison"
"local vector database options"
```

---

### 5.3 databases-pinecone-weaviate-qdrant.md
**Цель:** Cloud Vector Databases сравнение

**Содержание:**
- Pinecone (fully managed)
- Weaviate (open-source, hybrid search)
- Qdrant (Rust-based, performance)
- Milvus (distributed)
- Feature comparison table
- Pricing comparison
- When to use which
- Migration between platforms

**Deep Research запрос:**
```
"Pinecone vs Weaviate vs Qdrant 2024 2025"
"vector database comparison"
"best vector database for production"
"Milvus vs Pinecone"
```

---

### 5.4 databases-embedding-storage-strategies.md
**Цель:** Стратегии хранения embeddings

**Содержание:**
- Embedding dimensions trade-offs
- Quantization strategies
- Chunking for embeddings
- Metadata storage
- Hybrid storage (SQL + Vector)
- Cost optimization
- Caching embeddings
- Versioning embeddings

**Deep Research запрос:**
```
"embedding storage strategies 2024 2025"
"vector database cost optimization"
"embedding chunking strategies"
"hybrid search implementation"
```

---

## LEVEL 6: DATABASE INTERNALS

### 6.1 databases-btree-lsmtree-internals.md
**Цель:** Структуры данных под капотом

**Содержание:**
- B-Tree: structure and operations
- B+Tree: why databases use it
- B-Tree vs Hash index
- LSM-Tree: write-optimized structure
- Compaction strategies
- B-Tree vs LSM-Tree trade-offs
- RocksDB (LSM-based)
- LevelDB

**Deep Research запрос:**
```
"B-Tree database internals 2024"
"LSM Tree explained"
"B-Tree vs LSM Tree comparison"
"RocksDB architecture"
```

---

### 6.2 databases-wal-write-ahead-log.md
**Цель:** Write-Ahead Logging

**Содержание:**
- What is WAL and why it exists
- WAL structure
- Checkpointing
- Recovery process
- WAL in PostgreSQL
- WAL in SQLite
- Performance implications
- WAL tuning

**Deep Research запрос:**
```
"write ahead log explained 2024"
"PostgreSQL WAL internals"
"SQLite WAL mode internals"
"database recovery WAL"
```

---

### 6.3 databases-mvcc-concurrency.md
**Цель:** MVCC и конкурентный доступ

**Содержание:**
- What is MVCC (Multi-Version Concurrency Control)
- MVCC vs locking
- Snapshot isolation
- MVCC in PostgreSQL
- MVCC in MySQL (InnoDB)
- MVCC in SQLite
- Vacuum and bloat
- Deadlocks

**Deep Research запрос:**
```
"MVCC database explained 2024"
"PostgreSQL MVCC internals"
"database concurrency control"
"snapshot isolation explained"
```

---

### 6.4 databases-query-planning.md
**Цель:** Планировщик запросов

**Содержание:**
- Query parsing
- Query optimization
- Cost-based optimization
- Statistics and histograms
- EXPLAIN ANALYZE
- Execution plans
- Join algorithms (Nested Loop, Hash, Merge)
- Query hints

**Deep Research запрос:**
```
"database query planner internals 2024"
"PostgreSQL query optimization"
"EXPLAIN ANALYZE tutorial"
"join algorithms database"
```

---

### 6.5 databases-storage-engines.md
**Цель:** Storage Engines

**Содержание:**
- What is a storage engine
- InnoDB (MySQL)
- MyISAM (MySQL legacy)
- RocksDB (Facebook)
- WiredTiger (MongoDB)
- Pluggable storage engines
- Choosing the right engine

**Deep Research запрос:**
```
"database storage engine comparison 2024"
"InnoDB architecture"
"RocksDB internals"
"WiredTiger MongoDB"
```

---

## LEVEL 7: CLOUD DATABASES

### 7.1 databases-aws-rds-aurora.md
**Цель:** AWS Managed SQL Databases

**Содержание:**
- RDS overview (PostgreSQL, MySQL, MariaDB, Oracle, SQL Server)
- Aurora architecture
- Aurora Serverless v2
- Multi-AZ deployments
- Read replicas
- Performance Insights
- Pricing and cost optimization
- When to choose Aurora vs RDS

**Deep Research запрос:**
```
"AWS RDS complete guide 2024 2025"
"Aurora vs RDS comparison"
"Aurora Serverless v2 tutorial"
"AWS database cost optimization"
```

---

### 7.2 databases-aws-dynamodb-deep.md
**Цель:** DynamoDB глубоко

**Содержание:**
- DynamoDB data model
- Partition keys and sort keys
- Secondary indexes (GSI, LSI)
- Single-table design
- DynamoDB Streams
- DAX (DynamoDB Accelerator)
- On-demand vs provisioned capacity
- DynamoDB vs MongoDB
- Best practices

**Deep Research запрос:**
```
"DynamoDB complete guide 2024 2025"
"DynamoDB single table design"
"DynamoDB best practices"
"DynamoDB vs MongoDB comparison"
```

---

### 7.3 databases-gcp-spanner-firestore.md
**Цель:** Google Cloud Databases

**Содержание:**
- Cloud Spanner (globally distributed SQL)
- Cloud Firestore (document database)
- Cloud SQL (managed MySQL/PostgreSQL)
- BigQuery (data warehouse)
- Comparison and when to use which
- Pricing considerations

**Deep Research запрос:**
```
"Google Cloud Spanner guide 2024 2025"
"Firestore vs Realtime Database"
"Cloud Spanner vs Aurora"
"BigQuery tutorial"
```

---

### 7.4 databases-azure-cosmosdb.md
**Цель:** Azure Cosmos DB

**Содержание:**
- Cosmos DB multi-model
- APIs (SQL, MongoDB, Cassandra, Gremlin, Table)
- Consistency levels (5 levels)
- Global distribution
- Partitioning
- Pricing (RU/s model)
- Cosmos DB vs DynamoDB

**Deep Research запрос:**
```
"Azure Cosmos DB complete guide 2024 2025"
"Cosmos DB consistency levels"
"Cosmos DB vs DynamoDB comparison"
"Cosmos DB partitioning"
```

---

## ПОРЯДОК РЕАЛИЗАЦИИ

### Phase 1: Fundamentals (1-2 дня)
1. ✅ deep-research: "database fundamentals beginners"
2. ✅ Написать databases-what-is-database.md
3. ✅ deep-research: "database types comparison"
4. ✅ Написать databases-types-overview.md
5. ✅ Написать databases-core-concepts.md

### Phase 2: SQL Deep Dives (2-3 дня)
1. ✅ deep-research: PostgreSQL
2. ✅ Написать databases-postgresql-complete.md
3. ✅ deep-research: SQLite
4. ✅ Написать databases-sqlite-complete.md (критично для mobile!)

### Phase 3: Mobile Databases (2 дня)
1. ✅ deep-research: Room advanced
2. ✅ Написать databases-room-advanced-guide.md
3. ✅ Написать databases-mobile-sync-strategies.md

### Phase 4: NoSQL (2-3 дня)
1. ✅ deep-research: Redis, MongoDB
2. ✅ Написать по каждой технологии

### Phase 5: AI/ML Databases (1-2 дня)
1. ✅ deep-research: FAISS, ChromaDB
2. ✅ Дополнить существующие vector-databases-guide.md

### Phase 6: Internals (2 дня)
1. ✅ deep-research: B-Tree, WAL, MVCC
2. ✅ Написать технические материалы

### Phase 7: Cloud (1-2 дня)
1. ✅ deep-research: AWS, GCP, Azure databases
2. ✅ Написать облачные гайды

---

## CROSS-REFERENCES (Связи)

```
databases-what-is-database.md
    ├── → databases-types-overview.md
    └── → databases-core-concepts.md

databases-sqlite-complete.md
    ├── → databases-room-advanced-guide.md (Android)
    ├── → databases-sqlite-mobile-internals.md
    └── → databases-btree-lsmtree-internals.md

databases-room-advanced-guide.md
    ├── → android-data-persistence.md
    ├── → databases-mobile-migrations.md
    └── → databases-mobile-sync-strategies.md

vector-databases-guide.md
    ├── → embeddings-complete-guide.md
    ├── → databases-faiss-internals.md
    └── → databases-embedding-storage-strategies.md

databases-postgresql-complete.md
    ├── → databases-sql-fundamentals.md
    ├── → databases-transactions-acid.md
    └── → databases-aws-rds-aurora.md
```

---

## TEMPLATE для каждого файла

```markdown
---
title: "НАЗВАНИЕ"
created: ДАТА
modified: ДАТА
type: deep-dive
area: databases
confidence: high
tags:
  - databases
  - [SPECIFIC_TAGS]
related:
  - "[[СВЯЗАННЫЕ_ФАЙЛЫ]]"
---

# НАЗВАНИЕ

> **TL;DR:** Краткое описание в 2-3 предложениях

---

## Начнём с интуиции
[Объяснение простым языком, аналогии]

---

## Зачем это нужно
| Проблема | Без этого | С этим |
|----------|-----------|--------|
| ... | ... | ... |

---

## Основные концепции
[Подробные объяснения с примерами]

---

## Практические примеры
[Код, конфигурации, команды]

---

## Типичные ошибки
[Антипаттерны]

---

## Best Practices
[Рекомендации]

---

## Связи с другими темами
- [[ССЫЛКА]] — описание связи

---

## Источники
- [Название](URL) — описание
```

---

*Создано: 2025-12-30*
*Последнее обновление: 2025-12-30*
