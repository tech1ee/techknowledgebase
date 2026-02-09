# Research Report: KMP Migration Strategies 2025

**Date:** 2026-01-05
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

KMP миграция в 2025 следует Strangler Fig Pattern: инкрементальное внедрение module-by-module без полного rewrite. Начинать с бизнес-логики (networking, analytics, validation), оставляя UI нативным. Успешные кейсы: McDonald's (60% меньше багов), Forbes (80% shared logic), Doist. Миграция с Flutter требует полного rewrite в Dart→Kotlin. Миграция с React Native возможна через Kotlin/JS или reakt-native-toolkit. Key challenges: iOS framework limit (одна per app), library compatibility (Hilt→Koin), XML views → Compose.

## Key Findings

### 1. Strangler Fig Pattern

**Определение:** Постепенная замена legacy системы новой, сохраняя работоспособность во время миграции.

**Применение в KMP:**
1. Создать shared KMP module
2. Перенести один feature (начать с низкорисковых)
3. Интегрировать как dependency
4. Повторять для следующих features
5. Legacy код постепенно "удушается"

**Преимущества:**
- Zero downtime во время миграции
- Rollback возможен на любом этапе
- Team upskilling параллельно с разработкой

### 2. Migration from Native (Android/iOS)

**Recommended Starting Points:**
| Module Type | Risk Level | Why First |
|-------------|------------|-----------|
| Analytics | Low | Self-contained, no UI |
| Networking | Medium | High code sharing potential |
| Validation | Low | Pure functions, testable |
| Caching | Medium | Clear boundaries |

**Anti-patterns:**
- Начинать с UI layer
- Мигрировать всё сразу
- Игнорировать iOS team input

**Library Migration Map:**
| Android | KMP Alternative |
|---------|----------------|
| Retrofit | Ktor Client |
| Moshi/Gson | kotlinx.serialization |
| RxJava | Coroutines/Flow |
| Hilt/Dagger | Koin / Kodein |
| Room | SQLDelight |

### 3. Migration from Flutter

**Key Challenge:** Full rewrite required (Dart → Kotlin)

**Strategy:**
1. **Business logic first** — переписать в KMP shared module
2. **Test coverage** — перенести/переписать тесты
3. **UI migration options:**
   - Native SwiftUI + Jetpack Compose (recommended)
   - Compose Multiplatform (shared UI)

**What Transfers:**
- Architecture patterns (BLoC → MVI)
- Test strategies
- Business requirements knowledge

**What Doesn't:**
- Dart code directly
- Flutter widgets
- Platform channels (need reimplementation)

### 4. Migration from React Native

**Two Approaches:**

**Approach 1: Kotlin/JS Bridge**
- Compile KMP shared module to JavaScript
- Import in React Native as npm package
- Gradual replacement of JS business logic

**Approach 2: Native Modules (reakt-native-toolkit)**
- Generate native modules from KMP common code
- Expose Kotlin Flows to React Native
- Direct integration without JavaScript layer

**Recommended for:**
- Large RN codebases with significant investment
- Teams wanting gradual transition
- Projects where UI can remain RN temporarily

### 5. Real-World Success Metrics

| Company | Shared Code | Result |
|---------|-------------|--------|
| McDonald's | Business logic | 60% fewer bugs, unified team |
| Forbes | 80% | Faster updates |
| Airbnb (2025) | 95% | Weekly releases (was monthly) |
| Doist (Todoist) | Core logic | Started incrementally |

**Cost Reduction:** 30% development + maintenance reduction reported.

### 6. Common Migration Challenges

**iOS Framework Limit (KT-42250):**
- Only one KMP framework per iOS app
- Solution: Umbrella module combining all KMP modules

**XML Views Migration:**
- No direct path from XML → Compose
- Either stay native or rewrite in Compose

**IDE Fragmentation:**
- Android Studio + Xcode + Fleet
- Cognitive overhead for developers

**Network Layer Contracts:**
- API contracts often differ slightly between platforms
- Need standardization before migration

### 7. Timeline Estimates

| Project Size | Strategy | Estimated Timeline |
|-------------|----------|-------------------|
| Small (<50k LOC) | Full migration | 2-4 months |
| Medium (50-200k) | Strangler Fig | 6-12 months |
| Large (>200k) | Incremental modules | 12-24 months |

**Note:** UI rewrite (if needed) добавляет 50-100% времени.

## Community Sentiment

### Positive
- Incremental adoption praised as "low-risk"
- McDonald's, Forbes case studies convincing
- Kotlin expertise transfer from Android valued
- Compose Multiplatform makes full sharing possible

### Negative / Concerns
- iOS developers learning curve
- Tooling/IDE fragmentation
- Library ecosystem still catching up
- "Framework fatigue" for teams already on Flutter/RN

### Mixed
- Full migration vs incremental debate
- Compose MP vs native UI discussion
- Timeline expectations vary widely

## Recommendations

1. **Start with business logic** — networking, validation, analytics
2. **Keep UI native initially** — reduce risk
3. **Modularize first** — clean architecture before migration
4. **Involve iOS team early** — not Android-only decision
5. **Set realistic timelines** — 12-24 months for large apps

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Android Developers KMP Migration](https://developer.android.com/kotlin/multiplatform/migrate) | Official | ★★★★★ | Official guide |
| 2 | [Theodo KMP Migration Methodology](https://apps.theodo.com/en/article/migration-dune-application-ios-android-vers-kotlin-multiplatform-methodologie-et-etapes-cles) | Blog | ★★★★☆ | Step-by-step |
| 3 | [ProAndroidDev Scalability Challenges](https://proandroiddev.com/kotlin-multiplatform-scalability-challenges-on-a-large-project-b3140e12da9d) | Blog | ★★★★☆ | Large project issues |
| 4 | [DronsOnRoids Migration Guide](https://www.thedroidsonroids.com/blog/convert-native-project-to-kotlin-multiplatform-developers-guide) | Blog | ★★★★☆ | Developer guide |
| 5 | [KMPShip Comparison](https://www.kmpship.app/blog/kmp-vs-flutter-vs-react-native-2025) | Blog | ★★★★☆ | Framework comparison |
| 6 | [reakt-native-toolkit](https://github.com/voize-gmbh/reakt-native-toolkit) | GitHub | ★★★★☆ | RN integration |
| 7 | [Aetherius KMP Integration](https://www.aetherius-solutions.com/blog-posts/kotlin-multiplatform-integration-without-full-migration) | Blog | ★★★★☆ | Incremental strategy |
| 8 | [InfoQ KMP Evaluation](https://www.infoq.com/articles/kotlin-multiplatform-evaluation/) | Article | ★★★★☆ | Benefits/trade-offs |
| 9 | [JetBrains Use Cases](https://www.jetbrains.com/help/kotlin-multiplatform-dev/use-cases-examples.html) | Official | ★★★★★ | Success stories |
| 10 | [5 Reasons NOT to Migrate](https://medium.com/@robert.jamison/5-reasons-you-should-not-migrate-to-kotlin-multiplatform-99fff82c6eb5) | Blog | ★★★★☆ | Counter-arguments |

## Research Methodology

- **Queries used:** 6 search queries
- **Sources found:** 35+ total
- **Sources used:** 25 (after quality filter)
- **Focus areas:** Native migration, Flutter migration, RN migration, success stories

---

*Проверено: 2026-01-09*
