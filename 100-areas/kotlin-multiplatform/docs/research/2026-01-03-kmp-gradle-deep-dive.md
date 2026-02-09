---
title: "Research Report: KMP Gradle Deep Dive"
type: deep-dive
status: published
tags:
  - topic/kmp
  - type/deep-dive
  - level/advanced
---

# Research Report: KMP Gradle Deep Dive

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

KMP Gradle оптимизация критична для productivity. Ключевые настройки: `org.gradle.caching=true`, `org.gradle.parallel=true`, `org.gradle.configuration-cache=true`. Version Catalog (libs.versions.toml) централизует зависимости. Convention Plugins в build-logic/ уменьшают дублирование. Kotlin/Native: используй linkDebug* вместо build, сохраняй ~/.konan между билдами. Новый `com.android.kotlin.multiplatform.library` plugin (AGP 8.8+) заменит `com.android.library` в AGP 10.0 (2026). KSP 2x быстрее KAPT.

## Key Findings

1. **Build Optimization Properties**
   - org.gradle.parallel=true — parallel task execution
   - org.gradle.caching=true — local build cache
   - org.gradle.configuration-cache=true — skip config phase
   - org.gradle.jvmargs=-Xmx4g — increase heap

2. **Version Catalog (libs.versions.toml)**
   - Centralized dependency management
   - [versions], [libraries], [plugins], [bundles] sections
   - Type-safe access: libs.kotlinx.coroutines.core
   - Bundles for grouping: libs.bundles.ktor.common

3. **Convention Plugins**
   - build-logic/ composite build preferred over buildSrc
   - Precompiled script plugins: *.gradle.kts in src/main/kotlin
   - Access to version catalog via VersionCatalogsExtension
   - Reduces boilerplate in multi-module projects

4. **Kotlin/Native Optimization**
   - linkDebug* tasks instead of build (10x faster)
   - Cache ~/.konan between CI builds
   - kotlin.incremental.native=true (Experimental)
   - kotlin.native.cacheKind=static

5. **New Android-KMP Plugin**
   - com.android.kotlin.multiplatform.library
   - Configuration inside kotlin {} block
   - No build variants complexity
   - Required migration before AGP 10.0 (H2 2026)

6. **KSP over KAPT**
   - 2x faster annotation processing
   - Native Kotlin support
   - No Java stubs generation
   - Multi-platform support

## Community Sentiment

### Positive
- Version Catalog simplifies dependency management
- Convention Plugins reduce multi-module boilerplate
- Configuration cache significantly speeds up builds
- New Android-KMP plugin is cleaner

### Negative
- Configuration cache not compatible with all plugins
- Kotlin/Native builds still slow compared to JVM
- Convention plugins learning curve
- ~/.konan cache can be large

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Gradle Best Practices](https://kotlinlang.org/docs/gradle-best-practices.html) | Official | 0.95 | Optimization tips |
| 2 | [Native Compilation Time](https://kotlinlang.org/docs/native-improving-compilation-time.html) | Official | 0.95 | Native optimization |
| 3 | [Android-KMP Plugin](https://developer.android.com/kotlin/multiplatform/plugin) | Official | 0.95 | New plugin |
| 4 | [Convention Plugins](https://docs.gradle.org/current/userguide/implementing_gradle_plugins_convention.html) | Official | 0.95 | Gradle plugins |
| 5 | [KMP Roadmap Aug 2025](https://blog.jetbrains.com/kotlin/2025/08/kmp-roadmap-aug-2025/) | Official | 0.95 | Future plans |
| 6 | [Multi-module KMP](https://proandroiddev.com/effortless-multimodule-configuration-for-kotlin-multiplatform-projects-with-gradle-convention-8e6593dff1d9) | Blog | 0.85 | Practical guide |
