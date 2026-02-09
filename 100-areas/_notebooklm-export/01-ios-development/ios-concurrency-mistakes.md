# Common iOS Concurrency Mistakes and How to Avoid Them

Concurrency is one of the most challenging aspects of iOS development, and even experienced developers regularly make subtle mistakes that lead to crashes, data corruption, and hard-to-reproduce bugs. Understanding these common pitfalls, why they occur, and how to avoid them is essential for building reliable, performant applications.

## The Race Condition: When Order Matters But Isn't Guaranteed

Race conditions represent perhaps the most insidious category of concurrency bugs. They occur when multiple threads access shared mutable state without proper synchronization, and the final result depends on the unpredictable timing of thread execution. The same code might work perfectly a thousand times, then fail catastrophically on the thousand-and-first execution when threads happen to interleave differently.

Imagine a bank account class with a balance property. Two withdrawals of fifty dollars happen simultaneously from different threads. Both threads read the balance as one hundred dollars, both check that sufficient funds exist, both subtract fifty from what they read, and both write back fifty as the new balance. The account should have zero dollars, but instead has fifty—one withdrawal effectively disappeared.

Why is this so dangerous? Because race conditions are non-deterministic. They might never occur during development on your fast Mac with good network conditions. They might appear only on older devices under heavy load when thread scheduling changes. They might happen only in production under specific user interaction patterns. Testing doesn't reliably catch them, making prevention through correct design essential.

The fundamental solution is mutual exclusion—ensuring only one thread accesses the shared state at any moment. In modern Swift, actors provide the safest approach. Mark your account class as an actor, and the compiler enforces that all access happens serially through the actor's isolation. No manual locking, no forgotten synchronization, just compile-time guaranteed safety.

For GCD-based code, serial queues provide mutual exclusion. Create a private serial queue for the account, and dispatch all balance modifications to that queue. The queue serializes access automatically, preventing interleaving. This is less safe than actors because the compiler doesn't enforce queue usage, but it works reliably when applied consistently.

The subtle version of race conditions involves seemingly atomic operations that aren't actually atomic. Incrementing an integer feels like one operation, but at the CPU level it's three—read the current value, add one, write the new value. Two threads incrementing simultaneously can both read the same value, both increment it, both write the same result, and one increment is lost. Even simple counters need synchronization if accessed from multiple threads.

## Blocking the Main Thread: The UI Freeze

Users expect instant responsiveness—tap a button, see immediate feedback. When you block the main thread for even a few hundred milliseconds, users notice. Block it for seconds, and the app feels broken. The watchdog might even kill your app for being unresponsive. Yet blocking the main thread is one of the most common iOS programming mistakes.

Why does this happen so often? Because it's easy. Network requests, file I/O, database queries, complex computations—they're all naturally expressed as synchronous operations. The code reads linearly, errors propagate through throws, return values come back directly. Asynchronous code is more complex, requiring callbacks, error handling in multiple places, and managing state across async operations.

But the cost of blocking the main thread is severe. While your synchronous network request waits for a response, the run loop can't process events. Touch events queue up unprocessed. Animations freeze mid-frame. The app appears hung. If this continues for several seconds, iOS decides your app is unresponsive and terminates it. Users lose their work and gain frustration.

The canonical mistake is calling a synchronous API directly from a button tap handler. The user taps login, your handler calls a synchronous login API, and the UI freezes for however long authentication takes. On fast connections with responsive servers, maybe one second—noticeable but tolerable. On slow connections or during server issues, ten seconds or more—completely unacceptable.

The solution is always moving heavy work to background queues. Dispatch async to a global queue, perform the operation there, then dispatch async to the main queue only for UI updates. Or use async/await, marking your network code async and calling it from async contexts. The main thread stays responsive, processing events and updating UI, while background threads handle time-consuming work.

One subtlety: some operations you might expect to be fast are actually slow. Reading a file might hit network storage on iCloud Drive. Database queries might scan large tables. Image decoding might process megapixel photos. Even operations that seem instant can block long enough to cause jank. When in doubt, profile with Instruments or add main thread assertions to catch violations during development.

## The Deadlock: Waiting on Yourself

Deadlocks are concurrency errors where execution can never proceed because each participant is waiting for another, forming a cycle. The simplest deadlock is calling sync on a serial queue you're already executing on—you wait for the queue to become available, but you're the thing making it busy. Instant and total freeze.

The classic example happens on the main queue. You're already on the main thread, perhaps in a button handler or view lifecycle method. You dispatch sync to the main queue for some reason—perhaps trying to ensure code runs on the main thread, not realizing you're already there. The sync call blocks waiting for the main queue to become available. But the main queue is busy executing the code that called sync. Neither can proceed.

Less obvious deadlocks involve multiple queues or locks. Thread A holds lock X and waits for lock Y. Thread B holds lock Y and waits for lock X. Neither can proceed—classic deadlock. With queues, thread A might dispatch sync to queue Q1 which dispatches sync to queue Q2 which dispatches sync back to Q1. The circular dependency creates deadlock.

Preventing deadlocks requires understanding your synchronization graph. Which queues or locks do you hold while waiting for others? Can a cycle form? If queue A ever waits for queue B, queue B must never wait for queue A. This ordering discipline prevents cycles.

For simple cases, the solution is using async instead of sync. Async doesn't wait, so it can't deadlock. If you need a return value, restructure to use completion handlers or async/await. Sync has legitimate uses—like protecting shared state with a serial queue—but should be used cautiously and with clear understanding of the current execution context.

Testing can catch some deadlocks, but like race conditions, they're often non-deterministic. The deadlock might depend on specific timing—thread scheduling, CPU load, number of concurrent operations. Preventing deadlocks through correct design is more reliable than hoping to catch them in testing.

## Priority Inversion: When High Priority Waits on Low Priority

Priority inversion is a subtle concurrency problem where high-priority work ends up waiting for low-priority work to complete, effectively running at the low priority. This can cause UI responsiveness issues and missed deadlines in time-sensitive operations.

The scenario works like this: a background task acquires a lock, perhaps protecting a shared cache. Before releasing the lock, the task is preempted by a medium-priority task that runs for a while. Meanwhile, a high-priority UI task tries to acquire the same lock and blocks. The high-priority task waits for the background task to release the lock, but the background task can't run because the medium-priority task keeps the CPU busy. The high-priority task effectively runs at background priority, creating UI jank.

GCD mitigates priority inversion through priority inheritance. When a high-priority task blocks on a queue, GCD temporarily raises that queue's priority until the blocking work completes. The background task gets boosted to high priority, runs to completion, releases whatever the high-priority task needs, then returns to normal priority. This automatic boosting prevents most priority inversion without any code changes.

But priority inheritance can't solve all cases. If you use manual locks like NSLock instead of GCD queues, the system doesn't know about the dependency and can't boost priorities. If the dependency chain is complex—task A waits for task B which waits for task C—priority inheritance might not propagate through all the links.

The solution is using GCD's abstractions instead of manual locks when possible. Serial queues for mutual exclusion automatically participate in priority inheritance. Async/await with actors similarly handles priority correctly through the Swift runtime. Manual locks should be a last resort for performance-critical code where their overhead is unacceptable.

Quality of service matters here too. If you're inconsistent about QoS—marking some tasks with appropriate priorities but leaving others at default—you create scenarios where important work waits on unimportant work. Be deliberate and consistent with QoS to give the system the information it needs to schedule intelligently.

## Thread Explosion: Too Many Threads

Thread explosion occurs when you create far more threads than the system can efficiently manage. Each thread consumes memory for its stack, requires CPU time for context switching, and competes for scheduler attention. Creating too many threads makes everything slower despite the apparent parallelism.

The classic cause is loops that create concurrent operations. You have a thousand items to process, you iterate over them creating one async operation per item, and GCD creates many threads to run them. Soon you have hundreds of threads all trying to execute simultaneously on an eight-core CPU. The overhead of managing those threads exceeds the benefit of parallelism.

Why doesn't GCD prevent this? It does limit thread creation, but within broad bounds. GCD's thread pool can grow quite large before it stops creating threads. And once threads are created, they don't immediately disappear when work completes—they stick around for a while in case more work arrives. So a burst of many concurrent operations can grow the thread pool significantly.

The symptoms of thread explosion include high memory usage—each thread's stack consumes 512 kilobytes to a megabyte. CPU usage appears high but actual throughput is low because the system spends more time context switching than doing useful work. The debugger shows dozens or hundreds of threads, many of them blocked waiting for their turn to run.

The solution is limiting concurrency explicitly. Use operation queues with maximum concurrent operation counts, typically set to the number of CPU cores for CPU-bound work. Use semaphores to cap how many operations run simultaneously. Use async/await task groups which limit parallelism automatically based on system resources.

For I/O-bound work where threads spend most time waiting, higher concurrency makes sense—perhaps twice the number of CPU cores. But for CPU-bound work, more threads than cores just wastes resources. Measure and tune based on actual performance rather than assuming more concurrency is always better.

## Forgetting to Dispatch UI Updates to the Main Thread

UIKit is not thread-safe, and all UI updates must happen on the main thread. Violating this causes crashes, visual glitches, and undefined behavior. Yet forgetting to dispatch UI updates to the main thread is remarkably common, especially when async operations complete on background threads.

The typical scenario: you perform a network request on a background queue, the completion handler executes on that same background queue, and you update UI directly from the completion handler. In debug builds with Main Thread Checker enabled, you get a runtime warning. In release builds, you might get lucky and it works anyway—UIKit sometimes tolerates violations—or you might get crashes or weird UI artifacts.

Why does this mistake persist? Because it often appears to work. The crash or glitch might not happen every time. The warning appears in the console, but the app continues running. Developers in a hurry see the warning, note that everything seems fine, and move on. Later, in production with different timing, the violation causes a crash that's hard to reproduce and debug.

The solution is discipline and tooling. Always use Main Thread Checker during development. Treat its warnings as errors—fix them immediately rather than letting them accumulate. Create helper functions that check if you're on the main thread and dispatch if needed, reducing the boilerplate of manual checks.

With async/await, MainActor makes this safer. Mark your view model or view controller with MainActor, and all methods automatically execute on the main thread. The compiler enforces this—accessing MainActor-isolated state from other actors requires await, automatically hopping to the main thread. You can't accidentally update UI from a background thread because the compiler prevents it.

For legacy code using callbacks, the pattern is consistent: perform work on background queues, dispatch to main queue for UI updates. If a callback might execute on any thread, defensively dispatch to main before touching UI. The small overhead of potentially dispatching when you're already on main is negligible compared to the cost of a main thread violation.

## Retain Cycles in Async Closures

Closures capture references to self by default, and if those closures are stored or execute asynchronously, they can create retain cycles preventing memory release. This is a general Swift problem, not specific to concurrency, but async closures make it particularly common and problematic.

Consider dispatching an async block that captures self. The block references self strongly. You store the block or the cancellable token in a property of self. Now self owns the block and the block owns self—a retain cycle. Self will never deallocate, leaking memory and potentially resources like file handles or network connections.

The symptoms are subtle. Memory usage grows over time as leaked objects accumulate. View controllers don't deinit when you expect them to. Navigation back doesn't actually release the previous screen. But there's no crash, no obvious error, just a slow memory leak that's hard to track down.

The solution is weak or unowned self captures. In the closure capture list, specify weak self, then use guard let or if let to unwrap. If self deallocates before the closure executes, the guard fails and the closure exits early. No crash, no forced unwrapping of nil, just graceful abandonment.

When should you use weak versus unowned? Weak is safer—it becomes nil if the object deallocates, and you handle that explicitly. Unowned assumes the object will outlive the closure and crashes if it doesn't. Use weak unless you're absolutely certain the object can't deallocate before the closure completes. The tiny overhead of checking for nil is usually worth the safety.

With async/await, the problem persists but looks different. Task closures capture self, and if you store the task reference in self, you create a cycle. The solution is the same—capture self weakly in the task closure. Or design so tasks don't need to reference their creating object after starting, breaking the cycle structurally.

SwiftUI and Combine pipelines stored in properties also risk retain cycles. The sink closure references self to update state, and you store the cancellable in self. Weak self captures prevent the cycle, or you can restructure to use assign instead of sink, which doesn't require closures.

## Data Races with Actors

Actors prevent data races within their isolated state, but they don't prevent all data races in code using actors. If you pass mutable reference types into or out of actors, those objects can be accessed unsafely from multiple actors simultaneously.

The subtlety is that actor isolation protects the actor's properties, not objects those properties reference if those objects are shared elsewhere. Imagine an actor with an array property. The property itself is protected—access is serialized. But if you return the array to a caller, and the array contains mutable objects, those objects might be shared between the actor and the caller. Both might modify the objects simultaneously—data race.

Swift 6's Sendable checking addresses this by requiring types that cross actor boundaries to be Sendable—either value types, immutable reference types, or other actors. Non-Sendable types can't be passed between actors without triggering compiler errors. This catches the data race at compile time rather than runtime.

But Sendable checking can be bypassed with unsafe conformances or disabled with compiler flags during migration. If you're not yet fully strict about Sendable, you can still create data races with actors by passing shared mutable objects.

The solution is discipline about Sendable. Enable strict checking and fix compiler errors rather than bypassing them. When you must pass reference types, either make them immutable, create copies, or implement internal synchronization making them Sendable. Don't assume actor isolation magically makes everything thread-safe—it protects the actor's properties, not necessarily the objects they reference.

Another actor pitfall is assuming state doesn't change across suspension points. Inside an actor method, you read a property, then await something, then use the property again. During the await, other calls to the actor might run and modify that property. The value you read before the await might not match the value after. Capture the value in a local variable if you need it consistent across suspensions.

## Misunderstanding Task Cancellation

Task cancellation in Swift concurrency is cooperative, not preemptive, but this is easy to forget. Cancelling a task doesn't forcibly stop it. The task continues running until it checks for cancellation and exits voluntarily. Code that never checks for cancellation keeps running despite being cancelled.

The common mistake is cancelling a task and assuming the work stops immediately. You cancel a download task when the user navigates away, but the download continues consuming bandwidth and CPU because the code doesn't check cancellation. Or worse, the download completes and tries to update UI for a screen that no longer exists, causing crashes or memory leaks.

The solution is checking cancellation regularly in long-running operations. Call Task.checkCancellation to throw if cancelled, or check Task.isCancelled for manual handling. Do this at least between loop iterations, before expensive operations, and after suspension points.

Some APIs check cancellation automatically. URLSession's async methods abort when the task is cancelled. FileHandle async reads check cancellation. But your own computation loops or processing pipelines need explicit checks. Don't assume cancellation propagates without your cooperation.

Another subtlety: child tasks are automatically cancelled when parents cancel, but they still need to check and respond. Structured concurrency ensures the cancellation signal propagates through the task tree, but each task must respect the signal. A cancelled parent doesn't kill children; it asks them to stop.

For cleanup that must happen even when cancelled, use withTaskCancellationHandler. The handler executes when cancellation occurs, letting you clean up resources while the main work continues or exits. This is useful for releasing locks, closing files, or cancelling dependent operations.

## Holding Locks Across Await

Traditional locks don't compose well with async/await because await might suspend, and suspension releases the current thread, but locks are thread-local. If you acquire a lock, then await, the function might resume on a different thread, no longer holding the lock. Meanwhile, other code might acquire and release that same lock, violating the intended mutual exclusion.

This is one of the subtlest concurrency mistakes because it doesn't crash immediately and might even appear to work. The lock provides some synchronization, just not the synchronization you intended. Under specific timing, the race condition appears and you see data corruption or crashes.

The solution is actors instead of locks for async code. Actors are designed to work with suspension—their isolation survives across await. When an actor method awaits, the actor becomes available for other calls, then the original method resumes with isolation restored when the await completes.

If you must use locks with async code, never hold the lock across an await. Acquire the lock, read or write what you need into local variables, release the lock, then await. After the await, acquire the lock again if you need to write back. This is more complex but preserves the lock semantics.

Or restructure to avoid locks entirely. Async/await encourages different concurrency patterns than locks. Rather than protecting mutable state with locks, isolate it in actors. Rather than blocking on locks, await on actor calls. The language and runtime handle synchronization correctly without manual lock management.

## Unbalanced Dispatch Group Enters and Leaves

Dispatch groups coordinate multiple async operations, but they rely on balanced enter and leave calls. Every enter must have a corresponding leave, or the group never completes. Unbalanced calls create operations that appear to hang, never executing their notify handlers.

The typical mistake is conditional leave calls. You call enter unconditionally, perform an operation, and call leave in the success case but forget it in the error case. Now failures leave the group permanently incomplete. Your notify handler never executes, and any code waiting on the group waits forever.

Error handling makes this particularly tricky. Early returns, thrown errors, guard statements—all create code paths that might skip the leave call. You need to ensure every code path that entered the group also leaves it.

The solution is using defer. Call enter, then immediately defer the leave call. Defer executes when the scope exits, regardless of how it exits—normal return, thrown error, early return. This makes balancing automatic and prevents forgetting.

Alternatively, use the group parameter to async instead of explicit enter/leave. When you dispatch async with a group parameter, GCD automatically calls enter before executing the block and leave after it completes. This eliminates manual balancing entirely for standard dispatch cases.

For complex scenarios with conditional operations, consider whether dispatch groups are the right tool. Task groups in async/await might be simpler, with compiler-enforced structured concurrency preventing the unbalanced group problem entirely.

## Creating Too Many Tasks or Operations

Every task or operation has overhead—memory for the task structure, bookkeeping in the scheduler, potential thread creation. Creating thousands of tasks for a batch operation wastes resources and can degrade performance despite the apparent parallelism.

The naive approach to parallelizing a loop is creating one task per iteration. Process a thousand images, create a thousand tasks. This might create hundreds of threads, consume megabytes of memory, and actually run slower than a sequential approach due to overhead.

The solution is batching—processing multiple items per task. Create tasks equal to the number of CPU cores, and divide items evenly among them. Each task processes its batch sequentially. Now you have optimal parallelism without excessive overhead.

Operation queues with maximum concurrent operation counts automatically limit concurrency. Set the max to the number of CPU cores, add all operations, and the queue schedules them optimally. You don't manually batch; the queue manages it.

Task groups in async/await dynamically create child tasks, but they're still subject to overhead concerns. Creating thousands of child tasks for simple operations wastes resources. Consider whether parallelism actually helps—if each operation is very fast, the overhead might exceed the benefit.

Measure before optimizing. Sometimes creating many tasks works fine because the work per task is substantial enough that overhead is negligible. But if you see performance problems or memory pressure, consider batching. Profile with Instruments to see how many threads you're actually creating and whether you're spending more time on overhead than useful work.

## Assuming Async Means Parallel

A fundamental misconception is that async automatically means parallel. Calling an async function with await doesn't necessarily execute it in parallel with your current code. It might execute serially, just asynchronously, resuming your code after the async function completes.

Async means "might suspend," not "runs in parallel." An async function can execute entirely synchronously if its awaited operations complete immediately. Or it might suspend, letting other work run, then resume later. Whether that other work is your calling code continuing in parallel depends on the task structure.

Async let creates parallel execution—multiple async let bindings run concurrently. Task groups create parallel execution—child tasks run concurrently. But just calling await on an async function is sequential—wait for it to complete, then continue.

This matters for performance. If you await three network requests in sequence, they execute serially, taking the sum of their times. If you create async let bindings for all three, they execute in parallel, taking only the time of the slowest. The syntax differs, but more importantly, the execution model differs.

Understanding this prevents performance bugs where you expected parallelism but got serial execution. It also prevents bugs where you assumed serial execution but got parallelism and data races. Be explicit about whether you want concurrent or sequential execution, and use the appropriate async/await constructs.

## Not Testing Concurrency

Concurrency bugs are hard to test because they're often non-deterministic. The same code might work a thousand times, then fail on the thousand-and-first execution when timing aligns differently. But this doesn't mean you shouldn't test—it means you need different testing strategies.

Thread Sanitizer detects data races at runtime, instrumenting your code to track every memory access and flag when multiple threads access the same memory unsafely. Enable it in your scheme's diagnostics, run your app and tests, and address every race it reports. This catches real concurrency bugs that might otherwise only appear in production under load.

Stress testing with intentional delays reveals timing-dependent bugs. Add random sleeps in concurrent code, increasing the likelihood of problematic interleavings. Run operations many times in loops to increase the chance of hitting rare race conditions. This isn't foolproof, but it's better than hoping your normal test runs happen to catch concurrency bugs.

Unit tests for concurrent code should use expectations, waiting for async operations to complete before asserting results. Test both success and failure paths, ensuring errors propagate correctly and cleanup happens even when operations fail. Test cancellation explicitly, verifying that cancelled operations stop and release resources.

Integration tests under load surface concurrency bugs that unit tests miss. Simulate many concurrent users, heavy system load, or slow networks. Monitor for crashes, assertions, or data corruption. These tests are expensive to run but catch issues that only appear under production-like conditions.

Code review focusing on concurrency helps catch mistakes before they reach testing. Review every place shared mutable state is accessed, every sync dispatch, every closure capture. Check that actors are used correctly, that weak references prevent retain cycles, that cancellation is checked. A second pair of eyes catches mistakes the original developer missed.

## Debugging Concurrency Issues

When concurrency bugs do occur, debugging them requires different techniques than debugging sequential code. Stack traces show multiple threads, race conditions might not reproduce consistently, and the state causing the crash might differ from the state where the bug originated.

Xcode's Debug Navigator shows all threads and their current state. Pause execution and examine which threads are running, which are blocked, and what each is doing. Threads waiting on locks or semaphores show up clearly. Deadlocks usually show a cycle of threads waiting on each other.

Thread names help identify which threads are doing what. Set thread names with pthread_setname_np or Thread.current.name. When debugging with dozens of threads, names like "NetworkingQueue" or "ImageProcessing" are much more helpful than "Thread 47."

Logging is invaluable for concurrency debugging because it captures timing and ordering. Log when operations start and complete, when locks are acquired and released, when values change. When bugs occur, the logs show the sequence of events leading to the problem.

Assertions catch bugs early, before they cause visible failures. Assert that you're on the expected queue, that state is in expected ranges, that preconditions hold. In debug builds, these assertions crash immediately at the point of error rather than letting corruption propagate.

Instruments provides deep profiling of concurrent code. The Time Profiler shows where CPU time is spent across all threads. System Trace visualizes thread activity, showing which threads run when and where they block. The Allocations instrument tracks memory allocations across threads, helping debug leaks from retain cycles.

Understanding common concurrency mistakes, why they occur, and how to prevent them is as important as understanding concurrency primitives themselves. Code that never creates data races, never deadlocks, and handles cancellation correctly is robust and maintainable. Code that occasionally races, deadlocks under specific conditions, or leaks resources is fragile and expensive to maintain.

The good news is that modern Swift makes correct concurrent code easier than ever. Actors prevent data races through compile-time checking. Async/await makes control flow clear and linear. Structured concurrency ensures tasks complete or cancel together. These tools don't eliminate the need for understanding concurrency, but they catch many mistakes automatically that previously required careful manual verification.

As iOS development evolves, concurrency remains essential and challenging. Invest time in understanding these common mistakes and how to avoid them. Your apps will be more reliable, your users happier, and your debugging sessions shorter.
