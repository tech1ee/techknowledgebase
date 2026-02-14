---
title: "Интервью: System Design"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Подготовка к System Design интервью

Фреймворк, ключевые концепции, мобильная специфика, практические задачи.

---

## Фреймворк ответа (4 шага)

### 1. Clarify Requirements (5 мин)
- Функциональные: что система должна делать
- Нефункциональные: масштаб, latency, availability
- Ограничения: бюджет, команда, сроки

### 2. High-Level Design (10 мин)
- Основные компоненты и их взаимодействие
- API contract
- Data flow

### 3. Deep Dive (15 мин)
- Детали ключевых компонентов
- Trade-offs и обоснование решений
- Масштабирование

### 4. Wrap Up (5 мин)
- Bottlenecks и как их решить
- Мониторинг и observability
- Эволюция системы

---

## Ключевые концепции

### Архитектура
- [[architecture-overview]] — обзор архитектурных подходов
- [[architecture-distributed-systems]] — распределённые системы
  - CAP-теорема, Consistency models
  - Leader election, Consensus
  - Partitioning strategies

### Данные
- [[caching-strategies]] — стратегии кеширования
  - Cache-aside, Read-through, Write-through, Write-behind
  - TTL, Eviction policies
  - CDN, Application cache, Database cache
- [[databases-replication-sharding]] — репликация и шардирование
  - Master-slave, Multi-master
  - Horizontal vs Vertical sharding
  - Consistent hashing
- [[databases-transactions-acid]] — транзакции и ACID

### Коммуникация
- [[event-driven-architecture]] — event-driven паттерны
  - Message queues (Kafka, RabbitMQ)
  - Event sourcing, CQRS
  - Saga pattern
- [[microservices-vs-monolith]] — микросервисы vs монолит
  - Service discovery
  - API Gateway
  - Circuit breaker

### Инфраструктура
- [[architecture-rate-limiting]] — rate limiting
  - Token bucket, Sliding window
  - Distributed rate limiting
- [[architecture-resilience-patterns]] — паттерны устойчивости
  - Circuit breaker, Bulkhead, Retry
  - Timeout, Fallback
  - Health checks
- [[architecture-search-systems]] — поисковые системы
  - Inverted index
  - Full-text search
  - Ranking algorithms

### API
- [[api-design]] — принципы API-дизайна
- [[api-rest-deep-dive]] — REST
  - Pagination: cursor vs offset
  - Versioning
  - HATEOAS

---

## Мобильный System Design

### Фреймворк для мобильного SD
- [[system-design-android]] — мобильный system design
  - Client architecture
  - Networking layer
  - Data layer (offline-first)
  - Sync strategies

### Типичные мобильные задачи

#### 1. Messenger / Chat App
- Real-time: WebSocket / SSE
- Offline: local DB + sync queue
- Media: upload/download, thumbnails
- Notifications: push pipeline
- Связано: [[android-networking]], [[android-room-deep-dive]]

#### 2. Social Feed
- Pagination: cursor-based infinite scroll
- Caching: network → cache → UI
- Image loading: placeholders, lazy loading
- Pull-to-refresh, optimistic updates
- Связано: [[caching-strategies]], [[android-recyclerview-internals]]

#### 3. Offline-First App
- Conflict resolution: last-write-wins, CRDTs
- Sync: background sync, retry queue
- Storage: Room/SQLDelight + WorkManager
- Связано: [[android-data-persistence]], [[android-background-work]]

#### 4. Navigation / Maps App
- Location: GPS, network location
- Map rendering: tiles, clustering
- Route calculation: client vs server
- Battery: location frequency, geofencing
- Связано: [[android-app-startup-performance]]

#### 5. Media Player (Spotify-like)
- Streaming: adaptive bitrate
- Background playback: foreground service
- Downloads: offline content, DRM
- Queue management: state machine
- Связано: [[android-service-internals]], [[android-notifications]]

---

## Числа для оценки масштаба

| Метрика | Значение |
|---------|----------|
| DAU → QPS | 1M DAU ~ 100 QPS (если 10 req/user/day) |
| Storage | 1 tweet ~ 250 bytes, 1 photo ~ 500 KB |
| Bandwidth | 1 Gbps ~ 100 MB/s |
| SSD read | ~100 μs |
| Network roundtrip (same DC) | ~0.5 ms |
| Network roundtrip (cross-continent) | ~100 ms |
| Read from memory | ~100 ns |
| Read from SSD | ~100 μs |
| Read from HDD | ~10 ms |

---

## Распространённые ошибки

1. **Сразу в детали** — не уточнив requirements
2. **Один компонент** — не показать full system
3. **Нет trade-offs** — каждое решение имеет цену
4. **Игнорирование масштаба** — 100 users ≠ 100M users
5. **Забыть мониторинг** — как узнать что система работает

---

## Чеклист подготовки

### За 1 неделю
- [ ] Выучить фреймворк (4 шага)
- [ ] Прочитать [[architecture-distributed-systems]]
- [ ] Прочитать [[caching-strategies]]
- [ ] Прочитать [[system-design-android]]
- [ ] Решить 3 задачи по фреймворку

### За 1 месяц
- [ ] Все материалы из раздела "Ключевые концепции"
- [ ] 10+ задач по system design
- [ ] Mock interviews с фидбеком
- [ ] Выучить числа для back-of-envelope расчётов

---

## Связанные материалы
- [[architecture-overview]] — обзор архитектуры
- [[architecture-distributed-systems]] — распределённые системы
- [[caching-strategies]] — кеширование
- [[system-design-android]] — мобильный SD
- [[api-design]] — API-дизайн
- [[databases-overview]] — обзор баз данных
- [[performance-optimization]] — оптимизация производительности
