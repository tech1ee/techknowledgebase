---
title: "Kotlin Flow в Android: полный практический гайд"
created: 2026-02-14
modified: 2026-02-14
type: deep-dive
status: published
confidence: high
tags:
  - topic/android
  - type/deep-dive
  - level/intermediate
related:
  - "[[kotlin-flow]]"
  - "[[android-coroutines-guide]]"
  - "[[android-state-management]]"
  - "[[android-room-deep-dive]]"
  - "[[android-datastore-guide]]"
prerequisites:
  - "[[kotlin-flow]]"
  - "[[android-coroutines-guide]]"
reading_time: 50
difficulty: 6
study_status: not_started
mastery: 0
---

# Kotlin Flow в Android: полный практический гайд

Kotlin Flow стал стандартным способом работы с реактивными потоками данных в Android. Но между знанием API (операторы, builders, StateFlow/SharedFlow) и умением правильно использовать Flow на каждом слое Android-приложения лежит пропасть. Эта статья заполняет этот разрыв: от Room-запросов и DataStore до ViewModel и Compose UI -- полное практическое руководство по тому, как Flow пронизывает все слои архитектуры и какие паттерны Google рекомендует в 2025-2026 году.

Языковые основы Flow (builders, операторы, StateFlow, SharedFlow, backpressure) рассмотрены в [[kotlin-flow]]. Управление состоянием UI (StateFlow vs Channel, State vs Events, Compose State) -- в [[android-state-management]]. Эта статья фокусируется на практической стороне: как Flow используется в каждом слое Android-приложения, какие паттерны работают, какие ошибки типичны, и как всё это связано с lifecycle.

---

## Зачем это нужно

Android-приложение -- это набор слоёв (Data, Domain, Presentation, UI), через которые данные проходят от источника (база, сеть, сенсоры) до пикселей на экране. Каждый слой имеет свои требования к реактивности:

- **Data Layer** -- Room возвращает `Flow<List<Entity>>`, DataStore возвращает `Flow<Preferences>`, сенсоры генерируют непрерывный поток значений
- **Domain Layer** -- UseCase должен трансформировать, комбинировать и фильтровать потоки из нескольких репозиториев
- **Presentation Layer** -- ViewModel превращает холодные Flow в горячие StateFlow, которые переживают configuration change
- **UI Layer** -- Compose и Fragment должны собирать Flow lifecycle-aware, чтобы не тратить ресурсы в background

До Flow каждый слой использовал свой механизм: Room возвращал LiveData, сенсоры работали через Callback, сеть через RxJava, а UI подписывался на LiveData. Единого реактивного слоя не было. Flow унифицирует все слои одним API, который встроен в Kotlin и не требует сторонних библиотек.

### Актуальность 2025-2026

| API / Подход | Статус | Описание |
|---|---|---|
| `collectAsStateWithLifecycle()` | Стандарт | Lifecycle-aware сбор Flow в Compose |
| `repeatOnLifecycle` | Стандарт | Правильный collect в Activity/Fragment |
| `stateIn(WhileSubscribed(5_000))` | Best Practice | Конвертация cold Flow в hot StateFlow |
| `MutableStateFlow.update{}` | Рекомендован | Атомарное обновление вместо `.value =` |
| `Channel` для one-time events | Рекомендован | Замена SharedFlow(replay=0) для событий |
| `launchWhenStarted` | Устарел | Заменён на `repeatOnLifecycle` |
| `LiveData` | Legacy | Только для поддержки старого кода |
| `flowWithLifecycle` | Альтернатива | Для одиночного Flow без launch |

Google полностью перешёл на Flow как рекомендуемый реактивный подход. Все новые Jetpack-библиотеки (Room 2.6+, DataStore, Paging 3) возвращают Flow. Codelab и документация больше не содержат примеров с LiveData для новых проектов. Flow -- это не опция, а стандарт.

**Историческая перспектива.** В 2018-2019 Android-разработчики использовали LiveData повсеместно. LiveData решала проблему lifecycle-awareness, но создавала другие: невозможность трансформаций без `Transformations.map` (который работает только на Main thread), отсутствие backpressure, зависимость от Android SDK (невозможно использовать в чистом Kotlin-модуле). RxJava давала мощные трансформации, но имела сложный API с сотнями операторов и отдельную модель управления подписками (Disposable). В 2020 Google представил StateFlow и SharedFlow как замену LiveData, а к 2022 году -- `repeatOnLifecycle` и `collectAsStateWithLifecycle` как стандартные способы сбора Flow в UI. К 2025 году миграция завершена: все новые Android-проекты строятся на Flow, а LiveData остаётся только в legacy-коде.

**Ключевое преимущество Flow перед LiveData.** LiveData привязан к Android SDK -- его нельзя использовать в Kotlin Multiplatform, в чистых Kotlin-модулях (domain layer), в серверном коде. Flow -- часть kotlinx.coroutines, работает везде, где работает Kotlin. Это означает, что domain layer и data layer могут быть полностью platform-independent, а LiveData (если нужна) добавляется только на границе с UI.

**Ключевое преимущество Flow перед RxJava.** RxJava требует отдельной библиотеки (~2.5 MB), своей модели threading (Schedulers), своей модели отписки (Disposable), своей модели обработки ошибок (onError). Flow использует корутины: `suspend` для backpressure, structured concurrency для отписки, `try/catch` + `catch` оператор для ошибок. Один инструмент вместо двух параллельных миров.

---

## TL;DR

- **Data Layer**: Room возвращает `Flow<List<T>>` -- автоматический re-emit при INSERT/UPDATE/DELETE; DataStore возвращает `Flow<Preferences>`; для callback-API используй `callbackFlow` + `awaitClose`
- **Domain Layer**: UseCase возвращает `operator fun invoke(): Flow<T>`, трансформации через `map`, `combine`, `flatMapLatest`
- **Presentation Layer**: ViewModel конвертирует cold Flow в hot StateFlow через `stateIn(WhileSubscribed(5_000))`, UI-state описывается sealed-классом или data class
- **UI Layer**: Compose -- `collectAsStateWithLifecycle()`, Views -- `repeatOnLifecycle(Lifecycle.State.STARTED)`
- **Events**: `Channel<Event>` + `receiveAsFlow()` для one-time events (navigation, snackbar); НЕ SharedFlow(replay=0)
- **Типичные ошибки**: collect без lifecycle, SharedFlow для состояния, stateIn с `Eagerly`, забытый `flowOn` для тяжёлых операций

---

## Пререквизиты

| Тема | Зачем нужно | Где изучить |
|---|---|---|
| Kotlin Flow API | Builders, операторы, StateFlow, SharedFlow, backpressure | [[kotlin-flow]] |
| Kotlin Coroutines | suspend, CoroutineScope, Dispatchers, structured concurrency | [[kotlin-coroutines]] |
| Android Lifecycle | Activity/Fragment lifecycle, configuration change | [[android-activity-lifecycle]] |
| ViewModel | viewModelScope, переживание configuration change | [[android-viewmodel-internals]] |
| Compose basics | @Composable, State, recomposition | [[android-compose]] |

---

## Терминология

| Термин | Определение |
|---|---|
| **Cold Flow** | Поток, который начинает выполнение только при вызове `collect`. Каждый collector получает свой экземпляр потока |
| **Hot Flow** | Поток, который существует независимо от collectors. StateFlow и SharedFlow -- hot |
| **StateFlow** | Hot Flow с текущим значением (replay = 1). Всегда хранит последнее состояние |
| **SharedFlow** | Configurable hot Flow. Позволяет задать replay, buffer, onBufferOverflow |
| **Channel** | FIFO-очередь для передачи значений. Каждое значение доставляется ровно одному receiver |
| **stateIn** | Оператор, превращающий cold Flow в hot StateFlow. Требует scope, started и initialValue |
| **shareIn** | Оператор, превращающий cold Flow в hot SharedFlow. Требует scope и started |
| **WhileSubscribed** | Стратегия SharingStarted: upstream активен, пока есть подписчики (+ timeout) |
| **callbackFlow** | Builder для создания Flow из callback-based API (сенсоры, location, WebSocket) |
| **collectAsStateWithLifecycle** | Compose-функция для lifecycle-aware сбора Flow. Останавливает сбор в background |
| **repeatOnLifecycle** | Lifecycle-aware блок: запускает корутину при STARTED, отменяет при STOPPED |
| **flowOn** | Оператор, переключающий upstream Flow на указанный Dispatcher |

---

## Flow в каждом слое архитектуры

```
┌─────────────────────────────────────────────────────────────────────┐
│                         UI LAYER                                     │
│                                                                      │
│  Compose:  collectAsStateWithLifecycle()                            │
│  Views:    repeatOnLifecycle(STARTED) { flow.collect {} }           │
│                                                                      │
│  Получает: StateFlow<UiState>, Channel<UiEvent>                     │
├─────────────────────────────────────────────────────────────────────┤
│                    PRESENTATION LAYER                                │
│                                                                      │
│  ViewModel:                                                          │
│    repository.observe()                                              │
│      .map { toUiState(it) }                                         │
│      .stateIn(viewModelScope, WhileSubscribed(5000), initial)       │
│                                                                      │
│  Превращает: Flow<DomainModel> --> StateFlow<UiState>               │
├─────────────────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                                    │
│                                                                      │
│  UseCase:                                                            │
│    operator fun invoke(): Flow<Result<List<Item>>>                  │
│    combine(repoA.flow, repoB.flow) { a, b -> merge(a, b) }        │
│                                                                      │
│  Трансформирует: Flow<Entity> --> Flow<DomainModel>                 │
├─────────────────────────────────────────────────────────────────────┤
│                       DATA LAYER                                     │
│                                                                      │
│  Room:      @Query("SELECT * FROM items") fun observe(): Flow<..>  │
│  DataStore: preferences.data: Flow<Preferences>                     │
│  Network:   callbackFlow { webSocket.onMessage { trySend(it) } }   │
│  Sensors:   callbackFlow { sensorManager.registerListener(..) }    │
│                                                                      │
│  Источники: Flow<List<Entity>>, Flow<Preferences>, Flow<Event>     │
└─────────────────────────────────────────────────────────────────────┘
```

Поток данных всегда идёт снизу вверх: Data -> Domain -> Presentation -> UI. Каждый слой получает Flow от нижнего слоя, трансформирует его и передаёт верхнему. На границе Presentation-UI происходит ключевое преобразование: cold Flow превращается в hot StateFlow через `stateIn`, чтобы UI всегда получал последнее значение и не запускал повторные запросы при recomposition.

---

## Data Layer: Flow из источников данных

Data Layer -- первый уровень, где Flow рождаются. Каждый источник данных (Room, DataStore, Retrofit, сенсоры) предоставляет свой Flow, который репозиторий экспонирует наружу.

### Room + Flow

Room -- самый распространённый источник реактивных данных в Android. Когда DAO-метод возвращает `Flow`, Room автоматически перевыполняет запрос при любом изменении в таблице.

```kotlin
@Dao
interface TaskDao {
    // Реактивный запрос: Flow переизлучает при каждом изменении таблицы
    @Query("SELECT * FROM tasks WHERE is_completed = 0 ORDER BY created_at DESC")
    fun observeActiveTasks(): Flow<List<TaskEntity>>

    // Одноразовый запрос: suspend для операций без подписки
    @Query("SELECT * FROM tasks WHERE id = :taskId")
    suspend fun getTaskById(taskId: Long): TaskEntity?

    // Реактивный запрос с параметром
    @Query("SELECT * FROM tasks WHERE category = :category")
    fun observeByCategory(category: String): Flow<List<TaskEntity>>

    // Агрегация: Flow<Int> для счётчиков
    @Query("SELECT COUNT(*) FROM tasks WHERE is_completed = 0")
    fun observeActiveCount(): Flow<Int>

    // Одноразовые операции -- всегда suspend
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTask(task: TaskEntity)

    @Update
    suspend fun updateTask(task: TaskEntity)

    @Delete
    suspend fun deleteTask(task: TaskEntity)
}
```

**Когда использовать Flow, когда suspend в DAO:**

| Сценарий | Тип возврата | Причина |
|---|---|---|
| Список на экране (обновляется при изменениях) | `Flow<List<T>>` | UI должен реагировать на INSERT/UPDATE/DELETE |
| Счётчик badge в навигации | `Flow<Int>` | Обновляется автоматически при изменении данных |
| Загрузка одного элемента для редактирования | `suspend fun`: T? | Одноразовая операция, подписка не нужна |
| Вставка/обновление/удаление | `suspend fun` | Операция записи, не поток данных |

**Механизм автоматического re-emission.** Room использует SQLite triggers на уровне таблиц (не строк). Любое изменение в таблице `tasks` (INSERT, UPDATE, DELETE) вызывает invalidation -- Room перевыполняет запрос и Flow излучает новый `List<TaskEntity>`. Это означает важный нюанс: если вы обновили строку, которая не попадает в WHERE-условие вашего запроса, Flow всё равно перевыполнится. Результат будет тем же, но работа будет проделана.

Решение -- `distinctUntilChanged()`:

```kotlin
@Dao
interface TaskDao {
    @Query("SELECT * FROM tasks WHERE is_completed = 0")
    fun observeActiveTasks(): Flow<List<TaskEntity>>
}

// В репозитории: фильтруем дубликаты
class TaskRepository(private val dao: TaskDao) {
    fun observeActiveTasks(): Flow<List<Task>> =
        dao.observeActiveTasks()
            .distinctUntilChanged()  // Не переизлучает, если List не изменился
            .map { entities -> entities.map { it.toDomain() } }
}
```

`distinctUntilChanged()` сравнивает предыдущий и текущий результат через `equals()`. Для `List<TaskEntity>` это означает поэлементное сравнение. Если данные не изменились -- новое значение не пройдёт дальше по цепочке.

### DataStore + Flow

DataStore предоставляет `Flow<Preferences>`, который излучает новое значение при каждом изменении любого ключа.

```kotlin
class SettingsRepository(
    private val dataStore: DataStore<Preferences>
) {
    // Отдельные настройки через map
    val isDarkMode: Flow<Boolean> = dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.DARK_MODE] ?: false
        }
        .distinctUntilChanged()

    val fontSize: Flow<Int> = dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.FONT_SIZE] ?: 14
        }
        .distinctUntilChanged()

    // Комбинированная модель настроек
    val settings: Flow<UserSettings> = dataStore.data
        .map { preferences ->
            UserSettings(
                darkMode = preferences[PreferencesKeys.DARK_MODE] ?: false,
                fontSize = preferences[PreferencesKeys.FONT_SIZE] ?: 14,
                language = preferences[PreferencesKeys.LANGUAGE] ?: "en",
                notificationsEnabled = preferences[PreferencesKeys.NOTIFICATIONS] ?: true
            )
        }
        .distinctUntilChanged()

    // Запись -- suspend, не Flow
    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.DARK_MODE] = enabled
        }
    }

    private object PreferencesKeys {
        val DARK_MODE = booleanPreferencesKey("dark_mode")
        val FONT_SIZE = intPreferencesKey("font_size")
        val LANGUAGE = stringPreferencesKey("language")
        val NOTIFICATIONS = booleanPreferencesKey("notifications")
    }
}
```

**Combine нескольких DataStore.** Если приложение использует несколько DataStore (например, для разных категорий настроек), их Flow можно комбинировать:

```kotlin
class AppConfigRepository(
    private val userPrefsStore: DataStore<Preferences>,
    private val featureFlagsStore: DataStore<Preferences>
) {
    val appConfig: Flow<AppConfig> = combine(
        userPrefsStore.data.map { it[THEME_KEY] ?: "light" },
        featureFlagsStore.data.map { it[NEW_UI_KEY] ?: false }
    ) { theme, newUiEnabled ->
        AppConfig(theme = theme, newUiEnabled = newUiEnabled)
    }.distinctUntilChanged()
}
```

**Proto DataStore** работает аналогично, но вместо `Flow<Preferences>` возвращает `Flow<YourProtoMessage>` с типобезопасной схемой:

```kotlin
class UserProfileRepository(
    private val protoStore: DataStore<UserProfile>
) {
    // Уже типизированный Flow -- map не нужен для простого чтения
    val userProfile: Flow<UserProfile> = protoStore.data

    // Извлечение конкретного поля
    val userName: Flow<String> = protoStore.data
        .map { it.name }
        .distinctUntilChanged()

    suspend fun updateName(newName: String) {
        protoStore.updateData { current ->
            current.toBuilder().setName(newName).build()
        }
    }
}
```

### Retrofit + Flow

Retrofit-запросы -- одноразовые (single-shot), поэтому основной тип возврата -- `suspend fun`. Flow используется для потоковых протоколов: WebSocket, SSE (Server-Sent Events).

```kotlin
// Обычные запросы -- suspend, НЕ Flow
interface ApiService {
    @GET("tasks")
    suspend fun getTasks(): List<TaskDto>

    @POST("tasks")
    suspend fun createTask(@Body task: TaskDto): TaskDto
}

// WebSocket через callbackFlow
class WebSocketDataSource(private val okHttpClient: OkHttpClient) {

    fun observeMessages(url: String): Flow<WebSocketMessage> = callbackFlow {
        val request = Request.Builder().url(url).build()

        val webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = Json.decodeFromString<WebSocketMessage>(text)
                trySend(message)  // Неблокирующая отправка в Flow
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                close(t)  // Закрытие Flow с ошибкой
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                close()  // Нормальное закрытие Flow
            }
        })

        // ОБЯЗАТЕЛЬНО: cleanup при отмене Flow
        awaitClose {
            webSocket.close(1000, "Flow cancelled")
        }
    }
}
```

**SSE (Server-Sent Events) через Ktor:**

```kotlin
class SseDataSource(private val httpClient: HttpClient) {

    fun observeEvents(url: String): Flow<ServerEvent> = callbackFlow {
        val job = CoroutineScope(coroutineContext).launch {
            httpClient.prepareGet(url).execute { response ->
                val channel = response.bodyAsChannel()
                while (!channel.isClosedForRead) {
                    val line = channel.readUTF8Line() ?: break
                    if (line.startsWith("data:")) {
                        val event = parseEvent(line.removePrefix("data:").trim())
                        trySend(event)
                    }
                }
            }
        }

        awaitClose { job.cancel() }
    }
}
```

### Sensors / Location / Bluetooth: callbackFlow

Android SDK использует callback-паттерн для большинства системных API. `callbackFlow` -- мост между callback-миром и Flow-миром.

**Location updates:**

```kotlin
class LocationDataSource(
    private val fusedClient: FusedLocationProviderClient
) {
    @SuppressLint("MissingPermission")
    fun observeLocation(
        interval: Long = 10_000L,
        priority: Int = Priority.PRIORITY_HIGH_ACCURACY
    ): Flow<Location> = callbackFlow {

        val request = LocationRequest.Builder(priority, interval).build()

        val callback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                result.lastLocation?.let { location ->
                    trySend(location)
                }
            }
        }

        fusedClient.requestLocationUpdates(request, callback, Looper.getMainLooper())

        // awaitClose ОБЯЗАТЕЛЕН: без него -- утечка ресурсов
        awaitClose {
            fusedClient.removeLocationUpdates(callback)
        }
    }
}
```

**Sensor data:**

```kotlin
class SensorDataSource(
    private val sensorManager: SensorManager
) {
    fun observeAccelerometer(): Flow<FloatArray> = callbackFlow {
        val sensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
            ?: run { close(); return@callbackFlow }

        val listener = object : SensorEventListener {
            override fun onSensorChanged(event: SensorEvent) {
                trySend(event.values.copyOf())  // copyOf -- значения переиспользуются!
            }

            override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {}
        }

        sensorManager.registerListener(listener, sensor, SensorManager.SENSOR_DELAY_UI)

        awaitClose {
            sensorManager.unregisterListener(listener)
        }
    }
}
```

**Bluetooth GATT notifications:**

```kotlin
fun observeCharacteristic(
    gatt: BluetoothGatt,
    characteristic: BluetoothGattCharacteristic
): Flow<ByteArray> = callbackFlow {
    val callback = object : BluetoothGattCallback() {
        override fun onCharacteristicChanged(
            gatt: BluetoothGatt,
            characteristic: BluetoothGattCharacteristic,
            value: ByteArray
        ) {
            trySend(value.copyOf())
        }
    }

    gatt.setCharacteristicNotification(characteristic, true)

    awaitClose {
        gatt.setCharacteristicNotification(characteristic, false)
    }
}
```

**Паттерн callbackFlow -- три правила:**

1. **trySend** для отправки значений из callback (неблокирующий, не-suspend)
2. **close(cause)** для сигнала об ошибке или завершении
3. **awaitClose** для cleanup ресурсов -- ОБЯЗАТЕЛЕН, иначе callback продолжит работать после отмены Flow

Без `awaitClose` callbackFlow бросает `IllegalStateException`. Это защита от утечки ресурсов по дизайну.

**trySend vs send.** Внутри callbackFlow используется `trySend` (неблокирующий, возвращает `ChannelResult`), а не `send` (suspend). Причина: callback вызывается из произвольного потока (Main, Binder, Sensor), который не является suspend-контекстом. `trySend` пытается отправить значение в буфер и возвращает результат (success/failure). Если буфер переполнен, значение будет потеряно. Для большинства случаев (location, sensors) это приемлемо -- мы всегда хотим последнее значение. Если потеря недопустима, увеличьте буфер:

```kotlin
fun observeCriticalEvents(): Flow<Event> = callbackFlow {
    // Увеличенный буфер для критичных событий
    channel.invokeOnClose { /* cleanup */ }

    val callback = EventCallback { event ->
        val result = trySend(event)
        if (result.isFailure) {
            Log.w("Flow", "Event dropped: buffer overflow")
        }
    }

    registerCallback(callback)
    awaitClose { unregisterCallback(callback) }
}.buffer(Channel.BUFFERED)  // Или Channel.UNLIMITED для гарантии доставки
```

### Network connectivity

```kotlin
class ConnectivityDataSource(
    private val connectivityManager: ConnectivityManager
) {
    val isOnline: Flow<Boolean> = callbackFlow {
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                trySend(true)
            }

            override fun onLost(network: Network) {
                trySend(false)
            }
        }

        val request = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()

        connectivityManager.registerNetworkCallback(request, callback)

        // Начальное состояние
        val currentNetwork = connectivityManager.activeNetwork
        trySend(currentNetwork != null)

        awaitClose {
            connectivityManager.unregisterNetworkCallback(callback)
        }
    }.distinctUntilChanged()
}
```

---

## Domain Layer: Flow transformations

Domain Layer содержит UseCase-классы, которые инкапсулируют бизнес-логику. UseCase получает Flow от репозитория, трансформирует его и возвращает наружу.

### UseCase с Flow: конвенции

```kotlin
// Конвенция: operator fun invoke() для единообразного вызова
class ObserveActiveTasksUseCase(
    private val taskRepository: TaskRepository,
    private val settingsRepository: SettingsRepository
) {
    operator fun invoke(): Flow<List<TaskUiModel>> =
        combine(
            taskRepository.observeActiveTasks(),
            settingsRepository.settings
        ) { tasks, settings ->
            tasks
                .sortedWith(getSortComparator(settings.sortOrder))
                .map { task -> task.toUiModel(settings.dateFormat) }
        }

    private fun getSortComparator(order: SortOrder): Comparator<Task> = when (order) {
        SortOrder.BY_DATE -> compareByDescending { it.createdAt }
        SortOrder.BY_PRIORITY -> compareByDescending { it.priority }
        SortOrder.BY_NAME -> compareBy { it.name }
    }
}
```

**Почему `operator fun invoke()`?** Это позволяет вызывать UseCase как функцию: `observeActiveTasks()` вместо `observeActiveTasks.execute()`. Стандартная конвенция в Android-проектах.

### Типичные трансформации в Domain Layer

```kotlin
// combine: агрегация нескольких источников
class ObserveDashboardUseCase(
    private val taskRepo: TaskRepository,
    private val userRepo: UserRepository,
    private val statsRepo: StatsRepository
) {
    operator fun invoke(): Flow<DashboardModel> = combine(
        taskRepo.observeActiveTasks(),
        userRepo.observeCurrentUser(),
        statsRepo.observeWeeklyStats()
    ) { tasks, user, stats ->
        DashboardModel(
            userName = user.name,
            activeTasks = tasks.size,
            completedThisWeek = stats.completedCount,
            topPriorityTask = tasks.maxByOrNull { it.priority }
        )
    }
}

// distinctUntilChanged: фильтрация дубликатов по бизнес-логике
class ObserveUnreadCountUseCase(
    private val messageRepo: MessageRepository
) {
    operator fun invoke(): Flow<Int> =
        messageRepo.observeMessages()
            .map { messages -> messages.count { !it.isRead } }
            .distinctUntilChanged()  // UI обновляется только при изменении счётчика
}

// debounce + flatMapLatest: поиск с задержкой
class SearchProductsUseCase(
    private val productRepo: ProductRepository
) {
    operator fun invoke(queryFlow: Flow<String>): Flow<List<Product>> =
        queryFlow
            .debounce(300)
            .distinctUntilChanged()
            .flatMapLatest { query ->
                if (query.isBlank()) {
                    flowOf(emptyList())
                } else {
                    productRepo.search(query)
                        .catch { emit(emptyList()) }  // Fallback при ошибке
                }
            }
}

// map + filter: трансформация и фильтрация
class ObserveHighPriorityTasksUseCase(
    private val taskRepo: TaskRepository
) {
    operator fun invoke(): Flow<List<Task>> =
        taskRepo.observeActiveTasks()
            .map { tasks ->
                tasks.filter { it.priority >= Priority.HIGH }
            }
            .distinctUntilChanged()
}
```

### Обработка ошибок в Domain Layer

UseCase -- правильное место для обработки ошибок. Вместо того чтобы пробрасывать исключения до UI, UseCase оборачивает результат в `Result` или sealed-класс:

```kotlin
class ObserveOrdersUseCase(
    private val orderRepo: OrderRepository,
    private val analyticsRepo: AnalyticsRepository
) {
    operator fun invoke(): Flow<Result<List<Order>>> =
        orderRepo.observeOrders()
            .map { orders ->
                Result.success(orders.sortedByDescending { it.createdAt })
            }
            .catch { error ->
                // Логируем ошибку, но не роняем поток
                analyticsRepo.logError("ObserveOrders", error)
                emit(Result.failure(error))
            }
}

// Альтернативный подход: sealed class для более детальных ошибок
sealed interface DataResult<out T> {
    data class Success<T>(val data: T) : DataResult<T>
    data class Error(val exception: Throwable) : DataResult<Nothing>
    data object Loading : DataResult<Nothing>
}

class ObserveProductsUseCase(
    private val productRepo: ProductRepository
) {
    operator fun invoke(): Flow<DataResult<List<Product>>> = flow {
        emit(DataResult.Loading)
        emitAll(
            productRepo.observeProducts()
                .map<List<Product>, DataResult<List<Product>>> { DataResult.Success(it) }
                .catch { emit(DataResult.Error(it)) }
        )
    }
}
```

Принцип: чем выше по стеку, тем менее технические ошибки. Data Layer бросает `IOException`, Domain Layer превращает его в `DataResult.Error`, Presentation Layer показывает `"Нет подключения к интернету"`. Каждый слой понижает уровень абстракции ошибки.

### Retry и fallback в Domain Layer

Flow предоставляет операторы `retry` и `retryWhen` для автоматического восстановления после ошибок:

```kotlin
class ObserveNewsUseCase(
    private val newsRepo: NewsRepository,
    private val cacheRepo: CacheRepository
) {
    operator fun invoke(): Flow<List<NewsItem>> =
        newsRepo.observeNews()
            .retryWhen { cause, attempt ->
                // Повторяем до 3 раз для сетевых ошибок
                if (cause is IOException && attempt < 3) {
                    delay(1000L * (attempt + 1))  // Exponential backoff
                    true  // retry
                } else {
                    false  // propagate error
                }
            }
            .catch { error ->
                // Fallback: отдаём кэшированные данные при полном отказе
                val cached = cacheRepo.getCachedNews()
                if (cached.isNotEmpty()) {
                    emit(cached)
                } else {
                    throw error  // Пробрасываем, если и кэша нет
                }
            }
}
```

### flowOn в Domain Layer

Если трансформация в UseCase тяжёлая (парсинг JSON, обработка изображений, криптография), укажите Dispatcher явно:

```kotlin
class ProcessDataUseCase(
    private val repo: DataRepository
) {
    operator fun invoke(): Flow<ProcessedData> =
        repo.observeRawData()
            .map { raw -> heavyTransformation(raw) }  // CPU-intensive
            .flowOn(Dispatchers.Default)  // Только для upstream (map и выше)
}
```

`flowOn` влияет только на upstream -- операторы выше по цепочке. Collect всегда происходит в контексте вызывающей корутины.

---

## Presentation Layer: Flow в ViewModel

ViewModel -- ключевое место, где cold Flow превращается в hot StateFlow. Это необходимо, потому что:

1. UI может переподписаться в любой момент (rotation, navigation back) и должен получить последнее значение
2. Cold Flow запускает новый upstream при каждом collect -- горячий StateFlow разделяет один upstream между всеми collectors
3. ViewModel живёт дольше Activity/Fragment -- StateFlow сохраняет состояние между пересозданиями UI

### Паттерн MutableStateFlow + StateFlow

```kotlin
class TaskListViewModel(
    private val observeTasks: ObserveActiveTasksUseCase,
    private val deleteTask: DeleteTaskUseCase
) : ViewModel() {

    // Приватный MutableStateFlow -- только ViewModel может изменять
    private val _uiState = MutableStateFlow<TaskListUiState>(TaskListUiState.Loading)

    // Публичный StateFlow -- UI только читает
    val uiState: StateFlow<TaskListUiState> = _uiState.asStateFlow()

    init {
        viewModelScope.launch {
            observeTasks()
                .catch { error ->
                    _uiState.value = TaskListUiState.Error(error.message ?: "Unknown error")
                }
                .collect { tasks ->
                    _uiState.value = TaskListUiState.Success(tasks)
                }
        }
    }

    fun onDeleteTask(taskId: Long) {
        viewModelScope.launch {
            _uiState.update { current ->
                if (current is TaskListUiState.Success) {
                    current.copy(isDeleting = true)
                } else current
            }

            deleteTask(taskId)
                .onFailure { error ->
                    // Показать ошибку
                }

            _uiState.update { current ->
                if (current is TaskListUiState.Success) {
                    current.copy(isDeleting = false)
                } else current
            }
        }
    }
}

// UI State -- sealed interface для исчерпывающего when
sealed interface TaskListUiState {
    data object Loading : TaskListUiState
    data class Success(
        val tasks: List<TaskUiModel>,
        val isDeleting: Boolean = false
    ) : TaskListUiState
    data class Error(val message: String) : TaskListUiState
}
```

**Почему `update{}` вместо `.value =`?** Метод `update` атомарен -- он использует `compareAndSet` под капотом. Если два потока одновременно пытаются изменить state, `update` гарантирует, что оба изменения будут применены последовательно. С `.value =` второе присваивание может перезаписать первое.

### stateIn: cold-to-hot conversion

`stateIn` -- более декларативный подход, чем ручной collect в init:

```kotlin
class TaskListViewModel(
    observeTasks: ObserveActiveTasksUseCase
) : ViewModel() {

    val uiState: StateFlow<TaskListUiState> = observeTasks()
        .map<List<TaskUiModel>, TaskListUiState> { tasks ->
            TaskListUiState.Success(tasks)
        }
        .catch { error ->
            emit(TaskListUiState.Error(error.message ?: "Unknown error"))
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = TaskListUiState.Loading
        )
}
```

**Три стратегии SharingStarted:**

| Стратегия | Поведение | Когда использовать |
|---|---|---|
| `Eagerly` | Upstream запускается немедленно и никогда не останавливается | Данные нужны всегда (редко в Android) |
| `Lazily` | Upstream запускается при первом collector и никогда не останавливается | Один collector, данные нужны постоянно |
| `WhileSubscribed(timeout)` | Upstream останавливается через timeout после ухода последнего collector | Стандарт для Android ViewModel |

**Почему именно 5000 миллисекунд?** Число 5000 (5 секунд) -- не произвольное. При configuration change (rotation) Android уничтожает Activity и создаёт новую. Между уничтожением старого collector и появлением нового проходит от 100ms до нескольких секунд. 5 секунд -- достаточный запас, чтобы:

1. Новая Activity успела подписаться
2. Upstream не перезапускался при каждом rotation
3. При уходе в background (HOME) upstream останавливался через 5 секунд, экономя ресурсы

Если поставить 0 -- upstream перезапустится при каждом rotation. Если поставить Eagerly -- upstream никогда не остановится, даже когда приложение в background. 5000 -- оптимальный баланс.

### shareIn для общих вычислений

Когда несколько StateFlow используют один и тот же upstream, `shareIn` позволяет разделить вычисление:

```kotlin
class DashboardViewModel(
    private val observeTasks: ObserveActiveTasksUseCase,
    private val observeUser: ObserveCurrentUserUseCase
) : ViewModel() {

    // Общий upstream, разделённый между несколькими StateFlow
    private val tasks: SharedFlow<List<Task>> = observeTasks()
        .shareIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            replay = 1  // Последнее значение для новых подписчиков
        )

    val taskCount: StateFlow<Int> = tasks
        .map { it.size }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    val highPriorityTasks: StateFlow<List<Task>> = tasks
        .map { it.filter { task -> task.priority >= Priority.HIGH } }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
}
```

Без `shareIn` каждый `stateIn` запустил бы свой экземпляр `observeTasks()` -- два запроса к базе вместо одного.

### combine для композитного UiState

```kotlin
class ProfileViewModel(
    private val userRepo: UserRepository,
    private val settingsRepo: SettingsRepository,
    private val statsRepo: StatsRepository
) : ViewModel() {

    private val _isEditing = MutableStateFlow(false)

    val uiState: StateFlow<ProfileUiState> = combine(
        userRepo.observeCurrentUser(),
        settingsRepo.settings,
        statsRepo.observeUserStats(),
        _isEditing
    ) { user, settings, stats, isEditing ->
        ProfileUiState(
            name = user.name,
            email = user.email,
            avatarUrl = user.avatarUrl,
            theme = settings.theme,
            taskCount = stats.totalTasks,
            isEditing = isEditing
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = ProfileUiState.DEFAULT
    )

    fun toggleEditing() {
        _isEditing.update { !it }
    }
}
```

### Derived state: map + stateIn

**Паттерн combine + stateIn** -- основной способ создания композитного UI state в ViewModel. Каждый раз, когда любой из source Flow излучает новое значение, `combine` пересчитывает результат. Это означает, что UI state обновляется при изменении любого из источников -- пользовательских данных, настроек, статистики.

Важный нюанс: `combine` ждёт, пока каждый source Flow излучит хотя бы одно значение, прежде чем выполнить трансформацию. Если один из Flow "молчит" (например, сеть ещё не ответила), UI state не будет излучён. Решение -- предоставить initialValue через `onStart { emit(default) }`:

```kotlin
val uiState: StateFlow<UiState> = combine(
    userRepo.observeCurrentUser().onStart { emit(User.ANONYMOUS) },
    settingsRepo.settings.onStart { emit(Settings.DEFAULT) },
    statsRepo.observeStats().onStart { emit(Stats.EMPTY) }
) { user, settings, stats ->
    UiState(user = user, settings = settings, stats = stats)
}.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState.INITIAL)
```

### Derived state: map + stateIn

Если из одного StateFlow нужно вывести несколько производных значений:

```kotlin
class OrderViewModel(
    private val orderRepo: OrderRepository
) : ViewModel() {

    private val orders: StateFlow<List<Order>> = orderRepo.observeOrders()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    // Производное состояние через map + stateIn
    val pendingCount: StateFlow<Int> = orders
        .map { list -> list.count { it.status == OrderStatus.PENDING } }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0)

    val totalRevenue: StateFlow<Double> = orders
        .map { list -> list.sumOf { it.amount } }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 0.0)
}
```

---

## UI Layer: сбор Flow

UI Layer -- последний этап: Flow доходит до экрана и превращается в пиксели. Критически важно собирать Flow lifecycle-aware, чтобы не тратить ресурсы (батарея, CPU, сеть) когда приложение в background.

### Compose: collectAsStateWithLifecycle

```kotlin
// Зависимость: implementation("androidx.lifecycle:lifecycle-runtime-compose:2.9+")

@Composable
fun TaskListScreen(
    viewModel: TaskListViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when (val state = uiState) {
        is TaskListUiState.Loading -> LoadingIndicator()
        is TaskListUiState.Success -> TaskList(
            tasks = state.tasks,
            onDelete = viewModel::onDeleteTask
        )
        is TaskListUiState.Error -> ErrorMessage(state.message)
    }
}
```

**collectAsStateWithLifecycle vs collectAsState:**

| Аспект | collectAsState | collectAsStateWithLifecycle |
|---|---|---|
| Lifecycle-aware | Нет | Да |
| Останавливает collect в background | Нет | Да |
| Экономия ресурсов | Нет | Да |
| Multiplatform | Да | Только Android |
| Когда использовать | KMP/Desktop | Android-приложения |

`collectAsStateWithLifecycle()` -- обёртка над `repeatOnLifecycle`. Когда Activity уходит в STOPPED (пользователь нажал HOME), collection останавливается. Когда Activity возвращается в STARTED -- collection возобновляется. Это критично для Flow, которые запускают сетевые запросы, запросы к базе или прослушивают сенсоры.

**Параметр minActiveState:**

```kotlin
// По умолчанию: Lifecycle.State.STARTED
val state by viewModel.uiState.collectAsStateWithLifecycle()

// Для данных, которые нужны только когда экран полностью видим
val cameraData by viewModel.cameraFlow.collectAsStateWithLifecycle(
    minActiveState = Lifecycle.State.RESUMED
)
```

### Views: repeatOnLifecycle

Для Fragment и Activity с XML-layout:

```kotlin
class TaskListFragment : Fragment(R.layout.fragment_task_list) {

    private val viewModel: TaskListViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ПРАВИЛЬНО: viewLifecycleOwner.lifecycleScope + repeatOnLifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Каждый collect -- в отдельном launch внутри repeatOnLifecycle
                launch {
                    viewModel.uiState.collect { state ->
                        updateUi(state)
                    }
                }
                launch {
                    viewModel.events.collect { event ->
                        handleEvent(event)
                    }
                }
            }
        }
    }
}
```

**Почему viewLifecycleOwner, а не this (Fragment)?** Fragment живёт дольше, чем его View. При возврате из back stack Fragment не пересоздаётся, но View уничтожается и создаётся заново. `viewLifecycleOwner.lifecycleScope` привязан к lifecycle View, а не Fragment -- корутина отменится при уничтожении View, а не Fragment.

**Почему НЕ launchWhenStarted:**

```kotlin
// УСТАРЕЛО и ОПАСНО
lifecycleScope.launchWhenStarted {
    viewModel.uiState.collect { state ->
        updateUi(state)
    }
}
```

`launchWhenStarted` приостанавливает (suspend) корутину при STOPPED, но НЕ отменяет её. Это означает:
- Upstream Flow продолжает работать в background
- Database queries, network requests, sensor listeners -- всё продолжает потреблять ресурсы
- Буфер Flow наполняется данными, которые никто не обрабатывает

`repeatOnLifecycle` отменяет (cancel) корутину при STOPPED и запускает новую при STARTED. Upstream полностью останавливается.

### flowWithLifecycle: альтернатива для одиночного Flow

Если нужно собрать только один Flow:

```kotlin
viewLifecycleOwner.lifecycleScope.launch {
    viewModel.uiState
        .flowWithLifecycle(viewLifecycleOwner.lifecycle, Lifecycle.State.STARTED)
        .collect { state ->
            updateUi(state)
        }
}
```

`flowWithLifecycle` -- обёртка, которая внутри использует `repeatOnLifecycle`. Для нескольких Flow лучше использовать `repeatOnLifecycle` напрямую с отдельным `launch` для каждого.

### LaunchedEffect + Flow в Compose

Для обработки side-effects (events, navigation) в Compose:

```kotlin
@Composable
fun TaskListScreen(
    viewModel: TaskListViewModel = hiltViewModel(),
    onNavigateToDetail: (Long) -> Unit
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // LaunchedEffect для one-time events
    LaunchedEffect(Unit) {
        viewModel.navigationEvents.collect { event ->
            when (event) {
                is NavigationEvent.ToDetail -> onNavigateToDetail(event.taskId)
            }
        }
    }

    // Snackbar events
    val snackbarHostState = remember { SnackbarHostState() }
    LaunchedEffect(Unit) {
        viewModel.snackbarEvents.collect { message ->
            snackbarHostState.showSnackbar(message)
        }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) {
        // UI content
    }
}
```

Заметьте: `LaunchedEffect(Unit)` запускается один раз и живёт, пока Composable в composition. Он НЕ lifecycle-aware -- если Composable активен, collect работает. Для events это подходит, потому что Channel/SharedFlow и так не генерирует лишних значений в background.

### Сравнение подходов: полная таблица

```
┌──────────────────────────────────────────────────────────────────────┐
│               СПОСОБЫ СБОРА FLOW В ANDROID UI                        │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Compose:                                                            │
│    collectAsStateWithLifecycle()  -- для State (StateFlow)          │
│    LaunchedEffect + collect       -- для Events (Channel)           │
│                                                                      │
│  Views (Fragment/Activity):                                          │
│    repeatOnLifecycle(STARTED) {                                      │
│        launch { stateFlow.collect { } }  -- для State               │
│        launch { events.collect { } }     -- для Events              │
│    }                                                                 │
│                                                                      │
│  УСТАРЕВШИЕ:                                                        │
│    launchWhenStarted   -- suspend, НЕ cancel (утечка ресурсов)     │
│    launchWhenResumed   -- то же самое                               │
│    lifecycleScope.launch { collect } -- НЕ lifecycle-aware          │
│                                                                      │
│  MULTIPLATFORM:                                                      │
│    collectAsState()    -- НЕ lifecycle-aware, только для KMP/Desktop│
└──────────────────────────────────────────────────────────────────────┘
```

### Интеграция с Navigation Compose

При использовании Navigation Compose важно учитывать, что каждый NavBackStackEntry имеет свой lifecycle. Composable на предыдущем экране (в back stack) переходит в STOPPED, и `collectAsStateWithLifecycle` автоматически прекращает сбор:

```kotlin
@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(navController, startDestination = "list") {
        composable("list") {
            // Когда пользователь переходит на "detail",
            // этот composable уходит в STOPPED
            // collectAsStateWithLifecycle автоматически
            // прекратит сбор Flow
            val viewModel: ListViewModel = hiltViewModel()
            val state by viewModel.uiState.collectAsStateWithLifecycle()
            ListScreen(state, onItemClick = { id ->
                navController.navigate("detail/$id")
            })
        }
        composable("detail/{id}") { backStackEntry ->
            val viewModel: DetailViewModel = hiltViewModel()
            val state by viewModel.uiState.collectAsStateWithLifecycle()
            DetailScreen(state)
        }
    }
}
```

Это означает, что `stateIn(WhileSubscribed(5_000))` в ViewModel экрана "list" получит нулевых подписчиков через 5 секунд после навигации на "detail" -- upstream остановится. При возврате назад collector появится снова, upstream перезапустится и UI получит свежие данные.

---

## SharedFlow для events

Подробное сравнение State vs Events описано в [[android-state-management]]. Здесь -- практические паттерны для events в контексте Flow.

### SharedFlow vs Channel для one-time events

| Аспект | SharedFlow(replay=0) | Channel |
|---|---|---|
| Множественные collectors | Все получают одно значение | Только один получает |
| Потеря значений | Да, если нет активного collector | Нет, ждёт collector |
| Повторная доставка | Нет (replay=0) | Нет |
| Process death | Теряется | Теряется |
| Рекомендация Google | Для broadcasts | Для UI events |

**Рекомендация:** Для one-time UI events (navigation, snackbar, toast) используйте `Channel`, а не `SharedFlow(replay=0)`. Channel гарантирует, что событие будет доставлено ровно одному receiver и не потеряется, даже если collector временно отсутствует (буфер Channel сохраняет значение).

### Navigation events: паттерн с Channel

```kotlin
class TaskListViewModel(
    private val observeTasks: ObserveActiveTasksUseCase
) : ViewModel() {

    val uiState: StateFlow<TaskListUiState> = /* ... */

    // Channel для one-time events
    private val _events = Channel<TaskListEvent>(Channel.BUFFERED)
    val events: Flow<TaskListEvent> = _events.receiveAsFlow()

    fun onTaskClicked(taskId: Long) {
        viewModelScope.launch {
            _events.send(TaskListEvent.NavigateToDetail(taskId))
        }
    }

    fun onTaskDeleted(taskId: Long) {
        viewModelScope.launch {
            val result = deleteTask(taskId)
            if (result.isSuccess) {
                _events.send(TaskListEvent.ShowSnackbar("Task deleted"))
            } else {
                _events.send(TaskListEvent.ShowSnackbar("Failed to delete"))
            }
        }
    }
}

sealed interface TaskListEvent {
    data class NavigateToDetail(val taskId: Long) : TaskListEvent
    data class ShowSnackbar(val message: String) : TaskListEvent
}
```

### Event bus: анти-паттерн

```kotlin
// АНТИ-ПАТТЕРН: глобальный event bus на SharedFlow
object EventBus {
    private val _events = MutableSharedFlow<AppEvent>()
    val events: SharedFlow<AppEvent> = _events.asSharedFlow()

    suspend fun emit(event: AppEvent) {
        _events.emit(event)
    }
}
```

Проблемы глобального event bus:
- **Неявные зависимости** -- кто отправляет, кто получает, никому не понятно
- **Утечки** -- забытые collectors слушают события вечно
- **Тестируемость** -- невозможно изолировать компонент для тестирования
- **Потеря событий** -- SharedFlow(replay=0) теряет события без активного collector

**Почему event bus -- анти-паттерн в 2025.** В эпоху EventBus (GreenRobot) и Otto этот подход был популярен, потому что Android не предоставлял удобного механизма коммуникации между компонентами. Сегодня ViewModel + Channel решает ту же задачу типобезопасно, с lifecycle-awareness и без глобального состояния. Единственное исключение -- межмодульная коммуникация в модуляризированном приложении, где scoped event bus через DI может быть оправдан.

Альтернатива -- scoped events через DI:

```kotlin
// Scoped event: передаётся через DI, привязан к конкретному scope
class NavigationEventBus @Inject constructor() {
    private val _events = Channel<NavigationEvent>(Channel.BUFFERED)
    val events: Flow<NavigationEvent> = _events.receiveAsFlow()

    suspend fun send(event: NavigationEvent) {
        _events.send(event)
    }
}
```

---

## Практические паттерны

### Search с debounce + distinctUntilChanged + flatMapLatest

Полный пример от ViewModel до UI:

```kotlin
// ViewModel
class SearchViewModel(
    private val searchProducts: SearchProductsUseCase
) : ViewModel() {

    private val _query = MutableStateFlow("")

    val searchResults: StateFlow<SearchUiState> = _query
        .debounce(300)                  // Ждём 300ms паузы в наборе текста
        .distinctUntilChanged()         // Игнорируем, если текст не изменился
        .flatMapLatest { query ->       // Отменяем предыдущий поиск
            if (query.length < 2) {
                flowOf(SearchUiState.Empty)
            } else {
                flow {
                    emit(SearchUiState.Loading)
                    val results = searchProducts(query)
                    emit(SearchUiState.Success(results))
                }.catch { error ->
                    emit(SearchUiState.Error(error.message ?: "Search failed"))
                }
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5_000),
            initialValue = SearchUiState.Empty
        )

    fun onQueryChanged(query: String) {
        _query.value = query
    }
}

sealed interface SearchUiState {
    data object Empty : SearchUiState
    data object Loading : SearchUiState
    data class Success(val products: List<Product>) : SearchUiState
    data class Error(val message: String) : SearchUiState
}

// Compose UI
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val uiState by viewModel.searchResults.collectAsStateWithLifecycle()

    Column {
        var text by remember { mutableStateOf("") }

        TextField(
            value = text,
            onValueChange = { newText ->
                text = newText
                viewModel.onQueryChanged(newText)
            },
            placeholder = { Text("Search products...") }
        )

        when (val state = uiState) {
            is SearchUiState.Empty -> { /* пустой экран */ }
            is SearchUiState.Loading -> CircularProgressIndicator()
            is SearchUiState.Success -> ProductList(state.products)
            is SearchUiState.Error -> Text(state.message)
        }
    }
}
```

**Как работает цепочка:**
1. Пользователь набирает "k-o-t-l-i-n" -- каждый символ обновляет `_query`
2. `debounce(300)` пропускает только последнее значение, если 300ms не было новых
3. `distinctUntilChanged` отфильтрует, если пользователь удалил и набрал ту же букву
4. `flatMapLatest` отменяет предыдущий запрос "kotli" и запускает новый для "kotlin"
5. Результат попадает в StateFlow через `stateIn`

### Offline-first: Room Flow + API refresh

```
┌─────────────────────────────────────────────────────────┐
│                    OFFLINE-FIRST PATTERN                  │
│                                                          │
│   UI  <-- observe ---- Room (Flow) ---- Single Source   │
│                           ^             of Truth         │
│                           |                              │
│   Refresh --> Repository --+--> API --> Insert to Room   │
│                                    (triggers Flow re-emit)│
└─────────────────────────────────────────────────────────┘
```

```kotlin
class ArticleRepository(
    private val dao: ArticleDao,
    private val api: ArticleApi
) {
    // UI подписывается на Room -- единственный источник правды
    fun observeArticles(): Flow<List<Article>> =
        dao.observeAll()
            .map { entities -> entities.map { it.toDomain() } }
            .distinctUntilChanged()

    // Refresh: загрузить с API, сохранить в Room --> Flow автоматически переизлучит
    suspend fun refresh(): Result<Unit> = runCatching {
        val articles = api.getArticles()
        dao.insertAll(articles.map { it.toEntity() })
        // НЕ НУЖНО вручную обновлять Flow!
        // Room сам определит изменение и переизлучит Flow
    }
}

// ViewModel: объединяем observe + refresh
class ArticleListViewModel(
    private val repository: ArticleRepository
) : ViewModel() {

    private val _isRefreshing = MutableStateFlow(false)

    val uiState: StateFlow<ArticleListUiState> = combine(
        repository.observeArticles(),
        _isRefreshing
    ) { articles, isRefreshing ->
        ArticleListUiState(
            articles = articles,
            isRefreshing = isRefreshing,
            isEmpty = articles.isEmpty() && !isRefreshing
        )
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5_000),
        initialValue = ArticleListUiState()
    )

    fun onRefresh() {
        viewModelScope.launch {
            _isRefreshing.value = true
            repository.refresh()
            _isRefreshing.value = false
        }
    }

    init {
        onRefresh()  // Начальная загрузка при первом открытии
    }
}

data class ArticleListUiState(
    val articles: List<Article> = emptyList(),
    val isRefreshing: Boolean = false,
    val isEmpty: Boolean = true
)
```

Суть паттерна: UI никогда не получает данные напрямую от API. UI подписан на Room. API только записывает в Room. Room автоматически уведомляет UI через Flow. Это даёт:
- Мгновенное отображение кэшированных данных при открытии экрана
- Автоматическое обновление UI при получении свежих данных из API
- Работоспособность без интернета

**Почему именно Room как Single Source of Truth?** Можно было бы хранить данные в MutableStateFlow в ViewModel и обновлять его из API. Но это не переживёт process death (Android убивает процесс в background). Room сохраняет данные на диске -- при возвращении в приложение данные уже там. Кроме того, Room Flow уведомляет все активные экраны одновременно: если на одном экране данные обновились, на другом (badge, список) они обновятся автоматически без дополнительного кода.

**Обработка ошибок при refresh.** В offline-first архитектуре ошибка сети -- это не фатальная ошибка, а штатная ситуация. UI показывает кэшированные данные с индикатором "данные устарели", а не экран ошибки:

```kotlin
// В ViewModel: отдельный StateFlow для ошибок сети
private val _networkError = MutableStateFlow<String?>(null)
val networkError: StateFlow<String?> = _networkError.asStateFlow()

fun onRefresh() {
    viewModelScope.launch {
        _isRefreshing.value = true
        _networkError.value = null

        repository.refresh()
            .onFailure { error ->
                _networkError.value = when (error) {
                    is IOException -> "Нет подключения к интернету"
                    is HttpException -> "Ошибка сервера (${error.code()})"
                    else -> "Неизвестная ошибка"
                }
            }

        _isRefreshing.value = false
    }
}
```

### Pagination с Flow

Простая pagination без Paging 3:

```kotlin
class PaginatedRepository(
    private val api: ItemApi,
    private val dao: ItemDao
) {
    fun observeItems(): Flow<List<Item>> = dao.observeAll()
        .map { entities -> entities.map { it.toDomain() } }

    suspend fun loadNextPage(page: Int): Result<Boolean> = runCatching {
        val response = api.getItems(page = page, pageSize = 20)
        dao.insertAll(response.items.map { it.toEntity() })
        response.hasNextPage  // true, если есть ещё страницы
    }
}

class PaginatedListViewModel(
    private val repository: PaginatedRepository
) : ViewModel() {

    private val _paginationState = MutableStateFlow(PaginationState())

    val items: StateFlow<List<Item>> = repository.observeItems()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    val paginationState: StateFlow<PaginationState> = _paginationState.asStateFlow()

    init {
        loadPage(0)
    }

    fun onLoadMore() {
        val current = _paginationState.value
        if (!current.isLoading && current.hasMore) {
            loadPage(current.currentPage + 1)
        }
    }

    private fun loadPage(page: Int) {
        viewModelScope.launch {
            _paginationState.update { it.copy(isLoading = true) }

            repository.loadNextPage(page)
                .onSuccess { hasMore ->
                    _paginationState.update {
                        it.copy(
                            currentPage = page,
                            hasMore = hasMore,
                            isLoading = false
                        )
                    }
                }
                .onFailure {
                    _paginationState.update { it.copy(isLoading = false) }
                }
        }
    }
}

data class PaginationState(
    val currentPage: Int = 0,
    val hasMore: Boolean = true,
    val isLoading: Boolean = false
)
```

### Form validation с combine

```kotlin
class RegistrationViewModel : ViewModel() {

    val email = MutableStateFlow("")
    val password = MutableStateFlow("")
    val confirmPassword = MutableStateFlow("")

    val emailError: StateFlow<String?> = email
        .debounce(500)
        .map { value ->
            when {
                value.isBlank() -> null  // Не показывать ошибку для пустого поля
                !Patterns.EMAIL_ADDRESS.matcher(value).matches() -> "Invalid email"
                else -> null
            }
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    val passwordError: StateFlow<String?> = password
        .debounce(500)
        .map { value ->
            when {
                value.isBlank() -> null
                value.length < 8 -> "Minimum 8 characters"
                !value.any { it.isUpperCase() } -> "Need uppercase letter"
                else -> null
            }
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    val confirmError: StateFlow<String?> = combine(password, confirmPassword) { pass, confirm ->
        when {
            confirm.isBlank() -> null
            confirm != pass -> "Passwords don't match"
            else -> null
        }
    }
        .debounce(500)
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

    // Кнопка активна, только если все поля валидны и заполнены
    val isFormValid: StateFlow<Boolean> = combine(
        email, password, confirmPassword,
        emailError, passwordError, confirmError
    ) { values ->
        val (email, password, confirm) = values.take(3).map { it as String }
        val errors = values.drop(3).map { it as String? }
        email.isNotBlank() && password.isNotBlank() && confirm.isNotBlank()
            && errors.all { it == null }
    }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), false)
}
```

#### Retry с exponential backoff для API-вызовов

```kotlin
class ApiRepository(private val api: ApiService) {

    fun observeWithRetry(): Flow<List<Item>> = flow {
        while (true) {
            val items = api.getItems()
            emit(items)
            delay(30_000)  // Поллинг каждые 30 секунд
        }
    }.retryWhen { cause, attempt ->
        if (cause is IOException && attempt < 5) {
            val delayMs = minOf(
                1000L * (1L shl attempt.toInt()),  // Exponential: 1s, 2s, 4s, 8s, 16s
                30_000L  // Максимум 30 секунд
            )
            delay(delayMs)
            true
        } else {
            false
        }
    }.catch { error ->
        // После исчерпания retry -- отправить пустой список и сообщение об ошибке
        emit(emptyList())
    }
}
```

Этот паттерн полезен для polling-сценариев (когда сервер не поддерживает WebSocket или SSE). `retryWhen` получает причину ошибки и номер попытки, позволяя реализовать exponential backoff. После исчерпания попыток `catch` обрабатывает финальную ошибку.

### Countdown / Timer с Flow

```kotlin
fun countdownFlow(
    totalSeconds: Int,
    intervalMs: Long = 1_000L
): Flow<Int> = flow {
    var remaining = totalSeconds
    while (remaining >= 0) {
        emit(remaining)
        remaining--
        if (remaining >= 0) delay(intervalMs)
    }
}

// В ViewModel
class TimerViewModel : ViewModel() {

    private val _isRunning = MutableStateFlow(false)

    val timeRemaining: StateFlow<Int> = _isRunning
        .flatMapLatest { running ->
            if (running) {
                countdownFlow(totalSeconds = 60)
            } else {
                flowOf(60)
            }
        }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), 60)

    fun start() { _isRunning.value = true }
    fun stop() { _isRunning.value = false }
}
```

### Multicast: один upstream, несколько экранов

Когда несколько экранов наблюдают одни и те же данные (например, список уведомлений виден и в badge навигации, и на экране уведомлений), Repository может предоставить shared Flow:

```kotlin
class NotificationRepository(
    private val dao: NotificationDao,
    private val scope: CoroutineScope  // Application-scoped CoroutineScope
) {
    // Shared Flow на уровне Repository -- живёт дольше ViewModel
    val unreadNotifications: SharedFlow<List<Notification>> =
        dao.observeUnread()
            .map { entities -> entities.map { it.toDomain() } }
            .shareIn(
                scope = scope,              // Application scope, НЕ viewModelScope
                started = SharingStarted.WhileSubscribed(10_000),
                replay = 1
            )

    val unreadCount: StateFlow<Int> = unreadNotifications
        .map { it.size }
        .stateIn(scope, SharingStarted.WhileSubscribed(10_000), 0)
}
```

Внимание: `shareIn` и `stateIn` на уровне Repository требуют application-scoped CoroutineScope (не viewModelScope). Если использовать viewModelScope, upstream умрёт вместе с ViewModel, и другие экраны потеряют данные. Application scope обычно предоставляется через DI (Hilt `@Singleton`).

### Pull-to-refresh

```kotlin
class RefreshableViewModel(
    private val repository: DataRepository
) : ViewModel() {

    private val refreshTrigger = MutableSharedFlow<Unit>(extraBufferCapacity = 1)

    private val _isRefreshing = MutableStateFlow(false)
    val isRefreshing: StateFlow<Boolean> = _isRefreshing.asStateFlow()

    val data: StateFlow<List<Item>> = repository.observeItems()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

    init {
        viewModelScope.launch {
            refreshTrigger.collect {
                _isRefreshing.value = true
                repository.refresh()
                _isRefreshing.value = false
            }
        }
    }

    fun onRefresh() {
        refreshTrigger.tryEmit(Unit)
    }
}
```

---

## Распространённые ошибки

### 1. Collect без lifecycle

```kotlin
// ОШИБКА: collect работает даже в background
lifecycleScope.launch {
    viewModel.uiState.collect { state -> updateUi(state) }
}

// ПРАВИЛЬНО: Compose
val state by viewModel.uiState.collectAsStateWithLifecycle()

// ПРАВИЛЬНО: Views
viewLifecycleOwner.lifecycleScope.launch {
    viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state -> updateUi(state) }
    }
}
```

Без lifecycle-aware collection: Flow продолжает работать, когда приложение в background. Room-запросы, сетевые вызовы, обработка сенсоров -- всё тратит батарею впустую.

### 2. Множественный collect на cold Flow

```kotlin
// ОШИБКА: два независимых upstream запускаются
val expensiveFlow = repository.observeItems() // cold Flow
    .map { heavyTransformation(it) }

viewModelScope.launch { expensiveFlow.collect { /* collector A */ } }
viewModelScope.launch { expensiveFlow.collect { /* collector B */ } }
// heavyTransformation выполняется ДВАЖДЫ

// ПРАВИЛЬНО: shareIn для разделения upstream
val sharedFlow = repository.observeItems()
    .map { heavyTransformation(it) }
    .shareIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), replay = 1)

viewModelScope.launch { sharedFlow.collect { /* collector A */ } }
viewModelScope.launch { sharedFlow.collect { /* collector B */ } }
// heavyTransformation выполняется ОДИН РАЗ
```

### 3. Забытый flowOn для тяжёлых вычислений

```kotlin
// ОШИБКА: тяжёлый парсинг на Main thread
val data = repository.observeRawData()
    .map { parseJsonManually(it) }  // Main thread!
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)

// ПРАВИЛЬНО: flowOn переключает upstream на Default
val data = repository.observeRawData()
    .map { parseJsonManually(it) }
    .flowOn(Dispatchers.Default)  // Парсинг на Default
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), null)
```

`stateIn` и `collect` выполняются в scope (viewModelScope = Main), но `flowOn` переключает всё, что выше него, на указанный Dispatcher.

### 4. stateIn с Eagerly вместо WhileSubscribed

```kotlin
// ОШИБКА: upstream НИКОГДА не останавливается
val state = repository.observeItems()
    .stateIn(viewModelScope, SharingStarted.Eagerly, emptyList())
// Даже если UI в background -- Flow работает!

// ПРАВИЛЬНО: upstream останавливается через 5 секунд без collectors
val state = repository.observeItems()
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
```

`Eagerly` оправдан, только если данные нужны постоянно (очень редкий случай). Для 99% Android UI -- `WhileSubscribed(5_000)`.

### 5. SharedFlow для состояния

```kotlin
// ОШИБКА: SharedFlow теряет значение для новых подписчиков
private val _state = MutableSharedFlow<UiState>()  // replay = 0!
val state: SharedFlow<UiState> = _state

// Новый подписчик (после rotation) НЕ получит текущее состояние

// ПРАВИЛЬНО: StateFlow всегда хранит текущее значение
private val _state = MutableStateFlow<UiState>(UiState.Loading)
val state: StateFlow<UiState> = _state.asStateFlow()
```

StateFlow -- это SharedFlow(replay=1) с гарантией текущего значения. Для состояния UI всегда используйте StateFlow.

### 6. StateFlow equality trap

```kotlin
data class UiState(
    val items: List<String>,
    val timestamp: Long = System.currentTimeMillis()
)

val _state = MutableStateFlow(UiState(emptyList()))

// ПРОБЛЕМА: StateFlow НЕ переизлучает, если новое значение == старому
_state.value = UiState(listOf("a", "b"))  // Излучит
_state.value = UiState(listOf("a", "b"))  // НЕ излучит! equals() == true

// Обратная проблема: timestamp делает каждое значение уникальным
_state.value = UiState(listOf("a"), timestamp = 1)  // Излучит
_state.value = UiState(listOf("a"), timestamp = 2)  // Излучит (timestamp разный!)
// UI перерисуется, хотя данные не изменились
```

StateFlow использует `Any.equals()` для определения, изменилось ли значение. Если data class содержит поля, которые не влияют на UI (timestamp, requestId), StateFlow будет излучать "ложные" обновления. Если data class не содержит изменённых данных -- StateFlow пропустит обновление.

Решения:
- Исключить non-UI поля из data class (вынести в отдельный объект)
- Использовать `distinctUntilChangedBy { it.relevantField }` после StateFlow

### 7. Отсутствие обработки ошибок

```kotlin
// ОШИБКА: исключение в Flow обрушит корутину
val data = repository.observeItems()
    .map { transform(it) }  // Если бросит -- Flow и корутина умрут
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())

// ПРАВИЛЬНО: catch перехватывает ошибки в upstream
val data = repository.observeItems()
    .map { transform(it) }
    .catch { error ->
        emit(emptyList())  // Fallback value
        // Или: emit(Result.failure(error))
    }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
```

`catch` перехватывает исключения из upstream (операторы выше по цепочке). Исключения в `collect` или downstream НЕ перехватываются.

### 8. callbackFlow без awaitClose

```kotlin
// ОШИБКА: IllegalStateException + утечка ресурсов
fun observeLocation(): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            trySend(result.lastLocation)
        }
    }
    fusedClient.requestLocationUpdates(request, callback, Looper.getMainLooper())
    // Нет awaitClose! callbackFlow БРОСИТ ИСКЛЮЧЕНИЕ
}

// ПРАВИЛЬНО: awaitClose с cleanup
fun observeLocation(): Flow<Location> = callbackFlow {
    val callback = /* ... */
    fusedClient.requestLocationUpdates(request, callback, Looper.getMainLooper())

    awaitClose {
        fusedClient.removeLocationUpdates(callback)
    }
}
```

### 9. stateIn внутри функции (пересоздание при каждом вызове)

```kotlin
// ОШИБКА: stateIn вызывается при каждом обращении к свойству
class BadViewModel(repository: Repository) : ViewModel() {
    // Каждый вызов uiState создаёт НОВЫЙ StateFlow!
    fun getUiState(): StateFlow<UiState> =
        repository.observe()
            .map { UiState.Success(it) }
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState.Loading)
}

// ПРАВИЛЬНО: stateIn один раз в свойстве (val, не fun)
class GoodViewModel(repository: Repository) : ViewModel() {
    val uiState: StateFlow<UiState> =
        repository.observe()
            .map { UiState.Success(it) }
            .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), UiState.Loading)
}
```

`stateIn` создаёт новый StateFlow и запускает upstream в указанном scope. Если вызвать его внутри функции -- каждый вызов создаст новый StateFlow с новым upstream. Это и утечка памяти, и лишние запросы.

### 10. combine с большим количеством Flow

```kotlin
// ПРОБЛЕМА: combine с 5+ Flow становится нечитаемым
val uiState = combine(flow1, flow2, flow3, flow4, flow5) { a, b, c, d, e ->
    // 5 параметров, непонятно что есть что
}

// ПРАВИЛЬНО: промежуточные combine или data class
// Вариант 1: вложенные combine
val userInfo = combine(nameFlow, emailFlow) { name, email ->
    UserInfo(name, email)
}
val appSettings = combine(themeFlow, langFlow) { theme, lang ->
    AppSettings(theme, lang)
}
val uiState = combine(userInfo, appSettings, itemsFlow) { user, settings, items ->
    UiState(user = user, settings = settings, items = items)
}

// Вариант 2: combine с Array (для 6+ Flow)
val uiState = combine(
    flow1, flow2, flow3, flow4, flow5, flow6
) { values: Array<Any> ->
    // values[0], values[1], ... -- нужны cast
    // Менее типобезопасно, но работает для 6+ Flow
}
```

---

## Тестирование Flow

Тестирование Flow -- отдельная обширная тема (подробнее в [[kotlin-flow]]). Здесь -- ключевые паттерны для Android.

### Turbine: библиотека для тестирования Flow

Turbine (от Cash App) -- стандартная библиотека для тестирования Flow. Она предоставляет удобный DSL для проверки emissions.

```kotlin
// build.gradle.kts
// testImplementation("app.cash.turbine:turbine:1.1+")

class TaskListViewModelTest {

    @Test
    fun `initial state is Loading, then Success after data arrives`() = runTest {
        val fakeRepository = FakeTaskRepository()
        val viewModel = TaskListViewModel(ObserveActiveTasksUseCase(fakeRepository))

        viewModel.uiState.test {
            // Первое значение -- Loading (initialValue stateIn)
            assertEquals(TaskListUiState.Loading, awaitItem())

            // Фейковый репозиторий отправляет данные
            fakeRepository.emit(listOf(Task(1, "Test")))

            // Второе значение -- Success
            val success = awaitItem()
            assertIs<TaskListUiState.Success>(success)
            assertEquals(1, success.tasks.size)

            cancelAndConsumeRemainingEvents()
        }
    }
}
```

### Фейковый репозиторий для тестов

```kotlin
class FakeTaskRepository : TaskRepository {
    private val _tasks = MutableSharedFlow<List<Task>>()

    override fun observeActiveTasks(): Flow<List<Task>> = _tasks

    suspend fun emit(tasks: List<Task>) {
        _tasks.emit(tasks)
    }
}
```

### Тестирование stateIn с WhileSubscribed

`WhileSubscribed(5_000)` создаёт проблему в тестах: upstream останавливается через 5 секунд после последнего collector. В тестах это означает, что Flow может перестать излучать раньше, чем ожидается. Решения:

1. Использовать `backgroundScope` из `runTest` для keep-alive
2. Тестировать upstream Flow (до stateIn) отдельно от ViewModel
3. Использовать `Eagerly` в тестовой конфигурации

```kotlin
@Test
fun `stateIn test with backgroundScope`() = runTest {
    val viewModel = TaskListViewModel(/* ... */)

    // backgroundScope не завершается автоматически --
    // stateIn WhileSubscribed имеет активного подписчика
    backgroundScope.launch(UnconfinedTestDispatcher(testScheduler)) {
        viewModel.uiState.collect()
    }

    // Теперь stateIn считает, что есть подписчик
    // и upstream активен
    assertEquals(TaskListUiState.Loading, viewModel.uiState.value)
}
```

---

## CS-фундамент

| Концепция | Связь с Flow в Android |
|---|---|
| **Reactive Streams** | Flow реализует паттерн Publisher-Subscriber. Room и DataStore -- publishers, UI -- subscriber. Backpressure через suspend |
| **Observer Pattern** | StateFlow -- observable state. UI подписывается и реагирует на изменения. `collect` -- это `subscribe` |
| **Single Source of Truth** | Offline-first: Room -- единственный источник. API пишет в Room, UI читает из Room. Flow обеспечивает реактивность |
| **Cold vs Hot Streams** | Cold Flow (flow{}) -- ленивый, запускается при collect. Hot StateFlow -- всегда активен. stateIn -- мост между ними |
| **Structured Concurrency** | viewModelScope отменяет все Flow при уничтожении ViewModel. repeatOnLifecycle отменяет при STOPPED |
| **Cooperative Cancellation** | Flow проверяет cancellation на каждом emit и suspend. callbackFlow + awaitClose обеспечивает cleanup |
| **Producer-Consumer** | Channel -- FIFO-очередь между producer (ViewModel) и consumer (UI). Гарантирует exactly-once delivery |
| **Memoization** | stateIn кэширует последнее значение. distinctUntilChanged предотвращает повторные вычисления при одинаковых данных |

---

## Связь с другими темами

```
                        ┌──────────────────────┐
                        │   kotlin-flow         │
                        │   (API, операторы,    │
                        │   StateFlow/Shared)   │
                        └──────────┬───────────┘
                                   |
                    ┌──────────────┼──────────────┐
                    |              |              |
          ┌─────────v────┐  ┌─────v──────┐  ┌───v─────────────┐
          │ android-flow  │  │ android-   │  │ android-        │
          │ -guide        │  │ state-mgmt │  │ coroutines-     │
          │ (ЭТА СТАТЬЯ) │  │ (UI State) │  │ mistakes        │
          └──┬───────┬───┘  └────────────┘  └─────────────────┘
             |       |
    ┌────────v──┐  ┌─v──────────────┐
    │ android-  │  │ android-       │
    │ room-     │  │ datastore-     │
    │ deep-dive │  │ guide          │
    └───────────┘  └────────────────┘
```

| Тема | Связь |
|---|---|
| [[kotlin-flow]] | Языковые основы: builders, операторы, hot/cold, backpressure. Эта статья -- Android-специфика |
| [[android-state-management]] | UI state: StateFlow vs Channel, State vs Events, Compose State. Эта статья -- Flow через все слои |
| [[android-coroutines-guide]] | Корутины: scope, Dispatcher, structured concurrency. Flow построен на корутинах |
| [[android-room-deep-dive]] | Room: DAO, Entity, Relations. Здесь -- как Room возвращает Flow и механизм re-emission |
| [[android-datastore-guide]] | DataStore: Preferences, Proto. Здесь -- как Flow из DataStore интегрируется в архитектуру |
| [[android-viewmodel-internals]] | ViewModel: viewModelScope, SavedStateHandle. Здесь -- как stateIn использует viewModelScope |
| [[android-compose]] | Compose: recomposition, State. Здесь -- collectAsStateWithLifecycle |
| [[android-coroutines-mistakes]] | Типичные ошибки корутин. Эта статья дополняет ошибками, специфичными для Flow |

---

## Источники и дальнейшее чтение

### Книги

- **Moskala M. (2022). _Kotlin Coroutines: Deep Dive_** -- Ch. 25-29: Flow fundamentals, lifecycle, StateFlow/SharedFlow, testing Flow. Наиболее глубокое и систематическое изложение
- **Skeen S., Greenhalgh D. (2022). _Kotlin Coroutines by Tutorials_ (Kodeco)** -- практические примеры Flow в Android-приложениях

### Официальная документация

- [Kotlin flows on Android](https://developer.android.com/kotlin/flow) -- Google developer guide, основные паттерны Flow в Android
- [StateFlow and SharedFlow](https://developer.android.com/kotlin/flow/stateflow-and-sharedflow) -- официальное руководство по hot flows
- [Consuming flows safely in Jetpack Compose](https://medium.com/androiddevelopers/consuming-flows-safely-in-jetpack-compose-cde014d0d5a3) -- Manuel Vivo, collectAsStateWithLifecycle
- [repeatOnLifecycle API design story](https://manuelvivo.dev/repeatonlifecycle) -- Manuel Vivo, почему launchWhenStarted устарел и как проектировался repeatOnLifecycle
- [UI State production](https://developer.android.com/topic/architecture/ui-layer/state-production) -- Google guide по stateIn и WhileSubscribed в ViewModel
- [Room + Flow](https://medium.com/androiddevelopers/room-flow-273acffe5b57) -- Florina Muntenescu, механизм реактивных запросов Room

### Блоги и статьи

- [WhileSubscribed(5000)](https://blog.p-y.wtf/whilesubscribed5000) -- Pierre-Yves Ricau, подробный разбор магического числа 5000ms
- [Simplifying APIs with coroutines and Flow](https://manuelvivo.dev/simplifying-apis-coroutines) -- Manuel Vivo, callbackFlow и адаптация callback-API
- [Turning Any Android Callback into a Flow with callbackFlow](http://michaelevans.org/blog/2025/03/22/turning-any-android-callback-into-a-flow-with-callbackflow/) -- Michael Evans, практические примеры callbackFlow
- [callbackFlow: A lightweight architecture for location-aware Android apps](https://barbeau.medium.com/kotlin-callbackflow-a-lightweight-architecture-for-location-aware-android-apps-f97b5e66aaa2) -- Sean Barbeau, location + callbackFlow
- [SharedFlow vs Channel: When to Use Which in Android?](https://kamaldeepkakkar.medium.com/sharedflow-vs-channel-in-kotlin-coroutines-when-to-use-which-in-android-c7c3bc8da90d) -- сравнение подходов для events
- [The Complete Guide to Offline-First Architecture in Android](https://www.droidcon.com/2025/12/16/the-complete-guide-to-offline-first-architecture-in-android/) -- offline-first с Room Flow
- [Instant Search Using Kotlin Flow Operators](https://outcomeschool.com/blog/instant-search-using-kotlin-flow-operators) -- паттерн debounce + distinctUntilChanged + flatMapLatest

### Видео

- [StateFlow vs Flow vs SharedFlow vs LiveData - When to Use What](https://www.classcentral.com/course/youtube-stateflow-vs-flow-vs-sharedflow-vs-livedata-when-to-use-what-android-studio-tutorial-211356) -- Philipp Lackner, визуальное сравнение

---

## Проверь себя

1. **Почему `stateIn` использует `WhileSubscribed(5_000)`, а не `Eagerly` или `Lazily`?** Объясни связь 5-секундного таймаута с configuration change в Android. Что произойдёт, если использовать 0 вместо 5000? А если Eagerly?

2. **Room-запрос с `Flow<List<Entity>>` переизлучает при каждом изменении в таблице, даже если данные запроса не изменились. Почему это происходит и как это исправить?** Укажи конкретный оператор и объясни, как он работает.

3. **Почему `launchWhenStarted` устарел, а `repeatOnLifecycle` -- нет?** Опиши разницу в поведении при переходе Activity из STARTED в STOPPED. Что происходит с upstream Flow в каждом случае?

4. **В приложении ViewModel отправляет navigation events через `SharedFlow(replay=0)`. После rotation пользователь видит пустой экран вместо перехода на следующий экран. Почему? Какое решение?**

---

## Ключевые карточки

**Карточка 1: stateIn -- cold to hot**
- **Вопрос:** Зачем конвертировать cold Flow в StateFlow через stateIn в ViewModel?
- **Ответ:** Cold Flow запускает новый upstream при каждом collect. При recomposition Compose вызывает collect повторно -- это запустит повторный запрос к базе/сети. StateFlow через stateIn разделяет один upstream между всеми collectors и хранит последнее значение для мгновенного отображения.

**Карточка 2: collectAsStateWithLifecycle**
- **Вопрос:** Чем collectAsStateWithLifecycle отличается от collectAsState?
- **Ответ:** collectAsStateWithLifecycle останавливает сбор Flow, когда Activity в STOPPED (background). collectAsState продолжает собирать даже в background, тратя ресурсы. Для Android-приложений всегда используй collectAsStateWithLifecycle. collectAsState -- для multiplatform.

**Карточка 3: callbackFlow + awaitClose**
- **Вопрос:** Зачем awaitClose обязателен в callbackFlow?
- **Ответ:** awaitClose приостанавливает callbackFlow до момента отмены. Без него callbackFlow завершится мгновенно, но callback останется зарегистрирован -- утечка ресурсов. Внутри awaitClose вызывается cleanup: removeLocationUpdates, unregisterListener и т.д. Без awaitClose callbackFlow бросает IllegalStateException.

**Карточка 4: distinctUntilChanged для Room**
- **Вопрос:** Почему Room Flow переизлучает даже без изменения данных?
- **Ответ:** Room использует SQLite triggers на уровне таблиц. Любая операция INSERT/UPDATE/DELETE в таблице вызывает invalidation всех Flow, наблюдающих эту таблицу. distinctUntilChanged() сравнивает предыдущий и текущий результат через equals() и пропускает дубликаты.

**Карточка 5: Channel vs SharedFlow для events**
- **Вопрос:** Почему Channel лучше SharedFlow(replay=0) для one-time UI events?
- **Ответ:** SharedFlow(replay=0) теряет событие, если нет активного collector (например, при rotation). Channel буферизирует событие и доставляет его, когда collector подпишется. Channel гарантирует exactly-once delivery одному receiver -- именно то, что нужно для navigation и snackbar events.

**Карточка 6: debounce + distinctUntilChanged + flatMapLatest**
- **Вопрос:** Зачем нужны все три оператора для поиска? Что делает каждый?
- **Ответ:** debounce(300) -- ждёт 300ms паузы, предотвращает запрос на каждый символ. distinctUntilChanged -- пропускает, если текст не изменился (пользователь удалил и набрал то же). flatMapLatest -- отменяет предыдущий запрос при новом вводе, оставляет только актуальный результат. Вместе: минимум сетевых запросов, максимум отзывчивости.

---

## Куда дальше

После освоения Flow в Android рекомендуется изучить:

1. **[[android-state-management]]** -- углублённое управление состоянием: State vs Events, UDF, SavedStateHandle, Compose State hoisting
2. **[[android-coroutines-mistakes]]** -- 10 типичных ошибок с корутинами, включая ошибки с scope, cancellation и exception handling
3. **[[android-room-deep-dive]]** -- Room internals: annotation processing, миграции, TypeConverter, Relation, FTS
4. **[[kotlin-flow]]** -- языковые основы Flow: все операторы, backpressure, тестирование Flow с Turbine
5. **Testing Flow** -- `Turbine` библиотека для тестирования Flow, `runTest` для корутин, `TestScope` для контроля времени
6. **Molecule / Circuit** -- экспериментальные библиотеки (Cash App, Slack) для production state management поверх Compose runtime и Flow

---

*Последнее обновление: 2026-02-14. Актуально для Kotlin 2.1+, kotlinx.coroutines 1.9+, Compose BOM 2025.01+, lifecycle-runtime-compose 2.9+.*
