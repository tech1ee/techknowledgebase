---
title: "Research Report: KMP Migration from Native"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Migration from Native

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

Миграция на KMP выполняется поэтапно: Model → Data Sources → Repository → Use Cases. Android Studio Meerkat+ имеет встроенный KMP Shared Module Template. Замены: Retrofit → Ktor, Room → SQLDelight (или Room KMP), Hilt → Koin. iOS интегрируется через XCFramework (CocoaPods/SPM/KMMBridge). Монорепо рекомендуется для тесного сотрудничества. Case studies: Netflix 50-60%, McDonald's ~60%, Quizlet 60-70% shared code.

## Key Findings

1. **Migration Strategy**
   - Start with Model layer (least dependencies)
   - Then Data Sources (Retrofit → Ktor, Room → SQLDelight)
   - Then Repository and Use Cases
   - ViewModel optional (keep native or use KMP ViewModel)
   - UI last (or keep native)

2. **Library Replacements**
   - Retrofit → Ktor Client (full compatibility)
   - Room → SQLDelight or Room KMP (stable 2025)
   - Hilt/Dagger → Koin or kotlin-inject
   - Gson → kotlinx-serialization
   - SharedPreferences → multiplatform-settings

3. **Repository Structure Options**
   - Monorepo (recommended for close collaboration)
   - Git submodules (separate repos, linked)
   - Remote distribution (Maven + SPM/CocoaPods)

4. **iOS Integration**
   - XCFramework generation via Gradle
   - CocoaPods or SPM integration
   - Swift wrappers for suspend functions
   - SKIE plugin for better interop

5. **Case Studies**
   - Netflix: 50-60% shared, unified business logic
   - McDonald's: 60% fewer platform bugs
   - Quizlet: 25% faster iOS, 8MB smaller Android
   - Duolingo: 40M DAU, weekly releases

## Community Sentiment

### Positive
- Gradual migration reduces risk
- Android Studio template simplifies setup
- Real case studies prove value
- Compose Multiplatform iOS stable (May 2025)

### Negative
- Learning curve for iOS developers
- suspend → async/await bridging complexity
- Initial setup time investment
- XCFramework size can be large

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Add KMP to existing project](https://developer.android.com/kotlin/multiplatform/migrate) | Official | 0.95 | Google guide |
| 2 | [Migrating to KMP](https://proandroiddev.com/migrating-applications-to-kotlin-multiplatform-a-step-by-step-guide-47b365634924) | Blog | 0.85 | Step-by-step |
| 3 | [Case Studies](https://kotlinlang.org/docs/multiplatform/case-studies.html) | Official | 0.95 | Real examples |
| 4 | [KMP Shared Module Template](https://android-developers.googleblog.com/2025/05/kotlin-multiplatform-shared-module-templates.html) | Official | 0.95 | Android Studio |
| 5 | [Convert Native to KMP](https://www.thedroidsonroids.com/blog/convert-native-project-to-kotlin-multiplatform-developers-guide) | Blog | 0.85 | Detailed guide |
