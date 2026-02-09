---
title: "Research Report: KMP Unit Testing"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Unit Testing

**Date:** 2026-01-03
**Sources Evaluated:** 18+
**Research Depth:** Deep

## Executive Summary

KMP unit testing использует kotlin.test как базу с expect/actual для платформенных runners. Kotest 5.9.1 предоставляет 300+ matchers (shouldBe, shouldContain, collection matchers). Turbine 1.2.0 — стандарт для тестирования Flow (test{}, awaitItem(), awaitComplete()). runTest из kotlinx-coroutines-test заменяет runBlocking с виртуальным временем и advanceUntilIdle(). Fakes рекомендуются вместо mocks для KMP из-за ограничений MockK на Native.

## Key Findings

1. **kotlin.test Foundation**
   - @Test, @BeforeTest, @AfterTest annotations
   - assertEquals, assertTrue, assertNull, assertFailsWith
   - expect/actual для платформенных runners (JUnit5, XCTest)

2. **Kotest Assertions**
   - 300+ matchers в kotest-assertions-core
   - shouldBe, shouldNotBe, shouldBeNull
   - Collection: shouldContain, shouldHaveSize, shouldBeSorted
   - String: shouldStartWith, shouldMatch
   - Soft assertions: assertSoftly { }
   - Custom matchers через Matcher interface

3. **Turbine for Flow Testing**
   - flow.test { } extension function
   - awaitItem() — получить следующее значение
   - awaitComplete() — дождаться завершения
   - awaitError() — дождаться ошибки
   - cancelAndIgnoreRemainingEvents() — cleanup
   - Поддержка timeout и multiple flows

4. **runTest for Coroutines**
   - Заменяет runBlocking в тестах
   - Виртуальное время (instant execution)
   - advanceUntilIdle() — выполнить все pending coroutines
   - advanceTimeBy(ms) — продвинуть виртуальное время
   - TestDispatcher интеграция

5. **ViewModel Testing Pattern**
   - Inject TestDispatcher
   - Use Turbine for StateFlow testing
   - Pattern: Loading → Action → Success/Error
   - MainDispatcher замена через setMain()

6. **Mocking Strategies**
   - Fakes: recommended for KMP, simple, no dependencies
   - Mokkery: compiler plugin, KMP support
   - Mockative: KSP-based, works everywhere
   - MockK: JVM only, not for Native

## Community Sentiment

### Positive
- kotlin.test достаточен для базовых тестов
- Kotest matchers делают тесты читаемыми
- Turbine значительно упрощает Flow тестирование
- runTest с виртуальным временем ускоряет тесты

### Negative
- MockK не работает на Native (главная проблема)
- Kotest property testing не полностью KMP-совместим
- Turbine timeout иногда срабатывает ложно
- Документация по KMP тестированию разрозненная

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [kotlin.test](https://kotlinlang.org/api/latest/kotlin.test/) | Official | 0.95 | Core assertions |
| 2 | [Kotest](https://kotest.io/docs/assertions/assertions.html) | Official | 0.95 | Matcher library |
| 3 | [Turbine](https://github.com/cashapp/turbine) | GitHub | 0.90 | Flow testing |
| 4 | [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) | Official | 0.95 | runTest |
| 5 | [Testing Coroutines Guide](https://developer.android.com/kotlin/coroutines/test) | Official | 0.95 | Best practices |
| 6 | [Mokkery](https://github.com/nicholassm/mokkery) | GitHub | 0.85 | KMP mocking |
| 7 | [Mockative](https://github.com/nicholassm/mockative) | GitHub | 0.85 | KSP mocking |
