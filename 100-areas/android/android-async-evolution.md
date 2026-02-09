---
title: "Эволюция асинхронной работы в Android"
created: 2025-12-22
modified: 2026-01-05
type: overview
area: android
confidence: high
cs-foundations: [concurrency-models, thread-pools, cooperative-scheduling, structured-concurrency]
tags:
  - topic/android
  - topic/threading
  - type/overview
  - level/intermediate
related:
  - "[[android-handler-looper]]"
  - "[[android-asynctask-deprecated]]"
  - "[[android-executors]]"
  - "[[android-rxjava]]"
  - "[[android-coroutines-mistakes]]"
  - "[[android-threading]]"
---

# Эволюция асинхронной работы в Android

Комплексный обзор развития асинхронных подходов в Android с 2008 по 2025 год, от Handler/Thread до Kotlin Coroutines.

## Почему асинхронность критична для Android

### Application Not Responding (ANR)

Android завершит приложение с ANR dialog, если Main Thread (UI Thread) заблокирован более 5 секунд:

```kotlin
// ❌ ПЛОХО - гарантированный ANR
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Блокируем UI thread на 10 секунд
        Thread.sleep(10_000)

        setContentView(R.layout.activity_main)
    }
}
```

ANR возникает в следующих ситуациях:
- **Input event timeout**: не обработан touch/key event за 5 секунд
- **Broadcast timeout**: BroadcastReceiver не завершился за 10 секунд (foreground) или 60 секунд (background)
- **Service timeout**: Service не запустился за 20 секунд (foreground) или 200 секунд (background)
- **ContentProvider timeout**: не ответил за 10 секунд

### 16ms Frame Budget (60 FPS)

Для плавной анимации Android должен отрисовывать 60 кадров в секунду:

```
1000ms / 60 frames = 16.67ms per frame
```

Если Main Thread выполняет работу дольше 16ms:
- **Dropped frames** (jank) — пропущенные кадры
- **Stuttering animations** — рывки в анимациях
- **Delayed touch response** — задержка реакции на касания

```kotlin
// ❌ ПЛОХО - каждый кадр тормозит UI
override fun onDraw(canvas: Canvas) {
    super.onDraw(canvas)

    // Тяжёлая операция в onDraw = jank
    val bitmap = loadBitmapFromDisk() // ~50ms
    canvas.drawBitmap(bitmap, 0f, 0f, null)
}
```

### NetworkOnMainThreadException

С Android 3.0 (Honeycomb, 2011) сетевые операции на Main Thread запрещены:

```kotlin
// ❌ FATAL EXCEPTION - NetworkOnMainThreadException
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Crash на Android 3.0+
        val url = URL("https://api.example.com/data")
        val data = url.readText()
    }
}
```

Это принудительное ограничение, которое невозможно обойти без изменения `StrictMode`:

```kotlin
// ❌ Обход через StrictMode (не делайте так в продакшене!)
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .permitAll()
        .build()
)
```

## Timeline: Хронология подходов (2008-2025)

### 2008: Thread + Handler (Android 1.0)

**Контекст**: Первая версия Android, единственный способ асинхронной работы.

```java
// Android 1.0 - единственный способ background работы
public class MainActivity extends Activity {
    private final Handler handler = new Handler();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Background thread
        new Thread(() -> {
            // Тяжёлая работа
            String result = performNetworkRequest();

            // Возврат в UI thread
            handler.post(() -> {
                textView.setText(result);
            });
        }).start();
    }
}
```

**Проблемы**:
- Ручное управление потоками
- Memory leaks при уничтожении Activity
- Нет автоматической отмены задач
- Сложная обработка ошибок
- Отсутствие lifecycle awareness

### 2009: AsyncTask (API 3, Android 1.5 Cupcake)

**Контекст**: Google создал helper-класс для упрощения типичного паттерна "background work → UI update".

```java
// Android 1.5+ - официальное упрощение асинхронности
public class DownloadTask extends AsyncTask<String, Integer, String> {
    private WeakReference<TextView> textViewRef;

    public DownloadTask(TextView textView) {
        this.textViewRef = new WeakReference<>(textView);
    }

    @Override
    protected String doInBackground(String... urls) {
        // Background thread
        String result = downloadData(urls[0]);
        publishProgress(50);
        return result;
    }

    @Override
    protected void onProgressUpdate(Integer... progress) {
        // UI thread
        progressBar.setProgress(progress[0]);
    }

    @Override
    protected void onPostExecute(String result) {
        // UI thread
        TextView textView = textViewRef.get();
        if (textView != null) {
            textView.setText(result);
        }
    }
}

// Использование
new DownloadTask(textView).execute("https://example.com/data");
```

**Преимущества** (на момент 2009):
- Простой API для типичных задач
- Автоматический переход UI thread → background → UI thread
- Встроенная поддержка прогресса

**Проблемы** (проявились со временем):
- Memory leaks несмотря на WeakReference
- Configuration changes (rotation) прерывают задачи
- Serial execution по умолчанию (с API 11+)
- Невозможность композиции задач
- Хардкодная привязка к Activity/Fragment

### 2014: RxJava приходит в Android

**Контекст**: Netflix открыл исходники RxJava, Android-сообщество адаптировало reactive programming.

```kotlin
// RxJava 1.x - reactive revolution
api.getData()
    .subscribeOn(Schedulers.io())        // Background thread
    .observeOn(AndroidSchedulers.mainThread()) // UI thread
    .subscribe(
        { data -> textView.text = data },     // onNext
        { error -> showError(error) }         // onError
    )
```

**Ключевые возможности**:
- **Declarative**: описание "что делать", а не "как делать"
- **Composable**: цепочки операторов (map, flatMap, filter, etc.)
- **Error handling**: централизованная обработка ошибок
- **Backpressure**: управление потоком данных

```kotlin
// Композиция асинхронных операций
api.getUser(userId)
    .flatMap { user -> api.getPosts(user.id) }
    .flatMap { posts -> Observable.fromIterable(posts) }
    .flatMap { post -> api.getComments(post.id) }
    .toList()
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe { comments ->
        adapter.submitList(comments)
    }
```

**Проблемы**:
- Steep learning curve (кривая обучения)
- Memory leaks при неправильном отписывании
- Нет lifecycle awareness из коробки (до RxLifecycle/AutoDispose)
- Избыточность для простых задач

### 2015: Doze Mode (Android 6.0 Marshmallow)

**Контекст**: Google ввёл агрессивные ограничения фоновой работы для экономии батареи.

**Изменения**:
- **Doze Mode**: устройство игнорирует wake locks, network access, sync adapters, Wi-Fi scans
- **App Standby**: неиспользуемые приложения теряют доступ к сети
- **Maintenance windows**: короткие окна для фоновой работы

```kotlin
// ❌ Больше не работает в Doze Mode
AlarmManager.setRepeating(
    AlarmManager.RTC_WAKEUP,
    triggerAtMillis,
    intervalMillis,
    pendingIntent
)

// ✅ Нужно использовать setExactAndAllowWhileIdle или WorkManager
AlarmManager.setExactAndAllowWhileIdle(
    AlarmManager.RTC_WAKEUP,
    triggerAtMillis,
    pendingIntent
)
```

Это событие изменило правила игры: теперь простого Thread/AsyncTask недостаточно для гарантированной фоновой работы.

### 2017: Architecture Components + Executors

**Контекст**: Google I/O 2017, анонс Android Architecture Components и официальной альтернативы AsyncTask.

```kotlin
// Architecture Components - официальный подход
class UserRepository(
    private val api: ApiService,
    private val executor: Executor = Executors.newSingleThreadExecutor()
) {
    private val mainHandler = Handler(Looper.getMainLooper())

    fun getUser(callback: (User) -> Unit) {
        executor.execute {
            // Background thread
            val user = api.getUser()

            // UI thread
            mainHandler.post {
                callback(user)
            }
        }
    }
}
```

**LiveData** решил lifecycle awareness:

```kotlin
class UserViewModel : ViewModel() {
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user

    fun loadUser() {
        executor.execute {
            val user = repository.getUser()
            _user.postValue(user) // Thread-safe UI update
        }
    }
}

// Fragment
viewModel.user.observe(viewLifecycleOwner) { user ->
    // Автоматически отписывается при destroy
    textView.text = user.name
}
```

### 2019: Kotlin Coroutines становятся стандартом

**Контекст**: JetBrains и Google официально рекомендуют Coroutines для асинхронной работы в Android.

```kotlin
// Kotlin Coroutines - structured concurrency
class UserViewModel : ViewModel() {
    private val _user = MutableStateFlow<User?>(null)
    val user: StateFlow<User?> = _user.asStateFlow()

    fun loadUser() {
        viewModelScope.launch {
            // Suspend function - выглядит синхронно, работает асинхронно
            val user = repository.getUser() // Автоматически в IO dispatcher
            _user.value = user
        }
    }
}

// Repository
class UserRepository(private val api: ApiService) {
    suspend fun getUser(): User = withContext(Dispatchers.IO) {
        api.getUser()
    }
}
```

**Ключевые преимущества**:
- **Structured concurrency**: автоматическая отмена дочерних корутин
- **Sequential code**: async код выглядит как sync
- **Exception handling**: try/catch работает естественно
- **Lifecycle integration**: viewModelScope, lifecycleScope
- **Testability**: легко тестировать с TestDispatcher

```kotlin
// Композиция suspend functions
suspend fun loadUserWithPosts(userId: String): UserWithPosts {
    // Параллельное выполнение
    val user = async { api.getUser(userId) }
    val posts = async { api.getPosts(userId) }

    return UserWithPosts(
        user = user.await(),
        posts = posts.await()
    )
}
```

### 2020: AsyncTask deprecated (API 30)

**Контекст**: Google официально признал фундаментальные проблемы AsyncTask.

```java
/**
 * @deprecated Use the standard {@link java.util.concurrent} or
 * {@link Kotlin coroutines} instead.
 */
@Deprecated
public abstract class AsyncTask<Params, Progress, Result> {
    // ...
}
```

**Официальные причины deprecation**:
1. **Memory leaks**: implicit references к Activity
2. **Configuration changes**: потеря задач при rotation
3. **Serial execution**: bottleneck для параллельных задач
4. **No cancellation support**: сложно корректно отменить
5. **No error propagation**: onPostExecute вызывается даже при исключениях

### 2021-2023: Coroutines + Flow + WorkManager

**Контекст**: Устоявшийся современный стек для всех видов асинхронной работы.

```kotlin
// Flow - reactive streams для Kotlin
class PostsRepository(private val api: ApiService) {
    fun observePosts(): Flow<List<Post>> = flow {
        while (currentCoroutineContext().isActive) {
            val posts = api.getPosts()
            emit(posts)
            delay(30_000) // Обновление каждые 30 секунд
        }
    }.flowOn(Dispatchers.IO)
}

// ViewModel
class PostsViewModel : ViewModel() {
    val posts: StateFlow<List<Post>> = repository
        .observePosts()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}

// UI (Compose)
val posts by viewModel.posts.collectAsState()
LazyColumn {
    items(posts) { post ->
        PostItem(post)
    }
}
```

**WorkManager** для гарантированной фоновой работы:

```kotlin
// Работа, которая должна выполниться даже после перезагрузки
class SyncDataWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result = withContext(Dispatchers.IO) {
        try {
            repository.syncData()
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Планирование
val syncWork = PeriodicWorkRequestBuilder<SyncDataWorker>(
    repeatInterval = 1,
    repeatIntervalTimeUnit = TimeUnit.HOURS
).setConstraints(
    Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresBatteryNotLow(true)
        .build()
).build()

WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync_data",
    ExistingPeriodicWorkPolicy.KEEP,
    syncWork
)
```

### 2024-2025: Современный стандарт

**Текущее состояние**:
- **Coroutines + Flow**: стандарт для 95% асинхронных задач
- **WorkManager**: фоновая работа с гарантией выполнения
- **RxJava**: legacy support в крупных проектах
- **Executors**: Java interop и специфичные use cases

```kotlin
// Modern Android async (2024-2025)
class ModernViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    // StateFlow для UI state
    private val _uiState = MutableStateFlow<UiState>(UiState.Loading)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // Flow для reactive data streams
    val users: Flow<List<User>> = repository.observeUsers()
        .map { users -> users.sortedBy { it.name } }
        .flowOn(Dispatchers.Default)

    // Coroutines для one-shot operations
    fun loadUser(userId: String) {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            try {
                val user = repository.getUser(userId)
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message)
            }
        }
    }

    // Structured concurrency для параллельных операций
    suspend fun loadUserWithDetails(userId: String): UserDetails = coroutineScope {
        val user = async { repository.getUser(userId) }
        val posts = async { repository.getPosts(userId) }
        val followers = async { repository.getFollowers(userId) }

        UserDetails(
            user = user.await(),
            posts = posts.await(),
            followers = followers.await()
        )
    }
}
```

## Большая сравнительная таблица

| Подход | Годы | Lifecycle-aware | Cancellation | Тестируемость | Композиция | Error handling | Статус 2025 |
|--------|------|-----------------|--------------|---------------|------------|----------------|-------------|
| **Thread + Handler** | 2008+ | ❌ Нет | ❌ Ручная | ⚠️ Сложная | ❌ Нет | ❌ Ручная | 🟡 Legacy |
| **AsyncTask** | 2009-2020 | ❌ Нет | ⚠️ Частичная | ❌ Сложная | ❌ Нет | ⚠️ Слабая | 🔴 Deprecated |
| **Executors** | 2017+ | ❌ Нет | ⚠️ Future.cancel() | ✅ Хорошая | ⚠️ Callbacks | ⚠️ Ручная | 🟢 Java interop |
| **RxJava** | 2014+ | ⚠️ С библиотеками | ✅ dispose() | ✅ Отличная | ✅ Отличная | ✅ onError | 🟡 Maintenance |
| **Coroutines** | 2019+ | ✅ Scopes | ✅ Structured | ✅ Отличная | ✅ Отличная | ✅ Try/catch | 🟢 Стандарт |
| **Flow** | 2020+ | ✅ Scopes | ✅ Structured | ✅ Отличная | ✅ Отличная | ✅ Try/catch | 🟢 Стандарт |
| **WorkManager** | 2018+ | ✅ Да | ✅ cancel() | ✅ Хорошая | ⚠️ Chain | ✅ Result.retry() | 🟢 Background |

### Детализация характеристик

#### Lifecycle-aware

**Что это значит**: автоматическая отмена операций при уничтожении компонента.

```kotlin
// ❌ Thread - НЕ lifecycle-aware
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        Thread {
            Thread.sleep(10_000)
            // Crash если Activity уничтожена!
            textView.text = "Done"
        }.start()
    }
}

// ✅ Coroutines - lifecycle-aware
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            delay(10_000)
            // Автоматически отменяется при destroy
            textView.text = "Done"
        }
    }
}
```

#### Cancellation

**Важность**: избежание memory leaks и ненужной работы.

```kotlin
// RxJava - ручное управление subscriptions
class UserViewModel : ViewModel() {
    private val disposables = CompositeDisposable()

    fun loadUser() {
        api.getUser()
            .subscribeOn(Schedulers.io())
            .observeOn(AndroidSchedulers.mainThread())
            .subscribe { user ->
                // ...
            }.also { disposables.add(it) }
    }

    override fun onCleared() {
        disposables.dispose() // Ручная отмена
    }
}

// Coroutines - автоматическая отмена
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            // Автоматически отменяется при onCleared()
            val user = api.getUser()
        }
    }
}
```

#### Композиция

**Что это значит**: возможность комбинировать асинхронные операции.

```kotlin
// AsyncTask - НЕТ композиции
new DownloadUserTask().execute() // Нельзя легко скомбинировать с другой задачей

// Coroutines - естественная композиция
suspend fun loadUserDashboard(userId: String): Dashboard = coroutineScope {
    val user = async { repository.getUser(userId) }
    val posts = async { repository.getPosts(userId) }
    val notifications = async { repository.getNotifications(userId) }

    Dashboard(
        user = user.await(),
        posts = posts.await(),
        notifications = notifications.await()
    )
}
```

#### Тестируемость

```kotlin
// AsyncTask - сложное тестирование
class UserViewModelTest {
    @Test
    fun loadUser_setsUserData() {
        // Нужно ждать реального thread execution
        val latch = CountDownLatch(1)
        viewModel.loadUser { latch.countDown() }
        latch.await(5, TimeUnit.SECONDS)
        // Flaky test из-за timing
    }
}

// Coroutines - простое тестирование
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    @Test
    fun loadUser_setsUserData() = runTest {
        // Instant execution, полный контроль над временем
        viewModel.loadUser()
        advanceUntilIdle()

        assertEquals(expectedUser, viewModel.user.value)
    }
}
```

## Decision Tree: Какой подход выбрать в 2025

### 1. Простая одноразовая задача

**Используйте: Kotlin Coroutines**

```kotlin
// ✅ Загрузка данных с сервера
viewModelScope.launch {
    _uiState.value = UiState.Loading

    try {
        val data = repository.getData()
        _uiState.value = UiState.Success(data)
    } catch (e: Exception) {
        _uiState.value = UiState.Error(e)
    }
}
```

**Когда**:
- Загрузка данных при открытии экрана
- Отправка формы
- Обновление данных по нажатию кнопки
- Любые операции, привязанные к lifecycle компонента

**Почему не другие**:
- ❌ Thread + Handler: слишком verbose
- ❌ AsyncTask: deprecated
- ❌ RxJava: overkill для простой задачи
- ❌ WorkManager: для задач, которые должны пережить процесс

### 2. Фоновая работа с гарантией выполнения

**Используйте: WorkManager**

```kotlin
// ✅ Синхронизация данных раз в день
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 24,
    repeatIntervalTimeUnit = TimeUnit.HOURS
).setConstraints(
    Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresBatteryNotLow(true)
        .build()
).build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "daily_sync",
        ExistingPeriodicWorkPolicy.KEEP,
        syncWork
    )
```

**Когда**:
- Загрузка данных в фоне (upload/download)
- Периодическая синхронизация
- Работа, которая должна выполниться даже после закрытия приложения
- Задачи с retry logic
- Операции, которые должны пережить перезагрузку устройства

**Характеристики**:
- ✅ Переживает закрытие приложения
- ✅ Переживает перезагрузку устройства
- ✅ Уважает системные ограничения (Doze Mode, Battery Saver)
- ✅ Встроенный retry mechanism
- ✅ Constraints (WiFi, charging, battery level)

### 3. Legacy Java codebase

**Используйте: Executors + LiveData/Callbacks**

```kotlin
// ✅ Java-совместимый код
public class UserRepository {
    private final ExecutorService executor = Executors.newCachedThreadPool();
    private final Handler mainHandler = new Handler(Looper.getMainLooper());

    public void getUser(String userId, Callback<User> callback) {
        executor.execute(() -> {
            try {
                User user = api.getUser(userId);
                mainHandler.post(() -> callback.onSuccess(user));
            } catch (Exception e) {
                mainHandler.post(() -> callback.onError(e));
            }
        });
    }
}
```

**Когда**:
- Проект на Java без миграции на Kotlin
- Модуль, который должен работать в Java и Kotlin
- Интеграция с Java-библиотеками
- Постепенная миграция с AsyncTask

**Migration path к Coroutines**:

```kotlin
// Шаг 1: Оборачиваем Executor-based code
suspend fun getUser(userId: String): User = suspendCancellableCoroutine { continuation ->
    repository.getUser(userId, object : Callback<User> {
        override fun onSuccess(user: User) {
            continuation.resume(user)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })
}

// Шаг 2: Постепенно заменяем на suspend functions
suspend fun getUser(userId: String): User = withContext(Dispatchers.IO) {
    api.getUser(userId)
}
```

### 4. Complex event streams

**Используйте: Kotlin Flow (предпочтительно) или RxJava (legacy)**

```kotlin
// ✅ Kotlin Flow - реактивный поток данных
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = searchQuery
        .debounce(300)
        .filter { it.length >= 3 }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            repository.search(query)
                .catch { emit(emptyList()) }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

**Когда использовать Flow**:
- Поиск с debounce
- Real-time updates (WebSocket, Room database)
- Цепочки трансформаций данных
- Объединение нескольких источников данных

**Когда RxJava всё ещё оправдан**:
- Большой legacy codebase на RxJava
- Команда с глубоким опытом в RxJava
- Сложные backpressure требования
- Интеграция с RxJava-библиотеками (RxBinding, RxPermissions)

```kotlin
// RxJava - всё ещё используется в 2024-2025
searchView.textChanges()
    .debounce(300, TimeUnit.MILLISECONDS)
    .filter { it.length >= 3 }
    .distinctUntilChanged()
    .switchMap { query -> api.search(query) }
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe { results ->
        adapter.submitList(results)
    }
```

### 5. UI updates из background thread

**Используйте: Handler (редко) или postValue (LiveData/StateFlow)**

```kotlin
// ⚠️ Handler - только для специфичных случаев
class CustomView(context: Context) : View(context) {
    private val handler = Handler(Looper.getMainLooper())

    fun startAnimation() {
        Thread {
            var progress = 0
            while (progress <= 100) {
                handler.post {
                    invalidate() // UI update
                }
                Thread.sleep(16) // ~60fps
                progress++
            }
        }.start()
    }
}

// ✅ Современный подход с Flow
class CustomView(context: Context) : View(context) {
    init {
        lifecycleScope.launch {
            flow {
                for (progress in 0..100) {
                    emit(progress)
                    delay(16)
                }
            }.collect { progress ->
                // Автоматически на Main dispatcher
                invalidate()
            }
        }
    }
}
```

**Когда Handler уместен**:
- Низкоуровневая работа с Message Queue
- Custom timing механизмы
- Интеграция с legacy кодом
- Очень специфичные threading сценарии

### 6. Параллельное выполнение множественных задач

**Используйте: async/await (Coroutines)**

```kotlin
// ✅ Параллельная загрузка
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val user = async { repository.getUser() }
    val posts = async { repository.getPosts() }
    val notifications = async { repository.getNotifications() }
    val friends = async { repository.getFriends() }

    // Все запросы выполняются параллельно
    Dashboard(
        user = user.await(),
        posts = posts.await(),
        notifications = notifications.await(),
        friends = friends.await()
    )
}
```

**Сравнение с sequential**:

```kotlin
// ❌ Последовательное выполнение - медленно
suspend fun loadDashboardSlow(): Dashboard {
    val user = repository.getUser()          // 200ms
    val posts = repository.getPosts()        // 300ms
    val notifications = repository.getNotifications() // 150ms
    val friends = repository.getFriends()    // 250ms
    // Total: 900ms

    return Dashboard(user, posts, notifications, friends)
}

// ✅ Параллельное выполнение - быстро
suspend fun loadDashboardFast(): Dashboard = coroutineScope {
    // Total: max(200, 300, 150, 250) = 300ms
    val user = async { repository.getUser() }
    val posts = async { repository.getPosts() }
    val notifications = async { repository.getNotifications() }
    val friends = async { repository.getFriends() }

    Dashboard(
        user = user.await(),
        posts = posts.await(),
        notifications = notifications.await(),
        friends = friends.await()
    )
}
```

## Проверь себя

<details>
<summary><strong>1. Почему AsyncTask был deprecated в Android API 30?</strong></summary>

**Официальные причины**:

1. **Memory leaks**
   - AsyncTask часто держит implicit reference на Activity
   - WeakReference не решает проблему полностью

```java
// ❌ Memory leak
class MainActivity extends Activity {
    private class DownloadTask extends AsyncTask<Void, Void, String> {
        @Override
        protected String doInBackground(Void... voids) {
            // Implicit reference на MainActivity
            // Если Activity уничтожена, но задача работает - leak
            return downloadData();
        }

        @Override
        protected void onPostExecute(String result) {
            // Обращение к полям Activity после destroy
            textView.setText(result); // Crash или leak
        }
    }
}
```

2. **Configuration changes**
   - При rotation AsyncTask уничтожается вместе с Activity
   - Нет механизма сохранения состояния

3. **Serial execution по умолчанию**
   - С API 11+ AsyncTask выполняется последовательно
   - execute() использует SERIAL_EXECUTOR

```java
// ❌ Последовательное выполнение - медленно
new Task1().execute(); // Выполняется
new Task2().execute(); // Ждёт Task1
new Task3().execute(); // Ждёт Task1 и Task2

// ⚠️ Параллельное выполнение - нужно явно указывать
new Task1().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
new Task2().executeOnExecutor(AsyncTask.THREAD_POOL_EXECUTOR);
```

4. **Отсутствие cancellation support**
   - cancel(true) не гарантирует остановку
   - doInBackground продолжит выполняться

5. **Проблемы с error handling**
   - Исключения в doInBackground() проглатываются
   - onPostExecute() вызывается с null result

**Современная альтернатива**:

```kotlin
// ✅ Coroutines решают все проблемы AsyncTask
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            try {
                // Автоматическая отмена при destroy
                // Lifecycle-aware
                val user = repository.getUser()
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                // Естественная обработка ошибок
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```
</details>

<details>
<summary><strong>2. Когда Handler предпочтительнее Coroutines в современном Android?</strong></summary>

Handler оправдан в очень специфичных случаях:

### 1. Низкоуровневая работа с Message Queue

```kotlin
// Handler для точного контроля над Message Queue
class MessageProcessor {
    private val handler = Handler(Looper.getMainLooper())

    fun scheduleWithPriority(task: Runnable, priority: Int) {
        val message = handler.obtainMessage().apply {
            callback = task
            what = priority
        }
        handler.sendMessageAtFrontOfQueue(message) // Приоритетное выполнение
    }
}
```

### 2. Legacy Android APIs требующие Handler

```kotlin
// LocationManager callback работает через Handler
locationManager.requestLocationUpdates(
    LocationManager.GPS_PROVIDER,
    1000L,
    10f,
    locationListener,
    Looper.getMainLooper() // Требует Looper
)

// Vs modern Flow-based альтернатива
fun locationUpdates(): Flow<Location> = callbackFlow {
    val listener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            trySend(location)
        }
    }
    locationManager.requestLocationUpdates(/*...*/, listener)
    awaitClose { locationManager.removeUpdates(listener) }
}
```

### 3. Точная временная задержка с отменой

```kotlin
// Handler для отмены конкретного Runnable
class TimerView : View {
    private val handler = Handler(Looper.getMainLooper())
    private val updateRunnable = object : Runnable {
        override fun run() {
            invalidate()
            handler.postDelayed(this, 16) // Ровно 16ms
        }
    }

    fun startTimer() {
        handler.post(updateRunnable)
    }

    fun stopTimer() {
        handler.removeCallbacks(updateRunnable) // Точная отмена
    }
}

// Coroutines альтернатива - менее точный контроль
lifecycleScope.launch {
    while (isActive) {
        delay(16) // Может быть >16ms из-за scheduling
        invalidate()
    }
}
```

### 4. Интеграция с очень старым кодом

```kotlin
// Legacy Java library с Handler-based API
public class LegacyService {
    public void doWork(Handler resultHandler, int what) {
        // Результат через Handler
    }
}

// Обёртка для Coroutines
suspend fun doLegacyWork(): Result = suspendCancellableCoroutine { cont ->
    val handler = Handler(Looper.getMainLooper()) { message ->
        cont.resume(message.obj as Result)
        true
    }
    legacyService.doWork(handler, MSG_RESULT)
}
```

**Итог**: В 99% случаев используйте Coroutines. Handler только для специфичных low-level операций.
</details>

<details>
<summary><strong>3. Чем WorkManager отличается от Coroutines и когда его использовать?</strong></summary>

### Ключевые отличия

| Характеристика | Coroutines | WorkManager |
|----------------|------------|-------------|
| **Lifecycle** | Привязаны к scope (Activity, ViewModel) | Переживают закрытие приложения |
| **Гарантия выполнения** | Только пока жив scope | Гарантированное выполнение |
| **Перезагрузка устройства** | Отменяются | Восстанавливаются |
| **Constraints** | Нет | WiFi, charging, battery, storage |
| **Retry logic** | Ручная реализация | Встроенный механизм |
| **Doze Mode** | Не работают | Уважают, но выполнятся позже |

### Coroutines - для foreground операций

```kotlin
// ✅ Загрузка данных при открытии экрана
class UserViewModel : ViewModel() {
    fun loadUser() {
        viewModelScope.launch {
            // Отменяется при закрытии экрана
            val user = repository.getUser()
            _uiState.value = UiState.Success(user)
        }
    }
}
```

**Используйте для**:
- UI-driven операции
- Загрузка данных для текущего экрана
- Операции, которые должны отменяться при уходе с экрана
- Real-time updates во время использования приложения

### WorkManager - для background операций

```kotlin
// ✅ Загрузка файла, который должен докачаться
class DownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            val fileUrl = inputData.getString("file_url") ?: return Result.failure()

            // Загрузка продолжится даже если:
            // - Пользователь закрыл приложение
            // - Устройство перезагрузилось
            // - Приложение было убито системой
            downloadFile(fileUrl)

            Result.success()
        } catch (e: Exception) {
            // Автоматический retry
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
}

// Планирование с constraints
val downloadWork = OneTimeWorkRequestBuilder<DownloadWorker>()
    .setInputData(workDataOf("file_url" to url))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // Только WiFi
            .setRequiresBatteryNotLow(true)
            .setRequiresStorageNotLow(true)
            .build()
    )
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .build()

WorkManager.getInstance(context).enqueue(downloadWork)
```

**Используйте для**:
- Upload/download файлов
- Периодическая синхронизация данных
- Отправка аналитики
- Очистка кэша
- Backup данных
- Любая работа, которая должна выполниться независимо от состояния приложения

### Комбинация обоих подходов

```kotlin
// UI layer - Coroutines
class UploadViewModel : ViewModel() {
    fun uploadFile(file: File) {
        // Сразу показываем UI feedback
        viewModelScope.launch {
            _uiState.value = UiState.Uploading

            // Планируем WorkManager для надёжной загрузки
            val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
                .setInputData(workDataOf("file_path" to file.path))
                .build()

            WorkManager.getInstance(context).enqueue(uploadWork)

            // Наблюдаем за прогрессом
            WorkManager.getInstance(context)
                .getWorkInfoByIdFlow(uploadWork.id)
                .collect { workInfo ->
                    when (workInfo.state) {
                        WorkInfo.State.SUCCEEDED -> _uiState.value = UiState.Success
                        WorkInfo.State.FAILED -> _uiState.value = UiState.Error
                        else -> {}
                    }
                }
        }
    }
}
```
</details>

<details>
<summary><strong>4. Почему RxJava всё ещё используется в 2024-2025, несмотря на Kotlin Flow?</strong></summary>

### Причины продолжения использования RxJava

#### 1. Огромная legacy кодовая база

```kotlin
// Проекты с миллионами строк RxJava кода
class LegacyRepository {
    // Тысячи методов возвращают Observable/Single/Completable
    fun getUser(id: String): Single<User>
    fun observeUpdates(): Observable<Update>
    fun performAction(): Completable
}

// Полная миграция на Flow - огромные риски
// Частичная миграция - bridge между RxJava и Flow
fun observeUpdates(): Flow<Update> = repository
    .observeUpdates()
    .asFlow() // Конвертация RxJava → Flow
```

#### 2. Зрелая экосистема библиотек

```kotlin
// RxBinding - reactive view events
searchView.textChanges()
    .debounce(300, TimeUnit.MILLISECONDS)
    .subscribe { query -> search(query) }

// RxPermissions - reactive permissions
rxPermissions
    .request(Manifest.permission.CAMERA)
    .subscribe { granted ->
        if (granted) openCamera()
    }

// RxRelay - subjects без error/complete
val clickRelay = PublishRelay.create<Unit>()
clickRelay.accept(Unit)
```

**Flow альтернативы** появляются медленно:
- FlowBinding - ещё не покрывает все случаи
- Permissions - требуют custom реализации
- Нет прямого аналога Relay

#### 3. Backpressure для сложных сценариев

```kotlin
// RxJava - встроенный backpressure
Observable.interval(1, TimeUnit.MILLISECONDS) // Быстрый producer
    .onBackpressureBuffer(100) // Буфер
    .observeOn(Schedulers.io(), false, 10) // Медленный consumer
    .subscribe { processItem(it) }

// Flow - backpressure через buffer/conflate
flow {
    while (true) {
        emit(getItem())
        delay(1)
    }
}
    .buffer(100) // Аналог onBackpressureBuffer
    .collect { processItem(it) }
```

RxJava предоставляет больше стратегий backpressure из коробки:
- onBackpressureBuffer
- onBackpressureDrop
- onBackpressureLatest
- Custom strategies

#### 4. Команды с глубоким опытом RxJava

```kotlin
// Сложная композиция - RxJava более familiar для опытных команд
api.getUser()
    .flatMap { user ->
        Observable.zip(
            api.getPosts(user.id),
            api.getComments(user.id),
            api.getFollowers(user.id)
        ) { posts, comments, followers ->
            UserDashboard(user, posts, comments, followers)
        }
    }
    .retry(3)
    .timeout(30, TimeUnit.SECONDS)
    .subscribeOn(Schedulers.io())
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe(
        { dashboard -> showDashboard(dashboard) },
        { error -> showError(error) }
    )

// Flow эквивалент - менее знаком команде
flow {
    val user = api.getUser()

    coroutineScope {
        val posts = async { api.getPosts(user.id) }
        val comments = async { api.getComments(user.id) }
        val followers = async { api.getFollowers(user.id) }

        emit(UserDashboard(user, posts.await(), comments.await(), followers.await()))
    }
}
    .retry(3)
    .timeout(30.seconds)
    .flowOn(Dispatchers.IO)
    .catch { error -> showError(error) }
    .collect { dashboard -> showDashboard(dashboard) }
```

#### 5. Операторы, которых нет в Flow (пока)

```kotlin
// publish/replay - hot observables
val sharedObservable = coldObservable
    .replay(1)
    .refCount()

// window/groupBy - complex grouping
observable
    .window(5, TimeUnit.SECONDS)
    .flatMap { window -> window.toList() }

// Flow альтернативы появляются постепенно
val sharedFlow = flow.shareIn(
    scope = viewModelScope,
    started = SharingStarted.WhileSubscribed(),
    replay = 1
)
```

### Когда выбирать RxJava в 2024-2025

✅ **Используйте RxJava**:
- Существующий проект на RxJava с большой кодовой базой
- Команда с экспертизой в RxJava
- Необходимы специфичные RxJava библиотеки (RxBinding, RxPermissions)
- Сложные backpressure сценарии
- Интеграция с Java-кодом, где suspend functions неудобны

✅ **Используйте Flow**:
- Новый проект
- Kotlin-first подход
- Интеграция с Jetpack (Room, DataStore, WorkManager)
- Простая структура проекта
- Команда знакома с Coroutines

### Migration strategy: RxJava → Flow

```kotlin
// Постепенная миграция через interop
class UserRepository {
    // Legacy RxJava API
    private val rxApi: RxApiService

    // Modern Flow API
    suspend fun getUser(id: String): User = rxApi
        .getUser(id)
        .await() // RxJava Single → suspend

    fun observeUpdates(): Flow<Update> = rxApi
        .observeUpdates()
        .asFlow() // RxJava Observable → Flow
}
```
</details>

<details>
<summary><strong>5. Что такое structured concurrency и зачем она нужна в Android?</strong></summary>

### Определение

**Structured Concurrency** - принцип организации асинхронного кода, где:
1. Корутины организованы в иерархию (parent-child)
2. Parent корутина отвечает за lifecycle всех children
3. Отмена parent автоматически отменяет всех children
4. Parent завершается только после завершения всех children

### Проблема: неструктурированная конкурентность

```kotlin
// ❌ Thread - неструктурированная конкурентность
class UserViewModel : ViewModel() {
    private var threads = mutableListOf<Thread>()

    fun loadUserData() {
        // Запускаем 3 независимых потока
        val thread1 = Thread { loadUser() }
        val thread2 = Thread { loadPosts() }
        val thread3 = Thread { loadComments() }

        threads.add(thread1)
        threads.add(thread2)
        threads.add(thread3)

        thread1.start()
        thread2.start()
        thread3.start()
    }

    override fun onCleared() {
        // ⚠️ Ручная отмена каждого потока
        threads.forEach { it.interrupt() }
        threads.clear()
    }
}
```

**Проблемы**:
- Нужно вручную отслеживать все потоки
- Легко забыть отменить поток
- Сложно обрабатывать ошибки
- Нет гарантии завершения всех операций

### Решение: structured concurrency в Coroutines

```kotlin
// ✅ Coroutines - structured concurrency
class UserViewModel : ViewModel() {
    fun loadUserData() {
        viewModelScope.launch { // Parent coroutine
            // Все children автоматически отменятся при отмене parent
            val user = async { loadUser() }      // Child 1
            val posts = async { loadPosts() }    // Child 2
            val comments = async { loadComments() } // Child 3

            // Parent ждёт завершения всех children
            updateUI(user.await(), posts.await(), comments.await())
        }
        // При onCleared() viewModelScope автоматически отменит
        // parent и все children корутины
    }
}
```

### Ключевые преимущества

#### 1. Автоматическая отмена при lifecycle events

```kotlin
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            // Parent coroutine
            launch { observeUser() }      // Child 1
            launch { observePosts() }     // Child 2
            launch { observeComments() }  // Child 3
        }

        // При onDestroyView() все корутины автоматически отменяются
        // Нет memory leaks, нет crash из-за обращения к уничтоженным View
    }
}
```

#### 2. Гарантия выполнения всех операций

```kotlin
// ✅ coroutineScope ждёт завершения всех children
suspend fun loadDashboard(): Dashboard = coroutineScope {
    val user = async { api.getUser() }
    val posts = async { api.getPosts() }

    // Функция не вернётся, пока не завершатся оба запроса
    Dashboard(user.await(), posts.await())
}

// ❌ БЕЗ coroutineScope - race condition
suspend fun loadDashboardBad(): Dashboard {
    var user: User? = null
    var posts: List<Post>? = null

    launch { user = api.getUser() }   // Может не завершиться
    launch { posts = api.getPosts() } // Может не завершиться

    // Может вернуть Dashboard с null значениями!
    return Dashboard(user!!, posts!!)
}
```

#### 3. Централизованная обработка ошибок

```kotlin
// ✅ Исключение в child отменяет parent и всех siblings
suspend fun processData() = coroutineScope {
    launch {
        delay(1000)
        println("Task 1 completed")
    }

    launch {
        delay(500)
        throw Exception("Task 2 failed") // Отменяет Task 1 и parent
    }

    launch {
        delay(1500)
        println("Task 3 completed") // Не выполнится
    }
}

try {
    processData()
} catch (e: Exception) {
    // Централизованная обработка
    println("Error: ${e.message}")
}
```

#### 4. Предотвращение memory leaks

```kotlin
// ❌ GlobalScope - memory leak
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        GlobalScope.launch {
            // Корутина продолжит работать после destroy Activity
            delay(10_000)
            textView.text = "Done" // Crash или leak
        }
    }
}

// ✅ lifecycleScope - автоматическая очистка
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Автоматически отменяется при destroy
            delay(10_000)
            textView.text = "Done" // Безопасно
        }
    }
}
```

### Иерархия scopes в Android

```kotlin
// Уровень 1: Application scope
class App : Application() {
    val applicationScope = CoroutineScope(SupervisorJob() + Dispatchers.Default)

    override fun onTerminate() {
        applicationScope.cancel()
    }
}

// Уровень 2: ViewModel scope
class UserViewModel : ViewModel() {
    // viewModelScope автоматически отменяется в onCleared()
    fun loadData() = viewModelScope.launch {
        // ...
    }
}

// Уровень 3: Lifecycle scope
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        // lifecycleScope отменяется при destroy Fragment
        lifecycleScope.launch {
            // ...
        }

        // viewLifecycleOwner.lifecycleScope отменяется при destroyView
        viewLifecycleOwner.lifecycleScope.launch {
            // Безопасно для работы с View
        }
    }
}
```

### Structured Concurrency vs Unstructured

| Аспект | Unstructured (Thread, GlobalScope) | Structured (Coroutines with scopes) |
|--------|-----------------------------------|-------------------------------------|
| **Отмена** | Ручная для каждого потока | Автоматическая иерархическая |
| **Lifecycle** | Нет связи с Android lifecycle | Встроенная интеграция |
| **Ошибки** | Обработка в каждом потоке | Централизованная через scope |
| **Memory leaks** | Высокий риск | Автоматическая профилактика |
| **Тестирование** | Сложное | Простое с TestDispatcher |

### Итог

Structured Concurrency критична для Android, потому что:
- ✅ Предотвращает memory leaks автоматически
- ✅ Интегрируется с lifecycle компонентов
- ✅ Упрощает обработку ошибок
- ✅ Делает код более предсказуемым и надёжным
- ✅ Облегчает тестирование
</details>

## Связи с детальными файлами

Этот overview файл связан со следующими детальными материалами:

### Handler и Looper
**[[android-handler-looper]]** - детальное погружение в механизм Handler-Looper-MessageQueue, основу Android threading модели с 2008 года. Объясняет, как работает Main Thread, почему Handler всё ещё используется, и как правильно работать с Looper.

### AsyncTask и причины deprecation
**[[android-asynctask-deprecated]]** - полный разбор почему AsyncTask был deprecated, какие фундаментальные проблемы привели к этому решению, и как правильно мигрировать legacy код на современные альтернативы.

### Executors и ThreadPool
**[[android-executors]]** - Java Concurrency Utilities в Android: ExecutorService, ThreadPoolExecutor, ScheduledExecutorService. Когда использовать в 2025, интеграция с Kotlin Coroutines, и best practices для Java-Kotlin interop.

### RxJava в Android
**[[android-rxjava]]** - подробный гайд по RxJava 2/3 в Android-проектах: операторы, schedulers, error handling, интеграция с Android lifecycle, миграция на Flow, и когда RxJava всё ещё оправдан в 2024-2025.

### Типичные ошибки с Coroutines
**[[android-coroutines-mistakes]]** - каталог распространённых ошибок при работе с Kotlin Coroutines: неправильный выбор scope, блокирующие операции в suspend functions, неправильная отмена, и antipatterns.

### Threading и многопоточность
**[[android-threading]]** - комплексный гайд по threading в Android: Main Thread, Worker Threads, Thread Pool, StrictMode, профилирование performance, и best practices для многопоточного программирования.

## Заключение

Эволюция асинхронных подходов в Android отражает развитие всей платформы:

- **2008-2014**: Примитивные инструменты (Thread, Handler, AsyncTask)
- **2014-2019**: Reactive revolution (RxJava, LiveData, Architecture Components)
- **2019-2025**: Kotlin-first подход (Coroutines, Flow, structured concurrency)

**Современный стандарт (2025)**:
- Kotlin Coroutines для 95% асинхронных задач
- WorkManager для guaranteed background work
- Flow для reactive data streams
- Legacy RxJava в maintenance mode

**Ключевые принципы**:
- Всегда используйте lifecycle-aware scopes
- Предпочитайте structured concurrency
- Не блокируйте Main Thread
- Тестируйте асинхронный код с TestDispatcher
- Мониторьте performance с Android Profiler

Асинхронность в Android - это не просто технический аспект, а фундаментальная часть user experience. Правильный выбор и использование асинхронных подходов напрямую влияет на плавность UI, время отклика приложения, и удовлетворённость пользователей.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
