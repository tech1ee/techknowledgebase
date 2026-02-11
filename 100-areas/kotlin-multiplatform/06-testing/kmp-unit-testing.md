---
title: "Unit Testing в KMP: kotlin.test, Kotest, Turbine"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - testing
  - unit-tests
  - kotest
  - turbine
  - coroutines
  - type/concept
  - level/intermediate
prerequisites:
  - "[[kmp-getting-started]]"
  - "[[kmp-project-structure]]"
  - "[[kotlin-coroutines]]"
cs-foundations:
  - "[[unit-testing-theory]]"
  - "[[assertion-patterns]]"
  - "[[test-isolation-principles]]"
  - "[[virtual-time-testing]]"
  - "[[reactive-testing-patterns]]"
related:
  - "[[kmp-overview]]"
  - "[[kmp-testing-strategies]]"
  - "[[kmp-integration-testing]]"
status: published
---

# Unit Testing в Kotlin Multiplatform

> **TL;DR:** kotlin.test + Kotest assertions (300+ matchers) + kotlinx-coroutines-test (runTest) + Turbine (Flow testing). Тесты в commonTest работают на всех платформах. runTest автоматически пропускает delays. Turbine для StateFlow: `flow.test { awaitItem() shouldBe expected }`. Fakes вместо mocks для максимальной совместимости.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Kotlin Coroutines | suspend functions, Flow | [[kotlin-coroutines]] |
| KMP структура | Source sets | [[kmp-project-structure]] |
| Testing basics | Arrange-Act-Assert | Testing guide |
| Unit Testing Theory | Изоляция и быстрая обратная связь | [[unit-testing-theory]] |
| Virtual Time | Тестирование асинхронного кода | [[virtual-time-testing]] |
| Reactive Testing | Тестирование потоков данных | [[reactive-testing-patterns]] |

---

## Почему unit тесты — основа качества?

### CS-фундамент: F.I.R.S.T. принципы

Хорошие unit тесты следуют F.I.R.S.T.:

```
┌─────────────────────────────────────────────────────────────────┐
│ F - Fast         │ Миллисекунды, не секунды                    │
│                  │ Разработчик запускает 1000+ раз в день       │
├──────────────────┼──────────────────────────────────────────────┤
│ I - Isolated     │ Тест не зависит от других тестов            │
│                  │ Можно запустить в любом порядке              │
├──────────────────┼──────────────────────────────────────────────┤
│ R - Repeatable   │ Тот же результат при каждом запуске         │
│                  │ Не зависит от сети, времени, файлов          │
├──────────────────┼──────────────────────────────────────────────┤
│ S - Self-valid   │ Тест сам определяет pass/fail               │
│                  │ Не требует ручной проверки логов             │
├──────────────────┼──────────────────────────────────────────────┤
│ T - Timely       │ Пишется до или сразу после кода             │
│                  │ Не откладывается "на потом"                  │
└──────────────────┴──────────────────────────────────────────────┘
```

### Почему runTest вместо runBlocking?

```kotlin
// ❌ runBlocking — РЕАЛЬНОЕ время
@Test
fun slowTest() = runBlocking {
    delay(10_000)  // Ждёт 10 секунд!
    // CI билд: 100 таких тестов = 16+ минут ожидания
}

// ✅ runTest — ВИРТУАЛЬНОЕ время
@Test
fun fastTest() = runTest {
    delay(10_000)  // Мгновенно! Virtual time skip
    // CI билд: 100 тестов = миллисекунды
}
```

**Как работает виртуальное время:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Real Time (runBlocking)                                         │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ t=0      delay(1000)     t=1000    delay(1000)     t=2000      │
│ │        ░░░░░░░░░░░░░░░░│        ░░░░░░░░░░░░░░░░│            │
│ └────────────────────────┴────────────────────────┘            │
│         ↑ Реально ждём 2 секунды                                │
├─────────────────────────────────────────────────────────────────┤
│ Virtual Time (runTest)                                          │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ t=0 → skip → t=1000 → skip → t=2000                            │
│ │          │              │                                     │
│ └──────────┴──────────────┘                                    │
│   ↑ Мгновенно! Scheduler просто передвигает clock               │
└─────────────────────────────────────────────────────────────────┘
```

**TestCoroutineScheduler** — виртуальные часы, которые:
- Отслеживают все `delay()` вызовы
- Позволяют "перемотать" время через `advanceTimeBy()`
- Выполняют coroutines в правильном порядке

### Почему Turbine для Flow, а не collect?

**Проблема ручного тестирования Flow:**

```kotlin
// ❌ Ручной сбор — много boilerplate, легко пропустить ошибки
@Test
fun manualFlowTest() = runTest {
    val emissions = mutableListOf<Int>()
    val job = launch {
        flowOf(1, 2, 3).collect { emissions.add(it) }
    }
    advanceUntilIdle()
    job.cancel()
    assertEquals(listOf(1, 2, 3), emissions)
}

// ✅ Turbine — декларативно, безопасно
@Test
fun turbineFlowTest() = runTest {
    flowOf(1, 2, 3).test {
        awaitItem() shouldBe 1
        awaitItem() shouldBe 2
        awaitItem() shouldBe 3
        awaitComplete()
    }
}
```

**Что Turbine делает под капотом:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Flow: emit(1) → emit(2) → emit(3) → complete                    │
│       │          │          │          │                        │
│       ▼          ▼          ▼          ▼                        │
│ ┌───────────────────────────────────────────────────────────┐   │
│ │ Turbine internal channel (buffered)                       │   │
│ │ [1] [2] [3] [complete]                                    │   │
│ └───────────────────────────────────────────────────────────┘   │
│       │          │          │          │                        │
│       ▼          ▼          ▼          ▼                        │
│  awaitItem()  awaitItem()  awaitItem()  awaitComplete()         │
│       1          2          3          ✓                        │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевые преимущества Turbine:**
- Автоматический timeout (3 сек по умолчанию) — тест не зависнет
- Буферизация — не пропустит быстрые эмиссии
- Проверка completion/error — явный контроль жизненного цикла
- `expectMostRecentItem()` — для conflated StateFlow

### Two TestDispatchers: когда какой?

```
┌─────────────────────────────────────────────────────────────────┐
│ StandardTestDispatcher (default)                                │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ launch { value = 1 }                                            │
│        │                                                        │
│        ▼                                                        │
│ [Queued] ─── runCurrent() ──► [Executed]                        │
│                                                                 │
│ Use: Precise control, testing timing-sensitive logic            │
├─────────────────────────────────────────────────────────────────┤
│ UnconfinedTestDispatcher                                        │
│ ═══════════════════════════════════════════════════════════════ │
│                                                                 │
│ launch { value = 1 }                                            │
│        │                                                        │
│        ▼                                                        │
│ [Immediately Executed]                                          │
│                                                                 │
│ Use: Simple tests, backward compatibility, eager execution      │
└─────────────────────────────────────────────────────────────────┘
```

**Правило выбора:**
- **StandardTestDispatcher** (default): когда важен порядок выполнения
- **UnconfinedTestDispatcher**: когда просто нужен результат

---

## Настройка

### libs.versions.toml

```toml
[versions]
kotlin = "2.1.21"
coroutines = "1.10.2"
kotest = "5.9.1"
turbine = "1.2.0"

[libraries]
kotlin-test = { module = "org.jetbrains.kotlin:kotlin-test", version.ref = "kotlin" }
kotlinx-coroutines-test = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-test", version.ref = "coroutines" }
kotest-assertions = { module = "io.kotest:kotest-assertions-core", version.ref = "kotest" }
turbine = { module = "app.cash.turbine:turbine", version.ref = "turbine" }
```

### build.gradle.kts

```kotlin
kotlin {
    sourceSets {
        commonTest.dependencies {
            implementation(libs.kotlin.test)
            implementation(libs.kotlinx.coroutines.test)
            implementation(libs.kotest.assertions)
            implementation(libs.turbine)
        }
    }
}
```

---

## kotlin.test — базовые assertions

### Основные assertions

```kotlin
import kotlin.test.*

class BasicAssertionsTest {

    @Test
    fun `basic assertions`() {
        // Equality
        assertEquals(expected = 42, actual = 40 + 2)
        assertNotEquals(illegal = 0, actual = 1)

        // Boolean
        assertTrue(1 < 2)
        assertFalse(1 > 2)

        // Null
        assertNull(null)
        assertNotNull("hello")

        // Same instance
        val obj = Object()
        assertSame(obj, obj)

        // Contains
        assertContains(listOf(1, 2, 3), 2)
        assertContains("hello world", "world")

        // Type
        val value: Any = "string"
        assertIs<String>(value)
    }

    @Test
    fun `exception assertions`() {
        assertFailsWith<IllegalArgumentException> {
            require(false) { "Error" }
        }

        val exception = assertFailsWith<RuntimeException> {
            throw RuntimeException("test message")
        }
        assertEquals("test message", exception.message)
    }
}
```

---

## Kotest — продвинутые assertions

### Базовые matchers

```kotlin
import io.kotest.matchers.shouldBe
import io.kotest.matchers.shouldNotBe
import io.kotest.matchers.nulls.*
import io.kotest.matchers.string.*
import io.kotest.matchers.collections.*

class KotestAssertionsTest {

    @Test
    fun `shouldBe assertions`() {
        // Equality
        "hello" shouldBe "hello"
        42 shouldBe 42
        null shouldBe null

        // Not equal
        "hello" shouldNotBe "world"

        // Nullability
        val name: String? = "John"
        name.shouldNotBeNull()
        name shouldBe "John"

        val empty: String? = null
        empty.shouldBeNull()
    }

    @Test
    fun `string assertions`() {
        val text = "Hello, World!"

        text shouldContain "World"
        text shouldStartWith "Hello"
        text shouldEndWith "!"
        text shouldMatch Regex("Hello.*")
        text.shouldHaveLength(13)
        text.shouldNotBeBlank()
        text.shouldBeUpperCase().shouldBeFalse()  // Ошибка — не uppercase

        "hello".shouldBeLowerCase()
        "HELLO".shouldBeUpperCase()
    }

    @Test
    fun `collection assertions`() {
        val list = listOf(1, 2, 3, 4, 5)

        list shouldContain 3
        list shouldContainAll listOf(1, 3)
        list shouldNotContain 10
        list.shouldHaveSize(5)
        list.shouldNotBeEmpty()

        // Exact order
        list shouldContainExactly listOf(1, 2, 3, 4, 5)

        // Any order
        list shouldContainExactlyInAnyOrder listOf(5, 4, 3, 2, 1)

        // First/Last
        list.first() shouldBe 1
        list.last() shouldBe 5

        // All/None/Any
        list.forAll { it shouldBeGreaterThan 0 }
        list.forNone { it shouldBeLessThan 0 }
        list.forAny { it shouldBe 3 }
        list.forExactly(1) { it shouldBe 3 }
    }

    @Test
    fun `map assertions`() {
        val map = mapOf("a" to 1, "b" to 2)

        map shouldContainKey "a"
        map shouldContainValue 2
        map shouldContain ("a" to 1)
        map.shouldHaveSize(2)
    }
}
```

### Soft Assertions

```kotlin
import io.kotest.assertions.assertSoftly

class SoftAssertionsTest {

    @Test
    fun `soft assertions collect all failures`() {
        val user = User(
            id = "1",
            name = "John",
            email = "john@example.com",
            age = 25
        )

        // Все assertions выполнятся, все ошибки покажутся вместе
        assertSoftly(user) {
            id shouldBe "1"
            name shouldBe "John"
            email shouldContain "@"
            age shouldBeGreaterThan 18
        }
    }

    @Test
    fun `soft assertions without receiver`() {
        assertSoftly {
            "hello" shouldBe "hello"
            42 shouldBe 42
            listOf(1, 2, 3) shouldHaveSize 3
        }
    }
}
```

### Custom matchers

```kotlin
import io.kotest.matchers.Matcher
import io.kotest.matchers.MatcherResult
import io.kotest.matchers.should

// Custom matcher
fun beValidEmail() = Matcher<String> { value ->
    MatcherResult(
        passed = value.contains("@") && value.contains("."),
        failureMessageFn = { "$value should be a valid email" },
        negatedFailureMessageFn = { "$value should not be a valid email" }
    )
}

// Extension function
fun String.shouldBeValidEmail() = this should beValidEmail()

// Usage
class CustomMatcherTest {
    @Test
    fun `email validation`() {
        "john@example.com".shouldBeValidEmail()
    }
}
```

---

## Coroutines Testing

### runTest основы

```kotlin
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.delay
import kotlin.test.Test

class CoroutineBasicsTest {

    @Test
    fun `runTest skips delays`() = runTest {
        // delay автоматически пропускается
        delay(10_000)  // Не ждёт 10 секунд!

        val result = 1 + 1
        result shouldBe 2
    }

    @Test
    fun `test suspend function`() = runTest {
        val repository = FakeUserRepository()
        repository.addUser(User("1", "John", "john@example.com"))

        val user = repository.getUser("1")

        user.shouldNotBeNull()
        user.name shouldBe "John"
    }
}
```

### Virtual time control

```kotlin
import kotlinx.coroutines.test.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

class VirtualTimeTest {

    @Test
    fun `advanceTimeBy controls virtual time`() = runTest {
        var counter = 0

        launch {
            delay(1000)
            counter++
            delay(1000)
            counter++
        }

        // Ничего не выполнилось
        counter shouldBe 0

        // Продвигаем время на 1 секунду
        advanceTimeBy(1000)
        counter shouldBe 1

        // Продвигаем ещё
        advanceTimeBy(1000)
        counter shouldBe 2
    }

    @Test
    fun `advanceUntilIdle runs all coroutines`() = runTest {
        var completed = false

        launch {
            delay(5000)
            completed = true
        }

        advanceUntilIdle()  // Выполняет всё
        completed shouldBe true
    }
}
```

### TestDispatcher

```kotlin
import kotlinx.coroutines.test.*
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi

@OptIn(ExperimentalCoroutinesApi::class)
class TestDispatcherTest {

    @Test
    fun `StandardTestDispatcher for precise control`() = runTest {
        // По умолчанию используется StandardTestDispatcher
        // Coroutines не запускаются автоматически

        var value = 0
        launch {
            value = 1
        }

        // Ещё не выполнилось
        value shouldBe 0

        // Нужно явно запустить
        runCurrent()
        value shouldBe 1
    }

    @Test
    fun `UnconfinedTestDispatcher for eager execution`() =
        runTest(UnconfinedTestDispatcher()) {
            // Coroutines запускаются сразу

            var value = 0
            launch {
                value = 1
            }

            // Уже выполнилось!
            value shouldBe 1
        }
}
```

---

## Flow Testing с Turbine

### Базовое использование

```kotlin
import app.cash.turbine.test
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.test.runTest

class TurbineBasicsTest {

    @Test
    fun `test simple flow`() = runTest {
        val flow = flowOf(1, 2, 3)

        flow.test {
            awaitItem() shouldBe 1
            awaitItem() shouldBe 2
            awaitItem() shouldBe 3
            awaitComplete()
        }
    }

    @Test
    fun `test flow with transformations`() = runTest {
        val flow = flowOf(1, 2, 3)
            .map { it * 2 }
            .filter { it > 2 }

        flow.test {
            awaitItem() shouldBe 4  // 2 * 2
            awaitItem() shouldBe 6  // 3 * 2
            awaitComplete()
        }
    }

    @Test
    fun `test flow with error`() = runTest {
        val flow = flow<Int> {
            emit(1)
            throw RuntimeException("Error!")
        }

        flow.test {
            awaitItem() shouldBe 1
            val error = awaitError()
            error.message shouldBe "Error!"
        }
    }
}
```

### StateFlow Testing

```kotlin
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class StateFlowTest {

    @Test
    fun `test StateFlow emissions`() = runTest {
        val stateFlow = MutableStateFlow(0)

        stateFlow.test {
            // Initial value
            awaitItem() shouldBe 0

            stateFlow.value = 1
            awaitItem() shouldBe 1

            stateFlow.value = 2
            awaitItem() shouldBe 2

            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun `test StateFlow with skip`() = runTest {
        val stateFlow = MutableStateFlow("initial")

        stateFlow.test {
            skipItems(1)  // Пропустить initial value

            stateFlow.value = "updated"
            awaitItem() shouldBe "updated"

            cancelAndIgnoreRemainingEvents()
        }
    }
}
```

### Turbine Tips

```kotlin
class TurbineTipsTest {

    @Test
    fun `use expectMostRecentItem for conflated flows`() = runTest {
        val stateFlow = MutableStateFlow(0)

        stateFlow.test {
            // Пропускаем initial
            skipItems(1)

            // Быстро меняем значения (conflation!)
            stateFlow.value = 1
            stateFlow.value = 2
            stateFlow.value = 3

            // Берём последнее значение
            expectMostRecentItem() shouldBe 3

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `use turbineScope for multiple flows`() = runTest {
        val flow1 = MutableStateFlow(0)
        val flow2 = MutableStateFlow("a")

        turbineScope {
            val turbine1 = flow1.testIn(backgroundScope)
            val turbine2 = flow2.testIn(backgroundScope)

            turbine1.awaitItem() shouldBe 0
            turbine2.awaitItem() shouldBe "a"

            flow1.value = 1
            flow2.value = "b"

            turbine1.awaitItem() shouldBe 1
            turbine2.awaitItem() shouldBe "b"

            turbine1.cancelAndIgnoreRemainingEvents()
            turbine2.cancelAndIgnoreRemainingEvents()
        }
    }
}
```

---

## Тестирование ViewModel

### Пример ViewModel

```kotlin
// commonMain
class UserListViewModel(
    private val getUsersUseCase: GetUsersUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<User>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<User>>> = _uiState.asStateFlow()

    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            getUsersUseCase()
                .onSuccess { users ->
                    _uiState.value = UiState.Success(users)
                }
                .onFailure { error ->
                    _uiState.value = UiState.Error(error.message ?: "Unknown error")
                    _events.emit(UiEvent.ShowError(error.message ?: "Unknown error"))
                }
        }
    }
}

sealed class UiState<out T> {
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String) : UiState<Nothing>()
}

sealed class UiEvent {
    data class ShowError(val message: String) : UiEvent()
}
```

### Тесты ViewModel

```kotlin
// commonTest
class UserListViewModelTest {

    private lateinit var viewModel: UserListViewModel
    private lateinit var getUsersUseCase: FakeGetUsersUseCase

    @BeforeTest
    fun setup() {
        getUsersUseCase = FakeGetUsersUseCase()
        viewModel = UserListViewModel(getUsersUseCase)
    }

    @Test
    fun `loadUsers emits Loading then Success`() = runTest {
        // Arrange
        val users = listOf(
            User("1", "John", "john@example.com"),
            User("2", "Jane", "jane@example.com")
        )
        getUsersUseCase.setResult(Result.success(users))

        // Act & Assert
        viewModel.uiState.test {
            // Initial state
            awaitItem() shouldBe UiState.Loading

            // Trigger load
            viewModel.loadUsers()
            advanceUntilIdle()

            // Loading emitted (optional, may be conflated)
            // Success state
            val successState = awaitItem()
            successState shouldBe UiState.Success(users)

            cancelAndIgnoreRemainingEvents()
        }
    }

    @Test
    fun `loadUsers emits Error and event on failure`() = runTest {
        // Arrange
        getUsersUseCase.setResult(Result.failure(Exception("Network error")))

        turbineScope {
            val stateTurbine = viewModel.uiState.testIn(backgroundScope)
            val eventTurbine = viewModel.events.testIn(backgroundScope)

            // Skip initial Loading
            stateTurbine.awaitItem() shouldBe UiState.Loading

            // Act
            viewModel.loadUsers()
            advanceUntilIdle()

            // Assert state
            val errorState = stateTurbine.awaitItem()
            errorState shouldBe UiState.Error("Network error")

            // Assert event
            val event = eventTurbine.awaitItem()
            event shouldBe UiEvent.ShowError("Network error")

            stateTurbine.cancelAndIgnoreRemainingEvents()
            eventTurbine.cancelAndIgnoreRemainingEvents()
        }
    }
}

// Fake implementation
class FakeGetUsersUseCase : GetUsersUseCase {
    private var result: Result<List<User>> = Result.success(emptyList())

    fun setResult(result: Result<List<User>>) {
        this.result = result
    }

    override suspend fun invoke(): Result<List<User>> = result
}
```

---

## Тестирование UseCase

```kotlin
// UseCase
class GetUserUseCase(private val repository: UserRepository) {
    suspend operator fun invoke(id: String): Result<User> {
        return runCatching {
            repository.getUser(id)
                ?: throw UserNotFoundException(id)
        }
    }
}

// Test
class GetUserUseCaseTest {

    private lateinit var repository: FakeUserRepository
    private lateinit var useCase: GetUserUseCase

    @BeforeTest
    fun setup() {
        repository = FakeUserRepository()
        useCase = GetUserUseCase(repository)
    }

    @Test
    fun `invoke returns user when exists`() = runTest {
        // Arrange
        val user = User("1", "John", "john@example.com")
        repository.addUser(user)

        // Act
        val result = useCase("1")

        // Assert
        result.isSuccess shouldBe true
        result.getOrNull() shouldBe user
    }

    @Test
    fun `invoke returns failure when user not found`() = runTest {
        // Act
        val result = useCase("nonexistent")

        // Assert
        result.isFailure shouldBe true
        result.exceptionOrNull() shouldBeInstanceOf UserNotFoundException::class
    }
}
```

---

## Best Practices

### Checklist

| Практика | Описание |
|----------|----------|
| ✅ runTest | Всегда для suspend functions |
| ✅ Turbine | Для Flow testing |
| ✅ Fakes | Предпочитать mocks |
| ✅ assertSoftly | Для multiple assertions |
| ✅ Descriptive names | `should behavior when condition` |
| ✅ AAA pattern | Arrange-Act-Assert |
| ⚠️ awaitItem timeout | По умолчанию 3 секунды |
| ⚠️ cancelAndIgnoreRemainingEvents | Не забывать в конце |

### Common Mistakes

```kotlin
// ❌ Плохо: забыли runTest
@Test
fun `bad test`() {
    val result = runBlocking { useCase() }  // Не используйте runBlocking!
}

// ✅ Хорошо
@Test
fun `good test`() = runTest {
    val result = useCase()
}

// ❌ Плохо: не завершили Turbine
@Test
fun `leaky test`() = runTest {
    stateFlow.test {
        awaitItem()
        // Забыли cancel!
    }
}

// ✅ Хорошо
@Test
fun `clean test`() = runTest {
    stateFlow.test {
        awaitItem()
        cancelAndIgnoreRemainingEvents()
    }
}
```

---

## Мифы и заблуждения

### Миф 1: "runBlocking и runTest — одно и то же"

**Реальность:** Критическая разница. `runBlocking` использует **реальное время** — `delay(10_000)` ждёт 10 секунд. `runTest` использует **виртуальное время** — delays пропускаются мгновенно. Для CI это разница между минутами и миллисекундами.

### Миф 2: "Kotest assertions несовместимы с kotlin.test"

**Реальность:** Kotest модульный. Можно использовать **только assertions** (`kotest-assertions-core`) с любым test runner:
```kotlin
// kotlin.test @Test + Kotest shouldBe
@Test
fun test() {
    user.name shouldBe "John"  // ✅ Работает!
}
```

### Миф 3: "Turbine только для холодных Flow"

**Реальность:** Turbine отлично работает с **StateFlow и SharedFlow**. Для StateFlow рекомендуется `skipItems(1)` для пропуска initial value или `expectMostRecentItem()` для conflated значений.

### Миф 4: "awaitItem() блокирует навсегда"

**Реальность:** Turbine имеет **timeout по умолчанию 3 секунды**. Если Flow не эмитит — тест упадёт с понятной ошибкой, а не зависнет. Timeout настраивается через `turbineTimeout`.

### Миф 5: "UnconfinedTestDispatcher устарел"

**Реальность:** Оба диспатчера актуальны для разных сценариев. **StandardTestDispatcher** (default) — для precise control. **UnconfinedTestDispatcher** — для простых тестов, где важен только результат, не порядок выполнения.

### Миф 6: "assertSoftly замедляет тесты"

**Реальность:** `assertSoftly` не влияет на производительность. Он просто собирает **все failures** перед выбросом исключения, вместо остановки на первом. Это улучшает DX — видны все проблемы сразу.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [kotlin.test](https://kotlinlang.org/api/latest/kotlin.test/) | Official | Basic assertions |
| [Kotest Assertions](https://kotest.io/docs/assertions/assertions.html) | Official | 300+ matchers |
| [Turbine](https://github.com/cashapp/turbine) | GitHub | Flow testing |
| [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) | Official | runTest, TestDispatcher |
| [Android Coroutine Testing](https://developer.android.com/kotlin/coroutines/test) | Official | Android specifics |
| [Testing Kotlin Flows](https://kt.academy/article/cc-testing-flow) | Blog | Deep dive |

### CS-фундамент

| Тема | Применение в KMP | Где изучить |
|------|------------------|-------------|
| F.I.R.S.T. Principles | Качественные unit тесты | Robert Martin "Clean Code" |
| Virtual Time | runTest, TestDispatcher | Discrete Event Simulation |
| Reactive Testing | Turbine, Flow testing | Reactive Manifesto |
| Assertion Patterns | shouldBe, assertSoftly | xUnit Patterns |
| Test Isolation | Fakes, no shared state | Gerard Meszaros "xUnit Test Patterns" |

---

## Связь с другими темами

- **[[kmp-overview]]** — unit тесты в KMP пишутся в commonTest и автоматически запускаются на всех целевых платформах. Это означает, что один написанный тест проверяет поведение кода на JVM, Android, iOS и других targets. Понимание структуры source sets необходимо для правильной организации тестов и использования expect/actual для platform-specific test utilities.

- **[[kmp-testing-strategies]]** — unit тесты составляют основу тестовой пирамиды в KMP (70% от всех тестов). Стратегия тестирования определяет, что именно покрывать unit тестами (UseCases, ViewModels, Repositories), какие инструменты использовать (kotlin.test + Kotest + Turbine) и как организовать fakes вместо mocks для совместимости с Kotlin/Native, где нет reflection.

- **[[kmp-integration-testing]]** — unit тесты и integration тесты дополняют друг друга: unit тесты проверяют изолированную логику с fakes, а integration тесты — взаимодействие компонентов с MockEngine и in-memory SQLDelight. Понимание границ между ними позволяет избежать дублирования и сфокусировать каждый тип теста на своей зоне ответственности — логика vs контракты.

## Источники и дальнейшее чтение

- **Moskala M. (2022).** *Kotlin Coroutines: Deep Dive.* — Содержит подробную главу о тестировании корутин: runTest, TestDispatcher, virtual time, а также паттерны тестирования Flow и StateFlow. Без этих знаний невозможно правильно тестировать асинхронный код в KMP.

- **Martin R. (2017).** *Clean Architecture.* — Принципы тестируемости через инверсию зависимостей и разделение слоёв. Объясняет, почему UseCases и Repositories должны зависеть от интерфейсов, а не реализаций, что позволяет легко подставлять fakes в unit тестах.

- **Moskala M. (2021).** *Effective Kotlin.* — Практические рекомендации по написанию тестируемого Kotlin-кода: использование sealed classes для состояний (UiState), data classes для сравнения в assertions, и extension functions для custom matchers.

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, Kotest 5.9.1, Turbine 1.2.1, kotlinx-coroutines-test 1.10.2*
