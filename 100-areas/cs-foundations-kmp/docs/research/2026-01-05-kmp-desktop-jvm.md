# Research Report: KMP Desktop JVM

**Date:** 2026-01-05
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Compose Multiplatform Desktop (Stable) работает на JVM с Skia rendering. Поддерживает Windows, macOS, Linux. Packaging через jpackage создаёт self-contained installers. Hot Reload (Beta) ускоряет разработку UI. Нет cross-compilation — нужно билдить на каждой OS. Desktop-specific features: menus, keyboard shortcuts, window management, system tray. По сравнению с Electron: меньше памяти, лучше производительность, но меньше web ecosystem. JetBrains Runtime (JBR) рекомендуется для совместимости.

## Key Findings

### 1. Platform Status (January 2026)

| Component | Status | Notes |
|-----------|--------|-------|
| Compose Desktop | Stable | Since Compose MP 1.0 |
| JVM Target | Stable | Primary desktop target |
| Hot Reload | Beta | UI changes live |
| Native Packaging | Stable | jpackage-based |

**Supported platforms:**
- Windows (x64, arm64)
- macOS (x64, arm64)
- Linux (x64, arm64)

### 2. Architecture

```
Compose UI → Skia Renderer → JVM → OS Window
                             ↑
                             └── JetBrains Runtime (recommended)
```

**Important:** Desktop apps use JVM, not Kotlin/Native. Adding `linuxX64` or `mingwX64` targets breaks Compose Desktop.

### 3. Native Distribution Packaging

**Gradle commands:**
```bash
# Package for current OS
./gradlew packageDistributionForCurrentOS

# Specific formats
./gradlew packageDmg       # macOS
./gradlew packageMsi       # Windows
./gradlew packageDeb       # Linux Debian
./gradlew packageRpm       # Linux RPM
```

**Output:** `build/compose/binaries/`

**Requirements:**
- JDK 15+ for native packaging
- jlink minimizes package size
- No cross-compilation (build on target OS)

**Limitations:**
- Cannot customize installer UI
- No "Start app after install" option
- No built-in auto-update

### 4. Desktop-Specific Features

| Feature | API | Notes |
|---------|-----|-------|
| System Menu | `MenuBar`, `Menu`, `Item` | macOS integrates with system |
| Keyboard Shortcuts | `Modifier + Key` | Platform-aware |
| Window Management | `Window`, `WindowState` | Size, position, fullscreen |
| System Tray | `Tray` | Icons, menus |
| Notifications | `Notification` | OS notifications |
| File Dialogs | `FileDialog` | Open/Save dialogs |
| Drag & Drop | `onExternalDrag` | File drops |

### 5. Hot Reload (Beta)

Allows seeing UI changes without restarting:
- Edit Compose code
- Changes appear immediately
- Useful for UI development
- Works even when not targeting desktop

### 6. JVM Configuration

**Recommended: JetBrains Runtime (JBR)**
- Fixes compatibility issues
- Better font rendering
- Included in IntelliJ IDEA

**Build configuration:**
```kotlin
compose.desktop {
    application {
        mainClass = "MainKt"
        jvmArgs += listOf("-Xmx2g")

        nativeDistributions {
            targetFormats(
                TargetFormat.Dmg,
                TargetFormat.Msi,
                TargetFormat.Deb
            )
            packageName = "MyApp"
            packageVersion = "1.0.0"
        }
    }
}
```

### 7. Compose Desktop vs Electron

| Aspect | Compose Desktop | Electron |
|--------|-----------------|----------|
| Runtime | JVM | Chromium |
| Language | Kotlin | JavaScript |
| Memory | Lower | 100+ MB baseline |
| Binary size | 50-80 MB | 80-120 MB |
| Startup | Fast | 1-2 seconds |
| Web sharing | Compose for Web | Same codebase |
| Ecosystem | Swing libs | npm packages |
| Rendering | Skia | Chromium |

**Compose Desktop advantages:**
- Share code with Android
- Better memory efficiency
- Native performance
- Swing library ecosystem

**Electron advantages:**
- Larger web ecosystem
- Same web/desktop codebase
- More mature tooling
- Easier web developer onboarding

## Community Sentiment

### Positive
- Hot Reload speeds up development
- Good performance vs Electron
- Shares code with Android
- JetBrains support is strong
- Swing ecosystem available

### Negative / Concerns
- No cross-compilation
- Limited installer customization
- No built-in auto-update
- Smaller ecosystem than web
- Charting libraries limited

### Mixed
- JVM dependency (pro: familiar, con: requires bundling)
- Skia rendering (pro: consistent, con: not native widgets)
- jpackage (pro: works, con: basic features)

## Production Considerations

### Alternative Packaging: Conveyor

Third-party tool for better packaging:
- Custom installers
- Auto-updates
- Code signing
- macOS notarization

### CI/CD for Multiple Platforms

```yaml
# GitHub Actions example
jobs:
  build:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'
      - run: ./gradlew packageDistributionForCurrentOS
```

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Native Distributions](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-native-distribution.html) | Official | ★★★★★ | Packaging guide |
| 2 | [Desktop-only API](https://kotlinlang.org/docs/multiplatform/compose-desktop-components.html) | Official | ★★★★★ | Desktop features |
| 3 | [Desktop Template](https://github.com/JetBrains/compose-multiplatform-desktop-template) | Official | ★★★★☆ | Starter template |
| 4 | [Compose Desktop Production](https://composables.com/blog/compose-desktop) | Community | ★★★★☆ | Real experience |
| 5 | [KMP Roadmap Aug 2025](https://blog.jetbrains.com/kotlin/2025/08/kmp-roadmap-aug-2025/) | Official | ★★★★☆ | Future plans |

## Research Methodology

- **Queries used:** 3 search queries
- **Sources found:** 20+ total
- **Sources used:** 15 (after quality filter)
- **Focus areas:** Packaging, performance, features, comparison


---

*Проверено: 2026-01-09*
