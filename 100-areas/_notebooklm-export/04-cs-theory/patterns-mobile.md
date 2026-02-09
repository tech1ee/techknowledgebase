# Mobile Architecture Patterns: Structuring Applications for Scale and Maintainability

Mobile application development has matured significantly since the early days of smartphones. What once were simple utilities have evolved into sophisticated applications with complex business logic, multiple data sources, intricate navigation flows, and demanding user expectations. This evolution has driven the adoption of architectural patterns that help manage complexity, enable testing, and support team collaboration.

The patterns explored here—Repository, Coordinator/Navigator, Dependency Injection containers, and UseCase/Interactor—address recurring challenges in mobile development. They help separate concerns, define clear boundaries between components, and create code that remains maintainable as applications grow.

## The Repository Pattern: Abstracting Data Access

The Repository pattern mediates between the domain layer and data mapping layers, acting as an in-memory collection of domain objects. It provides a clean abstraction over data persistence and retrieval, allowing business logic to work with domain objects without concerning itself with how those objects are stored or retrieved.

### The Data Access Problem

Mobile applications consume data from diverse sources: local databases for offline capability, remote APIs for fresh content, caches for performance, files for user documents, and system services for device information. Each data source has its own access patterns, error conditions, and performance characteristics. Direct access from business logic to these varied sources creates coupling that makes code difficult to test, change, and understand.

Consider a social media app displaying a user's feed. The feed might come from a remote API, but for offline support and performance, recently viewed items should be cached locally. The decision of when to fetch fresh data versus serving cached data involves network status, cache age, user scroll position, and business rules about freshness. If this logic lives in the UI layer alongside display code, the code becomes tangled and untestable.

### How Repository Provides Abstraction

A Repository presents a simple, collection-like interface for accessing domain objects. The feed repository might offer methods to get recent items, refresh from the network, and search by criteria. Clients call these methods without knowing whether data comes from cache, network, or a combination.

Inside the repository, the complexity lives in isolation. The repository checks cache freshness. It decides whether to request from the network. It manages cache updates when fresh data arrives. It handles network errors gracefully, perhaps serving stale data with a freshness warning. It coordinates concurrent requests to avoid redundant network calls. All this complexity is encapsulated; clients see only a clean interface.

### Repository Benefits for Testing

Repositories dramatically improve testability. Business logic that depends on a repository can be tested with a mock repository that returns controlled data. You don't need a real database, network connection, or complex setup. The mock repository returns exactly the data needed for each test case.

This isolation makes tests fast, reliable, and focused. Network test failures don't break business logic tests. Database schema changes don't affect UI tests. Each layer tests against its dependencies' interfaces, not their implementations.

### Repository Implementation Patterns

Repositories commonly compose multiple data sources. A single repository might combine a local data source (database, file, preferences) with a remote data source (API client). The repository's strategy coordinates these sources: read from local first, fall back to remote, update local after remote fetch, invalidate local when stale.

Reactive repositories expose data as observable streams rather than single values. Clients subscribe to the stream; when data changes, they receive updates automatically. This fits naturally with mobile UI frameworks that need to refresh displays when underlying data changes. The repository handles the complexity of merging data source changes into a coherent stream.

Some repositories implement the specification pattern, accepting query specifications that describe what data to retrieve. This provides flexibility without a proliferation of specialized query methods. Rather than getUsersByStatus and getUsersByRole and getUsersByStatusAndRole, the repository takes a specification that encapsulates the query criteria.

### Repository Boundaries and Responsibilities

Repository boundaries require careful consideration. Too fine-grained repositories (one per entity) create choreography complexity when operations span entities. Too coarse-grained repositories (one per feature) become bloated and unfocused. A good heuristic is one repository per aggregate root—a cluster of related entities that form a consistency boundary.

Repositories should not contain business logic. They translate between domain objects and persistence representations, manage caching and synchronization, and handle data source errors. Business decisions about what data means and how to act on it belong in the domain layer, not the repository.

### Caching Strategies in Repositories

Caching is often a repository responsibility, and cache strategy significantly affects app behavior. Time-based expiration marks cached data as stale after a period, triggering refresh on next access. This simple strategy works for slowly-changing data but can serve stale data immediately after changes or waste bandwidth refreshing rarely-used data.

Event-based invalidation clears or updates cache in response to events. When a user posts new content, invalidate their cached feed. When push notification announces new messages, refresh the message cache. This provides fresher data but requires event infrastructure and careful coordination.

Stale-while-revalidate serves cached data immediately while fetching fresh data in the background. Users see instant results; if fresh data differs, the UI updates. This provides the best perceived performance but requires handling the update case gracefully.

Cache-first with network fallback prioritizes offline capability. The app functions from cache even when offline; network access updates the cache when available. Conflict resolution handles cases where local and remote data diverge.

## The Coordinator Pattern: Managing Navigation Complexity

The Coordinator pattern (sometimes called Navigator or Flow Controller) extracts navigation logic from view controllers and view models, centralizing navigation decisions in dedicated coordinator objects. This separation clarifies responsibilities, improves testability, and manages complex navigation flows more effectively.

### The Navigation Complexity Problem

Mobile apps have rich navigation patterns: tab bars, navigation stacks, modal presentations, deep links, push notification routes, and authentication flows. Navigation involves not just transitioning between screens but also passing data, managing backstack state, handling deep links that jump into the middle of flows, and coordinating multi-step processes.

When view controllers handle their own navigation, several problems emerge. Navigation logic duplicates across controllers—multiple places might navigate to the user profile, each recreating the same setup. Controllers become coupled to their destinations—a screen must know how to create and configure the screens it navigates to. Testing navigation requires instantiating entire view controller hierarchies.

Complex flows become particularly problematic. A checkout flow might involve address selection, payment method, review, and confirmation, with branches for adding addresses or payment methods. Without coordination, each screen manages its piece of the flow, making the overall flow hard to understand and modify.

### How Coordinators Manage Navigation

A Coordinator owns a portion of an app's navigation flow. It creates and configures the screens in its flow, responds to navigation events from those screens, and decides what happens next. Screens delegate navigation decisions to their coordinator rather than navigating directly.

The checkout coordinator creates the checkout flow's screens. When the address screen signals completion, the coordinator decides to show payment. When payment signals completion, the coordinator shows review. If the user backs out, the coordinator manages the backtrack. The screens know nothing about each other; they only communicate with their coordinator.

This centralization clarifies flow logic. The checkout flow is defined in one place—the checkout coordinator—not scattered across multiple screens. Changing the flow (adding a step, reordering screens, adding a branch) happens in the coordinator without touching individual screens.

### Coordinator Hierarchies

Apps often have hierarchies of coordinators. An app coordinator manages top-level flow: showing authentication if needed, switching between main tabs, handling universal links. Each main area might have its own coordinator: a feed coordinator, profile coordinator, settings coordinator. These child coordinators manage their areas' internal flows.

This hierarchy matches user mental models. Users understand they're "in" the settings area or "going through" checkout. Coordinators make this structure explicit in code.

Parent coordinators often start child coordinators for subflows. The main coordinator starts the checkout coordinator when the user initiates purchase. When checkout completes or cancels, it returns control to the main coordinator. This delegation keeps each coordinator focused on one coherent flow.

### Coordinator Implementation Approaches

Coordinators can be implemented in various ways depending on platform and preference. Some approaches use coordinator protocols that screens delegate to. The screen holds a weak reference to its coordinator and calls delegate methods for navigation events: userDidTapCheckout, userDidCompleteProfile. The coordinator implements these methods with navigation responses.

Other approaches use closures or callbacks. The screen receives a closure to call when navigation is needed. This avoids protocol ceremony but can create retain cycle concerns and less explicit contracts.

Some frameworks provide routing abstractions that coordinators implement. The coordinator declares the routes it handles; the framework delivers navigation requests to the appropriate coordinator.

### Handling Deep Links and Push Notifications

Coordinators excel at handling deep links and push notifications—navigation requests that arrive from outside the normal UI flow. A deep link to a specific product must navigate to that product regardless of current app state. This might require dismissing modals, switching tabs, pushing navigation controllers, and finally showing the product.

A coordinator-based architecture handles this cleanly. The deep link arrives at a top-level coordinator that parses the link type. It determines which child coordinator handles that destination. It ensures the correct navigation context (correct tab, no blocking modals) and tells the child coordinator to navigate to the specific destination. The child coordinator pushes the appropriate screen with the appropriate data.

Without coordinators, deep link handling becomes a maze of conditionals checking current state and manipulating various navigation controllers. With coordinators, each one handles deep links in its domain, and the hierarchy routes requests appropriately.

## Dependency Injection Containers: Managing Object Graphs

Dependency Injection (DI) is the practice of providing a component's dependencies from outside rather than having the component create them internally. A DI Container (or service locator, or IoC container) automates dependency management, creating object graphs with resolved dependencies and managing object lifecycles.

### The Dependency Problem

Real applications have complex dependency graphs. A view model might depend on a use case, which depends on a repository, which depends on a database and an API client, which depend on network configuration and authentication. Creating a view model means creating this entire chain—and ensuring shared resources (like the API client) are actually shared rather than duplicated.

Without systematic dependency management, construction code becomes verbose and scattered. Every place that creates a view model must know how to create use cases, repositories, and clients. Changes ripple through construction sites; adding a dependency to the repository affects every place that creates objects depending on it.

Testing suffers particularly. To test a view model with a mock repository, you must control how the view model gets its repository. If the view model creates its repository internally, mocking is impossible without modifying production code.

### How DI Containers Manage Dependencies

A DI container registers how to create instances of various types and resolves requests for those types by creating instances with their dependencies satisfied. You register that Repository is implemented by DefaultRepository, which needs a Database and an ApiClient. You register that ApiClient needs NetworkConfiguration and AuthProvider. When you request a Repository, the container creates the full dependency chain.

Containers typically support various lifecycles. Singleton scope creates one instance and reuses it for all requests—appropriate for shared resources like API clients. Transient scope creates a new instance for each request—appropriate for stateful objects that shouldn't be shared. Custom scopes support per-screen or per-flow lifecycles.

### Constructor Injection vs. Other Approaches

Constructor injection provides dependencies through the constructor. A view model's constructor declares the use cases and services it needs; the container provides them when creating the view model. This makes dependencies explicit—the constructor signature documents what the object needs—and ensures objects are fully initialized upon creation.

Property injection sets dependencies through writable properties after construction. This allows optional dependencies and can break circular dependency chains but makes dependencies less obvious and allows partially-initialized objects.

Method injection provides dependencies through method parameters when invoking specific methods. This works for dependencies needed only for particular operations but disperses dependency declaration.

Constructor injection is generally preferred for its explicitness and guarantees about initialization. The constructor signature becomes documentation of the object's needs.

### Container Registration Patterns

Small apps might register each type explicitly: register Repository as DefaultRepository, register ApiClient as DefaultApiClient. Larger apps often use conventions or scanning: register all classes implementing Repository interface, register all classes matching UseCase naming pattern.

Modules group related registrations. A NetworkModule registers API clients, interceptors, and serializers. A DatabaseModule registers database, migrations, and DAOs. Modules can be swapped for testing—the TestNetworkModule provides mock implementations—or for different configurations.

Frameworks often integrate with DI containers, automatically resolving dependencies for view controllers, view models, or other framework-managed objects. This reduces boilerplate but requires understanding the framework's resolution rules.

### Container Considerations

Containers introduce indirection that can obscure object relationships. Tracing how objects are created requires understanding the container's registration and resolution rules, not just reading construction code. This tradeoff favors automation over explicitness.

Overuse of containers can hide design problems. If an object has twenty dependencies resolved by the container, the container makes this manageable, but the fundamental problem—an object with too many responsibilities—remains. Containers should serve good design, not mask bad design.

Service locator patterns, where objects request dependencies from a global container rather than receiving them through constructors, share some container benefits but reintroduce hidden dependencies. The object's interface doesn't reveal what it needs; it secretly fetches dependencies. Constructor injection keeps dependencies visible.

## UseCase and Interactor Patterns: Encapsulating Business Logic

The UseCase pattern (also called Interactor) encapsulates application-specific business logic in focused, testable units. Each use case represents a single action the user can perform, containing the logic for that action independent of UI concerns or data access details.

### The Business Logic Distribution Problem

In naive architectures, business logic spreads across layers. View models contain validation logic, calculation logic, and coordination between multiple data operations. Controllers handle error mapping and response formatting. Repositories implement filtering and business rules alongside data access.

This distribution creates several problems. Understanding how a feature works requires reading code across multiple files and layers. Testing business logic requires setting up UI or database contexts. Reusing logic across different UI presentations requires duplication. Changes to business rules affect multiple layers.

### How UseCases Centralize Logic

A UseCase encapsulates one user action with all its business logic. A PlaceOrderUseCase handles everything involved in placing an order: validating the order, checking inventory, calculating prices, applying discounts, processing payment, creating the order record, and triggering confirmations. It receives input, performs the action, and returns output.

UseCases depend on repositories and services but not on UI. They receive plain data objects, not view-specific models. They return results without knowing how results will be displayed. This independence means the same use case serves different UI presentations—mobile, tablet, watch—without modification.

### UseCase Input and Output

UseCases typically define explicit input and output types. The input is a simple data object containing the information needed to perform the action—perhaps an order request with items, shipping address, and payment information. The output is a result indicating success with relevant data or failure with error information.

This explicit contract makes use cases self-documenting. The input type declares what information the action needs. The output type declares what results it produces. Callers understand the use case through these types without reading implementation details.

### UseCase Composition and Orchestration

Complex operations often compose multiple use cases. A checkout flow might orchestrate ValidateCartUseCase, CalculateTotalsUseCase, ProcessPaymentUseCase, and CreateOrderUseCase. This orchestration might live in a higher-level use case or in a coordinator that manages the flow.

Composition keeps individual use cases focused while enabling complex behaviors. Each use case is simple to understand and test. Their composition creates sophisticated processes from simple building blocks.

### Testing UseCases

UseCases are among the most testable components in a mobile architecture. They have explicit inputs and outputs. Their dependencies (repositories, services) are injected and easily mocked. They contain no UI or framework dependencies that complicate test setup.

A typical use case test creates mock dependencies, instantiates the use case with those mocks, invokes the use case with test input, and verifies the output and mock interactions. Tests run fast, require no device or simulator, and cover business logic thoroughly.

This testability provides confidence in business rules. When validation logic lives in a well-tested use case, you trust that validation works correctly. Changes to validation have clear test coverage to verify correctness.

### UseCase Error Handling

UseCases often return Result types that explicitly represent success or failure. Callers handle results without catching exceptions, making error handling visible in code flow. Different error types allow different handling: validation errors might highlight fields; network errors might offer retry; business rule violations might explain requirements.

This explicit error handling contrasts with exception-based approaches where errors propagate invisibly and handling happens (or doesn't) at arbitrary catch sites. Use case results make error cases as visible and handled as success cases.

## Combining Mobile Patterns

These patterns work together to create coherent mobile architectures. Repositories abstract data access, providing clean interfaces for use cases. Use cases encapsulate business logic, orchestrating repository calls and business rules. View models call use cases to perform actions, transforming results for display. Coordinators manage navigation between screens, receiving signals from view models about navigation needs. DI containers wire everything together, managing the complex dependency graph.

Consider a user tapping a "Purchase" button. The view model calls the PurchaseUseCase, which validates the purchase through a ValidationService, checks inventory through an InventoryRepository, processes payment through a PaymentService, and creates an order through an OrderRepository. Each dependency was injected by the DI container. The use case returns a Result; on success, the view model tells its coordinator to navigate to the confirmation screen.

This flow separates concerns cleanly. The button tap handler knows only to call the view model. The view model knows only to invoke the use case and handle results. The use case knows business logic without knowing UI. The repositories know data access without knowing business rules. The coordinator knows navigation without knowing purchase logic.

### Architecture is Not One-Size-Fits-All

These patterns provide tools, not mandates. A simple utility app might not need coordinators—direct navigation suffices. A data-light app might not need repositories—direct API calls work fine. A small team building a focused app might find elaborate architectures impose unnecessary overhead.

Architecture should match project needs: team size, application complexity, expected lifespan, testing requirements, and development pace. Start simpler than you think you need; add structure as complexity demands it. Over-architecture is as problematic as under-architecture.

The patterns presented here have proven valuable across many mobile projects. Understanding them equips you to recognize when they apply and implement them effectively when they do. They're vocabulary for discussing architecture and options for addressing complexity. Use them thoughtfully, adapting them to your context, and they'll help you build mobile applications that remain maintainable as they grow.

## Advanced Repository Patterns

Single source of truth repositories establish definitive data authority. Rather than multiple components each maintaining their own copies of data, the repository serves as the authoritative source. All reads come from the repository; all updates go through it. This prevents data inconsistencies where different parts of the app show different values for the same data.

The single source of truth typically combines with reactive streams. The repository exposes observable data flows; UI components subscribe and automatically update when data changes. Updates flow into the repository, which updates its authoritative store and emits new values to all subscribers.

Repository-mediated synchronization handles the complexity of keeping local and remote data consistent. When the app modifies data locally, the repository queues the change for remote sync. When network becomes available, it uploads pending changes. Conflicts—where local and remote changes clash—resolve through repository-defined rules: last-write-wins, server-wins, merge, or user-prompted resolution.

Pagination support in repositories manages large data sets. Rather than loading thousands of items at once, the repository provides paginated access—first page, next page, previous page. It might cache multiple pages locally while presenting a seamless scrolling experience to the UI. The pagination logic stays in the repository; UI components simply request more data as needed.

Search and filtering in repositories balance flexibility with simplicity. A search method might accept a query string and return matching items. More sophisticated repositories accept specification objects that describe complex filter criteria. The repository translates these specifications into appropriate queries for its data sources.

Data freshness tracking helps repositories make intelligent decisions. Each cached item might have a timestamp indicating when it was fetched. The repository uses these timestamps to decide whether to serve cached data or fetch fresh data. Freshness rules can be global (refresh anything older than ten minutes) or per-item (user profile caches longer than feed items).

## Coordinator Pattern: Advanced Navigation Scenarios

State restoration with coordinators preserves navigation state across app launches. When the app terminates, each coordinator serializes its state—current screen, screen parameters, child coordinators. On relaunch, the coordinator hierarchy rebuilds from serialized state, restoring the user to their previous position.

Animation coordination handles transitions between screens. Simple navigation might use platform defaults, but sophisticated apps customize transitions based on context. The coordinator decides which animation to use: a card detail might expand from the tapped card; a modal might slide up from the bottom; a cross-dissolve might connect related screens.

Coordinator communication handles data and events flowing between coordinators. A child coordinator might need to inform its parent when the user completes a flow and what result they achieved. Parent coordinators might need to pass context to children when starting them. Clear protocols for this communication prevent tight coupling while enabling necessary coordination.

Branching flows require coordinators to manage conditional paths. A checkout coordinator might branch to address entry if the user lacks saved addresses, branch to payment method entry if they lack saved cards, or proceed directly if everything is ready. The coordinator tracks which branches have been taken and manages returns from branches.

Overlay and popup coordination handles UI elements that appear over current content without replacing it. A coordinator might present an action sheet, handle the user's selection, and continue the flow. Modal presentations, bottom sheets, and floating panels all need coordination to appear, gather input, and dismiss appropriately.

Tab-based navigation with coordinators requires each tab to have its own coordinator managing its navigation stack. A parent tab coordinator manages switching between tabs and handling cross-tab navigation requests. Deep links might need to switch tabs before navigating within the target tab.

## Dependency Injection: Implementation Depth

Lazy initialization in DI containers defers object creation until first use. Rather than creating all registered objects at startup, the container creates them on demand. This improves startup time and avoids creating objects that might never be used in a particular session.

Scoped lifetimes beyond singleton and transient support specialized needs. A per-request scope creates a new instance for each request but shares it within that request. A per-session scope creates instances that last for a user session. Custom scopes align object lifetimes with application concepts.

Child containers support hierarchical scopes. A request container might be a child of the application container, inheriting application-scoped registrations while adding request-scoped ones. When the request completes, the child container disposes, cleaning up request-scoped objects while application-scoped objects persist.

Automatic disposal with containers cleans up resources when objects leave scope. Objects implementing disposal interfaces get disposed when their containing scope ends. This provides automatic resource management without manual tracking.

Compile-time DI verifies dependency graphs during compilation rather than at runtime. Missing registrations become compile errors rather than runtime crashes. This catches configuration mistakes earlier and provides better IDE support. Some mobile platforms provide compile-time DI frameworks that generate the dependency resolution code.

Property wrappers and annotations simplify injection syntax. Rather than explicit constructor parameters, dependencies might be marked with annotations that the framework interprets. The container inspects annotations and injects appropriate values. This reduces boilerplate but obscures the dependency list.

Testing with DI involves swapping real implementations for test doubles. Test modules register mock implementations; the test creates a container with test modules; test code receives mock dependencies automatically. This systematic mocking makes test setup consistent and comprehensive.

## UseCase Patterns: Architectural Integration

Reactive UseCases expose their results as observable streams rather than single values. A fetch-user use case might return a stream that first emits cached data, then emits fresh data when network response arrives. Subscribers receive both emissions, allowing UI to show cached data immediately then update.

Parameterized UseCases accept configuration that affects behavior. A search use case might accept minimum result count, search timeout, and whether to include archived items. Parameters allow flexible reuse without proliferating similar use cases.

UseCase isolation ensures each use case operates independently. One use case should not directly call another; if coordination is needed, a higher-level component (another use case or a coordinator) manages it. This isolation keeps use cases focused and independently testable.

Background execution support allows long-running use cases to continue after the user leaves the triggering screen. A file upload use case might run in the background, updating its state in the repository. When the user returns to relevant UI, they see the current upload status from the repository.

Progress reporting from use cases informs callers about long-running operation status. A download use case might emit progress updates indicating bytes downloaded, total bytes, and estimated time remaining. UI components subscribe to progress and display appropriate indicators.

Cancellation support allows use cases to abort gracefully when results are no longer needed. If the user navigates away from a screen, pending use cases for that screen can be cancelled, freeing resources and preventing unnecessary work.

UseCase factories create use cases with appropriate configuration. Rather than each call site knowing how to create and configure a use case, a factory encapsulates this. The factory itself might receive dependencies from the DI container.

## MVVM and Related View Model Patterns

View models in mobile architecture serve as the UI's direct collaborator. They expose data for the UI to display and accept user actions, delegating to use cases for business logic. This separation keeps UI components focused on display while view models handle state and coordination.

State management in view models determines how UI state is represented and updated. Some view models expose individual observable properties; changes to any property update the UI. Others expose a single state object; any change replaces the entire state. The single-state approach simplifies reasoning about state but requires immutable state objects.

Input validation in view models provides immediate feedback on user input. As the user types, the view model validates and exposes validation state. The UI displays validation errors without waiting for form submission. This responsive validation improves user experience.

Loading and error states in view models represent asynchronous operation status. A view model might expose a state that is loading, loaded with data, or error with message. The UI observes this state and displays appropriate content: loading indicators, data displays, or error messages with retry options.

View model lifecycle ties to screen lifecycle. When a screen appears, its view model activates, potentially loading data. When the screen disappears, the view model might pause observations or cancel pending operations. This lifecycle management prevents resource waste and stale updates.

View model testing verifies state management and use case coordination. Tests provide mock use cases, invoke view model actions, and verify state changes and use case calls. This testing covers the UI's brain without requiring UI automation.

## Platform-Specific Considerations

Android-specific patterns address Android's unique lifecycle challenges. Activities and Fragments can be destroyed and recreated; view models must survive these configuration changes. Android's ViewModel class provides this survival mechanism; architectural view models should extend it or work with it.

Android's navigation component provides framework support for coordinator-like navigation. Navigation graphs define destinations and transitions; the framework handles backstack management. Custom navigation controllers integrate architectural patterns with framework navigation.

iOS-specific patterns work with UIKit or SwiftUI paradigms. UIKit view controllers require manual lifecycle coordination; SwiftUI views are more declarative. Coordinators adapt to these differences, using navigation controllers with UIKit or NavigationStack with SwiftUI.

SwiftUI's declarative nature changes how view models expose state. Observable objects and published properties create reactive bindings. SwiftUI's environment can provide dependencies without explicit injection. These mechanisms complement traditional patterns.

Cross-platform frameworks like Flutter and React Native have their own patterns. State management libraries, navigation packages, and dependency injection approaches exist for each framework. Understanding the core patterns helps evaluate and use framework-specific implementations.

## Testing Mobile Architectures

Unit testing at each layer verifies components in isolation. Repository tests verify data source coordination and caching logic with mock data sources. UseCase tests verify business logic with mock repositories. View model tests verify state management with mock use cases. Each layer tests against dependencies' interfaces.

Integration testing verifies layer interactions. Repository integration tests might use a real database but mock network. UseCase integration tests might use real repositories but controlled data. These tests catch integration issues that unit tests miss.

UI testing verifies end-to-end flows. Automated tests drive the UI, verifying that tapping buttons, entering text, and navigating produces expected results. These tests are slower but catch issues in UI layer that other tests miss.

Mock implementations require careful design. A mock repository needs to support the same interface as the real repository, returning controlled data and recording method calls for verification. Shared mock implementations across tests reduce duplication and inconsistency.

Test fixtures provide common test data. Rather than creating test data in each test, fixtures define standard users, orders, products that tests reference. Fixtures make tests more readable and data changes easier.

## Evolution and Maintenance

Pattern adoption typically happens incrementally. You might introduce repositories first, then add use cases, then implement coordinators. Each step provides value; you don't need everything at once. Incremental adoption reduces risk and spreads learning.

Refactoring toward patterns improves existing code. Extract repository from inline data access. Extract use case from view controller. Introduce coordinator for complex navigation. Each refactoring improves structure without rewriting everything.

Team communication about patterns requires shared vocabulary. When everyone understands what "repository" and "use case" mean, code reviews and design discussions are more productive. Pattern names communicate design intent efficiently.

Documentation captures pattern decisions and rationale. Why did we choose this repository boundary? What does this coordinator's scope include? Documentation helps new team members understand existing choices and helps the team make consistent future decisions.

Pattern anti-patterns emerge when patterns are misapplied. Repositories that contain business logic, coordinators that manage too much, use cases that become god objects—these indicate pattern misuse. Recognizing anti-patterns helps correct course before problems compound.

The goal throughout is maintainable, testable, understandable code. Patterns are means to that end, not ends themselves. When patterns serve the goal, apply them. When they introduce unnecessary complexity without compensating benefits, simplify. The judgment to know which situation you're in comes from experience, reflection, and continuous learning.
