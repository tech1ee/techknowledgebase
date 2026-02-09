# Kotlin Multiplatform: Architecture, Expect/Actual, and Cross-Platform Development

Kotlin Multiplatform represents a fundamental rethinking of how developers build applications for multiple platforms. Rather than writing separate codebases for each platform or accepting the limitations of cross-platform frameworks, Kotlin Multiplatform enables sharing business logic while preserving access to native platform capabilities. This approach acknowledges a reality that other cross-platform solutions often ignore: platforms are different, and attempting to abstract away those differences entirely sacrifices the unique strengths of each platform.

The architecture of Kotlin Multiplatform reflects this philosophy. Common code expresses platform-independent logic. Platform-specific code implements interfaces that common code depends upon. The expect/actual mechanism bridges these layers with compile-time safety. Build configuration through Gradle orchestrates compilation for each target. Understanding this architecture enables developers to design systems that maximize code sharing while respecting platform differences.

## The Philosophy of Shared Code

The history of cross-platform development reveals a spectrum of approaches. At one extreme, frameworks like React Native or Flutter abstract platforms entirely behind a unified API. Applications built this way share nearly all code but access platforms through abstraction layers that may not expose every capability. At the other extreme, developers maintain separate codebases for each platform, duplicating logic but achieving complete platform fidelity.

Kotlin Multiplatform occupies a deliberate middle ground. It acknowledges that user interfaces are deeply platform-specific and that forcing a common UI paradigm compromises user experience. Native users expect native interfaces. At the same time, it recognizes that business logic, data processing, networking, and domain models are genuinely platform-independent. Sharing this logic eliminates duplication without sacrificing platform identity.

This philosophy manifests in the code structure. Common code contains domain models, business rules, data transformation logic, and algorithm implementations. Platform code contains UI implementations, platform service integrations, and platform-specific optimizations. The boundary between common and platform code is explicit and enforced by the compiler.

The expect/actual mechanism enables common code to depend on platform capabilities without knowing their implementation. Common code declares what it expects; platform code provides the actual implementation. This inversion enables common code to be written first, with platform implementations filled in later.

## Kotlin Multiplatform Project Structure

A Kotlin Multiplatform project organizes code into source sets. The common source set contains code shared across all platforms. Platform-specific source sets contain code for individual targets. Intermediate source sets can share code among subsets of targets.

The common source set is the heart of shared code. Every target must compile the common source set, so it can only use Kotlin standard library features available on all targets. Platform-specific APIs are not directly accessible. Instead, common code uses expect declarations for platform-specific needs.

Platform source sets build on the common source set. They can access platform-specific APIs directly. They provide actual implementations for expect declarations. They can extend, implement, or use types from common code.

Intermediate source sets enable sharing code among related platforms. An iOS source set might be shared between iosArm64 and iosX64 targets. A native source set might be shared among all native targets. A JVM source set might be shared among JVM and Android.

This hierarchical structure enables progressive specialization. Common code is most shared. Intermediate code shares among platform families. Platform code is fully specific. The compiler enforces that each level only accesses what is available to all its members.

## Compilation Targets and Backends

Kotlin Multiplatform compiles to multiple backends, each producing different output for different platforms. Understanding these backends helps developers choose appropriate targets and understand platform capabilities.

The JVM backend produces standard Java bytecode, running on any compliant JVM. This target covers server applications, Android applications, and desktop applications using Java-based frameworks. The JVM target has access to the full Java standard library and interoperates seamlessly with Java code.

The JavaScript backend produces JavaScript code for browser and Node.js environments. The output can be optimized for either environment. JavaScript target code can interoperate with existing JavaScript libraries through external declarations or TypeScript definitions.

The Native backend produces native binaries without requiring a virtual machine. Native targets include iOS (arm64, x64 for simulators), macOS, Linux, Windows, and WebAssembly. Native compilation uses LLVM for code generation. Native targets can interoperate with C libraries through the cinterop tool.

The Android target is distinct from the JVM target, producing Android-compatible bytecode. While similar to JVM, the Android target respects Android's runtime constraints and can access Android-specific APIs.

Each backend has different capabilities and constraints. The JVM backend supports reflection extensively. The Native backend has limited reflection. The JavaScript backend operates in a single-threaded environment. Understanding these differences guides architectural decisions.

## The Expect/Actual Mechanism

The expect/actual mechanism is the primary tool for bridging common and platform code. An expect declaration in common code declares what must exist. Actual declarations in platform code provide implementations. The compiler verifies that every expect has a corresponding actual for each target.

Expect functions declare a function signature without implementation. Platform code provides actual functions with the same signature plus implementation. Common code calls the expect function; at runtime, the platform's actual function executes.

Expect classes are more complex. The expect declaration specifies the class structure including constructors, properties, and methods. Actual implementations can be real classes with matching structure or typealiases to existing platform types. Typealiases are powerful because they allow platform-native types to satisfy expect declarations.

Expect properties declare properties without backing implementations. Actual properties provide implementations, potentially as computed properties, backing fields, or delegation to platform APIs.

Expect annotations enable platform-specific annotation processing. Common code uses the expect annotation; platform code maps it to platform-specific annotations that tools understand.

Expect objects and companion objects follow similar patterns, with common declarations and platform implementations.

## Expect/Actual Design Patterns

Effective use of expect/actual follows patterns that maximize sharing while enabling platform flexibility.

The interface pattern defines a common interface with platform implementations. Common code programs against the interface. Expect declarations provide factory functions returning the interface. Platform code implements the interface and the factory. This pattern is flexible but requires more boilerplate.

The typealias pattern uses expect classes with actual typealiases to platform types. When a platform has an existing type matching the expect declaration, a typealias avoids creating a wrapper. This pattern is efficient but requires the platform type to match the expected API exactly.

The extension pattern adds platform-specific functionality through extensions. Common code defines a base type with core operations. Platform code extends the type with additional capabilities. This keeps the core API shared while enabling platform additions.

The capability pattern uses optional dependencies to enable platform features when available. Common code defines optional interfaces. Platform code implements these interfaces only when the underlying capability exists. Common code checks for capability availability before use.

The encapsulation pattern hides platform complexity behind simple common interfaces. Common code defines high-level operations without exposing implementation details. Platform code implements these operations using whatever platform mechanisms are appropriate. This maximizes implementation freedom while maintaining API consistency.

## Common Code Constraints and Capabilities

Common code operates under constraints imposed by the need for universal availability. Understanding these constraints helps developers design appropriate common abstractions.

The Kotlin standard library provides a common subset available on all platforms. Collections, sequences, text processing, and mathematical operations work everywhere. Platform-specific standard library features like Java streams or JavaScript arrays are not directly accessible.

Threading models differ across platforms. The JVM has threads. JavaScript is single-threaded with async operations. Native has its own threading model with specific memory management requirements. Common code must be designed with thread safety in mind but cannot use platform-specific threading primitives directly.

Kotlinx libraries provide multiplatform implementations of common needs. Coroutines provide async programming across all platforms. Serialization provides JSON and other format handling. DateTime provides date and time operations. These libraries abstract platform differences while providing idiomatic Kotlin APIs.

Reflection is limited in common code. The JVM has rich reflection. Native and JavaScript have more limited capabilities. Common code should minimize reflection use or gate reflection behind expect declarations with platform-specific implementations.

Annotations may have different effects on different platforms. An annotation meaningful to the JVM might be ignored by Native. Common code should document expected annotation behavior and verify it on each platform.

## Platform-Specific Considerations

Each platform brings unique considerations that influence multiplatform design.

JVM targets have the richest capability set. Full Java interop is available. Reflection is comprehensive. Threading is straightforward. Most existing Kotlin libraries work without modification. JVM-specific code can use any Java library.

Android targets are similar to JVM but with constraints. Android runtime imposes limitations. UI code uses Android framework classes. Lifecycle management is essential. Android-specific code must respect the Android programming model.

iOS targets use Kotlin/Native, which compiles to native code callable from Swift and Objective-C. Kotlin classes appear as Objective-C classes to Swift code. iOS-specific code can use UIKit and other Apple frameworks through platform declarations or cinterop.

JavaScript targets produce code that runs in browsers or Node.js. DOM manipulation is available in browsers. Node.js APIs are available in that environment. JavaScript-specific code can interop with JavaScript libraries.

Native desktop targets (macOS, Linux, Windows) produce standalone executables. They can use platform C libraries through cinterop. UI frameworks vary by platform and may require significant platform-specific code.

## Gradle Configuration for Multiplatform

Gradle builds Kotlin Multiplatform projects, with configuration in the Kotlin DSL. Understanding this configuration enables customizing the build for specific needs.

The kotlin multiplatform plugin activates multiplatform support. Within the kotlin block, targets are declared. Each target declaration specifies a platform and optional configuration.

Target declarations include platform type and name. JVM targets use the jvm function. Native targets use functions like iosArm64, macosX64, or linuxX64. JavaScript targets use js with configuration for browser or node.

Source sets are configured within the sourceSets block. Each source set has a name following conventions: commonMain, commonTest, jvmMain, iosMain, and so on. Custom intermediate source sets can be created and positioned in the hierarchy.

Dependencies are declared per source set. CommonMain dependencies are available to all targets. Platform source set dependencies add platform-specific libraries. The implementation, api, and compileOnly configurations work as with single-platform projects.

Compiler options can be configured globally or per target. Options affecting all targets go in the top-level kotlin block. Target-specific options go within the target configuration.

Publishing multiplatform libraries requires additional configuration. The maven-publish plugin works with multiplatform. The published artifact includes metadata plus platform-specific artifacts.

## Hierarchical Project Structure

The hierarchical project structure, also called HMPP, enables sophisticated code sharing among platform subsets. Rather than only common and platform levels, intermediate source sets share code among related platforms.

The hierarchy is defined through depends on relationships. A source set declares it depends on another source set, inheriting its code and constraints. Platform source sets typically depend on intermediate source sets which depend on commonMain.

Typical hierarchies include groupings like native (all native targets), apple (iOS, macOS, tvOS, watchOS), posix (platforms with POSIX APIs), and custom groupings for project-specific needs.

Intermediate source sets enable using APIs available to their members but not universally. A native source set can use native-specific standard library features. An apple source set can use Apple-specific constructs. The compiler ensures each source set only uses what is available.

Configuring the hierarchy requires careful thought about what sharing is beneficial. Too many intermediate levels add complexity. Too few force code into either fully common or fully platform buckets. The right structure matches the actual sharing opportunities in the codebase.

## Interoperability: Calling Platform Code from Kotlin

Kotlin Multiplatform code frequently needs to call platform libraries. Each target has mechanisms for this interoperability.

JVM targets use standard Java interop. Kotlin calls Java code directly. Java types appear as Kotlin types with appropriate nullability. No special configuration is needed for Java libraries.

JavaScript targets use external declarations to describe JavaScript APIs. The external modifier marks declarations that have no Kotlin implementation but call JavaScript. TypeScript definitions can be converted to external declarations automatically.

Native targets use cinterop to generate Kotlin declarations from C header files. A def file configures which headers to process. The cinterop tool generates a library containing Kotlin declarations that call the C functions.

Apple platform frameworks are processed through cinterop automatically. Platform libraries like Foundation, UIKit, and AppKit are available without manual configuration. Third-party frameworks can be processed similarly.

Objective-C interop on Apple platforms is particularly seamless. Kotlin classes appear as Objective-C classes. Objective-C classes appear as Kotlin classes. Swift can call Kotlin code through the Objective-C bridge.

## Interoperability: Exposing Kotlin to Platform Code

Multiplatform projects often need to expose Kotlin APIs for platform consumption. Each target has different exposure mechanisms.

JVM targets produce classes callable from Java directly. Java code imports Kotlin classes and calls them naturally. JvmName and other annotations can adjust how Kotlin appears to Java.

JavaScript targets can expose Kotlin as a JavaScript module. The JsExport annotation marks declarations for export. The compiled JavaScript includes these exports following JavaScript module conventions.

Native targets produce Kotlin/Native libraries or frameworks. For Apple platforms, framework output creates an Xcode-compatible framework. Swift and Objective-C code can import and use this framework. KDoc comments become documentation in the generated headers.

The XCFramework format packages frameworks for multiple Apple architectures. This is the standard distribution format for Apple libraries. Gradle can build XCFrameworks from multiplatform projects.

## Testing Multiplatform Code

Testing multiplatform code requires running tests on each target platform. The test source sets mirror main source sets with commonTest and platform test sets.

CommonTest contains tests for common code. These tests run on all platforms. They use the kotlin-test library, which provides multiplatform testing APIs. Assertions, test annotations, and basic structure work across platforms.

Platform test source sets contain platform-specific tests. These tests only run on their specific platform. They can test platform implementations of expect declarations and any platform-specific extensions.

Test dependencies may include platform-specific testing libraries. JUnit integrates with kotlin-test on JVM. The JavaScript test runner uses appropriate JavaScript test frameworks. Native tests use the native test runner.

Running tests requires invoking the appropriate Gradle tasks. The check task runs all tests. Platform-specific test tasks run only those platform's tests. IDE integration enables running individual tests during development.

## Continuous Integration for Multiplatform

Building and testing multiplatform projects in CI requires consideration of platform availability. Not all targets can build on all hosts.

Native targets generally require matching or compatible hosts. iOS and macOS targets require macOS. Linux targets require Linux. Windows targets require Windows. Cross-compilation is limited.

A typical CI setup uses multiple runners. macOS runners build and test Apple targets. Linux runners handle Linux targets and JVM. Windows runners handle Windows targets. Common code tests run on all platforms.

Caching improves CI performance. Kotlin/Native downloads and compiles platform libraries on first use. Caching these artifacts significantly speeds subsequent builds.

Parallelization helps when targets are independent. Different platforms can build simultaneously on different runners. The final publish step waits for all platforms.

Publishing from CI requires coordinating platform artifacts. The metadata artifact aggregates platform information. Each platform publishes its artifacts. Repository configuration handles multiplatform publications.

## Migration Strategies

Adopting Kotlin Multiplatform in existing projects requires thoughtful migration. Several strategies can guide this process.

The extraction approach identifies existing code suitable for sharing. Business logic, models, and utilities are candidates. This code is refactored to remove platform dependencies, then moved to a common module. Platform projects depend on the shared module.

The expect/actual bridge approach creates interfaces in common code matching existing platform APIs. Actual implementations wrap existing platform code. Over time, implementations can be unified where platforms align.

The gradual approach starts with a single shared component. Perhaps networking logic or a specific feature. Success with this component guides expansion. Each phase adds more shared code based on lessons learned.

The greenfield approach creates new features multiplatform from the start. Existing features remain platform-specific. Over time, the proportion of multiplatform code grows as new development follows multiplatform patterns.

Risk mitigation includes maintaining the ability to fall back. Platform code can provide alternative implementations. Shared code can be forked to platform-specific versions if problems arise. Conservative adoption reduces risk.

## Common Challenges and Solutions

Multiplatform development presents characteristic challenges that experienced developers learn to navigate.

Dependency availability varies across platforms. A library available for JVM may not support other platforms. Solutions include finding multiplatform alternatives, creating expect/actual abstractions around single-platform libraries, or accepting reduced sharing.

Build complexity increases with multiple targets. Longer build times, more configuration, and platform-specific build issues all require attention. Incremental improvements to build configuration, strategic caching, and selective target building during development help.

Debugging across platforms requires different tools. Each platform has its own debugger. Platform-specific bugs may not reproduce elsewhere. Good logging and observability help diagnose cross-platform issues.

Team skill requirements broaden. Developers need familiarity with multiple platforms. Specialization is still valuable, but some breadth helps everyone. Documentation and knowledge sharing become more important.

Tooling maturity varies. IDE support for multiplatform continues improving but may lag behind single-platform development. Some refactorings and inspections may not understand multiplatform structure fully.

## Future Directions

Kotlin Multiplatform continues evolving with improvements across the stack.

Compose Multiplatform extends Jetpack Compose to iOS, desktop, and web. This provides a Kotlin-native UI framework for platforms beyond Android. Sharing UI code becomes possible for projects where appropriate.

Tooling improvements make multiplatform development more seamless. Better IDE integration, faster builds, and improved error messages all contribute. The goal is making multiplatform development feel as natural as single-platform.

Library ecosystem growth expands what can be shared. More libraries adopt multiplatform. Interop improvements make platform libraries more accessible. The practical sharing percentage increases.

New targets expand platform reach. WebAssembly support improves. Embedded systems become viable targets. Wherever Kotlin runs, multiplatform potentially applies.

Memory management improvements in Kotlin/Native reduce friction. The new memory model enables shared mutable state across threads. This aligns Native's capabilities more closely with JVM, enabling more code sharing.

## Conclusion

Kotlin Multiplatform offers a pragmatic approach to cross-platform development. By sharing logic while respecting platform uniqueness, it avoids the compromises of other cross-platform solutions. The expect/actual mechanism provides compile-time safety for platform abstractions. Gradle configuration orchestrates multi-target builds. The hierarchical source set structure enables nuanced sharing.

Success with Kotlin Multiplatform requires understanding its architecture and constraints. Common code must be designed for portability. Platform code provides implementations and extensions. The boundary between them is explicit and intentional.

As the ecosystem matures, Kotlin Multiplatform becomes increasingly practical for production use. Teams seeking to reduce duplication while maintaining platform quality find it a compelling option. The investment in understanding its architecture pays dividends in reduced maintenance burden and increased development velocity across platforms.
