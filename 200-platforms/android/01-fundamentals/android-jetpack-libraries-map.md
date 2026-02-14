---
title: "Карта Jetpack (AndroidX) библиотек"
created: 2026-02-14
modified: 2026-02-14
type: reference
status: published
confidence: high
area: android
tags:
  - topic/android
  - topic/jetpack
  - type/reference
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-compose]]"
  - "[[android-ecosystem-2026]]"
prerequisites:
  - "[[android-overview]]"
reading_time: 18
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Карта Jetpack (AndroidX) библиотек

В экосистеме AndroidX более 80 библиотек, но для типичного production-проекта достаточно ~15. Этот файл — навигационная карта: что делает каждая библиотека, когда она нужна и какие версии актуальны на февраль 2026.

> **Ключевой принцип:** AndroidX — это набор библиотек, которые поставляются отдельно от платформы Android. Они обновляются чаще, чем ОС, и обеспечивают обратную совместимость. С июня 2025 года default minSdk для новых релизов AndroidX повышен до **API 23** (Android 6.0).

---

## Архитектура Jetpack: общий обзор

```
┌─────────────────────────────────────────────────────────────────┐
│                          TEST                                   │
│  espresso · ui-test · benchmark · test.core · test.runner       │
├─────────────────────────────────────────────────────────────────┤
│                        BEHAVIOR                                 │
│  camerax · media3 · biometric · credentials · browser · webkit  │
├─────────────────────────────────────────────────────────────────┤
│                           UI                                    │
│  compose (ui, foundation, material3, animation, runtime)        │
│  constraintlayout · recyclerview · viewpager2 · splashscreen    │
│  window                                                         │
├─────────────────────────────────────────────────────────────────┤
│                      ARCHITECTURE                               │
│  lifecycle · navigation · paging · room · datastore · work      │
│  hilt                                                           │
├─────────────────────────────────────────────────────────────────┤
│                       FOUNDATION                                │
│  core-ktx · appcompat · activity · fragment · annotation        │
│  startup · collection                                           │
└─────────────────────────────────────────────────────────────────┘
```

### Как работает BOM

**BOM (Bill of Materials)** — это POM-файл, который фиксирует совместимые версии группы библиотек. Подключаешь одну версию BOM, и все библиотеки группы автоматически получают проверенные версии:

```kotlin
// build.gradle.kts
val composeBom = platform("androidx.compose:compose-bom:2026.01.01")
implementation(composeBom)
implementation("androidx.compose.ui:ui")           // версия из BOM
implementation("androidx.compose.material3:material3") // версия из BOM
```

**Version Catalogs** (`libs.versions.toml`) — механизм Gradle для централизованного управления версиями всех зависимостей проекта, не только AndroidX. Подробнее: [[android-dependencies]].

---

## 1. Foundation Libraries

Базовый слой — эти библиотеки нужны практически каждому приложению.

### core-ktx

**Артефакт:** `androidx.core:core-ktx`
Набор Kotlin extension functions для Android framework API: упрощённая работа с `SharedPreferences`, `Bundle`, `Canvas`, `View` и др. Без неё можно обойтись, но код будет значительно многословнее.

### appcompat

**Артефакт:** `androidx.appcompat:appcompat`
Обратная совместимость UI-компонентов (ActionBar, Toolbar, Theme) до API 21+. В Compose-only проектах нужен, если используются Activity из `AppCompatActivity` (для поддержки Material themes).

### activity и fragment

**Артефакты:** `androidx.activity:activity-compose`, `androidx.fragment:fragment-ktx`
- `activity-compose` — интеграция Compose с Activity (setContent, result API)
- `activity-ktx` — `registerForActivityResult()`, `viewModels()` delegate
- `fragment-ktx` — Kotlin extensions для Fragment (актуально для View-based проектов)

В чистом Compose-проекте Fragment не нужен. Activity остаётся точкой входа.

### annotation

**Артефакт:** `androidx.annotation:annotation`
Аннотации `@NonNull`, `@IntDef`, `@WorkerThread`, `@MainThread` и др. Помогают статическому анализу и Lint. Добавляются транзитивно через другие библиотеки.

### startup (App Startup)

**Артефакт:** `androidx.startup:startup-runtime`
Lazy-инициализация компонентов при старте приложения. Заменяет множество `ContentProvider`-ов (каждый из которых замедляет cold start) единой точкой инициализации. Подробнее: [[android-app-startup-performance]].

### multidex

**Артефакт:** `androidx.multidex:multidex`
**Legacy.** Не нужен при `minSdk >= 21` (API 21+ поддерживает multidex нативно). Если ваш minSdk 23+ (что рекомендуется с 2025), эта библиотека полностью избыточна.

---

## 2. Architecture Libraries

Скелет приложения — управление жизненным циклом, данными и фоновой работой.

### lifecycle

**Артефакты:** `lifecycle-viewmodel-compose`, `lifecycle-runtime-compose`, `lifecycle-livedata-ktx`

Центральная библиотека архитектуры Android:

| Компонент | Назначение |
|-----------|-----------|
| **ViewModel** | Хранение UI-состояния, переживает Configuration Change |
| **SavedStateHandle** | Сохранение состояния при process death |
| **LiveData** | Observable-контейнер с lifecycle-awareness (legacy, заменяется на Flow) |
| **ProcessLifecycleOwner** | Отслеживание foreground/background на уровне всего приложения |
| **Lifecycle** | Базовый lifecycle-aware интерфейс |

> **Важно:** `lifecycle-extensions` **deprecated**. Подключайте конкретные артефакты: `lifecycle-viewmodel-compose`, `lifecycle-runtime-compose`.

### navigation

**Артефакты:** `navigation-compose`, `navigation3`

Навигация в приложении: маршруты, deep links, Safe Args.

- **Navigation 2** (`navigation-compose`) — стабильная версия, работает с XML и Compose
- **Navigation 3** (`navigation3`) — **stable с ноября 2025**. Полностью переработана для Compose: разработчик сам контролирует back stack, лучшая интеграция с Compose state, поддержка adaptive layouts для foldables

Navigation 3 — рекомендуемый выбор для новых Compose-проектов. Подробнее: [[android-navigation]].

### paging 3

**Артефакт:** `androidx.paging:paging-compose`

Пагинация данных из сети, БД или комбинированных источников:
- `PagingSource` — единственный источник данных (только сеть или только БД)
- `RemoteMediator` — комбинация сети + Room как кэша
- `LoadState` — состояния загрузки (Loading, Error, NotLoading)

### room

**Артефакт:** `androidx.room:room-ktx`, `room-compiler` (KSP)

Абстракция над SQLite с compile-time проверкой SQL-запросов, поддержкой Flow, миграциями. Стандарт для локальных баз данных на Android. Подробнее: [[android-room-deep-dive]].

### datastore

**Артефакт:** `androidx.datastore:datastore-preferences`, `datastore-proto`

Замена `SharedPreferences` с поддержкой coroutines и Flow. Два варианта:
- **Preferences DataStore** — key-value (как SharedPreferences, но асинхронно)
- **Proto DataStore** — типизированное хранилище на базе Protocol Buffers

Подробнее: [[android-datastore-guide]].

### work (WorkManager)

**Артефакт:** `androidx.work:work-runtime-ktx`

Гарантированное выполнение фоновых задач (даже после перезагрузки устройства): sync, upload, периодические задачи. Использует JobScheduler / AlarmManager под капотом. Подробнее: [[android-background-work]].

### hilt

**Артефакт:** `com.google.dagger:hilt-android`, `hilt-compiler`

DI-фреймворк, рекомендованный Google. Надстройка над Dagger 2 с упрощённой конфигурацией для Android-компонентов (`@HiltAndroidApp`, `@AndroidEntryPoint`, `@HiltViewModel`). Подробнее: [[android-hilt-deep-dive]].

---

## 3. UI Libraries

### compose

**BOM:** `androidx.compose:compose-bom:2026.01.01`
**Версии (декабрь 2025):** Compose 1.10, Material 3 v1.4

| Модуль | Назначение |
|--------|-----------|
| `compose-ui` | Рендеринг, Layout, Modifier, Input |
| `compose-foundation` | Row, Column, LazyColumn, Scrolling, Gestures |
| `compose-material3` | Material 3 компоненты (Button, Card, TextField, TopAppBar) |
| `compose-runtime` | Ядро реактивности: State, remember, Composition |
| `compose-animation` | Анимации: AnimatedVisibility, animateAsState, Transition |

Новое в Material 3 v1.4: `TextFieldState`-based `TextField`, `SecureTextField`, autoSize для `Text`, `HorizontalCenteredHeroCarousel`.

Подробнее: [[android-compose]], [[android-compose-internals]].

### constraintlayout

**Артефакт:** `androidx.constraintlayout:constraintlayout-compose`

ConstraintLayout 2.x + **MotionLayout** для сложных анимированных переходов. В Compose менее востребован благодаря гибкой системе Layout, но полезен для сложных responsive layouts.

### recyclerview

**Артефакт:** `androidx.recyclerview:recyclerview`

Эффективный список с переиспользованием ViewHolder. В View-based проектах — стандарт. В Compose заменён на `LazyColumn` / `LazyRow`. Подробнее: [[android-recyclerview-internals]].

### viewpager2

**Артефакт:** `androidx.viewpager2:viewpager2`

Замена устаревшего ViewPager. Горизонтальный/вертикальный пейджинг с RecyclerView под капотом. В Compose используется `HorizontalPager` из `foundation`.

### splashscreen

**Артефакт:** `androidx.core:core-splashscreen`

Стандартизированный splash screen для Android 12+ с обратной совместимостью до API 23. Управляет анимацией при cold/warm start.

### window

**Артефакт:** `androidx.window:window`

Информация о window layout для поддержки foldables и больших экранов (планшеты, desktop mode). Определяет fold state, hinge position, display features.

---

## 4. Behavior Libraries

Интеграция с hardware и системными сервисами.

### camera (CameraX)

**Артефакт:** `androidx.camera:camera-camera2`, `camera-lifecycle`, `camera-view`
**Стабильная версия:** 1.5.x; **Beta:** 1.6.0-beta02 (январь 2026)

CameraX — абстракция над Camera2 API:

| Use Case | Назначение |
|----------|-----------|
| `Preview` | Предпросмотр камеры |
| `ImageCapture` | Фото (JPEG, включая HDR) |
| `VideoCapture` | Видеозапись |
| `ImageAnalysis` | Реалтайм анализ кадров (ML, QR-сканер) |

CameraX 1.5 принёс pro-level capture и улучшенную запись видео. В 1.6 добавлена интеграция с Media3 muxer, что устранило повреждение видео при неожиданном завершении приложения.

### media3

**Артефакт:** `androidx.media3:media3-exoplayer`, `media3-session`, `media3-ui`
**Версия:** 1.9.0 (декабрь 2025)

ExoPlayer объединён в Media3 — единая библиотека для воспроизведения медиа:

| Модуль | Назначение |
|--------|-----------|
| `media3-exoplayer` | Ядро плеера (HLS, DASH, SmoothStreaming, progressive) |
| `media3-session` | MediaSession для фонового воспроизведения и управления через системный UI |
| `media3-ui` | Готовый PlayerView |
| `media3-ui-compose-material3` | **Новый** — Compose UI для Media3 |
| `media3-transformer` | Транскодирование и редактирование видео |
| `media3-decoder-av1` | SW-декодер AV1 |
| `media3-inspector` | **Новый** — отладочный инспектор плеера |

### biometric

**Артефакт:** `androidx.biometric:biometric`

`BiometricPrompt` — стандартный диалог для аутентификации через отпечаток, Face ID, iris. Поддерживает fallback на device credential (PIN/pattern/password). Один API вместо ручного определения доступных методов биометрии.

### credentials (Credential Manager)

**Артефакт:** `androidx.credentials:credentials`, `credentials-play-services-auth`

**Рекомендованный API для аутентификации** с 2024 года. Объединяет в одном интерфейсе:
- **Passkeys** — криптографические ключи вместо паролей (FIDO2/WebAuthn)
- **Passwords** — классические пароли из менеджера паролей
- **Federated sign-in** — Google Sign-In, Apple Sign-In

Результаты индустрии: X (Twitter) — 2x рост login rate, KAYAK — 50% сокращение времени sign-up/sign-in, Zoho — 6x быстрее логин.

### browser (Custom Tabs)

**Артефакт:** `androidx.browser:browser`

Открытие ссылок в Custom Tabs (Chrome или другой default-браузер) внутри приложения. Быстрее, чем WebView, безопаснее, чем внешний intent.

### webkit

**Артефакт:** `androidx.webkit:webkit`

Расширенные возможности WebView: proxy, safe browsing, dark mode, JavaScript evaluation. Нужен только если в приложении используется WebView.

---

## 5. Test Libraries

### compose.ui:ui-test

**Артефакт:** `androidx.compose.ui:ui-test-junit4`

`ComposeTestRule` для тестирования Compose UI: поиск по semantics, assertions, жесты (click, swipe, scroll). Работает без эмулятора (Robolectric) и на устройстве.

### espresso

**Артефакт:** `androidx.test.espresso:espresso-core`

UI-автоматизация для View-based UI: onView(), perform(), check(). В Compose-проектах заменяется на `ui-test`.

### test.ext:junit / test.core / test.runner

**Артефакты:** `androidx.test.ext:junit`, `androidx.test:core`, `androidx.test:runner`

`AndroidJUnit4` runner, `ActivityScenario`, `ApplicationProvider` — базовая инфраструктура для instrumented-тестов.

### benchmark

**Артефакты:** `androidx.benchmark:benchmark-macro-junit4`, `benchmark-micro`

| Тип | Что измеряет |
|-----|-------------|
| **Microbenchmark** | Производительность отдельных функций/алгоритмов (наносекунды) |
| **Macrobenchmark** | App startup time, scroll jank, animation frame duration |

Версия 1.5.0 в alpha (январь 2026). Подробнее: [[android-testing]].

---

## 6. Управление версиями

### BOM (Bill of Materials)

| BOM | Что покрывает | Актуальная версия |
|-----|-------------|------------------|
| **Compose BOM** | compose-ui, foundation, material3, animation, runtime | `2026.01.01` |
| **Firebase BOM** | Analytics, Crashlytics, Auth, Firestore и др. | `33.x` |
| **OkHttp BOM** | okhttp, logging-interceptor, mockwebserver | `4.12.x` |

**Правило:** если для группы библиотек существует BOM — всегда используй его. Это гарантирует совместимость версий.

### Version Catalogs

Файл `gradle/libs.versions.toml` централизует все версии проекта:

```toml
[versions]
compose-bom = "2026.01.01"
room = "2.7.0"
hilt = "2.53"

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }

[plugins]
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
```

Подробнее: [[android-dependencies]].

---

## 7. Deprecated / Removed

Что устарело и чем заменено:

| Было | Стало | Когда |
|------|-------|-------|
| Support Library (`com.android.support`) | **AndroidX** (`androidx.*`) | 2018 |
| ViewPager | **ViewPager2** | 2019 |
| AsyncTask | **Coroutines** | 2020 |
| SharedPreferences | **DataStore** | 2021 |
| LiveData (в Compose) | **StateFlow** + `collectAsStateWithLifecycle()` | 2022 |
| ExoPlayer (`com.google.android.exoplayer2`) | **Media3** (`androidx.media3`) | 2023 |
| SafetyNet Attestation | **Play Integrity API** | 2024 (полностью отключён янв. 2025) |
| EncryptedSharedPreferences | **DataStore + Tink** | 2025 |
| Accompanist (insets, pager, systemuicontroller, navigation-material) | **Compose core** (foundation, material3) | 2023-2025 |
| lifecycle-extensions | Конкретные артефакты (`lifecycle-viewmodel`, `lifecycle-runtime`) | 2021 |
| AbstractSavedStateViewModelFactory | `ViewModelProvider.Factory` + `CreationExtras.createSavedStateHandle()` | 2024 |
| Navigation 2 (для новых проектов) | **Navigation 3** | ноябрь 2025 |

> **Accompanist:** Библиотека-инкубатор от Google. Успешные модули (Insets, Pager, System UI Controller, Navigation Material) перенесены в core Compose и deprecated в Accompanist. Оставшиеся модули (Permissions, Placeholder) ещё поддерживаются, но также ожидают upstreaming.

---

## 8. Starter Template: зависимости для нового проекта 2026

Минимальный набор для production-ready Compose-приложения:

| # | Артефакт | Зачем |
|---|----------|-------|
| 1 | `compose-bom:2026.01.01` | BOM для всех Compose-библиотек |
| 2 | `compose-ui` + `compose-material3` | UI-слой |
| 3 | `activity-compose` | Точка входа: `setContent {}` |
| 4 | `lifecycle-runtime-compose` | `collectAsStateWithLifecycle()` |
| 5 | `lifecycle-viewmodel-compose` | `viewModel()` в Compose |
| 6 | `navigation3` | Навигация (или navigation-compose для Nav2) |
| 7 | `room-runtime` + `room-compiler` (KSP) | Локальная БД |
| 8 | `datastore-preferences` | Key-value настройки |
| 9 | `work-runtime-ktx` | Фоновые задачи |
| 10 | `hilt-android` + `hilt-compiler` | DI |
| 11 | `hilt-navigation-compose` | Интеграция Hilt + Navigation |
| 12 | `core-splashscreen` | Splash screen |
| 13 | `compose-ui-test-junit4` | Тестирование UI |
| 14 | `benchmark-macro-junit4` | Тестирование производительности |
| 15 | `credentials` | Аутентификация (passkeys) |

**Вне AndroidX, но де-факто стандарт:**
- `kotlinx-coroutines-android` — structured concurrency
- `kotlinx-serialization-json` — JSON сериализация
- `ktor-client` или `retrofit` — HTTP-клиент
- `coil-compose` — загрузка изображений
- `timber` — логирование

---

## Проверь себя

**Q1:** Зачем нужен Compose BOM, если можно указать версии напрямую?

> BOM гарантирует совместимость версий между модулями Compose. Без BOM можно случайно смешать compose-ui 1.10 с material3 1.2, что вызовет runtime-ошибки. BOM — единая точка обновления: меняешь одну версию, все модули обновляются согласованно.

**Q2:** Когда нужен AppCompat в Compose-проекте?

> AppCompat нужен, когда Activity наследуется от `AppCompatActivity` (а не `ComponentActivity`). Это требуется для Material theming (если используются AppCompat-темы), для backward-compatible ActionBar/Toolbar, и для корректной работы некоторых библиотек, ожидающих AppCompatActivity.

**Q3:** Чем Navigation 3 принципиально отличается от Navigation 2?

> В Nav2 фреймворк сам управляет back stack (внутреннее состояние). В Nav3 разработчик контролирует back stack как обычный Compose state (например, `mutableStateListOf`). Это даёт: единый source of truth, предсказуемое поведение в reactive UI, простую поддержку adaptive layouts для foldables и больших экранов.

---

## Ключевые карточки

**Карточка 1**
Front: Что делает Compose BOM `2026.01.01`?
Back: Фиксирует совместимые версии всех Compose-библиотек (ui 1.10, material3 1.4 и др.). Подключается через `platform()`, после чего версии отдельных модулей указывать не нужно.

**Карточка 2**
Front: Чем DataStore отличается от SharedPreferences?
Back: DataStore работает асинхронно через coroutines/Flow (нет ANR от чтения на main thread), поддерживает типизацию через Proto, имеет атомарные обновления. SharedPreferences — синхронный, без type safety, с рисками потери данных при concurrent write.

**Карточка 3**
Front: Что такое Credential Manager и зачем он?
Back: Единый API для аутентификации: passkeys (FIDO2), пароли, federated sign-in (Google, Apple). Заменяет отдельные библиотеки SmartLock, FIDO2 API. Поддержка passkeys — основной тренд аутентификации 2025-2026.

**Карточка 4**
Front: Почему ExoPlayer deprecated?
Back: ExoPlayer (`com.google.android.exoplayer2`) объединён в **Media3** (`androidx.media3`). Media3 — единая библиотека для воспроизведения, сессий, UI и транскодирования. ExoPlayer API сохранён внутри Media3, миграция минимальна (в основном смена импортов).

**Карточка 5**
Front: Когда multidex НЕ нужен?
Back: При `minSdk >= 21` (API 21+). ART runtime нативно поддерживает multiple DEX files. С 2025 года AndroidX рекомендует minSdk 23, что делает multidex полностью избыточным.

---

## Куда дальше

- [[android-compose]] — глубокое погружение в Compose UI
- [[android-compose-internals]] — как работает Compose runtime
- [[android-navigation]] — навигация (Nav2 и Nav3)
- [[android-room-deep-dive]] — Room: запросы, миграции, производительность
- [[android-hilt-deep-dive]] — Hilt и Dagger под капотом
- [[android-dependencies]] — Gradle, Version Catalogs, dependency management
- [[android-testing]] — стратегии тестирования
- [[android-app-startup-performance]] — оптимизация старта приложения
- [[android-background-work]] — WorkManager и фоновые задачи
- [[android-datastore-guide]] — DataStore vs SharedPreferences
- [[android-recyclerview-internals]] — RecyclerView (для View-based проектов)

---

## Источники

- [AndroidX Releases — official version table](https://developer.android.com/jetpack/androidx/versions)
- [Compose BOM to library version mapping](https://developer.android.com/develop/ui/compose/bom/bom-mapping)
- [What's new in Jetpack Compose December '25 release](https://android-developers.googleblog.com/2025/12/whats-new-in-jetpack-compose-december.html)
- [Jetpack Navigation 3 is stable](https://android-developers.googleblog.com/2025/11/jetpack-navigation-3-is-stable.html)
- [Introducing CameraX 1.5](https://android-developers.googleblog.com/2025/11/introducing-camerax-15-powerful-video.html)
- [Media3 1.9.0 — What's new](https://android-developers.googleblog.com/2025/12/media3-190-whats-new.html)
- [Credential Manager — Android Developers](https://developer.android.com/identity/credential-manager)
- [Goodbye EncryptedSharedPreferences: A 2026 Migration Guide](https://www.droidcon.com/2025/12/16/goodbye-encryptedsharedpreferences-a-2026-migration-guide/)
- [Accompanist — GitHub](https://github.com/google/accompanist)
