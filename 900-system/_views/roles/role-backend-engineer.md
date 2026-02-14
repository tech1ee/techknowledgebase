---
title: "Роль: Backend-инженер"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Роль: Backend-инженер

> Портал для backend-инженера. Фокус: распределённые системы, базы данных, сети, инфраструктура, безопасность.

---

## Основные области

| Область | Файлов | Приоритет | Обзор |
|---------|--------|-----------|-------|
| Architecture | 16 | **Критический** | [[architecture-overview]] |
| Databases | 16 | **Критический** | [[databases-overview]] |
| Networking | 23 | **Высокий** | [[networking-overview]] |
| DevOps | 10 | **Высокий** | [[devops-overview]] |
| Cloud | 7 | **Высокий** | [[cloud-overview]] |
| Security | 19 | **Высокий** | [[security-overview]] |

---

## Поддерживающие области

| Область | Файлов | Зачем бэкендеру | Обзор |
|---------|--------|-----------------|-------|
| JVM / Kotlin | 37 | JVM-серверная разработка, корутины | [[jvm-overview]] |
| Programming | 12 | Паттерны, SOLID, тестирование | [[programming-overview]] |
| CS Fundamentals | 63 | Алгоритмы для собеседований | [[cs-fundamentals-overview]] |
| CS Foundations | 23 | Память, конкурентность, компиляция | [[cs-foundations-overview]] |
| Operating Systems | 8 | Процессы, потоки, файловые системы | [[os-overview]] |

---

## Ключевые файлы

### Архитектура и проектирование

| Файл | О чём |
|------|-------|
| [[architecture-distributed-systems]] | Распределённые системы: CAP, консенсус, eventual consistency |
| [[microservices-vs-monolith]] | Выбор архитектуры: монолит vs микросервисы |
| [[api-design]] | Проектирование API |
| [[api-rest-deep-dive]] | REST: best practices, версионирование |
| [[api-grpc-deep-dive]] | gRPC: протокол, streaming, service mesh |
| [[api-graphql-deep-dive]] | GraphQL: схемы, резолверы, N+1 |
| [[event-driven-architecture]] | Событийная архитектура: Kafka, RabbitMQ |
| [[caching-strategies]] | Кеширование: Redis, CDN, стратегии инвалидации |
| [[architecture-resilience-patterns]] | Паттерны устойчивости: circuit breaker, retry, bulkhead |
| [[architecture-rate-limiting]] | Rate limiting и throttling |
| [[performance-optimization]] | Оптимизация производительности |

### Базы данных

| Файл | О чём |
|------|-------|
| [[databases-fundamentals-complete]] | Фундаментальные концепции баз данных |
| [[databases-transactions-acid]] | Транзакции и ACID |
| [[databases-replication-sharding]] | Репликация и шардирование |
| [[database-design-optimization]] | Проектирование схем и оптимизация запросов |
| [[databases-sql-fundamentals]] | SQL: joins, подзапросы, оконные функции |
| [[databases-nosql-comparison]] | Сравнение NoSQL баз данных |
| [[database-internals-complete]] | Внутренности: B-trees, WAL, MVCC |

### Сети и протоколы

| Файл | О чём |
|------|-------|
| [[network-fundamentals-for-developers]] | Основы сетей для разработчиков |
| [[network-http-evolution]] | HTTP/1.1 → HTTP/2 → HTTP/3 |
| [[network-dns-tls]] | DNS, TLS, сертификаты |
| [[network-realtime-protocols]] | WebSocket, SSE, gRPC streaming |
| [[network-performance-optimization]] | Оптимизация сетевой производительности |
| [[network-latency-optimization]] | Борьба с latency |

### Инфраструктура и DevOps

| Файл | О чём |
|------|-------|
| [[ci-cd-pipelines]] | CI/CD: GitHub Actions, Jenkins, GitLab CI |
| [[docker-for-developers]] | Docker: контейнеризация приложений |
| [[kubernetes-basics]] | Kubernetes: основы оркестрации |
| [[kubernetes-advanced]] | Kubernetes: продвинутые паттерны |
| [[infrastructure-as-code]] | IaC: Terraform, Pulumi |
| [[observability]] | Observability: логи, метрики, трейсы |
| [[devops-incident-management]] | Управление инцидентами |

### Безопасность

| Файл | О чём |
|------|-------|
| [[security-api-protection]] | Защита API: rate limiting, WAF, input validation |
| [[auth-oauth2-oidc]] | OAuth 2.0 и OpenID Connect |
| [[auth-sessions-jwt-tokens]] | Сессии, JWT, токены |
| [[security-https-tls]] | HTTPS и TLS |
| [[security-secrets-management]] | Управление секретами |
| [[threat-modeling]] | Моделирование угроз |

### Облако

| Файл | О чём |
|------|-------|
| [[cloud-overview]] | Обзор облачных платформ |
| [[cloud-aws-core-services]] | AWS: ключевые сервисы |
| [[cloud-gcp-core-services]] | GCP: ключевые сервисы |
| [[cloud-serverless-patterns]] | Serverless: паттерны и антипаттерны |
| [[cloud-networking-security]] | Облачные сети и безопасность |

---

## Рекомендуемая траектория обучения

- [[interleaved-backend-engineer]] -- интерливинг-маршрут для backend-инженера

### Порядок изучения

```
Фаза 1: Основы (1-2 мес.)
  [[databases-fundamentals-complete]] → [[databases-transactions-acid]]
  [[network-fundamentals-for-developers]] → [[network-http-evolution]]
  [[api-design]] → [[api-rest-deep-dive]]

Фаза 2: Архитектура (2-3 мес.)
  [[architecture-distributed-systems]] → [[microservices-vs-monolith]]
  [[caching-strategies]] → [[event-driven-architecture]]
  [[architecture-resilience-patterns]]

Фаза 3: Инфраструктура (1-2 мес.)
  [[docker-for-developers]] → [[kubernetes-basics]]
  [[ci-cd-pipelines]] → [[observability]]

Фаза 4: Продвинутое (2-3 мес.)
  [[databases-replication-sharding]] → [[database-internals-complete]]
  [[security-api-protection]] → [[auth-oauth2-oidc]]
  [[cloud-aws-core-services]] → [[cloud-serverless-patterns]]
```

---

## Связанные файлы

- [[Home]] -- главная навигация
- [[role-interview-candidate]] -- подготовка к собеседованиям
- [[maturity-ladder]] -- лестница компетенций
- [[quick-reference]] -- топ-30 файлов для быстрого доступа
- [[study-dashboard]] -- дашборд прогресса обучения
