---
title: "Adapter: совместимость несовместимых интерфейсов"
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
  - "[[decorator-pattern]]"
  - "[[kotlin-interop]]"
  - "[[kotlin-advanced-features]]"
---

# Adapter: совместимость несовместимых интерфейсов

Два компонента, которые должны работать вместе, но не могут — интерфейсы не совпадают. Переписать их нельзя: один из библиотеки, другой из legacy. В Java это значит написать wrapper-класс с forwarding. В Kotlin часто хватает extension function, `typealias` или SAM-конверсии — язык адаптирует за тебя. А для callback-to-coroutine есть `suspendCancellableCoroutine` и `callbackFlow` — адаптеры, которые превращают колбэчный ад в последовательный код.

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Adapter (Wrapper)** | Объект, преобразующий интерфейс одного класса в интерфейс, ожидаемый клиентом |
| **Target** | Интерфейс, который нужен клиенту |
| **Adaptee** | Существующий класс с несовместимым интерфейсом |
| **Class Adapter** | Адаптер через наследование (множественное наследование, в Kotlin — через интерфейс + класс) |
| **Object Adapter** | Адаптер через композицию (содержит ссылку на adaptee) |
| **SAM conversion** | Single Abstract Method — Kotlin автоматически конвертирует лямбду в Java-интерфейс с одним методом |
| **Extension function** | Функция, «добавленная» к существующему типу без наследования |

---

## Проблема: несовместимые интерфейсы

Типичные сценарии, где нужен адаптер:

```
Сценарий 1: Интеграция с legacy
┌──────────┐          ┌──────────────┐
│  Новый   │  ✗ ──→   │   Legacy     │
│  код     │  не      │   библиотека │
│ (Kotlin) │  совпа-  │   (Java)     │
│          │  дают    │              │
└──────────┘          └──────────────┘

Сценарий 2: Замена компонента
Было:    MyApp → OldAnalytics.track(event: String)
Стало:   MyApp → NewAnalytics.logEvent(name: String, params: Map)
Проблема: 200 вызовов OldAnalytics в коде

Сценарий 3: Callback → Coroutine
Было:    api.fetchUser(id, callback)
Нужно:   val user = api.fetchUser(id)  // suspend
```

---

## Классический Adapter (GoF)

### Структура

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADAPTER (Object Adapter)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Client ──→ Target (interface)      Adaptee                    │
│              └── request()           └── specificRequest()      │
│                     ↑                       ↑                   │
│                     │                       │ содержит          │
│                  Adapter ───────────────────┘                   │
│                  └── request() {                                │
│                        adaptee.specificRequest()                │
│                      }                                          │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    ADAPTER (Class Adapter)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Client ──→ Target (interface)      Adaptee (class)            │
│              └── request()           └── specificRequest()      │
│                     ↑                       ↑                   │
│                     │ implements             │ extends           │
│                  Adapter ───────────────────┘                   │
│                  └── request() {                                │
│                        specificRequest() // наследуется         │
│                      }                                          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Participants

| Компонент | Роль | Пропустишь — сломаешь |
|-----------|------|----------------------|
| **Target** | Интерфейс, ожидаемый клиентом | Без него клиент не сможет работать с адаптером |
| **Adaptee** | Существующий класс, который нужно адаптировать | То, что адаптируем |
| **Adapter** | Преобразует вызовы Target в вызовы Adaptee | Мост между несовместимыми интерфейсами |
| **Client** | Работает с Target | Не должен знать об Adaptee |

### Class Adapter vs Object Adapter

| Критерий | Class Adapter | Object Adapter |
|----------|--------------|----------------|
| Механизм | Наследование от Adaptee | Композиция (содержит Adaptee) |
| Гибкость | Один Adaptee | Любой подтип Adaptee |
| Переопределение | Может override методы Adaptee | Нет (работает через интерфейс) |
| Kotlin-совместимость | Ограничен (классы final) | Предпочтительный подход |

> [!info] Kotlin-нюанс
> В Kotlin классы `final` по умолчанию, поэтому Class Adapter (через наследование) часто невозможен. Object Adapter (через композицию) — стандартный подход.

---

## Kotlin-идиоматичные адаптеры

### 1. Extension functions как адаптеры

Самый лёгкий способ — не создавая новый класс, добавить метод, адаптирующий один интерфейс в другой:

```kotlin
// Adaptee: Java Date (legacy API)
// Target: Kotlin Instant (modern API)
fun java.util.Date.toKotlinInstant(): Instant =
    this.toInstant()

fun Instant.toJavaDate(): java.util.Date =
    java.util.Date.from(this)

// Adaptee: Android Cursor
// Target: Kotlin List<User>
fun Cursor.toUserList(): List<User> = buildList {
    while (moveToNext()) {
        add(
            User(
                id = getLong(getColumnIndexOrThrow("id")),
                name = getString(getColumnIndexOrThrow("name")),
                email = getString(getColumnIndexOrThrow("email"))
            )
        )
    }
}

// Использование — адаптация выглядит как метод объекта
val instant = legacyDate.toKotlinInstant()
val users = cursor.toUserList()
```

**Когда это работает:** один метод адаптации, stateless, нет сложной логики трансформации.

**Когда не работает:** нужно адаптировать целый интерфейс (5+ методов), нужно состояние, нужна полиморфная подмена.

> [!info] Kotlin-нюанс
> Extension functions компилируются в static-методы: `fun Date.toKotlinInstant()` становится `public static Instant toKotlinInstant(Date $this)`. Никакого runtime overhead, но нет доступа к private полям.

### 2. `typealias` как type adapter

Когда два типа семантически идентичны, но имеют разные имена:

```kotlin
// Адаптация callback-стиля к Kotlin-идиомам
typealias Callback<T> = (Result<T>) -> Unit
typealias Predicate<T> = (T) -> Boolean
typealias Mapper<T, R> = (T) -> R

// Адаптация между модулями
typealias DomainUser = com.app.domain.model.User
typealias ApiUser = com.app.data.api.model.UserResponse
typealias DbUser = com.app.data.db.entity.UserEntity

// Использование
fun fetchUsers(callback: Callback<List<DomainUser>>) {
    api.getUsers { result ->
        callback(result.map { apiUsers -> apiUsers.map { it.toDomain() } })
    }
}
```

> [!warning] Ограничение typealias
> `typealias` **не создаёт новый тип** — это просто синоним. `typealias UserId = Long` и `typealias OrderId = Long` взаимозаменяемы! Для type safety используй `@JvmInline value class`.

### 3. Wrapper class с `by` — полная адаптация интерфейса

Когда нужно адаптировать целый интерфейс, `by` делегирует то, что совпадает, а ты переопределяешь то, что отличается:

```kotlin
// Target: новый интерфейс аналитики
interface Analytics {
    fun logEvent(name: String, params: Map<String, Any> = emptyMap())
    fun setUserId(id: String)
    fun setUserProperty(key: String, value: String)
}

// Adaptee: старый трекер (изменить нельзя — из SDK)
class LegacyTracker {
    fun track(eventName: String) { /* ... */ }
    fun trackWithData(eventName: String, data: Bundle) { /* ... */ }
    fun identify(userId: String) { /* ... */ }
    fun setProperty(name: String, value: Any) { /* ... */ }
}

// Adapter: преобразует вызовы Analytics в вызовы LegacyTracker
class LegacyAnalyticsAdapter(
    private val tracker: LegacyTracker
) : Analytics {

    override fun logEvent(name: String, params: Map<String, Any>) {
        if (params.isEmpty()) {
            tracker.track(name)
        } else {
            tracker.trackWithData(name, params.toBundle())
        }
    }

    override fun setUserId(id: String) {
        tracker.identify(id)
    }

    override fun setUserProperty(key: String, value: String) {
        tracker.setProperty(key, value)
    }

    private fun Map<String, Any>.toBundle() = Bundle().apply {
        forEach { (key, value) ->
            when (value) {
                is String -> putString(key, value)
                is Int -> putInt(key, value)
                is Long -> putLong(key, value)
                is Double -> putDouble(key, value)
                is Boolean -> putBoolean(key, value)
                else -> putString(key, value.toString())
            }
        }
    }
}

// Клиент работает с Analytics — не знает о LegacyTracker
class OrderViewModel(private val analytics: Analytics) {
    fun onOrderCompleted(order: Order) {
        analytics.logEvent("order_completed", mapOf(
            "order_id" to order.id,
            "total" to order.total,
            "items_count" to order.items.size
        ))
    }
}
```

### 4. Coroutine адаптеры: callback → suspend/Flow

Это **самый практически важный** тип адаптера в Kotlin-мире — превращение callback-based API в suspend-функции и Flow.

#### `suspendCancellableCoroutine` — одноразовый callback → suspend

```kotlin
// Adaptee: callback-based API
interface LocationClient {
    fun getCurrentLocation(
        onSuccess: (Location) -> Unit,
        onError: (Exception) -> Unit
    )
}

// Adapter: suspend-обёртка
suspend fun LocationClient.awaitCurrentLocation(): Location =
    suspendCancellableCoroutine { continuation ->
        getCurrentLocation(
            onSuccess = { location ->
                continuation.resume(location)
            },
            onError = { exception ->
                continuation.resumeWithException(exception)
            }
        )

        continuation.invokeOnCancellation {
            // Очистка при отмене корутины
            // cancelLocationRequest()
        }
    }

// Использование — вместо callback hell
suspend fun showUserLocation() {
    try {
        val location = locationClient.awaitCurrentLocation()  // suspend!
        updateMap(location)
    } catch (e: Exception) {
        showError(e)
    }
}
```

#### `callbackFlow` — многоразовый listener → Flow

```kotlin
// Adaptee: listener-based API (подписка на обновления)
interface SensorManager {
    fun registerListener(listener: SensorListener)
    fun unregisterListener(listener: SensorListener)
}

interface SensorListener {
    fun onSensorChanged(value: Float)
    fun onAccuracyChanged(accuracy: Int)
}

// Adapter: Flow-обёртка
fun SensorManager.sensorFlow(): Flow<Float> = callbackFlow {
    val listener = object : SensorListener {
        override fun onSensorChanged(value: Float) {
            trySend(value)  // Отправляем в Flow
        }
        override fun onAccuracyChanged(accuracy: Int) {
            // игнорируем или можно отправить sealed class
        }
    }

    registerListener(listener)

    awaitClose {
        unregisterListener(listener)  // Очистка при завершении Flow
    }
}

// Использование — стандартный Flow
sensorManager.sensorFlow()
    .filter { it > threshold }
    .debounce(100)
    .collect { value ->
        updateUI(value)
    }
```

> [!info] Kotlin-нюанс
> `suspendCancellableCoroutine` для one-shot (получить результат один раз). `callbackFlow` для stream (поток значений). Это не просто обёртки — они корректно обрабатывают отмену: `invokeOnCancellation` и `awaitClose` гарантируют cleanup.

---

## Java interop: встроенные адаптеры Kotlin

Kotlin сам является «адаптером» между Kotlin-стилем и Java-миром:

### SAM-конверсия — автоматический адаптер

```kotlin
// Java-интерфейс с одним методом
// public interface OnClickListener { void onClick(View v); }

// Java-стиль (verbose)
button.setOnClickListener(object : View.OnClickListener {
    override fun onClick(v: View) {
        handleClick(v)
    }
})

// Kotlin SAM-конверсия — автоматический адаптер
button.setOnClickListener { v -> handleClick(v) }
// Компилятор генерирует анонимный класс за тебя
```

### `@JvmStatic`, `@JvmOverloads` — адаптация Kotlin для Java

```kotlin
class NetworkConfig {
    companion object {
        @JvmStatic  // Адаптер: Kotlin companion → Java static
        fun default(): NetworkConfig = NetworkConfig()
    }

    @JvmOverloads  // Адаптер: Kotlin default params → Java overloads
    fun configure(
        timeout: Long = 30_000,
        retries: Int = 3,
        baseUrl: String = "https://api.example.com"
    ) { /* ... */ }
}

// Из Java можно вызвать:
// NetworkConfig.default()         — благодаря @JvmStatic
// config.configure()              — все defaults
// config.configure(5000)          — timeout
// config.configure(5000, 5)       — timeout + retries
```

### `asFlow()` / `asLiveData()` — kotlinx адаптеры

```kotlin
// Адаптация между реактивными типами
val flow: Flow<User> = liveData.asFlow()          // LiveData → Flow
val liveData: LiveData<User> = flow.asLiveData()   // Flow → LiveData

// Адаптация Java Stream → Kotlin Sequence/List
val kotlinList = javaStream.toList()               // Stream → List
val sequence = javaStream.asSequence()             // Stream → Sequence

// Адаптация RxJava → Coroutines (kotlinx-coroutines-rx3)
val flow = observable.asFlow()                     // Observable → Flow
val deferred = single.asDeferred()                 // Single → Deferred
```

---

## Real-world примеры

### Retrofit `CallAdapter` — адаптация HTTP-вызовов

Retrofit `CallAdapter.Factory` — классический пример паттерна Adapter. Он адаптирует `Call<T>` (HTTP-вызов) в нужный тип результата:

```kotlin
// Retrofit по умолчанию возвращает Call<T>
interface ApiService {
    @GET("users/{id}")
    fun getUser(@Path("id") id: Long): Call<UserResponse>
}

// С suspend — Retrofit адаптирует Call в suspend автоматически (2.6.0+)
interface ApiService {
    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: Long): UserResponse

    @GET("users/{id}")
    suspend fun getUserResponse(@Path("id") id: Long): Response<UserResponse>
}

// Custom CallAdapter для Result<T>
class ResultCallAdapter<T>(
    private val responseType: Type
) : CallAdapter<T, Flow<Result<T>>> {

    override fun responseType(): Type = responseType

    override fun adapt(call: Call<T>): Flow<Result<T>> = flow {
        emit(Result.Loading)
        try {
            val response = call.awaitResponse()
            if (response.isSuccessful) {
                emit(Result.Success(response.body()!!))
            } else {
                emit(Result.Error(HttpException(response)))
            }
        } catch (e: Exception) {
            emit(Result.Error(e))
        }
    }
}
```

### Room TypeConverters — адаптация типов для БД

```kotlin
// Room не знает как хранить Instant или List<String>
// TypeConverter = адаптер между Kotlin-типом и SQLite-типом

class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Instant? =
        value?.let { Instant.ofEpochMilli(it) }

    @TypeConverter
    fun toTimestamp(instant: Instant?): Long? =
        instant?.toEpochMilli()

    @TypeConverter
    fun fromStringList(value: String?): List<String> =
        value?.split(",")?.filter { it.isNotBlank() } ?: emptyList()

    @TypeConverter
    fun toStringList(list: List<String>): String =
        list.joinToString(",")
}

// Регистрация
@Database(entities = [UserEntity::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase()
```

### Android `ListAdapter` — адаптация данных для RecyclerView

```kotlin
// Target: RecyclerView ожидает ViewHolder-based adapter
// Adaptee: List<Article> — просто данные

class ArticleListAdapter : ListAdapter<Article, ArticleViewHolder>(
    object : DiffUtil.ItemCallback<Article>() {
        override fun areItemsTheSame(old: Article, new: Article) =
            old.id == new.id

        override fun areContentsTheSame(old: Article, new: Article) =
            old == new  // data class equals
    }
) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) =
        ArticleViewHolder(
            ItemArticleBinding.inflate(
                LayoutInflater.from(parent.context), parent, false
            )
        )

    override fun onBindViewHolder(holder: ArticleViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}

// Использование — адаптер «переводит» List<Article> в ViewHolder-ы
adapter.submitList(articles)  // DiffUtil рассчитает изменения
```

### Adapter между слоями архитектуры (mapper)

```kotlin
// API → Domain → UI: каждый переход = адаптация

// Data layer model
data class UserResponse(
    @SerializedName("user_id") val userId: Long,
    @SerializedName("full_name") val fullName: String,
    @SerializedName("avatar_url") val avatarUrl: String?,
    @SerializedName("created_at") val createdAt: String
)

// Domain model
data class User(
    val id: UserId,
    val name: String,
    val avatarUrl: String?,
    val memberSince: Instant
)

// Adapter: extension function как mapper
fun UserResponse.toDomain() = User(
    id = UserId(userId),
    name = fullName,
    avatarUrl = avatarUrl,
    memberSince = Instant.parse(createdAt)
)

fun User.toUiModel() = UserUiModel(
    displayName = name,
    avatarUrl = avatarUrl ?: DEFAULT_AVATAR,
    memberSinceText = memberSince.formatRelative()  // "2 года назад"
)
```

---

## Adapter vs Decorator vs Facade

```
┌────────────────────────────────────────────────────────────────┐
│                    СРАВНЕНИЕ ПАТТЕРНОВ                          │
├──────────┬───────────────┬───────────────┬─────────────────────┤
│          │   Adapter     │   Decorator   │   Facade            │
├──────────┼───────────────┼───────────────┼─────────────────────┤
│ Цель     │ Сделать       │ Добавить      │ Упростить           │
│          │ совместимым   │ поведение     │ интерфейс           │
├──────────┼───────────────┼───────────────┼─────────────────────┤
│ Интерфейс│ Меняет        │ Сохраняет     │ Создаёт новый       │
│          │ (A → B)       │ (A → A)       │ (упрощённый)        │
├──────────┼───────────────┼───────────────┼─────────────────────┤
│ Стекинг  │ Обычно нет    │ Да            │ Нет                 │
├──────────┼───────────────┼───────────────┼─────────────────────┤
│ Kotlin   │ Extension fn, │ `by` keyword  │ Object/function     │
│          │ typealias     │               │ с упрощённым API    │
└──────────┴───────────────┴───────────────┴─────────────────────┘
```

**Мнемоника:**
- **Adapter** = переводчик (переводит с одного «языка» на другой)
- **Decorator** = украшение (добавляет к тому же «языку»)
- **Facade** = ресепшн (один простой интерфейс вместо сложной системы)

---

## Anti-patterns

### 1. Adapter с бизнес-логикой

```kotlin
// ❌ Плохо: адаптер делает больше, чем адаптирует
class UserAdapter(private val api: LegacyApi) : UserRepository {
    override fun getUser(id: Long): User {
        val response = api.fetchUser(id)

        // Это НЕ адаптация — это бизнес-логика!
        if (response.isBlocked) {
            notifyAdmin(response)
            throw BlockedUserException(id)
        }

        // Вот это адаптация:
        return User(
            id = response.userId,
            name = response.fullName
        )
    }
}

// ✅ Лучше: адаптер только адаптирует, логика в UseCase
class UserApiAdapter(private val api: LegacyApi) : UserRepository {
    override fun getUser(id: Long): User {
        val response = api.fetchUser(id)
        return response.toUser()  // только маппинг
    }
}

class GetUserUseCase(private val repo: UserRepository) {
    fun execute(id: Long): User {
        val user = repo.getUser(id)
        if (user.isBlocked) throw BlockedUserException(id)
        return user
    }
}
```

### 2. Слишком много адаптеров — сигнал неверной абстракции

```kotlin
// ❌ Плохо: адаптер на каждый чих
class FirebaseToAnalytics : Analytics { ... }
class MixpanelToAnalytics : Analytics { ... }
class AmplitudeToAnalytics : Analytics { ... }
class AppsFlyerToAnalytics : Analytics { ... }
class AdjustToAnalytics : Analytics { ... }

// Если 5+ адаптеров для одного интерфейса — возможно,
// интерфейс Analytics слишком специфичен или слишком широк.

// ✅ Лучше: пересмотреть абстракцию
interface EventTracker {
    fun track(event: AnalyticsEvent)
}
// Один метод, один sealed class для событий — адаптеры проще
```

### 3. Bi-directional adapter (двусторонний)

```kotlin
// ❌ Плохо: адаптер в обе стороны создаёт запутанные зависимости
class BiDirectionalAdapter : OldSystem, NewSystem {
    override fun oldMethod() { /* адаптирует к new */ }
    override fun newMethod() { /* адаптирует к old */ }
    // Кто от кого зависит? Непонятно.
}

// ✅ Лучше: два отдельных адаптера с ясным направлением
class OldToNewAdapter(old: OldSystem) : NewSystem { ... }
class NewToOldAdapter(new: NewSystem) : OldSystem { ... }
```

---

## Проверь себя

> [!question]- В чём разница между Adapter и Decorator?
> Adapter меняет интерфейс (A → B) — делает несовместимые интерфейсы совместимыми. Decorator сохраняет интерфейс (A → A) — добавляет поведение. Adapter обычно не стекуется, Decorator — стекуется. Пример: `UserResponse.toDomain()` — адаптер (меняет тип). `LoggingRepository by delegate` — декоратор (тот же интерфейс, добавлено логирование).

> [!question]- Почему extension function — это адаптер?
> Extension function добавляет метод к типу, не модифицируя его. `fun Date.toKotlinInstant(): Instant` адаптирует Java Date к Kotlin Instant — как Object Adapter, но без создания wrapper-класса. Ограничение: подходит только для stateless адаптации одного метода. Для целого интерфейса нужен wrapper class.

> [!question]- Когда `suspendCancellableCoroutine`, а когда `callbackFlow`?
> `suspendCancellableCoroutine` — для one-shot callback (получить один результат). `callbackFlow` — для listener/stream (поток значений). Пример: получить текущую геолокацию — `suspendCancellableCoroutine`. Подписаться на обновления датчика — `callbackFlow`. Оба корректно обрабатывают отмену через `invokeOnCancellation` и `awaitClose`.

> [!question]- Почему Adapter не должен содержать бизнес-логику?
> Single Responsibility: адаптер отвечает только за трансформацию интерфейсов. Если добавить бизнес-логику — адаптер становится God Object, его невозможно переиспользовать, сложно тестировать. Бизнес-логика должна быть в UseCase/Service, адаптер — только маппинг и делегирование.

> [!question]- Как Kotlin сам выступает «адаптером» при работе с Java?
> SAM-конверсия (лямбда → Java-интерфейс), `@JvmStatic` (companion → static), `@JvmOverloads` (default params → overloads), `asFlow()`/`asLiveData()` (между реактивными типами). Kotlin автоматически генерирует адаптерный код в bytecode, минимизируя ручную работу по интеграции.

---

## Ключевые карточки

Что такое Adapter и какую проблему решает?
?
Структурный паттерн: преобразует интерфейс класса в интерфейс, ожидаемый клиентом. Решает проблему несовместимых интерфейсов при интеграции legacy/сторонних библиотек. Два варианта: Class Adapter (наследование) и Object Adapter (композиция). В Kotlin предпочтителен Object Adapter, т.к. классы final по умолчанию.

Какие Kotlin-идиомы заменяют классический Adapter?
?
Четыре подхода: (1) extension function — для одного метода адаптации; (2) typealias — синоним типа (без type safety); (3) wrapper class с `by` — полная адаптация интерфейса; (4) coroutine adapters — `suspendCancellableCoroutine` (one-shot callback → suspend) и `callbackFlow` (listener → Flow).

Чем отличаются `suspendCancellableCoroutine` и `callbackFlow`?
?
`suspendCancellableCoroutine` — для одноразового callback: вызвал → получил результат → done. Cleanup через `invokeOnCancellation`. `callbackFlow` — для потока значений (listener): подписался → получаешь обновления. Cleanup через `awaitClose`. Оба автоматически обрабатывают отмену корутины.

Чем Adapter отличается от Facade?
?
Adapter меняет интерфейс одного класса (A → B). Facade создаёт упрощённый интерфейс для группы классов. Adapter работает с одним adaptee, Facade — с подсистемой. Adapter про совместимость, Facade про упрощение. В Kotlin: Adapter часто extension function, Facade — object или функция-обёртка.

Что такое SAM-конверсия в Kotlin?
?
Single Abstract Method — Kotlin автоматически конвертирует лямбду в Java-интерфейс с одним абстрактным методом: `button.setOnClickListener { handleClick(it) }` вместо анонимного класса. Компилятор генерирует адаптерный код. Работает только с Java-интерфейсами; для Kotlin-интерфейсов нужно `fun interface`.

Что такое Retrofit CallAdapter?
?
Adapter, преобразующий `Call<T>` (сырой HTTP-вызов) в нужный тип: suspend function, `Flow<T>`, `Result<T>`. С Retrofit 2.6.0+ suspend поддерживается нативно. Custom CallAdapter.Factory позволяет адаптировать к любому типу — классический пример паттерна Adapter в production.

Когда Adapter — антипаттерн?
?
Три сигнала: (1) адаптер содержит бизнес-логику (должен только маппить); (2) 5+ адаптеров для одного интерфейса (пересмотри абстракцию); (3) двусторонний адаптер (запутанные зависимости — лучше два однонаправленных).

Зачем нужны mapper-функции между слоями архитектуры?
?
`UserResponse.toDomain()` и `User.toUiModel()` — адаптеры между слоями (Data → Domain → UI). Каждый слой имеет свою модель данных: API-модель с `@SerializedName`, Domain-модель с value class, UI-модель с форматированными строками. Маппер изолирует слои друг от друга.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Смежный паттерн | [[decorator-pattern]] | Decorator тоже оборачивает, но сохраняет интерфейс |
| Обзор | [[design-patterns-overview]] | Место Adapter среди 23 GoF-паттернов |
| Kotlin-deep | [[kotlin-interop]] | Java interop, SAM-конверсии, annotations |
| Kotlin-deep | [[kotlin-advanced-features]] | Extensions, delegates, inline — инструменты адаптации |
| Архитектура | [[android-architecture-patterns]] | Где живут адаптеры в Clean Architecture |
| Android | [[android-clean-architecture]] | Adapter/Mapper между слоями (Dto → Domain → UiModel) |

---

## Источники

### Первоисточники
- Gamma E., Helm R., Johnson R., Vlissides J. *Design Patterns: Elements of Reusable Object-Oriented Software* (1994) — оригинальное описание Adapter (Chapter 4: Structural Patterns)
- Bloch J. *Effective Java*, 3rd Edition (2018) — Item 18: "Favor composition over inheritance" — обоснование Object Adapter

### Kotlin-специфичные
- Moskala M. *Effective Kotlin* (2021) — Extension functions, delegation, interop best practices
- [Kotlin Documentation: Extensions](https://kotlinlang.org/docs/extensions.html) — официальная документация по extension functions
- [Kotlin Documentation: Calling Java from Kotlin](https://kotlinlang.org/docs/java-interop.html) — Java interop, SAM-конверсии
- [Kotlin-Java Interop Guide | Android Developers](https://developer.android.com/kotlin/interop) — best practices от Google
- [Baeldung: Extension Functions in Kotlin](https://www.baeldung.com/kotlin/extension-methods) — практический разбор

### Coroutine-адаптеры
- [Simplifying APIs with coroutines and Flow](https://manuelvivo.dev/simplifying-apis-coroutines) — Manuel Vivo, Google. Подробное руководство по callback → coroutine адаптации
- [Kotlin Academy: How to turn callbacks into suspend and Flow](https://kt.academy/article/interop-callbacks-to-coroutines) — пошаговые примеры
- [kotlinx.coroutines: suspendCancellableCoroutine](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines/suspend-cancellable-coroutine.html) — API reference
- [kotlinx.coroutines: callbackFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/callback-flow.html) — API reference

### Статьи и туториалы
- [Adam Swiderski: Adapter Pattern in Kotlin](https://asvid.github.io//kotlin-adapter-pattern) — практические примеры с Kotlin-идиомами
- [mimacom: 9 Java Patterns that Kotlin made obsolete](https://blog.mimacom.com/9-java-patterns-in-kotlin/) — как Kotlin упрощает классические паттерны
- [Refactoring Guru: Adapter](https://refactoring.guru/design-patterns/adapter) — визуальный справочник с UML

### Real-world
- [OkHttp: Interceptors](https://square.github.io/okhttp/features/interceptors/) — interceptor как adapter/decorator hybrid
- [Retrofit: CallAdapter](https://github.com/square/retrofit) — адаптация HTTP-вызовов

---

*Проверено: 2026-02-19*
