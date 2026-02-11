---
title: "Android: путь обучения"
created: 2026-02-10
modified: 2026-02-10
type: guide
tags:
  - topic/android
  - type/guide
  - navigation
---

# Android: путь обучения

> Структурированный маршрут изучения от основ до экспертного уровня.

---

## Уровень 1: Основы (Beginner)
> Цель: Понять архитектуру Android, жизненный цикл компонентов и базовые концепции платформы
> Время: ~3 недели

1. [[android-overview]] — карта раздела и точка входа в Android-разработку
2. [[android-architecture]] — архитектура Android от Linux ядра через Binder/Zygote до ART
3. [[android-project-structure]] — структура проекта, модули, директории
4. [[android-manifest]] — AndroidManifest.xml: декларативная конфигурация приложения
5. [[android-resources-system]] — система ресурсов: типы, квалификаторы, R класс
6. [[android-app-components]] — четыре компонента: Activity, Service, BR, ContentProvider
7. [[android-activity-lifecycle]] — жизненный цикл Activity: состояния и переходы
8. [[android-fragment-lifecycle]] — Fragment Lifecycle, ViewLifecycleOwner, FragmentManager
9. [[android-context-internals]] — иерархия Context, ContextImpl, getSystemService

---

## Уровень 2: Рабочие навыки (Intermediate)
> Цель: Освоить UI-разработку (Views + Compose), навигацию, архитектуру, работу с данными и сетью
> Время: ~6 недель
> Prerequisites: Level 1

### UI: View System
10. [[android-ui-views]] — XML Layouts, ViewBinding, RecyclerView, View-иерархия
11. [[android-custom-view-fundamentals]] — создание Custom View: от наследования до Canvas
12. [[android-view-measurement]] — onMeasure, MeasureSpec, LayoutParams
13. [[android-animations]] — от ValueAnimator до Compose Transition, Choreographer и VSYNC
14. [[android-touch-handling]] — обработка касаний: MotionEvent, dispatch, pointerInput

### UI: Jetpack Compose
15. [[android-compose]] — декларативный UI: Composable, State, Recomposition
16. [[android-state-management]] — StateFlow, SharedFlow, Channel и Compose State

### Навигация
17. [[android-navigation]] — полный гайд: Fragment, Jetpack Navigation, Compose Navigation
18. [[android-navigation-evolution]] — эволюция навигации: от Activity+Intent до Type-safe Navigation 3

### Архитектура
19. [[android-architecture-patterns]] — MVVM, MVI, Clean Architecture и UDF
20. [[android-architecture-evolution]] — от God Activity к Compose + MVI
21. [[android-viewmodel-internals]] — как ViewModel переживает configuration change
22. [[android-repository-pattern]] — Single Source of Truth и Offline-First

### Данные и сеть
23. [[android-data-persistence]] — Room, DataStore, файловое хранилище
24. [[android-networking]] — Retrofit, OkHttp, Ktor: HTTP-клиенты и сериализация
25. [[android-bundle-parcelable]] — Bundle, Parcelable, сериализация через Binder IPC

### DI
26. [[android-dependency-injection]] — обзор DI-экосистемы Android/KMP
27. [[android-hilt-deep-dive]] — Hilt: официальная DI от Google поверх Dagger 2
28. [[android-koin-deep-dive]] — Koin: Kotlin-native runtime DI

### Async
29. [[android-threading]] — Main Thread, Kotlin Coroutines, Dispatchers
30. [[android-handler-looper]] — Handler, Looper, MessageQueue: фундамент async в Android
31. [[android-async-evolution]] — эволюция async: от Thread/Handler до Coroutines
32. [[android-background-work]] — WorkManager, Foreground Services, Doze

### Build
33. [[android-gradle-fundamentals]] — Gradle и AGP: task graph, конфигурация, плагины
34. [[android-apk-aab]] — APK vs AAB, подпись, оптимизация размера
35. [[android-dependencies]] — управление зависимостями: Version Catalogs, BOM

### Тестирование
36. [[android-testing]] — Unit/Integration/UI тесты: JUnit, MockK, Espresso, Robolectric
37. [[android-notifications]] — система уведомлений: каналы, PendingIntent
38. [[android-permissions-security]] — Runtime Permissions, EncryptedSharedPreferences, Keystore

---

## Уровень 3: Глубокие знания (Advanced)
> Цель: Разобраться во внутренних механизмах Android: рендеринг, IPC, internals компонентов, DI фреймворки
> Время: ~4 недели
> Prerequisites: Level 2

### Internals компонентов
39. [[android-intent-internals]] — Intent resolution, PendingIntent, Deep Links
40. [[android-service-internals]] — Started/Bound/Foreground Service, Binder IPC, AIDL
41. [[android-broadcast-internals]] — BroadcastReceiver, publish-subscribe, ограничения Android 8+
42. [[android-content-provider-internals]] — ContentProvider: межпроцессный доступ к данным

### UI Internals
43. [[android-compose-internals]] — внутреннее устройство: Compiler Plugin, Slot Table, три фазы
44. [[android-view-rendering-pipeline]] — rendering pipeline: measure, layout, draw, GPU
45. [[android-recyclerview-internals]] — четырёхуровневый кэш, DiffUtil, ViewHolder pattern
46. [[android-window-system]] — PhoneWindow, DecorView, WindowManager, Surface, SurfaceFlinger
47. [[android-canvas-drawing]] — 2D-рисование: Canvas, Paint, Path, трансформации
48. [[android-graphics-apis]] — графические API: OpenGL ES, Vulkan

### DI Deep Dives
49. [[android-dagger-deep-dive]] — Dagger 2: compile-time DI, полный контроль графа
50. [[android-kotlin-inject-deep-dive]] — kotlin-inject: compile-time DI с KMP поддержкой
51. [[android-metro-deep-dive]] — Metro: compiler plugin DI от Zac Sweers (2025)
52. [[android-kodein-deep-dive]] — Kodein: runtime DI с множественными контейнерами
53. [[android-manual-di-alternatives]] — Manual DI, Anvil, Toothpick

### Async Deep Dives
54. [[android-coroutines-mistakes]] — 10 типичных ошибок с Kotlin Coroutines
55. [[android-asynctask-deprecated]] — AsyncTask: история, проблемы и уроки
56. [[android-executors]] — Executors и ThreadPoolExecutor в Android
57. [[android-rxjava]] — RxJava и RxAndroid: реактивный подход

### Build Deep Dives
58. [[android-compilation-pipeline]] — от исходников до APK: kotlinc, D8, R8, AAPT
59. [[android-proguard-r8]] — R8: code shrinking, obfuscation, bytecode optimization
60. [[android-build-evolution]] — эволюция систем сборки: от Ant до Gradle

---

## Уровень 4: Экспертиза (Expert)
> Цель: Освоить профилирование, оптимизацию производительности, CI/CD и модуляризацию на уровне архитектуры
> Время: ~3 недели
> Prerequisites: Level 3

61. [[android-performance-profiling]] — Android Studio Profiler: CPU, Memory, Network, GPU
62. [[android-app-startup-performance]] — оптимизация старта: Zygote, Baseline Profiles, Macrobenchmark
63. [[android-memory-leaks]] — паттерны утечек, LeakCanary, WeakReference
64. [[android-process-memory]] — процессы, LMK, управление памятью на уровне ОС
65. [[android-modularization]] — multi-module архитектура для масштабируемости
66. [[android-ci-cd]] — CI/CD: GitHub Actions, Fastlane, Firebase Test Lab
