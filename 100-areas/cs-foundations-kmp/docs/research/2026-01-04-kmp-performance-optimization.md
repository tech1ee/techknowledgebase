# Research Report: KMP Performance Optimization

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

KMP performance optimization охватывает три области: build time (K2 compiler даёт 40-94% ускорение, linkDebug* вместо build экономит 10x), binary size (embedBitcode=DISABLE, limit exposed API, dead_strip), runtime (value classes, sequences, tailrec, inline). Google Docs iOS на KMP показывает "on par or better" vs native Swift. Главное правило: профилируй перед оптимизацией.

## Key Findings

### 1. Build Time Optimization

**K2 Compiler Performance:**
- Anki-Android: 57.7s → 29.7s (-49%)
- Analysis phase: до 4x быстрее
- Initialization: до 5x быстрее

**Gradle Settings:**
```properties
org.gradle.jvmargs=-Xmx6g
org.gradle.parallel=true
org.gradle.caching=true
kotlin.incremental.native=true
```

**Debug vs Release:**
- Release builds в 10x медленнее из-за LLVM оптимизаций
- Используй linkDebug* при разработке

**Caching:**
- Кэшируй ~/.konan в CI
- Используй configuration-cache
- Windows: добавь .konan в исключения антивируса

### 2. Binary Size Optimization

**Typical sizes:**
- Minimum "Hello World": ~6 MB
- + Ktor: +13 MB
- + SQLDelight: +2 MB
- + kotlinx-serialization: +3 MB

**Оптимизации:**
- embedBitcode = DISABLE (iOS 16+ не использует)
- linkerOpts += "-dead_strip"
- internal вместо public для implementation details
- Один umbrella framework вместо нескольких

### 3. Runtime Performance

**Value Classes:**
- Zero allocation для wrappers
- Boxing при nullable, generics, Any
- 2-3x быстрее в tight loops

**Sequences:**
- Lazy evaluation
- Выгодны при 1000+ элементов
- Early termination (take, first)

**Inline Functions:**
- Убирает call overhead
- Убирает lambda allocation
- Увеличивает code size

**tailrec:**
- Компилируется в loop
- Избегает stack overflow

### 4. Profiling Tools

| Platform | Tool | Purpose |
|----------|------|---------|
| Android | Studio Profiler | CPU, Memory, Network |
| iOS | Xcode Instruments | Time Profiler, Allocations |
| Gradle | Build Scan | Build analysis |
| Multi | kotlinx-benchmark | Microbenchmarks |

### 5. Real-World Results

**Google Docs iOS (KMP):**
- Performance: "on par or better" vs native Swift
- Code sharing: 95%+ with Android
- Google contributed: LLVM 16, better GC, string optimizations

**K2 Adoption:**
- Exposed project: 80% compiler speed improvement
- Anki-Android: 94% improvement

## Community Sentiment

### Positive
- K2 significantly improves build times
- Google Docs proves production viability
- Value classes are powerful for hot paths
- Sequences help with large data processing

### Negative / Concerns
- iOS builds still slower than native Swift
- LLVM backend is the bottleneck (K2 doesn't help)
- Binary size larger than native
- Value class boxing can be surprising

### Mixed
- Debug vs Release tradeoff requires understanding
- Optimization requires profiling first (no silver bullets)

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Native Compilation Tips](https://kotlinlang.org/docs/native-improving-compilation-time.html) | Official | ★★★★★ | Authoritative |
| 2 | [K2 Benchmarks](https://blog.jetbrains.com/kotlin/2024/04/k2-compiler-performance-benchmarks/) | Official | ★★★★★ | Performance data |
| 3 | [Value Classes](https://kotlinlang.org/docs/inline-classes.html) | Official | ★★★★★ | Best practices |
| 4 | [kotlinx-benchmark](https://github.com/Kotlin/kotlinx-benchmark) | Tool | ★★★★☆ | Benchmarking |
| 5 | [KMP Roadmap 2025](https://blog.jetbrains.com/kotlin/2024/10/kotlin-multiplatform-development-roadmap-for-2025/) | Official | ★★★★☆ | Future improvements |

## Research Methodology

- **Queries used:** 4 search queries
- **Sources found:** 25+ total
- **Sources used:** 20 (after quality filter)
- **WebFetch deep reads:** 2 articles
- **Focus areas:** Build time, binary size, runtime, profiling


---

*Проверено: 2026-01-09*
