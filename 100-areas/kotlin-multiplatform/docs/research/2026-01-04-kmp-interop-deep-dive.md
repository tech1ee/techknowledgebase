---
title: "Research Report: KMP Interop Deep Dive"
type: deep-dive
status: published
tags:
  - topic/kmp
  - type/deep-dive
  - level/advanced
---

# Research Report: KMP Interop Deep Dive

**Date:** 2026-01-04
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

KMP interop охватывает три механизма: Objective-C interop (stable, через ObjC bridge), Swift Export (experimental, прямой Swift), cinterop (C/ObjC библиотеки). SKIE от Touchlab добавляет async/await, sealed classes, Flow→AsyncSequence пока Swift Export не ready. Generics ограничены в ObjC (теряется type info), Swift Export лучше с nullability. Suspend функции конвертируются в async/completionHandler. @Throws нужен для propagation исключений.

## Key Findings

1. **Objective-C Interop (Stable)**
   - Kotlin → ObjC headers → Swift
   - Collections: List→NSArray, Map→NSDictionary
   - Suspend → async/completionHandler
   - Generics limited (T becomes T?)
   - @Throws for exception propagation

2. **Swift Export (Experimental)**
   - Direct Kotlin → Swift (no ObjC bridge)
   - Better nullability for primitives
   - Native Swift enums from enum class
   - Type aliases preserved
   - Packages as Swift enums
   - Target: Stable in 2026

3. **SKIE (Touchlab)**
   - Flow → AsyncSequence
   - Suspend → async/await
   - Sealed classes with enums
   - Production-ready now
   - Bridge until Swift Export stable

4. **cinterop (C Libraries)**
   - .def files for configuration
   - Headers → Kotlin bindings
   - Platform libraries built-in
   - Static library embedding supported

5. **Best Practices**
   - Use @ObjCName for Swift-friendly names
   - @HiddenFromObjC for internal code
   - Avoid passing large collections
   - Explicit NSArray/NSDictionary casts for performance

## Community Sentiment

### Positive
- SKIE dramatically improves iOS developer experience
- Swift Export is promising future
- ObjC interop is stable and works
- cinterop enables any C library integration

### Negative
- Swift Export not production ready
- Generic limitations frustrating
- Exception handling complex
- Performance overhead with collections

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [ObjC Interop](https://kotlinlang.org/docs/native-objc-interop.html) | Official | 0.95 | Complete reference |
| 2 | [Swift Export](https://kotlinlang.org/docs/native-swift-export.html) | Official | 0.95 | Experimental docs |
| 3 | [SKIE](https://skie.touchlab.co/) | Official | 0.90 | Production tool |
| 4 | [C Interop](https://kotlinlang.org/docs/native-c-interop.html) | Official | 0.95 | cinterop guide |
| 5 | [Swift Interopedia](https://github.com/kotlin-hands-on/kotlin-swift-interopedia) | Official | 0.90 | Examples |
