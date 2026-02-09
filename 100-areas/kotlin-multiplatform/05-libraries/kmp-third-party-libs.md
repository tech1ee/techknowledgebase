---
title: "Экосистема библиотек KMP: Apollo, Coil, Realm и другие"
created: 2026-01-03
modified: 2026-01-05
tags:
  - topic/jvm
  - topic/kmp
  - libraries
  - apollo
  - coil
  - realm
  - ecosystem
  - type/concept
  - level/intermediate
related:
  - "[[kmp-overview]]"
  - "[[kmp-ktor-networking]]"
  - "[[kmp-sqldelight-database]]"
cs-foundations:
  - "[[library-evaluation-criteria]]"
  - "[[dependency-management]]"
  - "[[caching-strategies]]"
  - "[[graphql-vs-rest]]"
status: published
---

# Экосистема библиотек Kotlin Multiplatform

> **TL;DR:** 3000+ KMP библиотек на klibs.io. Apollo Kotlin 4.x — GraphQL с кэшированием. Coil 3.x — загрузка изображений для Compose MP. Realm — offline-first база с MongoDB sync. multiplatform-settings — key-value storage. Napier/Kermit — логирование. MOKO — resources, permissions, mvvm от IceRock.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить | CS-фундамент |
|------|-------------|-------------|--------------|
| KMP структура | Source sets | [[kmp-project-structure]] | — |
| Gradle | Зависимости | Gradle docs | [[dependency-management]] |
| Ktor | HTTP клиент | [[kmp-ktor-networking]] | [[http-protocol-fundamentals]] |
| Критерии выбора библиотек | Оценка качества | — | [[library-evaluation-criteria]] |

---

## Обзор экосистемы

```
┌─────────────────────────────────────────────────────────────┐
│                   KMP LIBRARY ECOSYSTEM                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📡 Networking                    🖼️ Images                │
│   ├── Ktor (Official)              ├── Coil 3.x             │
│   └── Apollo GraphQL               └── Kamel                │
│                                                             │
│   💾 Database                      🔧 Utilities              │
│   ├── SQLDelight                   ├── multiplatform-settings│
│   ├── Realm                        ├── Napier (logging)     │
│   └── Room KMP                     └── KVault (secure)      │
│                                                             │
│   🎨 UI/Resources                  📊 Analytics             │
│   ├── moko-resources               ├── Firebase KMP         │
│   ├── Compose Resources            └── Mixpanel KMP         │
│   └── Lyricist (i18n)                                       │
│                                                             │
│   🔑 Auth & Security               🧪 Testing               │
│   ├── AppAuth KMP                  ├── Turbine              │
│   └── KVault                       └── MockK                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Поиск библиотек

- **[klibs.io](https://klibs.io)** — официальный каталог от JetBrains (3000+ библиотек)
- **[kmp-awesome](https://github.com/terrakok/kmp-awesome)** — curated list
- **[libs.kmp.icerock.dev](https://libs.kmp.icerock.dev)** — каталог MOKO

---

## Почему выбор библиотек критичен? Теоретические основы

### Library Selection Framework

Выбор библиотеки — это архитектурное решение с долгосрочными последствиями. Framework оценки:

```
┌─────────────────────────────────────────────────────────────────┐
│                    LIBRARY EVALUATION CRITERIA                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   1. PLATFORM COVERAGE (блокирующий критерий)                  │
│      └── Поддерживает ли все нужные targets?                   │
│      └── Android, iOS, JVM, JS, Wasm?                          │
│                                                                 │
│   2. MAINTENANCE STATUS                                         │
│      └── Последний commit < 3 месяцев назад?                   │
│      └── Issues обрабатываются?                                │
│      └── Kotlin version совместимость?                         │
│                                                                 │
│   3. COMMUNITY & BACKING                                        │
│      └── JetBrains/Google/major company?                       │
│      └── GitHub stars, forks                                   │
│      └── Stack Overflow questions                              │
│                                                                 │
│   4. API QUALITY                                                │
│      └── Kotlin-idiomatic?                                     │
│      └── Coroutines support?                                   │
│      └── Type-safe?                                            │
│                                                                 │
│   5. BUNDLE SIZE IMPACT                                         │
│      └── Какой overhead добавит к APK/IPA?                     │
│      └── Transitive dependencies?                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2025 Consolidation: победители определились

Экосистема KMP в 2025 достигла зрелости — для каждой категории есть "де-факто стандарт":

| Категория | Рекомендация 2025 | Почему |
|-----------|------------------|--------|
| **Image Loading** | Coil 3.0 | Kotlin Foundation sponsorship, заменил Kamel |
| **Preferences** | DataStore 1.2+ | Official multiplatform от Google |
| **Logging** | Kermit | Thread-safe, performance-focused (Touchlab) |
| **GraphQL** | Apollo Kotlin 4.x | Единственный mature option |
| **Permissions** | moko-permissions | Stable, proven |

### Coil vs Kamel: история победителя

До 2024 года **Kamel** был популярным выбором для image loading в KMP. В 2024 **Coil 3.0** вышел с multiplatform support и:
- Получил sponsorship от Kotlin Foundation
- Имеет знакомый API для Android разработчиков
- Поддерживает все платформы: Android, iOS, JVM, JS, Wasm

**Результат:** Kamel development замедлился, Coil стал стандартом.

### DataStore vs multiplatform-settings

Google выпустил **DataStore 1.2+** с KMP поддержкой:

| Аспект | DataStore | multiplatform-settings |
|--------|-----------|----------------------|
| API | Flow-based, async | Sync простой |
| Platforms | Android, iOS, Desktop | All + Wasm, JS |
| Backing | Google (official) | Community |
| Use case | Complex typed data | Simple key-value |

**Рекомендация:**
- DataStore для новых проектов без Wasm/JS
- multiplatform-settings если нужен Wasm/JS или максимальная простота

### Kermit vs Napier: thread safety wins

| Аспект | Kermit (Touchlab) | Napier |
|--------|-------------------|--------|
| Thread safety | Excellent (immutable) | Improved (atomics) |
| Performance | Optimized (no atomics on log) | Atomics on each log |
| Crashlytics | Built-in | Available |
| iOS config | Easy | Complex |

**Рекомендация:** Kermit для новых проектов.

---

## Apollo Kotlin (GraphQL)

### Обзор

Apollo Kotlin — strongly-typed GraphQL клиент с кодогенерацией и кэшированием.

**Версия:** 4.3.3

### Настройка

```kotlin
// libs.versions.toml
[versions]
apollo = "4.3.3"

[plugins]
apollo = { id = "com.apollographql.apollo", version.ref = "apollo" }

[libraries]
apollo-runtime = { module = "com.apollographql.apollo:apollo-runtime", version.ref = "apollo" }
apollo-normalized-cache = { module = "com.apollographql.apollo:apollo-normalized-cache", version.ref = "apollo" }
apollo-normalized-cache-sqlite = { module = "com.apollographql.apollo:apollo-normalized-cache-sqlite", version.ref = "apollo" }
```

```kotlin
// build.gradle.kts
plugins {
    alias(libs.plugins.apollo)
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.apollo.runtime)
            implementation(libs.apollo.normalized.cache)
        }
    }
}

apollo {
    service("api") {
        packageName.set("com.example.graphql")
        // GraphQL файлы в src/commonMain/graphql/
    }
}
```

### Использование

```graphql
# src/commonMain/graphql/com/example/graphql/GetUser.graphql
query GetUser($id: ID!) {
    user(id: $id) {
        id
        name
        email
        avatar {
            url
        }
    }
}
```

```kotlin
// Сгенерированный код используется напрямую
class UserRepository(private val apolloClient: ApolloClient) {

    suspend fun getUser(id: String): User? {
        val response = apolloClient.query(GetUserQuery(id)).execute()
        return response.data?.user?.let { user ->
            User(
                id = user.id,
                name = user.name,
                email = user.email,
                avatarUrl = user.avatar?.url
            )
        }
    }

    // С кэшированием
    fun observeUser(id: String): Flow<User?> {
        return apolloClient
            .query(GetUserQuery(id))
            .watch()  // Наблюдает за кэшем
            .map { it.data?.user?.toDomain() }
    }
}

// Конфигурация клиента
val apolloClient = ApolloClient.Builder()
    .serverUrl("https://api.example.com/graphql")
    .normalizedCache(
        normalizedCacheFactory = MemoryCacheFactory(maxSizeBytes = 10 * 1024 * 1024),
        cacheKeyGenerator = TypePolicyCacheKeyGenerator
    )
    .build()
```

---

## Coil 3.x (Image Loading)

### Обзор

Coil — image loading библиотека для Android и Compose Multiplatform.

**Версия:** 3.3.0

### Настройка

```kotlin
// libs.versions.toml
[versions]
coil = "3.3.0"

[libraries]
coil-compose = { module = "io.coil-kt.coil3:coil-compose", version.ref = "coil" }
coil-network-ktor = { module = "io.coil-kt.coil3:coil-network-ktor3", version.ref = "coil" }
```

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.coil.compose)
            implementation(libs.coil.network.ktor)
        }
        jvmMain.dependencies {
            // Для Desktop нужен swing dispatcher
            implementation("org.jetbrains.kotlinx:kotlinx-coroutines-swing:1.10.2")
        }
    }
}
```

### Использование

```kotlin
import coil3.compose.AsyncImage
import coil3.compose.LocalPlatformContext
import coil3.request.ImageRequest

@Composable
fun UserAvatar(url: String, modifier: Modifier = Modifier) {
    AsyncImage(
        model = ImageRequest.Builder(LocalPlatformContext.current)
            .data(url)
            .crossfade(true)
            .build(),
        contentDescription = "Avatar",
        modifier = modifier.size(48.dp).clip(CircleShape),
        contentScale = ContentScale.Crop
    )
}

// С placeholder и error
@Composable
fun ProductImage(url: String) {
    AsyncImage(
        model = url,
        contentDescription = null,
        placeholder = painterResource(Res.drawable.placeholder),
        error = painterResource(Res.drawable.error),
        modifier = Modifier.fillMaxWidth().aspectRatio(1f)
    )
}
```

### Кэширование

```kotlin
import coil3.ImageLoader
import coil3.disk.DiskCache
import coil3.memory.MemoryCache
import coil3.request.CachePolicy

// Кастомный ImageLoader
val imageLoader = ImageLoader.Builder(context)
    .memoryCachePolicy(CachePolicy.ENABLED)
    .diskCachePolicy(CachePolicy.ENABLED)
    .memoryCache {
        MemoryCache.Builder()
            .maxSizePercent(context, 0.25)  // 25% памяти
            .build()
    }
    .diskCache {
        DiskCache.Builder()
            .directory(cacheDir.resolve("image_cache"))
            .maxSizeBytes(100 * 1024 * 1024)  // 100 MB
            .build()
    }
    .build()

// Использование в Compose
CompositionLocalProvider(LocalImageLoader provides imageLoader) {
    App()
}
```

---

## Realm Kotlin

### Обзор

Realm — offline-first объектная база данных с опциональной синхронизацией MongoDB Atlas.

**Версия:** 3.0.0+

### Настройка

```kotlin
// libs.versions.toml
[versions]
realm = "3.0.0"

[plugins]
realm = { id = "io.realm.kotlin", version.ref = "realm" }

[libraries]
realm-base = { module = "io.realm.kotlin:library-base", version.ref = "realm" }
realm-sync = { module = "io.realm.kotlin:library-sync", version.ref = "realm" }  # Для Atlas Sync
```

```kotlin
// build.gradle.kts
plugins {
    alias(libs.plugins.realm)
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.realm.base)
            // implementation(libs.realm.sync)  // Если нужен Atlas Sync
        }
    }
}
```

### Модели

```kotlin
import io.realm.kotlin.types.RealmObject
import io.realm.kotlin.types.annotations.PrimaryKey
import org.mongodb.kbson.ObjectId

class Task : RealmObject {
    @PrimaryKey
    var _id: ObjectId = ObjectId()
    var title: String = ""
    var isComplete: Boolean = false
    var priority: Int = 0
    var dueDate: RealmInstant? = null
}

class User : RealmObject {
    @PrimaryKey
    var _id: ObjectId = ObjectId()
    var name: String = ""
    var tasks: RealmList<Task> = realmListOf()
}
```

### Использование

```kotlin
import io.realm.kotlin.Realm
import io.realm.kotlin.RealmConfiguration
import io.realm.kotlin.ext.query

class TaskRepository {
    private val config = RealmConfiguration.Builder(
        schema = setOf(Task::class, User::class)
    )
        .name("app.realm")
        .schemaVersion(1)
        .build()

    private val realm = Realm.open(config)

    // Query
    fun getAllTasks(): Flow<List<Task>> {
        return realm.query<Task>()
            .sort("priority", Sort.DESCENDING)
            .asFlow()
            .map { it.list }
    }

    // Write
    suspend fun addTask(title: String, priority: Int) {
        realm.write {
            copyToRealm(Task().apply {
                this.title = title
                this.priority = priority
            })
        }
    }

    // Update
    suspend fun toggleComplete(taskId: ObjectId) {
        realm.write {
            val task = query<Task>("_id == $0", taskId).first().find()
            task?.isComplete = !task.isComplete
        }
    }

    // Delete
    suspend fun deleteTask(taskId: ObjectId) {
        realm.write {
            val task = query<Task>("_id == $0", taskId).first().find()
            task?.let { delete(it) }
        }
    }

    fun close() {
        realm.close()
    }
}
```

---

## multiplatform-settings

### Обзор

Простое key-value хранилище для KMP (SharedPreferences на Android, NSUserDefaults на iOS).

**Версия:** 1.3.0

### Настройка

```kotlin
// libs.versions.toml
[versions]
multiplatform-settings = "1.3.0"

[libraries]
multiplatform-settings = { module = "com.russhwolf:multiplatform-settings", version.ref = "multiplatform-settings" }
multiplatform-settings-coroutines = { module = "com.russhwolf:multiplatform-settings-coroutines", version.ref = "multiplatform-settings" }
```

### Использование

```kotlin
import com.russhwolf.settings.Settings
import com.russhwolf.settings.get
import com.russhwolf.settings.set

// Platform-specific factory
expect fun createSettings(): Settings

// commonMain
class UserPreferences(private val settings: Settings) {

    var isOnboardingComplete: Boolean
        get() = settings["onboarding_complete", false]
        set(value) { settings["onboarding_complete"] = value }

    var theme: String
        get() = settings["theme", "system"]
        set(value) { settings["theme"] = value }

    var authToken: String?
        get() = settings.getStringOrNull("auth_token")
        set(value) {
            if (value != null) settings["auth_token"] = value
            else settings.remove("auth_token")
        }

    fun clear() {
        settings.clear()
    }
}

// androidMain
actual fun createSettings(): Settings {
    val context: Context = // get from DI
    return SharedPreferencesSettings(
        context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
    )
}

// iosMain
actual fun createSettings(): Settings {
    return NSUserDefaultsSettings(NSUserDefaults.standardUserDefaults)
}
```

---

## Napier (Logging)

### Обзор

Logging библиотека для KMP, похожа на Timber.

**Версия:** 2.7.1

### Настройка

```kotlin
// libs.versions.toml
[versions]
napier = "2.7.1"

[libraries]
napier = { module = "io.github.aakira:napier", version.ref = "napier" }
```

### Использование

```kotlin
import io.github.aakira.napier.Napier
import io.github.aakira.napier.DebugAntilog

// Инициализация (в Application/AppDelegate)
fun initLogging() {
    if (BuildConfig.DEBUG) {  // или Platform check
        Napier.base(DebugAntilog())
    }
}

// Использование
class UserRepository {
    fun getUser(id: String) {
        Napier.d("Fetching user: $id")
        try {
            // ...
            Napier.i("User fetched successfully")
        } catch (e: Exception) {
            Napier.e("Failed to fetch user", e)
        }
    }
}

// Уровни логирования
Napier.v("Verbose")
Napier.d("Debug")
Napier.i("Info")
Napier.w("Warning")
Napier.e("Error")
Napier.wtf("What a Terrible Failure")
```

### Альтернатива: Kermit

```kotlin
// От Touchlab, интеграция с Crashlytics
implementation("co.touchlab:kermit:2.0.4")

val logger = Logger.withTag("UserRepository")
logger.d { "Debug message" }
```

---

## MOKO Libraries

### Обзор

MOKO — набор библиотек от IceRock для KMP.

### moko-resources

```kotlin
// Мультиплатформенные строки, изображения, шрифты
implementation("dev.icerock.moko:resources:0.24.4")
implementation("dev.icerock.moko:resources-compose:0.24.4")

// Использование
Text(stringResource(MR.strings.hello_world))
Image(painterResource(MR.images.logo))
```

### moko-permissions

```kotlin
// Запрос разрешений
implementation("dev.icerock.moko:permissions:0.18.0")
implementation("dev.icerock.moko:permissions-compose:0.18.0")

@Composable
fun CameraButton() {
    val permissionsController = rememberPermissionsController()

    Button(onClick = {
        permissionsController.providePermission(Permission.Camera)
    }) {
        Text("Open Camera")
    }
}
```

### moko-mvvm

```kotlin
// ViewModel с lifecycle
implementation("dev.icerock.moko:mvvm-core:0.16.1")
implementation("dev.icerock.moko:mvvm-compose:0.16.1")
```

---

## Другие полезные библиотеки

| Библиотека | Назначение | Версия |
|------------|------------|--------|
| **KVault** | Secure key-value (Keychain/Keystore) | 1.12.0 |
| **Kamel** | Image loading (альтернатива Coil) | 1.0.1 |
| **Kottie** | Lottie animations | 2.2.3 |
| **KMP-NativeCoroutines** | Coroutines → Swift | 1.0.0-ALPHA-37 |
| **SKIE** | Swift-friendly KMP | 0.10.0 |
| **Lyricist** | Type-safe i18n | 1.7.0 |
| **Kable** | Bluetooth LE | 1.0.0 |
| **multiplatform-paging** | Paging 3 for KMP | 3.3.0-alpha02 |

---

## Добавление зависимостей

### Правила

```kotlin
// ✅ commonMain — если библиотека multiplatform
commonMain.dependencies {
    implementation(libs.ktor.client.core)
    implementation(libs.sqldelight.coroutines)
}

// ✅ platformMain — если нужна платформо-специфичная версия
androidMain.dependencies {
    implementation(libs.ktor.client.okhttp)
}
iosMain.dependencies {
    implementation(libs.ktor.client.darwin)
}

// ⚠️ Проверяйте совместимость версий Kotlin!
```

### Проверка KMP поддержки

1. **klibs.io** — фильтр по платформам
2. **GitHub** — смотрите targets в build.gradle.kts
3. **Maven** — ищите `-iosx64`, `-androidnativearm64` артефакты

---

## Best Practices

| Практика | Описание |
|----------|----------|
| ✅ Проверяйте targets | Не все библиотеки поддерживают все платформы |
| ✅ Version catalogs | Централизованное управление версиями |
| ✅ Минимум зависимостей | Каждая добавляет к размеру бинарника |
| ✅ klibs.io | Первый источник для поиска |
| ⚠️ Kotlin версия | Библиотека должна быть совместима |
| ⚠️ Альфа/Бета | Используйте с осторожностью в production |

---

## Мифы и заблуждения

### Миф 1: "Больше библиотек = лучше"

**Реальность:** Каждая библиотека:
- Увеличивает размер бинарника
- Добавляет potential security vulnerabilities
- Требует обновлений и maintenance
- Может конфликтовать с другими

**Правило:** Добавляйте библиотеку только если она решает реальную проблему, которую сложно решить самостоятельно.

### Миф 2: "Популярная библиотека = хорошая библиотека"

**Реальность:** GitHub stars не гарантируют:
- Активную поддержку (может быть abandoned)
- KMP совместимость (популярна на Android ≠ работает в KMP)
- Production-ready качество

**Проверяйте:** дату последнего commit, открытые issues, Kotlin version compatibility.

### Миф 3: "MOKO библиотеки устарели после Compose Resources"

**Реальность:** Частично верно:
- **moko-resources** — да, Compose Resources 1.8+ покрывает большинство use cases
- **moko-permissions** — всё ещё актуален, Compose не имеет аналога
- **moko-mvvm** — менее актуален после AndroidX ViewModel multiplatform

### Миф 4: "Realm лучше SQLDelight для offline-first"

**Реальность:** Зависит от требований:

| Сценарий | Лучший выбор |
|----------|-------------|
| MongoDB Atlas sync | Realm |
| Custom backend | SQLDelight + Ktor |
| Complex queries | SQLDelight (SQL power) |
| Simple objects | Realm (easier API) |

**Важно:** Realm добавляет ~3-5MB к размеру приложения.

### Миф 5: "Apollo только для GraphQL-first архитектур"

**Реальность:** Apollo полезен даже если backend REST:
- Некоторые backend предоставляют GraphQL wrapper над REST
- GraphQL BFF (Backend for Frontend) паттерн
- Apollo кэширование работает и для REST-like queries

Но если у вас чистый REST — используйте Ktor + kotlinx-serialization.

### Миф 6: "Coil 3.0 — просто порт Android версии"

**Реальность:** Coil 3.0 — полностью переписанная библиотека:
- Kotlin-first архитектура
- Platform-specific оптимизации (не wrapper над Android API)
- Поддержка разных network backends (OkHttp, Ktor)

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [klibs.io](https://klibs.io) | Portal | Официальный каталог |
| [kmp-awesome](https://github.com/terrakok/kmp-awesome) | GitHub | Curated list |
| [Apollo Kotlin](https://www.apollographql.com/docs/kotlin) | Official | GraphQL docs |
| [Coil](https://coil-kt.github.io/coil/) | Official | Image loading |
| [Realm Kotlin](https://github.com/realm/realm-kotlin) | GitHub | Database |
| [MOKO](http://moko.icerock.dev/) | Official | IceRock libraries |

### CS-фундамент

| Концепция | Связь с библиотеками | Где углубить |
|-----------|---------------------|--------------|
| [[library-evaluation-criteria]] | Критерии выбора библиотек | "Software Architecture in Practice" |
| [[dependency-management]] | Transitive dependencies, conflicts | Gradle documentation |
| [[caching-strategies]] | Apollo cache, Coil cache | Cache-Aside, Write-Through patterns |
| [[graphql-vs-rest]] | Apollo vs Ktor выбор | GraphQL specification |

---

*Проверено: 2026-01-09 | KMP Ecosystem*
