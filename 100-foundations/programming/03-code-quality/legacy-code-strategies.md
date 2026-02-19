---
title: "Legacy Code: стратегии работы с унаследованным кодом"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/refactoring
  - topic/kotlin
related:
  - "[[code-smells]]"
  - "[[refactoring-catalog]]"
  - "[[clean-code]]"
  - "[[kotlin-interop]]"
---

# Legacy Code: стратегии работы с унаследованным кодом

"Legacy code --- код без тестов." Не возраст делает код legacy, а отсутствие safety net. Код, написанный вчера без тестов --- уже legacy. Код десятилетней давности с хорошим покрытием --- просто код. Это определение Майкла Фезерса из "Working Effectively with Legacy Code", и оно меняет отношение к проблеме: задача не "переписать", а "покрыть тестами и постепенно улучшить".

Kotlin добавляет уникальное измерение: благодаря 100% совместимости с Java можно мигрировать файл за файлом, не останавливая разработку. `@JvmStatic`, `@JvmOverloads`, extension-функции как Sprout Methods, typealias для плавного перехода --- инструменты, которых нет в других языках.

---

## Что делает код legacy

```
┌──────────────────────────────────────────────────────────────────────┐
│                    LEGACY CODE ≠ СТАРЫЙ КОД                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Legacy:                          Не legacy:                         │
│  ────────                         ──────────                         │
│  □ Нет тестов                     □ Покрыт тестами                  │
│  □ Никто не понимает              □ Есть документация               │
│  □ Страшно менять                 □ Изменения безопасны             │
│  □ "Не трогай — оно работает"    □ "Рефакторим по ходу"            │
│                                                                      │
│  Возраст кода:  ← НЕ КРИТЕРИЙ →                                    │
│                                                                      │
│  Вчерашний код без тестов = legacy                                  │
│  10-летний код с тестами = просто код                               │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Алгоритм работы с legacy (Feathers' Legacy Code Change Algorithm)

```
1. Определить точки изменения      (что менять?)
2. Найти точки тестирования        (что проверять?)
3. Разорвать зависимости           (seams)
4. Написать тесты                  (characterization tests)
5. Сделать изменение + рефакторинг (под защитой тестов)
```

---

## Characterization Tests: фиксация текущего поведения

Цель --- не протестировать "правильность", а **зафиксировать факт**: что код делает сейчас. Даже если поведение неправильное --- сначала фиксируем, потом (отдельным шагом) исправляем.

### Методика

1. Вызвать код с конкретным входом.
2. Посмотреть на результат.
3. Записать результат как expected.
4. Повторить для граничных случаев.

```kotlin
// Legacy-код: никто не знает все правила скидок
class LegacyOrderCalculator {
    fun calculate(items: List<Map<String, Any>>, customerType: String, date: LocalDate): Double {
        var total = 0.0
        for (item in items) {
            val price = item["price"] as Double
            total += if (customerType == "VIP") price * 0.8 else price
        }
        if (date.monthValue == 12) {
            total *= 0.9
        }
        return total
    }
}
```

```kotlin
// Characterization tests — фиксируем текущее поведение
class LegacyOrderCalculatorTest {
    private val calculator = LegacyOrderCalculator()

    @Test
    fun `regular customer single item`() {
        val items = listOf(mapOf("price" to 100.0))
        val result = calculator.calculate(items, "regular", LocalDate.of(2025, 6, 15))
        assertEquals(100.0, result, 0.01) // Зафиксировали!
    }

    @Test
    fun `VIP customer gets 20 percent discount`() {
        val items = listOf(mapOf("price" to 100.0))
        val result = calculator.calculate(items, "VIP", LocalDate.of(2025, 6, 15))
        assertEquals(80.0, result, 0.01) // 100 * 0.8 = 80
    }

    @Test
    fun `december gives additional 10 percent discount`() {
        val items = listOf(mapOf("price" to 100.0))
        val result = calculator.calculate(items, "regular", LocalDate.of(2025, 12, 15))
        assertEquals(90.0, result, 0.01) // 100 * 0.9 = 90
    }

    @Test
    fun `VIP in december — discounts stack multiplicatively`() {
        val items = listOf(mapOf("price" to 100.0))
        val result = calculator.calculate(items, "VIP", LocalDate.of(2025, 12, 15))
        // 100 * 0.8 = 80, 80 * 0.9 = 72 — скидки складываются!
        assertEquals(72.0, result, 0.01)
    }

    @Test
    fun `empty items returns zero`() {
        val result = calculator.calculate(emptyList(), "regular", LocalDate.of(2025, 6, 15))
        assertEquals(0.0, result, 0.01)
    }

    @Test
    fun `multiple items summed`() {
        val items = listOf(
            mapOf("price" to 50.0),
            mapOf("price" to 30.0)
        )
        val result = calculator.calculate(items, "regular", LocalDate.of(2025, 6, 15))
        assertEquals(80.0, result, 0.01) // 50 + 30
    }
}
```

> [!info] Kotlin-нюанс
> JUnit 5 в Kotlin позволяет использовать backtick-имена тестов: `` `VIP in december — discounts stack` ``. Это делает characterization tests самодокументирующимися --- имя теста описывает обнаруженное поведение.

---

## Seams: точки, где можно изменить поведение без редактирования

Seam (шов) --- место, где можно подменить поведение, не меняя сам код. Три типа:

### Object Seam (самый частый)

Подмена зависимости через конструктор или интерфейс.

```kotlin
// Legacy: жёстко привязан к реальному сервису
class OrderService {
    private val emailSender = SmtpEmailSender()  // ← нет шва!

    fun placeOrder(order: Order) {
        // ... бизнес-логика ...
        emailSender.send(order.customer.email, "Order confirmed")
    }
}
```

```kotlin
// С Object Seam: зависимость через конструктор
interface EmailSender {
    fun send(to: String, message: String)
}

class OrderService(
    private val emailSender: EmailSender  // ← seam!
) {
    fun placeOrder(order: Order) {
        // ... бизнес-логика ...
        emailSender.send(order.customer.email, "Order confirmed")
    }
}

// Тест: подмена через MockK
@Test
fun `placeOrder sends confirmation email`() {
    val mockSender = mockk<EmailSender>(relaxed = true)
    val service = OrderService(mockSender)

    service.placeOrder(testOrder)

    verify { mockSender.send("test@example.com", "Order confirmed") }
}
```

### Link Seam (Dependency Injection)

Зависимость определяется на уровне конфигурации, не кода.

```kotlin
// Через Koin (DI-фреймворк для Kotlin)
val productionModule = module {
    single<EmailSender> { SmtpEmailSender() }
    single { OrderService(get()) }
}

val testModule = module {
    single<EmailSender> { FakeEmailSender() }
    single { OrderService(get()) }
}
```

### Preprocessing Seam (Feature Flags)

```kotlin
class PaymentProcessor(
    private val featureFlags: FeatureFlags
) {
    fun processPayment(order: Order): PaymentResult {
        return if (featureFlags.isEnabled("new-payment-flow")) {
            newPaymentFlow(order)      // новый код
        } else {
            legacyPaymentFlow(order)   // старый код
        }
    }

    private fun newPaymentFlow(order: Order): PaymentResult = TODO()
    private fun legacyPaymentFlow(order: Order): PaymentResult = TODO()
}
```

> [!info] Kotlin-нюанс
> Constructor injection --- самый чистый Object Seam. Kotlin `interface` + конструктор с параметрами делают это тривиальным. В Java для этого часто нужен DI-фреймворк; в Kotlin достаточно языка.

---

## Sprout Method / Sprout Class

Нужно добавить новую функциональность в legacy-код, который страшно менять. Стратегия: написать новый код отдельно, полностью покрыть тестами, вызвать из legacy.

### Sprout Method

```kotlin
// Legacy: 500 строк спагетти-кода
class LegacyReportGenerator {
    fun generate(data: List<Map<String, Any>>): List<ReportRow> {
        // ... 500 строк необъяснимой логики ...
        val result = mutableListOf<ReportRow>()
        for (item in data) {
            // complex processing...
            result.add(processedRow)
        }
        return result
    }
}
```

```kotlin
// Sprout Method: новая логика в новом методе (тестируемом!)
class LegacyReportGenerator {
    fun generate(data: List<Map<String, Any>>): List<ReportRow> {
        val validatedData = validateData(data)  // NEW: sprout method
        // ... 500 строк оригинальной логики (не трогаем!) ...
        val result = mutableListOf<ReportRow>()
        for (item in validatedData) {
            // complex processing...
            result.add(processedRow)
        }
        return result
    }

    // Новый код — чистый и тестируемый
    internal fun validateData(data: List<Map<String, Any>>): List<Map<String, Any>> =
        data.filter { item ->
            val value = item["value"]
            value != null && (value as? Number)?.toDouble()?.let { it >= 0 } == true
        }
}

// Тест только для нового кода
@Test
fun `validateData filters negative values`() {
    val generator = LegacyReportGenerator()
    val data = listOf(
        mapOf("value" to 10.0),
        mapOf("value" to -5.0),
        mapOf("value" to null),
        mapOf("name" to "no value")
    )
    val result = generator.validateData(data)
    assertEquals(1, result.size)
    assertEquals(10.0, result[0]["value"])
}
```

### Sprout Method через Extension Function

```kotlin
// Extension как Sprout Method — не трогаем класс вообще!
fun LegacyReportGenerator.generateWithValidation(
    data: List<Map<String, Any>>
): List<ReportRow> {
    val validatedData = data.filter { item ->
        val value = item["value"]
        value != null && (value as? Number)?.toDouble()?.let { it >= 0 } == true
    }
    return generate(validatedData)  // вызываем legacy
}

// Использование: постепенно переходим на новый вызов
val report = generator.generateWithValidation(rawData)
```

> [!info] Kotlin-нюанс
> Extension-функция как Sprout Method --- уникальная возможность Kotlin. Добавляем поведение к legacy-классу, **не открывая его файл**. Новый код живёт в отдельном файле, полностью покрыт тестами.

### Sprout Class

Когда новая логика слишком сложна для одного метода.

```kotlin
// Sprout Class: полноценный новый класс
class DataValidator {
    fun validate(data: List<Map<String, Any>>): ValidationResult {
        val valid = mutableListOf<Map<String, Any>>()
        val errors = mutableListOf<ValidationError>()

        for ((index, item) in data.withIndex()) {
            val value = item["value"]
            when {
                value == null -> errors.add(ValidationError(index, "Missing value"))
                value !is Number -> errors.add(ValidationError(index, "Non-numeric value"))
                value.toDouble() < 0 -> errors.add(ValidationError(index, "Negative value"))
                else -> valid.add(item)
            }
        }

        return ValidationResult(valid, errors)
    }
}

data class ValidationResult(
    val validItems: List<Map<String, Any>>,
    val errors: List<ValidationError>
)

data class ValidationError(val index: Int, val message: String)

// Legacy вызывает Sprout Class
class LegacyReportGenerator(
    private val validator: DataValidator = DataValidator()
) {
    fun generate(data: List<Map<String, Any>>): List<ReportRow> {
        val result = validator.validate(data)
        if (result.errors.isNotEmpty()) {
            log.warn("Validation errors: ${result.errors}")
        }
        // ... оригинальная логика с result.validItems ...
    }
}
```

---

## Wrap Method

Нужно добавить логику до/после legacy-вызова, не меняя его.

```kotlin
// Legacy: метод, к которому нужно добавить логирование
class LegacyPaymentProcessor {
    fun processPayment(amount: BigDecimal, cardToken: String): Boolean {
        // ... 200 строк legacy логики ...
        return true
    }
}
```

```kotlin
// Wrap Method: оборачиваем с pre/post логикой
class MonitoredPaymentProcessor(
    private val legacy: LegacyPaymentProcessor,
    private val metrics: MetricsCollector,
    private val logger: Logger
) {
    fun processPayment(amount: BigDecimal, cardToken: String): Boolean {
        val startTime = System.currentTimeMillis()
        logger.info("Payment started: amount=$amount")

        val result = legacy.processPayment(amount, cardToken)  // legacy вызов

        val duration = System.currentTimeMillis() - startTime
        metrics.recordPaymentDuration(duration)
        logger.info("Payment completed: success=$result, duration=${duration}ms")

        return result
    }
}
```

```kotlin
// Kotlin-идиома: higher-order function для wrapping
inline fun <T> withMetrics(
    metrics: MetricsCollector,
    operation: String,
    block: () -> T
): T {
    val start = System.currentTimeMillis()
    return try {
        block().also {
            metrics.recordSuccess(operation, System.currentTimeMillis() - start)
        }
    } catch (e: Exception) {
        metrics.recordFailure(operation, System.currentTimeMillis() - start)
        throw e
    }
}

// Использование
fun processPayment(amount: BigDecimal, cardToken: String): Boolean =
    withMetrics(metrics, "payment") {
        legacy.processPayment(amount, cardToken)
    }
```

> [!info] Kotlin-нюанс
> Higher-order функции + `inline` --- Wrap Method без оверхеда. `inline fun` инлайнится в байткоде, нет создания лямбда-объекта. Это идеальный инструмент для cross-cutting concerns (логирование, метрики, retry) вокруг legacy.

---

## Strangler Fig Pattern: постепенная замена

Паттерн придуман Мартином Фаулером по аналогии с фикусом-душителем: новый код растёт вокруг старого, постепенно замещая его.

```
┌──────────────────────────────────────────────────────────────────────┐
│                      STRANGLER FIG PATTERN                          │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Этап 1: Старая система, новый фасад                                │
│  ┌──────────┐     ┌───────────────┐     ┌──────────────────┐       │
│  │  Client   │────▶│  Router/Facade │────▶│  Legacy System   │       │
│  └──────────┘     └───────────────┘     └──────────────────┘       │
│                                                                      │
│  Этап 2: Часть запросов → новая система                             │
│  ┌──────────┐     ┌───────────────┐──── ▶┌──────────────────┐      │
│  │  Client   │────▶│  Router/Facade │     │  Legacy System   │      │
│  └──────────┘     └───┬───────────┘     └──────────────────┘       │
│                        │                                             │
│                        └──── ▶┌──────────────────┐                  │
│                               │  New System (20%) │                  │
│                               └──────────────────┘                  │
│                                                                      │
│  Этап 3: Новая система обрабатывает всё, legacy удалён              │
│  ┌──────────┐     ┌───────────────┐     ┌──────────────────┐       │
│  │  Client   │────▶│  Router/Facade │────▶│  New System      │       │
│  └──────────┘     └───────────────┘     └──────────────────┘       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

```kotlin
// Router направляет запросы на legacy или новый код
interface OrderService {
    fun getOrder(id: String): Order
    fun placeOrder(request: OrderRequest): OrderResult
}

class StranglerOrderService(
    private val legacy: LegacyOrderService,
    private val modern: ModernOrderService,
    private val featureFlags: FeatureFlags
) : OrderService {

    override fun getOrder(id: String): Order =
        if (featureFlags.isEnabled("modern-get-order")) {
            modern.getOrder(id)
        } else {
            legacy.getOrder(id)
        }

    override fun placeOrder(request: OrderRequest): OrderResult =
        if (featureFlags.isEnabled("modern-place-order")) {
            modern.placeOrder(request)
        } else {
            legacy.placeOrder(request)
        }
}
```

---

## Kotlin-специфичные стратегии миграции Java → Kotlin

### Пофайловая конвертация

```
Стратегия: конвертируем по одному файлу, начиная с листьев графа зависимостей.

1. Выбрать файл без зависимых (или с минимумом)
2. IntelliJ: Ctrl+Alt+Shift+K (Convert Java to Kotlin)
3. Ручная доработка: nullability, data class, идиомы
4. Запустить тесты
5. Коммит
6. Повторить
```

### Аннотации для плавного перехода

```kotlin
// @JvmStatic — статический метод для вызова из Java
class UserRepository {
    companion object {
        @JvmStatic
        fun create(database: Database): UserRepository =
            UserRepository(database)
    }

    // Java: UserRepository.create(db)
    // Kotlin: UserRepository.create(db) или UserRepository(db)
}
```

```kotlin
// @JvmOverloads — генерирует overloads для Java
class NotificationBuilder @JvmOverloads constructor(
    val title: String,
    val message: String,
    val priority: Priority = Priority.NORMAL,
    val channel: String = "default"
) {
    // Java видит 4 конструктора:
    // NotificationBuilder(title, message, priority, channel)
    // NotificationBuilder(title, message, priority)
    // NotificationBuilder(title, message)
}
```

```kotlin
// @JvmField — прямой доступ к полю из Java (без getter)
class Config {
    companion object {
        @JvmField
        val DEFAULT_TIMEOUT = Duration.ofSeconds(30)

        @JvmField
        val MAX_RETRIES = 3
    }
}

// Java: Config.DEFAULT_TIMEOUT (не Config.Companion.getDEFAULT_TIMEOUT())
```

```kotlin
// typealias — мост между старыми и новыми типами
// Старый Java-код использует Map<String, Object>
// Новый Kotlin-код — типизированный Config

data class AppConfig(
    val dbUrl: String,
    val maxConnections: Int,
    val features: Set<String>
)

// Переходный период: старый код продолжает работать
typealias LegacyConfig = Map<String, Any>

fun LegacyConfig.toAppConfig(): AppConfig = AppConfig(
    dbUrl = this["db_url"] as String,
    maxConnections = this["max_connections"] as Int,
    features = (this["features"] as? List<*>)?.filterIsInstance<String>()?.toSet() ?: emptySet()
)
```

> [!info] Kotlin-нюанс
> `@JvmStatic`, `@JvmOverloads`, `@JvmField` --- три аннотации, которые делают Kotlin-код идиоматичным при вызове из Java. Без них Java-код вынужден обращаться к `Companion` и использовать геттеры. Правило: если файл вызывается из Java --- добавьте эти аннотации.

---

### Порядок миграции Java → Kotlin

```
┌──────────────────────────────────────────────────────────────────────┐
│                ПОРЯДОК МИГРАЦИИ JAVA → KOTLIN                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Фаза 1: Тесты (низкий риск)                                       │
│  ├── Конвертировать тесты в Kotlin                                  │
│  ├── Использовать MockK вместо Mockito                              │
│  └── Начать писать новые тесты на Kotlin                            │
│                                                                      │
│  Фаза 2: Утилиты и модели (средний риск)                           │
│  ├── Data-классы: POJO → data class                                 │
│  ├── Утилитарные классы → top-level/extension функции               │
│  └── Constants → const val / enum class                             │
│                                                                      │
│  Фаза 3: Бизнес-логика (высокий риск)                              │
│  ├── Сервисы — по одному файлу                                      │
│  ├── @JvmOverloads для обратной совместимости                       │
│  └── Null-safety: @Nullable → ? в Kotlin                            │
│                                                                      │
│  Фаза 4: API/UI (самый высокий риск)                               │
│  ├── Controllers / Activities / Fragments                           │
│  ├── API contracts — проверить сериализацию                         │
│  └── UI-тесты обязательны                                           │
│                                                                      │
│  ПРАВИЛО: Каждая фаза — отдельная ветка + code review              │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Decision Framework: рефакторить, переписать или оставить?

| Критерий | Рефакторить | Переписать | Оставить |
|----------|------------|-----------|---------|
| **Тесты** | Есть или можно добавить | Невозможно добавить | Не нужны (код стабилен) |
| **Понимание** | Разбираемся постепенно | Понимаем что нужно, но код — хаос | Никто не понимает, и не нужно |
| **Размер** | Любой | Маленький модуль | Любой |
| **Активность** | Часто меняется | Часто меняется | Не меняется |
| **Риск** | Низкий (инкрементально) | Высокий ("second system syndrome") | Нулевой |
| **Бизнес-давление** | Среднее | Низкое (нужно время) | Высокое (нет времени) |

### Красные флаги для переписывания

1. **Second System Effect** (Brooks): переписывание с нуля часто добавляет ненужную сложность.
2. **Потеря знаний**: legacy-код содержит неявные бизнес-правила, которые забудут перенести.
3. **Параллельная разработка**: поддерживать два кода одновременно --- двойные затраты.

> Правило: если сомневаетесь --- рефакторьте. Переписывание --- крайняя мера.

---

## Управление рисками

### Ветки и feature flags

```kotlin
// Feature flag для безопасного включения нового кода
interface FeatureFlags {
    fun isEnabled(feature: String): Boolean
}

// Использование
class CheckoutService(
    private val legacyProcessor: LegacyPaymentProcessor,
    private val newProcessor: NewPaymentProcessor,
    private val flags: FeatureFlags
) {
    fun checkout(cart: Cart): CheckoutResult {
        val paymentResult = if (flags.isEnabled("new-payment-processor")) {
            newProcessor.process(cart.total)
        } else {
            legacyProcessor.process(cart.total)
        }
        return CheckoutResult(paymentResult)
    }
}
```

### Parallel Run: сравнение legacy и нового кода

```kotlin
// Запускаем оба, сравниваем результаты, используем legacy
class ParallelPaymentProcessor(
    private val legacy: LegacyPaymentProcessor,
    private val modern: ModernPaymentProcessor,
    private val logger: Logger
) {
    fun process(amount: BigDecimal): PaymentResult {
        val legacyResult = legacy.process(amount)

        try {
            val modernResult = modern.process(amount)
            if (legacyResult != modernResult) {
                logger.warn(
                    "Payment mismatch! Legacy: $legacyResult, Modern: $modernResult"
                )
            }
        } catch (e: Exception) {
            logger.error("Modern processor failed", e)
        }

        return legacyResult  // ← всегда возвращаем legacy (пока не доверяем новому)
    }
}
```

### Boy Scout Rule: оставь код чище, чем нашёл

```kotlin
// При каждом изменении legacy-кода:
// 1. Добавить characterization test для затронутого метода
// 2. Сделать одно маленькое улучшение
// 3. Коммит

// Пример: заменили stringly-typed параметр на enum
// До: fun process(type: String)
// После: fun process(type: OrderType)
// + characterization test для всех существующих значений type
```

---

## Проверь себя

<details>
<summary>1. Почему characterization test фиксирует текущее поведение, а не "правильное"?</summary>

**Ответ:**

Цель characterization test --- создать **safety net** для рефакторинга, а не доказать корректность. Если зафиксировать "правильное" поведение, тест сразу будет красным, и нет baseline для рефакторинга. Стратегия: 1) зафиксировать текущее поведение (тесты зелёные), 2) рефакторить структуру (тесты остаются зелёные), 3) исправить поведение отдельным шагом (тест меняется). Исправление бага и рефакторинг --- **никогда** одновременно.

</details>

<details>
<summary>2. Чем Sprout Method отличается от Wrap Method?</summary>

**Ответ:**

**Sprout Method:** новая логика добавляется **перед/внутри** legacy-вызова. Пример: валидация данных перед обработкой. Legacy-код вызывает новый код.

**Wrap Method:** legacy-вызов оборачивается **снаружи** с pre/post логикой. Пример: логирование и метрики вокруг legacy-вызова. Новый код вызывает legacy.

Общее: оба позволяют добавить функциональность без изменения legacy-кода.

</details>

<details>
<summary>3. Почему extension-функция — идеальный Sprout Method в Kotlin?</summary>

**Ответ:**

1. **Не нужно открывать legacy-файл** --- extension живёт в отдельном файле.
2. **Выглядит как метод класса** --- вызывающий код читается естественно.
3. **Полностью тестируема** --- отдельный тест для extension.
4. **Не меняет legacy-класс** --- нет риска сломать существующее поведение.
5. **Легко найти** --- IDE показывает extensions при auto-complete.

Ограничение: extension не имеет доступа к private членам класса.

</details>

<details>
<summary>4. В каком порядке мигрировать Java → Kotlin?</summary>

**Ответ:**

1. **Тесты** (низкий риск): конвертировать, начать использовать MockK.
2. **Модели и утилиты** (средний риск): POJO → data class, utils → extensions.
3. **Бизнес-логика** (высокий риск): сервисы по одному файлу, `@JvmOverloads` для совместимости.
4. **API/UI** (самый высокий риск): controllers, проверить сериализацию, UI-тесты.

Начинать с листьев графа зависимостей (файлы, от которых никто не зависит).

</details>

<details>
<summary>5. Когда Strangler Fig лучше, чем Big Bang переписывание?</summary>

**Ответ:**

**Strangler Fig лучше когда:** система большая, нужна непрерывная работа, риски должны быть контролируемы, команда может работать инкрементально.

**Big Bang допустим когда:** модуль маленький и изолированный, поведение полностью понятно и задокументировано тестами, есть временной буфер.

Strangler Fig --- default choice. Big Bang --- исключение, требующее обоснования.

</details>

---

## Ключевые карточки

Что такое legacy code по определению Фезерса?
?
Код без тестов. Не возраст определяет legacy, а отсутствие safety net. Вчерашний код без тестов --- legacy. Десятилетний код с хорошим покрытием --- просто код. Ключевая проблема: без тестов нельзя безопасно менять код.

Что такое characterization test и как его писать?
?
Тест, фиксирующий ТЕКУЩЕЕ поведение (даже неправильное). Методика: 1) вызвать код с конкретным входом, 2) посмотреть результат, 3) записать как expected. Цель --- safety net для рефакторинга, не доказательство корректности. Баг-фикс и рефакторинг --- НИКОГДА одновременно.

Какие три типа Seams существуют?
?
1) **Object Seam** --- подмена зависимости через конструктор/интерфейс (самый частый). 2) **Link Seam** --- подмена через DI-контейнер (Koin, Dagger). 3) **Preprocessing Seam** --- feature flags. В Kotlin: constructor injection --- идиоматичный Object Seam.

Чем Sprout Method отличается от Wrap Method?
?
**Sprout:** новая логика ПЕРЕД/ВНУТРИ legacy. Legacy вызывает новый код. Пример: валидация. **Wrap:** legacy оборачивается СНАРУЖИ. Новый код вызывает legacy. Пример: логирование. В Kotlin: extension-функция --- идеальный Sprout Method (не трогаем legacy-файл).

Что такое Strangler Fig Pattern?
?
Постепенная замена legacy новым кодом. Router/Facade направляет запросы: сначала всё → legacy, потом часть → новый код, в конце всё → новый код. Feature flags управляют переключением. Придумал Мартин Фаулер по аналогии с фикусом-душителем.

Какие @Jvm-аннотации нужны для Java-interop при миграции?
?
`@JvmStatic` --- companion object метод доступен как static из Java. `@JvmOverloads` --- генерирует overloads для параметров с дефолтами. `@JvmField` --- прямой доступ к полю без getter. Правило: если Kotlin-код вызывается из Java --- добавьте эти аннотации.

Рефакторить, переписать или оставить — как решить?
?
**Рефакторить:** есть/можно добавить тесты, код часто меняется, риск низкий. **Переписать:** маленький модуль, код непонятен, тесты невозможно добавить. **Оставить:** код стабилен, не меняется, нет бизнес-давления. Default choice --- рефакторить. Переписывание --- крайняя мера (Second System Effect).

Что такое Parallel Run и зачем он нужен?
?
Запуск legacy и нового кода одновременно, сравнение результатов. Возвращается legacy-результат (пока не доверяем новому). Расхождения логируются. Позволяет валидировать новый код на production-данных без риска. Отключается когда расхождений 0% за N дней.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[refactoring-catalog]] | Конкретные техники для улучшения legacy |
| Углубиться | [[code-smells]] | Распознать запахи, чтобы знать что улучшать |
| Смежная тема | [[testing-fundamentals]] | Тесты --- prerequisite для безопасной работы с legacy |
| Практика | [[kotlin-interop]] | Kotlin-Java interop для миграции |

---

## Источники

- Feathers M. "Working Effectively with Legacy Code" (2004) --- каноническое руководство по legacy
- Fowler M. "Refactoring: Improving the Design of Existing Code" (2nd ed., 2018) --- рефакторинги для legacy
- Martin R.C. "Clean Code" (2008) --- Boy Scout Rule и принципы чистого кода
- Moskala M. "Effective Kotlin" (2nd ed., 2022) --- идиоматичный Kotlin и interop
- [Martin Fowler — Strangler Fig Application](https://martinfowler.com/bliki/StranglerFigApplication.html) --- описание паттерна
- [Understand Legacy Code — Key Points of Feathers' Book](https://understandlegacycode.com/blog/key-points-of-working-effectively-with-legacy-code/) --- конспект ключевых идей
- [Kotlin Documentation — Calling Kotlin from Java](https://kotlinlang.org/docs/java-to-kotlin-interop.html) --- @JvmStatic, @JvmOverloads, @JvmField
- [Android Developers — Kotlin-Java Interop Guide](https://developer.android.com/kotlin/interop) --- практический гайд для Android
- [Shopify Engineering — Strangler Fig Pattern](https://shopify.engineering/refactoring-legacy-code-strangler-fig-pattern) --- реальный кейс миграции

---

*Проверено: 2026-02-19*
