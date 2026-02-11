---
title: "Cross-Platform: Build Systems — Xcode vs Gradle"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - build
  - xcode
  - gradle
  - type/comparison
  - level/intermediate
prerequisites:
  - "[[cross-platform-overview]]"
related:
  - "[[android-gradle-fundamentals]]"
  - "[[ios-xcode-fundamentals]]"
  - "[[kmp-gradle-deep-dive]]"
---

# Build Systems: Xcode vs Gradle

## TL;DR

| Аспект | Xcode Build System | Gradle |
|--------|-------------------|--------|
| **Философия** | Opaque, GUI-first | Transparent, code-first |
| **Конфигурация** | `.xcodeproj` (бинарный XML) | `build.gradle.kts` (Kotlin DSL) |
| **Воспроизводимость** | Сложно, зависит от состояния IDE | Полная, декларативная |
| **Кэширование** | Локальное, непрозрачное | Распределённое, настраиваемое |
| **Параллелизм** | Автоматический | Явный контроль через tasks |
| **Dependency Management** | SPM / CocoaPods (внешние) | Встроенный (Maven/Ivy) |
| **CI/CD интеграция** | Через xcodebuild CLI | Нативная, headless |
| **Расширяемость** | Build Phases, Run Scripts | Plugins, custom tasks |
| **Отладка билда** | Xcode GUI лимитирован | `--scan`, `--info`, `--debug` |
| **Кривая обучения** | Низкая для базы, высокая для глубины | Средняя, но предсказуемая |

---

## 1. Философия: Opaque vs Transparent

### Xcode: Opaque Box

Xcode следует принципу **"доверься системе"**:

```
Разработчик → GUI → Чёрный ящик → Артефакт
                ↓
        .xcodeproj (непрозрачный)
```

**Характеристики:**
- Конфигурация через визуальный интерфейс
- Внутренняя логика скрыта
- "Магия" работает пока работает
- Проблемы сложно диагностировать

```bash
# Что реально делает Xcode при билде?
# Документация: "It builds your project"
# Реальность: 47 скрытых шагов

# Попытка понять процесс:
xcodebuild -showBuildSettings | wc -l
# Output: 847 переменных среды
```

### Gradle: Transparent Pipeline

Gradle следует принципу **"всё явно и декларативно"**:

```
Разработчик → DSL → DAG задач → Артефакт
                ↓
        build.gradle.kts (читаемый код)
```

**Характеристики:**
- Конфигурация как код
- Каждый шаг документирован
- Полный контроль над процессом
- Воспроизводимость из коробки

```kotlin
// Что делает Gradle? Ровно то, что написано:
tasks.register("buildApp") {
    dependsOn("compileKotlin", "processResources")
    doLast {
        println("Артефакт готов в build/outputs/")
    }
}

// Диагностика одной командой:
// ./gradlew buildApp --scan
```

### Почему это важно?

| Сценарий | Xcode | Gradle |
|----------|-------|--------|
| "Билд сломался на CI" | Часы отладки | `--stacktrace` за минуты |
| "Нужен кастомный шаг" | Build Phase с bash | Типизированный task |
| "Почему билд медленный?" | Profile в Xcode (ограничен) | Build Scan с детализацией |
| "Воспроизвести билд коллеги" | "У меня работает" 🤷 | Идентичный результат |

---

## 2. Структура проекта

### Xcode Project Structure

```
MyiOSApp/
├── MyiOSApp.xcodeproj/           # Проект (папка!)
│   ├── project.pbxproj           # Главный файл (монолит)
│   ├── xcshareddata/
│   │   └── xcschemes/            # Схемы сборки
│   └── xcuserdata/               # Пользовательские настройки
├── MyiOSApp/
│   ├── Sources/
│   ├── Resources/
│   └── Info.plist
├── MyiOSAppTests/
└── MyiOSAppUITests/
```

**Проблема `project.pbxproj`:**

```
// Это реальный формат файла:
/* Begin PBXBuildFile section */
        1A2B3C4D5E6F7890 /* AppDelegate.swift in Sources */ = {
            isa = PBXBuildFile;
            fileRef = 0A1B2C3D4E5F6789 /* AppDelegate.swift */;
        };
/* End PBXBuildFile section */

// 10000+ строк UUID-ов для среднего проекта
// Merge conflicts = боль
```

### Gradle Project Structure

```
MyAndroidApp/
├── build.gradle.kts              # Корневой билд
├── settings.gradle.kts           # Настройки проекта
├── gradle.properties             # Свойства
├── app/
│   ├── build.gradle.kts          # Модуль app
│   └── src/
│       ├── main/
│       │   ├── kotlin/
│       │   ├── res/
│       │   └── AndroidManifest.xml
│       ├── debug/                # Source set для debug
│       ├── release/              # Source set для release
│       └── test/
└── feature-auth/
    ├── build.gradle.kts          # Отдельный модуль
    └── src/
```

**Читаемая конфигурация:**

```kotlin
// app/build.gradle.kts
plugins {
    id("com.android.application")
    kotlin("android")
}

android {
    namespace = "com.example.myapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.myapp"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
    }
}

dependencies {
    implementation(project(":feature-auth"))
    implementation(libs.kotlinx.coroutines)
}
```

---

## 3. Build Configurations и Variants

### Xcode: Configurations + Schemes

```
Build Configuration (что собирать):
├── Debug
├── Release
└── Custom (Staging, Beta...)

Scheme (как собирать):
├── MyApp
├── MyApp-Staging
└── MyApp-UITests
```

**Создание конфигурации:**

```bash
# Через xcconfig файлы (рекомендуется)
# Debug.xcconfig
OTHER_SWIFT_FLAGS = -DDEBUG
SWIFT_OPTIMIZATION_LEVEL = -Onone
ENABLE_TESTABILITY = YES

# Release.xcconfig
OTHER_SWIFT_FLAGS = -DRELEASE
SWIFT_OPTIMIZATION_LEVEL = -O
ENABLE_TESTABILITY = NO

# Staging.xcconfig
#include "Release.xcconfig"
OTHER_SWIFT_FLAGS = $(inherited) -DSTAGING
API_BASE_URL = https://staging.api.com
```

**В коде:**

```swift
#if DEBUG
let apiUrl = "http://localhost:8080"
#elseif STAGING
let apiUrl = "https://staging.api.com"
#else
let apiUrl = "https://api.com"
#endif
```

### Gradle: Build Types + Product Flavors = Build Variants

```kotlin
android {
    buildTypes {
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
        }
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android.txt"))
        }
        create("staging") {
            initWith(getByName("release"))
            applicationIdSuffix = ".staging"
            isDebuggable = true
        }
    }

    productFlavors {
        flavorDimensions += "environment"

        create("free") {
            dimension = "environment"
            applicationIdSuffix = ".free"
            buildConfigField("boolean", "IS_PREMIUM", "false")
        }
        create("premium") {
            dimension = "environment"
            buildConfigField("boolean", "IS_PREMIUM", "true")
        }
    }
}

// Результат: Build Variants матрица
// freeDebug, freeRelease, freeStaging
// premiumDebug, premiumRelease, premiumStaging
```

**В коде:**

```kotlin
// Автогенерированный BuildConfig
if (BuildConfig.DEBUG) {
    Timber.plant(Timber.DebugTree())
}

if (BuildConfig.IS_PREMIUM) {
    enablePremiumFeatures()
}

// Разные source sets для разных вариантов
// src/free/kotlin/PremiumFeatures.kt (заглушки)
// src/premium/kotlin/PremiumFeatures.kt (реализация)
```

### Сравнение матрицы вариантов

| Возможность | Xcode | Gradle |
|-------------|-------|--------|
| Количество осей | 1 (Configuration) | N (flavor dimensions) |
| Комбинаторика | Ручная | Автоматическая |
| Source sets | Ручные target membership | Автоматические по convention |
| Переключение | Scheme picker | Build Variant picker |

---

## 4. CI/CD интеграция

### Xcode на CI

```yaml
# .github/workflows/ios.yml
name: iOS Build

on: [push]

jobs:
  build:
    runs-on: macos-14

    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.2.app

      - name: Install certificates
        env:
          P12_PASSWORD: ${{ secrets.P12_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: |
          # 50 строк создания keychain и импорта сертификатов
          security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          security default-keychain -s build.keychain
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
          # ... ещё много магии

      - name: Build
        run: |
          xcodebuild -workspace MyApp.xcworkspace \
            -scheme MyApp \
            -configuration Release \
            -destination 'generic/platform=iOS' \
            -archivePath build/MyApp.xcarchive \
            archive

      - name: Export IPA
        run: |
          xcodebuild -exportArchive \
            -archivePath build/MyApp.xcarchive \
            -exportPath build/output \
            -exportOptionsPlist ExportOptions.plist
```

**Боли Xcode CI:**
- Требует macOS runner (дорого)
- Сертификаты и provisioning profiles
- Непредсказуемое время билда
- Кэширование DerivedData ненадёжно

### Gradle на CI

```yaml
# .github/workflows/android.yml
name: Android Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest  # Дешевле!

    steps:
      - uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          cache-read-only: ${{ github.ref != 'refs/heads/main' }}

      - name: Build
        run: ./gradlew assembleRelease --no-daemon

      - name: Run tests
        run: ./gradlew testReleaseUnitTest

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: release-apk
          path: app/build/outputs/apk/release/*.apk
```

**Преимущества Gradle CI:**
- Linux runners (дешевле в 10x)
- Встроенное кэширование
- Предсказуемые билды
- Gradle Build Cache для распределённого кэша

### Сравнение CI/CD

| Аспект | Xcode | Gradle |
|--------|-------|--------|
| Runner OS | macOS only | Any (Linux рекомендуется) |
| Стоимость | $$$$ | $ |
| Setup сложность | Высокая (signing) | Низкая |
| Кэширование | Нестабильное | Надёжное |
| Параллелизм | Ограничен | `--parallel` |
| Инкрементальность | Непредсказуема | Детерминированная |

---

## 5. KMP: Gradle + Xcode интеграция

### Архитектура KMP билда

```
Kotlin Multiplatform Project
├── build.gradle.kts (Gradle управляет всем)
│
├── shared/                    # Общий код
│   ├── build.gradle.kts
│   └── src/
│       ├── commonMain/        # Общий код
│       ├── androidMain/       # Android-specific
│       └── iosMain/           # iOS-specific
│
├── androidApp/                # Android приложение
│   └── build.gradle.kts       # Gradle нативно
│
└── iosApp/                    # iOS приложение
    ├── iosApp.xcodeproj       # Xcode проект
    └── iosApp/
        └── ContentView.swift
```

### Gradle конфигурация для iOS

```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
    kotlin("native.cocoapods")  // Или SPM интеграция
}

kotlin {
    androidTarget()

    // iOS targets
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = "Shared"
            isStatic = true
        }
    }

    // CocoaPods интеграция
    cocoapods {
        summary = "Shared KMP module"
        homepage = "https://example.com"
        version = "1.0"
        ios.deploymentTarget = "14.0"

        framework {
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
            implementation(libs.ktor.client.okhttp)
        }

        iosMain.dependencies {
            implementation(libs.ktor.client.darwin)
        }
    }
}
```

### Xcode интеграция

**Вариант 1: CocoaPods**

```ruby
# iosApp/Podfile
platform :ios, '14.0'

target 'iosApp' do
  use_frameworks!

  # Сгенерированный Gradle pod
  pod 'Shared', :path => '../shared'
end
```

```bash
# Синхронизация после изменений в shared
cd shared && ../gradlew podInstall
cd ../iosApp && pod install
```

**Вариант 2: Direct Framework**

```bash
# Build Phase в Xcode (Run Script)
cd "$SRCROOT/../shared"
./gradlew :shared:embedAndSignAppleFrameworkForXcode
```

**Вариант 3: SPM (Swift Package Manager)**

```kotlin
// shared/build.gradle.kts
kotlin {
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach {
        it.binaries.framework {
            baseName = "Shared"
            binaryOption("bundleId", "com.example.shared")
        }
    }
}

// Генерация Package.swift
tasks.register("generatePackageSwift") {
    doLast {
        file("Package.swift").writeText("""
            // swift-tools-version:5.9
            import PackageDescription

            let package = Package(
                name: "Shared",
                platforms: [.iOS(.v14)],
                products: [
                    .library(name: "Shared", targets: ["Shared"])
                ],
                targets: [
                    .binaryTarget(
                        name: "Shared",
                        path: "build/XCFrameworks/release/Shared.xcframework"
                    )
                ]
            )
        """.trimIndent())
    }
}
```

### Build Flow в KMP

```
Developer изменяет shared/
            ↓
┌───────────────────────────────────────┐
│           Gradle Build                │
│  ┌─────────────────────────────────┐  │
│  │ :shared:compileKotlinIosArm64   │  │
│  │ :shared:linkReleaseFramework    │  │
│  │ :shared:podPublishXCFramework   │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
            ↓
    Shared.xcframework
            ↓
┌───────────────────────────────────────┐
│           Xcode Build                 │
│  ┌─────────────────────────────────┐  │
│  │ Embed Shared.xcframework        │  │
│  │ Compile Swift sources           │  │
│  │ Link and sign                   │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
            ↓
        iosApp.ipa
```

---

## 6. Типичные ошибки (6 ошибок)

### Ошибка 1: Игнорирование xcconfig файлов

```swift
// ❌ ПЛОХО: Хардкод в Build Settings GUI
// Нельзя версионировать, сложно сравнивать

// ✅ ХОРОШО: Всё в xcconfig
// Base.xcconfig
PRODUCT_BUNDLE_IDENTIFIER = com.example.$(PRODUCT_NAME:rfc1034identifier)
SWIFT_VERSION = 5.9
IPHONEOS_DEPLOYMENT_TARGET = 14.0

// Debug.xcconfig
#include "Base.xcconfig"
GCC_OPTIMIZATION_LEVEL = 0
SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG

// В Xcode: Project → Info → Configurations → Based on: Debug.xcconfig
```

### Ошибка 2: Монолитный Gradle файл

```kotlin
// ❌ ПЛОХО: Всё в одном build.gradle.kts (500+ строк)
plugins {
    // 20 плагинов
}
android {
    // 200 строк конфигурации
}
dependencies {
    // 100 зависимостей
}

// ✅ ХОРОШО: Convention plugins
// buildSrc/src/main/kotlin/android-library-convention.gradle.kts
plugins {
    id("com.android.library")
    kotlin("android")
}

android {
    compileSdk = 34
    defaultConfig {
        minSdk = 24
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

// Использование в модуле:
// feature/build.gradle.kts
plugins {
    id("android-library-convention")
}
// Готово! Конфигурация унаследована
```

### Ошибка 3: Неправильный KMP framework type

```kotlin
// ❌ ПЛОХО: Dynamic framework с CocoaPods
framework {
    baseName = "Shared"
    isStatic = false  // Проблемы с символами!
}

// Симптомы:
// - "Undefined symbols for architecture arm64"
// - Дублирование runtime
// - Падения при доступе к Kotlin объектам

// ✅ ХОРОШО: Static framework
framework {
    baseName = "Shared"
    isStatic = true  // Всегда для production
}
```

### Ошибка 4: Кэш DerivedData как silver bullet

```bash
# ❌ ПЛОХО: Надежда на кэш
# CI workflow:
- name: Cache DerivedData
  uses: actions/cache@v4
  with:
    path: ~/Library/Developer/Xcode/DerivedData
    key: derived-data-${{ hashFiles('*.xcodeproj') }}

# Проблема: DerivedData содержит абсолютные пути
# Кэш между разными машинами = случайные падения

# ✅ ХОРОШО: Инкрементальные билды через Xcode Cloud или Fastlane match
# Или принять clean builds на CI (надёжнее)
```

### Ошибка 5: Игнорирование Gradle configuration cache

```kotlin
// ❌ ПЛОХО: Configuration phase выполняется каждый раз
// build.gradle.kts
val gitCommit = "git rev-parse HEAD".execute()  // Выполняется при конфигурации!

android {
    defaultConfig {
        buildConfigField("String", "GIT_COMMIT", "\"$gitCommit\"")
    }
}

// Каждый запуск = перечитывание всех build.gradle файлов

// ✅ ХОРОШО: Используем Provider API для ленивости
val gitCommit = providers.exec {
    commandLine("git", "rev-parse", "HEAD")
}.standardOutput.asText.map { it.trim() }

android {
    defaultConfig {
        buildConfigField("String", "GIT_COMMIT", gitCommit.map { "\"$it\"" })
    }
}

// Включаем configuration cache:
// gradle.properties
org.gradle.configuration-cache=true
```

### Ошибка 6: Build Phase порядок в Xcode

```bash
# ❌ ПЛОХО: KMP framework генерируется после компиляции Swift
# Build Phases порядок:
# 1. Compile Sources  ← Не найдёт Shared framework!
# 2. Run Script (gradle embedAndSignAppleFrameworkForXcode)
# 3. Link Binary

# ✅ ХОРОШО: Правильный порядок
# Build Phases:
# 1. Run Script (gradle embedAndSignAppleFrameworkForXcode)
# 2. Compile Sources
# 3. Link Binary With Libraries
# 4. Embed Frameworks

# Script phase настройки:
# ☑️ Based on dependency analysis: OFF (для надёжности)
# Input Files: $(SRCROOT)/../shared/src/**/*.kt
# Output Files: $(BUILT_PRODUCTS_DIR)/Shared.framework
```

---

## 7. Mental Models (3 модели)

### Mental Model 1: "Makefile vs IDE Project"

```
Gradle ≈ Sophisticated Makefile
- Текстовый, декларативный
- DAG задач с зависимостями
- Инкрементальность по файлам
- Портируемый между машинами

Xcode Project ≈ Visual Studio Solution
- GUI-ориентированный
- Состояние в IDE
- "Build" как атомарная операция
- Привязан к конкретной машине

Практическое следствие:
- Gradle: "Что изменилось? Пересобрать только это"
- Xcode: "Пересобрать всё на всякий случай"
```

### Mental Model 2: "Recipe vs Ingredients"

```
Xcode = Набор ингредиентов
┌─────────────────────────────────────┐
│ Source Files    │ Framework         │
│ Resources       │ Build Settings    │
│ Entitlements    │ Schemes           │
└─────────────────────────────────────┘
"Как готовить? Xcode знает"

Gradle = Рецепт + Ингредиенты
┌─────────────────────────────────────┐
│ plugins { }     → Какие инструменты │
│ android { }     → Как настроить     │
│ dependencies {} → Что использовать  │
│ tasks { }       → Что делать        │
└─────────────────────────────────────┘
"Как готовить? Написано явно"

Когда рецепт важнее:
- Сложные проекты (много модулей)
- CI/CD (воспроизводимость)
- Командная работа (код-ревью конфигурации)
```

### Mental Model 3: "Push vs Pull Dependencies"

```
Xcode: Push Model
┌─────────┐
│ Target  │ ← "Добавь этот framework в target"
└─────────┘
           ← "Добавь эту библиотеку в target"
           ← "Добавь ресурсы в target"

Проблема: Target становится "свалкой"
Сложно понять, что от чего зависит

Gradle: Pull Model
┌─────────┐
│ Module  │
└─────────┘
     │
     ├── dependencies {
     │       implementation(project(":core"))  // Явная связь
     │       implementation(libs.retrofit)     // Версия в каталоге
     │   }
     │
     └── Модуль сам объявляет, что ему нужно

Преимущество:
- Зависимости рядом с кодом
- Version catalog = единая точка правды
- Dependency graph легко визуализировать:
  ./gradlew :app:dependencies
```

---

## 8. Quiz (3 вопроса)

### Вопрос 1: Configuration vs Execution Phase

```kotlin
// Что не так с этим кодом?
// build.gradle.kts

val apiKey = System.getenv("API_KEY") ?: "default"

android {
    defaultConfig {
        buildConfigField("String", "API_KEY", "\"$apiKey\"")
    }
}

tasks.register("printApiKey") {
    println("API Key: $apiKey")  // Строка A
    doLast {
        println("API Key: $apiKey")  // Строка B
    }
}
```

<details>
<summary>Ответ</summary>

**Проблема в разнице между Configuration и Execution phase:**

- `System.getenv("API_KEY")` выполняется в **configuration phase** (всегда)
- Строка A (`println` вне `doLast`) — **configuration phase** (всегда печатается)
- Строка B (`println` внутри `doLast`) — **execution phase** (только при запуске таска)

**Последствия:**
1. API_KEY читается даже если задача не запускается
2. Ломает configuration cache
3. "printApiKey" печатает значение дважды

**Правильное решение:**

```kotlin
val apiKey = providers.environmentVariable("API_KEY")
    .orElse("default")

android {
    defaultConfig {
        buildConfigField("String", "API_KEY", apiKey.map { "\"$it\"" })
    }
}

tasks.register("printApiKey") {
    val key = apiKey  // Захват provider
    doLast {
        println("API Key: ${key.get()}")  // Только execution
    }
}
```

</details>

### Вопрос 2: Xcode Build Settings Resolution

```
У вас есть:
1. Project-level: SWIFT_VERSION = 5.5
2. Target-level: SWIFT_VERSION = 5.9
3. xcconfig file: SWIFT_VERSION = 5.7
4. Build Settings GUI override: SWIFT_VERSION = 6.0

В каком порядке применяются? Какой результат?
```

<details>
<summary>Ответ</summary>

**Порядок разрешения (от низшего к высшему приоритету):**

1. Xcode defaults (встроенные)
2. Project-level xcconfig
3. Project-level Build Settings
4. Target-level xcconfig
5. Target-level Build Settings

**Но есть нюанс!** Если в GUI стоит значение (не "$(inherited)"), оно перезаписывает xcconfig.

**Визуально в Xcode:**
- Зелёный = из xcconfig
- Чёрный = явно задано в GUI
- Серый = унаследовано

**Результат для примера:**
Зависит от того, где именно "GUI override":
- Если это Target Build Settings GUI → `6.0` (перезапишет xcconfig)
- Если xcconfig подключён к Target → `5.7` (если GUI не менялся)

**Best Practice:**
```
// Не трогать GUI, всё в xcconfig
// Target.xcconfig
#include "../Project.xcconfig"
SWIFT_VERSION = 5.9
// Результат предсказуем: 5.9
```

</details>

### Вопрос 3: KMP Build Order

```kotlin
// Почему этот CI билд падает случайным образом?

// .github/workflows/kmp.yml
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Android
        run: ./gradlew :androidApp:assembleDebug &

      - name: Build iOS
        run: |
          cd iosApp
          xcodebuild -workspace iosApp.xcworkspace \
            -scheme iosApp build &

      - name: Wait
        run: wait
```

<details>
<summary>Ответ</summary>

**Проблемы:**

1. **Параллельный Gradle и Xcode конфликтуют на shared модуле**
   - Оба пытаются собрать `:shared`
   - Gradle лочит файлы, Xcode ждёт или падает

2. **Xcode нужен уже собранный framework**
   - `xcodebuild` ожидает Shared.framework
   - Gradle может не успеть его собрать

3. **Background processes (&) скрывают ошибки**
   - `wait` возвращает статус последнего процесса
   - Первый может упасть незаметно

**Правильное решение:**

```yaml
jobs:
  build-shared:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build Shared Framework
        run: ./gradlew :shared:linkReleaseFrameworkIosArm64
      - uses: actions/upload-artifact@v4
        with:
          name: shared-framework
          path: shared/build/bin/iosArm64/releaseFramework/

  build-android:
    runs-on: ubuntu-latest
    needs: build-shared  # Или параллельно, если не зависит
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew :androidApp:assembleRelease

  build-ios:
    runs-on: macos-latest
    needs: build-shared
    steps:
      - uses: actions/checkout@v4
      - uses: actions/download-artifact@v4
        with:
          name: shared-framework
          path: shared/build/bin/iosArm64/releaseFramework/
      - run: |
          cd iosApp
          xcodebuild -workspace iosApp.xcworkspace -scheme iosApp build
```

</details>

---

## 9. Связь с другими темами

[[android-gradle-fundamentals]] — Gradle — это не просто билд-инструмент, а полноценная платформа автоматизации с DSL на Kotlin/Groovy, системой плагинов и инкрементальной компиляцией. Заметка разбирает task graph, build phases (initialization → configuration → execution), кастомные плагины и оптимизацию через build cache. Глубокое понимание Gradle необходимо для настройки KMP-проектов, где один Gradle build объединяет Android, iOS framework и shared-модули.

[[ios-xcode-fundamentals]] — Xcode Build System использует принципиально другой подход: xcodeproj/xcworkspace, schemes, build configurations и build phases вместо task graph. Заметка объясняет, как работают compile sources, link binary, copy resources, run script phases, а также signing и provisioning. Знание Xcode необходимо для интеграции KMP framework через SPM или CocoaPods и для настройки CI/CD на macOS runners.

[[kmp-gradle-deep-dive]] — KMP-проекты требуют специфической настройки Gradle: kotlin-multiplatform плагин, source sets (commonMain, androidMain, iosMain), expect/actual declarations, настройка iOS framework export. Заметка раскрывает тонкости конфигурации cocoapods plugin, XCFramework генерации и интеграции с Xcode через embedAndSign task. Это мост между Android Gradle и iOS Xcode build pipelines.

---

## 10. Источники и дальнейшее чтение

- Moskala M. (2021). *Effective Kotlin: Best Practices.* — Включает разделы о Gradle конфигурации для Kotlin-проектов, оптимизации сборки и best practices для build scripts. Полезна для понимания Kotlin DSL в build.gradle.kts.
- Meier R. (2022). *Professional Android.* — Подробно описывает Android Build System, Gradle plugins, Build Variants, Product Flavors и ProGuard/R8 конфигурацию. Практическое руководство для настройки сложных Android-проектов.
- Neuburg M. (2023). *iOS Programming Fundamentals with Swift.* — Разбирает Xcode project structure, build settings, schemes и configurations. Незаменима для понимания iOS build pipeline и интеграции сторонних зависимостей.
