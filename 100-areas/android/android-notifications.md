---
title: "Notifications: система уведомлений Android от канала до пикселя"
created: 2026-01-27
modified: 2026-01-28
type: deep-dive
area: android
confidence: high
tags:
  - android
  - notifications
  - notificationchannel
  - pendingintent
  - foreground-service
related:
  - "[[android-overview]]"
  - "[[android-service-internals]]"
  - "[[android-intent-internals]]"
  - "[[android-permissions-security]]"
  - "[[android-broadcast-internals]]"
  - "[[android-compose]]"
cs-foundations: [publish-subscribe, observer-pattern, ipc, priority-queue, token-delegation]
---

# Notifications: система уведомлений Android от канала до пикселя

> Уведомление проходит путь от NotificationManager.notify() через Binder IPC в NotificationManagerService, где проверяются permissions, channel importance и user preferences, затем через StatusBarService в SystemUI и наконец на экран. С Android 13 требуется runtime permission, с Android 12 — immutable PendingIntent, а notification trampoline запрещён. Система использует priority queue для ранжирования, rate limiting для защиты от спама, и SQLite для persistence across reboots.

---

## Зачем это нужно

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| Уведомления не показываются | Нет POST_NOTIFICATIONS permission (13+) | Silent drop, пользователь ничего не видит |
| Channel importance нельзя изменить | Channel создан с LOW, нужен HIGH | Нет heads-up, звука, вибрации |
| Crash при PendingIntent | Нет FLAG_IMMUTABLE (Android 12+) | IllegalArgumentException |
| Activity не открывается из notification | Notification trampoline restriction (12+) | Logcat warning, no-op |
| Foreground service без notification | FGS requires notification | Crash: RemoteServiceException |
| Уведомления пропадают после reboot | Нет persistence или channel deleted | Пользователь пропускает важное |
| Notification не группируются | Нет setGroup() и summary | 10+ отдельных уведомлений забивают shade |
| Custom layout сломан на разных OEM | Неправильное использование RemoteViews | Обрезанный текст, невидимые элементы |
| Direct Reply не работает | FLAG_IMMUTABLE вместо FLAG_MUTABLE | Текст ответа не попадает в Intent |
| Badge count неправильный | Нет setNumber() или wrong channel | Запутанный пользователь |

### Актуальность (2024-2025)

```
Timeline эволюции Notifications:
──────────────────────────────────────────────────────────────────────

Android 4.1 (16)  ── Rich notifications (BigTextStyle, BigPictureStyle)
         │
Android 5.0 (21)  ── Heads-up notifications, Lock screen visibility
         │
Android 7.0 (24)  ── Direct Reply, Bundled (grouped) notifications
         │
Android 8.0 (26)  ── NotificationChannel (ОБЯЗАТЕЛЬНО)
         │                    ┌─ Channel = единственный контроль
         │                    ├─ Importance per channel
         │                    └─ User can disable per channel
         │
Android 10 (29)   ── Bubbles API (conversation), MessagingStyle enhancements
         │
Android 11 (30)   ── Conversation notifications, Bubble improvements
         │
Android 12 (31)   ── PendingIntent mutability REQUIRED
         │                    ├─ Trampoline restrictions
         │                    ├─ Custom notification appearance changes
         │                    └─ Exact alarm permission affects scheduled notifs
         │
Android 13 (33)   ── POST_NOTIFICATIONS runtime permission
         │                    ├─ Notifications OFF by default (new installs)
         │                    └─ Pre-granted for upgrades (if channels exist)
         │
Android 14 (34)   ── Foreground service types with specific permissions
         │                    ├─ FGS type required in manifest AND runtime
         │                    └─ New dismissal callback
         │
Android 15 (35)   ── Notification cooldown (rate limiting UI)
                     ├─ DND modes per profile
                     └─ Rich ongoing notifications
```

**Ключевые изменения последних версий:**

- **Android 13:** `POST_NOTIFICATIONS` — без этого permission уведомления молча отбрасываются
- **Android 12:** `FLAG_IMMUTABLE` / `FLAG_MUTABLE` обязателен, trampoline запрещён
- **Android 14:** Foreground service types требуют конкретных permissions в manifest
- **Android 15:** Rate limiting для частых уведомлений, cooldown mechanism

---

## Prerequisites

| Тема | Зачем | Где изучить |
|------|-------|-------------|
| PendingIntent | Действия при тапе на notification, identity model | [[android-intent-internals]] |
| Foreground Service | FGS requires notification, service types | [[android-service-internals]] |
| Permissions | POST_NOTIFICATIONS runtime, special permissions | [[android-permissions-security]] |
| Broadcast | NotificationListenerService events, receivers | [[android-broadcast-internals]] |
| Binder IPC | Notification delivery через system_server | [[android-binder-ipc]] |
| Compose | Современные UI для notification settings | [[android-compose]] |
| Activity Lifecycle | Notification opens Activity, state restoration | [[android-activity-lifecycle]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **Notification** | Сообщение вне UI приложения, отображаемое в shade | Записка на двери офиса |
| **NotificationChannel** | Категория уведомлений с user-controlled settings | Рубрика в газете (спорт, политика) |
| **NotificationChannelGroup** | Логическая группа каналов | Раздел газеты |
| **NotificationManager** | Клиентский API (proxy для NMS) | Почтальон принимающий письма |
| **NotificationManagerService (NMS)** | Серверный сервис в system_server | Почтовое отделение — сортировка и доставка |
| **NotificationRecord** | Внутренняя запись NMS об уведомлении | Карточка в архиве почты |
| **StatusBarManagerService** | Мост между NMS и SystemUI | Курьер из почты к получателю |
| **SystemUI** | Приложение отображающее shade, status bar | Доска объявлений |
| **Importance** | Уровень важности канала (0-4) | Степень срочности: от обычного до экстренного |
| **PendingIntent** | Отложенное действие с identity приложения | Доверенность на действие от чужого имени |
| **RemoteViews** | Парцеллируемый layout для cross-process rendering | Макет записки с инструкцией как нарисовать |
| **Heads-up** | Всплывающее уведомление поверх текущего UI | Экстренное сообщение на бегущей строке |
| **NotificationCompat** | AndroidX backward-compatible builder | Универсальный конверт для любой почтовой системы |
| **NotificationListenerService** | Сервис мониторинга всех уведомлений системы | Аудитор, читающий всю почту |
| **Bubble** | Floating conversation UI (Android 10+) | Плавающий стикер на экране |
| **Snooze** | Отложить уведомление на время | Будильник с кнопкой "ещё 5 минут" |

---

## Архитектура системы уведомлений

### Полный Pipeline: от notify() до пикселя на экране

```
App Process                    system_server                           SystemUI Process
┌──────────────┐             ┌──────────────────────────────────┐    ┌──────────────────┐
│              │             │  NotificationManagerService      │    │                  │
│ Notification │   Binder    │  ┌─────────────────────────────┐ │    │  StatusBarWindow │
│ Manager      │────────────→│  │ enqueueNotificationInternal │ │    │  ┌────────────┐  │
│ .notify(     │   IPC       │  │                             │ │    │  │ Notification│  │
│   id, notif) │   (async)   │  │  1. checkCallerIsSystem     │ │    │  │ ShadeWindow │  │
│              │             │  │     OrSameApp               │ │    │  │ Controller  │  │
└──────────────┘             │  │  2. fixNotification         │ │    │  └────────────┘  │
                             │  │     (defaults, sanitize)    │ │    │        ↓          │
                             │  │  3. checkChannel            │ │    │  ┌────────────┐  │
                             │  │     (exists? blocked?)      │ │    │  │ Heads-Up   │  │
                             │  │  4. checkPermission         │ │    │  │ Manager    │  │
                             │  │     (POST_NOTIFICATIONS)    │ │    │  └────────────┘  │
                             │  │  5. Rate limit check        │ │    │        ↓          │
                             │  │     (50/sec per UID)        │ │    │  ┌────────────┐  │
                             │  │  6. Create/update           │ │    │  │ StatusBar  │  │
                             │  │     NotificationRecord      │ │    │  │ Icon       │  │
                             │  │  7. applyZenMode (DND)      │ │    │  └────────────┘  │
                             │  │  8. Rank & Sort             │ │    │        ↓          │
                             │  │  9. Signal listeners        │ │    │  ┌────────────┐  │
                             │  │ 10. buzzBeepBlink           │──────→  │ Sound /    │  │
                             │  │     (sound/vibrate/LED)     │ │    │  │ Vibrate /  │  │
                             │  └─────────────────────────────┘ │    │  │ LED        │  │
                             │           ↓                      │    │  └────────────┘  │
                             │  ┌─────────────────────────────┐ │    │                  │
                             │  │ NotificationRecord Store    │ │    │                  │
                             │  │ (in-memory + SQLite)        │ │    │                  │
                             │  └─────────────────────────────┘ │    │                  │
                             └──────────────────────────────────┘    └──────────────────┘
```

### NotificationManagerService (NMS) — подробная архитектура

```
NotificationManagerService
├── mNotificationList          // ArrayList<NotificationRecord> — все активные
├── mEnqueuedNotifications     // ArrayList<NotificationRecord> — в очереди
├── mSummaryByGroupKey         // HashMap<String, NotificationRecord>
├── mNotificationsByKey        // ArrayMap<String, NotificationRecord>
│
├── RankingHelper              // Сортировка и фильтрация
│   ├── NotificationComparator // Сравнение по importance, priority, time
│   ├── mInterceptedNotifs     // Перехваченные DND
│   └── mProxyByGroupTmp       // Группировка
│
├── NotificationChannelLogger  // Логирование изменений каналов
├── NotificationUsageStats     // Статистика: показы, dismissals, clicks
├── SnoozeHelper               // Отложенные уведомления
├── GroupHelper                 // Автоматическая группировка
│
├── NotificationAssistants     // AI-based ranking (Device Personalization Services)
│   └── NAS (NotificationAssistantService) // Может менять ranking, suggest actions
│
└── Listeners                  // Подписчики на события
    ├── ManagedServices        // NotificationListenerService instances
    └── StatusBarManagerService // → SystemUI
```

### NotificationRecord — внутреннее представление

```kotlin
// Упрощённая структура NotificationRecord (AOSP)
// frameworks/base/services/core/java/com/android/server/notification/NotificationRecord.java

class NotificationRecord {
    // Идентификация
    val sbn: StatusBarNotification    // key = pkg + tag + id + uid
    val key: String                    // "0|com.example.app|tag|42|10150"
    val groupKey: String               // для группировки

    // Канал и настройки
    val channel: NotificationChannel
    val importance: Int                // effective importance (после user override)
    val importanceExplanation: String  // почему такой importance

    // Ranking
    var rankingScore: Float            // score от NAS (NotificationAssistant)
    var isIntercepted: Boolean         // перехвачен DND?
    var suppressedVisualEffects: Int   // какие эффекты подавлены

    // Звук и вибрация
    var sound: Uri?
    var vibration: LongArray?
    var light: Light?

    // Статистика
    var stats: NotificationUsageStats.SingleNotificationStats
    var visuallyInterruptive: Boolean  // обновление визуально заметно?
    var freshnessMs: Long              // время жизни

    // Snooze
    var snoozeCriteria: ArrayList<SnoozeCriterion>?

    // Smart actions (от NotificationAssistant)
    var systemGeneratedSmartActions: ArrayList<Action>?
    var smartReplies: ArrayList<CharSequence>?
}
```

### Путь уведомления — детальная последовательность

```
  App                    INotificationManager        NMS (system_server)          SystemUI
   │                          (Binder)                     │                        │
   │ notify(id, tag, notif)     │                          │                        │
   │────────────────────────────→                          │                        │
   │                          │ enqueueNotifInternal()     │                        │
   │                          │───────────────────────────→│                        │
   │                          │                            │                        │
   │                          │    ┌───────────────────────┤                        │
   │                          │    │ 1. checkCallerIs      │                        │
   │                          │    │    SystemOrSameApp    │                        │
   │                          │    │    (UID check)        │                        │
   │                          │    │                       │                        │
   │                          │    │ 2. fixNotification    │                        │
   │                          │    │    - defaults         │                        │
   │                          │    │    - sanitize extras  │                        │
   │                          │    │    - strip large bmp  │                        │
   │                          │    │                       │                        │
   │                          │    │ 3. Channel validation │                        │
   │                          │    │    - exists?          │                        │
   │                          │    │    - user blocked?    │                        │
   │                          │    │    - app blocked?     │                        │
   │                          │    │                       │                        │
   │                          │    │ 4. Permission check   │                        │
   │                          │    │    (POST_NOTIFICATIONS│                        │
   │                          │    │     for Android 13+)  │                        │
   │                          │    │                       │                        │
   │                          │    │ 5. Rate limit         │                        │
   │                          │    │    (MAX_PACKAGE_NOTIF │                        │
   │                          │    │     = 50 per second)  │                        │
   │                          │    │                       │                        │
   │                          │    │ 6. Create/update      │                        │
   │                          │    │    NotificationRecord │                        │
   │                          │    │                       │                        │
   │                          │    │ 7. Zen Mode (DND)     │                        │
   │                          │    │    filter             │                        │
   │                          │    │                       │                        │
   │                          │    │ 8. PostNotification   │                        │
   │                          │    │    Runnable (handler) │                        │
   │                          │    │    - rankAndSort      │                        │
   │                          │    │    - buzzBeepBlink    │──────────────────────→ │
   │                          │    │    - signal listeners │    onNotificationPosted│
   │                          │    │                       │                        │
   │                          │    └───────────────────────┘                        │
   │                          │                            │                        │
   │                          │                            │   updateNotification   │
   │                          │                            │───────────────────────→│
   │                          │                            │                        │
   │                          │                            │                  ┌─────┤
   │                          │                            │                  │Build│
   │                          │                            │                  │Views│
   │                          │                            │                  │     │
   │                          │                            │                  │Show │
   │                          │                            │                  │shade│
   │                          │                            │                  │entry│
   │                          │                            │                  │     │
   │                          │                            │                  │If   │
   │                          │                            │                  │HIGH:│
   │                          │                            │                  │heads│
   │                          │                            │                  │-up  │
   │                          │                            │                  └─────┤
```

### buzzBeepBlink — решение о звуке, вибрации, LED

```
buzzBeepBlink(NotificationRecord record)
│
├── Проверка: shouldMuteNotificationLocked()
│   ├── DND active? → filter by zen rules
│   ├── User blocked channel? → mute
│   ├── App importance = NONE? → mute
│   ├── Screen on + heads-up already showing? → might skip sound
│   └── Same notification updated < 1 sec ago? → skip duplicate alert
│
├── BEEP (Sound):
│   ├── Channel has custom sound? → use it
│   ├── Else → default notification sound
│   ├── Audio attributes from channel
│   └── Play via AudioManager (STREAM_NOTIFICATION)
│
├── BUZZ (Vibration):
│   ├── Channel vibration enabled?
│   ├── Custom vibration pattern? → use it
│   ├── Else → DEFAULT_VIBRATE_PATTERN = [0, 250, 250, 250]
│   └── Vibrate via VibratorService
│
└── BLINK (LED):
    ├── Channel lights enabled?
    ├── Custom light color?
    └── Trigger via LightsService (hardware LED or AOD)
```

---

## NotificationChannel (Android 8+)

### ЧТО: определение и концепция

NotificationChannel — обязательная категория для каждого уведомления начиная с Android 8 (API 26). Канал определяет **поведение по умолчанию** (звук, вибрация, importance), но **пользователь имеет полный контроль** и может изменить любую настройку.

```
Аналогия: Каналы = рубрики в газете

  ┌─────────────── Приложение "Мессенджер" ───────────────┐
  │                                                        │
  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
  │  │ Сообщения    │  │ Группы       │  │ Обновления   │ │
  │  │ IMPORTANCE_  │  │ IMPORTANCE_  │  │ IMPORTANCE_  │ │
  │  │ HIGH         │  │ DEFAULT      │  │ LOW          │ │
  │  │              │  │              │  │              │ │
  │  │ Sound: ✅    │  │ Sound: ✅    │  │ Sound: ❌    │ │
  │  │ Vibrate: ✅  │  │ Vibrate: ✅  │  │ Vibrate: ❌  │ │
  │  │ Heads-up: ✅ │  │ Heads-up: ❌ │  │ Heads-up: ❌ │ │
  │  │ Badge: ✅    │  │ Badge: ✅    │  │ Badge: ❌    │ │
  │  └──────────────┘  └──────────────┘  └──────────────┘ │
  │                                                        │
  │        Пользователь может переопределить               │
  │        ЛЮБУЮ настройку через Settings!                 │
  └────────────────────────────────────────────────────────┘
```

### ПОЧЕМУ: проблема до NotificationChannel

До Android 8 приложения контролировали поведение уведомлений (звук, вибрацию, priority). Пользователь мог только **полностью отключить** все уведомления от приложения. Это приводило к:
- Спаму промо-уведомлениями с высоким priority
- Невозможности отключить маркетинг, сохранив важные уведомления
- Злоупотреблению heads-up уведомлениями

### Создание каналов

```kotlin
// Создать каналы ДО отправки первого уведомления
// Рекомендуется: в Application.onCreate() или при первом запуске

class App : Application() {
    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        // Проверка API level (каналы существуют только на Android 8+)
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return

        val manager = getSystemService<NotificationManager>() ?: return

        // ── Группы каналов (опционально, но улучшают UX) ──
        val groups = listOf(
            NotificationChannelGroup("messaging", "Сообщения"),
            NotificationChannelGroup("social", "Социальные"),
            NotificationChannelGroup("system", "Системные")
        )
        manager.createNotificationChannelGroups(groups)

        // ── Канал: Личные сообщения (HIGH — heads-up) ──
        val directMessages = NotificationChannel(
            "direct_messages",                        // id (неизменяемый!)
            "Личные сообщения",                       // имя (видит пользователь)
            NotificationManager.IMPORTANCE_HIGH       // heads-up notification
        ).apply {
            description = "Уведомления о новых личных сообщениях"
            group = "messaging"

            // Звук
            setSound(
                RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION),
                AudioAttributes.Builder()
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION_COMMUNICATION_INSTANT)
                    .build()
            )

            // Вибрация
            enableVibration(true)
            vibrationPattern = longArrayOf(0, 250, 250, 250)

            // LED
            enableLights(true)
            lightColor = Color.BLUE

            // Lock screen
            lockscreenVisibility = Notification.VISIBILITY_PRIVATE

            // Bubbles (Android 11+)
            setAllowBubbles(true)

            // Conversation shortcut (Android 11+)
            // conversationId задаётся при отправке, не в канале
        }

        // ── Канал: Групповые чаты (DEFAULT — звук, без heads-up) ──
        val groupChats = NotificationChannel(
            "group_chats",
            "Групповые чаты",
            NotificationManager.IMPORTANCE_DEFAULT
        ).apply {
            description = "Уведомления из групповых чатов"
            group = "messaging"
        }

        // ── Канал: Обновления (LOW — без звука) ──
        val updates = NotificationChannel(
            "updates",
            "Обновления контента",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Новые посты, рекомендации"
            group = "social"
            setShowBadge(false) // без badge на иконке
        }

        // ── Канал: Загрузки (LOW — progress) ──
        val downloads = NotificationChannel(
            "downloads",
            "Загрузки",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Прогресс загрузки файлов"
            group = "system"
        }

        // ── Канал: Foreground Service (MIN — persistent но тихий) ──
        val foregroundService = NotificationChannel(
            "foreground_service",
            "Фоновая работа",
            NotificationManager.IMPORTANCE_MIN
        ).apply {
            description = "Уведомление о фоновых процессах"
            group = "system"
        }

        // createNotificationChannel — ИДЕМПОТЕНТНЫЙ
        // Safe to call repeatedly: если канал уже есть, обновляет ТОЛЬКО name и description
        // importance, sound, vibration — НЕ обновляются (user controls)
        manager.createNotificationChannels(listOf(
            directMessages, groupChats, updates, downloads, foregroundService
        ))
    }
}
```

### Importance levels — детальная таблица

| Importance | Код | Звук | Вибрация | Heads-up | Status bar | Shade | Lock screen | Badge |
|-----------|-----|------|----------|----------|------------|-------|-------------|-------|
| NONE | 0 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| MIN | 1 | ❌ | ❌ | ❌ | ❌ | Collapsed | ❌ | ❌ |
| LOW | 2 | ❌ | ❌ | ❌ | ✅ (small) | Normal | ✅ | ✅ |
| DEFAULT | 3 | ✅ | ✅ | ❌ | ✅ | Normal | ✅ | ✅ |
| HIGH | 4 | ✅ | ✅ | ✅ | ✅ | Normal | ✅ | ✅ |

**Соответствие pre-O priority и importance:**

| Priority (pre-O) | Importance (O+) | Поведение |
|-------------------|-----------------|-----------|
| PRIORITY_MIN (-2) | IMPORTANCE_MIN | Только shade |
| PRIORITY_LOW (-1) | IMPORTANCE_LOW | Status bar, без звука |
| PRIORITY_DEFAULT (0) | IMPORTANCE_DEFAULT | Звук |
| PRIORITY_HIGH (1) | IMPORTANCE_HIGH | Heads-up |
| PRIORITY_MAX (2) | IMPORTANCE_HIGH | Heads-up |

### Жизненный цикл канала

```
createNotificationChannel()
│
├─ Канал НЕ существует?
│  └─ Создать с указанными параметрами
│     importance, sound, vibration, lights, lockscreen...
│
├─ Канал УЖЕ существует?
│  └─ Обновить ТОЛЬКО:
│     ├─ name (отображаемое имя)
│     └─ description
│     НЕ обновляется: importance, sound, vibration, lights!
│
├─ Пользователь изменил настройки?
│  └─ User settings имеют ПРИОРИТЕТ
│     Программное изменение невозможно
│
└─ deleteNotificationChannel(channelId)
   └─ Канал удалён, НО:
      ├─ Если создать канал с тем же ID — восстановит USER settings
      ├─ В Settings появится "Deleted channels (N)"
      └─ Нельзя "сбросить" канал через delete+create
```

**КРИТИЧЕСКИ ВАЖНО:** importance нельзя повысить программно после создания канала. Только понизить. Только пользователь может повысить importance через Settings.

### Миграция каналов

```kotlin
// Ситуация: нужно изменить importance существующего канала
// Решение: создать НОВЫЙ канал, удалить старый

fun migrateChannel(manager: NotificationManager) {
    // 1. Удалить старый канал
    manager.deleteNotificationChannel("messages_v1")

    // 2. Создать новый с другим ID
    val newChannel = NotificationChannel(
        "messages_v2",                        // НОВЫЙ ID!
        "Сообщения",
        NotificationManager.IMPORTANCE_HIGH   // другой importance
    )
    manager.createNotificationChannel(newChannel)

    // 3. Обновить код отправки уведомлений
    // NotificationCompat.Builder(context, "messages_v2") // новый ID

    // ВАЖНО: пользователь увидит "Deleted channels (1)" в Settings
    // Это неизбежная цена миграции
}
```

### Backup/Restore поведение каналов

```
Backup (Google Drive / device transfer):
─────────────────────────────────────────
  Channel settings → backed up
  User overrides  → backed up
  Blocked state   → backed up

Restore on new device:
──────────────────────
  Если app установлен → channels восстановлены
  User settings      → восстановлены
  "Deleted channels" → тоже восстановлены (!)

  Если app НЕ установлен → settings cached
  При установке → applied
```

---

## Построение уведомления — полный гайд

### Минимальное уведомление

```kotlin
// МИНИМУМ для Android 8+:
// 1. Channel ID
// 2. SmallIcon
// 3. ContentTitle (рекомендуется)

val notification = NotificationCompat.Builder(context, "channel_id")
    .setSmallIcon(R.drawable.ic_notification)      // ОБЯЗАТЕЛЬНО
    .setContentTitle("Заголовок")                  // рекомендуется
    .setContentText("Текст уведомления")           // рекомендуется
    .build()

// Показать (нужно проверить permission на Android 13+)
if (ActivityCompat.checkSelfPermission(
        context, Manifest.permission.POST_NOTIFICATIONS
    ) == PackageManager.PERMISSION_GRANTED
) {
    NotificationManagerCompat.from(context).notify(
        notificationId,  // int: уникальный в пределах приложения
        notification
    )
}
```

### Полный пример с объяснениями

```kotlin
val notification = NotificationCompat.Builder(context, "messages")
    // ═══════════════════════════════════════════════════
    // ОБЯЗАТЕЛЬНЫЕ параметры
    // ═══════════════════════════════════════════════════

    // SmallIcon — ОБЯЗАТЕЛЬНО
    // Отображается в status bar (24x24 dp, monochrome)
    // На Android 5+ используется как маска (alpha channel only)
    // Цвет задаётся через setColor()
    .setSmallIcon(R.drawable.ic_message)

    // ═══════════════════════════════════════════════════
    // КОНТЕНТ
    // ═══════════════════════════════════════════════════

    // Заголовок (bold)
    .setContentTitle("Алиса")

    // Текст (обрезается если длинный → используйте Style)
    .setContentText("Привет! Как дела?")

    // Подзаголовок (между title и text на некоторых OEM)
    .setSubText("Мессенджер")

    // Large icon (72x72 dp, отображается справа)
    // Обычно — аватар пользователя
    .setLargeIcon(avatarBitmap)

    // ═══════════════════════════════════════════════════
    // ДЕЙСТВИЕ ПРИ ТАПЕ
    // ═══════════════════════════════════════════════════

    .setContentIntent(
        PendingIntent.getActivity(
            context,
            0,                                        // requestCode
            Intent(context, ChatActivity::class.java).apply {
                putExtra("chat_id", chatId)
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                        Intent.FLAG_ACTIVITY_CLEAR_TOP
            },
            PendingIntent.FLAG_IMMUTABLE or           // Android 12+
            PendingIntent.FLAG_UPDATE_CURRENT          // обновить extras
        )
    )
    .setAutoCancel(true) // убрать из shade после тапа

    // ═══════════════════════════════════════════════════
    // КНОПКИ ДЕЙСТВИЙ (максимум 3)
    // ═══════════════════════════════════════════════════

    .addAction(
        NotificationCompat.Action.Builder(
            IconCompat.createWithResource(context, R.drawable.ic_reply),
            "Ответить",
            replyPendingIntent
        ).addRemoteInput(remoteInput).build()  // Direct Reply
    )
    .addAction(
        R.drawable.ic_mark_read, "Прочитано",
        markReadPendingIntent
    )
    .addAction(
        R.drawable.ic_archive, "Архив",
        archivePendingIntent
    )

    // ═══════════════════════════════════════════════════
    // РАСШИРЕННЫЙ КОНТЕНТ (Style)
    // ═══════════════════════════════════════════════════

    .setStyle(
        NotificationCompat.MessagingStyle(
            Person.Builder().setName("Я").build()
        )
        .addMessage("Привет!", timestamp,
            Person.Builder().setName("Алиса").build())
        .addMessage("Как дела?", timestamp2,
            Person.Builder().setName("Алиса").build())
    )

    // ═══════════════════════════════════════════════════
    // КАТЕГОРИЯ И ПОВЕДЕНИЕ
    // ═══════════════════════════════════════════════════

    // Категория — помогает системе (DND, ranking)
    .setCategory(NotificationCompat.CATEGORY_MESSAGE)

    // Priority — для pre-O устройств
    .setPriority(NotificationCompat.PRIORITY_HIGH)

    // Время события (не время отправки!)
    .setWhen(messageTimestamp)
    .setShowWhen(true)

    // Badge count на иконке launcher
    .setNumber(unreadCount)

    // Цвет акцента (фон иконки в shade)
    .setColor(ContextCompat.getColor(context, R.color.primary))

    // ═══════════════════════════════════════════════════
    // LOCK SCREEN
    // ═══════════════════════════════════════════════════

    // VISIBILITY_PUBLIC — полный контент на lock screen
    // VISIBILITY_PRIVATE — скрыть контент (показать generic)
    // VISIBILITY_SECRET — не показывать вообще
    .setVisibility(NotificationCompat.VISIBILITY_PRIVATE)

    // Public version (что показать на lock screen если PRIVATE)
    .setPublicVersion(
        NotificationCompat.Builder(context, "messages")
            .setSmallIcon(R.drawable.ic_message)
            .setContentTitle("Новое сообщение")
            .setContentText("Разблокируйте чтобы прочитать")
            .build()
    )

    // ═══════════════════════════════════════════════════
    // ДОПОЛНИТЕЛЬНЫЕ НАСТРОЙКИ
    // ═══════════════════════════════════════════════════

    // Ongoing — нельзя swipe to dismiss
    .setOngoing(false)

    // Only alert once — не повторять звук при обновлении
    .setOnlyAlertOnce(true)

    // Delete intent — когда пользователь swipe to dismiss
    .setDeleteIntent(deletePI)

    // Timeout — автоматически убрать через N ms
    .setTimeoutAfter(TimeUnit.MINUTES.toMillis(30))

    // Shortcut (Android 11+ conversations)
    .setShortcutId("alice_chat")

    // Full-screen intent (звонки, будильники)
    // Требует USE_FULL_SCREEN_INTENT permission
    // .setFullScreenIntent(fullScreenPI, true)

    .build()
```

### Notification ID и Tag — стратегии

```kotlin
// ═══ ID-based: по числовому идентификатору ═══
// notify(id, notification) — id уникален в пределах приложения
// Если вызвать с тем же id — ОБНОВИТ существующее

// Стратегия 1: ID = entity ID
val chatNotificationId = chatId.hashCode()
manager.notify(chatNotificationId, notification)

// Стратегия 2: ID = тип + entity
val CHAT_BASE = 1000
val ORDER_BASE = 2000
manager.notify(CHAT_BASE + chatId, chatNotification)
manager.notify(ORDER_BASE + orderId, orderNotification)


// ═══ Tag-based: для более точного контроля ═══
// notify(tag, id, notification) — уникальность = tag + id

manager.notify("chat", chatId, chatNotification)
manager.notify("order", orderId, orderNotification)

// Отмена:
manager.cancel("chat", chatId)  // только конкретное
manager.cancelAll()              // все от этого приложения
```

---

## Стили уведомлений — детальный обзор

### BigTextStyle

```kotlin
// Для длинных текстовых уведомлений
// При раскрытии показывает до 450 символов

val style = NotificationCompat.BigTextStyle()
    .bigText(
        "Привет! Как дела? Давно не виделись, может встретимся " +
        "на выходных? Я знаю отличное кафе недалеко от метро. " +
        "Можем взять с собой Бориса и Катю, давно не собирались " +
        "всей компанией. Что скажешь?"
    )
    .setBigContentTitle("Алиса")           // заменяет title в раскрытом виде
    .setSummaryText("Мессенджер")          // доп. строка внизу

builder.setStyle(style)
```

### BigPictureStyle

```kotlin
// Для уведомлений с изображением (фото, превью)
// Показывает bitmap до 450dp в ширину

val style = NotificationCompat.BigPictureStyle()
    .bigPicture(photoBitmap)               // основное изображение
    .bigLargeIcon(null as Bitmap?)         // убрать largeIcon при раскрытии
    .setBigContentTitle("Фото от Алисы")   // заменяет title
    .setSummaryText("Посмотри что я нашла!")

// ВАЖНО: bitmap не должен быть огромным (OutOfMemory)
// Рекомендация: ≤ 1MB, масштабировать до 450 x 450 dp
// Для больших изображений: загрузить через Glide/Coil → notification
```

### MessagingStyle (рекомендуется для чатов)

```kotlin
// Android 7+: специальный стиль для переписки
// Android 11+: Conversation notifications с shortcut

val me = Person.Builder()
    .setName("Я")
    .setKey("user_self")
    .build()

val alice = Person.Builder()
    .setName("Алиса")
    .setKey("user_alice")
    .setIcon(IconCompat.createWithBitmap(aliceAvatar))
    .build()

val bob = Person.Builder()
    .setName("Боб")
    .setKey("user_bob")
    .setIcon(IconCompat.createWithBitmap(bobAvatar))
    .build()

val style = NotificationCompat.MessagingStyle(me)
    .setConversationTitle("Групповой чат")  // null для 1-to-1
    .setGroupConversation(true)              // true для группы
    .addMessage("Привет всем!", timestamp1, alice)
    .addMessage("Здорово!", timestamp2, bob)
    .addMessage("Планы на вечер?", timestamp3, alice)
    .addMessage("Давайте в кино!", timestamp4, me)

builder
    .setStyle(style)
    .setShortcutId("group_chat_1")  // связь с ShortcutInfo (Android 11+)
```

### InboxStyle

```kotlin
// Для списка коротких элементов (email inbox, tasks)
// Максимум 6 строк

val style = NotificationCompat.InboxStyle()
    .addLine("Алиса: Привет!")
    .addLine("Боб: Встречаемся в 5?")
    .addLine("Карл: Ок, буду")
    .addLine("Дина: Я тоже!")
    .addLine("Евгений: Может 6?")
    .setBigContentTitle("5 новых сообщений")
    .setSummaryText("Групповой чат")
```

### MediaStyle

```kotlin
// Для медиаплееров — интеграция с MediaSession
// Показывает до 5 действий, 3 в compact view

val style = androidx.media.app.NotificationCompat.MediaStyle()
    .setMediaSession(mediaSession.sessionToken)
    .setShowActionsInCompactView(0, 1, 2) // индексы actions для compact

builder
    .setStyle(style)
    // Обычно 5 действий для медиа:
    .addAction(R.drawable.ic_prev, "Previous", prevPI)       // 0
    .addAction(R.drawable.ic_pause, "Pause", pausePI)        // 1
    .addAction(R.drawable.ic_next, "Next", nextPI)            // 2
    .addAction(R.drawable.ic_shuffle, "Shuffle", shufflePI)  // 3
    .addAction(R.drawable.ic_close, "Close", closePI)        // 4

    // На Android 13+ MediaStyle интегрируется с MediaControl
    // Показывается в Quick Settings с обложкой альбома
```

### DecoratedCustomViewStyle

```kotlin
// Custom layout сохраняя platform header (icon, title, time)
// Используется когда стандартные стили не подходят

val customView = RemoteViews(packageName, R.layout.notification_custom)
customView.setTextViewText(R.id.title, "Заголовок")
customView.setProgressBar(R.id.progress, 100, 42, false)
customView.setImageViewBitmap(R.id.image, bitmap)

val customExpandedView = RemoteViews(packageName, R.layout.notification_custom_expanded)
// ... настроить expanded view

builder
    .setStyle(NotificationCompat.DecoratedCustomViewStyle())
    .setCustomContentView(customView)             // collapsed
    .setCustomBigContentView(customExpandedView)  // expanded
```

### CallStyle (Android 12+)

```kotlin
// Специальный стиль для входящих/исходящих звонков
// Показывается с высоким приоритетом

// Входящий звонок
val callStyle = NotificationCompat.CallStyle
    .forIncomingCall(
        Person.Builder().setName("Алиса").build(),
        declinePendingIntent,
        answerPendingIntent
    )
    .setIsVideo(true) // видеозвонок

// Исходящий звонок
val outgoingStyle = NotificationCompat.CallStyle
    .forOngoingCall(
        Person.Builder().setName("Алиса").build(),
        hangUpPendingIntent
    )

// Для screening
val screeningStyle = NotificationCompat.CallStyle
    .forScreeningCall(
        Person.Builder().setName("Неизвестный").build(),
        hangUpPendingIntent,
        answerPendingIntent
    )

builder
    .setStyle(callStyle)
    .setFullScreenIntent(fullScreenPI, true) // Показать Activity для звонка
    .setCategory(NotificationCompat.CATEGORY_CALL)
    .setOngoing(true)
```

---

## PendingIntent и безопасность

### Identity model — как работает

```
PendingIntent = токен, представляющий IDENTITY приложения

┌──────────────┐    createPendingIntent()    ┌──────────────────┐
│ App          │───────────────────────────→  │ ActivityManager  │
│ (uid=10150)  │                              │ Service          │
│              │  ←─── PendingIntent token ── │                  │
│              │       (Binder token)         │ Stores:          │
└──────────────┘                              │ - Intent         │
                                              │ - uid/pid        │
      ┌──────────────┐                        │ - flags          │
      │ Other App /  │   send()               │ - requestCode   │
      │ SystemUI     │────────────────────→   │                  │
      │              │                        │ Executes as      │
      └──────────────┘                        │ ORIGINAL app     │
                                              │ (uid=10150)      │
                                              └──────────────────┘

Ключевой принцип: PendingIntent выполняется с IDENTITY создателя,
а не вызывающего. Это делегация прав.
```

### Immutability (Android 12+)

```kotlin
// ═══ FLAG_IMMUTABLE — рекомендуется по умолчанию ═══
// Никто не может изменить Intent (extras, action, component)
// Безопасно: предотвращает PendingIntent hijacking

val immutablePI = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)

// ═══ FLAG_MUTABLE — только когда НЕОБХОДИМО ═══
// Кто-то ДОЛЖЕН модифицировать Intent (система или другое приложение)

val mutablePI = PendingIntent.getActivity(
    context,
    requestCode,
    intent,
    PendingIntent.FLAG_MUTABLE
)

// ❌ БЕЗ ФЛАГА — CRASH на Android 12+ (targetSdk 31)
// PendingIntent.getActivity(context, 0, intent, 0)
// → IllegalArgumentException: must specify FLAG_IMMUTABLE or FLAG_MUTABLE
```

### Когда нужен FLAG_MUTABLE — полный список

| Сценарий | Почему MUTABLE | Безопасность |
|----------|---------------|--------------|
| **Direct Reply** | RemoteInput добавляет текст в extras | Всегда explicit intent |
| **Bubbles** | Система добавляет extras для bubble | Framework-контролируемо |
| **Inline suggestions** | AutofillService модифицирует | Framework-контролируемо |
| **CarExtender** | Android Auto добавляет extras | Framework-контролируемо |

```kotlin
// БЕЗОПАСНЫЙ mutable PendingIntent:
// ВСЕГДА используйте explicit Intent (с ComponentName)
val safeIntent = Intent(context, ReplyReceiver::class.java) // explicit!
val mutablePI = PendingIntent.getBroadcast(
    context, 0, safeIntent, PendingIntent.FLAG_MUTABLE
)

// ❌ ОПАСНО: implicit + mutable
// val unsafePI = PendingIntent.getActivity(
//     context, 0,
//     Intent("com.example.ACTION"),  // implicit!
//     PendingIntent.FLAG_MUTABLE      // кто угодно может перехватить
// )
```

### Request code matching

```kotlin
// PendingIntent идентифицируется: requestCode + Intent (action, data, component, categories)
// extras НЕ участвуют в сравнении!

// Эти два PendingIntent — ОДИНАКОВЫЕ (extras разные, но не учитываются)
val pi1 = PendingIntent.getActivity(context, 0,
    Intent(context, ChatActivity::class.java).putExtra("id", 1),
    PendingIntent.FLAG_IMMUTABLE)

val pi2 = PendingIntent.getActivity(context, 0,
    Intent(context, ChatActivity::class.java).putExtra("id", 2),
    PendingIntent.FLAG_IMMUTABLE)
// pi1 == pi2! Второй ПЕРЕЗАПИШЕТ первый!

// ✅ РЕШЕНИЕ: уникальный requestCode
val pi1 = PendingIntent.getActivity(context, 1, // requestCode = 1
    Intent(context, ChatActivity::class.java).putExtra("id", 1),
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)

val pi2 = PendingIntent.getActivity(context, 2, // requestCode = 2
    Intent(context, ChatActivity::class.java).putExtra("id", 2),
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT)
// Теперь pi1 ≠ pi2
```

### Флаги PendingIntent

| Флаг | Действие | Когда использовать |
|------|----------|-------------------|
| FLAG_UPDATE_CURRENT | Обновить extras существующего PI | Обновление notification с новыми данными |
| FLAG_CANCEL_CURRENT | Отменить старый, создать новый | Полная замена PendingIntent |
| FLAG_ONE_SHOT | Выполнить только один раз | Одноразовые действия (confirm, delete) |
| FLAG_NO_CREATE | Вернуть null если PI не существует | Проверка существования PI |
| FLAG_IMMUTABLE | Запретить модификацию | По умолчанию (безопасность) |
| FLAG_MUTABLE | Разрешить модификацию | Direct Reply, Bubbles |

---

## Notification Trampoline Restrictions (Android 12+)

### Что такое trampoline

```
Trampoline — промежуточный компонент между notification tap и целевой Activity:

До Android 12 (работало):
┌────────────┐  tap   ┌────────────────────┐  startActivity  ┌──────────┐
│ Notification│──────→│ BroadcastReceiver  │───────────────→│ Activity │
│            │       │ (logging,          │                │          │
│            │       │  analytics,        │                │          │
│            │       │  navigation logic) │                │          │
└────────────┘       └────────────────────┘                └──────────┘

Android 12+ (запрещено для targetSdk 31+):
┌────────────┐  tap   ┌────────────────────┐  ╳  startActivity
│ Notification│──────→│ BroadcastReceiver  │─── (blocked!)
│            │       │ or Service         │
└────────────┘       └────────────────────┘

Правильно (Android 12+):
┌────────────┐  tap   ┌──────────┐
│ Notification│──────→│ Activity │  (прямой PendingIntent.getActivity)
└────────────┘       └──────────┘
```

### Что запрещено и что разрешено

| Действие | Разрешено? | Примечание |
|----------|-----------|------------|
| PendingIntent → Activity | ✅ | Рекомендуемый подход |
| PendingIntent → BroadcastReceiver → startActivity | ❌ | Trampoline |
| PendingIntent → Service → startActivity | ❌ | Trampoline |
| PendingIntent → BroadcastReceiver (без Activity) | ✅ | Действие без UI |
| PendingIntent → Service (без Activity) | ✅ | Фоновая работа |
| System apps trampoline | ✅ | Только для system apps |
| targetSdk < 31 trampoline | ✅ | Но deprecated |

### Правильный подход для аналитики

```kotlin
// ✅ ПРАВИЛЬНО: прямой PendingIntent к Activity + аналитика внутри

class ChatActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Аналитика из notification extras
        if (intent.hasExtra("notification_source")) {
            val source = intent.getStringExtra("notification_source")
            val chatId = intent.getStringExtra("chat_id")
            Analytics.trackNotificationOpened(source, chatId)

            // Убрать notification из shade
            val notifId = intent.getIntExtra("notification_id", -1)
            if (notifId != -1) {
                NotificationManagerCompat.from(this).cancel(notifId)
            }
        }

        // ... normal activity logic
    }
}

// PendingIntent:
val pi = PendingIntent.getActivity(
    context, chatId.hashCode(),
    Intent(context, ChatActivity::class.java).apply {
        putExtra("notification_source", "direct_message")
        putExtra("chat_id", chatId)
        putExtra("notification_id", notifId)
        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
    },
    PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
)
```

---

## POST_NOTIFICATIONS Permission (Android 13+)

### Полная стратегия запроса

```kotlin
class MainActivity : ComponentActivity() {

    // ActivityResult launcher для permission
    private val notificationPermissionLauncher =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            if (granted) {
                // Уведомления разрешены → показать welcome notification
                showWelcomeNotification()
            } else {
                // Отказано → объяснить в UI и предложить Settings
                showNotificationDisabledBanner()
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Запрашивать в подходящий момент (не сразу при запуске!)
        // Пример: после завершения onboarding
    }

    // Вызвать когда пользователь готов (например, включил уведомления в onboarding)
    fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU) {
            // На Android 12 и ниже permission не нужен
            return
        }

        when {
            // Уже есть разрешение
            ContextCompat.checkSelfPermission(
                this, Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED -> {
                // Всё хорошо, уведомления работают
            }

            // Показать объяснение (пользователь ранее отклонил)
            shouldShowRequestPermissionRationale(
                Manifest.permission.POST_NOTIFICATIONS
            ) -> {
                showPermissionRationaleDialog()
            }

            // Первый запрос или "Don't ask again"
            else -> {
                notificationPermissionLauncher.launch(
                    Manifest.permission.POST_NOTIFICATIONS
                )
            }
        }
    }

    private fun showPermissionRationaleDialog() {
        MaterialAlertDialogBuilder(this)
            .setTitle("Уведомления")
            .setMessage(
                "Уведомления нужны чтобы вы не пропускали " +
                "важные сообщения и обновления статусов заказов."
            )
            .setPositiveButton("Разрешить") { _, _ ->
                notificationPermissionLauncher.launch(
                    Manifest.permission.POST_NOTIFICATIONS
                )
            }
            .setNegativeButton("Не сейчас", null)
            .show()
    }

    private fun showNotificationDisabledBanner() {
        // Показать banner с кнопкой "Включить в настройках"
        // При клике:
        val intent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).apply {
            putExtra(Settings.EXTRA_APP_PACKAGE, packageName)
        }
        startActivity(intent)
    }
}
```

### Ключевые правила и edge cases

| Сценарий | Поведение |
|----------|----------|
| Новая установка на Android 13+ | Notifications **OFF** по умолчанию |
| Upgrade существующего app на Android 13 | **Pre-granted** если есть хотя бы 1 channel (кроме deleted) |
| Permission denied → notify() | Уведомление **silently dropped** (без crash) |
| FGS без permission | Notification не видно в shade, но FGS **работает**. Видно в **Task Manager** |
| Exempt: media sessions | **Не требуют** POST_NOTIFICATIONS (MediaStyle) |
| Exempt: self-managing FGS calls | Phone/video calls exempt |
| Auto-reset unused apps | POST_NOTIFICATIONS **может быть отозвано** |
| Permission revoked runtime | Существующие notifications **остаются** до dismiss |
| targetSdk < 33 на Android 13 | System shows prompt **автоматически** при первом channel creation |

### Compose UI для запроса

```kotlin
@Composable
fun NotificationPermissionScreen(
    onPermissionResult: (Boolean) -> Unit
) {
    val context = LocalContext.current

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        onPermissionResult(granted)
    }

    val hasPermission = remember {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ContextCompat.checkSelfPermission(
                context, Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            true // Не нужен на старых версиях
        }
    }

    if (!hasPermission) {
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Включите уведомления",
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "Получайте мгновенные уведомления о важных событиях",
                    style = MaterialTheme.typography.bodyMedium
                )
                Spacer(modifier = Modifier.height(16.dp))
                Button(onClick = {
                    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                        permissionLauncher.launch(
                            Manifest.permission.POST_NOTIFICATIONS
                        )
                    }
                }) {
                    Text("Включить уведомления")
                }
            }
        }
    }
}
```

---

## Foreground Service Notifications

### FGS Type → Permission → Notification

```
Android 14+ требует:
1. Тип FGS в AndroidManifest.xml
2. Соответствующий permission
3. Notification с этим типом

┌───────────────────────┬────────────────────────────────────┬──────────────────┐
│ FGS Type              │ Required Permission                │ Notification     │
├───────────────────────┼────────────────────────────────────┼──────────────────┤
│ camera                │ FOREGROUND_SERVICE_CAMERA           │ Camera active    │
│ connectedDevice       │ FOREGROUND_SERVICE_CONNECTED_DEVICE│ Device connected │
│ dataSync              │ FOREGROUND_SERVICE_DATA_SYNC       │ Syncing...       │
│ health                │ FOREGROUND_SERVICE_HEALTH          │ Workout active   │
│ location              │ FOREGROUND_SERVICE_LOCATION        │ Location tracking│
│ mediaPlayback         │ FOREGROUND_SERVICE_MEDIA_PLAYBACK  │ Now playing      │
│ mediaProjection       │ FOREGROUND_SERVICE_MEDIA_PROJECTION│ Screen sharing   │
│ microphone            │ FOREGROUND_SERVICE_MICROPHONE      │ Recording        │
│ phoneCall             │ FOREGROUND_SERVICE_PHONE_CALL      │ On call          │
│ remoteMessaging       │ FOREGROUND_SERVICE_REMOTE_MESSAGING│ Messages         │
│ shortService          │ (нет)                              │ Quick task       │
│ specialUse            │ FOREGROUND_SERVICE_SPECIAL_USE     │ Custom           │
│ systemExempted        │ (только system apps)               │ System           │
└───────────────────────┴────────────────────────────────────┴──────────────────┘
```

### Полный пример FGS с notification

```kotlin
// AndroidManifest.xml:
// <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
// <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
// <service android:name=".MusicService"
//     android:foregroundServiceType="mediaPlayback" />

class MusicService : Service() {

    private lateinit var mediaSession: MediaSessionCompat

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = createMusicNotification()

        // startForeground ДОЛЖЕН быть вызван в течение 10 секунд
        // после Context.startForegroundService()
        ServiceCompat.startForeground(
            this,
            NOTIFICATION_ID,
            notification,
            // Android 14: тип ОБЯЗАТЕЛЕН и должен совпадать с manifest
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            } else {
                0
            }
        )

        return START_STICKY
    }

    private fun createMusicNotification(): Notification {
        // Канал для FGS — обычно LOW importance (persistent, тихий)
        ensureChannelExists()

        return NotificationCompat.Builder(this, "playback")
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle("Сейчас играет")
            .setContentText("Artist — Song Title")
            .setLargeIcon(albumArtBitmap)

            // MediaStyle с MediaSession
            .setStyle(
                androidx.media.app.NotificationCompat.MediaStyle()
                    .setMediaSession(mediaSession.sessionToken)
                    .setShowActionsInCompactView(0, 1, 2)
            )

            // Действия
            .addAction(R.drawable.ic_prev, "Previous", prevPI)
            .addAction(R.drawable.ic_pause, "Pause", pausePI)
            .addAction(R.drawable.ic_next, "Next", nextPI)

            // FGS notification — ongoing
            .setOngoing(true)

            // Важно для медиа: показывать в lock screen
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)

            // Категория для DND rules
            .setCategory(NotificationCompat.CATEGORY_TRANSPORT)

            // Действие при тапе — открыть плеер
            .setContentIntent(playerPI)

            .build()
    }

    private fun ensureChannelExists() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                "playback",
                "Воспроизведение",
                NotificationManager.IMPORTANCE_LOW // тихий
            ).apply {
                description = "Уведомление о воспроизведении музыки"
            }
            getSystemService<NotificationManager>()
                ?.createNotificationChannel(channel)
        }
    }

    // Обновление notification (не нужен новый startForeground)
    fun updateNotification(title: String, artist: String, albumArt: Bitmap?) {
        val notification = NotificationCompat.Builder(this, "playback")
            .setSmallIcon(R.drawable.ic_music)
            .setContentTitle(title)
            .setContentText(artist)
            .setLargeIcon(albumArt)
            .setStyle(
                androidx.media.app.NotificationCompat.MediaStyle()
                    .setMediaSession(mediaSession.sessionToken)
                    .setShowActionsInCompactView(0, 1, 2)
            )
            .addAction(R.drawable.ic_prev, "Previous", prevPI)
            .addAction(
                if (isPlaying) R.drawable.ic_pause else R.drawable.ic_play,
                if (isPlaying) "Pause" else "Play",
                playPausePI
            )
            .addAction(R.drawable.ic_next, "Next", nextPI)
            .setOngoing(isPlaying)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setCategory(NotificationCompat.CATEGORY_TRANSPORT)
            .setContentIntent(playerPI)
            .build()

        // Обновить notification без restart FGS
        NotificationManagerCompat.from(this).notify(NOTIFICATION_ID, notification)
    }

    override fun onBind(intent: Intent?): IBinder? = null

    companion object {
        const val NOTIFICATION_ID = 1
    }
}
```

### dataSync FGS — ограничения Android 15

```kotlin
// Android 15: dataSync FGS ограничен 6 часами
// После — автоматически stopForeground + onTimeout() callback

class SyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        ServiceCompat.startForeground(
            this, 1, syncNotification(),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
        )

        // Начать sync
        startSync()

        return START_NOT_STICKY
    }

    // Android 15+: вызывается когда FGS timeout (6 часов для dataSync)
    override fun onTimeout(startId: Int, fgsType: Int) {
        // ОБЯЗАТЕЛЬНО: stopSelf() или stopForeground()
        // Иначе ANR через несколько секунд!

        // Перенести оставшуюся работу в WorkManager
        WorkManager.getInstance(this).enqueue(
            OneTimeWorkRequestBuilder<SyncWorker>()
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .build()
        )

        stopSelf(startId)
    }
}
```

---

## Direct Reply — встроенный ответ

### Полная реализация

```kotlin
// ═══ 1. RemoteInput — поле ввода ═══
val remoteInput = RemoteInput.Builder("key_text_reply")
    .setLabel("Ваш ответ...")
    // Предложенные ответы (Android 7+)
    .setChoices(arrayOf("Ок", "Понял", "Скоро буду"))
    // Разрешить свободный ввод (по умолчанию true)
    .setAllowFreeFormInput(true)
    .build()

// ═══ 2. PendingIntent для обработки — MUTABLE! ═══
val replyPendingIntent = PendingIntent.getBroadcast(
    context,
    chatId.hashCode(),  // уникальный requestCode для каждого чата
    Intent(context, ReplyReceiver::class.java).apply {
        putExtra("chat_id", chatId)
        putExtra("notification_id", notificationId)
    },
    PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
    // FLAG_MUTABLE обязателен: RemoteInput модифицирует extras!
)

// ═══ 3. Action с RemoteInput ═══
val replyAction = NotificationCompat.Action.Builder(
    IconCompat.createWithResource(context, R.drawable.ic_reply),
    "Ответить",
    replyPendingIntent
)
    .addRemoteInput(remoteInput)
    .setAllowGeneratedReplies(true)  // Smart Reply suggestions
    .setSemanticAction(NotificationCompat.Action.SEMANTIC_ACTION_REPLY)
    .build()

// ═══ 4. Добавить в notification ═══
builder.addAction(replyAction)
```

### Обработка ответа

```kotlin
class ReplyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // 1. Извлечь текст ответа
        val results = RemoteInput.getResultsFromIntent(intent)
        val replyText = results?.getCharSequence("key_text_reply")?.toString()
            ?: return

        val chatId = intent.getStringExtra("chat_id") ?: return
        val notificationId = intent.getIntExtra("notification_id", -1)

        // 2. Отправить сообщение (через корутину / WorkManager)
        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Отправить на сервер
                val success = messageRepository.sendMessage(chatId, replyText)

                withContext(Dispatchers.Main) {
                    if (success) {
                        // 3a. Обновить notification с подтверждением
                        updateNotificationSuccess(context, notificationId, replyText)
                    } else {
                        // 3b. Показать ошибку
                        updateNotificationError(context, notificationId)
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    updateNotificationError(context, notificationId)
                }
            }
        }
    }

    private fun updateNotificationSuccess(
        context: Context, notificationId: Int, replyText: String
    ) {
        // ОБЯЗАТЕЛЬНО обновить notification!
        // Иначе spinner будет крутиться бесконечно
        val notification = NotificationCompat.Builder(context, "messages")
            .setSmallIcon(R.drawable.ic_message)
            .setContentText("Вы: $replyText")
            .build()

        NotificationManagerCompat.from(context).notify(notificationId, notification)
    }

    private fun updateNotificationError(context: Context, notificationId: Int) {
        val notification = NotificationCompat.Builder(context, "messages")
            .setSmallIcon(R.drawable.ic_error)
            .setContentTitle("Ошибка отправки")
            .setContentText("Нажмите чтобы повторить")
            .build()

        NotificationManagerCompat.from(context).notify(notificationId, notification)
    }
}
```

---

## Группировка уведомлений

### Автоматическая и ручная группировка

```
Группировка:

Без группы:                    С группой:
┌──────────────┐              ┌──────────────────────────┐
│ Алиса: Прив  │              │ ▼ Мессенджер (3)         │
├──────────────┤              │   ├─ Алиса: Привет!      │
│ Боб: Встреча │              │   ├─ Боб: Встречаемся    │
├──────────────┤              │   └─ Карл: Ок            │
│ Карл: Ок     │              └──────────────────────────┘
├──────────────┤
│ ... ×10      │              Автоматически (Android 7+):
│ 10 отдельных │              Если ≥4 уведомлений от одного
│ уведомлений! │              приложения → система группирует
└──────────────┘
```

### Полная реализация группировки

```kotlin
object NotificationHelper {

    private const val GROUP_MESSAGES = "com.example.GROUP_MESSAGES"
    private const val SUMMARY_ID = 0

    // Показать уведомление для сообщения
    fun showMessageNotification(
        context: Context,
        chatId: String,
        senderName: String,
        message: String,
        senderAvatar: Bitmap?
    ) {
        val manager = NotificationManagerCompat.from(context)

        // Индивидуальное уведомление
        val notification = NotificationCompat.Builder(context, "messages")
            .setSmallIcon(R.drawable.ic_message)
            .setContentTitle(senderName)
            .setContentText(message)
            .setLargeIcon(senderAvatar)
            .setContentIntent(chatPendingIntent(context, chatId))
            .setAutoCancel(true)

            // Группировка
            .setGroup(GROUP_MESSAGES)

            // Для Android 7+: sortKey определяет порядок в группе
            .setSortKey(System.currentTimeMillis().toString())

            .build()

        if (ActivityCompat.checkSelfPermission(
                context, Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) return

        manager.notify(chatId.hashCode(), notification)

        // ОБЯЗАТЕЛЬНО: summary notification для группы
        showSummaryNotification(context, manager)
    }

    private fun showSummaryNotification(
        context: Context, manager: NotificationManagerCompat
    ) {
        // Summary — агрегированное уведомление для группы
        // На Android 7+: показывается как заголовок группы
        // На Android < 7: показывается вместо индивидуальных

        val summaryNotification = NotificationCompat.Builder(context, "messages")
            .setSmallIcon(R.drawable.ic_message)
            .setContentTitle("Новые сообщения")

            // InboxStyle для summary
            .setStyle(NotificationCompat.InboxStyle()
                .setSummaryText("Мессенджер"))

            // Группировка
            .setGroup(GROUP_MESSAGES)
            .setGroupSummary(true)  // ← ЭТО summary notification!

            // Summary не должен иметь contentIntent на конкретный чат
            .setContentIntent(mainActivityPI(context))
            .setAutoCancel(true)

            // Категория
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)

            .build()

        if (ActivityCompat.checkSelfPermission(
                context, Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) return

        manager.notify(SUMMARY_ID, summaryNotification)
    }

    // Убрать все уведомления чата
    fun cancelChatNotification(context: Context, chatId: String) {
        NotificationManagerCompat.from(context).cancel(chatId.hashCode())
        // Summary обновится автоматически (если 0 в группе — исчезнет)
    }
}
```

---

## NotificationListenerService

### Мониторинг всех уведомлений системы

```kotlin
// Требует: <service android:name=".NotificationMonitor"
//     android:permission="android.permission.BIND_NOTIFICATION_LISTENER_SERVICE">
//     <intent-filter>
//         <action android:name="android.service.notification.NotificationListenerService"/>
//     </intent-filter>
// </service>

// Пользователь ДОЛЖЕН вручную включить в Settings → Notifications → Notification access

class NotificationMonitor : NotificationListenerService() {

    // Новое уведомление
    override fun onNotificationPosted(sbn: StatusBarNotification) {
        val notification = sbn.notification
        val extras = notification.extras

        val title = extras.getString(Notification.EXTRA_TITLE)
        val text = extras.getCharSequence(Notification.EXTRA_TEXT)
        val packageName = sbn.packageName
        val key = sbn.key  // уникальный ключ

        Log.d("NotifMonitor", "[$packageName] $title: $text")

        // Ранжирование
        val ranking = Ranking()
        currentRanking.getRanking(key, ranking)
        val importance = ranking.importance
        val channel = ranking.channel
    }

    // Уведомление удалено
    override fun onNotificationRemoved(
        sbn: StatusBarNotification,
        rankingMap: RankingMap,
        reason: Int
    ) {
        val reasonStr = when (reason) {
            REASON_CLICK -> "User clicked"
            REASON_CANCEL -> "User dismissed"
            REASON_CANCEL_ALL -> "User cleared all"
            REASON_APP_CANCEL -> "App cancelled"
            REASON_APP_CANCEL_ALL -> "App cancelled all"
            REASON_TIMEOUT -> "Timeout"
            REASON_CHANNEL_BANNED -> "Channel blocked"
            else -> "Other ($reason)"
        }
        Log.d("NotifMonitor", "Removed [${sbn.packageName}]: $reasonStr")
    }

    // Ранжирование изменилось
    override fun onNotificationRankingUpdate(rankingMap: RankingMap) {
        // Обновить UI если показываете список уведомлений
    }

    // Получить все активные уведомления
    fun getAllActiveNotifications(): List<StatusBarNotification> {
        return try {
            activeNotifications?.toList() ?: emptyList()
        } catch (e: SecurityException) {
            emptyList() // listener не подключён
        }
    }

    // Программно dismiss уведомление
    fun dismissNotification(key: String) {
        cancelNotification(key)
    }

    // Snooze уведомление
    fun snoozeNotification(key: String, durationMs: Long) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            snoozeNotification(key, durationMs)
        }
    }
}
```

---

## Bubbles (Android 10+)

### Conversation как плавающий bubble

```kotlin
// ═══ 1. ShortcutInfo (обязательно для conversation) ═══
val shortcutInfo = ShortcutInfoCompat.Builder(context, "chat_alice")
    .setLongLived(true)  // ОБЯЗАТЕЛЬНО для bubbles
    .setShortLabel("Алиса")
    .setIcon(IconCompat.createWithAdaptiveBitmap(aliceAvatar))
    .setIntent(Intent(context, ChatActivity::class.java).apply {
        action = Intent.ACTION_VIEW
        putExtra("chat_id", "alice")
    })
    .setPerson(
        Person.Builder()
            .setName("Алиса")
            .setKey("alice")
            .setIcon(IconCompat.createWithBitmap(aliceAvatar))
            .build()
    )
    .build()

ShortcutManagerCompat.pushDynamicShortcut(context, shortcutInfo)

// ═══ 2. BubbleMetadata ═══
val bubbleMetadata = NotificationCompat.BubbleMetadata.Builder(
    PendingIntent.getActivity(
        context, 0,
        Intent(context, BubbleChatActivity::class.java).apply {
            putExtra("chat_id", "alice")
        },
        PendingIntent.FLAG_MUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
    ),
    IconCompat.createWithAdaptiveBitmap(aliceAvatar)
)
    .setDesiredHeight(600) // dp
    .setAutoExpandBubble(false)
    .setSuppressNotification(false) // показать и notification, и bubble
    .build()

// ═══ 3. Notification с bubble ═══
val notification = NotificationCompat.Builder(context, "messages")
    .setSmallIcon(R.drawable.ic_message)
    .setContentTitle("Алиса")
    .setContentText("Привет!")
    .setStyle(
        NotificationCompat.MessagingStyle(me)
            .addMessage("Привет!", timestamp, alicePerson)
    )
    .setShortcutId("chat_alice")       // связь с ShortcutInfo
    .setBubbleMetadata(bubbleMetadata) // bubble!
    .setCategory(NotificationCompat.CATEGORY_MESSAGE)
    .build()

// BubbleChatActivity ДОЛЖНА быть:
// - resizable (android:resizeableActivity="true")
// - embedded (allowEmbedded="true")
// - <activity android:documentLaunchMode="always" />
```

---

## Progress Notifications

### Determinate и indeterminate progress

```kotlin
// ═══ Determinate progress (известный прогресс) ═══
class DownloadNotificationHelper(private val context: Context) {

    private val manager = NotificationManagerCompat.from(context)
    private val builder = NotificationCompat.Builder(context, "downloads")
        .setSmallIcon(R.drawable.ic_download)
        .setContentTitle("Загрузка файла")
        .setOngoing(true)               // нельзя swipe
        .setOnlyAlertOnce(true)         // звук только один раз
        .setCategory(NotificationCompat.CATEGORY_PROGRESS)

    // Начало загрузки
    fun showProgress(notifId: Int) {
        builder
            .setContentText("Подготовка...")
            .setProgress(100, 0, true)  // indeterminate

        notifyIfPermitted(notifId)
    }

    // Обновление прогресса
    fun updateProgress(notifId: Int, progress: Int, total: Int) {
        val percent = (progress * 100 / total)
        val downloaded = formatBytes(progress.toLong())
        val totalStr = formatBytes(total.toLong())

        builder
            .setContentText("$downloaded / $totalStr ($percent%)")
            .setProgress(100, percent, false) // determinate

            // Действие: отмена
            .clearActions()
            .addAction(
                R.drawable.ic_cancel, "Отмена",
                cancelDownloadPI(notifId)
            )

        notifyIfPermitted(notifId)
    }

    // Завершение
    fun showComplete(notifId: Int, fileName: String) {
        builder
            .setContentTitle("Загрузка завершена")
            .setContentText(fileName)
            .setProgress(0, 0, false)    // убрать progress bar
            .setOngoing(false)            // можно swipe
            .clearActions()
            .setAutoCancel(true)
            .setContentIntent(openFilePI(fileName))

        notifyIfPermitted(notifId)
    }

    // Ошибка
    fun showError(notifId: Int, error: String) {
        builder
            .setContentTitle("Ошибка загрузки")
            .setContentText(error)
            .setProgress(0, 0, false)
            .setOngoing(false)
            .clearActions()
            .addAction(
                R.drawable.ic_retry, "Повторить",
                retryDownloadPI(notifId)
            )

        notifyIfPermitted(notifId)
    }

    private fun notifyIfPermitted(notifId: Int) {
        if (ActivityCompat.checkSelfPermission(
                context, Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
        ) {
            manager.notify(notifId, builder.build())
        }
    }
}

// ═══ Использование с WorkManager ═══
class DownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val url = inputData.getString("url") ?: return Result.failure()
        val helper = DownloadNotificationHelper(applicationContext)
        val notifId = url.hashCode()

        // Установить как FGS worker
        setForeground(
            ForegroundInfo(notifId, createInitialNotification())
        )

        return try {
            downloadFile(url) { progress, total ->
                helper.updateProgress(notifId, progress, total)
            }
            helper.showComplete(notifId, extractFileName(url))
            Result.success()
        } catch (e: Exception) {
            helper.showError(notifId, e.message ?: "Unknown error")
            Result.retry()
        }
    }
}
```

---

## Full-Screen Intent — звонки и будильники

```kotlin
// Full-screen intent показывает Activity поверх всего
// Используется для: входящих звонков, будильников, таймеров

// AndroidManifest.xml:
// <uses-permission android:name="android.permission.USE_FULL_SCREEN_INTENT" />
// Android 14+: это special permission, нужно проверять через
// NotificationManager.canUseFullScreenIntent()

fun showIncomingCallNotification(context: Context, callerName: String) {
    // Проверка permission (Android 14+)
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
        val nm = context.getSystemService<NotificationManager>()
        if (nm?.canUseFullScreenIntent() != true) {
            // Перенаправить пользователя в Settings
            val intent = Intent(
                Settings.ACTION_MANAGE_APP_USE_FULL_SCREEN_INTENT,
                Uri.parse("package:${context.packageName}")
            )
            context.startActivity(intent)
            return
        }
    }

    // Full-screen Activity
    val fullScreenIntent = Intent(context, IncomingCallActivity::class.java).apply {
        putExtra("caller_name", callerName)
        flags = Intent.FLAG_ACTIVITY_NEW_TASK or
                Intent.FLAG_ACTIVITY_NO_USER_ACTION
    }
    val fullScreenPI = PendingIntent.getActivity(
        context, 0, fullScreenIntent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
    )

    val notification = NotificationCompat.Builder(context, "calls")
        .setSmallIcon(R.drawable.ic_call)
        .setContentTitle("Входящий звонок")
        .setContentText(callerName)
        .setPriority(NotificationCompat.PRIORITY_MAX)
        .setCategory(NotificationCompat.CATEGORY_CALL)
        .setOngoing(true)

        // Full-screen intent
        // Если экран OFF → показывает Activity
        // Если экран ON → показывает heads-up notification
        .setFullScreenIntent(fullScreenPI, true)

        // Actions для heads-up
        .addAction(R.drawable.ic_decline, "Отклонить", declinePI)
        .addAction(R.drawable.ic_answer, "Ответить", answerPI)

        .build()

    if (ActivityCompat.checkSelfPermission(
            context, Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED
    ) {
        NotificationManagerCompat.from(context).notify(CALL_NOTIFICATION_ID, notification)
    }
}
```

---

## Do Not Disturb (DND) взаимодействие

### Как DND влияет на уведомления

```
DND Mode (Zen Mode):
───────────────────

Priority Only:
  ✅ Alarms, Media, System sounds
  ✅ Starred contacts (calls/messages)
  ✅ Repeat callers
  ✅ Reminders, Events
  ❌ Все остальные уведомления → подавлены

  Подавленные уведомления:
  ├── Не звучат и не вибрируют
  ├── Не показывают heads-up
  ├── Появляются в shade (по настройке)
  └── Badge может показываться (по настройке)

Total Silence:
  ❌ ВСЁ подавлено
  ❌ Даже alarms (!)

Alarms Only:
  ✅ Только alarms
  ❌ Всё остальное
```

### Notification categories и DND

```kotlin
// Category помогает DND определить пропускать ли уведомление

// Уведомления, которые МОГУТ пройти через DND Priority:
.setCategory(NotificationCompat.CATEGORY_ALARM)          // Будильник
.setCategory(NotificationCompat.CATEGORY_CALL)           // Входящий звонок
.setCategory(NotificationCompat.CATEGORY_MESSAGE)        // Сообщение от контакта
.setCategory(NotificationCompat.CATEGORY_REMINDER)       // Напоминание
.setCategory(NotificationCompat.CATEGORY_EVENT)          // Событие

// Уведомления, которые обычно БЛОКИРУЮТСЯ DND:
.setCategory(NotificationCompat.CATEGORY_EMAIL)           // Email
.setCategory(NotificationCompat.CATEGORY_SOCIAL)          // Социальные сети
.setCategory(NotificationCompat.CATEGORY_PROMO)           // Промо
.setCategory(NotificationCompat.CATEGORY_RECOMMENDATION)  // Рекомендации

// Для пропуска через DND (только system apps):
// Notification.FLAG_INSISTENT — повторять звук
// PRIORITY_MAX + CATEGORY_ALARM → наивысший шанс пройти
```

---

## Тестирование уведомлений

### Unit-тесты с Robolectric

```kotlin
@RunWith(RobolectricTestRunner::class)
class NotificationTest {

    @Test
    fun `notification has correct channel and content`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val manager = context.getSystemService<NotificationManager>()!!

        // Создать канал
        createChannels(context)

        // Проверить канал
        val channel = manager.getNotificationChannel("messages")
        assertNotNull(channel)
        assertEquals(NotificationManager.IMPORTANCE_HIGH, channel.importance)

        // Создать notification
        val notification = NotificationCompat.Builder(context, "messages")
            .setSmallIcon(R.drawable.ic_message)
            .setContentTitle("Test Title")
            .setContentText("Test Text")
            .build()

        // Проверить свойства
        assertEquals("Test Title",
            notification.extras.getString(Notification.EXTRA_TITLE))
        assertEquals("Test Text",
            notification.extras.getCharSequence(Notification.EXTRA_TEXT)?.toString())
    }

    @Test
    fun `notification has correct PendingIntent flags`() {
        val context = ApplicationProvider.getApplicationContext<Context>()

        // На Android 12+ PendingIntent ДОЛЖЕН иметь mutability flag
        val pi = PendingIntent.getActivity(
            context, 0,
            Intent(context, MainActivity::class.java),
            PendingIntent.FLAG_IMMUTABLE
        )

        assertNotNull(pi)
        // PendingIntent создан без crash → flags корректны
    }

    @Test
    fun `grouped notifications have summary`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val shadowManager = Shadows.shadowOf(
            context.getSystemService<NotificationManager>()
        )

        // Показать несколько grouped уведомлений
        showGroupedNotifications(context)

        // Проверить: есть summary
        val notifications = shadowManager.allNotifications
        val hasSummary = notifications.any {
            it.flags and Notification.FLAG_GROUP_SUMMARY != 0
        }
        assertTrue("Group must have summary notification", hasSummary)
    }
}
```

### Instrumented тесты

```kotlin
@RunWith(AndroidJUnit4::class)
class NotificationInstrumentedTest {

    @get:Rule
    val permissionRule = GrantPermissionRule.grant(
        Manifest.permission.POST_NOTIFICATIONS
    )

    @Test
    fun notificationIsPosted() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val manager = NotificationManagerCompat.from(context)

        // Создать и показать
        val notification = createTestNotification(context)
        manager.notify(42, notification)

        // Проверить через NotificationManager
        val nm = context.getSystemService<NotificationManager>()!!
        val active = nm.activeNotifications

        assertTrue(active.any { it.id == 42 })
    }

    @Test
    fun channelCreation() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val nm = context.getSystemService<NotificationManager>()!!

        // Создать канал
        val channel = NotificationChannel(
            "test_channel",
            "Test",
            NotificationManager.IMPORTANCE_DEFAULT
        )
        nm.createNotificationChannel(channel)

        // Проверить
        val created = nm.getNotificationChannel("test_channel")
        assertNotNull(created)
        assertEquals(NotificationManager.IMPORTANCE_DEFAULT, created!!.importance)

        // Cleanup
        nm.deleteNotificationChannel("test_channel")
    }
}
```

---

## Performance и Best Practices

### Оптимизация

```
1. Bitmap в notification:
   ├── LargeIcon: макс 256x256 dp (масштабировать!)
   ├── BigPicture: макс 450dp ширина
   ├── НЕ загружать из сети в main thread
   └── Использовать Glide/Coil → notification

2. Rate limiting:
   ├── NMS лимит: 50 notifications/sec per UID
   ├── Android 15: cooldown для частых обновлений
   ├── Рекомендация: ≤ 1 update/sec для progress
   └── Batch updates: копить и отправлять раз в секунду

3. Channel management:
   ├── Создавать в Application.onCreate()
   ├── Не создавать динамически на каждое событие
   ├── Используйте осмысленные ID (не timestamp/random)
   └── Документировать каналы для пользователя

4. PendingIntent:
   ├── Уникальный requestCode для каждого уведомления
   ├── FLAG_IMMUTABLE по умолчанию
   ├── Explicit intent для MUTABLE
   └── FLAG_UPDATE_CURRENT для обновления extras
```

### Чеклист для production

```
☐ NotificationChannel создан ДО первого notify()
☐ SmallIcon — monochrome (alpha channel), 24x24 dp
☐ PendingIntent имеет FLAG_IMMUTABLE или FLAG_MUTABLE
☐ MUTABLE → только explicit Intent
☐ POST_NOTIFICATIONS permission запрошен (Android 13+)
☐ Проверка permission перед каждым notify()
☐ FGS notification с правильным foregroundServiceType
☐ Grouped notifications имеют summary
☐ Direct Reply обновляет notification после отправки
☐ No trampoline (targetSdk 31+)
☐ Bitmap масштабирован (не OOM)
☐ setOnlyAlertOnce(true) для обновляемых notifications
☐ setAutoCancel(true) для тапаемых notifications
☐ setCategory() для DND compatibility
☐ Lock screen visibility настроена (PRIVATE для sensitive)
☐ Тестирование на Android 8, 12, 13, 14, 15
```

---

## Распространённые паттерны

### Паттерн 1: NotificationHelper (централизованный)

```kotlin
object NotificationHelper {

    // Все channel ID в одном месте
    object Channels {
        const val MESSAGES = "messages"
        const val UPDATES = "updates"
        const val DOWNLOADS = "downloads"
        const val FOREGROUND = "foreground"
    }

    // Все notification ID
    object Ids {
        const val SUMMARY = 0
        const val FGS = 1
        fun forChat(chatId: String) = chatId.hashCode().coerceAtLeast(2)
        fun forDownload(url: String) = url.hashCode().coerceAtLeast(1000)
    }

    // Инициализация каналов
    fun createChannels(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val manager = context.getSystemService<NotificationManager>() ?: return

        manager.createNotificationChannels(listOf(
            NotificationChannel(Channels.MESSAGES, "Сообщения",
                NotificationManager.IMPORTANCE_HIGH),
            NotificationChannel(Channels.UPDATES, "Обновления",
                NotificationManager.IMPORTANCE_LOW),
            NotificationChannel(Channels.DOWNLOADS, "Загрузки",
                NotificationManager.IMPORTANCE_LOW),
            NotificationChannel(Channels.FOREGROUND, "Фоновая работа",
                NotificationManager.IMPORTANCE_MIN)
        ))
    }

    // Проверка permission
    fun canPostNotifications(context: Context): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            ContextCompat.checkSelfPermission(
                context, Manifest.permission.POST_NOTIFICATIONS
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            NotificationManagerCompat.from(context).areNotificationsEnabled()
        }
    }

    // Безопасная отправка
    fun notify(context: Context, id: Int, notification: Notification) {
        if (canPostNotifications(context)) {
            NotificationManagerCompat.from(context).notify(id, notification)
        }
    }

    fun notify(context: Context, tag: String, id: Int, notification: Notification) {
        if (canPostNotifications(context)) {
            NotificationManagerCompat.from(context).notify(tag, id, notification)
        }
    }
}
```

### Паттерн 2: FCM → Notification

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        // FCM data message → построить notification вручную
        val data = remoteMessage.data

        when (data["type"]) {
            "message" -> showMessageNotification(data)
            "order_update" -> showOrderNotification(data)
            "promo" -> showPromoNotification(data)
        }
    }

    private fun showMessageNotification(data: Map<String, String>) {
        val chatId = data["chat_id"] ?: return
        val senderName = data["sender_name"] ?: return
        val text = data["text"] ?: return

        val notification = NotificationCompat.Builder(this, "messages")
            .setSmallIcon(R.drawable.ic_message)
            .setContentTitle(senderName)
            .setContentText(text)
            .setContentIntent(chatPI(chatId))
            .setAutoCancel(true)
            .setGroup("messages")
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        NotificationHelper.notify(this, chatId.hashCode(), notification)
    }
}
```

### Паттерн 3: Scheduled Notification с AlarmManager

```kotlin
// Запланировать notification
fun scheduleNotification(context: Context, delayMs: Long, title: String, text: String) {
    val intent = Intent(context, NotificationReceiver::class.java).apply {
        putExtra("title", title)
        putExtra("text", text)
    }

    val pendingIntent = PendingIntent.getBroadcast(
        context,
        System.currentTimeMillis().toInt(), // уникальный requestCode
        intent,
        PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_ONE_SHOT
    )

    val alarmManager = context.getSystemService<AlarmManager>()!!

    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        // Android 12+: нужен SCHEDULE_EXACT_ALARM permission
        if (alarmManager.canScheduleExactAlarms()) {
            alarmManager.setExactAndAllowWhileIdle(
                AlarmManager.RTC_WAKEUP,
                System.currentTimeMillis() + delayMs,
                pendingIntent
            )
        } else {
            // Fallback: inexact alarm
            alarmManager.set(
                AlarmManager.RTC_WAKEUP,
                System.currentTimeMillis() + delayMs,
                pendingIntent
            )
        }
    } else {
        alarmManager.setExactAndAllowWhileIdle(
            AlarmManager.RTC_WAKEUP,
            System.currentTimeMillis() + delayMs,
            pendingIntent
        )
    }
}

class NotificationReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val title = intent.getStringExtra("title") ?: return
        val text = intent.getStringExtra("text") ?: return

        val notification = NotificationCompat.Builder(context, "reminders")
            .setSmallIcon(R.drawable.ic_reminder)
            .setContentTitle(title)
            .setContentText(text)
            .setAutoCancel(true)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .build()

        NotificationHelper.notify(context, title.hashCode(), notification)
    }
}
```

---

## Мифы и заблуждения

| # | Миф | Реальность |
|---|-----|-----------|
| 1 | "Notification — просто Toast с кнопками" | Сложная система: IPC через Binder, NMS validation, channel management, DND filtering, ranking, persistence в SQLite, cross-process rendering через RemoteViews |
| 2 | "HIGH importance гарантирует heads-up" | Зависит от **пользовательских настроек** канала, DND mode, и даже screen state. Пользователь может понизить importance |
| 3 | "Можно программно изменить importance канала" | Нет. Можно только **понизить** (с Default до Low), но не повысить. Только пользователь через Settings может повысить |
| 4 | "POST_NOTIFICATIONS блокирует FGS" | FGS **работает** без permission. Notification просто не видно в shade — но видно в **Task Manager**. FGS не зависит от notification permission |
| 5 | "Notification trampoline запрещён полностью" | Только для targetSdk 31+ (Android 12). Старые apps с targetSdk < 31 могут использовать trampolines |
| 6 | "setContentIntent обязателен" | Технически не crash, но **lint warning** + плохой UX. Notification без intent = dead-end для пользователя |
| 7 | "Без channel на Android 8+ — crash" | Не crash, но notification **не покажется вообще**. Silent drop + logcat warning |
| 8 | "RemoteViews поддерживают любой View" | Ограниченный набор: TextView, ImageView, Button, ProgressBar, LinearLayout, FrameLayout, RelativeLayout и немногие другие |
| 9 | "notify() с тем же ID = всегда обновляет" | Обновляет только если совпадают id И tag. notify("tag", 1, n) и notify(1, n) — разные уведомления |
| 10 | "cancel() убирает уведомление мгновенно" | Асинхронно через Binder IPC. Может быть задержка, особенно при heavy load на NMS |
| 11 | "createNotificationChannel() можно вызвать один раз" | Рекомендуется вызывать при КАЖДОМ запуске (идемпотентно). Обновляет name и description, не трогает user settings |
| 12 | "Bubbles заменяют notification" | Bubbles — дополнительный UI поверх notification. Notification остаётся в shade. Можно подавить через setSuppressNotification(true) |

---

## CS-фундамент

| Концепция | Как используется | Пример |
|-----------|-----------------|--------|
| **IPC (Binder)** | App → NMS → SystemUI, три процесса | notify() → enqueueNotificationInternal() → StatusBarService |
| **Token delegation** | PendingIntent = Binder token с identity app | Notification action запускается с identity создателя PI |
| **Priority Queue** | Importance + ranking score определяют порядок | HIGH = heads-up, LOW = silent, ranking от NAS |
| **Observer pattern** | NotificationListenerService | Accessibility service, wearable companions |
| **Publish-Subscribe** | App публикует, SystemUI подписан через NMS | Разделение sender/renderer |
| **Rate limiting** | 50 notifications/sec per UID, cooldown (15) | Защита от flood |
| **Persistence** | NotificationRecord → SQLite | Уведомления выживают reboot |
| **Cross-process rendering** | RemoteViews → parcel → inflate в SystemUI | Custom notification layouts |

---

## Проверь себя

### Вопрос 1
**Q:** Вы создали канал с IMPORTANCE_LOW. Теперь хотите heads-up. Что делать?

<details>
<summary>Ответ</summary>

Программно **невозможно** повысить importance после создания канала. Варианты:
1. Создать **новый** канал с уникальным ID и IMPORTANCE_HIGH
2. Удалить старый канал (`deleteNotificationChannel`) и создать новый с тем же ID — но пользователь увидит "Deleted channels" в Settings и предыдущие user настройки восстановятся
3. Попросить пользователя изменить importance в Settings (через deep link `ACTION_CHANNEL_NOTIFICATION_SETTINGS`)
4. В новых версиях app: использовать миграцию каналов с версионным ID (`messages_v2`)
</details>

### Вопрос 2
**Q:** Почему Direct Reply требует FLAG_MUTABLE?

<details>
<summary>Ответ</summary>

RemoteInput **модифицирует** Intent extras, добавляя текст ответа пользователя через `RemoteInput.addResultsToIntent()`. С FLAG_IMMUTABLE система не может добавить результат RemoteInput в PendingIntent → `RemoteInput.getResultsFromIntent()` вернёт null → reply не работает. FLAG_MUTABLE позволяет системе модифицировать Intent extras. При этом для безопасности Intent ДОЛЖЕН быть explicit (с указанием ComponentName).
</details>

### Вопрос 3
**Q:** Приложение на Android 13 показывает уведомления после обновления, но не показывает после чистой установки. Почему?

<details>
<summary>Ответ</summary>

Android 13 ввёл POST_NOTIFICATIONS runtime permission. Правила:
- **Обновление** существующего приложения: permission **pre-granted** если приложение имеет хотя бы один не-удалённый notification channel
- **Чистая установка**: notifications **OFF** по умолчанию, нужно запросить `Manifest.permission.POST_NOTIFICATIONS`

Решение: добавить запрос permission в onboarding flow для новых установок.
</details>

### Вопрос 4
**Q:** Почему нельзя использовать BroadcastReceiver как trampoline для аналитики на Android 12+?

<details>
<summary>Ответ</summary>

Android 12 (targetSdk 31) запрещает **notification trampolines** — промежуточные компоненты (BroadcastReceiver, Service) которые запускают Activity из notification tap.

`context.startActivity()` из BroadcastReceiver/Service, вызванного через notification PendingIntent, **молча блокируется**. В logcat: "Indirect notification activity start (trampoline) from package blocked".

Решение: PendingIntent.getActivity() напрямую к целевой Activity, аналитику выполнять в `Activity.onCreate()` проверяя intent extras.
</details>

### Вопрос 5
**Q:** В чём разница между notify(id, notification) и notify(tag, id, notification)?

<details>
<summary>Ответ</summary>

Уникальность уведомления определяется комбинацией **tag + id + package**:
- `notify(42, n)` → key = `"pkg|null|42|uid"` (tag = null)
- `notify("chat", 42, n)` → key = `"pkg|chat|42|uid"`

Это **разные** уведомления! `cancel(42)` не уберёт уведомление с tag "chat". Нужен `cancel("chat", 42)`.

Tag удобен для категоризации: `notify("chat", chatId, n)` и `notify("order", orderId, n)` не пересекутся даже если chatId == orderId.
</details>

---

## Связи

### Фундамент
- **[[android-intent-internals]]** — PendingIntent token model, identity delegation, Intent extras для notification data, request code matching
- **[[android-service-internals]]** — FGS notification requirement, foreground service types, startForeground() timing, service lifecycle
- **[[android-binder-ipc]]** — Notification delivery через IPC: App → NMS → SystemUI, три процесса, асинхронная доставка

### Безопасность
- **[[android-permissions-security]]** — POST_NOTIFICATIONS runtime permission, USE_FULL_SCREEN_INTENT special permission, FGS type permissions, BIND_NOTIFICATION_LISTENER_SERVICE

### Системные события
- **[[android-broadcast-internals]]** — BroadcastReceiver для notification actions (Direct Reply, dismiss), system broadcast при изменении каналов

### UI и Compose
- **[[android-compose]]** — Compose UI для notification permission request, settings screens, in-app notification preferences
- **[[android-activity-lifecycle]]** — Notification opens Activity через PendingIntent, savedInstanceState при cold start из notification

### Архитектура
- **[[android-app-components]]** — Notification как системный компонент, связь с Activity, Service, BroadcastReceiver
- **[[android-background-work]]** — WorkManager + notification progress, FGS notifications для long-running tasks

---

## Источники

| # | Источник | Тип | Описание |
|---|---------|-----|----------|
| 1 | [Create a notification](https://developer.android.com/develop/ui/views/notifications/build-notification) | Docs | Построение уведомлений — полный guide |
| 2 | [Notification channels](https://developer.android.com/develop/ui/views/notifications/channels) | Docs | Управление каналами, importance levels |
| 3 | [Notification permission](https://developer.android.com/develop/ui/views/notifications/notification-permission) | Docs | POST_NOTIFICATIONS (Android 13+) |
| 4 | [Android 12 behavior changes](https://developer.android.com/about/versions/12/behavior-changes-12) | Docs | Trampoline restrictions, PendingIntent mutability |
| 5 | [Notification styles](https://developer.android.com/develop/ui/views/notifications/expanded) | Docs | BigText, BigPicture, Messaging, Inbox styles |
| 6 | [AOSP: NMS.java](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/services/core/java/com/android/server/notification/NotificationManagerService.java) | AOSP | NotificationManagerService source |
| 7 | [Foreground service types](https://developer.android.com/develop/background-work/services/fgs/service-types) | Docs | FGS types и required permissions (Android 14+) |
| 8 | [Bubbles](https://developer.android.com/develop/ui/views/notifications/bubbles) | Docs | Conversation bubbles API |
| 9 | [People and conversations](https://developer.android.com/develop/ui/views/notifications/conversations) | Docs | MessagingStyle, shortcuts, conversation space |
| 10 | [NotificationListenerService](https://developer.android.com/reference/android/service/notification/NotificationListenerService) | API | Мониторинг всех уведомлений системы |
| 11 | [Full-screen intents](https://developer.android.com/develop/ui/views/notifications/time-sensitive) | Docs | Звонки, будильники, urgent notifications |
| 12 | [AOSP: NotificationRecord.java](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/services/core/java/com/android/server/notification/NotificationRecord.java) | AOSP | Внутреннее представление уведомления |
| 13 | [Android 14 FGS changes](https://developer.android.com/about/versions/14/changes/fgs-types-required) | Docs | FGS type enforcement |
| 14 | [Android 15 notification changes](https://developer.android.com/about/versions/15/behavior-changes-all) | Docs | Cooldown, DND modes |
