---
title: "Решение: Какую базу данных выбрать"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Какую базу данных / хранилище выбрать

Дерево решений: Room vs SQLDelight vs CoreData vs SwiftData vs DataStore.

---

## Быстрый ответ

| Ситуация | Решение | Материал |
|----------|---------|----------|
| KMP shared-модуль | SQLDelight | [[kmp-sqldelight-database]] |
| Android + простые key-value | DataStore | [[android-datastore-guide]] |
| Android + сложные данные | Room | [[android-room-deep-dive]] |
| iOS + новый проект (iOS 17+) | SwiftData | [[ios-swiftdata]] |
| iOS + поддержка старых версий | Core Data | [[ios-core-data]] |
| Нужен SharedPreferences | DataStore (Proto или Preferences) | [[android-datastore-guide]] |

---

## Дерево решений

```
Какое хранилище использовать?
│
├── Кросс-платформа (KMP)?
│   ├── Да
│   │   ├── Реляционные данные → SQLDelight
│   │   ├── Key-value → Multiplatform Settings
│   │   └── Файловый кеш → okio / kotlinx-io
│   │
│   └── Нет (native)
│       ├── Android
│       │   ├── Key-value настройки → DataStore Preferences
│       │   ├── Typed settings → DataStore Proto
│       │   ├── Реляционные данные → Room
│       │   ├── Полнотекстовый поиск → Room + FTS
│       │   └── Файлы → Internal/External storage
│       │
│       └── iOS
│           ├── Key-value → UserDefaults
│           ├── Реляционные данные (iOS 17+) → SwiftData
│           ├── Реляционные данные (legacy) → Core Data
│           ├── Keychain → Security Framework
│           └── Файлы → FileManager
│
├── Объём данных?
│   ├── < 1 MB → Key-value (DataStore / UserDefaults)
│   ├── 1 MB - 100 MB → SQLite (Room / SQLDelight / Core Data)
│   └── > 100 MB → Нужна стратегия пагинации + очистки
│
└── Структура данных?
    ├── Плоские пары ключ-значение → DataStore / UserDefaults
    ├── Связанные таблицы → Room / SQLDelight / Core Data
    └── Документы / JSON → DataStore Proto / файлы
```

---

## Сравнительная таблица

| Критерий | Room | SQLDelight | DataStore | Core Data | SwiftData |
|----------|------|-----------|-----------|-----------|-----------|
| Платформа | Android | KMP | Android | iOS | iOS 17+ |
| Язык запросов | SQL | SQL | - | NSPredicate | SwiftData queries |
| Compile-time проверка SQL | + | + | n/a | - | + (Swift macros) |
| Reactive (Flow/Combine) | + | + | + | + | + |
| Миграции | Ручные/auto | Ручные | Авто | Ручные/auto | Авто |
| Кривая обучения | Средняя | Средняя | Низкая | Высокая | Низкая |
| Зрелость | Высокая | Высокая | Средняя | Очень высокая | Низкая |

---

## Детали по решениям

### Room — стандарт для Android
- SQLite-обёртка с compile-time проверкой SQL
- Интеграция с LiveData, Flow, Paging
- Автоматические миграции (с Room 2.4+)
- [[android-room-deep-dive]] — полное руководство
- [[android-room-migrations]] — стратегии миграций
- [[android-room-performance]] — оптимизация производительности

### SQLDelight — для KMP
- SQL-first: пишешь SQL, получаешь Kotlin-типы
- Compile-time проверка всех запросов
- Multiplatform: Android, iOS, Desktop, Web
- [[kmp-sqldelight-database]] — руководство по SQLDelight

### DataStore — замена SharedPreferences
- Preferences DataStore — key-value (как SharedPreferences, но лучше)
- Proto DataStore — typed данные через Protocol Buffers
- Coroutines + Flow API
- [[android-datastore-guide]] — полное руководство

### Core Data — классика iOS
- Object graph + persistence framework
- Мощный, но сложный API
- Отличная интеграция с UIKit и SwiftUI
- [[ios-core-data]] — руководство по Core Data

### SwiftData — будущее iOS
- Swift-native замена Core Data
- Декларативный API с макросами
- Требует iOS 17+
- [[ios-swiftdata]] — руководство по SwiftData

---

## Общие принципы
- [[android-data-persistence]] — обзор хранения данных в Android
- [[ios-data-persistence]] — обзор хранения данных в iOS
- [[cross-data-persistence]] — кросс-платформенное хранение
- [[databases-overview]] — обзор баз данных (серверная сторона)
- [[database-design-optimization]] — проектирование и оптимизация

---

## Связанные материалы
- [[android-room-deep-dive]] — Room
- [[kmp-sqldelight-database]] — SQLDelight
- [[android-datastore-guide]] — DataStore
- [[ios-core-data]] — Core Data
- [[ios-swiftdata]] — SwiftData
- [[mobile-databases-complete]] — мобильные БД
