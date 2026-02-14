---
title: "KMP: путь обучения"
created: 2026-02-10
modified: 2026-02-14
type: guide
tags:
  - topic/kotlin-multiplatform
  - type/guide
  - navigation
  - learning-path
---

# KMP: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

**Рекомендуемый темп:** 2-3 файла в день (~60-90 минут). Каждый 5-й день — повторение изученного.

**Общее время чтения:** ~1325 минут (~22 часа)

---

## Уровень 1: Основы (Beginner)
> Цель: Понять концепцию KMP, создать первый проект, освоить source sets и expect/actual
> Время: ~2 недели | Чтение: ~224 минут

- [ ] [[kmp-overview]] — обзор KMP: архитектура, экосистема, production readiness ⏱ 11m
- [ ] [[kmp-getting-started]] — первый KMP проект за 30 минут: IDE setup, KMP Wizard ⏱ 38m
- [ ] [[kmp-project-structure]] — анатомия KMP проекта: targets, source sets, Gradle ⏱ 50m
- [ ] [[kmp-source-sets]] — организация кода по платформам: commonMain, intermediate source sets ⏱ 52m
- [ ] [[kmp-expect-actual]] — механизм expect/actual для платформо-зависимого кода ⏱ 53m

> [!tip] Если используешь SwiftUI для iOS UI, можешь пропустить Compose MP iOS и focus на shared logic.

- [ ] [[compose-mp-overview]] — Compose Multiplatform: Shared UI через Skia rendering ⏱ 20m

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить платформенные интеграции, архитектуру, библиотеки и тестирование
> Время: ~6 недель | Чтение: ~876 минут
> Prerequisites: Level 1

### Платформы
- [ ] [[kmp-android-integration]] — Android как первоклассный target: Jetpack KMP (Room, DataStore, ViewModel) ⏱ 43m
- [ ] [[kmp-ios-deep-dive]] — iOS: Compose MP iOS, Swift Export, SKIE, XCFramework интеграция ⏱ 36m

> [!tip] Kotlin/Wasm — Beta. Пропусти если не планируешь web target.

- [ ] [[kmp-web-wasm]] — Kotlin/Wasm (Beta) и Compose Web: WasmGC, Canvas rendering ⏱ 34m

📝 День повторения

- [ ] [[kmp-desktop-jvm]] — Compose Desktop (Stable): нативные приложения через Skia + JVM ⏱ 35m

### Compose Multiplatform
- [ ] [[compose-mp-ios]] — Compose на iOS: Metal rendering, 120Hz, UIKit/SwiftUI interop ⏱ 39m
- [ ] [[compose-mp-desktop]] — Desktop приложения: Window management, MenuBar, Tray ⏱ 51m
- [ ] [[compose-mp-web]] — Web через Canvas/Wasm: Beta, deep linking, HTML interop ⏱ 46m

📝 День повторения

### Архитектура
- [ ] [[kmp-architecture-patterns]] — MVVM, MVI, Clean Architecture в KMP ⏱ 47m
- [ ] [[kmp-di-patterns]] — Dependency Injection: Koin, kotlin-inject, Manual DI ⏱ 38m
- [ ] [[kmp-navigation]] — Compose Navigation, Decompose, Voyager ⏱ 39m
- [ ] [[kmp-state-management]] — StateFlow как single source of truth, MVI, Redux ⏱ 41m

📝 День повторения

### Библиотеки
- [ ] [[kmp-ktor-networking]] — Ktor Client: HTTP/2, WebSockets, kotlinx.serialization ⏱ 49m
- [ ] [[kmp-sqldelight-database]] — SQLDelight: типобезопасные SQL API, multiplatform drivers ⏱ 47m
- [ ] [[kmp-kotlinx-libraries]] — kotlinx: serialization, datetime, coroutines, io ⏱ 38m
- [ ] [[kmp-third-party-libs]] — 3000+ KMP библиотек: Apollo, Coil, Realm, MOKO ⏱ 31m

📝 День повторения

### Тестирование
- [ ] [[kmp-testing-strategies]] — стратегия тестирования: commonTest, kotlin.test + Kotest ⏱ 24m
- [ ] [[kmp-unit-testing]] — unit тесты: kotlin.test, Kotest assertions, runTest, Turbine ⏱ 37m
- [ ] [[kmp-integration-testing]] — integration тесты: Ktor MockEngine, SQLDelight in-memory ⏱ 55m

📝 День повторения

### Build и Deploy
- [ ] [[kmp-ci-cd]] — CI/CD: GitHub Actions, macOS runners, кэширование, Fastlane ⏱ 26m
- [ ] [[kmp-publishing]] — публикация: Maven Central + SPM/CocoaPods, GPG signing ⏱ 23m
- [ ] [[kmp-gradle-deep-dive]] — Gradle оптимизация: caching, parallel, Convention Plugins ⏱ 27m

> [!tip] Секция миграции — читай только релевантный файл (с Flutter, RN или Native).

### Миграция
- [ ] [[kmp-migration-from-native]] — с Native Android+iOS: Strangler Fig pattern ⏱ 26m
- [ ] [[kmp-migration-from-flutter]] — с Flutter: полная перезапись Dart -> Kotlin ⏱ 23m
- [ ] [[kmp-migration-from-rn]] — с React Native: поэтапная интеграция или полная перезапись ⏱ 21m

📝 День повторения

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Глубоко понять interop, memory management, отладку и оптимизацию KMP
> Время: ~3 недели | Чтение: ~144 минуты
> Prerequisites: Level 2

- [ ] [[kmp-interop-deep-dive]] — ObjC bridge, Swift Export (experimental), cinterop, SKIE ⏱ 34m
- [ ] [[kmp-memory-management]] — Kotlin/Native tracing GC + Swift ARC, mixed retain cycles ⏱ 39m
- [ ] [[kmp-debugging]] — LLDB + xcode-kotlin plugin, crash reporting, KDoctor ⏱ 32m
- [ ] [[kmp-performance-optimization]] — build time (K2: до 94%), binary size, runtime hot paths ⏱ 39m

📝 День повторения

---

## Уровень 4: Экспертиза (Expert)
> Цель: Готовность к production: чеклисты, реальные кейсы, troubleshooting
> Время: ~2 недели | Чтение: ~81 минута
> Prerequisites: Level 3

> [!tip] Case studies и production checklist — читай когда готовишь реальный проект к launch.

- [ ] [[kmp-production-checklist]] — полный чеклист: архитектура, тесты, CI/CD, crash reporting ⏱ 21m
- [ ] [[kmp-case-studies]] — Netflix, McDonald's, Cash App: 60-80% shared code ⏱ 30m
- [ ] [[kmp-troubleshooting]] — типичные проблемы 2025-2026: Xcode 16 linker, AGP 9, ObjC bridge ⏱ 30m
