---
title: "iOS: путь обучения"
created: 2026-02-10
modified: 2026-02-14
type: guide
tags:
  - topic/ios
  - type/guide
  - navigation
  - learning-path
---

# iOS: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

### Рекомендуемый темп
2-3 файла в день (~60-90 минут). Каждый 5-й день — повторение изученного.

---

## Уровень 1: Основы (Beginner)
> Цель: Понять архитектуру iOS, освоить Xcode, базовые UI-фреймворки и жизненный цикл
> Время: ~3 недели
> Объём: ~321 мин чтения (5 файлов)

- [ ] [[ios-overview]] — карта раздела и точка входа в iOS-разработку ⏱ 27m
- [ ] [[ios-market-trends-2026]] — рынок iOS в 2026: Swift 6, SwiftUI adoption, on-device AI ⏱ 92m
- [ ] [[ios-xcode-fundamentals]] — проекты, Targets, Schemes, Build Settings ⏱ 72m
- [ ] [[ios-uikit-fundamentals]] — UIView, Auto Layout, Responder Chain, координатные системы ⏱ 73m
- [ ] [[ios-app-components]] — UIApplication, AppDelegate, SceneDelegate, scene-based lifecycle ⏱ 57m
- 📝 День повторения: пересмотри заметки 1-5, ответь на вопросы в конце каждого файла

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить SwiftUI/UIKit, навигацию, архитектуру, работу с данными и сетью, тестирование
> Время: ~6 недель
> Prerequisites: Level 1
> Объём: ~1982 мин чтения (25 файлов)

### Lifecycle
- [ ] [[ios-viewcontroller-lifecycle]] — жизненный цикл UIViewController: loadView, viewDidLoad, appear/disappear ⏱ 70m

### UI: SwiftUI и UIKit
- [ ] [[ios-swiftui]] — декларативный UI: View, модификаторы, Live Preview ⏱ 67m
- [ ] [[ios-swiftui-vs-uikit]] — сравнение подходов: когда SwiftUI, когда UIKit ⏱ 75m
- [ ] [[ios-state-management]] — @State, @Binding, @StateObject, @Observable ⏱ 55m
- 📝 День повторения: пересмотри заметки 6-9, проверь понимание SwiftUI lifecycle

> [!tip] Если начинаешь новый проект на SwiftUI, можешь пропустить UIKit deep dives и вернуться позже.

- [ ] [[ios-custom-views]] — Custom Views: UIView subclassing, draw(_:), intrinsicContentSize ⏱ 125m
- [ ] [[ios-navigation]] — UINavigationController, TabBarController, NavigationStack, Coordinator ⏱ 52m
- [ ] [[ios-accessibility]] — VoiceOver, Dynamic Type, контрасты, Reduce Motion ⏱ 66m
- [ ] [[ios-scroll-performance]] — UITableView/UICollectionView: cell reuse, prefetching, 60/120 FPS ⏱ 80m
- 📝 День повторения: пересмотри заметки 10-13, сравни UIKit и SwiftUI подходы

### Архитектура
- [ ] [[ios-architecture-patterns]] — MVC, MVVM, VIPER, TCA и Clean Architecture ⏱ 117m
- [ ] [[ios-architecture-evolution]] — от Massive ViewController к @Observable + TCA ⏱ 35m
- [ ] [[ios-viewmodel-patterns]] — ObservableObject, @Observable macro, Input-Output ⏱ 93m
- [ ] [[ios-dependency-injection]] — Constructor injection, Swinject, Environment ⏱ 58m
- [ ] [[ios-repository-pattern]] — Single Source of Truth, offline-first, кэширование ⏱ 64m
- 📝 День повторения: пересмотри заметки 14-18, нарисуй диаграмму архитектуры

### Данные и сеть
- [ ] [[ios-data-persistence]] — UserDefaults, FileManager, Keychain, iCloud KVS ⏱ 108m
- [ ] [[ios-swiftdata]] — SwiftData (iOS 17+): @Model macro, @Query ⏱ 80m
- [ ] [[ios-networking]] — URLSession: async/await, Codable, фоновые загрузки ⏱ 60m
- [ ] [[ios-notifications]] — UNUserNotificationCenter, APNs, Live Activities ⏱ 83m
- 📝 День повторения: пересмотри заметки 19-22, построй mental map хранения данных

### Concurrency
- [ ] [[ios-threading-fundamentals]] — Main Thread, GCD очереди, serial vs concurrent, QoS ⏱ 53m
- [ ] [[ios-async-evolution]] — эволюция: NSThread -> GCD -> async/await -> Swift 6 ⏱ 51m

### Build и безопасность
- [ ] [[ios-compilation-pipeline]] — от Swift до .app: AST -> SIL -> LLVM IR -> Machine Code ⏱ 108m
- [ ] [[ios-code-signing]] — сертификаты, provisioning profiles, entitlements ⏱ 86m
- [ ] [[ios-debugging]] — LLDB, breakpoints, view debugging, sanitizers ⏱ 69m
- [ ] [[ios-permissions-security]] — Privacy Manifest, Info.plist, Keychain, App Transport Security ⏱ 74m
- [ ] [[ios-testing]] — XCTest: unit, UI, performance, snapshot тесты ⏱ 64m
- 📝 День повторения: пересмотри заметки 23-29, проверь знание build pipeline
- [ ] [[ios-app-distribution]] — TestFlight, App Store, Ad Hoc, Enterprise ⏱ 169m
- 📝 День повторения: пересмотри заметки 25-30, убедись что понимаешь весь путь от кода до App Store

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Освоить concurrency в глубину, Core Data, рендеринг, производительность, модульную архитектуру
> Время: ~4 недели
> Prerequisites: Level 2
> Объём: ~857 мин чтения (11 файлов)

### Concurrency Deep Dives
- [ ] [[ios-gcd-deep-dive]] — Grand Central Dispatch: barriers, semaphores, groups ⏱ 80m
- [ ] [[ios-async-await]] — Swift async/await: suspension points, Actors, TaskGroup ⏱ 72m
- [ ] [[ios-concurrency-mistakes]] — типичные ошибки GCD и Swift Concurrency ⏱ 63m

> [!tip] С async/await в Swift 6, Combine менее актуален для новых проектов. Пропусти если не работаешь с Combine codebase.

- [ ] [[ios-combine]] — Combine framework: Publisher, Operators, backpressure ⏱ 64m
- 📝 День повторения: пересмотри заметки 31-34, сравни GCD vs async/await vs Combine

### Data Deep Dives

> [!tip] Если используешь SwiftData, Core Data можно изучить позже для legacy проектов.

- [ ] [[ios-core-data]] — Core Data: объектный граф, NSManagedObjectContext, CloudKit ⏱ 83m

### Рендеринг и графика
- [ ] [[ios-view-rendering]] — Render Loop: Layout -> Display -> Commit, off-screen rendering ⏱ 109m
- [ ] [[ios-graphics-fundamentals]] — Core Graphics, Core Animation, Metal ⏱ 121m
- [ ] [[ios-touch-interaction]] — Responder Chain, hit testing, UIGestureRecognizer ⏱ 82m
- 📝 День повторения: пересмотри заметки 35-38, нарисуй render pipeline

### Архитектура и Interop
- [ ] [[ios-modularization]] — SPM-based модульная архитектура: feature/interface/core ⏱ 58m

> [!tip] Если работаешь только со Swift кодом, ObjC interop можно пропустить.

- [ ] [[ios-swift-objc-interop]] — Bridging Header, @objc, Objective-C Runtime ⏱ 72m
- [ ] [[ios-background-execution]] — beginBackgroundTask, BGTaskScheduler, Background Modes ⏱ 53m
- 📝 День повторения: пересмотри заметки 39-41, продумай модульную структуру своего проекта

---

## Уровень 4: Экспертиза (Expert)
> Цель: Профилирование, оптимизация производительности, системная архитектура, CI/CD
> Время: ~3 недели
> Prerequisites: Level 3
> Объём: ~316 мин чтения (4 файла)

- [ ] [[ios-architecture]] — Darwin, XNU, 4 слоя системы (Core OS -> Cocoa Touch) ⏱ 33m
- [ ] [[ios-process-memory]] — ARC internals, Jetsam kills, лимиты памяти ⏱ 50m
- [ ] [[ios-performance-profiling]] — Instruments: Time Profiler, Memory Graph, MetricKit ⏱ 112m
- [ ] [[ios-ci-cd]] — Xcode Cloud, Fastlane, GitHub Actions: автоматизация сборки ⏱ 121m
- 📝 День повторения: пересмотри заметки 42-45, проведи профилирование реального приложения
