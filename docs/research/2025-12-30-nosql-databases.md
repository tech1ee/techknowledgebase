---
title: "Research Report: NoSQL Databases"
created: 2025-12-30
modified: 2025-12-30
type: reference
status: draft
tags:
  - topic/databases
  - topic/nosql
---

# Research Report: NoSQL Databases

**Date:** 2025-12-30
**Sources Evaluated:** 20+
**Research Depth:** Deep (comprehensive multi-source analysis)

## Executive Summary

NoSQL базы данных — это нереляционные СУБД, оптимизированные для горизонтального масштабирования и гибких схем данных. Четыре основных типа: Document (MongoDB), Key-Value (Redis), Wide-Column (Cassandra), Graph (Neo4j). Ключевые концепции: BASE vs ACID, eventual consistency, sharding, replication. MongoDB лидирует в document stores (гибкая схема, ACID с 4.0), Redis — стандарт для caching (sub-millisecond latency), Cassandra — для write-heavy workloads, DynamoDB — serverless на AWS. Тренды 2024-2025: многие NoSQL добавляют ACID транзакции, PostgreSQL улучшает JSON-возможности, гибридные решения становятся нормой.

---

## Key Findings

### 1. Типы NoSQL баз данных [HIGH CONFIDENCE]

| Тип | Примеры | Модель данных | Use Cases |
|-----|---------|---------------|-----------|
| Document | MongoDB, CouchDB, Firestore | JSON/BSON документы | CMS, e-commerce, гибкие схемы |
| Key-Value | Redis, Memcached, DynamoDB | Key → Value pairs | Caching, sessions, real-time |
| Wide-Column | Cassandra, ScyllaDB, HBase | Column families | Time-series, IoT, write-heavy |
| Graph | Neo4j, Amazon Neptune | Nodes + Relationships | Social networks, recommendations |
| Time-Series | InfluxDB, TimescaleDB | Time-indexed data | Metrics, monitoring, IoT |
| Search Engine | Elasticsearch | Inverted index | Full-text search, logs |

### 2. BASE vs ACID [HIGH CONFIDENCE]

**ACID (SQL databases):**
- Atomicity — всё или ничего
- Consistency — валидное состояние
- Isolation — транзакции изолированы
- Durability — данные сохранены

**BASE (NoSQL databases):**
- Basic Availability — данные доступны большую часть времени
- Soft State — реплики не всегда consistent
- Eventual Consistency — данные станут consistent "когда-нибудь"

**Важно:** Многие NoSQL теперь поддерживают ACID:
- MongoDB 4.0+ — multi-document ACID transactions
- DynamoDB — ACID transactions across tables
- Aerospike 8.0 (2025) — strict serializable ACID

### 3. MongoDB Deep Dive [HIGH CONFIDENCE]

**Архитектура:**
- Document store с BSON (Binary JSON)
- Flexible schema — можно добавлять поля без миграций
- Replica sets для high availability
- Sharding для horizontal scaling

**Ключевые особенности:**
- Multi-document ACID transactions (4.0+)
- Aggregation pipeline для complex queries
- Atlas — managed cloud service
- Change Streams для real-time updates

**Когда использовать:**
- Flexible schemas, evolving data
- Complex queries на документах
- E-commerce, CMS, social networks
- Rapid prototyping

**Когда НЕ использовать:**
- Complex joins между коллекциями
- Strict consistency requirements
- Heavy analytics (SQL лучше)

### 4. Redis Deep Dive [HIGH CONFIDENCE]

**Характеристики:**
- In-memory key-value store
- Sub-millisecond latency
- Rich data structures: Strings, Lists, Sets, Sorted Sets, Hashes, Streams
- Persistence: RDB snapshots, AOF logs

**Use Cases:**
- **Caching** — most common, 10-100x faster than DB
- **Session storage** — shared sessions across servers
- **Pub/Sub** — real-time messaging
- **Rate limiting** — API throttling
- **Leaderboards** — sorted sets
- **Queues** — lists as message queues

**Redis vs Memcached:**
| Критерий | Redis | Memcached |
|----------|-------|-----------|
| Data structures | Rich (lists, sets, hashes) | Simple (strings only) |
| Persistence | RDB + AOF | None |
| Pub/Sub | Yes | No |
| Threading | Single-threaded | Multi-threaded |
| Transactions | Yes | No |
| Licensing | AGPL (8.0+) | BSD |

**Рекомендация 2024-2025:** Redis для большинства проектов. Memcached только для extreme simplicity.

### 5. Cassandra Deep Dive [HIGH CONFIDENCE]

**Архитектура:**
- Wide-column store
- Distributed, no single point of failure
- Consistent hashing (ring topology)
- Tunable consistency levels

**Особенности:**
- Write-optimized (LSM-Tree storage)
- Linear scalability
- CQL (Cassandra Query Language) — SQL-like
- Eventual consistency by default

**Когда использовать:**
- Write-heavy workloads
- Time-series data
- Geographically distributed systems
- High availability requirements

**ScyllaDB vs Cassandra:**
- ScyllaDB: C++ (no GC stalls), 10x throughput
- 10x fewer nodes, 75% lower TCO
- Drop-in replacement для Cassandra

### 6. DynamoDB [HIGH CONFIDENCE]

**Архитектура:**
- Fully managed AWS service
- Key-value + Document models
- Auto-scaling (provisioned or on-demand)
- Global tables для multi-region

**Single Table Design:**
- Один table для всех entities
- GSI (Global Secondary Indexes) для access patterns
- Requires upfront data modeling
- Optimized для known query patterns

**Когда использовать:**
- AWS ecosystem
- Serverless applications
- Predictable, known access patterns
- Real-time, low-latency requirements

**Trade-offs:**
- Vendor lock-in
- Complex data modeling
- Max 2 consumers на DynamoDB Stream

### 7. Neo4j Graph Database [HIGH CONFIDENCE]

**Архитектура:**
- Property graph model
- Nodes, Relationships, Properties
- Cypher query language (GQL-compliant 2024)
- ACID compliant

**Cypher примеры:**
```cypher
// Find friends of friends
MATCH (user:Person {name: 'Alice'})-[:FRIEND]->()-[:FRIEND]->(fof)
RETURN fof.name

// Shortest path
MATCH path = shortestPath((a:Person)-[:KNOWS*]-(b:Person))
WHERE a.name = 'Alice' AND b.name = 'Bob'
RETURN path
```

**Use Cases:**
- Social networks
- Recommendation engines
- Fraud detection
- Knowledge graphs
- Supply chain analysis

### 8. Time-Series Databases [HIGH CONFIDENCE]

**InfluxDB vs TimescaleDB:**

| Критерий | InfluxDB | TimescaleDB |
|----------|----------|-------------|
| Architecture | Purpose-built | PostgreSQL extension |
| Query language | InfluxQL + SQL | Full SQL |
| Ingestion | Faster low-cardinality | Better high-cardinality |
| Complex queries | Limited | 3.4-71x faster |
| Ecosystem | Telegraf, Kapacitor | PostgreSQL tools |
| Storage | Better compression | Higher storage use |

**Выбор:**
- **InfluxDB:** Simple metrics, IoT with low cardinality
- **TimescaleDB:** Complex queries, PostgreSQL ecosystem, hybrid workloads

### 9. CouchDB/PouchDB — Offline-First [HIGH CONFIDENCE]

**Особенности:**
- Multi-master replication
- Built-in conflict resolution
- HTTP API, JSON documents
- PouchDB 9.0.0 (May 2024) — browser sync

**Offline-First Pattern:**
1. PouchDB stores data locally in browser/mobile
2. User works offline
3. Connection restored → auto-sync with CouchDB
4. Conflicts resolved by app logic

**Use Cases:**
- Mobile apps requiring offline mode
- Field data collection
- Collaborative editing
- Progressive Web Apps (PWA)

### 10. Elasticsearch [MEDIUM-HIGH CONFIDENCE]

**Архитектура:**
- Built on Apache Lucene
- Inverted index for full-text search
- Distributed, sharded
- RESTful JSON API

**Capabilities:**
- Full-text search with relevance scoring
- Fuzzy matching, autocomplete
- Aggregations and analytics
- Vector search (hybrid search 2024)

**Use Cases:**
- Log analysis (ELK Stack)
- E-commerce product search
- Application search
- Security analytics

**Важно:** Elasticsearch — не primary database, а search layer.

### 11. Scaling Strategies [HIGH CONFIDENCE]

**Sharding:**
- MongoDB: Range-based или hash-based
- Cassandra: Consistent hashing
- DynamoDB: Automatic partition management

**Replication:**
- Master-Slave: writes → master, reads → replicas
- Master-Master: writes to any node (CouchDB)
- Replica sets: automatic failover (MongoDB)

**Best Practices:**
- Minimum 3 replicas для redundancy
- Geographic distribution для disaster recovery
- Choose shard key carefully — bad key = hot spots
- Combine sharding + replication для scale + reliability

---

## Community Sentiment

### MongoDB
**Positive:**
- "Flexible schema is game-changer for rapid development"
- "ACID transactions since 4.0 solved our consistency issues"
- "Atlas simplifies operations significantly"

**Negative:**
- "Memory usage can be high"
- "Joins are painful compared to SQL"
- "Schema-less can lead to data quality issues"

### Redis
**Positive:**
- "Nothing beats Redis for caching performance"
- "Data structures are incredibly versatile"
- "Pub/Sub is simple and effective"

**Negative:**
- "Single-threaded can be limiting"
- "Memory-only requires careful capacity planning"
- "License change to AGPL (8.0+) concerns some"

### Cassandra
**Positive:**
- "Scales linearly, no bottlenecks"
- "Write performance is excellent"
- "No single point of failure"

**Negative:**
- "Steep learning curve"
- "Read-before-write antipattern hurts performance"
- "Schema changes can be complex"
- "Consider ScyllaDB for better performance"

### DynamoDB
**Positive:**
- "Truly serverless, zero ops"
- "Integrates perfectly with Lambda"
- "Consistent low latency at any scale"

**Negative:**
- "Vendor lock-in is real"
- "Single table design is complex to learn"
- "Costs can spike unexpectedly"
- "Limited query flexibility"

---

## When to Use SQL Instead

NoSQL is NOT always the answer. Use SQL when:

1. **Complex relationships** — JOINs between many tables
2. **ACID requirements** — financial transactions, banking
3. **Ad-hoc queries** — analytics, reporting
4. **Strong consistency** — data integrity is critical
5. **Mature tooling** — ORMs, migration tools
6. **Team expertise** — SQL is widely known

**Expert quote:** "Most data is naturally structured. NoSQL should 'almost never' be used if performance is important." — 30-year database professional (controversial but worth considering)

---

## Design Patterns & Anti-Patterns

### Patterns

**1. Denormalization:**
- Store redundant data to avoid joins
- Trade storage for read performance

**2. Embedding vs Referencing (MongoDB):**
- Embed: related data in same document
- Reference: store ID, join in application

**3. Single Table Design (DynamoDB):**
- All entities in one table
- Use composite keys + GSIs
- Requires known access patterns

**4. Time-bucketing (Time-series):**
- Partition by time intervals
- Efficient for range queries

### Anti-Patterns

**1. Hot Spots:**
- Poor shard key → all writes to one partition
- Solution: Choose high-cardinality keys

**2. Distributed Monolith:**
- Microservices sharing one database
- Solution: Database per service

**3. Unbounded Arrays:**
- Arrays that grow indefinitely
- Solution: Limit size or use separate collection

**4. Schema-less Chaos:**
- No validation leads to data quality issues
- Solution: Use schema validation (MongoDB)

---

## Conflicting Information

**Topic:** NoSQL vs SQL for performance
- **Pro-NoSQL:** "Horizontal scaling makes NoSQL faster at scale"
- **Pro-SQL:** "PostgreSQL scales well with proper optimization"
- **Resolution:** Both can be performant; choose based on data model fit

**Topic:** ACID in NoSQL
- **Old view:** "NoSQL sacrifices consistency for scale"
- **Modern view:** "MongoDB, DynamoDB, etc. now support ACID"
- **Resolution:** Many NoSQL now offer ACID when needed

**Topic:** Single Table Design
- **Proponents:** "Best for DynamoDB performance"
- **Critics:** "Overly complex for most applications"
- **Resolution:** Use for production DynamoDB; multi-table fine for development

---

## Recommendations

Based on research findings:

1. **Document Store:** MongoDB (Atlas for managed)
2. **Caching:** Redis (industry standard)
3. **Write-heavy:** Cassandra или ScyllaDB
4. **AWS Serverless:** DynamoDB
5. **Graph Data:** Neo4j
6. **Time-Series:** TimescaleDB (if need SQL) или InfluxDB (if simple metrics)
7. **Search:** Elasticsearch (as search layer, not primary DB)
8. **Offline-First:** CouchDB + PouchDB
9. **Real-time Mobile:** Firebase Firestore

**General advice:**
- Start with PostgreSQL if unsure — it handles JSON well
- Use NoSQL when you have a specific need it solves
- Don't choose based on hype; choose based on data model fit

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Neo4j Official Docs](https://neo4j.com/docs/getting-started/) | Official | 0.95 | Graph concepts, Cypher |
| 2 | [TimescaleDB vs InfluxDB](https://www.tigerdata.com/blog/timescaledb-vs-influxdb/) | Tech Blog | 0.85 | Time-series comparison |
| 3 | [MongoDB vs PostgreSQL](https://www.myscale.com/blog/mongodb-vs-postgresql/) | Tech Blog | 0.85 | Document vs relational |
| 4 | [Redis Use Cases](https://medium.com/@avraul7/redis-use-cases/) | Tech Blog | 0.80 | Caching patterns |
| 5 | [AWS DynamoDB Blog](https://aws.amazon.com/blogs/compute/creating-a-single-table-design/) | Official | 0.90 | Single table design |
| 6 | [Cassandra vs MongoDB vs DynamoDB](https://medium.com/@Tom1212121/nosql-labyrinth/) | Tech Blog | 0.80 | NoSQL comparison |
| 7 | [Redis vs Memcached](https://scalegrid.io/blog/redis-vs-memcached/) | Tech Blog | 0.85 | Caching comparison |
| 8 | [Elasticsearch Full-Text](https://www.elastic.co/docs/solutions/search/) | Official | 0.95 | Search capabilities |
| 9 | [NoSQL Design Patterns](https://medium.com/@artemkhrenov/database-design-patterns/) | Tech Blog | 0.80 | Architecture patterns |
| 10 | [MongoDB Anti-Patterns](https://www.mongodb.com/developer/products/mongodb/schema-design-anti-pattern-summary/) | Official | 0.90 | Schema best practices |
| 11 | [Firebase vs MongoDB](https://estuary.dev/blog/firebase-vs-mongodb/) | Tech Blog | 0.85 | Real-time comparison |
| 12 | [ACID vs BASE](https://neo4j.com/blog/acid-vs-base-consistency-models/) | Tech Blog | 0.85 | Consistency models |
| 13 | [ScyllaDB vs Cassandra](https://www.scylladb.com/compare/scylladb-vs-apache-cassandra/) | Official | 0.85 | Performance comparison |
| 14 | [PouchDB Replication](https://pouchdb.com/guides/replication.html) | Official | 0.90 | Offline-first sync |
| 15 | [NoSQL Scaling Strategies](https://moldstud.com/articles/p-scaling-your-nosql-database/) | Tech Blog | 0.80 | Sharding, replication |
| 16 | [DynamoDB Alex DeBrie](https://www.alexdebrie.com/posts/dynamodb-single-table/) | Expert Blog | 0.90 | Single table patterns |
| 17 | [QuestDB Comparison](https://questdb.com/blog/comparing-influxdb-timescaledb-questdb/) | Tech Blog | 0.85 | Time-series benchmarks |
| 18 | [AWS Redis vs Memcached](https://aws.amazon.com/elasticache/redis-vs-memcached/) | Official | 0.90 | Caching comparison |
| 19 | [CouchDB Offline-First](https://reintech.io/blog/building-offline-first-applications-couchdb) | Tech Blog | 0.80 | Offline architecture |
| 20 | [Database Sharding Guide](https://aerospike.com/blog/database-sharding-scalable-systems/) | Tech Blog | 0.85 | Scaling strategies |

---

## Research Methodology

- **Queries used:** 20 search queries covering all major NoSQL types, comparisons, patterns, community opinions
- **Source types:** Official documentation, tech blogs, community forums, comparison articles
- **Sources found:** 50+ total
- **Sources used:** 20 (after quality filter)
- **Research duration:** ~20 minutes
- **Coverage:** Document, Key-Value, Wide-Column, Graph, Time-Series, Search engines, Scaling, Consistency models
