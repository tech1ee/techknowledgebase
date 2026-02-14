---
title: "Broadcast Internals: механизм рассылки событий в Android"
created: 2026-01-27
modified: 2026-02-13
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/broadcast
  - type/deep-dive
  - level/advanced
related:
  - "[[android-overview]]"
  - "[[android-app-components]]"
  - "[[android-intent-internals]]"
  - "[[android-permissions-security]]"
  - "[[android-background-work]]"
  - "[[android-service-internals]]"
  - "[[android-handler-looper]]"
  - "[[android-process-memory]]"
cs-foundations: [publish-subscribe, observer-pattern, message-queue, event-bus, ordered-delivery, priority-queue, binder-ipc]
prerequisites:
  - "[[android-app-components]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-permissions-security]]"
reading_time: 107
difficulty: 7
study_status: not_started
mastery: 0
last_reviewed:
next_review: 
---

# Broadcast Internals: механизм рассылки событий в Android

> Broadcast — это publish-subscribe система Android для рассылки событий между компонентами и приложениями. От загрузки устройства (BOOT_COMPLETED) до смены locale — всё проходит через BroadcastQueue в system_server. Но ограничения Android 8+ и deprecation LocalBroadcastManager изменили ландшафт: сегодня для internal events используют SharedFlow, а для системных — dynamic registration.

---

## Зачем это нужно

### Проблемы без понимания Broadcast-системы

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| Приложение не получает BOOT_COMPLETED | Manifest receiver + implicit broadcast restrictions (API 26+) | Функциональность не работает после перезагрузки |
| SecurityException на Android 14 | Нет RECEIVER_EXPORTED/NOT_EXPORTED флага | Crash при регистрации receiver |
| ANR в BroadcastReceiver | Обработка > 10 секунд (fg) или > 60 секунд (bg) | ANR dialog, плохой UX |
| LocalBroadcastManager deprecated | Архитектурные проблемы, Intent overhead | Нужна миграция на SharedFlow |
| Broadcast не доставляется cached process | Android 14+ broadcast merging | Пропущенные события, inconsistent state |
| Утечка памяти от receiver | Забыли unregisterReceiver() | Memory leak, IntentReceiverLeaked |
| Broadcast не приходит после updatePackage | Receiver disabled или app in stopped state | Broken post-update initialization |
| Ordered broadcast приходит в неверном порядке | Cross-process priority не гарантирован (Android 16) | Race conditions, данные теряются |

### Актуальность (2025-2026)

```
Эволюция Broadcast-системы:
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  API 1-25:     Свободная регистрация + implicit broadcasts           │
│  API 26 (8.0): Implicit broadcast restrictions для manifest receivers │
│  API 28 (9.0): Background execution limits ужесточены                │
│  API 31 (12):  PendingIntent mutability flags обязательны            │
│  API 33 (13):  POST_NOTIFICATIONS permission                        │
│  API 34 (14):  RECEIVER_EXPORTED / RECEIVER_NOT_EXPORTED обязательны │
│                BroadcastQueueModernImpl (новая реализация очереди)   │
│  API 35 (15):  Cached process broadcast deferral                    │
│  API 36 (16):  Cross-process priority не гарантирован для ordered    │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

- **Android 14**: обязательный `RECEIVER_EXPORTED` / `RECEIVER_NOT_EXPORTED` для dynamic receivers
- **Android 14**: `BroadcastQueueModernImpl` — полная перезапись очереди Broadcast
- **Android 15**: Broadcast deferral для cached processes — broadcast задерживается пока app не выходит из cached
- **Android 16**: priority для ordered broadcasts гарантируется только внутри одного процесса
- **LocalBroadcastManager** deprecated → SharedFlow / StateFlow / EventBus

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| Intent и IntentFilter | Broadcasts используют Intent; matching mechanism | [[android-intent-internals]] |
| 4 компонента Android | BroadcastReceiver — один из 4 компонентов | [[android-app-components]] |
| Permissions | Защита broadcast sender и receiver | [[android-permissions-security]] |
| Background work | Альтернативы broadcast для фоновых задач | [[android-background-work]] |
| Handler/Looper | onReceive() выполняется на main thread через Handler | [[android-handler-looper]] |
| Binder IPC | Broadcast между процессами через Binder | [[android-art-zygote]] |
| Processes и LMK | Broadcast и process priority | [[android-process-memory]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **BroadcastReceiver** | Компонент-получатель событий | Радиоприёмник, настроенный на частоту |
| **BroadcastQueue** | Очередь broadcast в system_server | Очередь сообщений на радиостанции |
| **BroadcastRecord** | Запись об отправленном broadcast с метаданными | Карточка сообщения с адресами получателей |
| **Normal broadcast** | Параллельная доставка всем получателям | Радиопередача — все слышат одновременно |
| **Ordered broadcast** | Последовательная доставка по приоритету | Цепочка телефонных звонков |
| **Implicit broadcast** | Не указан конкретный получатель (только action) | Объявление по громкоговорителю |
| **Explicit broadcast** | Указан конкретный компонент | Личное сообщение адресату |
| **Sticky broadcast** | Broadcast, сохраняемый после доставки (deprecated) | Записка на двери — прочтёт каждый входящий |
| **goAsync()** | Асинхронная обработка в receiver | "Я перезвоню позже" |
| **PendingResult** | Объект для завершения async обработки в receiver | Обещание перезвонить с результатом |
| **RECEIVER_EXPORTED** | Флаг: dynamic receiver доступен извне (Android 14+) | Открытая дверь для гостей |
| **RECEIVER_NOT_EXPORTED** | Флаг: dynamic receiver только для своего приложения | Закрытая дверь — только свои |
| **SharedFlow** | Coroutine-based замена LocalBroadcastManager | Внутренняя рация между отделами |
| **ReceiverDispatcher** | Прокси между system_server и receiver в app process | Секретарь, передающий звонки |
| **InnerReceiver** | Binder-stub в app process для получения broadcast | Телефонная трубка |
| **BroadcastFilter** | Обёртка IntentFilter для dynamic receivers в AMS | Фильтр на частоту радиоприёмника |
| **BroadcastQueueModernImpl** | Новая реализация очереди (Android 14+) | Переезд из старого офиса в современный |

---

## Архитектура Broadcast-системы

### Что такое Broadcast

Broadcast — это механизм publish-subscribe, встроенный в ядро Android. Любой компонент (Activity, Service, другое приложение, system_server) может отправить Intent как broadcast, и все зарегистрированные BroadcastReceiver с подходящим IntentFilter получат его.

```
                    BROADCAST ECOSYSTEM
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌─────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │  System      │     │  App A       │     │  App B       │ │
│  │  (kernel,    │     │              │     │              │ │
│  │   drivers)   │     │  Activity    │     │  Service     │ │
│  └──────┬───────┘     └──────┬───────┘     └──────┬───────┘ │
│         │                    │                    │         │
│         │ sendBroadcast()    │ sendBroadcast()    │         │
│         ▼                    ▼                    ▼         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              system_server (AMS)                     │   │
│  │                                                      │   │
│  │  ┌─────────────────────────────────────────────┐     │   │
│  │  │  BroadcastQueue(s)                          │     │   │
│  │  │                                             │     │   │
│  │  │  ┌──────────┐ ┌──────────┐ ┌──────────┐    │     │   │
│  │  │  │BroadRec 1│→│BroadRec 2│→│BroadRec 3│    │     │   │
│  │  │  └──────────┘ └──────────┘ └──────────┘    │     │   │
│  │  └─────────────────────────────────────────────┘     │   │
│  │                                                      │   │
│  │  mReceiverResolver: HashMap<IntentFilter, Receiver>  │   │
│  │  mRegisteredReceivers: HashMap<IBinder, ReceiverList> │   │
│  └──────────────────────────────────────────────────────┘   │
│         │                    │                    │         │
│         │ Binder IPC         │ Binder IPC         │ Binder │
│         ▼                    ▼                    ▼         │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐ │
│  │  Receiver 1  │     │  Receiver 2  │     │  Receiver 3  │ │
│  │  (App C)     │     │  (App A)     │     │  (App B)     │ │
│  │  onReceive() │     │  onReceive() │     │  onReceive() │ │
│  └──────────────┘     └──────────────┘     └──────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Pipeline доставки broadcast (полный цикл)

```
 Sender Process                    system_server                    Receiver Process
┌────────────────┐            ┌─────────────────────────┐            ┌────────────────┐
│                │            │                         │            │                │
│ context        │  Binder    │  AMS                    │            │                │
│ .sendBroadcast │ ────────→  │  .broadcastIntentLocked │            │                │
│ (intent)       │  IPC       │                         │            │                │
│                │            │  1. Permission checks   │            │                │
│                │            │  2. Resolve receivers:  │            │                │
│                │            │     a. Dynamic (HashMap) │            │                │
│                │            │     b. Static (PMS)     │            │                │
│                │            │  3. Create BroadcastRec │            │                │
│                │            │  4. Enqueue to          │            │                │
│                │            │     BroadcastQueue      │            │                │
│                │            │     ↓                   │            │                │
│                │            │  scheduleBroadcast      │            │                │
│                │            │  Locked()               │            │                │
│                │            │     ↓                   │            │                │
│                │            │  Handler.sendMessage    │            │                │
│                │            │  (BROADCAST_INTENT_MSG) │            │                │
│                │            │     ↓                   │            │                │
│                │            │  processNextBroadcast   │  Binder    │ ReceiverDisp   │
│                │            │  Locked()               │ ────────→  │ .performReceive│
│                │            │     ↓                   │  IPC       │     ↓          │
│                │            │  deliverToRegistered    │            │ Args.run()     │
│                │            │  ReceiverLocked()       │            │     ↓          │
│                │            │  или                    │            │ receiver       │
│                │            │  processCurBroadcast    │            │ .onReceive()   │
│                │            │  Locked()               │            │                │
│                │            │                         │            │                │
└────────────────┘            └─────────────────────────┘            └────────────────┘
```

### BroadcastRecord: анатомия записи

Каждый broadcast в system_server представлен объектом `BroadcastRecord`:

```
BroadcastRecord (AOSP: BroadcastRecord.java)
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  intent: Intent              // Отправленный Intent      │
│  callerApp: ProcessRecord    // Процесс-отправитель      │
│  callerPackage: String       // Package отправителя      │
│  callingPid: int             // PID отправителя          │
│  callingUid: int             // UID отправителя          │
│                                                          │
│  receivers: List<Object>     // Список получателей       │
│    → BroadcastFilter (dynamic)                           │
│    → ResolveInfo (static/manifest)                       │
│                                                          │
│  nextReceiver: int           // Индекс текущего receiver │
│  state: int                  // Состояние доставки       │
│    → IDLE, APP_RECEIVE, CALL_IN_RECEIVE,                 │
│       CALL_DONE_RECEIVE, WAITING_SERVICES                │
│                                                          │
│  ordered: boolean            // Ordered broadcast?       │
│  sticky: boolean             // Sticky broadcast?        │
│  resultTo: IIntentReceiver   // Final receiver           │
│  resultCode: int             // Код результата (ordered) │
│  resultData: String          // Данные результата        │
│  resultExtras: Bundle        // Extras результата        │
│  resultAbort: boolean        // Был ли abortBroadcast()  │
│                                                          │
│  dispatchTime: long          // Когда начата доставка    │
│  receiverTime: long          // Время текущего receiver  │
│  finishTime: long            // Когда завершена доставка │
│  enqueueClockTime: long      // Wall-clock при enqueue   │
│                                                          │
│  initialSticky: boolean      // Initial sticky delivery  │
│  userId: int                 // User ID                  │
│  requiredPermissions: String[] // Required permissions    │
│  appOp: int                  // App op permission check  │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Две очереди: Foreground и Background

До Android 14 AMS использовал две параллельные `BroadcastQueue`:

```
system_server
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  ┌─────────────────────────────────┐                   │
│  │  Foreground Queue               │                   │
│  │  (Intent.FLAG_RECEIVER_FOREGROUND)                  │
│  │                                 │                   │
│  │  Timeout: 10 секунд per receiver│                   │
│  │  Для: пользовательские events   │                   │
│  │  Приоритет: высокий             │                   │
│  │                                 │                   │
│  │  [Rec1] → [Rec2] → [Rec3]      │                   │
│  └─────────────────────────────────┘                   │
│                                                         │
│  ┌─────────────────────────────────┐                   │
│  │  Background Queue               │                   │
│  │  (по умолчанию)                 │                   │
│  │                                 │                   │
│  │  Timeout: 60 секунд per receiver│                   │
│  │  Для: system events             │                   │
│  │  Приоритет: обычный             │                   │
│  │                                 │                   │
│  │  [Rec4] → [Rec5] → [Rec6]      │                   │
│  └─────────────────────────────────┘                   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

```kotlin
// Отправить в foreground queue (быстрая доставка)
Intent("com.example.URGENT").apply {
    addFlags(Intent.FLAG_RECEIVER_FOREGROUND)
}.also { context.sendBroadcast(it) }

// По умолчанию → background queue
context.sendBroadcast(Intent("com.example.NORMAL"))
```

### processNextBroadcastLocked() — сердце доставки

Это основной метод, обрабатывающий очередь broadcast. Вызывается через Handler при получении `BROADCAST_INTENT_MSG`:

```
processNextBroadcastLocked() algorithm:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  1. Обработать все parallel broadcasts (normal):            │
│     ┌─────────────────────────────────────────────┐         │
│     │  while (mParallelBroadcasts.size() > 0):    │         │
│     │    r = mParallelBroadcasts.remove(0)        │         │
│     │    for each receiver in r.receivers:         │         │
│     │      deliverToRegisteredReceiverLocked(r, …) │        │
│     │    // Все получатели обработаны параллельно  │         │
│     └─────────────────────────────────────────────┘         │
│                                                             │
│  2. Обработать ordered broadcasts (по одному receiver):     │
│     ┌─────────────────────────────────────────────┐         │
│     │  if (mPendingBroadcast != null):             │         │
│     │    // Ждём завершения предыдущего receiver   │         │
│     │    if (process still alive): return          │         │
│     │    else: cleanup and continue                │         │
│     │                                              │         │
│     │  r = mDispatcher.getNextBroadcastLocked(now) │         │
│     │                                              │         │
│     │  // Проверка timeout                         │         │
│     │  if (now > r.dispatchTime + TIMEOUT):        │         │
│     │    broadcastTimeoutLocked(false)              │         │
│     │    → ANR для приложения                      │         │
│     │                                              │         │
│     │  // Доставить текущему receiver               │         │
│     │  recIdx = r.nextReceiver++                   │         │
│     │                                              │         │
│     │  if (receiver is BroadcastFilter):           │         │
│     │    // Dynamic → deliver immediately          │         │
│     │    deliverToRegisteredReceiverLocked()        │         │
│     │                                              │         │
│     │  if (receiver is ResolveInfo):               │         │
│     │    // Static → может потребовать запуск app   │         │
│     │    if (app not running):                     │         │
│     │      mPendingBroadcast = r                   │         │
│     │      AMS.startProcessLocked()                │         │
│     │      return // ждём запуска app               │         │
│     │    else:                                     │         │
│     │      processCurBroadcastLocked(r, app)        │         │
│     │                                              │         │
│     └─────────────────────────────────────────────┘         │
│                                                             │
│  3. Если все broadcast обработаны → reschedule              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### BroadcastQueueModernImpl (Android 14+)

Android 14 представил полную перезапись очереди broadcast — `BroadcastQueueModernImpl`:

```
Сравнение старой и новой реализации:

BroadcastQueue (legacy):                BroadcastQueueModernImpl:
┌─────────────────────────────┐        ┌───────────────────────────────────┐
│                             │        │                                   │
│  Две отдельные очереди      │        │  Единая очередь с per-process     │
│  (FG и BG)                  │        │  scheduling                      │
│                             │        │                                   │
│  Линейная обработка         │        │  Параллельная доставка в разные   │
│  ordered broadcast          │        │  процессы (где возможно)          │
│                             │        │                                   │
│  Простой timeout            │        │  Адаптивные timeouts              │
│  (10s fg, 60s bg)           │        │  с учётом загруженности           │
│                             │        │                                   │
│  Нет deferral для           │        │  Broadcast deferral для           │
│  cached processes           │        │  cached processes (API 35+)       │
│                             │        │                                   │
│  Thundering herd при        │        │  Batching: группировка            │
│  массовых broadcasts        │        │  broadcast для одного процесса    │
│                             │        │                                   │
└─────────────────────────────┘        └───────────────────────────────────┘
```

Ключевые улучшения `BroadcastQueueModernImpl`:

```kotlin
// 1. Per-process runnable queue
// Broadcasts для каждого процесса обрабатываются последовательно,
// но разные процессы могут обрабатывать параллельно

// 2. Broadcast deferral (Android 15+)
// Если app в cached state, broadcast откладывается:
//   - Не будит процесс
//   - Доставляется когда app выходит из cached
//   - Уменьшает wake-ups и потребление батареи

// 3. Urgent queue
// Критичные системные broadcasts (BATTERY_LOW, SCREEN_OFF)
// обрабатываются вне очереди — через отдельный urgent path

// 4. Delivery grouping
// Несколько broadcasts для одного процесса группируются
// в один Binder вызов, снижая IPC overhead
```

```
Lifecycle broadcast в BroadcastQueueModernImpl:

  sendBroadcast(intent)
       │
       ▼
  enqueueOrReplaceBroadcast()
       │
       ├── Urgent? ──→ processUrgent()
       │
       ├── Cached process? ──→ deferBroadcast()
       │                          │
       │                          ▼ (когда app выходит из cached)
       │                       deliverDeferredBroadcasts()
       │
       ▼
  scheduleReceiverColdLocked() / scheduleReceiverWarmLocked()
       │
       ▼
  deliverToRegisteredReceiverLocked()
       │
       ▼
  app.thread.scheduleReceiver() // Binder IPC
       │
       ▼
  ActivityThread.handleReceiver()
       │
       ▼
  receiver.onReceive(context, intent)
```

---

## Регистрация получателей

### Два способа регистрации: Static vs Dynamic

```
Static (Manifest) Registration:          Dynamic (Context) Registration:
┌────────────────────────────────┐      ┌────────────────────────────────┐
│                                │      │                                │
│  ✅ Работает когда app не      │      │  ✅ Нет ограничений implicit   │
│     запущено (для exempt       │      │     broadcasts                 │
│     broadcasts)                │      │                                │
│                                │      │  ✅ Можно регистрировать       │
│  ❌ Ограничения Android 8+     │      │     динамически               │
│     (implicit broadcasts)      │      │                                │
│                                │      │  ❌ Работает только пока       │
│  ❌ Увеличивает время запуска  │      │     Context жив                │
│     (PMS сканирует manifest)   │      │                                │
│                                │      │  ❌ Нужно помнить про          │
│  ⚡ Запускает app process       │      │     unregisterReceiver()       │
│     если он не работает        │      │                                │
│                                │      │                                │
└────────────────────────────────┘      └────────────────────────────────┘
```

### Static (Manifest) Registration — под капотом

```xml
<!-- AndroidManifest.xml -->
<receiver
    android:name=".BootReceiver"
    android:exported="true"
    android:directBootAware="true"> <!-- Работает до разблокировки (FBE) -->
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

```kotlin
// Kotlin implementation
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Инициализация после загрузки
            // ВАЖНО: onReceive() на main thread, 10 сек лимит
            schedulePeriodicWork(context)
        }
    }

    private fun schedulePeriodicWork(context: Context) {
        val request = PeriodicWorkRequestBuilder<SyncWorker>(
            15, TimeUnit.MINUTES
        ).build()
        WorkManager.getInstance(context)
            .enqueueUniquePeriodicWork(
                "sync",
                ExistingPeriodicWorkPolicy.KEEP,
                request
            )
    }
}
```

Как AMS находит manifest receivers:

```
PackageManagerService (PMS) при установке APK:
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  1. APK install → parsePackage()                        │
│  2. AndroidManifest.xml → parseReceiver()               │
│  3. IntentFilter → добавляется в mReceivers             │
│     (PackageManagerService.mComponentResolver)           │
│  4. При sendBroadcast():                                │
│     AMS → PMS.queryBroadcastReceivers(intent, flags)    │
│     → возвращает List<ResolveInfo>                      │
│                                                         │
│  Кэш: PMS кэширует resolved receivers.                  │
│  При обновлении APK → кэш инвалидируется.              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Dynamic (Context) Registration — под капотом

```kotlin
// Базовый шаблон регистрации
class BatteryMonitorActivity : AppCompatActivity() {

    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            val percentage = level * 100 / scale
            updateBatteryUI(percentage)
        }
    }

    override fun onStart() {
        super.onStart()
        // Android 14+ (targetSdk 34): ОБЯЗАТЕЛЬНЫЙ флаг
        ContextCompat.registerReceiver(
            this,
            batteryReceiver,
            IntentFilter(Intent.ACTION_BATTERY_CHANGED),
            ContextCompat.RECEIVER_NOT_EXPORTED
        )
    }

    override fun onStop() {
        unregisterReceiver(batteryReceiver)
        super.onStop()
    }
}
```

Что происходит при `registerReceiver()` внутри Android:

```
App Process                              system_server
┌──────────────────────────┐            ┌───────────────────────────────┐
│                          │            │                               │
│  context.registerReceiver│            │                               │
│       │                  │            │                               │
│       ▼                  │            │                               │
│  ContextImpl             │            │                               │
│  .registerReceiverInternal│           │                               │
│       │                  │            │                               │
│       ▼                  │            │                               │
│  LoadedApk              │            │                               │
│  .getReceiverDispatcher │            │                               │
│       │                  │            │                               │
│       ▼                  │            │                               │
│  ReceiverDispatcher      │            │                               │
│    ├── InnerReceiver     │  Binder    │                               │
│    │   (IIntentReceiver  │ ────────→  │  AMS.registerReceiverWithFeature│
│    │    Binder stub)     │  IPC       │       │                       │
│    │                     │            │       ▼                       │
│    ├── mReceiver         │            │  mRegisteredReceivers         │
│    │   (BroadcastReceiver│            │    .put(IBinder, ReceiverList)│
│    │    reference)       │            │       │                       │
│    │                     │            │       ▼                       │
│    └── mContext           │            │  mReceiverResolver            │
│        (Context ref —    │            │    .addFilter(BroadcastFilter)│
│         LEAK DANGER!)    │            │                               │
│                          │            │                               │
└──────────────────────────┘            └───────────────────────────────┘
```

```
ReceiverDispatcher (AOSP: LoadedApk.java):
┌────────────────────────────────────────────────────────────┐
│                                                            │
│  InnerReceiver extends IIntentReceiver.Stub               │
│    │                                                       │
│    │  // Binder stub — система вызывает при broadcast      │
│    │  performReceive(Intent, resultCode, data, extras,     │
│    │                 ordered, sticky, sendingUser)          │
│    │      │                                                │
│    │      ▼                                                │
│    │  ReceiverDispatcher.performReceive()                   │
│    │      │                                                │
│    │      ▼                                                │
│    │  Args args = new Args(intent, resultCode, ...)        │
│    │  mActivityThread.post(args)  ← post на main thread   │
│    │      │                                                │
│    │      ▼                                                │
│    │  Args.run()                                           │
│    │    → receiver.onReceive(mContext, intent)              │
│    │                                                       │
│    │  ВАЖНО: receiver.onReceive() выполняется              │
│    │  НА MAIN THREAD через Handler                        │
│    │                                                       │
└────────────────────────────────────────────────────────────┘
```

### Android 14: обязательные флаги EXPORTED/NOT_EXPORTED

```kotlin
// ❌ CRASH на Android 14+ (targetSdk 34)
context.registerReceiver(receiver, filter)
// SecurityException: com.example.app: One of RECEIVER_EXPORTED or
// RECEIVER_NOT_EXPORTED should be specified

// ✅ Для внутренних broadcast (от своего приложения)
ContextCompat.registerReceiver(
    context, receiver, filter,
    ContextCompat.RECEIVER_NOT_EXPORTED
)

// ✅ Для внешних broadcast (от других приложений / системы)
ContextCompat.registerReceiver(
    context, receiver, filter,
    ContextCompat.RECEIVER_EXPORTED
)

// ⚠️ Системные protected broadcasts — флаг НЕ обязателен
// (ACTION_BATTERY_CHANGED, ACTION_SCREEN_ON, BOOT_COMPLETED и др.)
context.registerReceiver(
    receiver,
    IntentFilter(Intent.ACTION_BATTERY_CHANGED)
) // OK — protected broadcast автоматически NOT_EXPORTED
```

**Как AMS проверяет exported флаг:**

```
AMS.registerReceiverWithFeature():
  1. Проверить callerApp не null
  2. Если targetSdk >= 34:
     if (flags & (RECEIVER_EXPORTED | RECEIVER_NOT_EXPORTED) == 0):
       → Проверить: intent-filter содержит protected broadcast action?
         → Да: OK (системные broadcasts всегда разрешены)
         → Нет: throw SecurityException
  3. Если RECEIVER_NOT_EXPORTED:
     → В BroadcastFilter ставится visible=false
     → При matching: пропускать sender из других UID
  4. Если RECEIVER_EXPORTED:
     → В BroadcastFilter visible=true
     → Доступен для любого отправителя
```

### Lifecycle-aware receiver с repeatOnLifecycle

```kotlin
// Современный подход: lifecycle-aware registration
class NetworkActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Регистрация привязана к lifecycle
        val receiver = object : BroadcastReceiver() {
            override fun onReceive(context: Context, intent: Intent) {
                handleNetworkChange(intent)
            }
        }

        lifecycle.addObserver(object : DefaultLifecycleObserver {
            override fun onStart(owner: LifecycleOwner) {
                ContextCompat.registerReceiver(
                    this@NetworkActivity,
                    receiver,
                    IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION),
                    ContextCompat.RECEIVER_NOT_EXPORTED
                )
            }

            override fun onStop(owner: LifecycleOwner) {
                unregisterReceiver(receiver)
            }
        })
    }
}
```

```kotlin
// Ещё лучше — extension function для любого LifecycleOwner
fun LifecycleOwner.registerReceiverOnLifecycle(
    context: Context,
    receiver: BroadcastReceiver,
    filter: IntentFilter,
    exported: Boolean = false
) {
    val flag = if (exported) {
        ContextCompat.RECEIVER_EXPORTED
    } else {
        ContextCompat.RECEIVER_NOT_EXPORTED
    }

    lifecycle.addObserver(object : DefaultLifecycleObserver {
        override fun onStart(owner: LifecycleOwner) {
            ContextCompat.registerReceiver(context, receiver, filter, flag)
        }

        override fun onStop(owner: LifecycleOwner) {
            try {
                context.unregisterReceiver(receiver)
            } catch (e: IllegalArgumentException) {
                // Receiver already unregistered
            }
        }
    })
}

// Использование:
registerReceiverOnLifecycle(
    this,
    batteryReceiver,
    IntentFilter(Intent.ACTION_BATTERY_CHANGED)
)
```

---

## Normal vs Ordered Broadcasts

### Normal Broadcast (параллельная доставка)

Normal broadcast — параллельная доставка всем подходящим receivers. Receivers не могут влиять друг на друга.

```kotlin
// Отправка normal broadcast
context.sendBroadcast(Intent("com.example.DATA_UPDATED").apply {
    putExtra("count", 42)
    putExtra("timestamp", System.currentTimeMillis())
})

// С permission (только receivers с нужным permission получат)
context.sendBroadcast(
    Intent("com.example.SECURE_EVENT"),
    Manifest.permission.ACCESS_FINE_LOCATION
)
```

```
Normal Broadcast Processing:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  processNextBroadcastLocked():                               │
│                                                              │
│  while (mParallelBroadcasts.size() > 0):                     │
│    r = mParallelBroadcasts.remove(0)                         │
│    N = r.receivers.size()                                     │
│                                                              │
│    for i in 0..N:                                            │
│      target = r.receivers.get(i) as BroadcastFilter          │
│      deliverToRegisteredReceiverLocked(r, target, false, i)  │
│      // false = NOT ordered                                  │
│                                                              │
│    // Все receivers получили broadcast одновременно           │
│    // Порядок НЕ гарантирован                                │
│    // Receivers НЕ могут abort или modify result              │
│                                                              │
│  ВАЖНО: В mParallelBroadcasts попадают ТОЛЬКО                │
│  dynamic (context-registered) receivers для normal broadcasts │
│                                                              │
│  Static (manifest) receivers ВСЕГДА обрабатываются           │
│  как ordered, даже если broadcast послан через sendBroadcast()│
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Ordered Broadcast (последовательная доставка)

Ordered broadcast доставляется receivers последовательно по приоритету. Каждый receiver может:
- Изменить resultCode, resultData, resultExtras
- Прервать доставку через `abortBroadcast()`

```kotlin
// Отправка ordered broadcast
context.sendOrderedBroadcast(
    Intent("com.example.SMS_FILTER").apply {
        putExtra("message", "Hello World")
        putExtra("sender", "+1234567890")
    },
    "com.example.FILTER_PERMISSION",  // required permission
    object : BroadcastReceiver() {     // final result receiver
        override fun onReceive(context: Context, intent: Intent) {
            // Вызывается ПОСЛЕДНИМ, получает финальный результат
            val wasAborted = resultCode == Activity.RESULT_CANCELED
            val filteredMessage = resultData
            Log.d("SMS", "Final result: aborted=$wasAborted, msg=$filteredMessage")
        }
    },
    null,               // Handler (null = main thread)
    Activity.RESULT_OK, // initial resultCode
    null,               // initial resultData
    null                // initial resultExtras
)
```

```kotlin
// Receiver высокого приоритета (обрабатывается первым)
class SpamFilterReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val message = intent.getStringExtra("message") ?: return
        val sender = intent.getStringExtra("sender") ?: return

        if (isSpam(sender, message)) {
            // Прервать доставку — следующие receivers НЕ получат
            abortBroadcast()
            resultCode = Activity.RESULT_CANCELED
            resultData = "SPAM_DETECTED"
            return
        }

        // Передать модифицированные данные следующему receiver
        resultData = sanitize(message)
        setResultExtras(Bundle().apply {
            putBoolean("spam_checked", true)
            putFloat("spam_score", calculateSpamScore(message))
        })
    }
}
```

```xml
<!-- Manifest: приоритет определяет порядок для ordered broadcasts -->
<receiver android:name=".SpamFilterReceiver"
    android:exported="false">
    <intent-filter android:priority="100"> <!-- Высокий приоритет = первым -->
        <action android:name="com.example.SMS_FILTER" />
    </intent-filter>
</receiver>

<receiver android:name=".LoggingReceiver"
    android:exported="false">
    <intent-filter android:priority="0"> <!-- Низкий приоритет = последним -->
        <action android:name="com.example.SMS_FILTER" />
    </intent-filter>
</receiver>
```

### Сравнение Normal vs Ordered

```
Normal Broadcast:                     Ordered Broadcast:
┌──────┐                              ┌──────┐
│Sender│                              │Sender│
└──┬───┘                              └──┬───┘
   │                                     │
   ├──→ Receiver A ──→ done              ▼
   │                              ┌──────────────┐
   ├──→ Receiver B ──→ done       │ Receiver A   │ priority=100
   │                              │ (может abort, │
   └──→ Receiver C ──→ done       │  modify result)│
                                  └──────┬───────┘
   Параллельно.                          │ resultCode, resultData
   Порядок НЕ определён.                 ▼
   Нельзя abort/modify.           ┌──────────────┐
                                  │ Receiver B   │ priority=50
                                  │ (видит result │
                                  │  от A)        │
                                  └──────┬───────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │ Receiver C   │ priority=0
                                  └──────┬───────┘
                                         │
                                         ▼
                                  ┌──────────────┐
                                  │Final Receiver│
                                  │(resultReceiver│
                                  │ из sendOrdered│
                                  │ Broadcast)    │
                                  └──────────────┘
                                  Последовательно.
                                  Порядок по priority.
```

| Характеристика | Normal | Ordered |
|----------------|--------|---------|
| Доставка | Параллельная | Последовательная |
| Порядок | Не определён | По priority (высокий → низкий) |
| abort | Невозможен | `abortBroadcast()` |
| Модификация result | Невозможна | `resultCode`, `resultData`, `resultExtras` |
| Final receiver | Нет | Да (опционально) |
| Производительность | Быстрее (параллельно) | Медленнее (sequential + timeout на каждый) |
| Static receivers | Становятся ordered internally | Ordered как задумано |
| Timeout | Нет per-receiver timeout | 10s fg / 60s bg per receiver |

### Android 16: изменение priority для ordered broadcasts

```kotlin
// ⚠️ Android 16 (API 36):
// priority гарантируется ТОЛЬКО внутри одного процесса!
// Между разными приложениями порядок НЕ определён.

// До Android 16:
// App A (priority=100) → App B (priority=50) → App C (priority=0)
// Гарантированный порядок между приложениями

// Android 16+:
// Внутри одного приложения: priority=100 → 50 → 0 ✅ гарантирован
// Между приложениями: порядок НЕ определён ⚠️
```

---

## Implicit Broadcast Restrictions (Android 8.0+)

### Проблема: "Thundering Herd"

```
До Android 8.0 — Thundering Herd Problem:
┌─────────────────────────────────────────────────────────┐
│                                                         │
│  Событие: CONNECTIVITY_CHANGE                           │
│                                                         │
│  system_server отправляет broadcast...                  │
│                                                         │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐     ┌─────────┐  │
│  │ App 1   │ │ App 2   │ │ App 3   │ ... │ App 50  │  │
│  │ (killed)│ │ (killed)│ │ (killed)│     │ (killed)│  │
│  └────┬────┘ └────┬────┘ └────┬────┘     └────┬────┘  │
│       │          │          │               │         │
│       ▼          ▼          ▼               ▼         │
│    ЗАПУСК      ЗАПУСК      ЗАПУСК         ЗАПУСК      │
│    ПРОЦЕССА    ПРОЦЕССА    ПРОЦЕССА       ПРОЦЕССА    │
│                                                         │
│  Результат:                                             │
│  → 50 процессов пробуждаются одновременно               │
│  → CPU загружен на 100%                                 │
│  → RAM переполнена                                      │
│  → Батарея расходуется                                  │
│  → Пользователь видит "тормоза"                        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Решение Android 8.0 (API 26)

**Manifest-registered receivers НЕ могут получать большинство implicit broadcasts.**

```xml
<!-- ❌ НЕ работает с targetSdk 26+ (implicit broadcast) -->
<receiver android:name=".ConnectivityReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="android.net.conn.CONNECTIVITY_CHANGE" />
    </intent-filter>
</receiver>

<!-- ❌ Тоже НЕ работает (implicit broadcast не в exemption list) -->
<receiver android:name=".PowerReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.ACTION_POWER_CONNECTED" />
    </intent-filter>
</receiver>
```

### Исключения: manifest receivers ВСЁ ЕЩЁ работают

| Broadcast | Почему исключение | Примечание |
|-----------|-------------------|------------|
| `BOOT_COMPLETED` | Однократный, критичен для инициализации | Нужно `RECEIVE_BOOT_COMPLETED` permission |
| `LOCKED_BOOT_COMPLETED` | Direct Boot, до разблокировки | Receiver должен быть `directBootAware` |
| `LOCALE_CHANGED` | Требует перезагрузки ресурсов | Однократный при смене языка |
| `MY_PACKAGE_REPLACED` | Собственное обновление приложения | Только для обновлённого приложения |
| `MY_PACKAGE_FULLY_REMOVED` | Удаление приложения | Cleanup |
| `PACKAGE_ADDED/REMOVED` | Установка/удаление других apps | Для app managers |
| `USB_DEVICE_ATTACHED` | Hardware event | Для USB-аксессуаров |
| `ACTION_TIMEZONE_CHANGED` | Критичен для часов/будильников | Нечастый |
| `ACTION_TIME_SET` | Время изменилось | Для точных расписаний |
| `SMS_DELIVER/WAP_PUSH_DELIVER` | SMS/MMS приёмник | Для default SMS app |

Полный список: [Implicit broadcast exceptions](https://developer.android.com/develop/background-work/background-tasks/broadcasts/broadcast-exceptions)

### Миграция: manifest → dynamic

```kotlin
// ❌ Manifest receiver для CONNECTIVITY_CHANGE — не работает
// ✅ Dynamic registration — работает

class NetworkMonitorFragment : Fragment() {

    private val connectivityReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val cm = context.getSystemService<ConnectivityManager>()
            val isConnected = cm?.activeNetwork != null
            updateNetworkStatus(isConnected)
        }
    }

    override fun onStart() {
        super.onStart()
        ContextCompat.registerReceiver(
            requireContext(),
            connectivityReceiver,
            IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION),
            ContextCompat.RECEIVER_NOT_EXPORTED
        )
    }

    override fun onStop() {
        requireContext().unregisterReceiver(connectivityReceiver)
        super.onStop()
    }
}
```

```kotlin
// ✅ Ещё лучше: ConnectivityManager.NetworkCallback
class NetworkMonitorFragment : Fragment() {

    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            // Сеть появилась
        }

        override fun onLost(network: Network) {
            // Сеть пропала
        }

        override fun onCapabilitiesChanged(
            network: Network,
            capabilities: NetworkCapabilities
        ) {
            val hasInternet = capabilities
                .hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            val isWifi = capabilities
                .hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
        }
    }

    override fun onStart() {
        super.onStart()
        val cm = requireContext().getSystemService<ConnectivityManager>()
        cm?.registerDefaultNetworkCallback(networkCallback)
    }

    override fun onStop() {
        val cm = requireContext().getSystemService<ConnectivityManager>()
        cm?.unregisterNetworkCallback(networkCallback)
        super.onStop()
    }
}
```

### Explicit broadcast — обходит ограничения

```kotlin
// Explicit broadcast (указан конкретный компонент) — ВСЕГДА работает
val intent = Intent().apply {
    component = ComponentName(
        "com.example.target",
        "com.example.target.MyReceiver"
    )
    action = "com.example.CUSTOM_ACTION"
    putExtra("data", "value")
}
context.sendBroadcast(intent)
// ✅ Доставляется даже manifest receiver, даже на Android 14+
```

---

## goAsync() — асинхронная обработка в BroadcastReceiver

### Проблема: 10-секундный лимит

```kotlin
// ❌ ANR через 10 секунд (foreground) или 60 секунд (background)
class DataSyncReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Тяжёлая работа на MAIN THREAD
        val data = fetchFromNetwork()    // 5+ секунд
        saveToDatabase(data)             // 3+ секунд
        notifyUser()                     // 2+ секунды
        // → ANR! BroadcastQueue.broadcastTimeoutLocked()
    }
}
```

```
Без goAsync():
┌──────────────────────────────────────────────────┐
│  onReceive() вызван на main thread               │
│      ↓                                           │
│  system_server ждёт finishReceiver()              │
│      ↓                                           │
│  return из onReceive()                           │
│      ↓                                           │
│  система считает receiver завершённым            │
│      ↓                                           │
│  Процесс может быть убит LMK                    │
│      ↓                                           │
│  Если CoroutineScope запущена после return —     │
│  она может не доработать!                        │
│                                                  │
│  Timeline:                                       │
│  0s ──────── 10s ──────────────────→ ANR         │
│  │onReceive()│                                   │
│  └───────────┘                                   │
│  В этом окне нужно уложиться.                    │
│                                                  │
└──────────────────────────────────────────────────┘
```

### Решение: goAsync() + PendingResult

```kotlin
class DataSyncReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult: PendingResult = goAsync()
        // После goAsync(): система НЕ считает receiver завершённым
        // до вызова pendingResult.finish()

        // Запускаем корутину в background thread
        CoroutineScope(Dispatchers.IO + SupervisorJob()).launch {
            try {
                val data = fetchFromNetwork()
                saveToDatabase(data)

                pendingResult.resultCode = Activity.RESULT_OK
                pendingResult.resultData = "success"
            } catch (e: Exception) {
                Log.e("DataSync", "Failed", e)
                pendingResult.resultCode = Activity.RESULT_CANCELED
                pendingResult.resultData = e.message
            } finally {
                // ОБЯЗАТЕЛЬНО вызвать finish()!
                // Иначе система будет считать receiver "зависшим"
                pendingResult.finish()
            }
        }
        // return из onReceive() — но receiver ещё "живёт"
        // благодаря PendingResult
    }
}
```

### PendingResult — state machine

```
PendingResult State Machine:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  ┌──────────┐   goAsync()    ┌───────────────┐              │
│  │  ACTIVE   │ ────────────→ │  GO_ASYNC     │              │
│  │(onReceive │               │  (detached    │              │
│  │ running)  │               │   from thread)│              │
│  └─────┬─────┘               └───────┬───────┘              │
│        │                             │                      │
│        │ return from                 │ finish()             │
│        │ onReceive()                 │                      │
│        ▼                             ▼                      │
│  ┌──────────┐               ┌───────────────┐              │
│  │ FINISHED │               │  FINISHED     │              │
│  │(auto)    │               │  (manual)     │              │
│  └──────────┘               └───────────────┘              │
│                                                             │
│  ВАЖНО: ANR timeout (10s/60s) всё ещё действует!           │
│  goAsync() НЕ снимает timeout.                             │
│  Это только позволяет уйти с main thread.                  │
│                                                             │
│  Если finish() не вызван в timeout → ANR                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### goAsync() с WorkManager для длительных задач

```kotlin
// Для задач > 10 секунд: goAsync() + WorkManager
class LargeDataReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val pendingResult = goAsync()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                // Быстрая часть: запланировать длительную работу
                val data = intent.getStringExtra("data_url") ?: return@launch

                val workRequest = OneTimeWorkRequestBuilder<DataDownloadWorker>()
                    .setInputData(workDataOf("url" to data))
                    .setConstraints(
                        Constraints.Builder()
                            .setRequiredNetworkType(NetworkType.CONNECTED)
                            .build()
                    )
                    .build()

                WorkManager.getInstance(context).enqueue(workRequest)

                pendingResult.resultCode = Activity.RESULT_OK
            } finally {
                pendingResult.finish()
            }
        }
    }
}
```

### goAsync() под капотом (AOSP)

```
BroadcastReceiver.goAsync():
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  public final PendingResult goAsync() {                      │
│      PendingResult res = mPendingResult;                     │
│      mPendingResult = null;  // Отсоединяем от onReceive()   │
│      return res;                                             │
│  }                                                           │
│                                                              │
│  // В Args.run() (ReceiverDispatcher):                       │
│  receiver.onReceive(context, intent);                        │
│                                                              │
│  if (receiver.getPendingResult() != null) {                  │
│      // goAsync() НЕ был вызван → finish() автоматически    │
│      finish();                                               │
│  }                                                           │
│  // Если goAsync() был вызван → mPendingResult == null       │
│  // → finish() НЕ вызывается автоматически                   │
│  // → Ждём, пока разработчик вызовет pendingResult.finish()  │
│                                                              │
│  PendingResult.finish():                                     │
│    → sendFinished() → AMS.finishReceiver()                   │
│    → Сигнал system_server: "receiver завершил работу"        │
│    → BroadcastQueue.finishReceiverLocked()                   │
│    → processNextBroadcastLocked() — обработать следующий      │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## Sticky Broadcasts (deprecated, но нужно знать)

### Что это было

Sticky broadcast сохранялся системой после доставки. Новые receivers при регистрации сразу получали последний sticky broadcast.

```kotlin
// ❌ Deprecated API 21 (Android 5.0)
context.sendStickyBroadcast(intent)
context.removeStickyBroadcast(intent)
```

### Почему deprecated

```
Проблемы sticky broadcasts:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  1. БЕЗОПАСНОСТЬ: Любое приложение может перезаписать        │
│     sticky broadcast (no permission check on overwrite)      │
│                                                              │
│  2. УТЕЧКА ДАННЫХ: Sticky broadcast доступен всем            │
│     процессам, даже будущим                                  │
│                                                              │
│  3. ПАМЯТЬ: Sticky broadcasts хранятся в system_server        │
│     бесконечно (пока не removeStickyBroadcast)               │
│                                                              │
│  4. RACE CONDITIONS: При быстрой последовательности          │
│     sticky broadcast receiver может получить устаревший      │
│                                                              │
│  5. NO TYPE SAFETY: Данные в Intent extras не типизированы   │
│                                                              │
│  Замена: StateFlow, LiveData, SharedPreferences              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Единственный выживший: ACTION_BATTERY_CHANGED

```kotlin
// ACTION_BATTERY_CHANGED — sticky broadcast, который ВСЁ ЕЩЁ работает
// registerReceiver() возвращает текущее значение СРАЗУ
val batteryStatus: Intent? = context.registerReceiver(
    null, // null receiver = только получить текущий sticky Intent
    IntentFilter(Intent.ACTION_BATTERY_CHANGED)
)

val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
val batteryPct = level * 100 / scale.toFloat()

val isCharging = when (batteryStatus?.getIntExtra(BatteryManager.EXTRA_STATUS, -1)) {
    BatteryManager.BATTERY_STATUS_CHARGING -> true
    BatteryManager.BATTERY_STATUS_FULL -> true
    else -> false
}
```

---

## Безопасность Broadcast

### 6 уровней защиты

```
Уровни безопасности Broadcast (от слабого к сильному):
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Level 1: exported="false" (manifest)                       │
│  → Receiver виден только своему приложению                  │
│  → Самый простой способ для internal receivers              │
│                                                             │
│  Level 2: RECEIVER_NOT_EXPORTED (dynamic, Android 14+)      │
│  → Dynamic receiver виден только своему приложению          │
│  → Обязателен для targetSdk 34+                             │
│                                                             │
│  Level 3: setPackage() на Intent                            │
│  → Broadcast доставляется только указанному package         │
│  → Implicit → Explicit conversion                           │
│                                                             │
│  Level 4: Permission на sendBroadcast()                     │
│  → Receiver должен иметь указанный permission               │
│  → Фильтрация на стороне получателя                        │
│                                                             │
│  Level 5: Permission на registerReceiver()                  │
│  → Sender должен иметь указанный permission                 │
│  → Фильтрация на стороне отправителя                       │
│                                                             │
│  Level 6: Signature-level custom permission                 │
│  → Только приложения, подписанные тем же ключом             │
│  → Максимальная защита для inter-app communication          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Level 1: exported="false"

```xml
<!-- Receiver только для своего приложения -->
<receiver
    android:name=".InternalReceiver"
    android:exported="false"> <!-- Внешние приложения НЕ видят -->
    <intent-filter>
        <action android:name="com.example.INTERNAL_ACTION" />
    </intent-filter>
</receiver>
```

### Level 2: RECEIVER_NOT_EXPORTED (Android 14+)

```kotlin
// Dynamic receiver только для internal broadcasts
ContextCompat.registerReceiver(
    context,
    receiver,
    IntentFilter("com.example.INTERNAL"),
    ContextCompat.RECEIVER_NOT_EXPORTED
)
```

### Level 3: setPackage()

```kotlin
// Отправить broadcast только конкретному приложению
Intent("com.example.ACTION").apply {
    setPackage("com.example.targetapp") // Только этот package получит
    putExtra("secret", "data")
}.also { context.sendBroadcast(it) }
```

### Level 4: Permission на отправку

```kotlin
// Только receivers с MY_PERMISSION получат broadcast
context.sendBroadcast(
    Intent("com.example.SECURE_ACTION"),
    "com.example.MY_PERMISSION"
)
```

```xml
<!-- Объявление custom permission -->
<permission
    android:name="com.example.MY_PERMISSION"
    android:protectionLevel="signature" />

<!-- Receiver запрашивает permission -->
<uses-permission android:name="com.example.MY_PERMISSION" />
```

### Level 5: Permission на регистрацию

```kotlin
// Принимать broadcast только от sender с SENDER_PERMISSION
context.registerReceiver(
    receiver,
    IntentFilter("com.example.ACTION"),
    "com.example.SENDER_PERMISSION", // Sender должен иметь этот permission
    null // Handler
)
```

### Level 6: Signature-level permission (максимальная защита)

```xml
<!-- В обоих приложениях (sender и receiver), подписанных одним ключом -->
<permission
    android:name="com.example.SIGNATURE_BROADCAST"
    android:protectionLevel="signature" />

<uses-permission android:name="com.example.SIGNATURE_BROADCAST" />
```

```kotlin
// Sender
context.sendBroadcast(
    Intent("com.example.SECURE"),
    "com.example.SIGNATURE_BROADCAST"
)

// Receiver — только приложения с тем же signing key получат
context.registerReceiver(
    receiver,
    IntentFilter("com.example.SECURE"),
    "com.example.SIGNATURE_BROADCAST",
    null
)
```

### Уязвимости и защита

```
Типичные уязвимости:                Защита:
┌─────────────────────────┐        ┌──────────────────────────────┐
│                         │        │                              │
│ 1. Exported receiver    │  ────→ │ exported="false" или         │
│    без проверки sender  │        │ RECEIVER_NOT_EXPORTED        │
│                         │        │                              │
│ 2. Intent spoofing      │  ────→ │ Проверка callingUid/Pid      │
│    (поддельный broadcast)│       │ или signature permission     │
│                         │        │                              │
│ 3. Data leak через      │  ────→ │ Permission на sendBroadcast  │
│    broadcast extras     │        │ + setPackage()               │
│                         │        │                              │
│ 4. Replay attacks       │  ────→ │ Nonce/timestamp в extras     │
│    (повторная отправка) │        │ + проверка freshness          │
│                         │        │                              │
│ 5. Privilege escalation │  ────→ │ Минимальные permissions      │
│    через broadcast chain│        │ + ordered broadcast abort    │
│                         │        │                              │
└─────────────────────────┘        └──────────────────────────────┘
```

```kotlin
// Пример защиты от spoofing в receiver
class SecureReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Проверка: broadcast от системы?
        val senderUid = intent.getIntExtra("android.intent.extra.UID", -1)

        // Для ordered broadcast: проверить отправителя
        if (isOrderedBroadcast) {
            // Проверить, что данные не были модифицированы
            val checksum = intent.getStringExtra("checksum")
            if (!verifyChecksum(intent, checksum)) {
                abortBroadcast()
                return
            }
        }

        // Обработка только валидных broadcasts
        processSecurely(context, intent)
    }
}
```

---

## LocalBroadcastManager → SharedFlow / EventBus

### Почему LocalBroadcastManager deprecated

```
LocalBroadcastManager (deprecated 1.1.0-alpha01):
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ПРОБЛЕМЫ:                                                   │
│                                                              │
│  1. Layer violations                                         │
│     → Любой компонент может слушать любой другой             │
│     → Нет architectural boundaries                           │
│     → Хуже чем EventBus для modularity                       │
│                                                              │
│  2. Intent overhead                                          │
│     → Intent для in-process коммуникации — избыточно         │
│     → Parceling/unparceling для передачи в том же процессе   │
│     → Лишние аллокации (Intent, Bundle, extras)              │
│                                                              │
│  3. Not type-safe                                            │
│     → Строковые actions: typo = silent failure               │
│     → Extras без compile-time проверки типов                 │
│     → ClassCastException в runtime                           │
│                                                              │
│  4. Нет backpressure                                         │
│     → Если receiver медленный — events теряются              │
│     → Нет replay для новых подписчиков                       │
│                                                              │
│  5. Не lifecycle-aware                                       │
│     → Manual register/unregister = leak potential             │
│     → Нет автоматической привязки к lifecycle                 │
│                                                              │
│  ЗАМЕНЫ:                                                     │
│     → SharedFlow: broadcast semantics (0..N subscribers)     │
│     → StateFlow: conflated state (always latest value)       │
│     → Channel: point-to-point (exactly 1 consumer)           │
│     → LiveData: lifecycle-aware observable                   │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Миграция: типизированный EventBus на SharedFlow

```kotlin
// ===== EventBus на SharedFlow =====

// 1. Определяем типизированные события
sealed interface AppEvent {
    data class UserLoggedIn(val userId: String, val token: String) : AppEvent
    data class UserLoggedOut(val reason: LogoutReason) : AppEvent
    data class DataUpdated(val entityType: String, val entityId: Long) : AppEvent
    data class NetworkChanged(val isConnected: Boolean) : AppEvent
    data object AppForegrounded : AppEvent
    data object AppBackgrounded : AppEvent
}

enum class LogoutReason { USER_ACTION, TOKEN_EXPIRED, FORCE_LOGOUT }

// 2. Singleton EventBus
object EventBus {
    private val _events = MutableSharedFlow<AppEvent>(
        replay = 0,                          // Не хранить прошлые события
        extraBufferCapacity = 64,            // Буфер для быстрых emit
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<AppEvent> = _events.asSharedFlow()

    suspend fun emit(event: AppEvent) {
        _events.emit(event)
    }

    // Для вызова из non-suspending context
    fun tryEmit(event: AppEvent): Boolean {
        return _events.tryEmit(event)
    }
}

// 3. Отправка события
class AuthRepository @Inject constructor() {
    suspend fun login(credentials: Credentials): Result<User> {
        return try {
            val user = api.login(credentials)
            EventBus.emit(AppEvent.UserLoggedIn(user.id, user.token))
            Result.success(user)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun logout(reason: LogoutReason = LogoutReason.USER_ACTION) {
        tokenStorage.clear()
        EventBus.emit(AppEvent.UserLoggedOut(reason))
    }
}

// 4. Подписка (lifecycle-aware)
class ProfileFragment : Fragment() {

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                EventBus.events
                    .filterIsInstance<AppEvent.UserLoggedOut>()
                    .collect { event ->
                        when (event.reason) {
                            LogoutReason.TOKEN_EXPIRED -> showReloginDialog()
                            LogoutReason.FORCE_LOGOUT -> navigateToLogin()
                            LogoutReason.USER_ACTION -> navigateToLogin()
                        }
                    }
            }
        }
    }
}
```

### Scoped EventBus через Hilt

```kotlin
// Scoped EventBus — лучше чем Singleton для модульности
@Module
@InstallIn(SingletonComponent::class)
object EventModule {

    @Provides
    @Singleton
    fun provideEventBus(): MutableSharedFlow<AppEvent> {
        return MutableSharedFlow(
            replay = 0,
            extraBufferCapacity = 64,
            onBufferOverflow = BufferOverflow.DROP_OLDEST
        )
    }
}

// Repository emits
class DataRepository @Inject constructor(
    private val eventBus: MutableSharedFlow<AppEvent>
) {
    suspend fun updateData(data: Data) {
        dao.update(data)
        eventBus.emit(AppEvent.DataUpdated("data", data.id))
    }
}

// ViewModel collects
@HiltViewModel
class MainViewModel @Inject constructor(
    eventBus: MutableSharedFlow<AppEvent>
) : ViewModel() {

    val dataUpdates = eventBus
        .filterIsInstance<AppEvent.DataUpdated>()
        .shareIn(viewModelScope, SharingStarted.WhileSubscribed(5000))
}
```

### SharedFlow vs StateFlow vs Channel — выбор

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  SharedFlow:                                                    │
│  ├── Семантика: Event bus (fire-and-forget)                     │
│  ├── Подписчики: 0..N (broadcast)                               │
│  ├── Replay: настраиваемый (0 = только новые)                   │
│  ├── Backpressure: DROP_OLDEST / SUSPEND / DROP_LATEST          │
│  └── Use case: Notifications, analytics events, navigation      │
│                                                                 │
│  StateFlow:                                                     │
│  ├── Семантика: Observable state (always latest value)          │
│  ├── Подписчики: 0..N (broadcast)                               │
│  ├── Replay: всегда 1 (latest value)                            │
│  ├── Conflation: duplicate values пропускаются                  │
│  └── Use case: UI state, connection status, loading state       │
│                                                                 │
│  Channel:                                                       │
│  ├── Семантика: Queue (point-to-point)                          │
│  ├── Подписчики: 1 consumer (fan-out)                           │
│  ├── Replay: нет                                                │
│  ├── Delivery: exactly-once                                     │
│  └── Use case: Work distribution, one-time events               │
│                                                                 │
│  Callback Flow:                                                 │
│  ├── Семантика: Bridge callback API → Flow                      │
│  ├── Use case: BroadcastReceiver → Flow adapter                 │
│  └── Пример: см. ниже                                           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### BroadcastReceiver → callbackFlow adapter

```kotlin
// Обёртка BroadcastReceiver в Flow через callbackFlow
fun Context.broadcastFlow(
    vararg actions: String,
    exported: Boolean = false
): Flow<Intent> = callbackFlow {
    val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            trySend(intent)
        }
    }

    val filter = IntentFilter().apply {
        actions.forEach { addAction(it) }
    }

    val flag = if (exported) {
        ContextCompat.RECEIVER_EXPORTED
    } else {
        ContextCompat.RECEIVER_NOT_EXPORTED
    }

    ContextCompat.registerReceiver(this@broadcastFlow, receiver, filter, flag)

    awaitClose {
        unregisterReceiver(receiver)
    }
}

// Использование:
lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        applicationContext.broadcastFlow(
            Intent.ACTION_BATTERY_CHANGED,
            exported = false
        ).map { intent ->
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            level * 100f / scale
        }.collect { batteryPct ->
            updateBatteryIndicator(batteryPct)
        }
    }
}
```

---

## Тестирование Broadcasts

### Unit-тесты с Robolectric

```kotlin
@RunWith(RobolectricTestRunner::class)
class BootReceiverTest {

    @Test
    fun `onReceive with BOOT_COMPLETED schedules work`() {
        // Arrange
        val context = ApplicationProvider.getApplicationContext<Application>()
        val receiver = BootReceiver()
        val intent = Intent(Intent.ACTION_BOOT_COMPLETED)

        // Act
        receiver.onReceive(context, intent)

        // Assert
        val workManager = WorkManager.getInstance(context)
        val workInfos = workManager
            .getWorkInfosForUniqueWork("sync")
            .get()
        assertThat(workInfos).hasSize(1)
        assertThat(workInfos[0].state).isEqualTo(WorkInfo.State.ENQUEUED)
    }
}
```

### Проверка broadcast с ShadowApplication

```kotlin
@RunWith(RobolectricTestRunner::class)
class BroadcastSenderTest {

    @Test
    fun `sendBroadcast creates correct intent`() {
        val context = ApplicationProvider.getApplicationContext<Application>()
        val shadowApp = Shadows.shadowOf(context as Application)

        // Act
        context.sendBroadcast(Intent("com.example.TEST_ACTION").apply {
            putExtra("key", "value")
        })

        // Assert
        val broadcastIntents = shadowApp.broadcastIntents
        assertThat(broadcastIntents).hasSize(1)
        assertThat(broadcastIntents[0].action).isEqualTo("com.example.TEST_ACTION")
        assertThat(broadcastIntents[0].getStringExtra("key")).isEqualTo("value")
    }
}
```

### Instrumented тесты

```kotlin
@RunWith(AndroidJUnit4::class)
class BroadcastInstrumentedTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun receiver_responds_to_custom_broadcast() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext

        // Создаём receiver и ждём broadcast
        val latch = CountDownLatch(1)
        var receivedData: String? = null

        val receiver = object : BroadcastReceiver() {
            override fun onReceive(ctx: Context, intent: Intent) {
                receivedData = intent.getStringExtra("data")
                latch.countDown()
            }
        }

        ContextCompat.registerReceiver(
            context, receiver,
            IntentFilter("com.example.TEST"),
            ContextCompat.RECEIVER_NOT_EXPORTED
        )

        // Отправляем broadcast
        context.sendBroadcast(Intent("com.example.TEST").apply {
            putExtra("data", "hello")
        })

        // Ждём получения
        assertTrue(latch.await(5, TimeUnit.SECONDS))
        assertEquals("hello", receivedData)

        context.unregisterReceiver(receiver)
    }
}
```

### Тестирование goAsync()

```kotlin
@RunWith(RobolectricTestRunner::class)
class AsyncReceiverTest {

    @Test
    fun `goAsync receiver completes successfully`() = runTest {
        val context = ApplicationProvider.getApplicationContext<Application>()
        val receiver = DataSyncReceiver()

        // Mock the network call
        mockkStatic("com.example.NetworkKt")
        coEvery { fetchFromNetwork() } returns TestData("result")

        val intent = Intent("com.example.SYNC")
        receiver.onReceive(context, intent)

        // Дать время async обработке
        advanceUntilIdle()

        // Verify
        coVerify { fetchFromNetwork() }
    }
}
```

---

## Системные Broadcasts — полный каталог

### По категориям

```
SYSTEM BROADCASTS CATALOG:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ═══ BOOT & SHUTDOWN ═══                                        │
│  BOOT_COMPLETED           Загрузка завершена (manifest-exempt)   │
│  LOCKED_BOOT_COMPLETED    Direct Boot загрузка (до разблокировки)│
│  ACTION_SHUTDOWN          Устройство выключается                 │
│  QUICKBOOT_POWERON        Quick Boot (vendor)                    │
│                                                                  │
│  ═══ PACKAGE ═══                                                │
│  PACKAGE_ADDED            Приложение установлено                 │
│  PACKAGE_REMOVED          Приложение удалено                     │
│  PACKAGE_REPLACED         Приложение обновлено                   │
│  MY_PACKAGE_REPLACED      Собственное приложение обновлено       │
│  PACKAGE_DATA_CLEARED     Данные приложения очищены              │
│  PACKAGE_FULLY_REMOVED    Полное удаление (с данными)            │
│                                                                  │
│  ═══ POWER ═══                                                  │
│  BATTERY_CHANGED          Состояние батареи (sticky!)            │
│  BATTERY_LOW              Батарея низкая                         │
│  BATTERY_OKAY             Батарея OK (после LOW)                 │
│  ACTION_POWER_CONNECTED   Зарядка подключена                     │
│  ACTION_POWER_DISCONNECTED Зарядка отключена                     │
│                                                                  │
│  ═══ CONNECTIVITY ═══                                           │
│  CONNECTIVITY_CHANGE      Сеть изменилась (NOT manifest-exempt!) │
│  WIFI_STATE_CHANGED       WiFi состояние                         │
│  AIRPLANE_MODE_CHANGED    Авиарежим                              │
│                                                                  │
│  ═══ DISPLAY ═══                                                │
│  SCREEN_ON                Экран включился                        │
│  SCREEN_OFF               Экран выключился                       │
│  USER_PRESENT             Устройство разблокировано              │
│  CONFIGURATION_CHANGED    Конфигурация изменена (поворот и др.)  │
│                                                                  │
│  ═══ TIME ═══                                                   │
│  TIME_SET                 Время установлено (manifest-exempt)    │
│  TIMEZONE_CHANGED         Часовой пояс изменён (manifest-exempt) │
│  TIME_TICK                Каждую минуту (NOT manifest-exempt!)   │
│                                                                  │
│  ═══ LOCALE ═══                                                 │
│  LOCALE_CHANGED           Язык/регион изменён (manifest-exempt)  │
│                                                                  │
│  ═══ HARDWARE ═══                                               │
│  USB_DEVICE_ATTACHED      USB подключено (manifest-exempt)       │
│  USB_DEVICE_DETACHED      USB отключено                          │
│  HEADSET_PLUG             Наушники подключены/отключены           │
│                                                                  │
│  ═══ STORAGE ═══                                                │
│  DEVICE_STORAGE_LOW       Мало места на устройстве               │
│  DEVICE_STORAGE_OK        Место на устройстве OK                 │
│  MEDIA_MOUNTED            SD карта подключена                    │
│  MEDIA_REMOVED            SD карта извлечена                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Manifest-exempt broadcasts (полный список для API 34+)

| Broadcast | Примечание |
|-----------|------------|
| `BOOT_COMPLETED` | + `RECEIVE_BOOT_COMPLETED` permission |
| `LOCKED_BOOT_COMPLETED` | Direct Boot, `directBootAware=true` |
| `LOCALE_CHANGED` | Смена языка/региона |
| `MY_PACKAGE_REPLACED` | Собственное обновление |
| `MY_PACKAGE_FULLY_REMOVED` | Полное удаление |
| `MY_PACKAGE_SUSPENDED/UNSUSPENDED` | Приостановка приложения |
| `PACKAGE_ADDED/CHANGED/REMOVED` | Изменения в других packages |
| `PACKAGES_SUSPENDED/UNSUSPENDED` | Массовая приостановка |
| `UID_REMOVED` | UID удалён |
| `USB_DEVICE_ATTACHED/DETACHED` | USB hardware |
| `USB_ACCESSORY_ATTACHED/DETACHED` | USB аксессуары |
| `ACTION_TIMEZONE_CHANGED` | Часовой пояс |
| `ACTION_TIME_SET` | Время |
| `SMS_DELIVER` | SMS (default SMS app) |
| `WAP_PUSH_DELIVER` | MMS (default SMS app) |
| `ACTION_CARRIER_CONFIG_CHANGED` | Оператор |
| `ACTION_SIM_STATE_CHANGED` | SIM |
| `LOGIN_ACCOUNTS_CHANGED` | Аккаунты |
| `HEADSET_PLUG` | Наушники |

---

## Производительность и лучшие практики

### ANR Timeline

```
Broadcast ANR Detection:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Foreground broadcast:                                           │
│  0s ─────────── 10s ──────────→ ANR                             │
│  │  onReceive() │                                                │
│  │  должен      │                                                │
│  │  завершиться │                                                │
│                                                                  │
│  Background broadcast:                                           │
│  0s ─────────────────────────── 60s ──────────→ ANR             │
│  │  onReceive()                  │                               │
│  │  больше времени               │                               │
│                                                                  │
│  Как AMS отслеживает:                                           │
│  1. BroadcastQueue.setBroadcastTimeoutLocked(timeout)            │
│  2. Handler.sendMessageAtTime(BROADCAST_TIMEOUT_MSG, timeout)    │
│  3. Если finishReceiver() не вызван до timeout:                  │
│     → broadcastTimeoutLocked() → appNotResponding()              │
│     → AMS записывает ANR trace → показывает dialog              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Best Practices

```kotlin
// ✅ DO: Минимальная работа в onReceive()
class GoodReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Быстро: schedule work и return
        val data = intent.getStringExtra("data") ?: return
        WorkManager.getInstance(context).enqueue(
            OneTimeWorkRequestBuilder<ProcessWorker>()
                .setInputData(workDataOf("data" to data))
                .build()
        )
    }
}

// ❌ DON'T: Тяжёлая работа в onReceive()
class BadReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Плохо: network call на main thread
        val response = URL("https://api.example.com").readText()
        // Плохо: тяжёлая обработка
        val parsed = parseXml(response)
        // Плохо: disk I/O
        File(context.filesDir, "data.json").writeText(parsed)
    }
}
```

```kotlin
// ✅ DO: Lifecycle-aware registration
class LifecycleAwareActivity : AppCompatActivity() {
    private val receiver = MyReceiver()

    override fun onStart() {
        super.onStart()
        ContextCompat.registerReceiver(
            this, receiver, IntentFilter("ACTION"),
            ContextCompat.RECEIVER_NOT_EXPORTED
        )
    }

    override fun onStop() {
        unregisterReceiver(receiver)
        super.onStop()
    }
}

// ❌ DON'T: Регистрация в onCreate без unregister
class LeakyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // LEAK: registerReceiver без парного unregisterReceiver
        registerReceiver(receiver, IntentFilter("ACTION"))
    }
}
```

### Производительность: сколько broadcast — это "много"?

```
Performance Guidelines:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Кол-во receivers    │ Производительность                        │
│  ────────────────────┼───────────────────────────────────────── │
│  1-10                │ ✅ Нормально                              │
│  10-50               │ ⚠️ Следить за временем доставки            │
│  50-100              │ ❌ Проблемы с батареей и CPU               │
│  100+                │ 💀 "Thundering herd" — именно это          │
│                      │    починил Android 8.0                    │
│                                                                  │
│  Рекомендации:                                                   │
│  • Использовать explicit broadcasts где возможно                  │
│  • Предпочитать dynamic registration с lifecycle                 │
│  • Для internal events: SharedFlow, не Broadcast                 │
│  • Для connectivity: NetworkCallback, не CONNECTIVITY_CHANGE     │
│  • Для battery: BatteryManager API, не BATTERY_CHANGED receiver  │
│  • Для location: LocationManager/FusedProvider, не broadcasts    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Android 15: Broadcast deferral для cached processes

```
Android 15+ Broadcast Deferral:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Cached process (не foreground, не visible):                     │
│                                                                  │
│  ┌─────────┐   broadcast   ┌───────────────┐                    │
│  │ system   │ ────────────→ │  DEFERRED     │                    │
│  │ server   │               │  (не доставлен│                    │
│  └─────────┘               │   пока cached) │                    │
│                             └───────┬───────┘                    │
│                                     │                            │
│                                     │ App выходит из cached      │
│                                     │ (user открыл, FGS, etc.)   │
│                                     ▼                            │
│                             ┌───────────────┐                    │
│                             │  DELIVERED    │                    │
│                             │  (доставлен    │                    │
│                             │   после выхода │                    │
│                             │   из cached)   │                    │
│                             └───────────────┘                    │
│                                                                  │
│  Исключения (всегда доставляются):                               │
│  • ACTION_BOOT_COMPLETED                                         │
│  • ACTION_LOCALE_CHANGED                                         │
│  • Другие manifest-exempt broadcasts                             │
│  • Broadcasts с FLAG_RECEIVER_FOREGROUND                         │
│                                                                  │
│  Цель: уменьшить wake-ups cached processes → батарея             │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## Broadcast Decision Tree

```
Нужно ли использовать Broadcast?
┌────────────────────────────────────────────────────────────────┐
│                                                                │
│  Коммуникация МЕЖДУ приложениями?                              │
│  ├── Да → Broadcast (explicit, с permissions)                  │
│  └── Нет ↓                                                     │
│                                                                │
│  Нужно получить СИСТЕМНОЕ событие?                             │
│  ├── Да → Broadcast (dynamic receiver)                         │
│  │   ├── Connectivity → NetworkCallback (лучше!)               │
│  │   ├── Battery → BatteryManager API                          │
│  │   ├── Boot → Manifest receiver (exempt)                     │
│  │   └── Другие → Dynamic receiver с lifecycle                 │
│  └── Нет ↓                                                     │
│                                                                │
│  Коммуникация внутри СВОЕГО приложения?                        │
│  ├── State updates → StateFlow / LiveData                      │
│  ├── One-time events → SharedFlow / Channel                    │
│  ├── Between ViewModel → SharedFlow в shared scope             │
│  └── Between modules → EventBus на SharedFlow                  │
│                                                                │
│  Фоновая задача?                                               │
│  ├── Периодическая → WorkManager                               │
│  ├── One-time deferred → WorkManager                           │
│  ├── Immediate → Coroutines / Service                          │
│  └── Exact time → AlarmManager + BroadcastReceiver             │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

---

## Распространённые паттерны

### Pattern 1: Restart-safe initialization

```kotlin
// Инициализация, выживающая перезагрузку
class AppInitReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_MY_PACKAGE_REPLACED -> {
                // Перезапланировать periodic work после boot/update
                initializeApp(context)
            }
        }
    }

    private fun initializeApp(context: Context) {
        // 1. Перезапустить periodic sync
        WorkManager.getInstance(context).enqueueUniquePeriodicWork(
            "periodic_sync",
            ExistingPeriodicWorkPolicy.KEEP,
            PeriodicWorkRequestBuilder<SyncWorker>(1, TimeUnit.HOURS)
                .setConstraints(
                    Constraints.Builder()
                        .setRequiredNetworkType(NetworkType.CONNECTED)
                        .build()
                )
                .build()
        )

        // 2. Восстановить alarms
        AlarmScheduler.rescheduleAll(context)

        // 3. Обновить notification channels
        NotificationHelper.createChannels(context)
    }
}
```

```xml
<receiver
    android:name=".AppInitReceiver"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
        <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
    </intent-filter>
</receiver>

<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
```

### Pattern 2: Screen on/off tracking

```kotlin
// Отслеживание включения/выключения экрана
class ScreenStateTracker(private val context: Context) {

    private val _screenState = MutableStateFlow(true)
    val screenState: StateFlow<Boolean> = _screenState.asStateFlow()

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(ctx: Context, intent: Intent) {
            when (intent.action) {
                Intent.ACTION_SCREEN_ON -> _screenState.value = true
                Intent.ACTION_SCREEN_OFF -> _screenState.value = false
            }
        }
    }

    fun start() {
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_SCREEN_ON)
            addAction(Intent.ACTION_SCREEN_OFF)
        }
        // SCREEN_ON/OFF — protected broadcasts, флаг не нужен
        context.registerReceiver(receiver, filter)
    }

    fun stop() {
        try {
            context.unregisterReceiver(receiver)
        } catch (e: IllegalArgumentException) {
            // Already unregistered
        }
    }
}
```

### Pattern 3: Package install/uninstall observer

```kotlin
// Отслеживание установки/удаления приложений
class PackageObserver(context: Context) {

    private val _packageEvents = MutableSharedFlow<PackageEvent>(
        extraBufferCapacity = 10
    )
    val packageEvents: SharedFlow<PackageEvent> = _packageEvents.asSharedFlow()

    sealed interface PackageEvent {
        data class Installed(val packageName: String) : PackageEvent
        data class Removed(val packageName: String) : PackageEvent
        data class Updated(val packageName: String) : PackageEvent
    }

    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(ctx: Context, intent: Intent) {
            val packageName = intent.data?.schemeSpecificPart ?: return
            val replacing = intent.getBooleanExtra(Intent.EXTRA_REPLACING, false)

            val event = when (intent.action) {
                Intent.ACTION_PACKAGE_ADDED -> {
                    if (replacing) PackageEvent.Updated(packageName)
                    else PackageEvent.Installed(packageName)
                }
                Intent.ACTION_PACKAGE_REMOVED -> {
                    if (!replacing) PackageEvent.Removed(packageName)
                    else null
                }
                else -> null
            }

            event?.let { _packageEvents.tryEmit(it) }
        }
    }

    init {
        val filter = IntentFilter().apply {
            addAction(Intent.ACTION_PACKAGE_ADDED)
            addAction(Intent.ACTION_PACKAGE_REMOVED)
            addDataScheme("package")
        }
        ContextCompat.registerReceiver(
            context, receiver, filter,
            ContextCompat.RECEIVER_EXPORTED // Нужно видеть broadcasts от PMS
        )
    }
}
```

### Pattern 4: Locale change handling

```kotlin
// Обработка смены языка в runtime
class LocaleReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_LOCALE_CHANGED) {
            // 1. Обновить cached strings
            StringCache.invalidate()

            // 2. Перезапустить active activities (опционально)
            // Обычно система делает это автоматически через configChanges

            // 3. Обновить notifications
            NotificationHelper.updateAllNotifications(context)

            // 4. Обновить widgets
            val widgetManager = AppWidgetManager.getInstance(context)
            val widgetIds = widgetManager.getAppWidgetIds(
                ComponentName(context, MyWidgetProvider::class.java)
            )
            val updateIntent = Intent(context, MyWidgetProvider::class.java).apply {
                action = AppWidgetManager.ACTION_APPWIDGET_UPDATE
                putExtra(AppWidgetManager.EXTRA_APPWIDGET_IDS, widgetIds)
            }
            context.sendBroadcast(updateIntent)
        }
    }
}
```

---

## Мифы и заблуждения

| # | Миф | Реальность |
|---|-----|-----------|
| 1 | "LocalBroadcastManager — лучший способ для внутренних событий" | Deprecated с 1.1.0-alpha01. Используйте SharedFlow/StateFlow: type-safe, coroutine-aware, нет Intent overhead |
| 2 | "goAsync() снимает 10-секундный лимит" | Нет. goAsync() позволяет обработку в другом потоке, но ANR timeout (10s fg / 60s bg) остаётся. Для длительных задач → WorkManager |
| 3 | "Ordered broadcasts гарантируют порядок между приложениями" | Android 16: cross-process priority НЕ гарантирован. Только внутри одного процесса порядок определён |
| 4 | "Manifest receivers всегда работают" | С Android 8+ большинство implicit broadcasts НЕ доставляются manifest receivers. Только exempt list работает |
| 5 | "Broadcast — для фоновых задач" | Нет. Broadcast — для уведомлений о событиях. Для фоновых задач: WorkManager, Coroutines, Service |
| 6 | "Sticky broadcasts актуальны" | Deprecated с API 21 (Android 5.0). Единственный оставшийся — ACTION_BATTERY_CHANGED. Замена: StateFlow |
| 7 | "BroadcastReceiver безопасен по умолчанию" | Без exported=false или RECEIVER_NOT_EXPORTED любое приложение может отправить broadcast вашему receiver |
| 8 | "Dynamic receivers не требуют exported флага" | Android 14 (targetSdk 34) **требует** RECEIVER_EXPORTED или RECEIVER_NOT_EXPORTED для всех non-protected broadcasts |
| 9 | "sendBroadcast() — синхронный вызов" | Нет. sendBroadcast() — async: Intent отправляется в system_server через Binder, обрабатывается в BroadcastQueue, доставляется через Handler |
| 10 | "Broadcast доставляется мгновенно" | Нет. Normal broadcast идёт: app → Binder IPC → AMS → BroadcastQueue → Handler msg → Binder IPC → receiver. Latency может быть 10-100+ ms |
| 11 | "Можно отправлять большие данные через broadcast" | Binder transaction buffer = 1 MB (shared). Большие extras → TransactionTooLargeException. Передавайте ID/URI, не данные |
| 12 | "unregisterReceiver() можно вызвать в onDestroy()" | Опасно: onDestroy() может не вызваться при kill process. Лучше: onStop() для Activity, onDestroyView() для Fragment |

---

## CS-фундамент

| Концепция | Как используется в Broadcast | Пример в Android |
|-----------|------------------------------|-------------------|
| **Publish-Subscribe** | sendBroadcast (publish) → onReceive (subscribe). Отправитель не знает получателей | Context.sendBroadcast(intent) → все matching receivers |
| **Observer Pattern** | BroadcastReceiver наблюдает за событиями через IntentFilter | registerReceiver(receiver, filter) |
| **Message Queue** | BroadcastQueue в system_server — FIFO очередь broadcast records | mParallelBroadcasts, mDispatcher |
| **Priority Queue** | Ordered broadcasts сортируются по priority IntentFilter | android:priority="100" → обрабатывается первым |
| **Event Bus** | Broadcast = межпроцессный event bus; SharedFlow = внутрипроцессный | System broadcasts, custom broadcasts |
| **Binder IPC** | Все broadcast проходят через Binder: sender → AMS → receiver | IIntentReceiver.performReceive() |
| **Chain of Responsibility** | Ordered broadcast: каждый receiver решает — обработать или передать дальше | abortBroadcast(), setResult*() |
| **Decorator Pattern** | ReceiverDispatcher оборачивает BroadcastReceiver для IPC | LoadedApk.ReceiverDispatcher |

---

## Связи

### Фундамент
- **[[android-intent-internals]]** — Broadcast использует Intent; IntentFilter matching определяет получателей
- **[[android-app-components]]** — BroadcastReceiver один из 4 фундаментальных компонентов Android
- **[[android-handler-looper]]** — onReceive() выполняется на main thread через Handler; BroadcastQueue использует Handler для scheduling

### Механизмы доставки
- **[[android-art-zygote]]** — Binder IPC используется для cross-process broadcast delivery
- **[[android-process-memory]]** — Broadcast priority и process lifecycle; LMK может убить процесс после onReceive()

### Альтернативы и миграция
- **[[android-background-work]]** — WorkManager как замена broadcast для фоновых задач; goAsync() + WorkManager паттерн
- **[[android-service-internals]]** — Foreground Service для длительных задач из onReceive(); broadcast → service delegation

### Безопасность
- **[[android-permissions-security]]** — Permission-based protection для broadcasts; signature permissions для inter-app communication

### Связанные темы
- **[[android-notifications]]** — Notification system использует внутренние broadcasts; POST_NOTIFICATIONS permission
- **[[android-content-provider-internals]]** — ContentProvider.onCreate() vs BroadcastReceiver для initialization; ContentObserver vs Broadcast patterns

---

## Источники и дальнейшее чтение

**Книги:**
- Vasavada N. (2019). Android Internals: A Confectioner's Cookbook. — внутреннее устройство Android: BroadcastQueue, ActivityManagerService, Binder IPC — механизмы, через которые работает система рассылки событий
- Meier R. (2022). Professional Android, 4th Edition. — комплексное руководство по Android-разработке, включая BroadcastReceiver, Intent filters и security best practices
- Goetz B. (2006). Java Concurrency in Practice. — concurrency на JVM: понимание thread safety критично при работе с goAsync() и фоновыми потоками в broadcast receivers

**Веб-ресурсы:**

| # | Источник | Тип | Описание |
|---|---------|-----|----------|
| 1 | [Broadcasts overview](https://developer.android.com/develop/background-work/background-tasks/broadcasts) | Docs | Официальная документация по Broadcast |
| 2 | [Implicit broadcast exceptions](https://developer.android.com/develop/background-work/background-tasks/broadcasts/broadcast-exceptions) | Docs | Полный список исключений Android 8+ |
| 3 | [Android 14 behavior changes](https://developer.android.com/about/versions/14/behavior-changes-14) | Docs | RECEIVER_EXPORTED/NOT_EXPORTED requirement |
| 4 | [Android 15: broadcast deferral](https://developer.android.com/about/versions/15/behavior-changes-all) | Docs | Broadcast deferral для cached processes |
| 5 | [LocalBroadcastManager deprecated](https://developer.android.com/jetpack/androidx/releases/localbroadcastmanager) | Docs | Deprecation announcement и замены |
| 6 | [SharedFlow documentation](https://kotlin.github.io/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/) | Docs | SharedFlow как замена broadcast для internal events |
| 7 | [Background execution limits](https://developer.android.com/about/versions/oreo/background) | Docs | Android 8.0 implicit broadcast restrictions |
| 8 | [goAsync() API](https://developer.android.com/reference/android/content/BroadcastReceiver#goAsync()) | Docs | PendingResult API reference |
| 9 | [Insecure broadcast receivers](https://developer.android.com/privacy-and-security/risks/insecure-broadcast-receiver) | Docs | Security best practices |
| 10 | [BroadcastQueue.java (AOSP)](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/services/core/java/com/android/server/am/BroadcastQueue.java) | AOSP | Исходный код BroadcastQueue |
| 11 | [BroadcastQueueModernImpl.java (AOSP)](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/services/core/java/com/android/server/am/BroadcastQueueModernImpl.java) | AOSP | Новая реализация очереди (Android 14+) |
| 12 | [ActivityManagerService.java (AOSP)](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/services/core/java/com/android/server/am/ActivityManagerService.java) | AOSP | broadcastIntentLocked() |
| 13 | [LoadedApk.java (AOSP)](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/core/java/android/app/LoadedApk.java) | AOSP | ReceiverDispatcher, InnerReceiver |
| 14 | [Android 16 behavior changes](https://developer.android.com/about/versions/16/behavior-changes-all) | Docs | Cross-process priority changes |

---

## Проверь себя

> [!question]- Почему Android 8+ ограничил implicit broadcast через Manifest и как это влияет на архитектуру?
> До Android 8 каждый implicit broadcast будил все зарегистрированные в Manifest приложения, расходуя батарею и CPU. Ограничение заставляет использовать динамическую регистрацию (registerReceiver) -- приложение получает broadcast только когда активно. Для фоновых задач -- WorkManager с constraints вместо CONNECTIVITY_ACTION.

> [!question]- Сценарий: BroadcastReceiver вызывает сетевой запрос в onReceive(). Приложение крашится. Почему?
> onReceive() выполняется на Main Thread с ограничением ~10 секунд. После возврата из onReceive() процесс может быть убит. Сетевой запрос на Main Thread -> ANR. Решение: запустить корутину через goAsync() (до 30 секунд) или стартовать WorkManager/Foreground Service для долгих операций.


---

## Ключевые карточки

Чем Normal broadcast отличается от Ordered?
?
Normal (sendBroadcast) -- доставляется всем receivers параллельно, нельзя прервать. Ordered (sendOrderedBroadcast) -- доставляется по приоритету, каждый receiver может изменить данные или прервать (abortBroadcast).

Что такое goAsync() в BroadcastReceiver?
?
Возвращает PendingResult, позволяющий выполнить работу в фоновом потоке до 30 секунд (вместо 10). Нужно вызвать finish() на PendingResult по завершении. Процесс остается живым на время работы.

Какие implicit broadcast разрешены через Manifest в Android 8+?
?
BOOT_COMPLETED, LOCALE_CHANGED, USB_ACCESSORY_ATTACHED, SMS_RECEIVED (с permission). Большинство других (CONNECTIVITY_ACTION, POWER_CONNECTED) требуют динамической регистрации через registerReceiver.

Как LocalBroadcastManager отличается от системного broadcast?
?
LocalBroadcastManager (deprecated) работает in-process, без IPC через AMS. Быстрее, безопаснее (не выходит за пределы приложения). Замена: Flow, LiveData, или EventBus.

Что такое sticky broadcast?
?
Broadcast, который сохраняется системой и доставляется новым receivers при регистрации. Deprecated с API 21. Использовался для BATTERY_CHANGED. Замена: запрос текущего состояния через системные API.


---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-content-provider-internals]] | ContentProvider -- другой механизм IPC |
| Углубиться | [[android-handler-looper]] | Как AMS dispatch broadcast через Handler |
| Смежная тема | [[event-driven-architecture]] | Паттерн Pub/Sub в серверной архитектуре |
| Обзор | [[android-overview]] | Вернуться к карте раздела |

