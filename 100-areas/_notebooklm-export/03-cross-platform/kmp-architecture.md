# Clean Architecture for Kotlin Multiplatform

Organizing code in Kotlin Multiplatform projects requires thoughtful architecture that separates concerns appropriately for code sharing. Clean Architecture principles, adapted for KMP's unique requirements, provide a foundation for maintainable cross-platform codebases. The key insight is that different architectural layers have different sharing potential, and organizing code to reflect this enables maximum sharing where beneficial while preserving platform-specific capabilities where needed.

## Architectural Goals for KMP

KMP architecture serves multiple goals that sometimes tension against each other. Understanding these goals helps make appropriate trade-offs.

Maximizing code sharing reduces development effort and ensures consistent behavior across platforms. Logic implemented once in shared code does not need separate iOS and Android implementations. This is the primary motivation for using KMP.

Maintaining platform fidelity ensures that platform-specific code can leverage platform capabilities fully. iOS code should feel like iOS code. Android code should feel like Android code. Forcing everything into shared abstractions can sacrifice platform-appropriate patterns.

Enabling testability ensures that shared code can be tested independently from platform code. Unit tests in shared code run quickly without emulators or devices. This fast feedback loop accelerates development.

Supporting team workflows enables developers with different platform expertise to contribute effectively. iOS developers should be able to work on iOS code. Android developers should be able to work on Android code. Shared code developers should be able to work without deep platform expertise.

Clean Architecture addresses these goals through layered separation. Inner layers contain platform-independent business logic with maximum sharing potential. Outer layers contain platform-specific code with minimum sharing. Dependencies point inward, with shared layers not knowing about platform layers.

## Layer Structure for KMP

Clean Architecture traditionally defines layers including entities, use cases, interface adapters, and frameworks. Adapting this for KMP involves mapping layers to source sets with appropriate sharing.

The domain layer contains business entities, business rules, and use case definitions. This layer has no dependencies on external frameworks, databases, or UI. In KMP, the domain layer lives entirely in commonMain. It uses only Kotlin standard library and potentially other pure-Kotlin libraries. This layer has maximum sharing.

Entities represent core business objects. A User entity, a Product entity, a Transaction entity. These are data classes with validation logic and business methods. They do not know how they are stored or displayed.

Use cases encapsulate business operations. A LoginUseCase, a PlaceOrderUseCase, a FetchRecommendationsUseCase. They orchestrate entities and define business workflows. They declare dependencies on repositories and services as interfaces.

The data layer contains repository implementations, data sources, and network clients. Parts of this layer can be shared, particularly repository logic and data transformation. Parts may require platform-specific implementation for database access or platform API integration.

Repository implementations coordinate data sources and transform data to domain entities. These implementations often live in commonMain, depending on abstracted data sources that have platform-specific implementations.

Data sources access actual storage and network. Network data sources using Ktor or similar multiplatform libraries can be shared. Database data sources using SQLDelight can be largely shared. Platform-specific data sources for keychain, shared preferences, or platform APIs live in platform source sets.

The presentation layer contains UI logic and view models. With shared UI through Compose Multiplatform, this layer can be largely shared. With native UI, this layer may be partially shared through shared view models or largely platform-specific.

View models hold UI state and handle UI events. They depend on use cases for business operations. In shared architectures, view models live in commonMain and expose state through StateFlow or similar observable types.

## Dependency Flow and Inversion

Clean Architecture's dependency rule states that dependencies point inward. Outer layers depend on inner layers, never the reverse. This rule enables the inner layers to be shared without knowing about platform-specific outer layers.

The domain layer has no outward dependencies. It defines interfaces for what it needs. Repository interfaces declare methods for data access. Service interfaces declare methods for platform capabilities. The domain layer does not implement these interfaces.

The data layer depends inward on domain interfaces and implements them. A repository interface defined in domain has an implementation in data. The implementation uses whatever data sources are appropriate. The domain does not know or care about implementation details.

Dependency injection connects implementations to interfaces. A DI framework or manual injection provides implementations at runtime. Shared code receives implementations through constructor injection. Platform code provides the actual implementations.

This inversion enables testing. Tests provide mock or fake implementations of interfaces. Domain logic can be tested with fake repositories that return test data. Data layer logic can be tested with fake data sources. The layers are decoupled enough for isolated testing.

## Repository Pattern in KMP

Repositories mediate between domain and data layers, and their structure significantly impacts sharing in KMP.

A repository interface lives in domain. It declares methods like getUser, saveUser, observeUsers. The interface uses domain types. Return types are domain entities or flows of domain entities. The interface knows nothing about storage mechanisms.

Repository implementation lives in data and implements the interface. It coordinates data sources, handles caching, and transforms data types. The implementation depends on data source interfaces for actual access.

Data source interfaces in the data layer declare platform-independent access patterns. A LocalDataSource might declare methods for local storage. A RemoteDataSource might declare methods for network access. These interfaces use data layer types.

Data source implementations may be shared or platform-specific. A RemoteDataSource using Ktor can be shared entirely. A LocalDataSource using SQLDelight can be largely shared. A SecureStorageDataSource using Keychain or EncryptedSharedPreferences needs platform-specific implementations.

For platform-specific data sources, expect/actual provides the mechanism. An expected interface or factory in commonMain has actual implementations in platform source sets. The repository uses the expected type, receiving the platform-appropriate implementation at runtime.

## State Management Architecture

State management patterns must work across platforms, which affects architectural choices.

Unidirectional data flow provides a predictable state management pattern. Actions flow in one direction. State flows in one direction. UI observes state and dispatches actions. This pattern works well across platforms.

StateFlow provides the reactive state container. A StateFlow holds current state and emits updates. UI layers observe the flow and update when state changes. Android UI collects the flow directly. iOS UI bridges to Combine or uses SKIE's async sequence transformation.

Mutable state stays private within view models or stores. Only the view model can modify the MutableStateFlow. External code receives read-only StateFlow. This encapsulation prevents scattered state mutation.

Reducers transform state in response to actions. A reduce function takes current state and action, returning new state. This pure function is easily tested. The view model dispatches actions to the reducer and updates state with results.

Side effects for asynchronous operations integrate with the state flow. An action triggers a side effect like a network call. The side effect dispatches result actions that update state. The separation keeps the reducer pure while enabling async operations.

Redux-like patterns fit KMP well because they structure state management around pure functions that transform data. These functions live entirely in shared code. Only the observation mechanism differs between platforms.

## Navigation Architecture

Navigation presents architectural challenges because platform navigation systems differ significantly. Several approaches work for KMP navigation.

Shared navigation state with platform rendering separates what from how. Shared code maintains a navigation stack or graph as state. Platform code observes this state and renders appropriate screens using platform navigation primitives. Changes to shared state trigger navigation on each platform.

Decompose provides a component-based navigation approach. Components hold state and define child components. The component tree represents navigation state. Platform code renders the component tree using platform UI. Navigation actions modify the component tree.

Voyager provides simpler screen-based navigation for Compose Multiplatform. Screens are composable classes that can be pushed and popped. Navigation state is managed by the Navigator. This works across Compose targets but not for native UI.

Platform navigation with shared view models keeps navigation in platform code while sharing the logic within screens. Each platform uses its native navigation. Shared view models power individual screens. Deep linking and complex navigation flows require platform implementation.

The choice depends on whether UI is shared. Compose Multiplatform projects can share navigation through multiplatform navigation libraries. Native UI projects typically keep navigation in platform code.

## Dependency Injection Strategies

Dependency injection enables loose coupling and testability. KMP projects need DI that works across platforms.

Manual dependency injection through constructor injection works everywhere. Classes receive dependencies through constructors. A composition root creates instances with dependencies. This approach has no framework overhead and works identically on all platforms.

Factory patterns provide instance creation. Factories create fully-configured instances. Platform-specific factories create platform-specific implementations. Shared factories create shared implementations. The factory abstraction hides creation details.

Koin provides a multiplatform DI framework. Modules define how to create instances. The container resolves dependencies at runtime. Koin works in shared code and across platforms.

Kodein also provides multiplatform DI with a different API style. Both Koin and Kodein enable defining shared modules in commonMain with platform-specific additions in platform source sets.

The DI approach should match team familiarity and project needs. Manual injection is simple but requires more boilerplate. Framework injection reduces boilerplate but adds dependencies.

## Error Handling Architecture

Errors must flow through the architecture in a way that works across platforms.

Domain errors represent business-level failures. An InsufficientFundsError, an ItemNotFoundError, a ValidationError. These are defined in the domain layer and used throughout shared code.

Result types wrap success or failure explicitly. A Result or Either type makes potential failure explicit in return types. Callers must handle both cases. This catches error handling omissions at compile time.

Kotlin's Result type works but has limitations for custom error types. The kotlin-result library provides Either-like types with custom error types. Arrow's Either provides similar capability with more functional programming features.

Exceptions remain an option. Kotlin supports exceptions that propagate through call stacks. Exception handling is familiar to many developers. However, unchecked exceptions can be missed, causing runtime failures.

The architectural choice between result types and exceptions affects how errors flow through layers. Result types make errors explicit at every boundary. Exceptions flow implicitly until caught. KMP projects can use either consistently.

Platform error mapping at boundaries translates between error representations. Swift code might expect different error types than Kotlin provides. The boundary layer maps errors appropriately. SKIE helps by mapping exceptions to Swift errors.

## Testing Architecture

Test architecture enables verifying each layer independently.

Domain layer tests verify business logic with fake dependencies. Use cases receive fake repositories that return test data. Tests verify correct orchestration and business rules.

Data layer tests verify data transformation and coordination. Repositories receive fake data sources. Tests verify correct data source coordination and transformation.

Integration tests verify boundaries between layers and platforms. Tests that exercise the full path from API call through repository to domain verify correct integration.

Platform tests verify platform-specific implementations. iOS tests verify iOS actual implementations. Android tests verify Android actual implementations. These tests may require device or simulator.

Shared tests in commonTest run on all platforms, verifying shared code works everywhere. Platform tests in androidTest and iosTest verify platform-specific code.

Test doubles including fakes, stubs, and mocks enable isolated testing. Interfaces defined for dependencies enable providing test implementations. Shared test doubles in common test source sets can be used across platform tests.

## Practical Module Organization

Real KMP projects organize code into Gradle modules that reflect architectural layers.

A domain module contains domain layer code in commonMain only. It has no platform source sets because domain is entirely shared. Dependencies are minimal, perhaps only Kotlin standard library and serialization for data classes.

A data module contains data layer code. CommonMain holds repository implementations and data source interfaces. Platform source sets hold platform-specific data source implementations. Dependencies include network libraries, database libraries, and domain module.

A feature module contains presentation layer code for a feature. For shared UI, commonMain holds view models and composables. For native UI, commonMain might hold only view models. Platform source sets hold platform-specific UI code.

An app module for each platform composes other modules into applications. The Android app module creates the Android application. The iOS framework module creates the iOS framework. These modules perform DI composition and application bootstrap.

This modular structure enforces dependency direction through Gradle. Inner modules do not depend on outer modules. Build configuration prevents improper dependencies.

## Evolution and Migration

Architecture should support evolution as projects grow and requirements change.

Starting small with minimal layers works for initial development. As complexity grows, more explicit layering provides structure. Premature architecture adds overhead without benefit. Appropriate architecture grows with demonstrated need.

Migrating existing projects to KMP often proceeds incrementally. Extract shared logic first, keeping UI platform-specific. Add shared data layer next. Consider shared UI later if appropriate. Each step provides value without requiring complete conversion.

Adding platforms later should be possible. Architecture that works for Android and iOS should extend to desktop or web. Platform-agnostic shared layers ease adding targets.

## Conclusion

Clean Architecture adapted for KMP organizes code to maximize sharing in inner layers while preserving platform capabilities in outer layers. The domain layer shares completely. The data layer shares substantially with platform-specific data sources. The presentation layer shares according to UI strategy.

Dependency inversion keeps shared layers platform-agnostic. Interfaces define contracts that platform code fulfills. Dependency injection provides implementations at runtime. This structure enables testing shared code with fakes and testing platform code with real implementations.

The specific architecture for any project depends on project scope, team composition, and sharing strategy. Clean Architecture principles provide guidance adaptable to specific needs. The goal is maintainable code that shares effectively while preserving platform appropriateness.

KMP's flexibility enables various architectural approaches. Teams should choose architecture that serves their specific situation rather than following prescriptions blindly. Understanding architectural principles enables making appropriate choices as projects evolve.
