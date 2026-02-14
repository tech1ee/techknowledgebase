---
title: "Системы сборки: сквозной концепт"
created: 2026-02-14
modified: 2026-02-14
type: view
tags:
  - type/view
  - navigation
  - cross-cutting
---

# Системы сборки: сквозной концепт

> Как исходный код превращается в исполняемое приложение на разных платформах — от компиляции и линковки до подписи и дистрибуции.

## Сравнительная матрица

| Платформа | Система сборки | Язык конфигурации | Компиляция | Артефакт | Подпись | Ключевые файлы |
|---|---|---|---|---|---|---|
| Android | Gradle + AGP | Kotlin DSL (build.gradle.kts) | Kotlin → JVM bytecode → DEX | APK / AAB | v2/v3 signing | [[android-gradle-fundamentals]], [[android-compilation-pipeline]] |
| iOS | Xcode Build System | .xcodeproj / .xcconfig | Swift → LLVM IR → Machine Code | .app / .ipa | Code Signing + Provisioning | [[ios-xcode-fundamentals]], [[ios-compilation-pipeline]] |
| KMP | Gradle Multiplatform | Kotlin DSL | Per-target (JVM/Native/JS) | Platform-specific | Per-platform | [[kmp-gradle-deep-dive]], [[kmp-publishing]] |
| Cross-Platform | Gradle + Xcode | Смешанный | Зависит от таргета | Per-platform | Per-platform | [[cross-build-systems]], [[cross-code-signing]] |
| CS Foundations | Концептуальная модель | N/A | Frontend → IR → Backend | Object code | N/A | [[compilation-pipeline]], [[bytecode-virtual-machines]] |

## Android

- [[android-gradle-fundamentals]] — Gradle на Android: build types, flavors, buildConfigField, dependency configurations (api/implementation), convention plugins
- [[android-compilation-pipeline]] — полный путь: .kt → Kotlin compiler → .class → D8/R8 → .dex → APK/AAB, роль AAPT2 для ресурсов
- [[android-dependencies]] — управление зависимостями: Version Catalog, BOM, dependency resolution strategy, конфликты версий
- [[android-proguard-r8]] — оптимизация и обфускация: R8 как замена ProGuard, правила keep, tree shaking, десугаринг, влияние на размер APK
- [[android-apk-aab]] — форматы дистрибуции: APK vs AAB, Dynamic Delivery, App Signing by Google Play, split APKs
- [[android-build-evolution]] — от Ant через Maven к Gradle: почему Gradle победил, и что изменилось с AGP 8+

## iOS

- [[ios-xcode-fundamentals]] — Xcode Build System: targets, schemes, build settings, xcconfig, build phases, Swift Package Manager интеграция
- [[ios-compilation-pipeline]] — Swift → SIL → LLVM IR → Machine Code: этапы компиляции, whole-module optimization, incremental builds
- [[ios-code-signing]] — Code Signing: сертификаты, Provisioning Profiles, Entitlements, автоматический vs ручной signing, распространённые ошибки
- [[ios-app-distribution]] — TestFlight, App Store, Enterprise distribution, Ad Hoc, архивирование и загрузка

## KMP

- [[kmp-gradle-deep-dive]] — Gradle для мультиплатформы: kotlin { } DSL, source sets, таргеты, CocoaPods интеграция, иерархия source sets
- [[kmp-publishing]] — публикация KMP-библиотек: Maven Central, klib-формат, метаданные, interop с CocoaPods и SPM
- [[kmp-ci-cd]] — CI/CD для KMP: сборка на нескольких ОС, кэширование, матричные билды, автоматизация релизов

## Cross-Platform

- [[cross-build-systems]] — как кроссплатформенные фреймворки интегрируются с нативными системами сборки: Gradle + Xcode bridge, CMake
- [[cross-code-signing]] — подпись приложений для нескольких платформ: автоматизация, хранение сертификатов, CI/CD интеграция
- [[cross-distribution]] — дистрибуция на несколько магазинов: unified release pipeline, platform-specific метаданные, A/B rollouts

## CS Foundations

- [[compilation-pipeline]] — теория компиляции: лексический анализ → парсинг → семантический анализ → IR → оптимизация → кодогенерация
- [[bytecode-virtual-machines]] — JVM bytecode, Dalvik/ART, WASM: как виртуальные машины исполняют промежуточный код
- [[native-compilation-llvm]] — LLVM как универсальный бэкенд: IR-представление, оптимизации, генерация машинного кода для ARM/x86

## Общая теория

- [[build-systems-theory]] — фундаментальные концепции: инкрементальная сборка, кэширование, граф зависимостей, reproducible builds, Bazel vs Gradle

## Глубинные паттерны

Android и iOS представляют два фундаментально разных пути компиляции. **Android: Kotlin → JVM bytecode → DEX bytecode** (два уровня промежуточного представления). **iOS: Swift → SIL → LLVM IR → Machine Code** (компиляция в натив). Это различие определяет всё остальное: Android может дешеветь за счёт JIT-компиляции в рантайме (ART), iOS получает максимальную производительность на старте за счёт AOT. R8 на Android выполняет tree shaking на уровне DEX, а Swift compiler оптимизирует на уровне SIL и LLVM IR — разные этапы, но одна цель: убрать неиспользуемый код.

**Gradle стал мостом между платформами** благодаря KMP. Один build.gradle.kts файл может определять таргеты для JVM (Android), Native (iOS через Kotlin/Native + Xcode), JS и WASM. При этом iOS-часть всё равно требует Xcode для финальной сборки и подписи — Gradle генерирует framework, а Xcode собирает его в .app. Это создаёт «двойную систему сборки» — частый источник проблем и увеличенного времени CI.

Code signing — самая болезненная часть мобильной сборки. **Android signing** относительно прост: один keystore, v2/v3 подпись. **iOS code signing** — лабиринт из сертификатов, Provisioning Profiles, Entitlements и App IDs. Каждый мобильный разработчик проходит через «code signing hell», и автоматизация (Fastlane match, Xcode automatic signing) существует именно потому, что ручное управление неустойчиво при масштабировании команды.

## Для интервью

> [!tip] Ключевые вопросы
> - Опишите путь Kotlin-файла от исходного кода до исполнения на Android-устройстве. Какие промежуточные представления он проходит?
> - Чем APK отличается от AAB? Почему Google требует AAB для Play Store?
> - Что делает R8 и чем он отличается от ProGuard? Как debug и release сборки отличаются по оптимизации?
> - Как Gradle KMP организует сборку для нескольких платформ? Что происходит при `./gradlew iosArm64Framework`?
> - Почему iOS code signing сложнее Android signing? Объясните роль Provisioning Profile.
