

> **Stage:** 2 of 5 — Engineering Manager Screening
> **Interviewer:** Yura (Yury Garkavyy) — team lead, codes daily
> **Format:** Deep technical dive + behavioral + “Why Ziina?” (~45 min)
> **Prep note from Anton (HR):** “Nothing special to prepare — continuation of HR screening but deeper technical focus”
> **Key insight:** Yura is a hands-on engineer. He’ll dig into IMPLEMENTATION DETAILS. Surface-level answers won’t cut it.

-----

## TABLE OF CONTENTS

1. [Interview Process Overview](#1-interview-process-overview)
2. [Critical Intel from Anton](#2-critical-intel-from-anton)
3. [Interviewer Profile: Yura](#3-interviewer-profile-yura)
4. [Company Quick Reference](#4-company-quick-reference)
5. [TECHNICAL DEEP DIVE: Modular Architecture](#5-technical-deep-dive-modular-architecture)
6. [TECHNICAL DEEP DIVE: Jetpack Compose](#6-technical-deep-dive-jetpack-compose)
7. [TECHNICAL DEEP DIVE: Kotlin Coroutines & Flow](#7-technical-deep-dive-kotlin-coroutines--flow)
8. [TECHNICAL DEEP DIVE: GraphQL & Apollo Kotlin](#8-technical-deep-dive-graphql--apollo-kotlin)
9. [TECHNICAL DEEP DIVE: Fintech Security & Biometrics](#9-technical-deep-dive-fintech-security--biometrics)
10. [TECHNICAL DEEP DIVE: Performance Optimization](#10-technical-deep-dive-performance-optimization)
11. [TECHNICAL DEEP DIVE: Testing Strategy](#11-technical-deep-dive-testing-strategy)
12. [TECHNICAL DEEP DIVE: CI/CD & Release Engineering](#12-technical-deep-dive-cicd--release-engineering)
13. [TECHNICAL DEEP DIVE: Scalability for B2B Growth](#13-technical-deep-dive-scalability-for-b2b-growth)
14. [TECHNICAL DEEP DIVE: Java → Kotlin Migration](#14-technical-deep-dive-java--kotlin-migration)
15. [TECHNICAL DEEP DIVE: AR/3D Work at Seamm](#15-technical-deep-dive-ar3d-work-at-seamm)
16. [Behavioral Questions](#16-behavioral-questions)
17. [Motivation — “Why Ziina?”](#17-motivation--why-ziina)
18. [Red Flags & How to Handle Them](#18-red-flags--how-to-handle-them)
19. [Questions for Yura](#19-questions-for-yura)
20. [Key Metrics Cheat Sheet](#20-key-metrics-cheat-sheet)
21. [Pre-Call Checklist](#21-pre-call-checklist)
22. [Remaining Interview Stages](#22-remaining-interview-stages)
23. [Salary & Package Intel](#23-salary--package-intel)

-----

## 1. INTERVIEW PROCESS OVERVIEW

|#|Stage                            |Status    |Who                         |Format                                        |
|-|---------------------------------|----------|----------------------------|----------------------------------------------|
|1|HR Screening                     |✅ PASSED  |Anton Badashov              |30 min, motivation + experience overview      |
|2|**EM Screening**                 |**⬜ NEXT**|**Yura (team lead)**        |**Deep technical + behavioral + “Why Ziina?”**|
|3|Pair Programming                 |⬜         |TBD                         |Live coding session                           |
|4|System Design + Tech Presentation|⬜         |TBD                         |Architecture discussion + your prepared talk  |
|5|Culture Interview                |⬜         |Co-founders (Faisal + Sarah)|Values alignment, long-term vision            |

**Timeline:** Anton confirmed ≤3 weeks total for all stages.

-----

## 2. CRITICAL INTEL FROM ANTON

|Previous Assumption                            |Confirmed Reality                                           |
|-----------------------------------------------|------------------------------------------------------------|
|Interviewer: Talal Toukan (Head of Engineering)|**Yura — one of the team leads**                            |
|Format: unclear                                |**Deep dive in tech experience + behavioral + “Why Ziina?”**|
|Special prep needed?                           |**No — nothing special, no whiteboard/design tools**        |

**Strategic shift:** This is NOT a conversation with Head of Engineering about high-level strategy. This is a **conversation with a practicing team lead engineer** who codes every day. He will dig into **concrete implementation details**, not discuss vision.

### Three Golden Rules from Anton (HR Screening):

1. **Scalability is the #1 priority** — Ziina’s B2B deal will 2–3x the customer base
2. **Ask questions** — shows genuine interest
3. **Take your time to think** — don’t rush answers

-----

## 3. INTERVIEWER PROFILE: YURA

**LinkedIn:** Yury Garkavyy — ae.linkedin.com/in/yurygarkavyy
**Title:** MD | Lead / Senior Software Engineer
**Location:** UAE (Dubai)
**Background:** CIS origin (Belarusian/Ukrainian roots based on name)

### What We Know:

- **“MD” prefix** = likely “Mobile Developer” or “Managing Director” — suggests technical leadership
- **“Lead / Senior Software Engineer”** — generic title, NOT “Android Engineer” specifically
- **Possibly fullstack or backend-leaning** — may probe cross-platform thinking beyond pure Android
- **Very private profile** — no public technical activity (GitHub, Medium, StackOverflow) found
- **CIS engineering culture** = direct, practical communication style, values execution over self-promotion

### Interview Approach Based on Profile:

- Speak **concretely** with real examples — no buzzwords
- Be ready to discuss **backend integration, API design, cross-platform considerations** (not just Android)
- **Direct, honest communication** — no need to oversell
- **Concrete metrics > theoretical knowledge**

-----

## 4. COMPANY QUICK REFERENCE

|Detail                    |Info                                                                                                          |
|--------------------------|--------------------------------------------------------------------------------------------------------------|
|**Founded**               |January 2020 by Faisal Toukan (CEO), Sarah Toukan (CPO), Talal Toukan                                         |
|**HQ**                    |Dubai DIFC, UAE                                                                                               |
|**Funding**               |$30.85M total — Series A $22M (Sept 2024), Seed $7.5M, Pre-seed $850K                                         |
|**Investors**             |Altos Ventures, Avenir Growth Capital, Class 5 Global + angels from Revolut, Stripe, Venmo, Brex, Notion, Deel|
|**Users**                 |260,000+ businesses and consumers                                                                             |
|**Growth**                |10x YoY payment volume, 34% MoM customer growth, $300M annualized volume                                      |
|**License**               |Central Bank of UAE — Stored Value Facility (first VC-backed startup to get it)                               |
|**Team**                  |~25 employees                                                                                                 |
|**App Rating**            |4.7 stars                                                                                                     |
|**Awards**                |Red Dot Design Award + 8 international design awards                                                          |
|**Mission**               |“Bring financial freedom to every person in the Middle East”                                                  |
|**Co-founder Andrew Gold**|ex-Apple (iOS Safari), ex-Coinbase Wallet                                                                     |
|**Faisal’s vision**       |“200,000 monthly active businesses in 4 years” / “Nubank of the region”                                       |

### Tech Stack (from JD + research)

- **Android:** Kotlin, Jetpack Compose, modular architecture
- **iOS:** Swift, SwiftUI
- **Backend:** TypeScript + Node.js, event-driven microservices
- **API:** GraphQL Federation (Apollo)
- **Messaging:** Kafka (inter-service communication)
- **Storage:** Postgres, Redis, Elasticsearch
- **Infra:** Google Cloud Platform, Kubernetes, Docker
- **CI/CD:** GitHub Actions
- **Architecture:** Modular, principles of reliability, scalability, maintainability

### Recent Launches (Mention These!)

- **Open Finance** — first-ever Open Finance payment in UAE (Jan 2026)
- **Violet** — business payment product (B2B), growing fast
- **Ziina Card** — Digital Visa card, Apple Wallet + Google Pay, 0% currency fees (Oct 2025)
- **Tap to Pay on Android** — NFC payments (Apr 2025)
- **CommerCity** — Dubai free zone partnership
- **Expansion** — Jordan and Iraq on the roadmap
- **B2B deal pending** — will 2–3x customer base (confirmed by Anton)

-----

## 5. TECHNICAL DEEP DIVE: MODULAR ARCHITECTURE

### Initial Answer (2 min)

> “At IZI we have 20+ modules following clean architecture. The structure is feature-first — each feature module like `:feature:balance`, `:feature:tariffs`, `:feature:profile` contains its own domain, data, and presentation layers. Shared infrastructure lives in separate core modules: `:core:network`, `:core:ui` (design system), `:core:domain`, `:core:auth`, `:core:analytics`.”

### If he asks: “How do feature modules communicate?”

> “Feature modules never depend on each other directly. We use a navigation module — `:core:navigation` — that defines route contracts as interfaces. Each feature registers its routes. For data sharing, we use shared domain interfaces in `:core:domain`. For example, the balance feature exposes a `BalanceRepository` interface in core, but the implementation lives inside `:feature:balance:data`. Other modules depend only on the interface.”

### If he asks: “How do you handle dependency injection across modules?”

> “We use Hilt with `@InstallIn` scopes aligned to module boundaries. Each feature module has its own Hilt module that provides feature-scoped dependencies. Core modules provide singleton-scoped dependencies. The key rule: a feature’s Hilt module can only depend on core module bindings, never on another feature’s bindings.

> Concrete example:
> 
> - `:core:network` provides `ApolloClient` (or in our case `OkHttpClient` + `Retrofit`) as `@Singleton`
> - `:feature:balance` has its own `@Module` that provides `BalanceApi` and `BalanceRepositoryImpl` scoped to `@ActivityRetainedScoped`
> - ViewModel in `:feature:balance` injects `BalanceRepository` interface — doesn’t know about the implementation

> This keeps the dependency graph clean and modules truly isolated.”

### If he asks: “How do you enforce module boundaries?”

> “Three mechanisms:
> 
> 1. **Gradle `implementation` vs `api`** — strict rules. Feature modules use `implementation` for everything internal, only `api` for contracts exposed to `:core:domain`
> 2. **Custom lint rules** — we wrote a lint check that fails the build if a feature module imports classes from another feature module
> 3. **Convention plugins** — we use Gradle convention plugins (`build-logic` module) to standardize build configuration. Every feature module applies the same plugin that sets up Hilt, Compose, testing dependencies consistently.

> Convention plugin example:
> 
> ```
> // build-logic/convention/src/main/kotlin/AndroidFeatureConventionPlugin.kt
> plugins {
>     id("com.android.library")
>     id("kotlin-android")
>     id("dagger.hilt.android.plugin")
> }
> dependencies {
>     implementation(project(":core:ui"))
>     implementation(project(":core:domain"))
>     implementation(project(":core:navigation"))
>     testImplementation(project(":core:testing"))
> }
> ```
> 
> This means creating a new feature module takes 5 minutes, not hours.”

### If he asks: “What were the build time improvements?”

> “Before modularization, a clean build took ~4 minutes and incremental was ~90 seconds because everything got recompiled. After:
> 
> - Clean build: still ~4 minutes (expected — all code still compiles)
> - Incremental build: dropped to ~15-20 seconds because Gradle only recompiles the changed module and its dependents
> - CI parallelization: modules run tests in parallel, cutting CI time by ~60%

> The real win was developer experience — you change something in `:feature:balance`, only that module rebuilds. Before, touching one file could trigger half the project.”

### If he asks: “How do you handle navigation?”

> “We use a centralized navigation approach. `:core:navigation` defines sealed classes for routes:
> 
> ```kotlin
> sealed class AppRoute {
>     data object Balance : AppRoute()
>     data class TransactionDetail(val id: String) : AppRoute()
>     data class Profile(val userId: String) : AppRoute()
> }
> ```
> 
> The `:app` module wires everything together in a `NavHost`. Each feature module provides a composable `NavGraphBuilder` extension:
> 
> ```kotlin
> // In :feature:balance
> fun NavGraphBuilder.balanceGraph(onNavigate: (AppRoute) -> Unit) {
>     composable("balance") {
>         BalanceScreen(onTransactionClick = { id ->
>             onNavigate(AppRoute.TransactionDetail(id))
>         })
>     }
> }
> ```
> 
> This way feature modules don’t know about each other — they just emit navigation events, and the app module handles routing.”

### Connection to Ziina:

> “This architecture translates directly to Ziina’s needs. With B2B scaling 2-3x, you’ll need features to be independently deployable and testable. A properly modularized codebase means you can have engineers working on Violet (B2B) without touching the consumer wallet, and vice versa.”

-----

## 6. TECHNICAL DEEP DIVE: JETPACK COMPOSE

### Initial Answer (2 min)

> “I migrated IZI from Views to Compose incrementally over about 6 months. Started with new features in pure Compose, then gradually replaced existing screens. We now do all new UI in Compose. The migration was guided by a key rule: never mix View and Compose in the same screen — clean boundaries at the screen level.”

### If he asks: “How do you handle recomposition performance?”

> “This is the core challenge with Compose. The framework has three phases: Composition (building the tree), Layout (measuring/positioning), and Drawing (rendering pixels). Most performance issues happen in Composition — unnecessary recomposition.

> My approach:
> 
> **1. Stability first.** I ensure data classes passed to composables are stable. If Compose can’t guarantee a type is stable, it recomposes every time. Since Kotlin 2.0.20+, Strong Skipping Mode helps a lot — it uses reference equality (`===`) for unstable types, so if the same instance is passed, it skips. But it still fails for derived data that creates new instances.
> 
> Concrete example: if you pass `users.filter { it.isActive }` directly to a composable, every recomposition creates a new list instance. Even with Strong Skipping, `oldList !== newList` means it recomposes. The fix: wrap in `@Immutable` data class or use `remember` with a key:
> 
> ```kotlin
> val activeUsers = remember(users) { users.filter { it.isActive } }
> ```
> 
> **2. `derivedStateOf` for computed state.** When state changes frequently but the derived value changes rarely:
> 
> ```kotlin
> val showButton = remember {
>     derivedStateOf { scrollState.value > 100 }
> }
> ```
> 
> Without this, the composable recomposes on every scroll pixel. With `derivedStateOf`, it only recomposes when the boolean actually changes.
> 
> **3. Defer state reads.** Pass lambdas instead of values for frequently changing state:
> 
> ```kotlin
> // BAD — recomposes on every offset change
> Modifier.offset(x = offset)
> 
> // GOOD — reads state only in Layout phase
> Modifier.offset { IntOffset(x = offset.value, y = 0) }
> ```
> 
> This moves the state read from Composition phase to Layout phase, so Composition never needs to re-run.
> 
> **4. Keys in LazyColumn.** Always provide stable keys and contentType:
> 
> ```kotlin
> LazyColumn {
>     items(items, key = { it.id }, contentType = { it.type }) { item ->
>         TransactionItem(item)
>     }
> }
> ```
> 
> Without keys, Compose can’t track item identity across recomposition — insertions and deletions cause the entire list to recompose.”

### If he asks: “What tools do you use to debug recomposition?”

> “Several layers:
> 
> 1. **Layout Inspector** in Android Studio — shows recomposition counts per composable. A rising counter on a static element is a red flag
> 2. **Compose Compiler Metrics** — generates reports showing which composables are skippable and which parameters are unstable:
>    
>    ```
>    ./gradlew assembleRelease -PcomposeCompilerReports=true
>    ```
>    
>    This produces `.txt` reports showing exactly why a composable is non-skippable
> 3. **System Tracing with Perfetto** — visualize the three phases (Composition, Layout, Drawing) per frame. Long bars show where jank comes from
> 4. **Recomposition highlighting** in Android Studio — visual overlay, green = normal, red = excessive
> 
> In practice, I start with Layout Inspector when I notice jank, then use Compiler Metrics to find unstable types, and Perfetto for frame-level analysis.”

### If he asks: “How do you handle Compose state management?”

> “We follow unidirectional data flow with MVVM. The pattern:
> 
> ```kotlin
> @HiltViewModel
> class BalanceViewModel @Inject constructor(
>     private val getBalanceUseCase: GetBalanceUseCase
> ) : ViewModel() {
> 
>     private val _uiState = MutableStateFlow(BalanceUiState())
>     val uiState = _uiState.asStateFlow()
> 
>     fun onEvent(event: BalanceEvent) {
>         when (event) {
>             is BalanceEvent.Refresh -> loadBalance()
>             is BalanceEvent.TransactionClick -> { /* navigate */ }
>         }
>     }
> }
> 
> @Composable
> fun BalanceScreen(viewModel: BalanceViewModel = hiltViewModel()) {
>     val uiState by viewModel.uiState.collectAsStateWithLifecycle()
>     BalanceContent(
>         state = uiState,
>         onEvent = viewModel::onEvent
>     )
> }
> 
> @Composable
> private fun BalanceContent(
>     state: BalanceUiState,
>     onEvent: (BalanceEvent) -> Unit
> ) {
>     // Pure UI — no ViewModel dependency, easily testable
> }
> ```
> 
> Key principles:
> 
> - **State hoisting**: UI state lives in ViewModel, UI is stateless
> - **Event-driven**: UI sends events up, state flows down
> - **Separation**: `BalanceContent` is a pure composable — takes data, emits events. Easy to preview, easy to test
> - **`collectAsStateWithLifecycle`**: respects lifecycle — pauses collection when app is backgrounded, saves battery”

### If he asks about Compose interop with Views:

> “During migration, the key was clean boundaries. We never mixed Compose and Views within a single screen. Either the screen was fully Compose or fully View. At the interface level:
> 
> - `ComposeView` in XML layouts for embedding Compose in View screens
> - `AndroidView` composable for cases where we needed a View inside Compose (e.g., MapView)
> 
> The migration order: design system components first (buttons, cards, inputs), then new features in Compose, then existing screens one-by-one during refactoring sprints. We prioritized screens with the most frequent changes since they benefited most from Compose’s declarative approach.”

-----

## 7. TECHNICAL DEEP DIVE: KOTLIN COROUTINES & FLOW

### Initial Answer

> “Coroutines are fundamental to our architecture. Every async operation uses coroutines with structured concurrency. The key is proper scope management — ViewModels use `viewModelScope`, use cases use `withContext` for thread switching.”

### If he asks: “How do you handle error handling in coroutines?”

> “We use structured concurrency with `SupervisorJob` where failures in one child shouldn’t cancel siblings. For ViewModel scopes, the default `viewModelScope` uses `SupervisorJob`, which is correct.
> 
> Our pattern for error handling:
> 
> ```kotlin
> sealed class Result<out T> {
>     data class Success<T>(val data: T) : Result<T>()
>     data class Error(val exception: Throwable) : Result<Nothing>()
> }
> 
> // In use case
> class GetBalanceUseCase @Inject constructor(
>     private val repository: BalanceRepository
> ) {
>     suspend operator fun invoke(): Result<Balance> = try {
>         Result.Success(repository.getBalance())
>     } catch (e: CancellationException) {
>         throw e // CRITICAL: never catch CancellationException
>     } catch (e: Exception) {
>         Result.Error(e)
>     }
> }
> ```
> 
> The critical rule: **never catch `CancellationException`**. It breaks structured concurrency — coroutine cancellation propagation stops working. I’ve seen this bug in production at IZI — a caught cancellation exception caused a memory leak because the coroutine never cleaned up.”

### If he asks: “How do you use Flow?”

> “We use Flow extensively for reactive data streams:
> 
> **1. Repository layer — `flow { }` or `callbackFlow { }` for data sources:**
> 
> ```kotlin
> fun observeBalance(): Flow<Balance> = flow {
>     while (true) {
>         emit(api.getBalance())
>         delay(30_000) // Poll every 30s
>     }
> }
> ```
> 
> **2. Combining multiple flows:**
> 
> ```kotlin
> val uiState: StateFlow<DashboardState> = combine(
>     balanceRepository.observeBalance(),
>     transactionRepository.observeRecentTransactions(),
>     userRepository.observeProfile()
> ) { balance, transactions, profile ->
>     DashboardState(balance, transactions, profile)
> }.stateIn(
>     scope = viewModelScope,
>     started = SharingStarted.WhileSubscribed(5000),
>     initialValue = DashboardState.Loading
> )
> ```
> 
> **3. `WhileSubscribed(5000)`** — stops upstream collection 5 seconds after the last subscriber disappears. This is crucial for configuration changes (screen rotation) — keeps the flow alive during brief interruptions but cleans up if the user actually leaves.
> 
> **4. `flatMapLatest` for search:**
> 
> ```kotlin
> val searchResults = searchQuery
>     .debounce(300)
>     .distinctUntilChanged()
>     .flatMapLatest { query ->
>         if (query.isBlank()) flowOf(emptyList())
>         else repository.search(query)
>     }
>     .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())
> ```"
> ```

### If he asks: “How do you handle threading?”

> “We follow a simple rule: use cases and repositories switch to the appropriate dispatcher internally. ViewModels never specify dispatchers — they stay on Main.
> 
> ```kotlin
> class TransactionRepositoryImpl @Inject constructor(
>     private val api: TransactionApi,
>     private val db: TransactionDao,
>     @IoDispatcher private val ioDispatcher: CoroutineDispatcher
> ) : TransactionRepository {
> 
>     override suspend fun getTransactions(): List<Transaction> =
>         withContext(ioDispatcher) {
>             val cached = db.getAll()
>             if (cached.isNotEmpty()) return@withContext cached
>             val remote = api.fetchTransactions()
>             db.insertAll(remote)
>             remote
>         }
> }
> ```
> 
> The dispatchers are injected via Hilt, which makes testing easy — in tests we inject `UnconfinedTestDispatcher` or `StandardTestDispatcher` instead of `Dispatchers.IO`.”

-----

## 8. TECHNICAL DEEP DIVE: GRAPHQL & APOLLO KOTLIN

> **HONEST FRAMING:** “I haven’t used GraphQL in production, but I’ve studied Apollo Kotlin in depth because it’s in your stack, and my networking architecture experience translates directly.”

### How Apollo Kotlin works (show you’ve done homework):

> “Apollo Kotlin (v4.x) is a strongly-typed GraphQL client with code generation. You define `.graphql` query files, and the Gradle plugin generates Kotlin data classes and type-safe query builders. It’s similar to how I’ve used Moshi or Kotlinx Serialization with codegen — schema-first approach.
> 
> The setup in a modular project:
> 
> ```kotlin
> // build.gradle.kts
> plugins {
>     id("com.apollographql.apollo") version "4.4.1"
> }
> dependencies {
>     implementation("com.apollographql.apollo:apollo-runtime:4.4.1")
>     implementation("com.apollographql.apollo:apollo-normalized-cache-sqlite:4.4.1")
> }
> apollo {
>     service("ziina") {
>         packageName.set("com.ziina.graphql")
>         schemaFile.set(file("src/main/graphql/schema.graphqls"))
>     }
> }
> ```"
> ```

### Normalized Cache (this is the KEY differentiator vs REST):

> “The biggest shift from REST is the normalized cache. With REST, you cache by endpoint URL. With GraphQL, the normalized cache breaks each response into individual objects stored by ID.
> 
> Example: if `GetDashboard` query returns user balance and `GetTransactionDetail` returns the same user object, they share a single cache entry. Update the user in one place, both queries get the fresh data.
> 
> Two cache options:
> 
> - **MemoryCache** — LRU in-memory, lost on app kill
> - **SqlNormalizedCache** — SQLite-backed via SQLDelight, persists across sessions
> 
> For a fintech app like Ziina, I’d use both — chained:
> 
> ```kotlin
> val cacheFactory = MemoryCacheFactory(10 * 1024 * 1024)
>     .chain(SqlNormalizedCacheFactory(context, "apollo.db"))
> 
> val apolloClient = ApolloClient.Builder()
>     .serverUrl("https://api.ziina.com/graphql")
>     .normalizedCache(cacheFactory)
>     .build()
> ```
> 
> Memory cache for speed, SQLite for persistence. Reads check memory first, fall back to SQLite, then network.”

### Fetch Policies:

> “Apollo Kotlin has several fetch policies that map to real UX patterns:
> 
> - **CacheFirst** (default with normalized cache) — show cached data immediately, great for perceived performance
> - **NetworkFirst** — for payment-critical screens where stale data is dangerous
> - **CacheAndNetwork** — show cache immediately, update when network responds. Perfect for balance display: show last known balance instantly, update when fresh data arrives
> - **NetworkOnly** — for mutations and sensitive operations
> - **CacheOnly** — for offline mode
> 
> ```kotlin
> // Balance screen — show cached, then update
> apolloClient.query(GetBalanceQuery())
>     .fetchPolicy(FetchPolicy.CacheAndNetwork)
>     .toFlow()
>     .collect { response ->
>         updateUi(response.data)
>     }
> ```"
> ```

### GraphQL Subscriptions (real-time data):

> “For real-time features like payment notifications, Apollo Kotlin supports GraphQL subscriptions over WebSocket:
> 
> ```kotlin
> apolloClient.subscription(OnPaymentReceivedSubscription())
>     .toFlow()
>     .collect { response ->
>         showNotification(response.data?.paymentReceived)
>     }
> ```
> 
> I’ve used WebSockets at IZI for real-time balance updates — the concept is identical, just with GraphQL’s typed schema layer on top.”

### How this maps to my REST experience:

> “The mental model shift is: **graph thinking vs endpoint thinking**.
> 
> - REST normalized cache → Apollo normalized cache (same concept, better implementation)
> - Retrofit code generation → Apollo code generation from `.graphql` files
> - OkHttp interceptors → Apollo interceptors (same chain pattern)
> - Multiple REST calls → single GraphQL query with nested fields
> - WebSocket for real-time → GraphQL subscriptions
> 
> The fundamentals I built at IZI — modular networking layer, cache strategies, error handling, offline support — all transfer. The tooling changes, the engineering principles don’t.”

-----

## 9. TECHNICAL DEEP DIVE: FINTECH SECURITY & BIOMETRICS

### Initial Answer

> “At IZI we handle financial transactions for 2 million users. Security isn’t a feature — it’s the foundation. Every payment flow goes through biometric authentication, and we use Android Keystore for all cryptographic operations.”

### If he asks: “How did you implement biometric authentication?”

> “We use the `BiometricPrompt` API with `CryptoObject` for cryptographically-backed biometric auth. This is critical for fintech — simple biometric confirmation (just checking ‘is this the right person’) isn’t enough. You need to tie the biometric to a cryptographic operation.
> 
> The flow:
> 
> 1. Generate an AES key in Android Keystore with `setUserAuthenticationRequired(true)` — key can only be used after successful biometric auth
> 2. Create a `Cipher` instance initialized with that key
> 3. Pass the Cipher as `BiometricPrompt.CryptoObject(cipher)`
> 4. On success, use the authenticated cipher to encrypt/decrypt sensitive data (payment tokens, session keys)
> 
> ```kotlin
> // Key generation
> val keyGenerator = KeyGenerator.getInstance(
>     KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore"
> )
> keyGenerator.init(
>     KeyGenParameterSpec.Builder("payment_key",
>         KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
>         .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
>         .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
>         .setUserAuthenticationRequired(true)
>         .setUserAuthenticationParameters(30, // valid for 30 seconds
>             KeyProperties.AUTH_BIOMETRIC_STRONG)
>         .setInvalidatedByBiometricEnrollment(true) // re-enroll if biometrics change
>         .build()
> )
> keyGenerator.generateKey()
> ```
> 
> The key stays in hardware-backed Keystore (StrongBox if device supports it). Even if the device is rooted, the key can’t be extracted — it never leaves the secure enclave.
> 
> For Ziina, this is directly applicable — payment confirmations, fund transfers, anything above a threshold should require biometric auth tied to a CryptoObject.”

### If he asks: “What about data encryption at rest?”

> “We encrypt all sensitive data stored locally:
> 
> - **EncryptedSharedPreferences** — for tokens, session data, small key-value pairs. Uses AES-256/GCM with a master key in Android Keystore
> - **SQLCipher for Room** — if local database stores sensitive data, SQLCipher encrypts the entire database file
> - **DataStore with encryption** — for structured preferences, using EncryptedFile under the hood
> 
> Key management rule: encryption keys never exist in application memory longer than necessary. We clear byte arrays after use (`key.fill(0)`) to minimize the window for memory dump attacks.
> 
> For network communication:
> 
> - **Certificate pinning** via OkHttp’s `CertificatePinner` — prevents MITM even with compromised CA
> - **TLS 1.3** minimum
> - **No sensitive data in URL parameters** — everything in request body”

### If he asks: “How do you handle root/jailbreak detection?”

> “We implement multi-layer detection:
> 
> 1. **SafetyNet / Play Integrity API** — Google’s server-side device attestation. Checks device integrity, bootloader status, CTS profile match
> 2. **Local checks** — Superuser binary detection, test-keys in build fingerprint, Magisk Hide detection
> 3. **Runtime checks** — hooking framework detection (Xposed, Frida), debugger attachment detection
> 
> But the key principle is: **don’t rely solely on client-side detection**. A determined attacker can bypass any client check. The real security is server-side — rate limiting, anomaly detection, transaction verification. Client-side checks raise the bar, server-side checks enforce it.”

### If he asks: “ProGuard/R8 obfuscation?”

> “We use R8 with aggressive settings:
> 
> - Full code shrinking and optimization
> - Class/method/field name obfuscation
> - String encryption for sensitive strings (API endpoints, keys)
> - Custom ProGuard rules per module — each feature module has its own `proguard-rules.pro`
> - We keep obfuscation mappings in CI artifacts for crash symbolication
> 
> For fintech specifically, obfuscation makes reverse engineering harder — attackers can’t easily understand payment flow logic or find hardcoded endpoints.”

-----

## 10. TECHNICAL DEEP DIVE: PERFORMANCE OPTIMIZATION

### Initial Answer (cold start story)

> “At IZI, our app startup time had degraded to 4+ seconds as we added modules. I profiled with Perfetto and found two root causes: eager DI initialization and heavy work on the main thread during `Application.onCreate()`.”

### If he asks: “Walk me through the diagnosis and fix”

> “**Diagnosis:**
> 
> 1. Captured a Perfetto trace of cold start
> 2. Identified long blocks on the main thread in `Application.onCreate()`: DI graph initialization, analytics SDK init, crash reporting init, network client creation
> 3. Measured: Hilt was eagerly creating 15+ singletons, many of which weren’t needed until much later
> 
> **Fixes (each with measured impact):**
> 
> 4. **Lazy DI initialization** — converted heavy singletons from eager to `@Inject lateinit var` with `dagger.Lazy<T>` wrapper. Only `Auth`, `CrashReporting`, and `Analytics` init on startup. Everything else initializes on first use. **Impact: -1.2s**
> 5. **Background initialization** — moved non-UI-blocking work to background thread:
>    
>    ```kotlin
>    class App : Application() {
>        override fun onCreate() {
>            super.onCreate()
>            // Critical path: only what's needed for first frame
>            initCrashReporting()
>            initAuth()
>    
>            // Background: everything else
>            lifecycleScope.launch(Dispatchers.Default) {
>                initAnalytics()
>                initFeatureFlags()
>                preloadFonts()
>            }
>        }
>    }
>    ```
>    
>    **Impact: -0.5s**
> 6. **Baseline Profiles** — created app-specific Baseline Profile for critical startup path + main screens. AOT-compiles hot paths on install. **Impact: -0.3s**
> 7. **Splash screen optimization** — used `SplashScreen` API to show brand while initializing, so perceived startup feels instant even if actual init takes time
> 
> **Total: 4.0s → 2.4s cold start (40% improvement)**”

### If he asks: “How do you monitor performance in production?”

> “Three layers:
> 
> 1. **Firebase Performance Monitoring** — automated traces for startup, screen rendering, network calls. Custom traces for critical flows (payment completion, balance load)
> 2. **ANR monitoring** — track Application Not Responding events. We target <0.1% ANR rate
> 3. **Custom metrics** — we send frame rendering metrics from Compose (jank frame count) to our analytics backend
> 
> Key SLIs we track:
> 
> - Cold start P50 / P95
> - Screen render time (time to first meaningful frame)
> - Network request latency P50 / P95
> - Crash-free rate (target: 99.2%+)
> - ANR rate (target: <0.1%)
> 
> Every release, I compare these metrics against the previous version before widening rollout.”

### If he asks about memory optimization:

> “We use LeakCanary in debug builds to catch leaks during development. In production:
> 
> - **Strict lifecycle management** — coroutines tied to `viewModelScope` or `lifecycleScope`, never global scope
> - **Image loading** — Coil with proper caching and downsampling. For lists, we use `size(targetWidth, targetHeight)` to avoid loading full-resolution images
> - **RecyclerView/LazyColumn optimization** — proper view recycling, avoid allocations in `onBind`/composable functions
> - **Large object monitoring** — LeakCanary Square’s Shark library for automated heap analysis in CI”

-----

## 11. TECHNICAL DEEP DIVE: TESTING STRATEGY

### Initial Answer

> “Three levels: unit tests for business logic, integration tests for data layer, UI tests for critical user flows. For a fintech app, payment flows get the heaviest coverage — these can’t break.”

### If he asks: “Give me specifics on unit testing”

> “Our stack: **JUnit 5 + MockK + Turbine** (for Flow testing).
> 
> ViewModel testing pattern:
> 
> ```kotlin
> @Test
> fun `when refresh triggers, balance updates`() = runTest {
>     // Arrange
>     val balance = Balance(amount = 1000.0, currency = "AED")
>     coEvery { getBalanceUseCase() } returns Result.Success(balance)
>     val viewModel = BalanceViewModel(getBalanceUseCase)
> 
>     // Act & Assert
>     viewModel.uiState.test {
>         assertEquals(BalanceUiState.Loading, awaitItem())
>         viewModel.onEvent(BalanceEvent.Refresh)
>         val result = awaitItem()
>         assertEquals(1000.0, result.balance.amount)
>     }
> }
> ```
> 
> **Turbine** is critical for testing Flows — it gives you `awaitItem()`, `awaitError()`, `awaitComplete()` with proper coroutine test support. Without it, testing StateFlow is flaky.
> 
> **MockK over Mockito** because: better Kotlin support, coroutine mocking with `coEvery`, sealed class support, more readable syntax.”

### If he asks about Compose UI testing:

> “We use Compose test rules for UI testing:
> 
> ```kotlin
> @get:Rule
> val composeRule = createComposeRule()
> 
> @Test
> fun balanceScreen_showsAmount() {
>     composeRule.setContent {
>         BalanceContent(
>             state = BalanceUiState(balance = Balance(1000.0, "AED")),
>             onEvent = {}
>         )
>     }
> 
>     composeRule.onNodeWithText("1,000.00 AED").assertIsDisplayed()
>     composeRule.onNodeWithContentDescription("Refresh").performClick()
> }
> ```
> 
> Key principle: we test the stateless composable (`BalanceContent`), not the screen with ViewModel. This makes tests fast and deterministic — no DI, no real data, no flakiness.
> 
> For visual regression, we use **screenshot testing** with Paparazzi (JVM-based, no emulator needed). It captures composable screenshots and diffs against golden files. We use this extensively for design system components — if someone changes the Button, every screen screenshot test catches it.”

### If he asks about integration testing:

> “For the data layer, we test real Room database operations and mock the API:
> 
> ```kotlin
> @Test
> fun repository_cachesNetworkResponse() = runTest {
>     val db = Room.inMemoryDatabaseBuilder(context, AppDatabase::class.java).build()
>     val mockApi = MockWebServer() // or mockk<TransactionApi>()
>     val repo = TransactionRepositoryImpl(api, db.transactionDao(), testDispatcher)
> 
>     val result = repo.getTransactions()
> 
>     // Verify data came from network
>     assertEquals(3, result.size)
>     // Verify it was cached
>     assertEquals(3, db.transactionDao().getAll().size)
> }
> ```
> 
> For API testing, we use MockWebServer to simulate real HTTP responses, including error cases (timeouts, 500s, malformed JSON). This catches issues that mock objects miss.”

-----

## 12. TECHNICAL DEEP DIVE: CI/CD & RELEASE ENGINEERING

### Initial Answer

> “We have a multi-stage pipeline on every PR, with staged rollouts for production releases.”

### If he asks for details:

> “**PR Pipeline (runs on every push):**
> 
> 1. **Static analysis** — detekt (Kotlin linting), custom lint rules, Android Lint
> 2. **Build** — assemble debug + release (catches build config issues early)
> 3. **Unit tests** — all modules in parallel (modular architecture pays off here)
> 4. **Screenshot tests** — Paparazzi diffs against golden files
> 5. **Danger checks** — automated PR review bot: checks for missing tests on new files, large PR warnings, migration file detection
> 
> **Merge to `develop`:**
> 6. **Integration tests** — Room + API tests on emulator
> 7. **Instrumented UI tests** — critical flow smoke tests
> 
> **Release Pipeline:**
> 8. **Build release APK/AAB** with R8 optimization
> 9. **Upload to Google Play** via Gradle Play Publisher plugin
> 10. **Staged rollout:**
> - Day 1: 1% — monitor crash rate, ANR rate
> - Day 2-3: 10% — check performance metrics, user feedback
> - Day 4-5: 50% — broader monitoring
> - Day 6-7: 100% — full release
> 11. **Halt threshold:** if crash-free drops below 99.0% OR ANR rate exceeds 0.2%, auto-halt rollout and create P1 incident
> 
> **Release cadence:** Weekly releases every Tuesday. Hotfixes can be pushed same-day via fast-track pipeline (skip screenshot tests, full integration suite).”

### If he asks: “How do you handle feature flags?”

> “We use a remote config system for feature flags:
> 
> - **Server-driven flags** — Firebase Remote Config or custom backend config
> - **Local flag interface** — debug menu in dev builds for toggling features
> - **Compile-time flags** — for features that shouldn’t ship yet, use Gradle build config: `buildConfigField("Boolean", "FEATURE_X", "false")`
> 
> This enables:
> 
> - **Trunk-based development** — everyone merges to main, unfinished features behind flags
> - **Gradual rollout** — enable feature for 5% of users, measure, expand
> - **Kill switch** — disable a broken feature without deploying a new build
> 
> For Ziina’s B2B launch, this is critical — you can test Violet features with a subset of business users before wider release.”

-----

## 13. TECHNICAL DEEP DIVE: SCALABILITY FOR B2B GROWTH

> **Context:** Anton confirmed Ziina’s B2B deal will 2-3x the customer base. This is their #1 priority.

### If he asks: “How would you prepare an Android app for 2-3x user growth?”

> “Scaling an Android app isn’t just about backend — the client needs to handle it too. From my experience scaling IZI from 500K to 2M users, here’s what matters:
> 
> **1. Offline-first architecture:**
> When you have more users, you have more users on poor connections. The app should work offline for core read flows:
> 
> - Cache balance and transaction history locally (Room or GraphQL normalized cache)
> - Queue mutations (payments, transfers) and sync when connectivity returns
> - Show clear UI states for offline vs syncing vs online
> 
> **2. Pagination everywhere:**
> At 260K users, you might load all transactions at once. At 600K+, that breaks. Every list needs cursor-based pagination:
> 
> ```kotlin
> // GraphQL cursor pagination
> query GetTransactions($cursor: String, $limit: Int) {
>     transactions(after: $cursor, first: $limit) {
>         edges { node { id, amount, date } }
>         pageInfo { endCursor, hasNextPage }
>     }
> }
> ```
> 
> **3. Background sync efficiency:**
> More users = more push notifications, more background syncs. Use WorkManager with constraints:
> 
> ```kotlin
> val syncWork = PeriodicWorkRequestBuilder<BalanceSyncWorker>(15, TimeUnit.MINUTES)
>     .setConstraints(Constraints.Builder()
>         .setRequiredNetworkType(NetworkType.CONNECTED)
>         .setRequiresBatteryNotLow(true)
>         .build())
>     .build()
> ```
> 
> **4. App size optimization:**
> Serve different APKs for different device configs:
> 
> - **App Bundle** — Google Play generates optimized APKs per device
> - **Dynamic feature modules** — load B2B features on-demand, consumer users don’t carry that code
> - **Resource optimization** — WebP images, vector drawables, ProGuard aggressive tree-shaking
> 
> **5. Multi-tenant considerations for B2B:**
> Business accounts vs consumer accounts may need different UI, different feature sets, different limits. Architecture should support this via feature flags and configuration, not code branching.
> 
> At IZI, the modular architecture was key — when we added new service tiers, each tier was a feature module. Same principle applies to Ziina’s consumer vs Violet (B2B) split.”

-----

## 14. TECHNICAL DEEP DIVE: JAVA → KOTLIN MIGRATION

### Initial Answer

> “I led the full codebase migration at IZI. Incremental over 6 months. Never stopped shipping features.”

### If he digs deeper:

> “**Strategy: Bottom-up, layer by layer.**
> 
> Phase 1 (Weeks 1-3): **Utilities and data models**
> 
> - Started with data classes — Java POJOs to Kotlin data classes. Immediate 50% code reduction per file.
> - Extension functions replaced Java utility classes
> - Kotlin/Java interop is seamless here — Kotlin calls Java, Java calls Kotlin, no issues
> 
> Phase 2 (Weeks 4-8): **Business logic / Use cases**
> 
> - Converted use cases, repositories. This is where null safety paid off most — eliminated entire categories of NPE bugs
> - Introduced sealed classes for Result types replacing Java enums with data
> - Coroutines replaced RxJava (gradual migration: `kotlinx-coroutines-rx2` bridge for interop during transition)
> 
> Phase 3 (Weeks 9-16): **Presentation layer**
> 
> - ViewModels, Adapters, Fragments converted
> - This was the hardest because of tight coupling to Android framework
> - Key learning: don’t just convert Java syntax to Kotlin. Rewrite idiomatically — scope functions, sealed classes, extension functions, null-safe chains
> 
> Phase 4 (Ongoing): **New code only in Kotlin**
> 
> - Added ktlint rule to block `.java` file creation in PRs
> - Any Java file touched for a bug fix gets migrated as part of the fix
> 
> **Results:**
> 
> - 35% code reduction (dead code + Kotlin conciseness)
> - ~70% reduction in NPE crashes in first month
> - Developer productivity increase — new features shipped faster
> - Code review time decreased — Kotlin is more readable
> 
> **What I’d do differently:** I’d establish Kotlin coding conventions document BEFORE starting, not halfway through. Early migration PRs had inconsistent style that we had to go back and fix.”

-----

## 15. TECHNICAL DEEP DIVE: AR/3D WORK AT SEAMM

### Initial Answer

> “I was the sole Android developer at Seamm, a San Francisco fashion-tech startup. Built an AR try-on feature from scratch — Snapchat Camera Kit for face/body tracking, Google Filament for 3D model rendering.”

### If he asks for technical depth:

> “**Architecture:**
> 
> - Camera pipeline: Snapchat Camera Kit provides the camera feed with real-time body/face tracking
> - 3D rendering: Google Filament (PBR engine) renders product models (jewelry, glasses, accessories) on the tracked positions
> - Rendering pipeline: Camera frame → tracking data → 3D model transform → Filament render → composite onto camera preview → display
> 
> **Performance optimization (the hardest part):**
> The challenge was mid-range devices — rendering 3D PBR models at 30fps while maintaining smooth camera feed.
> 
> 1. **LOD (Level of Detail) switching** — three versions of each model: high (5K triangles), medium (2K), low (500). System auto-selects based on device GPU capability at startup and distance at runtime
> 2. **Asset preloading** — 3D models loaded and compiled into Filament’s binary format during app startup, not when user opens camera. Cold load of a model: ~2s. Preloaded: <100ms
> 3. **Texture compression** — ASTC compressed textures for GPUs that support it (most modern Android). Fallback to ETC2. Reduced GPU memory usage by ~60%
> 4. **Frame budget management** — Filament render pass must complete within 16ms (60fps target) or 33ms (30fps fallback). Monitored with custom frame timing and dynamically reduced quality if budget exceeded
> 
> **Business result:** 2M+ social media shares, 60% sales conversion uplift. The feature became the startup’s core differentiator.
> 
> **What this shows for Ziina:** Although Ziina doesn’t do AR, the skills transfer: performance optimization under constraints, working with complex rendering pipelines, shipping consumer-facing features with high quality standards, and sole ownership of a critical platform.”

-----

## 16. BEHAVIORAL QUESTIONS

Yura as a team lead wants to understand: **what’s it like to work with you on the same team?**

-----

### Q: “Tell me about a time you disagreed with a technical decision”

> “At IZI, the backend team wanted to push complex business logic to the client to speed up delivery. Specifically — tariff calculation logic. Their argument: faster to implement without backend changes.
> 
> I disagreed for three reasons: (1) maintenance burden — we’d need the same logic on iOS, (2) business rules change frequently — each change would require app update with review time, (3) testability — critical financial calculations should live where we control deployment.
> 
> I didn’t just say no — I proposed a sync meeting with backend, iOS lead, and product. We mapped out the responsibilities: backend owns all business rules and calculations, client focuses on presentation and user experience. We defined a clear API contract.
> 
> It took an extra sprint upfront to build the backend endpoints, but saved us months of cross-platform bugs and inconsistencies. The pattern became our standard: **thin client, smart server**.”

**Why this works for Ziina:** Shows you push back constructively with data, propose solutions, and think about long-term maintenance — exactly what they need scaling B2B with a small team.

-----

### Q: “How do you handle tight deadlines?”

> “At Seamm, we had 3 weeks to ship the AR try-on for a major client demo. This was a do-or-die feature for the startup.
> 
> I broke it into three tiers:
> 
> - **Must-have:** Camera with tracking overlay, one 3D model rendering correctly (P0)
> - **Should-have:** Multiple models, smooth transitions between products (P1)
> - **Nice-to-have:** Social sharing, screenshot with branding (P2)
> 
> Shipped P0 + most of P1 on time. The demo was successful — client signed. Polish and P2 came in the following sprint. The feature eventually drove 2M social shares and 60% conversion uplift.
> 
> The lesson: scope ruthlessly, communicate trade-offs clearly, ship the core experience first.”

-----

### Q: “How do you work with designers/product?”

> “I push back early if something is technically expensive relative to its value — not to say no, but to offer alternatives.
> 
> Example at IZI: designer wanted a complex nested scroll with parallax headers, animated transitions between card states, and spring physics. Full implementation: ~2 weeks for one screen.
> 
> I prototyped a simpler version in Compose in 2 hours that achieved 90% of the visual effect. Shared a screen recording. Designer loved it and agreed the trade-off was worth it.
> 
> At Ziina this matters especially — you have 8 design awards. The bar for UI quality is high, but the team is small. Finding the sweet spot between visual excellence and engineering velocity is critical. I think of my role as a **design partner**, not a design executor — I bring implementation perspective to design decisions.”

-----

### Q: “Tell me about mentoring or leading other engineers”

> “At IZI, I established several practices:
> 
> **Code review culture:** Reviews focus on architecture decisions, not just formatting. Every PR gets a review with comments categorized: 🔴 must-fix (blocking), 🟡 should-fix (non-blocking), 💬 discussion (optional). This removes ambiguity about what needs to change.
> 
> **Kotlin conventions document:** Created a living document of team-agreed patterns — coroutine scope usage, naming conventions, module structure rules. New developers read it day one.
> 
> **Onboarding:** I pair with new developers for their first week on a real feature — not a toy project. They ship something meaningful in their first sprint. This builds confidence and teaches the codebase faster than documentation. I pick a feature that touches 2-3 modules so they see the architecture in practice.
> 
> **Knowledge sharing:** Monthly tech talks where anyone presents something they learned. I presented on Compose migration lessons and coroutine pitfalls.”

-----

### Q: “Tell me about a production incident”

> “Post-release crash spike affecting balance display. Crash rate jumped from 99.2% to 98.5% within 2 hours.
> 
> **Detection:** Firebase Crashlytics alert triggered. I checked immediately — `IllegalStateException` in balance ViewModel.
> 
> **Root cause:** Race condition between two coroutines. One fetched user profile, another fetched balance. Both wrote to the same `MutableStateFlow`. On slower devices, the profile coroutine completed first and set state to a profile-only object, then the balance coroutine tried to update assuming profile was already in state — but a different profile object. The `copy()` call on the StateFlow value had a stale reference.
> 
> **Fix:** Restructured to use `combine()` on two separate StateFlows instead of mutating a shared one:
> 
> ```kotlin
> // BEFORE (buggy): both coroutines mutating one StateFlow
> _state.value = _state.value.copy(balance = newBalance)
> 
> // AFTER (correct): combine separate streams
> val uiState = combine(profileFlow, balanceFlow) { profile, balance ->
>     DashboardState(profile = profile, balance = balance)
> }.stateIn(viewModelScope, ...)
> ```
> 
> **Timeline:** Caught at hour 2, root cause identified by hour 3, hotfix PR at hour 4, fast-tracked to production by hour 6.
> 
> **Prevention:** Added regression test, introduced team-wide rule: never use `_state.value = _state.value.copy(...)` from multiple coroutines. Use `combine()` or `MutableStateFlow.update { }` (atomic) instead. Added custom lint rule to flag the anti-pattern.”

-----

## 17. MOTIVATION — “WHY ZIINA?”

### Q: “Why Ziina?”

> “Three things.
> 
> **First — the mission resonates.** I built IZI which serves 2 million people with financial services in Kazakhstan. I understand the impact of making finance accessible. Ziina is doing the same for the Middle East at a bigger scale — 560K SMEs in UAE alone, $80-90B GDP impact from Open Finance.
> 
> **Second — the stage.** You’re at the inflection point — Open Finance launch, the B2B partnership that will 2-3x the customer base, expansion to Jordan and Iraq. This is exactly when a senior engineer can have maximum impact. At 25 people, I’m not employee #500 filing JIRAs — I’m shaping the product and architecture.
> 
> **Third — Dubai.** It’s not a temporary move. I want to build my career here long-term. Ziina’s trajectory — YC backed, Series A, Central Bank license, Nubank of the region vision — combined with Dubai’s fintech ecosystem, is exactly where I want to be for the next 5+ years.”

-----

### Q: “Why are you leaving your current role?”

> “I’ve accomplished what I set out to do at IZI — migrated to Kotlin, built the modular architecture, scaled to 2 million users, established quality practices at 99.2% crash-free. The product is stable and mature.
> 
> I’m looking for the next challenge: bigger scale, more complex problems, and a market with more growth potential. Ziina’s growth trajectory — 10x YoY volume, B2B expansion — is exactly that challenge.”

-----

### Q: “What interests you about this role specifically?”

> “Ownership. The JD says ‘own and ship end-to-end’ — that’s exactly how I work. At a 25-person company with this growth, an Android engineer doesn’t just write features. They shape the product, influence architecture decisions, and see the direct impact on users.
> 
> Also, your modular architecture philosophy matches mine. I’ve built 20+ module systems at scale. I can contribute from day one to architecture as you prepare for B2B scaling — not ramp up for months learning patterns I already know.”

-----

## 18. RED FLAGS & HOW TO HANDLE THEM

|Concern                        |Response                                                                                                                                                                                                                                                 |
|-------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|**No CS degree**               |“I’m self-taught with 7 years production experience. Track record: 2M users, 99.2% crash-free, AR feature driving 60% conversion. I’ve passed Google-level system design interviews in practice sessions. The degree matters less than what I’ve built.” |
|**From Kazakhstan**            |“I’ve worked with SF team across 11-hour time difference for over a year. Being in-office in Dubai is actually easier. Dubai is my long-term plan — family relocation, not a work visa experiment.”                                                      |
|**English fluency**            |“All technical content consumption in English — docs, conferences, podcasts. Worked with English-speaking teams internationally. Immersion in English-speaking office will accelerate further. This conversation is in English.”                         |
|**No fintech background**      |“IZI handles financial transactions for 2M users. I implemented biometric auth with CryptoObject, secure payment flows with Android Keystore encryption, certificate pinning, and maintained 99.2% crash-free — exactly the reliability fintech demands.”|
|**No GraphQL experience**      |“I’ve studied Apollo Kotlin v4 in depth — normalized cache with SqlNormalizedCache, fetch policies, subscriptions, code generation. My modular networking architecture translates directly. Can demonstrate in pair programming.”                        |
|**Side projects = flight risk**|“Not looking for a short stint. The path from Series A to Nubank-of-the-region is a journey I want to be part of. Personal projects are creative outlets — Ziina gets full professional commitment.”                                                     |
|**Notice period**              |“Can start within a week of accepting an offer.”                                                                                                                                                                                                         |

-----

## 19. QUESTIONS FOR YURA (Ask 2–3 at the end)

These show you’re thinking as someone **already on the team**:

1. **“What does a typical feature development cycle look like — from design handoff to production?”**
   — Shows you think about process, not just code
2. **“What’s the biggest technical challenge the Android team is facing right now?”**
   — Shows you want to solve real problems from day one
3. **“How does the team handle on-call and production incidents?”**
   — Shows you care about reliability (connects to 99.2% crash-free)
4. **“What does code review culture look like here — how deep do reviews go?”**
   — Shows you value engineering quality

**Backup questions if conversation goes long:**

1. “How is the codebase currently structured — module-per-feature or something different?”
2. “What’s the testing strategy — unit, integration, E2E? What’s coverage like?”
3. “How does the team prioritize tech debt vs feature work?”
4. “Are Android and iOS codebases aligned architecturally, or do they diverge?”
5. “How do you handle schema changes with GraphQL — is there a client-server contract process?”
6. “What does the path to senior / lead look like on the engineering team?”

-----

## 20. KEY METRICS CHEAT SHEET

Memorize these. Weave them naturally into conversation:

|Metric             |Context                                       |When to use                    |
|-------------------|----------------------------------------------|-------------------------------|
|**7+ years**       |Android development experience                |Introduction                   |
|**2M+ users**      |IZI Kazakhstan app scale                      |Architecture, scale discussions|
|**20+ modules**    |Multi-module architecture at IZI              |Architecture deep dive         |
|**99.2%**          |Crash-free rate in production                 |Quality, testing, reliability  |
|**40%**            |Cold start improvement (4s → 2.5s)            |Performance discussion         |
|**35%**            |Code reduction after Kotlin migration         |Migration discussion           |
|**2M+ shares**     |AR try-on social media impact at Seamm        |AR/3D, business impact         |
|**60%**            |Sales conversion uplift from AR feature       |Business impact                |
|**11 hours**       |Timezone difference managed at Seamm (SF ↔ KZ)|Remote work capability         |
|**Weekly releases**|Release cadence at IZI                        |CI/CD discussion               |
|**6 months**       |Compose migration timeline                    |Compose discussion             |
|**15-20s**         |Incremental build time after modularization   |Modular arch benefits          |
|**70%**            |NPE crash reduction after Kotlin migration    |Kotlin benefits                |

-----

## 21. PRE-CALL CHECKLIST

- [ ] Re-read this document — focus on technical sections relevant to Ziina’s stack
- [ ] Memorize: 2M users, 20+ modules, 99.2% crash-free, 40% startup improvement, 2M shares, 60% conversion
- [ ] Remember three golden rules: **scalability**, **ask questions**, **take time to think**
- [ ] Ziina app installed and studied on your phone — note 3 things you like, 1 suggestion
- [ ] Quiet room, water, camera and mic tested
- [ ] This document open on screen for quick reference
- [ ] Resume and Ziina JD open on screen
- [ ] Mental rehearsal: Practice saying your modular architecture answer out loud once
- [ ] Prepared 2-3 questions for Yura memorized
- [ ] Smile — you already passed HR, they want you to succeed

-----

## 22. REMAINING INTERVIEW STAGES (Post-EM Screening)

### Stage 3: Pair Programming

- **Format:** Live coding session
- **Prep:** Have Android Studio open, clean demo project ready with Compose + Hilt
- **Focus:** Kotlin idioms, Compose UI, clean architecture, state management
- **Tip:** Talk through your thought process out loud. Narrate decisions.
- **Expected:** Build a small feature — maybe a list with detail screen, API integration, error handling

### Stage 4: System Design + Tech Presentation

- **System Design:** Mobile payment flow or modular architecture for scaling
- **Tech Presentation:** Prepare 7-min talk — “Monolith to Multi-Module at 2M Users”
  - Before: monolith pain points (build times, coupling, team conflicts)
  - Migration strategy (incremental, never stopped shipping)
  - Module structure diagram (feature-first, core modules)
  - Build time improvements (graph: before vs after)
  - Team velocity impact (parallel feature development)
  - Lessons learned (where to draw module boundaries)
  - How this applies to Ziina’s B2B scale

### Stage 5: Culture Interview with Co-founders

- **Faisal (CEO)** — vision alignment, “why Dubai”, long-term commitment
- **Sarah (CPO)** — product thinking, design appreciation, collaboration style
- **Key:** Be authentic, show genuine interest in Middle East fintech
- **Reference:** “Nubank of the region” — you want to be part of that journey

-----

## 23. SALARY & PACKAGE INTEL

|Component          |Details                                                    |
|-------------------|-----------------------------------------------------------|
|**Range**          |$100K–$150K net (0% income tax in Dubai)                   |
|**Equity**         |Stock options (YC startup standard)                        |
|**Vacation**       |6 weeks + UAE statutory holidays                           |
|**Insurance**      |Medical, dental, vision via Allianz (employee + dependents)|
|**Visa**           |Golden Visa nomination (10-year, auto-renewable)           |
|**Work style**     |Dubai-based, flexible hours                                |
|**Relocation**     |Support provided                                           |
|**Educational**    |Courses, books, programs covered                           |
|**Office**         |DIFC (Dubai financial district), ergonomic setup           |
|**Advisory access**|Office hours with execs from Stripe, Revolut, Uber         |

**Negotiation note:** Don’t discuss salary at EM Screening. If Yura asks, deflect: “I discussed range with Anton and we’re aligned. Happy to detail later in the process.”

-----

## FINAL REMINDERS

1. **Be concrete.** Yura codes daily. Real code examples > abstract principles. If you can mention a class name, a pattern, a specific tool — do it.
2. **Connect to scale.** Every answer should touch on how your experience helps Ziina scale. B2B growth = their #1 priority.
3. **Be yourself.** Anton already liked your energy. Don’t be a different person — amplify what worked.
4. **It’s a two-way conversation.** You’re also evaluating fit. Ask genuine questions.
5. **Take pauses.** “That’s a great question, let me think for a second” shows thoughtfulness, not weakness.
6. **Show depth, not breadth.** If he asks about modular architecture, go deep into one specific decision rather than listing 10 surface-level points.
7. **Admit what you don’t know.** GraphQL — be honest, show preparation. It’s more impressive to say “I studied this” than to pretend production experience.
8. **End strong.** Your last impression matters. Close with enthusiasm: “I’m excited about this opportunity — the stage Ziina is at, the challenges ahead, and the team. Looking forward to the next steps.”

-----

*You’ve done the work. 7 years, 2 million users, 99.2% crash-free, AR feature with 60% conversion uplift. You’re not asking for a favor — you’re bringing exactly what they need at exactly the right time. The only thing left is to be yourself and let the experience speak.*