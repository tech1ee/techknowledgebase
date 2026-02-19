---
title: "Обработка ошибок: от исключений до типизированных ошибок"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/error-handling
  - topic/kotlin
related:
  - "[[resilience-patterns]]"
  - "[[solid-principles]]"
  - "[[kotlin-basics]]"
  - "[[kotlin-coroutines]]"
---

# Обработка ошибок: от исключений до типизированных ошибок

Каждая программа рано или поздно сталкивается с ситуацией, которую не ожидала. Файл не найден, сеть отвалилась, пользователь ввёл буквы вместо цифр. Вопрос не в том, будут ли ошибки, а в том, насколько честно код сообщает о них. За 60 лет индустрия прошла путь от кодов возврата к исключениям, а затем — к типизированным ошибкам, где компилятор *заставляет* обработать каждый сценарий.

Kotlin занимает в этой эволюции уникальную позицию: все исключения unchecked (как в Python), но при этом язык даёт `Result<T>`, sealed-классы и Arrow `Either` — инструменты, которые делают ошибки видимыми в типах без многословности Java.

---

## Эволюция подходов к ошибкам

```
1960-е  Коды возврата (C, Fortran)
   │    └── -1, NULL, errno — вызывающий код ОБЯЗАН проверять
   │
1970-е  Исключения (Lisp, затем CLU, C++, Java)
   │    └── throw/catch — ошибка «летит» по стеку вызовов
   │
1990-е  Checked vs Unchecked (Java)
   │    ├── Checked: IOException — ОБЯЗАН обработать
   │    └── Unchecked: NullPointerException — на совести программиста
   │
2010-е  Result/Either типы (Rust, Haskell, Scala, Kotlin)
   │    └── Ошибка — часть типа: Result<User, Error>
   │
2020-е  Raise DSL, контекстные ресиверы (Arrow 1.2+)
        └── raise(error) вместо return Either.Left(error)
```

> [!info] Kotlin-нюанс
> Kotlin **отказался от checked-исключений** сознательно. Опыт Java показал: разработчики или игнорируют checked exceptions (`catch (e: Exception) {}`), или оборачивают в RuntimeException. Вместо этого Kotlin предлагает `Result<T>` и sealed-классы для явного моделирования ошибок.

---

## Три категории ошибок

Прежде чем выбирать механизм — определи, с каким типом ошибки имеешь дело:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      КАТЕГОРИИ ОШИБОК                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. ВОССТАНОВИМЫЕ (Recoverable)                                    │
│     ├── Валидация пользовательского ввода  → вернуть ошибку        │
│     ├── Таймаут сети                       → retry с backoff       │
│     ├── Ресурс временно занят              → подождать, повторить  │
│     └── Ожидаемый бизнес-кейс             → обработать корректно  │
│                                                                     │
│  2. НЕВОССТАНОВИМЫЕ (Unrecoverable)                                │
│     ├── OutOfMemoryError                   → crash                 │
│     ├── Повреждённые данные                → crash + alert         │
│     ├── Отсутствует конфигурация           → fail at startup       │
│     └── Баг в коде                         → crash + fix code      │
│                                                                     │
│  3. ФАТАЛЬНЫЕ (Panic)                                              │
│     ├── Обнаружен security breach          → немедленный shutdown  │
│     ├── Нарушена целостность данных        → stop, не портить ещё  │
│     └── Невозможное состояние              → bug! crash + контекст │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Правило:** Восстановимые → `Result` / sealed class. Невосстановимые → `throw`. Фатальные → `error()` + shutdown.

---

## Система исключений в Kotlin

### Все исключения — unchecked

В Kotlin нет checked exceptions. Любое исключение можно не ловить, и компилятор не скажет ни слова. Это упрощает код, но перекладывает ответственность на разработчика.

```kotlin
// Kotlin — компилятор НЕ заставляет обрабатывать
fun readFile(path: String): String =
    java.io.File(path).readText() // может бросить IOException — но компилятор молчит

// Java — компилятор ЗАСТАВЛЯЛ обрабатывать checked exception
// void readFile(String path) throws IOException { ... }
```

### try / catch / finally

Базовый механизм — знакомый и рабочий:

```kotlin
fun parseJson(raw: String): Config {
    return try {
        json.decodeFromString<Config>(raw)
    } catch (e: SerializationException) {
        logger.warn { "Невалидный JSON: ${e.message}" }
        Config.DEFAULT
    } catch (e: IllegalArgumentException) {
        logger.error(e) { "Неожиданная ошибка парсинга" }
        throw ConfigurationException("Не удалось прочитать конфигурацию", e)
    } finally {
        metrics.increment("config.parse.attempts")
    }
}
```

> [!info] Kotlin-нюанс
> `try/catch` в Kotlin — **выражение**, возвращающее значение. Не нужен отдельный `var result`.

### throw как выражение

`throw` в Kotlin имеет тип `Nothing` — подтип всех типов. Это позволяет использовать его в Elvis-операторе и в `when`:

```kotlin
// throw в Elvis-операторе
val user = userRepository.findById(id)
    ?: throw UserNotFoundException("User $id not found")

// throw в when
fun statusToCode(status: Status): Int = when (status) {
    Status.OK -> 200
    Status.NOT_FOUND -> 404
    Status.ERROR -> 500
    // Если добавят новый статус — компилятор предупредит (если sealed)
}

// Функция, которая НИКОГДА не возвращает
fun fail(message: String): Nothing {
    logger.error { message }
    throw IllegalStateException(message)
}

// Nothing позволяет использовать в любом контексте типов
val config: Config = loadConfig() ?: fail("Config not found")
```

### Preconditions: require, check, error

Kotlin предлагает встроенные функции для проверки предусловий — вместо ручного `if (...) throw ...`:

```kotlin
fun transferMoney(from: Account, to: Account, amount: BigDecimal) {
    // require → IllegalArgumentException (проверка АРГУМЕНТОВ)
    require(amount > BigDecimal.ZERO) { "Сумма должна быть положительной: $amount" }
    require(from.id != to.id) { "Нельзя перевести самому себе" }

    // check → IllegalStateException (проверка СОСТОЯНИЯ)
    check(from.isActive) { "Аккаунт ${from.id} деактивирован" }
    check(from.balance >= amount) { "Недостаточно средств: ${from.balance} < $amount" }

    // requireNotNull → IllegalArgumentException + smart-cast
    val fromCurrency = requireNotNull(from.currency) { "Валюта не задана для ${from.id}" }

    // checkNotNull → IllegalStateException + smart-cast
    val exchangeRate = checkNotNull(rateProvider.getRate(fromCurrency)) {
        "Курс для $fromCurrency недоступен"
    }

    // error → IllegalStateException (невозможное состояние)
    val fee = when (from.tier) {
        Tier.STANDARD -> amount * BigDecimal("0.01")
        Tier.PREMIUM -> BigDecimal.ZERO
        // Если добавят новый Tier — упадёт с понятным сообщением
        else -> error("Неизвестный tier: ${from.tier}")
    }

    from.withdraw(amount + fee)
    to.deposit(amount)
}
```

| Функция | Бросает | Когда использовать |
|---------|---------|-------------------|
| `require(condition)` | `IllegalArgumentException` | Проверка **аргументов** функции |
| `requireNotNull(value)` | `IllegalArgumentException` | Аргумент не должен быть null |
| `check(condition)` | `IllegalStateException` | Проверка **состояния** объекта |
| `checkNotNull(value)` | `IllegalStateException` | Состояние не должно быть null |
| `error(message)` | `IllegalStateException` | Невозможное / неожиданное состояние |

---

## Kotlin Result\<T\>

Начиная с Kotlin 1.5, `Result<T>` можно свободно использовать как возвращаемый тип функций (раньше компилятор запрещал это — ограничение было снято, так как команда Kotlin не нашла целесообразного способа изменить семантику null-safety операторов для Result).

### runCatching — обёртка над try/catch

```kotlin
// Вместо try/catch — получаем Result<T>
val result: Result<User> = runCatching {
    userApi.fetchUser(userId)
}

// Эквивалентно:
val result: Result<User> = try {
    Result.success(userApi.fetchUser(userId))
} catch (e: Throwable) {
    Result.failure(e)
}
```

### Извлечение значения

```kotlin
val result = runCatching { parseConfig(raw) }

// Безопасное извлечение
val config1: Config? = result.getOrNull()
val config2: Config = result.getOrDefault(Config.DEFAULT)
val config3: Config = result.getOrElse { error ->
    logger.warn { "Fallback config: ${error.message}" }
    Config.DEFAULT
}

// Опасное извлечение — бросит исключение если failure
val config4: Config = result.getOrThrow()
```

### Цепочки преобразований

Главная сила `Result` — функциональное комбинирование:

```kotlin
fun loadUserProfile(userId: String): Result<UserProfile> =
    runCatching { userApi.fetchUser(userId) }         // Result<UserDto>
        .map { dto -> dto.toDomain() }                 // Result<User>
        .mapCatching { user ->                          // может бросить
            val avatar = avatarService.download(user.avatarUrl)
            UserProfile(user, avatar)
        }
        .recover { error ->                             // fallback при ошибке
            when (error) {
                is NetworkException -> UserProfile.OFFLINE_STUB
                else -> throw error                     // пробросить дальше
            }
        }
        .onSuccess { profile ->
            cache.put(userId, profile)
            logger.info { "Профиль загружен: ${profile.name}" }
        }
        .onFailure { error ->
            logger.error(error) { "Не удалось загрузить профиль $userId" }
            metrics.increment("profile.load.failures")
        }
```

### Сравнение: Result vs try/catch

```kotlin
// ═══ try/catch: императивный стиль ═══
fun fetchAndSave(url: String): User? {
    val response = try {
        httpClient.get(url)
    } catch (e: IOException) {
        logger.error(e) { "Network error" }
        return null
    }

    val user = try {
        json.decodeFromString<User>(response.body)
    } catch (e: SerializationException) {
        logger.error(e) { "Parse error" }
        return null
    }

    try {
        database.save(user)
    } catch (e: SQLException) {
        logger.error(e) { "DB error" }
        return null
    }

    return user
}

// ═══ Result: функциональные цепочки ═══
fun fetchAndSave(url: String): Result<User> =
    runCatching { httpClient.get(url) }
        .mapCatching { response -> json.decodeFromString<User>(response.body) }
        .mapCatching { user -> database.save(user); user }
        .onFailure { error -> logger.error(error) { "Pipeline failed" } }
```

> [!warning] Осторожно с runCatching в корутинах
> `runCatching` ловит **все** `Throwable`, включая `CancellationException`. Это нарушает structured concurrency! В корутинах используй обёртку:
> ```kotlin
> // Безопасная версия для корутин
> suspend inline fun <T> runSuspendCatching(
>     block: () -> T
> ): Result<T> = try {
>     Result.success(block())
> } catch (e: CancellationException) {
>     throw e  // НЕ перехватываем — пусть корутина отменится
> } catch (e: Throwable) {
>     Result.failure(e)
> }
> ```

---

## Sealed class: типизированные иерархии ошибок

`Result<T>` хорош, когда ошибка — это просто `Throwable`. Но часто нужно различать *виды* ошибок на уровне типов, без наследования от `Exception`:

```kotlin
sealed interface AppError {
    data class NetworkError(
        val code: Int,
        val url: String,
        val cause: Throwable? = null
    ) : AppError

    data class ValidationError(
        val field: String,
        val reason: String
    ) : AppError

    data class DatabaseError(
        val query: String,
        val cause: Throwable
    ) : AppError

    data object Unauthorized : AppError
    data object RateLimited : AppError
}
```

### Exhaustive when — компилятор гарантирует полноту

```kotlin
fun handleError(error: AppError): HttpResponse = when (error) {
    is AppError.NetworkError -> HttpResponse(
        status = 502,
        body = "Upstream service error: ${error.code}"
    )
    is AppError.ValidationError -> HttpResponse(
        status = 422,
        body = "Invalid ${error.field}: ${error.reason}"
    )
    is AppError.DatabaseError -> {
        logger.error(error.cause) { "DB error: ${error.query}" }
        HttpResponse(status = 500, body = "Internal error")
    }
    AppError.Unauthorized -> HttpResponse(status = 401, body = "Unauthorized")
    AppError.RateLimited -> HttpResponse(status = 429, body = "Too many requests")
    // Если добавят новый тип — код НЕ скомпилируется без обработки!
}
```

### Sealed Result: свой тип-обёртка

Паттерн, популярный в Android-разработке — кастомный `Result` на sealed-классах:

```kotlin
sealed interface Result<out T> {
    data class Success<T>(val data: T) : Result<T>
    data class Error(val error: AppError) : Result<Nothing>
    data object Loading : Result<Nothing>
}

// Удобные extension-функции
inline fun <T, R> Result<T>.map(transform: (T) -> R): Result<R> = when (this) {
    is Result.Success -> Result.Success(transform(data))
    is Result.Error -> this
    is Result.Loading -> this
}

inline fun <T> Result<T>.onSuccess(action: (T) -> Unit): Result<T> {
    if (this is Result.Success) action(data)
    return this
}

inline fun <T> Result<T>.getOrElse(fallback: (AppError) -> T): T = when (this) {
    is Result.Success -> data
    is Result.Error -> fallback(error)
    is Result.Loading -> throw IllegalStateException("Still loading")
}
```

### Использование в репозитории

```kotlin
class UserRepository(
    private val api: UserApi,
    private val db: UserDao,
    private val mapper: UserMapper
) {
    suspend fun getUser(id: String): Result<User> {
        // Валидация на входе
        if (id.isBlank()) {
            return Result.Error(AppError.ValidationError("id", "не может быть пустым"))
        }

        return try {
            val dto = api.fetchUser(id)
            val user = mapper.toDomain(dto)
            db.cache(user)
            Result.Success(user)
        } catch (e: HttpException) {
            when (e.code) {
                401 -> Result.Error(AppError.Unauthorized)
                429 -> Result.Error(AppError.RateLimited)
                else -> Result.Error(AppError.NetworkError(e.code, "/users/$id", e))
            }
        } catch (e: IOException) {
            // Сеть недоступна — пробуем кеш
            val cached = db.findById(id)
            if (cached != null) Result.Success(cached)
            else Result.Error(AppError.NetworkError(0, "/users/$id", e))
        } catch (e: Exception) {
            Result.Error(AppError.DatabaseError("getUser($id)", e))
        }
    }
}
```

---

## Arrow Either\<E, A\>

Arrow — функциональная библиотека для Kotlin, предлагающая `Either<E, A>` для типизированных ошибок.

### Основы Either

```kotlin
import arrow.core.Either
import arrow.core.left
import arrow.core.right

sealed interface UserError {
    data class NotFound(val id: String) : UserError
    data class InvalidEmail(val email: String) : UserError
    data object Banned : UserError
}

// Left — ошибка, Right — успех (мнемоника: "right" = "правильно")
fun findUser(id: String): Either<UserError, User> {
    val user = database.findById(id)
        ?: return UserError.NotFound(id).left()

    if (user.isBanned) return UserError.Banned.left()

    return user.right()
}

// Использование
when (val result = findUser("123")) {
    is Either.Left -> handleError(result.value)
    is Either.Right -> showUser(result.value)
}
```

### Either builder и Raise DSL (Arrow 1.2+)

Начиная с Arrow 1.2, вместо ручного `left()`/`right()` можно использовать `either { }` builder и `Raise` DSL:

```kotlin
import arrow.core.raise.either
import arrow.core.raise.ensure
import arrow.core.raise.ensureNotNull

fun createUser(email: String, age: Int): Either<UserError, User> = either {
    // ensure — аналог require, но с типизированной ошибкой
    ensure(email.contains("@")) { UserError.InvalidEmail(email) }
    ensure(age >= 18) { UserError.TooYoung(age) }

    // ensureNotNull — аналог requireNotNull
    val domain = ensureNotNull(extractDomain(email)) {
        UserError.InvalidEmail(email)
    }

    // bind() — извлекает Right или short-circuits с Left
    val existingUser = findUserByEmail(email) // возвращает Either<UserError, User?>
    val isNew = existingUser.bind() == null

    ensure(isNew) { UserError.AlreadyExists(email) }

    User(email = email, age = age, domain = domain)
}
```

### Когда что использовать

```
┌──────────────────────────────────────────────────────────────────────┐
│               ВЫБОР МЕХАНИЗМА ОБРАБОТКИ ОШИБОК                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Kotlin Result<T>                                                    │
│  ├── Ошибка — это Throwable                                         │
│  ├── Одна операция, которая может упасть                            │
│  ├── Не нужна библиотека Arrow                                      │
│  └── Хорошо для: обёртка над legacy-кодом, простые случаи           │
│                                                                      │
│  Sealed class + custom Result                                        │
│  ├── Нужно моделировать бизнес-ошибки                               │
│  ├── Loading / Success / Error состояния (UI)                       │
│  ├── Не нужна монадическая композиция                               │
│  └── Хорошо для: Android UI, простые CRUD-операции                  │
│                                                                      │
│  Arrow Either<E, A>                                                  │
│  ├── Нужна функциональная композиция (map, flatMap, bind)           │
│  ├── Сложные пайплайны с несколькими точками отказа                  │
│  ├── Raise DSL для чистого кода                                      │
│  └── Хорошо для: backend, domain logic, compose pipelines           │
│                                                                      │
│  Exceptions (throw / try-catch)                                      │
│  ├── Баг в коде (IllegalStateException)                              │
│  ├── Нарушение контракта (require / check)                          │
│  ├── Инфраструктурные проблемы (OOM, StackOverflow)                 │
│  └── Хорошо для: preconditions, невосстановимые ошибки              │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Fail Fast: валидация на границах

Принцип: обнаружить ошибку **как можно раньше**, до того как система выполнит побочные эффекты.

```kotlin
// ❌ Fail slow — ошибка обнаружится позже
suspend fun processOrder(orderData: Map<String, Any?>) {
    val items = fetchItems(orderData["items"] as List<String>)  // может упасть
    val prices = calculatePrices(items)                          // тяжёлая работа
    // ... ещё работа
    val customerId = orderData["customer_id"] as? String         // может быть null
    val customer = getCustomer(customerId!!)                     // NPE!
    sendConfirmation(customer.email, prices)
}

// ✅ Fail fast — валидация СРАЗУ
suspend fun processOrder(orderData: Map<String, Any?>) {
    // Валидация на входе
    val customerId = requireNotNull(orderData["customer_id"] as? String) {
        "customer_id обязателен"
    }
    val itemIds = requireNotNull(orderData["items"] as? List<*>) {
        "items не может быть пустым"
    }
    require(itemIds.isNotEmpty()) { "Заказ должен содержать хотя бы один товар" }

    val customer = getCustomer(customerId)
        ?: throw NotFoundException("Клиент $customerId не найден")

    // Теперь спокойно работаем с провалидированными данными
    val items = fetchItems(itemIds.filterIsInstance<String>())
    val prices = calculatePrices(items)
    sendConfirmation(customer.email, prices)
}
```

### Guard Clauses — линейный код вместо вложенности

```kotlin
// ❌ Вложенные условия — сложно читать
fun getInsuranceAmount(employee: Employee?): BigDecimal {
    var result = BigDecimal.ZERO
    if (employee != null) {
        if (employee.isActive) {
            if (employee.hasInsurance) {
                employee.insurancePlan?.let {
                    result = it.amount
                }
            }
        }
    }
    return result
}

// ✅ Guard clauses — линейный код
fun getInsuranceAmount(employee: Employee?): BigDecimal {
    if (employee == null) return BigDecimal.ZERO
    if (!employee.isActive) return BigDecimal.ZERO
    if (!employee.hasInsurance) return BigDecimal.ZERO
    return employee.insurancePlan?.amount ?: BigDecimal.ZERO
}

// ✅✅ Kotlin-идиома — ещё короче
fun getInsuranceAmount(employee: Employee?): BigDecimal =
    employee
        ?.takeIf { it.isActive }
        ?.takeIf { it.hasInsurance }
        ?.insurancePlan
        ?.amount
        ?: BigDecimal.ZERO
```

---

## Railway-Oriented Programming

Метафора двух путей: **Success Track** и **Failure Track**. Каждый шаг возвращает результат. Если шаг «упал» — остальные пропускаются, ошибка катится по красному пути.

```
  Input ──► [Validate] ──► [Transform] ──► [Save] ──► [Notify] ──► Output
                │               │            │           │
                ▼               ▼            ▼           ▼
  Error Track ══════════════════════════════════════════════════► Error
```

### Реализация на Kotlin с sealed-классами

```kotlin
sealed interface PipelineResult<out T> {
    data class Success<T>(val value: T) : PipelineResult<T>
    data class Failure(val error: AppError) : PipelineResult<Nothing>
}

// Extension для Railway-oriented цепочек
inline fun <T, R> PipelineResult<T>.flatMap(
    transform: (T) -> PipelineResult<R>
): PipelineResult<R> = when (this) {
    is PipelineResult.Success -> transform(value)
    is PipelineResult.Failure -> this
}

inline fun <T, R> PipelineResult<T>.map(
    transform: (T) -> R
): PipelineResult<R> = when (this) {
    is PipelineResult.Success -> PipelineResult.Success(transform(value))
    is PipelineResult.Failure -> this
}

// Пайплайн регистрации пользователя
fun registerUser(request: RegistrationRequest): PipelineResult<User> =
    validateEmail(request.email)
        .flatMap { email -> validatePassword(request.password).map { pwd -> email to pwd } }
        .flatMap { (email, pwd) -> checkEmailUnique(email).map { email to pwd } }
        .flatMap { (email, pwd) -> createUser(email, pwd) }
        .also { result ->
            if (result is PipelineResult.Success) {
                sendWelcomeEmail(result.value) // side-effect
            }
        }

fun validateEmail(email: String): PipelineResult<String> =
    if (email.contains("@") && email.contains("."))
        PipelineResult.Success(email)
    else
        PipelineResult.Failure(AppError.ValidationError("email", "Невалидный формат"))

fun validatePassword(password: String): PipelineResult<String> {
    val errors = buildList {
        if (password.length < 8) add("Минимум 8 символов")
        if (password.none { it.isUpperCase() }) add("Нужна заглавная буква")
        if (password.none { it.isDigit() }) add("Нужна цифра")
    }
    return if (errors.isEmpty()) PipelineResult.Success(password)
    else PipelineResult.Failure(AppError.ValidationError("password", errors.joinToString("; ")))
}
```

### То же самое на Arrow Either

```kotlin
import arrow.core.raise.either

fun registerUser(request: RegistrationRequest): Either<AppError, User> = either {
    val email = validateEmail(request.email).bind()
    val password = validatePassword(request.password).bind()
    checkEmailUnique(email).bind()
    val user = createUser(email, password).bind()
    sendWelcomeEmail(user) // side-effect
    user
}
```

> [!tip] Сравни объём кода
> Arrow `either { }` builder делает Railway-oriented programming *встроенным в язык*. Вместо цепочек `flatMap` — линейный код с `bind()`.

---

## Обработка ошибок в корутинах

Корутины имеют свою модель распространения ошибок — **structured concurrency**. Исключение в дочерней корутине отменяет *всех* сиблингов и родителя.

### launch vs async — разное поведение

```kotlin
// launch: исключение ПРОБРАСЫВАЕТСЯ вверх по иерархии Job
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

scope.launch {
    throw RuntimeException("Boom!")
    // → отменяет родительскую Job (если не SupervisorJob)
    // → CoroutineExceptionHandler ловит
}

// async: исключение ОТКЛАДЫВАЕТСЯ до вызова await()
val deferred = scope.async {
    throw RuntimeException("Boom!")
}

try {
    deferred.await() // исключение бросается ЗДЕСЬ
} catch (e: RuntimeException) {
    println("Поймали: ${e.message}")
}
```

### SupervisorJob — изоляция сбоев

```kotlin
// Без SupervisorJob: одна ошибка убивает ВСЁ
coroutineScope {
    launch { fetchUsers() }        // ← отменится из-за ошибки ниже
    launch { throw IOException() } // ← ошибка
    launch { fetchProducts() }     // ← отменится из-за ошибки выше
}

// С supervisorScope: ошибки НЕ распространяются на сиблингов
supervisorScope {
    launch { fetchUsers() }        // ← продолжает работать
    launch { throw IOException() } // ← ошибка только здесь
    launch { fetchProducts() }     // ← продолжает работать
}
```

### CoroutineExceptionHandler — последний рубеж

```kotlin
val handler = CoroutineExceptionHandler { _, exception ->
    logger.error(exception) { "Необработанное исключение в корутине" }
    crashReporter.report(exception)
}

// Работает ТОЛЬКО с launch на корневых корутинах
val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main + handler)

scope.launch {
    // Если здесь бросить исключение — handler поймает
    riskyOperation()
}

scope.launch {
    // try/catch внутри launch — для конкретной обработки
    try {
        anotherRiskyOperation()
    } catch (e: SpecificException) {
        showErrorToUser(e.message)
    }
}
```

> [!warning] CoroutineExceptionHandler — не для восстановления
> Handler вызывается **после** завершения корутины. Восстановиться из него нельзя. Используйте `try/catch` внутри корутины для восстановимых ошибок.

### Полная схема обработки ошибок в корутинах

```
┌─────────────────────────────────────────────────────────────────────┐
│              ОБРАБОТКА ОШИБОК В КОРУТИНАХ                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  launch { ... }                     async { ... }                   │
│     │                                  │                            │
│     ▼                                  ▼                            │
│  Исключение бросается              Исключение сохраняется           │
│     │                              в Deferred<T>                    │
│     ▼                                  │                            │
│  try/catch внутри?                 await() бросает?                 │
│  ├── Да → обработано              ├── try/catch → обработано        │
│  └── Нет ▼                        └── Нет → propagation            │
│  Job → parent Job                      │                            │
│  ├── Regular Job → отменяет всех       │                            │
│  └── SupervisorJob → только себя       │                            │
│          │                             │                            │
│          ▼                             ▼                            │
│  CoroutineExceptionHandler        CoroutineExceptionHandler         │
│  (логирование, crash report)      (НЕ вызывается для async!)       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Null как ошибка: Kotlin null-safety

Kotlin борется с «billion dollar mistake» на уровне типов. Null может выступать как «мягкая ошибка»:

```kotlin
// ?.let — выполнить только если не null
fun processUser(userId: String?) {
    userId?.let { id ->
        val user = repository.findById(id)
        user?.let { showProfile(it) }
    }
}

// Elvis ?: — значение по умолчанию или бросить
val name = user?.name ?: "Гость"
val config = loadConfig() ?: throw ConfigMissingException()

// ?.also — логирование без нарушения цепочки
val user = cache.get(userId)
    ?.also { logger.debug { "Cache hit: $userId" } }
    ?: api.fetchUser(userId).also { cache.put(userId, it) }

// filterNotNull — очистка коллекций
val validUsers: List<User> = userIds
    .map { repository.findById(it) }  // List<User?>
    .filterNotNull()                    // List<User>

// mapNotNull — map + filterNotNull в одном
val emails: List<String> = users.mapNotNull { it.email }
```

> [!info] Kotlin-нюанс
> Используй `null` когда **отсутствие значения — нормальная ситуация** (пользователь без аватара). Используй `Result`/`Either` когда нужно **объяснить причину** отсутствия (сеть упала, нет прав доступа).

---

## Обработка ошибок по слоям

```
┌───────────────────────────────────────────────────────────────────┐
│  PRESENTATION (API / UI)                                          │
│  • Sealed Result → UI-состояние (Loading / Content / Error)      │
│  • HTTP-коды из AppError                                          │
│  • Скрыть внутренние детали от пользователя                      │
├───────────────────────────────────────────────────────────────────┤
│  APPLICATION (Use Cases)                                          │
│  • Оркестрация: retry → circuit breaker → fallback               │
│  • Перевод domain errors → app errors                            │
│  • Транзакционный откат                                           │
├───────────────────────────────────────────────────────────────────┤
│  DOMAIN (Business Logic)                                          │
│  • Sealed interface ошибок: ValidationError, NotFound...         │
│  • require/check для инвариантов                                  │
│  • Никаких HTTP-кодов, никаких исключений фреймворков            │
├───────────────────────────────────────────────────────────────────┤
│  INFRASTRUCTURE (DB, External APIs)                               │
│  • try/catch для внешних вызовов                                  │
│  • Оборачивание в доменные ошибки: IOException → NetworkError    │
│  • Добавление контекста (url, query, timeout)                    │
└───────────────────────────────────────────────────────────────────┘
```

### Пример: Ktor REST API с sealed errors

```kotlin
// Domain-ошибки
sealed interface OrderError {
    data class NotFound(val orderId: String) : OrderError
    data class InsufficientFunds(val balance: BigDecimal, val required: BigDecimal) : OrderError
    data class InvalidItem(val itemId: String, val reason: String) : OrderError
}

// Use case возвращает Either
class PlaceOrderUseCase(
    private val orderRepo: OrderRepository,
    private val paymentService: PaymentService
) {
    suspend fun execute(request: OrderRequest): Either<OrderError, Order> = either {
        val items = request.items.map { itemId ->
            ensureNotNull(orderRepo.findItem(itemId)) {
                OrderError.InvalidItem(itemId, "Товар не найден")
            }
        }

        val total = items.sumOf { it.price }
        val balance = paymentService.getBalance(request.userId).bind()
        ensure(balance >= total) {
            OrderError.InsufficientFunds(balance, total)
        }

        orderRepo.create(request.userId, items, total).bind()
    }
}

// Ktor routing — перевод ошибок в HTTP
fun Route.orderRoutes(placeOrder: PlaceOrderUseCase) {
    post("/orders") {
        val request = call.receive<OrderRequest>()

        when (val result = placeOrder.execute(request)) {
            is Either.Right -> call.respond(HttpStatusCode.Created, result.value)
            is Either.Left -> when (val error = result.value) {
                is OrderError.NotFound ->
                    call.respond(HttpStatusCode.NotFound, error.orderId)
                is OrderError.InsufficientFunds ->
                    call.respond(HttpStatusCode.PaymentRequired, "Недостаточно средств")
                is OrderError.InvalidItem ->
                    call.respond(HttpStatusCode.UnprocessableEntity, error.reason)
            }
        }
    }
}
```

---

## Антипаттерны

### 1. Pokemon Exception Handling — «ловлю их всех»

```kotlin
// ❌ Глотает ВСЕ ошибки, включая OOM и StackOverflow
try {
    doSomething()
} catch (e: Exception) {
    // "что-то пошло не так"
}

// ✅ Ловим конкретные исключения
try {
    doSomething()
} catch (e: IOException) {
    handleNetworkError(e)
} catch (e: SerializationException) {
    handleParseError(e)
}
```

### 2. Проглатывание исключений

```kotlin
// ❌ Исключение исчезает бесследно
try {
    saveToDatabase(data)
} catch (e: Exception) {
    // пустой блок — самый опасный антипаттерн
}

// ✅ Как минимум залогировать
try {
    saveToDatabase(data)
} catch (e: SQLException) {
    logger.error(e) { "Не удалось сохранить данные: ${data.id}" }
    throw DatabaseException("Save failed for ${data.id}", e)
}
```

### 3. Исключения для control flow

```kotlin
// ❌ Исключение как goto
fun findFirst(items: List<Item>, predicate: (Item) -> Boolean): Item? {
    try {
        items.forEach { item ->
            if (predicate(item)) throw FoundException(item) // WTF
        }
    } catch (e: FoundException) {
        return e.item
    }
    return null
}

// ✅ Нормальный control flow
fun findFirst(items: List<Item>, predicate: (Item) -> Boolean): Item? =
    items.firstOrNull(predicate)
```

### 4. Возврат null, когда нужна информация об ошибке

```kotlin
// ❌ Почему null? Сеть? Нет прав? Не найден?
fun getUser(id: String): User? { ... }

// ✅ Ошибка объясняет причину
fun getUser(id: String): Either<UserError, User> { ... }
// или
fun getUser(id: String): Result<User> { ... }
```

### 5. Несоблюдение иерархии ошибок

```kotlin
// ❌ Всё вперемешку — строки, исключения, data-классы
fun process(): Any = when {
    networkFail -> "network error"        // String
    validationFail -> ValidationError()    // data class
    authFail -> throw AuthException()      // exception
    else -> result
}

// ✅ Единая стратегия в рамках слоя
fun process(): Either<ProcessError, Result> = either {
    // Все ошибки — через sealed interface ProcessError
}
```

---

## Проверь себя

<details>
<summary>1. Чем отличается `require()` от `check()` в Kotlin?</summary>

**Ответ:**

- `require(condition)` бросает `IllegalArgumentException` — для проверки **аргументов** функции. Вызывающий передал невалидные данные.
- `check(condition)` бросает `IllegalStateException` — для проверки **состояния** объекта. Метод вызван в неподходящий момент жизненного цикла.

```kotlin
fun withdraw(amount: BigDecimal) {
    require(amount > BigDecimal.ZERO)  // аргумент
    check(isActive)                     // состояние объекта
}
```

</details>

<details>
<summary>2. Почему `runCatching` опасен в корутинах?</summary>

**Ответ:**

`runCatching` перехватывает **все** `Throwable`, включая `CancellationException`. В structured concurrency `CancellationException` — это не ошибка, а сигнал отмены. Перехватив его, вы нарушаете отмену корутины: родительская корутина думает, что дочерняя работает, хотя она должна была завершиться.

Решение — использовать обёртку `runSuspendCatching`, которая пробрасывает `CancellationException`.

</details>

<details>
<summary>3. Когда выбрать `Result<T>`, а когда sealed class?</summary>

**Ответ:**

- **`Result<T>`** — когда ошибка = `Throwable` и не нужно различать виды ошибок. Оборачивает одну операцию. Стандартная библиотека, без зависимостей.
- **Sealed class** — когда нужно моделировать конкретные бизнес-ошибки (`NotFound`, `Unauthorized`, `ValidationError`). Компилятор проверяет exhaustive `when`. Подходит для API-слоёв.

</details>

<details>
<summary>4. В чём разница обработки ошибок в `launch` и `async`?</summary>

**Ответ:**

- **`launch`**: исключение пробрасывается вверх по иерархии Job. Если нет `try/catch` внутри — отменяет родительскую Job (или попадает в `CoroutineExceptionHandler` при `SupervisorJob`).
- **`async`**: исключение сохраняется внутри `Deferred<T>` и бросается при вызове `await()`. `CoroutineExceptionHandler` **не** вызывается.

</details>

<details>
<summary>5. Что такое Railway-Oriented Programming?</summary>

**Ответ:**

Метафора двух путей: Success Track и Failure Track. Каждый шаг конвейера возвращает Result/Either. Если шаг возвращает ошибку — все последующие шаги пропускаются, ошибка «катится» по параллельному пути. Реализуется через `map`/`flatMap` на Result или через Arrow `either { }` builder с `bind()`.

</details>

---

## Ключевые карточки

Какие precondition-функции есть в Kotlin и что они бросают?
?
`require()` → IllegalArgumentException (аргументы), `check()` → IllegalStateException (состояние), `error()` → IllegalStateException (невозможное состояние). Также `requireNotNull()` и `checkNotNull()` для null-проверок с smart-cast.

Чем `Result<T>` отличается от `Either<E, A>` в Arrow?
?
`Result<T>` хранит `Throwable` — подходит для обёртки над кодом, который бросает исключения. `Either<E, A>` хранит **типизированную ошибку** `E` — подходит для бизнес-логики, где нужно различать виды ошибок. Arrow также предоставляет `Raise` DSL и `either { }` builder для линейного кода вместо цепочек `flatMap`.

Как работает `SupervisorJob` в корутинах?
?
`SupervisorJob` изолирует сбои: ошибка в дочерней корутине **не** отменяет родителя и сиблингов (в отличие от обычного `Job`, где одна ошибка отменяет всё). Используется в `supervisorScope { }` или при создании `CoroutineScope(SupervisorJob())`.

Почему `throw` в Kotlin имеет тип `Nothing`?
?
`Nothing` — подтип всех типов. Это позволяет использовать `throw` в любом контексте: Elvis-операторе (`val x = y ?: throw ...`), `when`, присваивании. Функции с возвращаемым типом `Nothing` никогда не завершаются нормально — компилятор знает это и позволяет smart-cast после вызова.

Что такое exhaustive `when` и зачем sealed-классы для ошибок?
?
Для sealed-типов компилятор проверяет, что `when` покрывает ВСЕ варианты. Если добавить новый тип ошибки — код не скомпилируется пока не обработаешь новый случай. Это гарантия на уровне компиляции, что ни одна ошибка не пропущена.

Когда использовать `null`, а когда `Result`/`Either`?
?
`null` — когда отсутствие значения **нормально** и не требует объяснения (опциональный аватар). `Result`/`Either` — когда нужно **объяснить причину** отсутствия (сеть упала, нет прав, невалидный формат). Мнемоника: если вызывающий код спросит «а ПОЧЕМУ null?» — нужен Result.

Какие три категории ошибок и как с ними поступать?
?
1) **Восстановимые** (сеть, валидация) → `Result`/`Either`, retry, fallback. 2) **Невосстановимые** (OOM, corrupted data) → crash, alert, fix code. 3) **Фатальные** (security breach) → немедленный shutdown, не допустить дальнейшей порчи.

В чём опасность пустого `catch`-блока?
?
Исключение **исчезает** бесследно. Программа продолжает работать в неопределённом состоянии — данные могут быть потеряны или повреждены, а разработчик никогда не узнает о проблеме. Как минимум нужно логировать: `catch (e: Exception) { logger.error(e) { "context" } }`.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[resilience-patterns]] | Retry, Circuit Breaker, Timeout — паттерны устойчивости к сбоям |
| Углубиться | [[functional-programming]] | Монады, функторы — теория за `map`/`flatMap`/`bind` |
| Практика | [[kotlin-coroutines]] | Structured concurrency, SupervisorJob, cancellation |
| Смежная тема | [[solid-principles]] | Принципы чистого кода и SOLID |
| Android | [[android-clean-architecture]] | Error handling через sealed class в Domain layer |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

## Источники

- Nygard M. — *Release It! Design and Deploy Production-Ready Software* (2nd ed., Pragmatic Bookshelf, 2018) — философия обработки ошибок в production-системах
- Martin R. — *Clean Architecture* (Prentice Hall, 2017) — обработка ошибок по слоям, Screaming Architecture
- Elizarov R. — [Kotlin Coroutines Exception Handling](https://kotlinlang.org/docs/exception-handling.html) — официальная документация по ошибкам в корутинах
- [Kotlin KEEP: Result type](https://github.com/Kotlin/KEEP/blob/master/proposals/stdlib/result.md) — proposal и история ограничений Result
- [KEEP PR #244: Lift Result restrictions](https://github.com/Kotlin/KEEP/pull/244) — снятие ограничений в Kotlin 1.5
- [Arrow: Working with Typed Errors](https://arrow-kt.io/learn/typed-errors/working-with-typed-errors/) — Raise DSL, Either builder
- [Arrow: Circuit Breaker](https://arrow-kt.io/learn/resilience/circuitbreaker/) — реализация Circuit Breaker в Arrow
- Phauer S. — [Sealed Classes Instead of Exceptions in Kotlin](https://phauer.com/2019/sealed-classes-exceptions-kotlin/) — практический гайд по sealed-ошибкам
- [Kotlin API: Result](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin/-result/) — stdlib Reference
- Marcin Moskala — *Effective Kotlin* (Kt. Academy, 2022) — Item 7: Prefer Result type when the lack of result is possible
- [ROP: Railway Oriented Programming](https://fsharpforfunandprofit.com/rop/) — Scott Wlaschin, оригинальная концепция

---

*Проверено: 2026-02-19*
