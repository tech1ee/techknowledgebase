# Dependency Injection in Android: Hilt, Koin, and Manual Approaches

## Understanding Dependency Injection

Dependency injection is a software design pattern where objects receive their dependencies from external sources rather than creating them internally. This seemingly simple concept has profound implications for code organization, testability, and maintainability in Android applications. When a class creates its own dependencies, it becomes tightly coupled to specific implementations, making testing difficult and modification risky. Dependency injection inverts this control, allowing external code to provide dependencies, which in turn enables flexibility and isolation.

The Android platform presents unique challenges for dependency injection due to the framework-controlled instantiation of Activities, Fragments, and other components. Developers cannot simply add constructor parameters to Activities because the Android system instantiates these classes. This constraint has driven the development of specialized dependency injection solutions that work within Android's constraints while providing the benefits of inversion of control.

The evolution of dependency injection in Android spans over a decade, from early manual approaches through multiple generations of frameworks. Understanding this history provides context for why current solutions exist and how they address accumulated lessons about what works and what fails in Android dependency injection.

## The Problem Without Dependency Injection

When classes create their own dependencies internally, numerous problems emerge that compound as applications grow in size and complexity.

Consider a repository class that needs to make network requests and cache data locally. Without dependency injection, this class creates its own Retrofit instance and Room database. Each instantiation of this repository creates new instances of these expensive objects. Memory usage increases unnecessarily, and the benefits of connection pooling and other optimizations are lost because multiple clients exist rather than shared instances.

Testing becomes extremely difficult when dependencies are created internally. To test the repository mentioned above, developers would need to somehow intercept the network requests it makes through its internally-created Retrofit instance. This typically requires mock server frameworks that intercept actual HTTP traffic, adding complexity and reducing test reliability. With dependency injection, a mock implementation of the network client can simply be passed to the repository, enabling fast and reliable unit tests.

Tight coupling prevents code reuse and modification. If a repository directly instantiates a specific API client implementation, switching to a different implementation requires modifying the repository. This violates the open-closed principle, which states that classes should be open for extension but closed for modification. With dependency injection, the repository depends on an interface, and different implementations can be provided without changing the repository code.

Global state and singletons often emerge as workarounds when proper dependency injection is absent. Developers create Application subclass instances or static variables to share expensive objects. This global state creates hidden dependencies that are not visible in class signatures, makes testing more difficult because global state must be reset between tests, and introduces potential memory leaks if these globals reference Android context objects incorrectly.

Configuration changes in Android exacerbate these problems. Activities and Fragments are destroyed and recreated during configuration changes like rotation. Without proper dependency injection and scoping, objects might be recreated unnecessarily, cached data might be lost, or leaked references to destroyed components might prevent garbage collection.

## The Evolution of Dependency Injection Frameworks

The Android dependency injection landscape has evolved significantly, with each generation of tools addressing limitations discovered in previous approaches.

In the early days of Android development, developers used manual dependency injection or service locator patterns. These approaches worked but required significant boilerplate code and offered no compile-time safety. Developers could forget to register dependencies or request wrong types, discovering errors only at runtime.

Dagger, originally created by Square in 2012, introduced compile-time dependency injection to Android. Using annotation processing, Dagger generated code at compile time that wired dependencies together. This approach caught configuration errors during compilation rather than at runtime. However, Dagger required significant boilerplate to configure, with Component interfaces, Module classes, and careful attention to scoping rules.

Dagger 2, released by Google in 2015, removed the reflection used in the original Dagger, making it fully compile-time with zero runtime overhead. While more efficient, Dagger 2 maintained the configuration complexity of its predecessor, requiring developers to manually define component hierarchies, subcomponents for different scopes, and carefully manage the relationships between them.

Koin emerged in 2017 as a lightweight alternative taking a fundamentally different approach. Rather than compile-time code generation, Koin uses a domain-specific language in Kotlin to define dependencies at runtime. This service locator pattern provides simpler syntax and faster build times but loses compile-time safety. Errors in dependency configuration only surface when the code executes.

Hilt, released by Google in 2020, builds on Dagger 2 while dramatically reducing configuration complexity. Hilt provides predefined component hierarchies matching Android's typical architecture, automatic integration with Android Jetpack components, and conventions that eliminate most boilerplate. Hilt has become Google's official recommendation for dependency injection in Android applications.

## Compile-Time Versus Runtime Dependency Injection

The fundamental distinction between Hilt and Koin lies in when dependency graphs are validated and how injection code is generated.

Compile-time dependency injection frameworks like Hilt and Dagger analyze annotations during compilation. They generate actual Java or Kotlin code that instantiates and wires dependencies. If a required dependency is missing or types do not match, the compiler produces an error. Developers discover configuration problems before the application ever runs, preventing entire categories of runtime crashes.

Runtime dependency injection frameworks like Koin build dependency graphs when the application starts. The configuration uses regular Kotlin code that executes at runtime. If a dependency is missing, the application compiles successfully but crashes when that dependency is requested. This means thorough testing is essential to catch configuration errors that the compiler cannot detect.

Build time differs significantly between approaches. Compile-time frameworks run annotation processors that add overhead to every build. For Hilt, this overhead can be substantial in large projects with many annotated classes. Koin requires no annotation processing, resulting in faster builds, particularly for incremental compilation where only changed code is recompiled.

Application startup performance favors compile-time approaches. Hilt's generated code executes directly without reflection or interpretation. Koin must build its dependency graph at runtime by executing the module definitions, adding some overhead to application launch. In practice, this difference is usually measured in milliseconds and is rarely noticeable to users, though it can be more significant in applications with very large dependency graphs.

## Hilt Fundamentals

Hilt simplifies dependency injection for Android applications by providing a standardized way to incorporate Dagger into Android projects. Setting up Hilt requires adding the Hilt Gradle plugin and dependencies, then annotating the Application class to enable injection.

The Application class annotated with HiltAndroidApp serves as the parent component for all other Hilt components in the application. This annotation triggers code generation that creates the root of the dependency graph. All application-wide singletons are managed through this component.

Modules in Hilt describe how to create dependencies that cannot be constructor-injected. When dealing with interfaces where the concrete implementation must be specified, or with classes from external libraries that cannot be annotated, modules provide the necessary instructions. A module is an object or class annotated with Module and InstallIn, specifying which component the module's bindings belong to.

The Provides annotation within modules tells Hilt how to create instances of types. Each method annotated with Provides returns an instance of a dependency. Hilt calls these methods when the corresponding type is needed. Methods can have parameters that are themselves injected, enabling composition of dependencies.

Constructor injection is the preferred method when you control the class being injected. By annotating a class constructor with Inject, Hilt understands how to create instances of that class. All constructor parameters must be types that Hilt knows how to provide, either through other Inject-annotated constructors or through module Provides methods.

ViewModels receive special treatment in Hilt through the HiltViewModel annotation. This annotation enables automatic ViewModel injection with proper scoping to the associated Activity or Fragment. The ViewModel's constructor can include injected dependencies, and Hilt handles the integration with ViewModel lifecycle management.

Activities and Fragments require the AndroidEntryPoint annotation to participate in injection. This annotation generates code that performs injection when the component is created. Without this annotation, attempts to inject dependencies into Activities or Fragments fail silently or with cryptic errors.

## Hilt Scopes and Components

Hilt provides predefined components corresponding to Android's lifecycle components, each with an associated scope that determines how long provided objects live.

SingletonComponent corresponds to the Application lifecycle. Objects scoped to this component exist as single instances throughout the entire application lifecycle. Network clients, databases, and other expensive resources that should be shared typically use this scope. The Singleton annotation marks types that should have only one instance in this component.

ActivityRetainedComponent survives configuration changes, matching ViewModel lifecycle. Objects scoped here persist across Activity recreation due to rotation or other configuration changes but are destroyed when the Activity is finished. This scope is useful for data that should survive configuration changes but is specific to a particular screen flow.

ViewModelComponent provides scope for objects tied to a specific ViewModel's lifecycle. This is useful for dependencies that should be unique per ViewModel instance but shared across components that use that ViewModel.

ActivityComponent and FragmentComponent provide shorter-lived scopes destroyed and recreated with their corresponding lifecycle components. These are appropriate for objects that should not survive configuration changes or that require fresh instances for each Activity or Fragment creation.

Choosing appropriate scopes prevents both memory leaks and incorrect sharing. Overusing singleton scope keeps objects in memory longer than necessary and can cause stale data issues. Underusing scope creates duplicate objects that waste memory and lose the benefit of shared state. The general principle is to scope objects at the narrowest level that still allows appropriate sharing.

## Hilt with Jetpack Compose

Compose integration with Hilt uses the hiltViewModel function to obtain ViewModels with injected dependencies. When navigating between composable destinations, each destination can obtain its own ViewModel scoped to its navigation back stack entry.

The hiltViewModel function creates or retrieves a ViewModel associated with the current composition context. The ViewModel's dependencies are automatically injected according to the Hilt configuration. This integration handles the complexity of ViewModel lifecycle management in Compose's declarative paradigm.

Shared ViewModels across multiple composables in a navigation flow use parent navigation graph scoping. By obtaining the ViewModel from a parent navigation entry rather than the immediate destination, multiple composables can share the same ViewModel instance. This enables multi-step flows where each step contributes to shared state.

Assisted injection addresses scenarios where ViewModels need runtime parameters not available from the dependency graph. Using the AssistedInject annotation and an associated factory interface, ViewModels can receive both injected dependencies and runtime parameters. This is particularly useful when navigation arguments need to be passed to ViewModels.

## Koin as an Alternative

Koin takes a fundamentally different approach to dependency injection, using Kotlin's language features to create a domain-specific language for defining dependencies. This approach prioritizes simplicity and readability over compile-time safety.

Module definitions in Koin use the module function with a lambda containing dependency declarations. The single function declares singleton instances, factory declares new instances for each request, and viewModel declares ViewModel instances with appropriate lifecycle management. Dependencies are resolved using the get function within these declarations.

Starting Koin requires calling startKoin in the Application class with the list of modules to load. This builds the dependency graph and makes it available throughout the application. The androidContext extension provides Android Context access within modules.

Injection in Activities, Fragments, and ViewModels uses delegation. The inject delegate lazily retrieves dependencies from the Koin container. The viewModel delegate retrieves ViewModel instances with proper lifecycle integration. These delegates provide concise syntax without requiring annotations or code generation.

Koin's advantages include simplicity of setup and understanding, faster build times due to lack of annotation processing, and full support for Kotlin Multiplatform. For teams that prioritize development velocity and are willing to rely on thorough testing to catch configuration errors, Koin provides an attractive option.

The tradeoff is runtime discovery of configuration errors. A missing dependency or type mismatch compiles successfully but crashes at runtime. Koin provides testing utilities to verify configuration, but these must be explicitly written and maintained. The koinApplication test helper can instantiate all dependencies to verify completeness, but this adds testing overhead.

## Manual Dependency Injection

For small projects or those with specific constraints, manual dependency injection remains a viable approach. This involves creating container classes that explicitly construct and provide dependencies without framework assistance.

A simple container class holds dependencies as properties, using lazy initialization to defer creation until needed. The container's constructor receives any external dependencies like Context. All other dependencies are constructed within the container using previously constructed dependencies.

The Application class instantiates and holds the container. Access to the container from Activities and Fragments goes through the Application, either via casting or extension functions. ViewModels receive dependencies through custom factory classes that extract them from the container.

Manual dependency injection provides complete transparency about how dependencies are created and wired. No annotation processing affects build time, and no framework-specific knowledge is required. However, as applications grow, maintaining the container becomes tedious, and the lack of automatic scope management requires careful attention to lifecycle issues.

## Testing with Dependency Injection

One of the primary motivations for dependency injection is enabling effective testing. Each approach to dependency injection provides different mechanisms for test configuration.

Unit tests for ViewModels and other classes should not require dependency injection frameworks at all. Because dependencies are passed through constructors, tests simply instantiate classes with mock or fake implementations. This approach provides the fastest tests and clearest control over test scenarios.

Hilt provides testing utilities for integration and instrumented tests. The HiltAndroidTest annotation enables Hilt in test classes, creating an appropriate dependency graph for testing. The TestInstallIn annotation allows replacing production modules with test modules that provide fake implementations. The UninstallModules annotation removes specific modules entirely, enabling BindValue to provide individual test doubles.

Koin testing uses the koinTestRule or manual startKoin calls within tests. Production modules can be supplemented or replaced with test modules providing different implementations. The checkModules function verifies that all dependencies can be resolved, catching configuration errors in test suites.

The general testing strategy maintains a distinction between unit tests that bypass frameworks entirely and integration tests that verify proper framework configuration. Unit tests should dominate, with framework-dependent tests reserved for verifying integration and configuration.

## Common Mistakes and Pitfalls

Several recurring mistakes cause problems in dependency injection implementations across all frameworks.

Overusing singleton scope creates problems when objects hold state that should not be shared or persist references that should be released. Not every dependency needs to be a singleton; most should use appropriate shorter scopes or no scope at all, creating new instances for each injection.

Circular dependencies occur when class A depends on class B and class B depends on class A. Compile-time frameworks detect these during compilation, while runtime frameworks may crash or behave unexpectedly. Resolution typically involves introducing a third class that breaks the cycle, or using lazy injection through Provider or Lazy wrappers.

Injecting Context incorrectly leads to memory leaks. Activity Context should rarely be injected because it ties the dependency's lifetime to a specific Activity. Application Context, obtained via ApplicationContext annotation in Hilt, is appropriate for long-lived dependencies. Short-lived dependencies scoped to Activities may use Activity Context if appropriate.

Missing annotations on Android entry points cause silent failures. Activities and Fragments must be annotated with AndroidEntryPoint for injection to occur. ViewModels must be annotated with HiltViewModel. Forgetting these annotations results in null injected fields or missing ViewModel instances.

Testing configuration separately from testing behavior ensures dependency graph correctness. A passing unit test with mocked dependencies does not verify that the production dependency graph is correctly configured. Dedicated configuration tests or integration tests that use the real graph catch configuration errors.

## Migration Strategies

Teams often need to migrate between dependency injection approaches as projects evolve or requirements change.

Migrating from Dagger to Hilt can be done incrementally. Hilt provides migration utilities that allow Dagger components to coexist with Hilt components. Individual screens or features can be migrated one at a time, with the full migration completed when all code uses Hilt patterns.

Migrating from manual injection to Hilt involves adding Hilt configuration, annotating existing classes with appropriate annotations, and gradually removing manual wiring code. The container classes can continue to exist during migration, with dependencies moved to Hilt modules over time.

Migrating from Koin to Hilt requires more substantial changes due to the different paradigms. Module definitions must be converted to annotated classes, delegation-based injection replaced with annotation-based injection, and testing approaches adapted. This migration typically involves touching most files that participate in injection.

The decision to migrate should consider the costs of transition against the benefits gained. A working dependency injection setup, even if not optimal, may not warrant the disruption of migration if the project is stable and the team is productive.

## Choosing Between Approaches

Selection criteria for dependency injection approaches depend on project characteristics and team preferences.

Project size influences the choice significantly. Small projects with limited dependency graphs may find manual injection sufficient or Koin's simplicity attractive. Large projects with complex graphs benefit from Hilt's compile-time safety and tooling support.

Kotlin Multiplatform requirements narrow the options. Hilt is Android-only, while Koin supports multiplatform projects. For shared code between Android and iOS, Koin provides a consistent approach across platforms.

Team experience affects adoption cost. Teams familiar with Dagger will find Hilt natural. Teams new to dependency injection may find Koin's DSL more approachable initially. The learning curve for proper understanding is similar across approaches, but initial productivity differs.

Testing culture matters because compile-time versus runtime error detection trades off against build time. Teams with comprehensive test suites that would catch Koin configuration errors experience fewer benefits from Hilt's compile-time checking. Teams relying more heavily on compilation for correctness gain more from Hilt.

## Relationship to Software Engineering Principles

Dependency injection embodies several fundamental software engineering principles.

Dependency Inversion Principle, the D in SOLID, states that high-level modules should not depend on low-level modules; both should depend on abstractions. Dependency injection enables this by allowing high-level classes to depend on interfaces while implementations are provided externally.

Inversion of Control describes the general principle where frameworks call application code rather than application code calling frameworks. Dependency injection inverts control of object creation, with the injection framework creating objects rather than objects creating their own dependencies.

Separation of Concerns is supported because classes focus on their primary responsibilities without also managing dependency creation. The responsibility for assembling the object graph is separated from the business logic those objects implement.

Single Responsibility Principle benefits because classes have fewer reasons to change when they do not contain dependency construction logic. Changes to how dependencies are created affect only configuration code, not the classes using those dependencies.

## Conclusion

Dependency injection has evolved from a nice-to-have practice to an essential component of modern Android development. The benefits for testing, maintainability, and flexibility compound as applications grow in complexity and team size.

Hilt represents the current state of the art for Android dependency injection, providing compile-time safety with dramatically reduced boilerplate compared to raw Dagger. Its deep integration with Android Jetpack makes it the natural choice for most Android applications.

Koin remains a viable alternative for teams prioritizing simplicity or requiring Kotlin Multiplatform support. Its runtime approach trades compile-time safety for reduced build overhead and syntactic simplicity.

Manual dependency injection should not be dismissed for appropriate use cases. Small projects, libraries that should minimize dependencies, and situations requiring complete transparency may benefit from manual approaches.

Regardless of the chosen approach, the underlying principle remains constant: classes should receive their dependencies rather than creating them. This simple inversion unlocks testing capabilities, enables flexibility, and improves code organization. Understanding why dependency injection matters is more important than mastering any particular framework, as frameworks evolve but principles endure.
