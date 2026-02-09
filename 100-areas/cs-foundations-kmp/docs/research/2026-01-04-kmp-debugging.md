# Research Report: KMP Debugging

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

KMP debugging различается между платформами: Android имеет полную поддержку через JDWP, iOS использует LLDB с ограничениями. Kotlin/Native генерирует DWARF 2 debug info, но LLDB видит код как C89 — expression evaluation не работает. xcode-kotlin plugin от Touchlab критичен для комфортной iOS отладки. Crash reporting требует CrashKiOS + отдельный upload dSYM для symbolication. Для cross-platform debugging используй logging (Kermit) и Result types вместо exceptions.

## Key Findings

### 1. Platform Debugging Comparison

| Feature | Android | iOS |
|---------|---------|-----|
| Debugger | JDWP | LLDB |
| Breakpoints | ✅ Full | ✅ Works |
| Variables | ✅ Full | ⚠️ Needs xcode-kotlin |
| Expression eval | ✅ Full | ❌ Not supported |
| Coroutines | ✅ With plugin | ⚠️ Limited |

### 2. DWARF and Debug Symbols

- Kotlin/Native generates DWARF 2 compatible debug info
- Before DWARF 5, no Kotlin language identifier — appears as C89
- dSYM files map memory addresses → source locations
- Required for crash report symbolication

### 3. xcode-kotlin Plugin

**Features:**
- Formats Kotlin objects for Xcode display
- Shows List, Map, StateFlow correctly
- Works in Swift, Kotlin, and Objective-C code
- Version 2.0 is 5x faster than previous

**Installation:**
```bash
brew install xcode-kotlin
```

### 4. Crash Reporting

**CrashKiOS benefits:**
- Captures Kotlin exception message
- Preserves Kotlin stack trace
- Integrates with Crashlytics/Bugsnag

**Without CrashKiOS:**
- Only native stack trace with `konan::abort()`
- No Kotlin exception information

**dSYM Upload:**
- Requires separate Xcode build phase
- Firebase Crashlytics upload-symbols script
- UUID must match crash report

### 5. Exception Handling

**Problem:** Kotlin exceptions lose stack trace at Swift boundary

**Solution:** Use Result types:
```kotlin
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(
        val message: String,
        val stackTrace: String?
    ) : Result<Nothing>()
}
```

### 6. New KMP Plugin (2025)

- Available in IntelliJ IDEA 2025.1.1.1 and Android Studio Narwhal
- Cross-language navigation
- Syntax highlighting
- Debugging support for iOS
- macOS only (Windows/Linux coming)

## Community Sentiment

### Positive
- xcode-kotlin 2.0 significantly improved experience
- Breakpoints and stepping work well
- SKIE can help debug published SPM builds
- CrashKiOS makes crash reports useful

### Negative / Concerns
- Expression evaluation not supported
- Coroutines debugging limited
- dSYM upload requires manual configuration
- LLDB learning curve for Android developers

### Mixed
- "Android first" debugging strategy works but not ideal
- Logging as alternative to debugging controversial

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Native Debugging](https://kotlinlang.org/docs/native-debugging.html) | Official | ★★★★★ | LLDB commands |
| 2 | [xcode-kotlin](https://github.com/touchlab/xcode-kotlin) | Tool | ★★★★★ | Essential plugin |
| 3 | [iOS Symbolication](https://kotlinlang.org/docs/native-ios-symbolication.html) | Official | ★★★★★ | dSYM guide |
| 4 | [CrashKiOS](https://crashkios.touchlab.co/) | Tool | ★★★★☆ | Crash reporting |
| 5 | [Touchlab SPM Debugging](https://touchlab.co/spm-kotlin-debugging) | Blog | ★★★★☆ | Advanced setup |

## Research Methodology

- **Queries used:** 4 search queries
- **Sources found:** 20+ total
- **Sources used:** 15 (after quality filter)
- **Focus areas:** LLDB, xcode-kotlin, crash reporting, symbolication


---

*Проверено: 2026-01-09*
