# Research Report: KMP Testing Strategies

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

KMP тесты организуются в commonTest (shared, запускаются на всех платформах) и platform-specific (androidTest, iosTest). Test Pyramid: 70% unit, 20% integration, 10% UI. Библиотеки: kotlin.test + Kotest assertions + Turbine (Flow) + Mokkery/Mockative (mocks). Kover для coverage (только JVM/Android, Native не поддерживается). CI через GitHub Actions с macOS runner для iOS тестов.

## Key Findings

1. **Test Structure**
   - commonTest: shared tests, run on all platforms
   - androidUnitTest: Android-specific unit tests
   - iosTest: iOS-specific tests
   - androidInstrumentedTest: UI tests

2. **Mocking in KMP**
   - MockK: JVM only, not for Native
   - Mokkery: Compiler plugin, KMP support
   - Mockative: KSP-based, works everywhere
   - Fakes: Recommended, simplest approach

3. **Testing Libraries**
   - kotlin.test: Basic assertions
   - Kotest: 300+ rich assertions
   - Turbine: Flow testing
   - kotlinx-coroutines-test: runTest

4. **Code Coverage**
   - Kover: Official JetBrains plugin
   - Only JVM/Android supported
   - HTML, XML reports
   - Verification thresholds

5. **CI/CD**
   - macOS runner required for iOS
   - allTests gradle task
   - Codecov integration

## Community Sentiment

### Positive
- commonTest provides maximum coverage with minimum code
- Fakes are simpler than mocks for KMP
- Turbine makes Flow testing easy
- Kover integrates well with CI

### Negative
- No MockK on Native
- Kover doesn't support Native/JS
- iOS tests require macOS
- Mocking libraries still maturing

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Multiplatform Testing](https://kotlinlang.org/docs/multiplatform/multiplatform-run-tests.html) | Official | 0.95 | Official docs |
| 2 | [Touchlab KMM Testing](https://touchlab.co/understanding-and-configuring-your-kmm-test-suite/) | Blog | 0.90 | Test structure |
| 3 | [Kotest](https://kotest.io/) | Official | 0.95 | Assertions |
| 4 | [Turbine](https://github.com/cashapp/turbine) | GitHub | 0.90 | Flow testing |
| 5 | [Kover](https://github.com/Kotlin/kotlinx-kover) | GitHub | 0.95 | Coverage |
| 6 | [KMP Testing 2025](https://www.kmpship.app/blog/kotlin-multiplatform-testing-guide-2025) | Blog | 0.85 | Overview |
| 7 | [Mokkery](https://github.com/nicholassm/mokkery) | GitHub | 0.85 | KMP mocking |

