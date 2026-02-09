# Android Repository Pattern: Single Source of Truth and Offline-First Architecture

## Understanding the Repository Pattern

The repository pattern creates an abstraction layer between data sources and the rest of the application. In Android development, data typically comes from multiple sources: remote APIs providing fresh data, local databases enabling offline access, and in-memory caches providing fast access. Without proper abstraction, ViewModels must know about each data source, coordinate between them, and handle the complexity of determining which source to use under what circumstances.

The repository pattern addresses this complexity by providing a single, unified interface for data access. ViewModels call repository methods without knowing whether data comes from network, database, or cache. The repository implementation contains the logic for coordinating between sources, implementing caching strategies, and managing data consistency. This separation enables cleaner ViewModels, easier testing, and centralized data management logic.

## The Problem Without Repository Pattern

When ViewModels directly access data sources, several problems emerge that compound as applications grow.

Duplicated coordination logic appears across ViewModels. If multiple screens need user data, each ViewModel implements its own logic for checking cache freshness, deciding when to fetch from network, and handling errors. This duplication leads to inconsistencies where different screens might have different caching behaviors or error handling approaches.

Testing becomes difficult because ViewModels depend directly on network clients and databases. Testing a ViewModel requires mocking both the API client and the database, understanding the interactions between them, and setting up complex scenarios. With a repository abstraction, tests can mock a single repository interface with predetermined behavior.

Changes to data source implementation ripple through the application. If the API endpoint changes, every ViewModel that uses that endpoint needs updating. If caching strategy needs adjustment, changes are needed wherever that logic is duplicated. The repository pattern isolates these concerns, limiting change impact to the repository implementation.

Data consistency issues arise when different screens maintain separate copies of the same data. One screen might show stale cached data while another shows fresh network data. Users see inconsistent information depending on which screen they view. Centralizing data management in repositories enables consistent views across the application.

## Single Source of Truth

The Single Source of Truth principle states that any piece of data should have one authoritative location. For Android applications, the local database typically serves as this source. The user interface observes data from the database, not directly from network responses. Network operations update the database, and database changes automatically propagate to observers.

This architecture provides several benefits. The user interface displays consistent data because it always reads from one location. Network failures do not cause the UI to show nothing; it continues showing the last known data from the database. The application works offline because the database contains persistent data. Complex synchronization logic between network and UI is eliminated because the database mediates all data flow.

Implementing Single Source of Truth involves specific patterns. Repository methods that provide data return Flow instances from the database. Refresh operations fetch from network and update the database but do not directly return network responses. The Flow from the database emits new values when the database changes, automatically updating observers.

The refresh pattern separates data observation from data fetching. A method like getUsers returns a Flow that emits user lists from the database. A separate method like refreshUsers fetches from network and updates the database, returning only success or failure indication. ViewModels observe the Flow for data and call refresh to update, but the two operations are independent.

## Data Sources Architecture

A well-structured repository delegates to data source classes that encapsulate access to specific sources.

Remote data sources wrap API clients, providing methods that make network requests and return data transfer objects. This layer handles network-specific concerns like authentication header attachment, response parsing, and network error mapping. The remote data source does not know about databases or caching.

Local data sources wrap database access, providing methods for queries, insertions, updates, and deletions. This layer returns entity objects as defined by the database schema. For Room databases, the data source might simply expose DAO methods. The local data source does not know about network operations.

In-memory cache data sources provide fast access to frequently used data. Unlike database storage, cache contents exist only in memory and are lost when the process terminates. Cache data sources typically implement time-based invalidation, size limits, and access patterns that determine what to cache.

The repository coordinates between these data sources according to its caching strategy. It transforms between data transfer objects, database entities, and domain models as data moves between layers. It implements business rules about data freshness, fallback behavior, and error handling.

This separation enables independent testing and modification of each layer. The remote data source can be tested with mock servers. The local data source can be tested with in-memory databases. The repository can be tested with fake data sources that return predetermined data.

## Caching Strategies

Different applications and data types require different caching strategies. Understanding these strategies enables appropriate choices for specific situations.

Cache-first strategy returns cached data immediately if available, then optionally refreshes from network in the background. This approach optimizes for display speed, showing users something immediately. It works well for data that changes infrequently or where slight staleness is acceptable, like reference data, configuration, or historical records.

Network-first strategy attempts to fetch fresh data from the network, falling back to cached data only if the network request fails. This approach prioritizes freshness over speed. It suits data that changes frequently and where users expect current information, like social feeds, prices, or availability.

Stale-while-revalidate strategy returns cached data immediately while simultaneously fetching fresh data. When fresh data arrives, it updates the cache and notifies observers. Users see data quickly but also see updates when available. This balances speed with freshness for data where both matter.

Cache-then-network strategy returns cached data first, then follows with network data as a second emission. Observers receive two updates: the fast cached response and the fresh network response. This approach is useful when the UI can smoothly transition from cached to fresh data.

Choosing between strategies depends on data characteristics. Configuration data that rarely changes suits aggressive caching. Real-time data like stock prices needs minimal caching. User-generated content like posts balances caching for offline access with freshness for social relevance.

## Cache Invalidation

Determining when cached data is no longer valid is one of the hardest problems in computer science, famously attributed as such by Phil Karlton. Several approaches address cache invalidation with different tradeoffs.

Time-based invalidation considers data stale after a specified duration. A cache entry created fifteen minutes ago might be considered fresh, while one created an hour ago might be considered stale. This approach is simple to implement but does not account for actual data changes. Data might change immediately after caching or remain unchanged for days.

Version-based invalidation uses version numbers or ETags to determine freshness. The server includes version information with responses. Subsequent requests include this version, and the server responds with data only if the version has changed. This approach accurately reflects actual changes but requires server support.

Event-based invalidation clears cache when specific events occur. A user editing their profile invalidates the profile cache. A purchase completing invalidates the order history cache. This approach requires identifying all events that affect each cache but provides accurate invalidation.

Manual invalidation allows users to explicitly request fresh data through pull-to-refresh or refresh buttons. This supplements automatic invalidation for situations where users know data should have changed.

Implementing time-based invalidation involves storing timestamps with cache entries. When retrieving data, compare the storage time with current time. If the difference exceeds the validity threshold, treat the entry as stale. Stale entries might be deleted immediately or kept as fallback while fetching fresh data.

## Offline-First Architecture

Offline-first architecture prioritizes local data over network data, enabling full application functionality without network connectivity. This approach is essential for applications used in areas with poor connectivity, during travel, or in other offline scenarios.

The fundamental shift in offline-first is treating the database as primary storage rather than cache. Data created or modified by users is immediately saved to the database. The network synchronizes database content with servers when connectivity exists. The application works fully offline, with synchronization happening opportunistically.

Optimistic updates provide immediate feedback for user actions. When a user submits a comment, the comment appears instantly in the UI because it is saved directly to the database. Network synchronization happens in the background. If synchronization fails, the comment is marked as pending and retried later. Users experience responsive interactions regardless of network conditions.

Conflict resolution addresses situations where offline changes conflict with server state. If two users modify the same record offline, synchronization must reconcile the differences. Strategies include last-write-wins where the most recent change prevails, server-wins where server state takes priority, client-wins where local changes take priority, and manual resolution where users choose between conflicting versions.

Synchronization status tracking enables the UI to show pending synchronization. Entities might include a sync status field indicating whether they are synced, pending sync, or failed to sync. The UI can show indicators for pending items and provide retry options for failed items.

WorkManager provides reliable background synchronization. Sync workers execute when network is available, surviving application termination and device restarts. Exponential backoff handles transient failures without overwhelming servers or draining battery.

## Implementing Repository Pattern

A repository implementation coordinates data sources to provide a unified interface.

The repository interface defines methods that consumers use. These methods typically include a Flow-returning method for observing data, a suspend method for refreshing data, and methods for creating, updating, and deleting data. The interface uses domain model types, not data transfer objects or database entities.

The repository implementation receives data sources through constructor injection. It implements interface methods by coordinating between sources according to the chosen caching strategy. It transforms between layer-specific types using mapper functions.

For data observation, the repository returns Flow from the local data source, transforming entities to domain models. For refresh, it fetches from the remote data source, transforms to entities, stores in the local data source, and returns success or failure indication. The Flow automatically emits new values when the local data source is updated.

Error handling in repositories wraps network and database errors in application-specific result types. A sealed class representing success, error, and loading states provides type-safe error handling. Repositories catch exceptions from data sources and wrap them appropriately.

## Mapping Between Layers

Different layers use different data models, requiring transformation between them.

Data transfer objects match API response structure. These classes use serialization annotations and names that match JSON field names. They might include fields that are API implementation details, not relevant to application logic.

Database entities match database schema. These classes use Room annotations for table names, column definitions, and relationships. They might include fields for local bookkeeping like sync status or creation timestamps.

Domain models represent business concepts. These classes contain only fields relevant to application logic, without serialization annotations or database details. They use appropriate Kotlin types like Instant for timestamps rather than strings or longs.

Mapper functions transform between these model types. Extension functions provide clear transformation syntax. Mapping functions belong to the layer that knows about both types, typically the data layer that knows about DTOs and domain models.

The mapping boundary protects inner layers from outer layer changes. If the API changes field names, only DTOs and mapper functions change. If database schema evolves, only entities and mappers change. Domain models remain stable, and consumers of the repository are unaffected.

## Testing Repositories

Repository testing verifies correct coordination between data sources and proper implementation of caching strategies.

Unit tests use fake data source implementations. A fake remote data source can be configured to return specific data or throw exceptions. A fake local data source might use in-memory collections. Tests verify that the repository calls appropriate sources and returns expected results.

Testing caching strategies involves verifying source selection. When cache is fresh, the repository should not call the remote source. When cache is stale, the repository should fetch from remote. When network fails, the repository should return cached data if available.

Testing offline behavior involves simulating network unavailability. The fake remote data source throws network exceptions. The repository should handle these gracefully, returning cached data if available or appropriate error states if not.

Testing sync behavior involves verifying correct synchronization flow. Local changes should be marked as pending. Sync operations should send pending changes to the remote source. Successful sync should update local sync status.

Integration tests verify actual data source behavior. Room database tests use in-memory databases for speed. Network tests might use mock servers to verify request construction and response handling. These tests catch issues that fake data sources cannot reveal.

## Common Mistakes and Antipatterns

Several recurring mistakes undermine repository implementations.

Exposing data source details through the repository interface couples consumers to implementation. Repository methods should use domain types, not DTOs or entities. This enables changing data sources without affecting consumers.

Returning network responses directly instead of observing database bypasses Single Source of Truth. This causes inconsistency between screens and complicates offline support. Even when data must be fresh, the pattern should be fetch, store, and observe.

Not handling errors leaves consumers vulnerable to crashes. Network failures, database errors, and parsing exceptions must be caught and wrapped in appropriate result types.

Overcomplicating caching with multiple invalidation schemes creates maintenance burden. Start with simple time-based invalidation and add complexity only when needed.

Creating one repository per entity rather than per feature leads to scattered data logic. A user feature might need data from multiple entities; a feature repository can coordinate this efficiently.

## Relationship to Architecture Patterns

Repository pattern integrates with broader architectural patterns.

In MVVM architecture, ViewModels depend on repositories. ViewModels observe repository flows and call repository methods in response to user actions. ViewModels do not depend on API clients or DAOs directly.

In Clean Architecture, repositories live in the data layer. The domain layer defines repository interfaces. The data layer provides implementations. This inversion enables domain logic testing without data layer dependencies.

Dependency injection provides repository implementations to consumers. Hilt modules bind repository interfaces to implementations. Different modules can provide different implementations for testing.

## Relationship to Computer Science Fundamentals

Repository pattern applies fundamental software engineering concepts.

Abstraction hides complexity behind simple interfaces. Consumers interact with a repository method without understanding the caching, synchronization, and error handling within.

Separation of concerns isolates data access logic from presentation logic. ViewModels focus on user interaction and presentation state. Repositories focus on data management.

The Facade pattern provides a unified interface to a complex subsystem. The repository is a facade over data sources, hiding their complexity from consumers.

Caching applies spatial and temporal locality principles. Recently accessed data is kept available. Frequently accessed data is prioritized.

## Conclusion

The repository pattern provides essential abstraction for data management in Android applications. By centralizing data access logic, it eliminates duplication, enables testing, and isolates consumers from implementation changes.

Single Source of Truth using local database as the authoritative source simplifies consistency management and enables offline functionality. The user interface observes database state, and network operations update the database.

Caching strategies balance freshness against speed according to data characteristics. Different strategies suit different situations, and understanding the tradeoffs enables appropriate choices.

Offline-first architecture extends these patterns to enable full functionality without network connectivity. Optimistic updates provide immediate feedback while background synchronization maintains consistency with servers.

Proper implementation requires careful attention to error handling, layer separation, and testing. The patterns are straightforward but require discipline to maintain consistently. The investment pays off in applications that are more reliable, testable, and maintainable.
