---
title: "Research Report: Cloud Databases"
created: 2025-12-30
modified: 2025-12-30
type: reference
status: draft
tags:
  - topic/databases
  - topic/cloud
---

# Research Report: Cloud Databases

**Date:** 2025-12-30
**Sources Evaluated:** 20+
**Research Depth:** Deep (comprehensive multi-source analysis)

## Executive Summary

Cloud databases — managed database services от AWS, GCP, Azure, устраняющие operational overhead. **AWS Aurora** — лидер managed MySQL/PostgreSQL (5x faster MySQL, 3x faster PostgreSQL), **Aurora DSQL** (Dec 2024) — serverless distributed SQL с unlimited scale. **DynamoDB** — NoSQL лидер с single-table design pattern. **Google Cloud Spanner** — единственная globally distributed SQL DB с 99.999% availability. **Azure Cosmos DB** — multi-model с 5 consistency levels. Serverless тренд 2024-2025: **Neon** (PostgreSQL, branching), **PlanetScale** (MySQL, Vitess), Aurora Serverless v2. Экономия до 72% через Reserved Instances/Savings Plans. Ключевой выбор: managed vs serverless, regional vs global, consistency vs latency.

---

## Key Findings

### 1. AWS RDS vs Aurora [HIGH CONFIDENCE]

**Сравнение архитектур:**

| Характеристика | RDS | Aurora |
|----------------|-----|--------|
| Storage | EBS volumes | Distributed storage (6 copies, 3 AZs) |
| Replication | Synchronous to standby | Asynchronous to 15 replicas |
| Failover | 60-120 seconds | <30 seconds |
| Storage limit | 64 TB | 128 TB |
| Performance | Baseline | 5x MySQL, 3x PostgreSQL |
| Cost | Lower baseline | 20% more, but better price/performance |

**Aurora Storage Architecture:**
```
┌─────────────────────────────────────────────────────┐
│                  Aurora Instance                      │
├─────────────────────────────────────────────────────┤
│                   Storage Layer                       │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐   │
│  │Copy1│ │Copy2│ │Copy3│ │Copy4│ │Copy5│ │Copy6│   │
│  │ AZ1 │ │ AZ1 │ │ AZ2 │ │ AZ2 │ │ AZ3 │ │ AZ3 │   │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘   │
│           Quorum: 4/6 write, 3/6 read                │
└─────────────────────────────────────────────────────┘
```

**Когда выбирать:**
- **RDS**: Простые workloads, tight budget, lift-and-shift
- **Aurora**: Production workloads, high availability required, read-heavy

### 2. Aurora DSQL (December 2024) [HIGH CONFIDENCE]

**Революционный анонс AWS re:Invent 2024:**
- Serverless distributed SQL database
- PostgreSQL-compatible
- Unlimited horizontal scaling
- Active-active multi-region
- Strong consistency (serializable isolation)
- Zero operational overhead
- Preview в us-east-1, us-east-2

**Отличия от Aurora Serverless v2:**
| Feature | Aurora Serverless v2 | Aurora DSQL |
|---------|---------------------|-------------|
| Architecture | Single-region | Multi-region active-active |
| Scaling | ACU-based (0.5-128) | Unlimited |
| Consistency | Single-master | Distributed consensus |
| Use case | Variable workloads | Global applications |

### 3. DynamoDB Single-Table Design [HIGH CONFIDENCE]

**Best Practices 2024-2025:**

```
┌─────────────────────────────────────────────────────┐
│                  Single Table                        │
├──────────────┬──────────────┬───────────────────────┤
│      PK      │      SK      │     Attributes        │
├──────────────┼──────────────┼───────────────────────┤
│ USER#123     │ PROFILE      │ name, email, created  │
│ USER#123     │ ORDER#001    │ total, status, items  │
│ USER#123     │ ORDER#002    │ total, status, items  │
│ ORDER#001    │ ORDER#001    │ (GSI1PK for queries)  │
│ PRODUCT#abc  │ PRODUCT#abc  │ name, price, stock    │
└──────────────┴──────────────┴───────────────────────┘
```

**Patterns:**
1. **Composite Keys**: PK + SK для иерархий
2. **GSI Overloading**: Один GSI для множества access patterns
3. **Sparse Indexes**: Индексируются только items с атрибутом
4. **Adjacency Lists**: Related items с общим PK

**Anti-patterns:**
- Много таблиц (как в RDBMS) — высокая latency
- Scan operations — дорого и медленно
- Hot partitions — неравномерное распределение

**Pricing Model:**
- On-Demand: $1.25/million WCU, $0.25/million RCU
- Provisioned: ~5x cheaper с commitment
- Storage: $0.25/GB/month

### 4. Google Cloud Spanner [HIGH CONFIDENCE]

**Уникальные характеристики:**
- Globally distributed SQL database
- 99.999% availability (5 nines) — 5.26 min downtime/year
- External consistency (strongest guarantee)
- TrueTime API для глобальной синхронизации
- Horizontal scaling без sharding overhead

**TrueTime Architecture:**
```
┌─────────────────────────────────────────────────────┐
│               TrueTime API                           │
├─────────────────────────────────────────────────────┤
│  GPS receivers + Atomic clocks в каждом datacenter  │
│  Возвращает interval [earliest, latest]             │
│  Commit wait: ждём пока uncertainty пройдёт         │
│  Гарантирует: if T1 < T2, then T1 committed before  │
└─────────────────────────────────────────────────────┘
```

**Pricing (2024):**
- Regional: $0.90/node/hour (~$657/month)
- Multi-regional: $3.00/node/hour (~$2,190/month)
- Storage: $0.30/GB/month
- Minimum: 1 node (но рекомендуется 3 для production)

**Когда выбирать:**
- Global applications с strong consistency
- Financial systems (transactions across regions)
- Gaming leaderboards (global, low-latency)

### 5. Google AlloyDB vs Cloud SQL [HIGH CONFIDENCE]

**AlloyDB (GA May 2022, AI features 2024):**
- PostgreSQL-compatible
- 4x faster than standard PostgreSQL (OLTP)
- 100x faster analytical queries
- Columnar engine для analytics
- AI/ML integration (vector search, embeddings)

**Сравнение:**
| Feature | Cloud SQL | AlloyDB |
|---------|-----------|---------|
| Engine | MySQL, PostgreSQL, SQL Server | PostgreSQL only |
| Performance | Standard | 4x OLTP, 100x analytics |
| Architecture | Traditional | Disaggregated compute/storage |
| Price | Lower | ~2x Cloud SQL |
| Use case | General purpose | High-performance PostgreSQL |

### 6. Azure Cosmos DB Consistency Levels [HIGH CONFIDENCE]

**5 уровней консистентности:**

```
Strong ─────────────────────────────────────────> Eventual
│                                                      │
│  Strong    Bounded    Session    Consistent   Eventual
│            Staleness             Prefix              │
│                                                      │
High Consistency ◄─────────────────────► High Availability
High Latency ◄─────────────────────────────► Low Latency
```

| Level | Guarantee | Latency | Use Case |
|-------|-----------|---------|----------|
| Strong | Linearizability | Highest | Financial |
| Bounded Staleness | K versions or T time behind | High | Leaderboards |
| Session | Read-your-writes within session | Medium | User sessions |
| Consistent Prefix | No out-of-order reads | Low | Social feeds |
| Eventual | No ordering guarantee | Lowest | Analytics |

**Default:** Session (best balance для большинства apps)

**Pricing:**
- Provisioned: $0.008/RU/hour (100 RU/s minimum)
- Serverless: $0.25/million RUs
- Storage: $0.25/GB/month

### 7. Serverless Databases 2024-2025 [HIGH CONFIDENCE]

**Aurora Serverless v2:**
- Scale: 0.5 to 128 ACUs
- Scaling speed: seconds
- Min cost: ~$43/month (0.5 ACU)
- Use case: Variable workloads, dev/test

**Neon (PostgreSQL):**
- Branching: instant database copies
- Scale to zero: true serverless
- Autoscaling: 0.25 to 8 CU
- Free tier: 0.5 GB storage, 3 branches
- Use case: Development, preview environments

**PlanetScale (MySQL):**
- Based on Vitess (YouTube's DB)
- Schema changes: non-blocking, no downtime
- Branching: like Neon
- Insights: query analytics built-in
- Free tier: 5 GB storage, 1 billion reads/month

**Сравнение:**
| Feature | Aurora Serverless | Neon | PlanetScale |
|---------|-------------------|------|-------------|
| Engine | MySQL/PostgreSQL | PostgreSQL | MySQL |
| Scale to zero | No (0.5 ACU min) | Yes | Yes |
| Branching | No | Yes | Yes |
| Pricing | ACU-based | CU-based | Reads/Writes |
| Best for | Enterprise | Startups/Dev | Startups/Dev |

### 8. AWS ElastiCache vs MemoryDB [HIGH CONFIDENCE]

**ElastiCache:**
- Redis/Memcached managed service
- Use case: Caching layer
- Durability: Optional (Redis AOF)
- Replication: Async
- Price: Lower

**MemoryDB for Redis:**
- Redis-compatible
- Use case: Primary database
- Durability: Multi-AZ transaction log
- Replication: Synchronous
- 99.99% availability
- Price: ~25% more than ElastiCache

**Когда выбирать:**
- **ElastiCache**: Caching, session storage, non-critical data
- **MemoryDB**: Primary datastore, need durability, financial apps

### 9. Cloud Database Migration [HIGH CONFIDENCE]

**AWS Database Migration Service (DMS):**
- Supports: Oracle, SQL Server, MySQL, PostgreSQL, MongoDB, etc.
- Heterogeneous migrations (Oracle → Aurora)
- Continuous replication (CDC)
- Schema Conversion Tool (SCT)

**Migration Patterns:**
```
┌─────────────────────────────────────────────────────┐
│           Migration Approaches                       │
├─────────────────────────────────────────────────────┤
│  1. Lift-and-Shift: Same engine, minimal changes    │
│  2. Replatform: Different engine, DMS + SCT         │
│  3. Refactor: Redesign for cloud-native             │
└─────────────────────────────────────────────────────┘
```

**Best Practices:**
1. Assessment: AWS SCT для compatibility report
2. Schema conversion first
3. Full load + CDC для minimal downtime
4. Validation: AWS DMS Data Validation
5. Cutover: DNS switch после sync complete

**Azure Database Migration Service:**
- Similar capabilities
- Azure Migrate для assessment
- Supports SQL Server → Azure SQL особенно хорошо

### 10. Multi-Region HA/DR [HIGH CONFIDENCE]

**Patterns:**

| Pattern | RTO | RPO | Cost | Complexity |
|---------|-----|-----|------|------------|
| Backup/Restore | Hours | Hours | Low | Low |
| Pilot Light | Minutes | Minutes | Medium | Medium |
| Warm Standby | Minutes | Seconds | High | High |
| Active-Active | Seconds | Zero | Highest | Highest |

**AWS Multi-Region:**
- Aurora Global Database: <1 second replication lag
- DynamoDB Global Tables: Active-active
- Cross-region read replicas

**GCP Multi-Region:**
- Cloud Spanner: Built-in multi-region
- Cloud SQL: Cross-region replicas

**Azure Multi-Region:**
- Cosmos DB: Multi-region writes
- Azure SQL: Failover groups

### 11. AWS DocumentDB vs MongoDB Atlas [HIGH CONFIDENCE]

**DocumentDB:**
- MongoDB 4.0/5.0 compatible (not 100%)
- AWS managed, integrated
- Storage: up to 128 TB
- Elastic Clusters (Dec 2022): sharding

**MongoDB Atlas:**
- Full MongoDB features
- Multi-cloud (AWS, GCP, Azure)
- Serverless option
- Atlas Search, Charts, Data Federation

**Compatibility Issues:**
- DocumentDB lacks: $merge, Change Streams (full), some aggregations
- For full MongoDB compatibility → Atlas
- For AWS integration → DocumentDB

### 12. Cloud Database Security [HIGH CONFIDENCE]

**Encryption:**
```
┌─────────────────────────────────────────────────────┐
│              Encryption Layers                       │
├─────────────────────────────────────────────────────┤
│  At Rest:                                           │
│  - AWS: KMS (AES-256)                               │
│  - GCP: Cloud KMS (default or CMEK)                 │
│  - Azure: Azure Key Vault                           │
├─────────────────────────────────────────────────────┤
│  In Transit:                                        │
│  - TLS 1.2/1.3 (mandatory)                          │
│  - Certificate rotation                             │
├─────────────────────────────────────────────────────┤
│  Client-side (optional):                            │
│  - Application-level encryption                      │
│  - AWS Encryption SDK                               │
└─────────────────────────────────────────────────────┘
```

**IAM Best Practices:**
1. Least privilege principle
2. IAM database authentication (Aurora, RDS)
3. Secrets Manager для credentials rotation
4. VPC endpoints (no internet exposure)
5. Security groups: restrict by IP/SG
6. Audit logging: CloudTrail, CloudWatch

### 13. Cost Optimization [HIGH CONFIDENCE]

**Reserved Instances / Savings Plans:**

| Commitment | Discount | Best For |
|------------|----------|----------|
| 1-year All Upfront | ~40% | Stable workloads |
| 3-year All Upfront | ~60-72% | Long-term production |
| No Upfront | ~30% | Uncertain growth |

**Cost Optimization Strategies:**
1. Right-sizing: Match instance to workload
2. Reserved capacity: 40-72% savings
3. Serverless: Pay-per-use для variable loads
4. Storage tiering: S3 IA для backups
5. Read replicas: Offload reads, smaller primary
6. Pause dev/test: Aurora Serverless, Neon

**Monitoring Tools:**
- AWS Cost Explorer, Budgets
- GCP Billing Reports
- Azure Cost Management

### 14. Supabase vs Firebase [HIGH CONFIDENCE]

**Supabase:**
- Open source (self-host option)
- PostgreSQL-based
- Row Level Security (RLS)
- Real-time subscriptions
- Edge Functions (Deno)
- Storage: S3-compatible

**Firebase:**
- Google proprietary
- Firestore (NoSQL) or Realtime DB
- Firebase Auth
- Cloud Functions (Node.js)
- Hosting, ML Kit, Analytics

**Сравнение:**
| Feature | Supabase | Firebase |
|---------|----------|----------|
| Database | PostgreSQL | Firestore/RTDB |
| Query | SQL | NoSQL (limited) |
| Self-host | Yes | No |
| Pricing | More transparent | Complex |
| Lock-in | Low | High |
| Best for | SQL lovers, open source | Mobile apps, Google stack |

### 15. Time-Series: Timestream vs InfluxDB Cloud [HIGH CONFIDENCE]

**AWS Timestream:**
- Serverless time-series DB
- Automatic tiering (memory → magnetic)
- SQL-like query language
- Built-in analytics
- Pricing: $0.50/GB ingested, $0.01/GB scanned

**InfluxDB Cloud:**
- Purpose-built for metrics
- InfluxQL or Flux query
- Telegraf agent integration
- Grafana native support
- Free tier: 2 buckets, 30-day retention

**Когда выбирать:**
- **Timestream**: AWS-native, serverless preference
- **InfluxDB**: Existing InfluxDB expertise, Grafana stack

### 16. Monitoring: RDS Performance Insights [HIGH CONFIDENCE]

**Capabilities:**
- Database load by wait events
- Top SQL identification
- 7 days free retention (extended: $)
- Counter metrics (CPU, memory, I/O)

**Key Metrics:**
```
┌─────────────────────────────────────────────────────┐
│           Performance Insights Dashboard             │
├─────────────────────────────────────────────────────┤
│  DB Load = Active Sessions (AAS)                    │
│  - CPU wait                                         │
│  - I/O wait                                         │
│  - Lock wait                                        │
│  - Network wait                                     │
├─────────────────────────────────────────────────────┤
│  Top SQL (by load):                                 │
│  1. SELECT * FROM orders... (45% load)              │
│  2. UPDATE users SET... (20% load)                  │
│  3. INSERT INTO logs... (15% load)                  │
└─────────────────────────────────────────────────────┘
```

**Enhanced Monitoring:**
- OS-level metrics
- 1-second granularity
- CloudWatch integration

---

## Community Sentiment

### AWS Aurora
**Positive:**
- "Best managed PostgreSQL/MySQL experience"
- "Failover is incredibly fast"
- "Storage auto-scaling is magical"

**Negative:**
- "20% more expensive than RDS"
- "Vendor lock-in concerns"
- "Some PostgreSQL features missing"

### DynamoDB
**Positive:**
- "Infinite scale, zero ops"
- "Single-digit millisecond latency"
- "Pay-per-request is great for variable traffic"

**Negative:**
- "Single-table design is complex"
- "Expensive at scale if not optimized"
- "Query flexibility limited"

### Cloud Spanner
**Positive:**
- "Only true global SQL database"
- "TrueTime is genius engineering"
- "Worth it for global consistency needs"

**Negative:**
- "Very expensive (minimum ~$657/month)"
- "Overkill for regional apps"
- "Learning curve for optimization"

### Serverless (Neon/PlanetScale)
**Positive:**
- "Branching is game-changer for development"
- "Scale to zero saves money"
- "Great DX (developer experience)"

**Negative:**
- "Cold starts can be slow"
- "Less control than self-managed"
- "Pricing can be unpredictable at scale"

---

## Conflicting Information

**Topic:** Aurora vs RDS cost-effectiveness
- **Source A says:** "Aurora is 20% more expensive but worth it"
- **Source B says:** "Aurora can be cheaper due to better performance"
- **Resolution:** Depends on workload — Aurora wins for read-heavy, high-availability needs

**Topic:** DynamoDB single-table vs multi-table
- **Source A says:** "Single-table is the only way"
- **Source B says:** "Multi-table is fine for simple apps"
- **Resolution:** Single-table for complex access patterns, multi-table acceptable for simple CRUD

**Topic:** Serverless databases for production
- **Source A says:** "Production-ready, used by many startups"
- **Source B says:** "Cold starts and unpredictable pricing are concerns"
- **Resolution:** Production-ready for many use cases, but evaluate latency requirements

---

## Recommendations

### By Use Case

**Standard Web Application:**
1. **AWS**: Aurora PostgreSQL/MySQL
2. **GCP**: Cloud SQL or AlloyDB
3. **Azure**: Azure SQL Database

**Global Application (Strong Consistency):**
1. **Best**: Google Cloud Spanner
2. **Alternative**: Aurora Global Database + careful design
3. **New**: Aurora DSQL (when GA)

**High-Performance NoSQL:**
1. **AWS**: DynamoDB
2. **GCP**: Firestore or Bigtable
3. **Azure**: Cosmos DB

**Startup/Development:**
1. **PostgreSQL**: Neon or Supabase
2. **MySQL**: PlanetScale
3. **Full-stack**: Supabase or Firebase

**Analytics/Time-Series:**
1. **AWS**: Timestream или Redshift
2. **GCP**: BigQuery
3. **Specialized**: InfluxDB Cloud

### Cost Optimization Priority

1. Reserved Instances для stable production workloads (40-72% savings)
2. Serverless для variable/dev workloads
3. Right-sizing с Performance Insights
4. Read replicas вместо larger primary
5. Storage tiering для backups

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [AWS Aurora Documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/) | Official | 0.95 | Aurora architecture |
| 2 | [AWS re:Invent 2024 Aurora DSQL](https://aws.amazon.com/blogs/database/introducing-amazon-aurora-dsql/) | Official | 0.95 | DSQL announcement |
| 3 | [DynamoDB Best Practices](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/best-practices.html) | Official | 0.95 | Single-table design |
| 4 | [Google Cloud Spanner](https://cloud.google.com/spanner/docs) | Official | 0.95 | Spanner architecture |
| 5 | [Azure Cosmos DB Consistency](https://learn.microsoft.com/en-us/azure/cosmos-db/consistency-levels) | Official | 0.95 | Consistency levels |
| 6 | [Neon Documentation](https://neon.tech/docs) | Official | 0.90 | Serverless PostgreSQL |
| 7 | [PlanetScale Documentation](https://planetscale.com/docs) | Official | 0.90 | Serverless MySQL |
| 8 | [AWS Pricing Calculator](https://calculator.aws/) | Official | 0.95 | Cost estimation |
| 9 | [GCP AlloyDB Overview](https://cloud.google.com/alloydb/docs) | Official | 0.95 | AlloyDB features |
| 10 | [AWS DMS User Guide](https://docs.aws.amazon.com/dms/latest/userguide/) | Official | 0.95 | Migration |
| 11 | [Supabase Documentation](https://supabase.com/docs) | Official | 0.90 | Supabase features |
| 12 | [Firebase Documentation](https://firebase.google.com/docs) | Official | 0.95 | Firebase comparison |
| 13 | [AWS MemoryDB](https://docs.aws.amazon.com/memorydb/) | Official | 0.95 | MemoryDB vs ElastiCache |
| 14 | [RDS Performance Insights](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html) | Official | 0.95 | Monitoring |
| 15 | [AWS Timestream](https://docs.aws.amazon.com/timestream/) | Official | 0.95 | Time-series DB |
| 16 | [Reddit r/aws](https://reddit.com/r/aws) | Community | 0.75 | User experiences |
| 17 | [Hacker News discussions](https://news.ycombinator.com) | Community | 0.80 | Expert opinions |
| 18 | [AWS Security Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/security-reference-architecture/) | Official | 0.95 | Security |
| 19 | [GCP vs AWS vs Azure comparison](https://cloud.google.com/docs/compare/aws) | Official | 0.85 | Cross-cloud |
| 20 | [MongoDB Atlas Documentation](https://www.mongodb.com/docs/atlas/) | Official | 0.90 | DocumentDB alternative |

---

## Research Methodology

- **Queries used:** 20 search queries covering AWS/GCP/Azure databases, serverless options, pricing, security, migration, monitoring
- **Source types:** Official documentation, vendor docs, community discussions, comparison articles
- **Coverage:** Relational (Aurora, RDS, Cloud SQL, Spanner), NoSQL (DynamoDB, Cosmos DB), Serverless (Neon, PlanetScale), Time-series, Caching
- **Key updates:** Aurora DSQL (Dec 2024), AlloyDB AI features (2024), Neon scale-to-zero improvements
