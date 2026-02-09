---
title: "Research Report: KMP Android Integration"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Android Integration

**Date:** 2026-01-03
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

Android является первоклассным target в KMP с полной поддержкой Jetpack библиотек: Room 2.8+, DataStore 1.2+, ViewModel 2.10+, Paging 3.3+. Google объявил KMP "validated" после успешного эксперимента с Google Docs iOS. Новый Android-KMP Gradle plugin заменяет устаревший com.android.library. Миграция инкрементальная — можно начать с одного модуля.

## Key Findings

1. **Jetpack KMP Support (Google I/O 2025)**
   - Room 2.8.4: Android, iOS, Desktop
   - DataStore 1.2.0: Preferences DataStore на всех платформах
   - ViewModel 2.10.0: Shared ViewModels
   - Paging 3.3.6: Cross-platform paging
   - Navigation 2.9.6: Through Compose Multiplatform

2. **New Android-KMP Gradle Plugin**
   - `com.android.kotlin.multiplatform.library` — современный подход
   - Single variant architecture (no build types/flavors)
   - Faster builds (Java/tests disabled by default)
   - Integrated into `kotlin {}` DSL block

3. **Room KMP Configuration**
   - BundledSQLiteDriver для consistency
   - Suspend functions only (no sync methods)
   - Flow instead of LiveData
   - KSP per-target configuration required

4. **Migration Strategy**
   - Gradual adoption supported
   - Start with data layer
   - Replace incompatible libraries (RxJava → Coroutines, Retrofit → Ktor)
   - 60-80% code can be shared

5. **Production Results**
   - Google Docs: "KMP validated", on par or better performance
   - McDonald's: Fewer crashes, better performance
   - Netflix: 60% shared code across 12+ apps

## Community Sentiment

### Positive Feedback
- Seamless integration with existing Android codebase
- Jetpack library support removes major blocker
- Performance matches native
- Incremental migration reduces risk

### Negative Feedback / Concerns
- KSP configuration complexity for multi-target
- New plugin doesn't support product flavors
- Proto DataStore not available in KMP
- Some tooling issues in early Android Studio versions

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Android Developers KMP](https://developer.android.com/kotlin/multiplatform) | Official | 0.95 | Jetpack library matrix |
| 2 | [Google I/O 2025 Blog](https://android-developers.googleblog.com/2025/05/android-kotlin-multiplatform-google-io-kotlinconf-2025.html) | Official | 0.95 | Announcements |
| 3 | [Android-KMP Plugin](https://developer.android.com/kotlin/multiplatform/plugin) | Official | 0.95 | Gradle config |
| 4 | [Room KMP Setup](https://developer.android.com/kotlin/multiplatform/room) | Official | 0.95 | Room configuration |
| 5 | [InfoQ KMP Evaluation](https://www.infoq.com/articles/kotlin-multiplatform-evaluation/) | Expert | 0.85 | Performance analysis |
| 6 | [Touchlab KMP ViewModel](https://touchlab.co/kmp-viewmodel) | Expert | 0.90 | ViewModel guide |
| 7 | [ProAndroidDev Migration](https://proandroiddev.com/migrating-applications-to-kotlin-multiplatform-a-step-by-step-guide-47b365634924) | Blog | 0.85 | Migration steps |
| 8 | [Appmilla DataStore Guide](https://appmilla.com/latest/getting-started-with-jetpack-viewmodels-and-datastore-in-kotlin-multiplatform/) | Blog | 0.80 | Practical examples |
