---
title: "Research Report: KMP Debugging"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Debugging

**Date:** 2026-01-04
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

KMP debugging включает LLDB для Kotlin/Native (Xcode), Android Studio debugger для Android. xcode-kotlin plugin от Touchlab критичен для iOS debugging — даёт 5x быстрее variable resolution. Debug info совместим с DWARF 2, LLDB видит Kotlin как C89. Expression evaluation не поддерживается. Для crash reporting: CrashKiOS + Firebase Crashlytics с отдельной загрузкой dSYM для Kotlin framework. Исключения из Kotlin не пробрасываются нормально в Swift — используй Result types.

## Key Findings

1. **LLDB Debugging**
   - DWARF 2 compatible debug info
   - Kotlin seen as C89 by debugger
   - Breakpoints: `b -f file.kt -l 1` or `b kfun:main(...)`
   - Variable inspection works for primitives and objects
   - Expression evaluation NOT supported

2. **xcode-kotlin Plugin (Touchlab)**
   - 5x faster frame variable resolution in 2.0
   - Works in Swift, Kotlin, Objective-C code
   - Built-in List/Map support
   - Install via Homebrew
   - Required for SPM build debugging

3. **Crash Reporting**
   - CrashKiOS for symbolicated Kotlin stack traces
   - Separate dSYM upload needed for Kotlin framework
   - Crashes end with konan::abort() — not useful without CrashKiOS
   - Kermit for logging + Crashlytics integration

4. **iOS Exception Handling**
   - Kotlin exceptions don't propagate well to Swift
   - Use Result types instead of throwing
   - stackTraceToString() for error logging
   - Coroutine stack traces often lost

5. **Common Issues**
   - IntelliJ debugger can't inspect iOS variables sometimes
   - Coroutines make debugging harder
   - Vision Pro simulator can break device list
   - Need Xcode update after each version

## Community Sentiment

### Positive
- xcode-kotlin 2.0 is major improvement
- Android Studio debugging works well
- CrashKiOS solves iOS crash reporting
- Tools are improving rapidly

### Negative
- iOS debugging still challenging (3+ years of issues)
- Expression evaluation not supported
- Coroutines debugging is problematic
- Two crash reports per Kotlin crash (fatal + non-fatal)

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Native Debugging](https://kotlinlang.org/docs/native-debugging.html) | Official | 0.95 | LLDB commands |
| 2 | [xcode-kotlin 2.0](https://touchlab.co/xcode-kotlin-2-0) | Official | 0.90 | Plugin features |
| 3 | [CrashKiOS](https://crashkios.touchlab.co/) | Official | 0.90 | Crash reporting |
| 4 | [Droidcon Debugging](https://www.droidcon.com/2025/07/23/effective-debugging-kotlin-native-in-xcode/) | Blog | 0.85 | Best practices |
| 5 | [Bugfender KMP Debug](https://bugfender.com/blog/how-to-debug-a-kotlin-multiplatform-mobile-app-from-scratch/) | Blog | 0.85 | Complete guide |
