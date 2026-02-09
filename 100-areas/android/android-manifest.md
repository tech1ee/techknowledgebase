---
title: "AndroidManifest.xml: конфигурация приложения"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [declarative-configuration, component-registration, metadata, xml-schema]
tags:
  - android
  - manifest
  - configuration
  - components
  - permissions
related:
  - "[[android-overview]]"
  - "[[android-app-components]]"
  - "[[android-permissions-security]]"
  - "[[android-project-structure]]"
  - "[[android-navigation]]"
---

# AndroidManifest.xml: конфигурация приложения

AndroidManifest.xml — это декларативный файл, описывающий приложение системе Android. Без него приложение не может быть установлено. Манифест определяет компоненты, разрешения, требования к устройству и метаданные.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android
> - [[android-app-components]] — Activity, Service, BroadcastReceiver, ContentProvider

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Manifest** | XML-файл с декларацией компонентов и конфигурацией |
| **Intent Filter** | Фильтр, определяющий, какие Intent'ы принимает компонент |
| **Permission** | Разрешение на доступ к защищённым ресурсам |
| **Package Name** | Уникальный идентификатор приложения |
| **Namespace** | Пространство имён для генерации R класса |
| **Manifest Merger** | Процесс объединения манифестов модулей и библиотек |

---

## Базовая структура

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- Разрешения -->
    <uses-permission android:name="android.permission.INTERNET" />

    <!-- Требования к устройству -->
    <uses-feature android:name="android.hardware.camera" android:required="true" />

    <!-- Приложение -->
    <application
        android:name=".MyApplication"
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.MyApp">

        <!-- Компоненты -->
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service android:name=".MyService" />
        <receiver android:name=".MyReceiver" />
        <provider android:name=".MyProvider" android:authorities="com.example.provider" />

    </application>

</manifest>
```

---

## Элемент `<manifest>`

```xml
<manifest
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools"
    package="com.example.myapp">  <!-- Deprecated в AGP 7.0+, используйте namespace -->

    <!-- package — исторически использовался для:
         1. Package name для R класса
         2. Относительные имена компонентов (.MainActivity)

         В AGP 7.0+ заменён на namespace в build.gradle.kts -->

</manifest>
```

### Namespace vs Package

```kotlin
// build.gradle.kts (AGP 7.0+)
android {
    namespace = "com.example.myapp"  // Для R класса и относительных имён

    defaultConfig {
        applicationId = "com.example.myapp"  // Уникальный ID в Play Store
    }

    productFlavors {
        create("free") {
            applicationIdSuffix = ".free"  // com.example.myapp.free
            // namespace остаётся com.example.myapp
        }
    }
}
```

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    NAMESPACE vs APPLICATION ID                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  namespace = "com.example.myapp"                                        │
│  ─────────────────────────────────                                      │
│  • Используется для генерации R класса                                  │
│  • Используется для относительных имён (.MainActivity)                  │
│  • НЕ меняется для разных flavors                                       │
│  • Определяется в build.gradle.kts                                      │
│                                                                         │
│  applicationId = "com.example.myapp.free"                               │
│  ────────────────────────────────────────                               │
│  • Уникальный ID в Play Store                                           │
│  • Может меняться для разных flavors                                    │
│  • Определяет identity приложения для системы                           │
│                                                                         │
│  Пример:                                                                │
│  namespace = "com.example.myapp"                                        │
│  applicationId (free) = "com.example.myapp.free"                        │
│  applicationId (paid) = "com.example.myapp.paid"                        │
│                                                                         │
│  Код: import com.example.myapp.R  (одинаковый для обоих)               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Элемент `<application>`

```xml
<application
    android:name=".MyApplication"
    android:icon="@mipmap/ic_launcher"
    android:roundIcon="@mipmap/ic_launcher_round"
    android:label="@string/app_name"
    android:theme="@style/Theme.MyApp"
    android:allowBackup="true"
    android:fullBackupContent="@xml/backup_rules"
    android:dataExtractionRules="@xml/data_extraction_rules"
    android:supportsRtl="true"
    android:networkSecurityConfig="@xml/network_security_config"
    android:enableOnBackInvokedCallback="true"
    android:localeConfig="@xml/locales_config"
    tools:targetApi="34">

    <!-- Компоненты приложения -->

</application>
```

### Ключевые атрибуты `<application>`

| Атрибут | Значение | Примечание |
|---------|----------|------------|
| `android:name` | Класс Application | `.MyApplication` или полный путь |
| `android:icon` | Иконка приложения | `@mipmap/ic_launcher` |
| `android:roundIcon` | Круглая иконка | Для устройств с круглыми иконками |
| `android:label` | Название приложения | Видно пользователю |
| `android:theme` | Тема по умолчанию | Применяется ко всем Activity |
| `android:allowBackup` | Разрешить backup | `false` для безопасности |
| `android:fullBackupContent` | Правила backup | XML с исключениями |
| `android:supportsRtl` | Поддержка RTL | Арабский, иврит |
| `android:networkSecurityConfig` | Настройки сети | HTTPS, certificate pinning |
| `android:enableOnBackInvokedCallback` | Predictive back | Android 13+ |
| `android:localeConfig` | Поддерживаемые языки | Per-app language |

### Network Security Config

```xml
<!-- res/xml/network_security_config.xml -->
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <!-- По умолчанию: только HTTPS -->
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>

    <!-- Исключение для development сервера -->
    <domain-config cleartextTrafficPermitted="true">
        <domain includeSubdomains="true">10.0.2.2</domain>
        <domain includeSubdomains="true">localhost</domain>
    </domain-config>

    <!-- Certificate pinning для production -->
    <domain-config>
        <domain includeSubdomains="true">api.example.com</domain>
        <pin-set expiration="2025-12-31">
            <pin digest="SHA-256">AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=</pin>
            <pin digest="SHA-256">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=</pin>
        </pin-set>
    </domain-config>
</network-security-config>
```

### Backup Rules

```xml
<!-- res/xml/backup_rules.xml (Android 11 и ниже) -->
<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <include domain="sharedpref" path="." />
    <exclude domain="sharedpref" path="secret_prefs.xml" />
    <exclude domain="database" path="cache.db" />
    <exclude domain="file" path="temp/" />
</full-backup-content>

<!-- res/xml/data_extraction_rules.xml (Android 12+) -->
<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <include domain="sharedpref" path="." />
        <exclude domain="sharedpref" path="secret_prefs.xml" />
    </cloud-backup>
    <device-transfer>
        <include domain="sharedpref" path="." />
    </device-transfer>
</data-extraction-rules>
```

---

## Activity

```xml
<activity
    android:name=".ui.MainActivity"
    android:exported="true"
    android:label="@string/app_name"
    android:theme="@style/Theme.MyApp.NoActionBar"
    android:launchMode="singleTop"
    android:screenOrientation="portrait"
    android:windowSoftInputMode="adjustResize"
    android:configChanges="orientation|screenSize|keyboardHidden">

    <!-- LAUNCHER: Точка входа -->
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>

    <!-- Deep Link -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="https"
            android:host="example.com"
            android:pathPrefix="/user" />
    </intent-filter>

    <!-- Custom Scheme -->
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="myapp" android:host="open" />
    </intent-filter>

</activity>
```

### Атрибуты Activity

| Атрибут | Значение | Когда использовать |
|---------|----------|-------------------|
| `android:exported` | `true/false` | `true` если принимает Intent извне |
| `android:launchMode` | `standard/singleTop/singleTask/singleInstance` | Управление стеком |
| `android:screenOrientation` | `portrait/landscape/sensor` | Фиксация ориентации |
| `android:windowSoftInputMode` | `adjustResize/adjustPan` | Поведение клавиатуры |
| `android:configChanges` | `orientation\|screenSize` | Не пересоздавать при изменениях |
| `android:parentActivityName` | `.ParentActivity` | Up navigation |

### Launch Modes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         LAUNCH MODES                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  standard (default):                                                    │
│  Каждый Intent создаёт новый instance                                   │
│  [A] → [A, B] → [A, B, B] → [A, B, B, B]                               │
│                                                                         │
│  singleTop:                                                             │
│  Если Activity на вершине стека — переиспользуется (onNewIntent)       │
│  [A] → [A, B] → Intent(B) → [A, B] (onNewIntent)                       │
│  [A] → [A, B] → Intent(A) → [A, B, A] (новый instance)                 │
│                                                                         │
│  singleTask:                                                            │
│  Только один instance в task. Если существует — поднимается наверх     │
│  [A, B, C] → Intent(A) → [A] (B и C уничтожены)                        │
│                                                                         │
│  singleInstance:                                                        │
│  Один instance в отдельном task. Другие Activity в другом task         │
│  Task1: [A, B]  Task2: [C (singleInstance)]                            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Deep Links и App Links

```xml
<!-- Deep Link (любое приложение может обработать) -->
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="myapp" android:host="profile" />
    <!-- myapp://profile/123 -->
</intent-filter>

<!-- App Link (только верифицированное приложение) -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="example.com"
        android:pathPattern="/user/.*" />
    <!-- https://example.com/user/123 -->
</intent-filter>
```

**Для App Links нужен Digital Asset Links файл:**
```json
// https://example.com/.well-known/assetlinks.json
[{
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
        "namespace": "android_app",
        "package_name": "com.example.myapp",
        "sha256_cert_fingerprints": [
            "AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99"
        ]
    }
}]
```

---

## Service

```xml
<!-- Foreground Service -->
<service
    android:name=".service.MusicPlayerService"
    android:exported="false"
    android:foregroundServiceType="mediaPlayback">
</service>

<!-- Background Service (ограничен начиная с Android 8) -->
<service
    android:name=".service.SyncService"
    android:exported="false">
</service>

<!-- Bound Service для IPC -->
<service
    android:name=".service.MessengerService"
    android:exported="true"
    android:permission="com.example.permission.BIND_SERVICE">
    <intent-filter>
        <action android:name="com.example.action.MESSENGER" />
    </intent-filter>
</service>
```

### Foreground Service Types (Android 14+)

```xml
<!-- Требуется указать тип для Foreground Service -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_CAMERA" />

<service
    android:name=".LocationTrackingService"
    android:foregroundServiceType="location"
    android:exported="false">
</service>

<!-- Несколько типов -->
<service
    android:name=".RecordingService"
    android:foregroundServiceType="camera|microphone"
    android:exported="false">
</service>
```

| Тип | Назначение | Permission |
|-----|-----------|------------|
| `camera` | Камера | `FOREGROUND_SERVICE_CAMERA` |
| `connectedDevice` | Bluetooth, USB | `FOREGROUND_SERVICE_CONNECTED_DEVICE` |
| `dataSync` | Синхронизация данных | `FOREGROUND_SERVICE_DATA_SYNC` |
| `location` | Геолокация | `FOREGROUND_SERVICE_LOCATION` |
| `mediaPlayback` | Аудио/видео | `FOREGROUND_SERVICE_MEDIA_PLAYBACK` |
| `mediaProjection` | Запись экрана | `FOREGROUND_SERVICE_MEDIA_PROJECTION` |
| `microphone` | Запись аудио | `FOREGROUND_SERVICE_MICROPHONE` |
| `phoneCall` | Звонки | `FOREGROUND_SERVICE_PHONE_CALL` |

---

## BroadcastReceiver

```xml
<!-- Статически зарегистрированный Receiver -->
<receiver
    android:name=".receiver.BootCompletedReceiver"
    android:exported="true"
    android:permission="android.permission.RECEIVE_BOOT_COMPLETED">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>

<!-- Receiver для локальных broadcast (exported=false) -->
<receiver
    android:name=".receiver.DataSyncReceiver"
    android:exported="false">
    <intent-filter>
        <action android:name="com.example.action.DATA_SYNCED" />
    </intent-filter>
</receiver>
```

### Ограничения на Implicit Broadcasts (Android 8+)

```
┌─────────────────────────────────────────────────────────────────────────┐
│           ОГРАНИЧЕНИЯ IMPLICIT BROADCASTS (Android 8+)                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Запрещено регистрировать в манифесте:                                  │
│  ✗ ACTION_PACKAGE_ADDED (кроме собственного пакета)                    │
│  ✗ ACTION_PACKAGE_REMOVED                                               │
│  ✗ CONNECTIVITY_ACTION                                                  │
│  ✗ ACTION_NEW_PICTURE                                                   │
│  ✗ ACTION_NEW_VIDEO                                                     │
│                                                                         │
│  Разрешено:                                                             │
│  ✓ ACTION_BOOT_COMPLETED                                                │
│  ✓ ACTION_LOCALE_CHANGED                                                │
│  ✓ ACTION_USB_ACCESSORY_ATTACHED                                        │
│  ✓ SMS_RECEIVED_ACTION (с разрешением)                                  │
│  ✓ Explicit broadcasts (с указанием package)                           │
│                                                                         │
│  Альтернатива: регистрация динамически в коде                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## ContentProvider

```xml
<provider
    android:name=".provider.NotesProvider"
    android:authorities="com.example.myapp.notes"
    android:exported="false"
    android:grantUriPermissions="true">

    <!-- Path permissions для fine-grained контроля -->
    <path-permission
        android:pathPrefix="/public"
        android:readPermission="com.example.permission.READ_NOTES"
        android:writePermission="com.example.permission.WRITE_NOTES" />

</provider>

<!-- FileProvider для шаринга файлов -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

### FileProvider paths

```xml
<!-- res/xml/file_paths.xml -->
<?xml version="1.0" encoding="utf-8"?>
<paths>
    <!-- getFilesDir() -->
    <files-path name="internal_files" path="shared/" />

    <!-- getCacheDir() -->
    <cache-path name="cache" path="images/" />

    <!-- getExternalFilesDir() -->
    <external-files-path name="external_files" path="documents/" />

    <!-- getExternalCacheDir() -->
    <external-cache-path name="external_cache" path="." />

    <!-- Environment.getExternalStorageDirectory() (deprecated) -->
    <external-path name="external" path="Download/" />

    <!-- MediaStore (API 29+) -->
    <external-media-path name="media" path="." />
</paths>
```

---

## Permissions

### Объявление используемых разрешений

```xml
<!-- Обычные разрешения (автоматически предоставляются) -->
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
<uses-permission android:name="android.permission.VIBRATE" />

<!-- Опасные разрешения (требуют запроса у пользователя) -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.READ_CONTACTS" />

<!-- Разрешение только для определённых API levels -->
<uses-permission
    android:name="android.permission.READ_EXTERNAL_STORAGE"
    android:maxSdkVersion="32" />

<!-- Разрешение для Foreground Service -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION" />

<!-- POST_NOTIFICATIONS (Android 13+) -->
<uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
```

### Создание собственных разрешений

```xml
<!-- Объявление кастомного разрешения -->
<permission
    android:name="com.example.myapp.permission.ACCESS_PREMIUM"
    android:label="@string/permission_label"
    android:description="@string/permission_description"
    android:protectionLevel="signature" />

<!-- Использование кастомного разрешения -->
<activity
    android:name=".PremiumActivity"
    android:permission="com.example.myapp.permission.ACCESS_PREMIUM"
    android:exported="true">
</activity>
```

| protectionLevel | Описание |
|-----------------|----------|
| `normal` | Автоматически предоставляется |
| `dangerous` | Требует подтверждения пользователя |
| `signature` | Только приложения с тем же ключом подписи |
| `signatureOrSystem` | Signature или системные приложения |

---

## uses-feature

```xml
<!-- Обязательные возможности устройства -->
<uses-feature android:name="android.hardware.camera" android:required="true" />
<uses-feature android:name="android.hardware.camera.autofocus" android:required="false" />

<!-- OpenGL ES версия -->
<uses-feature android:glEsVersion="0x00030000" android:required="true" />

<!-- Сенсоры -->
<uses-feature android:name="android.hardware.sensor.accelerometer" android:required="false" />
<uses-feature android:name="android.hardware.sensor.gyroscope" android:required="false" />

<!-- Связь -->
<uses-feature android:name="android.hardware.telephony" android:required="false" />
<uses-feature android:name="android.hardware.bluetooth" android:required="false" />
<uses-feature android:name="android.hardware.nfc" android:required="false" />
```

**Важно:** Некоторые permissions неявно требуют features:
```xml
<!-- CAMERA permission неявно добавляет: -->
<!-- <uses-feature android:name="android.hardware.camera" android:required="true" /> -->

<!-- Чтобы работать на устройствах без камеры: -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera" android:required="false" />
```

---

## Manifest Merger

При сборке манифесты из разных источников объединяются.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       MANIFEST MERGER                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Приоритет (высший → низший):                                           │
│                                                                         │
│  1. Build variant manifest (src/debug/AndroidManifest.xml)             │
│  2. Main manifest (src/main/AndroidManifest.xml)                       │
│  3. Library manifests (AAR dependencies)                               │
│  4. Gradle-injected values (applicationId, versionCode, etc.)          │
│                                                                         │
│  Конфликты решаются:                                                    │
│  • tools:replace — заменить атрибут                                     │
│  • tools:remove — удалить атрибут                                       │
│  • tools:node="remove" — удалить элемент целиком                       │
│  • tools:node="replace" — заменить элемент целиком                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Решение конфликтов

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- Заменить значение из библиотеки -->
    <application
        android:allowBackup="false"
        tools:replace="android:allowBackup">

        <!-- Удалить Activity, добавленную библиотекой -->
        <activity
            android:name="com.library.UnwantedActivity"
            tools:node="remove" />

        <!-- Заменить theme из библиотеки -->
        <activity
            android:name="com.library.SomeActivity"
            android:theme="@style/MyTheme"
            tools:replace="android:theme" />

        <!-- Удалить конкретный атрибут -->
        <activity
            android:name=".MainActivity"
            tools:remove="android:screenOrientation" />

    </application>

    <!-- Удалить permission, добавленное библиотекой -->
    <uses-permission
        android:name="android.permission.WRITE_EXTERNAL_STORAGE"
        tools:node="remove" />

</manifest>
```

### Просмотр merged manifest

В Android Studio: `app/build/intermediates/merged_manifests/debug/AndroidManifest.xml`

Или через View: Build → Analyze APK → AndroidManifest.xml

---

## Meta-data

```xml
<application>
    <!-- API ключи -->
    <meta-data
        android:name="com.google.android.geo.API_KEY"
        android:value="${MAPS_API_KEY}" />

    <!-- Firebase -->
    <meta-data
        android:name="firebase_analytics_collection_enabled"
        android:value="false" />

    <!-- Кастомные meta-data -->
    <meta-data
        android:name="com.example.BUILD_TIME"
        android:value="${buildTime}" />

    <!-- Ссылка на ресурс -->
    <meta-data
        android:name="com.example.config"
        android:resource="@xml/app_config" />

    <!-- Компонент с meta-data -->
    <activity android:name=".DetailsActivity">
        <meta-data
            android:name="android.app.default_searchable"
            android:value=".SearchActivity" />
    </activity>

</application>
```

### Manifest Placeholders

```kotlin
// build.gradle.kts
android {
    defaultConfig {
        manifestPlaceholders["MAPS_API_KEY"] = "AIzaSy..."
        manifestPlaceholders["appIcon"] = "@mipmap/ic_launcher"
    }

    buildTypes {
        debug {
            manifestPlaceholders["MAPS_API_KEY"] = "DEBUG_KEY"
            manifestPlaceholders["appIcon"] = "@mipmap/ic_launcher_debug"
        }
    }
}
```

```xml
<!-- AndroidManifest.xml -->
<application android:icon="${appIcon}">
    <meta-data
        android:name="com.google.android.geo.API_KEY"
        android:value="${MAPS_API_KEY}" />
</application>
```

---

## Типичные ошибки

### 1. exported без Intent Filter

```xml
<!-- ❌ ОШИБКА: Android 12+ требует явный exported -->
<activity android:name=".InternalActivity">
    <!-- Нет intent-filter, exported не указан — ошибка сборки -->
</activity>

<!-- ✅ ПРАВИЛЬНО -->
<activity
    android:name=".InternalActivity"
    android:exported="false">
</activity>

<!-- ✅ С intent-filter обычно exported=true -->
<activity
    android:name=".DeepLinkActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:scheme="myapp" />
    </intent-filter>
</activity>
```

### 2. allowBackup без правил

```xml
<!-- ❌ ПОТЕНЦИАЛЬНАЯ УТЕЧКА: backup включает все данные -->
<application android:allowBackup="true">
</application>

<!-- ✅ ПРАВИЛЬНО: явные правила -->
<application
    android:allowBackup="true"
    android:fullBackupContent="@xml/backup_rules"
    android:dataExtractionRules="@xml/data_extraction_rules">
</application>

<!-- ✅ ИЛИ: отключить backup -->
<application android:allowBackup="false">
</application>
```

### 3. Неявные uses-feature

```xml
<!-- ❌ ПРОБЛЕМА: приложение не появится на устройствах без камеры -->
<uses-permission android:name="android.permission.CAMERA" />
<!-- Неявно добавляется: <uses-feature android:name="android.hardware.camera" required="true" /> -->

<!-- ✅ ПРАВИЛЬНО: явно указать required=false -->
<uses-permission android:name="android.permission.CAMERA" />
<uses-feature android:name="android.hardware.camera" android:required="false" />
```

### 4. Hardcoded strings

```xml
<!-- ❌ ПЛОХО: hardcoded -->
<activity android:label="My Activity">
</activity>

<!-- ✅ ПРАВИЛЬНО: ресурс -->
<activity android:label="@string/activity_label">
</activity>
```

---

## Проверь себя

<details>
<summary>1. В чём разница между namespace и applicationId?</summary>

**Ответ:**
- **namespace** — используется для генерации R класса и разрешения относительных имён компонентов (`.MainActivity`). Определяется в `build.gradle.kts`. Одинаковый для всех flavors.

- **applicationId** — уникальный идентификатор приложения в Play Store. Может отличаться для разных flavors (`.free`, `.paid`). Определяет identity приложения для системы.

</details>

<details>
<summary>2. Когда нужен exported="true"?</summary>

**Ответ:**
`exported="true"` нужен когда компонент должен быть доступен извне приложения:
- Activity с LAUNCHER intent-filter
- Activity для deep links
- Service, к которому биндятся другие приложения
- BroadcastReceiver для системных broadcast
- ContentProvider, доступный другим приложениям

Начиная с Android 12, `exported` обязателен для всех компонентов с intent-filter.

</details>

<details>
<summary>3. Как решить конфликт manifest merger?</summary>

**Ответ:**
Используйте tools namespace:
- `tools:replace="android:атрибут"` — заменить значение
- `tools:remove="android:атрибут"` — удалить атрибут
- `tools:node="remove"` — удалить элемент целиком
- `tools:node="replace"` — заменить элемент целиком

Пример: библиотека устанавливает `allowBackup="true"`, а вам нужно `false`:
```xml
<application
    android:allowBackup="false"
    tools:replace="android:allowBackup">
```

</details>

<details>
<summary>4. Какие foregroundServiceType доступны и зачем они нужны?</summary>

**Ответ:**
Начиная с Android 14, Foreground Service должен явно указывать тип:
- `camera` — использование камеры
- `location` — доступ к геолокации
- `mediaPlayback` — воспроизведение аудио/видео
- `microphone` — запись аудио
- `dataSync` — синхронизация данных

Для каждого типа нужно соответствующее permission (`FOREGROUND_SERVICE_*`). Это ограничивает возможности service и повышает прозрачность для пользователя.

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "AndroidManifest.xml — просто конфиг" | Manifest — это контракт между приложением и системой. От него зависит: какие компоненты запускаются, какие разрешения запрашиваются, совместимость с устройствами, visibility в Play Store |
| "Один манифест на приложение" | Каждый модуль может иметь свой манифест. AGP объединяет их при сборке (Manifest Merger). Порядок приоритета: app > library > aar dependencies |
| "tools: атрибуты только для IDE" | tools:replace, tools:remove, tools:node — это директивы для Manifest Merger. Они определяют, как разрешать конфликты между манифестами модулей |
| "Deep Links и App Links — одно и то же" | Deep Links (//) работают без верификации, показывают chooser dialog. App Links (https://) требуют Digital Asset Links file на сервере, открываются напрямую в приложении |
| "exported=true безопасно для internal компонентов" | exported=true делает компонент доступным для ЛЮБОГО приложения. Для internal компонентов всегда exported=false или protection level signature |
| "Foreground Service не требует типа" | С Android 14 (API 34) foregroundServiceType обязателен. Без него сервис не запустится. Каждый тип требует соответствующее FOREGROUND_SERVICE_* permission |
| "minSdk влияет только на API" | minSdk определяет: доступные API, compile-time оптимизации R8, фильтрацию в Play Store, размер DEX (multidex не нужен с API 21+) |
| "uses-feature всегда required=true" | По умолчанию required=true, что исключает устройства без фичи из Play Store. Для опциональных фич (камера, GPS) часто нужен required=false с runtime проверкой |
| "ContentProvider только для sharing данных" | ContentProvider используется для: FileProvider (sharing файлов), startup initialization (App Startup), cross-app data access. Это универсальный механизм инициализации и доступа |
| "Manifest не влияет на производительность" | Неправильная конфигурация влияет: лишние permissions увеличивают attack surface, отсутствие largeHeap замедляет memory-intensive операции, configChanges предотвращают recreation |

---

## CS-фундамент

| CS-концепция | Применение в AndroidManifest.xml |
|--------------|----------------------------------|
| **Декларативное программирование** | Manifest декларирует структуру приложения (что), а не поведение (как). Система интерпретирует декларации и создаёт runtime environment |
| **Contract Programming** | Manifest — контракт между приложением и Android system. Нарушение контракта (missing permission, wrong export) приводит к runtime errors |
| **Schema Validation** | XML Schema определяет valid elements и attributes. AGP валидирует manifest при сборке, ошибки блокируют компиляцию |
| **Merge Strategy Pattern** | Manifest Merger реализует configurable merge strategy. tools: namespace управляет стратегией для каждого элемента (replace, remove, merge) |
| **URI Scheme (RFC 3986)** | Deep Links используют URI structure: scheme://host/path?query. Intent filters pattern-match по каждому компоненту |
| **Digital Signatures** | App Links verification использует PKI: Digital Asset Links JSON на сервере содержит SHA256 fingerprint сертификата приложения |
| **Access Control Lists** | Permissions реализуют ACL: каждое permission — право на действие. exported + permission = role-based access control |
| **Capability-based Security** | uses-feature декларирует capabilities. Система фильтрует приложения по capabilities устройства (hardware features) |
| **Component Model** | Android components (Activity, Service, etc.) — реализация component model. Manifest регистрирует компоненты в системе |
| **Declarative Configuration** | Intent filters декларативно описывают, какие Intents обрабатывает компонент. Система выполняет matching без кода приложения |

---

## Связи

**Компоненты:**
- [[android-app-components]] — Activity, Service, BroadcastReceiver, ContentProvider
- [[android-navigation]] — Deep links, App links

**Безопасность:**
- [[android-permissions-security]] — Runtime permissions, защита данных

**Структура:**
- [[android-project-structure]] — организация проекта
- [[android-gradle-fundamentals]] — конфигурация сборки

---

## Источники

- [App manifest overview - Android Developers](https://developer.android.com/guide/topics/manifest/manifest-intro)
- [Manifest element reference - Android Developers](https://developer.android.com/guide/topics/manifest/manifest-element)
- [Manage manifest files - Android Developers](https://developer.android.com/build/manage-manifests)
- [App Links - Android Developers](https://developer.android.com/training/app-links)
- [Foreground services - Android Developers](https://developer.android.com/develop/background-work/services/foreground-services)

---

*Проверено: 2026-01-09 | На основе официальной документации Android*
