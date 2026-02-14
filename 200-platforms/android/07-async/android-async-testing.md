---
title: "Тестирование асинхронного кода в Android"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - type/deep-dive
  - level/advanced
related:
  - "[[kotlin-testing]]"
  - "[[android-testing]]"
  - "[[android-coroutines-guide]]"
  - "[[android-flow-guide]]"
  - "[[kotlin-coroutines]]"
prerequisites:
  - "[[android-coroutines-guide]]"
  - "[[kotlin-testing]]"
reading_time: 45
difficulty: 6
study_status: not_started
mastery: 0
---

# Тестирование асинхронного кода в Android

Тесты асинхронного кода -- самые хрупкие тесты в Android-проекте. `kotlinx-coroutines-test` предоставляет виртуальное время и детерминистичные диспетчеры, **Turbine** делает тестирование Flow декларативным, а `MainDispatcherRule` решает проблему `Dispatchers.Main` в unit-тестах. Без понимания этой инфраструктуры каждый flaky-тест превращается в часы бессмысленной отладки.

> **Prerequisites:**
> - [[android-coroutines-guide]] -- понимание корутин, Dispatcher, structured concurrency
> - [[kotlin-testing]] -- JUnit 5, MockK, базовые паттерны тестирования
> - [[kotlin-coroutines]] -- suspend функции, CoroutineScope, Job, cancellation

---

## Зачем это нужно

Асинхронный код по своей природе недетерминирован: порядок выполнения, тайминги и переключение потоков зависят от рантайма. Это создает уникальные проблемы при тестировании:

**Проблемы без правильной инфраструктуры:**
- **Flaky тесты** -- проходят 9 из 10 запусков, падают на CI в самый неудачный момент
- **Зависание тестов** -- забытый `advanceUntilIdle()` или бесконечный Flow-коллектор блокирует тест навсегда
- **Crash на `Dispatchers.Main`** -- unit-тест на JVM не имеет Main Looper, любое обращение к `Dispatchers.Main` падает с `IllegalStateException`
- **Ложные срабатывания** -- тест проходит не потому что код работает правильно, а потому что `UnconfinedTestDispatcher` скрыл timing bug

**Масштаб проблемы:**
Типичный Android-проект на Clean Architecture имеет 60-80% кода с suspend-функциями и Flow. Без инструментов тестирования корутин невозможно покрыть тестами основную бизнес-логику.

**Эволюция инструментов:** До kotlinx-coroutines-test 1.6 (2022) тестирование корутин было хаотичным: `TestCoroutineDispatcher`, `TestCoroutineScope`, `runBlockingTest` -- всё это deprecated. Текущий API (`runTest`, `StandardTestDispatcher`, `UnconfinedTestDispatcher`) стабилен с 1.6 и является единственным рекомендованным подходом. Если вы встречаете в коде `runBlockingTest` или `TestCoroutineDispatcher` -- это legacy, требующее миграции.

### Актуальность 2025-2026

| Версия | Изменение | Влияние на тесты |
|--------|-----------|------------------|
| kotlinx.coroutines 1.9+ | Стабилизация `backgroundScope` | Тестирование фоновых корутин без `UncompletedCoroutinesError` |
| Turbine 1.1+ | `turbineScope`, улучшенная обработка ошибок | Eager reporting failed Turbines, `testIn` требует `turbineScope` |
| Kotlin 2.0+ | Новый K2 compiler | Улучшенная производительность компиляции тестов |
| MockK 1.13+ | Полная поддержка Kotlin 2.0 | `coEvery`/`coVerify` без проблем с K2 |
| JUnit 5.11+ | Параллельные тесты | Тесты с `runTest` безопасно параллелятся |
| Compose 1.7+ | `collectAsStateWithLifecycle()` | Новые паттерны тестирования Compose UI |

---

## TL;DR

| Задача | Инструмент | Пример |
|--------|------------|--------|
| Тестирование suspend-функций | `runTest { }` | `runTest { val result = repo.getData() }` |
| Контроль виртуального времени | `advanceTimeBy()`, `advanceUntilIdle()` | `advanceTimeBy(1000); runCurrent()` |
| Замена `Dispatchers.Main` | `MainDispatcherRule` | `@get:Rule val rule = MainDispatcherRule()` / JUnit 5 Extension |
| Тестирование Flow | Turbine `test { }` | `flow.test { assertEquals(expected, awaitItem()) }` |
| Тестирование StateFlow | `.value` или Turbine | `assertEquals(expected, viewModel.state.value)` |
| Мокирование suspend | MockK `coEvery` | `coEvery { repo.get() } returns data` |
| Фоновые корутины | `backgroundScope` | `backgroundScope.launch { ... }` |
| CoroutineWorker | `TestListenableWorkerBuilder` | `builder.build().doWork()` |

**Правило:** для простых тестов -- `UnconfinedTestDispatcher` + `.value` assertions. Для сложных сценариев с таймингами -- `StandardTestDispatcher` + Turbine + `advanceTimeBy`.

**Минимальный набор для старта:** `kotlinx-coroutines-test` + Turbine + MockK. Этих трёх библиотек достаточно для покрытия 95% сценариев async-тестирования в Android.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Kotlin Coroutines** | suspend, Dispatcher, Job, Scope | [[kotlin-coroutines]] |
| **Kotlin Flow** | Cold/Hot Flow, StateFlow, SharedFlow | [[kotlin-flow]] |
| **JUnit 5** | TestRule, Extension, lifecycle аннотации | [[kotlin-testing]] |
| **MockK** | coEvery, coVerify, slot | [[kotlin-testing]] |
| **MVVM / Clean Architecture** | ViewModel, UseCase, Repository | [[android-architecture-patterns]] |
| **Structured Concurrency** | Иерархия Job, cancellation, SupervisorJob | [[android-coroutines-guide]] |

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **`runTest`** | Coroutine builder для тестов. Создает `TestScope`, автоматически пропускает `delay()`, контролирует виртуальное время |
| **`TestScope`** | Специальный `CoroutineScope` с `TestCoroutineScheduler`. Предоставляет `advanceTimeBy()`, `advanceUntilIdle()`, `backgroundScope` |
| **`TestCoroutineScheduler`** | Управляет виртуальным временем. Все `TestDispatcher` в одном тесте должны разделять один scheduler |
| **`StandardTestDispatcher`** | Не выполняет корутины сразу -- ставит в очередь. Требует явного `advanceUntilIdle()`. По умолчанию в `runTest` |
| **`UnconfinedTestDispatcher`** | Выполняет корутины eagerly на текущем потоке. Проще в использовании, но скрывает timing bugs |
| **Virtual Time** | Механизм `TestCoroutineScheduler`, позволяющий `delay(10_000)` выполняться мгновенно. Контролируется через `advanceTimeBy()` |
| **`backgroundScope`** | Scope внутри `TestScope` для корутин, которые не завершаются самостоятельно. Автоматически cancel при завершении теста |
| **`MainDispatcherRule`** | JUnit Rule/Extension, заменяющий `Dispatchers.Main` на `TestDispatcher`. Обязателен для тестов ViewModel |
| **Turbine** | Библиотека Cash App для тестирования Flow. Превращает push-based Flow в pull-based `awaitItem()` API |
| **`awaitItem()`** | Suspend-функция Turbine. Ожидает следующий элемент из Flow с таймаутом (по умолчанию 3 секунды) |
| **`turbineScope`** | DSL-функция Turbine для тестирования нескольких Flow одновременно. Обеспечивает eager reporting ошибок |
| **`coEvery` / `coVerify`** | MockK-функции для мокирования и верификации suspend-функций |

---

## Инфраструктура тестирования

### Зависимости (Gradle)

```kotlin
// build.gradle.kts
dependencies {
    // Coroutines testing -- виртуальное время, TestDispatcher, runTest
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.9.0")

    // Turbine для тестирования Flow -- awaitItem(), test {}
    testImplementation("app.cash.turbine:turbine:1.1.0")

    // MockK -- мокирование suspend функций, final классов
    testImplementation("io.mockk:mockk:1.13.12")

    // JUnit 5 -- основной фреймворк тестирования
    testImplementation("org.junit.jupiter:junit-jupiter:5.11.0")

    // WorkManager testing -- TestListenableWorkerBuilder
    testImplementation("androidx.work:work-testing:2.9.1")

    // Kotlin test assertions (опционально, улучшает читаемость)
    testImplementation("org.jetbrains.kotlin:kotlin-test-junit5")
}
```

**Совместимость версий:** `kotlinx-coroutines-test` должен иметь ту же версию, что и основной `kotlinx-coroutines-core`. Несовпадение версий приводит к `NoClassDefFoundError` или `NoSuchMethodError` в рантайме тестов.

### Общая картина: что тестируем и чем

```
ViewModel
  └── viewModelScope (Dispatchers.Main)     → MainDispatcherRule
  └── StateFlow / SharedFlow                → Turbine или .value
  └── suspend fun в dependencies            → coEvery / coVerify

Repository
  └── suspend fun (сеть + кеш)             → runTest { }
  └── Flow (observe паттерн)               → Turbine test { }
  └── Room DAO Flow                        → inMemoryDatabaseBuilder + Turbine

UseCase
  └── operator fun invoke(): Flow           → Turbine test { }
  └── suspend operator fun invoke()         → runTest { }
  └── combine / merge                       → MutableStateFlow + Turbine

WorkManager
  └── CoroutineWorker.doWork()             → TestListenableWorkerBuilder
```

### kotlinx-coroutines-test: основа всего

Библиотека `kotlinx-coroutines-test` предоставляет три ключевых компонента: `runTest`, `TestDispatcher`, и `TestCoroutineScheduler`.

#### runTest: виртуальное время и автоматический advance

`runTest` -- это coroutine builder, созданный специально для тестов. Он:
1. Создает `TestScope` с `StandardTestDispatcher` по умолчанию
2. Автоматически пропускает вызовы `delay()` (виртуальное время)
3. После завершения тела теста вызывает `advanceUntilIdle()` для всех запущенных корутин
4. Выбрасывает `UncompletedCoroutinesError` если есть незавершенные корутины (не в `backgroundScope`)

```kotlin
@Test
fun `runTest automatically skips delays`() = runTest {
    val start = currentTime  // виртуальное время = 0

    delay(10_000)  // НЕ ждёт 10 секунд реального времени

    val elapsed = currentTime - start
    assertEquals(10_000, elapsed)  // виртуальное время = 10000
    // Реальное время выполнения: ~миллисекунды
}
```

**Важно:** `runTest` автоматически advance'ит только корутины, запущенные в `TestScope`. Корутины на других диспетчерах (например, `Dispatchers.IO`) не контролируются виртуальным временем.

**Что происходит внутри runTest:**
1. Создается `TestScope` с `StandardTestDispatcher` и `TestCoroutineScheduler`
2. Тело теста выполняется как suspend-функция внутри `TestScope`
3. После завершения тела вызывается `advanceUntilIdle()` для очистки очереди
4. Если остались незавершенные корутины (не в `backgroundScope`) -- выбрасывается `UncompletedCoroutinesError`
5. Проверяется, не было ли необработанных исключений в дочерних корутинах

#### TestCoroutineScheduler: общий scheduler

Все `TestDispatcher` в одном тесте должны разделять один `TestCoroutineScheduler`. Внутри `runTest` scheduler доступен через свойство `testScheduler`:

```kotlin
@Test
fun `shared scheduler across dispatchers`() = runTest {
    // Оба диспетчера разделяют один scheduler
    val ioDispatcher = StandardTestDispatcher(testScheduler)
    val defaultDispatcher = StandardTestDispatcher(testScheduler)

    var result1 = ""
    var result2 = ""

    launch(ioDispatcher) {
        delay(1000)
        result1 = "done from io"
    }

    launch(defaultDispatcher) {
        delay(500)
        result2 = "done from default"
    }

    advanceTimeBy(500)
    runCurrent()
    assertEquals("", result1)
    assertEquals("done from default", result2)

    advanceTimeBy(500)
    runCurrent()
    assertEquals("done from io", result1)
}
```

#### backgroundScope: для вечных корутин

Когда тестируемый код запускает корутины, которые не завершаются самостоятельно (например, бесконечный `collect`), используйте `backgroundScope`:

```kotlin
@Test
fun `backgroundScope prevents UncompletedCoroutinesError`() = runTest {
    val messages = mutableListOf<String>()

    // Без backgroundScope: UncompletedCoroutinesError
    // С backgroundScope: корутина автоматически cancel при завершении теста
    backgroundScope.launch {
        flow {
            emit("first")
            delay(1000)
            emit("second")
            // Flow никогда не завершается...
            delay(Long.MAX_VALUE)
        }.collect { messages.add(it) }
    }

    advanceTimeBy(1500)
    runCurrent()
    assertEquals(listOf("first", "second"), messages)
    // Тест завершается: backgroundScope cancel'ит корутину
}
```

### StandardTestDispatcher

`StandardTestDispatcher` -- дефолтный диспетчер в `runTest`. Он **не выполняет** корутины сразу, а ставит их в очередь планировщика. Это дает полный контроль над порядком и моментом выполнения.

```kotlin
@Test
fun `StandardTestDispatcher requires explicit advancing`() = runTest {
    // runTest использует StandardTestDispatcher по умолчанию
    var executed = false

    launch {
        executed = true
    }

    // Корутина ещё НЕ выполнена!
    assertFalse(executed)

    // Явно продвигаем планировщик
    advanceUntilIdle()

    // Теперь выполнена
    assertTrue(executed)
}
```

**Методы управления выполнением:**

| Метод | Поведение |
|-------|-----------|
| `advanceUntilIdle()` | Выполняет все корутины до полного завершения |
| `advanceTimeBy(ms)` | Продвигает виртуальное время на `ms` миллисекунд. **Не выполняет** задачи, запланированные точно на `currentTime + ms` |
| `runCurrent()` | Выполняет все задачи, запланированные на текущий момент виртуального времени |
| `testScheduler.advanceTimeBy(ms)` | То же что `advanceTimeBy`, но через scheduler напрямую |

**Важная деталь `advanceTimeBy`:**

```kotlin
@Test
fun `advanceTimeBy does not run tasks at exact target time`() = runTest {
    var executed = false

    launch {
        delay(1000)
        executed = true
    }

    advanceTimeBy(1000)
    // executed все еще false! Задача запланирована на time=1000,
    // но advanceTimeBy(1000) двигает время ДО 1000, не включая

    runCurrent()  // Теперь выполняет задачу на time=1000
    assertTrue(executed)

    // Альтернатива: advanceTimeBy(1001) -- сдвигает за 1000
}
```

**Когда использовать:** сложные тесты с таймингами, тестирование debounce/throttle, проверка порядка выполнения, тестирование timeout-логики.

**Типичный паттерн: тестирование retry с exponential backoff:**

```kotlin
@Test
fun `retry with exponential backoff`() = runTest {
    var attempts = 0

    val result = retryWithBackoff(maxRetries = 3) {
        attempts++
        if (attempts < 3) throw IOException("Fail #$attempts")
        "success"
    }

    assertEquals("success", result)
    assertEquals(3, attempts)
    // Виртуальное время: 1000 + 2000 = 3000ms (backoff delays)
    assertEquals(3000, currentTime)
}

// Тестируемая функция
suspend fun <T> retryWithBackoff(
    maxRetries: Int,
    initialDelay: Long = 1000,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay
    repeat(maxRetries - 1) {
        try {
            return block()
        } catch (e: IOException) {
            delay(currentDelay)
            currentDelay = (currentDelay * factor).toLong()
        }
    }
    return block()  // Последняя попытка
}
```

### UnconfinedTestDispatcher

`UnconfinedTestDispatcher` выполняет корутины **eagerly** на текущем потоке, без постановки в очередь. Это упрощает простые тесты, но жертвует детерминизмом.

```kotlin
@Test
fun `UnconfinedTestDispatcher executes eagerly`() = runTest(
    UnconfinedTestDispatcher()
) {
    var executed = false

    launch {
        executed = true
    }

    // Корутина уже выполнена -- eager execution!
    assertTrue(executed)
    // Не нужен advanceUntilIdle()
}
```

**Ключевое отличие:**

```kotlin
// StandardTestDispatcher (по умолчанию в runTest)
@Test
fun `standard - order matters`() = runTest {
    val results = mutableListOf<Int>()
    launch { results.add(1) }
    launch { results.add(2) }
    results.add(3)
    advanceUntilIdle()
    assertEquals(listOf(3, 1, 2), results)  // 3 добавлен первым!
}

// UnconfinedTestDispatcher
@Test
fun `unconfined - eager execution`() = runTest(
    UnconfinedTestDispatcher()
) {
    val results = mutableListOf<Int>()
    launch { results.add(1) }  // Выполняется сразу
    launch { results.add(2) }  // Выполняется сразу
    results.add(3)
    assertEquals(listOf(1, 2, 3), results)
}
```

**Когда использовать:** простые тесты без сложных таймингов, тестирование ViewModel с `MainDispatcherRule`, когда не важен порядок выполнения корутин.

**Опасность:** `UnconfinedTestDispatcher` может скрыть реальные баги:

```kotlin
// Этот тест пройдёт с UnconfinedTestDispatcher, но код может
// иметь race condition в production:
@Test
fun `unconfined hides timing bug`() = runTest(
    UnconfinedTestDispatcher()
) {
    var state = "initial"

    launch {
        state = "loading"
        delay(100)
        state = "loaded"
    }

    // С Unconfined: state уже "loading" (eager)
    // В production: state может быть "initial" (async)
    assertEquals("loading", state)
}
```

### Сравнительная таблица диспетчеров

| Характеристика | StandardTestDispatcher | UnconfinedTestDispatcher |
|---------------|----------------------|--------------------------|
| Выполнение | В очередь, по запросу | Eagerly, сразу |
| Детерминизм | Полный контроль | Нет гарантий порядка |
| Требует `advance*` | Да | Нет |
| По умолчанию в `runTest` | Да | Нет |
| Скрывает timing bugs | Нет | Да |
| Сложность | Выше | Ниже |
| Подходит для | Сложные сценарии, concurrency | Простые unit-тесты |

### MainDispatcherRule

ViewModel использует `viewModelScope`, который привязан к `Dispatchers.Main`. На JVM нет Main Looper, поэтому любой тест ViewModel без подмены `Dispatchers.Main` упадет:

```
Exception in thread "Test worker" java.lang.IllegalStateException:
  Module with the Main dispatcher had failed to initialize.
```

#### JUnit 4 -- TestRule

```kotlin
class MainDispatcherRule(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {

    override fun starting(description: Description) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}

// Использование
class MyViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun `test with main dispatcher`() = runTest {
        val viewModel = MyViewModel(FakeRepository())
        viewModel.loadData()
        advanceUntilIdle()
        assertEquals(expected, viewModel.uiState.value)
    }
}
```

#### JUnit 5 -- Extension

```kotlin
class MainDispatcherExtension(
    private val testDispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : BeforeEachCallback, AfterEachCallback {

    override fun beforeEach(context: ExtensionContext?) {
        Dispatchers.setMain(testDispatcher)
    }

    override fun afterEach(context: ExtensionContext?) {
        Dispatchers.resetMain()
    }
}

// Использование
@ExtendWith(MainDispatcherExtension::class)
class MyViewModelTest {

    @Test
    fun `test with main dispatcher`() = runTest {
        val viewModel = MyViewModel(FakeRepository())
        viewModel.loadData()
        advanceUntilIdle()
        assertEquals(expected, viewModel.uiState.value)
    }
}
```

#### Альтернатива: базовый класс

```kotlin
abstract class CoroutineTestBase {
    @BeforeEach
    fun setupDispatcher() {
        Dispatchers.setMain(UnconfinedTestDispatcher())
    }

    @AfterEach
    fun tearDownDispatcher() {
        Dispatchers.resetMain()
    }
}

class MyViewModelTest : CoroutineTestBase() {
    // Dispatchers.Main уже подменён
}
```

**Важно:** `MainDispatcherRule` по умолчанию использует `UnconfinedTestDispatcher`. Если нужен `StandardTestDispatcher` для конкретного теста, передайте его явно:

```kotlin
@get:Rule
val mainDispatcherRule = MainDispatcherRule(StandardTestDispatcher())
```

### Инжекция диспетчеров -- ключ к тестируемости

Прямое использование `Dispatchers.IO` в коде делает его трудно тестируемым. Правильный подход -- инжекция через конструктор:

```kotlin
// ПЛОХО: жестко привязан к Dispatchers.IO
class UserRepository {
    suspend fun getUser(id: String): User = withContext(Dispatchers.IO) {
        api.getUser(id)
    }
}

// ПРАВИЛЬНО: диспетчер инжектируется
class UserRepository(
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    suspend fun getUser(id: String): User = withContext(ioDispatcher) {
        api.getUser(id)
    }
}

// В тесте:
@Test
fun `test with injected dispatcher`() = runTest {
    val testDispatcher = StandardTestDispatcher(testScheduler)
    val repository = UserRepository(ioDispatcher = testDispatcher)

    // Теперь IO-операции контролируются виртуальным временем
    val user = repository.getUser("1")
    assertEquals("John", user.name)
}
```

Этот паттерн рекомендован Google в официальной документации Android и особенно важен для Repository и UseCase слоев, где `withContext(Dispatchers.IO)` встречается повсеместно.

---

## Тестирование ViewModel

ViewModel -- центральный компонент Android-архитектуры и самый частый объект тестирования. Все ViewModel-тесты требуют `MainDispatcherRule`.

### Тестирование StateFlow

#### Подход 1: Прямое чтение `.value`

Самый простой подход -- проверять текущее значение StateFlow после действия. Google рекомендует этот подход для большинства случаев, так как StateFlow conflated (промежуточные значения могут быть пропущены):

```kotlin
// Продакшн-код
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UserUiState>(UserUiState.Initial)
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UserUiState.Loading
            try {
                val user = repository.getUser(userId)
                _uiState.value = UserUiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UserUiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

sealed interface UserUiState {
    data object Initial : UserUiState
    data object Loading : UserUiState
    data class Success(val user: User) : UserUiState
    data class Error(val message: String) : UserUiState
}
```

```kotlin
// Тест
@ExtendWith(MainDispatcherExtension::class)
class UserViewModelTest {

    private val repository = mockk<UserRepository>()
    private lateinit var viewModel: UserViewModel

    @BeforeEach
    fun setup() {
        viewModel = UserViewModel(repository)
    }

    @Test
    fun `loadUser success updates state`() = runTest {
        // Given
        val expectedUser = User(id = "1", name = "John")
        coEvery { repository.getUser("1") } returns expectedUser

        // When
        viewModel.loadUser("1")
        advanceUntilIdle()

        // Then
        assertEquals(
            UserUiState.Success(expectedUser),
            viewModel.uiState.value
        )
    }

    @Test
    fun `loadUser error updates state`() = runTest {
        // Given
        coEvery { repository.getUser("1") } throws IOException("Network error")

        // When
        viewModel.loadUser("1")
        advanceUntilIdle()

        // Then
        assertEquals(
            UserUiState.Error("Network error"),
            viewModel.uiState.value
        )
    }
}
```

#### Подход 2: Turbine для проверки переходов состояний

Когда важно проверить **все** промежуточные состояния (Loading -> Success), используйте Turbine. Но помните: StateFlow conflated, поэтому быстрые переходы могут быть пропущены:

```kotlin
@Test
fun `loadUser emits loading then success`() = runTest {
    val expectedUser = User(id = "1", name = "John")
    coEvery { repository.getUser("1") } returns expectedUser

    viewModel.uiState.test {
        // StateFlow всегда эмитит текущее значение первым
        assertEquals(UserUiState.Initial, awaitItem())

        viewModel.loadUser("1")

        assertEquals(UserUiState.Loading, awaitItem())
        assertEquals(UserUiState.Success(expectedUser), awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Проблема conflation с StateFlow:**

StateFlow объединяет (conflates) быстрые обновления. Если Loading и Success эмитятся без suspension point между ними, коллектор может пропустить Loading. Решение:

```kotlin
@Test
fun `handle conflation -- skip intermediate states`() = runTest {
    coEvery { repository.getUser("1") } returns User("1", "John")

    viewModel.uiState.test {
        assertEquals(UserUiState.Initial, awaitItem())

        viewModel.loadUser("1")

        // Если Loading был conflated, получим сразу Success
        val finalState = expectMostRecentItem()
        assertTrue(finalState is UserUiState.Success)

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование SharedFlow events

`SharedFlow` часто используется для one-time events (навигация, снэкбары). В отличие от StateFlow, он не хранит текущее значение:

```kotlin
// Продакшн-код
class OrderViewModel(
    private val orderRepository: OrderRepository
) : ViewModel() {

    private val _events = MutableSharedFlow<OrderEvent>()
    val events: SharedFlow<OrderEvent> = _events.asSharedFlow()

    fun placeOrder(order: Order) {
        viewModelScope.launch {
            try {
                orderRepository.placeOrder(order)
                _events.emit(OrderEvent.OrderPlaced(order.id))
            } catch (e: Exception) {
                _events.emit(OrderEvent.OrderFailed(e.message ?: "Error"))
            }
        }
    }
}

sealed interface OrderEvent {
    data class OrderPlaced(val orderId: String) : OrderEvent
    data class OrderFailed(val message: String) : OrderEvent
}
```

```kotlin
// Тест
@Test
fun `placeOrder emits OrderPlaced event`() = runTest {
    val order = Order(id = "123", items = listOf())
    coEvery { orderRepository.placeOrder(order) } returns Unit

    viewModel.events.test {
        viewModel.placeOrder(order)

        assertEquals(OrderEvent.OrderPlaced("123"), awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

**Важно:** с `SharedFlow` надо начать коллекцию **до** вызова действия. Иначе событие будет потеряно, так как у SharedFlow (с replay=0) нет буфера.

**Распространенная ошибка с SharedFlow:**

```kotlin
// ПЛОХО: событие теряется
@Test
fun `event lost without prior collection`() = runTest {
    val viewModel = OrderViewModel(repository)

    // Действие выполняется ДО начала коллекции
    viewModel.placeOrder(order)
    advanceUntilIdle()

    viewModel.events.test {
        // Событие OrderPlaced уже было эмитировано и потеряно!
        // Тест зависнет на awaitItem() (таймаут 3 сек)
    }
}

// ПРАВИЛЬНО: коллекция начинается ДО действия
@Test
fun `event captured with prior collection`() = runTest {
    val viewModel = OrderViewModel(repository)

    viewModel.events.test {
        viewModel.placeOrder(order)  // Действие ПОСЛЕ начала коллекции

        assertEquals(OrderEvent.OrderPlaced("123"), awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```

### Тестирование параллельных операций

```kotlin
// Продакшн: при новом запросе старый отменяется
class SearchViewModel(
    private val searchRepository: SearchRepository
) : ViewModel() {

    private val _results = MutableStateFlow<List<String>>(emptyList())
    val results: StateFlow<List<String>> = _results.asStateFlow()

    private var searchJob: Job? = null

    fun search(query: String) {
        searchJob?.cancel()
        searchJob = viewModelScope.launch {
            delay(300)  // debounce
            val data = searchRepository.search(query)
            _results.value = data
        }
    }
}
```

```kotlin
// Тест: проверяем debounce и cancellation
@ExtendWith(MainDispatcherExtension::class)
class SearchViewModelTest {

    @Test
    fun `rapid search cancels previous and debounces`() = runTest {
        val repository = mockk<SearchRepository>()
        coEvery { repository.search("ab") } returns listOf("abc", "abd")
        coEvery { repository.search("abc") } returns listOf("abcd")

        val viewModel = SearchViewModel(repository)

        // Быстрый ввод: "ab" затем "abc"
        viewModel.search("ab")
        advanceTimeBy(100)  // 100ms < 300ms debounce

        viewModel.search("abc")
        advanceTimeBy(300)
        runCurrent()

        // Только "abc" должен был выполниться
        assertEquals(listOf("abcd"), viewModel.results.value)

        // "ab" не должен был вызвать repository
        coVerify(exactly = 0) { repository.search("ab") }
        coVerify(exactly = 1) { repository.search("abc") }
    }

    @Test
    fun `search after debounce delay executes`() = runTest {
        val repository = mockk<SearchRepository>()
        coEvery { repository.search("hello") } returns listOf("hello world")

        val viewModel = SearchViewModel(repository)

        viewModel.search("hello")
        advanceTimeBy(300)
        runCurrent()

        assertEquals(listOf("hello world"), viewModel.results.value)
    }
}
```

### Мокирование зависимостей

#### coEvery / coVerify для suspend-функций

```kotlin
// Мокирование suspend функции
val repository = mockk<UserRepository>()

// Успешный ответ
coEvery { repository.getUser("1") } returns User("1", "John")

// Ошибка
coEvery { repository.getUser("999") } throws NotFoundException("Not found")

// Последовательные ответы
coEvery { repository.getUser("1") } returnsMany listOf(
    User("1", "John"),
    User("1", "John Updated")
)

// Задержка в моке
coEvery { repository.getUser("1") } coAnswers {
    delay(1000)  // Симулируем сетевой запрос
    User("1", "John")
}

// Верификация
coVerify(exactly = 1) { repository.getUser("1") }
coVerify(ordering = Ordering.SEQUENCE) {
    repository.getUser("1")
    repository.saveUser(any())
}
```

#### Мокирование Flow-возвращающих функций

```kotlin
// Мок с flowOf
coEvery { repository.observeUsers() } returns flowOf(
    listOf(User("1", "John")),
    listOf(User("1", "John"), User("2", "Jane"))
)

// Мок с MutableStateFlow для управляемых эмиссий
val fakeUsersFlow = MutableStateFlow(emptyList<User>())
every { repository.observeUsers() } returns fakeUsersFlow

@Test
fun `react to user updates`() = runTest {
    val viewModel = UsersViewModel(repository)

    viewModel.users.test {
        assertEquals(emptyList(), awaitItem())

        // Симулируем обновление данных
        fakeUsersFlow.value = listOf(User("1", "John"))
        assertEquals(listOf(User("1", "John")), awaitItem())

        // Ещё обновление
        fakeUsersFlow.value = listOf(User("1", "John"), User("2", "Jane"))
        assertEquals(2, awaitItem().size)

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Полный пример теста ViewModel

```kotlin
// Продакшн-код
class ArticlesViewModel(
    private val getArticlesUseCase: GetArticlesUseCase,
    private val bookmarkUseCase: BookmarkArticleUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(ArticlesUiState())
    val uiState: StateFlow<ArticlesUiState> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<ArticlesEvent>()
    val events: SharedFlow<ArticlesEvent> = _events.asSharedFlow()

    init {
        loadArticles()
    }

    private fun loadArticles() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            getArticlesUseCase()
                .catch { e ->
                    _uiState.update {
                        it.copy(isLoading = false, error = e.message)
                    }
                }
                .collect { articles ->
                    _uiState.update {
                        it.copy(isLoading = false, articles = articles, error = null)
                    }
                }
        }
    }

    fun bookmarkArticle(articleId: String) {
        viewModelScope.launch {
            try {
                bookmarkUseCase(articleId)
                _events.emit(ArticlesEvent.BookmarkSaved)
            } catch (e: Exception) {
                _events.emit(ArticlesEvent.BookmarkFailed(e.message ?: "Error"))
            }
        }
    }
}

data class ArticlesUiState(
    val isLoading: Boolean = false,
    val articles: List<Article> = emptyList(),
    val error: String? = null
)

sealed interface ArticlesEvent {
    data object BookmarkSaved : ArticlesEvent
    data class BookmarkFailed(val message: String) : ArticlesEvent
}
```

```kotlin
// Полный тест
@ExtendWith(MainDispatcherExtension::class)
class ArticlesViewModelTest {

    private val getArticlesUseCase = mockk<GetArticlesUseCase>()
    private val bookmarkUseCase = mockk<BookmarkArticleUseCase>()

    private val fakeArticles = listOf(
        Article("1", "Kotlin 2.0", "Content..."),
        Article("2", "Compose", "Content...")
    )

    @Test
    fun `init loads articles successfully`() = runTest {
        // Given
        coEvery { getArticlesUseCase() } returns flowOf(fakeArticles)

        // When
        val viewModel = ArticlesViewModel(getArticlesUseCase, bookmarkUseCase)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals(fakeArticles, state.articles)
        assertNull(state.error)
    }

    @Test
    fun `init handles error`() = runTest {
        // Given
        coEvery { getArticlesUseCase() } returns flow {
            throw IOException("Network error")
        }

        // When
        val viewModel = ArticlesViewModel(getArticlesUseCase, bookmarkUseCase)
        advanceUntilIdle()

        // Then
        val state = viewModel.uiState.value
        assertFalse(state.isLoading)
        assertEquals("Network error", state.error)
    }

    @Test
    fun `bookmarkArticle emits success event`() = runTest {
        // Given
        coEvery { getArticlesUseCase() } returns flowOf(fakeArticles)
        coEvery { bookmarkUseCase("1") } returns Unit

        val viewModel = ArticlesViewModel(getArticlesUseCase, bookmarkUseCase)
        advanceUntilIdle()

        // When & Then
        viewModel.events.test {
            viewModel.bookmarkArticle("1")
            assertEquals(ArticlesEvent.BookmarkSaved, awaitItem())
            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `bookmarkArticle emits failure event on error`() = runTest {
        // Given
        coEvery { getArticlesUseCase() } returns flowOf(fakeArticles)
        coEvery { bookmarkUseCase("1") } throws IOException("Save failed")

        val viewModel = ArticlesViewModel(getArticlesUseCase, bookmarkUseCase)
        advanceUntilIdle()

        // When & Then
        viewModel.events.test {
            viewModel.bookmarkArticle("1")

            val event = awaitItem()
            assertTrue(event is ArticlesEvent.BookmarkFailed)
            assertEquals("Save failed", (event as ArticlesEvent.BookmarkFailed).message)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

## Тестирование Repository

Repository -- слой доступа к данным. Тесты Repository проверяют корректную координацию между сетью, кешем и БД.

### Тестирование suspend-функций

```kotlin
// Продакшн-код
class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {

    override suspend fun getUser(id: String): User {
        return try {
            val networkUser = api.getUser(id)
            dao.insertUser(networkUser.toEntity())
            networkUser
        } catch (e: IOException) {
            dao.getUserById(id)?.toUser()
                ?: throw NoDataException("No cached data for user $id")
        }
    }
}
```

```kotlin
// Тест
class UserRepositoryTest {

    private val api = mockk<UserApi>()
    private val dao = mockk<UserDao>(relaxed = true)
    private val repository = UserRepositoryImpl(api, dao)

    @Test
    fun `getUser returns network data and caches`() = runTest {
        // Given
        val networkUser = User("1", "John")
        coEvery { api.getUser("1") } returns networkUser

        // When
        val result = repository.getUser("1")

        // Then
        assertEquals(networkUser, result)
        coVerify { dao.insertUser(networkUser.toEntity()) }
    }

    @Test
    fun `getUser falls back to cache on network error`() = runTest {
        // Given
        coEvery { api.getUser("1") } throws IOException("No network")
        coEvery { dao.getUserById("1") } returns UserEntity("1", "Cached John")

        // When
        val result = repository.getUser("1")

        // Then
        assertEquals("Cached John", result.name)
    }

    @Test
    fun `getUser throws NoDataException when no cache`() = runTest {
        // Given
        coEvery { api.getUser("1") } throws IOException("No network")
        coEvery { dao.getUserById("1") } returns null

        // When & Then
        assertThrows<NoDataException> {
            repository.getUser("1")
        }
    }
}
```

### Тестирование Flow-возвращающих функций

```kotlin
// Продакшн: cache-then-network паттерн
class ProductRepository(
    private val api: ProductApi,
    private val dao: ProductDao
) {
    fun observeProducts(): Flow<List<Product>> = flow {
        // 1. Сначала кеш
        val cached = dao.getAllProducts()
        if (cached.isNotEmpty()) {
            emit(cached.map { it.toProduct() })
        }

        // 2. Потом сеть
        try {
            val fresh = api.getProducts()
            dao.insertAll(fresh.map { it.toEntity() })
            emit(fresh)
        } catch (e: IOException) {
            if (cached.isEmpty()) throw e
            // Если есть кеш -- молча проглатываем ошибку сети
        }
    }
}
```

```kotlin
// Тест с Turbine
class ProductRepositoryTest {

    private val api = mockk<ProductApi>()
    private val dao = mockk<ProductDao>(relaxed = true)
    private val repository = ProductRepository(api, dao)

    @Test
    fun `observeProducts emits cache then network`() = runTest {
        // Given
        val cachedProducts = listOf(ProductEntity("1", "Cached"))
        val freshProducts = listOf(Product("1", "Fresh"), Product("2", "New"))

        coEvery { dao.getAllProducts() } returns cachedProducts
        coEvery { api.getProducts() } returns freshProducts

        // When & Then
        repository.observeProducts().test {
            // Первая эмиссия -- кеш
            val cached = awaitItem()
            assertEquals(1, cached.size)
            assertEquals("Cached", cached[0].name)

            // Вторая эмиссия -- свежие данные
            val fresh = awaitItem()
            assertEquals(2, fresh.size)
            assertEquals("Fresh", fresh[0].name)

            awaitComplete()
        }
    }

    @Test
    fun `observeProducts emits only cache on network error`() = runTest {
        // Given
        val cachedProducts = listOf(ProductEntity("1", "Cached"))
        coEvery { dao.getAllProducts() } returns cachedProducts
        coEvery { api.getProducts() } throws IOException("Offline")

        // When & Then
        repository.observeProducts().test {
            val cached = awaitItem()
            assertEquals(1, cached.size)

            awaitComplete()  // Flow завершается без ошибки (кеш есть)
        }
    }

    @Test
    fun `observeProducts throws when no cache and network error`() = runTest {
        // Given
        coEvery { dao.getAllProducts() } returns emptyList()
        coEvery { api.getProducts() } throws IOException("Offline")

        // When & Then
        repository.observeProducts().test {
            awaitError()  // Flow завершается с ошибкой
        }
    }
}
```

### Тестирование Room DAO с Flow

Для интеграционных тестов Room DAO используйте `inMemoryDatabaseBuilder`:

```kotlin
@ExtendWith(MainDispatcherExtension::class)
class UserDaoTest {

    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @BeforeEach
    fun setup() {
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        ).allowMainThreadQueries().build()

        userDao = database.userDao()
    }

    @AfterEach
    fun tearDown() {
        database.close()
    }

    @Test
    fun `observe users emits on insert`() = runTest {
        // Room DAO возвращает Flow, который эмитит при изменениях
        userDao.observeAllUsers().test {
            // Начальное значение -- пустой список
            assertEquals(emptyList(), awaitItem())

            // Вставляем пользователя
            userDao.insert(UserEntity("1", "John"))

            // Flow эмитит обновленные данные
            val users = awaitItem()
            assertEquals(1, users.size)
            assertEquals("John", users[0].name)

            // Вставляем ещё
            userDao.insert(UserEntity("2", "Jane"))
            assertEquals(2, awaitItem().size)

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Fake vs Mock для асинхронных зависимостей

В async-тестировании выбор между Fake и Mock особенно важен:

```kotlin
// Fake: полная реализация для тестов
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<String, User>()
    private val _usersFlow = MutableStateFlow<List<User>>(emptyList())

    override suspend fun getUser(id: String): User {
        return users[id] ?: throw NotFoundException("User $id not found")
    }

    override fun observeUsers(): Flow<List<User>> = _usersFlow

    override suspend fun saveUser(user: User) {
        users[user.id] = user
        _usersFlow.value = users.values.toList()
    }

    // Тестовые хелперы
    fun addUser(user: User) {
        users[user.id] = user
        _usersFlow.value = users.values.toList()
    }

    fun clear() {
        users.clear()
        _usersFlow.value = emptyList()
    }
}
```

```kotlin
// Тест с Fake -- чище, не зависит от деталей MockK
@Test
fun `test with fake repository`() = runTest {
    val fakeRepo = FakeUserRepository()
    fakeRepo.addUser(User("1", "John"))

    val viewModel = UserViewModel(fakeRepo)
    advanceUntilIdle()

    assertEquals("John", (viewModel.uiState.value as UserUiState.Success).user.name)
}
```

**Когда что использовать:**
- **Fake** -- для Repository, DataSource, DAO. Лучше для интеграционных тестов, переиспользуется
- **Mock (coEvery)** -- для API-сервисов, одноразовых зависимостей. Быстрее писать для простых тестов
- **MutableStateFlow** -- для мокирования Flow-возвращающих зависимостей. Позволяет контролировать эмиссии из теста

---

## Тестирование UseCase

UseCase (Interactor) -- это единица бизнес-логики в Clean Architecture. Тестируется как чистая функция с мокированными зависимостями.

### UseCase, возвращающий Flow

```kotlin
// Продакшн-код
class ObserveFilteredProductsUseCase(
    private val productRepository: ProductRepository,
    private val preferencesRepository: PreferencesRepository
) {
    operator fun invoke(): Flow<List<Product>> {
        return combine(
            productRepository.observeProducts(),
            preferencesRepository.observeFilter()
        ) { products, filter ->
            products.filter { product ->
                when (filter) {
                    ProductFilter.ALL -> true
                    ProductFilter.IN_STOCK -> product.inStock
                    ProductFilter.ON_SALE -> product.onSale
                }
            }
        }
    }
}
```

```kotlin
// Тест
class ObserveFilteredProductsUseCaseTest {

    private val productRepo = mockk<ProductRepository>()
    private val prefsRepo = mockk<PreferencesRepository>()
    private val useCase = ObserveFilteredProductsUseCase(productRepo, prefsRepo)

    private val allProducts = listOf(
        Product("1", "A", inStock = true, onSale = false),
        Product("2", "B", inStock = false, onSale = true),
        Product("3", "C", inStock = true, onSale = true)
    )

    @Test
    fun `filters by IN_STOCK`() = runTest {
        // Given
        every { productRepo.observeProducts() } returns flowOf(allProducts)
        every { prefsRepo.observeFilter() } returns flowOf(ProductFilter.IN_STOCK)

        // When & Then
        useCase().test {
            val filtered = awaitItem()
            assertEquals(2, filtered.size)
            assertTrue(filtered.all { it.inStock })
            awaitComplete()
        }
    }

    @Test
    fun `reacts to filter change`() = runTest {
        // Given
        val filterFlow = MutableStateFlow(ProductFilter.ALL)
        every { productRepo.observeProducts() } returns flowOf(allProducts)
        every { prefsRepo.observeFilter() } returns filterFlow

        // When & Then
        useCase().test {
            // ALL filter -- все продукты
            assertEquals(3, awaitItem().size)

            // Меняем фильтр
            filterFlow.value = ProductFilter.ON_SALE
            val onSale = awaitItem()
            assertEquals(2, onSale.size)
            assertTrue(onSale.all { it.onSale })

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### UseCase с timeout

```kotlin
// Продакшн-код
class FetchWithTimeoutUseCase(
    private val api: DataApi
) {
    suspend operator fun invoke(id: String): Result<Data> {
        return try {
            val data = withTimeout(5_000) {
                api.fetchData(id)
            }
            Result.success(data)
        } catch (e: TimeoutCancellationException) {
            Result.failure(e)
        }
    }
}
```

```kotlin
// Тест
class FetchWithTimeoutUseCaseTest {

    private val api = mockk<DataApi>()
    private val useCase = FetchWithTimeoutUseCase(api)

    @Test
    fun `returns data within timeout`() = runTest {
        coEvery { api.fetchData("1") } coAnswers {
            delay(1_000)  // 1 секунда -- в пределах timeout
            Data("1", "content")
        }

        val result = useCase("1")

        assertTrue(result.isSuccess)
        assertEquals("content", result.getOrNull()?.content)
    }

    @Test
    fun `returns failure on timeout`() = runTest {
        coEvery { api.fetchData("1") } coAnswers {
            delay(10_000)  // 10 секунд -- превышает timeout 5 секунд
            Data("1", "content")
        }

        val result = useCase("1")

        assertTrue(result.isFailure)
        assertTrue(result.exceptionOrNull() is TimeoutCancellationException)
    }
}
```

### UseCase с merge для нескольких источников

```kotlin
// Продакшн-код
class ObserveNotificationsUseCase(
    private val pushRepo: PushRepository,
    private val localRepo: LocalNotificationRepository
) {
    operator fun invoke(): Flow<Notification> = merge(
        pushRepo.observePush(),
        localRepo.observeLocal()
    )
}
```

```kotlin
// Тест
@Test
fun `merges push and local notifications`() = runTest {
    val pushFlow = MutableSharedFlow<Notification>()
    val localFlow = MutableSharedFlow<Notification>()

    every { pushRepo.observePush() } returns pushFlow
    every { localRepo.observeLocal() } returns localFlow

    val useCase = ObserveNotificationsUseCase(pushRepo, localRepo)

    useCase().test {
        // Push notification
        pushFlow.emit(Notification("push", "Push msg"))
        assertEquals("Push msg", awaitItem().message)

        // Local notification
        localFlow.emit(Notification("local", "Local msg"))
        assertEquals("Local msg", awaitItem().message)

        // Оба источника работают параллельно
        pushFlow.emit(Notification("push", "Another push"))
        assertEquals("Another push", awaitItem().message)

        cancelAndIgnoreRemainingEvents()
    }
}
```

---

## Turbine: полный гайд

Turbine -- библиотека Cash App, которая превращает push-based Flow в pull-based API. Вместо коллекции и ожидания вы явно "вытягиваете" элементы через `awaitItem()`.

**Почему Turbine, а не ручная коллекция?** Без Turbine тестирование Flow требует запуска коллекции в отдельной корутине, управления таймаутами и ручной синхронизации. Turbine инкапсулирует эту сложность в один вызов `test { }`:

```kotlin
// Без Turbine -- verbose и хрупко
@Test
fun `manual flow testing - fragile`() = runTest {
    val results = mutableListOf<String>()
    val job = launch(UnconfinedTestDispatcher(testScheduler)) {
        myFlow.toList(results)
    }
    advanceUntilIdle()
    assertEquals(listOf("a", "b", "c"), results)
    job.cancel()
}

// С Turbine -- декларативно и надёжно
@Test
fun `turbine flow testing - clean`() = runTest {
    myFlow.test {
        assertEquals("a", awaitItem())
        assertEquals("b", awaitItem())
        assertEquals("c", awaitItem())
        awaitComplete()
    }
}
```

### Core API

| Метод | Описание |
|-------|----------|
| `flow.test { }` | Запускает коллекцию Flow и предоставляет API для ассертов |
| `awaitItem()` | Ожидает следующий элемент (таймаут 3 сек) |
| `awaitComplete()` | Ожидает завершение Flow |
| `awaitError()` | Ожидает ошибку из Flow |
| `expectNoEvents()` | Проверяет отсутствие событий в данный момент (без ожидания) |
| `expectMostRecentItem()` | Возвращает последний полученный элемент, игнорируя промежуточные |
| `skipItems(n)` | Пропускает `n` элементов |
| `cancelAndIgnoreRemainingEvents()` | Отменяет коллекцию, игнорирует оставшиеся |
| `cancelAndConsumeRemainingEvents()` | Отменяет и возвращает оставшиеся события |
| `ensureAllEventsConsumed()` | Проверяет, что все события обработаны |

### Базовые паттерны

#### Cold Flow

```kotlin
@Test
fun `test cold flow emissions`() = runTest {
    val myFlow = flow {
        emit(1)
        emit(2)
        emit(3)
    }

    myFlow.test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())
        assertEquals(3, awaitItem())
        awaitComplete()  // Flow завершился
    }
}
```

#### Hot Flow (StateFlow)

```kotlin
@Test
fun `StateFlow always emits current value first`() = runTest {
    val stateFlow = MutableStateFlow("initial")

    stateFlow.test {
        // StateFlow ВСЕГДА эмитит текущее значение первым
        assertEquals("initial", awaitItem())

        stateFlow.value = "updated"
        assertEquals("updated", awaitItem())

        // distinctUntilChanged: повтор того же значения не эмитится
        stateFlow.value = "updated"
        expectNoEvents()  // Ничего нового

        stateFlow.value = "changed"
        assertEquals("changed", awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

#### Тестирование порядка эмиссий

```kotlin
@Test
fun `verify emission order`() = runTest {
    val flow = flow {
        emit("loading")
        delay(100)
        emit("data")
        delay(200)
        emit("complete")
    }

    flow.test {
        assertEquals("loading", awaitItem())
        assertEquals("data", awaitItem())
        assertEquals("complete", awaitItem())
        awaitComplete()
    }
}
```

#### expectNoEvents

```kotlin
@Test
fun `no emission until trigger`() = runTest {
    val trigger = MutableSharedFlow<Unit>()
    val flow = trigger.map { "triggered" }

    flow.test {
        expectNoEvents()  // Ничего не эмитилось

        trigger.emit(Unit)
        assertEquals("triggered", awaitItem())

        expectNoEvents()  // Снова тишина

        cancelAndIgnoreRemainingEvents()
    }
}
```

### StateFlow + Turbine: distinctUntilChanged и skipItems

```kotlin
@Test
fun `skipItems for initial StateFlow value`() = runTest {
    val viewModel = MyViewModel()

    viewModel.uiState.test {
        // Пропускаем начальное значение
        skipItems(1)

        viewModel.doSomething()
        val result = awaitItem()
        assertEquals(expectedState, result)

        cancelAndIgnoreRemainingEvents()
    }
}
```

**distinctUntilChanged поведение StateFlow:**

```kotlin
@Test
fun `StateFlow skips duplicate values`() = runTest {
    val state = MutableStateFlow(0)

    state.test {
        assertEquals(0, awaitItem())

        state.value = 1
        assertEquals(1, awaitItem())

        state.value = 1  // Дубликат -- НЕ эмитится
        state.value = 1  // Дубликат -- НЕ эмитится
        state.value = 2  // Новое значение
        assertEquals(2, awaitItem())

        cancelAndIgnoreRemainingEvents()
    }
}
```

### Advanced: testIn для ручного управления

`testIn` позволяет создать `ReceiveTurbine` без блока `test { }`. Полезно для тестирования нескольких Flow одновременно:

```kotlin
@Test
fun `testIn for manual control`() = runTest {
    turbineScope {
        val flow1 = flowOf(1, 2, 3).testIn(backgroundScope)
        val flow2 = flowOf("a", "b", "c").testIn(backgroundScope)

        assertEquals(1, flow1.awaitItem())
        assertEquals("a", flow2.awaitItem())

        assertEquals(2, flow1.awaitItem())
        assertEquals("b", flow2.awaitItem())

        assertEquals(3, flow1.awaitItem())
        assertEquals("c", flow2.awaitItem())

        flow1.awaitComplete()
        flow2.awaitComplete()
    }
}
```

**Важно:** начиная с Turbine 1.1+, `testIn` требует `turbineScope`. Это гарантирует eager reporting ошибок из любого Turbine внутри скоупа.

### Несколько Turbine одновременно

```kotlin
@Test
fun `test ViewModel with state and events`() = runTest {
    val viewModel = MyViewModel()

    turbineScope {
        val stateTurbine = viewModel.uiState.testIn(backgroundScope)
        val eventsTurbine = viewModel.events.testIn(backgroundScope)

        // Начальное состояние
        assertEquals(UiState.Initial, stateTurbine.awaitItem())

        // Действие
        viewModel.performAction()

        // Проверяем и state, и event
        assertEquals(UiState.Loading, stateTurbine.awaitItem())
        assertEquals(UiState.Success, stateTurbine.awaitItem())
        assertEquals(Event.ActionCompleted, eventsTurbine.awaitItem())

        stateTurbine.cancelAndIgnoreRemainingEvents()
        eventsTurbine.cancelAndIgnoreRemainingEvents()
    }
}
```

### Настройка таймаута

По умолчанию Turbine ожидает 3 секунды. Можно изменить:

```kotlin
@Test
fun `custom timeout`() = runTest {
    slowFlow.test(timeout = 10.seconds) {
        val item = awaitItem()  // Ждёт до 10 секунд
        assertNotNull(item)
        cancelAndIgnoreRemainingEvents()
    }
}
```

**Когда увеличивать таймаут:** при тестировании Flow, который делает реальные IO-операции в интеграционных тестах (Room DAO, DataStore). В unit-тестах с виртуальным временем дефолтных 3 секунд обычно достаточно.

### Утверждения на всех оставшихся событиях

```kotlin
@Test
fun `cancelAndConsumeRemainingEvents returns remaining`() = runTest {
    flowOf(1, 2, 3, 4, 5).test {
        assertEquals(1, awaitItem())
        assertEquals(2, awaitItem())

        // Получаем оставшиеся события
        val remaining = cancelAndConsumeRemainingEvents()

        // remaining содержит Item(3), Item(4), Item(5), Complete
        assertEquals(4, remaining.size)
    }
}
```

### Turbine и runTest: взаимодействие с виртуальным временем

Turbine корректно работает с `runTest` и виртуальным временем. `delay()` внутри Flow пропускается автоматически:

```kotlin
@Test
fun `turbine respects virtual time`() = runTest {
    val flow = flow {
        emit("fast")
        delay(5_000)
        emit("after 5 seconds")
        delay(10_000)
        emit("after 15 seconds")
    }

    flow.test {
        assertEquals("fast", awaitItem())
        assertEquals("after 5 seconds", awaitItem())
        assertEquals("after 15 seconds", awaitItem())
        awaitComplete()
    }

    // Реальное время: миллисекунды
    // Виртуальное время: 15 секунд
    assertEquals(15_000, currentTime)
}
```

### Обработка ошибок Flow

```kotlin
@Test
fun `test flow error`() = runTest {
    val errorFlow = flow<String> {
        emit("ok")
        throw IllegalStateException("Something went wrong")
    }

    errorFlow.test {
        assertEquals("ok", awaitItem())

        val error = awaitError()
        assertTrue(error is IllegalStateException)
        assertEquals("Something went wrong", error.message)
    }
}
```

---

## Тестирование WorkManager

`CoroutineWorker` -- стандартный способ выполнения фоновой работы в Android. Тестируется с помощью `TestListenableWorkerBuilder`.

### Базовый тест CoroutineWorker

```kotlin
// Продакшн-код
class SyncWorker(
    context: Context,
    params: WorkerParameters,
    private val syncRepository: SyncRepository
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            syncRepository.syncAll()
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
}
```

```kotlin
// Тест
class SyncWorkerTest {

    private val context = ApplicationProvider.getApplicationContext<Context>()
    private val syncRepository = mockk<SyncRepository>()

    @Test
    fun `doWork returns success on sync completion`() = runTest {
        // Given
        coEvery { syncRepository.syncAll() } returns Unit

        val worker = TestListenableWorkerBuilder<SyncWorker>(context)
            .setWorkerFactory(SyncWorkerFactory(syncRepository))
            .build()

        // When
        val result = worker.doWork()

        // Then
        assertEquals(ListenableWorker.Result.success(), result)
        coVerify { syncRepository.syncAll() }
    }

    @Test
    fun `doWork returns retry on first failure`() = runTest {
        // Given
        coEvery { syncRepository.syncAll() } throws IOException("Sync failed")

        val worker = TestListenableWorkerBuilder<SyncWorker>(context)
            .setWorkerFactory(SyncWorkerFactory(syncRepository))
            .setRunAttemptCount(0)  // Первая попытка
            .build()

        // When
        val result = worker.doWork()

        // Then
        assertEquals(ListenableWorker.Result.retry(), result)
    }

    @Test
    fun `doWork returns failure after max retries`() = runTest {
        // Given
        coEvery { syncRepository.syncAll() } throws IOException("Sync failed")

        val worker = TestListenableWorkerBuilder<SyncWorker>(context)
            .setWorkerFactory(SyncWorkerFactory(syncRepository))
            .setRunAttemptCount(3)  // Максимум попыток
            .build()

        // When
        val result = worker.doWork()

        // Then
        assertEquals(ListenableWorker.Result.failure(), result)
    }
}
```

### WorkerFactory для DI в тестах

```kotlin
class SyncWorkerFactory(
    private val syncRepository: SyncRepository
) : WorkerFactory() {

    override fun createWorker(
        appContext: Context,
        workerClassName: String,
        workerParameters: WorkerParameters
    ): ListenableWorker? {
        return when (workerClassName) {
            SyncWorker::class.java.name ->
                SyncWorker(appContext, workerParameters, syncRepository)
            else -> null
        }
    }
}
```

### Input/Output Data

```kotlin
@Test
fun `worker processes input data and returns output`() = runTest {
    val inputData = workDataOf(
        "user_id" to "123",
        "action" to "sync_profile"
    )

    val worker = TestListenableWorkerBuilder<ProfileSyncWorker>(context)
        .setInputData(inputData)
        .setWorkerFactory(factory)
        .build()

    val result = worker.doWork()

    assertEquals(ListenableWorker.Result.success(), result)
    // Проверка output data если Worker возвращает Result.success(outputData)
}
```

### Тестирование CoroutineWorker с Progress

```kotlin
// Продакшн: воркер с прогрессом
class UploadWorker(
    context: Context,
    params: WorkerParameters,
    private val uploadService: UploadService
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val files = inputData.getStringArray("files") ?: return Result.failure()

        files.forEachIndexed { index, file ->
            uploadService.upload(file)
            setProgress(workDataOf("progress" to (index + 1) * 100 / files.size))
        }

        return Result.success(workDataOf("uploaded_count" to files.size))
    }
}
```

```kotlin
// Тест
@Test
fun `upload worker processes all files`() = runTest {
    val files = arrayOf("file1.jpg", "file2.jpg", "file3.jpg")
    coEvery { uploadService.upload(any()) } returns Unit

    val worker = TestListenableWorkerBuilder<UploadWorker>(context)
        .setInputData(workDataOf("files" to files))
        .setWorkerFactory(UploadWorkerFactory(uploadService))
        .build()

    val result = worker.doWork()

    assertEquals(ListenableWorker.Result.success(), result)
    coVerify(exactly = 3) { uploadService.upload(any()) }
}
```

**Ограничение:** `TestListenableWorkerBuilder` выполняет `doWork()` на `Dispatchers.Default`, а не на диспетчере, указанном в воркере. Это означает, что `setProgress` и `setForeground` не всегда ведут себя так же, как в production. Для полноценного тестирования прогресса используйте интеграционные тесты с `WorkManagerTestInitHelper`.

### Интеграционные тесты WorkManager

Для полных интеграционных тестов используйте `WorkManagerTestInitHelper`:

```kotlin
@Test
fun `integration test with WorkManager`() {
    val context = ApplicationProvider.getApplicationContext<Context>()

    // Инициализация тестового WorkManager
    val config = Configuration.Builder()
        .setMinimumLoggingLevel(Log.DEBUG)
        .setWorkerFactory(testWorkerFactory)
        .build()

    WorkManagerTestInitHelper.initializeTestWorkManager(context, config)

    val workManager = WorkManager.getInstance(context)

    // Создаём запрос
    val request = OneTimeWorkRequestBuilder<SyncWorker>()
        .setInputData(workDataOf("key" to "value"))
        .build()

    // Ставим в очередь
    workManager.enqueue(request).result.get()

    // Получаем info о работе
    val workInfo = workManager.getWorkInfoById(request.id).get()
    assertEquals(WorkInfo.State.ENQUEUED, workInfo.state)

    // Запускаем работу для периодических или отложенных задач
    val testDriver = WorkManagerTestInitHelper.getTestDriver(context)
    testDriver?.setAllConstraintsMet(request.id)

    // Проверяем результат
    val completedInfo = workManager.getWorkInfoById(request.id).get()
    assertEquals(WorkInfo.State.SUCCEEDED, completedInfo.state)
}
```

---

## Тестирование race conditions

Race conditions -- самые коварные баги в асинхронном коде. `StandardTestDispatcher` и `advanceTimeBy` позволяют создавать контролируемые условия для проверки таких сценариев.

#Race conditions -- самые коварные баги потому, что они проявляются недетерминированно: приложение работает нормально на тысячах устройств, но падает у конкретного пользователя с конкретным таймингом. В обычных тестах race conditions невоспроизводимы -- `StandardTestDispatcher` делает их воспроизводимыми.

### Контролируемые гонки через TestDispatcher

```kotlin
// Продакшн-код с потенциальной гонкой
class Counter {
    private var count = 0

    suspend fun increment() {
        val current = count
        delay(10)  // Симулируем IO-операцию
        count = current + 1
    }

    fun getCount() = count
}
```

```kotlin
// Тест, демонстрирующий гонку
@Test
fun `concurrent increments cause race condition`() = runTest {
    val counter = Counter()

    // Запускаем 100 параллельных increment
    val jobs = (1..100).map {
        launch {
            counter.increment()
        }
    }

    advanceUntilIdle()

    // Из-за race condition результат будет < 100
    // Это доказывает наличие бага
    assertTrue(counter.getCount() < 100)
}
```

```kotlin
// Исправленный код с Mutex
class SafeCounter {
    private val mutex = Mutex()
    private var count = 0

    suspend fun increment() {
        mutex.withLock {
            val current = count
            delay(10)
            count = current + 1
        }
    }

    fun getCount() = count
}
```

```kotlin
// Тест безопасного счетчика
@Test
fun `mutex protected counter is thread-safe`() = runTest {
    val counter = SafeCounter()

    val jobs = (1..100).map {
        launch {
            counter.increment()
        }
    }

    advanceUntilIdle()

    assertEquals(100, counter.getCount())
}
```

### Тестирование порядка операций с advanceTimeBy

```kotlin
@Test
fun `simulate interleaved operations`() = runTest {
    val results = mutableListOf<String>()

    // Операция A: 300ms
    launch {
        delay(100)
        results.add("A-start")
        delay(200)
        results.add("A-end")
    }

    // Операция B: 250ms, начинается на 50ms позже
    launch {
        delay(150)
        results.add("B-start")
        delay(100)
        results.add("B-end")
    }

    // Проверяем порядок шаг за шагом
    advanceTimeBy(100)
    runCurrent()
    assertEquals(listOf("A-start"), results)

    advanceTimeBy(50)
    runCurrent()
    assertEquals(listOf("A-start", "B-start"), results)

    advanceTimeBy(100)
    runCurrent()
    assertEquals(listOf("A-start", "B-start", "B-end"), results)

    advanceTimeBy(50)
    runCurrent()
    assertEquals(listOf("A-start", "B-start", "B-end", "A-end"), results)
}
```

### Stress tests: repeat(N) для поиска race conditions

```kotlin
@Test
fun `stress test - concurrent map access`() = runTest {
    // Повторяем тест много раз для обнаружения race conditions
    repeat(1000) {
        val sharedMap = mutableMapOf<String, Int>()
        val results = mutableListOf<Deferred<Unit>>()

        // Несколько корутин одновременно пишут в map
        repeat(10) { index ->
            results += async {
                sharedMap["key_$index"] = index
            }
        }

        advanceUntilIdle()
        results.forEach { it.await() }

        // Проверяем целостность данных
        assertEquals(10, sharedMap.size)
    }
}
```

### Тестирование cancellation и cleanup

```kotlin
@Test
fun `cancellation cleans up resources`() = runTest {
    var resourceAcquired = false
    var resourceReleased = false

    val job = launch {
        try {
            resourceAcquired = true
            delay(Long.MAX_VALUE)  // Бесконечная операция
        } finally {
            resourceReleased = true
        }
    }

    advanceUntilIdle()
    assertTrue(resourceAcquired)
    assertFalse(resourceReleased)

    job.cancel()
    advanceUntilIdle()

    assertTrue(resourceReleased)
}
```

### Тестирование CancellationException

Частая ошибка -- перехват `CancellationException` в `catch(e: Exception)`. Тест должен проверять, что cancellation пробрасывается корректно:

```kotlin
// Продакшн-код с багом
class BuggyRepository {
    suspend fun getData(): String {
        return try {
            delay(1000)
            api.fetch()
        } catch (e: Exception) {
            // БАГ: ловит CancellationException!
            "fallback"
        }
    }
}

// Продакшн-код без бага
class CorrectRepository {
    suspend fun getData(): String {
        return try {
            delay(1000)
            api.fetch()
        } catch (e: CancellationException) {
            throw e  // Пробрасываем!
        } catch (e: Exception) {
            "fallback"
        }
    }
}
```

```kotlin
// Тест: проверяем корректную обработку cancellation
@Test
fun `cancellation is properly propagated`() = runTest {
    val repository = CorrectRepository()

    val job = launch {
        repository.getData()
    }

    advanceTimeBy(500)  // Посередине delay
    job.cancel()
    advanceUntilIdle()

    // Job должен быть cancelled, а не completed
    assertTrue(job.isCancelled)
}
```

### Тестирование атомарных обновлений с MutableStateFlow

```kotlin
// Продакшн: атомарное обновление через update {}
class CartViewModel(
    private val cartRepository: CartRepository
) : ViewModel() {

    private val _cartState = MutableStateFlow(CartState())
    val cartState: StateFlow<CartState> = _cartState.asStateFlow()

    fun addItem(item: CartItem) {
        viewModelScope.launch {
            _cartState.update { current ->
                current.copy(items = current.items + item)
            }
            cartRepository.saveCart(_cartState.value)
        }
    }

    fun removeItem(itemId: String) {
        viewModelScope.launch {
            _cartState.update { current ->
                current.copy(items = current.items.filter { it.id != itemId })
            }
            cartRepository.saveCart(_cartState.value)
        }
    }
}
```

```kotlin
// Тест: параллельные add и remove
@Test
fun `concurrent add and remove maintain consistency`() = runTest {
    val repository = mockk<CartRepository>(relaxed = true)
    val viewModel = CartViewModel(repository)

    val item1 = CartItem("1", "Item A", 10.0)
    val item2 = CartItem("2", "Item B", 20.0)

    // Добавляем два товара
    viewModel.addItem(item1)
    viewModel.addItem(item2)
    advanceUntilIdle()

    assertEquals(2, viewModel.cartState.value.items.size)

    // Одновременно добавляем и удаляем
    viewModel.addItem(CartItem("3", "Item C", 30.0))
    viewModel.removeItem("1")
    advanceUntilIdle()

    val items = viewModel.cartState.value.items
    assertEquals(2, items.size)
    assertFalse(items.any { it.id == "1" })
    assertTrue(items.any { it.id == "3" })
}
```

---

## Распространённые ошибки в тестах

Эта секция -- каталог наиболее частых ошибок, которые допускают разработчики при тестировании async-кода. Каждая ошибка показана с "плохим" и "правильным" вариантом. Если ваш тест зависает, flaky или падает с непонятной ошибкой -- скорее всего, причина здесь.

### 1. Тест зависает: забыли advanceUntilIdle

```kotlin
// ПЛОХО: тест зависает
@Test
fun `test hangs forever`() = runTest {
    var result = ""

    launch {
        delay(1000)
        result = "done"
    }

    // Нет advanceUntilIdle() -- launch ещё не выполнен
    assertEquals("done", result)  // Fail! result == ""
}

// ПРАВИЛЬНО
@Test
fun `test completes`() = runTest {
    var result = ""

    launch {
        delay(1000)
        result = "done"
    }

    advanceUntilIdle()
    assertEquals("done", result)
}
```

### 2. Flaky: StandardTestDispatcher без advance

```kotlin
// ПЛОХО: тест иногда проходит, иногда нет
@Test
fun `flaky test`() = runTest {
    val viewModel = MyViewModel()
    viewModel.loadData()

    // Без advance: данные могут быть или не быть загружены
    assertNotNull(viewModel.data.value)  // Flaky!
}

// ПРАВИЛЬНО
@Test
fun `deterministic test`() = runTest {
    val viewModel = MyViewModel()
    viewModel.loadData()
    advanceUntilIdle()  // Гарантируем завершение

    assertNotNull(viewModel.data.value)
}
```

### 3. Missing MainDispatcherRule -- crash на Dispatchers.Main

```kotlin
// ПЛОХО: crash
@Test
fun `crash without MainDispatcherRule`() = runTest {
    val viewModel = UserViewModel(mockRepo)  // Использует viewModelScope
    viewModel.loadData()  // IllegalStateException: Module with the Main
                          // dispatcher had failed to initialize
}

// ПРАВИЛЬНО
@ExtendWith(MainDispatcherExtension::class)
class UserViewModelTest {
    @Test
    fun `works with MainDispatcherRule`() = runTest {
        val viewModel = UserViewModel(mockRepo)
        viewModel.loadData()
        advanceUntilIdle()
        // Работает!
    }
}
```

### 4. Бесконечный collect Hot Flow без отмены

```kotlin
// ПЛОХО: тест никогда не завершится
@Test
fun `infinite collection`() = runTest {
    val stateFlow = MutableStateFlow(0)

    // collect -- suspend функция, которая никогда не завершается
    // для Hot Flow
    stateFlow.collect { value ->
        assertEquals(0, value)
    }
    // Код после collect никогда не выполнится!
}

// ПРАВИЛЬНО: Turbine
@Test
fun `turbine handles hot flow`() = runTest {
    val stateFlow = MutableStateFlow(0)

    stateFlow.test {
        assertEquals(0, awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}

// ПРАВИЛЬНО: first()
@Test
fun `first terminates collection`() = runTest {
    val stateFlow = MutableStateFlow(0)
    assertEquals(0, stateFlow.first())
}
```

### 5. coEvery после launch -- неправильный порядок

```kotlin
// ПЛОХО: мок настраивается после старта корутины
@Test
fun `wrong mock order`() = runTest {
    val viewModel = MyViewModel(repository)

    viewModel.loadData()  // Уже запущена корутина

    // Мок настроен ПОСЛЕ запуска -- корутина могла уже обратиться
    // к repository и получить default (null/exception)
    coEvery { repository.getData() } returns data

    advanceUntilIdle()
    // Результат непредсказуем!
}

// ПРАВИЛЬНО: мок ДО действия
@Test
fun `correct mock order`() = runTest {
    coEvery { repository.getData() } returns data  // Сначала мок

    val viewModel = MyViewModel(repository)
    viewModel.loadData()  // Потом действие

    advanceUntilIdle()
    assertEquals(expected, viewModel.uiState.value)
}
```

### 6. Тестирование реализации вместо поведения

```kotlin
// ПЛОХО: привязка к деталям реализации
@Test
fun `tests implementation detail`() = runTest {
    viewModel.loadData()
    advanceUntilIdle()

    // Тест знает о внутренней реализации
    coVerify(exactly = 1) { repository.getData() }
    coVerify { cache.save(any()) }
    coVerify { analytics.trackLoad() }
}

// ПРАВИЛЬНО: тестируем поведение (результат)
@Test
fun `tests behavior`() = runTest {
    coEvery { repository.getData() } returns expectedData

    viewModel.loadData()
    advanceUntilIdle()

    // Проверяем результат, а не путь к нему
    assertEquals(
        UiState.Success(expectedData),
        viewModel.uiState.value
    )
}
```

### 7. UncompletedCoroutinesError из-за бесконечного Flow

```kotlin
// ПЛОХО: runTest ждёт завершения всех корутин
@Test
fun `uncompleted coroutine error`() = runTest {
    launch {
        someInfiniteFlow.collect { /* ... */ }
    }
    // UncompletedCoroutinesError: корутина не завершена
}

// ПРАВИЛЬНО: backgroundScope
@Test
fun `use backgroundScope`() = runTest {
    backgroundScope.launch {
        someInfiniteFlow.collect { /* ... */ }
    }
    // backgroundScope автоматически cancel при завершении теста
}
```

---

## Best Practices чеклист

### Структура теста

- [ ] Один `runTest` на тест, используйте expression body (`fun test() = runTest { }`)
- [ ] `MainDispatcherRule` / `MainDispatcherExtension` для всех тестов ViewModel
- [ ] Given-When-Then структура внутри теста
- [ ] Мокирование зависимостей **до** создания тестируемого объекта
- [ ] Явный `advanceUntilIdle()` после действий с `StandardTestDispatcher`

### Диспетчеры

- [ ] `StandardTestDispatcher` для тестов с таймингами (debounce, timeout, retry)
- [ ] `UnconfinedTestDispatcher` для простых тестов (загрузка данных)
- [ ] Все `TestDispatcher` в тесте разделяют один `testScheduler`
- [ ] Инжекция диспетчеров через конструктор: `class Repo(private val ioDispatcher: CoroutineDispatcher)`

### Flow-тесты

- [ ] Turbine для проверки последовательности эмиссий
- [ ] `.value` для простых проверок текущего состояния StateFlow
- [ ] `cancelAndIgnoreRemainingEvents()` в конце каждого Turbine-блока для Hot Flow
- [ ] `awaitComplete()` для Cold Flow, чтобы убедиться в завершении
- [ ] `expectMostRecentItem()` когда conflation допустима

### Моки

- [ ] `coEvery` / `coVerify` для suspend-функций (не `every` / `verify`)
- [ ] `MutableStateFlow` вместо `coEvery` для управляемых Flow-эмиссий в тестах
- [ ] `flowOf()` для простых одноразовых Flow-ответов
- [ ] Порядок: сначала `coEvery`, потом действие, потом `coVerify`

### Чего избегать

- [ ] **Не используйте** `Thread.sleep()` в корутинных тестах -- используйте виртуальное время
- [ ] **Не используйте** `runBlocking` для тестов корутин -- используйте `runTest`
- [ ] **Не используйте** `delay()` для "ожидания результата" -- используйте `advanceUntilIdle()`
- [ ] **Не мокируйте** `Flow` через `every { } returns flow { }` с side effects -- используйте `MutableStateFlow`
- [ ] **Не забывайте** `Dispatchers.resetMain()` в `@AfterEach`
- [ ] **Не тестируйте** реализацию (сколько раз вызван метод) -- тестируйте поведение (результат)

### Организация тестовых файлов

```
src/test/kotlin/com/example/
├── base/
│   ├── CoroutineTestBase.kt          // MainDispatcherExtension
│   └── TestDispatcherProvider.kt     // Инжектируемые диспетчеры
├── fakes/
│   ├── FakeUserRepository.kt
│   └── FakeProductRepository.kt
├── viewmodel/
│   ├── UserViewModelTest.kt
│   └── ArticlesViewModelTest.kt
├── repository/
│   ├── UserRepositoryTest.kt
│   └── ProductRepositoryTest.kt
├── usecase/
│   └── FilterProductsUseCaseTest.kt
└── worker/
    └── SyncWorkerTest.kt
```

**Правило именования тестов:** используйте backtick-синтаксис Kotlin для читаемых имен: `` `loadUser success updates state to Success` ``. Это позволяет при падении теста сразу понять, что именно сломалось, без разбора camelCase.

### Миграция с legacy API

Если в проекте используется deprecated `runBlockingTest`, миграция минимальна:

```kotlin
// БЫЛО (deprecated)
@Test
fun `old style`() = runBlockingTest {
    val result = repository.getData()
    assertEquals(expected, result)
}

// СТАЛО
@Test
fun `new style`() = runTest {
    val result = repository.getData()
    assertEquals(expected, result)
}
```

Ключевые изменения при миграции:
- `runBlockingTest` -> `runTest`
- `TestCoroutineDispatcher` -> `StandardTestDispatcher` / `UnconfinedTestDispatcher`
- `TestCoroutineScope` -> `TestScope` (создается автоматически в `runTest`)
- `pauseDispatcher` / `resumeDispatcher` -> `StandardTestDispatcher` + `advanceUntilIdle()`
- `cleanupTestCoroutines()` -> не нужен, `runTest` делает это автоматически

---

## CS-фундамент

| Концепция | Связь с async тестированием |
|-----------|----------------------------|
| **Determinism** | Тесты должны давать одинаковый результат при каждом запуске. `TestDispatcher` делает выполнение детерминированным, убирая зависимость от реального планировщика потоков |
| **Virtual Time** | Абстракция реального времени, позволяющая `delay(10_000)` выполняться мгновенно. Основа работы `TestCoroutineScheduler` |
| **Cooperative Scheduling** | Корутины добровольно уступают поток (suspension points). `StandardTestDispatcher` использует это: корутины выполняются только при явном advance |
| **Test Isolation** | Каждый тест независим. `Dispatchers.setMain/resetMain` обеспечивает изоляцию Main диспетчера между тестами |
| **Race Condition** | Некорректное поведение из-за недетерминированного порядка операций. `StandardTestDispatcher` + `advanceTimeBy` позволяют контролируемо воспроизводить гонки |
| **Mutual Exclusion** | `Mutex` в корутинах -- suspend-аналог `synchronized`. Тестируется через параллельные корутины с `advanceUntilIdle()` |
| **Push vs Pull Model** | Flow -- push (producer отправляет), Turbine превращает в pull (consumer запрашивает через `awaitItem`). Это классическое преобразование модели взаимодействия |
| **Conflation** | Стратегия обработки backpressure: при перегрузке промежуточные значения отбрасываются. StateFlow conflated по умолчанию, что влияет на тестирование через Turbine |

**Как CS-фундамент помогает на практике:**

Понимание *cooperative scheduling* объясняет, почему `StandardTestDispatcher` работает именно так: корутины сами решают, когда уступить поток (на каждом suspension point). Когда мы вызываем `advanceUntilIdle()`, планировщик выполняет все корутины до следующей точки suspension или завершения. Это не магия фреймворка, а фундаментальное свойство кооперативной многозадачности.

Понимание *conflation* как стратегии backpressure объясняет поведение StateFlow: когда producer быстрее consumer, промежуточные значения отбрасываются. Это не баг, а design decision для оптимизации UI-обновлений, где важно только последнее состояние.

---

## Связь с другими темами

| Тема | Связь |
|------|-------|
| [[kotlin-testing]] | Базовые инструменты: JUnit 5, MockK, Kotest. Эта статья расширяет раздел coroutine testing |
| [[android-testing]] | Пирамида тестирования, стратегии. Здесь -- конкретные паттерны async unit-тестов |
| [[kotlin-coroutines]] | Необходимый фундамент: suspend, Dispatcher, CoroutineScope, cancellation |
| [[kotlin-flow]] | Необходимый фундамент: Flow, StateFlow, SharedFlow, операторы |
| [[android-coroutines-mistakes]] | Типичные ошибки в production-коде, которые должны выявляться тестами |
| [[android-architecture-patterns]] | MVVM, Clean Architecture -- определяют структуру тестируемого кода |
| [[android-dependency-injection]] | DI обеспечивает подмену зависимостей в тестах |
| [[android-background-work]] | WorkManager, CoroutineWorker -- тестируется через `TestListenableWorkerBuilder` |

---

## Источники и дальнейшее чтение

### Книги

- Moskala M. (2022). *Kotlin Coroutines: Deep Dive* -- Ch.30 "Testing coroutines", Ch.31 "Testing Flow". Исчерпывающее руководство по `runTest`, `TestDispatcher`, виртуальному времени
- Turlcot P. (2023). *Kotlin in Action, 2nd Ed.* -- глава о тестировании корутин

### Официальная документация

- [Testing Kotlin coroutines on Android](https://developer.android.com/kotlin/coroutines/test) -- Android Developers, гайд по `runTest`, `MainDispatcherRule`, `StandardTestDispatcher` vs `UnconfinedTestDispatcher`
- [kotlinx-coroutines-test README](https://github.com/Kotlin/kotlinx.coroutines/tree/master/kotlinx-coroutines-test) -- полная документация библиотеки с примерами
- [Testing Kotlin flows on Android](https://developer.android.com/kotlin/flow/test) -- гайд по тестированию Flow, Turbine, `turbineScope`
- [Testing Worker implementation](https://developer.android.com/develop/background-work/background-tasks/testing/persistent/worker-impl) -- `TestListenableWorkerBuilder` для WorkManager

### Библиотеки

- [Turbine](https://github.com/cashapp/turbine) -- Cash App, библиотека для тестирования Flow. Документация, API reference, примеры
- [Turbine Blog Post](https://code.cash.app/flow-testing-with-turbine) -- вводная статья от авторов Turbine

### Статьи и доклады

- [Coroutine Testing Patterns](https://carrion.dev/en/posts/coroutine-testing-patterns/) -- паттерны тестирования с практическими примерами
- [The conflation problem of testing StateFlows](https://zsmb.co/conflating-stateflows/) -- zsmb.co, проблема conflation при тестировании StateFlow с Turbine
- [TestDispatcher: Become the Clock Master](https://proandroiddev.com/testdispatcher-become-the-clock-master-300c13ca46c0) -- ProAndroidDev, глубокое погружение в `TestDispatcher`
- [StandardTestDispatcher vs UnconfinedTestDispatcher](https://craigrussell.io/2022/01/19/comparing-standardtestdispatcher-and-unconfinedtestdispatcher) -- сравнение диспетчеров с примерами
- [Coroutine Testing: Controlling Time](https://kau.sh/blog/coroutine-testing-time/) -- Kaushik Gopal, управление виртуальным временем в тестах
- [Testing Android Flows in ViewModel with Turbine](https://www.droidcon.com/2023/06/14/testing-android-flows-in-viewmodel-with-turbine/) -- droidcon, практический гайд

---

## Проверь себя

1. **В чем разница между `StandardTestDispatcher` и `UnconfinedTestDispatcher`?** Когда каждый из них предпочтительнее? Что произойдет, если использовать `UnconfinedTestDispatcher` для тестирования debounce-логики?

2. **Почему тест с `StateFlow` и Turbine может получить "загадочный" пропуск промежуточных состояний?** Как conflation влияет на тестирование, и какие стратегии помогают это обойти?

3. **Что произойдет при запуске этого теста?**
```kotlin
@Test
fun `mystery test`() = runTest {
    val stateFlow = MutableStateFlow("a")
    stateFlow.test {
        stateFlow.value = "b"
        stateFlow.value = "c"
        assertEquals("a", awaitItem())
        assertEquals("c", awaitItem())
        cancelAndIgnoreRemainingEvents()
    }
}
```
Пройдет ли тест? Почему "b" может быть пропущено?

4. **Напишите тест для ViewModel**, который при вызове `retry()` должен повторить последний неуспешный запрос. Используйте `coEvery` с `returnsMany` для симуляции "первый раз -- ошибка, второй раз -- успех".

---

## Ключевые карточки

**Q:** Какой TestDispatcher используется в `runTest` по умолчанию?
**A:** `StandardTestDispatcher`. Он не выполняет корутины сразу, а ставит в очередь. Требует явного `advanceUntilIdle()` или `advanceTimeBy()` для выполнения.

---

**Q:** Зачем нужен `MainDispatcherRule` в тестах ViewModel?
**A:** На JVM нет Android Main Looper. Без `MainDispatcherRule` любое обращение к `Dispatchers.Main` (через `viewModelScope`) падает с `IllegalStateException`. Rule подменяет `Dispatchers.Main` на `TestDispatcher`.

---

**Q:** Как Turbine тестирует Flow?
**A:** Turbine превращает push-based Flow в pull-based API. Вместо коллекции в фоне вы явно вызываете `awaitItem()`, `awaitComplete()`, `awaitError()`. Таймаут по умолчанию -- 3 секунды.

---

**Q:** Что такое `backgroundScope` в `runTest`?
**A:** Scope для корутин, которые не завершаются самостоятельно (бесконечный Flow collect). Корутины в `backgroundScope` автоматически cancel при завершении теста, предотвращая `UncompletedCoroutinesError`.

---

**Q:** Почему `StateFlow.test { }` с Turbine может "пропустить" промежуточные состояния?
**A:** StateFlow conflated -- при быстрых последовательных обновлениях коллектор получает только последнее значение. Если `Loading` и `Success` устанавливаются без suspension point между ними, Turbine может не увидеть `Loading`.

---

**Q:** В чем опасность `UnconfinedTestDispatcher`?
**A:** Eager execution скрывает timing bugs. Код, который в production может иметь race condition из-за асинхронного порядка выполнения, в тесте с `UnconfinedTestDispatcher` выполняется синхронно и проходит. Баг обнаруживается только в production.

---

## Куда дальше

| Направление | Тема | Файл |
|-------------|------|------|
| **UI-тестирование** | Compose UI тесты с корутинами, `createComposeRule`, `waitForIdle` | [[android-testing]] |
| **Архитектура** | Тестируемая архитектура: инжекция диспетчеров, абстракции | [[android-architecture-patterns]] |
| **Ошибки** | Типичные ошибки корутин, которые тесты должны ловить | [[android-coroutines-mistakes]] |
| **Flow** | Глубокое понимание Flow, операторы, hot/cold | [[kotlin-flow]] |
| **Kotlin Testing** | JUnit 5, MockK, Kotest -- базовые инструменты | [[kotlin-testing]] |
| **Фоновая работа** | WorkManager, CoroutineWorker -- production patterns | [[android-background-work]] |
| **DI в тестах** | Hilt testing, подмена зависимостей для instrumented тестов | [[android-dependency-injection]] |

**Порядок изучения:**
1. Убедитесь, что понимаете основы корутин ([[kotlin-coroutines]]) и Flow ([[kotlin-flow]])
2. Изучите общие паттерны тестирования ([[kotlin-testing]])
3. Пройдите эту статью с практикой -- напишите тесты для реального проекта
4. Разберите типичные ошибки ([[android-coroutines-mistakes]]) и напишите тесты, которые их ловят
5. Переходите к UI-тестированию с Compose ([[android-testing]])
