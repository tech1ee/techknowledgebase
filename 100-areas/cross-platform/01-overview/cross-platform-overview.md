---
title: "Cross-Platform: iOS vs Android сравнение"
created: 2026-01-11
modified: 2026-01-11
type: overview
status: published
tags:
  - type/overview
  - topic/cross-platform
  - topic/ios
  - topic/android
  - topic/kmp
  - level/beginner
---

# Cross-Platform: iOS vs Android сравнение

## Введение

Этот раздел — глубокое погружение в сравнение iOS и Android платформ. Но это не просто таблица "Swift vs Kotlin" или "UIKit vs Jetpack Compose". Здесь мы исследуем **ПОЧЕМУ** каждая платформа выбрала свой подход.

Понимание причин важнее запоминания различий. Когда вы знаете, что iOS пришла из мира NeXTSTEP с его детерминированным управлением памятью, а Android — из мира Java с garbage collection, различия в API перестают казаться случайными.

Каждый файл в этом разделе отвечает на три вопроса:
1. **ЧТО** — конкретные различия в API, синтаксисе, подходах
2. **ПОЧЕМУ** — исторические и технические причины различий
3. **КАК** — практические паттерны для KMP разработки

---

## Ключевое философское различие

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ФУНДАМЕНТАЛЬНАЯ ФИЛОСОФИЯ ПЛАТФОРМ                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  iOS:  "ДЕТЕРМИНИЗМ И КОНТРОЛЬ"                                             │
│        ├── Разработчик контролирует lifecycle                                │
│        │   └── viewDidLoad, viewWillAppear — ВЫ решаете что делать          │
│        ├── Память освобождается предсказуемо (ARC)                          │
│        │   └── Объект умирает когда последняя ссылка исчезает               │
│        ├── Один vendor = консистентность                                     │
│        │   └── Все устройства ведут себя одинаково                          │
│        └── Закрытая экосистема = оптимизация                                │
│            └── Компилятор знает всё о целевом устройстве                    │
│                                                                              │
│  Android: "ГИБКОСТЬ И АДАПТИВНОСТЬ"                                         │
│           ├── Система контролирует lifecycle                                 │
│           │   └── onCreate, onDestroy — система УВЕДОМЛЯЕТ вас              │
│           ├── Память освобождается когда удобно (GC)                        │
│           │   └── Объект умирает когда GC решит это сделать                 │
│           ├── Много vendor'ов = адаптация                                   │
│           │   └── Код должен работать на 1000+ разных устройств             │
│           └── Открытая экосистема = универсальность                         │
│               └── Байткод JVM работает везде                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Почему это важно для разработчика?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ПРАКТИЧЕСКИЕ ПОСЛЕДСТВИЯ                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Ваш код iOS:                      │  Ваш код Android:                      │
│  ─────────────────────────────────┼──────────────────────────────────────── │
│  class MyViewController {          │  class MyActivity : Activity() {       │
│      deinit {                      │      override fun onDestroy() {        │
│          // ГАРАНТИРОВАННО         │          // ВОЗМОЖНО вызовется         │
│          // вызовется              │          // но не гарантировано        │
│          cleanup()                 │          cleanup()                     │
│      }                             │      }                                  │
│  }                                 │  }                                      │
│                                    │                                         │
│  ✓ Можно полагаться на deinit     │  ✗ Нельзя полагаться на onDestroy     │
│  ✓ Ресурсы освободятся            │  → Используйте ViewModel + onCleared   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Историческое наследие

### Корни платформ

| Аспект | iOS (2007) | Android (2008) |
|--------|------------|----------------|
| **Происхождение** | NeXTSTEP → macOS → iOS | Linux kernel + Java ME влияние |
| **Философия памяти** | Reference Counting (manual → ARC) | Garbage Collection (Dalvik → ART) |
| **UI парадигма** | Cocoa (AppKit → UIKit) | Java Swing влияние → Android Views |
| **Основной язык** | Objective-C → Swift (2014) | Java → Kotlin (2017 официально) |
| **Компиляция** | AOT (Ahead-of-Time) | JIT + AOT (с Android 7) |
| **Runtime** | Objective-C runtime + Swift runtime | ART (Android Runtime) |
| **Sandboxing** | Строгий с iOS 1.0 | Эволюционировал со временем |

### Эволюция UI фреймворков

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ИСТОРИЯ UI ФРЕЙМВОРКОВ                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  iOS:                                                                        │
│  ────                                                                        │
│  1988: NeXTSTEP ──► 2001: Cocoa/AppKit ──► 2007: UIKit ──► 2019: SwiftUI    │
│                         │                      │               │             │
│                         │                      │               │             │
│                    Interface Builder      Storyboards      Declarative       │
│                    (визуальный)           (XML-based)      (код = UI)        │
│                                                                              │
│  Android:                                                                    │
│  ────────                                                                    │
│  2008: Android Views ──► 2015: ConstraintLayout ──► 2021: Jetpack Compose   │
│           │                       │                          │               │
│           │                       │                          │               │
│      XML layouts              Мощный layout            Declarative           │
│      (verbose)                (гибкий)                 (Kotlin DSL)          │
│                                                                              │
│  KMP:                                                                        │
│  ────                                                                        │
│  2020: Compose Multiplatform ──► 2023: iOS Alpha ──► 2024: iOS Beta         │
│              │                         │                    │                │
│              │                         │                    │                │
│        Desktop + Web              Skia rendering       Production-ready?     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Эволюция языков

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ЭВОЛЮЦИЯ ЯЗЫКОВ                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Objective-C (1984)                    Java (1995)                          │
│       │                                     │                                │
│       │ Smalltalk + C                       │ C++ simplified                 │
│       │                                     │                                │
│       ▼                                     ▼                                │
│  Swift (2014)                          Kotlin (2011, Android 2017)          │
│       │                                     │                                │
│       │ Modern, safe, fast                  │ Modern, safe, interop         │
│       │                                     │                                │
│       └─────────────────┬───────────────────┘                                │
│                         │                                                    │
│                         ▼                                                    │
│                   Kotlin Multiplatform                                       │
│                   (общий код + expect/actual)                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Мифы и заблуждения

### Миф 1: "Android сложнее iOS"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  МИФ: Android сложнее iOS                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  РЕАЛЬНОСТЬ: Они сложны ПО-РАЗНОМУ                                          │
│                                                                              │
│  iOS сложности:                    Android сложности:                        │
│  ─────────────────────────────    ─────────────────────────────────         │
│  • Memory management (retain       • Fragment lifecycle (когда что          │
│    cycles, weak/unowned)             вызывается?)                           │
│  • Многопоточность (actors,        • Configuration changes (поворот         │
│    @MainActor, Sendable)             экрана = пересоздание)                 │
│  • Auto Layout constraints         • Фрагментация устройств                 │
│  • App Store review process        • Background restrictions                │
│  • Закрытость экосистемы           • Permissions model                      │
│                                                                              │
│  ВЫВОД: Изучайте ОБЕ платформы — каждая научит разному                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Миф 2: "Swift и Kotlin — это почти одно и то же"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  МИФ: Swift и Kotlin — почти идентичны                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  РЕАЛЬНОСТЬ: Синтаксис похож, СЕМАНТИКА разная                              │
│                                                                              │
│  Swift:                            Kotlin:                                   │
│  ──────                            ───────                                   │
│  struct Point {                    data class Point(                         │
│      var x: Int                        val x: Int,                           │
│      var y: Int                        val y: Int                            │
│  }                                 )                                         │
│                                                                              │
│  let p = Point(x: 1, y: 2)        val p = Point(1, 2)                       │
│  var p2 = p                        var p2 = p                                │
│  p2.x = 10                         // p2.x = 10 — НЕЛЬЗЯ, val!              │
│                                                                              │
│  // p.x всё ещё 1                  // В Kotlin нет value types              │
│  // struct = value type            // data class = reference type            │
│                                                                              │
│  ПОСЛЕДСТВИЯ:                                                                │
│  • Swift struct в 10x быстрее для простых данных                            │
│  • Kotlin требует осторожности с мутабельностью                             │
│  • KMP: приходится выбирать подход (обычно immutable)                       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Миф 3: "GC хуже ARC"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  МИФ: Garbage Collection хуже Automatic Reference Counting                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  РЕАЛЬНОСТЬ: У каждого подхода свои trade-offs                              │
│                                                                              │
│  ARC (iOS):                        GC (Android ART):                         │
│  ──────────                        ────────────────                          │
│  ✓ Предсказуемая задержка          ✓ Автоматически решает циклы            │
│  ✓ Низкий overhead                 ✓ Проще для разработчика                │
│  ✓ Нет пауз                        ✓ Оптимизация в runtime                 │
│                                                                              │
│  ✗ Retain cycles — ваша проблема   ✗ Непредсказуемые паузы                 │
│  ✗ weak/unowned overhead           ✗ Память освобождается "когда-то"       │
│  ✗ Больше boilerplate              ✗ Больше потребление памяти             │
│                                                                              │
│  ПРАКТИКА:                                                                   │
│  • iOS: используйте Instruments для поиска retain cycles                    │
│  • Android: используйте LeakCanary для поиска memory leaks                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Миф 4: "SwiftUI и Compose — это одно и то же"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  МИФ: SwiftUI = Jetpack Compose                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  РЕАЛЬНОСТЬ: Декларативные, но разная реализация                            │
│                                                                              │
│  SwiftUI:                          Jetpack Compose:                          │
│  ────────                          ─────────────────                         │
│  • View — struct (value type)      • @Composable — функция                  │
│  • @State — property wrapper       • remember {} — state holder             │
│  • body вызывается при изменении   • recomposition при изменении            │
│  • Поверх UIKit                    • Полностью новый рендеринг              │
│  • Интеграция с UIKit проста       • Интеграция с Views сложнее             │
│                                                                              │
│  ПРОИЗВОДИТЕЛЬНОСТЬ:                                                         │
│  • SwiftUI: diffing Views          • Compose: positional memoization        │
│  • Меньше контроля                 • Больше контроля (remember, key)        │
│                                                                              │
│  KMP ПОСЛЕДСТВИЯ:                                                            │
│  • Compose Multiplatform использует Compose модель                          │
│  • На iOS рендерит через Skia, не через UIKit                               │
│  • Разное поведение анимаций, скролла, жестов                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Миф 5: "KMP решает все проблемы кросс-платформенности"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  МИФ: KMP — серебряная пуля                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  РЕАЛЬНОСТЬ: KMP — инструмент с ограничениями                               │
│                                                                              │
│  ЧТО KMP ДЕЛАЕТ ХОРОШО:            ЧТО KMP НЕ РЕШАЕТ:                       │
│  ──────────────────────            ─────────────────────                     │
│  ✓ Общая бизнес-логика             ✗ UI остаётся платформенным*            │
│  ✓ Общие модели данных             ✗ Платформенные API нужно               │
│  ✓ Общий networking                  оборачивать через expect/actual        │
│  ✓ Общая валидация                 ✗ Debugging сложнее                      │
│  ✓ Общие тесты                     ✗ Build time увеличивается              │
│                                    ✗ Размер приложения растёт              │
│                                                                              │
│  * Compose Multiplatform меняет это, но пока в beta на iOS                  │
│                                                                              │
│  КОГДА ИСПОЛЬЗОВАТЬ:                                                         │
│  ✓ Сложная бизнес-логика           ✗ Простое приложение                    │
│  ✓ Большая команда                 ✗ Один разработчик                      │
│  ✓ Долгосрочный проект             ✗ MVP / прототип                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Миф 6: "Native всегда лучше"

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  МИФ: Native подход всегда лучше кросс-платформенного                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  РЕАЛЬНОСТЬ: Зависит от контекста                                           │
│                                                                              │
│  NATIVE ЛУЧШЕ КОГДА:               CROSS-PLATFORM ЛУЧШЕ КОГДА:              │
│  ───────────────────               ────────────────────────────              │
│  • Критичная производительность    • Ограниченные ресурсы команды          │
│  • Глубокая интеграция с OS        • Идентичная логика на обеих            │
│  • Платформенный look & feel         платформах                             │
│    критически важен                • Быстрый time-to-market                 │
│  • Долгосрочная поддержка          • B2B приложения                        │
│    одной платформы                 • Внутренние инструменты                │
│                                                                              │
│  ПРИМЕРЫ:                                                                    │
│  • Instagram: Native + shared C++ core                                       │
│  • Airbnb: Ушли с React Native → Native                                     │
│  • Cash App: KMP для бизнес-логики                                          │
│  • Netflix: KMP для части функциональности                                  │
│                                                                              │
│  ВЫВОД: Выбор зависит от проекта, команды и бизнес-целей                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Быстрое сравнение

### Основные концепции

| Концепция | iOS (Swift) | Android (Kotlin) | KMP |
|-----------|-------------|------------------|-----|
| **Memory** | ARC (автоматический подсчёт ссылок) | GC (сборка мусора ART) | Kotlin/Native: ARC-подобный |
| **Lifecycle** | UIViewController lifecycle | Activity/Fragment lifecycle | expect/actual для lifecycle |
| **Async** | async/await, Combine | Coroutines, Flow | Coroutines (общий код) |
| **UI Modern** | SwiftUI (2019) | Jetpack Compose (2021) | Compose Multiplatform |
| **UI Legacy** | UIKit (2007) | Android Views (2008) | — |
| **Networking** | URLSession, Alamofire | OkHttp, Retrofit | Ktor |
| **Database** | Core Data, SQLite | Room, SQLite | SQLDelight |
| **DI** | Manual, Swinject | Hilt, Koin | Koin, Kodein |
| **Build** | Xcode, Swift Package Manager | Gradle, AGP | Gradle KMP Plugin |

### Детальное сравнение по категориям

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         MEMORY MANAGEMENT                                    │
├──────────────────┬─────────────────────┬────────────────────────────────────┤
│      iOS         │      Android        │              KMP                   │
├──────────────────┼─────────────────────┼────────────────────────────────────┤
│ ARC              │ Garbage Collection  │ Kotlin/Native: трассирующий GC    │
│ weak, unowned    │ WeakReference       │ WeakReference в expect/actual     │
│ deinit           │ finalize (не надёж.)│ @SharedImmutable для потоков     │
│ @autoreleasepool │ —                   │ Freeze (deprecated в 1.7.20)     │
│ Instruments      │ LeakCanary, Profiler│ Комбинация инструментов          │
└──────────────────┴─────────────────────┴────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           LIFECYCLE                                          │
├──────────────────┬─────────────────────┬────────────────────────────────────┤
│      iOS         │      Android        │              KMP                   │
├──────────────────┼─────────────────────┼────────────────────────────────────┤
│ viewDidLoad      │ onCreate            │ Lifecycle.State в общем коде     │
│ viewWillAppear   │ onStart             │ KMM-ViewModel                     │
│ viewDidAppear    │ onResume            │ Decompose (навигация)            │
│ viewWillDisappear│ onPause             │ Essenty (lifecycle)              │
│ viewDidDisappear │ onStop              │                                   │
│ deinit           │ onDestroy           │                                   │
│ —                │ onSaveInstanceState │ SavedStateHandle аналоги         │
└──────────────────┴─────────────────────┴────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         ASYNC / CONCURRENCY                                  │
├──────────────────┬─────────────────────┬────────────────────────────────────┤
│      iOS         │      Android        │              KMP                   │
├──────────────────┼─────────────────────┼────────────────────────────────────┤
│ async/await      │ suspend fun         │ suspend fun (общий)              │
│ Task {}          │ CoroutineScope      │ CoroutineScope                   │
│ Actor            │ Mutex               │ Mutex, Atomics                   │
│ @MainActor       │ Dispatchers.Main    │ Dispatchers.Main                 │
│ Combine          │ Flow                │ Flow (общий)                     │
│ AsyncSequence    │ Flow                │ Flow                             │
│ TaskGroup        │ async {}            │ async {}                         │
└──────────────────┴─────────────────────┴────────────────────────────────────┘
```

---

## Структура раздела

### Визуальная карта всех 24 файлов

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CROSS-PLATFORM: 24 ФАЙЛА СРАВНЕНИЯ                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║                        ПРИОРИТЕТ 1: ФУНДАМЕНТ                         ║   │
│  ║                         (изучить первым)                              ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  01-memory-management.md        02-lifecycle.md                       ║   │
│  ║  ├── ARC vs GC                  ├── ViewController vs Activity        ║   │
│  ║  ├── retain cycles              ├── Fragment lifecycle                ║   │
│  ║  └── weak/unowned               └── SavedInstanceState               ║   │
│  ║                                                                       ║   │
│  ║  03-async-concurrency.md        04-data-types.md                     ║   │
│  ║  ├── async/await vs coroutines  ├── struct vs data class             ║   │
│  ║  ├── Combine vs Flow            ├── enum с associated values         ║   │
│  ║  └── actors vs mutex            └── optionals                        ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║                      ПРИОРИТЕТ 2: UI И АРХИТЕКТУРА                    ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  05-declarative-ui.md           06-legacy-ui.md                      ║   │
│  ║  ├── SwiftUI vs Compose         ├── UIKit vs Views                   ║   │
│  ║  ├── State management           ├── XML layouts                      ║   │
│  ║  └── Modifiers vs Modifiers     └── Storyboards                      ║   │
│  ║                                                                       ║   │
│  ║  07-navigation.md               08-architecture-patterns.md          ║   │
│  ║  ├── NavigationStack            ├── MVVM variations                  ║   │
│  ║  ├── Navigation Component       ├── MVI                              ║   │
│  ║  └── Deep links                 └── Clean Architecture              ║   │
│  ║                                                                       ║   │
│  ║  09-state-management.md         10-animations.md                     ║   │
│  ║  ├── @State/@Binding            ├── Core Animation                   ║   │
│  ║  ├── StateFlow/MutableState     ├── Lottie integration              ║   │
│  ║  └── Redux patterns             └── Physics-based                   ║   │
│  ║                                                                       ║   │
│  ║  11-accessibility.md            12-theming.md                        ║   │
│  ║  ├── VoiceOver                  ├── Assets catalogs                  ║   │
│  ║  ├── TalkBack                   ├── Material You                     ║   │
│  ║  └── Dynamic Type               └── Dark mode                       ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║                      ПРИОРИТЕТ 3: ИНФРАСТРУКТУРА                      ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  13-networking.md               14-database.md                       ║   │
│  ║  ├── URLSession vs OkHttp       ├── Core Data vs Room                ║   │
│  ║  ├── Alamofire vs Retrofit      ├── SQLite wrappers                  ║   │
│  ║  └── Ktor                       └── SQLDelight                       ║   │
│  ║                                                                       ║   │
│  ║  15-dependency-injection.md     16-testing.md                        ║   │
│  ║  ├── Manual DI                  ├── XCTest vs JUnit                  ║   │
│  ║  ├── Swinject vs Hilt           ├── UI testing                       ║   │
│  ║  └── Koin                       └── Mocking                         ║   │
│  ║                                                                       ║   │
│  ║  17-build-systems.md            18-project-structure.md              ║   │
│  ║  ├── Xcode vs Gradle            ├── iOS targets                      ║   │
│  ║  ├── SPM vs Maven               ├── Android modules                  ║   │
│  ║  └── KMP Gradle                 └── KMP structure                   ║   │
│  ║                                                                       ║   │
│  ║  19-debugging.md                20-performance.md                    ║   │
│  ║  ├── LLDB vs Android Studio     ├── Instruments                      ║   │
│  ║  ├── Breakpoints                ├── Android Profiler                 ║   │
│  ║  └── Logging                    └── Benchmarking                    ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
│  ╔══════════════════════════════════════════════════════════════════════╗   │
│  ║                        ПРИОРИТЕТ 4: ADVANCED                          ║   │
│  ╠══════════════════════════════════════════════════════════════════════╣   │
│  ║  21-platform-apis.md            22-background-processing.md          ║   │
│  ║  ├── HealthKit/Google Fit       ├── Background App Refresh           ║   │
│  ║  ├── ARKit/ARCore               ├── WorkManager                      ║   │
│  ║  └── Core ML/ML Kit             └── Foreground services             ║   │
│  ║                                                                       ║   │
│  ║  23-app-distribution.md         24-security.md                       ║   │
│  ║  ├── App Store/Play Store       ├── Keychain/Keystore                ║   │
│  ║  ├── TestFlight/Internal        ├── Biometrics                       ║   │
│  ║  └── CI/CD                      └── Certificate pinning            ║   │
│  ╚══════════════════════════════════════════════════════════════════════╝   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Материалы по категориям

### Фундамент (4 критических файла)

Эти файлы закладывают основу понимания платформ. **Изучите их первыми**.

| № | Файл | Ключевые темы | Критичность |
|---|------|---------------|-------------|
| 01 | [[01-memory-management]] | ARC vs GC, retain cycles, weak references | ⭐⭐⭐ Критично |
| 02 | [[02-lifecycle]] | ViewController vs Activity, Fragment, восстановление состояния | ⭐⭐⭐ Критично |
| 03 | [[03-async-concurrency]] | async/await vs coroutines, Combine vs Flow, threading | ⭐⭐⭐ Критично |
| 04 | [[04-data-types]] | struct vs class, enum, optionals, generics | ⭐⭐⭐ Критично |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ПОЧЕМУ ЭТИ ФАЙЛЫ ПЕРВЫЕ?                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Память + Lifecycle + Async + Типы = 80% понимания платформы                │
│                                                                              │
│  Без понимания ПАМЯТИ:                                                       │
│  ├── Будете создавать memory leaks                                          │
│  ├── Не поймёте weak/unowned (iOS) и WeakReference (Android)                │
│  └── KMP freeze/unfreeze будет непонятен                                    │
│                                                                              │
│  Без понимания LIFECYCLE:                                                    │
│  ├── Данные будут теряться при повороте экрана                              │
│  ├── Background tasks будут падать                                          │
│  └── ViewModel pattern будет непонятен                                      │
│                                                                              │
│  Без понимания ASYNC:                                                        │
│  ├── UI будет зависать                                                       │
│  ├── Race conditions                                                         │
│  └── Неправильное использование Flow/Combine                                │
│                                                                              │
│  Без понимания ТИПОВ:                                                        │
│  ├── struct vs class путаница                                               │
│  ├── Неправильное использование Optional                                    │
│  └── Generics ограничения                                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### UI и архитектура (8 файлов)

| № | Файл | Ключевые темы | Сложность |
|---|------|---------------|-----------|
| 05 | [[05-declarative-ui]] | SwiftUI vs Compose, state, modifiers | Средняя |
| 06 | [[06-legacy-ui]] | UIKit vs Views, XML, Interface Builder | Средняя |
| 07 | [[07-navigation]] | NavigationStack, NavController, deep links | Высокая |
| 08 | [[08-architecture-patterns]] | MVVM, MVI, Clean Architecture | Высокая |
| 09 | [[09-state-management]] | @State, StateFlow, Redux patterns | Высокая |
| 10 | [[10-animations]] | Core Animation, Compose animations, Lottie | Средняя |
| 11 | [[11-accessibility]] | VoiceOver, TalkBack, Dynamic Type | Средняя |
| 12 | [[12-theming]] | Assets, Material You, Dark mode | Низкая |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ПУТЬ ИЗУЧЕНИЯ UI                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Для НОВОГО проекта:                                                         │
│  ───────────────────                                                         │
│  05-declarative-ui → 09-state-management → 07-navigation → 08-architecture  │
│                                                                              │
│  Для LEGACY проекта:                                                         │
│  ──────────────────                                                          │
│  06-legacy-ui → 08-architecture → 05-declarative-ui (миграция)             │
│                                                                              │
│  Для KMP с Compose Multiplatform:                                           │
│  ─────────────────────────────────                                           │
│  05-declarative-ui → 09-state-management → 07-navigation                    │
│  (фокус на Compose-часть)                                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Инфраструктура (8 файлов)

| № | Файл | Ключевые темы | Для KMP |
|---|------|---------------|---------|
| 13 | [[13-networking]] | URLSession vs OkHttp, Ktor | ✅ Ktor |
| 14 | [[14-database]] | Core Data vs Room, SQLDelight | ✅ SQLDelight |
| 15 | [[15-dependency-injection]] | Swinject vs Hilt, Koin | ✅ Koin |
| 16 | [[16-testing]] | XCTest vs JUnit, UI tests | ✅ kotlin.test |
| 17 | [[17-build-systems]] | Xcode vs Gradle, SPM | ✅ Gradle KMP |
| 18 | [[18-project-structure]] | Targets, modules, KMP structure | ✅ KMP |
| 19 | [[19-debugging]] | LLDB, Android Studio, logging | ⚠️ Частично |
| 20 | [[20-performance]] | Instruments, Profiler, benchmarks | ⚠️ Частично |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    KMP-READY БИБЛИОТЕКИ                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Networking:                                                                 │
│  ├── Ktor — официальная от JetBrains                                        │
│  ├── Apollo — для GraphQL                                                   │
│  └── expect/actual для платформенных особенностей                          │
│                                                                              │
│  Database:                                                                   │
│  ├── SQLDelight — SQL-first, генерирует Kotlin                             │
│  ├── Realm Kotlin — объектная БД                                           │
│  └── Settings — для простого key-value                                     │
│                                                                              │
│  DI:                                                                         │
│  ├── Koin — простой, популярный в KMP                                       │
│  ├── Kodein — более мощный                                                  │
│  └── Manual DI — для простых проектов                                       │
│                                                                              │
│  Testing:                                                                    │
│  ├── kotlin.test — официальный                                              │
│  ├── Kotest — мощный, многоплатформенный                                   │
│  └── MockK — для mocking (JVM)                                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Advanced (4 файла)

| № | Файл | Ключевые темы | Когда изучать |
|---|------|---------------|---------------|
| 21 | [[21-platform-apis]] | HealthKit/Fit, AR, ML | При необходимости |
| 22 | [[22-background-processing]] | Background refresh, WorkManager | При работе с background |
| 23 | [[23-app-distribution]] | App Store, Play Store, CI/CD | Перед релизом |
| 24 | [[24-security]] | Keychain/Keystore, biometrics | При работе с security |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    КОГДА ПЕРЕХОДИТЬ К ADVANCED?                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Platform APIs (21):                                                         │
│  └── Когда нужны специфичные функции (здоровье, AR, ML)                    │
│                                                                              │
│  Background Processing (22):                                                 │
│  └── Когда приложение должно работать в фоне                               │
│  └── Синхронизация данных, push notifications                              │
│                                                                              │
│  App Distribution (23):                                                      │
│  └── Перед первым релизом                                                   │
│  └── При настройке CI/CD                                                    │
│                                                                              │
│  Security (24):                                                              │
│  └── При хранении sensitive данных                                          │
│  └── При работе с аутентификацией                                           │
│  └── ОБЯЗАТЕЛЬНО для финансовых/медицинских приложений                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## С чего начать

### iOS разработчик изучает Android

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              ПУТЬ: iOS → Android                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Неделя 1: Основы                                                           │
│  ─────────────────                                                           │
│  01-memory-management.md                                                     │
│  ├── Фокус: GC вместо ARC                                                   │
│  ├── Ключевой shift: нет deinit, есть onCleared()                          │
│  └── Практика: создай memory leak и найди его LeakCanary                   │
│                                                                              │
│  02-lifecycle.md                                                             │
│  ├── Фокус: Activity/Fragment lifecycle                                     │
│  ├── Ключевой shift: configuration changes = пересоздание                  │
│  └── Практика: поверни экран и сохрани состояние                           │
│                                                                              │
│  Неделя 2: Async и данные                                                   │
│  ────────────────────────                                                    │
│  03-async-concurrency.md                                                     │
│  ├── Фокус: Coroutines вместо async/await                                  │
│  ├── Ключевой shift: suspend fun ≈ async func                              │
│  └── Практика: перепиши URLSession код на Ktor                             │
│                                                                              │
│  04-data-types.md                                                            │
│  ├── Фокус: нет struct, только class                                        │
│  ├── Ключевой shift: data class ≈ struct с ограничениями                   │
│  └── Практика: перепиши модели на Kotlin                                   │
│                                                                              │
│  Неделя 3: UI                                                                │
│  ──────────                                                                  │
│  05-declarative-ui.md                                                        │
│  ├── Фокус: Compose вместо SwiftUI                                          │
│  ├── Ключевой shift: @Composable function ≈ View struct                    │
│  └── Практика: перепиши простой экран на Compose                           │
│                                                                              │
│  Неделя 4: Инфраструктура                                                   │
│  ─────────────────────────                                                   │
│  17-build-systems.md — Gradle вместо Xcode                                  │
│  18-project-structure.md — модули вместо targets                            │
│                                                                              │
│  ЛОВУШКИ ДЛЯ iOS РАЗРАБОТЧИКА:                                              │
│  ──────────────────────────────                                              │
│  ✗ Не полагайся на onDestroy() как на deinit                               │
│  ✗ Не забывай про configuration changes                                     │
│  ✗ Gradle медленнее — привыкни                                              │
│  ✗ Fragments — сложно, используй Navigation Component                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Android разработчик изучает iOS

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              ПУТЬ: Android → iOS                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Неделя 1: Основы                                                           │
│  ─────────────────                                                           │
│  01-memory-management.md                                                     │
│  ├── Фокус: ARC вместо GC                                                   │
│  ├── Ключевой shift: weak/unowned ОБЯЗАТЕЛЬНЫ для избежания циклов        │
│  └── Практика: создай retain cycle и найди его в Instruments               │
│                                                                              │
│  02-lifecycle.md                                                             │
│  ├── Фокус: UIViewController lifecycle                                      │
│  ├── Ключевой shift: нет configuration changes!                            │
│  └── Практика: deinit вызывается детерминированно                          │
│                                                                              │
│  Неделя 2: Async и данные                                                   │
│  ────────────────────────                                                    │
│  03-async-concurrency.md                                                     │
│  ├── Фокус: Swift async/await                                               │
│  ├── Ключевой shift: async func ≈ suspend fun                              │
│  ├── Actors для thread safety                                               │
│  └── Практика: перепиши Retrofit код на URLSession                         │
│                                                                              │
│  04-data-types.md                                                            │
│  ├── Фокус: struct — value type!                                            │
│  ├── Ключевой shift: struct копируется, не ссылается                       │
│  └── Практика: почувствуй разницу struct vs class                          │
│                                                                              │
│  Неделя 3: UI                                                                │
│  ──────────                                                                  │
│  05-declarative-ui.md                                                        │
│  ├── Фокус: SwiftUI                                                         │
│  ├── Ключевой shift: View — struct, не function                            │
│  └── Практика: перепиши Compose экран на SwiftUI                           │
│                                                                              │
│  Неделя 4: Инфраструктура                                                   │
│  ─────────────────────────                                                   │
│  17-build-systems.md — Xcode вместо Gradle                                  │
│  18-project-structure.md — targets вместо modules                           │
│                                                                              │
│  ЛОВУШКИ ДЛЯ ANDROID РАЗРАБОТЧИКА:                                          │
│  ─────────────────────────────────                                           │
│  ✗ ОБЯЗАТЕЛЬНО используй [weak self] в closures                            │
│  ✗ struct ≠ data class (value type!)                                        │
│  ✗ Xcode — один IDE, привыкни                                               │
│  ✗ Нет xml layouts — только код или Storyboards                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Разработчик изучает KMP

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              ПУТЬ: Любая платформа → KMP                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ:                                                │
│  ────────────────────────────                                                │
│  • Знание Kotlin (хотя бы базовое)                                          │
│  • Понимание ОДНОЙ из платформ (iOS или Android)                            │
│  • Понимание концепции shared code                                          │
│                                                                              │
│  Неделя 1: Основы KMP                                                       │
│  ────────────────────                                                        │
│  • Структура KMP проекта (commonMain, iosMain, androidMain)                │
│  • expect/actual механизм                                                   │
│  • Gradle KMP plugin                                                         │
│                                                                              │
│  Материалы:                                                                  │
│  ├── [[kmp-overview]] — общий обзор                                      │
│  ├── 18-project-structure.md — структура проекта                            │
│  └── 17-build-systems.md — Gradle для KMP                                   │
│                                                                              │
│  Неделя 2: Особенности Kotlin/Native                                        │
│  ────────────────────────────────                                            │
│  01-memory-management.md                                                     │
│  ├── Фокус: новая memory model (1.7.20+)                                    │
│  ├── @SharedImmutable, @ThreadLocal (deprecated)                            │
│  └── Как GC работает в Kotlin/Native                                        │
│                                                                              │
│  03-async-concurrency.md                                                     │
│  ├── Фокус: Coroutines в KMP                                                │
│  ├── Dispatchers на разных платформах                                       │
│  └── Flow в shared code                                                      │
│                                                                              │
│  Неделя 3: Инфраструктура                                                   │
│  ─────────────────────────                                                   │
│  13-networking.md — Ktor                                                     │
│  14-database.md — SQLDelight                                                 │
│  15-dependency-injection.md — Koin                                          │
│                                                                              │
│  Неделя 4: UI (опционально)                                                 │
│  ───────────────────────────                                                 │
│  05-declarative-ui.md — Compose Multiplatform                               │
│  ├── Фокус: Compose на iOS (Skia)                                           │
│  ├── Ограничения на iOS                                                     │
│  └── Когда использовать native UI                                           │
│                                                                              │
│  КЛЮЧЕВЫЕ МОМЕНТЫ KMP:                                                       │
│  ──────────────────────                                                      │
│  ✓ Начните с бизнес-логики, не с UI                                        │
│  ✓ expect/actual только когда ДЕЙСТВИТЕЛЬНО нужно                          │
│  ✓ Тестируйте в commonTest                                                  │
│  ✗ Не пытайтесь сделать ВСЁ общим сразу                                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Связь с другими разделами

### Навигация по Knowledge Base

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    СВЯЗАННЫЕ РАЗДЕЛЫ                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│                         ┌─────────────────┐                                 │
│                         │  ЭТОТ РАЗДЕЛ    │                                 │
│                         │  Cross-Platform │                                 │
│                         └────────┬────────┘                                 │
│                                  │                                          │
│           ┌──────────────────────┼──────────────────────┐                   │
│           │                      │                      │                   │
│           ▼                      ▼                      ▼                   │
│  ┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐           │
│  │ [[ios-overview]]│   │[[android-overview]]│  │[[kmp-overview]]│         │
│  │                 │   │                 │   │                 │           │
│  │ • Swift         │   │ • Kotlin        │   │ • Shared code   │           │
│  │ • SwiftUI       │   │ • Compose       │   │ • expect/actual │           │
│  │ • UIKit         │   │ • Views         │   │ • Libraries     │           │
│  │ • Combine       │   │ • Coroutines    │   │ • Build setup   │           │
│  └─────────────────┘   └─────────────────┘   └─────────────────┘           │
│                                                                              │
│  ДОПОЛНИТЕЛЬНЫЕ СВЯЗИ:                                                       │
│  ─────────────────────                                                       │
│                                                                              │
│  [[architecture]]                                                            │
│  ├── Clean Architecture — применимо к обеим платформам                     │
│  ├── MVVM patterns — различия в реализации                                  │
│  └── Dependency Injection — подходы                                         │
│                                                                              │
│  [[networking]]                                                              │
│  ├── REST API design — общее                                                │
│  ├── GraphQL — Apollo Kotlin (KMP)                                          │
│  └── WebSocket — платформенные особенности                                  │
│                                                                              │
│  [[databases]]                                                               │
│  ├── SQLite fundamentals — основа для обеих платформ                       │
│  ├── ORM patterns — Core Data vs Room vs SQLDelight                        │
│  └── Migrations — подходы                                                   │
│                                                                              │
│  [[cs-fundamentals]]                                                        │
│  ├── Memory management theory                                               │
│  ├── Concurrency patterns                                                   │
│  └── Data structures                                                        │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Как использовать связи

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    СТРАТЕГИЯ НАВИГАЦИИ                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  СЦЕНАРИЙ 1: Изучаю новую концепцию                                         │
│  ───────────────────────────────────                                         │
│                                                                              │
│  Хочу понять memory management:                                              │
│  1. [[cs-fundamentals]] → теория GC vs RC                                   │
│  2. 01-memory-management.md → практические различия                         │
│  3. [[ios-overview]] → детали ARC в Swift                                   │
│  4. [[android-overview]] → детали GC в Android                              │
│                                                                              │
│  СЦЕНАРИЙ 2: Пишу KMP код                                                   │
│  ────────────────────────                                                    │
│                                                                              │
│  Нужно сделать networking:                                                   │
│  1. 13-networking.md → сравнение подходов                                   │
│  2. [[kmp-overview]] → Ktor setup                                        │
│  3. [[networking]] → общие паттерны                                         │
│                                                                              │
│  СЦЕНАРИЙ 3: Debugging проблемы                                             │
│  ──────────────────────────────                                              │
│                                                                              │
│  Memory leak на iOS:                                                         │
│  1. 01-memory-management.md → как найти                                     │
│  2. [[ios-overview]] → Instruments guide                                    │
│  3. 19-debugging.md → общие подходы                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Источники

### Официальная документация

#### Apple

| Ресурс | URL | Описание |
|--------|-----|----------|
| Swift Documentation | developer.apple.com/swift | Официальная документация Swift |
| SwiftUI Tutorials | developer.apple.com/tutorials/swiftui | Интерактивные туториалы |
| Human Interface Guidelines | developer.apple.com/design/human-interface-guidelines | Гайдлайны дизайна |
| WWDC Videos | developer.apple.com/wwdc | Видео с конференций |
| Swift Evolution | github.com/apple/swift-evolution | Предложения по развитию Swift |

#### Android / Google

| Ресурс | URL | Описание |
|--------|-----|----------|
| Android Developers | developer.android.com | Основная документация |
| Kotlin Documentation | kotlinlang.org/docs | Документация Kotlin |
| Jetpack Compose | developer.android.com/jetpack/compose | Compose документация |
| Material Design | material.io | Гайдлайны дизайна |
| Android Architecture | developer.android.com/topic/architecture | Архитектурные паттерны |

#### Kotlin Multiplatform

| Ресурс | URL | Описание |
|--------|-----|----------|
| KMP Documentation | kotlinlang.org/docs/multiplatform.html | Официальная документация |
| Compose Multiplatform | jetbrains.com/lp/compose-multiplatform | Compose для всех платформ |
| KMP Libraries | github.com/AaronLiu/awesome-kmp | Каталог библиотек |
| Kotlin Slack | kotlinlang.slack.com | Сообщество |

### Рекомендуемые книги

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         РЕКОМЕНДУЕМЫЕ КНИГИ                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  iOS:                                                                        │
│  ────                                                                        │
│  • "iOS Programming" — Big Nerd Ranch                                       │
│  • "Swift Programming" — Big Nerd Ranch                                     │
│  • "Thinking in SwiftUI" — objc.io                                          │
│  • "Advanced Swift" — objc.io                                               │
│                                                                              │
│  Android:                                                                    │
│  ────────                                                                    │
│  • "Android Programming" — Big Nerd Ranch                                   │
│  • "Kotlin in Action" — Dmitry Jemerov, Svetlana Isakova                   │
│  • "Jetpack Compose by Tutorials" — raywenderlich                           │
│                                                                              │
│  KMP:                                                                        │
│  ────                                                                        │
│  • "Kotlin Multiplatform by Tutorials" — raywenderlich                      │
│  • "Kotlin Coroutines Deep Dive" — Marcin Moskala                          │
│                                                                              │
│  Общее:                                                                      │
│  ──────                                                                      │
│  • "Clean Architecture" — Robert C. Martin                                  │
│  • "Design Patterns" — Gang of Four                                         │
│  • "Refactoring" — Martin Fowler                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Блоги и ресурсы сообщества

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         БЛОГИ И РЕСУРСЫ                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  iOS:                                                                        │
│  ────                                                                        │
│  • Swift by Sundell — swiftbysundell.com                                    │
│  • Hacking with Swift — hackingwithswift.com                                │
│  • NSHipster — nshipster.com                                                │
│  • objc.io — objc.io                                                        │
│  • raywenderlich — kodeco.com                                               │
│                                                                              │
│  Android:                                                                    │
│  ────────                                                                    │
│  • Android Developers Blog — android-developers.googleblog.com              │
│  • ProAndroidDev — proandroiddev.com                                        │
│  • Styling Android — blog.stylingandroid.com                                │
│  • raywenderlich — kodeco.com                                               │
│                                                                              │
│  KMP:                                                                        │
│  ────                                                                        │
│  • Touchlab Blog — touchlab.co/blog                                         │
│  • JetBrains Blog — blog.jetbrains.com                                      │
│  • KMP Weekly — kmpweekly.com                                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Чеклист готовности

### Самопроверка знаний

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ЧЕКЛИСТ: ГОТОВ ЛИ Я К CROSS-PLATFORM?                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ФУНДАМЕНТ (обязательно):                                                   │
│  ─────────────────────────                                                   │
│  [ ] Понимаю различия ARC vs GC                                             │
│  [ ] Понимаю lifecycle обеих платформ                                       │
│  [ ] Умею писать async код на обеих платформах                             │
│  [ ] Понимаю различия struct vs class vs data class                        │
│                                                                              │
│  UI (для full-stack mobile):                                                │
│  ────────────────────────────                                                │
│  [ ] Могу написать UI на SwiftUI                                            │
│  [ ] Могу написать UI на Jetpack Compose                                    │
│  [ ] Понимаю state management в обоих фреймворках                          │
│  [ ] Понимаю navigation в обоих фреймворках                                │
│                                                                              │
│  KMP (для shared code):                                                      │
│  ───────────────────────                                                     │
│  [ ] Понимаю expect/actual                                                  │
│  [ ] Могу настроить KMP проект                                              │
│  [ ] Знаю основные KMP библиотеки (Ktor, SQLDelight, Koin)                 │
│  [ ] Понимаю ограничения Kotlin/Native                                      │
│                                                                              │
│  РЕЗУЛЬТАТ:                                                                  │
│  ──────────                                                                  │
│  • Все [ ] в ФУНДАМЕНТ → можете начинать cross-platform                    │
│  • Все [ ] в UI → можете писать UI на обеих платформах                     │
│  • Все [ ] в KMP → готовы к production KMP                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Заключение

Этот раздел — ваш путеводитель по миру кросс-платформенной мобильной разработки. Вместо того чтобы запоминать сотни различий между iOS и Android, сфокусируйтесь на понимании **ПОЧЕМУ** каждая платформа работает именно так.

Начните с фундамента (файлы 01-04), затем переходите к UI и архитектуре (05-12), потом к инфраструктуре (13-20), и наконец к advanced темам (21-24) по мере необходимости.

Помните: цель не в том, чтобы стать экспертом в обеих платформах одновременно, а в том, чтобы понимать обе достаточно глубоко для эффективной работы с общим кодом и командами из разных платформ.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ФИНАЛЬНАЯ МЫСЛЬ                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  "Лучший кросс-платформенный разработчик — это тот, кто глубоко            │
│   понимает ОБЕИ платформы, а не тот, кто поверхностно знает                │
│   кросс-платформенный фреймворк."                                           │
│                                                                              │
│  Инвестируйте время в понимание платформ — это окупится.                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

---

## Связь с другими темами

**[[ios-overview]]** — Обзор iOS-платформы охватывает Swift, SwiftUI, UIKit, Combine и экосистему Apple. Заметка описывает архитектурные паттерны iOS-разработки, инструменты (Xcode, Instruments, SPM) и ключевые API. Понимание iOS как целостной экосистемы помогает оценить, какие части можно вынести в shared-код при кросс-платформенной разработке, а какие останутся platform-specific.

**[[android-overview]]** — Обзор Android-платформы включает Kotlin, Jetpack Compose, Android Views, Coroutines и экосистему Google. Заметка раскрывает Gradle build system, Jetpack-библиотеки и архитектурные компоненты (ViewModel, LiveData, Room). Сравнение с iOS в текущем файле показывает фундаментальные различия: система контролирует lifecycle на Android vs разработчик на iOS, GC vs ARC, открытая vs закрытая экосистема.

**[[kmp-overview]]** — Kotlin Multiplatform — это технология JetBrains для написания shared-кода на Kotlin с компиляцией в JVM (Android), Native (iOS) и JS (Web). Заметка описывает expect/actual, Gradle-конфигурацию, SKIE, Compose Multiplatform и стратегии шаринга кода. Это практическая реализация кросс-платформенного подхода, теоретические основы которого изложены в текущем overview-файле.

---

## Источники и дальнейшее чтение

- **Moskala M. (2021). *Effective Kotlin*.** — Содержит best practices для идиоматичного Kotlin-кода, который является основой KMP-разработки. Рекомендации по API design, error handling и concurrency помогают писать shared-код, одинаково эффективный на обеих платформах.
- **Meier R. (2022). *Professional Android*.** — Полное руководство по Android-платформе: от Activity lifecycle до Jetpack Compose. Необходимо для глубокого понимания Android-стороны кросс-платформенного сравнения.
- **Neuburg M. (2023). *iOS Programming Fundamentals*.** — Раскрывает основы iOS-разработки: Swift, UIKit, SwiftUI, Xcode и Apple-экосистему. Даёт фундамент для понимания iOS-стороны кросс-платформенного сравнения и помогает оценить различия в философии платформ.

*Последнее обновление: 2026-01-11*
