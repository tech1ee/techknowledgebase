---
title: "KMP CI/CD"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, ci-cd, github-actions, bitrise, fastlane]
related: [[kmp-gradle-deep-dive]], [[kmp-publishing]], [[kmp-testing-strategies]]
cs-foundations: [continuous-integration, pipeline-architecture, cost-optimization, caching-strategies]
---

# KMP CI/CD

> **TL;DR:** GitHub Actions — основной CI для KMP. iOS билды требуют macOS runner ($0.08/min vs $0.008/min Linux). Кэшируй ~/.konan и Gradle. Используй `allTests` для тестов всех платформ. Fastlane для iOS signing и App Store Connect. Отдельные jobs для Android и iOS. GitHub secrets для сертификатов и ключей. KMMBridge для XCFramework через SPM.

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| GitHub Actions basics | Понимать workflows | GitHub Actions docs |
| Gradle | KMP билд система | [[kmp-gradle-deep-dive]] |
| KMP Testing | Что тестируем | [[kmp-testing-strategies]] |
| iOS/Android signing | Подписание приложений | Platform docs |
| **CS: Pipeline Architecture** | Оптимизация CI/CD | [[cs-ci-pipelines]] |

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| Runner | Машина выполняющая CI | Курьер доставляющий посылки |
| Workflow | Набор jobs | Рецепт приготовления |
| Job | Набор steps | Этап рецепта (подготовка, готовка) |
| Artifact | Результат билда | Готовое блюдо |
| Cache | Сохраненные данные между билдами | Заготовки на кухне |
| Secret | Зашифрованные данные | Сейф с ключами |

## Почему CI/CD для KMP особенный?

**Dual-Platform Cost Problem:** iOS билды требуют macOS runner ($0.08/min) — **10x дороже** Linux ($0.008/min). Решение: запускать iOS тесты только после успешных JVM тестов (`needs: test-jvm`).

**Caching Critical Path:** Kotlin/Native compiler качает tooling в ~/.konan (~1GB). Без кэша = cold build каждый раз. С кэшем: минуты вместо 20+ минут.

**Secret Management:** iOS signing требует certificates (P12) + provisioning profiles + App Store Connect API keys. Всё хранить в GitHub Secrets, никогда в репозитории.

## GitHub Actions: Структура

```
.github/
├── workflows/
│   ├── build-and-test.yml      # PR checks
│   ├── release-android.yml     # Play Store
│   ├── release-ios.yml         # App Store
│   └── publish-library.yml     # Maven Central
└── actions/
    └── setup-kmp/              # Reusable setup
        └── action.yml
```

## Базовый Workflow: Build & Test

```yaml
# .github/workflows/build-and-test.yml
name: Build and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  # ============================================
  # JVM/Android Tests (быстрый, дешевый)
  # ============================================
  test-jvm:
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          gradle-home-cache-cleanup: true

      - name: Run JVM Tests
        run: ./gradlew jvmTest

      - name: Run Android Unit Tests
        run: ./gradlew :shared:testDebugUnitTest

      - name: Upload Test Reports
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-reports-jvm
          path: '**/build/reports/tests/'

  # ============================================
  # iOS Tests (дорогой, требует macOS)
  # ============================================
  test-ios:
    runs-on: macos-14
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Cache Kotlin/Native
        uses: actions/cache@v4
        with:
          path: ~/.konan
          key: konan-${{ runner.os }}-${{ hashFiles('gradle/libs.versions.toml') }}
          restore-keys: |
            konan-${{ runner.os }}-

      - name: Run iOS Tests
        run: ./gradlew iosSimulatorArm64Test

      - name: Upload Test Reports
        uses: actions/upload-artifact@v4
        if: failure()
        with:
          name: test-reports-ios
          path: '**/build/reports/tests/'

  # ============================================
  # All Platforms (optional, comprehensive)
  # ============================================
  test-all:
    runs-on: macos-14
    timeout-minutes: 45
    needs: [test-jvm]  # Run after JVM tests pass

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Cache Kotlin/Native
        uses: actions/cache@v4
        with:
          path: ~/.konan
          key: konan-${{ runner.os }}-${{ hashFiles('gradle/libs.versions.toml') }}

      - name: Run All Tests
        run: ./gradlew allTests

      - name: Generate Coverage Report
        run: ./gradlew koverHtmlReport

      - name: Upload Coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: build/reports/kover/html/
```

## Android Release Workflow

```yaml
# .github/workflows/release-android.yml
name: Release Android

on:
  push:
    tags:
      - 'v*-android'
      - 'v*'  # Unified release

jobs:
  release-android:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Decode Keystore
        env:
          KEYSTORE_BASE64: ${{ secrets.KEYSTORE_BASE64 }}
        run: |
          echo "$KEYSTORE_BASE64" | base64 --decode > androidApp/keystore.jks

      - name: Build Release Bundle
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: |
          ./gradlew :androidApp:bundleRelease \
            -Pandroid.injected.signing.store.file=$PWD/androidApp/keystore.jks \
            -Pandroid.injected.signing.store.password=$KEYSTORE_PASSWORD \
            -Pandroid.injected.signing.key.alias=$KEY_ALIAS \
            -Pandroid.injected.signing.key.password=$KEY_PASSWORD

      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_SERVICE_ACCOUNT_JSON }}
          packageName: com.example.app
          releaseFiles: androidApp/build/outputs/bundle/release/*.aab
          track: internal  # internal, alpha, beta, production
          status: completed
          whatsNewDirectory: distribution/whatsnew

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: android-release
          path: androidApp/build/outputs/bundle/release/*.aab
```

## iOS Release Workflow

```yaml
# .github/workflows/release-ios.yml
name: Release iOS

on:
  push:
    tags:
      - 'v*-ios'
      - 'v*'  # Unified release

jobs:
  release-ios:
    runs-on: macos-14
    timeout-minutes: 45

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Xcode
        uses: maxim-lobanov/setup-xcode@v1
        with:
          xcode-version: '16.0'

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Cache Kotlin/Native
        uses: actions/cache@v4
        with:
          path: ~/.konan
          key: konan-${{ runner.os }}-${{ hashFiles('gradle/libs.versions.toml') }}

      # ============================================
      # Code Signing Setup
      # ============================================
      - name: Import Certificates
        uses: apple-actions/import-codesign-certs@v2
        with:
          p12-file-base64: ${{ secrets.CERTIFICATES_P12 }}
          p12-password: ${{ secrets.CERTIFICATES_PASSWORD }}

      - name: Download Provisioning Profiles
        uses: apple-actions/download-provisioning-profiles@v2
        with:
          bundle-id: com.example.app
          issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
          api-key-id: ${{ secrets.APPSTORE_API_KEY_ID }}
          api-private-key: ${{ secrets.APPSTORE_API_PRIVATE_KEY }}

      # ============================================
      # Build
      # ============================================
      - name: Build Shared Framework
        run: ./gradlew :shared:assembleSharedReleaseXCFramework

      - name: Build iOS App
        run: |
          cd iosApp
          xcodebuild archive \
            -scheme "iosApp" \
            -configuration Release \
            -archivePath $PWD/build/iosApp.xcarchive \
            -destination "generic/platform=iOS" \
            CODE_SIGN_STYLE="Manual" \
            DEVELOPMENT_TEAM="${{ secrets.APPLE_TEAM_ID }}" \
            CODE_SIGN_IDENTITY="iPhone Distribution"

      - name: Export IPA
        run: |
          cd iosApp
          xcodebuild -exportArchive \
            -archivePath $PWD/build/iosApp.xcarchive \
            -exportPath $PWD/build \
            -exportOptionsPlist exportOptions.plist

      # ============================================
      # Upload to App Store Connect
      # ============================================
      - name: Upload to TestFlight
        uses: apple-actions/upload-testflight-build@v1
        with:
          app-path: iosApp/build/iosApp.ipa
          issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
          api-key-id: ${{ secrets.APPSTORE_API_KEY_ID }}
          api-private-key: ${{ secrets.APPSTORE_API_PRIVATE_KEY }}

      - name: Upload Artifact
        uses: actions/upload-artifact@v4
        with:
          name: ios-release
          path: iosApp/build/*.ipa
```

## iOS Export Options

```xml
<!-- iosApp/exportOptions.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
    <key>uploadSymbols</key>
    <true/>
    <key>compileBitcode</key>
    <false/>
</dict>
</plist>
```

## Fastlane Integration

### Fastfile

```ruby
# iosApp/fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Build and upload to TestFlight"
  lane :release do
    # Match for certificates
    match(
      type: "appstore",
      readonly: true,
      git_url: ENV["MATCH_GIT_URL"]
    )

    # Increment build number
    increment_build_number(
      build_number: ENV["BUILD_NUMBER"] || latest_testflight_build_number + 1
    )

    # Build
    build_app(
      scheme: "iosApp",
      output_directory: "./build",
      output_name: "iosApp.ipa",
      export_method: "app-store"
    )

    # Upload
    upload_to_testflight(
      skip_waiting_for_build_processing: true
    )
  end

  desc "Build for testing"
  lane :build do
    build_app(
      scheme: "iosApp",
      configuration: "Debug",
      skip_archive: true,
      destination: "generic/platform=iOS Simulator"
    )
  end
end
```

### GitHub Actions с Fastlane

```yaml
# .github/workflows/release-ios-fastlane.yml
name: Release iOS (Fastlane)

on:
  push:
    tags: ['v*-ios']

jobs:
  release:
    runs-on: macos-14
    timeout-minutes: 45

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Ruby
        uses: ruby/setup-ruby@v1
        with:
          ruby-version: '3.2'
          bundler-cache: true
          working-directory: iosApp

      - name: Setup JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Cache Kotlin/Native
        uses: actions/cache@v4
        with:
          path: ~/.konan
          key: konan-${{ runner.os }}-${{ hashFiles('gradle/libs.versions.toml') }}

      - name: Build Shared Framework
        run: ./gradlew :shared:assembleSharedReleaseXCFramework

      - name: Run Fastlane
        env:
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_URL: ${{ secrets.MATCH_GIT_URL }}
          APP_STORE_CONNECT_API_KEY_KEY_ID: ${{ secrets.APPSTORE_API_KEY_ID }}
          APP_STORE_CONNECT_API_KEY_ISSUER_ID: ${{ secrets.APPSTORE_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY_KEY: ${{ secrets.APPSTORE_API_PRIVATE_KEY }}
          BUILD_NUMBER: ${{ github.run_number }}
        run: |
          cd iosApp
          bundle exec fastlane release
```

## Reusable Action: Setup KMP

```yaml
# .github/actions/setup-kmp/action.yml
name: 'Setup KMP'
description: 'Setup JDK, Gradle, and Kotlin/Native cache'

inputs:
  java-version:
    description: 'JDK version'
    default: '17'
  gradle-cache:
    description: 'Enable Gradle cache'
    default: 'true'
  konan-cache:
    description: 'Enable Kotlin/Native cache'
    default: 'true'

runs:
  using: 'composite'
  steps:
    - name: Setup JDK
      uses: actions/setup-java@v4
      with:
        distribution: 'zulu'
        java-version: ${{ inputs.java-version }}

    - name: Setup Gradle
      if: inputs.gradle-cache == 'true'
      uses: gradle/actions/setup-gradle@v3
      with:
        gradle-home-cache-cleanup: true

    - name: Cache Kotlin/Native
      if: inputs.konan-cache == 'true'
      uses: actions/cache@v4
      with:
        path: ~/.konan
        key: konan-${{ runner.os }}-${{ hashFiles('gradle/libs.versions.toml') }}
        restore-keys: |
          konan-${{ runner.os }}-
```

### Использование

```yaml
jobs:
  build:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-kmp
      - run: ./gradlew allTests
```

## Caching Strategies

### Что кэшировать

| Что | Path | Key Pattern | Размер |
|-----|------|-------------|--------|
| Gradle dependencies | ~/.gradle/caches | gradle-${{ hashFiles('**/*.gradle*') }} | ~500MB |
| Gradle wrapper | ~/.gradle/wrapper | gradle-wrapper-${{ hashFiles('gradle/wrapper/gradle-wrapper.properties') }} | ~100MB |
| Kotlin/Native | ~/.konan | konan-${{ hashFiles('gradle/libs.versions.toml') }} | ~1GB |
| CocoaPods | ~/Library/Caches/CocoaPods | pods-${{ hashFiles('iosApp/Podfile.lock') }} | Variable |

### Оптимизация Kotlin/Native кэша

```yaml
- name: Cache Kotlin/Native (optimized)
  uses: actions/cache@v4
  with:
    path: |
      ~/.konan/cache
      ~/.konan/dependencies
      ~/.konan/kotlin-native-prebuilt-*
    key: konan-${{ runner.os }}-${{ hashFiles('gradle/libs.versions.toml', '**/build.gradle.kts') }}
    restore-keys: |
      konan-${{ runner.os }}-
```

## Стоимость CI

| Runner | Цена/min | Используй для |
|--------|----------|---------------|
| ubuntu-latest | $0.008 | JVM/Android tests, builds |
| macos-14 | $0.08 | iOS tests, builds (10x дороже!) |
| macos-14-xlarge | $0.12 | Heavy iOS builds |
| windows-latest | $0.016 | Windows desktop |

### Оптимизация затрат

```yaml
jobs:
  # Сначала быстрые дешевые проверки
  lint:
    runs-on: ubuntu-latest
    steps:
      - run: ./gradlew detekt ktlintCheck

  # JVM тесты на Linux
  test-jvm:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - run: ./gradlew jvmTest testDebugUnitTest

  # iOS только после прохождения JVM
  test-ios:
    runs-on: macos-14
    needs: test-jvm  # Не тратить деньги если JVM тесты падают
    steps:
      - run: ./gradlew iosSimulatorArm64Test
```

## Bitrise Configuration

```yaml
# bitrise.yml
format_version: "11"
default_step_lib_source: https://github.com/bitrise-io/bitrise-steplib.git

workflows:
  primary:
    steps:
      - git-clone@8: {}

      - script@1:
          title: Setup JDK
          inputs:
            - content: |-
                #!/bin/bash
                set -ex
                sdkman_init
                sdk install java 17.0.9-zulu
                sdk use java 17.0.9-zulu

      - cache-pull@2: {}

      - script@1:
          title: Run Tests
          inputs:
            - content: |-
                #!/bin/bash
                set -ex
                ./gradlew allTests

      - cache-push@2:
          inputs:
            - cache_paths: |-
                ~/.gradle/caches
                ~/.gradle/wrapper
                ~/.konan

  deploy-ios:
    steps:
      - git-clone@8: {}
      - cache-pull@2: {}

      - script@1:
          title: Build Shared Framework
          inputs:
            - content: ./gradlew :shared:assembleSharedReleaseXCFramework

      - xcode-archive@5:
          inputs:
            - project_path: iosApp/iosApp.xcodeproj
            - scheme: iosApp
            - distribution_method: app-store

      - deploy-to-itunesconnect-application-loader@1:
          inputs:
            - ipa_path: $BITRISE_IPA_PATH
```

## KMMBridge для XCFramework

```kotlin
// shared/build.gradle.kts
plugins {
    id("co.touchlab.kmmbridge") version "1.0.0"
}

kmmbridge {
    mavenPublishArtifacts()  // Publish to Maven
    spm()  // Generate SPM Package.swift

    // Or GitHub Releases
    githubReleaseArtifacts {
        repository = "user/repo"
    }
}
```

### GitHub Actions с KMMBridge

```yaml
# .github/workflows/publish-framework.yml
name: Publish XCFramework

on:
  push:
    tags: ['v*']

jobs:
  publish:
    runs-on: macos-14

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - uses: gradle/actions/setup-gradle@v3

      - name: Cache Kotlin/Native
        uses: actions/cache@v4
        with:
          path: ~/.konan
          key: konan-${{ runner.os }}-${{ hashFiles('gradle/libs.versions.toml') }}

      - name: Publish Framework
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: ./gradlew kmmBridgePublish
```

## Best Practices Checklist

| Practice | Why | How |
|----------|-----|-----|
| Separate JVM/iOS jobs | Cost optimization | needs: dependency |
| Cache ~/.konan | Faster builds | actions/cache |
| Run iOS tests after JVM | Save money on failures | needs: test-jvm |
| Use reusable actions | DRY | .github/actions/ |
| Tag-based releases | Controlled deploys | on: push: tags |
| Secrets for signing | Security | GitHub secrets |
| Fastlane for iOS | Simplified signing | Fastfile |
| Timeout limits | Prevent stuck builds | timeout-minutes |
| Concurrency groups | Cancel stale PRs | concurrency: |

## Troubleshooting

| Проблема | Причина | Решение |
|----------|---------|---------|
| iOS build timeout | Kotlin/Native cold build | Cache ~/.konan |
| Signing failed | Wrong certificates | Regenerate in Apple Developer |
| Provisioning profile | Bundle ID mismatch | Match bundle ID |
| xcodebuild exit 74 | Xcode version issue | Pin Xcode version |
| allTests not found | Wrong Gradle command | Use ./gradlew allTests |
| Cache not restoring | Key mismatch | Check hashFiles paths |

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Нужен macOS для всех тестов" | JVM/Android тесты работают на Linux |
| "iOS билды всегда долгие" | С ~/.konan cache — минуты |
| "Fastlane устарел" | До сих пор лучший инструмент для iOS signing |
| "GitHub Actions дорого для KMP" | При правильной структуре jobs — экономно |
| "CocoaPods в CI сложно" | SPM через KMMBridge проще |

## CS-фундамент

| Концепция | Применение в CI/CD |
|-----------|---------------------|
| Pipeline parallelization | Parallel jobs в GitHub Actions |
| Dependency graph | `needs:` между jobs |
| Cost optimization | Дешёвые runners для дешёвых tasks |
| Caching strategies | ~/.konan, ~/.gradle/caches |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [KMPShip CI/CD Guide](https://www.kmpship.app/blog/ci-cd-kotlin-multiplatform-2025) | Blog | Полный гайд 2025 |
| [Marco Gomiero iOS CI](https://www.marcogomiero.com/posts/2024/kmp-ci-ios/) | Blog | iOS signing детально |
| [Marco Gomiero Android CI](https://www.marcogomiero.com/posts/2024/kmp-ci-android/) | Blog | Android Play Store |
| [Bitrise KMP](https://bitrise.io/blog/post/kotlin-multiplatform-mobile-kmm-ci-cd-tips-and-tricks) | Blog | Bitrise integration |
| [KMMBridge](https://kmmbridge.touchlab.co/) | Official | XCFramework publishing |
| [GitHub Actions Pricing](https://docs.github.com/en/billing/managing-billing-for-your-products/managing-billing-for-github-actions/about-billing-for-github-actions) | Official | Cost optimization |

---
*Проверено: 2026-01-09 | GitHub Actions, Fastlane, Bitrise*
