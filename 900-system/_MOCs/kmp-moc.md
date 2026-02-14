---
title: "KMP MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/kotlin-multiplatform
  - type/moc
  - navigation
---
# KMP MOC

> Kotlin Multiplatform: кросс-платформенная разработка для Android, iOS, Desktop и Web из единого Kotlin-кода.

**Путь обучения:** [[kmp-learning-path]]

---

## Рекомендуемый путь изучения

**Level 1 -- Fundamentals (1-2 недели):**
[[kmp-getting-started]] -> [[kmp-project-structure]] -> [[kmp-source-sets]] -> [[kmp-expect-actual]]

**Level 2 -- Platforms & UI (2-3 недели):**
[[kmp-android-integration]] -> [[kmp-ios-deep-dive]] -> [[compose-mp-overview]] -> [[compose-mp-ios]]

**Level 3 -- Architecture & Libraries (2-3 недели):**
[[kmp-architecture-patterns]] -> [[kmp-di-patterns]] -> [[kmp-state-management]] -> [[kmp-navigation]] -> [[kmp-ktor-networking]] -> [[kmp-sqldelight-database]]

**Level 4 -- Testing & CI/CD (1-2 недели):**
[[kmp-testing-strategies]] -> [[kmp-unit-testing]] -> [[kmp-integration-testing]] -> [[kmp-gradle-deep-dive]] -> [[kmp-ci-cd]]

**Level 5 -- Production (2-3 недели):**
[[kmp-performance-optimization]] -> [[kmp-memory-management]] -> [[kmp-debugging]] -> [[kmp-interop-deep-dive]] -> [[kmp-production-checklist]]

## Статьи по категориям

### Fundamentals
- [[kmp-getting-started]] — первый KMP проект за 30 минут: IDE setup, KMP Wizard и preflight checks
- [[kmp-project-structure]] — анатомия KMP проекта: targets, source sets, Gradle и default hierarchy template
- [[kmp-expect-actual]] — механизм expect/actual для платформо-зависимого кода: контракт в common, реализация per platform
- [[kmp-source-sets]] — организация кода по платформам: commonMain, intermediate source sets, dependsOn иерархия

### Platforms
- [[kmp-android-integration]] — Android как первоклассный target: Jetpack KMP (Room, DataStore, ViewModel, Paging)
- [[kmp-ios-deep-dive]] — iOS Tier 1: Compose MP iOS Stable, Swift Export, SKIE, XCFramework интеграция
- [[kmp-web-wasm]] — Kotlin/Wasm (Beta) и Compose Web: WasmGC, Canvas rendering, JS fallback
- [[kmp-desktop-jvm]] — Compose Desktop (Stable): нативные приложения для macOS/Windows/Linux через Skia + JVM

### Compose Multiplatform
- [[compose-mp-overview]] — Shared UI фреймворк: Skia rendering, iOS Stable, Web Beta, 95% shared UI code
- [[compose-mp-ios]] — Compose на iOS: Metal rendering, 120Hz ProMotion, UIKit/SwiftUI interop, VoiceOver
- [[compose-mp-desktop]] — Desktop приложения: Window management, MenuBar, Tray, Swing/AWT interop, jpackage
- [[compose-mp-web]] — Web через Canvas/Wasm: Beta, ~3x быстрее JS, deep linking, HTML interop

### Architecture
- [[kmp-architecture-patterns]] — MVVM, MVI, Clean Architecture в KMP: shared ViewModel, feature modules
- [[kmp-di-patterns]] — Dependency Injection: Koin (runtime DSL), kotlin-inject (compile-time), Manual DI
- [[kmp-navigation]] — Compose Navigation (official), Decompose (lifecycle-aware BLoC), Voyager (Compose-first)
- [[kmp-state-management]] — StateFlow как single source of truth, MVI для predictable state, iOS bridging через SKIE

### Libraries
- [[kmp-ktor-networking]] — Ktor Client: HTTP/2, WebSockets, kotlinx.serialization, MockEngine, platform engines
- [[kmp-sqldelight-database]] — SQLDelight 2.x: типобезопасные SQL API, multiplatform drivers, reactive Flow queries
- [[kmp-kotlinx-libraries]] — kotlinx ecosystem: serialization, datetime, coroutines, io (Buffer/Source/Sink)
- [[kmp-third-party-libs]] — 3000+ KMP библиотек: Apollo GraphQL, Coil, Realm, multiplatform-settings, MOKO

### Testing
- [[kmp-testing-strategies]] — стратегия тестирования: commonTest для всех платформ, kotlin.test + Kotest + Turbine
- [[kmp-unit-testing]] — unit тесты: kotlin.test, Kotest assertions (300+ matchers), runTest, Turbine для Flow
- [[kmp-integration-testing]] — integration тесты: Ktor MockEngine, SQLDelight in-memory drivers, fakes вместо mocks

### Build & Deploy
- [[kmp-gradle-deep-dive]] — Gradle оптимизация: caching, parallel, configuration-cache, Convention Plugins, Version Catalog
- [[kmp-ci-cd]] — CI/CD: GitHub Actions, macOS runners для iOS, кэширование ~/.konan, Fastlane, KMMBridge
- [[kmp-publishing]] — публикация библиотек: Maven Central + SPM/CocoaPods, GPG signing, KMMBridge для XCFramework

### Migration
- [[kmp-migration-from-native]] — с Native Android+iOS: поэтапно Model -> Data -> UseCase, Strangler Fig pattern
- [[kmp-migration-from-flutter]] — с Flutter: полная перезапись Dart -> Kotlin, нативный UI вместо единого widget tree
- [[kmp-migration-from-rn]] — с React Native: поэтапная интеграция через Kotlin/JS или полная перезапись JS -> Kotlin

### Advanced
- [[kmp-performance-optimization]] — оптимизация build time (K2: до 94%), binary size и runtime hot paths
- [[kmp-memory-management]] — Kotlin/Native tracing GC + Swift ARC: mixed retain cycles, autoreleasepool, мониторинг
- [[kmp-debugging]] — LLDB + xcode-kotlin plugin, crash reporting через CrashKiOS + Crashlytics, KDoctor
- [[kmp-interop-deep-dive]] — ObjC bridge, Swift Export (experimental), cinterop, SKIE для async/await и Flow

### Production
- [[kmp-production-checklist]] — полный чеклист: архитектура, тесты, CI/CD, crash reporting, app store submission
- [[kmp-case-studies]] — Netflix, McDonald's, Cash App, Quizlet, Philips: 60-80% shared code, 40-60% ускорение
- [[kmp-troubleshooting]] — типичные проблемы 2025-2026: Xcode 16 linker, AGP 9, CrashKiOS, ObjC bridge ограничения

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| Source Sets | Организация кода по платформам: commonMain, iosMain, androidMain | [[kmp-source-sets]] |
| expect/actual | Контракт в common коде, реализация для каждой платформы | [[kmp-expect-actual]] |
| Compose Multiplatform | Shared UI через Skia rendering на всех платформах | [[compose-mp-overview]] |
| SKIE | Swift-friendly API: Flow -> AsyncSequence, suspend -> async/await | [[kmp-ios-deep-dive]] |
| Kotlin/Wasm | Компиляция Kotlin в WebAssembly через WasmGC | [[kmp-web-wasm]] |
| Ktor Client | Мультиплатформенный HTTP-клиент с platform-specific engines | [[kmp-ktor-networking]] |
| SQLDelight | Type-safe SQL с compile-time verification и multiplatform drivers | [[kmp-sqldelight-database]] |
| KMMBridge | Автоматизация XCFramework -> SPM для iOS интеграции | [[kmp-publishing]] |

## Связанные области

- [[kotlin-moc]] — язык Kotlin: coroutines, Flow, serialization как фундамент KMP
- [[cs-fundamentals-moc]] — compilation pipeline, FFI, memory models как CS-основа KMP
- [[architecture-moc]] — архитектурные паттерны (Clean Architecture, MVVM, MVI) применяемые в KMP
