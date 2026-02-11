---
title: "Фоновая работа: история ограничений, WorkManager, Foreground Services"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [process-scheduling, power-management, job-scheduling, constraint-satisfaction]
tags:
  - topic/android
  - topic/background-processing
  - type/deep-dive
  - level/advanced
related:
  - "[[android-overview]]"
  - "[[android-app-components]]"
  - "[[android-process-memory]]"
  - "[[android-threading]]"
  - "[[android-async-evolution]]"
  - "[[android-executors]]"
  - "[[android-service-internals]]"
prerequisites:
  - "[[android-app-components]]"
  - "[[android-threading]]"
  - "[[android-activity-lifecycle]]"
---

# Фоновая работа: история ограничений, WorkManager, Foreground Services

Фоновая работа в Android — это область, которая **радикально изменилась** за последние 10 лет. То, что работало в Android 5.0, может быть полностью заблокировано в Android 15. Google постепенно закручивал гайки, реагируя на жалобы пользователей о батарее и производительности. Понимание этой истории критически важно для выбора правильного подхода.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android-приложений и их lifecycle
> - [[android-activity-lifecycle]] — почему background работа нужна когда Activity уничтожена
> - [[os-processes-threads]] — потоки и процессы на уровне ОС
> - [[kotlin-coroutines]] — корутины для асинхронной работы (рекомендуется)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Doze Mode** | Системный режим глубокого сна для экономии батареи (Android 6.0+) |
| **App Standby** | Ограничения для неиспользуемых приложений (Android 6.0+) |
| **App Standby Buckets** | Категории приложений с разными ограничениями (Android 9+) |
| **WorkManager** | Jetpack API для отложенной фоновой работы (рекомендуемый) |
| **Foreground Service** | Service с уведомлением, видимым пользователю |
| **JobScheduler** | Системный API для планирования задач (API 21+) |
| **Expedited Work** | Срочная работа в WorkManager с повышенным приоритетом |

---

## Хронология ограничений: как Google закручивал гайки

### Проблема: "Android жрёт батарею"

До Android 6.0 разработчики могли делать в фоне практически всё что угодно. Результат был катастрофическим для пользователей:

```
┌─────────────────────────────────────────────────────────────────┐
│              ЧТО ПРОИСХОДИЛО ДО ANDROID 6.0                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Пользователь кладёт телефон и идёт спать                      │
│                                                                 │
│  00:00  Батарея: 100%                                           │
│  00:05  Facebook: startService() → синхронизация                │
│  00:07  Twitter: AlarmManager → проверка уведомлений            │
│  00:10  Gmail: startService() → проверка почты                  │
│  00:12  WhatsApp: startService() → синхронизация                │
│  00:15  Instagram: AlarmManager → обновление ленты              │
│  00:20  Facebook: опять синхронизация                           │
│  ...    100+ приложений будят телефон каждые 5-10 минут         │
│  06:00  Батарея: 40%                                            │
│                                                                 │
│  Причина: каждое приложение работало независимо, без            │
│  координации. CPU не мог уйти в глубокий сон.                   │
│                                                                 │
│  Обзоры в Play Store: "★☆☆☆☆ Android убивает батарею!"         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Google понял, что нужны жёсткие системные ограничения. Началась эпоха "закручивания гаек".

---

### Android 6.0 Marshmallow (API 23) — 2015: Doze Mode и App Standby

**Что изменилось:**

Google ввёл два механизма для борьбы с фоновой активностью:

**Doze Mode** — системное состояние глубокого сна:
- Активируется когда устройство: экран выключен + не на зарядке + неподвижно
- В Doze: сеть заблокирована, wakelocks игнорируются, alarms и jobs откладываются
- Периодические "maintenance windows" (окна обслуживания) позволяют выполнить накопившуюся работу
- Чем дольше устройство в Doze, тем реже окна (экспоненциальный рост интервалов)

```
┌─────────────────────────────────────────────────────────────────┐
│                    DOZE MODE: КАК ЭТО РАБОТАЕТ                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Время:    00:00   01:00   02:00   03:00   04:00   05:00        │
│            ─────┬──────┬────────┬──────────────┬────────        │
│                 │      │        │              │                │
│  Doze:     ████ │ ████ │ ██████ │ ████████████ │ ████████       │
│            Deep │ Deep │ Deep   │ Deep         │ Deep           │
│                 │      │        │              │                │
│  Maintenance:   ▼      ▼        ▼              ▼                │
│            ─────────────────────────────────────────────        │
│                                                                 │
│  Интервалы между maintenance windows растут:                    │
│  15 мин → 30 мин → 1 час → 2 часа → 4 часа...                   │
│                                                                 │
│  В maintenance window:                                          │
│  - Выполняются отложенные jobs                                  │
│  - Доставляются отложенные alarms                              │
│  - Доступна сеть                                               │
│  - Все приложения обрабатываются одновременно (batching)        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**App Standby** — ограничения для неиспользуемых приложений:
- Если пользователь не взаимодействовал с приложением несколько дней
- Сеть ограничена до 1 раза в день
- Jobs и syncs откладываются

**Что продолжало работать:**
- Foreground Services (с уведомлением)
- High-priority FCM (Firebase Cloud Messaging)
- AlarmManager.setExactAndAllowWhileIdle() — но только несколько раз в час

**Влияние на разработчиков:**
- Нельзя было полагаться на точное время выполнения фоновых задач
- Пришлось использовать FCM для важных уведомлений вместо polling
- Начали использовать JobScheduler вместо AlarmManager для не-срочных задач

---

### Android 7.0 Nougat (API 24) — 2016: Doze-on-the-Go

**Что изменилось:**

Google расширил Doze Mode:
- **Doze-on-the-Go**: облегчённый Doze активируется даже когда устройство движется
- Раньше нужно было "неподвижно лежать", теперь достаточно "экран выключен + не на зарядке"
- Implicit broadcasts ограничены: CONNECTIVITY_ACTION больше не доставляется в manifest receivers

**Почему убрали CONNECTIVITY_ACTION:**

```kotlin
// ❌ До Android 7.0 — это будило ВСЕ приложения при изменении сети
// AndroidManifest.xml
<receiver android:name=".NetworkReceiver">
    <intent-filter>
        <action android:name="android.net.conn.CONNECTIVITY_CHANGE"/>
    </intent-filter>
</receiver>

// Проблема: 100 приложений с таким receiver = 100 процессов стартуют
// при каждом подключении/отключении WiFi

// ✅ Android 7.0+ — регистрация только программно, пока приложение живо
class MyActivity : Activity() {
    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            // Сеть доступна
        }
    }

    override fun onStart() {
        connectivityManager.registerDefaultNetworkCallback(networkCallback)
    }

    override fun onStop() {
        connectivityManager.unregisterNetworkCallback(networkCallback)
    }
}
```

---

### Android 8.0 Oreo (API 26) — 2017: Background Execution Limits

**Переломный момент.** Это был самый радикальный релиз в плане ограничений. Google фактически "убил" традиционные background services.

**Что изменилось:**

1. **Background Services убиты:**
   - Если приложение в фоне, startService() выбрасывает IllegalStateException
   - Даже если service уже запущен, он будет убит через ~1 минуту после ухода приложения в фон
   - START_STICKY больше не помогает — service всё равно убивается

```kotlin
// ❌ Больше не работает на Android 8.0+ (targetSdk 26+)
class MySyncService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        thread {
            syncData() // Эта работа будет прервана через ~1 минуту
        }
        return START_STICKY // Не поможет — service убьют
    }
}

// Вызов из фона:
context.startService(Intent(context, MySyncService::class.java))
// Результат: IllegalStateException на Android 8.0+
```

2. **Implicit Broadcast Receivers ограничены:**
   - Большинство implicit broadcasts не доставляются receivers, объявленным в manifest
   - ACTION_PACKAGE_REPLACED, ACTION_NEW_OUTGOING_CALL и другие — больше не работают через manifest
   - Только несколько исключений: BOOT_COMPLETED, LOCALE_CHANGED и др.

3. **Background Location ограничен:**
   - Приложения в фоне получают location updates значительно реже (несколько раз в час)

**Рекомендуемые альтернативы:**

| Было | Стало (Android 8.0+) |
|------|----------------------|
| startService() в фоне | JobScheduler / WorkManager |
| Постоянный background service | Foreground Service (с уведомлением) |
| Implicit broadcast в manifest | Программная регистрация или explicit broadcasts |
| Polling в service | FCM + WorkManager |

---

### Android 9 Pie (API 28) — 2018: App Standby Buckets

**Что изменилось:**

Google ввёл более гранулярную систему ограничений — **App Standby Buckets**. Вместо бинарного "используется/не используется" появилось 5 категорий:

```
┌─────────────────────────────────────────────────────────────────┐
│                    APP STANDBY BUCKETS                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ACTIVE (Активный)                                              │
│  ─────────────────                                              │
│  Приложение сейчас используется или использовалось только что   │
│  • Foreground activity                                          │
│  • Foreground service запущен                                   │
│  • Пользователь нажал на уведомление                           │
│  Ограничения: НЕТ                                               │
│                                                                 │
│  WORKING SET (Рабочий набор)                                    │
│  ───────────────────────────                                    │
│  Приложение используется регулярно, но не прямо сейчас          │
│  • Запускается каждый день                                      │
│  Ограничения: МЯГКИЕ (отложенные jobs)                          │
│                                                                 │
│  FREQUENT (Частое использование)                                │
│  ────────────────────────────                                   │
│  Приложение используется часто, но не каждый день               │
│  • Запускается несколько раз в неделю                          │
│  Ограничения: СРЕДНИЕ (jobs отложены дольше, alarms реже)       │
│                                                                 │
│  RARE (Редкое использование)                                    │
│  ──────────────────────────                                     │
│  Приложение используется редко                                  │
│  • Запускается раз в месяц                                      │
│  Ограничения: СТРОГИЕ (сеть ограничена, jobs раз в день)        │
│                                                                 │
│  RESTRICTED (Ограниченный) — добавлен в Android 12              │
│  ─────────────────────────                                      │
│  Система считает приложение проблемным                          │
│  • Потребляет много ресурсов                                    │
│  • Пользователь редко взаимодействует                          │
│  Ограничения: МАКСИМАЛЬНЫЕ (jobs раз в день в 10-мин окне)      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Конкретные лимиты по bucket'ам:**

| Bucket | Jobs | Alarms | Network |
|--------|------|--------|---------|
| Active | Без ограничений | Без ограничений | Без ограничений |
| Working Set | Отложены до 2 часов | До 6 в час | Без ограничений |
| Frequent | Отложены до 8 часов | До 2 в час | Без ограничений |
| Rare | Отложены до 24 часов | До 2 в день | До 1 раза в день |
| Restricted | 1 раз в день (10-мин окно) | 1 в день | Раз в день |

**Важно:** производители устройств могут менять критерии присвоения bucket'ов. Samsung, Xiaomi, Huawei добавляют собственные ограничения поверх стандартных Android.

---

### Android 10 (API 29) — 2019: Background Location и Foreground Service Types

**Что изменилось:**

1. **ACCESS_BACKGROUND_LOCATION** — новое отдельное разрешение:
   - До Android 10: ACCESS_FINE_LOCATION давало доступ к GPS везде
   - Android 10+: для доступа к GPS в фоне нужно отдельное разрешение
   - Пользователь должен явно разрешить "Allow all the time"

2. **Foreground Service Types** (начало):
   - Foreground services с location должны указывать android:foregroundServiceType="location"

```xml
<!-- AndroidManifest.xml -->
<service
    android:name=".LocationService"
    android:foregroundServiceType="location">
</service>
```

---

### Android 11 (API 30) — 2020: Deprecated APIs

**Что изменилось:**

1. **AsyncTask deprecated:**
   - AsyncTask был проблемным с момента создания (утечки памяти, crashes при rotation)
   - Google официально deprecated его
   - Рекомендация: Kotlin Coroutines или java.util.concurrent

2. **IntentService deprecated:**
   - IntentService не имел смысла после background execution limits Android 8.0
   - Рекомендация: WorkManager для большинства случаев

3. **Foreground Service Type для камеры/микрофона:**
   - Services использующие камеру/микрофон должны указывать соответствующий type

---

### Android 12 (API 31) — 2021: Exact Alarms и Restricted Bucket

**Что изменилось:**

1. **SCHEDULE_EXACT_ALARM требует разрешения:**
   - Раньше любое приложение могло устанавливать точные alarms
   - Теперь нужно разрешение + пользователь может отключить в настройках

```kotlin
// Проверка разрешения (Android 12+)
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    val alarmManager = getSystemService<AlarmManager>()
    if (!alarmManager.canScheduleExactAlarms()) {
        // Направить пользователя в настройки
        startActivity(Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM))
    }
}
```

2. **Restricted bucket** добавлен в App Standby Buckets (см. выше)

3. **Expedited Work в WorkManager 2.7.0:**
   - Новый способ запуска срочной работы
   - Заменяет foreground services для коротких задач

---

### Android 14 (API 34) — 2023: Foreground Service Types обязательны

**Переломный момент для Foreground Services.**

**Что изменилось:**

Все Foreground Services ОБЯЗАНЫ указывать тип. Без типа — crash.

**Доступные типы:**

| Тип | Использование | Разрешение |
|-----|---------------|------------|
| camera | Запись видео, фото в фоне | FOREGROUND_SERVICE_CAMERA |
| connectedDevice | Bluetooth, USB устройства | FOREGROUND_SERVICE_CONNECTED_DEVICE |
| dataSync | Синхронизация данных | FOREGROUND_SERVICE_DATA_SYNC |
| health | Фитнес-трекеры | FOREGROUND_SERVICE_HEALTH |
| location | GPS-навигация | FOREGROUND_SERVICE_LOCATION |
| mediaPlayback | Музыка, подкасты | FOREGROUND_SERVICE_MEDIA_PLAYBACK |
| mediaProjection | Запись экрана | FOREGROUND_SERVICE_MEDIA_PROJECTION |
| microphone | Запись звука | FOREGROUND_SERVICE_MICROPHONE |
| phoneCall | VoIP звонки | FOREGROUND_SERVICE_PHONE_CALL |
| remoteMessaging | SMS на другом устройстве | FOREGROUND_SERVICE_REMOTE_MESSAGING |
| shortService | Короткие задачи (<3 мин) | Не требуется |
| specialUse | Особые случаи | FOREGROUND_SERVICE_SPECIAL_USE |
| systemExempted | Системные приложения | — |

```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_LOCATION"/>

<service
    android:name=".NavigationService"
    android:foregroundServiceType="location">
</service>
```

```kotlin
// Kotlin код
startForeground(
    NOTIFICATION_ID,
    notification,
    ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION
)
```

**Play Console:** Нужно декларировать использование foreground services в Play Console и объяснить зачем они нужны.

---

### Android 15 (API 35) — 2024: dataSync ограничен, новые типы

**Что изменилось:**

1. **dataSync timeout:**
   - Максимум 6 часов работы в течение 24 часов
   - После 6 часов система вызывает onTimeout() — нужно остановить service
   - **dataSync будет deprecated в будущих версиях**

```kotlin
class SyncService : Service() {
    // Android 15+: система вызовет этот метод после 6 часов работы
    override fun onTimeout(startId: Int, fgsType: Int) {
        // Есть несколько секунд чтобы остановить service
        stopSelf(startId)
    }
}
```

2. **Новый тип mediaProcessing:**
   - Для конвертации медиа-файлов
   - Тоже ограничен 6 часами в 24-часовом периоде

3. **BOOT_COMPLETED ограничения:**
   - Нельзя запускать camera, dataSync, mediaPlayback, phoneCall foreground services из BOOT_COMPLETED receiver
   - Нужно использовать WorkManager для отложенного запуска

**Рекомендуемая миграция с dataSync:**

| Сценарий | Альтернатива |
|----------|--------------|
| Передача данных по сети по запросу пользователя | User-Initiated Data Transfer Jobs |
| Периодическая синхронизация | WorkManager |
| Короткая критическая задача | shortService foreground type |

---

## Эволюция API для фоновой работы

### Deprecated APIs: что НЕ использовать

```
┌─────────────────────────────────────────────────────────────────┐
│              DEPRECATED: НЕ ИСПОЛЬЗУЙТЕ                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AsyncTask (deprecated API 30)                                  │
│  ─────────────────────────────                                  │
│  Проблемы:                                                      │
│  • Утечки памяти (ссылка на Activity)                          │
│  • Crash при повороте экрана                                   │
│  • Не переживает смерть процесса                               │
│  • Нет гарантии выполнения                                     │
│  Замена: Kotlin Coroutines, WorkManager                         │
│                                                                 │
│  IntentService (deprecated API 30)                              │
│  ─────────────────────────────────                              │
│  Проблемы:                                                      │
│  • Убивается на Android 8.0+ через ~1 минуту                   │
│  • Не работает в фоне                                          │
│  Замена: WorkManager                                            │
│                                                                 │
│  JobIntentService (deprecated)                                  │
│  ────────────────────────────                                   │
│  Был временным решением между IntentService и WorkManager       │
│  Замена: WorkManager                                            │
│                                                                 │
│  AlarmManager для не-срочных задач                              │
│  ────────────────────────────────                               │
│  Проблемы:                                                      │
│  • Требует SCHEDULE_EXACT_ALARM на Android 12+                 │
│  • Не учитывает Doze, battery optimization                     │
│  Замена: WorkManager (для не-срочных), AlarmManager (только     │
│  для реальных будильников)                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### JobScheduler: низкоуровневый API

JobScheduler (API 21+) — системный API для планирования задач. WorkManager использует его внутри на API 23+.

**Когда использовать напрямую:**
- Нужны API недоступные в WorkManager (setPrefetch, setUserInitiated)
- Очень специфичные требования к планированию

**Когда НЕ использовать:**
- На API 21-22 есть серьёзные баги
- Много boilerplate кода
- Нет автоматического retry и backoff
- Не переживает reboot без дополнительного кода

```kotlin
// JobScheduler — много boilerplate
class SyncJobService : JobService() {
    override fun onStartJob(params: JobParameters): Boolean {
        thread {
            try {
                syncData()
                jobFinished(params, false) // false = не нужен reschedule
            } catch (e: Exception) {
                jobFinished(params, true) // true = нужен reschedule
            }
        }
        return true // работа выполняется асинхронно
    }

    override fun onStopJob(params: JobParameters): Boolean {
        // Система хочет остановить job
        return true // true = reschedule
    }
}

// Планирование
val jobScheduler = getSystemService<JobScheduler>()
val job = JobInfo.Builder(JOB_ID, ComponentName(this, SyncJobService::class.java))
    .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
    .setPersisted(true) // переживает reboot
    .build()
jobScheduler.schedule(job)
```

---

## WorkManager: рекомендуемое решение

### Почему WorkManager, а не JobScheduler напрямую

| Критерий | JobScheduler | WorkManager |
|----------|--------------|-------------|
| Минимальный API | 21 (баги до 23) | 14 (через fallback) |
| Boilerplate | Много | Минимум |
| Цепочки задач | Нет | Да |
| Уникальные задачи | Ручная реализация | ExistingWorkPolicy |
| Наблюдение за статусом | Нет | LiveData/Flow |
| Тестирование | Сложно | TestWorkerBuilder |
| Retry с backoff | Ручная реализация | Встроенный |
| Hilt интеграция | Нет | @HiltWorker |

### Как WorkManager работает внутри

```
┌─────────────────────────────────────────────────────────────────┐
│                    WORKMANAGER INTERNALS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WorkManager автоматически выбирает backend:                    │
│                                                                 │
│  API 23+ (Android 6.0+)                                         │
│  └─→ JobScheduler                                               │
│      • Системный сервис                                         │
│      • Оптимизирован для батареи                                │
│      • Учитывает Doze и App Standby                            │
│                                                                 │
│  API 14-22 (старые устройства)                                  │
│  └─→ AlarmManager + BroadcastReceiver                           │
│      • Fallback для старых устройств                           │
│      • Менее эффективен                                        │
│                                                                 │
│  Хранение:                                                      │
│  └─→ SQLite database                                            │
│      • Задачи переживают reboot                                │
│      • Переживают убийство процесса                            │
│      • Room под капотом                                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Практическое использование

```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.work:work-runtime-ktx:2.9.0")

    // Для Hilt
    implementation("androidx.hilt:hilt-work:1.1.0")
    ksp("androidx.hilt:hilt-compiler:1.1.0")
}
```

```kotlin
// Worker с Hilt
@HiltWorker
class SyncWorker @AssistedInject constructor(
    @Assisted context: Context,
    @Assisted params: WorkerParameters,
    private val repository: DataRepository,  // Инжектируется через Hilt
    private val analytics: Analytics
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        return try {
            // Получаем input data
            val userId = inputData.getString("user_id")
                ?: return Result.failure()

            // Выполняем работу
            val data = repository.syncUserData(userId)

            // Возвращаем output data
            val output = workDataOf("synced_items" to data.size)
            Result.success(output)

        } catch (e: IOException) {
            // Сетевая ошибка — повторить позже
            analytics.logError("sync_network_error", e)
            Result.retry()

        } catch (e: Exception) {
            // Фатальная ошибка — не повторять
            analytics.logError("sync_fatal_error", e)
            Result.failure()
        }
    }
}
```

### Constraints: когда выполнять

```kotlin
val constraints = Constraints.Builder()
    .setRequiredNetworkType(NetworkType.CONNECTED)     // Нужен интернет
    .setRequiresBatteryNotLow(true)                    // Не на низком заряде
    .setRequiresCharging(false)                        // Не обязательно на зарядке
    .setRequiresStorageNotLow(true)                    // Достаточно места
    .setRequiresDeviceIdle(false)                      // Не обязательно idle
    .build()

val request = OneTimeWorkRequestBuilder<SyncWorker>()
    .setConstraints(constraints)
    .setInputData(workDataOf("user_id" to "123"))
    .setBackoffCriteria(
        BackoffPolicy.EXPONENTIAL,  // 30s → 60s → 120s → ...
        WorkRequest.MIN_BACKOFF_MILLIS,
        TimeUnit.MILLISECONDS
    )
    .addTag("sync")
    .build()

WorkManager.getInstance(context)
    .enqueueUniqueWork(
        "user_sync_123",
        ExistingWorkPolicy.REPLACE,  // Заменить существующую
        request
    )
```

### Expedited Work: срочная работа

Для срочных задач, которые должны начаться немедленно:

```kotlin
val expeditedRequest = OneTimeWorkRequestBuilder<UrgentWorker>()
    .setExpedited(OutOfQuotaPolicy.RUN_AS_NON_EXPEDITED_WORK_REQUEST)
    .build()

WorkManager.getInstance(context).enqueue(expeditedRequest)
```

**Ограничения Expedited Work:**
- Квота на количество expedited работ в день
- Если квота исчерпана, OutOfQuotaPolicy определяет поведение
- Не для долгих задач (предназначено для коротких срочных операций)

### Periodic Work: периодические задачи

```kotlin
// Минимальный интервал — 15 минут
val periodicRequest = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 1,
    repeatIntervalTimeUnit = TimeUnit.HOURS,
    flexTimeInterval = 15,  // Окно гибкости: ±15 минут
    flexTimeIntervalUnit = TimeUnit.MINUTES
)
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.UNMETERED) // Только WiFi
            .build()
    )
    .build()

WorkManager.getInstance(context)
    .enqueueUniquePeriodicWork(
        "hourly_sync",
        ExistingPeriodicWorkPolicy.UPDATE,  // Обновить существующую
        periodicRequest
    )
```

---

## Foreground Services: когда WorkManager не подходит

### Когда использовать Foreground Service

Foreground Service нужен когда:
1. **Пользователь осознаёт, что что-то происходит** — музыка играет, навигация работает
2. **Задача должна выполняться непрерывно** — не может быть отложена системой
3. **Задача долгая и не может быть разбита** — загрузка большого файла

### Когда НЕ использовать Foreground Service

- Периодическая синхронизация → WorkManager
- Отправка аналитики → WorkManager
- Любая отложенная работа → WorkManager
- Короткие задачи по событию → WorkManager с Expedited

### Реализация (Android 14+)

```xml
<!-- AndroidManifest.xml -->
<uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
<uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK"/>
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>

<service
    android:name=".MusicService"
    android:foregroundServiceType="mediaPlayback"
    android:exported="false">
</service>
```

```kotlin
class MusicService : Service() {

    private val binder = MusicBinder()
    private var mediaPlayer: MediaPlayer? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startMusic(intent.getStringExtra(EXTRA_TRACK_URL)!!)
            ACTION_STOP -> stopMusic()
        }
        return START_NOT_STICKY
    }

    private fun startMusic(url: String) {
        // КРИТИЧНО: вызвать в первые 5 секунд после startForegroundService()
        val notification = createNotification()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(
                NOTIFICATION_ID,
                notification,
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            )
        } else {
            startForeground(NOTIFICATION_ID, notification)
        }

        mediaPlayer = MediaPlayer().apply {
            setDataSource(url)
            prepareAsync()
            setOnPreparedListener { start() }
        }
    }

    private fun createNotification(): Notification {
        // Создаём notification channel (Android 8+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Music Playback",
                NotificationManager.IMPORTANCE_LOW  // LOW = без звука
            )
            notificationManager.createNotificationChannel(channel)
        }

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Playing Music")
            .setContentText("Artist - Track Name")
            .setSmallIcon(R.drawable.ic_music)
            .setOngoing(true)  // Нельзя смахнуть
            .addAction(R.drawable.ic_pause, "Pause", pausePendingIntent)
            .addAction(R.drawable.ic_stop, "Stop", stopPendingIntent)
            .setStyle(
                androidx.media.app.NotificationCompat.MediaStyle()
                    .setShowActionsInCompactView(0, 1)
            )
            .build()
    }

    private fun stopMusic() {
        mediaPlayer?.release()
        mediaPlayer = null
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    override fun onBind(intent: Intent): IBinder = binder

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    companion object {
        const val ACTION_START = "start"
        const val ACTION_STOP = "stop"
        const val EXTRA_TRACK_URL = "track_url"
        private const val NOTIFICATION_ID = 1
        private const val CHANNEL_ID = "music_playback"
    }
}
```

### shortService: для коротких критических задач

Новый тип в Android 14 для задач до 3 минут:

```kotlin
// Короткий foreground service — без специального разрешения
class QuickSyncService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        startForeground(
            NOTIFICATION_ID,
            createNotification(),
            ServiceInfo.FOREGROUND_SERVICE_TYPE_SHORT_SERVICE
        )

        // Должен завершиться за 3 минуты!
        serviceScope.launch {
            try {
                quickSync()
            } finally {
                stopForeground(STOP_FOREGROUND_REMOVE)
                stopSelf()
            }
        }

        return START_NOT_STICKY  // SHORT_SERVICE не поддерживает sticky
    }

    // Система вызовет если превысим 3 минуты
    override fun onTimeout(startId: Int, fgsType: Int) {
        stopSelf(startId)
    }
}
```

**Ограничения shortService:**
- Максимум ~3 минуты работы
- Нельзя START_STICKY
- Нельзя запустить другой foreground service из shortService

---

## Тестирование в условиях Doze и ограничений

### ADB команды для тестирования

```bash
# Проверить текущий bucket приложения
adb shell am get-standby-bucket com.example.myapp

# Установить bucket вручную
adb shell am set-standby-bucket com.example.myapp active
adb shell am set-standby-bucket com.example.myapp rare
adb shell am set-standby-bucket com.example.myapp restricted

# Принудительно включить Doze
adb shell dumpsys deviceidle force-idle

# Симулировать maintenance window
adb shell dumpsys deviceidle step

# Выключить Doze
adb shell dumpsys deviceidle unforce

# Показать статус Doze
adb shell dumpsys deviceidle

# Показать все pending jobs
adb shell dumpsys jobscheduler

# Показать WorkManager jobs
adb shell dumpsys jobscheduler | grep -A 20 "WorkManager"
```

### Тестирование WorkManager

```kotlin
@RunWith(AndroidJUnit4::class)
class SyncWorkerTest {

    private lateinit var context: Context

    @Before
    fun setup() {
        context = ApplicationProvider.getApplicationContext()

        // Инициализация WorkManager для тестов
        val config = Configuration.Builder()
            .setMinimumLoggingLevel(Log.DEBUG)
            .setExecutor(SynchronousExecutor())
            .build()

        WorkManagerTestInitHelper.initializeTestWorkManager(context, config)
    }

    @Test
    fun syncWorker_succeeds_withNetwork() {
        // Arrange
        val request = OneTimeWorkRequestBuilder<SyncWorker>()
            .setInputData(workDataOf("user_id" to "123"))
            .build()

        val workManager = WorkManager.getInstance(context)
        val testDriver = WorkManagerTestInitHelper.getTestDriver(context)!!

        // Act
        workManager.enqueue(request).result.get()

        // Симулируем выполнение constraints
        testDriver.setAllConstraintsMet(request.id)

        // Assert
        val workInfo = workManager.getWorkInfoById(request.id).get()
        assertThat(workInfo.state).isEqualTo(WorkInfo.State.SUCCEEDED)
    }
}
```

---

## Выбор решения: Decision Tree

```
┌─────────────────────────────────────────────────────────────────┐
│           КАКОЕ РЕШЕНИЕ ВЫБРАТЬ ДЛЯ ФОНОВОЙ РАБОТЫ?              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Пользователь ЖДЁТ результат прямо сейчас?                      │
│  (загрузка данных при открытии экрана)                          │
│  │                                                              │
│  ├─ ДА → Coroutines в ViewModel                                 │
│  │       viewModelScope.launch { ... }                          │
│  │                                                              │
│  └─ НЕТ → Задача должна выполниться НЕМЕДЛЕННО?                 │
│           │                                                     │
│           ├─ ДА → Пользователь осознаёт что происходит?         │
│           │       (музыка, навигация, большая загрузка)         │
│           │       │                                             │
│           │       ├─ ДА → Foreground Service                    │
│           │       │                                             │
│           │       └─ НЕТ → Короткая задача (<3 мин)?            │
│           │               │                                     │
│           │               ├─ ДА → shortService или              │
│           │               │       WorkManager Expedited         │
│           │               │                                     │
│           │               └─ НЕТ → WorkManager                  │
│           │                                                     │
│           └─ НЕТ → Задача может подождать?                      │
│                   (синхронизация, аналитика, backup)            │
│                   │                                             │
│                   ├─ ДА → WorkManager                           │
│                   │       OneTimeWorkRequest или                │
│                   │       PeriodicWorkRequest                   │
│                   │                                             │
│                   └─ Нужно ТОЧНОЕ время?                        │
│                       (будильник, напоминание)                  │
│                       │                                         │
│                       ├─ ДА → AlarmManager                      │
│                       │       setExactAndAllowWhileIdle()       │
│                       │       (требует разрешение на Android 12+)│
│                       │                                         │
│                       └─ НЕТ → WorkManager                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Чеклист

```
□ Понимаю историю ограничений и почему они введены
□ Не использую deprecated APIs (AsyncTask, IntentService)
□ WorkManager для отложенных/периодических задач
□ Foreground Service только когда пользователь осознаёт работу
□ startForeground() в первые 5 секунд
□ foregroundServiceType указан для всех Foreground Services (API 34+)
□ Constraints для экономии батареи
□ Тестирую в Doze mode и разных standby buckets
□ FCM для push-уведомлений (не polling)
□ Unique work для избежания дубликатов
□ Expedited work для срочных коротких задач
□ Учитываю ограничения разных вендоров (Samsung, Xiaomi)
```

---

## Проверь себя

<details>
<summary>1. Когда использовать WorkManager, а когда Coroutines?</summary>

**Ответ:**
- **Coroutines/Threads:** Работа привязана к UI, отменяется когда пользователь уходит с экрана. Пример: загрузка данных для отображения.
- **WorkManager:** Работа должна завершиться даже если приложение убито. Пример: синхронизация с сервером, загрузка файла.

Правило: если пользователь ждёт результата прямо сейчас — coroutines. Если результат нужен "когда-нибудь" — WorkManager.

</details>

<details>
<summary>2. Почему Foreground Service требует notification?</summary>

**Ответ:** Android требует notification чтобы пользователь знал, что приложение работает в фоне и потребляет ресурсы. Это прозрачность перед пользователем. Без notification система может убить сервис. С Android 14+ нужно указывать тип foreground service (location, mediaPlayback и т.д.).

</details>

<details>
<summary>3. Чем WorkManager лучше AlarmManager + BroadcastReceiver?</summary>

**Ответ:** WorkManager:
- **Constraints:** Выполнить когда есть сеть, батарея заряжена и т.д.
- **Chaining:** Последовательные/параллельные задачи
- **Retry:** Автоматические повторы с backoff
- **Compatibility:** Работает на всех версиях Android, выбирает лучший способ (JobScheduler, AlarmManager)
- **Observability:** LiveData/Flow для отслеживания статуса

AlarmManager — низкоуровневый, всё это делать вручную.

</details>

<details>
<summary>4. Что такое Doze mode и как он влияет на background work?</summary>

**Ответ:** Doze mode — режим энергосбережения когда устройство не используется. В Doze:
- Network access заблокирован
- AlarmManager отложен
- Wake locks игнорируются

WorkManager с constraints будет ждать выхода из Doze. Для срочных задач — setExpedited() или foreground service (с ограничениями). Никакой обход Doze не рекомендуется — это вредит батарее пользователя.

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Coroutines заменили WorkManager" | Разные инструменты для разных задач. Coroutines — in-process async. WorkManager — guaranteed execution после смерти процесса |
| "Service = background work" | Service не гарантирует выполнение. Система может убить процесс. Для гарантии: WorkManager или Foreground Service с notification |
| "Foreground Service всегда работает" | Android 14+ ограничивает типы Foreground Services. Только определённые use cases (location, mediaPlayback). Остальное → WorkManager |
| "WorkManager медленный" | WorkManager schedules work, не выполняет сам. Для срочных задач: setExpedited(). Латентность от системного scheduling |
| "AlarmManager точнее WorkManager" | WorkManager использует AlarmManager/JobScheduler под капотом. setExact() AlarmManager игнорируется в Doze. Нет преимущества |
| "Wake locks решают проблему Doze" | Wake locks частично работают, но не в Deep Doze. Злоупотребление wake locks = battery drain = плохие отзывы. Не рекомендуется |
| "dataSync Foreground Service для sync" | Android 15 deprecated dataSync type. Используйте WorkManager с setExpedited() или shortService type. Миграция обязательна |
| "Background restrictions обходятся" | Технически возможно, но Google Play Policy violation. Приложение может быть заблокировано. Следуйте guidelines |
| "Периодическая работа = точное время" | PeriodicWorkRequest имеет flex window. Система группирует работы для battery optimization. Минимальный интервал 15 минут |
| "OneTimeWorkRequest для повторяющихся задач" | Можно, но сложнее управлять. PeriodicWorkRequest автоматически reschedules. OneTime требует ручного enqueue в onSuccess |

---

## CS-фундамент

| CS-концепция | Как применяется в Background Work |
|--------------|-----------------------------------|
| **Process Lifecycle** | Android убивает процессы по приоритету. Background процесс = низкий приоритет. WorkManager schedules независимо от процесса |
| **Job Scheduling** | Батчинг задач для энергоэффективности. Система группирует wake ups. Trade-off: latency vs battery |
| **Constraints Satisfaction** | WorkManager выполняет при соблюдении constraints (network, charging). CSP-like scheduling |
| **Retry with Backoff** | ExponentialBackoff при failure. Jitter для избежания thundering herd. Configurable policy |
| **Work Queues** | WorkManager = persistent queue. FIFO, но с приоритетами. Survives process death через SQLite |
| **State Machine** | Work states: ENQUEUED → RUNNING → SUCCEEDED/FAILED/CANCELLED. Observable через LiveData/Flow |
| **Idempotency** | ExistingWorkPolicy: KEEP, REPLACE, APPEND. Важно для unique work при restart |
| **Deferrable Execution** | Deferred не означает когда-нибудь. Система выполнит при первой возможности соблюдения constraints |
| **Power Management** | Doze, App Standby Buckets, Battery Saver. Понимание режимов критично для надёжной работы |
| **Foreground Promotion** | Background → Foreground при критичности. setForegroundAsync() в Worker. Требует notification |

---

## Источники и дальнейшее чтение

**Книги:**
- Meier R. (2022). Professional Android, 4th Edition. — комплексное руководство по Android-разработке, включая Services, WorkManager и background execution limits
- Moskala M. (2022). Kotlin Coroutines: Deep Dive. — корутины и их применение для фоновой работы: CoroutineWorker, viewModelScope, structured concurrency
- Phillips B. et al. (2022). Android Programming: The Big Nerd Ranch Guide, 5th Edition. — практический учебник с разделами по background work и Services

**Веб-ресурсы:**
- [Android Developers: Optimize for Doze and App Standby](https://developer.android.com/training/monitoring-device-state/doze-standby)
- [Android Developers: App Standby Buckets](https://developer.android.com/topic/performance/appstandby)
- [Android Developers: Background Execution Limits](https://developer.android.com/about/versions/oreo/background)
- [Android Developers: Foreground Service Types](https://developer.android.com/develop/background-work/services/fgs/service-types)
- [Android 15 Changes: dataSync Migration](https://developer.android.com/about/versions/15/changes/datasync-migration)

---

## Связь с другими темами

**[[android-activity-lifecycle]]** — когда Activity уходит в background (onStop/onDestroy), все привязанные к ней coroutines в lifecycleScope отменяются. Понимание lifecycle объясняет, почему для длительных задач нужен WorkManager или Foreground Service вместо coroutines в Activity scope. Изучайте lifecycle перед background work.

**[[android-process-memory]]** — Android использует Low Memory Killer для освобождения памяти, убивая фоновые процессы по приоритету. Foreground Service повышает приоритет процесса, защищая его от LMK. Понимание приоритетов процессов критично для выбора правильного механизма фоновой работы и гарантий выполнения.

**[[android-app-components]]** — Service является одним из четырёх компонентов Android и основным механизмом для длительной фоновой работы. Foreground Service требует notification и declaration в манифесте. BroadcastReceiver может инициировать фоновую работу через goAsync() с последующей делегацией в WorkManager.

**[[kotlin-coroutines]]** — coroutines являются основным инструментом для short-lived асинхронных операций (сетевые запросы, DB queries). viewModelScope и lifecycleScope обеспечивают автоматическую отмену при уничтожении компонента. Однако для задач, переживающих процесс, необходим WorkManager с CoroutineWorker.

**[[android-data-persistence]]** — Room + WorkManager — стандартный паттерн для offline-first приложений: данные сохраняются локально в Room, а WorkManager синхронизирует их с сервером при наличии connectivity. Понимание persistence необходимо для проектирования надёжной фоновой синхронизации.

**[[android-networking]]** — сетевые запросы часто выполняются в background, и правильный выбор механизма зависит от требований: coroutines для immediate requests, WorkManager для deferred sync, Foreground Service для long-running uploads/downloads. Constraints в WorkManager (NetworkType.CONNECTED) обеспечивают выполнение только при наличии сети.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

