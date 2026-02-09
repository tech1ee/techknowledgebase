---
title: "Эволюция систем сборки Android: от Ant до Gradle"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [build-systems, dependency-resolution, incremental-compilation, task-graph]
tags:
  - topic/android
  - topic/build-system
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-gradle-fundamentals]]"
  - "[[android-compilation-pipeline]]"
  - "[[android-project-structure]]"
---

# Эволюция систем сборки Android: от Ant до Gradle

История систем сборки Android — это история боли, костылей и постепенного движения к унификации. Понимание этой эволюции объясняет, почему современный Gradle выглядит именно так, и помогает избежать повторения старых ошибок.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android-разработки
> - Общее представление о системах сборки (make, maven, gradle)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Build System** | Инструмент для автоматизации компиляции, тестирования и упаковки кода |
| **Ant** | Apache Ant — XML-based build tool, первая официальная система сборки Android |
| **Maven** | Apache Maven — build tool с управлением зависимостями, использовался косвенно |
| **Gradle** | Современная build система с Groovy/Kotlin DSL |
| **AGP** | Android Gradle Plugin — плагин Gradle для сборки Android-приложений |
| **ADT** | Android Development Tools — плагин Eclipse для Android-разработки |
| **DSL** | Domain Specific Language — специализированный язык для конкретной области |

---

## Хронология: 17 лет эволюции

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ЭВОЛЮЦИЯ СИСТЕМ СБОРКИ ANDROID                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  2008        2010        2012        2014        2016        2020       │
│    │           │           │           │           │           │        │
│    ▼           ▼           ▼           ▼           ▼           ▼        │
│  ┌───┐      ┌───┐      ┌───────┐   ┌───────┐   ┌───────┐   ┌───────┐   │
│  │Ant│      │Ant│      │Eclipse│   │Android│   │Gradle │   │Kotlin │   │
│  │1.0│      │1.8│      │ ADT   │   │Studio │   │ 3.0   │   │ DSL   │   │
│  └───┘      └───┘      │ Build │   │+Gradle│   │ + AGP │   │default│   │
│    │           │       └───────┘   └───────┘   └───────┘   └───────┘   │
│    │           │           │           │           │           │        │
│    └───────────┴───────────┴───────────┴───────────┴───────────┘        │
│                                                                         │
│  Проблемы:   Проблемы:   Проблемы:   Решение:    Зрелость:   Будущее:  │
│  - Verbose   - CI ≠ IDE  - Нет CLI   - Единый    - Instant   - KTS     │
│  - Manual    - Manual    - Lock-in   - DSL       - Caching   - AGP 9.0 │
│  - No deps   - deps      - Slow      - Plugins   - D8/R8     - Compose │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Эра 1: Ant (2008-2013) — "Всё вручную"

### Как это работало

Android SDK изначально поставлялся с Ant-скриптами. Ant — это XML-based build tool от Apache, где каждый шаг сборки описывается явно.

```xml
<!-- build.xml — типичный Ant-скрипт для Android (2008-2010) -->
<?xml version="1.0" encoding="UTF-8"?>
<project name="MyApp" default="debug">

    <!-- Подключение Android-специфичных задач -->
    <property file="local.properties" />
    <property file="build.properties" />

    <!-- Переменные окружения -->
    <property name="sdk.dir" value="/path/to/android-sdk" />
    <property name="target" value="android-8" />

    <!-- Компиляция Java -->
    <target name="compile">
        <javac srcdir="src"
               destdir="bin/classes"
               classpath="${sdk.dir}/platforms/${target}/android.jar">
            <classpath>
                <fileset dir="libs" includes="*.jar"/>
            </classpath>
        </javac>
    </target>

    <!-- Генерация R.java -->
    <target name="generate-r" depends="compile">
        <exec executable="${sdk.dir}/platform-tools/aapt">
            <arg value="package"/>
            <arg value="-m"/>
            <arg value="-J"/>
            <arg value="gen"/>
            <arg value="-M"/>
            <arg value="AndroidManifest.xml"/>
            <arg value="-S"/>
            <arg value="res"/>
            <arg value="-I"/>
            <arg value="${sdk.dir}/platforms/${target}/android.jar"/>
        </exec>
    </target>

    <!-- DEX компиляция -->
    <target name="dex" depends="compile">
        <exec executable="${sdk.dir}/platform-tools/dx">
            <arg value="--dex"/>
            <arg value="--output=bin/classes.dex"/>
            <arg value="bin/classes"/>
            <arg value="libs"/>
        </exec>
    </target>

    <!-- Упаковка APK -->
    <target name="package" depends="dex">
        <exec executable="${sdk.dir}/platform-tools/aapt">
            <arg value="package"/>
            <arg value="-f"/>
            <arg value="-M"/>
            <arg value="AndroidManifest.xml"/>
            <arg value="-S"/>
            <arg value="res"/>
            <arg value="-I"/>
            <arg value="${sdk.dir}/platforms/${target}/android.jar"/>
            <arg value="-F"/>
            <arg value="bin/MyApp-unsigned.apk"/>
        </exec>
    </target>

    <!-- Подпись APK -->
    <target name="debug" depends="package">
        <signjar jar="bin/MyApp-unsigned.apk"
                 signedjar="bin/MyApp-debug.apk"
                 keystore="~/.android/debug.keystore"
                 alias="androiddebugkey"
                 storepass="android"/>
    </target>

</project>
```

### Проблемы Ant

**1. Избыточность (Verbosity)**
```xml
<!-- Чтобы просто скомпилировать Java-файлы, нужно было написать всё это -->
<target name="compile">
    <mkdir dir="${build.dir}/classes"/>
    <javac srcdir="${src.dir}"
           destdir="${build.dir}/classes"
           source="1.6"
           target="1.6"
           debug="true"
           includeantruntime="false">
        <classpath>
            <pathelement path="${android.jar}"/>
            <fileset dir="${libs.dir}" includes="*.jar"/>
        </classpath>
    </javac>
</target>

<!-- vs Gradle (современный) -->
<!-- Просто ничего — всё автоматически -->
```

**2. Управление зависимостями — вручную**
```
libs/
├── gson-2.2.4.jar          # Скачал с сайта
├── okhttp-1.0.0.jar        # Скачал с сайта
├── support-v4-r7.jar       # Скопировал из SDK
└── commons-lang-2.6.jar    # Откуда-то достал

# Проблемы:
# - Версии не отслеживаются
# - Транзитивные зависимости — вручную
# - Конфликты версий — "works on my machine"
# - Обновление — ручной труд
```

**3. Расхождение IDE и CLI**
```
┌─────────────────────────────────────────────────────────────────┐
│                    ПРОБЛЕМА: IDE ≠ CLI                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Eclipse ADT                        ant debug                   │
│  ───────────                        ─────────                   │
│  Собирает проект                    Собирает проект             │
│  своим способом                     своим способом              │
│                                                                 │
│  Результат:                         Результат:                  │
│  APK работает                       APK не работает             │
│                                     (или наоборот)              │
│                                                                 │
│  "У меня локально всё работает, а на CI падает!"               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**4. Нет стандартной структуры проекта**
```
# Проект A
MyApp/
├── src/
├── res/
└── build.xml

# Проект B (тот же разработчик)
AnotherApp/
├── source/
├── resources/
└── ant-build.xml

# Каждый проект — уникальная снежинка
```

---

## Эра 2: Eclipse ADT (2009-2014) — "Визуальная магия"

### Как это работало

Eclipse с плагином ADT (Android Development Tools) стал де-факто стандартом. ADT прятал Ant под капотом и давал визуальный интерфейс.

```
┌─────────────────────────────────────────────────────────────────┐
│                       ECLIPSE ADT BUILD                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────┐                                              │
│  │   Eclipse     │                                              │
│  │   + ADT       │                                              │
│  └───────┬───────┘                                              │
│          │                                                      │
│          ▼                                                      │
│  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐   │
│  │  ADT Builder  │───▶│  Ant Tasks    │───▶│     APK       │   │
│  │  (internal)   │    │  (hidden)     │    │               │   │
│  └───────────────┘    └───────────────┘    └───────────────┘   │
│                                                                 │
│  Проблема: Что именно делает ADT — чёрный ящик                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Проблемы Eclipse ADT

**1. Vendor Lock-in**
```
# Хотите собрать без Eclipse?
$ ant debug
BUILD FAILED
Error: Unable to find build.properties
Error: project.properties missing required settings

# ADT генерировал нестандартные конфиги,
# которые Ant без Eclipse не понимал
```

**2. Отсутствие командной строки**
```bash
# CI/CD в 2010:
# 1. Установить Eclipse на сервер (!)
# 2. Запустить Eclipse headless mode
# 3. Надеяться, что не упадёт

$ eclipse -nosplash -application org.eclipse.ant.core.antRunner \
    -buildfile build.xml

# Это реально так делали
```

**3. Медленная сборка**
```
┌─────────────────────────────────────────────────────────────────┐
│                    ВРЕМЯ СБОРКИ (2012)                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Маленький проект (~10K LOC):                                   │
│  Eclipse ADT: 45-60 секунд (полная пересборка)                  │
│  Инкрементальная: 15-30 секунд                                  │
│                                                                 │
│  Средний проект (~50K LOC):                                     │
│  Eclipse ADT: 3-5 минут                                         │
│  Инкрементальная: 1-2 минуты                                    │
│                                                                 │
│  Причины:                                                       │
│  - Нет кэширования артефактов                                   │
│  - Полная перекомпиляция при изменении ресурсов                │
│  - Однопоточная сборка                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**4. Проблемы с зависимостями между проектами**
```
# Android Library Projects — особая боль

MainApp/
├── libs/
│   └── library-project/  # Ссылка на другой проект
└── project.properties
    android.library.reference.1=../library-project

# Проблемы:
# - Относительные пути ломаются при переносе
# - Циклические зависимости — undefined behavior
# - Версионирование библиотек — невозможно
```

---

## Эра 3: Gradle приходит (2013-2015) — "Революция"

### Google I/O 2013: Анонс Android Studio

Google объявил о переходе на Gradle и новую IDE — Android Studio (на базе IntelliJ IDEA). Это был фундаментальный сдвиг.

```
┌─────────────────────────────────────────────────────────────────┐
│              GOOGLE I/O 2013: НОВАЯ ЭРА                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "We're announcing Android Studio, a new IDE for Android        │
│   development, based on the popular IntelliJ IDEA."             │
│                                                                 │
│   — Xavier Ducrohet, Android SDK Tech Lead                      │
│                                                                 │
│  Ключевые обещания:                                             │
│  ✓ Единая сборка: IDE = CLI = CI                               │
│  ✓ Декларативный DSL вместо императивного XML                  │
│  ✓ Управление зависимостями из коробки                         │
│  ✓ Build variants (debug, release, flavors)                    │
│  ✓ Параллельная сборка                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Первый build.gradle (2013)

```groovy
// build.gradle — первые версии AGP (0.x)
buildscript {
    repositories {
        mavenCentral()
    }
    dependencies {
        classpath 'com.android.tools.build:gradle:0.5.+'
    }
}

apply plugin: 'android'

android {
    compileSdkVersion 17
    buildToolsVersion "17.0.0"

    defaultConfig {
        minSdkVersion 7
        targetSdkVersion 17
    }
}

dependencies {
    compile 'com.google.code.gson:gson:2.2.4'
    compile 'com.squareup.okhttp:okhttp:1.0.0'
}
```

### Почему Gradle победил

**1. Единый источник правды**
```
┌─────────────────────────────────────────────────────────────────┐
│                    GRADLE: ЕДИНАЯ СБОРКА                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  build.gradle.kts                                               │
│       │                                                         │
│       ├──────────────────┬──────────────────┐                   │
│       ▼                  ▼                  ▼                   │
│  ┌─────────┐        ┌─────────┐        ┌─────────┐             │
│  │ Android │        │  CLI    │        │   CI    │             │
│  │ Studio  │        │ gradlew │        │ Jenkins │             │
│  └─────────┘        └─────────┘        └─────────┘             │
│       │                  │                  │                   │
│       └──────────────────┴──────────────────┘                   │
│                          │                                      │
│                          ▼                                      │
│                    ОДИНАКОВЫЙ APK                               │
│                                                                 │
│  Больше нет "works on my machine"!                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**2. Декларативный DSL**
```groovy
// Ant (императивно): ЧТО делать и КАК делать
<target name="compile">
    <mkdir dir="build/classes"/>
    <javac srcdir="src" destdir="build/classes">
        <classpath>
            <pathelement path="libs/gson.jar"/>
        </classpath>
    </javac>
</target>

// Gradle (декларативно): ЧТО нужно получить
dependencies {
    implementation("com.google.code.gson:gson:2.10")
}
// КАК — решает Gradle
```

**3. Управление зависимостями**
```kotlin
// build.gradle.kts — современный синтаксис
dependencies {
    // Gradle автоматически:
    // - Скачивает из Maven Central
    // - Кэширует локально
    // - Разрешает транзитивные зависимости
    // - Обнаруживает конфликты версий

    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    // → автоматически подтягивает okhttp, okio, и т.д.

    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    // → Gradle разрешает конфликт версий okhttp
}
```

**4. Build Variants**
```kotlin
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
        debug {
            isDebuggable = true
            applicationIdSuffix = ".debug"
        }
    }

    flavorDimensions += "environment"
    productFlavors {
        create("dev") {
            dimension = "environment"
            applicationIdSuffix = ".dev"
            buildConfigField("String", "API_URL", "\"https://dev.api.com\"")
        }
        create("prod") {
            dimension = "environment"
            buildConfigField("String", "API_URL", "\"https://api.com\"")
        }
    }
}

// Результат: 4 варианта сборки
// devDebug, devRelease, prodDebug, prodRelease
```

---

## Эра 4: Зрелость Gradle (2016-2020) — "Оптимизация"

### AGP 3.0: Большой рефакторинг (2017)

```kotlin
// BREAKING CHANGES в AGP 3.0

// ДО (AGP 2.x)
dependencies {
    compile 'com.example:library:1.0'      // Deprecated
    provided 'com.example:library:1.0'     // Deprecated
    apk 'com.example:library:1.0'          // Deprecated
}

// ПОСЛЕ (AGP 3.0+)
dependencies {
    implementation("com.example:library:1.0")  // Не экспортируется
    api("com.example:library:1.0")             // Экспортируется
    compileOnly("com.example:library:1.0")     // Только компиляция
    runtimeOnly("com.example:library:1.0")     // Только runtime
}
```

**Почему `implementation` вместо `compile`:**
```
┌─────────────────────────────────────────────────────────────────┐
│              COMPILE vs IMPLEMENTATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  compile (старый):                                              │
│  ┌─────┐    ┌─────┐    ┌─────┐                                 │
│  │ App │───▶│Lib A│───▶│Lib B│                                 │
│  └─────┘    └─────┘    └─────┘                                 │
│      │                    ▲                                     │
│      └────────────────────┘                                     │
│      App видит Lib B (транзитивно)                             │
│                                                                 │
│  Проблема: Изменение в Lib B → перекомпиляция App              │
│                                                                 │
│  implementation (новый):                                        │
│  ┌─────┐    ┌─────┐    ┌─────┐                                 │
│  │ App │───▶│Lib A│───▶│Lib B│                                 │
│  └─────┘    └─────┘    └─────┘                                 │
│      │         ▲                                                │
│      └─────────┘                                                │
│      App НЕ видит Lib B                                        │
│                                                                 │
│  Преимущество: Изменение в Lib B → перекомпиляция только Lib A │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### D8 и R8 (2017-2019)

```
┌─────────────────────────────────────────────────────────────────┐
│                    ЭВОЛЮЦИЯ КОМПИЛЯТОРОВ                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  2008-2017: DX                                                  │
│  .java → javac → .class → DX → .dex                            │
│  (медленный, большой output)                                    │
│                                                                 │
│  2017-2018: D8                                                  │
│  .java → javac → .class → D8 → .dex                            │
│  (быстрее, меньше output, desugaring)                          │
│                                                                 │
│  2018+: R8 (release builds)                                     │
│  .java → javac → .class → R8 → .dex                            │
│  (D8 + shrinking + obfuscation + optimization)                 │
│                                                                 │
│  Результаты:                                                    │
│  - Время сборки: -20%                                           │
│  - Размер APK: -10%                                             │
│  - Runtime performance: +15%                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Instant Run → Apply Changes (2016-2020)

```kotlin
// Эволюция горячей перезагрузки

// Instant Run (AGP 2.0, 2016) — первая попытка
// Проблемы:
// - Нестабильная работа
// - Иногда требовался полный rebuild
// - Corrupted state после нескольких изменений

// Apply Changes (AGP 3.5, 2019) — переосмысление
// Три уровня:
// 1. Apply Code Changes (Ctrl+Alt+F10)
//    - Изменения в методах
//    - Не требует restart Activity
//
// 2. Apply Changes and Restart Activity (Ctrl+F10)
//    - Изменения в ресурсах
//    - Новые методы/классы
//
// 3. Run (Shift+F10)
//    - Изменения в Manifest
//    - Изменения в native code
```

---

## Эра 5: Современность (2020-2025) — "Kotlin DSL и AGP 8+"

### Kotlin DSL становится стандартом

```kotlin
// settings.gradle.kts — современный проект
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "MyApp"
include(":app")
include(":core:data")
include(":core:domain")
include(":feature:home")
include(":feature:profile")
```

```kotlin
// build.gradle.kts (app module)
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
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}

dependencies {
    // Version Catalog
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.material3)

    // Hilt
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)

    // Testing
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.test.ext)
}
```

### Version Catalogs (libs.versions.toml)

```toml
# gradle/libs.versions.toml
[versions]
agp = "8.7.0"
kotlin = "2.0.21"
compose-bom = "2024.10.01"
hilt = "2.52"
retrofit = "2.11.0"
room = "2.6.1"

[libraries]
androidx-core-ktx = { group = "androidx.core", name = "core-ktx", version = "1.15.0" }
androidx-lifecycle-runtime-ktx = { group = "androidx.lifecycle", name = "lifecycle-runtime-ktx", version = "2.8.7" }
androidx-activity-compose = { group = "androidx.activity", name = "activity-compose", version = "1.9.3" }
androidx-compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
androidx-ui = { group = "androidx.compose.ui", name = "ui" }
androidx-material3 = { group = "androidx.compose.material3", name = "material3" }
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler = { group = "com.google.dagger", name = "hilt-compiler", version.ref = "hilt" }
retrofit = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }
room-runtime = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-ktx = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }

[bundles]
compose = ["androidx-ui", "androidx-material3"]
room = ["room-runtime", "room-ktx"]

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
android-library = { id = "com.android.library", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
kotlin-compose = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp = { id = "com.google.devtools.ksp", version = "2.0.21-1.0.27" }
```

### Configuration Cache и Build Cache

```kotlin
// gradle.properties — оптимизация сборки

# Configuration Cache (кэширует конфигурацию проекта)
org.gradle.configuration-cache=true

# Build Cache (кэширует артефакты между сборками)
org.gradle.caching=true

# Параллельная сборка
org.gradle.parallel=true

# Daemon (переиспользование JVM)
org.gradle.daemon=true

# Память
org.gradle.jvmargs=-Xmx4096m -XX:+UseParallelGC

# Non-transitive R classes (уменьшает размер R.java)
android.nonTransitiveRClass=true

# Использовать новый resource compiler
android.enableNewResourceShrinker=true
```

**Результаты оптимизации:**
```
┌─────────────────────────────────────────────────────────────────┐
│                 ВРЕМЯ СБОРКИ: ЭВОЛЮЦИЯ                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Проект: 100K LOC, 20 модулей                                   │
│                                                                 │
│  Эра          │ Clean Build │ Incremental │ Технологии          │
│  ─────────────┼─────────────┼─────────────┼────────────────────  │
│  Ant (2010)   │ 10 мин      │ 5 мин       │ Однопоточно          │
│  ADT (2013)   │ 8 мин       │ 3 мин       │ Eclipse builder      │
│  Gradle 2.x   │ 5 мин       │ 2 мин       │ Daemon               │
│  Gradle 4.x   │ 3 мин       │ 45 сек      │ +Build Cache         │
│  Gradle 7.x   │ 2 мин       │ 20 сек      │ +Config Cache        │
│  Gradle 8.x   │ 1.5 мин     │ 10 сек      │ +Parallel, KTS       │
│                                                                 │
│  Улучшение: 85% для clean, 97% для incremental                  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## AGP Roadmap: Что впереди

### AGP 9.0 (2025)

```kotlin
// Ключевые изменения AGP 9.0

// 1. Новые DSL-интерфейсы (старые removed)
android {
    // Некоторые deprecated API будут удалены
    // Проверьте warnings заранее!
}

// 2. Требуется Gradle 9.0+
// gradle-wrapper.properties
distributionUrl=https://services.gradle.org/distributions/gradle-9.0-bin.zip

// 3. Убрана поддержка proguard-android.txt
// Миграция на proguard-android-optimize.txt
proguardFiles(
    getDefaultProguardFile("proguard-android-optimize.txt"),  // ✓ Правильно
    // getDefaultProguardFile("proguard-android.txt"),        // ✗ Убрано
)

// 4. Variant API changes
// Deprecated API → New API migration
```

---

## Сравнительная таблица

| Критерий | Ant | Eclipse ADT | Gradle (early) | Gradle (modern) |
|----------|-----|-------------|----------------|-----------------|
| **Год** | 2008 | 2009 | 2013 | 2020+ |
| **Конфигурация** | XML | GUI + XML | Groovy DSL | Kotlin DSL |
| **Зависимости** | Manual JARs | Manual JARs | Maven repos | Version Catalogs |
| **CLI = IDE** | Нет | Нет | Да | Да |
| **Инкрементальность** | Нет | Частичная | Да | + Cache |
| **Build Variants** | Нет | Нет | Да | Да + Compose |
| **Время сборки** | Очень долго | Долго | Терпимо | Быстро |
| **Кривая обучения** | Высокая | Средняя | Средняя | Средняя |

---

## Проверь себя

<details>
<summary>1. Почему Google перешёл с Ant на Gradle?</summary>

**Ответ:** Главные причины:
1. **Разрыв IDE/CLI** — сборка в Eclipse отличалась от сборки через Ant, что создавало проблемы на CI
2. **Декларативный DSL** — Gradle позволяет описать ЧТО нужно, а не КАК это сделать
3. **Управление зависимостями** — интеграция с Maven-репозиториями вместо ручного копирования JAR
4. **Build variants** — возможность создавать разные варианты сборки (debug/release, flavors)
5. **Инкрементальная сборка** — пересборка только изменённых частей

</details>

<details>
<summary>2. В чём разница между `compile` и `implementation`?</summary>

**Ответ:**
- **compile** (deprecated) — зависимость экспортируется транзитивно всем, кто зависит от модуля
- **implementation** — зависимость не экспортируется, видна только внутри модуля

`implementation` ускоряет сборку, потому что изменения во внутренних зависимостях не вызывают перекомпиляцию зависимых модулей.

</details>

<details>
<summary>3. Что делает Configuration Cache?</summary>

**Ответ:** Configuration Cache кэширует результат фазы конфигурации Gradle. При повторных сборках Gradle пропускает конфигурацию проекта и сразу переходит к выполнению задач. Это особенно полезно для больших проектов с множеством модулей, где конфигурация может занимать значительное время.

</details>

<details>
<summary>4. Зачем нужны Version Catalogs (libs.versions.toml)?</summary>

**Ответ:** Version Catalogs решают несколько проблем:
1. **Единый источник версий** — все версии в одном файле
2. **Type-safe доступ** — `libs.retrofit` вместо строки "com.squareup.retrofit2:retrofit:2.9.0"
3. **Bundles** — группировка связанных зависимостей
4. **Автодополнение** — IDE подсказывает доступные зависимости
5. **Dependency updates** — легче обновлять версии централизованно

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Ant был хорошим build tool" | Ant требовал императивного описания КАЖДОГО шага сборки. Gradle декларативно описывает ЧТО нужно, а КАК — определяет AGP. Это сократило build scripts в 10+ раз |
| "Eclipse ADT был удобнее Android Studio" | ADT не имел: Gradle поддержки, build variants, instant run, APK analyzer, Memory Profiler. AS изначально строился с учётом современных практик CI/CD |
| "Groovy DSL устарел" | Kotlin DSL рекомендуется, но Groovy DSL полностью поддерживается. Для простых проектов Groovy короче. Kotlin DSL выигрывает в type safety и IDE support |
| "Configuration Cache ломает многие плагины" | В 2025 большинство популярных плагинов совместимы. Проверить: `./gradlew --configuration-cache-problems=warn`. Несовместимые плагины — повод для обновления или замены |
| "KSP полностью заменил kapt" | KSP быстрее (до 2x), но поддерживает не все annotation processors. Room, Dagger/Hilt — работают с KSP. Некоторые legacy библиотеки требуют kapt |
| "AGP версия = AS версия" | AGP и Android Studio версионируются независимо. AGP 8.x работает с разными версиями AS. Compatibility matrix в документации определяет совместимость |
| "Convention Plugins сложные" | Convention Plugins — это обычные Gradle плагины в отдельном project. Они проще buildSrc: инкрементальная компиляция, Configuration Cache support, sharing между проектами |
| "D8/R8 одинаковые" | D8 — dexer (java bytecode → DEX), R8 — optimizer + shrinker + D8. R8 заменил ProGuard + D8 в одном проходе, что быстрее и оптимальнее |
| "Version Catalogs не нужны для маленьких проектов" | Даже для single-module проекта Version Catalogs дают: type-safe access (libs.retrofit), автодополнение IDE, будущую готовность к multi-module |
| "Incremental builds не работают" | Инкрементальные сборки работают при соблюдении правил: не использовать buildSrc с частыми изменениями, не invalidate caches вручную, использовать Configuration Cache |

---

## CS-фундамент

| CS-концепция | Применение в Android Build Evolution |
|--------------|--------------------------------------|
| **Declarative vs Imperative** | Эволюция от Ant (императивный: каждый шаг описан) к Gradle (декларативный: описание целей). Декларативность упрощает maintainability и оптимизацию |
| **Build Graph (DAG)** | Gradle строит directed acyclic graph задач. Это позволяет: параллельное выполнение, caching, incremental builds. Ant не имел графа — линейное выполнение |
| **Incremental Computation** | Инкрементальные сборки пересчитывают только changed inputs → affected outputs. Requires: input/output annotations, deterministic tasks, proper caching |
| **Content-Addressable Storage** | Build cache использует content hashing: hash(inputs) → cached output. Одинаковые inputs гарантируют одинаковый output (reproducibility) |
| **Configuration as Code** | Kotlin DSL превращает build scripts в type-safe code: компиляция, автодополнение, рефакторинг. Groovy DSL — dynamic, ошибки в runtime |
| **Plugin Architecture** | Extensibility через plugins вместо monolithic tool. AGP — набор плагинов (application, library, test). Convention Plugins — user-defined extensions |
| **Lazy Evaluation** | Gradle использует lazy properties: значение вычисляется только при необходимости. Это ускоряет конфигурацию (не все tasks configured) |
| **Two-Phase Build** | Разделение Configuration и Execution фаз. Configuration Cache кэширует первую фазу. Понимание фаз критично для оптимизации |
| **Bytecode Transformation** | D8/R8 работают на уровне bytecode, не source code. Это позволяет: optimization, desugaring, minification без доступа к исходникам |
| **Ahead-of-Time Compilation** | ART использует AOT compilation (при установке) vs Dalvik JIT (при выполнении). Build pipeline оптимизирует DEX для обоих сценариев |

---

## Связи

**Основы:**
- [[android-overview]] — общий обзор Android-разработки
- [[android-gradle-fundamentals]] — глубокое погружение в Gradle и AGP

**Сборка:**
- [[android-compilation-pipeline]] — как код превращается в APK
- [[android-proguard-r8]] — code shrinking и obfuscation
- [[android-apk-aab]] — форматы пакетов

**Структура:**
- [[android-project-structure]] — организация Android-проекта
- [[android-dependencies]] — управление зависимостями

---

## Источники

- [Android Studio's 10 Year Anniversary - Android Developers Blog](https://android-developers.googleblog.com/2025/01/android-studios-10-year-anniversary.html)
- [Gradle build overview - Android Developers](https://developer.android.com/build/gradle-build-overview)
- [Configure your build - Android Developers](https://developer.android.com/build)
- [Android Gradle Plugin release notes](https://developer.android.com/build/releases/gradle-plugin)
- [Past Android Gradle plugin releases](https://developer.android.com/build/releases/past-releases)
- [Gradle Documentation](https://docs.gradle.org/current/userguide/userguide.html)
- [The path to DX deprecation - Android Developers Blog](https://android-developers.googleblog.com/2020/02/the-path-to-dx-deprecation.html)

---

*Проверено: 2026-01-09 | На основе официальной документации Android и Gradle*
