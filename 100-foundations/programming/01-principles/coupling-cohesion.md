---
title: "Coupling и Cohesion: фундаментальные метрики дизайна"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/design
  - topic/kotlin
related:
  - "[[solid-principles]]"
  - "[[composition-vs-inheritance]]"
  - "[[oop-fundamentals]]"
  - "[[clean-code]]"
---

# Coupling и Cohesion: фундаментальные метрики дизайна

SOLID появился в 2000-х. Clean Architecture -- в 2017. А coupling и cohesion сформулировали Ларри Константин и Эдвард Йордан в **1979 году**, в книге "Structured Design". Это старейшие метрики качества кода, и они более фундаментальны, чем любой набор принципов: SOLID, GRASP, DRY -- все они являются **следствиями** стремления к low coupling и high cohesion. Если вы понимаете только две вещи о дизайне -- пусть это будут coupling и cohesion.

---

## Теоретические основы

> **Coupling (связанность)** — степень взаимозависимости между модулями системы. **Cohesion (связность)** — степень, в которой элементы внутри одного модуля функционально связаны между собой. Формализованы Ларри Константином и Эдвардом Йорданом (1974/1979) как количественные метрики качества модульного дизайна.

### Формальные определения (Stevens, Myers, Constantine, 1974)

Оригинальная статья в IBM Systems Journal определила:
- **Coupling**: мера силы связи между двумя модулями. Минимизация coupling → минимизация «ripple effect» (изменение в одном модуле вызывает каскад изменений)
- **Cohesion**: мера функциональной связи между элементами одного модуля. Максимизация cohesion → модуль делает одну вещь хорошо

### Математическая модель (Martin, 2002)

Robert Martin формализовал coupling через метрики:

| Метрика | Формула | Что измеряет |
|---------|---------|-------------|
| **Ca** (Afferent coupling) | Число классов снаружи, зависящих от модуля | Ответственность (кто от нас зависит) |
| **Ce** (Efferent coupling) | Число классов снаружи, от которых зависит модуль | Зависимость (от кого мы зависим) |
| **Instability (I)** | Ce / (Ca + Ce), диапазон [0, 1] | 0 = стабильный, 1 = нестабильный |
| **Abstractness (A)** | Абстрактные классы / Все классы, [0, 1] | 0 = конкретный, 1 = абстрактный |
| **Distance (D)** | \|A + I - 1\| | Расстояние от «Main Sequence» (идеал D=0) |

### Связь с другими принципами

- **SRP** → следствие high cohesion (один модуль = одна ответственность)
- **DIP** → механизм снижения coupling (зависимость от абстракций)
- **ISP** → минимизация coupling через узкие интерфейсы
- **Conway's Law** → coupling между модулями отражает coupling между командами

> **См. также**: [[solid-principles]] — SOLID как следствие low coupling + high cohesion, [[clean-code]] — метрики сложности, [[microservices-vs-monolith]] — coupling на уровне сервисов

---



Coupling (связанность) отвечает на вопрос: **насколько модули зависят друг от друга?**
Cohesion (связность) отвечает на вопрос: **насколько элементы внутри модуля связаны между собой?**

Аналогия: представьте отделы в компании. **Cohesion** -- это насколько сотрудники одного отдела работают над одной задачей (а не каждый занят чем-то своим). **Coupling** -- это насколько отделы зависят друг от друга (нужно ли маркетингу ждать одобрения бухгалтерии для каждого решения).

Идеал: каждый отдел самодостаточен (high cohesion), отделы взаимодействуют только через чёткие интерфейсы (low coupling).

```
    High Cohesion + Low Coupling = Хороший дизайн
    Low Cohesion + High Coupling = Спагетти-код

    ┌───────────────────────────────────────────┐
    │         Cohesion (связность)              │
    │         LOW ──────────────── HIGH          │
    │  C  H  │ GOD OBJECT      │ IDEAL         │
    │  o  I  │ Всё связано,    │ Модули         │
    │  u  G  │ внутри каша     │ самодостаточны │
    │  p  H  ├────────────────┼────────────────│
    │  l     │ WORST CASE     │ LIBRARIES      │
    │  i  L  │ Хаос: ни       │ Мало связей    │
    │  n  O  │ внешней, ни    │ между модулями,│
    │  g  W  │ внутренней     │ но внутри      │
    │        │ логики         │ тоже слабо     │
    └───────────────────────────────────────────┘
```

---

## Cohesion: 7 типов от худшего к лучшему

Константин и Йордан определили 7 уровней cohesion. Запоминать все не обязательно, но полезно видеть спектр: от полного хаоса (coincidental) до идеала (functional).

### 1. Coincidental (случайная) -- ХУДШАЯ

Элементы модуля не связаны никак. Оказались рядом случайно.

```kotlin
// ❌ Coincidental cohesion: "Utils-класс" со всем подряд
object AppUtils {
    fun formatDate(date: LocalDate): String =
        date.format(DateTimeFormatter.ISO_DATE)

    fun calculateTax(amount: Double): Double =
        amount * 0.13

    fun isValidEmail(email: String): Boolean =
        email.contains("@") && email.contains(".")

    fun playSound(resourceId: Int) { /* ... */ }

    fun compressImage(bitmap: ByteArray): ByteArray = TODO()
}
// Форматирование дат, налоги, email, звук, изображения -- ничего общего
```

### 2. Logical (логическая)

Элементы делают **логически похожие**, но **функционально разные** вещи. Объединены "по типу операции".

```kotlin
// ❌ Logical cohesion: всё, что "валидирует" -- в одном месте
object Validators {
    fun validateEmail(email: String): Boolean = email.contains("@")
    fun validateAge(age: Int): Boolean = age in 0..150
    fun validateJson(json: String): Boolean = TODO("JSON schema validation")
    fun validateDatabaseConnection(url: String): Boolean = TODO()
}
// Связь только в том, что все "валидируют". Предметные области разные.
```

### 3. Temporal (временна'я)

Элементы выполняются в **одно и то же время** (при запуске, при ошибке, при завершении).

```kotlin
// ⚠️ Temporal cohesion: всё, что делаем при запуске
class AppInitializer {
    fun onAppStart() {
        initializeDatabase()
        loadConfiguration()
        setupAnalytics()
        preloadCache()
        registerNotificationChannels()
    }

    private fun initializeDatabase() { /* ... */ }
    private fun loadConfiguration() { /* ... */ }
    private fun setupAnalytics() { /* ... */ }
    private fun preloadCache() { /* ... */ }
    private fun registerNotificationChannels() { /* ... */ }
}
// Все действия запускаются "при старте", но логически не связаны
```

### 4. Procedural (процедурная)

Элементы выполняются **в определённом порядке**, но работают с **разными данными**.

```kotlin
// ⚠️ Procedural cohesion: последовательность шагов
class ReportGenerator {
    fun generateMonthlyReport() {
        checkPermissions()      // Данные: права пользователя
        fetchData()             // Данные: SQL-запрос
        formatReport()          // Данные: шаблон отчёта
        sendEmail()             // Данные: адрес получателя
    }

    private fun checkPermissions() { /* ... */ }
    private fun fetchData() { /* ... */ }
    private fun formatReport() { /* ... */ }
    private fun sendEmail() { /* ... */ }
}
// Шаги в фиксированном порядке, но каждый работает со своими данными
```

### 5. Communicational (коммуникационная) -- ХОРОШАЯ

Элементы работают с **одними и теми же данными**.

```kotlin
// ✅ Communicational cohesion: все операции над User
class UserRepository(private val db: Database) {
    fun findById(id: Long): User? =
        db.query("SELECT * FROM users WHERE id = ?", id)

    fun save(user: User): Long =
        db.insert("users", user.toContentValues())

    fun update(user: User) =
        db.update("users", user.toContentValues(), "id = ?", user.id)

    fun delete(id: Long) =
        db.delete("users", "id = ?", id)

    fun findByEmail(email: String): User? =
        db.query("SELECT * FROM users WHERE email = ?", email)
}
// Все методы работают с одной сущностью: User
```

### 6. Sequential (последовательная) -- ОЧЕНЬ ХОРОШАЯ

Выход одного элемента -- вход следующего. Конвейер.

```kotlin
// ✅ Sequential cohesion: pipeline обработки
class ImageProcessor {
    fun process(raw: ByteArray): ProcessedImage {
        val decoded = decode(raw)           // ByteArray → Bitmap
        val resized = resize(decoded)       // Bitmap → Bitmap (меньше)
        val filtered = applyFilter(resized) // Bitmap → Bitmap (с фильтром)
        val compressed = compress(filtered) // Bitmap → CompressedData
        return ProcessedImage(compressed)   // CompressedData → ProcessedImage
    }

    private fun decode(raw: ByteArray): Bitmap = TODO()
    private fun resize(bitmap: Bitmap): Bitmap = TODO()
    private fun applyFilter(bitmap: Bitmap): Bitmap = TODO()
    private fun compress(bitmap: Bitmap): CompressedData = TODO()
}
// Каждый шаг принимает результат предыдущего -- конвейер
```

### 7. Functional (функциональная) -- ЛУЧШАЯ

Все элементы работают вместе для выполнения **одной чётко определённой задачи**.

```kotlin
// ✅ Functional cohesion: одна задача -- вычисление цены заказа
class OrderPriceCalculator(
    private val taxRate: Double,
    private val discountPolicy: DiscountPolicy
) {
    fun calculate(items: List<OrderItem>): OrderPrice {
        val subtotal = calculateSubtotal(items)
        val discount = discountPolicy.calculateDiscount(subtotal, items)
        val tax = calculateTax(subtotal - discount)
        return OrderPrice(subtotal, discount, tax)
    }

    private fun calculateSubtotal(items: List<OrderItem>): Double =
        items.sumOf { it.price * it.quantity }

    private fun calculateTax(taxableAmount: Double): Double =
        taxableAmount * taxRate
}

data class OrderPrice(
    val subtotal: Double,
    val discount: Double,
    val tax: Double
) {
    val total: Double get() = subtotal - discount + tax
}
// Всё в классе работает на одну цель: вычислить цену
```

> [!info] Kotlin-нюанс
> `data class OrderPrice` -- пример функционально когезивного класса: все свойства (`subtotal`, `discount`, `tax`) нужны для одной цели (цена заказа), вычисляемое свойство `total` агрегирует остальные. Kotlin `data class` по природе способствует высокой cohesion: он вынуждает объявить все поля в primary constructor, делая их явными и сфокусированными.

---

## Coupling: 7 типов от худшего к лучшему

### 1. Content Coupling (по содержимому) -- ХУДШИЙ

Один модуль **напрямую обращается** к внутренним данным другого.

```kotlin
// ❌ Content coupling: прямой доступ к internal state
class OrderProcessor {
    // Прямое обращение к приватным деталям другого класса через рефлексию
    fun forceApprove(order: Order) {
        val field = order::class.java.getDeclaredField("status")
        field.isAccessible = true
        field.set(order, "APPROVED") // 💥 Лезем внутрь чужого класса!
    }
}

// ❌ Ещё хуже: глобальные переменные
var globalDatabase: Database? = null  // Кто угодно может изменить

class ModuleA {
    fun init() { globalDatabase = Database.connect() }
}

class ModuleB {
    fun query() { globalDatabase!!.execute("SELECT ...") } // 💥
}
```

### 2. Common Coupling (общая)

Модули разделяют **глобальное состояние**.

```kotlin
// ❌ Common coupling: разделяемый mutable state
object AppState {
    var currentUser: User? = null
    var isOnline: Boolean = true
    var theme: String = "light"
}

class LoginScreen {
    fun login(user: User) {
        AppState.currentUser = user  // Пишем в общее состояние
    }
}

class ProfileScreen {
    fun show() {
        val user = AppState.currentUser  // Читаем из общего состояния
        // Если LoginScreen изменит currentUser между чтением и использованием?
    }
}
```

### 3. External Coupling (внешняя)

Модули зависят от **одного внешнего формата**, протокола или API.

```kotlin
// ⚠️ External coupling: оба модуля зависят от формата JSON API
class UserService {
    fun getUser(id: Long): JSONObject {
        // Если API изменит формат -- сломается и этот класс, и все потребители
        return api.get("/users/$id")
    }
}

class UserDisplay {
    fun show(json: JSONObject) {
        val name = json.getString("user_name")  // Хардкод ключа API
        val age = json.getInt("user_age")        // Изменится ключ -- сломается
    }
}
```

### 4. Control Coupling (по управлению)

Один модуль передаёт **управляющий флаг**, определяющий логику другого.

```kotlin
// ❌ Control coupling: флаг управляет поведением
class ReportService {
    fun generateReport(type: String): Report {
        return when (type) {
            "pdf" -> generatePdf()
            "excel" -> generateExcel()
            "html" -> generateHtml()
            else -> throw IllegalArgumentException("Unknown type: $type")
        }
    }
    // Вызывающий код ЗНАЕТ о внутренних типах ReportService
}

// ✅ Лучше: Strategy через интерфейс
interface ReportGenerator {
    fun generate(): Report
}

class PdfReportGenerator : ReportGenerator {
    override fun generate(): Report = TODO()
}

class ReportService(private val generator: ReportGenerator) {
    fun generateReport(): Report = generator.generate()
    // Вызывающий код НЕ знает о типах -- передаёт реализацию
}
```

### 5. Stamp Coupling (по штампу)

Модули разделяют **составную структуру данных**, но используют **только часть** её.

```kotlin
// ⚠️ Stamp coupling: функция получает весь User, но использует только email
fun sendWelcomeEmail(user: User) {
    emailService.send(user.email, "Welcome!")
    // user.name, user.age, user.address -- не используются, но мы от них зависим
}

// ✅ Лучше: передавать только нужные данные
fun sendWelcomeEmail(email: String) {
    emailService.send(email, "Welcome!")
}

// ✅ Или создать узкий интерфейс
interface HasEmail {
    val email: String
}

data class User(
    val name: String,
    override val email: String,
    val age: Int
) : HasEmail

fun sendWelcomeEmail(recipient: HasEmail) {
    emailService.send(recipient.email, "Welcome!")
}
```

### 6. Data Coupling (по данным) -- ХОРОШАЯ

Модули обмениваются только **простыми данными** через параметры.

```kotlin
// ✅ Data coupling: только нужные данные, только примитивы
fun calculateShippingCost(weight: Double, distance: Double): Double {
    return weight * 0.5 + distance * 0.1
}

// Вызов:
val cost = calculateShippingCost(weight = 2.5, distance = 150.0)
```

### 7. Message Coupling (по сообщениям) -- ЛУЧШАЯ

Модули взаимодействуют только через **отправку сообщений** (вызов метода без параметров, или события).

```kotlin
// ✅ Message coupling: общение через события
interface Event
data class UserLoggedIn(val userId: String) : Event
data class OrderCreated(val orderId: String) : Event

interface EventBus {
    fun publish(event: Event)
    fun subscribe(handler: (Event) -> Unit)
}

class AuthModule(private val eventBus: EventBus) {
    fun login(credentials: Credentials) {
        val user = authenticate(credentials)
        eventBus.publish(UserLoggedIn(user.id))
        // AuthModule НЕ знает, кто подписан на событие
    }
}

class AnalyticsModule(eventBus: EventBus) {
    init {
        eventBus.subscribe { event ->
            when (event) {
                is UserLoggedIn -> trackLogin(event.userId)
                is OrderCreated -> trackOrder(event.orderId)
            }
        }
    }
}
// Модули НЕ знают друг о друге -- только о формате событий
```

---

## Kotlin-инструменты для снижения Coupling

### `internal`: граница модуля

```kotlin
// module: payment-core
// Публичный API модуля
class PaymentProcessor internal constructor(
    private val gateway: PaymentGateway
) {
    fun processPayment(amount: Double): PaymentResult {
        return gateway.charge(amount)
    }
}

// internal -- виден только внутри модуля payment-core
internal class StripeGateway : PaymentGateway {
    override fun charge(amount: Double): PaymentResult = TODO()
}

// Фабрика -- единственная точка входа
object PaymentModule {
    fun createProcessor(): PaymentProcessor =
        PaymentProcessor(StripeGateway()) // StripeGateway не виден извне!
}
```

> [!info] Kotlin-нюанс
> `internal` в Kotlin -- это **модульная видимость**: класс виден только внутри одного Gradle-модуля (или IntelliJ IDEA модуля). В Java нет аналога -- `package-private` ограничивает видимость пакетом, но не модулем. В multi-module Kotlin проекте `internal` позволяет строить чёткие границы: публичный API модуля минимален, реализация скрыта.

### `sealed class`: закрытые иерархии

```kotlin
// Все подтипы известны -- внешний код НЕ может создать новый
sealed interface DatabaseError {
    data class ConnectionFailed(val host: String, val port: Int) : DatabaseError
    data class QueryFailed(val query: String, val cause: Throwable) : DatabaseError
    data class Timeout(val durationMs: Long) : DatabaseError
    data object NotInitialized : DatabaseError
}

fun handleError(error: DatabaseError) = when (error) {
    is DatabaseError.ConnectionFailed -> reconnect(error.host, error.port)
    is DatabaseError.QueryFailed -> logAndRetry(error.query)
    is DatabaseError.Timeout -> increaseTimeout(error.durationMs)
    DatabaseError.NotInitialized -> initialize()
}
// Добавление нового подтипа → ошибка компиляции в КАЖДОМ when
// Это coupling, но КОНТРОЛИРУЕМЫЙ: все зависимости видны компилятору
```

### Interface-based design

```kotlin
// Программируем на абстракцию, не на реализацию
interface UserRepository {
    suspend fun findById(id: Long): User?
    suspend fun save(user: User): Long
}

// Реализация скрыта за интерфейсом
class PostgresUserRepository(
    private val db: Database
) : UserRepository {
    override suspend fun findById(id: Long): User? = TODO()
    override suspend fun save(user: User): Long = TODO()
}

// Клиентский код зависит ТОЛЬКО от интерфейса
class UserService(private val repository: UserRepository) {
    suspend fun getUser(id: Long): User =
        repository.findById(id) ?: throw UserNotFoundException(id)
}
```

### Extension functions: поведение без связи

```kotlin
// Extension function добавляет поведение БЕЗ модификации класса
// Класс User НЕ знает об этой функции -- coupling отсутствует

fun User.toDisplayName(): String =
    if (middleName != null) "$firstName $middleName $lastName"
    else "$firstName $lastName"

fun User.toDto(): UserDto = UserDto(
    id = id,
    displayName = toDisplayName(),
    email = email
)

// Можно сгруппировать по модулю: UI-слой имеет свои extensions,
// API-слой -- свои. Каждый слой добавляет нужное поведение,
// не загрязняя сам класс User
```

### Coroutines/Flow: развязка producer и consumer

```kotlin
// Producer НЕ знает, кто потребляет данные
class SensorDataSource {
    fun readings(): Flow<SensorReading> = flow {
        while (true) {
            emit(readSensor())
            delay(1000)
        }
    }
}

// Consumer НЕ знает, откуда данные
class SensorDisplay(private val dataSource: SensorDataSource) {
    suspend fun observe() {
        dataSource.readings()
            .filter { it.value > threshold }
            .map { it.toDisplayModel() }
            .collect { display(it) }
    }
}
// Flow развязывает: producer emits, consumer collects
// Backpressure, cancellation, threading -- всё управляется pipeline
```

---

## Kotlin-инструменты для повышения Cohesion

### `data class`: когезивные value objects

```kotlin
// Все поля -- для одной цели: представить адрес
data class Address(
    val street: String,
    val city: String,
    val postalCode: String,
    val country: String
) {
    fun toSingleLine(): String = "$street, $city, $postalCode, $country"
    fun isInCountry(code: String): Boolean = country.equals(code, ignoreCase = true)
}
// equals, hashCode, toString, copy -- всё про Address. Высокая cohesion.
```

### `sealed class`: все варианты в одном месте

```kotlin
// Все состояния загрузки -- вместе
sealed class LoadingState<out T> {
    data object Idle : LoadingState<Nothing>()
    data object Loading : LoadingState<Nothing>()
    data class Success<T>(val data: T) : LoadingState<T>()
    data class Error(val message: String, val retry: (() -> Unit)? = null) : LoadingState<Nothing>()
}
// Нельзя "забыть" вариант: sealed + when = compile-time exhaustiveness
```

### `companion object`: фабричная когезия

```kotlin
data class Temperature private constructor(val kelvin: Double) {
    companion object {
        fun fromCelsius(celsius: Double) = Temperature(celsius + 273.15)
        fun fromFahrenheit(fahrenheit: Double) = Temperature((fahrenheit - 32) * 5 / 9 + 273.15)
        fun fromKelvin(kelvin: Double): Temperature {
            require(kelvin >= 0) { "Temperature cannot be below absolute zero" }
            return Temperature(kelvin)
        }
    }

    fun toCelsius(): Double = kelvin - 273.15
    fun toFahrenheit(): Double = (kelvin - 273.15) * 9 / 5 + 32
}
// Создание и конвертация Temperature -- всё в одном месте
```

### Пакеты + `internal`: модульная когезия

```kotlin
// module: feature-auth
// Публичный API:
class AuthManager internal constructor(
    private val tokenStorage: TokenStorage,
    private val loginUseCase: LoginUseCase
) {
    suspend fun login(credentials: Credentials): AuthResult =
        loginUseCase(credentials)

    fun isLoggedIn(): Boolean = tokenStorage.hasValidToken()

    fun logout() = tokenStorage.clear()
}

// Внутренние классы -- не видны извне модуля:
internal class TokenStorage { /* ... */ }
internal class LoginUseCase(private val api: AuthApi) { /* ... */ }
internal class AuthApi { /* ... */ }

// Точка входа:
object AuthModule {
    fun create(): AuthManager = AuthManager(TokenStorage(), LoginUseCase(AuthApi()))
}
```

---

## Метрики: количественная оценка

### Метрики Роберта Мартина (1994)

| Метрика | Формула | Что измеряет |
|---------|---------|-------------|
| **Ca** (Afferent Coupling) | Число классов извне, зависящих от модуля | Ответственность модуля |
| **Ce** (Efferent Coupling) | Число внешних классов, от которых зависит модуль | Зависимость модуля |
| **I** (Instability) | Ce / (Ca + Ce) | Устойчивость: 0 = стабильный, 1 = нестабильный |
| **A** (Abstractness) | Абстрактные классы / Все классы | Абстрактность: 0 = конкретный, 1 = абстрактный |
| **D** (Distance) | \|A + I - 1\| | Расстояние от "Main Sequence" |

### Main Sequence: идеальный баланс

```
    Abstractness (A)
    1.0 ┌──────────────────────┐
        │ Zone of             /│
        │ Uselessness        / │
        │ (слишком          /  │
        │  абстрактно)     /   │
        │                 /    │
    0.5 │      Main      /     │
        │    Sequence   /      │
        │              /       │
        │             /        │
        │            /  Zone of│
        │           /   Pain   │
        │          / (слишком  │
        │         /  конкретно │
    0.0 │────────/──и стабильно│
        └──────────────────────┘
        0.0                  1.0
              Instability (I)

    Идеал: A + I ≈ 1 (точки на диагонали)
```

**Zone of Pain** (нижний левый угол): модуль стабильный (много зависимых) И конкретный (мало абстракций). Менять больно -- много зависимых сломается. Пример: `java.lang.String`.

**Zone of Uselessness** (верхний правый угол): модуль нестабильный (мало зависимых) И абстрактный (одни интерфейсы). Абстракции, которые никто не использует.

**Main Sequence** (диагональ): стабильные модули -- абстрактны, нестабильные -- конкретны.

### Пример расчёта для Kotlin-модулей

```kotlin
// module: domain (бизнес-логика)
// Ca = 5 (от domain зависят: app, ui, data, api, test)
// Ce = 0 (domain НЕ зависит ни от кого)
// I  = 0 / (5 + 0) = 0.0 (полностью стабильный)
// A  = 4/5 = 0.8 (4 интерфейса, 1 data class)
// D  = |0.8 + 0.0 - 1| = 0.2 (близко к Main Sequence ✅)

// module: data (реализация хранения)
// Ca = 1 (от data зависит только app)
// Ce = 3 (data зависит от domain, Room, Retrofit)
// I  = 3 / (1 + 3) = 0.75 (нестабильный)
// A  = 0/4 = 0.0 (все классы конкретные)
// D  = |0.0 + 0.75 - 1| = 0.25 (близко к Main Sequence ✅)
```

---

## Практика: модульные границы в Kotlin-проектах

### Multi-module Clean Architecture

```
    ┌──────────────────────────────────────────────┐
    │                    :app                       │
    │  Зависит от всех модулей                     │
    │  I ≈ 1.0 (максимально нестабильный)          │
    └────────┬─────────────┬───────────────┬───────┘
             │             │               │
    ┌────────▼────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  :feature-  │ │  :feature-  │ │  :feature-  │
    │   auth      │ │   profile   │ │   orders    │
    │  I ≈ 0.7    │ │  I ≈ 0.7    │ │  I ≈ 0.7    │
    └────────┬────┘ └──────┬──────┘ └──────┬──────┘
             │             │               │
    ┌────────▼─────────────▼───────────────▼──────┐
    │                  :domain                     │
    │  Интерфейсы + бизнес-логика                  │
    │  I ≈ 0.0 (максимально стабильный)            │
    │  A ≈ 0.8 (в основном интерфейсы)             │
    └──────────────────────┬──────────────────────┘
                           │
    ┌──────────────────────▼──────────────────────┐
    │                  :data                       │
    │  Реализации интерфейсов domain               │
    │  I ≈ 0.75, A ≈ 0.0                          │
    └─────────────────────────────────────────────┘
```

### Dependency Injection снижает coupling

```kotlin
// ❌ Высокий coupling: прямое создание зависимостей
class OrderService {
    private val userRepo = PostgresUserRepository(Database.instance)  // 💥
    private val orderRepo = PostgresOrderRepository(Database.instance) // 💥
    private val emailService = SmtpEmailService("smtp.gmail.com")     // 💥
}

// ✅ Низкий coupling: зависимости через конструктор
class OrderService(
    private val userRepo: UserRepository,      // Интерфейс
    private val orderRepo: OrderRepository,    // Интерфейс
    private val emailService: EmailService     // Интерфейс
) {
    suspend fun createOrder(userId: Long, items: List<Item>): Order {
        val user = userRepo.findById(userId) ?: throw UserNotFoundException(userId)
        val order = Order(user = user, items = items)
        orderRepo.save(order)
        emailService.sendOrderConfirmation(user.email, order)
        return order
    }
}
// OrderService зависит от АБСТРАКЦИЙ, не от конкретных реализаций
// В тестах подставляем mock, в production -- реальные реализации
```

### Модульные границы в build.gradle.kts

```kotlin
// :domain/build.gradle.kts
plugins { kotlin("jvm") }
// НИКАКИХ зависимостей на фреймворки!
// domain зависит только от stdlib

// :data/build.gradle.kts
dependencies {
    implementation(project(":domain"))  // Зависит от domain
    implementation("org.jetbrains.exposed:exposed-core:...")
    // internal реализации -- не видны из :app
}

// :feature-auth/build.gradle.kts
dependencies {
    implementation(project(":domain"))
    // НЕ зависит от :data -- только от интерфейсов!
}

// :app/build.gradle.kts
dependencies {
    implementation(project(":domain"))
    implementation(project(":data"))
    implementation(project(":feature-auth"))
    // Собирает всё вместе, DI подставляет реализации
}
```

---

## Подводные камни

### 1. "Low coupling" не значит "zero coupling"

Нулевая связанность = модули не взаимодействуют = бесполезная система. Цель -- **минимальная необходимая связанность** через **стабильные абстракции**.

### 2. God Object: высокая cohesion -- иллюзия

```kotlin
// ❌ "Всё про пользователя" -- кажется когезивным, но это God Object
class UserManager {
    fun register(user: User) { /* ... */ }
    fun login(credentials: Credentials) { /* ... */ }
    fun updateProfile(user: User) { /* ... */ }
    fun changePassword(userId: Long, newPassword: String) { /* ... */ }
    fun sendVerificationEmail(email: String) { /* ... */ }
    fun uploadAvatar(userId: Long, image: ByteArray) { /* ... */ }
    fun calculateLoyaltyPoints(userId: Long): Int { /* ... */ }
    fun exportUserData(userId: Long): ByteArray { /* ... */ }
    fun deleteAccount(userId: Long) { /* ... */ }
}
// Регистрация, авторизация, профиль, аватары, лояльность, GDPR --
// это РАЗНЫЕ ответственности, объединённые только словом "User"
```

### 3. Слишком мелкие модули -- coupling взрывается

```kotlin
// ❌ Каждый класс в своём модуле:
// :model-user (1 класс), :model-order (1 класс),
// :repo-user (1 класс), :service-user (1 класс)...
// Результат: 50 модулей, каждый зависит от 10 других = coupling nightmare
// Gradle build time: 5 минут вместо 30 секунд

// ✅ Модули по feature/domain:
// :domain (интерфейсы + модели), :feature-auth, :feature-orders
// Каждый модуль самодостаточен -- внутри высокая cohesion
```

### 4. Coupling через данные (hidden coupling)

```kotlin
// ❌ Два модуля "независимы", но оба зависят от формата JSON
// Module A пишет: {"user_name": "Alice"}
// Module B читает: json.getString("user_name")
// Переименовали поле в A → сломался B. Coupling через данные!

// ✅ Общая модель в shared module
// :shared-models
data class UserDto(val userName: String) // Оба модуля зависят от типа, не от строки
```

---

## Проверь себя

> [!question]- 1. Модуль содержит: парсинг CSV, валидацию email, генерацию PDF-отчёта и отправку push-уведомлений. Какой тип cohesion? Как исправить?
> Coincidental cohesion -- элементы не связаны друг с другом, объединены случайно. Исправление: выделить 4 отдельных модуля/класса по ответственности: `CsvParser`, `EmailValidator`, `PdfReportGenerator`, `PushNotificationService`. Каждый будет иметь functional cohesion.

> [!question]- 2. Функция принимает `User` (10 полей), но использует только `user.email`. Какой тип coupling? Как улучшить?
> Stamp coupling -- передаём составную структуру, используя лишь часть. Улучшение: (1) принимать `email: String` напрямую; или (2) создать интерфейс `HasEmail` с одним свойством `val email: String`, и `User` реализует его. Второй вариант позволяет передавать любой объект с email.

> [!question]- 3. Модуль :domain имеет Ca=8, Ce=0. Модуль :data имеет Ca=1, Ce=5. Вычислите Instability для обоих. Какой модуль должен быть абстрактнее?
> :domain: I = 0/(8+0) = 0.0 (полностью стабильный). :data: I = 5/(1+5) = 0.83 (нестабильный). По Main Sequence: стабильный модуль должен быть абстрактным → :domain должен содержать преимущественно интерфейсы и абстрактные классы (A ≈ 1.0). :data нестабилен → может быть конкретным (A ≈ 0.0). Это соответствует Clean Architecture: domain = интерфейсы, data = реализации.

> [!question]- 4. Как `internal` в Kotlin помогает снизить coupling по сравнению с Java `package-private`?
> `package-private` в Java ограничивает видимость одним пакетом, но в multi-module проекте другой модуль может создать тот же пакет и получить доступ. `internal` в Kotlin ограничивает видимость **модулем компиляции** (Gradle module). Если класс `internal`, он недоступен из другого Gradle-модуля, даже если пакеты совпадают. Это позволяет скрывать реализацию за фасадом модуля и экспортировать только публичный API.

> [!question]- 5. В чём разница между sequential и functional cohesion? Приведите пример каждой.
> Sequential: выход одного шага = вход следующего (конвейер). Пример: `readFile() → parseData() → validate() → save()`. Каждый шаг работает с результатом предыдущего. Functional: все элементы работают над ОДНОЙ задачей. Пример: `OrderPriceCalculator` с методами `calculateSubtotal()`, `applyDiscount()`, `calculateTax()` -- все для одной цели (цена заказа). Functional cohesion выше, потому что элементы не просто "по порядку", а "для одной цели".

---

## Ключевые карточки

Что такое Coupling и Cohesion?
?
**Coupling** -- степень зависимости между модулями. Чем ниже, тем лучше: модули можно менять независимо. **Cohesion** -- степень связанности элементов внутри модуля. Чем выше, тем лучше: модуль делает одну вещь хорошо. Сформулированы Константином и Йорданом в 1979. Low coupling + high cohesion = идеальный дизайн.

Назовите 7 типов cohesion от худшего к лучшему.
?
(1) **Coincidental** -- элементы не связаны. (2) **Logical** -- похожи по типу (все "валидаторы"). (3) **Temporal** -- выполняются в одно время. (4) **Procedural** -- в определённом порядке. (5) **Communicational** -- работают с одними данными. (6) **Sequential** -- выход одного = вход другого. (7) **Functional** -- все для одной задачи.

Что такое Instability и Main Sequence?
?
**Instability** I = Ce/(Ca+Ce). Ca -- число внешних зависимых, Ce -- число внешних зависимостей. I=0: стабильный (много зависимых). I=1: нестабильный (много зависимостей). **Main Sequence**: линия A+I=1. Стабильные модули должны быть абстрактны (интерфейсы), нестабильные -- конкретны (реализации). Distance D=|A+I-1| показывает отклонение от идеала.

Как `internal` в Kotlin снижает coupling?
?
`internal` ограничивает видимость **Gradle-модулем** (не пакетом, как `package-private` в Java). Реализация скрыта за границей модуля. Публичный API минимален. Другие модули зависят только от публичных интерфейсов, не от реализации. В multi-module проекте это позволяет строить чёткие архитектурные границы.

Чем Content Coupling отличается от Data Coupling?
?
**Content coupling** (худший): один модуль лезет внутрь другого (рефлексия, глобальные переменные, прямой доступ к приватным полям). **Data coupling** (хороший): модули обмениваются только простыми данными через параметры функций. Content coupling = нарушение инкапсуляции. Data coupling = чистый контракт.

Как SOLID связан с coupling и cohesion?
?
SOLID -- следствие стремления к low coupling + high cohesion. **SRP** = high cohesion (один класс -- одна ответственность). **OCP/LSP** = controlled coupling (зависимость от абстракций). **ISP** = устранение stamp coupling (узкие интерфейсы). **DIP** = зависимость от абстракций, а не реализаций = low coupling. Coupling и cohesion -- более фундаментальны, чем SOLID.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Фундамент | [[solid-principles]] | SOLID как следствие low coupling / high cohesion |
| Фундамент | [[composition-vs-inheritance]] | Композиция снижает coupling -- конкретные приёмы |
| Фундамент | [[oop-fundamentals]] | Инкапсуляция как основа управления coupling |
| Практика | [[clean-code]] | Чистый код: имена, функции, модули |
| Архитектура | [[clean-architecture]] | Multi-module проект с чёткими границами coupling |
| Android | [[android-architecture-patterns]] | Метрики coupling/cohesion для оценки слоёв |
| Android | [[android-modularization]] | Coupling и cohesion в модульной архитектуре Android |
| Kotlin | [[kotlin-oop]] | `sealed class`, `data class`, `internal` на практике |

---

## Источники

### Теоретические основы
- **Stevens W., Myers G., Constantine L. (1974). Structured Design. IBM Systems Journal.** — первая публикация формальных определений coupling и cohesion
- **Constantine L., Yourdon E. (1979). Structured Design. Prentice Hall.** — книга-первоисточник: 7 типов coupling, 7 типов cohesion
- **Martin R. (2002). Agile Software Development. Prentice Hall.** — метрики Ca, Ce, Instability, Abstractness, Distance from Main Sequence

### Практические руководства
- Constantine L., Yourdon E. (1979). *Structured Design: Fundamentals of a Discipline of Computer Program and Systems Design*. -- Первоисточник: определение 7 типов cohesion и 7 типов coupling.
- Stevens W., Myers G., Constantine L. (1974). "Structured Design". *IBM Systems Journal*, 13(2). -- Статья-предшественник книги, первая публикация метрик.
- Martin R. (2002). *Agile Software Development: Principles, Patterns, and Practices*. -- Метрики Ca, Ce, Instability, Abstractness, Distance from Main Sequence.
- Martin R. (2017). *Clean Architecture*. -- Принципы компонентного дизайна, Dependency Rule, границы модулей.
- Bloch J. (2018). *Effective Java, 3rd Edition*. -- Item 15: "Minimize the accessibility of classes and members" (связь с coupling).
- Москала М. (2021). *Effective Kotlin*. -- Модульный дизайн в Kotlin, использование `internal`, sealed class для контролируемых иерархий.
- [Coupling -- Wikipedia](https://en.wikipedia.org/wiki/Coupling_(computer_programming)) -- Обзор типов coupling, исторические ссылки.
- [Cohesion -- Wikipedia](https://en.wikipedia.org/wiki/Cohesion_(computer_science)) -- Обзор типов cohesion, примеры, исследования.
- [Kotlin Documentation: Visibility Modifiers](https://kotlinlang.org/docs/visibility-modifiers.html) -- Официальная документация по `internal`, `private`, `protected`.
- [Kotlin Documentation: Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html) -- Официальная документация по sealed class/interface.

---

*Проверено: 2026-02-19 | Источники: Constantine/Yourdon, Robert Martin, Effective Kotlin, Kotlin Docs, Wikipedia*
