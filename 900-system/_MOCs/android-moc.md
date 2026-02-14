---
title: "Android MOC"
created: 2026-02-09
modified: 2026-02-09
type: moc
tags:
  - topic/android
  - type/moc
  - navigation
---
# Android MOC

> Полная карта Android-разработки: от архитектуры платформы до production-оптимизаций

**Путь обучения:** [[android-learning-path]]

---

## Рекомендуемый путь изучения

```
1. [[android-overview]]                — Карта раздела, общая картина платформы
         ↓
2. [[android-architecture]]            — Архитектура Android: от Linux до ART
         ↓
3. [[android-app-components]]          — Activity, Service, BR, ContentProvider
         ↓
4. [[android-activity-lifecycle]]      — Жизненный цикл Activity и его подводные камни
         ↓
5. [[android-context-internals]]       — Context: иерархия, ContextImpl, getSystemService
         ↓
6. [[android-ui-views]]                — View System: XML, ViewBinding, RecyclerView
         ↓
7. [[android-compose]]                 — Jetpack Compose: декларативный UI
         ↓
8. [[android-threading]]               — Main Thread, Coroutines, Dispatchers
         ↓
9. [[android-architecture-patterns]]   — MVVM, MVI, Clean Architecture
         ↓
10. [[android-data-persistence]]       — Обзор хранения данных: Room, DataStore, Files
         ↓
11. [[android-networking]]             — Retrofit, OkHttp, Ktor
         ↓
12. [[android-dependency-injection]]   — DI: обзор экосистемы фреймворков
         ↓
13. [[android-testing]]                — Unit, Integration, UI тесты
         ↓
14. [[android-gradle-fundamentals]]    — Gradle и Android Gradle Plugin
         ↓
15. [[android-performance-profiling]]  — Profiling: CPU, память, рендеринг
```

---

## Статьи по категориям

### Платформа и основы
- [[android-overview]] — карта раздела и точка входа в Android-разработку
- [[android-architecture]] — архитектура Android от Linux ядра через Binder/Zygote до ART
- [[android-app-components]] — четыре компонента приложения: Activity, Service, BR, ContentProvider
- [[android-manifest]] — AndroidManifest.xml: декларативная конфигурация приложения
- [[android-project-structure]] — структура проекта, модули, директории
- [[android-resources-system]] — система ресурсов: типы, квалификаторы, R класс

### Lifecycle и компоненты
- [[android-activity-lifecycle]] — состояния Activity, callbacks, savedInstanceState
- [[android-fragment-lifecycle]] — Fragment Lifecycle, ViewLifecycleOwner, FragmentManager
- [[android-context-internals]] — иерархия Context, ContextImpl, утечки через Activity Context
- [[android-intent-internals]] — Intent resolution, PendingIntent, Deep Links
- [[android-service-internals]] — Started/Bound/Foreground Service, Binder IPC, AIDL
- [[android-broadcast-internals]] — BroadcastReceiver, publish-subscribe, ограничения Android 8+
- [[android-content-provider-internals]] — ContentProvider: межпроцессный доступ к данным
- [[android-bundle-parcelable]] — Bundle, Parcelable, сериализация через Binder IPC

### UI: View System
- [[android-ui-views]] — XML Layouts, ViewBinding, RecyclerView, View-иерархия
- [[android-custom-view-fundamentals]] — создание Custom View: от наследования до Canvas
- [[android-view-measurement]] — onMeasure, MeasureSpec, LayoutParams
- [[android-view-rendering-pipeline]] — rendering pipeline: measure, layout, draw, GPU
- [[android-recyclerview-internals]] — четырёхуровневый кэш, DiffUtil, ViewHolder pattern
- [[android-window-system]] — PhoneWindow, DecorView, WindowManager, Surface, SurfaceFlinger
- [[android-touch-handling]] — обработка касаний: MotionEvent, dispatch, Compose pointerInput
- [[android-canvas-drawing]] — 2D-рисование: Canvas, Paint, Path, трансформации
- [[android-graphics-apis]] — графические API: OpenGL ES, Vulkan, выбор уровня абстракции
- [[android-animations]] — от ValueAnimator до Compose Transition, Choreographer и VSYNC

### UI: Jetpack Compose
- [[android-compose]] — декларативный UI: Composable, State, Recomposition
- [[android-compose-internals]] — внутреннее устройство: Compiler Plugin, Slot Table, три фазы
- [[android-state-management]] — StateFlow, SharedFlow, Channel и Compose State

### Навигация
- [[android-navigation]] — полный гайд: Fragment, Jetpack Navigation, Compose Navigation
- [[android-navigation-evolution]] — эволюция навигации от Activity+Intent до Type-safe Navigation 3

### Архитектура приложения
- [[android-architecture-patterns]] — MVVM, MVI, Clean Architecture и UDF
- [[android-architecture-evolution]] — эволюция от God Activity к Compose + MVI
- [[android-viewmodel-internals]] — как ViewModel переживает configuration change
- [[android-repository-pattern]] — Single Source of Truth и Offline-First
- [[android-modularization]] — multi-module архитектура для масштабируемости

### Dependency Injection
- [[android-dependency-injection]] — навигационный хаб по DI-экосистеме Android/KMP
- [[android-hilt-deep-dive]] — Hilt: официальная DI от Google поверх Dagger 2
- [[android-dagger-deep-dive]] — Dagger 2: compile-time DI, полный контроль графа
- [[android-koin-deep-dive]] — Koin: Kotlin-native runtime DI для Android и KMP
- [[android-kotlin-inject-deep-dive]] — kotlin-inject: compile-time DI с KMP поддержкой
- [[android-metro-deep-dive]] — Metro: compiler plugin DI от Zac Sweers (2025)
- [[android-kodein-deep-dive]] — Kodein: runtime DI с множественными контейнерами для SDK
- [[android-manual-di-alternatives]] — Manual DI, Anvil (maintenance mode), Toothpick

### Асинхронность и многопоточность
- [[android-threading]] — Main Thread, Kotlin Coroutines, Dispatchers
- [[android-handler-looper]] — Handler, Looper, MessageQueue: фундамент async в Android
- [[android-async-evolution]] — эволюция async: от Thread/Handler до Coroutines (2008-2025)
- [[android-asynctask-deprecated]] — AsyncTask: история, проблемы и уроки
- [[android-executors]] — Executors и ThreadPoolExecutor в Android
- [[android-rxjava]] — RxJava и RxAndroid: реактивный подход
- [[android-coroutines-mistakes]] — 10 типичных ошибок с Kotlin Coroutines в Android
- [[android-background-work]] — WorkManager, Foreground Services, Doze, App Standby

### Данные и сеть
- [[android-data-persistence]] — навигационный хаб: обзор и выбор подхода к хранению данных
- [[android-room-deep-dive]] — Room: compile-time ORM, Entity, DAO, Relations, TypeConverters
- [[android-room-migrations]] — миграции Room: AutoMigration, ручные, тестирование схем
- [[android-room-performance]] — производительность Room: индексы, WAL, batch-операции, Paging
- [[android-datastore-guide]] — DataStore: Preferences, Proto, миграция с SharedPreferences
- [[android-networking]] — Retrofit, OkHttp, Ktor: HTTP-клиенты и сериализация

### Build и CI/CD
- [[android-gradle-fundamentals]] — Gradle и AGP: task graph, конфигурация, плагины
- [[android-build-evolution]] — эволюция систем сборки: от Ant до Gradle
- [[android-compilation-pipeline]] — от исходников до APK: kotlinc, D8, R8, AAPT
- [[android-apk-aab]] — APK vs AAB, подпись, оптимизация размера, App Distribution
- [[android-proguard-r8]] — R8: code shrinking, obfuscation, bytecode optimization
- [[android-dependencies]] — управление зависимостями: Version Catalogs, BOM, conflicts
- [[android-ci-cd]] — CI/CD: GitHub Actions, Fastlane, Firebase Test Lab

### Performance
- [[android-performance-profiling]] — Android Studio Profiler: CPU, Memory, Network, GPU
- [[android-app-startup-performance]] — оптимизация старта: Zygote, Baseline Profiles, Macrobenchmark
- [[android-memory-leaks]] — паттерны утечек, LeakCanary, WeakReference
- [[android-process-memory]] — процессы, LMK, управление памятью на уровне ОС

### Тестирование и безопасность
- [[android-testing]] — Unit/Integration/UI тесты: JUnit, MockK, Espresso, Robolectric
- [[android-permissions-security]] — Runtime Permissions, EncryptedSharedPreferences, Keystore
- [[android-notifications]] — система уведомлений: каналы, PendingIntent, Android 13+ permissions

---

## Ключевые концепции

| Концепция | Суть | Подробнее |
|-----------|------|-----------|
| ART (Android Runtime) | Виртуальная машина, выполняющая DEX-байткод с AOT + JIT компиляцией | [[android-architecture]] |
| Lifecycle | State machine компонентов: onCreate → onResume → onPause → onDestroy | [[android-activity-lifecycle]] |
| Recomposition | Повторный вызов composable-функций при изменении State | [[android-compose-internals]] |
| Unidirectional Data Flow | Состояние течёт вниз, события — вверх (MVI, Compose) | [[android-architecture-patterns]] |
| Binder IPC | Механизм межпроцессного взаимодействия (Intent, ContentProvider, AIDL) | [[android-intent-internals]] |
| Handler/Looper | Event loop Main Thread: MessageQueue обрабатывает сообщения по VSYNC | [[android-handler-looper]] |
| ViewHolder Pattern | Переиспользование View в списках: inflation 1 раз, binding N раз | [[android-recyclerview-internals]] |
| Structured Concurrency | Coroutine scope привязан к lifecycle; отмена каскадируется | [[android-coroutines-mistakes]] |
| R8 Shrinking | Удаление неиспользуемого кода + обфускация + bytecode optimization | [[android-proguard-r8]] |
| WorkManager | Гарантированная фоновая работа с constraints (сеть, зарядка) | [[android-background-work]] |

---

## Связанные области

- [[ios-moc]] — параллельное изучение iOS для кросс-платформенного понимания мобильной разработки
- [[cross-platform-moc]] — Flutter, React Native, KMP и другие кросс-платформенные решения
- [[kmp-moc]] — Kotlin Multiplatform: shared бизнес-логика для Android и iOS
- [[jvm-moc]] — JVM платформа: фундамент, на котором работает Android Runtime (ART)
