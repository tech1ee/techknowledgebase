# iOS Modularization

## Why Modularization Matters for iOS Apps

Modularization transforms how iOS applications are structured, developed, and maintained. Rather than building one monolithic target containing all code, modularized apps divide into independent modules with clear boundaries and explicit dependencies. This architectural shift provides profound benefits but requires understanding new concepts and accepting some ceremony. The investment pays dividends as applications and teams scale.

Think of modularization like organizing a house. A studio apartment has everything in one room—kitchen, bedroom, living area all together. This works fine for one person. But as more people move in, the single room becomes chaotic. People cooking interfere with people sleeping. There's no privacy, no boundaries, no way to isolate activities. A well-designed house has separate rooms with doors. Each room serves a purpose. People can work in different rooms without interfering. You can renovate the kitchen without affecting bedrooms.

Monolithic iOS apps work like studio apartments. All code lives in one target. Every class can access every other class. Dependencies form spaghetti tangles. Changing one component risks breaking unrelated features. Build times grow linearly with code size because the entire app recompiles for any change. Teams step on each other's toes working in the same files. Testing requires compiling the entire application.

Modularized apps work like houses with rooms. Each module is a room with a door—the public API. Modules cannot access each other's internals, only published interfaces. Dependencies are explicit in module definitions. Changing one module doesn't require recompiling others if the interface stays stable. Multiple developers work on different modules in parallel without conflicts. Testing compiles only the module being tested and its dependencies.

The benefits compound as applications grow. A small app with three screens and two developers gains little from modularization. The ceremony outweighs benefits. A large app with hundreds of screens and dozens of developers gains dramatically. Build times that would be unmaintainable in a monolith become reasonable with modules. Features that would be impossible to develop in parallel become straightforward. Code that would be hopelessly tangled becomes cleanly separated.

Modularization also enables code reuse across targets. iOS apps often have multiple targets: the main app, widgets, app extensions, today extensions, watch apps. Without modularization, code shared between targets gets duplicated or placed in a framework with unclear purpose. With modularization, shared business logic lives in modules that multiple targets consume. The expense report parsing logic used by both the main app and the widget lives in a dedicated module. Both targets depend on this module. No duplication, no divergence.

Swift Package Manager makes modularization practical for iOS. Before SPM, creating frameworks required Xcode project configuration complexity. SPM uses simple Package.swift manifest files. Creating a new module means creating a directory with a Package.swift file. No Xcode project files, no configuration screens. This simplicity lowered the barrier to modularization, making it accessible to more teams.

The fundamental tension in modularization is granularity. Too few modules and you haven't solved the monolith's problems. Too many modules and you drown in ceremony and dependency management. Finding the right granularity requires understanding your application's structure, team organization, and development workflow. There's no universal answer, only trade-offs to evaluate based on your context.

## Understanding Module Boundaries and Interfaces

Modules succeed or fail based on their boundaries. A well-designed boundary clearly separates concerns, hides implementation details, and provides a stable interface. A poorly-designed boundary leaks abstractions, creates unnecessary dependencies, and changes frequently, breaking dependents. Understanding what makes a good module boundary is essential for effective modularization.

Think of module boundaries like country borders. Good borders follow natural features—rivers, mountain ranges, coastlines. They're easy to defend, hard to accidentally cross, and relatively stable over time. Bad borders cut through towns, divide ethnic groups, and constantly dispute. Good module boundaries follow conceptual divisions in your application. They separate concerns that naturally belong together from concerns that are independent. Bad boundaries split related functionality and couple unrelated pieces.

The most fundamental question when defining a module is what it represents. Feature modules group all code for a user-facing feature: views, view models, models specific to that feature. Platform modules provide infrastructure used across features: networking, storage, analytics. Domain modules contain business logic independent of infrastructure: domain entities, business rules, use cases. Each type of module has different boundary considerations.

Feature modules should contain everything needed to implement a feature but nothing more. A profile feature module contains profile views, profile view models, and profile-specific models. It depends on networking and storage modules for infrastructure but implements all profile-specific logic internally. The boundary is the feature itself. Everything inside relates to profiles. Nothing unrelated sneaks in.

The challenge with feature modules is avoiding dependencies between features. If the profile module depends on the friends module, which depends on messaging, which depends on profile, you've created a circular dependency nightmare. Breaking these cycles requires interface modules—abstract protocols that features depend on rather than concrete implementations.

Platform modules provide capabilities that many features need. A networking module handles HTTP requests, response parsing, and error handling. Multiple features depend on it. The boundary is the capability—everything related to networking lives here, nothing unrelated intrudes. The module exposes protocols for making requests and concrete implementations of those protocols.

The key to good platform module boundaries is minimizing dependencies. A networking module should depend on nothing application-specific. It should work in any iOS app. This independence makes it reusable and testable. If your networking module depends on your user model, the boundary is wrong. Abstract the dependency through protocols or move user-specific logic to a higher-level module.

Domain modules contain pure business logic. They depend on no frameworks, no infrastructure. A ride-sharing app's domain module might contain entities like Driver, Rider, Trip and business rules like fare calculation and driver matching. The boundary is the domain concept. Everything that's true about the business domain, independent of technical implementation, belongs here.

Public APIs represent where boundaries become concrete. Only types and functions marked public are accessible to other modules. Everything else is private to the module. Designing public APIs carefully ensures stable boundaries. Exposing too much couples dependents to internal details. Changes break consumers. Exposing too little requires constant expansion, causing dependency churn.

A well-designed public API reveals what the module does while hiding how it does it. A networking module's API might expose a protocol for making requests and method for creating a network service. It doesn't expose JSON parsing details, retry logic, or caching implementation. Clients can make requests without understanding internals. This abstraction enables changing implementation without breaking clients.

Interface modules take this further by containing only protocols and models, no implementations. A ProfileAPI module might define a ProfileService protocol and a Profile model. The ProfileFeature module implements this protocol. Other features depend only on the API module, not the implementation module. This inverts dependencies and breaks circular references.

The stability of boundaries matters tremendously. A module whose public API changes frequently creates maintenance burden for all dependents. Every change requires updating dependent modules. Aim for stable APIs that change infrequently. When changes are necessary, consider adding new methods rather than modifying existing ones to maintain compatibility.

Semantic versioning helps communicate boundary stability. Major version changes indicate breaking API changes. Minor versions add functionality while maintaining compatibility. Patch versions fix bugs without changing APIs. Dependencies can specify version constraints, allowing minor and patch updates automatically while requiring explicit major version adoption.

Understanding what belongs inside versus outside a module requires clear mental models. Ask whether functionality relates to the module's core responsibility. If yes, it belongs inside. If no, it's a dependency. Drawing these lines clearly produces cohesive modules with clear purposes rather than grab-bag collections of loosely related code.

## Swift Package Manager for Modularization

Swift Package Manager provides the technical foundation for iOS modularization. Understanding SPM's concepts, capabilities, and limitations enables effective module organization. SPM started for server-side Swift but evolved into a powerful tool for iOS, replacing complex framework creation workflows with simple manifest-based configuration.

Think of SPM like a recipe book for building software. Each package is a recipe. The Package.swift file lists ingredients—dependencies—and instructions—how to compile sources into products. When you build a package, SPM reads the recipe, gathers ingredients, and follows instructions to produce the result. Xcode understands these recipes and integrates them into the build process seamlessly.

A Package.swift file defines a package's structure. It specifies the package name, supported platforms like iOS 17, products the package exports, dependencies on other packages, and targets containing actual code. Products are what consumers see—typically libraries that other packages or apps import. Targets are the building blocks—compilable units of source code.

Local packages live in your project's directory structure. Creating a module means making a directory containing Package.swift and a Sources subdirectory. The app's Xcode project adds this local package as a dependency. The app can then import the module. This setup works perfectly for application-specific modules that don't need external distribution.

Remote packages come from Git repositories. SPM clones them, resolves dependencies recursively, and integrates them into builds. Major open source libraries distribute via SPM. Your app might depend on networking libraries, image processing frameworks, or UI components distributed as SPM packages. SPM handles downloading, version management, and compilation automatically.

Dependencies can specify version requirements: exact versions, minimum versions, version ranges, branches, or commits. Semantic versioning works beautifully with SPM. Specify that you depend on a package from version 1.0 up to but not including 2.0. SPM resolves to the latest compatible version. When the package releases 1.1 with new features, SPM updates automatically. When 2.0 ships with breaking changes, SPM requires explicit adoption.

Targets represent compilable units within a package. A package might have multiple targets: the main library target, a test target, maybe a command-line tool target. Each target specifies its sources, resources like images or data files, and dependencies on other targets or products from dependency packages. This enables fine-grained control over what builds and what depends on what.

Products define what a package exports for consumption. A library product exposes targets for linking into apps or other packages. An executable product produces a binary. Most iOS packages export libraries. Products can be statically or dynamically linked, though iOS apps typically use static linking to avoid dynamic library overhead.

Resources support is crucial for iOS packages. Views need images, localized strings, and data files. SPM handles resources through resource declarations in targets. Process resources get copied into the bundle. Copy resources get copied literally. Localized resources support internationalization. This makes creating reusable UI components with assets straightforward.

Binary targets enable depending on pre-compiled frameworks like closed-source SDKs that only distribute as XCFrameworks. You create a binary target pointing to the XCFramework and other targets depend on it. This integrates third-party binaries into the SPM dependency graph seamlessly.

Access control in SPM modules uses Swift's normal visibility rules. Internal types are visible within the module but not to consumers. Public types are visible to consumers. This enforces boundaries. Unlike app targets where everything is effectively internal, modules must explicitly mark APIs public, forcing consideration of what should be exposed.

Build time optimization comes from incremental compilation. SPM compiles each module once. If the module's sources don't change, it doesn't recompile. Only modified modules and their dependents rebuild. In a well-modularized app with dozens of modules, this dramatically reduces build times compared to a monolith where every change triggers full recompilation.

Testing in SPM creates test targets that depend on the module being tested. Tests import the module and verify its behavior. This encourages testable module design—modules should be testable independently. Integration tests might depend on multiple modules, verifying they work together correctly.

One limitation is that SPM resolves all dependencies to compatible versions globally. If module A depends on version 1.x of package C and module B depends on version 2.x, SPM cannot resolve this. Both modules must agree on compatible versions. This encourages keeping dependencies updated and avoiding overly restrictive version constraints.

Another consideration is that Xcode generates derived data for SPM packages in a central cache. This speeds builds by sharing compiled modules across projects but can cause confusion when stale caches cause mysterious issues. Understanding when to clean derived data helps debug these situations.

SPM integrates directly into Xcode, making module management part of the standard development workflow. Adding a package, updating dependencies, and managing versions all happen in Xcode. This integration makes SPM feel native rather than bolted on, encouraging adoption.

## Organizing Modules by Architectural Layers

How you divide modules significantly impacts maintainability and scalability. Layer-based organization groups modules by architectural role: domain, data, presentation, infrastructure. This structure clarifies dependencies, enforces separation of concerns, and maps naturally to clean architecture principles.

Think of layered architecture like a building. The foundation provides structural support but doesn't care about interior design. The walls divide space and bear weight but don't generate power. Electrical systems provide power but don't decide room layout. Furniture makes rooms functional but doesn't provide structural support. Each layer serves a role. Dependencies flow downward—furniture depends on floors, not vice versa.

The domain layer forms the foundation containing pure business logic. Entities like User, Order, and Product live here. Business rules like discount calculation and eligibility determination belong here. This layer depends on nothing—no UIKit, no networking, no database. Pure Swift value types and logic. This independence makes domain logic testable and reusable across platforms.

Domain modules should be small and focused. Rather than one massive Domain module, create modules per domain concept: UserDomain, OrderDomain, ProductDomain. Each contains entities and business logic for that concept. This granularity enables parallel development and reduces coupling.

The data layer sits atop the domain layer, implementing data access. Repository modules define protocols for data operations. DataSource modules implement these protocols, fetching data from networks, databases, or caches. The data layer depends on the domain layer—repositories return domain entities. But the domain layer knows nothing about data sources.

Creating interface modules for repositories inverts dependencies cleanly. UserRepositoryInterface defines a protocol for user data access. UserDomain depends on this interface, not concrete implementations. UserRepository implements the interface, depending on domain for entity types and interface for protocol definitions. Features depend on the interface, not implementations. This enables swapping implementations without affecting dependents.

The presentation layer contains view models, views, and coordinators. This layer depends on domain and data interfaces but not data implementations. ViewModels orchestrate use cases from the domain layer. Views observe ViewModels and render UI. Coordinators handle navigation. Each feature gets its own module: ProfileFeature, SettingsFeature, CheckoutFeature.

Feature modules should be vertically sliced, containing everything needed for that feature: all views, view models, coordinators, and feature-specific logic. Features depend on shared UI components from a design system module and on use cases from domain modules. But features should not depend on each other. If ProfileFeature needs to navigate to SettingsFeature, both depend on a shared Navigation protocol, and the app coordinates the actual navigation.

The infrastructure layer provides cross-cutting concerns: logging, analytics, networking, caching. These modules depend on nothing application-specific. They could be extracted into separate packages used by multiple apps. A Networking module handles HTTP requests. An Analytics module tracks events. A Logger module provides structured logging.

This layering creates clear dependency rules. Domain depends on nothing. Data depends on domain. Presentation depends on domain and data interfaces. Infrastructure depends on nothing application-specific. The app target sits atop all layers, composing them into a working application.

The app target's responsibility is composition. It creates implementations, wires dependencies, and starts the app. Dependency injection happens here. The app creates a NetworkService, injects it into Repositories, injects Repositories into ViewModels, and presents the initial view. This composition root centralizes configuration.

Avoiding layer violations is crucial. A domain module should never import UIKit. A data implementation should never depend on presentation. A feature should never depend on another feature directly. These violations create coupling that defeats modularization's purpose. Code reviews should watch for improper imports as red flags.

Organizing files within modules matters too. Consistent structure helps developers navigate. A common pattern is grouping by type: Models, Views, ViewModels, Services. Another is grouping by feature within modules: ProfileView and ProfileViewModel together. Choose a pattern and apply it consistently.

The number of modules to create depends on application size. A small app might have domain, data, presentation, and infrastructure—four modules. A medium app might have a module per major feature and shared modules for common capabilities—twenty modules. A large app might have hundreds of modules, with sub-modules for feature aspects. Let pain drive granularity. If modules are too coarse, they don't provide benefits. If too fine, dependency management becomes overwhelming.

Layer-based organization provides structure that scales from small to large applications. Starting with a few modules and adding granularity where it helps produces practical architectures that balance ceremony with benefits.

## Feature Modules and Micro-Frontends

Feature modules represent an architectural pattern where each user-facing feature becomes an independent module. This vertical slicing maximizes team autonomy and development velocity by minimizing cross-team dependencies and enabling parallel development of features.

Think of feature modules like food trucks versus a traditional restaurant. A traditional restaurant has shared kitchen, shared dining room, shared staff. Changes to the kitchen affect all dishes. Adding a new menu item requires coordinating with the entire kitchen staff. Food trucks are independent. Each truck has its own kitchen, menu, and staff. They can innovate independently without coordination. They can be added or removed from a food truck park without affecting others.

Feature modules work similarly. Each feature is self-contained with all necessary code: views, view models, models, coordinators. Features communicate through well-defined interfaces, not internal details. Adding a feature means creating a new module and plugging it into the app. Removing a feature means deleting the module. Changing a feature affects only that module if the interface stays stable.

A social media app might have feature modules for Feed, Profile, Messaging, Search, and Settings. Each module contains all code for that feature. Feed module has feed views, feed view models, feed-specific data models, and feed navigation logic. Profile module is entirely separate. These modules depend on shared infrastructure like networking and UI components but are independent of each other.

This independence enables powerful development workflows. Different teams own different features. The feed team works on the feed module. The profile team works on the profile module. They don't conflict over files or step on each other's changes. Teams can release features independently if the app supports feature flags or progressive rollout.

Micro-frontends extend this concept by making features so independent that they could be developed and deployed separately. While full deployment independence is rare in mobile apps, the architectural principles apply. Features should be developable, testable, and deployable as independently as possible given platform constraints.

Creating feature modules requires careful interface design. Features must communicate without direct dependencies. One approach is defining coordinator protocols that features expose. The app's root coordinator composes feature coordinators. When one feature needs to navigate to another, it calls a coordinator method defined in a protocol. The root coordinator implements cross-feature navigation.

Another approach uses URL-based routing. Features register URL patterns they handle. Navigation happens by requesting a URL. The routing system finds the appropriate feature and presents it. This decouples features—they know nothing about each other, only URLs. Adding a feature means registering new URLs. Removing a feature means unregistering URLs.

Feature modules should minimize shared mutable state. Shared state creates coupling and synchronization challenges. Features should communicate through events or messages rather than sharing state objects. When state must be shared, own it at the app level and inject it into features as read-only dependencies.

One challenge with feature modules is avoiding duplication. Multiple features might need similar views, view models, or logic. Extracting shared components into a design system module or shared utilities module prevents duplication. But resist extracting too early—some duplication is healthy if it maintains feature independence. Only extract when duplication becomes genuine maintenance burden.

Testing feature modules independently is a major advantage. Each module's tests compile only that module and its dependencies, not the entire app. Tests run faster. Failures isolate to specific modules. You can test features thoroughly without the ceremony of full app testing.

Feature flags integrate naturally with feature modules. The app can disable entire modules based on flags, removing features from builds or hiding them at runtime. This enables A/B testing features, progressive rollout, and emergency feature disabling. Feature module boundaries make this granular control straightforward.

The main downside of heavy feature modularization is coordination overhead. Features need consistent design, shared navigation patterns, and compatible data models. Without coordination, the app feels disjointed. Establishing design systems, navigation standards, and data contracts provides necessary coherence while preserving feature autonomy.

Another consideration is build complexity. Many small modules create many dependency relationships. While each relationship is simple, the total complexity can be overwhelming. Tooling helps—dependency graphs, module templates, and linting rules keep things manageable. But expect some learning curve.

Feature modules represent a powerful organizational pattern for medium to large applications with multiple teams. The vertical slicing maximizes team autonomy, the interfaces minimize coupling, and the independence enables parallel development. For applications and teams that fit this pattern, the benefits far outweigh the costs.

## Reducing Build Times Through Modularization

Build time directly impacts developer productivity. Waiting minutes for compilation kills flow state, reduces iteration speed, and frustrates developers. Modularization offers dramatic build time improvements through incremental compilation, parallel builds, and reduced compilation units.

Think about build time like rush hour traffic. A single highway from suburbs to downtown creates a bottleneck. Everyone must wait for everyone else. Building side roads, express lanes, and alternative routes enables parallel movement. People reach destinations faster because they're not all stuck behind each other. Similarly, modularizing an app creates build parallelism and incremental compilation that dramatically reduce total build time.

Monolithic apps suffer from all-or-nothing compilation. Changing one file requires recompiling everything that depends on it. In practice, this often means the entire app. A small change to a view controller triggers recompiling hundreds of thousands of lines of code. The compile takes minutes even though the actual change was tiny. This wait time accumulates throughout the day, wasting hours.

Modularized apps enable incremental compilation. Changing a file recompiles only its module. If the module's interface doesn't change, dependent modules don't recompile—they use cached compiled versions. A small change to a view in ProfileFeature recompiles only ProfileFeature, not FeedFeature or any other module. Build time drops from minutes to seconds.

Parallel compilation amplifies this benefit. Xcode compiles multiple independent modules simultaneously. With a monolith, compilation is sequential—one file after another. With modules, compilation is parallel—multiple modules compile at once on different CPU cores. A machine with eight cores can compile eight modules simultaneously. This parallelism can cut build time by a factor matching core count.

The key to maximizing these benefits is creating modules with minimal dependencies. Modules that depend on few other modules compile early in the build process. Heavily dependent modules wait for their dependencies but then compile. The less interdependency, the more parallelism and incremental benefit.

Module size affects build time non-linearly. Doubling module size more than doubles compilation time. Creating many small modules generally builds faster than fewer large modules. Breaking a feature into separate view, view model, and model modules might seem like overkill but can improve build times by enabling more parallelism and better incrementality.

Interface modules provide another optimization. Implementations change frequently but interfaces stay stable. Putting protocols in interface modules means dependent modules depend only on interfaces, not implementations. Implementation changes don't trigger dependent module recompilation. This stability dramatically improves incremental build performance.

Binary frameworks offer ultimate build time optimization for stable dependencies. Third-party libraries that rarely change can be pre-compiled as XCFrameworks and integrated as binary targets. These never compile—they're already compiled. This saves significant time for large dependencies like graphics engines or analytics SDKs.

Dependency graph structure profoundly affects build time. A flat dependency graph where many modules depend directly on a few base modules enables great parallelism. A deep diamond graph where modules depend on many intermediate modules creates compilation bottlenecks. Designing the graph for build performance means minimizing depth and keeping fan-out shallow.

Measuring build time scientifically guides optimization. Xcode's build timeline shows which modules take longest to compile and which dependencies create bottlenecks. Looking at actual data reveals where to focus effort. Optimizing the slowest module or breaking critical path dependencies provides maximum improvement.

Clean builds versus incremental builds behave differently. Clean builds compile everything. Incremental builds compile only changed modules. Both matter but for different reasons. Clean builds happen when switching branches or updating dependencies. Incremental builds happen during normal development. Optimize both scenarios.

One challenge is that over-modularization can actually slow builds. Every module has overhead—parsing Package.swift, resolving dependencies, creating build products. Hundreds of trivial modules might be slower than dozens of reasonably-sized modules. Finding the sweet spot requires experimentation and measurement.

Another consideration is developer machine hardware. Fast compilation depends on CPU cores and SSD speed. Modularization benefits scale with hardware capability. On a slow machine with few cores, the benefit is less pronounced than on a high-end machine with many cores and fast storage.

Team size affects optimal build time strategies. Individual developers care about incremental build time—how long after making a change before they can run the app. CI/CD systems care about clean build time—how long to build the entire app from scratch. Optimizing for both might require different strategies.

Build time is a quality-of-life issue that affects daily productivity. Investing in modularization to reduce build time pays dividends every day developers work on the app. Faster builds mean more iterations, less waiting, and happier developers. For large applications, this alone justifies modularization.

## Managing Dependencies Between Modules

Dependency management makes or breaks modularized architectures. Well-managed dependencies create clean graphs that compile quickly and evolve smoothly. Poorly-managed dependencies create tangled graphs that compile slowly and resist change. Understanding dependency management principles and practices is essential for successful modularization.

Think of module dependencies like roads between cities. Well-planned roads connect cities efficiently with clear routes and minimal congestion. Poorly-planned roads create confusing spaghetti intersections and traffic jams. Similarly, well-managed module dependencies create clear paths for data and control flow. Poorly-managed dependencies create confusing tangles that slow everything down.

The first principle is minimizing dependencies. Each dependency is a coupling point. More dependencies mean more coupling, slower builds, and harder changes. Before adding a dependency, ask whether it's truly necessary. Can the functionality be implemented internally? Can the dependency be inverted using protocols? Can a shared utility module handle both uses? Add dependencies only when the value clearly exceeds the cost.

Dependency direction matters tremendously. Dependencies should flow from high-level modules to low-level modules, never the reverse. High-level modules contain application-specific logic. Low-level modules provide generic capabilities. The application depends on networking, not vice versa. Features depend on domain entities, not vice versa. This direction ensures low-level modules stay reusable and high-level modules can change without affecting foundations.

Circular dependencies are forbidden in SPM and for good reason. If module A depends on module B and module B depends on module A, neither can compile before the other. This creates an impossible situation. Breaking circular dependencies requires introducing abstractions. Extract protocols both modules depend on into a shared interface module. Or recognize one module should depend on the other but not vice versa and refactor accordingly.

Interface modules break dependency cycles elegantly. When two features need to interact, create a shared interface module defining protocols and models. Both features depend on the interface. One feature implements the interface, the other uses it through the protocol. This inverts the dependency, breaking the cycle. The features no longer depend on each other, only on the shared interface.

Transitive dependencies propagate through the dependency graph. If module A depends on module B, which depends on module C, then A transitively depends on C. Changes to C might affect A even though A doesn't directly depend on C. Minimizing transitive dependencies requires careful graph design. Deep dependency chains create brittleness. Flat graphs are more robust.

Versioning dependencies enables parallel evolution. Internal modules often use local file paths—they're always the latest version because they're part of the project. External dependencies should use semantic versions. Specify version constraints that allow compatible updates while preventing breaking changes. This enables updating dependencies without breaking dependents.

Dependency injection resolves dependencies at runtime rather than compile time. Modules define what they need through protocols. The app's composition root provides implementations. This deferred binding enables testing with mocks, swapping implementations, and maintaining clean boundaries. Protocol-based dependencies are generally preferable to concrete dependencies.

One-way dependencies simplify mental models. If all dependencies flow from features to infrastructure, you know infrastructure changes might affect features but feature changes won't affect infrastructure. This makes impact analysis straightforward. Two-way dependencies create complex feedback loops where changes ripple unpredictably.

Dependency graphs should be directed acyclic graphs—DAGs. Starting from any module and following dependencies should never return to the starting point. This property ensures compilation is possible and reasoning about dependencies is tractable. Any cycle violates this property and must be eliminated.

Layer violations—dependencies that skip layers or go the wrong direction—should be prevented through conventions and tooling. A presentation module should never depend on a data implementation module. Detecting these violations through linting or code review prevents architectural degradation. Every dependency should have a reason that aligns with architectural principles.

Optimizing for build time means considering dependency graph shape. Wide, shallow graphs build faster than narrow, deep graphs. If many modules can compile in parallel, overall build time drops. If dependencies force sequential compilation, build time increases. Designing for parallelism means minimizing critical path dependencies.

Documentation helps manage growing dependency graphs. A high-level diagram showing major modules and their relationships provides crucial context for developers. Without this overview, understanding where to make changes requires reading many Package.swift files. Maintaining architecture documentation prevents this comprehension burden.

As applications grow, dependency management becomes more challenging. Automated tools can help. Scripts that generate dependency graphs, detect cycles, and identify violations make management tractable. Code generation can create boilerplate for dependency injection, reducing manual wiring effort.

The key insight is that dependencies are not free. Each one is a commitment to couple modules together. Managing them deliberately rather than accidentally produces better architectures that age gracefully rather than ossifying into unmaintainable tangles.

## Common Modularization Mistakes and Solutions

Modularization seems straightforward until you encounter subtle issues that undermine benefits. Understanding common mistakes helps avoid them and build better modularized architectures.

Creating too few modules defeats the purpose. If your entire application lives in three modules, you haven't really modularized. You've just split a monolith into large chunks. The benefits of incremental compilation, parallel builds, and clear boundaries require genuine granularity. Start with more modules than seems comfortable. You can always merge if needed, but splitting large modules later is harder.

Creating too many modules drowns you in dependency management overhead. If you have separate modules for every single view, the Package.swift files become harder to maintain than the code. Each module has costs—dependency management, boilerplate, mental overhead. Balance granularity against overhead. Modules should represent meaningful architectural units, not arbitrary file groupings.

Leaking implementation details through public APIs couples dependents to internals. When a module exposes internal types or implementation-specific methods, clients depend on details that should be hidden. Changes to these internals break clients even though the logical interface hasn't changed. Design APIs around capabilities, not implementations. Expose only what clients genuinely need.

Circular dependencies create impossible build situations. SPM forbids them, so you catch these errors immediately. But they indicate design problems. Features that depend on each other aren't properly separated. Breaking cycles by extracting interfaces is the technical solution. Reconsidering feature boundaries is the design solution.

Inconsistent modularization confuses developers. If some features are modules while others live in the app target, or if some layers are modularized while others aren't, nobody knows where to put new code. Establish clear patterns—features as modules, infrastructure as modules, app target only for composition—and apply them consistently.

Forgetting to update dependencies when module interfaces change causes version skew issues. If module A changes its API but dependent modules still reference the old API, builds fail with confusing errors. When changing module interfaces, update all dependents in the same commit. This keeps everything synchronized and buildable.

Not documenting module purposes leaves developers guessing. When a module is named something vague like Common or Utilities, what belongs there? Clear naming and documentation prevent modules becoming dumping grounds for random code. Each module should have a clear responsibility stated in documentation.

Ignoring build time measurements means optimizing blindly. Measure before modularizing to establish baseline build times. Measure after each change to verify improvements. Without measurements, you're guessing whether modularization helped. Data guides effective optimization.

Mixing concerns within modules creates unclear boundaries. A module that contains both view code and business logic couples presentation to domain. Separating these into distinct modules clarifies responsibilities and enables better testing. Each module should represent one architectural concern.

Over-relying on dependency frameworks creates framework lock-in. If your entire modularization strategy depends on a specific DI framework, migrating becomes nearly impossible. Use framework-agnostic patterns where possible. Frameworks should enhance, not enable, your architecture.

Neglecting test modules means modules aren't actually testable. Each module should have corresponding test modules. If tests exist only at the app level, you haven't gained modularization's testing benefits. Module-level tests verify modules work independently. App-level tests verify integration.

Not considering module lifetime causes memory and initialization issues. Modules that create singletons or global state without cleanup can leak memory. Understanding when modules initialize and deinitialize helps design appropriate lifecycle management.

Forgetting about modularization when hiring and onboarding makes it harder for new developers. If your architecture documentation doesn't explain the module structure and conventions, new developers struggle to contribute effectively. Invest in documentation and onboarding that explains your modularization approach.

The overarching mistake is treating modularization as purely technical when it's also organizational. Modules should map to team boundaries and product features, not just technical layers. Successful modularization aligns technical structure with team structure and product structure. This alignment enables teams to work independently while maintaining a cohesive product.

Learning from these mistakes doesn't mean avoiding them entirely. Some mistakes teach valuable lessons. The key is recognizing problems quickly and correcting course rather than persisting with failing approaches. Modularization is iterative—you'll refine your approach over time based on experience with your specific application and team.
