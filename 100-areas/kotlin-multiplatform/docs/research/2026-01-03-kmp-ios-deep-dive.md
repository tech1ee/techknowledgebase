# Research Report: KMP iOS Deep Dive

**Date:** 2026-01-03
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

iOS — полноценный Tier 1 target в KMP. Compose Multiplatform for iOS достиг Stable статуса в мае 2025 (версия 1.8.0). Swift Export (experimental) позволяет экспортировать Kotlin напрямую в Swift без Objective-C. SKIE от Touchlab улучшает Swift API: Flow → AsyncSequence, suspend → async/await. Новый memory model сделал freeze() deprecated. Performance сравним с native: startup on par, scrolling on par с SwiftUI, +9 MB к размеру.

## Key Findings

1. **Compose Multiplatform iOS Stable (May 2025)**
   - Version 1.8.0 brings iOS to Stable
   - Startup time comparable to native
   - Scrolling on par with SwiftUI (ProMotion 120Hz supported)
   - +9 MB app size overhead
   - 96% of teams report no major performance concerns

2. **Swift Export (Experimental)**
   - Direct Kotlin → Swift export without Obj-C
   - 28 lines vs 175 lines generated code
   - Nullable primitives work natively
   - Overloaded functions work correctly
   - Available in Kotlin 2.2.20+

3. **SKIE (Touchlab)**
   - Flow → AsyncSequence
   - Suspend functions → async/await
   - Sealed classes → Swift exhaustive enums
   - Transparent enum conversion
   - Default argument overloading

4. **Memory Management**
   - New memory model is default
   - freeze() is deprecated
   - GC: stop-the-world mark + concurrent sweep
   - No generational separation yet
   - Can monitor with Xcode Instruments

5. **Integration Methods**
   - Direct Integration (recommended for simple projects)
   - CocoaPods (for projects with pods)
   - SPM via KMMBridge or spmForKmp

## Community Sentiment

### Positive Feedback
- Compose MP iOS is production-ready
- SKIE dramatically improves Swift developer experience
- New memory model removes freeze() complexity
- Performance matches native apps

### Negative Feedback / Concerns
- GitHub issue #4912: high CPU/memory in some cases
- Build speed remains a concern for large projects
- SPM not officially supported (community solutions)
- Some tooling gaps in Xcode debugging

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Compose MP 1.8.0 Release](https://blog.jetbrains.com/kotlin/2025/05/compose-multiplatform-1-8-0-released-compose-multiplatform-for-ios-is-stable-and-production-ready/) | Official | 0.95 | iOS Stable announcement |
| 2 | [iOS Integration Methods](https://kotlinlang.org/docs/multiplatform/multiplatform-ios-integration-overview.html) | Official | 0.95 | Integration approaches |
| 3 | [Swift Export](https://kotlinlang.org/docs/native-swift-export.html) | Official | 0.95 | New Swift interop |
| 4 | [SKIE](https://skie.touchlab.co/) | Tool | 0.90 | Swift API improvements |
| 5 | [Touchlab Memory Debugging](https://touchlab.co/kotlin-ios-memory-debugging-with-xcode-instruments) | Expert | 0.85 | Memory debugging |
| 6 | [KMMBridge](https://kmmbridge.touchlab.co/) | Tool | 0.85 | SPM distribution |
| 7 | [Memory Management](https://kotlinlang.org/docs/native-memory-manager.html) | Official | 0.95 | GC details |
