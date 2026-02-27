---
title: "Compose Multiplatform: Shared UI для всех платформ"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - topic/android
  - ui
  - skia
  - topic/ios
  - desktop
  - web
  - type/moc
  - level/beginner
related:
  - "[[kmp-overview]]"
  - "[[compose-mp-ios]]"
  - "[[compose-mp-desktop]]"
  - "[[compose-mp-web]]"
cs-foundations:
  - "[[rendering-pipelines]]"
  - "[[declarative-ui-paradigm]]"
  - "[[graphics-apis-fundamentals]]"
  - "[[composition-recomposition]]"
status: published
reading_time: 20
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Compose Multiplatform Overview

> **TL;DR:** Compose Multiplatform (CMP) — UI фреймворк от JetBrains, расширяющий Jetpack Compose на iOS, Desktop и Web. Рендеринг через Skia (Metal на iOS, OpenGL/Vulkan на других). iOS Stable с мая 2025 (1.8.0), Web Beta с сентября 2025 (1.9.0). 95% UI кода можно шарить. Тот же API что Jetpack Compose: @Composable, remember, Row/Column, Material 3. Resources API для images, strings, fonts. Навигация: AndroidX Navigation (официальная), Voyager, Decompose.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Jetpack Compose | Базовый API | [Android Compose](https://developer.android.com/compose) |
| Kotlin Basics | Язык | [[kotlin-overview]] |
| KMP Project Structure | Структура проекта | [[kmp-project-structure]] |
| State Management | remember, mutableStateOf | [[compose-state]] |
| **CS: Rendering Pipelines** | Понять как Skia рисует UI | [[rendering-pipelines]] |
| **CS: Declarative UI** | Парадигма описания UI | [[declarative-ui-paradigm]] |
| **CS: Graphics APIs** | Metal, OpenGL, Vulkan | [[graphics-apis-fundamentals]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Compose Multiplatform** | UI framework для всех платформ | Один дизайн интерьера для всех квартир |
| **Skia** | Графическая библиотека (Chrome, Flutter) | Универсальный художник |
| **Skiko** | Kotlin bindings для Skia | Переводчик между Kotlin и Skia |
| **Composable** | Функция, описывающая UI | Рецепт блюда |
| **Recomposition** | Перерисовка при изменении state | Обновление меню при смене сезона |
| **Resources API** | Доступ к images/strings/fonts | Склад материалов для всех филиалов |

---

## Теоретические основы

### Формальное определение

> **Declarative UI Framework** — парадигма построения пользовательских интерфейсов, в которой разработчик описывает желаемое состояние UI как функцию от данных, а framework автоматически вычисляет и применяет минимальные изменения (Elliott, Hudak, 1997, Functional Reactive Programming).

Compose Multiplatform расширяет Jetpack Compose на все платформы KMP, используя Skia/Skiko как единый рендеринг-движок.

### Эволюция декларативных UI-фреймворков

| Год | Фреймворк | Платформа | Рендеринг | Ключевая идея |
|-----|----------|-----------|-----------|---------------|
| 2013 | React | Web | Virtual DOM → DOM | UI = f(state), reconciliation |
| 2017 | Flutter | Mobile + Web | Skia canvas | Widget tree, собственный rendering |
| 2019 | SwiftUI | Apple | UIKit/AppKit backend | Declarative Swift DSL |
| 2020 | Jetpack Compose | Android | Android Canvas/Skia | @Composable functions, recomposition |
| 2021 | Compose Multiplatform | All | Skia/Skiko | Расширение Compose на Desktop, iOS, Web |

### Архитектура рендеринга: Skia/Skiko

Compose Multiplatform использует **Skiko** (Skia for Kotlin) — обёртку над Skia (Google, 2005):

| Платформа | Backend Skia | Графический API |
|-----------|-------------|-----------------|
| Android | Встроенный в систему | OpenGL ES / Vulkan |
| iOS | Bundled (~9 MB) | Metal |
| Desktop | Bundled | OpenGL / Metal / DirectX |
| Web | Bundled (Canvas) | WebGL / Canvas 2D |

### Теоретическая модель: Recomposition

Recomposition в Compose реализует **incremental computation** (Demers et al., 1981): при изменении state пересчитываются только те @Composable функции, которые зависят от изменённых данных. Формально это **dataflow graph** с автоматическим invalidation.

> **Связь с теорией:** Functional Reactive Programming (Elliott, Hudak, 1997) формализует UI как поток трансформаций состояния. Compose реализует эту модель через snapshot system и slot table — внутренние структуры данных для отслеживания зависимостей.


## Почему Compose Multiplatform использует Canvas-based Rendering (Skia)

> **CS-фундамент:** Rendering Pipelines, Graphics APIs, Immediate Mode vs Retained Mode

### Фундаментальная проблема: как рисовать UI на разных платформах?

Когда вы создаёте кроссплатформенный UI фреймворк, есть **два принципиально разных подхода:**

```
ПОДХОД 1: NATIVE WIDGETS (React Native, Xamarin)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Shared Code         Platform Bridges         Native UI        │
│   ───────────        ────────────────        ─────────────      │
│                                                                 │
│   <Button>    ──►    iOS Bridge    ──►    UIButton              │
│               ──►    Android Bridge ──►   android.widget.Button │
│               ──►    Web Bridge    ──►    <button>              │
│                                                                 │
│   ✅ Выглядит native                                             │
│   ❌ Different behavior per platform                            │
│   ❌ Limited to common denominator                              │
│   ❌ Bridge overhead                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

ПОДХОД 2: CANVAS RENDERING (Flutter, Compose MP)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Shared Code         Rendering Engine        Graphics API      │
│   ───────────        ────────────────        ─────────────      │
│                                                                 │
│   @Composable  ──►    Skia/Skiko    ──►    Metal (iOS)          │
│   Button()            (2D Graphics)  ──►    Vulkan/OpenGL       │
│                                       ──►    Canvas (Web)       │
│                                                                 │
│   ✅ Pixel-perfect consistency                                  │
│   ✅ No platform limitations                                    │
│   ✅ Full control over rendering                                │
│   ⚠️ Must implement platform behaviors                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Что такое Skia и почему именно она?

**Skia** — open-source 2D графическая библиотека, разработанная Google:

```
SKIA ECOSYSTEM
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Продукты использующие Skia:                                    │
│   ─────────────────────────────                                  │
│                                                                 │
│   • Google Chrome     (весь рендеринг страниц)                   │
│   • ChromeOS          (весь UI операционной системы)             │
│   • Android           (software rendering fallback)             │
│   • Flutter           (100% рендеринга UI)                       │
│   • Firefox           (некоторые части)                          │
│   • Compose MP        (iOS, Desktop, Web)                       │
│                                                                 │
│   Почему Skia надёжна:                                           │
│   ─────────────────────                                          │
│   • 20+ лет разработки                                          │
│   • Миллиарды устройств                                          │
│   • Поддержка Google                                             │
│   • Hardware acceleration                                       │
│   • Отличное качество текста и шрифтов                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Skiko: мост между Kotlin и Skia

**Skiko** (Skia for Kotlin) — это JetBrains' bindings для Skia:

```
RENDERING STACK
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Layer 1: Your Compose Code                                    │
│   ──────────────────────────                                    │
│   @Composable fun App() { ... }                                 │
│                    │                                            │
│                    ▼                                            │
│   Layer 2: Compose UI Runtime                                   │
│   ───────────────────────────                                   │
│   UI Tree → Layout → Draw Commands                              │
│                    │                                            │
│                    ▼                                            │
│   Layer 3: Skiko (Kotlin bindings)                              │
│   ────────────────────────────────                               │
│   canvas.drawRect(), canvas.drawText()                          │
│                    │                                            │
│                    ▼                                            │
│   Layer 4: Skia (C++ library)                                   │
│   ─────────────────────────────                                  │
│   SkCanvas, SkPaint, SkPath                                     │
│                    │                                            │
│                    ▼                                            │
│   Layer 5: Graphics API                                         │
│   ─────────────────────                                          │
│   ┌──────────┬──────────┬──────────┬──────────┐                 │
│   │  Metal   │  Vulkan  │  OpenGL  │  Canvas  │                 │
│   │   iOS    │ Android/ │  Legacy  │   Web    │                 │
│   │          │ Desktop  │  Desktop │          │                 │
│   └──────────┴──────────┴──────────┴──────────┘                 │
│                    │                                            │
│                    ▼                                            │
│   Layer 6: GPU Hardware                                         │
│   ─────────────────────                                          │
│   Actual pixels on screen                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Immediate Mode vs Retained Mode Rendering

Compose использует **Retained Mode** с характеристиками **Immediate Mode:**

```
RENDERING MODES
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   IMMEDIATE MODE (классический подход):                         │
│   ─────────────────────────────────────                          │
│   Каждый frame: перерисовать ВСЁ с нуля                          │
│                                                                 │
│   while (running) {                                             │
│       clearScreen()                                             │
│       drawButton(x, y)    // рисуем заново                       │
│       drawText("Hello")   // рисуем заново                       │
│       swapBuffers()                                             │
│   }                                                             │
│                                                                 │
│   ✅ Просто понять                                               │
│   ❌ Wasteful (перерисовка unchanged elements)                   │
│                                                                 │
│   ─────────────────────────────────────────────────────────────  │
│                                                                 │
│   RETAINED MODE (Compose/Flutter):                              │
│   ─────────────────────────────────                              │
│   Хранить UI tree, перерисовывать только изменения               │
│                                                                 │
│   // Initial render                                             │
│   buildUITree() → Layout → Draw → Cache                         │
│                                                                 │
│   // State change                                               │
│   detectChanges() → Recompose ONLY changed → Redraw ONLY dirty  │
│                                                                 │
│   ✅ Efficient (minimal redraws)                                │
│   ✅ Smart invalidation                                         │
│   ⚠️ More complex internally                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему не Native Widgets для iOS?

JetBrains выбрали Skia вместо маппинга на UIKit потому что:

| Критерий | Native Widgets | Canvas (Skia) |
|----------|---------------|---------------|
| **Консистентность** | Разная на платформах | Pixel-perfect везде |
| **Контроль** | Ограничен возможностями UIKit | Полный |
| **Анимации** | Разные API | Единый API |
| **Кастомизация** | Сложная | Простая |
| **Performance** | Зависит от bridge | Предсказуемый |

**Trade-off:** +9 MB к размеру app (Skia binary), но получаете полный контроль над рендерингом.

### Hardware Acceleration: Metal на iOS

```
iOS RENDERING PATH
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Compose UI                                                    │
│        │                                                        │
│        ▼                                                        │
│   Skia draw commands                                            │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      METAL API                           │   │
│   │   ─────────────────────────────────────────────────────  │   │
│   │   • Apple's modern graphics API (replaced OpenGL ES)     │   │
│   │   • Direct GPU access                                    │   │
│   │   • Optimized for Apple Silicon                          │   │
│   │   • Lower CPU overhead than OpenGL                       │   │
│   │                                                          │   │
│   │   Pipeline:                                              │   │
│   │   1. Skia batches draw commands                          │   │
│   │   2. Commands translated to Metal shaders                │   │
│   │   3. GPU executes in parallel                            │   │
│   │   4. Result composited with system UI                    │   │
│   │                                                          │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ▼                                                        │
│   GPU → Display                                                 │
│                                                                 │
│   Performance: 60/120 FPS на современных устройствах             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему Performance сравним с Native?

96% команд **не сообщают о проблемах** с производительностью (JetBrains survey):

1. **Hardware acceleration** — Skia использует GPU напрямую
2. **Батчинг** — draw commands группируются для эффективности
3. **Smart invalidation** — перерисовка только изменённых областей
4. **Native scrolling physics** — iOS scroll behavior эмулируется точно
5. **Composition caching** — неизменные части UI кэшируются

```
PERFORMANCE COMPARISON (CMP 1.8.0+)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Metric           │ Compose MP    │ SwiftUI       │ Difference │
│   ─────────────────┼───────────────┼───────────────┼────────────│
│   Startup time     │ Comparable    │ Native        │ ~same      │
│   Scroll 60 FPS    │ ✅            │ ✅            │ ~same      │
│   Scroll 120 FPS   │ ✅            │ ✅            │ ~same      │
│   Animation fluidity│ Smooth       │ Smooth        │ ~same      │
│   Memory usage     │ Similar       │ Similar       │ ~same      │
│   App size         │ +9 MB         │ 0 (system)    │ +9 MB      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Статус платформ (январь 2026)

```
┌─────────────────────────────────────────────────────────────────────┐
│              COMPOSE MULTIPLATFORM PLATFORM STATUS                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Platform        Status      Version    Rendering                 │
│   ─────────────────────────────────────────────────────────         │
│   Android         ✅ Stable    1.10.0     Native Compose            │
│   iOS             ✅ Stable    1.8.0+     Skia via Metal            │
│   Desktop         ✅ Stable    1.8.0+     Skia via OpenGL/Vulkan    │
│   Web (Wasm)      🧪 Beta      1.9.0+     Skia via Canvas           │
│   Web (JS)        🧪 Beta      1.9.0+     Skia via Canvas           │
│                                                                     │
│   Requirements:                                                     │
│   • Kotlin 2.1.0+ (K2 compiler required)                            │
│   • Compose Multiplatform 1.8.0+                                    │
│   • Android Studio Meerkat+ или IntelliJ IDEA 2025.1+               │
│                                                                     │
│   Latest: Compose Multiplatform 1.10.0-rc02 (December 2025)         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Compose Multiplatform vs Jetpack Compose

| Аспект | Jetpack Compose | Compose Multiplatform |
|--------|----------------|----------------------|
| **Платформы** | Только Android | Android, iOS, Desktop, Web |
| **Создатель** | Google | JetBrains |
| **API** | @Composable, Material 3 | Тот же API |
| **Рендеринг** | Android native | Skia (кроме Android) |
| **Resources** | `R.drawable`, `R.string` | `Res.drawable`, `Res.string` |
| **Статус** | Stable | Stable (кроме Web: Beta) |

### Совместимость

```kotlin
// При сборке под Android, CMP автоматически использует Jetpack artifacts:
// compose.material3 →
//   Android: androidx.compose.material3:material3
//   iOS/Desktop/Web: org.jetbrains.compose.material3:material3
```

**Важно:** Знание Jetpack Compose напрямую переносится на Compose Multiplatform!

---

## Как работает: Архитектура

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPOSE MULTIPLATFORM ARCHITECTURE               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │              @Composable Functions                       │       │
│   │        (Declarative UI Description)                      │       │
│   └────────────────────────┬────────────────────────────────┘       │
│                            ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │                   UI Tree                                │       │
│   │        (Hierarchy of UI Elements)                        │       │
│   └────────────────────────┬────────────────────────────────┘       │
│                            ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │              Layout & Measurement                        │       │
│   │        (Size & Position Calculation)                     │       │
│   └────────────────────────┬────────────────────────────────┘       │
│                            ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │                 Draw Commands                            │       │
│   │        (What to Draw, Where)                             │       │
│   └────────────────────────┬────────────────────────────────┘       │
│                            ▼                                        │
│   ┌─────────────────────────────────────────────────────────┐       │
│   │            SKIKO (Skia for Kotlin)                       │       │
│   │                                                          │       │
│   │   ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐    │       │
│   │   │ Metal   │  │ OpenGL  │  │ Vulkan  │  │ Canvas  │    │       │
│   │   │  iOS    │  │ Desktop │  │ Desktop │  │   Web   │    │       │
│   │   └─────────┘  └─────────┘  └─────────┘  └─────────┘    │       │
│   │                                                          │       │
│   └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│   Android: Uses native Jetpack Compose (not Skia)                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Skia

**Skia** — open-source 2D graphics library, используемая в:
- Google Chrome
- ChromeOS
- Flutter
- Android (software rendering)
- Compose Multiplatform

**Преимущества:**
- Консистентный рендеринг на всех платформах
- Hardware acceleration
- Высокое качество шрифтов и графики

---

## Быстрый старт

### 1. Создание проекта

```bash
# Использовать KMP Wizard
# https://kmp.jetbrains.com/?platforms=android,ios,desktop,web
```

### 2. Базовая структура

```
composeApp/
├── build.gradle.kts
└── src/
    ├── commonMain/kotlin/       # Shared UI
    │   ├── App.kt
    │   └── theme/
    ├── androidMain/kotlin/      # Android entry point
    ├── iosMain/kotlin/          # iOS entry point
    ├── desktopMain/kotlin/      # Desktop entry point
    └── wasmJsMain/kotlin/       # Web entry point
```

### 3. Shared Composable

```kotlin
// commonMain/kotlin/App.kt
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

### 4. Platform Entry Points

**Android:**
```kotlin
// androidMain/kotlin/MainActivity.kt
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            App()
        }
    }
}
```

**iOS:**
```kotlin
// iosMain/kotlin/MainViewController.kt
fun MainViewController() = ComposeUIViewController { App() }
```

**Desktop:**
```kotlin
// desktopMain/kotlin/main.kt
fun main() = application {
    Window(onCloseRequest = ::exitApplication, title = "My App") {
        App()
    }
}
```

**Web (Wasm):**
```kotlin
// wasmJsMain/kotlin/main.kt
@OptIn(ExperimentalComposeUiApi::class)
fun main() {
    CanvasBasedWindow(canvasElementId = "ComposeTarget") {
        App()
    }
}
```

---

## Resources API

### Настройка

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(compose.components.resources)
        }
    }
}
```

### Структура ресурсов

```
composeApp/src/commonMain/
└── composeResources/
    ├── drawable/
    │   ├── logo.png
    │   └── icon.xml          # Android Vector XML
    ├── font/
    │   ├── Roboto-Regular.ttf
    │   └── Roboto-Bold.ttf
    ├── values/
    │   └── strings.xml
    └── values-ru/
        └── strings.xml       # Локализация
```

### Использование

```kotlin
// Автоматически генерируется Res object

// Images
Image(
    painter = painterResource(Res.drawable.logo),
    contentDescription = "Logo"
)

// Strings
Text(stringResource(Res.string.app_name))

// Fonts
val customFont = FontFamily(Font(Res.font.Roboto_Regular))
Text(
    text = "Custom Font",
    fontFamily = customFont
)
```

### strings.xml

```xml
<!-- composeResources/values/strings.xml -->
<resources>
    <string name="app_name">My App</string>
    <string name="welcome_message">Welcome, %s!</string>
    <string name="items_count">You have %d items</string>
</resources>
```

```kotlin
// Использование с форматированием
Text(stringResource(Res.string.welcome_message, userName))
Text(stringResource(Res.string.items_count, itemCount))
```

### Qualifiers

| Qualifier | Пример | Описание |
|-----------|--------|----------|
| Language | `values-ru/` | Локализация |
| Theme | `drawable-dark/` | Dark mode |
| Density | `drawable-hdpi/` | Screen density |

---

## Навигация

### Официальная: AndroidX Navigation

```kotlin
// build.gradle.kts
commonMain.dependencies {
    implementation("org.jetbrains.androidx.navigation:navigation-compose:2.9.1")
}
```

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(onNavigateToDetails = { id ->
                navController.navigate("details/$id")
            })
        }
        composable("details/{id}") { backStackEntry ->
            val id = backStackEntry.arguments?.getString("id")
            DetailsScreen(id = id)
        }
    }
}
```

### Альтернативы

| Библиотека | Подход | Лучше для |
|------------|--------|-----------|
| **AndroidX Navigation** | Jetpack-style | Familiar for Android devs |
| **Voyager** | Stack-based, простой | Quick setup, Compose-centric |
| **Decompose** | Component-based, flexible | Complex apps, native + Compose |
| **PreCompose** | Jetpack-like | Easy migration |

### Voyager пример

```kotlin
// build.gradle.kts
commonMain.dependencies {
    implementation("cafe.adriel.voyager:voyager-navigator:1.0.0")
}
```

```kotlin
class HomeScreen : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow

        Button(onClick = { navigator.push(DetailsScreen()) }) {
            Text("Go to Details")
        }
    }
}

class DetailsScreen : Screen {
    @Composable
    override fun Content() {
        val navigator = LocalNavigator.currentOrThrow

        Button(onClick = { navigator.pop() }) {
            Text("Go Back")
        }
    }
}

// Entry point
@Composable
fun App() {
    Navigator(HomeScreen())
}
```

---

## Theming

### Material 3

```kotlin
// commonMain/kotlin/theme/Theme.kt
@Composable
fun AppTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) {
        darkColorScheme(
            primary = Purple80,
            secondary = PurpleGrey80,
            tertiary = Pink80
        )
    } else {
        lightColorScheme(
            primary = Purple40,
            secondary = PurpleGrey40,
            tertiary = Pink40
        )
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content
    )
}
```

### Custom Typography

```kotlin
val Typography = Typography(
    bodyLarge = TextStyle(
        fontFamily = FontFamily(Font(Res.font.Roboto_Regular)),
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp
    ),
    headlineMedium = TextStyle(
        fontFamily = FontFamily(Font(Res.font.Roboto_Bold)),
        fontWeight = FontWeight.Bold,
        fontSize = 24.sp
    )
)
```

---

## Platform-specific код

### expect/actual для UI

```kotlin
// commonMain
@Composable
expect fun PlatformSpecificButton(onClick: () -> Unit)

// androidMain
@Composable
actual fun PlatformSpecificButton(onClick: () -> Unit) {
    Button(onClick = onClick) {
        Text("Android Button")
    }
}

// iosMain
@Composable
actual fun PlatformSpecificButton(onClick: () -> Unit) {
    // Можно использовать UIKit interop
    Button(onClick = onClick) {
        Text("iOS Button")
    }
}
```

### Platform checks

```kotlin
// commonMain
expect val currentPlatform: Platform

enum class Platform {
    ANDROID, IOS, DESKTOP, WEB
}

@Composable
fun PlatformAwareUI() {
    when (currentPlatform) {
        Platform.ANDROID -> AndroidSpecificUI()
        Platform.IOS -> IOSSpecificUI()
        Platform.DESKTOP -> DesktopSpecificUI()
        Platform.WEB -> WebSpecificUI()
    }
}
```

---

## Android-only компоненты

Некоторые компоненты недоступны в common code:

| Компонент | Причина | Альтернатива в CMP |
|-----------|---------|-------------------|
| `R.drawable`, `R.string` | Android resource system | `Res.drawable`, `Res.string` |
| Maps Compose | Android-specific | Platform-specific implementation |
| `BackHandler` | Android navigation | Platform-specific |
| `LocalContext` | Android Context | Dependency injection |
| RxJava compose extensions | Java library | Coroutines Flow |

---

## Hot Reload & Previews

### Hot Reload (1.8.0+)

```
✅ Мгновенные изменения UI без потери state
✅ Работает на Android, iOS Simulator, Desktop
⚠️ Требует Android Studio или IntelliJ с KMP plugin
```

### Previews

```kotlin
@Preview
@Composable
fun MyComponentPreview() {
    AppTheme {
        MyComponent()
    }
}
```

**Поддержка:**
- Android: полная поддержка в Android Studio
- Desktop: поддержка в IntelliJ IDEA
- iOS/Web: ограниченная

---

## Производительность

### Метрики (Compose Multiplatform 1.8.0+)

| Метрика | iOS | Desktop | Web |
|---------|-----|---------|-----|
| Startup | On par с native | Fast | ~1-2s |
| Scrolling | 60/120 FPS | 60 FPS | 60 FPS |
| Animations | Smooth | Smooth | Smooth |
| Size overhead | +9 MB | +15-20 MB | +500KB-1MB gzip |

### Best Practices

```kotlin
// ✅ Стабильные параметры для skip recomposition
@Stable
data class UiState(
    val items: List<Item>,
    val isLoading: Boolean
)

// ✅ remember для expensive computations
val sortedItems = remember(items) {
    items.sortedBy { it.name }
}

// ✅ derivedStateOf для computed values
val hasItems by remember {
    derivedStateOf { items.isNotEmpty() }
}

// ✅ LazyColumn для списков
LazyColumn {
    items(items, key = { it.id }) { item ->
        ItemRow(item)
    }
}
```

---

## Кто использует в production

| Компания | Продукт | Code Sharing |
|----------|---------|--------------|
| **JetBrains** | Toolbox, Fleet | Desktop apps |
| **Netflix** | Studio apps | 60% shared |
| **The Respawn** | Gaming app | 96% shared |
| **Forbes** | News app | 80%+ shared |
| **Google Docs** | iOS app | Validated |
| **Pinterest** | Features | Mobile |

---

## Версионирование

```
Compose Multiplatform releases:
• 1.10.0-rc02 (Dec 2025) - Pausable compositions, haptics
• 1.9.0 (Sep 2025) - Web Beta, iOS improvements
• 1.8.0 (May 2025) - iOS Stable, K2 compiler required
• 1.7.0 - Resources in Android assets
• 1.6.0 - Improved resources API
```

**Compatibility:**

| CMP Version | Kotlin | Jetpack Compose |
|-------------|--------|-----------------|
| 1.10.0 | 2.1.21 | ~1.7.0 |
| 1.9.0 | 2.1.0 | ~1.6.0 |
| 1.8.0 | 2.1.0 | ~1.6.0 |

---

## Мифы и заблуждения

### Миф 1: "Canvas-based rendering = плохой UX"

**Заблуждение:** "Раз CMP не использует native widgets, значит UI будет выглядеть и чувствоваться чужеродно"

**Реальность:**
- Skia обеспечивает **pixel-perfect рендеринг** — нет разницы визуально
- Native scrolling physics **эмулируется точно** — iOS пользователи не заметят разницы
- Material 3 компоненты спроектированы для ощущения naturalness
- 96% команд не сообщают о UX проблемах (JetBrains survey 2025)

```
Факт: Flutter использует тот же подход (Skia) и имеет
тысячи успешных production apps в App Store/Play Store
```

---

### Миф 2: "Compose MP медленнее native SwiftUI"

**Заблуждение:** "Дополнительный слой абстракции = потеря производительности"

**Реальность:**

| Метрика | Compose MP | SwiftUI | Разница |
|---------|-----------|---------|---------|
| Startup time | Comparable | Native | Незаметна |
| Scrolling 120Hz | ✅ Smooth | ✅ Smooth | Нет |
| Animations | 60 FPS | 60 FPS | Нет |
| Memory | Similar | Similar | Минимальна |

**Причина:** Skia использует Metal напрямую (hardware acceleration), не проходя через UIKit.

---

### Миф 3: "+9 MB — это много для iOS app"

**Заблуждение:** "Overhead Skia делает приложение слишком тяжёлым"

**Реальность:**
- Средний iOS app: 50-200 MB
- Compose MP overhead: +9 MB ≈ 5-18% от среднего размера
- Это **меньше одной high-res картинки**
- Пользователи не заметят разницу при скачивании

```
Для сравнения:
• Firebase SDK: +5-10 MB
• Google Maps SDK: +15 MB
• React Native runtime: +7-10 MB
• Compose MP Skia: +9 MB (одноразово для всего UI)
```

---

### Миф 4: "Accessibility не работает с canvas rendering"

**Заблуждение:** "VoiceOver не может читать canvas-based UI"

**Реальность:** Compose MP имеет **полную поддержку accessibility:**

| Feature | Status | Как работает |
|---------|--------|--------------|
| VoiceOver | ✅ Full | Semantic tree → iOS accessibility tree |
| AssistiveTouch | ✅ Full | Touch events маппятся корректно |
| Full Keyboard Access | ✅ Full | Focus management встроен |
| Voice Control | ✅ Full | Actions exposed через semantics |

Compose semantic tree синхронизируется с iOS accessibility tree.

---

### Миф 5: "Нельзя использовать native iOS компоненты"

**Заблуждение:** "Выбрав Compose MP, вы заперты в его экосистеме"

**Реальность:** Interop работает в обе стороны:

```kotlin
// Compose → iOS: показать SwiftUI view в Compose
@Composable
fun UseNativeMapView() {
    UIKitViewController(
        factory = { MKMapView() },  // Native UIKit
        modifier = Modifier.height(200.dp)
    )
}

// iOS → Compose: использовать Compose в SwiftUI
// Swift:
struct ContentView: View {
    var body: some View {
        ComposeView()  // Compose content
            .ignoresSafeArea()
    }
}
```

**"Punch hole" interop** позволяет native компонентам "просвечивать" через Compose surface.

---

### Миф 6: "Web Beta = нельзя использовать"

**Заблуждение:** "Если Web в Beta, то весь CMP нестабилен"

**Реальность:**
- **iOS: Stable** (с мая 2025, v1.8.0)
- **Desktop: Stable** (с 2024)
- **Android: Stable** (использует Jetpack Compose)
- **Web: Beta** — означает "работает, но API может меняться"

Можно игнорировать Web target и иметь полностью production-ready iOS + Android.

---

### Миф 7: "Navigation библиотеки — это хаос"

**Заблуждение:** "Нет единого стандарта, каждый проект выбирает разное"

**Реальность:** В 2025 есть **официальная рекомендация:**

| Ситуация | Рекомендация |
|----------|-------------|
| Новый проект | **AndroidX Navigation** (official) |
| Простой app | Voyager |
| Сложная архитектура | Decompose |
| Миграция с Jetpack | AndroidX Navigation |

```kotlin
// Официальный подход (рекомендуется):
implementation("org.jetbrains.androidx.navigation:navigation-compose:2.9.1")
```

---

## Рекомендуемые источники

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Compose Multiplatform](https://www.jetbrains.com/compose-multiplatform/) | Landing | Главная страница |
| [Getting Started](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-multiplatform-getting-started.html) | Official | Быстрый старт |
| [CMP & Jetpack Compose](https://kotlinlang.org/docs/multiplatform/compose-multiplatform-and-jetpack-compose.html) | Official | Связь с Jetpack |
| [Resources API](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-multiplatform-resources.html) | Official | Работа с ресурсами |
| [GitHub](https://github.com/JetBrains/compose-multiplatform) | GitHub | Исходники, issues |

### Навигация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Navigation Docs](https://kotlinlang.org/docs/multiplatform/compose-navigation.html) | Official | AndroidX Navigation |
| [Voyager](https://github.com/adrielcafe/voyager) | Library | Pragmatic navigation |
| [Decompose](https://arkivanov.github.io/Decompose/) | Library | Component-based |

### Статьи и блоги

| Источник | Тип | Описание |
|----------|-----|----------|
| [Touchlab Transition Guide](https://touchlab.co/compose-multiplatform-transition-guide) | Expert | Миграция с Jetpack |
| [KMPShip Blog](https://www.kmpship.app/blog/) | Blog | Практические гайды |
| [JetBrains Blog](https://blog.jetbrains.com/kotlin/) | Official | Анонсы |

### CS-фундамент

| Концепция | Зачем изучать | Где применяется в CMP |
|-----------|--------------|----------------------|
| [[rendering-pipelines]] | Понять как Skia рисует UI | Весь rendering stack |
| [[declarative-ui-paradigm]] | Понять @Composable подход | Compose UI model |
| [[graphics-apis-fundamentals]] | Metal, OpenGL, Vulkan basics | Platform-specific rendering |
| [[composition-recomposition]] | Как Compose обновляет UI | State management, performance |
| [[immediate-vs-retained-mode]] | Два подхода к rendering | Понимание Compose internals |
| [[hardware-acceleration]] | GPU rendering | Почему Skia быстрая |

---

## Связь с другими темами

**[[kmp-overview]]** — Kotlin Multiplatform является фундаментом, на котором построен Compose Multiplatform. KMP обеспечивает shared бизнес-логику (networking, data, domain), тогда как Compose MP добавляет shared UI поверх этого фундамента. Понимание архитектуры KMP (source sets, expect/actual, Kotlin/Native) необходимо для правильной организации Compose MP проекта и разграничения UI и бизнес-логики.

**[[compose-mp-ios]]** — iOS является ключевой платформой для Compose Multiplatform, достигшей Stable статуса в версии 1.8.0. Compose MP на iOS использует Skia для рендеринга через Metal API, что обеспечивает нативную производительность. Понимание iOS-специфичных особенностей (UIKit interop, gesture handling, accessibility) необходимо для создания production-ready приложений с shared UI.

**[[compose-mp-desktop]]** — Desktop является наиболее зрелой платформой Compose Multiplatform, используемой JetBrains в собственных продуктах (Toolbox, Fleet). Desktop target работает на JVM через Skia и поддерживает Swing interop, нативные меню и window management. Изучение desktop-платформы помогает понять возможности Compose MP без iOS/web-ограничений.

**[[compose-mp-web]]** — Web (Beta) представляет собой новейшую платформу Compose Multiplatform, использующую Canvas API через Kotlin/Wasm. Web target демонстрирует ограничения Compose MP подхода (SEO, accessibility, bundle size) и помогает оценить, когда shared UI оправдан, а когда лучше использовать платформенные технологии.

## Источники и дальнейшее чтение

### Теоретические основы

- **Elliott C., Hudak P. (1997).** *Functional Reactive Animation.* ICFP '97. — Теоретическая основа декларативного UI: UI как функция состояния.
- **Martin R. (2017).** *Clean Architecture.* — Принципы разделения UI и бизнес-логики, определяющие архитектуру Compose MP приложений.

### Практические руководства

- **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* — Основы Kotlin для @Composable функций, delegation, DSL builders.
- **Moskala M. (2021).** *Effective Kotlin.* — Практические рекомендации для Composable-функций: state management, side effects.
- [Compose Multiplatform](https://www.jetbrains.com/compose-multiplatform/) — Официальная документация JetBrains.

---

*Проверено: 2026-01-09 | Compose Multiplatform 1.10.0, Kotlin 2.1.21, iOS Stable, Web Beta*

---

## Проверь себя

> [!question]- Почему JetBrains выбрали canvas-based rendering (Skia) вместо маппинга на нативные виджеты (UIButton, UILabel)? Какие trade-off'ы это создаёт по сравнению с подходом React Native?
> Canvas-based rendering даёт pixel-perfect консистентность на всех платформах, полный контроль над рендерингом и предсказуемую производительность без bridge overhead. Native widgets подход (React Native) ограничен "наименьшим общим знаменателем" между платформами, разное поведение на разных ОС, и overhead от bridge между JS и нативным кодом. Trade-off Skia: +9 MB к размеру приложения (Skia binary), необходимость эмулировать платформенные behaviors (scrolling physics, gestures), и accessibility реализуется через синхронизацию semantic tree с нативным accessibility tree, а не "бесплатно" от нативных виджетов.

> [!question]- Compose Multiplatform использует Retained Mode rendering. Объясни, почему это эффективнее Immediate Mode для UI-фреймворка, и как recomposition связана с этим выбором.
> В Immediate Mode каждый кадр перерисовывает всё с нуля — расточительно для UI, где большинство элементов не меняются между кадрами. Retained Mode хранит UI tree и перерисовывает только изменившиеся части. Recomposition — это механизм Compose для реализации Retained Mode: при изменении state Compose определяет, какие @Composable функции зависят от изменённого state, и перевызывает только их (smart invalidation). Неизменённые части UI кэшируются. Это даёт минимальное количество draw commands для Skia, что критично для 60/120 FPS.

> [!question]- На iOS Compose MP рендерит через Metal API, а на Android использует нативный Jetpack Compose. Почему на Android не используется Skia? Какие последствия это имеет для разработки?
> На Android Jetpack Compose уже является нативным UI-фреймворком с собственным оптимизированным rendering pipeline. Использование Skia поверх было бы избыточным — Jetpack Compose и так "рисует" UI, просто через RenderNode и Hardware Renderer Android. Последствие для разработки: на Android CMP автоматически подставляет androidx.compose артефакты вместо JetBrains' версий, поэтому поведение на Android идентично чистому Jetpack Compose. Это может создавать тонкие различия: на Android компоненты рендерятся нативно, а на iOS — через Skia, что иногда приводит к визуальным несоответствиям в edge cases (тени, blur effects, text rendering).

> [!question]- Команда переносит существующее Android-приложение на Compose Multiplatform. Какие компоненты из Jetpack Compose НЕ перенесутся в commonMain и какими альтернативами их заменить?
> Не перенесутся: 1) Android Resource system (R.drawable, R.string) — заменить на CMP Resources API (Res.drawable, Res.string). 2) LocalContext — заменить на dependency injection. 3) BackHandler — реализовать platform-specific через expect/actual. 4) Maps Compose — UIKitViewController interop на iOS. 5) RxJava compose extensions — заменить на Coroutines Flow. Также нужно учесть, что Previews работают полноценно только на Android/Desktop, а на iOS/Web — ограниченно. Навигацию можно сохранить, если использовать AndroidX Navigation (мультиплатформенная версия).

---

## Ключевые карточки

Что такое Compose Multiplatform и чем он отличается от Jetpack Compose?
?
Compose Multiplatform (CMP) — UI-фреймворк от JetBrains, расширяющий Jetpack Compose на iOS, Desktop и Web. Jetpack Compose работает только на Android с нативным рендерингом. CMP на не-Android платформах рендерит через Skia. API идентичен: @Composable, remember, Material 3. На Android CMP автоматически использует Jetpack Compose артефакты.

Что такое Skia и Skiko, и какую роль они играют в CMP?
?
Skia — open-source 2D графическая библиотека от Google (используется в Chrome, Flutter, Android). Skiko (Skia for Kotlin) — JetBrains' Kotlin bindings для Skia. Rendering stack CMP: @Composable код → Compose UI Runtime (UI Tree → Layout → Draw Commands) → Skiko → Skia (C++) → Graphics API (Metal/Vulkan/OpenGL/Canvas) → GPU.

Какие Graphics API использует CMP на разных платформах?
?
iOS: Metal (Apple's modern GPU API). Android: нативный Jetpack Compose (не Skia). Desktop: OpenGL или Vulkan. Web: Canvas API (через Kotlin/Wasm). Metal на iOS обеспечивает прямой доступ к GPU с низким CPU overhead.

В чём разница между Immediate Mode и Retained Mode rendering, и какой использует Compose?
?
Immediate Mode: каждый кадр перерисовывает всё с нуля (просто, но расточительно). Retained Mode: хранит UI tree, перерисовывает только изменения (эффективно). Compose использует Retained Mode: buildUITree → Layout → Draw → Cache, при изменении state → recompose только изменённое → redraw только dirty nodes.

Как работает Resources API в Compose Multiplatform?
?
Ресурсы размещаются в commonMain/composeResources/ (drawable/, font/, values/). Автоматически генерируется Res object. Использование: painterResource(Res.drawable.logo), stringResource(Res.string.app_name), Font(Res.font.Roboto_Regular). Поддерживаются qualifiers: языки (values-ru/), тема (drawable-dark/), плотность (drawable-hdpi/).

Какие библиотеки навигации доступны для CMP и какая рекомендуется?
?
Официальная рекомендация — AndroidX Navigation (org.jetbrains.androidx.navigation:navigation-compose). Альтернативы: Voyager (stack-based, простой, для быстрого старта), Decompose (component-based, для сложных приложений), PreCompose (Jetpack-like, для лёгкой миграции).

Каков размер overhead Skia на iOS и почему это приемлемо?
?
+9 MB к размеру приложения. Средний iOS app: 50-200 MB, значит overhead = 5-18%. Для сравнения: Firebase SDK +5-10 MB, Google Maps SDK +15 MB, React Native runtime +7-10 MB. Этот overhead одноразовый — покрывает рендеринг всего UI. Пользователи не замечают разницу при скачивании.

Как работает accessibility в CMP, если UI рисуется через canvas?
?
Compose MP имеет полную поддержку accessibility. Compose semantic tree синхронизируется с iOS accessibility tree. VoiceOver, AssistiveTouch, Full Keyboard Access и Voice Control работают полноценно. Semantics-информация из @Composable экспортируется в нативную accessibility-систему платформы.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| CMP на iOS | [[compose-mp-ios]] | Детали Skia/Metal рендеринга, UIKit interop, gesture handling |
| CMP на Desktop | [[compose-mp-desktop]] | Самая зрелая платформа CMP, Swing interop, window management |
| CMP на Web | [[compose-mp-web]] | Kotlin/Wasm, Canvas API, ограничения и перспективы |
| KMP фундамент | [[kmp-overview]] | Архитектура shared бизнес-логики под CMP |
| Навигация | [[kmp-navigation]] | Глубокое сравнение AndroidX Navigation, Decompose, Voyager |
| CS: rendering pipelines | [[rendering-pipelines]] | Понять, как Skia транслирует draw commands в пиксели на экране |
| Android Compose internals | [[android-compose-internals]] | Как работает recomposition, slot table, Composer — применимо к CMP |
