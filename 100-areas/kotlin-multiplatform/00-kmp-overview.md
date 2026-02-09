---
title: "Kotlin Multiplatform: Полный гайд по кросс-платформенной разработке"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, multiplatform, cross-platform, index]
related:
  - "[[kotlin-overview]]"
  - "[[kotlin-coroutines]]"
  - "[[android-architecture-patterns]]"
cs-foundations:
  - "[[compilation-pipeline]]"
  - "[[bytecode-virtual-machines]]"
  - "[[native-compilation-llvm]]"
  - "[[ffi-foreign-function-interface]]"
---

# Kotlin Multiplatform: полный гайд

> **TL;DR:** KMP — пишите бизнес-логику один раз, компилируйте в Android (JVM), iOS (Native), Web (JS/Wasm), Desktop. UI остаётся нативным: Compose для Android, SwiftUI для iOS. 60-80% кода можно вынести в common. KMP Stable с 2023, Compose Multiplatform iOS Stable с 2024. 20,000+ компаний в production включая Netflix, McDonald's, Google Docs iOS.

---

## Навигация по разделу

### Основы (01-fundamentals)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-getting-started]] | Первый проект за 30 минут | Новичок |
| [[kmp-project-structure]] | Анатомия KMP проекта | Новичок |
| [[kmp-expect-actual]] | Платформо-зависимый код | Новичок |
| [[kmp-source-sets]] | Организация кода по платформам | Новичок |

### Платформы (02-platforms)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-android-integration]] | Android + Jetpack + KMP интеграция | Средний |
| [[kmp-ios-deep-dive]] | iOS: SwiftUI, SKIE, memory, debugging | Средний |
| [[kmp-web-wasm]] | Kotlin/Wasm и Compose для Web | Средний |
| [[kmp-desktop-jvm]] | Desktop приложения с Compose | Средний |

### Compose Multiplatform (03-compose-multiplatform)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[compose-mp-overview]] | Shared UI на всех платформах | Средний |
| [[compose-mp-ios]] | Compose на iOS (Stable) | Средний |
| [[compose-mp-desktop]] | Desktop UI (Stable) | Средний |
| [[compose-mp-web]] | Web с Compose (Beta) | Продвинутый |

### Архитектура (04-architecture)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-architecture-patterns]] | Clean Architecture, MVI, MVVM | Средний |
| [[kmp-di-patterns]] | Koin, kotlin-inject, Manual DI | Средний |
| [[kmp-navigation]] | Compose Navigation, Decompose, Voyager | Средний |
| [[kmp-state-management]] | StateFlow, MVI, Redux patterns | Средний |

### Библиотеки (05-libraries)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-ktor-networking]] | Ktor Client, engines, auth, testing | Средний |
| [[kmp-sqldelight-database]] | SQLDelight, миграции, Flow | Средний |
| [[kmp-kotlinx-libraries]] | serialization, datetime, coroutines, io | Средний |
| [[kmp-third-party-libs]] | Apollo, Coil, Realm, MOKO | Средний |

### Тестирование (06-testing)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-testing-strategies]] | Test pyramid, commonTest, Kover, CI/CD | Средний |
| [[kmp-unit-testing]] | kotlin.test, Kotest, Turbine, runTest | Средний |
| [[kmp-integration-testing]] | MockEngine, in-memory SQLDelight, Fakes | Продвинутый |

### Build & Deploy (07-build-deploy)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-gradle-deep-dive]] | Optimization, caching, convention plugins | Продвинутый |
| [[kmp-ci-cd]] | GitHub Actions, Fastlane, Bitrise | Продвинутый |
| [[kmp-publishing]] | Maven Central, SPM, KMMBridge | Продвинутый |

### Migration (08-migration)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-migration-from-native]] | Android + iOS → KMP поэтапно | Средний |
| [[kmp-migration-from-flutter]] | Flutter → KMP, сравнение стеков | Средний |
| [[kmp-migration-from-rn]] | React Native → KMP, Kotlin/JS | Средний |

### Advanced (09-advanced)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-performance-optimization]] | Build time, binary size, runtime | Продвинутый |
| [[kmp-memory-management]] | GC, ARC, retain cycles, autoreleasepool | Продвинутый |
| [[kmp-debugging]] | LLDB, Xcode, CrashKiOS, crash reporting | Продвинутый |
| [[kmp-interop-deep-dive]] | ObjC bridge, Swift Export, cinterop, SKIE | Продвинутый |

### Production (10-production)

| Материал | Описание | Уровень |
|----------|----------|---------|
| [[kmp-production-checklist]] | Pre-launch checklist, CI/CD, monitoring | Продвинутый |
| [[kmp-case-studies]] | Netflix, McDonald's, Cash App, Forbes | Все уровни |
| [[kmp-troubleshooting]] | Gradle, Xcode, linker, memory issues | Продвинутый |

---

## Что такое KMP

```
┌─────────────────────────────────────────────────────────────┐
│                    KOTLIN MULTIPLATFORM                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📦 Common code (60-80%)        🎨 Platform UI (20-40%)    │
│   ─────────────────────────      ──────────────────────     │
│   • Бизнес-логика                • Android: Compose         │
│   • Модели данных                • iOS: SwiftUI             │
│   • API клиенты                  • Desktop: Compose         │
│   • Репозитории                  • Web: React/HTML          │
│   • Use cases                                               │
│   • Unit-тесты                                              │
│                                                             │
│   Компилируется в:                                          │
│   • JVM bytecode (Android, Server)                          │
│   • Native binary (iOS через LLVM)                          │
│   • JavaScript/WebAssembly (Web)                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Главная аналогия

> **Кондитерская фабрика:** Начинка торта (бисквит, крем) — одинаковая везде, это **common code**. Украшение (надписи, декор) — разное для каждой страны, это **platform UI**.
>
> KMP = одна начинка (бизнес-логика) + разные украшения (Compose для Android, SwiftUI для iOS).

---

## Как KMP работает под капотом

### Три компиляционных backend'а

KMP использует **разные компиляторы** для каждой платформы:

```
                    Kotlin Source Code
                           │
       ┌───────────────────┼───────────────────┐
       │                   │                   │
       ▼                   ▼                   ▼
   Kotlin/JVM         Kotlin/Native       Kotlin/JS|WASM
       │                   │                   │
       ▼                   ▼                   ▼
  JVM Bytecode         LLVM IR          JavaScript/WASM
       │                   │                   │
       ▼                   ▼                   ▼
  Android/JVM/       iOS/macOS/         Browser/Node.js
   Desktop            Linux
```

### Почему это работает

| Platform | Backend | Как компилируется | CS-фундамент |
|----------|---------|-------------------|--------------|
| Android | Kotlin/JVM | → JVM bytecode → ART | [[bytecode-virtual-machines]] |
| iOS | Kotlin/Native | → LLVM IR → Native binary | [[native-compilation-llvm]] |
| Web | Kotlin/JS/WASM | → JavaScript/WebAssembly | [[compilation-pipeline]] |
| Desktop | Kotlin/JVM | → JVM bytecode → JVM | [[bytecode-virtual-machines]] |

### Ключевой insight: один язык, разные runtime

```
Flutter:    Dart → Dart VM (везде одинаковый)
React Native: JS → JS bridge → Native (мост)
KMP:        Kotlin → Platform-native runtime (нативный для каждой платформы)
```

**Результат:** Нет overhead от virtual machine на iOS. Нет bridge между языками. Код исполняется как настоящий native.

> **Для глубокого понимания:** прочитай CS-фундамент [[compilation-pipeline]] и [[native-compilation-llvm]] — это объяснит, почему KMP имеет near-native performance.

---

## Зачем это нужно

### Проблема

| Без KMP | С KMP |
|---------|-------|
| Бизнес-логика пишется дважды | Пишется один раз |
| Баги разные на iOS и Android | Один баг — одно исправление |
| 2 команды, 2 кодовых базы | Общая кодовая база |
| Тесты пишутся дважды | Общие тесты |
| Синхронизация релизов | Одновременный релиз |

### Результаты на практике

- **Netflix, McDonald's, Philips, Forbes** — в production
- **60-80% кода** — выносится в common
- **25% дешевле** поддержка vs React Native
- **20,000+ компаний** используют KMP

---

## Статус технологии (январь 2026)

| Компонент | Статус | Описание |
|-----------|--------|----------|
| **KMP Core** | ✅ Stable | Production-ready с Kotlin 2.0+ |
| **Kotlin 2.1.21** | ✅ Stable | K2 компилятор, 2x быстрее |
| **Compose MP iOS** | ✅ Stable | Native scrolling, gestures |
| **Compose MP Web** | 🧪 Beta | Kotlin/Wasm Beta |
| **Swift Export** | 🆕 Experimental | Kotlin → Swift без Obj-C |
| **Jetpack Libraries** | ✅ Stable | Room, DataStore, ViewModel, Paging |

---

## KMP vs Flutter vs React Native

| Критерий | KMP | Flutter | React Native |
|----------|-----|---------|--------------|
| **UI** | Нативный (Compose/SwiftUI) | Собственный рендеринг | Нативные компоненты |
| **Язык** | Kotlin | Dart | JavaScript/TypeScript |
| **Производительность** | Нативная | Близка к нативной | Мост к нативному |
| **iOS look & feel** | Настоящий SwiftUI | Эмуляция | Частично нативный |
| **Постепенная миграция** | ✅ Per-module | Сложно | Сложно |
| **Learning curve** | Низкая для Android-девов | Средняя (Dart) | Средняя (JS) |

### Когда выбирать KMP

✅ **Выбирайте KMP если:**
- Нужен настоящий нативный UI
- Команда знает Kotlin (Android-разработчики)
- Постепенная миграция существующего приложения
- Важна максимальная производительность
- Нужен полный доступ к платформенным API

❌ **НЕ выбирайте KMP если:**
- Маленькая команда без опыта в нативной разработке
- Нужен одинаковый UI на всех платформах (выбирайте Flutter)
- Быстрый прототип MVP

---

## Ключевые компании в production

| Компания | Продукт | Результат |
|----------|---------|-----------|
| **Netflix** | Mobile studio apps | 60% shared code |
| **McDonald's** | Global mobile app | Unified experience |
| **Google Docs** | iOS app | Feature parity faster |
| **Philips** | Healthcare apps | Critical apps on KMP |
| **Cash App** | Fintech | Shared business logic |
| **Forbes** | Mobile apps | Faster development |
| **9GAG** | Entertainment | 70% shared code |

---

## Быстрый старт

### 1. Установка

```bash
# Требования:
# - IntelliJ IDEA 2025.2.2+ или Android Studio Otter 2025.2.1+
# - Kotlin Multiplatform IDE plugin
# - Для iOS: macOS + Xcode
```

### 2. Создание проекта

Открыть [kmp.jetbrains.com](https://kmp.jetbrains.com) → выбрать targets → скачать → открыть в IDE.

### 3. Первый shared код

```kotlin
// commonMain/kotlin/Greeting.kt
class Greeting {
    fun greet(): String = "Hello from ${getPlatformName()}!"
}

expect fun getPlatformName(): String

// androidMain/kotlin/Platform.android.kt
actual fun getPlatformName(): String = "Android"

// iosMain/kotlin/Platform.ios.kt
actual fun getPlatformName(): String = "iOS"
```

➡️ Подробнее: [[kmp-getting-started]]

---

## Мифы и заблуждения

### ❌ "KMP — это как Flutter, только на Kotlin"

**Реальность:** Принципиально разные подходы. Flutter использует единый Dart VM и собственный рендеринг на всех платформах. KMP компилирует в **нативный код каждой платформы**: JVM bytecode для Android, LLVM native binary для iOS, JavaScript/Wasm для Web.

```
Flutter:     Dart → Dart VM → Skia canvas (везде одинаково)
KMP:         Kotlin → Platform runtime (нативный для каждой платформы)
```

**Следствие:** KMP не добавляет runtime overhead — код исполняется как настоящий native.

### ❌ "Нужно переписать всё приложение"

**Реальность:** KMP спроектирован для **постепенной миграции**. Можно начать с одного модуля (например, networking), интегрировать его как обычную library, и расширять по мере необходимости. Многие компании начинают с 10-20% shared кода и постепенно доходят до 60-80%.

### ❌ "UI тоже shared — значит, будет выглядеть чужеродно"

**Реальность:** **UI остаётся нативным по умолчанию.** Стандартный подход — shared business logic + native UI (Compose для Android, SwiftUI для iOS). Compose Multiplatform — опциональный выбор для тех, кто хочет shared UI.

### ❌ "iOS разработчики не примут Kotlin"

**Реальность:** С появлением **SKIE** (Swift-Kotlin Interface Enhancer) и **Swift Export**, iOS разработчики видят KMP как обычную Swift library:
- Sealed classes → Swift enums
- Coroutines → async/await
- Flow → AsyncSequence
- Kotlin nullability → Swift optionals

### ❌ "KMP медленнее нативного кода"

**Реальность:** Kotlin/Native компилируется через LLVM в настоящий machine code — **тот же backend, что и Swift/Clang**. Performance benchmarks показывают near-native скорость. Единственный overhead — interop между Kotlin и Swift, который SKIE минимизирует.

### ❌ "Только для мобильных приложений"

**Реальность:** KMP поддерживает:
- **Mobile:** Android, iOS
- **Desktop:** Windows, macOS, Linux (JVM + Compose)
- **Web:** JavaScript, WebAssembly
- **Server:** JVM backend (Spring, Ktor)
- **Embedded:** Kotlin/Native для IoT

Netflix, например, использует KMP для mobile, TV apps и backend services.

---

## Рекомендуемые источники

### Официальная документация

| Источник | Описание |
|----------|----------|
| [kotlinlang.org/docs/multiplatform](https://kotlinlang.org/docs/multiplatform.html) | Главная документация |
| [kmp.jetbrains.com](https://kmp.jetbrains.com) | KMP Wizard |
| [developer.android.com/kotlin/multiplatform](https://developer.android.com/kotlin/multiplatform) | Android + KMP |

### Обучение

| Источник | Тип | Описание |
|----------|-----|----------|
| [JetBrains Learning Resources](https://kotlinlang.org/docs/multiplatform/kmp-learning-resources.html) | Collection | 30+ материалов |
| [Philipp Lackner](https://www.youtube.com/@PhilippLackner) | YouTube | Практические курсы |
| [Kodeco KMP by Tutorials](https://www.kodeco.com/books/kotlin-multiplatform-by-tutorials) | Book | Полный курс |

### Сообщество

| Ресурс | Описание |
|--------|----------|
| [#multiplatform](https://kotlinlang.slack.com/archives/C3PQML5NU) | Kotlin Slack channel |
| [klibs.io](https://klibs.io) | 2000+ KMP библиотек |

### CS-фундамент

| Концепция | Материал | Почему важно |
|-----------|----------|--------------|
| Компиляция | [[compilation-pipeline]] | Понимание frontend/backend/IR |
| Virtual Machines | [[bytecode-virtual-machines]] | JVM/ART для Android/Desktop |
| Native компиляция | [[native-compilation-llvm]] | LLVM для iOS/Native targets |
| FFI | [[ffi-foreign-function-interface]] | Interop между Kotlin и платформами |

---

## Дорожная карта этого раздела

- [x] **Фаза 1:** Fundamentals (4 материала)
- [x] **Фаза 2:** Platforms (4 материала)
- [x] **Фаза 3:** Compose Multiplatform (4 материала)
- [x] **Фаза 4:** Architecture (4 материала)
- [x] **Фаза 5:** Libraries (4 материала)
- [x] **Фаза 6:** Testing (3 материала)
- [x] **Фаза 7:** Build & Deploy (3 материала)
- [x] **Фаза 8:** Migration (3 материала)
- [x] **Фаза 9:** Advanced (4 материала)
- [x] **Фаза 10:** Production (3 материала) ✅

**Всего:** 36 детальных материалов с Deep Research для каждого. **ЗАВЕРШЕНО!**

---

*Проверено: 2026-01-09 | KMP Stable, Kotlin 2.1.21, Compose Multiplatform iOS Stable*
