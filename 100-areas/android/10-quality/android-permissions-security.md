---
title: "Permissions и Security: Runtime Permissions, Secure Storage"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [access-control, sandboxing, process-isolation, encryption]
tags:
  - topic/android
  - topic/security
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-app-components]]"
  - "[[android-data-persistence]]"
  - "[[android-intent-internals]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-app-components]]"
---

# Permissions и Security: Runtime Permissions, Secure Storage

Android использует модель разрешений для защиты приватных данных и опасных операций. С Android 6.0 (API 23) опасные разрешения запрашиваются в runtime. Безопасное хранение данных требует EncryptedSharedPreferences, Keystore и BiometricPrompt.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android архитектуры и жизненного цикла приложения
> - [[android-app-components]] — знание Activity, Service и BroadcastReceiver для понимания exported components
> - Понимание концепции sandbox и изоляции процессов в Android (каждое приложение работает в отдельном процессе с уникальным UID)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Normal Permission** | Автоматически предоставляется при установке |
| **Dangerous Permission** | Требует явного согласия пользователя |
| **Permission Group** | Группа связанных разрешений (CAMERA, LOCATION) |
| **Runtime Permission** | Запрос разрешения во время работы приложения |
| **Keystore** | Аппаратное хранилище криптографических ключей |
| **BiometricPrompt** | API для биометрической аутентификации |

---

## Почему Runtime Permissions?

### Проблема: install-time permissions (до Android 6.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                 СТАРАЯ МОДЕЛЬ (до Android 6.0)                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Установка приложения:                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ "Фонарик" запрашивает:                                   │   │
│  │  ✓ Доступ к камере                                       │   │
│  │  ✓ Доступ к контактам        ← Зачем фонарику контакты?  │   │
│  │  ✓ Доступ к SMS              ← Зачем фонарику SMS?       │   │
│  │  ✓ Доступ к местоположению   ← Зачем фонарику GPS?       │   │
│  │                                                          │   │
│  │  [Установить] [Отмена]                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Проблемы:                                                      │
│  - Всё или ничего — нельзя отказать в одном разрешении          │
│  - Пользователь не понимает зачем разрешения                   │
│  - Malware получает доступ ко всему при установке              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Решение: Runtime Permissions (Android 6.0+)

```
┌─────────────────────────────────────────────────────────────────┐
│                 НОВАЯ МОДЕЛЬ (Android 6.0+)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Установка:                                                     │
│  - Нет запросов разрешений                                      │
│  - Приложение устанавливается                                   │
│                                                                 │
│  Использование (когда реально нужно):                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ "Карты" запрашивает доступ к местоположению              │   │
│  │                                                          │   │
│  │ "Чтобы показать вашу позицию на карте"                   │   │
│  │                                                          │   │
│  │  [Разрешить] [Не разрешать]                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Преимущества:                                                  │
│  - Контекст: понятно зачем нужно разрешение                    │
│  - Гранулярность: можно отказать в конкретном                  │
│  - Контроль: можно отозвать в Settings в любое время           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Хронология изменений: как Google усиливал защиту приватности

### Android 6.0 Marshmallow (API 23) — 2015: Runtime Permissions

**Переломный момент.** Google полностью изменил модель разрешений.

**Что изменилось:**
- Dangerous permissions запрашиваются в runtime, не при установке
- Пользователь может отказать в конкретном разрешении
- Можно отозвать разрешение в любое время через Settings
- Normal permissions по-прежнему даются автоматически

**Новые API:**
- `checkSelfPermission()` — проверить есть ли разрешение
- `requestPermissions()` — запросить разрешение
- `onRequestPermissionsResult()` — обработать ответ
- `shouldShowRequestPermissionRationale()` — нужно ли показать объяснение

---

### Android 8.0 Oreo (API 26) — 2017: Background Location ограничен

**Что изменилось:**
- Приложения в фоне получают location updates значительно реже (несколько раз в час вместо постоянного)
- Это первый шаг к разделению foreground/background location

---

### Android 10 (API 29) — 2019: Scoped Storage и Background Location

**Два больших изменения:**

1. **ACCESS_BACKGROUND_LOCATION** — отдельное разрешение:
   - До Android 10: ACCESS_FINE_LOCATION давало доступ везде
   - Android 10+: для GPS в фоне нужно отдельное разрешение
   - Пользователь выбирает "Allow all the time" или "Allow only while using"

2. **Scoped Storage** — ограничение доступа к файлам:
   - До Android 10: READ/WRITE_EXTERNAL_STORAGE давали полный доступ ко всем файлам
   - Android 10+: приложения видят только свои файлы + медиа через MediaStore
   - В Android 10 можно было отключить через `requestLegacyExternalStorage="true"`

```xml
<!-- AndroidManifest.xml — временный opt-out в Android 10 -->
<application
    android:requestLegacyExternalStorage="true">
</application>
```

---

### Android 11 (API 30) — 2020: Scoped Storage обязателен, One-time Permissions

**Scoped Storage теперь обязателен:**
- `requestLegacyExternalStorage` игнорируется на Android 11+
- WRITE_EXTERNAL_STORAGE больше не даёт дополнительного доступа
- Для доступа ко всем файлам нужен MANAGE_EXTERNAL_STORAGE (только для file managers)

**One-time Permissions:**
- Новая опция "Only this time" для location, camera, microphone
- Разрешение действует пока приложение в foreground
- После ухода в фон разрешение отзывается

**Auto-reset Permissions:**
- Система автоматически отзывает разрешения у неиспользуемых приложений
- Если приложение не открывали несколько месяцев — все dangerous permissions сбрасываются

```
┌─────────────────────────────────────────────────────────────────┐
│           ONE-TIME PERMISSIONS (Android 11+)                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "Камера" запрашивает доступ к местоположению                   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ○ Allow all the time      (только для location)        │   │
│  │  ○ Allow only while using the app                       │   │
│  │  ○ Ask every time          ← НОВОЕ в Android 11         │   │
│  │  ○ Deny                                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Android 12 (API 31) — 2021: Approximate Location, Bluetooth Permissions

**Approximate vs Precise Location:**
- Новый диалог с выбором точности
- COARSE_LOCATION даёт примерное местоположение (~1-2 км)
- FINE_LOCATION даёт точное GPS
- Пользователь сам выбирает что дать

**Bluetooth Permissions разделены:**
- Раньше: нужен был ACCESS_FINE_LOCATION для сканирования Bluetooth
- Android 12+: отдельные разрешения:
  - BLUETOOTH_SCAN — сканирование устройств
  - BLUETOOTH_CONNECT — подключение к устройствам
  - BLUETOOTH_ADVERTISE — реклама BLE

```kotlin
// Android 12+: Bluetooth без location
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    requestPermissions(arrayOf(
        Manifest.permission.BLUETOOTH_SCAN,
        Manifest.permission.BLUETOOTH_CONNECT
    ), REQUEST_CODE)
}
```

---

### Android 13 (API 33) — 2022: Notification Permission, Granular Media

**POST_NOTIFICATIONS — новое dangerous permission:**
- До Android 13: любое приложение могло показывать уведомления
- Android 13+: нужно явное разрешение пользователя
- Приложения targetSdk 33+ должны запрашивать разрешение

```kotlin
// Android 13+: запрос разрешения на уведомления
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    requestPermissions(
        arrayOf(Manifest.permission.POST_NOTIFICATIONS),
        REQUEST_CODE
    )
}
```

**Granular Media Permissions:**
- READ_EXTERNAL_STORAGE разделён на три:
  - READ_MEDIA_IMAGES — фото
  - READ_MEDIA_VIDEO — видео
  - READ_MEDIA_AUDIO — аудио
- Пользователь может дать доступ только к фото, но не к музыке

```xml
<!-- AndroidManifest.xml -->
<!-- Для Android 13+ -->
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES"/>
<uses-permission android:name="android.permission.READ_MEDIA_VIDEO"/>
<uses-permission android:name="android.permission.READ_MEDIA_AUDIO"/>

<!-- Для Android 12 и ниже -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32"/>
```

---

### Android 14 (API 34) — 2023: Photo Picker, Selected Photos Access

**Photo Picker:**
- Системный UI для выбора фото без разрешений
- Приложение получает доступ только к выбранным файлам
- Не нужен READ_MEDIA_IMAGES для большинства случаев

```kotlin
// Photo Picker — без разрешений
val pickMedia = registerForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
    uri?.let { processSelectedImage(it) }
}

pickMedia.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))
```

**Selected Photos Access:**
- Новая опция "Select photos and videos"
- Пользователь выбирает конкретные файлы для доступа
- Приложение не видит всю галерею

```
┌─────────────────────────────────────────────────────────────────┐
│        PHOTO ACCESS OPTIONS (Android 14+)                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  "Instagram" запрашивает доступ к фото                          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ○ Allow access to all photos                           │   │
│  │  ○ Select photos and videos  ← НОВОЕ в Android 14       │   │
│  │  ○ Don't allow                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  При "Select photos": пользователь выбирает конкретные файлы   │
│  Приложение видит ТОЛЬКО выбранные, не всю галерею             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

### Эволюция Storage Permissions: сводная таблица

| Android | READ_EXTERNAL_STORAGE | WRITE_EXTERNAL_STORAGE | Доступ к чужим файлам |
|---------|----------------------|------------------------|----------------------|
| ≤9 | Полный доступ | Полный доступ | Да, ко всем |
| 10 | Медиа через MediaStore | Медиа через MediaStore | Opt-out возможен |
| 11 | Медиа через MediaStore | **Не работает** | Только MediaStore |
| 12 | Медиа через MediaStore | Не работает | Только MediaStore |
| 13+ | **Заменён на 3 разрешения** | Не работает | Гранулярный выбор |
| 14+ | Гранулярный + Photo Picker | Не работает | Selected photos |

---

## Типы разрешений

### Normal Permissions (автоматические)

```xml
<!-- AndroidManifest.xml — эти разрешения предоставляются автоматически -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.VIBRATE" />
<uses-permission android:name="android.permission.WAKE_LOCK" />
<uses-permission android:name="android.permission.SET_ALARM" />
```

### Dangerous Permissions (требуют запроса)

| Группа | Разрешения |
|--------|------------|
| **CALENDAR** | READ_CALENDAR, WRITE_CALENDAR |
| **CAMERA** | CAMERA |
| **CONTACTS** | READ_CONTACTS, WRITE_CONTACTS, GET_ACCOUNTS |
| **LOCATION** | ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION |
| **MICROPHONE** | RECORD_AUDIO |
| **PHONE** | READ_PHONE_STATE, CALL_PHONE, READ_CALL_LOG |
| **SMS** | SEND_SMS, RECEIVE_SMS, READ_SMS |
| **STORAGE** | READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE |

---

## Запрос Runtime Permissions

### Современный подход с ActivityResult API

```kotlin
class CameraFragment : Fragment() {

    // Регистрируем callback для результата
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            openCamera()
        } else {
            showPermissionDeniedMessage()
        }
    }

    private fun checkCameraPermission() {
        when {
            // Уже есть разрешение
            ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED -> {
                openCamera()
            }

            // Нужно показать объяснение (пользователь отказал ранее)
            shouldShowRequestPermissionRationale(Manifest.permission.CAMERA) -> {
                showRationaleDialog()
            }

            // Первый запрос или "Don't ask again"
            else -> {
                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
        }
    }

    private fun showRationaleDialog() {
        AlertDialog.Builder(requireContext())
            .setTitle("Доступ к камере")
            .setMessage("Для сканирования QR-кода нужен доступ к камере")
            .setPositiveButton("Разрешить") { _, _ ->
                requestPermissionLauncher.launch(Manifest.permission.CAMERA)
            }
            .setNegativeButton("Отмена", null)
            .show()
    }
}
```

### Запрос нескольких разрешений

```kotlin
private val requestMultiplePermissions = registerForActivityResult(
    ActivityResultContracts.RequestMultiplePermissions()
) { permissions ->
    val cameraGranted = permissions[Manifest.permission.CAMERA] ?: false
    val locationGranted = permissions[Manifest.permission.ACCESS_FINE_LOCATION] ?: false

    when {
        cameraGranted && locationGranted -> {
            startAugmentedReality()
        }
        cameraGranted -> {
            showMessage("AR требует также GPS")
        }
        else -> {
            showMessage("Нужны разрешения для AR")
        }
    }
}

fun requestArPermissions() {
    requestMultiplePermissions.launch(
        arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.ACCESS_FINE_LOCATION
        )
    )
}
```

### Location: особые случаи

```kotlin
// Android 10+: Background location — отдельное разрешение
private val requestBackgroundLocation = registerForActivityResult(
    ActivityResultContracts.RequestPermission()
) { isGranted ->
    if (isGranted) {
        startBackgroundLocationUpdates()
    }
}

fun requestLocationPermissions() {
    // Сначала запрашиваем foreground location
    val foregroundGranted = ContextCompat.checkSelfPermission(
        this, Manifest.permission.ACCESS_FINE_LOCATION
    ) == PackageManager.PERMISSION_GRANTED

    if (!foregroundGranted) {
        // Запросить foreground first
        requestForegroundLocation.launch(Manifest.permission.ACCESS_FINE_LOCATION)
        return
    }

    // Потом background (Android 10+)
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        val backgroundGranted = ContextCompat.checkSelfPermission(
            this, Manifest.permission.ACCESS_BACKGROUND_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        if (!backgroundGranted) {
            // Показать объяснение и направить в Settings
            // (нельзя запросить программно на Android 11+)
            showBackgroundLocationRationale()
        }
    }
}
```

---

## Secure Storage

### Почему не обычные SharedPreferences

```kotlin
// ❌ SharedPreferences — хранятся в plaintext
val prefs = getSharedPreferences("auth", MODE_PRIVATE)
prefs.edit().putString("access_token", "secret123").apply()

// Файл /data/data/com.example/shared_prefs/auth.xml:
// <string name="access_token">secret123</string>
// На rooted устройстве — читается легко!
```

### EncryptedSharedPreferences

```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.security:security-crypto:1.1.0-alpha06")
}

// ✅ Зашифрованное хранилище
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    .build()

val encryptedPrefs = EncryptedSharedPreferences.create(
    context,
    "secure_prefs",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)

// Использование — как обычные SharedPreferences
encryptedPrefs.edit().putString("access_token", "secret123").apply()
val token = encryptedPrefs.getString("access_token", null)

// Данные зашифрованы! Ключ в Android Keystore (hardware-backed)
```

### Когда что использовать

| Данные | Хранилище | Причина |
|--------|-----------|---------|
| Настройки UI (тема, язык) | DataStore | Не sensitive |
| Access token | EncryptedSharedPreferences | Credentials |
| Refresh token | EncryptedSharedPreferences | Long-lived credentials |
| PIN / пароль | НЕ хранить! | Используйте серверную авторизацию |
| Биометрия | BiometricPrompt + Keystore | Hardware security |
| Данные карты | Не хранить локально! | PCI DSS compliance |

---

## Biometric Authentication

```kotlin
class BiometricAuthManager(private val activity: FragmentActivity) {

    private val executor = ContextCompat.getMainExecutor(activity)

    fun authenticate(
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        // Проверяем доступность биометрии
        val biometricManager = BiometricManager.from(activity)
        when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                showBiometricPrompt(onSuccess, onError)
            }
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> {
                onError("Устройство не поддерживает биометрию")
            }
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> {
                onError("Биометрия временно недоступна")
            }
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
                onError("Биометрия не настроена")
            }
        }
    }

    private fun showBiometricPrompt(
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Вход в приложение")
            .setSubtitle("Используйте отпечаток пальца")
            .setNegativeButtonText("Отмена")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    onSuccess()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    onError(errString.toString())
                }

                override fun onAuthenticationFailed() {
                    // Неуспешная попытка (не ошибка, можно повторить)
                }
            }
        )

        biometricPrompt.authenticate(promptInfo)
    }
}
```

---

## Безопасность сети

### Network Security Config

```xml
<!-- res/xml/network_security_config.xml -->
<network-security-config>
    <!-- Запретить cleartext (HTTP) для всех доменов -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Разрешить cleartext только для локальной разработки -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>

    <!-- Certificate pinning для production API -->
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2025-01-01">
            <pin digest="SHA-256">base64EncodedPublicKeyHash=</pin>
            <!-- Backup pin -->
            <pin digest="SHA-256">backupBase64EncodedHash=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

```xml
<!-- AndroidManifest.xml -->
<application
    android:networkSecurityConfig="@xml/network_security_config">
```

---

## Типичные ошибки безопасности

### 1. Хранение секретов в BuildConfig/strings.xml

**Проблема:** API ключи и токены в коде легко извлечь из APK

```kotlin
// ❌ УЯЗВИМОСТЬ: секреты в BuildConfig
object ApiConfig {
    const val API_KEY = "sk_live_51HGhh2KGzQ..."  // Видно в декомпиляции!
}

// ❌ УЯЗВИМОСТЬ: секреты в strings.xml
<string name="google_maps_key">AIzaSyC...</string>
// Файл APK → res/values/strings.xml доступен через apktool

// ❌ УЯЗВИМОСТЬ: секреты в gradle.properties
apiKey=sk_live_51HGhh2KGzQ...
// Попадает в BuildConfig при сборке
```

**Почему опасно:**
- APK — это ZIP-архив, любой может распаковать и прочитать ресурсы
- ProGuard/R8 не обфусцирует строковые константы
- Декомпиляция через jadx показывает все секреты в plaintext

**Решение:**

```kotlin
// ✅ Получение ключей с бэкенда при первом запуске
class ApiKeyRepository(private val api: AuthApi) {
    suspend fun getApiKey(): String {
        // Бэкенд проверяет подпись APK и package name
        return api.fetchClientKey(
            packageName = BuildConfig.APPLICATION_ID,
            signature = getAppSignature()
        ).key
    }
}

// ✅ Для отладки: ключи в local.properties (не коммитится в Git)
// local.properties
debug.api.key=dev_key_for_testing_only

// build.gradle.kts
android {
    defaultConfig {
        val localProperties = Properties()
        localProperties.load(FileInputStream(rootProject.file("local.properties")))
        buildConfigField("String", "DEBUG_API_KEY",
            "\"${localProperties["debug.api.key"]}\"")
    }
}
```

---

### 2. SQL Injection в ContentProvider

**Проблема:** Пользовательский ввод напрямую в SQL запрос

```kotlin
// ❌ УЯЗВИМОСТЬ
class UserProvider : ContentProvider() {
    override fun query(uri: Uri, ..., selection: String?, ...): Cursor {
        val userName = uri.getQueryParameter("name")
        // Атака: content://com.example/users?name=' OR '1'='1
        val query = "SELECT * FROM users WHERE name = '$userName'"
        return db.rawQuery(query, null)
        // Вернёт ВСЕ записи вместо одной!
    }
}
```

**Атака:**
```kotlin
// Злоумышленник может получить все данные
val uri = Uri.parse("content://com.example/users?name=' OR '1'='1")
contentResolver.query(uri, null, null, null, null)

// Или удалить таблицу
val uri = Uri.parse("content://com.example/users?name='; DROP TABLE users; --")
```

**Решение:**

```kotlin
// ✅ Параметризованные запросы
class UserProvider : ContentProvider() {
    override fun query(uri: Uri, ..., selection: String?, ...): Cursor {
        val userName = uri.getQueryParameter("name")
        val query = "SELECT * FROM users WHERE name = ?"
        return db.rawQuery(query, arrayOf(userName))
        // SQL инъекция невозможна — userName экранируется
    }
}

// ✅ Или используйте query builder
val cursor = db.query(
    "users",                    // table
    arrayOf("id", "name"),      // columns
    "name = ?",                 // selection
    arrayOf(userName),          // selectionArgs — автоматически экранируется
    null, null, null
)

// ✅ Лучше всего: Room автоматически защищает
@Dao
interface UserDao {
    @Query("SELECT * FROM users WHERE name = :name")
    fun findByName(name: String): List<User>
    // Room автоматически использует параметризованные запросы
}
```

---

### 3. Intent Spoofing

**Проблема:** Обработка Intent от недоверенного источника

```kotlin
// ❌ УЯЗВИМОСТЬ: доверяем данным из Intent
class PaymentActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Опасно! Любое приложение может запустить этот Intent
        val amount = intent.getIntExtra("amount", 0)
        val recipient = intent.getStringExtra("recipient")

        // Атакующий может подделать данные:
        // Intent().apply {
        //     putExtra("amount", 1)        // Заплатить 1₽ вместо 1000₽
        //     putExtra("recipient", "hacker@example.com")
        // }
        processPayment(amount, recipient)
    }
}
```

**Атака:**

```kotlin
// Злоумышленное приложение
val fakeIntent = Intent().apply {
    setClassName("com.bank.app", "com.bank.PaymentActivity")
    putExtra("amount", 1)  // Подмена суммы
    putExtra("recipient", "attacker@evil.com")
}
startActivity(fakeIntent)
```

**Решение:**

```kotlin
// ✅ Не экспортируем Activity
<activity
    android:name=".PaymentActivity"
    android:exported="false">  <!-- Только свое приложение может запустить -->
</activity>

// ✅ Проверяем caller identity
class PaymentActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Проверяем кто запустил Activity
        val callingPackage = callingActivity?.packageName
        if (callingPackage != packageName) {
            finish()
            return
        }

        // Или используем signature verification
        if (!isCallerTrusted()) {
            finish()
            return
        }
    }

    private fun isCallerTrusted(): Boolean {
        val callingUid = Binder.getCallingUid()
        val callingPackages = packageManager.getPackagesForUid(callingUid) ?: return false

        return callingPackages.any { pkg ->
            pkg == packageName  // Только от нашего приложения
        }
    }
}

// ✅ Используем PendingIntent для безопасной передачи
// Вместо отправки Intent, создаём PendingIntent в доверенном контексте
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    Intent(context, PaymentActivity::class.java).apply {
        putExtra("amount", validatedAmount)
        putExtra("recipient", validatedRecipient)
    },
    PendingIntent.FLAG_IMMUTABLE  // Данные нельзя изменить
)
// Теперь другие приложения не могут подделать данные
```

---

### 4. Exported Components без protection

**Проблема:** Компоненты доступны любому приложению

```kotlin
// ❌ УЯЗВИМОСТЬ: Activity с intent-filter автоматически exported=true
<activity android:name=".DeepLinkActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <data android:scheme="myapp"/>
    </intent-filter>
    <!-- exported=true неявно! Любое приложение может запустить -->
</activity>

// ❌ УЯЗВИМОСТЬ: BroadcastReceiver без permission
<receiver android:name=".AdminCommandReceiver" android:exported="true">
    <intent-filter>
        <action android:name="com.example.ADMIN_ACTION"/>
    </intent-filter>
    <!-- Любое приложение может отправить команду! -->
</receiver>

// Атака:
val intent = Intent("com.example.ADMIN_ACTION")
intent.putExtra("command", "deleteAllData")
sendBroadcast(intent)  // Выполнится в чужом приложении!
```

**Решение:**

```kotlin
// ✅ Явно запретить экспорт если не нужен
<activity
    android:name=".DeepLinkActivity"
    android:exported="false">  <!-- Explicit -->
    <intent-filter>
        <action android:name="android.intent.action.VIEW"/>
        <data android:scheme="myapp"/>
    </intent-filter>
</activity>

// ✅ Защитить custom permission
<permission
    android:name="com.example.permission.ADMIN_ACCESS"
    android:protectionLevel="signature"/>  <!-- Только приложения с той же подписью -->

<receiver
    android:name=".AdminCommandReceiver"
    android:permission="com.example.permission.ADMIN_ACCESS"
    android:exported="true">
    <intent-filter>
        <action android:name="com.example.ADMIN_ACTION"/>
    </intent-filter>
</receiver>

// ✅ Проверяем caller в коде
class AdminCommandReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Проверяем подпись отправителя
        if (!isSenderTrusted(context)) {
            return
        }
        executeCommand(intent.getStringExtra("command"))
    }

    private fun isSenderTrusted(context: Context): Boolean {
        val callingUid = Binder.getCallingUid()
        val packages = context.packageManager.getPackagesForUid(callingUid)

        return packages?.any { pkg ->
            context.packageManager
                .getPackageInfo(pkg, PackageManager.GET_SIGNATURES)
                .signatures
                .contentEquals(getOurSignature(context))
        } ?: false
    }
}

// ✅ Android 12+: явно указываем exported
<activity
    android:name=".MainActivity"
    android:exported="true">  <!-- Обязательно для launcher -->
    <intent-filter>
        <action android:name="android.intent.action.MAIN"/>
        <category android:name="android.intent.category.LAUNCHER"/>
    </intent-filter>
</activity>
```

**Правило:** С Android 12 (API 31) компилятор требует явно указать `android:exported` для всех компонентов с intent-filter.

---

## Чеклист безопасности

```
□ Dangerous permissions запрашиваются в runtime
□ Показываем rationale перед повторным запросом
□ Credentials в EncryptedSharedPreferences
□ Биометрия для sensitive действий
□ Network Security Config запрещает HTTP
□ Certificate pinning для API
□ Компоненты exported="false" если не нужны извне
□ Параметризованные SQL запросы (или Room)
□ WebView с отключённым file access
□ Нет sensitive данных в логах
□ ProGuard/R8 для обфускации
```

---

## Проверь себя

Попробуйте ответить перед тем как смотреть ответы:

1. **Чем dangerous permissions отличаются от normal?**
   <details>
   <summary>Показать ответ</summary>

   - **Normal permissions** предоставляются автоматически при установке (INTERNET, VIBRATE, SET_ALARM). Они не влияют на приватность пользователя.
   - **Dangerous permissions** требуют явного согласия пользователя в runtime (CAMERA, LOCATION, CONTACTS). Они дают доступ к приватным данным или аппаратным возможностям, которые могут навредить приватности.
   - С Android 6.0+ dangerous permissions можно запросить только когда приложение активно, и пользователь может отозвать их в любое время через Settings.
   </details>

2. **Почему нельзя хранить API keys в APK?**
   <details>
   <summary>Показать ответ</summary>

   - APK — это обычный ZIP-архив. Любой может распаковать его через `apktool` и прочитать ресурсы (strings.xml, BuildConfig).
   - ProGuard/R8 обфусцирует код, но **не защищает строковые константы** — они остаются в plaintext.
   - Декомпиляторы (jadx, dex2jar) восстанавливают код с секретами за минуты.
   - **Правильно:** получать ключи с бэкенда после проверки подписи APK или использовать NDK (хранить в нативном коде), но это тоже не панацея.
   </details>

3. **Что такое exported=true и когда это опасно?**
   <details>
   <summary>Показать ответ</summary>

   - `exported=true` означает, что компонент (Activity, Service, BroadcastReceiver, ContentProvider) доступен другим приложениям.
   - **Опасно когда:** компонент выполняет sensitive операции (оплата, удаление данных, админские команды) без проверки caller identity.
   - **Автоматически exported=true** если компонент имеет intent-filter (до Android 12 неявно, с Android 12+ нужно явно указать).
   - **Защита:** используйте `android:exported="false"` если не нужен внешний доступ, или защитите custom permission с `protectionLevel="signature"`.
   </details>

4. **Как проверить подлинность Intent sender?**
   <details>
   <summary>Показать ответ</summary>

   - **Способ 1:** `getCallingActivity()` или `getCallingPackage()` — возвращает package name вызывающего.
   - **Способ 2:** `Binder.getCallingUid()` + `PackageManager.getPackagesForUid()` — проверка UID отправителя.
   - **Способ 3:** Проверка подписи (signature) — сравнить подпись отправителя с ожидаемой через `PackageManager.GET_SIGNATURES`.
   - **Лучший способ:** Использовать `PendingIntent.FLAG_IMMUTABLE` — создать Intent в безопасном контексте, чтобы другие приложения не могли изменить данные.
   - **Важно:** Никогда не доверяйте данным из Intent для critical операций без проверки источника.
   </details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "ProGuard защищает API ключи" | ProGuard обфусцирует код, НЕ строки. Строковые константы остаются в plaintext. Для защиты ключей — backend proxy или Play Integrity API |
| "Dangerous permission = опасность" | "Dangerous" означает требует runtime согласия, не "опасный". Запрос CAMERA для camera app — нормально. Опасность в over-requesting |
| "Runtime permission запрашивать сразу" | Не спрашивай сразу все permissions. Запрашивай в контексте использования. Пользователь понимает зачем → выше grant rate |
| "granted = навсегда" | Пользователь может отозвать permission в Settings. Auto-reset неиспользуемых (Android 11+). Проверяй перед каждым использованием |
| "exported=false = полная защита" | exported=false защищает от внешних apps. Но root пользователь, malware с root, или другой process того же uid могут обойти |
| "Биометрия = безопасно" | Биометрия — удобство, не замена encryption. BiometricPrompt + CryptoObject → настоящая безопасность. Fingerprint как fallback |
| "HTTPS = достаточно" | HTTPS защищает от перехвата, не от MITM. Certificate pinning защищает от подмены сертификата. Network Security Config для реализации |
| "SharedPreferences безопасны" | SharedPreferences plaintext XML на устройстве. На rooted device читаются. Для секретов — EncryptedSharedPreferences или Android Keystore |
| "API keys в BuildConfig безопасны" | BuildConfig компилируется в class файл. Декомпиляция за минуты. Для sensitive keys — серверная валидация с Play Integrity |
| "PendingIntent без флагов нормально" | Без FLAG_IMMUTABLE другие apps могут изменить Intent. Android 12+ требует explicit флаг. Всегда IMMUTABLE если не нужна мутация |

---

## CS-фундамент

| CS-концепция | Как применяется в Security |
|--------------|----------------------------|
| **Sandbox / Process Isolation** | Каждое приложение = отдельный Linux user/uid. Изоляция файловой системы. Один процесс не читает память другого |
| **Principle of Least Privilege** | Запрашивай только необходимые permissions. Минимальные права = минимальная attack surface |
| **Cryptography** | Android Keystore для ключей. AES для шифрования данных. Биометрия как factor для доступа к ключам |
| **Public Key Infrastructure** | TLS/SSL для сетевой безопасности. Certificate pinning для защиты от MITM. Certificate chain validation |
| **Access Control** | Permissions как ACL. signature level permissions для inter-app. ContentProvider permissions для данных |
| **Input Validation** | Intent data validation обязательна. SQL injection через ContentProvider возможен. Escape все inputs |
| **Secure Coding** | Не логировать sensitive данные. Не хранить plaintext секреты. Очищать память после использования |
| **Defense in Depth** | Многослойная защита: sandbox + permissions + encryption + validation. Каждый слой независим |
| **Threat Modeling** | STRIDE model для Android: Spoofing (Intent), Tampering (APK), Repudiation (logs), Info Disclosure (storage) |
| **Integrity Verification** | Play Integrity API для проверки устройства. APK signing для integrity. SafetyNet deprecated → Play Integrity |

---

## Связи

**Android раздел:**
- [[android-overview]] — архитектура Android и security model, понимание sandbox изоляции
- [[android-app-components]] — жизненный цикл Activity/Service и их exported настройки для безопасности
- [[android-data-persistence]] — Room и ContentProvider, безопасное хранение данных с EncryptedSharedPreferences
- [[android-networking]] — Network Security Config, certificate pinning и защита HTTPS соединений

**Security контекст:**
- [[web-security-owasp]] — OWASP Top 10 уязвимостей (SQL Injection, XSS применимы к Android WebView и ContentProvider)

**Почему связано:**
- Permissions неразрывно связаны с App Components — каждый компонент может требовать свои разрешения
- Data Persistence требует понимания безопасности — без шифрования токены утекут на rooted устройствах
- Networking без Network Security Config позволяет MITM атаки через поддельные сертификаты

---

## Источники

- [Permissions on Android - Android Developers](https://developer.android.com/guide/topics/permissions/overview) — официальная документация
- [Request Runtime Permissions - Android Developers](https://developer.android.com/training/permissions/requesting) — runtime permissions
- [Security Best Practices - Android Developers](https://developer.android.com/privacy-and-security/security-tips) — best practices
- [Network Security Configuration - Android Developers](https://developer.android.com/privacy-and-security/security-config) — network security

---

## Источники и дальнейшее чтение

- Meier (2022). *Professional Android*. — полное покрытие runtime permissions, Network Security Config, EncryptedSharedPreferences и Keystore API с практическими примерами обработки всех edge cases.
- Phillips et al. (2022). *Android Programming: The Big Nerd Ranch Guide*. — пошаговая реализация runtime permission flow, BiometricPrompt и secure storage с акцентом на UX лучших практик.
- Vasavada (2019). *Android Internals*. — системный взгляд на security model Android: sandbox isolation, UID/GID, SELinux, signature permissions и Binder security, что даёт глубокое понимание почему permissions работают именно так.

---

*Проверено: 2026-01-09 | На основе официальной документации Android*
