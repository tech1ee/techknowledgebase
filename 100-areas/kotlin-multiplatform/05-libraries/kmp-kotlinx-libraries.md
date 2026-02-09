---
title: "kotlinx библиотеки в KMP: сериализация, дата-время, корутины, IO"
created: 2026-01-03
modified: 2026-01-05
tags: [kotlin, kmp, kotlinx, serialization, datetime, coroutines, io, multiplatform]
related:
  - "[[00-kmp-overview]]"
  - "[[kmp-ktor-networking]]"
  - "[[kotlin-coroutines]]"
cs-foundations:
  - "[[serialization-theory]]"
  - "[[time-representation-computing]]"
  - "[[concurrency-models]]"
  - "[[io-streams-theory]]"
  - "[[type-systems-theory]]"
---

# kotlinx библиотеки в Kotlin Multiplatform

> **TL;DR:** kotlinx — официальные библиотеки от JetBrains для KMP. serialization (JSON, Protobuf, CBOR) с compile-time safety. datetime (Instant, LocalDateTime, TimeZone) — кросс-платформенная работа с датами. coroutines (Flow, StateFlow, Dispatchers) — асинхронный код. io (Buffer, Source, Sink) — низкоуровневые IO операции на базе Okio. atomicfu → мигрирует в stdlib (Kotlin 2.1+).

---

## Prerequisites

| Тема | Зачем нужно | Где изучить | CS-фундамент |
|------|-------------|-------------|--------------|
| Kotlin основы | Generics, annotations | Kotlin docs | [[type-systems-theory]] |
| KMP структура | Source sets, expect/actual | [[kmp-project-structure]] | — |
| Coroutines | suspend, Flow | [[kotlin-coroutines]] | [[concurrency-models]] |
| JSON формат | Структура данных | MDN Web Docs | [[serialization-theory]] |
| Время в компьютерах | UTC, timezones | — | [[time-representation-computing]] |

---

## Обзор kotlinx экосистемы

```
┌─────────────────────────────────────────────────────────────┐
│                   kotlinx ECOSYSTEM                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📦 kotlinx-serialization (1.9.0)                          │
│      • JSON, Protobuf, CBOR, Properties                     │
│      • Compile-time type safety                             │
│      • @Serializable annotation                             │
│                                                             │
│   🕐 kotlinx-datetime (0.7.1)                               │
│      • Instant, LocalDateTime, LocalDate                    │
│      • TimeZone support                                     │
│      • Duration arithmetic                                  │
│                                                             │
│   🔄 kotlinx-coroutines (1.10.2)                            │
│      • Flow, StateFlow, SharedFlow                          │
│      • Dispatchers (Main, IO, Default)                      │
│      • Multiplatform async                                  │
│                                                             │
│   💾 kotlinx-io (0.8.2)                                     │
│      • Buffer, Source, Sink                                 │
│      • Based on Okio                                        │
│      • File operations                                      │
│                                                             │
│   ⚛️ kotlinx-atomicfu → Kotlin stdlib (2.1+)                │
│      • AtomicInt, AtomicLong, AtomicRef                     │
│      • Migrating to kotlin.concurrent.atomics               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Почему kotlinx? Теоретические основы

### Serialization: проблема границы систем

Когда данные пересекают границу системы (сеть, файл, процесс), они должны быть преобразованы в **последовательность байтов** — это и есть сериализация. Обратный процесс — десериализация.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SERIALIZATION THEORY                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Kotlin Object          Serialization         Wire Format      │
│   ┌─────────────┐           ────→          ┌─────────────┐     │
│   │ User        │                          │ {"id":1,    │     │
│   │  id: 1      │        encode()          │  "name":    │     │
│   │  name: "Jo" │           →              │  "Jo"}      │     │
│   └─────────────┘                          └─────────────┘     │
│                         Deserialization                         │
│        ←────────────────────────                               │
│                          decode()                               │
│                                                                 │
│   Форматы:                                                      │
│   • JSON — human-readable, verbose, universal                   │
│   • Protobuf — binary, compact, schema-required                 │
│   • CBOR — binary JSON, self-describing                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Почему compile-time?** kotlinx-serialization генерирует сериализаторы во время компиляции:
- **Нет reflection** → быстрее, меньше memory
- **Ошибки при компиляции** → не в runtime
- **ProGuard-safe** → код не удаляется

### Performance: kotlinx-serialization vs alternatives

Бенчмарки 2025 показывают:

| Сценарий | kotlinx-serialization | Moshi | Gson |
|----------|----------------------|-------|------|
| Small JSON parse | **Fastest** | ~1.2x slower | ~2x slower |
| Large JSON parse | ~1.5x slower | **Fastest** | ~2x slower |
| Sealed class creation | **7x faster** | Baseline | — |
| Memory allocation | Higher | Lower | Moderate |

**Вывод:** для KMP kotlinx-serialization — единственный multiplatform вариант с отличной производительностью. Для JVM-only с огромными JSON (100MB+) можно рассмотреть Moshi.

### DateTime: почему время сложно

Время в компьютерах — одна из самых сложных проблем:

```
┌─────────────────────────────────────────────────────────────────┐
│                    TIME REPRESENTATION                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Instant (момент времени)                                      │
│   └── Количество секунд с Unix Epoch (1970-01-01T00:00:00Z)    │
│   └── Универсален, не зависит от timezone                       │
│   └── Пример: 1705312200 = 2024-01-15T10:30:00Z                │
│                                                                 │
│   LocalDateTime (дата и время без timezone)                     │
│   └── "15 января 2024, 10:30" — но КАКИЕ 10:30?                │
│   └── В Москве? В Нью-Йорке? Разница = 8 часов!                │
│   └── Используйте для UI display, НЕ для хранения              │
│                                                                 │
│   TimeZone (правила конвертации)                                │
│   └── UTC offset + DST rules + historical changes              │
│   └── Europe/Moscow: UTC+3 (без DST с 2014)                    │
│   └── America/New_York: UTC-5 зимой, UTC-4 летом               │
│                                                                 │
│   Правило: храните Instant, показывайте LocalDateTime          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Изменение в kotlinx-datetime 0.7+:** `kotlinx.datetime.Instant` стал type alias для `kotlin.time.Instant` (из stdlib). Это упрощает миграцию и интеграцию.

### Coroutines: модель конкурентности

Корутины — это **cooperative multitasking** в отличие от preemptive (threads):

| Аспект | Threads (preemptive) | Coroutines (cooperative) |
|--------|---------------------|-------------------------|
| Переключение | OS решает когда | Код решает (suspend) |
| Стоимость | ~1MB stack на thread | ~few KB на корутину |
| Количество | Сотни максимум | Миллионы возможно |
| Синхронизация | Locks, mutexes | Structured concurrency |

```kotlin
// Structured concurrency: parent-child relationship
coroutineScope {
    launch { task1() }  // Child 1
    launch { task2() }  // Child 2
}  // Ждёт завершения ВСЕХ children

// Cancellation propagates automatically:
// Отмена parent → отмена всех children
// Exception в child → отмена siblings (по умолчанию)
```

### IO: zero-copy и buffer management

kotlinx-io (основан на Okio) использует **segment pooling** для эффективности:

```
┌─────────────────────────────────────────────────────────────────┐
│                    BUFFER SEGMENTS                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Traditional I/O:                                              │
│   read() → copy to buffer1 → copy to buffer2 → process         │
│            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^                     │
│                    Много копирований                            │
│                                                                 │
│   kotlinx-io with segments:                                     │
│   ┌─────┬─────┬─────┐                                          │
│   │ Seg │ Seg │ Seg │  ← Linked list of segments                │
│   │ 8KB │ 8KB │ 8KB │                                          │
│   └─────┴─────┴─────┘                                          │
│      ↓                                                          │
│   Segments переиспользуются из pool                             │
│   Данные НЕ копируются при передаче между буферами             │
│   "Zero-copy" где возможно                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Это даёт **90%+ improvement** в Ktor 3.0+, который использует kotlinx-io внутри.

---

## kotlinx-serialization

### Настройка

```kotlin
// gradle/libs.versions.toml
[versions]
kotlin = "2.1.21"
kotlinx-serialization = "1.9.0"

[libraries]
kotlinx-serialization-json = { module = "org.jetbrains.kotlinx:kotlinx-serialization-json", version.ref = "kotlinx-serialization" }
kotlinx-serialization-protobuf = { module = "org.jetbrains.kotlinx:kotlinx-serialization-protobuf", version.ref = "kotlinx-serialization" }
kotlinx-serialization-cbor = { module = "org.jetbrains.kotlinx:kotlinx-serialization-cbor", version.ref = "kotlinx-serialization" }

[plugins]
kotlinSerialization = { id = "org.jetbrains.kotlin.plugin.serialization", version.ref = "kotlin" }
```

```kotlin
// build.gradle.kts
plugins {
    alias(libs.plugins.kotlinSerialization)
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.serialization.json)
        }
    }
}
```

### Базовое использование

```kotlin
import kotlinx.serialization.*
import kotlinx.serialization.json.*

@Serializable
data class User(
    val id: Long,
    val name: String,
    val email: String,
    @SerialName("avatar_url")  // Кастомное имя поля
    val avatarUrl: String? = null,
    @Transient  // Не сериализуется
    val localCache: String = ""
)

// Сериализация
val user = User(1, "John", "john@example.com")
val json = Json.encodeToString(user)
// {"id":1,"name":"John","email":"john@example.com"}

// Десериализация
val decoded = Json.decodeFromString<User>(json)
```

### Конфигурация Json

```kotlin
val json = Json {
    // Форматирование
    prettyPrint = true              // Красивый вывод
    prettyPrintIndent = "  "        // Отступ

    // Парсинг
    isLenient = true                // Разрешить нестрогий JSON
    ignoreUnknownKeys = true        // Игнорировать неизвестные поля
    coerceInputValues = true        // null → default value

    // Сериализация
    encodeDefaults = false          // Не включать default значения
    explicitNulls = false           // Не включать null поля

    // Имена полей
    namingStrategy = JsonNamingStrategy.SnakeCase  // camelCase → snake_case
}

// Использование
val userJson = json.encodeToString(user)
val parsedUser = json.decodeFromString<User>(userJson)
```

### Полиморфная сериализация

```kotlin
// Sealed class — лучший вариант
@Serializable
sealed class Message {
    @Serializable
    @SerialName("text")
    data class Text(val content: String) : Message()

    @Serializable
    @SerialName("image")
    data class Image(val url: String, val width: Int, val height: Int) : Message()

    @Serializable
    @SerialName("file")
    data class File(val name: String, val size: Long) : Message()
}

// Сериализация автоматически добавляет type discriminator
val message: Message = Message.Text("Hello")
val json = Json.encodeToString(message)
// {"type":"text","content":"Hello"}

// Десериализация определяет тип по discriminator
val decoded = Json.decodeFromString<Message>("""{"type":"image","url":"...","width":100,"height":100}""")
// decoded is Message.Image

// Кастомный discriminator
val json = Json {
    classDiscriminator = "#class"  // вместо "type"
}
```

### Content-based полиморфизм (без discriminator)

```kotlin
// Когда API не возвращает type field
object ApiResponseSerializer : JsonContentPolymorphicSerializer<ApiResponse>(ApiResponse::class) {
    override fun selectDeserializer(element: JsonElement): DeserializationStrategy<ApiResponse> {
        return when {
            "error" in element.jsonObject -> ApiResponse.Error.serializer()
            "data" in element.jsonObject -> ApiResponse.Success.serializer()
            else -> throw SerializationException("Unknown response type")
        }
    }
}

@Serializable(with = ApiResponseSerializer::class)
sealed class ApiResponse {
    @Serializable
    data class Success(val data: JsonElement) : ApiResponse()

    @Serializable
    data class Error(val error: String, val code: Int) : ApiResponse()
}
```

### Custom Serializers

```kotlin
// Сериализатор для java.time.Instant (JVM) → Long timestamp
object InstantAsLongSerializer : KSerializer<Instant> {
    override val descriptor = PrimitiveSerialDescriptor("Instant", PrimitiveKind.LONG)

    override fun serialize(encoder: Encoder, value: Instant) {
        encoder.encodeLong(value.toEpochMilliseconds())
    }

    override fun deserialize(decoder: Decoder): Instant {
        return Instant.fromEpochMilliseconds(decoder.decodeLong())
    }
}

@Serializable
data class Event(
    val name: String,
    @Serializable(with = InstantAsLongSerializer::class)
    val timestamp: Instant
)
```

---

## kotlinx-datetime

### Настройка

```kotlin
// libs.versions.toml
[versions]
kotlinx-datetime = "0.7.1"

[libraries]
kotlinx-datetime = { module = "org.jetbrains.kotlinx:kotlinx-datetime", version.ref = "kotlinx-datetime" }
```

### Основные типы

```kotlin
import kotlinx.datetime.*

// Instant — момент времени (UTC timestamp)
val now: Instant = Clock.System.now()
val parsed = Instant.parse("2024-01-15T10:30:00Z")

// LocalDateTime — дата и время без timezone
val localDateTime = LocalDateTime(2024, 1, 15, 10, 30, 0)
val parsedLocal = LocalDateTime.parse("2024-01-15T10:30:00")

// LocalDate — только дата
val date = LocalDate(2024, 1, 15)
val today = Clock.System.now().toLocalDateTime(TimeZone.currentSystemDefault()).date

// LocalTime — только время
val time = LocalTime(10, 30, 0)

// TimeZone
val utc = TimeZone.UTC
val moscow = TimeZone.of("Europe/Moscow")
val system = TimeZone.currentSystemDefault()
```

### Конвертации

```kotlin
// Instant → LocalDateTime
val instant = Clock.System.now()
val localDateTime = instant.toLocalDateTime(TimeZone.of("Europe/Berlin"))

// LocalDateTime → Instant
val dateTime = LocalDateTime(2024, 1, 15, 10, 30, 0)
val instantFromLocal = dateTime.toInstant(TimeZone.of("America/New_York"))

// Epoch conversions
val epochMillis = instant.toEpochMilliseconds()
val fromEpoch = Instant.fromEpochMilliseconds(epochMillis)
```

### Арифметика с датами

```kotlin
import kotlinx.datetime.*
import kotlin.time.Duration.Companion.hours
import kotlin.time.Duration.Companion.days

val now = Clock.System.now()

// С Duration (kotlin.time)
val later = now + 2.hours
val earlier = now - 7.days

// С DateTimeUnit
val tomorrow = now.plus(1, DateTimeUnit.DAY, TimeZone.UTC)
val nextMonth = now.plus(1, DateTimeUnit.MONTH, TimeZone.UTC)

// DateTimePeriod для сложных периодов
val period = DateTimePeriod(years = 1, months = 2, days = 15)
val futureDate = now.plus(period, TimeZone.UTC)

// Разница между датами
val date1 = LocalDate(2024, 1, 1)
val date2 = LocalDate(2024, 12, 31)
val daysBetween = date1.daysUntil(date2)  // 365
val monthsBetween = date1.monthsUntil(date2)  // 11
```

### Форматирование

```kotlin
// Стандартные форматы
val instant = Clock.System.now()
val isoString = instant.toString()  // 2024-01-15T10:30:00Z

// DateTimeComponents для парсинга сложных форматов
val parsed = DateTimeComponents.Formats.ISO_DATE_TIME_OFFSET
    .parse("2024-01-15T10:30:00.123+03:00")

val localDateTime = parsed.toLocalDateTime()
val offset = parsed.toUtcOffset()

// Custom formatting (требует expect/actual для полного контроля)
expect fun LocalDateTime.format(pattern: String): String

// Android actual
actual fun LocalDateTime.format(pattern: String): String {
    val formatter = java.time.format.DateTimeFormatter.ofPattern(pattern)
    return this.toJavaLocalDateTime().format(formatter)
}

// iOS actual
actual fun LocalDateTime.format(pattern: String): String {
    val formatter = NSDateFormatter().apply {
        dateFormat = pattern
    }
    // Convert LocalDateTime to NSDate...
}
```

### Best Practices

```kotlin
// ✅ Для timestamps используйте Instant
@Serializable
data class LogEntry(
    val message: String,
    @Serializable(with = InstantSerializer::class)
    val timestamp: Instant  // Момент когда произошло
)

// ✅ Для запланированных событий — LocalDateTime + TimeZone
@Serializable
data class Meeting(
    val title: String,
    val scheduledAt: LocalDateTime,  // 15:00
    val timeZone: String             // "Europe/Moscow"
)

// ✅ Для дней рождения — LocalDate
@Serializable
data class User(
    val name: String,
    val birthday: LocalDate  // Только дата, без времени
)
```

---

## kotlinx-coroutines

### Настройка

```kotlin
// libs.versions.toml
[versions]
kotlinx-coroutines = "1.10.2"

[libraries]
kotlinx-coroutines-core = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-core", version.ref = "kotlinx-coroutines" }
kotlinx-coroutines-android = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-android", version.ref = "kotlinx-coroutines" }
kotlinx-coroutines-swing = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-swing", version.ref = "kotlinx-coroutines" }  # Desktop
kotlinx-coroutines-test = { module = "org.jetbrains.kotlinx:kotlinx-coroutines-test", version.ref = "kotlinx-coroutines" }
```

```kotlin
// build.gradle.kts
kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
        }
        androidMain.dependencies {
            implementation(libs.kotlinx.coroutines.android)
        }
        jvmMain.dependencies {
            implementation(libs.kotlinx.coroutines.swing)  // Для Desktop
        }
        commonTest.dependencies {
            implementation(libs.kotlinx.coroutines.test)
        }
    }
}
```

### Dispatchers в KMP

```kotlin
// commonMain — expect
expect val Dispatchers.IO: CoroutineDispatcher

// androidMain — actual (уже есть в kotlinx-coroutines-android)
actual val Dispatchers.IO: CoroutineDispatcher
    get() = kotlinx.coroutines.Dispatchers.IO

// iosMain — actual
actual val Dispatchers.IO: CoroutineDispatcher
    get() = Dispatchers.Default  // На iOS нет отдельного IO

// Или использовать Dispatchers.Default везде для IO-bound операций
```

### Flow в KMP

```kotlin
// commonMain
class UserRepository(private val api: ApiService) {

    // Cold Flow — выполняется при collect
    fun getUsers(): Flow<List<User>> = flow {
        val users = api.fetchUsers()
        emit(users)
    }.flowOn(Dispatchers.Default)

    // Hot Flow — StateFlow
    private val _selectedUser = MutableStateFlow<User?>(null)
    val selectedUser: StateFlow<User?> = _selectedUser.asStateFlow()

    fun selectUser(user: User) {
        _selectedUser.value = user
    }

    // SharedFlow для events
    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    suspend fun emitEvent(event: UiEvent) {
        _events.emit(event)
    }
}
```

### iOS интеграция

```kotlin
// Проблема: StateFlow не работает напрямую в Swift
// Решение 1: Wrapper для iOS

class FlowWrapper<T>(private val flow: Flow<T>) {
    fun subscribe(
        scope: CoroutineScope,
        onEach: (T) -> Unit,
        onComplete: () -> Unit,
        onError: (Throwable) -> Unit
    ): Cancellable {
        val job = scope.launch(Dispatchers.Main) {
            try {
                flow.collect { onEach(it) }
                onComplete()
            } catch (e: Throwable) {
                onError(e)
            }
        }
        return object : Cancellable {
            override fun cancel() = job.cancel()
        }
    }
}

// Swift usage
let wrapper = FlowWrapper(viewModel.users)
wrapper.subscribe(
    scope: viewModel.scope,
    onEach: { users in self.users = users },
    onComplete: { },
    onError: { error in print(error) }
)

// Решение 2: SKIE (рекомендуется)
// SKIE автоматически генерирует Swift-friendly API для Flow
// См. kmp-state-management.md
```

### Тестирование

```kotlin
// commonTest
class UserRepositoryTest {

    @Test
    fun `getUsers emits list`() = runTest {
        // runTest использует TestDispatcher
        val api = FakeApiService()
        val repository = UserRepository(api)

        val result = repository.getUsers().first()

        assertEquals(2, result.size)
    }

    @Test
    fun `stateFlow updates`() = runTest {
        val repository = UserRepository(FakeApiService())

        val emissions = mutableListOf<User?>()
        val job = launch {
            repository.selectedUser.take(2).toList(emissions)
        }

        repository.selectUser(User(1, "John"))

        job.join()

        assertEquals(null, emissions[0])  // Initial
        assertEquals("John", emissions[1]?.name)
    }
}
```

---

## kotlinx-io

### Настройка

```kotlin
// libs.versions.toml
[versions]
kotlinx-io = "0.8.2"

[libraries]
kotlinx-io-core = { module = "org.jetbrains.kotlinx:kotlinx-io-core", version.ref = "kotlinx-io" }
kotlinx-io-bytestring = { module = "org.jetbrains.kotlinx:kotlinx-io-bytestring", version.ref = "kotlinx-io" }
```

### Основные типы

```kotlin
import kotlinx.io.*

// Buffer — изменяемая последовательность байтов
val buffer = Buffer()
buffer.writeString("Hello, World!")
buffer.writeInt(42)
buffer.writeLong(System.currentTimeMillis())

val text = buffer.readString()
val number = buffer.readInt()

// Source — источник данных (чтение)
// Sink — назначение данных (запись)

// Файловые операции (platform-specific)
expect fun readFile(path: String): ByteArray
expect fun writeFile(path: String, data: ByteArray)
```

### Использование с Ktor

```kotlin
// Ktor 3.x использует kotlinx-io внутри
// ByteReadChannel и ByteWriteChannel основаны на kotlinx-io

suspend fun downloadFile(url: String, sink: Sink) {
    val response = client.get(url)
    response.bodyAsChannel().readAll(sink)
}
```

---

## kotlinx-atomicfu

### Миграция в stdlib

```kotlin
// Старый подход (kotlinx-atomicfu)
import kotlinx.atomicfu.*

private val counter = atomic(0)
fun increment() = counter.incrementAndGet()

// Новый подход (Kotlin 2.1+, stdlib)
import kotlin.concurrent.atomics.*

@OptIn(ExperimentalAtomicApi::class)
private val counter = AtomicInt(0)
fun increment() = counter.incrementAndFetch()

// Доступные типы в stdlib:
// - AtomicInt
// - AtomicLong
// - AtomicBoolean
// - AtomicReference<T>
```

---

## Версии и совместимость

| Библиотека | Версия | Kotlin | Статус |
|------------|--------|--------|--------|
| kotlinx-serialization | 1.9.0 | 2.1+ | Stable |
| kotlinx-datetime | 0.7.1 | 2.0+ | Experimental |
| kotlinx-coroutines | 1.10.2 | 2.0+ | Stable |
| kotlinx-io | 0.8.2 | 2.0+ | Experimental |
| kotlinx-atomicfu | → stdlib | 2.1+ | Migrating |

---

## Best Practices

### Checklist

| Практика | Описание |
|----------|----------|
| ✅ ignoreUnknownKeys | Всегда для API responses |
| ✅ Sealed classes | Для полиморфной сериализации |
| ✅ Instant для timestamps | Не LocalDateTime |
| ✅ TimeZone explicit | Всегда указывайте timezone |
| ✅ Dispatchers.Default | Для iOS IO операций |
| ✅ SKIE для Flow | Лучшая iOS интеграция |
| ⚠️ @Experimental APIs | datetime, io ещё experimental |

---

## Мифы и заблуждения

### Миф 1: "kotlinx-serialization медленнее Gson/Moshi"

**Реальность:** Для типичных сценариев kotlinx-serialization **быстрее** благодаря compile-time code generation. Исключение — парсинг очень больших JSON (100MB+), где Moshi streaming parser выигрывает.

**Факт:** Создание сериализатора для sealed classes в 7 раз быстрее чем в Moshi.

### Миф 2: "kotlinx-datetime нестабилен для production"

**Реальность:** Несмотря на `@ExperimentalDatetimeApi`, библиотека используется в production многими компаниями. "Experimental" означает:
- API может измениться в minor версиях
- Нужен `@OptIn`

**Совет:** фиксируйте версию, следите за changelog при обновлении.

### Миф 3: "LocalDateTime безопаснее для хранения чем Instant"

**Реальность:** Категорически наоборот!

```kotlin
// ❌ Плохо: теряете информацию о timezone
val meetingTime: LocalDateTime  // 15:00... но какого часового пояса?

// ✅ Хорошо: сохраняете точный момент времени
val meetingTime: Instant  // Однозначный момент в UTC
// Конвертируйте в LocalDateTime только для отображения пользователю
```

### Миф 4: "Dispatchers.IO нужен везде для сетевых запросов"

**Реальность:** В KMP `Dispatchers.IO` существует только на JVM/Android. На iOS его нет, и это нормально:
- Ktor использует suspend functions — они не блокируют поток
- `Dispatchers.Default` подходит для большинства случаев
- Создавайте свой диспетчер только если действительно нужен thread pool

### Миф 5: "Flow и StateFlow — одно и то же"

**Реальность:** Принципиально разные концепции:

| Аспект | Flow (cold) | StateFlow (hot) |
|--------|-------------|-----------------|
| Запуск | При collect | Сразу при создании |
| Значение | Нет текущего | Всегда есть `.value` |
| Подписчики | Независимые потоки | Shared state |
| Replay | Нет | Последнее значение |

**Правило:** StateFlow для UI state, Flow для одноразовых операций (API calls).

### Миф 6: "encodeDefaults = false экономит трафик"

**Реальность:** Экономит, но может сломать совместимость! Если сервер ожидает поле — отсутствие поля может интерпретироваться как ошибка или другое значение.

**Рекомендация:** используйте `encodeDefaults = false` только если API документирован с optional fields.

### Миф 7: "kotlinx-io заменяет java.io"

**Реальность:** kotlinx-io — это **дополнение**, не замена. Оно предоставляет:
- Multiplatform API для I/O
- Эффективную работу с буферами
- Основу для Ktor 3.0

Для платформо-специфичных операций (файловая система, сокеты) всё равно нужен expect/actual.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [kotlinx.serialization](https://github.com/Kotlin/kotlinx.serialization) | GitHub | Официальная документация |
| [kotlinx-datetime](https://github.com/Kotlin/kotlinx-datetime) | GitHub | Date/time library |
| [kotlinx.coroutines](https://github.com/Kotlin/kotlinx.coroutines) | GitHub | Coroutines guide |
| [kotlinx-io](https://github.com/Kotlin/kotlinx-io) | GitHub | IO library |
| [Polymorphism Guide](https://github.com/Kotlin/kotlinx.serialization/blob/master/docs/polymorphism.md) | Official | Полиморфизм |

### CS-фундамент

| Концепция | Связь с kotlinx | Где углубить |
|-----------|-----------------|--------------|
| [[serialization-theory]] | JSON encoding/decoding, binary formats | Protocol Buffers docs |
| [[time-representation-computing]] | Instant vs LocalDateTime, timezones | "Falsehoods about time" |
| [[concurrency-models]] | Structured concurrency, Flow | Kotlin Coroutines Guide |
| [[io-streams-theory]] | Buffer, Source, Sink | Okio documentation |
| [[type-systems-theory]] | @Serializable compile-time checking | TAPL book |

---

*Проверено: 2026-01-09 | Kotlin 2.1.21*
