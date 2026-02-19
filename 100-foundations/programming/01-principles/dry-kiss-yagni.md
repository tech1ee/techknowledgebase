---
title: "DRY, KISS, YAGNI: мета-принципы проектирования"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/principles
  - topic/kotlin
related:
  - "[[clean-code]]"
  - "[[solid-principles]]"
  - "[[code-smells]]"
  - "[[composition-vs-inheritance]]"
  - "[[oop-fundamentals]]"
---

# DRY, KISS, YAGNI: мета-принципы проектирования

"Duplication is far cheaper than the wrong abstraction" --- Sandi Metz. Эта фраза противоречит DRY. "Make it work, make it right, make it fast" --- Kent Beck. А ведь "make it right" --- это и KISS, и DRY одновременно. Три мета-принципа звучат просто, но **конфликтуют** друг с другом. Понимание их границ --- то, что отличает инженера от человека, который цитирует акронимы.

---

## DRY: Don't Repeat Yourself

### Происхождение и точное определение

Принцип сформулирован Эндрю Хантом и Дэвидом Томасом в книге "The Pragmatic Programmer" (1999):

> "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."

**Ключевое слово --- "knowledge" (знание), а не "код".** DRY --- это не "нет дублированного кода". Это **единый источник истины** для каждого факта в системе.

### Что DRY на самом деле означает

```
DRY --- это НЕ:                     DRY --- это:
──────────────────────────────────── ──────────────────────────────────────
"Никогда не дублируй код"           "Одно знание --- одно место"
Механическое удаление дубликатов    Единый источник истины
Одинаковый код = нарушение DRY      Одинаковый КОД --- случайное совпадение
                                    Одинаковое ЗНАНИЕ --- нарушение DRY
```

**Пример "случайного совпадения":**

```kotlin
// Два одинаковых метода --- НЕ нарушение DRY!
// Они описывают РАЗНЫЕ бизнес-правила.

fun calculateShippingTax(amount: Double): Double = amount * 0.1

fun calculateServiceFee(amount: Double): Double = amount * 0.1

// Сегодня обе = 10%. Завтра шиппинг станет 12%, а сервис --- 8%.
// Если объединить их в одну функцию "calculate10Percent()" ---
// придётся разделять обратно, добавляя параметры и условия.
```

### Правило трёх (Rule of Three)

Принцип от Martin Fowler: дублируй спокойно до **третьего раза**. После третьего повторения --- извлекай абстракцию.

```kotlin
// Первый раз --- напиши
fun sendWelcomeEmail(user: User) {
    val subject = "Добро пожаловать, ${user.name}!"
    val body = loadTemplate("welcome", mapOf("name" to user.name))
    emailService.send(user.email, subject, body)
}

// Второй раз --- ОК, можно дублировать
fun sendOrderConfirmation(user: User, order: Order) {
    val subject = "Заказ #${order.id} подтверждён"
    val body = loadTemplate("order_confirm", mapOf("order" to order))
    emailService.send(user.email, subject, body)
}

// Третий раз --- пора извлечь абстракцию
fun sendPasswordReset(user: User, token: String) {
    val subject = "Сброс пароля"
    val body = loadTemplate("password_reset", mapOf("token" to token))
    emailService.send(user.email, subject, body)
}

// Видим паттерн --- извлекаем:
data class EmailMessage(
    val to: String,
    val subject: String,
    val template: String,
    val params: Map<String, Any>
)

fun sendEmail(message: EmailMessage) {
    val body = loadTemplate(message.template, message.params)
    emailService.send(message.to, message.subject, body)
}

// Теперь каждый вызов:
sendEmail(EmailMessage(
    to = user.email,
    subject = "Добро пожаловать, ${user.name}!",
    template = "welcome",
    params = mapOf("name" to user.name)
))
```

### Когда дублирование ЛУЧШЕ неправильной абстракции

Sandi Metz описала типичный путь к "неправильной абстракции":

```
1. Программист видит дублирование
      ↓
2. Извлекает абстракцию, даёт имя
      ↓
3. Приходит новое требование --- почти подходит
      ↓
4. Добавляется параметр и условие
      ↓
5. Повторить п.3-4 пять раз
      ↓
6. Функция стала: 8 параметров, 12 условий, никто не понимает

┌──────────────────────────────────────────────────┐
│ "Duplication is far cheaper than                 │
│  the wrong abstraction."  --- Sandi Metz          │
└──────────────────────────────────────────────────┘
```

```kotlin
// Неправильная абстракция: "универсальный" валидатор
fun validate(
    value: String,
    type: ValidationType,
    minLength: Int? = null,
    maxLength: Int? = null,
    pattern: Regex? = null,
    allowEmpty: Boolean = false,
    trimBefore: Boolean = true,
    customValidator: ((String) -> Boolean)? = null,
    errorPrefix: String = ""
): ValidationResult {
    // 50 строк условной логики...
    // Никто не помнит, какие комбинации параметров валидны
}

// Лучше: отдельные, простые валидаторы
fun validateEmail(email: String): ValidationResult {
    val trimmed = email.trim()
    if (trimmed.isBlank()) return ValidationResult.Error("Email обязателен")
    if (!trimmed.matches(EMAIL_REGEX)) return ValidationResult.Error("Невалидный email")
    return ValidationResult.Success(trimmed)
}

fun validatePassword(password: String): ValidationResult {
    if (password.length < 8) return ValidationResult.Error("Минимум 8 символов")
    if (!password.any { it.isUpperCase() }) return ValidationResult.Error("Нужна заглавная буква")
    return ValidationResult.Success(password)
}
```

### DRY в Kotlin: средства языка

```kotlin
// --- Extension functions убирают utility-классы ---
// Java-стиль: StringUtils.isBlankOrEmpty(str)
// Kotlin DRY: расширение самого типа
fun String?.isBlankOrEmpty(): Boolean = this.isNullOrBlank()

// --- Higher-order functions убирают повторяющийся boilerplate ---
// Вместо дублирования try-catch + logging в каждом методе:
inline fun <T> withErrorHandling(
    operationName: String,
    block: () -> T
): Result<T> = runCatching {
    block()
}.onFailure { error ->
    logger.error("$operationName failed: ${error.message}", error)
}

// Использование:
fun fetchUser(id: String) = withErrorHandling("fetchUser($id)") {
    api.getUser(id)
}

fun saveOrder(order: Order) = withErrorHandling("saveOrder(${order.id})") {
    repository.save(order)
}

// --- Generics для типобезопасного DRY ---
interface Repository<T, ID> {
    fun findById(id: ID): T?
    fun save(entity: T): T
    fun delete(id: ID)
}

class UserRepository : Repository<User, String> {
    override fun findById(id: String): User? = db.users.find { it.id == id }
    override fun save(entity: User): User = db.users.upsert(entity)
    override fun delete(id: String) { db.users.removeById(id) }
}

// --- Делегаты для повторяющихся свойств ---
class ObservableProperty<T>(
    initialValue: T,
    private val onChange: (old: T, new: T) -> Unit
) : ReadWriteProperty<Any?, T> {
    private var value = initialValue

    override fun getValue(thisRef: Any?, property: KProperty<*>): T = value
    override fun setValue(thisRef: Any?, property: KProperty<*>, value: T) {
        val old = this.value
        this.value = value
        onChange(old, value)
    }
}

// Использование --- DRY для всех observable свойств:
class Settings {
    var theme by ObservableProperty("light") { old, new ->
        logger.info("Theme changed: $old -> $new")
    }
    var fontSize by ObservableProperty(14) { old, new ->
        logger.info("Font size changed: $old -> $new")
    }
}
```

---

## KISS: Keep It Simple, Stupid

### Происхождение

Принцип приписывают Кларенсу "Келли" Джонсону, ведущему инженеру Lockheed Skunk Works (1960-е). Команда Джонсона создавала шпионский самолёт U-2 и истребитель SR-71 Blackbird.

Требование Джонсона к конструкторам: самолёт должен быть ремонтопригоден средним механиком в полевых условиях с ограниченным набором инструментов. **Сложность = точка отказа.**

> "Keep it simple, stupid" --- не оскорбление. Это напоминание: если конструкция настолько сложна, что её нельзя починить в поле --- она плохо спроектирована.

### Что KISS означает в коде

```
Простой код:                          Сложный код:
────────────────────────────────────  ────────────────────────────────────
Можно понять за 30 секунд             Требует "вчитывания" 5+ минут
Очевидный поток выполнения            Нелинейный, с callbacks и ветвлениями
Минимум уровней вложенности           3+ уровня if/for/try
Использует стандартную библиотеку     Использует custom abstractions
Легко объяснить новичку               Требует знания "контекста проекта"
```

### KISS в Kotlin: язык помогает

Kotlin на уровне языка устраняет boilerplate, который в Java заставляет писать "сложно":

```kotlin
// =============================================
// Пример 1: Data class вместо 40 строк Java
// =============================================

// Java --- ~40 строк: class + getters + setters + equals + hashCode + toString + copy
// Kotlin --- 1 строка:
data class User(val name: String, val email: String, val age: Int)

// Автоматически: equals(), hashCode(), toString(), copy(), componentN()
val updated = user.copy(age = user.age + 1)
val (name, email, _) = user  // destructuring


// =============================================
// Пример 2: Null-safety вместо defensive checks
// =============================================

// Java --- лесенка проверок:
// if (user != null) { if (user.getAddress() != null) { ... } }

// Kotlin --- одна строка:
val city = user?.address?.city ?: "Не указан"


// =============================================
// Пример 3: when вместо switch + break + cast
// =============================================

// Java: switch без exhaustive check, нужны break, нет smart cast
// Kotlin: when --- expression, exhaustive для sealed, smart cast

sealed interface PaymentMethod {
    data class Card(val number: String, val expiry: String) : PaymentMethod
    data class BankTransfer(val iban: String) : PaymentMethod
    data object Cash : PaymentMethod
}

fun describe(method: PaymentMethod): String = when (method) {
    is PaymentMethod.Card -> "Карта *${method.number.takeLast(4)}"
    is PaymentMethod.BankTransfer -> "Перевод на ${method.iban}"
    PaymentMethod.Cash -> "Наличные"
    // Нет else --- компилятор гарантирует, что все варианты обработаны
}


// =============================================
// Пример 4: Expression syntax вместо мутабельных переменных
// =============================================

// Сложно: var + ветвления
var status: String
if (code in 200..299) {
    status = "success"
} else if (code in 400..499) {
    status = "client_error"
} else {
    status = "server_error"
}

// Просто: val + when expression
val status = when (code) {
    in 200..299 -> "success"
    in 400..499 -> "client_error"
    else -> "server_error"
}
```

### Метрики простоты

Как измерить, прост ли код? Несколько эвристик:

```
┌─────────────────────────────────┬─────────────┬───────────────────┐
│ Метрика                         │ "Просто"    │ "Сложно"          │
├─────────────────────────────────┼─────────────┼───────────────────┤
│ Cyclomatic complexity           │ ≤ 5         │ > 10              │
│ Уровней вложенности             │ ≤ 2         │ > 3               │
│ Параметров у функции            │ ≤ 3         │ > 5               │
│ Строк в функции                 │ ≤ 30        │ > 50              │
│ Зависимостей у класса           │ ≤ 5         │ > 8               │
│ Время понимания новым человеком │ < 1 мин     │ > 5 мин           │
└─────────────────────────────────┴─────────────┴───────────────────┘
```

> [!info] Kotlin-нюанс
> **detekt** автоматически проверяет cyclomatic complexity, вложенность, длину функций и количество параметров. Настройте пороги в `detekt.yml` и запускайте в CI --- KISS станет не пожеланием, а автоматической проверкой.

---

## YAGNI: You Ain't Gonna Need It

### Происхождение

Принцип из Extreme Programming (XP), популяризован Роном Джеффрисом в конце 1990-х. Контекст: XP-команды заметили, что разработчики тратят 50%+ времени на функциональность, которая "понадобится потом". "Потом" обычно не наступает.

> "Always implement things when you actually need them, never when you just foresee that you need them." --- Ron Jeffries

### Стоимость преждевременной генерализации

```
Написать "на будущее":
• Время на разработку       → потрачено сейчас
• Время на тестирование     → потрачено сейчас
• Время на поддержку        → тратится всегда
• Когнитивная нагрузка      → увеличена для всех
• Вероятность использования → 20-30% (исследования Standish Group)

Итого: 70-80% "запасных" фич --- wasted effort.
```

### Примеры over-engineering

```kotlin
// =============================================
// YAGNI-нарушение 1: Visitor вместо sealed class
// =============================================

// Over-engineering: Visitor pattern "на будущее"
interface ShapeVisitor<T> {
    fun visitCircle(circle: Circle): T
    fun visitRectangle(rectangle: Rectangle): T
    fun visitTriangle(triangle: Triangle): T
}

interface Shape {
    fun <T> accept(visitor: ShapeVisitor<T>): T
}

class Circle(val radius: Double) : Shape {
    override fun <T> accept(visitor: ShapeVisitor<T>): T = visitor.visitCircle(this)
}

class AreaCalculator : ShapeVisitor<Double> {
    override fun visitCircle(circle: Circle) = Math.PI * circle.radius * circle.radius
    override fun visitRectangle(rectangle: Rectangle) = rectangle.width * rectangle.height
    override fun visitTriangle(triangle: Triangle) = 0.5 * triangle.base * triangle.height
}

// Достаточно: sealed class + when
sealed interface Shape {
    data class Circle(val radius: Double) : Shape
    data class Rectangle(val width: Double, val height: Double) : Shape
    data class Triangle(val base: Double, val height: Double) : Shape
}

fun area(shape: Shape): Double = when (shape) {
    is Shape.Circle -> Math.PI * shape.radius * shape.radius
    is Shape.Rectangle -> shape.width * shape.height
    is Shape.Triangle -> 0.5 * shape.base * shape.height
}


// =============================================
// YAGNI-нарушение 2: Strategy interface с одной реализацией
// =============================================

// Over-engineering: интерфейс ради интерфейса
interface SortingStrategy<T : Comparable<T>> {
    fun sort(items: List<T>): List<T>
}

class DefaultSortingStrategy<T : Comparable<T>> : SortingStrategy<T> {
    override fun sort(items: List<T>): List<T> = items.sorted()
}

class ItemListProcessor<T : Comparable<T>>(
    private val sortingStrategy: SortingStrategy<T>
) {
    fun process(items: List<T>): List<T> = sortingStrategy.sort(items)
}

// Достаточно: HOF (higher-order function)
fun <T> process(
    items: List<T>,
    comparator: Comparator<T> = compareBy { it.hashCode() }
): List<T> = items.sortedWith(comparator)

// Или ещё проще:
val sorted = items.sorted()


// =============================================
// YAGNI-нарушение 3: Abstract Factory "на вырост"
// =============================================

// Over-engineering: фабрика для одного типа уведомлений
interface NotificationFactory {
    fun create(type: String, message: String): Notification
}

interface Notification {
    fun send()
}

class EmailNotification(private val message: String) : Notification {
    override fun send() { /* email logic */ }
}

class NotificationFactoryImpl : NotificationFactory {
    override fun create(type: String, message: String): Notification = when (type) {
        "email" -> EmailNotification(message)
        else -> throw IllegalArgumentException("Unknown type: $type")
    }
}

// Достаточно: просто функция
fun sendEmailNotification(message: String) {
    // email logic
}

// Когда ДЕЙСТВИТЕЛЬНО появится SMS --- добавить:
fun sendSmsNotification(phone: String, message: String) {
    // sms logic
}
```

### YAGNI и Kotlin: sealed class вместо паттернов

Kotlin делает YAGNI проще, потому что `sealed class` + `when` заменяет многие паттерны GoF:

```
┌────────────────────────┬──────────────────────────────────────┐
│ GoF-паттерн            │ Kotlin-альтернатива (YAGNI)          │
├────────────────────────┼──────────────────────────────────────┤
│ Visitor                │ sealed class + when (exhaustive)     │
│ Strategy               │ Higher-order function (lambda)       │
│ Builder                │ Named params + default values        │
│ Factory Method         │ Companion object + invoke()          │
│ Singleton              │ object declaration                   │
│ Observer (простой)     │ Flow / StateFlow                     │
│ Decorator              │ Extension functions / delegation     │
│ Template Method        │ Higher-order function с lambda       │
└────────────────────────┴──────────────────────────────────────┘
```

> [!info] Kotlin-нюанс
> Sealed class + when --- это **exhaustive pattern matching**. Добавление нового варианта приводит к **ошибке компиляции** во всех when-выражениях. Не нужен Visitor для "расширяемости" --- компилятор уже контролирует полноту обработки.

---

## Напряжения между принципами

### DRY vs KISS

```
Конфликт: абстракция ради DRY добавляет сложность (нарушает KISS)

Пример:
┌──────────────────────────────────────────────────────────────────┐
│ DRY говорит: "Извлеки повторяющийся код в общую функцию"       │
│ KISS говорит: "Два простых метода лучше одного сложного"        │
└──────────────────────────────────────────────────────────────────┘
```

```kotlin
// Два endpoint'а с похожей, но разной логикой

// DRY-подход: одна "универсальная" функция
fun handleRequest(
    type: RequestType,
    payload: Any,
    validate: Boolean = true,
    transform: Boolean = true,
    notify: Boolean = false,
    audit: Boolean = false
): Response {
    if (validate) validate(payload, type)    // Что именно валидируем?
    val data = if (transform) transform(payload, type) else payload
    val result = process(data, type)
    if (notify) sendNotification(result, type)
    if (audit) auditLog(result, type)
    return result.toResponse(type)
}

// KISS-подход: два простых метода
fun handleUserRegistration(payload: RegistrationRequest): Response {
    validate(payload)
    val user = createUser(payload)
    sendWelcomeEmail(user)
    return Response.created(user.toDto())
}

fun handleOrderCreation(payload: OrderRequest): Response {
    validate(payload)
    val order = createOrder(payload)
    auditLog(order)
    return Response.created(order.toDto())
}
```

**Решение:** Дублирование допустимо, если альтернатива --- запутанная абстракция. Применяй DRY к **знаниям** (бизнес-правила, конфигурация), а KISS --- к **коду** (реализация).

### KISS vs SOLID

```
Конфликт: SRP требует разделения, но разделение добавляет файлы и навигацию

┌──────────────────────────────────────────────────────────────────┐
│ SOLID (SRP) говорит: "Раздели по причинам изменения"           │
│ KISS говорит: "20 строк в одном файле проще 3 файлов по 10"    │
└──────────────────────────────────────────────────────────────────┘
```

```kotlin
// SOLID-максимализм: 5 классов для простой операции
class OrderValidator { fun validate(order: Order) { /* ... */ } }
class OrderCalculator { fun calculate(order: Order): Double { /* ... */ } }
class OrderPersister { fun save(order: Order) { /* ... */ } }
class OrderNotifier { fun notify(order: Order) { /* ... */ } }
class OrderProcessor(
    private val validator: OrderValidator,
    private val calculator: OrderCalculator,
    private val persister: OrderPersister,
    private val notifier: OrderNotifier
) {
    fun process(order: Order) { /* ... */ }
}

// KISS-прагматизм: один класс, пока не появятся разные причины изменения
class OrderService(
    private val repository: OrderRepository,
    private val emailService: EmailService
) {
    fun processOrder(order: Order) {
        require(order.items.isNotEmpty()) { "Order must have items" }
        val total = order.items.sumOf { it.price * it.quantity }
        val saved = repository.save(order.copy(total = total))
        emailService.sendConfirmation(saved)
    }
}
```

### YAGNI vs OCP (Open/Closed Principle)

```
Конфликт: OCP требует "точек расширения", YAGNI --- "не делай заранее"

┌──────────────────────────────────────────────────────────────────┐
│ OCP говорит: "Предусмотри расширение без изменения кода"        │
│ YAGNI говорит: "Не предусматривай то, что не нужно сейчас"      │
└──────────────────────────────────────────────────────────────────┘
```

```kotlin
// YAGNI сейчас --- один вариант оплаты
fun processPayment(order: Order) {
    stripeApi.charge(order.total, order.paymentToken)
}

// Когда ДЕЙСТВИТЕЛЬНО понадобится второй способ --- тогда и рефакторим:
interface PaymentProcessor {
    fun charge(amount: Double, token: String)
}

class StripeProcessor(private val api: StripeApi) : PaymentProcessor {
    override fun charge(amount: Double, token: String) = api.charge(amount, token)
}

class PayPalProcessor(private val api: PayPalApi) : PaymentProcessor {
    override fun charge(amount: Double, token: String) = api.process(amount, token)
}
```

**Решение:** "Make it work, make it right, make it fast" (Kent Beck). Сначала рабочий код, потом правильный, потом быстрый. Абстракции добавляй при **второй** необходимости (Rule of Three), не при первой.

### Сводная таблица конфликтов

```
┌──────────────────┬───────────────────────────────────────────────┐
│ Конфликт         │ Как разрешать                                 │
├──────────────────┼───────────────────────────────────────────────┤
│ DRY vs KISS      │ DRY для знаний, KISS для реализации          │
│ KISS vs SRP      │ Разделяй при реальных причинах изменения     │
│ YAGNI vs OCP     │ Абстрагируй при 2-й необходимости            │
│ DRY vs YAGNI     │ Rule of Three: 3-й дубликат → абстракция     │
│ KISS vs DRY      │ Простая дупликация лучше сложной абстракции   │
│ YAGNI vs тесты   │ Тестируемость --- реальное требование, не YAGNI│
└──────────────────┴───────────────────────────────────────────────┘
```

---

## Практические примеры Kotlin: до и после

### Пример 1: DRY через extension function

```kotlin
// ---- ДО: дублирование форматирования в 5 местах ----
class UserProfileScreen {
    fun showCreatedDate(user: User) {
        val formatter = SimpleDateFormat("dd MMM yyyy", Locale("ru"))
        createdLabel.text = formatter.format(user.createdAt)
    }
}

class OrderDetailScreen {
    fun showOrderDate(order: Order) {
        val formatter = SimpleDateFormat("dd MMM yyyy", Locale("ru"))
        dateLabel.text = formatter.format(order.createdAt)
    }
}

// ---- ПОСЛЕ: extension function --- DRY без класса-утилиты ----
fun Date.formatRussian(): String {
    val formatter = SimpleDateFormat("dd MMM yyyy", Locale("ru"))
    return formatter.format(this)
}

// Использование:
createdLabel.text = user.createdAt.formatRussian()
dateLabel.text = order.createdAt.formatRussian()
```

### Пример 2: KISS через sealed class

```kotlin
// ---- ДО: сложная иерархия классов + интерфейсы ----
interface ApiResult
interface SuccessResult : ApiResult { val data: Any }
interface ErrorResult : ApiResult { val error: Throwable }
interface LoadingResult : ApiResult
class SuccessResultImpl(override val data: Any) : SuccessResult
class ErrorResultImpl(override val error: Throwable) : ErrorResult
class LoadingResultImpl : LoadingResult

fun handle(result: ApiResult) {
    if (result is SuccessResult) { /* ... */ }
    else if (result is ErrorResult) { /* ... */ }
    else if (result is LoadingResult) { /* ... */ }
}

// ---- ПОСЛЕ: sealed class --- KISS + type safety ----
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val exception: Throwable) : ApiResult<Nothing>()
    data object Loading : ApiResult<Nothing>()
}

fun <T> handle(result: ApiResult<T>) = when (result) {
    is ApiResult.Success -> showData(result.data)    // smart cast!
    is ApiResult.Error -> showError(result.exception)
    ApiResult.Loading -> showSpinner()
}
```

### Пример 3: YAGNI --- не создавай абстракции заранее

```kotlin
// ---- ДО: "А вдруг понадобится кэш для всего!" ----
interface Cache<K, V> {
    fun get(key: K): V?
    fun put(key: K, value: V)
    fun invalidate(key: K)
    fun invalidateAll()
    fun size(): Int
}

class InMemoryCache<K, V> : Cache<K, V> {
    private val map = mutableMapOf<K, V>()
    override fun get(key: K) = map[key]
    override fun put(key: K, value: V) { map[key] = value }
    override fun invalidate(key: K) { map.remove(key) }
    override fun invalidateAll() { map.clear() }
    override fun size() = map.size
}

class UserRepository(private val cache: Cache<String, User>) { /* ... */ }

// ---- ПОСЛЕ: просто Map пока хватает ----
class UserRepository {
    private val cache = mutableMapOf<String, User>()

    fun getUser(id: String): User {
        return cache.getOrPut(id) { api.fetchUser(id) }
    }
}

// Когда реально понадобится eviction, TTL, etc. --- тогда подключим
// полноценную библиотеку (Caffeine, Guava Cache).
// Не изобретай велосипед заранее.
```

### Пример 4: Всё вместе --- рефакторинг с тремя принципами

```kotlin
// ---- ДО: нарушены все три принципа ----

// DRY: валидация дублируется
// KISS: сложная условная логика
// YAGNI: поддержка 3 типов скидок, когда есть только 1
fun processOrder(order: Order, user: User, discountType: String?) {
    // Валидация (дублирование)
    if (order.items.isEmpty()) throw Exception("no items")
    if (user.id.isEmpty()) throw Exception("no user")

    var total = 0.0
    for (item in order.items) {
        total += item.price * item.qty
    }

    // YAGNI: 3 типа скидок, реально есть только процентная
    when (discountType) {
        "percentage" -> total *= 0.9
        "fixed" -> total -= 10.0  // Никогда не используется
        "loyalty" -> {            // Никогда не используется
            val points = user.loyaltyPoints ?: 0
            total -= points * 0.01
        }
    }

    // Валидация (дублирование)
    if (total <= 0) throw Exception("invalid total")
    if (user.balance < total) throw Exception("insufficient funds")

    // Сохранение
    database.save(order.copy(total = total))
}

// ---- ПОСЛЕ: DRY + KISS + YAGNI ----

fun processOrder(order: Order, user: User) {
    // Валидация: require (DRY + KISS --- стандартные функции Kotlin)
    require(order.items.isNotEmpty()) { "Order must have items" }
    require(user.id.isNotBlank()) { "User must have an ID" }

    // Расчёт (KISS: простое выражение)
    val subtotal = order.items.sumOf { it.price * it.qty }
    val total = applyDiscount(subtotal, STANDARD_DISCOUNT_RATE)

    // Проверка баланса
    check(total > 0) { "Total must be positive, got $total" }
    check(user.balance >= total) {
        "Insufficient funds: need $total, have ${user.balance}"
    }

    repository.save(order.copy(total = total))
}

// YAGNI: только процентная скидка --- потому что только она нужна
private fun applyDiscount(amount: Double, rate: Double): Double =
    amount * (1 - rate)

private const val STANDARD_DISCOUNT_RATE = 0.1
```

---

## Знаменитые цитаты

| Цитата | Автор | Контекст |
|--------|-------|----------|
| "Premature optimization is the root of all evil" | Donald Knuth, 1974 | "Мы должны забыть о маленьких оптимизациях 97% времени" |
| "Make it work, make it right, make it fast" | Kent Beck | Порядок приоритетов разработки |
| "Duplication is far cheaper than the wrong abstraction" | Sandi Metz, 2014 | Критика слепого DRY |
| "Simplicity is the ultimate sophistication" | Леонардо да Винчи | Применимо к коду: простое решение = зрелое решение |
| "The best code is no code at all" | Jeff Atwood | Каждая строка --- потенциальный баг |
| "Always implement things when you actually need them" | Ron Jeffries | Определение YAGNI |
| "Programs must be written for people to read" | Abelson & Sussman, SICP | KISS для кода |

---

## Подводные камни

### 1. "DRY-маньяк": абстрагирует всё

Видит 2 одинаковые строки --- немедленно извлекает в функцию. Через месяц проект из 50 файлов превращается в 200 файлов по 10 строк, где невозможно найти бизнес-логику.

**Лечение:** Rule of Three. Дублирование --- не грех. Неправильная абстракция --- грех.

### 2. "KISS-релятивист": у каждого своё "просто"

"Мне это просто" --- говорит senior про монадический стек трансформеров. Простота --- не субъективное ощущение, а **измеримая** характеристика: cyclomatic complexity, уровни вложенности, число зависимостей.

**Лечение:** Используйте detekt для объективных метрик. Проверяйте: может ли junior-разработчик понять код за 5 минут?

### 3. "YAGNI как оправдание": не рефакторить

"Нам это пока не нужно" --- говорят 6 месяцев подряд. Код обрастает техническим долгом. YAGNI не означает "не рефакторить". YAGNI означает "не добавлять функциональность на будущее".

**Лечение:** Различайте "новый функционал" (YAGNI) и "улучшение существующего" (рефакторинг). Рефакторинг --- не нарушение YAGNI.

### 4. Конфликт принципов в команде

Один разработчик --- фанат DRY, другой --- KISS. Код-ревью превращается в бесконечный спор.

**Лечение:** Явные правила в guidelines проекта: "Rule of Three для DRY", "Макс. cyclomatic complexity = 10", "Интерфейс --- только при 2+ реализациях".

---

## Проверь себя

> [!question]- Два метода содержат одинаковый код: `amount * 0.1`. Это нарушение DRY?
> Нет, если они описывают **разные бизнес-правила** (например, налог на доставку и сервисный сбор). Сегодня оба 10%, но завтра могут измениться независимо. DRY --- о дублировании **знаний**, не кода. Одинаковый код --- случайное совпадение. Объединение приведёт к "неправильной абстракции" Sandi Metz.

> [!question]- Разработчик создал интерфейс `PaymentProcessor` с единственной реализацией `StripeProcessor`. Какой принцип нарушен?
> YAGNI. Интерфейс для единственной реализации --- преждевременная абстракция. Когда реально появится второй способ оплаты --- тогда и извлекайте интерфейс (это займёт 5 минут в IDE). До этого момента интерфейс только добавляет когнитивную нагрузку при навигации. Исключение: если интерфейс нужен для тестирования (мок).

> [!question]- Функция `handleRequest()` принимает 8 параметров, 5 из которых --- boolean флаги. Какие принципы нарушены?
> **KISS** --- слишком много параметров, сложно понять поведение (2^5 = 32 комбинации флагов). **DRY в неправильной форме** --- попытка объединить разную логику в одну "универсальную" функцию. Решение: разбить на отдельные функции `handleUserRegistration()`, `handleOrderCreation()` и т.д.

> [!question]- Как Kotlin помогает соблюдать KISS на уровне языка? Назовите 4 фичи.
> 1) **Data classes** --- убирают boilerplate equals/hashCode/toString (40 строк Java = 1 строка Kotlin). 2) **Null-safety** --- убирает defensive checks (`if != null` лесенки). 3) **Expression syntax** --- `when` и `if` как выражения, без `var` + присвоения. 4) **Default parameters + named arguments** --- убирают цепочки перегрузок и Builder pattern.

> [!question]- Чем отличается "дублирование кода" от "дублирования знания"?
> Дублирование **кода** --- одинаковые строки в разных местах (может быть случайным совпадением, не требует рефакторинга). Дублирование **знания** --- одно бизнес-правило определено в нескольких местах (при изменении нужно обновить все). Пример: ставка налога `0.2` захардкожена в 5 файлах --- это дублирование знания. Два метода с `amount * 0.1` для разных бизнес-целей --- дублирование кода (допустимо).

---

## Ключевые карточки

Что на самом деле означает DRY?
?
"Every piece of **knowledge** must have a single, unambiguous, authoritative representation within a system" (Hunt, Thomas, 1999). Ключевое слово --- **knowledge** (знание), а не код. Одинаковый код --- не обязательно нарушение DRY, если он описывает разные бизнес-правила.

Что такое Rule of Three и зачем оно нужно?
?
Принцип от Martin Fowler: дублируй до третьего раза, после третьего повторения --- извлекай абстракцию. Защита от преждевременной абстракции: два совпадения могут быть случайностью, три --- паттерн.

Как Sandi Metz описала проблему "неправильной абстракции"?
?
"Duplication is far cheaper than the wrong abstraction." Типичный путь: программист видит дубликат → извлекает абстракцию → новые требования "почти подходят" → добавляются параметры и условия → функция превращается в нечитаемый монстр с 8 параметрами и 12 ветвлениями.

Откуда взялся KISS и что он означает в коде?
?
Kelly Johnson, Lockheed Skunk Works, 1960-е. Требование: самолёт должен ремонтироваться средним механиком в поле. В коде: решение должно быть понятно любому разработчику без "вчитывания". Метрики: cyclomatic complexity ≤ 5, вложенность ≤ 2, параметров ≤ 3.

Что такое YAGNI и откуда он взялся?
?
"You Ain't Gonna Need It" --- принцип из Extreme Programming (Ron Jeffries, конец 1990-х). Реализуй функциональность только когда она реально нужна. Исследования: 70--80% "запасных" фич никогда не используются (Standish Group).

Как разрешить конфликт DRY vs KISS?
?
DRY --- для **знаний** (бизнес-правила, конфигурация): одно место определения. KISS --- для **реализации** (код): два простых метода лучше одного сложного "универсального". Простая дупликация кода лучше сложной абстракции.

Как разрешить конфликт YAGNI vs OCP?
?
Правило Kent Beck: "Make it work, make it right, make it fast." Абстракции добавляй при **второй** необходимости (Rule of Three), не при первой. YAGNI не запрещает рефакторинг --- он запрещает преждевременную генерализацию.

Какие GoF-паттерны Kotlin заменяет средствами языка?
?
Visitor → sealed class + when. Strategy → higher-order function. Builder → named params + default values. Factory Method → companion object + invoke(). Singleton → object declaration. Observer → Flow/StateFlow. Decorator → extension functions / delegation.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Чистый код | [[clean-code]] | Практики именования, функций, комментариев в Kotlin |
| SOLID | [[solid-principles]] | 5 принципов ООП-дизайна, которые конфликтуют с KISS/YAGNI |
| Запахи | [[code-smells]] | Как распознать нарушения DRY/KISS/YAGNI в существующем коде |
| ООП | [[composition-vs-inheritance]] | Композиция vs наследование --- контекст для правильного DRY |
| Основы ООП | [[oop-fundamentals]] | Фундамент, на котором стоят все принципы |

---

## Источники

### Первоисточники
- Hunt A., Thomas D. (1999). *The Pragmatic Programmer*. --- Определение DRY: "Every piece of knowledge must have a single, unambiguous, authoritative representation within a system"
- Beck K. (1999). *Extreme Programming Explained*. --- YAGNI как часть методологии XP
- Martin R. C. (2008). *Clean Code*. --- Применение принципов к именованию, функциям, комментариям

### Критика и переосмысление
- Metz S. (2014). [The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction) --- "Duplication is far cheaper than the wrong abstraction"
- Dodds K. C. [AHA Programming](https://kentcdodds.com/blog/aha-programming) --- "Avoid Hasty Abstractions" как развитие идей Sandi Metz
- [DRY --- Wikipedia](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself) --- история и контекст принципа
- [YAGNI --- Wikipedia](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it) --- определение и контекст XP

### Kotlin-ресурсы
- Moskala M. (2024). *Effective Kotlin*. --- Применение принципов в контексте Kotlin
- [Kotlin Idioms](https://kotlinlang.org/docs/idioms.html) --- официальные идиомы, реализующие KISS
- [Coding Conventions](https://kotlinlang.org/docs/coding-conventions.html) --- стиль кода Kotlin
- [KISS in Android: Kotlin and Compose Best Practices](https://medium.com/@ramadan123sayed/keep-it-simple-stupid-kiss-in-android-kotlin-and-jetpack-compose-best-practices-4c910df93659) --- KISS в контексте Android

### Обзорные статьи
- [DRY, KISS & YAGNI Principles Guide](https://www.boldare.com/blog/kiss-yagni-dry-principles/) --- обзор с примерами
- [YAGNI: The pragmatic path](https://mikelvu.medium.com/yagni-the-pragmatic-path-to-prevent-over-engineering-in-software-development-e897911dedcb) --- over-engineering примеры
- [YAGNI Revisited](https://enterprisecraftsmanship.com/posts/yagni-revisited/) --- Enterprise Craftsmanship о границах применения

---

*Проверено: 2026-02-19 | Источники верифицированы*
