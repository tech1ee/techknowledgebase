---
title: "Databases MOC"
created: 2025-11-24
modified: 2025-12-18
type: moc
tags:
  - topic/databases
  - type/moc
  - navigation
---

# Databases MOC

> Проектирование, оптимизация, SQL/NoSQL — выбор правильной БД для задачи

---

## Быстрая навигация

- **Новичок?** → Начни с [[database-design-optimization]] — базовые концепции
- **Выбираешь SQL vs NoSQL?** → Раздел "Как выбрать тип БД" ниже
- **Оптимизируешь запросы?** → Раздел "Оптимизация" — индексы, EXPLAIN, N+1
- **Проектируешь архитектуру?** → Раздел "Polyglot Persistence"

---

## Рекомендуемый путь изучения

```
1. [[databases-overview]]               — Обзор раздела
         ↓
2. [[databases-fundamentals-complete]]  — Основы: модели данных, ACID, CAP
         ↓
3. [[databases-sql-fundamentals]]       — SQL: DDL, DML, JOIN, подзапросы
         ↓
4. [[databases-transactions-acid]]      — Транзакции, изоляция, MVCC
         ↓
5. [[database-design-optimization]]     — Индексы, N+1, нормализация
         ↓
6. [[database-internals-complete]]      — Внутренности: B-Tree, WAL, buffer pool
         ↓
7. [[databases-nosql-comparison]]       — NoSQL: Document, Key-Value, Graph, Column
         ↓
8. [[databases-replication-sharding]]   — Репликация, шардинг, партиционирование
         ↓
9. [[databases-backup-recovery]]        — Бэкапы, DR, point-in-time recovery
         ↓
10. [[databases-monitoring-security]]   — Мониторинг, slow queries, безопасность
```

---

## Статьи по категориям

### Fundamentals
- [[databases-overview]] — карта раздела, обзор
- [[databases-fundamentals-complete]] — модели данных, ACID, CAP теорема, BASE
- [[databases-sql-fundamentals]] — SQL: SELECT, JOIN, агрегации, оконные функции
- [[databases-transactions-acid]] — транзакции, уровни изоляции, MVCC, deadlocks

### Design & Optimization
- [[database-design-optimization]] — индексы, N+1, нормализация/денормализация, EXPLAIN
- [[database-internals-complete]] — внутренности СУБД: B-Tree, WAL, buffer pool, query optimizer

### SQL vs NoSQL
- [[databases-nosql-comparison]] — Document, Key-Value, Graph, Column: когда что выбрать
- [[sql-databases-complete]] — PostgreSQL, MySQL, SQLite: особенности и выбор
- [[nosql-databases-complete]] — MongoDB, Redis, Cassandra, Neo4j: глубокое сравнение

### Specialized
- [[cloud-databases-complete]] — managed БД: RDS, Cloud SQL, DynamoDB, Cosmos DB
- [[mobile-databases-complete]] — SQLite, Room, Core Data, Realm, SQLDelight
- [[aiml-databases-complete]] — vector databases, pgvector, Pinecone, Chroma для AI/ML

### Operations
- [[databases-replication-sharding]] — репликация, шардинг, партиционирование
- [[databases-backup-recovery]] — бэкапы, disaster recovery, point-in-time recovery
- [[databases-monitoring-security]] — мониторинг, pg_stat_statements, безопасность

---

## Как выбрать тип БД: SQL vs NoSQL

**Почему это важно:** Неправильный выбор БД → проблемы масштабирования, сложные миграции, потеря данных. В 2025 году smart teams используют **polyglot persistence** — разные БД для разных задач.

### Decision Tree

```
Какой тип данных?
├── Структурированный (таблицы, связи, схема) → SQL
│    ├── Финансы, транзакции → PostgreSQL, MySQL (ACID критичен)
│    └── Сложные JOIN, analytics → PostgreSQL, ClickHouse
│
├── Полуструктурированный (документы, JSON) → Document DB
│    └── Продуктовые каталоги, CMS → MongoDB, Couchbase
│
├── Граф (связи между объектами) → Graph DB
│    └── Рекомендации, соцсети → Neo4j, Amazon Neptune
│
├── Key-Value (простой доступ по ключу) → Key-Value Store
│    └── Кэш, сессии, real-time → Redis, DynamoDB
│
└── Временные ряды (метрики, события) → Time-Series DB
     └── IoT, мониторинг → InfluxDB, TimescaleDB
```

### Сравнение SQL vs NoSQL

| Критерий | SQL (реляционные) | NoSQL |
|----------|-------------------|-------|
| **Схема** | Строгая, заранее определена | Гибкая, schema-less |
| **Масштабирование** | Вертикальное (сложнее) | Горизонтальное (проще) |
| **ACID** | Полная поддержка | Часто eventual consistency |
| **Запросы** | Мощный SQL, JOIN | Простые запросы, нет JOIN |
| **Примеры** | PostgreSQL, MySQL, Oracle | MongoDB, Redis, Cassandra |

### Когда SQL

- **Финансовые системы** — ACID обязателен, каждая транзакция должна быть точной
- **ERP, CRM** — сложные связи между сущностями, много JOIN
- **Отчётность** — SQL мощнее для аналитических запросов
- **Регулируемые отрасли** — здравоохранение, банкинг (compliance требует структуры)

### Когда NoSQL

- **Продуктовые каталоги** — гибкая схема, разные атрибуты для разных товаров
- **Real-time приложения** — геолокация, игры, чаты (низкая latency)
- **Big Data** — логи, события, метрики (горизонтальное масштабирование)
- **Прототипирование** — быстрая итерация без миграций схемы

---

## Polyglot Persistence: разные БД для разных задач

**Концепция:** Использовать несколько типов БД в одной системе, каждую для своих задач. Применяют Bank of America, Netflix, Facebook.

### Реальные примеры архитектур

**E-commerce платформа:**
```
┌─────────────────────────────────────────────────────────────┐
│                     E-commerce System                        │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL        │ Заказы, платежи, пользователи (ACID)   │
│  MongoDB           │ Каталог товаров (гибкая схема)         │
│  Redis             │ Корзина, сессии (low latency)          │
│  Neo4j             │ "Похожие товары" рекомендации          │
│  Elasticsearch     │ Полнотекстовый поиск товаров           │
└─────────────────────────────────────────────────────────────┘
```

**Ride-sharing приложение:**
```
┌─────────────────────────────────────────────────────────────┐
│                   Ride-sharing System                        │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL        │ Пользователи, платежи (ACID)           │
│  Redis             │ Активные поездки, геолокация (cache)   │
│  Cassandra         │ История поездок (write-heavy)          │
│  InfluxDB          │ Метрики, мониторинг водителей          │
└─────────────────────────────────────────────────────────────┘
```

### Когда НЕ использовать Polyglot Persistence

- **Маленькая команда** — сложность управления несколькими БД
- **Простое приложение** — одна PostgreSQL покроет 90% кейсов
- **Нужна строгая консистентность** — синхронизация между БД сложна
- **Ограниченный бюджет** — каждая БД требует мониторинга, бэкапов

---

## Ключевые концепции

| Концепция | Суть | Когда важно | Подробнее |
|-----------|------|-------------|-----------|
| **B-Tree Index** | O(log n) поиск вместо O(n) | При медленных SELECT | [[database-design-optimization]] |
| **N+1 Problem** | 1 + N запросов вместо 1 JOIN | При работе с ORM | [[database-design-optimization]] |
| **Normalization** | Нет дублирования, data integrity | При проектировании схемы | [[database-design-optimization]] |
| **Denormalization** | Быстрее reads за счёт дублирования | Read-heavy нагрузки | [[database-design-optimization]] |
| **Polyglot Persistence** | Разные БД для разных задач | Сложные системы | См. раздел выше |
| **Connection Pooling** | Переиспользование соединений | High-traffic приложения | [[database-design-optimization]] |
| **EXPLAIN** | Анализ плана выполнения запроса | Оптимизация slow queries | [[database-design-optimization]] |

---

## Связанные темы

- [[caching-strategies]] — Кэш поверх БД: когда Redis как кэш, когда как primary store
- [[event-driven-architecture]] — Event Sourcing как альтернатива традиционному CRUD
- [[observability]] — Мониторинг slow queries, pg_stat_statements
- [[microservices-vs-monolith]] — Database per service pattern в микросервисах
- [[cloud-platforms-essentials]] — Managed databases: RDS, Cloud SQL, Azure SQL

---

## Связанные области

- [[architecture-moc]] — microservices database patterns, event sourcing
- [[cloud-moc]] — managed database services (RDS, Cloud SQL)
- [[security-moc]] — защита данных, шифрование, доступ
- [[ai-engineering-moc]] — vector databases для RAG и embeddings

---

## Источники

- [Polyglot Persistence - Martin Fowler](https://martinfowler.com/bliki/PolyglotPersistence.html) — оригинальная статья Мартина Фаулера
- [SQL vs NoSQL - IBM](https://www.ibm.com/think/topics/iaas-paas-saas) — сравнение от IBM
- [NoSQL vs SQL in 2025 - Hackr.io](https://hackr.io/blog/nosql-vs-sql) — актуальное руководство
- [Polyglot Database Architectures - NaN Labs](https://www.nan-labs.com/v4/blog/polyglot-database-architecture/) — реальные примеры архитектур
- [SQL vs NoSQL: Differences - Coursera](https://www.coursera.org/articles/nosql-vs-sql) — академический взгляд

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 15 |
| Последнее обновление | 2026-02-09 |

---

*Проверено: 2025-12-18 | На основе Martin Fowler, IBM, практических кейсов Netflix, Bank of America*
