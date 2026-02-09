# Research Report: Compose Multiplatform

**Date:** 2026-01-05
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Compose Multiplatform for iOS достиг Stable статуса в мае 2025 (версия 1.8.0). Использует Skiko/Skia для canvas-based rendering. Performance сравним со SwiftUI: startup time как у native, scrolling on par even on high-refresh devices. Добавляет ~9 MB к размеру iOS app. Поддержка accessibility (VoiceOver, AssistiveTouch, Full Keyboard Access) полная. Interop с SwiftUI/UIKit через UIHostingController и ComposeUIViewController. Navigation: Voyager (простой), Decompose (UI-agnostic), Navigation Compose (official). Compose Resources API стабилен. Production apps: Wrike, Instabee, Music Work, Feres, Physics Wallah.

## Key Findings

### 1. Stable Status (May 2025)

| Version | Date | Platform | Status |
|---------|------|----------|--------|
| CMP 1.8.0 | May 2025 | iOS | Stable |
| CMP 1.9.0 | Sep 2025 | Web | Beta |
| CMP 1.10.0 | Dec 2025 | All | Latest |

Features in stable release:
- Feature parity with Jetpack Compose
- Type-safe navigation with deep linking
- Flexible resource management
- First-class accessibility (VoiceOver, AssistiveTouch)
- Native iOS scrolling physics
- Drag-and-drop integration

### 2. Rendering Architecture (Skiko/Skia)

**Stack:**
```
Compose UI → Skiko → Skia → Metal/OpenGL → Screen
```

- **Skiko** = Skia for Kotlin (bindings)
- **Skia** = Google's 2D graphics library (Chrome, Flutter)
- Hardware-accelerated via Metal (iOS), Vulkan/OpenGL (Android)
- Canvas abstraction maps to Skia drawing API
- Same rendering on all platforms → consistent look

**Canvas rendering flow:**
- `onRender(canvas, width, height, nanoTime)` called per frame
- `needRedraw()` requests frame at next vsync
- Draw commands batched and submitted to Skia

### 3. Performance vs SwiftUI

| Metric | Compose MP | SwiftUI |
|--------|-----------|---------|
| Startup time | Comparable to native | Native |
| Scrolling | On par (high-refresh OK) | Native |
| App size overhead | +9 MB | 0 (system) |
| Memory | Similar | Similar |

**96% of teams report no major performance concerns** (JetBrains survey).

"Punch hole" interop allows native components to "shine through" Compose surface.

### 4. Accessibility

**Supported features:**
- VoiceOver (full support)
- AssistiveTouch (mouse/trackpad)
- Full Keyboard Access
- Voice Control
- RTL language support (1.8.2+)
- Scrolling state announcements

**Technical approach:**
- Compose semantic tree syncs with iOS accessibility tree
- Lazy loading after first accessibility request
- `testTag` maps to `accessibilityIdentifier` for XCTest

### 5. Navigation Libraries

| Library | Coupling | State | Official |
|---------|----------|-------|----------|
| Navigation Compose | Compose | ViewModel | Yes (JetBrains/Google) |
| Voyager | Compose | ScreenModel | No |
| Decompose | UI-agnostic | Components | No |

**Navigation Compose** (recommended for new projects):
- `org.jetbrains.androidx.navigation:navigation-compose:2.9.1`
- Type-safe argument passing
- Deep linking support
- Well documented

**Voyager** (simpler):
- Easy to start
- ScreenModel for state
- Supports Wasm since 1.1.0-alpha03

**Decompose** (most flexible):
- Separates navigation from UI
- Works with native UI too
- Higher learning curve

### 6. Resources API

**Setup:**
```kotlin
implementation(compose.components.resources)
```

**Structure:**
```
src/commonMain/composeResources/
├── drawable/
├── font/
├── string/
└── raw/
```

**Features:**
- Stable API (since 1.6.0)
- Qualifier support (locale, density, theme)
- Multi-module support (Kotlin 2.0+)
- Synchronous reading (except raw/web)

### 7. SwiftUI/UIKit Interop

**Compose → iOS:**
```kotlin
fun AppViewController() = ComposeUIViewController {
    App()
}
```

**SwiftUI in Compose:**
```kotlin
@Composable
fun UIKitViewController(factory: () -> UIViewController)
```

Uses `UIHostingController` to wrap SwiftUI views.

**UIKit common denominator** — can host UIKit, SwiftUI, or Compose screens.

### 8. Production Apps

| Company | Usage | Code Sharing |
|---------|-------|--------------|
| Wrike | Calendars, Boards, Dashboards | Full UI |
| Music Work | 100% UI shared | Full UI |
| Feres (1M+ downloads) | 90%+ UI shared | Full UI |
| Physics Wallah (10M+) | 20% of app | Partial |
| BiliBili | IM feature | Feature |
| Instabee | Android → iOS migration | Full |

## Community Sentiment

### Positive
- iOS Stable finally here
- Performance matches SwiftUI
- Accessibility support comprehensive
- Interop with native straightforward
- Resources API well designed
- JetBrains actively improving

### Negative / Concerns
- +9 MB app size (minor)
- Canvas-based = not native widgets
- Some edge cases with interop
- Web still Beta
- Tooling could be better (previews)

### Mixed
- Navigation library choice unclear
- Learning curve for iOS devs
- Debugging across platforms

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [CMP 1.8.0 Release](https://blog.jetbrains.com/kotlin/2025/05/compose-multiplatform-1-8-0-released-compose-multiplatform-for-ios-is-stable-and-production-ready/) | Official | ★★★★★ | iOS Stable announcement |
| 2 | [Skiko GitHub](https://github.com/JetBrains/skiko) | Official | ★★★★★ | Rendering internals |
| 3 | [iOS Accessibility Docs](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-ios-accessibility.html) | Official | ★★★★★ | Accessibility guide |
| 4 | [SwiftUI Integration](https://kotlinlang.org/docs/multiplatform/compose-swiftui-integration.html) | Official | ★★★★★ | Interop guide |
| 5 | [Navigation Docs](https://kotlinlang.org/docs/multiplatform/compose-navigation.html) | Official | ★★★★★ | Navigation options |
| 6 | [Resources Docs](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-multiplatform-resources.html) | Official | ★★★★★ | Resources API |
| 7 | [Use Cases](https://www.jetbrains.com/help/kotlin-multiplatform-dev/use-cases-examples.html) | Official | ★★★★☆ | Production examples |
| 8 | [KMPShip iOS Stable](https://www.kmpship.app/blog/compose-multiplatform-ios-stable-2025) | Community | ★★★★☆ | Overview |
| 9 | [Touchlab Interop](https://touchlab.co/jetpack-compose-ios-interop) | Expert | ★★★★☆ | Native interop |
| 10 | [Voyager Docs](https://voyager.adriel.cafe/) | Library | ★★★★☆ | Navigation library |

## Research Methodology

- **Queries used:** 7 search queries
- **Sources found:** 30+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** iOS Stable, rendering, performance, navigation, accessibility, interop

---

*Проверено: 2026-01-09*
