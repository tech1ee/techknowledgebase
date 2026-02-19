---
title: "Основы ООП: четыре столпа объектно-ориентированного программирования"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/oop
  - topic/kotlin
related:
  - "[[solid-principles]]"
  - "[[composition-vs-inheritance]]"
  - "[[coupling-cohesion]]"
  - "[[kotlin-oop]]"
  - "[[design-patterns-overview]]"
---

# Основы ООП: четыре столпа объектно-ориентированного программирования

В 1967 году норвежцы Оле-Йохан Даль и Кристен Нюгорд создали Simula — первый язык с классами и наследованием — для моделирования очередей в почтовом отделении. Через 57 лет ООП объявляют мёртвым примерно раз в квартал. При этом 8 из 10 самых популярных языков (TIOBE 2025) остаются объектно-ориентированными. Kotlin идёт дальше: классы `final` по умолчанию, `sealed class` вместо открытых иерархий, `by` вместо наследования. Это не классическое ООП из учебника 2005 года — это ООП, которое учло ошибки предшественников.

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Базовый синтаксис Kotlin | val/var, функции, null-safety | [[kotlin-basics]] |
| Что такое тип данных | Понимание зачем нужны классы | [[type-systems-theory]] |

---

## Краткая история ООП

```
1967  Simula        — Даль, Нюгорд. Классы, наследование, виртуальные методы
        │
1972  Smalltalk     — Алан Кей. "Всё — объект". Сообщения вместо вызовов
        │
1979  C++           — Бьёрн Страуструп. ООП + производительность С
        │
1995  Java          — Гослинг. "Write once, run anywhere". ООП как мейнстрим
        │
2004  Scala         — Одерский. ООП + ФП на JVM
        │
2011  Kotlin        — JetBrains. "Лучше Java": final by default,
                       data class, sealed class, delegation by
```

> [!info] Что имел в виду Алан Кей
> Кей, автор термина "object-oriented programming", позже уточнил: «Мне жаль, что я придумал термин "объекты". Главная идея была в **сообщениях**». Smalltalk строился на идее объектов, общающихся через сообщения, а не на наследовании иерархий. Kotlin ближе к этой идее через интерфейсы и delegation, чем Java с её глубокими деревьями наследования.

---

## Четыре столпа: обзор

```
┌──────────────────────────────────────────────────────────────┐
│                      ООП: 4 столпа                          │
├────────────────┬───────────────┬──────────────┬──────────────┤
│ Инкапсуляция   │ Наследование  │ Полиморфизм  │ Абстракция   │
│                │               │              │              │
│ Скрыть         │ Переиспольз.  │ Один         │ Выделить     │
│ внутренности   │ через         │ интерфейс,   │ суть,        │
│                │ иерархию      │ много         │ скрыть       │
│                │               │ реализаций   │ детали       │
├────────────────┼───────────────┼──────────────┼──────────────┤
│ Kotlin:        │ Kotlin:       │ Kotlin:      │ Kotlin:      │
│ private set,   │ final by      │ interface,   │ interface,   │
│ internal,      │ default,      │ extension    │ abstract,    │
│ backing props  │ open/sealed   │ fun, generics│ sealed class │
└────────────────┴───────────────┴──────────────┴──────────────┘
```

---

## 1. Инкапсуляция (Encapsulation)

### Суть

Инкапсуляция — объединение данных и поведения в одном месте с контролем доступа. Цель — защитить инварианты объекта: внешний код не может привести объект в невалидное состояние.

**Аналогия:** банкомат. Вы видите экран, кнопки, слот для карты (публичный интерфейс). Но механизм проверки PIN, хранилище купюр, связь с банком скрыты внутри корпуса. Вы не можете напрямую залезть в хранилище — только через интерфейс.

### Kotlin: модификаторы видимости

```kotlin
// 4 модификатора видимости Kotlin vs 3 в Java
class BankAccount(
    val id: String,                    // public (по умолчанию) — читать можно
    private var balance: Long = 0      // private — доступ только внутри класса
) {
    // internal — виден внутри модуля (лучше чем Java package-private!)
    internal val isVip: Boolean
        get() = balance >= 1_000_000

    // protected — виден в подклассах
    // (в Kotlin protected НЕ виден из того же пакета, в отличие от Java!)

    fun deposit(amount: Long) {
        require(amount > 0) { "Сумма должна быть положительной" }
        balance += amount       // Изменение через контролируемый метод
    }

    fun withdraw(amount: Long): Boolean {
        if (amount > balance) return false
        balance -= amount
        return true
    }

    // Снаружи balance можно прочитать, но не изменить
    fun getBalance(): Long = balance
}
```

> [!info] Kotlin-нюанс: `internal`
> В Java `package-private` (доступ по умолчанию) работает на уровне пакета — любой класс в том же пакете видит поля. В Kotlin `internal` работает на уровне **модуля** (Gradle/Maven module). Это гораздо полезнее: модуль — это единица компиляции и деплоя, а пакет — лишь способ организации файлов.

### Kotlin: `private set` и backing properties

```kotlin
// Паттерн 1: private set — свойство читается снаружи, меняется внутри
class Counter {
    var count: Int = 0
        private set                    // getter — public, setter — private

    fun increment() {
        count++                        // Изменение только через метод
    }
}

val counter = Counter()
println(counter.count)     // OK: чтение
// counter.count = 42      // Ошибка компиляции: setter private

// Паттерн 2: backing property — экспонируем immutable версию
class TaskManager {
    // Приватный мутабельный список
    private val _tasks = mutableListOf<String>()

    // Публичный иммутабельный вид (List, не MutableList)
    val tasks: List<String>
        get() = _tasks.toList()    // Возвращаем копию!

    fun addTask(task: String) {
        _tasks.add(task)
    }
}

val manager = TaskManager()
manager.addTask("Написать тесты")
val list = manager.tasks       // List<String> — нельзя добавить/удалить
// list.add("Хак")             // Ошибка компиляции
```

### Kotlin: `data class` как инструмент инкапсуляции

```kotlin
// data class — все поля val = immutable по умолчанию
data class User(
    val id: Long,
    val name: String,
    val email: String
)

val user = User(1, "Алексей", "alex@mail.ru")
// user.name = "Борис"         // Ошибка: val нельзя изменить

// Изменение через copy() — создаётся новый объект
val updated = user.copy(name = "Борис")
println(user.name)             // "Алексей" — оригинал не изменился
println(updated.name)          // "Борис"
```

> [!warning] Ловушка: `data class` с `var`
> `data class User(var name: String)` компилируется, но нарушает принцип инкапсуляции — любой код может менять `name` напрямую. Всегда используйте `val` в `data class`. Если нужна модификация — через `copy()`.

### Подводные камни инкапсуляции

| Ошибка | Почему плохо | Как в Kotlin |
|--------|-------------|--------------|
| Геттеры/сеттеры на всё | Это не инкапсуляция, а бюрократия | Используйте `val` и `private set` |
| Утечка мутабельной коллекции | Внешний код меняет внутреннее состояние | Backing property + `toList()` |
| `var` в data class | Позволяет менять состояние без контроля | Всегда `val` + `copy()` |
| Один гигантский public API | Слишком много знаний о внутренностях | `internal` для модульных API |

---

## 2. Наследование (Inheritance)

### Суть

Наследование — механизм повторного использования кода через иерархию "родитель-потомок". Подкласс получает все свойства и методы родителя и может добавлять свои или переопределять существующие.

**Аналогия:** должностные инструкции. Базовая инструкция «Сотрудник» описывает общие правила (приходить вовремя, носить бейдж). Инструкция «Разработчик» наследует общие правила и добавляет специфичные (код-ревью, on-call). Инструкция «Тимлид» наследует от «Разработчика» и добавляет ещё (1-on-1, ретроспективы).

### Kotlin: `final` по умолчанию — и это хорошо

```kotlin
// В Java все классы open по умолчанию → Fragile Base Class Problem
// В Kotlin все классы final по умолчанию → осознанный выбор наследования

class PaymentService   // final! Нельзя наследовать
// class ExtendedPayment : PaymentService()  // Ошибка компиляции

// Чтобы разрешить наследование — явно пометьте open
open class BaseRepository {
    open fun save(entity: Any) {     // open — можно переопределить
        println("Saving $entity")
    }

    fun validate(entity: Any) {      // final (без open) — нельзя переопределить
        require(entity.toString().isNotBlank())
    }
}

class UserRepository : BaseRepository() {
    override fun save(entity: Any) {
        println("Saving user to users table")
        super.save(entity)
    }

    // override fun validate(entity: Any) — ОШИБКА: validate не open
}
```

> [!info] Kotlin-нюанс: почему `final` по умолчанию — правильно
> Джошуа Блох в "Effective Java" (Item 19): *"Design and document for inheritance, or else prohibit it"*. Неконтролируемое наследование ведёт к Fragile Base Class Problem — изменение родителя ломает потомков непредсказуемым образом. Kotlin делает этот совет правилом по умолчанию. Хотите наследование — напишите `open` и примите ответственность.

### `abstract`, `open`, `sealed` — три уровня контроля

```kotlin
// abstract — нельзя создать экземпляр, нужно наследовать
abstract class Shape {
    abstract val area: Double          // Контракт: потомки обязаны реализовать
    abstract fun draw(): String

    // Конкретный метод — доступен всем потомкам
    fun describe(): String = "Фигура с площадью ${"%.2f".format(area)}"
}

class Circle(val radius: Double) : Shape() {
    override val area: Double
        get() = Math.PI * radius * radius

    override fun draw(): String = "Рисую круг с радиусом $radius"
}

class Rectangle(val width: Double, val height: Double) : Shape() {
    override val area: Double
        get() = width * height

    override fun draw(): String = "Рисую прямоугольник ${width}x${height}"
}
```

```kotlin
// sealed — закрытая иерархия: все потомки известны на этапе компиляции
sealed class PaymentMethod {
    data class Card(val number: String, val expiry: String) : PaymentMethod()
    data class BankTransfer(val iban: String) : PaymentMethod()
    data class Cash(val currency: String) : PaymentMethod()
    data object Crypto : PaymentMethod()
}

// Компилятор ГАРАНТИРУЕТ обработку всех вариантов
fun processPayment(method: PaymentMethod): String = when (method) {
    is PaymentMethod.Card -> "Оплата картой *${method.number.takeLast(4)}"
    is PaymentMethod.BankTransfer -> "Перевод на ${method.iban}"
    is PaymentMethod.Cash -> "Наличные (${method.currency})"
    PaymentMethod.Crypto -> "Криптовалюта"
    // else НЕ НУЖЕН — компилятор знает все варианты!
    // Добавили новый подтип → ошибка компиляции здесь
}
```

> [!info] Kotlin-нюанс: `sealed class` — алгебраический тип данных
> В теории типов `sealed class` — это **sum type** (тип-сумма): `PaymentMethod = Card | BankTransfer | Cash | Crypto`. Каждый подтип — это **product type** (тип-произведение): `Card = number × expiry`. Это фундаментальная концепция из функциональных языков (Haskell, Rust), встроенная в Kotlin.

### Когда наследование — плохой выбор

```
Вопрос: "Класс B — это разновидность класса A?"
│
├── ДА (is-a) → Наследование может быть оправдано
│   Пример: Circle IS-A Shape
│
└── НЕТ (has-a, uses-a) → Композиция
    Пример: Car HAS-A Engine (не Car IS-AN Engine)

Дополнительная проверка:
├── Нужно ли B подставлять вместо A? (LSP)
├── Есть ли другие потомки A?
└── Будет ли A меняться? (Fragile Base Class)
```

```kotlin
// ПЛОХО: наследование для переиспользования кода
open class ArrayList<E> : AbstractList<E>()

class Stack<E> : ArrayList<E>() {  // Stack IS-A ArrayList? Нет!
    fun push(e: E) = add(e)
    fun pop(): E = removeAt(size - 1)
    // Проблема: stack.add(0, element) добавляет не на вершину!
}

// ХОРОШО: композиция через delegation
class Stack<E>(
    private val storage: MutableList<E> = mutableListOf()
) {
    fun push(e: E) { storage.add(e) }
    fun pop(): E = storage.removeAt(storage.size - 1)
    fun peek(): E = storage.last()
    val size: Int get() = storage.size
    // Никакого add(0, element) — интерфейс контролируемый
}
```

### Kotlin: delegation `by` — альтернатива наследованию

```kotlin
interface Logger {
    fun log(message: String)
    fun error(message: String)
}

class ConsoleLogger : Logger {
    override fun log(message: String) = println("[LOG] $message")
    override fun error(message: String) = System.err.println("[ERR] $message")
}

// Delegation: класс реализует Logger, делегируя все вызовы объекту logger
class TimestampLogger(
    private val logger: Logger
) : Logger by logger {
    // Переопределяем только то, что нужно
    override fun log(message: String) {
        logger.log("[${System.currentTimeMillis()}] $message")
    }
    // error() автоматически делегируется в logger
}

// Использование — TimestampLogger ведёт себя как Logger
val log: Logger = TimestampLogger(ConsoleLogger())
log.log("Запуск")    // [LOG] [1708300000000] Запуск
log.error("Сбой")    // [ERR] Сбой
```

> [!info] Kotlin-нюанс: `by` компилируется в прямые вызовы
> Delegation `by` — это compile-time генерация кода, не рефлексия. Компилятор генерирует методы-обёртки, которые после JIT-оптимизации работают с нулевым overhead. Это встроенный GoF Delegation Pattern на уровне языка.

---

## 3. Полиморфизм (Polymorphism)

### Суть

Полиморфизм — способность единого интерфейса работать с разными типами. Код вызывает `shape.draw()` и не знает, круг это или прямоугольник — каждый рисует себя сам.

**Аналогия:** розетка. Одна розетка (интерфейс) — много устройств (реализаций). Чайник, телефон, ноутбук — все подключаются одинаково, но делают разное.

### Три вида полиморфизма в Kotlin

```
Полиморфизм
├── 1. Подтиповый (Subtype)
│      Классический: interface → реализации
│      Kotlin: interface, abstract class, sealed class
│
├── 2. Ad-hoc
│      Разное поведение для разных типов
│      Kotlin: extension functions, operator overloading
│
└── 3. Параметрический (Parametric)
       Код работает с любым типом
       Kotlin: generics, reified type parameters
```

### Подтиповый полиморфизм

```kotlin
// Интерфейс определяет контракт — "что", а не "как"
interface Notification {
    val recipient: String
    fun send(): Boolean
    fun preview(): String
}

class EmailNotification(
    override val recipient: String,
    private val subject: String,
    private val body: String
) : Notification {
    override fun send(): Boolean {
        println("Отправляем email на $recipient: $subject")
        return true  // В реальности — SMTP-вызов
    }

    override fun preview() = "Email → $recipient: $subject"
}

class SmsNotification(
    override val recipient: String,
    private val message: String
) : Notification {
    override fun send(): Boolean {
        println("Отправляем SMS на $recipient: ${message.take(70)}")
        return true
    }

    override fun preview() = "SMS → $recipient: ${message.take(30)}..."
}

class PushNotification(
    override val recipient: String,
    private val title: String,
    private val payload: Map<String, String>
) : Notification {
    override fun send(): Boolean {
        println("Push для $recipient: $title")
        return true
    }

    override fun preview() = "Push → $recipient: $title"
}

// Код работает с ЛЮБОЙ реализацией Notification
class NotificationService {
    fun broadcast(notifications: List<Notification>) {
        notifications.forEach { notification ->
            val result = notification.send()   // Полиморфный вызов
            if (!result) {
                println("Не удалось: ${notification.preview()}")
            }
        }
    }
}

// Добавление нового типа (Telegram) НЕ требует изменения NotificationService
class TelegramNotification(
    override val recipient: String,
    private val chatId: Long,
    private val text: String
) : Notification {
    override fun send(): Boolean {
        println("Telegram #$chatId: $text")
        return true
    }

    override fun preview() = "Telegram → $recipient"
}
```

### Ad-hoc полиморфизм: extension functions

```kotlin
// Extension functions — добавляем поведение без наследования
// Разное поведение для разных типов (ad-hoc полиморфизм)

fun String.toSlug(): String =
    this.lowercase()
        .replace(Regex("[^a-zа-яё0-9\\s-]"), "")
        .replace(Regex("\\s+"), "-")
        .trim('-')

fun Int.isEven(): Boolean = this % 2 == 0

fun <T> List<T>.secondOrNull(): T? = if (size >= 2) this[1] else null

// Использование — выглядит как встроенные методы
println("Hello World!".toSlug())        // "hello-world"
println(42.isEven())                     // true
println(listOf("a", "b").secondOrNull()) // "b"
```

### Ad-hoc полиморфизм: operator overloading

```kotlin
// Перегрузка операторов — идиоматичный Kotlin
data class Money(val amount: Long, val currency: String) {

    // operator + : Money + Money
    operator fun plus(other: Money): Money {
        require(currency == other.currency) {
            "Нельзя складывать $currency и ${other.currency}"
        }
        return Money(amount + other.amount, currency)
    }

    // operator * : Money * Int
    operator fun times(multiplier: Int): Money =
        Money(amount * multiplier, currency)

    // operator > : Money > Money
    operator fun compareTo(other: Money): Int {
        require(currency == other.currency)
        return amount.compareTo(other.amount)
    }

    override fun toString(): String = "$amount $currency"
}

val price = Money(1000, "RUB")
val tax = Money(200, "RUB")
val total = price + tax                  // Money(1200, "RUB")
val doubled = price * 2                  // Money(2000, "RUB")
println(total > price)                   // true
```

### Параметрический полиморфизм: generics

```kotlin
// Один класс/функция работает с ЛЮБЫМ типом
class Repository<T : Any>(
    private val items: MutableList<T> = mutableListOf()
) {
    fun add(item: T) { items.add(item) }
    fun getAll(): List<T> = items.toList()
    fun find(predicate: (T) -> Boolean): T? = items.find(predicate)
}

// Один класс — разные типы
val userRepo = Repository<User>()
val orderRepo = Repository<Order>()
userRepo.add(User(1, "Алексей", "alex@mail.ru"))
orderRepo.add(Order(1, "Заказ #1"))
```

```kotlin
// Kotlin reified — доступ к типу в runtime (невозможно в Java!)
inline fun <reified T> parseJson(json: String): T {
    // T доступен в runtime благодаря reified
    return Gson().fromJson(json, T::class.java)
}

// Использование — тип выводится автоматически
val user: User = parseJson("""{"name": "Алексей"}""")
val order: Order = parseJson("""{"id": 1}""")
// В Java пришлось бы передавать Class<T> аргументом
```

> [!info] Kotlin-нюанс: `reified` type parameters
> В JVM из-за type erasure generic-типы недоступны в runtime. Kotlin обходит это через `inline fun` + `reified`: функция инлайнится в место вызова, и компилятор подставляет конкретный тип. Это невозможно в Java без передачи `Class<T>`.

---

## 4. Абстракция (Abstraction)

### Суть

Абстракция — выделение существенных характеристик и сокрытие несущественных деталей. Вы определяете ЧТО делать, а не КАК.

**Аналогия:** карта города. Карта показывает улицы, парки, метро (существенное для навигации). Но не показывает каждое дерево, каждую трещину на асфальте, цвет каждого дома. Карта — абстракция города.

### Интерфейсы Kotlin: абстракция с default-реализациями

```kotlin
// Интерфейс — чистая абстракция: ЧТО делать
interface Cache<K, V> {
    fun get(key: K): V?
    fun put(key: K, value: V)
    fun remove(key: K): Boolean
    fun clear()

    // Default implementation — поведение по умолчанию
    fun getOrPut(key: K, defaultValue: () -> V): V {
        val existing = get(key)
        if (existing != null) return existing
        val value = defaultValue()
        put(key, value)
        return value
    }

    // Свойства в интерфейсах (без backing field)
    val size: Int
    val isEmpty: Boolean get() = size == 0
}

// Реализация 1: In-memory cache
class InMemoryCache<K, V> : Cache<K, V> {
    private val store = mutableMapOf<K, V>()

    override fun get(key: K): V? = store[key]
    override fun put(key: K, value: V) { store[key] = value }
    override fun remove(key: K): Boolean = store.remove(key) != null
    override fun clear() = store.clear()
    override val size: Int get() = store.size
}

// Реализация 2: LRU cache с ограничением размера
class LruCache<K, V>(private val maxSize: Int) : Cache<K, V> {
    private val store = LinkedHashMap<K, V>(maxSize, 0.75f, true)

    override fun get(key: K): V? = store[key]
    override fun put(key: K, value: V) {
        store[key] = value
        if (store.size > maxSize) {
            store.remove(store.keys.first())
        }
    }
    override fun remove(key: K): Boolean = store.remove(key) != null
    override fun clear() = store.clear()
    override val size: Int get() = store.size
}

// Код-потребитель работает с абстракцией Cache, не с реализацией
class UserService(private val cache: Cache<Long, User>) {
    fun getUser(id: Long): User = cache.getOrPut(id) {
        // Дорогой запрос к БД
        fetchFromDatabase(id)
    }
}
```

### `abstract class` vs `interface` — когда что

```
Нужно ли хранить состояние (поля)?
├── ДА → abstract class
│   Пример: abstract class ViewModel { val state: MutableStateFlow }
│
└── НЕТ → interface
    ├── Нужна множественная реализация? → interface
    │   Пример: class Button : Clickable, Focusable, Drawable
    │
    └── Единственная иерархия? → и то, и то подходит
        Предпочтение: interface (гибче)
```

```kotlin
// abstract class — когда нужно состояние и частичная реализация
abstract class ViewModel {
    // Состояние — причина выбрать abstract class вместо interface
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Template Method: подклассы реализуют только loadData()
    suspend fun refresh() {
        _isLoading.value = true
        try {
            loadData()
        } finally {
            _isLoading.value = false
        }
    }

    protected abstract suspend fun loadData()
}

class UserViewModel(private val api: UserApi) : ViewModel() {
    override suspend fun loadData() {
        val users = api.getUsers()
        // обработка данных
    }
}
```

### `sealed class` как абстракция конечных состояний

```kotlin
// sealed class — абстракция с ИЗВЕСТНЫМ набором вариантов
sealed class UiState<out T> {
    data object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val message: String, val cause: Throwable? = null) : UiState<Nothing>()
    data object Empty : UiState<Nothing>()
}

// sealed interface — позволяет реализовывать несколько sealed-иерархий
sealed interface DatabaseOperation {
    data class Insert(val table: String, val data: Map<String, Any>) : DatabaseOperation
    data class Update(val table: String, val id: Long, val data: Map<String, Any>) : DatabaseOperation
    data class Delete(val table: String, val id: Long) : DatabaseOperation
    data class Query(val sql: String, val params: List<Any> = emptyList()) : DatabaseOperation
}

fun execute(op: DatabaseOperation): Any = when (op) {
    is DatabaseOperation.Insert -> "INSERT INTO ${op.table} ..."
    is DatabaseOperation.Update -> "UPDATE ${op.table} SET ... WHERE id = ${op.id}"
    is DatabaseOperation.Delete -> "DELETE FROM ${op.table} WHERE id = ${op.id}"
    is DatabaseOperation.Query  -> "EXECUTE: ${op.sql}"
}
```

> [!info] Kotlin-нюанс: `sealed interface` (Kotlin 1.5+)
> В отличие от `sealed class`, `sealed interface` позволяет подтипу реализовывать **несколько** sealed-интерфейсов. Это расширяет возможности моделирования: `data class NetworkError(val code: Int) : UiState, Loggable, Retryable`.

---

## Kotlin vs Java: сравнение OOP-подходов

| Аспект | Java | Kotlin | Почему Kotlin лучше |
|--------|------|--------|---------------------|
| Классы по умолчанию | `open` (можно наследовать) | `final` (нельзя) | Защита от Fragile Base Class |
| Статические методы | `static` | `companion object` | Companion — настоящий объект, может реализовывать интерфейсы |
| Data-классы | Lombok / Records (Java 16+) | `data class` | equals, hashCode, copy, destructuring — из коробки |
| Закрытые иерархии | Sealed classes (Java 17+) | `sealed class` (Kotlin 1.0+) | Раньше, проще синтаксис, `sealed interface` |
| Delegation | Ручная реализация | `by` keyword | Встроено в язык, zero-overhead |
| Inline classes | Project Valhalla (будущее) | `value class` | Уже доступно, type-safe обёртки |
| Null-safety | `@Nullable` / `Optional` | `?` в системе типов | Compile-time проверки |
| Properties | Getter/setter boilerplate | Встроенные `val`/`var` | Custom getter/setter, `private set` |
| Singleton | Double-checked locking | `object` keyword | Thread-safe, лаконичный |
| Visibility | `public`, `protected`, `package-private`, `private` | `public`, `protected`, `internal`, `private` | `internal` (модуль) полезнее `package-private` |

---

## Мифы и заблуждения

### Миф 1: "ООП мертво"

**Реальность:** ООП не умерло — эволюционировало. Критика направлена на **злоупотребления** ООП (глубокие иерархии, God Classes, наследование ради наследования), а не на саму парадигму. Современные языки (Kotlin, Rust, Swift) берут лучшее из ООП и ФП.

| Критика | Ответ |
|---------|-------|
| "Наследование создаёт хрупкие связи" | Согласны! Поэтому Kotlin — `final` по default, `by` вместо extends |
| "Mutable state — зло" | Согласны! Поэтому `val`, `data class`, `copy()` |
| "OOP слишком verbose" | Было в Java. `data class User(val name: String)` — одна строка |

### Миф 2: "Наследование — всегда плохо"

**Реальность:** Наследование плохо, когда используется для **переиспользования кода** (механическая экономия). Наследование хорошо для **моделирования отношений is-a** с правильным контрактом. `sealed class` — контролируемое наследование, где потомки известны на compile-time.

### Миф 3: "Функциональное программирование заменяет ООП"

**Реальность:** ООП и ФП — не конкуренты, а инструменты для разных задач. Kotlin идиоматично сочетает оба подхода:

```kotlin
// ООП: sealed class для моделирования домена
sealed class Expr {
    data class Num(val value: Double) : Expr()
    data class Sum(val left: Expr, val right: Expr) : Expr()
    data class Mul(val left: Expr, val right: Expr) : Expr()
}

// ФП: рекурсия + pattern matching для обработки
fun eval(expr: Expr): Double = when (expr) {
    is Expr.Num -> expr.value
    is Expr.Sum -> eval(expr.left) + eval(expr.right)
    is Expr.Mul -> eval(expr.left) * eval(expr.right)
}

// Результат: type-safe + компактный + расширяемый
val expression = Expr.Sum(Expr.Num(3.0), Expr.Mul(Expr.Num(2.0), Expr.Num(5.0)))
println(eval(expression))  // 13.0
```

### Миф 4: "Инкапсуляция — это просто геттеры и сеттеры"

**Реальность:** Геттеры/сеттеры на каждое поле — это иллюзия инкапсуляции. Настоящая инкапсуляция — это **контроль инвариантов**: объект сам решает, как его данные изменяются и какие состояния допустимы.

```kotlin
// ПЛОХО: геттер + сеттер = публичное поле с дополнительными шагами
class Account {
    var balance: Long = 0  // Любой код может сделать balance = -1000
}

// ХОРОШО: контролируемый доступ через поведение
class Account(initialBalance: Long) {
    var balance: Long = initialBalance
        private set

    fun deposit(amount: Long) {
        require(amount > 0) { "Сумма должна быть положительной" }
        balance += amount
    }

    fun withdraw(amount: Long): Boolean {
        if (amount > balance) return false
        balance -= amount
        return true
    }
}
```

---

## Паттерны ООП в production

### Google — Sealed class для UI State в Jetpack Compose

```kotlin
// Стандартный паттерн в Android-разработке (Jetpack Compose / MVI)
sealed class ScreenState<out T> {
    data object Loading : ScreenState<Nothing>()
    data class Content<T>(val data: T) : ScreenState<T>()
    data class Error(val message: String) : ScreenState<Nothing>()
}

// В Compose — exhaustive when гарантирует обработку всех состояний
@Composable
fun UserScreen(state: ScreenState<List<User>>) {
    when (state) {
        ScreenState.Loading -> CircularProgressIndicator()
        is ScreenState.Content -> UserList(state.data)
        is ScreenState.Error -> ErrorMessage(state.message)
    }
}
```

### Square / Cash App — Value class для type-safety

```kotlin
// Перепутать userId и orderId — классическая ошибка
// fun getOrder(userId: Long, orderId: Long)  ← легко перепутать

@JvmInline
value class UserId(val value: Long)

@JvmInline
value class OrderId(val value: Long)

// Теперь перепутать невозможно — ошибка компиляции
fun getOrder(userId: UserId, orderId: OrderId): Order { /* ... */ }

val userId = UserId(42)
val orderId = OrderId(100)
getOrder(userId, orderId)          // OK
// getOrder(orderId, userId)       // Ошибка компиляции!
// В runtime: обычные Long — zero overhead
```

### JetBrains — Delegation вместо наследования в IntelliJ

```kotlin
// Декоратор через delegation — добавление логирования
interface HttpClient {
    suspend fun get(url: String): Response
    suspend fun post(url: String, body: String): Response
}

class OkHttpClient : HttpClient {
    override suspend fun get(url: String): Response = TODO()
    override suspend fun post(url: String, body: String): Response = TODO()
}

class LoggingHttpClient(
    private val delegate: HttpClient
) : HttpClient by delegate {
    override suspend fun get(url: String): Response {
        println("→ GET $url")
        val response = delegate.get(url)
        println("← ${response.code}")
        return response
    }
    // post() автоматически делегируется — не нужно переопределять
}

// Стек декораторов — composition в действии
val client: HttpClient = LoggingHttpClient(
    RetryingHttpClient(
        CachingHttpClient(
            OkHttpClient()
        )
    )
)
```

---

## CS-фундамент

| CS-концепция | Как проявляется в Kotlin ООП |
|--------------|------------------------------|
| **Algebraic Data Types** | `sealed class` = sum type (A \| B \| C). `data class` = product type (A x B x C) |
| **Liskov Substitution** | `final` by default предотвращает нарушение LSP. Наследование — осознанный выбор |
| **Composition over Inheritance** | `by` delegation — GoF паттерн на уровне языка |
| **Type Safety** | `value class` — type-safe обёртки без runtime overhead |
| **Information Hiding** | `internal` (модульный), `private set`, backing properties |
| **Parametric Polymorphism** | Generics + `reified` type parameters (недоступно в Java) |
| **Prototype Pattern** | `data class copy()` — копирование с изменениями |

---

## Проверь себя

> [!question]- Почему в Kotlin классы `final` по умолчанию, и как это связано с принципами ООП?
> Kotlin следует рекомендации Блоха (Effective Java, Item 19): *"Design for inheritance or prohibit it"*. `final` by default решает Fragile Base Class Problem — изменение базового класса не ломает потомков, потому что потомков просто нет (если не разрешено явно через `open`). Это поддерживает принцип инкапсуляции: класс контролирует, кто и как может расширять его поведение. Хотите наследование — пишите `open` и принимайте ответственность за стабильность API.

> [!question]- Когда `sealed class` лучше `enum class`, а когда наоборот?
> `enum class` — когда все варианты singleton и имеют одинаковую структуру: `enum class Color(val rgb: Int) { RED(0xFF0000), GREEN(0x00FF00) }`. `sealed class` — когда варианты имеют **разную структуру данных**: `sealed class Result { data class Success(val data: String), data class Error(val code: Int, val message: String) }`. Правило: одинаковые поля → enum, разные поля → sealed.

> [!question]- Чем `delegation by` принципиально отличается от наследования и почему это лучше для композиции?
> Наследование создаёт жёсткую связь (tight coupling): изменение родителя ломает потомков. Delegation `by` — это composition: класс делегирует реализацию интерфейса другому объекту. Преимущества: (1) делегат можно заменить в runtime; (2) можно делегировать несколько интерфейсов разным объектам; (3) переопределяешь только нужные методы; (4) нет Fragile Base Class Problem. Компилятор генерирует прямые вызовы — zero runtime overhead.

> [!question]- Назовите три вида полиморфизма в Kotlin и приведите пример каждого.
> 1) **Подтиповый**: интерфейс `Notification`, реализации `EmailNotification`, `SmsNotification` — вызов `notification.send()` работает с любой реализацией. 2) **Ad-hoc**: extension function `fun String.toSlug()` и operator overloading `operator fun Money.plus(other: Money)` — разное поведение для разных типов. 3) **Параметрический**: `class Repository<T>` — один класс работает с любым типом `T`, сохраняя type-safety.

> [!question]- Почему "геттеры и сеттеры на каждое поле" — это НЕ инкапсуляция?
> Настоящая инкапсуляция — это контроль инвариантов объекта. Если `balance` имеет публичный сеттер, любой код может установить отрицательный баланс. Инкапсуляция — это `private set` + метод `withdraw()`, который проверяет достаточность средств. Getter + setter = публичное поле с синтаксическим сахаром. Инкапсуляция = поведение, защищающее инварианты.

---

## Ключевые карточки

Что такое инкапсуляция и чем она отличается от простого сокрытия полей?
?
Инкапсуляция — объединение данных и поведения с контролем доступа для защиты инвариантов. Сокрытие полей (private + getter/setter) — лишь механизм. Настоящая инкапсуляция: объект сам решает, какие состояния допустимы. Kotlin: `private set`, backing properties, `data class` с `val`, `copy()`.

Почему Kotlin классы `final` по умолчанию?
?
Следуя "Effective Java" Item 19: "Design for inheritance or prohibit it". `final` by default решает Fragile Base Class Problem: изменение базового класса не ломает потомков. Для наследования нужно явно указать `open` — это осознанный выбор, а не случайность.

Чем `sealed class` отличается от `abstract class` и `enum class`?
?
`abstract class` — открытая иерархия: потомки могут быть где угодно. `enum class` — фиксированные singleton-экземпляры с одинаковой структурой. `sealed class` — закрытая иерархия: все потомки известны compile-time, каждый может иметь разную структуру. Компилятор проверяет exhaustiveness в `when`.

Что такое delegation `by` и зачем он нужен?
?
`class A(b: B) : Interface by b` — A реализует Interface, делегируя вызовы объекту b. Compile-time генерация, zero overhead. Заменяет наследование композицией: нет Fragile Base Class, можно делегировать несколько интерфейсов разным объектам, переопределять только нужные методы.

Что такое ad-hoc полиморфизм в Kotlin?
?
Разное поведение для разных типов без общего базового класса. Kotlin: extension functions (`fun String.toSlug()`) и operator overloading (`operator fun Money.plus()`). В отличие от подтипового полиморфизма, не требует наследования или интерфейсов.

Что такое `reified` type parameter и почему он невозможен в Java?
?
`inline fun <reified T> parse(json: String): T` — тип T доступен в runtime. Работает через inline: функция встраивается в место вызова, компилятор подставляет конкретный тип. В Java generic-типы стираются (type erasure), поэтому T недоступен в runtime без передачи `Class<T>`.

Чем `internal` в Kotlin лучше `package-private` в Java?
?
`internal` работает на уровне модуля (Gradle/Maven), а `package-private` — на уровне пакета. Модуль — единица компиляции и деплоя; пакет — лишь способ организации файлов. Любой код в том же пакете видит `package-private` поля, что слабее ограничения модуля.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Углубление | [[solid-principles]] | Пять принципов проектирования — как строить ООП правильно |
| Углубление | [[composition-vs-inheritance]] | Когда наследование, когда композиция — детальный разбор |
| Связь | [[kotlin-oop]] | Полный справочник Kotlin OOP: data class, sealed class, delegation |
| Связь | [[design-patterns-overview]] | Паттерны GoF в Kotlin — как ООП-принципы реализуются на практике |
| Связь | [[functional-programming]] | ФП + ООП: как Kotlin сочетает обе парадигмы |
| Навигация | [[programming-overview]] | Вернуться к карте раздела Programming |

---

## Источники

- Jemerov D., Isakova S. (2017). *Kotlin in Action*. Manning. — Главы 2, 4: классы, интерфейсы, data classes, object declarations. Лучшее объяснение ООП-модели Kotlin.
- Moskala M. (2021). *Effective Kotlin*. Kt. Academy. — Items о предпочтении composition over inheritance, правильном использовании data class и sealed class.
- Bloch J. (2018). *Effective Java*, 3rd ed. Addison-Wesley. — Item 17-19: design for inheritance, prefer interfaces, minimize mutability. Принципы, которым Kotlin следует на уровне языка.
- Martin R.C. (2008). *Clean Code*. Prentice Hall. — Глава 6: Objects and Data Structures, принципы инкапсуляции.
- [Kotlin Documentation: Classes and Objects](https://kotlinlang.org/docs/classes.html) — официальная документация по классам, наследованию, интерфейсам, sealed classes.
- [Kotlin Documentation: Sealed Classes](https://kotlinlang.org/docs/sealed-classes.html) — exhaustive when, sealed interface, ограничения наследования.
- [ByteByteGo: Fundamental Pillars of OOP](https://blog.bytebytego.com/p/ep142-the-fundamental-pillars-of) — визуальный обзор четырёх столпов с modern perspective.
- [In Defense of OOP (2024)](https://thinkingsideways.net/software/design/defense-of-oop.html) — сбалансированный взгляд на критику и защиту ООП.
- [The New Stack: Why Developers Hate OOP](https://thenewstack.io/why-are-so-many-developers-hating-on-object-oriented-programming/) — обзор основных критических аргументов.

---

*Проверено: 2026-02-19 | Источники: Kotlin docs, Effective Kotlin, Effective Java, Clean Code*