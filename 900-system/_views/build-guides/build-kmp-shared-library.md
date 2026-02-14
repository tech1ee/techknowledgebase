---
title: "Сборка: KMP Shared-библиотека"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# KMP Shared-библиотека

Полное руководство по созданию Kotlin Multiplatform shared-модуля.

---

## Фаза 1: Основы и структура

### Фундамент KMP
- [[kmp-overview]] — что такое KMP и зачем
- [[kmp-getting-started]] — начало работы
- [[kmp-project-structure]] — структура проекта
- [[kmp-source-sets]] — source sets (commonMain, androidMain, iosMain)
- [[kmp-expect-actual]] — механизм expect/actual

### Чеклист
- [ ] Kotlin Multiplatform plugin в Gradle
- [ ] Source sets: commonMain, commonTest, androidMain, iosMain
- [ ] Targets: Android, iOS (arm64, simulatorArm64)
- [ ] Настройка cocoapods или SPM для iOS
- [ ] CI с проверкой всех targets

---

## Фаза 2: Архитектура

### Паттерны и состояние
- [[kmp-architecture-patterns]] — архитектурные паттерны для KMP
- [[kmp-di-patterns]] — Dependency Injection в KMP
- [[kmp-state-management]] — управление состоянием
- [[kmp-navigation]] — навигация (если shared)

### Рекомендуемая архитектура
```
shared/
├── commonMain/
│   ├── domain/          ← use cases, entities
│   ├── data/            ← repositories, data sources
│   ├── network/         ← API clients
│   └── di/              ← DI modules
├── androidMain/
│   └── platform/        ← Android-специфичный код
└── iosMain/
    └── platform/        ← iOS-специфичный код
```

### Чеклист
- [ ] Clean Architecture: domain не зависит от platform
- [ ] DI: kotlin-inject или Koin
- [ ] State: StateFlow для реактивных данных
- [ ] expect/actual: минимум, только для платформенных API

---

## Фаза 3: Данные и сеть

### Networking
- [[kmp-ktor-networking]] — Ktor Client для KMP
  - HTTP-клиент, сериализация, interceptors
  - Engine: OkHttp (Android), Darwin (iOS)

### Хранение данных
- [[kmp-sqldelight-database]] — SQLDelight для KMP
  - SQL-first подход, compile-time проверка
  - Драйверы: Android SQLite, Native SQLite (iOS)

### Сериализация и утилиты
- [[kmp-kotlinx-libraries]] — kotlinx библиотеки
  - kotlinx.serialization: JSON, Protobuf
  - kotlinx.datetime: дата и время
  - kotlinx.coroutines: асинхронность

### Чеклист
- [ ] Ktor: HttpClient, ContentNegotiation, Logging
- [ ] SQLDelight: схема, миграции, запросы
- [ ] Serialization: @Serializable модели
- [ ] Coroutines: Dispatchers для каждой платформы

---

## Фаза 4: Тестирование

### Стратегия
- [[kmp-testing-strategies]] — общая стратегия тестирования
- [[kmp-unit-testing]] — unit-тесты в commonTest
- [[kmp-integration-testing]] — интеграционные тесты

### Чеклист
- [ ] commonTest: тесты domain и data слоёв
- [ ] kotlin-test: assertions, annotations
- [ ] Turbine: тестирование Flow
- [ ] Ktor MockEngine: тестирование API
- [ ] SQLDelight in-memory driver: тестирование БД
- [ ] CI: запуск тестов на всех targets

---

## Фаза 5: Интеграция с платформами

### Android
- [[kmp-android-integration]] — интеграция с Android
  - shared модуль как Gradle-зависимость
  - Прямой доступ к Kotlin API
  - Корутины и Flow нативно

### iOS
- [[kmp-ios-deep-dive]] — интеграция с iOS
  - Framework через CocoaPods или SPM
  - SKIE для улучшения Swift interop
  - Маппинг Kotlin → Swift типов

### Чеклист
- [ ] Android: shared как implementation зависимость
- [ ] iOS: framework export через cocoapods {} или SPM
- [ ] iOS: SKIE для sealed classes, coroutines, Flow
- [ ] API surface: удобный для обеих платформ

---

## Фаза 6: Сборка и публикация

### Gradle
- [[kmp-gradle-deep-dive]] — настройка Gradle для KMP
  - Targets и source sets
  - Зависимости: commonMain, platformMain
  - Build performance: кеши, параллельная сборка

### Публикация
- [[kmp-publishing]] — публикация shared-модуля
  - Maven: для Android-потребителей
  - CocoaPods / SPM: для iOS-потребителей
  - Version catalog для согласованности

### CI/CD
- [[kmp-ci-cd]] — CI/CD для KMP
  - macOS runner обязателен (для iOS)
  - Матрица: Android + iOS targets
  - Автоматическая публикация артефактов

### Чеклист
- [ ] Gradle: оптимизированная конфигурация
- [ ] Maven publish: для internal/external consumption
- [ ] CocoaPods/SPM: framework для iOS
- [ ] CI: macOS, Android + iOS тесты
- [ ] Versioning: SemVer, changelog

---

## Типичные проблемы и решения

### Отладка
- [[kmp-debugging]] — отладка KMP-кода
- [[kmp-troubleshooting]] — решение частых проблем

### Производительность
- [[kmp-performance-optimization]] — оптимизация KMP
- [[kmp-memory-management]] — управление памятью (GC vs ARC)

### Interop
- [[kmp-interop-deep-dive]] — глубокий interop Kotlin ↔ Swift/ObjC

### Продакшн
- [[kmp-production-checklist]] — чеклист для продакшена
- [[kmp-case-studies]] — кейсы использования KMP

---

## Связанные материалы
- [[kmp-overview]] — обзор KMP
- [[kmp-moc]] — карта знаний KMP
- [[compose-mp-overview]] — Compose Multiplatform (shared UI)
- [[cross-platform-overview]] — обзор кросс-платформы
- [[kmp-third-party-libs]] — сторонние KMP-библиотеки
