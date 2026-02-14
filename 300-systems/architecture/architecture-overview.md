---
title: "Software Architecture: Карта раздела"
created: 2025-12-22
modified: 2025-12-22
type: moc
status: published
confidence: high
tags:
  - topic/architecture
  - system-design
  - distributed-systems
  - type/moc
  - level/beginner
related:
  - "[[programming-overview]]"
  - "[[cloud-overview]]"
  - "[[databases-overview]]"
reading_time: 15
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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

## Связь с другими темами

**[[programming-overview]]** — Программирование и архитектура неразрывно связаны: архитектура определяет высокоуровневую структуру системы, а программные паттерны (SOLID, design patterns, clean code) обеспечивают качество реализации на уровне кода. Плохая архитектура невозможна без хорошей кодовой базы, и наоборот — чистый код без продуманной архитектуры превращается в хаос при масштабировании. Понимание обоих уровней — от паттернов проектирования до распределённых систем — необходимо для создания maintainable софта.

**[[cloud-overview]]** — Облачные платформы являются основной средой развёртывания современных архитектур. Managed-сервисы (очереди, базы данных, контейнерные оркестраторы) реализуют архитектурные паттерны: event-driven architecture через SQS/Pub-Sub, микросервисы через ECS/GKE, caching через ElastiCache/Memorystore. Выбор облачной платформы и её сервисов — это архитектурное решение, влияющее на стоимость, vendor lock-in и операционную сложность системы.

**[[databases-overview]]** — Базы данных — фундамент любой архитектуры, и выбор типа БД (реляционная, документная, графовая, колоночная) определяет возможности и ограничения системы. Архитектурные паттерны — CQRS, Event Sourcing, sharding, репликация — тесно связаны с особенностями хранения данных. Понимание CAP-теоремы, consistency моделей и trade-offs различных БД необходимо для принятия обоснованных архитектурных решений.

---

## Источники и дальнейшее чтение

- **Kleppmann M. (2017). Designing Data-Intensive Applications. O'Reilly.** — одна из важнейших книг по архитектуре, покрывающая модели данных, репликацию, партиционирование, транзакции и распределённые системы с глубоким теоретическим и практическим подходом
- **Newman S. (2021). Building Microservices. 2nd edition. O'Reilly.** — практическое руководство по проектированию, развёртыванию и эволюции микросервисных архитектур, включая service mesh, observability и миграцию с монолита
- **Ford N. et al. (2021). Software Architecture: The Hard Parts. O'Reilly.** — анализ сложных архитектурных решений (trade-off analysis, service granularity, data ownership), которые не имеют однозначно правильного ответа

---

*Проверено: 2025-12-22*

---

## Проверь себя

> [!question]- У вас стартап из 8 человек, product-market fit ещё не найден. CTO предлагает начать с микросервисов "чтобы потом не переписывать". Какие аргументы вы приведёте против?
> 1. **Premature optimization:** границы сервисов определяются практикой, не теорией — без понимания нагрузки вы проведёте границы неправильно. 2. **Пивоты:** при смене бизнес-модели придётся переписывать все сервисы и их контракты. 3. **Overhead:** 70% времени уйдёт на инфраструктуру (service discovery, API gateway, distributed tracing) вместо продукта. 4. **Distributed Monolith риск:** без опыта вы получите связанные сервисы с общей БД — худшее из обоих миров. Рекомендация: модульный монолит с чёткими границами модулей — подготовка к разделению без overhead.

> [!question]- Почему каждая дополнительная "девятка" в SLA (99.9% → 99.99% → 99.999%) стоит экспоненциально дороже?
> 99.9% = 8.7 часов downtime/год, 99.99% = 52 минуты, 99.999% = 5 минут. Переход от 8.7 часов к 52 минутам требует: multi-AZ deployment, автоматический failover, hot standby. Переход к 5 минутам добавляет: multi-region active-active, zero-downtime deployments, automated incident response. Каждый уровень требует удвоения инфраструктуры, команды и процессов. Правило: выбирайте SLA исходя из стоимости downtime для бизнеса, а не "чем больше, тем лучше".

> [!question]- Ваша система требует одновременно high consistency (банковские транзакции) и high availability (99.99%). Как CAP теорема влияет на ваш выбор архитектуры?
> CAP говорит: при network partition выбирайте CP или AP. Решение — **гибридная архитектура**: критические операции (платежи, баланс) используют CP-систему (PostgreSQL с synchronous replication), некритические (уведомления, аналитика) — AP-систему (Cassandra, eventual consistency). Разные части системы могут иметь разные consistency гарантии. DynamoDB предлагает tunable consistency — strong для чтения баланса, eventual для ленты активности.

> [!question]- Зачем документировать архитектурные решения через ADR, если "код — лучшая документация"?
> Код показывает КАК, но не ПОЧЕМУ. ADR фиксирует: контекст решения (какая проблема), рассмотренные альтернативы, принятые trade-offs, и последствия. Через 2 года новый разработчик видит Kafka в проекте, но без ADR не знает: почему не RabbitMQ? какие constraints учитывались? когда пересмотреть решение? ADR предотвращает бесконечные дискуссии ("мы это уже обсуждали") и позволяет пересмотреть решение при изменении контекста.

---

## Ключевые карточки

Что такое качественные атрибуты (quality attributes) в архитектуре?
?
Нефункциональные свойства системы: scalability, reliability, maintainability, security, performance. Архитектура — это решения, которые оптимизируют одни атрибуты за счёт других (trade-offs).

CAP теорема — что можно выбрать на практике?
?
При network partition: CP (consistency + partition tolerance) — banking, inventory; AP (availability + partition tolerance) — social media, caching. Без partition все три доступны. Многие системы предлагают tunable consistency (DynamoDB).

Что такое ADR и какой у него формат?
?
Architecture Decision Record: Title → Status (accepted/deprecated/superseded) → Context (почему) → Decision (что) → Consequences (trade-offs). Хранятся как нумерованные Markdown файлы в репозитории (ADR-001.md).

Чем SLI отличается от SLO и SLA?
?
SLI (Indicator) — метрика (latency P95 = 180ms). SLO (Objective) — целевое значение (P95 < 200ms). SLA (Agreement) — юридическое обязательство с последствиями при нарушении (99.9% uptime, иначе кредит).

В чём разница ACID и BASE?
?
ACID: Atomicity, Consistency, Isolation, Durability — строгие транзакции (SQL). BASE: Basically Available, Soft state, Eventually consistent — мягкие гарантии для масштабирования (NoSQL). ACID для корректности, BASE для производительности.

Рекомендуемый порядок эволюции архитектуры?
?
Monolith → Modular Monolith → Service-Oriented → Microservices. Start simple, evolve when needed. Modular Monolith (team 5-20, <1M users) — лучший старт в 2024-2025.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Первый шаг | [[api-design]] | Проектирование API — основа взаимодействия между компонентами |
| Следующий шаг | [[microservices-vs-monolith]] | Главный архитектурный выбор: когда что применять |
| Углубиться | [[architecture-distributed-systems]] | CAP, consistency, Saga — теория распределённых систем |
| Практика | [[caching-strategies]] | Оптимизация производительности через кэширование |
| Отказоустойчивость | [[architecture-resilience-patterns]] | Circuit breaker, retry, bulkhead — паттерны надёжности |
| Смежная тема | [[databases-overview]] | Выбор БД — фундамент архитектурных решений |
| Обзор | [[programming-overview]] | Code-level паттерны: SOLID, design patterns |
