---
title: "Cross-Platform: Code Signing — Provisioning Profiles vs Keystore"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - signing
  - topic/security
  - distribution
  - type/comparison
  - level/intermediate
reading_time: 33
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-build-systems]]"
related:
  - "[[ios-code-signing]]"
  - "[[android-apk-aab]]"
  - "[[security-cryptography-fundamentals]]"
---

# Code Signing: iOS vs Android

## TL;DR

| Аспект | iOS | Android |
|--------|-----|---------|
| **Основа подписи** | Сертификат + Provisioning Profile | Keystore (.jks/.keystore) |
| **Кто выдаёт** | Apple (через Developer Portal) | Самостоятельно генерируем |
| **Срок действия** | Сертификат: 1 год, Profile: 1 год | Keystore: 25+ лет (рекомендуется) |
| **Привязка к устройствам** | Да (для Development/Ad Hoc) | Нет |
| **Количество сущностей** | 3-4 (Cert + Profile + Entitlements + App ID) | 1-2 (Keystore + Upload Key) |
| **Восстановление** | Частично возможно | Невозможно без бэкапа |
| **Облачное хранение** | Нет (только через Match) | Play App Signing |
| **Сложность** | Высокая | Низкая |
| **Типичные ошибки** | Десятки вариантов | 2-3 основных |

---

## iOS: Сертификаты + Profiles + Entitlements

### Архитектура подписи iOS

```
┌─────────────────────────────────────────────────────────────┐
│                    Apple Developer Portal                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐      │
│  │ Certificates│    │   App IDs   │    │  Devices    │      │
│  │             │    │             │    │             │      │
│  │ - Development│   │ - Bundle ID │    │ - UDIDs     │      │
│  │ - Distribution│  │ - Capabilities│  │ - 100 limit │      │
│  └──────┬──────┘    └──────┬──────┘    └──────┬──────┘      │
│         │                  │                  │              │
│         └────────────┬─────┴──────────────────┘              │
│                      ▼                                       │
│         ┌────────────────────────┐                          │
│         │  Provisioning Profile  │                          │
│         │                        │                          │
│         │  = Cert + App ID +     │                          │
│         │    Devices + Entitlements                         │
│         └────────────────────────┘                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Типы сертификатов

```
Сертификаты (Certificates)
├── Development
│   ├── iOS App Development      — для отладки на устройстве
│   └── Apple Push Services      — для тестовых push-уведомлений
│
└── Distribution
    ├── iOS Distribution         — App Store + Ad Hoc
    ├── Apple Push Services (Prod) — боевые push
    └── Apple Pay Certificate    — для Apple Pay
```

### Типы Provisioning Profiles

| Тип | Назначение | Устройства | Срок |
|-----|------------|------------|------|
| **Development** | Отладка через Xcode | До 100 UDID | 1 год |
| **Ad Hoc** | Тестирование без Xcode | До 100 UDID | 1 год |
| **App Store** | Публикация | Все (после ревью) | 1 год |
| **Enterprise** | Внутреннее распространение | Все в организации | 1 год |

### Entitlements — возможности приложения

```xml
<!-- Example.entitlements -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>aps-environment</key>
    <string>production</string>

    <key>com.apple.developer.applesignin</key>
    <array>
        <string>Default</string>
    </array>

    <key>com.apple.developer.associated-domains</key>
    <array>
        <string>applinks:example.com</string>
    </array>

    <key>keychain-access-groups</key>
    <array>
        <string>$(AppIdentifierPrefix)com.example.app</string>
    </array>
</dict>
</plist>
```

### Процесс подписи iOS

```bash
# 1. Создание CSR (Certificate Signing Request)
openssl req -new -key private.key -out CertificateSigningRequest.certSigningRequest

# 2. Загрузка в Apple Portal → получение .cer

# 3. Импорт в Keychain
security import certificate.cer -k ~/Library/Keychains/login.keychain-db

# 4. Экспорт .p12 (для CI/CD)
security export -k login.keychain -t identities -f pkcs12 -o Certificates.p12

# 5. Подпись через codesign
codesign --force --sign "iPhone Distribution: Company Name" \
         --entitlements Entitlements.plist \
         MyApp.app
```

---

## Android: Keystore + Play App Signing

### Архитектура подписи Android

```
┌─────────────────────────────────────────────────────────────┐
│                     Простая модель                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────┐         ┌─────────────────┐            │
│  │    Keystore     │         │   Google Play   │            │
│  │                 │         │   App Signing   │            │
│  │  - Private Key  │────────▶│                 │            │
│  │  - Certificate  │  upload │  - App Signing  │            │
│  │  - Alias        │   key   │    Key (хранит  │            │
│  │  - Password     │         │    Google)      │            │
│  └─────────────────┘         └─────────────────┘            │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Создание Keystore

```bash
# Генерация нового keystore
keytool -genkeypair \
    -v \
    -storetype PKCS12 \
    -keystore my-release-key.keystore \
    -alias my-key-alias \
    -keyalg RSA \
    -keysize 2048 \
    -validity 10000 \
    -storepass YOUR_STORE_PASSWORD \
    -keypass YOUR_KEY_PASSWORD \
    -dname "CN=Your Name, OU=Your Unit, O=Your Organization, L=City, ST=State, C=US"

# Проверка содержимого
keytool -list -v -keystore my-release-key.keystore

# Экспорт сертификата (для проверки)
keytool -exportcert -alias my-key-alias \
    -keystore my-release-key.keystore \
    -file certificate.pem -rfc
```

### Конфигурация в Gradle

```kotlin
// app/build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file("../keystore/release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
                ?: properties["KEYSTORE_PASSWORD"] as String
            keyAlias = System.getenv("KEY_ALIAS")
                ?: properties["KEY_ALIAS"] as String
            keyPassword = System.getenv("KEY_PASSWORD")
                ?: properties["KEY_PASSWORD"] as String
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
}
```

### Play App Signing

```
Без Play App Signing:
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Keystore │────▶│   APK    │────▶│  Users   │
│ (у вас)  │     │ (signed) │     │          │
└──────────┘     └──────────┘     └──────────┘
     │
     └── Потеряли = конец приложения

С Play App Signing:
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│ Upload   │────▶│   AAB    │────▶│  Google  │────▶│  Users   │
│ Key      │     │ (signed) │     │ (re-sign)│     │          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                                  │
     └── Можно сбросить          App Signing Key
                                 (хранит Google)
```

---

## CI/CD: Автоматизация подписи

### Fastlane Match (iOS) — золотой стандарт

```ruby
# Matchfile
git_url("git@github.com:company/certificates.git")
storage_mode("git")  # или "google_cloud", "s3"

type("appstore")  # development, adhoc, appstore, enterprise

app_identifier(["com.example.app", "com.example.app.widget"])
username("developer@company.com")

team_id("TEAM_ID")

# Шифрование репозитория
encrypt_storage(true)
```

```ruby
# Fastfile
lane :setup_signing do
  # Скачивает/создаёт сертификаты и профили
  match(
    type: "appstore",
    readonly: is_ci,  # На CI только читаем
    force_for_new_devices: true
  )
end

lane :release do
  setup_signing

  build_app(
    scheme: "MyApp",
    export_method: "app-store"
  )

  upload_to_app_store
end
```

### GitHub Actions: iOS

```yaml
# .github/workflows/ios-release.yml
name: iOS Release

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: macos-14

    steps:
      - uses: actions/checkout@v4

      - name: Install certificates
        env:
          P12_BASE64: ${{ secrets.CERTIFICATES_P12_BASE64 }}
          P12_PASSWORD: ${{ secrets.CERTIFICATES_P12_PASSWORD }}
          KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
        run: |
          # Создаём временный keychain
          KEYCHAIN_PATH=$RUNNER_TEMP/app-signing.keychain-db
          security create-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          security set-keychain-settings -lut 21600 $KEYCHAIN_PATH
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH

          # Импортируем сертификат
          echo -n "$P12_BASE64" | base64 --decode -o $RUNNER_TEMP/certificate.p12
          security import $RUNNER_TEMP/certificate.p12 \
            -P "$P12_PASSWORD" \
            -A -t cert -f pkcs12 \
            -k $KEYCHAIN_PATH

          security list-keychain -d user -s $KEYCHAIN_PATH

      - name: Install provisioning profile
        env:
          PROVISIONING_PROFILE_BASE64: ${{ secrets.PROVISIONING_PROFILE_BASE64 }}
        run: |
          PP_PATH=$RUNNER_TEMP/profile.mobileprovision
          echo -n "$PROVISIONING_PROFILE_BASE64" | base64 --decode -o $PP_PATH

          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
          cp $PP_PATH ~/Library/MobileDevice/Provisioning\ Profiles/

      - name: Build and sign
        run: |
          xcodebuild archive \
            -scheme MyApp \
            -archivePath $RUNNER_TEMP/MyApp.xcarchive \
            -configuration Release \
            CODE_SIGN_IDENTITY="iPhone Distribution"
```

### GitHub Actions: Android

```yaml
# .github/workflows/android-release.yml
name: Android Release

on:
  push:
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Decode Keystore
        env:
          KEYSTORE_BASE64: ${{ secrets.KEYSTORE_BASE64 }}
        run: |
          echo $KEYSTORE_BASE64 | base64 -d > app/keystore/release.keystore

      - name: Build Release AAB
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}
        run: |
          ./gradlew bundleRelease

      - name: Upload to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.GOOGLE_PLAY_SERVICE_ACCOUNT }}
          packageName: com.example.app
          releaseFiles: app/build/outputs/bundle/release/app-release.aab
          track: internal
```

---

## Сценарии восстановления

### iOS: Потеря сертификата

```
Ситуация: Сертификат Distribution истёк или потерян

Решение:
1. Revoke старый сертификат в Apple Portal
2. Создать новый Certificate Signing Request
3. Загрузить новый сертификат
4. Пересоздать ВСЕ Provisioning Profiles
5. Обновить CI/CD

⚠️ Существующие приложения продолжат работать!
   Новый сертификат нужен только для новых сборок.
```

### iOS: Потеря Provisioning Profile

```bash
# Через Fastlane — проще всего
fastlane match nuke distribution  # Удалить старые
fastlane match appstore           # Создать новые

# Вручную через Apple Portal:
# 1. Certificates, Identifiers & Profiles
# 2. Profiles → создать новый
# 3. Скачать и установить
```

### Android: Потеря Keystore

```
БЕЗ Play App Signing:
┌─────────────────────────────────────────────┐
│  ПРИЛОЖЕНИЕ ПОТЕРЯНО НАВСЕГДА               │
│                                             │
│  Придётся публиковать под новым package name│
│  Все пользователи потеряют данные          │
│  Рейтинги и отзывы — с нуля                │
└─────────────────────────────────────────────┘

С Play App Signing:
┌─────────────────────────────────────────────┐
│  Upload Key можно сбросить!                 │
│                                             │
│  1. Play Console → Setup → App signing     │
│  2. Request upload key reset               │
│  3. Подтвердить личность                   │
│  4. Сгенерировать новый upload key         │
│  5. Продолжить публикации                  │
└─────────────────────────────────────────────┘
```

### Миграция на Play App Signing

```bash
# 1. Экспортируем текущий ключ
keytool -export -rfc \
    -keystore original.keystore \
    -alias original-alias \
    -file upload_certificate.pem

# 2. В Play Console:
#    Setup → App signing → Use different key
#    Загружаем .pepk файл (генерируется через PEPK tool)

# 3. Генерируем новый upload key
keytool -genkeypair \
    -alias upload \
    -keyalg RSA \
    -keystore upload.keystore \
    -validity 9125

# 4. Обновляем CI/CD на новый keystore
```

---

## 6 типичных ошибок

### Ошибка 1: Несовпадение Bundle ID / App ID

```
iOS:
"No matching provisioning profile found"

Причина: Bundle ID в Xcode ≠ App ID в Profile

Проверка:
1. Xcode → Target → Signing & Capabilities
2. Bundle Identifier должен ТОЧНО совпадать
3. Включая wildcard: com.company.* vs com.company.app
```

### Ошибка 2: Истёкший сертификат

```
"Your account already has a valid iOS Distribution certificate"

Причина:
- Сертификат истёк
- Или достигнут лимит (max 3 Distribution certificates)

Решение:
1. Revoke неиспользуемые сертификаты
2. Или дождаться истечения (автоудаление через 30 дней)
```

### Ошибка 3: Keychain locked на CI

```bash
# Ошибка:
"User interaction is not allowed"

# Причина: Keychain заблокирован

# Решение:
security unlock-keychain -p "$PASSWORD" $KEYCHAIN_PATH
security set-keychain-settings -t 3600 -u $KEYCHAIN_PATH
```

### Ошибка 4: Неверный пароль Keystore

```
Execution failed: jarsigner error
"keystore was tampered with, or password was incorrect"

Проверка:
keytool -list -keystore release.keystore
# Должен запросить пароль и показать содержимое

Частая причина:
- storePassword ≠ keyPassword (это разные пароли!)
```

### Ошибка 5: Entitlements mismatch

```
"Provisioning profile doesn't include the entitlement"

Причина:
Capability включена в Xcode, но не в App ID

Решение:
1. Apple Portal → Identifiers → выбрать App ID
2. Включить нужную Capability
3. Пересоздать Provisioning Profile
4. Скачать и установить
```

### Ошибка 6: Подпись debug-ключом в релиз

```kotlin
// Ошибка: release APK подписан debug keystore
// Google Play отклонит такую сборку

// Проверка подписи:
// apksigner verify --print-certs app-release.apk

// Должно быть:
// DN: CN=Your Name, OU=...
// НЕ: CN=Android Debug, O=Android, C=US
```

---

## 3 ментальные модели

### Модель 1: iOS = Паспортный контроль

```
┌─────────────────────────────────────────────────────────────┐
│                    ПАСПОРТНЫЙ КОНТРОЛЬ                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Сертификат = Паспорт разработчика                          │
│  ├── Подтверждает вашу личность                             │
│  ├── Выдаётся центром (Apple)                               │
│  └── Имеет срок действия                                    │
│                                                               │
│  App ID = Номер рейса                                        │
│  ├── Уникальный идентификатор приложения                    │
│  └── Определяет маршрут (capabilities)                      │
│                                                               │
│  Provisioning Profile = Посадочный талон                    │
│  ├── Связывает паспорт + рейс + места (устройства)         │
│  ├── Без него не пустят на борт (устройство)               │
│  └── Действует ограниченное время                           │
│                                                               │
│  Entitlements = Багаж (что можно взять на борт)            │
│  └── Push, Apple Pay, iCloud, etc.                          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Модель 2: Android = Личная печать

```
┌─────────────────────────────────────────────────────────────┐
│                      ЛИЧНАЯ ПЕЧАТЬ                           │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Keystore = Ваша личная печать                              │
│  ├── Создаёте сами, храните сами                            │
│  ├── Никто не проверяет подлинность                         │
│  ├── Потеряли = документ недействителен                     │
│  └── Подделать нельзя (криптография)                        │
│                                                               │
│  APK/AAB = Документ с печатью                               │
│  ├── Любой может проверить печать                           │
│  └── Изменить документ без печати нельзя                    │
│                                                               │
│  Play App Signing = Нотариус                                │
│  ├── Хранит копию вашей печати                              │
│  ├── Гарантирует, что печать не потеряется                  │
│  └── Может выдать новую доверенность (upload key)          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Модель 3: Цепочка доверия

```
iOS — Централизованное доверие:
Apple ──доверяет──▶ Developer ──подписывает──▶ App
  │                     │
  └── выдаёт ───────────┘
      сертификат

Пользователь доверяет Apple → Apple проверил разработчика →
→ разработчик подписал приложение → приложению можно доверять


Android — Самостоятельное доверие:
Developer ──создаёт──▶ Keystore ──подписывает──▶ App
                           │
                     уникальная подпись

Пользователь доверяет конкретному ключу →
→ все обновления должны быть подписаны тем же ключом →
→ гарантия, что автор тот же (но не проверка личности)
```

---

## Quiz: Проверь понимание

### Вопрос 1

```
У вас есть приложение в App Store. Истёк Distribution Certificate.
Что произойдёт?

A) Приложение удалится из App Store
B) Пользователи не смогут скачать приложение
C) Ничего, но вы не сможете выпустить обновление
D) Приложение перестанет работать на устройствах пользователей
```

<details>
<summary>Ответ</summary>

**C) Ничего, но вы не сможете выпустить обновление**

Сертификат нужен только для подписи НОВЫХ сборок. Уже опубликованные
приложения продолжат работать. Пользователи смогут скачивать и
устанавливать приложение. Но для публикации обновления потребуется
новый сертификат и новые Provisioning Profiles.

</details>

### Вопрос 2

```
Вы потеряли Android Keystore. Play App Signing НЕ был включён.
Какие варианты есть?

A) Обратиться в Google Support для восстановления ключа
B) Создать новый Keystore и продолжить обновления
C) Опубликовать приложение под новым package name
D) Использовать backup из Google Play Console
```

<details>
<summary>Ответ</summary>

**C) Опубликовать приложение под новым package name**

Без Play App Signing восстановление невозможно. Google не хранит
ваш ключ, поэтому обращение в поддержку не поможет. Новый keystore
создаст другую подпись, и Google Play отклонит обновление.
Единственный выход — новое приложение с новым package name,
что означает потерю всех пользователей, рейтингов и отзывов.

</details>

### Вопрос 3

```
В CI/CD для iOS вы получаете ошибку:
"No signing certificate 'iOS Distribution' found"

Keychain создан, сертификат импортирован. В чём может быть проблема?

A) Нужно добавить --allowable-acl в security import
B) Keychain не добавлен в search list
C) Сертификат импортирован без private key
D) Всё вышеперечисленное возможно
```

<details>
<summary>Ответ</summary>

**D) Всё вышеперечисленное возможно**

Частые причины этой ошибки:
- Keychain не в search list: `security list-keychain -d user -s $KEYCHAIN`
- Нет private key: нужно импортировать .p12, а не .cer
- Нет ACL: при импорте нужен флаг `-A` или `-T /usr/bin/codesign`
- Keychain заблокирован: нужен `security unlock-keychain`

Отладка:
```bash
security find-identity -v -p codesigning
# Должен показать ваш сертификат
```

</details>

---

## Связь с другими темами

[[ios-code-signing]] — iOS code signing — одна из самых сложных тем в мобильной разработке. Цепочка Apple Root CA → Developer Certificate → Provisioning Profile → Entitlements требует точного понимания каждого звена. Заметка детально разбирает типы сертификатов (Development, Distribution), Provisioning Profiles (Development, Ad Hoc, App Store, Enterprise), Entitlements и Keychain Access. Без этих знаний невозможно настроить автоматическую подпись в CI/CD или разобраться с ошибками codesign.

[[android-apk-aab]] — Android signing проще концептуально (один keystore), но имеет свои нюансы: Play App Signing, Upload Key vs App Signing Key, APK vs AAB форматы, v1/v2/v3/v4 signature schemes. Заметка объясняет, как работает zipalign, APK Signature Scheme v2+ и почему Google рекомендует AAB с динамической доставкой. Понимание Android-подписи критично для сравнения с iOS-моделью и для настройки release pipeline.

[[security-cryptography-fundamentals]] — Code signing на обеих платформах построен на криптографических примитивах: асимметричное шифрование (RSA/ECDSA), цифровые подписи, цепочки сертификатов (PKI), хэш-функции (SHA-256). Заметка даёт теоретическую базу для понимания, почему подпись работает именно так, что такое chain of trust и как верификация подписи защищает от подмены кода.

---

## Источники и дальнейшее чтение

- Neuburg M. (2023). *iOS Programming Fundamentals with Swift.* — Разбирает iOS code signing: сертификаты, provisioning profiles, entitlements и Keychain. Объясняет процесс настройки автоматической подписи в Xcode и типичные ошибки при ручной конфигурации.
- Meier R. (2022). *Professional Android.* — Описывает Android keystore, APK signing schemes, Play App Signing и подготовку приложения к публикации. Включает best practices по безопасному хранению ключей и автоматизации подписи в CI/CD.

---

## Чеклист перед релизом

### iOS
- [ ] Сертификат Distribution действителен
- [ ] Provisioning Profile типа App Store
- [ ] Bundle ID совпадает с App ID
- [ ] Все Capabilities включены в App ID
- [ ] Entitlements файл актуален
- [ ] Бэкап .p12 в безопасном месте

### Android
- [ ] Release keystore (не debug!)
- [ ] Play App Signing включён
- [ ] Upload key забэкаплен
- [ ] Пароли в секретах CI/CD
- [ ] ProGuard/R8 настроен
- [ ] AAB вместо APK (рекомендуется)

---

## Проверь себя

> [!question]- Почему iOS code signing значительно сложнее Android? Какие компоненты участвуют в iOS signing chain?
> iOS signing chain: Apple Root CA -> Developer Certificate (в Keychain) -> Provisioning Profile (связывает certificate + App ID + device UDIDs + entitlements) -> Entitlements (capabilities: push, keychain groups, App Groups). Каждый компонент может быть причиной ошибки. Android: один keystore файл с парой ключей, подписывает APK/AAB напрямую. Сложность iOS: Apple контролирует всю chain of trust, требует регистрации устройств (кроме App Store), и provisioning profiles истекают через год.

> [!question]- Сценарий: после обновления macOS Xcode перестал подписывать приложение с ошибкой "No valid signing identity". Как диагностировать?
> Причины: 1) Обновление macOS могло удалить или повредить certificates в Keychain. 2) Provisioning Profile истёк или не соответствует certificate. 3) Apple отозвал Developer Certificate. Диагностика: Keychain Access -> проверить наличие Apple Development/Distribution certificate и private key. Xcode -> Preferences -> Accounts -> Download Manual Profiles. Если certificate отсутствует: создать новый через Apple Developer Portal -> Certificates, затем обновить Provisioning Profile. security find-identity -p codesigning -- CLI команда для проверки.

> [!question]- Что такое Play App Signing и почему Google рекомендует его использовать?
> Play App Signing: Google хранит app signing key, разработчик подписывает upload key (отдельный). При загрузке в Play Console Google переподписывает AAB app signing key. Преимущества: 1) если upload key утерян/скомпрометирован -- можно сбросить (раньше потеря ключа = конец приложения), 2) Google может оптимизировать APK для устройства (Dynamic Delivery), 3) дополнительная защита от компрометации. Trade-off: Google имеет доступ к signing key.

---

## Ключевые карточки

Чем iOS code signing отличается от Android?
?
iOS: Certificate (Keychain) + Provisioning Profile (App ID + devices + entitlements) + Apple chain of trust. Несколько типов profiles (Development, Ad Hoc, App Store, Enterprise). Android: один keystore файл (JKS/PKCS12) с парой ключей, прямая подпись APK/AAB. Play App Signing добавляет upload key отдельно от signing key. iOS сложнее, Android проще.

Что такое Provisioning Profile на iOS?
?
Provisioning Profile -- XML-plist файл, подписанный Apple, который связывает: 1) Developer Certificate, 2) App ID (Bundle ID), 3) Device UDIDs (для Development/Ad Hoc), 4) Entitlements (capabilities). Типы: Development (dev devices), Ad Hoc (до 100 devices), App Store (без device limit, для store), Enterprise (internal distribution). Истекает через год.

Какие signature schemes существуют на Android?
?
v1 (JAR signing) -- подпись каждого файла в META-INF. v2 (APK Signature Scheme) -- подпись целого APK как блока, быстрее и безопаснее. v3 -- поддержка key rotation. v4 -- incremental installation signature. Android 11+ требует v2+. Каждая новая схема совместима с предыдущими. Android Studio по умолчанию подписывает v1+v2.

Как автоматизировать code signing в CI/CD?
?
iOS: Fastlane match (shared certificates/profiles в Git/S3), или ручное: экспорт .p12 + .mobileprovision в CI secrets, установка в Keychain через security CLI. Android: keystore файл + passwords в CI secrets (GitHub Secrets, Bitrise Secrets), signingConfigs в build.gradle.kts. Обе платформы: никогда не commit signing credentials в репозиторий.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-distribution]] | Distribution -- следующий шаг после подписания |
| Углубиться | [[ios-code-signing]] | Детальное погружение в iOS signing из раздела iOS |
| Смежная тема | [[security-fundamentals]] | Криптография, PKI, chain of trust |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |
