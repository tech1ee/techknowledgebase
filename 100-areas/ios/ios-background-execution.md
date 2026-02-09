---
title: iOS Background Execution
created: 2026-01-11
tags: [ios, swift, background-tasks, app-lifecycle, performance]
related: "[[android-background-work]]"
---

## TL;DR

iOS строго ограничивает фоновое выполнение для экономии батареи. У вас есть ~30 секунд при уходе в фон через `beginBackgroundTask`, или специальные режимы (Background Modes) для долгих задач: фоновая загрузка, локация, аудио, VoIP. Для периодических задач используйте `BGTaskScheduler` с `BGAppRefreshTask` (короткие задачи) или `BGProcessingTask` (длинные задачи при зарядке). Система сама решает, когда запускать ваши задачи, учитывая активность пользователя и заряд батареи.

## Аналогии

**Жизненный цикл приложения** — как состояния работника в офисе:
- **Active** — активно работает за компьютером
- **Inactive** — на пути к кофемашине (переходное состояние)
- **Background** — работает из дома удаленно (ограниченное время)
- **Suspended** — ушел на обед, вся работа заморожена
- **Not Running** — еще не пришел на работу или уже ушел домой

**Background Task** — как попросить босса дать вам 30 секунд для завершения документа перед уходом домой. Если не успели — босс силой забирает документ.

**BGTaskScheduler** — как договоренность с уборщиками о периодической уборке офиса. Вы просите убирать каждый день, но они приходят когда им удобно (обычно ночью, когда никого нет).

## Диаграммы

### Состояния приложения

```
┌─────────────┐
│ Not Running │
└──────┬──────┘
       │ Launch app
       ▼
┌─────────────┐
│   Inactive  │◄───────────┐
└──────┬──────┘            │
       │ Become active     │ Interruption
       ▼                   │ (call, alert)
┌─────────────┐            │
│   Active    ├────────────┘
└──────┬──────┘
       │ Enter background
       ▼
┌─────────────┐
│ Background  │ (~30 sec or background mode)
└──────┬──────┘
       │ System suspends
       ▼
┌─────────────┐
│  Suspended  │
└──────┬──────┘
       │ System terminates or reactivate
       ▼
┌─────────────┐
│ Not Running │
└─────────────┘
```

### Background Task Execution Flow

```
User leaves app
       │
       ▼
┌──────────────────────┐
│ beginBackgroundTask  │
└──────────┬───────────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
    ┌──────────┐      ┌──────────────┐
    │ Execute  │      │  Start Timer │
    │   Task   │      │  (~30 sec)   │
    └─────┬────┘      └──────┬───────┘
          │                  │
          │                  ▼
          │           ┌──────────────┐
          │           │  Expiration  │
          │           │   Handler    │
          │           └──────┬───────┘
          │                  │
          ▼                  ▼
    ┌──────────────────────────┐
    │ endBackgroundTask        │
    └──────────────────────────┘
```

### BGTaskScheduler Flow

```
App registers tasks
       │
       ▼
┌──────────────────────┐
│ BGTaskScheduler      │
│ .register()          │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ App schedules task   │
│ .submit()            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ System decides when  │
│ to execute (async)   │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│ Task launch handler  │
│ called in background │
└──────────┬───────────┘
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
    ┌──────────┐      ┌──────────────┐
    │ Execute  │      │  Expiration  │
    │   Work   │      │   Handler    │
    └─────┬────┘      └──────┬───────┘
          │                  │
          ▼                  ▼
    ┌──────────────────────────┐
    │ task.setTaskCompleted()  │
    └──────────────────────────┘
```

## Состояния приложения

### Пять состояний жизненного цикла

```swift
import UIKit

class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        print("📱 State: Not Running -> Launching")
        // Приложение запускается
        return true
    }

    func applicationWillResignActive(_ application: UIApplication) {
        print("📱 State: Active -> Inactive")
        // Временное прерывание (звонок, уведомление)
        // Приостановите анимации, таймеры
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        print("📱 State: Inactive -> Background")
        // У вас есть ~5 секунд для подготовки к приостановке
        // Сохраните данные, освободите ресурсы
    }

    func applicationWillEnterForeground(_ application: UIApplication) {
        print("📱 State: Background -> Inactive")
        // Приложение возвращается на передний план
        // Восстановите UI, обновите данные
    }

    func applicationDidBecomeActive(_ application: UIApplication) {
        print("📱 State: Inactive -> Active")
        // Приложение активно и получает события
        // Возобновите анимации, таймеры
    }

    func applicationWillTerminate(_ application: UIApplication) {
        print("📱 State: Any -> Not Running")
        // Приложение завершается (редко вызывается)
        // Только если приложение не в Suspended
    }
}
```

### SwiftUI Scene Phase

```swift
import SwiftUI

@main
struct MyApp: App {
    @Environment(\.scenePhase) private var scenePhase

    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            switch newPhase {
            case .active:
                print("📱 App Active")
                // Обновите UI, возобновите задачи

            case .inactive:
                print("📱 App Inactive")
                // Временное прерывание

            case .background:
                print("📱 App Background")
                // Сохраните данные, начните фоновые задачи

            @unknown default:
                break
            }
        }
    }
}
```

## Background Execution Limits

### Стандартное ограничение: ~30 секунд

При переходе в фон iOS дает приложению несколько секунд (~5 сек) для завершения текущих операций. Если нужно больше времени, используйте `beginBackgroundTask`:

```swift
import UIKit

class BackgroundTaskManager {
    private var backgroundTask: UIBackgroundTaskIdentifier = .invalid

    func startLongRunningTask() {
        // Запрашиваем дополнительное время (~30 секунд)
        backgroundTask = UIApplication.shared.beginBackgroundTask { [weak self] in
            // ⚠️ ВАЖНО: Expiration handler вызывается, когда время истекает
            print("⏰ Background time expired!")
            self?.cleanup()
        }

        // Проверяем, что задача зарегистрирована
        guard backgroundTask != .invalid else {
            print("❌ Failed to start background task")
            return
        }

        // Выполняем работу
        performWork { [weak self] in
            self?.cleanup()
        }
    }

    private func performWork(completion: @escaping () -> Void) {
        DispatchQueue.global(qos: .background).async {
            // Ваша работа здесь (максимум ~30 секунд)
            print("🔧 Performing background work...")
            Thread.sleep(forTimeInterval: 5)
            print("✅ Work completed")

            DispatchQueue.main.async {
                completion()
            }
        }
    }

    private func cleanup() {
        guard backgroundTask != .invalid else { return }

        print("🧹 Cleaning up background task")
        UIApplication.shared.endBackgroundTask(backgroundTask)
        backgroundTask = .invalid
    }

    // Проверка оставшегося времени
    func checkRemainingTime() {
        let remaining = UIApplication.shared.backgroundTimeRemaining
        if remaining == .infinity {
            print("⏱️ App is in foreground (infinite time)")
        } else {
            print("⏱️ Remaining background time: \(remaining) seconds")
        }
    }
}
```

### Практический пример: загрузка данных перед suspend

```swift
import UIKit

class DataSyncManager {
    private var backgroundTask: UIBackgroundTaskIdentifier = .invalid

    func syncDataBeforeBackground() {
        backgroundTask = UIApplication.shared.beginBackgroundTask(withName: "DataSync") {
            // Время истекло - останавливаем синхронизацию
            print("⏰ Sync time expired, cancelling...")
            self.cancelSync()
            self.endBackgroundTask()
        }

        Task {
            do {
                print("🔄 Starting data sync...")
                try await syncWithServer()
                print("✅ Sync completed successfully")
            } catch {
                print("❌ Sync failed: \(error)")
            }

            endBackgroundTask()
        }
    }

    private func syncWithServer() async throws {
        // Симуляция сетевого запроса
        try await Task.sleep(for: .seconds(10))
        // Сохранение данных
        saveToDatabase()
    }

    private func cancelSync() {
        // Отмените незавершенные операции
        // Сохраните прогресс для следующей попытки
    }

    private func saveToDatabase() {
        print("💾 Saving to database...")
    }

    private func endBackgroundTask() {
        guard backgroundTask != .invalid else { return }
        UIApplication.shared.endBackgroundTask(backgroundTask)
        backgroundTask = .invalid
    }
}

// Использование в SceneDelegate
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    let syncManager = DataSyncManager()

    func sceneDidEnterBackground(_ scene: UIScene) {
        syncManager.syncDataBeforeBackground()
    }
}
```

## Background Modes в Info.plist

### Включение Background Modes

В Xcode: Target → Signing & Capabilities → + Capability → Background Modes

Или добавьте в `Info.plist`:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>
    <string>processing</string>
    <string>remote-notification</string>
    <string>location</string>
    <string>audio</string>
    <string>voip</string>
    <string>external-accessory</string>
    <string>bluetooth-central</string>
    <string>bluetooth-peripheral</string>
</array>
```

### Доступные режимы

| Режим | Описание | Когда использовать |
|-------|----------|-------------------|
| `fetch` | Background fetch | Периодическое обновление контента |
| `processing` | Background processing | Длительные задачи (ML, индексация) |
| `remote-notification` | Silent push | Обновление данных по push |
| `location` | Location updates | Навигация, трекинг |
| `audio` | Audio playback | Музыкальные плееры |
| `voip` | VoIP calls | Мессенджеры с звонками |
| `external-accessory` | External accessories | Работа с MFi устройствами |
| `bluetooth-central` | Bluetooth LE | Фитнес-трекеры, IoT |

## BackgroundTasks Framework

### Регистрация задач

```swift
import UIKit
import BackgroundTasks

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    // Идентификаторы задач (должны быть в Info.plist)
    static let appRefreshTaskID = "com.yourapp.refresh"
    static let databaseCleaningTaskID = "com.yourapp.db-cleaning"

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        // Регистрируем обработчики задач
        registerBackgroundTasks()

        return true
    }

    private func registerBackgroundTasks() {
        // BGAppRefreshTask: короткие задачи (~30 секунд)
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.appRefreshTaskID,
            using: nil // nil = main queue
        ) { task in
            self.handleAppRefresh(task: task as! BGAppRefreshTask)
        }

        // BGProcessingTask: длинные задачи (минуты, при зарядке)
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: Self.databaseCleaningTaskID,
            using: DispatchQueue.global()
        ) { task in
            self.handleDatabaseCleaning(task: task as! BGProcessingTask)
        }

        print("✅ Background tasks registered")
    }

    func applicationDidEnterBackground(_ application: UIApplication) {
        // Планируем задачи при уходе в фон
        scheduleAppRefresh()
        scheduleDatabaseCleaning()
    }
}
```

### Info.plist конфигурация

```xml
<key>BGTaskSchedulerPermittedIdentifiers</key>
<array>
    <string>com.yourapp.refresh</string>
    <string>com.yourapp.db-cleaning</string>
</array>
```

### BGAppRefreshTask (короткие задачи)

```swift
import BackgroundTasks

extension AppDelegate {

    // Планирование задачи
    func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: Self.appRefreshTaskID)

        // Минимальное время до следующего запуска (не гарантировано!)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // 15 минут

        do {
            try BGTaskScheduler.shared.submit(request)
            print("📅 App refresh scheduled")
        } catch {
            print("❌ Could not schedule app refresh: \(error)")
        }
    }

    // Обработка задачи
    func handleAppRefresh(task: BGAppRefreshTask) {
        print("🔄 App refresh task started")

        // Планируем следующий запуск
        scheduleAppRefresh()

        // Устанавливаем expiration handler
        task.expirationHandler = {
            print("⏰ App refresh task expired")
            // Отмените операции
            task.setTaskCompleted(success: false)
        }

        // Выполняем работу (асинхронно)
        Task {
            do {
                try await fetchLatestData()
                print("✅ App refresh completed")
                task.setTaskCompleted(success: true)
            } catch {
                print("❌ App refresh failed: \(error)")
                task.setTaskCompleted(success: false)
            }
        }
    }

    private func fetchLatestData() async throws {
        // Загрузка данных с сервера
        let url = URL(string: "https://api.example.com/data")!
        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              httpResponse.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }

        // Обработка данных
        print("📦 Received \(data.count) bytes")
        // Сохраните в базу данных, обновите UI кэш и т.д.
    }
}
```

### BGProcessingTask (длинные задачи)

```swift
import BackgroundTasks

extension AppDelegate {

    // Планирование задачи обработки
    func scheduleDatabaseCleaning() {
        let request = BGProcessingTaskRequest(identifier: Self.databaseCleaningTaskID)

        // Минимальное время до запуска
        request.earliestBeginDate = Date(timeIntervalSinceNow: 60 * 60) // 1 час

        // Требуется подключение к питанию
        request.requiresNetworkConnectivity = false
        request.requiresExternalPower = true // Запускать только при зарядке

        do {
            try BGTaskScheduler.shared.submit(request)
            print("📅 Database cleaning scheduled")
        } catch {
            print("❌ Could not schedule database cleaning: \(error)")
        }
    }

    // Обработка задачи
    func handleDatabaseCleaning(task: BGProcessingTask) {
        print("🧹 Database cleaning task started")

        // Планируем следующий запуск
        scheduleDatabaseCleaning()

        // Создаем Operation для управления отменой
        let operation = DatabaseCleaningOperation()

        task.expirationHandler = {
            print("⏰ Database cleaning task expired")
            operation.cancel()
        }

        // Запускаем операцию
        let queue = OperationQueue()
        queue.maxConcurrentOperationCount = 1
        queue.addOperation(operation)

        // Ждем завершения
        operation.completionBlock = {
            task.setTaskCompleted(success: !operation.isCancelled)
        }
    }
}

// Операция для длительной обработки
class DatabaseCleaningOperation: Operation {
    override func main() {
        guard !isCancelled else { return }

        print("🗑️ Cleaning old database entries...")

        // Симуляция длительной работы с проверкой отмены
        for i in 1...100 {
            if isCancelled {
                print("⚠️ Cleaning cancelled at \(i)%")
                return
            }

            // Удаление старых записей
            Thread.sleep(forTimeInterval: 0.5)

            if i % 20 == 0 {
                print("📊 Progress: \(i)%")
            }
        }

        print("✅ Database cleaning completed")
    }
}
```

## Background Fetch

### Настройка (устаревший метод, используйте BGTaskScheduler)

```swift
import UIKit

class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        // Устаревший API (iOS 7-12)
        // Используйте BGTaskScheduler для iOS 13+
        UIApplication.shared.setMinimumBackgroundFetchInterval(
            UIApplication.backgroundFetchIntervalMinimum
        )

        return true
    }

    // Устаревший метод
    func application(
        _ application: UIApplication,
        performFetchWithCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
    ) {

        print("📥 Background fetch triggered")

        // Загрузка данных
        fetchNewData { newData in
            if newData {
                completionHandler(.newData)
            } else {
                completionHandler(.noData)
            }
        }
    }

    private func fetchNewData(completion: @escaping (Bool) -> Void) {
        // Загрузка данных...
        DispatchQueue.main.asyncAfter(deadline: .now() + 5) {
            completion(true)
        }
    }
}
```

## Silent Push Notifications

### Настройка APNs payload

```json
{
  "aps": {
    "content-available": 1,
    "sound": ""
  },
  "custom-data": {
    "sync-type": "messages",
    "timestamp": 1234567890
  }
}
```

### Обработка silent push

```swift
import UIKit
import UserNotifications

class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        // Регистрация для удаленных уведомлений
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }

        return true
    }

    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        print("📱 Device Token: \(token)")
        // Отправьте токен на ваш сервер
    }

    func application(
        _ application: UIApplication,
        didReceiveRemoteNotification userInfo: [AnyHashable: Any],
        fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
    ) {

        print("📨 Silent push received")
        print("📦 Payload: \(userInfo)")

        // Проверяем, что это silent notification
        if let aps = userInfo["aps"] as? [String: Any],
           aps["content-available"] as? Int == 1 {

            // Обрабатываем в фоне
            handleSilentPush(userInfo: userInfo) { success in
                completionHandler(success ? .newData : .failed)
            }
        } else {
            completionHandler(.noData)
        }
    }

    private func handleSilentPush(
        userInfo: [AnyHashable: Any],
        completion: @escaping (Bool) -> Void
    ) {
        // Извлекаем custom данные
        guard let customData = userInfo["custom-data"] as? [String: Any],
              let syncType = customData["sync-type"] as? String else {
            completion(false)
            return
        }

        print("🔄 Syncing: \(syncType)")

        // Выполняем синхронизацию
        Task {
            do {
                try await syncData(type: syncType)
                completion(true)
            } catch {
                print("❌ Sync failed: \(error)")
                completion(false)
            }
        }
    }

    private func syncData(type: String) async throws {
        // Загрузка данных с сервера
        try await Task.sleep(for: .seconds(3))
        print("✅ Synced: \(type)")
    }
}
```

## Background URLSession

### Создание background URLSession

```swift
import Foundation

class BackgroundDownloadManager: NSObject {
    static let shared = BackgroundDownloadManager()

    private var session: URLSession!
    private var completionHandlers: [String: () -> Void] = [:]

    private override init() {
        super.init()

        // Создаем background URLSession
        let config = URLSessionConfiguration.background(
            withIdentifier: "com.yourapp.background-download"
        )

        // Настройки
        config.isDiscretionary = true // Система выбирает оптимальное время
        config.sessionSendsLaunchEvents = true // Запускать app при завершении

        session = URLSession(
            configuration: config,
            delegate: self,
            delegateQueue: nil
        )
    }

    // Начать загрузку
    func startDownload(url: URL) {
        let task = session.downloadTask(with: url)
        task.resume()
        print("⬇️ Download started: \(url.lastPathComponent)")
    }

    // Сохранить completion handler для AppDelegate
    func setCompletionHandler(_ handler: @escaping () -> Void, for identifier: String) {
        completionHandlers[identifier] = handler
    }
}

// MARK: - URLSessionDownloadDelegate
extension BackgroundDownloadManager: URLSessionDownloadDelegate {

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didFinishDownloadingTo location: URL
    ) {
        print("✅ Download completed: \(downloadTask.originalRequest?.url?.lastPathComponent ?? "")")

        // Перемещаем файл из временной локации
        let documentsPath = FileManager.default.urls(
            for: .documentDirectory,
            in: .userDomainMask
        ).first!

        let destinationURL = documentsPath.appendingPathComponent(
            downloadTask.originalRequest?.url?.lastPathComponent ?? "download"
        )

        do {
            // Удаляем старый файл если есть
            try? FileManager.default.removeItem(at: destinationURL)

            // Перемещаем новый файл
            try FileManager.default.moveItem(at: location, to: destinationURL)
            print("💾 File saved to: \(destinationURL.path)")

        } catch {
            print("❌ File move error: \(error)")
        }
    }

    func urlSession(
        _ session: URLSession,
        downloadTask: URLSessionDownloadTask,
        didWriteData bytesWritten: Int64,
        totalBytesWritten: Int64,
        totalBytesExpectedToWrite: Int64
    ) {
        let progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite) * 100
        print("📊 Progress: \(String(format: "%.1f", progress))%")
    }

    func urlSession(
        _ session: URLSession,
        task: URLSessionTask,
        didCompleteWithError error: Error?
    ) {
        if let error = error {
            print("❌ Download error: \(error.localizedDescription)")
        }

        // Вызываем completion handler
        if let identifier = session.configuration.identifier,
           let handler = completionHandlers[identifier] {
            handler()
            completionHandlers.removeValue(forKey: identifier)
        }
    }
}
```

### Интеграция в AppDelegate

```swift
import UIKit

class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        handleEventsForBackgroundURLSession identifier: String,
        completionHandler: @escaping () -> Void
    ) {
        print("🔄 Background URLSession event: \(identifier)")

        // Сохраняем completion handler
        BackgroundDownloadManager.shared.setCompletionHandler(
            completionHandler,
            for: identifier
        )
    }
}
```

### Использование

```swift
import SwiftUI

struct DownloadView: View {
    var body: some View {
        Button("Download Large File") {
            let url = URL(string: "https://example.com/large-file.zip")!
            BackgroundDownloadManager.shared.startDownload(url: url)
        }
    }
}
```

## Location Updates в фоне

### Настройка Location Background Mode

```swift
import CoreLocation
import UIKit

class LocationManager: NSObject, CLLocationManagerDelegate {
    static let shared = LocationManager()

    private let locationManager = CLLocationManager()

    private override init() {
        super.init()

        locationManager.delegate = self
        locationManager.desiredAccuracy = kCLLocationAccuracyBest

        // Для фоновых обновлений
        locationManager.allowsBackgroundLocationUpdates = true
        locationManager.pausesLocationUpdatesAutomatically = false
        locationManager.showsBackgroundLocationIndicator = true // iOS 11+
    }

    func requestPermissions() {
        // Запрашиваем разрешение Always для фоновой локации
        locationManager.requestAlwaysAuthorization()
    }

    func startTracking() {
        locationManager.startUpdatingLocation()
        print("📍 Location tracking started")
    }

    func stopTracking() {
        locationManager.stopUpdatingLocation()
        print("⏹️ Location tracking stopped")
    }

    // MARK: - CLLocationManagerDelegate

    func locationManager(
        _ manager: CLLocationManager,
        didUpdateLocations locations: [CLLocation]
    ) {
        guard let location = locations.last else { return }

        print("📍 Location: \(location.coordinate.latitude), \(location.coordinate.longitude)")
        print("📱 App state: \(UIApplication.shared.applicationState.description)")

        // Отправьте на сервер или сохраните локально
        saveLocation(location)
    }

    func locationManager(
        _ manager: CLLocationManager,
        didFailWithError error: Error
    ) {
        print("❌ Location error: \(error.localizedDescription)")
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        switch manager.authorizationStatus {
        case .authorizedAlways:
            print("✅ Location permission: Always")
            startTracking()
        case .authorizedWhenInUse:
            print("⚠️ Location permission: When In Use (no background)")
        case .denied, .restricted:
            print("❌ Location permission denied")
        case .notDetermined:
            print("⏳ Location permission not determined")
        @unknown default:
            break
        }
    }

    private func saveLocation(_ location: CLLocation) {
        // Сохранение в базу данных или отправка на сервер
    }
}

// Extension для читаемости состояния приложения
extension UIApplication.State: CustomStringConvertible {
    public var description: String {
        switch self {
        case .active: return "Active"
        case .inactive: return "Inactive"
        case .background: return "Background"
        @unknown default: return "Unknown"
        }
    }
}
```

### Info.plist для Location

```xml
<key>UIBackgroundModes</key>
<array>
    <string>location</string>
</array>

<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>Мы используем вашу локацию для отслеживания маршрута в фоновом режиме</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Мы используем вашу локацию для показа вашего текущего положения</string>

<key>NSLocationAlwaysUsageDescription</key>
<string>Мы используем вашу локацию даже когда приложение закрыто</string>
```

## Audio Background Mode

### Настройка аудио сессии

```swift
import AVFoundation
import UIKit

class AudioPlayer {
    static let shared = AudioPlayer()

    private var player: AVAudioPlayer?

    private init() {
        setupAudioSession()
    }

    private func setupAudioSession() {
        do {
            let session = AVAudioSession.sharedInstance()

            // Категория для воспроизведения в фоне
            try session.setCategory(
                .playback,
                mode: .default,
                options: [.mixWithOthers]
            )

            // Активируем сессию
            try session.setActive(true)

            print("✅ Audio session configured for background playback")

        } catch {
            print("❌ Audio session error: \(error)")
        }
    }

    func playAudio(url: URL) {
        do {
            player = try AVAudioPlayer(contentsOf: url)
            player?.prepareToPlay()
            player?.play()

            print("🎵 Audio playing")

            // Настраиваем Now Playing Info для Lock Screen
            setupNowPlaying(title: url.lastPathComponent)

        } catch {
            print("❌ Playback error: \(error)")
        }
    }

    func pause() {
        player?.pause()
        print("⏸️ Audio paused")
    }

    func resume() {
        player?.play()
        print("▶️ Audio resumed")
    }

    private func setupNowPlaying(title: String) {
        var nowPlayingInfo = [String: Any]()
        nowPlayingInfo[MPMediaItemPropertyTitle] = title
        nowPlayingInfo[MPMediaItemPropertyArtist] = "Your App"

        if let duration = player?.duration {
            nowPlayingInfo[MPMediaItemPropertyPlaybackDuration] = duration
            nowPlayingInfo[MPNowPlayingInfoPropertyElapsedPlaybackTime] = player?.currentTime ?? 0
        }

        nowPlayingInfo[MPNowPlayingInfoPropertyPlaybackRate] = 1.0

        MPNowPlayingInfoCenter.default().nowPlayingInfo = nowPlayingInfo

        // Настраиваем Remote Command Center
        setupRemoteCommands()
    }

    private func setupRemoteCommands() {
        let commandCenter = MPRemoteCommandCenter.shared()

        commandCenter.playCommand.addTarget { [weak self] _ in
            self?.resume()
            return .success
        }

        commandCenter.pauseCommand.addTarget { [weak self] _ in
            self?.pause()
            return .success
        }
    }
}
```

### Info.plist для Audio

```xml
<key>UIBackgroundModes</key>
<array>
    <string>audio</string>
</array>
```

## Энергоэффективность

### Рекомендации по оптимизации

```swift
import Foundation
import UIKit

class EnergyEfficientTaskManager {

    // ✅ Объединяйте сетевые запросы
    func fetchDataEfficiently() async throws {
        // Вместо нескольких маленьких запросов
        // делайте один большой запрос

        async let userData = fetchUserData()
        async let postsData = fetchPosts()
        async let commentsData = fetchComments()

        // Все запросы выполняются параллельно
        let (user, posts, comments) = try await (userData, postsData, commentsData)

        print("✅ Fetched all data in one batch")
    }

    // ✅ Используйте фоновые задачи для тяжелых операций
    func processingTaskExample() {
        let request = BGProcessingTaskRequest(identifier: "com.app.heavy-processing")
        request.requiresExternalPower = true // Только при зарядке
        request.requiresNetworkConnectivity = false

        try? BGTaskScheduler.shared.submit(request)
    }

    // ✅ Используйте дискретные URLSession для некритичных загрузок
    func discretionaryDownload(url: URL) {
        let config = URLSessionConfiguration.background(
            withIdentifier: "discretionary-download"
        )
        config.isDiscretionary = true // Система выбирает лучшее время
        config.sessionSendsLaunchEvents = true

        let session = URLSession(configuration: config)
        let task = session.downloadTask(with: url)
        task.resume()
    }

    // ✅ Проверяйте состояние батареи
    func checkBatteryState() -> Bool {
        UIDevice.current.isBatteryMonitoringEnabled = true

        let batteryLevel = UIDevice.current.batteryLevel
        let batteryState = UIDevice.current.batteryState

        // Выполняем тяжелые задачи только при хорошем заряде
        let isChargingOrFull = batteryState == .charging || batteryState == .full
        let hasEnoughBattery = batteryLevel > 0.2

        return isChargingOrFull || hasEnoughBattery
    }

    // ✅ Используйте дебаунсинг для частых событий
    private var searchWorkItem: DispatchWorkItem?

    func searchWithDebounce(_ query: String) {
        // Отменяем предыдущий поиск
        searchWorkItem?.cancel()

        let workItem = DispatchWorkItem { [weak self] in
            self?.performSearch(query)
        }

        searchWorkItem = workItem

        // Ждем 0.5 сек перед поиском
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5, execute: workItem)
    }

    private func performSearch(_ query: String) {
        print("🔍 Searching: \(query)")
    }

    private func fetchUserData() async throws -> String { "user" }
    private func fetchPosts() async throws -> String { "posts" }
    private func fetchComments() async throws -> String { "comments" }
}
```

### Energy Diagnostics в Xcode

```swift
// Используйте os_signpost для профилирования

import os.signpost

class PerformanceMonitor {
    private let log = OSLog(subsystem: "com.yourapp", category: "Performance")

    func measureBackgroundTask() {
        let signpostID = OSSignpostID(log: log)

        os_signpost(.begin, log: log, name: "Background Task", signpostID: signpostID)

        // Ваша работа
        performHeavyWork()

        os_signpost(.end, log: log, name: "Background Task", signpostID: signpostID)
    }

    private func performHeavyWork() {
        // Тяжелая работа...
    }
}

// Просматривайте результаты в Instruments → os_signpost
```

## Тестирование фоновых задач

### Симуляция BGTaskScheduler в Xcode

```bash
# Запустите симуляцию BGAppRefreshTask
e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"com.yourapp.refresh"]

# Запустите симуляцию BGProcessingTask
e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"com.yourapp.db-cleaning"]

# Симуляция истечения времени
e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateExpirationForTaskWithIdentifier:@"com.yourapp.refresh"]
```

### Схема для тестирования

В Xcode → Edit Scheme → Run → Options:
- Background Fetch: включить для симуляции
- Background Tasks: добавить идентификаторы задач

### Unit тесты для фоновых задач

```swift
import XCTest
import BackgroundTasks
@testable import YourApp

class BackgroundTaskTests: XCTestCase {

    func testAppRefreshTaskRegistration() {
        let expectation = XCTestExpectation(description: "Task registered")

        let taskID = "com.yourapp.test.refresh"

        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: taskID,
            using: nil
        ) { task in
            XCTAssertNotNil(task)
            expectation.fulfill()
            task.setTaskCompleted(success: true)
        }

        // Симулируем запуск задачи
        // (требует специальной настройки в тестовой схеме)

        wait(for: [expectation], timeout: 5.0)
    }

    func testBackgroundTimeRemaining() {
        let app = UIApplication.shared
        let remaining = app.backgroundTimeRemaining

        // В foreground должно быть infinity
        XCTAssertEqual(remaining, .infinity)
    }
}
```

## 6 типичных ошибок

### ❌ Ошибка 1: Забыли вызвать endBackgroundTask

```swift
// ❌ ПЛОХО: Background task никогда не завершается
func downloadData() {
    let taskID = UIApplication.shared.beginBackgroundTask {
        print("Time expired!")
    }

    URLSession.shared.dataTask(with: url) { data, response, error in
        // Обработка данных...
        // Забыли вызвать endBackgroundTask!
    }.resume()
}

// ✅ ХОРОШО: Всегда завершаем задачу
func downloadData() {
    var taskID: UIBackgroundTaskIdentifier = .invalid

    taskID = UIApplication.shared.beginBackgroundTask {
        print("Time expired!")
        if taskID != .invalid {
            UIApplication.shared.endBackgroundTask(taskID)
            taskID = .invalid
        }
    }

    URLSession.shared.dataTask(with: url) { data, response, error in
        // Обработка данных...

        // Всегда завершаем задачу
        if taskID != .invalid {
            UIApplication.shared.endBackgroundTask(taskID)
            taskID = .invalid
        }
    }.resume()
}
```

### ❌ Ошибка 2: Не обрабатываем expiration handler

```swift
// ❌ ПЛОХО: Expiration handler пустой
func handleAppRefresh(task: BGAppRefreshTask) {
    task.expirationHandler = {
        // Ничего не делаем - операции продолжат выполняться!
    }

    performLongRunningOperation {
        task.setTaskCompleted(success: true)
    }
}

// ✅ ХОРОШО: Отменяем операции при истечении времени
func handleAppRefresh(task: BGAppRefreshTask) {
    let operation = DataSyncOperation()

    task.expirationHandler = {
        // Отменяем незавершенные операции
        operation.cancel()
        task.setTaskCompleted(success: false)
    }

    let queue = OperationQueue()
    queue.addOperation(operation)

    operation.completionBlock = {
        task.setTaskCompleted(success: !operation.isCancelled)
    }
}
```

### ❌ Ошибка 3: Забыли добавить Background Modes в Info.plist

```swift
// ❌ ПЛОХО: Код есть, но Background Mode не включен
class LocationManager: NSObject {
    func startTracking() {
        locationManager.allowsBackgroundLocationUpdates = true // CRASH!
        locationManager.startUpdatingLocation()
    }
}
// Error: "location" не указан в UIBackgroundModes

// ✅ ХОРОШО: Добавили в Info.plist и проверяем
class LocationManager: NSObject {
    func startTracking() {
        // Проверяем, что Background Mode включен
        guard Bundle.main.object(forInfoDictionaryKey: "UIBackgroundModes") != nil else {
            print("❌ Location background mode not enabled!")
            return
        }

        locationManager.allowsBackgroundLocationUpdates = true
        locationManager.startUpdatingLocation()
    }
}

// Info.plist:
// <key>UIBackgroundModes</key>
// <array>
//     <string>location</string>
// </array>
```

### ❌ Ошибка 4: Не планируем следующую задачу

```swift
// ❌ ПЛОХО: Задача выполнится только один раз
func handleAppRefresh(task: BGAppRefreshTask) {
    task.expirationHandler = {
        task.setTaskCompleted(success: false)
    }

    performSync {
        task.setTaskCompleted(success: true)
        // Забыли запланировать следующий запуск!
    }
}

// ✅ ХОРОШО: Планируем следующий запуск в начале
func handleAppRefresh(task: BGAppRefreshTask) {
    // Сразу планируем следующий запуск
    scheduleNextAppRefresh()

    task.expirationHandler = {
        task.setTaskCompleted(success: false)
    }

    performSync {
        task.setTaskCompleted(success: true)
    }
}

func scheduleNextAppRefresh() {
    let request = BGAppRefreshTaskRequest(identifier: "com.app.refresh")
    request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60)

    try? BGTaskScheduler.shared.submit(request)
}
```

### ❌ Ошибка 5: Используем обычную URLSession вместо background

```swift
// ❌ ПЛОХО: Обычная сессия прервется при переходе в фон
func downloadLargeFile(url: URL) {
    let session = URLSession.shared // Прервется в фоне!

    session.downloadTask(with: url) { location, response, error in
        // Может не завершиться если app в фоне
    }.resume()
}

// ✅ ХОРОШО: Background URLSession продолжит работу
func downloadLargeFile(url: URL) {
    let config = URLSessionConfiguration.background(
        withIdentifier: "com.app.downloads"
    )
    let session = URLSession(
        configuration: config,
        delegate: self,
        delegateQueue: nil
    )

    let task = session.downloadTask(with: url)
    task.resume()

    // Загрузка продолжится даже если app будет убит!
}

// Обработка завершения в AppDelegate
func application(
    _ application: UIApplication,
    handleEventsForBackgroundURLSession identifier: String,
    completionHandler: @escaping () -> Void
) {
    // Система вызовет когда загрузка завершится
    print("Background download completed!")
    completionHandler()
}
```

### ❌ Ошибка 6: Не учитываем энергопотребление

```swift
// ❌ ПЛОХО: Частые обновления локации разряжают батарею
func startLocationTracking() {
    locationManager.desiredAccuracy = kCLLocationAccuracyBest
    locationManager.distanceFilter = kCLDistanceFilterNone // Каждое движение!
    locationManager.startUpdatingLocation()
    // Батарея разрядится за пару часов
}

// ✅ ХОРОШО: Оптимизируем точность и частоту
func startLocationTracking() {
    // Адаптируем точность под задачу
    locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters

    // Обновляем только при значительном изменении
    locationManager.distanceFilter = 100 // 100 метров

    // Разрешаем iOS приостанавливать обновления
    locationManager.pausesLocationUpdatesAutomatically = true

    // Используем significant location changes для еще большей экономии
    locationManager.startMonitoringSignificantLocationChanges()

    // Батарея прослужит весь день
}

// Или используйте отложенные обновления
func startDeferredLocationUpdates() {
    locationManager.allowDeferredLocationUpdates(
        untilTraveled: 1000, // 1 км
        timeout: 300 // 5 минут
    )
}
```

## Связанные заметки

- [[android-background-work]] — сравнение с WorkManager и JobScheduler на Android
- [[ios-app-lifecycle]] — жизненный цикл приложения iOS
- [[ios-urlsession]] — сетевые запросы и background sessions
- [[ios-core-location]] — работа с геолокацией
- [[ios-performance-optimization]] — оптимизация производительности
- [[ios-testing-strategies]] — тестирование асинхронных операций
- [[ios-app-store-guidelines]] — требования App Store к фоновым режимам

## Ресурсы

- [Apple Documentation: Background Execution](https://developer.apple.com/documentation/uikit/app_and_environment/scenes/preparing_your_ui_to_run_in_the_background)
- [WWDC 2019: Advances in App Background Execution](https://developer.apple.com/videos/play/wwdc2019/707/)
- [Energy Efficiency Guide for iOS Apps](https://developer.apple.com/library/archive/documentation/Performance/Conceptual/EnergyGuide-iOS/)
- [BGTaskScheduler Documentation](https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler)
