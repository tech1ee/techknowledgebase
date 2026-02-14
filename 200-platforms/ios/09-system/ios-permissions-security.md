---
title: "Разрешения и безопасность в iOS"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 74
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/ios
  - topic/security
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-permissions-security]]"
  - "[[ios-overview]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-app-components]]"
---

# iOS Permissions & Security

## TL;DR

iOS использует строгую модель разрешений с обязательными текстовыми описаниями в Info.plist, Privacy Manifest для отслеживания API (iOS 17+), runtime-запросы через системные алерты, и Keychain для безопасного хранения. App Transport Security требует HTTPS, а App Tracking Transparency — явное согласие пользователя на трекинг. Всегда запрашивайте разрешения в контексте использования, обрабатывайте отказы gracefully, и используйте минимально необходимый уровень доступа.

## Аналогия

Представьте iOS как элитный жилой комплекс с охраной. Info.plist — это регистрационная форма, где вы объясняете, зачем вам нужен доступ в спортзал (камера) или бассейн (геолокация). Privacy Manifest — журнал посещений, который показывает, какие охраняемые зоны вы посещали. Keychain — персональный сейф в вашей квартире. App Transport Security — правило "только защищенные каналы связи". Охранник (система) спрашивает разрешение каждый раз, когда вы хотите войти в новую зону, и жильцы (пользователи) могут отозвать доступ в любой момент через диспетчерскую (Settings).

## Диаграммы

### Жизненный цикл разрешений

```
┌──────────────────────────────────────────────────────────────┐
│                    Permission Lifecycle                       │
└──────────────────────────────────────────────────────────────┘

App Install
    │
    ├─► Info.plist проверяется (Usage Descriptions обязательны)
    │
    ├─► Privacy Manifest валидируется (iOS 17+)
    │
    └─► Status: .notDetermined

First Feature Use (Runtime)
    │
    ├─► App запрашивает разрешение
    │
    ├─► System Alert показывается пользователю
    │
    ├─────┬─► User Allows ──► Status: .authorized
    │     │
    │     └─► User Denies ──► Status: .denied
    │
    └─► App обрабатывает результат

Subsequent Access
    │
    ├─► Status: .authorized ──► Direct access
    │
    ├─► Status: .denied ──► Show explanation + Settings deep link
    │
    └─► Status: .restricted ──► Feature unavailable (parental controls)

Settings Change
    │
    └─► App handles permission changes via notifications/delegates
```

### Privacy Manifest Structure

```
┌─────────────────────────────────────────────────────────────┐
│              PrivacyInfo.xcprivacy (iOS 17+)                │
└─────────────────────────────────────────────────────────────┘

PrivacyInfo.xcprivacy
│
├─► NSPrivacyTracking (Bool)
│   └─ true if app uses data for tracking
│
├─► NSPrivacyTrackingDomains (Array)
│   ├─ "analytics.example.com"
│   └─ "ads.partner.com"
│
├─► NSPrivacyCollectedDataTypes (Array)
│   ├─► NSPrivacyCollectedDataType: "NSPrivacyCollectedDataTypeLocation"
│   │   ├─ NSPrivacyCollectedDataTypeLinked: true
│   │   ├─ NSPrivacyCollectedDataTypeTracking: false
│   │   └─ NSPrivacyCollectedDataTypePurposes: ["NSPrivacyCollectedDataTypePurposeAnalytics"]
│   │
│   └─► NSPrivacyCollectedDataType: "NSPrivacyCollectedDataTypeEmailAddress"
│       ├─ NSPrivacyCollectedDataTypeLinked: true
│       └─ NSPrivacyCollectedDataTypePurposes: ["NSPrivacyCollectedDataTypePurposeAppFunctionality"]
│
└─► NSPrivacyAccessedAPITypes (Array)
    ├─► NSPrivacyAccessedAPIType: "NSPrivacyAccessedAPICategoryUserDefaults"
    │   ├─ NSPrivacyAccessedAPITypeReasons: ["CA92.1"]
    │   └─ Reason: Accessing user defaults within app
    │
    └─► NSPrivacyAccessedAPIType: "NSPrivacyAccessedAPICategoryFileTimestamp"
        └─ NSPrivacyAccessedAPITypeReasons: ["C617.1"]
```

### Permission Architecture Pattern

```
┌──────────────────────────────────────────────────────────────┐
│              Permission Management Architecture              │
└──────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   UI Layer      │
│  (SwiftUI/UIKit)│
└────────┬────────┘
         │ Request Permission
         ▼
┌─────────────────────────┐
│  PermissionManager      │◄──── Singleton/Injectable
│  (Business Logic)       │
├─────────────────────────┤
│ • checkStatus()         │
│ • requestPermission()   │
│ • handleDenied()        │
│ • openSettings()        │
└────────┬────────────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Location     │ │ Photos       │ │ Camera       │ │ Notifications│
│ Service      │ │ Service      │ │ Service      │ │ Service      │
├──────────────┤ ├──────────────┤ ├──────────────┤ ├──────────────┤
│ CLLocation   │ │ PHPhoto      │ │ AVCapture    │ │ UNNotif      │
│ Manager      │ │ Library      │ │ Device       │ │ Center       │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Модель разрешений в iOS

### Основные принципы

iOS использует **opt-in модель** с тремя ключевыми компонентами:

1. **Декларативный этап** — Info.plist usage descriptions (compile-time)
2. **Манифест приватности** — PrivacyInfo.xcprivacy (iOS 17+, обязателен с 2024)
3. **Runtime-запрос** — System alert с пользовательским выбором

### Статусы разрешений

```swift
// Общие статусы для большинства разрешений
enum AuthorizationStatus {
    case notDetermined  // Пользователь еще не видел запрос
    case restricted     // Ограничено системой (MDM, Screen Time)
    case denied         // Пользователь явно отказал
    case authorized     // Полный доступ разрешен
    case limited        // Ограниченный доступ (Photos, iOS 14+)
}
```

## Info.plist Usage Descriptions

### Обязательные ключи

Apple **отклонит** приложение при App Review, если отсутствуют usage descriptions для используемых API.

```xml
<!-- Info.plist -->
<dict>
    <!-- Камера -->
    <key>NSCameraUsageDescription</key>
    <string>Нам нужен доступ к камере, чтобы вы могли фотографировать документы</string>

    <!-- Фото библиотека -->
    <key>NSPhotoLibraryUsageDescription</key>
    <string>Выберите фото для загрузки в профиль</string>

    <key>NSPhotoLibraryAddUsageDescription</key>
    <string>Сохраните отредактированное изображение в Фото</string>

    <!-- Геолокация -->
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>Мы используем вашу геолокацию для поиска ближайших ресторанов</string>

    <key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
    <string>Геолокация в фоне нужна для отслеживания пробежек</string>

    <!-- Микрофон -->
    <key>NSMicrophoneUsageDescription</key>
    <string>Запись голосовых сообщений требует доступа к микрофону</string>

    <!-- Контакты -->
    <key>NSContactsUsageDescription</key>
    <string>Найдите друзей из контактов, которые уже используют приложение</string>

    <!-- Календарь -->
    <key>NSCalendarsUsageDescription</key>
    <string>Добавьте встречи в ваш календарь</string>

    <!-- Напоминания -->
    <key>NSRemindersUsageDescription</key>
    <string>Создавайте напоминания о важных задачах</string>

    <!-- Motion & Fitness -->
    <key>NSMotionUsageDescription</key>
    <string>Отслеживание активности для подсчета шагов</string>

    <!-- Bluetooth -->
    <key>NSBluetoothAlwaysUsageDescription</key>
    <string>Подключение к фитнес-браслету для синхронизации данных</string>

    <!-- Face ID -->
    <key>NSFaceIDUsageDescription</key>
    <string>Используйте Face ID для быстрого входа в приложение</string>

    <!-- Siri -->
    <key>NSSiriUsageDescription</key>
    <string>Используйте Siri для голосового управления задачами</string>

    <!-- Speech Recognition -->
    <key>NSSpeechRecognitionUsageDescription</key>
    <string>Распознавание речи для голосового ввода</string>

    <!-- Media Library -->
    <key>NSAppleMusicUsageDescription</key>
    <string>Доступ к медиатеке для добавления музыки в плейлисты</string>
</dict>
```

### Лучшие практики текстов

1. **Конкретность** — объясните реальную пользу для пользователя
2. **Краткость** — 1-2 предложения, без технического жаргона
3. **Честность** — не обманывайте о целях использования
4. **Локализация** — переведите на все поддерживаемые языки

## Privacy Manifest (iOS 17+)

### Когда требуется

**Обязателен** с весны 2024 для приложений и SDK, использующих:

- Required Reason API (UserDefaults, file timestamps, system boot time, disk space, etc.)
- Tracking пользователей
- Third-party SDK с трекингом

### Создание Privacy Manifest

1. В Xcode: **File → New → File → App Privacy**
2. Сохраните как `PrivacyInfo.xcprivacy` в корне проекта
3. Заполните через Property List Editor или XML

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Использует ли приложение данные для трекинга -->
    <key>NSPrivacyTracking</key>
    <true/>

    <!-- Домены для трекинга -->
    <key>NSPrivacyTrackingDomains</key>
    <array>
        <string>analytics.example.com</string>
        <string>ads.partner.com</string>
    </array>

    <!-- Типы собираемых данных -->
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <dict>
            <key>NSPrivacyCollectedDataType</key>
            <string>NSPrivacyCollectedDataTypeLocation</string>
            <key>NSPrivacyCollectedDataTypeLinked</key>
            <true/>
            <key>NSPrivacyCollectedDataTypeTracking</key>
            <false/>
            <key>NSPrivacyCollectedDataTypePurposes</key>
            <array>
                <string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string>
            </array>
        </dict>
        <dict>
            <key>NSPrivacyCollectedDataType</key>
            <string>NSPrivacyCollectedDataTypeEmailAddress</string>
            <key>NSPrivacyCollectedDataTypeLinked</key>
            <true/>
            <key>NSPrivacyCollectedDataTypeTracking</key>
            <false/>
            <key>NSPrivacyCollectedDataTypePurposes</key>
            <array>
                <string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string>
            </array>
        </dict>
    </array>

    <!-- Required Reason API -->
    <key>NSPrivacyAccessedAPITypes</key>
    <array>
        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryUserDefaults</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>CA92.1</string>
            </array>
        </dict>
        <dict>
            <key>NSPrivacyAccessedAPIType</key>
            <string>NSPrivacyAccessedAPICategoryFileTimestamp</string>
            <key>NSPrivacyAccessedAPITypeReasons</key>
            <array>
                <string>C617.1</string>
            </array>
        </dict>
    </array>
</dict>
</plist>
```

### Required Reason API Codes

| API Category | Reason Code | Description |
|-------------|-------------|-------------|
| UserDefaults | CA92.1 | Доступ к user defaults внутри приложения |
| UserDefaults | 1C8F.1 | Доступ к shared user defaults в app group |
| File Timestamp | C617.1 | Timestamps для файлов, созданных приложением |
| File Timestamp | 3B52.1 | Timestamps для bug reporting |
| System Boot Time | 35F9.1 | Вычисление времени с последней перезагрузки |
| Disk Space | E174.1 | Запись больших файлов, проверка доступного места |
| Active Keyboards | 54BD.1 | Кастомная клавиатура |

## Запрос разрешений в Runtime

### Общая стратегия

1. **Проверить текущий статус** — не показывайте алерт повторно
2. **Контекстуальный запрос** — запрашивайте перед использованием функции
3. **Priming** — объясните пользу перед системным алертом
4. **Обработка результата** — graceful degradation при отказе

### Camera Permission

```swift
import AVFoundation

actor CameraPermissionManager {
    enum CameraError: LocalizedError {
        case notAuthorized
        case restricted
        case deviceNotAvailable

        var errorDescription: String? {
            switch self {
            case .notAuthorized:
                return "Доступ к камере запрещен. Разрешите доступ в Настройках."
            case .restricted:
                return "Камера недоступна из-за ограничений системы."
            case .deviceNotAvailable:
                return "Камера недоступна на этом устройстве."
            }
        }
    }

    func checkCameraPermission() -> AVAuthorizationStatus {
        AVCaptureDevice.authorizationStatus(for: .video)
    }

    func requestCameraAccess() async throws {
        let status = checkCameraPermission()

        switch status {
        case .notDetermined:
            let granted = await AVCaptureDevice.requestAccess(for: .video)
            if !granted {
                throw CameraError.notAuthorized
            }

        case .restricted:
            throw CameraError.restricted

        case .denied:
            throw CameraError.notAuthorized

        case .authorized:
            return

        @unknown default:
            throw CameraError.deviceNotAvailable
        }
    }
}

// SwiftUI Usage
struct CameraView: View {
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var showCamera = false
    @State private var showPrimer = true

    private let permissionManager = CameraPermissionManager()

    var body: some View {
        VStack {
            if showPrimer {
                primerView
            } else if showCamera {
                cameraView
            }
        }
        .alert("Ошибка доступа", isPresented: $showError) {
            Button("Настройки") {
                openSettings()
            }
            Button("Отмена", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
    }

    private var primerView: some View {
        VStack(spacing: 20) {
            Image(systemName: "camera.fill")
                .font(.system(size: 60))
                .foregroundStyle(.blue)

            Text("Фотографируйте документы")
                .font(.title2.bold())

            Text("Мы используем камеру только для сканирования документов. Фото не сохраняются без вашего согласия.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
                .padding(.horizontal)

            Button("Продолжить") {
                requestPermission()
            }
            .buttonStyle(.borderedProminent)
        }
        .padding()
    }

    private var cameraView: some View {
        Text("Camera View Here")
    }

    private func requestPermission() {
        Task {
            do {
                try await permissionManager.requestCameraAccess()
                await MainActor.run {
                    showPrimer = false
                    showCamera = true
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    showError = true
                }
            }
        }
    }

    private func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }
}
```

### Location Permissions

```swift
import CoreLocation

@MainActor
final class LocationPermissionManager: NSObject, ObservableObject {
    @Published var authorizationStatus: CLAuthorizationStatus = .notDetermined
    @Published var location: CLLocation?

    private let locationManager = CLLocationManager()

    override init() {
        super.init()
        locationManager.delegate = self
        authorizationStatus = locationManager.authorizationStatus
    }

    // "When In Use" - только когда приложение активно
    func requestWhenInUseAuthorization() {
        locationManager.requestWhenInUseAuthorization()
    }

    // "Always" - в фоне (требует "When In Use" сначала)
    func requestAlwaysAuthorization() {
        // iOS запросит "When In Use", затем через некоторое время предложит "Always"
        locationManager.requestAlwaysAuthorization()
    }

    func startUpdatingLocation() {
        guard authorizationStatus == .authorizedWhenInUse ||
              authorizationStatus == .authorizedAlways else {
            return
        }
        locationManager.startUpdatingLocation()
    }

    func stopUpdatingLocation() {
        locationManager.stopUpdatingLocation()
    }

    var isAuthorized: Bool {
        authorizationStatus == .authorizedWhenInUse ||
        authorizationStatus == .authorizedAlways
    }
}

extension LocationPermissionManager: CLLocationManagerDelegate {
    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorizationStatus = manager.authorizationStatus
    }

    func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        location = locations.last
    }

    func locationManager(_ manager: CLLocationManager, didFailWithError error: Error) {
        print("Location error: \(error.localizedDescription)")
    }
}

// SwiftUI Usage
struct LocationView: View {
    @StateObject private var locationManager = LocationPermissionManager()

    var body: some View {
        VStack(spacing: 20) {
            statusView

            if !locationManager.isAuthorized {
                Button("Запросить доступ к геолокации") {
                    locationManager.requestWhenInUseAuthorization()
                }
                .buttonStyle(.borderedProminent)
            }

            if let location = locationManager.location {
                VStack {
                    Text("Широта: \(location.coordinate.latitude)")
                    Text("Долгота: \(location.coordinate.longitude)")
                }
                .font(.caption)
            }
        }
        .padding()
        .onChange(of: locationManager.isAuthorized) { _, isAuthorized in
            if isAuthorized {
                locationManager.startUpdatingLocation()
            }
        }
    }

    @ViewBuilder
    private var statusView: some View {
        switch locationManager.authorizationStatus {
        case .notDetermined:
            Label("Статус не определен", systemImage: "location.slash")
        case .restricted:
            Label("Доступ ограничен системой", systemImage: "exclamationmark.triangle")
        case .denied:
            VStack {
                Label("Доступ запрещен", systemImage: "location.slash.fill")
                    .foregroundStyle(.red)
                Button("Открыть Настройки") {
                    openSettings()
                }
            }
        case .authorizedWhenInUse:
            Label("Доступ при использовании", systemImage: "location.fill")
                .foregroundStyle(.green)
        case .authorizedAlways:
            Label("Всегда доступ", systemImage: "location.fill")
                .foregroundStyle(.green)
        @unknown default:
            Label("Неизвестный статус", systemImage: "questionmark")
        }
    }

    private func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }
}
```

### Photo Library Access

```swift
import Photos
import PhotosUI
import SwiftUI

@MainActor
final class PhotoLibraryPermissionManager: ObservableObject {
    @Published var authorizationStatus: PHAuthorizationStatus = .notDetermined
    @Published var accessLevel: PHAccessLevel = .readWrite

    init() {
        checkCurrentStatus()
    }

    func checkCurrentStatus() {
        authorizationStatus = PHPhotoLibrary.authorizationStatus(for: accessLevel)
    }

    // iOS 14+: Limited Access - пользователь выбирает конкретные фото
    func requestAuthorization(for level: PHAccessLevel = .readWrite) async -> PHAuthorizationStatus {
        accessLevel = level
        let status = await PHPhotoLibrary.requestAuthorization(for: level)
        authorizationStatus = status
        return status
    }

    // Показать Limited Library Picker повторно
    func presentLimitedLibraryPicker(from viewController: UIViewController) {
        PHPhotoLibrary.shared().presentLimitedLibraryPicker(from: viewController)
    }

    var isAuthorized: Bool {
        authorizationStatus == .authorized || authorizationStatus == .limited
    }

    var isLimited: Bool {
        authorizationStatus == .limited
    }
}

// SwiftUI with PhotosPicker (iOS 16+)
struct PhotoPickerView: View {
    @StateObject private var permissionManager = PhotoLibraryPermissionManager()
    @State private var selectedItem: PhotosPickerItem?
    @State private var selectedImage: Image?
    @State private var showPermissionAlert = false

    var body: some View {
        VStack(spacing: 20) {
            if let selectedImage {
                selectedImage
                    .resizable()
                    .scaledToFit()
                    .frame(height: 300)
            } else {
                Image(systemName: "photo.on.rectangle.angled")
                    .font(.system(size: 100))
                    .foregroundStyle(.gray)
            }

            // iOS 16+ PhotosPicker автоматически запрашивает разрешения
            PhotosPicker(selection: $selectedItem, matching: .images) {
                Label("Выбрать фото", systemImage: "photo.on.rectangle")
            }
            .buttonStyle(.borderedProminent)
            .onChange(of: selectedItem) { _, newItem in
                Task {
                    if let data = try? await newItem?.loadTransferable(type: Data.self),
                       let uiImage = UIImage(data: data) {
                        selectedImage = Image(uiImage: uiImage)
                    }
                }
            }

            if permissionManager.isLimited {
                Button("Выбрать больше фото") {
                    // Показать Limited Library Picker
                    showPermissionAlert = true
                }
                .buttonStyle(.bordered)
            }

            statusBadge
        }
        .padding()
        .alert("Доступ к фото", isPresented: $showPermissionAlert) {
            Button("Управление доступом") {
                openSettings()
            }
            Button("Отмена", role: .cancel) {}
        } message: {
            Text("У приложения ограниченный доступ к вашим фото. Вы можете выбрать больше фото в настройках.")
        }
    }

    @ViewBuilder
    private var statusBadge: some View {
        switch permissionManager.authorizationStatus {
        case .limited:
            Label("Ограниченный доступ к фото", systemImage: "photo.badge.plus")
                .font(.caption)
                .foregroundStyle(.orange)
        case .authorized:
            Label("Полный доступ к фото", systemImage: "photo.fill")
                .font(.caption)
                .foregroundStyle(.green)
        case .denied, .restricted:
            Label("Доступ запрещен", systemImage: "photo.badge.exclamationmark")
                .font(.caption)
                .foregroundStyle(.red)
        case .notDetermined:
            Label("Доступ не запрошен", systemImage: "photo")
                .font(.caption)
                .foregroundStyle(.gray)
        @unknown default:
            EmptyView()
        }
    }

    private func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }
}
```

### Notifications Permission

```swift
import UserNotifications

@MainActor
final class NotificationPermissionManager: ObservableObject {
    @Published var authorizationStatus: UNAuthorizationStatus = .notDetermined
    @Published var notificationSettings: UNNotificationSettings?

    func checkNotificationSettings() async {
        let settings = await UNUserNotificationCenter.current().notificationSettings()
        notificationSettings = settings
        authorizationStatus = settings.authorizationStatus
    }

    func requestAuthorization() async throws -> Bool {
        let granted = try await UNUserNotificationCenter.current()
            .requestAuthorization(options: [.alert, .badge, .sound])

        await checkNotificationSettings()
        return granted
    }

    // Проверка конкретных настроек
    var canSendAlerts: Bool {
        notificationSettings?.alertSetting == .enabled
    }

    var canPlaySound: Bool {
        notificationSettings?.soundSetting == .enabled
    }

    var canUpdateBadge: Bool {
        notificationSettings?.badgeSetting == .enabled
    }

    var isAuthorized: Bool {
        authorizationStatus == .authorized || authorizationStatus == .provisional
    }
}

// SwiftUI Usage
struct NotificationSettingsView: View {
    @StateObject private var permissionManager = NotificationPermissionManager()

    var body: some View {
        List {
            Section {
                statusRow
            }

            Section {
                if !permissionManager.isAuthorized {
                    Button("Разрешить уведомления") {
                        Task {
                            try? await permissionManager.requestAuthorization()
                        }
                    }
                }

                if permissionManager.authorizationStatus == .denied {
                    Button("Открыть Настройки") {
                        openSettings()
                    }
                }
            }

            if let settings = permissionManager.notificationSettings {
                Section("Детали настроек") {
                    settingRow(title: "Алерты", enabled: settings.alertSetting == .enabled)
                    settingRow(title: "Звуки", enabled: settings.soundSetting == .enabled)
                    settingRow(title: "Бейджи", enabled: settings.badgeSetting == .enabled)
                    settingRow(title: "Lock Screen", enabled: settings.lockScreenSetting == .enabled)
                    settingRow(title: "Notification Center", enabled: settings.notificationCenterSetting == .enabled)
                }
            }
        }
        .task {
            await permissionManager.checkNotificationSettings()
        }
    }

    @ViewBuilder
    private var statusRow: some View {
        HStack {
            Text("Статус")
            Spacer()
            statusBadge
        }
    }

    @ViewBuilder
    private var statusBadge: some View {
        switch permissionManager.authorizationStatus {
        case .notDetermined:
            Label("Не определен", systemImage: "bell.slash")
                .foregroundStyle(.gray)
        case .denied:
            Label("Запрещены", systemImage: "bell.slash.fill")
                .foregroundStyle(.red)
        case .authorized:
            Label("Разрешены", systemImage: "bell.fill")
                .foregroundStyle(.green)
        case .provisional:
            Label("Тихие уведомления", systemImage: "bell.badge")
                .foregroundStyle(.orange)
        case .ephemeral:
            Label("Временные", systemImage: "bell")
                .foregroundStyle(.blue)
        @unknown default:
            Label("Неизвестно", systemImage: "questionmark")
        }
    }

    private func settingRow(title: String, enabled: Bool) -> some View {
        HStack {
            Text(title)
            Spacer()
            Image(systemName: enabled ? "checkmark.circle.fill" : "xmark.circle")
                .foregroundStyle(enabled ? .green : .red)
        }
    }

    private func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) {
            UIApplication.shared.open(url)
        }
    }
}
```

## App Tracking Transparency (ATT)

### Когда требуется

**Обязателен** для трекинга пользователей (iOS 14.5+):

- Показ таргетированной рекламы
- Передача данных брокерам данных
- Шаринг данных с партнерами для трекинга
- Использование advertising ID

### Реализация ATT

```swift
import AppTrackingTransparency
import AdSupport

@MainActor
final class TrackingPermissionManager: ObservableObject {
    @Published var trackingStatus: ATTrackingManager.AuthorizationStatus = .notDetermined
    @Published var advertisingIdentifier: UUID?

    func checkTrackingStatus() {
        trackingStatus = ATTrackingManager.trackingAuthorizationStatus
        updateAdvertisingID()
    }

    // Запрос должен происходить после applicationDidBecomeActive
    func requestTrackingAuthorization() async {
        trackingStatus = await ATTrackingManager.requestTrackingAuthorization()
        updateAdvertisingID()
    }

    private func updateAdvertisingID() {
        // IDFA доступен только если tracking authorized
        if trackingStatus == .authorized {
            advertisingIdentifier = ASIdentifierManager.shared().advertisingIdentifier
        } else {
            advertisingIdentifier = nil
        }
    }

    var canTrack: Bool {
        trackingStatus == .authorized
    }
}

// Info.plist
/*
<key>NSUserTrackingUsageDescription</key>
<string>Мы используем данные для показа персонализированной рекламы и улучшения вашего опыта</string>
*/

// SwiftUI Usage
struct ContentView: View {
    @StateObject private var trackingManager = TrackingPermissionManager()
    @State private var showTrackingPrompt = false

    var body: some View {
        VStack(spacing: 20) {
            Text("App Tracking Transparency")
                .font(.headline)

            statusView

            if trackingManager.trackingStatus == .notDetermined {
                Button("Запросить разрешение на трекинг") {
                    showTrackingPrompt = true
                }
                .buttonStyle(.borderedProminent)
            }

            if let idfa = trackingManager.advertisingIdentifier {
                Text("IDFA: \(idfa.uuidString)")
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .padding()
        .onAppear {
            trackingManager.checkTrackingStatus()
        }
        .alert("Персонализация опыта", isPresented: $showTrackingPrompt) {
            Button("Продолжить") {
                Task {
                    await trackingManager.requestTrackingAuthorization()
                }
            }
            Button("Не сейчас", role: .cancel) {}
        } message: {
            Text("Разрешите отслеживание для показа релевантной рекламы и улучшения вашего опыта в приложении.")
        }
    }

    @ViewBuilder
    private var statusView: some View {
        switch trackingManager.trackingStatus {
        case .notDetermined:
            Label("Статус не определен", systemImage: "questionmark.circle")
                .foregroundStyle(.gray)
        case .restricted:
            Label("Ограничено системой", systemImage: "exclamationmark.shield")
                .foregroundStyle(.orange)
        case .denied:
            Label("Трекинг запрещен", systemImage: "hand.raised.fill")
                .foregroundStyle(.red)
        case .authorized:
            Label("Трекинг разрешен", systemImage: "checkmark.shield.fill")
                .foregroundStyle(.green)
        @unknown default:
            Label("Неизвестный статус", systemImage: "questionmark")
        }
    }
}
```

## Keychain для безопасного хранения

### Что хранить в Keychain

- Пароли пользователей
- API токены и ключи
- Сертификаты и криптографические ключи
- Sensitive user data (SSN, credit cards)

**НЕ хранить:** обычные настройки, кеш, временные данные

### Keychain Wrapper

```swift
import Security
import Foundation

enum KeychainError: Error {
    case duplicateItem
    case itemNotFound
    case invalidItemFormat
    case unexpectedStatus(OSStatus)
}

actor KeychainManager {
    // Сохранить данные
    func save(_ data: Data, for key: String, withBiometry: Bool = false) throws {
        var query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        // Защита биометрией
        if withBiometry {
            let access = SecAccessControlCreateWithFlags(
                nil,
                kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
                .userPresence,
                nil
            )
            query[kSecAttrAccessControl as String] = access
        }

        let status = SecItemAdd(query as CFDictionary, nil)

        guard status != errSecDuplicateItem else {
            throw KeychainError.duplicateItem
        }

        guard status == errSecSuccess else {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    // Получить данные
    func retrieve(for key: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status != errSecItemNotFound else {
            throw KeychainError.itemNotFound
        }

        guard status == errSecSuccess else {
            throw KeychainError.unexpectedStatus(status)
        }

        guard let data = result as? Data else {
            throw KeychainError.invalidItemFormat
        }

        return data
    }

    // Обновить данные
    func update(_ data: Data, for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let attributes: [String: Any] = [
            kSecValueData as String: data
        ]

        let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)

        guard status != errSecItemNotFound else {
            throw KeychainError.itemNotFound
        }

        guard status == errSecSuccess else {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    // Удалить данные
    func delete(for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)

        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    // Удалить все данные приложения
    func deleteAll() throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword
        ]

        let status = SecItemDelete(query as CFDictionary)

        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }
}

// Convenience методы для String
extension KeychainManager {
    func save(_ string: String, for key: String, withBiometry: Bool = false) throws {
        guard let data = string.data(using: .utf8) else {
            throw KeychainError.invalidItemFormat
        }
        try save(data, for: key, withBiometry: withBiometry)
    }

    func retrieveString(for key: String) throws -> String {
        let data = try retrieve(for: key)
        guard let string = String(data: data, encoding: .utf8) else {
            throw KeychainError.invalidItemFormat
        }
        return string
    }
}

// Convenience методы для Codable
extension KeychainManager {
    func save<T: Encodable>(_ item: T, for key: String, withBiometry: Bool = false) throws {
        let data = try JSONEncoder().encode(item)
        try save(data, for: key, withBiometry: withBiometry)
    }

    func retrieve<T: Decodable>(for key: String, as type: T.Type) throws -> T {
        let data = try retrieve(for: key)
        return try JSONDecoder().decode(type, from: data)
    }
}

// Usage Example
struct User: Codable {
    let id: String
    let email: String
}

actor AuthenticationService {
    private let keychain = KeychainManager()
    private let tokenKey = "auth_token"
    private let userKey = "current_user"

    func saveAuthToken(_ token: String) async throws {
        try await keychain.save(token, for: tokenKey)
    }

    func getAuthToken() async throws -> String? {
        try? await keychain.retrieveString(for: tokenKey)
    }

    func saveUser(_ user: User) async throws {
        try await keychain.save(user, for: userKey)
    }

    func getCurrentUser() async throws -> User? {
        try? await keychain.retrieve(for: userKey, as: User.self)
    }

    func logout() async throws {
        try await keychain.delete(for: tokenKey)
        try await keychain.delete(for: userKey)
    }
}
```

### Keychain с биометрией

```swift
import LocalAuthentication

actor BiometricAuthManager {
    private let keychain = KeychainManager()
    private let context = LAContext()

    enum BiometricError: LocalizedError {
        case notAvailable
        case notEnrolled
        case authenticationFailed

        var errorDescription: String? {
            switch self {
            case .notAvailable:
                return "Биометрическая аутентификация недоступна на этом устройстве"
            case .notEnrolled:
                return "Биометрия не настроена. Настройте Face ID или Touch ID в Настройках."
            case .authenticationFailed:
                return "Аутентификация не удалась"
            }
        }
    }

    func canUseBiometrics() -> Bool {
        var error: NSError?
        return context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error)
    }

    func biometricType() -> LABiometryType {
        context.biometryType
    }

    func authenticateAndRetrieve(for key: String, reason: String) async throws -> Data {
        guard canUseBiometrics() else {
            throw BiometricError.notAvailable
        }

        let context = LAContext()
        context.localizedCancelTitle = "Отмена"
        context.localizedFallbackTitle = "Использовать пароль"

        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )

            guard success else {
                throw BiometricError.authenticationFailed
            }

            return try await keychain.retrieve(for: key)
        } catch let error as LAError {
            switch error.code {
            case .biometryNotAvailable:
                throw BiometricError.notAvailable
            case .biometryNotEnrolled:
                throw BiometricError.notEnrolled
            default:
                throw BiometricError.authenticationFailed
            }
        }
    }

    func saveWithBiometry(_ data: Data, for key: String) async throws {
        guard canUseBiometrics() else {
            throw BiometricError.notAvailable
        }

        try await keychain.save(data, for: key, withBiometry: true)
    }
}

// SwiftUI Usage
struct BiometricLoginView: View {
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var isAuthenticated = false

    private let biometricAuth = BiometricAuthManager()

    var body: some View {
        VStack(spacing: 30) {
            if isAuthenticated {
                Text("Добро пожаловать!")
                    .font(.largeTitle)
            } else {
                Image(systemName: biometricIcon)
                    .font(.system(size: 100))
                    .foregroundStyle(.blue)

                Text(biometricTitle)
                    .font(.title2)

                Button {
                    authenticate()
                } label: {
                    Label("Войти", systemImage: biometricIcon)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
            }
        }
        .alert("Ошибка", isPresented: $showError) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(errorMessage)
        }
    }

    private var biometricIcon: String {
        switch biometricAuth.biometricType() {
        case .faceID: return "faceid"
        case .touchID: return "touchid"
        case .opticID: return "opticid"
        case .none: return "lock.fill"
        @unknown default: return "lock.fill"
        }
    }

    private var biometricTitle: String {
        switch biometricAuth.biometricType() {
        case .faceID: return "Войти с Face ID"
        case .touchID: return "Войти с Touch ID"
        case .opticID: return "Войти с Optic ID"
        case .none: return "Войти"
        @unknown default: return "Войти"
        }
    }

    private func authenticate() {
        Task {
            do {
                let _ = try await biometricAuth.authenticateAndRetrieve(
                    for: "auth_token",
                    reason: "Войдите для доступа к вашему аккаунту"
                )
                await MainActor.run {
                    isAuthenticated = true
                }
            } catch {
                await MainActor.run {
                    errorMessage = error.localizedDescription
                    showError = true
                }
            }
        }
    }
}
```

## Entitlements система

### Что такое Entitlements

**Entitlements** — это key-value пары, которые дают приложению специальные возможности:

- App Groups — шаринг данных между приложениями
- Keychain Sharing — общий Keychain между приложениями
- Associated Domains — Universal Links, Handoff
- Push Notifications
- iCloud — CloudKit, iCloud Drive
- HealthKit, HomeKit, SiriKit
- Wireless Accessory Configuration
- Inter-App Audio

### Добавление Entitlements

1. **Xcode:** Target → Signing & Capabilities → + Capability
2. Создается файл `YourApp.entitlements`
3. Автоматически добавляется в App ID на Developer Portal

```xml
<!-- YourApp.entitlements -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- App Groups -->
    <key>com.apple.security.application-groups</key>
    <array>
        <string>group.com.yourcompany.yourapp</string>
    </array>

    <!-- Keychain Sharing -->
    <key>keychain-access-groups</key>
    <array>
        <string>$(AppIdentifierPrefix)com.yourcompany.yourapp</string>
        <string>$(AppIdentifierPrefix)com.yourcompany.sharedkeychain</string>
    </array>

    <!-- Associated Domains -->
    <key>com.apple.developer.associated-domains</key>
    <array>
        <string>applinks:yourwebsite.com</string>
        <string>webcredentials:yourwebsite.com</string>
    </array>

    <!-- Push Notifications -->
    <key>aps-environment</key>
    <string>production</string>

    <!-- iCloud -->
    <key>com.apple.developer.icloud-container-identifiers</key>
    <array>
        <string>iCloud.com.yourcompany.yourapp</string>
    </array>

    <key>com.apple.developer.ubiquity-kvstore-identifier</key>
    <string>$(TeamIdentifierPrefix)com.yourcompany.yourapp</string>

    <!-- HealthKit -->
    <key>com.apple.developer.healthkit</key>
    <true/>

    <key>com.apple.developer.healthkit.access</key>
    <array>
        <string>health-records</string>
    </array>

    <!-- Siri -->
    <key>com.apple.developer.siri</key>
    <true/>
</dict>
</plist>
```

### App Groups для шаринга данных

```swift
import Foundation

// Shared UserDefaults между приложениями
extension UserDefaults {
    static let shared = UserDefaults(suiteName: "group.com.yourcompany.yourapp")!
}

// Usage
UserDefaults.shared.set("value", forKey: "sharedKey")
let value = UserDefaults.shared.string(forKey: "sharedKey")

// Shared file container
class SharedFileManager {
    static let shared = SharedFileManager()

    private let appGroupID = "group.com.yourcompany.yourapp"

    var containerURL: URL? {
        FileManager.default.containerURL(forSecurityApplicationGroupIdentifier: appGroupID)
    }

    func saveData(_ data: Data, filename: String) throws {
        guard let containerURL else {
            throw NSError(domain: "SharedFileManager", code: -1, userInfo: [
                NSLocalizedDescriptionKey: "App Group container недоступен"
            ])
        }

        let fileURL = containerURL.appendingPathComponent(filename)
        try data.write(to: fileURL, options: .atomic)
    }

    func loadData(filename: String) throws -> Data {
        guard let containerURL else {
            throw NSError(domain: "SharedFileManager", code: -1, userInfo: [
                NSLocalizedDescriptionKey: "App Group container недоступен"
            ])
        }

        let fileURL = containerURL.appendingPathComponent(filename)
        return try Data(contentsOf: fileURL)
    }
}
```

## App Transport Security (ATS)

### Основные требования

**ATS по умолчанию требует:**

- HTTPS с TLS 1.2+
- Сертификаты от доверенных CA
- Forward secrecy ciphers (ECDHE)
- SHA-2 подписи сертификатов
- Минимум RSA 2048 бит или ECC 256 бит

### Конфигурация ATS

```xml
<!-- Info.plist -->
<dict>
    <key>NSAppTransportSecurity</key>
    <dict>
        <!-- Отключить ATS полностью (НЕ ДЕЛАЙТЕ ЭТО) -->
        <key>NSAllowsArbitraryLoads</key>
        <false/>

        <!-- Разрешить локальные подключения для разработки -->
        <key>NSAllowsLocalNetworking</key>
        <true/>

        <!-- Исключения для конкретных доменов -->
        <key>NSExceptionDomains</key>
        <dict>
            <!-- Legacy API без HTTPS -->
            <key>legacy-api.example.com</key>
            <dict>
                <key>NSExceptionAllowsInsecureHTTPLoads</key>
                <true/>
                <key>NSIncludesSubdomains</key>
                <true/>
                <!-- Обоснование для App Review -->
                <key>NSExceptionReasonKey</key>
                <string>Legacy API не поддерживает HTTPS, планируется миграция</string>
            </dict>

            <!-- Кастомный сертификат -->
            <key>internal.example.com</key>
            <dict>
                <key>NSExceptionRequiresForwardSecrecy</key>
                <false/>
                <key>NSExceptionMinimumTLSVersion</key>
                <string>TLSv1.2</string>
            </dict>
        </dict>
    </dict>
</dict>
```

### Certificate Pinning

```swift
import Foundation

class CertificatePinner: NSObject, URLSessionDelegate {
    private let pinnedCertificates: [Data]

    init(certificateNames: [String]) {
        var certificates: [Data] = []

        for name in certificateNames {
            if let certPath = Bundle.main.path(forResource: name, ofType: "cer"),
               let certData = try? Data(contentsOf: URL(fileURLWithPath: certPath)) {
                certificates.append(certData)
            }
        }

        self.pinnedCertificates = certificates
        super.init()
    }

    func urlSession(
        _ session: URLSession,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Получить сертификат сервера
        guard let serverCertificate = SecTrustCopyCertificateChain(serverTrust) as? [SecCertificate],
              let serverCertificateData = SecCertificateCopyData(serverCertificate[0]) as Data? else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Проверить против pinned сертификатов
        if pinnedCertificates.contains(serverCertificateData) {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}

// Usage
class SecureNetworkManager {
    private lazy var session: URLSession = {
        let configuration = URLSessionConfiguration.default
        let pinner = CertificatePinner(certificateNames: ["your-cert"])
        return URLSession(configuration: configuration, delegate: pinner, delegateQueue: nil)
    }()

    func request(url: URL) async throws -> Data {
        let (data, response) = try await session.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw URLError(.badServerResponse)
        }

        return data
    }
}
```

## Code Signing

### Основы

**Code Signing** гарантирует:

1. Приложение подписано известным разработчиком
2. Код не был изменен после подписания
3. Приложение имеет правильные entitlements

### Компоненты

```
Code Signing Components:

Developer Certificate
    ├─► Signing Certificate (.p12)
    └─► Private Key

Provisioning Profile
    ├─► App ID (com.yourcompany.yourapp)
    ├─► Certificates (разрешенные для подписи)
    ├─► Devices (для Development/Ad Hoc)
    └─► Entitlements

App Binary
    ├─► Code Signature (embedded)
    ├─► Provisioning Profile (embedded.mobileprovision)
    └─► Entitlements (from profile)
```

### Типы профилей

| Profile Type | Use Case | Devices | App Store | TestFlight |
|-------------|----------|---------|-----------|------------|
| Development | Xcode debugging | Registered only | No | No |
| Ad Hoc | Internal testing | Registered only (max 100) | No | No |
| App Store | Production | Unlimited | Yes | Yes |
| Enterprise | In-house distribution | Unlimited | No | No |

### Automatic Signing (Xcode)

```
Target → Signing & Capabilities

✓ Automatically manage signing
Team: Your Development Team
Bundle Identifier: com.yourcompany.yourapp

Xcode автоматически:
├─► Создает/обновляет App ID
├─► Генерирует Provisioning Profile
├─► Подписывает приложение
└─► Обновляет entitlements
```

### Manual Signing

```bash
# Проверить доступные identities
security find-identity -v -p codesigning

# Подписать приложение вручную
codesign --force --sign "iPhone Distribution: Your Company (TEAM_ID)" \
    --entitlements YourApp.entitlements \
    --timestamp \
    YourApp.app

# Верифицировать подпись
codesign --verify --verbose=4 YourApp.app

# Проверить entitlements
codesign --display --entitlements - YourApp.app
```

## 6 типичных ошибок

### ❌ Ошибка 1: Запрос разрешений без объяснения

```swift
// ПЛОХО: Немедленный запрос без контекста
struct CameraView: View {
    var body: some View {
        VStack {
            Text("Camera View")
        }
        .onAppear {
            AVCaptureDevice.requestAccess(for: .video) { _ in }
        }
    }
}
```

```swift
// ХОРОШО: Priming screen перед системным алертом
struct CameraView: View {
    @State private var showPrimer = true
    @State private var cameraAuthorized = false

    var body: some View {
        if showPrimer {
            VStack(spacing: 20) {
                Image(systemName: "camera.fill")
                    .font(.system(size: 60))

                Text("Фотографируйте документы")
                    .font(.title2.bold())

                Text("Камера используется только для сканирования документов. Ваши фото не сохраняются автоматически.")
                    .multilineTextAlignment(.center)
                    .foregroundStyle(.secondary)

                Button("Разрешить доступ к камере") {
                    requestCameraAccess()
                }
                .buttonStyle(.borderedProminent)

                Button("Не сейчас") {
                    showPrimer = false
                }
                .buttonStyle(.bordered)
            }
            .padding()
        } else if cameraAuthorized {
            // Camera UI
            Text("Camera Interface")
        }
    }

    private func requestCameraAccess() {
        Task {
            let granted = await AVCaptureDevice.requestAccess(for: .video)
            await MainActor.run {
                cameraAuthorized = granted
                showPrimer = false
            }
        }
    }
}
```

### ❌ Ошибка 2: Игнорирование denied статуса

```swift
// ПЛОХО: Нет обработки отказа
func requestLocationAccess() {
    locationManager.requestWhenInUseAuthorization()
    // Что если пользователь отказал?
}
```

```swift
// ХОРОШО: Graceful handling с deep link в настройки
@MainActor
final class LocationManager: NSObject, ObservableObject, CLLocationManagerDelegate {
    @Published var authorizationStatus: CLAuthorizationStatus = .notDetermined
    @Published var showSettingsAlert = false

    private let manager = CLLocationManager()

    override init() {
        super.init()
        manager.delegate = self
        authorizationStatus = manager.authorizationStatus
    }

    func requestAuthorization() {
        switch authorizationStatus {
        case .notDetermined:
            manager.requestWhenInUseAuthorization()
        case .denied, .restricted:
            showSettingsAlert = true
        case .authorizedWhenInUse, .authorizedAlways:
            break
        @unknown default:
            break
        }
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        authorizationStatus = manager.authorizationStatus

        if authorizationStatus == .denied {
            showSettingsAlert = true
        }
    }
}

struct LocationView: View {
    @StateObject private var locationManager = LocationManager()

    var body: some View {
        VStack {
            Button("Запросить геолокацию") {
                locationManager.requestAuthorization()
            }
        }
        .alert("Доступ к геолокации", isPresented: $locationManager.showSettingsAlert) {
            Button("Открыть Настройки") {
                if let url = URL(string: UIApplication.openSettingsURLString) {
                    UIApplication.shared.open(url)
                }
            }
            Button("Отмена", role: .cancel) {}
        } message: {
            Text("Для использования функций карты необходимо разрешить доступ к геолокации в Настройках приложения.")
        }
    }
}
```

### ❌ Ошибка 3: Отсутствие Info.plist descriptions

```swift
// ПЛОХО: Код есть, но Info.plist пустой
func requestCameraAccess() {
    AVCaptureDevice.requestAccess(for: .video) { granted in
        print("Granted: \(granted)")
    }
}
// ❌ App Review Rejection: Missing NSCameraUsageDescription
```

```swift
// ХОРОШО: Info.plist содержит все необходимые ключи
/*
Info.plist:
<key>NSCameraUsageDescription</key>
<string>Камера используется для сканирования документов и QR-кодов</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>Доступ к фото для загрузки изображений профиля</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Геолокация используется для поиска ближайших точек на карте</string>
*/

func requestCameraAccess() async throws {
    let granted = await AVCaptureDevice.requestAccess(for: .video)
    if !granted {
        throw CameraError.accessDenied
    }
}
```

### ❌ Ошибка 4: Хранение токенов в UserDefaults

```swift
// ПЛОХО: Sensitive данные в UserDefaults (небезопасно)
func saveAuthToken(_ token: String) {
    UserDefaults.standard.set(token, forKey: "auth_token")
}

func getAuthToken() -> String? {
    UserDefaults.standard.string(forKey: "auth_token")
}
// ❌ Токены могут быть извлечены из backup или дампа памяти
```

```swift
// ХОРОШО: Используйте Keychain для sensitive данных
actor SecureTokenManager {
    private let keychain = KeychainManager()
    private let tokenKey = "auth_token"

    func saveAuthToken(_ token: String) async throws {
        try await keychain.save(token, for: tokenKey)
    }

    func getAuthToken() async throws -> String? {
        try? await keychain.retrieveString(for: tokenKey)
    }

    func deleteAuthToken() async throws {
        try await keychain.delete(for: tokenKey)
    }
}

// Usage
let tokenManager = SecureTokenManager()
try await tokenManager.saveAuthToken("secret_token_123")
```

### ❌ Ошибка 5: Отсутствие Privacy Manifest (iOS 17+)

```swift
// ПЛОХО: Использование Required Reason API без манифеста
func checkDiskSpace() -> UInt64 {
    let fileURL = URL(fileURLWithPath: NSHomeDirectory())
    let values = try? fileURL.resourceValues(forKeys: [.volumeAvailableCapacityKey])
    return values?.volumeAvailableCapacity as? UInt64 ?? 0
}
// ❌ App Review Rejection: Missing Privacy Manifest для File System API
```

```swift
// ХОРОШО: Создан PrivacyInfo.xcprivacy с reason codes
/*
PrivacyInfo.xcprivacy:
<key>NSPrivacyAccessedAPITypes</key>
<array>
    <dict>
        <key>NSPrivacyAccessedAPIType</key>
        <string>NSPrivacyAccessedAPICategoryFileTimestamp</string>
        <key>NSPrivacyAccessedAPITypeReasons</key>
        <array>
            <string>C617.1</string>
        </array>
    </dict>
    <dict>
        <key>NSPrivacyAccessedAPIType</key>
        <string>NSPrivacyAccessedAPICategoryDiskSpace</string>
        <key>NSPrivacyAccessedAPITypeReasons</key>
        <array>
            <string>E174.1</string>
        </array>
    </dict>
</array>
*/

func checkDiskSpace() -> UInt64 {
    let fileURL = URL(fileURLWithPath: NSHomeDirectory())
    let values = try? fileURL.resourceValues(forKeys: [.volumeAvailableCapacityKey])
    return values?.volumeAvailableCapacity as? UInt64 ?? 0
}
// ✅ Privacy Manifest декларирует использование API
```

### ❌ Ошибка 6: Неправильный уровень Location разрешений

```swift
// ПЛОХО: Запрос "Always" сразу для простой функции
func requestLocationForRestaurantSearch() {
    locationManager.requestAlwaysAuthorization()
}
// ❌ Пользователи скорее всего откажут
// ❌ Apple может отклонить при review
```

```swift
// ХОРОШО: Минимально необходимый уровень доступа
func requestLocationForRestaurantSearch() {
    // "When In Use" достаточно для поиска ресторанов
    locationManager.requestWhenInUseAuthorization()
}

// Запрашивайте "Always" только для фоновых функций
func requestLocationForRunTracking() {
    // Сначала "When In Use"
    if locationManager.authorizationStatus == .notDetermined {
        locationManager.requestWhenInUseAuthorization()
        return
    }

    // Затем объясните зачем нужен "Always"
    showAlwaysAuthorizationExplanation { userConfirmed in
        if userConfirmed {
            locationManager.requestAlwaysAuthorization()
        }
    }
}

func showAlwaysAuthorizationExplanation(completion: @escaping (Bool) -> Void) {
    // Показать UI с объяснением:
    // "Для отслеживания пробежек в фоне требуется разрешение 'Всегда'.
    // Мы используем геолокацию только во время тренировок."
}
```

## Лучшие практики

### 1. Just-in-Time запросы

Запрашивайте разрешения **непосредственно перед использованием** функции, а не при запуске приложения.

### 2. Прозрачность и честность

Четко объясняйте, **зачем** нужно разрешение и **как** будут использоваться данные.

### 3. Минимально необходимый доступ

- Location: "When In Use" вместо "Always" если возможно
- Photos: Limited Access по умолчанию
- Не запрашивайте разрешения "про запас"

### 4. Graceful degradation

Приложение должно **работать без разрешений**, с ограниченным функционалом.

### 5. Privacy-first подход

- Используйте on-device обработку где возможно
- Не собирайте больше данных, чем необходимо
- Предоставьте возможность удалить данные
- Регулярно пересматривайте Privacy Manifest

### 6. Тестирование всех сценариев

```swift
// Тестируйте все статусы разрешений
enum PermissionTestScenarios {
    case notDetermined    // Первый запуск
    case authorized       // Разрешено
    case denied           // Отказано пользователем
    case restricted       // Ограничено системой
    case limited          // Ограниченный доступ (Photos)
}
```

### 7. Мониторинг изменений

```swift
// Отслеживайте изменения разрешений
NotificationCenter.default.addObserver(
    forName: UIApplication.didBecomeActiveNotification,
    object: nil,
    queue: .main
) { _ in
    // Проверить статусы разрешений
    checkAllPermissions()
}
```

### 8. Документация для App Review

Подготовьте для App Review:

- Объяснение каждого используемого разрешения
- Screenshots priming screens
- Тестовый аккаунт если требуется авторизация
- Инструкции по воспроизведению функций с разрешениями

## Связь с другими темами

**[[android-permissions-security]]** — Android и iOS используют фундаментально разные модели разрешений: Android предоставляет runtime permissions с granular контролем (location accuracy, media selection), тогда как iOS акцентирует privacy через Info.plist descriptions, Privacy Manifest и принцип минимально необходимого доступа. Сравнение помогает понять, что iOS более строг в отношении пользовательских данных (нет аналога WRITE_EXTERNAL_STORAGE), но обе платформы движутся к privacy-first подходу. Рекомендуется для кросс-платформенных разработчиков.

**[[ios-app-components]]** — система разрешений тесно интегрирована с жизненным циклом приложения: AppDelegate/SceneDelegate обрабатывает changes authorization status, Background Modes требуют соответствующих entitlements, а Extension targets имеют собственные наборы разрешений. Без понимания app components невозможно правильно настроить разрешения для различных extension-ов (Notification Service, Widget, Share Extension).

**[[ios-notifications]]** — push-уведомления требуют отдельного разрешения через UNUserNotificationCenter.requestAuthorization, а App Tracking Transparency (ATT) влияет на возможность таргетирования push-кампаний. Правильная стратегия запроса notification permissions (priming screen перед системным алертом) может увеличить opt-in rate на 30-50%. Изучение обеих тем необходимо для построения эффективной notification-стратегии.

---

## Источники и дальнейшее чтение

### Книги
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — подробно описывает систему разрешений iOS, Info.plist ключи, Keychain Services и App Transport Security; обязательна для понимания security-модели платформы.
- Keur C., Hillegass A. (2020). *iOS Programming: Big Nerd Ranch Guide.* — практические примеры запроса разрешений камеры, геолокации и фотобиблиотеки с правильной обработкой всех статусов авторизации.
- Apple (2023). *The Swift Programming Language.* — описывает access control модификаторы (public, internal, private), которые являются частью общей security-модели Swift-приложений.

### Документация
- [Requesting Authorization for Media Capture](https://developer.apple.com/documentation/avfoundation/capture_setup/requesting_authorization_for_media_capture)
- [Protecting User Privacy](https://developer.apple.com/documentation/uikit/protecting_the_user_s_privacy)
- [Privacy Manifest Requirements](https://developer.apple.com/documentation/bundleresources/privacy_manifest_files)
- [App Tracking Transparency](https://developer.apple.com/documentation/apptrackingtransparency)

---

## Проверь себя

> [!question]- Почему iOS требует текстовое описание (Usage Description) в Info.plist для каждого разрешения, и что происходит без него?
> Apple требует объяснить пользователю зачем нужен доступ. Без ключа в Info.plist (например NSCameraUsageDescription) приложение упадет с crash при попытке запросить разрешение. App Review отклонит приложение с непонятными описаниями. Описание должно быть конкретным: "Для сканирования QR-кодов", а не "Нужен доступ к камере".

> [!question]- Что такое Privacy Manifest (iOS 17+) и какие последствия его отсутствия?
> Privacy Manifest (PrivacyInfo.xcprivacy) -- декларация используемых Required Reason APIs (UserDefaults timestamps, disk space, system boot time, file timestamps) и трекинговых доменов. Без него: App Store Connect warnings, с весны 2024 -- потенциальное отклонение. Нужен для приложения и каждого SDK. Apple может проверить соответствие declared vs actual usage.

> [!question]- Сценарий: пользователь отклонил запрос геолокации. Как правильно обработать отказ и мотивировать повторное разрешение?
> Нельзя показать системный алерт повторно (iOS показывает его один раз). Решение: 1) Показать объяснение перед запросом (pre-permission screen). 2) При отказе -- показать ненавязчивый баннер с объяснением ценности и кнопкой "Открыть Настройки" (UIApplication.openSettingsURL). 3) Деградировать gracefully -- показать альтернативный UI без геолокации. Никогда не блокировать основной функционал.

---

## Ключевые карточки

Какие типы разрешений существуют в iOS?
?
Runtime permissions (камера, микрофон, геолокация, контакты, фото) -- системный алерт. Info.plist only (Bluetooth, Local Network) -- системный алерт без кода запроса. Entitlements (Push, iCloud, HealthKit) -- настраиваются в capabilities. App Tracking Transparency -- отдельный фреймворк для трекинга.

Что такое App Tracking Transparency (ATT)?
?
Фреймворк (iOS 14.5+), требующий явного согласия пользователя на трекинг (IDFA). requestTrackingAuthorization показывает системный алерт. ~75% пользователей отклоняют. Без согласия: IDFA = нули. Влияет на рекламу, аналитику, attribution. Нужен NSUserTrackingUsageDescription в Info.plist.

Как Keychain обеспечивает безопасность данных?
?
Keychain шифрует данные ключом, привязанным к Secure Enclave (аппаратный чип). Данные не попадают в незашифрованные бэкапы. Access control: kSecAttrAccessible определяет когда данные доступны (WhenUnlocked, AfterFirstUnlock, Always). Поддерживает biometric authentication (Face ID/Touch ID) через SecAccessControl.

Что такое App Transport Security (ATS)?
?
Требование использовать HTTPS для всех сетевых соединений (iOS 9+). TLS 1.2+, forward secrecy. Исключения через Info.plist NSAppTransportSecurity: NSAllowsArbitraryLoads (все HTTP), NSExceptionDomains (конкретные домены). App Review проверяет обоснованность исключений.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-data-persistence]] | Безопасное хранение данных (Keychain) |
| Углубиться | [[mobile-security-owasp]] | OWASP Mobile Security для глубокого аудита |
| Смежная тема | [[android-permissions-security]] | Система разрешений Android для сравнения |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |
