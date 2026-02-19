---
title: "Builder: пошаговое создание сложных объектов"
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
  - "[[kotlin-advanced-features]]"
  - "[[dry-kiss-yagni]]"
---

# Builder: пошаговое создание сложных объектов

В Java Builder --- обязательный паттерн для объектов с 5+ параметрами (Effective Java, Item 2). В Kotlin **named parameters + default values** закрывают 80% случаев, превращая классический Builder в рудимент. Но оставшиеся 20% --- DSL-билдеры, type-safe builders для Ktor/Compose/Gradle --- делают этот паттерн **мощнее**, чем в любом другом JVM-языке. Builder в Kotlin не умер: он эволюционировал.

---

## Проблема: телескопические конструкторы

Представь, что ты заказываешь кастомный компьютер. У тебя 15 параметров: процессор, видеокарта, RAM, диск, корпус, блок питания, охлаждение... Передавать их все в одну строку --- путь к ошибке.

```kotlin
// Java-style: "телескопические конструкторы"
// Что здесь второй параметр? А пятый?
val server = Server(
    "prod-01",     // hostname? или datacenter?
    8080,          // port? или maxConnections?
    true,          // ssl? или logging?
    4,             // threads? или retryCount?
    30_000,        // timeout? или keepAlive?
    null,          // что это вообще?
    null,
    "us-east-1"
)
```

**Три классические проблемы:**
1. **Нечитаемость** --- порядок параметров легко перепутать
2. **Хрупкость** --- добавление нового параметра ломает все вызовы
3. **Null-засорение** --- необязательные параметры требуют `null` заглушек

---

## Классический Builder: Bloch's Effective Java Item 2

Решение Джошуа Блоха --- выделить процесс создания в отдельный объект:

```
+---------------------------------------------------------+
|                     BUILDER (GoF)                       |
+---------------------------------------------------------+
|   Director                    Builder (interface)       |
|   +-- builder: Builder        +-- buildPartA()          |
|   +-- construct() {           +-- buildPartB()          |
|         builder.buildPartA()  +-- getResult(): Product  |
|         builder.buildPartB()          |                 |
|       }                       ConcreteBuilder           |
|                               +-- product: Product      |
|                               +-- getResult()           |
+---------------------------------------------------------+
```

### Java-стиль Builder (verbose)

```kotlin
// Так писали до Kotlin --- и до сих пор пишут в Java-библиотеках
class ServerConfig private constructor(
    val hostname: String,
    val port: Int,
    val ssl: Boolean,
    val maxThreads: Int,
    val timeout: Long,
    val datacenter: String?
) {
    class Builder {
        private var hostname: String = "localhost"
        private var port: Int = 8080
        private var ssl: Boolean = false
        private var maxThreads: Int = 4
        private var timeout: Long = 30_000
        private var datacenter: String? = null

        fun hostname(value: String) = apply { hostname = value }
        fun port(value: Int) = apply { port = value }
        fun ssl(value: Boolean) = apply { ssl = value }
        fun maxThreads(value: Int) = apply { maxThreads = value }
        fun timeout(value: Long) = apply { timeout = value }
        fun datacenter(value: String?) = apply { datacenter = value }

        fun build(): ServerConfig {
            require(hostname.isNotBlank()) { "Hostname must not be blank" }
            require(port in 1..65535) { "Port must be in range 1..65535" }
            return ServerConfig(hostname, port, ssl, maxThreads, timeout, datacenter)
        }
    }
}

// Использование: читается хорошо, но сколько кода ради этого?
val config = ServerConfig.Builder()
    .hostname("prod-01")
    .port(443)
    .ssl(true)
    .maxThreads(16)
    .build()
```

**40+ строк boilerplate** для 6 параметров. Каждый новый параметр --- ещё 3-4 строки.

---

## Kotlin заменяет Builder: три механизма

### Механизм 1: Named parameters + default values (основной)

```kotlin
// Вся мощь Builder --- в одном объявлении класса
data class ServerConfig(
    val hostname: String = "localhost",
    val port: Int = 8080,
    val ssl: Boolean = false,
    val maxThreads: Int = 4,
    val timeout: Long = 30_000,
    val datacenter: String? = null
) {
    init {
        require(hostname.isNotBlank()) { "Hostname must not be blank" }
        require(port in 1..65535) { "Port must be in range 1..65535" }
    }
}

// Использование: именованные параметры = самодокументирующийся код
val config = ServerConfig(
    hostname = "prod-01",
    port = 443,
    ssl = true,
    maxThreads = 16
    // datacenter и timeout --- defaults
)
```

> [!info] Kotlin-нюанс
> Named parameters решают все три проблемы телескопического конструктора: параметры именованы (читаемость), порядок не важен (хрупкость), дефолты заменяют null (засорение). **6 строк вместо 40+.**

### Механизм 2: `copy()` на data class (иммутабельная модификация)

```kotlin
// Базовая конфигурация
val defaultConfig = ServerConfig(hostname = "default")

// "Модификация" без мутации --- создаём новый объект
val prodConfig = defaultConfig.copy(
    hostname = "prod-01",
    port = 443,
    ssl = true
)

val stagingConfig = defaultConfig.copy(
    hostname = "staging-01",
    maxThreads = 8
)

// defaultConfig не изменился!
println(defaultConfig.hostname) // "default"
println(prodConfig.hostname)    // "prod-01"
```

**Когда это полезно:**
- Конфигурация "по шаблону" с вариациями
- Immutable updates в state management
- Тесты: базовый объект + варианты

### Механизм 3: `apply {}` scope function (инициализация мутабельного объекта)

```kotlin
// Когда объект не data class и у него нет конструктора со всеми параметрами
class EmailMessage {
    var from: String = ""
    var to: String = ""
    var subject: String = ""
    var body: String = ""
    var isHtml: Boolean = false
    val attachments: MutableList<Attachment> = mutableListOf()

    fun addAttachment(file: Attachment) {
        attachments.add(file)
    }
}

// apply {} --- "билдер" одной строкой
val email = EmailMessage().apply {
    from = "noreply@example.com"
    to = "user@example.com"
    subject = "Confirmation"
    body = "<h1>Hello!</h1>"
    isHtml = true
    addAttachment(Attachment("invoice.pdf"))
}
```

> [!info] Kotlin-нюанс
> `apply {}` --- это не замена Builder, а инициализатор. Разница: Builder валидирует при `build()`, `apply {}` --- нет. Для объектов с инвариантами лучше named parameters + `init {}`.

---

## Сравнение: Java Builder vs Kotlin подходы

```
+-----------------------------------------------------------------+
|              Java Builder    |   Kotlin named params             |
+-----------------------------------------------------------------+
|  class Builder {             |   data class Config(              |
|    var host = ""             |       val host: String = "",      |
|    var port = 8080           |       val port: Int = 8080,       |
|    fun host(v) = apply {..} |       val ssl: Boolean = false    |
|    fun port(v) = apply {..} |   )                               |
|    fun ssl(v) = apply {..}  |                                   |
|    fun build() = Config(..) |   // Использование:               |
|  }                           |   Config(host = "prod", ssl = true)|
|                              |                                   |
|  ~40 строк                  |   ~5 строк                        |
+-----------------------------------------------------------------+
```

---

## Когда Builder ВСЁ-ТАКИ нужен в Kotlin

Named parameters не покрывают все сценарии. Вот когда Builder оправдан:

### 1. DSL Builders: `buildString`, `buildList`, `buildMap`

```kotlin
// Kotlin stdlib --- builder-функции для коллекций
val html = buildString {
    appendLine("<!DOCTYPE html>")
    appendLine("<html>")
    appendLine("  <body>")
    appendLine("    <h1>Hello</h1>")
    appendLine("  </body>")
    appendLine("</html>")
}

val config = buildMap<String, Any> {
    put("host", "localhost")
    put("port", 8080)
    if (isProduction) {
        put("ssl", true)
        put("threads", 16)
    }
}

val items = buildList {
    add("base-item")
    addAll(loadFromDatabase())
    if (premiumUser) {
        add("premium-item")
    }
}
```

**Ключевое отличие от named params:** логика внутри builder (условия, циклы, вызовы функций).

### 2. Type-safe builders (Ktor, Compose, Gradle DSL)

```kotlin
// Ktor --- routing DSL
fun Application.configureRouting() {
    routing {
        get("/") {
            call.respondText("Hello World!")
        }
        route("/api") {
            get("/users") {
                call.respond(userService.findAll())
            }
            post("/users") {
                val user = call.receive<CreateUserRequest>()
                call.respond(HttpStatusCode.Created, userService.create(user))
            }
        }
    }
}

// Jetpack Compose --- UI builder
@Composable
fun UserCard(user: User) {
    Card(modifier = Modifier.padding(8.dp)) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = user.name,
                style = MaterialTheme.typography.headlineSmall
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(text = user.email)
        }
    }
}

// Gradle Kotlin DSL
plugins {
    kotlin("jvm") version "2.0.0"
    application
}

dependencies {
    implementation("io.ktor:ktor-server-core:2.3.0")
    testImplementation(kotlin("test"))
}
```

### 3. Пошаговая конструкция с порядком шагов

```kotlin
// SQL Query builder --- порядок вызовов имеет значение
class QueryBuilder {
    private val parts = mutableListOf<String>()
    private val params = mutableListOf<Any?>()

    fun select(vararg columns: String) = apply {
        parts += "SELECT ${columns.joinToString()}"
    }

    fun from(table: String) = apply {
        parts += "FROM $table"
    }

    fun where(condition: String, vararg values: Any?) = apply {
        parts += "WHERE $condition"
        params.addAll(values)
    }

    fun orderBy(column: String, desc: Boolean = false) = apply {
        val dir = if (desc) "DESC" else "ASC"
        parts += "ORDER BY $column $dir"
    }

    fun limit(count: Int) = apply {
        parts += "LIMIT $count"
    }

    fun build(): Query {
        require(parts.any { it.startsWith("SELECT") }) { "SELECT is required" }
        require(parts.any { it.startsWith("FROM") }) { "FROM is required" }
        return Query(parts.joinToString(" "), params)
    }
}

data class Query(val sql: String, val params: List<Any?>)

// Использование: читается как SQL
val query = QueryBuilder()
    .select("id", "name", "email")
    .from("users")
    .where("status = ?", "active")
    .orderBy("created_at", desc = true)
    .limit(10)
    .build()
```

### 4. Builder как fluent API для библиотечных пользователей

```kotlin
// OkHttp --- Java-библиотека с Builder, идиоматично используется из Kotlin
val request = Request.Builder()
    .url("https://api.example.com/users")
    .addHeader("Authorization", "Bearer $token")
    .post(jsonBody.toRequestBody("application/json".toMediaType()))
    .build()

// Retrofit --- Builder для конфигурации
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/")
    .addConverterFactory(GsonConverterFactory.create())
    .client(okHttpClient)
    .build()

// Android Notification.Builder
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle("New message")
    .setContentText("You have 5 new messages")
    .setSmallIcon(R.drawable.ic_notification)
    .setPriority(NotificationCompat.PRIORITY_DEFAULT)
    .setAutoCancel(true)
    .build()
```

> [!info] Kotlin-нюанс
> Java-библиотеки (OkHttp, Retrofit, Android SDK) продолжают использовать Builder, потому что они должны быть совместимы с Java. В чистом Kotlin-коде предпочитайте named parameters.

---

## Kotlin DSL deep dive

### Receiver lambdas --- основа DSL

```kotlin
// Обычная лямбда
fun buildString(action: (StringBuilder) -> Unit): String {
    val sb = StringBuilder()
    action(sb)                  // передаём sb как аргумент
    return sb.toString()
}

// Receiver lambda --- sb становится this
fun buildString(action: StringBuilder.() -> Unit): String {
    val sb = StringBuilder()
    sb.action()                 // sb --- receiver, доступен как this
    return sb.toString()
}

// Разница для пользователя:
// Обычная лямбда:
buildString { sb -> sb.append("hello") }

// Receiver lambda:
buildString { append("hello") }  // this = StringBuilder, append() напрямую
```

### Создание собственного DSL Builder

```kotlin
// Шаг 1: модель данных
data class HtmlPage(
    val head: HtmlHead,
    val body: HtmlBody
)

data class HtmlHead(val title: String)

data class HtmlBody(val elements: List<HtmlElement>)

sealed class HtmlElement {
    data class Heading(val level: Int, val text: String) : HtmlElement()
    data class Paragraph(val text: String) : HtmlElement()
    data class Link(val href: String, val text: String) : HtmlElement()
}

// Шаг 2: Builder-классы с receiver-функциями
class HtmlBodyBuilder {
    private val elements = mutableListOf<HtmlElement>()

    fun h1(text: String) { elements += HtmlElement.Heading(1, text) }
    fun h2(text: String) { elements += HtmlElement.Heading(2, text) }
    fun p(text: String) { elements += HtmlElement.Paragraph(text) }
    fun a(href: String, text: String) { elements += HtmlElement.Link(href, text) }

    fun build() = HtmlBody(elements)
}

class HtmlPageBuilder {
    private var title: String = ""
    private var bodyBuilder: (HtmlBodyBuilder.() -> Unit)? = null

    fun head(title: String) { this.title = title }

    fun body(block: HtmlBodyBuilder.() -> Unit) {
        bodyBuilder = block
    }

    fun build(): HtmlPage {
        val body = HtmlBodyBuilder().apply { bodyBuilder?.invoke(this) }.build()
        return HtmlPage(HtmlHead(title), body)
    }
}

// Шаг 3: top-level DSL функция
fun html(block: HtmlPageBuilder.() -> Unit): HtmlPage {
    return HtmlPageBuilder().apply(block).build()
}

// Использование --- читается почти как HTML!
val page = html {
    head("My Page")
    body {
        h1("Welcome")
        p("This is a paragraph.")
        a(href = "https://kotlinlang.org", text = "Kotlin")
    }
}
```

### `@DslMarker` --- контроль области видимости

```kotlin
// Проблема без @DslMarker:
html {
    body {
        h1("Title")
        // Опа! Вызываем head() из внешнего scope --- ошибка логики
        head("Oops")  // Компилятор разрешает --- head() доступен через outer receiver
    }
}

// Решение: @DslMarker запрещает неявный доступ к внешним receivers
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class HtmlPageBuilder { /* ... */ }

@HtmlDsl
class HtmlBodyBuilder { /* ... */ }

// Теперь:
html {
    body {
        h1("Title")
        // head("Oops")  // ОШИБКА КОМПИЛЯЦИИ!
        // Если действительно нужно: this@html.head("...")
    }
}
```

> [!info] Kotlin-нюанс
> `@DslMarker` --- killer feature для DSL. Без него вложенные builders имеют доступ ко всем внешним receivers, что приводит к коварным багам. Ktor, Compose и Gradle все используют `@DslMarker`.

### Реальные DSL: Gradle Kotlin DSL (под капотом)

```kotlin
// Что мы пишем в build.gradle.kts:
dependencies {
    implementation("io.ktor:ktor-server-core:2.3.0")
    testImplementation(kotlin("test"))
}

// Что стоит за этим:
// dependencies {} --- receiver lambda: DependencyHandlerScope.() -> Unit
// implementation() --- extension-функция на DependencyHandlerScope
// Gradle использует @DslMarker (через @HasImplicitReceiver)
// чтобы ограничить scope
```

---

## Anti-patterns

### 1. Builder для 2-3 параметров

```kotlin
// ПЛОХО: Builder без причины
class UserBuilder {
    private var name: String = ""
    private var email: String = ""

    fun name(value: String) = apply { name = value }
    fun email(value: String) = apply { email = value }
    fun build() = User(name, email)
}

// ХОРОШО: просто конструктор
data class User(val name: String, val email: String)
val user = User(name = "Alice", email = "alice@mail.com")
```

### 2. Мутабельный Builder без `build()`

```kotlin
// ПЛОХО: Builder, который ЯВЛЯЕТСЯ результатом
class Config {
    var host: String = ""
    var port: Int = 0
    var ssl: Boolean = false
    // Нет build() --- Config используется напрямую
    // Клиент может мутировать объект в любой момент
}

// ХОРОШО: Builder создаёт immutable результат
class ConfigBuilder {
    var host: String = ""
    var port: Int = 0
    var ssl: Boolean = false

    fun build(): Config = Config(host, port, ssl)  // Config --- immutable
}

data class Config(val host: String, val port: Int, val ssl: Boolean)
```

### 3. Builder + наследование

```kotlin
// ПЛОХО: наследование от Builder --- проблемы с return type
open class BaseBuilder {
    var name: String = ""
    fun name(value: String) = apply { name = value }
    // apply возвращает BaseBuilder, не ChildBuilder!
}

class ChildBuilder : BaseBuilder() {
    var extra: String = ""
    fun extra(value: String) = apply { extra = value }
}

// Проблема: chaining ломается
// ChildBuilder().name("x").extra("y")  // ОШИБКА: name() возвращает BaseBuilder

// Решение в Java: generics self-type (<T extends Builder<T>>)
// Решение в Kotlin: не наследовать Builder. Используй composition или DSL.
```

### 4. Builder в Kotlin, когда хватит data class

```kotlin
// ПЛОХО: перенос Java-привычки в Kotlin
class HttpRequest private constructor(
    val url: String,
    val method: String,
    val headers: Map<String, String>,
    val body: String?
) {
    class Builder {
        // ...40 строк boilerplate...
    }
}

// ХОРОШО: Kotlin-way
data class HttpRequest(
    val url: String,
    val method: String = "GET",
    val headers: Map<String, String> = emptyMap(),
    val body: String? = null
) {
    init {
        require(url.isNotBlank()) { "URL must not be blank" }
        require(method in listOf("GET", "POST", "PUT", "DELETE", "PATCH")) {
            "Invalid HTTP method: $method"
        }
    }
}

val request = HttpRequest(
    url = "https://api.example.com/users",
    method = "POST",
    headers = mapOf("Content-Type" to "application/json"),
    body = """{"name": "Alice"}"""
)
```

---

## Real-world: когда Builder оправдан

### OkHttp `Request.Builder`

```kotlin
// OkHttp --- Java-библиотека. Builder обязателен.
val client = OkHttpClient()

val request = Request.Builder()
    .url("https://api.github.com/users/octocat")
    .addHeader("Accept", "application/json")
    .addHeader("Authorization", "Bearer $token")
    .cacheControl(CacheControl.Builder().maxAge(10, TimeUnit.MINUTES).build())
    .build()

val response = client.newCall(request).execute()
```

**Почему Builder оправдан здесь:**
- Объект immutable после `build()`
- Методы `addHeader()` --- аддитивные (нельзя выразить named params)
- Java-совместимость

### Android `NotificationCompat.Builder`

```kotlin
val notification = NotificationCompat.Builder(context, CHANNEL_ID)
    .setContentTitle("Download complete")
    .setContentText("file.zip downloaded successfully")
    .setSmallIcon(R.drawable.ic_download)
    .setProgress(0, 0, false)           // Убираем progress bar
    .setAutoCancel(true)
    .addAction(                         // Вложенный builder
        R.drawable.ic_open,
        "Open",
        openPendingIntent
    )
    .setStyle(                          // Разные стили --- полиморфизм
        NotificationCompat.BigTextStyle()
            .bigText("Full description of the download...")
    )
    .build()
```

### Ktor Routing DSL

```kotlin
// DSL builder --- не Bloch-style Builder, а receiver lambda
fun Application.module() {
    install(ContentNegotiation) {  // receiver: ContentNegotiationConfig.() -> Unit
        json(Json {               // receiver: JsonBuilder.() -> Unit
            prettyPrint = true
            ignoreUnknownKeys = true
        })
    }

    routing {                     // receiver: Routing.() -> Unit
        route("/api/v1") {
            authenticate("jwt") {
                get("/profile") {
                    val user = call.principal<JWTPrincipal>()
                    call.respond(user?.payload?.subject ?: "Unknown")
                }
            }
        }
    }
}
```

---

## Дерево решений: нужен ли Builder?

```
Нужно создать объект со многими параметрами?
|
+-- Параметры известны на этапе компиляции?
|   +-- ДА, все сразу --> Named parameters + default values
|   +-- ДА, но нужна "модификация" --> data class + copy()
|   +-- НЕТ, значения вычисляются --> Builder или apply {}
|
+-- Нужна логика внутри конструкции? (условия, циклы)
|   +-- ДА --> DSL Builder (receiver lambda)
|
+-- Порядок шагов важен?
|   +-- ДА --> Fluent Builder с method chaining
|
+-- Это Java-библиотека?
|   +-- ДА --> Используй их Builder, не оборачивай
|
+-- 2-3 параметра?
    +-- ДА --> Просто конструктор. Builder = overengineering
```

---

## Подводные камни

### Pitfall 1: Default values в data class не видны из Java

```kotlin
// Kotlin:
data class Config(val host: String = "localhost", val port: Int = 8080)

// Из Java: Config("localhost", 8080) --- defaults не работают!
// Решение: @JvmOverloads
data class Config @JvmOverloads constructor(
    val host: String = "localhost",
    val port: Int = 8080
)
```

### Pitfall 2: `copy()` не deep copy

```kotlin
data class Team(val name: String, val members: MutableList<String>)

val team1 = Team("Alpha", mutableListOf("Alice", "Bob"))
val team2 = team1.copy(name = "Beta")

team2.members.add("Charlie")
println(team1.members) // [Alice, Bob, Charlie] --- МУТАЦИЯ ОРИГИНАЛА!

// Решение: immutable collections
data class Team(val name: String, val members: List<String>)
```

### Pitfall 3: Builder thread-safety

```kotlin
// Builder НЕ thread-safe по умолчанию
// Не расшаривай Builder между потоками!
val builder = ServerConfig.Builder()

// Thread 1:
builder.hostname("server-1")

// Thread 2:
builder.hostname("server-2")  // Race condition!

// Решение: один builder --- один поток
```

---

## Проверь себя

> [!question]- Почему в Kotlin named parameters заменяют 80% случаев использования Builder?
> Named parameters решают три ключевые проблемы: (1) именование --- каждый параметр подписан, порядок не важен; (2) дефолты --- необязательные параметры не требуют null-заглушек; (3) валидация --- `init {}` блок проверяет инварианты. При этом кода в 5-8 раз меньше, чем у Java Builder. Builder нужен только когда конструкция пошаговая, динамическая или содержит логику.

> [!question]- В чём разница между `apply {}` и Builder для инициализации объекта?
> `apply {}` --- это scope function для инициализации мутабельного объекта. Builder --- отдельный объект, который накапливает параметры и создаёт immutable результат через `build()`. Критическое различие: Builder может валидировать при `build()` и гарантировать immutability результата. `apply {}` просто вызывает setters --- объект остаётся мутабельным и невалидированным.

> [!question]- Что делает `@DslMarker` и зачем он нужен?
> `@DslMarker` ограничивает область видимости implicit receivers во вложенных DSL-блоках. Без него внутренний блок имеет доступ ко всем внешним receivers, что позволяет случайно вызвать метод "не того" builder. С `@DslMarker` доступен только ближайший receiver; для доступа к внешнему нужен явный `this@outer`. Все крупные Kotlin DSL (Ktor, Compose, Gradle) используют `@DslMarker`.

> [!question]- Когда `copy()` на data class опасен?
> Когда data class содержит мутабельные свойства (MutableList, MutableMap, var). `copy()` делает shallow copy --- обе копии ссылаются на один и тот же мутабельный объект. Мутация через одну копию видна через другую. Решение: использовать только immutable типы (List, Map, val) в data class.

> [!question]- Почему Java-библиотеки (OkHttp, Retrofit) продолжают использовать Builder, даже будучи вызванными из Kotlin?
> Java-библиотеки должны поддерживать Java-пользователей, у которых нет named parameters и default values. Кроме того, Builder позволяет аддитивные операции (addHeader --- добавить ещё один, а не заменить), что невозможно выразить через конструктор. Builder также гарантирует immutability результата и инкапсулирует сложную логику валидации.

---

## Ключевые карточки

В чём главная альтернатива Builder в Kotlin?
?
Named parameters + default values. Вместо 40+ строк Builder-класса --- одно объявление `data class` с параметрами по умолчанию. Порядок параметров не важен, необязательные имеют дефолты, валидация --- в `init {}` блоке.

Какие три механизма Kotlin заменяют классический Builder?
?
1) Named params + default values --- основной механизм для большинства случаев. 2) `copy()` на data class --- иммутабельная модификация существующего объекта. 3) `apply {}` --- scope function для инициализации мутабельного объекта.

Что такое receiver lambda и как она связана с DSL?
?
Receiver lambda --- функция с типом `T.() -> Unit`, где T доступен как `this` внутри лямбды. Это основа Kotlin DSL: `fun html(block: HTML.() -> Unit)` позволяет внутри блока вызывать методы HTML напрямую. Используется в Ktor routing, Compose UI, Gradle DSL.

Когда Builder всё-таки нужен в Kotlin?
?
1) DSL builders с логикой внутри (условия, циклы). 2) Type-safe builders (Ktor, Compose, Gradle). 3) Пошаговая конструкция с порядком шагов. 4) Fluent API для библиотечных пользователей. 5) Java-совместимые библиотеки (OkHttp, Retrofit).

Что такое @DslMarker и какую проблему решает?
?
Аннотация, ограничивающая implicit receivers во вложенных DSL-блоках. Без неё внутренний builder имеет доступ к методам всех внешних builders, что ведёт к коварным багам. С @DslMarker доступен только ближайший receiver; для внешнего нужен явный `this@outer`.

Чем `copy()` отличается от Builder при модификации объекта?
?
`copy()` создаёт новый экземпляр data class с изменёнными полями. Это shallow copy --- мутабельные вложенные объекты расшариваются. Builder накапливает параметры и создаёт совершенно новый объект при `build()`. Для иммутабельных data class `copy()` проще; для объектов со сложной инициализацией --- Builder.

Почему Builder + наследование --- антипаттерн?
?
Метод chaining возвращает тип базового Builder, не дочернего: `ChildBuilder().name("x")` возвращает `BaseBuilder`, и метод `.extra("y")` недоступен. В Java решают через generics self-type (`<T extends Builder<T>>`). В Kotlin лучше не наследовать Builder, а использовать composition или DSL.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Фундамент | [[design-patterns-overview]] | Обзор всех GoF паттернов и когда их применять |
| Связанный паттерн | [[factory-pattern]] | Factory решает "какой объект создать", Builder --- "как его создать" |
| Kotlin-возможности | [[kotlin-advanced-features]] | Receiver lambdas, extensions, delegates --- инструменты для DSL |
| Принципы | [[dry-kiss-yagni]] | YAGNI помогает решить: нужен Builder или хватит конструктора |
| Обзор | [[design-patterns-overview]] | Вернуться к карте раздела Design Patterns |

---

## Источники

- Gamma E. et al. (1994). *Design Patterns: Elements of Reusable Object-Oriented Software* --- оригинальное описание Builder pattern в GoF каталоге
- Bloch J. (2018). *Effective Java*, 3rd Edition, Item 2: "Consider a builder when faced with many constructor parameters" --- классическая формулировка Builder для Java
- Moskala M. (2022). *Effective Kotlin*, Item 34: "Consider a primary constructor with named optional parameters" --- почему в Kotlin Builder обычно не нужен
- [Kotlin Documentation: Type-safe builders](https://kotlinlang.org/docs/type-safe-builders.html) --- официальная документация по DSL builders
- [Kotlin-ifying a Builder Pattern (Google Developers)](https://medium.com/google-developers/kotlin-ifying-a-builder-pattern-e5540c91bdbe) --- миграция Java Builder в идиоматичный Kotlin
- [Kotlin Builder Pattern (asvid.github.io)](https://asvid.github.io/kotlin-builder-pattern) --- обзор альтернатив Builder в Kotlin
- [Domain-Specific Languages in Kotlin (Xebia)](https://xebia.com/blog/domain-specific-languages-in-kotlin-the-type-safe-builder-pattern/) --- type-safe builder pattern для DSL
- [Building Type-safe DSLs with Kotlin (carrion.dev)](https://carrion.dev/en/posts/building-type-safe-dsls/) --- от основ до продвинутых паттернов DSL

---

*Проверено: 2026-02-19*
