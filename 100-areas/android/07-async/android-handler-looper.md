---
title: "Handler, Looper и MessageQueue: устройство Main Thread"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/threading
  - type/deep-dive
  - level/advanced
related:
  - "[[android-async-evolution]]"
  - "[[android-threading]]"
  - "[[os-processes-threads]]"
  - "[[android-memory-leaks]]"
cs-foundations: [event-loop, message-queue, producer-consumer, thread-confinement]
prerequisites:
  - "[[android-threading]]"
  - "[[android-activity-lifecycle]]"
---

# Handler, Looper и MessageQueue: устройство Main Thread

> Handler, Looper и MessageQueue — низкоуровневая триада, на которой построена вся асинхронная обработка в Android. Понимание этих механизмов критично для отладки ANR, предотвращения memory leaks и понимания внутреннего устройства Kotlin Coroutines.

---

## Зачем это нужно

### Проблема: скрытая сложность под капотом

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| ANR (Application Not Responding) | Main Thread заблокирован >5 сек | Принудительное закрытие приложения |
| Memory leak при ротации экрана | Handler держит ссылку на Activity | Рост потребления памяти, OOM |
| Потерянные UI обновления | Сообщения в очереди после onDestroy | Crash или некорректное поведение |
| Непонятное поведение Coroutines | Не знаем, что Dispatchers.Main = Handler | Неправильная отладка |

### Актуальность в 2024-2025

**Handler() без Looper — deprecated!**

```kotlin
// ❌ DEPRECATED (с Android R / API 30)
val handler = Handler()  // Implicit Looper can lead to bugs

// ✅ ПРАВИЛЬНО: явное указание Looper
val handler = Handler(Looper.getMainLooper())
```

**Почему deprecated?** Неявный выбор Looper приводит к:
- **Silent data loss** — операции теряются если Handler создан с неправильным Looper
- **Crashes** — создание Handler в потоке без Looper
- **Race conditions** — поток может не совпадать с ожидаемым

**Kotlin Coroutines под капотом = Handler:**

```kotlin
// Dispatchers.Main на Android реализован через Handler
val mainDispatcher = HandlerDispatcher(Handler(Looper.getMainLooper()))

// Dispatchers.Main.immediate — оптимизация для избежания лишнего dispatch
// Если уже на Main Thread — выполняет сразу
```

**Статистика (2024):**
- **73%** Kotlin проектов используют Coroutines ([JetBrains Survey](https://www.jetbrains.com/lp/devecosystem-2024/kotlin/))
- Handler всё ещё нужен для: работы с Framework API, IdleHandler, точного timing, legacy кода
- Memory leaks от Handler — в **топ-7** частых проблем Android ([Medium: Top 7 Android Memory Leaks](https://artemasoyan.medium.com/top-7-android-memory-leaks-and-how-to-avoid-them-in-2025-b77e15a7b62e))

**Что вы узнаете:**
1. Как работает Main Thread изнутри (ActivityThread.main())
2. MessageQueue и epoll на уровне Linux kernel
3. Handler anti-patterns и memory leak patterns
4. Сравнение Handler vs Coroutines с примерами миграции
5. Когда Handler всё ещё необходим

---

## Prerequisites

Для полного понимания материала необходимо:

- **[[os-processes-threads]]** — понимание потоков на уровне операционной системы, разница между процессами и потоками, планирование потоков
- **Базовое понимание Android lifecycle** — знание основных состояний Activity и Fragment
- **Основы Java/Kotlin** — понимание классов, наследования, WeakReference

## Введение

Handler, Looper и MessageQueue образуют фундаментальную триаду, на которой построена вся асинхронная обработка в Android. Это низкоуровневый механизм, который обеспечивает:

- Обработку UI событий на Main Thread
- Планирование и выполнение отложенных задач
- Коммуникацию между потоками
- Основу для всех высокоуровневых асинхронных API (AsyncTask, IntentService, HandlerThread)

Понимание этой триады критически важно для:

1. **Отладки проблем с производительностью** — ANR (Application Not Responding) возникает когда Main Thread заблокирован
2. **Предотвращения memory leaks** — неправильное использование Handler — одна из самых частых причин утечек памяти
3. **Понимания современных альтернатив** — Kotlin Coroutines построены на похожих принципах
4. **Работы с legacy кодом** — Handler активно используется в существующих проектах

## Терминология

### Looper
**Looper** — бесконечный цикл обработки сообщений, привязанный к конкретному потоку. Каждый поток может иметь максимум один Looper. Looper извлекает Message из очереди и диспетчеризует их соответствующим Handler'ам.

### Handler
**Handler** — интерфейс для отправки и обработки сообщений (Message) и задач (Runnable), ассоциированных с MessageQueue конкретного Looper. Handler'ы создаются в контексте Looper и используют его MessageQueue.

### MessageQueue
**MessageQueue** — упорядоченная по времени очередь сообщений. Несмотря на название "Queue", внутри реализована как односвязный список, отсортированный по времени выполнения (when).

### Message
**Message** — объект данных, содержащий описание и произвольные данные, которые могут быть отправлены Handler'у. Message содержит:
- `what` — идентификатор типа сообщения
- `arg1`, `arg2` — целочисленные параметры
- `obj` — произвольный объект
- `data` — Bundle с дополнительными данными
- `when` — время выполнения (SystemClock.uptimeMillis)
- `target` — Handler, который должен обработать сообщение

### Runnable
**Runnable** — функциональный интерфейс с единственным методом `run()`. Может использоваться как альтернатива Message для простых задач. Под капотом Handler оборачивает Runnable в Message.

## Как устроен Main Thread

### ActivityThread.main() — точка входа

Когда Android запускает приложение, создаётся процесс и вызывается `ActivityThread.main()` — это настоящая точка входа Android приложения (не `onCreate()` Activity).

```java
// android/app/ActivityThread.java (упрощённо)
public final class ActivityThread {

    public static void main(String[] args) {
        // 1. Инициализация trace для профилирования
        Trace.traceBegin(Trace.TRACE_TAG_ACTIVITY_MANAGER, "ActivityThreadMain");

        // 2. Установка default обработчика uncaught exceptions
        AndroidOs.install();

        // 3. Установка process priority
        Process.setArgV0("<pre-initialized>");

        // 4. КРИТИЧЕСКИ ВАЖНО: Подготовка Main Looper
        Looper.prepareMainLooper();

        // 5. Создание ActivityThread и attach к системе
        ActivityThread thread = new ActivityThread();
        thread.attach(false, startSeq);

        // 6. Получение Handler для Main Thread
        if (sMainThreadHandler == null) {
            sMainThreadHandler = thread.getHandler();
        }

        Trace.traceEnd(Trace.TRACE_TAG_ACTIVITY_MANAGER);

        // 7. БЕСКОНЕЧНЫЙ ЦИКЛ: запуск обработки сообщений
        Looper.loop();

        // 8. Этот код никогда не выполнится (loop() бесконечен)
        throw new RuntimeException("Main thread loop unexpectedly exited");
    }
}
```

### Looper.prepareMainLooper() и Looper.loop()

#### Looper.prepareMainLooper()

```java
// android/os/Looper.java
public final class Looper {
    // ThreadLocal хранит Looper для каждого потока
    static final ThreadLocal<Looper> sThreadLocal = new ThreadLocal<Looper>();

    // Глобальная ссылка на Main Looper
    private static Looper sMainLooper;

    // MessageQueue этого Looper'а
    final MessageQueue mQueue;

    // Поток, которому принадлежит Looper
    final Thread mThread;

    public static void prepareMainLooper() {
        // Создаём Looper с quitAllowed=false
        // Main Looper НЕЛЬЗЯ остановить
        prepare(false);

        synchronized (Looper.class) {
            if (sMainLooper != null) {
                throw new IllegalStateException(
                    "The main Looper has already been prepared.");
            }
            sMainLooper = myLooper();
        }
    }

    private static void prepare(boolean quitAllowed) {
        if (sThreadLocal.get() != null) {
            throw new RuntimeException(
                "Only one Looper may be created per thread");
        }
        sThreadLocal.set(new Looper(quitAllowed));
    }

    private Looper(boolean quitAllowed) {
        // Создаём MessageQueue
        mQueue = new MessageQueue(quitAllowed);
        mThread = Thread.currentThread();
    }

    // Получить Looper текущего потока
    public static @Nullable Looper myLooper() {
        return sThreadLocal.get();
    }

    // Получить Main Looper (можно вызвать из любого потока)
    public static Looper getMainLooper() {
        synchronized (Looper.class) {
            return sMainLooper;
        }
    }
}
```

#### Looper.loop() — бесконечный цикл обработки

```java
public static void loop() {
    final Looper me = myLooper();
    if (me == null) {
        throw new RuntimeException(
            "No Looper; Looper.prepare() wasn't called on this thread.");
    }

    final MessageQueue queue = me.mQueue;

    // Бесконечный цикл
    for (;;) {
        // Блокирующий вызов: ждём следующее сообщение
        // Может вернуть null только если MessageQueue был quit
        Message msg = queue.next(); // might block

        if (msg == null) {
            // MessageQueue был остановлен — выходим из цикла
            return;
        }

        try {
            // Диспетчеризация сообщения к target Handler
            // msg.target — это Handler, который отправил сообщение
            msg.target.dispatchMessage(msg);
        } catch (Exception exception) {
            throw exception;
        } finally {
            // Возвращаем Message в pool для переиспользования
            msg.recycleUnchecked();
        }
    }
}
```

**Ключевые моменты:**

1. **Блокирующий вызов**: `queue.next()` блокирует поток, пока не появится сообщение или не наступит время выполнения отложенного сообщения
2. **Нет активного ожидания**: CPU не тратится впустую — поток спит на уровне ядра
3. **Target Handler**: каждое сообщение знает, какой Handler должен его обработать
4. **Message recycling**: после обработки Message возвращается в pool для переиспользования

### MessageQueue internals

MessageQueue — это не классическая очередь (FIFO), а **priority queue**, отсортированная по времени выполнения.

```java
// android/os/MessageQueue.java (упрощённо)
public final class MessageQueue {
    // Голова односвязного списка сообщений
    Message mMessages;

    // Native pointer для работы с epoll
    private long mPtr;

    // Флаг остановки очереди
    private boolean mQuitting;

    MessageQueue(boolean quitAllowed) {
        mQuitAllowed = quitAllowed;
        // Инициализация native части (epoll)
        mPtr = nativeInit();
    }

    // Вставка сообщения в очередь
    boolean enqueueMessage(Message msg, long when) {
        if (msg.target == null) {
            throw new IllegalArgumentException("Message must have a target.");
        }

        synchronized (this) {
            if (mQuitting) {
                // Очередь останавливается — отклоняем сообщение
                msg.recycle();
                return false;
            }

            msg.markInUse();
            msg.when = when;

            Message p = mMessages;
            boolean needWake;

            // СЛУЧАЙ 1: Очередь пуста, или сообщение должно выполниться раньше всех
            if (p == null || when == 0 || when < p.when) {
                // Вставляем в голову списка
                msg.next = p;
                mMessages = msg;
                needWake = mBlocked; // Нужно разбудить поток?
            }
            // СЛУЧАЙ 2: Вставка в середину списка
            else {
                // Обычно не нужно будить поток, если вставляем не в голову
                needWake = mBlocked && p.target == null && msg.isAsynchronous();

                Message prev;
                // Поиск позиции для вставки (список отсортирован по when)
                for (;;) {
                    prev = p;
                    p = p.next;
                    if (p == null || when < p.when) {
                        break;
                    }
                    if (needWake && p.isAsynchronous()) {
                        needWake = false;
                    }
                }
                // Вставка между prev и p
                msg.next = p;
                prev.next = msg;
            }

            // Будим поток, если нужно
            if (needWake) {
                nativeWake(mPtr);
            }
        }
        return true;
    }

    // Извлечение следующего сообщения
    Message next() {
        final long ptr = mPtr;
        if (ptr == 0) {
            // MessageQueue был уничтожен
            return null;
        }

        int pendingIdleHandlerCount = -1;
        int nextPollTimeoutMillis = 0;

        for (;;) {
            if (nextPollTimeoutMillis != 0) {
                Binder.flushPendingCommands();
            }

            // БЛОКИРУЮЩИЙ ВЫЗОВ: ожидание на уровне native (epoll)
            nativePollOnce(ptr, nextPollTimeoutMillis);

            synchronized (this) {
                final long now = SystemClock.uptimeMillis();
                Message prevMsg = null;
                Message msg = mMessages;

                // Пропускаем sync barrier (используется для async messages)
                if (msg != null && msg.target == null) {
                    // Sync barrier — ищем первое async сообщение
                    do {
                        prevMsg = msg;
                        msg = msg.next;
                    } while (msg != null && !msg.isAsynchronous());
                }

                if (msg != null) {
                    if (now < msg.when) {
                        // Следующее сообщение ещё не готово — вычисляем время ожидания
                        nextPollTimeoutMillis = (int) Math.min(
                            msg.when - now, Integer.MAX_VALUE);
                    } else {
                        // Сообщение готово — извлекаем из списка
                        mBlocked = false;
                        if (prevMsg != null) {
                            prevMsg.next = msg.next;
                        } else {
                            mMessages = msg.next;
                        }
                        msg.next = null;
                        msg.markInUse();
                        return msg; // ВОЗВРАЩАЕМ СООБЩЕНИЕ
                    }
                } else {
                    // Очередь пуста — ждём бесконечно
                    nextPollTimeoutMillis = -1;
                }

                // Проверка на quit
                if (mQuitting) {
                    dispose();
                    return null;
                }

                // IdleHandlers обработка (не рассматриваем подробно)
                // ...
            }

            // Обработка IdleHandlers
            // ...

            // Следующая итерация цикла
            pendingIdleHandlerCount = 0;
            nextPollTimeoutMillis = 0;
        }
    }
}
```

**Ключевые моменты:**

1. **Односвязный список**: сообщения хранятся в linked list, отсортированном по `when`
2. **Insertion sort**: новые сообщения вставляются в нужную позицию за O(n)
3. **Блокировка на native уровне**: `nativePollOnce()` использует epoll для эффективного ожидания
4. **Sync barriers**: механизм для приоритизации асинхронных сообщений (используется для UI обновлений)

### epoll на уровне Linux

`nativePollOnce()` и `nativeWake()` — это JNI вызовы к native коду, который использует механизм **epoll** (Linux) для эффективного ожидания событий.

```cpp
// frameworks/base/core/jni/android_os_MessageQueue.cpp (упрощённо)

// Структура для native MessageQueue
struct NativeMessageQueue : public MessageQueue {
    NativeMessageQueue();
    virtual ~NativeMessageQueue();

    virtual void raiseException(JNIEnv* env, const char* msg, jthrowable exceptionObj);

    // Looper для работы с epoll
    sp<Looper> mLooper;
};

// Инициализация
static jlong android_os_MessageQueue_nativeInit(JNIEnv* env, jclass clazz) {
    NativeMessageQueue* nativeMessageQueue = new NativeMessageQueue();
    nativeMessageQueue->incStrong(env);
    return reinterpret_cast<jlong>(nativeMessageQueue);
}

// Ожидание событий (epoll_wait)
static void android_os_MessageQueue_nativePollOnce(
        JNIEnv* env, jobject obj, jlong ptr, jint timeoutMillis) {
    NativeMessageQueue* nativeMessageQueue =
        reinterpret_cast<NativeMessageQueue*>(ptr);

    // Вызываем pollOnce на Looper, который использует epoll_wait
    nativeMessageQueue->pollOnce(env, obj, timeoutMillis);
}

// Пробуждение (write в eventfd)
static void android_os_MessageQueue_nativeWake(JNIEnv* env, jclass clazz, jlong ptr) {
    NativeMessageQueue* nativeMessageQueue =
        reinterpret_cast<NativeMessageQueue*>(ptr);
    nativeMessageQueue->wake();
}
```

**Как работает epoll:**

1. **Создание epoll instance**: при инициализации MessageQueue создаётся epoll file descriptor
2. **Создание eventfd**: создаётся специальный file descriptor для пробуждения
3. **epoll_ctl**: eventfd добавляется в epoll для мониторинга
4. **epoll_wait**: поток блокируется, ожидая события на eventfd или таймаут
5. **Пробуждение**: когда новое сообщение добавляется в очередь, вызывается `write()` в eventfd
6. **epoll_wait возвращает управление**: поток просыпается и обрабатывает сообщение

**Преимущества epoll:**

- **Нет активного ожидания (busy-wait)**: CPU не тратится впустую
- **Эффективность**: поток спит на уровне ядра, используя минимум ресурсов
- **Точность таймеров**: можно указать точное время пробуждения
- **Масштабируемость**: epoll эффективен даже с большим количеством file descriptors

### Диаграмма потока сообщений

```
┌─────────────────────────────────────────────────────────────────┐
│                         Main Thread                              │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ ActivityThread.main()                                     │   │
│  │  1. Looper.prepareMainLooper()                           │   │
│  │  2. new ActivityThread()                                  │   │
│  │  3. thread.attach(...)                                    │   │
│  │  4. Looper.loop()  ◄────────────────────┐                │   │
│  └──────────────────────────────────────────│────────────────┘   │
│                                              │                    │
│  ┌──────────────────────────────────────────│────────────────┐   │
│  │ Looper.loop()                            │                 │   │
│  │  for(;;) {                                │                 │   │
│  │    msg = queue.next() ◄──────┐           │                 │   │
│  │    msg.target.dispatchMessage(msg)       │                 │   │
│  │    msg.recycle()                          │                 │   │
│  │  }                                        │                 │   │
│  └───────────────────────────────────────────│────────────────┘   │
│                                              │                    │
│  ┌──────────────────────────────────────────│────────────────┐   │
│  │ MessageQueue                              │                 │   │
│  │                                           │                 │   │
│  │  next() {                                 │                 │   │
│  │    nativePollOnce(timeout) ◄──┐          │                 │   │
│  │    return mMessages            │          │                 │   │
│  │  }                              │          │                 │   │
│  │                                 │          │                 │   │
│  │  enqueueMessage(msg) {          │          │                 │   │
│  │    insert into sorted list      │          │                 │   │
│  │    nativeWake() ────────────────┘          │                 │   │
│  │  }                                         │                 │   │
│  │                                            │                 │   │
│  │  mMessages: [Msg1]→[Msg2]→[Msg3]→null     │                 │   │
│  │             when=100  150    200           │                 │   │
│  └────────────────────────────────────────────│────────────────┘   │
│                                              │                    │
│  ┌──────────────────────────────────────────│────────────────┐   │
│  │ Handler (Main Thread)                    │                 │   │
│  │                                           │                 │   │
│  │  post(Runnable r) ────────────────────────┼────┐            │   │
│  │  sendMessage(Message msg) ────────────────┼────┤            │   │
│  │  postDelayed(Runnable, delay) ────────────┼────┤            │   │
│  │                                           │    │            │   │
│  │  dispatchMessage(msg) {                   │    │            │   │
│  │    if (msg.callback != null)              │    │            │   │
│  │      msg.callback.run()                   │    │            │   │
│  │    else                                   │    │            │   │
│  │      handleMessage(msg)                   │    │            │   │
│  │  }                                        │    │            │   │
│  └───────────────────────────────────────────┼────┼───────────┘   │
│                                              │    │               │
└──────────────────────────────────────────────│────│───────────────┘
                                               │    │
┌─────────────────────────────────────────────┼────┼────────────────┐
│                    Background Thread         │    │                │
│                                              │    │                │
│  ┌───────────────────────────────────────────┼───┼─────────────┐  │
│  │ Handler (Background)                      │   │              │  │
│  │                                           │   │              │  │
│  │  Looper.prepare() ◄───────────────────────┘   │              │  │
│  │  handler = Handler(Looper.myLooper())         │              │  │
│  │  Looper.loop()                                │              │  │
│  │                                               │              │  │
│  │  Messages enqueued to MessageQueue ───────────┘              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

Native Layer (Linux)
┌────────────────────────────────────────────────────────────────────┐
│  epoll instance                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ epoll_wait(timeout) ◄─── nativePollOnce()                    │  │
│  │   - blocks thread until event or timeout                      │  │
│  │   - CPU sleeping, no busy-wait                                │  │
│  │                                                                │  │
│  │ eventfd ◄─── nativeWake()                                     │  │
│  │   - write() to eventfd wakes up epoll_wait                    │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────┘
```

**Поток выполнения:**

1. **Main Thread запускается**: `ActivityThread.main()` → `Looper.prepareMainLooper()` → `Looper.loop()`
2. **Looper.loop() входит в бесконечный цикл**: вызывает `queue.next()`
3. **MessageQueue.next() блокируется**: `nativePollOnce()` → `epoll_wait()` на уровне ядра
4. **Background поток отправляет сообщение**: `handler.post(runnable)` → `queue.enqueueMessage()`
5. **MessageQueue будит Main Thread**: `nativeWake()` → `write(eventfd)` → `epoll_wait()` возвращает управление
6. **MessageQueue.next() возвращает сообщение**: извлекает из списка первое готовое сообщение
7. **Looper диспетчеризует**: `msg.target.dispatchMessage(msg)`
8. **Handler обрабатывает**: `handleMessage()` или `runnable.run()`
9. **Message возвращается в pool**: `msg.recycle()`
10. **Цикл повторяется**: `queue.next()` снова блокируется в ожидании

## Handler: отправка и обработка сообщений

### post() vs sendMessage()

Handler предоставляет два основных API для отправки задач:

#### post() — для Runnable

```kotlin
// Использование: простые задачи без параметров
handler.post {
    // Код выполнится на потоке Handler'а
    textView.text = "Updated"
}

// Под капотом Handler оборачивает Runnable в Message
public final boolean post(@NonNull Runnable r) {
    return sendMessageDelayed(getPostMessage(r), 0);
}

private static Message getPostMessage(Runnable r) {
    Message m = Message.obtain();
    m.callback = r; // Runnable сохраняется в callback
    return m;
}
```

#### sendMessage() — для Message с данными

```kotlin
// Использование: сложные задачи с параметрами
val message = Message.obtain().apply {
    what = MSG_UPDATE_PROGRESS
    arg1 = progress
    arg2 = total
    obj = additionalData
}
handler.sendMessage(message)

// Обработка в Handler
override fun handleMessage(msg: Message) {
    when (msg.what) {
        MSG_UPDATE_PROGRESS -> {
            val progress = msg.arg1
            val total = msg.arg2
            updateProgressBar(progress, total)
        }
    }
}
```

**Когда что использовать:**

| Критерий | post(Runnable) | sendMessage(Message) |
|----------|----------------|----------------------|
| **Простота** | Проще для одиночных задач | Требует создания Message |
| **Параметры** | Захватываются через замыкание | Явная передача через what/arg1/arg2/obj |
| **Типизация** | Нет типизации сообщений | Явная типизация через what (constants) |
| **Переиспользование** | Создаётся новый Message каждый раз | Можно переиспользовать через obtain() |
| **Производительность** | Немного медленнее (создание Message) | Быстрее с obtain() из pool |
| **Читаемость** | Лучше для inline кода | Лучше для switch/when по типам |

**Рекомендации:**

- **Используйте post()** для простых UI обновлений и одноразовых задач
- **Используйте sendMessage()** для сложной логики с множеством типов сообщений
- **Всегда используйте Message.obtain()** вместо `new Message()` для производительности

### Message pooling и recycling

Message — это объект, и его создание/уничтожение создаёт нагрузку на GC. Android оптимизирует это через **object pooling**.

```java
// android/os/Message.java (упрощённо)
public final class Message implements Parcelable {
    // Пул переиспользуемых объектов
    private static final Object sPoolSync = new Object();
    private static Message sPool;
    private static int sPoolSize = 0;
    private static final int MAX_POOL_SIZE = 50;

    // Следующий Message в пуле (linked list)
    Message next;

    // Флаги состояния
    int flags;
    static final int FLAG_IN_USE = 1 << 0;

    /**
     * Получить Message из пула (ВСЕГДА ИСПОЛЬЗУЙТЕ ЭТОТ МЕТОД)
     */
    public static Message obtain() {
        synchronized (sPoolSync) {
            if (sPool != null) {
                // Извлекаем из головы пула
                Message m = sPool;
                sPool = m.next;
                m.next = null;
                m.flags = 0; // Сбрасываем флаги
                sPoolSize--;
                return m;
            }
        }
        // Пул пуст — создаём новый
        return new Message();
    }

    /**
     * Получить Message с копированием из существующего
     */
    public static Message obtain(Message orig) {
        Message m = obtain();
        m.what = orig.what;
        m.arg1 = orig.arg1;
        m.arg2 = orig.arg2;
        m.obj = orig.obj;
        m.replyTo = orig.replyTo;
        m.sendingUid = orig.sendingUid;
        if (orig.data != null) {
            m.data = new Bundle(orig.data);
        }
        m.target = orig.target;
        m.callback = orig.callback;
        return m;
    }

    /**
     * Получить Message с target Handler
     */
    public static Message obtain(Handler h) {
        Message m = obtain();
        m.target = h;
        return m;
    }

    /**
     * Получить Message с target Handler и callback
     */
    public static Message obtain(Handler h, Runnable callback) {
        Message m = obtain();
        m.target = h;
        m.callback = callback;
        return m;
    }

    /**
     * Получить Message с параметрами
     */
    public static Message obtain(Handler h, int what) {
        Message m = obtain();
        m.target = h;
        m.what = what;
        return m;
    }

    public static Message obtain(Handler h, int what, Object obj) {
        Message m = obtain();
        m.target = h;
        m.what = what;
        m.obj = obj;
        return m;
    }

    public static Message obtain(Handler h, int what, int arg1, int arg2) {
        Message m = obtain();
        m.target = h;
        m.what = what;
        m.arg1 = arg1;
        m.arg2 = arg2;
        return m;
    }

    public static Message obtain(Handler h, int what, int arg1, int arg2, Object obj) {
        Message m = obtain();
        m.target = h;
        m.what = what;
        m.arg1 = arg1;
        m.arg2 = arg2;
        m.obj = obj;
        return m;
    }

    /**
     * Возврат Message в пул (вызывается автоматически)
     */
    public void recycle() {
        if (isInUse()) {
            // Message ещё в очереди — игнорируем
            return;
        }
        recycleUnchecked();
    }

    void recycleUnchecked() {
        // Очистка всех полей
        flags = FLAG_IN_USE;
        what = 0;
        arg1 = 0;
        arg2 = 0;
        obj = null;
        replyTo = null;
        sendingUid = UID_NONE;
        workSourceUid = UID_NONE;
        when = 0;
        target = null;
        callback = null;
        data = null;

        synchronized (sPoolSync) {
            if (sPoolSize < MAX_POOL_SIZE) {
                // Добавляем в голову пула
                next = sPool;
                sPool = this;
                sPoolSize++;
            }
        }
    }
}
```

**Как работает pooling:**

1. **Пул**: статический linked list из максимум 50 объектов
2. **obtain()**: извлекает из головы списка или создаёт новый
3. **recycle()**: очищает поля и возвращает в голову списка
4. **Автоматический recycling**: Looper вызывает `recycle()` после обработки

**Примеры использования:**

```kotlin
// ПРАВИЛЬНО: использование obtain()
val msg1 = Message.obtain(handler, WHAT_UPDATE)
val msg2 = Message.obtain(handler, WHAT_PROGRESS, progress, total)
val msg3 = Message.obtain().apply {
    target = handler
    what = WHAT_CUSTOM
    obj = customData
}

// НЕПРАВИЛЬНО: создание через конструктор
val msg = Message() // Не переиспользует объекты из пула
msg.target = handler
msg.what = WHAT_UPDATE

// Handler автоматически вызовет recycle() после обработки
handler.sendMessage(msg1)
```

**Измерение эффективности:**

```kotlin
// Без pooling (new Message())
// 1000 сообщений = 1000 аллокаций + GC паузы

// С pooling (Message.obtain())
// 1000 сообщений = ~50 аллокаций (размер пула) + переиспользование
// Снижение нагрузки на GC в ~20 раз
```

### Timing: отложенные и приоритетные сообщения

Handler поддерживает различные стратегии планирования:

#### postDelayed() — выполнение через задержку

```kotlin
// Выполнить через 1 секунду
handler.postDelayed({
    showToast("Delayed action")
}, 1000)

// Под капотом
public final boolean postDelayed(Runnable r, long delayMillis) {
    return sendMessageDelayed(getPostMessage(r), delayMillis);
}

public final boolean sendMessageDelayed(Message msg, long delayMillis) {
    if (delayMillis < 0) {
        delayMillis = 0;
    }
    return sendMessageAtTime(msg, SystemClock.uptimeMillis() + delayMillis);
}

public boolean sendMessageAtTime(Message msg, long uptimeMillis) {
    MessageQueue queue = mQueue;
    if (queue == null) {
        return false;
    }
    return enqueueMessage(queue, msg, uptimeMillis);
}

private boolean enqueueMessage(MessageQueue queue, Message msg, long uptimeMillis) {
    msg.target = this;
    return queue.enqueueMessage(msg, uptimeMillis);
}
```

**Как работает под капотом:**

1. **Преобразование в uptimeMillis**: `delay` преобразуется в абсолютное время
2. **Вставка в отсортированную очередь**: Message вставляется в нужную позицию по `when`
3. **epoll timeout**: если новое сообщение должно выполниться раньше текущего, поток просыпается
4. **Точность**: точность зависит от загрузки Main Thread и может варьироваться

#### postAtTime() — выполнение в конкретное время

```kotlin
// Выполнить в конкретное время (uptimeMillis)
val executeAt = SystemClock.uptimeMillis() + 5000
handler.postAtTime({
    performScheduledAction()
}, executeAt)

// Полезно для синхронизации с другими событиями
val token = "action_token"
handler.postAtTime({
    performAction()
}, token, executeAt)

// Отмена по token
handler.removeCallbacksAndMessages(token)
```

**SystemClock.uptimeMillis() vs System.currentTimeMillis():**

```kotlin
// SystemClock.uptimeMillis() — время с момента загрузки (НЕ включает deep sleep)
// ПРАВИЛЬНО для Handler timing
val uptime = SystemClock.uptimeMillis()

// System.currentTimeMillis() — wall clock time (UTC)
// НЕПРАВИЛЬНО для Handler — изменится при изменении системного времени
val wallTime = System.currentTimeMillis() // НЕ используйте для timing

// SystemClock.elapsedRealtime() — время с момента загрузки (ВКЛЮЧАЕТ deep sleep)
// Используйте для измерения длительности
val elapsed = SystemClock.elapsedRealtime()
```

#### postAtFrontOfQueue() — приоритетное выполнение

```kotlin
// Вставить в голову очереди (выполнится следующим)
handler.postAtFrontOfQueue {
    urgentAction()
}

public final boolean postAtFrontOfQueue(Runnable r) {
    return sendMessageAtFrontOfQueue(getPostMessage(r));
}

public final boolean sendMessageAtFrontOfQueue(Message msg) {
    MessageQueue queue = mQueue;
    if (queue == null) {
        return false;
    }
    return enqueueMessage(queue, msg, 0); // when = 0 означает "сейчас"
}
```

**Когда использовать:**

- **РЕДКО**: нарушает порядок обработки сообщений
- **Критические действия**: например, очистка ресурсов перед закрытием
- **Альтернатива**: обычно лучше правильно структурировать код, чем использовать приоритеты

#### removeCallbacksAndMessages() — отмена сообщений

```kotlin
// Отменить ВСЕ сообщения и callbacks
handler.removeCallbacksAndMessages(null)

// Отменить по конкретному token
val token = "animation_token"
handler.postDelayed({ animateView() }, token, 1000)
handler.removeCallbacksAndMessages(token) // Отменяет только с этим token

// Отменить конкретный Runnable
val runnable = Runnable { doSomething() }
handler.postDelayed(runnable, 1000)
handler.removeCallbacks(runnable)

// Отменить сообщения с конкретным what
handler.removeMessages(MSG_UPDATE)
```

**Критически важно для предотвращения утечек:**

```kotlin
override fun onDestroy() {
    super.onDestroy()
    // Отменяем все pending сообщения
    handler.removeCallbacksAndMessages(null)
}
```

### Looper.myLooper() vs Looper.getMainLooper()

```kotlin
// Looper.myLooper() — Looper ТЕКУЩЕГО потока
class BackgroundThread : Thread() {
    lateinit var handler: Handler

    override fun run() {
        Looper.prepare() // Создаём Looper для этого потока

        handler = Handler(Looper.myLooper()!!) { msg ->
            // Обработка на background потоке
            processMessage(msg)
            true
        }

        Looper.loop() // Запускаем цикл обработки
    }
}

// Looper.getMainLooper() — Main Looper (доступен из любого потока)
class NetworkClient {
    private val mainHandler = Handler(Looper.getMainLooper())

    fun fetchData() {
        Thread {
            val data = performNetworkRequest()

            // Переключаемся на Main Thread для UI обновления
            mainHandler.post {
                updateUI(data)
            }
        }.start()
    }
}

// Проверка текущего потока
fun isMainThread(): Boolean {
    return Looper.myLooper() == Looper.getMainLooper()
}

// Выполнение на Main Thread из любого потока
fun runOnMainThread(action: () -> Unit) {
    if (Looper.myLooper() == Looper.getMainLooper()) {
        // Уже на Main Thread — выполняем сразу
        action()
    } else {
        // На другом потоке — переключаемся на Main
        Handler(Looper.getMainLooper()).post(action)
    }
}
```

## HandlerThread

HandlerThread — это класс, который инкапсулирует создание потока с Looper.

### Что это и когда использовать

```kotlin
// android/os/HandlerThread.java (упрощённо)
public class HandlerThread extends Thread {
    private int mPriority;
    private int mTid = -1;
    private Looper mLooper;
    private @Nullable Handler mHandler;

    public HandlerThread(String name) {
        super(name);
        mPriority = Process.THREAD_PRIORITY_DEFAULT;
    }

    public HandlerThread(String name, int priority) {
        super(name);
        mPriority = priority;
    }

    @Override
    public void run() {
        mTid = Process.myTid();
        Looper.prepare();
        synchronized (this) {
            mLooper = Looper.myLooper();
            notifyAll(); // Уведомляем getLooper()
        }
        Process.setThreadPriority(mPriority);
        onLooperPrepared(); // Hook для подклассов
        Looper.loop();
        mTid = -1;
    }

    public Looper getLooper() {
        if (!isAlive()) {
            return null;
        }

        // Если Looper ещё не готов, ждём
        synchronized (this) {
            while (isAlive() && mLooper == null) {
                try {
                    wait();
                } catch (InterruptedException e) {
                }
            }
        }
        return mLooper;
    }

    public boolean quit() {
        Looper looper = getLooper();
        if (looper != null) {
            looper.quit();
            return true;
        }
        return false;
    }

    public boolean quitSafely() {
        Looper looper = getLooper();
        if (looper != null) {
            looper.quitSafely();
            return true;
        }
        return false;
    }
}
```

**Использование:**

```kotlin
class DatabaseManager {
    private val handlerThread = HandlerThread(
        "DatabaseThread",
        Process.THREAD_PRIORITY_BACKGROUND
    )

    private lateinit var dbHandler: Handler

    init {
        handlerThread.start()
        dbHandler = Handler(handlerThread.looper)
    }

    fun insertData(data: Data) {
        dbHandler.post {
            // Выполняется на background потоке
            database.insert(data)
        }
    }

    fun queryData(callback: (List<Data>) -> Unit) {
        dbHandler.post {
            val results = database.query()

            // Возвращаем результат на Main Thread
            Handler(Looper.getMainLooper()).post {
                callback(results)
            }
        }
    }

    fun shutdown() {
        handlerThread.quitSafely()
    }
}
```

**Когда использовать HandlerThread:**

1. **Последовательная обработка задач**: когда нужна очередь задач на background потоке
2. **Долгоживущие операции**: фоновый поток, который существует весь lifecycle приложения
3. **Альтернатива ThreadPoolExecutor**: когда важен порядок выполнения

**Когда НЕ использовать:**

1. **Короткие задачи**: лучше использовать Coroutines или ThreadPoolExecutor
2. **Параллельная обработка**: HandlerThread обрабатывает задачи последовательно
3. **Современный код**: Coroutines с Dispatchers.IO предпочтительнее

### IntentService под капотом

IntentService использует HandlerThread для последовательной обработки Intent'ов в фоне.

```kotlin
// android/app/IntentService.java (упрощённо, DEPRECATED с API 30)
public abstract class IntentService extends Service {
    private volatile Looper mServiceLooper;
    private volatile ServiceHandler mServiceHandler;

    private final class ServiceHandler extends Handler {
        public ServiceHandler(Looper looper) {
            super(looper);
        }

        @Override
        public void handleMessage(Message msg) {
            // Вызываем onHandleIntent на background потоке
            onHandleIntent((Intent)msg.obj);

            // Останавливаем сервис после обработки
            stopSelf(msg.arg1);
        }
    }

    @Override
    public void onCreate() {
        super.onCreate();

        // Создаём HandlerThread
        HandlerThread thread = new HandlerThread("IntentService[" + mName + "]");
        thread.start();

        mServiceLooper = thread.getLooper();
        mServiceHandler = new ServiceHandler(mServiceLooper);
    }

    @Override
    public void onStart(@Nullable Intent intent, int startId) {
        // Создаём Message с Intent
        Message msg = mServiceHandler.obtainMessage();
        msg.arg1 = startId;
        msg.obj = intent;

        // Отправляем в очередь HandlerThread
        mServiceHandler.sendMessage(msg);
    }

    @Override
    public void onDestroy() {
        mServiceLooper.quit();
    }

    // Переопределяется в подклассе
    protected abstract void onHandleIntent(@Nullable Intent intent);
}
```

**Современная альтернатива — WorkManager + CoroutineWorker:**

```kotlin
// Вместо IntentService (deprecated)
class DownloadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val url = inputData.getString("url") ?: return Result.failure()

        return try {
            downloadFile(url)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}

// Запуск
val downloadWork = OneTimeWorkRequestBuilder<DownloadWorker>()
    .setInputData(workDataOf("url" to fileUrl))
    .build()

WorkManager.getInstance(context).enqueue(downloadWork)
```

### Lifecycle management — quit() vs quitSafely()

```kotlin
// quit() — немедленная остановка
fun Looper.quit() {
    mQueue.quit(false)
}

// MessageQueue.quit(safe = false)
void quit(boolean safe) {
    if (!mQuitAllowed) {
        throw new IllegalStateException("Main thread not allowed to quit.");
    }

    synchronized (this) {
        if (mQuitting) {
            return;
        }
        mQuitting = true;

        if (safe) {
            // quitSafely: удаляем только БУДУЩИЕ сообщения
            removeAllFutureMessagesLocked();
        } else {
            // quit: удаляем ВСЕ сообщения
            removeAllMessagesLocked();
        }

        // Будим поток для завершения
        nativeWake(mPtr);
    }
}

private void removeAllMessagesLocked() {
    Message p = mMessages;
    while (p != null) {
        Message n = p.next;
        p.recycleUnchecked();
        p = n;
    }
    mMessages = null;
}

private void removeAllFutureMessagesLocked() {
    final long now = SystemClock.uptimeMillis();
    Message p = mMessages;

    // Ищем первое будущее сообщение
    if (p != null) {
        if (p.when > now) {
            // Первое сообщение в будущем — удаляем всё
            removeAllMessagesLocked();
        } else {
            // Ищем граничное сообщение
            Message n;
            for (;;) {
                n = p.next;
                if (n == null) {
                    return; // Нет будущих сообщений
                }
                if (n.when > now) {
                    break;
                }
                p = n;
            }
            // Удаляем хвост списка (будущие сообщения)
            p.next = null;
            do {
                p = n;
                n = p.next;
                p.recycleUnchecked();
            } while (n != null);
        }
    }
}
```

**Сравнение quit() vs quitSafely():**

| Метод | Поведение | Когда использовать |
|-------|-----------|-------------------|
| **quit()** | Удаляет ВСЕ pending сообщения немедленно | Экстренное завершение, ресурсы должны быть освобождены сразу |
| **quitSafely()** | Обрабатывает текущие и просроченные, удаляет будущие | Graceful shutdown, даём завершиться начатым операциям |

**Примеры:**

```kotlin
class BackgroundProcessor {
    private val handlerThread = HandlerThread("Processor")
    private val handler: Handler

    init {
        handlerThread.start()
        handler = Handler(handlerThread.looper)
    }

    fun process(data: Data) {
        handler.post {
            performProcessing(data)
        }
    }

    // Graceful shutdown — даём завершиться текущим задачам
    fun shutdownGracefully() {
        handlerThread.quitSafely()
        handlerThread.join(5000) // Ждём до 5 секунд
    }

    // Экстренное завершение — прерываем всё
    fun shutdownImmediately() {
        handlerThread.quit()
    }
}

// В Activity/Service
override fun onDestroy() {
    super.onDestroy()
    backgroundProcessor.shutdownGracefully()
}
```

## Anti-patterns и Memory Leaks

Неправильное использование Handler — **одна из самых частых причин утечек памяти** в Android приложениях.

### Non-static inner class Handler — implicit reference

```kotlin
// ПРОБЛЕМНЫЙ КОД — УТЕЧКА ПАМЯТИ!
class MainActivity : AppCompatActivity() {

    // Non-static inner class имеет неявную ссылку на outer class (MainActivity)
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            // Обработка сообщения
            updateUI(msg.arg1)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Отправляем отложенное сообщение на 10 минут
        handler.sendEmptyMessageDelayed(MSG_UPDATE, 10 * 60 * 1000)
    }

    // Пользователь закрывает Activity
    override fun onDestroy() {
        super.onDestroy()
        // Handler НЕ очищен — сообщение всё ещё в MessageQueue
    }
}
```

**Почему происходит утечка:**

```
┌─────────────────────────────────────────────────────────┐
│ MessageQueue (живёт пока жив процесс)                    │
│                                                          │
│  Message (when = now + 10 min)                           │
│    ├── target ───────────────────────┐                   │
│    │                                 │                   │
└────┼─────────────────────────────────┼───────────────────┘
     │                                 │
     ▼                                 │
┌─────────────────────────────────────┼───────────────────┐
│ Handler (anonymous inner class)     │                    │
│    ├── this$0 (implicit reference) ─┤                    │
└────┼─────────────────────────────────┼───────────────────┘
     │                                 │
     ▼                                 │
┌─────────────────────────────────────┼───────────────────┐
│ MainActivity (должна быть GC'd)     │                    │
│    ├── Views                         │                    │
│    ├── Resources                     │                    │
│    ├── Bitmaps                       │                    │
│    └── ... (несколько MB памяти)     │                    │
└──────────────────────────────────────┴───────────────────┘

Цепочка ссылок:
MessageQueue → Message → Handler → MainActivity → Views/Resources

Результат: MainActivity не может быть собрана GC 10 минут!
```

**Проблема:**

1. **Message в очереди**: отложенное сообщение находится в MessageQueue
2. **Message.target**: ссылается на Handler
3. **Handler — inner class**: имеет неявную ссылку `this$0` на MainActivity
4. **MainActivity не может быть GC'd**: пока Message в очереди
5. **Утечка памяти**: вся Activity со всеми View и ресурсами держится в памяти

**Обнаружение в LeakCanary:**

```
┌───────────────────────────────────────────────────────────────┐
│ HEAP ANALYSIS RESULT                                           │
├───────────────────────────────────────────────────────────────┤
│ 1 APPLICATION LEAKS                                            │
│                                                                │
│ Displaying only 1 leak trace out of 1 with the same signature │
│ Signature: 7c4f2a8b3d5e6f9a                                    │
│ ┌──────────────────────────────────────────────────────────┐ │
│ │ LEAKING: MainActivity                                      │ │
│ │ Leak Reason: Handler holds reference to Activity           │ │
│ │ Retaining 2.4 MB in 1542 objects                           │ │
│ │ GC Root: Main thread MessageQueue                          │ │
│ │                                                             │ │
│ │ References:                                                 │ │
│ │   MessageQueue.mMessages                                   │ │
│ │   ↓ Message.target                                         │ │
│ │   ↓ MainActivity$handler$1.this$0                          │ │
│ │   ↓ MainActivity (LEAKING)                                 │ │
│ └──────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

### Решение 1: static class + WeakReference

```kotlin
// ПРАВИЛЬНО: static Handler + WeakReference
class MainActivity : AppCompatActivity() {

    private lateinit var handler: MyHandler

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        handler = MyHandler(this)
        handler.sendEmptyMessageDelayed(MSG_UPDATE, 10 * 60 * 1000)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Очищаем все pending сообщения
        handler.removeCallbacksAndMessages(null)
    }

    fun updateUI(value: Int) {
        // UI обновление
    }

    // Static class НЕ имеет implicit reference на outer class
    private class MyHandler(activity: MainActivity) : Handler(Looper.getMainLooper()) {
        // WeakReference позволяет GC собрать Activity
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            // Получаем Activity через WeakReference
            val activity = activityRef.get()

            if (activity == null) {
                // Activity была уничтожена — игнорируем сообщение
                return
            }

            when (msg.what) {
                MSG_UPDATE -> activity.updateUI(msg.arg1)
            }
        }
    }

    companion object {
        private const val MSG_UPDATE = 1
    }
}
```

**Как работает WeakReference:**

```kotlin
// Strong reference — предотвращает GC
val strongRef: MainActivity = MainActivity()
// GC НЕ может собрать MainActivity, пока существует strongRef

// Weak reference — НЕ предотвращает GC
val weakRef = WeakReference(MainActivity())
// GC МОЖЕТ собрать MainActivity, даже если существует weakRef

// Проверка существования
val activity = weakRef.get()
if (activity != null) {
    // Activity всё ещё жива
    activity.updateUI()
} else {
    // Activity была собрана GC
    // Игнорируем сообщение
}
```

**Структура ссылок с WeakReference:**

```
┌─────────────────────────────────────────────────────────┐
│ MessageQueue                                             │
│  Message                                                 │
│    ├── target ──────────────────┐                        │
└────┼────────────────────────────┼────────────────────────┘
     │                            │
     ▼                            │
┌─────────────────────────────────┼────────────────────────┐
│ MyHandler (static class)        │                         │
│    ├── activityRef (WeakReference) ─┐                     │
└────┼────────────────────────────┼───┼────────────────────┘
     │                            │   │ (weak reference)
     │                            │   │
     │                            │   ▼
┌────┼────────────────────────────┼───────────────────────┐
│    │ MainActivity               │                        │
│    │   ├── Views                                         │
│    │   └── Resources                                     │
│    │                                                     │
│    │ НЕТ strong reference от Handler → GC может собрать! │
└─────────────────────────────────────────────────────────┘
```

### Решение 2: removeCallbacksAndMessages(null) в onDestroy

```kotlin
// ПРАВИЛЬНО: очистка в onDestroy
class MainActivity : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        handler.postDelayed({
            updateUI()
        }, 10 * 60 * 1000)
    }

    override fun onDestroy() {
        super.onDestroy()

        // КРИТИЧЕСКИ ВАЖНО: удаляем ВСЕ pending сообщения и callbacks
        handler.removeCallbacksAndMessages(null)

        // Теперь Handler не держит ссылок на Activity
    }

    private fun updateUI() {
        // UI обновление
    }
}
```

**Что делает removeCallbacksAndMessages(null):**

```java
// android/os/Handler.java
public final void removeCallbacksAndMessages(@Nullable Object token) {
    mQueue.removeCallbacksAndMessages(this, token);
}

// android/os/MessageQueue.java
void removeCallbacksAndMessages(Handler h, Object object) {
    if (h == null) {
        return;
    }

    synchronized (this) {
        Message p = mMessages;

        // Удаляем из головы списка
        while (p != null && p.target == h
               && (object == null || p.obj == object)) {
            Message n = p.next;
            mMessages = n;
            p.recycleUnchecked();
            p = n;
        }

        // Удаляем из середины/хвоста
        while (p != null) {
            Message n = p.next;
            if (n != null) {
                if (n.target == h
                    && (object == null || n.obj == object)) {
                    Message nn = n.next;
                    n.recycleUnchecked();
                    p.next = nn;
                    continue;
                }
            }
            p = n;
        }
    }
}
```

**Параметр token:**

```kotlin
// Удаление по token для селективной очистки
val animationToken = "animation"
handler.postDelayed({ animate() }, animationToken, 1000)

// В onPause: останавливаем только анимации
override fun onPause() {
    super.onPause()
    handler.removeCallbacksAndMessages(animationToken)
}

// В onDestroy: удаляем ВСЁ
override fun onDestroy() {
    super.onDestroy()
    handler.removeCallbacksAndMessages(null) // null = удалить всё
}
```

### Сравнение подходов

| Подход | Плюсы | Минусы | Когда использовать |
|--------|-------|--------|-------------------|
| **Static + WeakReference** | Безопасно даже если забыли очистить | Больше boilerplate кода | Legacy код, сложная логика Handler |
| **removeCallbacksAndMessages()** | Проще код | Нужно помнить вызывать в lifecycle | Современный код с чёткими lifecycle |
| **Оба подхода** | Максимальная безопасность | Избыточность | Критичные приложения |

### Лучшие практики

```kotlin
// РЕКОМЕНДУЕМЫЙ ПОДХОД для современного кода
class MainActivity : AppCompatActivity() {

    private val mainHandler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Используем lambda вместо anonymous class
        mainHandler.postDelayed({
            if (!isDestroyed && !isFinishing) {
                updateUI()
            }
        }, 5000)
    }

    override fun onDestroy() {
        super.onDestroy()

        // ВСЕГДА очищаем в onDestroy
        mainHandler.removeCallbacksAndMessages(null)
    }
}

// Для ViewModel — используйте Coroutines вместо Handler
class MyViewModel : ViewModel() {

    fun scheduleUpdate() {
        viewModelScope.launch {
            delay(5000)
            updateData()
        }
        // Автоматическая отмена при onCleared()
    }
}
```

### Обнаружение утечек — LeakCanary

```kotlin
// build.gradle.kts
dependencies {
    debugImplementation("com.squareup.leakcanary:leakcanary-android:2.12")
}

// LeakCanary автоматически обнаружит утечки Handler
// При обнаружении покажет notification и детальный анализ
```

**Пример отчёта LeakCanary:**

```
====================================
HEAP ANALYSIS RESULT
====================================
1 APPLICATION LEAK

References underlined with "~~~" are likely causes.
Learn more at https://squ.re/leaks.

Signature: 7c4f2a8b3d5e6f9a
┬───
│ GC Root: Main thread
│
├─ android.os.MessageQueue instance
│    Leaking: NO (Main thread MessageQueue)
│    ↓ MessageQueue.mMessages
│                   ~~~~~~~~~
├─ android.os.Message instance
│    Leaking: UNKNOWN
│    Message.what = 1
│    Message.when = 123456789
│    ↓ Message.target
│               ~~~~~~
├─ com.example.MainActivity$handler$1 instance
│    Leaking: UNKNOWN
│    Anonymous subclass of android.os.Handler
│    ↓ MainActivity$handler$1.this$0
│                              ~~~~~~
╰→ com.example.MainActivity instance
     Leaking: YES (Activity#mDestroyed is true)
     Retaining 2.4 MB in 1542 objects

     Activity lifecycle:
       onCreate: true
       onStart: true
       onResume: true
       onPause: true
       onStop: true
       onDestroy: true
       mDestroyed: true

====================================
ANALYSIS RESULT
====================================
1 retained object, 2.4 MB retained

Build failed: com.example.MainActivity retained after destroy
====================================
```

## Современные альтернативы

Handler всё ещё используется в Android framework, но для application кода рекомендуются современные альтернативы.

### Handler → Coroutines mapping

```kotlin
// СТАРЫЙ ПОДХОД: Handler
class OldViewModel {
    private val handler = Handler(Looper.getMainLooper())

    fun loadData() {
        // Background работа
        Thread {
            val data = fetchFromNetwork()

            // Переключение на Main Thread
            handler.post {
                updateUI(data)
            }
        }.start()
    }

    fun scheduleUpdate() {
        handler.postDelayed({
            performUpdate()
        }, 5000)
    }

    fun cleanup() {
        handler.removeCallbacksAndMessages(null)
    }
}

// СОВРЕМЕННЫЙ ПОДХОД: Coroutines
class ModernViewModel : ViewModel() {

    fun loadData() {
        viewModelScope.launch {
            // withContext автоматически переключает dispatcher
            val data = withContext(Dispatchers.IO) {
                fetchFromNetwork()
            }

            // Автоматически на Main после withContext
            updateUI(data)
        }
    }

    fun scheduleUpdate() {
        viewModelScope.launch {
            delay(5000)
            performUpdate()
        }
    }

    // Автоматическая очистка при onCleared()
    // Не нужен cleanup()
}
```

### withContext(Dispatchers.Main) вместо Handler.post()

```kotlin
// Handler: переключение между потоками
class HandlerExample {
    private val mainHandler = Handler(Looper.getMainLooper())

    fun performOperation() {
        Thread {
            // Background работа
            val result = heavyComputation()

            // Переключение на Main Thread
            mainHandler.post {
                textView.text = result
            }
        }.start()
    }
}

// Coroutines: более читаемый код
class CoroutinesExample {

    fun performOperation() = lifecycleScope.launch {
        // Background работа
        val result = withContext(Dispatchers.Default) {
            heavyComputation()
        }

        // Автоматически на Main Thread после withContext
        textView.text = result
    }
}

// Множественные переключения контекста
suspend fun complexOperation() {
    // Main Thread
    showLoading()

    // IO Thread
    val data = withContext(Dispatchers.IO) {
        fetchData()
    }

    // Default Thread (CPU-intensive)
    val processed = withContext(Dispatchers.Default) {
        processData(data)
    }

    // Main Thread
    hideLoading()
    displayResult(processed)
}
```

### delay() вместо postDelayed()

```kotlin
// Handler: отложенное выполнение
class HandlerDelayExample {
    private val handler = Handler(Looper.getMainLooper())
    private var currentRunnable: Runnable? = null

    fun scheduleAction() {
        currentRunnable = Runnable {
            performAction()
        }
        handler.postDelayed(currentRunnable!!, 5000)
    }

    fun cancel() {
        currentRunnable?.let { handler.removeCallbacks(it) }
    }

    fun cleanup() {
        handler.removeCallbacksAndMessages(null)
    }
}

// Coroutines: проще и безопаснее
class CoroutinesDelayExample {
    private var currentJob: Job? = null

    fun scheduleAction() {
        currentJob = lifecycleScope.launch {
            delay(5000)
            performAction()
        }
    }

    fun cancel() {
        currentJob?.cancel()
    }

    // Автоматическая очистка при lifecycle destroy
}

// Повторяющиеся задачи
// Handler: требует ручного management
class HandlerRepeatingTask {
    private val handler = Handler(Looper.getMainLooper())
    private val updateInterval = 1000L

    private val updateRunnable = object : Runnable {
        override fun run() {
            updateUI()
            handler.postDelayed(this, updateInterval)
        }
    }

    fun start() {
        handler.post(updateRunnable)
    }

    fun stop() {
        handler.removeCallbacks(updateRunnable)
    }
}

// Coroutines: встроенная поддержка
class CoroutinesRepeatingTask {
    private var updateJob: Job? = null

    fun start() {
        updateJob = lifecycleScope.launch {
            while (isActive) {
                updateUI()
                delay(1000)
            }
        }
    }

    fun stop() {
        updateJob?.cancel()
    }
}
```

### Когда Handler ещё актуален

Несмотря на Coroutines, Handler остаётся актуальным в некоторых случаях:

#### 1. Работа с Android Framework API

```kotlin
// Многие framework API требуют Handler
class CameraManager {
    private val cameraHandler = Handler(cameraThread.looper)

    fun openCamera() {
        cameraManager.openCamera(
            cameraId,
            cameraStateCallback,
            cameraHandler // Handler для camera callbacks
        )
    }
}

// SurfaceTexture требует Handler
surfaceTexture.setOnFrameAvailableListener(
    { /* callback */ },
    handler // Handler для frame callbacks
)
```

#### 2. Точное timing и sync

```kotlin
// Handler использует SystemClock.uptimeMillis() для точного timing
class AnimationController {
    private val handler = Handler(Looper.getMainLooper())

    fun startAnimation() {
        val startTime = SystemClock.uptimeMillis()

        handler.postAtTime({
            val elapsed = SystemClock.uptimeMillis() - startTime
            updateAnimation(elapsed)
        }, startTime + 16) // Точно через 16ms (60 FPS)
    }
}

// Coroutines delay() менее точен для sub-millisecond timing
```

#### 3. MessageQueue hooks

```kotlin
// IdleHandler — выполнение когда MessageQueue idle
class IdleTaskScheduler {

    fun scheduleIdleTask() {
        Looper.myQueue().addIdleHandler {
            // Выполняется когда Main Thread простаивает
            performBackgroundTask()
            false // false = one-time, true = повторяющийся
        }
    }
}

// Полезно для:
// - Preloading данных
// - Deferred initialization
// - Background cleanup
```

#### 4. Legacy код и библиотеки

```kotlin
// Многие legacy библиотеки используют Handler
class LegacyLibraryWrapper {
    private val handler = Handler(Looper.getMainLooper())

    fun initLegacyLibrary() {
        LegacyLib.setCallback(object : LegacyCallback {
            override fun onResult(data: Data) {
                // Legacy callback на background thread
                // Переключаемся на Main
                handler.post {
                    updateUI(data)
                }
            }
        })
    }
}
```

#### 5. Sync barriers для высокоприоритетных задач

```kotlin
// Sync barriers используются внутри View system
// Для приоритизации UI обновлений
class ViewRootImpl {

    fun scheduleTraversals() {
        if (!mTraversalScheduled) {
            mTraversalScheduled = true

            // Устанавливаем sync barrier
            mTraversalBarrier = mHandler.looper.queue.postSyncBarrier()

            // Отправляем async message (обходит barrier)
            mChoreographer.postCallback(
                Choreographer.CALLBACK_TRAVERSAL,
                mTraversalRunnable,
                null
            )
        }
    }
}

// Не доступно в Coroutines
```

### Миграция Handler → Coroutines

```kotlin
// BEFORE: Handler-based networking
class OldNetworkManager {
    private val handler = Handler(Looper.getMainLooper())

    interface Callback {
        fun onSuccess(data: Data)
        fun onError(error: Throwable)
    }

    fun fetchData(callback: Callback) {
        Thread {
            try {
                val data = api.getData()
                handler.post {
                    callback.onSuccess(data)
                }
            } catch (e: Exception) {
                handler.post {
                    callback.onError(e)
                }
            }
        }.start()
    }
}

// Usage
oldNetworkManager.fetchData(object : Callback {
    override fun onSuccess(data: Data) {
        updateUI(data)
    }

    override fun onError(error: Throwable) {
        showError(error)
    }
})

// AFTER: Coroutines-based networking
class ModernNetworkManager {

    suspend fun fetchData(): Result<Data> = withContext(Dispatchers.IO) {
        try {
            Result.success(api.getData())
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}

// Usage
lifecycleScope.launch {
    when (val result = modernNetworkManager.fetchData()) {
        is Result.Success -> updateUI(result.data)
        is Result.Failure -> showError(result.error)
    }
}
```

## Код примеры

### Создание Handler в Activity (правильно и неправильно)

```kotlin
// ❌ НЕПРАВИЛЬНО: Anonymous inner class
class BadActivity : AppCompatActivity() {

    // УТЕЧКА ПАМЯТИ: implicit reference к Activity
    private val handler = object : Handler(Looper.getMainLooper()) {
        override fun handleMessage(msg: Message) {
            updateUI(msg.arg1)
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Отложенное сообщение держит Activity в памяти
        handler.sendEmptyMessageDelayed(1, 60_000)
    }
}

// ❌ НЕПРАВИЛЬНО: Lambda с долгим lifecycle
class BadActivity2 : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Lambda захватывает this (Activity)
        handler.postDelayed({
            textView.text = "Updated" // this.textView
        }, 60_000)
    }
}

// ✅ ПРАВИЛЬНО: Static Handler + WeakReference
class GoodActivity : AppCompatActivity() {

    private lateinit var handler: MyHandler

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        handler = MyHandler(this)
        handler.sendEmptyMessageDelayed(MSG_UPDATE, 60_000)
    }

    override fun onDestroy() {
        super.onDestroy()
        handler.removeCallbacksAndMessages(null)
    }

    fun updateUI(value: Int) {
        findViewById<TextView>(R.id.textView).text = "Value: $value"
    }

    private class MyHandler(activity: GoodActivity) : Handler(Looper.getMainLooper()) {
        private val activityRef = WeakReference(activity)

        override fun handleMessage(msg: Message) {
            val activity = activityRef.get() ?: return

            when (msg.what) {
                MSG_UPDATE -> activity.updateUI(msg.arg1)
            }
        }
    }

    companion object {
        private const val MSG_UPDATE = 1
    }
}

// ✅ ПРАВИЛЬНО: Простой Handler с очисткой
class GoodActivity2 : AppCompatActivity() {

    private val handler = Handler(Looper.getMainLooper())

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        handler.postDelayed({
            if (!isDestroyed && !isFinishing) {
                updateUI()
            }
        }, 5000)
    }

    override fun onDestroy() {
        super.onDestroy()
        // КРИТИЧЕСКИ ВАЖНО
        handler.removeCallbacksAndMessages(null)
    }

    private fun updateUI() {
        findViewById<TextView>(R.id.textView).text = "Updated"
    }
}

// ✅ ЛУЧШЕ: Используйте Coroutines для нового кода
class BestActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        lifecycleScope.launch {
            delay(5000)
            if (lifecycle.currentState.isAtLeast(Lifecycle.State.STARTED)) {
                updateUI()
            }
        }
    }

    private fun updateUI() {
        findViewById<TextView>(R.id.textView).text = "Updated"
    }
}
```

### HandlerThread для background работы

```kotlin
// Пример: Background обработка изображений
class ImageProcessor {

    private val processingThread = HandlerThread(
        "ImageProcessing",
        Process.THREAD_PRIORITY_BACKGROUND
    ).apply { start() }

    private val processingHandler = Handler(processingThread.looper)
    private val mainHandler = Handler(Looper.getMainLooper())

    fun processImage(bitmap: Bitmap, callback: (Bitmap) -> Unit) {
        processingHandler.post {
            // Тяжёлая обработка на background потоке
            val processed = applyFilters(bitmap)

            // Возврат результата на Main Thread
            mainHandler.post {
                callback(processed)
            }
        }
    }

    fun processImages(bitmaps: List<Bitmap>, callback: (List<Bitmap>) -> Unit) {
        processingHandler.post {
            val results = mutableListOf<Bitmap>()

            // Последовательная обработка на background
            for (bitmap in bitmaps) {
                results.add(applyFilters(bitmap))
            }

            mainHandler.post {
                callback(results)
            }
        }
    }

    private fun applyFilters(bitmap: Bitmap): Bitmap {
        // Симуляция тяжёлой обработки
        Thread.sleep(100)

        // Применение фильтров
        return bitmap.copy(Bitmap.Config.ARGB_8888, true).apply {
            // Обработка пикселей...
        }
    }

    fun shutdown() {
        processingThread.quitSafely()

        try {
            processingThread.join(5000)
        } catch (e: InterruptedException) {
            processingThread.interrupt()
        }
    }
}

// Использование
class MainActivity : AppCompatActivity() {

    private lateinit var imageProcessor: ImageProcessor

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        imageProcessor = ImageProcessor()

        val bitmap = BitmapFactory.decodeResource(resources, R.drawable.photo)

        imageProcessor.processImage(bitmap) { processed ->
            imageView.setImageBitmap(processed)
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        imageProcessor.shutdown()
    }
}

// Современная альтернатива: Coroutines + Dispatchers.Default
class ModernImageProcessor {

    suspend fun processImage(bitmap: Bitmap): Bitmap = withContext(Dispatchers.Default) {
        applyFilters(bitmap)
    }

    suspend fun processImages(bitmaps: List<Bitmap>): List<Bitmap> =
        withContext(Dispatchers.Default) {
            bitmaps.map { applyFilters(it) }
        }

    private fun applyFilters(bitmap: Bitmap): Bitmap {
        Thread.sleep(100)
        return bitmap.copy(Bitmap.Config.ARGB_8888, true)
    }
}

// Использование
lifecycleScope.launch {
    val bitmap = BitmapFactory.decodeResource(resources, R.drawable.photo)
    val processed = modernImageProcessor.processImage(bitmap)
    imageView.setImageBitmap(processed)
}
```

### Коммуникация между потоками через Handler

```kotlin
// Пример: Worker поток отправляет progress updates на Main Thread
class DownloadManager {

    // Handler для Main Thread (UI updates)
    private val mainHandler = Handler(Looper.getMainLooper())

    // Background HandlerThread для download операций
    private val downloadThread = HandlerThread("DownloadThread").apply { start() }
    private val downloadHandler = Handler(downloadThread.looper)

    interface DownloadCallback {
        fun onProgress(progress: Int, total: Int)
        fun onComplete(file: File)
        fun onError(error: Exception)
    }

    fun downloadFile(url: String, callback: DownloadCallback) {
        // Отправляем задачу на background поток
        downloadHandler.post {
            performDownload(url, callback)
        }
    }

    private fun performDownload(url: String, callback: DownloadCallback) {
        try {
            val connection = URL(url).openConnection() as HttpURLConnection
            val totalBytes = connection.contentLength
            var downloadedBytes = 0

            val buffer = ByteArray(8192)
            val inputStream = connection.inputStream
            val outputFile = File(getDownloadPath(), "download.bin")
            val outputStream = FileOutputStream(outputFile)

            var bytesRead: Int
            while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                outputStream.write(buffer, 0, bytesRead)
                downloadedBytes += bytesRead

                // Progress update на Main Thread
                val progress = downloadedBytes
                val total = totalBytes
                mainHandler.post {
                    callback.onProgress(progress, total)
                }
            }

            outputStream.close()
            inputStream.close()

            // Completion на Main Thread
            mainHandler.post {
                callback.onComplete(outputFile)
            }

        } catch (e: Exception) {
            // Error на Main Thread
            mainHandler.post {
                callback.onError(e)
            }
        }
    }

    fun shutdown() {
        downloadThread.quitSafely()
    }

    private fun getDownloadPath(): File {
        // Реализация...
        return File("/tmp")
    }
}

// Использование
class DownloadActivity : AppCompatActivity() {

    private lateinit var downloadManager: DownloadManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_download)

        downloadManager = DownloadManager()

        startDownloadButton.setOnClickListener {
            downloadManager.downloadFile(fileUrl, object : DownloadCallback {
                override fun onProgress(progress: Int, total: Int) {
                    // На Main Thread — безопасно обновлять UI
                    val percent = (progress * 100L / total).toInt()
                    progressBar.progress = percent
                    progressText.text = "$percent%"
                }

                override fun onComplete(file: File) {
                    // На Main Thread
                    showToast("Download complete: ${file.name}")
                }

                override fun onError(error: Exception) {
                    // На Main Thread
                    showToast("Download failed: ${error.message}")
                }
            })
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        downloadManager.shutdown()
    }
}

// Современная альтернатива: Flow для progress updates
class ModernDownloadManager {

    fun downloadFile(url: String): Flow<DownloadState> = flow {
        emit(DownloadState.Progress(0, 0))

        try {
            val connection = URL(url).openConnection() as HttpURLConnection
            val totalBytes = connection.contentLength
            var downloadedBytes = 0

            val buffer = ByteArray(8192)
            val inputStream = connection.inputStream
            val outputFile = File(getDownloadPath(), "download.bin")
            val outputStream = FileOutputStream(outputFile)

            var bytesRead: Int
            while (inputStream.read(buffer).also { bytesRead = it } != -1) {
                outputStream.write(buffer, 0, bytesRead)
                downloadedBytes += bytesRead

                // Emit progress
                emit(DownloadState.Progress(downloadedBytes, totalBytes))
            }

            outputStream.close()
            inputStream.close()

            emit(DownloadState.Complete(outputFile))

        } catch (e: Exception) {
            emit(DownloadState.Error(e))
        }
    }.flowOn(Dispatchers.IO) // Выполнение на IO dispatcher

    private fun getDownloadPath(): File = File("/tmp")
}

sealed class DownloadState {
    data class Progress(val downloaded: Int, val total: Int) : DownloadState()
    data class Complete(val file: File) : DownloadState()
    data class Error(val exception: Exception) : DownloadState()
}

// Использование
lifecycleScope.launch {
    modernDownloadManager.downloadFile(fileUrl)
        .collect { state ->
            // Автоматически на Main Thread
            when (state) {
                is DownloadState.Progress -> {
                    val percent = (state.downloaded * 100L / state.total).toInt()
                    progressBar.progress = percent
                    progressText.text = "$percent%"
                }
                is DownloadState.Complete -> {
                    showToast("Download complete: ${state.file.name}")
                }
                is DownloadState.Error -> {
                    showToast("Download failed: ${state.exception.message}")
                }
            }
        }
}
```

## Проверь себя

### Вопрос 1: Почему Handler должен быть static?

**Ответ:**

Non-static inner class в Java/Kotlin имеет неявную (implicit) ссылку на экземпляр внешнего класса через поле `this$0`. Когда Handler является inner class Activity:

```kotlin
class Activity {
    private val handler = object : Handler() {
        // Компилятор добавляет:
        // private final Activity this$0;

        override fun handleMessage(msg: Message) {
            // Доступ к Activity через this$0
            this@Activity.updateUI()
        }
    }
}
```

Проблема возникает когда:

1. Handler отправляет отложенное сообщение (например, на 10 минут)
2. Message добавляется в MessageQueue с reference на Handler (msg.target)
3. Handler держит reference на Activity через `this$0`
4. Пользователь закрывает Activity
5. Activity не может быть собрана GC, пока Message в очереди
6. Утечка памяти: вся Activity со всеми View, Bitmap, Resources остаётся в памяти

**Решение:** static Handler не имеет implicit reference, поэтому используем WeakReference для доступа к Activity:

```kotlin
private class MyHandler(activity: Activity) : Handler(Looper.getMainLooper()) {
    private val weakRef = WeakReference(activity)

    override fun handleMessage(msg: Message) {
        weakRef.get()?.updateUI() ?: return // Activity может быть null
    }
}
```

### Вопрос 2: Что произойдёт если не вызвать Looper.prepare()?

**Ответ:**

Если попытаться создать Handler на потоке без Looper, получим RuntimeException:

```kotlin
Thread {
    // НЕТ Looper.prepare()

    try {
        val handler = Handler() // RuntimeException!
    } catch (e: RuntimeException) {
        // "Can't create handler inside thread Thread[Thread-2,5,main]
        //  that has not called Looper.prepare()"
    }
}.start()
```

**Причина:** Handler требует Looper для работы:

```java
// android/os/Handler.java
public Handler() {
    this(null, false);
}

public Handler(@Nullable Callback callback, boolean async) {
    // ...

    mLooper = Looper.myLooper(); // Получаем Looper текущего потока
    if (mLooper == null) {
        throw new RuntimeException(
            "Can't create handler inside thread " + Thread.currentThread()
                    + " that has not called Looper.prepare()");
    }
    mQueue = mLooper.mQueue;
    // ...
}
```

**Правильное использование:**

```kotlin
class WorkerThread : Thread() {
    lateinit var handler: Handler

    override fun run() {
        // 1. Создаём Looper для этого потока
        Looper.prepare()

        // 2. Теперь можем создать Handler
        handler = Handler(Looper.myLooper()!!)

        // 3. Запускаем цикл обработки сообщений
        Looper.loop()

        // Код после loop() не выполнится (loop бесконечен)
    }
}

// Или проще — используйте HandlerThread
val handlerThread = HandlerThread("Worker")
handlerThread.start()
val handler = Handler(handlerThread.looper) // Looper уже готов
```

**Main Thread:** Looper уже создан в `ActivityThread.main()`, поэтому Handler можно создавать сразу:

```kotlin
class Activity {
    // OK: Main Thread уже имеет Looper
    private val handler = Handler(Looper.getMainLooper())
}
```

### Вопрос 3: Как postDelayed() работает под капотом?

**Ответ:**

`postDelayed()` не использует Timer или ScheduledExecutor. Вместо этого:

**Шаг 1: Преобразование delay в absolute time**

```kotlin
handler.postDelayed(runnable, 5000)

// Под капотом:
public final boolean postDelayed(Runnable r, long delayMillis) {
    return sendMessageDelayed(getPostMessage(r), delayMillis);
}

public final boolean sendMessageDelayed(Message msg, long delayMillis) {
    if (delayMillis < 0) delayMillis = 0;

    // Преобразование относительного времени в абсолютное
    return sendMessageAtTime(msg, SystemClock.uptimeMillis() + delayMillis);
}
```

**Шаг 2: Вставка в sorted MessageQueue**

```kotlin
public boolean sendMessageAtTime(Message msg, long uptimeMillis) {
    MessageQueue queue = mQueue;
    return enqueueMessage(queue, msg, uptimeMillis); // when = uptimeMillis
}

// MessageQueue.enqueueMessage
boolean enqueueMessage(Message msg, long when) {
    msg.when = when;

    Message p = mMessages; // Голова списка

    // Вставка в отсортированную позицию по when
    if (p == null || when == 0 || when < p.when) {
        // Вставляем в голову
        msg.next = p;
        mMessages = msg;
        needWake = mBlocked;
    } else {
        // Ищем позицию для вставки
        Message prev;
        for (;;) {
            prev = p;
            p = p.next;
            if (p == null || when < p.when) {
                break;
            }
        }
        msg.next = p;
        prev.next = msg;
    }

    if (needWake) {
        nativeWake(mPtr); // Будим поток, если нужно
    }
}
```

**Шаг 3: Looper ждёт с timeout**

```kotlin
// MessageQueue.next()
Message next() {
    for (;;) {
        // Вычисляем timeout до следующего сообщения
        if (msg != null) {
            if (now < msg.when) {
                // Сообщение ещё не готово
                nextPollTimeoutMillis = (int) Math.min(msg.when - now, Integer.MAX_VALUE);
            } else {
                // Сообщение готово — возвращаем
                return msg;
            }
        }

        // Ждём с timeout на native уровне (epoll)
        nativePollOnce(ptr, nextPollTimeoutMillis);
    }
}
```

**Шаг 4: epoll_wait с timeout**

```cpp
// Native уровень
int pollOnce(int timeoutMillis) {
    // ...
    int result = epoll_wait(mEpollFd, eventItems, EPOLL_MAX_EVENTS, timeoutMillis);
    // ...
}
```

**Диаграмма:**

```
Time: 0ms              5000ms              10000ms
      │                 │                   │
      ▼                 ▼                   ▼
postDelayed(A, 5000)   Execute A          postDelayed(B, 10000)
      │
      ├─> Message.when = now + 5000 = 5000ms
      │
      └─> enqueueMessage() → insert sorted by when

MessageQueue: [A(5000)]

Looper.loop():
  - queue.next() blocks
  - nativePollOnce(timeout = 5000ms)
  - epoll_wait(5000) — поток спит 5 секунд
  - timeout истёк → epoll_wait returns
  - queue.next() returns Message A
  - dispatch to Handler
  - A.run() executed

MessageQueue: []

postDelayed(B, 10000):
  - Message.when = 15000ms (5000 + 10000)
  - enqueueMessage() → [B(15000)]
  - nativePollOnce(timeout = 10000ms)
  - epoll_wait(10000) — спит 10 секунд
  - ...
```

**Ключевые моменты:**

1. **Нет активного ожидания**: поток спит на уровне ядра (epoll_wait)
2. **Sorted insertion**: сообщения упорядочены по времени выполнения
3. **Dynamic timeout**: timeout пересчитывается для следующего сообщения
4. **Efficient wake-up**: если новое сообщение должно выполниться раньше, поток просыпается

### Вопрос 4: Зачем нужен Message.obtain()?

**Ответ:**

`Message.obtain()` реализует **object pooling pattern** для оптимизации производительности и снижения нагрузки на Garbage Collector.

**Проблема без pooling:**

```kotlin
// Создание через конструктор
for (i in 1..1000) {
    val msg = Message() // 1000 аллокаций
    msg.what = i
    handler.sendMessage(msg)
}

// Результат:
// - 1000 новых объектов в heap
// - После обработки — 1000 объектов для GC
// - GC паузы, особенно на старых устройствах
```

**Решение с pooling:**

```kotlin
// Использование pool
for (i in 1..1000) {
    val msg = Message.obtain() // Переиспользование из pool
    msg.what = i
    handler.sendMessage(msg)
}

// Результат:
// - ~50 объектов в pool (MAX_POOL_SIZE)
// - Переиспользование после recycle()
// - Минимальная нагрузка на GC
```

**Как работает pool:**

```java
public final class Message {
    // Пул объектов (linked list)
    private static Message sPool;
    private static int sPoolSize = 0;
    private static final int MAX_POOL_SIZE = 50;

    // Следующий Message в pool
    Message next;

    public static Message obtain() {
        synchronized (sPoolSync) {
            if (sPool != null) {
                // Извлекаем из pool
                Message m = sPool;
                sPool = m.next;
                m.next = null;
                sPoolSize--;
                return m; // ПЕРЕИСПОЛЬЗУЕМ существующий объект
            }
        }
        return new Message(); // Pool пуст — создаём новый
    }

    void recycleUnchecked() {
        // Очистка полей
        what = 0;
        arg1 = 0;
        arg2 = 0;
        obj = null;
        // ...

        synchronized (sPoolSync) {
            if (sPoolSize < MAX_POOL_SIZE) {
                // Возвращаем в pool
                next = sPool;
                sPool = this;
                sPoolSize++;
            }
        }
    }
}
```

**Lifecycle Message:**

```
1. Message.obtain() → извлекается из pool (или создаётся новый)
   ↓
2. Заполнение данными (what, arg1, obj, ...)
   ↓
3. handler.sendMessage(msg) → добавление в MessageQueue
   ↓
4. Looper обрабатывает → msg.target.dispatchMessage(msg)
   ↓
5. msg.recycle() → очистка и возврат в pool
   ↓
6. Message в pool готов к переиспользованию
```

**Производительность:**

```kotlin
// Benchmark: 10000 сообщений

// Без pooling (new Message())
// Время: 45ms
// GC collections: 3
// Память: 640KB allocated

// С pooling (Message.obtain())
// Время: 12ms
// GC collections: 0
// Память: 32KB allocated (только pool)

// Выигрыш: 3.75x быстрее, 20x меньше аллокаций
```

**Все варианты obtain():**

```kotlin
// Пустой Message
val msg1 = Message.obtain()

// С target Handler
val msg2 = Message.obtain(handler)

// С target + Runnable
val msg3 = Message.obtain(handler, runnable)

// С target + what
val msg4 = Message.obtain(handler, MSG_UPDATE)

// С target + what + obj
val msg5 = Message.obtain(handler, MSG_UPDATE, data)

// С target + what + args
val msg6 = Message.obtain(handler, MSG_UPDATE, arg1, arg2)

// С target + what + args + obj
val msg7 = Message.obtain(handler, MSG_UPDATE, arg1, arg2, data)

// Копирование из существующего
val msg8 = Message.obtain(existingMessage)
```

**Best practice:**

```kotlin
// ВСЕГДА используйте obtain()
val msg = Message.obtain(handler, MSG_UPDATE, progress, total)
handler.sendMessage(msg)

// НИКОГДА не создавайте через конструктор
val msg = Message() // ❌ Плохо для производительности
```

## Связи

### [[os-processes-threads]]
Handler/Looper основаны на thread-local storage и блокирующих операциях на уровне ОС. Понимание потоков помогает понять:
- Почему Looper.prepare() использует ThreadLocal
- Как epoll блокирует поток без CPU overhead
- Разницу между user-space и kernel-space блокировками
- Thread scheduling и priority (Process.THREAD_PRIORITY_*)

### [[android-threading]]
Handler/Looper — это низкоуровневый примитив, на котором построены все threading механизмы Android:
- AsyncTask использует Handler для publishProgress() и onPostExecute()
- IntentService построен на HandlerThread
- Lifecycle callbacks обрабатываются через Handler
- View.post() использует Handler внутри

### [[android-async-evolution]]
Эволюция асинхронного программирования в Android:
- **2008-2010**: Handler/AsyncTask — единственные опции
- **2011-2014**: Loader, IntentService, Service + Handler
- **2015-2017**: RxJava становится популярным
- **2018-2025**: Kotlin Coroutines — современный стандарт

Handler остаётся актуальным для:
- Legacy кода и миграции
- Framework API требующих Handler
- Понимания внутреннего устройства Android
- Специфичных use cases (timing, IdleHandler, sync barriers)

---

## Заключение

Handler, Looper и MessageQueue — это фундаментальный механизм Android, который:

1. **Обеспечивает работу Main Thread** через event loop
2. **Позволяет безопасную коммуникацию** между потоками
3. **Оптимизирован на всех уровнях** от Java до Linux kernel (epoll)
4. **Требует осторожности** для предотвращения memory leaks
5. **Активно используется в framework** даже если скрыт от разработчика

**Для современного кода:**
- Используйте **Kotlin Coroutines** вместо Handler для application логики
- Понимайте Handler для **работы с framework API**
- Знайте **anti-patterns** для code review и debugging
- Помните о **lifecycle management** и очистке ресурсов

**Ключевые принципы:**
- Один Looper на поток (ThreadLocal)
- Message очередь как sorted linked list
- epoll для эффективного ожидания
- Object pooling для производительности
- WeakReference для предотвращения утечек
- removeCallbacksAndMessages(null) в onDestroy()

Понимание этих концепций делает вас более эффективным Android разработчиком и помогает в отладке сложных проблем с производительностью и памятью.

---

## Связь с другими темами

**[[android-threading]]** — Handler, Looper и MessageQueue являются низкоуровневой реализацией threading в Android. Понимание threading модели (main thread, background threads, ANR) даёт контекст для изучения Handler/Looper. ThreadLocal<Looper> обеспечивает привязку одного Looper к одному потоку. Рекомендуется изучить threading fundamentals перед Handler/Looper.

**[[android-memory-leaks]]** — Handler является одним из главных источников memory leaks в Android. Анонимные inner class Handler-ы и non-static Runnable неявно держат ссылку на Activity, предотвращая GC. Паттерн WeakReference + static Handler и removeCallbacksAndMessages(null) в onDestroy() — стандартные решения. Рекомендуется изучать параллельно.

**[[os-processes-threads]]** — Каждый Thread в Android — это native OS thread (pthread на Linux). Looper использует epoll для эффективного ожидания сообщений, что напрямую связано с механизмами ядра Linux. Понимание OS-level потоков, context switching и stack memory объясняет стоимость создания HandlerThread и почему thread pools эффективнее.

**[[kotlin-coroutines]]** — Dispatchers.Main в Kotlin Coroutines реализован через Handler(Looper.getMainLooper()). Каждый dispatch на Main Dispatcher — это post Message в MessageQueue main thread. Понимание Handler/Looper объясняет разницу между Dispatchers.Main и Dispatchers.Main.immediate, а также помогает при отладке корутин.

---

## Источники и дальнейшее чтение

| # | Источник | Тип | Вклад |
|---|----------|-----|-------|
| 1 | [ProAndroidDev: Under the Hood - Loopers, Handlers and MessageQueue](https://proandroiddev.com/where-do-loopers-handlers-and-message-queue-come-from-and-how-do-they-help-in-communication-with-6eee4557fe55) | Статья | Внутреннее устройство |
| 2 | [Medium: Understanding Handler-Looper Mechanism](https://anmolsehgal.medium.com/android-handlers-loopers-messagequeue-basics-d56a750df2cc) | Статья | MessageQueue basics |
| 3 | [DeveloperMemos: Handling Deprecation of Handler()](https://developermemos.com/posts/handling-deprecation-of-handler-android/) | Статья | Deprecated patterns |
| 4 | [Medium: Top 7 Android Memory Leaks 2025](https://artemasoyan.medium.com/top-7-android-memory-leaks-and-how-to-avoid-them-in-2025-b77e15a7b62e) | Статья | Memory leak patterns |
| 5 | [Medium: Replacing Handlers with Coroutines](https://medium.com/@sandeepkella23/replacing-handlers-with-coroutines-in-android-a-comprehensive-guide-for-senior-developers-2bb07a8831cc) | Статья | Handler → Coroutines migration |
| 6 | [Android Developers: Threading Performance](https://developer.android.com/topic/performance/threads) | Документация | Best practices |
| 7 | [Medium: HandlerThreads and Why to Use Them](https://medium.com/@ali.muzaffar/handlerthreads-and-why-you-should-be-using-them-in-your-android-apps-dc8bf1540341) | Статья | HandlerThread usage |
| 8 | [GitHub: kotlinx.coroutines HandlerDispatcher.kt](https://github.com/Kotlin/kotlinx.coroutines/blob/master/ui/kotlinx-coroutines-android/src/HandlerDispatcher.kt) | Исходный код | Dispatchers.Main реализация |
| 9 | [Kotlin Blog: Dispatchers.Main vs Main.immediate](https://blog.shreyaspatil.dev/understanding-dispatchers-main-and-mainimmediate) | Статья | Performance optimization |
| 10 | [JetBrains: Kotlin Developer Survey 2024](https://www.jetbrains.com/lp/devecosystem-2024/kotlin/) | Исследование | Статистика использования |

### Книги

- **Goetz B. (2006)** *Java Concurrency in Practice* — фундаментальное описание producer-consumer паттерна, thread confinement и message passing, которые лежат в основе Handler/Looper/MessageQueue. Обязательное чтение для глубокого понимания.
- **Vasavada N. (2019)** *Android Internals* — детальное описание Looper, MessageQueue и native layer (epoll) на уровне AOSP. Объясняет связь между Java и C++ слоями MessageQueue.
- **Moskala M. (2022)** *Kotlin Coroutines: Deep Dive* — объясняет, как Dispatchers.Main использует Handler под капотом, и почему понимание Handler/Looper критично для отладки корутин.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
