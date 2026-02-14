---
title: "Решение: Какой DI-фреймворк выбрать"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
---

# Какой DI-фреймворк выбрать

Дерево решений для выбора фреймворка Dependency Injection.

---

## Быстрый ответ

| Ситуация | Фреймворк | Материал |
|----------|-----------|----------|
| Android + Google ecosystem | **Hilt** | [[android-hilt-deep-dive]] |
| KMP + compile-time safety | **kotlin-inject** | [[android-kotlin-inject-deep-dive]] |
| KMP + простота | **Koin** | [[android-koin-deep-dive]] |
| Максимальный контроль | **Dagger** | [[android-dagger-deep-dive]] |
| SDK / изолированный модуль | **Kodein** | [[android-kodein-deep-dive]] |
| Cutting edge (Slack) | **Metro** | [[android-metro-deep-dive]] |
| Без фреймворка | Manual DI | [[android-manual-di-alternatives]] |

---

## Дерево решений

```
Нужен DI для мобильного проекта?
│
├── KMP (мультиплатформа)?
│   ├── Да
│   │   ├── Нужна compile-time проверка?
│   │   │   ├── Да → kotlin-inject
│   │   │   └── Нет → Koin
│   │   └── SDK/библиотека?
│   │       └── Да → Kodein
│   │
│   └── Нет (только Android)
│       ├── Google ecosystem / новый проект?
│       │   └── Да → Hilt
│       ├── Legacy-проект на Dagger?
│       │   └── Мигрировать на Hilt постепенно
│       ├── Нужен максимальный контроль?
│       │   └── Да → Dagger
│       ├── Маленький проект?
│       │   └── Manual DI (без фреймворка)
│       └── Хочешь попробовать новое?
│           └── Metro
```

---

## Сравнительная таблица

| Критерий | Hilt | Dagger | Koin | kotlin-inject | Kodein | Metro |
|----------|------|--------|------|---------------|--------|-------|
| Compile-time safety | + | + | - | + | - | + |
| KMP support | - | - | + | + | + | - |
| Кривая обучения | Средняя | Высокая | Низкая | Средняя | Низкая | Средняя |
| Производительность | Высокая | Высокая | Средняя | Высокая | Средняя | Высокая |
| Boilerplate | Средний | Высокий | Низкий | Низкий | Низкий | Низкий |
| Google support | Да | Да | Нет | Нет | Нет | Нет |
| Зрелость | Высокая | Высокая | Высокая | Средняя | Средняя | Низкая |

---

## Детали по фреймворкам

### Hilt — стандарт для Android
- Обёртка над Dagger с Android-специфичными фичами
- Интеграция с ViewModel, WorkManager, Navigation
- Рекомендуется Google для новых Android-проектов
- [[android-hilt-deep-dive]]

### Dagger — мощь и контроль
- Compile-time генерация кода, максимальная производительность
- Сложный, но даёт полный контроль
- Подходит для больших проектов с нестандартными требованиями
- [[android-dagger-deep-dive]]

### Koin — простота
- Service Locator паттерн (не настоящий DI)
- Runtime-проверки, но очень простой API
- Поддержка KMP
- [[android-koin-deep-dive]]

### kotlin-inject — KMP + compile-time
- Аналог Dagger для Kotlin Multiplatform
- KSP-based, compile-time проверки
- Набирает популярность в KMP-проектах
- [[android-kotlin-inject-deep-dive]]

### Kodein — для библиотек
- Хорошо работает в изолированных модулях и SDK
- Поддержка KMP
- Не навязывает структуру проекта
- [[android-kodein-deep-dive]]

### Metro — новый подход (Slack)
- Разработан в Slack, основан на идеях Anvil + Dagger
- KSP-based, минимум boilerplate
- Экспериментальный, но перспективный
- [[android-metro-deep-dive]]

---

## Теоретическая база
- [[android-dependency-injection]] — обзор DI в Android
- [[dependency-injection-fundamentals]] — фундаментальные принципы DI
- [[android-manual-di-alternatives]] — DI без фреймворков

---

## Связанные материалы
- [[android-architecture-patterns]] — архитектурные паттерны
- [[kmp-di-patterns]] — DI-паттерны в KMP
- [[cross-dependency-injection]] — DI в кросс-платформе
