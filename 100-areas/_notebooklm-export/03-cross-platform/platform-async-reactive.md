# Reactive Streams: Combine versus Kotlin Flow

Reactive programming models asynchronous data as streams of values over time. Rather than callbacks that fire once, streams emit multiple values, errors, and completion signals. This paradigm proves powerful for handling user interactions, network events, database changes, and other ongoing asynchronous sources. Apple's Combine framework and Kotlin's Flow provide reactive streams for iOS and Android respectively, with similar capabilities but different designs.

## The Reactive Programming Model

Reactive programming centers on producers that emit values, operators that transform streams, and subscribers that consume results. A network monitor might emit connectivity states over time. Operators could filter to changes only, debounce rapid fluctuations, and map to user-friendly strings. A subscriber updates the UI with each string.

This model excels when dealing with multiple values over time. Traditional callback patterns handle single values well but become complex when sources emit repeatedly. Reactive streams provide consistent patterns for ongoing emissions including buffering, combining, error handling, and cancellation.

The observer pattern underlies reactive programming. Subjects or publishers maintain lists of observers. When values are available, all observers receive them. This decouples production from consumption, enabling flexible architectures where multiple consumers observe shared sources.

Backpressure handles situations where producers emit faster than consumers process. Without backpressure, buffers grow unbounded. Reactive streams define protocols for consumers to signal their processing capacity, enabling producers to adjust emission rates or for intermediate operators to buffer and batch appropriately.

## Combine Framework Architecture

Combine structures reactive streams around Publishers, Subscribers, and Operators. Publishers emit values over time. Subscribers receive those values. Operators transform streams, themselves implemented as publishers.

A Publisher declares what types of values and failures it emits. The Output associated type specifies value type. The Failure associated type specifies error type, with Never indicating the publisher cannot fail. Publishers define how subscribers attach through the receive subscriber method.

Subscribers declare what they accept through Input and Failure types. They implement receive subscription to handle attachment, receive to handle values, and receive completion to handle stream end. These methods form the communication protocol between publisher and subscriber.

Subscription represents the connection between a publisher and subscriber. Subscribers request demand through the subscription, indicating how many values they can handle. Publishers respect this demand, enabling backpressure. Canceling the subscription stops the stream.

Combine provides many built-in publishers. Just emits a single value and completes. Future resolves a single value asynchronously. Publishers.Sequence emits elements from a collection. CurrentValueSubject and PassthroughSubject enable imperative emission into reactive streams. Property wrappers like Published emit changes to properties.

Operators transform streams through chainable methods. Map transforms values. Filter removes values that do not match predicates. FlatMap transforms values into publishers and flattens results. CombineLatest combines multiple streams. These operators return new publishers, enabling fluent chains.

The sink subscriber provides convenient consumption. It takes closures for values and completion, returning an AnyCancellable that must be retained to keep the subscription alive. Releasing the cancellable cancels the subscription.

## Kotlin Flow Architecture

Flow provides cold asynchronous streams built on coroutines. Unlike Combine where publishers actively push values, Flow uses pull-based collection where the collector drives execution.

A Flow is defined by its collect function. When a coroutine collects a flow, the flow's code executes, emitting values through the emit function. The collector receives each value in its collect lambda. This inversion from push to pull affects how flows are structured and composed.

Cold streams mean flow code does not run until collection begins. Each collector gets independent execution. A flow that makes a network request makes a new request for each collector. This differs from hot publishers that emit regardless of subscribers.

SharedFlow and StateFlow provide hot stream equivalents. SharedFlow replays values to new collectors and supports multiple collectors sharing one emission source. StateFlow maintains current state, always providing the latest value to collectors. These enable patterns where multiple observers need the same stream.

Flow operators resemble Combine operators but execute in coroutine contexts. Map transforms values. Filter removes unwanted values. FlatMapConcat and flatMapMerge transform values to flows with different concurrency behaviors. Combine and zip merge multiple flows.

Terminal operators collect values. collect iterates over all values. first returns the first value. toList accumulates into a list. These operators are suspending functions that complete when the flow completes.

FlowOn changes the dispatcher for upstream operations. A flow emitted on a background thread can have its emissions processed on that thread while collection happens on Main. This enables appropriate thread placement without manual switching.

## Cold versus Hot Streams

The fundamental difference between Combine and Flow defaults involves cold and hot behavior.

Combine publishers are typically hot in the sense that publishers decide when to emit regardless of subscriber presence. A subject emits when send is called whether or not anyone subscribes. Late subscribers miss earlier emissions unless replay is configured. Network publishers might start requests when created rather than when subscribed.

Flow is cold by default. Flow code runs only during collection. Each collection is independent. A flow that fetches data fetches fresh data for each collection. This makes flows predictable but means multiple collectors cause multiple executions.

The mismatch affects how developers think about stream lifecycles. Combine developers consider when to start publishers and how to share among subscribers. Flow developers consider when collection happens and whether sharing is needed.

SharedFlow and StateFlow provide hot behavior in Flow. Converting cold flow to shared flow enables multiple collectors to share one source. SharedFlow with replay provides late subscriber access to recent values. StateFlow always provides current value.

Combine can achieve cold-like behavior through Deferred publishers that delay execution until subscription. However, the default mental model differs from Flow's default coldness.

## Operators and Transformations

Both frameworks provide rich operator sets for transforming streams, though naming and semantics sometimes differ.

Mapping transforms values one to one. Combine uses map for synchronous transformation, tryMap for throwing transformations, and flatMap for transformations returning publishers. Flow uses map for suspending transformations and mapNotNull to filter nulls.

Filtering removes unwanted values. Both provide filter for predicate-based removal. Combine adds removeDuplicates to remove consecutive equal values. Flow provides distinctUntilChanged for the same purpose.

Combining merges multiple streams. Combine provides combineLatest to emit when any input emits, using latest values from all. Zip pairs values from streams. Merge interleaves emissions. Flow provides combine with similar semantics, zip, and merge as functions that take multiple flows.

Flattening transforms values into streams and combines results. Combine flatMap by default processes concurrent inner publishers. FlatMap with maxPublishers limits concurrency. Flow flatMapConcat processes one inner flow at a time. FlatMapMerge processes concurrently. FlatMapLatest cancels previous inner flows when new values arrive.

Error handling differs between frameworks. Combine uses catch to replace errors with recovery publishers and replaceError to substitute values. Flow uses catch as a collector that handles errors. The catch lambda can emit recovery values before completing.

Buffering and timing operators control emission rates. Combine debounce waits for pauses in emission before forwarding. Throttle limits emission rate. Delay shifts emissions in time. Flow provides similar operators with debounce, sample, and delay.

## Subscription Management

Managing subscription lifecycles prevents resource leaks and ensures streams stop when no longer needed.

Combine uses AnyCancellable to manage subscriptions. Sink and assign operators return cancellables that must be retained. Releasing or explicitly canceling a cancellable cancels the subscription. The store method adds cancellables to collections for batch management.

A common pattern stores cancellables in a Set on the owning object. When the object deinitializes, the set releases its cancellables, canceling all subscriptions. This ties subscription lifetime to object lifetime.

Flow subscriptions are managed through coroutine cancellation. A collection running in a coroutine scope cancels when the scope cancels. Lifecycle-aware collection in Android automatically cancels when lifecycle ends. This integrates naturally with structured concurrency.

The repeatOnLifecycle function in Android collects flows only while lifecycle is in specified states. Collection stops when lifecycle drops below threshold and restarts when returning. This prevents flow collection in inappropriate states without manual management.

iOS equivalent patterns use Combine's sink with cancellable storage in view controllers. The cancellables cancel on deinit. SwiftUI views use onReceive or onChange to observe publishers with automatic lifetime management.

## Platform Integration Patterns

Both frameworks integrate with their platform's UI patterns for reactive state management.

Combine integrates with SwiftUI through observable objects. Classes conforming to ObservableObject can use Published property wrappers. Changes to published properties emit through objectWillChange, triggering SwiftUI view updates. This enables reactive model objects driving declarative UI.

CurrentValueSubject provides imperative control over values with current value access. PassthroughSubject provides pure event streams without retained values. These enable adapting various patterns to Combine streams.

UIKit integration uses sink to subscribe to publishers and update UI in the received values. KVO observation can be wrapped in Combine publishers. Notification center observations have Combine equivalents. These bridges enable using Combine with imperative UI code.

Flow integrates with Jetpack Compose through collectAsState. A state flow or regular flow collected as state provides Compose state that triggers recomposition when values change. This creates reactive data binding from flow to UI.

StateFlow serves as the preferred state container for view models in Android. The view model exposes state flow, and the UI collects it as compose state. Updates to the underlying state flow propagate through collection to UI recomposition.

Android LiveData can interoperate with Flow through asFlow and asLiveData extensions. This enables gradual migration between patterns and integration with code using either approach.

## Cross-Platform Reactive Patterns with Flow

Kotlin Flow works in shared KMP code because coroutines are multiplatform. Flow defined in common code works on both Android and iOS targets, making Flow a natural choice for shared reactive streams.

Android consumes shared flows directly using standard collection patterns. ViewModels can expose shared flows, and UI can collect them with lifecycle awareness. No adaptation is needed.

iOS consumption requires bridging Flow to Combine or Swift async sequences. Without tooling, this involves creating callbacks that forward flow emissions to Combine subjects. With SKIE, flows appear as Swift AsyncSequence, enabling for await consumption or conversion to Combine publishers.

The SKIE approach provides natural Swift integration. A shared flow becomes an AsyncSequence in Swift. Async iteration with for await consumes values. Cancellation propagates appropriately. This enables Swift code that feels native while powered by shared Flow definitions.

Without SKIE, manual bridging creates wrapper functions that take callbacks, start coroutines to collect flows, and invoke callbacks with emissions. These wrappers work but add boilerplate and require careful cancellation handling.

State management patterns that work across platforms often use StateFlow in shared code. The view model pattern with StateFlow holding UI state works naturally. Android collects directly. iOS bridges to observable patterns appropriate for SwiftUI or UIKit.

## Error Handling Strategies

Stream errors require explicit handling strategies that differ between frameworks.

Combine errors propagate through the stream and terminate it. A publisher that emits an error stops emitting. Downstream operators see the error through completion. The failure type is part of the publisher signature, with Never indicating infallibility.

Error handling operators transform errors. Catch replaces the error with a recovery publisher. ReplaceError substitutes a specific value for errors. Retry attempts the stream again on error. MapError transforms error types.

Type system enforcement in Combine requires error types to match when combining publishers. Publishers with different failure types must be adapted before combination. This catches error handling omissions at compile time but adds complexity.

Flow errors propagate as exceptions through the coroutine system. A flow that throws stops emitting. Collection fails with the exception. The exception model is familiar to Kotlin developers but less explicit than typed errors.

Flow catch operator handles errors. The catch block receives the exception and can emit recovery values. Upstream errors are caught; downstream and collection errors are not. Multiple catch operators handle errors at different points.

Retry in Flow uses retry operator that re-collects from the beginning on error. RetryWhen provides conditional retry with access to the exception. These enable resilient collection strategies.

Cross-platform code should document error behaviors clearly. Kotlin exceptions are not visible in function signatures. Swift code using bridged flows needs documentation about potential failures. Typed result values can make success and failure explicit.

## Testing Reactive Streams

Testing reactive code requires verifying emission sequences, timing, and error handling.

Combine testing uses Publishers.TestScheduler to control timing. Tests can advance virtual time to trigger debounces and timeouts. XCTest expectations can verify expected emissions. Publishers that complete quickly can be collected synchronously in tests.

The recorded property on some publishers provides emission history for verification. Testing publishers with finite known output can compare recorded values against expectations.

Flow testing uses runTest with virtual time. The TestScope controls time advancement. Turbine library provides fluent flow testing with expectations for emissions, errors, and completion.

Testing cold flows is straightforward because collection triggers execution. Tests collect and verify results. Hot flows require more setup to ensure subscribers are ready before emissions.

Testing timing-dependent behavior like debouncing uses virtual time. Advancing time past debounce thresholds triggers expected emissions. Tests run quickly despite testing long durations.

Both platforms benefit from injecting flows and publishers as dependencies. Production code observes injected streams. Tests provide test streams with controlled emissions. This enables unit testing of reactive logic without testing the actual data sources.

## Conclusion

Combine and Flow represent mature reactive stream solutions for their respective platforms. Both enable modeling asynchronous data as streams, transforming those streams with operators, and consuming results reactively. The core concepts translate directly between frameworks.

Key differences include cold versus hot defaults, error type handling, and platform integration. Flow's cold default matches its coroutine foundation and provides predictable independent execution. Combine's hot defaults reflect iOS patterns where publishers often represent ongoing system state.

Cross-platform development benefits from Flow's multiplatform nature. Shared code can define reactive streams in Flow. Android uses those streams directly. iOS bridges to Combine or async sequences through SKIE or manual wrappers. This enables sharing reactive business logic while maintaining platform-native consumption patterns.

Understanding both frameworks enables effective cross-platform architecture. Shared reactive patterns can be designed that work naturally with both platforms' idioms. Platform-specific consumption adapts shared streams to each platform's conventions. The result is shared logic with native feel on each platform.
