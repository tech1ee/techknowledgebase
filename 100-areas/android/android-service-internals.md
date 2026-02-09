---
title: "Service: Started, Bound, Foreground — жизненный цикл и IPC под капотом"
created: 2026-01-27
modified: 2026-01-27
type: deep-dive
area: android
confidence: high
tags:
  - android
  - service
  - foreground-service
  - bound-service
  - binder
  - aidl
  - workmanager
  - ipc
related:
  - "[[android-app-components]]"
  - "[[android-background-work]]"
  - "[[android-process-memory]]"
  - "[[android-context-internals]]"
  - "[[android-handler-looper]]"
  - "[[android-intent-internals]]"
cs-foundations: [client-server, ipc, proxy-pattern, observer-pattern, service-locator, command-pattern, reference-counting]
---

# Service: Started, Bound, Foreground — жизненный цикл и IPC под капотом

> Service — компонент Android для длительных операций без UI. Три формы: Started (запущен через startService, независимый lifecycle), Bound (клиент-серверный через bindService/ServiceConnection/IBinder), Foreground (с обязательным уведомлением, высокий приоритет для LMK). onStartCommand() возвращает START_STICKY (воссоздать с null intent), START_NOT_STICKY (не воссоздавать), START_REDELIVER_INTENT (воссоздать с последним intent). Bound Service использует три IPC механизма: Local Binder (тот же процесс), Messenger (однопоточный IPC), AIDL (многопоточный IPC). Android 14+ требует foregroundServiceType (dataSync, mediaPlayback, location, camera, microphone, health и др.) + соответствующие permissions. Android 15: dataSync ограничен 6 часами. Decision tree: Coroutines (in-process async) -> WorkManager (persistent, deferrable) -> Foreground Service (continuous, user-visible).

---

## Зачем это нужно

### Проблема: сервисы — один из самых неправильно понимаемых компонентов Android

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| ANR (Application Not Responding) | Тяжёлая работа в onStartCommand() на Main Thread | Принудительное закрытие приложения |
| Service убит системой неожиданно | Неправильный return value из onStartCommand() | Потеря данных, незавершённые операции |
| SecurityException на Android 14+ | Нет foregroundServiceType в манифесте | Crash при запуске Foreground Service |
| Background execution limits (Android 8+) | startService() из фона вместо startForegroundService() | IllegalStateException, crash |
| Неправильный выбор инструмента | Service вместо WorkManager или Coroutines | Перерасход батареи, убийство системой, плохой UX |
| ForegroundServiceStartNotAllowedException | Запуск FGS из фона на Android 12+ | Crash, невозможность выполнить задачу |
| Binder TransactionTooLargeException | Передача >1MB данных через IPC | Crash при обмене данными между процессами |
| Service leak | bindService() без unbindService() | Утечка памяти, Service живёт бесконечно |
| Timeout на Foreground Service | Не вызван startForeground() за 5 сек после startForegroundService() | ANR и crash |
| dataSync timeout на Android 15 | Foreground Service типа dataSync работает >6 часов | Принудительная остановка системой |

### Актуальность в 2025-2026

**Foreground Service Types обязательны с Android 14 (API 34):**

```kotlin
// ❌ CRASH на Android 14+: нет foregroundServiceType
<service android:name=".MyService"
    android:foregroundServiceType="" />  // SecurityException!

// ✅ ПРАВИЛЬНО: указываем конкретный тип
<service android:name=".MyService"
    android:foregroundServiceType="dataSync" />
```

**Android 15 (API 35): dataSync ограничен 6 часами:**

```kotlin
// На Android 15 система принудительно остановит dataSync FGS через 6 часов
// Решение: использовать WorkManager для длительной синхронизации
```

**Статистика:**
- **foregroundServiceType** обязателен с Android 14 (API 34)
- **dataSync** ограничен 6 часами на Android 15 (API 35)
- **WorkManager** рекомендован Google для 90%+ фоновой работы
- **Coroutines + lifecycleScope** — для in-process async операций
- Foreground Service — только для continuous, user-visible задач (музыка, GPS-навигация, звонки)

**Что вы узнаете:**
1. Полный lifecycle Service: Started, Bound, Hybrid
2. Foreground Service от Android 8 до Android 15: типы, permissions, ограничения
3. Три IPC механизма: Local Binder, Messenger, AIDL — под капотом
4. Binder IPC: Proxy/Stub, kernel driver, Parcel
5. LMK (Low Memory Killer) и приоритеты процессов
6. Decision tree: Service vs WorkManager vs Coroutines
7. Background execution limits: Android 8 -> 12 -> 14 -> 15

---

## Prerequisites

Для полного понимания материала необходимо:

| Тема | Почему нужна | Ссылка |
|------|-------------|--------|
| Android App Components | Понимание 4 компонентов: Activity, Service, BroadcastReceiver, ContentProvider | [[android-app-components]] |
| Background Work | Обзор способов фоновой работы: WorkManager, Coroutines, AlarmManager | [[android-background-work]] |
| Process & Memory | Как Android управляет процессами, LMK, OOM Killer | [[android-process-memory]] |
| Context Internals | Context — базовый класс Service; ApplicationContext vs Activity Context | [[android-context-internals]] |
| Handler/Looper | Service работает на Main Thread; Handler для IPC через Messenger | [[android-handler-looper]] |
| Intent Internals | startService(intent), bindService(intent) — механизм передачи данных | [[android-intent-internals]] |

---

## Терминология

### Service
**Service** — компонент приложения, который выполняет длительные операции без пользовательского интерфейса. Service работает на **Main Thread** вызвавшего процесса. Service — это НЕ отдельный поток и НЕ отдельный процесс (если явно не указан `android:process`).

### Started Service
**Started Service** — сервис, запущенный через `startService()` или `startForegroundService()`. Работает независимо от вызвавшего компонента. Продолжает работать даже если вызвавший компонент (Activity) уничтожен. Останавливается через `stopSelf()` или `stopService()`.

### Bound Service
**Bound Service** — сервис, к которому клиент привязывается через `bindService()`. Предоставляет клиент-серверный интерфейс через `IBinder`. Работает пока есть хотя бы один привязанный клиент. Когда все клиенты отвязались — Service уничтожается.

### Foreground Service
**Foreground Service** — сервис с обязательным уведомлением в статус-баре. Имеет высокий приоритет для LMK — система не убивает его при нехватке памяти. С Android 14 требует явного `foregroundServiceType` в манифесте.

### onStartCommand()
**onStartCommand()** — callback метод, вызываемый системой при каждом вызове `startService()`. Возвращает значение, определяющее поведение при убийстве сервиса системой: `START_NOT_STICKY`, `START_STICKY`, `START_REDELIVER_INTENT`.

### ServiceConnection
**ServiceConnection** — интерфейс с двумя callbacks: `onServiceConnected(ComponentName, IBinder)` и `onServiceDisconnected(ComponentName)`. Используется клиентом для получения `IBinder` при привязке к Bound Service.

### IBinder
**IBinder** — интерфейс для удалённого (или локального) взаимодействия с объектом. Основа всего IPC в Android. Возвращается из `onBind()` и передаётся клиенту через `ServiceConnection.onServiceConnected()`.

### AIDL (Android Interface Definition Language)
**AIDL** — язык описания интерфейсов для многопоточного межпроцессного взаимодействия. Компилятор AIDL генерирует `Stub` (серверная сторона) и `Proxy` (клиентская сторона). Поддерживает примитивы, String, List, Map, Parcelable.

### Messenger
**Messenger** — простой механизм однопоточного IPC на основе Handler + Message. Все сообщения обрабатываются последовательно в одном потоке. Подходит для простого IPC без необходимости thread-safety.

### WorkManager
**WorkManager** — Jetpack API для отложенной, гарантированной фоновой работы. Переживает перезагрузку устройства. Поддерживает constraints (сеть, зарядка, idle). Рекомендован Google для 90%+ случаев фоновой работы.

---

## 1. Service Lifecycle: Started vs Bound vs Hybrid

### ЧТО: полный lifecycle

Service имеет три формы lifecycle, которые могут комбинироваться:

```
╔══════════════════════════════════════════════════════════════════════╗
║                    STARTED SERVICE LIFECYCLE                        ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  startService(intent)                                                ║
║       │                                                              ║
║       ▼                                                              ║
║  ┌──────────┐    Только один раз                                    ║
║  │ onCreate()│───────────────────────────────────────────┐           ║
║  └────┬─────┘                                            │           ║
║       │                                                  │           ║
║       ▼                                                  │           ║
║  ┌──────────────────┐    При КАЖДОМ startService()       │           ║
║  │ onStartCommand() │◄──────────────────────────────┐    │           ║
║  │  return START_*   │                               │    │           ║
║  └────┬─────────────┘                               │    │           ║
║       │                                              │    │           ║
║       ▼                                              │    │           ║
║  ┌──────────────┐    startService() ещё раз          │    │           ║
║  │  [RUNNING]    │──────────────────────────────────┘    │           ║
║  └────┬─────────┘                                        │           ║
║       │                                                  │           ║
║       │ stopSelf() / stopService()                       │           ║
║       ▼                                                  │           ║
║  ┌─────────────┐                                         │           ║
║  │ onDestroy() │                                         │           ║
║  └─────────────┘                                         │           ║
║                                                          │           ║
╚══════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════╗
║                     BOUND SERVICE LIFECYCLE                          ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  bindService(intent, conn, flags)                                    ║
║       │                                                              ║
║       ▼                                                              ║
║  ┌──────────┐    Только один раз                                    ║
║  │ onCreate()│                                                       ║
║  └────┬─────┘                                                        ║
║       │                                                              ║
║       ▼                                                              ║
║  ┌──────────┐    Возвращает IBinder                                 ║
║  │ onBind() │──────────────────────────┐                             ║
║  └────┬─────┘                          │                             ║
║       │                                ▼                             ║
║       ▼                         ServiceConnection                    ║
║  ┌──────────────┐               .onServiceConnected()                ║
║  │ [CLIENTS     │                                                    ║
║  │  BOUND]      │    N клиентов привязаны                           ║
║  │  refCount: N │    (reference counting)                            ║
║  └────┬─────────┘                                                    ║
║       │                                                              ║
║       │ Последний клиент вызвал unbindService()                      ║
║       │ refCount: 0                                                  ║
║       ▼                                                              ║
║  ┌───────────┐                                                       ║
║  │ onUnbind() │    return true → onRebind() при новом bind          ║
║  └────┬──────┘    return false (default) → onBind() при новом bind  ║
║       │                                                              ║
║       ▼                                                              ║
║  ┌─────────────┐                                                     ║
║  │ onDestroy() │                                                     ║
║  └─────────────┘                                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝


╔══════════════════════════════════════════════════════════════════════╗
║                    HYBRID SERVICE LIFECYCLE                           ║
║               (Started + Bound одновременно)                         ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  startService() + bindService()                                      ║
║       │                │                                             ║
║       ▼                ▼                                             ║
║  ┌──────────┐                                                        ║
║  │ onCreate()│    (один раз)                                         ║
║  └────┬─────┘                                                        ║
║       │                                                              ║
║       ├─── onStartCommand()   (для started)                          ║
║       ├─── onBind()           (для bound)                            ║
║       │                                                              ║
║       ▼                                                              ║
║  ┌──────────────────────────────────────┐                            ║
║  │  [RUNNING + CLIENTS BOUND]            │                            ║
║  │                                        │                            ║
║  │  Уничтожается ТОЛЬКО когда:           │                            ║
║  │  1. stopSelf()/stopService() вызван   │                            ║
║  │     AND                                │                            ║
║  │  2. Все клиенты unbind()              │                            ║
║  └────┬──────────────────────────────────┘                            ║
║       │                                                              ║
║       ▼                                                              ║
║  ┌─────────────┐                                                     ║
║  │ onDestroy() │                                                     ║
║  └─────────────┘                                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
```

### ПОЧЕМУ: зачем три формы

**Started Service** — для задач, которые должны выполняться независимо от UI:
- Загрузка файла продолжается даже если Activity закрыта
- Service сам решает, когда остановиться (`stopSelf()`)

**Bound Service** — для клиент-серверного взаимодействия:
- Activity (клиент) вызывает методы Service (сервер)
- Lifecycle привязан к клиенту: нет клиентов = уничтожение

**Hybrid** — когда нужно и то, и другое:
- Музыкальный плеер: Started (фоновое воспроизведение) + Bound (UI управление)

### КАК РАБОТАЕТ: Service работает на MAIN THREAD

**КРИТИЧЕСКИ ВАЖНО:** Service работает на Main Thread процесса!

```kotlin
class MyService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ⚠️ ЭТО ВЫПОЛНЯЕТСЯ НА MAIN THREAD!
        // Тяжёлая работа здесь вызовет ANR через 5 секунд

        // ❌ НЕПРАВИЛЬНО: блокирующая операция на Main Thread
        // val data = downloadFile(url)  // ANR!

        // ✅ ПРАВИЛЬНО: переносим работу в отдельный поток
        Thread {
            val data = downloadFile(url)
            stopSelf(startId)
        }.start()

        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Service — это НЕ процесс:**

```
┌─────────────────────────────────────────────────────┐
│                  APPLICATION PROCESS                  │
│                                                       │
│  ┌──────────────────────────────────────────────┐    │
│  │              MAIN THREAD                       │    │
│  │                                                │    │
│  │  Activity.onCreate()         ← UI callbacks   │    │
│  │  Activity.onResume()                           │    │
│  │  Service.onCreate()          ← Service callbacks│   │
│  │  Service.onStartCommand()                      │    │
│  │  BroadcastReceiver.onReceive()                 │    │
│  │                                                │    │
│  │  ВСЁ на одном потоке!                         │    │
│  └──────────────────────────────────────────────┘    │
│                                                       │
│  ┌──────────────┐  ┌──────────────┐                  │
│  │ Worker Thread │  │ Worker Thread │   ← ваши потоки│
│  │ (download)    │  │ (processing)  │                 │
│  └──────────────┘  └──────────────┘                  │
│                                                       │
└─────────────────────────────────────────────────────┘
```

### КАК ПРИМЕНЯТЬ: onStartCommand() return values

```kotlin
class DownloadService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val url = intent?.getStringExtra("url")

        Thread {
            downloadFile(url)
            stopSelf(startId) // Останавливаем с конкретным startId
        }.start()

        // Выбираем return value в зависимости от логики
        return START_REDELIVER_INTENT
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Таблица return values onStartCommand():**

| Return Value | Система убила Service | Пересоздаст? | Intent при рестарте | Когда использовать |
|---|---|---|---|---|
| `START_NOT_STICKY` | Да | Нет | N/A | Задачи, которые можно НЕ повторять. Например: периодический upload аналитики |
| `START_STICKY` | Да | Да | `null` | Задачи без входных данных. Например: музыкальный плеер (возобновит воспроизведение) |
| `START_REDELIVER_INTENT` | Да | Да | Последний полученный intent | Задачи с критичными данными. Например: загрузка файла (URL в intent) |
| `START_STICKY_COMPATIBILITY` | Да | Возможно | `null` | Legacy: не гарантирует onStartCommand() при рестарте |

**stopSelf(startId) vs stopSelf():**

```kotlin
class MultiTaskService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Каждый вызов startService() получает уникальный startId

        Thread {
            processTask(intent)

            // stopSelf(startId) — безопасная остановка
            // Service остановится ТОЛЬКО если startId == последний полученный startId
            // Если пришли новые задачи — Service продолжит работать
            stopSelf(startId)

            // stopSelf() без параметра — немедленная остановка
            // ❌ Опасно: прервёт обработку новых задач
            // stopSelf()
        }.start()

        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### ПОДВОДНЫЕ КАМНИ

**1. Service убивается и не пересоздаётся:**

```kotlin
// ❌ ПРОБЛЕМА: START_NOT_STICKY + критичная задача
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    Thread {
        uploadImportantData(intent) // Может не завершиться!
    }.start()
    return START_NOT_STICKY // Система убьёт и НЕ пересоздаст
}

// ✅ РЕШЕНИЕ: START_REDELIVER_INTENT для критичных задач
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    Thread {
        uploadImportantData(intent)
        stopSelf(startId)
    }.start()
    return START_REDELIVER_INTENT // Система пересоздаст с тем же intent
}
```

**2. Multiple startService() calls:**

```kotlin
// Каждый вызов startService() → новый onStartCommand()
// НО onCreate() вызывается только один раз!

// Activity:
startService(Intent(this, MyService::class.java).putExtra("task", "A"))
startService(Intent(this, MyService::class.java).putExtra("task", "B"))
startService(Intent(this, MyService::class.java).putExtra("task", "C"))

// Service получит:
// onCreate() — один раз
// onStartCommand(intent="A", startId=1)
// onStartCommand(intent="B", startId=2)
// onStartCommand(intent="C", startId=3)
```

**3. Bound Service reference counting:**

```kotlin
// Activity A: bindService() → refCount = 1
// Activity B: bindService() → refCount = 2
// Activity A: unbindService() → refCount = 1 → Service продолжает работать
// Activity B: unbindService() → refCount = 0 → onUnbind() → onDestroy()
```

---

## 2. Foreground Service (Android 8 через 15)

### ЧТО: Foreground Service и его эволюция

Foreground Service — сервис с уведомлением в статус-баре. Система не убивает его при нехватке памяти (высокий приоритет для LMK).

### ПОЧЕМУ: почему нужен Foreground Service

1. **Visibility для пользователя** — уведомление показывает, что приложение работает
2. **Защита от LMK** — система не убьёт процесс с foreground service
3. **Требование платформы** — с Android 8 фоновые сервисы убиваются через несколько минут

### КАК РАБОТАЕТ: эволюция от Android 8 до Android 15

**Android 8 (API 26): Background Execution Limits**

```kotlin
// ❌ Android 8+: IllegalStateException из фона
context.startService(intent) // Crash если приложение в фоне!

// ✅ Правильно: startForegroundService() + startForeground() за 5 секунд
context.startForegroundService(intent)

// В Service: обязательно вызвать startForeground() за 5 секунд
class MyForegroundService : Service() {
    override fun onCreate() {
        super.onCreate()

        val notification = createNotification()
        // Вызвать в течение 5 секунд после startForegroundService()!
        startForeground(NOTIFICATION_ID, notification)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Работа в фоновом потоке
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    private fun createNotification(): Notification {
        val channelId = "foreground_service"
        val channel = NotificationChannel(
            channelId,
            "Фоновая работа",
            NotificationManager.IMPORTANCE_LOW
        )
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)

        return Notification.Builder(this, channelId)
            .setContentTitle("Сервис работает")
            .setContentText("Выполняется загрузка...")
            .setSmallIcon(R.drawable.ic_download)
            .build()
    }

    companion object {
        private const val NOTIFICATION_ID = 1
    }
}
```

**Android 12 (API 31): Restrictions on background FGS starts**

```kotlin
// Android 12+: нельзя запускать FGS из фона в большинстве случаев
// ForegroundServiceStartNotAllowedException

// Исключения — когда МОЖНО запускать FGS из фона:
// 1. Из BroadcastReceiver, запущенного visible notification
// 2. Из высокоприоритетного FCM (Firebase Cloud Messaging)
// 3. Из компонента с SYSTEM_ALERT_WINDOW permission
// 4. По клику на Action из Notification
// 5. Companion device / auto / TV / watch

// Рекомендация: используйте WorkManager для задач из фона
```

**Android 14 (API 34): foregroundServiceType ОБЯЗАТЕЛЕН**

```xml
<!-- AndroidManifest.xml -->

<!-- ❌ CRASH на Android 14+: нет foregroundServiceType -->
<service android:name=".MyService" />

<!-- ✅ ПРАВИЛЬНО: указываем тип -->
<service
    android:name=".DownloadService"
    android:foregroundServiceType="dataSync"
    android:exported="false" />

<!-- Для нескольких типов: объединяем через | -->
<service
    android:name=".MediaService"
    android:foregroundServiceType="mediaPlayback|camera"
    android:exported="false" />
```

```kotlin
// Код: указываем тип при вызове startForeground()
class DownloadService : Service() {
    override fun onCreate() {
        super.onCreate()

        val notification = createNotification()

        // Android 14+: указываем тип при startForeground
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Запускаем работу в фоновом потоке
        Thread {
            performDataSync()
            stopSelf()
        }.start()
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Android 15 (API 35): dataSync ограничен 6 часами**

```kotlin
// Android 15: dataSync foreground service принудительно останавливается через 6 часов
// Система вызывает Service.onTimeout(int fgsType)

class SyncService : Service() {

    // Android 15+: callback при таймауте FGS
    override fun onTimeout(foregroundServiceType: Int) {
        // Система уведомляет: у вас N секунд чтобы вызвать stopSelf()
        // Если не остановите — система убьёт Service

        // Сохраняем прогресс
        saveProgress()

        // Планируем продолжение через WorkManager
        scheduleResumeThroughWorkManager()

        // Останавливаем Service
        stopSelf()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### КАК ПРИМЕНЯТЬ: полная таблица foreground service types

| Тип | Permissions (Manifest) | Runtime Permissions | Типичное использование | Лимит времени (Android 15) |
|---|---|---|---|---|
| `dataSync` | `FOREGROUND_SERVICE_DATA_SYNC` | — | Загрузка/выгрузка файлов, синхронизация | 6 часов |
| `mediaPlayback` | `FOREGROUND_SERVICE_MEDIA_PLAYBACK` | — | Музыка, подкасты, аудиокниги | Нет |
| `location` | `FOREGROUND_SERVICE_LOCATION` | `ACCESS_FINE_LOCATION` или `ACCESS_COARSE_LOCATION` | GPS-навигация, трекинг | Нет |
| `camera` | `FOREGROUND_SERVICE_CAMERA` | `CAMERA` | Запись видео, видеозвонки | Нет |
| `microphone` | `FOREGROUND_SERVICE_MICROPHONE` | `RECORD_AUDIO` | Запись аудио, голосовые вызовы | Нет |
| `health` | `FOREGROUND_SERVICE_HEALTH` | `BODY_SENSORS` или `ACTIVITY_RECOGNITION` | Фитнес-трекер, пульсометр | Нет |
| `mediaProjection` | `FOREGROUND_SERVICE_MEDIA_PROJECTION` | Подтверждение пользователя через MediaProjection API | Запись экрана, скриншоты | Нет |
| `connectedDevice` | `FOREGROUND_SERVICE_CONNECTED_DEVICE` | `BLUETOOTH_CONNECT` или USB | Bluetooth-устройства, Auto | Нет |
| `phoneCall` | `FOREGROUND_SERVICE_PHONE_CALL` | `MANAGE_OWN_CALLS` | VoIP звонки, SIP | Нет |
| `remoteMessaging` | `FOREGROUND_SERVICE_REMOTE_MESSAGING` | — | Messaging на других устройствах (Wear, Auto) | Нет |
| `shortService` | `FOREGROUND_SERVICE_SHORT_SERVICE` | — | Быстрые задачи (<3 мин) | ~3 минуты |
| `specialUse` | `FOREGROUND_SERVICE_SPECIAL_USE` | — | Крайний случай; требует review от Google Play | Нет |
| `systemExempted` | — | — | Только для системных приложений | Нет |

### КАК ПРИМЕНЯТЬ: полный пример Foreground Service

```kotlin
// === AndroidManifest.xml ===
// <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
// <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
// <uses-permission android:name="android.permission.POST_NOTIFICATIONS" /> <!-- Android 13+ -->
//
// <service
//     android:name=".FileDownloadService"
//     android:foregroundServiceType="dataSync"
//     android:exported="false" />

class FileDownloadService : Service() {

    private val coroutineScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val url = intent?.getStringExtra(EXTRA_URL) ?: run {
            stopSelf()
            return START_NOT_STICKY
        }

        // Создаём уведомление и переходим в foreground
        val notification = buildNotification("Начинаем загрузку...", 0)

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        // Запускаем загрузку в корутине
        coroutineScope.launch {
            try {
                downloadFile(url) { progress ->
                    // Обновляем уведомление с прогрессом
                    updateNotification("Загрузка: $progress%", progress)
                }
                // Загрузка завершена
                updateNotification("Загрузка завершена", 100)
            } catch (e: Exception) {
                updateNotification("Ошибка: ${e.message}", 0)
            } finally {
                // Ждём немного чтобы пользователь увидел результат
                delay(2000)
                stopSelf(startId)
            }
        }

        return START_REDELIVER_INTENT
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        coroutineScope.cancel()
    }

    // Android 15: callback при таймауте dataSync (6 часов)
    override fun onTimeout(foregroundServiceType: Int) {
        coroutineScope.cancel()
        stopSelf()
    }

    private fun createNotificationChannel() {
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Загрузки",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "Уведомления о загрузке файлов"
        }
        val manager = getSystemService(NotificationManager::class.java)
        manager.createNotificationChannel(channel)
    }

    private fun buildNotification(text: String, progress: Int): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Загрузка файла")
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_download)
            .setProgress(100, progress, progress == 0)
            .setOngoing(true)
            .setSilent(true)
            .build()
    }

    private fun updateNotification(text: String, progress: Int) {
        val notification = buildNotification(text, progress)
        val manager = getSystemService(NotificationManager::class.java)
        manager.notify(NOTIFICATION_ID, notification)
    }

    private suspend fun downloadFile(
        url: String,
        onProgress: (Int) -> Unit
    ) {
        // Имитация загрузки
        for (i in 1..100) {
            delay(100) // Имитация работы
            onProgress(i)
        }
    }

    companion object {
        const val EXTRA_URL = "extra_url"
        private const val NOTIFICATION_ID = 1001
        private const val CHANNEL_ID = "download_channel"

        fun start(context: Context, url: String) {
            val intent = Intent(context, FileDownloadService::class.java).apply {
                putExtra(EXTRA_URL, url)
            }
            ContextCompat.startForegroundService(context, intent)
        }
    }
}

// Использование из Activity:
// FileDownloadService.start(this, "https://example.com/file.zip")
```

### ПОДВОДНЫЕ КАМНИ

**1. 5-секундный таймаут startForeground():**

```kotlin
// ❌ ПРОБЛЕМА: startForeground() не вызван вовремя
class BadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            // Тяжёлая инициализация в фоновом потоке
            Thread.sleep(6000) // >5 секунд!
            startForeground(1, createNotification()) // ПОЗДНО! ANR/Crash
        }.start()
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// ✅ РЕШЕНИЕ: startForeground() сразу в onCreate() или onStartCommand()
class GoodService : Service() {
    override fun onCreate() {
        super.onCreate()
        startForeground(1, createNotification()) // Сразу!
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            // Тяжёлая работа — можно без спешки
            performWork()
            stopSelf()
        }.start()
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**2. notificationId 0 запрещён:**

```kotlin
// ❌ CRASH: notificationId == 0
startForeground(0, notification) // IllegalArgumentException!

// ✅ ПРАВИЛЬНО: notificationId > 0
startForeground(1, notification)
```

**3. Android 13+ Permission POST_NOTIFICATIONS:**

```kotlin
// Android 13+ (API 33): нужен runtime permission для уведомлений
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    if (ContextCompat.checkSelfPermission(
            this, Manifest.permission.POST_NOTIFICATIONS
        ) != PackageManager.PERMISSION_GRANTED) {
        // Запрашиваем permission
        requestPermissions(
            arrayOf(Manifest.permission.POST_NOTIFICATIONS),
            REQUEST_CODE
        )
        return // Не запускаем Service без permission
    }
}

// Теперь можно запускать FGS
startForegroundService(intent)
```

---

## 3. Bound Service: три IPC механизма

### ЧТО: три способа связи клиента с Service

```
┌───────────────────────────────────────────────────────────────────┐
│                    BOUND SERVICE IPC MECHANISMS                    │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐                                              │
│  │  1. LOCAL BINDER │  Тот же процесс                            │
│  │                   │  Прямой вызов методов                      │
│  │  Самый быстрый   │  Нет сериализации                          │
│  └─────────────────┘                                              │
│                                                                   │
│  ┌─────────────────┐                                              │
│  │  2. MESSENGER    │  Межпроцессный (простой)                   │
│  │                   │  Однопоточная обработка                    │
│  │  Средний         │  Handler + Message                          │
│  └─────────────────┘                                              │
│                                                                   │
│  ┌─────────────────┐                                              │
│  │  3. AIDL         │  Межпроцессный (полный)                    │
│  │                   │  Многопоточная обработка                   │
│  │  Самый мощный    │  Binder thread pool                        │
│  └─────────────────┘                                              │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘

Выбор:
  Тот же процесс?      → Local Binder
  Простой IPC?          → Messenger
  Многопоточный IPC?    → AIDL
```

---

### 3a. Local Binder (тот же процесс)

#### ЧТО

Local Binder — самый простой способ привязки к Service. Клиент получает прямой доступ к экземпляру Service через IBinder. Работает только в одном процессе.

#### ПОЧЕМУ

- Нет overhead на сериализацию/десериализацию
- Прямой вызов методов — как обычный объект
- Идеален когда Service и Activity в одном процессе (99% приложений)

#### КАК РАБОТАЕТ

```kotlin
// === Service ===
class MusicService : Service() {

    // Binder, который возвращает ссылку на сам Service
    inner class LocalBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    private val binder = LocalBinder()

    private var isPlaying = false
    private var currentTrack: String? = null

    override fun onBind(intent: Intent?): IBinder {
        // Возвращаем binder клиенту
        return binder
    }

    // Публичные методы, доступные клиенту через binder
    fun play(track: String) {
        currentTrack = track
        isPlaying = true
        // Запуск воспроизведения...
    }

    fun pause() {
        isPlaying = false
    }

    fun isPlaying(): Boolean = isPlaying

    fun getCurrentTrack(): String? = currentTrack
}


// === Activity (клиент) ===
class MusicActivity : AppCompatActivity() {

    private var musicService: MusicService? = null
    private var isBound = false

    // ServiceConnection — callback при привязке/отвязке
    private val connection = object : ServiceConnection {

        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            // Приведение IBinder к нашему LocalBinder
            val binder = service as MusicService.LocalBinder
            musicService = binder.getService()
            isBound = true

            // Теперь можем вызывать методы Service напрямую
            updateUI()
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            // Вызывается ТОЛЬКО при crash сервиса или убийстве процесса
            // НЕ вызывается при unbindService()!
            musicService = null
            isBound = false
        }
    }

    override fun onStart() {
        super.onStart()
        // Привязка к Service
        Intent(this, MusicService::class.java).also { intent ->
            bindService(intent, connection, Context.BIND_AUTO_CREATE)
        }
    }

    override fun onStop() {
        super.onStop()
        // Отвязка от Service
        if (isBound) {
            unbindService(connection)
            isBound = false
        }
    }

    private fun onPlayButtonClick() {
        if (isBound) {
            musicService?.play("my_track.mp3")
            updateUI()
        }
    }

    private fun updateUI() {
        val isPlaying = musicService?.isPlaying() ?: false
        val track = musicService?.getCurrentTrack() ?: "—"
        // Обновление UI...
    }
}
```

#### КАК ПРИМЕНЯТЬ

```
┌─────────────────┐         ┌──────────────────────┐
│   Activity       │         │   MusicService        │
│                   │         │                        │
│  bindService() ──┼────────►│  onBind()              │
│                   │         │    return LocalBinder   │
│                   │◄────────┼──                       │
│  connection       │         │                        │
│   .onServiceConnected()    │                        │
│   binder.getService() ────►│                        │
│   service.play("track") ──►│  play("track")         │
│   service.isPlaying() ────►│  isPlaying(): Boolean  │
│                   │         │                        │
│  unbindService() ─┼────────►│  onUnbind()            │
│                   │         │  onDestroy()           │
└─────────────────┘         └──────────────────────┘

Прямой вызов методов — никакой сериализации!
```

#### ПОДВОДНЫЕ КАМНИ

```kotlin
// ❌ ПРОБЛЕМА: вызов метода Service до привязки
class BadActivity : AppCompatActivity() {
    private var service: MusicService? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        bindService(intent, connection, BIND_AUTO_CREATE)

        // ❌ service ещё null! bindService() — асинхронный!
        service?.play("track") // NullPointerException или ignored
    }
}

// ✅ РЕШЕНИЕ: дождаться onServiceConnected()
class GoodActivity : AppCompatActivity() {
    private var service: MusicService? = null
    private var pendingAction: (() -> Unit)? = null

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            service = (binder as MusicService.LocalBinder).getService()
            // Выполняем отложенное действие
            pendingAction?.invoke()
            pendingAction = null
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            service = null
        }
    }

    fun playTrack(track: String) {
        if (service != null) {
            service?.play(track)
        } else {
            // Откладываем до onServiceConnected()
            pendingAction = { service?.play(track) }
        }
    }
}
```

---

### 3b. Messenger (простой межпроцессный IPC)

#### ЧТО

Messenger — обёртка над Handler для однопоточного IPC. Все сообщения обрабатываются последовательно в одном потоке — не нужна thread-safety. Подходит для простого обмена данными между процессами.

#### ПОЧЕМУ

- Проще AIDL — не нужно писать .aidl файлы
- Однопоточный — не нужна синхронизация
- Межпроцессный — работает между разными процессами

#### КАК РАБОТАЕТ

```
┌──────────────────────┐              ┌──────────────────────┐
│     КЛИЕНТ            │              │     SERVICE            │
│     (Process A)       │              │     (Process B)        │
│                        │              │                        │
│  ┌──────────────────┐ │              │ ┌──────────────────┐  │
│  │ Client Handler   │ │              │ │ Service Handler  │  │
│  │ (для ответов)    │ │              │ │ handleMessage()  │  │
│  │       ▲           │ │              │ │       ▲          │  │
│  │       │           │ │              │ │       │          │  │
│  │ Client Messenger │ │              │ │ Srv Messenger    │  │
│  │   (replyTo)      │ │              │ │                  │  │
│  └───────┼──────────┘ │              │ └───────┼──────────┘  │
│          │             │              │         │              │
│          │   Message   │   Binder     │         │              │
│          │◄────────────┼──────────────┼─────────┘              │
│          │             │   IPC        │                        │
│   send ──┼─────────────┼──────────────┼─────────► receive     │
│  (Messenger.send())   │              │    handleMessage()     │
│                        │              │                        │
└──────────────────────┘              └──────────────────────┘
```

```kotlin
// === Service (Process B) ===

class MessengerService : Service() {

    // Handler для обработки входящих сообщений от клиентов
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MSG_SAY_HELLO -> {
                    // Обрабатываем сообщение от клиента
                    val data = msg.data.getString("name") ?: "Мир"

                    // Отправляем ответ клиенту через replyTo
                    msg.replyTo?.let { clientMessenger ->
                        val reply = Message.obtain(null, MSG_HELLO_RESPONSE).apply {
                            this.data = Bundle().apply {
                                putString("greeting", "Привет, $data!")
                            }
                        }
                        try {
                            clientMessenger.send(reply)
                        } catch (e: RemoteException) {
                            // Клиент отключился
                        }
                    }
                }

                MSG_GET_STATUS -> {
                    msg.replyTo?.let { clientMessenger ->
                        val reply = Message.obtain(null, MSG_STATUS_RESPONSE).apply {
                            arg1 = 42 // Статус
                        }
                        try {
                            clientMessenger.send(reply)
                        } catch (e: RemoteException) {
                            // Клиент отключился
                        }
                    }
                }
            }
        }
    }

    // Messenger на основе Handler
    private val messenger = Messenger(handler)

    override fun onBind(intent: Intent?): IBinder {
        // Возвращаем IBinder от Messenger
        return messenger.binder
    }

    companion object {
        const val MSG_SAY_HELLO = 1
        const val MSG_GET_STATUS = 2
        const val MSG_HELLO_RESPONSE = 3
        const val MSG_STATUS_RESPONSE = 4
    }
}


// === Activity (клиент, Process A) ===

class MessengerActivity : AppCompatActivity() {

    private var serviceMessenger: Messenger? = null
    private var isBound = false

    // Handler для получения ответов от Service
    private val replyHandler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            when (msg.what) {
                MessengerService.MSG_HELLO_RESPONSE -> {
                    val greeting = msg.data.getString("greeting")
                    // Обновляем UI с полученным приветствием
                    showMessage(greeting ?: "—")
                }

                MessengerService.MSG_STATUS_RESPONSE -> {
                    val status = msg.arg1
                    showMessage("Статус: $status")
                }
            }
        }
    }

    // Messenger для получения ответов
    private val replyMessenger = Messenger(replyHandler)

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            // Создаём Messenger для отправки сообщений в Service
            serviceMessenger = Messenger(service)
            isBound = true
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            serviceMessenger = null
            isBound = false
        }
    }

    override fun onStart() {
        super.onStart()
        // Привязка к Service в другом процессе
        val intent = Intent(this, MessengerService::class.java)
        bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    override fun onStop() {
        super.onStop()
        if (isBound) {
            unbindService(connection)
            isBound = false
        }
    }

    fun sayHello(name: String) {
        if (!isBound) return

        val msg = Message.obtain(null, MessengerService.MSG_SAY_HELLO).apply {
            data = Bundle().apply {
                putString("name", name)
            }
            // Указываем Messenger для ответа
            replyTo = replyMessenger
        }

        try {
            serviceMessenger?.send(msg)
        } catch (e: RemoteException) {
            // Service отключился
        }
    }

    private fun showMessage(text: String) {
        // Обновление UI
    }
}
```

#### ПОДВОДНЫЕ КАМНИ

```kotlin
// ❌ ПРОБЛЕМА: Messenger однопоточный — блокирующие операции заблокируют все сообщения
private val handler = object : Handler(Looper.getMainLooper()) {
    override fun handleMessage(msg: Message) {
        Thread.sleep(5000) // Все следующие сообщения ждут!
    }
}

// ✅ РЕШЕНИЕ: тяжёлую работу выносить в отдельный поток
private val handler = object : Handler(Looper.getMainLooper()) {
    override fun handleMessage(msg: Message) {
        val replyTo = msg.replyTo
        Thread {
            val result = heavyComputation()
            replyTo?.let {
                val reply = Message.obtain(null, MSG_RESULT).apply {
                    arg1 = result
                }
                it.send(reply)
            }
        }.start()
    }
}
```

---

### 3c. AIDL (полный многопоточный IPC)

#### ЧТО

AIDL (Android Interface Definition Language) — язык описания интерфейсов для многопоточного межпроцессного взаимодействия. Компилятор AIDL генерирует Stub (серверная сторона) и Proxy (клиентская сторона).

#### ПОЧЕМУ

- **Многопоточный** — запросы обрабатываются параллельно в Binder thread pool
- **Типизированный** — интерфейс описан в .aidl файле
- **Мощный** — поддерживает callbacks, in/out/inout параметры, oneway вызовы

#### КАК РАБОТАЕТ: от .aidl до IPC

**Шаг 1: Описание интерфейса (.aidl файл)**

```java
// ICalculatorService.aidl
package com.example.calculator;

// Описание IPC интерфейса
interface ICalculatorService {
    // Синхронный вызов — клиент блокируется до получения результата
    int add(int a, int b);
    int multiply(int a, int b);

    // oneway — асинхронный вызов, клиент НЕ блокируется
    oneway void logOperation(String operation);
}
```

**Шаг 2: Компилятор генерирует Stub и Proxy**

```
┌──────────────────────┐
│ ICalculatorService    │   (.aidl файл)
│  .aidl                │
└─────────┬────────────┘
          │
          ▼  AIDL compiler
┌──────────────────────────────────────────────────────┐
│ ICalculatorService.java (сгенерировано)               │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ interface ICalculatorService extends IInterface   │ │
│  │                                                    │ │
│  │  int add(int a, int b);                           │ │
│  │  int multiply(int a, int b);                      │ │
│  │  oneway void logOperation(String op);             │ │
│  │                                                    │ │
│  │  ┌────────────────────────────────────────────┐   │ │
│  │  │ abstract class Stub extends Binder          │   │ │
│  │  │   implements ICalculatorService             │   │ │
│  │  │                                              │   │ │
│  │  │   // Серверная сторона                       │   │ │
│  │  │   onTransact(code, data, reply, flags)      │   │ │
│  │  │                                              │   │ │
│  │  │   asInterface(IBinder):                     │   │ │
│  │  │     same process → cast to Stub             │   │ │
│  │  │     cross-process → new Proxy(binder)       │   │ │
│  │  │                                              │   │ │
│  │  │  ┌──────────────────────────────────────┐   │   │ │
│  │  │  │ class Proxy implements                │   │   │ │
│  │  │  │   ICalculatorService                  │   │   │ │
│  │  │  │                                        │   │   │ │
│  │  │  │   // Клиентская сторона               │   │   │ │
│  │  │  │   add(a, b) {                         │   │   │ │
│  │  │  │     Parcel data, reply;               │   │   │ │
│  │  │  │     data.writeInt(a);                 │   │   │ │
│  │  │  │     data.writeInt(b);                 │   │   │ │
│  │  │  │     mRemote.transact(CODE_ADD,        │   │   │ │
│  │  │  │       data, reply, 0);                │   │   │ │
│  │  │  │     return reply.readInt();           │   │   │ │
│  │  │  │   }                                   │   │   │ │
│  │  │  └──────────────────────────────────────┘   │   │ │
│  │  └────────────────────────────────────────────┘   │ │
│  └──────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘
```

**Шаг 3: Реализация Service**

```kotlin
// === Service (сервер) ===
class CalculatorService : Service() {

    // Реализация AIDL интерфейса
    private val binder = object : ICalculatorService.Stub() {

        // ⚠️ Вызывается из Binder thread pool!
        // Нужна thread-safety!
        override fun add(a: Int, b: Int): Int {
            return a + b
        }

        override fun multiply(a: Int, b: Int): Int {
            return a * b
        }

        override fun logOperation(operation: String?) {
            // oneway — вызывается асинхронно
            // Клиент не ждёт результата
            Log.d("Calculator", "Операция: $operation")
        }
    }

    override fun onBind(intent: Intent?): IBinder {
        return binder
    }
}
```

**Шаг 4: Клиент**

```kotlin
// === Activity (клиент) ===
class CalculatorActivity : AppCompatActivity() {

    private var calculatorService: ICalculatorService? = null
    private var isBound = false

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
            // Stub.asInterface() — ключевой метод:
            // - Тот же процесс: вернёт прямую ссылку на Stub (без IPC overhead)
            // - Другой процесс: вернёт Proxy (с полным IPC через Binder)
            calculatorService = ICalculatorService.Stub.asInterface(service)
            isBound = true
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            calculatorService = null
            isBound = false
        }
    }

    override fun onStart() {
        super.onStart()
        val intent = Intent(this, CalculatorService::class.java)
        bindService(intent, connection, Context.BIND_AUTO_CREATE)
    }

    override fun onStop() {
        super.onStop()
        if (isBound) {
            unbindService(connection)
            isBound = false
        }
    }

    fun calculate() {
        if (!isBound) return

        // ⚠️ IPC вызов — может быть медленным!
        // НЕ вызывать на Main Thread для тяжёлых операций
        lifecycleScope.launch(Dispatchers.IO) {
            try {
                val sum = calculatorService?.add(2, 3)
                val product = calculatorService?.multiply(4, 5)

                withContext(Dispatchers.Main) {
                    showResult("Сумма: $sum, Произведение: $product")
                }
            } catch (e: RemoteException) {
                // Сервис недоступен (процесс убит)
                withContext(Dispatchers.Main) {
                    showError("Сервис недоступен")
                }
            }
        }

        // oneway вызов — не блокирует
        calculatorService?.logOperation("add(2, 3)")
    }

    private fun showResult(text: String) { /* UI */ }
    private fun showError(text: String) { /* UI */ }
}
```

#### КАК РАБОТАЕТ: Binder IPC Flow

```
┌──────────────────────────────────┐   ┌──────────────────────────────────┐
│         PROCESS A (Client)        │   │         PROCESS B (Service)       │
│                                    │   │                                    │
│  ┌──────────────────────────────┐ │   │ ┌──────────────────────────────┐  │
│  │     Client Code               │ │   │ │     AIDL Stub Implementation │  │
│  │                                │ │   │ │                                │  │
│  │  service.add(2, 3)            │ │   │ │  override fun add(a, b): Int │  │
│  │     │                         │ │   │ │     return a + b              │  │
│  │     ▼                         │ │   │ │         ▲                      │  │
│  │  Proxy.add(2, 3)             │ │   │ │         │                      │  │
│  │     │                         │ │   │ │  Stub.onTransact()            │  │
│  │     │  1. Parcel data         │ │   │ │     │                          │  │
│  │     │     writeInt(2)         │ │   │ │     │  5. Parcel data          │  │
│  │     │     writeInt(3)         │ │   │ │     │     readInt() → 2        │  │
│  │     │                         │ │   │ │     │     readInt() → 3        │  │
│  │     │  2. transact(           │ │   │ │     │                          │  │
│  │     │       CODE_ADD,         │ │   │ │     │  6. Вызов add(2, 3)     │  │
│  │     │       data,             │ │   │ │     │     result = 5           │  │
│  │     │       reply,            │ │   │ │     │                          │  │
│  │     │       flags)            │ │   │ │     │  7. Parcel reply         │  │
│  │     │        │                │ │   │ │     │     writeInt(5)          │  │
│  └─────┼────────┼────────────────┘ │   │ └─────┼─────────────────────────┘  │
│        │        │                  │   │       │                            │
└────────┼────────┼──────────────────┘   └───────┼────────────────────────────┘
         │        │                              │
         │        ▼          KERNEL SPACE         │
         │  ┌─────────────────────────────────────┼──┐
         │  │        BINDER DRIVER                │   │
         │  │        /dev/binder                   │   │
         │  │                                      │   │
         │  │  3. Копирование Parcel data ─────────┘   │
         │  │     из process A → process B              │
         │  │     (mmap — одна копия вместо двух)       │
         │  │                                           │
         │  │  4. Пробуждение Binder thread             │
         │  │     в process B                            │
         │  │                                           │
         │  │  8. Копирование Parcel reply              │
         │  │     из process B → process A              │
         │  │                                           │
         │  └───────────────────────────────────────────┘
         │
         │  9. Proxy.add() возвращает reply.readInt() → 5
         ▼
      result = 5
```

**Ключевые моменты Binder IPC:**

1. **Proxy** сериализует аргументы в `Parcel` (data)
2. **transact()** отправляет Parcel через Binder driver в ядре
3. **Binder driver** копирует данные через mmap (одна копия вместо двух)
4. **Binder thread** в целевом процессе просыпается
5. **Stub.onTransact()** десериализует Parcel и вызывает реальную реализацию
6. Результат сериализуется в reply Parcel и возвращается через Binder driver
7. **Proxy** десериализует reply и возвращает результат клиенту

**Stub.asInterface() — ключевой метод:**

```kotlin
// Сгенерированный код (упрощённо)
abstract class Stub : Binder(), ICalculatorService {

    companion object {
        fun asInterface(binder: IBinder?): ICalculatorService? {
            if (binder == null) return null

            // Проверяем: тот же процесс?
            val localInterface = binder.queryLocalInterface(DESCRIPTOR)
            if (localInterface != null && localInterface is ICalculatorService) {
                // ТОТ ЖЕ ПРОЦЕСС: возвращаем прямую ссылку (без IPC!)
                return localInterface
            }

            // ДРУГОЙ ПРОЦЕСС: возвращаем Proxy для IPC через Binder
            return Proxy(binder)
        }
    }
}
```

#### ПОДВОДНЫЕ КАМНИ: thread-safety в AIDL

```kotlin
// ❌ ПРОБЛЕМА: AIDL Stub вызывается из Binder thread pool — несколько потоков одновременно!
class UnsafeService : Service() {

    private var count = 0 // ⚠️ Race condition!

    private val binder = object : IMyService.Stub() {
        override fun increment(): Int {
            count++ // НЕ thread-safe!
            return count
        }
    }

    override fun onBind(intent: Intent?): IBinder = binder
}

// ✅ РЕШЕНИЕ 1: synchronized
class SafeService : Service() {

    private var count = 0
    private val lock = Any()

    private val binder = object : IMyService.Stub() {
        override fun increment(): Int {
            synchronized(lock) {
                count++
                return count
            }
        }
    }

    override fun onBind(intent: Intent?): IBinder = binder
}

// ✅ РЕШЕНИЕ 2: AtomicInteger
class AtomicService : Service() {

    private val count = AtomicInteger(0)

    private val binder = object : IMyService.Stub() {
        override fun increment(): Int {
            return count.incrementAndGet()
        }
    }

    override fun onBind(intent: Intent?): IBinder = binder
}
```

**TransactionTooLargeException:**

```kotlin
// ❌ ПРОБЛЕМА: передача >1MB данных через Binder
// Binder transaction buffer ограничен ~1MB (на весь процесс!)

// IMyService.aidl:
// List<Parcelable> getLargeData();

// Реализация:
override fun getLargeData(): List<MyData> {
    return generateHugeList() // >1MB → TransactionTooLargeException!
}

// ✅ РЕШЕНИЕ: пагинация или передача через файл/ContentProvider
override fun getDataPage(offset: Int, limit: Int): List<MyData> {
    return getData().drop(offset).take(limit) // Пагинация
}

// ✅ РЕШЕНИЕ 2: передача ParcelFileDescriptor для больших данных
override fun getLargeDataFd(): ParcelFileDescriptor {
    val file = writeDataToFile()
    return ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
}
```

---

## 4. Service Process Priority и LMK

### ЧТО: как LMK решает, какие процессы убить

Low Memory Killer (LMK) использует oom_adj_score для определения приоритета процессов. Значение Service и его связей с другими компонентами влияет на приоритет.

### КАК РАБОТАЕТ: иерархия приоритетов

```
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESS PRIORITY HIERARCHY                    │
│                   (от высокого к низкому приоритету)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  1. FOREGROUND PROCESS (oom_adj = 0)                    ВЫСШИЙ   │
│     ├── Activity в foreground (onResume)                          │
│     ├── Service в startForeground()                               │
│     ├── BroadcastReceiver выполняет onReceive()                   │
│     └── Bound Service, привязанный к foreground Activity         │
│                                                                   │
│  2. VISIBLE PROCESS (oom_adj = 100)                              │
│     ├── Activity видима, но не в фокусе (onPause)                │
│     └── Bound Service, привязанный к visible Activity            │
│                                                                   │
│  3. SERVICE PROCESS (oom_adj = 500)                              │
│     ├── Started Service без foreground                            │
│     └── Работал <30 минут                                        │
│                                                                   │
│  4. CACHED (BACKGROUND) PROCESS (oom_adj = 900+)       НИЗШИЙ   │
│     ├── Activity в background (onStop)                            │
│     ├── Started Service, работающий >30 минут                    │
│     └── Кандидат на убийство при нехватке памяти                 │
│                                                                   │
│  LMK убивает процессы от НИЗШЕГО к ВЫСШЕМУ приоритету           │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### КАК ПРИМЕНЯТЬ: влияние Service на приоритет процесса

| Тип Service | Приоритет процесса | Вероятность убийства | Когда применимо |
|---|---|---|---|
| Foreground Service (startForeground) | Foreground (0) | Очень низкая | Музыка, навигация, звонки |
| Bound Service к foreground Activity | Foreground (0) | Очень низкая | Активное взаимодействие |
| Bound Service к visible Activity | Visible (100) | Низкая | Фоновое обновление видимого UI |
| Started Service (<30 мин) | Service (500) | Средняя | Фоновая загрузка, обработка |
| Started Service (>30 мин) | Cached (900+) | Высокая | Длительные фоновые задачи |
| Background (после unbind, без start) | Cached (900+) | Очень высокая | Кандидат на немедленное убийство |

```kotlin
// Повышение приоритета через foreground
class ImportantService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // ✅ Повышаем приоритет: Service process → Foreground process
        val notification = buildNotification()
        startForeground(NOTIFICATION_ID, notification)

        // Теперь LMK не убьёт этот процесс (пока есть свободная память)
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// Bound Service наследует приоритет клиента
// Если Activity (foreground) привязана к Service →
// процесс Service получает foreground приоритет
```

### ПОДВОДНЫЕ КАМНИ

```kotlin
// ❌ ПРОБЛЕМА: Started Service без foreground убивается через ~30 минут
class LongRunningService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            // Задача на 2 часа
            performLongTask() // Система убьёт процесс!
        }.start()
        return START_STICKY // Пересоздастся, но потеряет прогресс
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// ✅ РЕШЕНИЕ 1: Foreground Service
class LongRunningFGS : Service() {
    override fun onCreate() {
        super.onCreate()
        startForeground(1, buildNotification())
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            performLongTask() // Безопасно — foreground process
            stopSelf()
        }.start()
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// ✅ РЕШЕНИЕ 2: WorkManager для задач, которые могут быть прерваны
val workRequest = OneTimeWorkRequestBuilder<LongTaskWorker>()
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .build()
    )
    .build()

WorkManager.getInstance(context).enqueue(workRequest)
```

---

## 5. Service vs WorkManager vs Coroutines: Decision Tree

### ASCII Decision Tree

```
                        ┌──────────────────────────┐
                        │ Нужна фоновая работа?     │
                        └──────────┬───────────────┘
                                   │
                        ┌──────────▼───────────────┐
                        │ Нужно ли пережить         │
                        │ процесс/перезагрузку?     │
                        └──────────┬───────────────┘
                                   │
                    ┌──────────────┼──────────────────┐
                    │ ДА           │                    │ НЕТ
                    ▼              │                    ▼
          ┌─────────────────┐     │         ┌─────────────────────┐
          │ Задача может     │     │         │ Короткая async       │
          │ быть отложена?   │     │         │ задача while app     │
          └────────┬────────┘     │         │ visible?             │
                   │               │         └────────┬────────────┘
          ┌────────┼──────┐       │                   │
          │ ДА     │       │ НЕТ  │         ┌─────────┼──────────┐
          ▼        │       ▼      │         │ ДА      │           │ НЕТ
   ┌──────────┐   │  ┌─────────┐ │         ▼         │           ▼
   │WORKMANAGER│   │  │ FGS +   │ │   ┌──────────┐   │   ┌──────────────┐
   │           │   │  │WorkMgr  │ │   │COROUTINES│   │   │Continuous     │
   │Periodic/  │   │  │(hybrid) │ │   │          │   │   │real-time      │
   │one-time   │   │  └─────────┘ │   │lifecycle-│   │   │(music, GPS)? │
   │constraints│   │              │   │Scope /   │   │   └──────┬───────┘
   └──────────┘   │              │   │viewModel-│   │          │
                   │              │   │Scope     │   │   ┌──────▼───────┐
                   │              │   └──────────┘   │   │  FOREGROUND   │
                   │              │                   │   │  SERVICE      │
                   │              │                   │   └──────────────┘
                   │              │                   │
                   │              │                   │
                   └──────────────┘                   │
                                                      │
                                                      │
   ┌──────────────────────────────────────────────────┘
   │
   ▼
   Периодическая задача с constraints?
      ДА → WorkManager (PeriodicWorkRequest)
      НЕТ → Coroutines в ViewModel/Repository
```

### Таблица сравнения

| Критерий | Coroutines | WorkManager | Foreground Service |
|---|---|---|---|
| **Переживает процесс** | Нет | Да | Да (пока работает) |
| **Переживает перезагрузку** | Нет | Да | Нет |
| **Constraints (сеть, зарядка)** | Нет | Да | Нет (ручная проверка) |
| **Periodic** | Нет (ручной repeat) | Да (PeriodicWorkRequest) | Нет (ручной scheduling) |
| **Уведомление обязательно** | Нет | Нет (опционально) | Да |
| **Приоритет процесса** | Зависит от хоста | Background/Expedited | Foreground (высший) |
| **Отмена** | cancel() / scope | cancelById/Tag | stopSelf/stopService |
| **Макс. время** | Пока жив scope | ~10 мин (обычный), без лимита (long-running) | Нет (кроме dataSync 6ч) |
| **Use case** | In-process async, UI-bound | Persistent, deferrable | Continuous, user-visible |
| **API Level** | Kotlin 1.3+ | API 14+ (Jetpack) | API 26+ (обязательный) |

### Примеры выбора

```kotlin
// 1. Загрузка данных для отображения на экране
//    → Coroutines (lifecycleScope / viewModelScope)
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = withContext(Dispatchers.IO) {
                repository.fetchData()
            }
            _uiState.value = data
        }
        // Автоматическая отмена при onCleared()
    }
}

// 2. Синхронизация данных с сервером (может быть отложена)
//    → WorkManager
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 1, repeatIntervalTimeUnit = TimeUnit.HOURS
).setConstraints(
    Constraints.Builder()
        .setRequiredNetworkType(NetworkType.CONNECTED)
        .setRequiresCharging(false)
        .build()
).build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork("sync", ExistingPeriodicWorkPolicy.KEEP, syncWork)

// 3. Воспроизведение музыки в фоне
//    → Foreground Service (mediaPlayback)
class MusicPlaybackService : Service() {
    override fun onCreate() {
        super.onCreate()
        startForeground(
            NOTIFICATION_ID,
            buildMediaNotification(),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
        )
    }
    // Воспроизведение продолжается даже когда приложение в фоне
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        handlePlaybackCommand(intent)
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// 4. GPS-навигация
//    → Foreground Service (location)
class NavigationService : Service() {
    override fun onCreate() {
        super.onCreate()
        startForeground(
            NOTIFICATION_ID,
            buildNavNotification(),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
        )
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startLocationUpdates()
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// 5. Загрузка файла с гарантией завершения
//    → WorkManager + CoroutineWorker
class DownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val url = inputData.getString("url") ?: return Result.failure()

        // Показываем FGS notification для долгой работы
        setForeground(createForegroundInfo("Загрузка..."))

        return try {
            downloadFile(url)
            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry()
            else Result.failure()
        }
    }

    private fun createForegroundInfo(text: String): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, CHANNEL_ID)
            .setContentTitle("Загрузка")
            .setContentText(text)
            .setSmallIcon(R.drawable.ic_download)
            .build()

        return ForegroundInfo(NOTIFICATION_ID, notification)
    }
}
```

---

## 6. Background Execution Limits (Android 8+)

### ЧТО: эволюция ограничений

| Версия Android | API | Ограничение | Решение |
|---|---|---|---|
| Android 8 (Oreo) | 26 | Background Services убиваются через минуты | startForegroundService() |
| Android 8 | 26 | Implicit BroadcastReceiver ограничены | Explicit receiver или JobScheduler |
| Android 10 | 29 | Restrictions on Activity starts from background | Notification + PendingIntent |
| Android 12 | 31 | FGS нельзя запускать из фона | WorkManager, исключения |
| Android 13 | 33 | POST_NOTIFICATIONS permission | Runtime permission request |
| Android 14 | 34 | foregroundServiceType обязателен | Указать тип в манифесте |
| Android 14 | 34 | BOOT_COMPLETED не может запускать некоторые FGS | WorkManager для boot tasks |
| Android 15 | 35 | dataSync FGS ограничен 6 часами | onTimeout(), WorkManager |
| Android 15 | 35 | SYSTEM_ALERT_WINDOW больше не даёт FGS exemption | Альтернативные подходы |

### КАК РАБОТАЕТ: Android 8 Background Execution Limits

```kotlin
// До Android 8 (API <26): background service работал неограниченно
// Android 8+: background service убивается через ~1 минуту после ухода в фон

// Приложение считается в "фоне" когда:
// 1. Нет visible Activity
// 2. Нет foreground Service
// 3. Приложение не в списке "foreground" компонентов

// ❌ CRASH на Android 8+ из фона:
context.startService(intent) // IllegalStateException!

// ✅ Правильно:
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
    context.startForegroundService(intent) // + вызвать startForeground() за 5 сек
} else {
    context.startService(intent)
}

// ✅ Универсально (AndroidX):
ContextCompat.startForegroundService(context, intent)
```

### КАК РАБОТАЕТ: Android 12 Background FGS Restrictions

```kotlin
// Android 12+: ForegroundServiceStartNotAllowedException
// Нельзя запускать FGS из фона кроме специальных случаев

// МОЖНО запускать FGS из фона:
// 1. Из high-priority FCM push
// 2. По action из уведомления
// 3. Из AlarmManager exact alarm (с USE_EXACT_ALARM)
// 4. Из предоставленного SYSTEM_ALERT_WINDOW (Android <15)
// 5. Companion device manager
// 6. Из widget onClick

// ✅ Рекомендуемый подход: WorkManager вместо FGS из фона
class BackgroundSyncReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // ❌ НЕ запускаем FGS из BroadcastReceiver на Android 12+
        // context.startForegroundService(serviceIntent) // CRASH!

        // ✅ Используем WorkManager
        val syncWork = OneTimeWorkRequestBuilder<SyncWorker>()
            .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
            .build()
        WorkManager.getInstance(context).enqueue(syncWork)
    }
}
```

### ПОДВОДНЫЕ КАМНИ

**1. BOOT_COMPLETED + FGS на Android 14:**

```kotlin
// ❌ Android 14: BOOT_COMPLETED не может запускать некоторые FGS types
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // ❌ Может не работать на Android 14+ для dataSync FGS
            // ContextCompat.startForegroundService(context, serviceIntent)

            // ✅ ПРАВИЛЬНО: WorkManager
            val bootWork = OneTimeWorkRequestBuilder<BootTaskWorker>()
                .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
                .build()
            WorkManager.getInstance(context).enqueue(bootWork)
        }
    }
}
```

**2. Тестирование background restrictions:**

```kotlin
// ADB команды для тестирования
// Поместить приложение в standby bucket (ограничения)
// adb shell am set-standby-bucket com.example.app rare

// Проверить текущий standby bucket
// adb shell am get-standby-bucket com.example.app

// Имитировать device idle (Doze)
// adb shell dumpsys deviceidle force-idle

// Вывести из idle
// adb shell dumpsys deviceidle unforce
```

---

## Мифы и заблуждения

### Миф 1: "Service работает в отдельном потоке"

**НЕПРАВИЛЬНО!** Service работает на Main Thread процесса.

```kotlin
class MyService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Этот код выполняется на MAIN THREAD!
        val threadName = Thread.currentThread().name // "main"

        // Тяжёлая работа здесь → ANR через 5 секунд!
        // Thread.sleep(10_000) // ❌ ANR!

        // ✅ Тяжёлую работу — в отдельный поток
        Thread {
            performHeavyWork()
            stopSelf()
        }.start()

        return START_NOT_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### Миф 2: "Service — это отдельный процесс"

**НЕПРАВИЛЬНО!** По умолчанию Service работает в том же процессе, что и Activity. Отдельный процесс нужно указывать явно:

```xml
<!-- По умолчанию: тот же процесс что и Application -->
<service android:name=".MyService" />

<!-- Отдельный процесс: явное указание -->
<service
    android:name=".IsolatedService"
    android:process=":remote" />
```

### Миф 3: "START_STICKY гарантирует мгновенный рестарт"

**НЕПРАВИЛЬНО!** START_STICKY говорит системе "пересоздай Service когда будут ресурсы". Рестарт может произойти через секунды, минуты или вообще не произойти (если устройство в экстремальной нехватке памяти).

```kotlin
// START_STICKY: система ПОПЫТАЕТСЯ пересоздать Service
// Но нет гарантий по времени!
// На некоторых OEM (Xiaomi, Huawei) — агрессивное убийство, рестарт может не произойти

override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    // intent может быть null при рестарте (START_STICKY)!
    val url = intent?.getStringExtra("url") // ⚠️ null при рестарте!

    return START_STICKY
}
```

### Миф 4: "Foreground Service может работать без уведомления"

**НЕПРАВИЛЬНО** с Android 8 (API 26)! Foreground Service обязан иметь уведомление. Без уведомления `startForeground()` бросит exception.

```kotlin
// ❌ Нельзя скрыть уведомление Foreground Service
// На Android 13+ пользователь может отключить уведомления,
// но SERVICE всё равно ПРОДОЛЖИТ РАБОТАТЬ

// Минимальное уведомление:
val notification = NotificationCompat.Builder(this, channelId)
    .setContentTitle("Работа в фоне")
    .setSmallIcon(R.drawable.ic_service) // ОБЯЗАТЕЛЬНО!
    .setPriority(NotificationCompat.PRIORITY_LOW)
    .setSilent(true) // Без звука
    .build()

startForeground(1, notification)
```

### Миф 5: "WorkManager заменяет все Service"

**НЕПРАВИЛЬНО!** WorkManager НЕ подходит для:

```kotlin
// ❌ WorkManager НЕ для real-time задач
// - Воспроизведение музыки → Foreground Service (mediaPlayback)
// - VoIP звонки → Foreground Service (phoneCall)
// - GPS-навигация → Foreground Service (location)
// - Запись видео → Foreground Service (camera)

// ✅ WorkManager для:
// - Синхронизация данных с сервером
// - Загрузка файлов (с retry)
// - Обработка изображений
// - Периодические задачи (cleanup, backup)
// - Отправка аналитики
```

### Миф 6: "bindService() держит Service живым бесконечно"

**НЕПРАВИЛЬНО!** Bound Service живёт пока жив его клиент. Если Activity уничтожена — unbind автоматический → Service может быть уничтожен.

```kotlin
// Activity leaks ServiceConnection → Service продолжает работать
// Но если Activity убита системой → система автоматически unbind

// ⚠️ Однако: если забыли unbindService() → ServiceConnectionLeaked warning
// и потенциальная утечка памяти

override fun onStop() {
    super.onStop()
    // ОБЯЗАТЕЛЬНО unbind!
    if (isBound) {
        unbindService(connection)
        isBound = false
    }
}
```

### Миф 7: "onServiceDisconnected() вызывается при unbindService()"

**НЕПРАВИЛЬНО!** `onServiceDisconnected()` вызывается **ТОЛЬКО** при неожиданном отключении (crash сервиса, убийство процесса). При штатном `unbindService()` этот callback НЕ вызывается.

```kotlin
private val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName?, service: IBinder?) {
        // Вызывается при успешной привязке
    }

    override fun onServiceDisconnected(name: ComponentName?) {
        // ⚠️ Вызывается ТОЛЬКО при crash/kill Service!
        // НЕ вызывается при unbindService()!
        // Используйте для reconnect логики
    }
}
```

### Миф 8: "IntentService — лучший способ для фоновой работы"

**НЕПРАВИЛЬНО!** IntentService deprecated с API 30 (Android 11). Замена:

```kotlin
// ❌ DEPRECATED: IntentService
class MyIntentService : IntentService("MyIntentService") {
    override fun onHandleIntent(intent: Intent?) {
        // Выполняется в HandlerThread (background)
    }
}

// ✅ ЗАМЕНА 1: WorkManager + CoroutineWorker
class MyWorker(context: Context, params: WorkerParameters) :
    CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        // Выполняется в background
        return Result.success()
    }
}

// ✅ ЗАМЕНА 2: JobIntentService (тоже deprecated в пользу WorkManager)
// ✅ ЗАМЕНА 3: Coroutines в обычном Service
class ModernService : Service() {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        scope.launch {
            handleWork(intent)
            stopSelf(startId)
        }
        return START_NOT_STICKY
    }

    override fun onDestroy() {
        super.onDestroy()
        scope.cancel()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

### Миф 9: "AIDL нужен для общения между Service и Activity в одном приложении"

**НЕПРАВИЛЬНО!** Если Service и Activity в одном процессе (по умолчанию) — используйте Local Binder. AIDL нужен только для межпроцессного взаимодействия.

```kotlin
// Тот же процесс → Local Binder (проще и быстрее)
inner class LocalBinder : Binder() {
    fun getService(): MyService = this@MyService
}

// Разные процессы → AIDL или Messenger
// <service android:process=":remote" /> ← только тогда нужен AIDL
```

### Миф 10: "Service.onDestroy() всегда вызывается"

**НЕПРАВИЛЬНО!** Если процесс убит LMK — `onDestroy()` НЕ вызывается. Не полагайтесь на `onDestroy()` для критичной очистки.

```kotlin
class MyService : Service() {
    override fun onDestroy() {
        super.onDestroy()
        // ⚠️ Этот код может НЕ выполниться если процесс убит!
        saveImportantData() // Данные могут быть потеряны!
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            performWork()
            // ✅ Сохраняйте прогресс ВО ВРЕМЯ работы, не только в onDestroy()
            saveProgressIncrementally()
            stopSelf(startId)
        }.start()
        return START_REDELIVER_INTENT
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

---

## CS-фундамент

### Client-Server Pattern

Service реализует классическую клиент-серверную архитектуру:
- **Bound Service** = сервер, предоставляющий API через IBinder
- **Activity/Fragment** = клиент, вызывающий методы сервера
- **ServiceConnection** = установление соединения клиент-сервер
- **AIDL** = IDL (Interface Definition Language) — стандартный способ описания API в distributed systems

### IPC (Inter-Process Communication)

Android Binder — высокопроизводительный IPC механизм:
- **Binder driver** в ядре Linux (`/dev/binder`)
- **mmap** для zero-copy transfer (одна копия вместо двух)
- **Binder thread pool** для параллельной обработки запросов
- Аналогия: gRPC / CORBA / D-Bus в мире Linux

### Proxy Pattern

AIDL генерирует классический Proxy pattern:
- **Stub** — серверная реализация интерфейса
- **Proxy** — клиентская обёртка, которая маршалит вызовы через Binder
- **Stub.asInterface()** — фабричный метод: same process = direct, cross-process = proxy
- Аналогия: RPC stubs, Java RMI, gRPC generated code

### Observer Pattern

ServiceConnection реализует Observer pattern:
- **Subject** = система (ActivityManagerService)
- **Observer** = ServiceConnection
- **Events**: onServiceConnected(), onServiceDisconnected()
- Асинхронное уведомление: bindService() возвращает void, результат приходит через callback

### Reference Counting

Bound Service использует reference counting для lifecycle:
- Каждый `bindService()` увеличивает счётчик
- Каждый `unbindService()` уменьшает счётчик
- Когда счётчик = 0 → `onUnbind()` → `onDestroy()`
- Аналогия: shared_ptr в C++, ARC в Swift/Objective-C

### Command Pattern

Started Service реализует Command pattern:
- **Command** = Intent (содержит action + data)
- **Invoker** = startService(intent)
- **Receiver** = Service.onStartCommand()
- Каждый вызов startService() — отдельная команда
- `startId` — уникальный идентификатор команды

### Service Locator Pattern

Android использует Service Locator для системных сервисов:
- `context.getSystemService(Context.NOTIFICATION_SERVICE)` → NotificationManager
- `context.getSystemService(Context.ALARM_SERVICE)` → AlarmManager
- Централизованный реестр сервисов в SystemServiceRegistry
- Аналогия: JNDI, Spring ApplicationContext, Dagger

### Process Priority

LMK (Low Memory Killer) реализует priority-based scheduling:
- **oom_adj_score** — числовой приоритет процесса (0 = высший, 999 = низший)
- Foreground Service повышает oom_adj процесса до foreground уровня
- Аналогия: nice/renice в Unix, Thread.setPriority() в Java
- OOM Killer в Linux kernel — прародитель Android LMK

---

## Проверь себя

### Вопрос 1: В каком потоке выполняется onStartCommand()?

<details>
<summary>Ответ</summary>

`onStartCommand()` выполняется на **Main Thread** (UI Thread) процесса приложения. Service — это НЕ отдельный поток и НЕ отдельный процесс. Все lifecycle callbacks Service (onCreate, onStartCommand, onBind, onDestroy) вызываются на Main Thread.

Поэтому тяжёлую работу нужно выносить в отдельный поток:

```kotlin
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    // ❌ Тяжёлая работа здесь → ANR через 5 секунд!

    // ✅ Правильно: фоновый поток или корутины
    CoroutineScope(Dispatchers.IO).launch {
        performHeavyWork()
        stopSelf(startId)
    }

    return START_NOT_STICKY
}
```

</details>

### Вопрос 2: Чем отличаются START_STICKY и START_REDELIVER_INTENT?

<details>
<summary>Ответ</summary>

Оба значения говорят системе пересоздать Service после убийства, но отличаются тем, какой Intent передаётся при рестарте:

- **START_STICKY**: Service пересоздаётся, `onStartCommand()` вызывается с `intent = null`. Используется когда Service не зависит от входных данных (например, музыкальный плеер — возобновляет воспроизведение без конкретного Intent).

- **START_REDELIVER_INTENT**: Service пересоздаётся, `onStartCommand()` вызывается с **последним полученным Intent**. Используется когда входные данные критичны (например, загрузка файла — URL передаётся в Intent).

```kotlin
// START_STICKY: intent == null при рестарте
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    val url = intent?.getStringExtra("url") // null при рестарте!
    return START_STICKY
}

// START_REDELIVER_INTENT: intent == последний intent при рестарте
override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
    val url = intent?.getStringExtra("url") // тот же URL при рестарте!
    return START_REDELIVER_INTENT
}
```

</details>

### Вопрос 3: Когда Hybrid Service уничтожается?

<details>
<summary>Ответ</summary>

Hybrid Service (одновременно Started и Bound) уничтожается только когда выполнены **ОБА** условия:

1. Service был остановлен (`stopSelf()` или `stopService()`)
2. **И** все клиенты отвязались (`unbindService()` для каждого клиента)

Пока хотя бы одно из условий не выполнено — Service продолжает работать.

```
Started + Bound → оба активны → Service работает
stopSelf() вызван → Started завершён, но клиенты привязаны → Service работает
Последний клиент unbind → Started завершён И Bound завершён → onDestroy()
```

Это логическое AND: `destroyed = stopped AND (bindCount == 0)`.

</details>

### Вопрос 4: Что произойдёт если не вызвать startForeground() за 5 секунд?

<details>
<summary>Ответ</summary>

Если после вызова `startForegroundService()` не вызвать `startForeground()` в течение 5 секунд, система:

1. На Android 8-11: выбросит ANR (Application Not Responding)
2. На Android 12+: выбросит `ForegroundServiceDidNotStartInTimeException` и процесс будет убит

```kotlin
// ❌ ПРОБЛЕМА: startForeground() вызывается слишком поздно
class BadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Thread {
            Thread.sleep(6000) // >5 секунд!
            startForeground(1, notification) // ПОЗДНО → ANR/Crash
        }.start()
        return START_STICKY
    }
    override fun onBind(intent: Intent?): IBinder? = null
}

// ✅ РЕШЕНИЕ: startForeground() сразу в onCreate() или начале onStartCommand()
class GoodService : Service() {
    override fun onCreate() {
        super.onCreate()
        startForeground(1, createNotification()) // Сразу!
    }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Теперь можно спокойно работать
        return START_STICKY
    }
    override fun onBind(intent: Intent?): IBinder? = null
}
```

</details>

### Вопрос 5: Чем Local Binder отличается от AIDL в контексте производительности?

<details>
<summary>Ответ</summary>

**Local Binder** (тот же процесс):
- Прямой вызов метода — как обычный вызов функции в Java/Kotlin
- Нет сериализации/десериализации (нет Parcel)
- Нет копирования данных через Binder driver
- Нет переключения контекста (context switch)
- Производительность = обычный вызов метода

**AIDL** (межпроцессный):
- Proxy сериализует аргументы в Parcel
- Данные копируются через Binder driver в ядре (mmap)
- Context switch между процессами
- Stub десериализует Parcel в целевом процессе
- Binder thread pool — нужна thread-safety
- Производительность: ~10-100x медленнее прямого вызова

Ключевой момент: `Stub.asInterface()` автоматически определяет — тот же процесс или нет. Если тот же — возвращает прямую ссылку (без IPC overhead). Если другой — возвращает Proxy.

```kotlin
// asInterface() внутри:
fun asInterface(binder: IBinder?): IMyService? {
    val local = binder?.queryLocalInterface(DESCRIPTOR)
    if (local is IMyService) {
        return local // Тот же процесс → прямая ссылка (быстро)
    }
    return Proxy(binder) // Другой процесс → IPC через Binder (медленнее)
}
```

</details>

### Вопрос 6: Почему onServiceDisconnected() не вызывается при unbindService()?

<details>
<summary>Ответ</summary>

`onServiceDisconnected()` вызывается **ТОЛЬКО** при неожиданном отключении:
- Процесс Service был убит системой (LMK)
- Service crashed (uncaught exception)
- Процесс Service завершился аномально

При штатном вызове `unbindService()` этот callback **НЕ вызывается**. Это design decision Android — `unbindService()` — это осознанное действие клиента, а `onServiceDisconnected()` — уведомление о проблеме.

Для очистки ресурсов после `unbindService()` используйте:

```kotlin
override fun onStop() {
    super.onStop()
    if (isBound) {
        // Очищаем ссылку на service ПЕРЕД unbind
        myService = null
        isBound = false
        unbindService(connection)
    }
}
```

Если нужен reconnect при неожиданном отключении:

```kotlin
override fun onServiceDisconnected(name: ComponentName?) {
    myService = null
    isBound = false
    // Попытка reconnect
    Handler(Looper.getMainLooper()).postDelayed({
        bindService(intent, connection, BIND_AUTO_CREATE)
    }, 5000)
}
```

</details>

---

## Связи

### [[android-app-components]]
Service — один из 4 основных компонентов Android (Activity, Service, BroadcastReceiver, ContentProvider). Все компоненты управляются ActivityManagerService через Binder IPC. Понимание lifecycle других компонентов помогает понять, как Service взаимодействует с Activity (binding), BroadcastReceiver (запуск через intent) и ContentProvider (доступ к данным).

### [[android-background-work]]
Service — один из механизмов фоновой работы, но НЕ единственный. Важно знать полную картину: Coroutines (in-process), WorkManager (persistent), AlarmManager (exact timing), JobScheduler (system-optimized). Service нужен только когда задача continuous и user-visible (музыка, навигация).

### [[android-process-memory]]
LMK (Low Memory Killer) определяет приоритет процесса на основе компонентов внутри него. Foreground Service повышает приоритет до foreground. Понимание oom_adj_score и процессных приоритетов критично для выбора между Service и другими механизмами.

### [[android-context-internals]]
Service наследует от Context. ApplicationContext vs Service Context — разные объекты. Service Context нужен для bindService(), startForeground(). При создании notification channel нужен именно Service Context. Утечка Service Context = утечка всего Service.

### [[android-handler-looper]]
Service работает на Main Thread = Looper + Handler. Messenger IPC построен на Handler + Message. IntentService (deprecated) использовал HandlerThread внутри. Понимание Handler-Looper триады критично для работы с Messenger и понимания, почему Service callbacks блокируют Main Thread.

### [[android-intent-internals]]
Intent — механизм запуска Service (startService, bindService). Intent содержит action + data + extras. Explicit Intent (указываем класс) vs Implicit Intent (указываем action). На Android 5+ implicit intent для bindService() запрещён. PendingIntent используется для запуска Service из notification actions.

---

## Источники

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [Android Developers: Services overview](https://developer.android.com/develop/background-work/services) | Документация | Официальное руководство по Service lifecycle |
| 2 | [Android Developers: Bound Services](https://developer.android.com/develop/background-work/services/bound-services) | Документация | Local Binder, Messenger, AIDL |
| 3 | [Android Developers: Foreground Service Types](https://developer.android.com/develop/background-work/services/fgs/service-types) | Документация | Полный список FGS types и permissions |
| 4 | [Android Developers: Android 14 FGS Types Required](https://developer.android.com/about/versions/14/changes/fgs-types-required) | Документация | Android 14 breaking changes |
| 5 | [Android Developers: Android 15 FGS Changes](https://developer.android.com/about/versions/15/changes/foreground-service-types) | Документация | dataSync 6h limit, onTimeout() |
| 6 | [Android Developers: AIDL](https://developer.android.com/develop/background-work/services/aidl) | Документация | Официальное руководство по AIDL |
| 7 | [ProAndroidDev: Android Binder Mechanism](https://proandroiddev.com/android-binder-mechanism-the-backbone-of-ipc-in-android-6cfc279eb046) | Статья | Binder IPC internals, Proxy/Stub |
| 8 | [Medium: AIDL and Binder IPC Inside AOSP](https://medium.com/@anuragsingh7238/aidl-android-interface-definition-language-how-binder-ipc-works-inside-aosp-19465655bd00) | Статья | AIDL compiler, AOSP internals |
| 9 | [Android Developers: Background Tasks Overview](https://developer.android.com/develop/background-work/background-tasks) | Документация | Decision tree: Service vs WorkManager |
| 10 | [Medium: Guide to Foreground Services](https://medium.com/@domen.lanisnik/guide-to-foreground-services-on-android-9d0127dc8f9a) | Статья | Практическое руководство по FGS |
| 11 | [DeveloperLife: Android Component Lifecycles](https://developerlife.com/2017/07/09/android-o-n-and-below-component-lifecycles-and-background-tasks/) | Статья | Deep dive в lifecycle компонентов |
| 12 | [Medium: Foreground Service vs WorkManager](https://medium.com/@amar90aqi/foreground-service-vs-workmanager-in-android-choosing-the-right-tool-for-background-tasks-32c1242f9898) | Статья | Сравнение FGS и WorkManager |
| 13 | [Android Developers: WorkManager](https://developer.android.com/topic/libraries/architecture/workmanager) | Документация | WorkManager как замена Service |
| 14 | [Android Source: ActivityManagerService](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/services/core/java/com/android/server/am/ActiveServices.java) | Исходный код | Service management в AOSP |

---

*Проверено: 2026-01-27 — Педагогический контент проверен*
