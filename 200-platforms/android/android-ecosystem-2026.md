---
title: "Android Ecosystem Reference 2026"
created: 2026-02-14
modified: 2026-02-14
type: reference
status: published
confidence: high
area: android
tags:
  - topic/android
  - topic/kotlin
  - type/reference
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-moc]]"
  - "[[android-jetpack-libraries-map]]"
  - "[[android-platform-versions]]"
  - "[[android-firebase-platform]]"
reading_time: 15
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Android Ecosystem Reference 2026

Справочник по всем инструментам, библиотекам и технологиям Android-разработки. Актуально на февраль 2026.

> Для навигации по Jetpack-библиотекам: [[android-jetpack-libraries-map]]
> Для истории версий Android: [[android-platform-versions]]

---

## Platform Status

| Компонент | Версия | Дата выхода | Примечание |
|-----------|--------|-------------|------------|
| **Android** | 16 (API 35/36) | Июнь 2025 | Material 3 Expressive, ProgressStyle |
| **Android 17** | Beta 1 | Февраль 2026 | Developer preview |
| **Kotlin** | 2.2.20 / 2.3.0 | Сент / Дек 2025 | Guard conditions stable, Wasm Beta |
| **Jetpack Compose** | 1.10 | Декабрь 2025 | Производительность = Views, retain API |
| **Material 3** | 1.4 | Декабрь 2025 | AutoSize Text, SecureTextField |
| **AGP** | 9.0.1 | Январь 2026 | Новый DSL, старый variant API удалён |
| **Gradle** | 8.13+ | 2025 | Совместим с AGP 9.0 |
| **Android Studio** | Narwhal | 2025 | Gemini integration, AI code completion |
| **KSP** | 2.2.20-1.0.x | 2025 | Замена KAPT (KAPT deprecated) |

---

## Languages & Core

| Инструмент | Версия | Статус | Deep Dive |
|------------|--------|--------|-----------|
| **Kotlin** | 2.2.20 | Stable | [[kotlin-overview]] |
| **Java** | 17 (desugaring) | Support | — |
| **KSP** (Kotlin Symbol Processing) | 2.x | Stable | [[android-compilation-pipeline]] |
| **KAPT** | — | Deprecated | Мигрировать на KSP |
| **Compose Compiler** | Merged in Kotlin 2.0+ | Stable | [[android-compose-internals]] |

---

## UI

| Библиотека | Версия | Статус | Deep Dive |
|------------|--------|--------|-----------|
| **Jetpack Compose** | 1.10 (BOM 2026.01.01) | Standard | [[android-compose]], [[android-compose-internals]] |
| **Material 3** | 1.4 | Stable | [[android-compose]] |
| **Material 3 Expressive** | Rolling out | Preview | Blur, springs, enhanced animation |
| **Coil** | 3.x | Recommended | Kotlin-first, coroutine-based image loading |
| **Glide** | 4.16+ | Maintained | Legacy, Java-centric |
| **Lottie** | 6.x | Stable | After Effects animations |
| **Navigation** | Nav3 (stable Nov 2025) | Recommended | [[android-navigation]], [[android-navigation-evolution]] |
| **Paging 3** | 3.3+ | Stable | [[android-jetpack-libraries-map]] |

---

## Architecture

| Компонент | Версия | Статус | Deep Dive |
|-----------|--------|--------|-----------|
| **ViewModel** | lifecycle 2.9+ | Stable | [[android-viewmodel-internals]] |
| **Lifecycle** | 2.9+ | Stable | [[android-activity-lifecycle]] |
| **SavedStateHandle** | lifecycle 2.9+ | Stable | [[android-viewmodel-internals]] |
| **MVVM / MVI** | — | Recommended | [[android-architecture-patterns]] |
| **Repository Pattern** | — | Standard | [[android-repository-pattern]] |
| **Modularization** | — | Best practice | [[android-modularization]] |

---

## Networking

| Библиотека | Версия | Статус | Deep Dive |
|------------|--------|--------|-----------|
| **Retrofit** | 2.11+ | Standard | [[android-networking]] |
| **OkHttp** | 4.12+ | Standard | [[android-networking]] |
| **Ktor Client** | 3.1+ | Growing (KMP) | [[android-networking]] |
| **kotlinx.serialization** | 1.7+ | Recommended | Замена Gson/Moshi |
| **Moshi** | 1.15+ | Maintained | Ещё популярен |
| **Gson** | 2.11+ | Legacy | Не рекомендуется для новых проектов |

---

## Data Persistence

| Библиотека | Версия | Статус | Deep Dive |
|------------|--------|--------|-----------|
| **Room** | 2.7+ | Standard | [[android-room-deep-dive]], [[android-room-migrations]], [[android-room-performance]] |
| **DataStore** | 1.1+ | Recommended | [[android-datastore-guide]] |
| **SQLDelight** | 2.0+ | Growing (KMP) | Cross-platform SQL |
| **SharedPreferences** | — | Legacy | Мигрировать на DataStore |
| **EncryptedSharedPreferences** | — | Deprecated | DataStore + Tink |

---

## Dependency Injection

| Фреймворк | Версия | Тип | Статус | Deep Dive |
|-----------|--------|-----|--------|-----------|
| **Hilt** | 2.55+ | Compile-time | Recommended | [[android-hilt-deep-dive]] |
| **Koin** | 4.1+ | Runtime | Popular | [[android-koin-deep-dive]] |
| **kotlin-inject** | 0.7+ | Compile-time (KMP) | Growing | [[android-kotlin-inject-deep-dive]] |
| **Metro** | 0.3+ | Compiler plugin | New (2025) | [[android-metro-deep-dive]] |
| **Dagger 2** | 2.55+ | Compile-time | Legacy | [[android-dagger-deep-dive]] |

---

## Async & Background

| Инструмент | Версия | Статус | Deep Dive |
|------------|--------|--------|-----------|
| **Kotlin Coroutines** | 1.10+ | Standard | [[kotlin-coroutines]], [[android-coroutines-mistakes]] |
| **Kotlin Flow** | 1.10+ | Standard | [[kotlin-flow]] |
| **WorkManager** | 2.10+ | Standard | [[android-background-work]] |
| **RxJava** | 3.x | Legacy | Мигрировать на Coroutines/Flow |

---

## Build System

| Инструмент | Версия | Статус | Deep Dive |
|------------|--------|--------|-----------|
| **AGP** | 9.0.1 | Current | [[android-gradle-fundamentals]] |
| **Gradle** | 8.13+ | Current | [[android-gradle-fundamentals]] |
| **Version Catalogs** | libs.versions.toml | Standard | [[android-dependencies]] |
| **R8** | AGP-bundled | Standard | [[android-proguard-r8]] |
| **D8** | AGP-bundled | Standard | [[android-compilation-pipeline]] |
| **Baseline Profiles** | 1.4+ | Production-ready | [[android-app-startup-performance]] |

---

## Testing

| Инструмент | Версия | Назначение | Deep Dive |
|------------|--------|------------|-----------|
| **JUnit 5** | 5.11+ | Unit tests | [[android-testing]] |
| **MockK** | 1.13+ | Mocking (Kotlin) | [[android-testing]] |
| **Turbine** | 1.2+ | Flow testing | [[android-testing]] |
| **Espresso** | 3.6+ | UI tests | [[android-testing]] |
| **Compose Testing** | 1.10+ | Compose UI tests | [[android-testing]] |
| **Robolectric** | 4.14+ | JVM Android tests | [[android-testing]] |
| **Roborazzi** | 1.9+ | Screenshot tests | [[android-testing]] |
| **Macrobenchmark** | 1.3+ | Performance tests | [[android-app-startup-performance]] |
| **Firebase Test Lab** | — | Cloud device testing | [[android-ci-cd]] |

---

## CI/CD & Distribution

| Инструмент | Статус | Назначение | Deep Dive |
|------------|--------|------------|-----------|
| **GitHub Actions** | Dominant | CI/CD pipeline | [[android-ci-cd]] |
| **Fastlane** | Standard | Build automation, deployment | [[android-ci-cd]] |
| **Firebase App Distribution** | Standard | Beta testing | [[android-firebase-platform]] |
| **Google Play Console** | Required | Production distribution | [[android-apk-aab]] |
| **Gradle Play Publisher** | Popular | Automated Play Store deployment | [[android-ci-cd]] |
| **Gradle Managed Devices** | Stable | Declarative emulator control | [[android-ci-cd]] |

---

## Analytics & Observability

| Инструмент | Тип | Pricing | Deep Dive |
|------------|-----|---------|-----------|
| **Firebase Crashlytics** | Crash reporting | Free | [[android-analytics-crash-reporting]] |
| **Firebase Analytics** | Product analytics | Free | [[android-analytics-crash-reporting]] |
| **Firebase Performance** | Performance monitoring | Free | [[android-analytics-crash-reporting]] |
| **Sentry** | Crash + performance | Freemium | [[android-analytics-crash-reporting]] |
| **Amplitude** | Product analytics | Freemium | [[android-analytics-crash-reporting]] |
| **Mixpanel** | Event analytics | Freemium | [[android-analytics-crash-reporting]] |

---

## Firebase Platform

| Сервис | Назначение | Free Tier |
|--------|------------|-----------|
| **Authentication** | Auth (Email, Google, Apple, Phone) | 50K MAU |
| **Cloud Firestore** | Document database, real-time sync | 50K reads/day |
| **Cloud Messaging (FCM)** | Push notifications | Unlimited |
| **Crashlytics** | Crash reporting | Unlimited |
| **Remote Config** | Feature flags, A/B testing | Unlimited |
| **App Check** | Device attestation (Play Integrity) | 10K calls/day |
| **App Distribution** | Beta testing | Unlimited |
| **Test Lab** | Cloud device testing | 15 virtual + 5 physical/day |

→ Полный гайд: [[android-firebase-platform]]

---

## Code Quality

| Инструмент | Версия | Назначение | Deep Dive |
|------------|--------|------------|-----------|
| **Detekt** | 1.23.8 | Static analysis (Kotlin) | [[android-code-quality-tools]] |
| **ktlint** | 1.7.0 | Code formatting (Kotlin) | [[android-code-quality-tools]] |
| **ktfmt** | — | Opinionated formatting (Meta) | [[android-code-quality-tools]] |
| **Android Lint** | AGP-bundled | 2000+ built-in checks | [[android-code-quality-tools]] |
| **Spotless** | 8.2.1 | Multi-language formatting | [[android-code-quality-tools]] |

---

## Feature Flags

| Платформа | Тип | Hosting | Deep Dive |
|-----------|-----|---------|-----------|
| **Firebase Remote Config** | Managed | Cloud (Google) | [[android-feature-flags-remote-config]] |
| **LaunchDarkly** | Enterprise | Cloud | [[android-feature-flags-remote-config]] |
| **Unleash** | Open-source | Self-hosted / Cloud | [[android-feature-flags-remote-config]] |
| **Flagsmith** | Open-source | Self-hosted / Cloud | [[android-feature-flags-remote-config]] |

---

## On-Device AI

| Технология | Назначение | Доступность | Deep Dive |
|-----------|------------|-------------|-----------|
| **Gemini Nano** | On-device LLM (summarization, smart reply) | Pixel 8+, Galaxy S24+ | [[android-on-device-ai]] |
| **ML Kit GenAI** | Summarization, Proofreading, Image Description | Устройства с Gemini Nano | [[android-on-device-ai]] |
| **ML Kit Classic** | OCR, Barcode, Face, Pose | Все устройства | [[android-on-device-ai]] |
| **LiteRT (TFLite)** | Custom model inference | Все устройства | [[android-on-device-ai]], [[mobile-ai-ml-guide]] |
| **MediaPipe** | Pre-built vision/audio/LLM solutions | Все устройства | [[android-on-device-ai]] |

---

## Security

| Инструмент / API | Назначение | Статус | Deep Dive |
|------------------|------------|--------|-----------|
| **Play Integrity API** | Device/app attestation | Required (SafetyNet deprecated Jan 2025) | [[android-permissions-security]] |
| **BiometricPrompt** | Fingerprint / Face auth | Stable | [[android-permissions-security]] |
| **Android Keystore** | Hardware-backed key storage | Stable | [[android-permissions-security]] |
| **App Check** | Firebase request attestation | Stable | [[android-firebase-platform]] |
| **R8** | Code shrinking + obfuscation | Standard | [[android-proguard-r8]] |
| **Network Security Config** | Certificate pinning, cleartext control | Standard | [[android-networking]] |

---

## Trends 2026

### 1. Compose — стандарт
Compose 1.10 достиг паритета производительности с Views. Более 60% разработчиков используют Compose. XML layouts — legacy.

### 2. Kotlin-first экосистема
Coil > Glide, kotlinx.serialization > Gson, Ktor растёт. KAPT deprecated → KSP. KTX-модули Firebase упразднены.

### 3. AGP 9 и Gradle modernization
AGP 9.0.1 с новым DSL. Старые API удалены — миграция неизбежна. Version Catalogs — стандарт.

### 4. On-Device AI
Gemini Nano multimodal (Pixel 10+), ML Kit GenAI APIs, Prompt API (Alpha). AI — дифференциатор продукта.

### 5. Privacy-first
Privacy Sandbox retired (окт 2025). SafetyNet → Play Integrity. Фокус на data minimization и user consent.

### 6. Large screens & adaptive layouts
Android 16 enforces adaptive layouts для больших экранов. Orientation restrictions снимаются для targetSdk 36+.

### 7. minSdk 23+ как новый минимум
AndroidX библиотеки требуют API 23+ с июня 2025. targetSdk 35+ обязателен для Google Play с августа 2025.

---

## Проверь себя

> [!question]- Какой набор библиотек нужен для нового Android-проекта в 2026?
> Минимум: Kotlin 2.2+, Compose (BOM 2026.01.01), Material 3 1.4, Navigation 3, Hilt, Room, DataStore, Coroutines/Flow, Retrofit + OkHttp + kotlinx.serialization, Coil, WorkManager. CI: GitHub Actions + Fastlane. Quality: Detekt + ktlint + Android Lint. Monitoring: Firebase (Crashlytics + Analytics + Remote Config).

> [!question]- Что изменилось с 2024 по 2026?
> Compose достиг паритета с Views (1.10). AGP обновился с 8.x до 9.0.1 (новый DSL). Kotlin — с 1.9 до 2.3. SafetyNet deprecated → Play Integrity. Privacy Sandbox retired. Gemini Nano стал multimodal. Navigation 3 стабильна. KTX-модули Firebase упразднены. minSdk AndroidX = 23.

---

## Ключевые карточки

**Q:** Какой compileSdk / targetSdk / minSdk рекомендуется для нового проекта в 2026?
**A:** compileSdk = 36, targetSdk = 35 (или 36), minSdk = 26 (для consumer apps) или 23 (для максимального reach). Google Play требует targetSdk ≥ 35.

**Q:** Coil или Glide в 2026?
**A:** Coil — recommended для новых проектов (Kotlin-first, coroutine-based, Compose support). Glide — maintained, оправдан в legacy-проектах с Java. Picasso — не рекомендуется.

**Q:** Какие Firebase сервисы полностью бесплатны?
**A:** Crashlytics, Analytics, Remote Config, FCM, A/B Testing, In-App Messaging. Без usage-based pricing.

**Q:** Чем отличается AGP 9 от AGP 8?
**A:** AGP 9.0.1 использует новые DSL-интерфейсы и полностью удаляет deprecated variant API. Миграция с 8.x может потребовать рефакторинга build scripts.

**Q:** Gemini Nano доступен на всех устройствах?
**A:** Нет. Только на premium-устройствах (Pixel 8+, Galaxy S24+). Обязательна fallback-стратегия: on-device → cloud API → graceful degradation.

---

## Куда дальше

| Направление | Ссылка | Зачем |
|-------------|--------|-------|
| Jetpack-библиотеки | [[android-jetpack-libraries-map]] | Полная карта 80+ библиотек с версиями |
| Версии Android | [[android-platform-versions]] | API levels, feature matrix, minSdk guide |
| Firebase | [[android-firebase-platform]] | 20+ сервисов: Auth, Firestore, FCM, Crashlytics |
| Аналитика | [[android-analytics-crash-reporting]] | Crashlytics, Analytics, Amplitude, Sentry |
| Code quality | [[android-code-quality-tools]] | Detekt, ktlint, Lint, CI integration |
| Feature flags | [[android-feature-flags-remote-config]] | Remote Config, LaunchDarkly, A/B testing |
| On-device AI | [[android-on-device-ai]] | Gemini Nano, ML Kit, TFLite, MediaPipe |
| Обзор Android | [[android-overview]] | Архитектура платформы, компоненты |

---

## Источники

- [Android Developers — What's new](https://developer.android.com/about/versions) — версии Android и что нового
- [AndroidX Releases](https://developer.android.com/jetpack/androidx/versions) — все Jetpack-библиотеки
- [Kotlin Blog](https://blog.jetbrains.com/kotlin/) — релизы Kotlin
- [Firebase Blog](https://firebase.blog/) — обновления Firebase
- [Android Developers Blog](https://android-developers.googleblog.com/) — официальный блог
- [Compose BOM Mapping](https://developer.android.com/develop/ui/compose/bom/bom-mapping) — версии Compose
- [Google Play targetSdk Requirements](https://developer.android.com/google/play/requirements/target-sdk) — дедлайны

---

*Актуально на февраль 2026. Рекомендуемая дата ревизии: август 2026.*
