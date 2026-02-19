---
title: "Decorator: добавление поведения через делегирование"
created: 2026-02-19
modified: 2026-02-19
type: concept
tags:
  - topic/programming
  - topic/design-patterns
  - topic/kotlin
  - pattern/structural
related:
  - "[[design-patterns-overview]]"
  - "[[adapter-pattern]]"
  - "[[composition-vs-inheritance]]"
  - "[[solid-principles]]"
  - "[[kotlin-oop]]"
---

# Decorator: добавление поведения через делегирование

В Java Decorator — это 50 строк forwarding-методов ради одного `log.debug()`. В Kotlin одно слово `by` заменяет весь этот boilerplate: компилятор генерирует forwarding за тебя, а ты пишешь только то поведение, которое хочешь добавить. Но у `by` есть ловушка, о которой молчат туториалы — делегат не видит твои переопределения.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Decorator** | Объект-обёртка с тем же интерфейсом, добавляющий поведение |
| **Component** | Общий интерфейс для декорируемого объекта и декоратора |
| **Delegate** | Объект, которому делегируется реализация |
| **Class delegation (`by`)** | Языковая конструкция Kotlin: компилятор генерирует forwarding-методы |
| **Forwarding method** | Метод, который просто вызывает такой же метод на делегате |
| **Stacking** | Оборачивание декоратора в другой декоратор — цепочка обёрток |

---

## Проблема: поведение без модификации класса

Есть `UserRepository` — работает с базой. Нужно добавить логирование. Потом кеширование. Потом метрики. Менять исходный класс нельзя — он из другой команды, или из библиотеки, или просто нарушишь Single Responsibility.

Наследование? Для каждой комбинации — отдельный класс:

```
UserRepository
├── LoggingUserRepository
├── CachingUserRepository
├── MetricsUserRepository
├── LoggingCachingUserRepository        // 2^n комбинаций
├── LoggingMetricsUserRepository
├── CachingMetricsUserRepository
└── LoggingCachingMetricsUserRepository // комбинаторный взрыв
```

Три аспекта = 7 классов. Четыре = 15. Это **комбинаторный взрыв** — классическая проблема, которую Decorator решает через композицию.

---

## Классический Decorator (GoF)

### Структура

```
┌─────────────────────────────────────────────────────────────┐
│                       DECORATOR                             │
├─────────────────────────────────────────────────────────────┤
│   Component (interface)                                     │
│   └── operation()                                           │
│          ↑                                                  │
│   ┌──────┴───────────┐                                      │
│   │                  │                                      │
│   ConcreteComponent  Decorator (abstract)                   │
│   operation()        ├── component: Component               │
│                      └── operation() {                      │
│                            component.operation()            │
│                          }                                  │
│                               ↑                             │
│                      ┌────────┴────────┐                    │
│                      │                 │                    │
│               ConcreteDecoratorA  ConcreteDecoratorB        │
│               operation() {      operation() {              │
│                 addedBehavior()    super.operation()         │
│                 super.operation()  addedBehavior()           │
│               }                  }                          │
└─────────────────────────────────────────────────────────────┘
```

### Participants

| Компонент | Роль | Пропустишь — сломаешь |
|-----------|------|----------------------|
| **Component** | Общий интерфейс | Без него декоратор несовместим с оригиналом |
| **ConcreteComponent** | Базовый объект | То, что оборачиваем |
| **Decorator** | Абстрактный декоратор, хранит ссылку и делегирует | **Ключевой!** Связывает цепочку |
| **ConcreteDecorator** | Добавляет конкретное поведение | Реальное расширение функциональности |

### Java boilerplate: проблема forwarding

```kotlin
// Java-стиль: нужно руками переадресовать ВСЕ методы интерфейса
interface UserRepository {
    fun findById(id: Long): User?
    fun findAll(): List<User>
    fun save(user: User): User
    fun delete(id: Long)
    fun count(): Long
    fun existsById(id: Long): Boolean
}

// Декоратор в Java-стиле — переадресовка всех 6 методов
class LoggingUserRepository(
    private val delegate: UserRepository
) : UserRepository {

    override fun findById(id: Long): User? {
        log.debug("findById($id)")         // <-- единственное добавление
        return delegate.findById(id)        // forwarding
    }

    override fun findAll(): List<User> {
        log.debug("findAll()")
        return delegate.findAll()           // forwarding
    }

    override fun save(user: User): User {
        log.debug("save($user)")
        return delegate.save(user)          // forwarding
    }

    override fun delete(id: Long) {
        log.debug("delete($id)")
        delegate.delete(id)                 // forwarding
    }

    override fun count(): Long {
        log.debug("count()")
        return delegate.count()             // forwarding
    }

    override fun existsById(id: Long): Boolean {
        log.debug("existsById($id)")
        return delegate.existsById(id)      // forwarding
    }
}
// 40+ строк, из которых 80% — механический boilerplate
```

Добавишь метод в интерфейс — забудешь обновить декоратор — **тихий баг** (метод вызовется без логирования).

---

## Kotlin `by`: одна строка вместо forwarding

> [!info] Kotlin-нюанс
> Ключевое слово `by` говорит компилятору: «сгенерируй все forwarding-методы автоматически». Ты переопределяешь только те, которые хочешь изменить.

```kotlin
class LoggingUserRepository(
    private val delegate: UserRepository
) : UserRepository by delegate {

    // Переопределяем ТОЛЬКО то, что нужно
    override fun findById(id: Long): User? {
        log.debug("Finding user $id")
        return delegate.findById(id)
    }

    override fun save(user: User): User {
        log.debug("Saving user ${user.name}")
        val saved = delegate.save(user)
        log.debug("Saved with id ${saved.id}")
        return saved
    }

    // findAll(), delete(), count(), existsById() — автоматически делегируются
}
```

**Что изменилось:** 6 строк forwarding исчезли. Добавишь новый метод в `UserRepository` — он автоматически делегируется. Не нужно помнить про обновление декоратора.

### Что компилятор генерирует

Декомпилированный байткод `UserRepository by delegate` эквивалентен:

```kotlin
// Компилятор генерирует в bytecode (можно посмотреть через Show Kotlin Bytecode):
class LoggingUserRepository(private val delegate: UserRepository) : UserRepository {

    // Сгенерированные forwarding-методы:
    override fun findAll(): List<User> = delegate.findAll()
    override fun delete(id: Long) = delegate.delete(id)
    override fun count(): Long = delegate.count()
    override fun existsById(id: Long): Boolean = delegate.existsById(id)

    // Явно переопределённые — остаются как есть:
    override fun findById(id: Long): User? { /* твой код */ }
    override fun save(user: User): User { /* твой код */ }
}
```

Это **не рефлексия и не proxy** — прямые вызовы в bytecode. После JIT-компиляции производительность идентична ручному forwarding.

> [!tip] Как проверить
> IntelliJ IDEA: Tools > Kotlin > Show Kotlin Bytecode > Decompile. Увидишь все сгенерированные методы.

---

## Stacking декораторов: цепочка обёрток

Вся мощь Decorator — в композиции. Каждая обёртка добавляет ровно один аспект:

```kotlin
// Логирование
class LoggingRepository(
    private val delegate: UserRepository
) : UserRepository by delegate {
    override fun findById(id: Long): User? {
        log.debug("findById($id)")
        return delegate.findById(id).also { log.debug("Result: $it") }
    }
}

// Кеширование
class CachingRepository(
    private val delegate: UserRepository,
    private val cache: Cache<Long, User> = ConcurrentHashMap()
) : UserRepository by delegate {
    override fun findById(id: Long): User? {
        return cache.getOrPut(id) { delegate.findById(id) }
    }

    override fun save(user: User): User {
        return delegate.save(user).also { cache[it.id] = it }
    }

    override fun delete(id: Long) {
        cache.remove(id)
        delegate.delete(id)
    }
}

// Метрики
class MetricsRepository(
    private val delegate: UserRepository,
    private val metrics: MeterRegistry
) : UserRepository by delegate {
    override fun findById(id: Long): User? {
        return metrics.timer("repo.findById").recordCallable {
            delegate.findById(id)
        }
    }
}
```

**Сборка — одна строка:**

```kotlin
val repo: UserRepository = LoggingRepository(
    CachingRepository(
        MetricsRepository(
            DatabaseUserRepository(dataSource)
        )
    )
)

// Порядок важен! Вызов repo.findById(1):
// 1. LoggingRepository  → логирует запрос
// 2. CachingRepository  → проверяет кеш
// 3. MetricsRepository  → замеряет время
// 4. DatabaseRepository → идёт в БД (если кеш промахнулся)
```

```
┌──────────────────────────────────────────────────┐
│  Клиент                                          │
│     │                                            │
│     ▼                                            │
│  LoggingRepository ──by──> CachingRepository     │
│                              │                   │
│                           ──by──>                │
│                          MetricsRepository        │
│                              │                   │
│                           ──by──>                │
│                          DatabaseRepository       │
│                              │                   │
│                           ──> PostgreSQL          │
└──────────────────────────────────────────────────┘
```

Нужно убрать кеширование — убери одну обёртку. Нужно добавить аудит — добавь одну обёртку. Ни один существующий класс не меняется (**Open/Closed Principle**).

---

## Extension functions как «лёгкий декоратор»

> [!info] Kotlin-нюанс
> Когда нужно добавить один метод, а не оборачивать весь интерфейс — extension function проще и дешевле.

```kotlin
// Не нужен целый декоратор — достаточно extension
fun UserRepository.findByIdOrThrow(id: Long): User =
    findById(id) ?: throw UserNotFoundException(id)

fun UserRepository.findAllActive(): List<User> =
    findAll().filter { it.isActive }

// Использование — как будто методы были в интерфейсе
val user = repo.findByIdOrThrow(42)
val active = repo.findAllActive()
```

### Когда extension, когда Decorator?

| Критерий | Extension function | Decorator (`by`) |
|----------|-------------------|------------------|
| Добавить метод | Да | Overkill |
| Изменить существующий метод | Нет (не переопределяет) | Да |
| Стековать поведение | Нет | Да |
| Доступ к private state | Нет | Нет (тоже нет!) |
| Новое поведение в runtime | Нет (compile-time) | Да |

**Правило:** extension function = добавить новый метод. Decorator = изменить или дополнить существующие.

---

## Ловушка: делегат не видит переопределений

Это самая коварная особенность `by` в Kotlin. Делегат вызывает свои собственные реализации, а не переопределённые версии в декораторе.

```kotlin
interface Printer {
    fun header(): String
    fun body(): String
    fun print() // вызывает header() + body()
}

class BasicPrinter : Printer {
    override fun header() = "=== HEADER ==="
    override fun body() = "content"
    override fun print() {
        // Внутри BasicPrinter: вызывает СВОИ header() и body()
        println(header())
        println(body())
    }
}

class FancyPrinter(
    private val delegate: Printer
) : Printer by delegate {
    // Переопределяем header
    override fun header() = "*** FANCY HEADER ***"
}

fun main() {
    val printer = FancyPrinter(BasicPrinter())

    printer.header()  // "*** FANCY HEADER ***" — OK, прямой вызов
    printer.print()   // Выведет "=== HEADER ===" — СЮРПРИЗ!
                      // print() вызывается на delegate (BasicPrinter),
                      // который вызывает СВОЙ header(), не FancyPrinter.header()
}
```

**Почему так:** `by delegate` генерирует `fun print() = delegate.print()`. Внутри `delegate.print()` вызов `header()` идёт через `this` делегата — а это `BasicPrinter`, не `FancyPrinter`. Делегат ничего не знает о декораторе.

> [!warning] Это отличается от наследования!
> При наследовании `override fun header()` в подклассе виден через полиморфизм (`this` указывает на подкласс). При делегации `by` — нет. Это **by design**, не баг.

### Как обойти

Если нужно, чтобы внутренние вызовы видели переопределения — используй явную композицию вместо `by`:

```kotlin
class FancyPrinter(private val delegate: Printer) : Printer {
    override fun header() = "*** FANCY HEADER ***"
    override fun body() = delegate.body()
    override fun print() {
        // Теперь вызываем СВОЙ header()
        println(header())   // "*** FANCY HEADER ***"
        println(body())
    }
}
```

---

## Когда `by` не работает

### 1. Только интерфейсы, не abstract class

```kotlin
abstract class AbstractRepo {
    abstract fun findAll(): List<User>
    fun count() = findAll().size  // конкретный метод
}

// ❌ Нельзя: class Wrapper(r: AbstractRepo) : AbstractRepo by r
// by работает ТОЛЬКО с интерфейсами
```

### 2. Нет доступа к private state делегата

```kotlin
class DatabaseRepository : UserRepository {
    private val connectionPool = HikariPool(config)  // private!
    // ...
}

class LoggingRepository(
    private val delegate: UserRepository
) : UserRepository by delegate {
    // Нет доступа к delegate.connectionPool
    // Декоратор видит делегат только через интерфейс
}
```

### 3. Множественная делегация — конфликты

```kotlin
interface A { fun foo(): String }
interface B { fun foo(): String }

class MyClass(a: A, b: B) : A by a, B by b {
    // ❌ Ошибка компиляции: Class 'MyClass' must override 'foo'
    // Два делегата реализуют один метод — нужно выбрать явно
    override fun foo(): String = "resolved"
}
```

---

## Real-world примеры

### OkHttp Interceptors — цепочка декораторов

OkHttp `Interceptor` — классический Decorator. Каждый перехватчик оборачивает следующий через `chain.proceed()`:

```kotlin
class AuthInterceptor(
    private val tokenProvider: () -> String
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer ${tokenProvider()}")
            .build()
        return chain.proceed(request)  // передаём дальше по цепочке
    }
}

class LoggingInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        log.debug("→ ${request.method} ${request.url}")

        val response = chain.proceed(request)

        log.debug("← ${response.code} (${response.body?.contentLength()} bytes)")
        return response
    }
}

// Стекинг при создании клиента
val client = OkHttpClient.Builder()
    .addInterceptor(AuthInterceptor { getToken() })
    .addInterceptor(LoggingInterceptor())
    .addInterceptor(RetryInterceptor(maxRetries = 3))
    .build()
```

### InputStream wrappers — стандартная библиотека

```kotlin
// Java IO — классический пример Decorator из GoF
val input: InputStream = BufferedInputStream(   // буферизация
    GZIPInputStream(                            // распаковка
        FileInputStream("data.gz")              // чтение файла
    )
)

// Kotlin-идиоматичный вариант с extension functions
File("data.gz").inputStream()
    .let(::GZIPInputStream)
    .buffered()
    .reader()
    .useLines { lines ->
        lines.filter { it.isNotBlank() }.toList()
    }
```

### Repository logging/caching в Android

```kotlin
// Типичная архитектура Android Clean Architecture
interface ArticleRepository {
    suspend fun getArticles(): List<Article>
    suspend fun getArticle(id: ArticleId): Article?
    suspend fun saveArticle(article: Article)
}

// Сетевой источник
class RemoteArticleRepository(
    private val api: ArticleApi
) : ArticleRepository {
    override suspend fun getArticles() = api.fetchArticles().toDomain()
    override suspend fun getArticle(id: ArticleId) = api.fetchArticle(id.value).toDomain()
    override suspend fun saveArticle(article: Article) = api.postArticle(article.toDto())
}

// Offline-first декоратор
class OfflineFirstRepository(
    private val remote: ArticleRepository,
    private val local: ArticleDao
) : ArticleRepository by remote {

    override suspend fun getArticles(): List<Article> {
        return try {
            remote.getArticles().also { articles ->
                local.insertAll(articles)  // кешируем
            }
        } catch (e: IOException) {
            local.getAll()  // fallback на локальные данные
        }
    }
}
```

---

## Decorator vs Наследование vs Extension

```
┌──────────────────────────────────────────────────────────────────┐
│                    СРАВНЕНИЕ ПОДХОДОВ                             │
├──────────────┬──────────────┬──────────────┬─────────────────────┤
│ Критерий     │ Наследование │ Decorator by │ Extension function  │
├──────────────┼──────────────┼──────────────┼─────────────────────┤
│ Когда        │ Compile-time │ Runtime      │ Compile-time        │
│ Стекинг      │ Нет          │ Да           │ Нет                 │
│ Комбинации   │ 2^n классов  │ n классов    │ n функций           │
│ Open/Closed  │ Нарушает     │ Соблюдает    │ Соблюдает           │
│ Ограничения  │ Только open  │ Только       │ Нет доступа к       │
│              │ классы       │ интерфейсы   │ private             │
│ Overhead     │ Нет          │ +1 объект    │ Нет                 │
│              │              │ на обёртку   │                     │
│ self-problem │ Нет          │ Да           │ Не применимо        │
└──────────────┴──────────────┴──────────────┴─────────────────────┘
```

---

## Anti-patterns

### 1. Decorator с логикой, не связанной с декорированием

```kotlin
// ❌ Плохо: декоратор занимается трансформацией данных
class TransformingRepository(
    private val delegate: UserRepository
) : UserRepository by delegate {
    override fun findById(id: Long): User? {
        val user = delegate.findById(id)
        // Это НЕ декорирование — это бизнес-логика
        return user?.copy(
            name = user.name.uppercase(),
            email = user.email.lowercase()
        )
    }
}

// ✅ Лучше: вынести трансформацию в отдельный слой (UseCase/Service)
class NormalizeUserUseCase(private val repo: UserRepository) {
    suspend fun execute(id: Long): User? =
        repo.findById(id)?.let(::normalize)
}
```

### 2. Слишком глубокая цепочка

```kotlin
// ❌ Плохо: 7 уровней вложенности — дебаг превращается в ад
val repo = AuditRepository(
    RetryRepository(
        TimeoutRepository(
            LoggingRepository(
                CachingRepository(
                    MetricsRepository(
                        ValidationRepository(
                            DatabaseRepository()
                        )))))))

// ✅ Лучше: ограничь до 3-4 слоёв, или используй другой паттерн
// (например, middleware pipeline или AOP)
```

---

## Проверь себя

> [!question]- Какую проблему решает Decorator? Почему не наследование?
> Decorator решает проблему добавления поведения к объекту без изменения его класса. Наследование приводит к комбинаторному взрыву: для n аспектов нужно 2^n классов. Decorator = n классов, которые можно комбинировать в runtime через стекинг.

> [!question]- Что именно генерирует компилятор Kotlin для `by delegate`?
> Компилятор генерирует обычные forwarding-методы в bytecode: для каждого метода интерфейса создаётся метод, который просто вызывает `delegate.метод()`. Это не рефлексия и не proxy — прямые вызовы. Явно переопределённые методы остаются как есть и не генерируются.

> [!question]- В чём ловушка `by` — почему делегат не видит переопределений?
> При `by delegate` вызов внутри делегата (например, `print()` вызывает `header()`) идёт через `this` делегата, а не декоратора. Делегат ничего не знает об обёртке. Это отличается от наследования, где `this` в подклассе полиморфен. Решение: если внутренние вызовы должны видеть переопределения — используй явную композицию или наследование.

> [!question]- Когда extension function лучше Decorator?
> Когда нужно добавить новый метод (не изменить существующий), не нужен стекинг, и достаточно compile-time решения. Extension дешевле — нет объекта-обёртки. Decorator нужен когда хочешь изменить поведение существующего метода и/или стековать несколько аспектов в runtime.

> [!question]- Почему `by` работает только с интерфейсами?
> Интерфейс определяет контракт — набор методов, которые можно безопасно делегировать. Abstract class содержит состояние и конкретные методы, которые могут зависеть от internal state. Делегирование abstract class нарушило бы инкапсуляцию — декоратор не имеет доступа к protected/private полям.

---

## Ключевые карточки

Что такое Decorator и какую проблему решает?
?
Структурный паттерн: объект-обёртка с тем же интерфейсом, добавляющая поведение. Решает проблему расширения без модификации (Open/Closed Principle). Вместо 2^n классов при наследовании — n декораторов, которые стекуются в любых комбинациях.

Как Kotlin `by` упрощает Decorator?
?
`class Wrapper(d: Interface) : Interface by d` — компилятор генерирует все forwarding-методы автоматически. Переопределяешь только то, что нужно изменить. Новые методы в интерфейсе автоматически делегируются без изменения декоратора.

В чём self-problem при делегировании `by`?
?
Делегат не видит переопределённые методы декоратора. Если `delegate.print()` внутри вызывает `header()`, будет вызван `delegate.header()`, а не `decorator.header()`. Причина: `this` внутри делегата — сам делегат, не обёртка. Отличие от наследования, где полиморфизм работает.

Какие ограничения у `by` в Kotlin?
?
Три ограничения: (1) только интерфейсы, не abstract class; (2) нет доступа к private state делегата; (3) при множественной делегации конфликтные методы нужно разрешать явно. Плюс self-problem: делегат не видит override-ы.

Чем extension function отличается от Decorator?
?
Extension добавляет новый метод — compile-time, без обёртки. Decorator изменяет/дополняет существующие методы — runtime, с объектом-обёрткой. Extension нельзя стековать, Decorator можно. Extension не имеет доступа к private (Decorator тоже, но видит результат через интерфейс).

Как OkHttp Interceptor реализует Decorator?
?
Каждый Interceptor оборачивает `chain.proceed(request)` — может модифицировать request до и response после. Перехватчики стекуются: Auth → Logging → Retry → Network. Добавление/удаление аспекта = добавление/удаление одного interceptor.

Когда Decorator — антипаттерн?
?
Когда: (1) декоратор содержит бизнес-логику вместо cross-cutting concern; (2) цепочка глубже 4-5 уровней — дебаг становится кошмаром; (3) один декоратор для одного применения — проще вызвать напрямую. Decorator оправдан для стекируемых аспектов: логирование, кеширование, метрики, retry.

Как стекуются декораторы и почему порядок важен?
?
`Logging(Caching(Metrics(Database())))` — вызов идёт снаружи внутрь: сначала логирование (видит все запросы), потом кеш (может не пустить дальше), потом метрики (замеряет только cache miss), потом БД. Изменение порядка меняет поведение: если кеш перед логированием — cache hit не залогируется.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Смежный паттерн | [[adapter-pattern]] | Adapter тоже оборачивает, но меняет интерфейс, а не поведение |
| Смежный паттерн | [[design-patterns-overview]] | Контекст: место Decorator среди 23 GoF-паттернов |
| Фундамент | [[solid-principles]] | Open/Closed Principle — теоретическая основа Decorator |
| Kotlin-глубже | [[kotlin-oop]] | Delegation `by`, sealed class, companion object |
| Альтернатива | [[composition-vs-inheritance]] | Почему GoF советует «prefer composition over inheritance» |
| Android | [[android-clean-architecture]] | Decorator для обёртки Repository (кэширование, логирование) |

---

## Источники

### Первоисточники
- Gamma E., Helm R., Johnson R., Vlissides J. *Design Patterns: Elements of Reusable Object-Oriented Software* (1994) — оригинальное описание Decorator (Chapter 4: Structural Patterns)
- Bloch J. *Effective Java*, 3rd Edition (2018) — Item 18: "Favor composition over inheritance"

### Kotlin-специфичные
- Moskala M. *Effective Kotlin* (2021) — Item 36: "Prefer composition over inheritance", interface delegation
- [Kotlin Documentation: Delegation](https://kotlinlang.org/docs/delegation.html) — официальная документация по `by`
- [Kotlin Academy: Interface Delegation](https://kt.academy/article/ak-interface-delegation) — глубокий разбор с примерами и ловушками
- [Baeldung: Decorator Pattern in Kotlin](https://www.baeldung.com/kotlin/decorator-pattern) — сравнение классического и `by`-подхода
- [Baeldung: Delegation Pattern in Kotlin](https://www.baeldung.com/kotlin/delegation-pattern) — детальный разбор delegation
- [Manning: Compiler-Generated Methods](https://freecontent.manning.com/compiler-generated-methods-data-classes-and-class-delegation/) — что именно генерирует компилятор

### Статьи и туториалы
- [Ioannis Anifantakis: Decorator Pattern in Kotlin — Embracing Open/Closed Principle](https://itnext.io/decorator-pattern-in-kotlin-embracing-open-closed-principle-b469adc2ab7b) — практический разбор с OCP
- [Adam Swiderski: Decorator Pattern in Kotlin](https://swiderski.tech/kotlin-decorator-pattern/) — gotchas и bytecode анализ
- [zsmb.co: Effective Class Delegation](https://zsmb.co/effective-class-delegation/) — продвинутые техники и подводные камни
- [Lucas Fugisawa: Kotlin Design Patterns — Simplifying the Decorator](https://fugisawa.com/kotlin-design-patterns-simplifying-the-decorator-pattern/) — упрощение через Kotlin-идиомы

### Real-world
- [OkHttp: Interceptors](https://square.github.io/okhttp/features/interceptors/) — Decorator в production (Chain of Responsibility + Decorator)
- [Refactoring Guru: Decorator](https://refactoring.guru/design-patterns/decorator) — визуальный справочник с UML

---

*Проверено: 2026-02-19*
