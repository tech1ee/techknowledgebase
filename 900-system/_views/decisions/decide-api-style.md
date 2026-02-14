---
title: "Решение: REST vs GraphQL vs gRPC"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# REST vs GraphQL vs gRPC

Дерево решений для выбора стиля API.

---

## Быстрый ответ

| Сценарий | Стиль API | Почему |
|----------|----------|-------|
| Публичный API | REST | Универсальность, стандарты, документация |
| Mobile BFF (Backend For Frontend) | GraphQL | Гибкие запросы, меньше over-fetching |
| Микросервисы (внутренние) | gRPC | Производительность, строгие контракты |
| Real-time обновления | WebSocket / SSE | Push-модель, low latency |
| Простой CRUD | REST | Не усложняй |
| Сложная модель данных, множество клиентов | GraphQL | Каждый клиент берёт что нужно |
| High-throughput, low-latency | gRPC | Binary protocol, HTTP/2 |

---

## Дерево решений

```
Какой стиль API выбрать?
│
├── Кто потребитель?
│   ├── Внешние разработчики → REST
│   │   (универсальность, документация, OpenAPI)
│   │
│   ├── Собственные мобильные приложения → GraphQL или REST
│   │   ├── Много разных экранов с разными данными → GraphQL
│   │   ├── Простой CRUD → REST
│   │   └── Нужен offline-first → REST + стандартный кеш
│   │
│   ├── Внутренние сервисы → gRPC
│   │   (производительность, строгие типы)
│   │
│   └── Браузер (SPA) → REST или GraphQL
│       ├── Много вложенных данных → GraphQL
│       └── Простые ресурсы → REST
│
├── Требования к производительности?
│   ├── Критичны (< 10ms latency) → gRPC
│   ├── Обычные → REST или GraphQL
│   └── Real-time → WebSocket / SSE
│
└── Размер команды?
    ├── Маленькая → REST (проще)
    ├── Средняя → REST или GraphQL
    └── Большая → GraphQL + gRPC (разные уровни)
```

---

## Сравнительная таблица

| Критерий | REST | GraphQL | gRPC |
|----------|------|---------|------|
| Протокол | HTTP/1.1, HTTP/2 | HTTP | HTTP/2 |
| Формат данных | JSON (обычно) | JSON | Protocol Buffers |
| Типизация | OpenAPI (опционально) | Schema (обязательно) | Proto (обязательно) |
| Over-fetching | Да | Нет | Нет |
| Under-fetching | Да | Нет | Зависит |
| Кеширование | HTTP cache (стандарт) | Сложнее | Нет стандарта |
| Real-time | Нет (нужен SSE/WS) | Subscriptions | Streaming |
| Браузер | Да | Да | Ограничено (gRPC-Web) |
| Кривая обучения | Низкая | Средняя | Средняя |
| Tooling | Отличный | Отличный | Хороший |

---

## REST

### Когда выбирать
- Публичный API с внешними потребителями
- Простой CRUD без сложных связей
- Нужно стандартное HTTP-кеширование
- Маленькая команда, нужен быстрый старт

### Материалы
- [[api-rest-deep-dive]] — глубокое погружение в REST
- [[api-design]] — общие принципы API-дизайна

### Ключевые практики
- Versioning: URI path (`/v1/`) или headers
- HATEOAS для discoverability
- OpenAPI/Swagger для документации
- Pagination: cursor-based для мобильных

---

## GraphQL

### Когда выбирать
- Много разных клиентов (web, mobile, TV)
- Сложная модель данных со связями
- Проблема over-fetching / under-fetching
- Нужен BFF (Backend For Frontend)

### Материалы
- [[api-graphql-deep-dive]] — глубокое погружение в GraphQL

### Ключевые практики
- DataLoader для N+1 проблемы
- Persisted queries для безопасности
- Depth limiting для защиты от злоупотреблений
- Schema-first design

---

## gRPC

### Когда выбирать
- Межсервисная коммуникация (service-to-service)
- Нужна высокая производительность
- Строгие контракты между командами
- Streaming данных

### Материалы
- [[api-grpc-deep-dive]] — глубокое погружение в gRPC

### Ключевые практики
- Proto-first design
- Backward-compatible schema evolution
- Interceptors для логирования и мониторинга
- gRPC-Web для браузерных клиентов

---

## Современные паттерны и комбинации

### Типичные комбинации
```
Mobile App → GraphQL (BFF) → gRPC → Microservices
Web App → REST или GraphQL → gRPC → Microservices
3rd Party → REST (Public API)
```

### Подробнее
- [[api-modern-patterns]] — современные паттерны API
- [[api-design]] — общие принципы проектирования API

---

## Связанные материалы
- [[api-design]] — принципы API-дизайна
- [[api-rest-deep-dive]] — REST
- [[api-graphql-deep-dive]] — GraphQL
- [[api-grpc-deep-dive]] — gRPC
- [[api-modern-patterns]] — современные паттерны
- [[android-networking]] — сеть в Android
- [[ios-networking]] — сеть в iOS
- [[kmp-ktor-networking]] — Ktor для KMP
