# Kotlin Multiplatform Fundamentals: The Expect/Actual Mechanism

Kotlin Multiplatform enables sharing code across platforms while allowing platform-specific implementations where needed. At the core of this capability lies the expect/actual mechanism, a language feature that lets common code declare expectations that platform-specific code fulfills. Understanding this mechanism deeply is essential for effective KMP development.

## The Problem KMP Solves

Mobile development has long struggled with the duplication inherent in building for multiple platforms. iOS and Android applications often implement the same business logic twice, once in Swift or Objective-C and once in Kotlin or Java. This duplication increases development cost, creates opportunities for behavioral divergence, and complicates maintenance when logic must be updated identically on both platforms.

Previous cross-platform approaches typically sacrificed platform integration for code sharing. Write-once frameworks like Flutter and React Native provide their own runtime environments that sit between the application and the native platform. While enabling significant code sharing, this architecture introduces abstraction layers that can limit access to platform capabilities and affect performance.

KMP takes a different approach by enabling selective sharing at the code level rather than the runtime level. Shared Kotlin code compiles to JVM bytecode for Android and native binary for iOS. There is no intermediate runtime layer. Shared code runs as native code on each platform, with full access to platform capabilities through the interoperability mechanisms Kotlin provides.

The key insight is that not all code benefits equally from sharing. Business logic, data validation, API clients, and state management typically implement platform-independent algorithms that should behave identically everywhere. User interfaces, platform API access, and platform-specific features necessarily differ between platforms. KMP enables sharing the former while implementing the latter natively.

## Understanding Expect and Actual

The expect keyword declares a contract in common code. It says this class exists, this function exists, or this property exists without providing implementation. The actual keyword fulfills that contract in platform-specific source sets. Each platform provides its own actual declaration that matches the expected signature.

This mechanism separates interface from implementation across platforms. Common code programs against the expected declarations. Platform code provides actual implementations using platform-appropriate mechanisms. The compiler ensures that every expect has a matching actual on every targeted platform.

An expected function declares that a function with a given signature exists. Common code can call this function without knowing how any platform implements it. Each platform's actual function provides the implementation using whatever platform APIs are appropriate.

An expected class declares that a class with given members exists. Common code can instantiate the class and call its methods. Each platform provides an actual class implementing those members. The actual implementations can differ entirely as long as they satisfy the contract.

Expected properties similarly declare that properties exist. Platforms provide actual properties that may be computed differently on each platform. Common code accesses properties without knowing how they are implemented.

The expect/actual mechanism differs from interfaces in important ways. Interfaces define contracts that classes implement at runtime. Expect/actual defines contracts that platforms fulfill at compile time. An expected class becomes an actual class during compilation, with no runtime indirection. This enables expect/actual for classes where interfaces would not work, including those with constructors.

## Practical Expect/Actual Patterns

Several patterns appear repeatedly in KMP codebases, addressing common cross-platform needs.

Platform identification is a simple but useful pattern. Common code might need to know which platform it runs on for logging, analytics, or conditional behavior. An expected function returns platform identification. Android's actual returns information from Build.VERSION. iOS's actual returns information from UIDevice.

File system access differs between platforms. An expected FileSystem class declares methods for reading and writing files. Android's actual implementation uses java.io.File and Context.filesDir. iOS's actual implementation uses NSFileManager and NSSearchPathForDirectoriesInDomains. Common code accesses files through the expected interface.

Secure storage for credentials differs significantly. An expected SecureStorage class declares methods for saving and retrieving secrets. Android's actual uses EncryptedSharedPreferences or the Keystore system. iOS's actual uses the Keychain through Security framework. Common code stores credentials without concerning itself with platform-specific security mechanisms.

UUID generation provides another example. An expected function generates random UUIDs. Android's actual uses java.util.UUID.randomUUID. iOS's actual uses NSUUID. The implementations differ, but common code just calls the function.

Current time access might use an expected function returning epoch milliseconds. Android's actual uses System.currentTimeMillis or Instant.now. iOS's actual uses CFAbsoluteTimeGetCurrent or Date. Clock abstraction also enables testing by providing test doubles.

Threading primitives require platform-specific implementation. An expected AtomicInt class provides atomic integer operations. Android's actual can use java.util.concurrent.atomic.AtomicInteger. iOS's actual uses Kotlin Native's atomic references. Common code uses atomic operations without platform-specific imports.

Weak references behave differently under ARC versus garbage collection. An expected WeakReference class provides weak reference semantics. Android's actual wraps java.lang.ref.WeakReference. iOS's actual wraps kotlin.native.ref.WeakReference. Common code can hold weak references with platform-appropriate behavior.

## Actual Typealias for Existing Classes

When a platform already has a class that matches the expected signature, actual typealias provides implementation without writing new code. The actual declaration becomes an alias to the existing class.

This pattern works when platform classes have members matching the expected class exactly. Naming and signatures must align. If they do, the typealias approach avoids wrapper overhead and provides seamless integration with existing platform code.

For example, an expected AtomicInt with get and incrementAndGet methods might map directly to AtomicInteger on JVM through typealias. The existing class already has those methods with matching signatures. No wrapper is needed.

However, typealias only works when signatures match exactly. If the platform class uses different names, different parameter types, or different return types, typealias cannot adapt. In those cases, a full actual class implementation provides the necessary adaptation.

## Source Set Structure

KMP projects organize code into source sets that target different platforms. Understanding this structure clarifies where expect and actual declarations live.

The commonMain source set contains code shared across all platforms. This is where expect declarations live alongside platform-independent implementations. Most business logic resides here.

Platform-specific source sets contain actual declarations and platform-specific code. androidMain contains Android-specific code including actual declarations for Android. iosMain contains iOS-specific code including actual declarations for iOS.

Intermediate source sets enable sharing between platform subsets. appleMain might contain code shared between iOS, macOS, watchOS, and tvOS. nativeMain might contain code shared between all native targets. These intermediate sets can themselves have expect declarations fulfilled by more specific sets.

The compiler resolves expect declarations to actual declarations based on the target being compiled. When building for Android, expects resolve to actuals in androidMain. When building for iOS, expects resolve to actuals in iosMain. The resulting binary contains only the platform-appropriate implementations.

Test source sets parallel main source sets. commonTest contains shared tests. androidTest and iosTest contain platform-specific tests. Platform tests can test actual implementations directly. Common tests test common code using expected interfaces.

## When to Use Expect/Actual

The expect/actual mechanism is powerful but should be used judiciously. Several guidelines help determine appropriate usage.

Use expect/actual when common code needs platform capabilities that have no multiplatform library solution. If a multiplatform library exists that wraps the capability, using the library is usually preferable to writing expect/actual declarations. Libraries have been tested and handle edge cases.

Use expect/actual for platform primitives that differ in signature but not concept. UUIDs, atomic operations, and time access are conceptually identical across platforms but have different APIs. Expect/actual bridges these API differences.

Use expect/actual to inject platform dependencies into common code. Instead of common code depending directly on platform types, it depends on expected types that platforms fulfill. This maintains the common code's platform independence.

Avoid expect/actual for business logic that can be platform-independent. If logic can be written without platform dependencies, write it directly in commonMain. Expect/actual adds complexity and maintenance burden.

Avoid expect/actual when interfaces and dependency injection suffice. Interfaces defined in common code with implementations provided through dependency injection achieve similar decoupling without the expect/actual mechanism. This often provides more flexibility for testing.

Consider library-based solutions before custom expect/actual. Libraries like Kermit for logging, Ktor for networking, and SQLDelight for databases provide multiplatform APIs with tested platform implementations. Custom expect/actual should fill gaps, not duplicate available solutions.

## Compiler Enforcement and Errors

The Kotlin compiler enforces expect/actual contracts strictly, catching mismatches at compile time.

Missing actual declarations produce errors when compiling for a platform that lacks the required actual. The error identifies the expect that lacks a corresponding actual. This ensures all contracts are fulfilled before code can run.

Signature mismatches between expect and actual produce errors. If an actual function has different parameters than the expect, compilation fails. If an actual class lacks a method the expect declares, compilation fails. The compiler ensures actuals satisfy their contracts completely.

Visibility mismatches produce errors. An actual cannot be less visible than its expect. If an expect is public, the actual must be public. The actual can be more visible but not less.

Return type mismatches for functions and properties produce errors. The actual return type must match the expected return type. Covariant return types may be allowed in some cases, but exact matching is safest.

These compiler checks provide confidence that expect/actual contracts are correctly implemented. Errors are caught during development rather than at runtime. Platform-specific bugs from contract violations are prevented.

## Testing Expect/Actual Code

Testing code that uses expect/actual requires consideration of what to test where.

Common code that uses expect declarations should be tested in commonTest when possible. The tests run on all platforms, verifying that common logic works regardless of platform-specific implementations. Test expectations focus on contracts rather than implementation details.

Platform-specific actual implementations should be tested in platform test source sets. These tests can verify platform-specific behaviors, edge cases, and integration with platform APIs. They test that actuals correctly implement expected contracts.

Mock or fake implementations of expected types can be used in common tests. A test-only source set can provide actual implementations that are controllable for testing. This enables isolated testing of common code without invoking real platform implementations.

Integration tests that exercise expect/actual boundaries verify that real actuals work correctly when called from common code. These tests should run on each platform to catch platform-specific issues.

## Performance Considerations

The expect/actual mechanism has minimal runtime overhead because resolution happens at compile time.

When code compiles for a platform, expect declarations are replaced with actual implementations. There is no runtime lookup or indirection. The compiled code directly uses the actual implementation as if common code had called it directly.

Actual typealias has zero overhead because it creates no wrapper. The expected type becomes the platform type directly. Code compiled against the expect uses the platform type as its actual type.

Actual classes have the overhead of any class, but no additional expect-related overhead. If an actual class wraps a platform type, the wrapper overhead exists, but this is the cost of the abstraction, not of the expect/actual mechanism itself.

Function call overhead through expect/actual is identical to any function call. There is no virtual dispatch or reflection involved. The compiler resolves the actual at compile time.

## Common Pitfalls and Solutions

Several pitfalls can trip up developers working with expect/actual.

Forgetting to provide actual declarations for new platforms is a common mistake when adding platform targets. The solution is to ensure all expects have actuals before attempting to compile for new platforms. IDE support helps identify missing actuals.

Inconsistent behavior between actual implementations causes subtle bugs. An actual that behaves differently than other platforms' actuals violates the contract's spirit even if signatures match. The solution is thorough testing on all platforms and clear documentation of expected behavior.

Overusing expect/actual for code that could be common increases maintenance burden. Each expect/actual pair requires multiple implementations. The solution is preferring common code and multiplatform libraries when possible.

Platform type leakage into common code occurs when actual implementations return platform types that then spread through common code. The solution is ensuring expected types fully encapsulate platform types, exposing only platform-independent representations.

Constructor complexity in expected classes can cause issues because expect constructors must be matched by actual constructors. Complex construction with multiple parameters or optional parameters requires careful signature matching. Simpler constructors with factory functions can avoid issues.

## Conclusion

The expect/actual mechanism enables KMP's key value proposition: sharing code where it makes sense while maintaining native platform integration where it matters. Expected declarations create contracts that common code can rely on. Actual declarations fulfill those contracts with platform-appropriate implementations.

Understanding when and how to use expect/actual effectively distinguishes proficient KMP developers. The mechanism should bridge genuine platform differences for capabilities common code needs. It should not be overused for code that could be platform-independent or for capabilities that existing libraries provide.

The compile-time resolution of expect/actual means no runtime overhead, just clean separation of interface and implementation across platforms. Combined with the rich multiplatform library ecosystem and platform interoperability features, expect/actual completes the foundation for effective cross-platform Kotlin development.
