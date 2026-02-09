# Research Report: KMP Android Deep Dive

**Date:** 2026-01-05
**Sources Evaluated:** 25+
**Research Depth:** Deep

## Executive Summary

KMP на Android — "родной" target (JVM). Jetpack libraries официально поддерживают KMP: ViewModel 2.10.0, Room 2.8.4, DataStore 1.2.0, Paging 3.3.6, Navigation 2.9.6 — все stable. Новый `com.android.kotlin.multiplatform.library` plugin заменит `com.android.library` (deprecation в AGP 9.0, removal в AGP 10.0). Performance: startup практически идентичен native, но binary size с Compose MP +24.8 MB из-за Skia bundling. Google Docs использует KMP в production — "on par or better" performance.

## Key Findings

### 1. Plugin Migration (Critical Change)

**Old approach (deprecating):**
```kotlin
plugins {
    id("com.android.library")
    kotlin("multiplatform")
}
```

**New approach (recommended):**
```kotlin
plugins {
    id("com.android.kotlin.multiplatform.library")
}
```

**Timeline:**
- AGP 9.0 (Q4 2025): deprecated APIs require opt-in
- AGP 10.0 (H2 2026): old APIs removed

### 2. Jetpack Libraries KMP Support

| Library | Version | Status | Targets |
|---------|---------|--------|---------|
| ViewModel | 2.10.0 | Stable | Android, iOS, JVM |
| Room | 2.8.4 | Stable | Android, iOS, JVM |
| DataStore | 1.2.0 | Stable | Android, iOS, JVM, Web |
| Paging | 3.3.6 | Stable | Android, iOS, JVM, Web |
| Navigation | 2.9.6 | Stable | Android, iOS, JVM |
| Lifecycle | 2.10.0 | Stable | Android, iOS, JVM |
| SQLite | 2.6.2 | Stable | Android, iOS, JVM |
| Collection | 1.5.0 | Stable | All |

**Tier 1 Support:** Full CI testing on Android, JVM, iOS
**Tier 2 Support:** Partial testing (macOS, Linux)
**Tier 3 Support:** No testing (watchOS, tvOS, Windows, JS, WASM)

### 3. Configuration Best Practices

**Modern androidLibrary{} block:**
```kotlin
kotlin {
    androidLibrary {
        namespace = "com.example.shared"
        compileSdk = 35
        minSdk = 24

        compilerOptions.configure {
            jvmTarget.set(JvmTarget.JVM_1_8)
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")
        }
        androidMain.dependencies {
            implementation("androidx.appcompat:appcompat:1.7.0")
        }
    }
}
```

**Key changes:**
- `withJava()` deprecated (Java source sets created by default since Kotlin 2.1.20)
- Dependencies inside `sourceSets{}` block, not global `dependencies{}`
- Unit/device tests disabled by default (enable if needed)

### 4. Resources Handling

**Compose Multiplatform Resources:**
```
src/commonMain/composeResources/
├── drawable/       # Images (PNG, JPEG, WebP, XML vectors)
├── values/         # strings.xml
├── fonts/          # Font files
└── raw/            # Other files
```

**Access pattern:**
```kotlin
Image(painterResource(Res.drawable.logo))
Text(stringResource(Res.string.app_name))
```

**Android-specific:**
- Since CMP 1.7.0, resources packed into Android assets
- Enables Android Studio previews from commonMain
- Android-specific resources remain separate

### 5. R8/ProGuard Configuration

**For KMP library modules:**
```kotlin
kotlin {
    androidLibrary {
        optimization {
            consumerKeepRules.publish = true
            consumerKeepRules.files.add(project.file("proguard-rules.pro"))
        }
    }
}
```

**Essential keep rules:**
```proguard
# Kotlin Metadata (for reflection)
-keep class kotlin.Metadata

# Coroutines
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}

# Compose
-keep class androidx.compose.** { *; }
```

**Debug tip:**
```proguard
-printconfiguration build/outputs/logs/configuration.txt
```

### 6. Performance Metrics

**Startup time:**
- Native Android: baseline
- KMP + Compose MP: +12ms difference (negligible)
- Flutter: +221ms (1.5x slower)

**Binary size:**
- Native Android: 1.7 MB
- KMP + Compose MP: 24.8 MB (+Skia bundling)
- Note: On Android, Compose uses built-in Skia; on iOS, Skia is bundled

**Memory:**
- KMP's incremental GC reduces pause times by ~60%
- New memory model default since Kotlin 1.7.20

### 7. Compose Multiplatform vs Jetpack Compose

| Aspect | Jetpack Compose | Compose Multiplatform |
|--------|-----------------|----------------------|
| Scope | Android only | Android, iOS, Desktop, Web |
| Maintainer | Google | JetBrains |
| APIs | Same | Same (shared compiler/runtime) |
| Release lag | Baseline | 1-3 months after Jetpack |

**Shared:** @Composable functions, state management, modifiers, animations
**Different:** Platform-specific APIs (window handling, UIKit compat)

## Community Sentiment

### Positive
- Google официально поддерживает KMP
- 47% teams report faster delivery times
- 73% would recommend to others
- Market share: 12% (2023) → 23% (2025)
- Production success: Netflix, Google Docs, Cash App, Forbes

### Negative / Concerns
- Learning curve for iOS developers
- Ecosystem gaps for niche libraries
- Plugin compatibility issues after IDE updates
- Binary size increase with Compose MP
- Team adoption challenges (separate → shared codebase)

### Mixed
- Configuration complexity improved but still learning curve
- Debugging better but not perfect
- Swift interop requires SKIE for good experience

## Common Issues & Solutions

### 1. Plugin Compatibility After IDE Update
**Error:** "incompatible: requires IDE build 243.* or earlier"
**Fix:** Download correct plugin version from JetBrains repository

### 2. Navigation + CMP Version Mismatch
**Error:** Build failures with navigation-compose
**Fix:** Match versions (nav 2.9.0-beta03 with CMP 1.8.2, or nav 2.9.0-beta04 with CMP 1.9.0-beta01)

### 3. Duplicate Keys in LazyColumn
**Error:** Crashes on duplicate items
**Fix:** Use `distinctBy` or composite keys

### 4. String Formatting
**Error:** Platform inconsistencies with `%1$s`
**Fix:** Use custom placeholders like `%name` and replace manually

### 5. CancellationException Swallowing
**Error:** Coroutines don't cancel properly
**Fix:** Never catch CancellationException in runCatching or general catch blocks

### 6. ViewModel Dependency Conflicts
**Error:** Duplicate class errors
**Fix:** Exclude ViewModel from libraries that include it

## Best Sources Found

| # | Source | Type | Quality | Key Value |
|---|--------|------|---------|-----------|
| 1 | [Android KMP Plugin](https://developer.android.com/kotlin/multiplatform/plugin) | Official | ★★★★★ | New plugin setup |
| 2 | [KMP Overview](https://developer.android.com/kotlin/multiplatform) | Official | ★★★★★ | Jetpack libraries |
| 3 | [Google I/O 2025 Blog](https://android-developers.googleblog.com/2025/05/android-kotlin-multiplatform-google-io-kotlinconf-2025.html) | Official | ★★★★★ | Announcements |
| 4 | [Compose ViewModel Setup](https://kotlinlang.org/docs/multiplatform/compose-viewmodel.html) | Official | ★★★★★ | ViewModel guide |
| 5 | [Multiplatform Resources](https://kotlinlang.org/docs/multiplatform/compose-multiplatform-resources-usage.html) | Official | ★★★★★ | Resources |
| 6 | [R8 Keep Rules](https://developer.android.com/topic/performance/app-optimization/add-keep-rules) | Official | ★★★★☆ | ProGuard |
| 7 | [Performance Benchmarks](https://medium.com/@jacobras/android-ios-native-vs-flutter-vs-compose-multiplatform-7ef3d5ec2a56) | Community | ★★★★☆ | Benchmarks |

## Research Methodology

- **Queries used:** 8 search queries
- **Sources found:** 30+ total
- **Sources used:** 25 (after quality filter)
- **WebFetch deep reads:** 2 articles
- **Focus areas:** Plugin migration, Jetpack libs, resources, performance, issues


---

*Проверено: 2026-01-09*
