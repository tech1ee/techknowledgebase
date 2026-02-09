---
title: "KMP Project Structure: Анатомия мультиплатформенного проекта"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, multiplatform, project-structure, gradle, source-sets]
related:
  - "[[kmp-getting-started]]"
  - "[[kmp-source-sets]]"
  - "[[kmp-expect-actual]]"
cs-foundations:
  - "[[build-systems-theory]]"
  - "[[compilation-pipeline]]"
  - "[[dependency-resolution]]"
  - "[[module-systems]]"
---

# KMP Project Structure: как устроен мультиплатформенный проект

> **TL;DR:** KMP проект = targets (платформы) + source sets (папки с кодом) + Gradle конфигурация. `commonMain` — код для всех платформ, `<platform>Main` — платформо-специфичный. Default hierarchy template автоматически создаёт intermediate source sets (appleMain, nativeMain). Для multi-module используйте Convention Plugins. Kotlin компилятор из одного кода создаёт бинарники для каждой платформы.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **KMP Getting Started** | Базовое понимание KMP и создание проекта | [[kmp-getting-started]] |
| **Gradle basics** | Понимание build.gradle.kts синтаксиса | Gradle docs |
| **Kotlin basics** | Синтаксис языка, packages | [[kotlin-overview]] |
| **Build systems** | DAG, tasks, кэширование | [[build-systems-theory]] |
| **Module systems** | Модульность, инкапсуляция, интерфейсы | [[module-systems]] |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|----------|---------------------|
| **Target** | Целевая платформа компиляции (jvm, ios, js) | **Пункт назначения** — куда летит самолёт |
| **Source Set** | Набор исходных файлов с общими настройками | **Чемодан** — вещи для конкретной поездки |
| **commonMain** | Source set для кода всех платформ | **Универсальная аптечка** — нужна везде |
| **platformMain** | Source set для одной платформы (iosMain, jvmMain) | **Адаптер для розетки** — только для конкретной страны |
| **Intermediate Source Set** | Shared между subset'ом платформ | **Европейский адаптер** — для Франции, Германии, но не для США |
| **Hierarchy Template** | Автогенерация intermediate source sets | **Автопилот** — сам создаёт нужную структуру |
| **Convention Plugin** | Gradle плагин с общими настройками | **Корпоративный стандарт** — одинаковые правила для всех модулей |
| **Umbrella Module** | Модуль, объединяющий все shared модули для iOS | **Зонтик** — собирает всё под одну крышу для iOS |
| **Kotlin DSL** | Gradle скрипты на Kotlin (.kts) | **Рецепт на понятном языке** — вместо Groovy |
| **Version Catalog** | Централизованное управление версиями (libs.versions.toml) | **Прайс-лист** — все цены (версии) в одном месте |

---

## Почему структура KMP проекта такая

### Проблема, которую решает структура

При кросс-платформенной разработке возникает **фундаментальная дилемма**:

```
Дилемма code sharing:
─────────────────────

Вариант A: Дублирование           Вариант B: Общий код
─────────────────────             ─────────────────────
android/User.kt                   shared/User.kt
ios/User.swift                          │
server/User.java                        └─► компилируется для
                                            всех платформ
Проблемы:                         Проблемы:
- N реализаций                    - Разные API на платформах
- N наборов тестов                - Разные зависимости
- Рассинхронизация                - Как вызвать platform code?
```

### Как KMP решает эту дилемму

**Source Set Hierarchy** — решение через **иерархию и зависимости**:

```
                    ┌─────────────┐
                    │ commonMain  │  ← Pure Kotlin, никаких platform APIs
                    │             │     Доступен везде
                    └──────┬──────┘
                           │ dependsOn
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │ nativeMain  │ │  jvmMain    │ │   jsMain    │
    │             │ │             │ │             │
    │ Native APIs │ │ JVM APIs    │ │ JS APIs     │
    └──────┬──────┘ └──────┬──────┘ └─────────────┘
           │               │
    ┌──────▼──────┐ ┌──────▼──────┐
    │  iosMain    │ │ androidMain │
    │             │ │             │
    │ UIKit, etc  │ │ Android SDK │
    └─────────────┘ └─────────────┘
```

**Ключевой insight:** `dependsOn` — это **направление видимости**:
- Нижний level видит верхний (iosMain видит commonMain)
- Верхний level НЕ видит нижний (commonMain не видит iosMain)

Это соответствует принципу **Dependency Inversion** из [[module-systems]].

### Почему именно Gradle

Gradle выбран потому что:

1. **DAG (Directed Acyclic Graph)** — идеален для multi-target компиляции:
   ```
   :shared:compileCommonMainKotlin
          │
          ├─► :shared:compileAndroidMainKotlin
          ├─► :shared:compileIosMainKotlin
          └─► :shared:compileJsMainKotlin
   ```

2. **Incremental builds** — перекомпилируется только изменённое:
   ```
   Изменили commonMain/Utils.kt
         │
         └─► Перекомпиляция: commonMain + все зависящие source sets
             Но НЕ перекомпиляция: независимых модулей
   ```

3. **Task avoidance** — Gradle пропускает up-to-date tasks:
   ```bash
   # Второй запуск без изменений
   ./gradlew build
   # BUILD SUCCESSFUL (0 tasks executed, 45 up-to-date)
   ```

> **CS-фундамент:** Детали в [[build-systems-theory]] (DAG, task graph) и [[module-systems]] (cohesion, coupling).

---

## Анатомия KMP проекта

### Базовая структура

```
MyKmpApp/
├── build.gradle.kts              # Root build file
├── settings.gradle.kts           # Включает все модули
├── gradle.properties             # Глобальные настройки
├── gradle/
│   └── libs.versions.toml        # Version catalog
│
├── shared/                        # 📦 SHARED MODULE
│   ├── build.gradle.kts          # KMP конфигурация
│   └── src/
│       ├── commonMain/           # Код для ВСЕХ платформ
│       │   └── kotlin/
│       │       ├── models/       # Data classes, interfaces
│       │       ├── repository/   # Repository interfaces
│       │       └── utils/        # Utilities
│       ├── commonTest/           # Тесты для common кода
│       │   └── kotlin/
│       ├── androidMain/          # Android-специфичный код
│       │   └── kotlin/
│       ├── androidUnitTest/
│       ├── iosMain/              # iOS-специфичный код
│       │   └── kotlin/
│       ├── iosTest/
│       ├── jvmMain/              # JVM/Desktop код
│       └── jsMain/               # JavaScript код
│
├── composeApp/                    # 📱 Android app (или androidApp/)
│   ├── build.gradle.kts
│   └── src/
│       └── main/
│           ├── kotlin/
│           └── res/
│
└── iosApp/                        # 🍎 iOS app (Xcode project)
    ├── iosApp.xcodeproj
    └── iosApp/
        ├── ContentView.swift
        └── Info.plist
```

### Визуализация связей

```
┌─────────────────────────────────────────────────────────────┐
│                        settings.gradle.kts                   │
│   include(":shared", ":composeApp", ":iosApp")              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐      ┌──────────────┐
│   :shared    │     │ :composeApp  │      │   :iosApp    │
│              │     │              │      │              │
│ KMP модуль   │◄────│ depends on   │      │ Xcode project│
│ с общим кодом│     │ :shared      │      │ imports      │
│              │     │              │      │ Shared.xcf   │
└──────────────┘     └──────────────┘      └──────────────┘
```

---

## Targets: целевые платформы

### Объявление targets в build.gradle.kts

```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform") version "2.1.21"
}

kotlin {
    // ═══════════════════════════════════════════════════
    // TARGETS — куда компилируем
    // ═══════════════════════════════════════════════════

    // Android
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }

    // iOS — все архитектуры
    iosX64()           // Intel Simulator
    iosArm64()         // Реальные устройства
    iosSimulatorArm64() // Apple Silicon Simulator

    // Desktop (JVM)
    jvm("desktop")

    // Web
    js(IR) {
        browser()
    }

    // ═══════════════════════════════════════════════════
    // SOURCE SETS — откуда берём код
    // ═══════════════════════════════════════════════════

    sourceSets {
        val commonMain by getting {
            dependencies {
                // Зависимости для всех платформ
            }
        }

        val androidMain by getting {
            dependencies {
                // Android-специфичные зависимости
            }
        }

        val iosMain by creating {
            dependsOn(commonMain)
        }
        // ...
    }
}
```

### Доступные targets

| Target | Функция | Платформа |
|--------|---------|-----------|
| `androidTarget()` | Android | JVM (Android SDK) |
| `jvm()` | Desktop/Server | JVM |
| `iosX64()` | iOS Simulator (Intel) | Native |
| `iosArm64()` | iOS Device | Native |
| `iosSimulatorArm64()` | iOS Simulator (Apple Silicon) | Native |
| `macosX64()` | macOS (Intel) | Native |
| `macosArm64()` | macOS (Apple Silicon) | Native |
| `js(IR)` | JavaScript | JS/Browser |
| `wasmJs()` | WebAssembly | Wasm |
| `linuxX64()` | Linux | Native |
| `mingwX64()` | Windows | Native |

---

## Source Sets: наборы исходников

### Что такое Source Set

```
┌─────────────────────────────────────────────────────────────┐
│                      SOURCE SET                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Уникальное имя (commonMain, iosMain, jvmMain)          │
│  2. Свои targets (на какие платформы компилируется)        │
│  3. Свои dependencies (какие библиотеки использует)        │
│  4. Свои compiler options (настройки компилятора)          │
│  5. Расположение в src/ директории                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Стандартные Source Sets

```
src/
├── commonMain/        # Код для ВСЕХ targets
│   └── kotlin/
│       └── Platform.kt
│
├── commonTest/        # Тесты для common кода
│   └── kotlin/
│       └── PlatformTest.kt
│
├── androidMain/       # Только для Android
│   └── kotlin/
│       └── Platform.android.kt
│
├── iosMain/           # Только для iOS (все архитектуры)
│   └── kotlin/
│       └── Platform.ios.kt
│
├── jvmMain/           # Только для JVM/Desktop
│   └── kotlin/
│       └── Platform.jvm.kt
│
└── jsMain/            # Только для JavaScript
    └── kotlin/
        └── Platform.js.kt
```

### Правила видимости

```
┌─────────────────────────────────────────────────────────────┐
│                     ПРАВИЛА ВИДИМОСТИ                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Platform-specific код ВИДИТ common код                  │
│     iosMain → может использовать классы из commonMain      │
│                                                             │
│  ❌ Common код НЕ ВИДИТ platform-specific код               │
│     commonMain → НЕ может импортировать из iosMain         │
│                                                             │
│  ✅ Platform source sets могут использовать platform APIs   │
│     jvmMain → может использовать java.io.File              │
│     iosMain → может использовать platform.UIKit            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Hierarchical Structure: иерархия source sets

### Default Hierarchy Template

Kotlin Gradle Plugin автоматически создаёт intermediate source sets:

```kotlin
kotlin {
    androidTarget()
    iosArm64()
    iosSimulatorArm64()
}
// Plugin автоматически создаст:
// - iosMain (shared между iosArm64 и iosSimulatorArm64)
// - appleMain (если добавить macOS targets)
// - nativeMain (для всех Native targets)
```

### Визуализация иерархии

```
                        commonMain
                            │
            ┌───────────────┼───────────────┐
            │               │               │
        nativeMain       jvmMain         jsMain
            │               │               │
    ┌───────┴───────┐       │               │
    │               │       │               │
 appleMain      linuxMain   │               │
    │               │       │               │
 ┌──┴───┐          │       │               │
 │      │          │       │               │
iosMain macosMain  │    androidMain        │
 │ │        │      │       │               │
 │ │        │      │       │               │
iosArm64  macosArm64  linuxX64  androidTarget  js(IR)
iosX64    macosX64
iosSimulatorArm64
```

### Использование intermediate source sets

```kotlin
// appleMain/kotlin/AppleUtils.kt
// Этот код доступен на iOS и macOS, но НЕ на Android/JVM

import platform.Foundation.NSUUID

fun generateAppleUUID(): String {
    return NSUUID().UUIDString()
}

// Использование в iosMain
// iosMain/kotlin/SomeClass.kt
fun doSomething() {
    val uuid = generateAppleUUID() // ✅ Работает
}
```

### Кастомные intermediate source sets

```kotlin
kotlin {
    jvm()
    macosArm64()
    iosArm64()
    iosSimulatorArm64()

    applyDefaultHierarchyTemplate()

    sourceSets {
        // Создаём кастомный intermediate source set
        val jvmAndMacos by creating {
            dependsOn(commonMain.get())
        }
        macosArm64Main.get().dependsOn(jvmAndMacos)
        jvmMain.get().dependsOn(jvmAndMacos)
    }
}
```

---

## Gradle конфигурация

### Root build.gradle.kts

```kotlin
// build.gradle.kts (root)
plugins {
    // Объявляем плагины, но не применяем
    alias(libs.plugins.kotlinMultiplatform) apply false
    alias(libs.plugins.androidApplication) apply false
    alias(libs.plugins.androidLibrary) apply false
    alias(libs.plugins.composeMultiplatform) apply false
    alias(libs.plugins.composeCompiler) apply false
}
```

### Version Catalog (libs.versions.toml)

```toml
# gradle/libs.versions.toml
[versions]
kotlin = "2.1.21"
agp = "8.8.0"
compose-multiplatform = "1.7.3"
ktor = "3.0.3"
coroutines = "1.9.0"
sqldelight = "2.0.2"

[libraries]
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "coroutines" }
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
ktor-client-android = { module = "io.ktor:ktor-client-android", version.ref = "ktor" }
ktor-client-darwin = { module = "io.ktor:ktor-client-darwin", version.ref = "ktor" }

[plugins]
kotlinMultiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
androidApplication = { id = "com.android.application", version.ref = "agp" }
androidLibrary = { id = "com.android.library", version.ref = "agp" }
composeMultiplatform = { id = "org.jetbrains.compose", version.ref = "compose-multiplatform" }
composeCompiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

### Shared module build.gradle.kts

```kotlin
// shared/build.gradle.kts
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.androidLibrary)
    kotlin("plugin.serialization") version libs.versions.kotlin
}

kotlin {
    androidTarget {
        compilations.all {
            kotlinOptions {
                jvmTarget = "17"
            }
        }
    }

    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "Shared"
            isStatic = true
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
            implementation(libs.ktor.client.core)
        }

        androidMain.dependencies {
            implementation(libs.ktor.client.android)
        }

        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }
    }
}

android {
    namespace = "com.example.shared"
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

---

## Multi-Module Architecture

### Когда нужен multi-module

```
┌─────────────────────────────────────────────────────────────┐
│              КОГДА ПЕРЕХОДИТЬ НА MULTI-MODULE                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Shared модуль > 50 файлов                               │
│  ✅ Разные команды работают над разными features            │
│  ✅ Нужна изоляция для тестирования                         │
│  ✅ Разные features имеют разные зависимости                │
│  ✅ Хотите incremental builds                               │
│                                                             │
│  ❌ Маленький проект (< 30 файлов)                          │
│  ❌ Один разработчик                                        │
│  ❌ Прототип/MVP                                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Структура multi-module проекта

```
project/
├── build-logic/                   # Convention plugins
│   ├── convention/
│   │   ├── build.gradle.kts
│   │   └── src/main/kotlin/
│   │       ├── KmpLibraryConventionPlugin.kt
│   │       └── AndroidLibraryConventionPlugin.kt
│   └── settings.gradle.kts
│
├── core/
│   ├── common/                    # Базовые утилиты
│   ├── network/                   # Ktor client
│   ├── database/                  # SQLDelight
│   └── ui/                        # Shared UI components
│
├── feature/
│   ├── auth/                      # Auth feature
│   ├── home/                      # Home feature
│   └── profile/                   # Profile feature
│
├── shared/                        # Umbrella module для iOS
│   └── build.gradle.kts
│
├── androidApp/
└── iosApp/
```

### Convention Plugin пример

```kotlin
// build-logic/convention/src/main/kotlin/KmpLibraryConventionPlugin.kt
import org.gradle.api.Plugin
import org.gradle.api.Project
import org.gradle.kotlin.dsl.configure
import org.jetbrains.kotlin.gradle.dsl.KotlinMultiplatformExtension

class KmpLibraryConventionPlugin : Plugin<Project> {
    override fun apply(target: Project) {
        with(target) {
            pluginManager.apply("org.jetbrains.kotlin.multiplatform")

            extensions.configure<KotlinMultiplatformExtension> {
                androidTarget {
                    compilations.all {
                        kotlinOptions.jvmTarget = "17"
                    }
                }

                iosX64()
                iosArm64()
                iosSimulatorArm64()

                // Стандартные dependencies для всех KMP модулей
                sourceSets.commonMain.dependencies {
                    implementation(libs.findLibrary("kotlinx-coroutines-core").get())
                }
            }
        }
    }
}
```

### Umbrella Module для iOS

```kotlin
// shared/build.gradle.kts
plugins {
    id("kmp-library-convention")
}

kotlin {
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "Shared"
            isStatic = true

            // Экспортируем все feature модули
            export(project(":core:common"))
            export(project(":core:network"))
            export(project(":feature:auth"))
            export(project(":feature:home"))
        }
    }

    sourceSets {
        commonMain.dependencies {
            api(project(":core:common"))
            api(project(":core:network"))
            api(project(":feature:auth"))
            api(project(":feature:home"))
        }
    }
}
```

---

## Build файлы компиляции

### Что генерирует компилятор

```
┌─────────────────────────────────────────────────────────────┐
│                    ПРОЦЕСС КОМПИЛЯЦИИ                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  commonMain/                                                │
│      │                                                      │
│      ├──► jvmMain ──► .class файлы (JVM bytecode)          │
│      │                                                      │
│      ├──► androidMain ──► .class + Android resources       │
│      │                                                      │
│      ├──► iosMain ──► .framework (Native binary)           │
│      │                                                      │
│      └──► jsMain ──► .js файлы                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Расположение артефактов

```
shared/build/
├── classes/                       # JVM .class files
├── outputs/
│   └── aar/                      # Android AAR
├── bin/
│   ├── iosArm64/
│   │   └── releaseFramework/
│   │       └── Shared.framework/ # iOS Framework
│   └── iosSimulatorArm64/
└── js/
    └── packages/                 # JS bundle
```

---

## Типичные ошибки

### 1. Неправильная иерархия dependsOn

```kotlin
// ❌ НЕПРАВИЛЬНО — создаём orphan source set
sourceSets {
    val customMain by creating {
        // Забыли dependsOn(commonMain)!
    }
}

// ✅ ПРАВИЛЬНО
sourceSets {
    val customMain by creating {
        dependsOn(commonMain.get())
    }
}
```

### 2. Смешивание Groovy и Kotlin DSL

```kotlin
// ❌ НЕПРАВИЛЬНО — Groovy syntax в .kts файле
implementation "io.ktor:ktor-client-core:2.3.0"

// ✅ ПРАВИЛЬНО — Kotlin DSL
implementation("io.ktor:ktor-client-core:2.3.0")
// или через version catalog
implementation(libs.ktor.client.core)
```

### 3. Лишние targets в модулях

```kotlin
// ❌ НЕПРАВИЛЬНО — JVM target в модуле, который его не использует
kotlin {
    jvm()  // Не нужен, если модуль только для mobile
    android()
    iosArm64()
}

// ✅ ПРАВИЛЬНО — только нужные targets
kotlin {
    android()
    iosArm64()
    iosSimulatorArm64()
}
```

---

## Кто использует и реальные примеры

| Компания | Структура | Особенности |
|----------|-----------|-------------|
| **Touchlab** | Multi-module с Convention Plugins | 50%+ ускорение билдов после оптимизации |
| **Cash App** | Feature-based modularization | Отдельные модули для каждой фичи |
| **JetBrains** | Monorepo с shared core | Compose Multiplatform samples |
| **Google** | Shared Module Template | Официальный шаблон для Android Studio |

---

## Мифы и заблуждения о структуре KMP

### ❌ "Нужно сразу делать multi-module"

**Реальность:** Начинайте с **одного shared модуля**. Multi-module добавляет сложность:
- Больше Gradle конфигурации
- Сложнее dependency management
- Дольше sync time

**Переходите на multi-module** когда:
- Shared модуль > 50 файлов
- Разные команды работают над разными features
- Нужна изоляция для тестирования

### ❌ "Groovy Gradle всё ещё работает"

**Реальность:** JetBrains **официально рекомендует Kotlin DSL** (.kts):
- Лучшая поддержка в IDE (автодополнение, навигация)
- Type-safe конфигурация
- Единый язык (Kotlin везде)

Groovy поддерживается, но новые примеры — только на Kotlin DSL.

### ❌ "Default Hierarchy Template обязателен"

**Реальность:** Template **автоматически включён** с Kotlin 1.9+. Но в **больших проектах** (70+ модулей) может замедлить Gradle sync.

```kotlin
// Отключить если проблемы с sync
kotlin {
    // Не вызывайте applyDefaultHierarchyTemplate()
    // Настройте source sets вручную
}
```

### ❌ "iOS target = один target"

**Реальность:** Для iOS нужно **несколько targets**:

| Target | Для чего |
|--------|----------|
| `iosX64()` | Simulator на Intel Mac |
| `iosArm64()` | Реальные устройства |
| `iosSimulatorArm64()` | Simulator на Apple Silicon |

Все три объединяются через `iosMain` intermediate source set.

### ❌ "Umbrella module — это anti-pattern"

**Реальность:** Umbrella module **необходим для iOS** при multi-module структуре. iOS Xcode проект может импортировать только **один framework**. Umbrella экспортирует все модули в один Shared.framework.

### ❌ "Version Catalog опционален"

**Реальность:** Без version catalog в multi-module проекте:
- Дублирование версий в каждом build.gradle.kts
- Рассинхронизация зависимостей
- Сложнее обновлять

**libs.versions.toml** — must-have для любого серьёзного проекта.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [KMP Project Structure Basics](https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html) | Official Doc | Основы структуры |
| [Hierarchical Structure](https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html) | Official Doc | Иерархия source sets |
| [Gradle Best Practices](https://kotlinlang.org/docs/gradle-best-practices.html) | Official Doc | Оптимизация Gradle |
| [Touchlab Multi-module Guide](https://touchlab.co/optimizing-gradle-builds-in-Multi-module-projects) | Expert Blog | Оптимизация билдов |
| [KMP Architecture Best Practices](https://carrion.dev/en/posts/kmp-architecture/) | Blog | Архитектурные паттерны |

### CS-фундамент

| Концепция | Материал | Почему важно |
|-----------|----------|--------------|
| Build Systems | [[build-systems-theory]] | DAG, task graph, caching |
| Module Systems | [[module-systems]] | Cohesion, coupling, encapsulation |
| Dependency Resolution | [[dependency-resolution]] | Version conflicts, transitive deps |
| Compilation Pipeline | [[compilation-pipeline]] | Multi-target compilation |

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, Gradle 8.5+, Android Studio Otter 2025.2.1*
