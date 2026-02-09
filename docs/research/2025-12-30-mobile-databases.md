# Research Report: Mobile Databases

**Date:** 2025-12-30
**Sources Evaluated:** 20+
**Research Depth:** Deep (comprehensive multi-source analysis)

## Executive Summary

Mobile databases — локальные хранилища для iOS, Android и cross-platform приложений. SQLite — основа большинства решений (встроен в iOS/Android с 2007). Ключевые решения 2024-2025: **Room** (Android Jetpack, KMP support с 2.7.0), **SQLDelight** (Kotlin Multiplatform), **Core Data/SwiftData** (iOS), **GRDB** (Swift). Realm deprecated MongoDB в сентябре 2024 — sync отключается в сентябре 2025. Альтернативы для sync: PowerSync, ObjectBox, Couchbase Mobile. Тренды: KMP-first подход, offline-first архитектура, SQLite WAL mode для производительности.

---

## Key Findings

### 1. SQLite Internals [HIGH CONFIDENCE]

**Архитектура:**
```
┌────────────────────────────┐
│      SQL Interface         │ ← SQL parsing, optimization
├────────────────────────────┤
│     Virtual Machine        │ ← Bytecode execution
├────────────────────────────┤
│       B-Tree Module        │ ← Data organization
├────────────────────────────┤
│         Pager              │ ← Page cache, transactions
├────────────────────────────┤
│        OS Layer            │ ← File I/O, locking
└────────────────────────────┘
```

**Ключевые концепции:**
- B+Tree для хранения таблиц и индексов
- Page size: 4096 bytes (default), configurable 512-65536
- MVCC через copy-on-write
- WAL mode: 4x faster writes, concurrent readers

**WAL vs Rollback Journal:**
| Характеристика | WAL Mode | Rollback Journal |
|----------------|----------|------------------|
| Write speed | 4x faster | Baseline |
| Concurrent reads | Yes | Limited |
| File count | 3 files | 2 files |
| Network FS | No | Yes |
| Recommended | Mobile apps | Special cases |

### 2. Android Room [HIGH CONFIDENCE]

**Характеристики:**
- Jetpack library, abstraction over SQLite
- Compile-time SQL verification
- KMP support с версии 2.7.0-alpha01 (May 2024)
- Flow + Coroutines integration

**Best Practices:**
- Use KSP instead of KAPT (faster builds)
- Flow over LiveData для reactive queries
- In-memory database для тестов
- Never `allowMainThreadQueries()`
- Schema export для миграций

**Migration Testing:**
- `room-testing` artifact
- `MigrationTestHelper` class
- Export schema to JSON
- Test in androidTest (instrumented)

**Statistics:**
- 23% onboarding crashes from bad database implementation
- 40% developers don't test migrations

### 3. SQLDelight [HIGH CONFIDENCE]

**Подход:**
- SQL-first: пишешь .sq файлы, генерируется Kotlin
- Kotlin Multiplatform native
- Type-safe generated code

**SQLDelight vs Room:**
| Критерий | SQLDelight | Room |
|----------|------------|------|
| Approach | SQL-first | Annotation-first |
| KMP | Native | Since 2.7.0 |
| Learning curve | SQL knowledge needed | Android-friendly |
| Code generation | From SQL files | From annotations |

**Рекомендация:** Room для Android-only и Android-first teams, SQLDelight для KMP-first или SQL-heavy teams.

### 4. iOS Databases [HIGH CONFIDENCE]

**Core Data:**
- Object graph management framework
- Built on SQLite (usually)
- 15+ years of optimization
- Use background context for heavy operations
- CloudKit integration

**SwiftData (iOS 17+):**
- Swift-native, declarative
- @Model macro
- @Query for SwiftUI
- Simpler than Core Data
- Issues in iOS 17, improvements in iOS 18
- Requires iOS 17+ minimum

**GRDB.swift:**
- Direct SQLite access
- Better performance than Core Data/SwiftData
- More control, less abstraction
- v7.9.0 (December 2025)

**Выбор:**
- New iOS 17+ app: SwiftData
- Complex/legacy app: Core Data
- Performance-critical: GRDB

### 5. Realm Status (2024-2025) [CRITICAL UPDATE]

**Deprecation:**
- September 2024: MongoDB deprecated Atlas Device Sync
- September 2025: Sync service shuts down
- Open source but effectively abandoned

**Альтернативы для Sync:**
1. **PowerSync** — PostgreSQL/MongoDB to SQLite sync
2. **ObjectBox** — Built-in sync, drop-in replacement
3. **Couchbase Mobile** — Enterprise-grade
4. **Ditto** — Peer-to-peer sync

**Для apps без sync:** Realm open source works, but consider migration to Room/SQLDelight.

### 6. ObjectBox [HIGH CONFIDENCE]

**Характеристики:**
- NoSQL object database
- Written in C++ (no JVM overhead)
- Fastest CRUD in benchmarks
- 1-1.5MB footprint
- Auto schema migration
- ObjectBox 4.0 (May 2024): Vector DB support

**Benchmarks (ObjectBox vs Room vs Realm):**
- ObjectBox consistently fastest across CRUD
- 10x faster than SQLite for some operations

**Limitation:** No KMP support yet.

### 7. Flutter Databases [HIGH CONFIDENCE]

**Сравнение:**

| Database | Type | Status | Best For |
|----------|------|--------|----------|
| sqflite | SQLite wrapper | Stable | Basic SQL needs |
| Drift | SQLite ORM | Recommended | Most projects |
| Isar | NoSQL | Abandoned* | Legacy only |
| Hive | NoSQL | Deprecated | Legacy only |
| ObjectBox | NoSQL | Active | Performance |

*Isar abandoned by author, community fork exists but risky.

**Рекомендация 2024-2025:** Drift (formerly Moor) — best documented, actively maintained, SQL-based.

### 8. WatermelonDB (React Native) [HIGH CONFIDENCE]

**Характеристики:**
- Lazy loading by design
- App launch: instant (vs 2-5s with Redux persistence)
- SQLite under the hood
- Reactive (auto re-render on changes)
- ~2MB to app size
- v0.15: 5x faster sync on web, 23x on iOS

**Use cases:** Apps with 10K+ records, offline-first.

### 9. Mobile Database Encryption [HIGH CONFIDENCE]

**SQLCipher:**
- 256-bit AES encryption
- Drop-in SQLite replacement
- Works with Room, GRDB
- Current version: 4.9.0

**Implementation:**
1. Add SQLCipher dependency
2. Use `SupportSQLiteOpenHelper.Factory`
3. Store key in Android Keystore / iOS Keychain
4. Never hardcode passphrase

**SafeRoom:** Deprecated, use SQLCipher directly.

### 10. Sync Strategies [HIGH CONFIDENCE]

**Conflict Resolution:**
1. **Last-write-wins** — Simple but lossy
2. **Server wins** — Safe, may lose client data
3. **Client wins** — May overwrite server
4. **Version-based** — Optimistic concurrency
5. **Field-level merge** — Non-overlapping changes
6. **CRDTs** — Complex but correct

**Offline-First Architecture:**
- Local DB = Single Source of Truth
- Queue writes, sync when online
- Delta-sync for efficiency
- Handle conflicts explicitly

**PowerSync:**
- PostgreSQL/MongoDB → SQLite sync
- Self-hosted or cloud
- SDKs: Flutter, React Native, Web
- Open source (May 2024)

### 11. Testing Mobile Databases [HIGH CONFIDENCE]

**Room Testing:**
- Use in-memory database
- Instrumented tests (androidTest)
- MigrationTestHelper for migrations
- Google Truth for assertions

**Best Practices:**
- Isolate tests with in-memory DB
- Test DAO queries
- Test migrations on real device/emulator
- Export schema versions

### 12. Performance Optimization [HIGH CONFIDENCE]

**SQLite/Room:**
- Enable WAL mode: 4x write boost
- Use transactions for batch operations
- Index frequently queried columns
- Avoid over-indexing (5x slower inserts)
- `PRAGMA optimize` before closing
- Keep DB under 100-200MB for best performance

**General:**
- Background threads for DB operations
- Lazy loading
- Pagination for large datasets
- Monitor with profilers

---

## Community Sentiment

### Room
**Positive:**
- "Google's Jetpack library, well-supported"
- "KMP support is game-changer"
- "Good documentation and community"

**Negative:**
- "Migration handling can be complex"
- "KAPT is slow (use KSP)"

### Realm (Pre-deprecation)
**Positive:**
- "Fast, easy to use"
- "Great for prototyping"

**Negative:**
- "Deprecated in 2024"
- "Complex Rust core, hard to fork"
- "Vendor lock-in concerns"

### SQLDelight
**Positive:**
- "SQL-first is refreshing"
- "Great for KMP"
- "Type-safe generated code"

**Negative:**
- "Requires SQL knowledge"
- "Less Android-specific tooling"

### ObjectBox
**Positive:**
- "Fastest benchmarks consistently"
- "Auto migrations are great"
- "Good for offline-first"

**Negative:**
- "No KMP yet"
- "Smaller community than Room"

---

## Conflicting Information

**Topic:** Room vs SQLDelight for KMP
- **Pro-Room:** "Google backing, familiar API"
- **Pro-SQLDelight:** "SQL-first, mature KMP support"
- **Resolution:** Both valid; Room for Android-first, SQLDelight for SQL-heavy

**Topic:** SwiftData vs Core Data
- **Pro-SwiftData:** "Modern, Swift-native, simpler"
- **Pro-CoreData:** "Battle-tested, more features"
- **Resolution:** SwiftData for new iOS 17+ apps, Core Data for complex/legacy

**Topic:** Realm future
- **Some:** "Open source will continue"
- **Others:** "Effectively dead without MongoDB"
- **Resolution:** Migration recommended for new projects

---

## Recommendations

### Android-Only
1. **Standard:** Room + Coroutines + Flow
2. **Performance:** ObjectBox
3. **Legacy migration:** Consider SQLDelight for SQL-heavy

### iOS-Only
1. **iOS 17+:** SwiftData
2. **Complex/Legacy:** Core Data
3. **Performance:** GRDB.swift

### Kotlin Multiplatform
1. **Recommended:** Room KMP (2.7.0+) or SQLDelight
2. **Performance:** ObjectBox (when KMP available)

### Flutter
1. **Default:** Drift
2. **Performance:** ObjectBox
3. **Avoid:** Isar/Hive (maintenance issues)

### React Native
1. **Large datasets:** WatermelonDB
2. **Simple needs:** AsyncStorage + MMKV

### With Sync Requirements
1. **PostgreSQL backend:** PowerSync
2. **MongoDB backend:** PowerSync or ObjectBox
3. **Enterprise:** Couchbase Mobile
4. **Avoid:** Realm (deprecated sync)

---

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [SQLite Architecture](https://sqlite.org/arch.html) | Official | 0.95 | SQLite internals |
| 2 | [Android Room Guide](https://developer.android.com/training/data-storage/room) | Official | 0.95 | Room best practices |
| 3 | [Realm Deprecation Discussion](https://github.com/realm/realm-swift/discussions/8680) | Community | 0.85 | Realm status |
| 4 | [SQLDelight KMP](https://kotlinlang.org/docs/multiplatform/multiplatform-ktor-sqldelight.html) | Official | 0.90 | SQLDelight setup |
| 5 | [ObjectBox Benchmarks](https://objectbox.io/category/benchmarks/) | Vendor | 0.80 | Performance data |
| 6 | [SwiftData Issues](https://mjtsai.com/blog/2024/10/16/returning-to-core-data/) | Expert Blog | 0.85 | SwiftData problems |
| 7 | [GRDB Performance](https://github.com/groue/GRDB.swift/wiki/Performance) | Official | 0.90 | iOS DB benchmarks |
| 8 | [PowerSync Overview](https://docs.powersync.com/intro/powersync-overview) | Official | 0.90 | Sync solution |
| 9 | [Flutter Databases Overview](https://greenrobot.org/database/flutter-databases-overview/) | Expert | 0.85 | Flutter comparison |
| 10 | [WatermelonDB README](https://watermelondb.dev/docs) | Official | 0.90 | RN database |
| 11 | [Room Migration Testing](https://developer.android.com/training/data-storage/room/migrating-db-versions) | Official | 0.95 | Testing guide |
| 12 | [SQLCipher Encryption](https://proandroiddev.com/how-to-encrypt-your-room-database-in-android-using-sqlcipher) | Expert | 0.85 | Encryption |
| 13 | [Core Data Performance](https://www.avanderlee.com/swift/core-data-performance/) | Expert | 0.85 | iOS optimization |
| 14 | [Offline-First Android](https://developer.android.com/topic/architecture/data-layer/offline-first) | Official | 0.95 | Sync strategies |
| 15 | [Room KMP vs SQLDelight](https://medium.com/@muralivitt/database-solutions-for-kmp-cmp-sqldelight-vs-room-ea9a52c7bce7) | Expert | 0.80 | KMP comparison |
| 16 | [SQLite WAL Mode](https://sqlite.org/wal.html) | Official | 0.95 | WAL documentation |
| 17 | [droidcon Database Comparison](https://www.droidcon.com/2025/01/28/local-database-comparing-realm-sqldelight-and-room/) | Conference | 0.85 | 2025 comparison |
| 18 | [Realm Alternatives](https://objectbox.io/alternative-to-mongodb-sync/) | Vendor | 0.80 | Migration options |
| 19 | [Room Coroutines](https://medium.com/androiddevelopers/room-coroutines-422b786dc4c5) | Official | 0.90 | Async queries |
| 20 | [SQLite Performance Best Practices](https://developer.android.com/topic/performance/sqlite-performance-best-practices) | Official | 0.95 | Optimization |

---

## Research Methodology

- **Queries used:** 20 search queries covering SQLite internals, Room, SQLDelight, Realm, ObjectBox, Core Data, SwiftData, GRDB, Flutter databases, sync strategies, encryption, testing
- **Source types:** Official documentation, vendor docs, expert blogs, conference talks, GitHub discussions
- **Coverage:** Android, iOS, Flutter, React Native, Kotlin Multiplatform
- **Key updates:** Realm deprecation (Sept 2024), Room KMP (May 2024), ObjectBox 4.0 vector DB
