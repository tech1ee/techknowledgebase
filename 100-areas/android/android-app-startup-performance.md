---
title: "App Startup & Performance — от Zygote до первого кадра"
area: android
tags:
  - android
  - performance
  - startup
  - baseline-profiles
  - macrobenchmark
  - optimization
related:
  - "[[android-overview]]"
  - "[[android-compilation-pipeline]]"
  - "[[android-process-memory]]"
  - "[[android-view-rendering-pipeline]]"
  - "[[android-content-provider-internals]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-handler-looper]]"
  - "[[android-performance-profiling]]"
---

# App Startup & Performance — от Zygote до первого кадра

## Зачем это нужно

**Проблема:** Пользователь нажимает на иконку приложения и ждёт. Каждые 100ms задержки старта увеличивают вероятность "отвала" на 10-15%. Google Play Console показывает startup metrics, и приложения с медленным стартом ранжируются ниже.

**Решение:** Понимание полного пути запуска — от fork процесса в Zygote до рисования первого кадра — позволяет находить и устранять узкие места. Инструменты: App Startup library, Baseline Profiles, Startup Profiles, Macrobenchmark, Perfetto.

**Ключевой инсайт:** Startup — это НЕ "просто onCreate()". Это цепочка из ~20 этапов, и ContentProvider.onCreate() вызывается ДО Application.onCreate(). Библиотеки типа Firebase, WorkManager, LeakCanary инициализируются именно там.

```
Нажатие иконки → Launcher → system_server → Zygote fork →
→ ActivityThread → ContentProviders → Application.onCreate() →
→ Activity.onCreate() → setContentView() → measure/layout/draw →
→ ПЕРВЫЙ КАДР (reportFullyDrawn)
```

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| ART & Compilation pipeline | Понять JIT/AOT и как Baseline Profiles ускоряют | `[[android-compilation-pipeline]]` |
| View Rendering Pipeline | measure/layout/draw до первого кадра | `[[android-view-rendering-pipeline]]` |
| Process & Memory | Zygote fork, LMK, process priority | `[[android-process-memory]]` |
| ContentProvider | Почему CP — узкое место старта | `[[android-content-provider-internals]]` |
| Activity Lifecycle | onCreate → onStart → onResume путь | `[[android-activity-lifecycle]]` |
| Handler/Looper | Main thread event loop | `[[android-handler-looper]]` |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Cold Start** | Запуск с нуля: fork процесса, загрузка DEX, init | Холодный двигатель — прогрев с нуля |
| **Warm Start** | Процесс жив, Activity пересоздаётся | Двигатель тёплый — быстрый старт |
| **Hot Start** | Activity в памяти, только onResume | Двигатель работает — просто нажать газ |
| **TTID** | Time To Initial Display — первый кадр | Первая картинка на экране |
| **TTFD** | Time To Full Display — контент готов | Полная загрузка страницы |
| **Baseline Profile** | Предкомпилированный AOT-профиль горячих методов | Разогрев перед соревнованием |
| **Startup Profile** | Подмножество Baseline Profile для стартовых классов | Маршрут прогрева только стартовых мышц |
| **Macrobenchmark** | Инструмент для измерения startup/scroll/animation | Секундомер с точностью до мс |
| **Perfetto** | Системный trace tool (замена systrace) | Рентген всей системы |
| **App Startup library** | Jetpack: замена ContentProvider-инициализации | Один конвейер вместо множества фабрик |
| **Zygote** | Преинициализированный процесс-шаблон | Материнская клетка для всех приложений |
| **reportFullyDrawn()** | Сигнал системе что контент готов | "Я полностью загрузился!" |

---

## 1. Три типа запуска: Cold, Warm, Hot

### 1.1 ЧТО это

Android различает три типа запуска по "температуре":

```
┌─────────────────────────────────────────────────────────────┐
│                    ТИПЫ ЗАПУСКА                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  COLD START (Холодный)                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Zygote fork → Process init → ContentProviders →     │   │
│  │ Application.onCreate() → Activity lifecycle →       │   │
│  │ Window creation → measure/layout/draw               │   │
│  │                                                     │   │
│  │ Время: 500ms — 3000ms+                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  WARM START (Тёплый)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Process alive → Activity.onCreate() →               │   │
│  │ Window creation → measure/layout/draw               │   │
│  │                                                     │   │
│  │ Время: 200ms — 800ms                                │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  HOT START (Горячий)                                       │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Activity in memory → onRestart() → onResume()       │   │
│  │ → possibly re-draw                                  │   │
│  │                                                     │   │
│  │ Время: 50ms — 200ms                                 │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 ПОЧЕМУ это важно

Google определяет пороги для startup в Play Console:

| Метрика | Хорошо | Нужно улучшить | Плохо |
|---------|--------|----------------|-------|
| Cold TTID | < 500ms | 500ms — 1000ms | > 1000ms |
| Warm TTID | < 300ms | 300ms — 500ms | > 500ms |
| Hot TTID | < 100ms | 100ms — 200ms | > 200ms |

Android vitals в Play Console показывает процент пользователей с медленным стартом. Это влияет на:
- Ранжирование в поиске Play Store
- Рейтинг качества приложения
- Retention пользователей

### 1.3 КАК РАБОТАЕТ — полный путь Cold Start

```
┌──────────────────────────────────────────────────────────────────┐
│              ПОЛНЫЙ ПУТЬ COLD START                               │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. LAUNCHER → startActivity()                                   │
│     │                                                            │
│  2. system_server: ActivityTaskManagerService                     │
│     │  - resolve Intent                                          │
│     │  - check permissions                                       │
│     │  - find/create Task                                        │
│     │                                                            │
│  3. Zygote: fork() новый процесс                                │
│     │  - копирует предзагруженные классы (>8000)                │
│     │  - копирует предзагруженные ресурсы                       │
│     │  - Runtime уже инициализирован                             │
│     │                                                            │
│  4. ActivityThread.main()                                        │
│     │  - Looper.prepareMainLooper()                              │
│     │  - создание ActivityThread                                 │
│     │  - attach к system_server через IActivityManager           │
│     │                                                            │
│  5. bindApplication()                                            │
│     │  - LoadedApk: загрузка APK                                │
│     │  - создание Application объекта                            │
│     │  - создание AppComponentFactory (если есть)               │
│     │                                                            │
│  6. installContentProviders()          ← ПЕРВАЯ ИНИЦИАЛИЗАЦИЯ   │
│     │  - ВСЕ ContentProvider из Manifest                        │
│     │  - Firebase, WorkManager, Lifecycle и др.                 │
│     │  - ПОСЛЕДОВАТЕЛЬНО, в main thread                         │
│     │                                                            │
│  7. Application.onCreate()             ← ВТОРАЯ ИНИЦИАЛИЗАЦИЯ   │
│     │  - Dagger/Hilt, analytics, crash reporting                │
│     │                                                            │
│  8. Activity lifecycle                                           │
│     │  - Activity.onCreate() → setContentView()                 │
│     │  - Activity.onStart()                                      │
│     │  - Activity.onResume()                                     │
│     │                                                            │
│  9. ViewRootImpl.performTraversals()                             │
│     │  - measure → layout → draw                                │
│     │  - Surface allocation                                      │
│     │                                                            │
│  10. ПЕРВЫЙ КАДР → SurfaceFlinger composites                    │
│      → TTID (Time To Initial Display)                            │
│                                                                  │
│  11. Данные загружены → reportFullyDrawn()                      │
│      → TTFD (Time To Full Display)                               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 1.4 КАК ПРИМЕНЯТЬ — измерение типа старта

```kotlin
// Определение типа старта программно
class MyApplication : Application() {
    companion object {
        var startType: StartType = StartType.COLD
    }

    override fun onCreate() {
        super.onCreate()
        // Если process уже существовал — warm/hot
        // Cold start всегда начинается с Application.onCreate()
    }
}

// Измерение через adb (logcat фильтр)
// adb logcat -s ActivityTaskManager:I
// Вывод: "Displayed com.example/.MainActivity: +850ms"
// +850ms = TTID для этого запуска
```

```kotlin
// Программное измерение TTFD
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Загружаем данные
        viewModel.data.observe(this) { data ->
            // Данные готовы — сообщаем системе
            adapter.submitList(data)

            // reportFullyDrawn() сообщает:
            // "Весь контент отрисован, можно мерить TTFD"
            reportFullyDrawn()
        }
    }
}
```

### 1.5 ПОДВОДНЫЕ КАМНИ

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠ ОШИБКА: "Мой startup быстрый в debug"                    │
│                                                             │
│  Debug build:                                               │
│  - Debugger attached → дополнительные проверки              │
│  - Нет R8/ProGuard оптимизаций                             │
│  - Нет Baseline Profile (только release)                    │
│  - ART interpreter mode (не compiled)                       │
│                                                             │
│  ВСЕГДА измеряйте на RELEASE build на РЕАЛЬНОМ устройстве! │
│  Разница debug vs release: 2-5x                             │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ⚠ ОШИБКА: reportFullyDrawn() в onCreate()                  │
│                                                             │
│  reportFullyDrawn() = "контент готов"                       │
│  Если вызвать в onCreate() ДО загрузки данных:             │
│  - TTFD будет ложно быстрым                                │
│  - Play Console покажет неверные метрики                    │
│  - Вызывайте ПОСЛЕ реальной готовности контента            │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. ContentProvider — скрытый убийца startup

### 2.1 ЧТО это

ContentProvider-ы из AndroidManifest инициализируются ДО Application.onCreate(). Многие библиотеки используют CP как хук автоинициализации.

### 2.2 ПОЧЕМУ это проблема

```
┌──────────────────────────────────────────────────────────────┐
│         TIMELINE ИНИЦИАЛИЗАЦИИ                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Process fork                                                │
│  ├── ActivityThread.main()                                   │
│  ├── bindApplication()                                       │
│  │   ├── installContentProviders()    ← 200-500ms!          │
│  │   │   ├── FirebaseInitProvider     (~80ms)                │
│  │   │   ├── WorkManagerInitializer   (~30ms)                │
│  │   │   ├── ProcessLifecycleOwnerInit (~15ms)               │
│  │   │   ├── EmojiInitProvider        (~20ms)                │
│  │   │   ├── LeakCanary              (~40ms, debug only)     │
│  │   │   ├── FacebookInitProvider     (~50ms)                │
│  │   │   └── ... другие библиотеки                           │
│  │   │                                                       │
│  │   └── Application.onCreate()       ← ещё 100-300ms       │
│  │       ├── Dagger/Hilt component    (~50ms)                │
│  │       ├── Analytics init           (~30ms)                │
│  │       └── Other SDK init           (~varies)              │
│  │                                                           │
│  └── Activity.onCreate()                                     │
│                                                              │
│  ИТОГО до Activity: 400ms — 1000ms только на init!          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 2.3 КАК РАБОТАЕТ — App Startup Library

Jetpack App Startup заменяет множество ContentProvider-ов одним `InitializationProvider`:

```
БЕЗ App Startup:
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ Firebase CP  │  │ WorkMgr CP  │  │ Emoji CP    │
│ onCreate()   │  │ onCreate()  │  │ onCreate()  │
└──────┬───────┘  └──────┬──────┘  └──────┬──────┘
       │                 │                │
   3 отдельных CP → 3x overhead создания объектов

С App Startup:
┌──────────────────────────────────────────┐
│        InitializationProvider             │
│  ┌──────────────────────────────────┐    │
│  │ AppInitializer                    │    │
│  │ ├── FirebaseInitializer           │    │
│  │ ├── WorkManagerInitializer        │    │
│  │ └── EmojiInitializer             │    │
│  │                                   │    │
│  │ Dependency graph → topological    │    │
│  │ sort → правильный порядок         │    │
│  └──────────────────────────────────┘    │
└──────────────────────────────────────────┘
1 CP вместо N → меньше overhead
```

### 2.4 КАК ПРИМЕНЯТЬ — App Startup

```kotlin
// Шаг 1: Создаём Initializer для каждой библиотеки
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val configuration = Configuration.Builder()
            .setMinimumLoggingLevel(Log.INFO)
            .build()
        WorkManager.initialize(context, configuration)
        return WorkManager.getInstance(context)
    }

    // Зависимости — инициализируются ПЕРЕД этим Initializer
    override fun dependencies(): List<Class<out Initializer<*>>> {
        return emptyList() // нет зависимостей
    }
}

class AnalyticsInitializer : Initializer<AnalyticsClient> {
    override fun create(context: Context): AnalyticsClient {
        // Инициализация после WorkManager (зависимость)
        return AnalyticsClient.init(context)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return listOf(WorkManagerInitializer::class.java)
    }
}
```

```xml
<!-- Шаг 2: AndroidManifest.xml -->
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">

    <!-- Автоматическая инициализация -->
    <meta-data
        android:name="com.example.WorkManagerInitializer"
        android:value="androidx.startup" />

    <!-- Отключение автоинициализации библиотеки -->
    <!-- (она использовала свой CP) -->
    <meta-data
        android:name="androidx.work.WorkManagerInitializer"
        android:value="androidx.startup"
        tools:node="remove" />
</provider>
```

```kotlin
// Шаг 3: Ленивая инициализация (по требованию)
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Инициализируем Analytics только когда нужно
        val analytics = AppInitializer.getInstance(this)
            .initializeComponent(AnalyticsInitializer::class.java)
    }
}
```

```xml
<!-- Для ленивой инициализации — отключаем auto -->
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">
    <meta-data
        android:name="com.example.AnalyticsInitializer"
        tools:node="remove" />
</provider>
```

### 2.5 ПОДВОДНЫЕ КАМНИ

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠ Firebase отключение CP                                    │
│                                                             │
│  Firebase использует FirebaseInitProvider.                   │
│  Просто tools:node="remove" может сломать Firebase!         │
│                                                             │
│  Правильно:                                                 │
│  1. Добавить Firebase Initializer для App Startup           │
│  2. Вызвать FirebaseApp.initializeApp(context) в create()   │
│  3. Только потом отключить FirebaseInitProvider             │
│                                                             │
│  Тестируйте КАЖДУЮ библиотеку после миграции!              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Baseline Profiles — предкомпиляция горячего кода

### 3.1 ЧТО это

Baseline Profile — файл с перечнем классов и методов, которые ART должен скомпилировать AOT (Ahead-Of-Time) при установке приложения. Без профиля ART работает в JIT-режиме при первых запусках.

### 3.2 ПОЧЕМУ это нужно

```
┌──────────────────────────────────────────────────────────────┐
│         БЕЗ Baseline Profile vs С Baseline Profile           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  БЕЗ профиля (первый запуск):                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │ DEX bytecode → Interpreter → JIT compile         │       │
│  │ (медленно)     (медленно)    (фоновый поток)     │       │
│  │                                                   │       │
│  │ Первые 5-10 запусков: JIT собирает профиль       │       │
│  │ Затем: bg-dexopt компилирует AOT                 │       │
│  │                                                   │       │
│  │ Итог: 5-10 "холодных" стартов до оптимизации     │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  С Baseline Profile:                                         │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Install time: profile → AOT compile горячих      │       │
│  │ методов СРАЗУ                                    │       │
│  │                                                   │       │
│  │ Первый запуск: критические пути уже compiled     │       │
│  │ Startup: -30% до -50% быстрее                    │       │
│  │ Scroll: jank снижается на 40-60%                 │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Реальные цифры:                                            │
│  • Google Maps: -30% cold start                             │
│  • Now in Android: -40% TTID                                │
│  • Jetpack Compose: -25% initial composition                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3.3 КАК РАБОТАЕТ

```
┌──────────────────────────────────────────────────────────────┐
│           ЖИЗНЕННЫЙ ЦИКЛ BASELINE PROFILE                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  РАЗРАБОТКА (CI/CD):                                         │
│  ┌─────────────────────────┐                                │
│  │ Macrobenchmark тест     │                                │
│  │ запускает app на        │                                │
│  │ реальном устройстве     │                                │
│  │         │                │                                │
│  │         ▼                │                                │
│  │ Собирает .prof файл    │                                │
│  │ (горячие методы)        │                                │
│  └────────┬────────────────┘                                │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────┐                                │
│  │ Gradle plugin:          │                                │
│  │ generateBaselineProfile │                                │
│  │         │                │                                │
│  │         ▼                │                                │
│  │ baseline-prof.txt       │                                │
│  │ (текстовый, в src/main) │                                │
│  └────────┬────────────────┘                                │
│           │                                                  │
│           ▼                                                  │
│  BUILD:                                                      │
│  ┌─────────────────────────┐                                │
│  │ R8/D8 компилирует       │                                │
│  │ .txt → .dm (бинарный)  │                                │
│  │ Включается в APK/AAB   │                                │
│  └────────┬────────────────┘                                │
│           │                                                  │
│           ▼                                                  │
│  УСТАНОВКА (устройство):                                     │
│  ┌─────────────────────────┐                                │
│  │ PackageManager reads .dm │                                │
│  │ → dex2oat AOT compile   │                                │
│  │ → .odex / .art файлы   │                                │
│  │                          │                                │
│  │ Первый запуск: горячий  │                                │
│  │ код уже native!          │                                │
│  └─────────────────────────┘                                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 3.4 КАК ПРИМЕНЯТЬ

```kotlin
// build.gradle.kts (app module)
plugins {
    id("com.android.application")
    id("androidx.baselineprofile")
}

android {
    // ...
}

dependencies {
    // Macrobenchmark module для генерации профиля
    baselineProfile(project(":macrobenchmark"))
}

baselineProfile {
    // Автоматически генерировать при каждом release build
    automaticGenerationDuringBuild = true

    // Сохранять в src/main (для коммита в VCS)
    saveInSrc = true

    // Фильтрация: только наш пакет
    filter {
        include("com.example.myapp.**")
    }
}
```

```kotlin
// macrobenchmark/build.gradle.kts
plugins {
    id("com.android.test")
    id("androidx.baselineprofile")
}

android {
    namespace = "com.example.macrobenchmark"
    targetProjectPath = ":app"

    testOptions.managedDevices.devices {
        create<ManagedVirtualDevice>("pixel6Api34") {
            device = "Pixel 6"
            apiLevel = 34
            systemImageSource = "aosp-atd" // Automated Test Device image
        }
    }
}

baselineProfile {
    managedDevices += "pixel6Api34"
    useConnectedDevices = false
}
```

```kotlin
// macrobenchmark/src/main/java/.../BaselineProfileGenerator.kt
@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {

    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generateStartupProfile() {
        rule.collect(
            packageName = "com.example.myapp",
            // Запускаем стартовые сценарии
            // Каждый метод, вызванный во время этих действий,
            // попадёт в Baseline Profile
            profileBlock = {
                // Cold start
                startActivityAndWait()

                // Навигация по основным экранам
                device.findObject(By.text("Каталог")).click()
                device.waitForIdle()

                device.findObject(By.text("Профиль")).click()
                device.waitForIdle()

                // Скролл списка (для prefetch/RecyclerView)
                device.findObject(By.res("product_list"))
                    .fling(Direction.DOWN)
                device.waitForIdle()
            }
        )
    }
}
```

Результат — файл `app/src/main/baseline-prof.txt`:

```
# Формат: флаги + сигнатура метода/класса
# H = Hot, S = Startup, P = Post-startup
HSPLcom/example/myapp/MainActivity;->onCreate(Landroid/os/Bundle;)V
HSPLcom/example/myapp/data/ProductRepository;->getProducts()Lkotlinx/coroutines/flow/Flow;
HSPLcom/example/myapp/ui/ProductAdapter;->onCreateViewHolder(Landroid/view/ViewGroup;I)Lcom/example/myapp/ui/ProductViewHolder;
PLcom/example/myapp/ui/ProfileFragment;->onViewCreated(Landroid/view/View;Landroid/os/Bundle;)V
```

### 3.5 Startup Profile (Android 13+)

```
┌──────────────────────────────────────────────────────────────┐
│         STARTUP PROFILE vs BASELINE PROFILE                  │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Baseline Profile:                                           │
│  - ВСЕ горячие методы (startup + scrolling + navigation)    │
│  - Компилируется AOT при установке                          │
│  - Размер .dex компилируемого кода: ~15-30%                 │
│                                                              │
│  Startup Profile (подмножество Baseline):                    │
│  - ТОЛЬКО стартовые классы                                   │
│  - Влияет на DEX layout: стартовые классы в начале .dex     │
│  - Меньше page faults при загрузке                          │
│  - Дополнительно к Baseline: ещё ~5-10% ускорение           │
│                                                              │
│  Startup Profile влияет на R8 DEX layout:                    │
│  ┌─────────────────────────────────┐                        │
│  │ classes.dex                      │                        │
│  │ ┌───────────────────────────┐   │                        │
│  │ │ STARTUP CLASSES (начало)  │   │ ← загружаются первыми  │
│  │ │ MainActivity              │   │    минимум page faults  │
│  │ │ Application               │   │                        │
│  │ │ MainViewModel             │   │                        │
│  │ ├───────────────────────────┤   │                        │
│  │ │ POST-STARTUP CLASSES      │   │ ← загружаются позже    │
│  │ │ ProfileFragment           │   │                        │
│  │ │ SettingsActivity          │   │                        │
│  │ └───────────────────────────┘   │                        │
│  └─────────────────────────────────┘                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

```kotlin
// Startup Profile генерируется автоматически, если:
// 1. Используется Baseline Profile Gradle plugin ≥ 1.3.0
// 2. R8 включён (release build)
// 3. В baseline-prof.txt есть флаги S (Startup)
//
// Файл: startup-prof.txt (генерируется автоматически)
```

### 3.6 ПОДВОДНЫЕ КАМНИ Baseline Profiles

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠ ОШИБКА: Baseline Profile НЕ работает в debug            │
│                                                             │
│  Baseline Profile компилируется ТОЛЬКО для release build.   │
│  Debug build использует JIT/interpreter.                    │
│  Для тестирования используйте:                              │
│  - ./gradlew :app:installRelease                            │
│  - или benchmark variant                                    │
│                                                             │
│  Проверка что профиль применён:                             │
│  adb shell dumpsys package com.example.myapp | grep -i dex  │
│  → status=speed-profile (профиль применён)                  │
│  → status=verify (профиль НЕ применён)                      │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  ⚠ ОШИБКА: Слишком большой профиль                          │
│                                                             │
│  Если покрыть 100% кода — AOT compile всего → огромный      │
│  .odex файл, долгая установка.                              │
│                                                             │
│  Оптимально: 10-30% горячих методов                         │
│  - Стартовый путь                                           │
│  - Основные пользовательские сценарии                       │
│  - Горячие циклы (RecyclerView bind)                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Macrobenchmark — измерение производительности

### 4.1 ЧТО это

Macrobenchmark — Jetpack библиотека для измерения пользовательских сценариев на реальном устройстве. В отличие от Microbenchmark (функции), Macrobenchmark измеряет полные user flows.

### 4.2 КАК РАБОТАЕТ

```
┌──────────────────────────────────────────────────────────────┐
│           MACROBENCHMARK ARCHITECTURE                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ТЕСТОВЫЙ ПРОЦЕСС              ЦЕЛЕВОЙ ПРОЦЕСС              │
│  (macrobenchmark module)       (app)                         │
│  ┌────────────────────┐       ┌────────────────────┐        │
│  │ @Test benchmark     │       │                    │        │
│  │                     │ IPC   │   Your App         │        │
│  │ MacrobenchmarkRule ─┼──────→│   (release build)  │        │
│  │ - запускает app     │       │                    │        │
│  │ - UI Automator      │       │                    │        │
│  │ - собирает traces   │       │                    │        │
│  └────────┬───────────┘       └────────────────────┘        │
│           │                                                  │
│           ▼                                                  │
│  Perfetto/atrace                                             │
│  - Frame timing                                              │
│  - CPU scheduling                                            │
│  - Method tracing                                            │
│           │                                                  │
│           ▼                                                  │
│  РЕЗУЛЬТАТЫ:                                                 │
│  timeToInitialDisplayMs: 450.3 (min), 512.7 (median)        │
│  timeToFullDisplayMs:    892.1 (min), 1023.4 (median)       │
│  frameDurationCpuMs:     8.2 (p50), 16.1 (p90), 22.3 (p99) │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4.3 КАК ПРИМЕНЯТЬ

```kotlin
// macrobenchmark/src/main/java/.../StartupBenchmark.kt
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {

    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startupCold() = benchmarkRule.measureRepeated(
        packageName = "com.example.myapp",
        metrics = listOf(
            StartupTimingMetric(),      // TTID + TTFD
            TraceSectionMetric("MyCustomTrace"), // кастомные метрики
        ),
        iterations = 10,               // повторов для статистики
        startupMode = StartupMode.COLD, // тип старта
        compilationMode = CompilationMode.DEFAULT, // реальные условия
    ) {
        // Setup — до каждой итерации
        pressHome()
        // Сброс — убить процесс для cold start
        // (MacrobenchmarkRule делает это автоматически)

        // Action — что измеряем
        startActivityAndWait()

        // Wait for full content
        device.wait(
            Until.hasObject(By.res("content_loaded")),
            5_000
        )
    }

    @Test
    fun startupWarm() = benchmarkRule.measureRepeated(
        packageName = "com.example.myapp",
        metrics = listOf(StartupTimingMetric()),
        iterations = 10,
        startupMode = StartupMode.WARM,
        compilationMode = CompilationMode.Partial(
            baselineProfileMode = BaselineProfileMode.Require
        ),
    ) {
        pressHome()
        startActivityAndWait()
    }

    @Test
    fun scrollPerformance() = benchmarkRule.measureRepeated(
        packageName = "com.example.myapp",
        metrics = listOf(FrameTimingMetric()),
        iterations = 5,
        startupMode = StartupMode.COLD,
    ) {
        startActivityAndWait()

        val list = device.findObject(By.res("product_list"))
        // Fling для измерения frame timing
        list.setGestureMargin(device.displayWidth / 5)
        repeat(3) {
            list.fling(Direction.DOWN)
            device.waitForIdle()
        }
    }
}
```

```kotlin
// Кастомные trace sections для тонкого измерения
class MyRepository @Inject constructor(
    private val api: MyApi,
    private val dao: MyDao,
) {
    suspend fun loadInitialData(): List<Product> {
        // Кастомная секция — появится в Macrobenchmark
        return trace("MyRepo.loadInitialData") {
            val cached = trace("MyRepo.loadFromCache") {
                dao.getAllProducts()
            }
            if (cached.isNotEmpty()) return@trace cached

            trace("MyRepo.loadFromNetwork") {
                val response = api.getProducts()
                dao.insertAll(response)
                response
            }
        }
    }
}
```

### 4.4 CompilationMode — варианты

| Режим | Описание | Когда использовать |
|-------|----------|-------------------|
| `None()` | Без AOT, только JIT | Worst case сценарий |
| `Partial(warmup=3)` | JIT после N запусков | Типичный пользователь |
| `Partial(baselineProfileMode=Require)` | С Baseline Profile | Реальные условия |
| `Full()` | Полная AOT компиляция | Best case сценарий |
| `DEFAULT` | То же что `Partial()` | По умолчанию |

---

## 5. Perfetto — системный trace

### 5.1 ЧТО это

Perfetto — инструмент системного трейсинга, заменивший systrace. Показывает CPU scheduling, thread state, Binder transactions, frame rendering, custom trace events.

### 5.2 КАК ПРИМЕНЯТЬ

```kotlin
// Программные trace sections
import androidx.tracing.trace

// В коде приложения
class SplashViewModel : ViewModel() {
    fun initialize() {
        // Эти секции видны в Perfetto trace
        trace("SplashVM.initialize") {
            trace("SplashVM.loadConfig") {
                configRepository.load()
            }
            trace("SplashVM.initAnalytics") {
                analytics.init()
            }
            trace("SplashVM.prefetchData") {
                dataRepository.prefetch()
            }
        }
    }
}
```

```
Perfetto trace визуализация:
┌──────────────────────────────────────────────────────────────┐
│ main thread                                                   │
│ ┌───────────────────────────────────────────────────────────┐│
│ │ bindApplication                                          ││
│ │ ┌─────────────────────────────┐                          ││
│ │ │ installContentProviders     │                          ││
│ │ │ ┌──────┐┌──────┐┌────────┐ │                          ││
│ │ │ │ CP#1 ││ CP#2 ││ CP#3   │ │                          ││
│ │ │ └──────┘└──────┘└────────┘ │                          ││
│ │ └─────────────────────────────┘                          ││
│ │ ┌──────────────────────────┐                             ││
│ │ │ Application.onCreate()   │                             ││
│ │ └──────────────────────────┘                             ││
│ │ ┌──────────────────────────────────────┐                 ││
│ │ │ Activity.onCreate()                  │                 ││
│ │ │ ┌────────────────────────────────┐   │                 ││
│ │ │ │ setContentView() inflate       │   │                 ││
│ │ │ └────────────────────────────────┘   │                 ││
│ │ └──────────────────────────────────────┘                 ││
│ │ ┌──────────────────────────────────────┐                 ││
│ │ │ performTraversals (measure/layout/   │                 ││
│ │ │ draw) → FIRST FRAME                  │                 ││
│ │ └──────────────────────────────────────┘                 ││
│ └───────────────────────────────────────────────────────────┘│
│ 0ms        200ms        400ms        600ms        800ms      │
│                                                   TTID ─────↑│
└──────────────────────────────────────────────────────────────┘
```

### 5.3 Запуск Perfetto trace

```bash
# Через adb
adb shell perfetto \
  -c - --txt \
  -o /data/misc/perfetto-traces/trace.perfetto-trace \
  <<EOF
buffers: {
  size_kb: 63488
  fill_policy: RING_BUFFER
}
data_sources: {
  config {
    name: "linux.ftrace"
    ftrace_config {
      ftrace_events: "sched/sched_switch"
      ftrace_events: "power/suspend_resume"
      atrace_categories: "am"
      atrace_categories: "wm"
      atrace_categories: "view"
      atrace_categories: "dalvik"
      atrace_apps: "com.example.myapp"
    }
  }
}
duration_ms: 10000
EOF

# Скачать trace
adb pull /data/misc/perfetto-traces/trace.perfetto-trace

# Открыть: https://ui.perfetto.dev/
```

---

## 6. Оптимизация startup — практические техники

### 6.1 Чеклист оптимизации

```
┌──────────────────────────────────────────────────────────────┐
│          STARTUP OPTIMIZATION CHECKLIST                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  TIER 1 — Максимальный эффект:                              │
│  ☐ Baseline Profiles (–30-50% cold start)                   │
│  ☐ App Startup library (–50-200ms от CP overhead)           │
│  ☐ Ленивая инициализация SDK (analytics, ads)               │
│  ☐ Background thread для не-UI init                         │
│                                                              │
│  TIER 2 — Значимый эффект:                                  │
│  ☐ SplashScreen API (правильный starting window)            │
│  ☐ Уменьшить main activity layout complexity                │
│  ☐ Placeholder layouts + shimmer                            │
│  ☐ R8 full mode (оптимизация + tree shaking)                │
│                                                              │
│  TIER 3 — Тонкая настройка:                                 │
│  ☐ Профилировать Dagger/Hilt graph                          │
│  ☐ Избегать disk I/O на main thread (SharedPreferences!)    │
│  ☐ Startup Profile (DEX layout optimization)                │
│  ☐ Оптимизировать первый network request                    │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 6.2 Ленивая инициализация

```kotlin
class MyApplication : Application() {
    // ❌ ПЛОХО: всё в onCreate()
    override fun onCreate() {
        super.onCreate()
        // Каждая строка блокирует startup!
        Firebase.initialize(this)       // ~80ms
        Timber.plant(DebugTree())       // ~5ms
        ImageLoader.init(this)          // ~30ms
        Analytics.init(this)            // ~40ms
        CrashReporter.init(this)        // ~20ms
        // Итого: +175ms к startup
    }
}
```

```kotlin
class MyApplication : Application() {
    // ✅ ХОРОШО: критичное в onCreate, остальное лениво
    override fun onCreate() {
        super.onCreate()
        // Только критичное для первого кадра
        CrashReporter.init(this)  // нужен сразу для crash tracking

        // Остальное — после первого кадра
        val mainHandler = Handler(Looper.getMainLooper())
        mainHandler.post {
            // Выполнится после первого кадра (TTID уже засчитан)
            initializeNonCritical()
        }
    }

    private fun initializeNonCritical() {
        Firebase.initialize(this)
        Timber.plant(DebugTree())
        ImageLoader.init(this)
        Analytics.init(this)
    }
}
```

```kotlin
// Ещё лучше: с корутинами
class MyApplication : Application() {
    // ApplicationScope — живёт всё время приложения
    val applicationScope = CoroutineScope(
        SupervisorJob() + Dispatchers.Default
    )

    override fun onCreate() {
        super.onCreate()
        // Критичное — синхронно
        CrashReporter.init(this)

        // Параллельная инициализация в background
        applicationScope.launch {
            // Каждый в своей корутине — параллельно
            launch { Firebase.initialize(this@MyApplication) }
            launch { ImageLoader.init(this@MyApplication) }
            launch { Analytics.init(this@MyApplication) }
        }
    }
}
```

### 6.3 SplashScreen API

```kotlin
// Android 12+ SplashScreen API
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        // SplashScreen ПЕРЕД super.onCreate()
        val splashScreen = installSplashScreen()

        // Удерживаем splash пока данные не готовы
        var isReady = false
        splashScreen.setKeepOnScreenCondition { !isReady }

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Когда данные загружены — splash уходит
        viewModel.isDataReady.observe(this) { ready ->
            isReady = ready
        }

        // Анимация выхода splash
        splashScreen.setOnExitAnimationListener { splashScreenView ->
            val fadeOut = ObjectAnimator.ofFloat(
                splashScreenView.view,
                View.ALPHA,
                1f, 0f
            )
            fadeOut.duration = 300L
            fadeOut.doOnEnd { splashScreenView.remove() }
            fadeOut.start()
        }
    }
}
```

### 6.4 SharedPreferences на startup

```
┌─────────────────────────────────────────────────────────────┐
│  ⚠ SharedPreferences БЛОКИРУЕТ main thread                  │
│                                                             │
│  SharedPreferences.getXxx():                                │
│  - Первый вызов ЗАГРУЖАЕТ ВЕСЬ XML файл в память           │
│  - Парсинг XML на main thread                              │
│  - Блокирует до завершения загрузки (StrictMode violation)  │
│                                                             │
│  Если SharedPreferences файл большой (>50KB):              │
│  - Startup задержка: 50-200ms                              │
│                                                             │
│  РЕШЕНИЯ:                                                   │
│  1. DataStore (async, coroutines-based)                     │
│  2. Маленькие SP файлы для startup данных                   │
│  3. Preload SP в background thread                          │
└─────────────────────────────────────────────────────────────┘
```

```kotlin
// ❌ ПЛОХО: большой SharedPreferences на startup
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // Блокирует main thread пока весь файл не загружен
        val prefs = getSharedPreferences("app_prefs", MODE_PRIVATE)
        val theme = prefs.getString("theme", "light") // БЛОК!
        val userId = prefs.getString("user_id", null)  // уже в памяти
    }
}

// ✅ ХОРОШО: предзагрузка в background
class MyApplication : Application() {
    // Маленький файл ТОЛЬКО для startup данных
    val startupPrefs by lazy {
        getSharedPreferences("startup_prefs", MODE_PRIVATE)
    }

    override fun onCreate() {
        super.onCreate()
        // Или: DataStore (полностью async)
        // val themeFlow = dataStore.data.map { it.theme }
    }
}
```

---

## 7. Измерение в production — Android Vitals

### 7.1 ЧТО это

Android Vitals в Google Play Console показывает агрегированные метрики от реальных пользователей:

```
┌──────────────────────────────────────────────────────────────┐
│           ANDROID VITALS — STARTUP METRICS                   │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Cold Startup:                                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Время от нажатия иконки до первого кадра         │       │
│  │ Порог: > 5 секунд = "excessive"                  │       │
│  │ Таргет: < 500ms                                   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Warm Startup:                                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Activity restart без process restart              │       │
│  │ Порог: > 2 секунды = "excessive"                 │       │
│  │ Таргет: < 300ms                                   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Hot Startup:                                                │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Activity resume из background                     │       │
│  │ Порог: > 1.5 секунды = "excessive"               │       │
│  │ Таргет: < 100ms                                   │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  TTFD (Time To Full Display):                                │
│  ┌──────────────────────────────────────────────────┐       │
│  │ До reportFullyDrawn()                            │       │
│  │ Показывается в Play Console если вызван          │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 7.2 Кастомные метрики в production

```kotlin
// Отправка кастомных startup метрик в analytics
class StartupTracker {
    private var processStartTime: Long = 0L
    private var applicationCreateTime: Long = 0L
    private var activityCreateTime: Long = 0L
    private var firstFrameTime: Long = 0L

    fun onProcessStart() {
        processStartTime = SystemClock.elapsedRealtime()
    }

    fun onApplicationCreate() {
        applicationCreateTime = SystemClock.elapsedRealtime()
    }

    fun onActivityCreate() {
        activityCreateTime = SystemClock.elapsedRealtime()
    }

    fun onFirstFrame() {
        firstFrameTime = SystemClock.elapsedRealtime()

        // Отправляем метрики
        analytics.logStartupMetrics(
            processToApplication = applicationCreateTime - processStartTime,
            applicationToActivity = activityCreateTime - applicationCreateTime,
            activityToFirstFrame = firstFrameTime - activityCreateTime,
            totalStartup = firstFrameTime - processStartTime,
        )
    }
}
```

```kotlin
// Использование ProcessLifecycleOwner для определения типа старта
class StartupTypeDetector(application: Application) {
    var startType: StartType = StartType.COLD
        private set

    init {
        ProcessLifecycleOwner.get().lifecycle.addObserver(
            object : DefaultLifecycleObserver {
                var wasInBackground = true

                override fun onStart(owner: LifecycleOwner) {
                    startType = if (wasInBackground) {
                        StartType.COLD // или WARM — зависит от process
                    } else {
                        StartType.HOT
                    }
                }

                override fun onStop(owner: LifecycleOwner) {
                    wasInBackground = true
                }
            }
        )
    }
}

enum class StartType { COLD, WARM, HOT }
```

---

## 8. R8 и оптимизации сборки

### 8.1 R8 full mode

```kotlin
// build.gradle.kts
android {
    buildTypes {
        release {
            isMinifyEnabled = true      // R8 включён
            isShrinkResources = true    // Удаление неиспользуемых ресурсов

            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}

// gradle.properties
// R8 full mode — более агрессивные оптимизации
android.enableR8.fullMode=true
```

```
┌──────────────────────────────────────────────────────────────┐
│           R8 ВЛИЯНИЕ НА STARTUP                              │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  Tree Shaking:                                               │
│  • Удаляет неиспользуемые классы/методы                     │
│  • Меньше DEX → быстрее загрузка → быстрее startup          │
│  • Типичное уменьшение: 20-60% размера DEX                  │
│                                                              │
│  Code Optimization:                                          │
│  • Инлайнинг методов → меньше вызовов                       │
│  • Constant propagation                                      │
│  • Dead code elimination                                     │
│  • Enum unboxing (enum → int)                               │
│                                                              │
│  Obfuscation:                                                │
│  • Короткие имена → меньше string pool                      │
│  • Маргинальный эффект на startup                           │
│                                                              │
│  R8 Full Mode (дополнительно):                               │
│  • Более агрессивный tree shaking                            │
│  • Может сломать reflection-based код                       │
│  • Требует тщательных ProGuard rules                        │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 9. Compose startup considerations

### 9.1 Compose vs View startup

```
┌──────────────────────────────────────────────────────────────┐
│           COMPOSE vs VIEW SYSTEM — STARTUP                    │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  View System:                                                │
│  ┌─────────────────────────────────────────────────┐        │
│  │ setContentView() →                               │        │
│  │ LayoutInflater.inflate() →                       │        │
│  │ XML parsing → View creation → addView() →        │        │
│  │ requestLayout() → measure/layout/draw            │        │
│  │                                                   │        │
│  │ Стоимость: XML parsing + reflection (3-5ms/View) │        │
│  └─────────────────────────────────────────────────┘        │
│                                                              │
│  Compose:                                                    │
│  ┌─────────────────────────────────────────────────┐        │
│  │ setContent {} →                                   │        │
│  │ Composition →                                     │        │
│  │ Slot table allocation →                           │        │
│  │ Layout phase → Drawing phase                      │        │
│  │                                                   │        │
│  │ Стоимость: Kotlin function calls (no reflection)  │        │
│  │ НО: первая composition = инициализация Compose    │        │
│  │ runtime (50-100ms overhead)                       │        │
│  └─────────────────────────────────────────────────┘        │
│                                                              │
│  ВЫВОД: Compose startup может быть МЕДЛЕННЕЕ для первого     │
│  экрана из-за runtime init. Baseline Profile критичен!      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 9.2 Оптимизация Compose startup

```kotlin
// ❌ ПЛОХО: тяжёлая первая composition
@Composable
fun MainScreen(viewModel: MainViewModel = hiltViewModel()) {
    // Все данные загружаются синхронно
    val data by viewModel.heavyData.collectAsState(initial = emptyList())
    val config by viewModel.config.collectAsState(initial = null)

    // Сложный layout с условиями
    if (config != null) {
        ComplexLayout(data, config!!)
    }
}

// ✅ ХОРОШО: лёгкая первая composition + progressive loading
@Composable
fun MainScreen(viewModel: MainViewModel = hiltViewModel()) {
    val data by viewModel.data.collectAsState(initial = null)

    // Первый кадр — лёгкий placeholder (быстрый TTID)
    when (data) {
        null -> ShimmerPlaceholder() // Лёгкий, быстро рисуется
        else -> MainContent(data!!)
    }
}

@Composable
private fun ShimmerPlaceholder() {
    // Простой shimmer — минимальная composition
    Column(modifier = Modifier.fillMaxSize()) {
        repeat(5) {
            ShimmerBox(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(80.dp)
                    .padding(16.dp)
            )
        }
    }
}
```

---

## 10. Advanced: StrictMode для обнаружения проблем

```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            // StrictMode ловит проблемы на этапе разработки
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectDiskReads()       // Чтение с диска в main thread
                    .detectDiskWrites()      // Запись на диск в main thread
                    .detectNetwork()         // Сеть в main thread
                    .detectCustomSlowCalls() // trace("slow") > 500ms
                    .penaltyLog()            // Логируем
                    .penaltyFlashScreen()    // Мигаем экраном (визуально)
                    // .penaltyDeath()       // Крашим (строгий режим)
                    .build()
            )

            StrictMode.setVmPolicy(
                StrictMode.VmPolicy.Builder()
                    .detectLeakedClosableObjects()  // Незакрытые Closeable
                    .detectLeakedSqlLiteObjects()   // Незакрытые курсоры
                    .detectActivityLeaks()           // Activity leaks
                    .penaltyLog()
                    .build()
            )
        }
    }
}
```

---

## 11. Production Monitoring: метрики startup в production

### 11.1. Firebase Performance Monitoring

```kotlin
// АВТОМАТИЧЕСКОЕ ОТСЛЕЖИВАНИЕ STARTUP:
// Firebase Performance автоматически собирает:
// • _app_start trace (cold start)
// • _app_start_foreground_trace (foreground)

// КАСТОМНЫЕ TRACES для детализации:

class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Создаём кастомный trace для детализации startup
        val startupTrace = Firebase.performance.newTrace("custom_startup")
        startupTrace.start()

        // Фаза 1: DI инициализация
        val diTrace = Firebase.performance.newTrace("startup_di")
        diTrace.start()
        initDependencyInjection()
        diTrace.stop()

        // Фаза 2: Конфигурация
        val configTrace = Firebase.performance.newTrace("startup_config")
        configTrace.start()
        loadConfiguration()
        configTrace.stop()

        // Фаза 3: SDK инициализация
        val sdkTrace = Firebase.performance.newTrace("startup_sdks")
        sdkTrace.start()
        initThirdPartySdks()
        sdkTrace.stop()

        startupTrace.putAttribute("build_type", BuildConfig.BUILD_TYPE)
        startupTrace.putMetric("sdk_count", 5)
        startupTrace.stop()
    }
}

// ОТСЛЕЖИВАНИЕ TTFD:
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val ttfdTrace = Firebase.performance.newTrace("ttfd")
        ttfdTrace.start()

        setContent {
            MyApp(
                onFullyDrawn = {
                    ttfdTrace.stop()
                    reportFullyDrawn()  // Системный вызов
                }
            )
        }
    }
}

@Composable
fun MyApp(onFullyDrawn: () -> Unit) {
    val data by viewModel.data.collectAsState(initial = null)

    LaunchedEffect(data) {
        if (data != null) {
            onFullyDrawn()  // Данные загружены — fully drawn
        }
    }

    when (data) {
        null -> LoadingScreen()
        else -> MainContent(data!!)
    }
}
```

### 11.2. Crashlytics Custom Keys для анализа OOM

```kotlin
// ЛОГИРОВАНИЕ STARTUP КОНТЕКСТА:

class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        val startTime = SystemClock.elapsedRealtime()

        // Логируем контекст в Crashlytics
        Firebase.crashlytics.apply {
            setCustomKey("startup_type", determineStartupType())
            setCustomKey("process_start_time", android.os.Process.getStartElapsedRealtime())
            setCustomKey("total_memory_mb", Runtime.getRuntime().maxMemory() / 1024 / 1024)
        }

        // ... инициализация ...

        val startupDuration = SystemClock.elapsedRealtime() - startTime
        Firebase.crashlytics.setCustomKey("app_oncreate_duration_ms", startupDuration)
    }

    private fun determineStartupType(): String {
        // Определяем тип startup по времени от процесса
        val processAge = SystemClock.elapsedRealtime() -
            android.os.Process.getStartElapsedRealtime()

        return when {
            processAge < 100 -> "cold"  // Процесс только что создан
            processAge < 1000 -> "warm"  // Процесс недавно был создан
            else -> "hot"  // Процесс существовал долго
        }
    }
}

// В Activity:
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        val activityStartTime = SystemClock.elapsedRealtime()
        super.onCreate(savedInstanceState)

        Firebase.crashlytics.apply {
            setCustomKey("activity_create_start", activityStartTime)
            setCustomKey("saved_instance_state", savedInstanceState != null)
        }

        setContent {
            // ...
        }

        val onCreateDuration = SystemClock.elapsedRealtime() - activityStartTime
        Firebase.crashlytics.setCustomKey("activity_oncreate_duration_ms", onCreateDuration)
    }
}
```

### 11.3. Play Console Vitals

```
PLAY CONSOLE STARTUP METRICS:

┌─────────────────────────────────────────────────────────────────┐
│                    ANDROID VITALS: STARTUP TIME                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  МЕТРИКИ:                                                       │
│  • Cold start: время от tap до первого кадра                   │
│  • Warm start: время от tap до первого кадра (процесс жив)    │
│                                                                 │
│  THRESHOLDS (плохая startup):                                   │
│  • Cold start > 5 секунд = плохой показатель                   │
│  • Warm start > 2 секунды = плохой показатель                  │
│                                                                 │
│  ГДЕ СМОТРЕТЬ:                                                  │
│  Play Console → Android Vitals → Startup time                   │
│                                                                 │
│  SEGMENTATION:                                                  │
│  • По версии Android                                           │
│  • По типу устройства (phone/tablet)                           │
│  • По стране                                                    │
│  • По версии приложения                                        │
│                                                                 │
│  LIMITATIONS:                                                   │
│  • Только пользователи с Google Play Services                  │
│  • Только если пользователь согласился на сбор данных         │
│  • Примерно 28 дней данных                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

СРАВНЕНИЕ С PEERS:
┌─────────────────────────────────────────────────────────────────┐
│  Play Console показывает percentile вашего приложения          │
│  относительно похожих приложений в категории.                   │
│                                                                 │
│  Пример:                                                         │
│  "Your app's cold start time is in the 75th percentile"        │
│  = 75% похожих приложений запускаются быстрее                  │
│                                                                 │
│  ЦЕЛЬ: попасть в top 25% (bottom 25th percentile)              │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. Startup Tracing с Perfetto

### 12.1. Запись системного trace

```bash
# ЗАПИСЬ STARTUP TRACE:

# 1. Установить приложение
adb install app-release.apk

# 2. Остановить приложение (если запущено)
adb shell am force-stop com.example.app

# 3. Начать запись trace (до запуска!)
adb shell perfetto \
  -c - --txt \
  -o /data/misc/perfetto-traces/startup.perfetto-trace \
<<EOF
buffers: {
    size_kb: 131072
    fill_policy: DISCARD
}
buffers: {
    size_kb: 2048
    fill_policy: DISCARD
}
data_sources: {
    config {
        name: "linux.process_stats"
        target_buffer: 1
        process_stats_config {
            scan_all_processes_on_start: true
        }
    }
}
data_sources: {
    config {
        name: "android.log"
        android_log_config {
            log_ids: LID_DEFAULT
            log_ids: LID_SYSTEM
        }
    }
}
data_sources: {
    config {
        name: "linux.ftrace"
        ftrace_config {
            ftrace_events: "sched/sched_switch"
            ftrace_events: "power/suspend_resume"
            ftrace_events: "sched/sched_wakeup"
            ftrace_events: "sched/sched_wakeup_new"
            ftrace_events: "sched/sched_process_exit"
            ftrace_events: "sched/sched_process_free"
            ftrace_events: "task/task_newtask"
            ftrace_events: "task/task_rename"
            atrace_categories: "am"
            atrace_categories: "wm"
            atrace_categories: "view"
            atrace_categories: "gfx"
            atrace_categories: "dalvik"
            atrace_apps: "com.example.app"
        }
    }
}
duration_ms: 30000
EOF

# 4. Запустить приложение
adb shell am start -W -n com.example.app/.MainActivity

# 5. Подождать 30 секунд (или duration_ms)

# 6. Скачать trace
adb pull /data/misc/perfetto-traces/startup.perfetto-trace

# 7. Открыть в https://ui.perfetto.dev
```

### 12.2. Анализ Perfetto trace

```
PERFETTO UI: КЛЮЧЕВЫЕ СЕКЦИИ ДЛЯ STARTUP

┌─────────────────────────────────────────────────────────────────┐
│                      PERFETTO ANALYSIS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 1. НАЙТИ STARTUP TIMELINE:                                      │
│    • Process: com.example.app                                   │
│    • Thread: main                                               │
│    • Найти "bindApplication" → "activityStart" → "Choreographer"│
│                                                                 │
│ 2. КЛЮЧЕВЫЕ SLICE-Ы:                                            │
│    ┌────────────────────────────────────────────────────┐       │
│    │ bindApplication          │ Application создаётся   │       │
│    │ installContentProviders  │ CP инициализация        │       │
│    │ Application.onCreate()   │ Ваш код                 │       │
│    │ activityStart            │ Activity lifecycle      │       │
│    │ Choreographer#doFrame    │ Первый кадр (TTID)      │       │
│    └────────────────────────────────────────────────────┘       │
│                                                                 │
│ 3. ЧТО ИСКАТЬ:                                                  │
│    • Длинные slice-ы (> 100ms) = bottleneck                    │
│    • Gaps (пустые промежутки) = ожидание I/O или lock          │
│    • Concurrent activity на других threads                      │
│    • GC events ("Background concurrent copying GC")            │
│                                                                 │
│ 4. SQL QUERY В PERFETTO:                                        │
│    SELECT                                                        │
│      slice.name,                                                │
│      slice.dur / 1000000.0 as dur_ms                            │
│    FROM slice                                                    │
│    JOIN thread_track ON slice.track_id = thread_track.id       │
│    JOIN thread ON thread_track.utid = thread.utid               │
│    WHERE thread.name = 'main'                                   │
│      AND slice.dur > 10000000  -- > 10ms                       │
│    ORDER BY slice.dur DESC                                      │
│    LIMIT 20;                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 12.3. Custom Tracing в коде

```kotlin
// ДОБАВЛЕНИЕ СВОИХ TRACE SECTIONS:

import android.os.Trace

class MyApplication : Application() {

    override fun onCreate() {
        super.onCreate()

        // Обёртка для consistent tracing
        trace("MyApp.onCreate") {

            trace("MyApp.initDI") {
                initDependencyInjection()
            }

            trace("MyApp.initConfig") {
                loadConfiguration()
            }

            trace("MyApp.initSdks") {
                initThirdPartySdks()
            }
        }
    }
}

// Utility function для tracing:
inline fun <T> trace(label: String, block: () -> T): T {
    Trace.beginSection(label)
    try {
        return block()
    } finally {
        Trace.endSection()
    }
}

// Async tracing (для корутин):
suspend fun <T> traceAsync(label: String, block: suspend () -> T): T {
    val cookie = label.hashCode()
    Trace.beginAsyncSection(label, cookie)
    try {
        return block()
    } finally {
        Trace.endAsyncSection(label, cookie)
    }
}

// Compose tracing:
@Composable
fun TracedComposable(name: String, content: @Composable () -> Unit) {
    // Compose автоматически добавляет trace для recomposition
    // Но можно добавить кастомный:
    SideEffect {
        Trace.beginSection("Compose:$name")
    }
    content()
    SideEffect {
        Trace.endSection()
    }
}
```

---

## 13. Android 12+ SplashScreen API

### 13.1. Как работает SplashScreen

```
SPLASHSCREEN API (Android 12+):

┌─────────────────────────────────────────────────────────────────┐
│                 СИСТЕМНЫЙ SPLASH SCREEN                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ TIMELINE:                                                        │
│                                                                 │
│ [TAP] → [Системный Splash] → [Ваш контент]                     │
│           │                                                     │
│           │ • Показывается МГНОВЕННО (системой)                │
│           │ • Иконка из windowSplashScreenAnimatedIcon         │
│           │ • Цвет фона из windowSplashScreenBackground        │
│           │ • Показывается ПОКА Activity.onCreate() не завершён│
│           │                                                     │
│           └── setKeepOnScreenCondition { condition }            │
│               → Продлить показ до выполнения условия            │
│                                                                 │
│ АВТОМАТИЧЕСКИЙ ПЕРЕХОД:                                         │
│ После onCreate() система автоматически hide splash с анимацией │
│ → setOnExitAnimationListener {} для кастомной анимации         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 13.2. Конфигурация SplashScreen

```xml
<!-- res/values/themes.xml -->
<style name="Theme.App.Splash" parent="Theme.SplashScreen">
    <!-- Цвет фона splash -->
    <item name="windowSplashScreenBackground">@color/splash_background</item>

    <!-- Иконка (статичная или animated) -->
    <item name="windowSplashScreenAnimatedIcon">@drawable/ic_splash</item>

    <!-- Длительность анимации иконки (max 1000ms) -->
    <item name="windowSplashScreenAnimationDuration">500</item>

    <!-- Брендинг (опционально, внизу экрана) -->
    <item name="windowSplashScreenBrandingImage">@drawable/branding</item>

    <!-- Тема приложения для перехода -->
    <item name="postSplashScreenTheme">@style/Theme.App</item>
</style>
```

```kotlin
// Activity с SplashScreen API

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        // ВАЖНО: installSplashScreen() ПЕРЕД super.onCreate()!
        val splashScreen = installSplashScreen()

        super.onCreate(savedInstanceState)

        // Держим splash пока данные не загрузятся
        val viewModel: MainViewModel by viewModels()
        splashScreen.setKeepOnScreenCondition {
            viewModel.isLoading.value  // true = держать splash
        }

        // Кастомная анимация выхода
        splashScreen.setOnExitAnimationListener { splashScreenView ->
            // Анимация fade out
            val fadeOut = ObjectAnimator.ofFloat(
                splashScreenView.view,
                View.ALPHA,
                1f, 0f
            ).apply {
                duration = 300
                interpolator = AccelerateInterpolator()
                doOnEnd { splashScreenView.remove() }
            }
            fadeOut.start()
        }

        setContent {
            MyApp()
        }
    }
}
```

### 13.3. Animated Vector Drawable для Splash

```xml
<!-- res/drawable/ic_splash_animated.xml -->
<animated-vector
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:aapt="http://schemas.android.com/aapt">

    <aapt:attr name="android:drawable">
        <vector
            android:width="108dp"
            android:height="108dp"
            android:viewportWidth="108"
            android:viewportHeight="108">

            <group android:name="icon_group">
                <path
                    android:name="icon_path"
                    android:pathData="M54,54 L54,54"
                    android:strokeWidth="8"
                    android:strokeColor="#FFFFFF"
                    android:strokeLineCap="round"/>
            </group>
        </vector>
    </aapt:attr>

    <target android:name="icon_group">
        <aapt:attr name="android:animation">
            <set>
                <objectAnimator
                    android:propertyName="rotation"
                    android:valueFrom="0"
                    android:valueTo="360"
                    android:duration="1000"
                    android:repeatCount="infinite"/>
            </set>
        </aapt:attr>
    </target>
</animated-vector>
```

---

## 14. Startup Optimization Checklist

```
COMPREHENSIVE STARTUP CHECKLIST:

┌─────────────────────────────────────────────────────────────────┐
│                 PRE-LAUNCH CHECKLIST                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [ ] MEASUREMENT (измерение перед оптимизацией)                  │
│     [ ] Baseline Macrobenchmark тест настроен                   │
│     [ ] CI запускает benchmark на каждый PR                     │
│     [ ] Perfetto trace записан для cold start                   │
│     [ ] Firebase Performance настроен для production            │
│                                                                 │
│ [ ] APPLICATION CLASS                                           │
│     [ ] Минимальный код в onCreate()                           │
│     [ ] Тяжёлые SDK инициализируются lazy или async            │
│     [ ] App Startup library для ContentProvider-based SDKs     │
│     [ ] StrictMode включён в debug                              │
│                                                                 │
│ [ ] CONTENT PROVIDERS                                           │
│     [ ] Минимум собственных ContentProviders                    │
│     [ ] Проверен список CP от библиотек (merger manifest)      │
│     [ ] Firebase/WorkManager настроены через App Startup       │
│                                                                 │
│ [ ] DEPENDENCY INJECTION                                        │
│     [ ] Hilt с @Inject constructor (compile-time)              │
│     [ ] Нет reflection-based DI (Dagger 1, Guice)              │
│     [ ] Lazy injection для тяжёлых зависимостей                │
│                                                                 │
│ [ ] FIRST ACTIVITY                                              │
│     [ ] Layout оптимизирован (минимум nesting)                 │
│     [ ] Placeholder/skeleton для async данных                  │
│     [ ] reportFullyDrawn() вызывается после загрузки           │
│     [ ] Нет тяжёлых операций в onCreate/onStart                │
│                                                                 │
│ [ ] COMPOSE (если используется)                                 │
│     [ ] Baseline Profile включает startup Composables          │
│     [ ] Первая composition — минимальный UI                    │
│     [ ] derivedStateOf для тяжёлых вычислений                  │
│     [ ] collectAsStateWithLifecycle вместо collectAsState      │
│                                                                 │
│ [ ] BASELINE PROFILES                                           │
│     [ ] Baseline Profile сгенерирован                          │
│     [ ] Startup Profile сгенерирован                           │
│     [ ] Профили включены в release build                       │
│     [ ] Проверено применение: adb shell dumpsys package        │
│                                                                 │
│ [ ] R8/PROGUARD                                                 │
│     [ ] R8 full mode включён                                   │
│     [ ] Unused code removed                                     │
│     [ ] Keep rules минимальны                                  │
│                                                                 │
│ [ ] SPLASH SCREEN                                               │
│     [ ] SplashScreen API для Android 12+                       │
│     [ ] Compat library для Android < 12                        │
│     [ ] setKeepOnScreenCondition для async loading             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 15. Case Study: Оптимизация startup на 40%

```
РЕАЛЬНЫЙ КЕЙС: E-COMMERCE APP STARTUP OPTIMIZATION

ИСХОДНОЕ СОСТОЯНИЕ:
┌─────────────────────────────────────────────────────────────────┐
│ Cold start time (P50): 3200ms                                   │
│ Cold start time (P90): 4800ms                                   │
│                                                                 │
│ Breakdown (Perfetto analysis):                                  │
│ • ContentProviders: 450ms (7 CP от библиотек)                  │
│ • Application.onCreate: 1200ms                                 │
│   - Firebase init: 280ms                                       │
│   - Analytics SDKs: 350ms                                       │
│   - DI setup: 180ms                                             │
│   - Other: 390ms                                                 │
│ • MainActivity.onCreate: 800ms                                 │
│   - Layout inflation: 320ms                                     │
│   - Data loading: 480ms                                         │
│ • First frame: 750ms                                            │
└─────────────────────────────────────────────────────────────────┘

ПРИМЁННЫЕ ОПТИМИЗАЦИИ:

1. APP STARTUP LIBRARY
   ┌─────────────────────────────────────────────────────────────┐
   │ • Объединили 7 ContentProviders в 1 InitializationProvider │
   │ • Результат: 450ms → 180ms (-270ms)                        │
   └─────────────────────────────────────────────────────────────┘

2. LAZY SDK INITIALIZATION
   ┌─────────────────────────────────────────────────────────────┐
   │ • Firebase init: вынесли в background после first frame    │
   │ • Analytics: инициализация по требованию (lazy)            │
   │ • Результат: 630ms → 50ms (-580ms)                         │
   └─────────────────────────────────────────────────────────────┘

3. LAYOUT OPTIMIZATION
   ┌─────────────────────────────────────────────────────────────┐
   │ • ViewStub для below-the-fold content                       │
   │ • Placeholder вместо реальных данных                        │
   │ • Merge tags, ConstraintLayout вместо nested LinearLayout  │
   │ • Результат: 320ms → 120ms (-200ms)                        │
   └─────────────────────────────────────────────────────────────┘

4. ASYNC DATA LOADING
   ┌─────────────────────────────────────────────────────────────┐
   │ • Данные загружаются ПОСЛЕ first frame                     │
   │ • Skeleton UI показывается мгновенно                       │
   │ • reportFullyDrawn() после загрузки данных                 │
   │ • Результат: 480ms → 0ms для TTID (-480ms для first frame)│
   └─────────────────────────────────────────────────────────────┘

5. BASELINE PROFILES
   ┌─────────────────────────────────────────────────────────────┐
   │ • Сгенерирован Baseline Profile для startup path           │
   │ • Результат: дополнительно -15% на всех этапах            │
   └─────────────────────────────────────────────────────────────┘

ИТОГ:
┌─────────────────────────────────────────────────────────────────┐
│ Cold start time (P50): 3200ms → 1920ms (-40%)                  │
│ Cold start time (P90): 4800ms → 2760ms (-42%)                  │
│                                                                 │
│ TTID (время до первого кадра): 1850ms → 850ms (-54%)          │
│ TTFD (время до полной отрисовки): 3200ms → 2100ms (-34%)      │
│                                                                 │
│ Play Console Vitals: из 75th percentile в 15th percentile     │
│ (стали быстрее 85% похожих приложений)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Startup — это onCreate()" | Startup начинается с Zygote fork, ContentProviders вызываются ДО onCreate() |
| "Baseline Profile — это ProGuard" | Baseline Profile = AOT-компиляция горячих методов, ProGuard = обфускация + shrinking |
| "Debug build показывает реальную скорость" | Debug build в 2-5 раз медленнее: нет R8, нет Baseline Profile, interpreter mode |
| "Splash screen ускоряет запуск" | Splash screen СКРЫВАЕТ время загрузки, не ускоряет |
| "Больше потоков = быстрее init" | Main thread всё равно ждёт критичные init; потоки помогают только для некритичного |
| "SharedPreferences быстрый" | Первое чтение SP ЗАГРУЖАЕТ и ПАРСИТ весь XML файл на main thread |
| "App Startup library = быстрый старт" | App Startup убирает overhead множества CP, но всё ещё блокирует main thread |
| "Compose быстрее XML на startup" | Первая composition включает runtime init (~50-100ms overhead); Baseline Profile критичен |
| "Multidex замедляет только первый запуск" | Multidex загрузка происходит при КАЖДОМ cold start; minSdk 21+ решает это |
| "SplashScreen ускоряет startup" | SplashScreen СКРЫВАЕТ время загрузки, не ускоряет. Но улучшает perceived performance |
| "Нужно оптимизировать всё сразу" | Правило 80/20: найдите bottleneck через профилирование, оптимизируйте его |
| "Кэширование всегда помогает" | Чтение с диска тоже занимает время; SharedPreferences блокирует main thread |
| "Kotlin медленнее Java на startup" | Kotlin компилируется в тот же bytecode; разница только в runtime библиотеках |

### Детальный разбор мифов

```
МИФ: "Debug build показывает реальную скорость"

РЕАЛЬНОСТЬ:
┌─────────────────────────────────────────────────────────────────┐
│ DEBUG BUILD:                                                    │
│ • JIT compilation (интерпретация + JIT)                        │
│ • Нет R8 оптимизаций (unused code остаётся)                   │
│ • Нет Baseline Profile (всё JIT)                               │
│ • Debug symbols добавляют overhead                             │
│ • StrictMode может замедлять                                   │
│                                                                 │
│ Результат: Debug в 2-5x МЕДЛЕННЕЕ release!                     │
│                                                                 │
│ RELEASE BUILD:                                                  │
│ • AOT compilation для Baseline Profile методов                 │
│ • R8 убирает unused code                                       │
│ • ProGuard оптимизации                                         │
│ • Нет debug overhead                                           │
│                                                                 │
│ ПРАВИЛО:                                                        │
│ Всегда измеряйте startup на RELEASE build!                     │
│ Используйте Macrobenchmark с release variant.                  │
└─────────────────────────────────────────────────────────────────┘

МИФ: "ContentProvider только для данных"

РЕАЛЬНОСТЬ:
┌─────────────────────────────────────────────────────────────────┐
│ ContentProvider используется для:                               │
│                                                                 │
│ 1. Доступ к данным (традиционное использование)                │
│    • ContactsProvider, MediaProvider                           │
│    • Room с ContentProvider                                     │
│                                                                 │
│ 2. АВТОМАТИЧЕСКАЯ ИНИЦИАЛИЗАЦИЯ БИБЛИОТЕК                      │
│    • Firebase                                                   │
│    • WorkManager                                                │
│    • LeakCanary                                                 │
│    • Facebook SDK                                              │
│    • И многие другие...                                        │
│                                                                 │
│ ПРОБЛЕМА:                                                       │
│ Каждый ContentProvider.onCreate() вызывается ДО                │
│ Application.onCreate() и БЛОКИРУЕТ main thread!                │
│                                                                 │
│ Проверьте merged manifest:                                      │
│ Build → Analyze APK → AndroidManifest.xml                      │
│ Посчитайте <provider> элементы                                 │
│                                                                 │
│ РЕШЕНИЕ:                                                        │
│ App Startup library объединяет все CP в один                   │
└─────────────────────────────────────────────────────────────────┘

МИФ: "SharedPreferences быстрый"

РЕАЛЬНОСТЬ:
┌─────────────────────────────────────────────────────────────────┐
│ ПЕРВОЕ ЧТЕНИЕ SharedPreferences:                                │
│                                                                 │
│ 1. Открыть XML файл                                            │
│ 2. Распарсить весь XML (даже если нужен 1 ключ)               │
│ 3. Загрузить в HashMap в памяти                                │
│ 4. Вернуть значение                                            │
│                                                                 │
│ Всё это происходит СИНХРОННО на main thread!                   │
│                                                                 │
│ Для файла 100KB: ~50-100ms на mid-range device                │
│                                                                 │
│ ПОСЛЕДУЮЩИЕ ЧТЕНИЯ:                                             │
│ Из памяти (HashMap) — мгновенно                                 │
│                                                                 │
│ АЛЬТЕРНАТИВЫ:                                                   │
│ • DataStore Proto — binary format, coroutines                  │
│ • DataStore Preferences — async API                            │
│ • MMKV (Tencent) — memory-mapped, очень быстрый               │
│                                                                 │
│ ЕСЛИ НУЖЕН SP:                                                  │
│ • Разделите на маленькие файлы по категориям                  │
│ • Читайте в background до первого обращения                   │
│ • apply() вместо commit() для записи                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## CS-фундамент

| Концепция | Применение в App Startup |
|-----------|-------------------------|
| **Copy-on-Write (COW)** | Zygote fork: pages копируются только при записи — быстрый fork |
| **AOT vs JIT compilation** | Baseline Profile = AOT для горячих методов; остальное = JIT at runtime |
| **Profile-Guided Optimization** | Baseline Profile = PGO: реальный профиль → оптимизация компиляции |
| **Memory-mapped files** | DEX файлы mmap-ятся в память; Startup Profile оптимизирует page layout |
| **Page faults** | Startup Profile группирует стартовые классы → меньше page faults при загрузке |
| **Topological sort** | App Startup library: dependency graph → topological sort → правильный порядок init |
| **Lazy evaluation** | Ленивая инициализация: вычисление откладывается до первого обращения |
| **Pipeline architecture** | Startup = pipeline этапов; оптимизация = устранение bottleneck в каждом этапе |

---

## Проверь себя

### Вопрос 1: Порядок инициализации
**Q:** В каком порядке вызываются при cold start: Activity.onCreate(), ContentProvider.onCreate(), Application.onCreate()?

**A:** ContentProvider.onCreate() → Application.onCreate() → Activity.onCreate(). ContentProviders инициализируются ПЕРВЫМИ в installContentProviders(), затем вызывается Application.onCreate() в bindApplication(), и только потом запускается Activity lifecycle.

---

### Вопрос 2: Baseline Profile
**Q:** Почему Baseline Profile нельзя протестировать в debug build? Как проверить что профиль применён?

**A:** Baseline Profile компилируется в бинарный .dm файл только при release build. Debug build использует JIT/interpreter без AOT-компиляции. Проверка: `adb shell dumpsys package <pkg> | grep dex` → status=speed-profile означает что профиль применён, status=verify — не применён.

---

### Вопрос 3: Warm vs Hot start
**Q:** Приложение в background, пользователь переключается обратно. Когда это будет warm start, а когда hot?

**A:** Hot start: Activity всё ещё в памяти, вызывается только onRestart() → onStart() → onResume(). Warm start: система уничтожила Activity (LMK или конфигурация), но процесс жив — Activity пересоздаётся с savedInstanceState. Ключевое отличие: hot = Activity жива, warm = Activity уничтожена, процесс жив.

---

### Вопрос 4: App Startup Library
**Q:** Как App Startup library ускоряет старт, если Initializer-ы всё равно выполняются на main thread?

**A:** App Startup устраняет overhead создания множества ContentProvider объектов (каждый CP = отдельный объект с lifecycle). Вместо N ContentProvider-ов создаётся один InitializationProvider. Сама инициализация остаётся синхронной, но убирается "налог" на создание CP (15-30ms на каждый). Также App Startup решает проблему порядка: dependency graph гарантирует правильную последовательность.

---

### Вопрос 5: reportFullyDrawn()
**Q:** Что происходит если не вызывать reportFullyDrawn()? Будет ли TTFD всё равно измерен?

**A:** Без reportFullyDrawn() система НЕ может определить TTFD. В Play Console будет показан только TTID (время первого кадра). TTFD не будет собираться. Начиная с Jetpack Activity 1.7.0, reportFullyDrawn() корректно работает с Compose и автоматически ждёт pending compositions.

---

### Вопрос 6: Baseline Profile генерация
**Q:** Как генерируется Baseline Profile? Какие есть способы?

**A:** Три способа генерации:

1. **Macrobenchmark** (рекомендуется): Пишете BaselineProfileGenerator тест, который симулирует critical user journeys. Macrobenchmark записывает вызываемые методы и генерирует .txt профиль.

2. **Вручную**: Пишете baseline-prof.txt файл с правилами вида `HSPLcom/example/MyClass;->method()V`. H=hot, S=startup, P=post-startup, L=last.

3. **AGP 8.0+ автоматическая генерация**: При `generateBaselineProfile` Gradle task AGP может автоматически собрать профиль из instrumentation тестов.

Профиль компилируется в .dm файл и включается в APK/AAB.

---

### Вопрос 7: Startup vs Baseline Profile
**Q:** В чём разница между Startup Profile и Baseline Profile?

**A:**
- **Baseline Profile**: Определяет методы для AOT-компиляции. Ускоряет выполнение кода.
- **Startup Profile**: Определяет классы для оптимизации расположения в DEX файлах. Уменьшает page faults при загрузке.

Оба работают вместе. Baseline Profile улучшает execution time, Startup Profile улучшает class loading time. В AGP 8.0+ оба генерируются из одного Macrobenchmark теста.

---

### Вопрос 8: Cold start debugging
**Q:** Как определить что замедляет cold start? Опишите workflow диагностики.

**A:** Workflow:
1. **Запись trace**: `adb shell am start -W -S --start-profiler` или Perfetto
2. **Открыть в Perfetto UI**: ui.perfetto.dev
3. **Найти процесс**: Искать com.example.app, thread "main"
4. **Ключевые slice-ы**:
   - `bindApplication` — общее время init процесса
   - `installContentProviders` — CP overhead
   - `Application.onCreate` — ваш код
   - `activityStart` → `Choreographer#doFrame` — до первого кадра
5. **Найти bottleneck**: Slice > 100ms = проблема
6. **SQL query** в Perfetto для top-N медленных slice-ов
7. **Добавить кастомные Trace.beginSection()** для детализации

---

### Вопрос 9: Lazy initialization
**Q:** Когда lazy initialization помогает startup, а когда вредит?

**A:**
**Помогает когда:**
- Компонент не нужен на первом экране
- Компонент тяжёлый (SDK, база данных)
- Компонент используется условно (не всеми пользователями)

**Вредит когда:**
- Lazy initialization происходит на critical path (первый scroll, первый tap)
- Создаёт "jank" при первом использовании
- Усложняет debug (проблемы проявляются позже)

**Правило:** Lazy хорош для startup, но нужен "прогрев" (prefetch) в idle time после first frame.

---

### Вопрос 10: Compose startup optimization
**Q:** Почему Compose может быть медленнее XML на первом экране? Как оптимизировать?

**A:**
**Причина медленного Compose startup:**
- Первая composition инициализирует Compose runtime
- Slot table allocation
- Compiler генерирует код для recomposition tracking

**Оптимизация:**
1. **Baseline Profile** — AOT-компиляция Compose internals
2. **Простой первый Composable** — минимум nested Composables
3. **Placeholder/Skeleton** — показать UI до загрузки данных
4. **derivedStateOf** — кэшировать вычисления
5. **remember с правильными keys** — избегать лишних recompositions
6. **Не загружать данные синхронно** — use Loading state

---

### Вопрос 11: Process.getStartElapsedRealtime()
**Q:** Как измерить время от запуска процесса до Application.onCreate()?

**A:**
```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        val processStartTime = Process.getStartElapsedRealtime()
        val currentTime = SystemClock.elapsedRealtime()
        val timeToApplicationCreate = currentTime - processStartTime

        Log.d("Startup", "Time to Application.onCreate: ${timeToApplicationCreate}ms")
        // Это время включает: fork, ContentProvider init
    }
}
```

Это время показывает overhead до вашего кода: Zygote fork, class loading, ContentProvider инициализация.

---

### Вопрос 12: WorkManager и App Startup
**Q:** Как оптимизировать WorkManager initialization?

**A:** WorkManager по умолчанию использует ContentProvider для auto-init. Это добавляет 15-30ms к startup.

**Оптимизация:**
1. Отключить auto-init в manifest:
```xml
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    tools:node="merge">
    <meta-data
        android:name="androidx.work.WorkManagerInitializer"
        tools:node="remove" />
</provider>
```

2. Инициализировать lazy через App Startup или вручную:
```kotlin
class WorkManagerInitializer : Initializer<WorkManager> {
    override fun create(context: Context): WorkManager {
        val configuration = Configuration.Builder()
            .setMinimumLoggingLevel(Log.INFO)
            .build()
        WorkManager.initialize(context, configuration)
        return WorkManager.getInstance(context)
    }

    override fun dependencies() = emptyList<Class<Initializer<*>>>()
}
```

---

## Связанные темы

### Фундамент
- `[[android-compilation-pipeline]]` — ART JIT/AOT и как Baseline Profile взаимодействует с dex2oat
- `[[android-process-memory]]` — Zygote, fork(), LMK и почему процесс может быть убит
- `[[android-handler-looper]]` — Main thread event loop, куда попадают все init callbacks

### Жизненный цикл
- `[[android-activity-lifecycle]]` — Activity onCreate/onStart/onResume в контексте startup
- `[[android-content-provider-internals]]` — Почему CP — скрытый bottleneck и как App Startup решает это

### Отрисовка
- `[[android-view-rendering-pipeline]]` — measure/layout/draw до первого кадра
- `[[android-compose-internals]]` — Compose runtime init и первая composition

### Инструменты
- `[[android-performance-profiling]]` — Perfetto, CPU profiler, memory profiler
- `[[android-testing]]` — Macrobenchmark тесты в CI/CD

---

## Источники

1. **[Android Developers — App Startup Time](https://developer.android.com/topic/performance/vitals/launch-time)** — docs — Официальное руководство по типам запуска и метрикам
2. **[Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles/overview)** — docs — Официальная документация Baseline Profiles
3. **[Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview)** — docs — Руководство по Macrobenchmark
4. **[App Startup library](https://developer.android.com/topic/libraries/app-startup)** — docs — Jetpack App Startup документация
5. **[Perfetto documentation](https://perfetto.dev/docs/)** — docs — Системный trace tool
6. **[Android Performance Patterns — YouTube](https://www.youtube.com/playlist?list=PLWz5rJ2EKKc9CBxr3BVjPTPoDPLdPIFCE)** — video — Серия видео от Google о производительности
7. **[Startup Profiles — Android Dev Summit](https://www.youtube.com/watch?v=yJm5On5Gp4c)** — video — DEX layout оптимизация через Startup Profiles
8. **[R8 full mode](https://r8.googlesource.com/r8)** — docs — Документация R8 и оптимизации
9. **[SplashScreen API](https://developer.android.com/develop/ui/views/launch/splash-screen)** — docs — Android 12+ SplashScreen
10. **[Now in Android — Baseline Profiles case study](https://github.com/android/nowinandroid)** — code — Пример Baseline Profile в реальном проекте
11. **[Improving App Startup — Android Developers Blog](https://android-developers.googleblog.com/2020/07/improving-app-startup-facebook-app.html)** — article — Case study оптимизации Facebook
12. **[Macrobenchmark documentation](https://developer.android.com/studio/profile/macrobenchmark)** — docs — Подробное руководство по бенчмаркам
13. **[App Startup Tracing](https://developer.android.com/topic/performance/tracing/app-startup)** — docs — Системный tracing для startup

---

## Глоссарий терминов

| Термин | Определение |
|--------|-------------|
| **Cold Start** | Запуск приложения когда процесс не существует. Включает fork от Zygote, инициализацию runtime, ContentProviders, Application, Activity |
| **Warm Start** | Запуск когда процесс жив, но Activity уничтожена. Пропускает fork и Application init |
| **Hot Start** | Возврат к Activity которая всё ещё в памяти. Только onRestart/onStart/onResume |
| **TTID** | Time To Initial Display — время до первого кадра. Измеряется системой автоматически |
| **TTFD** | Time To Fully Drawn — время до полной загрузки контента. Требует вызова reportFullyDrawn() |
| **Baseline Profile** | Набор правил для AOT-компиляции "горячих" методов при установке приложения |
| **Startup Profile** | Subset Baseline Profile для оптимизации порядка классов в DEX (уменьшает page faults) |
| **Zygote** | Системный процесс-шаблон, от которого fork-аются все Android приложения |
| **AOT** | Ahead-Of-Time compilation — компиляция до выполнения (при установке) |
| **JIT** | Just-In-Time compilation — компиляция во время выполнения (runtime) |
| **dex2oat** | Инструмент ART для компиляции DEX в native code. Использует Baseline Profile |
| **ContentProvider** | Android компонент. Инициализируется ДО Application.onCreate() |
| **App Startup** | Jetpack библиотека для оптимизации инициализации библиотек через единый ContentProvider |
| **Macrobenchmark** | Jetpack библиотека для измерения производительности на уровне приложения |
| **Perfetto** | Системный инструмент трассировки Android. Визуализация в ui.perfetto.dev |
| **reportFullyDrawn()** | Метод Activity для сигнализации системе о завершении загрузки контента |
| **SplashScreen** | API Android 12+ для системного splash экрана. Показывается мгновенно при tap |
| **StrictMode** | Debug-инструмент для обнаружения проблем (I/O на main thread, leaks) |

---

## Формулы и метрики

```
КЛЮЧЕВЫЕ ФОРМУЛЫ:

Cold Start Time =
    Zygote Fork (~5ms) +
    ContentProvider Init (N × 15-30ms) +
    Application.onCreate() +
    Activity Lifecycle (onCreate → onResume) +
    First Frame Rendering

TTID = время от Intent до первого Choreographer.doFrame()

TTFD = время от Intent до reportFullyDrawn()

Startup Improvement = (Old_TTID - New_TTID) / Old_TTID × 100%

Frame Budget = 1000ms / 60fps ≈ 16.67ms

Baseline Profile Coverage =
    AOT-compiled methods / Total startup methods × 100%
    (цель: > 80% для critical path)

ContentProvider Overhead =
    installContentProviders time / Total Application init × 100%
    (цель: < 20%)
```

---

## Checklist для Code Review

```
STARTUP PR REVIEW CHECKLIST:

[ ] Application.onCreate() — есть ли новый код?
    [ ] Это блокирующий вызов?
    [ ] Можно ли сделать lazy?
    [ ] Есть ли Trace section?

[ ] Новые зависимости
    [ ] Проверить merged manifest на новые ContentProviders
    [ ] Проверить размер APK impact

[ ] Первая Activity
    [ ] Layout nesting < 10 уровней
    [ ] Нет тяжёлых операций в onCreate
    [ ] Есть placeholder для async данных

[ ] Compose
    [ ] Нет синхронной загрузки данных в composition
    [ ] collectAsStateWithLifecycle вместо collectAsState

[ ] Тесты
    [ ] Macrobenchmark покрывает изменения
    [ ] Baseline Profile обновлён если нужно
```

---

---

## Quick Reference: ADB Commands

```bash
# Измерить cold start time
adb shell am start -W -S com.example.app/.MainActivity

# Измерить startup с profiling
adb shell am start -W -S --start-profiler /data/local/tmp/startup.trace \
    com.example.app/.MainActivity

# Проверить статус Baseline Profile
adb shell dumpsys package com.example.app | grep -A 5 "dexopt"

# Принудительная компиляция с профилем
adb shell cmd package compile -m speed-profile -f com.example.app

# Сбросить компиляцию (для тестирования)
adb shell cmd package compile --reset com.example.app

# Получить информацию о процессе
adb shell dumpsys activity processes | grep -A 20 "com.example.app"

# Записать Perfetto trace
adb shell perfetto -o /data/misc/perfetto-traces/trace.perfetto-trace -t 10s \
    sched freq idle am wm gfx view

# Скачать trace
adb pull /data/misc/perfetto-traces/trace.perfetto-trace

# Проверить ContentProviders в приложении
adb shell dumpsys package com.example.app | grep "Provider"
```

---

*Последнее обновление: 2026-01-29*
*Эталон стиля: [[android-handler-looper]] (Gold Standard)*