---
title: "Research Report: Compose Multiplatform Desktop"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: Compose Multiplatform Desktop

**Date:** 2026-01-03
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

Compose Desktop (Stable) создаёт нативные приложения для macOS/Windows/Linux с GPU-accelerated rendering через Skia. JetBrains Toolbox (1M+ MAU) — главный пример в production: мигрировали с Electron, получили -50% installer size и значительное снижение RAM. Swing/AWT interop позволяет постепенную миграцию существующих Java приложений. Основные ограничения: нет cross-compilation, dated tray на Windows, проблемы с ProGuard optimization.

## Key Findings

1. **JetBrains Toolbox Migration**
   - From C++ + Chromium (React) to 100% Kotlin + Compose
   - Results: -50% installer size, significantly reduced RAM (was 200MB idle)
   - Single language enabled end-to-end feature development
   - No more JSON serialization between layers

2. **Rendering Architecture**
   - Skia library for all platforms
   - GPU backends: Metal (macOS), OpenGL (all), Direct3D (Windows)
   - Software fallback available but slow (10-20 FPS on high res)
   - Environment variable SKIKO_RENDER_API to override

3. **Desktop-Specific APIs**
   - Window management: declarative with @Composable Window
   - MenuBar with keyboard shortcuts and mnemonics
   - System Tray with notifications (3 types: Info, Warning, Error)
   - Context menus, scrollbars, tooltips

4. **Swing/AWT Interoperability**
   - ComposePanel: embed Compose in Swing apps
   - SwingPanel: embed Swing in Compose
   - Limitation: heavyweight components always render on top

5. **Packaging**
   - jpackage for native installers
   - jlink for minimizing JDK modules
   - No cross-compilation (must build on target OS)
   - Conveyor as alternative with cross-building support

6. **Production Gotchas**
   - Tray looks dated on Windows (Windows 95 style)
   - No rich notifications (actions, custom icons, sounds)
   - ProGuard optimization breaks Ktor serialization
   - No built-in auto-updates (use Conveyor)
   - No startup-on-boot API

## Community Sentiment

### Positive
- Single language (Kotlin) end-to-end development
- Excellent Swing interop for gradual migration
- Same UI paradigm as Android Compose
- JetBrains using it in production validates maturity

### Negative
- System integration features are limited
- Tray and notifications need improvement
- Must build on each platform separately
- ProGuard issues require disabling optimization
- Limited native API access documentation

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Native distributions docs](https://kotlinlang.org/docs/multiplatform/compose-native-distribution.html) | Official | 0.95 | Packaging configuration |
| 2 | [Desktop components docs](https://kotlinlang.org/docs/multiplatform/compose-desktop-components.html) | Official | 0.95 | Desktop-only APIs |
| 3 | [Toolbox Case Study](https://blog.jetbrains.com/kotlin/2021/12/compose-multiplatform-toolbox-case-study/) | Official | 0.95 | Production migration story |
| 4 | [Compose Desktop in Production](https://composables.com/blog/compose-desktop) | Blog | 0.85 | Real gotchas |
| 5 | [Swing Interop docs](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-desktop-swing-interoperability.html) | Official | 0.95 | Integration guide |
| 6 | [ComposeNativeTray](https://github.com/kdroidFilter/ComposeNativeTray) | GitHub | 0.80 | Better tray solution |
| 7 | [Skia in Compose](https://medium.com/@sandeepkella23/skia-in-jetpack-compose-the-core-graphics-engine-77e4f34b6695) | Blog | 0.75 | Rendering details |
| 8 | [Kotlin Discussions](https://discuss.kotlinlang.org/) | Forum | 0.70 | Community issues |

## Recommendations

1. **For new projects**: Use Compose Desktop for cross-platform desktop apps, especially if sharing code with mobile
2. **For existing Swing apps**: Gradually migrate using ComposePanel
3. **For packaging**: Consider Conveyor if auto-updates needed
4. **For tray apps**: Use ComposeNativeTray library instead of built-in
5. **For ProGuard**: Disable optimization, keep obfuscation
