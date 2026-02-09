# Android Dependency Injection: Overview & Navigation

---
type: overview
level: intermediate
topics: [android, kotlin, dependency-injection, navigation-hub]
related: [[dependency-injection-fundamentals]], [[android-architecture-patterns]]
version: "2025"
---

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
