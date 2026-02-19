---
title: "Singleton: объект в единственном экземпляре"
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
  - "[[factory-pattern]]"
  - "[[kotlin-oop]]"
  - "[[android-dependency-injection]]"
---

# Singleton: объект в единственном экземпляре

Singleton --- самый простой паттерн GoF и одновременно самый спорный. В Java для потокобезопасного singleton нужно 15-20 строк кода с `volatile`, `synchronized` и double-checked locking. В Kotlin: `object AppConfig { ... }` --- одна строка, компилятор гарантирует потокобезопасность и ленивую инициализацию. Но простота создания не делает Singleton хорошей идеей --- глобальное состояние остаётся глобальным состоянием, даже если оно обёрнуто в красивое ключевое слово. Разберёмся, когда `object` --- правильный выбор, а когда лучше использовать DI.

---

## Проблема

Иногда нужен **ровно один экземпляр** объекта на всё приложение:

- Пул подключений к базе данных
- Менеджер конфигурации
- Логгер
- Кэш в памяти

Без контроля создания каждый модуль может создать свой экземпляр --- и данные рассинхронизируются, ресурсы утекут, логи разъедутся по разным файлам.

```
Без Singleton:

Module A: val db = DatabasePool()    ← свой пул, 10 соединений
Module B: val db = DatabasePool()    ← ещё пул, ещё 10 соединений
Module C: val db = DatabasePool()    ← и ещё 10

Итого: 30 соединений вместо 10 → база падает
```

---

## Классические реализации (до Kotlin)

### Java: Double-Checked Locking

```kotlin
// Как это выглядело в Java (переведено в Kotlin-синтаксис для сравнения)
class DatabasePool private constructor() {
    companion object {
        @Volatile
        private var instance: DatabasePool? = null

        fun getInstance(): DatabasePool {
            if (instance == null) {                    // 1-я проверка (без lock)
                synchronized(this) {
                    if (instance == null) {             // 2-я проверка (с lock)
                        instance = DatabasePool()
                    }
                }
            }
            return instance!!
        }
    }
}
```

**Проблемы:**
- `@Volatile` + `synchronized` + двойная проверка --- легко ошибиться
- `instance!!` --- force unwrap, потенциальный NPE при рефлексии
- 15 строк boilerplate для простой задачи

### Java: Enum Singleton (Bloch)

Joshua Bloch в "Effective Java" рекомендовал enum-singleton как самый надёжный способ:

```kotlin
// Java-стиль: enum singleton
// Защищён от рефлексии и сериализации
enum class DatabasePool {
    INSTANCE;

    fun getConnection(): Connection { /* ... */ }
}

DatabasePool.INSTANCE.getConnection()
```

Работает, но неестественно --- enum создан для перечислений, а не для единственного экземпляра.

---

## Kotlin: `object` --- Singleton в одну строку

```kotlin
object DatabasePool {
    private val connections = mutableListOf<Connection>()
    private val maxSize = 10

    fun getConnection(): Connection {
        if (connections.isEmpty()) {
            return createConnection()
        }
        return connections.removeFirst()
    }

    fun releaseConnection(conn: Connection) {
        if (connections.size < maxSize) {
            connections.add(conn)
        }
    }

    private fun createConnection(): Connection {
        println("Creating new connection")
        return Connection()
    }
}

// Использование --- просто обращаемся по имени
val conn = DatabasePool.getConnection()
DatabasePool.releaseConnection(conn)
```

> [!info] Kotlin-нюанс
> `object` --- не синтаксический сахар, а первоклассная языковая конструкция. Компилятор генерирует класс с приватным конструктором, статическим полем `INSTANCE` и static initializer block. Потокобезопасность гарантируется JVM-механизмом загрузки классов --- тем же, что и у enum-singleton Блоха.

### Что генерирует компилятор (деcompiled bytecode)

```kotlin
// Kotlin:
object AppConfig {
    val apiUrl = "https://api.example.com"
    fun isDebug() = false
}
```

Компилятор превращает это в:

```java
// Decompiled Java:
public final class AppConfig {
    public static final AppConfig INSTANCE;  // единственный экземпляр
    private static final String apiUrl = "https://api.example.com";

    private AppConfig() { }  // приватный конструктор

    static {
        AppConfig var0 = new AppConfig();    // создание в static block
        INSTANCE = var0;                      // → потокобезопасно!
    }

    public final String getApiUrl() { return apiUrl; }
    public final boolean isDebug() { return false; }
}
```

```
Гарантии JVM:
┌──────────────────────────────────────────────────┐
│  Static initializer block выполняется ровно 1 раз│
│  JVM гарантирует:                                │
│  ✓ Thread-safety (через class loading lock)      │
│  ✓ Lazy init (при первом обращении к классу)     │
│  ✓ Атомарность инициализации                     │
│  ✗ НО: "lazy" = при загрузке класса, не объекта  │
└──────────────────────────────────────────────────┘
```

---

## `companion object` как частичный Singleton

`companion object` --- это singleton, привязанный к классу. Он часто используется для Factory Method:

```kotlin
class User private constructor(
    val name: String,
    val email: String
) {
    companion object {
        // companion object --- singleton внутри класса
        private val cache = mutableMapOf<String, User>()

        fun create(email: String): User {
            return cache.getOrPut(email) {
                val name = email.substringBefore("@")
                User(name, email)
            }
        }

        fun guest(): User = User("Guest", "guest@example.com")
    }
}

// Companion object работает как Singleton:
// User.create("a@b.com") всегда возвращает кэшированный экземпляр
// User.cache --- общий кэш на всё приложение
```

> [!info] Kotlin-нюанс
> `companion object` может реализовывать интерфейсы, что невозможно со `static` в Java. Это мост между Singleton и Factory:
> ```kotlin
> interface UserFactory {
>     fun fromEmail(email: String): User
> }
>
> class User private constructor(val name: String) {
>     companion object : UserFactory {
>         override fun fromEmail(email: String) =
>             User(email.substringBefore("@"))
>     }
> }
> ```

---

## `lazy {}` --- отложенная потокобезопасная инициализация

Для свойств, которые дорого создавать:

```kotlin
object AppConfig {
    // Инициализируется при первом обращении, не при загрузке object
    val database: DatabasePool by lazy {
        println("Initializing database pool...")
        DatabasePool.create(
            url = System.getenv("DB_URL"),
            maxConnections = 10
        )
    }

    val cache: RedisClient by lazy {
        println("Connecting to Redis...")
        RedisClient.connect(System.getenv("REDIS_URL"))
    }
}

// database не создаётся, пока к нему не обратились
val pool = AppConfig.database  // "Initializing database pool..."
val pool2 = AppConfig.database // повторный вызов --- без повторной инициализации
```

### Режимы потокобезопасности `lazy`

```kotlin
// По умолчанию: SYNCHRONIZED (потокобезопасный, с lock)
val heavy by lazy { computeExpensiveValue() }

// Без синхронизации (быстрее, но не для многопоточности)
val fast by lazy(LazyThreadSafetyMode.NONE) {
    computeExpensiveValue()
}

// Публикация: несколько потоков могут вычислить,
// но все увидят одно и то же значение
val published by lazy(LazyThreadSafetyMode.PUBLICATION) {
    computeExpensiveValue()
}
```

---

## Потокобезопасность: `object` безопасен, но его содержимое --- нет

**Критически важно:** `object` гарантирует единственность экземпляра, но **не защищает мутабельные данные внутри**:

```kotlin
object Counter {
    private var count = 0  // ← мутабельное состояние!

    fun increment() {
        count++  // ← НЕ атомарно! Race condition!
    }

    fun get() = count
}

// 1000 корутин одновременно:
// Ожидаем: count = 1000
// Получаем: count = 847 (или другое случайное число)
```

### Решение 1: `AtomicInteger` / `AtomicReference`

```kotlin
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference

object Counter {
    private val count = AtomicInteger(0)

    fun increment() {
        count.incrementAndGet()  // атомарная операция
    }

    fun get() = count.get()
}

// Для сложных объектов:
object ConfigHolder {
    private val config = AtomicReference(AppConfig.default())

    fun update(newConfig: AppConfig) {
        config.set(newConfig)
    }

    fun get(): AppConfig = config.get()
}
```

### Решение 2: `Mutex` (для корутин)

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

object UserCache {
    private val mutex = Mutex()
    private val cache = mutableMapOf<String, User>()

    suspend fun getOrLoad(id: String): User = mutex.withLock {
        cache.getOrPut(id) {
            // Загрузка из сети/БД --- только один поток делает это
            loadUser(id)
        }
    }

    suspend fun invalidate(id: String) = mutex.withLock {
        cache.remove(id)
    }
}
```

### Решение 3: `ConcurrentHashMap`

```kotlin
import java.util.concurrent.ConcurrentHashMap

object Registry {
    // ConcurrentHashMap --- потокобезопасен без явных блокировок
    private val services = ConcurrentHashMap<String, Any>()

    fun register(name: String, service: Any) {
        services[name] = service
    }

    @Suppress("UNCHECKED_CAST")
    fun <T> resolve(name: String): T =
        services[name] as? T
            ?: throw IllegalStateException("Service '$name' not registered")
}
```

---

## Когда Singleton --- антипаттерн

### 1. Скрытые зависимости

```kotlin
// Плохо: зависимость от UserRepository скрыта
class OrderService {
    fun createOrder(userId: String): Order {
        // Откуда взялся UserRepository? Из конструктора? Нет!
        val user = UserRepository.findById(userId)  // ← скрытая связь
        return Order(user, items)
    }
}

// Хорошо: зависимость явная
class OrderService(
    private val userRepo: UserRepository  // ← видно в конструкторе
) {
    fun createOrder(userId: String): Order {
        val user = userRepo.findById(userId)
        return Order(user, items)
    }
}
```

### 2. Невозможность тестирования

```kotlin
// Singleton: как подменить для теста?
object Analytics {
    fun track(event: String) {
        // Отправляет в production API --- в тестах не нужно!
        HttpClient.post("https://analytics.prod.com/track", event)
    }
}

class CheckoutService {
    fun checkout() {
        // ...
        Analytics.track("purchase")  // ← в тестах полетят реальные запросы!
    }
}

// С DI: легко подменить
interface Analytics {
    fun track(event: String)
}

class ProductionAnalytics : Analytics {
    override fun track(event: String) {
        HttpClient.post("https://analytics.prod.com/track", event)
    }
}

class FakeAnalytics : Analytics {
    val trackedEvents = mutableListOf<String>()
    override fun track(event: String) { trackedEvents.add(event) }
}

class CheckoutService(private val analytics: Analytics) {
    fun checkout() {
        analytics.track("purchase")
    }
}

// Тест:
val fakeAnalytics = FakeAnalytics()
val service = CheckoutService(fakeAnalytics)
service.checkout()
assertEquals("purchase", fakeAnalytics.trackedEvents.first())
```

### 3. Глобальное мутабельное состояние

```kotlin
// God Object Singleton --- антипаттерн
object AppState {
    var currentUser: User? = null
    var authToken: String? = null
    var cartItems: MutableList<Item> = mutableListOf()
    var theme: Theme = Theme.LIGHT
    var language: String = "ru"
    var notifications: MutableList<Notification> = mutableListOf()
    // ... ещё 30 полей

    // Кто менял currentUser? Когда? Из какого потока?
    // Удачи в отладке.
}
```

### 4. Нарушение Single Responsibility

```kotlin
// Singleton отвечает И за бизнес-логику, И за своё создание
object PaymentProcessor {
    // SRP нарушен: класс управляет и платежами, и собственным жизненным циклом
    fun process(payment: Payment): Result { /* ... */ }
}
```

---

## Современная альтернатива: Dependency Injection

DI-контейнеры (Hilt, Koin, Dagger) дают singleton-скоуп без недостатков паттерна:

### Koin

```kotlin
// Объявление singleton-скоупа
val appModule = module {
    single { DatabasePool(get()) }           // один экземпляр
    single { UserRepository(get()) }
    factory { OrderService(get(), get()) }   // новый на каждый запрос
}

// Использование
class OrderService(
    private val userRepo: UserRepository,  // ← внедряется DI
    private val db: DatabasePool           // ← тот же singleton
) {
    fun createOrder(userId: String): Order {
        val user = userRepo.findById(userId)
        return Order(user)
    }
}

// Тест: подменяем зависимости
@Test
fun `create order returns valid order`() {
    val testModule = module {
        single { FakeUserRepository() as UserRepository }
        single { InMemoryDatabase() as DatabasePool }
    }
    startKoin { modules(testModule) }
    // ...
}
```

### Hilt (Android)

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object AppModule {
    @Provides
    @Singleton  // ← singleton scope через аннотацию
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .build()

    @Provides
    @Singleton
    fun provideApiService(): ApiService =
        Retrofit.Builder()
            .baseUrl("https://api.example.com")
            .build()
            .create(ApiService::class.java)
}

// Зависимость внедряется автоматически
@HiltViewModel
class OrderViewModel @Inject constructor(
    private val db: AppDatabase,      // ← singleton, управляемый DI
    private val api: ApiService       // ← singleton, управляемый DI
) : ViewModel() {
    // Тестируемо: подменяем через конструктор
}
```

---

## Когда `object` по-прежнему уместен

Не всё нужно заворачивать в DI. `object` хорош для:

### 1. Stateless-утилиты

```kotlin
object StringUtils {
    fun isEmail(value: String): Boolean =
        value.matches(Regex("^[\\w.-]+@[\\w.-]+\\.[a-zA-Z]{2,}$"))

    fun slugify(text: String): String =
        text.lowercase()
            .replace(Regex("[^a-z0-9\\s-]"), "")
            .replace(Regex("[\\s-]+"), "-")
            .trim('-')
}
```

### 2. Константы

```kotlin
object ApiEndpoints {
    const val BASE_URL = "https://api.example.com/v2"
    const val USERS = "$BASE_URL/users"
    const val ORDERS = "$BASE_URL/orders"

    const val TIMEOUT_MS = 30_000L
    const val MAX_RETRIES = 3
}
```

### 3. Sealed class companions

```kotlin
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val code: Int, val message: String) : NetworkResult<Nothing>()
    data object Loading : NetworkResult<Nothing>()  // data object = singleton
}
```

### 4. Именованные реализации интерфейсов

```kotlin
interface Comparator<T> {
    fun compare(a: T, b: T): Int
}

object NaturalOrder : Comparator<Int> {
    override fun compare(a: Int, b: Int) = a.compareTo(b)
}

object ReverseOrder : Comparator<Int> {
    override fun compare(a: Int, b: Int) = b.compareTo(a)
}
```

---

## Сводная таблица: `object` vs DI

```
┌──────────────────────────────┬────────────────────────────────────┐
│     Kotlin `object`          │     DI singleton scope             │
├──────────────────────────────┼────────────────────────────────────┤
│ Stateless утилиты            │ Stateful сервисы                   │
│ Константы                    │ Репозитории                        │
│ Pure functions               │ Сетевые клиенты                    │
│ Sealed class variants        │ Базы данных                        │
│ Нет внешних зависимостей     │ Есть зависимости                   │
│ Тестировать не нужно         │ Нужно тестировать                  │
├──────────────────────────────┼────────────────────────────────────┤
│ Зависимости скрыты           │ Зависимости явные                  │
│ Подменить нельзя             │ Подменяется через DI               │
│ Создаётся при первом доступе │ Создаётся DI-контейнером           │
│ Живёт вечно                  │ Живёт в scope (app, activity, ...)│
└──────────────────────────────┴────────────────────────────────────┘
```

---

## Антипаттерны Singleton

### God Object Singleton

```kotlin
// Всё в одном object --- нарушает SRP, OCP, и здравый смысл
object AppManager {
    fun login(email: String, password: String) { /* ... */ }
    fun logout() { /* ... */ }
    fun fetchProducts() { /* ... */ }
    fun addToCart(item: Item) { /* ... */ }
    fun checkout() { /* ... */ }
    fun sendNotification(msg: String) { /* ... */ }
    fun updateTheme(theme: Theme) { /* ... */ }
    fun clearCache() { /* ... */ }
    // ... 200 методов
}
```

### Singleton вместо DI

```kotlin
// Не делайте так:
class UserViewModel : ViewModel() {
    // Прямые обращения к singleton --- невозможно тестировать
    private val repo = UserRepository  // object
    private val api = ApiClient        // object
    private val cache = AppCache       // object
    private val analytics = Analytics  // object
}
```

### Мутабельный singleton без синхронизации

```kotlin
// Race condition гарантирован:
object SessionManager {
    var currentSession: Session? = null  // ← кто угодно может записать
    var tokens = mutableMapOf<String, String>() // ← не потокобезопасно
}
```

---

## Проверь себя

> [!question]- Как Kotlin `object` обеспечивает потокобезопасность singleton без synchronized?
> Компилятор генерирует класс с `static final INSTANCE` полем, инициализируемым в `static {}` блоке. JVM гарантирует, что static initializer выполняется ровно один раз, атомарно, при первой загрузке класса. Это тот же механизм, который делает enum-singleton Блоха потокобезопасным --- без `volatile`, `synchronized` или double-checked locking.

> [!question]- Почему `object` потокобезопасен для создания экземпляра, но не для мутабельных данных внутри?
> `object` гарантирует единственность экземпляра (через static initializer), но `var count = 0` и `count++` внутри `object` --- это обычные операции чтения-записи без синхронизации. Для защиты нужно: `AtomicInteger` для примитивов, `Mutex` для корутин, `ConcurrentHashMap` для коллекций, или `@Synchronized` для методов.

> [!question]- Когда `object` оправдан, а когда лучше DI singleton scope?
> `object` оправдан для: stateless-утилит (pure functions), констант, sealed class companions, именованных реализаций интерфейсов без зависимостей. DI singleton scope лучше для: stateful-сервисов, классов с внешними зависимостями, всего, что нужно тестировать и подменять mock-ами. Ключевой критерий: если есть зависимости или мутабельное состояние --- DI.

> [!question]- Назовите 3 причины, почему Singleton считают антипаттерном.
> (1) **Скрытые зависимости**: `UserRepository.findById()` не видно в конструкторе класса. (2) **Сложность тестирования**: нельзя подменить singleton mock-ом без рефлексии. (3) **Глобальное мутабельное состояние**: любой код может изменить данные в singleton, отладка race conditions практически невозможна. Дополнительно: нарушение SRP (класс управляет и логикой, и своим жизненным циклом).

> [!question]- Чем `companion object` отличается от `object` и в чём его связь с Factory Method?
> `object` --- standalone singleton. `companion object` --- singleton, привязанный к классу, доступный через `ClassName.method()`. Companion object часто используется как Factory Method: приватный конструктор класса + публичные фабричные методы в companion (`User.fromEmail()`, `User.guest()`). В отличие от Java static, companion может реализовывать интерфейсы.

---

## Ключевые карточки

Как Kotlin `object` реализован на уровне байткода?
?
Компилятор генерирует Java-класс с: (1) `public static final INSTANCE` полем, (2) приватным конструктором, (3) `static {}` блоком, который создаёт экземпляр. JVM гарантирует потокобезопасность и ленивую инициализацию (при первой загрузке класса). Эквивалент enum-singleton из "Effective Java".

Какие три режима `lazy {}` существуют в Kotlin?
?
`SYNCHRONIZED` (default) --- потокобезопасный, с lock, один поток вычисляет. `NONE` --- без синхронизации, быстрее, только для однопоточного кода. `PUBLICATION` --- несколько потоков могут вычислить параллельно, но все увидят одно и то же значение (первое успешное).

Почему Singleton нарушает SRP?
?
Класс отвечает за две вещи: (1) бизнес-логику и (2) контроль собственного создания (один экземпляр). В DI-подходе создание и lifecycle управляется контейнером, а класс занимается только своей основной задачей.

Когда `object` предпочтительнее DI singleton scope?
?
Для stateless-утилит (pure functions), констант (`const val`), sealed class companions (`data object Loading`), именованных реализаций интерфейсов без зависимостей. Если у объекта нет мутабельного состояния и внешних зависимостей --- `object` проще и не требует DI-инфраструктуры.

Как защитить мутабельные данные внутри `object`?
?
`AtomicInteger`/`AtomicReference` для примитивов и ссылок. `Mutex().withLock { }` для suspend-функций в корутинах. `ConcurrentHashMap` для потокобезопасных коллекций. `@Synchronized` на методах как простое решение (но блокирует весь метод). `object` гарантирует один экземпляр, но не синхронизацию операций с данными.

Чем DI singleton scope лучше классического Singleton?
?
(1) Зависимости явные (через конструктор), видны при чтении кода. (2) Легко тестировать --- подменяем через конструктор или DI-модуль. (3) Lifecycle управляется контейнером (app scope, activity scope). (4) Нет глобального состояния --- DI может создать отдельный scope для каждого теста.

В чём разница между `object` и `companion object`?
?
`object` --- standalone singleton, обращение по имени: `DatabasePool.getConnection()`. `companion object` --- singleton внутри класса, обращение через класс: `User.create()`. Companion может реализовывать интерфейсы. В байткоде оба --- класс с `INSTANCE`, но companion вложен в родительский класс.

Почему double-checked locking в Java был проблемой?
?
До Java 5 (без `volatile`) JVM могла переупорядочить инструкции: поток A видел не-null ссылку на полуинициализированный объект. Нужны `volatile` + `synchronized` + две проверки null. В Kotlin `object` решает это через static initializer, а `lazy {}` --- через `SYNCHRONIZED` режим по умолчанию. Вся сложность спрятана в компиляторе.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Обзор | [[design-patterns-overview]] | Классификация всех паттернов, Kotlin-замены |
| Creational | [[factory-pattern]] | `companion object` как фабрика --- мост от Singleton к Factory |
| DI | [[android-dependency-injection]] | Hilt, Koin --- как DI заменяет Singleton в Android |
| Kotlin | [[kotlin-oop]] | `object`, `companion object`, delegation `by` |
| Concurrency | [[kotlin-coroutines-fundamentals]] | `Mutex`, `StateFlow` --- потокобезопасность в корутинах |

---

## Источники

- Gamma E., Helm R., Johnson R., Vlissides J. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software* --- оригинальное описание паттерна Singleton
- Bloch J. (2018). *Effective Java*, 3rd ed. --- Item 3: Enforce the singleton property with a private constructor or an enum type
- Moskala M. (2021). *Effective Kotlin* --- рекомендации по `object`, `companion object` и factory functions
- [Kotlin Docs: Object Declarations](https://kotlinlang.org/docs/object-declarations.html) --- официальная документация `object` и `companion object`
- [Baeldung: Singleton Classes in Kotlin](https://www.baeldung.com/kotlin/singleton-classes) --- обзор реализаций с bytecode-анализом
- [Internals of object class - Singleton in Kotlin](https://outcomeschool.substack.com/p/internals-of-object-class-singleton) --- деcompiled bytecode и JVM-гарантии
- [Singleton vs Dependency Injection](https://enterprisecraftsmanship.com/posts/singleton-vs-dependency-injection/) --- сравнение подходов
- [The Problems with Singletons and Why You Should Use DI](https://medium.com/@fatihcyln/the-problems-with-singletons-and-why-you-should-use-di-instead-5a0fa0a5baed) --- критика Singleton

---

*Проверено: 2026-02-19*
