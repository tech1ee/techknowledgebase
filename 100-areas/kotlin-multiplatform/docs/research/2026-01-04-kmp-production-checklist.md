# Research Report: KMP Production Checklist

**Date:** 2026-01-04
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

KMP production-ready в 2025 с proven adoption (CashApp, McDonald's, Netflix). Чеклист: архитектура (single core module + platform modules), тестирование (unit + integration + device), CI/CD (Gradle + GitHub Actions/Fastlane), monitoring (CrashKiOS + Crashlytics/Sentry), app store submission (AAB для Android, Xcode Archive для iOS). Критические проверки: iOS debugging настроен, dependencies версии зафиксированы, performance profiled.

## Key Findings

1. **Architecture Checklist**
   - Single core module for business logic
   - Separate platform modules for UI
   - Clear separation shared vs platform code
   - Dependencies documented and pinned

2. **Testing Checklist**
   - Unit tests for core module
   - Platform-specific integration tests
   - Device testing (not just simulators)
   - Automated regression tests

3. **Build & CI/CD Checklist**
   - Gradle as primary build backbone
   - GitHub Actions/Bitrise/Fastlane
   - Automated release builds
   - dSYM upload for crash reporting

4. **Monitoring Checklist**
   - CrashKiOS for Kotlin stack traces
   - Firebase Crashlytics or Sentry
   - Analytics (Firebase, Amplitude)
   - Performance monitoring

5. **App Store Requirements**
   - Android: AAB format, target API 35 (August 2025)
   - iOS: privacy manifest, App Tracking Transparency
   - Both: privacy policy, data safety declarations
   - Review time: 24-48h Apple, 3-7 days Google

## Community Sentiment

### Positive
- Major companies in production (McDonald's, Netflix)
- Tooling mature enough for production
- Clear best practices established
- Google backing increases confidence

### Negative
- iOS debugging still complex
- Compose Multiplatform iOS has caveats
- Two build systems to manage
- Mac runners required for iOS CI

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Guarana Production Guide](https://guarana-technologies.com/blog/kotlin-multiplatform-production) | Blog | 0.85 | Complete checklist |
| 2 | [KMPShip CI/CD](https://www.kmpship.app/blog/ci-cd-kotlin-multiplatform-2025) | Blog | 0.85 | CI/CD practices |
| 3 | [JetBrains KMP Stable](https://blog.jetbrains.com/kotlin/2023/11/kotlin-multiplatform-stable/) | Official | 0.95 | Stability announcement |
| 4 | [App Store Guidelines](https://ripenapps.com/blog/app-submission-guidelines/) | Blog | 0.80 | Store requirements |
| 5 | [KMP Roadmap 2025](https://blog.jetbrains.com/kotlin/2025/08/kmp-roadmap-aug-2025/) | Official | 0.95 | Future direction |
