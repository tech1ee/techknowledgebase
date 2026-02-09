# Research Report: KMP iOS Deep Dive

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

KMP iOS — полноценный Tier 1 target. Compose Multiplatform для iOS стал Stable в мае 2025 (1.8.0). Swift Export (experimental) убирает Objective-C прослойку. SKIE делает Swift API идиоматичным (Flow → AsyncSequence, suspend → async/await). Новый memory model убрал freeze(). Интеграция через XCFramework: Direct, CocoaPods или SPM. Performance: startup сравним с native, scrolling on par с SwiftUI, +9 MB к размеру.

## Key Findings

### 1. Integration Methods Comparison

| Method | Best For | Complexity | Official Support |
|--------|----------|------------|------------------|
| Direct Integration | Monorepo, no CocoaPods deps | Low | ✅ Full |
| CocoaPods (local) | Projects with CocoaPods deps | Medium | ✅ Full |
| CocoaPods (remote) | Distribution as pod | High | ✅ Full |
| SPM (XCFramework) | Modern Apple workflow | Medium | ⚠️ Community |

### 2. Why iOS is Harder Than Android

**Root cause:** Different runtime environments

```
Android: Kotlin → JVM bytecode → Same runtime as Java
iOS:     Kotlin → LLVM IR → Native code → ObjC bridge → Swift
```

**Specific challenges:**
- No stable Swift ABI for FFI → ObjC bridge required
- Different memory models (GC vs ARC)
- LLDB sees Kotlin as C89 (DWARF 2 limitation)
- Expression evaluation not supported in debugger

### 3. Compose Multiplatform iOS Status

**Stable since May 2025 (1.8.0)**

Performance metrics:
- Startup time: comparable to native
- Scrolling: on par with SwiftUI (120Hz ProMotion)
- 96% developers report no performance issues
- Size impact: +9 MB (includes Skia renderer)

Real-world adoption:
- The Respawn: 96% shared code
- Forbes: 80%+ shared code
- Google Docs iOS: "on par or better" vs native Swift

### 4. Swift Export vs ObjC Export

| Aspect | ObjC Export | Swift Export |
|--------|-------------|--------------|
| Generated code | 175 lines | 28 lines |
| Nullable primitives | `KotlinInt` wrapper | `Int?` directly |
| Overloaded functions | Conflicts | Work correctly |
| Package structure | Flat | Preserved via enums |
| Status | Stable | Experimental |

Swift Export goals: Stable in 2026

### 5. SKIE Benefits

**Transformations:**
- Kotlin Flow → Swift AsyncSequence
- Kotlin suspend → Swift async/await
- Kotlin sealed class → Swift enum (exhaustive)
- Kotlin default parameters → Swift overloads

**Impact on code:**
- 6x less boilerplate for Flow consumption
- Native Swift async/await syntax
- Compiler-checked exhaustive matching

### 6. Memory Model Evolution

**Old Model (deprecated):**
- freeze() required for thread sharing
- InvalidMutabilityException on violations
- Complex coroutines usage

**New Model (default since Kotlin 1.7.20):**
- No freeze() needed
- Standard multithreading
- Simple coroutines

**Mixed retain cycles:**
- GC on Kotlin side, ARC on Swift side
- Objects at boundary live by different rules
- Manual cleanup recommended for long-lived references

## Community Sentiment

### Positive
- Compose MP iOS stable is major milestone
- SKIE makes Swift integration seamless
- xcode-kotlin 2.0 significantly improves debugging
- Performance validated by Google Docs team
- Netflix running 12+ apps with KMP

### Negative / Concerns
- iOS builds still slower than native Swift (LLVM backend)
- Binary size larger than pure Swift
- SPM support requires third-party tools
- Expression evaluation not supported in LLDB
- Two Kotlin frameworks can't coexist (binary incompatibility)

### Mixed
- Direct vs CocoaPods vs SPM — no clear winner
- SKIE adds complexity but improves DX
- Compose MP vs SwiftUI — different tradeoffs

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [iOS Integration Overview](https://kotlinlang.org/docs/multiplatform/multiplatform-ios-integration-overview.html) | Official | ★★★★★ | Integration methods |
| 2 | [Compose MP 1.8.0 Release](https://blog.jetbrains.com/kotlin/2025/05/compose-multiplatform-1-8-0-released/) | Official | ★★★★★ | iOS Stable announcement |
| 3 | [SKIE Documentation](https://skie.touchlab.co/) | Tool | ★★★★★ | Swift interop |
| 4 | [KMMBridge](https://kmmbridge.touchlab.co/) | Tool | ★★★★☆ | SPM/CocoaPods distribution |
| 5 | [Swift Export](https://kotlinlang.org/docs/native-swift-export.html) | Official | ★★★★☆ | Future direction |
| 6 | [xcode-kotlin](https://github.com/touchlab/xcode-kotlin) | Tool | ★★★★☆ | Debugging |
| 7 | [Touchlab Blog](https://touchlab.co/blog) | Expert | ★★★★☆ | Best practices |

## Research Methodology

- **Queries used:** 3 search queries
- **Sources found:** 20+ total
- **Sources used:** 15 (after quality filter)
- **WebFetch deep reads:** 2 articles
- **Focus areas:** Integration methods, Compose MP, SKIE, performance, memory


---

*Проверено: 2026-01-09*
