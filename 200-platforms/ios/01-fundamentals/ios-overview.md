---
title: "iOS: карта раздела"
created: 2026-01-11
modified: 2026-02-13
type: overview
reading_time: 27
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
area: ios
confidence: high
tags:
  - topic/ios
  - topic/swift
  - type/overview
  - level/beginner
cs-foundations: [reference-counting-arc, ffi-foreign-function-interface, mobile-platform-architecture]
related:
  - "[[android-overview]]"
  - "[[kmp-overview]]"
  - "[[kmp-ios-deep-dive]]"
  - "[[compose-mp-ios]]"
  - "[[ios-architecture]]"
  - "[[ios-app-components]]"
  - "[[ios-viewcontroller-lifecycle]]"
  - "[[ios-process-memory]]"
  - "[[ios-uikit-fundamentals]]"
  - "[[ios-swiftui]]"
  - "[[ios-swiftui-vs-uikit]]"
  - "[[ios-navigation]]"
  - "[[ios-touch-interaction]]"
  - "[[ios-accessibility]]"
  - "[[ios-threading-fundamentals]]"
  - "[[ios-async-evolution]]"
  - "[[ios-gcd-deep-dive]]"
  - "[[ios-async-await]]"
  - "[[ios-combine]]"
  - "[[ios-concurrency-mistakes]]"
  - "[[ios-networking]]"
  - "[[ios-data-persistence]]"
  - "[[ios-core-data]]"
  - "[[ios-swiftdata]]"
  - "[[ios-architecture-patterns]]"
  - "[[ios-architecture-evolution]]"
  - "[[ios-viewmodel-patterns]]"
  - "[[ios-state-management]]"
  - "[[ios-dependency-injection]]"
  - "[[ios-repository-pattern]]"
  - "[[ios-modularization]]"
  - "[[ios-background-execution]]"
  - "[[ios-permissions-security]]"
  - "[[ios-notifications]]"
  - "[[ios-testing]]"
  - "[[ios-xcode-fundamentals]]"
  - "[[ios-compilation-pipeline]]"
  - "[[ios-code-signing]]"
  - "[[ios-app-distribution]]"
  - "[[ios-ci-cd]]"
  - "[[ios-graphics-fundamentals]]"
  - "[[ios-view-rendering]]"
  - "[[ios-performance-profiling]]"
  - "[[ios-scroll-performance]]"
  - "[[ios-swift-objc-interop]]"
  - "[[ios-custom-views]]"
  - "[[ios-debugging]]"
  - "[[ios-market-trends-2026]]"
---

# iOS: карта раздела

iOS — мобильная операционная система Apple на базе Darwin (XNU kernel). В отличие от Android, iOS использует ARC вместо GC, закрытую экосистему инструментов (Xcode), и два параллельных UI фреймворка (UIKit и SwiftUI). Swift — основной язык разработки с 2014 года.

> **Prerequisites:**
> - Базовое понимание программирования (ООП, Swift)
> - [[reference-counting-arc]] — как работает ARC (полезно)
> - Понимание что такое мобильное приложение

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "SwiftUI полностью заменил UIKit" | Нет. 60%+ production apps используют UIKit или hybrid. SwiftUI стабилен только с iOS 15+ |
| "ARC автоматически управляет памятью — утечек не будет" | ARC не обнаруживает retain cycles. Нужны weak/unowned references вручную |
| "iOS приложение всегда живёт в фоне" | Нет. Jetsam (iOS аналог LMK) агрессивно убивает приложения при нехватке памяти |
| "Swift async/await = Kotlin Coroutines" | Похоже, но отличия: разные модели structured concurrency, actors vs channels |
| "Core Data устарела, нужен SwiftData" | SwiftData требует iOS 17+. Core Data — production-ready для всех версий |
| "UI можно обновлять из любого потока" | Main Thread only! Нарушение = краши и undefined behavior |

---

## CS-фундамент

| CS-концепция | Применение в iOS |
|--------------|-----------------|
| **Reference counting** | ARC (Automatic Reference Counting) — память освобождается при retain count = 0 |
| **Message passing** | Objective-C runtime, KVO, NotificationCenter — динамическая диспетчеризация |
| **Run loop** | Main RunLoop обрабатывает события, таймеры, input sources |
| **MVC pattern** | Apple's recommended architecture (с оговорками о Massive VC) |
| **Declarative UI** | SwiftUI — функциональное описание UI, automatic diffing |
| **Sandbox isolation** | Каждое приложение изолировано, доступ через entitlements |
| **Hybrid kernel** | XNU = Mach (микроядро) + BSD (Unix APIs) + IOKit (драйверы) |

---

## Зачем разработчику глубоко понимать iOS

Многие разработчики знают "как написать приложение", но не понимают "почему оно работает именно так". Это приводит к типичным проблемам:

**Почему приложение крашится с EXC_BAD_ACCESS?** Потому что объект был освобождён, а на него остались ссылки. ARC не спасает от dangling pointers в Objective-C interop и unsafe Swift. Понимание ARC объясняет, почему weak references критичны.

**Почему UI "подвисает"?** Потому что тяжёлая работа выполняется на Main Thread. 16.67ms на кадр при 60 FPS, 8.33ms при 120 FPS (ProMotion). Понимание run loop объясняет, почему async нужен.

**Почему приложение убивается в фоне?** Потому что iOS агрессивно освобождает память. Jetsam приоритизирует foreground apps. Понимание процессной модели объясняет, зачем нужен state restoration.

---

## Структура раздела

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              iOS                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ФУНДАМЕНТ (сначала читать это)                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ Архитектура      │  │ Компоненты       │  │ Процессы и       │       │
│  │ Darwin, XNU      │  │ UIApplication    │  │ память (ARC)     │       │
│  │ Frameworks       │  │ Scenes, Windows  │  │ Jetsam           │       │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘       │
│           │                     │                     │                  │
│           ▼                     ▼                     ▼                  │
│  ┌──────────────────────────────────────────────────────────────────────┐│
│  │              ЖИЗНЕННЫЙ ЦИКЛ VIEWCONTROLLER                            ││
│  │  init → loadView → viewDidLoad → viewWillAppear → viewDidAppear      ││
│  │  ⟷ viewWillDisappear → viewDidDisappear → deinit                    ││
│  └──────────────────────────────────────────────────────────────────────┘│
│           │                     │                     │                  │
│           ▼                     ▼                     ▼                  │
│  UI (РАВНЫЙ БАЛАНС SwiftUI / UIKit)                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ UIKit            │  │ SwiftUI          │  │ Navigation       │       │
│  │ UIView, AutoLayout│  │ @State, Modifiers│  │ Both frameworks  │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                          │
│  ДАННЫЕ И СЕТЬ                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ Persistence      │  │ Networking       │  │ Threading        │       │
│  │ CoreData,SwiftData│  │ URLSession      │  │ GCD, async/await │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                          │
│  АРХИТЕКТУРА И КАЧЕСТВО                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ Architecture     │  │ DI               │  │ Testing          │       │
│  │ MVVM, TCA, Clean │  │ Swinject, Manual │  │ XCTest, UI tests │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                          │
│  СИСТЕМА И BUILD                                                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│  │ Background       │  │ Permissions      │  │ Xcode & Build    │       │
│  │ BackgroundTasks  │  │ Privacy Manifest │  │ Signing, CI/CD   │       │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Материалы раздела

### Фундамент (читать в этом порядке)

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[ios-architecture]] | Darwin, XNU, framework layers, app sandbox | [[os-overview]] |
| [[ios-app-components]] | UIApplication, Scenes, Windows, ViewControllers | [[ios-architecture]] |
| [[ios-viewcontroller-lifecycle]] | Жизненный цикл, состояния, переходы | [[android-activity-lifecycle]] |
| [[ios-process-memory]] | ARC internals, Jetsam, memory warnings | [[reference-counting-arc]] |

### UI и взаимодействие (50/50 SwiftUI / UIKit)

| Материал | Что узнаете | Фреймворк |
|----------|-------------|-----------|
| [[ios-uikit-fundamentals]] | UIView, Auto Layout, frames, constraints | UIKit |
| [[ios-swiftui]] | Declarative UI, @State, @Binding, modifiers | SwiftUI |
| [[ios-swiftui-vs-uikit]] | Сравнение, когда что выбрать, interop | Both |
| [[ios-navigation]] | NavigationStack + UINavigationController | Both |
| [[ios-touch-interaction]] | Gestures, responder chain | Both |
| [[ios-accessibility]] | VoiceOver, Dynamic Type | Both |

### Асинхронная работа (Balanced GCD + async/await)

| Материал | Что узнаете | Фокус |
|----------|-------------|-------|
| [[ios-threading-fundamentals]] | Main Thread, thread safety, DispatchQueue | GCD |
| [[ios-async-evolution]] | Timeline: Threads → GCD → Operations → async/await | Both |
| [[ios-gcd-deep-dive]] | DispatchQueue internals, QoS, groups | GCD |
| [[ios-async-await]] | Swift 6 async/await, Tasks, actors | Modern |
| [[ios-combine]] | Publishers, Subscribers, operators | Modern |
| [[ios-concurrency-mistakes]] | 12 anti-patterns: GCD + async/await | Both |

### Данные и сеть

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[ios-networking]] | URLSession, Codable, REST APIs | [[android-networking]] |
| [[ios-data-persistence]] | UserDefaults, FileManager, Keychain | [[android-data-persistence]] |
| [[ios-core-data]] | Managed objects, fetch requests, migrations | [[database-design-optimization]] |
| [[ios-swiftdata]] | SwiftData (iOS 17+), @Model, @Query | [[ios-core-data]] |

### Архитектура приложений

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[ios-architecture-patterns]] | MVC, MVVM, VIPER, Clean Architecture, TCA | [[android-architecture-patterns]] |
| [[ios-architecture-evolution]] | Эволюция: Massive VC → MVP → MVVM → TCA | [[android-architecture-evolution]] |
| [[ios-viewmodel-patterns]] | ObservableObject, @Published, Combine | [[android-viewmodel-internals]] |
| [[ios-state-management]] | @State, @StateObject, @Environment, Redux | [[android-state-management]] |
| [[ios-dependency-injection]] | Manual DI, Swinject, Needle, Environment | [[android-dependency-injection]] |
| [[ios-repository-pattern]] | SSOT, offline-first, caching | [[android-repository-pattern]] |
| [[ios-modularization]] | SPM modules, feature targets | [[android-modularization]] |

### Системная интеграция

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[ios-background-execution]] | Background modes, BackgroundTasks | [[android-background-work]] |
| [[ios-permissions-security]] | Privacy Manifest, entitlements, ATS | [[android-permissions-security]] |
| [[ios-notifications]] | UNUserNotificationCenter, push, extensions | |
| [[ios-testing]] | XCTest, UI tests, performance | [[android-testing]] |

### Build System

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[ios-xcode-fundamentals]] | Project structure, targets, schemes | [[android-gradle-fundamentals]] |
| [[ios-compilation-pipeline]] | Compilation, linking, app bundle | [[android-compilation-pipeline]] |
| [[ios-code-signing]] | Provisioning profiles, certificates | |
| [[ios-app-distribution]] | TestFlight, App Store Connect | [[android-apk-aab]] |
| [[ios-ci-cd]] | Xcode Cloud, Fastlane, GitHub Actions | [[android-ci-cd]] |

### Graphics & Performance

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[ios-graphics-fundamentals]] | Core Graphics, Core Animation, Metal | [[android-canvas-drawing]] |
| [[ios-view-rendering]] | Render loop, layers, off-screen rendering | [[android-view-rendering-pipeline]] |
| [[ios-performance-profiling]] | Instruments, Time Profiler, Memory Graph | |
| [[ios-scroll-performance]] | UITableView, UICollectionView optimization | |

### Advanced

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[ios-swift-objc-interop]] | Bridging headers, @objc, name mangling | [[ffi-foreign-function-interface]] |
| [[ios-custom-views]] | UIView subclassing, custom drawing | [[android-custom-view-fundamentals]] |
| [[ios-debugging]] | LLDB, Instruments, crash analysis | |
| [[ios-market-trends-2026]] | Job market, frameworks, KMP impact | |

---

## iOS vs Android: ключевые отличия

| Аспект | iOS | Android |
|--------|-----|---------|
| **Ядро** | XNU (hybrid: Mach + BSD) | Linux kernel |
| **Память** | ARC (reference counting) | GC (tracing garbage collection) |
| **Освобождение** | Немедленно при count = 0 | Периодически, batch |
| **Retain cycles** | Нужны weak references | GC справляется сам |
| **UI Framework** | SwiftUI + UIKit (параллельно) | Jetpack Compose (унифицирован) |
| **Async** | async/await + GCD | Coroutines |
| **IDE** | Xcode (Apple only) | Android Studio (cross-platform) |
| **Build System** | Xcode Build System (opaque) | Gradle (transparent) |
| **Distribution** | App Store only* | Play Store, APK sideload |
| **Code Signing** | Сложно (profiles, certs) | Просто (keystore) |
| **Lifecycle** | Scene-based (iOS 13+) | Activity/Fragment-based |
| **Background** | Очень ограничен | WorkManager (гибче) |

*Кроме enterprise distribution и TestFlight

---

## Числа, которые нужно знать

| Метрика | Значение | Почему важно |
|---------|----------|--------------|
| Frame time (60 FPS) | 16.67ms | Превышение = UI jank |
| Frame time (ProMotion) | 8.33ms | 120 FPS на Pro устройствах |
| App startup (cold) | <400ms желательно | Apple review guidelines |
| Memory limit | 1-2 GB (зависит от устройства) | Jetsam убивает при превышении |
| Background execution | ~30 секунд (без modes) | beginBackgroundTask лимит |
| SwiftUI adoption | ~40% новых проектов | UIKit всё ещё доминирует |

---

## Терминология раздела

| Термин | Значение |
|--------|----------|
| **ARC** | Automatic Reference Counting — управление памятью через подсчёт ссылок |
| **XNU** | X is Not Unix — гибридное ядро iOS/macOS |
| **Darwin** | Open-source основа iOS, включает XNU |
| **UIKit** | Императивный UI framework (2008+) |
| **SwiftUI** | Декларативный UI framework (2019+) |
| **Scene** | Независимый UI instance (iOS 13+), multi-window support |
| **Jetsam** | iOS memory pressure daemon, убивает приложения |
| **Entitlements** | Разрешения на системные функции (push, iCloud, etc.) |
| **Provisioning Profile** | Сертификат для запуска на устройствах |
| **Main Thread** | UI Thread, обрабатывает события и рендеринг |
| **RunLoop** | Event processing loop на потоке |
| **GCD** | Grand Central Dispatch — низкоуровневое API concurrency |
| **Combine** | Reactive framework от Apple |
| **Core Data** | ORM/Object Graph framework от Apple |
| **SwiftData** | Modern data persistence (iOS 17+) |
| **TCA** | The Composable Architecture — популярный architecture pattern |

---

## Связь с другими разделами

```
iOS РАЗРАБОТЧИКУ ПОЛЕЗНО ЗНАТЬ:
────────────────────────────────

[[reference-counting-arc]]  ← Как работает ARC на уровне CS
   │
   └── [[ios-process-memory]] ← Применение в iOS

[[os-overview]]             ← Darwin/XNU базируется на OS концепциях
   │
   ├── [[os-processes-threads]] ← Processes & threads
   └── [[os-memory-management]] ← Memory management

[[kmp-overview]]         ← Kotlin Multiplatform для iOS
   │
   ├── [[kmp-ios-deep-dive]]    ← iOS интеграция KMP
   └── [[compose-mp-ios]]       ← Compose Multiplatform на iOS

[[android-overview]]        ← Сравнение с Android
   │
   ├── Lifecycle differences
   ├── Memory management (GC vs ARC)
   └── UI frameworks (Compose vs SwiftUI)

[[architecture-overview]]   ← Паттерны проектирования
   │
   ├── [[api-design]]          ← REST, GraphQL
   └── [[caching-strategies]]  ← Кэширование данных
```

| Раздел | Как связан с iOS | Что даёт |
|--------|------------------|----------|
| [[reference-counting-arc]] | ARC = iOS memory management | Понимание retain cycles |
| [[os-overview]] | Darwin = iOS foundation | Process/memory концепции |
| [[kmp-overview]] | KMP targets iOS | Shared code с Android |
| [[android-overview]] | Сравнение платформ | Понимание отличий |
| [[networking-overview]] | URLSession patterns | HTTP, REST |

---

## С чего начать

**Если вы новичок в iOS:** Начните с [[ios-architecture]] для понимания того, как устроена система. Затем [[ios-app-components]] и [[ios-viewcontroller-lifecycle]] — это фундамент.

**Если вы знаете основы, но хотите глубже:** [[ios-process-memory]] объяснит ARC и Jetsam. [[ios-threading-fundamentals]] покажет правильную работу с async.

**Если вы переходите с Android:** Обратите внимание на [[ios-swiftui-vs-uikit]] — в iOS два UI framework. Изучите [[ios-process-memory]] — ARC отличается от GC принципиально.

**Если вы работаете с KMP:** [[kmp-ios-deep-dive]] и [[compose-mp-ios]] объяснят особенности iOS target.

---

## Источники

### Официальные
- [Apple Developer Documentation](https://developer.apple.com/documentation/) — официальная документация
- [Swift.org](https://www.swift.org/documentation/) — язык Swift
- [WWDC Videos](https://developer.apple.com/videos/) — ежегодные обновления
- [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) — дизайн гайдлайны

### Roadmaps & Best Practices
- [roadmap.sh/ios](https://roadmap.sh/ios) — iOS Developer Roadmap
- [iOS Development Hub 2025](https://www.alimertgulec.com/en/blog/ios-development-hub-2025) — comprehensive guide
- [Modern iOS Architecture 2025](https://medium.com/@csmax/the-ultimate-guide-to-modern-ios-architecture-in-2025-9f0d5fdc892f)

### Community
- [Hacking with Swift](https://www.hackingwithswift.com/) — tutorials by Paul Hudson
- [SwiftLee](https://www.avanderlee.com/) — advanced Swift articles
- [Swift by Sundell](https://www.swiftbysundell.com/) — Swift patterns
- [Point-Free](https://www.pointfree.co/) — TCA and functional Swift

---

---

## Проверь себя

> [!question]- Почему iOS использует ARC вместо Garbage Collection, и какие практические последствия это имеет для разработчика?
> ARC работает на этапе компиляции и освобождает объекты детерминированно при обнулении счётчика ссылок. Это обеспечивает предсказуемый performance без пауз GC, что критично для 60/120 FPS UI. Однако разработчик обязан вручную разрывать retain cycles через weak/unowned, иначе объекты останутся в памяти навсегда.

> [!question]- Вы разрабатываете новое приложение для банка с поддержкой iOS 15+. Какой UI-фреймворк выберете и почему?
> Оптимально гибридный подход: SwiftUI для новых экранов и навигации, UIKit для сложных кастомных компонентов (графики транзакций, кастомные input-формы). SwiftUI стабилен с iOS 15+, но enterprise-проекты часто требуют UIKit для accessibility compliance и сложных взаимодействий.

> [!question]- Почему в iOS нельзя обновлять UI из фонового потока, и что произойдёт при нарушении этого правила?
> UIKit и SwiftUI не являются thread-safe. Main RunLoop обрабатывает touch events, layout и rendering строго на Main Thread. При обновлении UI из другого потока возникают краши, визуальные артефакты и undefined behavior. Решение -- использовать DispatchQueue.main или MainActor.

> [!question]- Какова роль Jetsam в iOS и чем он отличается от Android Low Memory Killer?
> Jetsam -- демон iOS, который агрессивно убивает suspended-приложения при нехватке памяти, приоритизируя foreground apps. В отличие от Android LMK, iOS может убить приложение без предупреждения из suspended state, поэтому критически важно сохранять состояние в didEnterBackground.

---

## Ключевые карточки

Что такое ARC и как оно работает в iOS?
?
ARC (Automatic Reference Counting) -- compile-time механизм управления памятью. Компилятор вставляет retain/release инструкции. Объект освобождается немедленно при обнулении счётчика ссылок. Не обнаруживает retain cycles автоматически.

Какие два UI-фреймворка существуют в iOS и каков их текущий статус?
?
UIKit (2008+, императивный) и SwiftUI (2019+, декларативный). UIKit доминирует в production (~60%+ apps), SwiftUI стабилен с iOS 15+ и используется в ~40% новых проектов. Большинство команд используют гибридный подход.

Что такое Jetsam и почему он важен?
?
Jetsam -- iOS memory pressure daemon, который убивает приложения при нехватке памяти. Foreground apps имеют приоритет. Suspended apps убиваются без уведомления кода. Поэтому state restoration и сохранение в didEnterBackground критичны.

Из чего состоит XNU kernel?
?
XNU = Mach (микроядро: процессы, потоки, IPC, VM) + BSD (Unix APIs: файлы, сети, сокеты) + IOKit (драйверы устройств). Это гибридное ядро, основа Darwin и iOS.

Какое время отведено на один кадр при 60 FPS и 120 FPS?
?
При 60 FPS -- 16.67ms на кадр, при 120 FPS (ProMotion) -- 8.33ms. Превышение этого времени на Main Thread приводит к UI jank (подвисаниям интерфейса).

Чем отличается async/await в Swift от Kotlin Coroutines?
?
Обе системы поддерживают structured concurrency, но отличаются моделями: Swift использует actors для изоляции, Kotlin -- channels. Разные модели structured concurrency и разные подходы к shared mutable state.

Что такое Scene в iOS 13+?
?
Scene -- независимый UI instance приложения, поддерживающий multi-window. Каждая scene имеет свой lifecycle (foreground/background), свой UIWindow и управляется SceneDelegate. На iPhone обычно одна scene, на iPad -- несколько.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-architecture]] | Понять архитектуру Darwin/XNU и слои системы |
| Углубиться | [[ios-process-memory]] | Разобраться в ARC, retain cycles и Jetsam |
| Смежная тема | [[android-overview]] | Сравнить платформы: GC vs ARC, Compose vs SwiftUI |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |

---

*Проверено: 2026-02-13 | На основе официальной документации Apple и исследований*
