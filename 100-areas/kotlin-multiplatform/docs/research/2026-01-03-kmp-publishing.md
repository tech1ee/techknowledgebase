---
title: "Research Report: KMP Library Publishing"
type: concept
status: published
tags:
  - topic/kmp
  - type/concept
  - level/intermediate
---

# Research Report: KMP Library Publishing

**Date:** 2026-01-03
**Sources Evaluated:** 15+
**Research Depth:** Deep

## Executive Summary

KMP библиотеки публикуются в Maven Central (Android/JVM/Native) + SPM/CocoaPods (iOS). vanniktech/gradle-maven-publish-plugin — стандарт для Maven Central с GPG signing. KMMBridge от Touchlab автоматизирует XCFramework → SPM с поддержкой GitHub Releases, Maven, S3. Публикация с одного хоста обязательна для избежания дубликатов. После релиза артефакты доступны через 15-30 минут.

## Key Findings

1. **Maven Central Publishing**
   - vanniktech/gradle-maven-publish-plugin 0.35.0
   - GPG signing обязательна
   - Token-based auth (не login credentials)
   - publishAndReleaseToMavenCentral для auto-release
   - Central Portal UI для ручного подтверждения

2. **KMMBridge for iOS**
   - XCFramework publishing to GitHub Releases, Maven, S3
   - SPM Package.swift auto-generation
   - CocoaPods podspec support
   - Version management via GitHub releases
   - Local development with spmDevBuild

3. **Multi-Module Strategy**
   - Convention plugin для общих настроек
   - Один хост для всех публикаций
   - Placeholder Javadoc JAR если нет docs
   - In-memory GPG keys в CI

4. **Versioning**
   - Semantic versioning (MAJOR.MINOR.PATCH)
   - Git tag based automation
   - -SNAPSHOT для development
   - Sync versions между Maven и SPM

5. **GPG Signing**
   - ASCII-armored export
   - Escape newlines для CI
   - Publish to keyservers
   - In-memory keys preferred

## Community Sentiment

### Positive
- vanniktech plugin simplifies Maven Central
- KMMBridge automates iOS complexity
- Central Portal better than old Nexus
- Good documentation available

### Negative
- GPG setup still confusing
- Maven Central validation strict
- Multi-module setup complex
- SPM requires macOS runner

## Sources

| # | Source | Type | Credibility | Key Contribution |
|---|--------|------|-------------|------------------|
| 1 | [Vanniktech Plugin](https://vanniktech.github.io/gradle-maven-publish-plugin/) | Official | 0.95 | Maven Central |
| 2 | [KMMBridge](https://kmmbridge.touchlab.co/) | Official | 0.90 | iOS distribution |
| 3 | [Kotlin Publish Guide](https://kotlinlang.org/docs/multiplatform/multiplatform-publish-libraries.html) | Official | 0.95 | JetBrains guide |
| 4 | [Multi-module KMP](https://itnext.io/publishing-a-multi-module-kmp-library-to-maven-central-a9a92d5bc512) | Blog | 0.85 | Patterns |
| 5 | [Publish Without Mac](https://kdroidfilter.github.io/blog/2025/publish-kmp-library-to-maven-central) | Blog | 0.85 | Linux workflow |
