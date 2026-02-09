# Research Report: KMP Production 2025

**Date:** 2026-01-05
**Sources Evaluated:** 20+
**Research Depth:** Deep

## Executive Summary

KMP в production в 2025 — зрелая технология с proven track record. Netflix, McDonald's, Cash App, Forbes, Philips — в production с 40-80% shared code. Key challenges: iOS Swift interop через Obj-C bridge (решается SKIE, Swift Export в Kotlin 2.2.20), memory management с iOS объектами, Compose MP iOS performance. Production checklist: KDoctor verification, proper testing (30-40% UI coverage), CI/CD с code signing, monitoring с Crashlytics/Sentry.

## Key Findings

### 1. Production Readiness (2025)

**Status:** Stable, production-ready

**Backing:**
- JetBrains (core development)
- Google (Jetpack KMP libraries)
- Square/Block (Cash App, SQLDelight)

**Adoption:** 12% → 23% за 18 месяцев

### 2. Case Studies Summary

| Company | Shared Code | Use Case | Results |
|---------|-------------|----------|---------|
| Netflix | ~60% | Studio production apps | Unified logic, offline-first |
| McDonald's | ~60% | Ordering, payments | 60% fewer platform bugs |
| Cash App | ~50% | Payment processing | JS → KMP migration success |
| Forbes | 80%+ | News app | Simultaneous feature releases |
| Philips | SDK | Medical devices | Healthcare-grade reliability |
| 9GAG | Logic | Social app | 40% dev efficiency gains |

### 3. Swift Interop Challenges

**Core Problem:** Kotlin ↔ Swift через Objective-C bridge

**Specific Issues:**
1. **Result types** — `kotlin.Result` → `Any?` в Swift
2. **Suspend functions** — completion handlers, no real cancellation
3. **Flows** — incompatible с AsyncSequence
4. **Generics** — теряются в Obj-C protocols
5. **Default arguments** — не поддерживаются
6. **Swift-only APIs** — недоступны (WidgetKit, CryptoKit)

**Solutions:**
- **SKIE** — Swift wrappers, Flows → AsyncSequence
- **KMP-NativeCoroutines** — suspend → async/await
- **Swift Export (Kotlin 2.2.20)** — native Swift interop (upcoming)

### 4. Production Checklist

**Environment:**
- [ ] KDoctor verification passed
- [ ] Xcode version pinned
- [ ] Android Studio Meerkat+
- [ ] Gradle 8.x + configuration cache

**Code Quality:**
- [ ] Unit tests 80%+ coverage (business logic)
- [ ] Integration tests 60-70% (data layer)
- [ ] UI tests 30-40% (critical journeys)
- [ ] Crashlytics/Sentry integration

**CI/CD:**
- [ ] Separate JVM/iOS jobs
- [ ] ~/.konan caching
- [ ] Code signing (keystore + certificates)
- [ ] Fastlane for iOS

**iOS Specifics:**
- [ ] SKIE or KMP-NativeCoroutines
- [ ] Memory management testing (UIImage, camera)
- [ ] XCFramework size optimization

### 5. Common Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `Any?` instead of types | Inline class not supported | Custom wrapper types |
| App crash on exception | Swift doesn't catch Kotlin exceptions | Wrap in try-catch |
| Flow doesn't work | No direct Swift interop | Use SKIE |
| Large XCFramework | All architectures | Build only needed targets |
| Slow iOS builds | Cold ~/.konan | CI caching |
| Memory leaks | iOS object lifecycle | Explicit cleanup |

### 6. Monitoring & Observability

**Recommended Stack:**
- Crashlytics / Sentry for crash reporting
- Custom analytics in shared module
- Performance monitoring (startup time, memory)

**KMP-specific metrics:**
- Shared code % (target: 50-80%)
- iOS vs Android bug ratio
- Build time trends

## Community Sentiment

### Positive
- "Finally production-ready" (2025 consensus)
- Case studies convincing
- JetBrains + Google backing reassuring
- Compose MP iOS reaching stability

### Negative / Concerns
- Swift interop still painful
- iOS developer learning curve
- Compose MP iOS performance not native-level
- Build times (improving but still concern)

## Recommendations

1. **Use SKIE** for better Swift interop today
2. **Wait for Swift Export** (Kotlin 2.2.20) for new projects
3. **Start with business logic** — not UI
4. **Monitor iOS-specific metrics** — memory, performance
5. **Invest in CI/CD caching** — saves hours daily

## Sources

| # | Source | Type | Credibility |
|---|--------|------|-------------|
| 1 | [JetBrains Case Studies](https://kotlinlang.org/docs/multiplatform/use-cases-examples.html) | Official | ★★★★★ |
| 2 | [KMPShip Big Tech](https://www.kmpship.app/blog/big-companies-kotlin-multiplatform-2025) | Blog | ★★★★☆ |
| 3 | [KMP Roadmap Aug 2025](https://blog.jetbrains.com/kotlin/2025/08/kmp-roadmap-aug-2025/) | Official | ★★★★★ |
| 4 | [SKIE](https://skie.touchlab.co/) | Official | ★★★★★ |
| 5 | [iOS Interop Challenges](https://medium.com/@eduardofelipi/ios-specific-integration-challenges-with-kotlin-multiplatform-75c6fa7a932e) | Blog | ★★★★☆ |
| 6 | [Volpis Production Ready](https://volpis.com/blog/is-kotlin-multiplatform-production-ready/) | Blog | ★★★★☆ |
| 7 | [Guarana Production](https://guarana-technologies.com/blog/kotlin-multiplatform-production) | Blog | ★★★★☆ |

---

*Проверено: 2026-01-09*
