# Research Report: KMP Testing Deep Dive 2025

**Date:** 2026-01-05
**Sources Evaluated:** 35+
**Research Depth:** Deep

## Executive Summary

KMP тестирование в 2025 достигло зрелости с чёткой экосистемой: kotlin.test как стандарт для multiplatform, Kotest 6.0 для advanced DSL и property testing, Turbine для Flow testing, kotlinx-coroutines-test с runTest/TestDispatcher для coroutines. Мокирование остаётся challenge — MockK не поддерживает Kotlin/Native, рекомендуются Mokkery (compiler plugin) или manual fakes. Kover — official tool для code coverage. Three-layer architecture (Unit 80%+, Integration 60-70%, UI 30-40%) — production best practice.

## Key Findings

### 1. Testing Frameworks Landscape 2025

| Framework | Type | Multiplatform | Best For |
|-----------|------|---------------|----------|
| kotlin.test | Annotation | ✅ All platforms | Default choice |
| Kotest 6.0 | DSL | ✅ JVM, JS, Native, Wasm | Advanced DSL, property testing |
| JUnit 5 | Annotation | ❌ JVM only | Android, Spring |
| TestBalloon | DSL (compiler) | ✅ Via plugin | Newest, innovative |
| Prepared | DSL (layered) | ⚠️ Depends on base | Fixture management |

**Kotest 6.0 Changes:**
- Simplified multiplatform setup (no compiler plugin)
- Gradle plugin `io.kotest.multiplatform` version 6.0.0.M4
- JS, Wasm, Native engines feature-limited vs JVM

### 2. Coroutine Testing: runTest + TestDispatcher

**Core Pattern:**
```kotlin
@Test
fun testCoroutine() = runTest {
    val result = repository.fetchData()
    assertEquals(expected, result)
}
```

**Two TestDispatchers:**

| Dispatcher | Behavior | Use Case |
|------------|----------|----------|
| StandardTestDispatcher | Pauses at launch/async, requires manual advance | Precise control |
| UnconfinedTestDispatcher | Immediate execution | Simple tests, backward compat |

**Virtual Time Control:**
```kotlin
@Test
fun testWithDelay() = runTest {
    val values = mutableListOf<Int>()
    launch {
        delay(1000)
        values.add(1)
    }
    advanceTimeBy(1000)
    assertEquals(listOf(1), values)
}
```

**Critical Rule:** One scheduler per test — all TestDispatchers must share same scheduler.

### 3. Flow Testing with Turbine

**Current Version:** 1.2.1 (stable), 1.3.0-SNAPSHOT

**Basic Pattern:**
```kotlin
@Test
fun testFlow() = runTest {
    flowOf(1, 2, 3).test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()
    }
}
```

**StateFlow Best Practice:**
```kotlin
// Prefer value property over Turbine for StateFlow
assertEquals(expected, stateFlow.value)
```

**Multiple Flows:**
```kotlin
turbineScope {
    val turbine1 = flow1.testIn(backgroundScope)
    val turbine2 = flow2.testIn(backgroundScope)
    // Test both...
}
```

**Key Methods:**
- `awaitItem()` — get next emission
- `awaitComplete()` — assert completion
- `expectNoEvents()` — verify no emissions
- `cancelAndIgnoreRemainingEvents()` — cleanup

### 4. Mocking in KMP: The Challenge

**Why MockK Doesn't Work:**
- Kotlin/Native is statically compiled
- No reflection or runtime type inspection
- MockK relies on JVM reflection mechanisms

**Recommended Solutions:**

| Library | Approach | Platforms | Pros | Cons |
|---------|----------|-----------|------|------|
| **Mokkery** | Compiler Plugin | All (JVM, Native, JS, Wasm) | MockK-like API, boilerplate-free | Single maintainer |
| **Mockative** | KSP | All | Annotation-based | Generated code |
| **KMock** | KSP | All | Full KMP | Complex setup |
| **MocKMP** | KSP | All | Kodein ecosystem | Interface-only |
| **Manual Fakes** | Handwritten | All | Simple, debuggable | Boilerplate |

**Mokkery Example:**
```kotlin
val repository = mock<UserRepository>()
everySuspend { repository.findById(any()) } returns User("1", "John")

verifySuspend { repository.findById("1") }
```

**Production Recommendation:** Manual fakes for simple cases, Mokkery for complex scenarios.

### 5. Three-Layer Testing Architecture

```
┌─────────────────────────────────────────────┐
│ Layer 3: UI Tests (30-40%)                  │
│ Platform-specific or Compose MP             │
│ Critical user journeys only                 │
├─────────────────────────────────────────────┤
│ Layer 2: Integration Tests (60-70%)         │
│ commonTest + platform-specific              │
│ Database, network, platform APIs            │
├─────────────────────────────────────────────┤
│ Layer 1: Unit Tests (80%+)                  │
│ commonTest source set                       │
│ Pure functions, business logic              │
└─────────────────────────────────────────────┘
```

**Coverage Targets by Layer:**
- Domain layer: 80-90%
- Data layer: 70-80%
- Presentation layer: 60-70%
- UI layer: 30-40%
- **Overall: 65-75% = excellent**

### 6. Platform-Specific Testing

**Directory Structure:**
```
shared/src/
├── commonMain/
├── commonTest/          # Shared tests
├── androidMain/
├── androidTest/         # Android JVM unit tests
├── androidAndroidTest/  # Android instrumented tests
├── iosMain/
└── iosTest/             # iOS tests
```

**Android vs iOS Differences:**

| Aspect | Android | iOS |
|--------|---------|-----|
| Unit Tests | JVM (no emulator) | Simulator required |
| Instrumented | Emulator/device | Simulator/device |
| Framework | JUnit 4/5 | XCTest |
| UI Testing | Espresso | XCTest UI |
| Test Separation | Separate directories | Same target |

**Common Mistake:** Placing Android instrumented tests in `androidTest` instead of `androidAndroidTest` causes runtime exceptions.

### 7. Compose Multiplatform UI Testing

**API:**
```kotlin
@Test
fun testButton() = runComposeUiTest {
    setContent {
        MyButton(onClick = {})
    }

    onNodeWithText("Click me")
        .performClick()
        .assertIsEnabled()
}
```

**Screenshot Testing Options:**

| Tool | Type | Platforms |
|------|------|-----------|
| ComposablePreviewScanner | Preview-based | Android, Desktop |
| Compose Preview Screenshot | Official (alpha) | Android |
| Telereso KMP | Desktop-based | All (CI-friendly) |
| Snappy | Snapshot | Multiplatform |

**Best Practice:** Use `testTag` for stable selectors:
```kotlin
Modifier.testTag("submit_button")
```

### 8. Property-Based Testing

**Kotest (Multiplatform):**
```kotlin
class PropertyTest : StringSpec({
    "length is always non-negative" {
        checkAll<String> { str ->
            str.length shouldBeGreaterThanOrEqualTo 0
        }
    }
})
```

**jqwik (JVM only, more powerful):**
```kotlin
@Property
fun stringConcatenation(@ForAll a: String, @ForAll b: String) =
    (a + b).length == a.length + b.length
```

**Comparison:**
- Kotest: Multiplatform, integrated, simpler
- jqwik: More sophisticated shrinking, exhaustive generation, state-based testing

### 9. Code Coverage with Kover

**Setup:**
```kotlin
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.9.4"
}
```

**Commands:**
```bash
./gradlew koverHtmlReport      # HTML report
./gradlew koverXmlReport       # CI integration
./gradlew koverVerify          # Enforce thresholds
```

**CI/CD Integration:**
```yaml
- name: Run tests with coverage
  run: ./gradlew koverXmlReportDebug

- name: Upload coverage
  uses: mi-kas/kover-report@v1
  with:
    min-coverage-overall: 60
```

**Limitations:**
- JS and Native targets not supported yet
- Android instrumented tests not supported

### 10. Test Architecture Patterns

**AAA Pattern (Arrange-Act-Assert):**
```kotlin
@Test
fun testUserCreation() {
    // Arrange
    val repository = FakeUserRepository()
    val useCase = CreateUserUseCase(repository)

    // Act
    val result = useCase.execute("John")

    // Assert
    assertEquals(User("John"), result)
}
```

**Given-When-Then (Kotest):**
```kotlin
"given valid input" - {
    val input = ValidInput()

    "when processing" - {
        val result = processor.process(input)

        "then should succeed" {
            result.shouldBeSuccess()
        }
    }
}
```

## Community Sentiment

### Positive
- kotlin.test simplicity praised
- Turbine "essential" for Flow testing
- Kotest assertions expressiveness loved
- runTest + TestDispatcher finally stable
- Kover native Kotlin support welcomed

### Negative / Concerns
- MockK KMP support absence frustrating
- Kotest slow update cycles (6.0 delayed)
- Screenshot testing cross-platform challenges
- Kover no JS/Native support
- Test configuration complexity (androidTest vs androidAndroidTest)

### Mixed
- Manual fakes vs mocking libraries debate
- JUnit vs Kotest preference varies
- Property testing adoption still low
- UI test coverage targets controversial

## Recommended Stack (2025)

```
Framework:      kotlin.test (default) + Kotest (advanced)
Coroutines:     kotlinx-coroutines-test 1.10+
Flows:          Turbine 1.2+
Mocking:        Manual fakes / Mokkery 3.1+
Coverage:       Kover 0.9+
Assertions:     Kotest Assertions 5.8+
Property:       Kotest PropTest / jqwik (JVM)
UI:             runComposeUiTest + Telereso (screenshots)
```

## Best Practices Checklist

1. ✅ Write tests in `commonTest` by default
2. ✅ Use `runTest` for all coroutine tests
3. ✅ Use Turbine for Flow testing (not manual collection)
4. ✅ Prefer manual fakes over mocking in shared code
5. ✅ Test contracts, not implementation details
6. ✅ Use in-memory databases for integration tests
7. ✅ Add `testTag` to Compose UI elements
8. ✅ Don't chase 100% coverage — focus on quality
9. ✅ Separate Android instrumented tests properly
10. ✅ Run tests on both platforms in CI

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [JetBrains KMP Testing Tutorial](https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-run-tests.html) | Official | ★★★★★ | Test structure |
| 2 | [Compose MP Testing Docs](https://kotlinlang.org/docs/multiplatform/compose-test.html) | Official | ★★★★★ | UI testing API |
| 3 | [Turbine GitHub](https://github.com/cashapp/turbine) | Official | ★★★★★ | Flow testing |
| 4 | [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) | Official | ★★★★★ | runTest, TestDispatcher |
| 5 | [Kotest Docs](https://kotest.io/) | Official | ★★★★★ | DSL, property testing |
| 6 | [Kover GitHub](https://github.com/Kotlin/kotlinx-kover) | Official | ★★★★★ | Coverage tool |
| 7 | [Mokkery Docs](https://mokkery.dev/) | Official | ★★★★☆ | KMP mocking |
| 8 | [KMPShip Testing Guide 2025](https://www.kmpship.app/blog/kotlin-multiplatform-testing-guide-2025) | Blog | ★★★★☆ | Production practices |
| 9 | [State of Kotlin Tests 2025](https://ivan.canet.dev/blog/2025/06/17/state-of-kotlin-tests.html) | Blog | ★★★★☆ | Framework comparison |
| 10 | [Touchlab KMM Test Suite](https://touchlab.co/understanding-and-configuring-your-kmm-test-suite/) | Blog | ★★★★☆ | Project structure |
| 11 | [Android Coroutine Testing](https://developer.android.com/kotlin/coroutines/test) | Official | ★★★★★ | Android specifics |
| 12 | [Mocking in KMP: KSP vs Plugins](https://medium.com/@mhristev/mocking-in-kotlin-multiplatform-ksp-vs-compiler-plugins-4424751b83d7) | Blog | ★★★★☆ | Mocking approaches |
| 13 | [jqwik Property Testing](https://johanneslink.net/property-based-testing-in-kotlin/) | Blog | ★★★★☆ | PBT deep dive |
| 14 | [Compose Screenshot Testing](https://github.com/sergio-sastre/ComposablePreviewScanner) | GitHub | ★★★★☆ | Screenshot tools |
| 15 | [MockK GitHub](https://github.com/mockk/mockk) | Official | ★★★★★ | JVM mocking |

## Research Methodology

- **Queries used:** 12 search queries
- **Sources found:** 50+ total
- **Sources used:** 35 (after quality filter)
- **Focus areas:** Testing frameworks, coroutines, mocking, coverage, platform-specific, UI testing

---

*Проверено: 2026-01-09*
