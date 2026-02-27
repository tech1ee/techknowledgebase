---
title: "Compose Multiplatform Web: Beta для современных браузеров"
created: 2026-01-03
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - topic/android
  - web
  - wasm
  - wasmgc
  - canvas
  - browser
  - javascript
  - type/concept
  - level/intermediate
related:
  - "[[compose-mp-overview]]"
  - "[[kmp-web-wasm]]"
  - "[[kmp-overview]]"
prerequisites:
  - "[[compose-mp-overview]]"
  - "[[kmp-web-wasm]]"
cs-foundations:
  - "[[webassembly-internals]]"
  - "[[browser-rendering-engine]]"
  - "[[canvas-api-graphics]]"
  - "[[web-accessibility-fundamentals]]"
status: published
reading_time: 46
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Compose Multiplatform Web

> **TL;DR:** Compose Multiplatform for Web достиг Beta в сентябре 2025 (CMP 1.9.0). Canvas-based rendering через Skia — ~3x быстрее JS в UI scenarios. WasmGC поддерживается всеми major browsers с декабря 2024 (Safari 18.2+). Beta включает: type-safe navigation с deep linking, HTML interop, базовую accessibility, dark mode support. Ограничения: не для SEO (Canvas не индексируется), initial load 1-3 секунды, нет SSR. Production apps: Kotlin Playground, KotlinConf.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Compose Multiplatform Basics | Основы CMP | [[compose-mp-overview]] |
| KMP Web/Wasm | Kotlin/Wasm target | [[kmp-web-wasm]] |
| HTML/CSS/JavaScript | Web основы | [MDN Web Docs](https://developer.mozilla.org/) |
| WebAssembly Basics | Wasm концепции | [WebAssembly.org](https://webassembly.org/) |
| **CS: WebAssembly** | Wasm bytecode, GC | [[webassembly-internals]] |
| **CS: Browser Rendering** | Layout, paint, composite | [[browser-rendering-engine]] |
| **CS: Canvas API** | 2D graphics в браузере | [[canvas-api-graphics]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Canvas Rendering** | Рисование всего UI на HTML Canvas | Художник рисует картину на холсте |
| **DOM Rendering** | Построение UI из HTML элементов | Строительство дома из блоков |
| **WasmGC** | Garbage Collection в WebAssembly | Уборщик мусора для Wasm |
| **Compatibility Mode** | Wasm + JS fallback | Два паспорта для разных стран |
| **Deep Linking** | URL-based навигация | Адрес квартиры в многоэтажке |
| **Skiko** | Skia bindings для Kotlin | Мост между художником и холстом |

---

## Теоретические основы

### Формальное определение

> **Canvas-based Web Rendering** — подход к построению веб-интерфейсов, при котором UI рисуется на HTML5 Canvas элементе через 2D/WebGL API, минуя DOM layout engine браузера (W3C Canvas API Specification, 2015).

Compose for Web использует Skia → Canvas rendering через WebAssembly, реализуя **Immediate Mode GUI** в браузерном контексте.

### Сравнение подходов к Web UI

| Подход | Рендеринг | SEO | Accessibility | Производительность |
|--------|-----------|-----|---------------|-------------------|
| DOM-based (React, Vue) | HTML elements + CSS | Полная | Встроенная | Layout engine overhead |
| Canvas-based (Compose) | Skia → Canvas pixels | Ограничена | Требует доработки | Высокая (обход DOM) |
| WebGL-based (Unity Web) | GPU shaders | Нет | Нет | Максимальная для 3D |
| Hybrid (Flutter Web) | Canvas + HTML fallback | Частичная | Частичная | Высокая |

### Историческая эволюция: от DOM к Canvas

| Этап | Год | Технология | Подход |
|------|-----|-----------|--------|
| Static HTML | 1993 | HTML + CSS | Документы, не приложения |
| Dynamic DOM | 2005 | AJAX + jQuery | Манипуляция DOM-деревом |
| Virtual DOM | 2013 | React | Diff-алгоритм, минимальные обновления DOM |
| Canvas rendering | 2018 | Flutter Web | Обход DOM, рисование на Canvas |
| Wasm + Canvas | 2024 | Compose Web | Kotlin → Wasm → Skia → Canvas |

### Компромиссы Canvas-подхода (формализация)

Выбор Canvas-рендеринга — это инженерный trade-off между **performance** и **platform integration**:

- **Performance:** Canvas обходит DOM layout (O(n) reflow), рендерит через GPU — constant-time per frame
- **Accessibility:** DOM имеет встроенное accessibility tree; Canvas требует ручной ARIA-разметки
- **SEO:** DOM-контент индексируется; Canvas-контент невидим для поисковых роботов

> **CS-фундамент:** WebAssembly как target — [[compilation-pipeline]]. Canvas vs DOM — два подхода к rendering pipeline, аналогичные Immediate vs Retained Mode GUI.


## Почему Compose Web использует Canvas + WebAssembly

> **CS-фундамент:** WebAssembly Internals, Browser Rendering Engine, Canvas API

### Проблема: как запустить Compose UI в браузере?

```
ДВА ПОДХОДА К WEB UI
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   ПОДХОД 1: DOM-BASED (Compose HTML, React, Vue)                │
│   ──────────────────────────────────────────────                 │
│                                                                 │
│   Kotlin/JS Code → DOM Elements → Browser Layout → Screen       │
│                                                                 │
│   @Composable                                                   │
│   fun Button() {                                                │
│       Div { ... }    ──►   <div class="button">...</div>        │
│   }                                                             │
│                                                                 │
│   ✅ SEO (Google видит HTML)                                    │
│   ✅ Accessibility (screen readers читают DOM)                  │
│   ✅ DevTools работают                                          │
│   ❌ Разный код для web vs mobile                               │
│   ❌ Layout thrashing при сложном UI                            │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ПОДХОД 2: CANVAS-BASED (Compose MP, Figma, Google Docs)       │
│   ────────────────────────────────────────────────────────       │
│                                                                 │
│   Kotlin/Wasm Code → Skia → Canvas 2D → Screen                  │
│                                                                 │
│   @Composable                                                   │
│   fun Button() {                                                │
│       Button { ... }  ──►  canvas.drawRect()                    │
│   }                        canvas.drawText()                    │
│                                                                 │
│   ✅ Тот же код что mobile/desktop                              │
│   ✅ Pixel-perfect рендеринг                                    │
│   ✅ ~3x быстрее для animations                                 │
│   ❌ SEO невозможен                                             │
│   ❌ Accessibility ограничена                                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### WebAssembly + Garbage Collection (WasmGC)

**WebAssembly** — бинарный формат для выполнения кода в браузере:

```
WASM EVOLUTION
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Wasm 1.0 (2017)                                               │
│   ────────────────                                               │
│   • Линейная память (manual management)                         │
│   • Для C/C++/Rust                                              │
│   • Нет GC → Kotlin нужен свой runtime                           │
│                                                                 │
│   ─────────────────────────────────────────────────────────────  │
│                                                                 │
│   WasmGC (2023-2024)                                            │
│   ──────────────────                                             │
│   • Garbage Collection встроен в Wasm                           │
│   • Structs и arrays как first-class citizens                   │
│   • Идеально для Kotlin, Java, Dart                             │
│                                                                 │
│   Browser Support:                                              │
│   • Chrome 119+   (Nov 2023)                                    │
│   • Firefox 120+  (Nov 2023)                                    │
│   • Edge 119+     (Nov 2023)                                    │
│   • Safari 18.2+  (Dec 2024) ← последний major browser          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему ~3x быстрее JavaScript?

```
PERFORMANCE COMPARISON
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   JavaScript Path:                                              │
│   ─────────────────                                              │
│   JS Code → JIT Compilation → Optimization → Deoptimization → … │
│                                                                 │
│   Проблемы:                                                      │
│   • JIT compilation overhead                                    │
│   • Deoptimization при type changes                             │
│   • GC pauses непредсказуемы                                    │
│   • Hidden class transitions                                    │
│                                                                 │
│   ─────────────────────────────────────────────────────────────  │
│                                                                 │
│   WebAssembly Path:                                             │
│   ──────────────────                                             │
│   Wasm Bytecode → Direct Execution → Predictable Performance    │
│                                                                 │
│   Преимущества:                                                  │
│   • Pre-compiled bytecode                                       │
│   • Static types → no type checks at runtime                    │
│   • Predictable GC (WasmGC)                                     │
│   • Near-native speed                                           │
│                                                                 │
│   Benchmark Results (UI scenarios):                             │
│   • Animations: Wasm ~3x faster                                 │
│   • Complex layouts: Wasm ~2-3x faster                          │
│   • Recomposition: Wasm ~2x faster                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Canvas API: как Skia рисует UI

```
CANVAS RENDERING PIPELINE
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   1. COMPOSE UI TREE                                            │
│   ──────────────────                                             │
│   @Composable fun Screen() {                                    │
│       Column {                                                  │
│           Text("Hello")                                         │
│           Button(onClick = {}) { Text("Click") }                │
│       }                                                         │
│   }                                                             │
│         │                                                       │
│         ▼                                                       │
│   2. LAYOUT PHASE                                               │
│   ────────────────                                               │
│   Calculate size and position of each element                   │
│         │                                                       │
│         ▼                                                       │
│   3. DRAW PHASE (Skia/Skiko)                                    │
│   ─────────────────────────────                                  │
│   canvas.drawRect(x, y, width, height, paint)                   │
│   canvas.drawText("Hello", x, y, textPaint)                     │
│   canvas.drawRoundRect(buttonBounds, cornerRadius, paint)       │
│         │                                                       │
│         ▼                                                       │
│   4. CANVAS 2D CONTEXT                                          │
│   ─────────────────────                                          │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │   <canvas id="ComposeTarget" width="1920" height="1080"> │   │
│   │                                                          │   │
│   │   ctx.fillRect(...)                                      │   │
│   │   ctx.fillText(...)                                      │   │
│   │   ctx.beginPath()...                                     │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│         │                                                       │
│         ▼                                                       │
│   5. GPU COMPOSITING                                            │
│   ──────────────────                                             │
│   Browser composites canvas with rest of page                   │
│   Displayed at 60 FPS (or higher)                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Trade-off: Initial Load Time

```
INITIAL LOAD BREAKDOWN
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Compose Web (Wasm):                                           │
│   ─────────────────────                                          │
│   1. Download .wasm file:     ~2-4 MB (500KB-1MB compressed)    │
│   2. Compile Wasm bytecode:   ~500ms                            │
│   3. Initialize runtime:      ~200ms                            │
│   4. First render:            ~300ms                            │
│   ────────────────────────────────────────                       │
│   Total cold start:           1-3 seconds                       │
│   Cached reload:              1-1.5 seconds                     │
│                                                                 │
│   vs JavaScript App:                                            │
│   ──────────────────                                             │
│   1. Download JS:             ~200-500 KB                       │
│   2. Parse + JIT compile:     ~100-300ms                        │
│   3. Initialize:              ~100ms                            │
│   ────────────────────────────────────────                       │
│   Total cold start:           0.5-1 second                      │
│                                                                 │
│   Trade-off:                                                    │
│   Longer initial load → Better runtime performance              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Статус (январь 2026)

```
┌─────────────────────────────────────────────────────────────────────┐
│              COMPOSE MULTIPLATFORM WEB STATUS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Status: 🧪 BETA (since September 2025, CMP 1.9.0)                 │
│                                                                     │
│   Rendering: Canvas-based via Skia/Skiko                            │
│                                                                     │
│   Browser Requirements (WasmGC):                                    │
│   • Chrome 119+ (Nov 2023)                                          │
│   • Firefox 120+ (Nov 2023)                                         │
│   • Safari 18.2+ (Dec 2024) ← последний major browser               │
│   • Edge 119+ (Nov 2023)                                            │
│                                                                     │
│   Performance:                                                      │
│   • ~3x faster than JS in UI scenarios                              │
│   • Initial load: 1-3 seconds (Wasm initialization)                 │
│   • After cache: 1-1.5 seconds                                      │
│                                                                     │
│   Beta Features:                                                    │
│   • Type-safe navigation with deep linking                          │
│   • HTML interop                                                    │
│   • Fundamental accessibility support                               │
│   • Dark mode / system preferences                                  │
│   • Material 3 components                                           │
│   • Cross-browser compatibility mode                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Canvas vs DOM Rendering

### Архитектура Compose Web

```
┌─────────────────────────────────────────────────────────────────────┐
│               COMPOSE WEB: CANVAS-BASED RENDERING                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐   │
│   │  Kotlin  │ --> │ Compose  │ --> │  Skia/   │ --> │  HTML5   │   │
│   │  Code    │     │  Runtime │     │  Skiko   │     │  Canvas  │   │
│   └──────────┘     └──────────┘     └──────────┘     └──────────┘   │
│                                                                     │
│   Весь UI рисуется на одном <canvas> элементе                       │
│   Браузер не "знает" о структуре UI (нет DOM-элементов)             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Сравнение подходов

| Аспект | Canvas (Compose MP) | DOM (Compose HTML/Kobweb) |
|--------|---------------------|---------------------------|
| **UI sharing** | ✅ Тот же код что и mobile/desktop | ❌ Web-specific код |
| **Performance** | ✅ ~3x быстрее animations | ⚠️ Зависит от браузера |
| **SEO** | ❌ Не индексируется | ✅ Индексируется |
| **Accessibility** | ⚠️ Ограниченная | ✅ Нативная |
| **Bundle size** | ⚠️ 2-5 MB | ✅ 200-300 KB |
| **DevTools** | ❌ Не работают для UI | ✅ Полная поддержка |
| **SSR/SSG** | ❌ Невозможно | ✅ Возможно |

### Когда использовать Compose Web (Canvas)

```
✅ ИСПОЛЬЗУЙТЕ когда:
   • Нужен тот же UI на mobile + desktop + web
   • Внутренние инструменты / dashboards / SaaS
   • Не критичен SEO (приложение за логином)
   • Важна runtime performance (анимации, графики)

❌ НЕ ИСПОЛЬЗУЙТЕ когда:
   • Нужен SEO (landing pages, блоги)
   • Важна accessibility (государственные сайты)
   • Поддержка очень старых браузеров
   • Маркетинговый сайт
```

---

## Быстрый старт

### Entry Point

```kotlin
// wasmJsMain/kotlin/main.kt
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.window.CanvasBasedWindow

@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    CanvasBasedWindow(canvasElementId = "ComposeTarget") {
        App()  // Shared Composable из commonMain
    }
}
```

### HTML Host

```html
<!-- wasmJsMain/resources/index.html -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Compose Web App</title>
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
        /* Loading screen */
        .loading {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
        }
    </style>
</head>
<body>
    <div class="loading" id="loading">Loading...</div>
    <canvas id="ComposeTarget"></canvas>
    <script>
        // Hide loading when Wasm is ready
        window.onload = () => {
            document.getElementById('loading').style.display = 'none';
        };
    </script>
    <script src="composeApp.js"></script>
</body>
</html>
```

### Gradle конфигурация

```kotlin
// composeApp/build.gradle.kts
import org.jetbrains.kotlin.gradle.ExperimentalWasmDsl

plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose") version "1.9.0"
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.0"
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
    }
}
```

### Команды

```bash
# Development (hot reload)
./gradlew wasmJsBrowserDevelopmentRun

# Production build
./gradlew wasmJsBrowserDistribution

# Output: composeApp/build/dist/wasmJs/productionExecutable/
```

---

## Beta Features (CMP 1.9.0+)

### 1. Type-Safe Navigation с Deep Linking

```kotlin
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToDetails = { id ->
                    navController.navigate("details/$id")
                }
            )
        }

        composable("details/{id}") { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id")
            DetailsScreen(id = id)
        }
    }
}
```

**Результат в URL:**
- `https://app.com/` → HomeScreen
- `https://app.com/details/123` → DetailsScreen с id=123
- Кнопки Forward/Back браузера работают

### 2. HTML Interop

```kotlin
import androidx.compose.ui.interop.HtmlView
import org.w3c.dom.HTMLDivElement

@Composable
fun HtmlInteropExample() {
    Column {
        // Compose content
        Text("Compose UI above")

        // Native HTML element
        HtmlView(
            factory = { document ->
                (document.createElement("div") as HTMLDivElement).apply {
                    innerHTML = "<p>Native HTML content</p>"
                    style.color = "blue"
                }
            },
            modifier = Modifier.fillMaxWidth().height(100.dp)
        )

        // More Compose content
        Text("Compose UI below")
    }
}
```

### 3. Dark Mode / System Preferences

```kotlin
import androidx.compose.foundation.isSystemInDarkTheme

@Composable
fun App() {
    val isDark = isSystemInDarkTheme()  // Автоматически из браузера

    MaterialTheme(
        colorScheme = if (isDark) darkColorScheme() else lightColorScheme()
    ) {
        // UI автоматически адаптируется к настройкам браузера/OS
        Content()
    }
}
```

### 4. Accessibility (базовая)

```kotlin
@Composable
fun AccessibleButton(
    onClick: () -> Unit,
    label: String
) {
    Button(
        onClick = onClick,
        modifier = Modifier.semantics {
            contentDescription = label
            role = Role.Button
        }
    ) {
        Text(label)
    }
}
```

> **Важно:** Accessibility в Canvas-based rendering имеет ограничения. Screen readers могут не "видеть" всю структуру UI. Для критичных accessibility требований рассмотрите Compose HTML.

---

## Compatibility Mode

### Wasm + JS Fallback

```kotlin
// build.gradle.kts
kotlin {
    // Kotlin/JS для старых браузеров
    js {
        browser()
        binaries.executable()
    }

    // Kotlin/Wasm для современных браузеров
    @OptIn(ExperimentalWasmDsl::class)
    wasmJs {
        browser()
        binaries.executable()
    }

    sourceSets {
        // webMain для общего кода (Kotlin 2.2.20+)
        val webMain by creating {
            dependsOn(commonMain.get())
        }
        jsMain.get().dependsOn(webMain)
        wasmJsMain.get().dependsOn(webMain)
    }
}
```

### Runtime Detection

```html
<script>
    // Проверка поддержки WasmGC
    async function detectWasmGC() {
        try {
            // Feature detection для WasmGC
            const bytes = new Uint8Array([0,97,115,109,1,0,0,0]);
            await WebAssembly.compile(bytes);
            return true;
        } catch {
            return false;
        }
    }

    detectWasmGC().then(supported => {
        if (supported) {
            // Load Wasm version (faster)
            import('./composeApp-wasm.js');
        } else {
            // Load JS fallback
            import('./composeApp-js.js');
        }
    });
</script>
```

---

## Performance

### Benchmarks

| Метрика | Kotlin/Wasm | Kotlin/JS |
|---------|-------------|-----------|
| UI rendering | ~3x faster | Baseline |
| Animations | Smooth 60 FPS | May drop |
| Initial load | 1-3 seconds | 0.5-1 second |
| After cache | 1-1.5 seconds | ~0.5 second |
| Bundle size | 2-5 MB | 1-3 MB |

### Оптимизация Initial Load

```html
<!-- 1. Loading Screen (CSS-based) -->
<style>
    .splash {
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #121212;
        color: white;
        font-family: system-ui;
    }
    .spinner {
        width: 50px;
        height: 50px;
        border: 3px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
</style>

<body>
    <div class="splash" id="splash">
        <div class="spinner"></div>
    </div>
    <canvas id="ComposeTarget" style="display:none"></canvas>
</body>
```

```kotlin
// В main.kt после инициализации
@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    // Hide splash, show canvas
    document.getElementById("splash")?.apply {
        style.display = "none"
    }
    document.getElementById("ComposeTarget")?.apply {
        style.display = "block"
    }

    CanvasBasedWindow(canvasElementId = "ComposeTarget") {
        App()
    }
}
```

### Server Configuration

```nginx
# nginx.conf - Enable Brotli compression
gzip on;
gzip_types application/wasm application/javascript;

# Brotli (лучше для Wasm)
brotli on;
brotli_types application/wasm application/javascript;

# Caching
location ~* \.(wasm|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

---

## Ограничения

### 1. SEO

```
⚠️ CANVAS НЕ ИНДЕКСИРУЕТСЯ

Весь контент рисуется на Canvas, который search engines
не могут парсить. Google видит только пустой <canvas>.

Workarounds:
• Landing page на обычном HTML
• Structured data в <head>
• Pre-rendered статический контент
• Server-side rendered альтернатива для public pages
```

### 2. Accessibility

```
⚠️ ОГРАНИЧЕННАЯ ACCESSIBILITY

Screen readers не могут напрямую читать Canvas.
Beta включает базовую поддержку, но не полную WCAG compliance.

Workarounds:
• Semantic properties в Compose
• ARIA labels через HTML interop
• Альтернативный текстовый контент
• Тестирование с реальными assistive technologies
```

### 3. DevTools

```
⚠️ CHROME DEVTOOLS НЕ ВИДЯТ COMPOSE UI

Elements panel показывает только <canvas>.
Lighthouse даёт неполные результаты.

Workarounds:
• Compose Layout Inspector (Android Studio)
• Console logging
• Custom debug overlays
```

### 4. Bundle Size

```
Типичные размеры:

Compose Web (Wasm):
├── .wasm file:     ~2-4 MB
├── .js loader:     ~100 KB
└── Compressed:     ~500 KB - 1 MB

vs Native Web:
├── React app:      ~200-500 KB
└── Vanilla JS:     ~50-200 KB

Mitigation:
• Compression (Brotli preferred)
• Code splitting (в разработке)
• Lazy loading (в разработке)
```

---

## Альтернативы для Web

### Compose HTML (DOM-based)

```kotlin
// Compose HTML — DOM rendering, не Canvas
// Работает с SEO, accessibility, но НЕ shared UI

import org.jetbrains.compose.web.dom.*
import org.jetbrains.compose.web.css.*

@Composable
fun ComposeHtmlExample() {
    Div({ style { padding(16.px) } }) {
        H1 { Text("This is DOM-based") }
        P { Text("Accessible and SEO-friendly") }
    }
}
```

### Kobweb (Compose HTML + SSG)

```kotlin
// Kobweb добавляет routing, SSG, и многое другое
// к Compose HTML

// https://kobweb.varabyte.com/

// Преимущества:
// • Static Site Generation
// • SEO-friendly
// • Markdown support
// • Server-side features
```

### Kilua (Compose-like для DOM)

```kotlin
// https://github.com/rjaros/kilua
// Composable web framework для Kotlin/Wasm и Kotlin/JS
// DOM-based с типобезопасными компонентами
```

### Decision Matrix

| Цель | Решение |
|------|---------|
| Shared UI mobile+desktop+web | Compose Multiplatform (Canvas) |
| Web-only с SEO | Compose HTML / Kobweb |
| SaaS / Internal tools | Compose Multiplatform (Canvas) |
| Marketing site | Compose HTML / Kobweb / Plain HTML |
| Maximum accessibility | Compose HTML / Kobweb |

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

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build
        run: ./gradlew wasmJsBrowserDistribution

      - name: Deploy
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./composeApp/build/dist/wasmJs/productionExecutable
```

### Netlify/Vercel

```toml
# netlify.toml
[build]
  command = "./gradlew wasmJsBrowserDistribution"
  publish = "composeApp/build/dist/wasmJs/productionExecutable"

[[headers]]
  for = "/*.wasm"
  [headers.values]
    Content-Type = "application/wasm"
    Cache-Control = "public, max-age=31536000, immutable"
```

### Cloudflare Workers

```javascript
// worker.js — serve from R2/KV
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname === '/' ? '/index.html' : url.pathname;

    const response = await env.BUCKET.get(path);
    if (!response) return new Response('Not Found', { status: 404 });

    const headers = new Headers();
    if (path.endsWith('.wasm')) {
      headers.set('Content-Type', 'application/wasm');
      headers.set('Cache-Control', 'public, max-age=31536000');
    }

    return new Response(response.body, { headers });
  }
};
```

---

## Production Apps

| Приложение | Описание | Ссылка |
|------------|----------|--------|
| **Kotlin Playground** | IDE в браузере | [play.kotlinlang.org](https://play.kotlinlang.org/) |
| **KotlinConf App** | Web версия конференции | [kotlinconf.com](https://kotlinconf.com/) |
| **Rijksmuseum Demo** | Галерея изображений | JetBrains demo |

---

## Мифы и заблуждения

### Миф 1: "Canvas rendering = плохой web app"

**Заблуждение:** "Настоящие веб-приложения строятся на DOM"

**Реальность:**
- **Figma** — canvas-based, один из лучших design tools
- **Google Docs** — canvas rendering для document view
- **Excalidraw** — canvas-based collaborative whiteboard
- Для SaaS/internal tools canvas — отличный выбор

---

### Миф 2: "SEO невозможен — это критично"

**Заблуждение:** "Без SEO приложение бесполезно"

**Реальность:**
- SEO критичен для: landing pages, blogs, e-commerce
- SEO **не нужен** для: SaaS apps за логином, internal tools, dashboards
- Workaround: Landing page на HTML/Kobweb + app на Compose Web

```
Пример архитектуры:
• marketing.example.com → Kobweb (SEO-friendly)
• app.example.com → Compose Web (shared UI)
```

---

### Миф 3: "WebAssembly не поддерживается"

**Заблуждение:** "WasmGC слишком новый, Safari не поддерживает"

**Реальность:** WasmGC поддерживается **всеми major browsers** с декабря 2024:
- Chrome 119+ (Nov 2023)
- Firefox 120+ (Nov 2023)
- Edge 119+ (Nov 2023)
- **Safari 18.2+** (Dec 2024) — последний major browser

Compatibility mode позволяет fallback на JS для старых браузеров.

---

### Миф 4: "Initial load 3 секунды — это неприемлемо"

**Заблуждение:** "Пользователи уйдут пока грузится Wasm"

**Реальность:**
- Loading screen скрывает wait time
- После первой загрузки — кэширование (1-1.5 сек)
- Runtime performance ~3x быстрее JS — компенсирует
- Для SPA (Single Page App) initial load — один раз за сессию

---

### Миф 5: "Accessibility невозможна с Canvas"

**Заблуждение:** "Screen readers не видят canvas"

**Реальность:**
- Beta включает базовую accessibility поддержку
- Semantic properties транслируются в ARIA
- Для критичной accessibility — использовать Compose HTML / Kobweb
- Большинство SaaS apps не требуют WCAG AAA compliance

---

### Миф 6: "Beta = нельзя в production"

**Заблуждение:** "Beta статус означает нестабильность"

**Реальность:**
- **Kotlin Playground** — production на Compose Web
- **KotlinConf app** — web версия работает
- Beta означает: API может меняться, но работает стабильно
- Для internal tools риск минимален

---

## Production Checklist

```markdown
## Перед релизом

### Build
- [ ] Production build (не development)
- [ ] Compression enabled (Brotli/gzip)
- [ ] Assets cached with immutable headers

### Performance
- [ ] Loading screen для initial load
- [ ] Тестирование на разных браузерах
- [ ] Тестирование на слабых устройствах

### Browser Support
- [ ] Chrome 119+ тест
- [ ] Firefox 120+ тест
- [ ] Safari 18.2+ тест
- [ ] Edge 119+ тест
- [ ] Compatibility mode для старых браузеров (если нужно)

### UX
- [ ] Loading indicator
- [ ] Error handling для failed Wasm load
- [ ] Fallback message для unsupported browsers

### Optional
- [ ] Analytics integration
- [ ] Error tracking (Sentry и др.)
- [ ] Performance monitoring
```

---

## Рекомендуемые источники

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Compose MP 1.9.0 Release](https://blog.jetbrains.com/kotlin/2025/09/compose-multiplatform-1-9-0-compose-for-web-beta/) | Official | Web Beta announcement |
| [Kotlin/Wasm Overview](https://kotlinlang.org/docs/wasm-overview.html) | Official | Wasm documentation |
| [Get Started with Wasm](https://kotlinlang.org/docs/wasm-get-started.html) | Official | Quick start guide |
| [Choosing Web Target](https://www.jetbrains.com/help/kotlin-multiplatform-dev/choosing-web-target.html) | Official | JS vs Wasm decision |

### Блоги и статьи

| Источник | Тип | Описание |
|----------|-----|----------|
| [KMPShip Web Guide](https://www.kmpship.app/blog/kotlin-wasm-and-compose-web-2025) | Blog | Практический гайд 2025 |
| [Present and Future of Kotlin for Web](https://blog.jetbrains.com/kotlin/2025/05/present-and-future-kotlin-for-web/) | Official | Roadmap |
| [C4W: Maybe You Shouldn't Use](https://bitspittle.dev/blog/2024/c4w) | Blog | Критический анализ Canvas approach |

### Альтернативы

| Ресурс | Описание |
|--------|----------|
| [Kobweb](https://kobweb.varabyte.com/) | Compose HTML framework с SSG |
| [Kilua](https://github.com/rjaros/kilua) | Composable DOM framework |
| [kotlin-wasm-compose-template](https://github.com/Kotlin/kotlin-wasm-compose-template) | Официальный шаблон |

### CS-фундамент

| Концепция | Зачем изучать | Где применяется |
|-----------|--------------|-----------------|
| [[webassembly-internals]] | Wasm bytecode, WasmGC | Runtime execution |
| [[browser-rendering-engine]] | Layout, paint, composite | Performance understanding |
| [[canvas-api-graphics]] | 2D graphics в браузере | Skia → Canvas bridge |
| [[web-accessibility-fundamentals]] | ARIA, screen readers | Accessibility implementation |
| [[javascript-engine-internals]] | V8, JIT compilation | JS vs Wasm comparison |
| [[browser-caching-mechanisms]] | HTTP cache, ServiceWorker | Load time optimization |

---

## Связь с другими темами

**[[compose-mp-overview]]** — Обзор Compose Multiplatform описывает общую архитектуру фреймворка, а Web является его новейшей платформой (Beta с версии 1.9.0). Web target использует Canvas API для рендеринга через Skia, что обеспечивает визуальную идентичность с другими платформами, но создаёт уникальные вызовы: SEO, accessibility, bundle size. Понимание общей архитектуры помогает оценить trade-offs web-платформы.

**[[kmp-web-wasm]]** — Kotlin/Wasm и WasmGC являются технологическим фундаментом для Compose MP Web. Данный материал описывает UI-слой (Composable-функции, рендеринг, interop с DOM), тогда как kmp-web-wasm фокусируется на платформенном уровне (WebAssembly, JS interop, deployment). Вместе они формируют полное понимание web-разработки в экосистеме KMP.

**[[kmp-overview]]** — Обзор KMP помогает понять место Web target в мультиплатформенной стратегии. Web Beta означает, что API может измениться, и для production-приложений рекомендуется использовать его с осторожностью. Понимание общей roadmap KMP помогает спланировать поэтапное внедрение web-платформы в существующие мультиплатформенные проекты.

## Источники и дальнейшее чтение

### Теоретические основы

- **Haas A. et al. (2017).** *Bringing the Web up to Speed with WebAssembly.* PLDI '17. — WebAssembly как target для Compose Web (Canvas rendering через Wasm).
- **Elliott C., Hudak P. (1997).** *Functional Reactive Animation.* — FRP как теоретическая основа декларативного UI в браузере.

### Практические руководства

- **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* — Kotlin для web-разработки через Compose/Wasm.
- **Moskala M. (2021).** *Effective Kotlin.* — Практики Kotlin-кода для web target.
- [Kotlin/Wasm + Compose](https://kotlinlang.org/docs/wasm-overview.html) — Официальная документация.

---

## Проверь себя

> [!question]- Почему Compose MP Web рендерит через Canvas, а не генерирует HTML-элементы?
> Canvas-рендеринг через Skia обеспечивает pixel-perfect consistency с другими платформами (Android, iOS, Desktop). Генерация HTML-элементов потребовала бы отдельной layout-системы и не гарантировала бы визуальную идентичность. Trade-off: потеря SEO и нативной accessibility.

> [!question]- Клиент хочет использовать Compose MP Web для публичного маркетингового сайта. Почему это плохая идея?
> Canvas-рендеринг не индексируется поисковыми движками (плохой SEO), bundle size значительно больше HTML/CSS, нативная accessibility ограничена, а WasmGC требует современных браузеров. Для маркетинговых сайтов лучше использовать HTML/CSS/JS фреймворки.

> [!question]- Для каких типов web-приложений Compose MP Web подходит лучше всего?
> Для internal tools, dashboards, admin panels и SPA, где SEO не важен, пользователи имеют современные браузеры, и ценность shared-кода с мобильными приложениями перевешивает ограничения Canvas-рендеринга.

---

## Ключевые карточки

Как Compose MP Web рендерит UI в браузере?
?
Kotlin-код компилируется в WebAssembly (Kotlin/Wasm), Skia рендерит UI в HTML Canvas. Результат -- pixel-perfect UI, идентичный другим платформам, но невидимый для поисковых движков.

Какие ограничения имеет Compose MP Web (Beta)?
?
SEO не работает (Canvas-рендеринг), ограниченная accessibility, большой bundle size, требуется WasmGC (Chrome 119+, Firefox 120+, Safari 18.2+), не все KMP-библиотеки поддерживают wasmJs target.

Чем Compose MP Web отличается от Compose HTML?
?
Compose MP Web -- Canvas-based рендеринг через Skia с shared Composable-функциями. Compose HTML (устаревший подход) генерировал реальные HTML/DOM элементы. Compose MP Web обеспечивает код sharing, но теряет SEO.

Как DOM interop работает в Compose MP Web?
?
Через Kotlin/JS и Kotlin/Wasm external-декларации можно взаимодействовать с DOM, JavaScript-библиотеками и браузерными API. Это позволяет встраивать HTML-элементы поверх Canvas и вызывать JS-функции из Kotlin.

Почему bundle size -- проблема для Compose MP Web?
?
Wasm-бандл включает Kotlin runtime, Skia renderer и код приложения. Типичный размер начинается от нескольких мегабайт, что значительно больше минимального HTML/CSS/JS сайта. Для пользователей с медленным интернетом это критично.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-architecture-patterns]] | Архитектура для кросс-платформенных приложений |
| Углубиться | [[kmp-web-wasm]] | Платформенный фундамент: Kotlin/Wasm, WasmGC, JS interop |
| Смежная тема | [[kmp-performance-optimization]] | Оптимизация bundle size и производительности |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Compose Multiplatform 1.9.0, Kotlin/Wasm Beta, WasmGC in all browsers*
