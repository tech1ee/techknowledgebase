---
title: "Диагностика: Как выбрать архитектуру"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Как выбрать архитектуру

Руководство по принятию архитектурных решений для разных типов систем.

---

## Быстрый выбор

| Что строишь | Рекомендация | Материал |
|-------------|-------------|----------|
| Android-приложение | MVVM + Clean Architecture | [[android-architecture-patterns]] |
| iOS-приложение | MVVM или TCA | [[ios-architecture-patterns]] |
| KMP shared-модуль | MVI + Clean | [[kmp-architecture-patterns]] |
| Микросервисный бэкенд | Event-driven + DDD | [[event-driven-architecture]] |
| Монолит → микросервисы | Strangler Fig Pattern | [[microservices-vs-monolith]] |
| Выбор API | REST / GraphQL / gRPC | [[api-design]] |

---

## Мобильная архитектура

### Android
- **Паттерны:** MVVM, MVI, Clean Architecture — [[android-architecture-patterns]]
- **Эволюция:** от God Activity к Compose — [[android-architecture-evolution]]
- **Модуляризация:** разбиение на модули — [[android-modularization]]
- **Навигация:** подходы и фреймворки — [[android-navigation]]
- **Repository:** организация слоя данных — [[android-repository-pattern]]
- **ViewModel:** детали реализации — [[android-viewmodel-internals]]

### iOS
- **Паттерны:** MVC, MVVM, VIPER, TCA — [[ios-architecture-patterns]]
- **Эволюция:** от MVC к SwiftUI — [[ios-architecture-evolution]]
- **Модуляризация:** SPM, фреймворки — [[ios-modularization]]
- **ViewModel:** паттерны для SwiftUI — [[ios-viewmodel-patterns]]
- **Repository:** организация данных — [[ios-repository-pattern]]

### Кросс-платформа
- **KMP-архитектура:** паттерны для shared-кода — [[kmp-architecture-patterns]]
- **Кросс-платформенный обзор:** [[cross-architecture]]
- **KMP-специфика:** [[cross-kmp-patterns]]

---

## Серверная архитектура

### Монолит или микросервисы?
- **Сравнение подходов:** [[microservices-vs-monolith]]
- Стартап / MVP / маленькая команда → Модульный монолит
- Большая организация / независимые домены → Микросервисы
- Нужна гибкость деплоя → Микросервисы

### Паттерны распределённых систем
- **Обзор:** [[architecture-distributed-systems]]
- **Устойчивость:** circuit breaker, retry, bulkhead — [[architecture-resilience-patterns]]
- **Rate limiting:** защита от перегрузки — [[architecture-rate-limiting]]
- **Кеширование:** стратегии и уровни — [[caching-strategies]]
- **Поисковые системы:** [[architecture-search-systems]]

### Event-Driven Architecture
- **Паттерны:** CQRS, Event Sourcing, Saga — [[event-driven-architecture]]
- Подходит для: асинхронные процессы, eventual consistency, интеграция систем

---

## Выбор API

| Сценарий | API стиль | Материал |
|----------|----------|----------|
| Публичный API | REST | [[api-rest-deep-dive]] |
| Mobile BFF | GraphQL | [[api-graphql-deep-dive]] |
| Внутренние сервисы | gRPC | [[api-grpc-deep-dive]] |
| Real-time | WebSocket / SSE | [[api-modern-patterns]] |

- **Общие принципы API-дизайна:** [[api-design]]
- **Современные паттерны:** [[api-modern-patterns]]

---

## Процесс принятия решений

### Фреймворк
1. **Контекст:** размер команды, навыки, сроки, масштаб
2. **Требования:** функциональные и нефункциональные
3. **Ограничения:** бюджет, технологический стек, legacy
4. **Альтернативы:** минимум 2-3 варианта
5. **Решение:** задокументировать через ADR

### Документирование
- [[architecture-decisions]] — Architecture Decision Records (ADR)
- [[technical-vision]] — техническое видение продукта

---

## Антипаттерны

1. **Resume-Driven Architecture** — выбор ради резюме, а не продукта
2. **Golden Hammer** — использование одного паттерна для всего
3. **Premature Microservices** — микросервисы без необходимости
4. **Analysis Paralysis** — бесконечный анализ вместо решения

---

## Связанные материалы
- [[architecture-overview]] — обзор архитектуры
- [[dependency-injection-fundamentals]] — принципы DI
- [[performance-optimization]] — оптимизация производительности
- [[technical-debt]] — технический долг
