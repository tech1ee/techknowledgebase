---
title: "KMP Debugging: LLDB, Xcode, Crash Reporting"
created: 2026-01-04
modified: 2026-01-04
tags:
  - topic/jvm
  - topic/kmp
  - debugging
  - lldb
  - xcode
  - crashlytics
  - topic/ios
  - topic/android
  - type/concept
  - level/advanced
related:
  - "[[kmp-memory-management]]"
  - "[[kmp-ios-deep-dive]]"
  - "[[kmp-testing-strategies]]"
prerequisites:
  - "[[kmp-getting-started]]"
  - "[[kmp-ios-deep-dive]]"
  - "[[kmp-testing-strategies]]"
cs-foundations:
  - "[[compilation-pipeline]]"
  - "[[native-compilation-llvm]]"
  - "[[memory-model-fundamentals]]"
status: published
---

# KMP Debugging

> **TL;DR:** LLDB для iOS (xcode-kotlin plugin обязателен!), Android Studio Debugger для Android. Breakpoints работают, expression evaluation — нет. Crash reporting: CrashKiOS + Firebase Crashlytics с отдельной загрузкой dSYM. Kotlin исключения плохо пробрасываются в Swift — используй Result types вместо throw. KDoctor для проверки setup.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Compilation Pipeline** | Понять debug symbols | [[compilation-pipeline]] |
| **Native/LLVM** | Как работает DWARF info | [[native-compilation-llvm]] |
| KMP Architecture | Структура проекта | [[kmp-project-structure]] |
| Memory Management | Для memory debugging | [[kmp-memory-management]] |

> **Важно:** Понимание compilation pipeline и debug symbols поможет эффективнее использовать LLDB и понять ограничения iOS debugging.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **LLDB** | Low Level Debugger от Apple | Детектив, исследующий место преступления |
| **dSYM** | Debug Symbol file | Словарь для перевода машинного кода в читаемый |
| **Symbolication** | Преобразование адресов в код | Расшифровка шифра — адрес → файл:строка |
| **Breakpoint** | Точка остановки в коде | Стоп-кран в поезде |
| **DWARF** | Debug info format | Формат хранения отладочной информации |
| **Frame** | Stack frame в отладчике | Кадр фильма — состояние в момент времени |

---

## Почему iOS debugging сложнее

### Проблема двух debugger'ов

Android использует JVM-based debugging (JDWP), оптимизированный для Kotlin/Java. iOS использует LLDB, который разработан для C/C++/Objective-C/Swift. Kotlin/Native компилируется в native code, и LLDB видит его как C89 код.

**Результат:**
- Expression evaluation не работает (LLDB не понимает Kotlin синтаксис)
- Coroutines отображаются криво (LLDB не знает про suspend/resume)
- Переменные могут показываться как `ObjHeader*` вместо типа

### DWARF и debug symbols

Kotlin/Native генерирует DWARF 2 debug info. DWARF — это формат хранения отладочной информации (соответствие адресов → файл:строка). До DWARF 5 не было идентификатора для Kotlin, поэтому он маркируется как C89.

**Важно:** dSYM файл = debug symbols для symbolication. Без него crash reports бесполезны (только адреса, не код).

### xcode-kotlin как решение

Touchlab создал xcode-kotlin plugin, который:
- Форматирует Kotlin объекты для отображения в Xcode
- Показывает List, Map, StateFlow красиво
- Работает в Swift, Kotlin и Objective-C коде
- Версия 2.0 в 5x быстрее предыдущей

### Сравнение debugging experience

| Feature | Android | iOS |
|---------|---------|-----|
| Breakpoints | ✅ Полная поддержка | ✅ Работает |
| Step into/over | ✅ Полная поддержка | ✅ Работает |
| Variables view | ✅ Полная поддержка | ⚠️ Требует xcode-kotlin |
| Expression eval | ✅ Полная поддержка | ❌ Не работает |
| Coroutines debug | ✅ С плагином | ⚠️ Ограничено |

---

## Инструменты отладки

```
┌─────────────────────────────────────────────────────────────┐
│              KMP DEBUGGING TOOLS                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ANDROID                         iOS                       │
│   ─────────                       ───                       │
│                                                             │
│   ┌─────────────────┐            ┌─────────────────┐        │
│   │ Android Studio  │            │ Xcode           │        │
│   │ Debugger        │            │ + xcode-kotlin  │        │
│   │                 │            │ + LLDB          │        │
│   │ ✅ Full support │            │ ⚠️ Limited     │        │
│   │ ✅ Expressions  │            │ ❌ Expressions  │        │
│   │ ✅ Coroutines   │            │ ⚠️ Coroutines  │        │
│   └─────────────────┘            └─────────────────┘        │
│                                                             │
│   COMMON TOOLS                                              │
│   ────────────                                              │
│   • KDoctor — проверка окружения                            │
│   • Kermit — logging                                        │
│   • CrashKiOS — crash reporting                             │
│   • Firebase Crashlytics                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Android Debugging

### Android Studio Setup

```kotlin
// 1. Убедись что используешь Debug build
// Build Variants → выбери *Debug variant

// 2. Поставь breakpoint (click на gutter)

// 3. Run → Debug (Shift+F9)

// 4. Используй Debug panel:
// - Variables: просмотр переменных
// - Watches: отслеживание выражений
// - Frames: call stack
// - Console: evaluate expressions
```

### Debugging Shared Module

```kotlin
// В shared module:
// commonMain/kotlin/com/example/Repository.kt

class UserRepository {
    suspend fun getUser(id: String): User {
        // ← Ставь breakpoint здесь
        val response = api.fetchUser(id)
        return response.toUser()
    }
}

// Debugging из Android app:
// 1. Открой shared module в Android Studio
// 2. Поставь breakpoint в shared code
// 3. Debug Android app
// 4. Breakpoint сработает при вызове shared кода
```

### Evaluate Expression

```kotlin
// В Debug Console (Evaluate Expression — Alt+F8):

// Можно:
user.name
user.copy(name = "New Name")
listOf(1, 2, 3).filter { it > 1 }

// Нельзя:
// - Вызывать suspend functions напрямую
// - Модифицировать некоторые final переменные
```

---

## 2. iOS Debugging с LLDB

### Установка xcode-kotlin

```bash
# ОБЯЗАТЕЛЬНО для iOS debugging!
# Homebrew установка:
brew install xcode-kotlin

# Или manual:
# https://github.com/touchlab/xcode-kotlin

# Проверка установки:
xcode-kotlin info
```

### LLDB Basics

```lldb
# Breakpoints

# По файлу и строке:
(lldb) b -f UserRepository.kt -l 15
Breakpoint 1: where = shared`kfun:UserRepository.getUser...

# По имени функции:
(lldb) b -n kfun:com.example.UserRepository.getUser(kotlin.String)

# По regex (для лямбд с #):
(lldb) b -r getUser

# Список breakpoints:
(lldb) br list

# Удалить breakpoint:
(lldb) br delete 1
```

### Variable Inspection

```lldb
# Просмотр переменных в текущем frame:
(lldb) fr var
(ObjHeader *) user = User(id=123, name="John")
(int) count = 5

# Конкретная переменная:
(lldb) v user
(ObjHeader *) user = User(id=123, name="John")

# Поле объекта:
(lldb) v user->name
(ObjHeader *) user->name = "John"

# С xcode-kotlin: красивый вывод Kotlin объектов
# List, Map отображаются корректно
```

### Stepping Commands

```lldb
# Step over (не входить в функцию):
(lldb) n
# или F6 в Xcode

# Step into (войти в функцию):
(lldb) s
# или F7 в Xcode

# Step out (выйти из функции):
(lldb) finish
# или F8 в Xcode

# Continue (продолжить выполнение):
(lldb) c
# или F5 в Xcode
```

### Xcode Workflow

```
┌─────────────────────────────────────────────────────────────┐
│              XCODE DEBUGGING WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   1. Build shared framework with debug info                 │
│      ./gradlew :shared:linkDebugFrameworkIosSimulatorArm64  │
│                                                             │
│   2. Open iOS project in Xcode                              │
│                                                             │
│   3. Navigate to Kotlin source file                         │
│      (если xcode-kotlin установлен — файлы видны)           │
│                                                             │
│   4. Set breakpoint (click on gutter)                       │
│                                                             │
│   5. Run with debugging (⌘R)                                │
│                                                             │
│   6. When breakpoint hits:                                  │
│      - Variables pane shows Kotlin objects                  │
│      - Use stepping commands                                │
│      - Console for LLDB commands                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Expression Evaluation (Ограничения)

### Что НЕ работает

```kotlin
// ⚠️ Expression evaluation НЕ поддерживается в LLDB для Kotlin!

// Нельзя:
// (lldb) expr user.name.uppercase()  ❌
// (lldb) expr repository.getUser("123")  ❌
// (lldb) expr listOf(1, 2, 3)  ❌

// Можно только смотреть существующие переменные:
// (lldb) v user  ✅
// (lldb) v user->name  ✅
```

### Workaround: Debug Logging

```kotlin
// Добавь временные print statements:

class UserRepository {
    suspend fun getUser(id: String): User {
        println("DEBUG: getUser called with id=$id")  // Temporary

        val response = api.fetchUser(id)
        println("DEBUG: response=$response")  // Temporary

        return response.toUser()
    }
}

// Или используй Kermit для structured logging
```

---

## 4. Crash Reporting

### CrashKiOS Setup

```kotlin
// build.gradle.kts (shared module)
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("co.touchlab.crashkios:crashlytics:0.9.1")
        }
    }
}
```

```kotlin
// commonMain/kotlin/CrashReporting.kt
import co.touchlab.crashkios.crashlytics.CrashlyticsKotlin
import co.touchlab.crashkios.crashlytics.setCrashlyticsUnhandledExceptionHook

// При старте приложения:
fun initCrashReporting() {
    setCrashlyticsUnhandledExceptionHook()
}

// Для ручного logging:
fun logError(throwable: Throwable) {
    CrashlyticsKotlin.logException(throwable)
}

// Custom keys:
fun setUserContext(userId: String) {
    CrashlyticsKotlin.setCustomValue("user_id", userId)
}

// Breadcrumbs:
fun logEvent(event: String) {
    CrashlyticsKotlin.log(event)
}
```

### Firebase Crashlytics dSYM Upload

```bash
# Проблема: Kotlin framework dSYM не загружается автоматически

# Решение: отдельный Build Phase в Xcode

# Xcode → Project → Build Phases → + → New Run Script Phase
# Name: "Upload Kotlin dSYM"

# Script:
"${PODS_ROOT}/FirebaseCrashlytics/upload-symbols" \
    -gsp "${PROJECT_DIR}/GoogleService-Info.plist" \
    -p ios \
    "${BUILT_PRODUCTS_DIR}/${FRAMEWORKS_FOLDER_PATH}/Shared.framework.dSYM"
```

```
┌─────────────────────────────────────────────────────────────┐
│              CRASHLYTICS dSYM FLOW                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   BUILD TIME                                                │
│   ──────────                                                │
│   1. Kotlin compiler generates Shared.framework.dSYM       │
│   2. Xcode build phase uploads to Firebase                  │
│                                                             │
│   CRASH TIME                                                │
│   ──────────                                                │
│   1. App crashes in Kotlin code                             │
│   2. CrashKiOS captures Kotlin stack trace                  │
│   3. Stack trace sent to Crashlytics                        │
│   4. Firebase symbolicates using uploaded dSYM              │
│   5. Dashboard shows: UserRepository.kt:15                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Stack Trace без CrashKiOS

```
// БЕЗ CrashKiOS — бесполезный crash:
Thread 0 Crashed:
0   libsystem_kernel.dylib    0x00007fff6123 __pthread_kill + 10
1   libsystem_pthread.dylib   0x00007fff6124 pthread_kill + 263
2   shared                    0x00000001234 konan::abort() + 44
3   shared                    0x00000001235 ThrowException + 112
...

// С CrashKiOS — читаемый stack:
kotlin.IllegalStateException: User not found
    at com.example.UserRepository.getUser(UserRepository.kt:15)
    at com.example.ViewModel.loadUser(ViewModel.kt:42)
    at com.example.Screen.onAppear(Screen.kt:23)
```

---

## 5. Exception Handling Best Practices

### Проблема: Kotlin → Swift Exceptions

```kotlin
// ❌ ПЛОХО: исключения теряются при переходе в Swift

// Kotlin:
class Repository {
    @Throws(Exception::class)
    fun getData(): String {
        throw IllegalStateException("Something went wrong")
    }
}

// Swift:
// do {
//     let data = try repository.getData()
// } catch {
//     // error не содержит полную информацию!
//     // stack trace потерян
// }
```

### Решение: Result Types

```kotlin
// ✅ ХОРОШО: используй sealed class для результата

// commonMain/kotlin/Result.kt
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(
        val message: String,
        val stackTrace: String? = null
    ) : Result<Nothing>()
}

// Repository:
class Repository {
    fun getData(): Result<String> {
        return try {
            val data = api.fetchData()
            Result.Success(data)
        } catch (e: Exception) {
            Result.Error(
                message = e.message ?: "Unknown error",
                stackTrace = e.stackTraceToString()  // Сохраняем!
            )
        }
    }
}

// Swift side:
// switch repository.getData() {
// case let success as ResultSuccess<NSString>:
//     print(success.data)
// case let error as ResultError:
//     print(error.message)
//     logError(error.stackTrace)  // Полный stack trace!
// }
```

### Kermit для Logging

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("co.touchlab:kermit:2.0.4")
            implementation("co.touchlab:kermit-crashlytics:2.0.4")
        }
    }
}
```

```kotlin
// commonMain/kotlin/Logging.kt
import co.touchlab.kermit.Logger
import co.touchlab.kermit.crashlytics.CrashlyticsLogWriter

// Setup:
fun initLogging() {
    Logger.addLogWriter(CrashlyticsLogWriter())
}

// Usage:
class UserRepository {
    private val log = Logger.withTag("UserRepository")

    suspend fun getUser(id: String): User {
        log.d { "Fetching user: $id" }

        return try {
            val user = api.fetchUser(id)
            log.i { "User fetched: ${user.name}" }
            user
        } catch (e: Exception) {
            log.e(e) { "Failed to fetch user: $id" }
            throw e
        }
    }
}
```

---

## 6. Environment Setup

### KDoctor

```bash
# Проверка KMP окружения
brew install kdoctor

kdoctor

# Пример вывода:
# Environment diagnose (to see all details, use -v option):
# [✓] Operation System
# [✓] Java
# [✓] Android Studio
# [✓] Xcode
# [✓] CocoaPods
# [✓] Ruby
# [!] Xcode license  ← Нужно принять лицензию

# Исправление:
sudo xcodebuild -license accept
```

### Common Setup Issues

```bash
# Issue: iOS devices не видны в Android Studio
# Причина: Vision Pro simulator
# Решение: удалить Vision Pro simulator

# Issue: "Building for iOS Simulator, but framework was built for iOS"
# Решение:
./gradlew clean
# Пересобрать framework

# Issue: Xcode не видит Kotlin исходники
# Решение: установить xcode-kotlin
brew install xcode-kotlin

# Issue: Breakpoints не срабатывают
# Проверь: Debug build, не Release
./gradlew :shared:linkDebugFrameworkIosSimulatorArm64
```

### gradle.properties для Debug

```properties
# gradle.properties

# Debug символы для iOS
kotlin.native.cocoapods.generate.wrapper=true

# Не оптимизировать (быстрее билд, лучше debug)
# НЕ используй в production!
kotlin.native.cacheKind=none

# Подробные логи
org.gradle.logging.level=debug
```

---

## 7. Debugging Coroutines

### Проблема

```kotlin
// Coroutine stack traces часто обрезаются или теряются

suspend fun problematicFunction() {
    withContext(Dispatchers.Default) {
        // ← Stack trace может потеряться здесь
        throw IllegalStateException("Error!")
    }
}
```

### Решение: Debug Mode

```kotlin
// При разработке включи debug mode:

// JVM (Android):
// -Dkotlinx.coroutines.debug=on

// Или в коде:
System.setProperty("kotlinx.coroutines.debug", "on")

// Даёт полные stack traces для coroutines
```

### Try-Catch в Coroutines

```kotlin
// ✅ Ловим ошибки близко к источнику

class ViewModel {
    private val _state = MutableStateFlow<UiState>(UiState.Loading)

    fun loadData() {
        viewModelScope.launch {
            _state.value = try {
                val data = repository.getData()
                UiState.Success(data)
            } catch (e: Exception) {
                // Логируем с полным stack trace
                Logger.e(e) { "Failed to load data" }
                UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}
```

---

## 8. Remote Debugging

### Real-Time Logger

```kotlin
// KMP RealTime Logger для отладки на устройстве

// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("io.github.kdroidfilter:kmp-realtime-logger:1.0.0")
        }
    }
}

// Usage:
RealTimeLogger.init(
    appName = "MyApp",
    broadcastEnabled = true  // Broadcast в локальную сеть
)

RealTimeLogger.d("Debug message")
RealTimeLogger.e("Error", exception)

// На компьютере:
// Слушать broadcast и видеть логи в реальном времени
```

### Print Debugging

```kotlin
// Классический но эффективный подход:

fun debugFunction() {
    println(">>> ENTER debugFunction")
    println(">>> param1=$param1, param2=$param2")

    // ... код ...

    println(">>> EXIT debugFunction, result=$result")
}

// Для iOS: NSLog доступен через expect/actual
expect fun debugLog(message: String)

// iosMain:
actual fun debugLog(message: String) {
    NSLog(message)
}
```

---

## Best Practices

### Debugging Strategy

```kotlin
// 1. Android first
// - Легче отлаживать в Android Studio
// - Полная поддержка expression evaluation
// - Потом проверяй на iOS

// 2. Используй logging
// - Kermit для structured logging
// - CrashKiOS для crash reporting
// - Логи помогают когда debugger не работает

// 3. Result types вместо exceptions
// - Сохраняют stack trace
// - Работают через Swift boundary
// - Явное error handling

// 4. Unit tests
// - Легче дебажить изолированно
// - Не нужен simulator/device
// - runTest для coroutines
```

### Checklist

```markdown
## Pre-Debug Checklist

### Environment
- [ ] KDoctor проходит без ошибок
- [ ] xcode-kotlin установлен
- [ ] Xcode обновлён и лицензия принята
- [ ] Android Studio с KMP plugin

### Build
- [ ] Используешь Debug variant
- [ ] Framework собран с debug info
- [ ] dSYM загружен (для crash reporting)

### Tools
- [ ] CrashKiOS настроен
- [ ] Kermit logging работает
- [ ] Breakpoints в правильных местах
```

---

## Troubleshooting

### Breakpoints не срабатывают

```bash
# 1. Проверь Debug vs Release
./gradlew :shared:tasks | grep -i link
# Должен быть linkDebug*, не linkRelease*

# 2. Пересобери
./gradlew clean
./gradlew :shared:linkDebugFrameworkIosSimulatorArm64

# 3. В Xcode: Product → Clean Build Folder (Shift+Cmd+K)
```

### Переменные не видны

```bash
# 1. Установи xcode-kotlin
brew install xcode-kotlin

# 2. Проверь что framework с debug symbols
# dSYM файл должен быть рядом с framework

# 3. В LLDB:
(lldb) image list
# Проверь что shared.framework загружен с symbols
```

### Crash reports без symbolication

```bash
# 1. Проверь dSYM upload
# Crashlytics dashboard → должен показать symbols

# 2. Добавь Build Phase для Kotlin dSYM
# См. секцию "Firebase Crashlytics dSYM Upload"

# 3. Проверь что UUID совпадают
dwarfdump --uuid Shared.framework.dSYM
# Должен совпадать с тем что в crash report
```

---

## Мифы и заблуждения

### Миф 1: "iOS debugging в KMP невозможен"

**Реальность:** Breakpoints и stepping работают отлично. Проблема только в expression evaluation (нельзя выполнять Kotlin код в LLDB). С xcode-kotlin plugin переменные отображаются корректно. Для большинства задач этого достаточно.

### Миф 2: "Android Studio может отлаживать iOS полностью"

**Реальность:** Android Studio может отлаживать Kotlin код при запуске на iOS target, но это работает через LLDB, не через JDWP. Те же ограничения, что и в Xcode. Expression evaluation не работает в любом случае.

### Миф 3: "dSYM генерируется только для Release"

**Реальность:** Kotlin/Native генерирует debug info и для Debug builds. dSYM автоматически создаётся для Release binaries. Debug builds имеют встроенную debug info. Проблема обычно в том, что dSYM не загружается в Crashlytics — нужен отдельный build phase.

### Миф 4: "CrashKiOS обязателен для crash reporting"

**Реальность:** CrashKiOS улучшает Kotlin stack traces в crash reports, но базовый crash reporting работает и без него. Без CrashKiOS ты увидишь native stack trace с `konan::abort()`, но не увидишь Kotlin exception message и stack.

### Миф 5: "@Throws делает исключения идентичными Swift"

**Реальность:** @Throws позволяет Swift ловить исключения через try/catch, но stack trace теряется при переходе границы. Для полной информации используй Result types с сохранением stackTraceToString().

---

## Рекомендуемые источники

### Official Documentation

| Источник | Описание |
|----------|----------|
| [Native Debugging](https://kotlinlang.org/docs/native-debugging.html) | LLDB commands, DWARF info |
| [iOS Symbolication](https://kotlinlang.org/docs/native-ios-symbolication.html) | dSYM и crash reports |

### Tools (Touchlab)

| Инструмент | Назначение |
|------------|-----------|
| [xcode-kotlin](https://github.com/touchlab/xcode-kotlin) | Xcode plugin для Kotlin |
| [CrashKiOS](https://crashkios.touchlab.co/) | Улучшенный crash reporting |
| [Kermit](https://kermit.touchlab.co/) | Multiplatform logging |

### JetBrains Tools

| Инструмент | Назначение |
|------------|-----------|
| [KDoctor](https://github.com/Kotlin/kdoctor) | Environment check |
| KMP Plugin 2025 | Cross-language debugging |

### CS-фундамент

| Источник | Зачем |
|----------|-------|
| [[compilation-pipeline]] | Понять debug symbols |
| [[native-compilation-llvm]] | DWARF и LLDB

---

## Связь с другими темами

- **[[kmp-memory-management]]** — Отладка утечек памяти в KMP требует понимания взаимодействия двух моделей управления памятью: tracing GC Kotlin/Native и ARC Swift. Без этих знаний вы не сможете интерпретировать результаты Xcode Instruments и диагностировать mixed retain cycles. Многие «необъяснимые» краши на iOS связаны именно с некорректным управлением памятью на границе Kotlin-Swift.

- **[[kmp-ios-deep-dive]]** — Глубокое понимание iOS-интеграции необходимо для эффективной отладки: как устроен framework, как работает dSYM-символикация, почему LLDB видит Kotlin как C89. Проблемы с breakpoints, невидимыми переменными и отсутствием expression evaluation напрямую связаны с особенностями компиляции Kotlin/Native через LLVM. Этот материал объясняет архитектурные причины ограничений iOS-отладки.

- **[[kmp-testing-strategies]]** — Юнит-тесты в commonTest — первая линия обороны против багов, и часто более эффективный инструмент отладки, чем debugger. Когда expression evaluation недоступен на iOS, изолированные тесты с runTest позволяют воспроизвести и исследовать проблему без симулятора. Стратегия «debug Android first, test common, verify iOS» основана на взаимодополняемости отладки и тестирования.

## Источники и дальнейшее чтение

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive.* — Глубокое понимание корутин критично для отладки асинхронного кода в KMP. Книга объясняет, почему stack traces обрезаются при переключении контекста, как работает structured concurrency и как правильно обрабатывать CancellationException — частая причина крашей при переходе Kotlin→Swift.

- Moskala M. (2021). *Effective Kotlin.* — Практические рекомендации по обработке ошибок (Item: Prefer Kotlin Result), которые напрямую применимы к стратегии Result types вместо exceptions на границе Kotlin-Swift. Помогает писать код, который легче отлаживать.

- Martin R. (2017). *Clean Architecture.* — Принцип разделения ответственности между слоями упрощает отладку: если баг в Repository, вы точно знаете, где ставить breakpoints. Чистая архитектура делает код предсказуемым и диагностируемым.

---

*Проверено: 2026-01-09 | xcode-kotlin 2.0, CrashKiOS 0.9.1, Kermit 2.0.4*
