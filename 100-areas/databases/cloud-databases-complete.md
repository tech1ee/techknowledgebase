---
title: "Cloud Databases: Complete Guide"
type: guide
status: published
tags:
  - topic/databases
  - type/guide
  - level/intermediate
---

# Cloud Databases: Complete Guide

> Managed database services от AWS, GCP, Azure — от basics до production best practices

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **SQL и NoSQL основы** | Понимание типов БД | [[databases-fundamentals-complete]] |
| **Cloud basics** | AWS/GCP/Azure основы | [[cloud-overview]] |
| **Networking** | VPC, subnets, security groups | [[networking-basics]] |
| **DevOps basics** | IaC, CI/CD, мониторинг | [[devops-overview]] |

### Для кого этот материал

| Уровень | Что получите |
|---------|--------------|
| **Backend разработчик** | Выбор managed DB, настройка, использование |
| **DevOps/SRE** | High Availability, backup, monitoring, security |
| **Архитектор** | Multi-region, cost optimization, migration |

---

## Терминология

> 💡 **Главная аналогия:**
>
> **Self-managed БД** = своя квартира (сам чинишь, сам убираешь)
> **Managed БД** = отель (персонал всё делает, ты только пользуешься)
> **Serverless БД** = Airbnb (платишь только когда живёшь)

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **RDS** | Relational Database Service (AWS) | **Отель для SQL** — PostgreSQL/MySQL как сервис |
| **Aurora** | AWS cloud-native SQL, совместим с MySQL/PostgreSQL | **5-звёздочный отель** — быстрее, надёжнее RDS |
| **DynamoDB** | AWS NoSQL, key-value + document | **Автоматический склад** — масштабируется сам |
| **Serverless** | Автоскейлинг, платишь за использование | **Такси** — платишь только когда едешь |
| **Multi-AZ** | Реплика в другой зоне доступности | **Запасной ключ у соседа** — сгорела квартира, ключ у соседа |
| **Read Replica** | Копия для чтения | **Ксерокопия документа** — оригинал для записи, копии для чтения |
| **Connection Pooling** | Переиспользование соединений | **Общий телефон в офисе** — один на всех |
| **RCU/WCU** | Read/Write Capacity Units (DynamoDB) | **Билеты на чтение/запись** — сколько операций в секунду |
| **Spanner** | Google globally distributed SQL | **Всемирная библиотека** — consistent везде |
| **Cosmos DB** | Azure multi-model, global distribution | **Швейцарский нож Azure** — SQL, MongoDB, Cassandra API |

---

## Table of Contents

1. [Overview: Why Cloud Databases](#overview)
2. [AWS Databases](#aws-databases)
3. [Google Cloud Databases](#google-cloud-databases)
4. [Azure Databases](#azure-databases)
5. [Serverless Databases](#serverless-databases)
6. [Multi-Region & High Availability](#multi-region-ha)
7. [Migration Strategies](#migration-strategies)
8. [Security Best Practices](#security-best-practices)
9. [Cost Optimization](#cost-optimization)
10. [Monitoring & Performance](#monitoring-performance)
11. [Decision Framework](#decision-framework)
12. [Practical Examples](#practical-examples)

---

## Overview: Why Cloud Databases {#overview}

### Managed vs Self-Managed

```
┌─────────────────────────────────────────────────────────────────┐
│                    Responsibility Matrix                         │
├─────────────────────┬──────────────────┬───────────────────────┤
│                     │   Self-Managed   │      Managed          │
├─────────────────────┼──────────────────┼───────────────────────┤
│ Hardware            │      You         │      Provider         │
│ OS Patching         │      You         │      Provider         │
│ DB Installation     │      You         │      Provider         │
│ Backups             │      You         │      Provider         │
│ High Availability   │      You         │      Provider         │
│ Scaling             │      You         │      Provider/You     │
│ Security Patching   │      You         │      Provider         │
│ Schema Design       │      You         │      You              │
│ Query Optimization  │      You         │      You              │
│ Application Code    │      You         │      You              │
└─────────────────────┴──────────────────┴───────────────────────┘
```

### Cloud Database Categories

```
┌─────────────────────────────────────────────────────────────────┐
│                   Cloud Database Types                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Relational (SQL)          NoSQL                                │
│  ├── AWS RDS               ├── DynamoDB (Key-Value/Document)    │
│  ├── AWS Aurora            ├── Cosmos DB (Multi-model)          │
│  ├── Cloud SQL             ├── Firestore (Document)             │
│  ├── Cloud Spanner         ├── MongoDB Atlas (Document)         │
│  ├── Azure SQL             └── Bigtable (Wide-column)           │
│  └── AlloyDB                                                    │
│                                                                  │
│  In-Memory                 Time-Series                          │
│  ├── ElastiCache           ├── Timestream                       │
│  ├── MemoryDB              ├── InfluxDB Cloud                   │
│  └── Cloud Memorystore     └── TimescaleDB Cloud                │
│                                                                  │
│  Serverless                Analytics                            │
│  ├── Neon                  ├── Redshift                         │
│  ├── PlanetScale           ├── BigQuery                         │
│  ├── Aurora Serverless     └── Synapse                          │
│  └── Cosmos DB Serverless                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## AWS Databases {#aws-databases}

### RDS (Relational Database Service)

**Supported Engines:**
- MySQL, PostgreSQL, MariaDB
- Oracle, SQL Server
- Custom (bring your own)

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                        RDS Architecture                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐           ┌─────────────┐                     │
│   │   Primary   │◄─────────►│   Standby   │  Multi-AZ           │
│   │  Instance   │  Sync     │  Instance   │  (Failover)         │
│   └──────┬──────┘  Repl     └─────────────┘                     │
│          │                                                       │
│          ▼                                                       │
│   ┌─────────────┐                                               │
│   │ EBS Volume  │  Storage (gp3, io1, io2)                      │
│   │   (Data)    │                                               │
│   └─────────────┘                                               │
│                                                                  │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │ Read Replica│  │ Read Replica│  │ Read Replica│  Up to 15   │
│   │    (AZ1)    │  │    (AZ2)    │  │   (Region2) │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Features:**
```python
# Terraform example: RDS PostgreSQL
resource "aws_db_instance" "main" {
  identifier           = "production-db"
  engine              = "postgres"
  engine_version      = "15.4"
  instance_class      = "db.r6g.xlarge"
  allocated_storage   = 100
  storage_type        = "gp3"
  storage_encrypted   = true

  # High Availability
  multi_az            = true

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]
  publicly_accessible    = false

  # Backup
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Mon:04:00-Mon:05:00"

  # Performance
  performance_insights_enabled = true

  # Parameters
  parameter_group_name = aws_db_parameter_group.main.name

  # Deletion protection
  deletion_protection = true

  tags = {
    Environment = "production"
  }
}

# Parameter Group for tuning
resource "aws_db_parameter_group" "main" {
  family = "postgres15"
  name   = "production-params"

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"  # Log queries > 1s
  }
}
```

### Aurora

**Architecture (Distributed Storage):**
```
┌─────────────────────────────────────────────────────────────────┐
│                      Aurora Architecture                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Compute Layer (Instances)                                     │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │   Writer    │  │   Reader    │  │   Reader    │            │
│   │  Instance   │  │  Instance   │  │  Instance   │            │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘            │
│          │                │                │                     │
│          └────────────────┼────────────────┘                     │
│                           │                                      │
│   ────────────────────────┼────────────────────────────────────  │
│                           ▼                                      │
│   Storage Layer (Shared, Distributed)                           │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                          │   │
│   │   ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐      │   │
│   │   │ 10GB│ │ 10GB│ │ 10GB│ │ 10GB│ │ 10GB│ │ 10GB│      │   │
│   │   │Segm1│ │Segm2│ │Segm3│ │Segm4│ │Segm5│ │Segm6│      │   │
│   │   └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘      │   │
│   │      │       │       │       │       │       │          │   │
│   │   ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐     │   │
│   │   │6copy│ │6copy│ │6copy│ │6copy│ │6copy│ │6copy│     │   │
│   │   │3 AZs│ │3 AZs│ │3 AZs│ │3 AZs│ │3 AZs│ │3 AZs│     │   │
│   │   └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘     │   │
│   │                                                          │   │
│   │   Quorum: 4/6 for writes, 3/6 for reads                 │   │
│   │   Automatic repair, no data loss with 2 AZ failure      │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Aurora vs RDS Performance:**
```
┌─────────────────────────────────────────────────────────────────┐
│                    Performance Comparison                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Throughput (TPS)                                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ RDS MySQL:    ████████████████████ 50,000                  │ │
│  │ Aurora MySQL: ████████████████████████████████████ 250,000 │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Failover Time                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ RDS:    ████████████████████████████████████ 60-120 sec    │ │
│  │ Aurora: ████████ <30 sec                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Replication Lag                                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ RDS:    Seconds to minutes (async)                         │ │
│  │ Aurora: <100ms (shared storage)                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Aurora Terraform:**
```python
resource "aws_rds_cluster" "aurora" {
  cluster_identifier     = "production-aurora"
  engine                = "aurora-postgresql"
  engine_version        = "15.4"
  database_name         = "myapp"
  master_username       = "admin"
  master_password       = var.db_password

  # Storage
  storage_encrypted     = true
  kms_key_id           = aws_kms_key.db.arn

  # Backup
  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"

  # Networking
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.aurora.id]

  # Performance
  enabled_cloudwatch_logs_exports = ["postgresql"]

  # Deletion protection
  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "production-aurora-final"
}

resource "aws_rds_cluster_instance" "aurora_instances" {
  count              = 3  # 1 writer + 2 readers
  identifier         = "production-aurora-${count.index}"
  cluster_identifier = aws_rds_cluster.aurora.id
  instance_class     = "db.r6g.xlarge"
  engine            = aws_rds_cluster.aurora.engine
  engine_version    = aws_rds_cluster.aurora.engine_version

  performance_insights_enabled = true
}
```

### Aurora DSQL (December 2024)

**Revolutionary Features:**
```
┌─────────────────────────────────────────────────────────────────┐
│                     Aurora DSQL Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Region A                    Region B                          │
│   ┌──────────────────┐       ┌──────────────────┐              │
│   │  ┌────────────┐  │       │  ┌────────────┐  │              │
│   │  │   Writer   │◄─┼───────┼─►│   Writer   │  │              │
│   │  │  (Active)  │  │       │  │  (Active)  │  │              │
│   │  └────────────┘  │       │  └────────────┘  │              │
│   │        │         │       │        │         │              │
│   │  ┌─────┴─────┐   │       │  ┌─────┴─────┐   │              │
│   │  │  Storage  │   │       │  │  Storage  │   │              │
│   │  └───────────┘   │       │  └───────────┘   │              │
│   └──────────────────┘       └──────────────────┘              │
│                                                                  │
│   Key Features:                                                 │
│   - Active-Active Multi-Region Writes                           │
│   - Serializable Isolation (Strong Consistency)                 │
│   - Unlimited Horizontal Scaling                                │
│   - Zero Operational Overhead                                   │
│   - PostgreSQL Compatible                                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### DynamoDB

**Single-Table Design Pattern:**
```
┌─────────────────────────────────────────────────────────────────┐
│                  DynamoDB Single-Table Design                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Table: EcommerceApp                                            │
│  ┌─────────────────┬─────────────────┬───────────────────────┐  │
│  │       PK        │       SK        │     Attributes        │  │
│  ├─────────────────┼─────────────────┼───────────────────────┤  │
│  │ USER#u123       │ PROFILE         │ name, email, created  │  │
│  │ USER#u123       │ ORDER#o001      │ total, status, date   │  │
│  │ USER#u123       │ ORDER#o002      │ total, status, date   │  │
│  │ ORDER#o001      │ ITEM#i001       │ product, qty, price   │  │
│  │ ORDER#o001      │ ITEM#i002       │ product, qty, price   │  │
│  │ PRODUCT#p001    │ PRODUCT#p001    │ name, price, stock    │  │
│  │ PRODUCT#p001    │ REVIEW#r001     │ user, rating, text    │  │
│  └─────────────────┴─────────────────┴───────────────────────┘  │
│                                                                  │
│  GSI1 (Inverted Index):                                         │
│  ┌─────────────────┬─────────────────┐                          │
│  │    GSI1PK       │    GSI1SK       │  Access Pattern          │
│  ├─────────────────┼─────────────────┼────────────────────────  │
│  │ ORDER#o001      │ USER#u123       │  Get order by ID         │
│  │ STATUS#pending  │ 2024-01-15#o001 │  Orders by status+date   │
│  │ PRODUCT#p001    │ RATING#5#r001   │  Reviews by product      │
│  └─────────────────┴─────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**DynamoDB with AWS SDK:**
```python
import boto3
from boto3.dynamodb.conditions import Key, Attr
from decimal import Decimal
import json

# Initialize
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('EcommerceApp')

# ============================================
# Access Pattern 1: Get User Profile
# ============================================
def get_user_profile(user_id: str):
    response = table.get_item(
        Key={
            'PK': f'USER#{user_id}',
            'SK': 'PROFILE'
        }
    )
    return response.get('Item')

# ============================================
# Access Pattern 2: Get User's Orders
# ============================================
def get_user_orders(user_id: str, limit: int = 20):
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f'USER#{user_id}') &
                              Key('SK').begins_with('ORDER#'),
        ScanIndexForward=False,  # Latest first
        Limit=limit
    )
    return response['Items']

# ============================================
# Access Pattern 3: Get Order with Items
# ============================================
def get_order_with_items(order_id: str):
    response = table.query(
        KeyConditionExpression=Key('PK').eq(f'ORDER#{order_id}')
    )
    items = response['Items']

    # Separate order metadata from items
    order = next((i for i in items if i['SK'].startswith('ORDER#')), None)
    order_items = [i for i in items if i['SK'].startswith('ITEM#')]

    return {'order': order, 'items': order_items}

# ============================================
# Access Pattern 4: Create Order (Transaction)
# ============================================
def create_order(user_id: str, order_id: str, items: list, total: Decimal):
    transaction_items = [
        # Order metadata under user
        {
            'Put': {
                'TableName': 'EcommerceApp',
                'Item': {
                    'PK': f'USER#{user_id}',
                    'SK': f'ORDER#{order_id}',
                    'GSI1PK': f'ORDER#{order_id}',
                    'GSI1SK': f'USER#{user_id}',
                    'total': total,
                    'status': 'pending',
                    'created_at': '2024-01-15T10:30:00Z'
                }
            }
        }
    ]

    # Add each item
    for idx, item in enumerate(items):
        transaction_items.append({
            'Put': {
                'TableName': 'EcommerceApp',
                'Item': {
                    'PK': f'ORDER#{order_id}',
                    'SK': f'ITEM#{idx:04d}',
                    'product_id': item['product_id'],
                    'quantity': item['quantity'],
                    'price': item['price']
                }
            }
        })

        # Update product stock (conditional)
        transaction_items.append({
            'Update': {
                'TableName': 'EcommerceApp',
                'Key': {
                    'PK': f"PRODUCT#{item['product_id']}",
                    'SK': f"PRODUCT#{item['product_id']}"
                },
                'UpdateExpression': 'SET stock = stock - :qty',
                'ConditionExpression': 'stock >= :qty',
                'ExpressionAttributeValues': {
                    ':qty': item['quantity']
                }
            }
        })

    client = boto3.client('dynamodb')
    client.transact_write_items(TransactItems=transaction_items)

# ============================================
# Access Pattern 5: Query by Status (GSI)
# ============================================
def get_orders_by_status(status: str, date_from: str = None):
    key_condition = Key('GSI1PK').eq(f'STATUS#{status}')

    if date_from:
        key_condition = key_condition & Key('GSI1SK').gte(date_from)

    response = table.query(
        IndexName='GSI1',
        KeyConditionExpression=key_condition
    )
    return response['Items']
```

**DynamoDB Terraform:**
```python
resource "aws_dynamodb_table" "main" {
  name           = "EcommerceApp"
  billing_mode   = "PAY_PER_REQUEST"  # On-demand
  hash_key       = "PK"
  range_key      = "SK"

  # Primary key
  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  # GSI attributes
  attribute {
    name = "GSI1PK"
    type = "S"
  }

  attribute {
    name = "GSI1SK"
    type = "S"
  }

  # Global Secondary Index
  global_secondary_index {
    name               = "GSI1"
    hash_key           = "GSI1PK"
    range_key          = "GSI1SK"
    projection_type    = "ALL"
  }

  # Encryption
  server_side_encryption {
    enabled = true
  }

  # Point-in-time recovery
  point_in_time_recovery {
    enabled = true
  }

  # TTL for automatic deletion
  ttl {
    attribute_name = "expires_at"
    enabled        = true
  }

  tags = {
    Environment = "production"
  }
}
```

### ElastiCache vs MemoryDB

```
┌─────────────────────────────────────────────────────────────────┐
│              ElastiCache vs MemoryDB Comparison                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ElastiCache (Redis)           MemoryDB for Redis               │
│  ┌───────────────────┐        ┌───────────────────┐            │
│  │                   │        │                   │            │
│  │   Caching Layer   │        │  Primary Database │            │
│  │   Session Store   │        │  Durable Storage  │            │
│  │   Leaderboards    │        │  Transaction Log  │            │
│  │                   │        │                   │            │
│  └───────────────────┘        └───────────────────┘            │
│                                                                  │
│  Durability:                  Durability:                       │
│  - Optional AOF               - Multi-AZ Transaction Log        │
│  - Async replication          - Synchronous replication         │
│  - Data loss possible         - 99.99% durability               │
│                                                                  │
│  Use Cases:                   Use Cases:                        │
│  - Cache in front of DB       - Primary datastore               │
│  - Session management         - Financial applications          │
│  - Real-time analytics        - Shopping carts                  │
│  - Pub/Sub messaging          - Leaderboards (durable)          │
│                                                                  │
│  Price: Lower                 Price: ~25% more                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Google Cloud Databases {#google-cloud-databases}

### Cloud Spanner

**Global Distribution with TrueTime:**
```
┌─────────────────────────────────────────────────────────────────┐
│                  Cloud Spanner Architecture                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      TrueTime API                        │   │
│   │   GPS Receivers + Atomic Clocks in every datacenter     │   │
│   │   Returns: [earliest_time, latest_time] interval        │   │
│   │   Uncertainty: typically < 7ms                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   US-East              Europe              Asia-Pacific          │
│   ┌────────┐          ┌────────┐          ┌────────┐            │
│   │ Node 1 │◄────────►│ Node 1 │◄────────►│ Node 1 │            │
│   │ Node 2 │          │ Node 2 │          │ Node 2 │            │
│   │ Node 3 │          │ Node 3 │          │ Node 3 │            │
│   └────────┘          └────────┘          └────────┘            │
│       │                   │                   │                  │
│       ▼                   ▼                   ▼                  │
│   ┌────────┐          ┌────────┐          ┌────────┐            │
│   │ Splits │          │ Splits │          │ Splits │            │
│   │(Shards)│          │(Shards)│          │(Shards)│            │
│   └────────┘          └────────┘          └────────┘            │
│                                                                  │
│   Guarantees:                                                   │
│   - External Consistency (strongest possible)                   │
│   - 99.999% availability (5 nines)                             │
│   - Automatic resharding                                        │
│   - ACID transactions across regions                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Spanner Schema Design:**
```sql
-- Interleaved tables for co-location
CREATE TABLE Users (
    UserId    INT64 NOT NULL,
    Email     STRING(255) NOT NULL,
    Name      STRING(100),
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
) PRIMARY KEY (UserId);

-- Orders interleaved in Users (co-located for efficient joins)
CREATE TABLE Orders (
    UserId    INT64 NOT NULL,
    OrderId   INT64 NOT NULL,
    Total     NUMERIC,
    Status    STRING(20),
    CreatedAt TIMESTAMP NOT NULL OPTIONS (allow_commit_timestamp=true),
) PRIMARY KEY (UserId, OrderId),
  INTERLEAVE IN PARENT Users ON DELETE CASCADE;

-- Order items interleaved in Orders
CREATE TABLE OrderItems (
    UserId    INT64 NOT NULL,
    OrderId   INT64 NOT NULL,
    ItemId    INT64 NOT NULL,
    ProductId INT64 NOT NULL,
    Quantity  INT64,
    Price     NUMERIC,
) PRIMARY KEY (UserId, OrderId, ItemId),
  INTERLEAVE IN PARENT Orders ON DELETE CASCADE;

-- Secondary index for queries by status
CREATE INDEX OrdersByStatus ON Orders(Status, CreatedAt DESC);

-- Read-optimized index with additional columns
CREATE INDEX OrdersByStatusWithTotal ON Orders(Status) STORING (Total);
```

**Spanner with Go:**
```go
package main

import (
    "context"
    "fmt"
    "time"

    "cloud.google.com/go/spanner"
    "google.golang.org/api/iterator"
)

func main() {
    ctx := context.Background()
    client, err := spanner.NewClient(ctx, "projects/my-project/instances/my-instance/databases/my-db")
    if err != nil {
        panic(err)
    }
    defer client.Close()

    // Read with strong consistency
    readUser(ctx, client, 123)

    // Write with transaction
    createOrder(ctx, client, 123, 456, []OrderItem{
        {ProductId: 1, Quantity: 2, Price: 29.99},
        {ProductId: 2, Quantity: 1, Price: 49.99},
    })
}

func readUser(ctx context.Context, client *spanner.Client, userId int64) {
    row, err := client.Single().ReadRow(ctx, "Users",
        spanner.Key{userId},
        []string{"UserId", "Email", "Name"})
    if err != nil {
        panic(err)
    }

    var user User
    if err := row.ToStruct(&user); err != nil {
        panic(err)
    }
    fmt.Printf("User: %+v\n", user)
}

type OrderItem struct {
    ProductId int64
    Quantity  int64
    Price     float64
}

func createOrder(ctx context.Context, client *spanner.Client,
                 userId, orderId int64, items []OrderItem) {

    _, err := client.ReadWriteTransaction(ctx,
        func(ctx context.Context, txn *spanner.ReadWriteTransaction) error {

            // Insert order
            orderMutation := spanner.InsertOrUpdate("Orders",
                []string{"UserId", "OrderId", "Status", "CreatedAt"},
                []interface{}{userId, orderId, "pending", spanner.CommitTimestamp})

            mutations := []*spanner.Mutation{orderMutation}

            // Insert items
            for i, item := range items {
                itemMutation := spanner.InsertOrUpdate("OrderItems",
                    []string{"UserId", "OrderId", "ItemId", "ProductId", "Quantity", "Price"},
                    []interface{}{userId, orderId, int64(i), item.ProductId, item.Quantity, item.Price})
                mutations = append(mutations, itemMutation)
            }

            return txn.BufferWrite(mutations)
        })

    if err != nil {
        panic(err)
    }
}
```

### AlloyDB

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                     AlloyDB Architecture                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────┐    ┌────────────────┐                      │
│   │    Primary     │    │  Read Pools    │                      │
│   │   Instance     │    │  (Up to 20)    │                      │
│   └───────┬────────┘    └───────┬────────┘                      │
│           │                     │                                │
│           └──────────┬──────────┘                                │
│                      │                                           │
│   ─────────────────────────────────────────────────────────────  │
│                      │                                           │
│   ┌──────────────────┴─────────────────────────────────────┐    │
│   │              Intelligent Storage                         │    │
│   │  ┌─────────────────────────────────────────────────┐   │    │
│   │  │           Log Processing Service                 │   │    │
│   │  │   - Converts WAL to storage pages               │   │    │
│   │  │   - Parallel processing                         │   │    │
│   │  └─────────────────────────────────────────────────┘   │    │
│   │  ┌────────────┐  ┌────────────┐  ┌────────────┐       │    │
│   │  │  Block     │  │  Block     │  │  Block     │       │    │
│   │  │  Server 1  │  │  Server 2  │  │  Server 3  │       │    │
│   │  └────────────┘  └────────────┘  └────────────┘       │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
│   Performance vs Cloud SQL:                                     │
│   - 4x faster OLTP                                              │
│   - 100x faster analytical queries                              │
│   - Columnar engine for analytics                               │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Cloud SQL vs AlloyDB Decision

```
┌─────────────────────────────────────────────────────────────────┐
│                 Cloud SQL vs AlloyDB Decision                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Choose Cloud SQL when:                                         │
│  ✓ Standard PostgreSQL/MySQL workloads                          │
│  ✓ Cost-sensitive (AlloyDB ~2x price)                           │
│  ✓ Need MySQL or SQL Server                                     │
│  ✓ Simple CRUD applications                                     │
│                                                                  │
│  Choose AlloyDB when:                                           │
│  ✓ High-performance PostgreSQL required                         │
│  ✓ Mixed OLTP + analytics workloads                             │
│  ✓ Need AI/ML integration                                       │
│  ✓ Large-scale enterprise apps                                  │
│  ✓ Require columnar analytics                                   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Azure Databases {#azure-databases}

### Cosmos DB Consistency Levels

```
┌─────────────────────────────────────────────────────────────────┐
│                Cosmos DB Consistency Spectrum                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Strong ◄───────────────────────────────────────► Eventual     │
│                                                                  │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐  │
│   │ STRONG  │ │ BOUNDED │ │ SESSION │ │CONSISTENT│ │EVENTUAL │  │
│   │         │ │STALENESS│ │         │ │ PREFIX  │ │         │  │
│   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘  │
│        │          │          │          │          │           │
│   ┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐┌────┴────┐     │
│   │Linearize││ K vers  ││Read your││ In-order ││ No order│     │
│   │ability  ││ or T    ││  writes ││ reads    ││guarantee│     │
│   │         ││ behind  ││         ││          ││         │     │
│   └────┬────┘└────┬────┘└────┬────┘└────┬────┘└────┬────┘     │
│        │          │          │          │          │           │
│   High ◄────────────────────────────────────────► Low          │
│   Latency                                      Latency          │
│                                                                  │
│   Low ◄─────────────────────────────────────────► High          │
│   Availability                              Availability         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**When to Use Each Level:**

| Level | Guarantee | Use Case | RU Cost |
|-------|-----------|----------|---------|
| Strong | Linearizable | Financial transactions | 2x |
| Bounded Staleness | Max K versions behind | Gaming leaderboards | 1.5x |
| Session (Default) | Read-your-writes | User sessions, shopping carts | 1x |
| Consistent Prefix | Ordered reads | Social feeds, timelines | 1x |
| Eventual | No ordering | Analytics, logs | 1x |

**Cosmos DB with .NET:**
```csharp
using Microsoft.Azure.Cosmos;

public class CosmosDbService
{
    private readonly Container _container;

    public CosmosDbService(string connectionString, string databaseId, string containerId)
    {
        var client = new CosmosClient(connectionString, new CosmosClientOptions
        {
            ConsistencyLevel = ConsistencyLevel.Session,
            ApplicationRegion = Regions.EastUS
        });

        _container = client.GetContainer(databaseId, containerId);
    }

    // Create item
    public async Task<T> CreateAsync<T>(T item, string partitionKey)
    {
        var response = await _container.CreateItemAsync(
            item,
            new PartitionKey(partitionKey));

        Console.WriteLine($"Request charge: {response.RequestCharge} RUs");
        return response.Resource;
    }

    // Read with strong consistency override
    public async Task<T> ReadStrongAsync<T>(string id, string partitionKey)
    {
        var response = await _container.ReadItemAsync<T>(
            id,
            new PartitionKey(partitionKey),
            new ItemRequestOptions
            {
                ConsistencyLevel = ConsistencyLevel.Strong
            });

        return response.Resource;
    }

    // Query with continuation
    public async Task<(List<T> Items, string ContinuationToken)> QueryAsync<T>(
        string query,
        string continuationToken = null)
    {
        var queryDefinition = new QueryDefinition(query);
        var items = new List<T>();

        using var iterator = _container.GetItemQueryIterator<T>(
            queryDefinition,
            continuationToken,
            new QueryRequestOptions { MaxItemCount = 100 });

        while (iterator.HasMoreResults)
        {
            var response = await iterator.ReadNextAsync();
            items.AddRange(response);

            if (items.Count >= 100)
            {
                return (items, response.ContinuationToken);
            }
        }

        return (items, null);
    }

    // Transactional batch
    public async Task ExecuteBatchAsync(string partitionKey, List<(string id, object item)> operations)
    {
        var batch = _container.CreateTransactionalBatch(new PartitionKey(partitionKey));

        foreach (var (id, item) in operations)
        {
            batch.UpsertItem(item);
        }

        using var response = await batch.ExecuteAsync();

        if (!response.IsSuccessStatusCode)
        {
            throw new Exception($"Batch failed: {response.StatusCode}");
        }
    }
}
```

---

## Serverless Databases {#serverless-databases}

### Comparison Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│               Serverless Database Comparison                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                  Aurora         Neon      PlanetScale            │
│                 Serverless                                       │
│  ────────────────────────────────────────────────────────────   │
│  Engine         MySQL/PG      PostgreSQL    MySQL                │
│  ────────────────────────────────────────────────────────────   │
│  Scale to 0     No (0.5 ACU)    Yes          Yes                 │
│  ────────────────────────────────────────────────────────────   │
│  Branching      No              Yes          Yes                 │
│  ────────────────────────────────────────────────────────────   │
│  Min Price      ~$43/mo        Free tier    Free tier            │
│  ────────────────────────────────────────────────────────────   │
│  Cold Start     N/A             ~500ms       ~1s                 │
│  ────────────────────────────────────────────────────────────   │
│  Max Scale      128 ACU         8 CU         Unlimited*          │
│  ────────────────────────────────────────────────────────────   │
│  Best For       Enterprise    Startups/Dev  Startups/Dev         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Neon (Serverless PostgreSQL)

**Key Features:**
```
┌─────────────────────────────────────────────────────────────────┐
│                     Neon Architecture                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Compute Nodes                         │   │
│   │   Scale: 0.25 CU to 8 CU                                │   │
│   │   Autoscaling: Based on load                            │   │
│   │   Scale to Zero: After 5 min inactivity                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Pageserver                            │   │
│   │   - On-demand page loading                              │   │
│   │   - Copy-on-write branching                             │   │
│   │   - WAL processing                                      │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   Object Storage (S3)                    │   │
│   │   - Durable storage                                     │   │
│   │   - Unlimited capacity                                  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   Branching:                                                    │
│   main ─────●─────●─────●─────●                                 │
│              \                                                   │
│               └──► feature-1 (instant copy, shared storage)     │
│                     \                                            │
│                      └──► preview-pr-123                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Neon with Prisma:**
```typescript
// schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id        Int      @id @default(autoincrement())
  title     String
  content   String?
  published Boolean  @default(false)
  author    User     @relation(fields: [authorId], references: [id])
  authorId  Int
  createdAt DateTime @default(now())
}

// Application code
import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  // Create user with posts
  const user = await prisma.user.create({
    data: {
      email: 'alice@example.com',
      name: 'Alice',
      posts: {
        create: [
          { title: 'Hello World', content: 'My first post' },
          { title: 'Second Post', published: true }
        ]
      }
    },
    include: { posts: true }
  })

  console.log('Created user:', user)

  // Query with filtering
  const publishedPosts = await prisma.post.findMany({
    where: { published: true },
    include: { author: true },
    orderBy: { createdAt: 'desc' }
  })

  console.log('Published posts:', publishedPosts)
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
```

### PlanetScale (Serverless MySQL)

**Branching Workflow:**
```
┌─────────────────────────────────────────────────────────────────┐
│                PlanetScale Branch Workflow                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Production (main)                                             │
│   ─────●─────●─────●─────●─────●─────●─────●                    │
│                     \           \                                │
│                      \           └─► Deploy Request              │
│                       \              (Review changes)            │
│                        \                    │                    │
│                         \                   ▼                    │
│                          └─► feature-branch                     │
│                               ─────●─────●                      │
│                                     │                            │
│                               Schema changes                     │
│                               (Non-blocking DDL)                 │
│                                                                  │
│   Deploy Request:                                               │
│   1. Create PR-like review                                      │
│   2. Show schema diff                                           │
│   3. Analyze for compatibility                                  │
│   4. Deploy with zero downtime                                  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**PlanetScale CLI Workflow:**
```bash
# Create development branch
pscale branch create mydb feature-auth

# Connect to branch (local development)
pscale connect mydb feature-auth --port 3309

# Make schema changes
mysql -h 127.0.0.1 -P 3309 -u root << EOF
ALTER TABLE users ADD COLUMN avatar_url VARCHAR(255);
CREATE INDEX idx_users_email ON users(email);
EOF

# Create deploy request
pscale deploy-request create mydb feature-auth

# Deploy to production (after review)
pscale deploy-request deploy mydb 1

# Delete branch after merge
pscale branch delete mydb feature-auth
```

### Supabase vs Firebase

```
┌─────────────────────────────────────────────────────────────────┐
│                  Supabase vs Firebase                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│                     Supabase              Firebase               │
│  ─────────────────────────────────────────────────────────────  │
│  Database         PostgreSQL          Firestore (NoSQL)         │
│  ─────────────────────────────────────────────────────────────  │
│  Query Language   SQL                 Document queries          │
│  ─────────────────────────────────────────────────────────────  │
│  Self-Host        Yes (open source)   No                        │
│  ─────────────────────────────────────────────────────────────  │
│  Auth             Built-in            Firebase Auth             │
│  ─────────────────────────────────────────────────────────────  │
│  Real-time        PostgreSQL LISTEN   Native real-time          │
│  ─────────────────────────────────────────────────────────────  │
│  Storage          S3-compatible       Firebase Storage          │
│  ─────────────────────────────────────────────────────────────  │
│  Functions        Edge (Deno)         Cloud Functions           │
│  ─────────────────────────────────────────────────────────────  │
│  Lock-in          Low                 High                      │
│  ─────────────────────────────────────────────────────────────  │
│  Best For         SQL lovers,         Mobile apps,              │
│                   open source fans    Google ecosystem          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Supabase with JavaScript:**
```typescript
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_ANON_KEY!
)

// ============================================
// CRUD Operations
// ============================================

// Create
async function createUser(email: string, name: string) {
  const { data, error } = await supabase
    .from('users')
    .insert({ email, name })
    .select()
    .single()

  if (error) throw error
  return data
}

// Read with filtering
async function getPublishedPosts(limit = 10) {
  const { data, error } = await supabase
    .from('posts')
    .select(`
      id,
      title,
      content,
      created_at,
      author:users(id, name, email)
    `)
    .eq('published', true)
    .order('created_at', { ascending: false })
    .limit(limit)

  if (error) throw error
  return data
}

// Update
async function updatePost(id: number, updates: Partial<Post>) {
  const { data, error } = await supabase
    .from('posts')
    .update(updates)
    .eq('id', id)
    .select()
    .single()

  if (error) throw error
  return data
}

// Delete
async function deletePost(id: number) {
  const { error } = await supabase
    .from('posts')
    .delete()
    .eq('id', id)

  if (error) throw error
}

// ============================================
// Real-time Subscriptions
// ============================================

function subscribeToNewPosts(callback: (post: Post) => void) {
  const subscription = supabase
    .channel('posts')
    .on(
      'postgres_changes',
      { event: 'INSERT', schema: 'public', table: 'posts' },
      (payload) => callback(payload.new as Post)
    )
    .subscribe()

  return () => subscription.unsubscribe()
}

// ============================================
// Row Level Security (RLS)
// ============================================

// SQL for RLS policies
/*
-- Enable RLS
ALTER TABLE posts ENABLE ROW LEVEL SECURITY;

-- Users can only see their own posts
CREATE POLICY "Users can view own posts" ON posts
  FOR SELECT
  USING (auth.uid() = author_id);

-- Users can only update their own posts
CREATE POLICY "Users can update own posts" ON posts
  FOR UPDATE
  USING (auth.uid() = author_id);

-- Anyone can view published posts
CREATE POLICY "Anyone can view published posts" ON posts
  FOR SELECT
  USING (published = true);
*/

// ============================================
// Auth Integration
// ============================================

async function signUp(email: string, password: string) {
  const { data, error } = await supabase.auth.signUp({
    email,
    password
  })

  if (error) throw error
  return data
}

async function signIn(email: string, password: string) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password
  })

  if (error) throw error
  return data
}
```

---

## Multi-Region & High Availability {#multi-region-ha}

### DR Patterns

```
┌─────────────────────────────────────────────────────────────────┐
│                    DR Pattern Comparison                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Pattern           RTO        RPO       Cost      Complexity    │
│  ────────────────────────────────────────────────────────────   │
│  Backup/Restore    Hours      Hours     $         Low           │
│  ────────────────────────────────────────────────────────────   │
│  Pilot Light       10-30 min  Minutes   $$        Medium        │
│  ────────────────────────────────────────────────────────────   │
│  Warm Standby      Minutes    Seconds   $$$       High          │
│  ────────────────────────────────────────────────────────────   │
│  Active-Active     Seconds    Zero      $$$$      Very High     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   Active-Active Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│        Region A                        Region B                  │
│   ┌─────────────────┐            ┌─────────────────┐            │
│   │   Application   │            │   Application   │            │
│   │    Servers      │            │    Servers      │            │
│   └────────┬────────┘            └────────┬────────┘            │
│            │                              │                      │
│            ▼                              ▼                      │
│   ┌─────────────────┐            ┌─────────────────┐            │
│   │    Database     │◄──────────►│    Database     │            │
│   │    (Writer)     │  Bi-dir    │    (Writer)     │            │
│   │                 │  Repl      │                 │            │
│   └─────────────────┘            └─────────────────┘            │
│                                                                  │
│   Services:                                                     │
│   - DynamoDB Global Tables                                      │
│   - Cosmos DB Multi-region Writes                               │
│   - Cloud Spanner Multi-region                                  │
│   - Aurora DSQL (Dec 2024)                                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Aurora Global Database

```
┌─────────────────────────────────────────────────────────────────┐
│                  Aurora Global Database                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Primary Region (us-east-1)                                    │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │ │
│   │  │ Writer  │  │ Reader  │  │ Reader  │                   │ │
│   │  └────┬────┘  └─────────┘  └─────────┘                   │ │
│   │       │                                                   │ │
│   │  ┌────┴────────────────────────────────────────────────┐ │ │
│   │  │              Aurora Storage (6 copies)               │ │ │
│   │  └──────────────────────────┬──────────────────────────┘ │ │
│   └─────────────────────────────┼─────────────────────────────┘ │
│                                 │                                │
│                    <1 second replication                        │
│                                 │                                │
│   Secondary Region (eu-west-1)  ▼                               │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │  ┌─────────┐  ┌─────────┐  ┌─────────┐                   │ │
│   │  │ Reader  │  │ Reader  │  │ Reader  │  (Promote to      │ │
│   │  │(Headless│  └─────────┘  └─────────┘   Writer on       │ │
│   │  │ Writer) │                             failover)        │ │
│   │  └────┬────┘                                              │ │
│   │       │                                                   │ │
│   │  ┌────┴────────────────────────────────────────────────┐ │ │
│   │  │              Aurora Storage (6 copies)               │ │ │
│   │  └─────────────────────────────────────────────────────┘ │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                  │
│   Failover: <1 minute RTO, <1 second RPO                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Terraform for Aurora Global:**
```python
# Primary cluster
resource "aws_rds_global_cluster" "global" {
  global_cluster_identifier = "global-production"
  engine                    = "aurora-postgresql"
  engine_version           = "15.4"
  database_name            = "myapp"
}

resource "aws_rds_cluster" "primary" {
  provider                  = aws.us_east_1
  cluster_identifier        = "primary-cluster"
  engine                   = aws_rds_global_cluster.global.engine
  engine_version           = aws_rds_global_cluster.global.engine_version
  global_cluster_identifier = aws_rds_global_cluster.global.id
  master_username          = "admin"
  master_password          = var.db_password

  # ... other settings
}

# Secondary cluster
resource "aws_rds_cluster" "secondary" {
  provider                  = aws.eu_west_1
  cluster_identifier        = "secondary-cluster"
  engine                   = aws_rds_global_cluster.global.engine
  engine_version           = aws_rds_global_cluster.global.engine_version
  global_cluster_identifier = aws_rds_global_cluster.global.id

  # Secondary doesn't need master credentials
  # It replicates from primary

  depends_on = [aws_rds_cluster.primary]
}
```

---

## Migration Strategies {#migration-strategies}

### AWS DMS Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DMS Migration Workflow                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Phase 1: Assessment                                           │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  AWS Schema Conversion Tool (SCT)                        │   │
│   │  - Analyze source schema                                 │   │
│   │  - Generate compatibility report                         │   │
│   │  - Identify manual conversion needs                      │   │
│   │  - Convert schema to target dialect                      │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   Phase 2: Schema Migration                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  Deploy converted schema to target database              │   │
│   │  - Tables, indexes, constraints                         │   │
│   │  - Stored procedures (may need manual conversion)       │   │
│   │  - Triggers, views                                      │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   Phase 3: Data Migration (DMS)                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                                                          │   │
│   │   Source DB ──► Replication Instance ──► Target DB      │   │
│   │                                                          │   │
│   │   Step 1: Full Load                                     │   │
│   │   - Bulk copy all existing data                         │   │
│   │   - Can run while source is live                        │   │
│   │                                                          │   │
│   │   Step 2: Change Data Capture (CDC)                     │   │
│   │   - Replicate ongoing changes                           │   │
│   │   - Keep target in sync                                 │   │
│   │   - Continue until cutover                              │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   Phase 4: Validation & Cutover                                 │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  - DMS Data Validation                                  │   │
│   │  - Application testing against target                   │   │
│   │  - Stop source writes                                   │   │
│   │  - Final CDC sync                                       │   │
│   │  - Switch application connection strings                │   │
│   │  - Monitor and verify                                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**DMS Terraform Configuration:**
```python
# Replication instance
resource "aws_dms_replication_instance" "main" {
  replication_instance_id     = "migration-instance"
  replication_instance_class  = "dms.r5.xlarge"
  allocated_storage          = 100

  vpc_security_group_ids     = [aws_security_group.dms.id]
  replication_subnet_group_id = aws_dms_replication_subnet_group.main.id

  publicly_accessible        = false
  multi_az                   = true

  tags = {
    Name = "migration-instance"
  }
}

# Source endpoint (Oracle)
resource "aws_dms_endpoint" "source" {
  endpoint_id   = "oracle-source"
  endpoint_type = "source"
  engine_name   = "oracle"

  server_name   = var.oracle_host
  port          = 1521
  database_name = var.oracle_sid
  username      = var.oracle_user
  password      = var.oracle_password

  extra_connection_attributes = "addSupplementalLogging=Y"
}

# Target endpoint (Aurora PostgreSQL)
resource "aws_dms_endpoint" "target" {
  endpoint_id   = "aurora-target"
  endpoint_type = "target"
  engine_name   = "aurora-postgresql"

  server_name   = aws_rds_cluster.aurora.endpoint
  port          = 5432
  database_name = "myapp"
  username      = var.aurora_user
  password      = var.aurora_password
}

# Replication task
resource "aws_dms_replication_task" "main" {
  replication_task_id      = "oracle-to-aurora"
  migration_type           = "full-load-and-cdc"
  replication_instance_arn = aws_dms_replication_instance.main.replication_instance_arn
  source_endpoint_arn      = aws_dms_endpoint.source.endpoint_arn
  target_endpoint_arn      = aws_dms_endpoint.target.endpoint_arn

  table_mappings = jsonencode({
    rules = [
      {
        rule-type = "selection"
        rule-id   = "1"
        rule-name = "include-all"
        object-locator = {
          schema-name = "MYSCHEMA"
          table-name  = "%"
        }
        rule-action = "include"
      }
    ]
  })

  replication_task_settings = jsonencode({
    TargetMetadata = {
      TargetSchema         = ""
      SupportLobs          = true
      FullLobMode          = false
      LobChunkSize         = 64
      LimitedSizeLobMode   = true
      LobMaxSize           = 32
    }
    FullLoadSettings = {
      TargetTablePrepMode = "DROP_AND_CREATE"
    }
    Logging = {
      EnableLogging = true
    }
  })
}
```

---

## Security Best Practices {#security-best-practices}

### Defense in Depth

```
┌─────────────────────────────────────────────────────────────────┐
│                   Security Layers                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Layer 1: Network Security                                     │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  - VPC isolation (private subnets only)                 │   │
│   │  - Security Groups (least privilege)                    │   │
│   │  - VPC Endpoints (no internet exposure)                 │   │
│   │  - Network ACLs                                         │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   Layer 2: Authentication                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  - IAM Database Authentication                          │   │
│   │  - Secrets Manager for credentials                      │   │
│   │  - Automatic credential rotation                        │   │
│   │  - MFA for admin access                                 │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   Layer 3: Encryption                                           │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  - At Rest: KMS (AES-256)                               │   │
│   │  - In Transit: TLS 1.2/1.3                              │   │
│   │  - Client-side encryption (optional)                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│   Layer 4: Audit & Monitoring                                   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │  - CloudTrail for API calls                             │   │
│   │  - Database Activity Streams                            │   │
│   │  - CloudWatch Logs for queries                          │   │
│   │  - GuardDuty for threat detection                       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**IAM Database Authentication (Aurora/RDS):**
```python
import boto3
import psycopg2

def get_db_connection():
    # Generate IAM auth token
    client = boto3.client('rds')
    token = client.generate_db_auth_token(
        DBHostname='mydb.cluster-xxx.us-east-1.rds.amazonaws.com',
        Port=5432,
        DBUsername='iam_user',
        Region='us-east-1'
    )

    # Connect using token as password
    conn = psycopg2.connect(
        host='mydb.cluster-xxx.us-east-1.rds.amazonaws.com',
        port=5432,
        database='myapp',
        user='iam_user',
        password=token,
        sslmode='require',
        sslrootcert='/path/to/rds-ca-2019-root.pem'
    )

    return conn

# IAM policy for database access
"""
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "rds-db:connect",
            "Resource": "arn:aws:rds-db:us-east-1:123456789012:dbuser:cluster-xxx/iam_user"
        }
    ]
}
"""
```

**Secrets Manager Rotation:**
```python
resource "aws_secretsmanager_secret" "db_password" {
  name = "production/database/master"

  tags = {
    Environment = "production"
  }
}

resource "aws_secretsmanager_secret_rotation" "db_rotation" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = aws_lambda_function.secret_rotation.arn

  rotation_rules {
    automatically_after_days = 30
  }
}

# Application retrieves secret
import boto3
import json

def get_db_credentials():
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(
        SecretId='production/database/master'
    )
    return json.loads(response['SecretString'])
```

---

## Cost Optimization {#cost-optimization}

### Pricing Comparison

```
┌─────────────────────────────────────────────────────────────────┐
│              Monthly Cost Comparison (Production)                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Database                 Instance         Monthly Cost          │
│  ────────────────────────────────────────────────────────────   │
│  RDS PostgreSQL          db.r6g.xlarge     ~$550                │
│  Aurora PostgreSQL       db.r6g.xlarge     ~$660 (+20%)         │
│  ────────────────────────────────────────────────────────────   │
│  Cloud SQL PostgreSQL    db-custom-4-16384 ~$450                │
│  AlloyDB                 4 vCPU, 32 GB     ~$900                │
│  Cloud Spanner           3 nodes           ~$2,000              │
│  ────────────────────────────────────────────────────────────   │
│  Azure SQL Database      S3 (100 DTU)      ~$150                │
│  Cosmos DB               400 RU/s          ~$24 (serverless)    │
│  ────────────────────────────────────────────────────────────   │
│  Neon                    Scale to zero     ~$19 (Pro tier)      │
│  PlanetScale             Scaler            ~$29                 │
│                                                                  │
│  Note: Prices are approximate, vary by region and usage         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Savings Strategies

```
┌─────────────────────────────────────────────────────────────────┐
│                  Cost Optimization Strategies                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. Reserved Instances / Commitments                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Commitment     Savings    Best For                        │ │
│  │  ─────────────────────────────────────────────────────────│ │
│  │  1-yr No Upfront  ~30%    Uncertain growth                 │ │
│  │  1-yr All Upfront ~40%    Stable workloads                 │ │
│  │  3-yr All Upfront ~60-72% Long-term production             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  2. Right-Sizing                                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  - Monitor CPU/Memory utilization                          │ │
│  │  - Use Performance Insights                                │ │
│  │  - Target 60-70% utilization                               │ │
│  │  - Downsize over-provisioned instances                     │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  3. Serverless for Variable Workloads                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  - Dev/Test: Aurora Serverless, Neon                       │ │
│  │  - Preview environments: Branch databases                  │ │
│  │  - Infrequent access: Scale to zero                        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  4. Read Replicas Strategy                                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  - Offload reads to replicas                               │ │
│  │  - Use smaller primary instance                            │ │
│  │  - Replicas can be different instance class                │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  5. Storage Optimization                                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  - gp3 instead of io1 for most workloads                   │ │
│  │  - Archive old data to S3                                  │ │
│  │  - Use TTL for automatic cleanup (DynamoDB)                │ │
│  │  - Compress large text/JSON fields                         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Monitoring & Performance {#monitoring-performance}

### RDS Performance Insights

```
┌─────────────────────────────────────────────────────────────────┐
│              Performance Insights Dashboard                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Database Load (Active Sessions)                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 10│                    ████                                │ │
│  │   │                   █████                                │ │
│  │  8│         ████     ██████                                │ │
│  │   │        █████    ███████                                │ │
│  │  6│  ███  ██████   ████████ ───── vCPU limit (4)          │ │
│  │   │ ████ ███████  █████████                                │ │
│  │  4│█████████████ ██████████                                │ │
│  │   │██████████████████████████                              │ │
│  │  2│██████████████████████████████                          │ │
│  │   │████████████████████████████████                        │ │
│  │  0└────────────────────────────────                        │ │
│  │    09:00  10:00  11:00  12:00  13:00                       │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Wait Events Breakdown:                                         │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ CPU             ████████████████████████████████ 45%       │ │
│  │ I/O:wait        ████████████████ 25%                       │ │
│  │ Lock:wait       ████████ 15%                               │ │
│  │ LWLock:wait     ████ 10%                                   │ │
│  │ Client:wait     ██ 5%                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  Top SQL by Load:                                               │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ 1. SELECT * FROM orders WHERE status = 'pending'  (45%)    │ │
│  │ 2. UPDATE users SET last_login = NOW() WHERE...   (20%)    │ │
│  │ 3. INSERT INTO audit_log VALUES...                (15%)    │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**CloudWatch Alarms:**
```python
resource "aws_cloudwatch_metric_alarm" "db_cpu" {
  alarm_name          = "rds-high-cpu"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80
  alarm_description   = "Database CPU > 80%"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "db_connections" {
  alarm_name          = "rds-connection-limit"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "DatabaseConnections"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 150  # e.g., 75% of max_connections
  alarm_description   = "Database connections approaching limit"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "db_storage" {
  alarm_name          = "rds-low-storage"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 1
  metric_name         = "FreeStorageSpace"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 10737418240  # 10 GB in bytes
  alarm_description   = "Database storage < 10 GB"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}
```

---

## Decision Framework {#decision-framework}

### Database Selection Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                  Cloud Database Decision Tree                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Start: What's your primary requirement?                       │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Relational (SQL)?                                        │   │
│   │   │                                                      │   │
│   │   ├─► Need global distribution?                          │   │
│   │   │     ├─► Yes ──► Cloud Spanner or Aurora DSQL        │   │
│   │   │     └─► No ──► Aurora/RDS, Cloud SQL, Azure SQL     │   │
│   │   │                                                      │   │
│   │   ├─► Need serverless/branching?                         │   │
│   │   │     └─► Yes ──► Neon (PG), PlanetScale (MySQL)      │   │
│   │   │                                                      │   │
│   │   └─► High analytics needs?                              │   │
│   │         └─► Yes ──► AlloyDB or Aurora with Redshift     │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ NoSQL (Key-Value/Document)?                              │   │
│   │   │                                                      │   │
│   │   ├─► AWS ecosystem?                                     │   │
│   │   │     └─► DynamoDB                                    │   │
│   │   │                                                      │   │
│   │   ├─► Multi-cloud/Flexible consistency?                  │   │
│   │   │     └─► Cosmos DB                                   │   │
│   │   │                                                      │   │
│   │   └─► Full MongoDB features?                             │   │
│   │         └─► MongoDB Atlas                               │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Caching/In-Memory?                                       │   │
│   │   │                                                      │   │
│   │   ├─► Caching layer only?                                │   │
│   │   │     └─► ElastiCache                                 │   │
│   │   │                                                      │   │
│   │   └─► Durable in-memory DB?                              │   │
│   │         └─► MemoryDB                                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ Full-stack (backend as service)?                         │   │
│   │   │                                                      │   │
│   │   ├─► Open source preference?                            │   │
│   │   │     └─► Supabase                                    │   │
│   │   │                                                      │   │
│   │   └─► Google ecosystem?                                  │   │
│   │         └─► Firebase                                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Quick Reference: When to Use What

| Scenario | Recommended | Alternative |
|----------|-------------|-------------|
| Standard web app (AWS) | Aurora PostgreSQL | RDS PostgreSQL |
| Standard web app (GCP) | Cloud SQL | AlloyDB (high perf) |
| Standard web app (Azure) | Azure SQL | Cosmos DB |
| Global app, strong consistency | Cloud Spanner | Aurora DSQL |
| High-scale key-value | DynamoDB | Cosmos DB |
| Startup, fast iteration | Neon/PlanetScale | Supabase |
| Mobile app backend | Firebase | Supabase |
| Caching layer | ElastiCache | MemoryDB |
| Time-series/IoT | Timestream | InfluxDB Cloud |
| Analytics/OLAP | Redshift | BigQuery |

---

## Practical Examples {#practical-examples}

### Complete Production Setup (AWS)

```python
# main.tf - Production Aurora PostgreSQL Setup

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

# VPC & Networking
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "production-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = false

  tags = {
    Environment = "production"
  }
}

# Security Group
resource "aws_security_group" "aurora" {
  name        = "aurora-sg"
  description = "Security group for Aurora cluster"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# KMS Key for encryption
resource "aws_kms_key" "aurora" {
  description             = "KMS key for Aurora encryption"
  deletion_window_in_days = 30
  enable_key_rotation     = true
}

# Subnet Group
resource "aws_db_subnet_group" "aurora" {
  name       = "aurora-subnet-group"
  subnet_ids = module.vpc.private_subnets
}

# Parameter Group
resource "aws_rds_cluster_parameter_group" "aurora" {
  family = "aurora-postgresql15"
  name   = "aurora-production-params"

  parameter {
    name  = "shared_preload_libraries"
    value = "pg_stat_statements,auto_explain"
  }

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"
  }

  parameter {
    name  = "auto_explain.log_min_duration"
    value = "1000"
  }
}

# Aurora Cluster
resource "aws_rds_cluster" "main" {
  cluster_identifier = "production-aurora"
  engine            = "aurora-postgresql"
  engine_version    = "15.4"
  database_name     = "myapp"

  master_username                     = "admin"
  manage_master_user_password         = true
  master_user_secret_kms_key_id      = aws_kms_key.aurora.id

  db_subnet_group_name               = aws_db_subnet_group.aurora.name
  vpc_security_group_ids             = [aws_security_group.aurora.id]
  db_cluster_parameter_group_name    = aws_rds_cluster_parameter_group.aurora.name

  storage_encrypted = true
  kms_key_id       = aws_kms_key.aurora.arn

  backup_retention_period = 7
  preferred_backup_window = "03:00-04:00"
  preferred_maintenance_window = "Mon:04:00-Mon:05:00"

  enabled_cloudwatch_logs_exports = ["postgresql"]

  deletion_protection = true
  skip_final_snapshot = false
  final_snapshot_identifier = "production-aurora-final-${formatdate("YYYY-MM-DD", timestamp())}"

  tags = {
    Environment = "production"
  }
}

# Writer Instance
resource "aws_rds_cluster_instance" "writer" {
  identifier         = "production-aurora-writer"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.r6g.xlarge"
  engine            = aws_rds_cluster.main.engine
  engine_version    = aws_rds_cluster.main.engine_version

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.aurora.arn

  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  tags = {
    Role = "writer"
  }
}

# Reader Instances
resource "aws_rds_cluster_instance" "readers" {
  count              = 2
  identifier         = "production-aurora-reader-${count.index}"
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.r6g.large"
  engine            = aws_rds_cluster.main.engine
  engine_version    = aws_rds_cluster.main.engine_version

  performance_insights_enabled    = true
  performance_insights_kms_key_id = aws_kms_key.aurora.arn

  monitoring_interval = 60
  monitoring_role_arn = aws_iam_role.rds_monitoring.arn

  tags = {
    Role = "reader"
  }
}

# Enhanced Monitoring IAM Role
resource "aws_iam_role" "rds_monitoring" {
  name = "rds-monitoring-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "monitoring.rds.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

# CloudWatch Alarms
resource "aws_cloudwatch_metric_alarm" "cpu_high" {
  alarm_name          = "aurora-cpu-high"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 2
  metric_name         = "CPUUtilization"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 80

  dimensions = {
    DBClusterIdentifier = aws_rds_cluster.main.cluster_identifier
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

resource "aws_cloudwatch_metric_alarm" "freeable_memory" {
  alarm_name          = "aurora-memory-low"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = 2
  metric_name         = "FreeableMemory"
  namespace           = "AWS/RDS"
  period              = 300
  statistic           = "Average"
  threshold           = 1073741824  # 1 GB

  dimensions = {
    DBClusterIdentifier = aws_rds_cluster.main.cluster_identifier
  }

  alarm_actions = [aws_sns_topic.alerts.arn]
}

# Outputs
output "cluster_endpoint" {
  value = aws_rds_cluster.main.endpoint
}

output "reader_endpoint" {
  value = aws_rds_cluster.main.reader_endpoint
}

output "secret_arn" {
  value = aws_rds_cluster.main.master_user_secret[0].secret_arn
}
```

---

## Summary

### Key Takeaways

1. **Choose Based on Requirements:**
   - Global consistency → Cloud Spanner, Aurora DSQL
   - Standard workloads → Aurora, RDS, Cloud SQL
   - Serverless/Dev → Neon, PlanetScale
   - Key-Value scale → DynamoDB

2. **Cost Optimization:**
   - Reserved Instances: 40-72% savings
   - Serverless for variable workloads
   - Right-size using Performance Insights
   - Read replicas to offload primary

3. **Security First:**
   - VPC isolation (private subnets only)
   - IAM database authentication
   - Encryption at rest and in transit
   - Secrets Manager with rotation

4. **High Availability:**
   - Multi-AZ for production
   - Aurora Global Database for DR
   - Regular backup testing
   - Document RTO/RPO requirements

5. **Migration Strategy:**
   - Assessment first (SCT)
   - Full load + CDC for minimal downtime
   - Validate before cutover
   - Keep rollback plan ready

---

## Quick Commands Reference

```bash
# AWS CLI
aws rds describe-db-clusters --query 'DBClusters[*].[DBClusterIdentifier,Status]'
aws rds create-db-cluster-snapshot --db-cluster-identifier my-cluster --db-cluster-snapshot-identifier my-snapshot
aws rds describe-events --source-type db-cluster --duration 1440

# GCP gcloud
gcloud sql instances list
gcloud spanner instances list
gcloud sql operations list --instance=my-instance

# Azure CLI
az sql server list
az cosmosdb list
az sql db show-connection-string --server my-server --name my-db

# PlanetScale CLI
pscale branch list mydb
pscale connect mydb main --port 3309
pscale deploy-request create mydb feature-branch

# Neon CLI
neon branches list
neon connection-string
```
