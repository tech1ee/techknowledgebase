---
title: "KMP Library Publishing"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, publishing, maven-central, spm, cocoapods]
related: [[kmp-gradle-deep-dive]], [[kmp-ci-cd]], [[kmp-third-party-libs]]
cs-foundations: [package-management, digital-signatures, semantic-versioning, artifact-distribution]
---

# KMP Library Publishing

> **TL;DR:** KMP библиотеки публикуются в Maven Central (Android/JVM) + SPM/CocoaPods (iOS). Используй vanniktech/gradle-maven-publish-plugin для Maven Central. KMMBridge от Touchlab автоматизирует XCFramework → SPM. Публикуй с одного хоста чтобы избежать дубликатов. GPG signing обязателен для Maven Central. После релиза артефакты доступны через 15-30 минут.

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Gradle publishing | Основы публикации | Gradle docs |
| KMP project structure | Что публикуем | [[kmp-project-structure]] |
| Maven/Gradle | Понимать repositories | Maven Central docs |
| GPG/PGP | Подпись артефактов | GPG docs |
| **CS: Package Management & Signatures** | Архитектура репозиториев | [[cs-package-management]] |

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| Maven Central | Главный репозиторий Java/Kotlin | App Store для библиотек |
| Artifact | Опубликованный файл (jar, klib) | Товар на полке магазина |
| POM | Описание артефакта | Этикетка товара |
| GPG Signing | Криптографическая подпись | Печать и подпись документа |
| XCFramework | Apple multi-architecture bundle | Универсальный пакет для всех Apple устройств |
| SPM | Swift Package Manager | CocoaPods нового поколения |
| Sonatype | Оператор Maven Central | Дистрибьютор |

## Почему publishing в KMP сложнее?

**Multi-Target Artifacts:** KMP библиотека = N артефактов (JVM jar, Android aar, iOS klib × architectures). Все должны быть координированы по версии и подписаны.

**Dual Ecosystem Problem:** Android/JVM потребители ожидают Maven. iOS разработчики — SPM или CocoaPods. Нужны оба канала дистрибуции.

**GPG Signing:** Maven Central требует криптографическую подпись каждого артефакта. Публичный ключ → keyservers, приватный → in-memory в CI (никогда в репозитории).

**CocoaPods → SPM:** CocoaPods в maintenance mode. KMMBridge решает: XCFramework → GitHub Releases + Package.swift генерация.

## Структура публикации KMP

```
KMP Library Publication
│
├── Maven Central (Android, JVM, JS, Native)
│   ├── library-jvm-1.0.0.jar
│   ├── library-android-1.0.0.aar
│   ├── library-iosarm64-1.0.0.klib
│   ├── library-iossimulatorarm64-1.0.0.klib
│   └── library-1.0.0 (metadata/BOM)
│
├── SPM (iOS/macOS)
│   ├── XCFramework.zip (на GitHub Releases / S3)
│   └── Package.swift (в репозитории)
│
└── CocoaPods (iOS/macOS)
    ├── XCFramework
    └── .podspec (в CocoaPods spec repo)
```

## Maven Central: vanniktech plugin

### Setup

```kotlin
// build.gradle.kts (root)
plugins {
    id("com.vanniktech.maven.publish") version "0.35.0" apply false
}

// shared/build.gradle.kts
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.vanniktech.maven.publish")
}

mavenPublishing {
    // Публикация в Maven Central
    publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL)

    // Автоматический релиз после валидации
    // publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL, automaticRelease = true)

    // GPG подпись обязательна
    signAllPublications()

    // Координаты (можно в gradle.properties)
    coordinates(
        groupId = "com.example",
        artifactId = "my-kmp-library",
        version = "1.0.0"
    )

    // POM информация
    pom {
        name.set("My KMP Library")
        description.set("A Kotlin Multiplatform library for amazing things")
        url.set("https://github.com/example/my-kmp-library")
        inceptionYear.set("2026")

        licenses {
            license {
                name.set("The Apache License, Version 2.0")
                url.set("https://www.apache.org/licenses/LICENSE-2.0.txt")
            }
        }

        developers {
            developer {
                id.set("username")
                name.set("Your Name")
                url.set("https://github.com/username")
            }
        }

        scm {
            url.set("https://github.com/example/my-kmp-library")
            connection.set("scm:git:git://github.com/example/my-kmp-library.git")
            developerConnection.set("scm:git:ssh://git@github.com/example/my-kmp-library.git")
        }
    }
}
```

### gradle.properties

```properties
# Maven Central credentials (Sonatype user token)
mavenCentralUsername=your-token-username
mavenCentralPassword=your-token-password

# GPG signing (in-memory)
signing.keyId=ABC12345
signing.password=your-gpg-password
signing.key=-----BEGIN PGP PRIVATE KEY BLOCK-----\n...\n-----END PGP PRIVATE KEY BLOCK-----

# OR use Gradle properties
# signingInMemoryKey=...
# signingInMemoryKeyId=...
# signingInMemoryKeyPassword=...

# Project coordinates
GROUP=com.example
POM_ARTIFACT_ID=my-kmp-library
VERSION_NAME=1.0.0
```

### GPG Key Setup

```bash
# 1. Сгенерировать GPG ключ
gpg --full-generate-key
# Выбрать: RSA and RSA, 4096 bits, no expiration

# 2. Показать ключи
gpg --list-secret-keys --keyid-format=long

# 3. Экспорт для CI (ASCII armored)
gpg --export-secret-keys --armor ABC12345 > private-key.asc

# 4. Для CI: одной строкой (заменить переносы на \n)
gpg --export-secret-keys --armor ABC12345 | grep -v '^----' | tr -d '\n'

# 5. Опубликовать публичный ключ на keyservers
gpg --keyserver keyserver.ubuntu.com --send-keys ABC12345
gpg --keyserver keys.openpgp.org --send-keys ABC12345
```

### Publishing Commands

```bash
# Snapshot версия (автоматически)
./gradlew publishToMavenCentral

# Release версия (требует подтверждения в Central Portal)
./gradlew publishToMavenCentral
# Затем: central.sonatype.com → Deployments → Publish

# Release с автоматическим подтверждением
./gradlew publishAndReleaseToMavenCentral

# Локальный тест
./gradlew publishToMavenLocal
```

## Multi-Module Publishing

### Convention Plugin для publishing

```kotlin
// build-logic/src/main/kotlin/publishing.convention.gradle.kts
import com.vanniktech.maven.publish.MavenPublishBaseExtension
import com.vanniktech.maven.publish.SonatypeHost

plugins {
    id("com.vanniktech.maven.publish")
}

configure<MavenPublishBaseExtension> {
    publishToMavenCentral(SonatypeHost.CENTRAL_PORTAL)
    signAllPublications()

    val versionName = findProperty("VERSION_NAME")?.toString() ?: "0.0.0-SNAPSHOT"
    val groupId = findProperty("GROUP")?.toString() ?: "com.example"

    coordinates(
        groupId = groupId,
        artifactId = project.name,  // Имя модуля как artifactId
        version = versionName
    )

    pom {
        name.set(project.name)
        description.set(project.description ?: "KMP Library module")
        url.set("https://github.com/example/my-kmp-library")
        // ... остальные поля
    }
}
```

### Использование

```kotlin
// shared/core/build.gradle.kts
plugins {
    id("kmp.library")
    id("publishing.convention")
}

description = "Core utilities for the library"

// shared/feature/build.gradle.kts
plugins {
    id("kmp.library")
    id("publishing.convention")
}

description = "Feature module"
```

## KMMBridge: iOS Distribution

### Setup

```kotlin
// shared/build.gradle.kts
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("co.touchlab.kmmbridge") version "1.2.0"
}

kotlin {
    listOf(
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { target ->
        target.binaries.framework {
            baseName = "SharedKit"
            isStatic = true
        }
    }
}

kmmbridge {
    // Где хранить XCFramework
    mavenPublishArtifacts()  // Maven (private Artifactory, GitHub Packages)
    // githubReleaseArtifacts()  // GitHub Releases (free, simple)
    // s3PublicArtifacts()  // AWS S3

    // SPM интеграция
    spm {
        iOS { v("14") }
        macOS { v("12") }
    }

    // Или CocoaPods
    // cocoapods("git@github.com:example/podspecs.git")

    // Версионирование
    githubReleaseVersions()  // Использовать GitHub releases для версий
    // manualVersions()  // Ручное указание версии
}
```

### GitHub Actions для KMMBridge

```yaml
# .github/workflows/publish-ios-framework.yml
name: Publish iOS Framework

on:
  push:
    tags:
      - 'v*'

jobs:
  publish:
    runs-on: macos-14
    timeout-minutes: 45

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
        run: ./gradlew kmmBridgePublish -PGITHUB_PUBLISH_TOKEN=${{ secrets.GITHUB_TOKEN }}
```

### Результат: Package.swift

```swift
// Package.swift (сгенерирован KMMBridge)
// swift-tools-version:5.9
import PackageDescription

let remoteKotlinUrl = "https://github.com/example/my-kmp-library/releases/download/1.0.0/SharedKit.xcframework.zip"
let remoteKotlinChecksum = "abc123def456..."

let package = Package(
    name: "SharedKit",
    platforms: [
        .iOS(.v14),
        .macOS(.v12)
    ],
    products: [
        .library(
            name: "SharedKit",
            targets: ["SharedKit"]
        )
    ],
    targets: [
        .binaryTarget(
            name: "SharedKit",
            url: remoteKotlinUrl,
            checksum: remoteKotlinChecksum
        )
    ]
)
```

### Использование в Xcode

```
1. Xcode → File → Add Package Dependencies
2. Ввести URL: https://github.com/example/my-kmp-library
3. Выбрать версию
4. import SharedKit
```

## CocoaPods Distribution

### KMMBridge с CocoaPods

```kotlin
// shared/build.gradle.kts
kmmbridge {
    mavenPublishArtifacts()
    cocoapods("git@github.com:example/podspecs.git")
    githubReleaseVersions()
}
```

### Или встроенный CocoaPods plugin

```kotlin
// shared/build.gradle.kts
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("org.jetbrains.kotlin.native.cocoapods")
}

kotlin {
    cocoapods {
        summary = "Shared Kotlin code"
        homepage = "https://github.com/example/my-kmp-library"
        version = "1.0.0"

        ios.deploymentTarget = "14.0"

        framework {
            baseName = "SharedKit"
            isStatic = true
        }

        // Локальная разработка
        // podfile = project.file("../iosApp/Podfile")

        // Публикация
        specRepos {
            url("https://github.com/example/podspecs.git")
        }
    }
}
```

### Podfile (iOS проект)

```ruby
# iosApp/Podfile
platform :ios, '14.0'

target 'iosApp' do
  use_frameworks!

  # Локальная разработка
  pod 'SharedKit', :path => '../shared'

  # Production (после публикации)
  # pod 'SharedKit', '~> 1.0.0'
end
```

## Versioning Strategies

### Semantic Versioning

```properties
# gradle.properties
VERSION_NAME=1.2.3
# MAJOR.MINOR.PATCH
# 1 - breaking changes
# 2 - new features (backward compatible)
# 3 - bug fixes
```

### Snapshot Versions

```kotlin
// build.gradle.kts
val isRelease = !version.toString().endsWith("-SNAPSHOT")

if (!isRelease) {
    // Snapshot specific config
}
```

### Git Tag Versioning

```bash
# Автоматическое версионирование из git tags
git tag v1.0.0
git push origin v1.0.0
```

```kotlin
// build.gradle.kts
val gitTag = providers.exec {
    commandLine("git", "describe", "--tags", "--abbrev=0")
}.standardOutput.asText.get().trim().removePrefix("v")

version = gitTag.ifEmpty { "0.0.1-SNAPSHOT" }
```

## CI/CD Publishing Workflow

```yaml
# .github/workflows/publish.yml
name: Publish Library

on:
  push:
    tags:
      - 'v*'

jobs:
  # ============================================
  # Maven Central
  # ============================================
  publish-maven:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - uses: gradle/actions/setup-gradle@v3

      - name: Publish to Maven Central
        env:
          ORG_GRADLE_PROJECT_mavenCentralUsername: ${{ secrets.MAVEN_CENTRAL_USERNAME }}
          ORG_GRADLE_PROJECT_mavenCentralPassword: ${{ secrets.MAVEN_CENTRAL_PASSWORD }}
          ORG_GRADLE_PROJECT_signingInMemoryKey: ${{ secrets.GPG_SIGNING_KEY }}
          ORG_GRADLE_PROJECT_signingInMemoryKeyId: ${{ secrets.GPG_KEY_ID }}
          ORG_GRADLE_PROJECT_signingInMemoryKeyPassword: ${{ secrets.GPG_PASSWORD }}
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          ./gradlew publishAndReleaseToMavenCentral -PVERSION_NAME=$VERSION

  # ============================================
  # iOS Framework (SPM)
  # ============================================
  publish-ios:
    runs-on: macos-14
    needs: publish-maven
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

      - name: Publish iOS Framework
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          VERSION=${GITHUB_REF#refs/tags/v}
          ./gradlew kmmBridgePublish -PVERSION_NAME=$VERSION
```

## Verifying Publication

### Maven Central

```bash
# Проверить наличие артефакта
curl -s "https://repo1.maven.org/maven2/com/example/my-kmp-library/1.0.0/" | head

# Проверить POM
curl -s "https://repo1.maven.org/maven2/com/example/my-kmp-library/1.0.0/my-kmp-library-1.0.0.pom"
```

### Использование в проекте

```kotlin
// build.gradle.kts (consumer)
repositories {
    mavenCentral()
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("com.example:my-kmp-library:1.0.0")
        }
    }
}
```

## Best Practices Checklist

| Practice | Why | How |
|----------|-----|-----|
| One host publishing | Avoid duplicates | Single CI job |
| GPG signing | Maven Central requires | In-memory keys in CI |
| Semantic versioning | Clear compatibility | MAJOR.MINOR.PATCH |
| Test before publish | Catch issues early | ./gradlew allTests |
| Publish to local first | Verify artifacts | ./gradlew publishToMavenLocal |
| README with usage | Documentation | Include in repo |
| Keep versions in sync | Avoid confusion | Same version for Maven + SPM |
| Automate releases | Consistency | GitHub Actions |
| Javadoc/Dokka | API documentation | Optional but recommended |

## Troubleshooting

| Проблема | Причина | Решение |
|----------|---------|---------|
| Duplicate publication | Multiple hosts | Publish from one CI job |
| GPG signature failed | Wrong key format | Use ASCII-armored, escape newlines |
| Maven Central rejected | Missing POM fields | Add all required metadata |
| SPM checksum mismatch | XCFramework rebuilt | Consistent CI builds |
| CocoaPods validation failed | Missing fields | Check podspec requirements |
| Publication timeout | Large artifacts | Increase CI timeout |

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Нужен Mac для публикации iOS" | vanniktech plugin позволяет cross-compilation на Linux |
| "CocoaPods обязателен для iOS" | SPM через KMMBridge — современный способ |
| "Maven Central сложно настроить" | С vanniktech plugin — 10 минут |
| "Snapshot версии не нужны" | Критичны для тестирования до релиза |
| "Публиковать с нескольких машин ОК" | Риск duplicate artifacts, всегда один CI job |

## CS-фундамент

| Концепция | Применение в Publishing |
|-----------|-------------------------|
| Asymmetric cryptography | GPG signing (private/public keys) |
| Content-addressable storage | Maven coordinates (group:artifact:version) |
| Semantic versioning | MAJOR.MINOR.PATCH compatibility |
| Package manifest | POM.xml, Package.swift, .podspec |

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [Vanniktech Plugin](https://vanniktech.github.io/gradle-maven-publish-plugin/) | Official | Maven Central publishing |
| [Kotlin Multiplatform Publish](https://kotlinlang.org/docs/multiplatform/multiplatform-publish-libraries.html) | Official | JetBrains guide |
| [KMMBridge](https://kmmbridge.touchlab.co/) | Official | iOS framework distribution |
| [Maven Central Portal](https://central.sonatype.com/) | Official | Deployment management |
| [Multi-module Publishing](https://itnext.io/publishing-a-multi-module-kmp-library-to-maven-central-a9a92d5bc512) | Blog | Advanced patterns |
| [Publish Without Mac](https://kdroidfilter.github.io/blog/2025/publish-kmp-library-to-maven-central) | Blog | Linux CI setup |

---
*Проверено: 2026-01-09 | vanniktech 0.35.0, KMMBridge 1.2.0*
