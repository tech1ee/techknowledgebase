---
title: "Kotlin Multiplatform: Полный гайд по кросс-платформенной разработке"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - topic/cross-platform
  - type/moc
  - level/beginner
related:
  - "[[kotlin-overview]]"
  - "[[kotlin-coroutines]]"
  - "[[android-architecture-patterns]]"
cs-foundations:
  - "[[compilation-pipeline]]"
  - "[[bytecode-virtual-machines]]"
  - "[[native-compilation-llvm]]"
  - "[[ffi-foreign-function-interface]]"
status: published
reading_time: 11
difficulty: 3
study_status: not_started
mastery: 0
last_reviewed:
next_review:
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

## Теоретические основы

### Формальное определение

> **Кросс-платформенная разработка (Cross-Platform Development)** — методология создания программного обеспечения, при которой единая кодовая база компилируется или интерпретируется для исполнения на нескольких целевых платформах (Jemerov, Isakova, 2017).

KMP реализует подход **shared-source compilation** — в отличие от write-once-run-anywhere (Java, 1995) или transpilation (React Native, 2015), исходный код Kotlin компилируется отдельным backend-компилятором для каждой целевой платформы.

### Историческая эволюция кросс-платформенных подходов

| Год | Технология | Подход | Ключевая идея |
|-----|-----------|--------|---------------|
| 1995 | Java / JVM | Write Once, Run Anywhere | Единая виртуальная машина на всех платформах |
| 2008 | PhoneGap / Cordova | Hybrid WebView | Web-приложение внутри нативной обёртки |
| 2011 | Xamarin | Shared runtime (Mono) | C# компилируется через общий CLR |
| 2015 | React Native | Bridge-based | JavaScript ↔ Native bridge, интерпретация |
| 2017 | Flutter | Custom rendering engine | Dart VM + Skia canvas, единый рендеринг |
| 2020 | KMP Stable (Alpha→Beta) | Per-platform compilation | Kotlin → JVM / LLVM / JS, нативный runtime |
| 2023 | KMP 1.0 Stable | Production-ready | Официальная стабильность от JetBrains |

### Таксономия разделяемого кода

В теории кросс-платформенной разработки выделяют два уровня разделения (Touchlab, 2023):

| Уровень | Что разделяется | Примеры технологий |
|---------|----------------|-------------------|
| **Shared Logic** | Бизнес-логика, модели, networking, storage | KMP (default), Xamarin.Core |
| **Shared UI** | Пользовательский интерфейс + логика | Flutter, Compose Multiplatform, React Native |

KMP уникален тем, что поддерживает **оба уровня**: shared logic по умолчанию (commonMain), shared UI опционально (Compose Multiplatform).

### Архитектура компиляции KMP

KMP базируется на концепции **multi-backend compiler** (Breslav, 2017). Фронтенд компилятора K2 анализирует исходный код один раз, а затем несколько backend-генераторов создают платформо-специфичный выход:

- **Kotlin/JVM** → JVM bytecode → ART (Android) / HotSpot (Desktop/Server) — см. [[bytecode-virtual-machines]]
- **Kotlin/Native** → LLVM IR → machine code (iOS, macOS, Linux) — см. [[native-compilation-llvm]]
- **Kotlin/JS** → JavaScript AST → .js файлы — см. [[compilation-pipeline]]
- **Kotlin/Wasm** → WebAssembly binary → браузерная VM

> **Принцип Liskov в контексте KMP:** платформенные реализации (actual) должны быть полностью взаимозаменяемы с контрактом (expect) — это формальное применение Liskov Substitution Principle (Martin, 2017) к кросс-платформенному коду.

### Сравнение моделей исполнения

| Характеристика | KMP | Flutter | React Native |
|---------------|-----|---------|--------------|
| Модель компиляции | AOT per-platform | AOT (Dart → ARM) + JIT (dev) | JIT (Hermes/JSC) |
| Уровень абстракции runtime | Нативный runtime платформы | Единый Dart VM | JavaScript engine + bridge |
| Overhead вызова платформы | Нулевой (JVM) / FFI (Native) | Platform channels (async) | JSI bridge (sync/async) |
| Garbage collection | Platform GC (JVM GC / K/N GC) | Dart GC (generational) | JS engine GC |

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

## Связь с другими темами

**[[kotlin-overview]]** — Kotlin Multiplatform построен на фундаменте языка Kotlin и его экосистемы. Понимание ключевых возможностей Kotlin (null safety, extension functions, sealed classes, DSL builders) критически важно для эффективной работы с KMP. Все мультиплатформенные абстракции (expect/actual, common source sets) опираются на систему типов и компилятор Kotlin. Изучение основ языка необходимо до погружения в мультиплатформенную разработку.

**[[kotlin-coroutines]]** — Корутины являются основным механизмом асинхронного программирования в KMP. Они обеспечивают единый подход к concurrency на всех платформах: JVM использует thread pool, Native — worker threads, а JS — event loop. Понимание structured concurrency, Flow, Channel и CoroutineScope необходимо для написания shared-кода, работающего корректно на каждой целевой платформе. Без корутин невозможно реализовать networking, базы данных и UI-обновления в KMP.

**[[android-architecture-patterns]]** — Android является основной платформой, где KMP чаще всего внедряется первым. Паттерны Android-архитектуры (MVVM, MVI, Clean Architecture) напрямую переносятся в KMP через shared ViewModel и UseCase слои. Опыт работы с Jetpack Compose, Navigation Component и ViewModel помогает быстрее освоить Compose Multiplatform и мультиплатформенную навигацию.

## Источники и дальнейшее чтение

### Теоретические основы

1. **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* Manning. — Фундаментальное руководство по языку Kotlin от разработчиков JetBrains. Описывает систему типов, корутины и JVM-interop, лежащие в основе KMP.
2. **Martin R. (2017).** *Clean Architecture.* Prentice Hall. — Принципы Dependency Inversion и Boundary Objects, определяющие разделение shared и platform-specific кода.
3. **Breslav A. (2017).** *Kotlin: Multi-target Compilation.* JetBrains Technical Report. — Формальное описание архитектуры multi-backend компилятора Kotlin.
4. **Gosling J. et al. (1996).** *The Java Language Specification.* Addison-Wesley. — Исторический контекст «Write Once, Run Anywhere», первой попытки кросс-платформенной компиляции.

### Практические руководства

1. **Moskala M. (2021).** *Effective Kotlin.* — Практические рекомендации по написанию идиоматичного Kotlin-кода для shared-модулей KMP.
2. **Moskala M. (2022).** *Kotlin Coroutines: Deep Dive.* — Корутины как основа асинхронного программирования в KMP.
3. [kotlinlang.org/docs/multiplatform](https://kotlinlang.org/docs/multiplatform.html) — Официальная документация KMP от JetBrains.
4. [developer.android.com/kotlin/multiplatform](https://developer.android.com/kotlin/multiplatform) — Android + KMP интеграция от Google.

---

*Проверено: 2026-01-09 | KMP Stable, Kotlin 2.1.21, Compose Multiplatform iOS Stable*

---

## Проверь себя

> [!question]- Почему KMP на iOS показывает near-native производительность, тогда как React Native работает через bridge? Объясни разницу на уровне компиляции.
> KMP компилирует Kotlin-код через Kotlin/Native → LLVM IR → native machine code. Это тот же компиляционный backend, что использует Swift/Clang, поэтому результирующий бинарник исполняется напрямую процессором без посредников. React Native, напротив, исполняет JavaScript в отдельном runtime (Hermes/JSC) и взаимодействует с нативными компонентами через bridge/JSI, что создаёт overhead на сериализацию данных и переключение контекстов. Ключевое отличие — KMP не добавляет дополнительный runtime layer на iOS.

> [!question]- Компания решает мигрировать существующее Android+iOS приложение на KMP. Какую стратегию миграции ты порекомендуешь и почему KMP подходит для этого лучше, чем Flutter?
> KMP спроектирован для постепенной миграции — можно начать с одного модуля (например, networking или data layer), упаковать его как обычную library и интегрировать в существующие Android и iOS проекты. UI остаётся нативным (Compose/SwiftUI), поэтому переписывать экраны не нужно. Flutter требует переписывания всего UI на Dart и собственный rendering engine, что делает постепенную миграцию практически невозможной. Рекомендуемая стратегия: начать с 10-20% shared кода (модели, API-клиенты), постепенно расширяя до 60-80%.

> [!question]- Как механизм expect/actual связан с концепцией FFI (Foreign Function Interface) из CS-фундамента? В чём принципиальное отличие?
> И expect/actual, и FFI решают одну задачу — взаимодействие с платформо-зависимым кодом. Однако expect/actual работает на уровне компилятора: компилятор проверяет, что для каждого `expect`-объявления в common-коде существует `actual`-реализация в каждом платформенном source set. Это type-safe и проверяется в compile time. FFI (например, JNI, cinterop) работает на уровне runtime — вызов функций из другого языка через бинарный интерфейс, что менее безопасно и требует ручного управления маршаллингом данных. expect/actual — это абстракция уровнем выше FFI.

> [!question]- Если KMP использует три разных компиляционных backend'а (JVM, Native, JS/Wasm), как достигается единообразное поведение shared-кода на всех платформах? Где могут возникнуть несоответствия?
> Единообразие достигается через общий frontend компилятора (K2) и стандартную библиотеку kotlinx, которая предоставляет идентичный API на всех платформах. Однако несоответствия возможны: разные модели concurrency (корутины на JVM используют thread pool, на Native — worker threads, на JS — event loop), различия в числовой точности (JS не имеет настоящего Long), разные реализации regex, различное поведение при interop с платформенными API. Также garbage collector на JVM и ARC на Native имеют разные характеристики, что может влиять на паттерны управления памятью.

---

## Ключевые карточки

KMP — что это и какую проблему решает?
?
Kotlin Multiplatform — технология, позволяющая писать бизнес-логику один раз на Kotlin и компилировать в нативный код для Android (JVM), iOS (Native/LLVM), Web (JS/Wasm) и Desktop. Решает проблему дублирования 60-80% кода между платформами.

Какие три компиляционных backend'а использует KMP и во что они компилируют?
?
1) Kotlin/JVM → JVM bytecode (для Android, Desktop, Server). 2) Kotlin/Native → LLVM IR → native binary (для iOS, macOS, Linux). 3) Kotlin/JS и Kotlin/Wasm → JavaScript или WebAssembly (для Web/Node.js).

Чем подход KMP к кросс-платформенности принципиально отличается от Flutter и React Native?
?
KMP компилирует в platform-native runtime (JVM, LLVM, JS) — нет overhead от виртуальной машины или bridge. Flutter использует единый Dart VM и собственный рендеринг (Skia) на всех платформах. React Native исполняет JS и общается с нативными компонентами через bridge. KMP = нативное исполнение, Flutter = единый runtime, RN = bridge.

Что такое expect/actual в KMP?
?
Механизм платформо-зависимого кода: `expect` объявляет интерфейс в common-коде, `actual` предоставляет реализацию в каждом платформенном source set. Проверяется компилятором в compile time, обеспечивает type safety.

Какой процент кода обычно выносится в common и что именно туда входит?
?
60-80% кода: бизнес-логика, модели данных, API-клиенты, репозитории, use cases, unit-тесты. Платформо-зависимым остаётся UI (20-40%): Compose для Android, SwiftUI для iOS, HTML/React для Web.

Каков текущий статус KMP и Compose Multiplatform (январь 2026)?
?
KMP Core — Stable (с 2023). Kotlin 2.1.21 с K2 компилятором. Compose MP iOS — Stable (с мая 2025). Compose MP Web — Beta. Swift Export — Experimental. Jetpack Libraries (Room, DataStore, ViewModel) — Stable для KMP.

Как SKIE решает проблему принятия KMP iOS-разработчиками?
?
SKIE (Swift-Kotlin Interface Enhancer) транслирует Kotlin-конструкции в идиоматичный Swift: sealed classes → Swift enums, coroutines → async/await, Flow → AsyncSequence, Kotlin nullability → Swift optionals. iOS-разработчики видят KMP как обычную Swift-библиотеку.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Первый проект | [[kmp-getting-started]] | Создать работающий KMP-проект за 30 минут |
| Структура проекта | [[kmp-project-structure]] | Понять source sets, Gradle конфигурацию |
| Shared UI | [[compose-mp-overview]] | Изучить Compose Multiplatform для кросс-платформенного UI |
| Архитектура | [[kmp-architecture-patterns]] | Clean Architecture, MVI, MVVM в мультиплатформенном контексте |
| CS: компиляция | [[compilation-pipeline]] | Понять, как Kotlin компилируется в разные target'ы |
| CS: нативная компиляция | [[native-compilation-llvm]] | Почему Kotlin/Native даёт near-native performance на iOS |
| Корутины | [[kotlin-coroutines]] | Асинхронное программирование — основа networking и data layer в KMP |
