---
title: "Factory: создание объектов без привязки к конкретным классам"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/design-patterns
  - topic/kotlin
  - pattern/creational
related:
  - "[[design-patterns-overview]]"
  - "[[singleton-pattern]]"
  - "[[builder-pattern]]"
  - "[[solid-principles]]"
  - "[[kotlin-oop]]"
---

# Factory: создание объектов без привязки к конкретным классам

Вызов `listOf(1, 2, 3)` в Kotlin --- это Factory. `Retrofit.create(ApiService::class.java)` --- тоже Factory. `Room.databaseBuilder(...)` --- и это Factory. Паттерн настолько фундаментален, что используется повсеместно, даже когда разработчик не задумывается о нём. Factory Method и Abstract Factory --- два GoF-паттерна, которые решают одну задачу: **отделить создание объекта от его использования**. В Kotlin они реализуются элегантнее, чем в Java, благодаря `companion object`, `sealed class`, `operator fun invoke()` и reified-дженерикам.

---

## Проблема

Без фабрики клиентский код знает о конкретных классах и их зависимостях:

```kotlin
// Плохо: код знает о ВСЕХ типах платежей и их конфигурациях
fun processPayment(type: String, amount: Double) {
    when (type) {
        "card" -> {
            val processor = CardProcessor(apiKey, merchantId, timeout)
            processor.charge(amount)
        }
        "paypal" -> {
            val processor = PayPalProcessor(clientId, secret, sandbox = false)
            processor.charge(amount)
        }
        "crypto" -> {
            val processor = CryptoProcessor(walletAddress, network, gasLimit)
            processor.charge(amount)
        }
        // Добавить Apple Pay? → менять ЭТУ функцию
        // Добавить Google Pay? → менять ЭТУ функцию
        // Через год: 200 строк в одном when
    }
}
```

```
Проблемы:
┌─────────────────────────────────────────────────────────────────┐
│  1. Tight coupling: код привязан к конкретным классам           │
│  2. OCP нарушен: новый тип = изменение существующего кода       │
│  3. Дублирование: если создание в 5 местах → менять 5 мест     │
│  4. Тестирование: нельзя подменить CardProcessor на mock        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Factory Method

### Intent

Определить интерфейс для создания объекта, но позволить подклассам решать, какой класс создавать.

```
┌──────────────────────────────────────────────────────────────────┐
│                      FACTORY METHOD                              │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Creator (abstract)                Product (interface)            │
│  ├── factoryMethod(): Product      ├── execute()                 │
│  └── doWork() {                    │                             │
│        val p = factoryMethod()     │                             │
│        p.execute()                 │                             │
│      }                                    ↑                      │
│          ↑                         ┌──────┴──────┐               │
│  ┌───────┴────────┐               ProductA    ProductB           │
│  CreatorA    CreatorB                                            │
│  factoryMethod()  factoryMethod()                                │
│  → ProductA       → ProductB                                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

| Участник | Роль | Зачем нужен |
|----------|------|-------------|
| **Product** | Общий интерфейс объектов | Полиморфизм --- клиент работает с интерфейсом |
| **ConcreteProduct** | Конкретная реализация | Реальная логика |
| **Creator** | Объявляет factory method | Единая точка создания |
| **ConcreteCreator** | Решает, какой Product создать | Инкапсулирует логику выбора |

### Классическая реализация

```kotlin
// Product --- общий интерфейс
interface Notification {
    fun send(message: String)
}

// Конкретные продукты
class EmailNotification(private val address: String) : Notification {
    override fun send(message: String) {
        println("Email to $address: $message")
    }
}

class PushNotification(private val token: String) : Notification {
    override fun send(message: String) {
        println("Push to $token: $message")
    }
}

class SmsNotification(private val phone: String) : Notification {
    override fun send(message: String) {
        println("SMS to $phone: $message")
    }
}

// Creator --- абстрактный класс с factory method
abstract class NotificationService {
    abstract fun createNotification(recipient: String): Notification

    // Template Method: использует factory method
    fun notify(recipient: String, message: String) {
        val notification = createNotification(recipient)
        notification.send(message)
    }
}

// Конкретные Creators
class EmailNotificationService : NotificationService() {
    override fun createNotification(recipient: String) =
        EmailNotification(recipient)
}

class PushNotificationService : NotificationService() {
    override fun createNotification(recipient: String) =
        PushNotification(recipient)
}
```

---

## Kotlin-идиоматичные фабрики

В Kotlin не обязательно создавать отдельные классы-фабрики. Язык предоставляет более лаконичные инструменты.

### 1. `companion object` как Factory

```kotlin
class User private constructor(
    val id: String,
    val name: String,
    val email: String,
    val role: Role
) {
    companion object {
        fun fromEmail(email: String): User {
            val name = email.substringBefore("@")
                .replaceFirstChar { it.uppercase() }
            return User(
                id = generateId(),
                name = name,
                email = email,
                role = Role.USER
            )
        }

        fun admin(name: String, email: String): User =
            User(generateId(), name, email, Role.ADMIN)

        fun guest(): User =
            User("guest", "Guest", "guest@example.com", Role.GUEST)

        private fun generateId(): String =
            java.util.UUID.randomUUID().toString()
    }
}

// Использование --- выразительнее, чем конструктор
val user1 = User.fromEmail("alice@company.com")  // User(name=Alice, role=USER)
val user2 = User.admin("Bob", "bob@company.com") // User(name=Bob, role=ADMIN)
val user3 = User.guest()                           // Guest user
```

> [!info] Kotlin-нюанс
> Маркин Москала в "Effective Kotlin" (Item 30) рекомендует factory functions вместо конструкторов по тем же причинам, что и Блох в "Effective Java" (Item 1): (1) именованные --- `fromEmail()` понятнее, чем `User(email)`, (2) могут возвращать подтипы, (3) могут кэшировать, (4) могут возвращать `null` вместо бросания исключения.

### 2. `operator fun invoke()` --- естественный синтаксис

```kotlin
class Color private constructor(
    val red: Int,
    val green: Int,
    val blue: Int
) {
    init {
        require(red in 0..255) { "Red must be 0..255, got $red" }
        require(green in 0..255) { "Green must be 0..255, got $green" }
        require(blue in 0..255) { "Blue must be 0..255, got $blue" }
    }

    companion object {
        // operator invoke --- вызывается как конструктор
        operator fun invoke(red: Int, green: Int, blue: Int): Color =
            Color(red, green, blue)

        operator fun invoke(hex: String): Color {
            val clean = hex.removePrefix("#")
            return Color(
                red = clean.substring(0, 2).toInt(16),
                green = clean.substring(2, 4).toInt(16),
                blue = clean.substring(4, 6).toInt(16)
            )
        }

        // Предопределённые цвета
        val RED = Color(255, 0, 0)
        val GREEN = Color(0, 255, 0)
        val BLUE = Color(0, 0, 255)
    }

    override fun toString() = "#${red.hex()}${green.hex()}${blue.hex()}"
    private fun Int.hex() = toString(16).padStart(2, '0')
}

// Использование --- выглядит как конструктор, но это фабрика
val red = Color(255, 0, 0)       // через RGB
val blue = Color("#0000FF")      // через HEX
val green = Color.GREEN          // предопределённый
```

> [!info] Kotlin-нюанс
> `operator fun invoke()` позволяет вызывать объект как функцию: `Color(...)` на самом деле вызывает `Color.Companion.invoke(...)`. Однако Москала предостерегает: это может сбивать с толку, потому что выглядит как конструктор, но поведение может отличаться (кэширование, nullable return, побочные эффекты). Используйте, когда семантика действительно "создание экземпляра".

### 3. `sealed class` + `when` для типобезопасных фабрик

```kotlin
sealed class PaymentProcessor {
    abstract fun charge(amount: Double): PaymentResult

    data class Card(
        val cardNumber: String,
        val expiry: String,
        val cvv: String
    ) : PaymentProcessor() {
        override fun charge(amount: Double): PaymentResult {
            // Обработка карточного платежа
            println("Charging card ${"*".repeat(12)}${cardNumber.takeLast(4)}: $$amount")
            return PaymentResult.Success(transactionId = "card_${System.currentTimeMillis()}")
        }
    }

    data class PayPal(
        val email: String
    ) : PaymentProcessor() {
        override fun charge(amount: Double): PaymentResult {
            println("Charging PayPal $email: $$amount")
            return PaymentResult.Success(transactionId = "pp_${System.currentTimeMillis()}")
        }
    }

    data class Crypto(
        val walletAddress: String,
        val network: String = "ethereum"
    ) : PaymentProcessor() {
        override fun charge(amount: Double): PaymentResult {
            println("Charging crypto $walletAddress on $network: $$amount")
            return PaymentResult.Success(transactionId = "crypto_${System.currentTimeMillis()}")
        }
    }

    companion object {
        fun fromConfig(config: PaymentConfig): PaymentProcessor =
            when (config) {
                is PaymentConfig.CardConfig ->
                    Card(config.number, config.expiry, config.cvv)
                is PaymentConfig.PayPalConfig ->
                    PayPal(config.email)
                is PaymentConfig.CryptoConfig ->
                    Crypto(config.wallet, config.network)
                // Компилятор гарантирует: если добавим новый тип ---
                // код не скомпилируется, пока не обработаем его здесь
            }
    }
}

sealed class PaymentResult {
    data class Success(val transactionId: String) : PaymentResult()
    data class Failure(val error: String) : PaymentResult()
}
```

### 4. Extension functions как фабрики

```kotlin
// String → доменный объект
fun String.toEmail(): Email {
    require(contains("@")) { "Invalid email: $this" }
    return Email(this)
}

fun String.toUserId(): UserId {
    require(isNotBlank()) { "UserId cannot be blank" }
    return UserId(this)
}

// Map → доменный объект
fun Map<String, Any>.toUser(): User = User(
    id = (this["id"] as String).toUserId(),
    name = this["name"] as String,
    email = (this["email"] as String).toEmail()
)

// Использование
val email = "alice@company.com".toEmail()
val userId = "usr_123".toUserId()
val user = mapOf(
    "id" to "usr_123",
    "name" to "Alice",
    "email" to "alice@company.com"
).toUser()
```

### 5. Top-level factory functions (стиль stdlib)

Kotlin stdlib активно использует top-level фабричные функции:

```kotlin
// Стандартная библиотека Kotlin:
val list = listOf(1, 2, 3)               // → List<Int>
val mutableList = mutableListOf(1, 2, 3) // → MutableList<Int>
val map = mapOf("a" to 1, "b" to 2)      // → Map<String, Int>
val set = setOf(1, 2, 3)                  // → Set<Int>
val sequence = sequenceOf(1, 2, 3)        // → Sequence<Int>

// Свои top-level фабрики:
fun userOf(name: String, email: String): User =
    User(generateId(), name, email, Role.USER)

fun connectionPool(
    url: String,
    maxSize: Int = 10,
    timeout: Long = 30_000L
): ConnectionPool = ConnectionPool.Builder()
    .url(url)
    .maxSize(maxSize)
    .timeout(timeout)
    .build()
```

### 6. `inline fun <reified T>` --- типизированные фабрики

```kotlin
// Фабрика, которая знает тип в runtime
inline fun <reified T : ViewModel> Fragment.viewModel(): T {
    return ViewModelProvider(this)[T::class.java]
}

// Использование --- тип выводится автоматически
class UserFragment : Fragment() {
    private val viewModel: UserViewModel by lazy { viewModel() }
}

// Фабрика с сериализацией
inline fun <reified T> String.fromJson(): T {
    val adapter = Moshi.Builder().build().adapter(T::class.java)
    return adapter.fromJson(this)
        ?: throw JsonDataException("Failed to parse ${T::class.simpleName}")
}

// Использование
val user = """{"name": "Alice", "age": 30}""".fromJson<User>()
val config = configJson.fromJson<AppConfig>()
```

> [!info] Kotlin-нюанс
> `reified` generics --- уникальная фича Kotlin. В Java generic типы стираются в runtime (type erasure), поэтому `T::class.java` невозможен. В Kotlin `inline fun <reified T>` сохраняет тип: функция инлайнится, и конкретный тип подставляется в месте вызова. Это позволяет создавать type-safe фабрики без передачи `Class<T>` параметра.

---

## Abstract Factory

### Intent

Предоставить интерфейс для создания **семейства связанных объектов** без привязки к конкретным классам.

```
┌──────────────────────────────────────────────────────────────────┐
│                     ABSTRACT FACTORY                             │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  AbstractFactory                 AbstractProductA                │
│  ├── createProductA()            AbstractProductB                │
│  └── createProductB()                                            │
│          ↑                              ↑                        │
│  ┌───────┴───────┐              ┌───────┴───────┐               │
│  Factory1   Factory2            ProductA1  ProductA2             │
│  createA()→A1  createA()→A2    ProductB1  ProductB2             │
│  createB()→B1  createB()→B2                                     │
│                                                                  │
│  Factory1 создаёт семейство: ProductA1 + ProductB1              │
│  Factory2 создаёт семейство: ProductA2 + ProductB2              │
└──────────────────────────────────────────────────────────────────┘
```

**Разница с Factory Method:**
- **Factory Method** --- один метод создаёт один тип продукта
- **Abstract Factory** --- интерфейс с несколькими методами, создающими **семейство** связанных продуктов

### Пример: UI-тема (Material / iOS)

```kotlin
// Абстрактные продукты
interface Button {
    fun render(): String
}

interface TextField {
    fun render(): String
}

interface Dialog {
    fun show(title: String, message: String): String
}

// Абстрактная фабрика
interface UIFactory {
    fun createButton(text: String): Button
    fun createTextField(placeholder: String): TextField
    fun createDialog(): Dialog
}

// ─── Семейство Material Design ──────────────────────────────────

class MaterialButton(private val text: String) : Button {
    override fun render() = "<MaterialButton>$text</MaterialButton>"
}

class MaterialTextField(private val placeholder: String) : TextField {
    override fun render() = "<MaterialTextField hint='$placeholder'/>"
}

class MaterialDialog : Dialog {
    override fun show(title: String, message: String) =
        "<MaterialDialog title='$title'>$message</MaterialDialog>"
}

class MaterialUIFactory : UIFactory {
    override fun createButton(text: String) = MaterialButton(text)
    override fun createTextField(placeholder: String) = MaterialTextField(placeholder)
    override fun createDialog() = MaterialDialog()
}

// ─── Семейство iOS-стиль ────────────────────────────────────────

class IOSButton(private val text: String) : Button {
    override fun render() = "<UIButton>$text</UIButton>"
}

class IOSTextField(private val placeholder: String) : TextField {
    override fun render() = "<UITextField placeholder='$placeholder'/>"
}

class IOSDialog : Dialog {
    override fun show(title: String, message: String) =
        "<UIAlertController title='$title'>$message</UIAlertController>"
}

class IOSUIFactory : UIFactory {
    override fun createButton(text: String) = IOSButton(text)
    override fun createTextField(placeholder: String) = IOSTextField(placeholder)
    override fun createDialog() = IOSDialog()
}

// ─── Клиентский код ─────────────────────────────────────────────

class LoginScreen(private val ui: UIFactory) {
    fun render(): String {
        val emailField = ui.createTextField("Email")
        val passwordField = ui.createTextField("Password")
        val loginButton = ui.createButton("Sign In")

        return """
            ${emailField.render()}
            ${passwordField.render()}
            ${loginButton.render()}
        """.trimIndent()
    }
}

// LoginScreen не знает, Material это или iOS
val materialLogin = LoginScreen(MaterialUIFactory())
val iosLogin = LoginScreen(IOSUIFactory())
```

### Kotlin-идиоматичная Abstract Factory

```kotlin
// sealed class как семейство + companion factory
sealed class UITheme {
    abstract val factory: UIFactory

    data object Material : UITheme() {
        override val factory = MaterialUIFactory()
    }

    data object IOS : UITheme() {
        override val factory = IOSUIFactory()
    }

    data object Custom : UITheme() {
        override val factory = CustomUIFactory()
    }

    companion object {
        fun fromPlatform(): UITheme = when {
            System.getProperty("os.name").contains("Mac") -> IOS
            else -> Material
        }
    }
}

// Использование
val theme = UITheme.fromPlatform()
val screen = LoginScreen(theme.factory)
```

---

## Когда использовать Factory

### Factory Method

```
Используй когда:
├── Тип объекта определяется в runtime
├── Создание сложное (много зависимостей, валидация)
├── Нужно кэширование (возвращать существующий объект)
├── Нужны именованные конструкторы (fromEmail, fromJson, guest)
└── Тестирование: подменить создание mock-ом

Не используй когда:
├── Конструктор простой: User(name, email)
├── Тип всегда один --- фабрика без выбора
├── Named/default parameters достаточно
└── Фабрика просто оборачивает new (cargo cult)
```

### Abstract Factory

```
Используй когда:
├── Нужно семейство связанных объектов (UI-компоненты одной темы)
├── Семейства должны быть взаимозаменяемы
├── Нельзя смешивать объекты из разных семейств
└── Добавление нового семейства --- частая операция

Не используй когда:
├── Один тип продукта --- достаточно Factory Method
├── Семейство состоит из 1-2 объектов --- слишком много абстракции
└── Семейства не заменяемы --- нет смысла в фабрике
```

---

## Factory в реальных библиотеках

### Retrofit

```kotlin
// Retrofit.create() --- Factory Method
val apiService = Retrofit.Builder()
    .baseUrl("https://api.example.com")
    .addConverterFactory(MoshiConverterFactory.create())
    .build()
    .create(ApiService::class.java)  // ← Factory Method: создаёт реализацию интерфейса

// Под капотом: Retrofit генерирует класс, реализующий ApiService,
// через Dynamic Proxy. Клиент не знает конкретный класс.
```

### Room

```kotlin
// Room.databaseBuilder() --- Builder + Factory
val database = Room.databaseBuilder(
    context.applicationContext,
    AppDatabase::class.java,
    "app-database"
)
    .addMigrations(MIGRATION_1_2, MIGRATION_2_3)
    .fallbackToDestructiveMigration()
    .build()  // ← Factory: создаёт конкретную реализацию AppDatabase
```

### Ktor HttpClient

```kotlin
// HttpClient {} --- Factory с DSL-конфигурацией
val client = HttpClient(CIO) {  // CIO --- engine factory
    install(ContentNegotiation) {
        json(Json {
            prettyPrint = true
            ignoreUnknownKeys = true
        })
    }
    install(Logging) {
        level = LogLevel.HEADERS
    }
    defaultRequest {
        url("https://api.example.com")
        header("Authorization", "Bearer $token")
    }
}
// HttpClient сам выбирает реализацию в зависимости от engine (CIO, Netty, OkHttp)
```

### Kotlin stdlib

```kotlin
// Top-level factory functions --- самый простой Factory Method
val list = listOf(1, 2, 3)       // создаёт ArrayList или оптимизированную версию
val emptyList = emptyList<Int>()  // создаёт singleton EmptyList
val map = buildMap {              // builder-factory
    put("key1", "value1")
    put("key2", "value2")
}
val sequence = sequence {         // factory для ленивой последовательности
    yield(1)
    yieldAll(listOf(2, 3))
}
```

---

## Когда Factory --- антипаттерн

### 1. Factory для одного типа

```kotlin
// Плохо: Factory без выбора --- просто обёртка
class UserFactory {
    fun create(name: String, email: String) = User(name, email)
}

// Зачем? Достаточно:
val user = User(name, email)
```

### 2. Factory Factory

```kotlin
// Плохо: фабрика создаёт фабрику
class PaymentProcessorFactoryFactory {
    fun createFactory(region: String): PaymentProcessorFactory =
        when (region) {
            "EU" -> EUPaymentProcessorFactory()
            "US" -> USPaymentProcessorFactory()
            else -> DefaultPaymentProcessorFactory()
        }
}

// Проще:
fun createPaymentProcessor(region: String, type: String): PaymentProcessor =
    when (region to type) {
        "EU" to "card" -> EUCardProcessor()
        "US" to "card" -> USCardProcessor()
        // ...
        else -> DefaultProcessor()
    }
```

### 3. Factory вместо конструктора с named params

```kotlin
// Не нужно:
class NotificationBuilder {
    private var title: String = ""
    private var body: String = ""
    private var icon: Int = 0
    private var channel: String = "default"

    fun title(t: String) = apply { title = t }
    fun body(b: String) = apply { body = b }
    fun icon(i: Int) = apply { icon = i }
    fun channel(c: String) = apply { channel = c }
    fun build() = Notification(title, body, icon, channel)
}

// В Kotlin достаточно:
data class Notification(
    val title: String,
    val body: String,
    val icon: Int = 0,
    val channel: String = "default"
)

val notification = Notification(
    title = "New message",
    body = "Hello!"
)
```

---

## Продвинутый пример: Registry-based Factory

Расширяемая фабрика, где новые типы регистрируются без изменения фабричного кода:

```kotlin
// Интерфейс продукта
interface FileParser {
    fun parse(content: String): ParseResult
}

// Конкретные парсеры
class JsonParser : FileParser {
    override fun parse(content: String): ParseResult {
        // парсинг JSON
        return ParseResult(format = "JSON", data = content)
    }
}

class XmlParser : FileParser {
    override fun parse(content: String): ParseResult {
        // парсинг XML
        return ParseResult(format = "XML", data = content)
    }
}

class CsvParser(private val delimiter: Char = ',') : FileParser {
    override fun parse(content: String): ParseResult {
        return ParseResult(format = "CSV", data = content)
    }
}

// Registry-based Factory
object ParserFactory {
    private val registry = mutableMapOf<String, () -> FileParser>()

    init {
        // Регистрация стандартных парсеров
        register("json") { JsonParser() }
        register("xml") { XmlParser() }
        register("csv") { CsvParser() }
        register("tsv") { CsvParser(delimiter = '\t') }
    }

    fun register(extension: String, creator: () -> FileParser) {
        registry[extension.lowercase()] = creator
    }

    fun create(filename: String): FileParser {
        val extension = filename.substringAfterLast('.').lowercase()
        return registry[extension]?.invoke()
            ?: throw UnsupportedFormatException("No parser for .$extension")
    }

    fun supportedFormats(): Set<String> = registry.keys.toSet()
}

// Расширение --- без изменения фабрики
class YamlParser : FileParser {
    override fun parse(content: String) = ParseResult("YAML", content)
}

// Регистрация нового формата --- одна строка
ParserFactory.register("yaml") { YamlParser() }
ParserFactory.register("yml") { YamlParser() }

// Использование
val parser = ParserFactory.create("config.yaml")
val result = parser.parse(fileContent)
```

---

## Factory Method vs Abstract Factory: сводка

```
┌──────────────────────────────┬──────────────────────────────────────┐
│       Factory Method         │         Abstract Factory             │
├──────────────────────────────┼──────────────────────────────────────┤
│ Один метод создания          │ Несколько методов создания           │
│ Один тип продукта            │ Семейство связанных продуктов        │
│ Наследование (override)      │ Композиция (передаём фабрику)        │
│ Подкласс решает что создать  │ Фабрика создаёт согласованный набор  │
├──────────────────────────────┼──────────────────────────────────────┤
│ Kotlin: companion object,    │ Kotlin: interface с методами +       │
│ top-level fun, sealed + when │ sealed class для семейств             │
├──────────────────────────────┼──────────────────────────────────────┤
│ Пример: User.fromEmail()     │ Пример: UIFactory (Button+TextField) │
│ Пример: listOf(), mapOf()    │ Пример: тема приложения              │
└──────────────────────────────┴──────────────────────────────────────┘
```

---

## Проверь себя

> [!question]- В чём разница между Factory Method и Abstract Factory?
> **Factory Method** --- один метод, создающий один тип продукта. Подкласс или companion object решает, какой конкретный тип вернуть. Пример: `User.fromEmail()`. **Abstract Factory** --- интерфейс с несколькими методами, которые создают **семейство** связанных объектов. Пример: `UIFactory` создаёт согласованный набор Button + TextField + Dialog для одной темы. Abstract Factory гарантирует, что объекты из одного семейства не смешиваются с объектами из другого.

> [!question]- Почему `companion object` с factory methods лучше конструктора?
> (1) **Именованные** --- `User.fromEmail()` понятнее, чем `User(email)`. (2) **Могут возвращать подтипы** --- конструктор всегда возвращает свой тип. (3) **Могут кэшировать** --- вернуть существующий объект вместо нового. (4) **Могут возвращать null** --- `User.findById(id): User?` вместо исключения. (5) **Могут реализовывать интерфейсы** --- companion object реализует `UserFactory`.

> [!question]- Какие Kotlin-специфичные способы реализации фабрик вы знаете?
> (1) `companion object` с именованными фабричными методами. (2) `operator fun invoke()` для синтаксиса конструктора. (3) `sealed class` + `when` для типобезопасного выбора. (4) Extension functions (`"email".toUser()`). (5) Top-level functions (`listOf()`, `mapOf()`). (6) `inline fun <reified T>` для type-safe фабрик без передачи `Class<T>`.

> [!question]- Когда Factory --- антипаттерн?
> (1) Factory для единственного типа --- `UserFactory.create(name) = User(name)` просто оборачивает конструктор. (2) Factory Factory --- фабрика создаёт фабрику без реальной необходимости. (3) Factory вместо named parameters --- в Kotlin `data class` с default values заменяет Builder/Factory для простых случаев. Признак: если убрать фабрику и код станет проще --- фабрика была лишней.

> [!question]- Как `reified` generics связаны с Factory pattern?
> `inline fun <reified T>` сохраняет тип в runtime (обход type erasure JVM). Это позволяет создавать type-safe фабрики: `inline fun <reified T : ViewModel> viewModel(): T = ViewModelProvider(this)[T::class.java]`. Без reified пришлось бы передавать `Class<T>` параметром: `fun <T : ViewModel> viewModel(clazz: Class<T>): T`. Reified делает API чище и безопаснее.

---

## Ключевые карточки

Что такое Factory Method и какую проблему он решает?
?
Factory Method отделяет создание объекта от его использования. Клиент работает с интерфейсом Product, а конкретный тип определяется в factory method. Решает: tight coupling к конкретным классам, нарушение OCP (новый тип = изменение клиентского кода), дублирование логики создания. В Kotlin: `companion object` с именованными методами.

Чем Abstract Factory отличается от Factory Method?
?
Factory Method --- один метод, один тип продукта, использует наследование. Abstract Factory --- интерфейс с несколькими методами, создаёт **семейство** связанных продуктов, использует композицию. Пример FM: `User.fromEmail()`. Пример AF: `UIFactory` создаёт согласованный набор Button + TextField + Dialog. AF гарантирует, что компоненты из разных семейств не смешиваются.

Как `operator fun invoke()` работает как фабрика?
?
`operator fun invoke()` в companion object позволяет вызывать класс как функцию: `Color(255, 0, 0)` на самом деле вызывает `Color.Companion.invoke(255, 0, 0)`. Выглядит как конструктор, но это фабричный метод --- может валидировать, кэшировать, возвращать подтип. Предостережение: может сбивать с толку, если поведение сильно отличается от конструктора.

Какие фабричные функции есть в Kotlin stdlib?
?
Top-level: `listOf()`, `mutableListOf()`, `mapOf()`, `setOf()`, `sequenceOf()`, `buildList {}`, `buildMap {}`. Builder-style: `sequence { yield() }`, `flow { emit() }`. Все скрывают конкретные реализации: `listOf(1)` возвращает `SingletonList`, `listOf(1,2,3)` --- `ArrayList`, `emptyList()` --- singleton `EmptyList`.

Когда Factory оправдана, а когда нет?
?
Оправдана: тип определяется в runtime, создание сложное (валидация, зависимости), нужны именованные конструкторы, кэширование, тестирование. Не оправдана: один тип (Factory для `User(name)`), простой конструктор, named/default parameters достаточно. Антипаттерн: Factory ради Factory, Factory Factory, Factory вместо конструктора.

Что такое Registry-based Factory?
?
Расширяемая фабрика, где типы продуктов регистрируются в Map. Новый тип добавляется через `register("yaml") { YamlParser() }` --- без изменения кода фабрики (OCP). Фабрика по ключу находит creator и вызывает его. Примеры: парсеры файлов, обработчики событий, провайдеры платежей.

Как `sealed class` помогает в Factory pattern?
?
`sealed class` ограничивает набор продуктов на уровне компилятора. `when` по sealed class --- exhaustive: если добавить новый подтип, код не скомпилируется, пока не обработают все ветки. Идеально для фабрик с фиксированным набором типов: `PaymentProcessor.fromConfig(config)` с `when(config)` по sealed PaymentConfig.

Почему Москала рекомендует factory functions вместо конструкторов?
?
"Effective Kotlin" Item 30: factory functions (1) именованные --- `fromEmail()` понятнее `User(email)`, (2) не обязаны создавать новый объект --- кэширование, (3) могут возвращать подтип, (4) могут возвращать null вместо исключения. Те же аргументы, что у Блоха в "Effective Java" Item 1, но усилены Kotlin-фичами: companion object реализует интерфейсы, extension functions, reified generics.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Обзор | [[design-patterns-overview]] | Классификация паттернов, Kotlin-замены |
| Creational | [[singleton-pattern]] | `object` и `companion object` --- мост между Singleton и Factory |
| Creational | [[builder-pattern]] | Когда named params недостаточно: DSL-builders |
| Фундамент | [[solid-principles]] | OCP и DIP --- принципы, которые Factory реализует |
| Kotlin | [[kotlin-oop]] | `companion object`, `sealed class`, `operator fun` |
| Реальность | [[android-dependency-injection]] | Hilt/Koin --- DI как современная альтернатива фабрикам |
| Android | [[android-clean-architecture]] | Factory для создания объектов Domain layer |

---

## Источники

- Gamma E., Helm R., Johnson R., Vlissides J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software* --- оригинальные описания Factory Method и Abstract Factory
- Bloch J. (2018). *Effective Java*, 3rd ed. --- Item 1: Consider static factory methods instead of constructors
- Moskala M. (2021). *Effective Kotlin* --- Item 30: Consider factory functions instead of constructors; Item 32: Consider factory functions for complex object creation
- [Kotlin Docs: Object Declarations](https://kotlinlang.org/docs/object-declarations.html) --- companion object и именованные factory methods
- [Effective Kotlin: Factory Functions](https://kt.academy/article/ek-factory-functions) --- детальный разбор с примерами
- [Refactoring Guru: Factory Comparison](https://refactoring.guru/design-patterns/factory-comparison) --- визуальное сравнение Factory Method, Abstract Factory и Simple Factory
- [Baeldung: Abstract Factory Pattern in Kotlin](https://www.baeldung.com/kotlin/abstract-factory-pattern) --- реализация с Kotlin-примерами
- [Kotlin Static Factory Methods](https://asvid.github.io/kotlin-static-factory-methods) --- companion object, invoke, extension functions

---

*Проверено: 2026-02-19*
