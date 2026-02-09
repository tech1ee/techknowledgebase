---
title: "KMP Source Sets: Организация кода по платформам"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - source-sets
  - dependencies
  - gradle
  - type/concept
  - level/beginner
related:
  - "[[kmp-project-structure]]"
  - "[[kmp-expect-actual]]"
  - "[[kmp-getting-started]]"
cs-foundations:
  - "[[module-systems]]"
  - "[[dependency-resolution]]"
  - "[[compilation-pipeline]]"
  - "[[type-systems-theory]]"
status: published
---

# KMP Source Sets: организация кода для разных платформ

> **TL;DR:** Source set — папка с кодом + dependencies + compiler options. commonMain для всего общего, platformMain для платформо-специфичного. Dependencies добавляются через `sourceSets { commonMain.dependencies { } }`. Иерархия: platform видит common, common НЕ видит platform. Default hierarchy template автоматически создаёт intermediate source sets (iosMain, appleMain, nativeMain). dependsOn связывает source sets в иерархию.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **KMP Project Structure** | Понимание targets и структуры проекта | [[kmp-project-structure]] |
| **Gradle basics** | Конфигурация build.gradle.kts | Gradle docs |
| **Module systems** | Понимание encapsulation, visibility | [[module-systems]] |
| **Dependency resolution** | Как разрешаются зависимости | [[dependency-resolution]] |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|----------|---------------------|
| **Source Set** | Набор файлов + dependencies + compiler options | **Чемодан для поездки** — вещи + список того, что взять |
| **commonMain** | Source set для всех платформ | **Универсальный набор** — подходит везде |
| **platformMain** | Source set для одной платформы (androidMain, iosMain) | **Специальное снаряжение** — только для конкретного места |
| **dependsOn** | Связь между source sets в иерархии | **Наследование** — дочерний видит родительский |
| **implementation** | Dependency scope — внутренняя зависимость | **Личные вещи** — не показываем другим модулям |
| **api** | Dependency scope — публичная зависимость | **Визитка** — показываем всем кто использует наш модуль |
| **Default Hierarchy Template** | Автогенерация intermediate source sets | **Автопилот** — сам создаёт нужные папки |
| **Intermediate Source Set** | Shared между subset'ом платформ | **Региональный** — между глобальным и локальным |

---

## Почему Source Sets устроены именно так

### Фундаментальная проблема: разные API на разных платформах

На разных платформах **одни и те же концепции реализованы по-разному**:

```kotlin
// Задача: получить UUID

// На JVM:
java.util.UUID.randomUUID().toString()

// На iOS:
platform.Foundation.NSUUID().UUIDString()

// На JS:
crypto.randomUUID()  // или polyfill
```

**Проблема:** Как написать код, который:
1. Использует правильную реализацию на каждой платформе
2. Предоставляет единый интерфейс для common кода

### Решение: иерархия видимости

Source Sets реализуют **односторонний visibility**:

```
                  ┌────────────────┐
                  │  commonMain    │  ← НЕ видит platform code
                  │                │     Только pure Kotlin
                  │  fun getUUID() │     (expect declaration)
                  └───────┬────────┘
                          │ dependsOn (видит вверх)
          ┌───────────────┼───────────────┐
          │               │               │
   ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
   │ androidMain │ │   iosMain   │ │   jsMain    │
   │             │ │             │ │             │
   │ ВИДИТ:      │ │ ВИДИТ:      │ │ ВИДИТ:      │
   │ - common    │ │ - common    │ │ - common    │
   │ - java.*    │ │ - platform.*│ │ - js APIs   │
   │             │ │             │ │             │
   │ actual fun  │ │ actual fun  │ │ actual fun  │
   │ getUUID()   │ │ getUUID()   │ │ getUUID()   │
   └─────────────┘ └─────────────┘ └─────────────┘
```

### Почему именно dependsOn, а не include или import

**dependsOn** — это **направленная связь в compile-time graph**:

```
dependsOn(X) означает:
────────────────────────────────────────────────────────
1. Я ВИЖУ весь код из X
2. Мои dependencies ДОБАВЛЯЮТСЯ к dependencies X
3. При компиляции X компилируется РАНЬШЕ меня
4. Я должен предоставить actual для всех expect из X
```

Это отличается от:
- **include** — просто добавить файлы (нет dependency ordering)
- **import** — runtime загрузка (а не compile-time)

### Почему intermediate source sets

Без intermediate source sets нужно **дублировать код**:

```kotlin
// БЕЗ iosMain intermediate source set:

// iosArm64Main/kotlin/Utils.kt
fun getDeviceInfo(): String = UIDevice.currentDevice.name

// iosX64Main/kotlin/Utils.kt (ДУБЛИКАТ!)
fun getDeviceInfo(): String = UIDevice.currentDevice.name

// iosSimulatorArm64Main/kotlin/Utils.kt (ЕЩЁ ДУБЛИКАТ!)
fun getDeviceInfo(): String = UIDevice.currentDevice.name
```

**Intermediate source set** решает это:

```kotlin
// С iosMain:

// iosMain/kotlin/Utils.kt (ОДИН РАЗ)
fun getDeviceInfo(): String = UIDevice.currentDevice.name

// iosArm64Main, iosX64Main, iosSimulatorArm64Main — наследуют через dependsOn
```

### Type system connection

Source set hierarchy связана с **type system constraints**:

```kotlin
// В commonMain доступны только типы, которые существуют НА ВСЕХ платформах

// ✅ commonMain
val text: String      // String есть везде
val number: Int       // Int есть везде
val list: List<T>     // List есть везде

// ❌ commonMain (compilation error)
val file: java.io.File  // File есть только на JVM
val date: NSDate         // NSDate есть только на Apple

// ✅ jvmMain
val file: java.io.File  // OK — JVM target

// ✅ iosMain
val date: NSDate        // OK — Apple target
```

> **CS-фундамент:** Детали в [[module-systems]] (encapsulation boundaries) и [[type-systems-theory]] (platform-specific types).

---

## Что такое Source Set

### Структура Source Set

```
┌─────────────────────────────────────────────────────────────┐
│                     SOURCE SET = 3 КОМПОНЕНТА                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. ИСХОДНЫЕ ФАЙЛЫ                                          │
│     src/<sourceSetName>/kotlin/                             │
│     src/<sourceSetName>/resources/                          │
│                                                             │
│  2. DEPENDENCIES                                            │
│     Библиотеки которые можно использовать                   │
│     implementation(), api(), compileOnly()                  │
│                                                             │
│  3. COMPILER OPTIONS                                        │
│     Настройки компилятора для этого source set             │
│     languageVersion, apiVersion, freeCompilerArgs           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Стандартные Source Sets

```
src/
├── commonMain/kotlin/         # Код для ВСЕХ платформ
├── commonTest/kotlin/         # Тесты для common кода
│
├── androidMain/kotlin/        # Android-специфичный код
├── androidUnitTest/kotlin/    # Android unit tests
├── androidInstrumentedTest/   # Android instrumentation tests
│
├── iosMain/kotlin/            # iOS (все архитектуры)
├── iosTest/kotlin/            # iOS tests
│
├── iosArm64Main/kotlin/       # iOS Device only
├── iosX64Main/kotlin/         # iOS Intel Simulator only
├── iosSimulatorArm64Main/     # iOS Apple Silicon Simulator only
│
├── jvmMain/kotlin/            # JVM/Desktop
├── jvmTest/kotlin/            # JVM tests
│
├── jsMain/kotlin/             # JavaScript
└── jsTest/kotlin/             # JS tests
```

---

## Иерархия Source Sets

### Правила видимости

```
┌─────────────────────────────────────────────────────────────┐
│                    ПРАВИЛА ВИДИМОСТИ                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Platform → видит → Common                               │
│     androidMain может использовать код из commonMain        │
│     iosMain может использовать код из commonMain            │
│                                                             │
│  ❌ Common → НЕ видит → Platform                            │
│     commonMain НЕ может импортировать из androidMain        │
│     commonMain НЕ может импортировать из iosMain            │
│                                                             │
│  ✅ Platform → использует → Platform APIs                   │
│     androidMain может использовать android.content.Context  │
│     iosMain может использовать platform.UIKit.UIDevice      │
│                                                             │
│  ❌ Common → НЕ использует → Platform APIs                  │
│     commonMain НЕ может использовать java.io.File           │
│     commonMain НЕ может использовать NSUserDefaults         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Визуализация иерархии

```
                            commonMain
                                │
                    ┌───────────┼───────────┐
                    │           │           │
                nativeMain    jvmMain     jsMain
                    │           │           │
        ┌───────────┴───────┐   │           │
        │                   │   │           │
     appleMain          linuxMain  │        │
        │                   │      │        │
    ┌───┴────┐             │      │        │
    │        │             │      │        │
 iosMain  macosMain        │  androidMain  │
    │        │             │      │        │
 ┌──┴──┐  ┌──┴──┐         │      │        │
 │  │  │  │     │         │      │        │
iosX64 iosArm64 macosX64 linuxX64 android js
       iosSimulatorArm64  macosArm64
```

### dependsOn механизм

```kotlin
kotlin {
    // Targets
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        // ═══════════════════════════════════════════════════
        // АВТОМАТИЧЕСКИЕ dependsOn (default hierarchy template)
        // ═══════════════════════════════════════════════════

        // iosMain автоматически:
        // - dependsOn(commonMain)
        // - является родителем для iosX64Main, iosArm64Main, iosSimulatorArm64Main

        // ═══════════════════════════════════════════════════
        // РУЧНОЙ dependsOn для кастомных source sets
        // ═══════════════════════════════════════════════════

        // Создаём кастомный source set
        val mobileMain by creating {
            dependsOn(commonMain.get())
        }

        // Подключаем к нему platform source sets
        androidMain.get().dependsOn(mobileMain)
        iosMain.get().dependsOn(mobileMain)

        // Теперь код в mobileMain доступен и для Android, и для iOS
    }
}
```

---

## Конфигурация Dependencies

### Добавление зависимостей

```kotlin
kotlin {
    sourceSets {
        // ═══════════════════════════════════════════════════
        // COMMON DEPENDENCIES — для всех платформ
        // ═══════════════════════════════════════════════════
        commonMain.dependencies {
            // Coroutines — автоматически подберёт правильную версию
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")

            // Serialization
            implementation("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")

            // Ktor client (core)
            implementation("io.ktor:ktor-client-core:3.0.3")

            // DateTime
            implementation("org.jetbrains.kotlinx:kotlinx-datetime:0.6.1")
        }

        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
        }

        // ═══════════════════════════════════════════════════
        // ANDROID DEPENDENCIES
        // ═══════════════════════════════════════════════════
        androidMain.dependencies {
            // Ktor engine для Android
            implementation("io.ktor:ktor-client-okhttp:3.0.3")

            // Android-specific coroutines
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.9.0")

            // AndroidX
            implementation("androidx.core:core-ktx:1.15.0")
        }

        // ═══════════════════════════════════════════════════
        // iOS DEPENDENCIES
        // ═══════════════════════════════════════════════════
        iosMain.dependencies {
            // Ktor engine для iOS
            implementation("io.ktor:ktor-client-darwin:3.0.3")
        }

        // ═══════════════════════════════════════════════════
        // JVM DEPENDENCIES
        // ═══════════════════════════════════════════════════
        jvmMain.dependencies {
            implementation("io.ktor:ktor-client-cio:3.0.3")
        }

        // ═══════════════════════════════════════════════════
        // JS DEPENDENCIES
        // ═══════════════════════════════════════════════════
        jsMain.dependencies {
            implementation("io.ktor:ktor-client-js:3.0.3")
        }
    }
}
```

### Dependency Scopes

```kotlin
sourceSets {
    commonMain.dependencies {
        // ═══════════════════════════════════════════════════
        // implementation — внутренняя зависимость
        // НЕ видна модулям, которые зависят от нашего
        // ═══════════════════════════════════════════════════
        implementation("io.ktor:ktor-client-core:3.0.3")

        // ═══════════════════════════════════════════════════
        // api — публичная зависимость
        // ВИДНА модулям, которые зависят от нашего
        // Используйте когда dependency — часть вашего публичного API
        // ═══════════════════════════════════════════════════
        api("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")

        // ═══════════════════════════════════════════════════
        // compileOnly — только для компиляции
        // НЕ включается в runtime
        // ═══════════════════════════════════════════════════
        compileOnly("org.jetbrains.compose.runtime:runtime:1.7.3")

        // ═══════════════════════════════════════════════════
        // runtimeOnly — только для runtime
        // НЕ доступна при компиляции
        // ═══════════════════════════════════════════════════
        runtimeOnly("org.slf4j:slf4j-simple:2.0.9")
    }
}
```

### Альтернативный синтаксис

```kotlin
// Top-level dependencies block
dependencies {
    // Паттерн: <sourceSetName><DependencyScope>
    commonMainImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
    commonMainApi("org.jetbrains.kotlinx:kotlinx-serialization-json:1.7.3")

    androidMainImplementation("io.ktor:ktor-client-okhttp:3.0.3")
    iosMainImplementation("io.ktor:ktor-client-darwin:3.0.3")

    commonTestImplementation(kotlin("test"))
}
```

---

## Default Hierarchy Template

### Как работает

```kotlin
kotlin {
    // При объявлении targets...
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    // ...plugin автоматически создаёт intermediate source sets:
    // - iosMain (shared между всеми iOS targets)
    // - appleMain (если добавить macOS)
    // - nativeMain (shared между всеми native targets)

    // Type-safe accessors уже доступны:
    sourceSets {
        iosMain.dependencies {  // ✅ Работает автоматически
            implementation("io.ktor:ktor-client-darwin:3.0.3")
        }
    }
}
```

### Какие source sets создаются автоматически

| Targets | Автоматически создаётся |
|---------|------------------------|
| iosX64 + iosArm64 | iosMain |
| iosX64 + macosX64 | appleMain, nativeMain |
| jvm + android | - (нет shared, кроме common) |
| js + wasmJs | - (нет shared) |
| linuxX64 + mingwX64 | nativeMain |

### Отключение Default Template

```properties
# gradle.properties
kotlin.mpp.applyDefaultHierarchyTemplate=false
```

```kotlin
// build.gradle.kts — ручная конфигурация
kotlin {
    iosX64()
    iosArm64()

    sourceSets {
        // Ручное создание intermediate source set
        val iosMain by creating {
            dependsOn(commonMain.get())
        }

        val iosX64Main by getting {
            dependsOn(iosMain)
        }

        val iosArm64Main by getting {
            dependsOn(iosMain)
        }
    }
}
```

---

## Compiler Options

### Конфигурация для source set

```kotlin
kotlin {
    sourceSets {
        commonMain {
            // Compiler options для этого source set
            compilerOptions {
                // Версия языка
                languageVersion.set(KotlinVersion.KOTLIN_2_1)

                // API version
                apiVersion.set(KotlinVersion.KOTLIN_2_1)

                // Free compiler args
                freeCompilerArgs.add("-Xexpect-actual-classes")
            }
        }
    }

    // Или глобально для всех source sets
    compilerOptions {
        freeCompilerArgs.add("-opt-in=kotlin.RequiresOptIn")
    }
}
```

### Target-specific options

```kotlin
kotlin {
    androidTarget {
        compilations.all {
            compilerOptions.configure {
                jvmTarget.set(JvmTarget.JVM_17)
            }
        }
    }

    jvm {
        compilations.all {
            compilerOptions.configure {
                jvmTarget.set(JvmTarget.JVM_17)
            }
        }
    }
}
```

---

## Практические паттерны

### Pattern 1: Shared между mobile платформами

```kotlin
kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        // Кастомный source set для mobile-only кода
        val mobileMain by creating {
            dependsOn(commonMain.get())
            dependencies {
                // Dependencies только для mobile
                implementation("io.github.nickhsine:touch-id-checker:1.0.0")
            }
        }

        androidMain.get().dependsOn(mobileMain)
        iosMain.get().dependsOn(mobileMain)
    }
}
```

**Структура папок:**

```
src/
├── commonMain/kotlin/         # Код для всех (mobile + desktop + web)
├── mobileMain/kotlin/         # Код только для mobile (Android + iOS)
│   └── BiometricAuth.kt       # expect для biometric
├── androidMain/kotlin/        # Android-specific
│   └── BiometricAuth.android.kt
└── iosMain/kotlin/            # iOS-specific
    └── BiometricAuth.ios.kt
```

### Pattern 2: Resources per platform

```kotlin
kotlin {
    sourceSets {
        commonMain {
            resources.srcDir("src/commonMain/resources")
        }

        androidMain {
            // Android использует res/ folder
        }

        iosMain {
            resources.srcDir("src/iosMain/resources")
        }
    }
}
```

### Pattern 3: Test source sets

```kotlin
kotlin {
    sourceSets {
        commonTest.dependencies {
            implementation(kotlin("test"))
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
            implementation("io.kotest:kotest-assertions-core:5.9.1")
        }

        androidUnitTest.dependencies {
            implementation("junit:junit:4.13.2")
            implementation("io.mockk:mockk-android:1.13.13")
        }

        // Android instrumented tests
        val androidInstrumentedTest by getting {
            dependencies {
                implementation("androidx.test:core:1.6.1")
                implementation("androidx.test.espresso:espresso-core:3.6.1")
            }
        }

        iosTest.dependencies {
            // iOS-specific test dependencies
        }
    }
}
```

---

## Dependency Alignment

### Автоматическое выравнивание версий

```kotlin
// Если в commonMain добавить coroutines 1.9.0,
// все platform source sets получат совместимые версии автоматически

sourceSets {
    commonMain.dependencies {
        implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.9.0")
        // Android получит coroutines-android:1.9.0
        // iOS получит coroutines-core-iosx64:1.9.0
    }
}
```

### BOM для версий

```kotlin
sourceSets {
    commonMain.dependencies {
        implementation(platform("io.ktor:ktor-bom:3.0.3"))
        implementation("io.ktor:ktor-client-core")  // Версия из BOM
        implementation("io.ktor:ktor-client-content-negotiation")
    }

    androidMain.dependencies {
        implementation("io.ktor:ktor-client-okhttp")  // Версия из BOM
    }

    iosMain.dependencies {
        implementation("io.ktor:ktor-client-darwin")  // Версия из BOM
    }
}
```

---

## Типичные ошибки

### 1. Зависимость в неправильном source set

```kotlin
// ❌ НЕПРАВИЛЬНО — Android dependency в common
sourceSets {
    commonMain.dependencies {
        implementation("androidx.core:core-ktx:1.15.0")  // Не скомпилируется для iOS!
    }
}

// ✅ ПРАВИЛЬНО
sourceSets {
    androidMain.dependencies {
        implementation("androidx.core:core-ktx:1.15.0")
    }
}
```

### 2. Пропущенный dependsOn

```kotlin
// ❌ НЕПРАВИЛЬНО — orphan source set
sourceSets {
    val mobileMain by creating {
        // Забыли dependsOn!
    }
}

// ✅ ПРАВИЛЬНО
sourceSets {
    val mobileMain by creating {
        dependsOn(commonMain.get())
    }
}
```

### 3. Несовместимые версии dependencies

```kotlin
// ❌ НЕПРАВИЛЬНО — разные версии ktor
sourceSets {
    commonMain.dependencies {
        implementation("io.ktor:ktor-client-core:2.3.0")
    }
    androidMain.dependencies {
        implementation("io.ktor:ktor-client-okhttp:3.0.3")  // Несовместимо!
    }
}

// ✅ ПРАВИЛЬНО — одинаковые версии или BOM
sourceSets {
    commonMain.dependencies {
        implementation(platform("io.ktor:ktor-bom:3.0.3"))
        implementation("io.ktor:ktor-client-core")
    }
    androidMain.dependencies {
        implementation("io.ktor:ktor-client-okhttp")
    }
}
```

### 4. Неправильный getting vs creating

```kotlin
// ❌ НЕПРАВИЛЬНО — creating для существующего source set
sourceSets {
    val commonMain by creating { }  // Ошибка! commonMain уже существует
}

// ✅ ПРАВИЛЬНО
sourceSets {
    val commonMain by getting { }  // getting для существующих
    val customMain by creating { } // creating для новых
}
```

---

## Кто использует и реальные примеры

| Компания | Source Set паттерн | Описание |
|----------|-------------------|----------|
| **Ktor** | Platform-specific engines | commonMain: core, androidMain: OkHttp, iosMain: Darwin |
| **SQLDelight** | Platform-specific drivers | commonMain: queries, platform: SqlDriver |
| **Compose MP** | Shared UI + platform specifics | commonMain: Composables, platform: Window management |

---

## Мифы и заблуждения о Source Sets

### ❌ "commonMain = общие утилиты, всё остальное в platform"

**Реальность:** В хорошо спроектированном KMP проекте **60-80% кода в commonMain**:
- Data models
- Repository interfaces
- Use cases / Interactors
- Network DTOs
- Business logic

Platform source sets содержат только **то, что невозможно сделать в common**:
- Platform API calls (sensors, biometrics)
- UI framework specifics
- Platform-specific libraries

### ❌ "Все dependencies должны быть multiplatform"

**Реальность:** Можно использовать **platform-specific libraries** в platform source sets:

```kotlin
sourceSets {
    androidMain.dependencies {
        // ✅ Android-only library — это нормально
        implementation("com.google.android.gms:play-services-auth:21.0.0")
    }

    iosMain.dependencies {
        // ✅ iOS-specific через cinterop тоже работает
    }
}
```

Multiplatform libraries нужны **только для commonMain**.

### ❌ "Test source sets наследуют все dependencies"

**Реальность:** Test source sets имеют **свои собственные dependencies**:

```kotlin
sourceSets {
    commonTest.dependencies {
        // Нужно явно добавить тестовые зависимости
        implementation(kotlin("test"))
        implementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")
    }
}
```

Test source sets видят код из main, но **не dependencies**.

### ❌ "implementation vs api не важно в KMP"

**Реальность:** Критически важно для multi-module проектов:

| Scope | Видимость | Когда использовать |
|-------|-----------|-------------------|
| `implementation` | Скрыт от dependents | Внутренняя реализация |
| `api` | Виден dependents | Часть публичного API |

Неправильное использование → compilation errors в зависимых модулях.

### ❌ "Можно создать произвольную иерархию"

**Реальность:** Иерархия должна **соответствовать реальности платформ**:

```kotlin
// ❌ НЕПРАВИЛЬНО — android и ios не имеют общего subset API
val mobileMain by creating {
    dependsOn(commonMain.get())
}
androidMain.get().dependsOn(mobileMain)
iosMain.get().dependsOn(mobileMain)

// В mobileMain нет platform APIs — только чистый Kotlin
// Это работает, но смысла мало

// ✅ ПРАВИЛЬНО — appleMain имеет смысл
val appleMain by creating {
    dependsOn(commonMain.get())
}
iosMain.get().dependsOn(appleMain)
macosMain.get().dependsOn(appleMain)

// В appleMain доступны Foundation, UIKit, etc.
```

### ❌ "Default Hierarchy Template всегда лучше"

**Реальность:** В **больших проектах** (70+ модулей) template может **замедлить Gradle sync**. В таких случаях ручная конфигурация быстрее.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Adding Dependencies](https://kotlinlang.org/docs/multiplatform/multiplatform-add-dependencies.html) | Official Doc | Полный гайд по dependencies |
| [Hierarchical Structure](https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html) | Official Doc | Default template и кастомные иерархии |
| [DSL Reference](https://kotlinlang.org/docs/multiplatform/multiplatform-dsl-reference.html) | Official Doc | Все настройки Gradle DSL |
| [Advanced Structure](https://kotlinlang.org/docs/multiplatform/multiplatform-advanced-project-structure.html) | Official Doc | Продвинутые концепции |

### CS-фундамент

| Концепция | Материал | Почему важно |
|-----------|----------|--------------|
| Module Systems | [[module-systems]] | Visibility, encapsulation boundaries |
| Dependency Resolution | [[dependency-resolution]] | Transitive deps, version alignment |
| Type Systems | [[type-systems-theory]] | Platform-specific types constraints |
| Compilation Pipeline | [[compilation-pipeline]] | Per-target compilation |

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, Gradle 8.5+*
