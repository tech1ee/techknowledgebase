---
title: "Cross-Platform: Background Work — BackgroundTasks vs WorkManager"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - background
  - backgroundtasks
  - workmanager
  - type/comparison
  - level/intermediate
reading_time: 44
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-lifecycle]]"
  - "[[cross-concurrency-modern]]"
related:
  - "[[android-background-work]]"
  - "[[ios-background-execution]]"
  - "[[concurrency-fundamentals]]"
---

# Cross-Platform: Background Work — BackgroundTasks vs WorkManager

## TL;DR

| Аспект | iOS (BackgroundTasks) | Android (WorkManager) |
|--------|----------------------|----------------------|
| **Гарантия выполнения** | Нет гарантий, система решает | Гарантированное выполнение |
| **Максимальное время** | ~30 секунд (processing: до 1-5 мин) | Без жёстких ограничений |
| **Контроль разработчика** | Минимальный | Полный |
| **Периодические задачи** | Минимум 15 минут, негарантированно | Минимум 15 минут, гарантированно |
| **Приоритет системы** | Батарея > приложение | Баланс батареи и функциональности |
| **Foreground режим** | Background Modes (ограниченные типы) | Foreground Service (любые задачи) |
| **Ретрай при ошибке** | Нет встроенного | Встроенные стратегии backoff |
| **Constraints** | Ограниченные (сеть, зарядка) | Богатые (сеть, батарея, storage, idle) |
| **Цепочки задач** | Нет | WorkManager chains |
| **Наблюдение за статусом** | Нет | LiveData/Flow |
| **Отладка** | Сложная (симуляция через Xcode) | Простая (adb команды) |
| **Jetsam/Kill** | Агрессивный | Умеренный |

---

## Философия платформ

### iOS: Батарея превыше всего

Apple придерживается агрессивной политики энергосбережения. Система jetsam может убить приложение в любой момент:

```
┌─────────────────────────────────────────────────────────┐
│                    iOS Memory Pressure                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Foreground App ─────────────────────────── Protected    │
│                                                          │
│  Background App (recent) ────────────────── Low Risk     │
│                                                          │
│  Background App (old) ───────────────────── Medium Risk  │
│                                                          │
│  Background App (no activity) ───────────── HIGH RISK    │
│                                                          │
│  Suspended App ──────────────────────────── KILLED FIRST │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**Jetsam приоритеты:**
- Foreground приложение почти никогда не убивается
- Background приложения убиваются без предупреждения
- Нет callback'а о завершении — просто SIGKILL

### Android: Гибкость с ответственностью

Android даёт больше свободы, но требует правильного использования:

```
┌─────────────────────────────────────────────────────────┐
│                 Android Process Priority                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Foreground Activity ────────────────────── Critical     │
│                                                          │
│  Foreground Service ─────────────────────── High         │
│                                                          │
│  Visible Activity ───────────────────────── High         │
│                                                          │
│  Service (started) ──────────────────────── Medium       │
│                                                          │
│  Cached (recent) ────────────────────────── Low          │
│                                                          │
│  Cached (old) ───────────────────────────── Lowest       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## BackgroundTasks Framework (iOS)

### Типы задач

```swift
// iOS: Регистрация background задач
import BackgroundTasks

class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        // 1. App Refresh Task — короткие задачи (~30 сек)
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.app.refresh",
            using: nil
        ) { task in
            self.handleAppRefresh(task: task as! BGAppRefreshTask)
        }

        // 2. Processing Task — длинные задачи (до нескольких минут)
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: "com.app.processing",
            using: nil
        ) { task in
            self.handleProcessing(task: task as! BGProcessingTask)
        }

        return true
    }

    // MARK: - App Refresh (короткие задачи)

    func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // Минимум 15 минут

        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Не удалось запланировать refresh: \(error)")
        }
    }

    func handleAppRefresh(task: BGAppRefreshTask) {
        // Планируем следующий refresh
        scheduleAppRefresh()

        // Создаём операцию
        let operation = RefreshOperation()

        // Обработка отмены системой
        task.expirationHandler = {
            operation.cancel()
        }

        operation.completionBlock = {
            task.setTaskCompleted(success: !operation.isCancelled)
        }

        OperationQueue.main.addOperation(operation)
    }

    // MARK: - Processing Task (длинные задачи)

    func scheduleProcessing() {
        let request = BGProcessingTaskRequest(identifier: "com.app.processing")
        request.requiresNetworkConnectivity = true
        request.requiresExternalPower = true // Увеличивает шансы выполнения

        do {
            try BGTaskScheduler.shared.submit(request)
        } catch {
            print("Не удалось запланировать processing: \(error)")
        }
    }

    func handleProcessing(task: BGProcessingTask) {
        let operation = SyncOperation()

        task.expirationHandler = {
            operation.cancel()
        }

        operation.completionBlock = {
            task.setTaskCompleted(success: !operation.isCancelled)
        }

        OperationQueue.main.addOperation(operation)
    }
}
```

### Info.plist конфигурация

```xml
<!-- iOS: Info.plist -->
<key>BGTaskSchedulerPermittedIdentifiers</key>
<array>
    <string>com.app.refresh</string>
    <string>com.app.processing</string>
</array>

<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>
    <string>processing</string>
</array>
```

---

## WorkManager (Android)

### Базовое использование

```kotlin
// Android: WorkManager — гарантированное выполнение
class SyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Получаем входные данные
            val userId = inputData.getString("user_id") ?: return Result.failure()

            // Выполняем синхронизацию
            val syncResult = syncRepository.sync(userId)

            // Возвращаем результат
            if (syncResult.isSuccess) {
                val outputData = workDataOf("synced_count" to syncResult.count)
                Result.success(outputData)
            } else {
                Result.retry() // Автоматический повтор с backoff
            }
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                Result.failure()
            }
        }
    }
}

// Планирование задачи
class SyncScheduler(private val context: Context) {

    private val workManager = WorkManager.getInstance(context)

    // Одноразовая задача
    fun scheduleOneTimeSync(userId: String) {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()

        val inputData = workDataOf("user_id" to userId)

        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(constraints)
            .setInputData(inputData)
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                WorkRequest.MIN_BACKOFF_MILLIS,
                TimeUnit.MILLISECONDS
            )
            .addTag("sync")
            .build()

        workManager.enqueueUniqueWork(
            "sync_$userId",
            ExistingWorkPolicy.REPLACE,
            request
        )
    }

    // Периодическая задача
    fun schedulePeriodicSync() {
        val constraints = Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // Только WiFi
            .setRequiresCharging(true)
            .build()

        val request = PeriodicWorkRequestBuilder<SyncWorker>(
            repeatInterval = 1,
            repeatIntervalTimeUnit = TimeUnit.HOURS,
            flexTimeInterval = 15,
            flexTimeIntervalUnit = TimeUnit.MINUTES
        )
            .setConstraints(constraints)
            .addTag("periodic_sync")
            .build()

        workManager.enqueueUniquePeriodicWork(
            "periodic_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            request
        )
    }

    // Наблюдение за статусом
    fun observeSyncStatus(userId: String): Flow<WorkInfo?> {
        return workManager
            .getWorkInfosForUniqueWorkFlow("sync_$userId")
            .map { it.firstOrNull() }
    }
}
```

### Цепочки задач

```kotlin
// Android: Цепочки задач (нет аналога в iOS)
fun scheduleComplexSync() {
    val download = OneTimeWorkRequestBuilder<DownloadWorker>().build()
    val process = OneTimeWorkRequestBuilder<ProcessWorker>().build()
    val upload = OneTimeWorkRequestBuilder<UploadWorker>().build()
    val cleanup = OneTimeWorkRequestBuilder<CleanupWorker>().build()

    workManager
        .beginWith(download)           // Сначала скачиваем
        .then(process)                 // Затем обрабатываем
        .then(upload)                  // Загружаем результат
        .then(cleanup)                 // Очищаем временные файлы
        .enqueue()
}

// Параллельное выполнение
fun scheduleParallelDownloads() {
    val download1 = OneTimeWorkRequestBuilder<DownloadWorker>()
        .setInputData(workDataOf("url" to "https://example.com/file1"))
        .build()

    val download2 = OneTimeWorkRequestBuilder<DownloadWorker>()
        .setInputData(workDataOf("url" to "https://example.com/file2"))
        .build()

    val merge = OneTimeWorkRequestBuilder<MergeWorker>().build()

    workManager
        .beginWith(listOf(download1, download2)) // Параллельно
        .then(merge)                              // Затем объединяем
        .enqueue()
}
```

---

## Foreground Service vs Background Modes

### iOS Background Modes

```swift
// iOS: Background Modes — ограниченные категории
// Доступные типы в Info.plist UIBackgroundModes:

/*
 audio          — воспроизведение аудио
 location       — обновления геолокации
 voip           — VoIP звонки
 fetch          — периодическое обновление контента
 remote-notification — обработка push уведомлений
 processing     — длительные задачи
 bluetooth-central    — работа с BLE устройствами
 bluetooth-peripheral — BLE peripheral mode
*/

// Пример: Location updates в background
class LocationManager: NSObject, CLLocationManagerDelegate {

    private let manager = CLLocationManager()

    func startBackgroundLocationUpdates() {
        manager.delegate = self
        manager.requestAlwaysAuthorization()
        manager.allowsBackgroundLocationUpdates = true
        manager.pausesLocationUpdatesAutomatically = false
        manager.desiredAccuracy = kCLLocationAccuracyBest
        manager.startUpdatingLocation()
    }

    func locationManager(
        _ manager: CLLocationManager,
        didUpdateLocations locations: [CLLocation]
    ) {
        guard let location = locations.last else { return }
        // Обработка локации в background
        processLocation(location)
    }
}

// Пример: Audio background mode
class AudioPlayer {

    private var audioPlayer: AVAudioPlayer?

    func setupBackgroundAudio() {
        do {
            try AVAudioSession.sharedInstance().setCategory(
                .playback,
                mode: .default,
                options: []
            )
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            print("Ошибка настройки аудио сессии: \(error)")
        }
    }
}
```

### Android Foreground Service

```kotlin
// Android: Foreground Service — любые длительные задачи
class SyncForegroundService : Service() {

    private val binder = LocalBinder()
    private var syncJob: Job? = null

    override fun onBind(intent: Intent?): IBinder = binder

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startSync()
            ACTION_STOP -> stopSync()
        }
        return START_STICKY
    }

    private fun startSync() {
        // Создаём notification для foreground service
        val notification = createNotification()

        // API 34+ требует указания типа
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        // Запускаем длительную операцию
        syncJob = CoroutineScope(Dispatchers.IO).launch {
            performLongRunningSync()
        }
    }

    private fun createNotification(): Notification {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Синхронизация",
            NotificationManager.IMPORTANCE_LOW
        )

        val notificationManager = getSystemService(NotificationManager::class.java)
        notificationManager.createNotificationChannel(channel)

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Синхронизация данных")
            .setContentText("Идёт синхронизация...")
            .setSmallIcon(R.drawable.ic_sync)
            .setOngoing(true)
            .addAction(
                R.drawable.ic_stop,
                "Остановить",
                createStopPendingIntent()
            )
            .build()
    }

    private suspend fun performLongRunningSync() {
        // Длительная операция без ограничений по времени
        for (i in 1..100) {
            if (!isActive) break

            syncBatch(i)
            updateNotificationProgress(i)

            delay(1000)
        }
        stopSelf()
    }

    private fun stopSync() {
        syncJob?.cancel()
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    companion object {
        const val ACTION_START = "START"
        const val ACTION_STOP = "STOP"
        const val NOTIFICATION_ID = 1
        const val CHANNEL_ID = "sync_channel"
    }

    inner class LocalBinder : Binder() {
        fun getService(): SyncForegroundService = this@SyncForegroundService
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />

<service
    android:name=".SyncForegroundService"
    android:foregroundServiceType="dataSync"
    android:exported="false" />
```

---

## Push Notification Triggered Work

### iOS: Notification Service Extension

```swift
// iOS: Обработка push в background
// NotificationServiceExtension — отдельный target

class NotificationService: UNNotificationServiceExtension {

    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttemptContent: UNMutableNotificationContent?

    // Максимум ~30 секунд на обработку
    override func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
    ) {
        self.contentHandler = contentHandler
        bestAttemptContent = (request.content.mutableCopy() as? UNMutableNotificationContent)

        guard let bestAttemptContent = bestAttemptContent else {
            contentHandler(request.content)
            return
        }

        // Скачиваем дополнительный контент
        Task {
            do {
                let imageUrl = bestAttemptContent.userInfo["image_url"] as? String
                if let urlString = imageUrl, let url = URL(string: urlString) {
                    let attachment = try await downloadAttachment(from: url)
                    bestAttemptContent.attachments = [attachment]
                }

                contentHandler(bestAttemptContent)
            } catch {
                contentHandler(bestAttemptContent)
            }
        }
    }

    // Вызывается если время истекло
    override func serviceExtensionTimeWillExpire() {
        if let contentHandler = contentHandler,
           let bestAttemptContent = bestAttemptContent {
            contentHandler(bestAttemptContent)
        }
    }

    private func downloadAttachment(from url: URL) async throws -> UNNotificationAttachment {
        let (data, _) = try await URLSession.shared.data(from: url)

        let tempDir = FileManager.default.temporaryDirectory
        let fileUrl = tempDir.appendingPathComponent(UUID().uuidString + ".jpg")
        try data.write(to: fileUrl)

        return try UNNotificationAttachment(identifier: "image", url: fileUrl, options: nil)
    }
}

// Background push для silent обновлений
// AppDelegate
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
    fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
) {
    // Максимум ~30 секунд
    Task {
        do {
            let result = try await processBackgroundNotification(userInfo)
            completionHandler(result ? .newData : .noData)
        } catch {
            completionHandler(.failed)
        }
    }
}
```

### Android: FCM с WorkManager

```kotlin
// Android: FCM + WorkManager для надёжной обработки
class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        // Для надёжного выполнения — используем WorkManager
        remoteMessage.data["sync_id"]?.let { syncId ->
            scheduleSyncWork(syncId)
        }

        // Показываем notification если есть
        remoteMessage.notification?.let { notification ->
            showNotification(notification)
        }
    }

    private fun scheduleSyncWork(syncId: String) {
        val request = OneTimeWorkRequestBuilder<PushSyncWorker>()
            .setInputData(workDataOf("sync_id" to syncId))
            .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
            .build()

        WorkManager.getInstance(applicationContext)
            .enqueueUniqueWork(
                "push_sync_$syncId",
                ExistingWorkPolicy.REPLACE,
                request
            )
    }
}

// Worker для обработки push
class PushSyncWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val syncId = inputData.getString("sync_id") ?: return Result.failure()

        return try {
            syncRepository.syncById(syncId)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }

    // Для expedited work
    override suspend fun getForegroundInfo(): ForegroundInfo {
        return ForegroundInfo(
            NOTIFICATION_ID,
            createNotification()
        )
    }
}
```

---

## 6 распространённых ошибок

### Ошибка 1: Ожидание гарантированного выполнения на iOS

```swift
// ❌ НЕПРАВИЛЬНО: Полагаться на background task для критичных данных
func scheduleImportantSync() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.sync")
    try? BGTaskScheduler.shared.submit(request)
    // Задача может НИКОГДА не выполниться!
}

// ✅ ПРАВИЛЬНО: Критичные данные — при активном использовании
func syncCriticalData() {
    // 1. Синхронизируем при каждом открытии приложения
    // 2. Background task — только для "nice to have" обновлений
    // 3. Push notifications для срочных обновлений
}
```

### Ошибка 2: Игнорирование expirationHandler на iOS

```swift
// ❌ НЕПРАВИЛЬНО: Нет обработки отмены
func handleTask(task: BGTask) {
    performLongOperation() // Система убьёт без предупреждения
    task.setTaskCompleted(success: true)
}

// ✅ ПРАВИЛЬНО: Graceful cancellation
func handleTask(task: BGTask) {
    let operation = CancellableOperation()

    task.expirationHandler = {
        operation.cancel()
        // Сохраняем промежуточное состояние!
        operation.saveProgress()
    }

    operation.completionBlock = {
        task.setTaskCompleted(success: !operation.isCancelled)
    }

    queue.addOperation(operation)
}
```

### Ошибка 3: Использование Service вместо WorkManager на Android

```kotlin
// ❌ НЕПРАВИЛЬНО: Обычный Service для background работы
class SyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Может быть убит системой в любой момент
        // Не переживёт Doze mode
        // Не восстановится после перезагрузки
        performSync()
        return START_STICKY
    }
}

// ✅ ПРАВИЛЬНО: WorkManager для надёжного выполнения
val request = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(constraints)
    .build()
WorkManager.getInstance(context).enqueue(request)
```

### Ошибка 4: Неправильный foreground service type на Android 14+

```kotlin
// ❌ НЕПРАВИЛЬНО: Нет указания типа
startForeground(NOTIFICATION_ID, notification)
// Краш на Android 14+!

// ✅ ПРАВИЛЬНО: Указываем тип
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
    startForeground(
        NOTIFICATION_ID,
        notification,
        ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
    )
} else {
    startForeground(NOTIFICATION_ID, notification)
}
```

### Ошибка 5: Игнорирование Battery Optimization на Android

```kotlin
// ❌ НЕПРАВИЛЬНО: Полагаться на точное время
val request = PeriodicWorkRequestBuilder<SyncWorker>(15, TimeUnit.MINUTES)
    .build()
// С включённой оптимизацией батареи задачи могут откладываться на часы!

// ✅ ПРАВИЛЬНО: Использовать constraints и учитывать задержки
val request = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 1,
    repeatIntervalTimeUnit = TimeUnit.HOURS
)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

// + Показать пользователю как отключить оптимизацию для критичных случаев
fun requestBatteryOptimizationExemption(context: Context) {
    val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
        data = Uri.parse("package:${context.packageName}")
    }
    context.startActivity(intent)
}
```

### Ошибка 6: Неправильная отладка background задач

```swift
// iOS: Симуляция background task в Xcode
// В консоли LLDB:
// e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"com.app.refresh"]

// Или через Xcode:
// Debug -> Simulate Background Fetch
```

```kotlin
// Android: Команды adb для отладки WorkManager
// Запустить задачу немедленно:
// adb shell cmd jobscheduler run -f com.app.package JOB_ID

// Посмотреть запланированные задачи:
// adb shell dumpsys jobscheduler | grep com.app.package

// Симулировать Doze mode:
// adb shell dumpsys deviceidle force-idle
// adb shell dumpsys deviceidle unforce
```

---

## 3 Mental Models

### Mental Model 1: iOS как строгий родитель

```
┌─────────────────────────────────────────────────────────┐
│              iOS Background Model                        │
│                                                          │
│   ┌─────────────┐                                       │
│   │ Приложение  │ ──> "Можно поработать в background?"  │
│   └─────────────┘                                       │
│          │                                               │
│          ▼                                               │
│   ┌─────────────┐                                       │
│   │   Система   │ ──> "Посмотрим... может быть"        │
│   └─────────────┘                                       │
│          │                                               │
│          ▼                                               │
│   Факторы решения:                                       │
│   • Уровень заряда батареи                              │
│   • Подключено ли зарядное устройство                   │
│   • Паттерны использования приложения                   │
│   • Текущая нагрузка на систему                         │
│   • Настроение системы (шутка... или нет)               │
│                                                          │
│   Результат: ВОЗМОЖНО выполнит, КОГДА-НИБУДЬ            │
└─────────────────────────────────────────────────────────┘
```

**Мантра:** "Надейся на лучшее, готовься к худшему"

### Mental Model 2: Android как менеджер задач

```
┌─────────────────────────────────────────────────────────┐
│            Android WorkManager Model                     │
│                                                          │
│   ┌─────────────┐                                       │
│   │ Приложение  │ ──> Создаёт WorkRequest с constraints │
│   └─────────────┘                                       │
│          │                                               │
│          ▼                                               │
│   ┌─────────────┐                                       │
│   │ WorkManager │ ──> Сохраняет в SQLite базу          │
│   └─────────────┘                                       │
│          │                                               │
│          ▼                                               │
│   ┌─────────────┐                                       │
│   │  Система    │ ──> Ждёт выполнения constraints       │
│   └─────────────┘                                       │
│          │                                               │
│          ▼                                               │
│   ГАРАНТИРОВАННО выполнит когда:                        │
│   • Constraints выполнены                               │
│   • (даже после перезагрузки устройства!)               │
│                                                          │
│   Результат: ОБЯЗАТЕЛЬНО выполнит при условиях          │
└─────────────────────────────────────────────────────────┘
```

**Мантра:** "Контракт есть контракт"

### Mental Model 3: Foreground как VIP-статус

```
┌─────────────────────────────────────────────────────────┐
│         Foreground Execution Priority                    │
│                                                          │
│  iOS Background Modes:          Android Foreground Svc:  │
│  ┌─────────────────┐           ┌─────────────────┐      │
│  │ Пропуск VIP     │           │ Пропуск VIP     │      │
│  │                 │           │                 │      │
│  │ Только для:     │           │ Для любых       │      │
│  │ • Audio         │           │ задач!          │      │
│  │ • Location      │           │                 │      │
│  │ • VoIP          │           │ Требования:     │      │
│  │ • BLE           │           │ • Notification  │      │
│  │                 │           │ • Service type  │      │
│  │ Нельзя:         │           │                 │      │
│  │ • Sync данных   │           │ Можно:          │      │
│  │ • Вычисления    │           │ • Что угодно    │      │
│  └─────────────────┘           └─────────────────┘      │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**iOS мантра:** "VIP только для избранных категорий"
**Android мантра:** "VIP за notification"

---

## 3 Quiz Questions

### Вопрос 1

Ваше iOS приложение должно синхронизировать данные каждые 30 минут. Вы используете `BGAppRefreshTask`. Пользователь жалуется, что синхронизация происходит раз в несколько часов или не происходит вовсе. В чём причина?

<details>
<summary>Ответ</summary>

**Причина:** iOS не гарантирует выполнение `BGAppRefreshTask`. Система самостоятельно решает когда и запускать ли задачу вообще, основываясь на:
- Паттернах использования приложения пользователем
- Уровне заряда батареи
- Подключении к зарядке
- Общей нагрузке на систему

**Решение:**
1. Использовать Push Notifications для критичных обновлений
2. Синхронизировать данные при каждом открытии приложения
3. Комбинировать Background Task с silent push
4. Если требуется точное время — использовать Background Location с `significantLocationChanges`

</details>

### Вопрос 2

На Android вы используете `WorkManager` с `PeriodicWorkRequest` каждые 15 минут. На устройстве Xiaomi задача выполняется раз в 2-3 часа. Почему и как исправить?

<details>
<summary>Ответ</summary>

**Причина:** Производители (Xiaomi, Huawei, Samsung) добавляют агрессивные оптимизации батареи поверх стандартного Android. Они могут:
- Убивать приложения в background
- Откладывать JobScheduler/WorkManager задачи
- Ограничивать сетевой доступ

**Решения:**
1. Попросить пользователя отключить оптимизацию батареи для приложения
2. Использовать `setExpedited()` для срочных задач
3. Использовать Foreground Service для критичных операций
4. Показать инструкции для конкретного производителя (dontkillmyapp.com)

```kotlin
// Запрос на исключение из оптимизации
val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
    data = Uri.parse("package:${context.packageName}")
}
startActivity(intent)
```

</details>

### Вопрос 3

Вы разрабатываете кросс-платформенное приложение для загрузки больших файлов (100+ МБ). Какую стратегию выбрать для каждой платформы?

<details>
<summary>Ответ</summary>

**iOS:**
```swift
// URLSession с background configuration
let config = URLSessionConfiguration.background(
    withIdentifier: "com.app.download"
)
config.isDiscretionary = false // Не откладывать
config.sessionSendsLaunchEvents = true // Запустить приложение по завершении

let session = URLSession(configuration: config, delegate: self, delegateQueue: nil)
let task = session.downloadTask(with: url)
task.resume()

// Обработка в AppDelegate
func application(
    _ application: UIApplication,
    handleEventsForBackgroundURLSession identifier: String,
    completionHandler: @escaping () -> Void
) {
    // Сохраняем completion handler
    backgroundCompletionHandler = completionHandler
}
```

**Android:**
```kotlin
// WorkManager + Foreground Service для прогресса
class DownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        setForeground(getForegroundInfo())

        val url = inputData.getString("url") ?: return Result.failure()
        return downloadFile(url)
    }

    override suspend fun getForegroundInfo(): ForegroundInfo {
        return ForegroundInfo(
            NOTIFICATION_ID,
            createProgressNotification(),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
        )
    }
}
```

**Ключевые отличия:**
- iOS: `URLSession` background configuration — система сама управляет загрузкой
- Android: `WorkManager` + `ForegroundService` для контроля и отображения прогресса
- iOS продолжит загрузку даже после kill приложения
- Android требует Foreground Service для надёжной длительной загрузки

</details>

---

## Связь с другими темами

[[android-background-work]] — Android предоставляет многоуровневую систему фоновой работы: WorkManager для отложенных задач с гарантией выполнения, Foreground Services для длительных операций с уведомлением пользователя, AlarmManager для точных таймеров. Заметка детально разбирает ограничения Android 12+ на фоновые запуски, типы Foreground Services в Android 14 и стратегии миграции с deprecated JobScheduler. Без этих знаний невозможно корректно портировать iOS background-логику на Android.

[[ios-background-execution]] — iOS имеет самую строгую модель фоновой работы среди мобильных платформ: BGTaskScheduler с ограничениями по времени (30 секунд для app refresh, несколько минут для processing), URLSession background transfers для загрузок и Silent Push для пробуждения приложения. Заметка объясняет, почему iOS убивает приложения агрессивнее Android и как проектировать задачи для работы в этих условиях. Понимание ограничений iOS критично для проектирования кросс-платформенной фоновой логики.

[[concurrency-fundamentals]] — Фоновая работа на обеих платформах опирается на фундаментальные концепции конкурентности: потоки, очереди, synchronization primitives. Заметка раскрывает теоретические основы — разницу между concurrency и parallelism, модели потоков (preemptive vs cooperative), механизмы синхронизации. Эти знания помогают понять, почему GCD и Dispatchers.IO работают именно так, и как избежать deadlock и race conditions в фоновых задачах.

---

## Источники и дальнейшее чтение

- Meier R. (2022). *Professional Android.* — Полное руководство по Android-разработке, включая WorkManager, Services и background execution limits. Подробно описывает Doze Mode, App Standby и стратегии надёжного выполнения фоновых задач.
- Neuburg M. (2023). *iOS Programming Fundamentals with Swift.* — Фундаментальная книга по iOS, включая главы о многопоточности, URLSession background configuration и BGTaskScheduler. Помогает понять системные ограничения iOS на фоновую работу.

---

## Проверь себя

> [!question]- Почему iOS агрессивнее Android ограничивает фоновую работу приложений? Какая философия стоит за этим?
> Apple приоритизирует battery life и user experience над convenience разработчика. iOS даёт приложению ~30 секунд на app refresh и несколько минут на processing task. Причина: неконтролируемая фоновая работа -- главная причина разряда батареи. Android исторически был более либеральным, но с каждой версией (Doze Mode API 23, App Standby API 23, Background Execution Limits API 26, Background Location Limits API 29) приближается к iOS-модели. Философия Apple: система управляет ресурсами, приложение адаптируется.

> [!question]- Сценарий: приложение должно синхронизировать данные каждые 15 минут, даже если пользователь его закрыл. Как реализовать на обеих платформах?
> Android: WorkManager с PeriodicWorkRequest (минимум 15 минут). WorkManager гарантирует выполнение даже после reboot (через JobScheduler/AlarmManager под капотом). Constraints: setRequiredNetworkType(CONNECTED). iOS: BGAppRefreshTaskRequest через BGTaskScheduler с earliestBeginDate. Но iOS НЕ гарантирует точный интервал -- система решает когда запустить, учитывая использование приложения, заряд батареи и сетевое подключение. Для надёжной синхронизации на iOS: дополнительно использовать Silent Push Notifications как trigger.

> [!question]- Почему WorkManager предпочтительнее Foreground Service для большинства фоновых задач на Android?
> WorkManager: система оптимизирует выполнение (батчит задачи, учитывает Doze Mode), задачи переживают process death и reboot, поддерживает constraints (сеть, зарядка), цепочки зависимых задач. Foreground Service: требует постоянное уведомление (раздражает пользователя), потребляет ресурсы непрерывно, с Android 12+ ограничен запуск из background. Foreground Service нужен только для задач, требующих непрерывного выполнения с обратной связью пользователю (навигация, воспроизведение музыки, запись).

> [!question]- Как URLSession background transfer на iOS отличается от аналога на Android?
> iOS URLSession с background configuration: система сама управляет загрузкой, продолжает после kill приложения, оптимизирует по сети/батарее, уведомляет через delegate при завершении (application:handleEventsForBackgroundURLSession:). На Android нет прямого аналога: DownloadManager предоставляет похожий функционал, но менее интегрирован. Обычно используют WorkManager + OkHttp для фоновых загрузок, но они не переживают force-stop без WorkManager persistence.

---

## Ключевые карточки

Чем BGTaskScheduler на iOS отличается от WorkManager на Android?
?
BGTaskScheduler: два типа задач (app refresh ~30 сек, processing ~несколько минут), система решает когда запускать (нет гарантии интервала), привязан к app lifecycle. WorkManager: гарантированное выполнение, constraints (сеть, зарядка), цепочки задач, periodic (мин 15 мин), переживает reboot. WorkManager более мощный и предсказуемый.

Какие ограничения Android накладывает на фоновую работу начиная с API 26+?
?
API 26 (Oreo): Background Execution Limits -- нельзя запускать services из background, implicit broadcasts ограничены. API 28: App Standby Buckets (Active/Working/Frequent/Rare) с разными лимитами. API 29: Background Location требует отдельного разрешения. API 31: Foreground Service launch restrictions из background. API 34: новые типы Foreground Service с обязательной декларацией.

Что такое Silent Push Notification и как используется для фоновой работы?
?
Silent Push (iOS: content-available, Android: data-only FCM) -- push уведомление без UI, которое пробуждает приложение для фоновой работы. iOS: ~30 секунд на обработку, система может throttle (не доставлять, если приложение не использовалось). Android: более надёжно, но Doze Mode может задержать доставку. Используется для trigger синхронизации данных.

Когда использовать Foreground Service на Android?
?
Только для задач, требующих непрерывного выполнения с осведомлением пользователя: воспроизведение медиа, навигация, запись, VoIP-звонки. Требует обязательное уведомление. С API 34: обязателен foregroundServiceType в manifest (mediaPlayback, location, dataSync и др.). Для отложенных/периодических задач -- всегда WorkManager.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-concurrency-modern]] | Async/await и корутины -- основа современной фоновой работы |
| Углубиться | [[android-background-work]] | Детальное погружение в WorkManager, Services, Doze Mode |
| Смежная тема | [[ios-background-execution]] | BGTaskScheduler и URLSession background из раздела iOS |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |
