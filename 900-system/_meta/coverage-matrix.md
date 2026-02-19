---
title: "Coverage Matrix"
created: 2026-02-10
modified: 2026-02-10
type: reference
tags:
  - system/guidelines
  - system/metadata
---

# Coverage Matrix

> Матрица покрытия контента по областям и уровням сложности.
> Помогает найти пробелы в покрытии и спланировать создание контента.

---

## Сводка

Всего файлов в 100-areas: **553**

| Область | Файлов | Beginner | Intermediate | Advanced | Expert | Без уровня |
|---------|:------:|:--------:|:------------:|:--------:|:------:|:----------:|
| Android | 66 | 3 | 25 | 32 | 6 | 0 |
| Kotlin Multiplatform | 37 | 6 | 22 | 9 | 0 | 0 |
| CS Fundamentals | 61 | 8 | 35 | 13 | 5 | 0 |
| CS Foundations (KMP) | 23 | 0 | 13 | 9 | 1 | 0 |
| iOS | 45 | 4 | 27 | 14 | 0 | 0 |
| Leadership | 42 | 4 | 27 | 11 | 0 | 0 |
| AI/ML | 35 | 1 | 26 | 5 | 0 | 3 |
| Architecture | 12 | 2 | 9 | 1 | 0 | 0 |
| Career | 36 | 0 | 23 | 13 | 0 | 0 |
| Cloud | 7 | 1 | 6 | 0 | 0 | 0 |
| Communication | 24 | 4 | 16 | 4 | 0 | 0 |
| Cross-Platform | 24 | 1 | 23 | 0 | 0 | 0 |
| Databases | 16 | 3 | 10 | 2 | 0 | 1 |
| DevOps | 10 | 2 | 7 | 1 | 0 | 0 |
| JVM | 37 | 9 | 19 | 9 | 0 | 0 |
| Networking | 23 | 3 | 14 | 5 | 0 | 1 |
| Operating Systems | 8 | 1 | 7 | 0 | 0 | 0 |
| Programming | 12 | 0 | 11 | 0 | 0 | 1 |
| Security | 13 | 3 | 10 | 0 | 0 | 0 |
| Thinking & Learning | 22 | 1 | 21 | 0 | 0 | 0 |

---

## Крупные области

### Android (66 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Жизненный цикл Activity: состояния и переходы | — | [[android-activity-lifecycle]] | — | — |
| Анимации Android: от ValueAnimator до Compose Transi... | — | [[android-animations]] | — | — |
| Android APK и AAB: форматы пакетов и дистрибуция | — | [[android-apk-aab]] | — | — |
| Компоненты приложения: Activity, Service, BR, CP | — | [[android-app-components]] | — | — |
| Производительность запуска приложения: от Zygote до ... | — | — | [[android-app-startup-performance]] | — |
| Эволюция архитектуры Android-приложений | — | [[android-architecture-evolution]] | — | — |
| Архитектура приложения: MVVM, MVI, Clean Architecture | — | [[android-architecture-patterns]] | — | — |
| Архитектура Android: от Linux до приложения | — | — | [[android-architecture]] | — |
| Эволюция асинхронной работы в Android | — | [[android-async-evolution]] | — | — |
| AsyncTask: история, проблемы и уроки | — | [[android-asynctask-deprecated]] | — | — |
| Фоновая работа: история ограничений, WorkManager, Fo... | — | — | [[android-background-work]] | — |
| Broadcast Internals: механизм рассылки событий в And... | — | — | [[android-broadcast-internals]] | — |
| Эволюция систем сборки Android: от Ant до Gradle | — | [[android-build-evolution]] | — | — |
| Bundle и Parcelable: сериализация данных в Android | — | — | [[android-bundle-parcelable]] | — |
| Canvas Drawing: отрисовка на Canvas | — | — | [[android-canvas-drawing]] | — |
| Android CI/CD: от локального билда до Play Store | — | — | [[android-ci-cd]] | — |
| Compilation Pipeline: от исходников до APK | — | — | [[android-compilation-pipeline]] | — |
| Внутреннее устройство Jetpack Compose | — | — | — | [[android-compose-internals]] |
| Jetpack Compose: декларативный UI | — | [[android-compose]] | — | — |
| ContentProvider Internals: межпроцессный доступ к да... | — | — | — | [[android-content-provider-internals]] |
| Context: иерархия, ContextImpl и getSystemService по... | — | — | — | [[android-context-internals]] |
| Kotlin Coroutines: 10 типичных ошибок в Android | — | — | [[android-coroutines-mistakes]] | — |
| Custom Views: основы создания | — | — | [[android-custom-view-fundamentals]] | — |
| Dagger и Dagger 2: Deep-Dive — compile-time DI | — | — | [[android-dagger-deep-dive]] | — |
| Хранение данных: Room, DataStore, Files | — | [[android-data-persistence]] | — | — |
| Управление зависимостями в Android Gradle | — | [[android-dependencies]] | — | — |
| Dependency Injection в Android: обзор и навигация | — | [[android-dependency-injection]] | — | — |
| Executors и ThreadPoolExecutor в Android | — | — | [[android-executors]] | — |
| Fragment Lifecycle: состояния, View lifecycle и Frag... | — | — | [[android-fragment-lifecycle]] | — |
| Gradle и Android Gradle Plugin: полное руководство | — | [[android-gradle-fundamentals]] | — | — |
| Graphics APIs: OpenGL, Vulkan, Metal для мобильных | — | — | [[android-graphics-apis]] | — |
| Handler, Looper и MessageQueue: устройство Main Thread | — | — | [[android-handler-looper]] | — |
| Hilt Deep-dive: от Dagger до production | — | — | [[android-hilt-deep-dive]] | — |
| Intent: resolution, PendingIntent и Deep Links под к... | — | — | — | [[android-intent-internals]] |
| Kodein: Deep-Dive — runtime DI для Kotlin | — | [[android-kodein-deep-dive]] | — | — |
| Koin Deep-dive: Kotlin-native DI для Android и KMP | — | — | [[android-koin-deep-dive]] | — |
| kotlin-inject: Deep-Dive — compile-time DI для KMP | — | — | [[android-kotlin-inject-deep-dive]] | — |
| AndroidManifest.xml: конфигурация приложения | [[android-manifest]] | — | — | — |
| Manual DI и альтернативные фреймворки | — | [[android-manual-di-alternatives]] | — | — |
| Memory Leaks в Android: паттерны, обнаружение и пред... | — | — | [[android-memory-leaks]] | — |
| Metro: Deep-Dive — DI фреймворк нового поколения | — | — | [[android-metro-deep-dive]] | — |
| Модуляризация Android-приложений | — | — | [[android-modularization]] | — |
| Эволюция навигации в Android | — | [[android-navigation-evolution]] | — | — |
| Android Navigation: Полный гайд по всем подходам | — | [[android-navigation]] | — | — |
| Сеть: Retrofit, OkHttp, Ktor | — | — | [[android-networking]] | — |
| Notifications: система уведомлений Android от канала... | — | — | [[android-notifications]] | — |
| Android: карта раздела | [[android-overview]] | — | — | — |
| Профилирование производительности Android | — | — | [[android-performance-profiling]] | — |
| Permissions и Security: Runtime Permissions, Secure ... | — | [[android-permissions-security]] | — | — |
| Процессы и память: как Android управляет ресурсами | — | — | [[android-process-memory]] | — |
| Android ProGuard и R8: Code Shrinking, Obfuscation и... | — | — | [[android-proguard-r8]] | — |
| Структура Android-проекта: модули, директории, конфи... | [[android-project-structure]] | — | — | — |
| RecyclerView Internals: кэширование, переработка и п... | — | — | — | [[android-recyclerview-internals]] |
| Android Repository Pattern: Single Source of Truth и... | — | [[android-repository-pattern]] | — | — |
| Система ресурсов Android: типы, квалификаторы, R класс | — | [[android-resources-system]] | — | — |
| RxJava и RxAndroid: полный гайд | — | — | [[android-rxjava]] | — |
| Service: Started, Bound, Foreground — жизненный цикл... | — | — | [[android-service-internals]] | — |
| Управление состоянием в Android | — | [[android-state-management]] | — | — |
| Тестирование: Unit, Integration, UI тесты | — | [[android-testing]] | — | — |
| Threading в Android: Main Thread и Coroutines | — | [[android-threading]] | — | — |
| Обработка касаний в Android | — | — | [[android-touch-handling]] | — |
| View System: XML Layouts, ViewBinding, RecyclerView | — | [[android-ui-views]] | — | — |
| View Measurement: onMeasure и MeasureSpec | — | — | [[android-view-measurement]] | — |
| Конвейер рендеринга View в Android | — | — | [[android-view-rendering-pipeline]] | — |
| Внутреннее устройство Android ViewModel | — | — | [[android-viewmodel-internals]] | — |
| Window System: PhoneWindow, DecorView, WindowManager... | — | — | — | [[android-window-system]] |

---

### Kotlin Multiplatform (37 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Kotlin Multiplatform: Полный гайд по кросс-платформе... | [[kmp-overview]] | — | — | — |
| Миграция с Flutter на KMP | — | [[kmp-migration-from-flutter]] | — | — |
| Миграция на KMP с Native (Android + iOS) | — | [[kmp-migration-from-native]] | — | — |
| Миграция с React Native на KMP | — | [[kmp-migration-from-rn]] | — | — |
| KMP CI/CD | — | [[kmp-ci-cd]] | — | — |
| KMP Gradle Deep Dive | — | — | [[kmp-gradle-deep-dive]] | — |
| KMP Library Publishing | — | [[kmp-publishing]] | — | — |
| expect/actual: Платформо-зависимый код в KMP | [[kmp-expect-actual]] | — | — | — |
| KMP Getting Started: Первый проект за 30 минут | [[kmp-getting-started]] | — | — | — |
| KMP Project Structure: Анатомия мультиплатформенного... | [[kmp-project-structure]] | — | — | — |
| KMP Source Sets: Организация кода по платформам | [[kmp-source-sets]] | — | — | — |
| KMP Integration Testing | — | [[kmp-integration-testing]] | — | — |
| Стратегия тестирования в KMP: от unit до UI тестов | — | [[kmp-testing-strategies]] | — | — |
| Unit Testing в KMP: kotlin.test, Kotest, Turbine | — | [[kmp-unit-testing]] | — | — |
| KMP Architecture Patterns: Clean Architecture, MVI, ... | — | [[kmp-architecture-patterns]] | — | — |
| KMP DI Patterns: Koin, kotlin-inject, Manual DI | — | [[kmp-di-patterns]] | — | — |
| KMP Navigation: Decompose, Voyager, Compose Navigation | — | [[kmp-navigation]] | — | — |
| KMP State Management: StateFlow, MVI, Redux patterns | — | [[kmp-state-management]] | — | — |
| Compose Multiplatform Desktop: Production-ready прил... | — | [[compose-mp-desktop]] | — | — |
| Compose Multiplatform iOS: Production-ready UI для iOS | — | [[compose-mp-ios]] | — | — |
| Compose Multiplatform: Shared UI для всех платформ | [[compose-mp-overview]] | — | — | — |
| Compose Multiplatform Web: Beta для современных брау... | — | [[compose-mp-web]] | — | — |
| KMP Case Studies: Реальные примеры в production | — | — | [[kmp-case-studies]] | — |
| KMP Production Checklist: От разработки до релиза | — | — | [[kmp-production-checklist]] | — |
| KMP Troubleshooting: Решение типичных проблем | — | — | [[kmp-troubleshooting]] | — |
| kotlinx библиотеки в KMP: сериализация, дата-время, ... | — | [[kmp-kotlinx-libraries]] | — | — |
| Ktor Client в Kotlin Multiplatform: сетевой слой на ... | — | [[kmp-ktor-networking]] | — | — |
| SQLDelight в Kotlin Multiplatform: типобезопасная ба... | — | [[kmp-sqldelight-database]] | — | — |
| Экосистема библиотек KMP: Apollo, Coil, Realm и другие | — | [[kmp-third-party-libs]] | — | — |
| KMP Android Integration: Полный гайд по интеграции с... | — | [[kmp-android-integration]] | — | — |
| KMP Desktop/JVM: Compose для десктопных приложений | — | [[kmp-desktop-jvm]] | — | — |
| KMP iOS Deep Dive: Полный гайд по iOS интеграции | — | — | [[kmp-ios-deep-dive]] | — |
| KMP Web/Wasm: Kotlin для Web через WebAssembly | — | [[kmp-web-wasm]] | — | — |
| KMP Debugging: LLDB, Xcode, Crash Reporting | — | — | [[kmp-debugging]] | — |
| KMP Interop Deep Dive: ObjC, Swift Export, cinterop | — | — | [[kmp-interop-deep-dive]] | — |
| KMP Memory Management: GC, ARC, и их взаимодействие | — | — | [[kmp-memory-management]] | — |
| KMP Performance Optimization: Build, Size, Runtime | — | — | [[kmp-performance-optimization]] | — |

#### Gaps:
- [ ] Kotlin Multiplatform: экспертный уровень (expert) -- отсутствует или мало

---

### CS Fundamentals (61 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Big O нотация: полное руководство по анализу сложности | [[big-o-complexity]] | — | — | — |
| Продвинутый код с объяснением каждой детали | — | — | [[code-explained-advanced]] | — |
| Код с объяснением каждой детали (с нуля) | [[code-explained-from-zero]] | — | — | — |
| CS Fundamentals: Алгоритмы и Структуры Данных | [[cs-fundamentals-overview]] | — | — | — |
| Фреймворк решения задач: UMPIRE и метод Полья | [[problem-solving-framework]] | — | — | — |
| Массивы и строки: фундамент всех алгоритмов | [[arrays-strings]] | — | — | — |
| Дерево Фенвика (Binary Indexed Tree) | — | — | [[fenwick-tree]] | — |
| Графы (Graphs) | — | [[graphs]] | — | — |
| Хеш-таблицы (Hash Tables) | — | [[hash-tables]] | — | — |
| Кучи и очереди с приоритетом (Heaps & Priority Queues) | — | [[heaps-priority-queues]] | — | — |
| Связные списки (Linked Lists) | [[linked-lists]] | — | — | — |
| Персистентные структуры данных | — | — | — | [[persistent-structures]] |
| Дерево отрезков (Segment Tree) | — | — | [[segment-tree]] | — |
| Разреженная таблица (Sparse Table) | — | — | [[sparse-table]] | — |
| Стеки и очереди: LIFO и FIFO от нуля | [[stacks-queues]] | — | — | — |
| Продвинутые деревья: AVL и красно-чёрные деревья | — | — | [[trees-advanced]] | — |
| Бинарные деревья и деревья поиска (BST) | — | [[trees-binary]] | — | — |
| Префиксное дерево (Trie) | — | [[tries]] | — | — |
| Паттерн бинарного поиска (Binary Search) | — | [[binary-search-pattern]] | — | — |
| Паттерн битовых манипуляций (Bit Manipulation) | — | [[bit-manipulation]] | — | — |
| Паттерн циклической сортировки (Cyclic Sort) | — | [[cyclic-sort-pattern]] | — | — |
| Паттерны DFS и BFS | — | [[dfs-bfs-patterns]] | — | — |
| Паттерны динамического программирования | — | — | [[dp-patterns]] | — |
| Паттерн быстрого и медленного указателей (Floyd) | — | [[fast-slow-pointers-pattern]] | — | — |
| Паттерн интервалов (Intervals) | — | [[intervals-pattern]] | — | — |
| Паттерн K-way Merge | — | [[k-way-merge-pattern]] | — | — |
| Паттерн Meet in the Middle | — | — | [[meet-in-the-middle]] | — |
| Паттерн монотонного стека (Monotonic Stack) | — | [[monotonic-stack-pattern]] | — | — |
| Алгоритмические паттерны: карта паттернов решения задач | — | [[patterns-overview]] | — | — |
| Паттерн скользящего окна (Sliding Window) | — | [[sliding-window-pattern]] | — | — |
| Продвинутые строковые алгоритмы | — | — | [[string-algorithms-advanced]] | — |
| Паттерн Top K элементов | — | [[top-k-elements-pattern]] | — | — |
| Паттерн топологической сортировки (Topological Sort) | — | [[topological-sort-pattern]] | — | — |
| Паттерн двух куч (Two Heaps) | — | [[two-heaps-pattern]] | — | — |
| Паттерн двух указателей (Two Pointers) | — | [[two-pointers-pattern]] | — | — |
| Паттерн Union-Find (Disjoint Set Union) | — | [[union-find-pattern]] | — | — |
| Перебор с возвратом (Backtracking) | — | [[backtracking]] | — | — |
| Комбинаторика для соревновательного программирования | — | — | [[combinatorics]] | — |
| Вычислительная геометрия | — | — | — | [[computational-geometry]] |
| Разделяй и властвуй (Divide and Conquer) | — | [[divide-and-conquer]] | — | — |
| Оптимизации динамического программирования | — | — | — | [[dp-optimization]] |
| Динамическое программирование | — | [[dynamic-programming]] | — | — |
| Продвинутые алгоритмы на графах | — | — | [[graph-advanced]] | — |
| Алгоритмы на графах: BFS, DFS, Dijkstra | — | [[graph-algorithms]] | — | — |
| Жадные алгоритмы (Greedy) | — | [[greedy-algorithms]] | — | — |
| Минимальное остовное дерево (MST) | — | — | [[minimum-spanning-tree]] | — |
| Сетевые потоки (Network Flow) | — | — | — | [[network-flow]] |
| Теория чисел для алгоритмов | — | — | [[number-theory]] | — |
| Рекурсия: полное руководство для понимания с нуля | [[recursion-fundamentals]] | — | — | — |
| Алгоритмы поиска | — | [[searching-algorithms]] | — | — |
| Алгоритмы кратчайших путей | — | — | [[shortest-paths]] | — |
| Алгоритмы сортировки | — | [[sorting-algorithms]] | — | — |
| Продвинутые строковые алгоритмы (Suffix Array, Aho-C... | — | — | — | [[string-advanced]] |
| Строковые алгоритмы | — | [[string-algorithms]] | — | — |
| Типичные ошибки на coding интервью | — | [[common-mistakes]] | — | — |
| LeetCode Roadmap: планы и стратегия подготовки | — | [[leetcode-roadmap]] | — | — |
| Руководство по мок-интервью | — | [[mock-interview-guide]] | — | — |
| Обзор соревновательного программирования | — | [[competitive-programming-overview]] | — | — |
| Стратегия проведения контеста | — | [[contest-strategy]] | — | — |
| Советы по реализации для соревнований | — | [[implementation-tips]] | — | — |
| Классификация задач по ограничениям | — | [[problem-classification]] | — | — |

---

### CS Foundations (KMP) (23 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| CS Foundations для KMP: Компьютерные основы для пони... | — | [[cs-foundations-overview]] | — | — |
| CPU Architecture: что должен знать программист | — | [[cpu-architecture-basics]] | — | — |
| OS Fundamentals: что должен знать разработчик | — | [[os-fundamentals-for-devs]] | — | — |
| Bytecode и виртуальные машины: как код исполняется б... | — | [[bytecode-virtual-machines]] | — | — |
| Compilation Pipeline: путь кода от текста до исполнения | — | [[compilation-pipeline]] | — | — |
| Интерпретация и JIT: от байткода к скорости | — | — | [[interpretation-jit]] | — |
| Native Compilation и LLVM: как Kotlin становится маш... | — | — | [[native-compilation-llvm]] | — |
| Garbage Collection: как компьютер убирает за тобой | — | [[garbage-collection-explained]] | — | — |
| Модель памяти: Stack и Heap | — | [[memory-model-fundamentals]] | — | — |
| Memory Safety: от багов к гарантиям | — | — | [[memory-safety-ownership]] | — |
| Reference Counting и ARC: как Swift управляет памятью | — | [[reference-counting-arc]] | — | — |
| ABI и Calling Conventions: как бинарный код общается | — | — | — | [[abi-calling-conventions]] |
| Bridges и Bindings: автоматизация interop | — | — | [[bridges-bindings-overview]] | — |
| FFI: как языки общаются друг с другом | — | — | [[ffi-foreign-function-interface]] | — |
| Memory Layout и Marshalling: как данные хранятся и п... | — | — | [[memory-layout-marshalling]] | — |
| Generics: параметрический полиморфизм | — | [[generics-parametric-polymorphism]] | — | — |
| Type Erasure и Reification: что происходит с типами ... | — | — | [[type-erasure-reification]] | — |
| Type Systems: фундамент типизации | — | [[type-systems-fundamentals]] | — | — |
| Variance: ковариантность и контравариантность | — | — | [[variance-covariance]] | — |
| Async модели: от callbacks до coroutines | — | [[async-models-overview]] | — | — |
| Concurrency vs Parallelism: принципиальная разница | — | [[concurrency-vs-parallelism]] | — | — |
| Процессы и потоки: фундамент конкурентности | — | [[processes-threads-fundamentals]] | — | — |
| Synchronization Primitives: mutex, semaphore и другие | — | — | [[synchronization-primitives]] | — |

#### Gaps:
- [ ] CS Foundations (KMP): начальный уровень (beginner) -- отсутствует
- [ ] CS Foundations (KMP): мало материалов начального уровня (0 из 23)

---

### iOS (45 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Доступность iOS-приложений | — | [[ios-accessibility]] | — | — |
| Компоненты iOS-приложения и жизненный цикл | — | [[ios-app-components]] | — | — |
| iOS App Distribution: TestFlight, App Store, Enterprise | — | [[ios-app-distribution]] | — | — |
| Эволюция архитектуры iOS-приложений | — | [[ios-architecture-evolution]] | — | — |
| Архитектурные паттерны iOS | — | [[ios-architecture-patterns]] | — | — |
| iOS Architecture: Darwin, XNU и слои системы | — | — | [[ios-architecture]] | — |
| iOS Async/Await и современная конкурентность в Swift | — | — | [[ios-async-await]] | — |
| Эволюция асинхронности в iOS | — | [[ios-async-evolution]] | — | — |
| Фоновое выполнение в iOS | — | — | [[ios-background-execution]] | — |
| iOS CI/CD: Xcode Cloud, Fastlane, GitHub Actions | — | — | [[ios-ci-cd]] | — |
| iOS Code Signing: сертификаты, профили, entitlements | — | [[ios-code-signing]] | — | — |
| Combine Framework: реактивное программирование в iOS | — | — | [[ios-combine]] | — |
| iOS Compilation Pipeline: от Swift до .app | — | [[ios-compilation-pipeline]] | — | — |
| Типичные ошибки конкурентности в iOS | — | — | [[ios-concurrency-mistakes]] | — |
| Core Data: персистентность данных в iOS | — | — | [[ios-core-data]] | — |
| iOS Custom Views: UIView subclassing, drawing, layout | — | [[ios-custom-views]] | — | — |
| Хранение данных в iOS | — | [[ios-data-persistence]] | — | — |
| iOS Debugging: LLDB, breakpoints, crash analysis | — | [[ios-debugging]] | — | — |
| Dependency Injection в iOS | — | [[ios-dependency-injection]] | — | — |
| Grand Central Dispatch: глубокое погружение | — | — | [[ios-gcd-deep-dive]] | — |
| iOS Graphics Fundamentals: Core Graphics, Core Anima... | — | [[ios-graphics-fundamentals]] | — | — |
| iOS Market Trends 2026: рынок, востребованные навыки... | [[ios-market-trends-2026]] | — | — | — |
| Модуляризация iOS-приложений | — | — | [[ios-modularization]] | — |
| Навигация в iOS: UIKit и SwiftUI | — | [[ios-navigation]] | — | — |
| iOS Networking: URLSession и современные подходы | — | [[ios-networking]] | — | — |
| Уведомления в iOS: Push, Local, Live Activities | — | [[ios-notifications]] | — | — |
| iOS: карта раздела | [[ios-overview]] | — | — | — |
| iOS Performance Profiling: Instruments, Time Profile... | — | — | [[ios-performance-profiling]] | — |
| Разрешения и безопасность в iOS | — | [[ios-permissions-security]] | — | — |
| Управление памятью и процессами в iOS (ARC) | — | — | [[ios-process-memory]] | — |
| Repository Pattern в iOS | — | [[ios-repository-pattern]] | — | — |
| iOS Scroll Performance: UITableView, UICollectionVie... | — | [[ios-scroll-performance]] | — | — |
| Управление состоянием в iOS | — | [[ios-state-management]] | — | — |
| iOS Swift-Objective-C Interop: bridging, @objc, runtime | — | — | [[ios-swift-objc-interop]] | — |
| SwiftData: современная персистентность в iOS | — | [[ios-swiftdata]] | — | — |
| SwiftUI vs UIKit: выбор UI-фреймворка для iOS | — | [[ios-swiftui-vs-uikit]] | — | — |
| SwiftUI: декларативный UI для iOS | — | [[ios-swiftui]] | — | — |
| Тестирование iOS-приложений | — | [[ios-testing]] | — | — |
| Основы многопоточности в iOS | — | [[ios-threading-fundamentals]] | — | — |
| Обработка касаний в iOS | — | — | [[ios-touch-interaction]] | — |
| UIKit Fundamentals: основы построения интерфейсов в iOS | [[ios-uikit-fundamentals]] | — | — | — |
| iOS View Rendering: render loop, layers, off-screen ... | — | — | [[ios-view-rendering]] | — |
| UIViewController Lifecycle: полный разбор жизненного... | — | [[ios-viewcontroller-lifecycle]] | — | — |
| Паттерны ViewModel в iOS | — | [[ios-viewmodel-patterns]] | — | — |
| iOS Xcode Fundamentals: проекты, targets, schemes | [[ios-xcode-fundamentals]] | — | — | — |

#### Gaps:
- [ ] iOS: экспертный уровень (expert) -- отсутствует или мало

---

### Leadership (42 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Tech Leadership: от Tech Lead до CTO | — | [[leadership-overview]] | — | — |
| Как нанимать инженеров: Полный гайд | — | [[hiring-engineers]] | — | — |
| Дизайн процесса интервью | — | [[interview-process-design]] | — | — |
| Интервью на EM/Director/VP/CTO | — | — | [[leadership-interviews]] | — |
| Офферы и переговоры | — | [[making-offers]] | — | — |
| Где искать кандидатов | — | [[sourcing-candidates]] | — | — |
| CTO vs VP Engineering: ключевые различия | — | [[cto-vs-vpe]] | — | — |
| Engineering Manager: роль и обязанности | — | [[engineering-manager]] | — | — |
| Первые 90 дней в роли лидера | — | [[first-90-days]] | — | — |
| IC Track vs Management Track: как выбрать | — | [[ic-vs-management]] | — | — |
| Tech Lead: роль, обязанности, навыки | — | [[tech-lead-role]] | — | — |
| Founding Engineer | — | [[founding-engineer]] | — | — |
| Масштабирование с нуля | — | — | [[scaling-from-zero]] | — |
| CTO в стартапе | — | — | [[startup-cto]] | — |
| Техническое Due Diligence | — | — | [[technical-due-diligence]] | — |
| Делегирование: Отпустить контроль | — | [[delegation]] | — | — |
| Engineering Management: Фундаментальные принципы | — | [[em-fundamentals]] | — | — |
| Manager README: Как работать со мной | [[manager-readme]] | — | — | — |
| 1-on-1 Meetings: Главный инструмент менеджера | — | [[one-on-one-meetings]] | — | — |
| Performance Management: Оценка и развитие | — | [[performance-management]] | — | — |
| Переход от IC к менеджеру | — | [[transition-to-management]] | — | — |
| Планирование бюджета | — | — | [[budget-planning]] | — |
| Кризисный менеджмент | — | — | [[crisis-management]] | — |
| Коммуникация с руководством | — | — | [[executive-communication]] | — |
| Управление stakeholders | — | — | [[stakeholder-management]] | — |
| Стратегическое мышление | — | — | [[strategic-thinking]] | — |
| Строительство инженерной команды | — | [[building-engineering-team]] | — | — |
| Справочники компаний | [[company-handbooks]] | — | — | — |
| Мотивация команды | — | [[motivation]] | — | — |
| Онбординг инженеров | [[onboarding]] | — | — | — |
| Культура инженерной команды | — | [[team-culture]] | — | — |
| Динамика команды | — | [[team-dynamics]] | — | — |
| Agile практики | [[agile-practices]] | — | — | — |
| Метрики инженерии | — | [[engineering-metrics]] | — | — |
| OKRs и KPIs для инженерии | — | [[okrs-kpis]] | — | — |
| Масштабирование инженерной организации | — | — | [[scaling-engineering-org]] | — |
| Структуры команд | — | [[team-structures]] | — | — |
| Архитектурные решения (ADR) | — | [[architecture-decisions]] | — | — |
| Процессы разработки | — | [[development-process]] | — | — |
| Инженерные практики | — | [[engineering-practices]] | — | — |
| Управление техническим долгом | — | [[tech-debt-management]] | — | — |
| Техническое видение и стратегия | — | — | [[technical-vision]] | — |

#### Gaps:
- [ ] Leadership: экспертный уровень (expert) -- отсутствует или мало

---

## Остальные области

### AI/ML (35 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| AI Agent Cost Optimization | — | — | [[agent-cost-optimization]] | — |
| AI Agent Debugging & Troubleshooting | — | [[agent-debugging-troubleshooting]] | — | — |
| AI Agent Evaluation & Testing Framework | — | [[agent-evaluation-testing]] | — | — |
| Сравнение Agent Frameworks: Полное руководство 2025 | — | [[agent-frameworks-comparison]] | — | — |
| AI Agent Production Deployment | — | [[agent-production-deployment]] | — | — |
| Agentic RAG: AI Agents + Retrieval | — | [[agentic-rag]] | — | — |
| AI Агенты - Продвинутое Руководство | — | — | [[ai-agents-advanced]] | — |
| LLM API Integration - Практическое руководство 2025 | — | [[ai-api-integration]] | — | — |
| AI Cost Optimization - Полное Руководство | — | — | [[ai-cost-optimization]] | — |
| Подготовка данных для AI: Chunking, Синтетические да... | — | [[ai-data-preparation]] | — | — |
| AI DevOps & Deployment - Полное Руководство 2025 | — | [[ai-devops-deployment]] | — | — |
| Что такое AI Engineering | — | [[ai-engineering-intro]] | — | — |
| Fine-tuning и адаптация моделей: LoRA, QLoRA, когда ... | — | [[ai-fine-tuning-guide]] | — | — |
| AI Observability & Monitoring - Полное Руководство 2025 | — | [[ai-observability-monitoring]] | — | — |
| Безопасность LLM приложений: от Prompt Injection до ... | — | [[ai-security-safety]] | — | — |
| AI Tools Ecosystem 2025: Полный справочник | — | [[ai-tools-ecosystem-2025]] | — | — |
| Embeddings: Полное руководство | — | [[embeddings-complete-guide]] | — | — |
| LLM Fundamentals: От нейронных сетей к современным я... | [[llm-fundamentals]] | — | — | — |
| LLM Inference Optimization - Полное Руководство | — | — | [[llm-inference-optimization]] | — |
| Локальные LLM и Self-Hosting - Полное Руководство | — | [[local-llms-self-hosting]] | — | — |
| Model Context Protocol (MCP) | — | [[mcp-model-context-protocol]] | — | — |
| Mobile AI/ML: Complete Guide to On-Device Inference ... | — | [[mobile-ai-ml-guide]] | — | — |
| Ландшафт LLM моделей 2025 | — | [[models-landscape-2025]] | — | — |
| Multimodal AI: Полное руководство по мультимодальным... | — | [[multimodal-ai-guide]] | — | — |
| Prompt Engineering Masterclass: От основ до production | — | [[prompt-engineering-masterclass]] | — | — |
| RAG: Продвинутые техники | — | — | [[rag-advanced-techniques]] | — |
| Reasoning Models: o1, o3, DeepSeek R1, Claude Extend... | — | [[reasoning-models-guide]] | — | — |
| Structured Outputs и Tool Use: От хаоса к порядку | — | [[structured-outputs-tools]] | — | — |
| Практикум: AI Agent с инструментами | — | [[tutorial-ai-agent]] | — | — |
| Практикум: Document Q&A System | — | [[tutorial-document-qa]] | — | — |
| Tutorial: Production-Ready RAG Chatbot с нуля | — | [[tutorial-rag-chatbot]] | — | — |
| Vector Databases: Полное руководство | — | [[vector-databases-guide]] | — | — |

#### Gaps:
- [ ] AI/ML: экспертный уровень (expert) -- отсутствует

---

### Architecture (12 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| API Design: REST, GraphQL и когда что использовать | — | [[api-design]] | — | — |
| Distributed Systems: CAP, consistency, Saga pattern | — | [[architecture-distributed-systems]] | — | — |
| Rate Limiting: защита API от перегрузки | — | [[architecture-rate-limiting]] | — | — |
| Resilience Patterns: Circuit Breaker, Retry, Bulkhead | — | [[architecture-resilience-patterns]] | — | — |
| Search Systems: Elasticsearch, Full-Text Search, Rel... | — | [[architecture-search-systems]] | — | — |
| Caching: быстро, но сложно | — | [[caching-strategies]] | — | — |
| Dependency Injection: фундаментальные концепции | [[dependency-injection-fundamentals]] | — | — | — |
| Event-Driven Architecture: реактивные системы | — | [[event-driven-architecture]] | — | — |
| Микросервисы vs Монолит: когда что выбирать | — | [[microservices-vs-monolith]] | — | — |
| Performance: от 3s до 300ms | — | — | [[performance-optimization]] | — |
| Технический долг: $2 триллиона проблем | — | [[technical-debt]] | — | — |

---

### Career (36 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| AI-Era Job Search 2025: инструменты и стратегии | — | — | [[ai-era-job-search]] | — |
| AI-Powered Interview Preparation 2026: полный гайд | — | — | [[ai-interview-preparation]] | — |
| AI Interview Prompts Library: 100+ готовых промптов | — | — | [[ai-interview-prompts]] | — |
| Personal Brand 2025: visibility без становления инфл... | — | — | [[personal-brand]] | — |
| Portfolio Strategy 2026: GitHub как proof of work | — | — | [[portfolio-strategy]] | — |
| Standing Out 2025: как выделиться среди 250+ кандидатов | — | — | [[standing-out]] | — |
| Software Engineer Interview Foundation 2026: универс... | — | [[se-interview-foundation]] | — | — |
| Австрия для Android Developer: Red-White-Red Card и ... | — | [[austria-guide]] | — | — |
| Нидерланды для Android-разработчиков: HSM виза и 30%... | — | [[netherlands-guide]] | — | — |
| Швейцария: максимальные зарплаты в Европе | — | [[switzerland-guide]] | — | — |
| UAE Tech Market: Dubai и Abu Dhabi для Android-разра... | — | [[uae-tech-market]] | — | — |
| LinkedIn Optimization 2026: AI-powered visibility | — | [[linkedin-optimization]] | — | — |
| Resume Design Standards 2026 | — | [[resume-design-standards-2026]] | — | — |
| Resume Strategy 2026: AI-powered ATS optimization | — | [[resume-strategy]] | — | — |
| Hidden Job Market 2025: 70-80% вакансий не публикуются | — | [[hidden-job-market]] | — | — |
| Job Search Strategy 2025: 15-25% success rate вместо 2% | — | [[job-search-strategy]] | — | — |
| Networking Tactics 2025: качество над количеством | — | [[networking-tactics]] | — | — |
| Recruiter Relationships 2025: как работать с рекруте... | — | [[recruiter-relationships]] | — | — |
| Remote-First компании для Android-разработчиков | — | [[remote-first-companies]] | — | — |
| Remote из Казахстана: полный гайд для Android Senior... | — | — | [[remote-from-kazakhstan]] | — |
| Android Job Market 2025: реальное состояние | — | [[android-job-market-2025]] | — | — |
| In-Demand Android Skills 2025: что учить, что забыть | — | [[in-demand-skills-2025]] | — | — |
| Android Developer Salary 2025: глобальные бенчмарки | — | [[salary-benchmarks]] | — | — |
| Staff+ Engineering: путь выше Senior | — | — | [[staff-plus-engineering]] | — |
| Android Senior Interview 2026: полный гайд | — | — | [[android-senior-2026]] | — |
| Behavioral Interview 2025: STAR method и как его пра... | — | [[behavioral-interview]] | — | — |
| Coding Challenges 2025: LeetCode patterns и подготов... | — | [[coding-challenges]] | — | — |
| Android Interview Process 2025: от заявки до оффера | — | [[interview-process]] | — | — |
| Interview Tracking System 2026: templates и отчёты | — | [[interview-tracking-system]] | — | — |
| Salary Negotiation 2025: как получить +$50K к офферу | — | — | [[negotiation]] | — |
| System Design для Android: думай как архитектор | — | — | [[system-design-android]] | — |
| Android Technical Interview 2025: полный гайд по рау... | — | — | [[technical-interview]] | — |
| Android Interview Questions 2025: 50+ вопросов с отв... | — | [[android-questions]] | — | — |
| Architecture Interview Questions 2025: MVVM, MVI, Cl... | — | — | [[architecture-questions]] | — |
| Behavioral Interview Questions 2025: STAR примеры дл... | — | [[behavioral-questions]] | — | — |
| Kotlin Interview Questions 2025: 40+ вопросов с отве... | — | [[kotlin-questions]] | — | — |

#### Gaps:
- [ ] Career: начальный уровень (beginner) -- отсутствует
- [ ] Career: экспертный уровень (expert) -- отсутствует

---

### Cloud (7 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| AWS Core Services: EC2, RDS, Lambda, S3, IAM | — | [[cloud-aws-core-services]] | — | — |
| Cloud Disaster Recovery: Multi-AZ, Multi-Region, RTO... | — | [[cloud-disaster-recovery]] | — | — |
| GCP Core Services: Compute Engine, Cloud SQL, BigQuery | — | [[cloud-gcp-core-services]] | — | — |
| Cloud Networking & Security: VPC, Security Groups, IAM | — | [[cloud-networking-security]] | — | — |
| Cloud Platforms: от bare metal до serverless | — | [[cloud-platforms-essentials]] | — | — |
| Serverless Patterns: Lambda, Event-Driven, Step Func... | — | [[cloud-serverless-patterns]] | — | — |

#### Gaps:
- [ ] Cloud: начальный уровень (beginner) -- отсутствует
- [ ] Cloud: продвинутый уровень (advanced) -- отсутствует
- [ ] Cloud: перекос к intermediate (100%), нужно разнообразие уровней

---

### Communication (24 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Communication Skills для IT-специалистов | — | [[communication-overview]] | — | — |
| Communication Barriers: что мешает понять друг друга | [[communication-barriers]] | — | — | — |
| Модели коммуникации | [[communication-models]] | — | — | — |
| Communication Styles: DISC и как адаптироваться | — | [[communication-styles]] | — | — |
| Async Communication: Slack, Email и Remote Best Prac... | — | [[async-communication]] | — | — |
| Email Communication для IT-специалистов | [[email-communication]] | — | — | — |
| Technical Writing: RFC, ADR и документация | — | [[technical-writing]] | — | — |
| Cultural Dimensions: Hofstede и Lewis Model | — | [[cultural-dimensions]] | — | — |
| Remote Team Communication: Timezone, Async-First и T... | — | [[remote-team-communication]] | — | — |
| Conflict Resolution для IT-специалистов | — | — | [[conflict-resolution]] | — |
| Delivering Bad News: layoffs, cancellations и другие... | — | — | [[delivering-bad-news]] | — |
| Performance Conversations: reviews, PIPs и promotion... | — | — | [[performance-conversations]] | — |
| Saying No: отказывать без разрушения отношений | — | [[saying-no]] | — | — |
| Feedback Frameworks: SBI vs COIN vs DESC vs STAR vs ... | — | [[feedback-frameworks]] | — | — |
| Giving Feedback: как давать обратную связь, которая ... | — | [[giving-feedback]] | — | — |
| Receiving Feedback: как принимать обратную связь без... | — | [[receiving-feedback]] | — | — |
| Active Listening: Базовый навык коммуникации | [[active-listening]] | — | — | — |
| Empathetic Listening: слушать чтобы понять, а не отв... | — | [[empathetic-listening]] | — | — |
| Negotiation Frameworks: Harvard Method и другие подходы | — | [[negotiation-frameworks]] | — | — |
| Negotiation Fundamentals для IT-специалистов | — | [[negotiation-fundamentals]] | — | — |
| Stakeholder Negotiation: работа с руководством, PM и... | — | — | [[stakeholder-negotiation]] | — |
| Presentation Design: Структура и визуальный дизайн п... | — | [[presentation-design]] | — | — |
| Technical Storytelling: Нарратив в IT-коммуникации | — | [[storytelling-tech]] | — | — |
| Technical Presentations для IT-специалистов | — | [[technical-presentations]] | — | — |

#### Gaps:
- [ ] Communication: экспертный уровень (expert) -- отсутствует

---

### Cross-Platform (24 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Cross-Platform: Architecture — MVVM, Clean Architecture | — | [[cross-architecture]] | — | — |
| Cross-Platform: Background Work — BackgroundTasks vs... | — | [[cross-background-work]] | — | — |
| Cross-Platform: Build Systems — Xcode vs Gradle | — | [[cross-build-systems]] | — | — |
| Cross-Platform: Code Signing — Provisioning Profiles... | — | [[cross-code-signing]] | — | — |
| Cross-Platform: Legacy Concurrency — GCD vs Handler/... | — | [[cross-concurrency-legacy]] | — | — |
| Cross-Platform: Modern Concurrency — async/await vs ... | — | [[cross-concurrency-modern]] | — | — |
| Cross-Platform: Data Persistence — Core Data vs Room | — | [[cross-data-persistence]] | — | — |
| Cross-Platform: Decision Guide — Native vs KMP vs Fl... | — | [[cross-decision-guide]] | — | — |
| Cross-Platform: Dependency Injection — Swinject vs Hilt | — | [[cross-dependency-injection]] | — | — |
| Cross-Platform: Distribution — App Store vs Play Store | — | [[cross-distribution]] | — | — |
| Cross-Platform: Graphics — Core Animation vs RenderT... | — | [[cross-graphics-rendering]] | — | — |
| Cross-Platform: Interop — Swift-ObjC vs Kotlin-Java | — | [[cross-interop]] | — | — |
| Cross-Platform: KMP Patterns — expect/actual, SKIE, ... | — | [[cross-kmp-patterns]] | — | — |
| Cross-Platform: Lifecycle — UIViewController vs Acti... | — | [[cross-lifecycle]] | — | — |
| Cross-Platform: Memory Management — ARC vs GC | — | [[cross-memory-management]] | — | — |
| Cross-Platform: Navigation — NavigationStack vs Navi... | — | [[cross-navigation]] | — | — |
| Cross-Platform: Networking — URLSession vs Retrofit | — | [[cross-networking]] | — | — |
| Cross-Platform: Profiling — Instruments vs Android S... | — | [[cross-performance-profiling]] | — | — |
| Cross-Platform: Permissions — Privacy Manifest vs Ru... | — | [[cross-permissions]] | — | — |
| Cross-Platform: iOS vs Android сравнение | [[cross-platform-overview]] | — | — | — |
| Cross-Platform: State Management — @State vs StateFlow | — | [[cross-state-management]] | — | — |
| Cross-Platform: Testing — XCTest vs JUnit | — | [[cross-testing]] | — | — |
| Cross-Platform: Declarative UI — SwiftUI vs Compose | — | [[cross-ui-declarative]] | — | — |
| Cross-Platform: Imperative UI — UIKit vs Android Views | — | [[cross-ui-imperative]] | — | — |

#### Gaps:
- [ ] Cross-Platform: продвинутый уровень (advanced) -- отсутствует
- [ ] Cross-Platform: экспертный уровень (expert) -- отсутствует
- [ ] Cross-Platform: перекос к intermediate (96%), нужно разнообразие уровней

---

### Databases (16 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| AI/ML Databases: Vector Databases & Embeddings | — | [[aiml-databases-complete]] | — | — |
| Cloud Databases: Complete Guide | — | [[cloud-databases-complete]] | — | — |
| Databases: от SELECT * до миллисекундных запросов | — | — | [[database-design-optimization]] | — |
| Database Internals: From Storage to Transactions | — | — | [[database-internals-complete]] | — |
| Backup & Recovery: PITR, WAL, RTO/RPO | — | [[databases-backup-recovery]] | — | — |
| Базы данных: Полный фундаментальный гайд | [[databases-fundamentals-complete]] | — | — | — |
| Database Monitoring & Security: pg_stat, RLS, encryp... | — | [[databases-monitoring-security]] | — | — |
| NoSQL: MongoDB, Redis, DynamoDB, Cassandra — когда ч... | — | [[databases-nosql-comparison]] | — | — |
| Replication & Sharding: масштабирование баз данных | — | [[databases-replication-sharding]] | — | — |
| SQL Fundamentals: от SELECT до оконных функций | [[databases-sql-fundamentals]] | — | — | — |
| Transactions & ACID: уровни изоляции, блокировки, de... | — | [[databases-transactions-acid]] | — | — |
| Mobile Databases: Complete Guide | — | [[mobile-databases-complete]] | — | — |
| NoSQL Databases: Complete Guide | — | [[nosql-databases-complete]] | — | — |
| SQL Базы данных: PostgreSQL, MySQL, SQLite — Полный ... | — | [[sql-databases-complete]] | — | — |

---

### DevOps (10 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| CI/CD: автоматизация, которая меняет всё | — | [[ci-cd-pipelines]] | — | — |
| Incident Management: On-call, Runbooks, Post-mortems | — | [[devops-incident-management]] | — | — |
| Docker для разработчиков: от хаоса к порядку | — | [[docker-for-developers]] | — | — |
| Git Workflows: от хаоса к порядку | — | [[git-workflows]] | — | — |
| GitOps: ArgoCD, Flux, Declarative Deployments | — | [[gitops-argocd-flux]] | — | — |
| Infrastructure as Code: Terraform и декларативный по... | — | [[infrastructure-as-code]] | — | — |
| Kubernetes Advanced: RBAC, Network Policies, Operators | — | — | [[kubernetes-advanced]] | — |
| Kubernetes: оркестрация контейнеров | [[kubernetes-basics]] | — | — | — |
| Observability: видеть, что происходит в системе | — | [[observability]] | — | — |

---

### JVM (37 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| JVM Annotations & Processing - Метапрограммирование ... | — | — | [[jvm-annotations-processing]] | — |
| JVM Bytecode Manipulation - ASM, Javassist, ByteBuddy | — | — | [[jvm-bytecode-manipulation]] | — |
| JVM Instrumentation & Agents - Модификация байткода ... | — | — | [[jvm-instrumentation-agents]] | — |
| JVM JNI - Java Native Interface | — | — | [[jvm-jni-deep-dive]] | — |
| Java Module System (JPMS): Модульность и инкапсуляция | — | — | [[jvm-module-system]] | — |
| Reflection API: Интроспекция и динамическое поведени... | — | — | [[jvm-reflection-api]] | — |
| JVM Security Model - Модель безопасности Java | — | — | [[jvm-security-model]] | — |
| JVM ServiceLoader & SPI - Service Provider Interface | — | — | [[jvm-service-loader-spi]] | — |
| GC Tuning: выбор и настройка сборщика мусора | — | [[jvm-gc-tuning]] | — | — |
| JVM Memory Model: где живут объекты | — | [[jvm-memory-model]] | — | — |
| JVM Performance: карта оптимизации | [[jvm-performance-overview]] | — | — | — |
| Class Loader: как JVM загружает классы | [[jvm-class-loader-deep-dive]] | — | — | — |
| JIT Compiler: как JVM ускоряет код | [[jvm-jit-compiler]] | — | — | — |
| Виртуальная машина: что это и зачем | [[jvm-virtual-machine-concept]] | — | — | — |
| Java Modern Features: От Java 8 до Java 21 | — | [[java-modern-features]] | — | — |
| JVM Languages: Kotlin, Scala, Clojure, Groovy | — | [[jvm-languages-ecosystem]] | — | — |
| Kotlin Advanced Features: Extension Functions, Deleg... | — | — | [[kotlin-advanced-features]] | — |
| Kotlin: Основы языка | [[kotlin-basics]] | — | — | — |
| Kotlin Best Practices: Идиоматичный код и оптимизация | — | [[kotlin-best-practices]] | — | — |
| Kotlin Collections API: List, Set, Map и их операции | — | [[kotlin-collections]] | — | — |
| Kotlin Coroutines: Асинхронное программирование | — | [[kotlin-coroutines]] | — | — |
| Kotlin Flow: Реактивные потоки данных | — | [[kotlin-flow]] | — | — |
| Kotlin Functional Programming: Lambdas, Higher-Order... | — | [[kotlin-functional]] | — | — |
| Kotlin-Java Interoperability: Интеграция с Java | — | [[kotlin-interop]] | — | — |
| Kotlin: Объектно-ориентированное программирование | — | [[kotlin-oop]] | — | — |
| Kotlin Testing: JUnit, MockK, Kotest, Coroutines Tes... | — | [[kotlin-testing]] | — | — |
| Kotlin Type System: Generics, Variance, Reified Types | — | [[kotlin-type-system]] | — | — |
| JVM Concurrent Collections: потокобезопасные коллекции | — | [[jvm-concurrent-collections]] | — | — |
| JVM Executors & Futures: управление потоками | — | [[jvm-executors-futures]] | — | — |
| JVM Synchronization: synchronized, volatile, atomic | — | [[jvm-synchronization]] | — | — |
| JMH: правильные бенчмарки в Java | — | [[jvm-benchmarking-jmh]] | — | — |
| JVM Production Debugging: диагностика без downtime | — | [[jvm-production-debugging]] | — | — |
| JVM Profiling: как найти bottleneck | — | [[jvm-profiling]] | — | — |

#### Gaps:
- [ ] JVM: экспертный уровень (expert) -- отсутствует

---

### Networking (23 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Bluetooth: от гарнитур до IoT mesh | — | [[network-bluetooth]] | — | — |
| Сотовые сети: от GSM до 5G | — | [[network-cellular]] | — | — |
| Облачные сети: VPC, Load Balancing, CDN | — | [[network-cloud-modern]] | — | — |
| Network Debugging Basics | [[network-debugging-basics]] | — | — | — |
| DNS и TLS: имена и безопасность | — | [[network-dns-tls]] | — | — |
| Docker Networking Deep Dive | — | — | [[network-docker-deep-dive]] | — |
| Сетевые основы для разработчиков | [[network-fundamentals-for-developers]] | — | — | — |
| Эволюция HTTP: от 1.0 до QUIC | — | [[network-http-evolution]] | — | — |
| IP-адресация и маршрутизация | — | [[network-ip-routing]] | — | — |
| Kubernetes Networking Deep Dive | — | — | [[network-kubernetes-deep-dive]] | — |
| Network Latency Optimization | — | — | [[network-latency-optimization]] | — |
| Network Observability | — | [[network-observability]] | — | — |
| Network Performance Optimization | — | — | [[network-performance-optimization]] | — |
| Физический и канальный уровень: Ethernet, WiFi, MAC | — | [[network-physical-layer]] | — | — |
| Real-time протоколы: WebSocket, SSE, WebRTC, gRPC | — | [[network-realtime-protocols]] | — | — |
| Network Security Fundamentals | [[network-security-fundamentals]] | — | — | — |
| Network Packet Analysis: tcpdump & Wireshark | — | [[network-tcpdump-wireshark]] | — | — |
| Network Tools Reference | — | [[network-tools-reference]] | — | — |
| Транспортный уровень: TCP, UDP, QUIC | — | [[network-transport-layer]] | — | — |
| Advanced Network Troubleshooting | — | — | [[network-troubleshooting-advanced]] | — |
| Беспроводные IoT протоколы: Zigbee, Thread, Matter, ... | — | [[network-wireless-iot]] | — | — |
| Сетевые технологии: карта раздела | — | — | — | — |
| Сетевой стек ОС: Linux networking, сокеты, netfilter | — | [[os-networking]] | — | — |

#### Gaps:
- [ ] Networking: экспертный уровень (expert) -- отсутствует

---

### Operating Systems (8 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Файловые системы: как данные хранятся на диске | — | [[os-file-systems]] | — | — |
| Ввод/Вывод и устройства: как CPU общается с внешним ... | — | [[os-io-devices]] | — | — |
| Управление памятью: виртуальная память и paging | — | [[os-memory-management]] | — | — |
| Операционные системы: карта раздела | [[os-overview]] | — | — | — |
| Процессы и потоки: единицы выполнения | — | [[os-processes-threads]] | — | — |
| Планирование процессов: как ОС распределяет CPU | — | [[os-scheduling]] | — | — |
| Синхронизация: координация параллельных процессов | — | [[os-synchronization]] | — | — |
| Виртуализация и контейнеры: изоляция окружений | — | [[os-virtualization]] | — | — |

#### Gaps:
- [ ] Operating Systems: продвинутый уровень (advanced) -- отсутствует
- [ ] Operating Systems: перекос к intermediate (88%), нужно разнообразие уровней

---

### Programming (12 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Build Systems: от Make до Gradle | — | [[build-systems-theory]] | — | — |
| Clean Code и SOLID: код, который не стыдно показать | — | [[solid-principles]] | — | — |
| Concurrency & Parallelism: Threads, Async, Race Cond... | — | [[concurrency-fundamentals]] | — | — |
| Dependency Resolution: как разрешаются зависимости | — | [[dependency-resolution]] | — | — |
| Design Patterns: решения, которые уже работают | — | [[design-patterns-overview]] | — | — |
| Error Handling & Resilience: Обработка ошибок и усто... | — | [[error-handling]] | — | — |
| Functional Programming: Pure Functions, Immutability... | — | [[functional-programming]] | — | — |
| Module Systems: модульность от CommonJS до ESM | — | [[module-systems]] | — | — |
| Refactoring Techniques: Улучшение кода без изменения... | — | [[refactoring-catalog]] | — | — |
| Testing: пирамида, которая спасает от 3am багов | — | [[testing-fundamentals]] | — | — |
| Type Systems: теория и практика систем типов | — | [[type-systems-theory]] | — | — |

#### Gaps:
- [ ] Programming: начальный уровень (beginner) -- отсутствует
- [ ] Programming: продвинутый уровень (advanced) -- отсутствует
- [ ] Programming: перекос к intermediate (100%), нужно разнообразие уровней

---

### Security (13 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| Authentication & Authorization: кто ты и что тебе можно | — | [[authentication-authorization]] | — | — |
| Mobile App Protection: Защита приложений от атак | — | [[mobile-app-protection]] | — | — |
| OWASP MASVS & MASTG: Mobile Application Security Ver... | — | [[mobile-security-masvs]] | — | — |
| OWASP Mobile Top 10 2024: Угрозы мобильных приложений | — | [[mobile-security-owasp]] | — | — |
| API Protection: rate limiting, input validation, API... | — | [[security-api-protection]] | — | — |
| Cryptography Fundamentals: шифрование, хеширование, ... | [[security-cryptography-fundamentals]] | — | — | — |
| Security Fundamentals: Основы информационной безопас... | [[security-fundamentals]] | — | — | — |
| HTTPS & TLS: handshake, сертификаты, certificate pin... | — | [[security-https-tls]] | — | — |
| Incident Response: detection, containment, recovery | — | [[security-incident-response]] | — | — |
| Secrets Management: Vault, rotation, environment var... | — | [[security-secrets-management]] | — | — |
| Threat Modeling: Моделирование угроз | — | [[threat-modeling]] | — | — |
| Web Security: OWASP Top 10 и защита приложений | — | [[web-security-owasp]] | — | — |

#### Gaps:
- [ ] Security: продвинутый уровень (advanced) -- отсутствует

---

### Thinking & Learning (22 файлов)

| Тема | Beginner | Intermediate | Advanced | Expert |
|------|:--------:|:------------:|:--------:|:------:|
| AI и мышление: усиление, а не замена | — | [[ai-augmented-thinking]] | — | — |
| Кризис внимания: 47 секунд и что с этим делать | — | [[attention-crisis]] | — | — |
| Burnout: как не сгореть на работе | — | [[burnout-prevention]] | — | — |
| Когнитивные искажения: ловушки разума | — | [[cognitive-biases]] | — | — |
| Теория когнитивной нагрузки: почему сложное кажется ... | — | [[cognitive-load-theory]] | — | — |
| Переключение контекста: скрытый убийца продуктивности | — | [[context-switching]] | — | — |
| Deep Work: фокус в мире отвлечений | — | [[deep-work]] | — | — |
| Deliberate Practice: 10,000 часов - это миф | — | [[deliberate-practice]] | — | — |
| Desirable Difficulties: почему сложнее — значит лучше | — | [[desirable-difficulties]] | — | — |
| Писать так, чтобы читали: контент в эпоху СДВГ | — | [[engaging-writing]] | — | — |
| Физическая активность и мозг: двигайся, чтобы думать | — | [[exercise-and-brain]] | — | — |
| Flow State: когда работа становится игрой | — | [[flow-state]] | — | — |
| Как мозг учится: нейронаука обучения | — | [[how-brain-learns]] | — | — |
| Как учиться сложным вещам: научный подход | — | [[learning-complex-things]] | — | — |
| Ментальные модели: инструментарий мышления | — | [[mental-models]] | — | — |
| Метакогниция: думать о том, как ты думаешь | — | [[metacognition]] | — | — |
| Наука мотивации: почему награды не работают | — | [[motivation-science]] | — | — |
| Прокрастинация: это не лень, а эмоции | — | [[procrastination-science]] | — | — |
| Сон и обучение: почему всё забывается без отдыха | — | [[sleep-and-learning]] | — | — |
| Системное мышление: видеть лес за деревьями | — | [[systems-thinking]] | — | — |
| Transfer of Learning: как применять знания | — | [[transfer-of-learning]] | — | — |

#### Gaps:
- [ ] Thinking & Learning: начальный уровень (beginner) -- отсутствует
- [ ] Thinking & Learning: продвинутый уровень (advanced) -- отсутствует
- [ ] Thinking & Learning: экспертный уровень (expert) -- отсутствует
- [ ] Thinking & Learning: перекос к intermediate (100%), нужно разнообразие уровней

---

## Общие пробелы

### Области с минимальным покрытием


### Области без beginner-контента

- [ ] **Career** -- нет файлов beginner уровня
- [ ] **Cloud** -- нет файлов beginner уровня
- [ ] **CS Foundations (KMP)** -- нет файлов beginner уровня
- [ ] **Programming** -- нет файлов beginner уровня
- [ ] **Thinking & Learning** -- нет файлов beginner уровня

### Области без expert-контента

- [ ] **AI/ML** -- нет файлов expert уровня
- [ ] **Architecture** -- нет файлов expert уровня
- [ ] **Career** -- нет файлов expert уровня
- [ ] **Communication** -- нет файлов expert уровня
- [ ] **Cross-Platform** -- нет файлов expert уровня
- [ ] **Databases** -- нет файлов expert уровня
- [ ] **iOS** -- нет файлов expert уровня
- [ ] **JVM** -- нет файлов expert уровня
- [ ] **Kotlin Multiplatform** -- нет файлов expert уровня
- [ ] **Leadership** -- нет файлов expert уровня
- [ ] **Networking** -- нет файлов expert уровня
- [ ] **Programming** -- нет файлов expert уровня
- [ ] **Security** -- нет файлов expert уровня
- [ ] **Thinking & Learning** -- нет файлов expert уровня

---

## Связанные файлы

- [[frontmatter-standard]] -- стандарт метаданных
- [[tag-taxonomy]] -- таксономия тегов
- [[content-levels]] -- описание уровней сложности

---

*Сгенерировано: 2026-02-10*