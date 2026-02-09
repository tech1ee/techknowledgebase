# Practical Memory Patterns: Porting Code Between iOS and Android

Translating memory management patterns between iOS and Android requires more than mechanical code conversion. The underlying memory models differ so fundamentally that patterns which work naturally on one platform may fail subtly on the other. This document examines practical patterns for managing memory correctly on both platforms, with particular attention to cross-platform code that must work under both reference counting and garbage collection.

## Understanding Ownership Semantics Across Platforms

Ownership in iOS development is explicit and enforced. Every reference is either strong, which keeps the target alive, weak, which does not keep the target alive and becomes nil when the target is deallocated, or unowned, which does not keep the target alive and assumes the target outlives the reference. The compiler tracks these relationships and enforces them through the type system.

Ownership in Android development is implicit and managed by the garbage collector. All references are essentially strong in the sense that they keep objects reachable for garbage collection purposes. The concept of weak references exists through explicit WeakReference wrapper classes, but their use is opt-in rather than required by the type system. The garbage collector handles cycles automatically, so the primary reason for weak references is not cycle breaking but rather allowing objects to be collected while maintaining a reference that might be used if the object survives.

When porting iOS code to Android, explicit ownership annotations should be removed since they have no equivalent. Strong references remain references. Weak references should be replaced with explicit WeakReference wrappers if the weak semantics are actually needed, but often they were used only to break cycles which Android handles automatically. Unowned references have no direct equivalent and typically become normal references with appropriate lifecycle management.

When porting Android code to iOS, the absence of ownership annotations creates challenges. Every reference must be analyzed to determine appropriate ownership. References that participate in potential cycles must be carefully annotated. Callbacks and delegates require particular attention since they commonly create cycles that garbage collection handles silently but reference counting does not.

## The Delegate Pattern Across Platforms

Delegates represent one of the most common patterns that differ significantly between platforms. On iOS, delegates are typically weak references because the delegating object should not keep its delegate alive. The delegate pattern creates a potential cycle when the delegate holds a reference to the delegating object while the delegating object holds a reference to its delegate.

Consider a network manager that uses a delegate for callbacks. On iOS, the network manager holds a weak reference to its delegate. When the delegate is deallocated, the weak reference becomes nil, and subsequent callbacks simply do nothing. This pattern safely breaks the potential cycle where the delegate holds a strong reference to the network manager as a property.

On Android, this same pattern requires different thinking. The potential cycle exists in the reference graph but does not prevent garbage collection because the collector handles cycles. However, maintaining a reference to a deallocated delegate is not a concern since objects are not deallocated while references exist. The concern shifts to maintaining references to objects that should have been released, such as holding a reference to an Activity that has been destroyed.

Porting the delegate pattern from iOS to Android often means removing the weakness. The delegate reference can be a normal reference because cycles do not cause memory leaks. However, the pattern must still be designed to clear the delegate reference at appropriate lifecycle points. When an Activity is destroyed, anything holding a reference to that Activity should release it. This is not about memory leaks from cycles but about preventing use of destroyed UI components.

Porting the delegate pattern from Android to iOS requires adding weakness. Every delegate relationship that could create a cycle needs a weak reference. Missing a single weak annotation can create a memory leak that persists for the application's lifetime. Delegates should declare their delegate properties as weak, and any callbacks that store closures need capture lists specifying weak or unowned captures.

For Kotlin Multiplatform code, the delegate pattern requires abstraction. The shared layer defines interfaces for delegates but cannot specify ownership. Platform-specific code that uses these interfaces must apply appropriate ownership semantics. iOS implementations should use weak references where appropriate. Android implementations can use normal references but must manage lifecycle appropriately.

## Closure Capture Semantics

Closures on iOS capture references to external variables, and the ownership of those captures matters critically for memory management. By default, closures capture strong references. If a closure captures self and is stored in a property of self, a reference cycle exists. The closure keeps self alive, and self keeps the closure alive.

The solution is capture lists that specify how variables should be captured. Capturing weak self means the closure holds a weak reference that becomes nil if self is deallocated. Capturing unowned self means the closure assumes self will remain alive and crashes if that assumption is violated. The choice depends on whether the closure might outlive self and whether crashing on invalid access is acceptable.

Closures on Android through Kotlin lambdas capture references similarly, but the ownership implications differ. All captures are strong in the garbage collection sense, but cycles do not prevent collection. The concern is not memory leaks but rather accessing objects after their useful lifetime has ended. A lambda that captures an Activity reference might execute after the Activity is destroyed, attempting to update views that no longer exist.

Porting closure-heavy code from iOS to Android often means removing capture lists since they have no equivalent. However, the code may need lifecycle checks that were unnecessary on iOS. On iOS, if self is captured weakly and is nil when the closure executes, the closure simply does nothing. On Android, the equivalent pattern checks whether the captured object is still in a valid state before attempting to use it.

Porting closure-heavy code from Android to iOS requires adding capture lists everywhere closures are stored. Each closure must be analyzed to determine whether its captures could create cycles. Closures passed as immediate arguments to functions that do not store them usually do not need weak captures, but closures stored in properties or collections almost always do.

For cross-platform code, closures present a challenge because Kotlin has no equivalent to Swift capture lists. Shared code that passes callbacks to platform-specific code must document ownership expectations. iOS implementations must use appropriate capture lists when implementing callbacks. Android implementations must check object validity when executing callbacks.

## Object Pools and Reuse Patterns

Object pooling reduces allocation overhead by reusing objects rather than creating new ones. The pattern exists on both platforms but with different motivations reflecting different memory management costs.

On iOS, object pooling reduces retain and release overhead. Every object creation involves allocation plus at least one retain when the reference is assigned. Every object release involves at least one release plus potential deallocation. For objects created frequently in tight loops, this overhead accumulates. Pooling allows reusing existing objects, avoiding the allocation and deallocation costs.

On Android, object pooling reduces garbage collection pressure. Every object allocation eventually requires collection. Frequent allocations in performance-critical code paths generate garbage that triggers collection, potentially causing pauses at inopportune moments. Pooling reduces the allocation rate, reducing collection frequency and the chance of a pause during critical operations.

The implementation differs between platforms. iOS pools can rely on deterministic object lifetime. When an object is returned to the pool, it is available immediately for reuse. The reset logic runs synchronously before the object is placed back in the pool. iOS pools typically use arrays or linked lists with explicit acquire and release methods.

Android pools must account for the lack of deterministic timing. Objects returned to the pool might not be immediately reusable because finalization or other cleanup has not completed. Android pool implementations often use ArrayDeque or similar concurrent collections. The pool checks object state before providing an object to a requester, potentially discarding objects that are not in a clean state.

For cross-platform pooling in KMP, the shared layer defines the pooling interface while platform implementations provide the actual pooling logic. The interface specifies acquire and release semantics. The iOS implementation can assume synchronous cleanup. The Android implementation must handle potential asynchronous cleanup or require explicit cleanup before return.

## Managing Long-Lived Caches

Caches that store objects for extended periods present memory management challenges on both platforms, but the challenges differ.

On iOS, caches must be careful about ownership. If a cache holds strong references to its contents, those contents remain alive regardless of whether anything else needs them. This might be the desired behavior for frequently accessed data, but for large or numerous objects, it can consume excessive memory. Using NSCache provides automatic eviction under memory pressure, but custom caches need explicit eviction policies.

The cache should also consider what else references the cached objects. If callers receive objects from the cache and hold their own strong references, the objects remain alive even after cache eviction. This might be desirable, allowing callers to keep using objects they obtained, or undesirable, preventing memory reclamation. Clear ownership documentation helps callers understand their responsibilities.

On Android, caches interact with the garbage collector differently. Strong references in a cache keep objects reachable and alive, just as on iOS. However, Android provides SoftReference and WeakReference alternatives that allow the garbage collector to reclaim objects while the cache maintains a reference.

SoftReference keeps objects alive until memory pressure requires their collection. This is ideal for caches because objects remain available while memory is plentiful but can be reclaimed when the system needs memory. The cache checks whether the referenced object still exists before returning it, loading fresh data if the object was collected.

WeakReference allows collection at any garbage collection cycle regardless of memory pressure. This is less suitable for caches where the goal is to keep objects available, but useful for tracking objects without preventing their collection.

Porting iOS caches to Android should consider soft references for memory-sensitive caches. The NSCache behavior of automatic eviction under memory pressure maps conceptually to soft reference behavior, though the exact timing differs.

Porting Android caches to iOS requires implementing the eviction behavior explicitly if soft reference semantics were relied upon. iOS has no soft references. Caches must implement their own memory pressure responses through didReceiveMemoryWarning notifications or explicit size limits.

Cross-platform caches in KMP typically define platform-specific cache implementations rather than sharing implementation. The interface defines caching semantics while implementations use platform-appropriate mechanisms.

## Timer and Scheduled Task Patterns

Timers create classic memory management challenges because they typically hold references to their targets while running on system scheduler threads.

On iOS, timers hold strong references to their targets by default. A repeating timer that targets self keeps self alive as long as the timer is scheduled, regardless of whether other references to self exist. This can prevent view controllers from being deallocated when dismissed because their timers maintain strong references.

The solution is to invalidate timers before the target should be deallocated. The timer should be invalidated in appropriate lifecycle callbacks, not in deinit, because deinit will not be called while the timer holds a strong reference. Using closures with weak captures or block-based timer APIs can help by allowing the timer to continue without keeping its target alive.

On Android, timers through Handler, Timer, or coroutine delays do not prevent garbage collection of their targets because cycles are handled automatically. However, timers can still cause problems by executing after their target is destroyed. A timer that updates UI on a destroyed Activity causes exceptions or undefined behavior.

The solution is lifecycle-aware scheduling. Timers should be cancelled in appropriate lifecycle callbacks. LifecycleObserver patterns can automate this. Coroutine scopes tied to lifecycle automatically cancel scheduled work when the lifecycle ends.

Porting timer code from iOS to Android means removing the concern about retention but adding the concern about post-destruction execution. The timer no longer keeps its target alive, so target lifetime must be managed through other means, typically lifecycle callbacks that cancel the timer.

Porting timer code from Android to iOS means adding the concern about retention. Timers that worked correctly on Android might create retention cycles on iOS. Each timer must be analyzed to ensure it does not prevent deallocation of its target.

Cross-platform timer abstractions should provide lifecycle integration. The shared layer can define timer interfaces. Platform implementations hook into appropriate lifecycle mechanisms. iOS implementations ensure timers do not prevent deallocation. Android implementations ensure timers cancel when their lifecycle scope ends.

## Observable and Subscription Patterns

Reactive patterns with observables and subscriptions create long-lived references that require careful management on both platforms.

On iOS, subscribing to an observable typically involves providing a closure that handles emitted values. That closure captures references, and if it captures self while the subscription is stored on self, a cycle exists. The subscription keeps the closure alive, the closure keeps self alive, and self keeps the subscription alive.

The solution is weak captures in subscription closures combined with explicit subscription disposal. RxSwift and Combine both provide mechanisms to manage subscription lifetime. DisposeBag and AnyCancellable collections automatically dispose subscriptions when the bag or collection is deallocated. Combined with weak captures, this ensures that subscriptions do not prevent their observers from being deallocated.

On Android, subscriptions have different challenges. The cycle concern is reduced because garbage collection handles cycles, but lifetime management remains important. A subscription that emits on the main thread after its observer's Activity is destroyed causes problems. RxJava and Kotlin Flow provide scope-based subscription management that cancels subscriptions when scopes end.

Porting reactive code from iOS to Android means removing weak captures but ensuring lifecycle-scoped subscription management. The subscription should be tied to an appropriate scope, typically a ViewModel scope or lifecycle scope, that ensures cancellation at the appropriate time.

Porting reactive code from Android to iOS means adding weak captures and ensuring disposal. Every subscription closure that might create a cycle needs weak captures. Subscriptions should be collected in disposal containers that are disposed at appropriate lifecycle points.

Cross-platform reactive code with Kotlin Flow requires bridging to platform reactive patterns. SKIE provides Swift-friendly Flow consumption. Android can use Flow directly or bridge to RxJava. The shared layer emits Flow, and platform code consumes appropriately with lifecycle awareness.

## Static and Singleton References

Static references and singletons present memory management considerations that differ between platforms.

On iOS, static variables hold strong references that persist for the application lifetime. Objects referenced statically are never deallocated through reference count reaching zero. This is sometimes desirable for true singletons but problematic when static references inadvertently capture view controllers or other objects that should have bounded lifetimes.

The solution is careful design of what static references hold. Singletons should be genuinely application-lifetime objects. Static references should not hold or indirectly capture UI components. Weak static references can track objects without preventing their deallocation, useful for debugging or loose coupling.

On Android, static references similarly keep objects reachable for the application lifetime. The additional concern is that static references to Context or UI components can leak those components. An Activity stored in a static variable will never be garbage collected even after it is destroyed, wasting memory and potentially causing bugs if the static reference is used.

The solution is to avoid static references to Context and UI components entirely or to use Application context when a context is needed statically. WeakReference can be used when static code needs to access an Activity that might be destroyed, checking whether the reference is still valid before use.

Porting static patterns between platforms requires attention to what those statics reference. iOS code that works correctly might have subtle static references that cause leaks on Android. Android code that correctly avoids static context references might add them inadvertently when ported to iOS where the concern seems less pressing.

Cross-platform singletons should be application-lifetime objects only. They should not hold references to platform-specific components with bounded lifetimes. Any registration patterns where platform components register with shared singletons must include corresponding unregistration at appropriate lifecycle points.

## Debugging Memory Issues in Cross-Platform Code

Memory debugging in cross-platform codebases requires understanding where issues might originate and using appropriate tools for each platform.

Leaks that appear on iOS but not Android typically involve reference cycles. The shared Kotlin code might store callbacks that on iOS create cycles through closure captures. The solution is analyzing the reference graph on iOS to identify the cycle and modifying either the shared code to support weak references or the iOS-specific code to break the cycle.

Leaks that appear on Android but not iOS typically involve static references or registrations without corresponding unregistration. The shared code might register listeners that are never unregistered. The solution is ensuring every registration has a corresponding unregistration tied to appropriate lifecycle events.

Memory growth that appears on both platforms might indicate actual logic issues in shared code, such as collections that grow without bounds or caches without eviction. These issues manifest similarly on both platforms because they do not depend on memory management differences.

Testing shared code for memory correctness should include tests on both platforms. A test class that creates objects, performs operations, and then verifies objects are released catches many issues. On iOS, checking that deinit is called confirms no retention. On Android, forcing garbage collection and checking object finalization or weak reference clearing confirms no unexpected retention.

## Conclusion

Memory management patterns require adaptation when moving between iOS and Android. The fundamental difference, deterministic reference counting versus non-deterministic garbage collection, means that patterns which work correctly on one platform may fail on the other. Ownership semantics are explicit and enforced on iOS but implicit and unenforced on Android. Cycles are dangerous on iOS but harmless on Android. Lifecycle management matters on both platforms but for different reasons.

Effective cross-platform development requires understanding both models thoroughly. Developers should recognize when iOS-specific ownership patterns are needed and when Android-specific lifecycle management is needed. Shared code should be designed to work under both models, avoiding assumptions that only hold on one platform.

The practical patterns covered here, delegates, closures, pools, caches, timers, observables, and statics, appear in nearly every mobile application. Handling them correctly across platforms requires conscious attention to the differences in memory management models. This attention, developed through understanding and practice, enables building applications that are memory-correct on both platforms rather than coincidentally working on one while leaking on the other.
