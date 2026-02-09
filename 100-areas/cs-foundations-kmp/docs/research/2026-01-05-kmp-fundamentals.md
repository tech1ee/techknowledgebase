# Research Report: KMP Fundamentals

**Date:** 2026-01-05
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

KMP (Kotlin Multiplatform) — набор официальных инструментов для кросс-платформенной разработки. Компилирует код в platform-specific binaries: JVM bytecode (Android/JVM), LLVM native (iOS), JavaScript/WASM (Web). Expect/actual — механизм для platform-specific APIs в common code. Source sets образуют иерархию через dependsOn. Default Hierarchy Template упрощает настройку, но может замедлить sync в больших проектах. Новый Android-KMP plugin (`com.android.kotlin.multiplatform.library`) заменит старый в AGP 10.0.

## Key Findings

### 1. How KMP Works Under the Hood

**Compilation Backends:**

| Platform | Backend | Output | Notes |
|----------|---------|--------|-------|
| Android/JVM | Kotlin/JVM | JVM bytecode | Most mature |
| iOS | Kotlin/Native (LLVM) | Native binary | ObjC headers |
| Web | Kotlin/JS or Kotlin/WASM | JS or WASM | WasmGC in Beta |
| Desktop | Kotlin/JVM | JVM bytecode | Same as JVM |

**Architecture:**
```
Kotlin Source Code
       │
       ├─→ Kotlin/JVM → JVM Bytecode → Android/Desktop/Server
       │
       ├─→ Kotlin/Native → LLVM IR → Native Binary → iOS/macOS/Linux
       │
       └─→ Kotlin/JS|WASM → JavaScript/WASM → Browser/Node.js
```

### 2. Expect/Actual Mechanism

**Purpose:** Access platform-specific APIs from common code

**Syntax:**
```kotlin
// commonMain (expect)
expect fun getPlatformName(): String

// androidMain (actual)
actual fun getPlatformName(): String = "Android ${Build.VERSION.SDK_INT}"

// iosMain (actual)
actual fun getPlatformName(): String = "iOS ${UIDevice.currentDevice.systemVersion}"
```

**Rules:**
- Every `expect` must have matching `actual` in all targets
- Works for: functions, classes, interfaces, enums, properties, annotations
- Compiler enforces matching at compile time

**Best practice:** Prefer interfaces over expect/actual for flexibility (testing, multiple implementations)

### 3. Source Set Hierarchy

**Structure:**
```
src/
├── commonMain/           # Shared code (expect declarations)
├── commonTest/           # Shared tests
├── androidMain/          # Android-specific (actual declarations)
├── iosMain/              # iOS-specific (actual declarations)
│   ├── iosArm64Main/     # iOS device
│   └── iosSimulatorArm64Main/  # iOS simulator
└── jvmMain/              # JVM/Desktop-specific
```

**dependsOn Relationship:**
- Creates hierarchy between source sets
- Determines code visibility and dependency propagation
- `androidMain.dependsOn(commonMain)` = Android can use common code

### 4. Default Hierarchy Template

**Benefit:** Auto-configures intermediate source sets based on targets

**Caution:** In large codebases (70+ modules), can slow sync from 15 min to 1+ hour

**Manual override:**
```kotlin
kotlin {
    applyDefaultHierarchyTemplate()
    // or custom hierarchy
}
```

### 5. Gradle Best Practices (2025)

**Required:**
- Kotlin DSL (not Groovy)
- Version catalogs (`libs.versions.toml`)
- kotlin-multiplatform plugin 2.3.0+
- KSP instead of KAPT

**New Android Plugin:**
```kotlin
// OLD (deprecated in AGP 9.0, removed in AGP 10.0)
plugins {
    id("com.android.library")
    kotlin("multiplatform")
}

// NEW (recommended)
plugins {
    kotlin("multiplatform")
    id("com.android.kotlin.multiplatform.library")
}
```

**withJava() deprecated:** Java source sets created by default since Kotlin 2.1.20

### 6. Production Readiness

**Status:** Stable since November 2023

**Adoption:**
- Netflix: 12+ apps
- McDonald's: Global mobile app
- Cash App: Fintech
- Philips: Healthcare

**Efficiency:** ~40% development efficiency gains reported

## Community Sentiment

### Positive
- Mature JVM backend
- Growing iOS support
- Official Jetpack libraries
- Strong JetBrains commitment
- Real production success stories

### Negative / Concerns
- iOS builds slower than native Swift
- Default Hierarchy Template can slow large projects
- Learning curve for iOS developers
- Some library ecosystem gaps

### Mixed
- Swift Export still experimental (goal: 2025)
- Compose for Web in Beta
- Tooling improving but not complete

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Project Structure Basics](https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-discover-project.html) | Official | ★★★★★ | Structure guide |
| 2 | [Gradle Best Practices](https://kotlinlang.org/docs/gradle-best-practices.html) | Official | ★★★★★ | Gradle config |
| 3 | [Platform-Specific APIs](https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-connect-to-apis.html) | Official | ★★★★★ | Expect/actual |
| 4 | [Hierarchical Structure](https://kotlinlang.org/docs/multiplatform-hierarchy.html) | Official | ★★★★★ | Source sets |
| 5 | [Under the Hood Article](https://ranveergour781.medium.com/how-kotlin-multiplatform-works-under-the-hood-and-why-jetbrains-is-all-in-83514d5fa2ef) | Community | ★★★★☆ | Deep dive |
| 6 | [2025 Roadmap](https://blog.jetbrains.com/kotlin/2024/10/kotlin-multiplatform-development-roadmap-for-2025/) | Official | ★★★★☆ | Future plans |

## Research Methodology

- **Queries used:** 3 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **Focus areas:** Architecture, expect/actual, source sets, Gradle


---

*Проверено: 2026-01-09*
