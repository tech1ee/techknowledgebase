# Research Report: KMP Desktop/JVM

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

Compose Desktop (Stable) позволяет создавать нативные приложения для macOS, Windows, Linux. Рендеринг через Skia с hardware acceleration. Desktop-specific APIs включают Window management, MenuBar, Tray, Notifications, Keyboard Shortcuts. Packaging через jpackage (JDK 17+): .dmg/.pkg (macOS), .exe/.msi (Windows), .deb/.rpm (Linux). jlink минимизирует размер bundling только нужных JDK modules. Поддерживается code signing и notarization для macOS.

## Key Findings

1. **Platform Support**
   - macOS (x64, arm64/M1/M2/M3)
   - Windows (x64, arm64)
   - Linux (x64, arm64)
   - All use Skia for hardware-accelerated rendering

2. **Desktop-only APIs**
   - Window composable with WindowState
   - MenuBar with Items, Separators, CheckboxItems
   - Tray icons with menus
   - System notifications (Info, Warning, Error)
   - Keyboard shortcuts (KeyShortcut)
   - Context menus, Scrollbars, Tooltips

3. **Native Packaging**
   - jpackage for self-contained installers
   - jlink to minimize JDK modules
   - ProGuard for release builds
   - Cross-compilation not supported (build on target OS)

4. **Code Signing**
   - macOS: Developer ID + Notarization required
   - Windows: Optional but recommended
   - Linux: Package signing available

5. **Production Usage**
   - JetBrains: Toolbox App, Fleet components
   - Companies hiring Compose Desktop devs: Slack, Spotify
   - Internal enterprise tools and dashboards

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Compose Desktop](https://www.jetbrains.com/lp/compose/) | Official | 0.95 | Overview |
| 2 | [Native Distributions](https://kotlinlang.org/docs/multiplatform/compose-native-distribution.html) | Official | 0.95 | Packaging |
| 3 | [Desktop Components](https://kotlinlang.org/docs/multiplatform/compose-desktop-components.html) | Official | 0.95 | APIs |
| 4 | [Desktop Template](https://github.com/JetBrains/compose-multiplatform-desktop-template) | GitHub | 0.90 | Starter |
| 5 | [Netguru KMP Apps](https://www.netguru.com/blog/top-apps-built-with-kotlin-multiplatform) | Blog | 0.80 | Production examples |
