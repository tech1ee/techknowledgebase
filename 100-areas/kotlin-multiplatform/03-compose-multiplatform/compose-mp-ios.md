---
title: "Compose Multiplatform iOS: Production-ready UI для iOS"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, compose, ios, swiftui, uikit, metal, skia]
related:
  - "[[compose-mp-overview]]"
  - "[[kmp-ios-deep-dive]]"
  - "[[00-kmp-overview]]"
cs-foundations:
  - "[[graphics-apis-fundamentals]]"
  - "[[native-code-interop]]"
  - "[[rendering-pipelines]]"
  - "[[accessibility-fundamentals]]"
---

# Compose Multiplatform iOS

> **TL;DR:** Compose Multiplatform for iOS достиг Stable в мае 2025 (1.8.0). Рендеринг через Skia + Metal API. Scrolling on par с SwiftUI (120Hz ProMotion). +9 MB к размеру приложения. 96% команд не сообщают о проблемах с performance. Hot Reload работает на iOS Simulator. Полная interop с UIKit и SwiftUI — можно embed Compose в existing app или embed native views в Compose. VoiceOver и Full Keyboard Access поддерживаются.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Compose Multiplatform Basics | Основы CMP | [[compose-mp-overview]] |
| Swift/SwiftUI Basics | iOS interop | [Swift.org](https://swift.org/) |
| KMP iOS Integration | Настройка iOS target | [[kmp-ios-deep-dive]] |
| Xcode | iOS development tools | [Xcode](https://developer.apple.com/xcode/) |
| **CS: Graphics APIs** | Понять Metal API | [[graphics-apis-fundamentals]] |
| **CS: Native Interop** | FFI между Kotlin и Swift | [[native-code-interop]] |
| **CS: Accessibility** | VoiceOver, assistive tech | [[accessibility-fundamentals]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Metal API** | Apple graphics API | Язык, на котором говорит GPU |
| **ComposeUIViewController** | Мост между Compose и iOS | Адаптер розетки |
| **Punch Hole Interop** | Native views через Compose | Окно в стене |
| **UIViewControllerRepresentable** | SwiftUI wrapper для UIViewController | Переводчик между языками |
| **Hot Reload** | Live UI updates без restart | Правки на лету |

---

## Почему Compose MP на iOS использует Metal, а не UIKit

> **CS-фундамент:** Graphics APIs, Native Code Interop, Rendering Pipelines

### Проблема: как Kotlin-код может рисовать UI на iOS?

iOS предоставляет **два пути** для отображения UI:

```
ПУТЬ 1: NATIVE WIDGETS (React Native approach)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Kotlin Code          Bridge           iOS Native              │
│   ───────────         ─────────         ──────────              │
│                                                                 │
│   Button()    ──►    Obj-C bridge  ──►   UIButton               │
│   TextField() ──►    Swift bridge  ──►   UITextField            │
│   List()      ──►    JS bridge     ──►   UITableView            │
│                                                                 │
│   Проблемы:                                                      │
│   • Bridge overhead (маршалинг данных)                           │
│   • Ограничен возможностями UIKit                                │
│   • Разное поведение на разных iOS версиях                       │
│   • Сложно добиться pixel-perfect consistency                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

ПУТЬ 2: CANVAS RENDERING (Compose MP approach)
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Kotlin Code          Skiko            Metal API               │
│   ───────────         ─────────         ─────────               │
│                                                                 │
│   @Composable  ──►    Skia       ──►    GPU Commands            │
│   Button()            drawRect()  ──►   Metal Shaders           │
│                       drawText()  ──►   Textures                │
│                                                                 │
│   Преимущества:                                                  │
│   • Нет bridge overhead                                         │
│   • Полный контроль над каждым пикселем                          │
│   • Одинаковый рендеринг на всех платформах                      │
│   • Hardware acceleration через Metal                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Metal API: язык общения с GPU

**Metal** — Apple's low-level graphics API (замена OpenGL ES):

```
METAL RENDERING PIPELINE
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   1. COMMAND ENCODING                                           │
│   ─────────────────────                                          │
│   • Skia создаёт draw commands                                   │
│   • Commands кодируются в Metal buffers                         │
│   • Батчинг для минимизации GPU calls                            │
│                                                                 │
│   2. SHADER COMPILATION                                         │
│   ───────────────────────                                        │
│   • Metal Shading Language (MSL)                                │
│   • Pre-compiled shaders для production                         │
│   • Optimized для Apple Silicon                                 │
│                                                                 │
│   3. GPU EXECUTION                                              │
│   ─────────────────────                                          │
│   • Parallel execution на GPU cores                             │
│   • Texture sampling, blending                                  │
│   • Output to framebuffer                                       │
│                                                                 │
│   4. DISPLAY                                                    │
│   ──────────                                                     │
│   • Triple buffering                                            │
│   • VSync с ProMotion (24-120Hz)                                │
│   • Compositor layer                                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему Performance сравним со SwiftUI?

SwiftUI тоже использует Metal под капотом:

```
SWIFTUI vs COMPOSE MP RENDERING
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   SwiftUI:                                                      │
│   ─────────                                                      │
│   SwiftUI View → Core Animation → Metal → GPU                   │
│                  (CALayer)                                      │
│                                                                 │
│   Compose MP:                                                   │
│   ────────────                                                   │
│   Compose UI → Skia → Metal → GPU                               │
│               (direct)                                          │
│                                                                 │
│   Обе системы:                                                   │
│   • Используют Metal                                            │
│   • Hardware-accelerated                                        │
│   • 60/120 FPS capable                                          │
│                                                                 │
│   Разница:                                                       │
│   • SwiftUI использует Core Animation для compositing           │
│   • Compose MP рисует напрямую через Skia                       │
│   • В итоге performance практически идентичен                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Interop: как Compose и UIKit сосуществуют?

**ComposeUIViewController** — ключевой мост:

```
COMPOSE ↔ iOS INTEROP ARCHITECTURE
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   iOS App                                                       │
│   ┌───────────────────────────────────────────────────────────┐ │
│   │                    UIWindow                                │ │
│   │                       │                                    │ │
│   │   ┌───────────────────┴───────────────────┐                │ │
│   │   │                                       │                │ │
│   │   ▼                                       ▼                │ │
│   │ UIViewController                   SwiftUI.View            │ │
│   │   │                                       │                │ │
│   │   ├── Native UIViews                      │                │ │
│   │   │                                       │                │ │
│   │   └── ComposeUIViewController      UIHostingController     │ │
│   │         │                                 │                │ │
│   │         ▼                                 ▼                │ │
│   │   ┌─────────────────────────────────────────────────────┐  │ │
│   │   │              COMPOSE LAYER (MTKView)                 │  │ │
│   │   │   ─────────────────────────────────────────────────  │  │ │
│   │   │   Skia Canvas → Metal Commands → GPU → Pixels        │  │ │
│   │   │                                                      │  │ │
│   │   │   Может содержать "punch holes" для native views:    │  │ │
│   │   │   ┌───────┐  ┌─────────────┐  ┌───────────┐          │  │ │
│   │   │   │UIKit  │  │   Compose   │  │ SwiftUI   │          │  │ │
│   │   │   │ View  │  │   Content   │  │   View    │          │  │ │
│   │   │   └───────┘  └─────────────┘  └───────────┘          │  │ │
│   │   └─────────────────────────────────────────────────────┘  │ │
│   └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Accessibility: как VoiceOver читает canvas?

Compose **синхронизирует semantic tree** с iOS accessibility tree:

```
ACCESSIBILITY BRIDGE
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│   Compose Semantic Tree        iOS Accessibility Tree           │
│   ─────────────────────        ──────────────────────           │
│                                                                 │
│   @Composable                                                   │
│   fun MyScreen() {                                              │
│       Text(                                                     │
│           "Hello",                                              │
│           modifier = Modifier                                   │
│               .semantics {                                      │
│                   contentDescription = "Greeting"               │
│               }                                                 │
│       )                                                         │
│   }                                                             │
│         │                                                       │
│         │    Sync                                               │
│         ▼                                                       │
│   UIAccessibilityElement:                                       │
│   • accessibilityLabel = "Greeting"                             │
│   • accessibilityTraits = .staticText                           │
│   • accessibilityFrame = calculated from layout                 │
│                                                                 │
│   VoiceOver reads: "Greeting, static text"                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Поддерживаемые accessibility features:**
- VoiceOver (screen reader)
- AssistiveTouch (mouse/trackpad)
- Full Keyboard Access
- Voice Control
- Dynamic Type (via Material 3 typography)

---

## Статус (январь 2026)

```
┌─────────────────────────────────────────────────────────────────────┐
│              COMPOSE MULTIPLATFORM iOS STATUS                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Status: ✅ STABLE (since May 2025, version 1.8.0)                 │
│                                                                     │
│   Requirements:                                                     │
│   • Kotlin 2.1.0+ (K2 compiler required)                            │
│   • Compose Multiplatform 1.8.0+                                    │
│   • Xcode 15+ (recommended: 16+)                                    │
│   • macOS for development                                           │
│                                                                     │
│   Rendering: Skia via Metal API                                     │
│                                                                     │
│   Performance:                                                      │
│   • Startup: comparable to native                                   │
│   • Scrolling: on par with SwiftUI (120Hz ProMotion)                │
│   • Size overhead: +9 MB vs native SwiftUI                          │
│   • 96% teams report no major performance concerns                  │
│                                                                     │
│   Developer Experience:                                             │
│   • Hot Reload on iOS Simulator                                     │
│   • Compose Previews in Android Studio                              │
│   • iOS Simulator deployment from Android Studio                    │
│   • Xcode integration for debugging                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Быстрый старт

### 1. Entry Point

```kotlin
// iosMain/kotlin/MainViewController.kt
import androidx.compose.ui.window.ComposeUIViewController

fun MainViewController() = ComposeUIViewController {
    App()  // Shared Composable из commonMain
}
```

### 2. SwiftUI Integration

```swift
// ContentView.swift
import SwiftUI
import SharedKit  // KMP framework

struct ContentView: View {
    var body: some View {
        ComposeView()
            .ignoresSafeArea(.all)
    }
}

struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }

    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {
        // Update if needed
    }
}
```

### 3. Xcode Project Setup

```swift
// App.swift
import SwiftUI

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
    }
}
```

---

## UIKit Interop

### Embed Compose в UIKit

```swift
// ViewController.swift
import UIKit
import SharedKit

class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // Создать ComposeUIViewController
        let composeVC = MainViewControllerKt.MainViewController()

        // Добавить как child
        addChild(composeVC)
        view.addSubview(composeVC.view)
        composeVC.view.frame = view.bounds
        composeVC.view.autoresizingMask = [.flexibleWidth, .flexibleHeight]
        composeVC.didMove(toParent: self)
    }
}
```

### Embed UIKit в Compose

```kotlin
// commonMain/kotlin/NativeViews.kt
@Composable
expect fun NativeMapView(modifier: Modifier)

// iosMain/kotlin/NativeViews.ios.kt
import androidx.compose.ui.interop.UIKitView
import platform.MapKit.MKMapView

@Composable
actual fun NativeMapView(modifier: Modifier) {
    UIKitView(
        factory = {
            MKMapView().apply {
                // Настройка MKMapView
                mapType = MKMapType.MKMapTypeStandard
            }
        },
        modifier = modifier,
        update = { mapView ->
            // Обновление при recomposition
        }
    )
}
```

### UIKitView options

```kotlin
UIKitView(
    factory = { /* создать UIView */ },
    modifier = Modifier.fillMaxSize(),
    update = { view ->
        // Вызывается при recomposition
    },
    onRelease = { view ->
        // Cleanup при dispose
    },
    interactive = true,  // Передавать touch events
    accessibilityEnabled = true  // VoiceOver support
)
```

---

## SwiftUI Interop

### Embed SwiftUI в Compose

**Шаг 1: Создать interface в Kotlin**

```kotlin
// commonMain/kotlin/SwiftUIBridge.kt
interface SwiftUIViewFactory {
    fun createNativeSearchBar(
        query: String,
        onQueryChange: (String) -> Unit
    ): Any  // Returns UIViewController
}

expect fun getSwiftUIFactory(): SwiftUIViewFactory
```

**Шаг 2: Реализовать в Swift**

```swift
// SwiftUIViews.swift
import SwiftUI
import SharedKit

class SwiftUIViewFactoryImpl: SwiftUIViewFactory {
    func createNativeSearchBar(query: String, onQueryChange: @escaping (String) -> Void) -> Any {
        let hostingController = UIHostingController(
            rootView: SearchBarView(query: query, onQueryChange: onQueryChange)
        )
        return hostingController
    }
}

struct SearchBarView: View {
    let query: String
    let onQueryChange: (String) -> Void

    @State private var text: String = ""

    var body: some View {
        TextField("Search...", text: $text)
            .textFieldStyle(RoundedBorderTextFieldStyle())
            .onChange(of: text) { newValue in
                onQueryChange(newValue)
            }
            .onAppear {
                text = query
            }
    }
}
```

**Шаг 3: Использовать в Compose**

```kotlin
// iosMain/kotlin/SwiftUIBridge.ios.kt
actual fun getSwiftUIFactory(): SwiftUIViewFactory = SwiftUIViewFactoryImpl()

@Composable
fun NativeSearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    val factory = remember { getSwiftUIFactory() }

    UIKitViewController(
        factory = {
            factory.createNativeSearchBar(query, onQueryChange) as UIViewController
        },
        modifier = modifier
    )
}
```

---

## "Punch Hole" Interop

Техника, позволяющая native iOS компонентам "просвечивать" через Compose:

```kotlin
@Composable
fun HybridScreen() {
    Box(modifier = Modifier.fillMaxSize()) {
        // Compose content
        Column(modifier = Modifier.fillMaxSize()) {
            // Header - Compose
            TopAppBar(title = { Text("My App") })

            // Content - Compose
            LazyColumn(
                modifier = Modifier.weight(1f)
            ) {
                items(100) { index ->
                    ListItem(headlineContent = { Text("Item $index") })
                }
            }

            // Native TabBar через "punch hole"
            Box(modifier = Modifier.height(49.dp)) {
                NativeTabBar(
                    selectedIndex = selectedTab,
                    onTabSelected = { selectedTab = it }
                )
            }
        }
    }
}
```

**Преимущества:**
- Native iOS look & feel для критичных компонентов
- Touch events корректно передаются
- Seamless визуальная интеграция

---

## Performance

### Benchmarks (CMP 1.8.0+)

| Метрика | Результат |
|---------|-----------|
| Startup time | Comparable to native |
| LazyGrid scrolling | ~9% faster (vs 1.7.0) |
| Missed frames | < 8.33ms (120Hz capable) |
| VisualEffects render | 3.6x faster |
| AnimatedVisibility | ~6% faster |
| GC pause reduction | ~60% |
| Frame time improvement | 25% |

### Рекомендации

```kotlin
// ✅ Использовать LazyColumn/LazyRow
LazyColumn {
    items(items, key = { it.id }) { item ->
        ItemRow(item)
    }
}

// ✅ Стабильные классы для skip recomposition
@Stable
data class ItemState(
    val id: String,
    val title: String
)

// ✅ Remember expensive computations
val processed = remember(rawData) {
    processData(rawData)
}

// ✅ derivedStateOf для computed values
val showButton by remember {
    derivedStateOf { items.size > 10 }
}

// ✅ Built-in animation APIs
val size by animateDpAsState(
    targetValue = if (expanded) 200.dp else 100.dp
)
```

### Offloading to Render Thread (1.10.0+)

```kotlin
// Опционально: выделенный render thread
// Улучшает performance в scenarios без UIKit interop
```

---

## Hot Reload

### Настройка

```kotlin
// build.gradle.kts (CMP 1.10.0+ — уже включено)
// Для ранних версий:
plugins {
    id("org.jetbrains.compose-hot-reload") version "1.0.0"
}
```

### Использование

1. **Android Studio** с KMP plugin
2. Запустить на **iOS Simulator**
3. Изменить код → UI обновляется мгновенно
4. **State сохраняется**

### Ограничения Hot Reload

| Работает | Не работает |
|----------|-------------|
| UI changes | Structural changes |
| Color/text updates | New composable functions |
| Layout modifications | Build config changes |
| Animation tweaks | Swift/Obj-C code |

---

## Accessibility

### VoiceOver Support

```kotlin
@Composable
fun AccessibleButton(
    onClick: () -> Unit,
    text: String
) {
    Button(
        onClick = onClick,
        modifier = Modifier.semantics {
            contentDescription = text
            role = Role.Button
        }
    ) {
        Text(text)
    }
}
```

### Full Keyboard Access

```kotlin
@Composable
fun FocusableItem() {
    val focusRequester = remember { FocusRequester() }

    Box(
        modifier = Modifier
            .focusRequester(focusRequester)
            .focusable()
            .onKeyEvent { event ->
                when (event.key) {
                    Key.Enter -> {
                        // Handle enter
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

## Ограничения

### Что не работает / работает с ограничениями

| Аспект | Статус | Workaround |
|--------|--------|------------|
| Cupertino widgets | ❌ Нет | Material 3 или custom |
| Native text fields | ⚠️ Через interop | UIKitView |
| Push Notifications | ⚠️ Platform-specific | Swift implementation |
| App Extensions | ⚠️ Ограничено | Native Swift |
| Xcode visual debugging | ❌ Нет | Logs, profiling |
| XCTest для Compose | ⚠️ Ограничено | Shared tests |
| App Clips | ⚠️ Ограничено | Native wrapper |

### Размер приложения

```
Native SwiftUI app: ~5 MB
Compose MP app:     ~14 MB (+9 MB overhead)

Breakdown:
• Skia renderer:    ~6 MB
• Kotlin runtime:   ~2 MB
• Compose runtime:  ~1 MB
```

---

## Debugging

### Xcode Integration

```bash
# Запуск с debug symbols
./gradlew :composeApp:linkDebugFrameworkIosSimulatorArm64

# Открыть в Xcode
open iosApp/iosApp.xcworkspace
```

### Logging

```kotlin
// commonMain
expect fun log(message: String)

// iosMain
import platform.Foundation.NSLog

actual fun log(message: String) {
    NSLog(message)
}
```

### Memory Profiling

1. Product → Profile в Xcode
2. Instruments → Allocations
3. Kotlin память помечена "kotlin" tag

---

## Production Checklist

```markdown
## Перед релизом

### Build
- [ ] Release build (не debug)
- [ ] Strip debug symbols
- [ ] ProGuard/R8 для Android
- [ ] Correct signing & provisioning

### Performance
- [ ] Протестировать на реальных устройствах
- [ ] Проверить 60/120 FPS scrolling
- [ ] Memory leaks check
- [ ] Startup time measurement

### Accessibility
- [ ] VoiceOver тестирование
- [ ] Dynamic Type support
- [ ] Color contrast check

### Interop
- [ ] UIKit integration работает
- [ ] Native keyboards
- [ ] Safe area handling
- [ ] Orientation changes
```

---

## Кто использует в production

| Компания | Тип приложения | Результат |
|----------|---------------|-----------|
| **Forbes** | News | 80%+ shared code |
| **The Respawn** | Gaming | 96% shared code |
| **Indie devs** | Various | App Store approved |
| **Google Docs** | Productivity | "KMP validated" |
| **JioHotstar** | Streaming | Production use |

---

## Мифы и заблуждения

### Миф 1: "Compose на iOS — это обёртка над UIKit"

**Заблуждение:** "CMP использует UIKit компоненты под капотом, как React Native"

**Реальность:**
- Compose MP рисует **напрямую через Metal** (GPU API)
- Skia генерирует Metal commands, минуя UIKit
- Это тот же подход что Flutter — canvas-based rendering
- UIKit используется только для interop (когда нужны native компоненты)

---

### Миф 2: "iOS пользователи заметят, что это не native"

**Заблуждение:** "Canvas rendering = плохой iOS experience"

**Реальность:**
- Scrolling physics **эмулирует iOS behavior** (bounce, velocity, deceleration)
- 120Hz ProMotion поддерживается полностью
- Touch feedback идентичен native
- 96% команд не сообщают о UX проблемах

```
Пример: Wrike (production app) — пользователи не различают
Compose и native экраны в одном приложении
```

---

### Миф 3: "SwiftUI interop — это костыль"

**Заблуждение:** "Нельзя нормально использовать SwiftUI views в Compose"

**Реальность:** Interop работает в **обе стороны:**

| Направление | Метод | Пример использования |
|-------------|-------|---------------------|
| Compose → iOS app | ComposeUIViewController | Весь UI на Compose |
| SwiftUI → Compose | UIKitViewController | Native карты, камера |
| UIKit → Compose | addChild(composeVC) | Постепенная миграция |
| Compose → SwiftUI | UIHostingController | Native search bar |

**"Punch hole"** interop позволяет seamless интеграцию.

---

### Миф 4: "Hot Reload не работает на iOS"

**Заблуждение:** "Hot Reload — это только для Android"

**Реальность:**
- Hot Reload работает на **iOS Simulator** (с CMP 1.8.0+)
- State сохраняется между изменениями
- Изменения UI видны мгновенно
- Ограничение: не работает на физических устройствах (Apple signing)

---

### Миф 5: "VoiceOver не работает с canvas-based UI"

**Заблуждение:** "Accessibility невозможна без native widgets"

**Реальность:** Compose **полностью поддерживает** iOS accessibility:

| Feature | Status | Реализация |
|---------|--------|-----------|
| VoiceOver | ✅ | Semantic tree sync |
| AssistiveTouch | ✅ | Touch event mapping |
| Full Keyboard Access | ✅ | Focus management |
| Voice Control | ✅ | Action exposure |
| Switch Control | ✅ | Accessibility elements |

Semantic tree из Compose синхронизируется с iOS accessibility tree.

---

### Миф 6: "App Store отклонит приложение на Compose"

**Заблуждение:** "Apple не любит не-native UI frameworks"

**Реальность:**
- Forbes, The Respawn, множество indie apps — **approved** в App Store
- Flutter (тот же Skia) имеет тысячи apps в App Store
- Apple не запрещает canvas-based rendering
- Главное — соблюдать Human Interface Guidelines

---

## Рекомендуемые источники

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [CMP 1.8.0 Release](https://blog.jetbrains.com/kotlin/2025/05/compose-multiplatform-1-8-0-released-compose-multiplatform-for-ios-is-stable-and-production-ready/) | Official | iOS Stable announcement |
| [iOS Integration](https://www.jetbrains.com/help/kotlin-multiplatform-dev/compose-ios-ui-integration.html) | Official | UIKit/SwiftUI interop |
| [Hot Reload](https://kotlinlang.org/docs/multiplatform/compose-hot-reload.html) | Official | Настройка Hot Reload |

### Статьи и блоги

| Источник | Тип | Описание |
|----------|-----|----------|
| [Touchlab iOS Interop](https://touchlab.co/jetpack-compose-ios-interop) | Expert | Практические примеры |
| [KMPShip iOS Stable](https://www.kmpship.app/blog/compose-multiplatform-ios-stable-2025) | Blog | Обзор 1.8.0 |
| [Infinum SwiftUI Bridge](https://infinum.com/blog/kotlin-multiplatform-swiftui/) | Blog | SwiftUI integration |

### CS-фундамент

| Концепция | Зачем изучать | Где применяется |
|-----------|--------------|-----------------|
| [[graphics-apis-fundamentals]] | Понять Metal API | Rendering через GPU |
| [[native-code-interop]] | FFI между языками | Kotlin ↔ Swift/Obj-C |
| [[rendering-pipelines]] | GPU rendering | Skia → Metal → Display |
| [[accessibility-fundamentals]] | Assistive technologies | VoiceOver, semantic tree |
| [[touch-event-handling]] | iOS touch system | Gesture recognition |
| [[memory-management-arc]] | Apple ARC | Kotlin/Native ↔ iOS |

---

*Проверено: 2026-01-09 | Compose Multiplatform 1.10.0, iOS Stable since 1.8.0, Kotlin 2.1.21*
