---
title: "Уведомления в iOS: Push, Local, Live Activities"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/notifications
  - type/deep-dive
  - level/intermediate
related:
  - "[[ios-background-execution]]"
  - "[[ios-app-components]]"
  - "[[ios-networking]]"
  - "[[android-notifications]]"
---

# iOS Notifications

## TL;DR

iOS notifications system provides local and remote push notifications through UNUserNotificationCenter. Local notifications are scheduled by the app itself, while remote notifications arrive via Apple Push Notification service (APNs). Supports rich media, custom actions, notification extensions, and modern features like Live Activities and Dynamic Island integration.

## Аналогии

**UNUserNotificationCenter** - это как персональный секретарь, который управляет всеми напоминаниями и сообщениями. Вы даёте ему инструкции (местные уведомления) или он получает срочные сообщения извне (push-уведомления), и он решает, когда и как их показать.

**APNs (Apple Push Notification service)** - это как почтовая служба Apple. Ваш сервер отправляет письмо (notification) в почтовое отделение Apple, а Apple доставляет его на устройство пользователя. Вы не можете напрямую отправить письмо - всё идёт через Apple.

**Notification Extensions** - это как preview письма с возможностью открыть конверт и увидеть содержимое прямо в почтовом ящике, не заходя в сам дом (приложение). Service extension читает письмо первым и может его отредактировать, а content extension показывает красиво оформленный preview.

**Live Activities** - это как живое табло на стадионе, которое показывает счёт матча в реальном времени прямо на вашем локскрине и Dynamic Island, обновляясь без отправки десятков отдельных уведомлений.

## Архитектура системы уведомлений

```
┌─────────────────────────────────────────────────────────────────┐
│                          Your App                                │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Request Authorization                                      │ │
│  │  UNUserNotificationCenter.current()                        │ │
│  │    .requestAuthorization(options: [.alert, .sound])        │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              │                                    │
└──────────────────────────────┼────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│              UNUserNotificationCenter (iOS System)              │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────┐  │
│  │ Local Scheduler  │  │ Remote Handler   │  │ Authorization│  │
│  │ (Triggers)       │  │ (APNs)          │  │ Manager      │  │
│  └──────────────────┘  └──────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ Notification    │  │ Notification     │  │ App Delegate     │
│ Service Ext     │  │ Content Ext      │  │ Handler          │
│ (Modify)        │  │ (Rich UI)        │  │ (Action)         │
└─────────────────┘  └──────────────────┘  └──────────────────┘


Remote Push Flow:
┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│ Your Server  │───────▶│    APNs      │───────▶│ iOS Device   │
│              │  JWT   │   Gateway    │  Push  │              │
└──────────────┘        └──────────────┘        └──────────────┘
     │                                                   │
     │ 1. Generate device token                        │
     └───────────────────────────────────────────────────┘
```

## 1. Основы UNUserNotificationCenter

### Запрос разрешений

```swift
import UserNotifications

class NotificationManager {
    static let shared = NotificationManager()

    func requestAuthorization() async throws -> Bool {
        let center = UNUserNotificationCenter.current()

        // iOS 10+ authorization options
        let options: UNAuthorizationOptions = [
            .alert,      // Показ баннера/алерта
            .sound,      // Звук
            .badge,      // Бейдж на иконке
            .carPlay,    // CarPlay поддержка
            .provisional // Тихие уведомления (iOS 12+)
        ]

        return try await center.requestAuthorization(options: options)
    }

    // Проверка текущих настроек
    func checkAuthorizationStatus() async -> UNAuthorizationStatus {
        let settings = await UNUserNotificationCenter.current().notificationSettings()
        return settings.authorizationStatus
    }
}
```

### Настройки уведомлений

```swift
func checkNotificationSettings() async {
    let settings = await UNUserNotificationCenter.current().notificationSettings()

    print("Authorization status: \(settings.authorizationStatus.rawValue)")
    // .notDetermined = 0, .denied = 1, .authorized = 2, .provisional = 3

    print("Alert setting: \(settings.alertSetting.rawValue)")
    print("Badge setting: \(settings.badgeSetting.rawValue)")
    print("Sound setting: \(settings.soundSetting.rawValue)")
    print("Critical alert: \(settings.criticalAlertSetting.rawValue)")
    print("Time sensitive: \(settings.timeSensitiveSetting.rawValue)")
}
```

## 2. Локальные уведомления

### Создание и отправка

```swift
class LocalNotificationManager {

    // Простое уведомление
    func scheduleBasicNotification() async throws {
        let content = UNMutableNotificationContent()
        content.title = "Напоминание"
        content.subtitle = "Время встречи"
        content.body = "Встреча начнётся через 15 минут"
        content.sound = .default
        content.badge = 1

        // Триггер через 5 секунд
        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: 5,
            repeats: false
        )

        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }

    // Уведомление с календарным триггером
    func scheduleDailyReminder(hour: Int, minute: Int) async throws {
        let content = UNMutableNotificationContent()
        content.title = "Ежедневное напоминание"
        content.body = "Время выполнить задачу!"
        content.sound = .default

        var dateComponents = DateComponents()
        dateComponents.hour = hour
        dateComponents.minute = minute

        let trigger = UNCalendarNotificationTrigger(
            dateMatching: dateComponents,
            repeats: true
        )

        let request = UNNotificationRequest(
            identifier: "daily-reminder",
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }

    // Уведомление с location триггером
    func scheduleLocationNotification(latitude: Double, longitude: Double, radius: CLLocationDistance) async throws {
        let content = UNMutableNotificationContent()
        content.title = "Вы рядом!"
        content.body = "Вы находитесь рядом с выбранной локацией"
        content.sound = .default

        let center = CLLocationCoordinate2D(latitude: latitude, longitude: longitude)
        let region = CLCircularRegion(
            center: center,
            radius: radius,
            identifier: "location-reminder"
        )
        region.notifyOnEntry = true
        region.notifyOnExit = false

        let trigger = UNLocationNotificationTrigger(
            region: region,
            repeats: false
        )

        let request = UNNotificationRequest(
            identifier: "location-notification",
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }
}
```

### Управление уведомлениями

```swift
extension LocalNotificationManager {

    // Получить все запланированные уведомления
    func getPendingNotifications() async -> [UNNotificationRequest] {
        await UNUserNotificationCenter.current().pendingNotificationRequests()
    }

    // Получить доставленные уведомления
    func getDeliveredNotifications() async -> [UNNotification] {
        await UNUserNotificationCenter.current().deliveredNotifications()
    }

    // Удалить конкретные запланированные уведомления
    func removePendingNotifications(withIdentifiers identifiers: [String]) {
        UNUserNotificationCenter.current()
            .removePendingNotificationRequests(withIdentifiers: identifiers)
    }

    // Удалить все запланированные уведомления
    func removeAllPendingNotifications() {
        UNUserNotificationCenter.current().removeAllPendingNotificationRequests()
    }

    // Удалить доставленные уведомления
    func removeDeliveredNotifications(withIdentifiers identifiers: [String]) {
        UNUserNotificationCenter.current()
            .removeDeliveredNotifications(withIdentifiers: identifiers)
    }

    // Очистить badge
    func clearBadge() {
        Task { @MainActor in
            UIApplication.shared.applicationIconBadgeNumber = 0
        }
    }
}
```

## 3. Remote Push Notifications (APNs)

### Настройка APNs

#### Шаг 1: Apple Developer Portal

1. **Создать App ID** с Push Notifications capability
2. **Создать APNs Key** (рекомендуется) или **Certificate**:
   - Key: Certificates, Identifiers & Profiles → Keys → Create a key
   - Выбрать "Apple Push Notifications service (APNs)"
   - Скачать `.p8` файл (только один раз!)
   - Записать Key ID и Team ID

#### Шаг 2: Xcode Project Setup

```swift
// AppDelegate.swift
import UIKit
import UserNotifications

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        // Регистрация для remote notifications
        registerForRemoteNotifications()

        return true
    }

    func registerForRemoteNotifications() {
        Task {
            do {
                // Запрос разрешений
                let granted = try await UNUserNotificationCenter.current()
                    .requestAuthorization(options: [.alert, .sound, .badge])

                if granted {
                    await MainActor.run {
                        UIApplication.shared.registerForRemoteNotifications()
                    }
                }
            } catch {
                print("Failed to register: \(error)")
            }
        }
    }

    // Успешная регистрация - получаем device token
    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        print("Device Token: \(token)")

        // Отправить токен на ваш сервер
        sendTokenToServer(token)
    }

    // Ошибка регистрации
    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        print("Failed to register: \(error.localizedDescription)")
    }

    func sendTokenToServer(_ token: String) {
        // Отправить на backend
        Task {
            var request = URLRequest(url: URL(string: "https://yourserver.com/register")!)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")

            let body: [String: Any] = [
                "device_token": token,
                "platform": "ios",
                "bundle_id": Bundle.main.bundleIdentifier ?? ""
            ]

            request.httpBody = try? JSONSerialization.data(withJSONObject: body)

            let (_, response) = try await URLSession.shared.data(for: request)
            print("Token registered: \(response)")
        }
    }
}
```

### Server-side APNs Integration (Swift Vapor Example)

```swift
// Package.swift
dependencies: [
    .package(url: "https://github.com/vapor/vapor.git", from: "4.0.0"),
    .package(url: "https://github.com/vapor/apns.git", from: "4.0.0")
]

// configure.swift
import Vapor
import APNS

public func configure(_ app: Application) throws {

    // Конфигурация APNs с .p8 key
    let apnsConfig = APNSConfiguration(
        authenticationMethod: .jwt(
            key: .private(filePath: "/path/to/AuthKey_XXXXXXXXX.p8"),
            keyIdentifier: "XXXXXXXXX",  // Key ID из Apple Developer
            teamIdentifier: "XXXXXXXXX"  // Team ID
        ),
        topic: "com.yourcompany.yourapp", // Bundle ID
        environment: .sandbox // .production для прода
    )

    app.apns.configuration = apnsConfig

    // Routes
    try routes(app)
}

// Routes.swift
import Vapor
import APNS

func routes(_ app: Application) throws {

    // Endpoint для отправки push уведомления
    app.post("send-notification") { req async throws -> HTTPStatus in

        struct PushRequest: Content {
            let deviceToken: String
            let title: String
            let body: String
            let badge: Int?
            let data: [String: String]?
        }

        let pushRequest = try req.content.decode(PushRequest.self)

        // Создание payload
        let alert = APNSAlertNotification(
            alert: .init(
                title: .raw(pushRequest.title),
                subtitle: nil,
                body: .raw(pushRequest.body)
            ),
            expiration: .immediately,
            priority: .immediately,
            topic: "com.yourcompany.yourapp",
            sound: .default,
            badge: pushRequest.badge
        )

        // Отправка
        try await req.apns.send(
            alert,
            to: pushRequest.deviceToken
        )

        return .ok
    }

    // Массовая отправка
    app.post("send-bulk") { req async throws -> HTTPStatus in

        struct BulkRequest: Content {
            let deviceTokens: [String]
            let title: String
            let body: String
        }

        let bulkRequest = try req.content.decode(BulkRequest.self)

        try await withThrowingTaskGroup(of: Void.self) { group in
            for token in bulkRequest.deviceTokens {
                group.addTask {
                    let alert = APNSAlertNotification(
                        alert: .init(
                            title: .raw(bulkRequest.title),
                            body: .raw(bulkRequest.body)
                        ),
                        expiration: .immediately,
                        priority: .immediately,
                        topic: "com.yourcompany.yourapp"
                    )

                    try await req.apns.send(alert, to: token)
                }
            }

            try await group.waitForAll()
        }

        return .ok
    }
}
```

### APNs Payload Structure

```json
{
  "aps": {
    "alert": {
      "title": "Новое сообщение",
      "subtitle": "От Джона",
      "body": "Привет! Как дела?"
    },
    "badge": 1,
    "sound": "default",
    "category": "MESSAGE_CATEGORY",
    "thread-id": "chat-123",
    "mutable-content": 1,
    "content-available": 1,
    "interruption-level": "time-sensitive",
    "relevance-score": 0.8
  },
  "customData": {
    "userId": "12345",
    "chatId": "67890",
    "messageId": "msg-999"
  }
}
```

**Payload поля:**
- `alert` - текст уведомления
- `badge` - число на иконке приложения
- `sound` - звук ("default" или имя файла)
- `category` - identifier для действий
- `thread-id` - группировка уведомлений
- `mutable-content: 1` - разрешает Notification Service Extension модифицировать
- `content-available: 1` - silent notification, разбудит app в background
- `interruption-level` - iOS 15+ приоритет (passive, active, time-sensitive, critical)
- `relevance-score` - iOS 15+ для сортировки в notification summary (0.0-1.0)

## 4. Обработка уведомлений

### UNUserNotificationCenterDelegate

```swift
import UserNotifications

class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {

    // Уведомление пришло, когда app в foreground
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        print("Received notification in foreground: \(notification.request.content.title)")

        // iOS 14+: показать баннер даже если app активно
        completionHandler([.banner, .sound, .badge])

        // iOS 10-13:
        // completionHandler([.alert, .sound, .badge])
    }

    // Пользователь нажал на уведомление или action
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        let actionIdentifier = response.actionIdentifier

        switch actionIdentifier {
        case UNNotificationDefaultActionIdentifier:
            // Нажал на само уведомление
            print("User tapped notification")
            handleNotificationTap(userInfo: userInfo)

        case UNNotificationDismissActionIdentifier:
            // Dismiss
            print("User dismissed notification")

        case "ACCEPT_ACTION":
            print("User accepted")
            handleAcceptAction(userInfo: userInfo)

        case "DECLINE_ACTION":
            print("User declined")
            handleDeclineAction(userInfo: userInfo)

        default:
            break
        }

        completionHandler()
    }

    func handleNotificationTap(userInfo: [AnyHashable: Any]) {
        // Навигация в нужный экран
        if let chatId = userInfo["chatId"] as? String {
            NotificationCenter.default.post(
                name: .openChat,
                object: nil,
                userInfo: ["chatId": chatId]
            )
        }
    }

    func handleAcceptAction(userInfo: [AnyHashable: Any]) {
        // Backend request
        Task {
            guard let requestId = userInfo["requestId"] as? String else { return }
            try? await acceptRequest(requestId: requestId)
        }
    }

    func handleDeclineAction(userInfo: [AnyHashable: Any]) {
        Task {
            guard let requestId = userInfo["requestId"] as? String else { return }
            try? await declineRequest(requestId: requestId)
        }
    }

    func acceptRequest(requestId: String) async throws {
        // API call
    }

    func declineRequest(requestId: String) async throws {
        // API call
    }
}

// Setup в AppDelegate
func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
    UNUserNotificationCenter.current().delegate = NotificationDelegate()
    return true
}

extension Notification.Name {
    static let openChat = Notification.Name("openChat")
}
```

### Обработка в разных состояниях app

```swift
// App terminated → Пользователь нажал на notification
func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {

    if let notificationResponse = launchOptions?[.remoteNotification] as? [AnyHashable: Any] {
        print("App launched from notification: \(notificationResponse)")
        // Delay navigation пока UI не готов
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.handleNotificationLaunch(userInfo: notificationResponse)
        }
    }

    return true
}

// App в background → Получен silent notification
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
    fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
) {
    print("Received remote notification in background")

    // Background work (max 30 seconds)
    Task {
        do {
            // Fetch new data
            let hasNewData = try await fetchNewData(from: userInfo)

            if hasNewData {
                completionHandler(.newData)
            } else {
                completionHandler(.noData)
            }
        } catch {
            completionHandler(.failed)
        }
    }
}

func fetchNewData(from userInfo: [AnyHashable: Any]) async throws -> Bool {
    // Sync data from server
    return true
}
```

## 5. Notification Actions и Categories

```swift
class NotificationActionManager {

    func setupNotificationActions() {
        // Actions для категории MESSAGE
        let replyAction = UNTextInputNotificationAction(
            identifier: "REPLY_ACTION",
            title: "Ответить",
            options: [.authenticationRequired],
            textInputButtonTitle: "Отправить",
            textInputPlaceholder: "Введите сообщение..."
        )

        let markReadAction = UNNotificationAction(
            identifier: "MARK_READ_ACTION",
            title: "Прочитано",
            options: []
        )

        let deleteAction = UNNotificationAction(
            identifier: "DELETE_ACTION",
            title: "Удалить",
            options: [.destructive, .authenticationRequired]
        )

        let messageCategory = UNNotificationCategory(
            identifier: "MESSAGE_CATEGORY",
            actions: [replyAction, markReadAction, deleteAction],
            intentIdentifiers: [],
            options: [.customDismissAction]
        )

        // Actions для категории FRIEND_REQUEST
        let acceptAction = UNNotificationAction(
            identifier: "ACCEPT_ACTION",
            title: "Принять",
            options: [.foreground] // Откроет app
        )

        let declineAction = UNNotificationAction(
            identifier: "DECLINE_ACTION",
            title: "Отклонить",
            options: [.destructive]
        )

        let friendRequestCategory = UNNotificationCategory(
            identifier: "FRIEND_REQUEST_CATEGORY",
            actions: [acceptAction, declineAction],
            intentIdentifiers: [],
            options: []
        )

        // Actions для категории REMINDER
        let snoozeAction = UNNotificationAction(
            identifier: "SNOOZE_ACTION",
            title: "Отложить",
            options: []
        )

        let completeAction = UNNotificationAction(
            identifier: "COMPLETE_ACTION",
            title: "Выполнено",
            options: []
        )

        let reminderCategory = UNNotificationCategory(
            identifier: "REMINDER_CATEGORY",
            actions: [snoozeAction, completeAction],
            intentIdentifiers: [],
            options: []
        )

        // Регистрация всех categories
        UNUserNotificationCenter.current().setNotificationCategories([
            messageCategory,
            friendRequestCategory,
            reminderCategory
        ])
    }
}

// Использование с локальным уведомлением
func scheduleNotificationWithActions() async throws {
    let content = UNMutableNotificationContent()
    content.title = "Новое сообщение"
    content.body = "У вас новое сообщение от Джона"
    content.categoryIdentifier = "MESSAGE_CATEGORY" // Связываем с category
    content.sound = .default

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
    let request = UNNotificationRequest(
        identifier: UUID().uuidString,
        content: content,
        trigger: trigger
    )

    try await UNUserNotificationCenter.current().add(request)
}

// Обработка text input action
func userNotificationCenter(
    _ center: UNUserNotificationCenter,
    didReceive response: UNNotificationResponse,
    withCompletionHandler completionHandler: @escaping () -> Void
) {
    if response.actionIdentifier == "REPLY_ACTION",
       let textResponse = response as? UNTextInputNotificationResponse {

        let replyText = textResponse.userText
        print("User replied: \(replyText)")

        // Отправить сообщение на сервер
        Task {
            try? await sendMessage(text: replyText, userInfo: response.notification.request.content.userInfo)
        }
    }

    completionHandler()
}

func sendMessage(text: String, userInfo: [AnyHashable: Any]) async throws {
    // API call
}
```

## 6. Notification Extensions

### Service Extension (Modify Push Notifications)

**Создание:** File → New → Target → Notification Service Extension

```swift
// NotificationService.swift
import UserNotifications

class NotificationService: UNNotificationServiceExtension {

    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttemptContent: UNMutableNotificationContent?

    override func didReceive(
        _ request: UNNotificationRequest,
        withContentHandler contentHandler: @escaping (UNNotificationContent) -> Void
    ) {
        self.contentHandler = contentHandler

        guard let bestAttemptContent = request.content.mutableCopy() as? UNMutableNotificationContent else {
            contentHandler(request.content)
            return
        }

        self.bestAttemptContent = bestAttemptContent

        // 1. Модификация текста
        bestAttemptContent.title = "[Изменено] \(bestAttemptContent.title)"

        // 2. Декриптация (если отправляли encrypted payload)
        if let encryptedBody = bestAttemptContent.userInfo["encrypted_body"] as? String {
            bestAttemptContent.body = decrypt(encryptedBody)
        }

        // 3. Загрузка изображения
        if let imageURLString = bestAttemptContent.userInfo["image_url"] as? String,
           let imageURL = URL(string: imageURLString) {

            Task {
                await downloadAndAttachMedia(url: imageURL, content: bestAttemptContent)
            }
        } else {
            contentHandler(bestAttemptContent)
        }
    }

    func downloadAndAttachMedia(url: URL, content: UNMutableNotificationContent) async {
        do {
            // Скачать файл
            let (tempURL, _) = try await URLSession.shared.download(from: url)

            // Создать постоянную копию (temp файлы удаляются)
            let fileManager = FileManager.default
            let documentsPath = fileManager.temporaryDirectory
                .appendingPathComponent(url.lastPathComponent)

            try? fileManager.removeItem(at: documentsPath) // Remove если существует
            try fileManager.moveItem(at: tempURL, to: documentsPath)

            // Прикрепить как attachment
            let attachment = try UNNotificationAttachment(
                identifier: "image",
                url: documentsPath,
                options: [UNNotificationAttachmentOptionsTypeHintKey: "public.jpeg"]
            )

            content.attachments = [attachment]

            // Показать notification
            contentHandler?(content)

        } catch {
            print("Failed to download media: \(error)")
            contentHandler?(content)
        }
    }

    func decrypt(_ encryptedString: String) -> String {
        // Decrypt logic
        return encryptedString
    }

    override func serviceExtensionTimeWillExpire() {
        // iOS вызывает через ~30 секунд
        // Последний шанс вернуть content
        if let contentHandler = contentHandler,
           let bestAttemptContent = bestAttemptContent {
            contentHandler(bestAttemptContent)
        }
    }
}
```

### Content Extension (Custom Notification UI)

**Создание:** File → New → Target → Notification Content Extension

```swift
// NotificationViewController.swift
import UIKit
import UserNotifications
import UserNotificationsUI

class NotificationViewController: UIViewController, UNNotificationContentExtension {

    @IBOutlet weak var titleLabel: UILabel!
    @IBOutlet weak var bodyLabel: UILabel!
    @IBOutlet weak var imageView: UIImageView!
    @IBOutlet weak var actionButton: UIButton!

    func didReceive(_ notification: UNNotification) {
        let content = notification.request.content

        // Заполнить UI
        titleLabel.text = content.title
        bodyLabel.text = content.body

        // Показать attachment (если есть)
        if let attachment = content.attachments.first {
            if attachment.url.startAccessingSecurityScopedResource() {
                if let imageData = try? Data(contentsOf: attachment.url),
                   let image = UIImage(data: imageData) {
                    imageView.image = image
                }
                attachment.url.stopAccessingSecurityScopedResource()
            }
        }

        // Custom data
        if let imageURLString = content.userInfo["avatar_url"] as? String,
           let imageURL = URL(string: imageURLString) {
            loadImage(from: imageURL)
        }
    }

    func loadImage(from url: URL) {
        Task {
            let (data, _) = try await URLSession.shared.data(from: url)
            if let image = UIImage(data: data) {
                await MainActor.run {
                    imageView.image = image
                }
            }
        }
    }

    // MARK: - Actions (iOS 12+)

    func didReceive(
        _ response: UNNotificationResponse,
        completionHandler completion: @escaping (UNNotificationContentExtensionResponseOption) -> Void
    ) {
        if response.actionIdentifier == "LIKE_ACTION" {
            // Handle like
            completion(.dismiss) // Закрыть notification
        } else if response.actionIdentifier == "COMMENT_ACTION" {
            completion(.dismissAndForwardAction) // Dismiss и отправить в app
        }
    }

    @IBAction func buttonTapped(_ sender: UIButton) {
        // Custom action внутри notification
        // Через completion можно открыть app
    }
}

// Info.plist настройка в Content Extension
/*
<key>NSExtension</key>
<dict>
    <key>NSExtensionAttributes</key>
    <dict>
        <key>UNNotificationExtensionCategory</key>
        <string>MESSAGE_CATEGORY</string>
        <key>UNNotificationExtensionInitialContentSizeRatio</key>
        <real>0.5</real>
        <key>UNNotificationExtensionDefaultContentHidden</key>
        <false/>
    </dict>
    <key>NSExtensionPointIdentifier</key>
    <string>com.apple.usernotifications.content-extension</string>
    <key>NSExtensionPrincipalClass</key>
    <string>$(PRODUCT_MODULE_NAME).NotificationViewController</string>
</dict>
*/
```

## 7. Rich Notifications (Images, Videos, Audio)

```swift
class RichNotificationManager {

    // Локальное уведомление с изображением
    func scheduleNotificationWithImage(imageURL: URL) async throws {
        let content = UNMutableNotificationContent()
        content.title = "Новая фотография"
        content.body = "Посмотрите новый снимок!"
        content.sound = .default

        // Скачать изображение
        let (tempURL, _) = try await URLSession.shared.download(from: imageURL)

        // Переместить в постоянное место
        let fileManager = FileManager.default
        let documentsPath = fileManager.temporaryDirectory
            .appendingPathComponent(imageURL.lastPathComponent)

        try? fileManager.removeItem(at: documentsPath)
        try fileManager.moveItem(at: tempURL, to: documentsPath)

        // Создать attachment
        let attachment = try UNNotificationAttachment(
            identifier: "image",
            url: documentsPath,
            options: nil
        )

        content.attachments = [attachment]

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }

    // Уведомление с видео
    func scheduleNotificationWithVideo(videoURL: URL) async throws {
        let content = UNMutableNotificationContent()
        content.title = "Новое видео"
        content.body = "Смотрите сейчас!"

        let (tempURL, _) = try await URLSession.shared.download(from: videoURL)

        let fileManager = FileManager.default
        let documentsPath = fileManager.temporaryDirectory
            .appendingPathComponent(videoURL.lastPathComponent)

        try? fileManager.removeItem(at: documentsPath)
        try fileManager.moveItem(at: tempURL, to: documentsPath)

        let attachment = try UNNotificationAttachment(
            identifier: "video",
            url: documentsPath,
            options: [UNNotificationAttachmentOptionsTypeHintKey: "public.mpeg-4"]
        )

        content.attachments = [attachment]

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }

    // Уведомление с GIF
    func scheduleNotificationWithGIF(gifURL: URL) async throws {
        let content = UNMutableNotificationContent()
        content.title = "GIF для вас!"
        content.body = "Проверьте это"

        let (tempURL, _) = try await URLSession.shared.download(from: gifURL)

        let fileManager = FileManager.default
        let documentsPath = fileManager.temporaryDirectory
            .appendingPathComponent("animation.gif")

        try? fileManager.removeItem(at: documentsPath)
        try fileManager.moveItem(at: tempURL, to: documentsPath)

        let attachment = try UNNotificationAttachment(
            identifier: "gif",
            url: documentsPath,
            options: [UNNotificationAttachmentOptionsTypeHintKey: "com.compuserve.gif"]
        )

        content.attachments = [attachment]

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }
}

// Поддерживаемые форматы:
// Images: JPEG, GIF, PNG
// Audio: MP3, MPEG4 Audio, AIFF, WAV
// Video: MPEG, MPEG2, MPEG4, AVI
//
// Ограничения:
// - Image: 10 MB
// - Audio: 5 MB
// - Video: 50 MB
```

## 8. Provisional Notifications (iOS 12+)

```swift
// Тихие уведомления без явного запроса разрешения
class ProvisionalNotificationManager {

    func requestProvisionalAuthorization() async throws {
        let center = UNUserNotificationCenter.current()

        // Provisional authorization
        let granted = try await center.requestAuthorization(options: [
            .alert,
            .sound,
            .badge,
            .provisional // Ключевая опция
        ])

        print("Provisional authorization: \(granted)")
    }

    // Проверить тип авторизации
    func checkAuthorizationType() async {
        let settings = await UNUserNotificationCenter.current().notificationSettings()

        switch settings.authorizationStatus {
        case .notDetermined:
            print("Not requested yet")
        case .denied:
            print("User denied")
        case .authorized:
            print("Fully authorized")
        case .provisional:
            print("Provisional - silent notifications allowed")
        case .ephemeral:
            print("Ephemeral - App Clip authorization")
        @unknown default:
            print("Unknown status")
        }
    }
}

// Provisional notifications:
// - Показываются только в Notification Center, не на экране
// - Нет звука и вибрации
// - Пользователь может Keep или Turn Off
// - Keep → full authorization
// - Turn Off → denied
```

## 9. Time Sensitive Notifications (iOS 15+)

```swift
class TimeSensitiveNotificationManager {

    func requestTimeSensitiveAuthorization() async throws {
        let center = UNUserNotificationCenter.current()

        // Time Sensitive требует отдельного разрешения
        let granted = try await center.requestAuthorization(options: [
            .alert,
            .sound,
            .badge,
            .timeSensitive // iOS 15+
        ])

        print("Authorization granted: \(granted)")
    }

    func scheduleTimeSensitiveNotification() async throws {
        let content = UNMutableNotificationContent()
        content.title = "Срочно!"
        content.body = "Ваша поездка прибывает через 2 минуты"
        content.sound = .defaultCritical // Громкий звук
        content.interruptionLevel = .timeSensitive // Ключевое свойство

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }

    // Critical notifications (требует entitlement)
    func scheduleCriticalNotification() async throws {
        let content = UNMutableNotificationContent()
        content.title = "Критически важно"
        content.body = "Пожарная тревога"
        content.sound = .defaultCritical
        content.interruptionLevel = .critical // Игнорирует Focus/DND

        // Критические уведомления требуют:
        // 1. Entitlement: com.apple.developer.usernotifications.critical-alerts
        // 2. Approval от Apple

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 1, repeats: false)
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }
}

// Interruption Levels (iOS 15+):
// - .passive: Тихое, показывается только в Notification Center
// - .active: Обычное поведение (default)
// - .timeSensitive: Прорывается через Focus mode
// - .critical: Игнорирует все настройки, требует entitlement
```

## 10. Live Activities и Dynamic Island (iOS 16+)

```swift
// ActivityAttributes.swift
import ActivityKit

struct PizzaDeliveryAttributes: ActivityAttributes {
    public struct ContentState: Codable, Hashable {
        var status: DeliveryStatus
        var estimatedDeliveryTime: Date
        var driverLocation: Location?
    }

    var orderId: String
    var pizzaName: String
    var orderTotal: Double
}

enum DeliveryStatus: String, Codable {
    case preparing = "Готовится"
    case outForDelivery = "В пути"
    case delivered = "Доставлено"
}

struct Location: Codable, Hashable {
    var latitude: Double
    var longitude: Double
}

// PizzaDeliveryLiveActivity.swift
import WidgetKit
import SwiftUI
import ActivityKit

struct PizzaDeliveryLiveActivity: Widget {
    var body: some WidgetConfiguration {
        ActivityConfiguration(for: PizzaDeliveryAttributes.self) { context in
            // Lock Screen UI
            LockScreenLiveActivityView(context: context)
        } dynamicIsland: { context in
            DynamicIsland {
                // Expanded UI
                DynamicIslandExpandedRegion(.leading) {
                    HStack {
                        Image(systemName: "box.truck.fill")
                            .foregroundColor(.orange)
                        Text(context.state.status.rawValue)
                            .font(.caption)
                    }
                }

                DynamicIslandExpandedRegion(.trailing) {
                    Text(context.state.estimatedDeliveryTime, style: .timer)
                        .font(.caption)
                        .monospacedDigit()
                }

                DynamicIslandExpandedRegion(.center) {
                    Text(context.attributes.pizzaName)
                        .font(.headline)
                }

                DynamicIslandExpandedRegion(.bottom) {
                    ProgressView(value: progressValue(for: context.state.status))
                        .tint(.orange)
                }
            } compactLeading: {
                // Compact Leading (слева от notch)
                Image(systemName: "box.truck.fill")
                    .foregroundColor(.orange)
            } compactTrailing: {
                // Compact Trailing (справа от notch)
                Text(context.state.estimatedDeliveryTime, style: .timer)
                    .monospacedDigit()
                    .font(.caption2)
            } minimal: {
                // Minimal (когда несколько activities)
                Image(systemName: "box.truck.fill")
            }
        }
    }

    func progressValue(for status: DeliveryStatus) -> Double {
        switch status {
        case .preparing: return 0.33
        case .outForDelivery: return 0.66
        case .delivered: return 1.0
        }
    }
}

struct LockScreenLiveActivityView: View {
    let context: ActivityViewContext<PizzaDeliveryAttributes>

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "box.truck.fill")
                    .foregroundColor(.orange)
                Text(context.attributes.pizzaName)
                    .font(.headline)
                Spacer()
                Text(context.state.status.rawValue)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            HStack {
                Text("Доставка:")
                Text(context.state.estimatedDeliveryTime, style: .relative)
                    .bold()
            }
            .font(.caption)

            ProgressView(value: progressValue(for: context.state.status))
                .tint(.orange)
        }
        .padding()
    }

    func progressValue(for status: DeliveryStatus) -> Double {
        switch status {
        case .preparing: return 0.33
        case .outForDelivery: return 0.66
        case .delivered: return 1.0
        }
    }
}

// Управление Live Activity
class LiveActivityManager {

    // Запустить Live Activity
    func startDeliveryTracking(orderId: String, pizzaName: String, total: Double) async throws {
        let attributes = PizzaDeliveryAttributes(
            orderId: orderId,
            pizzaName: pizzaName,
            orderTotal: total
        )

        let initialState = PizzaDeliveryAttributes.ContentState(
            status: .preparing,
            estimatedDeliveryTime: Date().addingTimeInterval(30 * 60), // +30 минут
            driverLocation: nil
        )

        let activity = try Activity<PizzaDeliveryAttributes>.request(
            attributes: attributes,
            contentState: initialState,
            pushType: .token // Разрешить push updates
        )

        print("Started activity: \(activity.id)")

        // Получить push token для обновлений
        for await pushToken in activity.pushTokenUpdates {
            let token = pushToken.map { String(format: "%02x", $0) }.joined()
            print("Push token: \(token)")

            // Отправить токен на сервер для удалённых обновлений
            try await sendPushTokenToServer(token: token, activityId: activity.id)
        }
    }

    // Обновить состояние локально
    func updateDeliveryStatus(to status: DeliveryStatus, eta: Date) async {
        let activities = Activity<PizzaDeliveryAttributes>.activities

        guard let activity = activities.first else { return }

        let newState = PizzaDeliveryAttributes.ContentState(
            status: status,
            estimatedDeliveryTime: eta,
            driverLocation: Location(latitude: 37.7749, longitude: -122.4194)
        )

        await activity.update(using: newState)
    }

    // Завершить Live Activity
    func endDelivery() async {
        let activities = Activity<PizzaDeliveryAttributes>.activities

        guard let activity = activities.first else { return }

        let finalState = PizzaDeliveryAttributes.ContentState(
            status: .delivered,
            estimatedDeliveryTime: Date(),
            driverLocation: nil
        )

        await activity.end(using: finalState, dismissalPolicy: .immediate)
        // .default - через 4 часа
        // .immediate - сразу
        // .after(Date) - в указанное время
    }

    func sendPushTokenToServer(token: String, activityId: String) async throws {
        // Отправить на backend
    }
}

// Push обновление Live Activity с сервера
// APNs payload:
/*
{
  "aps": {
    "timestamp": 1234567890,
    "event": "update",
    "content-state": {
      "status": "outForDelivery",
      "estimatedDeliveryTime": 1234567890,
      "driverLocation": {
        "latitude": 37.7749,
        "longitude": -122.4194
      }
    }
  }
}

Headers:
apns-topic: your.bundle.id.push-type.liveactivity
apns-push-type: liveactivity
*/
```

## 11. Тестирование уведомлений

```swift
class NotificationTester {

    // Симулятор: Push notifications симуляция через .apns файл
    // Создать файл payload.apns:
    /*
    {
      "Simulator Target Bundle": "com.yourcompany.yourapp",
      "aps": {
        "alert": {
          "title": "Test Notification",
          "body": "This is a test"
        },
        "badge": 1,
        "sound": "default"
      }
    }
    */

    // Отправка через terminal:
    // xcrun simctl push booted com.yourcompany.yourapp payload.apns

    // Или drag & drop файл в simulator

    func testLocalNotification() async throws {
        let content = UNMutableNotificationContent()
        content.title = "Test Local"
        content.body = "Testing local notification"
        content.sound = .default
        content.badge = 1

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
        let request = UNNotificationRequest(
            identifier: "test-notification",
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
        print("Test notification scheduled")
    }

    func testNotificationWithActions() async throws {
        // Setup categories first
        setupTestCategory()

        let content = UNMutableNotificationContent()
        content.title = "Test Actions"
        content.body = "Tap to test actions"
        content.categoryIdentifier = "TEST_CATEGORY"
        content.sound = .default

        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
        let request = UNNotificationRequest(
            identifier: "test-actions",
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }

    func setupTestCategory() {
        let action1 = UNNotificationAction(
            identifier: "ACTION1",
            title: "Action 1",
            options: []
        )

        let action2 = UNNotificationAction(
            identifier: "ACTION2",
            title: "Action 2",
            options: [.destructive]
        )

        let category = UNNotificationCategory(
            identifier: "TEST_CATEGORY",
            actions: [action1, action2],
            intentIdentifiers: [],
            options: []
        )

        UNUserNotificationCenter.current().setNotificationCategories([category])
    }

    // Debugging: посмотреть все запланированные
    func printPendingNotifications() async {
        let requests = await UNUserNotificationCenter.current().pendingNotificationRequests()
        print("Pending notifications: \(requests.count)")

        for request in requests {
            print("ID: \(request.identifier)")
            print("Title: \(request.content.title)")
            print("Body: \(request.content.body)")
            if let trigger = request.trigger as? UNTimeIntervalNotificationTrigger {
                print("Time interval: \(trigger.timeInterval)")
            }
            print("---")
        }
    }
}

// Real device testing:
// 1. Нужен Apple Developer аккаунт
// 2. Создать APNs key в Developer Portal
// 3. Use production APNs endpoint для TestFlight builds
// 4. Use sandbox APNs endpoint для development builds
//
// APNs endpoints:
// Sandbox: api.sandbox.push.apple.com:443
// Production: api.push.apple.com:443
```

## 12. Сторонние сервисы (Firebase, OneSignal)

### Firebase Cloud Messaging (FCM)

```swift
// Package.swift or CocoaPods
// pod 'Firebase/Messaging'

import Firebase
import FirebaseMessaging

class FCMManager: NSObject, MessagingDelegate {

    func setupFirebase() {
        FirebaseApp.configure()
        Messaging.messaging().delegate = self

        // Включить auto-init
        Messaging.messaging().isAutoInitEnabled = true
    }

    func registerForFCM() {
        Task {
            do {
                // Request authorization
                let granted = try await UNUserNotificationCenter.current()
                    .requestAuthorization(options: [.alert, .sound, .badge])

                if granted {
                    await MainActor.run {
                        UIApplication.shared.registerForRemoteNotifications()
                    }
                }
            } catch {
                print("Failed to register: \(error)")
            }
        }
    }

    // Получить FCM token
    func getFCMToken() async throws -> String {
        return try await Messaging.messaging().token()
    }

    // MessagingDelegate
    func messaging(_ messaging: Messaging, didReceiveRegistrationToken fcmToken: String?) {
        print("FCM Token: \(fcmToken ?? "")")

        // Отправить на ваш backend
        if let token = fcmToken {
            Task {
                try? await sendFCMTokenToServer(token)
            }
        }
    }

    func sendFCMTokenToServer(_ token: String) async throws {
        // API call
    }
}

// AppDelegate
func application(
    _ application: UIApplication,
    didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
) {
    // Передать APNs token в Firebase
    Messaging.messaging().apnsToken = deviceToken
}

// Отправка с сервера через FCM REST API
/*
POST https://fcm.googleapis.com/v1/projects/YOUR_PROJECT_ID/messages:send
Authorization: Bearer YOUR_ACCESS_TOKEN

{
  "message": {
    "token": "DEVICE_FCM_TOKEN",
    "notification": {
      "title": "FCM Notification",
      "body": "Hello from Firebase"
    },
    "data": {
      "customKey": "customValue"
    },
    "apns": {
      "payload": {
        "aps": {
          "badge": 1,
          "sound": "default",
          "mutable-content": 1
        }
      }
    }
  }
}
*/
```

### OneSignal

```swift
// CocoaPods: pod 'OneSignalXCFramework'
// SPM: https://github.com/OneSignal/OneSignal-XCFramework

import OneSignalFramework

class OneSignalManager {

    func setupOneSignal() {
        // Initialize with App ID
        OneSignal.initialize("YOUR_ONESIGNAL_APP_ID", withLaunchOptions: nil)

        // Request permission
        OneSignal.Notifications.requestPermission({ accepted in
            print("User accepted notifications: \(accepted)")
        }, fallbackToSettings: true)
    }

    func setupNotificationHandlers() {
        // Notification opened
        OneSignal.Notifications.addEventListener { event in
            print("Notification opened: \(event.notification.notificationId)")

            let data = event.notification.additionalData
            print("Custom data: \(data ?? [:])")

            // Navigate based on data
            if let screenName = data?["screen"] as? String {
                self.navigateToScreen(screenName)
            }
        }

        // Notification will show
        OneSignal.Notifications.addForegroundWillDisplayEventHandler { event in
            print("Notification will display: \(event.notification.title ?? "")")

            // Можно предотвратить показ
            // event.preventDefault()

            // Или изменить notification
            event.notification.display()
        }
    }

    func setUserTags() {
        OneSignal.User.addTags([
            "user_id": "12345",
            "username": "john_doe",
            "subscription": "premium"
        ])
    }

    func sendTagsBasedNotification() {
        // Отправляется с OneSignal dashboard или API
        // Targeting: user_id = 12345
    }

    func navigateToScreen(_ screenName: String) {
        // Navigation logic
    }
}

// OneSignal REST API для отправки
/*
POST https://onesignal.com/api/v1/notifications
Authorization: Basic YOUR_REST_API_KEY

{
  "app_id": "YOUR_APP_ID",
  "include_player_ids": ["device-id-1", "device-id-2"],
  "headings": {"en": "Hello"},
  "contents": {"en": "World"},
  "data": {
    "screen": "profile",
    "userId": "12345"
  }
}
*/
```

## Полный пример настройки Push Notifications

```swift
// 1. AppDelegate.swift
import UIKit
import UserNotifications

@main
class AppDelegate: UIResponder, UIApplicationDelegate {

    let notificationManager = NotificationManager.shared

    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {

        // Setup notification delegate
        UNUserNotificationCenter.current().delegate = notificationManager

        // Setup notification categories
        notificationManager.setupNotificationCategories()

        // Register for remote notifications
        notificationManager.registerForRemoteNotifications()

        // Check if launched from notification
        if let notificationResponse = launchOptions?[.remoteNotification] as? [AnyHashable: Any] {
            DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
                self.notificationManager.handleNotificationLaunch(userInfo: notificationResponse)
            }
        }

        return true
    }

    // MARK: - Remote Notifications

    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        notificationManager.handleDeviceToken(token)
    }

    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        print("Failed to register for remote notifications: \(error)")
    }

    func application(
        _ application: UIApplication,
        didReceiveRemoteNotification userInfo: [AnyHashable: Any],
        fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
    ) {
        notificationManager.handleBackgroundNotification(userInfo: userInfo) { result in
            completionHandler(result)
        }
    }
}

// 2. NotificationManager.swift
import UserNotifications
import UIKit

class NotificationManager: NSObject {

    static let shared = NotificationManager()

    private override init() {
        super.init()
    }

    // MARK: - Registration

    func registerForRemoteNotifications() {
        Task {
            do {
                let granted = try await UNUserNotificationCenter.current()
                    .requestAuthorization(options: [.alert, .sound, .badge])

                if granted {
                    await MainActor.run {
                        UIApplication.shared.registerForRemoteNotifications()
                    }
                }
            } catch {
                print("Authorization failed: \(error)")
            }
        }
    }

    func handleDeviceToken(_ token: String) {
        print("Device Token: \(token)")

        // Save locally
        UserDefaults.standard.set(token, forKey: "deviceToken")

        // Send to server
        Task {
            try? await sendTokenToServer(token)
        }
    }

    func sendTokenToServer(_ token: String) async throws {
        guard let url = URL(string: "https://yourapi.com/register-device") else { return }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let body: [String: Any] = [
            "device_token": token,
            "platform": "ios",
            "bundle_id": Bundle.main.bundleIdentifier ?? "",
            "app_version": Bundle.main.infoDictionary?["CFBundleShortVersionString"] as? String ?? ""
        ]

        request.httpBody = try JSONSerialization.data(withJSONObject: body)

        let (data, response) = try await URLSession.shared.data(for: request)

        if let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 {
            print("Token registered successfully")
        } else {
            print("Failed to register token")
        }
    }

    // MARK: - Categories

    func setupNotificationCategories() {
        // Message category
        let replyAction = UNTextInputNotificationAction(
            identifier: "REPLY_ACTION",
            title: "Ответить",
            options: [.authenticationRequired],
            textInputButtonTitle: "Отправить",
            textInputPlaceholder: "Введите сообщение..."
        )

        let markReadAction = UNNotificationAction(
            identifier: "MARK_READ_ACTION",
            title: "Прочитано",
            options: []
        )

        let messageCategory = UNNotificationCategory(
            identifier: "MESSAGE_CATEGORY",
            actions: [replyAction, markReadAction],
            intentIdentifiers: [],
            options: [.customDismissAction]
        )

        // Friend request category
        let acceptAction = UNNotificationAction(
            identifier: "ACCEPT_ACTION",
            title: "Принять",
            options: [.foreground]
        )

        let declineAction = UNNotificationAction(
            identifier: "DECLINE_ACTION",
            title: "Отклонить",
            options: [.destructive]
        )

        let friendRequestCategory = UNNotificationCategory(
            identifier: "FRIEND_REQUEST_CATEGORY",
            actions: [acceptAction, declineAction],
            intentIdentifiers: [],
            options: []
        )

        UNUserNotificationCenter.current().setNotificationCategories([
            messageCategory,
            friendRequestCategory
        ])
    }

    // MARK: - Handling

    func handleNotificationLaunch(userInfo: [AnyHashable: Any]) {
        print("App launched from notification")
        processNotificationData(userInfo)
    }

    func handleBackgroundNotification(
        userInfo: [AnyHashable: Any],
        completion: @escaping (UIBackgroundFetchResult) -> Void
    ) {
        print("Received background notification")

        Task {
            do {
                let hasNewData = try await fetchNewData(from: userInfo)
                completion(hasNewData ? .newData : .noData)
            } catch {
                completion(.failed)
            }
        }
    }

    func fetchNewData(from userInfo: [AnyHashable: Any]) async throws -> Bool {
        // Sync logic
        return true
    }

    func processNotificationData(_ userInfo: [AnyHashable: Any]) {
        guard let screenName = userInfo["screen"] as? String else { return }

        NotificationCenter.default.post(
            name: .navigateToScreen,
            object: nil,
            userInfo: ["screen": screenName, "data": userInfo]
        )
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        print("Notification received in foreground")
        completionHandler([.banner, .sound, .badge])
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        let actionIdentifier = response.actionIdentifier

        switch actionIdentifier {
        case UNNotificationDefaultActionIdentifier:
            print("User tapped notification")
            processNotificationData(userInfo)

        case "REPLY_ACTION":
            if let textResponse = response as? UNTextInputNotificationResponse {
                handleReply(text: textResponse.userText, userInfo: userInfo)
            }

        case "MARK_READ_ACTION":
            handleMarkRead(userInfo: userInfo)

        case "ACCEPT_ACTION":
            handleAccept(userInfo: userInfo)

        case "DECLINE_ACTION":
            handleDecline(userInfo: userInfo)

        default:
            break
        }

        completionHandler()
    }

    // MARK: - Action Handlers

    func handleReply(text: String, userInfo: [AnyHashable: Any]) {
        Task {
            guard let chatId = userInfo["chatId"] as? String else { return }
            try? await sendMessage(text: text, chatId: chatId)
        }
    }

    func handleMarkRead(userInfo: [AnyHashable: Any]) {
        Task {
            guard let messageId = userInfo["messageId"] as? String else { return }
            try? await markMessageAsRead(messageId: messageId)
        }
    }

    func handleAccept(userInfo: [AnyHashable: Any]) {
        Task {
            guard let requestId = userInfo["requestId"] as? String else { return }
            try? await acceptFriendRequest(requestId: requestId)
        }
    }

    func handleDecline(userInfo: [AnyHashable: Any]) {
        Task {
            guard let requestId = userInfo["requestId"] as? String else { return }
            try? await declineFriendRequest(requestId: requestId)
        }
    }

    // API Calls

    func sendMessage(text: String, chatId: String) async throws {
        // Implementation
    }

    func markMessageAsRead(messageId: String) async throws {
        // Implementation
    }

    func acceptFriendRequest(requestId: String) async throws {
        // Implementation
    }

    func declineFriendRequest(requestId: String) async throws {
        // Implementation
    }
}

extension Notification.Name {
    static let navigateToScreen = Notification.Name("navigateToScreen")
}

// 3. Coordinator для навигации
class NotificationCoordinator {

    init() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleNavigateToScreen),
            name: .navigateToScreen,
            object: nil
        )
    }

    @objc func handleNavigateToScreen(_ notification: Notification) {
        guard let screenName = notification.userInfo?["screen"] as? String else { return }

        DispatchQueue.main.async {
            switch screenName {
            case "chat":
                if let chatId = notification.userInfo?["chatId"] as? String {
                    self.navigateToChat(chatId: chatId)
                }
            case "profile":
                if let userId = notification.userInfo?["userId"] as? String {
                    self.navigateToProfile(userId: userId)
                }
            default:
                break
            }
        }
    }

    func navigateToChat(chatId: String) {
        // Navigation logic
    }

    func navigateToProfile(userId: String) {
        // Navigation logic
    }
}
```

## 6 типичных ошибок

### ❌ Ошибка 1: Не проверяем authorization status перед планированием

```swift
// Неправильно
func scheduleNotification() async throws {
    let content = UNMutableNotificationContent()
    content.title = "Reminder"
    content.body = "Time to work!"

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 60, repeats: false)
    let request = UNNotificationRequest(identifier: "reminder", content: content, trigger: trigger)

    try await UNUserNotificationCenter.current().add(request)
    // Если разрешения нет - notification не покажется, но ошибки не будет!
}
```

```swift
// ✅ Правильно
func scheduleNotification() async throws {
    let center = UNUserNotificationCenter.current()
    let settings = await center.notificationSettings()

    // Проверяем статус
    guard settings.authorizationStatus == .authorized else {
        if settings.authorizationStatus == .notDetermined {
            // Запросить разрешение
            let granted = try await center.requestAuthorization(options: [.alert, .sound])
            guard granted else {
                throw NotificationError.permissionDenied
            }
        } else {
            throw NotificationError.permissionDenied
        }
    }

    let content = UNMutableNotificationContent()
    content.title = "Reminder"
    content.body = "Time to work!"

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 60, repeats: false)
    let request = UNNotificationRequest(identifier: "reminder", content: content, trigger: trigger)

    try await center.add(request)
}

enum NotificationError: Error {
    case permissionDenied
}
```

### ❌ Ошибка 2: Забываем установить delegate перед регистрацией

```swift
// Неправильно
func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
    // Регистрируем notification сразу
    UIApplication.shared.registerForRemoteNotifications()

    // Delegate устанавливаем позже
    UNUserNotificationCenter.current().delegate = self

    // Проблема: можем пропустить notifications пока delegate не установлен
    return true
}
```

```swift
// ✅ Правильно
func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
) -> Bool {
    // СНАЧАЛА устанавливаем delegate
    UNUserNotificationCenter.current().delegate = self

    // Регистрируем categories
    setupNotificationCategories()

    // ПОТОМ регистрируем для remote notifications
    Task {
        do {
            let granted = try await UNUserNotificationCenter.current()
                .requestAuthorization(options: [.alert, .sound, .badge])

            if granted {
                await MainActor.run {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        } catch {
            print("Failed to authorize: \(error)")
        }
    }

    return true
}
```

### ❌ Ошибка 3: Не сохраняем temp файлы для attachments

```swift
// Неправильно
func scheduleNotificationWithImage(imageURL: URL) async throws {
    let content = UNMutableNotificationContent()
    content.title = "New Photo"

    let (tempURL, _) = try await URLSession.shared.download(from: imageURL)

    // Проблема: temp файл будет удалён системой
    let attachment = try UNNotificationAttachment(identifier: "image", url: tempURL, options: nil)
    content.attachments = [attachment]

    // Notification покажется без изображения
    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
    let request = UNNotificationRequest(identifier: "photo", content: content, trigger: trigger)
    try await UNUserNotificationCenter.current().add(request)
}
```

```swift
// ✅ Правильно
func scheduleNotificationWithImage(imageURL: URL) async throws {
    let content = UNMutableNotificationContent()
    content.title = "New Photo"

    let (tempURL, _) = try await URLSession.shared.download(from: imageURL)

    // Копируем в постоянную директорию
    let fileManager = FileManager.default
    let documentsURL = fileManager.temporaryDirectory
        .appendingPathComponent(UUID().uuidString)
        .appendingPathExtension(imageURL.pathExtension)

    try fileManager.copyItem(at: tempURL, to: documentsURL)

    // Теперь файл не будет удалён
    let attachment = try UNNotificationAttachment(identifier: "image", url: documentsURL, options: nil)
    content.attachments = [attachment]

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
    let request = UNNotificationRequest(identifier: "photo", content: content, trigger: trigger)
    try await UNUserNotificationCenter.current().add(request)
}
```

### ❌ Ошибка 4: Не вызываем completionHandler в background fetch

```swift
// Неправильно
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
    fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
) {
    print("Received notification")

    Task {
        try await fetchNewData(from: userInfo)
    }

    // Проблема: completionHandler НЕ вызван!
    // iOS будет считать app неотзывчивым и может прекратить background execution
}
```

```swift
// ✅ Правильно
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
    fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
) {
    print("Received notification")

    Task {
        do {
            let hasNewData = try await fetchNewData(from: userInfo)

            // ОБЯЗАТЕЛЬНО вызываем completion
            if hasNewData {
                completionHandler(.newData)
            } else {
                completionHandler(.noData)
            }
        } catch {
            completionHandler(.failed)
        }
    }
}

func fetchNewData(from userInfo: [AnyHashable: Any]) async throws -> Bool {
    // Fetch logic
    return true
}
```

### ❌ Ошибка 5: Не включаем "mutable-content" для Service Extension

```swift
// Неправильно - Server payload
/*
{
  "aps": {
    "alert": {
      "title": "New Message",
      "body": "Check this out"
    },
    "sound": "default"
  },
  "image_url": "https://example.com/image.jpg"
}
*/

// Service Extension НЕ вызовется!
```

```swift
// ✅ Правильно - Server payload
/*
{
  "aps": {
    "alert": {
      "title": "New Message",
      "body": "Check this out"
    },
    "sound": "default",
    "mutable-content": 1  // Обязательное поле!
  },
  "image_url": "https://example.com/image.jpg"
}
*/

// Теперь Service Extension получит notification и сможет загрузить изображение
```

### ❌ Ошибка 6: Используем один identifier для разных notifications

```swift
// Неправильно
func scheduleMultipleReminders() async throws {
    for i in 1...5 {
        let content = UNMutableNotificationContent()
        content.title = "Reminder \(i)"
        content.body = "Task \(i)"

        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: Double(i * 60),
            repeats: false
        )

        // Проблема: один и тот же identifier!
        let request = UNNotificationRequest(
            identifier: "reminder", // Одинаковый для всех
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
        // Каждое новое notification заменит предыдущее
    }
    // В итоге будет только последнее notification!
}
```

```swift
// ✅ Правильно
func scheduleMultipleReminders() async throws {
    for i in 1...5 {
        let content = UNMutableNotificationContent()
        content.title = "Reminder \(i)"
        content.body = "Task \(i)"

        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: Double(i * 60),
            repeats: false
        )

        // Уникальный identifier для каждого
        let request = UNNotificationRequest(
            identifier: "reminder-\(i)", // Уникальный
            content: content,
            trigger: trigger
        )

        try await UNUserNotificationCenter.current().add(request)
    }
    // Все 5 notifications будут запланированы
}

// Или используем UUID
func scheduleReminder() async throws {
    let content = UNMutableNotificationContent()
    content.title = "Reminder"

    let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 60, repeats: false)

    let request = UNNotificationRequest(
        identifier: UUID().uuidString, // Гарантированно уникальный
        content: content,
        trigger: trigger
    )

    try await UNUserNotificationCenter.current().add(request)
}
```

## Связанные темы

- Background Tasks (Background App Refresh)
- App Lifecycle (Active, Background, Terminated states)
- Deep Linking и Universal Links
- WidgetKit и Widget extensions
- CloudKit для cross-device notifications
- Core Location для location-based notifications
- CallKit для VoIP notifications
- PushKit (deprecated в iOS 13, заменён на PushKit для VoIP)

## Ресурсы

- [Apple Documentation: UserNotifications](https://developer.apple.com/documentation/usernotifications)
- [WWDC: What's New in Notifications](https://developer.apple.com/videos)
- [APNs Provider API](https://developer.apple.com/documentation/usernotifications/setting_up_a_remote_notification_server)
- [Firebase Cloud Messaging](https://firebase.google.com/docs/cloud-messaging/ios/client)
- [OneSignal iOS SDK](https://documentation.onesignal.com/docs/ios-sdk-setup)
