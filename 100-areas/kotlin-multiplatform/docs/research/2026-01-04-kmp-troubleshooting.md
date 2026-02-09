---
title: "Research Report: KMP Troubleshooting"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Troubleshooting

**Date:** 2026-01-04
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

KMP troubleshooting охватывает Gradle sync issues, iOS build errors, expect/actual проблемы, memory leaks, и crash debugging. Ключевые проблемы 2025-2026: Xcode 16 linker (exit code 138 → `-ld_classic`), AGP 9 migration (`com.android.kotlin.multiplatform.library`), CrashKiOS + dynamic frameworks crash on launch, withJava() deprecation. Expect/actual частые ошибки: default implementations в expect classes (используй interfaces), iOS ограничения default arguments и generics. Memory: freeze() deprecated, new memory manager default, mixed retain cycles не собираются.

## Key Findings

### 1. Gradle Sync Issues (2025-2026)

**AGP 9 Migration:**
- `com.android.library` deprecated, use `com.android.kotlin.multiplatform.library`
- Break occurs AGP 9.0.0-alpha14+
- Android Studio Otter 2 fixes Compose preview failures
- `androidLibrary{}` → `android{}` block migration

**withJava() Deprecation:**
- From Kotlin 2.1.20, Java source sets created by default
- Remove if Gradle 8.7+ and no Java plugins needed

**CInterop Commonization Issue:**
- `kotlin.mpp.enableCInteropCommonization=true` causes sync failure
- Runs `compileCommonMainKotlinMetadata` during sync

### 2. iOS Build/Linker Errors

**Xcode 16 + Kotlin 2.1.0:**
- Exit code 138, SIGBUS
- Fix: `linkerOpts("-ld_classic")`
- BUT: may cause CrashKiOS crash on launch
- Solution: remove CrashKiOS or wait for fix

**Framework Not Found:**
- Check Build Active Architecture Only = Yes
- Use .xcworkspace, not .xcodeproj
- Framework Search Paths: `$(SRCROOT)/library/.../$(CONFIGURATION)/$(SDK_NAME)`
- SQLDelight needs: `-lsqlite3` in Other Linker Flags

**Architecture Mismatch:**
- arm64 vs x86_64 simulator
- Add arm64 to EXCLUDED_ARCHS if needed

### 3. Expect/Actual Errors

**Common Mistakes:**
- Default implementations in expect classes → use interfaces instead
- Interface owns default implementation, actual implements interface
- expect class acts as bridge

**iOS-Specific:**
- Default arguments don't work through ObjC bridge
- Provide explicit overloads for common cases
- Generics limited in ObjC interop
- Will be fixed with Swift Export (Kotlin 2.2.20+)

### 4. Memory Issues

**Freeze Deprecated:**
- New memory manager is default
- Remove all freeze() calls
- AtomicReference cycles don't leak anymore

**Debugging Tools:**
- Xcode Instruments with signposts
- `GC.lastGCInfo()` for stats
- Enable concurrent marking for better performance

**iOS Strict Memory:**
- 50MB limit for network extensions
- GC may not release fast enough
- Use `kotlin.native.binary.pagedAllocator=false` for strict limits

### 5. Crash Debugging

**CrashKiOS Issues:**
- Problems with dynamic frameworks
- Kotlin 2.1.0 compatibility issues
- May need to remove temporarily

**Stack Traces:**
- Kotlin crashes show konan::abort() without symbolication
- Need separate dSYM upload for Kotlin framework
- Use Kermit + Crashlytics for logging

## Community Sentiment

### Positive
- New memory manager eliminates freeze() complexity
- AGP KMP plugin improves build performance
- Swift Export will fix many iOS issues
- Active community support on Slack

### Negative
- Xcode 16 linker issues widespread
- CrashKiOS compatibility problems
- AGP 9 migration requires changes
- iOS debugging still challenging

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Kotlin Docs - Memory Manager](https://kotlinlang.org/docs/native-memory-manager.html) | Official | 0.95 | Memory management |
| 2 | [Kotlin Docs - expect/actual](https://kotlinlang.org/docs/multiplatform-expect-actual.html) | Official | 0.95 | Mechanism explanation |
| 3 | [KMP Compatibility Guide](https://kotlinlang.org/docs/multiplatform/multiplatform-compatibility-guide.html) | Official | 0.95 | Breaking changes |
| 4 | [Android Developers - KMP Plugin](https://developer.android.com/kotlin/multiplatform/plugin) | Official | 0.95 | AGP 9 setup |
| 5 | [Kotlin Slack](https://slack-chats.kotlinlang.org/) | Community | 0.80 | Real issues |
| 6 | [Droidcon - expect/actual](https://www.droidcon.com/2025/07/09/expect-actual-mechanism-in-kotlin-multiplatform-explained/) | Blog | 0.85 | Patterns |
| 7 | [Medium - iOS Challenges](https://medium.com/@eduardofelipi/ios-specific-integration-challenges-with-kotlin-multiplatform-75c6fa7a932e) | Blog | 0.80 | iOS pitfalls |
| 8 | [Touchlab - Crash Reporting](https://dev.to/touchlab/kotlin-native-ios-crash-reporting-3m84) | Blog | 0.85 | CrashKiOS |
| 9 | [YouTrack KT-70202](https://youtrack.jetbrains.com/issue/KT-70202) | Official | 0.90 | Xcode 16 linker |
| 10 | [Medium - App Crashes](https://medium.com/@anouarelmaaroufi/common-app-crash-issues-in-kotlin-multiplatform-using-jetpack-compose-and-how-to-fix-them-34d81db660c3) | Blog | 0.80 | Crash solutions |
