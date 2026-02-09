---
title: "Architecture MOC"
created: 2025-11-24
modified: 2025-11-24
type: moc
tags:
  - topic/architecture
  - type/moc
  - navigation
---

# Architecture MOC

> Архитектурные паттерны, решения и антипаттерны

---

## Статьи

### Архитектурные решения
- [[microservices-vs-monolith]] — Когда микросервисы, когда монолит. Кейсы Netflix, Uber, Shopify

### API и интеграции
- [[api-design]] — REST, GraphQL, gRPC. Когда что использовать, безопасность, версионирование

### Качество и долг
- [[technical-debt]] — $2 триллиона проблем. Southwest Airlines, Friendster, как измерять и бороться

### Производительность и масштабирование
- [[caching-strategies]] — Redis, стратегии кэширования, инвалидация. 10-1000x ускорение
- [[event-driven-architecture]] — Kafka, RabbitMQ, Event Sourcing, Saga pattern
- [[performance-optimization]] — From 3s to 300ms. Profiling, Frontend/Backend optimization, Web Vitals

---

## Связанные темы

- [[docker-for-developers]] — Инфраструктура для современной архитектуры
- [[ci-cd-pipelines]] — Автоматизация деплоя
- [[ai-engineering-moc]] — AI системы и их архитектура

---

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| Модульный монолит | Лучшее из двух миров | [[microservices-vs-monolith]] |
| Strangler Fig | Постепенная миграция | [[technical-debt]] |
| 15-20% правило | Бюджет на долг | [[technical-debt]] |
| REST vs GraphQL | Простота vs гибкость | [[api-design]] |
| OAuth 2.0 | Стандарт авторизации API | [[api-design]] |
| OpenAPI 3.2 | Стандарт документации | [[api-design]] |
| Cache-Aside | Ручное управление кэшем | [[caching-strategies]] |
| Thundering Herd | Проблема при cache miss | [[caching-strategies]] |
| Event Sourcing | События как источник истины | [[event-driven-architecture]] |
| Saga Pattern | Распределённые транзакции | [[event-driven-architecture]] |
| Outbox Pattern | Атомарность event + DB | [[event-driven-architecture]] |
| Core Web Vitals | LCP, FID, CLS — метрики UX | [[performance-optimization]] |
| Code Splitting | Lazy loading для меньших bundles | [[performance-optimization]] |
| Async Operations | Promise.all для параллельности | [[performance-optimization]] |
| Performance Budget | Лимиты размера bundles | [[performance-optimization]] |

---

## Статистика раздела

| Метрика | Значение |
|---------|----------|
| Всего заметок | 6 |
| Последнее обновление | 2025-11-24 |

---

*Последнее обновление: 2025-11-24*
