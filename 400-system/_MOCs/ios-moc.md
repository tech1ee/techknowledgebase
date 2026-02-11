---
title: "iOS MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/ios
  - type/moc
  - navigation
---
# iOS MOC

> Полная карта iOS-разработки: от Darwin/XNU до SwiftUI и production deployment

**Путь обучения:** [[ios-learning-path]]

---

## Рекомендуемый путь изучения

```
1. [[ios-overview]]                  — Карта раздела, общая картина платформы
         ↓
2. [[ios-architecture]]              — Darwin, XNU, 4 слоя системы
         ↓
3. [[ios-app-components]]            — UIApplication, делегаты, Scene-based lifecycle
         ↓
4. [[ios-viewcontroller-lifecycle]]  — UIViewController lifecycle: загрузка, появление, deinit
         ↓
5. [[ios-uikit-fundamentals]]       — UIView, Auto Layout, Responder Chain
         ↓
6. [[ios-swiftui]]                   — Декларативный UI, модификаторы, @State
         ↓
7. [[ios-state-management]]          — Property wrappers: @State, @Binding, @Observable
         ↓
8. [[ios-threading-fundamentals]]    — Main Thread, GCD, Quality of Service
         ↓
9. [[ios-async-await]]               — Swift Concurrency: async/await, Actors, TaskGroup
         ↓
10. [[ios-architecture-patterns]]    — MVC, MVVM, VIPER, TCA и Clean Architecture
         ↓
11. [[ios-data-persistence]]         — UserDefaults, FileManager, Keychain, iCloud KVS
         ↓
12. [[ios-networking]]               — URLSession, async/await, Codable
         ↓
13. [[ios-testing]]                  — XCTest: unit, UI, performance, snapshot тесты
         ↓
14. [[ios-xcode-fundamentals]]       — Проекты, Targets, Schemes, Build Settings
         ↓
15. [[ios-performance-profiling]]    — Instruments: Time Profiler, Memory Graph, MetricKit
```

---

## Статьи по категориям

### Платформа и основы
- [[ios-overview]] — карта раздела и точка входа в iOS-разработку
- [[ios-architecture]] — архитектура iOS: Darwin, XNU, 4 слоя от Core OS до Cocoa Touch
- [[ios-app-components]] — UIApplication, AppDelegate, SceneDelegate, scene-based lifecycle
- [[ios-viewcontroller-lifecycle]] — жизненный цикл UIViewController: loadView, viewDidLoad, appear/disappear
- [[ios-process-memory]] — ARC, reference counting, Jetsam kills, лимиты памяти по устройствам
- [[ios-market-trends-2026]] — рынок iOS в 2026: Swift 6, SwiftUI adoption, on-device AI

### SwiftUI
- [[ios-swiftui]] — декларативный UI фреймворк: View, модификаторы, Live Preview
- [[ios-swiftui-vs-uikit]] — сравнение подходов: когда SwiftUI, когда UIKit, гибридная стратегия
- [[ios-state-management]] — @State, @Binding, @StateObject, @Observable, single source of truth
- [[ios-custom-views]] — Custom Views: UIView subclassing, composиция, draw(_:), intrinsicContentSize

### UIKit
- [[ios-uikit-fundamentals]] — UIView, View Hierarchy, Auto Layout, координатные системы
- [[ios-navigation]] — UINavigationController, TabBarController, NavigationStack, Coordinator
- [[ios-touch-interaction]] — Responder Chain, hit testing, UIGestureRecognizer, SwiftUI gestures
- [[ios-accessibility]] — VoiceOver, Dynamic Type, контрасты, Reduce Motion, Switch Control
- [[ios-scroll-performance]] — UITableView/UICollectionView: cell reuse, prefetching, 60/120 FPS

### Concurrency
- [[ios-threading-fundamentals]] — Main Thread, GCD очереди, serial vs concurrent, QoS
- [[ios-gcd-deep-dive]] — Grand Central Dispatch: barriers, semaphores, groups, DispatchSource
- [[ios-async-await]] — Swift async/await: suspension points, Actors, TaskGroup, MainActor
- [[ios-async-evolution]] — эволюция: NSThread (2007) -> GCD (2009) -> async/await (2021) -> Swift 6
- [[ios-concurrency-mistakes]] — типичные ошибки GCD и Swift Concurrency: deadlocks, data races
- [[ios-combine]] — Combine framework: Publisher, Operators, Subscriber, backpressure

### Архитектура приложения
- [[ios-architecture-patterns]] — MVC, MVVM, VIPER, TCA, Clean Architecture: выбор и сравнение
- [[ios-architecture-evolution]] — от Massive ViewController (2008) к @Observable + TCA (2025)
- [[ios-viewmodel-patterns]] — ObservableObject, @Observable macro, Input-Output, protocol-based
- [[ios-dependency-injection]] — Constructor injection, Swinject, Needle, SwiftUI Environment
- [[ios-repository-pattern]] — Single Source of Truth, offline-first, кэширование
- [[ios-modularization]] — SPM-based модульная архитектура: feature/interface/core модули

### Данные и сеть
- [[ios-data-persistence]] — UserDefaults, FileManager, Keychain, iCloud KVS, File Protection
- [[ios-core-data]] — Core Data: объектный граф, NSManagedObjectContext, CloudKit синхронизация
- [[ios-swiftdata]] — SwiftData (iOS 17+): @Model macro, @Query, автоматическая миграция
- [[ios-networking]] — URLSession: конфигурации, async/await, Codable, фоновые загрузки

### Рендеринг и графика
- [[ios-view-rendering]] — Render Loop: Layout -> Display -> Commit, Render Server, off-screen rendering
- [[ios-graphics-fundamentals]] — Core Graphics, Core Animation, Metal: многоуровневый графический стек

### Build, CI/CD и дистрибуция
- [[ios-xcode-fundamentals]] — проекты, Targets, Schemes, Build Settings и Build Configurations
- [[ios-compilation-pipeline]] — от Swift до .app: AST -> SIL -> LLVM IR -> Machine Code
- [[ios-code-signing]] — сертификаты, provisioning profiles, entitlements
- [[ios-ci-cd]] — Xcode Cloud, Fastlane, GitHub Actions: автоматизация сборки и деплоя
- [[ios-app-distribution]] — TestFlight, App Store, Ad Hoc, Enterprise дистрибуция

### Performance и отладка
- [[ios-performance-profiling]] — Instruments: Time Profiler, Memory Graph, Core Animation, MetricKit
- [[ios-debugging]] — LLDB, breakpoints, view debugging, sanitizers, crash symbolication

### Безопасность и фоновая работа
- [[ios-permissions-security]] — Privacy Manifest, Info.plist, Keychain, App Transport Security
- [[ios-notifications]] — UNUserNotificationCenter, APNs, Live Activities, Dynamic Island
- [[ios-background-execution]] — beginBackgroundTask, BGTaskScheduler, Background Modes
- [[ios-swift-objc-interop]] — Bridging Header, @objc, Objective-C Runtime, миграция legacy кода

---

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| ARC (Automatic Reference Counting) | Компилятор автоматически вставляет retain/release; детерминированное освобождение памяти | [[ios-process-memory]] |
| Retain Cycle | Два объекта держат strong ссылки друг на друга; решение: weak/unowned | [[ios-process-memory]] |
| Responder Chain | Цепочка обработки событий от view через контроллеры до UIApplication | [[ios-touch-interaction]] |
| Render Loop | Три фазы (Layout, Display, Commit) синхронизированные с VSYNC дисплея | [[ios-view-rendering]] |
| @State / @Binding | Механизм владения и передачи состояния между SwiftUI View | [[ios-state-management]] |
| @Observable (iOS 17+) | Макро для автоматического отслеживания изменений без @Published | [[ios-viewmodel-patterns]] |
| Structured Concurrency | Task иерархия с автоматической отменой и propagation ошибок | [[ios-async-await]] |
| Actor Isolation | Защита данных от data races через изоляцию на уровне типа | [[ios-async-await]] |
| Code Signing | Цепочка доверия: сертификат + provisioning profile + entitlements | [[ios-code-signing]] |
| Jetsam | Системный демон, убивающий процессы при превышении лимита памяти | [[ios-process-memory]] |

---

## Связанные области

- [[android-moc]] — параллельное изучение Android для понимания различий платформ
- [[cross-platform-moc]] — Flutter, React Native, KMP: альтернативы нативной разработке
- [[kmp-moc]] — Kotlin Multiplatform: shared бизнес-логика с нативным UI на каждой платформе
