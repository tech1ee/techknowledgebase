---
title: "Gradle и Android Gradle Plugin: полное руководство"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [build-systems, task-graph, dependency-resolution, incremental-builds]
tags:
  - topic/android
  - topic/build-system
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-build-evolution]]"
  - "[[android-project-structure]]"
  - "[[android-compilation-pipeline]]"
  - "[[android-dependencies]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-project-structure]]"
---

# Gradle и Android Gradle Plugin: полное руководство

Gradle — это build-система, которая управляет сборкой Android-приложений. Android Gradle Plugin (AGP) — это плагин, который добавляет Android-специфичные задачи: компиляция ресурсов, DEX-компиляция, подпись APK. Понимание этих инструментов критично для эффективной разработки.

> **Prerequisites:**
> - [[android-build-evolution]] — история систем сборки Android
> - [[android-overview]] — базовое понимание Android
> - Базовое понимание командной строки и Kotlin

---

## Зачем это нужно

### Проблема: "Магия" сборки

Многие разработчики относятся к Gradle как к "чёрному ящику":

| Проблема | Последствия |
|----------|-------------|
| **Не понимаю, что делает Gradle** | Не могу оптимизировать билд, 5+ минут на каждую сборку |
| **Копирую build.gradle из StackOverflow** | Конфликты версий, непонятные ошибки |
| **Не знаю разницу implementation/api** | Всё пересобирается при любом изменении |
| **Не использую Configuration Cache** | Потеря 15-30% времени на каждом билде |

### Актуальность в 2024-2025

**AGP 8.x → 9.0 — значительные изменения:**
- **Kotlin DSL** — стандарт с Android Studio Giraffe (build.gradle.kts)
- **Version Catalogs** — libs.versions.toml для централизованного управления версиями
- **Convention Plugins** — замена buildSrc для shared build logic
- **AGP 9.0**: встроенная поддержка Kotlin (не нужен kotlin-android плагин!)
- **Configuration Cache**: Gradle 8.11 даёт +8-14% к скорости конфигурации
- **Declarative Gradle (EAP 2025)**: новый декларативный язык для build-файлов

**Рекомендованный стек 2025:**
- Gradle 8.11+, AGP 8.10+, Kotlin 2.1+, KSP вместо kapt

### Что даёт понимание Gradle

```
Без понимания:                    С пониманием:
┌─────────────────┐               ┌─────────────────┐
│ Build: 5 min    │               │ Build: 45 sec   │
│ Sync: fails     │               │ Sync: works     │
│ Errors: ???     │               │ Errors: fixed   │
│ CI/CD: unstable │               │ CI/CD: green    │
└─────────────────┘               └─────────────────┘
```

**Конкретные выгоды:**
- **Configuration Cache** — пропуск фазы конфигурации при повторных сборках
- **Parallel builds** — модули собираются параллельно
- **Build Cache** — переиспользование результатов между машинами
- **Incremental builds** — пересборка только изменённого кода

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Gradle** | Build-система с декларативным DSL |
| **AGP** | Android Gradle Plugin — плагин для сборки Android |
| **DSL** | Domain Specific Language — Groovy или Kotlin |
| **Task** | Единица работы в Gradle (compile, assemble, test) |
| **Plugin** | Расширение, добавляющее задачи и конфигурацию |
| **Build Type** | Тип сборки: debug, release |
| **Product Flavor** | Вариант продукта: free, paid, dev, prod |
| **Build Variant** | Комбинация Build Type + Flavor |
| **Configuration** | Набор зависимостей: implementation, api, testImplementation |

---

## Архитектура Gradle

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       АРХИТЕКТУРА GRADLE BUILD                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         GRADLE CORE                              │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────────┐ │   │
│  │  │ Task    │  │ Project │  │ Config  │  │ Dependency          │ │   │
│  │  │ Graph   │  │ Model   │  │ Cache   │  │ Resolution          │ │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    ANDROID GRADLE PLUGIN (AGP)                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │ AAPT2       │  │ D8/R8       │  │ Signing                 │  │   │
│  │  │ Resources   │  │ DEX         │  │ APK/AAB                 │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │   │
│  │  │ Build       │  │ Product     │  │ Variant                 │  │   │
│  │  │ Types       │  │ Flavors     │  │ API                     │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                         YOUR PROJECT                             │   │
│  │  build.gradle.kts  │  settings.gradle.kts  │  gradle.properties  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Gradle Lifecycle: три фазы

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       GRADLE BUILD LIFECYCLE                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ФАЗА 1: INITIALIZATION                                                 │
│  ─────────────────────                                                  │
│  • Читает settings.gradle.kts                                           │
│  • Определяет, какие проекты участвуют в сборке                        │
│  • Создаёт Project objects                                              │
│                                                                         │
│  settings.gradle.kts                                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ rootProject.name = "MyApp"                                       │   │
│  │ include(":app", ":core", ":feature:home")                        │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ФАЗА 2: CONFIGURATION                                                  │
│  ─────────────────────                                                  │
│  • Выполняет build.gradle.kts каждого проекта                          │
│  • Создаёт Task graph                                                   │
│  • Разрешает зависимости (какие задачи от каких зависят)               │
│                                                                         │
│  build.gradle.kts                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ plugins { ... }         // ← Выполняется                        │   │
│  │ android { ... }         // ← Выполняется                        │   │
│  │ dependencies { ... }    // ← Выполняется                        │   │
│  │                                                                  │   │
│  │ tasks.register("myTask") {                                       │   │
│  │     // Этот блок выполняется при CONFIGURATION                   │   │
│  │     doLast {                                                     │   │
│  │         // Этот блок выполняется при EXECUTION                   │   │
│  │     }                                                            │   │
│  │ }                                                                │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ФАЗА 3: EXECUTION                                                      │
│  ─────────────────                                                      │
│  • Выполняет только запрошенные задачи                                 │
│  • Следует порядку зависимостей                                        │
│  • Использует кэширование                                               │
│                                                                         │
│  $ ./gradlew assembleDebug                                              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ preBuild → generateDebugSources → compileDebugKotlin →          │   │
│  │ → mergeDebugResources → processDebugResources →                 │   │
│  │ → dexBuilderDebug → mergeDebugDex → packageDebug →              │   │
│  │ → assembleDebug                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Anti-pattern: работа в Configuration phase

```kotlin
// ❌ ПЛОХО: Тяжёлая работа в Configuration phase
android {
    defaultConfig {
        // Это выполняется при КАЖДОЙ сборке, даже ./gradlew tasks
        val gitHash = Runtime.getRuntime()
            .exec("git rev-parse --short HEAD")
            .inputStream.bufferedReader().readText().trim()

        buildConfigField("String", "GIT_HASH", "\"$gitHash\"")
    }
}

// ✅ ХОРОШО: Ленивое вычисление
android {
    defaultConfig {
        buildConfigField("String", "GIT_HASH", "\"${getGitHash()}\"")
    }
}

// Функция вызывается только когда реально нужна
fun getGitHash(): String = providers.exec {
    commandLine("git", "rev-parse", "--short", "HEAD")
}.standardOutput.asText.get().trim()
```

---

## Файлы конфигурации

### settings.gradle.kts

```kotlin
// settings.gradle.kts — точка входа Gradle
pluginManagement {
    // Откуда брать плагины
    repositories {
        google()           // AGP, Firebase, etc.
        mavenCentral()     // Большинство библиотек
        gradlePluginPortal() // Gradle-специфичные плагины
    }

    // Версии плагинов по умолчанию
    plugins {
        id("com.android.application") version "8.7.0"
        id("org.jetbrains.kotlin.android") version "2.0.21"
    }
}

dependencyResolutionManagement {
    // Запретить добавление репозиториев в build.gradle модулей
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)

    repositories {
        google()
        mavenCentral()
        // Кастомный репозиторий
        maven { url = uri("https://jitpack.io") }
    }
}

// Название проекта (используется для корневой директории)
rootProject.name = "MyApp"

// Модули проекта
include(":app")
include(":core:data")
include(":core:domain")
include(":core:ui")
include(":feature:home")
include(":feature:profile")
include(":feature:settings")
```

### build.gradle.kts (project-level)

```kotlin
// build.gradle.kts (корневой) — общие настройки
plugins {
    // Объявление плагинов без применения
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.android.library) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
    alias(libs.plugins.hilt) apply false
    alias(libs.plugins.ksp) apply false
}

// Задачи для всего проекта
tasks.register("clean", Delete::class) {
    delete(rootProject.layout.buildDirectory)
}

// Общие настройки для всех подпроектов
subprojects {
    tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile>().configureEach {
        kotlinOptions {
            // Warnings как errors для всех модулей
            allWarningsAsErrors = true
        }
    }
}
```

### build.gradle.kts (module-level)

```kotlin
// app/build.gradle.kts — модуль приложения
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.myapp"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        // BuildConfig поля
        buildConfigField("String", "API_BASE_URL", "\"https://api.example.com\"")

        // Векторные drawables для старых API
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    signingConfigs {
        create("release") {
            storeFile = file("../keystore/release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = "myapp"
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }

    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-DEBUG"
        }
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
            signingConfig = signingConfigs.getByName("release")
        }
    }

    flavorDimensions += listOf("environment", "store")

    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            buildConfigField("String", "API_BASE_URL", "\"https://dev.api.example.com\"")
        }
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            buildConfigField("String", "API_BASE_URL", "\"https://staging.api.example.com\"")
        }
        create("prod") {
            dimension = "environment"
            buildConfigField("String", "API_BASE_URL", "\"https://api.example.com\"")
        }
        create("google") {
            dimension = "store"
            // Google Play specific config
        }
        create("huawei") {
            dimension = "store"
            // Huawei AppGallery specific config
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
        viewBinding = true  // Если используете View System
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
        // Java 8+ API desugaring
        isCoreLibraryDesugaringEnabled = true
    }

    kotlinOptions {
        jvmTarget = "17"
        freeCompilerArgs += listOf(
            "-opt-in=kotlinx.coroutines.ExperimentalCoroutinesApi",
            "-opt-in=androidx.compose.material3.ExperimentalMaterial3Api"
        )
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
            excludes += "META-INF/LICENSE.md"
        }
    }

    testOptions {
        unitTests {
            isIncludeAndroidResources = true
            isReturnDefaultValues = true
        }
    }
}

dependencies {
    // Desugaring для Java 8+ API
    coreLibraryDesugaring(libs.desugar.jdk.libs)

    // Modules
    implementation(project(":core:domain"))
    implementation(project(":core:data"))
    implementation(project(":core:ui"))
    implementation(project(":feature:home"))
    implementation(project(":feature:profile"))

    // AndroidX Core
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)

    // Compose
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.bundles.compose)
    debugImplementation(libs.androidx.ui.tooling)

    // Hilt
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)

    // Network
    implementation(libs.bundles.network)

    // Testing
    testImplementation(libs.junit)
    testImplementation(libs.mockk)
    testImplementation(libs.turbine)
    testImplementation(libs.kotlinx.coroutines.test)
    androidTestImplementation(libs.androidx.test.ext)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.ui.test.junit4)
}
```

### gradle.properties

```properties
# gradle.properties — глобальные настройки Gradle

# JVM настройки
org.gradle.jvmargs=-Xmx4096m -XX:+UseParallelGC -XX:MaxMetaspaceSize=1g

# Параллельная сборка модулей
org.gradle.parallel=true

# Configuration Cache (значительно ускоряет повторные сборки)
org.gradle.configuration-cache=true

# Build Cache (кэширование артефактов)
org.gradle.caching=true

# Gradle Daemon (переиспользование JVM)
org.gradle.daemon=true

# Kotlin Daemon (переиспользование компилятора)
kotlin.daemon.jvmargs=-Xmx2048m

# Android-специфичные
android.useAndroidX=true
android.nonTransitiveRClass=true
android.enableJetifier=false

# Kotlin
kotlin.code.style=official
kotlin.incremental=true

# Experimental features
android.experimental.enableScreenshotTest=true
```

---

## Build Types

Build Types определяют, КАК собирается приложение.

```kotlin
android {
    buildTypes {
        // Debug — для разработки
        debug {
            isDebuggable = true
            isMinifyEnabled = false
            isShrinkResources = false
            applicationIdSuffix = ".debug"
            versionNameSuffix = "-DEBUG"

            // Кастомные BuildConfig поля
            buildConfigField("Boolean", "ENABLE_LOGGING", "true")
            buildConfigField("Boolean", "ENABLE_CRASH_REPORTING", "false")

            // Кастомные ресурсы
            resValue("string", "app_name", "MyApp Debug")
        }

        // Release — для production
        release {
            isDebuggable = false
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )

            buildConfigField("Boolean", "ENABLE_LOGGING", "false")
            buildConfigField("Boolean", "ENABLE_CRASH_REPORTING", "true")

            resValue("string", "app_name", "MyApp")

            // Ndk stripping
            ndk {
                debugSymbolLevel = "FULL"
            }
        }

        // Staging — для тестирования
        create("staging") {
            initWith(getByName("release"))
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-STAGING"
            isDebuggable = true  // Для отладки на staging

            buildConfigField("Boolean", "ENABLE_LOGGING", "true")

            // Отдельная подпись для staging
            signingConfig = signingConfigs.getByName("debug")
        }

        // Benchmark — для performance тестов
        create("benchmark") {
            initWith(getByName("release"))
            signingConfig = signingConfigs.getByName("debug")
            matchingFallbacks += listOf("release")
            isDebuggable = false
            proguardFiles("benchmark-rules.pro")
        }
    }
}
```

---

## Product Flavors

Product Flavors определяют, ЧТО собирается — разные версии продукта.

```kotlin
android {
    // Измерения для flavors
    flavorDimensions += listOf("environment", "monetization")

    productFlavors {
        // Environment dimension
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            versionNameSuffix = "-dev"

            buildConfigField("String", "API_URL", "\"https://dev.api.example.com\"")
            buildConfigField("String", "ANALYTICS_KEY", "\"dev-key-123\"")

            // Манифест placeholders
            manifestPlaceholders["appIcon"] = "@mipmap/ic_launcher_dev"
            manifestPlaceholders["appIconRound"] = "@mipmap/ic_launcher_dev_round"
        }

        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            versionNameSuffix = "-staging"

            buildConfigField("String", "API_URL", "\"https://staging.api.example.com\"")
            buildConfigField("String", "ANALYTICS_KEY", "\"staging-key-456\"")

            manifestPlaceholders["appIcon"] = "@mipmap/ic_launcher_staging"
            manifestPlaceholders["appIconRound"] = "@mipmap/ic_launcher_staging_round"
        }

        create("prod") {
            dimension = "environment"
            // Без суффиксов для production

            buildConfigField("String", "API_URL", "\"https://api.example.com\"")
            buildConfigField("String", "ANALYTICS_KEY", "\"prod-key-789\"")

            manifestPlaceholders["appIcon"] = "@mipmap/ic_launcher"
            manifestPlaceholders["appIconRound"] = "@mipmap/ic_launcher_round"
        }

        // Monetization dimension
        create("free") {
            dimension = "monetization"
            applicationIdSuffix = ".free"

            buildConfigField("Boolean", "IS_PREMIUM", "false")
            buildConfigField("Boolean", "SHOW_ADS", "true")
        }

        create("premium") {
            dimension = "monetization"
            applicationIdSuffix = ".premium"

            buildConfigField("Boolean", "IS_PREMIUM", "true")
            buildConfigField("Boolean", "SHOW_ADS", "false")
        }
    }

    // Исключение некоторых комбинаций
    androidComponents {
        beforeVariants { variantBuilder ->
            // Не собирать devPremium — не имеет смысла
            if (variantBuilder.productFlavors.containsAll(
                listOf("environment" to "dev", "monetization" to "premium")
            )) {
                variantBuilder.enable = false
            }
        }
    }
}
```

**Результирующие варианты:**
```
devFreeDebug
devFreeRelease
stagingFreeDebug
stagingFreeRelease
stagingPremiumDebug
stagingPremiumRelease
prodFreeDebug
prodFreeRelease
prodPremiumDebug
prodPremiumRelease
```

### Source Sets для Flavors

```
app/
└── src/
    ├── main/                  # Общий код
    │   ├── kotlin/
    │   └── res/
    ├── debug/                 # Только для debug
    │   └── kotlin/
    ├── release/               # Только для release
    │   └── kotlin/
    ├── dev/                   # Только для dev flavor
    │   ├── kotlin/
    │   └── res/
    │       └── values/
    │           └── strings.xml  # Dev-специфичные строки
    ├── prod/                  # Только для prod flavor
    │   └── res/
    ├── free/                  # Только для free flavor
    │   └── kotlin/
    │       └── AdsManager.kt  # Реализация с рекламой
    ├── premium/               # Только для premium flavor
    │   └── kotlin/
    │       └── AdsManager.kt  # Пустая реализация
    └── devFreeDebug/          # Только для этой комбинации
        └── kotlin/
```

---

## Dependency Configurations

```kotlin
dependencies {
    // implementation — зависимость НЕ экспортируется
    // Потребители модуля не видят эту зависимость
    implementation(libs.retrofit)

    // api — зависимость экспортируется
    // Потребители модуля видят эту зависимость
    api(libs.gson)

    // compileOnly — только для компиляции
    // НЕ включается в APK
    compileOnly(libs.lombok)

    // runtimeOnly — только для runtime
    // НЕ доступна при компиляции
    runtimeOnly(libs.slf4j.android)

    // testImplementation — только для unit-тестов
    testImplementation(libs.junit)
    testImplementation(libs.mockk)

    // androidTestImplementation — только для instrumented тестов
    androidTestImplementation(libs.espresso.core)

    // debugImplementation — только для debug build type
    debugImplementation(libs.leakcanary)

    // releaseImplementation — только для release build type
    releaseImplementation(libs.firebase.crashlytics)

    // devImplementation — только для dev flavor
    "devImplementation"(libs.stetho)

    // Annotation processors (deprecated, используйте ksp)
    annotationProcessor(libs.room.compiler)

    // KSP (Kotlin Symbol Processing) — современная альтернатива kapt
    ksp(libs.room.compiler)
    ksp(libs.hilt.compiler)

    // Platform/BOM — управление версиями группы библиотек
    implementation(platform(libs.firebase.bom))
    implementation("com.google.firebase:firebase-analytics")  // Версия из BOM
    implementation("com.google.firebase:firebase-crashlytics") // Версия из BOM

    // Bundles — группа зависимостей из Version Catalog
    implementation(libs.bundles.compose)
    implementation(libs.bundles.network)
}
```

### implementation vs api

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    IMPLEMENTATION vs API                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  implementation (изолирует):                                            │
│                                                                         │
│  ┌───────┐    ┌─────────┐    ┌─────────┐                               │
│  │  App  │───▶│  LibA   │───▶│  Gson   │                               │
│  └───────┘    └─────────┘    └─────────┘                               │
│      │             │              │                                     │
│      │             └──────────────┘                                     │
│      │                  видит                                           │
│      └──────────────────────X                                           │
│                        НЕ видит                                         │
│                                                                         │
│  Преимущество: изменение в Gson → перекомпиляция только LibA           │
│                                                                         │
│  ─────────────────────────────────────────────────────────────────────  │
│                                                                         │
│  api (экспортирует):                                                    │
│                                                                         │
│  ┌───────┐    ┌─────────┐    ┌─────────┐                               │
│  │  App  │───▶│  LibA   │───▶│  Gson   │                               │
│  └───────┘    └─────────┘    └─────────┘                               │
│      │             │              │                                     │
│      │             └──────────────┘                                     │
│      │                  видит                                           │
│      └────────────────────────────┘                                     │
│                       видит                                             │
│                                                                         │
│  Недостаток: изменение в Gson → перекомпиляция LibA и App              │
│                                                                         │
│  Используйте api только если App реально использует типы из Gson       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Задачи (Tasks)

### Основные задачи AGP

```bash
# Компиляция и сборка
./gradlew assembleDebug          # Собрать debug APK
./gradlew assembleRelease        # Собрать release APK
./gradlew bundleRelease          # Собрать release AAB
./gradlew installDebug           # Собрать и установить debug

# Тестирование
./gradlew test                   # Unit тесты
./gradlew testDebugUnitTest      # Unit тесты для debug
./gradlew connectedAndroidTest   # Instrumented тесты на устройстве

# Анализ
./gradlew lint                   # Lint проверки
./gradlew lintDebug             # Lint для debug варианта
./gradlew dependencies          # Дерево зависимостей

# Очистка
./gradlew clean                 # Удалить build директории
./gradlew cleanBuildCache       # Очистить build cache

# Информация
./gradlew tasks                 # Список всех задач
./gradlew tasks --all           # Все задачи включая internal
./gradlew :app:dependencies     # Зависимости модуля app
./gradlew :app:dependencyInsight --dependency okhttp  # Детали о зависимости

# Build Scan (диагностика)
./gradlew assembleDebug --scan  # Сгенерировать build scan
```

### Кастомные задачи

```kotlin
// build.gradle.kts

// Простая задача
tasks.register("hello") {
    group = "custom"
    description = "Prints hello"

    doLast {
        println("Hello from custom task!")
    }
}

// Задача с типом Copy
tasks.register<Copy>("copyApk") {
    group = "distribution"
    description = "Copies APK to distribution folder"

    // Зависит от assembleRelease
    dependsOn("assembleRelease")

    from(layout.buildDirectory.dir("outputs/apk/release"))
    into(rootProject.layout.buildDirectory.dir("distribution"))

    include("*.apk")

    // Переименование
    rename { fileName ->
        val versionName = android.defaultConfig.versionName
        fileName.replace(".apk", "-v$versionName.apk")
    }
}

// Задача для генерации версии из Git
tasks.register("printVersionInfo") {
    group = "versioning"

    doLast {
        val gitHash = providers.exec {
            commandLine("git", "rev-parse", "--short", "HEAD")
        }.standardOutput.asText.get().trim()

        val gitBranch = providers.exec {
            commandLine("git", "rev-parse", "--abbrev-ref", "HEAD")
        }.standardOutput.asText.get().trim()

        println("Git hash: $gitHash")
        println("Git branch: $gitBranch")
    }
}

// Финализатор для задачи
tasks.named("assembleRelease") {
    finalizedBy("copyApk")
}
```

---

## Build Cache и Configuration Cache

### Build Cache

```kotlin
// settings.gradle.kts — включение remote build cache
buildCache {
    local {
        isEnabled = true
        directory = File(rootDir, ".gradle/build-cache")
        removeUnusedEntriesAfterDays = 7
    }

    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/cache/")
        isEnabled = true
        isPush = System.getenv("CI") == "true"  // Push только на CI

        credentials {
            username = System.getenv("CACHE_USER") ?: ""
            password = System.getenv("CACHE_PASSWORD") ?: ""
        }
    }
}
```

### Configuration Cache

```kotlin
// gradle.properties
org.gradle.configuration-cache=true

// Проблемы с Configuration Cache и как их решать:

// ❌ ПЛОХО: Чтение environment variable при configuration
android {
    defaultConfig {
        val apiKey = System.getenv("API_KEY")  // Ломает configuration cache
        buildConfigField("String", "API_KEY", "\"$apiKey\"")
    }
}

// ✅ ХОРОШО: Использование providers
android {
    defaultConfig {
        val apiKey = providers.environmentVariable("API_KEY").getOrElse("")
        buildConfigField("String", "API_KEY", "\"$apiKey\"")
    }
}

// ❌ ПЛОХО: Runtime.exec() при configuration
val gitHash = Runtime.getRuntime()
    .exec("git rev-parse --short HEAD")
    .inputStream.bufferedReader().readText()

// ✅ ХОРОШО: Providers API
val gitHash = providers.exec {
    commandLine("git", "rev-parse", "--short", "HEAD")
}.standardOutput.asText.map { it.trim() }
```

---

## Типичные ошибки и Anti-patterns

### 1. Версии зависимостей в нескольких местах

```kotlin
// ❌ ПЛОХО: Версии разбросаны по файлам
// app/build.gradle.kts
implementation("com.squareup.retrofit2:retrofit:2.9.0")

// feature/build.gradle.kts
implementation("com.squareup.retrofit2:retrofit:2.11.0")  // Конфликт!

// ✅ ХОРОШО: Version Catalog
// gradle/libs.versions.toml
[versions]
retrofit = "2.11.0"

[libraries]
retrofit = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }

// Везде одинаково
implementation(libs.retrofit)
```

### 2. Тяжёлые операции в configuration phase

```kotlin
// ❌ ПЛОХО: Сеть при configuration
android {
    defaultConfig {
        val latestVersion = URL("https://api.example.com/version").readText()
        versionName = latestVersion  // HTTP запрос при каждой сборке!
    }
}

// ✅ ХОРОШО: Версия в файле или переменной окружения
android {
    defaultConfig {
        versionName = providers.gradleProperty("VERSION_NAME").getOrElse("1.0.0")
    }
}
```

### 3. buildSrc без caching

```kotlin
// ❌ ПЛОХО: buildSrc меняется часто
// buildSrc/build.gradle.kts
// При любом изменении здесь — полная пересборка всего!

// ✅ ХОРОШО: Convention plugins в build-logic
// build-logic/convention/build.gradle.kts
// Используйте Composite Builds и Convention Plugins
```

### 4. Неправильное использование implementation/api

```kotlin
// ❌ ПЛОХО: Всё через api
// core/build.gradle.kts
api(libs.retrofit)  // Все модули видят Retrofit

// ✅ ХОРОШО: implementation + internal
// core/build.gradle.kts
implementation(libs.retrofit)  // Только core видит Retrofit
// Если нужны типы Retrofit в публичном API — используйте обёртки
```

### 5. Ignoring variant-specific dependencies

```kotlin
// ❌ ПЛОХО: LeakCanary в production
implementation(libs.leakcanary)  // Будет в release APK!

// ✅ ХОРОШО: Только для debug
debugImplementation(libs.leakcanary)
```

---

## Оптимизация времени сборки

```kotlin
// gradle.properties — максимальная оптимизация

# Память
org.gradle.jvmargs=-Xmx4096m -XX:+UseParallelGC -XX:MaxMetaspaceSize=1g

# Параллелизм
org.gradle.parallel=true
org.gradle.workers.max=8

# Caching
org.gradle.caching=true
org.gradle.configuration-cache=true

# Daemon
org.gradle.daemon=true
org.gradle.daemon.idletimeout=10800000

# Kotlin
kotlin.incremental=true
kotlin.daemon.jvmargs=-Xmx2048m
kotlin.caching.enabled=true

# Android
android.enableBuildConfigAsBytecode=true
android.nonTransitiveRClass=true
```

### Модульная архитектура

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    МОДУЛЬНАЯ АРХИТЕКТУРА                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Монолит:                              Модули:                          │
│  ─────────                             ────────                         │
│                                                                         │
│  ┌───────────────┐                     ┌─────────┐                      │
│  │     App       │                     │   App   │                      │
│  │               │                     └────┬────┘                      │
│  │  • UI         │                          │                           │
│  │  • Domain     │                     ┌────┴────┬─────────┐            │
│  │  • Data       │                     ▼         ▼         ▼            │
│  │  • Network    │               ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│  │  • Database   │               │ feature │ │ feature │ │ feature │   │
│  │               │               │  :home  │ │:profile │ │:settings│   │
│  └───────────────┘               └────┬────┘ └────┬────┘ └────┬────┘   │
│                                       │          │          │          │
│  Изменение UI →                       └──────────┴──────────┘          │
│  пересборка ВСЕГО                            │                          │
│                                              ▼                          │
│                                        ┌───────────┐                    │
│                                        │   :core   │                    │
│                                        │  domain   │                    │
│                                        └─────┬─────┘                    │
│                                              │                          │
│                                        ┌─────┴─────┐                    │
│                                        ▼           ▼                    │
│                                   ┌─────────┐ ┌─────────┐              │
│                                   │  :core  │ │  :core  │              │
│                                   │  data   │ │   ui    │              │
│                                   └─────────┘ └─────────┘              │
│                                                                         │
│  Изменение :feature:home → пересборка только :feature:home и :app     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

<details>
<summary>1. В чём разница между Build Types и Product Flavors?</summary>

**Ответ:**
- **Build Types** определяют КАК собирается приложение: debug/release, minification, signing
- **Product Flavors** определяют ЧТО собирается: разные версии продукта (free/paid, dev/prod)

Build Variants = Build Type × Product Flavors.
Например: devFreeDebug, prodPaidRelease.

</details>

<details>
<summary>2. Почему implementation лучше api для большинства зависимостей?</summary>

**Ответ:**
`implementation` изолирует зависимость — потребители модуля не видят её напрямую. Это означает:
1. Меньше перекомпиляции при изменении внутренних зависимостей
2. Чище API модуля
3. Меньше конфликтов версий

Используйте `api` только если типы зависимости являются частью публичного API модуля.

</details>

<details>
<summary>3. Что делает Configuration Cache?</summary>

**Ответ:**
Configuration Cache кэширует результат фазы конфигурации Gradle. При повторных сборках Gradle пропускает чтение и выполнение build.gradle.kts файлов, сразу используя закэшированный граф задач.

Требования: код конфигурации должен быть детерминированным (не читать файлы, не делать HTTP-запросы при конфигурации).

</details>

<details>
<summary>4. Как правильно управлять версиями зависимостей?</summary>

**Ответ:**
Используйте Version Catalogs (libs.versions.toml):
1. Все версии в одном файле
2. Type-safe доступ: `libs.retrofit` вместо строки
3. Bundles для группировки
4. IDE автодополнение

Для связанных библиотек используйте BOM (Bill of Materials): `platform(libs.compose.bom)`.

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Clean build нужен при каждой проблеме" | Clean build удаляет ВЕСЬ кэш, не только проблемный. 95% проблем решаются через `./gradlew --refresh-dependencies` или удаление .gradle/caches конкретного проекта. Clean — крайняя мера |
| "Gradle медленный по природе" | Gradle быстрый при правильной настройке. Configuration Cache, Build Cache, Parallel execution, Incremental compilation дают 5-10x ускорение. Медленность — обычно неправильная конфигурация |
| "buildSrc — лучший способ для shared логики" | buildSrc инвалидирует configuration cache при каждом изменении. Composite builds (includeBuild) и Convention Plugins в build-logic — современный подход |
| "api = implementation, просто публичнее" | api transitively expose зависимости потребителям модуля. Это увеличивает coupling, перекомпиляцию, потенциальные конфликты. api нужен ТОЛЬКО если типы зависимости в public API модуля |
| "kapt медленнее чем KSP в 2 раза" | Реальное ускорение от KSP: 1.5-2x, не 2x+. Выигрыш зависит от количества annotation processors и кода. Для мелких проектов разница минимальна |
| "Version Catalogs обязательны" | Version Catalogs — удобство, не требование. ext {} блоки, buildSrc константы всё ещё работают. Каталоги лучше для больших проектов с множеством модулей |
| "Kotlin DSL медленнее Groovy DSL" | С Gradle 8+ разница минимальна. Kotlin DSL даёт type-safety, IDE autocomplete, compile-time проверки. Начальный import дольше, но общая продуктивность выше |
| "Build Variants нужны всем" | Для простых приложений debug/release достаточно. Product Flavors добавляют сложность и время сборки. Используйте только если РЕАЛЬНО нужны разные версии продукта |
| "Convention Plugins сложные" | Базовый convention plugin = 20 строк кода. Копипаста в 10 модулях сложнее поддерживать чем один plugin. Начните с android-library convention, потом расширяйте |
| "Gradle Daemon ест память зря" | Daemon ускоряет повторные сборки в 2-3 раза за счёт warm JVM. org.gradle.jvmargs настраивает потребление. Без daemon каждая сборка cold start |

---

## CS-фундамент

| CS-концепция | Как применяется в Gradle |
|--------------|--------------------------|
| **DAG (Directed Acyclic Graph)** | Task graph Gradle — DAG. Задачи имеют зависимости (dependsOn). Gradle выполняет топологическую сортировку для определения порядка. Циклические зависимости → ошибка |
| **Incremental Computation** | Incremental builds: Gradle отслеживает inputs/outputs задач. Если inputs не изменились → skip task. UP-TO-DATE означает кэширование результата |
| **Caching (Multi-level)** | Build Cache (local/remote), Configuration Cache, Dependency Cache. Каждый уровень ускоряет разные фазы. Remote Cache позволяет шарить результаты между CI и разработчиками |
| **Lazy Evaluation** | Property<T>, Provider<T> — lazy containers. Значение вычисляется только когда нужно. Это критично для Configuration Cache и производительности |
| **Plugin Architecture** | Gradle extensible через plugins. Plugins регистрируют задачи, extensions, conventions. Composition over inheritance: несколько plugins комбинируются |
| **Dependency Resolution** | Conflict resolution через Gradle Module Metadata. Strategies: fail, newest, force. Platform (BOM) enforces consistent versions. Dynamic versions (1.+) vs strict |
| **Parallel Execution** | Gradle выполняет независимые задачи параллельно. Worker API для параллелизма внутри задачи. --parallel включает межпроектный параллелизм |
| **Configuration vs Execution** | Две фазы сборки. Configuration: чтение build.gradle, построение task graph. Execution: выполнение задач. Configuration Cache кэширует первую фазу |
| **Declarative vs Imperative** | Gradle DSL декларативный (dependencies {}), но позволяет императивный код (tasks.register {}). Convention plugins инкапсулируют императивную логику |
| **Isolation / Sandboxing** | Gradle изолирует проекты друг от друга. Cross-project configuration deprecated. Isolated Projects feature (Gradle 9) усиливает изоляцию |

---

## Связь с другими темами

**[[android-overview]]** — Обзор Android-разработки даёт общий контекст, в котором Gradle является системой сборки. Понимание архитектуры Android-приложения (модули, компоненты, ресурсы) необходимо для осмысленной работы с build.gradle.kts. Рекомендуется начинать с overview.

**[[android-build-evolution]]** — История систем сборки Android (Ant, Maven, Gradle) объясняет, почему текущий стек выглядит именно так: Kotlin DSL вместо Groovy, Version Catalogs вместо ext-блоков, Convention Plugins вместо buildSrc. Знание эволюции помогает при миграции legacy-проектов и понимании deprecated подходов.

**[[android-dependencies]]** — Управление зависимостями является одной из ключевых задач Gradle. Понимание configurations (implementation, api, compileOnly), Version Catalogs, BOM и conflict resolution тесно связано с Gradle fundamentals. Рекомендуется изучать dependency management как продолжение данного материала.

**[[android-compilation-pipeline]]** — Gradle Task Graph определяет порядок выполнения компиляции: AAPT2 для ресурсов, kotlinc/javac для кода, KAPT/KSP для annotation processing, D8/R8 для DEX. Понимание pipeline помогает диагностировать медленные билды и правильно настраивать incremental builds.

**[[android-proguard-r8]]** — R8 (замена ProGuard) интегрирован в Gradle build pipeline и управляется через proguard-rules.pro и AGP конфигурацию. Понимание Gradle task graph объясняет, когда и как R8 обрабатывает код. Изучайте после базового освоения Gradle.

---

## Источники и дальнейшее чтение

| # | Источник | Тип | Ключевой вклад |
|---|----------|-----|----------------|
| 1 | [Configure your build](https://developer.android.com/build) | Official Docs | Основы конфигурации |
| 2 | [AGP 8.x Release Notes](https://developer.android.com/build/releases/gradle-plugin) | Official Docs | Новые фичи AGP 8.x |
| 3 | [Migrate to Kotlin DSL](https://developer.android.com/build/migrate-to-kotlin-dsl) | Official Docs | Миграция на Kotlin DSL |
| 4 | [Version Catalogs](https://docs.gradle.org/current/userguide/version_catalogs.html) | Official Docs | libs.versions.toml |
| 5 | [Convention Plugins](https://docs.gradle.org/current/samples/sample_convention_plugins.html) | Official Docs | build-logic структура |
| 6 | [Configuration Cache](https://docs.gradle.org/current/userguide/configuration_cache.html) | Official Docs | Оптимизация билда |
| 7 | [Gradle 8.11: Faster Configuration Cache](https://dev.to/cdsap/gradle-811-faster-configuration-cache-and-improved-configuration-time-ja1) | Blog | +8-14% к скорости |
| 8 | [Making Your Android Project Modular With Convention Plugins](https://michiganlabs.com/blogs/making-your-android-project-modular-with-convention-plugins) | Blog | Практика convention plugins |
| 9 | [Build Modular Android Projects](https://medium.com/@a.f.k/build-modular-android-projects-with-custom-gradle-plugin-jetpack-compose-friendly-c76bbe51d639) | Blog | Модульная архитектура |
| 10 | [Now in Android](https://github.com/android/nowinandroid) | GitHub | Референсная реализация |

### Книги

- **Meier R. (2022)** *Professional Android* — практическое руководство по настройке Gradle для Android проектов, включая Build Variants, Product Flavors и signing configurations.
- **Phillips B. et al. (2022)** *Android Programming: The Big Nerd Ranch Guide* — введение в Gradle и AGP для начинающих, включая работу с dependencies и build types.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
