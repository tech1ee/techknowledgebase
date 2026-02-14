---
title: "Intent: resolution, PendingIntent и Deep Links под капотом"
created: 2026-01-27
modified: 2026-02-13
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/intents
  - type/deep-dive
  - level/expert
related:
  - "[[android-app-components]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-navigation]]"
  - "[[android-bundle-parcelable]]"
  - "[[android-context-internals]]"
  - "[[android-permissions-security]]"
  - "[[android-handler-looper]]"
  - "[[android-process-memory]]"
  - "[[android-background-work]]"
  - "[[android-binder-internals]]"
  - "[[android-manifest-merging]]"
  - "[[android-testing]]"
cs-foundations: [message-passing, pattern-matching, uri-scheme, capability-token, ipc, pub-sub, loose-coupling, indexing, delegation, serialization]
prerequisites:
  - "[[android-app-components]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-navigation]]"
  - "[[android-permissions-security]]"
reading_time: 116
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Intent: resolution, PendingIntent и Deep Links под капотом

> **TL;DR:** Intent — это объект-сообщение для межкомпонентной коммуникации. **Explicit Intent** напрямую указывает целевой компонент (ComponentName), **Implicit Intent** описывает действие (action + data + category) и система находит подходящий компонент через IntentFilter matching. Matching работает через `IntentResolver` в AOSP: фильтры индексируются по scheme, MIME type и action в 6 lookup-maps ("cuts"), а `buildResolveList()` проверяет каждый кандидат. **PendingIntent** — это Binder-токен (capability token), делегирующий право выполнить Intent от имени создателя; с Android 12 обязателен FLAG_IMMUTABLE или FLAG_MUTABLE. **App Links** (http/https + `assetlinks.json`) позволяют открывать ссылки напрямую в приложении без disambiguation dialog, в отличие от **Deep Links** (custom scheme). **Result API** (ActivityResultContracts) заменяет устаревший onActivityResult. **Intent flags** управляют поведением Task/Back Stack. **Package visibility** (Android 11+) ограничивает видимость приложений через `<queries>`.

---

## Зачем это нужно

### Проблема: Intent — ядро Android, которое мало кто понимает глубоко

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| `ActivityNotFoundException` | Нет компонента, matching implicit Intent | Crash при попытке открыть URL/email |
| Disambiguation dialog у пользователя | Несколько приложений match одному Intent | Плохой UX, пользователь путается |
| App Links не открывают приложение | Не настроен `assetlinks.json` или не пройдена верификация | Ссылки открываются в браузере |
| `SecurityException` при PendingIntent | Неверные flags или mutable PendingIntent | Crash на Android 12+ |
| Intent extras теряются/пустые | Bundle не содержит Parcelable или пересоздан | Данные не доставляются в целевой компонент |
| Перехват Intent вредоносным приложением | Implicit Intent к Service без ограничений | Утечка данных, security vulnerability |
| `onActivityResult` не вызывается | Неверный requestCode или launch mode | Потеря результата, сломанный UX-флоу |
| `queryIntentActivities()` возвращает пустой список | Package visibility (Android 11+), нет `<queries>` | Приложение "не видит" другие приложения |
| Intent flags конфликтуют | Комбинация несовместимых FLAG_* | Неожиданное поведение Task/Back Stack |
| Custom deep link перехвачен чужим приложением | Custom scheme без верификации | Пользователь попадает не туда |

### Актуальность в 2024-2026

**Intent — фундамент Android IPC:**

```
КАЖДОЕ ВЗАИМОДЕЙСТВИЕ = Intent:

Запуск Activity          -> startActivity(intent)
Запуск Service           -> startService(intent)
Отправка Broadcast       -> sendBroadcast(intent)
Ответ на Deep Link       -> IntentFilter + autoVerify
Уведомление (tap)        -> PendingIntent
Alarm (планирование)     -> PendingIntent + AlarmManager
Widget (клик)            -> PendingIntent
Navigation (Jetpack)     -> implicit intents + deep links
Share Sheet              -> Intent.createChooser()
Получение результата     -> ActivityResultContracts
Файловый доступ          -> Intent + FLAG_GRANT_*_PERMISSION
```

**Ключевые изменения (2022-2026):**
- **Android 12 (API 31):** Обязательный FLAG_IMMUTABLE / FLAG_MUTABLE для PendingIntent
- **Android 12:** Строгая верификация App Links — без `assetlinks.json` ссылки открываются в браузере
- **Android 12:** Exported компоненты с intent-filter обязаны явно указать `android:exported`
- **Android 13 (API 33):** Intent matching ужесточён — target app должен объявить matching actions и categories
- **Android 14 (API 34):** Ограничения на implicit broadcast для повышения безопасности
- **Android 14:** Runtime-registered broadcasts receivers должны указать export behavior
- **Android 15 (API 35):** Dynamic App Links — `assetlinks.json` как динамический конфигуратор маршрутов

**Что вы узнаете:**
1. Explicit vs Implicit Intent — путь resolution через ActivityManagerService
2. IntentFilter matching: action, category, data — три теста
3. AOSP IntentResolver: "cuts" система и lookup maps
4. PendingIntent: Binder capability token и identity delegation
5. Deep Links vs App Links: верификация через Digital Asset Links
6. Intent flags: полный каталог и комбинации
7. Chooser и ShareSheet: внутреннее устройство
8. Result API: ActivityResultContracts и registerForActivityResult
9. Package visibility (Android 11+): `<queries>` element
10. Тестирование Intent-ов: Espresso Intents, Robolectric shadows
11. Безопасность: когда Intent = уязвимость

---

## Prerequisites

Для полного понимания материала необходимо:

| Тема | Зачем | Где изучить |
|------|-------|-------------|
| **[[android-app-components]]** | Activity, Service, BroadcastReceiver, ContentProvider — 4 типа компонентов, между которыми Intent обеспечивает коммуникацию | Раздел Android |
| **[[android-bundle-parcelable]]** | Intent extras = Bundle; данные передаются через Parcel/Binder IPC | Раздел Android |
| **[[android-context-internals]]** | startActivity(), startService(), sendBroadcast() — методы Context | Раздел Android |
| **[[android-activity-lifecycle]]** | Запуск Activity через Intent связан с lifecycle callbacks | Раздел Android |
| **[[android-binder-internals]]** | PendingIntent хранится как Binder token в system_server | Раздел Android |
| **URI / URL** | Data часть Intent — это URI (scheme://host:port/path) | Базовые знания |
| **Kotlin Coroutines** | Современные API (ActivityResultLauncher) используют корутины | Раздел Kotlin |
| **AndroidManifest.xml** | IntentFilter, queries, exported объявляются в манифесте | Раздел Android |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Intent** | Объект-сообщение для запуска компонентов или передачи данных | **Письмо** — содержит адрес (explicit) или описание (implicit) |
| **Explicit Intent** | Intent с указанным ComponentName (package + class) | **Письмо с точным адресом** — доставляется напрямую |
| **Implicit Intent** | Intent с action/data/category, без целевого компонента | **Объявление на доске** — кто подходит, тот и ответит |
| **IntentFilter** | Декларация в Manifest: какие Intent-ы компонент принимает | **Вывеска на магазине** — "мы принимаем оплату картой" |
| **IntentResolver** | AOSP класс, выполняющий matching Intent -> IntentFilter | **Почтовое отделение** — сортирует письма по адресам |
| **PendingIntent** | Binder-токен для выполнения Intent от имени создателя | **Доверенность** — даёт право действовать от вашего имени |
| **App Links** | HTTP/HTTPS deep links с верификацией через `assetlinks.json` | **Верифицированная визитка** — подтверждённая принадлежность |
| **Deep Links** | Любые URI (включая custom scheme), ведущие в приложение | **QR-код** — ведёт по ссылке, но не доказывает авторство |
| **Action** | Строка, описывающая действие (ACTION_VIEW, ACTION_SEND) | **Глагол** в предложении — "открыть", "отправить" |
| **Category** | Дополнительная классификация Intent (DEFAULT, BROWSABLE) | **Контекст** — "из браузера", "по умолчанию" |
| **ComponentName** | Пара (package, class) — уникальный идентификатор компонента | **ФИО + паспорт** — однозначно идентифицирует человека |
| **ResolveInfo** | Результат resolution: информация о подходящем компоненте | **Карточка из картотеки** — данные найденного получателя |
| **Chooser** | Системный диалог выбора приложения для обработки Intent | **Меню** — выберите, какой "курьер" доставит |
| **Bundle** | Контейнер key-value для передачи данных через Intent extras | **Посылка** — содержимое, прикреплённое к письму |
| **ActivityResultContract** | Типизированный контракт для получения результата от Activity | **Бланк заявления** — шаблон запроса с ожидаемым ответом |
| **Digital Asset Links** | Протокол верификации связи между приложением и доменом | **Нотариальная печать** — подтверждает владение доменом |
| **Package Visibility** | Ограничение видимости установленных приложений (Android 11+) | **Закрытый телефонный справочник** — видны только объявленные контакты |

---

## 1. Explicit vs Implicit Intent

### 1.1 ЧТО: два способа адресации

```
+------------------------------------------------------------------+
|                    ДВА ТИПА INTENT                               |
|                                                                  |
|  EXPLICIT INTENT                  IMPLICIT INTENT                |
|  +------------------+           +----------------------+         |
|  | component:        |           | action: ACTION_VIEW   |         |
|  |   com.app/.Detail |           | data: https://...     |         |
|  | extras: Bundle    |           | category: BROWSABLE   |         |
|  +------+-----------+           | extras: Bundle        |         |
|         |                        +----------+-----------+         |
|         v                                   v                    |
|  ActivityManager                 PackageManager                  |
|  -> напрямую запускает            -> queryIntentActivities()       |
|    указанный компонент           -> IntentFilter matching         |
|                                  -> 0 matches: Exception          |
|  Безопасно: вы знаете            -> 1 match: запускает            |
|  кто получит Intent              -> N matches: chooser dialog     |
|                                                                  |
|  Когда использовать:             Когда использовать:             |
|  * Навигация внутри app          * Открыть URL в браузере       |
|  * Запуск конкретного Service    * Поделиться контентом         |
|  * Работа со своими компонентами * Отправить email/SMS          |
|  * IPC к известному компоненту   * Выбрать файл/фото            |
+------------------------------------------------------------------+
```

### 1.2 ПОЧЕМУ: зачем нужны два типа

**Explicit Intent** — для детерминированного запуска конкретного компонента внутри приложения или для IPC к известному компоненту другого приложения.

**Implicit Intent** — для **loose coupling**: приложение описывает _что_ нужно сделать, а не _кто_ это делает. Это позволяет:
1. Заменять приложения (другой браузер, другой email-клиент)
2. Расширять экосистему (новое приложение может обрабатывать существующие Intent-ы)
3. Изолировать знания (отправителю не нужно знать о получателе)

**Архитектурный принцип:**
```
+------------------------------------------------------------------+
|             INTENT КАК РЕАЛИЗАЦИЯ MESSAGE PASSING                |
|                                                                  |
|  ООП / Tight Coupling:          Intent / Loose Coupling:         |
|                                                                  |
|  class App {                    class App {                      |
|    val browser = Chrome()         fun open(url: String) {        |
|    fun open(url: String) {          val i = Intent(ACTION_VIEW,  |
|      browser.load(url)                Uri.parse(url))            |
|    }                                startActivity(i)             |
|  }                                }                              |
|                                 }                                |
|  App ЗНАЕТ о Chrome.            App НЕ ЗНАЕТ кто откроет.       |
|  Замена = изменение кода.       Замена = установка другого       |
|                                 браузера, код не меняется.       |
+------------------------------------------------------------------+
```

### 1.3 КАК РАБОТАЕТ: полный путь Intent через систему

**Explicit Intent — прямой путь:**

```
+------------------------------------------------------------------+
|  startActivity(Intent(this, DetailActivity::class.java))        |
|         |                                                        |
|         v                                                        |
|  Instrumentation.execStartActivity()                             |
|         |                                                        |
|         v  (Binder IPC)                                          |
|  ActivityTaskManagerService.startActivity()                      |
|         |  // Intent содержит ComponentName                      |
|         |  // -> прямой lookup по package + class                |
|         v                                                        |
|  ActivityStarter.execute()                                       |
|         |  // Проверяет permissions                              |
|         |  // Находит/создаёт Task                              |
|         v                                                        |
|  ActivityThread.handleLaunchActivity()                            |
|         |  // В процессе целевого приложения                     |
|         v                                                        |
|  Activity.onCreate(savedInstanceState)                           |
|         |  val data = intent.getStringExtra("key")              |
|         v                                                        |
|  Компонент запущен                                               |
+------------------------------------------------------------------+
```

**Implicit Intent — путь через resolution:**

```
+------------------------------------------------------------------+
|  val intent = Intent(Intent.ACTION_VIEW,                         |
|      Uri.parse("https://example.com"))                           |
|  startActivity(intent)                                           |
|         |                                                        |
|         v                                                        |
|  Instrumentation.execStartActivity()                             |
|         |                                                        |
|         v  (Binder IPC)                                          |
|  ActivityTaskManagerService.startActivity()                      |
|         |  // Intent НЕ содержит ComponentName                   |
|         |  // -> нужен resolution                                |
|         v                                                        |
|  PackageManagerService.queryIntentActivities()                   |
|         |                                                        |
|         v                                                        |
|  ComponentResolver.queryActivities()                             |
|         |                                                        |
|         v                                                        |
|  IntentResolver.queryIntent()                                    |
|         |  // 6 "cuts" по lookup maps                           |
|         |  // buildResolveList() -> проверка каждого кандидата    |
|         v                                                        |
|  Результат: List<ResolveInfo>                                    |
|         |                                                        |
|         +-- 0 кандидатов -> ActivityNotFoundException             |
|         +-- 1 кандидат -> запускаем напрямую                     |
|         +-- N кандидатов:                                        |
|             +-- App Links verified? -> автоматически              |
|             +-- Нет -> Chooser Dialog                             |
+------------------------------------------------------------------+
```

### 1.4 КАК ПРИМЕНЯТЬ: создание Intent-ов

```kotlin
// === EXPLICIT INTENT ===

// Вариант 1: через Class
val intent = Intent(this, DetailActivity::class.java).apply {
    putExtra("user_id", 42L)       // Передаём ID пользователя
    putExtra("source", "home_screen") // Откуда пришли
}
startActivity(intent)

// Вариант 2: через ComponentName (для IPC к другому приложению)
val intent = Intent().apply {
    component = ComponentName(
        "com.other.app",                    // Пакет целевого приложения
        "com.other.app.SharedActivity"      // Полное имя класса
    )
    putExtra("data", "shared_content")
}
startActivity(intent)

// Вариант 3: через setClassName (эквивалент ComponentName)
val intent = Intent().apply {
    setClassName(
        "com.other.app",
        "com.other.app.SharedActivity"
    )
}
startActivity(intent)

// === IMPLICIT INTENT ===

// Открыть URL в браузере
val browseIntent = Intent(Intent.ACTION_VIEW,
    Uri.parse("https://developer.android.com"))
startActivity(browseIntent)

// Поделиться текстом
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"                           // MIME тип контента
    putExtra(Intent.EXTRA_TEXT, "Посмотри это!")   // Текст для передачи
    putExtra(Intent.EXTRA_SUBJECT, "Интересная статья") // Тема
}
startActivity(Intent.createChooser(shareIntent, "Поделиться через"))

// Отправить email
val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
    data = Uri.parse("mailto:") // Только email-приложения
    putExtra(Intent.EXTRA_EMAIL, arrayOf("user@example.com"))
    putExtra(Intent.EXTRA_SUBJECT, "Тема письма")
}
if (emailIntent.resolveActivity(packageManager) != null) {
    startActivity(emailIntent)
}

// Открыть файл
val fileIntent = Intent(Intent.ACTION_VIEW).apply {
    setDataAndType(
        fileUri,                            // URI файла
        "application/pdf"                   // MIME тип файла
    )
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION) // Даём доступ на чтение
}
startActivity(fileIntent)

// Позвонить по номеру
val dialIntent = Intent(Intent.ACTION_DIAL).apply {
    data = Uri.parse("tel:+79001234567")   // Номер телефона
}
startActivity(dialIntent)

// Открыть настройки приложения
val settingsIntent = Intent(
    android.provider.Settings.ACTION_APPLICATION_DETAILS_SETTINGS,
    Uri.parse("package:${packageName}")    // Наш пакет
)
startActivity(settingsIntent)

// Открыть карту с координатами
val mapIntent = Intent(Intent.ACTION_VIEW).apply {
    data = Uri.parse("geo:55.7558,37.6173?q=Москва") // Координаты + запрос
}
startActivity(mapIntent)
```

### 1.5 ПОДВОДНЫЕ КАМНИ

**Ошибка 1: Implicit Intent без проверки**

```kotlin
// --- CRASH: ActivityNotFoundException если нет подходящего приложения
startActivity(Intent(Intent.ACTION_VIEW, Uri.parse("custom://deeplink")))

// +++ Проверяем перед запуском
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("custom://deeplink"))
if (intent.resolveActivity(packageManager) != null) {
    startActivity(intent)
} else {
    // Fallback: открыть в браузере или показать сообщение
}

// +++ Или используем try-catch
try {
    startActivity(intent)
} catch (e: ActivityNotFoundException) {
    Toast.makeText(this, "Нет приложения для этого действия", LENGTH_SHORT).show()
}
```

**Ошибка 2: Implicit Intent для Service (security risk)**

```kotlin
// --- ЗАПРЕЩЕНО с Android 5.0 (API 21)
// Implicit Intent к Service — security risk!
val serviceIntent = Intent("com.example.ACTION_DO_WORK")
startService(serviceIntent)
// -> IllegalArgumentException: Service Intent must be explicit

// +++ Всегда используйте explicit Intent для Service
val serviceIntent = Intent(this, MyService::class.java)
startService(serviceIntent)
```

**Ошибка 3: Package visibility (Android 11+)**

```kotlin
// --- На Android 11+ queryIntentActivities() может вернуть пустой список
// Нужно объявить <queries> в Manifest

// AndroidManifest.xml:
// <queries>
//     <intent>
//         <action android:name="android.intent.action.VIEW" />
//         <data android:scheme="https" />
//     </intent>
// </queries>

// Или для конкретного пакета:
// <queries>
//     <package android:name="com.other.app" />
// </queries>
```

**Ошибка 4: Забыли android:exported на Android 12+**

```kotlin
// --- CRASH при установке на Android 12+
// <activity android:name=".MyActivity">
//     <intent-filter>
//         <action android:name="android.intent.action.VIEW" />
//     </intent-filter>
// </activity>
// -> Manifest merger error: android:exported must be explicitly specified

// +++ Явно укажите exported
// <activity android:name=".MyActivity"
//     android:exported="true">   <-- обязательно для компонентов с intent-filter
//     <intent-filter>
//         <action android:name="android.intent.action.VIEW" />
//     </intent-filter>
// </activity>
```

---

## 2. IntentFilter Matching: три теста

### 2.1 ЧТО: IntentFilter — декларация возможностей компонента

```xml
<!-- AndroidManifest.xml -->
<activity android:name=".ShareActivity"
    android:exported="true">

    <!-- IntentFilter: "я могу отправлять текст" -->
    <intent-filter>
        <!-- ACTION: какое действие поддерживаю -->
        <action android:name="android.intent.action.SEND" />

        <!-- CATEGORY: в каком контексте -->
        <category android:name="android.intent.category.DEFAULT" />

        <!-- DATA: какой тип данных -->
        <data android:mimeType="text/plain" />
    </intent-filter>

    <!-- Второй фильтр: "я могу отправлять изображения" -->
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="image/*" />
    </intent-filter>
</activity>
```

### 2.2 ПОЧЕМУ: алгоритм matching критически важен

IntentFilter matching определяет:
- Какое приложение откроет ссылку пользователя
- Кто получит broadcast-сообщение
- Будет ли показан chooser dialog или приложение откроется напрямую
- Безопасность: неверный фильтр = перехват данных чужим приложением

### 2.3 КАК РАБОТАЕТ: три теста matching

```
+------------------------------------------------------------------+
|           INTENTFILTER MATCHING: 3 ТЕСТА                         |
|                                                                  |
|  Intent: { action=SEND, category=DEFAULT, type="text/plain" }    |
|                                                                  |
|  ТЕСТ 1: ACTION (обязательный)                                   |
|  ----------------------------                                    |
|  Intent.action MUST match хотя бы одному <action> в фильтре     |
|                                                                  |
|  Filter: <action name="SEND" /> <-- match!                       |
|  Правило: фильтр может объявить несколько action — достаточно    |
|  совпадения хотя бы с одним. Если Intent не имеет action и      |
|  фильтр имеет хотя бы один — тест ПРОВАЛЕН.                     |
|  [PASSED]                                                        |
|                                                                  |
|  ТЕСТ 2: CATEGORY (обязательный)                                 |
|  --------------------------------                                |
|  ВСЕ категории из Intent MUST присутствовать в фильтре          |
|                                                                  |
|  Intent: { DEFAULT }                                             |
|  Filter: { DEFAULT } <-- все present!                            |
|  Правило: фильтр может иметь дополнительные категории, но       |
|  ВСЕ категории Intent должны быть в фильтре.                    |
|  CATEGORY_DEFAULT обязательна для implicit Intent!               |
|  Если не объявлена в фильтре — implicit Intent НИКОГДА           |
|  не будет доставлен (startActivity добавляет DEFAULT автоматически)
|  [PASSED]                                                        |
|                                                                  |
|  ТЕСТ 3: DATA (URI + MIME type)                                  |
|  --------------------------------                                |
|  Сложный тест: сравниваются URI и MIME type                      |
|                                                                  |
|  Intent: type="text/plain"                                       |
|  Filter: <data mimeType="text/plain" /> <-- match!               |
|  [PASSED]                                                        |
|                                                                  |
|  ВСЕ 3 ТЕСТА ПРОЙДЕНЫ -> КОМПОНЕНТ ПОДХОДИТ                     |
+------------------------------------------------------------------+
```

**Тест DATA — подробные правила URI matching:**

```
+------------------------------------------------------------------+
|               DATA TEST: URI MATCHING RULES                      |
|                                                                  |
|  URI структура: scheme://host:port/path                          |
|                                                                  |
|  1. Intent без URI и без MIME -> pass только если фильтр тоже    |
|     без URI и без MIME                                           |
|                                                                  |
|  2. Intent с URI, без MIME -> URI должен match, фильтр           |
|     тоже без MIME                                                |
|                                                                  |
|  3. Intent с MIME, без URI -> MIME должен match, фильтр          |
|     тоже без URI                                                 |
|                                                                  |
|  4. Intent с URI И MIME -> оба должны match                      |
|     Исключение: content: и file: URI подразумевают               |
|     что MIME будет проверен отдельно                              |
|                                                                  |
|  Правила URI matching:                                           |
|  * scheme: exact match (case-sensitive!)                         |
|  * host: exact match или wildcard (*.example.com)               |
|  * port: exact match (если указан в фильтре)                    |
|  * path: exact match или pathPrefix / pathPattern               |
|                                                                  |
|  Правила MIME matching:                                          |
|  * Exact: "image/png" == "image/png"                             |
|  * Subtype wildcard: "image/*" matches "image/png"              |
|  * Full wildcard: "*/*" matches всё                              |
|  * Case-sensitive! "Image/PNG" != "image/png"                    |
+------------------------------------------------------------------+
```

**Таблица: Data test — все комбинации:**

| Intent URI | Intent MIME | Filter URI | Filter MIME | Результат |
|-----------|-------------|-----------|-------------|-----------|
| нет | нет | нет | нет | PASS |
| нет | нет | есть | нет | FAIL |
| есть | нет | нет | нет | FAIL |
| нет | `text/plain` | нет | `text/plain` | PASS |
| нет | `text/plain` | нет | `text/*` | PASS |
| нет | `text/plain` | нет | `*/*` | PASS |
| `https://a.com` | нет | `https` | нет | PASS |
| `https://a.com` | нет | `http` | нет | FAIL |
| `https://a.com` | `text/html` | `https` | `text/html` | PASS |
| `https://a.com` | `text/html` | `https` | `image/*` | FAIL |
| `content://x` | `text/plain` | нет | `text/plain` | PASS (content/file — особый случай) |

### 2.4 КАК РАБОТАЕТ: IntentResolver "cuts" в AOSP

```
+------------------------------------------------------------------+
|         AOSP IntentResolver: LOOKUP MAPS ("CUTS")                |
|                                                                  |
|  При установке приложения IntentFilter индексируются:            |
|                                                                  |
|  ComponentResolver.addAllComponents()                            |
|    -> addActivitiesLocked()                                      |
|      -> mActivities.addActivity(activity)                        |
|        -> IntentResolver.addFilter(filter)                       |
|                                                                  |
|  addFilter() индексирует в 6 lookup maps:                        |
|                                                                  |
|  +---------------------------------------------------------+     |
|  |  1. mTypeToFilter        -- full MIME (image/png)        |     |
|  |  2. mBaseTypeToFilter    -- base MIME (image/*)          |     |
|  |  3. mWildTypeToFilter    -- wild MIME (*/* или неполные) |     |
|  |  4. mTypedActionToFilter -- action с MIME type           |     |
|  |  5. mSchemeToFilter      -- scheme (https, geo, tel)     |     |
|  |  6. mActionToFilter      -- action без data (fallback)   |     |
|  +---------------------------------------------------------+     |
|                                                                  |
|  При resolution — queryIntent() проверяет cuts последовательно:  |
|                                                                  |
|  queryIntent(intent, resolvedType, ...)                          |
|    |                                                             |
|    +-- MIME type задан?                                          |
|    |   +-- Exact MIME -> mTypeToFilter.get(type)                 |
|    |   +-- Base type -> mBaseTypeToFilter.get(baseType)          |
|    |   +-- Wild type -> mWildTypeToFilter.get("*")               |
|    |   +-- type == "*/*" -> mTypedActionToFilter.get(action)     |
|    |                                                             |
|    +-- Scheme задан?                                             |
|    |   +-- mSchemeToFilter.get(scheme)                           |
|    |                                                             |
|    +-- Нет scheme, нет MIME?                                     |
|        +-- mActionToFilter.get(action)                           |
|                                                                  |
|  Каждый "cut" -> buildResolveList()                              |
|    -> intentFilter.match() для каждого кандидата                 |
|    -> finalList (только подходящие)                              |
+------------------------------------------------------------------+
```

**Подробная схема buildResolveList():**

```
+------------------------------------------------------------------+
|         buildResolveList() — ПРОВЕРКА КАЖДОГО КАНДИДАТА          |
|                                                                  |
|  Вход: List<IntentFilter> candidates (из lookup map)             |
|                                                                  |
|  for (filter in candidates) {                                    |
|    |                                                             |
|    +-- 1. Проверка action:                                       |
|    |   filter.matchAction(intent.action)                         |
|    |   -> action есть в фильтре? Нет -> SKIP                    |
|    |                                                             |
|    +-- 2. Проверка categories:                                   |
|    |   filter.matchCategories(intent.categories)                 |
|    |   -> ВСЕ категории Intent есть в фильтре? Нет -> SKIP      |
|    |                                                             |
|    +-- 3. Проверка data (URI + MIME):                            |
|    |   filter.matchData(intent.scheme, intent.type,              |
|    |                     intent.data)                             |
|    |   -> scheme match? host match? path match?                  |
|    |   -> MIME type match? Нет -> SKIP                           |
|    |                                                             |
|    +-- 4. Все проверки пройдены -> добавить в result list        |
|  }                                                               |
|                                                                  |
|  Выход: List<ResolveInfo> (подходящие компоненты)                |
+------------------------------------------------------------------+
```

### 2.5 КАК ПРИМЕНЯТЬ: правильное объявление IntentFilter

```xml
<!-- +++ ПРАВИЛЬНО: обработка Deep Link -->
<activity android:name=".ProductActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="https"
            android:host="www.example.com"
            android:pathPrefix="/product/" />
    </intent-filter>
</activity>

<!-- ВАЖНО: раздельные intent-filter для разных URI -->
<!-- --- НЕПРАВИЛЬНО: объединение разных scheme/host в одном фильтре -->
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:scheme="https" android:host="www.example.com" />
    <data android:scheme="myapp" android:host="open" />
    <!-- Android МЕРЖИТ data elements! Это создаст 4 комбинации:
         https://www.example.com, https://open,
         myapp://www.example.com, myapp://open -->
</intent-filter>

<!-- +++ ПРАВИЛЬНО: отдельные фильтры -->
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="https" android:host="www.example.com" />
</intent-filter>
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data android:scheme="myapp" android:host="open" />
</intent-filter>
```

```kotlin
// Обработка входящего Intent в Activity
class ProductActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Обработка Intent (как от explicit, так и от implicit)
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        // Для singleTop/singleTask — новый Intent приходит сюда
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent) {
        when (intent.action) {
            Intent.ACTION_VIEW -> {
                // Deep Link: https://www.example.com/product/42
                val productId = intent.data?.lastPathSegment
                    ?.toLongOrNull()
                if (productId != null) {
                    loadProduct(productId)
                }
            }
            else -> {
                // Explicit Intent: из навигации внутри приложения
                val productId = intent.getLongExtra("product_id", -1)
                if (productId != -1L) {
                    loadProduct(productId)
                }
            }
        }
    }
}
```

### 2.6 ПОДВОДНЫЕ КАМНИ

**CATEGORY_DEFAULT — забытый но критичный:**

```xml
<!-- --- Implicit Intent НИКОГДА не будет доставлен! -->
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <!-- Забыли DEFAULT -> startActivity() добавляет DEFAULT автоматически
         -> фильтр не совпадёт! -->
    <data android:scheme="myapp" />
</intent-filter>

<!-- +++ ВСЕГДА добавляйте DEFAULT для implicit Intent -->
<intent-filter>
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:scheme="myapp" />
</intent-filter>

<!-- Исключение: LAUNCHER не требует DEFAULT -->
<intent-filter>
    <action android:name="android.intent.action.MAIN" />
    <category android:name="android.intent.category.LAUNCHER" />
    <!-- MAIN + LAUNCHER — это особый случай, DEFAULT не нужна -->
</intent-filter>
```

**pathPattern vs pathPrefix — важное различие:**

```xml
<!-- pathPrefix: "/product/" матчит "/product/42", "/product/abc/def" -->
<data android:pathPrefix="/product/" />

<!-- pathPattern: поддерживает wildcards -->
<!-- ".*" = любая строка, "." = любой символ -->
<data android:pathPattern="/product/.*" />

<!-- pathAdvancedPattern (Android 12+): regex-подобный синтаксис -->
<data android:pathAdvancedPattern="/product/[0-9]+" />
```

---

## 3. PendingIntent: Binder capability token

### 3.1 ЧТО: PendingIntent — это токен для отложенного действия

```
+------------------------------------------------------------------+
|                    PENDINGINTENT = TOKEN                          |
|                                                                  |
|  Обычный Intent:                                                 |
|  +---------+   startActivity(intent)   +--------------+          |
|  | App A   | --------------------------->| Activity B   |          |
|  | (sender)|                            | (receiver)   |          |
|  +---------+                            +--------------+          |
|  App A выполняет действие СЕЙЧАС, от своего имени                |
|                                                                  |
|  PendingIntent:                                                  |
|  +---------+   create PendingIntent   +---------------+          |
|  | App A   | ------------------------>| System Server |          |
|  | (creator)|  (хранит token)          | (holds token) |          |
|  +----+----+                           +-------+-------+          |
|       | передаёт token                         |                 |
|       v                                        |                 |
|  +---------+   send PendingIntent     +--------v------+          |
|  | App B   | ------------------------>| System Server |          |
|  | (sender)|  (использует token)       | выполняет от  |          |
|  +---------+                           | имени App A!  |          |
|                                        +---------------+          |
|                                                                  |
|  PendingIntent позволяет App B выполнить действие                |
|  от имени App A, с правами App A, даже если App A уже мёртв!    |
+------------------------------------------------------------------+
```

### 3.2 ПОЧЕМУ: зачем нужна делегация прав

**Сценарии, где PendingIntent необходим:**
1. **Notifications:** Система показывает уведомление. Когда пользователь нажимает — нужно открыть Activity вашего приложения. Но NotificationManager — это system_server, не ваше приложение.
2. **AlarmManager:** Будильник должен сработать через 8 часов. Ваш процесс может быть убит. PendingIntent переживёт процесс.
3. **Widget:** AppWidgetHost рисует ваш виджет. При клике — нужно выполнить действие от имени вашего приложения.
4. **Geofence:** GPS-подсистема обнаруживает вход в зону. Нужно уведомить ваше приложение.
5. **MediaSession:** Система показывает media controls. При нажатии Play/Pause нужен PendingIntent.

**Четыре типа PendingIntent:**

| Метод | Целевой компонент | Типичное использование |
|-------|-------------------|------------------------|
| `PendingIntent.getActivity()` | Activity | Notification tap, widget tap |
| `PendingIntent.getService()` | Service | Background task triggering |
| `PendingIntent.getBroadcast()` | BroadcastReceiver | Alarm, Geofence, notification action |
| `PendingIntent.getForegroundService()` | Foreground Service | Long-running task (Android 8+) |

### 3.3 КАК РАБОТАЕТ: Binder token model

```
+------------------------------------------------------------------+
|           PENDINGINTENT BINDER TOKEN MODEL                       |
|                                                                  |
|  1. СОЗДАНИЕ (в вашем приложении):                               |
|     PendingIntent.getActivity(context, requestCode, intent, flags)|
|           |                                                      |
|           v (Binder IPC)                                         |
|     ActivityManagerService.getIntentSender()                     |
|           |                                                      |
|           v                                                      |
|     Создаёт PendingIntentRecord:                                 |
|     +----------------------------------------------+             |
|     |  PendingIntentRecord (в system_server):       |             |
|     |  * uid: 10042 (UID вашего приложения)         |             |
|     |  * packageName: "com.your.app"                |             |
|     |  * intent: Intent(...)                        |             |
|     |  * flags: FLAG_IMMUTABLE                      |             |
|     |  * requestCode: 0                             |             |
|     |  * key: hash(uid + package + intent + code)   |             |
|     |  * binder: IIntentSender.Stub (токен)         |             |
|     +----------------------------------------------+             |
|           |                                                      |
|           v                                                      |
|     Возвращает PendingIntent (обёртка над Binder token)          |
|                                                                  |
|  2. ПЕРЕДАЧА (другому приложению/системе):                       |
|     PendingIntent — Parcelable -> передаётся через Binder IPC   |
|     Содержит только token (IBinder), НЕ содержит Intent          |
|                                                                  |
|  3. ИСПОЛНЕНИЕ (когда получатель вызывает send()):               |
|     PendingIntent.send()                                         |
|           |                                                      |
|           v (Binder IPC через token)                             |
|     ActivityManagerService.sendIntentSender()                    |
|           |                                                      |
|           v                                                      |
|     Находит PendingIntentRecord по token                         |
|     -> Проверяет flags (IMMUTABLE -> нельзя изменить intent)     |
|     -> Выполняет intent от имени СОЗДАТЕЛЯ (uid 10042)           |
|     -> startActivity / startService / sendBroadcast              |
|                                                                  |
|  КЛЮЧЕВОЙ МОМЕНТ:                                                |
|  * Token unforgeable (защищён kernel-level Binder)               |
|  * Действие выполняется с identity СОЗДАТЕЛЯ, не ВЫЗЫВАЮЩЕГО     |
|  * PendingIntentRecord живёт в system_server                     |
|    -> переживает смерть процесса создателя                       |
+------------------------------------------------------------------+
```

**PendingIntent identity и equality:**

```
+------------------------------------------------------------------+
|          PENDINGINTENT IDENTITY (Key matching)                   |
|                                                                  |
|  Два PendingIntent считаются ОДИНАКОВЫМИ если совпадают:        |
|                                                                  |
|  1. requestCode (int)                                            |
|  2. Intent: action, data, type, identity, class, categories      |
|  3. Тип: getActivity vs getBroadcast vs getService               |
|  4. Package (создатель)                                          |
|                                                                  |
|  НЕ учитываются при сравнении:                                   |
|  * extras (Bundle)                                               |
|  * flags самого PendingIntent                                    |
|                                                                  |
|  Пример проблемы:                                                |
|  PI_1 = getActivity(ctx, 0, Intent(ctx, A.class), IMMUTABLE)    |
|  PI_2 = getActivity(ctx, 0, Intent(ctx, A.class), IMMUTABLE)    |
|  PI_1 == PI_2  // TRUE! Это ОДИН И ТОТ ЖЕ токен.               |
|                                                                  |
|  Чтобы различить:                                                |
|  PI_1 = getActivity(ctx, 1, Intent(ctx, A.class), IMMUTABLE)    |
|  PI_2 = getActivity(ctx, 2, Intent(ctx, A.class), IMMUTABLE)    |
|  PI_1 != PI_2  // Разные requestCode -> разные токены.           |
+------------------------------------------------------------------+
```

### 3.4 КАК ПРИМЕНЯТЬ: создание PendingIntent

```kotlin
// === NOTIFICATION с PendingIntent ===
fun showNotification(context: Context) {
    // Intent, который откроет Activity при нажатии на уведомление
    val intent = Intent(context, DetailActivity::class.java).apply {
        putExtra("notification_id", 42)         // Идентификатор уведомления
        flags = Intent.FLAG_ACTIVITY_NEW_TASK or // Новый Task
                Intent.FLAG_ACTIVITY_CLEAR_TASK  // Очистить Task
    }

    // FLAG_IMMUTABLE: Intent не может быть изменён получателем
    val pendingIntent = PendingIntent.getActivity(
        context,
        0,                                       // requestCode
        intent,
        PendingIntent.FLAG_IMMUTABLE or          // Неизменяемый
            PendingIntent.FLAG_UPDATE_CURRENT    // Обновить extras
    )

    val notification = NotificationCompat.Builder(context, CHANNEL_ID)
        .setContentTitle("Новое сообщение")
        .setContentText("У вас 3 непрочитанных сообщения")
        .setSmallIcon(R.drawable.ic_notification)
        .setContentIntent(pendingIntent)         // PendingIntent при нажатии
        .setAutoCancel(true)                     // Закрыть при нажатии
        .build()

    NotificationManagerCompat.from(context).notify(42, notification)
}

// === ALARM с PendingIntent ===
fun scheduleAlarm(context: Context) {
    val intent = Intent(context, AlarmReceiver::class.java).apply {
        action = "com.example.ALARM_TRIGGERED"    // Действие при срабатывании
    }

    val pendingIntent = PendingIntent.getBroadcast(
        context,
        0,                                        // requestCode
        intent,
        PendingIntent.FLAG_IMMUTABLE              // Неизменяемый
    )

    val alarmManager = context.getSystemService<AlarmManager>()
    alarmManager?.setExactAndAllowWhileIdle(
        AlarmManager.RTC_WAKEUP,
        System.currentTimeMillis() + 60_000,      // Через 1 минуту
        pendingIntent
    )
}

// === WIDGET с PendingIntent ===
fun createWidgetPendingIntent(
    context: Context,
    appWidgetId: Int
): PendingIntent {
    val intent = Intent(context, MainActivity::class.java).apply {
        putExtra(AppWidgetManager.EXTRA_APPWIDGET_ID, appWidgetId)
        // Уникализируем URI чтобы получить разные PendingIntent для разных виджетов
        data = Uri.parse("widget://$appWidgetId")
    }

    return PendingIntent.getActivity(
        context,
        appWidgetId,                              // Уникальный requestCode
        intent,
        PendingIntent.FLAG_IMMUTABLE or
            PendingIntent.FLAG_UPDATE_CURRENT
    )
}

// === MUTABLE PendingIntent (для inline reply) ===
fun createReplyAction(context: Context): NotificationCompat.Action {
    val replyIntent = Intent(context, ReplyReceiver::class.java)

    // FLAG_MUTABLE: система может добавить RemoteInput extras
    val pendingIntent = PendingIntent.getBroadcast(
        context,
        0,
        replyIntent,
        PendingIntent.FLAG_MUTABLE or            // Изменяемый (для RemoteInput)
            PendingIntent.FLAG_UPDATE_CURRENT
    )

    val remoteInput = RemoteInput.Builder("key_reply")
        .setLabel("Ответить...")                  // Подсказка для пользователя
        .build()

    return NotificationCompat.Action.Builder(
        R.drawable.ic_reply,
        "Ответить",
        pendingIntent
    ).addRemoteInput(remoteInput).build()
}

// === ОТМЕНА PendingIntent ===
fun cancelScheduledAlarm(context: Context) {
    // Создаём идентичный PendingIntent (тот же requestCode, тот же Intent)
    val intent = Intent(context, AlarmReceiver::class.java).apply {
        action = "com.example.ALARM_TRIGGERED"
    }
    val pendingIntent = PendingIntent.getBroadcast(
        context, 0, intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_NO_CREATE
        // FLAG_NO_CREATE: вернёт null, если PI не существует
    )

    if (pendingIntent != null) {
        val alarmManager = context.getSystemService<AlarmManager>()
        alarmManager?.cancel(pendingIntent)       // Отменяем alarm
        pendingIntent.cancel()                    // Удаляем сам токен
    }
}
```

### 3.5 ПОДВОДНЫЕ КАМНИ

**Android 12+ mutability crash:**

```kotlin
// --- CRASH на Android 12+ (API 31+)
val pi = PendingIntent.getActivity(context, 0, intent, 0)
// -> IllegalArgumentException: Targeting S+ requires FLAG_IMMUTABLE or FLAG_MUTABLE

// +++ Всегда указывайте mutability flag
val pi = PendingIntent.getActivity(
    context, 0, intent,
    PendingIntent.FLAG_IMMUTABLE // или FLAG_MUTABLE если нужно
)

// +++ Для совместимости с API < 23 (FLAG_IMMUTABLE добавлен в API 23):
val flags = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
} else {
    PendingIntent.FLAG_UPDATE_CURRENT
}
val pi = PendingIntent.getActivity(context, 0, intent, flags)
```

**Implicit PendingIntent — security vulnerability:**

```kotlin
// --- SECURITY RISK: Implicit Intent + Mutable PendingIntent
val intent = Intent("com.example.ACTION")
// Не указан компонент -> любое приложение может перехватить!
val pi = PendingIntent.getActivity(
    context, 0, intent,
    PendingIntent.FLAG_MUTABLE // Ещё и можно изменить!
)
// Вредоносное приложение может: перенаправить Intent,
// изменить extras, выполнить от имени вашего приложения

// +++ БЕЗОПАСНО: Explicit Intent + Immutable
val intent = Intent(context, DetailActivity::class.java)
val pi = PendingIntent.getActivity(
    context, 0, intent,
    PendingIntent.FLAG_IMMUTABLE
)
```

**FLAG_ONE_SHOT для предотвращения replay:**

```kotlin
// Одноразовый PendingIntent (нельзя использовать повторно)
val pi = PendingIntent.getActivity(
    context, 0, intent,
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_ONE_SHOT
)
// После первого использования token аннулируется
// Предотвращает replay attacks
```

**Таблица PendingIntent flags:**

| Flag | Назначение | Когда использовать |
|------|------------|-------------------|
| `FLAG_IMMUTABLE` | Intent нельзя изменить при send() | Всегда по умолчанию (Android 12+) |
| `FLAG_MUTABLE` | Intent можно изменить при send() | RemoteInput, fillIn(), navigation bubble |
| `FLAG_UPDATE_CURRENT` | Обновить extras существующего PI | Обновление notification extras |
| `FLAG_CANCEL_CURRENT` | Отменить старый PI, создать новый | Полная замена PendingIntent |
| `FLAG_NO_CREATE` | Вернуть null если PI не существует | Проверка существования PI |
| `FLAG_ONE_SHOT` | PI можно использовать только раз | Security-критичные операции |

---

## 4. Deep Links vs App Links

### 4.1 ЧТО: три типа deep linking

```
+------------------------------------------------------------------+
|                ТРИ ТИПА DEEP LINKING                             |
|                                                                  |
|  1. CUSTOM DEEP LINKS                                            |
|     Scheme: myapp://product/42                                   |
|     Верификация: нет                                             |
|     Disambiguation: да (может показать chooser)                  |
|     Безопасность: любое приложение может зарегистрировать        |
|                   такой же scheme                                |
|                                                                  |
|  2. WEB DEEP LINKS                                               |
|     Scheme: https://example.com/product/42                       |
|     Верификация: нет (нет autoVerify)                            |
|     Disambiguation: да (chooser: Chrome vs Your App)             |
|     Безопасность: средняя                                        |
|                                                                  |
|  3. APP LINKS (рекомендуемый!)                                   |
|     Scheme: https://example.com/product/42                       |
|     Верификация: ДА (assetlinks.json + autoVerify="true")        |
|     Disambiguation: НЕТ (открывается сразу в приложении)         |
|     Безопасность: высокая (доменная верификация)                 |
|                                                                  |
|  +----------------+--------------+--------------+--------------+ |
|  |                | Custom Deep  | Web Deep     | App Links    | |
|  |                | Links        | Links        |              | |
|  +----------------+--------------+--------------+--------------+ |
|  | Scheme         | custom://    | http(s)://   | http(s)://   | |
|  | Verification   | нет          | нет          | assetlinks   | |
|  | Chooser        | может быть   | всегда       | НЕТ          | |
|  | autoVerify     | ---          | ---          | true         | |
|  | Fallback       | crash/ignore | браузер      | браузер      | |
|  | Security       | низкая       | средняя      | высокая      | |
|  +----------------+--------------+--------------+--------------+ |
+------------------------------------------------------------------+
```

### 4.2 ПОЧЕМУ: зачем верифицировать ссылки

Без верификации (App Links) любое приложение может зарегистрировать IntentFilter на ваш домен. Пользователь увидит disambiguation dialog или, что хуже, вредоносное приложение может перехватить ссылку.

**App Links решают три проблемы:**
1. **UX:** Ссылка открывается мгновенно в приложении, без chooser
2. **Безопасность:** Только приложение с подтверждённым SHA-256 сертификатом может обрабатывать ссылки домена
3. **SEO:** Google индексирует App Links для Android Instant Apps

### 4.3 КАК РАБОТАЕТ: App Links verification

```
+------------------------------------------------------------------+
|           APP LINKS VERIFICATION PROCESS                         |
|                                                                  |
|  1. РАЗРАБОТЧИК:                                                 |
|     a) Добавляет в Manifest:                                     |
|        <intent-filter android:autoVerify="true">                 |
|            <action android:name="...VIEW" />                     |
|            <category android:name="...DEFAULT" />                |
|            <category android:name="...BROWSABLE" />              |
|            <data android:scheme="https"                          |
|                  android:host="www.example.com" />               |
|        </intent-filter>                                          |
|                                                                  |
|     b) Размещает на сервере:                                     |
|        https://www.example.com/.well-known/assetlinks.json       |
|        [{                                                        |
|          "relation": [                                           |
|            "delegate_permission/common.handle_all_urls"          |
|          ],                                                      |
|          "target": {                                             |
|            "namespace": "android_app",                           |
|            "package_name": "com.example.app",                    |
|            "sha256_cert_fingerprints": [                         |
|              "14:6D:E9:83:..."                                   |
|            ]                                                     |
|          }                                                       |
|        }]                                                        |
|                                                                  |
|  2. ВЕРИФИКАЦИЯ (при установке / обновлении):                    |
|     +-----------+  install  +----------------------+             |
|     | Play Store| --------->| IntentVerification   |             |
|     | / adb     |           | Service              |             |
|     +-----------+           +----------+-----------+             |
|                                        |                         |
|     Для КАЖДОГО host из autoVerify=true:                         |
|                                        v                         |
|     GET https://host/.well-known/assetlinks.json                 |
|                                        |                         |
|                                        v                         |
|     Проверка:                                                    |
|     [ok] package_name совпадает?                                 |
|     [ok] sha256_cert_fingerprints совпадает?                     |
|     [ok] relation содержит handle_all_urls?                      |
|                                        |                         |
|                              +---------+--------+                |
|                              |                  |                |
|                         Verified            Failed               |
|                         Ссылки ->           Ссылки ->            |
|                         приложение          браузер              |
|                                                                  |
|  Android 12+: каждый host верифицируется отдельно                |
|  Android 11-: если хотя бы один host failed -> ВСЕ failed        |
+------------------------------------------------------------------+
```

**intent:// scheme — специальный формат:**

```
+------------------------------------------------------------------+
|              INTENT:// SCHEME (Chrome)                            |
|                                                                  |
|  Формат: intent://host/path#Intent;parameters;end                |
|                                                                  |
|  Пример:                                                         |
|  intent://product/42#Intent;                                     |
|    scheme=myapp;                                                 |
|    package=com.example.app;                                      |
|    action=android.intent.action.VIEW;                            |
|    S.extra_key=value;                                            |
|  end                                                             |
|                                                                  |
|  Chrome парсит этот URI и создаёт Intent:                        |
|  Intent {                                                        |
|    action: ACTION_VIEW                                           |
|    data: myapp://product/42                                      |
|    package: com.example.app                                      |
|    extras: { "extra_key": "value" }                              |
|  }                                                               |
|                                                                  |
|  Преимущества:                                                   |
|  * Можно указать package (explicit)                              |
|  * Можно указать fallback URL (S.browser_fallback_url=...)      |
|  * Работает только в Chrome / Android Browser                    |
+------------------------------------------------------------------+
```

### 4.4 КАК ПРИМЕНЯТЬ: настройка App Links

```xml
<!-- AndroidManifest.xml -->
<activity android:name=".DeepLinkActivity"
    android:exported="true">

    <!-- App Link: верифицированный deep link -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />

        <!-- ОБА scheme обязательны для App Links -->
        <data android:scheme="http" />
        <data android:scheme="https" />
        <data android:host="www.example.com" />
        <data android:pathPrefix="/product/" />
    </intent-filter>

    <!-- Fallback: custom deep link (без верификации) -->
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="myapp"
              android:host="product" />
    </intent-filter>
</activity>
```

```json
// https://www.example.com/.well-known/assetlinks.json
[{
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
        "namespace": "android_app",
        "package_name": "com.example.app",
        "sha256_cert_fingerprints": [
            "14:6D:E9:83:C5:73:06:50:D8:EE:B9:95:2F:34:FC:64:16:A0:83:42:E6:1D:BE:A8:8A:04:96:B2:3F:CF:44:E5"
        ]
    }
}]
```

```kotlin
// Обработка App Link в Activity:
class DeepLinkActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val uri = intent.data ?: return finish()  // Нет URI -> закрываем

        when {
            uri.pathSegments.firstOrNull() == "product" -> {
                // /product/42 -> открываем товар
                val productId = uri.lastPathSegment?.toLongOrNull()
                if (productId != null) {
                    navigateToProduct(productId)
                }
            }
            uri.pathSegments.firstOrNull() == "user" -> {
                // /user/john -> открываем профиль
                val userId = uri.lastPathSegment
                navigateToUser(userId)
            }
            else -> {
                // Неизвестный path -> главный экран
                navigateToHome()
            }
        }
    }
}

// Утилита для парсинга Deep Link параметров
object DeepLinkParser {
    // Парсинг query parameters из URI
    fun parseParams(uri: Uri): Map<String, String> {
        return uri.queryParameterNames.associateWith { key ->
            uri.getQueryParameter(key).orEmpty()   // Извлекаем значение
        }
    }

    // Безопасное извлечение path segment
    fun getPathSegment(uri: Uri, index: Int): String? {
        return uri.pathSegments.getOrNull(index)   // Null если нет сегмента
    }

    // Проверка валидности deep link
    fun isValidDeepLink(uri: Uri, expectedHost: String): Boolean {
        return uri.scheme in listOf("https", "http") && // Только HTTP(S)
               uri.host == expectedHost &&               // Только наш домен
               uri.pathSegments.isNotEmpty()             // Есть путь
    }
}
```

### 4.5 ПОДВОДНЫЕ КАМНИ

**Android 12: строгая верификация**

```kotlin
// До Android 12: невалидный assetlinks.json -> chooser dialog
// Android 12+: невалидный assetlinks.json -> БРАУЗЕР (не приложение!)

// Проверка верификации (adb):
// adb shell pm get-app-links com.example.app
// -> Domain: www.example.com  Status: verified     <-- OK
// -> Domain: www.example.com  Status: none         <-- ПРОБЛЕМА!

// Ручной запуск верификации (Android 12+):
// adb shell pm verify-app-links --re-verify com.example.app
```

**Play App Signing — другой сертификат:**

```kotlin
// Если используете Play App Signing, SHA-256 fingerprint
// в assetlinks.json должен быть от App Signing Key
// (НЕ от upload certificate!)
//
// Проверьте в Play Console:
// Release -> Setup -> App signing -> SHA-256 certificate fingerprint
//
// Можно указать ОБА fingerprint (upload + signing):
// "sha256_cert_fingerprints": [
//     "AA:BB:CC:...",  // App signing key
//     "DD:EE:FF:..."   // Upload key (для debug)
// ]
```

**Custom URI scheme — регистрация:**

```kotlin
// Custom scheme: myapp://product/42
// Любое приложение может зарегистрировать "myapp://"!
// Используйте ТОЛЬКО как fallback к App Links.

// Рекомендуемый формат:
// com.example.app://path  (package-based scheme)
// Менее вероятна коллизия, но НЕ гарантирует уникальность
```

**Dynamic App Links (Android 15+):**

```json
// assetlinks.json с динамическими правилами (Android 15+):
[{
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
        "namespace": "android_app",
        "package_name": "com.example.app",
        "sha256_cert_fingerprints": ["..."]
    }
},
{
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
        "namespace": "android_app",
        "package_name": "com.example.app",
        "sha256_cert_fingerprints": ["..."]
    },
    "include": [{
        "path": {"urlPattern": "/product/.*"}
    }],
    "exclude": [{
        "path": {"urlPattern": "/product/admin/.*"}
    }]
}]
// Можно обновить маршруты БЕЗ нового релиза приложения!
```

---

## 5. Intent extras: связь с Bundle

### 5.1 ЧТО: Intent extras = Bundle

```
+------------------------------------------------------------------+
|                INTENT EXTRAS = BUNDLE                             |
|                                                                  |
|  Intent {                                                        |
|      action: "android.intent.action.VIEW"                        |
|      data: Uri                                                   |
|      categories: Set<String>                                     |
|      component: ComponentName?                                   |
|      flags: Int                                                  |
|      extras: Bundle   <-- ТОТ ЖЕ Bundle из android-bundle-parcel |
|  }                                                               |
|                                                                  |
|  Intent передаётся через Binder IPC:                             |
|  Intent -> Parcel -> Binder -> system_server -> Parcel -> Intent |
|                                                                  |
|  Ограничения Bundle действуют:                                   |
|  * 1 МБ лимит Binder буфера на процесс                          |
|  * TransactionTooLargeException при превышении                   |
|  * Все extras должны быть Serializable или Parcelable            |
|  * НЕ храните Bitmap, large lists, complex objects в extras      |
|                                                                  |
|  Рекомендация: передавайте ID, а не объекты                      |
|  [ok]  intent.putExtra("user_id", 42L)                           |
|  [bad] intent.putExtra("user", userObject) // слишком большой    |
+------------------------------------------------------------------+
```

### 5.2 ПОЧЕМУ: Bundle определяет размер и безопасность передачи

**Таблица лимитов передачи данных через Intent:**

| Тип данных | Размер | Рекомендация |
|-----------|--------|-------------|
| Примитивы (Int, Long, Boolean) | Байты | Всегда ОК |
| Строки (< 100KB) | Килобайты | ОК |
| Parcelable объекты | Килобайты | Осторожно, следить за размером |
| Bitmap | Мегабайты | НИКОГДА через Intent, используйте URI/File |
| List<Parcelable> | Зависит от размера | Передавайте ID, загружайте из БД |
| Serializable | Зависит | Медленнее Parcelable, избегать |

### 5.3 КАК ПРИМЕНЯТЬ: type-safe передача данных

```kotlin
// +++ Современный подход: companion object с factory method
class DetailActivity : AppCompatActivity() {
    companion object {
        private const val EXTRA_USER_ID = "extra_user_id"
        private const val EXTRA_SOURCE = "extra_source"

        // Фабричный метод для создания Intent
        fun createIntent(
            context: Context,
            userId: Long,
            source: String
        ): Intent {
            return Intent(context, DetailActivity::class.java).apply {
                putExtra(EXTRA_USER_ID, userId)   // ID пользователя
                putExtra(EXTRA_SOURCE, source)     // Источник перехода
            }
        }
    }

    // Ленивое извлечение extras
    private val userId by lazy {
        intent.getLongExtra(EXTRA_USER_ID, -1L)
    }
    private val source by lazy {
        intent.getStringExtra(EXTRA_SOURCE)
    }
}

// Использование:
startActivity(DetailActivity.createIntent(this, userId = 42, source = "home"))

// +++ Вариант 2: Kotlin contract с require
class DetailActivity : AppCompatActivity() {
    private val args by lazy {
        requireNotNull(
            intent.getLongExtra("user_id", -1L).takeIf { it != -1L }
        ) {
            "DetailActivity requires user_id extra"  // Сообщение об ошибке
        }
    }
}

// +++ Вариант 3: Parcelable data class (Kotlin Parcelize)
@Parcelize
data class ProductArgs(
    val productId: Long,           // ID товара
    val source: String,            // Откуда пришли
    val showReviews: Boolean       // Показывать отзывы
) : Parcelable

// Передача:
val args = ProductArgs(42L, "search", true)
val intent = Intent(this, ProductActivity::class.java).apply {
    putExtra("args", args)          // Передаём как Parcelable
}
startActivity(intent)

// Получение:
val args = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    intent.getParcelableExtra("args", ProductArgs::class.java)
} else {
    @Suppress("DEPRECATION")
    intent.getParcelableExtra("args")
}
```

---

## 6. Intent Flags: полный каталог

### 6.1 ЧТО: флаги управляют Task и Back Stack

Intent flags — это битовые маски, определяющие как Activity будет запущена, в каком Task окажется и как повлияет на Back Stack.

```
+------------------------------------------------------------------+
|          INTENT FLAGS: КАТЕГОРИИ                                 |
|                                                                  |
|  КАТЕГОРИЯ 1: LAUNCH FLAGS (управление Task/Back Stack)          |
|  * FLAG_ACTIVITY_NEW_TASK                                        |
|  * FLAG_ACTIVITY_CLEAR_TOP                                       |
|  * FLAG_ACTIVITY_SINGLE_TOP                                      |
|  * FLAG_ACTIVITY_CLEAR_TASK                                      |
|  * FLAG_ACTIVITY_NO_HISTORY                                      |
|  * FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS                            |
|  * FLAG_ACTIVITY_REORDER_TO_FRONT                                |
|  * FLAG_ACTIVITY_NEW_DOCUMENT                                    |
|  * FLAG_ACTIVITY_MULTIPLE_TASK                                   |
|                                                                  |
|  КАТЕГОРИЯ 2: PERMISSION FLAGS (доступ к данным)                 |
|  * FLAG_GRANT_READ_URI_PERMISSION                                |
|  * FLAG_GRANT_WRITE_URI_PERMISSION                               |
|  * FLAG_GRANT_PERSISTABLE_URI_PERMISSION                         |
|  * FLAG_GRANT_PREFIX_URI_PERMISSION                              |
|                                                                  |
|  КАТЕГОРИЯ 3: DELIVERY FLAGS (доставка)                          |
|  * FLAG_RECEIVER_REGISTERED_ONLY                                 |
|  * FLAG_RECEIVER_FOREGROUND                                      |
|  * FLAG_INCLUDE_STOPPED_PACKAGES                                 |
|  * FLAG_EXCLUDE_STOPPED_PACKAGES                                 |
+------------------------------------------------------------------+
```

### 6.2 КАК РАБОТАЕТ: основные launch flags

**Полная таблица launch flags:**

| Flag | Поведение | Аналогия | Типичный сценарий |
|------|-----------|----------|-------------------|
| `FLAG_ACTIVITY_NEW_TASK` | Запускает Activity в новом Task (или в существующем, если taskAffinity совпадает) | Открыть новое окно | Запуск из Service, BroadcastReceiver, не-Activity Context |
| `FLAG_ACTIVITY_CLEAR_TOP` | Если Activity уже в стеке — уничтожает все Activity над ней, доставляет Intent | Вернуться "назад" к конкретному экрану, убрав промежуточные | Кнопка "Домой" в навигации |
| `FLAG_ACTIVITY_SINGLE_TOP` | Не создаёт новый экземпляр, если Activity уже на вершине стека. Вызывает onNewIntent() | Не открывать дубликат | Notification tap, deep link |
| `FLAG_ACTIVITY_CLEAR_TASK` | Очищает весь Task перед запуском Activity (требует NEW_TASK) | Начать с чистого листа | Logout -> Login screen |
| `FLAG_ACTIVITY_NO_HISTORY` | Activity не остаётся в Back Stack после ухода | Одноразовый экран | Payment confirmation, OTP |
| `FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS` | Task не появляется в Recent Apps | Скрытый экран | Auth dialog, permission request |
| `FLAG_ACTIVITY_REORDER_TO_FRONT` | Перемещает существующий экземпляр на вершину стека | Поднять из-под стопки | Переключение между разделами |
| `FLAG_ACTIVITY_NEW_DOCUMENT` | Создаёт новый document/task в Recent Apps | Новый документ | Открытие нового чата/документа |
| `FLAG_ACTIVITY_MULTIPLE_TASK` | С NEW_TASK: всегда создаёт новый Task | Несколько окон | Multi-window сценарии |

### 6.3 КАК ПРИМЕНЯТЬ: комбинации флагов

```kotlin
// === ЗАПУСК ИЗ SERVICE (обязателен NEW_TASK) ===
val intent = Intent(this, MainActivity::class.java).apply {
    // Из не-Activity Context обязателен NEW_TASK
    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
}
startActivity(intent)

// === NOTIFICATION TAP: открыть и очистить стек ===
val intent = Intent(context, MainActivity::class.java).apply {
    // Очистить Task и открыть MainActivity как корневую
    addFlags(
        Intent.FLAG_ACTIVITY_NEW_TASK or        // Новый/существующий Task
        Intent.FLAG_ACTIVITY_CLEAR_TASK          // Очистить Task полностью
    )
}

// === DEEP LINK: не создавать дубликат ===
val intent = Intent(context, DetailActivity::class.java).apply {
    // Если DetailActivity уже на вершине — вызвать onNewIntent()
    addFlags(
        Intent.FLAG_ACTIVITY_SINGLE_TOP or       // Не дублировать
        Intent.FLAG_ACTIVITY_CLEAR_TOP           // Убрать Activity выше
    )
}

// === LOGOUT: полный сброс навигации ===
fun logout(context: Context) {
    val intent = Intent(context, LoginActivity::class.java).apply {
        addFlags(
            Intent.FLAG_ACTIVITY_NEW_TASK or      // Новый Task
            Intent.FLAG_ACTIVITY_CLEAR_TASK        // Очистить всё
        )
    }
    context.startActivity(intent)
}

// === ВРЕМЕННЫЙ ЭКРАН (не в Back Stack) ===
val intent = Intent(this, OtpVerificationActivity::class.java).apply {
    addFlags(Intent.FLAG_ACTIVITY_NO_HISTORY)    // Не сохранять в стеке
}
startActivity(intent)

// === ПРЕДОСТАВЛЕНИЕ ДОСТУПА К ФАЙЛУ ===
val intent = Intent(Intent.ACTION_VIEW).apply {
    setDataAndType(contentUri, "image/jpeg")
    // Даём временный доступ на чтение получателю
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
}
startActivity(intent)

// === СКРЫТЬ ИЗ RECENT APPS ===
val intent = Intent(this, AuthActivity::class.java).apply {
    addFlags(
        Intent.FLAG_ACTIVITY_NEW_TASK or                // Новый Task
        Intent.FLAG_ACTIVITY_EXCLUDE_FROM_RECENTS       // Не показывать в Recents
    )
}
startActivity(intent)
```

### 6.4 ПОДВОДНЫЕ КАМНИ

```kotlin
// --- ОШИБКА: CLEAR_TASK без NEW_TASK
val intent = Intent(this, MainActivity::class.java).apply {
    addFlags(Intent.FLAG_ACTIVITY_CLEAR_TASK)  // Без NEW_TASK не работает!
}
// CLEAR_TASK ТРЕБУЕТ NEW_TASK, иначе flag игнорируется

// +++ ПРАВИЛЬНО:
val intent = Intent(this, MainActivity::class.java).apply {
    addFlags(
        Intent.FLAG_ACTIVITY_NEW_TASK or
        Intent.FLAG_ACTIVITY_CLEAR_TASK
    )
}

// --- ОШИБКА: NEW_TASK из Activity без понимания последствий
// Из Activity контекста NEW_TASK создаст Activity в ДРУГОМ Task
// если taskAffinity отличается!

// +++ Понимание taskAffinity:
// По умолчанию taskAffinity = packageName
// NEW_TASK ищет Task с совпадающей taskAffinity
// Если нашёл — добавляет туда, если нет — создаёт новый
```

**Таблица: CLEAR_TOP + launchMode комбинации:**

| launchMode | CLEAR_TOP | Результат |
|-----------|-----------|-----------|
| standard | да | Activity уничтожается и пересоздаётся |
| singleTop | да | Activity получает onNewIntent() |
| standard | + SINGLE_TOP | Activity получает onNewIntent() |
| singleTask | да | Activity получает onNewIntent() |

---

## 7. Chooser и ShareSheet

### 7.1 ЧТО: механизм выбора приложения

```
+------------------------------------------------------------------+
|              CHOOSER vs SHARESHEET                               |
|                                                                  |
|  CHOOSER (Intent.createChooser):                                 |
|  * Всегда показывается (даже если есть default handler)         |
|  * Пользователь выбирает из списка подходящих приложений         |
|  * Можно добавить заголовок                                      |
|  * Можно исключить/добавить конкретные targets                   |
|                                                                  |
|  SHARESHEET (Android 10+ Direct Share):                          |
|  * Расширенный chooser для ACTION_SEND                           |
|  * Показывает конкретных людей/чатов из приложений              |
|  * ChooserTargetService (deprecated) -> ShortcutManager          |
|  * Системная ShareSheet с preview контента                       |
|                                                                  |
|  Путь через систему:                                             |
|  createChooser(intent, title)                                    |
|    |                                                             |
|    v                                                             |
|  Создаёт Intent с ACTION_CHOOSER:                                |
|    action = ACTION_CHOOSER                                       |
|    extra[EXTRA_INTENT] = original intent                         |
|    extra[EXTRA_TITLE] = title                                    |
|    |                                                             |
|    v                                                             |
|  System UI: ResolverActivity / ShareSheet                        |
|    |                                                             |
|    v                                                             |
|  queryIntentActivities(originalIntent)                           |
|    |                                                             |
|    v                                                             |
|  Показывает список + Direct Share targets                        |
+------------------------------------------------------------------+
```

### 7.2 КАК ПРИМЕНЯТЬ: создание Chooser

```kotlin
// === БАЗОВЫЙ CHOOSER ===
val sendIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Привет! Посмотри эту ссылку: https://example.com")
    putExtra(Intent.EXTRA_SUBJECT, "Интересная статья")
}
// createChooser() гарантирует показ списка приложений
val chooser = Intent.createChooser(sendIntent, "Поделиться через")
startActivity(chooser)

// === CHOOSER С ИСКЛЮЧЕНИЯМИ (Android 10+) ===
val sendIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Текст для отправки")
}

// Исключаем определённые приложения
val excludedComponents = arrayOf(
    ComponentName("com.facebook.orca", "com.facebook.orca.ShareActivity"),
    ComponentName("com.whatsapp", "com.whatsapp.ShareActivity")
)

val chooser = Intent.createChooser(sendIntent, "Поделиться").apply {
    // Исключить конкретные компоненты
    putExtra(Intent.EXTRA_EXCLUDE_COMPONENTS, excludedComponents)
}
startActivity(chooser)

// === CHOOSER С ДОПОЛНИТЕЛЬНЫМИ INITIAL TARGETS (Android 10+) ===
val mainIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Текст")
}

// Дополнительные Intent-ы для показа в начале списка
val copyIntent = Intent(this, CopyToClipboardActivity::class.java).apply {
    putExtra(Intent.EXTRA_TEXT, "Текст")
}
val initialIntents = arrayOf(copyIntent)

val chooser = Intent.createChooser(mainIntent, "Поделиться").apply {
    putExtra(Intent.EXTRA_INITIAL_INTENTS, initialIntents)
}
startActivity(chooser)

// === SHARE SHEET С PREVIEW (Android 10+) ===
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "image/jpeg"
    putExtra(Intent.EXTRA_STREAM, imageUri)          // URI изображения
    // Metadata для preview
    clipData = ClipData.newRawUri(null, imageUri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
}
val chooser = Intent.createChooser(shareIntent, null)  // null title для ShareSheet
startActivity(chooser)

// === ОТПРАВКА НЕСКОЛЬКИХ ФАЙЛОВ ===
val shareIntent = Intent(Intent.ACTION_SEND_MULTIPLE).apply {
    type = "image/*"                                     // Тип контента
    val uris = ArrayList<Uri>().apply {
        add(imageUri1)                                   // Первое изображение
        add(imageUri2)                                   // Второе изображение
    }
    putParcelableArrayListExtra(Intent.EXTRA_STREAM, uris) // Список URI
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)        // Доступ на чтение
}
startActivity(Intent.createChooser(shareIntent, "Отправить фото"))
```

### 7.3 Direct Share Targets (ShortcutManager)

```kotlin
// Регистрация Direct Share targets через ShortcutManager
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        publishDirectShareTargets()  // Регистрируем при старте приложения
    }

    private fun publishDirectShareTargets() {
        val shortcutManager = getSystemService<ShortcutManager>() ?: return

        // Создаём shortcuts для частых контактов
        val shortcuts = listOf(
            ShortcutInfoCompat.Builder(this, "contact_1")
                .setShortLabel("Иван")                         // Имя контакта
                .setLongLabel("Иван Петров")                   // Полное имя
                .setIcon(IconCompat.createWithResource(this,
                    R.drawable.ic_person))                      // Иконка
                .setCategories(setOf("com.example.SHARE_TARGET")) // Категория
                .setIntent(Intent(this, ChatActivity::class.java).apply {
                    action = Intent.ACTION_SEND
                    putExtra("contact_id", "contact_1")
                })
                .setLongLived(true)                             // Долгоживущий shortcut
                .setPerson(
                    Person.Builder()
                        .setName("Иван Петров")                // Имя для ranking
                        .build()
                )
                .build()
        )

        // Публикуем как dynamic shortcuts
        ShortcutManagerCompat.addDynamicShortcuts(this, shortcuts)
    }
}
```

```xml
<!-- AndroidManifest.xml: share-target declaration -->
<activity android:name=".ChatActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="text/plain" />
    </intent-filter>

    <!-- Связь с shortcuts categories -->
    <meta-data
        android:name="android.service.chooser.chooser_target_service"
        android:value="androidx.sharetarget.ChooserTargetServiceCompat" />
</activity>

<!-- share_targets.xml (в res/xml/) -->
<shortcuts xmlns:android="http://schemas.android.com/apk/res/android">
    <share-target android:targetClass=".ChatActivity">
        <data android:mimeType="text/plain" />
        <category android:name="com.example.SHARE_TARGET" />
    </share-target>
</shortcuts>
```

---

## 8. Result API: ActivityResultContracts

### 8.1 ЧТО: замена onActivityResult

```
+------------------------------------------------------------------+
|          СТАРЫЙ vs НОВЫЙ ПОДХОД ПОЛУЧЕНИЯ РЕЗУЛЬТАТА             |
|                                                                  |
|  СТАРЫЙ (deprecated):                                            |
|  startActivityForResult(intent, REQUEST_CODE)                    |
|    |                                                             |
|    v                                                             |
|  override fun onActivityResult(requestCode, resultCode, data)    |
|    when(requestCode) {                                           |
|      100 -> обработка фото                                       |
|      200 -> обработка файла                                      |
|      300 -> обработка разрешения                                 |
|    }                                                             |
|  Проблемы: magic numbers, один callback на всё,                  |
|  нет type safety, fragment confusion                             |
|                                                                  |
|  НОВЫЙ (Activity Result API):                                    |
|  val launcher = registerForActivityResult(Contract) { result ->  |
|    // Type-safe callback для конкретного запроса                  |
|  }                                                               |
|  launcher.launch(input)                                          |
|  Преимущества: type safety, отдельные callbacks,                 |
|  работает в Fragment, тестируемость                              |
+------------------------------------------------------------------+
```

### 8.2 ПОЧЕМУ: преимущества Result API

| Критерий | onActivityResult | ActivityResultContracts |
|----------|-----------------|------------------------|
| Type safety | Нет (requestCode: Int) | Да (типизированный Contract) |
| Отдельные callbacks | Нет (один метод на всё) | Да (отдельный launcher) |
| Фрагменты | Баги с nested fragments | Работает корректно |
| Тестируемость | Сложно | Легко (mock Contract) |
| Compile-time checks | Нет | Да |
| Lifecycle awareness | Нет | Да (LifecycleObserver) |

### 8.3 КАК РАБОТАЕТ: внутренняя механика

```
+------------------------------------------------------------------+
|     ACTIVITY RESULT API: ВНУТРЕННЕЕ УСТРОЙСТВО                   |
|                                                                  |
|  registerForActivityResult(contract, callback)                   |
|    |                                                             |
|    v                                                             |
|  ActivityResultRegistry.register(key, contract, callback)        |
|    |  * Регистрирует callback в registry                         |
|    |  * Ключ = "activity_rq#N" (автоинкремент)                   |
|    |  * Привязывает к Lifecycle (auto-unregister)                 |
|    v                                                             |
|  Возвращает ActivityResultLauncher<I>                            |
|                                                                  |
|  launcher.launch(input)                                          |
|    |                                                             |
|    v                                                             |
|  contract.createIntent(context, input)                           |
|    |  * Contract преобразует input в Intent                      |
|    v                                                             |
|  ActivityResultRegistry.onLaunch(requestCode, contract, input)   |
|    |                                                             |
|    v                                                             |
|  startActivityForResult(intent, requestCode)  // под капотом!    |
|                                                                  |
|  ... Activity завершена ...                                      |
|                                                                  |
|  onActivityResult(requestCode, resultCode, data)  // под капотом |
|    |                                                             |
|    v                                                             |
|  ActivityResultRegistry.dispatchResult(requestCode, ...)         |
|    |                                                             |
|    v                                                             |
|  contract.parseResult(resultCode, data)                          |
|    |  * Contract преобразует resultCode+data в output             |
|    v                                                             |
|  callback.invoke(output)  // ваш типизированный callback         |
+------------------------------------------------------------------+
```

### 8.4 КАК ПРИМЕНЯТЬ: стандартные контракты

```kotlin
// === ВЫБОР ФОТО ИЗ ГАЛЕРЕИ ===
class PhotoActivity : AppCompatActivity() {

    // Регистрируем launcher (ОБЯЗАТЕЛЬНО до STARTED)
    private val pickPhoto = registerForActivityResult(
        ActivityResultContracts.PickVisualMedia()       // Контракт для выбора медиа
    ) { uri: Uri? ->
        // Callback: получаем URI выбранного фото
        if (uri != null) {
            imageView.setImageURI(uri)                 // Показываем фото
        }
    }

    fun onSelectPhotoClicked() {
        // Запускаем выбор фото
        pickPhoto.launch(
            PickVisualMediaRequest(
                ActivityResultContracts.PickVisualMedia.ImageOnly  // Только фото
            )
        )
    }
}

// === ЗАПРОС РАЗРЕШЕНИЯ ===
class LocationActivity : AppCompatActivity() {

    // Запрос одного разрешения
    private val requestPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()     // Контракт для разрешения
    ) { isGranted: Boolean ->
        if (isGranted) {
            startLocationUpdates()                     // Разрешение получено
        } else {
            showPermissionDeniedMessage()               // Отказано
        }
    }

    // Запрос нескольких разрешений
    private val requestMultiplePermissions = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions() // Контракт для нескольких
    ) { permissions: Map<String, Boolean> ->
        val fineLocation = permissions[Manifest.permission.ACCESS_FINE_LOCATION] ?: false
        val coarseLocation = permissions[Manifest.permission.ACCESS_COARSE_LOCATION] ?: false

        when {
            fineLocation -> startPreciseLocationUpdates()   // Точное местоположение
            coarseLocation -> startApproxLocationUpdates()  // Приблизительное
            else -> showPermissionDeniedMessage()           // Отказано
        }
    }

    fun onRequestLocation() {
        requestPermission.launch(
            Manifest.permission.ACCESS_FINE_LOCATION       // Запрашиваемое разрешение
        )
    }
}

// === СЪЁМКА ФОТО ===
class CameraActivity : AppCompatActivity() {

    private lateinit var photoUri: Uri                      // URI для фото

    private val takePicture = registerForActivityResult(
        ActivityResultContracts.TakePicture()               // Контракт для камеры
    ) { success: Boolean ->
        if (success) {
            // Фото сохранено по URI photoUri
            processPhoto(photoUri)
        }
    }

    fun onTakePhotoClicked() {
        // Создаём временный файл для фото
        photoUri = FileProvider.getUriForFile(
            this,
            "${packageName}.fileprovider",                  // Authority
            createImageFile()                               // Файл
        )
        takePicture.launch(photoUri)                        // Запускаем камеру
    }
}

// === ВЫБОР ФАЙЛА (GetContent) ===
class FilePickerActivity : AppCompatActivity() {

    private val pickFile = registerForActivityResult(
        ActivityResultContracts.GetContent()                // Контракт для файла
    ) { uri: Uri? ->
        uri?.let { processFile(it) }                       // Обрабатываем файл
    }

    fun onPickPdfClicked() {
        pickFile.launch("application/pdf")                  // Только PDF файлы
    }

    fun onPickAnyFileClicked() {
        pickFile.launch("*/*")                              // Любой файл
    }
}

// === ОТКРЫТИЕ ДОКУМЕНТА (OpenDocument) ===
class DocumentActivity : AppCompatActivity() {

    private val openDocument = registerForActivityResult(
        ActivityResultContracts.OpenDocument()               // SAF документ
    ) { uri: Uri? ->
        uri?.let {
            // Получаем persistable permission
            contentResolver.takePersistableUriPermission(
                it,
                Intent.FLAG_GRANT_READ_URI_PERMISSION       // Сохраняем доступ
            )
            readDocument(it)
        }
    }

    fun onOpenDocumentClicked() {
        openDocument.launch(
            arrayOf("application/pdf", "text/plain")        // Допустимые типы
        )
    }
}

// === CUSTOM CONTRACT ===
class PickColorContract : ActivityResultContract<Unit, Int?>() {

    // Создаём Intent для запуска
    override fun createIntent(context: Context, input: Unit): Intent {
        return Intent(context, ColorPickerActivity::class.java)
    }

    // Парсим результат
    override fun parseResult(resultCode: Int, intent: Intent?): Int? {
        if (resultCode != Activity.RESULT_OK) return null  // Отмена
        return intent?.getIntExtra("selected_color", -1)   // Извлекаем цвет
    }
}

// Использование custom contract:
class DesignActivity : AppCompatActivity() {
    private val pickColor = registerForActivityResult(PickColorContract()) { color ->
        color?.let { applyColor(it) }                      // Применяем цвет
    }

    fun onChangeColor() {
        pickColor.launch(Unit)                              // Запускаем выбор
    }
}
```

### 8.5 ПОДВОДНЫЕ КАМНИ

```kotlin
// --- ОШИБКА: Регистрация launcher после STARTED
class BrokenActivity : AppCompatActivity() {
    fun onButtonClicked() {
        // CRASH: LifecycleOwner is attempting to register while current state is RESUMED
        val launcher = registerForActivityResult(
            ActivityResultContracts.GetContent()
        ) { uri -> /* ... */ }
        launcher.launch("image/*")
    }
}

// +++ ПРАВИЛЬНО: Регистрация как свойство класса (до STARTED)
class CorrectActivity : AppCompatActivity() {
    // Регистрация происходит при создании экземпляра (до onCreate)
    private val pickImage = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri -> /* ... */ }

    fun onButtonClicked() {
        pickImage.launch("image/*")                         // Только launch в runtime
    }
}

// --- ОШИБКА: Потеря результата при configuration change
// Result API автоматически обрабатывает это!
// Callback вызывается ПОСЛЕ re-creation Activity.
// НО: lambda замыкает старые ссылки.

// +++ ПРАВИЛЬНО: Используйте ViewModel для хранения результата
class SafeActivity : AppCompatActivity() {
    private val viewModel: MyViewModel by viewModels()

    private val pickImage = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri ->
        uri?.let { viewModel.onImageSelected(it) }         // Сохраняем в ViewModel
    }
}
```

**Таблица стандартных контрактов:**

| Contract | Input | Output | Описание |
|----------|-------|--------|----------|
| `StartActivityForResult` | `Intent` | `ActivityResult` | Общий контракт |
| `RequestPermission` | `String` | `Boolean` | Запрос одного разрешения |
| `RequestMultiplePermissions` | `Array<String>` | `Map<String,Boolean>` | Запрос нескольких |
| `TakePicture` | `Uri` | `Boolean` | Съёмка фото |
| `TakePicturePreview` | `Void?` | `Bitmap?` | Превью фото |
| `PickVisualMedia` | `PickVisualMediaRequest` | `Uri?` | Выбор фото/видео |
| `GetContent` | `String` (mimeType) | `Uri?` | Выбор файла |
| `GetMultipleContents` | `String` | `List<Uri>` | Выбор нескольких файлов |
| `OpenDocument` | `Array<String>` | `Uri?` | Открыть документ (SAF) |
| `CreateDocument` | `String` | `Uri?` | Создать документ (SAF) |
| `OpenDocumentTree` | `Uri?` | `Uri?` | Выбрать папку (SAF) |

---

## 9. Intent Security: защита от злоупотреблений

### 9.1. Intent Spoofing и защита

```
INTENT SPOOFING — АТАКА НА ANDROID КОМПОНЕНТЫ:

СЦЕНАРИЙ АТАКИ:
┌─────────────────────────────────────────────────────────────────┐
│ 1. Злоумышленник узнаёт exported Activity в вашем приложении   │
│ 2. Создаёт Intent с поддельными данными                        │
│ 3. Отправляет Intent вашему компоненту                         │
│ 4. Ваше приложение обрабатывает поддельные данные              │
│                                                                 │
│ ПРИМЕР:                                                         │
│ PaymentActivity (exported=true, intent-filter для deep link)   │
│ Атакующий: Intent с amount=1000000, recipient="attacker"       │
│ → Ваше приложение выполняет перевод!                           │
└─────────────────────────────────────────────────────────────────┘

ЗАЩИТА:
┌─────────────────────────────────────────────────────────────────┐
│ 1. exported=false по умолчанию (Android 12+ требует явно)      │
│ 2. Signature-level permissions для sensitive компонентов        │
│ 3. Валидация ВСЕХ Intent данных                                │
│ 4. Проверка calling package для критических операций           │
└─────────────────────────────────────────────────────────────────┘
```

```kotlin
// ЗАЩИТА ACTIVITY ОТ SPOOFING

// 1. ВАЛИДАЦИЯ INTENT ДАННЫХ
class SecurePaymentActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Валидируем ВСЕ данные из Intent
        val amount = intent.getDoubleExtra("amount", -1.0)
        val recipient = intent.getStringExtra("recipient")
        val token = intent.getStringExtra("auth_token")

        // Проверяем диапазоны и формат
        if (amount < 0 || amount > MAX_PAYMENT_AMOUNT) {
            Log.w("Security", "Invalid payment amount: $amount")
            finish()
            return
        }

        if (recipient.isNullOrBlank() || !isValidRecipientId(recipient)) {
            Log.w("Security", "Invalid recipient: $recipient")
            finish()
            return
        }

        // КРИТИЧНО: Проверяем auth token на сервере!
        // Не доверяем токену из Intent без проверки
        verifyTokenOnServer(token) { isValid ->
            if (!isValid) {
                Log.w("Security", "Invalid auth token")
                finish()
                return@verifyTokenOnServer
            }
            proceedWithPayment(amount, recipient)
        }
    }

    companion object {
        private const val MAX_PAYMENT_AMOUNT = 10_000.0
    }
}

// 2. ПРОВЕРКА CALLING PACKAGE
class SensitiveDataActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Проверяем кто вызвал Activity
        val callingPackage = callingActivity?.packageName

        // Разрешаем только доверенным приложениям
        val trustedPackages = listOf(
            packageName,  // Наше приложение
            "com.mycompany.trusted_app"  // Доверенное приложение
        )

        if (callingPackage !in trustedPackages) {
            Log.w("Security", "Untrusted caller: $callingPackage")
            setResult(RESULT_CANCELED)
            finish()
            return
        }

        // Продолжаем обработку
    }
}

// 3. SIGNATURE-LEVEL PERMISSION
// В AndroidManifest.xml:
// <permission
//     android:name="com.myapp.permission.SENSITIVE_DATA"
//     android:protectionLevel="signature" />
//
// <activity
//     android:name=".SensitiveActivity"
//     android:permission="com.myapp.permission.SENSITIVE_DATA"
//     android:exported="true" />
```

### 9.2. PendingIntent Security

```kotlin
// PENDINGINTENT SECURITY (Android 12+)

/*
ПРОБЛЕМА: PendingIntent hijacking
┌─────────────────────────────────────────────────────────────────┐
│ 1. Вы создаёте mutable PendingIntent без explicit Intent       │
│ 2. Передаёте его другому приложению (например, в notification) │
│ 3. Злоумышленник перехватывает PendingIntent                   │
│ 4. Модифицирует Intent (добавляет свои extras, меняет target)  │
│ 5. Выполняет от имени вашего приложения!                       │
└─────────────────────────────────────────────────────────────────┘

ЗАЩИТА: FLAG_IMMUTABLE + explicit Intent
*/

// ❌ УЯЗВИМО (до Android 12 компилировалось)
fun createInsecurePendingIntent(): PendingIntent {
    val intent = Intent("com.myapp.ACTION")  // Implicit intent
    return PendingIntent.getBroadcast(
        context,
        0,
        intent,
        0  // ❌ Нет флага! Mutable по умолчанию на старых API
    )
}

// ✅ БЕЗОПАСНО
fun createSecurePendingIntent(): PendingIntent {
    // Explicit Intent
    val intent = Intent(context, MyReceiver::class.java).apply {
        action = "com.myapp.ACTION"
        putExtra("secure_data", "value")
    }

    return PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_IMMUTABLE  // ✅ Нельзя модифицировать
    )
}

// Когда НУЖЕН FLAG_MUTABLE (редкие случаи):
fun createMutablePendingIntent(): PendingIntent {
    // Direct Reply в notifications требует mutable PendingIntent
    val intent = Intent(context, DirectReplyReceiver::class.java)

    return PendingIntent.getBroadcast(
        context,
        0,
        intent,
        PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
    )
}
```

### 9.3. Intent Redirection Attack

```kotlin
// INTENT REDIRECTION — ОПАСНЫЙ ПАТТЕРН

/*
СЦЕНАРИЙ:
1. Activity получает Intent из недоверенного источника
2. Использует данные из Intent для создания НОВОГО Intent
3. Запускает Activity/Service с новым Intent
→ Атакующий контролирует куда и что отправляется!
*/

// ❌ УЯЗВИМО: Intent Redirection
class VulnerableActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Получаем Intent из недоверенного источника (deep link)
        val targetAction = intent.getStringExtra("target_action")
        val targetClass = intent.getStringExtra("target_class")

        // ОПАСНО: создаём Intent на основе недоверенных данных!
        val redirectIntent = Intent(targetAction).apply {
            setClassName(packageName, targetClass!!)
        }
        startActivity(redirectIntent)  // ❌ Атакующий контролирует target!
    }
}

// ✅ БЕЗОПАСНО: Whitelist allowed targets
class SecureActivity : AppCompatActivity() {

    // Whitelist разрешённых targets
    private val allowedTargets = mapOf(
        "profile" to ProfileActivity::class.java,
        "settings" to SettingsActivity::class.java,
        "help" to HelpActivity::class.java
    )

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val targetKey = intent.getStringExtra("target") ?: return

        // Проверяем по whitelist
        val targetClass = allowedTargets[targetKey]
        if (targetClass == null) {
            Log.w("Security", "Unknown target: $targetKey")
            return
        }

        // Безопасно создаём Intent
        val safeIntent = Intent(this, targetClass)
        startActivity(safeIntent)
    }
}
```

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|------------|
| "Implicit Intent всегда работает" | Если нет приложения для обработки, будет ActivityNotFoundException. Проверяйте resolveActivity() |
| "Intent extras безопасны" | Любое приложение может отправить Intent с произвольными extras. Всегда валидируйте! |
| "exported=false защищает полностью" | Root-приложения или adb могут обойти. Для sensitive данных нужна дополнительная защита |
| "PendingIntent нельзя изменить" | До Android 12 mutable PendingIntent мог быть изменён. Используйте FLAG_IMMUTABLE |
| "Deep Link = App Link" | Deep Links не верифицированы, любое приложение может зарегистрировать. App Links требуют assetlinks.json |
| "IntentFilter action достаточен для matching" | Нужно ещё совпадение category и data (если указаны). Часто забывают DEFAULT category |
| "startActivityForResult deprecated = не работает" | Работает, но deprecated. Используйте Activity Result API для type safety |
| "Intent передаётся напрямую" | Intent сериализуется в Parcel, передаётся через Binder, десериализуется. Есть лимит 1MB |
| "Можно передать любой объект через Intent" | Только Parcelable/Serializable. Для больших данных используйте ContentProvider или файлы |
| "BroadcastReceiver получает Intent мгновенно" | Broadcast проходит через system_server, есть очередь и приоритеты. Может быть задержка |

---

## CS-фундамент

| CS-концепция | Применение в Intent |
|-------------|---------------------|
| **IPC (Inter-Process Communication)** | Intent — основной механизм IPC в Android. Binder транспорт, Parcel сериализация |
| **Message Passing** | Intent как message между компонентами. Loose coupling через implicit intents |
| **URI Scheme** | Deep Links используют URI схемы для навигации. Hierarchical structure (scheme://host/path) |
| **Pattern Matching** | IntentFilter matching: regex-подобный matching для action, category, data |
| **Publish-Subscribe** | Broadcast Intents как pub-sub: отправитель не знает получателей |
| **Token-Based Authorization** | PendingIntent как token: делегация права выполнить действие от имени приложения |
| **Serialization** | Intent extras сериализуются в Parcel для передачи через Binder |
| **Capability-Based Security** | PendingIntent передаёт capability (право) другому процессу |

---

## Связь с другими темами

**[[android-app-components]]** — Intent является фундаментальным механизмом связи между всеми четырьмя типами компонентов Android: Activity, Service, BroadcastReceiver и ContentProvider. Понимание жизненного цикла компонентов и их взаимодействия через Intent — необходимая основа для работы с Intent resolution и implicit/explicit Intent. Рекомендуется начать с обзора компонентов, затем переходить к внутренней механике Intent.

**[[android-activity-lifecycle]]** — Intent непосредственно запускает Activity и определяет поведение через launch mode flags (FLAG_ACTIVITY_NEW_TASK, FLAG_ACTIVITY_SINGLE_TOP и т.д.), влияя на создание, переиспользование и расположение Activity в Task/Back Stack. Без понимания жизненного цикла Activity невозможно корректно использовать Intent flags и предсказывать поведение навигации. Изучайте lifecycle параллельно с Intent flags.

**[[android-bundle-parcelable]]** — Intent extras представляют собой Bundle, и вся передача данных между компонентами через Intent основана на механизме Parcelable/Serializable сериализации. Понимание ограничений Bundle (TransactionTooLargeException при превышении 1 МБ) и правильной реализации Parcelable критично для надёжной передачи данных. Сериализация — обязательное знание перед работой с Intent extras.

**[[android-navigation]]** — Navigation Component использует Intent под капотом для реализации deep links и навигации между feature-модулями. Deep Links и App Links, описанные в этой статье, напрямую интегрируются с Navigation graph через `<deepLink>` элемент. После изучения Intent resolution переходите к Navigation для понимания высокоуровневых абстракций.

**[[android-permissions-security]]** — Intent-based permissions и URI permissions (FLAG_GRANT_READ_URI_PERMISSION) являются ключевым механизмом безопасности при межкомпонентном взаимодействии. PendingIntent security (FLAG_IMMUTABLE requirement с Android 12) и защита от Intent Redirection vulnerability напрямую связаны с моделью безопасности Android. Изучайте параллельно для целостного понимания security модели.

**[[android-context-internals]]** — Все методы отправки Intent (startActivity, sendBroadcast, startService, bindService) являются методами Context, и их поведение зависит от типа Context (Application vs Activity). Понимание иерархии Context объясняет ограничения вроде необходимости FLAG_ACTIVITY_NEW_TASK при вызове startActivity из non-Activity Context. Рекомендуется изучить Context internals для глубокого понимания dispatch механизма Intent.

**[[android-handler-looper]]** — Доставка Intent и результатов через ActivityResultCallback происходит через Handler/Looper механизм главного потока. Понимание message queue помогает объяснить асинхронную природу Intent resolution и delivery, а также порядок доставки broadcast Intent. Изучайте Handler/Looper для понимания низкоуровневой механики доставки сообщений.

**[[android-process-memory]]** — Intent resolution проходит через system_server процесс (ActivityManagerService), и понимание межпроцессного взаимодействия через Binder объясняет ограничения на размер Intent extras и механизм PendingIntent как Binder-токена. Знание процессной модели Android помогает понять, почему PendingIntent переживает смерть создавшего его процесса.

---

## Источники и дальнейшее чтение

| Источник | Тип | Описание |
|----------|-----|----------|
| [Intents and Intent Filters — Android Developers](https://developer.android.com/guide/components/intents-filters) | Docs | Официальная документация по Intent |
| [Common Intents — Android Developers](https://developer.android.com/guide/components/intents-common) | Docs | Стандартные Intent actions и их использование |
| [App Links — Android Developers](https://developer.android.com/training/app-links) | Docs | Верификация App Links, assetlinks.json |
| [Activity Result API — Android Developers](https://developer.android.com/training/basics/intents/result) | Docs | Современный API для получения результатов |
| [PendingIntent — Android Developers](https://developer.android.com/reference/android/app/PendingIntent) | Docs | Reference документация PendingIntent |
| [Intent Resolution — AOSP](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/services/core/java/com/android/server/pm/resolution/) | Code | AOSP код IntentResolver |
| [Android Security: Intent Spoofing](https://owasp.org/www-project-mobile-security-testing-guide/) | Guide | OWASP Mobile Security Testing Guide |
| [Oversecured: Intent Redirection](https://blog.oversecured.com/Android-Access-to-app-protected-components/) | Article | Детальный разбор Intent Redirection |
| [Deep Links vs App Links — ProAndroidDev](https://proandroiddev.com/deep-links-crash-course-for-android-developers-e1a12d5d5f) | Article | Практическое сравнение Deep Links и App Links |
| [PendingIntent Security — Google Security Blog](https://security.googleblog.com/2021/10/protecting-android-users-from-malicious.html) | Article | Объяснение FLAG_IMMUTABLE requirement |

### Книги

- **Meier R.** *Professional Android* (2022) — подробное описание Intent resolution, IntentFilter matching, Deep Links и App Links с практическими примерами
- **Phillips B., Stewart C., Marsicano K.** *Android Programming: The Big Nerd Ranch Guide* (2022) — пошаговое введение в Intent, explicit/implicit Intent, Activity Result API
- **Vasavada C.** *Android Internals* (2019) — AOSP-уровневый разбор Intent dispatch через ActivityManagerService и Binder

---

*Последнее обновление: 2026-01-29*
*Эталон стиля: [[android-handler-looper]] (Gold Standard)*

---

## Проверь себя

> [!question]- Почему Intent resolution для implicit Intent проходит через PackageManager, а не через прямое обращение к компоненту?
> Implicit Intent описывает действие (что сделать), а не компонент (кто сделает). PackageManager хранит реестр всех intent-filter из манифестов установленных приложений. Он выполняет matching по action, category и data, возвращая список подходящих компонентов. Это обеспечивает loose coupling между приложениями.

> [!question]- Сценарий: PendingIntent, созданный для уведомления, открывает неправильную Activity после обновления приложения. Почему?
> PendingIntent кэшируется системой по requestCode + Intent (action, data, categories, component). Если requestCode и Intent совпадают, система возвращает старый PendingIntent с устаревшими extras. Решение: использовать FLAG_UPDATE_CURRENT для обновления extras или уникальные requestCode для каждого уведомления.


---

## Ключевые карточки

Как система разрешает implicit Intent?
?
PackageManager проверяет intent-filter всех компонентов: 1) action match, 2) category match (все категории Intent должны быть в filter), 3) data match (scheme, host, path, mimeType). Все три теста должны пройти.

Что такое PendingIntent и какие флаги бывают?
?
Token для отложенного выполнения Intent от имени приложения. Флаги: FLAG_IMMUTABLE (нельзя изменить), FLAG_MUTABLE (можно), FLAG_UPDATE_CURRENT (обновить extras), FLAG_ONE_SHOT (однократный), FLAG_CANCEL_CURRENT (отменить старый).

Чем Deep Link отличается от App Link?
?
Deep Link -- custom scheme (myapp://), показывает chooser. App Link -- https:// с autoVerify=true и Digital Asset Links на сервере, открывается напрямую без chooser.

Что такое Intent extras и как данные передаются через IPC?
?
Extras -- Bundle с key-value парами. При IPC (между процессами) Bundle сериализуется в Parcel и передается через Binder. Ограничение: ~1MB на транзакцию.

Что происходит при startActivity() под капотом?
?
Activity -> Instrumentation -> AMS (через Binder IPC) -> AMS проверяет permissions, resolves Intent -> AMS создает ActivityRecord -> AMS отправляет команду в целевой процесс -> ActivityThread создает Activity.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-navigation]] | Навигация через Intent и Navigation Component |
| Углубиться | [[android-bundle-parcelable]] | Как данные сериализуются для передачи через Intent |
| Смежная тема | [[network-http-evolution]] | Сравнение URI scheme в Android и HTTP |
| Обзор | [[android-overview]] | Вернуться к карте раздела |

