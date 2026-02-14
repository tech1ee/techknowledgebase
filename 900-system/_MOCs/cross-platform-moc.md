---
title: "Cross-Platform MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/cross-platform
  - type/moc
  - navigation
---
# Cross-Platform MOC

> Глубокое сравнение iOS и Android платформ по всем аспектам: от памяти и lifecycle до UI, сборки и дистрибуции.

---

## Рекомендуемый путь изучения

1. **Обзор и философия** — [[cross-platform-overview]] → [[cross-decision-guide]]
2. **Фундамент** — [[cross-memory-management]] → [[cross-lifecycle]] → [[cross-architecture]]
3. **UI** — [[cross-ui-imperative]] → [[cross-ui-declarative]] → [[cross-navigation]] → [[cross-state-management]] → [[cross-graphics-rendering]]
4. **Concurrency** — [[cross-concurrency-legacy]] → [[cross-concurrency-modern]]
5. **Данные и сеть** — [[cross-data-persistence]] → [[cross-networking]]
6. **Инфраструктура** — [[cross-build-systems]] → [[cross-dependency-injection]] → [[cross-testing]] → [[cross-performance-profiling]]
7. **Платформенные особенности** — [[cross-background-work]] → [[cross-permissions]] → [[cross-interop]]
8. **Релиз** — [[cross-code-signing]] → [[cross-distribution]]
9. **KMP интеграция** — [[cross-kmp-patterns]]

## Статьи по категориям

### Обзор и принятие решений
- [[cross-platform-overview]] — философия платформ: iOS (детерминизм и контроль) vs Android (гибкость и адаптивность)
- [[cross-decision-guide]] — руководство по выбору стека: Native vs KMP vs Flutter

### Memory и Lifecycle
- [[cross-memory-management]] — ARC (iOS) vs GC (Android): детерминированное vs отложенное освобождение памяти
- [[cross-lifecycle]] — UIViewController lifecycle vs Activity/Fragment lifecycle

### Архитектура
- [[cross-architecture]] — MVVM + Combine/async (iOS) vs MVVM + Flow/Coroutines (Android), Clean Architecture

### UI: Imperative
- [[cross-ui-imperative]] — UIKit (UIView, Auto Layout) vs Android Views (XML, ConstraintLayout)

### UI: Declarative
- [[cross-ui-declarative]] — SwiftUI vs Jetpack Compose: state-driven, recomposition, модификаторы
- [[cross-navigation]] — NavigationStack (iOS, стек) vs Navigation Component (Android, граф)
- [[cross-state-management]] — @State/@StateObject (SwiftUI) vs remember/mutableStateOf (Compose)

### Graphics и Rendering
- [[cross-graphics-rendering]] — Core Animation + Metal (iOS) vs RenderThread + Skia + Vulkan (Android)

### Concurrency
- [[cross-concurrency-legacy]] — GCD + DispatchQueue (iOS) vs Handler/Looper (Android)
- [[cross-concurrency-modern]] — Swift async/await + actors vs Kotlin Coroutines + Flow

### Данные и Сеть
- [[cross-data-persistence]] — Core Data/SwiftData (iOS) vs Room (Android), SQLDelight для KMP
- [[cross-networking]] — URLSession (iOS) vs OkHttp/Retrofit (Android), Ktor для KMP

### Инфраструктура и Качество
- [[cross-build-systems]] — Xcode Build System (GUI-first) vs Gradle (code-first, Kotlin DSL)
- [[cross-dependency-injection]] — Swinject (iOS) vs Hilt (Android), Koin для KMP
- [[cross-testing]] — XCTest (Xcode) vs JUnit + AndroidX Test
- [[cross-performance-profiling]] — Instruments (iOS) vs Android Studio Profiler

### Платформенные особенности
- [[cross-background-work]] — BackgroundTasks (iOS, без гарантий, ~30 сек) vs WorkManager (Android, гарантированное выполнение)
- [[cross-permissions]] — Privacy Manifest + Info.plist (iOS) vs Runtime Permissions + AndroidManifest (Android)
- [[cross-interop]] — Swift-ObjC (bridging headers) vs Kotlin-Java (полная бинарная совместимость)

### Релиз и Дистрибуция
- [[cross-code-signing]] — Provisioning Profiles + сертификаты Apple vs Keystore (самоподписанные)
- [[cross-distribution]] — App Store (ревью 24-48ч, $99/год) vs Play Store (1-3 дня, $25 единоразово)

### KMP Паттерны
- [[cross-kmp-patterns]] — expect/actual, interface + impl, SKIE для iOS-friendly API, Swift Export

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| ARC vs GC | Детерминированное (iOS) vs отложенное (Android) управление памятью | [[cross-memory-management]] |
| Lifecycle | iOS: разработчик контролирует; Android: система уведомляет | [[cross-lifecycle]] |
| SwiftUI vs Compose | Декларативные UI фреймворки с разной моделью recomposition | [[cross-ui-declarative]] |
| async/await vs Coroutines | Нативная конкурентность Swift vs библиотечная в Kotlin | [[cross-concurrency-modern]] |
| expect/actual | KMP механизм платформенных реализаций общего API | [[cross-kmp-patterns]] |
| NavigationStack vs NavHost | Stack-based (iOS) vs Graph-based (Android) навигация | [[cross-navigation]] |
| Core Data vs Room | ORM/Database с платформенной спецификой, SQLDelight как KMP альтернатива | [[cross-data-persistence]] |
| Xcode vs Gradle | GUI-first opaque сборка (iOS) vs code-first transparent (Android) | [[cross-build-systems]] |

## Связанные области

- [[android-moc]] — Android-специфичные темы: Jetpack, Compose, архитектура
- [[ios-moc]] — iOS-специфичные темы: SwiftUI, UIKit, Swift concurrency
- [[kmp-moc]] — Kotlin Multiplatform: общий код, expect/actual, targets
