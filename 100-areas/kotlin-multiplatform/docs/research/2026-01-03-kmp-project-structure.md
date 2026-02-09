# Research Report: KMP Project Structure 2025/2026

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

KMP проект состоит из targets (целевых платформ), source sets (наборов исходников) и Gradle конфигурации. Default hierarchy template автоматически создаёт intermediate source sets. Для multi-module проектов рекомендуется использовать Gradle Convention Plugins. Android Gradle Plugin 9.0+ требует новый `com.android.kotlin.multiplatform.library` плагин. Для iOS используется umbrella module pattern.

## Key Findings

### 1. Core Project Structure
- **targets** — целевые платформы (jvm, android, ios, js, native)
- **source sets** — папки с кодом для конкретных платформ (commonMain, iosMain, jvmMain)
- **intermediate source sets** — shared между subset'ом платформ (appleMain для всех iOS/macOS)

### 2. Default Hierarchy Template
- Автоматически создаёт нужные source sets на основе declared targets
- Type-safe accessors для всех source sets
- Неиспользуемые templates игнорируются

### 3. Multi-Module Best Practices
- Convention Plugins для централизации конфигурации
- Umbrella module pattern для iOS
- Модуляризация по feature или layer

### 4. Gradle Configuration (2025)
- Kotlin Multiplatform plugin 2.1.21 (текущая)
- Требуется Gradle 7.6.3+ (max supported 9.0.0)
- Kotlin DSL вместо Groovy
- Version catalogs (libs.versions.toml)

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [KMP Project Structure Basics](https://kotlinlang.org/docs/multiplatform/multiplatform-discover-project.html) | Official Doc | 0.95 | Core concepts |
| 2 | [Hierarchical Structure](https://kotlinlang.org/docs/multiplatform/multiplatform-hierarchy.html) | Official Doc | 0.95 | Hierarchy template |
| 3 | [Gradle Best Practices](https://kotlinlang.org/docs/gradle-best-practices.html) | Official Doc | 0.95 | Build configuration |
| 4 | [Touchlab - Multi-module Optimization](https://touchlab.co/optimizing-gradle-builds-in-Multi-module-projects) | Expert Blog | 0.85 | Performance tips |
| 5 | [Android KMP Plugin](https://developer.android.com/kotlin/multiplatform/plugin) | Official Doc | 0.95 | New Android plugin |
| 6 | [KMP Architecture Best Practices](https://carrion.dev/en/posts/kmp-architecture/) | Blog | 0.80 | Architecture patterns |
| 7 | [Google - KMP Shared Module Template](https://android-developers.googleblog.com/2025/05/kotlin-multiplatform-shared-module-templates.html) | Official Blog | 0.90 | Template usage |
