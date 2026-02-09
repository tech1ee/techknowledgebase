---
title: "Research Report: KMP Migration from Flutter"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Migration from Flutter

**Date:** 2026-01-03
**Sources Evaluated:** 12+
**Research Depth:** Deep

## Executive Summary

Flutter → KMP миграция требует полную перезапись: Dart → Kotlin (shared logic) + нативный UI (SwiftUI/Compose) или Compose Multiplatform. Причины миграции: нативный UI/UX, интеграция с Kotlin/Swift кодбазами, модульное внедрение, производительность. Flutter лучше для MVP и единого UI. KMP лучше для нативного опыта и существующих команд. Netflix, VMware, Philips успешно используют KMP.

## Key Findings

1. **Architectural Differences**
   - Flutter: Dart for UI + logic, Skia rendering
   - KMP: Kotlin shared logic + native UI (or Compose MP)
   - Migration requires rewriting both layers

2. **Migration Path**
   - Models (freezed → data class)
   - Networking (Dio → Ktor)
   - Database (sqflite → SQLDelight)
   - State (BLoC → ViewModel + StateFlow)
   - UI (Widgets → Compose/SwiftUI or Compose MP)

3. **When to Migrate**
   - Need native UI/UX
   - Existing Kotlin/Swift codebase
   - Platform API deep integration
   - Team knows Kotlin/Swift

4. **When NOT to Migrate**
   - Need identical UI everywhere
   - Building MVP quickly
   - Small team, Dart expertise
   - Working Flutter app

5. **Timeline Estimates**
   - Small (5-10 screens): 2-3 months
   - Medium (10-30 screens): 4-6 months
   - Large (30+ screens): 6-12 months

## Community Sentiment

### Positive
- Native performance without bridges
- Modular integration possible
- Growing KMP ecosystem
- Compose MP as alternative for shared UI

### Negative
- Complete rewrite required
- Longer migration time
- Need Kotlin AND Swift/SwiftUI expertise
- Flutter more mature for UI

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Flutter vs KMP 2025](https://www.instabug.com/blog/flutter-vs-kotlin-mutliplatform-guide) | Blog | 0.85 | Comparison |
| 2 | [Migration Journey](https://medium.com/@tsortanidis.ch/from-flutter-to-kotlin-multiplatform-a-flutter-developers-migration-journey-864d1fac0be6) | Blog | 0.80 | Experience |
| 3 | [KMP vs Flutter official](https://kotlinlang.org/docs/multiplatform/kotlin-multiplatform-flutter.html) | Official | 0.95 | JetBrains |
| 4 | [Full Comparison](https://guarana-technologies.com/blog/flutter-vs-kotlin-multiplatform-2025) | Blog | 0.85 | Analysis |
