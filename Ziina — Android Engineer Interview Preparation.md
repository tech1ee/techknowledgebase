

> **Candidate:** Arman Aralbayev | Senior Android Engineer, 7+ years
> **Company:** Ziina (Dubai, UAE) | YC W21 | Series A ($22M)
> **Prepared:** February 2026

-----

## Company Quick Reference

|Detail        |Info                                                                                            |
|--------------|------------------------------------------------------------------------------------------------|
|**Founded**   |January 2020 by Faisal Toukan (CEO), Sarah Toukan (CPO), Talal Toukan                           |
|**HQ**        |Dubai DIFC, UAE                                                                                 |
|**Funding**   |$30.85M total — Series A $22M (Sept 2024), Seed $7.5M, Pre-seed $850K                           |
|**Investors** |Altos Ventures, Avenir Growth Capital, Class 5 Global + angels from Revolut, Stripe, Venmo, Brex|
|**Users**     |260,000+ businesses and consumers                                                               |
|**Growth**    |10x YoY payment volume, 34% MoM customer growth, $300M annualized volume                        |
|**License**   |Central Bank of UAE — Stored Value Facility (first VC-backed startup to get it)                 |
|**Team**      |~25 employees                                                                                   |
|**App Rating**|4.7 stars                                                                                       |
|**Awards**    |Red Dot Design Award + 8 international design awards                                            |
|**Mission**   |“Bring financial freedom to every person in the Middle East”                                    |

### Key People

- **Faisal Toukan** — CEO & Co-founder
- **Sarah Toukan** — CPO & Co-founder
- **Talal Toukan** — Head of Engineering (ex-Uber San Francisco, Columbia University)
- **Caner Tatar** — Mobile Engineer (ex-Depop London) — likely your closest teammate

### Recent Launches (Mention These!)

- **Ziina Violet** (Jan 6, 2026) — Lifestyle membership, 100 AED/month, 12 UAE brand partners, 850+ AED monthly value
- **Open Finance** (Jan 15, 2026) — First live Open Finance payment in UAE, partnership with Lean Technologies
- **Ziina Card** (Oct 2025) — Digital Visa card, Apple Wallet + Google Pay, 0% currency fees
- **Tap to Pay on Android** (Apr 2025) — Contactless payments without hardware via NFC

### Tech Stack

- **Backend:** TypeScript + Node.js, GraphQL Federation (Apollo), Kafka, Postgres, Redis, Elasticsearch
- **Mobile:** Kotlin (Android), Swift (iOS), React (Web)
- **Infra:** Google Cloud Platform, Docker, Kubernetes, Cloudflare
- **Architecture:** Modular, event-driven microservices, weekly releases with automation

### Expansion Plans

- Saudi Arabia (planned)
- Jordan (planned — “homecoming” for Toukan family)

-----

## Your 30-Second Elevator Pitch

> “I’m a Senior Android Engineer with 7+ years of experience. Currently at IZI Kazakhstan — a digital operator serving 2 million users — where I built and maintain a 20+ module Kotlin architecture with a 99.2% crash-free rate. Before that, I built AR try-on features for a San Francisco startup that generated 2 million social shares and a 60% sales conversion uplift. I’m excited about Ziina because you’re at the intersection of fintech scale and design excellence, and I want to help take the Android experience to the next level as you expand across the region.”

### Three Messages to Repeat Throughout

1. **Scale + Quality:** “2M users, 99.2% crash-free — I know how to build reliable systems at scale”
2. **Ownership:** “I’ve owned features end-to-end in small teams, from architecture to production”
3. **Fintech Fit:** “IZI has similar challenges — payments, security, compliance, user trust”

-----

## Technical Android Questions (6)

### Q1: “How do you approach modular architecture in Android?”

**Context:** Ziina emphasizes modular architecture. This is your strongest alignment point.

**Answer:**

At IZI Kazakhstan, I led the migration from a monolithic codebase to a multi-module architecture with 20+ modules. The structure follows a layered approach:

- **`:app`** — the shell, wiring everything together
- **`:core:network`**, **`:core:ui`**, **`:core:domain`** — shared foundations
- **Feature modules** like `:feature:auth`, `:feature:payments`, `:feature:profile` — fully isolated

Key architectural decisions:

- Feature modules never depend on each other — they communicate through navigation and shared domain interfaces
- Convention plugins unify build configuration across all modules
- Strict dependency rules enforced via Gradle’s `api` vs `implementation` boundaries

**Results:** Build time dropped ~40% due to parallel compilation. Team could work on features independently. Crash-free rate improved to 99.2% thanks to module isolation — a bug in one feature can’t cascade into another.

**Bridge to Ziina:** “I see Ziina emphasizes modular architecture — at IZI we went through the same evolution with a 2M-user app, and I can bring those lessons directly to help scale your codebase.”

-----

### Q2: “Describe your experience with Jetpack Compose and state management.”

**Answer:**

I use Compose as my primary UI framework in production. My state management approach follows Unidirectional Data Flow:

- **ViewModel** exposes `StateFlow<ScreenState>` — a single sealed class representing the entire screen state
- **Compose** collects it via `collectAsStateWithLifecycle()`
- **Events** flow up through lambda callbacks or a sealed `Event` class
- **Side effects** (navigation, toasts) go through `SharedFlow<Effect>` collected in `LaunchedEffect`

For Compose-specific optimization:

- Mark data classes with `@Immutable` or `@Stable` to prevent unnecessary recompositions
- Use `remember` and `derivedStateOf` for computed values
- Structure composables so that state changes only recompose the minimum subtree

**Concrete example:** At IZI, I migrated the payment screen from View-based XML to Compose. Code volume shrank by ~35%, and an entire category of state-related UI bugs disappeared because the declarative model eliminates manual view updates.

-----

### Q3: “How do you ensure code quality with weekly releases?”

**Context:** Ziina ships weekly. This question is almost guaranteed.

**Answer:**

At IZI we also ship weekly, and here’s the system that keeps us at 99.2% crash-free:

1. **CI Pipeline:** Every PR triggers linting (ktlint + detekt), unit tests, and critical UI tests. Merge is blocked on failures.
2. **Code Review:** Mandatory review with a structured checklist — architecture compliance, test coverage, edge case handling.
3. **Feature Flags:** New features ship behind flags. We can deploy to production without exposing unfinished work, and roll back without a new release.
4. **Staged Rollout:** 1% → 5% → 25% → 100%, monitoring crash-free rate between each step. If it drops below 99%, we halt the rollout.
5. **Monitoring:** Firebase Crashlytics with custom alerts, plus business-level analytics to catch silent failures (payment flows completing but data inconsistent).

The key insight is that weekly releases are actually *safer* than monthly ones — smaller changesets are easier to review, easier to roll back, and easier to debug when something goes wrong.

-----

### Q4: “How do you handle concurrency and threading?”

**Context:** The JD specifically mentions “difficult bugs, concurrency, persistence.”

**Answer:**

Kotlin Coroutines are the foundation:

- **Scoping:** `viewModelScope` for UI-bound work, `lifecycleScope` for lifecycle-aware operations, custom `CoroutineScope` for long-running background tasks
- **Dispatchers:** `IO` for network/database, `Default` for CPU-bound computation, `Main` for UI updates
- **Reactive streams:** `StateFlow` for state, `SharedFlow` for one-time events, `Flow` for data streams from repositories

For structured concurrency:

- `supervisorScope` when parallel operations should be independent — a failure in one shouldn’t cancel siblings
- `async/await` for parallel data loading
- Proper `CancellationException` handling — never swallowing it

**Concrete example:** On IZI’s main screen, I load profile data, account balance, and tariff information in parallel using `async` inside a `supervisorScope`. If the tariff API fails, the user still sees their profile and balance — graceful degradation instead of a full-screen error. Total load time dropped from ~1.8s (sequential) to ~0.7s (parallel).

For persistence: Room with `Flow` for reactive queries, ensuring all write operations run on `Dispatchers.IO` with proper transaction boundaries.

-----

### Q5: “Tell me about a difficult bug you’ve debugged.”

**Answer (STAR):**

**Situation:** At IZI, we had a rare crash during biometric authentication — only on Samsung devices running Android 12, affecting about 0.3% of sessions. But it hit the most critical flow: app login.

**Task:** Find the root cause and fix it without breaking biometrics on other devices.

**Action:** I analyzed the Crashlytics stacktrace — the crash was in the `BiometricPrompt` callback. After reproducing on a Samsung S21 with Android 12, I discovered a race condition: `onAuthenticationSucceeded` was being called *after* the Fragment’s `onDestroy` on certain Samsung devices due to their custom lifecycle handling. The callback tried to update UI on a destroyed fragment.

The fix was threefold:

1. Check `isAdded` and `lifecycle.currentState` before processing any biometric callback
2. Register a `Lifecycle.Event.ON_DESTROY` observer to clean up the BiometricPrompt
3. Add defensive logging to catch similar edge cases early

**Result:** The crash was completely eliminated. Crash-free rate went from 98.9% to 99.2%. I documented the pattern as a team-wide best practice for all biometric and lifecycle-sensitive operations.

-----

### Q6: “How do you approach performance optimization?”

**Answer:**

I think about performance across five dimensions:

1. **App Startup:** Lazy initialization of SDKs (don’t init what you don’t need yet), baseline profiles for AOT compilation of critical paths. At IZI, I reduced cold start time by 40%.
2. **UI Performance:** In Compose — avoid unstable parameters, use `LazyColumn` with proper `key` and `contentType`, profile with Layout Inspector and Compose compiler metrics reports. The goal is zero unnecessary recompositions on the critical path.
3. **Memory:** LeakCanary in debug builds, strict lifecycle management. Common leak sources: static references to Context, unregistered listeners, coroutines outliving their scope.
4. **Network:** OkHttp cache interceptors, pagination for all lists, prefetch strategies for predictable user flows (if user opens payments list, prefetch the first payment detail).
5. **APK Size:** R8 with aggressive shrinking, WebP for images, vector drawables where possible. For a fintech app like Ziina, smaller APK means faster installs — especially important for the UAE market where you’re competing for first-time users.

-----

## Fintech & Payments Questions (4)

### Q7: “How do you handle security in a fintech app?”

**Answer:**

Security in fintech is non-negotiable. Here’s my layered approach:

**Network Layer:**

- Certificate pinning to prevent MITM attacks
- TLS 1.3, network security config blocking cleartext traffic
- Request signing for critical API calls

**Local Storage:**

- `EncryptedSharedPreferences` for tokens and sensitive data
- Never store card numbers, PINs, or passwords in plain text — ever
- Room database encryption for offline transaction history

**Authentication:**

- Biometric + PIN/password fallback
- Session management with short-lived access tokens + refresh tokens
- Re-authentication for high-value operations (large transfers, settings changes)

**App Integrity:**

- Play Integrity API (replaced SafetyNet) for root/tamper detection
- R8 obfuscation for release builds
- `FLAG_SECURE` on screens showing sensitive data (balances, card numbers)
- Clipboard auto-clear after copying sensitive data

**PCI-DSS Compliance:**

- Tokenization — never handle raw card data in the app
- Never log PAN, CVV, or full card numbers
- Minimize data retention

-----

### Q8: “How would you implement Tap to Pay on Android?”

**Context:** Ziina launched this in April 2025. Shows you understand their product.

**Answer:**

Tap to Pay on Android uses Host Card Emulation (HCE):

1. **`HostApduService`** — the app emulates an NFC payment terminal, processing APDU commands from the customer’s card/phone
2. **AID Registration** — declare the Application ID in the manifest so Android routes NFC taps to your app
3. **Payment Flow:** Detect NFC tap → Authenticate merchant (biometric/PIN) → Read card data via APDU → Tokenize via Visa/Mastercard → Process payment through backend → Display confirmation
4. **Tokenization:** Each transaction generates a unique cryptogram — no raw card data touches the device
5. **Challenges:** NFC stack differences between manufacturers (Samsung, Xiaomi, Huawei all behave slightly differently), battery optimization killing the HCE service in the background, handling edge cases like NFC tag lost mid-transaction

This is particularly interesting for Ziina’s SME customers — they can accept card payments with just their phone, no hardware needed. That’s a huge unlock for the 208,000 micro-businesses in the UAE.

-----

### Q9: “How would you architect a subscription feature like Violet?”

**Context:** Violet launched January 6, 2026. Demonstrates you follow their product closely.

**Answer:**

I’d structure it as a dedicated `:feature:violet` module:

**Domain Layer:**

- `SubscriptionState` sealed class: `Active(tier, expiresAt, benefits)`, `Expired`, `Trial`, `None`
- `SubscriptionRepository` exposing `Flow<SubscriptionState>` — reactive, always current
- `BenefitRedemptionUseCase` for tracking partner benefit usage

**Data Layer:**

- Backend API for subscription management (for a fintech, you’d likely handle billing internally rather than through Google Play)
- Local caching of subscription state and available benefits for offline access
- Sync strategy: pull on app launch + push via WebSocket for real-time status changes

**UI Layer (Compose):**

- Violet membership card component — visually distinct from regular Ziina card
- Benefits grid with partner logos, redemption status, deep links to partner apps
- Subscription management screen (upgrade, downgrade, cancel)

**Partner Integration:**

- Each of the 12 partners gets a domain model with: eligibility rules, redemption flow, usage tracking
- Deep links or SDK integration per partner (e.g., ClassPass, Deliveroo APIs)
- Analytics: activation rate, usage per partner, which benefits drive retention vs. churn

**Key Consideration:** With 100 AED/month pricing and 850+ AED value, the unit economics depend on partner benefit utilization rates. The app should surface underused benefits to increase perceived value.

-----

### Q10: “Experience with payment SDK integrations?”

**Answer:**

At IZI Kazakhstan, I worked with payment processing flows that share the same fundamentals as Ziina’s:

- **Transaction lifecycle:** Tokenization → Authorization → Capture → Settlement — I understand each stage and the error handling needed at every step
- **Webhook-driven architecture:** Payment status updates arrive asynchronously. The app needs to handle optimistic UI (show “pending” immediately), then reconcile with the actual status from webhooks
- **Idempotency:** Every payment operation needs a unique idempotency key to prevent duplicate charges — critical for user trust
- **Error handling:** Retry with exponential backoff for transient failures, clear user-facing error messages for terminal failures, graceful degradation when payment providers are unavailable

I also built biometric authentication for high-security payment operations — the same pattern Ziina would need for confirming transfers.

-----

## System Design Questions (3)

### Q11: “Design a P2P payment system for mobile.”

**Context:** This is literally Ziina’s core product. Nail this.

**Answer:**

**High-Level Architecture:**

```
User A (Sender)
  → Android App
    → GraphQL API (Apollo Federation)
      → Payment Service
        → Debit sender wallet
        → Credit receiver wallet
        → Notification Service → Push to User B
      → Fraud Detection (async)
      → Audit Log (async via Kafka)
```

**Mobile Architecture:**

```
PaymentScreen (Compose)
  → PaymentViewModel
    → SendPaymentUseCase
      → PaymentRepository
        → PaymentRemoteDataSource (GraphQL client)
        → PaymentLocalDataSource (Room - transaction cache)
```

**Key Design Decisions:**

1. **Contact Resolution:** Phone number → Ziina user lookup. Cache the mapping locally, invalidate periodically. Handle the case where receiver doesn’t have Ziina (prompt to invite).
2. **Optimistic UI:** Show “Payment Sent — Pending” immediately after API confirms the debit. Update to “Completed” when the credit settles (via WebSocket or SSE). This makes the app feel instant.
3. **Idempotency:** Generate a `transactionId` client-side (UUID). Server deduplicates. If the network drops mid-request, retrying with the same ID is safe.
4. **Security Per Transaction:** Biometric or PIN confirmation before every send. Amount limits (per-transaction, daily). Device fingerprint + geo + velocity checks sent to fraud detection.
5. **Offline Resilience:** Queue payment intents locally if network is unavailable. Sync when connectivity returns. Show clear “Pending — will send when online” state.

-----

### Q12: “How would you handle offline-first in a payments app?”

**Answer:**

For a payments app, “offline-first” is nuanced — you can’t complete a payment offline, but you can make the app *usable* offline:

**Read Operations (fully offline):**

- Room DB as single source of truth for transaction history, contacts, account info
- Network-bound resource pattern: Show cache → Fetch fresh data → Update cache → Update UI
- Users can browse their history, check balances (last known), view contacts

**Write Operations (queue and sync):**

- Payment intents saved to a local queue with status `QUEUED`
- `ConnectivityManager` callback triggers sync when network returns
- UI shows clear “Pending — will send when online” indicator
- Important: Server is always source of truth for balance. Client shows optimistic balance (last known minus queued payments) but reconciles on sync

**Conflict Resolution:**

- If balance changed server-side while offline (someone sent you money), the sync resolves it
- If queued payment fails (insufficient funds after server check), notify user clearly
- Never silently drop a queued operation

-----

### Q13: “How do you handle navigation in a multi-module project?”

**Context:** Anton Dudakov (former Ziina engineer) wrote about `DeeplinkGenerator` — navigation is clearly important to them.

**Answer:**

My approach at IZI:

1. **Shared Navigation Module** (`:core:navigation`): Contains all route definitions as sealed classes or string constants. Every feature module depends on this, but it depends on nothing.
2. **NavGraph Per Feature:** Each feature module defines its own `NavGraph` composable. The app module wires them together in the root NavHost.
3. **Deep Links:** Centralized deeplink registry in `:core:navigation`. Each feature module registers its supported deep link patterns. A `DeeplinkRouter` in the app module resolves incoming URIs to the correct destination.
4. **Inter-Module Communication:** Through navigation arguments (type-safe with Kotlin Serialization) or shared domain events via a `SharedFlow` in a common module. Feature modules never import each other.
5. **Type Safety:** Using the Compose Navigation type-safe API with `@Serializable` route classes — eliminates string-based route errors at compile time.

This approach means a new feature module can be added without touching existing modules — just register routes and deep links.

-----

## Behavioral Questions (5)

### Q14: “Tell me about a time you owned a feature independently.”

**STAR:**

**Situation:** At Seamm, a San Francisco jewelry startup, I was the sole Android developer. The company needed an AR try-on feature — their core differentiator — built from scratch.

**Task:** Full ownership: research AR SDKs, architect the solution, integrate with existing app, ship to production. No Android team to consult — just me, a designer, and a product manager.

**Action:** I evaluated Snapchat Camera Kit and Google Filament for 3D rendering, built a proof of concept in 2 weeks, then iterated on rendering quality over 6 weeks. I made all technical decisions independently — chose the rendering pipeline, designed the caching strategy for 3D models, and optimized frame rates across mid-range devices. Daily async standups with the SF team (11-hour time difference) kept everyone aligned.

**Result:** The AR try-on feature generated 2M+ social media shares, drove a 60% uplift in sales conversion, and maintained 99.2% crash-free rate. It became the product’s main competitive advantage.

**Bridge to Ziina:** “This is exactly the kind of ownership the job description mentions — building features from the ground up in a small team where your judgment matters.”

-----

### Q15: “Describe a situation where you moved quickly and made tradeoffs.”

**STAR:**

**Situation:** At IZI, marketing had a promotional campaign launching in 3 days. They needed a custom screen with animations and campaign-specific logic — but no one had told engineering until the last minute.

**Task:** Ship a fully functional promotional feature in 3 days without breaking existing functionality.

**Action:** I made a pragmatic tradeoff: built the feature inside an existing module (not ideal separation) but with clean API boundaries so it could be extracted later. I wrote unit tests for the business logic but skipped UI tests. Created a detailed tech debt ticket with the refactoring plan. Communicated the tradeoff clearly to the team lead.

**Result:** Shipped on time. The campaign drove +15% new activations. Two weeks later, I executed the refactoring plan — extracted into its own module in a single PR. Zero production issues throughout.

**Key Point:** “I believe in making deliberate tradeoffs, not accidental ones. When I cut a corner, I document it, create a ticket, and come back to fix it.”

-----

### Q16: “How do you handle working in a small team?”

**Answer:**

I thrive in small teams — both my best career results came from them.

At Seamm, I was the only Android developer working with a 5-person SF team, 11 hours of timezone difference. What I learned:

1. **Overcommunicate asynchronously.** Write decisions down. Record short Loom videos for complex topics. Don’t wait for meetings.
2. **Don’t wait for permission.** In a small team, if you see a problem, propose a solution and start implementing. Blocking on approval kills velocity.
3. **Wear multiple hats.** I did architecture, implementation, code review (self-review + iOS peer review), QA, and release management. That’s what small teams require.
4. **Direct impact.** Every line of code reaches users. Every decision matters. That’s more motivating than being a cog in a 200-person engineering org.

At IZI, same pattern — I took ownership of the entire modular architecture migration without being asked. Saw the problem, proposed the solution, executed it.

-----

### Q17: “Tell me about a time you shaped engineering practices.”

**Context:** The JD literally says “shape engineering culture by introducing good practices and methods of knowledge-sharing.” This is a key evaluation criterion.

**STAR:**

**Situation:** When I joined QazCode (IZI), there were no unified coding standards. Code review was a rubber stamp — people approved PRs without meaningful feedback.

**Task:** Raise the quality bar across the Android team without creating bureaucratic overhead that would slow us down.

**Action:**

- Introduced `detekt` and `ktlint` as blocking CI checks — code that doesn’t meet standards can’t merge
- Created a PR review checklist: architecture compliance, test coverage, edge case handling, accessibility
- Started writing Architecture Decision Records (ADRs) for significant technical choices — creating institutional memory
- Organized bi-weekly tech talks where team members present interesting problems they solved

**Result:** Bug rate decreased measurably. Onboarding new developers went from weeks to days because conventions were documented. The team became more autonomous — people started catching their own issues before review. The ADR practice was adopted by the iOS team as well.

**Bridge to Ziina:** “The JD mentions shaping engineering culture — I’ve done exactly this at IZI, and I’d love to bring that same energy to Ziina.”

-----

### Q18: “Why Ziina? Why leave your current role?”

**Answer:**

Three reasons, honestly:

**The mission resonates.** Ziina is building financial infrastructure for a region that needs it. Coming from IZI Kazakhstan — a similar market where financial accessibility is a real challenge — I understand the problem viscerally. It’s not abstract to me.

**The stage is perfect.** 260K users growing 10x year over year, Series A in the bank, expanding to Saudi Arabia and Jordan. This is the inflection point where engineering decisions really matter — the architecture you build now will serve millions. I want to be part of shaping that.

**The craft matters here.** Eight design awards, Red Dot winner, 4.7-star rating — Ziina clearly cares about quality. That aligns with how I work. I don’t ship features, I ship *experiences* — and the crash-free rate to prove it. Plus, recent launches like Violet and Open Finance show the technical ambition matches the design ambition.

And practically — Dubai is where I want to build my career long-term. The tech ecosystem is growing, the tax environment is favorable, and being in the same timezone as the team means maximum collaboration.

**What NOT to say:** Don’t mention salary, boredom, or dissatisfaction with current role.

-----

## Questions You Ask the Interviewer (10)

1. “Violet launched just last month — what were the biggest Android-specific challenges in shipping it?”
2. “How is the Android codebase structured today? Single module, multi-module, or somewhere in between?”
3. “What does a typical feature development cycle look like — from design handoff to production?”
4. “What’s on the Android team’s roadmap for the next 6 months?”
5. “How do you balance moving fast and maintaining code quality with weekly releases?”
6. “With Saudi Arabia expansion planned — how are you thinking about localization and regional differences in the mobile apps?”
7. “What’s the testing strategy? Unit tests, UI tests, manual QA — what does the pyramid look like?”
8. “How does the Android team interact with the backend team, given the GraphQL Federation setup?”
9. “What would success look like for me in the first 90 days?”
10. “What’s the most exciting technical challenge the Android team will face this year?”

### Bonus Questions (if conversation allows)

1. “I noticed Anton Dudakov recently left — what’s the current Android team size?”
2. “How does the Open Finance integration affect the mobile architecture? Any new SDK integrations planned?”
3. “The ZiiBoard keyboard is a patented feature — are there plans to expand it further?”

-----

## Salary Negotiation Strategy

### Market Data

|Factor                            |Detail                                                          |
|----------------------------------|----------------------------------------------------------------|
|**Dubai Senior Android (fintech)**|$6,000–$12,000/month base                                       |
|**Ziina positioning**             |“Above-market compensation” + equity                            |
|**Tax**                           |0% income tax in UAE                                            |
|**Ziina stage**                   |Series A — has money, but startup-level base + meaningful equity|

### Negotiation Playbook

1. **Don’t name a number first.** Say: “What’s the compensation range you have in mind for this role?”
2. **If pressed for a number:** “Based on my experience level and the Dubai fintech market, I’d expect something in the $7,000–$10,000/month range, but I’m flexible depending on the total package — equity, relocation support, and benefits all factor in.”
3. **Your leverage:**
- You’re currently employed — no desperation
- AR/3D experience is rare — hard to find in other candidates
- 7+ years with 2M-user scale — proven, not theoretical
- Willing to relocate — shows commitment
1. **Equity questions to ask:**
- “What’s the vesting schedule?”
- “What was the most recent 409A valuation?”
- “What percentage of the company does this grant represent?”
- “Is there any acceleration on change of control?”
1. **Relocation questions:**
- Visa sponsorship — who handles it, timeline?
- Relocation package — flights, shipping, temporary housing?
- First month accommodation support?

### Benefits to Factor In

- 6-week vacation policy + UAE statutory holidays
- Medical/dental/vision insurance (Allianz) for you + dependents
- 0% income tax = gross equals net
- DIFC office location (premium business district)
- Flexible work hours

-----

## Expected Interview Process

Based on YC startups of this size:

|Stage                               |Duration |Likely Interviewer       |Focus                                       |
|------------------------------------|---------|-------------------------|--------------------------------------------|
|**1. Intro/Culture Call**           |30–45 min|Talal Toukan or recruiter|Motivation, experience overview, culture fit|
|**2. Technical Interview**          |60–90 min|Caner Tatar or Talal     |Kotlin, Compose, architecture, live coding  |
|**3. System Design**                |45–60 min|Talal Toukan             |Mobile architecture, modularization, scaling|
|**4. Take-Home or Pair Programming**|2–4 hours|—                        |Practical coding exercise                   |
|**5. Founders Call**                |30 min   |Faisal or Sarah Toukan   |Culture fit, vision alignment               |

**Timeline:** YC startups typically move fast — expect 1–2 weeks from first call to offer.

**Prep tip:** Have your laptop ready with Android Studio open for any live coding. Have a clean demo project ready to show architecture patterns if asked.

-----

## Pre-Interview Checklist

- [ ] Download Ziina app, explore every feature, take notes on UX
- [ ] Review your IZI architecture diagram — be ready to whiteboard it
- [ ] Prepare 3 questions specific to each interviewer (research their LinkedIn)
- [ ] Test your camera, mic, and internet connection
- [ ] Have water and notes nearby
- [ ] Review this document 30 minutes before the call
- [ ] Prepare a quiet, professional-looking background
- [ ] Have your resume and Ziina JD open on screen for reference

-----

## Quick Reference: Your Key Metrics

Use these numbers throughout the interview — repetition builds memory:

|Metric         |Context                                               |
|---------------|------------------------------------------------------|
|**7+ years**   |Android development experience                        |
|**2M+ users**  |IZI Kazakhstan app scale                              |
|**20+ modules**|Multi-module architecture at IZI                      |
|**99.2%**      |Crash-free rate in production                         |
|**40%**        |Startup time improvement                              |
|**2M+ shares** |AR try-on social media impact at Seamm                |
|**60%**        |Sales conversion uplift from AR feature               |
|**35%**        |Code reduction after Compose migration                |
|**11 hours**   |Timezone difference managed at Seamm (SF ↔ Kazakhstan)|

-----

*Good luck, Arman. You’ve got the skills, the experience, and the preparation. Now go show them.* 🚀