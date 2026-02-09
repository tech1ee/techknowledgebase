---
title: "Cross-Platform: Permissions — Privacy Manifest vs Runtime Permissions"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - permissions
  - privacy
  - topic/security
  - type/comparison
  - level/intermediate
---

# Cross-Platform: Permissions — Privacy Manifest vs Runtime Permissions

## TL;DR

| Аспект | iOS | Android |
|--------|-----|---------|
| **Модель** | Декларативная + Runtime | Runtime-first |
| **Конфигурация** | Info.plist + PrivacyInfo.xcprivacy | AndroidManifest.xml |
| **Когда запрашивать** | При первом использовании | При первом использовании (API 23+) |
| **Отзыв разрешений** | Настройки системы | Настройки + автоотзыв (API 30+) |
| **Dangerous permissions** | Все требуют runtime-запроса | Только dangerous group |
| **Privacy Manifest** | Обязателен (iOS 17+) | Нет аналога |
| **ATT (реклама)** | Обязателен для трекинга | Нет прямого аналога |
| **Rationale UI** | Системный alert | Кастомный UI рекомендован |
| **Группировка** | Нет | Permission groups |
| **Фоновые разрешения** | Отдельный запрос | Отдельный запрос (API 29+) |

---

## iOS: Info.plist + Privacy Manifest + ATT

### Info.plist — Декларация намерений

Info.plist содержит **Usage Description** строки — обязательное объяснение, зачем приложению нужно разрешение.

```xml
<!-- Info.plist -->
<key>NSCameraUsageDescription</key>
<string>Камера нужна для сканирования QR-кодов</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>Геолокация используется для показа ближайших магазинов</string>

<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>Фоновая геолокация нужна для уведомлений о скидках рядом</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>Доступ к фото для выбора аватара профиля</string>

<key>NSMicrophoneUsageDescription</key>
<string>Микрофон используется для голосовых сообщений</string>

<key>NSUserTrackingUsageDescription</key>
<string>Данные используются для персонализации рекламы</string>
```

### Privacy Manifest (iOS 17+) — PrivacyInfo.xcprivacy

Apple ввёл **Privacy Manifest** для прозрачности сбора данных. Это декларация того, какие данные собирает приложение и зачем.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Типы собираемых данных -->
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <dict>
            <key>NSPrivacyCollectedDataType</key>
            <string>NSPrivacyCollectedDataTypePreciseLocation</string>
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

    <!-- Required Reason APIs -->
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

    <!-- Tracking Domains -->
    <key>NSPrivacyTrackingDomains</key>
    <array>
        <string>analytics.example.com</string>
    </array>

    <key>NSPrivacyTracking</key>
    <false/>
</dict>
</plist>
```

### App Tracking Transparency (ATT)

ATT — отдельный фреймворк для запроса разрешения на трекинг пользователя.

```swift
import AppTrackingTransparency
import AdSupport

class TrackingManager {

    func requestTrackingPermission() async -> Bool {
        // Проверяем текущий статус
        let currentStatus = ATTrackingManager.trackingAuthorizationStatus

        switch currentStatus {
        case .notDetermined:
            // Запрашиваем разрешение
            let status = await ATTrackingManager.requestTrackingAuthorization()
            return status == .authorized

        case .authorized:
            return true

        case .denied, .restricted:
            return false

        @unknown default:
            return false
        }
    }

    var advertisingIdentifier: String? {
        guard ATTrackingManager.trackingAuthorizationStatus == .authorized else {
            return nil
        }

        let idfa = ASIdentifierManager.shared().advertisingIdentifier
        // Проверяем, что IDFA не нулевой
        guard idfa.uuidString != "00000000-0000-0000-0000-000000000000" else {
            return nil
        }

        return idfa.uuidString
    }
}
```

### Runtime Permission Request (iOS)

```swift
import AVFoundation
import CoreLocation
import Photos
import UserNotifications

// MARK: - Camera Permission

class CameraPermissionHandler {

    func checkCameraPermission() -> AVAuthorizationStatus {
        AVCaptureDevice.authorizationStatus(for: .video)
    }

    func requestCameraPermission() async -> Bool {
        let status = checkCameraPermission()

        switch status {
        case .notDetermined:
            return await AVCaptureDevice.requestAccess(for: .video)

        case .authorized:
            return true

        case .denied, .restricted:
            // Направляем в настройки
            await openSettings()
            return false

        @unknown default:
            return false
        }
    }

    @MainActor
    private func openSettings() {
        guard let settingsURL = URL(string: UIApplication.openSettingsURLString) else {
            return
        }
        UIApplication.shared.open(settingsURL)
    }
}

// MARK: - Location Permission

class LocationPermissionHandler: NSObject, CLLocationManagerDelegate {

    private let locationManager = CLLocationManager()
    private var permissionContinuation: CheckedContinuation<CLAuthorizationStatus, Never>?

    override init() {
        super.init()
        locationManager.delegate = self
    }

    func requestWhenInUsePermission() async -> CLAuthorizationStatus {
        let currentStatus = locationManager.authorizationStatus

        guard currentStatus == .notDetermined else {
            return currentStatus
        }

        return await withCheckedContinuation { continuation in
            self.permissionContinuation = continuation
            locationManager.requestWhenInUseAuthorization()
        }
    }

    func requestAlwaysPermission() async -> CLAuthorizationStatus {
        let currentStatus = locationManager.authorizationStatus

        // Сначала нужно получить whenInUse
        guard currentStatus == .authorizedWhenInUse else {
            return await requestWhenInUsePermission()
        }

        return await withCheckedContinuation { continuation in
            self.permissionContinuation = continuation
            locationManager.requestAlwaysAuthorization()
        }
    }

    func locationManagerDidChangeAuthorization(_ manager: CLLocationManager) {
        permissionContinuation?.resume(returning: manager.authorizationStatus)
        permissionContinuation = nil
    }
}
```

---

## Android: Runtime Permissions + Rationale

### AndroidManifest.xml — Декларация

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Normal Permissions (автоматически выдаются) -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.VIBRATE" />

    <!-- Dangerous Permissions (требуют runtime-запроса) -->
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
        android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />

    <!-- Background Location (отдельный запрос, API 29+) -->
    <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />

    <!-- Notifications (API 33+) -->
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />

    <!-- Hardware Features -->
    <uses-feature
        android:name="android.hardware.camera"
        android:required="false" />
    <uses-feature
        android:name="android.hardware.location.gps"
        android:required="false" />

</manifest>
```

### Runtime Permission Request (Android)

```kotlin
import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume

// MARK: - Permission Result

sealed class PermissionResult {
    data object Granted : PermissionResult()
    data object Denied : PermissionResult()
    data object PermanentlyDenied : PermissionResult()
}

// MARK: - Permission Handler

class PermissionHandler(private val activity: ComponentActivity) {

    private var permissionCallback: ((Boolean) -> Unit)? = null

    private val permissionLauncher = activity.registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        permissionCallback?.invoke(isGranted)
        permissionCallback = null
    }

    private val multiplePermissionsLauncher = activity.registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        // Обрабатываем результат
    }

    // Проверка одного разрешения
    fun isPermissionGranted(permission: String): Boolean {
        return ContextCompat.checkSelfPermission(
            activity,
            permission
        ) == PackageManager.PERMISSION_GRANTED
    }

    // Проверка, нужно ли показать rationale
    fun shouldShowRationale(permission: String): Boolean {
        return activity.shouldShowRequestPermissionRationale(permission)
    }

    // Запрос одного разрешения
    suspend fun requestPermission(permission: String): PermissionResult {
        // Уже выдано
        if (isPermissionGranted(permission)) {
            return PermissionResult.Granted
        }

        // Запрашиваем
        val isGranted = suspendCancellableCoroutine { continuation ->
            permissionCallback = { granted ->
                continuation.resume(granted)
            }
            permissionLauncher.launch(permission)
        }

        return when {
            isGranted -> PermissionResult.Granted
            shouldShowRationale(permission) -> PermissionResult.Denied
            else -> PermissionResult.PermanentlyDenied
        }
    }

    // Открыть настройки приложения
    fun openAppSettings() {
        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.fromParts("package", activity.packageName, null)
        }
        activity.startActivity(intent)
    }
}

// MARK: - Camera Permission

class CameraPermissionManager(
    private val handler: PermissionHandler,
    private val context: Context
) {
    private val _permissionState = MutableStateFlow<PermissionResult?>(null)
    val permissionState: StateFlow<PermissionResult?> = _permissionState

    suspend fun requestCameraPermission(): PermissionResult {
        val result = handler.requestPermission(Manifest.permission.CAMERA)
        _permissionState.value = result
        return result
    }

    fun hasCameraPermission(): Boolean {
        return handler.isPermissionGranted(Manifest.permission.CAMERA)
    }
}

// MARK: - Location Permission

class LocationPermissionManager(private val handler: PermissionHandler) {

    suspend fun requestFineLocation(): PermissionResult {
        // Сначала проверяем coarse, потом fine
        val coarseResult = handler.requestPermission(
            Manifest.permission.ACCESS_COARSE_LOCATION
        )

        if (coarseResult != PermissionResult.Granted) {
            return coarseResult
        }

        return handler.requestPermission(
            Manifest.permission.ACCESS_FINE_LOCATION
        )
    }

    suspend fun requestBackgroundLocation(): PermissionResult {
        // Background location требует сначала foreground
        if (!handler.isPermissionGranted(Manifest.permission.ACCESS_FINE_LOCATION)) {
            val foregroundResult = requestFineLocation()
            if (foregroundResult != PermissionResult.Granted) {
                return foregroundResult
            }
        }

        // На Android 10+ background запрашивается отдельно
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            handler.requestPermission(
                Manifest.permission.ACCESS_BACKGROUND_LOCATION
            )
        } else {
            PermissionResult.Granted
        }
    }
}

// MARK: - Notification Permission (API 33+)

class NotificationPermissionManager(private val handler: PermissionHandler) {

    suspend fun requestNotificationPermission(): PermissionResult {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            handler.requestPermission(Manifest.permission.POST_NOTIFICATIONS)
        } else {
            // До Android 13 разрешение не требуется
            PermissionResult.Granted
        }
    }
}
```

### Rationale UI Pattern

```kotlin
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@Composable
fun PermissionRationaleDialog(
    permission: String,
    rationale: String,
    onConfirm: () -> Unit,
    onDismiss: () -> Unit
) {
    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text("Требуется разрешение")
        },
        text = {
            Text(rationale)
        },
        confirmButton = {
            TextButton(onClick = onConfirm) {
                Text("Разрешить")
            }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) {
                Text("Отмена")
            }
        }
    )
}

@Composable
fun PermissionDeniedCard(
    title: String,
    description: String,
    onOpenSettings: () -> Unit
) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = description,
                style = MaterialTheme.typography.bodyMedium
            )
            Spacer(modifier = Modifier.height(16.dp))
            Button(onClick = onOpenSettings) {
                Text("Открыть настройки")
            }
        }
    }
}
```

---

## Сравнение по типам разрешений

### Camera / Камера

| Аспект | iOS | Android |
|--------|-----|---------|
| **Манифест** | `NSCameraUsageDescription` | `android.permission.CAMERA` |
| **API** | `AVCaptureDevice.requestAccess` | `ActivityResultContracts.RequestPermission` |
| **Статусы** | authorized, denied, restricted, notDetermined | granted, denied |
| **Повторный запрос** | Нет (только через настройки) | Да, пока не "Don't ask again" |

**Swift:**
```swift
let status = AVCaptureDevice.authorizationStatus(for: .video)
let granted = await AVCaptureDevice.requestAccess(for: .video)
```

**Kotlin:**
```kotlin
val granted = ContextCompat.checkSelfPermission(
    context,
    Manifest.permission.CAMERA
) == PackageManager.PERMISSION_GRANTED
```

### Location / Геолокация

| Аспект | iOS | Android |
|--------|-----|---------|
| **Foreground** | `requestWhenInUseAuthorization()` | `ACCESS_FINE_LOCATION` / `ACCESS_COARSE_LOCATION` |
| **Background** | `requestAlwaysAuthorization()` | `ACCESS_BACKGROUND_LOCATION` (отдельно, API 29+) |
| **Точность** | Approximate (iOS 14+) vs Precise | Coarse vs Fine |
| **Индикатор** | Синяя стрелка в статус-баре | Иконка в статус-баре |

**Swift:**
```swift
// Foreground
locationManager.requestWhenInUseAuthorization()

// Background (после получения whenInUse)
locationManager.requestAlwaysAuthorization()

// Проверка точности (iOS 14+)
switch locationManager.accuracyAuthorization {
case .fullAccuracy:
    print("Точная геолокация")
case .reducedAccuracy:
    print("Приблизительная геолокация")
@unknown default:
    break
}
```

**Kotlin:**
```kotlin
// Foreground
val fineLocation = handler.requestPermission(
    Manifest.permission.ACCESS_FINE_LOCATION
)

// Background (отдельный запрос на Android 10+)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
    handler.requestPermission(
        Manifest.permission.ACCESS_BACKGROUND_LOCATION
    )
}
```

### Notifications / Уведомления

| Аспект | iOS | Android |
|--------|-----|---------|
| **Требуется разрешение** | Всегда | API 33+ (Android 13+) |
| **API** | `UNUserNotificationCenter` | `POST_NOTIFICATIONS` |
| **Provisional** | Да (тихие уведомления) | Нет |

**Swift:**
```swift
let center = UNUserNotificationCenter.current()

// Проверка статуса
let settings = await center.notificationSettings()

// Запрос разрешения
let granted = try await center.requestAuthorization(
    options: [.alert, .badge, .sound]
)

// Provisional (iOS 12+) — тихие уведомления без запроса
let provisionalGranted = try await center.requestAuthorization(
    options: [.alert, .badge, .sound, .provisional]
)
```

**Kotlin:**
```kotlin
// Android 13+ (API 33)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    val result = handler.requestPermission(
        Manifest.permission.POST_NOTIFICATIONS
    )
}

// Для более старых версий — создаём notification channel
val channel = NotificationChannel(
    "channel_id",
    "Channel Name",
    NotificationManager.IMPORTANCE_DEFAULT
)
notificationManager.createNotificationChannel(channel)
```

---

## KMP Handling с expect/actual

### Общий интерфейс

```kotlin
// commonMain/src/permissions/PermissionManager.kt

enum class Permission {
    CAMERA,
    LOCATION_FOREGROUND,
    LOCATION_BACKGROUND,
    NOTIFICATIONS,
    PHOTO_LIBRARY,
    MICROPHONE
}

enum class PermissionStatus {
    GRANTED,
    DENIED,
    NOT_DETERMINED,  // Только iOS
    RESTRICTED,      // Только iOS
    PERMANENTLY_DENIED
}

expect class PermissionManager {
    suspend fun checkPermission(permission: Permission): PermissionStatus
    suspend fun requestPermission(permission: Permission): PermissionStatus
    fun openSettings()
}
```

### iOS Implementation

```kotlin
// iosMain/src/permissions/PermissionManager.ios.kt

import platform.AVFoundation.*
import platform.CoreLocation.*
import platform.Photos.*
import platform.UserNotifications.*
import platform.UIKit.UIApplication
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlin.coroutines.resume

actual class PermissionManager {

    private val locationManager = CLLocationManager()

    actual suspend fun checkPermission(permission: Permission): PermissionStatus {
        return when (permission) {
            Permission.CAMERA -> checkCameraPermission()
            Permission.LOCATION_FOREGROUND -> checkLocationPermission()
            Permission.LOCATION_BACKGROUND -> checkLocationPermission()
            Permission.NOTIFICATIONS -> checkNotificationPermission()
            Permission.PHOTO_LIBRARY -> checkPhotoLibraryPermission()
            Permission.MICROPHONE -> checkMicrophonePermission()
        }
    }

    actual suspend fun requestPermission(permission: Permission): PermissionStatus {
        return when (permission) {
            Permission.CAMERA -> requestCameraPermission()
            Permission.LOCATION_FOREGROUND -> requestLocationPermission(always = false)
            Permission.LOCATION_BACKGROUND -> requestLocationPermission(always = true)
            Permission.NOTIFICATIONS -> requestNotificationPermission()
            Permission.PHOTO_LIBRARY -> requestPhotoLibraryPermission()
            Permission.MICROPHONE -> requestMicrophonePermission()
        }
    }

    actual fun openSettings() {
        val url = platform.Foundation.NSURL.URLWithString(
            UIApplicationOpenSettingsURLString
        ) ?: return
        UIApplication.sharedApplication.openURL(url)
    }

    // Camera
    private fun checkCameraPermission(): PermissionStatus {
        return when (AVCaptureDevice.authorizationStatusForMediaType(AVMediaTypeVideo)) {
            AVAuthorizationStatusAuthorized -> PermissionStatus.GRANTED
            AVAuthorizationStatusDenied -> PermissionStatus.DENIED
            AVAuthorizationStatusRestricted -> PermissionStatus.RESTRICTED
            AVAuthorizationStatusNotDetermined -> PermissionStatus.NOT_DETERMINED
            else -> PermissionStatus.DENIED
        }
    }

    private suspend fun requestCameraPermission(): PermissionStatus {
        if (checkCameraPermission() != PermissionStatus.NOT_DETERMINED) {
            return checkCameraPermission()
        }

        return suspendCancellableCoroutine { continuation ->
            AVCaptureDevice.requestAccessForMediaType(AVMediaTypeVideo) { granted ->
                val status = if (granted) {
                    PermissionStatus.GRANTED
                } else {
                    PermissionStatus.DENIED
                }
                continuation.resume(status)
            }
        }
    }

    // Location
    private fun checkLocationPermission(): PermissionStatus {
        return when (locationManager.authorizationStatus) {
            kCLAuthorizationStatusAuthorizedWhenInUse,
            kCLAuthorizationStatusAuthorizedAlways -> PermissionStatus.GRANTED
            kCLAuthorizationStatusDenied -> PermissionStatus.DENIED
            kCLAuthorizationStatusRestricted -> PermissionStatus.RESTRICTED
            kCLAuthorizationStatusNotDetermined -> PermissionStatus.NOT_DETERMINED
            else -> PermissionStatus.DENIED
        }
    }

    private suspend fun requestLocationPermission(always: Boolean): PermissionStatus {
        // Реализация через делегат CLLocationManager
        if (always) {
            locationManager.requestAlwaysAuthorization()
        } else {
            locationManager.requestWhenInUseAuthorization()
        }
        return checkLocationPermission()
    }

    // Notifications
    private suspend fun checkNotificationPermission(): PermissionStatus {
        return suspendCancellableCoroutine { continuation ->
            UNUserNotificationCenter.currentNotificationCenter()
                .getNotificationSettingsWithCompletionHandler { settings ->
                    val status = when (settings?.authorizationStatus) {
                        UNAuthorizationStatusAuthorized -> PermissionStatus.GRANTED
                        UNAuthorizationStatusDenied -> PermissionStatus.DENIED
                        UNAuthorizationStatusNotDetermined -> PermissionStatus.NOT_DETERMINED
                        else -> PermissionStatus.DENIED
                    }
                    continuation.resume(status)
                }
        }
    }

    private suspend fun requestNotificationPermission(): PermissionStatus {
        return suspendCancellableCoroutine { continuation ->
            UNUserNotificationCenter.currentNotificationCenter()
                .requestAuthorizationWithOptions(
                    UNAuthorizationOptionAlert or
                    UNAuthorizationOptionBadge or
                    UNAuthorizationOptionSound
                ) { granted, _ ->
                    val status = if (granted) {
                        PermissionStatus.GRANTED
                    } else {
                        PermissionStatus.DENIED
                    }
                    continuation.resume(status)
                }
        }
    }

    // Photo Library & Microphone — аналогично
    private fun checkPhotoLibraryPermission(): PermissionStatus = TODO()
    private suspend fun requestPhotoLibraryPermission(): PermissionStatus = TODO()
    private fun checkMicrophonePermission(): PermissionStatus = TODO()
    private suspend fun requestMicrophonePermission(): PermissionStatus = TODO()
}
```

### Android Implementation

```kotlin
// androidMain/src/permissions/PermissionManager.android.kt

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.core.content.ContextCompat

actual class PermissionManager(
    private val context: Context,
    private val activityProvider: () -> androidx.activity.ComponentActivity
) {

    actual suspend fun checkPermission(permission: Permission): PermissionStatus {
        val androidPermission = permission.toAndroidPermission()

        return if (ContextCompat.checkSelfPermission(
            context,
            androidPermission
        ) == PackageManager.PERMISSION_GRANTED) {
            PermissionStatus.GRANTED
        } else {
            PermissionStatus.DENIED
        }
    }

    actual suspend fun requestPermission(permission: Permission): PermissionStatus {
        val androidPermission = permission.toAndroidPermission()

        // Проверяем, выдано ли уже
        if (checkPermission(permission) == PermissionStatus.GRANTED) {
            return PermissionStatus.GRANTED
        }

        // Запрашиваем через Activity Result API
        // (упрощённая версия — в реальности нужен ActivityResultLauncher)
        val activity = activityProvider()

        val shouldShowRationale = activity
            .shouldShowRequestPermissionRationale(androidPermission)

        // Здесь должен быть реальный запрос через ActivityResultContracts
        // Возвращаем текущий статус как placeholder
        return if (shouldShowRationale) {
            PermissionStatus.DENIED
        } else {
            PermissionStatus.PERMANENTLY_DENIED
        }
    }

    actual fun openSettings() {
        val intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS).apply {
            data = Uri.fromParts("package", context.packageName, null)
            addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        }
        context.startActivity(intent)
    }

    private fun Permission.toAndroidPermission(): String {
        return when (this) {
            Permission.CAMERA -> Manifest.permission.CAMERA
            Permission.LOCATION_FOREGROUND -> Manifest.permission.ACCESS_FINE_LOCATION
            Permission.LOCATION_BACKGROUND -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    Manifest.permission.ACCESS_BACKGROUND_LOCATION
                } else {
                    Manifest.permission.ACCESS_FINE_LOCATION
                }
            }
            Permission.NOTIFICATIONS -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    Manifest.permission.POST_NOTIFICATIONS
                } else {
                    "" // Не требуется на старых версиях
                }
            }
            Permission.PHOTO_LIBRARY -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                    Manifest.permission.READ_MEDIA_IMAGES
                } else {
                    Manifest.permission.READ_EXTERNAL_STORAGE
                }
            }
            Permission.MICROPHONE -> Manifest.permission.RECORD_AUDIO
        }
    }
}
```

---

## 6 распространённых ошибок

### 1. Запрос всех разрешений при старте

```swift
// ❌ НЕПРАВИЛЬНО — запрашиваем всё сразу при запуске
func application(_ application: UIApplication,
                 didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    Task {
        await AVCaptureDevice.requestAccess(for: .video)
        await AVCaptureDevice.requestAccess(for: .audio)
        locationManager.requestAlwaysAuthorization()
        // Пользователь увидит 3 алерта подряд — UX катастрофа
    }
    return true
}

// ✅ ПРАВИЛЬНО — запрашиваем в контексте использования
func scanQRCodeButtonTapped() async {
    let granted = await cameraPermissionHandler.requestCameraPermission()
    if granted {
        presentScanner()
    } else {
        showPermissionDeniedAlert()
    }
}
```

### 2. Игнорирование статуса Restricted (iOS)

```swift
// ❌ НЕПРАВИЛЬНО — не обрабатываем restricted
func handleCameraPermission() async {
    let granted = await AVCaptureDevice.requestAccess(for: .video)
    if !granted {
        showSettingsAlert() // Настройки не помогут при restricted!
    }
}

// ✅ ПРАВИЛЬНО — проверяем restricted отдельно
func handleCameraPermission() async {
    let status = AVCaptureDevice.authorizationStatus(for: .video)

    switch status {
    case .restricted:
        // Родительский контроль или MDM — настройки не помогут
        showRestrictedAlert(message: "Камера заблокирована администратором устройства")
    case .denied:
        showSettingsAlert()
    case .notDetermined:
        let granted = await AVCaptureDevice.requestAccess(for: .video)
        // ...
    case .authorized:
        proceedWithCamera()
    @unknown default:
        break
    }
}
```

### 3. Неправильный порядок запроса Location Background

```kotlin
// ❌ НЕПРАВИЛЬНО — запрашиваем background сразу
suspend fun requestBackgroundLocation() {
    handler.requestPermission(Manifest.permission.ACCESS_BACKGROUND_LOCATION)
    // Краш на Android 10+: нужно сначала foreground!
}

// ✅ ПРАВИЛЬНО — сначала foreground, потом background
suspend fun requestBackgroundLocation(): PermissionResult {
    // Шаг 1: Получаем foreground
    val foregroundResult = handler.requestPermission(
        Manifest.permission.ACCESS_FINE_LOCATION
    )

    if (foregroundResult != PermissionResult.Granted) {
        return foregroundResult
    }

    // Шаг 2: Только после foreground запрашиваем background
    return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        handler.requestPermission(
            Manifest.permission.ACCESS_BACKGROUND_LOCATION
        )
    } else {
        PermissionResult.Granted
    }
}
```

### 4. Отсутствие Privacy Manifest для SDK

```xml
<!-- ❌ НЕПРАВИЛЬНО — SDK без Privacy Manifest (iOS 17+) -->
<!-- App Store отклонит приложение -->

<!-- ✅ ПРАВИЛЬНО — каждый SDK должен иметь свой PrivacyInfo.xcprivacy -->
<!-- Или агрегированный манифест в основном приложении -->
```

### 5. Не показываем Rationale перед повторным запросом (Android)

```kotlin
// ❌ НЕПРАВИЛЬНО — сразу запрашиваем повторно
fun requestCameraAgain() {
    permissionLauncher.launch(Manifest.permission.CAMERA)
}

// ✅ ПРАВИЛЬНО — показываем объяснение перед повторным запросом
fun requestCameraAgain() {
    if (shouldShowRequestPermissionRationale(Manifest.permission.CAMERA)) {
        // Показываем UI с объяснением, ЗАЧЕМ нужна камера
        showRationaleDialog(
            title = "Нужен доступ к камере",
            message = "Камера используется для сканирования QR-кодов. " +
                      "Без этого разрешения функция недоступна.",
            onConfirm = {
                permissionLauncher.launch(Manifest.permission.CAMERA)
            }
        )
    } else {
        // Permanently denied — направляем в настройки
        showSettingsDialog()
    }
}
```

### 6. Забываем про Photo Picker (не требует разрешений)

```swift
// ❌ НЕПРАВИЛЬНО — запрашиваем полный доступ к фото
PHPhotoLibrary.requestAuthorization(for: .readWrite) { status in
    // Пользователь должен дать доступ ко ВСЕЙ библиотеке
}

// ✅ ПРАВИЛЬНО — используем PHPicker (iOS 14+), не требует разрешений
import PhotosUI

func presentPhotoPicker() {
    var config = PHPickerConfiguration()
    config.selectionLimit = 1
    config.filter = .images

    let picker = PHPickerViewController(configuration: config)
    picker.delegate = self
    present(picker, animated: true)
    // Пользователь выбирает ТОЛЬКО нужные фото — приватность сохранена
}
```

---

## 3 ментальные модели

### 1. "Контекстный запрос" vs "Упреждающий запрос"

```
┌─────────────────────────────────────────────────────────────────┐
│                    КОНТЕКСТНЫЙ ЗАПРОС                          │
│                                                                 │
│    Пользователь        Действие           Запрос разрешения    │
│         │                  │                      │            │
│         ▼                  ▼                      ▼            │
│    [Нажал "Скан"]  →  [Открыть камеру]  →  [Нужна камера?]    │
│                                                   │            │
│                                              ✅ Понятно!       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                    УПРЕЖДАЮЩИЙ ЗАПРОС                          │
│                                                                 │
│    Запуск приложения       Запросы              Реакция        │
│         │                     │                    │           │
│         ▼                     ▼                    ▼           │
│    [App Launch]  →  [Камера? Гео? Фото?]  →  [Зачем всё это?] │
│                                                    │           │
│                                               ❌ Отказ!        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Правило:** Запрашивай разрешение непосредственно перед использованием функции, когда пользователь понимает контекст.

### 2. "Воронка разрешений" — от меньшего к большему

```
┌─────────────────────────────────────────────────────────────┐
│                    ВОРОНКА РАЗРЕШЕНИЙ                       │
│                                                             │
│   Уровень 1: Минимум                                        │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Photo Picker (без разрешений)                      │   │
│   │  Coarse Location (город)                            │   │
│   │  Provisional Notifications (тихие)                  │   │
│   └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│   Уровень 2: Стандарт                                       │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Camera (для конкретной функции)                    │   │
│   │  Fine Location (точные координаты)                  │   │
│   │  Full Notifications (с запросом)                    │   │
│   └─────────────────────────────────────────────────────┘   │
│                          │                                  │
│                          ▼                                  │
│   Уровень 3: Расширенный                                    │
│   ┌─────────────────────────────────────────────────────┐   │
│   │  Photo Library Full Access                          │   │
│   │  Background Location                                │   │
│   │  ATT (App Tracking Transparency)                    │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Правило:** Начинай с минимально необходимых разрешений. Расширяй только когда пользователь явно нуждается в дополнительной функциональности.

### 3. "Состояние — это не boolean"

```
┌──────────────────────────────────────────────────────────────┐
│              СОСТОЯНИЯ РАЗРЕШЕНИЙ — НЕ BOOLEAN               │
│                                                              │
│  ┌────────────────┐                                          │
│  │ NOT_DETERMINED │ ─────► Можно запросить                   │
│  └───────┬────────┘                                          │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────┐                                          │
│  │    GRANTED     │ ─────► Функция доступна                  │
│  └────────────────┘                                          │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────┐                                          │
│  │     DENIED     │ ─────► Показать rationale, повторить     │
│  └────────────────┘        (Android) / Настройки (iOS)       │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────┐                                          │
│  │   RESTRICTED   │ ─────► MDM/Parental Control              │
│  │   (iOS only)   │        Настройки НЕ помогут!             │
│  └────────────────┘                                          │
│          │                                                   │
│          ▼                                                   │
│  ┌────────────────┐                                          │
│  │  PERMANENTLY   │ ─────► Только настройки системы          │
│  │    DENIED      │        (Android "Don't ask again")       │
│  └────────────────┘                                          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Правило:** Обрабатывай каждое состояние отдельно. `denied` и `restricted` требуют разных UI-решений.

---

## Quiz

### Вопрос 1

Приложение запрашивает `ACCESS_BACKGROUND_LOCATION` на Android 11, но foreground location ещё не выдан. Что произойдёт?

<details>
<summary>Ответ</summary>

**Запрос будет проигнорирован или приведёт к ошибке.**

На Android 10+ (API 29+) background location можно запросить ТОЛЬКО после того, как пользователь уже выдал foreground location (`ACCESS_FINE_LOCATION` или `ACCESS_COARSE_LOCATION`).

Правильный порядок:
1. Запросить `ACCESS_FINE_LOCATION`
2. Дождаться выдачи
3. Только потом запросить `ACCESS_BACKGROUND_LOCATION`

```kotlin
// Сначала foreground
val foreground = requestPermission(ACCESS_FINE_LOCATION)
if (foreground == GRANTED) {
    // Потом background
    requestPermission(ACCESS_BACKGROUND_LOCATION)
}
```
</details>

### Вопрос 2

Пользователь iOS отклонил запрос на камеру. Можно ли показать системный диалог запроса повторно?

<details>
<summary>Ответ</summary>

**Нет, системный диалог показывается только один раз.**

После отклонения статус становится `.denied`, и `requestAccess(for:)` сразу вернёт `false` без показа диалога.

Единственный способ получить разрешение — направить пользователя в системные настройки:

```swift
if let url = URL(string: UIApplication.openSettingsURLString) {
    await UIApplication.shared.open(url)
}
```

Поэтому критически важно:
1. Запрашивать разрешение в правильном контексте
2. Показать pre-permission screen с объяснением ПЕРЕД системным запросом
</details>

### Вопрос 3

Что такое Privacy Manifest и когда он обязателен?

<details>
<summary>Ответ</summary>

**Privacy Manifest (PrivacyInfo.xcprivacy)** — файл декларации, который описывает:
1. Какие данные собирает приложение/SDK
2. Зачем используются "Required Reason APIs"
3. Какие домены используются для трекинга

**Обязателен с iOS 17 (2024)** для:
- Всех приложений в App Store
- Всех сторонних SDK (каждый SDK должен иметь свой манифест)
- При использовании "Required Reason APIs" (UserDefaults, File Timestamps, System Boot Time, Disk Space, Active Keyboard)

Без Privacy Manifest приложение будет отклонено при ревью в App Store.

```xml
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
</array>
```
</details>

---

## Связанные заметки

- [[ios-permissions-security]] — детальное руководство по iOS permissions
- [[android-permissions-security]] — детальное руководство по Android permissions
- [[kmp-platform-specific]] — expect/actual patterns в KMP
- [[privacy-by-design]] — принципы проектирования с учётом приватности
