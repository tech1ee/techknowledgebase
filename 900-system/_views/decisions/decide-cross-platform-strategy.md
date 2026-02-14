---
title: "Решение: KMP vs Flutter vs React Native vs Native"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# KMP vs Flutter vs React Native vs Native

Дерево решений для выбора кросс-платформенной стратегии.

---

## Быстрый ответ

| Ситуация | Решение | Почему |
|----------|---------|--------|
| Нативный опыт критичен | Native | Полный контроль, лучший UX |
| Хочешь шарить бизнес-логику | KMP | Shared Kotlin, native UI |
| Один UI для всех платформ | Flutter | Один codebase, свой рендеринг |
| Есть web-команда (JS/TS) | React Native | Переиспользование навыков |
| Стартап, нужен MVP быстро | Flutter или RN | Скорость разработки |
| Enterprise, есть Android-команда | KMP | Инкрементальная миграция |
| Нужен Desktop + Mobile + Web | Compose Multiplatform | Единый UI через Compose |

---

## Дерево решений

```
Выбор кросс-платформенной стратегии
│
├── Сколько платформ?
│   ├── Только Android + iOS
│   │   ├── Критичен нативный UX? → Native или KMP (shared logic)
│   │   ├── Нужен единый UI? → Flutter
│   │   └── Есть JS-команда? → React Native
│   │
│   ├── Mobile + Web
│   │   ├── Flutter Web (ограничения)
│   │   ├── React Native + React
│   │   └── KMP + Compose Multiplatform (emerging)
│   │
│   └── Mobile + Desktop
│       └── Compose Multiplatform или Flutter
│
├── Команда?
│   ├── Kotlin/Android разработчики → KMP
│   ├── Dart-разработчики → Flutter
│   ├── JS/TS-разработчики → React Native
│   └── Смешанная → зависит от проекта
│
├── Существующий проект?
│   ├── Есть Android-приложение → KMP (инкрементально)
│   ├── Есть iOS-приложение → KMP shared module
│   └── Новый проект → любой вариант
│
└── Что шарить?
    ├── Только бизнес-логику → KMP
    ├── Бизнес-логику + UI → Flutter / Compose Multiplatform
    └── Всё включая нативные API → Native
```

---

## Сравнительная таблица

| Критерий | Native | KMP | Flutter | React Native |
|----------|--------|-----|---------|-------------|
| UI-качество | Лучшее | Нативное | Свой рендеринг | Нативные компоненты |
| Code sharing | 0% | 50-80% | 90-95% | 85-95% |
| Производительность | Лучшая | Нативная | Отличная | Хорошая |
| Зрелость экосистемы | Полная | Растущая | Зрелая | Зрелая |
| Доступ к нативным API | Полный | expect/actual | Platform channels | Native modules |
| Hot reload | Compose preview | Ограничен | Отличный | Отличный |
| Размер приложения | Минимальный | +1-3 MB | +5-10 MB | +5-8 MB |
| Рынок вакансий | Самый большой | Растущий | Большой | Большой |

---

## Подробные материалы

### Обзоры
- [[cross-platform-overview]] — полный обзор кросс-платформенных подходов
- [[cross-decision-guide]] — детальный гайд по выбору

### KMP (Kotlin Multiplatform)
- [[kmp-overview]] — обзор KMP
- [[kmp-getting-started]] — начало работы
- [[kmp-architecture-patterns]] — архитектурные паттерны
- [[compose-mp-overview]] — Compose Multiplatform

### Миграция
- С Flutter на KMP: [[kmp-migration-from-flutter]]
- С React Native на KMP: [[kmp-migration-from-rn]]
- С Native на KMP: [[kmp-migration-from-native]]

### Кросс-платформенная архитектура
- [[cross-architecture]] — архитектурные паттерны
- [[cross-lifecycle]] — жизненный цикл
- [[cross-state-management]] — управление состоянием
- [[cross-navigation]] — навигация
- [[cross-dependency-injection]] — DI
- [[cross-networking]] — сеть

---

## Стратегии миграции

### Native → KMP (рекомендуемый путь)
```
1. Выдели shared networking module
2. Перенеси модели данных в KMP
3. Добавь shared бизнес-логику
4. (Опционально) Compose Multiplatform для UI
```

### Оценка рисков

| Риск | Native | KMP | Flutter | RN |
|------|--------|-----|---------|-----|
| Vendor lock-in | Low | Low | Medium | Medium |
| Прекращение поддержки | Very Low | Low | Low | Medium |
| Найм разработчиков | Easy | Medium | Easy | Easy |
| Сложные нативные фичи | Easy | Medium | Hard | Hard |

---

## Связанные материалы
- [[cross-platform-overview]] — обзор кросс-платформы
- [[cross-decision-guide]] — гайд по выбору
- [[kmp-overview]] — KMP обзор
- [[compose-mp-overview]] — Compose Multiplatform
- [[kmp-migration-from-flutter]] — миграция с Flutter
- [[kmp-migration-from-rn]] — миграция с React Native
- [[kmp-migration-from-native]] — миграция с Native
