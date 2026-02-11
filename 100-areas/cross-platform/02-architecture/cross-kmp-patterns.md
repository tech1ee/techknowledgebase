---
title: "Cross-Platform: KMP Patterns — expect/actual, SKIE, bridging"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - topic/kmp
  - expect-actual
  - skie
  - type/comparison
  - level/intermediate
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[kmp-expect-actual]]"
  - "[[kmp-getting-started]]"
related:
  - "[[kmp-expect-actual]]"
  - "[[kmp-interop-deep-dive]]"
  - "[[cross-interop]]"
---

# KMP Patterns: expect/actual, SKIE и Bridging

## TL;DR: Сравнительная таблица

| Паттерн | Когда использовать | iOS-friendly |
|---------|-------------------|--------------|
| **expect/actual** | Платформенный API | Нет |
| **interface + impl** | DI, абстракции | Да |
| **SKIE** | Swift-friendly APIs | Да |
| **Flow → Combine** | Реактивные потоки | С SKIE — да |
| **Compose Multiplatform** | Shared UI | Да |

---

## 1. expect/actual: Механизм платформенной абстракции

```kotlin
// commonMain — декларация контракта
expect fun getPlatformName(): String

expect class UUID {
    fun randomUUID(): String
}
```

```kotlin
// androidMain — реализация
actual fun getPlatformName(): String = "Android ${Build.VERSION.SDK_INT}"

actual class UUID {
    actual fun randomUUID(): String = java.util.UUID.randomUUID().toString()
}
```

```kotlin
// iosMain — реализация
import platform.Foundation.NSUUID

actual fun getPlatformName(): String = "iOS"

actual class UUID {
    actual fun randomUUID(): String = NSUUID().UUIDString()
}
```

### actual typealias для существующих классов

```kotlin
// commonMain
expect class AtomicInt(value: Int) {
    fun get(): Int
    fun incrementAndGet(): Int
}

// androidMain — typealias на существующий класс
actual typealias AtomicInt = java.util.concurrent.atomic.AtomicInteger

// iosMain — своя реализация
actual class AtomicInt actual constructor(value: Int) {
    private val atomicRef = kotlin.native.concurrent.AtomicInt(value)
    actual fun get(): Int = atomicRef.value
    actual fun incrementAndGet(): Int = atomicRef.addAndGet(1)
}
```

---

## 2. SKIE: Swift-friendly APIs

### Проблема без SKIE

```kotlin
// Kotlin sealed class
sealed class Result<T> {
    data class Success(val data: T) : Result<T>()
    data class Error(val e: Throwable) : Result<Nothing>()
}
// Swift видит: просто классы без exhaustive switch!
```

### С SKIE — нативный Swift

```swift
// Swift с SKIE — нативный enum!
switch onEnum(of: result) {
case .success(let success):
    print(success.data)
case .error(let error):
    print(error.e)
}
// Exhaustive! Компилятор проверит все кейсы
```

### suspend → async/await

```kotlin
// Kotlin
suspend fun login(email: String, password: String): AuthToken
```

```swift
// Swift с SKIE — нативный async/await!
let token = try await apiService.login(email: email, password: password)
```

---

## 3. Platform-specific Implementations

### FileSystem

```kotlin
// commonMain
expect class FileSystem {
    fun readText(path: String): String
    fun writeText(path: String, content: String)
    val documentsDirectory: String
}

// androidMain
actual class FileSystem(private val context: Context) {
    actual fun readText(path: String) = File(path).readText()
    actual fun writeText(path: String, content: String) = File(path).writeText(content)
    actual val documentsDirectory get() = context.filesDir.absolutePath
}

// iosMain
actual class FileSystem {
    actual fun readText(path: String) =
        NSString.stringWithContentsOfFile(path, NSUTF8StringEncoding, null) ?: ""
    actual fun writeText(path: String, content: String) {
        (content as NSString).writeToFile(path, true, NSUTF8StringEncoding, null)
    }
    actual val documentsDirectory get() =
        NSSearchPathForDirectoriesInDomains(NSDocumentDirectory, NSUserDomainMask, true).first() as String
}
```

### Preferences

```kotlin
// commonMain
interface Preferences {
    fun getString(key: String, default: String = ""): String
    fun putString(key: String, value: String)
}

expect fun createPreferences(name: String): Preferences

// androidMain — SharedPreferences
// iosMain — NSUserDefaults
```

### Analytics

```kotlin
// commonMain
interface Analytics {
    fun logEvent(name: String, params: Map<String, Any> = emptyMap())
    fun setUserId(userId: String?)
}

// androidMain — Firebase Analytics
// iosMain — FIRAnalytics
```

---

## 4. Compose Multiplatform для iOS

```kotlin
// commonMain — shared composable
@Composable
fun App() {
    MaterialTheme {
        Column(modifier = Modifier.fillMaxSize().padding(16.dp)) {
            Text("KMP + Compose", style = MaterialTheme.typography.headlineLarge)
        }
    }
}

// iosMain — entry point
fun MainViewController() = ComposeUIViewController { App() }
```

```swift
// Swift — интеграция
struct ComposeView: UIViewControllerRepresentable {
    func makeUIViewController(context: Context) -> UIViewController {
        MainViewControllerKt.MainViewController()
    }
    func updateUIViewController(_ uiViewController: UIViewController, context: Context) {}
}
```

---

## 5. Flow ↔ Combine Bridging

### С SKIE (рекомендуемый)

```kotlin
// Kotlin — просто возвращаем Flow
fun observeUsers(): Flow<List<User>> = usersDao.observeAll()
```

```swift
// Swift — SKIE автоматически преобразует
for await users in repository.observeUsers() {
    self.users = users
}
// Или через Combine
repository.observeUsers().asPublisher()
```

### Ручной мост (без SKIE)

```kotlin
// commonMain — wrapper для Flow
class FlowWrapper<T>(private val flow: Flow<T>) {
    fun subscribe(
        onEach: (T) -> Unit,
        onComplete: () -> Unit,
        onError: (Throwable) -> Unit
    ): Cancellable {
        val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
        scope.launch {
            try {
                flow.collect { onEach(it) }
                onComplete()
            } catch (e: Throwable) {
                onError(e)
            }
        }
        return object : Cancellable {
            override fun cancel() { scope.cancel() }
        }
    }
}

fun <T> Flow<T>.wrap(): FlowWrapper<T> = FlowWrapper(this)
```

```swift
// Swift — использование без SKIE
repository.observeUsers().wrap().subscribe(
    onEach: { users in self.users = users },
    onComplete: { },
    onError: { error in print(error) }
)
```

---

## 6. Шесть ошибок в KMP разработке

### 1. Игнорирование SKIE
```
✗ Писать ручные wrappers для Flow → Combine
✓ Добавить SKIE и получить нативный Swift опыт
```

### 2. expect/actual для всего
```
✗ expect/actual для каждой мелочи
✓ Interface + DI для бизнес-логики
✓ expect/actual только для primitives
```

### 3. Неправильные Dispatchers
```kotlin
// ✗ Dispatchers.IO не существует на iOS!
withContext(Dispatchers.IO) { ... }

// ✓ Создать expect Dispatchers
expect val ioDispatcher: CoroutineDispatcher
// androidMain: actual val ioDispatcher = Dispatchers.IO
// iosMain: actual val ioDispatcher = Dispatchers.Default
```

### 4. Memory Model (legacy)
```
✗ Мутабельные объекты между потоками (старая модель)
✓ Использовать новую memory model (Kotlin 1.7.20+)
```

### 5. Lifecycle на iOS
```
✗ CoroutineScope без отмены → memory leaks
✓ Привязывать scope к жизненному циклу ViewController
```

### 6. Огромный Framework Size
```
✗ Тащить всё в commonMain
✓ Разделять на модули, isStatic = true
```

---

## 7. Три ментальные модели

### Модель 1: Слои абстракции
```
Platform Layer (Swift/Android) — минимум логики
       ↑
Bridge Layer (expect/actual, SKIE) — только адаптация
       ↑
Shared Layer (commonMain) — максимум логики
```

### Модель 2: Контракт и реализация
```
expect = КОНТРАКТ (что нужно)
actual = РЕАЛИЗАЦИЯ (как работает на платформе)
```

### Модель 3: Мост между мирами
```
Swift World          SKIE          Kotlin World
async/await    ←────────────→    suspend
Combine        ←────────────→    Flow
enum switch    ←────────────→    sealed when
```

**Правило**: Если код уходит в Swift — используйте SKIE. Иначе вы потеряете часы на написание wrappers и адаптеров.

---

## 8. Quiz: Проверьте понимание

### Вопрос 1
```kotlin
// A: expect fun getCurrentTimestamp(): Long
// B: interface TimeProvider { fun getCurrentTimestamp(): Long }
```
**Какой вариант лучше?**

<details><summary>Ответ</summary>
A — для простых утилит, B — если нужно мокать в тестах.
</details>

### Вопрос 2
```kotlin
sealed class AuthState { ... }
fun observeAuthState(): Flow<AuthState>
```
**Как сделать Swift-friendly?**

<details><summary>Ответ</summary>
Использовать SKIE — автоматически преобразует sealed в enum и Flow в AsyncSequence.
</details>

### Вопрос 3
```kotlin
withContext(Dispatchers.IO) { api.getData() }
```
**Что не так на iOS?**

<details><summary>Ответ</summary>
Dispatchers.IO не существует на iOS! Используйте expect val ioDispatcher.
</details>

---

## Итоговая шпаргалка

| Задача | Решение |
|--------|---------|
| Платформенный API | `expect/actual` |
| Бизнес-логика с DI | `interface` + impl |
| sealed class → Swift | SKIE |
| suspend → Swift | SKIE (async/await) |
| Flow → Swift | SKIE (AsyncSequence) |
| Shared UI | Compose Multiplatform |
| Dispatchers.IO на iOS | `expect val ioDispatcher` |
| Lifecycle scope iOS | Отменять в deinit |

---

## 9. Полезные ссылки

### Связанные заметки
- [[kmp-expect-actual]] — Глубокое погружение в expect/actual
- [[kmp-ios-deep-dive]] — Особенности KMP на iOS

### Документация
- [Kotlin Multiplatform](https://kotlinlang.org/docs/multiplatform.html)
- [SKIE by Touchlab](https://skie.touchlab.co/)
- [Compose Multiplatform](https://www.jetbrains.com/lp/compose-multiplatform/)

---

## Связь с другими темами

**[[kmp-expect-actual]]** — Механизм expect/actual является ключевым строительным блоком всех KMP-паттернов, рассмотренных в этом файле. Понимание ограничений expect/actual (нельзя использовать default-параметры, ограничения на typealias) позволяет осознанно выбирать между ним и альтернативными подходами вроде interface + DI. Эта заметка даёт детальное погружение в нюансы компиляции expect/actual-деклараций на каждом таргете.

**[[kmp-interop-deep-dive]]** — Интероперабельность между Kotlin и нативными платформами определяет, насколько «чужеродным» будет выглядеть KMP-код со стороны Swift или Java. SKIE-паттерны из текущего файла решают именно проблемы interop: sealed class → enum, suspend → async/await, Flow → AsyncSequence. Глубокое понимание interop-механизмов помогает выбрать правильный bridging-подход для каждого конкретного случая.

**[[cross-interop]]** — Кросс-платформенный interop рассматривает проблему взаимодействия платформ шире, чем только KMP: FFI, C-interop, Kotlin/Native ↔ Objective-C bridging. Паттерны из текущего файла (expect/actual, SKIE, Compose Multiplatform) являются высокоуровневыми абстракциями над этими низкоуровневыми механизмами. Понимание обоих уровней помогает диагностировать проблемы производительности и совместимости при кросс-платформенной разработке.

---

## Источники и дальнейшее чтение

- **Moskala M. (2021). *Effective Kotlin*.** — Содержит лучшие практики написания идиоматичного Kotlin-кода, что критически важно для проектирования API в commonMain. Паттерны из книги (sealed class hierarchies, extension functions, DSL builders) напрямую применяются при создании кросс-платформенных абстракций.
- **Martin R. (2017). *Clean Architecture*.** — Принципы разделения ответственности и инверсии зависимостей лежат в основе выбора между expect/actual и interface + DI. Книга объясняет, почему бизнес-логика должна быть в commonMain, а платформенные детали — за абстракцией.
- **Gamma E. et al. (1994). *Design Patterns*.** — Bridge, Adapter и Factory Method — это именно те паттерны, которые реализуются через expect/actual и interface + impl в KMP. Книга даёт теоретический фундамент для понимания, когда какой паттерн применять.
