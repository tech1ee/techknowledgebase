# Research Report: KMP Build/Deploy 2025

**Date:** 2026-01-05
**Sources Evaluated:** 30+
**Research Depth:** Deep

## Executive Summary

KMP Build/Deploy в 2025 достиг зрелости с чётким стеком: Gradle Kotlin DSL + Version Catalog (libs.versions.toml) + Convention Plugins в build-logic/. Новый `com.android.kotlin.multiplatform.library` plugin (AGP 8.10+) заменит `com.android.library` в AGP 10.0 (H2 2026). Kotlin/Native оптимизация критична: linkDebug* вместо build, кэширование ~/.konan. Publishing: Maven Central через maven-publish + vanniktech plugin, iOS через KMMBridge/XCFramework + SPM (CocoaPods в maintenance mode), npm через kt-npm-publish. CI/CD: GitHub Actions с раздельными jobs для JVM (ubuntu) и iOS (macos, 10x дороже).

## Key Findings

### 1. Gradle Optimization Properties

**Критические настройки gradle.properties:**
```properties
org.gradle.parallel=true          # Parallel task execution
org.gradle.caching=true           # Local build cache
org.gradle.configuration-cache=true # Skip config phase
org.gradle.jvmargs=-Xmx4g         # Increase heap
kotlin.incremental.native=true    # Experimental Native incremental
```

**Configuration Cache Benefits:**
- Caches configuration phase results
- Enables parallel task execution даже в одном subproject
- Caches dependency resolution

### 2. Version Catalog (libs.versions.toml)

**Structure:**
```toml
[versions]
kotlin = "2.3.0"
ktor = "3.1.0"

[libraries]
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "kotlin" }

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }

[bundles]
ktor-common = ["ktor-client-core", "ktor-client-content-negotiation"]
```

**Type-safe access:** `libs.kotlinx.coroutines.core`, `libs.bundles.ktor.common`

### 3. Convention Plugins

**build-logic/ vs buildSrc:**

| Aspect | buildSrc | build-logic |
|--------|----------|-------------|
| Setup | Automatic | Requires settings.gradle |
| Cache invalidation | Fixed in Gradle 8+ | Never had issue |
| Flexibility | Single directory | Multiple modules |

**Рекомендация:** build-logic/ как composite build для больших проектов.

### 4. Kotlin/Native Optimization

**linkDebug* vs build:**
- `linkDebug*` — **10x быстрее** чем release
- Release применяет heavy optimizations
- Для dev workflow всегда Debug

**Кэширование:**
```yaml
# CI/CD cache
- uses: actions/cache@v4
  with:
    path: ~/.konan
    key: konan-${{ runner.os }}-${{ hashFiles('**/*.kts') }}
```

**Incremental compilation:**
- `kotlin.incremental.native=true` — Experimental
- Linking task (~18 min) НЕ поддерживает incremental

### 5. New Android-KMP Plugin

**Plugin:** `com.android.kotlin.multiplatform.library`

**Requirements:**
- AGP 8.10.0+
- KGP 2.0.0+

**Migration timeline:**
- AGP 9.0 (Q4 2025): deprecated APIs require opt-in
- AGP 10.0 (H2 2026): old APIs removed

**Benefits:**
- Single variant architecture (no build types/flavors)
- Cleaner source set names
- Configuration inside `kotlin {}` block

**Known issues:**
- KSP not yet supported
- Some third-party plugins incompatible

### 6. Maven Central Publishing

**Recommended setup:**
```kotlin
plugins {
    id("maven-publish")
    id("signing")
}

publishing {
    publications {
        withType<MavenPublication> {
            pom {
                name.set("Library Name")
                description.set("Description")
                url.set("https://github.com/...")
            }
        }
    }
}
```

**Prerequisites:**
- Sonatype account with validated namespace
- GPG key for signing
- io.github.<username> namespace via GitHub verification

**Vanniktech plugin** — упрощает publishing без Mac для iOS targets.

### 7. iOS Distribution: SPM vs CocoaPods

**CocoaPods status:** Maintenance mode (no new features)

**KMMBridge (Touchlab):**
- XCFramework zip archives
- Publishing to GitHub Releases, Maven, S3
- SPM Package.swift generation

**spmForKmp Gradle Plugin:**
- Alternative to "dying CocoaPods Plugin"
- Uses embedded Swift Package Manager
- Less intrusive than CocoaPods

**Official JetBrains approach:**
- Separate Git repo for Package.swift
- Store XCFramework separately from code

### 8. npm Publishing

**kt-npm-publish plugin:**
```kotlin
npmPublishing {
    token.set("<NPM token>")
}

// Task: :npmPublish
```

**Challenges:**
- Module naming (uppercase not allowed on npm)
- kotlinx-serialization compatibility issues

### 9. CI/CD: GitHub Actions

**Cost optimization:**
- ubuntu-latest: $0.008/min
- macos-latest: $0.08/min (10x!)

**Recommended structure:**
```yaml
jobs:
  build-jvm:
    runs-on: ubuntu-latest
    # All JVM/Android tests

  build-ios:
    needs: build-jvm  # Run only if JVM passes
    runs-on: macos-latest
    # iOS tests
```

**Caching:**
```yaml
- uses: gradle/actions/setup-gradle@v4
- uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.konan
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.kts') }}
```

### 10. Build Time Optimization Summary

**From 20 min to <2 min:**
1. Use linkDebug* instead of assembleRelease
2. Cache ~/.konan in CI
3. Enable Configuration Cache
4. Use KSP instead of KAPT (2x faster)
5. Build only needed architectures
6. Don't disable Gradle Daemon
7. Avoid transitiveExport = true
8. Apply plugins only where needed

## Community Sentiment

### Positive
- Version Catalog simplifies dependency management
- Convention Plugins reduce multi-module boilerplate
- Configuration cache significantly speeds up builds
- KMMBridge solves XCFramework distribution
- New Android-KMP plugin is cleaner

### Negative / Concerns
- Configuration cache not compatible with all plugins
- Kotlin/Native builds still slow compared to JVM
- Convention plugins learning curve
- macOS runners expensive (10x Linux)
- KSP not supporting new Android-KMP plugin yet
- iOS signing complexity in CI
- Gradle sync painful in multiplatform

### Mixed
- buildSrc vs build-logic preference varies
- CocoaPods dying but impact unclear
- Migration timeline to new AGP plugin concerning

## Recommendations

1. **Gradle setup:** Version Catalog + Convention Plugins in build-logic/
2. **Native builds:** Always linkDebug* for development
3. **CI caching:** ~/.konan + ~/.gradle/caches
4. **iOS distribution:** KMMBridge + SPM (not CocoaPods)
5. **Publishing:** maven-publish + signing, vanniktech for simplification
6. **Migration:** Start preparing for Android-KMP plugin now

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Gradle Best Practices](https://kotlinlang.org/docs/gradle-best-practices.html) | Official | ★★★★★ | Optimization tips |
| 2 | [Native Compilation Time](https://kotlinlang.org/docs/native-improving-compilation-time.html) | Official | ★★★★★ | Native optimization |
| 3 | [Android-KMP Plugin](https://developer.android.com/kotlin/multiplatform/plugin) | Official | ★★★★★ | New plugin migration |
| 4 | [KMMBridge](https://kmmbridge.touchlab.co/) | Official | ★★★★★ | XCFramework distribution |
| 5 | [Maven Central Publishing](https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-publish-libraries.html) | Official | ★★★★★ | Publishing tutorial |
| 6 | [SPM Export Setup](https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-spm-export.html) | Official | ★★★★★ | SPM integration |
| 7 | [Multi-module Publishing](https://itnext.io/publishing-a-multi-module-kmp-library-to-maven-central-a9a92d5bc512) | Blog | ★★★★☆ | Multi-module guide |
| 8 | [KMP Without Mac](https://kdroidfilter.github.io/blog/2025/publish-kmp-library-to-maven-central) | Blog | ★★★★☆ | vanniktech approach |
| 9 | [spmForKmp](https://spmforkmp.eu/) | Official | ★★★★☆ | SPM plugin |
| 10 | [kt-npm-publish](https://github.com/gciatto/kt-npm-publish) | GitHub | ★★★★☆ | npm publishing |
| 11 | [Build Time Optimization](https://www.zacsweers.dev/optimizing-your-kotlin-build/) | Blog | ★★★★☆ | Comprehensive guide |
| 12 | [Convention Plugins KMP](https://proandroiddev.com/effortless-multimodule-configuration-for-kotlin-multiplatform-projects-with-gradle-convention-8e6593dff1d9) | Blog | ★★★★☆ | Multi-module setup |
| 13 | [Touchlab Build Optimization](https://touchlab.co/optimizing-gradle-builds-in-Multi-module-projects) | Blog | ★★★★☆ | Multi-module builds |
| 14 | [20 min to Fast Builds](https://medium.com/@houssembababendermel/how-i-fixed-my-kmp-ios-build-from-20-minute-builds-to-lightning-fast-c4f0f5c102b0) | Blog | ★★★★☆ | Practical optimization |
| 15 | [KMP Developer Survey 2024](https://www.snappmobile.io/kmp) | Survey | ★★★★☆ | Community challenges |

## Research Methodology

- **Queries used:** 10 search queries
- **Sources found:** 40+ total
- **Sources used:** 30 (after quality filter)
- **Combined with existing research:** 2026-01-03-kmp-gradle-deep-dive.md, 2026-01-03-kmp-ci-cd.md

---

*Проверено: 2026-01-09*
