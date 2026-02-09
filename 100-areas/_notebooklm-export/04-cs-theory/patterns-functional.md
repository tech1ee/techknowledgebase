# Functional Patterns: Composable Abstractions for Reliable Software

Functional programming introduces patterns that approach software construction from a fundamentally different perspective than object-oriented design. Rather than focusing on objects and their interactions, functional patterns emphasize data transformation, composition, and explicit effect handling. These patterns have migrated from academic languages into mainstream development because they solve real problems: making code more predictable, more testable, and more compositional.

The patterns explored here—Functors, Monads, map and flatMap operations, functional composition, and Option/Result types—form a coherent system for handling data transformation and error cases. Understanding these patterns doesn't require a mathematics degree, but it does require setting aside some object-oriented intuitions and embracing new ways of thinking about computation.

## Building Intuition: The Wrapper Pattern

Before diving into specific patterns, consider a fundamental idea that underlies all of them: the concept of a context or wrapper around values. We constantly work with values that exist in some context. A value might be optional—it might exist or might be absent. A value might be the result of an operation that could fail—it's either a success value or an error description. A value might be asynchronous—it will exist eventually but doesn't exist yet. A value might be one of several possibilities in a collection.

These contexts share a common need: we want to work with the values inside them without manually extracting, checking, processing, and re-wrapping. If I have an optional integer and want to double it, I want to express "double the value if it exists" without writing conditional extraction and rewrapping code everywhere. Functional patterns provide exactly this capability—uniform ways to work with values in various contexts.

## Functors: Mapping Over Contexts

A Functor is any context that supports a mapping operation. You can take a function that transforms values and "lift" it to work on values inside the context. The mapping operation applies the function to the wrapped value while preserving the context structure.

### The Mapping Intuition

Consider a list of numbers and a function that doubles a number. Mapping the doubling function over the list produces a new list where each element is doubled. The list structure is preserved—same length, same ordering—but each element has been transformed. The mapping operation lifted a simple number-to-number function to work on entire lists.

Now consider an optional value. You have an optional number and a doubling function. Mapping the function over the optional produces a new optional: if the original contained a value, the result contains the doubled value; if the original was empty, the result is empty. The optionality is preserved while the contained value (if any) is transformed.

This pattern repeats across contexts. A Future value that will eventually contain a number, mapped with a doubling function, produces a Future that will eventually contain a doubled number. The asynchronicity is preserved while the eventual value is transformed. A Result that's either a success number or an error, mapped with doubling, produces a Result that's either a doubled success or the same error. The success/failure context is preserved.

### Why Functors Matter

Functors matter because they let you compose transformations without context management. Without the Functor pattern, working with optional values requires constant presence checking: is the value present? If so, extract it, transform it, wrap it back. This checking code obscures the actual logic. With Functor's map operation, you express the transformation directly, and the context handles presence checking automatically.

This reduces boilerplate and increases clarity. The logic of your transformation stands out clearly. The context management is standardized and invisible. Different contexts—optionals, lists, results, futures—all support the same mapping interface, so you learn one pattern and apply it everywhere.

Functors also compose naturally. If you map function f over a value, then map function g over the result, the outcome is the same as mapping the composition of f and g. This property, called the composition law, means you can think about transformations independently of when and how they're applied.

### Functor Laws

The Functor pattern comes with laws that any implementation should satisfy. The identity law says that mapping the identity function (which returns its input unchanged) over a Functor should produce an identical Functor. Mapping "do nothing" should do nothing. The composition law says that mapping f then mapping g should equal mapping the composition of g and f. These laws ensure that mapping behaves predictably and that you can reason about transformations algebraically.

These laws aren't arbitrary academic requirements. They capture essential expectations about how mapping should behave. If an implementation violates these laws, code that depends on Functor behavior might break in subtle ways. The laws provide guarantees that enable confident composition.

## Understanding map: Transforming Contents

The map operation is the concrete manifestation of Functor behavior. When you call map on a context with a transformation function, you get a new context of the same type with transformed contents. Understanding map deeply—what it does, what it preserves, how it composes—unlocks effective use of functional patterns.

### map Preserves Structure

A crucial property of map is that it preserves the structure of the context while transforming contents. Mapping over a list with three elements produces a list with three elements. Mapping over an optional that contains a value produces an optional that contains a value. Mapping over an empty optional produces an empty optional. Mapping over a successful result produces a successful result; mapping over a failed result produces a failed result with the same error.

This preservation is why map is safe to call without checking the context's state. You don't need to know if the optional is empty before mapping—if it is, map handles it correctly. You don't need to know if the result is an error before mapping—if it is, the error propagates. This unconditional applicability reduces branching and conditional logic throughout your code.

### map Never Changes Context Type

Map transforms values, not contexts. Mapping a function over an optional produces an optional, never a bare value. Mapping over a list produces a list, never a single element. If you map a function that returns a list over an optional, you get an optional containing a list, not a plain list.

This consistency is important for reasoning about code. When you see a map call, you know the result type's wrapper is the same as the input type's wrapper. Only the content type changes according to the mapped function.

### Chaining map Operations

Map operations chain naturally. Starting with an optional string, you might map a parsing function to get an optional number, then map a multiplication function to get an optional scaled number, then map a formatting function to get an optional string representation. Each map transforms the content while preserving optionality through the entire chain.

This chaining enables declarative data pipelines. Instead of imperative steps with intermediate variables and presence checks, you express the transformation sequence directly. The chain reads as a description of what happens to the data, not how to manage the optional context.

## Understanding flatMap: Handling Nested Contexts

While map handles straightforward transformations, many operations naturally produce wrapped results. A function that parses a string to a number might return an optional number—the parse could fail if the string isn't a valid number. If you have an optional string and map this parsing function, you get an optional optional number: the outer optional from the original string, the inner optional from the parse result.

Nested contexts are awkward. Working with an optional optional number requires checking two layers of presence. Chains of operations that each might fail create deeply nested optionals that become unwieldy. What you usually want is to flatten these nested contexts into a single layer.

### How flatMap Differs from map

flatMap applies a function and then flattens one layer of nesting. Given an optional string and a function from string to optional number (like parsing), flatMap produces an optional number—not an optional optional number. If the original optional is empty, the result is empty. If the original contains a value, the function runs, and its result (optional number) becomes the final result.

This flattening makes flatMap the tool for sequencing operations that each produce wrapped results. Parse the input (might fail), validate the parsed value (might fail), look up related data (might fail), compute a result (might fail). Each step returns an optional or result type. Chaining with flatMap produces a single optional or result representing success through all steps or failure at any step.

### flatMap Enables Context-Aware Sequencing

The power of flatMap emerges in sequences where each step depends on the previous step's success. Consider a multi-step process: look up a user by ID (might not find them), get their current subscription (might not have one), check their permissions (might not have required permission), perform an action. Each step only makes sense if the previous step succeeded.

With flatMap, you chain these operations naturally. FlatMap the user lookup; the function only runs if the user exists. FlatMap getting the subscription; that function only runs if we have a user. FlatMap the permission check; that function only runs if we have a subscription. Any failure short-circuits the chain, producing an empty result without executing subsequent steps.

Without flatMap, you'd write nested conditionals: if user exists, then if subscription exists, then if permission granted, then perform action. Each level adds indentation and obscures the core logic. FlatMap flattens this into a linear sequence that expresses the happy path clearly while handling failures implicitly.

### The Relationship Between map and flatMap

Map and flatMap are related but serve different purposes. Map transforms values with functions that return plain values. FlatMap sequences operations with functions that return wrapped values. You can actually define map in terms of flatMap: map with function f is flatMap with a function that applies f then wraps the result.

In practice, you use map when your transformation doesn't introduce new context (doubling a number never fails; it doesn't return an optional). You use flatMap when your transformation might introduce new context (parsing might fail; it returns an optional).

Mixing map and flatMap in chains is common. Parse the string (flatMap, might fail), double the number (map, won't fail), format as string (map, won't fail), prefix with label (map, won't fail). Use the lighter operation when it suffices; use flatMap only when context production requires it.

## Monads: The Pattern Behind flatMap

A Monad is any context that supports flatMap (often called bind or chain in different languages) along with a way to wrap a plain value into the context. Optionals, Results, Lists, and Futures are all Monads. The Monad pattern captures the commonality that makes flatMap possible across these different contexts.

### What Makes Something a Monad

A Monad provides two operations. First, a way to take a plain value and wrap it in the context—creating an optional containing a value, a successful result, a list with one element, a completed future. This is often called return, pure, or unit. Second, the flatMap operation that sequences computations.

These operations must satisfy the Monad laws. The left identity law says that wrapping a value and then flatMapping a function is the same as just applying the function. The right identity law says that flatMapping the wrapping function over a monadic value produces an identical value. The associativity law says that the order of flatMap nesting doesn't matter.

These laws ensure flatMap behaves predictably. They guarantee that sequencing operations works as expected, that wrapping and unwrapping don't change values, and that different ways of combining the same operations produce the same results.

### The Monad Intuition

Monads model sequential computations in contexts. Each step in a monadic sequence produces a value in a context. The next step receives that value and produces another contextual result. FlatMap handles the plumbing of extracting values and rewrapping results, letting you focus on the steps themselves.

Think of Monads as programmable semicolons. In imperative programming, a semicolon sequences statements—first this, then that. Monadic flatMap sequences computations while handling the context-specific behavior between steps. For optionals, the behavior is "stop if empty." For results, it's "stop on error." For lists, it's "do this for each element." For futures, it's "wait for completion, then continue."

### Why Monads Feel Complex Initially

Monads have a reputation for being difficult to understand, but this difficulty is largely pedagogical rather than inherent. Traditional explanations introduce category theory terminology, speak in abstract generalities, and provide examples that feel disconnected from practical programming.

The practical reality is simpler: if you've used optional chaining, promise chains, or list comprehensions, you've used Monads. The pattern is familiar; only the name and explicit articulation are new. Understanding that these diverse features share common structure helps you apply the pattern in new contexts and recognize it in unfamiliar libraries.

## Functional Composition: Building Complex Operations from Simple Ones

Functional composition combines simple functions to create complex ones. Instead of writing large functions that do many things, you write small functions that each do one thing, then compose them into pipelines that do exactly what you need.

### The Composition Operator

Composing two functions f and g (written f compose g or g after f) creates a new function that applies f first, then applies g to the result. If f converts strings to numbers and g doubles numbers, their composition converts strings to doubled numbers.

This simple operation enables powerful abstraction. You build a library of small, focused, reusable functions. You compose them in different ways for different needs. The individual functions are easy to test and understand. The compositions express complex transformations as combinations of simple steps.

### Point-Free Style

Composition enables point-free style, where you define functions without mentioning their arguments. Instead of writing a function that takes x, applies f to it, then applies g to the result, you simply write the composition of f and g. The argument is implicit—the composition already expresses what happens to it.

Point-free style can make code more concise and declarative when used appropriately. Instead of describing how to process data step by step, you describe what the processing is—a pipeline of transformations. However, taken to extremes, point-free style becomes cryptic. Balance conciseness with clarity.

### Composition in Practice

Data transformation pipelines exemplify composition. Raw data enters and undergoes a series of transformations: filtering, mapping, sorting, grouping, aggregating. Each transformation is a simple function. The overall pipeline is the composition of these transformations.

Middleware in web frameworks uses composition. Each middleware function does one thing—log the request, check authentication, parse the body. The request handler is the composition of all middleware followed by the core handler. Adding or removing a concern means adding or removing a function from the composition.

Validation systems compose validation rules. Each rule checks one thing—field present, value in range, format correct. Composing rules creates compound validators. Different forms might need different rule compositions, easily assembled from the rule library.

## Option and Result: Explicit Absence and Failure

The Option (or Maybe or Optional) pattern explicitly represents the possible absence of a value. The Result (or Either) pattern explicitly represents the possibility of failure with error information. These patterns replace implicit null values and exceptions with explicit, type-tracked alternatives.

### The Problem with Null

Null references have been called the "billion dollar mistake." When a value might be null, every use of that value risks a null pointer exception. The type system doesn't track nullability—a reference to a string might or might not actually refer to a string. Callers must defensively check for null, but nothing enforces these checks. Forgotten checks cause runtime crashes.

Option makes potential absence explicit in the type. An optional string is a different type than a string. You cannot use an optional string where a string is expected without explicitly handling the potential absence. The type system enforces that you address the possibility—no forgotten null checks, no runtime surprises.

### Working with Option

Option values are either present (containing a value) or absent (empty). You work with them through map and flatMap rather than extraction and null checking. Map transforms the contained value if present; flatMap sequences operations that might produce absence.

When you eventually need the actual value, Option provides explicit handling mechanisms. You might provide a default value to use if absent. You might throw an exception (but now the possible exception is explicit, not hidden). You might branch explicitly on presence. The handling is always explicit, never implicit.

### The Problem with Exceptions

Exceptions create invisible control flow. Any function might throw; the signature doesn't indicate which ones do. Exception handling is optional—uncaught exceptions crash the program or propagate to distant handlers. The exception hierarchy makes it unclear which exceptions to catch. Checked exceptions (in languages that have them) address some issues but create their own problems.

Result makes failure explicit in the return type. A function that might fail returns a Result containing either a success value or an error. Callers must handle both possibilities—the type system enforces it. Error propagation is explicit through flatMap chains, not implicit through stack unwinding.

### Working with Result

Result values are either success (containing a value) or failure (containing an error). Like Option, you work with them through map and flatMap. Map transforms success values; failures propagate unchanged. FlatMap sequences operations that might fail; the first failure short-circuits the chain.

Error recovery is explicit. You can provide fallback values for failures. You can transform errors into different errors. You can recover from specific error types while propagating others. All error handling appears in the code, visible and verifiable.

### Option vs. Result

Option and Result serve related but distinct purposes. Option represents potential absence without explaining why—the value either exists or doesn't. Result represents potential failure with an explanation—the operation either succeeded or failed for a specific reason.

Use Option when absence is a normal possibility without interesting cause. A dictionary lookup might not find a key—there's no error, just no value. A user might not have an optional profile field set—absence is expected and requires no explanation.

Use Result when failure needs explanation. A network request might fail for many reasons—timeout, connection lost, server error, authentication failed. A validation might fail with specific messages. File operations might fail with IO errors. The error information helps callers respond appropriately.

Some languages combine these concepts. Either types can hold either of two types, often used as left-error/right-success. Some Result types include a None/absent case alongside success and error cases.

## Combining Functional Patterns

These functional patterns work together as a coherent system. Functors provide map; Monads provide flatMap and wrapping. Option and Result are specific Monads with specific semantics. Composition builds complex transformations from simple ones. Together, they enable expressive, composable, error-handling code.

Consider a data processing pipeline. Read configuration from file (returns Result—might fail to read). Parse configuration (returns Result—might fail to parse). Look up database connection settings (returns Option—might be absent). Connect to database (returns Result—might fail to connect). Query for user (returns Option—might not exist). Validate user permissions (returns Result—might be unauthorized). Perform action.

With traditional imperative style, this becomes a tower of nested error handling. With functional patterns, it becomes a flatMap chain that expresses the happy path while implicitly handling each failure possibility. Error handling is present but doesn't obscure the main logic.

Functional patterns also interact well with concurrency patterns. Futures are Monads; you can map and flatMap over them to transform eventual results and sequence asynchronous operations. Combining Futures with Results gives you asynchronous operations that might fail, with explicit handling for both dimensions.

Understanding these patterns provides vocabulary for discussing code design and tools for implementing robust data processing. They're not purely theoretical—they're practical patterns that improve real code quality. The investment in understanding them pays dividends in cleaner, more reliable, more composable software.

## Advanced Functor Concepts: Applicative Functors

Between Functor and Monad lies another important abstraction: the Applicative Functor. While Functor's map applies a single-argument function to a wrapped value, Applicative extends this to functions with multiple arguments, all wrapped in the same context.

Consider wanting to add two optional numbers. With Functor alone, you're stuck: map can apply a function to one optional, but addition needs two optionals. You'd need to extract both values, check both for presence, add them, and wrap the result. Applicative provides operations that handle multiple wrapped values elegantly.

The key insight is that if you have an optional function and an optional value, Applicative lets you apply the function to the value, producing an optional result. Empty on either side produces empty. If you have an optional partially-applied addition function (waiting for one more number) and an optional number, you can apply to get an optional result.

This pattern enables parallel independent operations. Where flatMap sequences operations—the second depends on the first's result—Applicative combines independent operations. Loading user profile and user preferences are independent; neither needs the other's result. Applicative combines them in parallel; flatMap would sequence them unnecessarily.

In practice, languages provide syntax sugar for Applicative patterns. Comprehension syntax, liftA2 functions, and operator overloading make Applicative usage natural without explicitly naming the pattern. Understanding the underlying abstraction helps recognize when these tools apply.

## Deeper Monad Understanding: Common Monad Types

The List Monad treats lists as representing multiple possible values. FlatMap over a list with a function that returns lists produces a flattened list of all possibilities. If you have a list of users and each user has a list of orders, flatMapping users to their orders produces a flat list of all orders across all users.

List comprehensions in many languages are syntactic sugar for List Monad operations. Filtering, mapping, and combining lists through comprehension syntax expresses monadic computation without explicit flatMap calls. Understanding this connection reveals the power underlying familiar syntax.

The Reader Monad represents computations that read from a shared environment. Rather than passing configuration through every function explicitly, Reader encapsulates the dependency. FlatMap sequences computations that all need the same environment. At the end, you provide the environment once, and the composed computation runs with access to it throughout.

The Writer Monad accumulates output alongside computation. Each step can append to a log; flatMap combines the logs. This pattern enables logging or debugging output without threading log state through every function. The computation and its logging compose cleanly.

The State Monad threads state through a sequence of computations. Each step receives current state and produces new state along with a value. FlatMap sequences these state transformations. This enables stateful computation in a pure functional style, with state changes explicit rather than hidden.

The IO Monad, prominent in Haskell, separates description of effects from their execution. An IO value doesn't perform an effect; it describes one. FlatMap sequences descriptions; only at program boundaries do effects actually occur. This separation enables reasoning about effects as first-class values.

## Monad Transformers: Combining Monadic Effects

Real programs often need multiple monadic effects simultaneously: optionality and failure, asynchrony and error handling, state and IO. Combining monads naively creates nested types like Option of Result of Future that are awkward to work with.

Monad transformers provide systematic combination. A transformer wraps one monad around another, providing combined behavior. OptionT wraps Option around another monad; you get the base monad's capabilities plus optionality. ResultT adds error handling to a base monad. These transformers compose, building up the exact combination of effects you need.

Working with transformers requires lifting operations from inner monads to the combined stack. A pure Option operation needs lifting to work in an OptionT stack. Libraries provide these lifting operations; understanding when and how to use them enables effective transformer stacks.

In practice, many applications settle on a fixed effect stack—perhaps asynchrony with error handling—and use it consistently. Framework-provided types often encode common effect combinations, hiding transformer mechanics while providing combined capabilities.

## Laziness and Strictness in Functional Patterns

Evaluation strategy significantly affects functional pattern behavior. Strict evaluation evaluates arguments before function application; lazy evaluation defers evaluation until results are needed. Different languages default to different strategies, affecting how patterns behave.

Lazy evaluation enables infinite data structures. A lazy list of all natural numbers doesn't compute all numbers upfront—that's impossible—but generates them on demand. Mapping over an infinite lazy list produces another infinite lazy list; taking the first ten elements evaluates only what's needed.

Strict evaluation provides predictable performance and memory characteristics. You know when computation happens and can reason about resource usage. Lazy evaluation can cause surprising space leaks where unevaluated computations accumulate, consuming memory unexpectedly.

Many functional patterns work better with one strategy or the other. Composition benefits from laziness—intermediate results in a pipeline might not need full evaluation. Error handling with Result often assumes strictness—errors should propagate immediately, not lurk in unevaluated thunks.

Languages and libraries provide mechanisms to control evaluation. Strict languages might offer lazy types; lazy languages might offer strict annotations. Understanding your tools' default behavior and override mechanisms helps write code that performs as expected.

## Higher-Kinded Types and Type-Level Abstraction

Functional patterns often involve abstracting over type constructors—types that take type parameters. List is not a type; List of Integer is. Map works on any Functor; its signature needs to express "any type constructor F such that F is a Functor."

Higher-kinded types enable this abstraction. Where regular generics abstract over types, higher-kinded types abstract over type constructors. This enables writing code generic over Functor, Monad, or any other type class without specifying the particular container.

Not all languages support higher-kinded types directly. Java's generics don't extend to higher kinds; you can't write a generic map that works across all container types. Workarounds exist—type lambdas, wrapper types, encoding through interfaces—but they're more cumbersome than native support.

Languages like Haskell, Scala (with some extensions), and others provide higher-kinded types, enabling full expression of functional patterns at the type level. Understanding this limitation helps when applying functional patterns in less-expressive languages.

## Functional Error Handling Strategies

Railway-oriented programming visualizes Result chains as parallel tracks—success track and failure track. Each operation continues on the success track or switches to the failure track. Once on the failure track, subsequent operations are bypassed until error handling switches back. This mental model helps design and understand error-handling flows.

Accumulating errors differs from short-circuiting. Short-circuit semantics stop at the first error; subsequent operations don't run. Sometimes you want all errors—validation should report all violations, not just the first. Applicative validation accumulates errors into a collection rather than short-circuiting.

Error transformation enables domain-appropriate error types at each layer. Low-level IO errors transform to service errors; service errors transform to API errors. Each transformation adds context appropriate to that layer. The final error presented to users differs from the original low-level error.

Retry and recovery operations provide resilience. A network operation might retry with exponential backoff on certain errors. A cache lookup might fall back to network on miss. These patterns compose with Result/Either to build robust operation sequences.

Resource cleanup with errors requires careful handling. If an operation fails, resources should still be cleaned up. The bracket pattern (or try-with-resources) ensures cleanup runs regardless of success or failure. Functional languages provide bracket operations that work with their effect systems.

## Functional Composition Patterns

Kleisli composition extends regular composition to monadic functions. Regular composition chains simple functions; Kleisli composition chains functions that return monadic values. If f returns Option and g returns Option, Kleisli composition produces a function that returns Option, handling the chaining correctly.

This composition appears in point-free monadic code. Rather than explicit flatMap chains, you compose the operations and apply once. The composed function captures the entire transformation sequence, reusable and testable as a unit.

Arrows generalize function composition further, enabling composition of things that aren't quite functions—processes with multiple inputs, signal processors, parser combinators. Arrow abstractions aren't as common as Functor/Monad but appear in specialized domains.

Optics—lenses, prisms, and related abstractions—compose access paths into data structures. A lens focuses on a field; composing lenses focuses through nested fields. Prisms focus on optional paths (like pattern matching); composing prisms navigates deep optional structures. Optics enable clean, composable data manipulation without mutation.

## Practical Functional Programming

Functional patterns have migrated into mainstream languages and libraries. Even in primarily object-oriented languages, functional patterns appear throughout modern codebases. Understanding them helps you use and contribute to these codebases effectively.

Stream APIs in Java, LINQ in C#, collection operations in Kotlin and Swift all embrace functional patterns. Map, filter, and reduce appear everywhere. FlatMap for flattening nested operations is standard. These aren't theoretical curiosities; they're daily tools.

Reactive programming libraries are built on functional abstractions. Observables are effectively monads with time and multiplicity. Operators like map, flatMap, and filter work exactly as the patterns describe. Understanding the underlying patterns helps you understand reactive code.

State management in UI frameworks increasingly uses functional patterns. Immutable state, pure reducer functions, and unidirectional data flow create predictable UI behavior. These patterns draw directly from functional programming principles.

Testing benefits from functional patterns. Pure functions are trivially testable—same inputs always produce same outputs, with no hidden state to set up or verify. Map and flatMap chains decompose into independently testable pieces. Functional code often has cleaner test boundaries than stateful object code.

When adopting functional patterns, start with the simplest applications: using Option instead of null, using Result instead of exceptions, using map instead of manual iteration. As comfort grows, explore flatMap, composition, and more advanced patterns. The patterns reinforce each other; learning one makes others more accessible.

## Functional Patterns in Mobile Development

Modern mobile development embraces functional patterns extensively. Reactive streams in both Android and iOS use monadic operations. Combine in iOS and Kotlin Flows in Android are built on these foundations.

Data transformation pipelines appear throughout mobile apps. Parsing JSON responses involves mapping parsing functions over data. Validating user input chains validation operations with flatMap. Converting between data representations uses pure transformation functions.

Immutable data structures reduce concurrency bugs in mobile apps. Immutable models can be safely shared between threads. Copy-on-write collections provide apparent mutability with immutable semantics. These patterns complement reactive streams that deliver immutable snapshots.

State management with reducers appears in mobile architectures. Redux-style state management, MVI architecture, and similar approaches use pure functions to compute new state from old state and actions. These pure reducers are easily testable and predictable.

Error handling with Result types improves mobile code reliability. Network operations, parsing, and validation all can fail. Explicit Result types ensure failure cases are handled rather than forgotten. The type system enforces completeness.

Functional programming isn't all-or-nothing. Most mobile projects use a mix of functional and object-oriented styles. Understanding functional patterns helps you recognize where they apply, use them effectively when they do, and mix them appropriately with other approaches. The patterns are tools in your toolkit, applicable when they improve your code.
