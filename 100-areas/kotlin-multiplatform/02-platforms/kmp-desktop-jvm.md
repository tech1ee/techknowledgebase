---
title: "KMP Desktop/JVM: Compose для десктопных приложений"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - desktop
  - topic/android
  - windows
  - macos
  - linux
  - packaging
  - type/concept
  - level/intermediate
related:
  - "[[kmp-overview]]"
  - "[[kmp-android-integration]]"
  - "[[compose-mp-desktop]]"
prerequisites:
  - "[[kmp-getting-started]]"
  - "[[kmp-project-structure]]"
cs-foundations:
  - "[[bytecode-virtual-machines]]"
  - "[[compilation-pipeline]]"
  - "[[garbage-collection-explained]]"
  - "[[memory-model-fundamentals]]"
status: published
---

# KMP Desktop/JVM

> **TL;DR:** Compose Desktop (Stable) позволяет создавать нативные приложения для macOS, Windows, Linux из одного Kotlin кода. Рендеринг через Skia, hardware-accelerated. Desktop-specific APIs: Window management, MenuBar, Tray, Notifications, Shortcuts. Packaging через jpackage: .dmg/.pkg (macOS), .exe/.msi (Windows), .deb/.rpm (Linux). jlink минимизирует размер, bundling JDK modules. Code signing и notarization для macOS.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **JVM & Bytecode** | Почему Desktop использует JVM | [[bytecode-virtual-machines]] |
| **Compilation Pipeline** | Как работает Kotlin → JVM bytecode | [[compilation-pipeline]] |
| **GC (Garbage Collection)** | Memory management в JVM | [[garbage-collection-explained]] |
| Jetpack Compose | UI фреймворк | [[compose-basics]] |
| JVM/Kotlin | Базовый Kotlin | [[kotlin-overview]] |
| Gradle | Сборка проекта | [[gradle-kotlin-dsl]] |
| KMP Project Structure | Основы KMP | [[kmp-project-structure]] |

> **Рекомендация:** Для понимания ПОЧЕМУ Desktop использует JVM (а не Kotlin/Native), прочитай CS-фундамент о bytecode и virtual machines.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Compose Desktop** | UI фреймворк для Desktop | Android Compose, но для компьютеров |
| **jpackage** | Java инструмент для создания установщиков | Завод по упаковке продукции |
| **jlink** | Инструмент для минимизации JDK | Фильтр, оставляющий только нужное |
| **Notarization** | Проверка Apple для macOS apps | Паспортный контроль для приложений |
| **MenuBar** | Системное меню приложения | Навигационная панель ресторана |
| **Tray** | Иконка в системном трее | Звоночек уведомлений |

---

## Почему Desktop использует JVM, а не Kotlin/Native

### Парадокс: Desktop — JVM target

В Kotlin Multiplatform есть Kotlin/Native (iOS, Linux, Windows), но Compose Desktop использует **JVM**. Почему?

### Причина 1: Ecosystem и библиотеки

JVM имеет 25+ лет экосистемы:
```
JVM Ecosystem для Desktop:
├── Swing libraries (charts, tables, editors)
├── JavaFX components
├── PDF generation (iText, Apache PDFBox)
├── Database drivers (JDBC)
├── Network libraries (Netty, OkHttp)
└── Enterprise integration
```

Kotlin/Native ecosystem значительно меньше.

### Причина 2: Performance на практике

JVM с JIT-компиляцией достигает near-native performance после "warm-up":

```
Cold start:    Native > JVM (на ~200-500ms)
Warm runtime:  JVM ≈ Native (иногда JVM быстрее из-за runtime optimization)
Long-running:  JVM часто быстрее (adaptive optimization)
```

Desktop приложения — long-running, что play into JVM's strengths.

### Причина 3: Cross-platform consistency

JVM обеспечивает идентичное поведение на Windows/macOS/Linux:
- Одинаковый bytecode везде
- Одинаковые библиотеки
- Одинаковое поведение GC

Kotlin/Native для каждой платформы — разные бинарники с потенциально разным поведением.

### Сравнение Desktop подходов

| Подход | Runtime | Code Sharing | Native APIs |
|--------|---------|--------------|-------------|
| Compose Desktop | JVM | Android, Desktop | Through JVM |
| Kotlin/Native Desktop | Native | iOS | Direct FFI |
| Electron | Chromium | Web, Desktop | Node.js bindings |
| Flutter Desktop | Dart VM | iOS, Android, Desktop | Platform channels |

### jpackage: Решение проблемы JVM

Главный минус JVM — требование установленной Java. **jpackage** решает это:

```
jpackage bundles:
├── Your app code (JAR)
├── Minimal JDK modules (jlink)
├── Native launcher
└── Platform-specific installer
```

Результат: **self-contained installer**, пользователь не знает про JVM.

---

## Статус Desktop в KMP (январь 2026)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMPOSE DESKTOP STATUS                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Component              Status        Requirements                 │
│   ─────────────────────────────────────────────────────────         │
│   Compose Desktop        ✅ Stable     JDK 17+ for packaging        │
│   Skia Rendering         ✅ Stable     Hardware accelerated         │
│   Native Packaging       ✅ Stable     jpackage (JDK 17+)           │
│   Code Signing           ✅ Stable     Platform certificates        │
│   ProGuard Minification  ✅ Stable     Release builds               │
│                                                                     │
│   Supported Platforms:                                              │
│   • macOS (x64, arm64/M1/M2/M3)                                     │
│   • Windows (x64, arm64)                                            │
│   • Linux (x64, arm64)                                              │
│                                                                     │
│   Package Formats:                                                  │
│   • macOS: .dmg, .pkg                                               │
│   • Windows: .exe, .msi                                             │
│   • Linux: .deb, .rpm                                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Быстрый старт

### Способ 1: KMP Wizard

1. Открыть [kmp.jetbrains.com](https://kmp.jetbrains.com/)
2. Выбрать "Desktop" target
3. Скачать и открыть в IDE

### Способ 2: Desktop-only Template

```bash
git clone https://github.com/JetBrains/compose-multiplatform-desktop-template
cd compose-multiplatform-desktop-template
./gradlew run
```

### Базовая структура

**settings.gradle.kts:**

```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

rootProject.name = "DesktopApp"
include(":composeApp")
```

**composeApp/build.gradle.kts:**

```kotlin
import org.jetbrains.compose.desktop.application.dsl.TargetFormat

plugins {
    kotlin("jvm")
    id("org.jetbrains.compose")
    id("org.jetbrains.kotlin.plugin.compose")
}

dependencies {
    implementation(compose.desktop.currentOs)
    implementation(compose.material3)
    implementation(compose.components.resources)
}

compose.desktop {
    application {
        mainClass = "MainKt"

        nativeDistributions {
            targetFormats(TargetFormat.Dmg, TargetFormat.Msi, TargetFormat.Deb)

            packageName = "MyDesktopApp"
            packageVersion = "1.0.0"
        }
    }
}
```

**src/main/kotlin/Main.kt:**

```kotlin
import androidx.compose.desktop.ui.tooling.preview.Preview
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "My Desktop App"
    ) {
        App()
    }
}

@Composable
@Preview
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

### Запуск

```bash
# Development run
./gradlew run

# Run packaged distributable
./gradlew runDistributable

# Create installer
./gradlew packageDmg          # macOS
./gradlew packageMsi          # Windows
./gradlew packageDeb          # Linux
```

---

## Desktop-only APIs

### Window Management

```kotlin
import androidx.compose.ui.window.*
import androidx.compose.ui.unit.DpSize
import androidx.compose.ui.unit.dp

fun main() = application {
    val windowState = rememberWindowState(
        size = DpSize(800.dp, 600.dp),
        position = WindowPosition(100.dp, 100.dp)
    )

    Window(
        onCloseRequest = ::exitApplication,
        state = windowState,
        title = "My App",
        resizable = true,
        undecorated = false,  // Без рамки окна
        transparent = false,  // Прозрачное окно
        alwaysOnTop = false
    ) {
        // Window content
        App()
    }
}
```

### Несколько окон

```kotlin
fun main() = application {
    var showSecondWindow by remember { mutableStateOf(false) }

    Window(onCloseRequest = ::exitApplication, title = "Main Window") {
        Button(onClick = { showSecondWindow = true }) {
            Text("Open Second Window")
        }
    }

    if (showSecondWindow) {
        Window(
            onCloseRequest = { showSecondWindow = false },
            title = "Second Window"
        ) {
            Text("This is the second window")
        }
    }
}
```

### MenuBar

```kotlin
import androidx.compose.ui.input.key.*
import androidx.compose.ui.window.*

fun main() = application {
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
                Item("Cut", onClick = { }, shortcut = KeyShortcut(Key.X, ctrl = true))
                Item("Copy", onClick = { }, shortcut = KeyShortcut(Key.C, ctrl = true))
                Item("Paste", onClick = { }, shortcut = KeyShortcut(Key.V, ctrl = true))
            }

            Menu("View") {
                CheckboxItem(
                    text = "Show Toolbar",
                    checked = true,
                    onCheckedChange = { /* Handle */ }
                )
            }
        }

        // Window content
        App()
    }
}
```

### System Tray и Notifications

```kotlin
import androidx.compose.ui.window.*
import androidx.compose.ui.graphics.painter.BitmapPainter
import androidx.compose.ui.res.loadImageBitmap
import java.io.File

fun main() = application {
    val trayState = rememberTrayState()
    val notification = rememberNotification(
        title = "Notification Title",
        message = "This is the notification message"
    )

    // Load tray icon
    val trayIcon = BitmapPainter(
        loadImageBitmap(File("icon.png").inputStream())
    )

    Tray(
        state = trayState,
        icon = trayIcon,
        tooltip = "My App",
        menu = {
            Item("Show Notification") {
                trayState.sendNotification(notification)
            }
            Separator()
            Item("Exit") {
                exitApplication()
            }
        }
    )

    Window(onCloseRequest = ::exitApplication) {
        // Window content
    }
}
```

### Notification Types

```kotlin
// Три типа уведомлений
val infoNotification = Notification(
    title = "Info",
    message = "Information message",
    type = Notification.Type.Info  // notify
)

val warnNotification = Notification(
    title = "Warning",
    message = "Warning message",
    type = Notification.Type.Warning  // warn
)

val errorNotification = Notification(
    title = "Error",
    message = "Error message",
    type = Notification.Type.Error  // error
)
```

### Keyboard Shortcuts

```kotlin
import androidx.compose.ui.input.key.*

@Composable
fun App() {
    var text by remember { mutableStateOf("") }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .onKeyEvent { event ->
                when {
                    event.isCtrlPressed && event.key == Key.S -> {
                        // Ctrl+S: Save
                        saveDocument()
                        true
                    }
                    event.key == Key.Escape -> {
                        // Escape: Cancel
                        cancelOperation()
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

### File Dialogs

```kotlin
import androidx.compose.ui.window.AwtWindow
import java.awt.FileDialog
import java.awt.Frame

@Composable
fun FileDialogExample(
    onFileSelected: (String?) -> Unit
) {
    AwtWindow(
        create = {
            object : FileDialog(Frame(), "Choose a file", LOAD) {
                override fun setVisible(b: Boolean) {
                    super.setVisible(b)
                    if (b) {
                        onFileSelected(directory + file)
                    }
                }
            }
        },
        dispose = FileDialog::dispose
    )
}

// Альтернатива: использовать JFileChooser
import javax.swing.JFileChooser

fun openFileChooser(): String? {
    val chooser = JFileChooser()
    val result = chooser.showOpenDialog(null)
    return if (result == JFileChooser.APPROVE_OPTION) {
        chooser.selectedFile.absolutePath
    } else null
}
```

### Context Menus

```kotlin
import androidx.compose.foundation.ContextMenuArea
import androidx.compose.foundation.ContextMenuItem

@Composable
fun ContextMenuExample() {
    ContextMenuArea(
        items = {
            listOf(
                ContextMenuItem("Copy") { /* Handle */ },
                ContextMenuItem("Paste") { /* Handle */ },
                ContextMenuItem("Delete") { /* Handle */ }
            )
        }
    ) {
        Text("Right-click me!")
    }
}
```

### Scrollbars

```kotlin
import androidx.compose.foundation.VerticalScrollbar
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.rememberScrollbarAdapter
import androidx.compose.foundation.verticalScroll

@Composable
fun ScrollableContent() {
    Box(modifier = Modifier.fillMaxSize()) {
        val scrollState = rememberScrollState()

        Column(
            modifier = Modifier
                .fillMaxSize()
                .verticalScroll(scrollState)
        ) {
            repeat(100) { index ->
                Text("Item $index", modifier = Modifier.padding(8.dp))
            }
        }

        VerticalScrollbar(
            modifier = Modifier.align(Alignment.CenterEnd).fillMaxHeight(),
            adapter = rememberScrollbarAdapter(scrollState)
        )
    }
}
```

---

## Native Packaging

### Базовая конфигурация

```kotlin
compose.desktop {
    application {
        mainClass = "MainKt"

        nativeDistributions {
            // Форматы для сборки
            targetFormats(
                TargetFormat.Dmg,  // macOS
                TargetFormat.Pkg,  // macOS installer
                TargetFormat.Msi,  // Windows
                TargetFormat.Exe,  // Windows
                TargetFormat.Deb,  // Linux Debian
                TargetFormat.Rpm   // Linux Red Hat
            )

            // Метаданные
            packageName = "MyApp"
            packageVersion = "1.0.0"
            description = "My Desktop Application"
            copyright = "© 2026 My Company"
            vendor = "My Company"
            licenseFile.set(project.file("LICENSE.txt"))
        }
    }
}
```

### Platform-specific конфигурация

```kotlin
compose.desktop {
    application {
        nativeDistributions {
            // macOS
            macOS {
                iconFile.set(project.file("icons/icon.icns"))
                bundleID = "com.mycompany.myapp"
                minimumSystemVersion = "10.15"

                // Info.plist дополнения
                infoPlist {
                    extraKeysRawXml = """
                        <key>NSHighResolutionCapable</key>
                        <true/>
                    """.trimIndent()
                }
            }

            // Windows
            windows {
                iconFile.set(project.file("icons/icon.ico"))
                console = false           // Показывать консоль
                dirChooser = true         // Выбор директории при установке
                perUserInstall = true     // Установка для текущего пользователя
                menuGroup = "My Company"  // Группа в Start Menu
                upgradeUuid = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  // Для обновлений
            }

            // Linux
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

### Code Signing (macOS)

```kotlin
compose.desktop {
    application {
        nativeDistributions {
            macOS {
                signing {
                    sign.set(true)
                    identity.set("Developer ID Application: Your Name (TEAMID)")

                    // Keychain пароль (для CI)
                    keychain.set("/path/to/keychain")
                    keychainPassword.set(
                        providers.environmentVariable("KEYCHAIN_PASSWORD")
                    )
                }
            }
        }
    }
}
```

### Notarization (macOS)

```kotlin
compose.desktop {
    application {
        nativeDistributions {
            macOS {
                notarization {
                    appleID.set("your-apple-id@example.com")
                    password.set(
                        providers.environmentVariable("NOTARIZATION_PASSWORD")
                    )
                    teamID.set("ABCDEFG123")
                }
            }
        }
    }
}
```

> **Получение App-Specific Password:**
> 1. Перейти на [appleid.apple.com](https://appleid.apple.com/)
> 2. Security → App-Specific Passwords → Generate Password

### JDK Modules (jlink)

```kotlin
compose.desktop {
    application {
        nativeDistributions {
            // Минимальный набор модулей
            modules("java.sql", "java.net.http", "jdk.unsupported")

            // Или включить все (больший размер)
            includeAllModules = true
        }
    }
}
```

**Определить нужные модули:**

```bash
./gradlew suggestModules
# Выведет список рекомендуемых модулей
```

### ProGuard (Release builds)

```kotlin
compose.desktop {
    application {
        buildTypes.release.proguard {
            // Конфигурационный файл
            configurationFiles.from(project.file("compose-desktop.pro"))

            // Опции
            obfuscate.set(true)       // Обфускация имён
            optimize.set(true)        // Оптимизация (default)
            joinOutputJars.set(true)  // Один JAR
        }
    }
}
```

**compose-desktop.pro:**

```proguard
-keep class MainKt { *; }
-keep class ** extends androidx.compose.runtime.Composer { *; }

# Kotlin
-dontwarn kotlin.**
-keep class kotlin.Metadata { *; }

# Compose
-keep class androidx.compose.** { *; }
```

---

## JVM Configuration

### Memory Settings

```kotlin
compose.desktop {
    application {
        jvmArgs += listOf(
            "-Xmx2G",           // Max heap
            "-Xms512M",         // Initial heap
            "-XX:+UseG1GC"      // Garbage collector
        )
    }
}
```

### JDK Version

```kotlin
compose.desktop {
    application {
        // Использовать конкретный JDK
        javaHome = System.getenv("JDK_17")
    }
}
```

### System Properties

```kotlin
compose.desktop {
    application {
        jvmArgs += listOf(
            "-Dapp.name=MyApp",
            "-Dapp.version=1.0.0",
            "-Dfile.encoding=UTF-8"
        )
    }
}
```

---

## Multi-Platform с Desktop

### Структура проекта

```
project/
├── composeApp/
│   ├── build.gradle.kts
│   └── src/
│       ├── commonMain/kotlin/      # Shared UI & logic
│       ├── desktopMain/kotlin/     # Desktop-specific
│       ├── androidMain/kotlin/     # Android-specific
│       └── iosMain/kotlin/         # iOS-specific
└── settings.gradle.kts
```

### build.gradle.kts (multiplatform)

```kotlin
plugins {
    kotlin("multiplatform")
    id("org.jetbrains.compose")
    id("org.jetbrains.kotlin.plugin.compose")
}

kotlin {
    jvm("desktop")

    sourceSets {
        val commonMain by getting {
            dependencies {
                implementation(compose.runtime)
                implementation(compose.foundation)
                implementation(compose.material3)
            }
        }

        val desktopMain by getting {
            dependencies {
                implementation(compose.desktop.currentOs)
            }
        }
    }
}

compose.desktop {
    application {
        mainClass = "MainKt"
        // ...
    }
}
```

### Expect/Actual для Desktop

```kotlin
// commonMain
expect fun getPlatformName(): String
expect fun openBrowser(url: String)

// desktopMain
actual fun getPlatformName(): String = "Desktop (JVM)"

actual fun openBrowser(url: String) {
    if (Desktop.isDesktopSupported()) {
        Desktop.getDesktop().browse(URI(url))
    }
}
```

---

## Gradle Tasks

| Task | Описание |
|------|----------|
| `run` | Запуск в dev режиме |
| `runDistributable` | Запуск packaged image |
| `createDistributable` | Создать бинарник (без installer) |
| `createReleaseDistributable` | Release с ProGuard |
| `packageDmg` | macOS DMG installer |
| `packagePkg` | macOS PKG installer |
| `packageMsi` | Windows MSI installer |
| `packageExe` | Windows EXE installer |
| `packageDeb` | Linux DEB package |
| `packageRpm` | Linux RPM package |
| `packageDistributionForCurrentOS` | Все форматы для текущей OS |
| `suggestModules` | Определить нужные JDK modules |

---

## CI/CD

### GitHub Actions

```yaml
# .github/workflows/release.yml
name: Release Desktop App

on:
  push:
    tags: ['v*']

jobs:
  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build DMG
        run: ./gradlew packageDmg

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: macos-dmg
          path: composeApp/build/compose/binaries/main/dmg/*.dmg

  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build MSI
        run: ./gradlew packageMsi

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: windows-msi
          path: composeApp/build/compose/binaries/main/msi/*.msi

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Build DEB
        run: ./gradlew packageDeb

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: linux-deb
          path: composeApp/build/compose/binaries/main/deb/*.deb
```

---

## Кто использует в production

| Компания/Продукт | Описание |
|------------------|----------|
| **JetBrains IDEs** | Toolbox App, части Fleet |
| **JetBrains Space** | Desktop client |
| **Slack** | Некоторые внутренние tools |
| **Spotify** | Hiring Compose Desktop devs |
| **Enterprise Apps** | Internal tools, dashboards |
| **Kotlin Playground** | Desktop version |

---

## Мифы и заблуждения

### Миф 1: "JVM приложения медленные и тяжёлые"

**Реальность:** JVM с JIT-компиляцией достигает near-native performance. Startup time с GraalVM native-image можно сократить до 50-100ms. jlink убирает неиспользуемые модули — итоговый размер 50-80 MB (сравните с Electron 80-120 MB).

### Миф 2: "Пользователю нужно устанавливать Java"

**Реальность:** jpackage создаёт **self-contained installer** с bundled JDK. Пользователь не знает про JVM. Установка выглядит как любое native приложение.

### Миф 3: "Kotlin/Native лучше для Desktop"

**Реальность:** Compose Desktop использует JVM по дизайну:
- Богатая экосистема (25+ лет библиотек)
- Лучшая производительность для long-running apps
- Code sharing с Android

Kotlin/Native для Desktop возможен, но без Compose (только CLI или custom UI).

### Миф 4: "Desktop — это просто Android код на десктопе"

**Реальность:** Desktop имеет специфичные API:
- Window management (multi-window, positioning)
- MenuBar, system tray, notifications
- File dialogs (AWT/Swing integration)
- Keyboard shortcuts
- Drag & drop

Эти API недоступны на Android.

### Миф 5: "Cross-compilation работает"

**Реальность:** **Нет cross-compilation** для Desktop. Нужно билдить на каждой OS:
- macOS installer → build on macOS
- Windows installer → build on Windows
- Linux package → build on Linux

Используйте CI/CD с matrix builds для всех платформ.

### Миф 6: "Compose Desktop = Electron конкурент"

**Реальность:** Разные ниши:

| Compose Desktop | Electron |
|-----------------|----------|
| Kotlin/JVM | JavaScript/TypeScript |
| Skia rendering | Chromium rendering |
| Android code sharing | Web code sharing |
| Desktop-first | Web-first |

Compose Desktop лучше для Android/Desktop, Electron — для Web/Desktop.

---

## Рекомендуемые источники

### CS-фундамент для глубокого понимания

| Материал | Зачем нужен |
|----------|-------------|
| [[bytecode-virtual-machines]] | Почему Desktop использует JVM |
| [[compilation-pipeline]] | Как работает Kotlin → JVM bytecode |
| [[garbage-collection-explained]] | GC в JVM |
| [[memory-model-fundamentals]] | Threading и concurrency в JVM |

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Compose Desktop](https://www.jetbrains.com/lp/compose/) | Landing | Главная страница |
| [Native Distributions](https://kotlinlang.org/docs/multiplatform/compose-native-distribution.html) | Official | Packaging guide |
| [Desktop Components](https://kotlinlang.org/docs/multiplatform/compose-desktop-components.html) | Official | Desktop-only APIs |
| [Desktop Template](https://github.com/JetBrains/compose-multiplatform-desktop-template) | GitHub | Стартовый шаблон |

### Tutorials

| Источник | Тип | Описание |
|----------|-----|----------|
| [Signing & Notarization](https://github.com/JetBrains/compose-multiplatform/tree/master/tutorials/Signing_and_notarization_on_macOS) | Tutorial | macOS code signing |
| [Window API](https://github.com/JetBrains/compose-multiplatform/tree/master/tutorials/Window_API_new) | Tutorial | Window management |
| [Menu, Tray, Notifications](https://github.com/JetBrains/compose-multiplatform/tree/master/tutorials/Tray_Notifications_MenuBar) | Tutorial | Desktop features |

### Alternative Tools

| Инструмент | Описание |
|------------|----------|
| [Conveyor](https://www.hydraulic.dev/) | Alternative packaging tool |

---

## Связь с другими темами

**[[kmp-overview]]** — Обзор Kotlin Multiplatform описывает место Desktop/JVM target в общей экосистеме KMP. Desktop является одной из наиболее зрелых платформ KMP благодаря прямому запуску на JVM. Понимание общей архитектуры KMP (expect/actual, source sets) необходимо для правильной организации desktop-специфичного кода в jvmMain source set.

**[[kmp-android-integration]]** — Android и Desktop JVM разделяют значительную часть кодовой базы, так как обе платформы работают на JVM. Паттерны интеграции с Jetpack-библиотеками на Android часто имеют прямые аналоги в desktop-разработке. Опыт Android KMP-интеграции ускоряет освоение desktop target, особенно в области ViewModel, навигации и работы с данными.

**[[compose-mp-desktop]]** — Compose Multiplatform для Desktop предоставляет декларативный UI-фреймворк поверх JVM target. Данный материал фокусируется на платформенной интеграции (JVM, jpackage, системные API), тогда как compose-mp-desktop описывает UI-слой: Window API, Swing interop, нативные меню и трей. Вместе они дают полную картину desktop-разработки на KMP.

## Источники и дальнейшее чтение

1. **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* — Фундамент для понимания работы Kotlin на JVM, включая interop с Java, корутины и систему типов. Особенно полезны главы про JVM-специфичные особенности, которые напрямую применяются в desktop-разработке.
2. **Moskala M. (2021).** *Effective Kotlin.* — Лучшие практики написания Kotlin-кода, которые особенно актуальны для desktop-приложений: управление ресурсами, обработка ошибок и оптимизация производительности на JVM.
3. **Skeen A. (2019).** *Kotlin Programming: The Big Nerd Ranch Guide.* — Практическое введение в Kotlin с акцентом на JVM-платформу. Помогает понять взаимодействие Kotlin с Java-экосистемой, что критически важно для desktop-разработки с использованием Swing interop и системных API.

---

*Проверено: 2026-01-09 | Compose Multiplatform 1.8.2, Kotlin 2.1.21, JDK 17+*
