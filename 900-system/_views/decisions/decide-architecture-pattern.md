---
title: "Решение: MVVM vs MVI vs Clean vs TCA"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# MVVM vs MVI vs Clean Architecture vs TCA

Дерево решений для выбора архитектурного паттерна мобильного приложения.

---

## Быстрый ответ

| Ситуация | Паттерн | Почему |
|----------|---------|--------|
| Простое приложение (< 20 экранов) | MVVM | Минимум boilerplate |
| Сложное состояние, много side effects | MVI | Предсказуемый state flow |
| Большая команда, долгий проект | Clean Architecture | Чёткие границы, тестируемость |
| iOS + SwiftUI | TCA | Нативный для Swift-экосистемы |
| KMP shared-модуль | MVI + Clean | Хорошо ложится на KMP |
| Legacy-проект | Текущий + постепенная миграция | Не переписывать всё сразу |

---

## Дерево решений

```
Какой архитектурный паттерн?
│
├── Платформа?
│   ├── Android
│   │   ├── Маленький проект? → MVVM
│   │   ├── Сложный state? → MVI
│   │   └── Большая команда? → Clean Architecture + MVVM/MVI
│   │
│   ├── iOS
│   │   ├── SwiftUI + сложный state? → TCA
│   │   ├── UIKit legacy? → MVVM + Coordinator
│   │   └── Новый проект SwiftUI? → MVVM или TCA
│   │
│   └── KMP
│       └── MVI + Clean Architecture (shared domain)
│
├── Размер команды?
│   ├── 1-3 разработчика → MVVM (проще)
│   ├── 4-10 разработчиков → Clean Architecture
│   └── 10+ → Clean Architecture + модуляризация
│
└── Состояние приложения?
    ├── Простое (формы, списки) → MVVM
    ├── Сложное (real-time, offline) → MVI
    └── Очень сложное (множество source of truth) → MVI + Event Sourcing
```

---

## Сравнение паттернов

### MVVM (Model-View-ViewModel)
```
View ←→ ViewModel → Model
```
- **Плюсы:** простота, привычность, мало boilerplate
- **Минусы:** ViewModel может разрастись, нечёткие границы
- **Подходит:** простые и средние приложения
- **Android:** [[android-architecture-patterns]]
- **iOS:** [[ios-architecture-patterns]]

### MVI (Model-View-Intent)
```
View → Intent → Reducer → State → View
```
- **Плюсы:** предсказуемость, single source of truth, легко дебажить
- **Минусы:** больше boilerplate, кривая обучения
- **Подходит:** сложное состояние, real-time данные
- **Android:** [[android-architecture-patterns]]
- **KMP:** [[kmp-state-management]]

### Clean Architecture
```
UI → Presentation → Domain ← Data
```
- **Плюсы:** независимость слоёв, тестируемость, масштабируемость
- **Минусы:** много файлов, over-engineering для маленьких проектов
- **Подходит:** большие проекты, большие команды
- **Android:** [[android-architecture-patterns]]
- **KMP:** [[kmp-architecture-patterns]]

### TCA (The Composable Architecture)
```
View → Action → Reducer → State + Effect
```
- **Плюсы:** composability, полная тестируемость, Swift-native
- **Минусы:** только Swift/SwiftUI, кривая обучения
- **Подходит:** iOS-проекты на SwiftUI
- **iOS:** [[ios-architecture-patterns]]

---

## Эволюция архитектуры

### Android
```
God Activity → MVC → MVP → MVVM → MVI → Compose + MVI
```
- [[android-architecture-evolution]] — полная история эволюции

### iOS
```
MVC → MVVM + Coordinator → VIPER → TCA → SwiftUI + TCA
```
- [[ios-architecture-evolution]] — полная история эволюции

---

## Комбинирование паттернов

В реальных проектах паттерны часто комбинируются:

| Комбинация | Когда |
|------------|-------|
| Clean + MVVM | Стандарт для Android |
| Clean + MVI | Сложные Android-проекты |
| MVVM + Coordinator | iOS с UIKit |
| TCA + Clean Domain | Большие iOS-проекты |
| MVI + Clean + KMP | Кросс-платформенные проекты |

---

## Антипаттерны

1. **Dogmatic Architecture** — следовать паттерну буквально без учёта контекста
2. **Layer Lasagna** — бессмысленные прослойки ради "чистой архитектуры"
3. **ViewModel God Object** — всё в одном ViewModel
4. **Premature Abstraction** — абстракции ради абстракций

---

## Связанные материалы
- [[android-architecture-patterns]] — Android-архитектура
- [[ios-architecture-patterns]] — iOS-архитектура
- [[android-architecture-evolution]] — эволюция Android-архитектуры
- [[ios-architecture-evolution]] — эволюция iOS-архитектуры
- [[kmp-architecture-patterns]] — KMP-архитектура
- [[design-patterns]] — паттерны проектирования
- [[clean-code-solid]] — принципы SOLID
