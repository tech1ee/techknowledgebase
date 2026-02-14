---
title: "Compose Multiplatform Desktop: Production-ready приложения для macOS, Windows, Linux"
created: 2026-01-03
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - topic/android
  - desktop
  - windows
  - macos
  - linux
  - skia
  - packaging
  - type/concept
  - level/intermediate
related:
  - "[[compose-mp-overview]]"
  - "[[kmp-desktop-jvm]]"
  - "[[kmp-overview]]"
prerequisites:
  - "[[compose-mp-overview]]"
  - "[[kmp-desktop-jvm]]"
cs-foundations:
  - "[[jvm-internals]]"
  - "[[graphics-apis-fundamentals]]"
  - "[[native-packaging-distribution]]"
  - "[[gui-frameworks-history]]"
status: published
reading_time: 51
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Compose Multiplatform Desktop

> **TL;DR:** Compose Desktop (Stable) создаёт нативные приложения для macOS/Windows/Linux из одного Kotlin кода. JetBrains Toolbox (1M+ пользователей) мигрировал с Electron: -50% размер installer, -200 MB RAM idle, лучшая производительность. Рендеринг через Skia + GPU (OpenGL/Metal). Desktop-specific APIs: Window management, MenuBar, Tray, Notifications. Swing/AWT interop позволяет интегрировать Compose в существующие Java приложения. Packaging через jpackage. Ограничения: нет cross-compilation, dated tray на Windows, нет rich notifications.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Compose Multiplatform Basics | Основы CMP | [[compose-mp-overview]] |
| JVM/Kotlin | Базовый Kotlin | [[kotlin-overview]] |
| Gradle | Сборка проекта | [[gradle-kotlin-dsl]] |
| KMP Desktop Integration | Платформа Desktop | [[kmp-desktop-jvm]] |
| **CS: JVM Internals** | JDK modules, jpackage | [[jvm-internals]] |
| **CS: Graphics APIs** | OpenGL, Metal, Vulkan | [[graphics-apis-fundamentals]] |
| **CS: GUI History** | Swing/AWT legacy | [[gui-frameworks-history]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Skia** | 2D graphics library для рендеринга | Художник, который рисует UI |
| **jpackage** | Инструмент создания native installers | Завод по упаковке товаров |
| **jlink** | Минимизация JDK modules | Фильтр, отсеивающий ненужное |
| **ComposePanel** | Swing container для Compose UI | Рамка для картины |
| **SwingPanel** | Compose container для Swing | Окно в стене для Swing |
| **Conveyor** | Альтернативный инструмент packaging | Другая фабрика упаковки |
| **Notarization** | Проверка Apple для macOS apps | Сертификация безопасности |

---

## Почему Compose Desktop лучше Electron для desktop apps

> **CS-фундамент:** JVM Internals, Graphics APIs, GUI Frameworks History

### Историческая проблема: как создать desktop app?

```
ЭВОЛЮЦИЯ DESKTOP FRAMEWORKS
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   1990s              2000s              2010s            NOW    │
│   ─────              ─────              ─────            ────   │
│                                                                 │
│   Win32 API    →    Java Swing    →    Electron    →   Compose │
│   MFC               Qt/GTK             NW.js            Flutter │
│   Delphi            .NET WinForms      Tauri                    │
│                     WPF                                         │
│                                                                 │
│   Platform-         Cross-             Web-based        GPU-    │
│   specific          platform           (Chromium)       native  │
│                     (heavy runtime)    (heavy RAM)      render  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Electron: почему он стал популярен и его проблемы

**Electron** = Chromium + Node.js + ваш JS код

```
ELECTRON ARCHITECTURE
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Your JS/React App                                             │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      CHROMIUM                            │   │
│   │   ─────────────────────────────────────────────────────  │   │
│   │   • Blink rendering engine                              │   │
│   │   • V8 JavaScript engine                                │   │
│   │   • Multi-process architecture                          │   │
│   │   • Network stack                                       │   │
│   │   • ~100 MB of binary                                   │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                       NODE.JS                            │   │
│   │   ─────────────────────────────────────────────────────  │   │
│   │   • V8 again (separate process)                         │   │
│   │   • Native modules                                      │   │
│   │   • File system access                                  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Результат:                                                     │
│   • 200+ MB RAM в idle                                          │
│   • Медленный startup                                           │
│   • Большой размер installer                                    │
│   • Два языка (JS + native)                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Compose Desktop: другой подход

```
COMPOSE DESKTOP ARCHITECTURE
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Your Kotlin Code                                              │
│   @Composable fun App() { ... }                                 │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                  COMPOSE RUNTIME                         │   │
│   │   ─────────────────────────────────────────────────────  │   │
│   │   • Declarative UI tree                                 │   │
│   │   • Smart recomposition                                 │   │
│   │   • State management                                    │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                      SKIKO/SKIA                          │   │
│   │   ─────────────────────────────────────────────────────  │   │
│   │   • 2D graphics library                                 │   │
│   │   • Hardware accelerated                                │   │
│   │   • ~6 MB                                               │   │
│   └─────────────────────────────────────────────────────────┘   │
│        │                                                        │
│        ▼                                                        │
│   ┌──────────┬──────────┬──────────┐                            │
│   │  Metal   │  OpenGL  │ Direct3D │                            │
│   │  macOS   │  Linux   │ Windows  │                            │
│   └──────────┴──────────┴──────────┘                            │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                   JVM (jlink'd)                          │   │
│   │   ─────────────────────────────────────────────────────  │   │
│   │   • Only needed modules                                 │   │
│   │   • Typically 30-50 MB                                  │   │
│   │   • Single language (Kotlin)                            │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Результат:                                                     │
│   • -50% размер vs Electron                                     │
│   • Значительно меньше RAM                                       │
│   • Быстрый startup                                             │
│   • Один язык end-to-end                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### JetBrains Toolbox: реальное сравнение

| Метрика | Electron (до) | Compose (после) |
|---------|--------------|-----------------|
| Installer size | ~X MB | **-50%** |
| RAM (idle) | ~200 MB | **Значительно меньше** |
| Languages | C++ + JS | **Kotlin only** |
| Codebase | 2 отдельных | **Unified** |
| Developer velocity | Медленнее | **Быстрее** |

### GPU Backends: почему это важно

Compose Desktop использует **hardware acceleration** через разные GPU APIs:

```
GPU BACKEND SELECTION
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Platform        │ Primary Backend │ Fallback                  │
│   ────────────────┼─────────────────┼───────────────────────    │
│   macOS           │ Metal           │ OpenGL                    │
│   Windows         │ Direct3D        │ OpenGL                    │
│   Linux           │ OpenGL          │ Software (CPU)            │
│                                                                 │
│   Skia выбирает автоматически лучший доступный backend.          │
│                                                                 │
│   Software fallback:                                            │
│   • Используется если нет GPU или драйверы сломаны               │
│   • Performance ~10-20 FPS на высоких разрешениях                │
│   • Рекомендуется предупреждать пользователей                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Swing/AWT Interop: зачем это нужно

Java имеет **30+ лет** истории desktop apps. Compose Desktop может:

```
INTEROP SCENARIOS
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Сценарий 1: Legacy Swing app + New Compose features           │
│   ────────────────────────────────────────────────────────────   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    JFrame (Swing)                        │   │
│   │   ┌───────────────────┬─────────────────────────────┐   │   │
│   │   │  Swing MenuBar    │                             │   │   │
│   │   ├───────────────────┤                             │   │   │
│   │   │  Swing TreeView   │   ComposePanel              │   │   │
│   │   │  (legacy code)    │   (new modern UI)           │   │   │
│   │   │                   │                             │   │   │
│   │   └───────────────────┴─────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   Сценарий 2: New Compose app + Legacy Swing widget             │
│   ────────────────────────────────────────────────────────────   │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │                    Window (Compose)                      │   │
│   │   ┌─────────────────────────────────────────────────┐   │   │
│   │   │               Compose UI                         │   │   │
│   │   │   ┌─────────────────────────────────────────┐   │   │   │
│   │   │   │   SwingPanel (legacy JTable или др.)    │   │   │   │
│   │   │   └─────────────────────────────────────────┘   │   │   │
│   │   └─────────────────────────────────────────────────┘   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Ограничение:** Heavyweight Swing components (video players, JCEF) всегда рендерятся поверх Compose.

---

## Статус (январь 2026)

```
┌─────────────────────────────────────────────────────────────────────┐
│              COMPOSE DESKTOP STATUS                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Status: ✅ STABLE                                                 │
│                                                                     │
│   Requirements:                                                     │
│   • Kotlin 2.1.0+ (K2 compiler)                                     │
│   • Compose Multiplatform 1.8.0+                                    │
│   • JDK 17+ for packaging (jpackage)                                │
│                                                                     │
│   Rendering: Skia via OpenGL/Metal/Direct3D                         │
│                                                                     │
│   Supported Platforms:                                              │
│   • macOS (x64, arm64/Apple Silicon)                                │
│   • Windows (x64, arm64)                                            │
│   • Linux (x64, arm64)                                              │
│                                                                     │
│   Package Formats:                                                  │
│   • macOS: .dmg, .pkg                                               │
│   • Windows: .exe, .msi                                             │
│   • Linux: .deb, .rpm                                               │
│                                                                     │
│   Notable Users: JetBrains Toolbox (1M+ MAU)                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## JetBrains Toolbox Case Study

Самый значимый пример Compose Desktop в production — **JetBrains Toolbox App** (1+ миллион MAU).

### История миграции

```
┌─────────────────────────────────────────────────────────────────────┐
│   2015                          2021                     NOW        │
│   ─────                         ─────                    ────       │
│                                                                     │
│   C++ business logic    →   Full migration   →   100% Kotlin       │
│   + Chromium (React)        to Kotlin              + Compose       │
│   + HTML/CSS/JS UI          + Compose                              │
│                                                                     │
│   Problems:                 Solution:              Results:         │
│   • 200 MB RAM idle         • Single language      • -50% size     │
│   • JSON serialization      • Native rendering     • Much less RAM │
│   • Two codebases           • Unified data model   • Better perf   │
│   • Different languages     • No CEF overhead                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Результаты миграции

| Метрика | До (Electron) | После (Compose) |
|---------|---------------|-----------------|
| RAM (idle) | ~200 MB | Значительно меньше |
| Installer size | ~X MB | -50% |
| Runtime performance | JS | Нативная Kotlin |
| Codebase | C++ + JS | 100% Kotlin |
| Developer experience | 2 языка | 1 язык end-to-end |

### Уроки от JetBrains

1. **Single Language Benefit**: Разработчики могут делать features от начала до конца
2. **No Serialization Overhead**: Unified data model без JSON между слоями
3. **Early Adoption Pays Off**: Same-day fixes от Compose team при обнаружении issues
4. **Material → Desktop**: Изначальные Material components заменены на desktop-optimized

---

## Быстрый старт

### Entry Point

```kotlin
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "My Desktop App"
    ) {
        App()  // Shared Composable из commonMain
    }
}
```

### Структура проекта

```
project/
├── composeApp/
│   └── src/
│       ├── commonMain/kotlin/       # Shared code
│       │   └── App.kt               # Main UI
│       └── desktopMain/kotlin/      # Desktop-specific
│           └── Main.kt              # Entry point
└── build.gradle.kts
```

### Gradle конфигурация

```kotlin
import org.jetbrains.compose.desktop.application.dsl.TargetFormat

plugins {
    kotlin("jvm")
    id("org.jetbrains.compose") version "1.8.0"
    id("org.jetbrains.kotlin.plugin.compose") version "2.1.0"
}

dependencies {
    implementation(compose.desktop.currentOs)
    implementation(compose.material3)
}

compose.desktop {
    application {
        mainClass = "MainKt"

        nativeDistributions {
            targetFormats(TargetFormat.Dmg, TargetFormat.Msi, TargetFormat.Deb)
            packageName = "MyApp"
            packageVersion = "1.0.0"
        }
    }
}
```

---

## Desktop-Specific APIs

### Window Management

```kotlin
import androidx.compose.ui.window.*
import androidx.compose.ui.unit.DpSize
import androidx.compose.ui.unit.dp

fun main() = application {
    // Declarative window state
    val windowState = rememberWindowState(
        size = DpSize(800.dp, 600.dp),
        position = WindowPosition(100.dp, 100.dp)
    )

    Window(
        onCloseRequest = ::exitApplication,
        state = windowState,
        title = "My App",
        resizable = true,
        undecorated = false,   // Без системной рамки
        transparent = false,   // Прозрачный фон
        alwaysOnTop = false
    ) {
        App()
    }
}
```

### Multi-Window Support

```kotlin
fun main() = application {
    var showSettings by remember { mutableStateOf(false) }

    // Main window
    Window(
        onCloseRequest = ::exitApplication,
        title = "Main Window"
    ) {
        Button(onClick = { showSettings = true }) {
            Text("Open Settings")
        }
    }

    // Conditional second window
    if (showSettings) {
        Window(
            onCloseRequest = { showSettings = false },
            title = "Settings"
        ) {
            SettingsScreen()
        }
    }
}
```

### MenuBar

```kotlin
import androidx.compose.ui.input.key.*
import androidx.compose.ui.window.*

Window(onCloseRequest = ::exitApplication) {
    MenuBar {
        Menu("File", mnemonic = 'F') {
            Item(
                text = "New",
                onClick = { /* Handle */ },
                shortcut = KeyShortcut(Key.N, ctrl = true)
            )
            Item(
                text = "Open",
                onClick = { /* Handle */ },
                shortcut = KeyShortcut(Key.O, ctrl = true)
            )
            Separator()
            Item(
                text = "Exit",
                onClick = ::exitApplication,
                shortcut = KeyShortcut(Key.Q, ctrl = true)
            )
        }

        Menu("Edit", mnemonic = 'E') {
            Item("Cut", onClick = {}, shortcut = KeyShortcut(Key.X, ctrl = true))
            Item("Copy", onClick = {}, shortcut = KeyShortcut(Key.C, ctrl = true))
            Item("Paste", onClick = {}, shortcut = KeyShortcut(Key.V, ctrl = true))
        }

        Menu("View") {
            CheckboxItem(
                text = "Show Toolbar",
                checked = showToolbar,
                onCheckedChange = { showToolbar = it }
            )
        }
    }

    App()
}
```

### System Tray

```kotlin
import androidx.compose.ui.window.*

fun main() = application {
    val trayState = rememberTrayState()

    val notification = rememberNotification(
        title = "My App",
        message = "Task completed!"
    )

    Tray(
        state = trayState,
        icon = painterResource("icon.png"),
        tooltip = "My App",
        menu = {
            Item("Show Notification") {
                trayState.sendNotification(notification)
            }
            Separator()
            Item("Exit") { exitApplication() }
        }
    )

    Window(onCloseRequest = ::exitApplication) {
        App()
    }
}
```

### Notification Types

```kotlin
// Info notification
val infoNotification = Notification(
    title = "Info",
    message = "Operation completed",
    type = Notification.Type.Info
)

// Warning notification
val warnNotification = Notification(
    title = "Warning",
    message = "Check your settings",
    type = Notification.Type.Warning
)

// Error notification
val errorNotification = Notification(
    title = "Error",
    message = "Something went wrong",
    type = Notification.Type.Error
)
```

---

## Swing/AWT Interoperability

### Embed Compose в Swing (ComposePanel)

```kotlin
import androidx.compose.ui.awt.ComposePanel
import javax.swing.JFrame
import javax.swing.SwingUtilities

fun main() = SwingUtilities.invokeLater {
    val frame = JFrame("Swing + Compose")

    val composePanel = ComposePanel().apply {
        setContent {
            // Compose content inside Swing
            MaterialTheme {
                Surface {
                    Text("Hello from Compose!")
                }
            }
        }
    }

    frame.contentPane.add(composePanel)
    frame.setSize(800, 600)
    frame.defaultCloseOperation = JFrame.EXIT_ON_CLOSE
    frame.isVisible = true
}
```

### Embed Swing в Compose (SwingPanel)

```kotlin
import androidx.compose.ui.awt.SwingPanel
import javax.swing.JButton

@Composable
fun SwingButtonInCompose() {
    SwingPanel(
        factory = {
            JButton("Swing Button").apply {
                addActionListener {
                    println("Swing button clicked!")
                }
            }
        },
        modifier = Modifier.size(200.dp, 50.dp)
    )
}
```

### Use Cases для Interop

| Сценарий | Подход |
|----------|--------|
| Новое Compose UI в старом Swing app | ComposePanel |
| Legacy Swing widget в Compose | SwingPanel |
| Gradual migration | Комбинация обоих |
| Video player (heavyweight) | SwingPanel с ограничениями |

### Ограничения Interop

```
⚠️ HEAVYWEIGHT COMPONENTS (Video players, 3D, Maps)

Swing/AWT Heavyweight components (JFXPanel, JCEF, etc.)
всегда рендерятся поверх Compose content!

Workaround: Не используйте Box/overlay над heavyweight.
             Используйте отдельные окна для таких компонентов.
```

---

## Rendering и Performance

### Skia Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPOSE DESKTOP RENDERING                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Compose UI Tree → Skia Commands → GPU Backend → Screen           │
│                                                                     │
│   GPU Backends:                                                     │
│   • macOS:   Metal (default), OpenGL                                │
│   • Windows: Direct3D, OpenGL                                       │
│   • Linux:   OpenGL                                                 │
│                                                                     │
│   Fallback:  Software renderer (CPU)                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Выбор рендерера

```kotlin
// Через environment variable
// SKIKO_RENDER_API=SOFTWARE|OPENGL|METAL

// Или через JVM property
compose.desktop {
    application {
        jvmArgs += listOf(
            "-Dskiko.renderApi=OPENGL"
        )
    }
}
```

### Performance Tips

```kotlin
// ✅ Использовать LazyColumn/LazyRow для списков
LazyColumn {
    items(items, key = { it.id }) { item ->
        ItemRow(item)
    }
}

// ✅ Minimize overdraw
// Избегать лишних прозрачных слоёв
Box(modifier = Modifier.background(Color.White)) {  // Opaque
    Content()
}

// ✅ Remember expensive computations
val processed = remember(data) {
    expensiveProcess(data)
}

// ✅ Use derivedStateOf для computed values
val showButton by remember {
    derivedStateOf { items.size > threshold }
}
```

### Software Renderer Issues

```
⚠️ SOFTWARE RENDERER PERFORMANCE

На машинах без GPU (или с disabled GPU):
• FPS ~10-20 при SOFTWARE_FAST
• Drops на высоких разрешениях (1920x1080)

Решение: Проверять наличие GPU и предупреждать пользователей
```

---

## Native Packaging

### Форматы

| OS | Форматы | Команды |
|----|---------|---------|
| macOS | .dmg, .pkg | `packageDmg`, `packagePkg` |
| Windows | .exe, .msi | `packageExe`, `packageMsi` |
| Linux | .deb, .rpm | `packageDeb`, `packageRpm` |

### Полная конфигурация

```kotlin
compose.desktop {
    application {
        mainClass = "MainKt"

        nativeDistributions {
            targetFormats(
                TargetFormat.Dmg, TargetFormat.Pkg,  // macOS
                TargetFormat.Msi, TargetFormat.Exe,  // Windows
                TargetFormat.Deb, TargetFormat.Rpm   // Linux
            )

            // Metadata
            packageName = "MyApp"
            packageVersion = "1.0.0"
            description = "My Desktop Application"
            copyright = "© 2026 My Company"
            vendor = "My Company"
            licenseFile.set(project.file("LICENSE.txt"))

            // JDK modules (jlink)
            modules("java.sql", "java.net.http")
            // Или все модули (больший размер)
            // includeAllModules = true

            // macOS specific
            macOS {
                iconFile.set(project.file("icons/icon.icns"))
                bundleID = "com.mycompany.myapp"
                minimumSystemVersion = "10.15"

                // Code signing
                signing {
                    sign.set(true)
                    identity.set("Developer ID Application: My Name (TEAMID)")
                }

                // Notarization
                notarization {
                    appleID.set("email@example.com")
                    password.set(providers.environmentVariable("NOTARIZATION_PASSWORD"))
                    teamID.set("TEAMID")
                }
            }

            // Windows specific
            windows {
                iconFile.set(project.file("icons/icon.ico"))
                console = false
                dirChooser = true
                perUserInstall = true
                menuGroup = "My Company"
                upgradeUuid = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            }

            // Linux specific
            linux {
                iconFile.set(project.file("icons/icon.png"))
                debMaintainer = "maintainer@mycompany.com"
                menuGroup = "Development"
                appCategory = "Development"
            }
        }
    }
}
```

### Cross-Compilation

```
⚠️ CROSS-COMPILATION НЕ ПОДДЕРЖИВАЕТСЯ

Нужно собирать на каждой платформе отдельно:
• .dmg → только на macOS
• .exe/.msi → только на Windows
• .deb/.rpm → только на Linux

Решение: GitHub Actions с matrix build на разных runners
```

### Альтернатива: Conveyor

[Conveyor](https://www.hydraulic.dev/) предоставляет:
- Cross-building с одной машины
- Auto-updates для пользователей
- Code signing automation
- Требует лицензию для closed-source проектов

---

## Production Gotchas

### Известные ограничения

| Проблема | Описание | Workaround |
|----------|----------|------------|
| **Tray на Windows** | Выглядит устаревшим (Windows 95 style) | ComposeNativeTray library |
| **Rich Notifications** | Нет actions, custom icons, sounds | Platform-specific native code |
| **Native APIs** | Сложный доступ через JNI/JNA | Ограниченное использование |
| **Auto-updates** | Не встроено | Conveyor или custom solution |
| **Startup on boot** | Нет API | Platform-specific registration |

### Tray Improvements с ComposeNativeTray

```kotlin
// Сторонняя библиотека с лучшей поддержкой
// https://github.com/kdroidFilter/ComposeNativeTray

// Преимущества:
// • HDPI поддержка на Windows/Linux
// • GTK на Linux (не AWT)
// • Checkable items, dividers, submenus
// • Single instance management
```

### ProGuard Issues

```kotlin
// ⚠️ Optimization может ломать приложение
compose.desktop {
    application {
        buildTypes.release.proguard {
            // Рекомендация: отключить optimization
            optimize.set(false)  // Многие devs отключают
            obfuscate.set(true)  // Можно оставить
        }
    }
}
```

### KTOR Serialization

```
⚠️ KTOR + PROGUARD ISSUE

С включённой ProGuard optimization:
• kotlinx.serialization работает
• ktor .body<T>() вызовы НЕ работают

Решение: optimize.set(false) или ProGuard rules для Ktor
```

---

## File Dialogs

### AWT FileDialog (Native)

```kotlin
import java.awt.FileDialog
import java.awt.Frame

fun openFileDialog(): String? {
    val dialog = FileDialog(Frame(), "Choose a file", FileDialog.LOAD)
    dialog.isVisible = true
    return if (dialog.file != null) {
        dialog.directory + dialog.file
    } else null
}
```

### JFileChooser (Swing)

```kotlin
import javax.swing.JFileChooser

fun openFileChooser(): String? {
    val chooser = JFileChooser()
    val result = chooser.showOpenDialog(null)
    return if (result == JFileChooser.APPROVE_OPTION) {
        chooser.selectedFile.absolutePath
    } else null
}
```

### Multiplatform File Picker Library

```kotlin
// https://github.com/Wavesonics/compose-multiplatform-file-picker

// Использование в Compose
var showFilePicker by remember { mutableStateOf(false) }

FilePicker(show = showFilePicker, fileExtensions = listOf("txt", "md")) { file ->
    showFilePicker = false
    file?.let { processFile(it) }
}
```

---

## Keyboard Navigation

### Tab Navigation

```kotlin
// По умолчанию работает для focusable компонентов:
// - TextField, OutlinedTextField
// - Button, IconButton
// - Любой с Modifier.clickable

// Tab → следующий элемент
// Shift+Tab → предыдущий элемент
```

### Custom Keyboard Handling

```kotlin
@Composable
fun KeyboardHandling() {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .onKeyEvent { event ->
                when {
                    event.isCtrlPressed && event.key == Key.S -> {
                        save()
                        true
                    }
                    event.key == Key.Escape -> {
                        cancel()
                        true
                    }
                    else -> false
                }
            }
    ) {
        // Content
    }
}
```

---

## CI/CD

### GitHub Actions Matrix Build

```yaml
name: Release Desktop App

on:
  push:
    tags: ['v*']

jobs:
  build:
    strategy:
      matrix:
        os: [macos-latest, windows-latest, ubuntu-latest]
        include:
          - os: macos-latest
            task: packageDmg
            artifact: dmg
          - os: windows-latest
            task: packageMsi
            artifact: msi
          - os: ubuntu-latest
            task: packageDeb
            artifact: deb

    runs-on: ${{ matrix.os }}

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build
        run: ./gradlew ${{ matrix.task }}

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: ${{ matrix.os }}-${{ matrix.artifact }}
          path: |
            build/compose/binaries/main/${{ matrix.artifact }}/*
```

---

## Кто использует в production

| Компания/Продукт | Описание | Результат |
|------------------|----------|-----------|
| **JetBrains Toolbox** | 1M+ MAU, IDE manager | -50% size, -RAM, better perf |
| **JetBrains Fleet** | Части UI | Modern editor |
| **Ubidrop** | File sharing | Production desktop app |
| **Internal Tools** | Enterprise dashboards | Cross-platform deployment |

---

## Мифы и заблуждения

### Миф 1: "JVM = медленный startup"

**Заблуждение:** "Desktop apps на JVM запускаются медленно из-за JIT"

**Реальность:**
- jlink минимизирует JDK (только нужные модули)
- Startup ~1-2 секунды для типичного app
- Compose Toolbox (production) стартует быстро
- Native GraalVM compilation возможна для ещё быстрее

---

### Миф 2: "Нужен установленный JDK у пользователей"

**Заблуждение:** "Пользователям нужно устанавливать Java"

**Реальность:**
- jpackage **включает JVM в installer**
- Пользователь видит обычный .dmg / .exe / .deb
- Никакой зависимости от системной Java
- Полностью self-contained приложение

---

### Миф 3: "Swing interop — это legacy костыль"

**Заблуждение:** "Swing устарел, интеграция не нужна"

**Реальность:** Swing interop позволяет:
- Постепенную миграцию с 30+ летней кодовой базы
- Использование mature Swing компонентов (JTree, JTable)
- Embed Compose в existing Java apps
- IntelliJ IDEA использует эту технику

---

### Миф 4: "Cross-compilation невозможна — это критично"

**Заблуждение:** "Нужна Windows машина для .exe — это blocker"

**Реальность:**
- GitHub Actions matrix builds решают проблему:
  - macos-latest → .dmg
  - windows-latest → .msi
  - ubuntu-latest → .deb
- Conveyor позволяет cross-build с одной машины (платно)
- Для большинства проектов CI/CD достаточно

---

### Миф 5: "Compose Desktop не production-ready"

**Заблуждение:** "Это экспериментальная технология"

**Реальность:**
- **JetBrains Toolbox**: 1M+ MAU (ежемесячных активных)
- **JetBrains Fleet**: используют Compose Desktop
- Статус: **Stable** (уже несколько лет)
- JetBrains "dogfooding" — используют в своих продуктах

---

### Миф 6: "Приложения выглядят чужеродно"

**Заблуждение:** "Compose UI не похож на native macOS/Windows"

**Реальность:**
- Material 3 design универсален и современен
- Jewel (JetBrains) — IntelliJ-like theme для Compose
- Можно кастомизировать под любой OS look
- Window decorations нативные (title bar, buttons)

---

## Рекомендуемые источники

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Compose Desktop Landing](https://www.jetbrains.com/lp/compose/) | Official | Главная страница |
| [Native Distributions](https://kotlinlang.org/docs/multiplatform/compose-native-distribution.html) | Official | Packaging guide |
| [Desktop Components](https://kotlinlang.org/docs/multiplatform/compose-desktop-components.html) | Official | Desktop-only APIs |
| [Desktop Template](https://github.com/JetBrains/compose-multiplatform-desktop-template) | GitHub | Стартовый шаблон |

### Case Studies и блоги

| Источник | Тип | Описание |
|----------|-----|----------|
| [Toolbox Case Study](https://blog.jetbrains.com/kotlin/2021/12/compose-multiplatform-toolbox-case-study/) | Official | JetBrains migration story |
| [Compose Desktop in Production](https://composables.com/blog/compose-desktop) | Blog | Real gotchas |
| [Swing Interop](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-desktop-swing-interoperability.html) | Official | AWT/Swing integration |

### Tutorials

| Источник | Тип | Описание |
|----------|-----|----------|
| [Signing & Notarization](https://github.com/JetBrains/compose-multiplatform/tree/master/tutorials/Signing_and_notarization_on_macOS) | Tutorial | macOS code signing |
| [Window API](https://github.com/JetBrains/compose-multiplatform/tree/master/tutorials/Window_API_new) | Tutorial | Window management |
| [Tray & Notifications](https://github.com/JetBrains/compose-multiplatform/tree/master/tutorials/Tray_Notifications_MenuBar_new) | Tutorial | Desktop features |

### Tools

| Инструмент | Описание |
|------------|----------|
| [Conveyor](https://www.hydraulic.dev/) | Cross-platform packaging с auto-updates |
| [ComposeNativeTray](https://github.com/kdroidFilter/ComposeNativeTray) | Better tray support |
| [compose-multiplatform-file-picker](https://github.com/Wavesonics/compose-multiplatform-file-picker) | Native file dialogs |

### CS-фундамент

| Концепция | Зачем изучать | Где применяется |
|-----------|--------------|-----------------|
| [[jvm-internals]] | jlink, jpackage, modules | Native packaging |
| [[graphics-apis-fundamentals]] | OpenGL, Metal, Direct3D | GPU rendering |
| [[gui-frameworks-history]] | Swing, AWT, WinForms | Interop понимание |
| [[native-packaging-distribution]] | Installers, signing | jpackage, Conveyor |
| [[process-memory-management]] | JVM heap, native memory | Performance tuning |
| [[cross-platform-development]] | Shared code strategies | Code organization |

---

## Связь с другими темами

**[[compose-mp-overview]]** — Обзор Compose Multiplatform описывает общий фреймворк, а Desktop является его наиболее зрелой платформой. JetBrains использует Compose MP Desktop в собственных продуктах (Toolbox, Fleet), что обеспечивает production-grade стабильность. Понимание общей архитектуры (Skia rendering, composition, state management) необходимо перед погружением в desktop-специфичные возможности.

**[[kmp-desktop-jvm]]** — Desktop JVM target описывает платформенный фундамент: JVM runtime, jpackage для нативных инсталляторов, системные API и работу с файловой системой. Compose MP Desktop работает поверх этого фундамента, предоставляя декларативный UI с Window API, Swing interop, нативными меню и системным треем. Вместе эти материалы дают полную картину desktop-разработки.

**[[kmp-overview]]** — Обзор Kotlin Multiplatform помогает понять роль Desktop target в мультиплатформенной стратегии. Desktop JVM часто используется как первая платформа для прототипирования shared-кода благодаря быстрому циклу разработки и отладки на JVM. Понимание общей архитектуры KMP помогает организовать desktop-специфичный код в jvmMain source set.

## Источники и дальнейшее чтение

1. **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* — Глубокое понимание Kotlin на JVM необходимо для desktop-разработки: Java interop (Swing), работа с потоками, корутины и extension functions используются повсеместно в desktop-приложениях.
2. **Moskala M. (2021).** *Effective Kotlin.* — Рекомендации по эффективному коду особенно актуальны для desktop: управление ресурсами (use, Closeable), обработка ошибок и оптимизация производительности JVM-приложений с GUI.
3. **Skeen A. (2019).** *Kotlin Programming: The Big Nerd Ranch Guide.* — Практическое руководство по Kotlin с акцентом на JVM. Помогает понять взаимодействие Kotlin с Java-экосистемой, что важно для Swing interop и использования Java-библиотек в desktop-приложениях.

---

## Проверь себя

> [!question]- Почему Compose Desktop считается наиболее зрелой платформой Compose Multiplatform?
> JetBrains использует Compose Desktop в своих собственных продуктах (Toolbox App, Fleet IDE), что обеспечивает production-grade стабильность. Desktop был первой non-Android платформой в Compose MP и имеет самый длительный период стабилизации.

> [!question]- Вам нужно отобразить контекстное меню по правому клику в desktop-приложении. Как это реализовать в Compose MP?
> Использовать ContextMenuArea или ContextMenuDataProvider composable из десктопного API. Compose Desktop поддерживает нативные контекстные меню через JVM AWT, а также кастомные Compose-based меню с полным контролем над стилизацией.

> [!question]- Почему Swing interop важен для Compose Desktop, несмотря на наличие полноценного Compose API?
> Существует огромная экосистема Java/Swing-компонентов (JFreeChart, текстовые редакторы, терминалы). Swing interop позволяет постепенно мигрировать существующие Swing-приложения на Compose и переиспользовать зрелые Swing-виджеты.

---

## Ключевые карточки

Что такое Window API в Compose Desktop?
?
API для управления окнами приложения: создание, размер, позиция, иконка, состояние (minimized/maximized/fullscreen). Каждое Window -- точка входа в Compose-иерархию на Desktop.

Как системный трей работает в Compose Desktop?
?
Через Tray composable, который добавляет иконку в системный трей (notification area). Поддерживает контекстное меню по клику, tooltip и custom actions. Работает на Windows, macOS и Linux.

Как packaged desktop-приложение с Compose распространяется?
?
Через compose.desktop.application Gradle-плагин, который использует jpackage для создания нативных инсталляторов: .dmg для macOS, .msi/.exe для Windows, .deb/.rpm для Linux с встроенной JVM.

Чем Compose Desktop отличается от Electron?
?
Compose Desktop рендерит через Skia (нативный GPU), Electron -- через Chromium (веб-движок). Compose Desktop потребляет меньше памяти, запускается быстрее и имеет нативную производительность. Но Electron имеет большую web-экосистему.

Как нативные меню работают в Compose Desktop?
?
Через MenuBar composable для главного меню приложения и ContextMenuArea для контекстных меню. На macOS меню интегрируется в системную строку, на Windows/Linux -- в окно приложения.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[compose-mp-web]] | Compose UI для Web-платформы |
| Углубиться | [[kmp-desktop-jvm]] | Платформенный фундамент: JVM, jpackage, системные API |
| Смежная тема | [[kmp-architecture-patterns]] | Архитектурные паттерны для кросс-платформенных приложений |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Compose Multiplatform 1.8.0+, Kotlin 2.1.21, JDK 17+*
