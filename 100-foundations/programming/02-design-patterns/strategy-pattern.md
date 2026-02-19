---
title: "Strategy: взаимозаменяемые алгоритмы"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/design-patterns
  - topic/kotlin
  - pattern/behavioral
related:
  - "[[design-patterns-overview]]"
  - "[[observer-pattern]]"
  - "[[kotlin-functional]]"
  - "[[dry-kiss-yagni]]"
---

# Strategy: взаимозаменяемые алгоритмы

В GoF-каталоге Strategy --- это интерфейс + набор конкретных классов + контекст. В Kotlin **функциональный тип `(Input) -> Output`** и есть Strategy. Три класса превращаются в три лямбды, интерфейс --- в `typealias`, а контекст --- в функцию с параметром-функцией. Функции высшего порядка не убили Strategy: они **сделали его настолько естественным**, что он перестал выглядеть как паттерн.

---

## Проблема: алгоритм, вшитый намертво

Представь, что ты --- навигатор. Пользователь просит маршрут, а ты всегда строишь по кратчайшему расстоянию. Но один хочет избежать платных дорог, другой --- ехать быстрее, третий --- пешком. Ты вынужден разветвлять логику:

```kotlin
// ПЛОХО: алгоритм захардкожен
class Navigator {
    fun buildRoute(origin: Point, destination: Point, mode: String): Route {
        return when (mode) {
            "fastest"  -> buildFastestRoute(origin, destination)
            "shortest" -> buildShortestRoute(origin, destination)
            "cheapest" -> buildCheapestRoute(origin, destination)
            "walking"  -> buildWalkingRoute(origin, destination)
            "cycling"  -> buildCyclingRoute(origin, destination)
            else -> throw IllegalArgumentException("Unknown mode: $mode")
        }
    }

    // 5 приватных методов по 50-100 строк каждый
    // Добавление нового режима = изменение Navigator
    // Тестирование: нужно создавать Navigator для тестирования одного алгоритма
    private fun buildFastestRoute(o: Point, d: Point): Route { /* ... */ }
    private fun buildShortestRoute(o: Point, d: Point): Route { /* ... */ }
    private fun buildCheapestRoute(o: Point, d: Point): Route { /* ... */ }
    private fun buildWalkingRoute(o: Point, d: Point): Route { /* ... */ }
    private fun buildCyclingRoute(o: Point, d: Point): Route { /* ... */ }
}
```

**Три проблемы:**
1. **Нарушение Open/Closed** --- новый режим = изменение существующего кода
2. **God class** --- Navigator знает все алгоритмы маршрутизации
3. **Невозможность подмены** --- алгоритм выбирается строкой, не типом

---

## Классический Strategy: Java-style

```
+---------------------------------------------------------+
|                      STRATEGY                           |
+---------------------------------------------------------+
|   Context                      Strategy (interface)     |
|   +-- strategy: Strategy       +-- execute(data): R     |
|   +-- doWork() {                      |                 |
|         strategy.execute(data) +------+------+          |
|       }                   ConcreteA    ConcreteB        |
|                           execute()    execute()        |
+---------------------------------------------------------+
```

| Компонент | Роль | Без него |
|-----------|------|----------|
| **Strategy** | Интерфейс алгоритма | Нет взаимозаменяемости |
| **ConcreteStrategy** | Реализация одного алгоритма | Нечего подставлять |
| **Context** | Владеет стратегией, делегирует | Клиент привязан к конкретной стратегии |

### Java-style реализация в Kotlin (verbose)

```kotlin
// Интерфейс стратегии
interface RoutingStrategy {
    fun buildRoute(origin: Point, destination: Point): Route
}

// Конкретные стратегии --- каждая в своём классе
class FastestRouteStrategy : RoutingStrategy {
    override fun buildRoute(origin: Point, destination: Point): Route {
        // Алгоритм Дейкстры с весами = время
        return Route(/* ... */)
    }
}

class ShortestRouteStrategy : RoutingStrategy {
    override fun buildRoute(origin: Point, destination: Point): Route {
        // Алгоритм Дейкстры с весами = расстояние
        return Route(/* ... */)
    }
}

class CheapestRouteStrategy : RoutingStrategy {
    override fun buildRoute(origin: Point, destination: Point): Route {
        // Исключаем платные дороги
        return Route(/* ... */)
    }
}

// Context --- владеет стратегией
class Navigator(private val strategy: RoutingStrategy) {
    fun navigate(origin: Point, destination: Point): Route {
        return strategy.buildRoute(origin, destination)
    }
}

// Использование
val navigator = Navigator(FastestRouteStrategy())
val route = navigator.navigate(pointA, pointB)
```

**Итого:** 1 интерфейс + 3 класса + 1 Context = **5 файлов** для трёх алгоритмов.

---

## Kotlin заменяет Strategy функциональным типом

### Функциональный тип --- это и есть Strategy

```kotlin
// Вместо interface --- функциональный тип
typealias RoutingStrategy = (origin: Point, destination: Point) -> Route

// Вместо классов --- лямбды или функции
val fastestRoute: RoutingStrategy = { origin, destination ->
    // Алгоритм Дейкстры с весами = время
    Route(/* ... */)
}

val shortestRoute: RoutingStrategy = { origin, destination ->
    // Алгоритм Дейкстры с весами = расстояние
    Route(/* ... */)
}

val cheapestRoute: RoutingStrategy = { origin, destination ->
    // Исключаем платные дороги
    Route(/* ... */)
}

// Context --- функция с параметром-функцией
class Navigator(private val strategy: RoutingStrategy) {
    fun navigate(origin: Point, destination: Point): Route {
        return strategy(origin, destination)
    }
}

// Использование --- идентично
val navigator = Navigator(fastestRoute)
val route = navigator.navigate(pointA, pointB)

// Или inline:
val navigator2 = Navigator { origin, destination ->
    // Custom one-off алгоритм
    Route(/* ... */)
}
```

> [!info] Kotlin-нюанс
> `typealias RoutingStrategy = (Point, Point) -> Route` --- это не просто сахар. Это **полноценный тип** в системе типов Kotlin. Компилятор проверяет сигнатуру, IDE подсказывает параметры, и лямбда передаётся как first-class citizen.

### Сравнение: Java-style vs Kotlin-style

```
+-----------------------------------------------------------------+
|         Java-style Strategy    |   Kotlin functional Strategy   |
+-----------------------------------------------------------------+
|  interface RoutingStrategy {   |   typealias RoutingStrategy =  |
|    fun buildRoute(             |     (Point, Point) -> Route    |
|      o: Point, d: Point       |                                |
|    ): Route                    |   val fastest: RoutingStrategy |
|  }                             |     = { o, d -> Route(...) }   |
|                                |                                |
|  class FastestRoute :          |   val shortest: RoutingStrategy|
|    RoutingStrategy { ... }     |     = { o, d -> Route(...) }   |
|  class ShortestRoute :        |                                |
|    RoutingStrategy { ... }     |   val cheapest: RoutingStrategy|
|  class CheapestRoute :        |     = { o, d -> Route(...) }   |
|    RoutingStrategy { ... }     |                                |
|                                |                                |
|  1 interface + 3 classes       |   1 typealias + 3 lambdas     |
|  ~60 строк                    |   ~15 строк                    |
+-----------------------------------------------------------------+
```

### Function references вместо лямбд

```kotlin
// Если алгоритмы уже существуют как функции:
object RouteAlgorithms {
    fun fastest(origin: Point, destination: Point): Route { /* ... */ }
    fun shortest(origin: Point, destination: Point): Route { /* ... */ }
    fun cheapest(origin: Point, destination: Point): Route { /* ... */ }
}

// Function reference --- ссылка на функцию
val navigator = Navigator(RouteAlgorithms::fastest)
```

---

## Реальный пример: система ценообразования

### Задача: разные стратегии расчёта цены

```kotlin
// Модель
data class Order(
    val items: List<OrderItem>,
    val customerId: String,
    val promoCode: String? = null
)

data class OrderItem(
    val productId: String,
    val name: String,
    val price: Double,
    val quantity: Int
)

data class PricingResult(
    val subtotal: Double,
    val discount: Double,
    val total: Double,
    val appliedStrategy: String
)

// Strategy как typealias
typealias PricingStrategy = (Order) -> PricingResult

// Стратегии --- лямбды
val standardPricing: PricingStrategy = { order ->
    val subtotal = order.items.sumOf { it.price * it.quantity }
    PricingResult(subtotal, 0.0, subtotal, "standard")
}

val premiumPricing: PricingStrategy = { order ->
    val subtotal = order.items.sumOf { it.price * it.quantity }
    val discount = subtotal * 0.10  // 10% скидка
    PricingResult(subtotal, discount, subtotal - discount, "premium")
}

val wholesalePricing: PricingStrategy = { order ->
    val subtotal = order.items.sumOf { it.price * it.quantity }
    val discount = when {
        subtotal > 10_000 -> subtotal * 0.25
        subtotal > 5_000  -> subtotal * 0.15
        subtotal > 1_000  -> subtotal * 0.10
        else              -> 0.0
    }
    PricingResult(subtotal, discount, subtotal - discount, "wholesale")
}

// Context
class PriceCalculator(private val strategy: PricingStrategy) {
    fun calculate(order: Order): PricingResult = strategy(order)

    // Можно менять стратегию в runtime
    fun withStrategy(newStrategy: PricingStrategy) = PriceCalculator(newStrategy)
}

// Использование
val calculator = PriceCalculator(standardPricing)
val result = calculator.calculate(order)

// Смена стратегии в runtime --- бизнес-правило
val customerStrategy = when (customerType) {
    CustomerType.REGULAR  -> standardPricing
    CustomerType.PREMIUM  -> premiumPricing
    CustomerType.WHOLESALE -> wholesalePricing
}
val finalPrice = PriceCalculator(customerStrategy).calculate(order)
```

### Композиция стратегий

```kotlin
// Стратегии можно комбинировать!
fun combinedPricing(vararg strategies: PricingStrategy): PricingStrategy = { order ->
    val subtotal = order.items.sumOf { it.price * it.quantity }
    var totalDiscount = 0.0

    for (strategy in strategies) {
        val result = strategy(order)
        totalDiscount += result.discount
    }

    PricingResult(subtotal, totalDiscount, subtotal - totalDiscount, "combined")
}

// Black Friday: premium скидка + дополнительная 5%
val blackFridayExtra: PricingStrategy = { order ->
    val subtotal = order.items.sumOf { it.price * it.quantity }
    PricingResult(subtotal, subtotal * 0.05, subtotal * 0.95, "black-friday")
}

val blackFridayPremium = combinedPricing(premiumPricing, blackFridayExtra)
val promo = PriceCalculator(blackFridayPremium).calculate(order)
```

---

## Kotlin Collections --- Strategy "из коробки"

Стандартная библиотека Kotlin --- это Strategy pattern повсюду. Каждый раз, когда ты передаёшь лямбду в `sortedBy`, `filter`, `groupBy`, `fold` --- ты используешь Strategy:

```kotlin
data class Product(
    val name: String,
    val price: Double,
    val rating: Double,
    val salesCount: Int
)

val products: List<Product> = loadProducts()

// sortedBy --- стратегия сортировки
val byPrice = products.sortedBy { it.price }
val byRating = products.sortedByDescending { it.rating }
val bySales = products.sortedByDescending { it.salesCount }

// filter --- стратегия фильтрации
val cheap = products.filter { it.price < 100.0 }
val popular = products.filter { it.salesCount > 1000 }
val topRated = products.filter { it.rating >= 4.5 }

// groupBy --- стратегия группировки
val byPriceRange = products.groupBy { product ->
    when {
        product.price < 50   -> "budget"
        product.price < 200  -> "mid-range"
        else                 -> "premium"
    }
}

// Comparator<T> --- это буквально Strategy interface из GoF
val customComparator = compareBy<Product> { it.rating }
    .thenByDescending { it.salesCount }
    .thenBy { it.price }

val sorted = products.sortedWith(customComparator)
```

> [!info] Kotlin-нюанс
> `Comparator<T>` --- это единственный оставшийся "классический" Strategy interface в stdlib. Но даже он используется через лямбды: `compareBy { it.price }` создаёт `Comparator` из лямбды. GoF Strategy превратился в одну строку.

---

## Когда Strategy-интерфейс ВСЁ-ТАКИ нужен

Функциональный тип не покрывает все сценарии. Интерфейс оправдан когда:

### 1. Стратегия имеет состояние

```kotlin
// Стратегия с состоянием --- лямбда не подходит
interface RetryStrategy {
    fun shouldRetry(attempt: Int, error: Throwable): Boolean
    fun delayMillis(attempt: Int): Long
    fun reset()
}

class ExponentialBackoff(
    private val maxAttempts: Int = 3,
    private val baseDelay: Long = 1000
) : RetryStrategy {
    private var totalRetries = 0

    override fun shouldRetry(attempt: Int, error: Throwable): Boolean {
        return attempt < maxAttempts && error !is FatalException
    }

    override fun delayMillis(attempt: Int): Long {
        return baseDelay * (1L shl attempt)  // 1s, 2s, 4s, 8s...
    }

    override fun reset() {
        totalRetries = 0
    }
}

class LinearBackoff(private val delay: Long = 2000) : RetryStrategy {
    override fun shouldRetry(attempt: Int, error: Throwable) = attempt < 5
    override fun delayMillis(attempt: Int) = delay * attempt
    override fun reset() {}
}
```

**Почему не лямбда:** стратегия состоит из трёх связанных методов + имеет mutable state. Один функциональный тип не выразит эту связность.

### 2. Стратегия группирует несколько функций

```kotlin
// Стратегия сериализации --- несколько связанных операций
interface SerializationStrategy<T> {
    fun serialize(value: T): ByteArray
    fun deserialize(bytes: ByteArray): T
    val contentType: String
}

class JsonStrategy<T>(private val clazz: Class<T>) : SerializationStrategy<T> {
    private val mapper = ObjectMapper()

    override fun serialize(value: T): ByteArray = mapper.writeValueAsBytes(value)
    override fun deserialize(bytes: ByteArray): T = mapper.readValue(bytes, clazz)
    override val contentType = "application/json"
}

class ProtobufStrategy<T : Message>(
    private val parser: Parser<T>
) : SerializationStrategy<T> {
    override fun serialize(value: T): ByteArray = value.toByteArray()
    override fun deserialize(bytes: ByteArray): T = parser.parseFrom(bytes)
    override val contentType = "application/protobuf"
}
```

### 3. DI-контейнер инжектирует стратегию

```kotlin
// Hilt/Dagger --- нужен интерфейс для binding
interface AnalyticsStrategy {
    fun trackEvent(name: String, params: Map<String, Any>)
}

class FirebaseAnalytics @Inject constructor() : AnalyticsStrategy {
    override fun trackEvent(name: String, params: Map<String, Any>) {
        Firebase.analytics.logEvent(name) {
            params.forEach { (k, v) -> param(k, v.toString()) }
        }
    }
}

class MixpanelAnalytics @Inject constructor() : AnalyticsStrategy {
    override fun trackEvent(name: String, params: Map<String, Any>) {
        mixpanel.track(name, JSONObject(params))
    }
}

// Module --- Hilt нужен интерфейс для binding
@Module
@InstallIn(SingletonComponent::class)
abstract class AnalyticsModule {
    @Binds
    abstract fun bindAnalytics(impl: FirebaseAnalytics): AnalyticsStrategy
}
```

### Дерево решений: интерфейс или функциональный тип?

```
Стратегия --- это ОДИН метод без состояния?
+-- ДА --> typealias + lambda
|         typealias Pricing = (Order) -> Price
|
+-- НЕТ, несколько связанных методов?
|   +-- ДА --> interface
|             interface Serializer<T> { serialize(); deserialize() }
|
+-- НЕТ, есть mutable state?
|   +-- ДА --> interface или class
|
+-- Нужна инжекция через DI?
    +-- ДА --> interface (Hilt/Dagger/Koin binding)
```

---

## Real-world Strategy

### OkHttp `Interceptor` --- Strategy для HTTP

```kotlin
// OkHttp Interceptor --- это Strategy interface
// Каждый Interceptor --- стратегия обработки запроса/ответа

class AuthInterceptor(private val tokenProvider: () -> String) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer ${tokenProvider()}")
            .build()
        return chain.proceed(request)
    }
}

class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        println("--> ${request.method} ${request.url}")

        val response = chain.proceed(request)
        println("<-- ${response.code} (${response.body?.contentLength()} bytes)")

        return response
    }
}

class CacheInterceptor(private val maxAge: Int = 60) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val response = chain.proceed(chain.request())
        return response.newBuilder()
            .header("Cache-Control", "max-age=$maxAge")
            .build()
    }
}

// Context: OkHttpClient комбинирует стратегии
val client = OkHttpClient.Builder()
    .addInterceptor(AuthInterceptor { getToken() })
    .addInterceptor(LoggingInterceptor())
    .addNetworkInterceptor(CacheInterceptor(300))
    .build()
```

### Ktor Plugins --- Strategy через лямбды

```kotlin
// Ktor plugin --- Strategy, настроенная через DSL
install(ContentNegotiation) {
    json(Json {
        prettyPrint = true
        ignoreUnknownKeys = true
    })
}

// Стратегия авторизации
install(Authentication) {
    jwt("auth-jwt") {
        verifier(JwtConfig.verifier)
        validate { credential ->
            if (credential.payload.audience.contains("my-audience"))
                JWTPrincipal(credential.payload)
            else null
        }
    }
}
```

### Стратегия валидации

```kotlin
// Простой пример: валидация через function type
typealias Validator<T> = (T) -> ValidationResult

sealed class ValidationResult {
    data object Valid : ValidationResult()
    data class Invalid(val errors: List<String>) : ValidationResult()
}

// Валидаторы --- лямбды
val emailValidator: Validator<String> = { email ->
    when {
        email.isBlank() -> ValidationResult.Invalid(listOf("Email is required"))
        !email.contains("@") -> ValidationResult.Invalid(listOf("Invalid email format"))
        else -> ValidationResult.Valid
    }
}

val passwordValidator: Validator<String> = { password ->
    val errors = mutableListOf<String>()
    if (password.length < 8) errors += "Password must be at least 8 characters"
    if (!password.any { it.isUpperCase() }) errors += "Must contain uppercase letter"
    if (!password.any { it.isDigit() }) errors += "Must contain digit"

    if (errors.isEmpty()) ValidationResult.Valid
    else ValidationResult.Invalid(errors)
}

// Композиция валидаторов
fun <T> compose(vararg validators: Validator<T>): Validator<T> = { value ->
    val allErrors = validators.flatMap { validator ->
        when (val result = validator(value)) {
            is ValidationResult.Valid -> emptyList()
            is ValidationResult.Invalid -> result.errors
        }
    }
    if (allErrors.isEmpty()) ValidationResult.Valid
    else ValidationResult.Invalid(allErrors)
}
```

---

## Anti-patterns

### 1. Strategy для единственного алгоритма

```kotlin
// ПЛОХО: один ConcreteStrategy --- зачем абстракция?
interface SortStrategy {
    fun <T : Comparable<T>> sort(list: List<T>): List<T>
}

class QuickSortStrategy : SortStrategy {
    override fun <T : Comparable<T>> sort(list: List<T>) = list.sorted()
}

class Sorter(private val strategy: SortStrategy) {
    fun <T : Comparable<T>> sort(list: List<T>) = strategy.sort(list)
}

// ХОРОШО: просто функция
fun <T : Comparable<T>> sort(list: List<T>): List<T> = list.sorted()
```

### 2. Over-abstraction: Strategy + Factory + DI

```kotlin
// ПЛОХО: три уровня абстракции для простой задачи
interface StringFormatter { fun format(s: String): String }
class UpperCaseFormatter : StringFormatter { /* ... */ }
class LowerCaseFormatter : StringFormatter { /* ... */ }
class FormatterFactory { fun create(type: String): StringFormatter { /* ... */ } }

// ХОРОШО: просто передай лямбду
fun processText(text: String, format: (String) -> String = { it }): String {
    return format(text)
}

processText("hello", String::uppercase)
processText("HELLO", String::lowercase)
```

### 3. Стратегия, которая никогда не меняется

```kotlin
// ПЛОХО: Strategy для статического поведения
class TaxCalculator(private val strategy: TaxStrategy) {
    fun calculate(amount: Double) = strategy.calculate(amount)
}
// Если налоговая ставка всегда 20% --- Strategy не нужна

// ХОРОШО: если ставка зависит от страны --- Strategy оправдана
typealias TaxStrategy = (amount: Double) -> Double

val usTax: TaxStrategy = { it * 0.0725 }     // 7.25%
val ukVat: TaxStrategy = { it * 0.20 }       // 20%
val germanVat: TaxStrategy = { it * 0.19 }   // 19%
```

---

## Подводные камни

### Pitfall 1: Lambda capture и утечки

```kotlin
// Осторожно с захватом контекста
class Activity {
    private val heavy = HeavyResource()

    fun createStrategy(): PricingStrategy {
        // Лямбда захватывает this (Activity) --- heavy не соберётся GC
        return { order -> heavy.calculate(order) }
    }
}

// Решение: передавай только нужные данные
fun createStrategy(calculator: Calculator): PricingStrategy {
    return { order -> calculator.calculate(order) }
}
```

### Pitfall 2: Потеря читаемости при сложных лямбдах

```kotlin
// ПЛОХО: лямбда на 30 строк --- нечитаемо
val strategy: PricingStrategy = { order ->
    val subtotal = order.items.sumOf { it.price * it.quantity }
    val memberDiscount = if (order.isMember) 0.1 else 0.0
    val volumeDiscount = when {
        order.items.size > 50 -> 0.15
        order.items.size > 20 -> 0.10
        order.items.size > 10 -> 0.05
        else -> 0.0
    }
    // ... ещё 20 строк
    PricingResult(/* ... */)
}

// ХОРОШО: выноси сложную логику в именованную функцию
fun wholesalePricing(order: Order): PricingResult {
    val subtotal = order.items.sumOf { it.price * it.quantity }
    val memberDiscount = calculateMemberDiscount(order)
    val volumeDiscount = calculateVolumeDiscount(order)
    // ...
    return PricingResult(/* ... */)
}

// Используй function reference
val calculator = PriceCalculator(::wholesalePricing)
```

---

## Проверь себя

> [!question]- Почему в Kotlin функциональный тип `(Input) -> Output` заменяет Strategy interface?
> Потому что функция в Kotlin --- first-class citizen. Функциональный тип `(Input) -> Output` определяет контракт (входные и выходные данные), лямбда --- конкретную реализацию, а передача функции как параметра --- подмену алгоритма в runtime. Это те же три роли (Strategy, ConcreteStrategy, Context), но без boilerplate интерфейсов и классов.

> [!question]- Когда лямбда НЕ подходит для Strategy и нужен интерфейс?
> Три случая: (1) стратегия группирует несколько связанных методов (serialize + deserialize); (2) стратегия имеет mutable state (retry counter, backoff state); (3) DI-контейнер (Hilt/Dagger) требует интерфейс для binding. Правило: если стратегия --- один stateless метод, используй лямбду; иначе --- интерфейс.

> [!question]- Как `Comparator<T>` в Kotlin stdlib реализует Strategy pattern?
> `Comparator<T>` --- классический Strategy interface с одним методом `compare(a: T, b: T): Int`. Конкретные стратегии создаются через `compareBy { it.price }`, `compareByDescending { it.rating }`. Context --- функции `sortedWith(comparator)`, `sortedBy {}`. Но благодаря SAM-conversion и `compareBy {}`, интерфейс используется как лямбда.

> [!question]- Что такое `typealias` для функционального типа и когда его использовать?
> `typealias PricingStrategy = (Order) -> PricingResult` --- даёт имя функциональному типу. Это не новый тип (нет type safety), а псевдоним для читаемости. Используй когда функциональный тип передаётся в нескольких местах и сигнатура длинная. Не используй для тривиальных типов вроде `(Int) -> Boolean`.

---

## Ключевые карточки

Чем функциональная Strategy в Kotlin отличается от классической GoF Strategy?
?
GoF: interface + N классов + Context. Kotlin: `typealias` + N лямбд/function references + функция с параметром-функцией. Те же три роли (абстракция, реализация, контекст), но без boilerplate. 1 interface + 3 класса (~60 строк) = 1 typealias + 3 лямбды (~15 строк).

Что такое typealias для Strategy и чем он НЕ является?
?
`typealias PricingStrategy = (Order) -> PricingResult` --- псевдоним для функционального типа. Улучшает читаемость. НЕ является новым типом: `PricingStrategy` и `(Order) -> PricingResult` --- одно и то же для компилятора. Нет type safety между разными typealias с одинаковой сигнатурой.

Как stdlib Kotlin использует Strategy "из коробки"?
?
`sortedBy {}` --- стратегия сортировки. `filter {}` --- стратегия фильтрации. `groupBy {}` --- стратегия группировки. `fold {}` --- стратегия агрегации. Каждый раз, когда передаёшь лямбду в collection-функцию, используешь Strategy. `Comparator<T>` --- единственный оставшийся "классический" Strategy interface.

Когда Strategy-interface нужен вместо лямбды?
?
1) Стратегия группирует несколько связанных методов (serialize + deserialize). 2) Стратегия имеет mutable state (retry counter). 3) DI-контейнер (Hilt/Dagger) требует интерфейс. Правило: один stateless метод = лямбда, всё остальное = interface.

Как композировать функциональные стратегии?
?
Стратегии-функции можно комбинировать как обычные функции: `fun combine(vararg strategies: PricingStrategy): PricingStrategy = { order -> strategies.fold(initialResult) { acc, s -> s(order) } }`. Это невозможно с классическими GoF стратегиями без дополнительного кода.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Фундамент | [[design-patterns-overview]] | Обзор всех GoF паттернов |
| Связанный паттерн | [[observer-pattern]] | Observer --- реакция на события, Strategy --- выбор алгоритма |
| Kotlin-возможности | [[kotlin-functional]] | HOF, lambdas, function types --- основа для functional Strategy |
| Принципы | [[dry-kiss-yagni]] | Не создавай Strategy для одного алгоритма (YAGNI) |
| Android | [[android-architecture-patterns]] | Strategy в выборе архитектурных подходов |
| Обзор | [[design-patterns-overview]] | Вернуться к карте раздела Design Patterns |

---

## Источники

- Gamma E. et al. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software* --- оригинальное описание Strategy pattern в GoF каталоге
- Moskala M. (2022). *Effective Kotlin*, Item 46: "Use function types instead of interfaces for functional contracts" --- предпочтение функциональных типов в Kotlin
- Nystrom R. (2014). *Game Programming Patterns*, Chapter "Strategy" --- отличное объяснение Strategy с примерами из геймдева
- [A Functional Programming Alternative to the Strategy Pattern (Expedia)](https://medium.com/expedia-group-tech/a-functional-programming-alternative-to-the-strategy-pattern-73268b68868a) --- замена Strategy функциональным подходом
- [Function Types and the Strategy Pattern (VerboseMode)](https://verbosemode.dev/p/function-types-and-the-strategy-pattern) --- Strategy через function types в Kotlin
- [Strategy Pattern in Kotlin (asvid.github.io)](https://asvid.github.io/kotlin-strategy-pattern) --- сравнение классического и функционального подходов
- [Kotlin Documentation: Higher-order functions and lambdas](https://kotlinlang.org/docs/lambdas.html) --- официальная документация по HOF
- [Interfaces as Method Parameters and Higher Order Functions (Baeldung)](https://www.baeldung.com/kotlin/interfaces-higher-order-functions) --- когда interface, когда лямбда

---

*Проверено: 2026-02-19*
