---
title: "iOS Code Signing: сертификаты, профили, entitlements"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - type/deep-dive
  - topic/ios
  - topic/security
  - level/intermediate
---

# iOS Code Signing: сертификаты, профили, entitlements

## TL;DR

Code signing — механизм Apple для подтверждения личности разработчика и целостности приложения. Каждое iOS-приложение должно быть подписано сертификатом разработчика и содержать provisioning profile, который определяет, на каких устройствах и с какими возможностями приложение может работать. Без правильной подписи приложение не запустится ни на реальном устройстве, ни в App Store.

## Зачем это нужно?

iOS использует **закрытую экосистему** с многоуровневой защитой:

1. **Идентификация разработчика** — Apple знает, кто создал приложение
2. **Целостность кода** — гарантия, что код не был изменён после подписи
3. **Контроль распространения** — приложение работает только там, где разрешено
4. **Отзыв доверия** — Apple может заблокировать скомпрометированные сертификаты

```
Почему iOS требует code signing?
════════════════════════════════

┌─────────────────────────────────────────────────────────────┐
│                    Угрозы без подписи                       │
├─────────────────────────────────────────────────────────────┤
│ • Malware под видом легитимных приложений                   │
│ • Модификация приложений (внедрение вредоносного кода)      │
│ • Неконтролируемое распространение                          │
│ • Невозможность отследить источник угрозы                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   Code Signing решает                        │
├─────────────────────────────────────────────────────────────┤
│ • Developer Certificate → Кто создал                         │
│ • Code Signature → Код не изменён                           │
│ • Provisioning Profile → Где может работать                  │
│ • Entitlements → Что может делать                           │
└─────────────────────────────────────────────────────────────┘
```

## Аналогии из жизни

### 1. Certificate = Паспорт разработчика

```
┌─────────────────────────────────────────┐
│        DEVELOPER CERTIFICATE            │
│         (Паспорт разработчика)          │
├─────────────────────────────────────────┤
│                                         │
│  Имя: Ivan Petrov                       │
│  Team ID: A1B2C3D4E5                    │
│  Выдан: Apple Inc.                      │
│  Действителен до: 2027-01-11            │
│                                         │
│  ┌─────────────────┐                    │
│  │   [Фото/Ключ]   │  ← Public Key      │
│  └─────────────────┘                    │
│                                         │
│  Подпись: Apple Certificate Authority   │
│                                         │
└─────────────────────────────────────────┘

Аналогия: Паспорт удостоверяет вашу личность.
Apple выступает как "государство", которое выдаёт
и подтверждает подлинность вашего документа.
```

### 2. Private Key = Личная подпись

```
┌─────────────────────────────────────────┐
│           PRIVATE KEY                   │
│         (Личная подпись)                │
├─────────────────────────────────────────┤
│                                         │
│     🔐 Хранится ТОЛЬКО у вас            │
│                                         │
│  ┌─────────────────────────────────┐    │
│  │  MIIEpA...очень секретный...    │    │
│  │  ключ который нельзя терять     │    │
│  │  и нельзя показывать другим     │    │
│  └─────────────────────────────────┘    │
│                                         │
│  Потеряли = новый сертификат            │
│  Скомпрометировали = отзыв + новый      │
│                                         │
└─────────────────────────────────────────┘

Аналогия: Как личная подпись на документах —
только вы можете её поставить, и она
подтверждает, что документ подписали именно вы.
```

### 3. Provisioning Profile = Виза

```
┌─────────────────────────────────────────┐
│       PROVISIONING PROFILE              │
│             (Виза)                       │
├─────────────────────────────────────────┤
│                                         │
│  Тип: Development / Distribution        │
│                                         │
│  Разрешено:                             │
│  ├─ App ID: com.mycompany.myapp         │
│  ├─ Devices: iPhone-ABC, iPad-XYZ       │
│  ├─ Certificate: Ivan Petrov            │
│  └─ Entitlements: Push, iCloud          │
│                                         │
│  Действует до: 2027-01-11               │
│                                         │
└─────────────────────────────────────────┘

Аналогия: Виза определяет:
• В какую "страну" (устройства) можно въехать
• Какой "паспорт" (сертификат) привязан
• Что можно делать (entitlements)
• Срок действия
```

### 4. App ID = Имя в паспортной системе

```
┌─────────────────────────────────────────┐
│              APP ID                     │
│     (Имя в паспортной системе)          │
├─────────────────────────────────────────┤
│                                         │
│  Team ID + Bundle ID = App ID           │
│                                         │
│  Пример:                                │
│  A1B2C3D4E5.com.mycompany.myapp         │
│  ──────────┬───────────────────         │
│      Team ID │    Bundle ID             │
│              │                          │
│  Explicit: com.mycompany.myapp          │
│  Wildcard: com.mycompany.*              │
│                                         │
└─────────────────────────────────────────┘

Аналогия: Как уникальный идентификатор
гражданина в государственной системе.
Один App ID = одно приложение в экосистеме Apple.
```

### 5. Entitlements = Права в паспорте

```
┌─────────────────────────────────────────┐
│           ENTITLEMENTS                  │
│      (Права в паспорте)                 │
├─────────────────────────────────────────┤
│                                         │
│  ✓ Push Notifications                   │
│  ✓ App Groups                           │
│  ✓ iCloud                               │
│  ✓ Keychain Sharing                     │
│  ✗ Apple Pay (не запрошено)             │
│  ✗ HealthKit (не запрошено)             │
│                                         │
└─────────────────────────────────────────┘

Аналогия: Как отметки в паспорте о праве
на работу, вождение, голосование.
Каждое право нужно явно запросить и получить.
```

## Компоненты Code Signing

```
┌────────────────────────────────────────────────────────────────────┐
│                    iOS CODE SIGNING ECOSYSTEM                      │
└────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────────┐
                    │   Apple Developer   │
                    │      Portal         │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ Certificates│    │   App IDs   │    │  Profiles   │
    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
           │                  │                   │
           │                  │                   │
    ┌──────┴──────┐    ┌──────┴──────┐    ┌──────┴──────┐
    │ Development │    │  Explicit   │    │ Development │
    │ Distribution│    │  Wildcard   │    │  Ad Hoc     │
    └─────────────┘    └─────────────┘    │ App Store   │
                                          │ Enterprise  │
                                          └─────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                        На вашем Mac                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Keychain Access                     Xcode                          │
│  ┌───────────────────┐              ┌────────────────────────┐      │
│  │ • Private Keys    │◄────────────►│ Signing & Capabilities │      │
│  │ • Certificates    │              │ • Team                 │      │
│  │ • Identities      │              │ • Signing Certificate  │      │
│  └───────────────────┘              │ • Provisioning Profile │      │
│                                     │ • Entitlements         │      │
│                                     └────────────────────────┘      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                     Результат: Подписанное приложение               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  MyApp.app/                                                         │
│  ├── _CodeSignature/                                                │
│  │   └── CodeResources          ← Хеши всех файлов                  │
│  ├── embedded.mobileprovision   ← Provisioning Profile              │
│  ├── Info.plist                 ← Bundle ID и метаданные            │
│  ├── MyApp                      ← Подписанный бинарник              │
│  └── MyApp.entitlements         ← Права приложения                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Сертификаты в деталях

### Типы сертификатов

```
┌─────────────────────────────────────────────────────────────────────┐
│                      ТИПЫ СЕРТИФИКАТОВ                              │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐  ┌─────────────────────────────────┐
│     Apple Development           │  │     Apple Distribution          │
├─────────────────────────────────┤  ├─────────────────────────────────┤
│                                 │  │                                 │
│ Для: Разработка и тестирование  │  │ Для: App Store / Ad Hoc /       │
│      на реальных устройствах    │  │      Enterprise распространение │
│                                 │  │                                 │
│ Устройства: Зарегистрированные  │  │ Устройства: Любые (App Store)   │
│             в Developer Portal   │  │             или список (Ad Hoc) │
│                                 │  │                                 │
│ Лимит: До 100 устройств/тип     │  │ Лимит: Без ограничений          │
│                                 │  │                                 │
│ Количество: Много на команду    │  │ Количество: До 3 на команду     │
│                                 │  │                                 │
└─────────────────────────────────┘  └─────────────────────────────────┘

Устаревшие названия (до Xcode 11):
• iOS Development → Apple Development
• iOS Distribution → Apple Distribution
```

### CSR (Certificate Signing Request)

```
Процесс получения сертификата:
══════════════════════════════

┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│   Ваш Mac    │        │   Apple      │        │   Результат  │
│   Keychain   │        │   Portal     │        │              │
└──────┬───────┘        └──────┬───────┘        └──────┬───────┘
       │                       │                       │
       │  1. Генерация         │                       │
       │     Private Key       │                       │
       │  ────────────►        │                       │
       │  (остаётся у вас)     │                       │
       │                       │                       │
       │  2. CSR содержит      │                       │
       │     Public Key        │                       │
       │  ─────────────────────►                       │
       │                       │                       │
       │                       │  3. Apple подписывает │
       │                       │     и создаёт         │
       │                       │     сертификат        │
       │                       │  ─────────────────────►
       │                       │                       │
       │  4. Скачиваем .cer    │                       │
       │◄──────────────────────                        │
       │                       │                       │
       │  5. Private Key +     │                       │
       │     Certificate =     │                       │
       │     Signing Identity  │                       │
       │                       │                       │

⚠️ ВАЖНО: Private Key создаётся ОДИН раз на вашем Mac.
   Если потеряете — нужен новый сертификат!
```

### Keychain Storage

```swift
// Где хранятся ключи и сертификаты
// Keychain Access → login keychain

/*
┌─────────────────────────────────────────────────────────────┐
│                    Keychain Access                          │
├─────────────────────────────────────────────────────────────┤
│ Category         │ Name                                     │
├──────────────────┼──────────────────────────────────────────┤
│ My Certificates  │ Apple Development: Ivan Petrov (ABC123)  │
│                  │ Apple Distribution: MyCompany (XYZ789)   │
├──────────────────┼──────────────────────────────────────────┤
│ Keys             │ Ivan Petrov                              │
│                  │   ├── Private Key  🔐                    │
│                  │   └── Public Key                         │
├──────────────────┼──────────────────────────────────────────┤
│ Certificates     │ Apple Development: Ivan Petrov           │
│                  │ Apple Worldwide Developer Relations      │
│                  │ Apple Root CA                            │
└─────────────────────────────────────────────────────────────┘
*/

// Экспорт для CI/CD или другого Mac
// 1. Выбрать сертификат в Keychain Access
// 2. File → Export Items...
// 3. Формат: .p12 (включает private key)
// 4. Задать пароль
```

### Team vs Personal сертификаты

```
┌─────────────────────────────────────────────────────────────────────┐
│              PERSONAL vs TEAM CERTIFICATES                          │
└─────────────────────────────────────────────────────────────────────┘

Personal (Individual Account)          Team (Company Account)
─────────────────────────────          ────────────────────────

┌───────────────────────────┐          ┌───────────────────────────┐
│    Один разработчик       │          │    Компания/Команда       │
├───────────────────────────┤          ├───────────────────────────┤
│ • $99/год                 │          │ • $99/год (или $299       │
│ • Один человек            │          │   Enterprise)             │
│ • Сертификат привязан     │          │ • Team ID общий           │
│   к Apple ID              │          │ • Много разработчиков     │
│ • Нельзя добавить         │          │ • Роли: Admin, Developer  │
│   других людей            │          │ • Shared certificates     │
└───────────────────────────┘          └───────────────────────────┘

В команде:
┌─────────────────────────────────────────────────────────────────────┐
│ Admin                                                               │
│ ├── Создаёт Distribution сертификаты                                │
│ ├── Управляет Provisioning Profiles                                 │
│ └── Добавляет устройства                                            │
│                                                                     │
│ Developer                                                           │
│ ├── Создаёт Development сертификаты (свой)                          │
│ ├── Использует общие Distribution сертификаты                       │
│ └── Не может управлять профилями                                    │
└─────────────────────────────────────────────────────────────────────┘
```

## Provisioning Profiles

### Что внутри профиля

```
┌─────────────────────────────────────────────────────────────────────┐
│              ANATOMY OF PROVISIONING PROFILE                        │
└─────────────────────────────────────────────────────────────────────┘

MyApp_Development.mobileprovision (XML/plist внутри)
│
├── AppIDName: "MyApp"
│
├── ApplicationIdentifierPrefix: ["A1B2C3D4E5"]
│
├── CreationDate: 2026-01-11
├── ExpirationDate: 2027-01-11
│
├── DeveloperCertificates: [
│   │   <data>...Certificate 1 (base64)...</data>
│   │   <data>...Certificate 2 (base64)...</data>
│   └── ]
│
├── Entitlements: {
│   │   "application-identifier": "A1B2C3D4E5.com.mycompany.myapp"
│   │   "aps-environment": "development"
│   │   "com.apple.developer.team-identifier": "A1B2C3D4E5"
│   │   "keychain-access-groups": ["A1B2C3D4E5.*"]
│   └── }
│
├── Name: "MyApp Development"
│
├── ProvisionedDevices: [
│   │   "00001234-000A1B2C3D4E5F6G"  ← Device UDID 1
│   │   "00005678-000X9Y8Z7W6V5U4T"  ← Device UDID 2
│   └── ]
│
├── TeamIdentifier: ["A1B2C3D4E5"]
├── TeamName: "My Company LLC"
│
├── TimeToLive: 365
│
├── UUID: "12345678-1234-1234-1234-123456789ABC"
│
└── Version: 1

Просмотр содержимого:
$ security cms -D -i MyApp.mobileprovision
```

### Типы Provisioning Profiles

```
┌─────────────────────────────────────────────────────────────────────┐
│                  PROVISIONING PROFILE TYPES                         │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────┐
│   Development    │
├──────────────────┤
│ Цель: Разработка │      Используемые сертификаты: Apple Development
│ и отладка        │      Устройства: Список зарегистрированных (до 100)
│                  │      Срок: 1 год
│ Xcode debugger ✓ │      Entitlements: development environment
└──────────────────┘

┌──────────────────┐
│     Ad Hoc       │
├──────────────────┤
│ Цель: Тестиро-   │      Используемые сертификаты: Apple Distribution
│ вание вне        │      Устройства: Список зарегистрированных (до 100)
│ App Store        │      Срок: 1 год
│                  │      Entitlements: production environment
│ TestFlight alt ✓ │
└──────────────────┘

┌──────────────────┐
│    App Store     │
├──────────────────┤
│ Цель: Публика-   │      Используемые сертификаты: Apple Distribution
│ ция в App Store  │      Устройства: Любые (после проверки Apple)
│                  │      Срок: 1 год
│ Production ✓     │      Entitlements: production environment
└──────────────────┘

┌──────────────────┐
│    Enterprise    │
├──────────────────┤
│ Цель: Внутренние │      Используемые сертификаты: In-House Distribution
│ приложения       │      Устройства: Любые в организации
│ компании         │      Срок: 3 года
│                  │      Требуется: Enterprise Program ($299/год)
│ $299/year only   │
└──────────────────┘

Сравнение:
┌────────────────┬─────────────┬──────────┬───────────┬────────────┐
│                │ Development │ Ad Hoc   │ App Store │ Enterprise │
├────────────────┼─────────────┼──────────┼───────────┼────────────┤
│ Debugger       │     ✓       │    ✗     │     ✗     │     ✗      │
│ Device limit   │    100      │   100    │     ∞     │     ∞      │
│ Device list    │     ✓       │    ✓     │     ✗     │     ✗      │
│ App Review     │     ✗       │    ✗     │     ✓     │     ✗      │
│ Public distrib │     ✗       │    ✗     │     ✓     │     ✗      │
└────────────────┴─────────────┴──────────┴───────────┴────────────┘
```

### Automatic vs Manual Signing

```
┌─────────────────────────────────────────────────────────────────────┐
│              AUTOMATIC vs MANUAL SIGNING                            │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────┐  ┌─────────────────────────────────┐
│     AUTOMATIC SIGNING           │  │      MANUAL SIGNING             │
├─────────────────────────────────┤  ├─────────────────────────────────┤
│                                 │  │                                 │
│ Xcode делает всё сам:           │  │ Вы контролируете всё:           │
│                                 │  │                                 │
│ ✓ Создаёт App ID                │  │ • Создание App ID вручную       │
│ ✓ Создаёт сертификаты           │  │ • Создание сертификатов         │
│ ✓ Создаёт profiles              │  │ • Создание profiles             │
│ ✓ Обновляет при изменениях      │  │ • Скачивание и установка        │
│ ✓ Добавляет устройства          │  │ • Явный выбор в Xcode           │
│                                 │  │                                 │
│ Когда использовать:             │  │ Когда использовать:             │
│ • Личные проекты                │  │ • CI/CD pipelines               │
│ • Небольшие команды             │  │ • Enterprise distribution       │
│ • Быстрый старт                 │  │ • Множественные targets         │
│ • Простые приложения            │  │ • Специфичные entitlements      │
│                                 │  │ • Полный контроль               │
└─────────────────────────────────┘  └─────────────────────────────────┘

В Xcode → Signing & Capabilities:

Automatic:
┌─────────────────────────────────────────────────────────────────────┐
│ ☑ Automatically manage signing                                      │
│                                                                     │
│ Team: My Company LLC (A1B2C3D4E5)                                   │
│                                                                     │
│ Signing Certificate: Apple Development: Ivan Petrov (ABC123)        │
│ Provisioning Profile: Xcode Managed Profile                         │
│ Status: ✓                                                           │
└─────────────────────────────────────────────────────────────────────┘

Manual:
┌─────────────────────────────────────────────────────────────────────┐
│ ☐ Automatically manage signing                                      │
│                                                                     │
│ Team: My Company LLC (A1B2C3D4E5)                                   │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Debug                                                           │ │
│ │ Signing Certificate: Apple Development: Ivan Petrov ▼           │ │
│ │ Provisioning Profile: MyApp Development Profile ▼               │ │
│ └─────────────────────────────────────────────────────────────────┘ │
│                                                                     │
│ ┌─────────────────────────────────────────────────────────────────┐ │
│ │ Release                                                         │ │
│ │ Signing Certificate: Apple Distribution: My Company ▼           │ │
│ │ Provisioning Profile: MyApp App Store Profile ▼                 │ │
│ └─────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Entitlements

### Распространённые Entitlements

```
┌─────────────────────────────────────────────────────────────────────┐
│                    COMMON ENTITLEMENTS                              │
└─────────────────────────────────────────────────────────────────────┘

Push Notifications
──────────────────
Key: aps-environment
Values: development | production
Требуется: Регистрация App ID для Push в Developer Portal

App Groups
──────────
Key: com.apple.security.application-groups
Value: ["group.com.mycompany.shared"]
Требуется: Создать App Group в Developer Portal
Использование: Shared UserDefaults, файлы между app и extensions

Keychain Sharing
────────────────
Key: keychain-access-groups
Value: ["A1B2C3D4E5.com.mycompany.shared"]
Требуется: Один Team ID для всех приложений
Использование: Общий keychain между приложениями

iCloud
──────
Key: com.apple.developer.icloud-container-identifiers
Value: ["iCloud.com.mycompany.myapp"]
Дополнительно: com.apple.developer.icloud-services
Требуется: Настройка CloudKit в Developer Portal

Associated Domains (Universal Links)
────────────────────────────────────
Key: com.apple.developer.associated-domains
Value: ["applinks:example.com", "webcredentials:example.com"]
Требуется: apple-app-site-association файл на сервере

Sign In with Apple
──────────────────
Key: com.apple.developer.applesignin
Value: ["Default"]
Требуется: Настройка в Developer Portal + Keys

HealthKit
─────────
Key: com.apple.developer.healthkit
Value: true
Дополнительно: com.apple.developer.healthkit.access
Требуется: HealthKit capability + Info.plist descriptions

Apple Pay
─────────
Key: com.apple.developer.in-app-payments
Value: ["merchant.com.mycompany.myapp"]
Требуется: Merchant ID в Developer Portal
```

### Файл .entitlements

```xml
<!-- MyApp.entitlements -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <!-- Push Notifications -->
    <key>aps-environment</key>
    <string>development</string>

    <!-- App Groups -->
    <key>com.apple.security.application-groups</key>
    <array>
        <string>group.com.mycompany.shared</string>
    </array>

    <!-- Keychain Sharing -->
    <key>keychain-access-groups</key>
    <array>
        <string>$(AppIdentifierPrefix)com.mycompany.shared</string>
    </array>

    <!-- iCloud -->
    <key>com.apple.developer.icloud-container-identifiers</key>
    <array>
        <string>iCloud.com.mycompany.myapp</string>
    </array>
    <key>com.apple.developer.icloud-services</key>
    <array>
        <string>CloudKit</string>
        <string>CloudDocuments</string>
    </array>

    <!-- Associated Domains -->
    <key>com.apple.developer.associated-domains</key>
    <array>
        <string>applinks:www.mycompany.com</string>
        <string>webcredentials:www.mycompany.com</string>
    </array>

    <!-- Sign In with Apple -->
    <key>com.apple.developer.applesignin</key>
    <array>
        <string>Default</string>
    </array>
</dict>
</plist>
```

### Capabilities в Xcode

```
┌─────────────────────────────────────────────────────────────────────┐
│        Xcode → Target → Signing & Capabilities                      │
└─────────────────────────────────────────────────────────────────────┘

+ Capability                          Текущие capabilities:
────────────────                      ─────────────────────
• Access Wi-Fi Information            ┌─────────────────────────────┐
• App Groups                    ───►  │ Push Notifications          │
• Apple Pay                           │ ┌─────────────────────────┐ │
• Associated Domains                  │ │ ✓ Push Notifications    │ │
• Background Modes                    │ └─────────────────────────┘ │
• Data Protection                     └─────────────────────────────┘
• HealthKit
• HomeKit                             ┌─────────────────────────────┐
• iCloud                        ───►  │ App Groups                  │
• In-App Purchase                     │ ┌─────────────────────────┐ │
• Inter-App Audio                     │ │ group.com.mycompany.app │ │
• Keychain Sharing                    │ └─────────────────────────┘ │
• Maps                                │ [+] Add Group               │
• Network Extensions                  └─────────────────────────────┘
• Personal VPN
• Push Notifications            ───►  ┌─────────────────────────────┐
• Sign In with Apple                  │ iCloud                      │
• Siri                                │ ┌─────────────────────────┐ │
• Wallet                              │ │ Services:               │ │
• ...                                 │ │ ☑ Key-value storage     │ │
                                      │ │ ☑ CloudKit              │ │
                                      │ │ ☐ iCloud Documents      │ │
                                      │ │                         │ │
                                      │ │ Containers:             │ │
                                      │ │ iCloud.com.mycompany... │ │
                                      │ └─────────────────────────┘ │
                                      └─────────────────────────────┘

При добавлении Capability:
1. Xcode обновляет .entitlements файл
2. При Automatic Signing — обновляет App ID и Profile в Developer Portal
3. При Manual Signing — вам нужно обновить App ID и скачать новый Profile
```

## Automatic Signing vs Manual

### Когда использовать Automatic

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AUTOMATIC SIGNING                                │
│                    Рекомендуется для:                               │
└─────────────────────────────────────────────────────────────────────┘

✅ Идеально подходит:
   • Личные/учебные проекты
   • Небольшие команды (2-5 разработчиков)
   • Простые приложения без extensions
   • Быстрое прототипирование
   • Когда один человек делает сборки

⚠️ Ограничения:
   • Xcode управляет профилями (может перезаписать)
   • Сложно контролировать точные настройки
   • Проблемы при работе нескольких Macs
   • Неудобно для CI/CD без дополнительных инструментов

Настройка:
──────────

// project.pbxproj (автоматически)
DEVELOPMENT_TEAM = A1B2C3D4E5;
CODE_SIGN_STYLE = Automatic;
PROVISIONING_PROFILE_SPECIFIER = "";  // Xcode выбирает сам

// или в Xcode UI
Target → Signing & Capabilities → ☑ Automatically manage signing
```

### Когда использовать Manual

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MANUAL SIGNING                                  │
│                     Рекомендуется для:                              │
└─────────────────────────────────────────────────────────────────────┘

✅ Идеально подходит:
   • CI/CD pipelines (Jenkins, GitHub Actions, Fastlane)
   • Enterprise распространение
   • Множественные targets (App + Extensions)
   • Разные конфигурации (Dev, Staging, Prod)
   • Большие команды с разделением ролей
   • Полный контроль над сертификатами

Настройка:
──────────

// project.pbxproj
CODE_SIGN_STYLE = Manual;
DEVELOPMENT_TEAM = A1B2C3D4E5;

// Для Debug
CODE_SIGN_IDENTITY[config=Debug] = "Apple Development";
PROVISIONING_PROFILE_SPECIFIER[config=Debug] = "MyApp Development";

// Для Release
CODE_SIGN_IDENTITY[config=Release] = "Apple Distribution";
PROVISIONING_PROFILE_SPECIFIER[config=Release] = "MyApp App Store";
```

### CI/CD Configuration

```yaml
# .github/workflows/ios.yml (GitHub Actions пример)
name: iOS Build

on: [push]

jobs:
  build:
    runs-on: macos-latest

    steps:
    - uses: actions/checkout@v4

    # Установка сертификата и профиля
    - name: Install Certificates
      env:
        P12_CERTIFICATE: ${{ secrets.P12_CERTIFICATE }}
        P12_PASSWORD: ${{ secrets.P12_PASSWORD }}
        PROVISIONING_PROFILE: ${{ secrets.PROVISIONING_PROFILE }}
        KEYCHAIN_PASSWORD: ${{ secrets.KEYCHAIN_PASSWORD }}
      run: |
        # Создаём временный keychain
        security create-keychain -p "$KEYCHAIN_PASSWORD" build.keychain
        security default-keychain -s build.keychain
        security unlock-keychain -p "$KEYCHAIN_PASSWORD" build.keychain

        # Импортируем сертификат
        echo $P12_CERTIFICATE | base64 --decode > certificate.p12
        security import certificate.p12 -k build.keychain \
          -P "$P12_PASSWORD" -T /usr/bin/codesign

        # Разрешаем доступ к ключам
        security set-key-partition-list -S apple-tool:,apple: \
          -s -k "$KEYCHAIN_PASSWORD" build.keychain

        # Устанавливаем provisioning profile
        mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
        echo $PROVISIONING_PROFILE | base64 --decode > profile.mobileprovision
        cp profile.mobileprovision ~/Library/MobileDevice/Provisioning\ Profiles/

    - name: Build
      run: |
        xcodebuild -project MyApp.xcodeproj \
          -scheme MyApp \
          -configuration Release \
          -archivePath build/MyApp.xcarchive \
          archive \
          CODE_SIGN_STYLE=Manual \
          DEVELOPMENT_TEAM=A1B2C3D4E5 \
          PROVISIONING_PROFILE_SPECIFIER="MyApp App Store"
```

```ruby
# Fastlane (fastlane/Fastfile)
default_platform(:ios)

platform :ios do
  desc "Build for App Store"
  lane :release do
    # Match управляет сертификатами через Git
    match(
      type: "appstore",
      app_identifier: "com.mycompany.myapp",
      readonly: true  # Не создавать новые, только использовать существующие
    )

    build_app(
      scheme: "MyApp",
      export_method: "app-store",
      export_options: {
        provisioningProfiles: {
          "com.mycompany.myapp" => "MyApp App Store"
        }
      }
    )

    upload_to_app_store
  end

  desc "Build for Testing (Ad Hoc)"
  lane :beta do
    match(type: "adhoc")

    build_app(
      scheme: "MyApp",
      export_method: "ad-hoc"
    )

    # Загрузка в Firebase App Distribution / TestFlight
  end
end
```

## Распространённые ошибки

### 1. Profile/Certificate Mismatch

```
❌ НЕПРАВИЛЬНО:
═══════════════

Ошибка: "Provisioning profile doesn't include signing certificate"

Причина: Профиль был создан с одним сертификатом,
         а вы пытаетесь подписать другим

┌─────────────────────┐     ┌─────────────────────┐
│ Profile содержит:   │     │ Вы используете:     │
│ Certificate A       │  ≠  │ Certificate B       │
└─────────────────────┘     └─────────────────────┘


✅ ПРАВИЛЬНО:
═════════════

Решения:
1. Regenerate profile с текущим сертификатом в Developer Portal
2. Использовать сертификат, указанный в профиле
3. При Automatic Signing — просто "Trust" диалог или перелогин Team

// Проверить какой сертификат в профиле:
$ security cms -D -i profile.mobileprovision | grep -A1 "DeveloperCertificates"
```

### 2. Expired Certificates

```
❌ НЕПРАВИЛЬНО:
═══════════════

Ошибка: "Your certificate has expired"
или:   "Certificate is not valid"

┌─────────────────────────────────────┐
│  Certificate                        │
│  Expires: 2025-01-01  ← ИСТЁК!      │
│  Today:   2026-01-11                │
└─────────────────────────────────────┘


✅ ПРАВИЛЬНО:
═════════════

Профилактика:
• Отслеживать срок действия (1 год для сертификатов)
• Настроить напоминания
• Использовать Fastlane match для автоматизации

Решение:
1. Developer Portal → Certificates → Revoke истёкший
2. Создать новый сертификат
3. Обновить все Provisioning Profiles
4. Скачать и установить

// Проверить срок действия:
$ security find-certificate -c "Apple Development" -p | \
  openssl x509 -noout -dates

// notBefore=Jan 11 00:00:00 2025 GMT
// notAfter=Jan 11 00:00:00 2026 GMT
```

### 3. Missing Entitlements

```
❌ НЕПРАВИЛЬНО:
═══════════════

Ошибка: "Application does not have required entitlements"
или при Push: "No valid aps-environment entitlement"

Код запрашивает Push:
┌────────────────────────────────────────┐
│ UNUserNotificationCenter.current()     │
│   .requestAuthorization(...)           │
└────────────────────────────────────────┘

Но в Entitlements/Profile:
┌────────────────────────────────────────┐
│ aps-environment: НЕТ                   │
└────────────────────────────────────────┘


✅ ПРАВИЛЬНО:
═════════════

1. Developer Portal → App IDs → Capabilities → Push Notifications ✓
2. Regenerate Provisioning Profile
3. Xcode → Signing & Capabilities → + Push Notifications
4. Убедиться что .entitlements содержит:
   <key>aps-environment</key>
   <string>development</string>  <!-- или production -->

// Проверить entitlements в приложении:
$ codesign -d --entitlements - MyApp.app
```

### 4. Wrong Team Selected

```
❌ НЕПРАВИЛЬНО:
═══════════════

Ошибка: "No signing certificate matching team ID found"
или:   "The provisioning profile is not from the team"

┌─────────────────────────────────────┐
│  Project Settings                   │
│  Team: Personal Team (ABC123)       │  ← Личный аккаунт
│                                     │
│  Profile Team: My Company (XYZ789)  │  ← Профиль компании
└─────────────────────────────────────┘


✅ ПРАВИЛЬНО:
═════════════

1. Xcode → Preferences → Accounts → добавить правильный Apple ID
2. Target → Signing → Team → выбрать правильную команду
3. При нескольких accounts — убедиться что выбран нужный

// Проверить какой Team ID в профиле:
$ security cms -D -i profile.mobileprovision | grep TeamIdentifier -A2

// Вывод:
// <key>TeamIdentifier</key>
// <array>
//     <string>A1B2C3D4E5</string>
```

### 5. Device Not in Profile

```
❌ НЕПРАВИЛЬНО:
═══════════════

Ошибка: "A valid provisioning profile for this executable was not found"
или:   "Device is not registered"

При запуске на устройстве:
┌─────────────────────────────────────┐
│  Device UDID: 00008101-000...       │
│                                     │
│  Profile Devices:                   │
│  • 00008102-000...                  │  ← Другое устройство
│  • 00008103-000...                  │  ← Другое устройство
└─────────────────────────────────────┘


✅ ПРАВИЛЬНО:
═════════════

1. Developer Portal → Devices → + добавить устройство
2. Скопировать UDID: Window → Devices and Simulators → Identifier
3. Regenerate Development Profile с новым устройством
4. Скачать и установить профиль

// Быстро получить UDID:
$ xcrun xctrace list devices

// Или для подключённого устройства:
$ system_profiler SPUSBDataType | grep "Serial Number:" | head -1

⚠️ Лимит: 100 устройств каждого типа (iPhone, iPad, Apple Watch, Mac, Apple TV)
   в год! Сброс счётчика — при обновлении членства.
```

### 6. Bundle ID Mismatch

```
❌ НЕПРАВИЛЬНО:
═══════════════

Ошибка: "Bundle ID does not match App ID"
или:   "Provisioning profile doesn't match bundle identifier"

┌─────────────────────────────────────┐
│  Info.plist                         │
│  Bundle ID: com.mycompany.MyApp     │  ← Регистр!
│                                     │
│  App ID: com.mycompany.myapp        │  ← Нижний регистр
└─────────────────────────────────────┘

Или:
┌─────────────────────────────────────┐
│  Project: com.mycompany.myapp       │
│  Profile: com.othercompany.myapp    │  ← Другой Bundle ID
└─────────────────────────────────────┘


✅ ПРАВИЛЬНО:
═════════════

Bundle ID должен ТОЧНО совпадать с App ID в профиле:
• Регистр имеет значение (case-sensitive)
• Никаких опечаток
• Используйте $(PRODUCT_BUNDLE_IDENTIFIER) в Info.plist

// В Build Settings:
PRODUCT_BUNDLE_IDENTIFIER = com.mycompany.myapp

// Проверить App ID в профиле:
$ security cms -D -i profile.mobileprovision | grep application-identifier

// Wildcard App ID (com.mycompany.*) матчит любой suffix,
// но не поддерживает некоторые capabilities (Push, App Groups)
```

## Ментальные модели

### 1. Цепочка доверия (Chain of Trust)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CHAIN OF TRUST                                   │
│                    (Цепочка доверия)                                │
└─────────────────────────────────────────────────────────────────────┘

Apple Root CA
    │
    │ подписывает
    ▼
Apple Worldwide Developer Relations CA
    │
    │ подписывает
    ▼
Ваш Developer Certificate
    │
    │ + Private Key →  подписывает
    ▼
Ваше приложение (MyApp.app)
    │
    │ содержит
    ▼
Provisioning Profile (embedded.mobileprovision)
    │
    │ указывает на
    ▼
Entitlements + Devices + App ID

───────────────────────────────────────────────────────────────────────

iOS проверяет при запуске:
1. Сертификат подписан Apple? ✓
2. Сертификат не отозван? ✓
3. Подпись приложения валидна? ✓
4. Profile не истёк? ✓
5. Устройство в Profile? (для Dev/Ad Hoc) ✓
6. Bundle ID совпадает? ✓
7. Entitlements соответствуют? ✓

→ Если всё ОК — приложение запускается
→ Если нет — "App could not be installed"
```

### 2. Модель Паспортного контроля

```
┌─────────────────────────────────────────────────────────────────────┐
│                    PASSPORT CONTROL MODEL                           │
│                    (Модель паспортного контроля)                    │
└─────────────────────────────────────────────────────────────────────┘

Вы (Разработчик) хотите "въехать" (установить приложение) на iPhone

┌─────────────────┐
│  ПОГРАНИЧНИК    │  ← iOS Security
│  (iOS)          │
└────────┬────────┘
         │
         │ Проверяет:
         │
┌────────┴────────┐   ┌─────────────────────────────────────────┐
│ 1. ПАСПОРТ      │ → │ Certificate: Кто вы? Apple знает вас?   │
├─────────────────┤   └─────────────────────────────────────────┘
│ 2. ВИЗА         │ → │ Profile: Разрешён ли въезд сюда?        │
├─────────────────┤   └─────────────────────────────────────────┘
│ 3. ЦЕЛЬ ВИЗИТА  │ → │ Entitlements: Что собираетесь делать?   │
├─────────────────┤   └─────────────────────────────────────────┘
│ 4. ПРИГЛАШЕНИЕ  │ → │ Device List: Вас тут ждут? (Dev/Ad Hoc) │
└─────────────────┘   └─────────────────────────────────────────┘

App Store Distribution = "Туристическая виза" (любое устройство)
Development = "Рабочая виза" (только одобренные места)
Enterprise = "Корпоративный пропуск" (только внутри компании)
```

### 3. Матрёшка компонентов

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MATRYOSHKA MODEL                                 │
│                    (Модель матрёшки)                                │
└─────────────────────────────────────────────────────────────────────┘

Каждый внешний слой содержит и ограничивает внутренний:

┌─────────────────────────────────────────────────────────────────┐
│                      Apple Developer Account                     │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                   Team (A1B2C3D4E5)                       │  │
│  │  ┌─────────────────────────────────────────────────────┐  │  │
│  │  │               App ID (Bundle ID)                    │  │  │
│  │  │  ┌───────────────────────────────────────────────┐  │  │  │
│  │  │  │         Provisioning Profile                  │  │  │  │
│  │  │  │  ┌─────────────────────────────────────────┐  │  │  │  │
│  │  │  │  │           Certificate                   │  │  │  │  │
│  │  │  │  │  ┌───────────────────────────────────┐  │  │  │  │  │
│  │  │  │  │  │          Private Key              │  │  │  │  │  │
│  │  │  │  │  │  ┌─────────────────────────────┐  │  │  │  │  │  │
│  │  │  │  │  │  │       Code Signature        │  │  │  │  │  │  │
│  │  │  │  │  │  │  ┌───────────────────────┐  │  │  │  │  │  │  │
│  │  │  │  │  │  │  │    Entitlements       │  │  │  │  │  │  │  │
│  │  │  │  │  │  │  └───────────────────────┘  │  │  │  │  │  │  │
│  │  │  │  │  │  └─────────────────────────────┘  │  │  │  │  │  │
│  │  │  │  │  └───────────────────────────────────┘  │  │  │  │  │
│  │  │  │  └─────────────────────────────────────────┘  │  │  │  │
│  │  │  └───────────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

Изменение внешнего слоя влияет на все внутренние!
Новый сертификат → Новые профили → Перекомпиляция
```

### 4. Треугольник подписи

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SIGNING TRIANGLE                                 │
│                    (Треугольник подписи)                            │
└─────────────────────────────────────────────────────────────────────┘

Три компонента должны быть согласованы:

                     Certificate
                         /\
                        /  \
                       /    \
                      /      \
                     /   ✓    \      Все три должны
                    /          \     "указывать" друг на друга
                   /____________\
                  /              \
          App ID ─────────────── Profile

┌─────────────────────────────────────────────────────────────────────┐
│ Certificate  ←──────────────→  Profile содержит Certificate        │
│ Certificate  ←──────────────→  Code подписан Certificate           │
│ App ID       ←──────────────→  Profile привязан к App ID           │
│ App ID       ←──────────────→  Bundle ID в коде = App ID           │
│ Profile      ←──────────────→  Embedded в app bundle               │
└─────────────────────────────────────────────────────────────────────┘

Разрыв любой связи = ошибка подписи!
```

### 5. Жизненный цикл артефактов

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ARTIFACT LIFECYCLE                               │
│                    (Жизненный цикл артефактов)                      │
└─────────────────────────────────────────────────────────────────────┘

Timeline →

Certificate (1 год)
├──────────────────────────────────────────────────────────────┤
│  Create          Active                          Expires/Revoke
│    ▼               │                                  ▼
│    │               │                                  │
│    │   Profile 1 (1 год)                              │
│    │   ├────────────────────────────────────┤         │
│    │   │                                    │         │
│    │   │   Profile 2 (1 год)                │         │
│    │   │   ├────────────────────────────────┼────┤    │
│    │   │   │                                │    │    │
│    │   │   │                                │    │    │
└────│───│───│────────────────────────────────│────│────│─────────────

При истечении Certificate:
• Все связанные Profiles становятся невалидными
• Нужно создать новый Certificate
• Нужно пересоздать все Profiles
• Нужно пересобрать и переподписать приложения

Рекомендация:
• Отслеживать сроки
• Обновлять заранее (за месяц)
• Автоматизировать через Fastlane match
```

## Проверь себя

### Вопрос 1
**Что произойдёт, если потерять Private Key от сертификата?**

<details>
<summary>Ответ</summary>

При потере Private Key:
1. **Нельзя подписать** приложение этим сертификатом
2. **Все Provisioning Profiles**, использующие этот сертификат, станут бесполезными
3. **Нужно создать новый сертификат** (CSR создаст новый Private Key)
4. **Пересоздать все Profiles** с новым сертификатом
5. Старый сертификат рекомендуется **отозвать (revoke)** в Developer Portal

**Профилактика:**
- Экспортировать .p12 файл (Certificate + Private Key) в безопасное место
- Использовать Fastlane match с Git-репозиторием для хранения
- Настроить бэкап Keychain

```bash
# Экспорт identity (cert + key) через командную строку:
security export -k ~/Library/Keychains/login.keychain-db \
  -t identities -f pkcs12 -o backup.p12 -P "password"
```
</details>

### Вопрос 2
**В чём разница между Development и Ad Hoc Provisioning Profile?**

<details>
<summary>Ответ</summary>

| Характеристика | Development | Ad Hoc |
|---------------|-------------|--------|
| **Сертификат** | Apple Development | Apple Distribution |
| **Отладка** | ✓ Xcode debugger работает | ✗ Нельзя отлаживать |
| **Устройства** | До 100, явный список | До 100, явный список |
| **Push env** | development | production |
| **Цель** | Разработка и тестирование | Бета-тестирование, QA |
| **Символы** | Debug symbols доступны | Часто stripped |
| **Установка** | Xcode, Apple Configurator | IPA файл, OTA, MDM |

**Когда использовать Ad Hoc:**
- Тестирование production-like сборки
- Когда TestFlight недоступен
- Внутреннее распространение без Enterprise Program
- QA тестирование перед App Store submission
</details>

### Вопрос 3
**Приложение работает на симуляторе, но не на реальном устройстве с ошибкой "Unable to install". Какие шаги для диагностики?**

<details>
<summary>Ответ</summary>

Пошаговая диагностика:

1. **Проверить регистрацию устройства:**
```bash
# Получить UDID устройства
xcrun xctrace list devices
# Убедиться что UDID есть в Developer Portal → Devices
```

2. **Проверить Provisioning Profile:**
```bash
# Посмотреть устройства в профиле
security cms -D -i ~/Library/MobileDevice/Provisioning\ Profiles/*.mobileprovision | grep ProvisionedDevices -A 100
```

3. **Проверить Certificate:**
- Keychain Access → убедиться что есть Private Key
- Developer Portal → Certificate не истёк и не отозван

4. **Проверить Bundle ID:**
```bash
# В проекте
grep PRODUCT_BUNDLE_IDENTIFIER *.xcodeproj/project.pbxproj
# В профиле
security cms -D -i profile.mobileprovision | grep application-identifier
```

5. **Проверить Team:**
- Xcode → Preferences → Accounts → нужный team залогинен
- Target → Signing → правильный Team выбран

6. **Очистить и пересобрать:**
```bash
rm -rf ~/Library/Developer/Xcode/DerivedData
# Xcode → Product → Clean Build Folder (Cmd+Shift+K)
```

7. **При Automatic Signing:**
- Xcode → Preferences → Accounts → Download Manual Profiles
- Попробовать переключить на Manual и обратно
</details>

### Вопрос 4
**Как настроить CI/CD для подписи iOS-приложения без Automatic Signing?**

<details>
<summary>Ответ</summary>

**Основные подходы:**

**1. Ручное управление (базовый):**
```bash
# На CI машине:
# 1. Создать keychain
security create-keychain -p "$PASSWORD" build.keychain
security default-keychain -s build.keychain
security unlock-keychain -p "$PASSWORD" build.keychain

# 2. Импортировать .p12 (из secrets)
security import certificate.p12 -k build.keychain -P "$P12_PASSWORD" -T /usr/bin/codesign

# 3. Установить provisioning profile
cp profile.mobileprovision ~/Library/MobileDevice/Provisioning\ Profiles/

# 4. Собрать
xcodebuild -scheme MyApp -configuration Release \
  CODE_SIGN_STYLE=Manual \
  CODE_SIGN_IDENTITY="Apple Distribution: My Company" \
  PROVISIONING_PROFILE_SPECIFIER="MyApp App Store" \
  archive
```

**2. Fastlane Match (рекомендуется):**
```ruby
# Fastfile
lane :build do
  match(
    type: "appstore",
    readonly: true,  # Не создавать новые
    keychain_name: "build.keychain",
    keychain_password: ENV["KEYCHAIN_PASSWORD"]
  )

  build_app(scheme: "MyApp")
end
```

Match хранит сертификаты и профили в зашифрованном Git-репозитории.

**3. Xcode Cloud:**
- Apple's native CI/CD
- Автоматически управляет signing
- Интегрирован с App Store Connect
</details>

## Связанные темы

### Prerequisites (изучить до)
- [[ios-xcode-fundamentals]] — Основы работы с Xcode, проектами и схемами сборки
- [[ios-compilation-pipeline]] — Как компилируется iOS-приложение (от Swift до IPA)

### Next (изучить после)
- [[ios-app-distribution]] — TestFlight, App Store, Enterprise distribution
- [[ios-ci-cd]] — Настройка continuous integration для iOS

### Related (связанные темы)
- [[ios-permissions-security]] — Система разрешений и безопасность в iOS
- [[ios-keychain]] — Работа с Keychain для безопасного хранения
- [[ios-app-extensions]] — Signing для app extensions (Watch, Widget, etc.)

## Источники

### Официальная документация Apple
- [Code Signing Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/CodeSigningGuide/Introduction/Introduction.html) — Полное руководство по code signing
- [App Distribution Guide](https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases) — Распространение приложений
- [Certificates, Identifiers & Profiles](https://developer.apple.com/account/resources/certificates/list) — Developer Portal

### WWDC Sessions
- [WWDC 2019: What's New in Xcode 11 (Signing)](https://developer.apple.com/videos/play/wwdc2019/401/) — Automatic signing improvements
- [WWDC 2021: Distribute apps in Xcode with cloud signing](https://developer.apple.com/videos/play/wwdc2021/10204/) — Xcode Cloud signing

### Инструменты
- [Fastlane Match](https://docs.fastlane.tools/actions/match/) — Автоматизация управления сертификатами
- [Fastlane Sigh](https://docs.fastlane.tools/actions/sigh/) — Управление provisioning profiles
- [codesign man page](x-man-page://codesign) — Утилита командной строки для подписи

### Troubleshooting
- [Resolve common code signing errors](https://developer.apple.com/documentation/xcode/resolve-code-signing-errors) — Официальный troubleshooting guide
- [Technical Note TN3125: Inside Code Signing: Provisioning Profiles](https://developer.apple.com/documentation/technotes/tn3125-inside-code-signing-provisioning-profiles)
