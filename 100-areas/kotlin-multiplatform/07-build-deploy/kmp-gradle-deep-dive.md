---
title: "KMP Gradle Deep Dive"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, gradle, build, optimization, convention-plugins]
related: [[kmp-project-structure]], [[kmp-ci-cd]], [[kmp-publishing]]
cs-foundations: [build-systems, caching, directed-acyclic-graph, incremental-computation]
---

# KMP Gradle Deep Dive

> **TL;DR:** KMP Gradle оптимизация: включи `org.gradle.caching=true`, `org.gradle.parallel=true`, `org.gradle.configuration-cache=true` в gradle.properties. Используй Version Catalog (libs.versions.toml) и Convention Plugins для multi-module. Kotlin/Native: используй `linkDebug*` вместо `build`, сохраняй ~/.konan между билдами. Новый `com.android.kotlin.multiplatform.library` plugin заменит `com.android.library` в AGP 10.0 (2026). KSP вместо KAPT для скорости.

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Gradle basics | Понимать tasks, plugins | Gradle docs |
| Kotlin DSL | build.gradle.kts синтаксис | Gradle Kotlin DSL Primer |
| KMP Project Structure | Понимать source sets | [[kmp-project-structure]] |
| Multi-module Android | Опыт с модульными проектами | Android docs |
| **CS: DAG и инкрементальные вычисления** | Почему Gradle быстрый | [[cs-dag-incremental]] |

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| Build Cache | Кэш результатов задач | Заметки с прошлых совещаний — не пересчитываем |
| Configuration Cache | Кэш конфигурации билда | Готовый план проекта — не планируем заново |
| Convention Plugin | Переиспользуемая логика билда | Шаблон документа для всех отделов |
| Version Catalog | Централизованное управление версиями | Единый список поставщиков для всех офисов |
| Composite Build | Включенный под-билд | Субподрядчик внутри проекта |
| Precompiled Script Plugin | Плагин из .gradle.kts файла | Макрос в Excel |

## Почему Gradle — DAG и кэширование?

**Gradle как DAG (Directed Acyclic Graph):** Tasks связаны зависимостями без циклов. Это позволяет параллельное выполнение независимых веток и инкрементальную пересборку только изменившихся узлов.

**Три уровня кэширования:** (1) **Configuration cache** — кэш результата парсинга build.gradle.kts, (2) **Task output cache** — кэш результатов выполнения задач по хэшу входов, (3) **Build cache** — shared cache между машинами (remote).

**KMP специфика:** Kotlin/Native компилирует в machine code, что **10x дольше** JVM. Решение: `linkDebug*` вместо `linkRelease*` + кэширование ~/.konan.

**KSP vs KAPT:** KAPT генерирует Java stubs → потом обрабатывает → **2x медленнее**. KSP работает напрямую с Kotlin symbols.

## Структура KMP Gradle проекта

```
my-kmp-project/
├── gradle/
│   ├── wrapper/
│   │   └── gradle-wrapper.properties
│   └── libs.versions.toml              # Version Catalog
├── build-logic/                         # Convention Plugins
│   ├── settings.gradle.kts
│   ├── build.gradle.kts
│   └── src/main/kotlin/
│       ├── kmp.library.gradle.kts
│       └── kmp.application.gradle.kts
├── shared/                              # Shared KMP module
│   ├── build.gradle.kts
│   └── src/
├── androidApp/
│   └── build.gradle.kts
├── iosApp/
├── settings.gradle.kts
├── build.gradle.kts
└── gradle.properties                    # Build optimization
```

## gradle.properties: Оптимизация

```properties
# ==========================
# GRADLE CORE OPTIMIZATION
# ==========================

# Parallel task execution
org.gradle.parallel=true

# Maximum workers (default: number of CPU cores)
org.gradle.workers.max=8

# Daemon (default: true, keep enabled)
org.gradle.daemon=true

# JVM heap size for Gradle
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC -XX:MaxMetaspaceSize=512m

# Build cache (local)
org.gradle.caching=true

# Configuration cache (experimental, но стабилен в 8.x)
org.gradle.configuration-cache=true

# ==========================
# KOTLIN OPTIMIZATION
# ==========================

# Kotlin incremental compilation
kotlin.incremental=true

# Kotlin/Native incremental (Experimental)
kotlin.incremental.native=true

# K2 compiler (Kotlin 2.0+)
kotlin.experimental.tryK2=true

# ==========================
# KMP SPECIFIC
# ==========================

# Share cinterop klibs between targets
kotlin.mpp.enableCInteropCommonization=true

# Skip unused dependency metadata
kotlin.mpp.enableIntransitiveMetadataConfiguration=true

# Hierarchical source sets (default true in Kotlin 2.x)
kotlin.mpp.enableHierarchicalSourceSetsModel=true

# Stability warnings
kotlin.mpp.stability.nowarn=true

# ==========================
# KOTLIN/NATIVE
# ==========================

# Native cache kind: static (faster rebuilds) or none
kotlin.native.cacheKind=static

# Binary distribution (prevents re-download)
kotlin.native.distribution.downloadFromMaven=true

# ==========================
# ANDROID (if applicable)
# ==========================

# Non-transitive R classes (faster builds)
android.nonTransitiveRClass=true

# Use AndroidX
android.useAndroidX=true

# Enable Jetifier only if needed
android.enableJetifier=false

# ==========================
# KSP (Kotlin Symbol Processing)
# ==========================

# Incremental KSP
ksp.incremental=true

# KSP for all KMP targets
ksp.useKSP2=true
```

## Version Catalog: libs.versions.toml

```toml
# gradle/libs.versions.toml

[versions]
kotlin = "2.1.21"
agp = "8.8.0"
compose-multiplatform = "1.8.0"

# KMP Libraries
ktor = "3.1.0"
sqldelight = "2.2.1"
koin = "4.1.0"
kotlinxCoroutines = "1.10.2"
kotlinxSerialization = "1.8.1"
kotlinxDatetime = "0.7.1"

# Testing
kotest = "5.9.1"
turbine = "1.2.0"

[libraries]
# Kotlin
kotlin-stdlib = { module = "org.jetbrains.kotlin:kotlin-stdlib", version.ref = "kotlin" }
kotlin-test = { module = "org.jetbrains.kotlin:kotlin-test", version.ref = "kotlin" }

# Coroutines
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "kotlinxCoroutines" }
kotlinx-coroutines-test = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-test", version.ref = "kotlinxCoroutines" }

# Serialization
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "kotlinxSerialization" }

# Ktor Client
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-okhttp = { module = "io.ktor:ktor-client-okhttp", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }
ktor-client-content-negotiation = { module = "io.ktor:ktor-client-content-negotiation", version.ref = "ktor" }
ktor-serialization-json = { module = "io.ktor:ktor-serialization-kotlinx-json", version.ref = "ktor" }
ktor-client-mock = { module = "io.ktor:ktor-client-mock", version.ref = "ktor" }

# SQLDelight
sqldelight-runtime = { module = "app.cash.sqldelight:runtime", version.ref = "sqldelight" }
sqldelight-coroutines = { module = "app.cash.sqldelight:coroutines-extensions", version.ref = "sqldelight" }
sqldelight-android-driver = { module = "app.cash.sqldelight:android-driver", version.ref = "sqldelight" }
sqldelight-native-driver = { module = "app.cash.sqldelight:native-driver", version.ref = "sqldelight" }
sqldelight-sqlite-driver = { module = "app.cash.sqldelight:sqlite-driver", version.ref = "sqldelight" }

# Koin
koin-core = { module = "io.insert-koin:koin-core", version.ref = "koin" }
koin-android = { module = "io.insert-koin:koin-android", version.ref = "koin" }
koin-compose = { module = "io.insert-koin:koin-compose", version.ref = "koin" }
koin-test = { module = "io.insert-koin:koin-test", version.ref = "koin" }

# Testing
kotest-assertions = { module = "io.kotest:kotest-assertions-core", version.ref = "kotest" }
turbine = { module = "app.cash.turbine:turbine", version.ref = "turbine" }

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
kotlin-serialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
compose-multiplatform = { id = "org.jetbrains.compose", version.ref = "compose-multiplatform" }
android-library = { id = "com.android.library", version.ref = "agp" }
android-application = { id = "com.android.application", version.ref = "agp" }
sqldelight = { id = "app.cash.sqldelight", version.ref = "sqldelight" }
ksp = { id = "com.google.devtools.ksp", version = "2.1.21-1.0.31" }

[bundles]
ktor-common = ["ktor-client-core", "ktor-client-content-negotiation", "ktor-serialization-json"]
sqldelight-common = ["sqldelight-runtime", "sqldelight-coroutines"]
testing-common = ["kotlin-test", "kotlinx-coroutines-test", "kotest-assertions", "turbine"]
```

## Использование Version Catalog

```kotlin
// shared/build.gradle.kts
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.kotlin.serialization)
    alias(libs.plugins.sqldelight)
}

kotlin {
    androidTarget()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation(libs.bundles.ktor.common)
            implementation(libs.bundles.sqldelight.common)
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.kotlinx.serialization.json)
            implementation(libs.koin.core)
        }

        commonTest.dependencies {
            implementation(libs.bundles.testing.common)
            implementation(libs.ktor.client.mock)
        }

        androidMain.dependencies {
            implementation(libs.ktor.client.okhttp)
            implementation(libs.sqldelight.android.driver)
        }

        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
            implementation(libs.sqldelight.native.driver)
        }
    }
}
```

## Convention Plugins

### Структура build-logic

```
build-logic/
├── settings.gradle.kts
├── build.gradle.kts
└── src/main/kotlin/
    ├── kmp.library.gradle.kts
    ├── kmp.compose.gradle.kts
    └── android.library.gradle.kts
```

### build-logic/settings.gradle.kts

```kotlin
// build-logic/settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }

    versionCatalogs {
        create("libs") {
            from(files("../gradle/libs.versions.toml"))
        }
    }
}

rootProject.name = "build-logic"
```

### build-logic/build.gradle.kts

```kotlin
// build-logic/build.gradle.kts
plugins {
    `kotlin-dsl`
}

dependencies {
    // Plugins as dependencies для precompiled script plugins
    implementation(libs.plugins.kotlin.multiplatform.get().toString())
    implementation(libs.plugins.kotlin.serialization.get().toString())
    implementation(libs.plugins.compose.multiplatform.get().toString())
    implementation(libs.plugins.android.library.get().toString())
    implementation(libs.plugins.sqldelight.get().toString())
}

// Helper extension для доступа к Version Catalog
fun Provider<PluginDependency>.get(): String =
    this.get().run { "${pluginId}:${pluginId}.gradle.plugin:${version}" }
```

### Convention Plugin: KMP Library

```kotlin
// build-logic/src/main/kotlin/kmp.library.gradle.kts
import org.jetbrains.kotlin.gradle.dsl.KotlinMultiplatformExtension

plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("org.jetbrains.kotlin.plugin.serialization")
}

kotlin {
    // Android target
    androidTarget {
        compilations.all {
            compileTaskProvider.configure {
                compilerOptions {
                    jvmTarget.set(org.jetbrains.kotlin.gradle.dsl.JvmTarget.JVM_17)
                }
            }
        }
    }

    // iOS targets
    listOf(
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = project.name
            isStatic = true
        }
    }

    // JVM target (опционально)
    jvm()

    // Source sets hierarchy
    sourceSets {
        commonMain.dependencies {
            implementation(libs.findLibrary("kotlinx-coroutines-core").get())
            implementation(libs.findLibrary("kotlinx-serialization-json").get())
        }

        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation(libs.findLibrary("kotlinx-coroutines-test").get())
        }
    }
}

// Доступ к version catalog
val libs: VersionCatalog = extensions.getByType<VersionCatalogsExtension>().named("libs")
```

### Convention Plugin: Android Library

```kotlin
// build-logic/src/main/kotlin/android.library.gradle.kts
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    compileSdk = 35

    defaultConfig {
        minSdk = 24
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}
```

### Использование Convention Plugin

```kotlin
// shared/build.gradle.kts
plugins {
    id("kmp.library")  // Наш convention plugin
}

// Дополнительная конфигурация если нужно
kotlin {
    sourceSets {
        commonMain.dependencies {
            // Специфичные для модуля зависимости
            implementation(libs.koin.core)
        }
    }
}
```

### Root settings.gradle.kts

```kotlin
// settings.gradle.kts
pluginManagement {
    includeBuild("build-logic")

    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyKMPProject"
include(":shared")
include(":shared:core")
include(":shared:feature-auth")
include(":androidApp")
```

## Новый Android-KMP Plugin (2025+)

### Миграция с com.android.library

```kotlin
// ДО: com.android.library (deprecated для KMP в AGP 10.0)
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.multiplatform")
}

android {
    namespace = "com.example.shared"
    compileSdk = 35
    // ... много конфигурации
}

kotlin {
    androidTarget()
    // ...
}

// ПОСЛЕ: com.android.kotlin.multiplatform.library
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
}

kotlin {
    androidLibrary {
        namespace = "com.example.shared"
        compileSdk = 35
        minSdk = 24
    }

    iosArm64()
    iosSimulatorArm64()
}
```

### Преимущества нового плагина

| Аспект | com.android.library | android.kotlin.multiplatform.library |
|--------|---------------------|--------------------------------------|
| Build Performance | Базовая | Оптимизирована для KMP |
| Configuration | Отдельный android {} блок | Внутри kotlin {} |
| Build Variants | Полная поддержка | Упрощено (no variants) |
| Deprecation | AGP 9.0 (Q4 2025) | Long-term support |

## Kotlin/Native Оптимизация

### Debug vs Release

```bash
# ❌ МЕДЛЕННО: Release build во время разработки
./gradlew assembleXCFramework

# ✅ БЫСТРО: Debug build для разработки
./gradlew assembleSharedDebugXCFramework

# ❌ МЕДЛЕННО: Все targets
./gradlew linkReleaseFrameworkIosArm64 linkReleaseFrameworkIosSimulatorArm64

# ✅ БЫСТРО: Только нужный target
./gradlew linkDebugFrameworkIosSimulatorArm64
```

### Сохранение ~/.konan в CI

```yaml
# GitHub Actions
- name: Cache Kotlin/Native
  uses: actions/cache@v4
  with:
    path: |
      ~/.konan
    key: konan-${{ runner.os }}-${{ hashFiles('**/*.gradle.kts') }}
    restore-keys: |
      konan-${{ runner.os }}-
```

### Gradle Tasks для Kotlin/Native

```bash
# Показать все native tasks
./gradlew tasks --group="build" | grep -i native

# Только iOS Simulator (ARM64 для M1+)
./gradlew :shared:linkDebugFrameworkIosSimulatorArm64

# Только iOS Device
./gradlew :shared:linkDebugFrameworkIosArm64

# Показать зависимости
./gradlew :shared:dependencies --configuration=iosArm64MainImplementation
```

## Multi-Module Dependencies

### Общая структура

```
shared/
├── core/
│   └── build.gradle.kts
├── data/
│   └── build.gradle.kts
├── domain/
│   └── build.gradle.kts
└── feature-auth/
    └── build.gradle.kts
```

### Зависимости между модулями

```kotlin
// shared/feature-auth/build.gradle.kts
plugins {
    id("kmp.library")
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            // Зависимость на другие KMP модули
            implementation(project(":shared:core"))
            implementation(project(":shared:domain"))

            // Если используете Type-safe project accessors:
            // implementation(projects.shared.core)
        }
    }
}
```

### Type-safe Project Accessors

```kotlin
// settings.gradle.kts
enableFeaturePreview("TYPESAFE_PROJECT_ACCESSORS")
```

```kotlin
// shared/feature-auth/build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(projects.shared.core)
            implementation(projects.shared.domain)
        }
    }
}
```

## KSP vs KAPT

```kotlin
// ❌ KAPT (медленнее, генерирует Java stubs)
plugins {
    kotlin("kapt")
}

dependencies {
    kapt("com.some:processor:1.0")
}

// ✅ KSP (быстрее, native Kotlin support)
plugins {
    id("com.google.devtools.ksp")
}

dependencies {
    // Для всех targets
    ksp("com.some:processor:1.0")

    // Для конкретного target
    add("kspAndroid", "com.some:processor:1.0")
    add("kspIosArm64", "com.some:processor:1.0")
}
```

## Build Reports

### Включение build reports

```properties
# gradle.properties
kotlin.build.report.output=file,build_scan
kotlin.build.report.file.output_dir=build/reports/kotlin-build
```

### Анализ build performance

```bash
# Профилирование билда
./gradlew build --profile

# Build scan (требует Gradle Enterprise)
./gradlew build --scan

# Dry run (проверка без выполнения)
./gradlew build --dry-run
```

## Troubleshooting

| Проблема | Причина | Решение |
|----------|---------|---------|
| Slow first build | ~/.konan not cached | Cache в CI, сохранять между билдами |
| Configuration cache failure | Plugin incompatibility | Disable для несовместимых plugins |
| Out of memory | Недостаточно heap | `-Xmx4g` в gradle.properties |
| Native build 20+ min | Release вместо Debug | Использовать linkDebug* tasks |
| Version catalog not found | Неправильный путь | Проверить from(files()) в build-logic |
| Plugin not found in convention | Classpath issue | Добавить plugin как dependency |

## Best Practices Checklist

| Practice | Why | How |
|----------|-----|-----|
| Version Catalog | Централизация версий | libs.versions.toml |
| Convention Plugins | DRY, consistency | build-logic/ folder |
| Parallel builds | Faster builds | org.gradle.parallel=true |
| Build cache | Reuse artifacts | org.gradle.caching=true |
| Configuration cache | Skip config phase | org.gradle.configuration-cache=true |
| Debug builds | Fast iteration | linkDebug* tasks |
| KSP over KAPT | Faster annotation processing | Migrate to KSP |
| Cache ~/.konan | Skip downloads | CI caching |
| New Android-KMP plugin | Future-proof | Migrate before AGP 10.0 |

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "buildSrc медленный" | Исправлено в Gradle 8+, теперь treated as included build |
| "Configuration cache всё ломает" | Большинство modern plugins совместимы |
| "Kotlin/Native всегда медленный" | linkDebug* + ~/.konan cache → билды за минуты |
| "KSP только для JVM" | KSP 2 поддерживает все KMP targets |
| "Version Catalog избыточен для маленьких проектов" | Даже для 2-3 модулей упрощает поддержку |

## CS-фундамент

| Концепция | Применение в Gradle |
|-----------|---------------------|
| DAG (Directed Acyclic Graph) | Task dependencies graph |
| Incremental computation | Up-to-date check по хэшам входов |
| Memoization | Build cache (local + remote) |
| Topological sort | Порядок выполнения tasks |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Gradle Best Practices](https://kotlinlang.org/docs/gradle-best-practices.html) | Official | Kotlin Gradle оптимизация |
| [Native Compilation Time](https://kotlinlang.org/docs/native-improving-compilation-time.html) | Official | Kotlin/Native ускорение |
| [Convention Plugins](https://docs.gradle.org/current/userguide/implementing_gradle_plugins_convention.html) | Official | Gradle convention plugins |
| [Android-KMP Plugin](https://developer.android.com/kotlin/multiplatform/plugin) | Official | Новый Android plugin |
| [KMP Configuration Plugin](https://github.com/05nelsonm/gradle-kmp-configuration-plugin) | GitHub | Готовый KMP plugin |
| [Multi-module KMP](https://proandroiddev.com/effortless-multimodule-configuration-for-kotlin-multiplatform-projects-with-gradle-convention-8e6593dff1d9) | Blog | Convention plugins для KMP |

---
*Проверено: 2026-01-09 | Gradle 8.12, Kotlin 2.1.21, AGP 8.8.0*
