---
title: "KMP Web/Wasm: Kotlin для Web через WebAssembly"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - wasm
  - webassembly
  - web
  - compose
  - browser
  - javascript
  - type/concept
  - level/intermediate
related:
  - "[[kmp-overview]]"
  - "[[kmp-android-integration]]"
  - "[[compose-mp-web]]"
cs-foundations:
  - "[[compilation-pipeline]]"
  - "[[native-compilation-llvm]]"
  - "[[bytecode-virtual-machines]]"
  - "[[memory-model-fundamentals]]"
status: published
---

# KMP Web/Wasm

> **TL;DR:** Kotlin/Wasm (Beta) компилирует Kotlin в WebAssembly. С декабря 2024 все major browsers поддерживают WasmGC. Compose Multiplatform Web (Beta с сентября 2025) использует Canvas rendering — ~3x быстрее JS в UI scenarios. Kotlin/JS лучше для business logic sharing, Kotlin/Wasm — для shared UI. webMain source set объединяет js и wasmJs targets. Compatibility mode: Wasm для современных browsers, JS fallback для старых.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Compilation Pipeline** | Как Kotlin компилируется в разные targets | [[compilation-pipeline]] |
| **LLVM & Native Compilation** | Как работает WebAssembly compilation | [[native-compilation-llvm]] |
| **Virtual Machines** | Сравнение JVM vs Wasm VM | [[bytecode-virtual-machines]] |
| WebAssembly Basics | Понимание Wasm | [WebAssembly.org](https://webassembly.org/) |
| JavaScript/HTML/CSS | Web основы | [MDN Web Docs](https://developer.mozilla.org/) |
| Jetpack Compose | UI фреймворк | [[compose-basics]] |
| KMP Project Structure | Основы KMP | [[kmp-project-structure]] |

> **Рекомендация:** Для понимания ПОЧЕМУ Wasm быстрее JS, прочитай CS-фундамент о compilation pipeline и LLVM. Это объяснит архитектурные преимущества.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **WebAssembly (Wasm)** | Бинарный формат для VM в браузере | Машинный код для виртуального компьютера в браузере |
| **WasmGC** | Garbage Collection для Wasm | Уборщик мусора для Wasm-приложений |
| **wasmJs** | Kotlin target для браузера/Node.js | Выход на web-платформу |
| **wasmWasi** | Kotlin target для standalone Wasm | Выход на серверный Wasm |
| **Canvas Rendering** | Рисование UI на HTML Canvas | Художник рисует на холсте, а не строит из кубиков |
| **DOM Rendering** | Построение UI из HTML элементов | Строительство из готовых блоков |
| **webMain** | Общий source set для js и wasmJs | Единый чемодан для двух путешествий |

---

## Почему WebAssembly — революция для Web

### Фундаментальная проблема JavaScript

JavaScript был создан за 10 дней в 1995 году как "скриптовый язык для форм". Его архитектура не предназначалась для сложных приложений:

```
JavaScript execution:
Source code → Parser → AST → Interpreter → JIT → Native code
                                           ↑
                                           └── Runtime optimization, speculation, deoptimization
```

**Результат:** Непредсказуемая производительность, "warming up" время, jank в анимациях.

### WebAssembly: новый подход

WebAssembly — это **бинарный формат**, компилируемый AOT (ahead-of-time):

```
Kotlin → LLVM IR → WebAssembly bytecode → Browser Wasm VM
                   ↑
                   └── Уже оптимизирован, предсказуемая производительность
```

### Почему Wasm ~3x быстрее JS в UI

| Аспект | JavaScript | WebAssembly |
|--------|------------|-------------|
| Парсинг | Текст → AST (медленно) | Бинарный (быстро) |
| Оптимизация | Runtime JIT | AOT (ahead-of-time) |
| Типы | Dynamic (проверки в runtime) | Static (проверки в compile-time) |
| Memory | GC JavaScript | WasmGC (оптимизирован для Kotlin) |
| Производительность | Непредсказуемая | Стабильная |

### WasmGC — ключевое изменение 2024

До WasmGC языки с GC (Kotlin, Java) должны были bundling собственный GC в Wasm binary (+1-5 MB). WasmGC — это GC в браузере:

```
До WasmGC (2023):   Kotlin + bundled GC → большой binary, overhead
После WasmGC (2024): Kotlin → WasmGC → компактный binary, native GC
```

**Safari поддержал WasmGC в декабре 2024** — последний major browser. Теперь 100% modern browsers совместимы.

### Compose for Web: Canvas vs DOM

Compose Multiplatform использует **Canvas rendering** (рисование на HTML5 Canvas), а не DOM manipulation:

```
Traditional Web:     JavaScript → DOM → Browser layout → Pixels
Compose for Web:     Kotlin → Skia → Canvas → Pixels
                              ↑
                              └── Обходит медленный DOM layout
```

**Преимущества:**
- Одинаковый UI на всех платформах
- Полный контроль над рендерингом
- ~3x быстрее в анимациях и скроллинге

**Компромиссы:**
- Нет нативных browser controls
- SEO ограничено (Canvas не индексируется)
- Accessibility требует доработки

---

## Статус Web в KMP (январь 2026)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    KMP WEB STATUS MATRIX                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Technology              Status        Browser Support             │
│   ─────────────────────────────────────────────────────────         │
│   Kotlin/Wasm             🧪 Beta       All major (Dec 2024+)       │
│   Kotlin/JS               ✅ Stable     All browsers                │
│   Compose MP Web          🧪 Beta       WasmGC required             │
│   Compose MP Web + JS     🧪 Beta       All (compatibility mode)    │
│   webMain source set      🆕 New        K 2.2.20+                   │
│                                                                     │
│   Browser Requirements for WasmGC:                                  │
│   • Chrome 119+ (Nov 2023)                                          │
│   • Firefox 120+ (Nov 2023)                                         │
│   • Safari 18.2+ (Dec 2024)                                         │
│   • Edge 119+ (Nov 2023)                                            │
│                                                                     │
│   Performance (UI scenarios):                                       │
│   • Kotlin/Wasm: ~3x faster than Kotlin/JS                          │
│   • Initial load: Kotlin/JS 0.25-0.5s faster                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Kotlin/JS vs Kotlin/Wasm

### Когда использовать что?

| Критерий | Kotlin/JS | Kotlin/Wasm |
|----------|-----------|-------------|
| **Use case** | Business logic sharing | UI sharing (Compose MP) |
| **Performance** | Хорошая | ~3x быстрее в UI |
| **Initial load** | 0.25-0.5s быстрее | Медленнее загрузка |
| **Browser support** | Все браузеры | WasmGC required |
| **JS Interop** | Нативная | Через мост |
| **DOM manipulation** | Отличная | Ограниченная |
| **Статус** | Stable | Beta |

### Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHOOSING WEB TARGET                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   "Хочу шарить бизнес-логику с web"                                 │
│   └─> Kotlin/JS (лучший JS interop)                                 │
│                                                                     │
│   "Хочу шарить UI между platforms"                                  │
│   └─> Kotlin/Wasm + Compose Multiplatform                           │
│                                                                     │
│   "Нужна поддержка старых браузеров"                                │
│   └─> Kotlin/JS или Compatibility Mode                              │
│                                                                     │
│   "Важна runtime performance"                                       │
│   └─> Kotlin/Wasm                                                   │
│                                                                     │
│   "Важна initial load speed"                                        │
│   └─> Kotlin/JS                                                     │
│                                                                     │
│   "Хочу и то, и другое"                                             │
│   └─> webMain source set + Compatibility Mode                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Быстрый старт с Kotlin/Wasm

### Способ 1: KMP Wizard (рекомендуется)

1. Открыть [kmp.jetbrains.com](https://kmp.jetbrains.com/?web=true&webui=compose)
2. Выбрать "Web" target и "Share UI"
3. Скачать и открыть в IDE

### Способ 2: Ручная настройка

**settings.gradle.kts:**

```kotlin
pluginManagement {
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

rootProject.name = "WasmDemo"
include(":composeApp")
```

**composeApp/build.gradle.kts:**

```kotlin
import org.jetbrains.kotlin.gradle.ExperimentalWasmDsl

plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose")
    id("org.jetbrains.kotlin.plugin.compose")
}

kotlin {
    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        browser {
            commonWebpackConfig {
                outputFileName = "composeApp.js"
            }
        }
        binaries.executable()
    }

    sourceSets {
        commonMain.dependencies {
            implementation(compose.runtime)
            implementation(compose.foundation)
            implementation(compose.material3)
            implementation(compose.ui)
            implementation(compose.components.resources)
        }

        wasmJsMain.dependencies {
            // Web-specific dependencies
        }
    }
}

compose.experimental {
    web.application {}
}
```

**Структура проекта:**

```
composeApp/
├── build.gradle.kts
└── src/
    ├── commonMain/
    │   └── kotlin/
    │       └── App.kt           # Shared Compose UI
    └── wasmJsMain/
        ├── kotlin/
        │   └── main.kt          # Entry point
        └── resources/
            └── index.html       # HTML host
```

### Entry Point

**wasmJsMain/kotlin/main.kt:**

```kotlin
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.window.CanvasBasedWindow

@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    CanvasBasedWindow(canvasElementId = "ComposeTarget") {
        App()  // Compose UI из commonMain
    }
}
```

**wasmJsMain/resources/index.html:**

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kotlin/Wasm App</title>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
        }
        #ComposeTarget {
            width: 100%;
            height: 100%;
        }
    </style>
</head>
<body>
    <canvas id="ComposeTarget"></canvas>
    <script src="composeApp.js"></script>
</body>
</html>
```

### Запуск и сборка

```bash
# Development (hot reload)
./gradlew wasmJsBrowserDevelopmentRun

# Production build
./gradlew wasmJsBrowserProductionWebpack

# Output: build/dist/wasmJs/productionExecutable/
```

---

## Compose Multiplatform для Web

### Canvas-based Rendering

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPOSE WEB RENDERING                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Compose Multiplatform Web использует Canvas rendering:            │
│                                                                     │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│   │   Compose   │ -> │    Skia     │ -> │   Canvas    │             │
│   │     UI      │    │  Renderer   │    │   (HTML5)   │             │
│   └─────────────┘    └─────────────┘    └─────────────┘             │
│                                                                     │
│   Преимущества:                                                     │
│   • Одинаковый UI на всех платформах                                │
│   • Полный контроль над отрисовкой                                  │
│   • ~3x быстрее в animations/scrolling                              │
│                                                                     │
│   Недостатки:                                                       │
│   • Нет native browser controls                                     │
│   • SEO ограничено (Canvas не индексируется)                        │
│   • Accessibility требует доработки                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Базовый пример Compose UI

**commonMain/kotlin/App.kt:**

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun App() {
    MaterialTheme {
        var count by remember { mutableStateOf(0) }

        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background
        ) {
            Column(
                modifier = Modifier.fillMaxSize(),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.Center
            ) {
                Text(
                    text = "Count: $count",
                    style = MaterialTheme.typography.headlineMedium
                )

                Spacer(modifier = Modifier.height(16.dp))

                Button(onClick = { count++ }) {
                    Text("Increment")
                }
            }
        }
    }
}
```

### Platform-specific code

```kotlin
// commonMain/kotlin/Platform.kt
expect fun getPlatformName(): String

// wasmJsMain/kotlin/Platform.wasmJs.kt
actual fun getPlatformName(): String = "Web (Wasm)"

// jsMain/kotlin/Platform.js.kt (если используете JS fallback)
actual fun getPlatformName(): String = "Web (JS)"
```

---

## webMain Source Set (Kotlin 2.2.20+)

### Что это?

Новый общий source set для `js` и `wasmJs` targets. Позволяет писать один `actual` для обоих web targets.

### Конфигурация

```kotlin
kotlin {
    js {
        browser()
        binaries.executable()
    }

    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        browser()
        binaries.executable()
    }

    sourceSets {
        // Новый webMain source set
        val webMain by creating {
            dependsOn(commonMain.get())
        }

        jsMain.get().dependsOn(webMain)
        wasmJsMain.get().dependsOn(webMain)

        webMain.dependencies {
            // Dependencies для обоих web targets
        }
    }
}
```

### Структура проекта

```
src/
├── commonMain/kotlin/       # Общий для всех platforms
├── webMain/kotlin/          # Общий для js и wasmJs
├── jsMain/kotlin/           # Только Kotlin/JS
└── wasmJsMain/kotlin/       # Только Kotlin/Wasm
```

---

## Compatibility Mode

### Зачем нужен?

- Wasm для современных браузеров (лучшая performance)
- JS fallback для старых браузеров (широкая совместимость)

### Конфигурация

```kotlin
kotlin {
    js {
        browser()
        binaries.executable()
    }

    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        browser()
        binaries.executable()
    }

    // Compose automatically uses Wasm where supported, JS otherwise
}
```

### Runtime Detection

```javascript
// В HTML можно определить поддержку WasmGC
<script>
    const wasmGCSupported = (() => {
        try {
            // Check for WasmGC support
            return typeof WebAssembly.instantiate !== 'undefined';
        } catch (e) {
            return false;
        }
    })();

    if (wasmGCSupported) {
        // Load Wasm version
        import('./composeApp.js');
    } else {
        // Load JS fallback
        import('./composeApp-js.js');
    }
</script>
```

---

## JavaScript Interop

### Calling JS from Kotlin/Wasm

```kotlin
// Определение внешних JS функций
external fun alert(message: String)

external object console {
    fun log(message: String)
    fun error(message: String)
}

// Использование
fun showAlert() {
    alert("Hello from Kotlin/Wasm!")
    console.log("Logged from Kotlin")
}
```

### Working with DOM

```kotlin
import kotlinx.browser.document
import kotlinx.browser.window

fun setupDom() {
    // Получить элемент
    val element = document.getElementById("myElement")

    // Добавить event listener
    element?.addEventListener("click") { event ->
        console.log("Clicked!")
    }

    // Изменить стили
    window.setTimeout({
        element?.setAttribute("style", "color: red")
    }, 1000)
}
```

### Важные отличия Wasm vs JS interop

```kotlin
// В Kotlin/JS можно использовать Any
external fun jsFunction(value: Any)

// В Kotlin/Wasm нужно использовать JsAny
external fun wasmFunction(value: JsAny)

// Конвертация
val kotlinString = "Hello"
val jsString: JsString = kotlinString.toJsString()
```

---

## Browser APIs

### Fetch API

```kotlin
import kotlinx.browser.window
import org.w3c.fetch.RequestInit

suspend fun fetchData(url: String): String {
    val response = window.fetch(url).await()
    return response.text().await()
}

// Использование с корутинами
fun loadData() {
    GlobalScope.launch {
        try {
            val data = fetchData("https://api.example.com/data")
            console.log(data)
        } catch (e: Exception) {
            console.error("Failed to fetch: ${e.message}")
        }
    }
}
```

### Local Storage

```kotlin
import kotlinx.browser.localStorage

fun saveToStorage(key: String, value: String) {
    localStorage.setItem(key, value)
}

fun loadFromStorage(key: String): String? {
    return localStorage.getItem(key)
}

fun clearStorage() {
    localStorage.clear()
}
```

### Session Storage (DataStore Web)

```kotlin
// DataStore использует sessionStorage в KMP Web
// Данные сохраняются только в текущей вкладке браузера
```

---

## Оптимизация и Production

### Минимизация размера

```kotlin
kotlin {
    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        browser {
            commonWebpackConfig {
                // Optimize for production
                devServer?.open = false
            }
        }
        binaries.executable()

        // Compile optimizations
        compilations.all {
            kotlinOptions {
                // Enable dead code elimination
            }
        }
    }
}
```

### Incremental Compilation

**gradle.properties:**

```properties
# Включить incremental compilation для Wasm
kotlin.incremental.wasm=true

# Кеширование
org.gradle.caching=true
kotlin.native.cacheKind=static
```

### CDN и Caching

```kotlin
// В webpack.config.js (если используете)
module.exports = {
    output: {
        filename: '[name].[contenthash].js'
    }
}
```

---

## Deployment

### GitHub Pages

```yaml
# .github/workflows/deploy.yml
name: Deploy to GitHub Pages

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build
        run: ./gradlew wasmJsBrowserProductionWebpack

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./composeApp/build/dist/wasmJs/productionExecutable
```

### Netlify / Vercel / Cloudflare

```bash
# Build command
./gradlew wasmJsBrowserProductionWebpack

# Publish directory
composeApp/build/dist/wasmJs/productionExecutable
```

---

## Ограничения и Workarounds

### 1. SEO

**Проблема:** Canvas-based UI не индексируется поисковиками

**Workaround:**
- Server-side rendering для critical content
- Static HTML для landing pages
- Structured data в `<head>`

### 2. Accessibility

**Проблема:** Canvas не имеет нативного accessibility

**Workaround:**
- ARIA labels через JS interop
- Fallback текстовый контент
- Следить за Compose MP updates

### 3. Text Input

**Проблема:** Сложности с IME и mobile keyboards

**Workaround:**
- Использовать nativeInput в Compose
- JS overlay для text fields

### 4. Размер бинарника

**Типичные размеры:**
- Kotlin/Wasm: ~2-5 MB (gzipped: ~500KB-1MB)
- Kotlin/JS: ~1-3 MB (gzipped: ~300-500KB)

**Оптимизации:**
```properties
# gradle.properties
kotlin.js.ir.output.granularity=per-file
```

---

## Production Apps

| Приложение | Описание |
|------------|----------|
| [Kotlin Playground](https://play.kotlinlang.org/) | IDE в браузере на Compose MP |
| [KotlinConf App](https://kotlinconf.com/) | Официальное приложение конференции |
| [Rijksmuseum Demo](https://www.jetbrains.com/lp/compose-multiplatform/) | Демо галереи |

---

## Мифы и заблуждения

### Миф 1: "Wasm заменит JavaScript"

**Реальность:** Wasm и JS — взаимодополняющие технологии:
- Wasm: computation-heavy tasks, shared UI
- JS: DOM manipulation, existing ecosystem, quick scripts

Kotlin/JS остаётся stable и лучше для sharing business logic with native JS UI.

### Миф 2: "Wasm требует переписать весь frontend"

**Реальность:** Wasm работает вместе с JavaScript:
- Можно постепенно добавлять Wasm modules
- JS вызывает Wasm functions и наоборот
- Compose component можно встроить в существующий JS app

### Миф 3: "Compose for Web — это обычный web framework"

**Реальность:** Compose for Web использует Canvas rendering, что принципиально отличается:
- Не использует DOM для UI (только Canvas element)
- Skia рендерит пиксели напрямую
- Одинаковый код для Android/iOS/Desktop/Web

Это **не** React/Vue/Angular альтернатива — это другой подход.

### Миф 4: "WasmGC поддерживается не везде"

**Реальность (январь 2026):** WasmGC поддерживается **всеми** major browsers:
- Chrome 119+ (ноябрь 2023)
- Firefox 120+ (ноябрь 2023)
- Safari 18.2+ (декабрь 2024)
- Edge 119+ (ноябрь 2023)

Для старых browsers используйте Compatibility Mode с JS fallback.

### Миф 5: "Wasm binary размер огромный"

**Реальность:** После WasmGC размеры уменьшились:
- Типичный Compose Web app: 2-5 MB (gzipped: 500KB-1MB)
- Сравните: средний React app: 1-3 MB
- Wasm binary streaming загружается и компилируется параллельно

### Миф 6: "Kotlin/Wasm — это Kotlin/Native для браузера"

**Реальность:** Kotlin/Wasm — отдельный backend:
- Kotlin/Native → LLVM → Machine code (iOS, macOS, Linux)
- Kotlin/Wasm → LLVM → WebAssembly (браузеры, Node.js)

Разные interop (JsAny vs Objective-C), разные ограничения.

---

## Рекомендуемые источники

### CS-фундамент для глубокого понимания

| Материал | Зачем нужен |
|----------|-------------|
| [[compilation-pipeline]] | Как Kotlin компилируется в Wasm |
| [[native-compilation-llvm]] | LLVM backend для WebAssembly |
| [[bytecode-virtual-machines]] | Сравнение JVM vs Wasm VM |
| [[memory-model-fundamentals]] | GC и memory в разных runtimes |

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Kotlin/Wasm Overview](https://kotlinlang.org/docs/wasm-overview.html) | Official | Обзор технологии |
| [Get Started with Wasm](https://kotlinlang.org/docs/wasm-get-started.html) | Official | Быстрый старт |
| [Compose MP Web](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-multiplatform-web.html) | Official | Compose для Web |
| [Choosing Web Target](https://www.jetbrains.com/help/kotlin-multiplatform-dev/choosing-web-target.html) | Official | JS vs Wasm |

### Блоги и статьи

| Источник | Тип | Описание |
|----------|-----|----------|
| [Present and Future of Kotlin for Web](https://blog.jetbrains.com/kotlin/2025/05/present-and-future-kotlin-for-web/) | Official | Roadmap 2025 |
| [Compose MP 1.9.0 Release](https://blog.jetbrains.com/kotlin/2025/09/compose-multiplatform-1-9-0-compose-for-web-beta/) | Official | Web Beta announcement |
| [Touchlab Wasm Getting Started](https://touchlab.co/kotlin-wasm-getting-started) | Expert | Практический гайд |

### Шаблоны

| Ресурс | Описание |
|--------|----------|
| [kotlin-wasm-compose-template](https://github.com/Kotlin/kotlin-wasm-compose-template) | Официальный шаблон |
| [KMP Web Wizard](https://kmp.jetbrains.com/?web=true&webui=compose) | Генератор проектов |

---

*Проверено: 2026-01-09 | Kotlin 2.2.20, Compose Multiplatform 1.9.0, Kotlin/Wasm Beta*
