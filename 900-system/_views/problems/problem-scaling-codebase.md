---
title: "Диагностика: Кодовая база выходит из-под контроля"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Кодовая база выходит из-под контроля

Руководство для растущих проектов: модуляризация, архитектура, сборка, команда.

---

## Симптомы

| Симптом | Корневая причина | Раздел |
|---------|-----------------|--------|
| Сборка занимает > 5 минут | Монолитный модуль, плохая конфигурация Gradle | Сборка |
| Каждый PR вызывает конфликты | Слишком связанный код, один модуль | Модуляризация |
| Новые разработчики входят месяцами | Нет границ, нет документации | Команда |
| Фича в одном месте ломает другое | Нет чётких границ, общее состояние | Архитектура |
| Тесты падают рандомно | Flaky тесты, связанность | Качество |

---

## Модуляризация

### Android
- **Стратегия модуляризации:** [[android-modularization]]
  - По фичам (feature modules)
  - По слоям (data, domain, presentation)
  - Гибрид: по фичам + общие слои
- **Зависимости между модулями:** [[android-dependencies]]
- **Граф зависимостей:** [[android-gradle-fundamentals]]

### iOS
- **Модуляризация:** [[ios-modularization]]
  - Swift Package Manager
  - Фреймворки
  - Workspace с несколькими проектами

### Когда модуляризировать?
```
Размер команды > 5 → обязательно
Время сборки > 3 мин → обязательно
Один модуль > 500 файлов → обязательно
Команда < 3, проект маленький → не нужно
```

---

## Архитектура

### Эволюция архитектуры
- **Android:** от God Activity к многомодульному Clean Architecture — [[android-architecture-evolution]]
- **Общие принципы:** [[architecture-overview]]

### Ключевые решения при росте
1. **Разделение слоёв** — UI, Domain, Data
2. **Инверсия зависимостей** — domain не зависит от framework
3. **Feature-flag система** — независимая доставка фич
4. **Navigation framework** — [[android-navigation]], [[ios-navigation]]

### Паттерны для больших кодовых баз
- [[android-architecture-patterns]] — MVVM, MVI, Clean Architecture
- [[ios-architecture-patterns]] — архитектурные паттерны iOS
- [[design-patterns]] — общие паттерны проектирования
- [[clean-code-solid]] — SOLID-принципы

---

## Сборка и CI/CD

### Оптимизация сборки Android
- **Gradle fundamentals:** [[android-gradle-fundamentals]]
  - Настройка кешей (local + remote)
  - Параллельная сборка
  - Configuration cache
  - Build scan анализ
- **Зависимости:** [[android-dependencies]]
  - Version catalog
  - BOM для согласованных версий
  - Dependency locking
- **Эволюция систем сборки:** [[android-build-evolution]]

### CI/CD
- **Android CI/CD:** [[android-ci-cd]]
- **iOS CI/CD:** [[ios-ci-cd]]
- **Общие принципы:** [[ci-cd-pipelines]]
- **Git-воркфлоу:** [[git-workflows]]

---

## Масштабирование команды

### Организация
- **Масштабирование инженерной организации:** [[scaling-engineering-org]]
- **Структуры команд:** [[team-structures]]
  - Squad model (Spotify)
  - Platform teams
  - Embedded vs centralized

### Процессы для больших команд
- **Code ownership** — CODEOWNERS файл, ответственность за модули
- **RFC-процесс** — для значимых изменений
- **ADR** — Architecture Decision Records — [[architecture-decisions]]
- **Инженерные практики:** [[engineering-practices]]

### Онбординг в большой проект
- [[onboarding]] — процесс онбординга
- Модульная документация — README в каждом модуле
- Architecture diagrams — актуальные диаграммы
- Starter tasks — простые задачи для входа

---

## План действий

### Быстрые победы (1-2 недели)
1. Настроить Gradle build cache
2. Включить параллельную сборку
3. Добавить CODEOWNERS
4. Lint + format автоматически в CI

### Среднесрочные (1-3 месяца)
1. Выделить core/common модуль
2. Вынести первую фичу в отдельный модуль
3. Настроить remote build cache
4. Написать ADR для архитектурных решений

### Долгосрочные (3-6 месяцев)
1. Полная модуляризация по фичам
2. Выделить design system модуль
3. Внедрить feature flags
4. Настроить метрики качества — [[engineering-metrics]]

---

## Связанные материалы
- [[android-modularization]] — модуляризация Android
- [[ios-modularization]] — модуляризация iOS
- [[architecture-overview]] — обзор архитектуры
- [[android-gradle-fundamentals]] — Gradle
- [[scaling-engineering-org]] — масштабирование организации
- [[team-structures]] — структуры команд
- [[technical-debt]] — технический долг
- [[refactoring-techniques]] — техники рефакторинга
