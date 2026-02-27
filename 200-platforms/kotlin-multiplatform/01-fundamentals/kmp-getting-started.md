---
title: "KMP Getting Started: Первый проект за 30 минут"
created: 2026-01-03
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - getting-started
  - setup
  - beginner
  - type/concept
  - level/beginner
related:
  - "[[kmp-project-structure]]"
  - "[[kmp-expect-actual]]"
  - "[[kotlin-overview]]"
cs-foundations:
  - "[[compilation-pipeline]]"
  - "[[build-systems-theory]]"
  - "[[dependency-resolution]]"
status: published
reading_time: 38
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# KMP Getting Started: от нуля до работающего проекта

> **TL;DR:** Для старта KMP нужны: IntelliJ IDEA 2025.2.2+ или Android Studio Otter 2025.2.1+ с KMP плагином. Создать проект через [KMP Wizard](https://kmp.jetbrains.com) или IDE wizard. Для iOS нужен Mac + Xcode (запустить хотя бы раз). Preflight checks в IDE автоматически проверят окружение. Первый проект — shared data layer, не UI. Android-разработчики адаптируются за 1-2 недели.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Kotlin basics** | KMP = Kotlin; нужно знать язык на базовом уровне | [[kotlin-overview]] |
| **Gradle basics** | KMP проекты конфигурируются через Gradle | Gradle docs |
| **Android или iOS опыт** | Понимание хотя бы одной целевой платформы | Android/iOS docs |
| **Compilation pipeline** | Понять как Kotlin компилируется в разные платформы | [[compilation-pipeline]] |
| **Build systems** | Как Gradle управляет зависимостями и задачами | [[build-systems-theory]] |

### Для кого этот материал

| Уровень | Что получите |
|---------|--------------|
| **Полный новичок** | Работающий KMP проект за 30 минут с пониманием каждого шага |
| **Android-разработчик** | Быстрый старт + понимание iOS-специфики |
| **iOS-разработчик** | Понимание как интегрировать Kotlin в Swift-проект |

---

## Терминология для новичков

| Термин | Что это | Аналогия из жизни |
|--------|----------|---------------------|
| **KMP Wizard** | Веб-инструмент JetBrains для генерации KMP проекта | **Конструктор IKEA** — выбираешь что нужно, получаешь готовый набор |
| **Preflight Checks** | Автопроверка окружения в IDE (Java, SDK, Xcode) | **Техосмотр** перед поездкой — всё ли работает |
| **Target** | Целевая платформа (Android, iOS, Desktop, Web) | **Пункт назначения** — куда едем |
| **Source Set** | Папка с кодом для конкретной платформы | **Чемодан** для конкретной страны |
| **commonMain** | Код, работающий на всех платформах | **Универсальный адаптер** — подходит везде |
| **shared module** | Gradle-модуль с общим кодом | **Общий склад** — берут все платформы |
| **K2 mode** | Новый компилятор Kotlin 2.0 (быстрее) | **Турбо-режим** — компилирует в 2x быстрее |
| **Direct Integration** | Подключение iOS framework напрямую | **Прямой рейс** — без пересадок |
| **CocoaPods** | Менеджер зависимостей для iOS | **Посылочная служба** для iOS-библиотек |
| **Framework** | Скомпилированный Kotlin код для iOS | **Полуфабрикат** — готовый модуль для iOS-команды |

---

## Теоретические основы

### Формальное определение

> **Toolchain** — совокупность инструментов компиляции, линковки и упаковки, необходимых для преобразования исходного кода в исполняемый артефакт целевой платформы (Aho et al., 2006).

В контексте KMP каждый target требует собственного toolchain: Android SDK для JVM bytecode, Xcode/LLVM для iOS native binary, Node.js для JavaScript.

### Теоретическая модель: Build System как DAG

Создание KMP-проекта инициализирует **направленный ациклический граф задач** (Directed Acyclic Graph), где каждая вершина — задача компиляции, а рёбра — зависимости между ними (Feldman, 1979):

```
:shared:compileCommonMainKotlin → :shared:compileAndroidMainKotlin → :composeApp:assembleDebug
                                → :shared:compileIosMainKotlin → embedAndSignAppleFramework
                                → :shared:compileJsMainKotlin → jsBrowserProductionWebpack
```

Gradle реализует этот граф через механизм **task avoidance** и **incremental compilation** — см. [[build-systems-theory]].

### Историческая справка: эволюция IDE для мультиплатформенной разработки

| Год | IDE / Инструмент | Целевые платформы | Подход к настройке |
|-----|-----------------|-------------------|-------------------|
| 2003 | Eclipse + Android ADT | Android | Ручная конфигурация SDK |
| 2013 | Android Studio (IntelliJ) | Android | Gradle + SDK Manager |
| 2014 | Xcode 6 + Swift | iOS | Xcode-integrated toolchain |
| 2017 | IntelliJ + KMP plugin | Android + JVM | Experimental, ручная настройка |
| 2023 | Fleet / AS + KMP | Android + iOS + Desktop + Web | Preflight Checks, KMP Wizard |

### Концепция Preflight Verification

Preflight Checks в KMP IDE — реализация паттерна **Environment Validation** из теории непрерывной интеграции (Humble, Farley, 2010). Система проверяет выполнимость инвариантов:

- **JAVA_HOME** → JDK доступен для Kotlin/JVM компиляции
- **ANDROID_HOME** → Android SDK доступен для AGP
- **Xcode** → LLVM toolchain доступен для Kotlin/Native → iOS

> **Связь с CS-фундаментом:** Каждый toolchain соответствует определённому этапу [[compilation-pipeline]]: frontend (K2) общий, backend — платформо-зависимый. [[build-systems-theory]] объясняет, как Gradle координирует параллельное выполнение задач для разных targets.

---

## Почему настройка KMP требует понимания compilation pipeline

### Что происходит при создании проекта

Когда вы создаёте KMP проект, Gradle настраивает **три разных компиляционных pipeline**:

```
                    build.gradle.kts
                          │
       ┌──────────────────┼──────────────────┐
       │                  │                  │
       ▼                  ▼                  ▼
    Kotlin/JVM       Kotlin/Native       Kotlin/JS
       │                  │                  │
    [kotlinc-jvm]     [kotlinc-native]   [kotlinc-js]
       │                  │                  │
       ▼                  ▼                  ▼
   JVM Bytecode       LLVM IR          JavaScript
       │                  │                  │
       ▼                  ▼                  ▼
     Android            iOS              Browser
```

**Каждый target требует свой toolchain:**

| Target | Компилятор | Toolchain | Результат |
|--------|-----------|-----------|-----------|
| Android | Kotlin/JVM | Android SDK, ANDROID_HOME | .aar / .apk |
| iOS | Kotlin/Native | Xcode, Command Line Tools | .framework |
| Desktop | Kotlin/JVM | JDK | .jar / installer |
| Web | Kotlin/JS/WASM | Node.js (optional) | .js / .wasm |

### Почему нужен Xcode для iOS

Kotlin/Native **использует LLVM** — тот же backend, что и Swift/Clang. Но LLVM toolchain для Apple платформ **встроен в Xcode**:

```
Kotlin/Native Compiler
        │
        ▼
     LLVM IR
        │
        ▼
   Xcode LLVM ← [Вот почему Xcode обязателен]
        │
        ▼
  iOS Framework
```

**Без Xcode** нет LLVM для Apple → нет iOS сборки.

### Почему настройка ANDROID_HOME критична

Gradle plugin для Android (`com.android.application`) **ищет Android SDK по ANDROID_HOME**:

```kotlin
// Внутри Android Gradle Plugin
val sdkPath = System.getenv("ANDROID_HOME")
    ?: System.getenv("ANDROID_SDK_ROOT")
    ?: throw GradleException("SDK location not found")
```

**Без ANDROID_HOME:**
- AGP не найдёт SDK
- Не соберётся androidMain source set
- Даже commonMain не скомпилируется (нужны все targets)

### Почему первый запуск iOS долгий

При **первом запуске** Kotlin/Native:
1. Скачивает platform-specific libraries
2. Компилирует Kotlin stdlib в native code
3. Кэширует результат в `~/.konan/`

```bash
# Кэш Kotlin/Native (~2-3 GB)
~/.konan/
├── cache/              # Скомпилированные klibs
├── dependencies/       # LLVM, platform libs
└── kotlin-native-prebuilt-*/  # Компилятор
```

**Последующие сборки** используют кэш — значительно быстрее.

> **CS-фундамент:** Детали в [[compilation-pipeline]] (compiler phases) и [[build-systems-theory]] (dependency graph, task caching).

---

## Шаг 0: Проверка требований

### Минимальные требования

```
┌─────────────────────────────────────────────────────────────┐
│                 СИСТЕМНЫЕ ТРЕБОВАНИЯ                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  IDE (выбрать одну):                                        │
│  ├── IntelliJ IDEA 2025.2.2+                               │
│  └── Android Studio Otter 2025.2.1+                        │
│                                                             │
│  Kotlin: 2.1.20+ (текущая стабильная)                      │
│                                                             │
│  Java/JDK: JetBrains Runtime (JBR) рекомендуется           │
│                                                             │
│  Для Android-таргета:                                       │
│  └── Android SDK + ANDROID_HOME env variable               │
│                                                             │
│  Для iOS-таргета (ТОЛЬКО macOS):                           │
│  ├── macOS                                                  │
│  ├── Xcode (последняя версия)                              │
│  └── Xcode должен быть запущен хотя бы 1 раз!              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Environment Variables

**macOS/Linux** — добавить в `~/.zprofile` или `~/.bashrc`:

```bash
# Java
export JAVA_HOME=$(/usr/libexec/java_home)
export PATH=$JAVA_HOME/bin:$PATH

# Android SDK
export ANDROID_HOME=~/Library/Android/sdk
export PATH=$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin:$ANDROID_HOME/platform-tools:$PATH
```

**Windows (PowerShell)**:

```powershell
[Environment]::SetEnvironmentVariable('JAVA_HOME', 'C:\Program Files\Java\jdk-17', 'Machine')
[Environment]::SetEnvironmentVariable('ANDROID_HOME', 'C:\Users\<user>\AppData\Local\Android\Sdk', 'Machine')
```

---

## Шаг 1: Установка IDE и плагина

### Вариант A: IntelliJ IDEA

1. Скачать [IntelliJ IDEA](https://www.jetbrains.com/idea/) (Community или Ultimate)
2. Установить [Kotlin Multiplatform IDE plugin](https://plugins.jetbrains.com/plugin/14936-kotlin-multiplatform)
3. Включить K2 mode: **Settings → Languages & Frameworks → Kotlin → Enable K2 mode**

### Вариант B: Android Studio

1. Скачать [Android Studio](https://developer.android.com/studio) (Otter 2025.2.1+)
2. KMP плагин уже bundled, но проверить: **Settings → Plugins → Installed → Kotlin Multiplatform**
3. Включить K2 mode аналогично

### Проверка установки (Preflight Checks)

После установки плагина появится инструмент **Preflight Checks**:

```
┌─────────────────────────────────────────────────────────────┐
│              PROJECT ENVIRONMENT PREFLIGHT CHECKS            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ✅ Operating System: macOS 14.0                           │
│  ✅ Java: JetBrains Runtime 17.0.9                         │
│  ✅ Android SDK: API 34                                     │
│  ✅ Xcode: 15.4                                             │
│  ✅ Gradle: 8.5                                             │
│                                                             │
│  All checks passed! Ready to create KMP project.           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Как открыть:** Shift+Shift → поиск "preflight" или иконка самолёта в sidebar.

---

## Шаг 2: Создание проекта

### Способ 1: KMP Wizard (Рекомендуется для новичков)

1. Открыть [kmp.jetbrains.com](https://kmp.jetbrains.com)
2. Выбрать таргеты:
   - ✅ Android
   - ✅ iOS (если есть Mac)
   - ⬜ Desktop (опционально)
   - ⬜ Web (опционально)
3. Выбрать UI-подход:
   - **"Do not share UI"** — нативный UI (Compose + SwiftUI) ← рекомендуется для начала
   - **"Share UI"** — Compose Multiplatform везде
4. Скачать и распаковать проект
5. Открыть в IDE

**Почему Wizard лучше для начала:**
- Избегает "Gradle pain" — конфигурация уже готова
- Проверенный шаблон от JetBrains
- Минимум boilerplate

### Способ 2: IDE Wizard

1. **File → New → Project**
2. Выбрать **Kotlin Multiplatform** в левой панели
3. Настроить:
   - Project name
   - Location
   - JDK: выбрать **JetBrains Runtime (JBR)**
4. Выбрать таргеты (Android, iOS, Desktop, Web)
5. Для iOS выбрать: **Compose UI** или **SwiftUI (native)**
6. **Create**

```
┌─────────────────────────────────────────────────────────────┐
│                    NEW KMP PROJECT                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Name: MyKmpApp                                             │
│  Location: ~/Projects/MyKmpApp                              │
│  JDK: JetBrains Runtime 17 (recommended)                   │
│                                                             │
│  Targets:                                                   │
│  ☑ Android                                                  │
│  ☑ iOS                                                      │
│    ○ Compose Multiplatform UI                               │
│    ● Native SwiftUI (recommended for start)                │
│  ☐ Desktop                                                  │
│  ☐ Web                                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Шаг 3: Структура проекта

После создания проект выглядит так:

```
MyKmpApp/
├── shared/                        # 📦 ОБЩИЙ МОДУЛЬ
│   ├── src/
│   │   ├── commonMain/           # Код для ВСЕХ платформ
│   │   │   └── kotlin/
│   │   │       └── Greeting.kt   # Пример общего кода
│   │   ├── commonTest/           # Тесты для общего кода
│   │   ├── androidMain/          # Android-специфичный код
│   │   │   └── kotlin/
│   │   │       └── Platform.android.kt
│   │   └── iosMain/              # iOS-специфичный код
│   │       └── kotlin/
│   │           └── Platform.ios.kt
│   └── build.gradle.kts          # Конфигурация shared модуля
│
├── composeApp/                    # 📱 ANDROID ПРИЛОЖЕНИЕ
│   └── src/
│       └── androidMain/
│           └── kotlin/
│               └── MainActivity.kt
│
├── iosApp/                        # 🍎 iOS ПРИЛОЖЕНИЕ (Xcode)
│   ├── iosApp.xcodeproj
│   └── iosApp/
│       └── ContentView.swift
│
├── build.gradle.kts              # Корневой Gradle
├── settings.gradle.kts
└── gradle.properties
```

### Ключевые файлы

**shared/src/commonMain/kotlin/Greeting.kt** — пример общего кода:

```kotlin
class Greeting {
    private val platform = getPlatform()

    fun greet(): String {
        return "Hello, ${platform.name}!"
    }
}
```

**shared/src/commonMain/kotlin/Platform.kt** — expect declaration:

```kotlin
interface Platform {
    val name: String
}

expect fun getPlatform(): Platform
```

**shared/src/androidMain/kotlin/Platform.android.kt** — actual для Android:

```kotlin
class AndroidPlatform : Platform {
    override val name: String = "Android ${android.os.Build.VERSION.SDK_INT}"
}

actual fun getPlatform(): Platform = AndroidPlatform()
```

**shared/src/iosMain/kotlin/Platform.ios.kt** — actual для iOS:

```kotlin
import platform.UIKit.UIDevice

class IOSPlatform : Platform {
    override val name: String = UIDevice.currentDevice.systemName() + " " +
            UIDevice.currentDevice.systemVersion
}

actual fun getPlatform(): Platform = IOSPlatform()
```

---

## Шаг 4: Запуск проекта

### Android

1. Выбрать run configuration: **composeApp** (или **androidApp**)
2. Выбрать эмулятор или устройство
3. Нажать **Run** (▶️) или `Shift+F10`

### iOS (только macOS)

1. Выбрать run configuration: **iosApp**
2. Выбрать iOS симулятор
3. Нажать **Run** (▶️)

**Первый запуск iOS занимает время!** Kotlin/Native собирает native dependencies.

### Альтернатива: запуск через Xcode

```bash
cd iosApp
open iosApp.xcodeproj
```

В Xcode: выбрать симулятор → Run (⌘R)

---

## Шаг 5: Добавление первой shared функции

Добавим простую функцию в shared модуль:

**shared/src/commonMain/kotlin/Calculator.kt**:

```kotlin
object Calculator {
    fun add(a: Int, b: Int): Int = a + b
    fun multiply(a: Int, b: Int): Int = a * b

    fun fibonacci(n: Int): Long {
        if (n <= 1) return n.toLong()
        var a = 0L
        var b = 1L
        repeat(n - 1) {
            val sum = a + b
            a = b
            b = sum
        }
        return b
    }
}
```

Использование на Android (Compose):

```kotlin
@Composable
fun CalculatorScreen() {
    var result by remember { mutableStateOf(0) }

    Column {
        Text("Result: $result")
        Button(onClick = { result = Calculator.add(2, 3) }) {
            Text("Add 2 + 3")
        }
    }
}
```

Использование на iOS (SwiftUI):

```swift
import Shared  // Импорт KMP framework

struct CalculatorView: View {
    @State private var result: Int32 = 0

    var body: some View {
        VStack {
            Text("Result: \(result)")
            Button("Add 2 + 3") {
                result = Calculator.shared.add(a: 2, b: 3)
            }
        }
    }
}
```

---

## Типичные ошибки новичков

### 1. Xcode не запущен

```
❌ Error: Xcode not found or not configured
```

**Решение:** Запустить Xcode хотя бы раз, принять лицензию.

### 2. Отсутствует ANDROID_HOME

```
❌ Error: SDK location not found
```

**Решение:** Установить environment variable ANDROID_HOME.

### 3. K2 mode не включен

```
⚠️ Warning: K2 mode is recommended for KMP
```

**Решение:** Settings → Languages & Frameworks → Kotlin → Enable K2 mode.

### 4. Использование `!!` вместо safe calls

```kotlin
// ❌ Плохо — может crashнуться
val length = str!!.length

// ✅ Хорошо — безопасно
val length = str?.length ?: 0
```

### 5. Swallowing CancellationException

```kotlin
// ❌ Плохо — ломает coroutine cancellation
try {
    suspendFunction()
} catch (e: Exception) {
    // CancellationException тоже ловится!
}

// ✅ Хорошо — пробрасываем CancellationException
try {
    suspendFunction()
} catch (e: CancellationException) {
    throw e
} catch (e: Exception) {
    // Handle other exceptions
}
```

### 6. Изменения в Kotlin не отражаются в iOS

**Причина:** Xcode кэширует старый framework.

**Решение:**
1. Product → Clean Build Folder (⌘⇧K)
2. Пересобрать shared модуль в IDE

---

## iOS Integration: выбор метода

| Метод | Плюсы | Минусы | Когда использовать |
|-------|-------|--------|-------------------|
| **Direct Integration** | Простота, автоконфигурация | Нельзя добавить Pod-зависимости | Простые проекты, начало |
| **CocoaPods** | Pod-зависимости работают | Сложнее настройка | Проект использует Pods |
| **SPM** | Familiar для iOS-разработчиков | Manual config, больше шагов | Remote distribution |

**Рекомендация для начала:** Direct Integration (по умолчанию в wizard).

---

## Что дальше?

После первого проекта изучить:

1. [[kmp-project-structure]] — глубокое понимание структуры
2. [[kmp-expect-actual]] — механизм платформо-зависимых реализаций
3. [[kmp-source-sets]] — иерархия source sets
4. [[kmp-ktor-networking]] — сетевые запросы в KMP

---

## Кто использует и реальные примеры

| Компания | Контекст | Паттерн начала |
|----------|----------|----------------|
| **Netflix** | Mobile studio apps | Начали со shared data layer |
| **McDonald's** | Global mobile app | Shared business logic, native UI |
| **Philips** | Healthcare apps | Постепенная миграция модуль за модулем |
| **Cash App** | Fintech | KMP для критической бизнес-логики |

### Netflix: подход к старту

> "The smallest realistic project to actually prove KMP in your environment is a shared data or utility layer — something both applications can call without touching the UI."

---

## Мифы и заблуждения о старте с KMP

### ❌ "Нужно сразу настраивать все платформы"

**Реальность:** Начните с **одной пары** — Android + iOS или Android + Desktop. Добавляйте другие targets постепенно. KMP wizard даже предлагает выбрать конкретные targets.

### ❌ "KMP проект сложнее обычного Android проекта"

**Реальность:** Структура практически идентична. `commonMain` = дополнительная папка для shared кода. Если вы знаете Gradle — настройка занимает 10-15 минут.

```
Android-only:                   KMP:
app/                            shared/
└── src/main/kotlin/            ├── src/commonMain/kotlin/  ← NEW
                                └── src/androidMain/kotlin/
                                composeApp/
                                └── src/androidMain/kotlin/
```

### ❌ "Первый проект должен быть с shared UI"

**Реальность:** Netflix, McDonald's и другие крупные компании **начинали со shared data layer** — networking, repositories, use cases. UI оставался нативным. Это **наименее рискованный** подход.

### ❌ "K2 mode опционален"

**Реальность:** K2 — это **новый компилятор Kotlin 2.0**, а не просто "mode". Он:
- В 2 раза быстрее компилирует
- Лучше выводит типы
- Обязателен для некоторых новых фич

**Включайте сразу** — нет причин использовать старый компилятор в новых проектах.

### ❌ "IDE не важна — можно работать из командной строки"

**Реальность:** IDE даёт критический DX:
- Preflight checks (автопроверка окружения)
- Run configurations для Android/iOS
- Навигация между expect/actual
- Debugging обоих платформ

Командная строка работает для CI, но для разработки — IDE must-have.

### ❌ "CocoaPods обязателен для iOS"

**Реальность:** Есть **три способа** интеграции с iOS:

| Метод | Когда использовать |
|-------|-------------------|
| Direct Integration | По умолчанию, проще всего |
| CocoaPods | Если проект уже использует Pods |
| SPM | Для distribution или чистого Swift-проекта |

**Direct Integration** — рекомендуется для начала.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [KMP Quickstart](https://kotlinlang.org/docs/multiplatform/quickstart.html) | Official Doc | Официальный гайд от JetBrains |
| [Create First App](https://kotlinlang.org/docs/multiplatform/multiplatform-create-first-app.html) | Tutorial | Step-by-step туториал |
| [Android Developers Codelab](https://developer.android.com/codelabs/kmp-get-started) | Codelab | Интерактивный курс от Google |
| [KMP Learning Resources](https://kotlinlang.org/docs/multiplatform/kmp-learning-resources.html) | Collection | 30+ материалов по уровням |
| [Philipp Lackner - CMP Crash Course](https://www.youtube.com/watch?v=WT9-4DXUqsM) | Video | 5-часовой курс (бесплатно) |
| [Kotlin Multiplatform by Tutorials](https://www.kodeco.com/books/kotlin-multiplatform-by-tutorials/v3.0) | Book | Комплексная книга (~$60) |

### CS-фундамент

| Концепция | Материал | Почему важно |
|-----------|----------|--------------|
| Compilation Pipeline | [[compilation-pipeline]] | Как Kotlin превращается в native/JVM/JS |
| Build Systems | [[build-systems-theory]] | Понимание Gradle tasks, caching, DAG |
| Dependency Resolution | [[dependency-resolution]] | Как Gradle разрешает зависимости для разных targets |

---

## Связь с другими темами

- **[[kmp-project-structure]]** — После создания первого проекта следующий шаг — понять его внутреннее устройство. Этот материал детально объясняет, что такое targets, source sets, default hierarchy template и как Gradle координирует компиляцию для разных платформ. Понимание структуры превращает проект из «магической шаблонной папки» в осознанную архитектуру, которую вы можете модифицировать под свои нужды.

- **[[kmp-expect-actual]]** — Механизм expect/actual — первый инструмент платформо-зависимого кода, который вы встретите в шаблонном проекте (Platform.kt). Файлы Platform.android.kt и Platform.ios.kt — это actual-реализации expect-декларации из commonMain. Понимание этого механизма позволяет выйти за рамки шаблона и начать выносить реальную бизнес-логику в shared-модуль с платформенными реализациями.

- **[[kotlin-overview]]** — KMP — это Kotlin, и знание языка на базовом уровне является обязательным prerequisite. Data classes, sealed classes, extensions, null safety, coroutines — всё это составляет основу shared-кода. Если Kotlin ещё не знаком, рекомендуется начать с обзора языка и затем вернуться к KMP. Для Android-разработчиков адаптация занимает 1-2 недели, для iOS-разработчиков — 2-4 недели.

## Источники и дальнейшее чтение

### Теоретические основы

- **Aho A., Lam M., Sethi R., Ullman J. (2006).** *Compilers: Principles, Techniques, and Tools.* 2nd ed. Addison-Wesley. — Теория компиляторов, объясняющая frontend/backend разделение, лежащее в основе multi-target архитектуры KMP.
- **Feldman S. (1979).** *Make — A Program for Maintaining Computer Programs.* Bell Labs. — Формализация концепции DAG для систем сборки, реализованной в Gradle.
- **Humble J., Farley D. (2010).** *Continuous Delivery.* Addison-Wesley. — Принципы Environment Validation, реализованные в Preflight Checks KMP IDE.

### Практические руководства

- **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* Manning. — Полное руководство по Kotlin для начала работы с KMP.
- **Moskala M. (2021).** *Effective Kotlin.* — Идиоматичный Kotlin-код в shared-модуле.
- **Moskala M. (2022).** *Kotlin Coroutines: Deep Dive.* — Асинхронное программирование в KMP.
- [KMP Quickstart](https://kotlinlang.org/docs/multiplatform/quickstart.html) — Официальный гайд от JetBrains.
- [Android Developers Codelab](https://developer.android.com/codelabs/kmp-get-started) — Интерактивный курс от Google.

---

## Проверь себя

> [!question]- Почему первый запуск iOS-таргета в KMP занимает значительно больше времени, чем последующие?
> При первом запуске Kotlin/Native скачивает platform-specific библиотеки, компилирует стандартную библиотеку Kotlin в native-код и кэширует результат в ~/.konan/. Последующие сборки переиспользуют этот кэш, что существенно ускоряет процесс.

> [!question]- Вы создаёте KMP-проект и получаете ошибку "SDK location not found". Какова причина и как решить проблему?
> Причина в отсутствии переменной окружения ANDROID_HOME. Android Gradle Plugin ищет SDK по ANDROID_HOME или ANDROID_SDK_ROOT. Решение: добавить export ANDROID_HOME=~/Library/Android/sdk в ~/.zprofile (macOS) или установить системную переменную (Windows).

> [!question]- Почему Netflix и McDonald's начинали внедрение KMP со shared data layer, а не с shared UI?
> Shared data layer (networking, repositories, use cases) -- наименее рискованный подход. Он не затрагивает пользовательский интерфейс, позволяет оставить нативный UI (Compose/SwiftUI), и даёт измеримую выгоду (единая бизнес-логика) при минимальных изменениях в существующей архитектуре.

> [!question]- Почему для сборки iOS-таргета в KMP обязательно нужен установленный Xcode?
> Kotlin/Native компилирует Kotlin-код в LLVM IR, а затем использует LLVM-toolchain Apple для генерации native binary. Этот toolchain встроен в Xcode и недоступен отдельно. Без Xcode нет LLVM для Apple-платформ -- значит, невозможно собрать iOS framework.

---

## Ключевые карточки

Какие три компиляционных pipeline настраивает Gradle при создании KMP-проекта?
?
Kotlin/JVM (для Android/Desktop), Kotlin/Native (для iOS через LLVM), и Kotlin/JS (для Web). Каждый pipeline использует свой backend-компилятор и создаёт бинарники для целевой платформы.

Что такое Preflight Checks в контексте KMP?
?
Автоматическая проверка окружения разработки в IDE (Java, Android SDK, Xcode, Gradle). Позволяет убедиться, что все необходимые инструменты установлены и настроены корректно перед созданием проекта.

Чем Direct Integration отличается от CocoaPods для подключения KMP к iOS?
?
Direct Integration подключает iOS framework напрямую без дополнительных менеджеров зависимостей. CocoaPods позволяет добавлять Pod-зависимости, но требует более сложной настройки. Direct Integration рекомендуется для начала.

Что такое K2 mode и почему его нужно включать сразу?
?
K2 -- это новый компилятор Kotlin 2.0, который компилирует в 2 раза быстрее, лучше выводит типы и обязателен для некоторых новых фич. Нет причин использовать старый компилятор в новых проектах.

Какова рекомендуемая минимальная структура для первого KMP-проекта?
?
shared/ (общий модуль с commonMain, androidMain, iosMain), composeApp/ (Android-приложение), iosApp/ (Xcode-проект). Начинать со shared data layer, а не shared UI.

Почему настройка ANDROID_HOME критична для KMP-проекта?
?
Android Gradle Plugin ищет Android SDK по ANDROID_HOME. Без этой переменной не соберётся androidMain source set, и даже commonMain не скомпилируется, так как для компиляции нужны все объявленные targets.

Что хранится в ~/.konan/ и зачем этот каталог?
?
Кэш Kotlin/Native (~2-3 GB): скомпилированные klibs, LLVM и platform-зависимые библиотеки, prebuild-версия компилятора. Используется для ускорения последующих сборок iOS/Native-таргетов.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-project-structure]] | Глубокое понимание структуры KMP-проекта |
| Углубиться | [[kmp-expect-actual]] | Механизм платформо-зависимых реализаций |
| Смежная тема | [[compilation-pipeline]] | CS-фундамент компиляции Kotlin в разные платформы |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | KMP Stable, Kotlin 2.1.21, Android Studio Otter 2025.2.1, IntelliJ IDEA 2025.2.2*
