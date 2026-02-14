---
title: "Android APK и AAB: форматы пакетов и дистрибуция"
created: 2025-01-15
modified: 2026-02-13
type: deep-dive
status: published
cs-foundations: [package-formats, code-signing, compression, resource-bundling]
tags:
  - topic/android
  - topic/build-system
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-proguard-r8]]"
  - "[[android-compilation-pipeline]]"
  - "[[android-resources-system]]"
  - "[[android-gradle-fundamentals]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-gradle-fundamentals]]"
  - "[[android-project-structure]]"
reading_time: 67
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Android APK и AAB: Форматы пакетов и App Distribution

> Полное руководство по форматам пакетов Android: структура APK, Android App Bundle, подписание, оптимизация размера и App Distribution.

---

## Зачем это нужно

### Проблема: "Собрал APK — и что дальше?"

Многие разработчики знают, как нажать "Build APK", но не понимают:

| Вопрос | Почему важно |
|--------|--------------|
| **APK vs AAB — в чём разница?** | С августа 2021 AAB обязателен для Google Play |
| **Почему APK такой большой?** | Содержит ресурсы для ВСЕХ устройств |
| **Как работает подпись?** | Без правильной подписи — нет обновлений |
| **Что такое Play App Signing?** | Google управляет ключом — есть плюсы и риски |

### Актуальность в 2024-2025

**Требования Google Play:**
- **AAB обязателен** для всех новых приложений
- **Play App Signing** — требуется для AAB
- **35% экономия** размера по сравнению с Universal APK
- **Dynamic Features** — загрузка модулей по требованию

### Кому и когда это нужно

| Ситуация | Формат |
|----------|--------|
| Публикация в Google Play | AAB (обязательно) |
| Тестирование на устройстве | APK (Debug или local AAB → APK) |
| Сторонние магазины (F-Droid, Huawei) | APK или AAB (зависит от магазина) |
| Enterprise distribution | APK (с собственной подписью) |
| Альтернативные маркеты (Amazon) | APK или AAB |

### Что даёт понимание форматов

```
Без понимания:                     С пониманием:
┌──────────────────┐               ┌──────────────────┐
│ APK: 80 MB       │               │ APK per device:  │
│ "Почему так?"    │               │ ~30 MB (-60%)    │
│ Ключ потерян     │               │ Play App Signing │
│ Нет обновлений!  │               │ всё под контролем│
└──────────────────┘               └──────────────────┘
```

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **APK** | Android Package — формат установочного пакета Android |
| **AAB** | Android App Bundle — формат публикации для Google Play |
| **Split APK** | Отдельный APK для конкретной конфигурации (density, ABI, language) |
| **Base APK** | Основной APK с core функциональностью в split delivery |
| **DEX** | Dalvik Executable — bytecode для Android Runtime |
| **resources.arsc** | Скомпилированная таблица ресурсов |
| **Signing** | Цифровая подпись для верификации и безопасности |
| **Keystore** | Хранилище ключей для подписи |
| **zipalign** | Оптимизация выравнивания данных в APK |
| **bundletool** | CLI инструмент для работы с AAB |
| **Dynamic Feature** | Модуль загружаемый по требованию (on-demand) |
| **Play Asset Delivery** | Система доставки больших assets через Play Store |

---

## APK: Структура и Формат

### APK — это ZIP архив

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           APK FILE STRUCTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  app-release.apk (ZIP archive)                                              │
│  │                                                                          │
│  ├── META-INF/                    # Signing информация                     │
│  │   ├── MANIFEST.MF              # Список файлов с их checksums           │
│  │   ├── CERT.SF                  # Подписанный manifest (v1)              │
│  │   └── CERT.RSA                 # Сертификат подписи                     │
│  │                                                                          │
│  ├── classes.dex                  # Основной DEX файл                      │
│  ├── classes2.dex                 # Дополнительные DEX (multidex)          │
│  ├── classes3.dex                 # ...                                    │
│  │                                                                          │
│  ├── AndroidManifest.xml          # Binary XML (не текстовый!)             │
│  ├── resources.arsc               # Compiled resource table                │
│  │                                                                          │
│  ├── res/                         # Ресурсы (layouts, drawables, etc.)     │
│  │   ├── layout/                  # XML layouts (binary)                   │
│  │   ├── drawable-hdpi/           # Drawables для hdpi                     │
│  │   ├── drawable-xxhdpi/         # Drawables для xxhdpi                   │
│  │   ├── values/                  # Не хранится! → в resources.arsc       │
│  │   └── ...                                                               │
│  │                                                                          │
│  ├── assets/                      # Raw assets (не обрабатываются)         │
│  │   ├── fonts/                                                            │
│  │   ├── databases/                                                        │
│  │   └── ...                                                               │
│  │                                                                          │
│  ├── lib/                         # Native libraries                       │
│  │   ├── armeabi-v7a/             # ARM 32-bit                             │
│  │   │   └── libnative.so                                                  │
│  │   ├── arm64-v8a/               # ARM 64-bit                             │
│  │   │   └── libnative.so                                                  │
│  │   ├── x86/                     # Intel 32-bit                           │
│  │   │   └── libnative.so                                                  │
│  │   └── x86_64/                  # Intel 64-bit                           │
│  │       └── libnative.so                                                  │
│  │                                                                          │
│  └── kotlin/                      # Kotlin metadata (если есть)            │
│      └── *.kotlin_module                                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Подробнее о компонентах

#### classes.dex

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DEX FILE STRUCTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  classes.dex                                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Header                                                             │   │
│  │  ├── magic: "dex\n039\0"     # DEX версия (039 = Android 9+)       │   │
│  │  ├── checksum                # Adler-32 для проверки целостности   │   │
│  │  ├── signature               # SHA-1 (20 bytes)                    │   │
│  │  ├── file_size               # Полный размер файла                 │   │
│  │  └── ...offsets to sections                                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  String IDs                  # Таблица строковых литералов         │   │
│  │  Type IDs                    # Таблица типов (классов)             │   │
│  │  Proto IDs                   # Прототипы методов (signatures)      │   │
│  │  Field IDs                   # Таблица полей                       │   │
│  │  Method IDs                  # Таблица методов                     │   │
│  │  Class Defs                  # Определения классов                 │   │
│  │  Call Site IDs               # Для invokedynamic (lambdas)         │   │
│  │  Method Handles              # Для invokedynamic                   │   │
│  │  Data                        # Bytecode, annotations, debug info   │   │
│  │  Link Data                   # Данные для линковки                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Ограничения (до multidex):                                                │
│  • Max 65,536 method references per DEX                                    │
│  • Max 65,536 field references per DEX                                     │
│  • Max 65,536 type references per DEX                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### resources.arsc

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RESOURCES.ARSC STRUCTURE                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  resources.arsc — бинарная таблица ресурсов                                │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Resource Table Header                                              │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  String Pool                 # Все строковые значения               │   │
│  │  ├── "Hello World"                                                  │   │
│  │  ├── "Settings"                                                     │   │
│  │  ├── "res/drawable-hdpi/icon.png"                                   │   │
│  │  └── ...                                                            │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  Package Chunk              # Один или несколько packages           │   │
│  │  ├── Package Header                                                 │   │
│  │  ├── Type String Pool       # "drawable", "layout", "string"...    │   │
│  │  ├── Key String Pool        # "app_name", "icon", "main_activity" │   │
│  │  └── Type Specs + Types     # Конфигурации и значения              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Как работает R.id.button:                                                 │
│  R.id.button = 0x7f0a0001                                                  │
│  │             │  │  │                                                     │
│  │             │  │  └── Entry index (1)                                   │
│  │             │  └── Type index (0x0a = id)                               │
│  │             └── Package ID (0x7f = app)                                 │
│  └── 0x01-0x7e = system, 0x7f = app, 0x80+ = shared libs                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### AndroidManifest.xml (Binary)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      BINARY MANIFEST FORMAT                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  В APK AndroidManifest.xml — НЕ текстовый XML!                             │
│                                                                             │
│  Преобразование:                                                            │
│  ┌─────────────────┐      AAPT2      ┌─────────────────┐                   │
│  │ Text XML        │ ─────────────▶  │ Binary XML      │                   │
│  │ (source)        │   Compile       │ (APK)           │                   │
│  └─────────────────┘                 └─────────────────┘                   │
│                                                                             │
│  Binary XML структура:                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  XML Header                                                         │   │
│  │  String Pool            # Все строки: тэги, атрибуты, значения     │   │
│  │  Resource IDs           # Ссылки на resources.arsc                  │   │
│  │  XML Tree               # Сам XML как дерево токенов                │   │
│  │  ├── START_NAMESPACE    # xmlns:android="..."                       │   │
│  │  ├── START_ELEMENT      # <manifest ...>                            │   │
│  │  ├── START_ELEMENT      #   <application ...>                       │   │
│  │  ├── START_ELEMENT      #     <activity ...>                        │   │
│  │  ├── END_ELEMENT        #     </activity>                           │   │
│  │  ├── END_ELEMENT        #   </application>                          │   │
│  │  ├── END_ELEMENT        # </manifest>                               │   │
│  │  └── END_NAMESPACE                                                  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Как посмотреть текстовый:                                                 │
│  $ aapt2 dump xmltree app.apk --file AndroidManifest.xml                   │
│  # или                                                                      │
│  $ apktool d app.apk  # декомпилирует в текстовый XML                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Просмотр содержимого APK

```bash
# Как ZIP архив
unzip -l app-release.apk

# AAPT2 dump
aapt2 dump badging app.apk           # Package info, permissions, features
aapt2 dump permissions app.apk       # Только permissions
aapt2 dump resources app.apk         # Resources table
aapt2 dump xmltree app.apk AndroidManifest.xml  # Manifest как дерево

# Android Studio
# Build → Analyze APK...

# Размер компонентов
aapt2 dump resources app.apk | head -100
```

---

## AAB: Android App Bundle

### Почему AAB?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APK VS AAB COMPARISON                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Проблема с Universal APK:                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  Universal APK (25 MB)                                              │   │
│  │  ├── lib/armeabi-v7a/    (3 MB)  ─┐                                │   │
│  │  ├── lib/arm64-v8a/      (4 MB)   │ Только одна ABI используется   │   │
│  │  ├── lib/x86/            (3 MB)   │ на конкретном устройстве       │   │
│  │  ├── lib/x86_64/         (4 MB)  ─┘                                │   │
│  │  ├── res/drawable-mdpi/  (1 MB)  ─┐                                │   │
│  │  ├── res/drawable-hdpi/  (2 MB)   │ Только одна density            │   │
│  │  ├── res/drawable-xhdpi/ (3 MB)   │ используется                   │   │
│  │  ├── res/drawable-xxhdpi/(4 MB)  ─┘                                │   │
│  │  └── res/values-*/       (1 MB)    # Все языки                     │   │
│  │                                                                     │   │
│  │  Реально используется: ~8 MB из 25 MB = 32%                        │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Решение с AAB:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  AAB ──▶ Google Play ──▶ Optimized APK для устройства             │   │
│  │                                                                     │   │
│  │  Pixel 7 (arm64-v8a, xxhdpi, en):                                  │   │
│  │  base.apk (5 MB)                                                    │   │
│  │  ├── classes.dex                                                    │   │
│  │  ├── lib/arm64-v8a/      (4 MB)  ← только нужная ABI              │   │
│  │  ├── res/drawable-xxhdpi/(4 MB)  ← только нужная density          │   │
│  │  └── res/values/         (100 KB) ← только en                      │   │
│  │                                                                     │   │
│  │  Загружается: ~8 MB (вместо 25 MB) = экономия 68%                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AAB Структура

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AAB FILE STRUCTURE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  app-release.aab (ZIP archive)                                              │
│  │                                                                          │
│  ├── BundleConfig.pb            # Конфигурация bundle (protobuf)           │
│  │                                                                          │
│  ├── base/                      # Base module (всегда устанавливается)     │
│  │   ├── manifest/                                                          │
│  │   │   └── AndroidManifest.xml  # Text XML (не binary!)                  │
│  │   ├── dex/                                                               │
│  │   │   ├── classes.dex                                                    │
│  │   │   └── classes2.dex                                                   │
│  │   ├── res/                     # Ресурсы (как в APK)                    │
│  │   ├── assets/                                                            │
│  │   ├── lib/                     # Native libraries                       │
│  │   │   ├── armeabi-v7a/                                                   │
│  │   │   └── arm64-v8a/                                                     │
│  │   ├── root/                    # Файлы в корень APK                     │
│  │   └── resources.pb            # Resource table (protobuf)               │
│  │                                                                          │
│  ├── feature1/                  # Dynamic Feature module                   │
│  │   ├── manifest/                                                          │
│  │   ├── dex/                                                               │
│  │   ├── res/                                                               │
│  │   └── resources.pb                                                       │
│  │                                                                          │
│  ├── asset_pack_1/              # Play Asset Delivery                      │
│  │   └── assets/                                                            │
│  │                                                                          │
│  └── BUNDLE-METADATA/           # Metadata                                 │
│      ├── com.android.tools.build.libraries/                                │
│      └── com.android.tools.build.obfuscation/                              │
│          └── proguard.map                                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### AAB vs APK: Ключевые отличия

| Аспект | APK | AAB |
|--------|-----|-----|
| Формат | Готовый к установке | Публикационный формат |
| Manifest | Binary XML | Text XML |
| Resources | resources.arsc | resources.pb (protobuf) |
| Установка | Напрямую | Через Google Play |
| Split delivery | Нет | Да |
| Dynamic features | Нет | Да |
| Размер загрузки | Universal | Оптимизирован под устройство |
| Подпись | Разработчик | Google Play (App Signing) |

### Генерация AAB

```kotlin
// app/build.gradle.kts
android {
    bundle {
        language {
            // Включить split по языкам (default: true)
            enableSplit = true
        }
        density {
            // Включить split по density (default: true)
            enableSplit = true
        }
        abi {
            // Включить split по ABI (default: true)
            enableSplit = true
        }
    }
}
```

```bash
# Сборка AAB
./gradlew bundleRelease

# Результат:
# app/build/outputs/bundle/release/app-release.aab
```

---

## Split APKs и Dynamic Delivery

### Типы Split APKs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SPLIT APK TYPES                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Когда AAB загружается на Google Play, генерируются Split APKs:            │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Base APK (base-master.apk)                                         │   │
│  │  ├── Core code (classes.dex)                                        │   │
│  │  ├── Core resources                                                 │   │
│  │  └── AndroidManifest.xml                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Configuration APKs (устанавливаются автоматически)                 │   │
│  │  ├── base-arm64_v8a.apk      # ABI split                           │   │
│  │  ├── base-xxhdpi.apk         # Density split                       │   │
│  │  └── base-en.apk             # Language split                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Dynamic Feature APKs (загружаются on-demand)                       │   │
│  │  ├── feature1-master.apk                                            │   │
│  │  ├── feature1-arm64_v8a.apk                                         │   │
│  │  └── feature1-xxhdpi.apk                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Все APKs устанавливаются как один app:                                    │
│  pm install-create → pm install-write (multiple) → pm install-commit       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Dynamic Feature Modules

```kotlin
// settings.gradle.kts
include(":app")
include(":feature:camera")
include(":feature:ar")

// feature/camera/build.gradle.kts
plugins {
    id("com.android.dynamic-feature")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.example.feature.camera"

    defaultConfig {
        minSdk = 24
    }
}

dependencies {
    // Dynamic feature зависит от app module
    implementation(project(":app"))
}
```

```xml
<!-- feature/camera/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:dist="http://schemas.android.com/apk/distribution">

    <dist:module
        dist:instant="false"
        dist:title="@string/title_camera">

        <dist:delivery>
            <!-- On-demand: загружается когда нужно -->
            <dist:on-demand />
        </dist:delivery>

        <dist:fusing dist:include="true" />
    </dist:module>

    <application>
        <activity android:name=".CameraActivity" />
    </application>
</manifest>
```

### Загрузка Dynamic Features

```kotlin
// В app module
class MainActivity : AppCompatActivity() {
    private lateinit var splitInstallManager: SplitInstallManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        splitInstallManager = SplitInstallManagerFactory.create(this)
    }

    fun loadCameraFeature() {
        val request = SplitInstallRequest.newBuilder()
            .addModule("camera")
            .build()

        splitInstallManager.startInstall(request)
            .addOnSuccessListener { sessionId ->
                // Начата загрузка
            }
            .addOnFailureListener { exception ->
                // Ошибка
            }

        // Отслеживание прогресса
        splitInstallManager.registerListener { state ->
            when (state.status()) {
                SplitInstallSessionStatus.DOWNLOADING -> {
                    val progress = state.bytesDownloaded() * 100 / state.totalBytesToDownload()
                    updateProgress(progress)
                }
                SplitInstallSessionStatus.INSTALLED -> {
                    // Модуль установлен, можно использовать
                    launchCameraActivity()
                }
                SplitInstallSessionStatus.FAILED -> {
                    // Обработка ошибки
                }
            }
        }
    }

    private fun launchCameraActivity() {
        // Запуск activity из dynamic feature
        val intent = Intent()
        intent.setClassName(
            packageName,
            "com.example.feature.camera.CameraActivity"
        )
        startActivity(intent)
    }
}
```

### Delivery Modes

```xml
<!-- Режимы доставки Dynamic Features -->

<!-- 1. Install-time: устанавливается вместе с app -->
<dist:delivery>
    <dist:install-time />
</dist:delivery>

<!-- 2. On-demand: загружается по запросу -->
<dist:delivery>
    <dist:on-demand />
</dist:delivery>

<!-- 3. Conditional: зависит от условий устройства -->
<dist:delivery>
    <dist:install-time>
        <dist:conditions>
            <!-- Только для устройств с минимум 4GB RAM -->
            <dist:device-feature dist:name="android.hardware.ram.low"
                                 dist:value="false" />
            <!-- Только для определённых стран -->
            <dist:user-countries dist:exclude="false">
                <dist:country dist:code="US" />
                <dist:country dist:code="GB" />
            </dist:user-countries>
        </dist:conditions>
    </dist:install-time>
</dist:delivery>
```

---

## Play Asset Delivery (PAD)

### Для чего нужен PAD

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PLAY ASSET DELIVERY                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Проблема:                                                                  │
│  • Игры с большими assets (текстуры, модели, видео)                        │
│  • APK/AAB лимит: 150 MB base + 2 GB asset packs                           │
│  • Раньше: APK Expansion Files (.obb) — устаревшее решение                │
│                                                                             │
│  Решение — Play Asset Delivery:                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  AAB с Asset Packs                                                  │   │
│  │  ├── base/ (150 MB max)                                            │   │
│  │  ├── asset_pack_install_time/ (устанавливается сразу)             │   │
│  │  ├── asset_pack_fast_follow/ (сразу после установки)              │   │
│  │  └── asset_pack_on_demand/ (по запросу)                           │   │
│  │                                                                     │   │
│  │  Общий лимит: 2 GB для asset packs                                 │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Delivery Modes:                                                            │
│  • install-time: вместе с APK, в internal storage                         │
│  • fast-follow: автоматически после установки                             │
│  • on-demand: когда приложение запрашивает                                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Создание Asset Pack

```kotlin
// settings.gradle.kts
include(":app")
include(":assetpack") // Asset pack module

// assetpack/build.gradle.kts
plugins {
    id("com.android.asset-pack")
}

assetPack {
    packName.set("level_textures")
    dynamicDelivery {
        deliveryType.set("on-demand")
    }
}
```

```
// Структура asset pack
assetpack/
├── build.gradle.kts
└── src/main/assets/
    ├── level1/
    │   ├── textures/
    │   └── models/
    └── level2/
        ├── textures/
        └── models/
```

### Использование Asset Pack

```kotlin
class GameActivity : AppCompatActivity() {
    private lateinit var assetPackManager: AssetPackManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        assetPackManager = AssetPackManagerFactory.getInstance(this)
    }

    fun loadLevelAssets(level: String) {
        val packName = "level_textures"

        // Проверить статус
        val location = assetPackManager.getPackLocation(packName)

        if (location != null) {
            // Assets уже загружены
            val assetsPath = location.assetsPath()
            loadAssetsFromPath("$assetsPath/$level")
        } else {
            // Нужно загрузить
            requestAssetPack(packName)
        }
    }

    private fun requestAssetPack(packName: String) {
        assetPackManager.fetch(listOf(packName))
            .addOnSuccessListener {
                // Начата загрузка
            }

        // Отслеживание
        assetPackManager.registerListener { state ->
            val status = state.packStates()[packName]?.status()

            when (status) {
                AssetPackStatus.COMPLETED -> {
                    val location = assetPackManager.getPackLocation(packName)
                    // Использовать assets
                }
                AssetPackStatus.DOWNLOADING -> {
                    // Показать прогресс
                }
            }
        }
    }
}
```

---

## APK Signing

### Зачем нужна подпись

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APK SIGNING PURPOSE                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Идентификация разработчика                                             │
│     • Все APK от одного разработчика подписаны одним ключом               │
│     • Android проверяет при обновлении app                                 │
│                                                                             │
│  2. Целостность                                                             │
│     • Гарантия что APK не изменён после подписи                           │
│     • Защита от tampering                                                  │
│                                                                             │
│  3. Trust                                                                   │
│     • Signature Permissions работают только между APK с одной подписью    │
│     • Shared UID требует одинаковую подпись                                │
│                                                                             │
│  ВАЖНО:                                                                     │
│  • Потеря ключа = невозможно обновить app (новый package name)            │
│  • Утечка ключа = кто угодно может подделать ваши обновления              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Keystore и ключи

```bash
# Создание keystore
keytool -genkey -v \
    -keystore my-release-key.jks \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -alias my-key-alias

# Параметры:
# -keystore: файл хранилища
# -keyalg: алгоритм (RSA рекомендуется)
# -keysize: размер ключа (минимум 2048)
# -validity: срок действия в днях
# -alias: имя ключа в хранилище

# Просмотр содержимого keystore
keytool -list -v -keystore my-release-key.jks
```

### Signing Schemes (v1-v4)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APK SIGNING SCHEMES                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  v1 (JAR Signing) — Android 1.0+                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Подписывает отдельные файлы в ZIP                               │   │
│  │  • META-INF/MANIFEST.MF — checksums файлов                         │   │
│  │  • META-INF/*.SF — подписанный manifest                            │   │
│  │  • META-INF/*.RSA — сертификат                                     │   │
│  │                                                                     │   │
│  │  Проблема: META-INF/ не защищён, медленная верификация            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  v2 (Full APK Signing) — Android 7.0+                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Подписывает ВЕСЬ APK как blob                                   │   │
│  │  • Signing Block вставляется перед Central Directory              │   │
│  │  • Быстрая верификация (не нужно разархивировать)                 │   │
│  │  • Защита от изменения любой части APK                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  v3 (Key Rotation) — Android 9.0+                                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Всё из v2                                                        │   │
│  │  • + Proof-of-rotation: цепочка ключей                             │   │
│  │  • Позволяет ротацию signing key без потери обновлений            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  v4 (Incremental) — Android 11+                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  • Отдельный .idsig файл                                           │   │
│  │  • Merkle tree для инкрементальной верификации                    │   │
│  │  • Поддержка ADB incremental install                              │   │
│  │  • Streaming installation                                          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Рекомендация: v1 + v2 + v3 + v4 для максимальной совместимости           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Конфигурация подписи в Gradle

```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            // НЕ храните credentials в build.gradle!
            // Используйте local.properties или environment variables

            val keystorePropertiesFile = rootProject.file("keystore.properties")
            val keystoreProperties = Properties().apply {
                load(keystorePropertiesFile.inputStream())
            }

            storeFile = file(keystoreProperties["storeFile"] as String)
            storePassword = keystoreProperties["storePassword"] as String
            keyAlias = keystoreProperties["keyAlias"] as String
            keyPassword = keystoreProperties["keyPassword"] as String
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")

            // Подпись v1, v2, v3, v4
            // AGP автоматически использует все доступные схемы
        }
    }
}
```

```properties
# keystore.properties (НЕ коммитить в git!)
storeFile=../my-release-key.jks
storePassword=password123
keyAlias=my-key-alias
keyPassword=password123
```

```gitignore
# .gitignore
keystore.properties
*.jks
*.keystore
```

### Google Play App Signing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       PLAY APP SIGNING                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Традиционная схема:                                                        │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐            │
│  │  Developer    │────▶│  Google Play  │────▶│   User        │            │
│  │  signs APK    │     │  distributes  │     │   installs    │            │
│  └───────────────┘     └───────────────┘     └───────────────┘            │
│        ↑                                                                    │
│  Developer key                                                              │
│  (потеря = катастрофа)                                                     │
│                                                                             │
│  Play App Signing:                                                          │
│  ┌───────────────┐     ┌───────────────┐     ┌───────────────┐            │
│  │  Developer    │────▶│  Google Play  │────▶│   User        │            │
│  │  signs with   │     │  re-signs     │     │   installs    │            │
│  │  upload key   │     │  with app key │     │               │            │
│  └───────────────┘     └───────────────┘     └───────────────┘            │
│        ↑                      ↑                                            │
│  Upload key            App signing key                                     │
│  (можно сбросить)      (хранится у Google)                                │
│                                                                             │
│  Преимущества:                                                              │
│  • Потеря upload key ≠ потеря app (можно сбросить)                        │
│  • Google оптимизирует APK для устройств                                  │
│  • Обязательно для AAB                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## zipalign

### Что такое zipalign

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ZIPALIGN                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Проблема:                                                                  │
│  • APK — ZIP архив                                                         │
│  • ZIP хранит файлы последовательно                                        │
│  • mmap() требует выравнивание по page boundary (обычно 4KB)              │
│  • Невыровненные файлы = копирование в память (медленно, больше RAM)     │
│                                                                             │
│  zipalign выравнивает uncompressed данные на 4-byte boundary:             │
│                                                                             │
│  До zipalign:                                                               │
│  ┌────┬────────────────┬────────────────┬────────────────┐                 │
│  │hdr │ file1.png      │ file2.xml      │ file3.so       │                 │
│  └────┴────────────────┴────────────────┴────────────────┘                 │
│       ↑                 ↑                ↑                                 │
│    offset: 45       offset: 1023      offset: 2047                         │
│    (не выровнен)    (не выровнен)    (не выровнен)                        │
│                                                                             │
│  После zipalign:                                                            │
│  ┌────┬───┬────────────────┬───┬────────────────┬───┬────────────────┐    │
│  │hdr │pad│ file1.png      │pad│ file2.xml      │pad│ file3.so       │    │
│  └────┴───┴────────────────┴───┴────────────────┴───┴────────────────┘    │
│           ↑                     ↑                     ↑                    │
│       offset: 48            offset: 1024          offset: 2048             │
│       (выровнен)            (выровнен)            (выровнен)              │
│                                                                             │
│  Результат:                                                                 │
│  • mmap() работает эффективно                                             │
│  • Меньше RAM usage                                                        │
│  • Быстрее запуск                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Использование

```bash
# zipalign ПОСЛЕ подписи ломает подпись для v1!
# Правильный порядок: sign → zipalign (для v1)
# Для v2+ порядок не важен (AGP делает автоматически)

# Проверка выравнивания
zipalign -c -v 4 app.apk

# Выравнивание
zipalign -v 4 input.apk output.apk

# AGP делает это автоматически — обычно вручную не нужно
```

---

## bundletool

### Основные команды

```bash
# Установка
# https://github.com/google/bundletool/releases

# Сборка APKs из AAB
bundletool build-apks \
    --bundle=app.aab \
    --output=app.apks \
    --ks=keystore.jks \
    --ks-key-alias=my-alias \
    --ks-pass=pass:password

# Сборка APKs для конкретного устройства
bundletool build-apks \
    --bundle=app.aab \
    --output=app.apks \
    --connected-device  # Использует подключённое устройство

# Сборка universal APK (все конфигурации)
bundletool build-apks \
    --bundle=app.aab \
    --output=app.apks \
    --mode=universal

# Установка APKs на устройство
bundletool install-apks --apks=app.apks

# Извлечь APKs в директорию
bundletool extract-apks \
    --apks=app.apks \
    --output-dir=extracted/

# Информация об AAB
bundletool dump manifest --bundle=app.aab
bundletool dump resources --bundle=app.aab
bundletool dump config --bundle=app.aab
```

### Device Specification

```bash
# Получить spec текущего устройства
bundletool get-device-spec --output=device-spec.json

# device-spec.json пример:
{
  "supportedAbis": ["arm64-v8a", "armeabi-v7a"],
  "supportedLocales": ["en-US", "ru-RU"],
  "deviceFeatures": ["android.hardware.camera"],
  "screenDensity": 480,
  "sdkVersion": 33
}

# Сборка APKs для конкретной спецификации
bundletool build-apks \
    --bundle=app.aab \
    --output=app.apks \
    --device-spec=device-spec.json
```

---

## APK Analyzer

### В Android Studio

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        APK ANALYZER IN ANDROID STUDIO                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Build → Analyze APK... → Выбрать APK                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  APK Analyzer                                                        │   │
│  │  ──────────────────────────────────────────────────────────────────  │   │
│  │                                                                      │   │
│  │  Raw File Size: 15.2 MB                                             │   │
│  │  Download Size: 12.1 MB (estimated)                                 │   │
│  │                                                                      │   │
│  │  ├── classes.dex              3.2 MB   21.1%   ◀ Развернуть         │   │
│  │  │   ├── com.myapp            1.2 MB                                │   │
│  │  │   ├── kotlin               800 KB                                │   │
│  │  │   ├── androidx             600 KB                                │   │
│  │  │   └── com.google           600 KB                                │   │
│  │  │                                                                   │   │
│  │  ├── lib/                     5.1 MB   33.6%                        │   │
│  │  │   ├── arm64-v8a/           2.6 MB                                │   │
│  │  │   └── armeabi-v7a/         2.5 MB                                │   │
│  │  │                                                                   │   │
│  │  ├── res/                     4.2 MB   27.6%                        │   │
│  │  │   ├── drawable-xxhdpi/     2.1 MB                                │   │
│  │  │   ├── drawable-xhdpi/      1.1 MB                                │   │
│  │  │   └── ...                                                        │   │
│  │  │                                                                   │   │
│  │  ├── resources.arsc           1.2 MB    7.9%                        │   │
│  │  ├── assets/                  1.0 MB    6.6%                        │   │
│  │  └── META-INF/                500 KB    3.2%                        │   │
│  │                                                                      │   │
│  │  [Compare with previous APK...]                                     │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Функции:                                                                   │
│  • Размер каждого компонента                                               │
│  • DEX viewer: классы, методы, referenced methods                          │
│  • Manifest viewer                                                         │
│  • Resources viewer                                                        │
│  • Сравнение двух APK                                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### DEX Анализ

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          DEX ANALYSIS                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  classes.dex (развёрнуто)                                                  │
│  │                                                                          │
│  ├── Defined Methods: 45,231                                               │
│  ├── Referenced Methods: 78,542                                            │
│  │                                                                          │
│  ├── com.myapp.feature.user                                                │
│  │   ├── UserRepository                                                    │
│  │   │   ├── getUser(String): User         ◀ Defined                      │
│  │   │   ├── saveUser(User): void          ◀ Defined                      │
│  │   │   └── [referenced] retrofit2.Call   ◀ Referenced                    │
│  │   └── ...                                                               │
│  │                                                                          │
│  └── [Keep rules...] → Показывает какие keep rules применены              │
│                                                                             │
│  Полезно для:                                                               │
│  • Найти самые "тяжёлые" библиотеки                                        │
│  • Проверить что R8 удалил                                                 │
│  • Анализ method count (64K limit)                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Сравнение APK

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         APK COMPARISON                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Compare with... → Выбрать старый APK                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  APK Comparison                                                      │   │
│  │  ──────────────────────────────────────────────────────────────────  │   │
│  │                                                                      │   │
│  │  Old: app-v1.0.apk (14.2 MB)                                        │   │
│  │  New: app-v1.1.apk (15.2 MB)                                        │   │
│  │  Diff: +1.0 MB (+7%)                                                │   │
│  │                                                                      │   │
│  │  Changes:                                                            │   │
│  │  ├── classes.dex        +500 KB   (new: UserAnalytics class)       │   │
│  │  ├── lib/arm64-v8a/     +300 KB   (updated native lib)             │   │
│  │  ├── res/drawable/      +200 KB   (new icons)                      │   │
│  │  └── assets/            +0 KB     (no change)                      │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Используйте для:                                                          │
│  • Отслеживания роста размера между версиями                               │
│  • Выявления неожиданных изменений                                         │
│  • Проверки эффекта оптимизаций                                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Оптимизация размера APK/AAB

### Чеклист оптимизации

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      APK SIZE OPTIMIZATION CHECKLIST                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Code Shrinking                                                          │
│     □ minifyEnabled = true                                                 │
│     □ R8 Full Mode enabled                                                 │
│     □ Удалены debug logs (assumenosideeffects)                            │
│                                                                             │
│  2. Resource Shrinking                                                      │
│     □ shrinkResources = true                                               │
│     □ resConfigs ограничены нужными языками                               │
│     □ Удалены unused resources                                             │
│                                                                             │
│  3. Images                                                                  │
│     □ WebP вместо PNG/JPEG                                                 │
│     □ Vector drawables где возможно                                        │
│     □ Оптимизированы через ImageOptim/TinyPNG                             │
│     □ Правильные density buckets                                          │
│                                                                             │
│  4. Native Libraries                                                        │
│     □ Только нужные ABI (abiFilters)                                      │
│     □ Split APKs для native libs                                          │
│                                                                             │
│  5. Dependencies                                                            │
│     □ Удалены неиспользуемые dependencies                                 │
│     □ Заменены тяжёлые библиотеки на легковесные альтернативы            │
│     □ Используется AAB для split по конфигурациям                        │
│                                                                             │
│  6. Assets                                                                  │
│     □ Сжатие где возможно                                                 │
│     □ Play Asset Delivery для больших assets                              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Примеры оптимизаций

```kotlin
// app/build.gradle.kts
android {
    defaultConfig {
        // Только нужные ABI
        ndk {
            abiFilters += listOf("armeabi-v7a", "arm64-v8a")
            // Убрать x86, x86_64 если не нужны эмуляторы
        }

        // Только нужные языки
        resourceConfigurations += listOf("en", "ru")
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    // Использовать WebP
    androidResources {
        // Автоконвертация PNG в WebP
        noCompress += "webp"
    }
}
```

```xml
<!-- Использовать vector drawables -->
<!-- res/drawable/ic_icon.xml -->
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp"
    android:height="24dp"
    android:viewportWidth="24"
    android:viewportHeight="24">
    <path
        android:fillColor="#FF000000"
        android:pathData="M12,2L2,7l10,5l10,-5L12,2z"/>
</vector>
<!-- Один файл вместо 5 PNG разных density -->
```

---

## Anti-patterns и Best Practices

### Anti-patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ANTI-PATTERNS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ❌ Хранение keystore в репозитории                                        │
│     → Утечка ключа = кто угодно может подделать ваше приложение           │
│                                                                             │
│  ❌ Один APK для всех конфигураций                                         │
│     → Пользователи скачивают 50MB вместо 15MB                             │
│     → Решение: используйте AAB                                             │
│                                                                             │
│  ❌ Все native libraries в одном APK                                       │
│     → 4 ABI × 5MB = 20MB лишних данных                                    │
│     → Решение: split APKs или AAB                                         │
│                                                                             │
│  ❌ Игнорирование APK Analyzer                                             │
│     → Не видите откуда взялся размер                                      │
│     → Регулярно анализируйте и сравнивайте версии                         │
│                                                                             │
│  ❌ Хранение credentials в build.gradle                                    │
│     → Утечка при публикации кода                                          │
│     → Используйте environment variables или отдельный файл                │
│                                                                             │
│  ❌ Только v1 signing                                                       │
│     → Медленная верификация, менее безопасно                              │
│     → Используйте v1 + v2 + v3 + v4                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Best Practices

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BEST PRACTICES                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ✅ Публикуйте AAB вместо APK                                              │
│     • Автоматическая оптимизация под устройства                           │
│     • Split APKs по ABI, density, language                                 │
│     • Требование Google Play с 2021                                       │
│                                                                             │
│  ✅ Используйте Play App Signing                                           │
│     • Потеря upload key ≠ потеря приложения                               │
│     • Google управляет app signing key                                    │
│                                                                             │
│  ✅ Храните keystore безопасно                                             │
│     • Отдельное защищённое хранилище                                      │
│     • Backup в нескольких местах                                          │
│     • Ограниченный доступ                                                 │
│                                                                             │
│  ✅ Регулярно анализируйте размер                                          │
│     • APK Analyzer после каждого релиза                                   │
│     • Сравнивайте с предыдущей версией                                    │
│     • Устанавливайте бюджет размера                                       │
│                                                                             │
│  ✅ Тестируйте на реальных устройствах                                     │
│     • bundletool для генерации device-specific APKs                       │
│     • Internal App Sharing для тестирования AAB                           │
│                                                                             │
│  ✅ Используйте Dynamic Features для крупных features                      │
│     • Уменьшает initial download                                          │
│     • Загружается только когда нужно                                      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Связь с другими темами

**[[android-proguard-r8]]** — R8 является ключевым инструментом оптимизации размера APK/AAB: shrinking удаляет неиспользуемый код, obfuscation сокращает имена классов и методов, а optimization улучшает bytecode. Понимание R8 необходимо для контроля размера финального пакета и диагностики проблем (ClassNotFoundException после минификации). Изучайте параллельно с форматами пакетов.

**[[android-compilation-pipeline]]** — pipeline сборки генерирует DEX-файлы и собирает APK/AAB из скомпилированных ресурсов, bytecode и нативных библиотек. Знание этапов компиляции (javac/kotlinc -> D8/R8 -> APK packaging) объясняет структуру APK и почему AAB может быть оптимизирован для разных устройств. Рекомендуется изучить pipeline для понимания процесса от исходников до пакета.

**[[android-resources-system]]** — ресурсы (layouts, drawables, strings) компилируются AAPT2 в бинарный формат и включаются в APK как resources.arsc. Понимание системы ресурсов объясняет, почему Split APK работает (ресурсы можно разделить по density, locale, ABI) и как Configuration APKs экономят размер на устройстве.

**[[android-gradle-fundamentals]]** — Gradle и Android Gradle Plugin управляют конфигурацией сборки APK/AAB: signing configs, build types, product flavors, split configurations. Без понимания Gradle невозможно настроить правильную подпись, multi-APK delivery или dynamic feature modules.

---

## Источники и дальнейшее чтение

**Книги:**
- Meier R. (2022). Professional Android, 4th Edition. — комплексное руководство по Android-разработке, включая процесс сборки и дистрибуции приложений
- Phillips B. et al. (2022). Android Programming: The Big Nerd Ranch Guide, 5th Edition. — практический учебник с разделами по сборке, подписанию и публикации APK/AAB

**Веб-ресурсы:**

| # | Источник | Тип | Ключевой вклад |
|---|----------|-----|----------------|
| 1 | [Android App Bundle Documentation](https://developer.android.com/guide/app-bundle) | Official Docs | AAB структура и концепции |
| 2 | [App Bundle FAQ](https://developer.android.com/guide/app-bundle/faq) | Official Docs | Часто задаваемые вопросы |
| 3 | [Sign Your App](https://developer.android.com/studio/publish/app-signing) | Official Docs | Подписание и ключи |
| 4 | [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756) | Official Docs | Google управление ключами |
| 5 | [bundletool](https://github.com/google/bundletool) | GitHub | CLI для работы с AAB |
| 6 | [AAB vs APK](https://www.browserstack.com/guide/aab-file) | Blog | Сравнение форматов |
| 7 | [Complete Guide to Android App Publishing 2025](https://foresightmobile.com/blog/complete-guide-to-android-app-publishing-in-2025) | Blog | Публикация в 2025 |
| 8 | [APK Signature Scheme v2](https://source.android.com/docs/security/features/apksigning/v2) | Official Docs | Схема подписи v2 |

---

---

## Проверь себя

> [!question]- Почему Google требует AAB вместо APK для Play Store?
> AAB позволяет Dynamic Delivery: 1) Device-specific APK (только нужные resources, ABI, language) -- экономия 15-40% размера. 2) Dynamic Feature Modules -- загрузка по требованию. 3) Google подписывает финальный APK (Play App Signing). 4) Instant Apps support. APK -- один файл для всех устройств, с лишними ресурсами.

> [!question]- Сценарий: APK размером 150MB, целевой -- 50MB. Какие шаги для оптимизации?
> 1) AAB вместо APK (splits по density, ABI, language). 2) R8 с minifyEnabled и shrinkResources. 3) WebP вместо PNG для изображений. 4) Vector drawables вместо растровых иконок. 5) Dynamic Feature для редких функций. 6) Proguard rules для удаления unused libraries. 7) Android Size Analyzer plugin для анализа.


---

## Ключевые карточки

Чем AAB отличается от APK?
?
APK: final installable package для одного устройства. AAB: publishing format для Play Store. Google генерирует оптимизированные APK из AAB для каждого устройства. AAB меньше на 15-40% благодаря device-specific splits.

Что содержит APK?
?
classes.dex (код), resources.arsc (compiled resources), res/ (drawables, layouts), lib/ (native .so), assets/, META-INF/ (signature), AndroidManifest.xml. Всё в ZIP формате.

Что такое Play App Signing?
?
Google хранит upload key и signing key. Разработчик подписывает AAB upload key. Google пересоздает APK и подписывает signing key. Преимущества: Google может оптимизировать APK, key recovery при потере. Обязательно для новых приложений.

Что такое ABI Split?
?
Разделение native библиотек по CPU архитектуре: arm64-v8a, armeabi-v7a, x86, x86_64. APK содержит .so только для target ABI. Экономит 10-30MB для приложений с NDK. В AAB -- автоматически.

Как работает APK Signature?
?
v1 (JAR signature): подпись каждого файла. v2 (APK Signature Scheme): подпись всего APK как blob (быстрее verification). v3: key rotation support. v4: streaming install. Минимум v2 для Android 7+.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-proguard-r8]] | R8 для уменьшения размера APK |
| Углубиться | [[android-compilation-pipeline]] | Полный pipeline до APK |
| Смежная тема | [[ios-app-distribution]] | App distribution в iOS |
| Обзор | [[android-overview]] | Вернуться к карте раздела |


*Проверено: 2026-01-09 — Педагогический контент проверен*
