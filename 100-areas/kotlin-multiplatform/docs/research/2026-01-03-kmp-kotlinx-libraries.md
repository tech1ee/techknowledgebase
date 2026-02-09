---
title: "Research Report: kotlinx Libraries in KMP"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: kotlinx Libraries in KMP

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

kotlinx — официальные библиотеки от JetBrains для KMP. serialization 1.9.0 — JSON/Protobuf/CBOR с compile-time safety и polymorphic support через sealed classes. datetime 0.7.1 — Instant, LocalDateTime, TimeZone для кросс-платформенной работы с датами. coroutines 1.10.2 — Flow, StateFlow, Dispatchers (iOS требует SKIE для удобной интеграции). io 0.8.2 — Buffer, Source, Sink на базе Okio. atomicfu мигрирует в stdlib (Kotlin 2.1+).

## Key Findings

1. **kotlinx-serialization**
   - JSON, Protobuf, CBOR, Properties formats
   - Compile-time type safety
   - Sealed classes for polymorphism (recommended)
   - JsonContentPolymorphicSerializer for content-based polymorphism
   - Version 1.9.0 (Kotlin 2.3.0)

2. **kotlinx-datetime**
   - Instant, LocalDateTime, LocalDate, LocalTime
   - TimeZone with platform interop
   - Duration arithmetic
   - Still experimental (0.7.1)

3. **kotlinx-coroutines**
   - Flow, StateFlow, SharedFlow
   - Dispatchers.IO not available on iOS (use Default)
   - SKIE recommended for iOS Flow integration
   - Version 1.10.2

4. **kotlinx-io**
   - Based on Okio but not backward compatible
   - Buffer, Source, Sink primitives
   - File operations support
   - Used by Ktor 3.x internally
   - Version 0.8.2 (experimental)

5. **kotlinx-atomicfu Migration**
   - AtomicInt, AtomicLong, AtomicBoolean, AtomicRef
   - Moving to kotlin.concurrent.atomics (stdlib)
   - Available from Kotlin 2.1.20-Beta1

## Community Sentiment

### Positive
- serialization compile-time safety prevents runtime errors
- datetime simplifies cross-platform date handling
- coroutines work seamlessly in shared code
- io provides consistent API across platforms

### Negative
- datetime still experimental
- iOS Flow collection requires bridging/SKIE
- No Dispatchers.IO on iOS
- serialization single classDiscriminator limitation

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [kotlinx.serialization](https://github.com/Kotlin/kotlinx.serialization) | GitHub | 0.95 | Serialization docs |
| 2 | [Polymorphism Guide](https://github.com/Kotlin/kotlinx.serialization/blob/master/docs/polymorphism.md) | Official | 0.95 | Sealed classes |
| 3 | [kotlinx-datetime](https://github.com/Kotlin/kotlinx-datetime) | GitHub | 0.95 | DateTime API |
| 4 | [kotlinx.coroutines](https://github.com/Kotlin/kotlinx.coroutines) | GitHub | 0.95 | Coroutines |
| 5 | [kotlinx-io](https://github.com/Kotlin/kotlinx-io) | GitHub | 0.90 | IO primitives |
| 6 | [atomicfu migration](https://github.com/Kotlin/kotlinx-atomicfu/issues/493) | GitHub | 0.90 | Stdlib migration |

