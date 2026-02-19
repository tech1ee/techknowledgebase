---
title: "Clean Code: практики чистого кода"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/clean-code
  - topic/kotlin
related:
  - "[[solid-principles]]"
  - "[[dry-kiss-yagni]]"
  - "[[code-smells]]"
  - "[[refactoring-catalog]]"
  - "[[kotlin-best-practices]]"
---

# Clean Code: практики чистого кода

Knight Capital Group потеряла $440 миллионов за 45 минут из-за мёртвого кода, который никто не удалил. Это не исключение --- в индустрии 80% времени тратится на **чтение** кода, а не на написание. Чистый код --- не эстетика, а экономическая необходимость. Но и догматичное следование правилам Clean Code порождает over-engineering. Эта заметка --- баланс между двумя крайностями, с примерами на идиоматичном Kotlin.

---

## Что такое "чистый код"

Роберт Мартин в книге "Clean Code" (2008) определил чистый код через мнения нескольких ведущих разработчиков:

> "Clean code reads like well-written prose." --- Grady Booch

> "Clean code can be read, and enhanced by a developer other than its original author." --- Dave Thomas

Но спустя 15+ лет книга получила и заслуженную критику: примеры кода устарели, советы подаются как догмы, а функциональный подход полностью игнорируется. Kotlin --- язык, который **на уровне синтаксиса** решает многие проблемы, описанные в книге: null-safety вместо defensive checks, `data class` вместо ручного boilerplate, expression body вместо многословных return.

> [!info] Kotlin-нюанс
> Многие "правила" Clean Code (defensive null-checks, boilerplate equals/hashCode, utility-классы) в Kotlin решаются средствами языка --- не нужно прикладывать усилия, чтобы код был чистым в этих аспектах.

---

## 1. Именование: имена говорят сами за себя

### Проблема

Мозг тратит когнитивные ресурсы на "перевод" однобуквенных имён. `d`, `t`, `x` --- что это? Каждая расшифровка --- микро-задержка. На масштабе проекта это десятки часов потерянного времени.

### Конвенции Kotlin

| Тип | Правило | Примеры |
|-----|---------|---------|
| Классы/интерфейсы | PascalCase | `UserRepository`, `PaymentGateway` |
| Функции/свойства | camelCase | `calculateTotal()`, `userName` |
| Константы | UPPER_SNAKE_CASE | `MAX_RETRIES`, `API_BASE_URL` |
| Boolean | `is`/`has`/`can`/`should` | `isActive`, `hasPermission`, `canEdit` |
| Пакеты | lowercase, без подчёркиваний | `com.example.myapp` |
| Backing properties | подчёркивание | `_users` (private), `users` (public) |
| Тесты | backtick-имена | `` `should return user when ID exists`() `` |

### Пример: до и после

```kotlin
// ---- Плохо: требует "перевод" в голове ----
val d = Date()
val t = d.time
val u = getU(id)
val f = u.a > 0

// ---- Хорошо: читается как текст ----
val currentDate = Date()
val timestampMs = currentDate.time
val user = getUserById(userId)
val hasPositiveBalance = user.accountBalance > 0
```

### Kotlin-специфика: named parameters

```kotlin
// Без named parameters --- что значит true, true, 30?
createNotification("Ошибка", "Сервер недоступен", true, true, 30)

// С named parameters --- самодокументирующийся вызов
createNotification(
    title = "Ошибка",
    message = "Сервер недоступен",
    isUrgent = true,
    showBadge = true,
    dismissAfterSeconds = 30
)
```

> [!info] Kotlin-нюанс
> Named parameters делают вызовы функций **самодокументирующимися**. В Java для этого нужен Builder pattern (десятки строк кода). В Kotlin это встроено в язык.

### Магические числа и строки

```kotlin
// ---- Плохо: что значит 86400000? ----
if (user.role == 1) { /* ... */ }
if (retries > 3) { /* ... */ }
delay(86400000)

// ---- Хорошо: самодокументирующийся код ----
enum class UserRole(val code: Int) {
    ADMIN(1), USER(2), GUEST(3)
}

const val MAX_RETRIES = 3
val ONE_DAY_MS = 24.hours.inWholeMilliseconds  // kotlin.time

if (user.role == UserRole.ADMIN) { /* ... */ }
if (retries > MAX_RETRIES) { /* ... */ }
delay(1.days)  // kotlinx.coroutines + kotlin.time
```

---

## 2. Функции: маленькие, с одной задачей

### Принцип одного уровня абстракции

Функция должна работать на **одном** уровне абстракции. Смешивание бизнес-логики с SQL-запросами или HTTP-вызовами --- признак нарушения.

```kotlin
// ---- Плохо: 5 ответственностей, смешанные уровни абстракции ----
suspend fun processOrder(order: Order) {
    // 1. Валидация
    if (order.items.isEmpty()) throw IllegalArgumentException("Empty order")
    if (order.userId.isBlank()) throw IllegalArgumentException("No user")

    // 2. Расчёт цены (бизнес-логика)
    var total = 0.0
    for (item in order.items) {
        total += item.price * item.quantity
        if (item.discount > 0) total -= item.discount
    }

    // 3. Проверка баланса (доступ к БД)
    val user = database.users.findById(order.userId)
        ?: throw UserNotFoundException(order.userId)
    if (user.balance < total) throw InsufficientFundsException()

    // 4. Списание (мутация + БД)
    user.balance -= total
    database.users.update(user)

    // 5. Уведомление (HTTP)
    emailService.send(user.email, "Заказ подтверждён", order)
}

// ---- Хорошо: одна функция = один уровень абстракции ----
suspend fun processOrder(order: Order) {
    validateOrder(order)
    val total = calculateTotal(order)
    val user = getVerifiedUser(order.userId, total)
    chargeUser(user, total)
    notifyOrderConfirmed(user, order)
}

private fun validateOrder(order: Order) {
    require(order.items.isNotEmpty()) { "Order must have items" }
    require(order.userId.isNotBlank()) { "Order must have userId" }
}

private fun calculateTotal(order: Order): Double =
    order.items.sumOf { it.price * it.quantity - it.discount }

private suspend fun getVerifiedUser(userId: String, requiredBalance: Double): User {
    val user = userRepository.findById(userId)
        ?: throw UserNotFoundException(userId)
    check(user.balance >= requiredBalance) { "Insufficient funds" }
    return user
}
```

### Kotlin: expression body для коротких функций

```kotlin
// ---- Statement body: многословно ----
fun isAdult(age: Int): Boolean {
    return age >= 18
}

fun getDiscount(user: User): Double {
    return if (user.isPremium) 0.2 else 0.0
}

// ---- Expression body: лаконично ----
fun isAdult(age: Int): Boolean = age >= 18

fun getDiscount(user: User): Double =
    if (user.isPremium) 0.2 else 0.0

fun formatName(first: String, last: String): String =
    "${first.trim()} ${last.trim()}"
```

### Kotlin: default values вместо перегрузок

```kotlin
// ---- Java-подход: 4 перегрузки ----
fun connect(host: String, port: Int, timeout: Int, retries: Int) { /* ... */ }
fun connect(host: String, port: Int, timeout: Int) = connect(host, port, timeout, 3)
fun connect(host: String, port: Int) = connect(host, port, 5000, 3)
fun connect(host: String) = connect(host, 8080, 5000, 3)

// ---- Kotlin: одна функция с default values ----
fun connect(
    host: String,
    port: Int = 8080,
    timeout: Int = 5_000,
    retries: Int = 3
) {
    // ...
}

// Вызовы --- только нужные параметры
connect("localhost")
connect("api.example.com", port = 443)
connect("db.internal", timeout = 30_000, retries = 5)
```

### Когда НЕ дробить

Функция на 20 строк, делающая **одно** логическое действие --- нормально. Три функции по 5 строк хуже одной на 15, если они используются только вместе и не переиспользуются.

```
Правило:
• Если функцию сложно назвать --- она делает слишком много
• Если функция нужна только в одном месте и тривиальна --- не выделяй
• Идеальный размер: помещается на экране без прокрутки
```

---

## 3. Комментарии: когда код не может объяснить "почему"

### Плохие комментарии: пересказ кода

```kotlin
// ---- Плохо: комментарий дублирует код ----

// Проверяем, активен ли пользователь
if (user.isActive) { /* ... */ }

// Увеличиваем счётчик на 1
counter++

// Получаем список пользователей
val users = userRepository.findAll()
```

Если комментарий объясняет **что** делает код --- код непонятен, и нужно **переписать код**, а не добавлять комментарий.

### Хорошие комментарии: объяснение "почему"

```kotlin
// Binary search: массив гарантированно отсортирован загрузчиком,
// линейный поиск на 10M элементах занимает >500ms
val index = items.binarySearch(target)

// Используем delay вместо sleep: внутри корутины sleep заблокирует весь поток
delay(retryInterval)

// Формула из RFC 6298, Section 2: https://tools.ietf.org/html/rfc6298
val rto = srtt + max(G, K * rttvar)

// HACK: Android 12 API bug — MediaCodec.configure() крашится без этого workaround
// Трекер: https://issuetracker.google.com/issues/123456
if (Build.VERSION.SDK_INT == 31) { /* ... */ }
```

### KDoc: документация в Kotlin

KDoc --- аналог Javadoc для Kotlin. Использует Markdown-синтаксис.

```kotlin
/**
 * Вычисляет стоимость доставки на основе расстояния и веса.
 *
 * Использует тарифную сетку из [DeliveryConfig.rates].
 * Для расстояний > 500 км применяется множитель [LONG_DISTANCE_MULTIPLIER].
 *
 * @param distance расстояние в километрах (должно быть > 0)
 * @param weight вес посылки в килограммах
 * @return стоимость доставки в рублях
 * @throws IllegalArgumentException если [distance] <= 0
 * @see DeliveryConfig.rates
 * @sample com.example.delivery.samples.calculateShippingCostSample
 */
fun calculateShippingCost(distance: Double, weight: Double): Double {
    require(distance > 0) { "Distance must be positive, got $distance" }
    // ...
}
```

**Основные теги KDoc:**

| Тег | Назначение |
|-----|-----------|
| `@param name` | Параметр функции или type parameter |
| `@return` | Возвращаемое значение |
| `@throws` / `@exception` | Исключения |
| `@see` | Ссылка на связанный элемент |
| `@sample` | Ссылка на пример использования |
| `@receiver` | Документация receiver'а extension function |
| `@property name` | Свойство класса (в документации класса) |
| `@constructor` | Первичный конструктор класса |

### TODO и FIXME: конвенции

```kotlin
// TODO(arman): заменить на Result<T> после миграции на API v2 (PROJ-456)
// FIXME: race condition при параллельных запросах — нужен mutex
// HACK: обход бага в библиотеке X, убрать после обновления до 2.0
// NOTE: порядок вызовов критичен — init() до start()
```

> [!info] Kotlin-нюанс
> IntelliJ/Android Studio подсвечивает `TODO` и `FIXME` в специальном окне, поэтому они не теряются. Но `TODO` без номера тикета --- это путь к забвению.

---

## 4. Форматирование: единый стиль команды

### Kotlin Official Style Guide

Официальный стиль от JetBrains и Google описывает всё: отступы (4 пробела), максимальную длину строки (обычно 120 символов), правила переноса параметров, порядок модификаторов.

```
Порядок модификаторов в Kotlin (по style guide):
public / protected / private / internal
expect / actual
final / open / abstract / sealed / const
external
override
lateinit
tailrec
vararg
suspend
inner
enum / annotation / fun (как модификатор)
companion
inline / value
infix
operator
data
```

### Инструменты автоматического форматирования

```
┌──────────┬─────────────────────────────────────────────────────────┐
│ ktlint   │ Линтер + форматтер. Проверяет стиль кодирования.      │
│          │ Автоформатирование: ktlint -F                          │
├──────────┼─────────────────────────────────────────────────────────┤
│ ktfmt    │ Альтернатива от Google/Square. На 40% быстрее ktlint.  │
│          │ Полностью детерминированный форматтер.                  │
├──────────┼─────────────────────────────────────────────────────────┤
│ detekt   │ Статический анализатор. Сложность, naming,             │
│          │ code smells, maintainability. Интеграция с ktlint.     │
└──────────┴─────────────────────────────────────────────────────────┘
```

**Рекомендация:** используйте **detekt + ktlint** (или **detekt + ktfmt**) в CI --- форматирование и анализ в одном прогоне.

```kotlin
// build.gradle.kts
plugins {
    id("io.gitlab.arturbosch.detekt") version "1.23.7"
}

detekt {
    config.setFrom("$rootDir/config/detekt.yml")
    buildUponDefaultConfig = true
}
```

---

## 5. Обработка ошибок: Kotlin-way

### Null-safety вместо defensive checks

В Java огромная часть "чистого кода" --- это defensive null-checks. Kotlin решает это на уровне системы типов.

```kotlin
// ---- Java-стиль: defensive checks ----
fun processUser(user: User?) {
    if (user == null) return
    if (user.name == null) return
    if (user.email == null) return
    // Наконец-то работаем...
    sendEmail(user.email, "Hello, ${user.name}")
}

// ---- Kotlin-стиль: null-safety в типах ----
fun processUser(user: User) {  // non-null по контракту
    sendEmail(user.email, "Hello, ${user.name}")
}

// Если nullable действительно нужен:
fun processUser(user: User?) {
    val name = user?.name ?: return        // early return
    val email = user.email ?: return
    sendEmail(email, "Hello, $name")
}
```

### require / check / error: предусловия

Kotlin предоставляет три стандартные функции для fail-fast:

```kotlin
fun transferMoney(from: Account, to: Account, amount: Double) {
    // require --- для входных параметров (IllegalArgumentException)
    require(amount > 0) { "Amount must be positive, got $amount" }
    require(from.id != to.id) { "Cannot transfer to the same account" }

    // check --- для состояния объекта (IllegalStateException)
    check(from.isActive) { "Source account ${from.id} is not active" }
    check(!from.isFrozen) { "Source account ${from.id} is frozen" }

    // error --- для "невозможных" ситуаций (IllegalStateException)
    val rate = exchangeRates[from.currency to to.currency]
        ?: error("No exchange rate for ${from.currency} -> ${to.currency}")

    // Основная логика --- без проверок, все инварианты гарантированы
    from.withdraw(amount)
    to.deposit(amount * rate)
}
```

### Result<T>: функциональная обработка ошибок

```kotlin
// ---- Плохо: catch-all молча проглатывает ошибки ----
fun fetchUser(id: String): User? {
    return try {
        api.getUser(id)
    } catch (e: Exception) {
        null  // Сеть? 404? 500? Баг? --- непонятно
    }
}

// ---- Хорошо: Result<T> сохраняет информацию об ошибке ----
fun fetchUser(id: String): Result<User> = runCatching {
    api.getUser(id)
}

// Использование:
fetchUser("123")
    .onSuccess { user -> showProfile(user) }
    .onFailure { error -> showError(error.message) }

// Трансформация:
val userName: String = fetchUser("123")
    .map { it.name }
    .getOrDefault("Unknown")

// Цепочка:
fun fetchUserProfile(id: String): Result<Profile> =
    fetchUser(id)
        .mapCatching { user -> profileService.getProfile(user.profileId) }
```

### sealed class для доменных ошибок

```kotlin
sealed class OrderError {
    data class ValidationError(val field: String, val reason: String) : OrderError()
    data class InsufficientFunds(val required: Double, val available: Double) : OrderError()
    data class ProductUnavailable(val productId: String) : OrderError()
    data object ServiceUnavailable : OrderError()
}

// Использование с when --- компилятор проверит exhaustiveness
fun handleError(error: OrderError): String = when (error) {
    is OrderError.ValidationError ->
        "Ошибка валидации: ${error.field} --- ${error.reason}"
    is OrderError.InsufficientFunds ->
        "Недостаточно средств: нужно ${error.required}, доступно ${error.available}"
    is OrderError.ProductUnavailable ->
        "Товар ${error.productId} недоступен"
    OrderError.ServiceUnavailable ->
        "Сервис временно недоступен"
    // Нет else --- если добавим новый тип, компилятор заставит обработать
}
```

---

## 6. Scope functions: мощный инструмент с подводными камнями

### Когда какую использовать

```
┌───────────┬──────────────┬──────────────┬─────────────────────────┐
│ Функция   │ Контекст     │ Возвращает   │ Когда использовать      │
├───────────┼──────────────┼──────────────┼─────────────────────────┤
│ let       │ it           │ результат λ  │ null-safety, трансформ. │
│ run       │ this         │ результат λ  │ вычисления с контекстом │
│ apply     │ this         │ сам объект   │ конфигурация объекта    │
│ also      │ it           │ сам объект   │ побочные эффекты (лог)  │
│ with      │ this         │ результат λ  │ группировка операций    │
└───────────┴──────────────┴──────────────┴─────────────────────────┘
```

### Примеры правильного использования

```kotlin
// let: null-safety + трансформация
val displayName = user?.name?.let { name ->
    "${name.first()} ${name.last()}"
} ?: "Гость"

// apply: конфигурация объекта (Builder без Builder)
val request = HttpRequest().apply {
    url = "https://api.example.com/users"
    method = "GET"
    headers["Authorization"] = "Bearer $token"
    timeout = 30_000
}

// also: побочный эффект без изменения цепочки
fun createUser(dto: CreateUserDto): User =
    User.fromDto(dto)
        .also { logger.info("Created user: ${it.id}") }
        .also { analytics.track("user_created", it.id) }

// run: вычисление с контекстом
val result = connection.run {
    open()
    val data = fetchData()
    close()
    data
}

// with: группировка операций на одном объекте
with(canvas) {
    drawColor(Color.WHITE)
    drawCircle(centerX, centerY, radius, paint)
    drawText("Hello", textX, textY, textPaint)
}
```

### Антипаттерн: вложенные scope functions

```kotlin
// ---- Плохо: три уровня вложенности, непонятно что this/it ----
user?.let { u ->
    u.profile?.run {
        address?.let { addr ->
            addr.city.also { city ->
                logger.info("City: $city")  // Какой контекст? Что есть this?
            }
        }
    }
}

// ---- Хорошо: safe call chain ----
val city = user?.profile?.address?.city
city?.let { logger.info("City: $it") }
```

> [!warning] Правило Netflix
> Максимум **одна** scope function на выражение. Вложенные `let { run { also {} } }` --- code smell. Netflix применяет это правило в code review: результат --- ревью проходят в 2 раза быстрее.

---

## 7. when expression: замена if-else цепочкам

```kotlin
// ---- Плохо: длинная if-else цепочка ----
fun getStatusMessage(code: Int): String {
    if (code == 200) return "OK"
    else if (code == 201) return "Created"
    else if (code == 400) return "Bad Request"
    else if (code == 401) return "Unauthorized"
    else if (code == 403) return "Forbidden"
    else if (code == 404) return "Not Found"
    else if (code == 500) return "Internal Server Error"
    else return "Unknown: $code"
}

// ---- Хорошо: when expression ----
fun getStatusMessage(code: Int): String = when (code) {
    200 -> "OK"
    201 -> "Created"
    400 -> "Bad Request"
    401 -> "Unauthorized"
    403 -> "Forbidden"
    404 -> "Not Found"
    500 -> "Internal Server Error"
    else -> "Unknown: $code"
}

// when с диапазонами и условиями:
fun classifyAge(age: Int): String = when {
    age < 0 -> error("Age cannot be negative")
    age < 13 -> "ребёнок"
    age < 18 -> "подросток"
    age < 65 -> "взрослый"
    else -> "пенсионер"
}

// when + sealed class: exhaustive без else
sealed interface Shape {
    data class Circle(val radius: Double) : Shape
    data class Rectangle(val width: Double, val height: Double) : Shape
    data class Triangle(val base: Double, val height: Double) : Shape
}

fun area(shape: Shape): Double = when (shape) {
    is Shape.Circle -> Math.PI * shape.radius * shape.radius
    is Shape.Rectangle -> shape.width * shape.height
    is Shape.Triangle -> 0.5 * shape.base * shape.height
    // Без else: добавление нового Shape --- ошибка компиляции
}
```

---

## 8. Extension functions для чистого API

```kotlin
// ---- Без extension functions: utility-класс (Java-стиль) ----
object StringUtils {
    fun isValidEmail(str: String): Boolean =
        str.matches(Regex("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"))

    fun capitalize(str: String): String =
        str.replaceFirstChar { it.uppercase() }
}

// Вызов:
if (StringUtils.isValidEmail(email)) { /* ... */ }

// ---- С extension functions: естественный API ----
fun String.isValidEmail(): Boolean =
    matches(Regex("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"))

fun String.capitalizeFirst(): String =
    replaceFirstChar { it.uppercase() }

// Вызов --- читается как свойство самого String:
if (email.isValidEmail()) { /* ... */ }
val title = name.capitalizeFirst()

// Extension для доменных типов:
fun List<Order>.totalRevenue(): Double =
    filter { it.status == OrderStatus.COMPLETED }
        .sumOf { it.total }

fun User.hasAccess(resource: Resource): Boolean =
    roles.any { it.permissions.contains(resource.requiredPermission) }

// Использование:
val revenue = orders.totalRevenue()
if (currentUser.hasAccess(document)) { /* ... */ }
```

> [!info] Kotlin-нюанс
> Extension functions компилируются в static-методы --- нет overhead в рантайме. Но помните: они **не имеют доступа к private members** и **не поддерживают полиморфизм** (резолвятся статически, на этапе компиляции).

---

## Подводные камни

### 1. Чрезмерное использование scope functions

```kotlin
// "Умный" одно-строчник, который никто не поймёт через неделю:
val result = data?.let { it.parse() }?.run { validate() }?.also { log(it) }?.apply { transform() }

// Разверни в несколько строк --- читаемость важнее краткости:
val parsed = data?.parse() ?: return
val validated = parsed.validate()
logger.info("Validated: $validated")
validated.transform()
```

### 2. Слишком "умные" однострочники

```kotlin
// "Элегантно", но нечитаемо:
fun process(items: List<Item>) = items.asSequence()
    .filter { it.isActive }
    .groupBy { it.category }
    .mapValues { (_, v) -> v.sortedByDescending { it.priority }.take(3) }
    .flatMap { (k, v) -> v.map { k to it } }
    .toMap()

// Понятнее с промежуточными переменными:
fun process(items: List<Item>): Map<Category, Item> {
    val activeItems = items.filter { it.isActive }
    val groupedByCategory = activeItems.groupBy { it.category }
    val topThreePerCategory = groupedByCategory.mapValues { (_, categoryItems) ->
        categoryItems.sortedByDescending { it.priority }.take(3)
    }
    return topThreePerCategory.flatMap { (category, topItems) ->
        topItems.map { category to it }
    }.toMap()
}
```

### 3. Преждевременная абстракция

```kotlin
// YAGNI: не создавай интерфейс ради единственной реализации
// ---- Over-engineering ----
interface UserMapper {
    fun toDto(user: User): UserDto
}

class UserMapperImpl : UserMapper {
    override fun toDto(user: User) = UserDto(user.name, user.email)
}

// ---- Проще и достаточно ----
fun User.toDto() = UserDto(name, email)
```

### 4. Злоупотребление expression body

```kotlin
// Expression body для длинных выражений --- ухудшает читаемость:
fun processTransaction(tx: Transaction): Result<Receipt> = runCatching {
    validateTransaction(tx).let { validTx ->
        chargeAccount(validTx.account, validTx.amount).let { charge ->
            Receipt(validTx.id, charge.confirmation, Instant.now())
        }
    }
}

// Обычный блок --- понятнее:
fun processTransaction(tx: Transaction): Result<Receipt> = runCatching {
    val validTx = validateTransaction(tx)
    val charge = chargeAccount(validTx.account, validTx.amount)
    Receipt(validTx.id, charge.confirmation, Instant.now())
}
```

### 5. Cargo-cult из книги Clean Code

Слепое следование правилам без понимания контекста:

```
Догма                        │ Реальность
─────────────────────────────┼─────────────────────────────────────
"Функция <= 5 строк"        │ 10-строчная может быть чище трёх по 5
"Никогда else"               │ else иногда читается лучше early return
"Каждый класс в своём файле" │ Связанные sealed class/enum в одном файле --- OK
"Нет комментариев"           │ Комментарий "почему" --- необходимость
"Без аббревиатур"            │ id, url, dto --- общепринятые сокращения
```

---

## Code Review чеклист

```
□ Имена понятны без контекста?
□ Функции работают на одном уровне абстракции?
□ Нет магических чисел и строк?
□ Ошибки обрабатываются явно (не catch-all → null)?
□ Нет !! (not-null assertion) без обоснования?
□ Scope functions используются уместно (макс. 1 на выражение)?
□ Named parameters для функций с > 2 параметрами одного типа?
□ val вместо var где возможно?
□ Read-only коллекции в публичном API?
□ KDoc для публичных функций?
```

---

## Приоритеты рефакторинга

```
1. Имена         — дёшево, высокий impact      → делай сразу
2. Extract method — средний effort               → при первом code review
3. Ошибки        — require/check/Result          → при обнаружении бага
4. Форматирование — настрой ktlint/detekt в CI   → один раз для проекта
5. Архитектура   — SOLID, паттерны               → при планировании спринта
```

---

## Проверь себя

> [!question]- Почему комментарий "что делает код" --- обычно code smell, а "почему так сделано" --- нужный комментарий?
> Комментарий "что" сигнализирует, что код непонятен сам по себе --- его нужно переписать с понятными именами. Код отвечает на "как", имена --- на "что", и только комментарии могут ответить на "почему именно так": бизнес-решение, ссылка на баг, ограничение внешней системы.

> [!question]- Назовите три Kotlin-фичи, которые делают код чистым "бесплатно" (без усилий разработчика).
> 1) **Null-safety в системе типов** --- компилятор не даст обратиться к nullable без проверки, defensive null-checks не нужны. 2) **Data classes** --- автоматические equals/hashCode/toString/copy, нет boilerplate. 3) **Named parameters + default values** --- самодокументирующиеся вызовы и одна функция вместо цепочки перегрузок.

> [!question]- Когда `!!` (not-null assertion) допустим в продакшен-коде?
> Практически никогда. Используйте `requireNotNull(value) { "message" }` для входных данных, `checkNotNull(value) { "message" }` для состояния, `?: return` для раннего выхода, `?: throw CustomException()` для доменных ошибок. `!!` оправдан только когда контракт **гарантирует** non-null, но компилятор не может это вывести (например, сразу после `lateinit` инициализации в тестах).

> [!question]- Что выбрать для обработки ошибок: исключения, `Result<T>` или `sealed class`?
> **Исключения** --- для "невозможных" ситуаций (programming errors), которые не нужно ловить вызывающим кодом. **`Result<T>`** --- для операций, которые ожидаемо могут провалиться (сеть, I/O). **`sealed class`** --- для доменных ошибок, где важны конкретные типы сбоев и компилятор должен проверить exhaustive handling. Правило: чем ближе к бизнес-логике, тем более typed должна быть ошибка.

> [!question]- Какие scope functions в Kotlin вы бы использовали и для чего: `let`, `apply`, `also`, `run`, `with`?
> **`let`** --- null-safety: `nullable?.let { use(it) }`. **`apply`** --- конфигурация объекта: `User().apply { name = "Alice" }`. **`also`** --- побочные эффекты в цепочке: `.also { log(it) }`. **`run`** --- вычисление с контекстом: `connection.run { fetchData() }`. **`with`** --- группировка операций: `with(canvas) { drawCircle(); drawText() }`. Главное правило: не вкладывать друг в друга.

---

## Ключевые карточки

Что такое "чистый код" и почему он важен экономически?
?
Код, который легко читать и изменять. 80% времени тратится на чтение кода, а не написание. Плохой код замедляет команду в 2--10 раз. Knight Capital потеряла $440M за 45 минут из-за мёртвого кода --- это экономическая цена "грязного" кода.

Какие три вида функций проверки предусловий предоставляет Kotlin?
?
`require(condition) { message }` --- для входных параметров (бросает `IllegalArgumentException`). `check(condition) { message }` --- для состояния объекта (бросает `IllegalStateException`). `error(message)` --- для "невозможных" ситуаций (бросает `IllegalStateException`). Все три поддерживают lazy message через лямбду.

Какие инструменты форматирования и анализа используются для Kotlin?
?
**ktlint** --- линтер + форматтер, проверяет соответствие Kotlin style guide. **ktfmt** --- альтернатива от Google, на 40% быстрее ktlint. **detekt** --- статический анализатор: сложность, naming, code smells. Рекомендация: detekt + ktlint (или ktfmt) в CI.

Как scope functions отличаются по контексту и возвращаемому значению?
?
`let` (it, результат лямбды), `run` (this, результат лямбды), `apply` (this, сам объект), `also` (it, сам объект), `with` (this, результат лямбды). Правило: `it` --- когда нужно явное имя, `this` --- когда настраиваешь объект. Не вкладывать друг в друга.

Чем named parameters в Kotlin лучше Builder pattern?
?
Named parameters встроены в язык --- не нужно писать Builder-класс. Вызов самодокументируется: `createUser(name = "Alice", age = 25, isAdmin = false)`. Поддерживают default values, что устраняет необходимость перегрузок. Компилятор проверяет типы --- в Builder можно забыть обязательное поле.

Когда `Result<T>` предпочтительнее исключений?
?
Для операций, которые **ожидаемо** могут провалиться: сетевые запросы, I/O, парсинг. `Result<T>` делает ошибку частью сигнатуры --- вызывающий код **обязан** обработать оба случая. Исключения лучше для programming errors (баги), которые не должны ловиться в обычном потоке.

Какой порядок приоритетов при рефакторинге?
?
1) Имена --- дёшево, высокий impact. 2) Extract method --- средний effort. 3) Обработка ошибок --- require/check/Result. 4) Форматирование --- настроить ktlint/detekt один раз. 5) Архитектура --- SOLID, паттерны при планировании.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Принципы | [[solid-principles]] | 5 принципов ООП-дизайна --- следующий уровень после Clean Code |
| Мета-принципы | [[dry-kiss-yagni]] | DRY, KISS, YAGNI --- когда Clean Code конфликтует с простотой |
| Запахи кода | [[code-smells]] | Как распознать "грязный" код: каталог запахов |
| Рефакторинг | [[refactoring-catalog]] | Практические техники исправления проблем |
| Kotlin | [[kotlin-best-practices]] | Полный гайд по идиоматичному Kotlin |
| Android | [[android-architecture-patterns]] | Clean Code принципы в архитектуре Android |

---

## Источники

### Книги
- Martin R. C. (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. --- Каноническая книга о чистом коде, несмотря на критику примеров
- Moskala M. (2024). *Effective Kotlin*. --- 60+ правил идиоматичного Kotlin, аналог Effective Java
- Bloch J. (2018). *Effective Java, 3rd Edition*. --- Многие принципы применимы к Kotlin через JVM

### Критика Clean Code
- [It's probably time to stop recommending Clean Code](https://qntm.org/clean) --- обзор устаревших аспектов книги
- [Clean Code: First Edition Critique](https://bugzmanov.github.io/cleancode-critique/) --- построчный разбор примеров из книги
- [The Good, the Bad and the Ugly](https://gerlacdt.github.io/blog/posts/clean_code/) --- сбалансированный обзор

### Kotlin-ресурсы
- [Kotlin Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html) --- официальный style guide от JetBrains
- [Kotlin Idioms](https://kotlinlang.org/docs/idioms.html) --- официальная страница идиом
- [Document Kotlin code: KDoc](https://kotlinlang.org/docs/kotlin-doc.html) --- синтаксис документации
- [Clean Code with Kotlin](https://phauer.com/2017/clean-code-kotlin/) --- как Kotlin решает проблемы Clean Code
- [Effective Kotlin: Design for readability](https://kt.academy/article/ek-readability) --- Marcin Moskala о читаемости

### Инструменты
- [detekt](https://github.com/detekt/detekt) --- статический анализатор для Kotlin
- [ktlint](https://pinterest.github.io/ktlint/) --- линтер и форматтер
- [Detekt vs Ktlint 2024](https://medium.com/@SaezChristopher/detekt-vs-ktlint-2024-which-linter-is-the-best-for-an-android-project-d1b7585a0103) --- сравнение инструментов

### Реальные кейсы
- [Knight Capital Disaster](https://www.henricodolfing.com/2019/06/project-failure-case-study-knight-capital.html) --- $440M потеря из-за мёртвого кода

---

*Проверено: 2026-02-19 | Источники верифицированы*
