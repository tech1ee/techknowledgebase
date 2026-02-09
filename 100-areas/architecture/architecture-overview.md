---
title: "Software Architecture: Карта раздела"
created: 2025-12-22
modified: 2025-12-22
type: moc
status: verified
confidence: high
tags:
  - moc
  - architecture
  - system-design
  - distributed-systems
related:
  - "[[programming-overview]]"
  - "[[cloud-overview]]"
  - "[[databases-overview]]"
---

# Software Architecture: Карта раздела

> Архитектура — это решения, которые сложно изменить. Выбирай мудро.

---

## TL;DR

- **Архитектура** — структурные решения системы, влияющие на качественные атрибуты (scalability, reliability, maintainability)
- **Ключевые trade-offs:** Consistency vs Availability, Simplicity vs Flexibility, Cost vs Performance
- **Главный принцип:** Start simple, evolve when needed. Premature optimization = root of all evil

---

## Быстрая навигация

| Вопрос | Куда идти |
|--------|-----------|
| Monolith или microservices? | [[microservices-vs-monolith]] |
| Как проектировать API? | [[api-design]] |
| Event-driven подход? | [[event-driven-architecture]] |
| Как кэшировать? | [[caching-strategies]] |
| Распределённые системы? | [[architecture-distributed-systems]] |
| Отказоустойчивость? | [[architecture-resilience-patterns]] |
| Rate limiting? | [[architecture-rate-limiting]] |
| Поиск и Elasticsearch? | [[architecture-search-systems]] |
| Оптимизация производительности? | [[performance-optimization]] |
| Технический долг? | [[technical-debt]] |

---

## Architectural Decision Framework

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   ARCHITECTURE DECISION FRAMEWORK                           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. UNDERSTAND REQUIREMENTS                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Functional:                  Non-Functional:                       │   │
│  │  • What system does           • Scalability (10x, 100x?)           │   │
│  │  • Core features              • Availability (99.9%? 99.99%?)      │   │
│  │  • User flows                 • Latency (P95 < 200ms?)             │   │
│  │                               • Security, Compliance               │   │
│  │                               • Cost constraints                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│  2. IDENTIFY TRADE-OFFS                                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Consistency ◀──────────────────────────▶ Availability              │   │
│  │  Simplicity  ◀──────────────────────────▶ Flexibility               │   │
│  │  Cost        ◀──────────────────────────▶ Performance               │   │
│  │  Speed       ◀──────────────────────────▶ Quality                   │   │
│  │                                                                      │   │
│  │  Pick 2, optimize for them. Accept trade-offs on others.           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│  3. EVALUATE OPTIONS                                                       │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                      │   │
│  │  Option A: Monolith                                                 │   │
│  │  ├── Pros: Simple, fast, easy debugging                            │   │
│  │  ├── Cons: Scaling limits, deployment coupling                     │   │
│  │  └── Fit: Small team, early stage                                  │   │
│  │                                                                      │   │
│  │  Option B: Microservices                                           │   │
│  │  ├── Pros: Independent scaling, team autonomy                      │   │
│  │  ├── Cons: Complexity, network overhead                            │   │
│  │  └── Fit: Large team, high scale needs                            │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                   │                                         │
│                                   ▼                                         │
│  4. DOCUMENT DECISION (ADR)                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Title: Use Event-Driven Architecture for Order Processing          │   │
│  │  Status: Accepted                                                   │   │
│  │  Context: Order volume growing, sync processing hits limits        │   │
│  │  Decision: Use Kafka for async order processing                    │   │
│  │  Consequences: Added complexity, eventual consistency              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Путь обучения

```
УРОВЕНЬ 1: Developer (понимаю архитектуру)
└── [[api-design]] → [[caching-strategies]] → [[microservices-vs-monolith]]

УРОВЕНЬ 2: Senior Developer (принимаю архитектурные решения)
└── [[event-driven-architecture]] → [[architecture-distributed-systems]] → [[architecture-resilience-patterns]]

УРОВЕНЬ 3: Architect (проектирую системы)
└── [[architecture-rate-limiting]] → [[architecture-search-systems]] → [[performance-optimization]]

РЕКОМЕНДУЕМЫЙ ПОРЯДОК:
1. API Design (2-3 дня)           ← REST, GraphQL, gRPC
2. Caching (2-3 дня)              ← Cache strategies
3. Monolith vs Microservices      ← Когда что выбирать
4. Event-Driven (3-5 дней)        ← CQRS, Event Sourcing
5. Distributed Systems (1 неделя) ← CAP, consistency
6. Resilience Patterns (2-3 дня)  ← Circuit breaker, retry
7. Rate Limiting (1-2 дня)        ← Protection patterns
8. Search Systems (2-3 дня)       ← Elasticsearch
```

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Scalability** | Способность обрабатывать растущую нагрузку |
| **Availability** | Процент времени, когда система работает (99.9% = 8.7h downtime/год) |
| **Latency** | Время ответа системы |
| **Throughput** | Количество операций в единицу времени |
| **CAP Theorem** | Consistency, Availability, Partition Tolerance — выбери 2 |
| **ACID** | Atomicity, Consistency, Isolation, Durability (транзакции) |
| **BASE** | Basically Available, Soft state, Eventually consistent |
| **SLA/SLO/SLI** | Agreement/Objective/Indicator — метрики надёжности |

---

## Структура раздела

### Core Architecture

| Статья | Описание |
|--------|----------|
| [[microservices-vs-monolith]] | Trade-offs, когда что выбирать |
| [[api-design]] | REST, GraphQL, gRPC — проектирование API |
| [[event-driven-architecture]] | Events, CQRS, Event Sourcing |

### Data & Storage

| Статья | Описание |
|--------|----------|
| [[caching-strategies]] | Cache-aside, Write-through, TTL стратегии |
| [[architecture-search-systems]] | Elasticsearch, full-text search |
| [[databases-overview]] | → Database раздел |

### Distributed Systems

| Статья | Описание |
|--------|----------|
| [[architecture-distributed-systems]] | CAP, consistency, Saga pattern |
| [[architecture-resilience-patterns]] | Circuit breaker, retry, bulkhead |
| [[architecture-rate-limiting]] | Token bucket, distributed limiting |

### Operations

| Статья | Описание |
|--------|----------|
| [[performance-optimization]] | Profiling, optimization strategies |
| [[technical-debt]] | Управление техническим долгом |

---

## Architecture Patterns Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    ARCHITECTURE PATTERNS SPECTRUM                           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  SIMPLICITY ◀────────────────────────────────────────────▶ COMPLEXITY      │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Monolith │  │ Modular  │  │  Service │  │  Micro-  │  │  Distrib │    │
│  │          │  │ Monolith │  │ Oriented │  │ services │  │  Systems │    │
│  │          │  │          │  │          │  │          │  │          │    │
│  │ 1 deploy │  │ 1 deploy │  │ 3-10     │  │ 10-100   │  │ Complex  │    │
│  │ 1 DB     │  │ modules  │  │ services │  │ services │  │ mesh     │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│       │              │              │              │              │        │
│       ▼              ▼              ▼              ▼              ▼        │
│  Team: 1-5      Team: 5-15     Team: 15-50   Team: 50-200  Team: 200+    │
│  Stage: MVP     Stage: Growth  Stage: Scale  Stage: Large  Stage: FAANG   │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

### Когда что использовать

| Pattern | Team Size | Scale | Когда НЕ использовать |
|---------|-----------|-------|----------------------|
| **Monolith** | 1-10 | < 100K users | Нужна независимая масштабируемость |
| **Modular Monolith** | 5-20 | < 1M users | Уже есть legacy mess |
| **Microservices** | 20+ | 1M+ users | Маленькая команда, MVP |
| **Event-Driven** | Any | High throughput | Simple CRUD, low latency |
| **Serverless** | Any | Variable load | Predictable high load |

---

## System Design Checklist

```
┌────────────────────────────────────────────────────────────────────────────┐
│                    SYSTEM DESIGN CHECKLIST                                  │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  □ FUNCTIONAL REQUIREMENTS                                                 │
│    □ Core features defined                                                 │
│    □ User stories documented                                               │
│    □ API contracts specified                                               │
│                                                                             │
│  □ NON-FUNCTIONAL REQUIREMENTS                                             │
│    □ Expected load (users, RPS, data volume)                              │
│    □ Latency requirements (P50, P95, P99)                                 │
│    □ Availability target (99.9%? 99.99%?)                                 │
│    □ Data retention and compliance                                        │
│                                                                             │
│  □ DATA DESIGN                                                             │
│    □ Data model defined                                                   │
│    □ Database choice justified                                            │
│    □ Indexing strategy                                                    │
│    □ Caching strategy                                                     │
│                                                                             │
│  □ API DESIGN                                                              │
│    □ Protocol chosen (REST/GraphQL/gRPC)                                  │
│    □ Versioning strategy                                                  │
│    □ Error handling                                                       │
│    □ Rate limiting                                                        │
│                                                                             │
│  □ RESILIENCE                                                              │
│    □ Failure modes identified                                             │
│    □ Retry/circuit breaker policies                                       │
│    □ Fallback strategies                                                  │
│    □ Disaster recovery plan                                               │
│                                                                             │
│  □ SECURITY                                                                │
│    □ Authentication/Authorization                                         │
│    □ Data encryption (transit + rest)                                     │
│    □ Input validation                                                     │
│    □ Audit logging                                                        │
│                                                                             │
│  □ OBSERVABILITY                                                           │
│    □ Logging strategy                                                     │
│    □ Metrics and alerts                                                   │
│    □ Distributed tracing                                                  │
│    □ Health checks                                                        │
│                                                                             │
│  □ OPERATIONS                                                              │
│    □ Deployment strategy                                                  │
│    □ Rollback plan                                                        │
│    □ On-call runbooks                                                     │
│    □ Capacity planning                                                    │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Key Trade-offs

### Consistency vs Availability (CAP)

| Выбор | Описание | Use Cases |
|-------|----------|-----------|
| **CP** | Consistency + Partition tolerance | Banking, inventory |
| **AP** | Availability + Partition tolerance | Social media, caching |

### Sync vs Async

| Sync | Async |
|------|-------|
| Простой код | Сложный код |
| Blocking | Non-blocking |
| Меньше throughput | Больше throughput |
| Immediate feedback | Eventual feedback |
| User-facing | Background processing |

### SQL vs NoSQL

| SQL | NoSQL |
|-----|-------|
| ACID guarantees | Eventual consistency |
| Fixed schema | Flexible schema |
| Complex queries | Simple queries |
| Vertical scaling | Horizontal scaling |
| Relational data | Document/Key-value |

---

## Проверь себя

<details>
<summary>1. Когда выбрать microservices вместо monolith?</summary>

**Ответ:**

Microservices оправданы когда:
1. **Команда большая** (>20 человек, >3 команды)
2. **Разная скорость изменений** частей системы
3. **Разные требования к масштабированию**
4. **Разные технологические стеки** нужны
5. **Независимые деплои** критичны

НЕ выбирай microservices если:
- Маленькая команда (1-10)
- MVP / ранняя стадия
- Нет опыта с distributed systems
- Нет DevOps культуры

**Правило:** Начни с monolith, разделяй когда больно.

</details>

<details>
<summary>2. Что такое CAP теорема на практике?</summary>

**Ответ:**

**CAP:** В распределённой системе при network partition нужно выбрать между:
- **Consistency** — все узлы видят одинаковые данные
- **Availability** — каждый запрос получает ответ

**На практике:**
- Network partitions случаются редко
- Выбор делается для worst case scenario
- Многие системы предлагают "tunable consistency"

**Примеры:**
- PostgreSQL single-node: CA (нет partition)
- PostgreSQL with sync replication: CP
- Cassandra: AP (eventual consistency)
- DynamoDB: Configurable (strong or eventual)

</details>

<details>
<summary>3. Как определить нужный уровень availability?</summary>

**Ответ:**

| SLA | Downtime/год | Downtime/месяц | Use Case |
|-----|-------------|----------------|----------|
| 99% | 3.65 дня | 7.2 часа | Internal tools |
| 99.9% | 8.7 часа | 43 минуты | Standard SaaS |
| 99.99% | 52 минуты | 4.3 минуты | Critical business |
| 99.999% | 5 минут | 26 секунд | Healthcare, finance |

**Факторы выбора:**
- Стоимость downtime для бизнеса
- Стоимость достижения SLA
- Конкурентные требования
- Регуляторные требования

**Каждая "девятка" стоит экспоненциально дороже!**

</details>

<details>
<summary>4. Зачем нужны ADR (Architecture Decision Records)?</summary>

**Ответ:**

**ADR фиксирует:**
- Context — почему возникла необходимость
- Decision — что решили
- Consequences — какие trade-offs приняли
- Status — accepted/deprecated/superseded

**Польза:**
1. **Onboarding** — новые члены команды понимают "почему так"
2. **Revisiting** — можно пересмотреть при изменении контекста
3. **Avoiding repeat** — не обсуждаем одно и то же
4. **Accountability** — понятно кто и когда принял решение

**Формат:** Markdown файлы в репозитории, нумерованные (ADR-001.md)

</details>

---

## Связи с другими разделами

- [[cloud-overview]] — Cloud patterns
- [[databases-overview]] — Database architecture
- [[devops-overview]] — Deployment & operations
- [[security-overview]] — Security architecture
- [[programming-overview]] — Code-level patterns

---

## Источники

- "Designing Data-Intensive Applications" by Martin Kleppmann
- "Building Microservices" by Sam Newman
- "Software Architecture: The Hard Parts" by Neal Ford
- [Microsoft Architecture Center](https://docs.microsoft.com/en-us/azure/architecture/)
- [AWS Architecture Center](https://aws.amazon.com/architecture/)

---

*Проверено: 2025-12-22*
