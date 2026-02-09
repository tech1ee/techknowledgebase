---
title: "Research Report: KMP Integration Testing"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Integration Testing

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

KMP integration тесты проверяют взаимодействие компонентов: API через Ktor MockEngine, Database через SQLDelight in-memory drivers (expect/actual для каждой платформы). Fakes рекомендуются вместо mocks из-за отсутствия reflection в Kotlin/Native. SQLDelight in-memory: JdbcSqliteDriver.IN_MEMORY для JVM/Android, NativeSqliteDriver с inMemory=true для iOS (требуется уникальное имя на каждый тест). Testcontainers доступны только для JVM.

## Key Findings

1. **SQLDelight In-Memory Testing**
   - Android/JVM: `JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)`
   - iOS: `NativeSqliteDriver` with `inMemory = true` and unique name per test
   - expect/actual pattern for platform-specific drivers
   - Schema.create(driver) required after driver creation

2. **Ktor MockEngine**
   - Replaces real HTTP engine with predefined responses
   - Supports request history verification
   - Dynamic routing based on path/query parameters
   - Works identically in integration and UI tests

3. **Why Fakes over Mocks**
   - Kotlin/Native lacks runtime reflection
   - MockK is JVM-only
   - Fakes work on all platforms
   - Simpler, more predictable

4. **Repository Testing Pattern**
   - Combine real LocalDataSource (SQLDelight) with MockEngine
   - Test caching behavior
   - Verify fallback to cache on network failure

5. **Available Mocking Libraries**
   - Mokkery: compiler plugin, KMP support
   - Mockative: KSP-based, works everywhere
   - MocKMP: generates fakes via KSP
   - Fakes: recommended, simplest approach

6. **Testcontainers**
   - JVM only (uses Docker)
   - PostgreSQL, MySQL, Redis containers
   - Kotest integration available
   - Not for Native/iOS

## Community Sentiment

### Positive
- In-memory databases ensure test isolation
- MockEngine integrates well with DI frameworks
- Fakes pattern is simple and reliable
- Shared tests reduce duplication

### Negative
- iOS requires unique DB names per test (workaround)
- No MockK on Native
- Testcontainers JVM-only limitation
- Setup complexity for multi-platform tests

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [SQLDelight In-Memory Testing](https://akjaw.com/kotlin-multiplatform-testing-sqldelight-integration-ios-android/) | Blog | 0.90 | Platform drivers |
| 2 | [Ktor MockEngine](https://akjaw.com/using-ktor-client-mock-engine-for-integration-and-ui-tests/) | Blog | 0.90 | MockEngine patterns |
| 3 | [Ktor Client Testing](https://ktor.io/docs/client-testing.html) | Official | 0.95 | Official docs |
| 4 | [KMP Testing 2025](https://www.kmpship.app/blog/kotlin-multiplatform-testing-guide-2025) | Blog | 0.85 | Overview |
| 5 | [Kotest Testcontainers](https://kotest.io/docs/extensions/test_containers.html) | Official | 0.90 | JVM integration |
| 6 | [KMP Testing Medium](https://medium.com/@santimattius/kmp-for-mobile-native-developers-part-5-testing-46e150d26750) | Blog | 0.85 | Patterns |
