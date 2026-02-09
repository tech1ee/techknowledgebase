# KMP iOS Interoperability: SKIE and Swift Integration

Kotlin Multiplatform produces native frameworks for iOS that Swift code can consume. However, the default interoperability experience has rough edges. Kotlin language features do not always translate naturally to Swift idioms. SKIE, developed by Touchlab, addresses these gaps by transforming Kotlin declarations into Swift-friendly forms. Understanding both the default interoperability and SKIE's enhancements enables building KMP frameworks that feel native to iOS developers.

## Default Kotlin to Swift Interoperability

The Kotlin Native compiler produces Objective-C frameworks from Kotlin code. Swift interoperates with Objective-C, so Swift can consume these frameworks. This two-step bridge works but introduces friction because Kotlin features must first map to Objective-C, then Swift interprets the Objective-C declarations.

Classes in Kotlin become classes in the generated framework. Swift can instantiate Kotlin classes and call their methods. Properties map to properties. Functions map to methods. Basic interoperability works without special effort.

However, many Kotlin features lack direct Objective-C equivalents. Suspend functions become functions with completion handlers. Flows become custom types requiring manual iteration. Sealed classes become class hierarchies without compiler-enforced exhaustiveness. Generics map imperfectly, sometimes requiring explicit casting. These gaps create friction for iOS developers consuming KMP frameworks.

The generated Objective-C headers influence how Swift sees Kotlin code. Naming conventions may differ from Swift idioms. Parameter labels may not match Swift expectations. Nullability annotations may not carry through perfectly. iOS developers working with KMP frameworks encounter unfamiliar patterns.

## Suspend Functions Without SKIE

Kotlin suspend functions are central to modern Kotlin async programming. They enable writing asynchronous code that reads like synchronous code. However, their translation to iOS is problematic without assistance.

By default, a suspend function becomes a function taking a completion handler. The function returns immediately. When the operation completes, the completion handler is called with the result or error. This pattern is familiar to iOS developers from older Objective-C code but has been superseded by async/await in modern Swift.

Using completion handler patterns in Swift code that otherwise uses async/await creates inconsistency. Developers must mix paradigms, using callbacks for KMP code and async/await for native Swift code. This context switching increases cognitive load and reduces code clarity.

Error handling compounds the issue. Kotlin exceptions must map to Objective-C errors, which Swift then interprets. The error types may not be what Swift developers expect. Handling errors from completion handlers requires different patterns than handling errors from async functions.

Cancellation support is also problematic. Swift async functions can be cancelled through task cancellation. Completion handler functions have no standard cancellation mechanism. Developers must implement custom cancellation if needed, adding complexity.

## SKIE Suspend Function Transformation

SKIE transforms suspend functions into Swift async functions. What appears in Kotlin as a suspend function appears in Swift as an async function. Swift developers use await to call these functions just like native Swift async functions.

This transformation preserves the programming model across the language boundary. Kotlin code uses suspend. Swift code uses async/await. The paradigms align, making KMP code feel native in Swift contexts.

Error handling maps to Swift throwing functions. Kotlin exceptions become Swift errors that can be caught with try/catch. The error handling pattern matches Swift conventions.

Cancellation propagates correctly. When a Swift task is cancelled, the underlying Kotlin coroutine cancels. When Kotlin throws CancellationException, Swift sees appropriate cancellation behavior. The cancellation semantics match what Swift developers expect.

The transformation happens in the framework generation process. Developers enable SKIE in their build configuration. SKIE processes the Kotlin code and generates enhanced Objective-C headers that Swift interprets as async functions. No runtime library is required for basic async support.

## Sealed Classes Without SKIE

Kotlin sealed classes provide exhaustive type hierarchies where the compiler verifies all subclasses are handled. This enables safe pattern matching through when expressions. The compiler ensures no cases are missed.

Without SKIE, sealed classes become ordinary class hierarchies in generated frameworks. Swift can see the base class and its subclasses, but Swift has no knowledge that these are the only subclasses. Switch statements over sealed class instances cannot be exhaustive because Swift does not know the hierarchy is closed.

This limitation affects code quality and safety. Kotlin code benefits from exhaustiveness checking. Swift code handling the same types lacks this checking. New subclasses added to the Kotlin sealed hierarchy would be silently unhandled in Swift code that thinks it covers all cases.

The workaround without SKIE involves maintaining parallel Swift enums or using default cases that should never execute. Neither approach is satisfying. Parallel enums require manual synchronization. Default cases hide potential bugs when hierarchies change.

## SKIE Sealed Class Transformation

SKIE transforms sealed classes into a form that enables exhaustive switching in Swift. The generated code includes an enum that mirrors the sealed hierarchy. Switch statements over this enum are exhaustive, with the compiler verifying all cases are handled.

The transformation provides onEnum helper functions that convert sealed class instances to the enum form. Swift code switches over the enum result, with access to the specific subclass inside each case. The pattern is slightly different from Kotlin's when but achieves the same exhaustiveness guarantee.

New sealed class subclasses cause Swift code to fail compilation until the new case is handled. This maintains the safety property across the language boundary. Changes to the Kotlin hierarchy surface as Swift compilation errors rather than runtime bugs.

The enum approach preserves type information. Inside each case, the full subclass type is available with all its properties and methods. The pattern enables safe decomposition of sealed hierarchies in Swift code.

## Flow Without SKIE

Kotlin Flow provides reactive streams built on coroutines. Flows emit multiple values over time, handle errors, and complete when done. The flow operators enable rich stream transformation. Flow is central to modern Kotlin data architecture.

Without SKIE, Flows become opaque types that Swift cannot easily consume. Collecting a flow requires starting a coroutine, which requires bridging from Swift to Kotlin's coroutine system. The ceremony is significant and the code unfamiliar to iOS developers.

Manual bridging typically involves creating Kotlin helper functions that accept Swift callbacks. These helpers start coroutines, collect flows, and invoke callbacks for each emission, completion, and error. The result works but requires boilerplate and does not feel native.

Combine integration requires additional bridging. Converting Flow to Combine Publisher involves creating intermediary types that forward emissions. Memory management and cancellation require careful attention. The integration code can be complex and error-prone.

## SKIE Flow Transformation

SKIE transforms Flows into Swift AsyncSequence. What appears as a Flow in Kotlin appears as an AsyncSequence in Swift. Swift code can iterate with for await, receiving each emission as it occurs.

This transformation aligns Flow with Swift's native async iteration pattern. The syntax matches how Swift developers work with other async sequences. No special knowledge of Kotlin patterns is required.

Error handling integrates with Swift patterns. Errors emitted by the flow become thrown errors during iteration. Swift code uses standard error handling patterns.

Cancellation propagates appropriately. When Swift code stops iterating, the underlying flow collection cancels. When the flow completes or errors, the Swift iteration ends. The lifecycle semantics match expectations.

SKIE also provides Combine integration. Flows can be accessed as Publishers for code that uses Combine patterns. Both consumption approaches are available, enabling gradual migration or mixed usage.

## Other SKIE Enhancements

SKIE provides additional improvements beyond the major transformations.

Default parameter support enables Kotlin functions with default parameters to be called from Swift without providing all parameters. Without SKIE, Swift sees all parameters as required, forcing callers to provide values even when defaults exist in Kotlin.

Enum class improvements make Kotlin enums work more naturally in Swift. The transformation provides better naming and functionality for enum cases.

Function type improvements help with passing Swift closures to Kotlin functions that expect function types. The bridging becomes more seamless.

Naming customization enables adjusting how Kotlin declarations appear in Swift. This helps when default naming does not match Swift conventions.

These improvements accumulate to make KMP frameworks feel native. iOS developers experience APIs that work like Swift APIs, hiding the Kotlin origins behind idiomatic interfaces.

## Integration and Build Configuration

Enabling SKIE requires adding it to the build configuration. The SKIE Gradle plugin integrates with the Kotlin Multiplatform plugin. Configuration options control which transformations apply and how they behave.

The framework generation process incorporates SKIE processing. Kotlin code compiles to Kotlin Native, SKIE processes the declarations, and the resulting framework includes SKIE's transformations. The process is transparent once configured.

Binary size may increase slightly due to generated bridging code. The impact is typically small and acceptable for the improved developer experience. Measurement for specific projects helps validate acceptable overhead.

Build time may increase due to additional processing. The increase is usually proportional to the amount of code being transformed. For large projects, incremental builds help maintain reasonable iteration speed.

Debugging SKIE-bridged code works through standard Kotlin Native debugging. Breakpoints in Kotlin code hit when called from Swift. Variable inspection works across the boundary. The transformation does not impede debugging.

## Designing APIs for iOS Consumption

Even with SKIE, thoughtful API design improves iOS developer experience. Several principles guide effective KMP API design for iOS consumers.

Prefer suspend functions over Flow for single-value async operations. While SKIE handles both well, suspend functions map to simpler Swift async functions. Flows are appropriate for multiple values over time, but overusing them complicates consumption.

Use sealed classes for closed type hierarchies. SKIE's transformation provides exhaustiveness checking. Open class hierarchies do not benefit from this, so prefer sealed when the hierarchy is logically closed.

Consider nullability carefully. Kotlin's nullable types map to Swift optionals, but the mapping can sometimes be surprising. Explicit nullability annotations help ensure correct interpretation.

Document error cases even though Kotlin exceptions are unchecked. Swift developers need to know what errors might be thrown. Documentation compensates for Kotlin's lack of checked exceptions.

Avoid complex generic signatures when possible. Generics mapping between Kotlin and Swift can be imperfect. Simpler signatures reduce potential issues.

Provide data classes for return values rather than tuples or complex nested structures. Data classes become clear types in Swift with named properties, while other constructs may map less clearly.

## Memory Management Considerations

Memory management across the Kotlin-Swift boundary requires attention because Swift uses ARC while Kotlin Native uses its own reference counting that interoperates with ARC.

Kotlin Native produces Objective-C compatible objects that participate in ARC. Swift code holding references to Kotlin objects keeps them alive. Releasing references allows deallocation. The basic lifecycle matches Swift expectations.

Callbacks and closures present cycle risks. A Swift closure passed to Kotlin that captures self can create a retain cycle if Kotlin holds the closure while self holds the Kotlin object. Using weak references in captures prevents cycles, just as in pure Swift code.

SKIE transformations do not change memory management fundamentals. Transformed APIs still produce Objective-C objects that participate in ARC. The same attention to cycles applies.

Long-lived Kotlin objects that observe or register callbacks should provide clear unregistration mechanisms. Swift code should call these mechanisms at appropriate lifecycle points. Documentation should clarify ownership and lifecycle expectations.

## Testing Interoperability

Testing the iOS interface of KMP frameworks verifies that transformations work correctly and APIs behave as expected.

Swift tests can call into KMP frameworks just like any Swift dependency. Tests verify that suspend functions work as async functions, that sealed class switches are exhaustive, and that flows iterate correctly.

Integration tests that exercise the boundary catch issues specific to the transformation. A test might verify that cancellation propagates, that errors are typed correctly, or that memory is managed correctly.

Unit tests in Kotlin verify shared code independent of iOS consumption. These tests run faster and catch issues unrelated to interoperability.

The combination of Swift integration tests and Kotlin unit tests provides confidence in both the shared logic and its iOS interface.

## Conclusion

iOS interoperability is crucial for KMP adoption because iOS applications must consume shared frameworks naturally. The default interoperability works but creates friction through completion handlers, non-exhaustive switches, and opaque Flow types.

SKIE transforms KMP frameworks into Swift-friendly forms. Suspend functions become async functions. Sealed classes become exhaustively switchable. Flows become AsyncSequences. The transformations enable iOS developers to work with KMP code using native Swift patterns.

Thoughtful API design complements SKIE's transformations. Choosing appropriate Kotlin constructs that transform well, documenting behavior, and managing memory correctly ensures excellent iOS developer experience.

The combination of Kotlin Multiplatform's code sharing with SKIE's interoperability enhancements enables building shared libraries that feel native on iOS. This removes a significant barrier to KMP adoption and enables teams to share more code while maintaining platform-appropriate interfaces.
