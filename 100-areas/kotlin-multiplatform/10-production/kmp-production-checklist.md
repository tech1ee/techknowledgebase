---
title: "KMP Production Checklist: От разработки до релиза"
created: 2026-01-04
modified: 2026-01-05
tags: [kotlin, kmp, production, checklist, release, deployment]
related:
  - "[[kmp-ci-cd]]"
  - "[[kmp-debugging]]"
  - "[[kmp-testing-strategies]]"
cs-foundations: [release-engineering, observability, quality-gates, production-readiness]
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

*Проверено: 2026-01-09 | Android API 35, iOS 18, Kotlin 2.1.21*
