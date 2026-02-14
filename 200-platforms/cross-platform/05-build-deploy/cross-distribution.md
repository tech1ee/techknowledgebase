---
title: "Cross-Platform: Distribution — App Store vs Play Store"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - distribution
  - app-store
  - play-store
  - type/comparison
  - level/intermediate
reading_time: 45
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-code-signing]]"
  - "[[cross-build-systems]]"
related:
  - "[[ios-app-distribution]]"
  - "[[android-apk-aab]]"
  - "[[cross-code-signing]]"
---

# Cross-Platform Distribution: App Store vs Play Store

## TL;DR — Ключевые различия

| Аспект | App Store (iOS) | Play Store (Android) |
|--------|-----------------|----------------------|
| **Время ревью** | 24-48 часов (до 7 дней) | 1-3 дня (до 7 дней) |
| **Стоимость аккаунта** | $99/год | $25 единоразово |
| **Формат приложения** | .ipa (через App Store Connect) | .aab (Android App Bundle) |
| **Подписание** | Сертификаты + Provisioning Profiles | Keystore + App Signing by Google |
| **Тестирование** | TestFlight | Internal/Closed/Open Testing |
| **Staged rollout** | Phased Release (7 дней) | Staged Rollout (0.1%-100%) |
| **Откат версии** | Невозможен | Возможен (через новый релиз) |
| **Модерация контента** | Строгая | Умеренная |
| **In-App Purchases** | Только через Apple (30%/15%) | Google Play Billing (30%/15%) |
| **Альтернативные сторы** | Ограничено (EU DMA) | Полностью разрешено |
| **Hot updates** | Запрещено (кроме JS) | Разрешено с ограничениями |
| **Максимальный размер** | 4 GB | 150 MB (+ PAD до 2 GB) |

---

## 1. Review Process — Процесс модерации

### App Store Review

```
Submission → Waiting for Review → In Review → Pending Release / Rejected
     ↓              ↓                  ↓              ↓
  Метаданные    1-24 часа         15 мин - 24ч    Исправления
```

**Что проверяют:**
- Соответствие App Store Guidelines (100+ правил)
- Функциональность и стабильность
- Дизайн и UX (соответствие HIG)
- Приватность и безопасность данных
- Контент и метаданные
- In-App Purchases корректность

**Частые причины отказа:**
1. **Guideline 2.1** — Падения и баги
2. **Guideline 2.3** — Неточные метаданные
3. **Guideline 4.2** — Минимальная функциональность
4. **Guideline 5.1.1** — Проблемы с приватностью
5. **Guideline 3.1.1** — IAP нарушения

```swift
// Пример: обязательный App Tracking Transparency
import AppTrackingTransparency

func requestTracking() {
    ATTrackingManager.requestTrackingAuthorization { status in
        switch status {
        case .authorized:
            // Можно использовать IDFA
        case .denied, .restricted, .notDetermined:
            // Нельзя отслеживать
        @unknown default:
            break
        }
    }
}
```

### Play Store Review

```
Submission → Processing → In Review → Published / Rejected
     ↓           ↓            ↓            ↓
  AAB/APK    Автотесты    1-72 часа   Policy violation
```

**Что проверяют:**
- Google Play Policies compliance
- Malware и security scanning
- Content rating accuracy
- Data safety section
- Target API level requirements

**Частые причины отказа:**
1. **Deceptive behavior** — Обманчивая функциональность
2. **Data safety** — Несоответствие заявлениям
3. **Sensitive permissions** — Необоснованные разрешения
4. **Impersonation** — Имитация других приложений
5. **API level** — Устаревший targetSdkVersion

```kotlin
// Пример: обоснование разрешений
class PermissionRationale {
    fun explainCameraPermission(context: Context) {
        AlertDialog.Builder(context)
            .setTitle("Доступ к камере")
            .setMessage(
                "Камера нужна для сканирования QR-кодов. " +
                "Фото не сохраняются и не передаются."
            )
            .setPositiveButton("Разрешить") { _, _ ->
                requestCameraPermission()
            }
            .setNegativeButton("Отмена", null)
            .show()
    }
}
```

### Сравнение процессов

| Этап | App Store | Play Store |
|------|-----------|------------|
| Автоматические проверки | Базовые | Расширенные (ML) |
| Ручная модерация | Всегда | При флагах |
| Апелляция | App Review Board | Policy Support |
| Экспедированный ревью | По запросу (редко) | Нет |
| Pre-submission check | App Store Connect валидация | Pre-launch report |

---

## 2. TestFlight vs Internal Testing

### TestFlight (iOS)

```
Internal Testing          External Testing
      ↓                         ↓
   До 100                   До 10,000
   тестеров                 тестеров
      ↓                         ↓
  Мгновенно              Beta App Review
      ↓                    (24-48 часов)
  90 дней                   90 дней
  доступа                   доступа
```

**Типы тестирования:**

```
┌─────────────────────────────────────────────────────────┐
│                    TESTFLIGHT                            │
├─────────────────────┬───────────────────────────────────┤
│  Internal Testing   │        External Testing           │
├─────────────────────┼───────────────────────────────────┤
│ • App Store Connect │ • Public link (до 10K)            │
│   пользователи      │ • Groups (до 10K на группу)       │
│ • До 100 тестеров   │ • Требует Beta Review             │
│ • Без ревью         │ • Отдельные билды                 │
│ • Все билды         │ • Feedback встроен                │
└─────────────────────┴───────────────────────────────────┘
```

**Настройка группы:**

```swift
// Информация для тестеров (What to Test)
"""
Версия 2.5.0 (Build 142)

Что тестировать:
1. Новый онбординг — пройдите все шаги
2. Оплата подписки — используйте Sandbox
3. Push-уведомления — проверьте доставку

Известные проблемы:
- iPad: кнопка может обрезаться в landscape

Feedback: Используйте скриншот + описание
"""
```

### Google Play Testing Tracks

```
Internal Testing → Closed Testing → Open Testing → Production
       ↓                 ↓               ↓              ↓
   До 100            До 200K         Без лимита    Все пользователи
   быстро            по email        публично      staged rollout
```

**Треки тестирования:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    GOOGLE PLAY TESTING                          │
├───────────────┬─────────────────┬─────────────────┬─────────────┤
│   Internal    │     Closed      │      Open       │  Production │
├───────────────┼─────────────────┼─────────────────┼─────────────┤
│ • 100 тестеров│ • Email списки  │ • Публичный     │ • Staged    │
│ • Мгновенно   │ • Google Groups │ • Opt-in link   │   rollout   │
│ • Без ревью   │ • Ревью ~часы   │ • Ревью ~дни    │ • 0.1%-100% │
│ • QA команда  │ • Beta группы   │ • Early access  │ • Full      │
└───────────────┴─────────────────┴─────────────────┴─────────────┘
```

**Конфигурация в build.gradle:**

```kotlin
android {
    defaultConfig {
        versionCode = 142
        versionName = "2.5.0"
    }

    buildTypes {
        create("internal") {
            applicationIdSuffix = ".internal"
            versionNameSuffix = "-internal"
            isDebuggable = true
        }
        create("beta") {
            applicationIdSuffix = ".beta"
            versionNameSuffix = "-beta"
            isDebuggable = false
        }
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"))
        }
    }
}
```

### Сравнение тестирования

| Аспект | TestFlight | Play Testing |
|--------|------------|--------------|
| Максимум тестеров | 10,100 | Без лимита |
| Время публикации | Мгновенно (internal) | Мгновенно (internal) |
| Feedback система | Встроенная | Play Console + Firebase |
| Crash reports | Да | Pre-launch report |
| Автотесты | Нет | Robo tests |
| A/B тестирование | Нет | Store listing experiments |

---

## 3. Code Signing vs Keystore

### iOS Code Signing

```
┌─────────────────────────────────────────────────────────────┐
│                    iOS SIGNING FLOW                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Developer Account                                           │
│        ↓                                                     │
│  ┌─────────────┐    ┌──────────────────┐                    │
│  │ Certificate │ +  │ Provisioning     │ = Signed .ipa      │
│  │ (.p12)      │    │ Profile (.mobileprovision)            │
│  └─────────────┘    └──────────────────┘                    │
│        ↑                    ↑                                │
│   Private Key         App ID + Devices + Entitlements       │
│   (Keychain)          (Apple Developer Portal)              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Типы сертификатов:**

| Сертификат | Назначение | Срок действия |
|------------|------------|---------------|
| Development | Отладка на устройствах | 1 год |
| Distribution | App Store / Ad Hoc | 1 год |
| Enterprise | In-House distribution | 3 года |

**Типы Provisioning Profiles:**

```swift
/*
 Development Profile:
 - Список конкретных устройств (до 100)
 - Development сертификат
 - Debug entitlements

 Ad Hoc Profile:
 - Список устройств (до 100)
 - Distribution сертификат
 - Для тестирования вне TestFlight

 App Store Profile:
 - Без списка устройств
 - Distribution сертификат
 - Только для App Store

 Enterprise Profile:
 - Без ограничений устройств
 - Enterprise сертификат
 - Только для компаний (DUNS)
*/
```

**Автоматизация с fastlane:**

```ruby
# Fastfile
lane :certificates do
  match(
    type: "appstore",
    app_identifier: "com.company.app",
    readonly: true
  )
end

lane :release do
  certificates
  build_app(
    scheme: "Release",
    export_method: "app-store"
  )
  upload_to_app_store(
    skip_screenshots: true,
    skip_metadata: true
  )
end
```

### Android Keystore

```
┌─────────────────────────────────────────────────────────────┐
│                   ANDROID SIGNING FLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐                                            │
│  │  Keystore   │ (.jks / .keystore)                         │
│  │  ─────────  │                                            │
│  │  Key Alias  │ ←── Private Key + Certificate              │
│  │  Password   │                                            │
│  └──────┬──────┘                                            │
│         ↓                                                    │
│  ┌─────────────┐    ┌──────────────────┐                    │
│  │ Upload Key  │ →  │ Google Play      │ → Signed APK       │
│  │ (ваш)       │    │ App Signing      │   (Google's key)   │
│  └─────────────┘    └──────────────────┘                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Создание Keystore:**

```bash
# Генерация keystore
keytool -genkeypair \
  -v \
  -storetype PKCS12 \
  -keystore release.keystore \
  -alias release \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000 \
  -storepass 'STORE_PASSWORD' \
  -keypass 'KEY_PASSWORD' \
  -dname "CN=Company Name, OU=Mobile, O=Company, L=City, ST=State, C=US"
```

**Конфигурация подписи:**

```kotlin
// build.gradle.kts
android {
    signingConfigs {
        create("release") {
            storeFile = file("../keystore/release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD")
            keyAlias = System.getenv("KEY_ALIAS")
            keyPassword = System.getenv("KEY_PASSWORD")
        }
    }

    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
        }
    }
}
```

**Play App Signing:**

```
┌────────────────────────────────────────────────────────────┐
│              PLAY APP SIGNING (рекомендуется)               │
├────────────────────────────────────────────────────────────┤
│                                                             │
│  Upload Key (ваш)          App Signing Key (Google)         │
│       ↓                           ↓                         │
│  Подписываете AAB    →    Google переподписывает    →  APK  │
│  для загрузки              для распространения              │
│                                                             │
│  Преимущества:                                              │
│  • Меньший размер APK (App Bundle)                          │
│  • Google хранит ключ безопасно                             │
│  • Можно сбросить upload key при утере                      │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

### Сравнение подписания

| Аспект | iOS | Android |
|--------|-----|---------|
| Управление ключами | Apple (обязательно) | Google (опционально) |
| Утеря ключа | Apple восстановит | Новое приложение* |
| Срок действия | 1-3 года (обновляемый) | До 25 лет |
| Ротация | Автоматическая | Manual / Play Signing |
| Количество ключей | Несколько (по типам) | Один на приложение |

*С Play App Signing можно восстановить upload key

---

## 4. Release Strategies — Стратегии релиза

### Phased Release (iOS)

```
┌─────────────────────────────────────────────────────────────┐
│                  iOS PHASED RELEASE                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  День 1    День 2    День 3    День 4-7    После           │
│    ↓         ↓         ↓          ↓          ↓              │
│   1%        2%        5%        10-50%     100%             │
│                                                              │
│  Особенности:                                                │
│  • Фиксированный 7-дневный график                           │
│  • Нельзя выбрать процент                                   │
│  • Можно приостановить                                      │
│  • Можно выпустить всем сразу                               │
│  • Ручное обновление доступно всем                          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Управление в App Store Connect:**

```
Release Options:
├── Manual release (требует подтверждения)
├── Automatic release (сразу после ревью)
└── Phased release
    ├── Pause (остановить раскатку)
    ├── Resume (продолжить)
    └── Release to All Users (форсировать 100%)
```

### Staged Rollout (Android)

```
┌─────────────────────────────────────────────────────────────┐
│                ANDROID STAGED ROLLOUT                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Гибкие проценты: 0.1% → 1% → 5% → 10% → 25% → 50% → 100%   │
│                                                              │
│  Возможности:                                                │
│  • Любой процент от 0.1% до 100%                            │
│  • Halt rollout (полная остановка)                          │
│  • Увеличение/уменьшение процента                           │
│  • Нет временных ограничений                                │
│  • Мониторинг crash rate и ANR                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**Стратегия постепенного релиза:**

```kotlin
/*
 Рекомендуемая стратегия:

 День 1:  1%  → Мониторинг 24 часа
 День 2:  5%  → Проверка crash rate < 0.5%
 День 3: 10%  → Анализ отзывов
 День 4: 25%  → Проверка метрик
 День 5: 50%  → Финальная проверка
 День 6: 100% → Полный релиз

 Критерии отката (Halt):
 - Crash rate > 2%
 - ANR rate > 0.5%
 - Негативные отзывы > 20%
 - Critical bug reports
*/
```

### Hotfix стратегии

```
┌─────────────────────────────────────────────────────────────┐
│                    HOTFIX COMPARISON                         │
├────────────────────────────┬────────────────────────────────┤
│         iOS                │           Android              │
├────────────────────────────┼────────────────────────────────┤
│ 1. Expedited Review        │ 1. Halt current rollout        │
│    (запросить ускорение)   │    (мгновенно)                 │
│                            │                                │
│ 2. Новый билд + ревью      │ 2. Загрузить hotfix            │
│    (24-48 часов)           │    (без ревью если minor)      │
│                            │                                │
│ 3. Phased release 100%     │ 3. Staged rollout 100%         │
│    (форсировать)           │    (мгновенно)                 │
│                            │                                │
│ Время: 24-72 часа          │ Время: 1-4 часа                │
├────────────────────────────┼────────────────────────────────┤
│ CodePush (React Native)    │ CodePush (React Native)        │
│ • JS bundle updates        │ • JS bundle updates            │
│ • Без App Store ревью      │ • Без Play Store ревью         │
│ • Ограничения Apple        │ • Более гибко                  │
└────────────────────────────┴────────────────────────────────┘
```

---

## 5. Распространённые ошибки

### Ошибка 1: Потеря Keystore/Сертификатов

```
❌ ПРОБЛЕМА:
   Потерян keystore без Play App Signing
   → Приложение нельзя обновить
   → Нужно публиковать как новое

✅ РЕШЕНИЕ:
   • Включить Play App Signing (Android)
   • Использовать match/fastlane (iOS)
   • Хранить в защищённом месте (1Password, AWS Secrets)
   • Документировать пароли отдельно от файлов
```

```bash
# Безопасное хранение (пример с git-crypt)
git-crypt init
echo "*.keystore filter=git-crypt diff=git-crypt" >> .gitattributes
echo "*.p12 filter=git-crypt diff=git-crypt" >> .gitattributes
```

### Ошибка 2: Неправильный versionCode/Build Number

```
❌ ПРОБЛЕМА:
   Version code 142 уже существует
   → Отказ в загрузке

✅ РЕШЕНИЕ:
   • Автоинкремент в CI/CD
   • Формула: MAJOR * 10000 + MINOR * 100 + PATCH
   • Использовать timestamp: yyMMddHHmm
```

```kotlin
// Android: автоматический versionCode
android {
    defaultConfig {
        val code = (System.currentTimeMillis() / 1000 / 60).toInt()
        versionCode = code
        versionName = "2.5.0"
    }
}
```

```ruby
# iOS: автоинкремент с fastlane
lane :bump_build do
  increment_build_number(
    build_number: latest_testflight_build_number + 1
  )
end
```

### Ошибка 3: Staging/Production API endpoints

```
❌ ПРОБЛЕМА:
   Production билд указывает на staging API
   → Приложение не работает у пользователей

✅ РЕШЕНИЕ:
   • Build configurations / flavors
   • Проверка в CI/CD
   • Разные Bundle ID для окружений
```

```kotlin
// Android: productFlavors
android {
    flavorDimensions += "environment"
    productFlavors {
        create("staging") {
            dimension = "environment"
            applicationIdSuffix = ".staging"
            buildConfigField("String", "API_URL", "\"https://staging.api.com\"")
        }
        create("production") {
            dimension = "environment"
            buildConfigField("String", "API_URL", "\"https://api.com\"")
        }
    }
}
```

### Ошибка 4: Забытые Debug-конфигурации

```
❌ ПРОБЛЕМА:
   • Android: debuggable = true в release
   • iOS: Development provisioning profile
   → Отказ в публикации или уязвимости

✅ РЕШЕНИЕ:
   Проверка перед релизом:
```

```bash
# Android: проверка debuggable
aapt dump badging app-release.apk | grep -i debug

# iOS: проверка provisioning
security cms -D -i embedded.mobileprovision | grep -A1 "get-task-allow"
# Должно быть <false/> для App Store
```

### Ошибка 5: Несоответствие Data Safety / Privacy Manifest

```
❌ ПРОБЛЕМА:
   Заявлено "не собираем данные", но используем analytics
   → Отказ в публикации или удаление из стора

✅ РЕШЕНИЕ:
   • Аудит всех SDK и их данных
   • iOS: Privacy Manifest (PrivacyInfo.xcprivacy)
   • Android: Data Safety form
```

```xml
<!-- iOS: PrivacyInfo.xcprivacy -->
<dict>
    <key>NSPrivacyTracking</key>
    <false/>
    <key>NSPrivacyCollectedDataTypes</key>
    <array>
        <dict>
            <key>NSPrivacyCollectedDataType</key>
            <string>NSPrivacyCollectedDataTypeCrashData</string>
            <key>NSPrivacyCollectedDataTypeLinked</key>
            <false/>
            <key>NSPrivacyCollectedDataTypeTracking</key>
            <false/>
            <key>NSPrivacyCollectedDataTypePurposes</key>
            <array>
                <string>NSPrivacyCollectedDataTypePurposeAppFunctionality</string>
            </array>
        </dict>
    </array>
</dict>
```

### Ошибка 6: 100% rollout критического бага

```
❌ ПРОБЛЕМА:
   Выкатили на 100% без staged rollout
   → Массовые жалобы, падение рейтинга

✅ РЕШЕНИЕ:
   • ВСЕГДА staged rollout для production
   • Мониторинг на каждом этапе
   • Автоматический halt при пороговых значениях
```

```yaml
# Пример: GitHub Actions с проверкой
- name: Check crash rate before increasing rollout
  run: |
    CRASH_RATE=$(get_crash_rate.sh)
    if (( $(echo "$CRASH_RATE > 1.0" | bc -l) )); then
      echo "Crash rate too high: $CRASH_RATE%"
      halt_rollout.sh
      exit 1
    fi
```

---

## 6. Mental Models — Ментальные модели

### Model 1: "Airport Security" — Модерация как досмотр

```
┌─────────────────────────────────────────────────────────────┐
│              AIRPORT SECURITY MODEL                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  App Store = Международный аэропорт (JFK)                   │
│  ───────────────────────────────────────                    │
│  • Строгий досмотр ВСЕХ                                     │
│  • Чёткие правила, мало исключений                          │
│  • Длинные очереди (время ревью)                            │
│  • Отказ = возврат и исправление                            │
│  • Безопасность > удобство                                  │
│                                                              │
│  Play Store = Региональный аэропорт                         │
│  ─────────────────────────────────────                      │
│  • Автоматизированный скрининг                              │
│  • Быстрее, но есть проверки                                │
│  • Ручная проверка при "флагах"                             │
│  • Больше доверия разработчику                              │
│  • Баланс безопасности и скорости                           │
│                                                              │
│  Вывод: Готовьте "документы" заранее — метаданные,          │
│         privacy policy, все разрешения обоснованы           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Model 2: "Key Management" — Ключи как банковские карты

```
┌─────────────────────────────────────────────────────────────┐
│              KEY MANAGEMENT MODEL                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Keystore/Сертификат = Банковская карта приложения          │
│  ─────────────────────────────────────────────────          │
│                                                              │
│  iOS Certificates:                                           │
│  • Development = Дебетовая карта (ограниченный доступ)      │
│  • Distribution = Кредитная карта (полный доступ)           │
│  • Apple = Банк (может перевыпустить)                       │
│                                                              │
│  Android Keystore:                                           │
│  • Upload Key = PIN-код (можно сменить)                     │
│  • App Signing Key = Сама карта (без Play Signing —         │
│    потеря = блокировка навсегда)                            │
│  • Play App Signing = Банк хранит карту в сейфе             │
│                                                              │
│  Правила:                                                    │
│  1. Никогда не храните "в кошельке" (в репозитории)         │
│  2. Записывайте PIN отдельно (пароли отдельно от keystore)  │
│  3. Делайте "копии" в сейфе (backup в secure storage)       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Model 3: "Rollout as Experiment" — Релиз как научный эксперимент

```
┌─────────────────────────────────────────────────────────────┐
│              SCIENTIFIC EXPERIMENT MODEL                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Staged Rollout = Клиническое испытание                     │
│  ───────────────────────────────────────                    │
│                                                              │
│  Фаза 1 (1%):   Безопасность                                │
│  ─────────────  • Критические краши?                        │
│                 • Приложение запускается?                   │
│                                                              │
│  Фаза 2 (5-10%): Эффективность                              │
│  ──────────────  • Метрики в норме?                         │
│                  • Конверсия не упала?                       │
│                                                              │
│  Фаза 3 (25-50%): Масштаб                                   │
│  ───────────────  • Нагрузка на серверы?                    │
│                   • Edge cases?                              │
│                                                              │
│  Релиз (100%): Одобрение                                    │
│  ────────────  • Все проверки пройдены                      │
│                • Готовы к поддержке                          │
│                                                              │
│  Halt = Остановка испытания при побочных эффектах           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Quiz — Проверка знаний

### Вопрос 1: Потеря Upload Key

**Ситуация:** Вы потеряли Android upload key (keystore). Play App Signing включён.

**Что произойдёт?**

A) Приложение нельзя обновить, нужно создавать новое
B) Можно запросить сброс upload key в Google Play Console
C) Google автоматически сгенерирует новый ключ
D) Нужно связаться с Google Support для восстановления

<details>
<summary>Ответ</summary>

**B) Можно запросить сброс upload key в Google Play Console**

При включённом Play App Signing:
- Upload key используется только для подписания загружаемого AAB
- App Signing Key (который подписывает финальный APK) хранит Google
- Можно сгенерировать новый upload key и зарегистрировать его

Без Play App Signing был бы ответ A — полная потеря доступа к обновлениям.

</details>

---

### Вопрос 2: Phased Release остановка

**Ситуация:** iOS приложение на Phased Release (день 3, 5% пользователей). Обнаружен критический баг.

**Какой оптимальный порядок действий?**

A) Pause Phased Release → Исправить → Новый билд → Expedited Review
B) Release to All Users → Быстро исправить → Новый билд
C) Ничего не делать, 5% мало → Исправить в следующей версии
D) Pause Phased Release → Исправить → Обычный Review → Resume

<details>
<summary>Ответ</summary>

**A) Pause Phased Release → Исправить → Новый билд → Expedited Review**

Правильная стратегия:
1. **Pause** — остановить распространение багованной версии
2. **Fix** — исправить критический баг
3. **New Build** — подготовить исправленную версию
4. **Expedited Review** — запросить ускоренный ревью для критического бага

Ответ D неверен, потому что Resume продолжит раскатку той же багованной версии. Нужен именно новый билд.

Важно: Expedited Review не гарантирован, но для критических багов обычно одобряется.

</details>

---

### Вопрос 3: Различие тестирования

**Ситуация:** Вам нужно раздать beta-версию 500 внешним тестерам, которые не являются сотрудниками компании.

**Какие варианты подходят?**

| Платформа | Вариант |
|-----------|---------|
| iOS | A) TestFlight Internal Testing |
| iOS | B) TestFlight External Testing |
| Android | C) Internal Testing Track |
| Android | D) Closed Testing Track |

<details>
<summary>Ответ</summary>

**iOS: B) TestFlight External Testing**
**Android: D) Closed Testing Track**

Разбор:
- **A неверно** — Internal Testing: макс 100 человек, только App Store Connect users
- **B верно** — External Testing: до 10,000, по email/ссылке, требует Beta Review
- **C неверно** — Internal Track: макс 100 человек, для QA команды
- **D верно** — Closed Testing: до 200K по email, Google Groups, закрытая ссылка

Ключевое различие: "внешние" тестеры требуют External/Closed треки, "внутренние" (сотрудники с аккаунтами) могут использовать Internal.

</details>

---

## 8. Связь с другими темами

[[ios-app-distribution]] — Дистрибуция iOS-приложений включает App Store Connect, TestFlight (Internal/External), Ad Hoc, Enterprise и Custom B2B. Заметка детально разбирает процесс от Xcode Archive до публикации: metadata requirements, screenshots guidelines, App Review процесс, phased release, а также автоматизацию через Fastlane deliver. Понимание iOS-дистрибуции необходимо для сравнения с Play Store и для настройки единого release pipeline.

[[android-apk-aab]] — Android-дистрибуция строится вокруг Play Console: Internal/Closed/Open Testing tracks, Production с staged rollout, AAB формат с Dynamic Delivery. Заметка объясняет различия APK и AAB, Play Feature Delivery, in-app updates API и процесс review. Сравнение с iOS показывает, что Google дает больше контроля над rollout (percentage-based), а Apple — больше инструментов для тестирования (TestFlight).

[[cross-code-signing]] — Code signing — обязательный этап перед дистрибуцией на обеих платформах. Заметка сравнивает iOS Provisioning Profiles с Android Keystore, объясняет цепочки доверия и автоматизацию подписи в CI/CD. Без корректной подписи приложение не пройдёт ни App Store Review, ни Play Store проверку. Связь с дистрибуцией прямая: ошибки в подписи — самая частая причина сбоев при публикации.

---

## Источники и дальнейшее чтение

- Meier R. (2022). *Professional Android.* — Разбирает Play Store публикацию, AAB формат, staged rollout, in-app updates и Play Feature Delivery. Практическое руководство по подготовке Android-приложения к release.
- Neuburg M. (2023). *iOS Programming Fundamentals with Swift.* — Охватывает App Store Connect, TestFlight, provisioning и процесс публикации iOS-приложений. Помогает понять требования Apple к метаданным, скриншотам и App Review guidelines.

---

## Changelog

- 2026-01-11: Создание документа, сравнение App Store и Play Store дистрибуции

---

## Проверь себя

> [!question]- Почему App Store Review занимает дольше, чем Google Play Review? Какие типы проверок проводит каждый store?
> App Store Review: ручная проверка (human reviewers) + автоматические сканы. Проверяют: соответствие App Store Review Guidelines (safety, performance, business, design, legal), metadata accuracy, privacy compliance, in-app purchase requirements. Средняя: 24-48 часов. Play Store: преимущественно автоматические проверки (malware, policy violations, content rating), ручная только при флагах. Средняя: несколько часов. Apple строже: часто отклоняет по дизайну, UX, или hidden features. Google отклоняет реже, но может удалить после публикации.

> [!question]- Сценарий: приложение отклонено App Store с причиной "Guideline 2.1 - Performance - App Completeness". Какие типичные причины и как исправить?
> Guideline 2.1: приложение не работает как ожидается или содержит баги. Типичные причины: 1) crash при запуске (особенно на старых устройствах/iOS версиях), 2) нерабочие функции (кнопки ведут в никуда, пустые экраны), 3) placeholder-контент ("Lorem ipsum", demo data), 4) требуется login но нет demo аккаунта для reviewer. Исправления: тестировать на минимальной поддерживаемой iOS версии, убрать placeholder, предоставить demo credentials в App Store Connect (Review Notes), протестировать все user flows.

> [!question]- Почему Google рекомендует AAB (Android App Bundle) вместо APK для распространения?
> AAB содержит весь код и ресурсы, но Google Play генерирует оптимизированные APK для каждого устройства (Dynamic Delivery). Split APKs по: ABI (arm64, x86), screen density (hdpi, xxhdpi), language. Результат: размер скачивания на 15-30% меньше. Дополнительно: Play Feature Delivery для on-demand модулей, Play Asset Delivery для больших ассетов (игры). APK -- один файл для всех устройств, больше размер. AAB обязателен для новых приложений в Play Store.

> [!question]- Как staged rollout работает на обеих платформах и зачем он нужен?
> iOS: Phased Release -- автоматически раскатывает обновление на 1%, 2%, 5%, 10%, 20%, 50%, 100% за 7 дней. Пользователи с автообновлением получают постепенно. Можно остановить (pause) при обнаружении проблем. Android: Staged Rollout -- вручную устанавливаешь процент (1%, 5%, 10%...). Можно изменить процент или откатить (halt) в любой момент. Зачем: обнаружить crash/regression на малом проценте до 100% rollout. Мониторинг через Crashlytics/Sentry/MetricKit.

---

## Ключевые карточки

Чем App Store Connect отличается от Google Play Console?
?
App Store Connect: TestFlight (Internal/External), App Analytics, Phased Release, App Review (24-48h), Pricing tiers (Apple sets prices). Play Console: Testing tracks (Internal/Closed/Open), Android Vitals, Staged Rollout (manual %), Review (hours), Free pricing control. Обе: подробная аналитика, crash reporting, A/B testing для store listing. Apple строже в review, Google гибче в rollout.

Какие типы тестирования доступны перед публикацией?
?
iOS TestFlight: Internal Testing (до 100, App Store Connect users, мгновенно), External Testing (до 10000, по email/link, требует Beta Review). Android: Internal Testing (до 100, мгновенно), Closed Testing (до 200K, Google Groups/emails), Open Testing (публичный, через Play Store listing). Оба: staged rollout для production.

Что такое App Review и какие Guidelines проверяются?
?
Apple App Review Guidelines: 5 категорий -- Safety (скрытые features, malware), Performance (completeness, accuracy), Business (subscriptions, in-app purchase rules), Design (UI guidelines, UX quality), Legal (privacy, GDPR). Google Play Policies: аналогичные, но менее строгие к дизайну. Обе: privacy policy обязательна, COPPA для детских приложений, финансовые ограничения для крипто/gambling.

Как работает In-App Update API на Android и есть ли аналог на iOS?
?
Android: Play Core In-App Update API -- проверяет доступность обновления, показывает Flexible (продолжай использовать) или Immediate (блокирующий) update UI. Скачивание в фоне. iOS: нет нативного API. Можно проверять версию через iTunes Lookup API и показать alert с ссылкой на App Store. Сторонние: Firebase Remote Config для force update. Apple не поддерживает принудительное обновление.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[cross-testing]] | Тестирование -- последний шаг перед публикацией |
| Углубиться | [[ios-app-distribution]] | TestFlight, App Store Connect из раздела iOS |
| Смежная тема | [[android-apk-aab]] | AAB, Play App Signing из раздела Android |
| Обзор | [[cross-platform-overview]] | Вернуться к обзору раздела |
