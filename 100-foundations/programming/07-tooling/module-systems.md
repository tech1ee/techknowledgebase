---
title: "Module Systems: модульность в Kotlin/JVM"
created: 2026-01-09
modified: 2026-02-19
type: concept
status: published
confidence: high
tags:
  - programming/modules
  - topic/jvm
  - kotlin
  - gradle
  - build-systems
  - type/concept
  - level/intermediate
related:
  - "[[build-systems-theory]]"
  - "[[dependency-resolution]]"
  - "[[solid-principles]]"
  - "[[android-modularization]]"
  - "[[kotlin-multiplatform-overview]]"
prerequisites:
  - "[[solid-principles]]"
reading_time: 18
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Module Systems: модульность в Kotlin/JVM

> **TL;DR:** Модульная система позволяет разбивать код на независимые части с явными зависимостями и контролируемыми границами. В Kotlin/JVM модульность реализуется на нескольких уровнях: visibility modifiers (`internal`, `public`, `private`), Gradle multi-module проекты (`api` vs `implementation`), JPMS (`module-info.java`), и Kotlin Multiplatform (`expect`/`actual`). Хорошая модульность = низкая связанность + высокая связность + чёткие границы API.

---

## Исторический контекст

Идея модульности в программировании формализована **David Parnas** в знаковой статье *"On the Criteria To Be Used in Decomposing Systems into Modules"* (1972). Parnas показал, что декомпозиция должна основываться на **information hiding** — каждый модуль скрывает "design decision", а не просто группирует код по функциональности. Этот принцип остаётся фундаментом модульного проектирования.

Ранние языки реализовывали модульность по-разному. **Modula-2** (Niklaus Wirth, 1978) ввёл явное разделение на definition module (интерфейс) и implementation module. **Ada** (1983) использовал packages с public/private секциями. **C** до сих пор использует примитивную модульность через header files (.h) и compilation units (.c) — подход, известный своей хрупкостью (include guards, forward declarations).

В **Java-мире** модульность на уровне языка появилась лишь в **Java 9** (2017) с **JPMS** (Java Platform Module System, Project Jigsaw) — после 10 лет разработки. JPMS добавил `module-info.java` с явными `requires`/`exports`, решив проблему "classpath hell", когда любой публичный класс был доступен из любой точки приложения. До JPMS единственный механизм ограничения доступа — `package-private` visibility в Java, что было слишком мелкозернистым.

**Kotlin** (2016+) привнёс ключевое нововведение — модификатор видимости `internal`, который ограничивает доступ рамками модуля компиляции (Gradle module, Maven artifact). Это дало разработчикам инструмент для определения границ API без необходимости использовать JPMS. В сочетании с Gradle multi-module проектами (`api` vs `implementation`) это создаёт мощную многоуровневую систему модульности.

В **JavaScript** модульность долго отсутствовала: до 2009 года весь код жил в глобальном scope. **CommonJS** (2009) решил проблему для Node.js через `require()`/`module.exports`. **ES Modules** (2015) стандартизировал модульную систему с статическим анализом (tree shaking). Эта эволюция параллельна JVM-миру, но с принципиально другим подходом: JS-модули — файловые, JVM-модули — пакетные/JAR-based.

```
1972: Parnas — "Information Hiding" (теория)
        │
1978: Modula-2 — definition/implementation modules
        │
1995: Java — packages + package-private visibility
        │
2004: Maven — артефакты как единицы распространения
        │
2007: Gradle — multi-project builds с api/implementation
        │
2016: Kotlin — internal visibility modifier
        │
2017: Java 9 JPMS — module-info.java (requires/exports)
        │
2020+: Kotlin Multiplatform — expect/actual для кроссплатформы
```

---

## Интуиция: 5 аналогий

### 1. Модули как LEGO
```
БЕЗ модулей:
  Один огромный кусок пластика
  Изменить часть = сломать всё

С модулями:
  Отдельные кубики LEGO
  Каждый кубик:
  - Имеет чёткий интерфейс (пупырышки)
  - Работает независимо
  - Можно заменить на другой

Хороший модуль = хороший LEGO-кубик
```

### 2. Модули как комнаты в доме
```
┌─────────────────────────────────────────┐
│                  ДОМ                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │ Кухня   │  │Гостиная │  │ Спальня │ │
│  │         │──│         │──│         │ │
│  └─────────┘  └─────────┘  └─────────┘ │
└─────────────────────────────────────────┘

Каждая комната (модуль):
- Имеет своё назначение (ответственность)
- Имеет двери (public API)
- Стены = internal — видно внутри, но не снаружи
- Не нужно проходить через спальню, чтобы попасть на кухню

Плохая архитектура: все комнаты проходные (всё public)
```

### 3. Public API как витрина магазина
```
┌────────────────────────────────────────┐
│           ВИТРИНА (public)             │
│  ┌──────┐  ┌──────┐  ┌──────┐        │
│  │ fun  │  │class │  │const │        │
│  └──────┘  └──────┘  └──────┘        │
├────────────────────────────────────────┤
│          СКЛАД (internal/private)     │
│    helpers, utils, internal state     │
│    Другие модули НЕ ВИДЯТ             │
└────────────────────────────────────────┘

public = выставить в витрину (доступно всем)
internal = видно сотрудникам (внутри модуля)
private = личный сейф (только в файле/классе)
```

### 4. Зависимость как контракт
```
Модуль :feature-auth зависит от :core-network:

// core-network (публичный API)
class NetworkClient {
    fun get(url: String): Response  // ← контракт
}

// feature-auth (потребитель)
class AuthRepository(
    private val client: NetworkClient  // Зависит от контракта
)

Если :core-network изменит внутренности — :feature-auth продолжит работать
Если :core-network изменит public API — :feature-auth сломается

Loose coupling = зависимость от контракта, не от реализации
```

### 5. Циклические зависимости как deadlock
```
:module-a зависит от :module-b
:module-b зависит от :module-a

         ┌───────┐
    ┌───►│   A   │────┐
    │    └───────┘    │
    │                 ▼
    │    ┌───────┐
    └────│   B   │◄───┘
         └───────┘

Что компилировать первым?
- A нужен B → жди B
- B нужен A → жди A
→ Gradle: "Circular dependency between projects"

Решение: выделить общую часть в :module-common
```

---

## Уровни модульности в Kotlin/JVM

В Kotlin/JVM модульность работает на нескольких уровнях, от самого мелкого к самому крупному:

```
УРОВЕНЬ 1: Visibility modifiers (язык)
  private → protected → internal → public

УРОВЕНЬ 2: Packages (JVM)
  com.myapp.core.api vs com.myapp.core.internal

УРОВЕНЬ 3: Gradle modules (build system)
  :core, :feature-auth, :feature-profile
  api vs implementation зависимости

УРОВЕНЬ 4: JPMS (Java Platform Module System)
  module-info.java: requires/exports

УРОВЕНЬ 5: Kotlin Multiplatform
  expect/actual: commonMain → androidMain / iosMain
```

---

## Kotlin visibility modifiers как границы модуля

### Четыре модификатора

```kotlin
// ═══ УРОВЕНЬ ФАЙЛА (top-level declarations) ═══

public fun apiFunction() { ... }        // Видно всем (по умолчанию)
internal fun moduleHelper() { ... }     // Видно только в этом Gradle-модуле
private fun fileOnly() { ... }          // Видно только в этом файле
// protected нельзя для top-level

// ═══ УРОВЕНЬ КЛАССА ═══

class UserRepository {
    public fun getUser(id: String): User { ... }     // API модуля
    internal fun invalidateCache() { ... }            // Для использования внутри модуля
    protected fun onDataChanged() { ... }             // Для наследников
    private fun queryDatabase(id: String): User { ... } // Только этот класс
}
```

### internal — ключ к модульности в Kotlin

```kotlin
// ═══ Модуль :core-network ═══

// Публичный API модуля (видно потребителям)
public class NetworkClient(
    private val baseUrl: String
) {
    public fun get(url: String): Response = executeRequest(Request.Get(url))
    public fun post(url: String, body: RequestBody): Response = executeRequest(Request.Post(url, body))
}

// Внутренняя реализация (НЕ видна потребителям)
internal class RetryInterceptor(
    private val maxRetries: Int = 3
) {
    internal fun intercept(request: Request): Response {
        repeat(maxRetries) { attempt ->
            try {
                return executeRaw(request)
            } catch (e: IOException) {
                if (attempt == maxRetries - 1) throw e
            }
        }
        throw IllegalStateException("Unreachable")
    }
}

internal fun executeRequest(request: Request): Response {
    // Детали реализации, скрытые от внешнего мира
    val interceptor = RetryInterceptor()
    return interceptor.intercept(request)
}
```

```kotlin
// ═══ Модуль :feature-auth (потребитель) ═══

class AuthRepository(private val client: NetworkClient) {

    fun login(credentials: Credentials): AuthToken {
        val response = client.post("/auth/login", credentials.toBody())
        //
        // client.executeRequest(...)  // ❌ ОШИБКА: internal, не виден
        // RetryInterceptor()          // ❌ ОШИБКА: internal class
        //
        return response.parseAs<AuthToken>()
    }
}
```

### Как internal работает на JVM

```
ПРОБЛЕМА: JVM не имеет концепции "internal"

РЕШЕНИЕ: Kotlin использует name mangling

Kotlin код:
  internal fun helper() { ... }

Скомпилированный байткод:
  public fun helper$mymodule() { ... }  // Имя "испорчено"

Java-код из другого модуля:
  // Технически можно вызвать helper$mymodule()
  // Но IDE не предложит, и это явный code smell

ВЫВОД: internal — enforcement на уровне компилятора Kotlin,
       а не на уровне JVM
```

### internal vs package-private (Java)

```
JAVA package-private (default):
  Видно в том же пакете
  ПРОБЛЕМА: пакет может быть "размазан" по нескольким JAR

  com.mylib.internal.Helper  // Если кто-то создаст такой же пакет
                              // в своём проекте — увидит Helper!

KOTLIN internal:
  Видно в том же модуле компиляции (Gradle module)
  Не зависит от пакетной структуры
  Модуль = единица компиляции = JAR

  Это СИЛЬНЕЕ чем package-private:
  - Пакеты не влияют на видимость
  - Невозможно "подсмотреть" из другого JAR
  - Чёткая граница = Gradle module boundary
```

---

## Gradle модули: api vs implementation

### Что такое Gradle module

```
myproject/
├── settings.gradle.kts          # Перечисляет все модули
├── build.gradle.kts             # Root project
├── core/
│   ├── network/
│   │   ├── build.gradle.kts     # :core:network
│   │   └── src/main/kotlin/
│   └── database/
│       ├── build.gradle.kts     # :core:database
│       └── src/main/kotlin/
├── feature/
│   ├── auth/
│   │   ├── build.gradle.kts     # :feature:auth
│   │   └── src/main/kotlin/
│   └── profile/
│       ├── build.gradle.kts     # :feature:profile
│       └── src/main/kotlin/
└── app/
    ├── build.gradle.kts         # :app (собирает всё вместе)
    └── src/main/kotlin/
```

```kotlin
// settings.gradle.kts
rootProject.name = "myproject"

include(":core:network")
include(":core:database")
include(":feature:auth")
include(":feature:profile")
include(":app")
```

### api vs implementation: ключевое различие

```kotlin
// ═══ :core:network/build.gradle.kts ═══
plugins {
    kotlin("jvm")
    `java-library`  // Необходим для api scope
}

dependencies {
    // api — тип из OkHttp ВИДЕН потребителям :core:network
    api("com.squareup.okhttp3:okhttp:4.12.0")

    // implementation — Moshi СКРЫТ от потребителей
    implementation("com.squareup.moshi:moshi:1.15.0")
}
```

```kotlin
// ═══ :core:network — публичный API ═══
// OkHttp тип в публичном API → зависимость должна быть api
class NetworkClient(
    val httpClient: OkHttpClient  // OkHttp тип виден потребителям
) {
    fun get(url: String): Response { ... }
}

// Moshi используется только внутри → implementation достаточно
internal class JsonParser {
    private val moshi = Moshi.Builder().build()  // Moshi не течёт наружу
    fun <T> parse(json: String, type: Class<T>): T = ...
}
```

```kotlin
// ═══ :feature:auth/build.gradle.kts ═══
dependencies {
    implementation(project(":core:network"))
}

// ═══ :feature:auth — использование ═══
class AuthRepository(private val client: NetworkClient) {
    fun login(): AuthToken {
        val response = client.get("/auth/me")
        // client.httpClient — OkHttpClient, доступен (api scope)

        // JsonParser()  // ❌ internal — не видно
        // Moshi.Builder() // ❌ implementation — не видно из :feature:auth
        return parseResponse(response)
    }
}
```

### Влияние на время сборки

```
СЦЕНАРИЙ: изменился OkHttp (api зависимость :core:network)

С api:
  :core:network изменился
      → :feature:auth перекомпилируется     (видит OkHttp)
      → :feature:profile перекомпилируется  (видит OkHttp)
      → :app перекомпилируется

С implementation:
  :core:network изменился
      → :feature:auth НЕ перекомпилируется  (не видит внутренности)
      → :feature:profile НЕ перекомпилируется
      → :app может не перекомпилироваться

ПРАВИЛО: Чем меньше api зависимостей, тем быстрее incremental build
```

### Типичная структура build.gradle.kts для Kotlin модуля

```kotlin
// feature/auth/build.gradle.kts
plugins {
    kotlin("jvm")
    `java-library`
}

dependencies {
    // Публичные зависимости (типы в API)
    api(project(":core:model"))        // Domain модели в сигнатурах

    // Скрытые зависимости (реализация)
    implementation(project(":core:network"))   // Сетевой слой
    implementation(project(":core:database"))  // Хранилище

    // Только для компиляции
    compileOnly("javax.annotation:javax.annotation-api:1.3.2")

    // Тесты
    testImplementation(kotlin("test"))
    testImplementation("io.mockk:mockk:1.13.8")
}
```

### Convention plugins для единообразия

```kotlin
// buildSrc/src/main/kotlin/kotlin-library-conventions.gradle.kts
plugins {
    kotlin("jvm")
    `java-library`
}

kotlin {
    jvmToolchain(17)
}

dependencies {
    testImplementation(kotlin("test"))
    testImplementation("io.mockk:mockk:1.13.8")
}

tasks.test {
    useJUnitPlatform()
}

// Теперь в каждом модуле:
// build.gradle.kts
plugins {
    id("kotlin-library-conventions")
}

dependencies {
    // Только специфичные зависимости модуля
    implementation(project(":core:network"))
}
```

---

## Java Platform Module System (JPMS)

### Основы JPMS

```java
// module-info.java (в корне src/main/java)
module com.myapp.core {
    // Зависимости
    requires java.base;                    // Неявно (всегда есть)
    requires transitive java.sql;          // Транзитивная: потребители тоже видят java.sql
    requires kotlin.stdlib;                // Kotlin stdlib

    // Экспорт пакетов
    exports com.myapp.core.api;            // Публичный API
    exports com.myapp.core.model;          // Публичные модели

    // Ограниченный экспорт (qualified export)
    exports com.myapp.core.spi to com.myapp.plugins;

    // Для рефлексии (Gson, Jackson, Spring)
    opens com.myapp.core.model to com.google.gson;

    // Service Provider Interface
    uses com.myapp.core.spi.StorageProvider;
    provides com.myapp.core.spi.StorageProvider
        with com.myapp.core.internal.FileStorageProvider;
}
```

### JPMS vs Kotlin internal

```
JPMS (Java 9+):
  ✅ Контроль на уровне JVM (runtime enforcement)
  ✅ Ограничение рефлексии (opens)
  ✅ Service Provider Interface
  ❌ Сложно настроить с Kotlin
  ❌ Многие библиотеки не поддерживают
  ❌ Контроль на уровне пакетов (пакет = экспортируемый или нет)

Kotlin internal:
  ✅ Просто использовать (один keyword)
  ✅ Контроль на уровне деклараций (класс, функция)
  ✅ Хорошо работает с Gradle modules
  ❌ Не enforcement на уровне JVM (name mangling)
  ❌ Java-код может обойти (через mangled имена)
  ❌ Нет контроля рефлексии

РЕКОМЕНДАЦИЯ для Kotlin проектов:
  1. internal + Gradle modules = основной механизм
  2. JPMS — если нужен runtime enforcement или library for Java consumers
```

### JPMS в Kotlin проекте

```kotlin
// build.gradle.kts
plugins {
    kotlin("jvm")
}

// Kotlin компилирует module-info.java автоматически,
// если файл находится в src/main/java/module-info.java

tasks.compileJava {
    // module-info.java компилируется после Kotlin
    dependsOn(tasks.compileKotlin)

    // Добавляем Kotlin-классы в module path
    options.compilerArgs.addAll(listOf(
        "--patch-module", "com.myapp.core=${tasks.compileKotlin.get().destinationDirectory.asFile.get()}"
    ))
}
```

---

## Kotlin Multiplatform: expect/actual

### Кроссплатформенная модульность

```kotlin
// ═══ commonMain — общий код (платформонезависимый) ═══

// expect = "я ожидаю, что каждая платформа предоставит реализацию"
expect class Platform {
    val name: String
    val version: String
}

expect fun createHttpClient(): HttpClient

expect fun currentTimeMillis(): Long

// Общая бизнес-логика, использующая expect-декларации
class AnalyticsTracker(private val platform: Platform) {
    fun trackEvent(event: String) {
        val timestamp = currentTimeMillis()
        val client = createHttpClient()
        client.post("/analytics", mapOf(
            "event" to event,
            "platform" to platform.name,
            "version" to platform.version,
            "timestamp" to timestamp
        ))
    }
}
```

```kotlin
// ═══ androidMain — Android реализация ═══

actual class Platform {
    actual val name: String = "Android"
    actual val version: String = "${Build.VERSION.SDK_INT}"
}

actual fun createHttpClient(): HttpClient = OkHttpClient()

actual fun currentTimeMillis(): Long = System.currentTimeMillis()
```

```kotlin
// ═══ iosMain — iOS реализация ═══

actual class Platform {
    actual val name: String = "iOS"
    actual val version: String = UIDevice.current.systemVersion
}

actual fun createHttpClient(): HttpClient = NSURLSessionClient()

actual fun currentTimeMillis(): Long =
    (NSDate().timeIntervalSince1970 * 1000).toLong()
```

### Структура KMP модуля

```
shared/
├── build.gradle.kts
└── src/
    ├── commonMain/kotlin/       ← Общий код + expect
    │   └── com/myapp/shared/
    │       ├── Platform.kt
    │       └── Analytics.kt
    ├── commonTest/kotlin/       ← Общие тесты
    ├── androidMain/kotlin/      ← actual для Android
    │   └── com/myapp/shared/
    │       └── Platform.android.kt
    ├── iosMain/kotlin/          ← actual для iOS
    │   └── com/myapp/shared/
    │       └── Platform.ios.kt
    └── jvmMain/kotlin/          ← actual для JVM (server)
        └── com/myapp/shared/
            └── Platform.jvm.kt
```

```kotlin
// shared/build.gradle.kts
plugins {
    kotlin("multiplatform")
}

kotlin {
    androidTarget()
    iosArm64()
    iosSimulatorArm64()
    jvm()

    sourceSets {
        commonMain.dependencies {
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-core:1.8.0")
            implementation("io.ktor:ktor-client-core:2.3.0")
        }
        androidMain.dependencies {
            implementation("io.ktor:ktor-client-okhttp:2.3.0")
        }
        iosMain.dependencies {
            implementation("io.ktor:ktor-client-darwin:2.3.0")
        }
    }
}
```

---

## Организация пакетов в Kotlin/JVM

### Стратегия пакетирования

```
ПЛОХО — плоская структура:
com.myapp/
├── UserRepository.kt
├── UserService.kt
├── OrderRepository.kt
├── OrderService.kt
├── NetworkClient.kt
├── DatabaseHelper.kt
└── ... 200 файлов в одном пакете

ХОРОШО — по feature/layer:
com.myapp/
├── core/
│   ├── network/
│   │   ├── NetworkClient.kt       (public)
│   │   ├── RetryInterceptor.kt    (internal)
│   │   └── RequestBuilder.kt      (internal)
│   └── database/
│       ├── AppDatabase.kt         (public)
│       └── MigrationHelper.kt     (internal)
├── feature/
│   ├── auth/
│   │   ├── AuthRepository.kt      (public)
│   │   ├── TokenManager.kt        (internal)
│   │   └── CredentialValidator.kt  (internal)
│   └── profile/
│       ├── ProfileRepository.kt   (public)
│       └── AvatarProcessor.kt     (internal)
└── di/
    └── AppModule.kt               (internal)
```

### Правила именования и организации

```kotlin
// ПРАВИЛО 1: Пакет = модуль ответственности
// Каждый пакет — это мини-модуль с чётким назначением

// ПРАВИЛО 2: Public API на верхнем уровне пакета
package com.myapp.core.network

public class NetworkClient { ... }         // ← Публичный API
public data class NetworkConfig { ... }    // ← Публичная конфигурация

// ПРАВИЛО 3: Internal implementation в подпакетах или тут же
internal class ConnectionPool { ... }      // ← Реализация, скрыта

// ПРАВИЛО 4: Один публичный класс = один файл (по конвенции)
// NetworkClient.kt, NetworkConfig.kt

// ПРАВИЛО 5: Extension functions в отдельном файле
// Extensions.kt или NetworkExtensions.kt
internal fun Response.isRetryable(): Boolean = code in 500..599
```

---

## Android модульность

Модульность в Android-проектах — это применение Gradle multi-module подхода с учётом специфики Android (activities, fragments, resources, manifest merging). Подробнее: [[android-modularization]].

### Типичная архитектура модулей Android

```
┌─────────────────────────────────────────────────┐
│                    :app                          │
│          (Application, DI, Navigation)           │
├───────────┬───────────┬──────────┬──────────────┤
│:feature   │:feature   │:feature  │:feature      │
│:auth      │:profile   │:feed     │:settings     │
├───────────┴───────────┴──────────┴──────────────┤
│              :core:ui (Compose/Design System)    │
├────────────┬────────────┬───────────────────────┤
│:core       │:core       │:core                   │
│:network    │:database   │:model                  │
├────────────┴────────────┴───────────────────────┤
│              :core:common (utils, extensions)    │
└─────────────────────────────────────────────────┘

Правила:
- :feature модули НЕ зависят друг от друга
- :core модули НЕ зависят от :feature
- :app собирает всё через DI
- Навигация между features через :core:navigation
```

```kotlin
// feature/auth/build.gradle.kts
plugins {
    id("com.android.library")
    kotlin("android")
}

dependencies {
    implementation(project(":core:network"))
    implementation(project(":core:model"))
    implementation(project(":core:ui"))

    // НЕ зависит от других features!
    // implementation(project(":feature:profile"))  // ❌ Запрещено
}
```

---

## Частые ошибки: 6 проблем

### ❌ Ошибка 1: Циклические зависимости между модулями

**Симптом:** `Circular dependency between projects ':module-a' and ':module-b'`

```kotlin
// ПЛОХО:
// :module-a/build.gradle.kts
dependencies {
    implementation(project(":module-b"))
}

// :module-b/build.gradle.kts
dependencies {
    implementation(project(":module-a"))  // ❌ Цикл!
}

// ХОРОШО — выделить общую часть:
// :module-common — общие интерфейсы и модели
interface UserProvider {
    fun getUser(id: String): User
}

// :module-a зависит от :module-common
class UserService : UserProvider { ... }

// :module-b зависит от :module-common
class OrderService(private val userProvider: UserProvider) { ... }
```

**Решение:** Dependency Inversion — выделить интерфейсы в общий модуль, зависеть от абстракций.

---

### ❌ Ошибка 2: Утечка internal API

**Симптом:** Потребители модуля используют внутренние классы

```kotlin
// ПЛОХО — всё public по умолчанию:
package com.myapp.core.network

class NetworkClient { ... }          // API
class RetryInterceptor { ... }       // Должен быть internal!
class ConnectionPool { ... }         // Должен быть internal!
fun buildRequest(): Request { ... }  // Должен быть internal!

// ХОРОШО — явные границы:
public class NetworkClient { ... }           // API — public
internal class RetryInterceptor { ... }      // Реализация — internal
internal class ConnectionPool { ... }        // Реализация — internal
internal fun buildRequest(): Request { ... } // Helper — internal
```

**Решение:** По умолчанию делай `internal`, переводи в `public` только то, что является частью API модуля.

---

### ❌ Ошибка 3: Монолитный модуль (God module)

**Симптом:** Один модуль на 500+ классов, все зависят от него

```kotlin
// ПЛОХО — монолитный :core на 500 классов:
// :core/build.gradle.kts
dependencies {
    api("com.squareup.okhttp3:okhttp:4.12.0")
    api("com.squareup.moshi:moshi:1.15.0")
    api("androidx.room:room-runtime:2.6.0")
    api("io.ktor:ktor-client-core:2.3.0")
    // ... ещё 50 зависимостей
}
// Изменение ЛЮБОЙ строки → пересборка ВСЕГО

// ХОРОШО — разбить по ответственности:
// :core:network — OkHttp, Ktor
// :core:database — Room, SQLDelight
// :core:model — domain модели (только data classes, нет зависимостей)
// :core:common — утилиты, extensions
```

**Решение:** Single Responsibility для модулей. Каждый модуль имеет одну причину для изменения.

---

### ❌ Ошибка 4: Злоупотребление api вместо implementation

**Симптом:** Медленная инкрементальная сборка, всё перекомпилируется

```kotlin
// ПЛОХО — всё через api:
dependencies {
    api(project(":core:network"))     // Все зависимости :core:network течь потребителям
    api(project(":core:database"))    // То же самое
    api("com.google.guava:guava:31.0")
}

// ХОРОШО — api только для публичных типов:
dependencies {
    api(project(":core:model"))       // Типы из :core:model в сигнатурах
    implementation(project(":core:network"))   // Скрыто
    implementation(project(":core:database"))  // Скрыто
    implementation("com.google.guava:guava:31.0")  // Скрыто
}
```

**Правило:** Используй `api` ТОЛЬКО если тип из зависимости появляется в публичных сигнатурах (параметры, возвращаемые значения, наследование).

---

### ❌ Ошибка 5: Отсутствие границ модуля

**Симптом:** Модули есть, но любой класс доступен из любого модуля

```kotlin
// ПЛОХО — модуль :core:database, всё public:
public class AppDatabase { ... }
public class UserDao { ... }
public class MigrationHelper { ... }
public fun rawQuery(sql: String): Cursor { ... }  // Опасно!

// Любой feature-модуль может:
val helper = MigrationHelper()  // Не должен!
rawQuery("DROP TABLE users")     // Точно не должен!

// ХОРОШО — чёткие границы:
public class AppDatabase {
    public fun userDao(): UserDao
}
public interface UserDao {
    public suspend fun getUser(id: String): User?
    public suspend fun insertUser(user: User)
}
internal class UserDaoImpl : UserDao { ... }
internal class MigrationHelper { ... }
internal fun rawQuery(sql: String): Cursor { ... }
```

**Решение:** Публичный API модуля — интерфейсы. Реализация — internal.

---

### ❌ Ошибка 6: Feature модули зависят друг от друга

**Симптом:** Изменение в :feature:auth ломает :feature:profile

```kotlin
// ПЛОХО:
// :feature:profile зависит от :feature:auth
dependencies {
    implementation(project(":feature:auth"))  // ❌ Coupling между features
}

// Теперь :feature:profile знает про AuthToken, LoginScreen...
// Рефакторинг auth ломает profile

// ХОРОШО — через core модуль или навигацию:
// :core:auth-api — только интерфейсы и модели
interface AuthStateProvider {
    fun isAuthenticated(): Boolean
    fun getCurrentUser(): User?
}

// :feature:profile зависит от :core:auth-api
dependencies {
    implementation(project(":core:auth-api"))
}

// :feature:auth реализует :core:auth-api
class AuthStateProviderImpl : AuthStateProvider { ... }
```

**Решение:** Features общаются через абстракции в core модулях.

---

## Ментальные модели: 5 принципов

### 1. Cohesion vs Coupling

```
HIGH COHESION (хорошо):
  Модуль делает ОДНО дело хорошо
  Все части модуля связаны логически

  :core:network →
  - NetworkClient
  - RequestBuilder
  - ResponseParser
  - RetryInterceptor
  ← Всё про сетевое взаимодействие!

LOW COUPLING (хорошо):
  Модули минимально зависят друг от друга
  Изменение в A не ломает B

  :feature:auth ──interface──► :core:network
                 (не impl!)
```

### 2. Принцип наименьшего знания

```
Модуль должен знать МИНИМУМ о других модулях

ПЛОХО:
  // :feature:auth знает про внутренности :core:database
  val db = AppDatabase.getInstance()
  db.openHelper.writableDatabase.execSQL("INSERT ...")

ХОРОШО:
  // :feature:auth знает только про UserDao
  val user = userDao.getUser(id)
```

### 3. Stable Abstractions Principle

```
Стабильные модули должны быть абстрактными
Нестабильные могут быть конкретными

         Абстрактный ←───────────────→ Конкретный
              │                              │
        :core:model/             :feature:auth/
        :core:auth-api/          :feature:profile/
              │                              │
         Редко меняется              Часто меняется
              │                              │
          Много зависящих            Мало зависящих
```

### 4. Acyclic Dependencies

```
Зависимости должны быть АЦИКЛИЧЕСКИМИ (DAG)

✅ ХОРОШО:
  :app → :feature:auth → :core:network → :core:model
                       → :core:database → :core:model

❌ ПЛОХО:
  :feature:auth → :feature:profile
       ↑                │
       └────────────────┘
```

### 5. Interface Segregation для модулей

```
Лучше много маленьких модулей, чем один большой

ПЛОХО:
  :core (всё в одном — 500 классов, 80 зависимостей)

ХОРОШО:
  :core:network    (сетевой слой)
  :core:database   (хранилище)
  :core:model      (domain модели — 0 зависимостей!)
  :core:common     (утилиты)
  :core:ui         (design system)
```

---

## Историческая справка: модули в JavaScript

Для полноты картины — эволюция модулей в JavaScript, принципиально отличающаяся от JVM-подхода:

```javascript
// CommonJS (Node.js, 2009) — синхронный, runtime
const math = require('./math');        // Динамический
module.exports = { add: (a, b) => a + b };

// ES Modules (ES6, 2015) — статический, compile-time
import { add } from './math.js';       // Статический анализ
export const add = (a, b) => a + b;    // Tree shaking возможен
```

| Аспект | CommonJS | ESM | Kotlin/Gradle |
|--------|----------|-----|---------------|
| **Единица** | Файл | Файл | Gradle module (набор файлов) |
| **Видимость** | module.exports | export/import | public/internal/private |
| **Анализ** | Runtime | Static | Static (compile-time) |
| **Tree shaking** | Нет | Да | N/A (JVM classpath) |
| **Транзитивность** | Нет | Нет | api vs implementation |

---

## Проверь себя

> [!question]- Чем `internal` в Kotlin отличается от `package-private` в Java?
> `internal` — видно в пределах одного модуля компиляции (Gradle module, JAR). Не зависит от пакетной структуры. `package-private` (Java default) — видно в пределах одного пакета, но пакет может быть "размазан" по нескольким JAR, что нарушает инкапсуляцию. `internal` строже: модуль = чёткая граница, невозможно "подсмотреть" из другого JAR, создав одноимённый пакет.

> [!question]- Когда использовать `api`, а когда `implementation` в Gradle?
> `api` — только если тип из зависимости появляется в публичных сигнатурах модуля (параметры, возвращаемые значения, публичные свойства, наследование). `implementation` — во всех остальных случаях. Чем меньше `api` зависимостей, тем быстрее incremental build: изменение `implementation`-зависимости не вызывает перекомпиляцию потребителей модуля.

> [!question]- Как решить циклическую зависимость между Gradle модулями?
> Три стратегии: (1) выделить общие интерфейсы и модели в отдельный модуль `:common`, от которого зависят оба; (2) Dependency Inversion — модуль A зависит от интерфейса в `:common`, модуль B реализует этот интерфейс; (3) пересмотреть архитектуру — циклические зависимости часто сигнализируют о нарушении SRP и необходимости перегруппировки ответственностей.

> [!question]- Сценарий: у вас Kotlin-библиотека с internal классами. Java-потребитель вызывает эти классы. Как это возможно и как защититься?
> Kotlin компилирует `internal` в `public` на уровне JVM байткода, добавляя name mangling (суффикс с именем модуля). Java-код технически может вызвать `helper$mymodule()`. Защита: (1) JPMS module-info.java с exports только нужных пакетов; (2) ProGuard/R8 для обфускации internal классов; (3) организационно — code review и линтинг.

---

## Связи

- [[build-systems-theory]] — Build system непосредственно работает с module boundaries: Gradle multi-project build отражает модульную структуру. Incremental build возможен только при чётких границах модулей: если изменился модуль A, пересобираются только A и зависящие от него модули
- [[dependency-resolution]] — Module system определяет "контракт" (что экспортируется), а dependency resolution определяет "какую версию контракта использовать". JPMS `requires` объявляет зависимость между модулями, а Gradle разрешает конкретные артефакты
- [[solid-principles]] — Принципы SOLID определяют качество модульного дизайна. SRP: модуль имеет одну причину для изменения. ISP: лучше много маленьких модулей. DIP: зависимость от абстракций (api vs implementation). Information hiding Parnas (1972) — прямой предшественник SOLID
- [[android-modularization]] — Практическая модульность в Android-проектах: app/feature/core архитектура, navigation между features, manifest merging, resource namespacing

---

## Источники и дальнейшее чтение

Parnas D.L. (1972). *"On the Criteria To Be Used in Decomposing Systems into Modules."* Communications of the ACM. — Основополагающая статья о модульности. Parnas показал, что правильная декомпозиция основана на information hiding (сокрытии design decisions), а не на функциональной декомпозиции. Каждый модуль должен скрывать одно решение, которое может измениться.

Martin R.C. (2017). *"Clean Architecture: A Craftsman's Guide to Software Structure and Design."* — Развивает идеи Parnas. Главы о Component Principles (REP, CCP, CRP) и Component Coupling (ADP, SDP, SAP) дают практические правила проектирования модулей и управления зависимостями.

- [Kotlin Visibility Modifiers](https://kotlinlang.org/docs/visibility-modifiers.html) — официальная документация по public, internal, protected, private
- [Gradle: Declaring Dependencies Between Subprojects](https://docs.gradle.org/current/userguide/declaring_dependencies_between_subprojects.html) — api vs implementation, project dependencies
- [Gradle: The Java Library Plugin](https://docs.gradle.org/current/userguide/java_library_plugin.html) — детали api/implementation scopes
- [Android Modularization Patterns](https://developer.android.com/topic/modularization/patterns) — официальное руководство Google по модульности в Android
- [JPMS Quick Start](https://openjdk.org/projects/jigsaw/quick-start) — введение в Java Platform Module System
- [Mastering API Visibility in Kotlin](https://zsmb.co/mastering-api-visibility-in-kotlin/) — практическое руководство по видимости в Kotlin

---

---

## Ключевые карточки

Что такое information hiding по Parnas и как оно связано с модулями?
?
David Parnas (1972) показал, что декомпозиция на модули должна основываться на сокрытии design decisions, а не на группировке по функциональности. Каждый модуль скрывает одно решение, которое может измениться (формат данных, алгоритм, протокол). В Kotlin/JVM: `internal` скрывает реализацию модуля, `public` — его API.

Чем `internal` в Kotlin отличается от `package-private` в Java?
?
`internal` — видимость в пределах модуля компиляции (Gradle module/JAR). Не зависит от пакетов. `package-private` — видимость в пределах пакета, но пакет может быть в нескольких JAR (split package). `internal` строже: модуль = чёткая компиляционная единица. На JVM internal реализован через name mangling (public с суффиксом модуля).

Когда использовать api vs implementation в Gradle?
?
`api` — тип зависимости появляется в публичных сигнатурах модуля (параметры функций, return types, базовые классы). `implementation` — зависимость используется только внутри. Правило: по умолчанию `implementation`, переключай на `api` только при необходимости. Меньше `api` = быстрее incremental build, потому что изменение `implementation`-зависимости не перекомпилирует потребителей.

Как решить циклическую зависимость между Gradle модулями?
?
Три стратегии: (1) выделить общие интерфейсы/модели в модуль `:common`, от которого зависят оба; (2) Dependency Inversion — один модуль зависит от интерфейса в `:common`, другой реализует; (3) пересмотреть архитектуру — цикл часто означает нарушение SRP. Gradle не позволяет циклические зависимости — build упадёт с ошибкой.

Что такое JPMS и когда его использовать в Kotlin проекте?
?
JPMS (Java 9) — модульная система на уровне JVM с runtime enforcement. module-info.java объявляет requires (зависимости) и exports (публичные пакеты). Использовать в Kotlin: (1) при создании библиотек для Java-потребителей; (2) когда нужен runtime enforcement доступа; (3) для контроля рефлексии (opens). Для внутренних проектов обычно достаточно internal + Gradle modules.

Как expect/actual в Kotlin Multiplatform реализует кроссплатформенную модульность?
?
В commonMain объявляется expect-декларация (контракт без реализации). Каждая платформа (androidMain, iosMain) предоставляет actual-реализацию. Компилятор гарантирует, что все expect имеют actual на каждой целевой платформе. Это information hiding на уровне платформ: общий код не знает деталей реализации, работая с абстрактным контрактом.

Почему feature-модули не должны зависеть друг от друга?
?
Зависимость :feature:A от :feature:B создаёт coupling: изменения в B могут сломать A. Это затрудняет независимую разработку, тестирование и навигацию. Решение: features общаются через абстракции в core модулях (:core:auth-api содержит интерфейс, :feature:auth реализует, :feature:profile потребляет интерфейс). DI связывает на уровне :app.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[dependency-resolution]] | Как разрешаются конфликты версий между модулями |
| Углубиться | [[android-modularization]] | Практическая модульность в Android-проектах с Gradle |
| Смежная тема | [[build-systems-theory]] | Как build system работает с границами модулей |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

*Проверено: 2026-02-19*

---

[[programming-overview|← Programming]] | [[build-systems-theory|Build Systems →]]