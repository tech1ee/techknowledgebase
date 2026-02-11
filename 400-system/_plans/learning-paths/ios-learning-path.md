---
title: "iOS: путь обучения"
created: 2026-02-10
modified: 2026-02-10
type: guide
tags:
  - topic/ios
  - type/guide
  - navigation
---

# iOS: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

---

## Уровень 1: Основы (Beginner)
> Цель: Понять архитектуру iOS, освоить Xcode, базовые UI-фреймворки и жизненный цикл
> Время: ~3 недели

1. [[ios-overview]] — карта раздела и точка входа в iOS-разработку
2. [[ios-market-trends-2026]] — рынок iOS в 2026: Swift 6, SwiftUI adoption, on-device AI
3. [[ios-xcode-fundamentals]] — проекты, Targets, Schemes, Build Settings
4. [[ios-uikit-fundamentals]] — UIView, Auto Layout, Responder Chain, координатные системы
5. [[ios-app-components]] — UIApplication, AppDelegate, SceneDelegate, scene-based lifecycle

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить SwiftUI/UIKit, навигацию, архитектуру, работу с данными и сетью, тестирование
> Время: ~6 недель
> Prerequisites: Level 1

### Lifecycle
6. [[ios-viewcontroller-lifecycle]] — жизненный цикл UIViewController: loadView, viewDidLoad, appear/disappear

### UI: SwiftUI и UIKit
7. [[ios-swiftui]] — декларативный UI: View, модификаторы, Live Preview
8. [[ios-swiftui-vs-uikit]] — сравнение подходов: когда SwiftUI, когда UIKit
9. [[ios-state-management]] — @State, @Binding, @StateObject, @Observable
10. [[ios-custom-views]] — Custom Views: UIView subclassing, draw(_:), intrinsicContentSize
11. [[ios-navigation]] — UINavigationController, TabBarController, NavigationStack, Coordinator
12. [[ios-accessibility]] — VoiceOver, Dynamic Type, контрасты, Reduce Motion
13. [[ios-scroll-performance]] — UITableView/UICollectionView: cell reuse, prefetching, 60/120 FPS

### Архитектура
14. [[ios-architecture-patterns]] — MVC, MVVM, VIPER, TCA и Clean Architecture
15. [[ios-architecture-evolution]] — от Massive ViewController к @Observable + TCA
16. [[ios-viewmodel-patterns]] — ObservableObject, @Observable macro, Input-Output
17. [[ios-dependency-injection]] — Constructor injection, Swinject, Environment
18. [[ios-repository-pattern]] — Single Source of Truth, offline-first, кэширование

### Данные и сеть
19. [[ios-data-persistence]] — UserDefaults, FileManager, Keychain, iCloud KVS
20. [[ios-swiftdata]] — SwiftData (iOS 17+): @Model macro, @Query
21. [[ios-networking]] — URLSession: async/await, Codable, фоновые загрузки
22. [[ios-notifications]] — UNUserNotificationCenter, APNs, Live Activities

### Concurrency
23. [[ios-threading-fundamentals]] — Main Thread, GCD очереди, serial vs concurrent, QoS
24. [[ios-async-evolution]] — эволюция: NSThread -> GCD -> async/await -> Swift 6

### Build и безопасность
25. [[ios-compilation-pipeline]] — от Swift до .app: AST -> SIL -> LLVM IR -> Machine Code
26. [[ios-code-signing]] — сертификаты, provisioning profiles, entitlements
27. [[ios-debugging]] — LLDB, breakpoints, view debugging, sanitizers
28. [[ios-permissions-security]] — Privacy Manifest, Info.plist, Keychain, App Transport Security
29. [[ios-testing]] — XCTest: unit, UI, performance, snapshot тесты
30. [[ios-app-distribution]] — TestFlight, App Store, Ad Hoc, Enterprise

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Освоить concurrency в глубину, Core Data, рендеринг, производительность, модульную архитектуру
> Время: ~4 недели
> Prerequisites: Level 2

### Concurrency Deep Dives
31. [[ios-gcd-deep-dive]] — Grand Central Dispatch: barriers, semaphores, groups
32. [[ios-async-await]] — Swift async/await: suspension points, Actors, TaskGroup
33. [[ios-concurrency-mistakes]] — типичные ошибки GCD и Swift Concurrency
34. [[ios-combine]] — Combine framework: Publisher, Operators, backpressure

### Data Deep Dives
35. [[ios-core-data]] — Core Data: объектный граф, NSManagedObjectContext, CloudKit

### Рендеринг и графика
36. [[ios-view-rendering]] — Render Loop: Layout -> Display -> Commit, off-screen rendering
37. [[ios-graphics-fundamentals]] — Core Graphics, Core Animation, Metal
38. [[ios-touch-interaction]] — Responder Chain, hit testing, UIGestureRecognizer

### Архитектура и Interop
39. [[ios-modularization]] — SPM-based модульная архитектура: feature/interface/core
40. [[ios-swift-objc-interop]] — Bridging Header, @objc, Objective-C Runtime
41. [[ios-background-execution]] — beginBackgroundTask, BGTaskScheduler, Background Modes

---

## Уровень 4: Экспертиза (Expert)
> Цель: Профилирование, оптимизация производительности, системная архитектура, CI/CD
> Время: ~3 недели
> Prerequisites: Level 3

42. [[ios-architecture]] — Darwin, XNU, 4 слоя системы (Core OS -> Cocoa Touch)
43. [[ios-process-memory]] — ARC internals, Jetsam kills, лимиты памяти
44. [[ios-performance-profiling]] — Instruments: Time Profiler, Memory Graph, MetricKit
45. [[ios-ci-cd]] — Xcode Cloud, Fastlane, GitHub Actions: автоматизация сборки
