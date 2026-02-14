---
title: "Стратегия тестирования в KMP: от unit до UI тестов"
created: 2026-01-03
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - testing
  - unit-tests
  - integration
  - type/concept
  - level/intermediate
prerequisites:
  - "[[kmp-getting-started]]"
  - "[[kmp-unit-testing]]"
cs-foundations:
  - "[[testing-pyramid-theory]]"
  - "[[test-driven-development]]"
  - "[[mock-stub-fake-patterns]]"
  - "[[code-coverage-theory]]"
  - "[[continuous-integration]]"
related:
  - "[[kmp-overview]]"
  - "[[kmp-unit-testing]]"
  - "[[kmp-integration-testing]]"
status: published
reading_time: 24
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Стратегия тестирования в Kotlin Multiplatform

> **TL;DR:** KMP тесты пишутся в commonTest (запускаются на всех платформах) и platform-specific (androidTest, iosTest). Используйте kotlin.test + Kotest assertions + Turbine (Flow) + Mokkery (mocks). Test pyramid: больше unit, меньше UI. Kover для coverage (только JVM/Android). CI: `./gradlew allTests`.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Unit testing | Базовые концепции | Любой testing guide |
| KMP структура | Source sets | [[kmp-project-structure]] |
| Coroutines | Тестирование Flow | [[kotlin-coroutines]] |
| Test Pyramid Theory | Понимание соотношения тестов | [[testing-pyramid-theory]] |
| Mock/Stub/Fake | Типы test doubles | [[mock-stub-fake-patterns]] |
| Code Coverage | Метрики покрытия | [[code-coverage-theory]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **commonTest** | Тесты для shared кода | Универсальный тест-драйв для всех рынков |
| **Test Pyramid** | Соотношение типов тестов | Пирамида питания — больше овощей (unit), меньше сладкого (UI) |
| **Kover** | Code coverage tool | Счётчик посещений — какой код был выполнен |
| **Turbine** | Flow testing library | Детектор потока — отслеживает все эмиссии |
| **Fake** | Простая реализация для тестов | Муляж — выглядит как настоящее, но проще |

---

## Почему тестирование в KMP особенное?

### Test Pyramid: экономика дефектов

Баг в production стоит **100x** дороже чем пойманный unit тестом. Unit тесты: быстрые (мс), стабильные. UI тесты: медленные (минуты), flaky. Инвертированная пирамида = "Ice Cream Cone" антипаттерн.

### KMP: "Write Once, Test Everywhere"

Тесты в `commonTest` запускаются на **всех платформах**. 70 shared тестов = 70 × N платформ проверок. Один тест — двойная уверенность.

### Mocking в KMP: проблема Native

**MockK не работает на Kotlin/Native** — нет reflection. Решения: Mokkery (compiler plugin), Mockative/KMock (KSP), или **manual fakes** (рекомендуется для простоты).

### Coverage targets (industry consensus)

| Слой | Coverage | Скорость |
|------|----------|----------|
| Unit (commonTest) | 80%+ | мс |
| Integration | 60-70% | сек |
| UI | 30-40% | мин |

**Overall 65-75% = excellent** — не гонитесь за 100%.

---

## Test Pyramid в KMP

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST PYRAMID                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│                        /\                                   │
│                       /  \     UI Tests                     │
│                      /    \    (платформо-специфичные)      │
│                     /      \   • XCUITest (iOS)             │
│                    /        \  • Compose UI Test (Android)  │
│                   /__________\                              │
│                  /            \                             │
│                 /  Integration \   Integration Tests        │
│                /     Tests      \  • API + Database         │
│               /                  \ • MockEngine + SQLDelight│
│              /____________________\                         │
│             /                      \                        │
│            /       Unit Tests       \  Unit Tests           │
│           /        (commonTest)      \ • ViewModels         │
│          /                            \• UseCases           │
│         /                              • Repositories       │
│        /__________________________________\                 │
│                                                             │
│   Больше → Быстрее → Дешевле (снизу вверх)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Рекомендуемое соотношение

| Тип | Доля | Скорость | Где запускать |
|-----|------|----------|---------------|
| **Unit Tests** | 70% | Миллисекунды | commonTest, CI |
| **Integration Tests** | 20% | Секунды | commonTest/platform, CI |
| **UI Tests** | 10% | Минуты | Platform-specific, CD |

---

## Структура тестов

### Организация файлов

```
shared/
├── src/
│   ├── commonMain/
│   │   └── kotlin/
│   │       └── com/example/
│   │           ├── domain/
│   │           ├── data/
│   │           └── presentation/
│   ├── commonTest/                    # ← Shared tests (70%)
│   │   └── kotlin/
│   │       └── com/example/
│   │           ├── domain/
│   │           │   └── GetUserUseCaseTest.kt
│   │           ├── data/
│   │           │   └── UserRepositoryTest.kt
│   │           └── presentation/
│   │               └── UserViewModelTest.kt
│   ├── androidMain/
│   ├── androidUnitTest/               # ← Android unit tests
│   │   └── kotlin/
│   │       └── com/example/
│   │           └── AndroidSpecificTest.kt
│   ├── androidInstrumentedTest/       # ← Android UI tests
│   ├── iosMain/
│   └── iosTest/                       # ← iOS-specific tests
│       └── kotlin/
│           └── com/example/
│               └── IosSpecificTest.kt
```

### Именование тестов

```kotlin
// Паттерн: SubjectTest
// Файл: UserRepositoryTest.kt

class UserRepositoryTest {

    // Паттерн: `method should behavior when condition`
    @Test
    fun `getUser should return user when exists`() { ... }

    @Test
    fun `getUser should throw when not found`() { ... }

    @Test
    fun `saveUser should update existing user`() { ... }
}
```

---

## Настройка зависимостей

### libs.versions.toml

```toml
[versions]
kotlin = "2.1.21"
coroutines = "1.10.2"
kotest = "5.9.1"
turbine = "1.2.0"
mokkery = "2.5.0"
kover = "0.9.1"

[libraries]
kotlin-test = { module = "org.jetbrains.kotlin:kotlin-test", version.ref = "kotlin" }
kotlinx-coroutines-test = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-test", version.ref = "coroutines" }
kotest-assertions = { module = "io.kotest:kotest-assertions-core", version.ref = "kotest" }
turbine = { module = "app.cash.turbine:turbine", version.ref = "turbine" }

[plugins]
mokkery = { id = "dev.mokkery", version.ref = "mokkery" }
kover = { id = "org.jetbrains.kotlinx.kover", version.ref = "kover" }
```

### build.gradle.kts

```kotlin
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.mokkery)  // Mocking
    alias(libs.plugins.kover)    // Coverage
}

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

// Kover configuration
kover {
    reports {
        filters {
            excludes {
                classes("*_Factory", "*_Impl", "*.BuildConfig")
            }
        }
    }
}
```

---

## Что тестировать

### ✅ Приоритеты для commonTest

| Слой | Что тестировать | Пример |
|------|-----------------|--------|
| **Domain** | UseCases, бизнес-логика | `GetUserUseCase`, `ValidateEmailUseCase` |
| **Data** | Repositories, mappers | `UserRepository`, `UserMapper` |
| **Presentation** | ViewModels, state | `UserListViewModel` |
| **Utils** | Helpers, extensions | `DateFormatter`, `StringUtils` |

### ⚠️ Platform-specific тесты

| Платформа | Что тестировать |
|-----------|-----------------|
| **Android** | Room integration, WorkManager, Compose UI |
| **iOS** | NSUserDefaults, KeyChain, SwiftUI preview tests |

### ❌ Не тестируйте

- Trivial getters/setters
- Framework code (Ktor, SQLDelight — уже протестированы)
- Generated code

---

## Mocking в KMP

### Проблема

```kotlin
// ❌ MockK не работает на Native
val repository = mockk<UserRepository>()  // Только JVM!
```

### Решение 1: Fakes (рекомендуется)

```kotlin
// Интерфейс
interface UserRepository {
    suspend fun getUser(id: String): User?
    suspend fun saveUser(user: User)
}

// Fake для тестов
class FakeUserRepository : UserRepository {
    private val users = mutableMapOf<String, User>()

    override suspend fun getUser(id: String): User? = users[id]

    override suspend fun saveUser(user: User) {
        users[user.id] = user
    }

    // Test helpers
    fun addUser(user: User) {
        users[user.id] = user
    }

    fun clear() {
        users.clear()
    }
}

// Использование в тестах
class GetUserUseCaseTest {
    private val repository = FakeUserRepository()
    private val useCase = GetUserUseCase(repository)

    @Test
    fun `invoke returns user when exists`() = runTest {
        // Arrange
        repository.addUser(User("1", "John", "john@example.com"))

        // Act
        val result = useCase("1")

        // Assert
        result.shouldBeSuccess()
        result.getOrNull()?.name shouldBe "John"
    }
}
```

### Решение 2: Mokkery (библиотека)

```kotlin
// build.gradle.kts
plugins {
    id("dev.mokkery") version "2.5.0"
}

// Тест
import dev.mokkery.mock
import dev.mokkery.every
import dev.mokkery.verify

class UserViewModelTest {

    @Test
    fun `loadUsers calls repository`() = runTest {
        // Arrange
        val repository = mock<UserRepository> {
            every { getUsers() } returns flowOf(listOf(testUser))
        }
        val viewModel = UserListViewModel(repository)

        // Act
        viewModel.loadUsers()

        // Assert
        verify { repository.getUsers() }
    }
}
```

### Сравнение подходов

| Подход | Плюсы | Минусы |
|--------|-------|--------|
| **Fakes** | Простота, читаемость, работает везде | Больше кода |
| **Mokkery** | Меньше boilerplate, знакомый API | Compiler plugin |
| **Mockative** | KSP-based | Требует аннотации |

---

## Запуск тестов

### Gradle команды

```bash
# Все тесты на всех платформах
./gradlew allTests

# Только commonTest
./gradlew :shared:cleanAllTests :shared:allTests

# Android unit тесты
./gradlew :shared:testDebugUnitTest

# iOS тесты (требует macOS)
./gradlew :shared:iosSimulatorArm64Test

# Конкретный тест класс
./gradlew :shared:jvmTest --tests "com.example.UserRepositoryTest"

# Coverage report
./gradlew :shared:koverHtmlReport
```

### IDE запуск

- **IntelliJ/Android Studio:** Click на ▶️ рядом с тестом
- **Xcode:** Для iOS-specific тестов через XCTest

---

## Code Coverage с Kover

### Конфигурация

```kotlin
// build.gradle.kts
plugins {
    id("org.jetbrains.kotlinx.kover") version "0.9.1"
}

kover {
    reports {
        // Фильтры исключений
        filters {
            excludes {
                classes(
                    "*_Factory",
                    "*_Impl",
                    "*.di.*",
                    "*.BuildConfig"
                )
                packages("*.generated.*")
            }
        }

        // Verification rules
        verify {
            rule {
                bound {
                    minValue = 80  // Минимум 80% coverage
                }
            }
        }
    }
}
```

### Отчёты

```bash
# HTML отчёт
./gradlew koverHtmlReport
# → build/reports/kover/html/index.html

# XML для CI
./gradlew koverXmlReport
# → build/reports/kover/report.xml

# Проверка threshold
./gradlew koverVerify
```

### Ограничения Kover

| Платформа | Поддержка |
|-----------|-----------|
| JVM | ✅ |
| Android | ✅ |
| iOS/Native | ❌ |
| JS/Wasm | ❌ |

---

## CI/CD интеграция

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: macos-latest  # Для iOS тестов

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Run all tests
        run: ./gradlew allTests

      - name: Generate coverage report
        run: ./gradlew koverXmlReport

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          files: ./shared/build/reports/kover/report.xml
          fail_ci_if_error: true

      - name: Verify coverage threshold
        run: ./gradlew koverVerify
```

---

## Best Practices

### Checklist

| Практика | Описание |
|----------|----------|
| ✅ commonTest first | 70% тестов в shared |
| ✅ Fakes > Mocks | Проще, работают везде |
| ✅ Turbine для Flow | Правильная работа с async |
| ✅ runTest | Для coroutines |
| ✅ AAA pattern | Arrange-Act-Assert |
| ✅ Говорящие имена | `should behavior when condition` |
| ⚠️ Kover только JVM | Native не поддерживается |
| ⚠️ CI на macOS | Для iOS тестов |

### AAA Pattern

```kotlin
@Test
fun `getUser returns user when exists`() = runTest {
    // Arrange
    val repository = FakeUserRepository()
    repository.addUser(User("1", "John", "john@example.com"))
    val useCase = GetUserUseCase(repository)

    // Act
    val result = useCase("1")

    // Assert
    result.shouldBeSuccess()
    result.getOrNull()?.name shouldBe "John"
}
```

---

## Мифы и заблуждения

### Миф 1: "MockK работает в KMP"

**Реальность:** MockK работает **только на JVM**. Kotlin/Native компилируется статически (LLVM), без reflection API. Для KMP нужны Mokkery (compiler plugin), Mockative, KMock (KSP) или manual fakes.

### Миф 2: "100% coverage = качественный код"

**Реальность:** Coverage — метрика количества, не качества. Один хороший тест, ловящий реальные баги, ценнее десяти тестов на тривиальные геттеры. Industry consensus: **65-75% overall = excellent**. Гонка за 100% ведёт к тестам ради тестов.

### Миф 3: "UI тесты важнее unit тестов"

**Реальность:** Ice Cream Cone антипаттерн — когда UI тестов больше unit. Результат: медленный CI (минуты vs миллисекунды), flaky тесты (нестабильность UI), дорогая поддержка. **Правильно: 70% unit, 20% integration, 10% UI.**

### Миф 4: "Тесты в commonTest запускаются один раз"

**Реальность:** commonTest запускается **на каждой платформе отдельно**. `./gradlew allTests` = JVM + Android + iOS Simulator + JS. Один написанный тест даёт несколько запусков — это feature, а не bug.

### Миф 5: "androidTest = instrumented тесты"

**Реальность:** В KMP **androidTest = JVM unit тесты**, а **androidInstrumentedTest** (или androidAndroidTest) = instrumented тесты на эмуляторе. Путаница приводит к runtime exceptions.

### Миф 6: "Kotest заменяет kotlin.test"

**Реальность:** Kotest — модульный фреймворк. Можно использовать **только Kotest Assertions** с kotlin.test:
```kotlin
// kotlin.test + Kotest assertions
@Test
fun testUser() {
    user.name shouldBe "John"  // Kotest assertion
}
```
Не обязательно переписывать все тесты на Kotest DSL.

### Миф 7: "Kover покрывает все платформы"

**Реальность:** Kover 0.9.x поддерживает **только JVM и Android**. iOS/Native и JS/Wasm coverage пока не поддерживается. Для Native нет альтернатив в 2025.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [JetBrains KMP Testing](https://www.jetbrains.com/help/kotlin-multiplatform-dev/multiplatform-run-tests.html) | Official | Документация |
| [Compose MP Testing](https://kotlinlang.org/docs/multiplatform/compose-test.html) | Official | UI тесты |
| [Kotest](https://kotest.io/) | Official | DSL + assertions + property |
| [Turbine](https://github.com/cashapp/turbine) | GitHub | Flow testing |
| [Mokkery](https://mokkery.dev/) | Official | KMP mocking |
| [Kover](https://github.com/Kotlin/kotlinx-kover) | GitHub | Coverage |
| [kotlinx-coroutines-test](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-test/) | Official | runTest, TestDispatcher |
| [Touchlab KMM Testing](https://touchlab.co/understanding-and-configuring-your-kmm-test-suite/) | Blog | Project structure |
| [KMPShip Testing Guide 2025](https://www.kmpship.app/blog/kotlin-multiplatform-testing-guide-2025) | Blog | Production practices |

### CS-фундамент

| Тема | Применение в KMP | Где изучить |
|------|------------------|-------------|
| Test Pyramid | Соотношение типов тестов | Mike Cohn "Succeeding with Agile" |
| Cost of Defects | Почему ранние тесты дешевле | Barry Boehm research |
| Test Doubles | Fakes vs Mocks vs Stubs | xUnit Patterns |
| Code Coverage | Branch vs Line vs Path | ISTQB Foundation |
| TDD | Red-Green-Refactor | Kent Beck "TDD by Example" |

---

## Связь с другими темами

- **[[kmp-overview]]** — стратегия тестирования в KMP уникальна тем, что тесты из commonTest запускаются на каждой целевой платформе отдельно. Это даёт мультипликативный эффект: 70 shared тестов при 3 targets = 210 проверок. Понимание архитектуры KMP определяет, какие тесты писать в commonTest (70%), а какие — в platform-specific source sets.

- **[[kmp-unit-testing]]** — unit тесты формируют основание тестовой пирамиды и составляют 70% всех тестов. Стратегия определяет инструменты (kotlin.test + Kotest assertions + Turbine), подходы (fakes вместо mocks из-за ограничений Kotlin/Native) и приоритеты (Domain → Data → Presentation). Без продуманной стратегии unit тесты превращаются в хаотичный набор проверок без системного покрытия.

- **[[kmp-integration-testing]]** — integration тесты занимают среднюю часть пирамиды (20%) и проверяют контракты между компонентами: Repository + MockEngine + SQLDelight in-memory. Стратегия определяет границы интеграции — что тестировать вместе, а что изолировать — и обеспечивает баланс между скоростью и полнотой покрытия.

## Источники и дальнейшее чтение

- **Martin R. (2017).** *Clean Architecture.* — Определяет принципы тестируемой архитектуры: Dependency Inversion, Separation of Concerns и Boundary interfaces. Эти принципы напрямую применяются к организации тестовой стратегии в KMP — от выбора слоёв для покрытия до проектирования test doubles.

- **Moskala M. (2022).** *Kotlin Coroutines: Deep Dive.* — Глава о тестировании корутин охватывает runTest, TestDispatcher и паттерны тестирования Flow. Поскольку большинство KMP-кода использует корутины, эти знания критичны для всех уровней тестовой пирамиды.

- **Moskala M. (2021).** *Effective Kotlin.* — Рекомендации по написанию идиоматического Kotlin-кода, который легко тестировать: prefer composition over inheritance, используйте sealed classes для представления состояний, избегайте side effects в pure functions.

---

## Проверь себя

> [!question]- Почему тестовая пирамида в KMP имеет особенности по сравнению с обычной Android-разработкой?
> В KMP тесты в commonTest запускаются на всех target-платформах, обеспечивая кросс-платформенную верификацию. Unit-тесты в commonTest заменяют необходимость дублирования тестов для каждой платформы. UI-тесты остаются platform-specific.

> [!question]- Как Kover помогает с code coverage в KMP-проектах?
> Kover -- мультиплатформенный инструмент code coverage от JetBrains. Он объединяет coverage из commonTest, androidTest, iosTest в единый отчёт, показывая общее покрытие shared-кода. Поддерживает HTML, XML, console отчёты.

> [!question]- Почему для мокирования в KMP используется Mokkery, а не Mockito?
> Mockito работает через reflection и byte-code generation на JVM, что несовместимо с Kotlin/Native и Kotlin/JS. Mokkery -- мультиплатформенная библиотека мокирования через KSP code generation, работающая в commonTest.

---

## Ключевые карточки

Как выглядит тестовая пирамида в KMP?
?
Unit-тесты (commonTest, 70%): бизнес-логика, use cases, repositories. Integration-тесты (commonTest/platformTest, 20%): Ktor MockEngine, SQLDelight in-memory. UI-тесты (platformTest, 10%): Compose UI tests, XCTest.

Какие тестовые фреймворки поддерживают KMP?
?
kotlin.test (стандартный, минимальный), Kotest (rich assertions, property testing), Turbine (Flow testing), Mokkery (mocking), kotlinx-coroutines-test (runTest, TestDispatcher).

Что такое commonTest и как он работает?
?
Source set для тестов, запускаемых на всех target-платформах. Тесты пишутся один раз в commonTest и автоматически выполняются для JVM, Native, JS. Обеспечивает единую верификацию shared-кода.

Как настроить CI/CD для KMP-тестов?
?
./gradlew allTests запускает тесты для всех targets. Для iOS нужен macOS runner. GitHub Actions: matrix strategy с ubuntu (JVM/JS) и macos (iOS/macOS). Kover для coverage отчётов.

Когда нужны platform-specific тесты?
?
Для тестирования actual-реализаций (platform-specific code), UI-тестов (Compose UI Test, XCTest), интеграции с platform API (Keychain, SharedPreferences) и проверки platform-specific behavior.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-unit-testing]] | Детальное руководство по unit-тестированию |
| Углубиться | [[kmp-integration-testing]] | Integration-тесты: MockEngine, in-memory DB |
| Смежная тема | [[kmp-ci-cd]] | CI/CD для запуска тестов на всех платформах |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Kotlin 2.1.21, Kotest 5.9.1, Turbine 1.2.1, Mokkery 3.1.1*
