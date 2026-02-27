---
title: "KMP Production Checklist: От разработки до релиза"
created: 2026-01-04
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - production
  - checklist
  - release
  - deployment
  - type/concept
  - level/advanced
related:
  - "[[kmp-ci-cd]]"
  - "[[kmp-debugging]]"
  - "[[kmp-testing-strategies]]"
prerequisites:
  - "[[kmp-architecture-patterns]]"
  - "[[kmp-testing-strategies]]"
  - "[[kmp-ci-cd]]"
  - "[[kmp-debugging]]"
cs-foundations:
  - release-engineering
  - observability
  - quality-gates
  - production-readiness
status: published
reading_time: 21
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# KMP Production Checklist

> **TL;DR:** Полный чеклист перед релизом: архитектура (core + platform modules), тесты (unit, integration, device), CI/CD (Gradle + Actions/Fastlane), crash reporting (CrashKiOS + Crashlytics), app stores (AAB для Android API 35+, Xcode Archive + privacy manifest). Критично: dependencies зафиксированы, dSYM загружен, performance профилирован.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| KMP Architecture | Структура проекта | [[kmp-architecture-patterns]] |
| Testing | Стратегии тестирования | [[kmp-testing-strategies]] |
| CI/CD | Автоматизация | [[kmp-ci-cd]] |
| Debugging | Отладка и crash reporting | [[kmp-debugging]] |
| **CS: Release Engineering** | Production readiness gates | [[cs-release-engineering]] |

---


## Теоретические основы

### Формальное определение

> **Production Readiness** — состояние программной системы, при котором она удовлетворяет критериям качества, надёжности, наблюдаемости и безопасности, необходимым для обслуживания пользователей в промышленном окружении (Limoncelli et al., 2014, The Practice of Cloud System Administration).

### Quality Gates Model

Production readiness формализуется как последовательность **quality gates** (Humphrey, 1989, Managing the Software Process):

| Gate | Критерии | KMP-специфика |
|------|----------|---------------|
| **G1: Build** | Компилируется на всех targets | Android + iOS (arm64, simulator) |
| **G2: Test** | Тесты проходят | commonTest + platform-specific tests |
| **G3: Integration** | Компоненты работают вместе | Shared module + native apps |
| **G4: Performance** | Метрики в пределах SLA | Build time, binary size, runtime |
| **G5: Observability** | Мониторинг и crash reporting | Crashlytics + dSYM + unified logging |
| **G6: Security** | Безопасность и подпись | Code signing (iOS + Android) |
| **G7: Release** | Готовность к дистрибуции | App Store + Play Store requirements |

### Observability Theory

Термин из теории управления (Kalman, 1960): система наблюдаема, если по выходным данным можно восстановить внутреннее состояние. В контексте KMP production:

```
Observability = Logs + Metrics + Traces + Crash Reports
```

Уникальная проблема KMP: один и тот же shared-код порождает **разные observable signals** на Android (Logcat, Crashlytics) и iOS (OSLog, dSYM symbolication). Unified observability требует нормализации signals с обоих платформ.

### Release Engineering

Humble & Farley (2010), *Continuous Delivery*: каждый коммит — потенциальный релиз. Для KMP это означает:

- **Dual pipeline**: Android AAB + iOS Archive из одного коммита
- **Atomic release**: обе платформы должны быть release-ready одновременно
- **Версионирование**: shared module version ≠ app version

> **CS-фундамент:** Production readiness связана с [[kmp-ci-cd]] (автоматизация pipeline), [[kmp-debugging]] (crash reporting) и [[kmp-testing-strategies]] (quality gates). Теоретическая база — Quality Gates (Humphrey, 1989), Observability (Kalman, 1960), Continuous Delivery (Humble & Farley, 2010).

## Почему KMP в production требует особого внимания?

**Dual-Platform Complexity:** Релиз = Android (Play Store) + iOS (App Store). Разные signing, разные review processes, разные crash reporting stacks.

**Observability Gap:** Crash в shared Kotlin коде может выглядеть по-разному на Android (Crashlytics) и iOS (dSYM symbolication). Нужна unified observability.

**Swift Interop в Production:** SKIE/KMP-NativeCoroutines критичны для правильной обработки exceptions и coroutines в iOS.

---

## Production Readiness Overview

```
┌─────────────────────────────────────────────────────────────┐
│              KMP PRODUCTION READINESS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ✅ KMP Core                    Stable since Nov 2023      │
│   ✅ Kotlin 2.1.21               K2 compiler, production    │
│   ✅ Compose MP iOS              Stable since 2024          │
│   ✅ Jetpack Libraries           Room, DataStore, ViewModel │
│                                                             │
│   PROVEN IN PRODUCTION:                                     │
│   • Netflix, McDonald's, Cash App, Google Docs iOS          │
│   • 20,000+ companies using KMP                             │
│   • 60-80% shared code typical                              │
│                                                             │
│   CAVEATS:                                                  │
│   ⚠️ iOS debugging more complex than Android                │
│   ⚠️ Mac runners required for iOS CI                        │
│   ⚠️ Compose MP iOS: some perf/accessibility gaps           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Architecture Checklist

### Project Structure

```markdown
## Architecture ✓

- [ ] Single `shared` module for business logic
- [ ] Separate `androidApp` and `iosApp` platform modules
- [ ] Clear separation: shared code vs platform-specific
- [ ] Dependencies documented in libs.versions.toml
- [ ] No business logic leaking into platform modules

## Code Organization ✓

- [ ] Repository pattern for data access
- [ ] Use cases / Interactors in shared module
- [ ] ViewModels shared (or platform-specific)
- [ ] Platform UI: Compose (Android), SwiftUI (iOS)
```

```kotlin
// Правильная структура проекта
project/
├── shared/                 # ← Всё общее здесь
│   ├── commonMain/
│   │   ├── data/          # Repositories, APIs
│   │   ├── domain/        # Use cases, Models
│   │   └── presentation/  # Shared ViewModels (optional)
│   ├── androidMain/       # Platform implementations
│   └── iosMain/
├── androidApp/            # ← Только UI и DI
│   └── src/main/
└── iosApp/               # ← Только UI и DI
    └── Sources/
```

### Dependency Management

```kotlin
// libs.versions.toml — зафиксируй версии!
[versions]
kotlin = "2.1.21"           # Фиксированная версия
ktor = "3.0.3"
sqldelight = "2.0.2"
coroutines = "1.9.0"

[libraries]
ktor-client-core = { module = "io.ktor:ktor-client-core", version.ref = "ktor" }
# ...
```

```properties
# gradle.properties — lock dependencies
dependencyLocking.enabled=true
```

---

## 2. Testing Checklist

### Test Coverage

```markdown
## Unit Tests ✓

- [ ] Core business logic tested (≥80% coverage)
- [ ] Repository tests with fake data sources
- [ ] Use case tests with mocked dependencies
- [ ] ViewModel tests with Turbine for Flow

## Integration Tests ✓

- [ ] Ktor MockEngine for API tests
- [ ] SQLDelight in-memory for DB tests
- [ ] End-to-end scenarios in commonTest

## Platform Tests ✓

- [ ] Android instrumented tests
- [ ] iOS XCTest for Swift interop
- [ ] Real device testing (not just simulators)
```

```kotlin
// Минимальный тестовый setup
// commonTest/kotlin/
class UserRepositoryTest {
    private val fakeApi = FakeUserApi()
    private val repository = UserRepository(fakeApi)

    @Test
    fun `getUser returns user from API`() = runTest {
        fakeApi.setUser(User("123", "John"))

        val user = repository.getUser("123")

        assertEquals("John", user.name)
    }
}
```

### Test Automation

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]

jobs:
  test-common:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew :shared:allTests

  test-ios:
    runs-on: macos-latest
    needs: test-common  # iOS только после успеха common
    steps:
      - uses: actions/checkout@v4
      - run: ./gradlew :shared:iosSimulatorArm64Test
```

---

## 3. CI/CD Checklist

### Build Pipeline

```markdown
## CI Setup ✓

- [ ] GitHub Actions / Bitrise / Jenkins configured
- [ ] Gradle caching enabled (actions/cache)
- [ ] ~/.konan cached for Kotlin/Native
- [ ] Separate jobs: Android (ubuntu), iOS (macos)

## Release Pipeline ✓

- [ ] Debug builds on every PR
- [ ] Release builds on tags (v*)
- [ ] Code signing configured (Android keystore, iOS certs)
- [ ] Artifact upload to stores automated
```

```yaml
# Release workflow
name: Release
on:
  push:
    tags: ['v*']

jobs:
  release-android:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: gradle/actions/setup-gradle@v3

      # Keystore setup
      - name: Decode Keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > keystore.jks

      # Build
      - run: ./gradlew :androidApp:bundleRelease

      # Upload to Play Store
      - uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_SERVICE_ACCOUNT }}
          packageName: com.example.app
          releaseFiles: androidApp/build/outputs/bundle/release/*.aab
          track: internal

  release-ios:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4

      # Certificates
      - uses: apple-actions/import-codesign-certs@v2
        with:
          p12-file-base64: ${{ secrets.CERTIFICATES_P12 }}
          p12-password: ${{ secrets.CERTIFICATES_PASSWORD }}

      # Build
      - run: |
          ./gradlew :shared:linkReleaseFrameworkIosArm64
          cd iosApp && fastlane release
```

---

## 4. Crash Reporting Checklist

### Setup

```markdown
## Crash Reporting ✓

- [ ] CrashKiOS integrated for Kotlin stack traces
- [ ] Firebase Crashlytics configured (or Sentry/Bugsnag)
- [ ] dSYM upload automated in CI
- [ ] Crash alerts configured

## Logging ✓

- [ ] Kermit for structured logging
- [ ] Log levels appropriate (no debug in prod)
- [ ] Breadcrumbs for crash context
```

```kotlin
// CrashKiOS + Crashlytics setup
// shared/build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("co.touchlab.crashkios:crashlytics:0.9.1")
            implementation("co.touchlab:kermit:2.0.4")
            implementation("co.touchlab:kermit-crashlytics:2.0.4")
        }
    }
}
```

```kotlin
// Application startup
fun initCrashReporting() {
    // Hook Kotlin exceptions
    setCrashlyticsUnhandledExceptionHook()

    // Setup logging
    Logger.addLogWriter(CrashlyticsLogWriter())
}
```

### dSYM Upload (iOS)

```bash
# Xcode Build Phase: "Upload Kotlin dSYM"
# Добавь ПОСЛЕ всех других фаз

"${PODS_ROOT}/FirebaseCrashlytics/upload-symbols" \
    -gsp "${PROJECT_DIR}/GoogleService-Info.plist" \
    -p ios \
    "${BUILT_PRODUCTS_DIR}/${FRAMEWORKS_FOLDER_PATH}/Shared.framework.dSYM"
```

---

## 5. Performance Checklist

### Optimization

```markdown
## Build Performance ✓

- [ ] Gradle caching enabled
- [ ] Configuration cache enabled
- [ ] Using Debug builds for development
- [ ] ~/.konan preserved in CI

## Runtime Performance ✓

- [ ] Profiled on real devices (not just simulators)
- [ ] Memory leaks checked (Xcode Instruments, Android Profiler)
- [ ] Startup time acceptable
- [ ] No UI jank (60 FPS)

## Size Optimization ✓

- [ ] Release builds with R8/ProGuard (Android)
- [ ] embedBitcode disabled (iOS, deprecated)
- [ ] Dead code stripping enabled
- [ ] Bundle size within limits
```

```properties
# gradle.properties — performance settings
org.gradle.parallel=true
org.gradle.caching=true
org.gradle.configuration-cache=true
org.gradle.jvmargs=-Xmx6g

kotlin.incremental.native=true
```

---

## 6. Security Checklist

```markdown
## Code Security ✓

- [ ] No secrets in code (use BuildConfig / env vars)
- [ ] API keys in secure storage
- [ ] HTTPS for all network calls
- [ ] Certificate pinning (if required)

## Data Security ✓

- [ ] Sensitive data encrypted at rest
- [ ] No logging of sensitive info
- [ ] Secure preferences (EncryptedSharedPreferences / Keychain)

## App Security ✓

- [ ] ProGuard/R8 obfuscation enabled
- [ ] Root/jailbreak detection (if required)
- [ ] SSL pinning (if required)
```

```kotlin
// Secure storage example
// expect/actual for secure preferences

// commonMain
expect class SecureStorage() {
    fun save(key: String, value: String)
    fun get(key: String): String?
    fun remove(key: String)
}

// androidMain
actual class SecureStorage {
    private val prefs = EncryptedSharedPreferences.create(...)
    // ...
}

// iosMain
actual class SecureStorage {
    // Keychain wrapper
    // ...
}
```

---

## 7. App Store Checklist

### Google Play Store

```markdown
## Android Requirements (2025) ✓

- [ ] AAB format (not APK)
- [ ] Target API 35 (Android 15) — required August 2025
- [ ] 64-bit support
- [ ] Data safety form completed
- [ ] Privacy policy URL provided

## Assets ✓

- [ ] App icon: 512x512 PNG
- [ ] Feature graphic: 1024x500
- [ ] Screenshots: phone + tablet
- [ ] Short description (80 chars)
- [ ] Full description (4000 chars)
```

```kotlin
// build.gradle.kts — Android config
android {
    compileSdk = 35
    defaultConfig {
        targetSdk = 35
        minSdk = 24
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}
```

### Apple App Store

```markdown
## iOS Requirements (2025) ✓

- [ ] Privacy manifest (PrivacyInfo.xcprivacy)
- [ ] App Tracking Transparency (if tracking)
- [ ] Account deletion option (if login)
- [ ] Sign in with Apple (if 3rd party login)
- [ ] Privacy policy URL

## Assets ✓

- [ ] App icon: 1024x1024 PNG
- [ ] Screenshots: all required device sizes
- [ ] Preview videos (optional)
- [ ] Description, keywords, category
```

```swift
// PrivacyInfo.xcprivacy — пример
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN">
<plist version="1.0">
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyTrackingDomains</key>
    <array/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array/>
    <key>NSPrivacyAccessedAPITypes</key>
    <array/>
</dict>
</plist>
```

---

## 8. Pre-Launch Final Checklist

```markdown
## Week Before Launch ✓

### Code & Build
- [ ] All tests passing
- [ ] No critical bugs in issue tracker
- [ ] Release branch created and frozen
- [ ] Version bumped (versionCode, CFBundleVersion)

### Infrastructure
- [ ] Backend ready for production load
- [ ] Feature flags configured
- [ ] Analytics events verified
- [ ] Crash reporting verified (test crash)

### Stores
- [ ] Store listings complete
- [ ] Screenshots updated
- [ ] Release notes written
- [ ] Review submitted (allow 24-48h Apple, 3-7d Google)

### Team
- [ ] On-call schedule for launch day
- [ ] Rollback plan documented
- [ ] Support team briefed
```

---

## 9. Post-Launch Checklist

```markdown
## Day 1 After Launch ✓

- [ ] Monitor crash rates (target: <1%)
- [ ] Monitor ANR rates (Android, target: <0.5%)
- [ ] Check user reviews
- [ ] Verify analytics data flowing
- [ ] Check performance metrics

## Week 1 ✓

- [ ] Address critical crashes
- [ ] Respond to user reviews
- [ ] Analyze user behavior
- [ ] Plan hotfix if needed
- [ ] Retrospective with team
```

---

## Quick Reference: Critical Commands

```bash
# Build release (Android)
./gradlew :androidApp:bundleRelease

# Build release (iOS framework)
./gradlew :shared:linkReleaseFrameworkIosArm64

# Run all tests
./gradlew allTests

# Check for dependency updates
./gradlew dependencyUpdates

# Analyze bundle size
./gradlew :androidApp:bundleRelease --info
# Xcode: Product → Archive → Distribute → App Store Connect
```

---

## When NOT to Launch

```markdown
## Red Flags 🚩

❌ Crash rate > 2% in testing
❌ Critical functionality broken
❌ Security vulnerabilities unfixed
❌ Store rejection issues unresolved
❌ Backend not production-ready
❌ No crash reporting configured
❌ No rollback plan
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "KMP ещё не production-ready" | Stable с Nov 2023, Netflix/McDonald's в production |
| "Crash reporting работает из коробки" | Нужен CrashKiOS + dSYM upload для iOS |
| "Compose MP iOS = native performance" | Есть gaps в accessibility и perf |
| "Один CI job для обеих платформ" | iOS требует macOS runner (10x дороже) |
| "Tests на одной платформе достаточно" | Bugs platform-specific, тестировать обе |

## CS-фундамент

| Концепция | Применение в Production |
|-----------|------------------------|
| Quality Gates | Pre-release checklist verification |
| Observability | Crash reporting + metrics |
| Release Engineering | Dual-platform deployment |
| Feature Flags | Gradual rollout |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Guarana Production Guide](https://guarana-technologies.com/blog/kotlin-multiplatform-production) | Blog | Complete checklist |
| [Play Store Guidelines](https://developer.android.com/distribute/best-practices/launch) | Official | Android launch |
| [App Store Guidelines](https://developer.apple.com/app-store/review/guidelines/) | Official | iOS requirements |
| [CrashKiOS](https://crashkios.touchlab.co/) | Tool | Crash reporting |

---

## Связь с другими темами

- **[[kmp-ci-cd]]** — CI/CD — неотъемлемая часть production readiness. Чеклист определяет ЧТО нужно проверить, а CI/CD автоматизирует КАК это проверяется. Настройка GitHub Actions с отдельными jobs для Android (ubuntu) и iOS (macos), кэширование ~/.konan, автоматическая загрузка dSYM и деплой в App Store/Play Store — всё это детали, которые отличают production pipeline от ручной сборки. Без автоматизированного CI/CD чеклист остаётся теорией.

- **[[kmp-debugging]]** — Crash reporting — один из критичных пунктов чеклиста, и его правильная настройка требует глубокого понимания отладки в KMP. CrashKiOS для Kotlin stack traces, загрузка dSYM для символикации, Kermit для structured logging — это инструменты, детально описанные в материале по debugging. Без них production-приложение генерирует нечитаемые crash reports с адресами `konan::abort()` вместо имён файлов и строк.

- **[[kmp-testing-strategies]]** — Тестирование — фундамент quality gates в production checklist. Unit tests в commonTest с coverage не менее 80%, integration tests с Ktor MockEngine и SQLDelight in-memory, platform-specific тесты на реальных устройствах — стратегия тестирования определяет, насколько вы уверены в релизе. Материал по testing strategies детализирует подходы к тестированию shared-кода, которые чеклист лишь перечисляет.

## Источники и дальнейшее чтение

### Теоретические основы

- **Humphrey W. (1989).** *Managing the Software Process.* — Quality Gates как формальная модель production readiness.
- **Kalman R. (1960).** *A New Approach to Linear Filtering and Prediction Problems.* — Observability theory: восстановление внутреннего состояния системы по выходным данным.
- **Humble J., Farley D. (2010).** *Continuous Delivery.* — Deployment pipeline как автоматизированный quality gate.

### Практические руководства

- **Moskala M. (2021).** *Effective Kotlin.* — Kotlin-практики для production-quality кода.
- [KMP Production Guide](https://kotlinlang.org/docs/multiplatform-expect-actual.html) — Официальные best practices.

---

## Проверь себя

> [!question]- Почему crash reporting для KMP iOS требует дополнительной настройки по сравнению с Android?
> На Android Crashlytics/Sentry подключаются стандартно. На iOS Kotlin/Native crash traces содержат mangled names. Нужен CrashKiOS для demangling, DSYM-файлы для symbolication, и правильная конфигурация framework export для включения debug symbols.

> [!question]- Какие аспекты KMP-приложения нужно проверить перед первым production-релизом?
> Build: все targets компилируются, CI/CD green, signing настроен. Quality: test coverage >70%, crash rate <0.1%, performance benchmarks OK. iOS: XCFramework корректен, SKIE настроен. Security: no secrets в коде, ProGuard/R8 enabled.

> [!question]- Почему monitoring в KMP-production должен охватывать обе платформы раздельно?
> Shared-код одинаков, но runtime behavior различается: JVM GC vs Kotlin/Native GC, разные HTTP engines, разная memory availability. Баг может проявиться только на одной платформе. Нужен platform-specific monitoring с общим dashboard.

---

## Ключевые карточки

Что входит в pre-launch checklist для KMP?
?
Build (all targets, CI green, signing), Testing (coverage, crash rate, performance), Security (R8/ProGuard, no secrets), iOS (XCFramework, SKIE, DSYM), Monitoring (Crashlytics, analytics, logging), Documentation (API docs, runbook).

Как настроить monitoring для KMP в production?
?
Kermit для structured logging (platform-native: Logcat/OSLog). CrashKiOS + Crashlytics/Sentry для crash reporting. Custom analytics через expect/actual (Firebase/Mixpanel). Platform-specific dashboards + unified metrics.

Какие security-меры нужны для KMP production?
?
ProGuard/R8 для Android (obfuscation + shrinking), -Xstrip-debug-info для iOS release, secrets через BuildConfig/environment (не в коде), certificate pinning через Ktor, encrypted storage через expect/actual.

Как организовать release process для KMP?
?
Semantic versioning, CI/CD pipeline с matrix (ubuntu + macos), automated tests, Gradle publish для libraries, Fastlane для iOS App Store, Gradle Play Publisher для Google Play. One-click release.

Какие метрики отслеживать в KMP production?
?
Crash-free rate (>99.9%), cold start time, shared code % (цель 60-80%), build time trend, binary size, memory usage per platform, API response times, feature parity between platforms.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-troubleshooting]] | Решение проблем в production |
| Углубиться | [[kmp-ci-cd]] | Автоматизация release process |
| Смежная тема | [[kmp-case-studies]] | Как другие компании запускали KMP в production |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Android API 35, iOS 18, Kotlin 2.1.21*
