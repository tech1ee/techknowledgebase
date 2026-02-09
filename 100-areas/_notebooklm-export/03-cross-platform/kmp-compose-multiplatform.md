# Compose Multiplatform: Shared UI Across Platforms

Compose Multiplatform extends Jetpack Compose beyond Android to iOS, desktop, and web platforms. The same declarative UI code can render on multiple targets, potentially enabling shared UI in addition to shared business logic. This represents a significant expansion of what KMP can share, but it comes with trade-offs that teams must understand to make appropriate decisions.

## The Evolution from Android-Only to Multiplatform

Jetpack Compose was designed as Android's modern declarative UI toolkit. Its architecture, however, was designed with multiplatform potential in mind. The Compose compiler plugin and runtime are separate from Android-specific rendering. This separation enabled JetBrains to create Compose Multiplatform, using the same programming model on other platforms.

Compose for Desktop reached stable status first, rendering through Skia to desktop windows on macOS, Windows, and Linux. The same composable functions that build Android UI build desktop UI with appropriate adaptations for desktop input and windowing.

Compose for iOS followed, rendering through Skia on iOS devices. Composable functions produce UI that appears on iPhone and iPad screens. The rendering path uses Skia rather than UIKit, meaning Compose draws its own pixels rather than using native iOS controls.

Compose for Web targets browser deployment. The rendering can use either DOM elements styled with CSS or Skia-based canvas rendering matching other platforms. The DOM approach provides better web integration while Skia provides visual consistency.

JetBrains maintains Compose Multiplatform while Google maintains Android Jetpack Compose. The projects collaborate, with JetBrains extending Google's foundation. Updates to Android Compose typically flow to Compose Multiplatform, though version synchronization is not instantaneous.

## How Compose Multiplatform Rendering Works

Understanding the rendering architecture clarifies what Compose Multiplatform actually does on each platform.

On Android, Compose renders through the standard Android graphics pipeline. Composables become Android Views or draw directly to Android canvases. This is native Android rendering using Android graphics primitives.

On iOS, Compose renders through Skia, a 2D graphics library also used by Chrome, Firefox, and Flutter. A Metal-backed Skia context draws Compose UI to the screen. The rendering does not use UIKit controls. A Compose Button is not a UIButton; it is pixels drawn by Skia that look like a button and respond to touches.

This distinction matters for understanding platform fidelity. UIKit controls carry behaviors accumulated over years of iOS development: scrolling physics, haptic feedback, accessibility integration, text editing, and more. Skia-rendered controls must implement these behaviors explicitly rather than inheriting them from the platform.

On desktop, Skia renders to native windows through platform-appropriate graphics contexts. The windowing system handles window chrome, focus, and input routing. Compose handles content within the window.

On web, DOM rendering creates HTML elements that CSS styles. This integrates with web accessibility and styling systems. Canvas rendering uses Skia targeting HTML canvas, providing visual consistency at the cost of web integration.

## Shared UI Code Structure

Compose Multiplatform projects structure code to maximize sharing while allowing platform customization.

The commonMain source set contains shared composables. These composables use common Compose APIs that work across all targets. Layout composables like Row, Column, and Box work everywhere. Basic components like Text and Image work everywhere. Modifiers for styling and interaction work everywhere.

Platform source sets contain platform-specific composables and entry points. Android's MainActivity sets up the Compose content. iOS's MainViewController creates the Compose view controller. Desktop's main function creates windows. Web's entry point mounts to DOM elements.

The expect/actual mechanism extends to composables when needed. A composable might have platform-specific behavior requiring actual implementations. However, the goal is minimizing this by providing common implementations that work everywhere.

Resource access differs between platforms. Images, strings, and other resources need platform-appropriate loading. Libraries like Moko Resources or JetBrains' resource system provide multiplatform resource access, enabling shared composables to access resources defined once and bundled appropriately for each platform.

## Building a Multiplatform UI

Creating multiplatform composables follows patterns similar to Android Compose with attention to cross-platform considerations.

Common composables should not depend on platform-specific APIs. Referencing Android Context, iOS UIDevice, or desktop Window in shared code prevents that code from compiling for other platforms. Platform capabilities should be accessed through abstraction or injected through parameters.

Theming typically uses MaterialTheme which works across platforms. Color schemes, typography, and shapes defined in common code apply everywhere. Platform-specific theme variations can override common values when needed.

Navigation can use multiplatform navigation libraries like Voyager or Decompose. These libraries provide navigation that works across Compose targets. Android-specific navigation libraries do not work in shared code.

State management patterns from Android Compose apply to multiplatform. ViewModel patterns work through multiplatform ViewModel libraries. State hoisting works identically. Remember and derivedStateOf work identically.

Testing composables uses multiplatform testing frameworks. The compose-multiplatform-testing library enables testing composable behavior across platforms. UI tests verify that composables render correctly and respond to interaction.

## Platform Fidelity Considerations

The key trade-off in Compose Multiplatform is between code sharing and platform-native experience. This trade-off deserves careful consideration.

Android apps using Compose Multiplatform are native Android apps with native Compose rendering. There is no platform fidelity concern on Android because Compose is the native framework.

iOS apps using Compose Multiplatform are not using UIKit. The UI looks similar but is rendered differently. Scrolling physics, text editing behavior, navigation transitions, and many subtle interactions differ from what iOS users expect. These differences may be imperceptible for simple applications or jarring for complex ones.

The significance of platform fidelity depends on application type. A utility application where users focus on functionality may tolerate non-native UI. A consumer application competing with polished native apps may suffer from subtle wrongness that users feel without articulating.

Some projects use Compose Multiplatform for most UI while dropping to native for critical interactions. A login flow might use shared Compose. A photo gallery might use native UICollectionView for iOS-perfect scrolling. This hybrid approach captures sharing benefits where they matter while maintaining fidelity where it matters.

Testing with real users on iOS devices helps assess fidelity impact. What engineers tolerate may differ from what users expect. User feedback on iOS prototypes reveals whether platform differences affect perception.

## Integration with Native Platforms

Compose Multiplatform integrates with native platform code through embedding mechanisms.

On Android, Compose Multiplatform IS Android Compose, so no special integration is needed. ComposeView embeds Compose in View hierarchies. AndroidView embeds Views in Compose. These standard mechanisms apply.

On iOS, UIKitView embeds UIKit views in Compose hierarchies. This enables using native iOS components where needed. A Compose screen might embed a MKMapView for mapping or a WKWebView for web content. The native views work normally while surrounding UI is Compose-rendered.

Conversely, UIViewControllerRepresentable can embed Compose view controllers in SwiftUI. An existing SwiftUI app can incorporate Compose views for shared components. This enables gradual adoption or hybrid architectures.

The integration boundaries require attention. Gesture handling across the boundary can be complex. Focus management between Compose and native components requires coordination. Accessibility must be configured appropriately on both sides.

## Performance Characteristics

Performance of Compose Multiplatform varies by platform and usage.

Android performance matches Jetpack Compose performance because the rendering path is identical. The maturity of Android Compose and its optimizations apply directly.

iOS performance depends on Skia rendering efficiency and Compose runtime overhead. For typical application UI, performance is acceptable. Complex animations, long lists, or heavy custom drawing may reveal performance differences versus native UIKit.

Startup time on iOS includes initializing the Compose runtime and Skia context. This adds overhead versus pure native apps. The impact varies with application complexity and can be mitigated through appropriate architecture.

Memory usage includes the Compose runtime, Skia library, and rendered UI data structures. This baseline exceeds minimal native applications but is reasonable for typical apps.

Binary size increases due to including Skia and the Compose runtime. The increase is significant in absolute terms but may be acceptable relative to typical app sizes. Measuring for specific projects helps assess acceptability.

## When to Choose Compose Multiplatform

Several factors guide the decision to use Compose Multiplatform versus native UI.

Teams with strong Kotlin skills and limited iOS experience benefit from writing UI in familiar Kotlin rather than learning SwiftUI. The learning curve for Compose is lower for Android developers than the learning curve for SwiftUI.

Projects with limited resources that must ship on both platforms benefit from genuine UI code sharing. Writing UI once is faster than writing it twice, even accounting for platform adaptation.

Applications where UI is relatively simple and platform conventions are less critical work well with Compose Multiplatform. Business tools, utilities, and internal applications often fit this profile.

Projects that can accept iOS UI that looks similar but feels slightly different may find Compose Multiplatform acceptable. Not all users notice platform fidelity differences, and some applications do not require perfect native feel.

Conversely, teams with strong platform expertise, applications competing on experience quality, and projects targeting demanding iOS users may prefer native UI on each platform. The code sharing benefit must outweigh the platform fidelity cost.

Hybrid approaches provide middle ground. Share some screens with Compose Multiplatform while implementing critical screens natively. Use Compose for common patterns while using native for platform-specific features.

## Comparison with Other Cross-Platform Approaches

Compose Multiplatform fits among several cross-platform UI approaches with different characteristics.

Flutter also uses Skia-based rendering with full UI code sharing. Flutter has more maturity on iOS, having targeted iOS from the start. The language is Dart rather than Kotlin. Teams choosing between Flutter and Compose Multiplatform often consider language preference and existing Kotlin investment.

React Native bridges to native components rather than drawing its own pixels. UI may feel more native because it uses actual native controls. The language is JavaScript or TypeScript. Performance characteristics differ because of the bridge overhead.

Native UI on each platform with KMP shared logic provides maximum platform fidelity with business logic sharing. This is more work than shared UI but produces the most native experience. Teams with platform UI expertise often prefer this approach.

The choice depends on team composition, product requirements, and acceptable trade-offs. No approach is universally best. Understanding what each approach actually does enables informed decisions.

## Future Evolution

Compose Multiplatform continues evolving with improved iOS support a key focus.

iOS platform integration improves with each release. Better interoperability with UIKit, improved scrolling and text editing, and more platform-appropriate default behaviors address fidelity concerns incrementally.

The Compose ecosystem grows with more multiplatform libraries. Libraries that were Android-only become multiplatform, expanding what shared composables can do.

JetBrains investment in Compose Multiplatform suggests continued development. The alignment with Google's Compose development provides stable foundation.

Teams adopting Compose Multiplatform today should expect continued improvement. What requires workarounds today may work natively in future versions. Early adoption involves accepting current limitations with expectation of improvement.

## Conclusion

Compose Multiplatform extends the Compose programming model beyond Android to iOS, desktop, and web. Shared composable code produces UI on all targets, dramatically expanding potential code sharing.

The trade-off is platform fidelity, particularly on iOS where Skia rendering replaces UIKit controls. Applications using Compose Multiplatform on iOS look similar to native but may feel different in subtle ways.

Teams must evaluate this trade-off for their specific context. Development efficiency from shared UI benefits constrained teams. Platform fidelity concerns may override for experience-critical applications. Hybrid approaches blend sharing and native implementation as appropriate.

Compose Multiplatform represents a significant capability for KMP. Combined with shared business logic, it enables truly cross-platform applications from a single Kotlin codebase. Whether to use this capability depends on project-specific analysis of benefits versus trade-offs.
