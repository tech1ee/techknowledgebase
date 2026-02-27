---
title: "NoSQL Databases: Complete Guide"
type: guide
status: published
tags:
  - topic/databases
  - type/guide
  - level/intermediate
related:
  - "[[sql-databases-complete]]"
  - "[[databases-nosql-comparison]]"
  - "[[architecture-distributed-systems]]"
modified: 2026-02-13
prerequisites:
  - "[[databases-nosql-comparison]]"
  - "[[databases-fundamentals-complete]]"
reading_time: 35
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# NoSQL Databases: Complete Guide

> Полное руководство по NoSQL базам данных — Document, Key-Value, Wide-Column, Graph, Time-Series

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Основы баз данных** | Понимание SQL, ACID, ключи, индексы | [[databases-fundamentals-complete]] |
| **JSON** | Document DBs хранят данные в JSON-like формате | [[json-basics]] |
| **CAP теорема** | NoSQL часто жертвует C ради A и P | [[databases-fundamentals-complete]] |
| **Распределённые системы** | NoSQL часто distributed by design | [[distributed-systems-basics]] |

### Для кого этот материал

| Уровень | Что получите |
|---------|--------------|
| **SQL-разработчик** | Понимание когда NoSQL лучше SQL и наоборот |
| **Backend разработчик** | MongoDB, Redis, Cassandra — практические паттерны |
| **Архитектор** | Decision framework для выбора типа БД под задачу |

---

## Терминология

> 💡 **Главная аналогия для понимания NoSQL:**
>
> **SQL** = офис с жёстким расписанием (9-18, дресс-код, строгие правила)
> **NoSQL** = коворкинг (гибкий график, любая одежда, каждый работает по-своему)
>
> Оба эффективны — для разных задач!

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **Document DB** | Хранит JSON-подобные документы (MongoDB) | **Папка с документами** — каждый документ может иметь свою структуру |
| **Key-Value** | Простейшая модель: ключ → значение (Redis) | **Камера хранения** — номерок → ячейка с вещами |
| **Wide-Column** | Данные по колонкам, не строкам (Cassandra) | **Таблица Excel с разреженными данными** — не все ячейки заполнены |
| **Graph DB** | Узлы и связи между ними (Neo4j) | **Социальная сеть** — люди и их связи "друзья", "подписчики" |
| **BASE** | Basically Available, Soft state, Eventually consistent | **Компромисс** — система всегда отвечает, но данные могут быть не совсем свежими |
| **Eventual Consistency** | Данные синхронизируются "со временем" | **Слухи** — новость распространяется, но не мгновенно все узнают |
| **Sharding** | Разделение данных по серверам | **Библиотека по этажам** — книги A-M на 1-м, N-Z на 2-м |
| **Replica Set** | Несколько копий данных для отказоустойчивости | **Копии ключей** — потерял один, есть запасной |
| **BSON** | Binary JSON — формат MongoDB | **Сжатый JSON** — быстрее парсится и меньше места |
| **TTL** | Time To Live — автоудаление данных | **Срок годности** — истёк и удалился автоматически |
| **Pub/Sub** | Publish/Subscribe — паттерн обмена сообщениями | **Подписка на канал** — автор публикует, подписчики получают |
| **Aggregation Pipeline** | Цепочка трансформаций в MongoDB | **Конвейер на заводе** — каждый этап обрабатывает и передаёт дальше |
| **Cypher** | Язык запросов Neo4j для графов | **SQL для связей** — MATCH, WHERE, RETURN вместо SELECT |

---

## Теоретические основы: формальный базис NoSQL

### CAP Theorem: формальные определения (Gilbert & Lynch, 2002)

Каждая NoSQL-система делает выбор в рамках CAP:

| Свойство | Формальное определение | Пример |
|----------|----------------------|--------|
| **Consistency** | Каждое чтение возвращает результат последней записи (linearizability) | CP: MongoDB (single-document), HBase |
| **Availability** | Каждый запрос к не-failed узлу получает ответ | AP: Cassandra, DynamoDB, CouchDB |
| **Partition Tolerance** | Система продолжает работать при потере сообщений между узлами | Обязательно для distributed systems |

Brewer (2012) уточнил: выбор CP vs AP делается **per-operation**, а не раз и навсегда для всей системы.

### BASE vs ACID

> **BASE** (Basically Available, Soft state, Eventually consistent) — акроним, противопоставляемый ACID для описания свойств AP-систем. Не является формальной спецификацией (в отличие от ACID), а скорее набором design principles.

**Eventual Consistency** (Vogels, 2009) — формально: если не поступает новых обновлений, все реплики в конечном итоге сойдутся к одному значению. Время сходимости (convergence window) зависит от протокола: **gossip** (Cassandra) — O(log N) раундов, **anti-entropy** — O(N) обменов.

### Vector Clocks и Conflict Resolution (Lamport, 1978; Fidge/Mattern, 1988)

> **Vector Clock** — механизм отслеживания причинно-следственных связей (causality) между событиями в распределённой системе. Каждый узел поддерживает вектор `[c1, c2, ..., cn]`, где `ci` — логическое время узла `i`.

Правило: событие A **happened-before** B (`A → B`) тогда и только тогда, когда `VC(A) < VC(B)` покомпонентно. Если ни `A → B`, ни `B → A` — события **concurrent**, требующие conflict resolution.

| Стратегия | Механизм | Используется в |
|-----------|----------|----------------|
| **Last-Writer-Wins (LWW)** | Timestamp определяет победителя | Cassandra |
| **Vector Clocks** | Клиент разрешает конфликт | Riak (до v2.0) |
| **CRDTs** | Conflict-free merge без координации | Riak (v2.0+), Redis CRDT |

### LSM-Tree vs B-Tree (O'Neil et al., 1996)

NoSQL-базы используют два основных storage engine:

| Свойство | B-Tree | LSM-Tree |
|----------|--------|----------|
| **Write** | O(log N) random I/O | O(1) sequential I/O (append-only) |
| **Read** | O(log N) — одна структура | O(log N × L) — проверка L уровней |
| **Space amplification** | Низкая | Высокая (compaction) |
| **Используется** | PostgreSQL, MySQL/InnoDB, MongoDB (WiredTiger) | Cassandra, RocksDB, LevelDB |

> **Связь**: CAP → [[databases-fundamentals-complete]], Vector Clocks → [[concurrency-fundamentals]], LSM-Tree → [[sql-databases-complete]]

---

## Table of Contents

1. [Введение в NoSQL](#введение-в-nosql)
2. [ACID vs BASE](#acid-vs-base)
3. [Document Databases](#document-databases)
   - [MongoDB Deep Dive](#mongodb-deep-dive)
   - [CouchDB & PouchDB](#couchdb--pouchdb)
   - [Firebase Firestore](#firebase-firestore)
4. [Key-Value Stores](#key-value-stores)
   - [Redis Deep Dive](#redis-deep-dive)
   - [Redis vs Memcached](#redis-vs-memcached)
5. [Wide-Column Stores](#wide-column-stores)
   - [Apache Cassandra](#apache-cassandra)
   - [ScyllaDB](#scylladb)
   - [Amazon DynamoDB](#amazon-dynamodb)
6. [Graph Databases](#graph-databases)
   - [Neo4j Deep Dive](#neo4j-deep-dive)
7. [Time-Series Databases](#time-series-databases)
   - [InfluxDB vs TimescaleDB](#influxdb-vs-timescaledb)
8. [Search Engines](#search-engines)
   - [Elasticsearch](#elasticsearch)
9. [Scaling Strategies](#scaling-strategies)
10. [Design Patterns & Anti-Patterns](#design-patterns--anti-patterns)
11. [When to Use NoSQL vs SQL](#when-to-use-nosql-vs-sql)
12. [Decision Guide](#decision-guide)

---

## Введение в NoSQL

### Что такое NoSQL?

**NoSQL** (Not Only SQL) — семейство нереляционных баз данных, созданных для решения задач, с которыми SQL плохо справляется:

- Горизонтальное масштабирование
- Гибкие схемы данных
- Высокая доступность
- Работа с большими объёмами данных

### Типы NoSQL баз данных

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           NoSQL Database Types                               │
├──────────────────┬──────────────────┬───────────────────┬───────────────────┤
│    Document      │    Key-Value     │   Wide-Column     │      Graph        │
├──────────────────┼──────────────────┼───────────────────┼───────────────────┤
│   MongoDB        │     Redis        │    Cassandra      │      Neo4j        │
│   CouchDB        │   Memcached      │    ScyllaDB       │   Amazon Neptune  │
│   Firestore      │   DynamoDB*      │     HBase         │    ArangoDB       │
└──────────────────┴──────────────────┴───────────────────┴───────────────────┘
           ↓                  ↓                  ↓                  ↓
     JSON/BSON          Key → Value      Column Families    Nodes + Edges
     documents          simple, fast     write-optimized    relationships
```

### Сравнительная таблица

| Тип | Модель данных | Сильные стороны | Слабые стороны | Use Cases |
|-----|---------------|-----------------|----------------|-----------|
| Document | JSON/BSON docs | Гибкая схема, rich queries | Нет joins | CMS, e-commerce, каталоги |
| Key-Value | Key → Value | Fastest reads/writes | Limited queries | Caching, sessions |
| Wide-Column | Column families | Write performance, scale | Complex modeling | Time-series, IoT, logs |
| Graph | Nodes + Relations | Relationship queries | Not for simple data | Social, recommendations |
| Time-Series | Time-indexed | Time-range queries | Specific use case | Metrics, monitoring |

---

## ACID vs BASE

### ACID (Traditional SQL)

```
┌───────────────────────────────────────────────────────────────────┐
│                          ACID Properties                           │
├───────────────────────────────────────────────────────────────────┤
│  Atomicity      │  Транзакция — всё или ничего                    │
│                 │  BEGIN → операции → COMMIT или ROLLBACK         │
├───────────────────────────────────────────────────────────────────┤
│  Consistency    │  БД всегда в валидном состоянии                 │
│                 │  Constraints проверяются перед коммитом         │
├───────────────────────────────────────────────────────────────────┤
│  Isolation      │  Параллельные транзакции не влияют друг на друга│
│                 │  Levels: Read Uncommitted → Serializable        │
├───────────────────────────────────────────────────────────────────┤
│  Durability     │  После COMMIT данные сохранены навсегда         │
│                 │  Даже при сбое питания                          │
└───────────────────────────────────────────────────────────────────┘
```

### BASE (NoSQL Approach)

```
┌───────────────────────────────────────────────────────────────────┐
│                          BASE Properties                           │
├───────────────────────────────────────────────────────────────────┤
│  Basically      │  Система доступна большую часть времени         │
│  Available      │  Partial failures не ломают всю систему         │
├───────────────────────────────────────────────────────────────────┤
│  Soft State     │  Состояние может меняться без input             │
│                 │  Реплики синхронизируются асинхронно            │
├───────────────────────────────────────────────────────────────────┤
│  Eventual       │  Данные станут consistent "когда-нибудь"        │
│  Consistency    │  Не мгновенно, но в итоге — да                  │
└───────────────────────────────────────────────────────────────────┘
```

### Когда что использовать

| Требование | ACID (SQL) | BASE (NoSQL) |
|------------|------------|--------------|
| Банковские транзакции | ✓ | |
| Инвентаризация | ✓ | |
| Social media feeds | | ✓ |
| Кэширование | | ✓ |
| Аналитика real-time | | ✓ |
| Медицинские записи | ✓ | |

### ACID в NoSQL (2024+)

Современные NoSQL поддерживают ACID когда нужно:

```javascript
// MongoDB 4.0+ — Multi-document transactions
const session = client.startSession();
try {
  session.startTransaction();

  await orders.insertOne({ item: "laptop", qty: 1 }, { session });
  await inventory.updateOne(
    { item: "laptop" },
    { $inc: { qty: -1 } },
    { session }
  );

  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
} finally {
  session.endSession();
}
```

---

## Document Databases

### MongoDB Deep Dive

#### Архитектура

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MongoDB Architecture                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        Application Layer                             │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐                │    │
│  │  │ Driver  │  │ Driver  │  │ Driver  │  │  Atlas  │                │    │
│  │  │ Node.js │  │  Java   │  │ Python  │  │   UI    │                │    │
│  │  └────┬────┘  └────┬────┘  └────┬────┘  └────┬────┘                │    │
│  └───────┼────────────┼───────────┼────────────┼───────────────────────┘    │
│          └────────────┴───────────┴────────────┘                            │
│                              │                                               │
│  ┌───────────────────────────┼───────────────────────────────────────────┐  │
│  │                     mongos (Router)                                    │  │
│  │              Routes queries to correct shard                           │  │
│  └───────────────────────────┬───────────────────────────────────────────┘  │
│                              │                                               │
│  ┌───────────────────────────┼───────────────────────────────────────────┐  │
│  │                    Config Servers                                      │  │
│  │               Metadata about shards                                    │  │
│  └───────────────────────────┬───────────────────────────────────────────┘  │
│                              │                                               │
│  ┌───────────────┬───────────┴───────────┬───────────────┐                  │
│  │   Shard 1     │       Shard 2         │    Shard 3    │                  │
│  │ ┌───────────┐ │    ┌───────────┐      │ ┌───────────┐ │                  │
│  │ │  Primary  │ │    │  Primary  │      │ │  Primary  │ │                  │
│  │ └─────┬─────┘ │    └─────┬─────┘      │ └─────┬─────┘ │                  │
│  │   ┌───┴───┐   │      ┌───┴───┐        │   ┌───┴───┐   │                  │
│  │   │  Sec  │   │      │  Sec  │        │   │  Sec  │   │                  │
│  │   └───────┘   │      └───────┘        │   └───────┘   │                  │
│  └───────────────┴───────────────────────┴───────────────┘                  │
│                        Replica Sets                                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### BSON Document Model

```javascript
// MongoDB Document (BSON)
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "name": "John Doe",
  "email": "john@example.com",
  "age": 30,
  "address": {                          // Embedded document
    "street": "123 Main St",
    "city": "New York",
    "zip": "10001"
  },
  "orders": [                           // Array of embedded documents
    { "product": "Laptop", "price": 999 },
    { "product": "Mouse", "price": 25 }
  ],
  "tags": ["premium", "active"],        // Array
  "created_at": ISODate("2024-01-15"),
  "metadata": {
    "last_login": ISODate("2024-12-30"),
    "preferences": { "theme": "dark" }
  }
}
```

#### Индексы в MongoDB

```javascript
// Single field index
db.users.createIndex({ email: 1 });

// Compound index
db.products.createIndex({ category: 1, price: -1 });

// Text index (full-text search)
db.articles.createIndex({ title: "text", body: "text" });

// Geospatial index
db.locations.createIndex({ coordinates: "2dsphere" });

// TTL index (auto-delete after time)
db.sessions.createIndex({ createdAt: 1 }, { expireAfterSeconds: 3600 });

// Unique index
db.users.createIndex({ email: 1 }, { unique: true });

// Partial index (index subset of documents)
db.orders.createIndex(
  { status: 1 },
  { partialFilterExpression: { status: "active" } }
);
```

#### Aggregation Pipeline

```javascript
// Complex analytics query
db.orders.aggregate([
  // Stage 1: Filter
  { $match: { status: "completed", date: { $gte: ISODate("2024-01-01") } } },

  // Stage 2: Unwind array
  { $unwind: "$items" },

  // Stage 3: Group by product
  { $group: {
      _id: "$items.product_id",
      totalQuantity: { $sum: "$items.quantity" },
      totalRevenue: { $sum: { $multiply: ["$items.price", "$items.quantity"] } },
      orderCount: { $sum: 1 }
  }},

  // Stage 4: Lookup (JOIN equivalent)
  { $lookup: {
      from: "products",
      localField: "_id",
      foreignField: "_id",
      as: "product"
  }},

  // Stage 5: Flatten product array
  { $unwind: "$product" },

  // Stage 6: Project final fields
  { $project: {
      productName: "$product.name",
      category: "$product.category",
      totalQuantity: 1,
      totalRevenue: 1,
      avgOrderValue: { $divide: ["$totalRevenue", "$orderCount"] }
  }},

  // Stage 7: Sort by revenue
  { $sort: { totalRevenue: -1 } },

  // Stage 8: Limit top 10
  { $limit: 10 }
]);
```

#### Change Streams (Real-time)

```javascript
// Watch for changes in real-time
const changeStream = db.collection("orders").watch([
  { $match: { "fullDocument.status": "pending" } }
]);

changeStream.on("change", (change) => {
  console.log("Change detected:", change);

  switch (change.operationType) {
    case "insert":
      notifyNewOrder(change.fullDocument);
      break;
    case "update":
      syncOrderStatus(change.documentKey._id, change.updateDescription);
      break;
    case "delete":
      archiveOrder(change.documentKey._id);
      break;
  }
});
```

#### Schema Validation

```javascript
// Enforce schema in MongoDB
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "name", "createdAt"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
          description: "must be a valid email"
        },
        name: {
          bsonType: "string",
          minLength: 2,
          maxLength: 100
        },
        age: {
          bsonType: "int",
          minimum: 0,
          maximum: 150
        },
        status: {
          enum: ["active", "inactive", "pending"],
          description: "must be one of the allowed values"
        },
        createdAt: {
          bsonType: "date"
        }
      }
    }
  },
  validationAction: "error"  // or "warn"
});
```

### CouchDB & PouchDB

#### Offline-First Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Offline-First with CouchDB + PouchDB                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                           Client Side                                │    │
│  │                                                                      │    │
│  │  ┌─────────────────┐      ┌─────────────────┐                       │    │
│  │  │  React/Vue/     │ ←──→ │    PouchDB      │                       │    │
│  │  │  Angular App    │      │  (IndexedDB)    │                       │    │
│  │  └─────────────────┘      └────────┬────────┘                       │    │
│  │                                    │                                 │    │
│  │                         ┌──────────┴──────────┐                     │    │
│  │                         │  Sync Engine        │                     │    │
│  │                         │  (auto-retry,       │                     │    │
│  │                         │   conflict detect)  │                     │    │
│  │                         └──────────┬──────────┘                     │    │
│  └────────────────────────────────────┼────────────────────────────────┘    │
│                                       │                                      │
│                          ┌────────────┴────────────┐                        │
│                          │     Network Layer       │                        │
│                          │  (Online/Offline aware) │                        │
│                          └────────────┬────────────┘                        │
│                                       │                                      │
│  ┌────────────────────────────────────┼────────────────────────────────┐    │
│  │                           Server Side                                │    │
│  │                                    │                                 │    │
│  │                         ┌──────────┴──────────┐                     │    │
│  │                         │      CouchDB        │                     │    │
│  │                         │  (Master database)  │                     │    │
│  │                         └──────────┬──────────┘                     │    │
│  │                                    │                                 │    │
│  │                    ┌───────────────┼───────────────┐                │    │
│  │                    ↓               ↓               ↓                │    │
│  │              ┌─────────┐     ┌─────────┐     ┌─────────┐           │    │
│  │              │ Replica │     │ Replica │     │ Replica │           │    │
│  │              └─────────┘     └─────────┘     └─────────┘           │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### PouchDB Example

```javascript
// Initialize PouchDB (browser)
const localDB = new PouchDB('myapp');
const remoteDB = new PouchDB('https://mycouch.example.com/myapp');

// Create document
await localDB.put({
  _id: 'task_001',
  title: 'Buy groceries',
  completed: false,
  createdAt: new Date().toISOString()
});

// Read document
const doc = await localDB.get('task_001');

// Update document
doc.completed = true;
await localDB.put(doc);

// Sync with remote (two-way)
localDB.sync(remoteDB, {
  live: true,      // Continuous sync
  retry: true      // Retry on connection loss
}).on('change', (change) => {
  console.log('Sync change:', change);
}).on('paused', (info) => {
  console.log('Sync paused (probably offline)');
}).on('active', () => {
  console.log('Sync resumed');
}).on('error', (err) => {
  console.error('Sync error:', err);
});

// Conflict resolution
localDB.get('task_001', { conflicts: true }).then((doc) => {
  if (doc._conflicts) {
    // Handle conflicts
    doc._conflicts.forEach(async (conflictRev) => {
      const conflictDoc = await localDB.get('task_001', { rev: conflictRev });
      // Merge logic here
      // Delete losing revision
      await localDB.remove('task_001', conflictRev);
    });
  }
});
```

### Firebase Firestore

#### Real-time Sync

```javascript
import { initializeApp } from 'firebase/app';
import {
  getFirestore,
  collection,
  doc,
  onSnapshot,
  query,
  where,
  orderBy,
  limit
} from 'firebase/firestore';

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

// Real-time listener on collection
const q = query(
  collection(db, 'messages'),
  where('roomId', '==', 'general'),
  orderBy('timestamp', 'desc'),
  limit(50)
);

const unsubscribe = onSnapshot(q, (snapshot) => {
  snapshot.docChanges().forEach((change) => {
    if (change.type === 'added') {
      console.log('New message:', change.doc.data());
    }
    if (change.type === 'modified') {
      console.log('Modified message:', change.doc.data());
    }
    if (change.type === 'removed') {
      console.log('Removed message:', change.doc.data());
    }
  });
}, (error) => {
  console.error('Listener error:', error);
});

// Offline persistence (enabled by default on mobile)
import { enableIndexedDbPersistence } from 'firebase/firestore';
enableIndexedDbPersistence(db).catch((err) => {
  if (err.code === 'failed-precondition') {
    // Multiple tabs open
  } else if (err.code === 'unimplemented') {
    // Browser doesn't support
  }
});
```

---

## Key-Value Stores

### Redis Deep Dive

#### Архитектура

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Redis Architecture                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         In-Memory Storage                            │    │
│  │                                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │   Strings   │  │    Lists    │  │    Sets     │  │   Hashes   │ │    │
│  │  │  key:value  │  │  [a,b,c,d]  │  │  {a,b,c}    │  │ {f1:v1,..} │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  │                                                                      │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │    │
│  │  │ Sorted Sets │  │   Streams   │  │  Bitmaps    │  │ HyperLog   │ │    │
│  │  │ {a:1,b:2}   │  │ time-events │  │  bits[...]  │  │  Log       │ │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Persistence Layer                            │    │
│  │  ┌────────────────────────┐  ┌────────────────────────────────┐     │    │
│  │  │ RDB Snapshots          │  │ AOF (Append Only File)         │     │    │
│  │  │ Point-in-time backups  │  │ Log of all write operations    │     │    │
│  │  │ Compact, fast restore  │  │ More durable, larger files     │     │    │
│  │  └────────────────────────┘  └────────────────────────────────┘     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Replication                                  │    │
│  │                                                                      │    │
│  │        ┌─────────┐                                                  │    │
│  │        │ Primary │ ────────────────────────────────                 │    │
│  │        └────┬────┘           │               │                      │    │
│  │             │                │               │                      │    │
│  │        ┌────┴────┐     ┌─────┴─────┐   ┌─────┴─────┐               │    │
│  │        │ Replica │     │  Replica  │   │  Replica  │               │    │
│  │        └─────────┘     └───────────┘   └───────────┘               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Data Structures

```bash
# STRINGS - Basic key-value
SET user:1:name "John Doe"
GET user:1:name                  # "John Doe"
INCR page:views                  # Atomic increment
SETEX session:abc 3600 "data"    # Set with TTL (1 hour)
SETNX lock:order:123 "locked"    # Set if not exists (for locking)

# HASHES - Object-like storage
HSET user:1 name "John" age 30 city "NYC"
HGET user:1 name                 # "John"
HGETALL user:1                   # {name: "John", age: "30", city: "NYC"}
HINCRBY user:1 age 1             # Increment field

# LISTS - Ordered collections (queue/stack)
LPUSH notifications:user:1 "msg1" "msg2"  # Push left
RPOP notifications:user:1                  # Pop right (queue behavior)
LRANGE notifications:user:1 0 9            # Get first 10
BRPOP queue:orders 30                      # Blocking pop with timeout

# SETS - Unique unordered collections
SADD product:1:tags "electronics" "sale" "featured"
SISMEMBER product:1:tags "sale"            # Check membership
SINTER product:1:tags product:2:tags       # Intersection
SUNION product:1:tags product:2:tags       # Union

# SORTED SETS - Scored ordered collections
ZADD leaderboard 100 "player:1" 95 "player:2" 150 "player:3"
ZRANGE leaderboard 0 9 REV WITHSCORES      # Top 10
ZINCRBY leaderboard 10 "player:1"          # Increment score
ZRANK leaderboard "player:1"               # Get rank

# STREAMS - Append-only log (like Kafka topics)
XADD events:orders * product "laptop" qty 1 user "john"
XREAD COUNT 10 STREAMS events:orders 0     # Read from beginning
XREAD BLOCK 5000 STREAMS events:orders $   # Wait for new events
```

#### Common Patterns

```python
import redis
import json
from datetime import timedelta

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

# ============================================
# PATTERN 1: CACHING
# ============================================
def get_user_cached(user_id: int):
    cache_key = f"cache:user:{user_id}"

    # Try cache first
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Miss - fetch from DB
    user = db.fetch_user(user_id)

    # Store in cache with TTL
    r.setex(cache_key, timedelta(hours=1), json.dumps(user))

    return user

# Cache invalidation
def update_user(user_id: int, data: dict):
    db.update_user(user_id, data)
    r.delete(f"cache:user:{user_id}")  # Invalidate cache


# ============================================
# PATTERN 2: SESSION STORAGE
# ============================================
def create_session(user_id: int, session_data: dict):
    session_id = generate_uuid()
    session_key = f"session:{session_id}"

    r.hset(session_key, mapping={
        "user_id": user_id,
        "created_at": datetime.now().isoformat(),
        **session_data
    })
    r.expire(session_key, timedelta(days=7))

    return session_id

def get_session(session_id: str):
    session_key = f"session:{session_id}"
    session = r.hgetall(session_key)

    if session:
        # Extend TTL on access
        r.expire(session_key, timedelta(days=7))

    return session if session else None


# ============================================
# PATTERN 3: RATE LIMITING
# ============================================
def is_rate_limited(user_id: int, limit: int = 100, window: int = 60):
    """Sliding window rate limiter"""
    key = f"ratelimit:{user_id}"
    now = time.time()

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window)  # Remove old entries
    pipe.zadd(key, {str(now): now})               # Add current request
    pipe.zcard(key)                               # Count requests
    pipe.expire(key, window)                      # Set TTL
    results = pipe.execute()

    request_count = results[2]
    return request_count > limit


# ============================================
# PATTERN 4: DISTRIBUTED LOCK
# ============================================
def acquire_lock(resource_id: str, timeout: int = 10):
    lock_key = f"lock:{resource_id}"
    lock_value = str(uuid.uuid4())

    acquired = r.set(lock_key, lock_value, nx=True, ex=timeout)
    return lock_value if acquired else None

def release_lock(resource_id: str, lock_value: str):
    lock_key = f"lock:{resource_id}"

    # Lua script for atomic check-and-delete
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    return r.eval(script, 1, lock_key, lock_value)


# ============================================
# PATTERN 5: PUB/SUB
# ============================================
def publish_event(channel: str, event: dict):
    r.publish(channel, json.dumps(event))

def subscribe_to_events(channel: str):
    pubsub = r.pubsub()
    pubsub.subscribe(channel)

    for message in pubsub.listen():
        if message['type'] == 'message':
            event = json.loads(message['data'])
            process_event(event)


# ============================================
# PATTERN 6: LEADERBOARD
# ============================================
def update_score(user_id: str, score: int):
    r.zadd("leaderboard", {user_id: score})

def get_top_players(count: int = 10):
    return r.zrevrange("leaderboard", 0, count - 1, withscores=True)

def get_user_rank(user_id: str):
    rank = r.zrevrank("leaderboard", user_id)
    score = r.zscore("leaderboard", user_id)
    return {"rank": rank + 1 if rank else None, "score": score}
```

### Redis vs Memcached

| Feature | Redis | Memcached |
|---------|-------|-----------|
| **Data types** | Strings, Lists, Sets, Hashes, Sorted Sets, Streams | Strings only |
| **Persistence** | RDB + AOF | None |
| **Replication** | Primary-Replica | None |
| **Pub/Sub** | Yes | No |
| **Transactions** | Yes (MULTI/EXEC) | No |
| **Lua scripting** | Yes | No |
| **Threading** | Single-threaded (mostly) | Multi-threaded |
| **Memory efficiency** | Good | Slightly better |
| **Max key size** | 512 MB | 250 bytes |
| **Max value size** | 512 MB | 1 MB |
| **Cluster support** | Yes (Redis Cluster) | Yes (client-side) |
| **License (2025)** | AGPL v3 (Redis 8+) | BSD |

**Recommendation:** Use Redis for most cases. Memcached only for extreme simplicity or when Redis license is a concern.

---

## Wide-Column Stores

### Apache Cassandra

#### Архитектура

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Cassandra Ring Architecture                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                              Token Ring                                      │
│                                                                              │
│                          ┌───────────────┐                                  │
│                    ┌─────│   Node A      │─────┐                            │
│                    │     │ Token: 0-25   │     │                            │
│                    │     └───────────────┘     │                            │
│          ┌─────────┴───┐                 ┌─────┴─────────┐                  │
│          │   Node F    │                 │    Node B     │                  │
│          │ Token: 75-0 │                 │ Token: 25-50  │                  │
│          └─────────┬───┘                 └─────┬─────────┘                  │
│                    │                           │                            │
│          ┌─────────┴───┐                 ┌─────┴─────────┐                  │
│          │   Node E    │                 │    Node C     │                  │
│          │ Token: 62-75│                 │ Token: 37-50  │                  │
│          └─────────────┘                 └───────────────┘                  │
│                    │     ┌───────────────┐     │                            │
│                    └─────│    Node D     │─────┘                            │
│                          │ Token: 50-62  │                                  │
│                          └───────────────┘                                  │
│                                                                              │
│  Key Features:                                                               │
│  • No master node - all nodes equal                                         │
│  • Consistent hashing distributes data                                      │
│  • Replication factor determines copies                                     │
│  • Any node can handle any request                                          │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Data Model

```sql
-- Keyspace (like database)
CREATE KEYSPACE ecommerce
WITH replication = {
  'class': 'NetworkTopologyStrategy',
  'dc1': 3,      -- 3 replicas in datacenter 1
  'dc2': 2       -- 2 replicas in datacenter 2
};

USE ecommerce;

-- Table with partition key and clustering columns
CREATE TABLE orders (
    user_id UUID,              -- Partition key
    order_date TIMESTAMP,      -- Clustering column
    order_id UUID,             -- Clustering column
    items LIST<FROZEN<item>>,  -- Collection type
    total DECIMAL,
    status TEXT,
    PRIMARY KEY ((user_id), order_date, order_id)
) WITH CLUSTERING ORDER BY (order_date DESC, order_id ASC);

-- User-Defined Type
CREATE TYPE item (
    product_id UUID,
    name TEXT,
    quantity INT,
    price DECIMAL
);

-- Efficient queries (follow partition key)
SELECT * FROM orders WHERE user_id = ?;  -- Fast: uses partition key
SELECT * FROM orders WHERE user_id = ? AND order_date >= ?;  -- Fast: uses clustering

-- Inefficient query (requires ALLOW FILTERING)
SELECT * FROM orders WHERE status = 'pending';  -- Slow: full table scan
```

#### Consistency Levels

```sql
-- Write consistency
CONSISTENCY QUORUM;  -- Majority of replicas must acknowledge
INSERT INTO orders (user_id, order_date, order_id, total)
VALUES (uuid(), toTimestamp(now()), uuid(), 99.99);

-- Consistency levels:
-- ANY        - Write to any node (fast, lowest durability)
-- ONE        - Write to at least 1 replica
-- TWO        - Write to at least 2 replicas
-- THREE      - Write to at least 3 replicas
-- QUORUM     - Write to majority ((RF/2) + 1)
-- LOCAL_QUORUM - Quorum in local datacenter
-- EACH_QUORUM  - Quorum in each datacenter
-- ALL        - Write to all replicas (slowest, highest durability)
```

### ScyllaDB

**ScyllaDB** — Cassandra-compatible, написана на C++:

| Metric | Cassandra | ScyllaDB |
|--------|-----------|----------|
| Throughput | Baseline | 10x higher |
| Latency p99 | 40-125ms | 5-15ms |
| Nodes needed | 40 | 4 |
| Cost | Baseline | 75% lower |
| Language | Java (GC pauses) | C++ (no GC) |

### Amazon DynamoDB

#### Single Table Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DynamoDB Single Table Design                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Instead of:                           Use:                                  │
│  ┌─────────────┐  ┌─────────────┐      ┌────────────────────────────────┐   │
│  │   Users     │  │   Orders    │      │       Single Table             │   │
│  ├─────────────┤  ├─────────────┤      ├────────────────────────────────┤   │
│  │ user_id     │  │ order_id    │      │ PK            │ SK             │   │
│  │ name        │  │ user_id     │  →   ├───────────────┼────────────────┤   │
│  │ email       │  │ date        │      │ USER#123      │ PROFILE        │   │
│  └─────────────┘  │ total       │      │ USER#123      │ ORDER#001      │   │
│                   └─────────────┘      │ USER#123      │ ORDER#002      │   │
│  ┌─────────────┐                       │ USER#456      │ PROFILE        │   │
│  │  Products   │                       │ PRODUCT#AAA   │ DETAILS        │   │
│  ├─────────────┤                       │ PRODUCT#AAA   │ REVIEW#001     │   │
│  │ product_id  │                       └───────────────┴────────────────┘   │
│  │ name        │                                                            │
│  └─────────────┘                                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Access Patterns with GSIs

```python
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('MyApp')

# Primary table access patterns

# 1. Get user profile
response = table.query(
    KeyConditionExpression=Key('PK').eq('USER#123') & Key('SK').eq('PROFILE')
)

# 2. Get all orders for user
response = table.query(
    KeyConditionExpression=Key('PK').eq('USER#123') & Key('SK').begins_with('ORDER#')
)

# GSI access patterns

# GSI1: Inverted index (SK as partition key)
# Use case: Get all users who reviewed a product
response = table.query(
    IndexName='GSI1',
    KeyConditionExpression=Key('GSI1PK').eq('PRODUCT#AAA') & Key('GSI1SK').begins_with('REVIEW#')
)

# GSI2: By status and date
# Use case: Get all pending orders
response = table.query(
    IndexName='GSI2',
    KeyConditionExpression=Key('GSI2PK').eq('ORDER#PENDING') & Key('GSI2SK').between('2024-01-01', '2024-12-31')
)

# Transactions (ACID)
response = dynamodb.meta.client.transact_write_items(
    TransactItems=[
        {
            'Put': {
                'TableName': 'MyApp',
                'Item': {'PK': {'S': 'ORDER#789'}, 'SK': {'S': 'DETAILS'}, ...}
            }
        },
        {
            'Update': {
                'TableName': 'MyApp',
                'Key': {'PK': {'S': 'PRODUCT#AAA'}, 'SK': {'S': 'DETAILS'}},
                'UpdateExpression': 'SET stock = stock - :qty',
                'ConditionExpression': 'stock >= :qty',
                'ExpressionAttributeValues': {':qty': {'N': '1'}}
            }
        }
    ]
)
```

---

## Graph Databases

### Neo4j Deep Dive

#### Property Graph Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Neo4j Property Graph Model                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│     ┌──────────────────┐                    ┌──────────────────┐            │
│     │    Node          │                    │    Node          │            │
│     │  (:Person)       │                    │  (:Movie)        │            │
│     ├──────────────────┤                    ├──────────────────┤            │
│     │ name: "Tom"      │ ─── :ACTED_IN ──→  │ title: "Forrest" │            │
│     │ born: 1956       │     role: "Forrest"│ released: 1994   │            │
│     └──────────────────┘                    └──────────────────┘            │
│            │                                         ↑                       │
│            │                                         │                       │
│        :KNOWS                                    :DIRECTED                   │
│            │                                         │                       │
│            ↓                                         │                       │
│     ┌──────────────────┐                    ┌──────────────────┐            │
│     │    Node          │                    │    Node          │            │
│     │  (:Person)       │                    │  (:Person)       │            │
│     ├──────────────────┤                    ├──────────────────┤            │
│     │ name: "Robin"    │                    │ name: "Robert"   │            │
│     │ born: 1964       │                    │ born: 1952       │            │
│     └──────────────────┘                    └──────────────────┘            │
│                                                                              │
│  Components:                                                                 │
│  • Nodes: Entities (labeled with types like :Person, :Movie)                │
│  • Relationships: Connections (typed like :ACTED_IN, :KNOWS)                │
│  • Properties: Key-value attributes on nodes and relationships             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Cypher Query Language

```cypher
-- CREATE nodes and relationships
CREATE (tom:Person {name: 'Tom Hanks', born: 1956})
CREATE (forrest:Movie {title: 'Forrest Gump', released: 1994})
CREATE (tom)-[:ACTED_IN {role: 'Forrest'}]->(forrest);

-- MATCH and RETURN
MATCH (p:Person {name: 'Tom Hanks'})-[:ACTED_IN]->(m:Movie)
RETURN m.title, m.released
ORDER BY m.released DESC;

-- Find friends of friends (2 hops)
MATCH (me:Person {name: 'Alice'})-[:FRIEND]->()-[:FRIEND]->(fof)
WHERE fof <> me AND NOT (me)-[:FRIEND]->(fof)
RETURN DISTINCT fof.name AS RecommendedFriend;

-- Shortest path
MATCH path = shortestPath(
  (kevin:Person {name: 'Kevin Bacon'})-[:ACTED_IN*]-(other:Person)
)
WHERE other.name = 'Tom Hanks'
RETURN path, length(path) AS degrees;

-- Variable length relationships
MATCH (a:Person)-[:MANAGES*1..5]->(b:Person)
WHERE a.name = 'CEO'
RETURN b.name, length(path) AS level;

-- Aggregation
MATCH (m:Movie)<-[:ACTED_IN]-(a:Person)
RETURN m.title,
       count(a) AS actorCount,
       collect(a.name) AS actors
ORDER BY actorCount DESC
LIMIT 10;

-- Recommendations based on common connections
MATCH (me:Person {name: 'Alice'})-[:LIKES]->(item:Product)<-[:LIKES]-(other:Person)
MATCH (other)-[:LIKES]->(rec:Product)
WHERE NOT (me)-[:LIKES]->(rec)
RETURN rec.name, count(*) AS score
ORDER BY score DESC
LIMIT 5;

-- Pattern detection (fraud detection example)
MATCH (a:Account)-[:TRANSFER]->(b:Account)-[:TRANSFER]->(c:Account)
WHERE a = c  -- Money comes back to source
AND NOT a = b
RETURN a, b, c;
```

#### Use Cases

| Use Case | Why Graph? |
|----------|------------|
| Social Networks | Friend connections, degrees of separation |
| Recommendations | Collaborative filtering, "users who liked X also liked Y" |
| Fraud Detection | Pattern matching, circular transactions |
| Knowledge Graphs | Entity relationships, semantic search |
| Network/IT | Dependencies, impact analysis |
| Supply Chain | Routing, bottleneck detection |

---

## Time-Series Databases

### InfluxDB vs TimescaleDB

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Time-Series Database Comparison                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  InfluxDB                              TimescaleDB                           │
│  ─────────                             ───────────                           │
│  Purpose-built from scratch            PostgreSQL extension                  │
│                                                                              │
│  ┌─────────────────────────┐           ┌─────────────────────────┐          │
│  │   Line Protocol         │           │   Standard SQL          │          │
│  │   cpu,host=A value=0.64 │           │   INSERT INTO metrics   │          │
│  │   1465839830100400200   │           │   (time, cpu, host)     │          │
│  └─────────────────────────┘           │   VALUES (NOW(), 0.64,  │          │
│                                        │   'A');                  │          │
│  Query: InfluxQL or SQL                └─────────────────────────┘          │
│                                                                              │
│  ┌─────────────────────────┐           ┌─────────────────────────┐          │
│  │ SELECT mean("value")    │           │ SELECT time_bucket('1h',│          │
│  │ FROM "cpu"              │           │   time) AS hour,        │          │
│  │ WHERE time > now() - 1h │           │   avg(cpu) AS avg_cpu   │          │
│  │ GROUP BY time(10m)      │           │ FROM metrics            │          │
│  └─────────────────────────┘           │ WHERE time > NOW() - '1h│          │
│                                        │ GROUP BY hour;          │          │
│                                        └─────────────────────────┘          │
│                                                                              │
│  Best for:                             Best for:                             │
│  • Simple metrics                      • Complex SQL queries                 │
│  • Low cardinality                     • High cardinality                    │
│  • Monitoring/IoT                      • Analytics + time-series            │
│  • Fast ingestion                      • PostgreSQL ecosystem               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Search Engines

### Elasticsearch

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Elasticsearch Architecture                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                        Cluster                                        │   │
│  │                                                                       │   │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐       │   │
│  │  │     Node 1      │  │     Node 2      │  │     Node 3      │       │   │
│  │  │ ┌─────┬───────┐ │  │ ┌─────┬───────┐ │  │ ┌─────┬───────┐ │       │   │
│  │  │ │Shard│Replica│ │  │ │Shard│Replica│ │  │ │Shard│Replica│ │       │   │
│  │  │ │  0  │  1    │ │  │ │  1  │  2    │ │  │ │  2  │  0    │ │       │   │
│  │  │ └─────┴───────┘ │  │ └─────┴───────┘ │  │ └─────┴───────┘ │       │   │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘       │   │
│  │                                                                       │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  Index → Documents → Fields                                                  │
│                                                                              │
│  products (index)                                                            │
│  ├── doc 1: {name: "iPhone 15", price: 999, category: "phones"}            │
│  ├── doc 2: {name: "MacBook Pro", price: 2499, category: "laptops"}        │
│  └── doc 3: {name: "iPad Pro", price: 1099, category: "tablets"}           │
│                                                                              │
│  Inverted Index:                                                             │
│  ┌─────────────┬─────────────────────┐                                      │
│  │ Term        │ Document IDs        │                                      │
│  ├─────────────┼─────────────────────┤                                      │
│  │ "iphone"    │ [1]                 │                                      │
│  │ "macbook"   │ [2]                 │                                      │
│  │ "pro"       │ [2, 3]              │                                      │
│  │ "ipad"      │ [3]                 │                                      │
│  └─────────────┴─────────────────────┘                                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Search Queries

```json
// Full-text search
GET /products/_search
{
  "query": {
    "match": {
      "description": "wireless bluetooth headphones"
    }
  }
}

// Boolean query
GET /products/_search
{
  "query": {
    "bool": {
      "must": [
        { "match": { "category": "electronics" } }
      ],
      "filter": [
        { "range": { "price": { "gte": 100, "lte": 500 } } },
        { "term": { "in_stock": true } }
      ],
      "should": [
        { "match": { "brand": "Apple" } }
      ],
      "must_not": [
        { "term": { "discontinued": true } }
      ]
    }
  }
}

// Aggregations
GET /orders/_search
{
  "size": 0,
  "aggs": {
    "sales_by_category": {
      "terms": { "field": "category.keyword" },
      "aggs": {
        "total_revenue": {
          "sum": { "field": "total" }
        },
        "avg_order_value": {
          "avg": { "field": "total" }
        }
      }
    }
  }
}

// Autocomplete/Suggest
GET /products/_search
{
  "suggest": {
    "product-suggest": {
      "prefix": "iph",
      "completion": {
        "field": "suggest",
        "fuzzy": {
          "fuzziness": 2
        }
      }
    }
  }
}
```

---

## Scaling Strategies

### Sharding

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Sharding Strategies                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. RANGE-BASED SHARDING                                                    │
│     ─────────────────────                                                   │
│     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│     │   Shard 1   │  │   Shard 2   │  │   Shard 3   │                      │
│     │   A - H     │  │   I - P     │  │   Q - Z     │                      │
│     └─────────────┘  └─────────────┘  └─────────────┘                      │
│     Pros: Range queries efficient                                           │
│     Cons: Can create hot spots                                              │
│                                                                              │
│  2. HASH-BASED SHARDING                                                     │
│     ─────────────────────                                                   │
│     hash(user_id) % 3 → shard_number                                        │
│     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│     │   Shard 0   │  │   Shard 1   │  │   Shard 2   │                      │
│     │  hash % 3=0 │  │  hash % 3=1 │  │  hash % 3=2 │                      │
│     └─────────────┘  └─────────────┘  └─────────────┘                      │
│     Pros: Even distribution                                                 │
│     Cons: Range queries need all shards                                     │
│                                                                              │
│  3. CONSISTENT HASHING (Cassandra, DynamoDB)                                │
│     ─────────────────────────────────────────                               │
│           ┌───────────────┐                                                 │
│      ┌────│   Node A      │────┐                                            │
│      │    │ Token: 0-25   │    │                                            │
│      │    └───────────────┘    │                                            │
│ ┌────┴───┐                ┌────┴───┐                                        │
│ │ Node D │                │ Node B │                                        │
│ │ 75-100 │                │ 25-50  │                                        │
│ └────┬───┘                └────┬───┘                                        │
│      │    ┌───────────────┐    │                                            │
│      └────│    Node C     │────┘                                            │
│           │ Token: 50-75  │                                                 │
│           └───────────────┘                                                 │
│     Pros: Adding/removing nodes moves minimal data                          │
│     Cons: More complex to understand                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Replication

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Replication Strategies                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. MASTER-SLAVE (Primary-Replica)                                          │
│     ─────────────────────────────                                           │
│                    Writes                                                    │
│                      ↓                                                       │
│              ┌─────────────┐                                                │
│              │   Primary   │                                                │
│              │   (Master)  │                                                │
│              └──────┬──────┘                                                │
│           ┌─────────┼─────────┐                                             │
│           ↓         ↓         ↓                                             │
│     ┌──────────┐ ┌──────────┐ ┌──────────┐                                 │
│     │ Replica  │ │ Replica  │ │ Replica  │  ← Reads                        │
│     └──────────┘ └──────────┘ └──────────┘                                 │
│                                                                              │
│  2. MASTER-MASTER (Multi-Primary)                                           │
│     ───────────────────────────                                             │
│     ┌──────────┐     ┌──────────┐                                          │
│     │ Primary  │ ←→  │ Primary  │                                          │
│     │    A     │     │    B     │                                          │
│     └──────────┘     └──────────┘                                          │
│          ↑               ↑                                                  │
│       Writes          Writes                                                │
│     Pros: High write availability                                           │
│     Cons: Conflict resolution required                                      │
│                                                                              │
│  3. QUORUM-BASED (Cassandra, DynamoDB)                                      │
│     ──────────────────────────────────                                      │
│     Write Quorum: (N/2) + 1 nodes must acknowledge                          │
│     Read Quorum: (N/2) + 1 nodes must respond                               │
│                                                                              │
│     For N=3 replicas:                                                       │
│     • Write to 2 nodes → success                                            │
│     • Read from 2 nodes → get latest                                        │
│                                                                              │
│     W + R > N ensures strong consistency                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Design Patterns & Anti-Patterns

### Patterns

#### 1. Denormalization

```javascript
// SQL (normalized)
// users table: id, name, email
// orders table: id, user_id, total, status

// NoSQL (denormalized)
{
  "_id": "order:123",
  "user": {
    "id": "user:456",
    "name": "John Doe",      // Duplicated from users
    "email": "john@test.com" // Duplicated from users
  },
  "total": 99.99,
  "status": "pending"
}
// Pros: No joins, faster reads
// Cons: Data duplication, update complexity
```

#### 2. Embedding vs Referencing (MongoDB)

```javascript
// EMBEDDING - One-to-few, data accessed together
{
  "_id": "post:1",
  "title": "My Post",
  "comments": [           // Embedded
    { "user": "alice", "text": "Great!" },
    { "user": "bob", "text": "Nice post" }
  ]
}

// REFERENCING - One-to-many, independent access
{
  "_id": "user:1",
  "name": "John",
  "order_ids": ["order:1", "order:2", "order:3"]  // References
}

// When to embed:
// • Data always accessed together
// • Child data doesn't grow unbounded
// • Strong ownership (delete parent = delete children)

// When to reference:
// • Data accessed independently
// • Many-to-many relationships
// • Unbounded growth possible
```

#### 3. Composite Keys (DynamoDB)

```javascript
// Access patterns determine key design
// Pattern: Get user's orders by date range

{
  PK: "USER#123",
  SK: "ORDER#2024-01-15#abc",  // Composite: type + date + id
  // ... other attributes
}

// Query: Get orders for January 2024
table.query({
  KeyConditionExpression: "PK = :pk AND SK BETWEEN :start AND :end",
  ExpressionAttributeValues: {
    ":pk": "USER#123",
    ":start": "ORDER#2024-01-01",
    ":end": "ORDER#2024-01-31"
  }
});
```

### Anti-Patterns

#### 1. Hot Spots

```
BAD: Using sequential IDs or timestamps as partition key
┌─────────┐  ┌─────────┐  ┌─────────┐
│ Shard 1 │  │ Shard 2 │  │ Shard 3 │
│ 100%    │  │  0%     │  │  0%     │  ← All writes to one shard!
└─────────┘  └─────────┘  └─────────┘

GOOD: Use high-cardinality keys
// Instead of: partition_key = date
// Use: partition_key = user_id or hash(user_id + date)
```

#### 2. Unbounded Arrays

```javascript
// BAD: Array that grows forever
{
  "_id": "user:1",
  "followers": ["user:2", "user:3", ... "user:1000000"]  // Too big!
}

// GOOD: Separate collection with pagination
// followers collection
{ "_id": "follow:1", "user": "user:1", "follower": "user:2" }
{ "_id": "follow:2", "user": "user:1", "follower": "user:3" }
```

#### 3. Over-Fetching

```javascript
// BAD: Fetching entire document for one field
const user = await db.users.findOne({ _id: userId });
const name = user.name;

// GOOD: Project only needed fields
const user = await db.users.findOne(
  { _id: userId },
  { projection: { name: 1 } }
);
```

---

## When to Use NoSQL vs SQL

### Use SQL When:

| Scenario | Why SQL |
|----------|---------|
| Complex transactions | ACID guarantees |
| Complex joins | Relational model excels |
| Ad-hoc queries | SQL is flexible |
| Strong consistency | Data integrity critical |
| Structured data | Fixed schema is advantage |
| Reporting/Analytics | SQL aggregations powerful |
| Existing SQL expertise | Team productivity |

### Use NoSQL When:

| Scenario | Which NoSQL |
|----------|-------------|
| Flexible schema | MongoDB, CouchDB |
| Caching | Redis |
| Write-heavy | Cassandra, ScyllaDB |
| Graph relationships | Neo4j |
| Real-time sync | Firebase, CouchDB |
| Search | Elasticsearch |
| Time-series | InfluxDB, TimescaleDB |
| Serverless | DynamoDB |

### Decision Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       NoSQL vs SQL Decision Tree                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Start: What is your primary need?                                          │
│                    │                                                         │
│      ┌─────────────┼─────────────┐                                          │
│      ↓             ↓             ↓                                          │
│  Transactions  Flexibility   Performance                                    │
│      │             │             │                                          │
│      ↓             ↓             ↓                                          │
│   ┌─────┐     ┌─────┐       ┌─────┐                                        │
│   │ SQL │     │NoSQL│       │Both?│                                        │
│   └──┬──┘     └──┬──┘       └──┬──┘                                        │
│      │           │             │                                            │
│      ↓           ↓             ↓                                            │
│ PostgreSQL   ┌───┴───┐    What type?                                        │
│              │       │         │                                            │
│           Schema  Real-time ┌──┴──┐                                        │
│           flex?   sync?     │     │                                        │
│              │       │    Reads Writes                                      │
│              ↓       ↓       │     │                                        │
│          MongoDB Firebase    ↓     ↓                                        │
│                           Redis Cassandra                                   │
│                                                                              │
│  Pro tip: When in doubt, start with PostgreSQL.                            │
│  It handles JSON well and is battle-tested.                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Decision Guide

### Quick Reference

| Need | Recommended | Alternative |
|------|-------------|-------------|
| Document store | MongoDB | CouchDB |
| Caching | Redis | Memcached |
| Write-heavy | Cassandra | ScyllaDB |
| AWS serverless | DynamoDB | - |
| Graph queries | Neo4j | Amazon Neptune |
| Time-series | TimescaleDB | InfluxDB |
| Full-text search | Elasticsearch | Algolia |
| Offline-first | CouchDB + PouchDB | Firebase |
| Real-time mobile | Firebase Firestore | Supabase |

### By Industry

| Industry | Primary DB | Why |
|----------|------------|-----|
| E-commerce | MongoDB + Redis | Flexible catalog + fast caching |
| Social Media | Neo4j + Cassandra | Relationships + high writes |
| IoT | InfluxDB/TimescaleDB | Time-series data |
| Gaming | Redis + DynamoDB | Leaderboards + serverless |
| Banking | PostgreSQL | ACID transactions |
| Log Analytics | Elasticsearch | Full-text search |
| Mobile Apps | Firebase/CouchDB | Real-time sync, offline |

### By Scale

| Stage | Recommendation |
|-------|----------------|
| MVP/Prototype | SQLite or Firebase |
| Early Startup | PostgreSQL or MongoDB Atlas |
| Growth | PostgreSQL + Redis cache |
| Scale | Sharded MongoDB or Cassandra |
| Enterprise | Multi-database (polyglot persistence) |

---

## Summary

### Key Takeaways

1. **NoSQL is not a replacement for SQL** — it's a complement for specific use cases
2. **Choose based on data model fit**, not hype
3. **Modern NoSQL supports ACID** when needed (MongoDB, DynamoDB)
4. **Start simple** — PostgreSQL + Redis covers most needs
5. **Polyglot persistence** is the future — use the right tool for each job

### The Golden Rules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         NoSQL Golden Rules                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. Design for your queries, not your data                                  │
│     Know access patterns BEFORE choosing a database                         │
│                                                                              │
│  2. Denormalization is OK — embrace it                                      │
│     Storage is cheap, joins are expensive                                   │
│                                                                              │
│  3. Choose the right tool for the job                                       │
│     Graph data → Neo4j, not MongoDB                                         │
│     Time-series → InfluxDB, not Redis                                       │
│                                                                              │
│  4. Plan for scale, but don't over-engineer                                 │
│     Start with single node, shard when needed                               │
│                                                                              │
│  5. Understand CAP tradeoffs                                                │
│     You can't have all three: Consistency, Availability, Partition Tolerance│
│                                                                              │
│  6. Always have a caching strategy                                          │
│     Database → Redis → Application is standard pattern                      │
│                                                                              │
│  7. Test at scale before production                                         │
│     Benchmarks matter — measure, don't guess                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Further Reading

- [MongoDB University](https://university.mongodb.com/) — Free MongoDB courses
- [Redis University](https://university.redis.com/) — Free Redis courses
- [DataStax Academy](https://www.datastax.com/dev/academy) — Cassandra training
- [Neo4j GraphAcademy](https://graphacademy.neo4j.com/) — Graph database courses
- [DynamoDB Book](https://www.dynamodbbook.com/) — Alex DeBrie's guide
- [Designing Data-Intensive Applications](https://dataintensive.net/) — Martin Kleppmann

## Связь с другими темами

[[sql-databases-complete]] — SQL-базы данных (PostgreSQL, MySQL, SQLite) представляют противоположный подход к хранению данных: строгая схема, ACID-транзакции, мощные JOIN. Сравнение SQL и NoSQL помогает осознанно выбирать инструмент под задачу: транзакционные системы — SQL, гибкая схема и горизонтальное масштабирование — NoSQL, часто оба вместе (Polyglot Persistence). Рекомендуется изучать параллельно.

[[databases-nosql-comparison]] — Материал по сравнению NoSQL-решений даёт общий framework для выбора между Document, Key-Value, Wide-Column и Graph моделями. Текущий документ углубляет каждую категорию практическими примерами (MongoDB, Redis, Cassandra, Neo4j) и production-паттернами. Рекомендуется прочитать comparison для общей картины, затем этот материал для деталей.

[[architecture-distributed-systems]] — NoSQL-базы данных часто являются distributed by design: MongoDB Replica Set, Cassandra ring, DynamoDB partitioning. Понимание распределённых систем (consensus, eventual consistency, vector clocks) помогает правильно настраивать и диагностировать NoSQL-кластеры. Рекомендуется для архитекторов и senior-разработчиков.

[[databases-fundamentals-complete]] — Фундаментальные концепции (ACID vs BASE, CAP-теорема, индексы) являются основой для понимания trade-offs NoSQL. Без знания реляционной модели сложно оценить, от чего именно отказывается каждый тип NoSQL и какие преимущества это даёт. Обязательный пререквизит перед этим материалом.

## Источники и дальнейшее чтение

### Теоретические основы

- Gilbert S., Lynch N. (2002). *Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services.* — Формальное доказательство CAP-теоремы.
- Vogels W. (2009). *Eventually Consistent.* Communications of the ACM. — Формальное определение eventual consistency и таксономия consistency моделей.
- O'Neil P. et al. (1996). *The Log-Structured Merge-Tree (LSM-Tree).* Acta Informatica. — Определение LSM-Tree, используемого в Cassandra, RocksDB, LevelDB.
- Lamport L. (1978). *Time, Clocks, and the Ordering of Events in a Distributed System.* — Logical clocks, на основе которых построены Vector Clocks.
- Shapiro M. et al. (2011). *Conflict-free Replicated Data Types.* — Формальное определение CRDTs для eventual consistency без координации.

### Практические руководства

- Kleppmann M. (2017). *Designing Data-Intensive Applications*. — Лучшая книга для понимания trade-offs между SQL и NoSQL: репликация, партиционирование, consistency модели. Обязательна для осознанного выбора NoSQL-решения.
- Redmond E., Wilson J.R. (2012). *Seven Databases in Seven Weeks*. — Практический обзор PostgreSQL, MongoDB, Redis, CouchDB, Neo4j, HBase, Riak с hands-on примерами. Идеальна для быстрого знакомства с разными моделями данных.
- Petrov A. (2019). *Database Internals*. — Глубокий разбор storage engines (LSM-Tree для Cassandra, B-Tree для MongoDB WiredTiger) и distributed protocols (gossip, anti-entropy), которые лежат в основе NoSQL-систем.

---

---

## Проверь себя

> [!question]- Почему MongoDB добавил поддержку транзакций в v4.0, и означает ли это что MongoDB теперь заменяет PostgreSQL?
> MongoDB добавил multi-document транзакции для случаев, когда атомарность нескольких документов необходима (перевод денег). Но транзакции в MongoDB медленнее, чем в PostgreSQL, и не рекомендуются как основной паттерн — это «защитная сетка», а не основной инструмент. PostgreSQL превосходит при частых JOIN, сложных запросах и строгой консистентности.

> [!question]- В каком сценарии Redis нельзя использовать как основную базу данных?
> Redis хранит данные в памяти (RAM), что означает ограничение объёма и риск потери данных при сбое (даже с AOF/RDB persistence). Нельзя использовать как основную БД для данных, потеря которых критична (финансовые транзакции), при объёмах данных, превышающих RAM, и когда нужны сложные запросы с JOIN. Redis — кэш и вспомогательное хранилище.

> [!question]- Почему Cassandra требует проектирования схемы от запросов, а не от данных?
> Cassandra оптимизирована для записи и чтения по partition key. Данные физически организованы по partition key, и чтение без него — full scan кластера. Поэтому сначала определяются access patterns (какие запросы будут), затем проектируются таблицы с правильными partition key и clustering columns. Денормализация — норма.

> [!question]- Когда Graph DB (Neo4j) действительно лучше реляционной базы?
> Когда основная ценность — в связях между сущностями: социальные графы (друзья друзей), рекомендательные системы, fraud detection, knowledge graphs. В SQL для обхода графа глубиной N нужно N JOIN, что экспоненциально замедляется. Neo4j обходит граф за O(1) на каждый переход через прямые указатели между узлами.

---

## Ключевые карточки

Какие 5 типов NoSQL баз данных существуют?
?
Document (MongoDB, CouchDB), Key-Value (Redis, DynamoDB), Wide-Column (Cassandra, ScyllaDB), Graph (Neo4j, ArangoDB), Time-Series (InfluxDB, TimescaleDB). Каждый оптимизирован под свой паттерн доступа.

Что такое BASE и чем отличается от ACID?
?
BASE: Basically Available (система отвечает), Soft state (состояние может быть временно неконсистентным), Eventually consistent (консистентность восстановится). Это компромисс в пользу доступности, типичный для NoSQL.

Как работает шардинг в MongoDB?
?
MongoDB распределяет данные по шардам на основе shard key. Range sharding — последовательные диапазоны, Hashed sharding — равномерное распределение. mongos-роутер направляет запросы на нужные шарды. Выбор shard key критичен для производительности.

Что такое Consistent Hashing и зачем он нужен?
?
Алгоритм распределения данных по узлам, при котором добавление/удаление узла перемещает минимум данных (~1/N). Используется в Cassandra, DynamoDB. В отличие от простого хэширования, не требует перераспределения всех данных.

Чем Document DB отличается от Key-Value?
?
Key-Value хранит непрозрачные значения по ключу (Redis: GET/SET). Document DB хранит структурированные документы (JSON) и позволяет запрашивать по полям внутри документа (MongoDB: find({age: {$gt: 25}})). Document DB знает содержимое, KV — нет.

Что такое TTL (Time-To-Live) в Redis?
?
Механизм автоматического удаления ключа через заданное время. SETEX key 3600 value — ключ удалится через час. Используется для кэша, сессий, rate limiting. Освобождает память без ручной очистки.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[databases-replication-sharding]] | Масштабирование и репликация в NoSQL-системах |
| Углубиться | [[database-internals-complete]] | LSM-Tree, storage engines под капотом Cassandra и MongoDB |
| Смежная тема | [[architecture-distributed-systems]] | CAP-теорема, consensus-протоколы, eventual consistency |
| Смежная тема | [[caching-strategies]] | Redis как кэш, паттерны Cache-Aside, Write-Through |
| Обзор | [[databases-overview]] | Вернуться к карте раздела |

---

*Last updated: 2025-12-30*
