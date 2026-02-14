---
title: "Android: путь обучения"
created: 2026-02-10
modified: 2026-02-14
type: guide
tags:
  - topic/android
  - type/guide
  - navigation
  - learning-path
---

# Android: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

## Рекомендуемый темп

2-3 файла в день (~60-90 минут). Каждый 5-й день — повторение изученного.

---

## Уровень 1: Основы (Beginner)
> Цель: Понять архитектуру Android, жизненный цикл компонентов и базовые концепции платформы
> Время: ~4.5 часа (9 файлов)

- [ ] [[android-overview]] — карта раздела и точка входа в Android-разработку ⏱ 30m
- [ ] [[android-architecture]] — архитектура Android от Linux ядра через Binder/Zygote до ART ⏱ 25m
- [ ] [[android-project-structure]] — структура проекта, модули, директории ⏱ 35m
- [ ] [[android-manifest]] — AndroidManifest.xml: декларативная конфигурация приложения ⏱ 35m
- [ ] [[android-resources-system]] — система ресурсов: типы, квалификаторы, R класс ⏱ 20m
- 📝 День повторения
- [ ] [[android-app-components]] — четыре компонента: Activity, Service, BR, ContentProvider ⏱ 20m
- [ ] [[android-activity-lifecycle]] — жизненный цикл Activity: состояния и переходы ⏱ 15m
- [ ] [[android-fragment-lifecycle]] — Fragment Lifecycle, ViewLifecycleOwner, FragmentManager ⏱ 40m
- [ ] [[android-context-internals]] — иерархия Context, ContextImpl, getSystemService ⏱ 40m
- 📝 День повторения

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить UI-разработку (Views + Compose), навигацию, архитектуру, работу с данными и сетью
> Время: ~12 часов (29 файлов)
> Prerequisites: Level 1

### UI: View System

> [!tip] Если ты работаешь только с Compose, можешь пропустить View System и вернуться к нему позже.

- [ ] [[android-ui-views]] — XML Layouts, ViewBinding, RecyclerView, View-иерархия ⏱ 15m
- [ ] [[android-custom-view-fundamentals]] — создание Custom View: от наследования до Canvas ⏱ 20m
- [ ] [[android-view-measurement]] — onMeasure, MeasureSpec, LayoutParams ⏱ 20m
- [ ] [[android-animations]] — от ValueAnimator до Compose Transition, Choreographer и VSYNC ⏱ 40m
- [ ] [[android-touch-handling]] — обработка касаний: MotionEvent, dispatch, pointerInput ⏱ 35m
- 📝 День повторения

### UI: Jetpack Compose
- [ ] [[android-compose]] — декларативный UI: Composable, State, Recomposition ⏱ 20m
- [ ] [[android-state-management]] — StateFlow, SharedFlow, Channel и Compose State ⏱ 25m

### Навигация
- [ ] [[android-navigation]] — полный гайд: Fragment, Jetpack Navigation, Compose Navigation ⏱ 25m
- [ ] [[android-navigation-evolution]] — эволюция навигации: от Activity+Intent до Type-safe Navigation 3 ⏱ 20m
- 📝 День повторения

### Архитектура
- [ ] [[android-architecture-patterns]] — MVVM, MVI, Clean Architecture и UDF ⏱ 20m
- [ ] [[android-architecture-evolution]] — от God Activity к Compose + MVI ⏱ 55m
- [ ] [[android-viewmodel-internals]] — как ViewModel переживает configuration change ⏱ 25m
- [ ] [[android-repository-pattern]] — Single Source of Truth и Offline-First ⏱ 25m

### Данные и сеть
- [ ] [[android-data-persistence]] — Room, DataStore, файловое хранилище ⏱ 10m
- 📝 День повторения
- [ ] [[android-networking]] — Retrofit, OkHttp, Ktor: HTTP-клиенты и сериализация ⏱ 20m
- [ ] [[android-bundle-parcelable]] — Bundle, Parcelable, сериализация через Binder IPC ⏱ 40m

### DI

> [!tip] Если ты используешь только Hilt, можно пропустить Koin deep dive и вернуться к нему при необходимости.

- [ ] [[android-dependency-injection]] — обзор DI-экосистемы Android/KMP ⏱ 10m
- [ ] [[android-hilt-deep-dive]] — Hilt: официальная DI от Google поверх Dagger 2 ⏱ 20m
- [ ] [[android-koin-deep-dive]] — Koin: Kotlin-native runtime DI ⏱ 20m
- 📝 День повторения

### Async
- [ ] [[android-threading]] — Main Thread, Kotlin Coroutines, Dispatchers ⏱ 20m
- [ ] [[android-handler-looper]] — Handler, Looper, MessageQueue: фундамент async в Android ⏱ 40m
- [ ] [[android-async-evolution]] — эволюция async: от Thread/Handler до Coroutines ⏱ 20m
- [ ] [[android-coroutines-guide]] — практический гайд: scopes, dispatchers, patterns ⏱ 45m
- [ ] [[android-flow-guide]] — Flow на каждом слое архитектуры: data → domain → UI ⏱ 40m
- [ ] [[android-background-work]] — WorkManager, Foreground Services, Doze ⏱ 25m

### Build
- [ ] [[android-gradle-fundamentals]] — Gradle и AGP: task graph, конфигурация, плагины ⏱ 20m
- 📝 День повторения
- [ ] [[android-apk-aab]] — APK vs AAB, подпись, оптимизация размера ⏱ 30m
- [ ] [[android-dependencies]] — управление зависимостями: Version Catalogs, BOM ⏱ 20m

### Тестирование
- [ ] [[android-testing]] — Unit/Integration/UI тесты: JUnit, MockK, Espresso, Robolectric ⏱ 15m
- [ ] [[android-notifications]] — система уведомлений: каналы, PendingIntent ⏱ 45m
- [ ] [[android-permissions-security]] — Runtime Permissions, EncryptedSharedPreferences, Keystore ⏱ 20m
- 📝 День повторения

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Разобраться во внутренних механизмах Android: рендеринг, IPC, internals компонентов, DI фреймворки
> Время: ~11.5 часов (22 файла)
> Prerequisites: Level 2

### Internals компонентов
- [ ] [[android-intent-internals]] — Intent resolution, PendingIntent, Deep Links ⏱ 55m
- [ ] [[android-service-internals]] — Started/Bound/Foreground Service, Binder IPC, AIDL ⏱ 50m
- [ ] [[android-broadcast-internals]] — BroadcastReceiver, publish-subscribe, ограничения Android 8+ ⏱ 50m
- [ ] [[android-content-provider-internals]] — ContentProvider: межпроцессный доступ к данным ⏱ 40m
- 📝 День повторения

### UI Internals

> [!tip] Если ты работаешь только с Compose, можешь пропустить View Rendering Pipeline и RecyclerView Internals.

- [ ] [[android-compose-internals]] — внутреннее устройство: Compiler Plugin, Slot Table, три фазы ⏱ 20m
- [ ] [[android-view-rendering-pipeline]] — rendering pipeline: measure, layout, draw, GPU ⏱ 15m
- [ ] [[android-recyclerview-internals]] — четырёхуровневый кэш, DiffUtil, ViewHolder pattern ⏱ 40m
- [ ] [[android-window-system]] — PhoneWindow, DecorView, WindowManager, Surface, SurfaceFlinger ⏱ 45m
- [ ] [[android-canvas-drawing]] — 2D-рисование: Canvas, Paint, Path, трансформации ⏱ 20m
- 📝 День повторения
- [ ] [[android-graphics-apis]] — графические API: OpenGL ES, Vulkan ⏱ 10m

### DI Deep Dives

> [!tip] Если ты используешь только Hilt, можно пропустить Dagger/Kodein/Metro deep dives.

- [ ] [[android-dagger-deep-dive]] — Dagger 2: compile-time DI, полный контроль графа ⏱ 40m
- [ ] [[android-kotlin-inject-deep-dive]] — kotlin-inject: compile-time DI с KMP поддержкой ⏱ 15m
- [ ] [[android-metro-deep-dive]] — Metro: compiler plugin DI от Zac Sweers (2025) ⏱ 15m
- [ ] [[android-kodein-deep-dive]] — Kodein: runtime DI с множественными контейнерами ⏱ 20m
- 📝 День повторения
- [ ] [[android-manual-di-alternatives]] — Manual DI, Anvil, Toothpick ⏱ 20m

### Async Deep Dives

> [!tip] AsyncTask и RxJava — legacy. Пропусти если работаешь только с Coroutines.

- [ ] [[android-coroutines-mistakes]] — 10 типичных ошибок с Kotlin Coroutines ⏱ 45m
- [ ] [[android-async-testing]] — тестирование корутин, Flow, Turbine ⏱ 50m
- [ ] [[android-asynctask-deprecated]] — AsyncTask: история, проблемы и уроки ⏱ 40m
- [ ] [[android-executors]] — Executors и ThreadPoolExecutor в Android ⏱ 45m
- [ ] [[android-rxjava]] — RxJava и RxAndroid: реактивный подход ⏱ 40m
- [ ] [[android-rxjava-migration]] — миграция с RxJava на Coroutines/Flow ⏱ 30m
- 📝 День повторения

### Build Deep Dives

> [!tip] Если не занимаешься оптимизацией сборки, пропусти Level 3 Build deep dives.

- [ ] [[android-compilation-pipeline]] — от исходников до APK: kotlinc, D8, R8, AAPT ⏱ 20m
- [ ] [[android-proguard-r8]] — R8: code shrinking, obfuscation, bytecode optimization ⏱ 25m
- [ ] [[android-build-evolution]] — эволюция систем сборки: от Ant до Gradle ⏱ 20m

---

## Уровень 4: Экспертиза (Expert)
> Цель: Освоить профилирование, оптимизацию производительности, CI/CD и модуляризацию на уровне архитектуры
> Время: ~3 часа (6 файлов)
> Prerequisites: Level 3

- [ ] [[android-performance-profiling]] — Android Studio Profiler: CPU, Memory, Network, GPU ⏱ 20m
- [ ] [[android-app-startup-performance]] — оптимизация старта: Zygote, Baseline Profiles, Macrobenchmark ⏱ 45m
- [ ] [[android-memory-leaks]] — паттерны утечек, LeakCanary, WeakReference ⏱ 45m
- [ ] [[android-process-memory]] — процессы, LMK, управление памятью на уровне ОС ⏱ 20m
- [ ] [[android-modularization]] — multi-module архитектура для масштабируемости ⏱ 20m
- 📝 День повторения
- [ ] [[android-ci-cd]] — CI/CD: GitHub Actions, Fastlane, Firebase Test Lab ⏱ 20m
