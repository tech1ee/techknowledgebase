---
title: "Research Report: KMP Performance Optimization"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/advanced
---

# Research Report: KMP Performance Optimization

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

KMP performance optimization охватывает три области: build time (компиляция), binary size (размер приложения), runtime performance (производительность). K2 compiler даёт до 94% ускорения билдов и 2x быстрее в enterprise проектах. Kotlin 2.1.21 включает новый inlining pass с 9.5% улучшением runtime. Для iOS: static frameworks, dead_strip, disable bitcode (-50% размера). Value classes — zero-cost abstractions без object allocation. Google Docs iOS на KMP показывает "on par or better" производительность vs native Swift.

## Key Findings

1. **K2 Compiler Performance (Kotlin 2.0+)**
   - Up to 94% compilation speed gains
   - Initialization phase: 488% faster
   - Analysis phase: 376% faster
   - Clean build: 57.7s → 29.7s (Anki-Android)
   - IDE: 1.8x faster highlighting, 1.5x faster completion

2. **Kotlin 2.1.20+ Optimizations**
   - New inlining pass: 9.5% runtime improvement (threshold 40)
   - Xcode 16.3 support
   - Improved incremental compilation

3. **Kotlin/Native Build Optimization**
   - Use linkDebug* not build (10x faster)
   - Cache ~/.konan between builds
   - kotlin.incremental.native=true (experimental)
   - kotlin.native.cacheKind=static
   - Debug builds 10x faster than Release

4. **Binary Size Reduction**
   - Minimum KMP framework: ~6MB release
   - With Ktor: ~19MB per architecture
   - embedBitcode=DISABLE: saves ~3MB
   - Limit exposed interface: reduces Obj-C adapters
   - Final IPA: ~500KB minimum, few MB with libs

5. **Runtime Performance Techniques**
   - Value classes: zero object allocation
   - Sequences for large collections: lazy evaluation
   - tailrec for recursion optimization
   - Coroutines for async without blocking
   - Platform-specific implementations for hot paths

6. **Profiling Tools**
   - iOS: Xcode Instruments, LLDB, Memory Graph
   - Android: Android Studio Profiler
   - Build: Gradle --scan, Build Analyzer

## Community Sentiment

### Positive
- K2 compiler is game-changer for build times
- Google Docs iOS proves production viability
- Value classes excellent for performance-critical code
- Tooling continues to improve rapidly

### Negative
- Kotlin/Native still slower than JVM builds
- Release builds very slow (10x debug)
- Binary size can be large with many dependencies
- Windows antivirus can slow ~/.konan

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [K2 Benchmarks](https://blog.jetbrains.com/kotlin/2024/04/k2-compiler-performance-benchmarks/) | Official | 0.95 | K2 metrics |
| 2 | [Kotlin 2.1.20](https://blog.jetbrains.com/kotlin/2025/03/kotlin-2-1-20-released/) | Official | 0.95 | New features |
| 3 | [KMP Roadmap Aug 2025](https://blog.jetbrains.com/kotlin/2025/08/kmp-roadmap-aug-2025/) | Official | 0.95 | Future plans |
| 4 | [Native Compilation Tips](https://kotlinlang.org/docs/native-improving-compilation-time.html) | Official | 0.95 | Build optimization |
| 5 | [Value Classes](https://kotlinlang.org/docs/inline-classes.html) | Official | 0.95 | Zero-cost abstractions |
| 6 | [Jake Wharton Binary Shrinking](https://jakewharton.com/shrinking-a-kotlin-binary/) | Expert | 0.90 | Size optimization |
| 7 | [iOS Build Fix](https://medium.com/@houssembababendermel/how-i-fixed-my-kmp-ios-build) | Blog | 0.85 | 20min → 2min |
| 8 | [Google I/O KMP](https://android-developers.googleblog.com/2025/05/android-kotlin-multiplatform-google-io-kotlinconf-2025.html) | Official | 0.95 | Google adoption |
