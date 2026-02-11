---
title: "Android: карта раздела"
created: 2025-12-17
modified: 2026-01-05
type: overview
area: android
confidence: high
tags:
  - topic/android
  - topic/kotlin
  - type/overview
  - level/beginner
cs-foundations: [mobile-platform-architecture, application-sandbox, component-lifecycle]
related:
  - "[[mobile-ai-ml-guide]]"
  - "[[os-overview]]"
  - "[[kotlin-basics]]"
  - "[[jvm-overview]]"
  - "[[kmp-overview]]"
---

# Android: карта раздела

Android — мобильная операционная система на базе модифицированного ядра Linux. В отличие от десктопного Linux, Android использует собственную систему управления процессами, специализированный runtime (ART) вместо стандартной JVM, и уникальную модель приложений с компонентами вместо единого main().

> **Prerequisites:**
> - Базовое понимание программирования (ООП, Java/Kotlin)
> - [[os-overview]] — процессы, память, потоки на уровне ОС (полезно)
> - Понимание что такое мобильное приложение

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Моё приложение контролирует свой lifecycle" | Система (Android) контролирует. Activity может быть убита в любой момент для освобождения памяти. Приложение должно быть готово к пересозданию |
| "ViewModel сохраняет данные при process death" | Нет! ViewModel переживает только config changes. Для process death нужен SavedStateHandle или persistent storage |
| "onDestroy() всегда вызывается" | Не гарантируется при process death. Система убивает процесс без предупреждения |
| "Compose заменил XML — больше не нужно знать View system" | 70%+ приложений используют XML или гибридный подход. View system знания критичны для legacy и interop |
| "Coroutines автоматически отменяются" | Только в правильных scopes. Без lifecycleScope/viewModelScope — memory leaks и краши |

---

## CS-фундамент

| CS-концепция | Применение в Android |
|--------------|---------------------|
| **Process lifecycle** | Activity lifecycle callbacks — система управляет памятью через процессы |
| **State machine** | Activity states (CREATED→STARTED→RESUMED), Configuration state machine |
| **Message queue** | Handler/Looper — Main Thread message processing |
| **Garbage collection** | ART GC — memory management, heap limits, memory leaks |
| **Component model** | Activity, Service, BroadcastReceiver, ContentProvider — entry points |
| **Sandbox isolation** | App sandbox — каждое приложение в своём процессе с уникальным UID |
| **IPC mechanisms** | Binder — высокоэффективный inter-process communication |
| **Declarative UI** | Jetpack Compose — functional UI, immutability, recomposition |

---

## Зачем разработчику глубоко понимать Android

Многие разработчики знают "как написать приложение", но не понимают "почему оно работает именно так". Это приводит к типичным проблемам:

**Почему приложение крашится при повороте экрана?** Потому что Android пересоздаёт Activity, а разработчик хранил данные в полях Activity вместо ViewModel. Понимание жизненного цикла объясняет, почему state management критически важен.

**Почему фоновая задача не выполняется?** Потому что система убила процесс приложения для освобождения памяти. Low Memory Killer работает агрессивно на мобильных устройствах. Понимание процессной модели объясняет, зачем нужны WorkManager и foreground services.

**Почему UI тормозит?** Потому что тяжёлая работа выполняется на Main Thread, который должен рендерить 60 кадров в секунду. 16ms на кадр — это мало. Понимание threading модели объясняет, почему coroutines и фоновые потоки необходимы.

---

## Структура раздела

```
┌─────────────────────────────────────────────────────────────────┐
│                         ANDROID                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ФУНДАМЕНТ (сначала читать это)                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Архитектура     │  │ Компоненты      │  │ Процессы и      │ │
│  │ системы         │  │ приложения      │  │ память          │ │
│  │ ART, Zygote     │  │ Activity,       │  │ LMK, heap       │ │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘ │
│           │                    │                    │          │
│           ▼                    ▼                    ▼          │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              ЖИЗНЕННЫЙ ЦИКЛ ACTIVITY                         ││
│  │  onCreate → onStart → onResume ⟷ onPause → onStop → onDestroy││
│  └─────────────────────────────────────────────────────────────┘│
│           │                    │                    │          │
│           ▼                    ▼                    ▼          │
│  UI                                                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ View System     │  │ Jetpack Compose │  │ Navigation      │ │
│  │ XML, ViewBinding│  │ Declarative UI  │  │ Deep Links      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  ДАННЫЕ И СЕТЬ                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Persistence     │  │ Networking      │  │ Threading       │ │
│  │ Room, DataStore │  │ Retrofit, Ktor  │  │ Coroutines      │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  АРХИТЕКТУРА И КАЧЕСТВО                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Architecture    │  │ DI              │  │ Testing         │ │
│  │ MVVM, Clean     │  │ Hilt, Koin      │  │ Unit, UI tests  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  ARCHITECTURE DEEP DIVE                                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Evolution       │  │ ViewModel       │  │ State Mgmt      │ │
│  │ MVP→MVVM→MVI    │  │ Internals       │  │ Flow, Compose   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ Repository      │  │ Modularization  │                      │
│  │ Pattern, SSOT   │  │ Modules, APIs   │                      │
│  └─────────────────┘  └─────────────────┘                      │
│                                                                 │
│  СИСТЕМА                                                        │
│  ┌─────────────────┐  ┌─────────────────┐                      │
│  │ Background Work │  │ Permissions     │                      │
│  │ WorkManager     │  │ Security        │                      │
│  └─────────────────┘  └─────────────────┘                      │
│                                                                 │
│  UNDER THE HOOD (Deep Dive)                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Bundle/Parcel   │  │ Context         │  │ Intent          │ │
│  │ Internals       │  │ Internals       │  │ Internals       │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Fragment        │  │ Service         │  │ Memory Leaks    │ │
│  │ Lifecycle       │  │ Internals       │  │ & Detection     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
│  UI DEEP DIVE                                                   │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ RecyclerView    │  │ Window System   │  │ Animations      │ │
│  │ Internals       │  │ DecorView, WMS  │  │ Choreographer   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐                                            │
│  │ Graphics APIs   │                                            │
│  │ OpenGL, Vulkan  │                                            │
│  └─────────────────┘                                            │
│                                                                 │
│  SYSTEM INTERNALS                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ ContentProvider │  │ Broadcast       │  │ Notifications   │ │
│  │ Internals       │  │ Internals       │  │ Channels, NMS   │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐                                            │
│  │ App Startup     │                                            │
│  │ Baseline Prof.  │                                            │
│  └─────────────────┘                                            │
│                                                                 │
│  BUILD SYSTEM (Under the Hood)                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Gradle & AGP   │  │ Compilation     │  │ APK/AAB         │ │
│  │ Build variants  │  │ D8, R8, DEX    │  │ Signing, Split  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Материалы раздела

### Фундамент (читать в этом порядке)

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-architecture]] | ART vs JVM, Zygote, системные сервисы | [[os-processes-threads]], [[jvm-basics-history]] |
| [[android-app-components]] | Activity, Service, BroadcastReceiver, ContentProvider | [[os-processes-threads]] |
| [[android-activity-lifecycle]] | Жизненный цикл, состояния, конфигурации | [[android-app-components]] |
| [[android-process-memory]] | Процессы, приоритеты, Low Memory Killer | [[os-memory-management]], [[jvm-gc-tuning]] |

### UI и взаимодействие

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-ui-views]] | View system, layouts, ViewBinding | [[android-activity-lifecycle]] |
| [[android-compose]] | Declarative UI, State, recomposition | [[kotlin-basics]], [[kotlin-functional]] |
| [[android-threading]] | Main thread, coroutines, Dispatchers | [[kotlin-coroutines]], [[os-scheduling]] |

### Асинхронная работа (Deep Dive)

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-async-evolution]] | Хронология подходов 2008-2025, decision tree | [[android-threading]] |
| [[android-handler-looper]] | Looper, MessageQueue, Main Thread internals | [[os-processes-threads]] |
| [[android-asynctask-deprecated]] | Почему deprecated, миграция | [[android-async-evolution]] |
| [[android-executors]] | ThreadPool, ExecutorService | [[os-scheduling]] |
| [[android-rxjava]] | RxJava 2/3, operators, lifecycle | [[kotlin-flow]] |
| [[android-coroutines-mistakes]] | 10 anti-patterns, debugging | [[kotlin-coroutines]] |

### Данные

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-data-persistence]] | Room, DataStore, файлы | [[database-design-optimization]] |
| [[android-networking]] | Retrofit, OkHttp, сериализация | [[kotlin-coroutines]] |

### Архитектура приложений (Deep Dive)

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-architecture-patterns]] | MVVM, MVI, Clean Architecture | [[design-patterns]], [[clean-code-solid]] |
| [[android-architecture-evolution]] | Эволюция: God Activity → MVP → MVVM → MVI | [[android-architecture-patterns]] |
| [[android-viewmodel-internals]] | ViewModelStore, SavedStateHandle, scopes | [[android-activity-lifecycle]] |
| [[android-state-management]] | StateFlow vs SharedFlow vs Channel, Compose state | [[kotlin-coroutines]] |
| [[android-repository-pattern]] | SSOT, caching strategies, offline-first | [[android-data-persistence]] |
| [[android-modularization]] | Feature modules, Convention Plugins, API modules | [[android-architecture-patterns]] |

### Навигация и DI

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-navigation-evolution]] | Обзор всех подходов навигации 2008-2025 | [[android-navigation]] |
| [[android-navigation]] | Все подходы: Compose, Navigation Component, Fragments, Activities | [[android-activity-lifecycle]] |
| [[android-dependency-injection]] | Hilt, Koin, Manual DI | [[android-architecture-patterns]] |

### Фоновая работа и безопасность

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-background-work]] | WorkManager, Foreground Services, Doze | [[android-process-memory]] |
| [[android-permissions-security]] | Runtime Permissions, Secure Storage | [[android-data-persistence]] |
| [[android-testing]] | Unit, Integration, UI тесты | [[android-architecture-patterns]] |

### Build System (Under the Hood)

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-build-evolution]] | Эволюция от Ant к Gradle, почему Gradle победил | [[android-gradle-fundamentals]] |
| [[android-gradle-fundamentals]] | Gradle basics, AGP, tasks, variants, caching | [[android-project-structure]] |
| [[android-project-structure]] | Source sets, модули, Version Catalogs | [[android-manifest]] |
| [[android-manifest]] | Структура, компоненты, permissions, manifest merger | [[android-app-components]] |
| [[android-resources-system]] | Ресурсы, qualifiers, R class, AAPT2, локализация | [[android-compilation-pipeline]] |
| [[android-compilation-pipeline]] | Pipeline: Source → Bytecode → DEX → APK | [[android-proguard-r8]] |
| [[android-proguard-r8]] | R8, shrinking, obfuscation, keep rules | [[android-apk-aab]] |
| [[android-apk-aab]] | APK структура, AAB, Split APKs, signing | [[android-dependencies]] |
| [[android-dependencies]] | Dependency resolution, BOM, Version Catalogs | [[android-gradle-fundamentals]] |

### Under the Hood (Deep Dive)

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-bundle-parcelable]] | Bundle/Parcel binary format, Binder buffer, @Parcelize | [[android-activity-lifecycle]], [[android-intent-internals]] |
| [[android-memory-leaks]] | Leak patterns, LeakCanary, WeakReference, prevention | [[android-process-memory]], [[android-handler-looper]] |
| [[android-context-internals]] | Context hierarchy, ContextImpl, Application vs Activity context | [[android-app-components]], [[android-activity-lifecycle]] |
| [[android-intent-internals]] | Intent resolution, IntentFilter matching, PendingIntent, Deep Links | [[android-app-components]], [[android-navigation]] |
| [[android-fragment-lifecycle]] | Fragment lifecycle vs View lifecycle, FragmentManager, commit variants | [[android-activity-lifecycle]], [[android-navigation]] |
| [[android-service-internals]] | Started vs Bound, Foreground Service types (Android 14+), AIDL | [[android-background-work]], [[android-app-components]] |

### UI Deep Dive

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-recyclerview-internals]] | 4-level cache, DiffUtil, GapWorker prefetch | [[android-ui-views]], [[android-view-rendering-pipeline]] |
| [[android-window-system]] | PhoneWindow, DecorView, WMS, Surface, Edge-to-edge | [[android-view-rendering-pipeline]], [[android-activity-lifecycle]] |
| [[android-animations]] | Property Animation, Choreographer, Compose Animation, spring physics | [[android-view-rendering-pipeline]], [[android-compose]] |
| [[android-graphics-apis]] | OpenGL ES, Vulkan, GPU rendering pipeline | [[android-view-rendering-pipeline]], [[android-canvas-drawing]] |

### System Internals

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-content-provider-internals]] | ContentResolver dispatch, UriMatcher, FileProvider, App Startup hook | [[android-app-components]], [[android-app-startup-performance]] |
| [[android-broadcast-internals]] | Normal vs Ordered, AMS dispatch, Android 8+ restrictions, goAsync() | [[android-app-components]], [[android-handler-looper]] |
| [[android-notifications]] | NotificationChannel, NMS pipeline, PendingIntent, POST_NOTIFICATIONS | [[android-service-internals]], [[android-permissions-security]] |
| [[android-app-startup-performance]] | Cold/Warm/Hot start, Baseline Profiles, Macrobenchmark, Perfetto | [[android-compilation-pipeline]], [[android-content-provider-internals]] |

### DevOps & CI/CD

| Материал | Что узнаете | Связан с |
|----------|-------------|----------|
| [[android-ci-cd]] | GitHub Actions, Fastlane, Play Store automation, testing pipelines | [[android-gradle-fundamentals]] |

---

## Android vs Desktop/Server: ключевые отличия

| Аспект | Desktop/Server | Android |
|--------|----------------|---------|
| **Жизненный цикл** | Приложение живёт пока не закрыто | Система может убить в любой момент |
| **Память** | Гигабайты RAM | 2-8 GB на всё устройство |
| **CPU** | Всегда доступен | Ограничен для экономии батареи |
| **Точка входа** | main() | Компоненты (Activity, Service, ...) |
| **UI поток** | Опционально | Обязателен, 16ms на кадр |
| **Фоновая работа** | Свободно | Жёстко ограничена (Doze, App Standby) |

---

## Проверь себя

<details>
<summary>1. Почему Android может убить процесс приложения в любой момент?</summary>

**Ответ:** Android работает на устройствах с ограниченными ресурсами. Когда системе не хватает памяти, она убивает фоновые процессы по приоритету (LMK — Low Memory Killer). Поэтому приложение должно сохранять состояние и корректно обрабатывать lifecycle callbacks. Это не ошибка, а дизайн системы.

</details>

<details>
<summary>2. Чем Activity отличается от Fragment?</summary>

**Ответ:**
- **Activity:** Точка входа для взаимодействия с пользователем. Хостит UI, получает Intent. Один Activity = один экран (обычно).
- **Fragment:** Переиспользуемая часть UI внутри Activity. Свой lifecycle, но зависит от хостящей Activity. Используется для модульности и адаптации под разные экраны.

</details>

<details>
<summary>3. Зачем нужен Main Thread (UI Thread)?</summary>

**Ответ:** Android UI toolkit не thread-safe. Все операции с UI (обновление View, обработка ввода) должны выполняться в одном потоке — Main Thread. Если блокировать Main Thread (тяжёлые вычисления, сеть), приложение "зависнет" и система покажет ANR (Application Not Responding). Тяжёлые операции — в фоновые потоки/корутины.

</details>

---

## Связь с операционными системами

Android построен на Linux, но значительно модифицирован:

```
┌─────────────────────────────────────────────────────────────────┐
│                    КАК ANDROID СВЯЗАН С ОС                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Linux Kernel                Android                            │
│  ────────────                 ───────                           │
│  Процессы            ←───→   Каждое приложение = процесс        │
│  fork()              ←───→   Zygote fork() для новых apps       │
│  OOM Killer          ←───→   Low Memory Killer (более агрессивный)│
│  Scheduler           ←───→   + cgroups для foreground/background │
│  Virtual Memory      ←───→   + per-app heap limits              │
│                                                                 │
│  JVM                         ART (Android Runtime)              │
│  ───                         ────────────────────               │
│  JIT compilation     ←───→   AOT + JIT (Profile-guided)         │
│  Garbage Collection  ←───→   Concurrent GC (оптимизирован)      │
│  Bytecode            ←───→   DEX bytecode (компактнее)          │
│                                                                 │
│  Kotlin/JVM                  Kotlin/Android                     │
│  ──────────                  ──────────────                     │
│  Coroutines          ←───→   + Dispatchers.Main для UI          │
│  Flow                ←───→   + lifecycle-aware collection       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Подробнее о базовых концепциях ОС — в [[os-overview]].

---

## Числа, которые нужно знать

| Метрика | Значение | Почему важно |
|---------|----------|--------------|
| Frame time | 16ms (60 FPS) | Превышение = UI jank |
| App startup (cold) | <500ms желательно | Пользователь ждёт |
| Heap limit | 128-512MB (зависит от устройства) | OutOfMemoryError |
| Background execution | ~10 min после ухода в фон | Doze убивает долгие задачи |
| Activity recreation | При любом config change | Нужен state management |

---

## С чего начать

**Если вы новичок в Android:** Начните с [[android-architecture]] для понимания того, как устроена система. Затем [[android-app-components]] и [[android-activity-lifecycle]] — это фундамент, без которого невозможно писать надёжные приложения.

**Если вы знаете основы, но хотите глубже:** [[android-process-memory]] объяснит, как система управляет ресурсами и почему приложения "умирают". [[android-threading]] покажет правильную работу с асинхронностью.

**Если вы переходите с backend/desktop:** Обратите внимание на [[android-activity-lifecycle]] — это главное отличие от серверной разработки. Понимание того, что ваш код может быть прерван в любой момент, меняет подход к архитектуре.

---

## Терминология раздела

| Термин | Значение |
|--------|----------|
| **ART** | Android Runtime — виртуальная машина для запуска приложений |
| **DEX** | Dalvik Executable — формат байткода Android |
| **Zygote** | Процесс-шаблон, от которого fork'аются все приложения |
| **Activity** | Экран приложения с UI |
| **Fragment** | Переиспользуемая часть UI внутри Activity |
| **Intent** | Сообщение для запуска компонентов или передачи данных |
| **Context** | Доступ к ресурсам системы и приложения |
| **LMK** | Low Memory Killer — убивает процессы при нехватке памяти |
| **ANR** | Application Not Responding — UI заблокирован >5 секунд |
| **Doze** | Режим энергосбережения, ограничивающий фоновую активность |
| **Main Thread** | Поток UI, он же UI Thread |
| **Configuration Change** | Изменение конфигурации (поворот, язык, размер) |
| **Gradle** | Система сборки Android проектов |
| **AGP** | Android Gradle Plugin — плагин Gradle для Android |
| **APK** | Android Package — установочный пакет приложения |
| **AAB** | Android App Bundle — формат публикации для Google Play |
| **R8** | Компилятор для shrinking, obfuscation, optimization |
| **DEX** | Dalvik Executable — формат байткода для ART |
| **Bundle** | Контейнер key-value пар на базе ArrayMap для передачи данных между компонентами |
| **Parcelable** | Интерфейс высокопроизводительной сериализации для IPC через Binder |
| **Fragment** | Переиспользуемая часть UI внутри Activity со своим lifecycle |
| **NotificationChannel** | Канал уведомлений (Android 8+), контролирует важность и поведение |
| **ContentResolver** | Клиент для доступа к ContentProvider через URI |
| **Baseline Profile** | Предкомпилированный AOT-профиль горячих методов для ускорения startup |
| **Choreographer** | Системный компонент для синхронизации анимаций с VSYNC |

---

## Связи

**Фундамент:**
- [[os-overview]] — Android построен на Linux kernel, понимание процессов/памяти объясняет lifecycle и memory management
- [[os-processes-threads]] — каждое приложение = отдельный процесс, UI Thread и Worker threads

**Компоненты приложения:**
- [[android-activity-lifecycle]] — самый важный концепт: как Activity живёт и умирает
- [[android-app-components]] — Activity, Service, BroadcastReceiver, ContentProvider
- [[android-compose]] — современный декларативный UI вместо XML Views

**Архитектура:**
- [[android-architecture]] — слои приложения (UI, Domain, Data)
- [[android-architecture-patterns]] — MVVM, MVI, Clean Architecture
- [[android-architecture-evolution]] — эволюция: God Activity → MVP → MVVM → MVI → Compose
- [[android-viewmodel-internals]] — как ViewModel переживает configuration changes
- [[android-state-management]] — StateFlow vs SharedFlow vs Channel, Compose state
- [[android-repository-pattern]] — SSOT, caching strategies, offline-first
- [[android-modularization]] — feature modules, Convention Plugins, API modules

**Практика:**
- [[android-navigation-evolution]] — обзор эволюции навигации
- [[android-navigation]] — навигация между экранами (все подходы)
- [[android-data-persistence]] — хранение данных (Room, DataStore)
- [[android-networking]] — сетевые запросы (Retrofit, OkHttp)

**Асинхронность:**
- [[android-async-evolution]] — полный обзор всех подходов к асинхронности (2008-2025)
- [[android-handler-looper]] — низкоуровневый механизм Main Thread
- [[android-coroutines-mistakes]] — типичные ошибки при работе с корутинами

**Under the Hood (Deep Dive):**
- [[android-bundle-parcelable]] — Bundle/Parcel internals, Binder buffer, savedInstanceState
- [[android-memory-leaks]] — утечки памяти, LeakCanary, Reference types, prevention
- [[android-context-internals]] — иерархия Context, ContextImpl, какой Context для чего
- [[android-intent-internals]] — Intent resolution, PendingIntent, Deep Links/App Links
- [[android-fragment-lifecycle]] — Fragment lifecycle, FragmentManager, commit variants
- [[android-service-internals]] — Started/Bound lifecycle, Foreground Service types

**UI Deep Dive:**
- [[android-recyclerview-internals]] — 4-level cache, DiffUtil, prefetch, shared pool
- [[android-window-system]] — PhoneWindow, DecorView, WMS, Surface, edge-to-edge
- [[android-animations]] — Property Animation, Choreographer, Compose Animation, spring physics
- [[android-graphics-apis]] — OpenGL ES, Vulkan, GPU rendering

**System Internals:**
- [[android-content-provider-internals]] — ContentResolver dispatch, FileProvider, App Startup hook
- [[android-broadcast-internals]] — Normal/Ordered, AMS dispatch, Android 8+ restrictions
- [[android-notifications]] — NotificationChannel, NMS pipeline, POST_NOTIFICATIONS
- [[android-app-startup-performance]] — Cold/Warm/Hot start, Baseline Profiles, Macrobenchmark

**Build System:**
- [[android-build-evolution]] — эволюция систем сборки: Ant → Maven → Gradle
- [[android-gradle-fundamentals]] — Gradle и Android Gradle Plugin под капотом
- [[android-compilation-pipeline]] — полный pipeline: Source → DEX → APK
- [[android-proguard-r8]] — code shrinking, obfuscation, оптимизация R8
- [[android-apk-aab]] — форматы пакетов, подпись, distribution

---

## Связи с другими разделами

```
ANDROID РАЗРАБОТЧИКУ ПОЛЕЗНО ЗНАТЬ:
────────────────────────────────────

[[jvm-overview]]           ← ART основан на JVM концепциях
   │
   ├── [[jvm-gc-tuning]]   ← Понимание GC помогает с memory leaks
   └── [[jvm-memory-model]] ← Важно для многопоточности

[[kotlin-overview]]        ← Kotlin — основной язык Android
   │
   ├── [[kotlin-coroutines]] ← Асинхронность
   └── [[kotlin-flow]]       ← Реактивные потоки

[[kmp-overview]]        ← Кросс-платформенная разработка
   │
   └── [[kmp-android-integration]] ← Интеграция KMP в Android

[[architecture-overview]]  ← Паттерны проектирования
   │
   ├── [[api-design]]      ← REST, GraphQL
   └── [[caching-strategies]] ← Кэширование данных

[[devops-overview]]        ← CI/CD для Android
   │
   ├── [[ci-cd-pipelines]] ← GitHub Actions, Fastlane
   └── [[docker-for-developers]] ← Containerized builds
```

| Раздел | Как связан с Android | Что даёт |
|--------|---------------------|----------|
| [[jvm-overview]] | ART = Android Runtime на базе JVM | Понимание памяти, GC |
| [[kotlin-overview]] | Kotlin = основной язык | Coroutines, Flow |
| [[kmp-overview]] | KMP для shared code | 60-80% общего кода |
| [[cs-fundamentals-overview]] | DSA для интервью | Подготовка к собеседованиям |
| [[networking-overview]] | HTTP, REST, GraphQL | API интеграция |

---

## Источники

- [Guide to App Architecture - Android Developers](https://developer.android.com/topic/architecture) — официальное руководство по архитектуре
- [Recommendations for Android Architecture](https://developer.android.com/topic/architecture/recommendations) — best practices от Google
- [Modern Android App Architecture Pathway](https://developer.android.com/courses/pathways/android-architecture) — курс по современной архитектуре
- [MVVM with Clean Architecture - Toptal](https://www.toptal.com/android/android-apps-mvvm-with-clean-architecture) — практическое руководство

---

## Источники и дальнейшее чтение

- Meier (2022). *Professional Android*. — наиболее полное современное руководство по Android-разработке, охватывающее все ключевые компоненты от Activity lifecycle до WorkManager, Compose и модуляризации.
- Phillips et al. (2022). *Android Programming: The Big Nerd Ranch Guide*. — пошаговое введение в Android-разработку с Kotlin, идеально для систематизации знаний и заполнения пробелов в понимании компонентной модели.
- Vasavada (2019). *Android Internals*. — системный взгляд на Android: ART, Zygote, Binder IPC, process model и memory management. Даёт глубокое понимание того, почему Android работает именно так, а не иначе.

---

*Проверено: 2026-01-09 | На основе официальной документации Android и Deep Research*
