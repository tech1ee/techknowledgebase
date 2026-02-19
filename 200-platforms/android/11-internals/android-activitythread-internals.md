---
title: "ActivityThread: внутри процесса Android-приложения"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/activitythread
  - topic/internals
  - type/deep-dive
  - level/expert
related:
  - "[[android-activity-lifecycle]]"
  - "[[android-handler-looper]]"
  - "[[android-binder-ipc]]"
  - "[[android-system-services]]"
  - "[[android-context-internals]]"
  - "[[android-boot-process]]"
  - "[[android-app-startup-performance]]"
  - "[[android-service-internals]]"
  - "[[android-architecture]]"
cs-foundations: [event-loop, command-pattern, transaction-pattern, proxy-stub, instrumentation-pattern]
prerequisites:
  - "[[android-architecture]]"
  - "[[android-handler-looper]]"
  - "[[android-binder-ipc]]"
  - "[[android-system-services]]"
reading_time: 95
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# ActivityThread: внутри процесса Android-приложения

> **Несмотря на название, ActivityThread — это НЕ поток.** Это главный объект каждого Android-приложения: он получает команды от `system_server` через Binder и переводит их в lifecycle-callbacks. Когда вы пишете `onCreate()`, Framework вызывает его через цепочку из 12 шагов, начинающуюся в `ActivityManagerService`. Понимание этого механизма — ключ к диагностике проблем жизненного цикла, поведения при process death, тонкостей configuration changes и тестирования через Instrumentation.

```
┌─────────────────────────────────────────────────────────────────┐
│                    ОБЩАЯ КАРТИНА                                │
│                                                                 │
│   system_server (AMS)                     App Process           │
│   ┌───────────────┐    Binder IPC    ┌──────────────────┐      │
│   │ ActivityManager│ ──────────────► │ ApplicationThread │      │
│   │   Service      │                 │   (Binder stub)   │      │
│   │               │ ◄────────────── │                    │      │
│   │               │    Binder IPC    └────────┬───────────┘      │
│   └───────────────┘                          │ post()           │
│                                              ▼                  │
│                                     ┌──────────────────┐        │
│                                     │    Handler H      │        │
│                                     │  (Main Thread)    │        │
│                                     └────────┬───────────┘       │
│                                              │                  │
│                                              ▼                  │
│                                     ┌──────────────────┐        │
│                                     │ TransactionExecutor│       │
│                                     └────────┬───────────┘       │
│                                              │                  │
│                                              ▼                  │
│                                     ┌──────────────────┐        │
│                                     │ Instrumentation   │        │
│                                     └────────┬───────────┘       │
│                                              │                  │
│                                              ▼                  │
│                                     ┌──────────────────┐        │
│                                     │    Activity       │        │
│                                     │  onCreate/onStart │        │
│                                     │  onResume/...     │        │
│                                     └──────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Зачем это нужно

| Проблема | Без знания ActivityThread | С пониманием ActivityThread |
|----------|--------------------------|----------------------------|
| Почему lifecycle вызывается в определённом порядке? | Магия фреймворка | `TransactionExecutor` обеспечивает state machine: нельзя перейти в `ON_RESUME` не пройдя `ON_START` |
| Поведение при process death | Непредсказуемо | LMK убивает процесс без `onDestroy()`; AMS хранит `savedInstanceState` и восстанавливает через новый `ActivityThread` |
| Configuration changes | Просто пересоздание | `ActivityClientRecord` сохраняет `ViewModelStore`; `handleRelaunchActivity()` уничтожает и создаёт Activity заново |
| Почему `ContentProvider.onCreate()` блокирует старт? | Неясно | `handleBindApplication()` инициализирует ContentProvider ДО `Application.onCreate()` |
| Instrumentation для тестирования | Чёрный ящик | `Instrumentation` — перехватчик между `ActivityThread` и `Activity`, позволяет Espresso контролировать lifecycle |
| `TransactionTooLargeException` | Необъяснимый краш | `savedInstanceState` передаётся через Binder buffer (1 МБ лимит) |
| Почему `onStop()` вызывается с задержкой? | Баг? | `StopActivityItem` исполняется после завершения предыдущей транзакции |
| Как ViewModel переживает поворот экрана? | "Магия AAC" | `ViewModelStore` хранится в `ActivityClientRecord`, который переиспользуется при recreate |

---

## ActivityThread.main() — настоящая точка входа

### Что такое ActivityThread

`ActivityThread` — это **не** поток (`Thread`). Это обычный Java-класс, единственный экземпляр которого (`sCurrentActivityThread`) живёт в каждом процессе приложения. Он является:

1. **Точкой входа** — метод `main()` вызывается после fork от Zygote
2. **Диспетчером** — получает команды от `system_server` через Binder
3. **Менеджером состояния** — хранит все `ActivityClientRecord`, `ProviderClientRecord`, `ServiceInfo`
4. **Обработчиком** — вызывает `handleLaunchActivity()`, `handleBindApplication()` и т.д.

### Метод main()

```java
// frameworks/base/core/java/android/app/ActivityThread.java (упрощённо)
public static void main(String[] args) {
    // 1. Подготовка Looper главного потока
    Looper.prepareMainLooper();

    // 2. Создание единственного экземпляра ActivityThread
    ActivityThread thread = new ActivityThread();

    // 3. Привязка к system_server через AMS
    thread.attach(false, startSeq);

    // 4. Получение Handler H (sMainThreadHandler)
    if (sMainThreadHandler == null) {
        sMainThreadHandler = thread.getHandler();
    }

    // 5. Запуск бесконечного цикла обработки сообщений
    Looper.loop();

    // Сюда выполнение НИКОГДА не дойдёт в нормальных условиях
    throw new RuntimeException("Main thread loop unexpectedly exited");
}
```

### Последовательность инициализации

```
┌─────────────────────────────────────────────────────────────────────┐
│              ActivityThread.main() — ПОСЛЕДОВАТЕЛЬНОСТЬ             │
│                                                                     │
│  Zygote fork                                                        │
│      │                                                              │
│      ▼                                                              │
│  ┌─────────────────────────────┐                                    │
│  │ 1. Looper.prepareMainLooper│  Создаёт MessageQueue              │
│  │    ()                       │  для главного потока               │
│  └──────────────┬──────────────┘                                    │
│                 ▼                                                    │
│  ┌─────────────────────────────┐                                    │
│  │ 2. new ActivityThread()     │  Создаёт экземпляр,               │
│  │                             │  инициализирует Handler H          │
│  └──────────────┬──────────────┘                                    │
│                 ▼                                                    │
│  ┌─────────────────────────────┐                                    │
│  │ 3. thread.attach(false)     │  Вызывает AMS.attachApplication() │
│  │                             │  через Binder (IActivityManager)  │
│  └──────────────┬──────────────┘                                    │
│                 │                                                    │
│                 │  ◄── AMS теперь знает про этот процесс           │
│                 │      и может отправлять команды                   │
│                 ▼                                                    │
│  ┌─────────────────────────────┐                                    │
│  │ 4. Looper.loop()           │  Бесконечный цикл:                │
│  │                             │  берёт Message из очереди         │
│  │                             │  и отправляет в Handler H         │
│  └─────────────────────────────┘                                    │
│                 │                                                    │
│                 ▼                                                    │
│          ┌─────────────┐                                            │
│          │  NEVER ENDS │                                            │
│          └─────────────┘                                            │
└─────────────────────────────────────────────────────────────────────┘
```

### attach() — регистрация в system_server

Метод `attach(false, startSeq)` выполняет критически важную операцию — регистрирует процесс приложения в `ActivityManagerService`:

```java
// Упрощённый attach()
private void attach(boolean system, long startSeq) {
    sCurrentActivityThread = this;

    if (!system) {
        // Получаем прокси к AMS через ServiceManager
        final IActivityManager mgr = ActivityManager.getService();

        // Регистрируем ApplicationThread как Binder callback
        // AMS сохраняет ссылку на mAppThread для отправки команд
        mgr.attachApplication(mAppThread, startSeq);
    }
}
```

Параметр `mAppThread` — это экземпляр `ApplicationThread`, внутреннего класса `ActivityThread`. Именно через него `AMS` будет отправлять все lifecycle-команды.

> **Ключевой момент:** после вызова `attach()` поток блокируется в `Looper.loop()`. Вся дальнейшая работа происходит через Messages, которые `AMS` отправляет через `ApplicationThread` → `Handler H`.

Подробнее о механизме Looper: [[android-handler-looper]]

---

## ApplicationThread: Binder-мост с system_server

### Архитектура

`ApplicationThread` — это **приватный внутренний класс** `ActivityThread`, реализующий интерфейс `IApplicationThread.Stub`. Это Binder-stub, через который `system_server` (а конкретно `ActivityManagerService`) общается с процессом приложения.

```
┌──────────────────────────────────────────────────────────────────┐
│                    BINDER-МОСТ                                   │
│                                                                  │
│   system_server process              App process                 │
│   ┌──────────────────┐              ┌──────────────────────┐     │
│   │                  │              │   ActivityThread      │     │
│   │  AMS             │              │   ┌────────────────┐  │     │
│   │  ┌────────────┐  │    Binder    │   │ApplicationThread│  │     │
│   │  │IApplication│──│──────────────│──►│(IApplicationThread│ │     │
│   │  │Thread.Proxy│  │    IPC       │   │     .Stub)      │  │     │
│   │  └────────────┘  │              │   └───────┬────────┘  │     │
│   │                  │              │            │           │     │
│   └──────────────────┘              │            │ post()    │     │
│                                     │            ▼           │     │
│                                     │   ┌──────────────┐    │     │
│                                     │   │  Handler H   │    │     │
│                                     │   │ (main thread)│    │     │
│                                     │   └──────────────┘    │     │
│                                     └──────────────────────┘     │
└──────────────────────────────────────────────────────────────────┘

  Binder thread pool                   Main thread
  (несколько потоков)                   (один поток, Looper.loop())
```

### Ключевые методы ApplicationThread

Все методы `ApplicationThread` имеют префикс `schedule*` — они **планируют** выполнение на главном потоке через `Handler H`:

```java
// frameworks/base/core/java/android/app/ActivityThread.java
private class ApplicationThread extends IApplicationThread.Stub {

    // === Lifecycle транзакции (Android 9+) ===
    @Override
    public void scheduleTransaction(ClientTransaction transaction) {
        ActivityThread.this.scheduleTransaction(transaction);
    }

    // === Инициализация приложения ===
    @Override
    public void bindApplication(String processName, ApplicationInfo appInfo,
            List<ProviderInfo> providers, ComponentName testName,
            ProfilerInfo profilerInfo, Bundle testArgs,
            IInstrumentationWatcher testWatcher, IUiAutomationConnection uiAutomationConnection,
            int debugMode, boolean enableBinderTracking,
            boolean trackAllocation, boolean restrictedBackupMode,
            boolean persistent, Configuration config, CompatibilityInfo compatInfo,
            Map services, Bundle coreSettings, String buildSerial,
            AutofillOptions autofillOptions, ContentCaptureOptions contentCaptureOptions,
            long[] disabledCompatChanges, SharedMemory serializedSystemFontMap,
            long startRequestedElapsedTime, long startRequestedUptime) {
        // ... отправляет BIND_APPLICATION в Handler H
    }

    // === Управление памятью ===
    @Override
    public void scheduleTrimMemory(int level) {
        // Запрос на освобождение памяти
    }

    // === Service lifecycle ===
    @Override
    public void scheduleCreateService(IBinder token, ServiceInfo info,
            CompatibilityInfo compatInfo, int processState) {
        // Создание Service
    }

    @Override
    public void scheduleBindService(IBinder token, Intent intent,
            boolean rebind, int processState) {
        // Привязка к Service
    }

    // === Broadcast ===
    @Override
    public void scheduleReceiver(Intent intent, ActivityInfo info,
            CompatibilityInfo compatInfo, int resultCode, String data,
            Bundle extras, boolean ordered, boolean assumeDelivered,
            int sendingUser, int processState, int estimatedDeliveryCount,
            long intentReceivedTime) {
        // Доставка Broadcast
    }

    // === ContentProvider ===
    @Override
    public void scheduleInstallProvider(ProviderInfo provider) {
        // Установка ContentProvider
    }

    // === Низкоуровневые ===
    @Override
    public void scheduleExit() {
        // Завершение процесса
    }

    @Override
    public void scheduleSuicide() {
        // Принудительное завершение
    }
}
```

### Критический момент: переключение потоков

Методы `ApplicationThread` вызываются на **Binder-потоке**, а не на главном потоке. Поэтому каждый метод делает одно и то же — **ставит сообщение в очередь Handler H**:

```
  Binder thread #1                    Main thread
  ┌──────────────┐                    ┌──────────────────────┐
  │ AMS вызывает │                    │                      │
  │ schedule     │    sendMessage()   │   Handler H          │
  │ Transaction()│ ──────────────────►│   handleMessage()    │
  │              │                    │     │                 │
  │              │                    │     ▼                 │
  │              │                    │   TransactionExecutor │
  │              │                    │     │                 │
  │              │                    │     ▼                 │
  │              │                    │   Activity.onCreate() │
  └──────────────┘                    └──────────────────────┘
```

> **Важно:** никогда не следует обращаться к UI-компонентам из Binder-потока. Вся работа с Activity, View и т.д. происходит строго на главном потоке.

Подробнее о механизме Binder: [[android-binder-ipc]]

---

## Handler H: диспетчер lifecycle-команд

### Архитектура

Класс `H` — приватный внутренний класс `ActivityThread`, наследующий от `Handler`. Это единственный Handler, через который проходят **все** lifecycle-операции приложения.

```java
// Упрощённая структура
class H extends Handler {
    // === Pre-Android 9 (API < 28): индивидуальные коды ===
    public static final int BIND_APPLICATION        = 110;
    public static final int EXIT_APPLICATION        = 111;
    public static final int RECEIVER                = 113;
    public static final int CREATE_SERVICE          = 114;
    public static final int STOP_SERVICE            = 116;
    public static final int BIND_SERVICE            = 121;
    public static final int UNBIND_SERVICE          = 122;
    public static final int CONFIGURATION_CHANGED   = 118;
    public static final int RELAUNCH_ACTIVITY       = 160;
    // ... и многие другие

    // === Android 9+ (API 28): единый код для транзакций ===
    public static final int EXECUTE_TRANSACTION     = 159;

    @Override
    public void handleMessage(Message msg) {
        switch (msg.what) {
            case BIND_APPLICATION:
                handleBindApplication((AppBindData) msg.obj);
                break;
            case EXECUTE_TRANSACTION:
                // Делегирует в TransactionExecutor
                final ClientTransaction transaction = (ClientTransaction) msg.obj;
                mTransactionExecutor.execute(transaction);
                break;
            case RECEIVER:
                handleReceiver((ReceiverData) msg.obj);
                break;
            case CREATE_SERVICE:
                handleCreateService((CreateServiceData) msg.obj);
                break;
            case BIND_SERVICE:
                handleBindService((BindServiceData) msg.obj);
                break;
            case CONFIGURATION_CHANGED:
                handleConfigurationChanged((Configuration) msg.obj);
                break;
            // ... остальные case
        }
    }
}
```

### Эволюция Handler H

```
┌─────────────────────────────────────────────────────────────────────┐
│          ЭВОЛЮЦИЯ ДИСПЕТЧЕРИЗАЦИИ LIFECYCLE                        │
│                                                                     │
│  Pre-Android 9 (API < 28):                                         │
│  ┌─────────────────┐    ┌───────────────────────────────────┐      │
│  │ ApplicationThread│    │         Handler H                 │      │
│  │                  │    │                                   │      │
│  │ scheduleLaunch   │───►│ LAUNCH_ACTIVITY → handleLaunch   │      │
│  │ Activity()       │    │                    Activity()     │      │
│  │                  │    │                                   │      │
│  │ schedulePause    │───►│ PAUSE_ACTIVITY  → handlePause    │      │
│  │ Activity()       │    │                    Activity()     │      │
│  │                  │    │                                   │      │
│  │ scheduleDestroy  │───►│ DESTROY_ACTIVITY→ handleDestroy  │      │
│  │ Activity()       │    │                    Activity()     │      │
│  └─────────────────┘    └───────────────────────────────────┘      │
│                                                                     │
│  Android 9+ (API 28):                                              │
│  ┌─────────────────┐    ┌───────────────────────────────────┐      │
│  │ ApplicationThread│    │         Handler H                 │      │
│  │                  │    │                                   │      │
│  │ scheduleTransac  │───►│ EXECUTE_TRANSACTION               │      │
│  │ tion()           │    │     │                             │      │
│  │                  │    │     ▼                             │      │
│  │  (единый метод   │    │ TransactionExecutor.execute()    │      │
│  │   для ВСЕХ       │    │     │                             │      │
│  │   lifecycle)     │    │     ├─► LaunchActivityItem        │      │
│  │                  │    │     ├─► PauseActivityItem         │      │
│  │                  │    │     ├─► DestroyActivityItem       │      │
│  │                  │    │     └─► ...                       │      │
│  └─────────────────┘    └───────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────┘
```

### Почему единственный Handler

Использование единственного Handler для всех lifecycle-операций даёт критически важную гарантию: **все lifecycle-переходы выполняются последовательно на главном потоке**. Это означает:

1. **Атомарность** — `onCreate()` полностью завершится до начала `onStart()`
2. **Порядок** — гарантированная последовательность lifecycle-переходов
3. **Потокобезопасность** — не нужна синхронизация между lifecycle-вызовами
4. **Предсказуемость** — все Activity в процессе делят один поток, операции с ними — последовательны

```
  MessageQueue главного потока:
  ┌────────┬────────┬──────────┬─────────┬────────────┐
  │ Launch │ Resume │  Pause   │  Input  │   Stop     │
  │Activity│Activity│ Activity │  Event  │  Activity  │
  │   A    │   A    │    A     │         │     A      │
  └────┬───┴────┬───┴────┬─────┴────┬────┴─────┬──────┘
       │        │        │          │          │
       ▼        ▼        ▼          ▼          ▼
   Выполняются СТРОГО ПОСЛЕДОВАТЕЛЬНО на main thread
```

---

## ClientTransaction System (Android 9+, Pie)

### Мотивация перехода

До Android 9 каждая lifecycle-операция имела отдельный метод в `ApplicationThread` и отдельный код сообщения в `Handler H`. Это создавало проблемы:

| Проблема | Pre-Android 9 | Android 9+ ClientTransaction |
|----------|---------------|------------------------------|
| Тестируемость | Сложно — логика размазана по десяткам методов | Каждый `ClientTransactionItem` — изолированный, тестируемый объект |
| Консистентность | Разные пути для разных операций, возможны нарушения порядка | Единый путь: `TransactionExecutor` гарантирует state machine |
| State machine | Неявная, легко нарушить | Явная: `TransactionExecutor` проверяет текущее состояние и вычисляет путь |
| Расширяемость | Добавление нового lifecycle = новый метод + новый код | Добавление = новый `ClientTransactionItem` подкласс |
| Batching | Невозможно | `ClientTransaction` может содержать несколько callbacks |

### Структура ClientTransaction

```java
// frameworks/base/core/java/android/app/servertransaction/ClientTransaction.java
public class ClientTransaction implements Parcelable {
    /** Целевой IApplicationThread (Binder к процессу приложения) */
    private IApplicationThread mClient;

    /** Токен Activity (или null для process-level транзакций) */
    private IBinder mActivityToken;

    /** Список callbacks для выполнения (например, LaunchActivityItem) */
    private List<ClientTransactionItem> mActivityCallbacks;

    /** Конечное lifecycle-состояние после выполнения всех callbacks */
    private ActivityLifecycleItem mLifecycleStateRequest;
}
```

### Иерархия ClientTransactionItem

```
┌─────────────────────────────────────────────────────────────────┐
│              ИЕРАРХИЯ ClientTransactionItem                      │
│                                                                 │
│  ClientTransactionItem (abstract)                               │
│  ├── ActivityTransactionItem (abstract)                         │
│  │   ├── LaunchActivityItem          — создание Activity        │
│  │   ├── NewIntentItem               — onNewIntent()            │
│  │   ├── ActivityConfigurationChangeItem — config change        │
│  │   ├── ActivityResultItem          — onActivityResult()       │
│  │   ├── TopResumedActivityChangeItem— multi-resume             │
│  │   └── TransferSplashScreenItem    — splash screen            │
│  │                                                              │
│  ActivityLifecycleItem (abstract extends ClientTransactionItem) │
│  ├── ResumeActivityItem              — переход в ON_RESUME      │
│  ├── PauseActivityItem               — переход в ON_PAUSE       │
│  ├── StopActivityItem                — переход в ON_STOP        │
│  └── DestroyActivityItem             — переход в ON_DESTROY     │
│                                                                 │
│  (Не привязанные к Activity)                                    │
│  ├── ConfigurationChangeItem         — глобальная config change │
│  ├── MoveToDisplayItem               — смена дисплея            │
│  └── WindowStateResizeItem           — изменение размера окна   │
└─────────────────────────────────────────────────────────────────┘
```

### TransactionExecutor: сердце lifecycle state machine

`TransactionExecutor` — ключевой класс, обеспечивающий **корректность lifecycle-переходов**:

```java
// frameworks/base/core/java/android/app/servertransaction/TransactionExecutor.java
public class TransactionExecutor {
    private ClientTransactionHandler mTransactionHandler; // = ActivityThread

    public void execute(ClientTransaction transaction) {
        // 1. Выполнить все callbacks (например, LaunchActivityItem)
        executeCallbacks(transaction);

        // 2. Перевести в конечное lifecycle-состояние
        executeLifecycleState(transaction);
    }

    private void executeCallbacks(ClientTransaction transaction) {
        final List<ClientTransactionItem> callbacks = transaction.getCallbacks();
        if (callbacks == null || callbacks.isEmpty()) return;

        for (int i = 0; i < callbacks.size(); i++) {
            final ClientTransactionItem item = callbacks.get(i);

            // Выполняем callback
            item.execute(mTransactionHandler, token, mPendingActions);
            item.postExecute(mTransactionHandler, token, mPendingActions);
        }
    }

    private void executeLifecycleState(ClientTransaction transaction) {
        final ActivityLifecycleItem lifecycleItem = transaction.getLifecycleStateRequest();
        if (lifecycleItem == null) return;

        final IBinder token = transaction.getActivityToken();
        final ActivityClientRecord r = mTransactionHandler.getActivityClient(token);

        // Текущее состояние Activity
        final int currentState = cycleToCurrentState(r);

        // Целевое состояние
        final int targetState = lifecycleItem.getTargetState();

        // Вычисляем путь: [ON_CREATE → ON_START → ON_RESUME] и т.д.
        cycleToPath(currentState, targetState, transaction);

        // Выполняем каждый промежуточный шаг
        performLifecycleSequence(r, path, transaction);

        // Финальный переход
        lifecycleItem.execute(mTransactionHandler, token, mPendingActions);
        lifecycleItem.postExecute(mTransactionHandler, token, mPendingActions);
    }
}
```

### State Machine lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│              LIFECYCLE STATE MACHINE                             │
│                                                                 │
│                                                                 │
│  PRE_ON_CREATE ──────► ON_CREATE ──────► ON_START               │
│       (0)                 (1)              (2)                  │
│                                              │                  │
│                                              ▼                  │
│                           ┌──────────── ON_RESUME               │
│                           │                (3)                  │
│                           │                                     │
│                           ▼                                     │
│                       ON_PAUSE ────────► ON_STOP                │
│                          (4)               (5)                  │
│                                              │                  │
│                                              ▼                  │
│                                         ON_DESTROY              │
│                                            (6)                  │
│                                                                 │
│                                                                 │
│  TransactionExecutor АВТОМАТИЧЕСКИ вычисляет путь:              │
│                                                                 │
│  Пример: текущее ON_RESUME (3) → цель ON_DESTROY (6)           │
│  Путь: ON_PAUSE(4) → ON_STOP(5) → ON_DESTROY(6)               │
│                                                                 │
│  Пример: текущее ON_STOP (5) → цель ON_RESUME (3)              │
│  Путь: ON_START(2) → ON_RESUME(3) (рестарт)                    │
│                                                                 │
│  НЕЛЬЗЯ пропустить состояние! State machine гарантирует.        │
└─────────────────────────────────────────────────────────────────┘
```

### Пример: запуск Activity через ClientTransaction

На стороне `system_server` (в `ActivityTaskManagerService`):

```java
// Упрощённо: как AMS создаёт транзакцию для запуска Activity
// frameworks/base/services/core/.../ActivityTaskSupervisor.java
void realStartActivityLocked(ActivityRecord r, WindowProcessController proc, ...) {

    // Создаём транзакцию
    final ClientTransaction clientTransaction = ClientTransaction.obtain(
            proc.getThread(),  // IApplicationThread (Binder к приложению)
            r.token            // IBinder — токен Activity
    );

    // Добавляем callback: "создай Activity"
    clientTransaction.addCallback(LaunchActivityItem.obtain(
            new Intent(r.intent),
            r.info,            // ActivityInfo
            // ... остальные параметры
    ));

    // Устанавливаем конечное состояние: ON_RESUME
    clientTransaction.setLifecycleStateRequest(
            ResumeActivityItem.obtain(/* isForward */ true)
    );

    // Отправляем! (через Binder → ApplicationThread → Handler H)
    mService.getLifecycleManager().scheduleTransaction(clientTransaction);
}
```

На стороне приложения:

```kotlin
// Псевдокод: что происходит в процессе приложения

// 1. ApplicationThread.scheduleTransaction() — Binder thread
//    → отправляет EXECUTE_TRANSACTION в Handler H

// 2. Handler H.handleMessage(EXECUTE_TRANSACTION)
//    → TransactionExecutor.execute(transaction)

// 3. TransactionExecutor.executeCallbacks()
//    → LaunchActivityItem.execute()
//       → ActivityThread.handleLaunchActivity()
//          → ActivityThread.performLaunchActivity()
//             → Instrumentation.newActivity()  // создание Activity
//             → Activity.attach()              // настройка Window, Fragment
//             → Instrumentation.callActivityOnCreate()
//                → Activity.performCreate()
//                   → YOUR Activity.onCreate(savedInstanceState)

// 4. TransactionExecutor.executeLifecycleState()
//    → cycleToPath(ON_CREATE → ON_RESUME)
//    → путь: [ON_START, ON_RESUME]
//    → performLifecycleSequence():
//       → ActivityThread.handleStartActivity()
//          → Activity.performStart() → Activity.onStart()
//    → ResumeActivityItem.execute()
//       → ActivityThread.handleResumeActivity()
//          → Activity.performResume() → Activity.onResume()
```

---

## Instrumentation: тестовый хук framework

### Роль Instrumentation

`Instrumentation` — это **прослойка** между `ActivityThread` и компонентами приложения (`Activity`, `Application`). Каждый процесс приложения имеет ровно один экземпляр `Instrumentation`, который перехватывает все lifecycle-вызовы.

```
┌─────────────────────────────────────────────────────────────────┐
│              INSTRUMENTATION КАК ПЕРЕХВАТЧИК                    │
│                                                                 │
│  ActivityThread                                                 │
│      │                                                          │
│      │ performLaunchActivity()                                  │
│      │                                                          │
│      ▼                                                          │
│  ┌──────────────────────────────────────────────────┐           │
│  │              Instrumentation                      │           │
│  │                                                   │           │
│  │  ┌─────────────────┐   ┌──────────────────────┐  │           │
│  │  │  newActivity()  │   │ callActivityOnCreate()│  │           │
│  │  │  Создание через │   │ Вызов onCreate()     │  │           │
│  │  │  ClassLoader    │   │ через performCreate()│  │           │
│  │  └────────┬────────┘   └──────────┬───────────┘  │           │
│  │           │                       │               │           │
│  │  ┌────────────────────┐   ┌────────────────────┐ │           │
│  │  │callActivityOnStart│   │callActivityOnResume│  │           │
│  │  │ Вызов onStart()   │   │ Вызов onResume()   │  │           │
│  │  └────────┬───────────┘   └──────────┬────────┘  │           │
│  │           │                          │            │           │
│  │  ┌────────────────────┐   ┌────────────────────┐ │           │
│  │  │callActivityOnPause│   │callActivityOnStop  │  │           │
│  │  │ Вызов onPause()   │   │ Вызов onStop()     │  │           │
│  │  └────────────────────┘   └────────────────────┘ │           │
│  │                                                   │           │
│  │  В тестах: Espresso/UIAutomator подменяют         │           │
│  │  Instrumentation для контроля lifecycle           │           │
│  └──────────────────────────────────────────────────┘           │
│      │                                                          │
│      ▼                                                          │
│  ┌──────────────┐                                               │
│  │   Activity   │                                               │
│  │  onCreate()  │                                               │
│  │  onStart()   │                                               │
│  │  onResume()  │                                               │
│  └──────────────┘                                               │
└─────────────────────────────────────────────────────────────────┘
```

### Ключевые методы Instrumentation

```java
// frameworks/base/core/java/android/app/Instrumentation.java (упрощённо)
public class Instrumentation {

    // === Создание компонентов ===

    /** Создание Activity через ClassLoader */
    public Activity newActivity(ClassLoader cl, String className, Intent intent) {
        String pkg = intent != null && intent.getComponent() != null
                ? intent.getComponent().getPackageName() : null;
        return getFactory(pkg).instantiateActivity(cl, className, intent);
    }

    /** Создание Application через ClassLoader */
    public Application newApplication(ClassLoader cl, String className, Context context) {
        Application app = getFactory(context.getPackageName())
                .instantiateApplication(cl, className);
        app.attach(context);
        return app;
    }

    // === Lifecycle hooks ===

    /** Вызов Activity.onCreate() */
    public void callActivityOnCreate(Activity activity, Bundle icicle) {
        prePerformCreate(activity);
        activity.performCreate(icicle);  // → Activity.onCreate(icicle)
        postPerformCreate(activity);
    }

    /** Вызов Activity.onStart() */
    public void callActivityOnStart(Activity activity) {
        activity.onStart();
    }

    /** Вызов Activity.onResume() */
    public void callActivityOnResume(Activity activity) {
        activity.mResumed = true;
        activity.onResume();
    }

    /** Вызов Activity.onPause() */
    public void callActivityOnPause(Activity activity) {
        activity.performPause();  // → Activity.onPause()
    }

    /** Вызов Activity.onStop() */
    public void callActivityOnStop(Activity activity) {
        activity.performStop(true);  // → Activity.onStop()
    }

    /** Вызов Activity.onDestroy() */
    public void callActivityOnDestroy(Activity activity) {
        activity.performDestroy();  // → Activity.onDestroy()
    }

    /** Вызов Activity.onSaveInstanceState() */
    public void callActivityOnSaveInstanceState(Activity activity, Bundle outState) {
        activity.performSaveInstanceState(outState);
    }

    /** Вызов Activity.onRestoreInstanceState() */
    public void callActivityOnRestoreInstanceState(Activity activity, Bundle savedState) {
        activity.performRestoreInstanceState(savedState);
    }

    // === Мониторинг ===

    /** Перехват startActivity — используется в тестах */
    public ActivityResult execStartActivity(
            Context who, IBinder contextThread, IBinder token, Activity target,
            Intent intent, int requestCode, Bundle options) {
        // ... можно перехватить и заблокировать запуск Activity
    }

    // === Activity Monitor ===
    public static class ActivityMonitor {
        // Позволяет тестам отслеживать запуск Activity
        // и подменять результат
    }

    public ActivityMonitor addMonitor(IntentFilter filter, ActivityResult result,
            boolean block) {
        // Регистрирует монитор для перехвата запуска Activity
    }
}
```

### Instrumentation в тестировании

В обычном приложении используется стандартный `Instrumentation`. В тестах (`androidTest`) — специализированная реализация:

```kotlin
// В тестах через AndroidJUnitRunner:
// AndroidJUnitRunner наследует от Instrumentation
// и регистрируется в AndroidManifest.xml тестового APK

// Получение Instrumentation в тесте:
val instrumentation = InstrumentationRegistry.getInstrumentation()

// Espresso использует Instrumentation для:
// 1. Ожидания idle состояния UI (IdlingResource)
// 2. Контроля lifecycle Activity
// 3. Синхронизации с main thread

// Пример: ActivityScenario (из androidx.test) использует Instrumentation
// для контроля lifecycle
val scenario = ActivityScenario.launch(MyActivity::class.java)
scenario.moveToState(Lifecycle.State.CREATED)  // через Instrumentation!
```

```
┌─────────────────────────────────────────────────────────────────┐
│          INSTRUMENTATION В ТЕСТИРОВАНИИ                          │
│                                                                 │
│  Обычное приложение:                                            │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────┐          │
│  │ Activity │◄───│ Instrumentation  │◄───│ Activity │          │
│  │ Thread   │    │ (стандартный)    │    │          │          │
│  └──────────┘    └──────────────────┘    └──────────┘          │
│                                                                 │
│  Тестовое окружение (androidTest):                              │
│  ┌──────────┐    ┌──────────────────┐    ┌──────────┐          │
│  │ Activity │◄───│AndroidJUnitRunner│◄───│ Activity │          │
│  │ Thread   │    │ (extends         │    │          │          │
│  │          │    │  Instrumentation)│    │          │          │
│  └──────────┘    └────────┬─────────┘    └──────────┘          │
│                           │                                     │
│                    ┌──────┴────────┐                            │
│                    │               │                            │
│                    ▼               ▼                            │
│              ┌──────────┐   ┌──────────┐                       │
│              │ Espresso │   │UIAutomator│                       │
│              │ (intra-  │   │ (cross-   │                       │
│              │  process)│   │  process) │                       │
│              └──────────┘   └──────────┘                       │
└─────────────────────────────────────────────────────────────────┘
```

### MonitoringInstrumentation

`MonitoringInstrumentation` (из `androidx.test`) расширяет стандартный `Instrumentation` и добавляет:

- **ActivityLifecycleMonitorRegistry** — отслеживание lifecycle всех Activity
- **IdleSync** — синхронизация с `Looper.getMainLooper()` для ожидания idle
- **IntentMonitor** — перехват и запись всех Intent
- **InterceptingActivityFactory** — подмена создания Activity (для тестовых двойников)

```kotlin
// Как Espresso синхронизируется с lifecycle:
// 1. MonitoringInstrumentation перехватывает callActivityOnResume()
// 2. Проверяет, что Activity в состоянии RESUMED
// 3. Ждёт idle главного Looper (нет pending Messages)
// 4. Только тогда выполняет тестовый код (onView(...).check(...))
```

---

## Создание Activity: пошаговый разбор (12 шагов)

Это полная цепочка от нажатия иконки на Launcher до вызова `onCreate()` вашей Activity:

### Шаг 1: Launcher вызывает startActivity()

```kotlin
// Launcher — это обычное приложение с category LAUNCHER
// При нажатии на иконку:
val intent = Intent(Intent.ACTION_MAIN).apply {
    addCategory(Intent.CATEGORY_LAUNCHER)
    component = ComponentName("com.example.app", "com.example.app.MainActivity")
    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
}
context.startActivity(intent)
```

### Шаг 2: AMS получает запрос через Binder

```
Launcher process                 system_server process
┌──────────────┐    Binder      ┌──────────────────────┐
│ startActivity│ ──────────────►│ ActivityTaskManager   │
│   (intent)   │    IPC         │   Service             │
│              │                │   .startActivity()    │
└──────────────┘                └──────────┬───────────┘
                                           │
                                           ▼
                                ┌──────────────────────┐
                                │ ActivityStarter       │
                                │   .execute()          │
                                └──────────────────────┘
```

### Шаг 3: AMS разрешает Activity и проверяет разрешения

```
ActivityStarter.execute()
    │
    ├── PackageManagerService.resolveActivity()
    │   └── Находит ActivityInfo по Intent
    │
    ├── Проверка разрешений (permission check)
    │
    ├── Проверка, не заблокировано ли приложение
    │
    └── Создание ActivityRecord (серверное представление Activity)
```

### Шаг 4: AMS решает — новый процесс или существующий?

```
                    Нужен ли новый процесс?
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
    Процесс НЕ запущен      Процесс УЖЕ запущен
              │                     │
              ▼                     │
    Шаг 5: Zygote fork             │
              │                     │
              ▼                     │
    ActivityThread.main()           │
              │                     │
              ▼                     ▼
    attach() → AMS           Сразу к шагу 6
    bindApplication()
```

### Шаг 5: Если новый процесс — Zygote fork

```
AMS                     Zygote                  New Process
 │                        │                        │
 │  fork request          │                        │
 │ ──────────────────────►│                        │
 │  (через LocalSocket)   │                        │
 │                        │  fork()                │
 │                        │───────────────────────►│
 │                        │                        │
 │                        │               ActivityThread.main()
 │                        │                        │
 │◄────────────────────────────────────────────────│
 │  attachApplication()  (Binder IPC)              │
 │                                                 │
 │  bindApplication()                              │
 │ ───────────────────────────────────────────────►│
 │  (через ApplicationThread Binder)               │
```

### Шаг 6: AMS создаёт ClientTransaction

```java
// В ActivityTaskSupervisor.realStartActivityLocked():
final ClientTransaction clientTransaction = ClientTransaction.obtain(
    proc.getThread(),  // IApplicationThread — Binder-прокси к приложению
    r.token            // IBinder — уникальный токен Activity
);

// Callback: создать Activity
clientTransaction.addCallback(LaunchActivityItem.obtain(
    new Intent(r.intent),
    r.ident,
    r.info,           // ActivityInfo из AndroidManifest
    // ... конфигурация, совместимость, и т.д.
));

// Конечное состояние: RESUMED
clientTransaction.setLifecycleStateRequest(
    ResumeActivityItem.obtain(isForward)
);
```

### Шаг 7: AMS отправляет через Binder

```java
// ClientLifecycleManager.scheduleTransaction():
void scheduleTransaction(ClientTransaction transaction) {
    transaction.schedule();  // → IApplicationThread.scheduleTransaction()
}

// Это Binder-вызов: из system_server → в процесс приложения
```

### Шаг 8: ApplicationThread получает на Binder-потоке

```java
// В процессе приложения, на BINDER-потоке (не main!):
class ApplicationThread extends IApplicationThread.Stub {
    @Override
    public void scheduleTransaction(ClientTransaction transaction) {
        // Делегируем в ActivityThread (он же ClientTransactionHandler)
        ActivityThread.this.scheduleTransaction(transaction);
    }
}

// ClientTransactionHandler.scheduleTransaction():
void scheduleTransaction(ClientTransaction transaction) {
    transaction.preExecute(this);
    // Отправляем сообщение в Handler H на MAIN поток
    sendMessage(ActivityThread.H.EXECUTE_TRANSACTION, transaction);
}
```

### Шаг 9: Handler H принимает на Main thread

```java
// Handler H на ГЛАВНОМ потоке:
case EXECUTE_TRANSACTION:
    final ClientTransaction transaction = (ClientTransaction) msg.obj;
    mTransactionExecutor.execute(transaction);
    break;
```

### Шаг 10: TransactionExecutor выполняет

```java
// TransactionExecutor.execute():
public void execute(ClientTransaction transaction) {
    // 10a. Выполняем callbacks
    executeCallbacks(transaction);
    //   → LaunchActivityItem.execute(mTransactionHandler, token, ...)
    //     → mTransactionHandler.handleLaunchActivity(r, ...)
    //       → ActivityThread.handleLaunchActivity()

    // 10b. Переходим в конечное lifecycle-состояние
    executeLifecycleState(transaction);
    //   → cycleToPath(ON_CREATE → ON_RESUME)
    //   → путь: ON_START, ON_RESUME
    //   → handleStartActivity() → handleResumeActivity()
}
```

### Шаг 11: performLaunchActivity() — создание Activity

```java
// ActivityThread.performLaunchActivity():
private Activity performLaunchActivity(ActivityClientRecord r, Intent customIntent) {

    // 11a. Создаём Activity через Instrumentation
    Activity activity = mInstrumentation.newActivity(
        cl,                    // ClassLoader
        component.getClassName(), // "com.example.app.MainActivity"
        r.intent
    );

    // 11b. Создаём ContextImpl
    ContextImpl appContext = createBaseContextForActivity(r);

    // 11c. Activity.attach() — настройка Window, FragmentManager и т.д.
    activity.attach(
        appContext,
        this,                  // ActivityThread
        mInstrumentation,      // Instrumentation
        r.token,               // IBinder — токен Activity в AMS
        r.ident,
        app,                   // Application
        r.intent,
        r.activityInfo,
        title,
        r.parent,
        r.embeddedID,
        r.lastNonConfigurationInstances,  // ViewModelStore!
        config,
        r.referrer,
        r.voiceInteractor,
        r.window,
        r.activityConfigCallback,
        r.assistToken,
        r.shareableActivityToken
    );

    // 11d. Вызов onCreate через Instrumentation
    if (r.isPersistable()) {
        mInstrumentation.callActivityOnCreate(activity, r.state, r.persistentState);
    } else {
        mInstrumentation.callActivityOnCreate(activity, r.state);
    }

    return activity;
}
```

### Шаг 12: Ваш onCreate()!

```java
// Instrumentation.callActivityOnCreate():
public void callActivityOnCreate(Activity activity, Bundle icicle) {
    prePerformCreate(activity);
    activity.performCreate(icicle);   // ← здесь
    postPerformCreate(activity);
}

// Activity.performCreate():
final void performCreate(Bundle icicle) {
    // ...
    onCreate(icicle);   // ← ВАШ КОД!
    // ...
}
```

### Полная диаграмма 12 шагов

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    12 ШАГОВ СОЗДАНИЯ ACTIVITY                           │
│                                                                         │
│  Launcher         AMS              Zygote      ActivityThread           │
│  (app process)    (system_server)              (app process)            │
│     │                │                │              │                  │
│  1. │ startActivity  │                │              │                  │
│     │───────────────►│                │              │                  │
│     │   (Binder)     │                │              │                  │
│     │                │                │              │                  │
│  2. │                │ resolveActivity│              │                  │
│     │                │ (PackageManager)              │                  │
│     │                │                │              │                  │
│  3. │                │ check permissions             │                  │
│     │                │ create ActivityRecord          │                  │
│     │                │                │              │                  │
│  4. │                │ process alive? │              │                  │
│     │                │───┐            │              │                  │
│     │                │   │ NO         │              │                  │
│     │                │◄──┘            │              │                  │
│     │                │                │              │                  │
│  5. │                │ fork request   │              │                  │
│     │                │───────────────►│  fork()      │                  │
│     │                │                │─────────────►│                  │
│     │                │                │    AT.main() │                  │
│     │                │◄─────────────────────────────│ attach()         │
│     │                │                │              │                  │
│  6. │                │ create ClientTransaction      │                  │
│     │                │ + LaunchActivityItem           │                  │
│     │                │ + ResumeActivityItem           │                  │
│     │                │                │              │                  │
│  7. │                │ scheduleTransaction()          │                  │
│     │                │──────────────────────────────►│ (Binder thread) │
│     │                │         (Binder IPC)          │                  │
│     │                │                │              │                  │
│  8. │                │                │              │ ApplicationThread│
│     │                │                │              │ receives on      │
│     │                │                │              │ Binder thread    │
│     │                │                │              │                  │
│  9. │                │                │              │ post to Handler H│
│     │                │                │              │ (main thread)    │
│     │                │                │              │                  │
│ 10. │                │                │              │ TransactionExec  │
│     │                │                │              │ .execute()       │
│     │                │                │              │   │              │
│     │                │                │              │   ▼              │
│ 11. │                │                │              │ performLaunch    │
│     │                │                │              │ Activity()       │
│     │                │                │              │   │              │
│     │                │                │              │   ├─ newActivity()│
│     │                │                │              │   ├─ attach()    │
│     │                │                │              │   ├─ callOnCreate│
│     │                │                │              │   │              │
│ 12. │                │                │              │   ▼              │
│     │                │                │              │ YOUR onCreate()! │
│     │                │                │              │                  │
│     │                │                │              │ (затем onStart,  │
│     │                │                │              │  onResume через  │
│     │                │                │              │  TransactionExec)│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## bindApplication: инициализация процесса

### Контекст

Когда Zygote создаёт новый процесс (fork), `ActivityThread.main()` вызывает `attach()`, который регистрируется в AMS. В ответ AMS вызывает `ApplicationThread.bindApplication()` — это **инициализация процесса приложения**.

### Последовательность handleBindApplication()

```java
// ActivityThread.handleBindApplication() — упрощённо
private void handleBindApplication(AppBindData data) {

    // 1. Настройка часового пояса и локали
    TimeZone.setDefault(data.config.getTimeZone());

    // 2. Настройка StrictMode (если debug)
    if (data.debugMode != 0) {
        StrictMode.enableDefaults();
    }

    // 3. Создание LoadedApk (обёртка над APK)
    data.info = getPackageInfoNoCheck(data.appInfo, data.compatInfo);
    // LoadedApk содержит: ClassLoader, Resources, путь к APK

    // 4. Создание Instrumentation
    if (data.instrumentationName != null) {
        // Тестовый Instrumentation (androidTest)
        mInstrumentation = (Instrumentation)
            cl.loadClass(data.instrumentationName.getClassName())
              .newInstance();
    } else {
        // Стандартный Instrumentation
        mInstrumentation = new Instrumentation();
    }
    mInstrumentation.init(this, instrContext, appContext, ...);

    // 5. Создание ContextImpl для Application
    final ContextImpl appContext = ContextImpl.createAppContext(this, data.info);

    // 6. ВАЖНО: ContentProviders инициализируются ДО Application!
    if (!data.restrictedBackupMode) {
        if (!ArrayUtils.isEmpty(data.providers)) {
            installContentProviders(app, data.providers);
            // ^ Вот почему ContentProvider.onCreate() блокирует старт!
        }
    }

    // 7. Создание Application через Instrumentation
    Application app = data.info.makeApplicationInner(data.restrictedBackupMode, null);
    // Внутри: mInstrumentation.newApplication(cl, appClass, appContext)

    // 8. Вызов Application.onCreate()
    mInstrumentation.callApplicationOnCreate(app);
    // → app.onCreate()  ← ВАШ Application.onCreate()!
}
```

### Диаграмма: порядок инициализации

```
┌─────────────────────────────────────────────────────────────────┐
│              handleBindApplication() — ПОРЯДОК                  │
│                                                                 │
│  AMS                         ActivityThread                     │
│   │                              │                              │
│   │  bindApplication()           │                              │
│   │─────────────────────────────►│                              │
│   │  (Binder thread)             │                              │
│   │                              │                              │
│   │                    ┌─────────▼─────────┐                    │
│   │                    │ 1. Timezone/Locale │                    │
│   │                    └─────────┬─────────┘                    │
│   │                              │                              │
│   │                    ┌─────────▼─────────┐                    │
│   │                    │ 2. StrictMode      │                    │
│   │                    └─────────┬─────────┘                    │
│   │                              │                              │
│   │                    ┌─────────▼─────────┐                    │
│   │                    │ 3. Create LoadedApk│                    │
│   │                    │    (ClassLoader,   │                    │
│   │                    │     Resources)     │                    │
│   │                    └─────────┬─────────┘                    │
│   │                              │                              │
│   │                    ┌─────────▼─────────┐                    │
│   │                    │ 4. Create/init     │                    │
│   │                    │    Instrumentation │                    │
│   │                    └─────────┬─────────┘                    │
│   │                              │                              │
│   │                    ┌─────────▼─────────┐                    │
│   │                    │ 5. Create ContextImpl                  │
│   │                    │    for Application │                    │
│   │                    └─────────┬─────────┘                    │
│   │                              │                              │
│   │                    ┌─────────▼──────────────┐               │
│   │                    │ 6. installContent      │  ◄── ВАЖНО!   │
│   │                    │    Providers()          │  ДО App!      │
│   │                    │    ┌──────────────────┐ │               │
│   │                    │    │CP1.onCreate()    │ │               │
│   │                    │    │CP2.onCreate()    │ │               │
│   │                    │    │CP3.onCreate()    │ │               │
│   │                    │    └──────────────────┘ │               │
│   │                    └─────────┬──────────────┘               │
│   │                              │                              │
│   │                    ┌─────────▼─────────┐                    │
│   │                    │ 7. Create          │                    │
│   │                    │    Application     │                    │
│   │                    └─────────┬─────────┘                    │
│   │                              │                              │
│   │                    ┌─────────▼─────────┐                    │
│   │                    │ 8. Application     │                    │
│   │                    │    .onCreate()     │  ◄── ВАШ КОД      │
│   │                    └───────────────────┘                    │
│   │                                                             │
└─────────────────────────────────────────────────────────────────┘
```

### Почему ContentProviders инициализируются первыми

Это **историческое решение**, которое активно эксплуатируется современными библиотеками:

```kotlin
// Многие библиотеки используют ContentProvider для автоматической инициализации:

// 1. Firebase — FirebaseInitProvider
// 2. WorkManager — WorkManagerInitializer
// 3. Lifecycle — ProcessLifecycleOwnerInitializer
// 4. AndroidX Startup — InitializationProvider

// Проблема: каждый ContentProvider.onCreate() блокирует запуск приложения!

// Решение: AndroidX App Startup Library
// Объединяет все инициализации в один ContentProvider
// и позволяет указать зависимости между Initializer-ами
```

```
┌─────────────────────────────────────────────────────────────────┐
│  ПРОБЛЕМА: множество ContentProvider при старте                 │
│                                                                 │
│  handleBindApplication()                                        │
│      │                                                          │
│      ├── FirebaseInitProvider.onCreate()      ← 50ms            │
│      ├── WorkManagerInitializer.onCreate()    ← 30ms            │
│      ├── ProcessLifecycleOwnerInit.onCreate() ← 10ms            │
│      ├── YourCustomProvider.onCreate()        ← ???ms           │
│      │                                                          │
│      └── Application.onCreate()  ← начинается ПОСЛЕ всех CP    │
│                                                                 │
│  РЕШЕНИЕ: AndroidX App Startup                                  │
│      │                                                          │
│      ├── InitializationProvider.onCreate()    ← один CP         │
│      │     ├── FirebaseInitializer             вместо           │
│      │     ├── WorkManagerInitializer          множества         │
│      │     └── YourInitializer                                  │
│      │                                                          │
│      └── Application.onCreate()                                 │
└─────────────────────────────────────────────────────────────────┘
```

Подробнее об оптимизации запуска: [[android-app-startup-performance]]

---

## Configuration Changes

### Механизм обнаружения

Когда происходит изменение конфигурации (поворот экрана, смена языка, тёмная тема и т.д.), `system_server` уведомляет все затронутые процессы.

### handleConfigurationChanged — глобальная конфигурация

```java
// ActivityThread.handleConfigurationChanged():
void handleConfigurationChanged(Configuration config) {
    // Обновляем Resources для всего процесса
    applyConfigurationToResources(config);

    // Уведомляем все зарегистрированные ComponentCallbacks
    // (Application, Activity, Service, etc.)
    for (ComponentCallbacks2 cb : collectComponentCallbacks()) {
        cb.onConfigurationChanged(config);
    }
}
```

### handleRelaunchActivity — пересоздание Activity

Когда Activity не обрабатывает изменение конфигурации самостоятельно (нет `configChanges` в манифесте), AMS отправляет команду на пересоздание:

```java
// ActivityThread — упрощённый handleRelaunchActivity:
void handleRelaunchActivity(ActivityClientRecord r, PendingTransactionActions actions) {

    // 1. Сохранить состояние
    performPauseActivity(r, false, "handleRelaunch");
    //   → Activity.onPause()

    // Вызов onSaveInstanceState() ПЕРЕД onStop()
    callActivityOnSaveInstanceState(r);
    //   → Activity.onSaveInstanceState(outBundle)

    performStopActivity(r, false, "handleRelaunch");
    //   → Activity.onStop()

    // 2. Уничтожить Activity
    handleDestroyActivity(r, false, false, "handleRelaunch");
    //   → Activity.onDestroy()

    // НО: ActivityClientRecord НЕ удаляется!
    // ViewModelStore сохраняется в r.lastNonConfigurationInstances

    // 3. Пересоздать Activity с сохранённым состоянием
    handleLaunchActivity(r, actions);
    //   → performLaunchActivity(r)
    //     → newActivity()
    //     → activity.attach(..., r.lastNonConfigurationInstances, ...)
    //     → Activity.onCreate(savedInstanceState)  ← с сохранённым Bundle

    handleStartActivity(r, actions);
    //   → Activity.onStart()

    handleResumeActivity(r, false, "handleRelaunch");
    //   → Activity.onResume()
}
```

### Диаграмма configuration change

```
┌─────────────────────────────────────────────────────────────────┐
│              CONFIGURATION CHANGE (поворот экрана)              │
│                                                                 │
│  Sensor Manager          AMS              ActivityThread        │
│       │                   │                    │                │
│  rotation detected        │                    │                │
│       │                   │                    │                │
│       │──────────────────►│                    │                │
│       │                   │                    │                │
│       │          handleRelaunchActivity()      │                │
│       │                   │───────────────────►│                │
│       │                   │                    │                │
│       │                   │            ┌───────▼────────┐      │
│       │                   │            │ Old Activity:  │      │
│       │                   │            │                │      │
│       │                   │            │ onPause()      │      │
│       │                   │            │ onSaveInstance │      │
│       │                   │            │   State()      │      │
│       │                   │            │ onStop()       │      │
│       │                   │            │ onDestroy()    │      │
│       │                   │            │                │      │
│       │                   │            │ ──── ViewModelStore   │
│       │                   │            │       сохранён в      │
│       │                   │            │       ActivityClient  │
│       │                   │            │       Record ────     │
│       │                   │            │                │      │
│       │                   │            │ New Activity:  │      │
│       │                   │            │                │      │
│       │                   │            │ onCreate(saved)│      │
│       │                   │            │ onStart()      │      │
│       │                   │            │ onResume()     │      │
│       │                   │            │                │      │
│       │                   │            │ ViewModel      │      │
│       │                   │            │ восстановлен!  │      │
│       │                   │            └────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### configChanges в манифесте

```xml
<!-- AndroidManifest.xml -->
<activity
    android:name=".VideoPlayerActivity"
    android:configChanges="orientation|screenSize|keyboardHidden">
    <!-- Activity сама обработает эти изменения -->
    <!-- НЕ будет пересоздана -->
</activity>
```

При наличии `configChanges` фреймворк НЕ пересоздаёт Activity, а вызывает:

```kotlin
class VideoPlayerActivity : AppCompatActivity() {
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        // Обработка изменения конфигурации без пересоздания
        when (newConfig.orientation) {
            Configuration.ORIENTATION_LANDSCAPE -> switchToLandscapeLayout()
            Configuration.ORIENTATION_PORTRAIT -> switchToPortraitLayout()
        }
    }
}
```

### Как ViewModel переживает configuration change

Механизм внутри `ActivityThread`:

```
┌─────────────────────────────────────────────────────────────────┐
│       КАК VIEWMODEL ПЕРЕЖИВАЕТ CONFIGURATION CHANGE            │
│                                                                 │
│  ActivityClientRecord (r)                                       │
│  ┌─────────────────────────────────────────┐                    │
│  │ token: IBinder                          │                    │
│  │ activity: Activity (текущий экземпляр)  │                    │
│  │ state: Bundle (savedInstanceState)      │                    │
│  │                                         │                    │
│  │ lastNonConfigurationInstances:          │                    │
│  │   ┌──────────────────────────────────┐  │                    │
│  │   │ NonConfigurationInstances        │  │                    │
│  │   │   ┌────────────────────────────┐ │  │                    │
│  │   │   │ viewModelStore:            │ │  │                    │
│  │   │   │   ViewModelStore           │ │  │  ◄── ПЕРЕЖИВАЕТ   │
│  │   │   │   ┌──────────────────────┐ │ │  │      DESTROY!     │
│  │   │   │   │ map:                 │ │ │  │                    │
│  │   │   │   │   "key" → ViewModel  │ │ │  │                    │
│  │   │   │   └──────────────────────┘ │ │  │                    │
│  │   │   └────────────────────────────┘ │  │                    │
│  │   └──────────────────────────────────┘  │                    │
│  └─────────────────────────────────────────┘                    │
│                                                                 │
│  При config change:                                             │
│  1. Old Activity.onRetainNonConfigurationInstance()              │
│     → сохраняет ViewModelStore в ACR                            │
│  2. Old Activity уничтожается (onDestroy)                       │
│  3. New Activity создаётся                                      │
│  4. Activity.attach(..., r.lastNonConfigurationInstances, ...)  │
│     → передаёт ViewModelStore в новую Activity                  │
│  5. ViewModelProvider видит существующий ViewModel               │
│     → возвращает его, а не создаёт новый                        │
│                                                                 │
│  ВАЖНО: при PROCESS DEATH ActivityClientRecord уничтожается     │
│  вместе с процессом → ViewModel НЕ переживает process death!    │
└─────────────────────────────────────────────────────────────────┘
```

---

## ActivityClientRecord

### Назначение

`ActivityClientRecord` — внутренний класс `ActivityThread`, хранящий **всё состояние Activity** на стороне процесса приложения. Каждая Activity имеет ровно один `ActivityClientRecord`.

### Структура

```java
// ActivityThread.ActivityClientRecord — упрощённо
static final class ActivityClientRecord {
    // === Идентификация ===
    IBinder token;              // Уникальный токен от AMS
    int ident;                  // Идентификатор Activity

    // === Компонент ===
    Intent intent;              // Intent, которым запущена Activity
    ActivityInfo activityInfo;  // Информация из AndroidManifest

    // === Текущий экземпляр ===
    Activity activity;          // Ссылка на живой объект Activity
    Window window;              // Окно Activity

    // === Lifecycle состояние ===
    int lifecycleState;         // Текущее состояние (ON_CREATE, ON_RESUME, ...)
    boolean paused;
    boolean stopped;

    // === Сохранённое состояние ===
    Bundle state;               // savedInstanceState
    PersistableBundle persistentState;

    // === Configuration ===
    Configuration overrideConfig;
    Configuration tmpConfig;    // Для сравнения при config change

    // === Ключевое: NonConfigurationInstances ===
    // Это то, что позволяет ViewModel переживать config change!
    Activity.NonConfigurationInstances lastNonConfigurationInstances;

    // === Application ===
    LoadedApk packageInfo;      // Ссылка на APK

    // === Метаинформация ===
    boolean isForward;          // Направление анимации
    ProfilerInfo profilerInfo;  // Профилирование
    CompatibilityInfo compatInfo; // Совместимость

    // === Флаги ===
    boolean startsNotResumed;   // Для "stopped" запуска
    boolean hideForNow;
}
```

### Хранение в ActivityThread

```java
// ActivityThread хранит все ActivityClientRecord в Map:
final ArrayMap<IBinder, ActivityClientRecord> mActivities = new ArrayMap<>();

// IBinder token — это уникальный идентификатор Activity,
// выданный AMS при создании ActivityRecord на сервере.

// Методы доступа:
ActivityClientRecord getActivityClient(IBinder token) {
    return mActivities.get(token);
}
```

### Жизненный цикл ActivityClientRecord

```
┌─────────────────────────────────────────────────────────────────┐
│          ЖИЗНЕННЫЙ ЦИКЛ ActivityClientRecord                    │
│                                                                 │
│  LaunchActivityItem.execute()                                   │
│      │                                                          │
│      ▼                                                          │
│  Создание ACR                                                   │
│  mActivities.put(token, r)                                      │
│      │                                                          │
│      ▼                                                          │
│  performLaunchActivity()                                        │
│  r.activity = newActivity()                                     │
│      │                                                          │
│      │                     ┌────────────────────┐               │
│      │  Config change? ───►│ handleRelaunchAct  │               │
│      │                     │                    │               │
│      │                     │ r.lastNonConfig =  │               │
│      │                     │   activity.retainNC│               │
│      │                     │                    │               │
│      │                     │ destroy old Activity│               │
│      │                     │ create new Activity │               │
│      │                     │ r.activity = new    │               │
│      │                     │                    │               │
│      │                     │ ACR ПЕРЕИСПОЛЬЗОВАН│               │
│      │                     └────────┬───────────┘               │
│      │◄─────────────────────────────┘                           │
│      │                                                          │
│      ▼                                                          │
│  DestroyActivityItem.execute()                                  │
│  (финальное уничтожение)                                        │
│      │                                                          │
│      ▼                                                          │
│  mActivities.remove(token)                                      │
│  ACR удалён                                                     │
└─────────────────────────────────────────────────────────────────┘
```

### Важное отличие: config change vs finish

```
  Config change (поворот):            finish() / back:
  ┌────────────────────┐              ┌────────────────────┐
  │ ACR остаётся       │              │ ACR удаляется      │
  │ в mActivities      │              │ из mActivities     │
  │                    │              │                    │
  │ ViewModel жив!     │              │ ViewModel.onCleared│
  │                    │              │ ViewModel мёртв    │
  │ Activity пересоздан│              │                    │
  │ с тем же ACR       │              │ Activity уничтожен │
  └────────────────────┘              └────────────────────┘
```

---

## Process Death: что происходит внутри

### Сценарии process death

```
┌─────────────────────────────────────────────────────────────────┐
│              СЦЕНАРИИ PROCESS DEATH                              │
│                                                                 │
│  1. Low Memory Killer (LMK)                                     │
│     ├── Процесс в фоне → OOM adj high → LMK убивает            │
│     ├── НЕТ callback'ов! Нет onDestroy()!                       │
│     └── kill -9 — мгновенная смерть процесса                    │
│                                                                 │
│  2. Пользователь свайпает из Recent Tasks                       │
│     ├── AMS вызывает finishActivity() → onDestroy()             │
│     └── Затем убивает процесс                                   │
│                                                                 │
│  3. Force Stop (Settings → Force Stop)                          │
│     ├── AMS немедленно убивает процесс                          │
│     └── НЕТ callback'ов!                                        │
│                                                                 │
│  4. System kill при нехватке ресурсов                            │
│     ├── Аналогично LMK                                          │
│     └── НЕТ callback'ов!                                        │
│                                                                 │
│  5. Crash (необработанное исключение)                           │
│     ├── UncaughtExceptionHandler → Process.killProcess()        │
│     └── Зависит от обработчика                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Что происходит при возврате пользователя

```
┌─────────────────────────────────────────────────────────────────┐
│              ВОССТАНОВЛЕНИЕ ПОСЛЕ PROCESS DEATH                 │
│                                                                 │
│  LMK убил процесс                                              │
│      │                                                          │
│      │  Пользователь возвращается (из Recent Tasks)             │
│      │                                                          │
│      ▼                                                          │
│  AMS обнаруживает: процесс мёртв, но Task/ActivityRecord жив   │
│      │                                                          │
│      ▼                                                          │
│  AMS → Zygote: fork новый процесс                              │
│      │                                                          │
│      ▼                                                          │
│  ActivityThread.main()                                          │
│      │                                                          │
│      ├── attach() → AMS                                         │
│      ├── bindApplication() → Application.onCreate()             │
│      │                                                          │
│      ▼                                                          │
│  AMS отправляет ClientTransaction с LaunchActivityItem          │
│      │                                                          │
│      │  ActivityRecord на сервере хранит:                       │
│      │  - intent (каким Intent запущена Activity)               │
│      │  - icicle (savedInstanceState Bundle)                    │
│      │                                                          │
│      ▼                                                          │
│  performLaunchActivity()                                        │
│      │                                                          │
│      ▼                                                          │
│  Activity.onCreate(savedInstanceState)                          │
│      │         ^^^^^^^^^^^^^^^^^^^^                             │
│      │         Bundle с данными, сохранёнными                   │
│      │         в onSaveInstanceState() ДО смерти процесса       │
│      │                                                          │
│      │  НО:                                                     │
│      │  - ViewModel УТЕРЯН (был в памяти процесса)             │
│      │  - Все объекты в памяти — утеряны                       │
│      │  - Только savedInstanceState восстановлен               │
│      │  - SavedStateHandle (AAC) восстановлен                   │
│      │                                                          │
│      ▼                                                          │
│  Для полного восстановления нужны:                              │
│  1. savedInstanceState (из AMS)                                 │
│  2. SavedStateHandle в ViewModel (из savedInstanceState)        │
│  3. Persistent storage (Room, SharedPreferences, DataStore)     │
└─────────────────────────────────────────────────────────────────┘
```

### savedInstanceState и Binder buffer

```kotlin
// Activity.onSaveInstanceState() сохраняет состояние в Bundle
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // Данные сохраняются в Bundle
    outState.putString("key", value)

    // ВАЖНО: Bundle передаётся через Binder IPC!
    // Binder buffer = 1 МБ на ВЕСЬ процесс (не на транзакцию)
    // Если Bundle слишком большой → TransactionTooLargeException
}
```

```
┌─────────────────────────────────────────────────────────────────┐
│              savedInstanceState ЧЕРЕЗ BINDER                    │
│                                                                 │
│  App process                        system_server               │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │ onSaveInstance   │   Binder     │ AMS              │        │
│  │ State(outState)  │──────────────│                  │        │
│  │                  │   (Bundle    │ ActivityRecord    │        │
│  │ Bundle:          │   parceled   │   .icicle = Bundle│        │
│  │  - UI state      │   и передан  │                  │        │
│  │  - user data     │   через IPC) │ Хранит до        │        │
│  │  - scroll pos    │              │ восстановления   │        │
│  └──────────────────┘              └──────────────────┘        │
│                                                                 │
│  ⚠ ОГРАНИЧЕНИЕ BINDER BUFFER:                                  │
│  ┌─────────────────────────────────────┐                        │
│  │          1 МБ Binder Buffer         │                        │
│  │  ┌─────────────────────────────────┐│                        │
│  │  │ savedInstanceState Bundle       ││                        │
│  │  │ + Fragment savedState           ││                        │
│  │  │ + все pending Binder транзакции ││                        │
│  │  │ = должны уместиться в 1 МБ!    ││                        │
│  │  └─────────────────────────────────┘│                        │
│  └─────────────────────────────────────┘                        │
│                                                                 │
│  Если не умещается:                                             │
│  → android.os.TransactionTooLargeException                      │
│  → Crash!                                                       │
└─────────────────────────────────────────────────────────────────┘
```

### Стратегии работы с process death

```kotlin
// 1. Минимальный savedInstanceState — только ID и ключи
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // ✅ Хорошо: маленькие данные
    outState.putLong("user_id", userId)
    outState.putInt("scroll_position", scrollPos)

    // ❌ Плохо: большие объекты
    // outState.putParcelableArrayList("items", hugeList)
}

// 2. SavedStateHandle для ViewModel
class MyViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Переживает И config change, И process death
    val userId: StateFlow<Long> = savedStateHandle.getStateFlow("user_id", 0L)

    fun setUserId(id: Long) {
        savedStateHandle["user_id"] = id
    }
}

// 3. Persistent storage для больших данных
class MyRepository(
    private val dao: MyDao,           // Room
    private val dataStore: DataStore   // DataStore
) {
    // Данные переживают всё, включая удаление процесса
}
```

---

## Подводные камни

### 1. ContentProvider блокирует Application.onCreate()

```kotlin
// ПРОБЛЕМА: каждый ContentProvider.onCreate() выполняется синхронно
// ПЕРЕД Application.onCreate()

class SlowContentProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // Этот код блокирует запуск приложения!
        Thread.sleep(500) // Имитация тяжёлой инициализации
        return true
    }
    // ... остальные методы
}

// РЕШЕНИЕ 1: AndroidX App Startup
class MyInitializer : Initializer<MyLibrary> {
    override fun create(context: Context): MyLibrary {
        return MyLibrary.init(context)
    }
    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

// РЕШЕНИЕ 2: Ленивая инициализация
class LazyContentProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // Ничего тяжёлого здесь
        return true
    }

    override fun query(...): Cursor? {
        ensureInitialized() // Инициализация при первом использовании
        // ...
    }
}
```

### 2. TransactionTooLargeException — слишком большой savedInstanceState

```kotlin
// ПРОБЛЕМА: сохранение больших данных в Bundle
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // ❌ ОПАСНО: список из 10000 Parcelable объектов
    outState.putParcelableArrayList("items", ArrayList(items))
    // → TransactionTooLargeException при передаче через Binder
}

// ДИАГНОСТИКА: в debug режиме можно измерить размер Bundle
fun Bundle.sizeInBytes(): Int {
    val parcel = Parcel.obtain()
    try {
        parcel.writeBundle(this)
        return parcel.dataSize()
    } finally {
        parcel.recycle()
    }
}

// РЕШЕНИЕ: сохраняйте только ID, загружайте данные из репозитория
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putLong("selected_item_id", selectedItemId)
    // НЕ сохраняйте сам список — восстановите из БД/сети
}
```

### 3. Binder callbacks на неправильном потоке

```kotlin
// ПРОБЛЕМА: ApplicationThread получает вызовы на Binder-потоке
// Если случайно обратиться к UI из Binder-потока — crash

// Это ВНУТРЕННЯЯ проблема framework, но проявляется при:
// - Использовании AIDL-сервисов
// - Работе с ContentResolver из разных потоков
// - Custom Binder callbacks

// ПРИМЕР: IPC callback вызывается на Binder-потоке
class MyBinder : IMyService.Stub() {
    override fun onDataReady(data: String) {
        // ❌ Мы НА BINDER-ПОТОКЕ! Нельзя обновлять UI!
        // textView.text = data  // CRASH: CalledFromWrongThreadException

        // ✅ Переключаемся на main thread
        Handler(Looper.getMainLooper()).post {
            textView.text = data
        }
    }
}
```

### 4. Fragment transactions во время save state

```kotlin
// ПРОБЛЕМА: после onSaveInstanceState() Fragment transactions запрещены
class MyActivity : AppCompatActivity() {

    fun showDialog() {
        // ❌ Если вызвано после onSaveInstanceState():
        // → IllegalStateException: Can not perform this action after onSaveInstanceState
        MyDialogFragment().show(supportFragmentManager, "dialog")
    }

    // РЕШЕНИЕ 1: commitAllowingStateLoss()
    fun showDialogSafe() {
        supportFragmentManager.beginTransaction()
            .add(MyDialogFragment(), "dialog")
            .commitAllowingStateLoss()  // Позволяет потерю состояния
    }

    // РЕШЕНИЕ 2: Проверяйте lifecycle state
    fun showDialogChecked() {
        if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
            MyDialogFragment().show(supportFragmentManager, "dialog")
        }
    }

    // РЕШЕНИЕ 3: Используйте lifecycle-aware подход
    // ViewModel + SingleLiveEvent / SharedFlow → collect в onStart-onStop
}
```

### 5. onDestroy не гарантирован при process death

```kotlin
// ПРОБЛЕМА: полагаться на onDestroy() для сохранения данных
class MyActivity : AppCompatActivity() {

    // ❌ ОПАСНО: не будет вызвано при process death
    override fun onDestroy() {
        super.onDestroy()
        saveImportantData() // НЕ НАДЁЖНО!
    }

    // ✅ ПРАВИЛЬНО: сохраняйте в onPause() или onStop()
    override fun onStop() {
        super.onStop()
        saveImportantData() // Будет вызвано перед уходом в фон
    }

    // Или ещё лучше: автосохранение при изменении данных
    // через Room/DataStore
}
```

### 6. Неправильное понимание порядка инициализации

```kotlin
// ПРОБЛЕМА: использование Application context в ContentProvider
class MyProvider : ContentProvider() {
    override fun onCreate(): Boolean {
        // ❌ Application ещё НЕ создан!
        // val app = context?.applicationContext as MyApp
        // app.someField  // NPE или неинициализированное состояние

        // ✅ context доступен, но Application.onCreate() ещё не вызван
        // Используйте только базовый Context
        val db = Room.databaseBuilder(context!!, MyDb::class.java, "db").build()
        return true
    }
}

// Порядок инициализации:
// 1. Application.attachBaseContext()
// 2. ContentProvider.onCreate()  ← Application.onCreate() ещё НЕ вызван!
// 3. Application.onCreate()
// 4. Activity.onCreate()
```

---

## Мифы и заблуждения

### Миф 1: "ActivityThread — это поток"

```
  ❌ МИФ:  ActivityThread = Thread

  ✅ РЕАЛЬНОСТЬ:
  ┌─────────────────────────────────────────────────────┐
  │  ActivityThread — это обычный Java-класс,           │
  │  НЕ наследующий от Thread.                          │
  │                                                     │
  │  Название вводит в заблуждение.                     │
  │                                                     │
  │  Единственный поток, который он "создаёт" —         │
  │  это Main Thread (через Looper.prepareMainLooper()) │
  │  в методе main().                                   │
  │                                                     │
  │  Но сам ActivityThread — это объект, живущий         │
  │  НА главном потоке, а не ЯВЛЯЮЩИЙСЯ потоком.        │
  │                                                     │
  │  class ActivityThread extends ClientTransactionHandler│
  │  // НЕ extends Thread!                              │
  └─────────────────────────────────────────────────────┘
```

### Миф 2: "onCreate() — первое, что выполняется в приложении"

```
  ❌ МИФ:  Application.onCreate() → первый код пользователя

  ✅ РЕАЛЬНОСТЬ:
  ┌─────────────────────────────────────────────────────┐
  │  Порядок выполнения:                                │
  │                                                     │
  │  1. Application.attachBaseContext()  ← ДО onCreate  │
  │  2. ContentProvider.onCreate()       ← ДО App.onCreate│
  │  3. Application.onCreate()           ← третий!      │
  │                                                     │
  │  Многие библиотеки (Firebase, WorkManager)          │
  │  инициализируются через ContentProvider,             │
  │  то есть ДО вашего Application.onCreate()!          │
  └─────────────────────────────────────────────────────┘
```

### Миф 3: "ViewModel переживает всё благодаря SavedStateHandle"

```
  ❌ МИФ:  ViewModel переживает config change через SavedStateHandle

  ✅ РЕАЛЬНОСТЬ:
  ┌─────────────────────────────────────────────────────┐
  │  ДВА РАЗНЫХ МЕХАНИЗМА:                              │
  │                                                     │
  │  Config change (поворот):                           │
  │  - ViewModel ЖИВЁТ в памяти                         │
  │  - Хранится в ViewModelStore                        │
  │  - ViewModelStore в ActivityClientRecord             │
  │  - ACR переиспользуется при recreate                │
  │  - SavedStateHandle НЕ нужен!                       │
  │                                                     │
  │  Process death:                                     │
  │  - ViewModel УНИЧТОЖЕН вместе с процессом           │
  │  - ViewModelStore уничтожен                         │
  │  - Восстановление ТОЛЬКО через:                     │
  │    a) savedInstanceState (Activity)                  │
  │    b) SavedStateHandle (ViewModel)                   │
  │    c) Persistent storage (Room/DataStore)            │
  │                                                     │
  │  SavedStateHandle нужен ТОЛЬКО для process death!   │
  └─────────────────────────────────────────────────────┘
```

### Миф 4: "Process death всегда вызывает onDestroy()"

```
  ❌ МИФ:  onDestroy() всегда вызывается перед смертью процесса

  ✅ РЕАЛЬНОСТЬ:
  ┌─────────────────────────────────────────────────────┐
  │  Low Memory Killer использует kill -9 (SIGKILL)     │
  │  → Процесс убит МГНОВЕННО                          │
  │  → Нет шанса выполнить какой-либо код               │
  │  → onDestroy() НЕ вызывается                        │
  │  → onStop() тоже НЕ вызывается                      │
  │  → finalize() НЕ вызывается                         │
  │                                                     │
  │  ТОЛЬКО onStop() ГАРАНТИРОВАН перед уходом в фон    │
  │  (если Activity была visible)                       │
  │                                                     │
  │  onDestroy() гарантирован ТОЛЬКО для:               │
  │  - finish()                                         │
  │  - config change (recreate)                         │
  │  - back navigation                                  │
  └─────────────────────────────────────────────────────┘
```

### Миф 5: "Каждая Activity живёт в отдельном процессе"

```
  ❌ МИФ:  Activity A и Activity B — разные процессы

  ✅ РЕАЛЬНОСТЬ:
  ┌─────────────────────────────────────────────────────┐
  │  По умолчанию ВСЕ компоненты приложения             │
  │  (Activity, Service, ContentProvider, BroadcastReceiver)│
  │  живут в ОДНОМ процессе.                            │
  │                                                     │
  │  ОДИН ActivityThread на ВЕСЬ процесс.               │
  │  ОДНА Map<IBinder, ActivityClientRecord> для всех    │
  │  Activity в процессе.                               │
  │                                                     │
  │  Можно назначить отдельный процесс:                 │
  │  <activity android:process=":isolated" />           │
  │  Но это создаёт НОВЫЙ процесс с НОВЫМ              │
  │  ActivityThread, Application и т.д.                 │
  │                                                     │
  │  Это дорого! Используется редко:                    │
  │  - WebView в отдельном процессе                     │
  │  - Push-сервис в отдельном процессе                 │
  └─────────────────────────────────────────────────────┘
```

---

## CS-фундамент

| Паттерн/Концепция | Где применяется в ActivityThread |
|---|---|
| **Event Loop** | `Looper.loop()` в `main()` — бесконечный цикл обработки сообщений. Main thread = event loop, Messages = события |
| **Command Pattern** | `ClientTransactionItem` — каждая lifecycle-операция инкапсулирована в объект-команду (`LaunchActivityItem`, `DestroyActivityItem`). Можно сериализовать, передавать через Binder, выполнять последовательно |
| **Transaction Pattern** | `ClientTransaction` — группа операций (callbacks + lifecycle state), выполняемых атомарно через `TransactionExecutor` |
| **Proxy-Stub** | `IApplicationThread.Stub` (ApplicationThread) на стороне приложения, `IApplicationThread.Proxy` на стороне AMS — классический Binder proxy-stub для IPC |
| **State Machine** | `TransactionExecutor` реализует lifecycle state machine: автоматически вычисляет путь между состояниями и не позволяет пропускать промежуточные |
| **Instrumentation Pattern** | `Instrumentation` — прослойка-перехватчик между framework и компонентами, позволяющая подменять поведение для тестирования |
| **Mediator** | `ActivityThread` — медиатор между `system_server` (AMS) и компонентами приложения (Activity, Service, Provider). Компоненты не общаются с AMS напрямую |
| **Observer** | `ComponentCallbacks` — Activity, Application регистрируются для получения уведомлений о config changes |
| **Template Method** | `Activity.performCreate()` вызывает `onCreate()` — шаблонный метод, переопределяемый пользователем |
| **Factory Method** | `Instrumentation.newActivity()` — фабричный метод создания Activity через ClassLoader |

---

## Проверь себя

### Вопрос 1
**Почему `ActivityThread` — не поток, хотя имеет "Thread" в названии? Что он собой представляет?**

<details>
<summary>Ответ</summary>

`ActivityThread` наследует от `ClientTransactionHandler`, а не от `Thread`. Это обычный Java-класс — главный объект в каждом процессе Android-приложения. Он управляет lifecycle всех компонентов через `Handler H` на главном потоке. Название исторически связано с тем, что `ActivityThread.main()` является точкой входа главного потока приложения, но сам объект — не поток.

</details>

### Вопрос 2
**Опишите путь lifecycle-команды от AMS до вызова `Activity.onCreate()` в Android 9+. Какие классы участвуют?**

<details>
<summary>Ответ</summary>

1. AMS создаёт `ClientTransaction` с `LaunchActivityItem` callback и `ResumeActivityItem` lifecycle state
2. Отправляет через `IApplicationThread.scheduleTransaction()` (Binder IPC)
3. `ApplicationThread` получает на Binder-потоке
4. Вызывает `sendMessage(EXECUTE_TRANSACTION)` → `Handler H` на main thread
5. `Handler H.handleMessage()` → `TransactionExecutor.execute()`
6. `TransactionExecutor.executeCallbacks()` → `LaunchActivityItem.execute()`
7. `ActivityThread.handleLaunchActivity()` → `performLaunchActivity()`
8. `Instrumentation.newActivity()` — создание через ClassLoader
9. `Activity.attach()` — настройка Window, FragmentManager
10. `Instrumentation.callActivityOnCreate()` → `Activity.performCreate()` → `Activity.onCreate()`

</details>

### Вопрос 3
**Почему ContentProvider инициализируется ДО Application.onCreate()? Какие проблемы это создаёт и как их решить?**

<details>
<summary>Ответ</summary>

В `handleBindApplication()` вызов `installContentProviders()` происходит ДО `Instrumentation.callApplicationOnCreate()`. Это историческое решение: ContentProvider может быть доступен другим процессам сразу после создания процесса. Многие библиотеки (Firebase, WorkManager, Lifecycle) используют этот механизм для автоинициализации. Проблема: каждый `ContentProvider.onCreate()` блокирует запуск приложения. Решения: 1) AndroidX App Startup — объединяет инициализации в один ContentProvider; 2) Ленивая инициализация; 3) Асинхронная инициализация с помощью корутин.

</details>

### Вопрос 4
**Как ViewModel переживает configuration change на уровне ActivityThread? Почему ViewModel НЕ переживает process death?**

<details>
<summary>Ответ</summary>

При config change: `ActivityClientRecord` (ACR) не удаляется из `mActivities`. Перед уничтожением Activity, `onRetainNonConfigurationInstance()` сохраняет `ViewModelStore` в `ACR.lastNonConfigurationInstances`. При создании новой Activity, `performLaunchActivity()` передаёт `lastNonConfigurationInstances` в `activity.attach()`. Новая Activity получает существующий `ViewModelStore` с живыми ViewModel-ами.

При process death: весь процесс убит (kill -9), вся память освобождена. `ActivityClientRecord`, `ViewModelStore`, `ViewModel` — всё уничтожено. Восстановление возможно только через `savedInstanceState` (из AMS) и `SavedStateHandle`.

</details>

### Вопрос 5
**Что такое `TransactionExecutor` и зачем он нужен? Как он обеспечивает корректность lifecycle-переходов?**

<details>
<summary>Ответ</summary>

`TransactionExecutor` — класс, введённый в Android 9, который выполняет `ClientTransaction`. Он: 1) Выполняет все callbacks (например, `LaunchActivityItem`); 2) Вычисляет путь между текущим и целевым lifecycle-состоянием; 3) Выполняет все промежуточные переходы. Например, если Activity в `ON_RESUME` и нужен `ON_DESTROY`, `TransactionExecutor` автоматически проведёт через `ON_PAUSE` → `ON_STOP` → `ON_DESTROY`. Нельзя пропустить промежуточное состояние — state machine гарантирует корректность. До Android 9 каждый lifecycle-переход обрабатывался отдельным методом, что могло приводить к нарушениям порядка.

</details>

---

## Ключевые карточки

### Карточка 1
**Q:** Что делает `ActivityThread.main()`?
**A:** Создаёт главный Looper (`Looper.prepareMainLooper()`), создаёт экземпляр `ActivityThread`, вызывает `attach()` для регистрации в AMS через Binder, запускает бесконечный `Looper.loop()`. Это реальная точка входа каждого Android-приложения после fork от Zygote.

### Карточка 2
**Q:** Что такое `ApplicationThread` и как он связан с AMS?
**A:** Приватный внутренний класс `ActivityThread`, реализующий `IApplicationThread.Stub` — Binder-stub. AMS получает ссылку на него через `attachApplication()` и использует для отправки lifecycle-команд (`scheduleTransaction()`, `bindApplication()`, `scheduleCreateService()` и т.д.). Вызовы приходят на Binder-поток и перенаправляются на main thread через `Handler H`.

### Карточка 3
**Q:** Зачем `Handler H` и почему один Handler для всего?
**A:** `Handler H` — внутренний класс `ActivityThread`, единственный Handler для всех lifecycle-операций. Гарантирует: 1) Все lifecycle-вызовы на main thread; 2) Последовательное выполнение (нет параллельных lifecycle-переходов); 3) Атомарность каждого перехода. В Android 9+ использует единый код `EXECUTE_TRANSACTION`, делегируя в `TransactionExecutor`.

### Карточка 4
**Q:** Как `ClientTransaction` заменил индивидуальные schedule-методы?
**A:** До Android 9: каждая операция имела свой метод (`scheduleLaunchActivity`, `schedulePauseActivity`) и код в `Handler H`. С Android 9: единый `ClientTransaction` содержит список `ClientTransactionItem` (callbacks) и `ActivityLifecycleItem` (целевое состояние). `TransactionExecutor` выполняет callbacks, затем автоматически проводит lifecycle state machine к целевому состоянию.

### Карточка 5
**Q:** Какова роль `Instrumentation` в lifecycle?
**A:** `Instrumentation` — прослойка между `ActivityThread` и компонентами. Все lifecycle-вызовы проходят через неё: `newActivity()` (создание), `callActivityOnCreate()` (→ `performCreate()` → `onCreate()`), `callActivityOnResume()` и т.д. В обычном приложении — стандартная реализация. В тестах (`androidTest`) — `AndroidJUnitRunner` (наследник `Instrumentation`), позволяющий Espresso и UIAutomator контролировать lifecycle.

### Карточка 6
**Q:** Что хранится в `ActivityClientRecord` и почему это важно?
**A:** `ActivityClientRecord` (ACR) — внутренний класс, хранящий всё состояние Activity: `token` (IBinder), `activity` (экземпляр), `state` (savedInstanceState), `lastNonConfigurationInstances` (ViewModelStore!), `lifecycleState`, конфигурацию. Критично: при config change ACR **переиспользуется** — старая Activity уничтожается, новая создаётся, но ACR (и ViewModelStore) сохраняются. Это механизм выживания ViewModel при повороте экрана.

### Карточка 7
**Q:** Почему `onDestroy()` не гарантирован и что это значит для разработчика?
**A:** Low Memory Killer использует `kill -9` (SIGKILL) — процесс убит мгновенно без возможности выполнить код. `onDestroy()`, `onStop()`, `finalize()` — ничего не вызывается. Следствия: 1) Никогда не полагайтесь на `onDestroy()` для сохранения данных; 2) Сохраняйте важные данные в `onStop()` (гарантирован перед уходом в фон); 3) Используйте persistent storage (Room, DataStore) для критичных данных; 4) `savedInstanceState` сохраняется AMS ДО process death (в `onSaveInstanceState()`).

---

## Куда дальше

| Направление | Файл | Что изучить |
|---|---|---|
| Lifecycle Activity | [[android-activity-lifecycle]] | Полный lifecycle, edge cases, multi-window |
| Handler/Looper | [[android-handler-looper]] | MessageQueue, idle handlers, синхронные barriers |
| Binder IPC | [[android-binder-ipc]] | Протокол, threading model, death notification |
| System Services | [[android-system-services]] | AMS, WMS, PMS — серверная сторона |
| Context | [[android-context-internals]] | ContextImpl, ContextWrapper, memory leaks |
| Boot Process | [[android-boot-process]] | Zygote, system_server, init |
| App Startup | [[android-app-startup-performance]] | Оптимизация cold/warm/hot start |
| Service Internals | [[android-service-internals]] | handleCreateService(), bindService() flow |
| Architecture | [[android-architecture]] | Общая архитектура Android OS |

---

## Связи

```
                    ┌──────────────────────┐
                    │   android-boot-      │
                    │   process            │
                    │   (Zygote fork)      │
                    └──────────┬───────────┘
                               │
                               ▼
┌──────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│ android-     │    │                      │    │ android-         │
│ binder-ipc   │◄──►│  android-activity    │◄──►│ handler-looper   │
│ (IPC)        │    │  thread-internals    │    │ (event loop)     │
└──────────────┘    │  (ЭТОТ ФАЙЛ)         │    └──────────────────┘
                    │                      │
                    └──┬────────┬───────┬──┘
                       │        │       │
          ┌────────────┘        │       └────────────┐
          ▼                     ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│ android-activity │ │ android-context  │ │ android-app-     │
│ -lifecycle       │ │ -internals       │ │ startup-         │
│ (callbacks)      │ │ (ContextImpl)    │ │ performance      │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │                                        │
          ▼                                        ▼
┌──────────────────┐                    ┌──────────────────┐
│ android-system-  │                    │ android-service-  │
│ services         │                    │ internals         │
│ (AMS, WMS)       │                    │ (Service lifecycle)│
└──────────────────┘                    └──────────────────┘
```

**Прямые связи:**
- [[android-activity-lifecycle]] — lifecycle callbacks, которые диспетчеризует ActivityThread
- [[android-handler-looper]] — механизм event loop (Looper, Handler, MessageQueue), используемый в main()
- [[android-binder-ipc]] — IPC-протокол для связи ApplicationThread ↔ AMS
- [[android-system-services]] — серверная сторона (AMS, ATMS), отправляющая команды
- [[android-context-internals]] — ContextImpl создаётся в performLaunchActivity() и handleBindApplication()
- [[android-boot-process]] — Zygote fork → ActivityThread.main()
- [[android-app-startup-performance]] — оптимизация handleBindApplication() и ContentProvider init
- [[android-service-internals]] — handleCreateService(), handleBindService() в ActivityThread
- [[android-architecture]] — общая архитектура, в которую вписывается ActivityThread

---

## Источники

### AOSP Source Code
- [ActivityThread.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/app/ActivityThread.java) — главный исходный файл
- [ClientTransactionHandler.java](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/app/ClientTransactionHandler.java) — базовый класс ActivityThread
- [IApplicationThread.aidl](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/app/IApplicationThread.aidl) — Binder-интерфейс
- [TransactionExecutor.java](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/app/servertransaction/TransactionExecutor.java) — исполнитель lifecycle state machine
- [ClientTransaction.java](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/core/java/android/app/servertransaction/ClientTransaction.java) — контейнер lifecycle-команд
- [LaunchActivityItem.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/app/servertransaction/LaunchActivityItem.java) — команда запуска Activity
- [Instrumentation.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/app/Instrumentation.java) — тестовый перехватчик
- [ActivityManagerService.java](https://github.com/aosp-mirror/platform_frameworks_base/blob/master/services/core/java/com/android/server/am/ActivityManagerService.java) — серверная сторона
- [ActivityTaskSupervisor.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/services/core/java/com/android/server/wm/ActivityTaskSupervisor.java) — координатор запуска Activity

### Книги
- **"Android Internals: A Confectioner's Cookbook"** — Jonathan Levin. Глубокий разбор внутренностей Android, включая ActivityThread и Binder
- **"Android Programming: The Big Nerd Ranch Guide"** — Bill Phillips, Chris Stewart. Глава о Activity lifecycle с объяснением внутренних механизмов
- **"Android System Programming"** — Roger Ye. Системное программирование Android, процессы и IPC

### Статьи и блоги
- [Android Activity Lifecycle Blueprint](https://8ksec.io/a-blueprint-of-android-activity-lifecycle/) — детальная визуализация lifecycle с точки зрения AOSP
- [Internal AOSP process when user clicks App Icon from Launcher](https://medium.com/@boopalan457/internal-aosp-process-when-user-clicks-app-icon-from-launcher-81113bf3c111) — пошаговый разбор запуска приложения
- [Binder Threading Model](https://medium.com/swlh/binder-threading-model-79077b7c892c) — модель потоков Binder
- [Instrumentation Tests — Android Open Source Project](https://source.android.com/docs/core/tests/development/instrumentation) — официальная документация по Instrumentation
- [Build instrumented tests — Android Developers](https://developer.android.com/training/testing/instrumented-tests) — руководство по тестированию с Instrumentation

### Видео
- **"Android Internals for Developers"** — Effie Barak, Google I/O — обзор внутренностей для разработчиков
- **"The Activity Lifecycle"** — Android Developers на YouTube — официальное объяснение lifecycle
- **"Deep Dive into Android IPC/Binder Framework"** — Android Dev Summit — глубокий разбор Binder
