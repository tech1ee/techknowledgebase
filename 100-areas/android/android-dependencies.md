---
title: "Android Dependencies: Управление зависимостями в Gradle"
created: 2025-01-15
modified: 2026-01-05
cs-foundations: [dependency-resolution, version-conflict, transitive-dependencies, build-graph]
tags:
  - android
  - gradle
  - dependencies
  - maven
  - version-catalog
  - bom
  - build
related:
  - "[[android-gradle-fundamentals]]"
  - "[[android-project-structure]]"
  - "[[android-build-evolution]]"
---

# Android Dependencies: Управление зависимостями в Gradle

> Полное руководство по dependency management: implementation vs api, Version Catalogs, BOM, conflict resolution.

---

## Зачем это нужно

### Проблема: "Dependency Hell"

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| **Конфликт версий** | Разные библиотеки требуют разные версии одной зависимости | NoSuchMethodError, ClassNotFoundException в runtime |
| **Медленные builds** | Неправильный scope (api везде) | Всё пересобирается при любом изменении |
| **Дублирование** | Версии в каждом модуле | Рассинхронизация, ошибки обновления |
| **Сломанные обновления** | Transitive dependencies изменились | "Работало вчера, сломалось сегодня" |

### Актуальность 2024-2025

| Инструмент | Статус | Описание |
|------------|--------|----------|
| **Version Catalogs** | ✅ Стандарт | libs.versions.toml в каждом новом проекте |
| **BOM (Bill of Materials)** | ✅ Рекомендуется | Compose BOM, Firebase BOM |
| **Convention Plugins** | ✅ Best Practice | Замена buildSrc для shared logic |
| **Dependency Locking** | ⚠️ Для CI | Reproducible builds |
| **buildSrc** | ⚠️ Legacy | Замедляет configuration, мигрируйте на Version Catalogs |

**Ключевые изменения:**
- `libs.versions.toml` — стандарт с Android Studio Giraffe
- Compose BOM 2024 — единая версия для всех Compose библиотек
- `implementation` — всегда по умолчанию, `api` — только когда нужно

### Что даёт правильное управление

```
До:                                 После:
┌──────────────────────┐            ┌──────────────────────┐
│ версии в каждом      │            │ libs.versions.toml   │
│ build.gradle         │            │ единый источник      │
│ конфликты версий     │            │ совместимые версии   │
│ медленные билды      │            │ быстрые builds       │
└──────────────────────┘            └──────────────────────┘
```

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **Dependency** | Внешняя библиотека или модуль, необходимый для сборки |
| **Transitive Dependency** | Зависимость зависимости (автоматически подтягивается) |
| **Repository** | Хранилище артефактов (Maven Central, Google Maven) |
| **Artifact** | Конкретный файл/пакет в репозитории (JAR, AAR) |
| **GAV** | Group:Artifact:Version — координаты зависимости |
| **BOM** | Bill of Materials — спецификация версий для группы библиотек |
| **Version Catalog** | Централизованное управление версиями в Gradle |
| **Configuration** | Scope зависимости (implementation, api, compileOnly) |
| **Resolution** | Процесс разрешения версий при конфликтах |
| **AAR** | Android Archive — формат Android библиотеки |

---

## Dependency Coordinates (GAV)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEPENDENCY COORDINATES                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  implementation("androidx.core:core-ktx:1.12.0")                           │
│                  ──────────── ──────── ──────                               │
│                       │          │       │                                  │
│                       │          │       └── Version                        │
│                       │          └── Artifact ID                            │
│                       └── Group ID                                          │
│                                                                             │
│  Полная форма (редко используется):                                        │
│  implementation("group:artifact:version:classifier@extension")             │
│                                                                             │
│  Примеры:                                                                   │
│  • implementation("com.google.code.gson:gson:2.10.1")                      │
│  • implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.7.3")   │
│  • implementation("com.squareup.retrofit2:retrofit:2.9.0")                 │
│                                                                             │
│  Версии:                                                                    │
│  • Точная: "1.2.3"                                                         │
│  • Range: "[1.0, 2.0)" — от 1.0 включительно до 2.0 не включая            │
│  • Latest: "+" или "latest.release" (НЕ рекомендуется!)                   │
│  • Snapshot: "1.0-SNAPSHOT" (dev версии)                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Repositories (Репозитории)

### Основные репозитории

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        // Google Maven — AndroidX, Google libraries
        google()

        // Maven Central — большинство open source библиотек
        mavenCentral()

        // JitPack — GitHub-based builds
        maven { url = uri("https://jitpack.io") }

        // Собственный/приватный репозиторий
        maven {
            url = uri("https://maven.mycompany.com/releases")
            credentials {
                username = providers.gradleProperty("maven.user").get()
                password = providers.gradleProperty("maven.password").get()
            }
        }
    }
}
```

### Репозитории подробнее

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         REPOSITORY OVERVIEW                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Google Maven Repository                                                    │
│  URL: https://maven.google.com                                              │
│  ├── AndroidX библиотеки                                                   │
│  ├── Google Play Services                                                   │
│  ├── Firebase                                                               │
│  ├── Material Components                                                    │
│  └── Android Gradle Plugin                                                  │
│                                                                             │
│  Maven Central                                                              │
│  URL: https://repo.maven.apache.org/maven2                                 │
│  ├── Kotlin stdlib/coroutines                                              │
│  ├── Retrofit, OkHttp                                                       │
│  ├── Gson, Moshi                                                            │
│  ├── JUnit, Mockito                                                         │
│  └── Большинство Java/Kotlin библиотек                                     │
│                                                                             │
│  JCenter (DEPRECATED!)                                                      │
│  URL: https://jcenter.bintray.com                                          │
│  ├── Закрыт в 2021                                                         │
│  └── НЕ использовать в новых проектах                                     │
│                                                                             │
│  JitPack                                                                    │
│  URL: https://jitpack.io                                                    │
│  ├── Любой GitHub репозиторий как Maven dependency                         │
│  ├── implementation("com.github.User:Repo:Tag")                            │
│  └── Билдит на лету из source                                              │
│                                                                             │
│  Порядок поиска:                                                            │
│  Gradle ищет в репозиториях в порядке объявления.                          │
│  Первый найденный артефакт используется.                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Repository Content Filtering

```kotlin
// settings.gradle.kts
repositories {
    google {
        content {
            // Только AndroidX и Google группы
            includeGroupByRegex("androidx\\..*")
            includeGroupByRegex("com\\.google\\..*")
            includeGroup("com.android")
        }
    }

    mavenCentral {
        content {
            // Исключить Google артефакты (они в google())
            excludeGroupByRegex("androidx\\..*")
            excludeGroupByRegex("com\\.google\\..*")
        }
    }

    maven("https://jitpack.io") {
        content {
            // Только GitHub packages
            includeGroupByRegex("com\\.github\\..*")
        }
    }
}
```

---

## Dependency Configurations

### Основные конфигурации

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DEPENDENCY CONFIGURATIONS                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  implementation                                                      │   │
│  │  ├── Доступна в compile + runtime                                   │   │
│  │  ├── НЕ видна потребителям библиотеки                               │   │
│  │  └── Рекомендуется по умолчанию                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  api                                                                 │   │
│  │  ├── Доступна в compile + runtime                                   │   │
│  │  ├── ВИДНА потребителям библиотеки (transitive)                    │   │
│  │  ├── Используйте если API вашей библиотеки экспортирует типы       │   │
│  │  └── Замедляет incremental builds                                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  compileOnly                                                         │   │
│  │  ├── Доступна ТОЛЬКО в compile time                                 │   │
│  │  ├── НЕ включается в APK                                            │   │
│  │  └── Для annotation processors, provided dependencies              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  runtimeOnly                                                         │   │
│  │  ├── Доступна ТОЛЬКО в runtime                                      │   │
│  │  ├── Включается в APK, но не видна при компиляции                  │   │
│  │  └── Для реализаций интерфейсов (SLF4J implementations)            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  testImplementation                                                  │   │
│  │  ├── Только для unit tests (src/test)                              │   │
│  │  └── НЕ включается в production APK                                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  androidTestImplementation                                           │   │
│  │  ├── Только для instrumented tests (src/androidTest)               │   │
│  │  └── Включается в test APK                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  kapt / ksp                                                          │   │
│  │  ├── Annotation processors для Kotlin                               │   │
│  │  ├── kapt — старый (работает через Java stubs)                     │   │
│  │  └── ksp — новый, быстрее (Kotlin Symbol Processing)               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  annotationProcessor                                                 │   │
│  │  ├── Annotation processors для Java                                 │   │
│  │  └── Для Kotlin используйте kapt/ksp                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### implementation vs api

```kotlin
// library/build.gradle.kts
dependencies {
    // ❌ api — тип Gson будет виден потребителям
    api("com.google.code.gson:gson:2.10.1")

    // ✅ implementation — внутренняя деталь реализации
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
}

// Пример: когда нужен api
class MyLibraryClass {
    // Возвращаемый тип использует Gson — нужен api
    fun parseJson(json: String): JsonElement {
        return Gson().fromJson(json, JsonElement::class.java)
    }

    // Внутренняя реализация с OkHttp — достаточно implementation
    fun fetchData(): String {
        val client = OkHttpClient()
        // ...
        return response.body?.string() ?: ""
    }
}
```

### Variant-specific Dependencies

```kotlin
// app/build.gradle.kts
dependencies {
    // Для всех вариантов
    implementation(libs.retrofit)

    // Только для debug
    debugImplementation(libs.leakcanary)

    // Только для release
    releaseImplementation(libs.firebase.crashlytics)

    // Для конкретного flavor
    paidImplementation(libs.premium.features)

    // Для конкретного варианта (flavor + build type)
    paidDebugImplementation(libs.debug.tools)
}
```

---

## Transitive Dependencies

### Как работают transitive dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      TRANSITIVE DEPENDENCIES                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Ваш build.gradle.kts:                                                      │
│  implementation("com.squareup.retrofit2:retrofit:2.9.0")                   │
│                                                                             │
│  Что Gradle реально загружает:                                             │
│                                                                             │
│  retrofit:2.9.0                                                             │
│  └─── com.squareup.okhttp3:okhttp:3.14.9        ◀ transitive              │
│       └─── com.squareup.okio:okio:1.17.2        ◀ transitive              │
│                                                                             │
│  Все 3 библиотеки будут в вашем APK!                                       │
│                                                                             │
│  Просмотр дерева зависимостей:                                             │
│  ./gradlew :app:dependencies --configuration releaseRuntimeClasspath       │
│                                                                             │
│  +--- com.squareup.retrofit2:retrofit:2.9.0                                │
│  |    \--- com.squareup.okhttp3:okhttp:3.14.9                              │
│  |         \--- com.squareup.okio:okio:1.17.2                              │
│  +--- ...                                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Исключение transitive dependencies

```kotlin
// build.gradle.kts
dependencies {
    // Исключить конкретную transitive dependency
    implementation("com.example:library:1.0") {
        exclude(group = "org.slf4j", module = "slf4j-api")
    }

    // Исключить все transitive от группы
    implementation("com.example:library:1.0") {
        exclude(group = "org.slf4j")
    }

    // Отключить все transitive dependencies
    implementation("com.example:library:1.0") {
        isTransitive = false
    }
}

// Глобальное исключение
configurations.all {
    exclude(group = "commons-logging", module = "commons-logging")
}
```

---

## Version Resolution и Conflict Resolution

### Как Gradle разрешает конфликты

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        VERSION CONFLICT RESOLUTION                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Ситуация: разные библиотеки требуют разные версии одной зависимости       │
│                                                                             │
│  your-app                                                                   │
│  ├── library-a:1.0                                                         │
│  │   └── okhttp:4.9.0                                                      │
│  └── library-b:2.0                                                         │
│      └── okhttp:4.12.0                                                     │
│                                                                             │
│  Какая версия okhttp будет использована?                                   │
│                                                                             │
│  Default Strategy: HIGHEST VERSION WINS                                    │
│  → okhttp:4.12.0 будет использована                                        │
│                                                                             │
│  Потенциальная проблема:                                                   │
│  library-a может быть несовместима с okhttp:4.12.0!                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Стратегии разрешения

```kotlin
// build.gradle.kts
configurations.all {
    resolutionStrategy {
        // 1. Force конкретную версию (override всего)
        force("com.squareup.okhttp3:okhttp:4.11.0")

        // 2. Fail при конфликте (вместо автоматического выбора)
        failOnVersionConflict()

        // 3. Prefer project modules над external
        preferProjectModules()

        // 4. Использовать конкретную версию для группы
        eachDependency {
            if (requested.group == "org.jetbrains.kotlin") {
                useVersion("1.9.21")
            }
        }

        // 5. Заменить модуль другим
        dependencySubstitution {
            substitute(module("org.json:json"))
                .using(module("com.google.code.gson:gson:2.10.1"))
        }

        // 6. Cache settings
        cacheChangingModulesFor(0, TimeUnit.SECONDS)
        cacheDynamicVersionsFor(10, TimeUnit.MINUTES)
    }
}
```

### Strict Versions

```kotlin
// build.gradle.kts
dependencies {
    // Обычная версия — может быть upgraded
    implementation("com.example:lib:1.0")

    // Strict версия — НЕЛЬЗЯ изменить
    implementation("com.example:lib") {
        version {
            strictly("1.0")
        }
    }

    // Или короткая форма
    implementation("com.example:lib:1.0!!")
}
```

### Просмотр и анализ зависимостей

```bash
# Дерево зависимостей
./gradlew :app:dependencies

# Только для конкретной configuration
./gradlew :app:dependencies --configuration releaseRuntimeClasspath

# Insight о конкретной зависимости
./gradlew :app:dependencyInsight --dependency okhttp

# Вывод:
# com.squareup.okhttp3:okhttp:4.12.0
#    Variant releaseRuntimeClasspath:
#    Selection reasons:
#       - By conflict resolution: between versions 4.9.0 and 4.12.0
#       - Was requested: com.squareup.retrofit2:retrofit:2.9.0
#       - Was requested: com.example:library:1.0
```

---

## BOM (Bill of Materials)

### Что такое BOM

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BILL OF MATERIALS                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Проблема: множество связанных библиотек с разными версиями               │
│                                                                             │
│  // Без BOM — нужно следить за совместимостью вручную                      │
│  implementation("androidx.compose.ui:ui:1.5.4")                            │
│  implementation("androidx.compose.material3:material3:1.1.2")              │
│  implementation("androidx.compose.foundation:foundation:1.5.4")            │
│  implementation("androidx.compose.runtime:runtime:1.5.4")                  │
│  // Какие версии совместимы друг с другом???                               │
│                                                                             │
│  Решение — BOM:                                                             │
│  implementation(platform("androidx.compose:compose-bom:2024.01.00"))       │
│  implementation("androidx.compose.ui:ui")             // версия из BOM     │
│  implementation("androidx.compose.material3:material3")                    │
│  implementation("androidx.compose.foundation:foundation")                  │
│                                                                             │
│  BOM определяет совместимые версии для ВСЕХ библиотек группы              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Использование BOM

```kotlin
// build.gradle.kts
dependencies {
    // Compose BOM
    val composeBom = platform("androidx.compose:compose-bom:2024.01.00")
    implementation(composeBom)
    androidTestImplementation(composeBom)

    // Теперь версии не нужны
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")

    // Firebase BOM
    implementation(platform("com.google.firebase:firebase-bom:32.7.0"))
    implementation("com.google.firebase:firebase-analytics")
    implementation("com.google.firebase:firebase-crashlytics")
    implementation("com.google.firebase:firebase-messaging")

    // OkHttp BOM
    implementation(platform("com.squareup.okhttp3:okhttp-bom:4.12.0"))
    implementation("com.squareup.okhttp3:okhttp")
    implementation("com.squareup.okhttp3:logging-interceptor")

    // Kotlin BOM (для kotlinx библиотек)
    implementation(platform("org.jetbrains.kotlin:kotlin-bom:1.9.21"))
}
```

### Override версии из BOM

```kotlin
// build.gradle.kts
dependencies {
    // BOM
    implementation(platform("androidx.compose:compose-bom:2024.01.00"))

    // Override конкретной библиотеки
    implementation("androidx.compose.material3:material3:1.2.0-beta01")

    // Остальные используют версии из BOM
    implementation("androidx.compose.ui:ui")
}
```

### Популярные BOM

| BOM | Описание |
|-----|----------|
| `androidx.compose:compose-bom` | Jetpack Compose библиотеки |
| `com.google.firebase:firebase-bom` | Firebase SDKs |
| `com.squareup.okhttp3:okhttp-bom` | OkHttp и связанные |
| `io.ktor:ktor-bom` | Ktor клиент/сервер |
| `org.jetbrains.kotlin:kotlin-bom` | Kotlin stdlib |
| `software.amazon.awssdk:bom` | AWS SDK |

---

## Version Catalogs (libs.versions.toml)

### Структура Version Catalog

```toml
# gradle/libs.versions.toml

[versions]
# Версии объявляются здесь
kotlin = "1.9.21"
agp = "8.2.0"
compose-bom = "2024.01.00"
coroutines = "1.7.3"
retrofit = "2.9.0"
room = "2.6.1"
hilt = "2.50"
junit = "4.13.2"

[libraries]
# Библиотеки с референсами на версии
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }

# Можно указать версию напрямую
gson = { module = "com.google.code.gson:gson", version = "2.10.1" }

# Compose BOM
compose-bom = { module = "androidx.compose:compose-bom", version.ref = "compose-bom" }
compose-ui = { module = "androidx.compose.ui:ui" }
compose-material3 = { module = "androidx.compose.material3:material3" }

# Coroutines
coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
coroutines-android = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-android", version.ref = "coroutines" }

# Retrofit
retrofit = { module = "com.squareup.retrofit2:retrofit", version.ref = "retrofit" }
retrofit-gson = { module = "com.squareup.retrofit2:converter-gson", version.ref = "retrofit" }

# Room
room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
room-ktx = { module = "androidx.room:room-ktx", version.ref = "room" }
room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }

# Hilt
hilt-android = { module = "com.google.dagger:hilt-android", version.ref = "hilt" }
hilt-compiler = { module = "com.google.dagger:hilt-compiler", version.ref = "hilt" }

# Testing
junit = { module = "junit:junit", version.ref = "junit" }

[bundles]
# Группы библиотек для удобства
compose = ["compose-ui", "compose-material3"]
retrofit = ["retrofit", "retrofit-gson"]
room = ["room-runtime", "room-ktx"]

[plugins]
# Плагины
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-kapt = { id = "org.jetbrains.kotlin.kapt", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
```

### Использование в build.gradle.kts

```kotlin
// build.gradle.kts
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
}

dependencies {
    // Отдельные библиотеки
    implementation(libs.kotlin.stdlib)
    implementation(libs.gson)

    // BOM
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.compose.material3)

    // Bundle (группа)
    implementation(libs.bundles.retrofit)
    implementation(libs.bundles.room)

    // Annotation processors
    kapt(libs.room.compiler)
    kapt(libs.hilt.compiler)

    // Hilt
    implementation(libs.hilt.android)

    // Testing
    testImplementation(libs.junit)
}
```

### Преимущества Version Catalogs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   VERSION CATALOGS BENEFITS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ Централизованное управление версиями                                   │
│     • Все версии в одном файле                                             │
│     • Легко обновлять                                                      │
│     • Consistent across modules                                            │
│                                                                             │
│  ✅ Type-safe accessors                                                     │
│     • libs.retrofit вместо строки "com.squareup.retrofit2:retrofit:2.9.0" │
│     • IDE autocompletion                                                   │
│     • Compile-time проверка                                                │
│                                                                             │
│  ✅ Bundles для группировки                                                 │
│     • implementation(libs.bundles.compose)                                 │
│     • Меньше boilerplate                                                   │
│                                                                             │
│  ✅ Version references                                                      │
│     • Одна версия для группы библиотек                                     │
│     • room = "2.6.1" → room-runtime, room-ktx, room-compiler              │
│                                                                             │
│  ✅ Плагины тоже поддерживаются                                            │
│     • alias(libs.plugins.kotlin.android)                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Dependency Updates

### Gradle Versions Plugin

```kotlin
// build.gradle.kts (root)
plugins {
    id("com.github.ben-manes.versions") version "0.50.0"
}

// Запуск проверки обновлений
// ./gradlew dependencyUpdates

// Вывод:
// The following dependencies have later release versions:
//  - androidx.core:core-ktx [1.12.0 -> 1.13.0]
//  - com.squareup.retrofit2:retrofit [2.9.0 -> 2.11.0]
```

### Renovate Bot

```json
// renovate.json (в корне репозитория)
{
  "$schema": "https://docs.renovatebot.com/renovate-schema.json",
  "extends": [
    "config:base"
  ],
  "packageRules": [
    {
      "matchPackagePatterns": ["androidx.*"],
      "groupName": "AndroidX"
    },
    {
      "matchPackagePatterns": ["com.google.firebase.*"],
      "groupName": "Firebase"
    },
    {
      "matchPackagePatterns": ["org.jetbrains.kotlin.*"],
      "groupName": "Kotlin"
    }
  ],
  "gradle": {
    "enabled": true
  }
}
```

### Dependabot

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "gradle"
    directory: "/"
    schedule:
      interval: "weekly"
    groups:
      android:
        patterns:
          - "androidx.*"
          - "com.google.android.*"
      kotlin:
        patterns:
          - "org.jetbrains.kotlin*"
```

### Version Catalog Updates Plugin

```kotlin
// settings.gradle.kts
plugins {
    id("nl.littlerobots.version-catalog-update") version "0.8.3"
}

// Обновить libs.versions.toml
// ./gradlew versionCatalogUpdate
```

---

## AAR vs JAR

### Отличия форматов

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           JAR vs AAR                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  JAR (Java Archive)                    AAR (Android Archive)               │
│  ─────────────────────                 ─────────────────────               │
│  library.jar                           library.aar                          │
│  ├── META-INF/                         ├── AndroidManifest.xml             │
│  │   └── MANIFEST.MF                   ├── classes.jar                     │
│  └── com/                              ├── res/                            │
│      └── example/                      ├── R.txt                           │
│          └── *.class                   ├── public.txt                      │
│                                        ├── assets/                         │
│                                        ├── libs/                           │
│                                        ├── jni/                            │
│                                        └── proguard.txt                    │
│                                                                             │
│  JAR:                                  AAR:                                 │
│  • Только Java/Kotlin код             • Код + Android ресурсы              │
│  • Для любой JVM                       • Только для Android                │
│  • Нет ресурсов                        • Layouts, drawables, strings       │
│  • Нет manifest                        • Свой AndroidManifest              │
│                                        • ProGuard consumer rules           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Публикация AAR

```kotlin
// library/build.gradle.kts
plugins {
    id("com.android.library")
    id("maven-publish")
}

android {
    namespace = "com.example.mylibrary"
    // ...

    publishing {
        singleVariant("release") {
            withSourcesJar()
            withJavadocJar()
        }
    }
}

publishing {
    publications {
        register<MavenPublication>("release") {
            groupId = "com.example"
            artifactId = "mylibrary"
            version = "1.0.0"

            afterEvaluate {
                from(components["release"])
            }

            pom {
                name.set("My Library")
                description.set("A useful library")
                url.set("https://github.com/example/mylibrary")
            }
        }
    }

    repositories {
        maven {
            url = uri("https://maven.mycompany.com/releases")
            credentials {
                username = System.getenv("MAVEN_USER")
                password = System.getenv("MAVEN_PASSWORD")
            }
        }
    }
}
```

---

## Типичные проблемы и решения

### 1. Duplicate Class

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DUPLICATE CLASS ERROR                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Error: Duplicate class com.google.common.util.concurrent.ListenableFuture │
│  found in modules guava-28.0-android.jar and                               │
│  listenablefuture-1.0.jar                                                  │
│                                                                             │
│  Причина:                                                                   │
│  • Две разные библиотеки содержат один и тот же класс                      │
│  • Обычно — конфликт transitive dependencies                               │
│                                                                             │
│  Решение:                                                                   │
│  configurations.all {                                                       │
│      resolutionStrategy {                                                  │
│          // Принудительно использовать guava                               │
│          force("com.google.guava:guava:31.1-android")                      │
│      }                                                                     │
│  }                                                                          │
│                                                                             │
│  Или исключить дубликат:                                                   │
│  implementation("com.example:library:1.0") {                               │
│      exclude(group = "com.google.guava", module = "listenablefuture")     │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2. Version Mismatch

```kotlin
// Ошибка: несовместимые версии Kotlin
// e.g., Library compiled with Kotlin 1.9, your project uses 1.8

// Решение 1: обновить Kotlin в проекте
// settings.gradle.kts
plugins {
    kotlin("jvm") version "1.9.21"
}

// Решение 2: force версию библиотеки
configurations.all {
    resolutionStrategy {
        eachDependency {
            if (requested.group == "org.jetbrains.kotlin") {
                useVersion("1.9.21")
            }
        }
    }
}
```

### 3. Could Not Resolve

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     COULD NOT RESOLVE DEPENDENCY                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Error: Could not resolve com.example:library:1.0.0                        │
│                                                                             │
│  Возможные причины:                                                        │
│  1. Библиотека не существует в указанных репозиториях                     │
│  2. Нет доступа к приватному репозиторию                                  │
│  3. Опечатка в координатах                                                │
│  4. Версия не существует                                                  │
│                                                                             │
│  Решения:                                                                   │
│  1. Добавить правильный репозиторий                                       │
│  2. Проверить credentials                                                  │
│  3. Проверить координаты на Maven Central / Google Maven                  │
│  4. Использовать --info для деталей:                                      │
│     ./gradlew build --info                                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4. Slow Dependency Resolution

```kotlin
// gradle.properties

// Включить parallel downloads
org.gradle.parallel=true

// Увеличить память
org.gradle.jvmargs=-Xmx4g -XX:MaxMetaspaceSize=1g

// Offline mode (если все dependencies cached)
org.gradle.offline=true

// Использовать configuration cache
org.gradle.configuration-cache=true
```

```kotlin
// settings.gradle.kts
// Фильтрация репозиториев ускоряет resolution
repositories {
    google {
        content {
            includeGroupByRegex("androidx\\..*")
            includeGroupByRegex("com\\.google\\..*")
        }
    }
    mavenCentral {
        content {
            excludeGroupByRegex("androidx\\..*")
        }
    }
}
```

---

## Anti-patterns и Best Practices

### Anti-patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANTI-PATTERNS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❌ Dynamic versions                                                        │
│     implementation("com.example:lib:+")                                    │
│     implementation("com.example:lib:1.+")                                  │
│     → Builds не reproducible                                               │
│     → Неожиданные breaking changes                                         │
│                                                                             │
│  ❌ SNAPSHOT dependencies в production                                      │
│     implementation("com.example:lib:1.0-SNAPSHOT")                         │
│     → Нестабильные версии                                                  │
│     → Могут измениться в любой момент                                     │
│                                                                             │
│  ❌ Все dependencies как api                                                │
│     api("com.example:internal-lib:1.0")                                    │
│     → Замедляет incremental builds                                         │
│     → Загрязняет classpath потребителей                                   │
│                                                                             │
│  ❌ Версии в каждом build.gradle                                            │
│     // module1: implementation("okhttp:4.10.0")                            │
│     // module2: implementation("okhttp:4.11.0")                            │
│     → Версия inconsistency                                                 │
│     → Сложно обновлять                                                     │
│                                                                             │
│  ❌ Игнорирование dependency warnings                                       │
│     → Могут стать errors в следующих версиях                              │
│                                                                             │
│  ❌ Использование jcenter()                                                 │
│     → Deprecated, закрыт в 2021                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BEST PRACTICES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ Используйте Version Catalogs                                           │
│     • Централизованное управление версиями                                │
│     • Type-safe accessors                                                  │
│     • Bundles для группировки                                              │
│                                                                             │
│  ✅ Используйте BOM где возможно                                           │
│     • Compose BOM, Firebase BOM                                            │
│     • Гарантированно совместимые версии                                   │
│                                                                             │
│  ✅ implementation вместо api (по умолчанию)                               │
│     • api только когда тип экспортируется                                 │
│     • Быстрее incremental builds                                          │
│                                                                             │
│  ✅ Регулярно обновляйте dependencies                                      │
│     • Renovate, Dependabot, Versions plugin                               │
│     • Security patches                                                     │
│                                                                             │
│  ✅ Проверяйте transitive dependencies                                     │
│     • ./gradlew dependencies                                               │
│     • ./gradlew dependencyInsight --dependency X                          │
│                                                                             │
│  ✅ Фильтруйте repositories                                                │
│     • content { includeGroup(...) }                                        │
│     • Быстрее resolution                                                   │
│                                                                             │
│  ✅ Lock dependency versions для CI                                        │
│     • ./gradlew dependencies --write-locks                                │
│     • Reproducible builds                                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Dependency Locking

### Зачем нужен locking

```kotlin
// build.gradle.kts
dependencyLocking {
    lockAllConfigurations()
}

// Создать lock файлы
// ./gradlew dependencies --write-locks

// gradle/dependency-locks/releaseRuntimeClasspath.lockfile
# This is a Gradle generated file
com.google.code.gson:gson:2.10.1=releaseRuntimeClasspath
com.squareup.okhttp3:okhttp:4.12.0=releaseRuntimeClasspath
com.squareup.retrofit2:retrofit:2.9.0=releaseRuntimeClasspath
...
```

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       DEPENDENCY LOCKING                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Без locking:                                                               │
│  • Transitive dependency может обновиться                                  │
│  • Build на CI ≠ build локально                                            │
│  • "Работает на моей машине"                                               │
│                                                                             │
│  С locking:                                                                 │
│  • Все версии зафиксированы в файле                                       │
│  • Reproducible builds                                                     │
│  • Обновление требует явного --write-locks                                │
│                                                                             │
│  Lock файлы коммитятся в git!                                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Проверь себя

### Вопросы для самопроверки

1. **В чём разница между implementation и api?**
   - implementation: не видна потребителям, рекомендуется по умолчанию
   - api: видна потребителям (transitive), замедляет builds

2. **Что такое BOM и зачем он нужен?**
   - Bill of Materials — спецификация совместимых версий
   - Одна версия BOM определяет версии всех библиотек группы
   - Гарантирует совместимость

3. **Как Gradle разрешает конфликты версий?**
   - По умолчанию: highest version wins
   - Можно настроить: force(), failOnVersionConflict()

4. **Что такое Version Catalog?**
   - Централизованное управление версиями в libs.versions.toml
   - Type-safe accessors (libs.retrofit)
   - Bundles для группировки

5. **Чем AAR отличается от JAR?**
   - AAR: Android-specific, включает ресурсы, manifest, ProGuard rules
   - JAR: только Java bytecode

6. **Как исключить transitive dependency?**
   - implementation("lib") { exclude(group = "...", module = "...") }
   - Глобально: configurations.all { exclude(...) }

7. **Зачем нужен dependency locking?**
   - Reproducible builds
   - Одинаковые версии на CI и локально
   - Защита от неожиданных изменений transitive dependencies

---

## Связи

- **[[android-gradle-fundamentals]]** — базовые концепции Gradle
- **[[android-project-structure]]** — организация модулей и dependencies
- **[[android-build-evolution]]** — эволюция систем управления зависимостями

---

## Источники

| # | Источник | Тип | Описание |
|---|----------|-----|----------|
| 1 | [Gradle Dependency Management](https://docs.gradle.org/current/userguide/dependency_management.html) | Docs | Официальная документация Gradle |
| 2 | [Android Dependencies Documentation](https://developer.android.com/studio/build/dependencies) | Docs | Android developer guide по зависимостям |
| 3 | [Version Catalogs](https://docs.gradle.org/current/userguide/platforms.html) | Docs | Gradle platforms и version catalogs |
| 4 | [Compose BOM](https://developer.android.com/jetpack/compose/bom) | Docs | Compose Bill of Materials |
| 5 | [Maven Central Repository](https://search.maven.org/) | Tool | Поиск библиотек |
| 6 | [Google Maven Repository](https://maven.google.com/web/index.html) | Tool | AndroidX и Google библиотеки |
| 7 | [Renovate Bot](https://docs.renovatebot.com/) | Docs | Автоматическое обновление зависимостей |
| 8 | [Dependabot](https://docs.github.com/en/code-security/dependabot) | Docs | GitHub Dependabot |
| 9 | [AndroidWeekly — Gradle & Dependencies](https://androidweekly.net/) | Blog | Актуальные статьи о зависимостях |
| 10 | [Jake Wharton's Blog](https://jakewharton.com/) | Blog | Практики от автора Retrofit/OkHttp |

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
