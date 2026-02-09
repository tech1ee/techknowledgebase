---
title: "Структура Android-проекта: модули, директории, конфигурация"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [modular-architecture, dependency-graph, namespace-isolation, convention-over-configuration]
tags:
  - android
  - project-structure
  - modules
  - gradle
  - multi-module
related:
  - "[[android-overview]]"
  - "[[android-gradle-fundamentals]]"
  - "[[android-manifest]]"
  - "[[android-resources-system]]"
  - "[[android-architecture-patterns]]"
---

# Структура Android-проекта: модули, директории, конфигурация

Правильная структура проекта — это фундамент масштабируемости. Понимание того, какие файлы где находятся и зачем, позволяет быстро ориентироваться в любом Android-проекте и принимать правильные архитектурные решения.

> **Prerequisites:**
> - [[android-gradle-fundamentals]] — основы Gradle и AGP
> - [[android-overview]] — базовое понимание Android

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Module** | Независимый компонент проекта со своим build.gradle |
| **Source Set** | Набор исходных файлов для определённого варианта |
| **Application Module** | Модуль, собирающийся в APK/AAB |
| **Library Module** | Модуль, собирающийся в AAR для переиспользования |
| **Dynamic Feature** | Модуль, загружаемый по требованию |
| **Build Variant** | Комбинация Build Type и Product Flavor |
| **Gradle Wrapper** | Скрипт для запуска Gradle определённой версии |

---

## Стандартная структура проекта

```
MyApp/
├── .gradle/                    # Кэш Gradle (в .gitignore)
├── .idea/                      # Настройки Android Studio (частично в .gitignore)
├── build/                      # Артефакты сборки проекта (в .gitignore)
├── gradle/
│   ├── libs.versions.toml      # Version Catalog
│   └── wrapper/
│       ├── gradle-wrapper.jar  # Gradle Wrapper JAR
│       └── gradle-wrapper.properties  # Версия Gradle
├── app/                        # Application module
│   ├── build/                  # Артефакты сборки модуля (в .gitignore)
│   ├── src/
│   │   ├── main/               # Основной source set
│   │   ├── debug/              # Source set для debug
│   │   ├── release/            # Source set для release
│   │   ├── test/               # Unit тесты
│   │   └── androidTest/        # Instrumented тесты
│   ├── build.gradle.kts        # Конфигурация модуля
│   └── proguard-rules.pro      # ProGuard/R8 правила
├── core/                       # Core модули
│   ├── data/
│   ├── domain/
│   └── ui/
├── feature/                    # Feature модули
│   ├── home/
│   ├── profile/
│   └── settings/
├── build.gradle.kts            # Корневой build file
├── settings.gradle.kts         # Настройки проекта и модулей
├── gradle.properties           # Свойства Gradle
├── local.properties            # Локальные пути (в .gitignore)
├── gradlew                     # Gradle Wrapper (Unix)
├── gradlew.bat                 # Gradle Wrapper (Windows)
└── .gitignore                  # Git ignore rules
```

---

## Source Sets: организация кода

### Структура main source set

```
app/src/main/
├── AndroidManifest.xml         # Манифест приложения
├── kotlin/                     # Kotlin исходники (или java/)
│   └── com/
│       └── example/
│           └── myapp/
│               ├── MainActivity.kt
│               ├── MyApplication.kt
│               ├── di/         # Dependency Injection
│               ├── ui/         # UI компоненты
│               └── utils/      # Утилиты
├── res/                        # Ресурсы
│   ├── drawable/               # Графика (vectors, shapes)
│   ├── drawable-hdpi/          # Растровая графика (hdpi)
│   ├── drawable-xhdpi/         # Растровая графика (xhdpi)
│   ├── drawable-xxhdpi/        # Растровая графика (xxhdpi)
│   ├── drawable-xxxhdpi/       # Растровая графика (xxxhdpi)
│   ├── layout/                 # XML layouts
│   ├── menu/                   # Menu ресурсы
│   ├── mipmap-hdpi/            # Иконки приложения
│   ├── mipmap-xhdpi/
│   ├── mipmap-xxhdpi/
│   ├── mipmap-xxxhdpi/
│   ├── mipmap-anydpi-v26/      # Adaptive icons
│   ├── navigation/             # Navigation graphs
│   ├── values/                 # Строки, цвета, стили, темы
│   │   ├── strings.xml
│   │   ├── colors.xml
│   │   ├── themes.xml
│   │   └── dimens.xml
│   ├── values-night/           # Dark theme
│   ├── values-ru/              # Русская локализация
│   ├── values-sw600dp/         # Tablet-specific values
│   ├── xml/                    # Конфигурационные XML
│   └── raw/                    # Raw файлы (audio, video)
├── assets/                     # Assets (fonts, databases)
└── jniLibs/                    # Native библиотеки (.so)
    ├── arm64-v8a/
    ├── armeabi-v7a/
    └── x86_64/
```

### Source Sets для Build Variants

```
app/src/
├── main/                       # Общий код для всех вариантов
│   └── kotlin/com/example/
│       └── NetworkClient.kt    # Базовая реализация
│
├── debug/                      # Только для debug builds
│   ├── kotlin/com/example/
│   │   └── DebugTools.kt      # Debug-only утилиты
│   └── res/values/
│       └── strings.xml        # Debug строки (app_name = "MyApp DEV")
│
├── release/                    # Только для release builds
│   └── kotlin/com/example/
│       └── ReleaseConfig.kt   # Release-only конфигурация
│
├── dev/                        # Product Flavor: dev
│   ├── kotlin/com/example/
│   │   └── ApiConfig.kt       # dev API URL
│   └── res/
│       └── values/
│           └── strings.xml
│
├── prod/                       # Product Flavor: prod
│   └── kotlin/com/example/
│       └── ApiConfig.kt       # prod API URL
│
├── devDebug/                   # Комбинация: dev + debug
│   └── kotlin/com/example/
│       └── DevDebugSetup.kt   # Специфичный код
│
├── test/                       # Unit тесты (JVM)
│   └── kotlin/com/example/
│       └── NetworkClientTest.kt
│
└── androidTest/                # Instrumented тесты (устройство)
    └── kotlin/com/example/
        └── MainActivityTest.kt
```

### Приоритет Source Sets

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 ПРИОРИТЕТ MERGE SOURCE SETS                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Для варианта: devDebug                                                 │
│                                                                         │
│  Приоритет (высший → низший):                                           │
│                                                                         │
│  1. src/devDebug/     ← Специфичный для комбинации                     │
│  2. src/dev/          ← Product Flavor                                  │
│  3. src/debug/        ← Build Type                                      │
│  4. src/main/         ← Общий код                                       │
│                                                                         │
│  Ресурсы:                                                               │
│  • Файлы с одинаковым именем — заменяются (выигрывает высший приоритет)│
│  • values/*.xml — мержатся (можно переопределить отдельные строки)     │
│                                                                         │
│  Код:                                                                   │
│  • Классы с одинаковым FQN — ошибка компиляции                         │
│  • Используйте expect/actual или интерфейсы для замены реализаций      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Gradle конфигурационные файлы

### settings.gradle.kts

```kotlin
// settings.gradle.kts — точка входа, определяет структуру проекта

pluginManagement {
    // Репозитории для плагинов
    repositories {
        google {
            content {
                includeGroupByRegex("com\\.android.*")
                includeGroupByRegex("com\\.google.*")
                includeGroupByRegex("androidx.*")
            }
        }
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    // Централизованное управление репозиториями
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
        maven { url = uri("https://jitpack.io") }
    }
}

// Название проекта
rootProject.name = "MyApp"

// Модули проекта
include(":app")

// Core модули
include(":core:data")
include(":core:domain")
include(":core:ui")
include(":core:network")
include(":core:database")
include(":core:common")

// Feature модули
include(":feature:home")
include(":feature:profile")
include(":feature:settings")
include(":feature:auth")

// Build logic (convention plugins)
includeBuild("build-logic")
```

### gradle.properties

```properties
# gradle.properties — глобальные свойства

# === JVM Settings ===
org.gradle.jvmargs=-Xmx4096m -XX:+UseParallelGC -XX:MaxMetaspaceSize=1g

# === Gradle Settings ===
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.daemon=true

# === Kotlin Settings ===
kotlin.code.style=official
kotlin.incremental=true
kotlin.daemon.jvmargs=-Xmx2048m

# === Android Settings ===
android.useAndroidX=true
android.nonTransitiveRClass=true
android.defaults.buildfeatures.buildconfig=true

# === Custom Properties ===
# Используются в build.gradle.kts
myapp.versionCode=1
myapp.versionName=1.0.0
myapp.minSdk=24
myapp.targetSdk=35
myapp.compileSdk=35
```

### local.properties

```properties
# local.properties — локальные настройки (НЕ коммитить в Git!)

# Путь к Android SDK
sdk.dir=/Users/username/Library/Android/sdk

# Путь к NDK (опционально)
ndk.dir=/Users/username/Library/Android/sdk/ndk/25.2.9519653

# Keystore для подписи (опционально)
keystore.path=/Users/username/keystores/release.keystore
keystore.password=mySecretPassword
key.alias=myapp
key.password=myKeyPassword

# API ключи (опционально)
MAPS_API_KEY=AIzaSy...
```

### gradle/libs.versions.toml

```toml
# gradle/libs.versions.toml — Version Catalog

[versions]
# Android & Kotlin
agp = "8.7.0"
kotlin = "2.0.21"
ksp = "2.0.21-1.0.27"

# AndroidX
core-ktx = "1.15.0"
lifecycle = "2.8.7"
activity-compose = "1.9.3"
navigation = "2.8.4"

# Compose
compose-bom = "2024.10.01"
compose-compiler = "1.5.14"

# Networking
retrofit = "2.11.0"
okhttp = "4.12.0"
kotlinx-serialization = "1.7.3"

# Database
room = "2.6.1"

# DI
hilt = "2.52"

# Testing
junit = "4.13.2"
mockk = "1.13.12"
turbine = "1.1.0"
coroutines-test = "1.9.0"

[libraries]
# AndroidX Core
androidx-core-ktx = { group = "androidx.core", name = "core-ktx", version.ref = "core-ktx" }
androidx-lifecycle-runtime-ktx = { group = "androidx.lifecycle", name = "lifecycle-runtime-ktx", version.ref = "lifecycle" }
androidx-lifecycle-viewmodel-compose = { group = "androidx.lifecycle", name = "lifecycle-viewmodel-compose", version.ref = "lifecycle" }
androidx-activity-compose = { group = "androidx.activity", name = "activity-compose", version.ref = "activity-compose" }

# Compose
androidx-compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
androidx-compose-ui = { group = "androidx.compose.ui", name = "ui" }
androidx-compose-ui-graphics = { group = "androidx.compose.ui", name = "ui-graphics" }
androidx-compose-ui-tooling = { group = "androidx.compose.ui", name = "ui-tooling" }
androidx-compose-ui-tooling-preview = { group = "androidx.compose.ui", name = "ui-tooling-preview" }
androidx-compose-material3 = { group = "androidx.compose.material3", name = "material3" }
androidx-navigation-compose = { group = "androidx.navigation", name = "navigation-compose", version.ref = "navigation" }

# Networking
retrofit = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }
retrofit-kotlinx-serialization = { group = "com.squareup.retrofit2", name = "converter-kotlinx-serialization", version.ref = "retrofit" }
okhttp = { group = "com.squareup.okhttp3", name = "okhttp", version.ref = "okhttp" }
okhttp-logging = { group = "com.squareup.okhttp3", name = "logging-interceptor", version.ref = "okhttp" }
kotlinx-serialization-json = { group = "org.jetbrains.kotlinx", name = "kotlinx-serialization-json", version.ref = "kotlinx-serialization" }

# Database
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }

# DI
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }
hilt-navigation-compose = { group = "androidx.hilt", name = "hilt-navigation-compose", version = "1.2.0" }

# Testing
junit = { group = "junit", name = "junit", version.ref = "junit" }
mockk = { group = "io.mockk", name = "mockk", version.ref = "mockk" }
turbine = { group = "app.cash.turbine", name = "turbine", version.ref = "turbine" }
kotlinx-coroutines-test = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-test", version.ref = "coroutines-test" }

[bundles]
compose = [
    "androidx-compose-ui",
    "androidx-compose-ui-graphics",
    "androidx-compose-ui-tooling-preview",
    "androidx-compose-material3",
]
compose-debug = [
    "androidx-compose-ui-tooling",
]
network = [
    "retrofit",
    "retrofit-kotlinx-serialization",
    "okhttp",
    "okhttp-logging",
    "kotlinx-serialization-json",
]
room = [
    "room-runtime",
    "room-ktx",
]

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
```

---

## Модульная архитектура

### Типы модулей

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ТИПЫ МОДУЛЕЙ                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    APPLICATION MODULE                            │   │
│  │  com.android.application                                         │   │
│  │  • Собирается в APK/AAB                                          │   │
│  │  • Содержит Application class                                    │   │
│  │  • Основной entry point                                          │   │
│  │  • Обычно: :app                                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│                                    ▼                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     LIBRARY MODULES                              │   │
│  │  com.android.library                                             │   │
│  │  • Собираются в AAR                                              │   │
│  │  • Переиспользуемый код                                          │   │
│  │  • Feature modules: :feature:home, :feature:profile              │   │
│  │  • Core modules: :core:data, :core:domain, :core:ui              │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                    │                                    │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   DYNAMIC FEATURE MODULES                        │   │
│  │  com.android.dynamic-feature                                     │   │
│  │  • Загружаются по требованию                                     │   │
│  │  • Уменьшают начальный размер APK                                │   │
│  │  • Используют Play Core Library                                  │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    KOTLIN/JAVA MODULES                           │   │
│  │  kotlin("jvm") / java-library                                    │   │
│  │  • Чистый Kotlin/Java без Android                                │   │
│  │  • Domain logic, utilities                                       │   │
│  │  • Быстрее компилируются                                         │   │
│  │  • :core:domain часто такой                                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Рекомендуемая структура модулей

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    МОДУЛЬНАЯ АРХИТЕКТУРА                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│                            ┌───────────┐                                │
│                            │   :app    │                                │
│                            └─────┬─────┘                                │
│                                  │                                      │
│              ┌───────────────────┼───────────────────┐                  │
│              ▼                   ▼                   ▼                  │
│        ┌───────────┐       ┌───────────┐       ┌───────────┐           │
│        │ :feature  │       │ :feature  │       │ :feature  │           │
│        │   :home   │       │ :profile  │       │ :settings │           │
│        └─────┬─────┘       └─────┬─────┘       └─────┬─────┘           │
│              │                   │                   │                  │
│              └───────────────────┼───────────────────┘                  │
│                                  │                                      │
│                                  ▼                                      │
│                          ┌─────────────┐                                │
│                          │  :core:ui   │ ← Compose components           │
│                          └──────┬──────┘                                │
│                                 │                                       │
│              ┌──────────────────┼──────────────────┐                    │
│              ▼                  ▼                  ▼                    │
│        ┌───────────┐      ┌───────────┐      ┌───────────┐             │
│        │  :core    │      │  :core    │      │  :core    │             │
│        │  :domain  │◀─────│  :data    │      │ :network  │             │
│        └───────────┘      └─────┬─────┘      └───────────┘             │
│              │                  │                                       │
│              │                  ▼                                       │
│              │           ┌───────────┐                                  │
│              │           │  :core    │                                  │
│              └──────────▶│ :database │                                  │
│                          └───────────┘                                  │
│                                                                         │
│  Правила:                                                               │
│  • :app зависит только от :feature модулей                             │
│  • :feature зависит от :core:ui и :core:domain                         │
│  • :core:data зависит от :core:domain (инверсия зависимостей)          │
│  • :core:domain — чистый Kotlin, без Android зависимостей              │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Пример: core:domain модуль

```kotlin
// core/domain/build.gradle.kts
plugins {
    kotlin("jvm")  // Чистый Kotlin, без Android!
}

dependencies {
    // Только Kotlin stdlib и coroutines
    implementation(libs.kotlinx.coroutines.core)

    // Тестирование
    testImplementation(libs.junit)
    testImplementation(libs.mockk)
    testImplementation(libs.kotlinx.coroutines.test)
}
```

```kotlin
// core/domain/src/main/kotlin/com/example/domain/model/User.kt
package com.example.domain.model

data class User(
    val id: String,
    val name: String,
    val email: String,
)

// core/domain/src/main/kotlin/com/example/domain/repository/UserRepository.kt
package com.example.domain.repository

import com.example.domain.model.User
import kotlinx.coroutines.flow.Flow

interface UserRepository {
    fun getUser(id: String): Flow<User>
    suspend fun updateUser(user: User)
}

// core/domain/src/main/kotlin/com/example/domain/usecase/GetUserUseCase.kt
package com.example.domain.usecase

import com.example.domain.model.User
import com.example.domain.repository.UserRepository
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject

class GetUserUseCase @Inject constructor(
    private val userRepository: UserRepository,
) {
    operator fun invoke(userId: String): Flow<User> {
        return userRepository.getUser(userId)
    }
}
```

### Пример: core:data модуль

```kotlin
// core/data/build.gradle.kts
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.core.data"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
    }
}

dependencies {
    // Зависимость от domain
    implementation(project(":core:domain"))
    implementation(project(":core:network"))
    implementation(project(":core:database"))

    // Hilt
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)

    // Coroutines
    implementation(libs.kotlinx.coroutines.android)
}
```

### Пример: feature:home модуль

```kotlin
// feature/home/build.gradle.kts
plugins {
    alias(libs.plugins.android.library)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.example.feature.home"
    compileSdk = 35

    defaultConfig {
        minSdk = 24
    }

    buildFeatures {
        compose = true
    }
}

dependencies {
    // Core modules
    implementation(project(":core:ui"))
    implementation(project(":core:domain"))

    // Compose
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.bundles.compose)

    // Hilt
    implementation(libs.hilt.android)
    implementation(libs.hilt.navigation.compose)
    ksp(libs.hilt.compiler)

    // Testing
    testImplementation(libs.junit)
    testImplementation(libs.mockk)
}
```

---

## Convention Plugins

Convention Plugins позволяют избежать дублирования конфигурации.

### Структура build-logic

```
build-logic/
├── convention/
│   ├── build.gradle.kts
│   └── src/main/kotlin/
│       ├── AndroidApplicationConventionPlugin.kt
│       ├── AndroidLibraryConventionPlugin.kt
│       ├── AndroidComposeConventionPlugin.kt
│       ├── AndroidHiltConventionPlugin.kt
│       └── KotlinLibraryConventionPlugin.kt
└── settings.gradle.kts
```

### build-logic/settings.gradle.kts

```kotlin
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
    versionCatalogs {
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}

rootProject.name = "build-logic"
include(":convention")
```

### build-logic/convention/build.gradle.kts

```kotlin
plugins {
    `kotlin-dsl`
}

dependencies {
    compileOnly(libs.android.gradlePlugin)
    compileOnly(libs.kotlin.gradlePlugin)
    compileOnly(libs.compose.gradlePlugin)
    compileOnly(libs.ksp.gradlePlugin)
}

gradlePlugin {
    plugins {
        register("androidApplication") {
            id = "myapp.android.application"
            implementationClass = "AndroidApplicationConventionPlugin"
        }
        register("androidLibrary") {
            id = "myapp.android.library"
            implementationClass = "AndroidLibraryConventionPlugin"
        }
        register("androidCompose") {
            id = "myapp.android.compose"
            implementationClass = "AndroidComposeConventionPlugin"
        }
        register("androidHilt") {
            id = "myapp.android.hilt"
            implementationClass = "AndroidHiltConventionPlugin"
        }
        register("kotlinLibrary") {
            id = "myapp.kotlin.library"
            implementationClass = "KotlinLibraryConventionPlugin"
        }
    }
}
```

### AndroidLibraryConventionPlugin.kt

```kotlin
import com.android.build.gradle.LibraryExtension
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure

class AndroidLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            with(pluginManager) {
                apply("com.android.library")
                apply("org.jetbrains.kotlin.android")
            }

            extensions.configure<LibraryExtension> {
                compileSdk = 35

                defaultConfig {
                    minSdk = 24
                    testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
                }

                compileOptions {
                    sourceCompatibility = JavaVersion.VERSION_17
                    targetCompatibility = JavaVersion.VERSION_17
                }
            }
        }
    }
}
```

### Использование convention plugins

```kotlin
// feature/home/build.gradle.kts
plugins {
    id("myapp.android.library")
    id("myapp.android.compose")
    id("myapp.android.hilt")
}

android {
    namespace = "com.example.feature.home"
}

dependencies {
    implementation(project(":core:ui"))
    implementation(project(":core:domain"))
}
// Всё остальное настроено в convention plugins!
```

---

## .gitignore для Android

```gitignore
# .gitignore — правила для Git

# === Gradle ===
.gradle/
build/
!gradle/wrapper/gradle-wrapper.jar

# === IDE ===
.idea/
*.iml
*.iws
*.ipr
local.properties

# === Android ===
*.apk
*.aab
*.ap_
*.dex
*.class
gen/
out/
bin/

# === Kotlin ===
*.kotlin_module

# === Testing ===
.coverage/
coverage.ec

# === OS ===
.DS_Store
Thumbs.db

# === Secrets ===
*.keystore
*.jks
google-services.json
secrets.properties
apikey.properties

# === Crash Reports ===
*.hprof
```

---

## Проверь себя

<details>
<summary>1. В чём разница между main и debug source sets?</summary>

**Ответ:**
- **main** — код, который включается во все варианты сборки (debug, release, и т.д.)
- **debug** — код, который включается только в debug builds

Source sets мержатся по приоритету: debug/release переопределяют main. Ресурсы в values/ мержатся, остальные файлы заменяются.

</details>

<details>
<summary>2. Зачем нужны convention plugins?</summary>

**Ответ:**
Convention plugins устраняют дублирование конфигурации между модулями. Вместо копирования одинаковых настроек compileSdk, minSdk, compileOptions в каждый модуль, эти настройки определяются один раз в convention plugin и применяются ко всем модулям.

Преимущества:
1. DRY — не повторяемся
2. Консистентность — все модули настроены одинаково
3. Легко обновлять — изменение в одном месте

</details>

<details>
<summary>3. Почему :core:domain должен быть Kotlin/JVM модулем, а не Android?</summary>

**Ответ:**
Domain модуль содержит бизнес-логику, которая не должна зависеть от Android:
1. **Быстрее компилируется** — не нужен Android SDK
2. **Проще тестировать** — обычные JUnit тесты без эмулятора
3. **Переиспользуемость** — можно использовать в KMP проектах
4. **Чистая архитектура** — domain не знает о платформе

</details>

<details>
<summary>4. Что такое Version Catalog и зачем он нужен?</summary>

**Ответ:**
Version Catalog (libs.versions.toml) — централизованное хранилище версий зависимостей:
1. **Единый источник правды** — все версии в одном файле
2. **Type-safe** — `libs.retrofit` вместо строки, IDE подсказывает
3. **Bundles** — группировка связанных зависимостей
4. **Plugins** — версии плагинов тоже централизованы

Это избавляет от проблемы разных версий одной библиотеки в разных модулях.

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Monolith проще multi-module" | Monolith проще только на старте (до ~50k LOC). После этого сборка замедляется экспоненциально, конфликты слияния учащаются, а навигация по коду становится мучительной. Multi-module с самого начала — инвестиция в будущую скорость разработки |
| "Каждая фича = отдельный модуль" | Слишком мелкие модули создают overhead: время конфигурации Gradle, сложность dependency graph. Оптимально — модуль на 5-15k строк кода. Слишком крупные модули теряют преимущества параллельной сборки |
| ":app модуль должен быть маленьким" | :app модуль — точка сборки, а не место для кода. Он должен содержать только Application class, DI setup, и navigation graph. Вся бизнес-логика — в feature/domain модулях |
| "buildSrc лучше Convention Plugins" | buildSrc перекомпилирует весь проект при любом изменении. Composite builds с Convention Plugins в отдельном gradle project компилируются инкрементально и поддерживают Configuration Cache |
| ":core:common — хорошая идея" | Common модули становятся "свалкой" для всего подряд, создавая циклические зависимости и замедляя сборку. Лучше: :core:ui, :core:network, :core:database — по конкретному назначению |
| "Плоская структура feature модулей достаточна" | Для 5+ фич нужна вложенная структура: :feature:profile:api, :feature:profile:impl, :feature:profile:ui. Это позволяет скрывать implementation details и уменьшать recompilation scope |
| "Version Catalogs только для версий" | libs.versions.toml поддерживает bundles (группы зависимостей), plugins, и даже BOM. Это полноценная система управления зависимостями, не только версиями |
| "Модули без Android SDK медленнее" | Наоборот: Kotlin/JVM модули (:core:domain) компилируются быстрее, тестируются без эмулятора, и могут переиспользоваться в KMP. Domain layer всегда должен быть Kotlin/JVM |
| "Gradle dependency configurations сложные" | Основных всего 3: implementation (внутренняя), api (экспортируемая), compileOnly (только компиляция). Всё остальное — вариации для тестов и специфичных случаев |
| "Source sets — только для build types" | Source sets работают для: build types (debug/release), flavors (free/paid), build variants (freeDebug), и даже test types (test/androidTest). Это мощный механизм организации кода |

---

## CS-фундамент

| CS-концепция | Применение в Android Project Structure |
|--------------|----------------------------------------|
| **Directed Acyclic Graph (DAG)** | Dependency graph между модулями — ациклический граф. Gradle использует DAG для определения порядка сборки и параллелизма. Циклические зависимости запрещены |
| **Модульность (Modularity)** | Разделение кода на модули с чёткими boundaries уменьшает coupling и увеличивает cohesion. Каждый модуль — единица изменений с собственным API |
| **Инкапсуляция (Encapsulation)** | internal visibility в Kotlin ограничивает доступ границами модуля. :api/:impl разделение скрывает реализацию от потребителей |
| **Separation of Concerns** | Layered architecture (:data → :domain → :presentation) разделяет ответственности. Каждый слой знает только о нижележащих слоях |
| **Инверсия зависимостей (DIP)** | :feature:profile:api определяет интерфейсы, :feature:profile:impl реализует. Зависимость направлена на абстракции, не на реализации |
| **Параллельные вычисления** | Gradle параллельно компилирует независимые модули. Больше модулей = больше параллелизма, но overhead на конфигурацию |
| **Кэширование (Caching)** | Build cache хранит скомпилированные артефакты по content hash. Configuration cache кэширует граф задач. Remote cache ускоряет сборку в CI |
| **Топологическая сортировка** | Gradle сортирует задачи в topological order по DAG зависимостей. Это гарантирует, что зависимости собраны до зависимых модулей |
| **Information Hiding** | api vs implementation конфигурации контролируют, какие зависимости "протекают" наружу. implementation скрывает internal dependencies |
| **Build Reproducibility** | Version Catalogs + dependency locking обеспечивают детерминированные сборки. Одинаковый код → одинаковый артефакт |

---

## Связи

**Gradle:**
- [[android-gradle-fundamentals]] — основы Gradle и AGP
- [[android-dependencies]] — управление зависимостями

**Архитектура:**
- [[android-architecture-patterns]] — MVVM, Clean Architecture
- [[android-manifest]] — AndroidManifest.xml

**Ресурсы:**
- [[android-resources-system]] — система ресурсов Android

---

## Источники

- [Create an Android project - Android Developers](https://developer.android.com/studio/projects)
- [Configure your build - Android Developers](https://developer.android.com/build)
- [Add build dependencies - Android Developers](https://developer.android.com/build/dependencies)
- [Create source sets - Android Developers](https://developer.android.com/build/build-variants#sourcesets)
- [Guide to app architecture - Android Developers](https://developer.android.com/topic/architecture)
- [Now in Android - GitHub](https://github.com/android/nowinandroid) — reference project

---

*Проверено: 2026-01-09 | На основе официальной документации Android*
