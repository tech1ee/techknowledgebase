# Research Report: KMP Third-Party Libraries

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

Экосистема KMP насчитывает 3000+ библиотек на klibs.io. Apollo Kotlin 4.x — GraphQL с type-safe codegen и normalized caching. Coil 3.x — image loading для Compose MP (Android, iOS, Desktop, Wasm). Realm 3.x — offline-first база с опциональным MongoDB Atlas sync. multiplatform-settings — key-value storage. Napier/Kermit — logging. MOKO — resources, permissions, mvvm от IceRock.

## Key Findings

1. **klibs.io**
   - Official JetBrains catalog
   - 3000+ KMP libraries
   - AI-powered search
   - Platform filtering

2. **Apollo Kotlin 4.x**
   - Strongly-typed GraphQL
   - Code generation from .graphql
   - Normalized cache with SQLite
   - watch() for Flow updates

3. **Coil 3.x**
   - Compose Multiplatform support
   - Memory + disk caching
   - Ktor network backend
   - PlatformContext instead of Context

4. **Realm Kotlin 3.x**
   - Object-oriented database
   - Offline-first
   - Optional MongoDB Atlas sync
   - Flow integration

5. **Utility Libraries**
   - multiplatform-settings: key-value storage
   - Napier: logging (like Timber)
   - KVault: secure storage
   - MOKO: resources, permissions, mvvm

## Community Sentiment

### Positive
- Ecosystem growing rapidly (doubled in 2024)
- klibs.io makes discovery easy
- Major libraries (Apollo, Coil) have KMP support
- Realm provides true offline-first

### Negative
- Not all libraries support all platforms
- Kotlin version compatibility issues
- Some libraries still in alpha/beta
- Documentation varies in quality

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [klibs.io](https://klibs.io) | Official | 0.95 | Library catalog |
| 2 | [Apollo Kotlin](https://www.apollographql.com/docs/kotlin) | Official | 0.95 | GraphQL docs |
| 3 | [Coil](https://coil-kt.github.io/coil/) | Official | 0.95 | Image loading |
| 4 | [Realm Kotlin](https://github.com/realm/realm-kotlin) | GitHub | 0.90 | Database |
| 5 | [multiplatform-settings](https://github.com/russhwolf/multiplatform-settings) | GitHub | 0.90 | Key-value |
| 6 | [Napier](https://github.com/AAkira/Napier) | GitHub | 0.85 | Logging |
| 7 | [MOKO](http://moko.icerock.dev/) | Official | 0.90 | IceRock libs |
| 8 | [kmp-awesome](https://github.com/terrakok/kmp-awesome) | GitHub | 0.85 | Curated list |

