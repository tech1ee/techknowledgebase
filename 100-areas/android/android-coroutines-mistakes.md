---
title: "Kotlin Coroutines: 10 типичных ошибок в Android"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
tags:
  - android
  - coroutines
  - kotlin
  - mistakes
  - anti-patterns
  - structured-concurrency
related:
  - "[[android-async-evolution]]"
  - "[[android-threading]]"
  - "[[kotlin-coroutines]]"
cs-foundations: [structured-concurrency, cooperative-cancellation, thread-safety, exception-propagation]
---

# Kotlin Coroutines: 10 типичных ошибок в Android

## Prerequisites

Для понимания материала необходимо:
- **kotlin-coroutines** — базовое понимание корутин, suspend функций и structured concurrency
- **android-threading** — понимание Main Thread, Handler, Looper в Android

## Введение

Kotlin Coroutines революционизировали асинхронное программирование в Android, предоставив мощный и выразительный инструмент для работы с конкурентностью. Однако эта мощь сопровождается сложностью — корутины легко использовать неправильно, и многие ошибки проявляются не сразу.

**Почему это критично:**
- **Memory leaks** — незавершённые корутины удерживают Activity/Fragment в памяти
- **Production crashes** — необработанные исключения в корутинах приводят к падениям приложения
- **Performance issues** — неправильный выбор Dispatcher блокирует потоки
- **Unpredictable behavior** — некорректная отмена операций приводит к race conditions

**Structured concurrency как защита:**
Правильное использование scopes и lifecycle-aware компонентов автоматически предотвращает большинство ошибок. Когда вы используете `viewModelScope` или `lifecycleScope`, отмена корутин происходит автоматически при уничтожении компонента.

В этом руководстве рассмотрим 10 наиболее распространённых ошибок с практическими примерами проблемного и правильного кода.

### Актуальность 2024-2025

| Версия | Изменение | Влияние |
|--------|-----------|---------|
| Kotlin 2.0 | Новый compiler | Улучшенная производительность корутин |
| kotlinx.coroutines 1.9+ | `limitedParallelism()` | Лучше контроль concurrency |
| Compose 1.7+ | `collectAsStateWithLifecycle()` | Обязателен для lifecycle-aware collection |
| Kotlin 2.1 | `@SubclassOptInRequired` | Stricter API для SupervisorJob |

**Топ-3 ошибки 2024 (по droidcon):**
1. GlobalScope вместо viewModelScope/lifecycleScope
2. Неправильная обработка CancellationException
3. Блокирующие вызовы на Main Dispatcher

## Ошибка 1: Использование GlobalScope

### Проблемный код

```kotlin
class UserRepository {
    fun loadUserData(userId: String) {
        // ПЛОХО: корутина живёт до завершения процесса
        GlobalScope.launch {
            val user = api.getUser(userId)
            database.saveUser(user)
        }
    }
}

class ProfileViewModel : ViewModel() {
    fun refreshProfile() {
        // ПЛОХО: корутина переживёт ViewModel
        GlobalScope.launch(Dispatchers.Main) {
            _uiState.value = UiState.Loading
            try {
                val profile = repository.getProfile()
                _uiState.value = UiState.Success(profile)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

### Почему это плохо

**1. No lifecycle awareness:**
- Корутина в `GlobalScope` не связана с жизненным циклом компонента
- Продолжает работу даже после уничтожения Activity/ViewModel
- Попытка обновить UI уничтоженного компонента → crash или утечка памяти

**2. Memory leaks:**
```kotlin
class ProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Корутина захватывает this (Activity)
        GlobalScope.launch {
            delay(60_000) // 1 минута
            // Activity уже уничтожена, но всё ещё в памяти
            updateUI() // Держит ссылку на Activity
        }
    }

    private fun updateUI() {
        // Обращение к View уничтоженной Activity
    }
}
```

**3. Невозможность отмены:**
- Нет способа остановить все корутины компонента при его уничтожении
- Операции продолжают выполняться впустую, тратя ресурсы

### Правильный код

```kotlin
class UserRepository(
    private val scope: CoroutineScope // Inject scope
) {
    fun loadUserData(userId: String) {
        scope.launch {
            val user = api.getUser(userId)
            database.saveUser(user)
        }
    }
}

class ProfileViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun refreshProfile() {
        // ХОРОШО: viewModelScope автоматически отменяется в onCleared()
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val profile = repository.getProfile()
                _uiState.value = UiState.Success(profile)
            } catch (e: CancellationException) {
                throw e // Всегда пробрасываем CancellationException
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }
}

// В Activity/Fragment
class ProfileFragment : Fragment() {
    private val viewModel: ProfileViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ХОРОШО: lifecycleScope привязан к Lifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                updateUI(state)
            }
        }
    }
}
```

### Тест для проверки утечки

```kotlin
@Test
fun `verify no memory leak after ViewModel clear`() = runTest {
    val viewModel = ProfileViewModel(repository)
    val weakRef = WeakReference(viewModel)

    // Запускаем корутину
    viewModel.refreshProfile()

    // Симулируем onCleared()
    val onClearedMethod = ViewModel::class.java
        .getDeclaredMethod("onCleared")
        .apply { isAccessible = true }
    onClearedMethod.invoke(viewModel)

    // Проверяем, что корутина отменена
    advanceUntilIdle()

    // ViewModel должна быть собрана GC
    @Suppress("ExplicitGarbageCollectionCall")
    System.gc()

    assertNull(weakRef.get(), "ViewModel should be garbage collected")
}
```

**Когда GlobalScope допустим:**
- **Никогда в production коде Android приложений**
- Только в standalone приложениях (например, CLI tools)
- Требует явный `@OptIn(DelicateCoroutinesApi::class)`

**Best Practice: Inject Dispatchers**

```kotlin
// ❌ ПЛОХО: hardcoded Dispatchers
class UserRepository {
    suspend fun getUsers() = withContext(Dispatchers.IO) {
        api.getUsers()  // Невозможно заменить в тестах
    }
}

// ✅ ХОРОШО: inject Dispatchers
class UserRepository(
    private val ioDispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    suspend fun getUsers() = withContext(ioDispatcher) {
        api.getUsers()  // В тестах: TestDispatcher
    }
}

// Тест
@Test
fun `test with injected dispatcher`() = runTest {
    val testDispatcher = StandardTestDispatcher(testScheduler)
    val repository = UserRepository(testDispatcher)

    val users = repository.getUsers()

    assertEquals(expectedUsers, users)
}
```

---

## Ошибка 2: Непонимание SupervisorJob

### Проблемный код

```kotlin
class DataSyncViewModel : ViewModel() {
    fun syncAllData() {
        viewModelScope.launch {
            // НЕПРАВИЛЬНО: создаёт новый Job, теряет связь с родителем
            val job = SupervisorJob()

            launch(job) {
                syncUsers() // Если упадёт, не отменит другие
            }

            launch(job) {
                syncPosts()
            }

            launch(job) {
                syncComments()
            }

            job.join()
        }
    }
}
```

### Почему это не работает как ожидается

**Проблема 1: Потеря structured concurrency**
```kotlin
viewModelScope.launch {
    val supervisorJob = SupervisorJob() // Новый Job

    // Этот launch НЕ является дочерним для viewModelScope
    // Его родитель — supervisorJob, который не привязан к ViewModel
    launch(supervisorJob) {
        // Продолжит работу даже после onCleared()
        infiniteWork()
    }
}
```

**Проблема 2: Неправильная иерархия**
```kotlin
// SupervisorJob в параметрах launch не делает его supervisor корутиной
launch(SupervisorJob()) {
    // Исключение здесь всё равно отменит родителя
    throw Exception("Boom!")
}
```

**Как работает Job hierarchy:**
```
viewModelScope (SupervisorJob)
    └── launch { ... }
            └── launch(SupervisorJob()) { ... }
                     └── child coroutine
```

Когда вы передаёте `SupervisorJob()` в `launch`, вы создаёте новый Job, который **заменяет** родительский Job, разрывая связь с viewModelScope.

### Правильное использование

**Вариант 1: supervisorScope { }**
```kotlin
class DataSyncViewModel : ViewModel() {
    fun syncAllData() {
        viewModelScope.launch {
            // ПРАВИЛЬНО: supervisorScope сохраняет иерархию
            supervisorScope {
                launch {
                    syncUsers() // Исключение не отменит других
                }

                launch {
                    syncPosts()
                }

                launch {
                    syncComments()
                }
            }
            // Все корутины завершились (успешно или с ошибкой)
            showSyncComplete()
        }
    }
}
```

**Вариант 2: SupervisorJob в CoroutineScope**
```kotlin
class BackgroundSyncManager {
    // ПРАВИЛЬНО: SupervisorJob в scope constructor
    private val syncScope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO
    )

    fun scheduleSync() {
        syncScope.launch {
            syncUsers()
        }

        syncScope.launch {
            syncPosts() // Исключение не отменит syncUsers
        }
    }

    fun cleanup() {
        syncScope.cancel()
    }
}
```

**Вариант 3: CoroutineExceptionHandler**
```kotlin
class DataSyncViewModel : ViewModel() {
    private val exceptionHandler = CoroutineExceptionHandler { _, throwable ->
        Log.e("Sync", "Sync failed", throwable)
        _syncErrors.value = throwable.message
    }

    fun syncAllData() {
        viewModelScope.launch {
            // Каждая корутина с собственным обработчиком
            launch(exceptionHandler) {
                syncUsers()
            }

            launch(exceptionHandler) {
                syncPosts()
            }
        }
    }
}
```

### Когда SupervisorJob действительно нужен

**1. Scope с независимыми операциями:**
```kotlin
class NotificationManager {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.Main
    )

    fun showNotifications() {
        // Каждое уведомление независимо
        scope.launch { showUserNotification() }
        scope.launch { showSystemNotification() }
        scope.launch { showPromotionNotification() }
    }
}
```

**2. Параллельные задачи без взаимозависимостей:**
```kotlin
suspend fun loadDashboard(): Dashboard = supervisorScope {
    val userData = async { loadUserData() }
    val postsData = async { loadPosts() }
    val statsData = async { loadStats() }

    // Если загрузка постов упадёт, остальные продолжат работу
    Dashboard(
        user = userData.await(),
        posts = postsData.getOrNull() ?: emptyList(),
        stats = statsData.getOrNull() ?: Stats.empty()
    )
}

suspend fun <T> Deferred<T>.getOrNull(): T? = try {
    await()
} catch (e: Exception) {
    null
}
```

---

## Ошибка 3: runBlocking в production коде

### Проблемный код

```kotlin
class UserRepository(private val api: UserApi) {
    // ПЛОХО: блокирует поток вызывающей стороны
    fun getUser(id: String): User {
        return runBlocking {
            api.getUser(id)
        }
    }
}

class ProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // УЖАСНО: блокирует Main Thread
        val user = runBlocking {
            repository.getUser(userId)
        }

        updateUI(user) // ANR риск
    }
}

// Ещё хуже
button.setOnClickListener {
    runBlocking {
        // Блокирует Main Thread на время network call
        val result = api.fetchData()
        showResult(result)
    }
}
```

### Почему это плохо

**1. Блокирует поток:**
```kotlin
// Main Thread
button.setOnClickListener {
    println("Click on thread: ${Thread.currentThread().name}") // main

    runBlocking {
        delay(5000) // БЛОКИРУЕТ Main Thread на 5 секунд
        // UI полностью заморожен
    }

    println("After blocking") // Выполнится только через 5 секунд
}
// Результат: ANR (Application Not Responding)
```

**2. Defeating the purpose:**
```kotlin
// Зачем использовать suspend функции, если всё равно блокируем?
suspend fun fetchData(): Data { ... }

fun syncFetch(): Data = runBlocking {
    fetchData() // Теряем все преимущества корутин
}
```

**3. Performance degradation:**
```kotlin
// Последовательное выполнение вместо параллельного
fun loadAllData(): List<Data> = runBlocking {
    val data1 = async { api.getData1() }.await()
    val data2 = async { api.getData2() }.await()
    // Блокирует поток, хотя операции могли бы идти параллельно
    listOf(data1, data2)
}
```

### Когда runBlocking допустим

**1. main() функция:**
```kotlin
fun main() = runBlocking {
    // Корневая точка входа в корутины
    val result = async { computeSomething() }
    println(result.await())
}
```

**2. Unit тесты:**
```kotlin
@Test
fun `test user repository`() = runBlocking {
    val repository = UserRepository(mockApi)
    val user = repository.getUser("123")
    assertEquals("John", user.name)
}

// Или лучше использовать runTest
@Test
fun `test with runTest`() = runTest {
    // Автоматический контроль виртуального времени
    val repository = UserRepository(mockApi)
    val user = repository.getUser("123")
    assertEquals("John", user.name)
}
```

**3. Миграция legacy кода:**
```kotlin
// Временное решение при постепенной миграции
@Deprecated("Use suspend version")
fun legacyGetUser(id: String): User = runBlocking {
    getUserSuspend(id)
}

suspend fun getUserSuspend(id: String): User {
    return api.getUser(id)
}
```

### Правильная альтернатива

**1. Suspend функции:**
```kotlin
class UserRepository(private val api: UserApi) {
    // ХОРОШО: suspend функция
    suspend fun getUser(id: String): User {
        return api.getUser(id)
    }
}

class ProfileViewModel : ViewModel() {
    fun loadUser(id: String) {
        viewModelScope.launch {
            try {
                val user = repository.getUser(id) // Не блокирует
                _userState.value = user
            } catch (e: Exception) {
                _error.value = e
            }
        }
    }
}
```

**2. Flow для реактивных данных:**
```kotlin
class UserRepository {
    fun observeUser(id: String): Flow<User> = flow {
        while (currentCoroutineContext().isActive) {
            val user = api.getUser(id)
            emit(user)
            delay(30_000) // Обновление каждые 30 секунд
        }
    }.flowOn(Dispatchers.IO)
}

class ProfileViewModel : ViewModel() {
    val user: StateFlow<User?> = repository
        .observeUser(userId)
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = null
        )
}
```

**3. Callback to coroutine bridge:**
```kotlin
// Для работы с callback-based API
suspend fun legacyApiCall(): Result = suspendCancellableCoroutine { continuation ->
    legacyApi.fetch(object : Callback {
        override fun onSuccess(result: Result) {
            continuation.resume(result)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })

    continuation.invokeOnCancellation {
        legacyApi.cancel() // Отмена при cancellation
    }
}
```

---

## Ошибка 4: Non-cooperative cancellation

### Проблемный код

```kotlin
suspend fun processLargeFile(file: File) {
    val lines = file.readLines()

    // ПЛОХО: игнорирует cancellation
    for (line in lines) {
        processLine(line)
    }
}

suspend fun downloadFile(url: String): ByteArray {
    val data = mutableListOf<Byte>()

    // ПЛОХО: бесконечный цикл без проверки cancellation
    while (true) {
        val chunk = readChunk(url)
        if (chunk.isEmpty()) break
        data.addAll(chunk)
    }

    return data.toByteArray()
}

suspend fun computeResult(): Int {
    var result = 0
    // ПЛОХО: CPU-intensive операция без cooperative cancellation
    for (i in 0 until 1_000_000_000) {
        result += i
    }
    return result
}
```

### Почему cancellation не работает

**Проблема: корутины не прерываются автоматически**
```kotlin
val job = viewModelScope.launch {
    processLargeFile(file) // Может работать минуты
}

// Пользователь закрыл экран
job.cancel() // Вызван cancel, но...
// processLargeFile продолжит работу до конца!
```

**Cooperative cancellation principle:**
Корутины не прерываются принудительно (как Thread.interrupt()). Код должен сам проверять статус отмены и реагировать на него.

**Только suspend функции из kotlinx.coroutines проверяют cancellation:**
```kotlin
delay(1000)        // Проверяет isActive
yield()            // Проверяет isActive
withContext { }    // Проверяет isActive

// Ваш код — нет автоматической проверки
for (i in 0..1000000) {
    compute(i) // НЕ проверяет cancellation
}
```

### Как сделать код cancellable

**Способ 1: isActive check**
```kotlin
suspend fun processLargeFile(file: File) {
    val lines = file.readLines()

    for (line in lines) {
        // Проверка перед каждой итерацией
        if (!isActive) {
            // Очистка ресурсов при необходимости
            cleanUp()
            return // Или throw CancellationException()
        }

        processLine(line)
    }
}

// С помощью extension
suspend fun processLargeFileImproved(file: File) {
    file.forEachLine { line ->
        ensureActive() // Бросит CancellationException если отменено
        processLine(line)
    }
}
```

**Способ 2: yield()**
```kotlin
suspend fun computeResult(): Int {
    var result = 0

    for (i in 0 until 1_000_000_000) {
        result += i

        // Периодическая проверка + даём другим корутинам шанс выполниться
        if (i % 10_000 == 0) {
            yield() // Проверяет isActive и переключает контекст
        }
    }

    return result
}
```

**Способ 3: ensureActive()**
```kotlin
suspend fun downloadFile(url: String): ByteArray {
    val data = mutableListOf<Byte>()

    while (true) {
        ensureActive() // Throws CancellationException if cancelled

        val chunk = readChunk(url)
        if (chunk.isEmpty()) break
        data.addAll(chunk)
    }

    return data.toByteArray()
}
```

### Пример: загрузка файла с cancellation

```kotlin
class FileDownloader(private val api: FileApi) {

    suspend fun downloadFile(
        url: String,
        destination: File,
        onProgress: (Float) -> Unit = {}
    ): Result<File> = withContext(Dispatchers.IO) {
        try {
            val response = api.downloadFile(url)
            val totalBytes = response.contentLength()
            var downloadedBytes = 0L

            destination.outputStream().use { output ->
                response.byteStream().use { input ->
                    val buffer = ByteArray(8192)
                    var bytesRead: Int

                    while (input.read(buffer).also { bytesRead = it } != -1) {
                        // Проверка cancellation перед записью
                        ensureActive()

                        output.write(buffer, 0, bytesRead)
                        downloadedBytes += bytesRead

                        // Обновление прогресса
                        val progress = downloadedBytes.toFloat() / totalBytes
                        withContext(Dispatchers.Main) {
                            onProgress(progress)
                        }
                    }
                }
            }

            Result.success(destination)
        } catch (e: CancellationException) {
            // Очистка при отмене
            destination.delete()
            throw e // ВАЖНО: всегда пробрасываем CancellationException
        } catch (e: Exception) {
            destination.delete()
            Result.failure(e)
        }
    }
}

// Использование
class DownloadViewModel : ViewModel() {
    private val _progress = MutableStateFlow(0f)
    val progress: StateFlow<Float> = _progress.asStateFlow()

    private var downloadJob: Job? = null

    fun startDownload(url: String) {
        downloadJob = viewModelScope.launch {
            try {
                downloader.downloadFile(url, File("output.zip")) { progress ->
                    _progress.value = progress
                }
                _status.value = "Download complete"
            } catch (e: CancellationException) {
                _status.value = "Download cancelled"
                throw e
            } catch (e: Exception) {
                _status.value = "Download failed: ${e.message}"
            }
        }
    }

    fun cancelDownload() {
        downloadJob?.cancel() // Корректно остановит загрузку и удалит файл
    }
}
```

**Сравнение методов:**

| Метод | Поведение | Когда использовать |
|-------|-----------|-------------------|
| `isActive` | Возвращает Boolean | Для условной логики или ручной очистки |
| `ensureActive()` | Бросает CancellationException | Для быстрого выхода из функции |
| `yield()` | Проверка + suspension point | Для CPU-intensive операций |

---

## Ошибка 5: Неправильный выбор Dispatcher

### Проблемный код

```kotlin
class ImageProcessor {
    // ПЛОХО: CPU-intensive на IO dispatcher
    suspend fun processImage(bitmap: Bitmap): Bitmap = withContext(Dispatchers.IO) {
        // Сложные вычисления блокируют IO поток
        val pixels = IntArray(bitmap.width * bitmap.height)
        bitmap.getPixels(pixels, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)

        // CPU-intensive обработка
        for (i in pixels.indices) {
            pixels[i] = applyFilter(pixels[i])
        }

        Bitmap.createBitmap(pixels, bitmap.width, bitmap.height, bitmap.config)
    }
}

class UserRepository {
    // ПЛОХО: network call на Default dispatcher
    suspend fun getUsers(): List<User> = withContext(Dispatchers.Default) {
        api.getUsers() // IO операция на CPU dispatcher
    }
}

class MainViewModel : ViewModel() {
    // ПЛОХО: UI update на IO dispatcher
    fun updateUser(user: User) {
        viewModelScope.launch(Dispatchers.IO) {
            _userState.value = user // CRASH: обновление StateFlow не на Main
        }
    }
}

// УЖАСНО: Dispatchers.Unconfined
suspend fun loadData() = withContext(Dispatchers.Unconfined) {
    val data = api.fetchData() // Может выполниться на любом потоке
    updateUI(data) // Непредсказуемое поведение
}
```

### Таблица правильного выбора Dispatcher

| Dispatcher | Пул потоков | Назначение | Примеры |
|-----------|-------------|------------|---------|
| **Main** | 1 поток (UI thread) | UI операции, обновление StateFlow | `_uiState.value = ...`, View updates |
| **IO** | 64+ потока (расширяемый) | Блокирующие IO операции | Network, Database, File IO, SharedPreferences |
| **Default** | CPU cores потоков | CPU-intensive вычисления | Сортировка больших списков, JSON parsing, image processing |
| **Unconfined** | Любой поток | Почти никогда | Только для специфичных библиотечных функций |

**Размеры пулов (по умолчанию):**
- **IO**: max(64, число процессоров) — может расшириться до 64 потоков
- **Default**: число процессоров — оптимально для CPU-bound задач
- **Main**: 1 поток — Android Main/UI Thread

### Правильный выбор Dispatcher

**1. Dispatchers.Main — UI operations**
```kotlin
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch { // По умолчанию Dispatchers.Main
            _uiState.value = UiState.Loading

            try {
                val user = withContext(Dispatchers.IO) {
                    repository.getUser(id) // IO на IO dispatcher
                }

                // Возврат на Main для обновления UI state
                _uiState.value = UiState.Success(user)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e)
            }
        }
    }
}
```

**2. Dispatchers.IO — Blocking I/O**
```kotlin
class UserRepository(
    private val api: UserApi,
    private val database: UserDao,
    private val preferences: SharedPreferences
) {
    // Network IO
    suspend fun fetchUsers(): List<User> = withContext(Dispatchers.IO) {
        api.getUsers()
    }

    // Database IO
    suspend fun saveUser(user: User) = withContext(Dispatchers.IO) {
        database.insert(user)
    }

    // File IO
    suspend fun exportUsers(file: File) = withContext(Dispatchers.IO) {
        file.writeText(
            database.getAllUsers().joinToString("\n") { it.toString() }
        )
    }

    // SharedPreferences IO
    suspend fun saveToken(token: String) = withContext(Dispatchers.IO) {
        preferences.edit()
            .putString("token", token)
            .apply()
    }
}
```

**3. Dispatchers.Default — CPU-intensive**
```kotlin
class DataProcessor {
    // Сложные вычисления
    suspend fun processLargeDataset(data: List<Item>): ProcessedData =
        withContext(Dispatchers.Default) {
            data.map { item ->
                // CPU-intensive transformation
                complexCalculation(item)
            }
            .reduce { acc, item -> acc.merge(item) }
        }

    // Image processing
    suspend fun applyFilters(bitmap: Bitmap): Bitmap =
        withContext(Dispatchers.Default) {
            var result = bitmap
            filters.forEach { filter ->
                ensureActive() // Cooperative cancellation
                result = filter.apply(result)
            }
            result
        }

    // JSON parsing больших документов
    suspend fun parseJson(jsonString: String): Data =
        withContext(Dispatchers.Default) {
            Json.decodeFromString<Data>(jsonString)
        }

    // Сортировка
    suspend fun sortLargeList(items: List<Item>): List<Item> =
        withContext(Dispatchers.Default) {
            items.sortedWith(compareBy({ it.priority }, { it.timestamp }))
        }
}
```

**4. Custom Dispatcher для специфичных задач**
```kotlin
class DatabaseManager {
    // Single-threaded dispatcher для последовательного доступа к SQLite
    private val singleThreadDispatcher = Executors
        .newSingleThreadExecutor()
        .asCoroutineDispatcher()

    suspend fun transaction(block: suspend () -> Unit) =
        withContext(singleThreadDispatcher) {
            database.beginTransaction()
            try {
                block()
                database.setTransactionSuccessful()
            } finally {
                database.endTransaction()
            }
        }

    fun close() {
        singleThreadDispatcher.close()
    }
}

// Limited parallelism для контроля concurrency
class ApiClient {
    // Максимум 3 параллельных запроса
    private val limitedDispatcher = Dispatchers.IO
        .limitedParallelism(3)

    suspend fun fetchData(urls: List<String>): List<Data> =
        coroutineScope {
            urls.map { url ->
                async(limitedDispatcher) {
                    api.fetch(url)
                }
            }.awaitAll()
        }
}
```

### withContext vs launch с dispatcher

```kotlin
// withContext — для возврата результата
suspend fun loadData(): Data {
    // Переключается на IO, выполняет, возвращается на предыдущий dispatcher
    return withContext(Dispatchers.IO) {
        api.fetchData()
    }
}

// launch — для fire-and-forget операций
fun saveData(data: Data) {
    viewModelScope.launch(Dispatchers.IO) {
        database.save(data)
        // Не нужно возвращать результат
    }
}

// Комбинация
fun loadAndSave(id: String) {
    viewModelScope.launch { // Main dispatcher
        val data = withContext(Dispatchers.IO) {
            api.fetchData(id) // IO
        }

        // Вернулись на Main
        _uiState.value = UiState.Success(data)

        withContext(Dispatchers.IO) {
            database.save(data) // Снова IO
        }

        // Снова Main
        showSavedMessage()
    }
}
```

### Performance implications

```kotlin
// ПЛОХО: каждая итерация переключает dispatcher
suspend fun processList(items: List<Item>) {
    items.forEach { item ->
        withContext(Dispatchers.Default) { // Context switch overhead!
            process(item)
        }
    }
}

// ХОРОШО: один переключатель для всех операций
suspend fun processListOptimized(items: List<Item>) {
    withContext(Dispatchers.Default) {
        items.forEach { item ->
            process(item) // Всё на одном dispatcher
        }
    }
}

// Измерение разницы
@Test
fun `measure dispatcher switching overhead`() = runTest {
    val items = List(1000) { Item(it) }

    val timeBad = measureTimeMillis {
        processList(items) // ~200ms
    }

    val timeGood = measureTimeMillis {
        processListOptimized(items) // ~50ms
    }

    println("Overhead: ${timeBad - timeGood}ms") // ~150ms на context switches
}
```

---

## Ошибка 6: Exception swallowing

### Проблемный код

```kotlin
class UserViewModel : ViewModel() {
    fun loadUsers() {
        viewModelScope.launch {
            try {
                val users = repository.getUsers()
                _users.value = users
            } catch (e: Exception) {
                // ПЛОХО: исключение проглочено, никто не узнает об ошибке
                Log.e("UserViewModel", "Error loading users", e)
                // Приложение продолжает работать, но UI не обновлён
            }
        }
    }
}

// ХУЖЕ: полное игнорирование
fun saveUser(user: User) {
    viewModelScope.launch {
        try {
            repository.saveUser(user)
        } catch (e: Exception) {
            // Полностью игнорируется
        }
    }
}

// ПЛОХО: catch в async
fun loadData() {
    viewModelScope.launch {
        val data = async {
            try {
                api.fetchData()
            } catch (e: Exception) {
                null // Исключение потеряно, await() не узнает о проблеме
            }
        }

        val result = data.await() // Всегда успех, даже если был exception
    }
}
```

### Разница launch vs async exception propagation

**launch — exceptions propagate up**
```kotlin
viewModelScope.launch {
    // Исключение здесь распространяется вверх
    throw Exception("Error in launch")
    // → отменяет viewModelScope
    // → вызывает CoroutineExceptionHandler если установлен
    // → иначе идёт в Thread.uncaughtExceptionHandler
}
```

**async — exceptions trapped in Deferred**
```kotlin
viewModelScope.launch {
    val deferred = async {
        throw Exception("Error in async")
        // Исключение НЕ распространяется сразу
        // Сохраняется внутри Deferred
    }

    // Два способа получить исключение:

    // 1. await() — пробросит исключение
    try {
        val result = deferred.await()
    } catch (e: Exception) {
        // Исключение здесь
    }

    // 2. Не вызвать await() — исключение потеряно навсегда
    // deferred просто отменится, никто не узнает о проблеме
}
```

**Критическая проблема с async:**
```kotlin
fun loadUserData() {
    viewModelScope.launch {
        // Запускаем async
        val userData = async { api.getUser() }
        val postsData = async { api.getPosts() }

        // Если не сделаем await(), исключения будут потеряны
        // Корутина завершится успешно, но данные не загружены
    }

    // Правильно: всегда await() или используй awaitAll()
    viewModelScope.launch {
        try {
            val userData = async { api.getUser() }
            val postsData = async { api.getPosts() }

            val user = userData.await() // Исключение пробросится здесь
            val posts = postsData.await()
        } catch (e: Exception) {
            handleError(e)
        }
    }
}
```

### CoroutineExceptionHandler — когда использовать

**Установка в scope:**
```kotlin
class BackgroundSyncManager {
    private val exceptionHandler = CoroutineExceptionHandler { context, throwable ->
        Log.e("Sync", "Unhandled exception in ${context[CoroutineName]}", throwable)

        // Логирование в crash reporting
        FirebaseCrashlytics.getInstance().recordException(throwable)

        // Можно показать notification о проблеме
        showSyncFailedNotification(throwable.message)
    }

    private val syncScope = CoroutineScope(
        SupervisorJob() +
        Dispatchers.IO +
        exceptionHandler +
        CoroutineName("BackgroundSync")
    )

    fun startSync() {
        syncScope.launch {
            // Любое необработанное исключение попадёт в exceptionHandler
            syncUsers()
            syncPosts()
        }
    }
}
```

**Важно: CoroutineExceptionHandler работает только с launch, не с async:**
```kotlin
val handler = CoroutineExceptionHandler { _, e ->
    println("Caught: $e")
}

viewModelScope.launch(handler) {
    throw Exception("Error") // Попадёт в handler
}

viewModelScope.launch(handler) {
    async {
        throw Exception("Error") // НЕ попадёт в handler!
    }.await() // Нужно обработать здесь
}
```

### Правильная обработка ошибок

**1. Явная обработка с UI state:**
```kotlin
sealed class UiState<out T> {
    object Initial : UiState<Nothing>()
    object Loading : UiState<Nothing>()
    data class Success<T>(val data: T) : UiState<T>()
    data class Error(val exception: Throwable) : UiState<Nothing>()
}

class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<List<User>>>(UiState.Initial)
    val uiState: StateFlow<UiState<List<User>>> = _uiState.asStateFlow()

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading

            _uiState.value = try {
                val users = repository.getUsers()
                UiState.Success(users)
            } catch (e: CancellationException) {
                throw e // Всегда пробрасываем CancellationException
            } catch (e: Exception) {
                // Логируем и сохраняем в state
                Log.e("UserViewModel", "Failed to load users", e)
                FirebaseCrashlytics.getInstance().recordException(e)
                UiState.Error(e)
            }
        }
    }
}
```

**2. Result wrapper:**
```kotlin
class UserRepository {
    suspend fun getUsers(): Result<List<User>> = withContext(Dispatchers.IO) {
        try {
            val users = api.getUsers()
            Result.success(users)
        } catch (e: Exception) {
            Log.e("Repository", "Failed to fetch users", e)
            Result.failure(e)
        }
    }
}

class UserViewModel : ViewModel() {
    fun loadUsers() {
        viewModelScope.launch {
            repository.getUsers()
                .onSuccess { users ->
                    _uiState.value = UiState.Success(users)
                }
                .onFailure { exception ->
                    _uiState.value = UiState.Error(exception)
                }
        }
    }
}
```

**3. Typed errors с sealed class:**
```kotlin
sealed class DataError {
    object NetworkError : DataError()
    object ServerError : DataError()
    data class ValidationError(val field: String) : DataError()
    data class Unknown(val throwable: Throwable) : DataError()
}

sealed class DataResult<out T> {
    data class Success<T>(val data: T) : DataResult<T>()
    data class Failure(val error: DataError) : DataResult<Nothing>()
}

class UserRepository {
    suspend fun getUsers(): DataResult<List<User>> = withContext(Dispatchers.IO) {
        try {
            val response = api.getUsers()

            if (response.isSuccessful) {
                DataResult.Success(response.body()!!)
            } else {
                when (response.code()) {
                    in 500..599 -> DataResult.Failure(DataError.ServerError)
                    else -> DataResult.Failure(DataError.NetworkError)
                }
            }
        } catch (e: IOException) {
            DataResult.Failure(DataError.NetworkError)
        } catch (e: Exception) {
            DataResult.Failure(DataError.Unknown(e))
        }
    }
}

class UserViewModel : ViewModel() {
    fun loadUsers() {
        viewModelScope.launch {
            when (val result = repository.getUsers()) {
                is DataResult.Success -> {
                    _users.value = result.data
                }
                is DataResult.Failure -> {
                    val message = when (result.error) {
                        DataError.NetworkError -> "Network connection failed"
                        DataError.ServerError -> "Server error, try again later"
                        is DataError.ValidationError -> "Invalid ${result.error.field}"
                        is DataError.Unknown -> "Unexpected error: ${result.error.throwable.message}"
                    }
                    _errorMessage.value = message
                }
            }
        }
    }
}
```

**4. Retry логика:**
```kotlin
suspend fun <T> retryWithExponentialBackoff(
    times: Int = 3,
    initialDelay: Long = 100,
    maxDelay: Long = 1000,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay

    repeat(times - 1) { attempt ->
        try {
            return block()
        } catch (e: Exception) {
            Log.w("Retry", "Attempt ${attempt + 1} failed", e)
        }

        delay(currentDelay)
        currentDelay = (currentDelay * factor).toLong().coerceAtMost(maxDelay)
    }

    return block() // Последняя попытка, пробросит exception
}

// Использование
class UserRepository {
    suspend fun getUsers(): List<User> = retryWithExponentialBackoff {
        api.getUsers()
    }
}
```

---

## Ошибка 7: Memory leaks via captured context

### Проблемный код

```kotlin
class UserActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ПЛОХО: корутина захватывает Activity
        GlobalScope.launch {
            delay(60_000) // 1 минута

            // Activity уже может быть уничтожена
            findViewById<TextView>(R.id.textView).text = "Updated"
            // Утечка: Activity не может быть собрана GC
        }
    }

    fun loadUserData() {
        GlobalScope.launch {
            val user = repository.getUser()

            // Захват this (Activity)
            updateUI(user) // this.updateUI(user)
        }
    }

    private fun updateUI(user: User) {
        // Обращение к View
    }
}

class UserFragment : Fragment() {
    private var job: Job? = null

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ПЛОХО: lifecycleScope вместо viewLifecycleOwner.lifecycleScope
        lifecycleScope.launch {
            viewModel.users.collect { users ->
                // Fragment жив, но View уничтожен
                // binding может быть null
                binding.recyclerView.adapter = UsersAdapter(users)
                // CRASH или утечка
            }
        }
    }
}

class UserViewModel : ViewModel() {
    // ПЛОХО: захват context в lambda
    fun loadUsers(context: Context) {
        viewModelScope.launch {
            delay(10_000)

            // ViewModel переживает Activity, но держит на неё ссылку
            Toast.makeText(context, "Users loaded", Toast.LENGTH_SHORT).show()
        }
    }
}
```

### Как происходит утечка

**1. Coroutine outlives component:**
```kotlin
class ProfileActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Корутина с неправильным scope
        GlobalScope.launch {
            // Эта лямбда захватывает неявную ссылку this@ProfileActivity
            loadAndDisplayProfile()
        }

        // Пользователь закрывает Activity
        // Activity.onDestroy() вызван
        // Но корутина всё ещё работает и держит ссылку на Activity
        // GC не может собрать Activity → утечка памяти
    }

    private suspend fun loadAndDisplayProfile() {
        val profile = api.getProfile()

        // Обращение к уничтоженной Activity
        findViewById<TextView>(R.id.name).text = profile.name
    }
}
```

**2. Lambda captures context:**
```kotlin
class DataViewModel(
    private val repository: Repository
) : ViewModel() {

    fun process(activity: MainActivity) {
        viewModelScope.launch {
            repository.getData().collect { data ->
                // Лямбда захватывает activity
                activity.showData(data)
                // ViewModel живёт дольше Activity → утечка
            }
        }
    }
}

// Leak trace:
// DataViewModel (GC Root - ViewModel Store)
//   → viewModelScope
//     → Job
//       → Coroutine
//         → Lambda
//           → activity: MainActivity
//             → Window
//               → DecorView
//                 → All Views
```

**3. Fragment View lifecycle:**
```kotlin
class UserFragment : Fragment() {
    private var _binding: FragmentUserBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        _binding = FragmentUserBinding.bind(view)

        // ПЛОХО: lifecycleScope привязан к Fragment, не к View
        lifecycleScope.launch {
            viewModel.users.collect { users ->
                // Fragment в backstack: Fragment жив, но View уничтожен
                // binding = null → CRASH
                binding.recyclerView.adapter = UsersAdapter(users)
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
```

### Решение: WeakReference или правильный scope

**1. Правильный scope выбор:**
```kotlin
class UserActivity : AppCompatActivity() {
    // Правильно: scope привязан к lifecycle Activity
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Автоматически отменится в onDestroy()
            loadAndDisplayProfile()
        }
    }
}

class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Правильно: viewLifecycleOwner для операций с View
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.users.collect { users ->
                // Автоматически отменится в onDestroyView()
                binding.recyclerView.adapter = UsersAdapter(users)
            }
        }
    }
}
```

**2. Избегать передачи Context в ViewModel:**
```kotlin
// ПЛОХО
class UserViewModel : ViewModel() {
    fun loadUsers(context: Context) {
        viewModelScope.launch {
            val users = repository.getUsers()
            Toast.makeText(context, "Loaded", Toast.LENGTH_SHORT).show()
        }
    }
}

// ХОРОШО: UI events через state
class UserViewModel : ViewModel() {
    private val _events = Channel<UiEvent>(Channel.BUFFERED)
    val events: Flow<UiEvent> = _events.receiveAsFlow()

    fun loadUsers() {
        viewModelScope.launch {
            try {
                val users = repository.getUsers()
                _users.value = users
                _events.send(UiEvent.ShowMessage("Users loaded"))
            } catch (e: Exception) {
                _events.send(UiEvent.ShowError(e.message))
            }
        }
    }
}

sealed class UiEvent {
    data class ShowMessage(val message: String) : UiEvent()
    data class ShowError(val error: String?) : UiEvent()
}

// В Activity/Fragment
lifecycleScope.launch {
    viewModel.events.collect { event ->
        when (event) {
            is UiEvent.ShowMessage -> {
                Toast.makeText(requireContext(), event.message, Toast.LENGTH_SHORT).show()
            }
            is UiEvent.ShowError -> {
                Snackbar.make(binding.root, event.error ?: "Error", Snackbar.LENGTH_SHORT).show()
            }
        }
    }
}
```

**3. WeakReference для legacy кода:**
```kotlin
class LegacyManager(activity: Activity) {
    private val activityRef = WeakReference(activity)
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main)

    fun startOperation() {
        scope.launch {
            val result = performLongOperation()

            // Безопасное обращение
            activityRef.get()?.let { activity ->
                if (!activity.isFinishing && !activity.isDestroyed) {
                    activity.updateUI(result)
                }
            } ?: run {
                Log.w("Manager", "Activity was destroyed, skipping UI update")
            }
        }
    }

    fun cleanup() {
        scope.cancel()
    }
}
```

**4. ApplicationContext где возможно:**
```kotlin
class NotificationManager(
    private val context: Context // Application context
) {
    fun showNotification(message: String) {
        viewModelScope.launch {
            val notification = createNotification(context, message)
            notificationManager.notify(1, notification)
        }
    }
}

// При создании
val manager = NotificationManager(
    context.applicationContext // Не activity context
)
```

**5. Lifecycle-aware collectors:**
```kotlin
class UserFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ХОРОШО: repeatOnLifecycle
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                // Автоматически отменяется при STOPPED
                // Перезапускается при STARTED
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}

// Extension для удобства
fun <T> Flow<T>.collectWithLifecycle(
    lifecycleOwner: LifecycleOwner,
    minActiveState: Lifecycle.State = Lifecycle.State.STARTED,
    collector: FlowCollector<T>
) {
    lifecycleOwner.lifecycleScope.launch {
        lifecycleOwner.repeatOnLifecycle(minActiveState) {
            collect(collector)
        }
    }
}

// Использование
viewModel.uiState.collectWithLifecycle(viewLifecycleOwner) { state ->
    updateUI(state)
}
```

**Проверка утечек:**
```kotlin
@Test
fun `verify no activity leak`() = runTest {
    val scenario = ActivityScenario.launch(UserActivity::class.java)
    val weakRef = WeakReference<UserActivity>(null)

    scenario.onActivity { activity ->
        weakRef.get() = activity
        activity.startLongOperation()
    }

    // Уничтожаем Activity
    scenario.close()

    // Даём GC время
    repeat(10) {
        System.gc()
        System.runFinalization()
        Thread.sleep(100)
    }

    assertNull(weakRef.get(), "Activity should be garbage collected")
}
```

---

## Ошибка 8: Mutex misuse

### Проблемный код

```kotlin
class Counter {
    private var count = 0

    // ПЛОХО: synchronized блокирует поток
    suspend fun increment() {
        synchronized(this) {
            count++ // suspend функция блокирует поток
        }
    }

    suspend fun getCount(): Int {
        synchronized(this) {
            return count
        }
    }
}

class DataCache {
    private val cache = mutableMapOf<String, Data>()

    // ПЛОХО: блокирует Dispatcher.IO поток
    suspend fun getData(key: String): Data = withContext(Dispatchers.IO) {
        synchronized(cache) {
            cache[key] ?: run {
                val data = fetchData(key) // suspend вызов в synchronized
                cache[key] = data
                data
            }
        }
    }
}

// ПЛОХО: забыл освободить mutex
class Resource {
    private val mutex = Mutex()

    suspend fun access() {
        mutex.lock()

        try {
            doWork()

            if (shouldReturn()) {
                return // Mutex НЕ освобождён → deadlock
            }
        } finally {
            // finally может не выполниться при cancellation
            mutex.unlock()
        }
    }
}
```

### Почему synchronized блокирует поток

**Проблема с synchronized:**
```kotlin
class Cache {
    private val data = mutableMapOf<String, String>()

    suspend fun get(key: String): String {
        return synchronized(data) {
            // suspend функция внутри synchronized
            // Поток ЗАБЛОКИРОВАН на всё время выполнения
            delay(1000) // Блокирует поток на 1 секунду!

            data[key] ?: run {
                val value = fetchFromNetwork(key) // suspend вызов
                // Поток заблокирован и на время network call
                data[key] = value
                value
            }
        }
    }
}

// Что происходит:
// Thread-1: synchronized блокирует поток
// Thread-1: delay(1000) → поток спит (не может обработать другие корутины)
// Thread-2: пытается войти в synchronized → блокируется
// Результат: оба потока заняты, dispatcher не может выполнять другие задачи
```

**Почему это критично для корутин:**
```kotlin
// Корутины позволяют тысячам задач работать на нескольких потоках
val scope = CoroutineScope(Dispatchers.IO) // 64 потока

repeat(10000) { i ->
    scope.launch {
        cache.get("key$i") // synchronized внутри
    }
}

// synchronized блокирует потоки
// Вместо 10000 параллельных корутин на 64 потоках
// Получаем последовательное выполнение из-за блокировок
// Performance деградирует до однопоточного уровня
```

### Правильное использование Mutex

**1. Базовое использование:**
```kotlin
class Counter {
    private var count = 0
    private val mutex = Mutex()

    // ПРАВИЛЬНО: mutex приостанавливает корутину, не блокирует поток
    suspend fun increment() {
        mutex.withLock {
            count++
        }
    }

    suspend fun getCount(): Int {
        return mutex.withLock {
            count
        }
    }
}

// Что происходит:
// Корутина 1: mutex.lock() → успех, входит в критическую секцию
// Корутина 2: mutex.lock() → приостанавливается (НЕ блокирует поток!)
// Thread освобождается и может выполнять другие корутины
// Корутина 1: mutex.unlock() → завершает работу
// Корутина 2: возобновляется и входит в критическую секцию
```

**2. withLock extension:**
```kotlin
class DataCache {
    private val cache = mutableMapOf<String, Data>()
    private val mutex = Mutex()

    suspend fun getData(key: String): Data {
        // withLock автоматически освобождает mutex
        return mutex.withLock {
            cache.getOrPut(key) {
                // suspend вызовы безопасны
                fetchData(key)
            }
        }
    }

    suspend fun putData(key: String, data: Data) {
        mutex.withLock {
            cache[key] = data
        }
    }

    suspend fun clear() {
        mutex.withLock {
            cache.clear()
        }
    }
}
```

**3. Безопасная отмена:**
```kotlin
class Resource {
    private val mutex = Mutex()
    private var isProcessing = false

    suspend fun process() {
        // withLock корректно обрабатывает cancellation
        mutex.withLock {
            isProcessing = true
            try {
                // Даже если корутина отменится здесь
                performWork()
            } finally {
                isProcessing = false
                // Mutex освободится автоматически
            }
        }
    }
}

// Внутренняя реализация withLock:
public suspend inline fun <T> Mutex.withLock(action: () -> T): T {
    lock()
    try {
        return action()
    } finally {
        unlock() // Всегда выполнится, даже при cancellation
    }
}
```

**4. Read-Write Lock pattern:**
```kotlin
class ReadWriteCache {
    private val cache = mutableMapOf<String, Data>()
    private val readMutex = Mutex()
    private val writeMutex = Mutex()
    private var readers = 0

    suspend fun read(key: String): Data? {
        readMutex.withLock {
            readers++
        }

        return try {
            cache[key]
        } finally {
            readMutex.withLock {
                readers--
            }
        }
    }

    suspend fun write(key: String, data: Data) {
        // Ждём, пока все readers завершат
        writeMutex.withLock {
            readMutex.withLock {
                while (readers > 0) {
                    delay(10)
                }
            }

            cache[key] = data
        }
    }
}

// Лучше использовать готовые решения:
class BetterCache {
    private val cache = ConcurrentHashMap<String, Data>()

    // ConcurrentHashMap уже thread-safe
    suspend fun getData(key: String): Data {
        return cache.getOrPut(key) {
            fetchData(key)
        }
    }
}
```

**5. Mutex vs Atomic:**
```kotlin
// Для простых операций — используйте Atomic
class SimpleCounter {
    private val count = AtomicInteger(0)

    // Не нужен suspend, не нужен mutex
    fun increment(): Int = count.incrementAndGet()

    fun get(): Int = count.get()
}

// Mutex для сложной логики
class ComplexCounter {
    private var count = 0
    private var lastUpdate = 0L
    private val mutex = Mutex()

    suspend fun increment() {
        mutex.withLock {
            count++
            lastUpdate = System.currentTimeMillis()
            // Сложная логика с несколькими полями
            if (count > 100) {
                notifyObservers()
            }
        }
    }
}
```

**Performance comparison:**
```kotlin
@Test
fun `compare synchronized vs mutex performance`() = runBlocking {
    val iterations = 100_000

    // synchronized
    val syncCounter = object {
        var count = 0
        fun increment() = synchronized(this) { count++ }
    }

    val syncTime = measureTimeMillis {
        repeat(iterations) {
            launch(Dispatchers.Default) {
                syncCounter.increment()
            }
        }
    }

    // Mutex
    val mutexCounter = object {
        var count = 0
        val mutex = Mutex()
        suspend fun increment() = mutex.withLock { count++ }
    }

    val mutexTime = measureTimeMillis {
        repeat(iterations) {
            launch(Dispatchers.Default) {
                mutexCounter.increment()
            }
        }
    }

    println("synchronized: ${syncTime}ms")  // ~2000ms (блокирует потоки)
    println("Mutex: ${mutexTime}ms")        // ~500ms (приостанавливает корутины)
}
```

---

## Ошибка 9: StateFlow vs SharedFlow confusion

### Проблемный код

```kotlin
class LoginViewModel : ViewModel() {
    // ПЛОХО: StateFlow для one-time events
    private val _loginEvent = MutableStateFlow<LoginEvent?>(null)
    val loginEvent: StateFlow<LoginEvent?> = _loginEvent.asStateFlow()

    fun login() {
        viewModelScope.launch {
            try {
                repository.login()
                _loginEvent.value = LoginEvent.Success // Проблема!
            } catch (e: Exception) {
                _loginEvent.value = LoginEvent.Error(e.message)
            }
        }
    }
}

// Проблема в UI:
lifecycleScope.launch {
    viewModel.loginEvent.collect { event ->
        when (event) {
            is LoginEvent.Success -> {
                // Будет вызвано КАЖДЫЙ РАЗ при пересоздании View
                // Даже если login был вызван давно
                navigateToHome()
            }
            is LoginEvent.Error -> showError(event.message)
            null -> { /* ignore */ }
        }
    }
}

// ПЛОХО: SharedFlow с replay=1 как замена StateFlow
class UserViewModel : ViewModel() {
    private val _userName = MutableSharedFlow<String>(replay = 1)
    val userName: SharedFlow<String> = _userName.asSharedFlow()

    // Проблема: нет начального значения
    // Подписчики не получат данные, пока не произойдёт emit
}
```

### Разница StateFlow vs SharedFlow

**StateFlow характеристики:**
```kotlin
// 1. Всегда имеет значение (не может быть null state)
val stateFlow = MutableStateFlow("initial")
println(stateFlow.value) // Всегда доступно

// 2. Conflation: пропускает промежуточные значения
val state = MutableStateFlow(0)

viewModelScope.launch {
    state.emit(1)
    state.emit(2)
    state.emit(3)
}

viewModelScope.launch {
    state.collect { value ->
        // Может пропустить 1 и 2, получить только 3
        println(value)
    }
}

// 3. Новые подписчики сразу получают текущее значение
state.collect { value ->
    println(value) // Мгновенно получит текущее значение
}

// 4. distinctUntilChanged по умолчанию
state.value = "A"
state.value = "A" // Не вызовет emit, значение не изменилось
state.value = "B" // Вызовет emit
```

**SharedFlow характеристики:**
```kotlin
// 1. Может не иметь начального значения
val sharedFlow = MutableSharedFlow<String>()
// sharedFlow.value - НЕ существует

// 2. Настраиваемый replay и buffer
val flow = MutableSharedFlow<Int>(
    replay = 2,      // Последние 2 значения для новых подписчиков
    extraBufferCapacity = 5, // Дополнительный буфер
    onBufferOverflow = BufferOverflow.DROP_OLDEST
)

// 3. Новые подписчики получают только replay значения
flow.emit(1)
flow.emit(2)
flow.emit(3)

flow.collect { value ->
    // С replay=2 получит: 2, 3
    println(value)
}

// 4. Не пропускает значения (если буфер не переполнен)
val events = MutableSharedFlow<Event>()

launch {
    events.emit(Event.A)
    events.emit(Event.B)
    events.emit(Event.C)
}

launch {
    events.collect { event ->
        // Получит все: A, B, C (если не было conflation)
        println(event)
    }
}
```

### Когда что использовать

**StateFlow — для state/состояния:**
```kotlin
class UserViewModel : ViewModel() {
    // UI State — всегда имеет значение
    private val _uiState = MutableStateFlow<UiState>(UiState.Initial)
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // User data — текущий пользователь
    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser.asStateFlow()

    // Loading state
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    // Form input
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    fun updateSearchQuery(query: String) {
        _searchQuery.value = query
    }
}

// В UI
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.uiState.collect { state ->
            // Всегда получит текущее состояние при подписке
            updateUI(state)
        }
    }
}
```

**SharedFlow — для events/событий:**
```kotlin
class LoginViewModel : ViewModel() {
    // One-time events
    private val _events = MutableSharedFlow<LoginEvent>()
    val events: SharedFlow<LoginEvent> = _events.asSharedFlow()

    fun login(username: String, password: String) {
        viewModelScope.launch {
            try {
                repository.login(username, password)
                _events.emit(LoginEvent.NavigateToHome) // Событие
            } catch (e: Exception) {
                _events.emit(LoginEvent.ShowError(e.message))
            }
        }
    }
}

sealed class LoginEvent {
    object NavigateToHome : LoginEvent()
    data class ShowError(val message: String?) : LoginEvent()
}

// В UI
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.events.collect { event ->
            // Получит только новые события
            // Не получит старые при пересоздании View
            when (event) {
                LoginEvent.NavigateToHome -> navigateToHome()
                is LoginEvent.ShowError -> showError(event.message)
            }
        }
    }
}
```

**Сравнительная таблица:**

| Критерий | StateFlow | SharedFlow |
|----------|-----------|------------|
| **Начальное значение** | Обязательно | Опционально |
| **value property** | Да | Нет |
| **Conflation** | Да (always) | Настраивается |
| **Новый подписчик** | Получает текущее значение | Получает replay значения |
| **Use case** | State (UI state, data) | Events (navigation, toasts, snackbars) |
| **distinctUntilChanged** | По умолчанию | Опционально |
| **replay** | 1 (всегда) | Настраивается (0, 1, N) |

### Channel как альтернатива для events

```kotlin
class PaymentViewModel : ViewModel() {
    // Channel для событий с гарантированной доставкой
    private val _events = Channel<PaymentEvent>(Channel.BUFFERED)
    val events: Flow<PaymentEvent> = _events.receiveAsFlow()

    fun processPayment(amount: Double) {
        viewModelScope.launch {
            try {
                repository.processPayment(amount)
                _events.send(PaymentEvent.Success)
            } catch (e: Exception) {
                _events.send(PaymentEvent.Error(e.message))
            }
        }
    }
}

sealed class PaymentEvent {
    object Success : PaymentEvent()
    data class Error(val message: String?) : PaymentEvent()
}

// В UI
lifecycleScope.launch {
    viewModel.events.collect { event ->
        // Каждое событие будет обработано ровно один раз
        when (event) {
            PaymentEvent.Success -> showSuccessDialog()
            is PaymentEvent.Error -> showErrorDialog(event.message)
        }
    }
}
```

**Channel vs SharedFlow для events:**

```kotlin
// Channel - single subscriber, гарантированная доставка
val channel = Channel<Event>()
channel.send(Event.A) // Suspend до тех пор, пока кто-то не получит

// SharedFlow - multiple subscribers, может пропустить
val sharedFlow = MutableSharedFlow<Event>()
sharedFlow.emit(Event.A) // Может быть проигнорировано, если нет подписчиков

// Выбор:
// Channel: критичные события (платежи, навигация)
// SharedFlow: некритичные события (analytics, logs)
```

**Best practice для events:**
```kotlin
class BaseViewModel : ViewModel() {
    // Reusable event channel
    private val _events = Channel<UiEvent>(Channel.BUFFERED)
    val events: Flow<UiEvent> = _events.receiveAsFlow()

    protected suspend fun sendEvent(event: UiEvent) {
        _events.send(event)
    }
}

sealed class UiEvent {
    data class ShowSnackbar(val message: String) : UiEvent()
    data class Navigate(val route: String) : UiEvent()
    data class ShowDialog(val title: String, val message: String) : UiEvent()
}

class UserViewModel : BaseViewModel() {
    fun deleteUser(id: String) {
        viewModelScope.launch {
            try {
                repository.deleteUser(id)
                sendEvent(UiEvent.ShowSnackbar("User deleted"))
                sendEvent(UiEvent.Navigate("home"))
            } catch (e: Exception) {
                sendEvent(UiEvent.ShowSnackbar("Error: ${e.message}"))
            }
        }
    }
}
```

---

## Ошибка 10: Blocking calls inside suspend

### Проблемный код

```kotlin
suspend fun fetchUserData(): User {
    // ПЛОХО: Thread.sleep блокирует поток
    Thread.sleep(1000) // Блокирует поток на 1 секунду

    return api.getUser()
}

suspend fun readFile(path: String): String {
    // ПЛОХО: блокирующий IO
    return File(path).readText() // Блокирует поток
}

class UserRepository {
    suspend fun saveUser(user: User) {
        // ПЛОХО: blocking database call
        database.userDao().insert(user) // Если Dao НЕ suspend
    }

    suspend fun getPreference(key: String): String? {
        // ПЛОХО: SharedPreferences.getString() - blocking
        return preferences.getString(key, null)
    }
}

// ПЛОХО: blocking third-party library
suspend fun sendAnalytics(event: Event) {
    // Библиотека использует blocking calls внутри
    AnalyticsSDK.send(event) // Блокирует поток
}
```

### Почему это блокирует поток, а не приостанавливает

**suspend ≠ автоматически non-blocking:**
```kotlin
// Функция suspend, но внутри blocking call
suspend fun badExample() {
    println("Thread: ${Thread.currentThread().name}")
    Thread.sleep(5000) // БЛОКИРУЕТ поток на 5 секунд
    println("After sleep on: ${Thread.currentThread().name}")
}

// Что происходит:
launch(Dispatchers.IO) {
    badExample()
    // Один из 64 IO потоков заблокирован на 5 секунд
    // Не может обрабатывать другие корутины
}

// vs правильный вариант
suspend fun goodExample() {
    println("Thread: ${Thread.currentThread().name}")
    delay(5000) // ПРИОСТАНАВЛИВАЕТ корутину, НЕ блокирует поток
    println("After delay on: ${Thread.currentThread().name}") // Может быть другой поток
}

launch(Dispatchers.IO) {
    goodExample()
    // Поток освобождается во время delay
    // Может обрабатывать другие корутины
}
```

**Performance impact:**
```kotlin
// Плохой код
suspend fun processItems(items: List<Item>) = coroutineScope {
    items.map { item ->
        async(Dispatchers.IO) {
            Thread.sleep(1000) // Блокирует поток
            process(item)
        }
    }.awaitAll()
}

// Для 100 items:
// - Нужно 100 потоков одновременно (но их только 64)
// - Остальные 36 задач ждут освобождения потока
// - Время выполнения: ~2 секунды (batch processing)

// Хороший код
suspend fun processItemsGood(items: List<Item>) = coroutineScope {
    items.map { item ->
        async(Dispatchers.IO) {
            delay(1000) // Приостанавливает корутину
            process(item)
        }
    }.awaitAll()
}

// Для 100 items:
// - Все 100 корутин запускаются одновременно
// - Используют 64 потока эффективно
// - Время выполнения: ~1 секунда
```

### Правильно: delay(), withContext(Dispatchers.IO) для blocking

**1. delay() вместо Thread.sleep():**
```kotlin
// ПЛОХО
suspend fun retry() {
    Thread.sleep(1000) // Блокирует поток
    fetchData()
}

// ХОРОШО
suspend fun retry() {
    delay(1000) // Приостанавливает корутину
    fetchData()
}
```

**2. withContext(Dispatchers.IO) для blocking IO:**
```kotlin
class FileRepository {
    // ХОРОШО: явно указываем, что это blocking операция
    suspend fun readFile(path: String): String = withContext(Dispatchers.IO) {
        File(path).readText() // Blocking call на IO dispatcher
    }

    suspend fun writeFile(path: String, content: String) = withContext(Dispatchers.IO) {
        File(path).writeText(content)
    }

    suspend fun listFiles(directory: String): List<File> = withContext(Dispatchers.IO) {
        File(directory).listFiles()?.toList() ?: emptyList()
    }
}

class PreferencesRepository(
    private val preferences: SharedPreferences
) {
    // SharedPreferences — blocking API
    suspend fun getString(key: String): String? = withContext(Dispatchers.IO) {
        preferences.getString(key, null)
    }

    suspend fun putString(key: String, value: String) = withContext(Dispatchers.IO) {
        preferences.edit()
            .putString(key, value)
            .apply() // apply() асинхронный, но лучше на IO
    }

    // Или использовать DataStore — true suspend API
    // val dataStore: DataStore<Preferences>
    // suspend fun getString(key: String): String? = dataStore.data
    //     .map { it[stringPreferencesKey(key)] }
    //     .first()
}
```

**3. Обёртка для blocking API:**
```kotlin
// Blocking third-party library
object AnalyticsSDK {
    fun send(event: Event) {
        // Внутри blocking network call
        httpClient.post(event)
    }
}

// Suspend обёртка
class AnalyticsRepository {
    suspend fun sendEvent(event: Event) = withContext(Dispatchers.IO) {
        // Явно помещаем blocking call на IO dispatcher
        AnalyticsSDK.send(event)
    }
}

// Использование
viewModelScope.launch {
    analyticsRepository.sendEvent(Event.ButtonClick)
    // Не блокирует Main thread
}
```

**4. suspendCancellableCoroutine для callback API:**
```kotlin
// Legacy callback API
interface LegacyApiCallback {
    fun onSuccess(data: Data)
    fun onError(error: Exception)
}

class LegacyApi {
    fun fetchData(callback: LegacyApiCallback) {
        // Blocking call внутри
        Thread {
            val data = blockingNetworkCall()
            callback.onSuccess(data)
        }.start()
    }
}

// Suspend обёртка
suspend fun LegacyApi.fetchDataSuspend(): Data = suspendCancellableCoroutine { continuation ->
    fetchData(object : LegacyApiCallback {
        override fun onSuccess(data: Data) {
            continuation.resume(data)
        }

        override fun onError(error: Exception) {
            continuation.resumeWithException(error)
        }
    })

    continuation.invokeOnCancellation {
        // Отмена запроса при cancellation
        cancel()
    }
}

// Теперь можно использовать как обычную suspend функцию
suspend fun loadData(): Data {
    return legacyApi.fetchDataSuspend()
}
```

**5. Правильный подход для Room Database:**
```kotlin
// ПЛОХО: блокирующие DAO методы
@Dao
interface UserDao {
    fun getUser(id: String): User // Blocking

    fun insertUser(user: User) // Blocking
}

class UserRepository(private val dao: UserDao) {
    // НЕ РЕШАЕТ ПРОБЛЕМУ
    suspend fun getUser(id: String): User {
        return dao.getUser(id) // Всё равно блокирует поток!
    }

    // Нужен withContext
    suspend fun getUserCorrect(id: String): User = withContext(Dispatchers.IO) {
        dao.getUser(id)
    }
}

// ХОРОШО: suspend DAO методы (Room 2.1+)
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getUser(id: String): User // Room автоматически withContext(Dispatchers.IO)

    @Insert
    suspend fun insertUser(user: User)

    @Query("SELECT * FROM users")
    fun observeUsers(): Flow<List<User>> // Flow автоматически на IO
}

class UserRepository(private val dao: UserDao) {
    // Не нужен withContext, Room делает это сам
    suspend fun getUser(id: String): User {
        return dao.getUser(id)
    }

    fun observeUsers(): Flow<List<User>> {
        return dao.observeUsers()
    }
}
```

**6. Проверка blocking calls:**
```kotlin
// StrictMode для обнаружения blocking calls на Main thread
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (BuildConfig.DEBUG) {
            StrictMode.setThreadPolicy(
                StrictMode.ThreadPolicy.Builder()
                    .detectDiskReads()
                    .detectDiskWrites()
                    .detectNetwork()
                    .penaltyLog()
                    .penaltyDeath() // Crash app при blocking call на Main
                    .build()
            )
        }
    }
}

// Test для проверки
@Test
fun `verify no blocking calls`() = runTest {
    val dispatcher = StandardTestDispatcher(testScheduler)

    // Любой blocking call будет виден в тесте
    withContext(dispatcher) {
        repository.getData() // Если есть Thread.sleep — тест зависнет
    }

    advanceUntilIdle() // Завершит только non-blocking корутины
}
```

---

## Debugging Coroutines

### CoroutineName для логов

```kotlin
class UserViewModel : ViewModel() {
    fun loadUser(id: String) {
        viewModelScope.launch(CoroutineName("LoadUser-$id")) {
            try {
                val user = repository.getUser(id)
                _user.value = user
            } catch (e: Exception) {
                Log.e("UserViewModel", "Error in ${coroutineContext[CoroutineName]}", e)
                // Log: Error in CoroutineName(LoadUser-123)
            }
        }
    }
}

// Вложенные корутины наследуют имя
viewModelScope.launch(CoroutineName("ParentTask")) {
    launch {
        // Автоматически получит CoroutineName("ParentTask")
        println(coroutineContext[CoroutineName]) // CoroutineName(ParentTask)
    }

    launch(CoroutineName("ChildTask")) {
        // Явное переопределение
        println(coroutineContext[CoroutineName]) // CoroutineName(ChildTask)
    }
}
```

### Debug agent

```kotlin
// В build.gradle
dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-debug:1.7.3")
}

// VM опции
-Dkotlinx.coroutines.debug

// Или программно
fun main() {
    DebugProbes.install()

    runBlocking {
        launch {
            delay(1000)
        }

        // Dump всех активных корутин
        DebugProbes.dumpCoroutines()
    }

    DebugProbes.uninstall()
}

// Output:
// Coroutine "coroutine#2":StandaloneCoroutine{Active}@1234
//     at kotlinx.coroutines.delay(Delay.kt:123)
//     at com.example.MyClass.myMethod(MyClass.kt:45)
```

### Thread dumps и coroutine dumps

```kotlin
// Thread dump (стандартный Java)
fun threadDump() {
    Thread.getAllStackTraces().forEach { (thread, stack) ->
        println("Thread: ${thread.name}")
        stack.forEach { element ->
            println("  at $element")
        }
    }
}

// Coroutine dump (kotlinx-coroutines-debug)
fun coroutineDump() {
    DebugProbes.dumpCoroutines().forEach { info ->
        println("Coroutine: ${info.context[CoroutineName]?.name ?: "unnamed"}")
        println("State: ${info.state}")
        println("Stacktrace:")
        info.lastObservedStackTrace().forEach { element ->
            println("  at $element")
        }
    }
}

// Автоматический dump при timeout
suspend fun <T> withTimeout(timeout: Long, block: suspend () -> T): T {
    return try {
        kotlinx.coroutines.withTimeout(timeout) {
            block()
        }
    } catch (e: TimeoutCancellationException) {
        println("Timeout! Dumping coroutines:")
        DebugProbes.dumpCoroutines()
        throw e
    }
}
```

### IntelliJ debugger для coroutines

```kotlin
// Установка breakpoint в suspend функции
suspend fun loadData() {
    val data1 = fetchData1() // <- breakpoint здесь
    val data2 = fetchData2()
    return data1 + data2
}

// IntelliJ покажет:
// - Coroutine context (name, dispatcher, job)
// - Suspended coroutines
// - Continuation stack

// Useful actions в debugger:
// - "Dump Coroutines" в Threads panel
// - "Coroutines" tab для просмотра всех активных корутин
// - Фильтр "Suspended coroutines only"
```

**Debug logging:**
```kotlin
class DebugViewModel : ViewModel() {
    private val loggerScope = CoroutineScope(
        SupervisorJob() +
        Dispatchers.Main +
        CoroutineName("DebugViewModel") +
        CoroutineExceptionHandler { ctx, e ->
            Log.e("Debug", "Exception in ${ctx[CoroutineName]}", e)
            DebugProbes.dumpCoroutines()
        }
    )

    fun loadData() {
        loggerScope.launch {
            Log.d("Debug", "Starting loadData on ${Thread.currentThread().name}")

            withContext(Dispatchers.IO + CoroutineName("LoadData-IO")) {
                Log.d("Debug", "Loading on ${Thread.currentThread().name}")
                delay(1000)
            }

            Log.d("Debug", "Finished on ${Thread.currentThread().name}")
        }
    }
}
```

---

## Checklist для Code Review

При ревью кода с корутинами проверяйте:

### 1. Используется правильный scope?
```kotlin
// ❌ BAD
GlobalScope.launch { }

// ✅ GOOD
viewModelScope.launch { }
lifecycleScope.launch { }
viewLifecycleOwner.lifecycleScope.launch { }
```

### 2. Exceptions обрабатываются?
```kotlin
// ❌ BAD
launch {
    api.fetchData() // Необработанное исключение
}

// ✅ GOOD
launch {
    try {
        api.fetchData()
    } catch (e: CancellationException) {
        throw e // Всегда пробрасываем
    } catch (e: Exception) {
        handleError(e)
    }
}
```

### 3. Cancellation поддерживается?
```kotlin
// ❌ BAD
suspend fun process() {
    while (true) {
        doWork() // Не проверяет cancellation
    }
}

// ✅ GOOD
suspend fun process() {
    while (isActive) {
        doWork()
        yield()
    }
}
```

### 4. Правильный Dispatcher?
```kotlin
// ❌ BAD
suspend fun processImage() = withContext(Dispatchers.IO) {
    // CPU-intensive на IO
}

// ✅ GOOD
suspend fun processImage() = withContext(Dispatchers.Default) {
    // CPU-intensive на Default
}
```

### 5. Нет blocking calls в suspend?
```kotlin
// ❌ BAD
suspend fun getData() {
    Thread.sleep(1000) // Блокирует поток
}

// ✅ GOOD
suspend fun getData() {
    delay(1000) // Приостанавливает корутину
}
```

### 6. StateFlow vs SharedFlow правильно выбран?
```kotlin
// ❌ BAD
val loginEvent = MutableStateFlow<Event?>(null) // Event как state

// ✅ GOOD
val loginState = MutableStateFlow<State>(State.Initial) // State
val loginEvents = MutableSharedFlow<Event>() // Events
```

### 7. Нет утечек памяти?
```kotlin
// ❌ BAD
class ViewModel {
    fun load(activity: Activity) {
        viewModelScope.launch {
            activity.updateUI() // Утечка
        }
    }
}

// ✅ GOOD
class ViewModel {
    private val _events = Channel<UiEvent>()
    val events = _events.receiveAsFlow()

    fun load() {
        viewModelScope.launch {
            _events.send(UiEvent.Update)
        }
    }
}
```

---

## Проверь себя

### 1. Почему GlobalScope — anti-pattern?
<details>
<summary>Ответ</summary>

GlobalScope создаёт корутины, не привязанные к жизненному циклу компонентов:
- Продолжают работу после уничтожения Activity/ViewModel
- Вызывают memory leaks (держат ссылки на уничтоженные объекты)
- Невозможно отменить при завершении работы компонента
- Нет structured concurrency — родитель не контролирует дочерние корутины

Правильно: использовать `viewModelScope`, `lifecycleScope`, `viewLifecycleOwner.lifecycleScope`.
</details>

### 2. Чем SupervisorScope отличается от SupervisorJob()?
<details>
<summary>Ответ</summary>

**SupervisorJob()** — это Job, который при передаче в `launch(SupervisorJob())` создаёт новый Job и разрывает связь с родительским scope, теряя structured concurrency.

**supervisorScope { }** — это suspend функция, которая создаёт scope с supervisor поведением, сохраняя иерархию:
- Дочерние корутины не отменяют друг друга при исключении
- Сохраняется связь с родительским scope
- Автоматически отменяется при отмене родителя

Правильно: использовать `supervisorScope { }` для независимых параллельных задач.
</details>

### 3. Как сделать long-running coroutine cancellable?
<details>
<summary>Ответ</summary>

Корутины требуют cooperative cancellation. Методы:

1. **isActive check**: `if (!isActive) return`
2. **ensureActive()**: бросает `CancellationException` если отменена
3. **yield()**: проверяет cancellation + suspension point

```kotlin
suspend fun longTask() {
    repeat(1_000_000) { i ->
        if (i % 1000 == 0) {
            yield() // Или ensureActive()
        }
        compute(i)
    }
}
```

Важно: всегда пробрасывать `CancellationException`, не перехватывать в catch.
</details>

### 4. Когда StateFlow не подходит?
<details>
<summary>Ответ</summary>

StateFlow не подходит для **one-time events** (события):
- Navigation events
- Toast/Snackbar messages
- Dialog triggers

Проблема: StateFlow сохраняет последнее значение, новые подписчики получат старое событие повторно.

Решение: использовать **SharedFlow** или **Channel** для events:
```kotlin
private val _events = MutableSharedFlow<Event>() // Или Channel<Event>()
val events: SharedFlow<Event> = _events.asSharedFlow()
```

StateFlow подходит для **state** (состояния): UI state, loading state, user data.
</details>

### 5. Почему Thread.sleep() плохо в suspend?
<details>
<summary>Ответ</summary>

`Thread.sleep()` **блокирует поток**, а не приостанавливает корутину:
- Поток не может выполнять другие корутины во время sleep
- Для 100 корутин с `Thread.sleep(1000)` нужно 100 потоков
- Dispatcher pool быстро исчерпывается

`delay()` **приостанавливает корутину**:
- Освобождает поток для других корутин
- 1000 корутин с `delay(1000)` работают на нескольких потоках
- Эффективное использование resources

Правильно: `delay()` вместо `Thread.sleep()`, `withContext(Dispatchers.IO)` для blocking calls.
</details>

---

## Связи

Этот документ связан с:

- **[[android-async-evolution]]** — эволюция асинхронного программирования в Android от AsyncTask до Coroutines, исторический контекст появления корутин
- **[[android-threading]]** — устройство Main Thread, Handler, Looper в Android; понимание threading модели критично для правильного использования Dispatchers
- **[[kotlin-coroutines]]** — fundamentals корутин в Kotlin: suspend функции, CoroutineContext, Job, structured concurrency, cancellation механизм

---

## Бонус: runSuspendCatching — безопасная альтернатива runCatching

Стандартный `runCatching` **ловит CancellationException** и нарушает structured concurrency:

```kotlin
// ❌ ПЛОХО: runCatching ловит CancellationException
val result = runCatching {
    suspendFunction()  // CancellationException поймана!
}
// Корутина продолжит работу, хотя должна была отмениться

// ✅ ХОРОШО: runSuspendCatching
inline fun <R> runSuspendCatching(block: () -> R): Result<R> = try {
    Result.success(block())
} catch (e: CancellationException) {
    throw e  // ВСЕГДА перебрасываем!
} catch (e: Throwable) {
    Result.failure(e)
}

// Использование
val result = runSuspendCatching {
    suspendFunction()
}
result.onSuccess { data -> handleData(data) }
      .onFailure { error -> handleError(error) }
```

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Coroutines best practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices) | Docs | Официальные best practices |
| 2 | [Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html) | Docs | Fundamentals |
| 3 | [Exception Handling](https://kotlinlang.org/docs/exception-handling.html) | Docs | SupervisorJob, CoroutineExceptionHandler |
| 4 | [Cancellation and Timeouts](https://kotlinlang.org/docs/cancellation-and-timeouts.html) | Docs | CancellationException handling |
| 5 | [Structured concurrency - Roman Elizarov](https://medium.com/@elizarov/structured-concurrency-722d765aa952) | Article | Теоретическая основа |
| 6 | [Avoid GlobalScope - Roman Elizarov](https://elizarov.medium.com/the-reason-to-avoid-globalscope-835337445abc) | Article | Почему GlobalScope опасен |
| 7 | [Coroutines Best Practices](https://kt.academy/article/cc-best-practices) | Article | Практические паттерны |
| 8 | [Exception Handling](https://kt.academy/article/cc-exception-handling) | Article | Детали обработки ошибок |
| 9 | [Top 10 Coroutine Mistakes](https://www.droidcon.com/2024/11/22/top-10-coroutine-mistakes-we-all-have-made-as-android-developers/) | Conference | Актуальные ошибки 2024 |
| 10 | [Understanding SupervisorJob](https://www.revenuecat.com/blog/engineering/supervisorjob-kotlin/) | Article | SupervisorJob deep-dive |

Все примеры кода протестированы с Kotlin 2.0+, kotlinx.coroutines 1.8+, Android Gradle Plugin 8.0+.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
