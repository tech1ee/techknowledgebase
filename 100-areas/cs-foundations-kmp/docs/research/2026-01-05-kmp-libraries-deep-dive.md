# Research Report: KMP Libraries Deep Dive 2025

**Date:** 2026-01-05
**Sources Evaluated:** 30+
**Research Depth:** Deep

## Executive Summary

KMP экосистема библиотек в 2025 достигла зрелости. Ktor 3.2+ предлагает 90%+ performance improvements благодаря kotlinx-io, поддержку Wasm, Unix sockets. SQLDelight 2.2+ — standard для multiplatform databases с compile-time SQL verification. kotlinx-serialization лидирует по performance для sealed classes (7x faster serializer creation). Coil 3.0 заменил Kamel как de facto standard для image loading. DataStore 1.2+ теперь official multiplatform, конкурирует с Multiplatform Settings. Kermit рекомендуется над Napier благодаря thread safety и performance focus.

## Key Findings

### 1. Ktor 3.x Evolution (2024-2025)

| Version | Date | Key Features |
|---------|------|--------------|
| 3.0 | Oct 2024 | kotlinx-io, 90%+ performance, Wasm support |
| 3.1 | Feb 2025 | CIO for wasm-js/js, refined IO |
| 3.2 | Jun 2025 | Unix domain sockets, DI module, HTMX |
| 3.3 | Sep 2025 | WebRTC preview, OpenAPI |

**Performance Breakthrough:**
- Switched from custom IO to kotlinx-io (based on Okio)
- 90%+ improvement by reducing byte copying
- Native platform optimizations

**Multiplatform Engines:**

| Engine | Platforms | Best For |
|--------|-----------|----------|
| CIO | All (including Wasm) | General purpose |
| OkHttp | JVM, Android | Android legacy integration |
| Darwin | iOS, macOS | Native iOS performance |
| Curl | Native | CLI tools |
| Js/Fetch | JS/Wasm | Browser |

### 2. SQLDelight 2.x Best Practices

**Migration Strategy:**
```
.sqm files: SQL migrations
.db files: Migration verification
verifyMigrations = true in Gradle
```

**Data Migration with Callbacks:**
```kotlin
Database.Schema.migrate(
    driver,
    oldVersion,
    newVersion,
    AfterVersion(3) { driver ->
        // Custom data migration logic
    }
)
```

**Important Rules:**
- No `BEGIN/END TRANSACTION` in migrations (crashes some drivers)
- Use `.db` files for schema verification
- Temp tables for complex data migrations
- Package changed from `com.squareup` to `app.cash` in 2.0

**Current Version:** 2.2.1 (recommended)

### 3. kotlinx-serialization Performance

**Benchmark Results (2025):**

| Scenario | kotlinx-serialization | Moshi | Jackson |
|----------|----------------------|-------|---------|
| Small JSON | Fastest | Slower | Comparable |
| Large JSON (deserialize) | 2x slower | Fastest | - |
| Large JSON (serialize) | Fastest | Slower | - |
| Sealed classes | 7x faster creation | Slower | - |

**Known Trade-offs:**
- More memory allocation than Moshi for large responses
- Faster runtime than Gson/Moshi reflective mode
- Better Kotlin type system support (nullables, defaults)

**Current Stable:** 1.9.0 (Kotlin 2.2+)
**Upcoming:** 1.10.0 (API stabilization)

### 4. kotlinx-datetime 0.7.x

**Key Changes:**
- Removed `kotlinx.datetime.Instant` → use `kotlin.time.Instant`
- Type aliases for migration
- RFC 9557 grammar for timezone parsing

**Platform Considerations:**

| Platform | Timezone Support |
|----------|-----------------|
| JVM | Full (Java time zones) |
| Android | Full |
| iOS/Darwin | Full (Foundation fallback) |
| Wasm WASI | UTC only (add zoneinfo dependency for full) |
| JS | Browser timezones |

**Best Practice:**
```kotlin
// Store as Instant (UTC)
val instant = Clock.System.now()

// Convert to local only for display
val local = instant.toLocalDateTime(TimeZone.currentSystemDefault())
```

### 5. Image Loading: Coil 3.0 (Winner)

**Why Coil Won:**
- Kotlin Foundation sponsorship
- Familiar Android API
- All platforms: Android, iOS, JVM, JS, Wasm
- Multiple network backends (OkHttp, Ktor)

**Migration from Kamel:**
Kamel was community-driven, Coil 3.0 is now official with JetBrains support.

**Setup:**
```kotlin
implementation("io.coil-kt.coil3:coil-compose:3.3.0")
implementation("io.coil-kt.coil3:coil-network-ktor:3.3.0")
```

### 6. Preferences: DataStore vs Multiplatform Settings

| Feature | DataStore | Multiplatform Settings |
|---------|-----------|----------------------|
| API Style | Flow-based | Simple sync |
| Platforms | Android, iOS, Desktop | All + Wasm, JS |
| Type Safety | Proto (typed), Preferences (key-value) | Key-value |
| Async | Yes (coroutines) | Optional |
| Migration | Built-in | Manual |

**Recommendation:**
- New projects with standard platforms → DataStore 1.2+
- Need Wasm/JS or simple API → Multiplatform Settings
- Proto DataStore for complex structured data

### 7. Logging: Kermit vs Napier

| Aspect | Kermit (Touchlab) | Napier |
|--------|-------------------|--------|
| Thread Safety | Excellent (immutable config) | Improved (atomics) |
| iOS Config | Easy | Complex |
| Performance | Optimized (no atomics on log) | Atomics on each log |
| Crashlytics | Built-in | Available |
| API | Tag optional | Timber-inspired |

**Recommendation:** Kermit for new projects

## Community Sentiment

### Positive
- Ktor 3.x performance praised
- SQLDelight compile-time safety loved
- Coil 3.0 multiplatform migration smooth
- DataStore KMP support welcomed

### Negative / Concerns
- kotlinx-serialization memory usage with large JSON
- kotlinx-datetime still "experimental"
- DataStore no Wasm/JS support
- Ktor learning curve for iOS devs

### Mixed
- SQLDelight vs Room debate continues
- DataStore vs Multiplatform Settings preference varies
- Kermit vs Napier — both viable

## Recommended Stack (2025)

```
Networking:     Ktor 3.2+ (CIO engine)
Database:       SQLDelight 2.2+
Serialization:  kotlinx-serialization 1.9+
DateTime:       kotlinx-datetime 0.7+
Image Loading:  Coil 3.3+
Preferences:    DataStore 1.2+ (or Multiplatform Settings for Wasm/JS)
Logging:        Kermit 2.0+
```

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Ktor 3.0 Release](https://blog.jetbrains.com/kotlin/2024/10/ktor-3-0/) | Official | ★★★★★ | Performance details |
| 2 | [Ktor 3.2 Release](https://blog.jetbrains.com/kotlin/2025/06/ktor-3-2-0-is-now-available/) | Official | ★★★★★ | Latest features |
| 3 | [SQLDelight Migrations](https://sqldelight.github.io/sqldelight/2.0.2/multiplatform_sqlite/migrations/) | Official | ★★★★★ | Migration guide |
| 4 | [Coil 3.0 Release](https://colinwhite.me/post/coil_3_release) | Official | ★★★★★ | Multiplatform support |
| 5 | [DataStore KMP Setup](https://developer.android.com/kotlin/multiplatform/datastore) | Official | ★★★★★ | Official guide |
| 6 | [kotlinx-datetime GitHub](https://github.com/Kotlin/kotlinx-datetime) | Official | ★★★★★ | Timezone handling |
| 7 | [JSON Performance Benchmarks](https://tech.teaddict.net/kotlin/programming/json/2025/02/15/kotlin-json-performance/) | Blog | ★★★★☆ | Comparison data |
| 8 | [Kermit 1.0](https://touchlab.co/kermit-kmp-logging-1-0) | Official | ★★★★☆ | Logging design |
| 9 | [Networking 2025](https://medium.com/@hiren6997/the-state-of-android-networking-in-2025-retrofit-ktor-and-beyond-7a5a5317802c) | Blog | ★★★★☆ | State of ecosystem |
| 10 | [Moshi vs kotlinx Benchmark](https://medium.com/@kacper.wojciechowski/moshi-vs-kotlinx-serialization-the-ultimate-benchmark-a7ed776a46c0) | Blog | ★★★★☆ | Performance data |

## Research Methodology

- **Queries used:** 7 search queries
- **Sources found:** 40+ total
- **Sources used:** 30 (after quality filter)
- **Focus areas:** Ktor, SQLDelight, kotlinx libs, image loading, preferences, logging

---

*Проверено: 2026-01-09*
