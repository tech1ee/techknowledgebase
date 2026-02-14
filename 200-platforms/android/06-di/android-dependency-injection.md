---
title: "Dependency Injection в Android: обзор и навигация"
created: 2026-02-09
modified: 2026-02-13
type: overview
status: published
tags:
  - topic/android
  - topic/kotlin
  - topic/dependency-injection
  - type/overview
  - level/intermediate
related:
  - "[[dependency-injection-fundamentals]]"
  - "[[android-architecture-patterns]]"
reading_time: 10
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Android Dependency Injection: Overview & Navigation

## TL;DR

Обзор всех DI решений для Android и Kotlin Multiplatform. Этот материал — **навигационный хаб** со ссылками на deep-dive материалы по каждому фреймворку.

---

## Экосистема DI: Карта решений

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANDROID/KMP DI ECOSYSTEM 2025                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│                     ┌─────────────────────┐                    │
│                     │  DI Fundamentals    │                    │
│                     │  (общая теория)     │                    │
│                     └──────────┬──────────┘                    │
│                                │                                │
│         ┌──────────────────────┼──────────────────────┐        │
│         │                      │                      │        │
│         ▼                      ▼                      ▼        │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐    │
│  │  COMPILE    │      │   RUNTIME   │      │   MANUAL    │    │
│  │    TIME     │      │             │      │             │    │
│  └──────┬──────┘      └──────┬──────┘      └─────────────┘    │
│         │                    │                                  │
│    ┌────┴────┐          ┌────┴────┐                            │
│    │         │          │         │                            │
│    ▼         ▼          ▼         ▼                            │
│ ┌──────┐ ┌──────┐   ┌──────┐ ┌──────┐                         │
│ │Dagger│ │Metro │   │ Koin │ │Kodein│                         │
│ │ Hilt │ │k-inj │   │      │ │      │                         │
│ └──────┘ └──────┘   └──────┘ └──────┘                         │
│                                                                 │
│  LEGEND:                                                        │
│  Dagger/Hilt — Android-only, Google recommended                │
│  Metro/kotlin-inject — KMP, compile-time                       │
│  Koin/Kodein — KMP, runtime                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Deep-Dive материалы

### Теория DI

| Материал | Описание |
|----------|----------|
| **[[dependency-injection-fundamentals]]** | DIP, IoC, типы DI, история, мифы |

### Compile-Time DI

| Материал | Платформа | Описание |
|----------|-----------|----------|
| **[[android-dagger-deep-dive]]** | JVM/Android | Dagger 2 — основа Hilt, annotation processing, KSP |
| **[[android-hilt-deep-dive]]** | Android | Google-рекомендованный, Jetpack интеграция |
| **[[android-kotlin-inject-deep-dive]]** | KMP | Compile-time DI для Multiplatform |
| **[[android-metro-deep-dive]]** | KMP | Новейший (2025), compiler plugin, Cash App |

### Runtime DI

| Материал | Платформа | Описание |
|----------|-----------|----------|
| **[[android-koin-deep-dive]]** | KMP | Популярный, Kotlin DSL, простой |
| **[[android-kodein-deep-dive]]** | KMP | Множественные контейнеры, SDK-friendly |

### Другие решения

| Материал | Описание |
|----------|----------|
| **[[android-manual-di-alternatives]]** | Manual DI, Anvil, Toothpick |

---

## Quick Comparison

| Framework | Type | KMP | Compile-time | Рекомендация |
|-----------|------|-----|--------------|--------------|
| **Hilt** | Framework | ❌ | ✅ | Android-only проекты |
| **Dagger 2** | Framework | ❌ | ✅ | Legacy, понимание Hilt |
| **Metro** | Framework | ✅ | ✅ | KMP, новые проекты |
| **kotlin-inject** | Framework | ✅ | ✅ | KMP, Dagger-like API |
| **Koin** | Framework | ✅ | ❌ | KMP, простота |
| **Kodein** | Framework | ✅ | ❌ | SDK разработка |
| **Manual DI** | Pattern | ✅ | ❌ | Простые apps |

---

## Decision Tree: Какой выбрать?

```
┌─────────────────────────────────────────────────────────────┐
│                   ВЫБОР DI РЕШЕНИЯ                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Простое приложение (<50 классов)?                         │
│        │                                                    │
│       YES ──▶ Manual DI / Koin                             │
│        │                                                    │
│       NO                                                    │
│        │                                                    │
│        ▼                                                    │
│  Kotlin Multiplatform?                                      │
│        │                                                    │
│       YES ──▶ Compile-time важен?                          │
│        │            │                                       │
│        │           YES ──▶ Metro (2025) / kotlin-inject    │
│        │            │                                       │
│        │           NO ──▶ Koin (популярнее) / Kodein       │
│        │                                                    │
│       NO                                                    │
│        │                                                    │
│        ▼                                                    │
│  Android-only?                                              │
│        │                                                    │
│       YES ──▶ Hilt (Google рекомендация)                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Рекомендации 2025

### Для новых проектов

| Сценарий | Рекомендация | Deep-dive |
|----------|--------------|-----------|
| **Android-only** | Hilt | [[android-hilt-deep-dive]] |
| **KMP + compile-time** | Metro | [[android-metro-deep-dive]] |
| **KMP + простота** | Koin 4.0 | [[android-koin-deep-dive]] |
| **Обучение DI** | Manual DI → Hilt | [[android-manual-di-alternatives]] |

### Миграция

| С чего | На что | Причина |
|--------|--------|---------|
| Dagger 2 | Hilt | Меньше boilerplate |
| Anvil | Metro | Anvil в maintenance mode |
| KAPT | KSP | 2x быстрее builds |

---

## История DI в Android

```
2012    Dagger 1 (Square)
        └── Первый compile-time DI для Android

2015    Dagger 2 (Google)
        └── Без reflection, annotation processing

2017    Koin
        └── Runtime DI, Kotlin DSL

2020    Hilt (Google)
        └── Dagger + Android Jetpack

2023    kotlin-inject 0.6
        └── Compile-time KMP DI

2024    Koin 4.0
        └── Performance improvements

2025    Metro (Zac Sweers)
        └── Compiler plugin, объединяет лучшее

2025    Anvil → Maintenance mode
        └── Рекомендация: мигрировать на Metro
```

---

## Benchmark 2024-2025

Данные из ProAndroidDev benchmark (Now In Android app):

| Метрика | Hilt 2.52 | Koin 4.0 |
|---------|-----------|----------|
| ViewModel creation | ~comparable | ~comparable |
| App startup | Быстрее (AOT) | Медленнее (graph build) |
| Build time | Медленнее (codegen) | Быстрее |

**Вывод:** Для real-world приложений разница в производительности незначительна. Выбирайте по другим критериям.

---

## Ключевые концепции

Все DI решения оперируют общими концепциями:

| Концепция | Hilt | Koin | Metro |
|-----------|------|------|-------|
| **Container** | Component | KoinApplication | DependencyGraph |
| **Module** | @Module | module { } | @Provides |
| **Singleton** | @Singleton | single { } | @Singleton |
| **Factory** | @Provides | factory { } | @Provides |
| **Scope** | @ActivityScoped | scope { } | @Scope |
| **Inject** | @Inject | inject() | @Inject |

Подробнее: [[dependency-injection-fundamentals]]

---

## Источники

### Официальные
- [Android Developers - DI Guide](https://developer.android.com/training/dependency-injection)
- [Hilt Documentation](https://developer.android.com/training/dependency-injection/hilt-android)
- [Koin Documentation](https://insert-koin.io/)

### Benchmarks
- [ProAndroidDev Benchmark 2024](https://proandroiddev.com/benchmarking-koin-vs-dagger-hilt-in-modern-android-development-2024-ff7bb40470df)

---

## Связанные материалы

### Теория
- [[dependency-injection-fundamentals]] — DIP, IoC, типы DI

### Compile-Time
- [[android-dagger-deep-dive]] — Dagger 2
- [[android-hilt-deep-dive]] — Hilt
- [[android-kotlin-inject-deep-dive]] — kotlin-inject
- [[android-metro-deep-dive]] — Metro

### Runtime
- [[android-koin-deep-dive]] — Koin
- [[android-kodein-deep-dive]] — Kodein

### Другое
- [[android-manual-di-alternatives]] — Manual DI, Anvil, Toothpick

---

## Связь с другими темами

### [[dependency-injection-fundamentals]]

Фундаментальные концепции DI (Dependency Inversion Principle, Inversion of Control, Service Locator vs DI Container) — теоретическая основа для всех фреймворков, описанных в этом обзоре. Без понимания DIP невозможно осознанно выбирать между compile-time и runtime DI, между Hilt и Koin. Знание типов injection (constructor, field, method) и их trade-offs объясняет, почему Hilt использует @Inject constructor, а Koin — DSL factory.

### [[android-architecture-patterns]]

DI — ключевой enabler для архитектурных паттернов в Android (MVVM, MVI, Clean Architecture). Без DI контейнера ViewModel'и получают жёсткие зависимости от Repository, Repository — от DataSource, и тестирование становится невозможным. Hilt интегрируется с Android Jetpack (ViewModel Injection, WorkManager), а архитектурные паттерны определяют структуру DI-графа: какие scope нужны, как разделить модули, где проводить границы между слоями.

---

## Проверь себя

> [!question]- Почему Dependency Injection предпочтительнее Service Locator в Android?
> DI: зависимости передаются извне (конструктор), явные, проверяются на этапе компиляции. Service Locator: зависимости запрашиваются изнутри, скрытые, ошибки только в runtime. DI упрощает тестирование (передать mock через конструктор), делает зависимости явными и позволяет IDE показать что нужно классу.

> [!question]- Сценарий: в проекте 50 классов с manual DI через конструкторы. Код раздувается. Когда переходить на DI-фреймворк?
> Признаки необходимости DI-фреймворка: 1) Граф зависимостей > 30 классов. 2) Scoping нужен (Activity scope, Fragment scope). 3) Многомодульный проект (manual DI через модули сложнее). 4) Тестирование затруднено из-за сложного графа. Hilt -- для большинства Android-проектов. Koin -- для простых проектов или KMP.

> [!question]- Почему constructor injection лучше field injection?
> Constructor injection: 1) Зависимости explicit (видны в сигнатуре). 2) Объект невозможно создать без зависимостей (compile-time safety). 3) Объект immutable после создания (val). Field injection (lateinit var): зависимости скрыты, возможен доступ до инициализации (UninitializedPropertyAccessException), сложнее тестировать.


---

## Ключевые карточки

Что такое Dependency Injection?
?
Паттерн: объект получает зависимости извне, а не создает сам. Три формы: constructor injection (через конструктор, предпочтительная), field injection (через свойства), method injection (через метод). Снижает coupling и упрощает тестирование.

Какие DI фреймворки есть для Android?
?
Hilt (Google, поверх Dagger, compile-time), Dagger 2 (Google, compile-time, complex), Koin (runtime, простой DSL, KMP), kotlin-inject (compile-time, KMP), Kodein (runtime, KMP), Metro (JetBrains, compile-time, KMP). Для Android: Hilt. Для KMP: Koin или kotlin-inject.

Чем compile-time DI отличается от runtime DI?
?
Compile-time (Dagger/Hilt): граф проверяется при компиляции, ошибки видны сразу, code generation, быстрее в runtime. Runtime (Koin): граф строится при запуске, ошибки только в runtime, рефлексия, проще API. Trade-off: безопасность vs простота.

Что такое Scope в DI?
?
Lifecycle зависимости: Singleton (одна instance на приложение), ActivityScoped (одна на Activity), ViewModelScoped (одна на ViewModel), FragmentScoped. Scope определяет когда создается и уничтожается объект.

Что такое Module в DI?
?
Класс/функция, описывающий КАК создавать зависимости. Содержит bindings: provides (создание), binds (interface -> implementation). В Hilt: @Module + @InstallIn(scope). В Koin: module { single { }, factory { } }.

Зачем нужен Qualifier?
?
Различает несколько реализаций одного типа. Пример: @Named('io') Dispatcher и @Named('main') Dispatcher. Без qualifier DI не знает какую реализацию инжектить. В Hilt: @Qualifier annotation. В Koin: named('io').


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-hilt-deep-dive]] | Hilt -- рекомендуемый DI для Android |
| Углубиться | [[android-dagger-deep-dive]] | Dagger 2 -- основа Hilt |
| Смежная тема | [[ios-dependency-injection]] | DI в iOS: Property Wrappers и Swinject |
| Обзор | [[android-overview]] | Вернуться к карте раздела |

