---
title: "KMP: путь обучения"
created: 2026-02-10
modified: 2026-02-10
type: guide
tags:
  - topic/kotlin-multiplatform
  - type/guide
  - navigation
---

# KMP: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

---

## Уровень 1: Основы (Beginner)
> Цель: Понять концепцию KMP, создать первый проект, освоить source sets и expect/actual
> Время: ~2 недели

1. [[kmp-overview]] — обзор KMP: архитектура, экосистема, production readiness
2. [[kmp-getting-started]] — первый KMP проект за 30 минут: IDE setup, KMP Wizard
3. [[kmp-project-structure]] — анатомия KMP проекта: targets, source sets, Gradle
4. [[kmp-source-sets]] — организация кода по платформам: commonMain, intermediate source sets
5. [[kmp-expect-actual]] — механизм expect/actual для платформо-зависимого кода
6. [[compose-mp-overview]] — Compose Multiplatform: Shared UI через Skia rendering

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить платформенные интеграции, архитектуру, библиотеки и тестирование
> Время: ~6 недель
> Prerequisites: Level 1

### Платформы
7. [[kmp-android-integration]] — Android как первоклассный target: Jetpack KMP (Room, DataStore, ViewModel)
8. [[kmp-ios-deep-dive]] — iOS: Compose MP iOS, Swift Export, SKIE, XCFramework интеграция
9. [[kmp-web-wasm]] — Kotlin/Wasm (Beta) и Compose Web: WasmGC, Canvas rendering
10. [[kmp-desktop-jvm]] — Compose Desktop (Stable): нативные приложения через Skia + JVM

### Compose Multiplatform
11. [[compose-mp-ios]] — Compose на iOS: Metal rendering, 120Hz, UIKit/SwiftUI interop
12. [[compose-mp-desktop]] — Desktop приложения: Window management, MenuBar, Tray
13. [[compose-mp-web]] — Web через Canvas/Wasm: Beta, deep linking, HTML interop

### Архитектура
14. [[kmp-architecture-patterns]] — MVVM, MVI, Clean Architecture в KMP
15. [[kmp-di-patterns]] — Dependency Injection: Koin, kotlin-inject, Manual DI
16. [[kmp-navigation]] — Compose Navigation, Decompose, Voyager
17. [[kmp-state-management]] — StateFlow как single source of truth, MVI, Redux

### Библиотеки
18. [[kmp-ktor-networking]] — Ktor Client: HTTP/2, WebSockets, kotlinx.serialization
19. [[kmp-sqldelight-database]] — SQLDelight: типобезопасные SQL API, multiplatform drivers
20. [[kmp-kotlinx-libraries]] — kotlinx: serialization, datetime, coroutines, io
21. [[kmp-third-party-libs]] — 3000+ KMP библиотек: Apollo, Coil, Realm, MOKO

### Тестирование
22. [[kmp-testing-strategies]] — стратегия тестирования: commonTest, kotlin.test + Kotest
23. [[kmp-unit-testing]] — unit тесты: kotlin.test, Kotest assertions, runTest, Turbine
24. [[kmp-integration-testing]] — integration тесты: Ktor MockEngine, SQLDelight in-memory

### Build и Deploy
25. [[kmp-ci-cd]] — CI/CD: GitHub Actions, macOS runners, кэширование, Fastlane
26. [[kmp-publishing]] — публикация: Maven Central + SPM/CocoaPods, GPG signing
27. [[kmp-gradle-deep-dive]] — Gradle оптимизация: caching, parallel, Convention Plugins

### Миграция
28. [[kmp-migration-from-native]] — с Native Android+iOS: Strangler Fig pattern
29. [[kmp-migration-from-flutter]] — с Flutter: полная перезапись Dart -> Kotlin
30. [[kmp-migration-from-rn]] — с React Native: поэтапная интеграция или полная перезапись

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Глубоко понять interop, memory management, отладку и оптимизацию KMP
> Время: ~3 недели
> Prerequisites: Level 2

31. [[kmp-interop-deep-dive]] — ObjC bridge, Swift Export (experimental), cinterop, SKIE
32. [[kmp-memory-management]] — Kotlin/Native tracing GC + Swift ARC, mixed retain cycles
33. [[kmp-debugging]] — LLDB + xcode-kotlin plugin, crash reporting, KDoctor
34. [[kmp-performance-optimization]] — build time (K2: до 94%), binary size, runtime hot paths

---

## Уровень 4: Экспертиза (Expert)
> Цель: Готовность к production: чеклисты, реальные кейсы, troubleshooting
> Время: ~2 недели
> Prerequisites: Level 3

35. [[kmp-production-checklist]] — полный чеклист: архитектура, тесты, CI/CD, crash reporting
36. [[kmp-case-studies]] — Netflix, McDonald's, Cash App: 60-80% shared code
37. [[kmp-troubleshooting]] — типичные проблемы 2025-2026: Xcode 16 linker, AGP 9, ObjC bridge
