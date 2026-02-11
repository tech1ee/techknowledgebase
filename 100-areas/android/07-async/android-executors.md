---
title: "Executors и ThreadPoolExecutor в Android"
created: 2025-12-22
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [thread-pool, task-scheduling, work-stealing, resource-pooling]
tags:
  - topic/android
  - topic/threading
  - topic/jvm
  - type/deep-dive
  - level/advanced
related:
  - "[[android-async-evolution]]"
  - "[[android-threading]]"
  - "[[os-processes-threads]]"
  - "[[os-scheduling]]"
prerequisites:
  - "[[android-threading]]"
  - "[[android-activity-lifecycle]]"
---

# Executors и ThreadPoolExecutor в Android

## Prerequisites

Перед изучением этого материала необходимо понимание следующих концепций:

- **os-processes-threads** — фундаментальное понимание того, как операционная система управляет потоками, переключение контекста, стоимость создания потоков
- **os-scheduling** — как OS scheduler распределяет CPU время между потоками, приоритеты потоков, time slicing
- **Базовые знания java.util.concurrent** — понимание проблем многопоточности (race conditions, visibility), понятие thread-safety

Без этой базы сложно понять, почему пулы потоков эффективнее создания новых потоков для каждой задачи, и как правильно настраивать параметры ThreadPoolExecutor.

## Обзор

Executors framework — это высокоуровневая абстракция над низкоуровневыми потоками Java, появившаяся в Java 5 как часть пакета `java.util.concurrent`. Вместо создания и управления потоками напрямую через `Thread`, Executors предоставляют удобный механизм для выполнения асинхронных задач с переиспользованием потоков.

В Android, хотя современная разработка всё больше движется в сторону Kotlin Coroutines, понимание Executors остаётся критически важным:
- Многие legacy проекты и библиотеки используют Executors
- Room, WorkManager, LiveData внутренне работают с Executors
- Для интеграции с Java-кодом без зависимости от Kotlin
- Для точного контроля над потоками в специфичных сценариях

## Терминология

### Executor
Простейший интерфейс с единственным методом:
```java
public interface Executor {
    void execute(Runnable command);
}
```

Это базовый контракт: "Возьми задачу и выполни её где-то, когда-то". Детали реализации скрыты.

### ExecutorService
Расширенный интерфейс, добавляющий lifecycle management и возможность получения результатов:
```java
public interface ExecutorService extends Executor {
    void shutdown();
    List<Runnable> shutdownNow();
    boolean isShutdown();
    boolean isTerminated();
    boolean awaitTermination(long timeout, TimeUnit unit);
    <T> Future<T> submit(Callable<T> task);
    Future<?> submit(Runnable task);
    // и другие методы
}
```

### ThreadPoolExecutor
Конкретная реализация ExecutorService, использующая пул потоков для выполнения задач. Это рабочая лошадка всего Executors framework.

### ScheduledExecutorService
Специализированный ExecutorService для выполнения задач с задержкой или периодически:
```java
public interface ScheduledExecutorService extends ExecutorService {
    ScheduledFuture<?> schedule(Runnable command, long delay, TimeUnit unit);
    ScheduledFuture<?> scheduleAtFixedRate(Runnable command,
        long initialDelay, long period, TimeUnit unit);
    ScheduledFuture<?> scheduleWithFixedDelay(Runnable command,
        long initialDelay, long delay, TimeUnit unit);
}
```

### Future
Представляет результат асинхронной операции:
```java
public interface Future<V> {
    boolean cancel(boolean mayInterruptIfRunning);
    boolean isCancelled();
    boolean isDone();
    V get() throws InterruptedException, ExecutionException;
    V get(long timeout, TimeUnit unit) throws InterruptedException,
        ExecutionException, TimeoutException;
}
```

Вызов `get()` блокирует текущий поток до завершения задачи.

### Callable vs Runnable

**Runnable** — задача без результата:
```kotlin
val runnable = Runnable {
    println("Выполняется в фоновом потоке")
    // Нет возвращаемого значения
}
```

**Callable** — задача с результатом:
```kotlin
val callable = Callable<String> {
    // Может выбросить checked exception
    Thread.sleep(1000)
    "Результат вычисления"
}
```

Основные отличия:
- `Callable.call()` возвращает значение, `Runnable.run()` — void
- `Callable` может выбрасывать checked exceptions
- `Callable` используется с `submit()`, возвращающим `Future`

## java.util.concurrent в Android

### Executor Interface — минимальный контракт

Интерфейс `Executor` предоставляет decoupling между отправкой задачи и механизмом её выполнения:

```kotlin
// Вместо:
Thread {
    performBackgroundWork()
}.start()

// Можно:
val executor: Executor = ... // реализация скрыта
executor.execute {
    performBackgroundWork()
}
```

Это позволяет менять стратегию выполнения без изменения кода отправки задач:
- Выполнение в текущем потоке
- Выполнение в новом потоке
- Выполнение в пуле потоков
- Очередь задач для последовательного выполнения

### ExecutorService Lifecycle

ExecutorService имеет чёткий жизненный цикл:

```
[RUNNING] → shutdown() → [SHUTDOWN] → все задачи завершены → [TERMINATED]
              ↓
        shutdownNow()
              ↓
         [TERMINATED]
```

**RUNNING**:
- Принимает новые задачи
- Обрабатывает задачи в очереди
- Начальное состояние после создания

**SHUTDOWN** (после вызова `shutdown()`):
- НЕ принимает новые задачи (будет `RejectedExecutionException`)
- Продолжает обработку задач в очереди
- Graceful shutdown

**TERMINATED**:
- Все задачи завершены
- Все потоки остановлены
- Финальное состояние

Пример правильного shutdown:

```kotlin
class MyViewModel : ViewModel() {
    private val executor = Executors.newFixedThreadPool(4)

    override fun onCleared() {
        super.onCleared()
        executor.shutdown() // не принимать новые задачи
        try {
            // Ждём завершения до 60 секунд
            if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                // Форсированное завершение если таймаут
                executor.shutdownNow()
                // Ждём ещё немного после форсированного завершения
                if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
                    Log.e("MyViewModel", "Executor не завершился")
                }
            }
        } catch (e: InterruptedException) {
            executor.shutdownNow()
            Thread.currentThread().interrupt()
        }
    }
}
```

### submit() vs execute()

**execute(Runnable)** — из интерфейса `Executor`:
```kotlin
executor.execute {
    // Fire-and-forget
    performWork()
    // Нельзя получить результат
    // Exceptions теряются (только в UncaughtExceptionHandler)
}
```

**submit(Callable)** или **submit(Runnable)** — из `ExecutorService`:
```kotlin
val future: Future<String> = executor.submit(Callable {
    performWorkWithResult()
    "Result"
})

// Позже можно получить результат
try {
    val result = future.get() // блокирующий вызов
    println(result)
} catch (e: ExecutionException) {
    // Exception из задачи обёрнут в ExecutionException
    val cause = e.cause
}
```

Ключевые отличия:
- `submit()` возвращает `Future`, `execute()` — void
- `submit()` позволяет отменить задачу через `Future.cancel()`
- `submit()` оборачивает exceptions в `ExecutionException`
- `execute()` немного эффективнее если результат не нужен

### Future.get() и блокировка

**Критическое предупреждение**: `Future.get()` блокирует текущий поток до завершения задачи. Никогда не вызывайте `get()` на главном потоке Android:

```kotlin
// АНТИ-ПАТТЕРН - заморозит UI!
val future = executor.submit {
    fetchDataFromNetwork()
}
val data = future.get() // БЛОКИРОВКА MAIN THREAD
updateUI(data)
```

Правильные подходы:

**Вариант 1: Callback в фоновом потоке**
```kotlin
executor.execute {
    val future = anotherExecutor.submit {
        fetchDataFromNetwork()
    }
    val data = future.get() // блокировка безопасна, мы в фоновом потоке
    runOnUiThread {
        updateUI(data)
    }
}
```

**Вариант 2: Timeout**
```kotlin
executor.execute {
    try {
        val data = future.get(30, TimeUnit.SECONDS)
        runOnUiThread { updateUI(data) }
    } catch (e: TimeoutException) {
        future.cancel(true)
        runOnUiThread { showError() }
    }
}
```

**Вариант 3: Polling (не рекомендуется)**
```kotlin
fun checkResult() {
    if (future.isDone) {
        try {
            val data = future.get() // не блокирует, уже готово
            updateUI(data)
        } catch (e: Exception) {
            handleError(e)
        }
    } else {
        handler.postDelayed({ checkResult() }, 100)
    }
}
```

## ThreadPoolExecutor Internals

`ThreadPoolExecutor` — это сердце Executors framework. Понимание его внутреннего устройства критично для правильной настройки.

### Конструктор

```java
public ThreadPoolExecutor(
    int corePoolSize,                      // минимальное число потоков
    int maximumPoolSize,                   // максимальное число потоков
    long keepAliveTime,                    // время жизни idle потоков
    TimeUnit unit,                         // единица времени
    BlockingQueue<Runnable> workQueue,     // очередь задач
    ThreadFactory threadFactory,           // фабрика для создания потоков
    RejectedExecutionHandler handler       // обработка отклонённых задач
)
```

### corePoolSize vs maximumPoolSize

Эти два параметра определяют, как пул адаптируется к нагрузке.

**corePoolSize** — минимальное число потоков, которые живут постоянно (даже если idle):
- При создании пула потоки не создаются сразу (lazy initialization)
- При поступлении задачи создаётся новый поток, если текущее число потоков < corePoolSize
- Эти потоки НЕ умирают даже если нет работы (если не установлен `allowCoreThreadTimeOut`)

**maximumPoolSize** — максимальное число потоков в пуле:
- Новые потоки создаются сверх corePoolSize только если очередь заполнена
- Эти "extra" потоки умирают после keepAliveTime бездействия

**Диаграмма процесса принятия решений:**

```
Новая задача поступает
        ↓
┌───────────────────────────────┐
│ Текущее число потоков        │
│ < corePoolSize?               │
└───────────────────────────────┘
        ↓ Да                    ↓ Нет
Создать новый поток    ┌────────────────────────┐
для задачи             │ Очередь полна?         │
                       └────────────────────────┘
                         ↓ Нет        ↓ Да
                    Добавить в    ┌─────────────────────────┐
                    очередь       │ Число потоков <         │
                                  │ maximumPoolSize?        │
                                  └─────────────────────────┘
                                    ↓ Да           ↓ Нет
                              Создать новый   Вызвать
                              поток           RejectedExecutionHandler
```

**Пример настройки:**

```kotlin
val executor = ThreadPoolExecutor(
    2,                              // corePoolSize = 2
    4,                              // maximumPoolSize = 4
    60L,                            // keepAliveTime = 60 секунд
    TimeUnit.SECONDS,
    LinkedBlockingQueue(10),        // очередь на 10 задач
    threadFactory,
    ThreadPoolExecutor.CallerRunsPolicy()
)

// Сценарий выполнения:
// Задачи 1-2: создаются 2 core потока, задачи выполняются сразу
// Задачи 3-12: core потоки заняты, задачи идут в очередь (capacity = 10)
// Задача 13: очередь полна, создаётся 3-й поток (extra)
// Задача 14: создаётся 4-й поток (достигнут maximumPoolSize)
// Задача 15: все потоки заняты, очередь полна → CallerRunsPolicy
//            задача выполняется в потоке вызывающего
// Через 60 сек бездействия: потоки 3-4 умирают, остаются только core 1-2
```

### workQueue — очередь задач

Очередь задач используется между corePoolSize и maximumPoolSize. Выбор типа очереди критически важен:

**SynchronousQueue** (capacity = 0):
```kotlin
val executor = ThreadPoolExecutor(
    0, Integer.MAX_VALUE, 60L, TimeUnit.SECONDS,
    SynchronousQueue<Runnable>()
) // Это newCachedThreadPool()
```
- Задача должна быть немедленно передана свободному потоку или создан новый
- Если нет свободного потока и не можем создать новый → reject
- Используется в `newCachedThreadPool()` для максимальной responsive

**LinkedBlockingQueue** (unbounded или bounded):
```kotlin
// Unbounded - опасно, может привести к OOM
val unbounded = ThreadPoolExecutor(
    4, 4, 0L, TimeUnit.MILLISECONDS,
    LinkedBlockingQueue<Runnable>()
) // Это newFixedThreadPool(4)

// Bounded - безопаснее
val bounded = ThreadPoolExecutor(
    2, 4, 60L, TimeUnit.SECONDS,
    LinkedBlockingQueue<Runnable>(100)
)
```
- Unbounded: нет лимита, maximumPoolSize игнорируется (новые потоки никогда не создаются)
- Bounded: фиксированная capacity, создание extra потоков работает как задумано
- FIFO порядок

**ArrayBlockingQueue** (bounded):
```kotlin
val executor = ThreadPoolExecutor(
    2, 4, 60L, TimeUnit.SECONDS,
    ArrayBlockingQueue<Runnable>(50)
)
```
- Фиксированный capacity, установленный при создании
- Backed by array, немного эффективнее LinkedBlockingQueue
- FIFO порядок
- Может быть fair (честная очерёдность потоков)

**PriorityBlockingQueue** (unbounded):
```kotlin
val executor = ThreadPoolExecutor(
    2, 4, 60L, TimeUnit.SECONDS,
    PriorityBlockingQueue<Runnable>()
)
```
- Задачи выполняются по приоритету (нужно implements Comparable)
- Unbounded, может привести к OOM
- Полезно для разных уровней важности задач

### keepAliveTime — время жизни idle потоков

Потоки сверх corePoolSize умирают после keepAliveTime бездействия:

```kotlin
val executor = ThreadPoolExecutor(
    2, 10,                          // core=2, max=10
    30L, TimeUnit.SECONDS,          // idle потоки живут 30 сек
    LinkedBlockingQueue(100)
)

// Опционально: разрешить core потокам тоже умирать
executor.allowCoreThreadTimeOut(true)
```

**Когда увеличивать keepAliveTime:**
- Burst нагрузки с непредсказуемыми интервалами
- Стоимость создания потока высока (например, с инициализацией)
- Хотите держать потоки "warm" для быстрого отклика

**Когда уменьшать keepAliveTime:**
- Нужно освобождать ресурсы быстро
- Потоки создаются быстро
- Memory-constrained окружение (Android!)

### ThreadFactory — именование потоков для debugging

Custom ThreadFactory позволяет именовать потоки, что критически важно для debugging:

```kotlin
class NamedThreadFactory(
    private val namePrefix: String,
    private val daemon: Boolean = false
) : ThreadFactory {
    private val threadNumber = AtomicInteger(1)
    private val group: ThreadGroup = Thread.currentThread().threadGroup!!

    override fun newThread(r: Runnable): Thread {
        val thread = Thread(group, r,
            "$namePrefix-${threadNumber.getAndIncrement()}",
            0
        )
        thread.isDaemon = daemon
        if (thread.priority != Thread.NORM_PRIORITY) {
            thread.priority = Thread.NORM_PRIORITY
        }
        return thread
    }
}

// Использование:
val executor = ThreadPoolExecutor(
    4, 4, 0L, TimeUnit.MILLISECONDS,
    LinkedBlockingQueue(),
    NamedThreadFactory("database-worker", daemon = true)
)

// В логах и профайлере:
// database-worker-1
// database-worker-2
// database-worker-3
// database-worker-4
```

**Best practices для именования:**
- Используйте осмысленные префиксы: "network-", "database-", "image-"
- Включайте компонент: "UserRepository-db-"
- В Android Studio Profiler это упрощает поиск bottleneck
- StrictMode покажет конкретный поток в violation

**Daemon threads:**
```kotlin
thread.isDaemon = true
```
- Daemon потоки не препятствуют завершению JVM/приложения
- Non-daemon потоки держат процесс живым
- Для Android обычно daemon = true (иначе может помешать процессу умереть)

### RejectedExecutionHandler — обработка отклонённых задач

Когда задачу невозможно принять (пул shutdown или очередь полна), вызывается RejectedExecutionHandler.

**AbortPolicy** (по умолчанию):
```kotlin
val executor = ThreadPoolExecutor(
    2, 2, 0L, TimeUnit.MILLISECONDS,
    ArrayBlockingQueue(1),
    ThreadPoolExecutor.AbortPolicy() // default
)

executor.execute { task1() }
executor.execute { task2() }
executor.execute { task3() } // очередь полна
executor.execute { task4() } // RejectedExecutionException!
```
- Выбрасывает `RejectedExecutionException`
- Caller должен обработать exception
- Явно сигнализирует о проблеме

**CallerRunsPolicy** — выполнить в вызывающем потоке:
```kotlin
val executor = ThreadPoolExecutor(
    2, 2, 0L, TimeUnit.MILLISECONDS,
    ArrayBlockingQueue(1),
    ThreadPoolExecutor.CallerRunsPolicy()
)

// В UI thread:
executor.execute { heavyTask() } // если reject → выполнится в UI thread!
```
- Задача выполняется в потоке, который вызвал `execute()`
- Естественный throttling: caller блокируется, не может отправлять новые задачи
- **ОПАСНО для Android**: если вызов из main thread, задача выполнится там же!
- Полезно для non-UI потоков в producer-consumer сценариях

**DiscardPolicy** — молча отбросить:
```kotlin
val executor = ThreadPoolExecutor(
    2, 2, 0L, TimeUnit.MILLISECONDS,
    ArrayBlockingQueue(1),
    ThreadPoolExecutor.DiscardPolicy()
)

executor.execute { task() } // если reject → просто проигнорировано
```
- Задача молча отбрасывается
- Никаких exceptions
- Подходит для non-critical задач (аналитика, logging)
- Опасно: можно потерять важные данные

**DiscardOldestPolicy** — отбросить старейшую задачу в очереди:
```kotlin
val executor = ThreadPoolExecutor(
    2, 2, 0L, TimeUnit.MILLISECONDS,
    ArrayBlockingQueue(1),
    ThreadPoolExecutor.DiscardOldestPolicy()
)

executor.execute { task1() }
executor.execute { task2() } // в очередь
executor.execute { task3() } // task2 выброшена из очереди, task3 добавлена
```
- Удаляет head очереди (самая старая)
- Пытается добавить новую задачу
- Подходит для time-sensitive задач где актуальность важнее истории
- Пример: обновление UI с сенсора, нужна последняя точка данных

**Custom handler:**
```kotlin
class LogAndDiscardPolicy : RejectedExecutionHandler {
    override fun rejectedExecution(r: Runnable, executor: ThreadPoolExecutor) {
        Log.w("Executor", "Task rejected: queue=${executor.queue.size}, " +
            "active=${executor.activeCount}, pool=${executor.poolSize}")

        // Можно отправить в другой executor
        // Можно сохранить в БД для retry
        // Можно показать user notification
    }
}

val executor = ThreadPoolExecutor(
    2, 4, 60L, TimeUnit.SECONDS,
    LinkedBlockingQueue(10),
    NamedThreadFactory("api-worker"),
    LogAndDiscardPolicy()
)
```

**Выбор strategy для Android:**

| Сценарий | Рекомендация |
|----------|--------------|
| Critical операции (сохранение данных) | `AbortPolicy` + retry logic |
| Non-critical (аналитика) | `DiscardPolicy` |
| Realtime UI updates | `DiscardOldestPolicy` |
| Background sync | Custom handler с retry queue |
| НИКОГДА | `CallerRunsPolicy` если caller может быть main thread |

## Factory Methods (Executors Class)

Класс `Executors` предоставляет convenience методы для создания распространённых конфигураций.

### newFixedThreadPool(n)

```kotlin
val executor = Executors.newFixedThreadPool(4)

// Эквивалентно:
ThreadPoolExecutor(
    4,                               // corePoolSize = n
    4,                               // maximumPoolSize = n (фиксировано!)
    0L, TimeUnit.MILLISECONDS,       // keepAlive не важен (все core)
    LinkedBlockingQueue<Runnable>()  // unbounded queue
)
```

**Характеристики:**
- Фиксированное число потоков (всегда n потоков после разогрева)
- Unbounded очередь — может привести к OOM при переполнении
- Потоки никогда не умирают (keepAliveTime = 0)
- Задачи выполняются в порядке поступления (FIFO)

**Когда использовать:**
- Предсказуемая нагрузка
- CPU-bound задачи: `n = Runtime.getRuntime().availableProcessors()`
- IO-bound задачи: `n = больше, например 2 * cores`

**Проблемы:**
- Unbounded queue может привести к OOM
- Не адаптируется к burst нагрузкам

**Лучше для Android:**
```kotlin
// Bounded queue для защиты от OOM
val executor = ThreadPoolExecutor(
    4, 4, 0L, TimeUnit.MILLISECONDS,
    LinkedBlockingQueue(100), // bounded!
    NamedThreadFactory("fixed-pool"),
    ThreadPoolExecutor.CallerRunsPolicy() // или custom handler
)
```

### newCachedThreadPool()

```kotlin
val executor = Executors.newCachedThreadPool()

// Эквивалентно:
ThreadPoolExecutor(
    0,                               // corePoolSize = 0 (нет постоянных)
    Integer.MAX_VALUE,               // maximumPoolSize = unbounded
    60L, TimeUnit.SECONDS,           // idle потоки умирают через 60 сек
    SynchronousQueue<Runnable>()     // прямая передача, нет очереди
)
```

**Характеристики:**
- Создаёт новый поток для каждой задачи если нет свободного
- Потоки переиспользуются если доступны
- Idle потоки умирают через 60 секунд
- Нет ограничения на число потоков — **ОПАСНО!**

**Когда использовать (осторожно):**
- Много коротких асинхронных задач
- Непредсказуемое время выполнения
- Нужна высокая responsiveness

**ОПАСНОСТИ для Android:**
```kotlin
val executor = Executors.newCachedThreadPool()

// Сценарий катастрофы:
repeat(10000) {
    executor.execute {
        Thread.sleep(5000) // долгая задача
    }
}
// Создаст 10000 потоков → OOM crash!
```

**Почему опасно:**
- Android имеет лимит потоков (обычно ~1000-2000)
- Каждый поток потребляет memory (stack size ~1MB)
- Context switching overhead убивает performance
- Battery drain от избыточных потоков

**Безопасная альтернатива для Android:**
```kotlin
// Ограниченный cached pool
val executor = ThreadPoolExecutor(
    0,                               // нет core потоков
    20,                              // максимум 20 потоков (разумный лимит)
    60L, TimeUnit.SECONDS,
    SynchronousQueue<Runnable>(),
    NamedThreadFactory("cached-pool"),
    ThreadPoolExecutor.AbortPolicy() // явно падать при превышении
)
```

### newSingleThreadExecutor()

```kotlin
val executor = Executors.newSingleThreadExecutor()

// Эквивалентно (но wrapped для immutability):
ThreadPoolExecutor(
    1,                               // только 1 поток
    1,                               // максимум 1 поток
    0L, TimeUnit.MILLISECONDS,
    LinkedBlockingQueue<Runnable>()  // unbounded queue
)
```

**Характеристики:**
- Ровно один поток
- Задачи выполняются последовательно в порядке поступления
- Гарантия порядка выполнения
- Unbounded очередь

**Когда использовать:**
- Нужна гарантия последовательного выполнения
- State модификация без locks (single-threaded)
- Замена HandlerThread в некоторых случаях

**Примеры использования в Android:**
```kotlin
// Database executor для последовательных операций
class DatabaseExecutor {
    companion object {
        val instance = Executors.newSingleThreadExecutor(
            NamedThreadFactory("database-sequential")
        )
    }
}

// Использование:
DatabaseExecutor.instance.execute {
    // Гарантированно последовательно
    db.insert(record1)
    db.insert(record2)
    db.update(record3)
}
```

**Проблема unbounded queue:**
```kotlin
// Безопаснее:
val executor = ThreadPoolExecutor(
    1, 1, 0L, TimeUnit.MILLISECONDS,
    LinkedBlockingQueue(50),         // bounded
    NamedThreadFactory("sequential"),
    ThreadPoolExecutor.DiscardOldestPolicy()
)
```

### newScheduledThreadPool(n)

```kotlin
val scheduler = Executors.newScheduledThreadPool(2)

// Эквивалентно:
ScheduledThreadPoolExecutor(
    2                                 // corePoolSize = n
    // maximumPoolSize = Integer.MAX_VALUE
    // keepAliveTime = 0
    // DelayedWorkQueue
)
```

**Характеристики:**
- Для отложенных и периодических задач
- Фиксированное число потоков для выполнения
- DelayedWorkQueue — специальная очередь с приоритетом по времени

**API методы:**

```kotlin
// Однократное выполнение с задержкой
scheduler.schedule({
    performTask()
}, 5, TimeUnit.SECONDS) // через 5 секунд

// Периодическое выполнение с фиксированной частотой
scheduler.scheduleAtFixedRate({
    syncData()
}, 0, 30, TimeUnit.SECONDS) // сразу, затем каждые 30 сек
// Следующий запуск через 30 сек от начала предыдущего

// Периодическое выполнение с фиксированной задержкой
scheduler.scheduleWithFixedDelay({
    checkHealth()
}, 10, 60, TimeUnit.SECONDS) // через 10 сек, затем каждые 60 сек после завершения
// Следующий запуск через 60 сек от окончания предыдущего
```

**Когда использовать:**
- Периодические фоновые синхронизации
- Polling механизмы
- Timeout механизмы
- Retry logic с backoff

**ВАЖНО для Android:**
- WorkManager предпочтительнее для background работы (respects Doze mode)
- ScheduledExecutor НЕ работает когда приложение убито
- НЕ respects battery optimization

**Пример использования:**
```kotlin
class SessionManager {
    private val scheduler = Executors.newScheduledThreadPool(1,
        NamedThreadFactory("session-manager")
    )

    fun startSessionRefresh() {
        scheduler.scheduleWithFixedDelay({
            try {
                refreshAuthToken()
            } catch (e: Exception) {
                Log.e("Session", "Token refresh failed", e)
            }
        }, 0, 15, TimeUnit.MINUTES)
    }

    fun shutdown() {
        scheduler.shutdown()
    }
}
```

### Таблица сравнения Factory Methods

| Factory Method | corePoolSize | maxPoolSize | keepAlive | Queue | Pros | Cons | Android Use |
|----------------|--------------|-------------|-----------|-------|------|------|-------------|
| `newFixedThreadPool(n)` | n | n | 0 | Unbounded LinkedBlockingQueue | Предсказуемое число потоков, простая настройка | Unbounded queue → OOM риск | CPU/IO-bound задачи с bounded queue версией |
| `newCachedThreadPool()` | 0 | MAX_VALUE | 60s | SynchronousQueue | Быстрая адаптация к нагрузке, переиспользование | Unbounded threads → OOM, thread explosion | ИЗБЕГАТЬ или строго ограничивать maxPoolSize |
| `newSingleThreadExecutor()` | 1 | 1 | 0 | Unbounded LinkedBlockingQueue | Гарантия порядка, thread-safety без locks | Unbounded queue, низкая throughput | Sequential операции, state модификация |
| `newScheduledThreadPool(n)` | n | MAX_VALUE | 0 | DelayedWorkQueue | Поддержка scheduling, периодические задачи | Не работает в background (Doze mode) | In-app периодические задачи (НЕ для background) |

**Общие рекомендации для Android:**
- Всегда используйте bounded queues вместо unbounded
- Всегда используйте custom ThreadFactory с именованием
- Всегда устанавливайте RejectedExecutionHandler явно
- Для фоновой работы предпочитайте WorkManager
- Для долгих операций рассмотрите Kotlin Coroutines

## Best Practices для Android

### Singleton Executor vs Per-Component

**Singleton подход (рекомендуется для большинства случаев):**

```kotlin
object AppExecutors {
    // Для database операций - sequential
    val diskIO: Executor = Executors.newSingleThreadExecutor(
        NamedThreadFactory("disk-io", daemon = true)
    )

    // Для network запросов
    val networkIO: Executor = ThreadPoolExecutor(
        0, 3, 60L, TimeUnit.SECONDS,
        SynchronousQueue<Runnable>(),
        NamedThreadFactory("network-io", daemon = true),
        ThreadPoolExecutor.AbortPolicy()
    )

    // Для легких вычислений
    val computation: Executor = ThreadPoolExecutor(
        Runtime.getRuntime().availableProcessors(),
        Runtime.getRuntime().availableProcessors(),
        0L, TimeUnit.MILLISECONDS,
        LinkedBlockingQueue(128),
        NamedThreadFactory("computation", daemon = true),
        ThreadPoolExecutor.CallerRunsPolicy()
    )

    // Для UI-related задач (например, bitmap processing)
    val mainThread: Executor = MainThreadExecutor()
}

private class MainThreadExecutor : Executor {
    private val handler = Handler(Looper.getMainLooper())

    override fun execute(command: Runnable) {
        handler.post(command)
    }
}
```

**Pros:**
- Централизованное управление ресурсами
- Контроль над общим числом потоков в приложении
- Легко мониторить и настраивать
- Переиспользование потоков между компонентами

**Cons:**
- Глобальное состояние (но для Executors это ок)
- Нужно аккуратно с shutdown (обычно не shutdown вовсе)

**Per-component подход:**

```kotlin
class UserRepository {
    private val executor = Executors.newFixedThreadPool(2,
        NamedThreadFactory("user-repo")
    )

    fun close() {
        executor.shutdown()
    }
}
```

**Когда использовать per-component:**
- Компонент имеет специфичные требования (priority, threading policy)
- Нужна изоляция (сбой одного компонента не влияет на другие)
- Короткий lifecycle (например, на время одной операции)
- Тестирование (легче мокировать)

**Hybrid подход:**
```kotlin
class ImageLoader {
    // Используем shared для network
    private val networkExecutor = AppExecutors.networkIO

    // Собственный для decoding (CPU-intensive)
    private val decodingExecutor = ThreadPoolExecutor(
        2, 4, 60L, TimeUnit.SECONDS,
        LinkedBlockingQueue(50),
        NamedThreadFactory("image-decoder"),
        ThreadPoolExecutor.DiscardOldestPolicy()
    )
}
```

### Shutdown в Lifecycle

Правильное управление lifecycle критично для предотвращения утечек.

**Activity/Fragment:**
```kotlin
class MyActivity : AppCompatActivity() {
    private lateinit var executor: ExecutorService

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        executor = Executors.newFixedThreadPool(2)
    }

    override fun onDestroy() {
        super.onDestroy()
        // Graceful shutdown
        executor.shutdown()
        try {
            if (!executor.awaitTermination(800, TimeUnit.MILLISECONDS)) {
                executor.shutdownNow()
            }
        } catch (e: InterruptedException) {
            executor.shutdownNow()
        }
    }
}
```

**ViewModel (рекомендуется):**
```kotlin
class MyViewModel : ViewModel() {
    private val executor = Executors.newFixedThreadPool(2,
        NamedThreadFactory("viewmodel-worker")
    )

    override fun onCleared() {
        super.onCleared()
        executor.shutdown()
        // Можно не ждать - ViewModel cleanup не должна блокировать
        // Но установите daemon = true в ThreadFactory
    }

    fun loadData() {
        executor.execute {
            val data = repository.fetchData()
            // Используйте LiveData.postValue() для UI update
            _liveData.postValue(data)
        }
    }
}
```

**Application-wide executors (singleton):**
```kotlin
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()
        // НЕ shutdown application-wide executors
        // Они живут весь lifecycle приложения
    }
}
```

**Service:**
```kotlin
class DataSyncService : Service() {
    private lateinit var executor: ExecutorService

    override fun onCreate() {
        super.onCreate()
        executor = Executors.newSingleThreadExecutor()
    }

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdown()
        // Service может быть killed, не ждём долго
        executor.awaitTermination(1, TimeUnit.SECONDS)
    }
}
```

### Thread Naming для Debugging

Именование потоков критично для профилирования и debugging:

```kotlin
class NamedThreadFactory(
    private val namePrefix: String,
    private val daemon: Boolean = true,
    private val priority: Int = Thread.NORM_PRIORITY
) : ThreadFactory {
    private val poolNumber = AtomicInteger(1)
    private val threadNumber = AtomicInteger(1)
    private val group: ThreadGroup

    init {
        val s = System.getSecurityManager()
        group = if (s != null) {
            s.threadGroup
        } else {
            Thread.currentThread().threadGroup!!
        }
    }

    override fun newThread(r: Runnable): Thread {
        val name = "$namePrefix-pool-${poolNumber.get()}-thread-${threadNumber.getAndIncrement()}"
        val thread = Thread(group, r, name, 0)

        if (thread.isDaemon != daemon) {
            thread.isDaemon = daemon
        }

        if (thread.priority != priority) {
            thread.priority = priority
        }

        return thread
    }
}
```

**Naming conventions:**
```kotlin
object AppExecutors {
    val database = Executors.newSingleThreadExecutor(
        NamedThreadFactory("db")
    )
    // Потоки: db-pool-1-thread-1

    val network = Executors.newFixedThreadPool(3,
        NamedThreadFactory("net")
    )
    // Потоки: net-pool-1-thread-1, net-pool-1-thread-2, ...

    val imageDecoding = Executors.newFixedThreadPool(2,
        NamedThreadFactory("img-decode")
    )
    // Потоки: img-decode-pool-1-thread-1, ...
}
```

**Польза в Android Studio Profiler:**
- Легко идентифицировать threads в Thread view
- Быстро найти bottleneck (например, все img-decode потоки заняты)
- StrictMode violations показывают конкретный поток
- ANR traces читабельнее

**Пример ANR trace с именованием:**
```
"main" prio=5 tid=1 Waiting
"net-pool-1-thread-1" prio=5 tid=12 Native (fetching data)
"net-pool-1-thread-2" prio=5 tid=13 Native (fetching data)
"db-pool-1-thread-1" prio=5 tid=14 Runnable (writing to DB)
"img-decode-pool-1-thread-1" prio=5 tid=15 Native (decoding bitmap)
```

### CPU-bound vs IO-bound Sizing

Правильный размер пула зависит от типа задач.

**CPU-bound задачи** (вычисления, encoding, parsing):
```kotlin
val cpuCount = Runtime.getRuntime().availableProcessors()

// Классическая формула: n_threads = n_cpu
val computeExecutor = Executors.newFixedThreadPool(cpuCount,
    NamedThreadFactory("compute")
)

// Для Android можно чуть больше для responsiveness:
val computeExecutor = ThreadPoolExecutor(
    cpuCount,
    cpuCount + 1,
    60L, TimeUnit.SECONDS,
    LinkedBlockingQueue(128),
    NamedThreadFactory("compute"),
    ThreadPoolExecutor.CallerRunsPolicy()
)
```

**Почему n_cpu:**
- Больше потоков → больше context switching overhead
- CPU-bound задачи не блокируются на IO, постоянно используют CPU
- Оптимально загружает все cores без overhead

**IO-bound задачи** (network, disk, database):
```kotlin
val cpuCount = Runtime.getRuntime().availableProcessors()

// Формула: n_threads = n_cpu * (1 + wait_time / compute_time)
// Для типичного IO: wait_time >> compute_time
// Практически: 2 * n_cpu до 10 * n_cpu

val ioExecutor = ThreadPoolExecutor(
    cpuCount * 2,                    // core
    cpuCount * 4,                    // max
    60L, TimeUnit.SECONDS,
    LinkedBlockingQueue(100),
    NamedThreadFactory("io"),
    ThreadPoolExecutor.AbortPolicy()
)
```

**Почему больше потоков:**
- IO-bound потоки большую часть времени блокируются (waiting on socket, disk)
- Пока один поток ждёт, другой может использовать CPU
- Но не слишком много — контекст switching и memory overhead

**Network IO (специфика Android):**
```kotlin
// Network обычно имеет concurrency limits на уровне сервера
// Слишком много параллельных запросов могут перегрузить server
val networkExecutor = ThreadPoolExecutor(
    0,                               // no core threads
    3,                               // максимум 3 одновременных запроса
    60L, TimeUnit.SECONDS,
    SynchronousQueue<Runnable>(),
    NamedThreadFactory("network"),
    ThreadPoolExecutor.CallerRunsPolicy()
)
```

**Database IO:**
```kotlin
// SQLite имеет WAL mode для concurrent reads
// Но writes всё равно serialized
val dbReadExecutor = Executors.newFixedThreadPool(4,
    NamedThreadFactory("db-read")
)

val dbWriteExecutor = Executors.newSingleThreadExecutor(
    NamedThreadFactory("db-write") // sequential writes
)
```

**Mixed workload:**
```kotlin
// Разные пулы для разных типов
object AppExecutors {
    private val CPU_COUNT = Runtime.getRuntime().availableProcessors()

    // CPU-intensive (image processing, crypto)
    val compute = Executors.newFixedThreadPool(CPU_COUNT)

    // Disk IO
    val diskIO = Executors.newFixedThreadPool(CPU_COUNT * 2)

    // Network IO
    val networkIO = ThreadPoolExecutor(
        0, 3, 60L, TimeUnit.SECONDS,
        SynchronousQueue()
    )
}
```

### AppExecutors Pattern

Паттерн из Google Architecture Components samples:

```kotlin
/**
 * Global executor pools for the whole application.
 *
 * Grouping tasks like this avoids the effects of task starvation
 * (e.g. disk reads don't wait behind webservice requests).
 */
object AppExecutors {
    private val CPU_COUNT = Runtime.getRuntime().availableProcessors()

    /**
     * Executor for disk I/O operations (database, file system).
     * Uses a single thread to ensure serial execution.
     */
    val diskIO: Executor by lazy {
        Executors.newSingleThreadExecutor(
            NamedThreadFactory("disk-io", daemon = true)
        )
    }

    /**
     * Executor for network I/O operations.
     * Limited pool size to avoid overwhelming the server.
     */
    val networkIO: Executor by lazy {
        ThreadPoolExecutor(
            0,                               // No core threads
            3,                               // Max 3 concurrent requests
            60L, TimeUnit.SECONDS,
            SynchronousQueue<Runnable>(),
            NamedThreadFactory("network-io", daemon = true),
            ThreadPoolExecutor.AbortPolicy()
        )
    }

    /**
     * Executor for CPU-intensive operations.
     * Pool size equals CPU count for optimal performance.
     */
    val computation: Executor by lazy {
        Executors.newFixedThreadPool(
            CPU_COUNT,
            NamedThreadFactory("computation", daemon = true)
        )
    }

    /**
     * Executor that runs tasks on the main thread.
     */
    val mainThread: Executor by lazy {
        MainThreadExecutor()
    }

    private class MainThreadExecutor : Executor {
        private val mainThreadHandler = Handler(Looper.getMainLooper())

        override fun execute(command: Runnable) {
            mainThreadHandler.post(command)
        }
    }

    private class NamedThreadFactory(
        private val name: String,
        private val daemon: Boolean = false
    ) : ThreadFactory {
        private val threadNumber = AtomicInteger(1)

        override fun newThread(r: Runnable): Thread {
            val thread = Thread(r, "$name-${threadNumber.getAndIncrement()}")
            thread.isDaemon = daemon
            if (thread.priority != Thread.NORM_PRIORITY) {
                thread.priority = Thread.NORM_PRIORITY
            }
            return thread
        }
    }
}
```

**Использование в приложении:**

```kotlin
class UserRepository(
    private val userDao: UserDao,
    private val userService: UserService
) {
    fun getUser(userId: String): LiveData<User> {
        val result = MutableLiveData<User>()

        // Сначала загружаем из БД (disk IO)
        AppExecutors.diskIO.execute {
            val cachedUser = userDao.getUser(userId)
            result.postValue(cachedUser)

            // Затем обновляем с сервера (network IO)
            AppExecutors.networkIO.execute {
                try {
                    val freshUser = userService.getUser(userId)

                    // Сохраняем в БД (disk IO)
                    AppExecutors.diskIO.execute {
                        userDao.insert(freshUser)
                        result.postValue(freshUser)
                    }
                } catch (e: Exception) {
                    Log.e("UserRepository", "Failed to fetch user", e)
                }
            }
        }

        return result
    }
}
```

## Когда Executors Вместо Coroutines

Несмотря на популярность Kotlin Coroutines, есть сценарии когда Executors остаются предпочтительным выбором.

### Java-only Codebase

```kotlin
// Если проект на Java или migration на Kotlin невозможна
public class UserRepository {
    private final ExecutorService executor = Executors.newFixedThreadPool(2);
    private final UserDao userDao;

    public UserRepository(UserDao userDao) {
        this.userDao = userDao;
    }

    public Future<User> getUser(String userId) {
        return executor.submit(() -> userDao.getUser(userId));
    }

    public void close() {
        executor.shutdown();
    }
}
```

### Library Code без Зависимости от Kotlin

```kotlin
// Публичная библиотека, которая не хочет тянуть Kotlin runtime
class ImageLoader {
    private val executor = Executors.newFixedThreadPool(3)

    fun loadImage(url: String, callback: (Bitmap) -> Unit) {
        executor.execute {
            val bitmap = downloadAndDecode(url)
            callback(bitmap)
        }
    }

    // Пользователи библиотеки могут использовать её из Java и Kotlin
}
```

### Precise Thread Control

```kotlin
// Когда нужен точный контроль над thread policies
class RealtimeAudioProcessor {
    private val executor = ThreadPoolExecutor(
        1, 1, 0L, TimeUnit.MILLISECONDS,
        LinkedBlockingQueue(1), // Drop frames if can't keep up
        object : ThreadFactory {
            override fun newThread(r: Runnable): Thread {
                return Thread(r, "audio-processor").apply {
                    priority = Thread.MAX_PRIORITY  // Высокий приоритет
                    isDaemon = false                // НЕ daemon
                }
            }
        },
        ThreadPoolExecutor.DiscardOldestPolicy() // Drop old frames
    )

    fun processAudioFrame(frame: ByteArray) {
        executor.execute {
            // Real-time обработка с гарантиями latency
            processFrame(frame)
        }
    }
}
```

### Integration с Legacy Code

```kotlin
// Интеграция с существующим кодом на Executors
class DataSyncManager(
    private val legacyExecutor: ExecutorService // Передан извне
) {
    fun syncData() {
        legacyExecutor.submit {
            // Используем существующий executor для консистентности
            performSync()
        }
    }

    // Можно bridge к Coroutines если нужно:
    suspend fun syncDataSuspend() = suspendCoroutine<Unit> { continuation ->
        legacyExecutor.execute {
            try {
                performSync()
                continuation.resume(Unit)
            } catch (e: Exception) {
                continuation.resumeWithException(e)
            }
        }
    }
}
```

### Blocking API Integration

```kotlin
// Room до версии 2.1 не поддерживал suspend
class OldRoomRepository {
    private val executor = AppExecutors.diskIO

    fun getUsers(): LiveData<List<User>> {
        val result = MutableLiveData<List<User>>()
        executor.execute {
            // Room blocking call
            val users = userDao.getUsers() // List, not Flow
            result.postValue(users)
        }
        return result
    }
}
```

### Benchmark и Testing

```kotlin
// Для benchmark нужен точный контроль
class PerformanceBenchmark {
    fun benchmarkThreadPool() {
        val executor = Executors.newFixedThreadPool(4)
        val startTime = System.nanoTime()

        val futures = (1..1000).map { i ->
            executor.submit {
                performTask(i)
            }
        }

        futures.forEach { it.get() } // Wait all

        val duration = System.nanoTime() - startTime
        println("Duration: ${duration / 1_000_000}ms")

        executor.shutdown()
    }
}
```

**Когда всё-таки Coroutines лучше:**
- Современный Kotlin codebase
- Structured concurrency нужна
- Нужны cancellation и timeout
- UI code с lifecycle awareness
- Асинхронные операции с множественными шагами
- Reactive streams (Flow)

## Anti-patterns

### Unbounded Queue + Cached Pool → OOM

```kotlin
// АНТИ-ПАТТЕРН
val executor = Executors.newCachedThreadPool()

// Сценарий: user быстро скроллит список, триггерит загрузку изображений
repeat(10000) { index ->
    executor.execute {
        loadImage(index) // Долгая операция
    }
}
// Результат: 10000 потоков → OOM crash
```

**Почему происходит:**
- `newCachedThreadPool()` имеет `maximumPoolSize = Integer.MAX_VALUE`
- `SynchronousQueue` не хранит задачи
- Каждая задача создаёт новый поток если нет свободного
- Потоки потребляют ~1MB stack каждый + overhead
- 10000 потоков = ~10GB RAM → crash

**Правильно:**
```kotlin
val executor = ThreadPoolExecutor(
    0,
    10,                              // Разумный лимит
    60L, TimeUnit.SECONDS,
    LinkedBlockingQueue(100),        // Bounded queue
    NamedThreadFactory("image-loader"),
    ThreadPoolExecutor.DiscardOldestPolicy() // Сбрасываем старые
)

// Или ещё лучше: debounce/throttle на уровне UI
```

### Missing Shutdown → Thread Leak

```kotlin
// АНТИ-ПАТТЕРН
class MyActivity : AppCompatActivity() {
    private val executor = Executors.newFixedThreadPool(4)

    fun loadData() {
        executor.execute {
            // Долгая операция
        }
    }

    // onDestroy() НЕ вызывает shutdown()
}

// Activity пересоздаётся (rotation) → новый executor
// Старый executor продолжает жить → утечка потоков
```

**Последствия:**
- Потоки продолжают работу после destroy
- Memory leak (thread держит reference на Activity через closure)
- Бесполезная работа (результат никому не нужен)
- Накопление потоков при пересоздании Activity

**Правильно:**
```kotlin
class MyActivity : AppCompatActivity() {
    private val executor = Executors.newFixedThreadPool(4,
        NamedThreadFactory("activity-worker", daemon = true)
    )

    override fun onDestroy() {
        super.onDestroy()
        executor.shutdown()
        // Опционально: отменить running задачи
        if (isFinishing) {
            executor.shutdownNow()
        }
    }
}

// Лучше: используйте ViewModel с lifecycle-aware executor
```

### Blocking на Main Thread

```kotlin
// АНТИ-ПАТТЕРН
fun loadUserData() {
    val future = executor.submit {
        fetchUserFromNetwork() // 2 секунды
    }

    val user = future.get() // БЛОКИРОВКА UI потока на 2 секунды!
    updateUI(user)
}
// Результат: Frozen UI, ANR
```

**Правильно:**
```kotlin
fun loadUserData() {
    executor.execute {
        val user = fetchUserFromNetwork() // В фоне
        runOnUiThread {
            updateUI(user)
        }
    }
}

// Или с LiveData:
fun loadUserData() {
    val liveData = MutableLiveData<User>()
    executor.execute {
        val user = fetchUserFromNetwork()
        liveData.postValue(user)
    }
    return liveData
}
```

### new Thread() Everywhere

```kotlin
// АНТИ-ПАТТЕРН
fun performTask1() {
    Thread {
        // Работа
    }.start()
}

fun performTask2() {
    Thread {
        // Работа
    }.start()
}

// Вызывается 1000 раз → 1000 новых потоков
```

**Проблемы:**
- Стоимость создания потока высока (~1-2ms)
- Нет переиспользования
- Нет контроля над concurrency
- Нет graceful shutdown

**Правильно:**
```kotlin
object AppExecutors {
    val shared = Executors.newFixedThreadPool(4)
}

fun performTask1() {
    AppExecutors.shared.execute {
        // Переиспользование потоков
    }
}
```

### Неправильный Выбор Queue Type

```kotlin
// АНТИ-ПАТТЕРН: SynchronousQueue с ограниченным пулом
val executor = ThreadPoolExecutor(
    2, 2,                            // Только 2 потока
    0L, TimeUnit.MILLISECONDS,
    SynchronousQueue<Runnable>(),    // Нет очереди!
    ThreadPoolExecutor.AbortPolicy()
)

executor.execute { task1() } // поток 1
executor.execute { task2() } // поток 2
executor.execute { task3() } // RejectedExecutionException!
// SynchronousQueue требует свободный поток немедленно
```

**Правильно:**
```kotlin
val executor = ThreadPoolExecutor(
    2, 2,
    0L, TimeUnit.MILLISECONDS,
    LinkedBlockingQueue(100),        // Bounded queue
    ThreadPoolExecutor.CallerRunsPolicy()
)
```

**Когда какую queue:**
- **LinkedBlockingQueue (unbounded)**: fixed pool, не критично к OOM
- **LinkedBlockingQueue (bounded)**: нужен контроль над memory
- **ArrayBlockingQueue**: bounded с лучшей performance
- **SynchronousQueue**: cached pool, прямая передача
- **PriorityBlockingQueue**: нужен priority, но unbounded
- **DelayedWorkQueue**: только для ScheduledExecutorService

## Интеграция с Architecture Components

### Executor + LiveData

```kotlin
class UserRepository(
    private val userDao: UserDao,
    private val userService: UserService,
    private val executor: Executor = AppExecutors.diskIO
) {
    fun loadUser(userId: String): LiveData<Resource<User>> {
        return object : LiveData<Resource<User>>() {
            override fun onActive() {
                super.onActive()

                // Показываем loading
                value = Resource.Loading()

                executor.execute {
                    try {
                        // Сначала из кеша
                        val cached = userDao.getUser(userId)
                        postValue(Resource.Success(cached))

                        // Затем fresh с сервера
                        val fresh = userService.getUser(userId)
                        userDao.insert(fresh)
                        postValue(Resource.Success(fresh))

                    } catch (e: Exception) {
                        postValue(Resource.Error(e.message ?: "Unknown error"))
                    }
                }
            }
        }
    }
}

sealed class Resource<T> {
    class Loading<T> : Resource<T>()
    data class Success<T>(val data: T) : Resource<T>()
    data class Error<T>(val message: String) : Resource<T>()
}
```

### Executor + Repository Pattern

```kotlin
class UserRepository(
    private val localDataSource: UserLocalDataSource,
    private val remoteDataSource: UserRemoteDataSource
) {
    private val executors = AppExecutors

    fun getUsers(): LiveData<List<User>> {
        val result = MediatorLiveData<List<User>>()

        // Локальные данные немедленно
        val localData = localDataSource.getUsers()
        result.addSource(localData) { users ->
            result.value = users
        }

        // Обновление с сервера
        executors.networkIO.execute {
            try {
                val remoteUsers = remoteDataSource.fetchUsers()

                executors.diskIO.execute {
                    localDataSource.saveUsers(remoteUsers)
                    // LiveData автоматически уведомит об изменениях
                }
            } catch (e: Exception) {
                Log.e("UserRepository", "Failed to sync", e)
            }
        }

        return result
    }

    fun updateUser(user: User, callback: (Result<Unit>) -> Unit) {
        executors.networkIO.execute {
            try {
                remoteDataSource.updateUser(user)

                executors.diskIO.execute {
                    localDataSource.updateUser(user)

                    executors.mainThread.execute {
                        callback(Result.success(Unit))
                    }
                }
            } catch (e: Exception) {
                executors.mainThread.execute {
                    callback(Result.failure(e))
                }
            }
        }
    }
}
```

### Room @Query на Background Executor

```kotlin
// Room 2.1+ поддерживает suspend, но для старых версий:
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getUsers(): List<User> // Blocking call

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    fun insert(user: User)
}

// Repository с executor:
class UserRepository(
    private val userDao: UserDao,
    private val executor: Executor = AppExecutors.diskIO
) {
    fun getUsers(): LiveData<List<User>> {
        val result = MutableLiveData<List<User>>()
        executor.execute {
            val users = userDao.getUsers() // Blocking в фоне
            result.postValue(users)
        }
        return result
    }

    fun insertUser(user: User, callback: () -> Unit) {
        executor.execute {
            userDao.insert(user)
            AppExecutors.mainThread.execute {
                callback()
            }
        }
    }
}
```

### Полная Архитектура

```kotlin
// Application-level executors
object AppExecutors {
    private val CPU_COUNT = Runtime.getRuntime().availableProcessors()

    val diskIO: Executor = Executors.newSingleThreadExecutor(
        NamedThreadFactory("disk-io", daemon = true)
    )

    val networkIO: Executor = ThreadPoolExecutor(
        0, 3, 60L, TimeUnit.SECONDS,
        SynchronousQueue<Runnable>(),
        NamedThreadFactory("network-io", daemon = true),
        ThreadPoolExecutor.AbortPolicy()
    )

    val mainThread: Executor = MainThreadExecutor()

    private class MainThreadExecutor : Executor {
        private val handler = Handler(Looper.getMainLooper())
        override fun execute(command: Runnable) = handler.post(command)
    }

    private class NamedThreadFactory(
        private val name: String,
        private val daemon: Boolean
    ) : ThreadFactory {
        private val count = AtomicInteger(1)
        override fun newThread(r: Runnable) = Thread(r, "$name-${count.getAndIncrement()}").apply {
            isDaemon = daemon
        }
    }
}

// Data sources
class UserLocalDataSource(private val userDao: UserDao) {
    fun getUsers(): LiveData<List<User>> = userDao.getUsersLiveData()

    fun saveUsers(users: List<User>) {
        userDao.insertAll(users)
    }
}

class UserRemoteDataSource(private val apiService: ApiService) {
    @Throws(IOException::class)
    fun fetchUsers(): List<User> = apiService.getUsers().execute().body()!!
}

// Repository
class UserRepository(
    private val localDataSource: UserLocalDataSource,
    private val remoteDataSource: UserRemoteDataSource,
    private val appExecutors: AppExecutors = AppExecutors
) {
    fun loadUsers(forceRefresh: Boolean = false): LiveData<Resource<List<User>>> {
        return object : NetworkBoundResource<List<User>, List<User>>(appExecutors) {
            override fun saveCallResult(item: List<User>) {
                localDataSource.saveUsers(item)
            }

            override fun shouldFetch(data: List<User>?): Boolean {
                return forceRefresh || data == null || data.isEmpty()
            }

            override fun loadFromDb(): LiveData<List<User>> {
                return localDataSource.getUsers()
            }

            override fun createCall(): Call<List<User>> {
                return remoteDataSource.fetchUsers()
            }
        }.asLiveData()
    }
}

// NetworkBoundResource helper
abstract class NetworkBoundResource<ResultType, RequestType>(
    private val appExecutors: AppExecutors
) {
    private val result = MediatorLiveData<Resource<ResultType>>()

    init {
        result.value = Resource.Loading()

        val dbSource = loadFromDb()
        result.addSource(dbSource) { data ->
            result.removeSource(dbSource)

            if (shouldFetch(data)) {
                fetchFromNetwork(dbSource)
            } else {
                result.addSource(dbSource) { newData ->
                    result.value = Resource.Success(newData)
                }
            }
        }
    }

    private fun fetchFromNetwork(dbSource: LiveData<ResultType>) {
        result.addSource(dbSource) { newData ->
            result.value = Resource.Loading(newData)
        }

        appExecutors.networkIO.execute {
            try {
                val response = createCall()
                appExecutors.diskIO.execute {
                    saveCallResult(response)
                }
            } catch (e: Exception) {
                appExecutors.mainThread.execute {
                    result.removeSource(dbSource)
                    result.addSource(dbSource) { newData ->
                        result.value = Resource.Error(e.message, newData)
                    }
                }
            }
        }
    }

    fun asLiveData(): LiveData<Resource<ResultType>> = result

    protected abstract fun saveCallResult(item: RequestType)
    protected abstract fun shouldFetch(data: ResultType?): Boolean
    protected abstract fun loadFromDb(): LiveData<ResultType>
    protected abstract fun createCall(): RequestType
}

// ViewModel
class UserViewModel(
    private val repository: UserRepository
) : ViewModel() {
    private val _users = MutableLiveData<Resource<List<User>>>()
    val users: LiveData<Resource<List<User>>> = _users

    fun loadUsers(forceRefresh: Boolean = false) {
        _users.addSource(repository.loadUsers(forceRefresh)) { resource ->
            _users.value = resource
        }
    }
}

// Activity
class UserActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        viewModel.users.observe(this) { resource ->
            when (resource) {
                is Resource.Loading -> showLoading()
                is Resource.Success -> showUsers(resource.data)
                is Resource.Error -> showError(resource.message)
            }
        }

        viewModel.loadUsers()
    }
}
```

## Код Примеры

### Создание Правильного ThreadPoolExecutor

```kotlin
/**
 * Создание production-ready ThreadPoolExecutor с полным контролем
 */
class CustomExecutorFactory {
    companion object {
        private val CPU_COUNT = Runtime.getRuntime().availableProcessors()

        /**
         * Создаёт executor для CPU-intensive задач
         * - Число потоков = CPU cores
         * - Bounded queue для защиты от OOM
         * - Named threads для debugging
         * - CallerRunsPolicy для естественного throttling
         */
        fun createComputeExecutor(): ExecutorService {
            return ThreadPoolExecutor(
                CPU_COUNT,                       // corePoolSize
                CPU_COUNT,                       // maximumPoolSize
                0L,                              // keepAliveTime (все core)
                TimeUnit.MILLISECONDS,
                LinkedBlockingQueue(128),        // bounded queue
                NamedThreadFactory("compute", daemon = true),
                ThreadPoolExecutor.CallerRunsPolicy() // throttling
            )
        }

        /**
         * Создаёт executor для IO-intensive задач
         * - Динамический пул (0 core, до 2*CPU max)
         * - Потоки умирают через 60 сек
         * - Bounded queue
         * - Abort policy для явного failure
         */
        fun createIOExecutor(): ExecutorService {
            return ThreadPoolExecutor(
                0,                               // no core threads
                CPU_COUNT * 2,                   // max для IO
                60L,                             // idle threads умирают
                TimeUnit.SECONDS,
                LinkedBlockingQueue(100),
                NamedThreadFactory("io", daemon = true),
                ThreadPoolExecutor.AbortPolicy()
            )
        }

        /**
         * Создаёт executor для realtime задач
         * - Приоритетная очередь
         * - DiscardOldestPolicy для latest data
         * - Высокий приоритет потоков
         */
        fun createRealtimeExecutor(): ExecutorService {
            return ThreadPoolExecutor(
                1,                               // single thread
                1,
                0L,
                TimeUnit.MILLISECONDS,
                PriorityBlockingQueue(50),
                object : ThreadFactory {
                    private val count = AtomicInteger(1)
                    override fun newThread(r: Runnable) = Thread(r, "realtime-${count.getAndIncrement()}").apply {
                        priority = Thread.MAX_PRIORITY
                        isDaemon = true
                    }
                },
                ThreadPoolExecutor.DiscardOldestPolicy()
            )
        }
    }
}

// Использование:
val computeExecutor = CustomExecutorFactory.createComputeExecutor()
val ioExecutor = CustomExecutorFactory.createIOExecutor()
```

### AppExecutors Singleton

```kotlin
/**
 * Singleton для централизованного управления executors в приложении
 */
object AppExecutors {
    private val CPU_COUNT = Runtime.getRuntime().availableProcessors()

    /**
     * Для последовательных disk операций (database, file I/O)
     */
    val diskIO: Executor by lazy {
        Executors.newSingleThreadExecutor(
            NamedThreadFactory("disk-io", daemon = true)
        )
    }

    /**
     * Для network запросов (ограничен для защиты сервера)
     */
    val networkIO: Executor by lazy {
        ThreadPoolExecutor(
            0,
            3,
            60L, TimeUnit.SECONDS,
            SynchronousQueue<Runnable>(),
            NamedThreadFactory("network-io", daemon = true),
            RateLimitedRejectionHandler(diskIO) // custom handler
        )
    }

    /**
     * Для CPU-intensive вычислений
     */
    val computation: Executor by lazy {
        ThreadPoolExecutor(
            CPU_COUNT,
            CPU_COUNT,
            0L, TimeUnit.MILLISECONDS,
            LinkedBlockingQueue(128),
            NamedThreadFactory("computation", daemon = true),
            ThreadPoolExecutor.CallerRunsPolicy()
        )
    }

    /**
     * Для выполнения на main thread
     */
    val mainThread: Executor by lazy {
        MainThreadExecutor()
    }

    /**
     * Main thread executor
     */
    private class MainThreadExecutor : Executor {
        private val handler = Handler(Looper.getMainLooper())

        override fun execute(command: Runnable) {
            if (Looper.myLooper() == Looper.getMainLooper()) {
                // Уже на main thread
                command.run()
            } else {
                handler.post(command)
            }
        }
    }

    /**
     * Custom rejection handler с rate limiting logging
     */
    private class RateLimitedRejectionHandler(
        private val fallbackExecutor: Executor
    ) : RejectedExecutionHandler {
        private var lastLogTime = 0L
        private val logThrottleMs = 5000L // Лог не чаще раза в 5 сек

        override fun rejectedExecution(r: Runnable, executor: ThreadPoolExecutor) {
            val now = System.currentTimeMillis()
            if (now - lastLogTime > logThrottleMs) {
                Log.w("AppExecutors",
                    "Task rejected - queue: ${executor.queue.size}, " +
                    "active: ${executor.activeCount}, " +
                    "pool: ${executor.poolSize}/${executor.maximumPoolSize}")
                lastLogTime = now
            }

            // Fallback на другой executor
            try {
                fallbackExecutor.execute(r)
            } catch (e: RejectedExecutionException) {
                Log.e("AppExecutors", "Fallback executor also rejected task", e)
            }
        }
    }

    /**
     * Named thread factory
     */
    private class NamedThreadFactory(
        private val namePrefix: String,
        private val daemon: Boolean = false
    ) : ThreadFactory {
        private val threadNumber = AtomicInteger(1)

        override fun newThread(r: Runnable): Thread {
            return Thread(r, "$namePrefix-${threadNumber.getAndIncrement()}").apply {
                isDaemon = daemon
                if (priority != Thread.NORM_PRIORITY) {
                    priority = Thread.NORM_PRIORITY
                }
            }
        }
    }
}
```

### Executor + LiveData в Repository

```kotlin
/**
 * Repository с executor и LiveData интеграцией
 */
class ProductRepository(
    private val productDao: ProductDao,
    private val productApi: ProductApi,
    private val executors: AppExecutors = AppExecutors
) {
    /**
     * Загружает продукты с network-first стратегией
     */
    fun loadProducts(): LiveData<Resource<List<Product>>> {
        val result = MediatorLiveData<Resource<List<Product>>>()

        // Показываем loading
        result.value = Resource.Loading()

        // Сначала пытаемся загрузить с сервера
        executors.networkIO.execute {
            try {
                val products = productApi.getProducts()

                // Сохраняем в БД
                executors.diskIO.execute {
                    productDao.insertAll(products)

                    // LiveData автоматически триггерит обновление
                    executors.mainThread.execute {
                        result.value = Resource.Success(products)
                    }
                }
            } catch (e: Exception) {
                // Network failed, fallback на кеш
                executors.diskIO.execute {
                    val cachedProducts = productDao.getAllProducts()

                    executors.mainThread.execute {
                        if (cachedProducts.isNotEmpty()) {
                            result.value = Resource.Success(cachedProducts)
                        } else {
                            result.value = Resource.Error("No cached data", e)
                        }
                    }
                }
            }
        }

        return result
    }

    /**
     * Поиск продуктов с debounce
     */
    fun searchProducts(query: String): LiveData<List<Product>> {
        val result = MutableLiveData<List<Product>>()

        executors.diskIO.execute {
            // Simulate debounce
            Thread.sleep(300)

            val products = productDao.searchProducts("%$query%")
            result.postValue(products)
        }

        return result
    }

    /**
     * Обновление продукта с callback
     */
    fun updateProduct(
        product: Product,
        onSuccess: () -> Unit,
        onError: (Exception) -> Unit
    ) {
        executors.networkIO.execute {
            try {
                productApi.updateProduct(product)

                executors.diskIO.execute {
                    productDao.update(product)

                    executors.mainThread.execute {
                        onSuccess()
                    }
                }
            } catch (e: Exception) {
                executors.mainThread.execute {
                    onError(e)
                }
            }
        }
    }
}

// Resource wrapper
sealed class Resource<T>(
    val data: T? = null,
    val error: Throwable? = null
) {
    class Loading<T> : Resource<T>()
    class Success<T>(data: T) : Resource<T>(data)
    class Error<T>(message: String, error: Throwable? = null, data: T? = null) :
        Resource<T>(data, error)
}
```

### Scheduled Tasks

```kotlin
/**
 * Менеджер для периодических задач
 */
class ScheduledTasksManager {
    private val scheduler = Executors.newScheduledThreadPool(2,
        NamedThreadFactory("scheduler", daemon = true)
    )

    private val scheduledTasks = ConcurrentHashMap<String, ScheduledFuture<*>>()

    /**
     * Запускает периодическую синхронизацию
     */
    fun startPeriodicSync(intervalMinutes: Long) {
        val future = scheduler.scheduleWithFixedDelay({
            try {
                performSync()
            } catch (e: Exception) {
                Log.e("Scheduler", "Sync failed", e)
            }
        }, 0, intervalMinutes, TimeUnit.MINUTES)

        scheduledTasks["sync"] = future
    }

    /**
     * Запускает проверку health с фиксированной частотой
     */
    fun startHealthCheck() {
        val future = scheduler.scheduleAtFixedRate({
            try {
                checkApplicationHealth()
            } catch (e: Exception) {
                Log.e("Scheduler", "Health check failed", e)
            }
        }, 10, 60, TimeUnit.SECONDS)

        scheduledTasks["health"] = future
    }

    /**
     * Планирует отложенную задачу
     */
    fun scheduleDelayed(delaySeconds: Long, task: () -> Unit) {
        scheduler.schedule({
            try {
                task()
            } catch (e: Exception) {
                Log.e("Scheduler", "Delayed task failed", e)
            }
        }, delaySeconds, TimeUnit.SECONDS)
    }

    /**
     * Retry механизм с exponential backoff
     */
    fun scheduleWithRetry(
        maxRetries: Int = 3,
        initialDelaySeconds: Long = 1,
        task: () -> Boolean // true = success, false = retry
    ) {
        var attempt = 0

        fun scheduleAttempt() {
            if (attempt >= maxRetries) {
                Log.e("Scheduler", "Max retries reached")
                return
            }

            val delay = initialDelaySeconds * (1 shl attempt) // exponential: 1, 2, 4, 8...

            scheduler.schedule({
                try {
                    val success = task()
                    if (!success) {
                        attempt++
                        scheduleAttempt()
                    }
                } catch (e: Exception) {
                    Log.e("Scheduler", "Retry attempt $attempt failed", e)
                    attempt++
                    scheduleAttempt()
                }
            }, delay, TimeUnit.SECONDS)
        }

        scheduleAttempt()
    }

    /**
     * Отменяет конкретную задачу
     */
    fun cancelTask(taskId: String) {
        scheduledTasks[taskId]?.cancel(false)
        scheduledTasks.remove(taskId)
    }

    /**
     * Останавливает все задачи
     */
    fun shutdown() {
        scheduledTasks.values.forEach { it.cancel(false) }
        scheduledTasks.clear()

        scheduler.shutdown()
        try {
            if (!scheduler.awaitTermination(5, TimeUnit.SECONDS)) {
                scheduler.shutdownNow()
            }
        } catch (e: InterruptedException) {
            scheduler.shutdownNow()
            Thread.currentThread().interrupt()
        }
    }

    private fun performSync() {
        Log.d("Scheduler", "Performing sync...")
    }

    private fun checkApplicationHealth() {
        Log.d("Scheduler", "Checking health...")
    }
}

// Использование:
class MyApplication : Application() {
    private val scheduledTasksManager = ScheduledTasksManager()

    override fun onCreate() {
        super.onCreate()

        // Запускаем периодические задачи
        scheduledTasksManager.startPeriodicSync(intervalMinutes = 30)
        scheduledTasksManager.startHealthCheck()

        // Отложенная задача
        scheduledTasksManager.scheduleDelayed(60) {
            performInitialSetup()
        }

        // Retry с backoff
        scheduledTasksManager.scheduleWithRetry(maxRetries = 5) {
            attemptConnection()
        }
    }

    override fun onTerminate() {
        super.onTerminate()
        scheduledTasksManager.shutdown()
    }
}
```

## Проверь Себя

### Вопрос 1: corePoolSize vs maximumPoolSize

**Вопрос:** Чем принципиально отличается corePoolSize от maximumPoolSize в ThreadPoolExecutor? Когда создаются потоки сверх corePoolSize?

<details>
<summary>Ответ</summary>

**Ключевые отличия:**

1. **corePoolSize** — минимальное число потоков, которые:
   - Создаются по мере поступления задач (lazy)
   - Живут постоянно даже если idle (если не установлен `allowCoreThreadTimeOut`)
   - НЕ умирают после keepAliveTime
   - Представляют "базовый" размер пула

2. **maximumPoolSize** — максимальное число потоков, которые:
   - Создаются только когда очередь полностью заполнена
   - Умирают после keepAliveTime бездействия
   - Представляют пиковую capacity пула

**Порядок создания потоков:**

1. Задача поступает, текущее число потоков < corePoolSize → создать новый core поток
2. Все core потоки заняты → задача идёт в очередь
3. Очередь заполнена + текущее число потоков < maximumPoolSize → создать новый "extra" поток
4. Достигнут maximumPoolSize + очередь полна → RejectedExecutionHandler

**Пример:**
```kotlin
val executor = ThreadPoolExecutor(
    2,    // corePoolSize
    5,    // maximumPoolSize
    60L, TimeUnit.SECONDS,
    LinkedBlockingQueue(10)
)

// Задачи 1-2: создаются 2 core потока
// Задачи 3-12: идут в очередь (capacity = 10)
// Задача 13: очередь полна, создаётся 3-й поток (extra)
// Задачи 14-15: создаются 4-й и 5-й потоки (достигнут max)
// Задача 16: reject (все потоки заняты, очередь полна)
// Через 60 сек idle: потоки 3-5 умирают, остаются 1-2
```

</details>

### Вопрос 2: Опасности newCachedThreadPool()

**Вопрос:** Почему `Executors.newCachedThreadPool()` опасен для Android приложений? Приведите конкретный сценарий катастрофы.

<details>
<summary>Ответ</summary>

**Почему опасен:**

`newCachedThreadPool()` создан как:
```kotlin
ThreadPoolExecutor(
    0,                    // corePoolSize = 0
    Integer.MAX_VALUE,    // maximumPoolSize = unbounded!
    60L, TimeUnit.SECONDS,
    SynchronousQueue()    // нет очереди, прямая передача
)
```

**Проблемы:**

1. **Unbounded thread creation**: Нет лимита на число потоков
2. **SynchronousQueue**: Каждая задача требует свободный поток или создаёт новый
3. **Memory exhaustion**: Каждый поток ~1MB stack + overhead
4. **CPU thrashing**: Context switching убивает performance

**Сценарий катастрофы:**

```kotlin
val executor = Executors.newCachedThreadPool()

// User быстро скроллит RecyclerView с 10000 элементами
recyclerView.adapter = object : RecyclerView.Adapter<VH>() {
    override fun onBindViewHolder(holder: VH, position: Int) {
        executor.execute {
            // Загрузка и decode изображения (3 секунды)
            val bitmap = loadAndDecodeImage(items[position].imageUrl)
            runOnUiThread {
                holder.imageView.setImageBitmap(bitmap)
            }
        }
    }
}

// Результат:
// - User скроллит через 1000 элементов за 10 секунд
// - Каждый bind триггерит новую задачу
// - Задачи выполняются 3 секунды каждая
// - За 10 секунд накопится ~3000 активных потоков
// - 3000 threads * 1MB = ~3GB RAM
// - OutOfMemoryError → crash
```

**Безопасная альтернатива:**

```kotlin
val executor = ThreadPoolExecutor(
    0,
    10,  // Разумный лимит
    60L, TimeUnit.SECONDS,
    LinkedBlockingQueue(50),
    ThreadPoolExecutor.DiscardOldestPolicy() // Сбрасываем старые
)
```

</details>

### Вопрос 3: CallerRunsPolicy

**Вопрос:** Когда `ThreadPoolExecutor.CallerRunsPolicy()` может быть полезна, и когда она категорически опасна в Android?

<details>
<summary>Ответ</summary>

**Что делает CallerRunsPolicy:**

При reject задачи (пул занят, очередь полна) задача выполняется в потоке, который вызвал `execute()`.

**Когда полезна:**

1. **Естественный throttling**:
```kotlin
// Producer-consumer в фоновых потоках
val executor = ThreadPoolExecutor(
    2, 2, 0L, TimeUnit.MILLISECONDS,
    LinkedBlockingQueue(10),
    CallerRunsPolicy()
)

thread(name = "producer") {
    while (true) {
        executor.execute {
            processItem()  // Если пул занят, processItem выполнится в producer
        }
        // Producer автоматически замедляется когда consumer не успевает
    }
}
```

2. **Graceful degradation** для non-critical задач:
```kotlin
// Analytics events
analyticsExecutor.execute {
    sendAnalyticsEvent()  // Если очередь полна, отправим в текущем потоке
}
```

**Когда ОПАСНА:**

1. **Вызов из main thread**:
```kotlin
// ОПАСНО!
button.setOnClickListener {
    heavyTaskExecutor.execute {
        performHeavyComputation()  // Если reject → выполнится на main thread!
    }
    // UI заморозится
}
```

2. **Долгие задачи**:
```kotlin
// ОПАСНО!
executor.execute {
    downloadLargeFile()  // Если reject → caller блокируется на скачивание
}
```

3. **Time-sensitive caller**:
```kotlin
// ОПАСНО!
override fun onSensorChanged(event: SensorEvent) {
    sensorExecutor.execute {
        processSensorData(event)  // Если reject → пропустим следующие события
    }
}
```

**Правила безопасности:**

- ✅ Используйте если caller — фоновый поток и может блокироваться
- ✅ Используйте для естественного backpressure в producer-consumer
- ❌ НЕ используйте если caller может быть main thread
- ❌ НЕ используйте для долгих или blocking операций
- ❌ НЕ используйте для realtime/time-sensitive систем

**Безопасная альтернатива для UI:**

```kotlin
button.setOnClickListener {
    try {
        executor.execute {
            performTask()
        }
    } catch (e: RejectedExecutionException) {
        Toast.makeText(this, "Too busy, try later", Toast.LENGTH_SHORT).show()
    }
}
```

</details>

### Вопрос 4: Graceful Shutdown

**Вопрос:** Как правильно выполнить graceful shutdown ExecutorService? Что произойдёт если просто вызвать `shutdown()` и забыть?

<details>
<summary>Ответ</summary>

**Правильный graceful shutdown:**

```kotlin
fun shutdownExecutor(executor: ExecutorService, timeoutSeconds: Long = 60) {
    // Шаг 1: Запретить принимать новые задачи
    executor.shutdown()

    try {
        // Шаг 2: Дождаться завершения running задач
        if (!executor.awaitTermination(timeoutSeconds, TimeUnit.SECONDS)) {
            // Шаг 3: Если таймаут, форсированное завершение
            val notExecuted = executor.shutdownNow()
            Log.w("Shutdown", "${notExecuted.size} tasks were not executed")

            // Шаг 4: Дать время на interrupt handling
            if (!executor.awaitTermination(timeoutSeconds, TimeUnit.SECONDS)) {
                Log.e("Shutdown", "Executor did not terminate")
            }
        }
    } catch (e: InterruptedException) {
        // Шаг 5: Текущий поток interrupted
        executor.shutdownNow()
        Thread.currentThread().interrupt() // Preserve interrupt status
    }
}
```

**Что произойдёт при просто shutdown():**

```kotlin
executor.shutdown()  // И всё?
```

**Проблемы:**

1. **Running задачи продолжают работу**:
```kotlin
executor.execute {
    while (true) {
        // Бесконечный цикл продолжит работу!
        doWork()
    }
}
executor.shutdown()  // Поток продолжает жить
```

2. **Ресурсы не освобождены**:
```kotlin
class MyViewModel : ViewModel() {
    private val executor = Executors.newFixedThreadPool(4)

    override fun onCleared() {
        executor.shutdown()  // Потоки продолжают работу
        // ViewModel уничтожена, но потоки живы → memory leak
    }
}
```

3. **Pending задачи остаются в очереди**:
```kotlin
executor.execute { saveImportantData1() }
executor.execute { saveImportantData2() }
executor.shutdown()  // Задачи в очереди не выполнены!
```

**Разница shutdown() vs shutdownNow():**

| Метод | Новые задачи | Queued задачи | Running задачи |
|-------|--------------|---------------|----------------|
| `shutdown()` | Reject | Выполнятся | Продолжат работу |
| `shutdownNow()` | Reject | Возвращаются как List | Interrupt (если проверяют) |

**Корректная обработка interrupt:**

```kotlin
executor.execute {
    try {
        while (!Thread.currentThread().isInterrupted) {
            doWork()
        }
    } catch (e: InterruptedException) {
        Thread.currentThread().interrupt()  // Restore flag
        Log.d("Task", "Interrupted, cleaning up...")
    }
}
```

**Рекомендации для Android:**

```kotlin
// ViewModel
override fun onCleared() {
    executor.shutdown()
    // Короткий timeout, ViewModel cleanup не должна блокировать
    executor.awaitTermination(1, TimeUnit.SECONDS)
}

// Activity
override fun onDestroy() {
    executor.shutdown()
    if (isFinishing) {
        executor.shutdownNow()  // Форсированно при финальном destroy
    }
}

// Application-wide executors
// НЕ shutdown, они живут весь lifecycle приложения
```

</details>

### Вопрос 5: CPU-bound Threading

**Вопрос:** Сколько потоков оптимально для CPU-bound задач и почему? Что произойдёт если сделать пул в 2 раза больше?

<details>
<summary>Ответ</summary>

**Оптимальное число для CPU-bound:**

```kotlin
val cpuCount = Runtime.getRuntime().availableProcessors()
val executor = Executors.newFixedThreadPool(cpuCount)

// Для типичного устройства (8 cores): 8 потоков
```

**Теория:**

CPU-bound задача — задача, которая постоянно использует CPU (вычисления, encoding, parsing), минимально блокируется на IO.

**Формула Little's Law:**
```
Optimal threads = CPU cores × (1 + wait_time / compute_time)
```

Для pure CPU-bound: wait_time ≈ 0
```
Optimal threads = CPU cores × (1 + 0) = CPU cores
```

**Почему ровно CPU cores:**

1. **Максимальная утилизация**: Каждый core занят выполнением полезной работы
2. **Минимальный context switching**: OS scheduler не должен часто переключаться
3. **Минимальный overhead**: Нет лишних потоков, нет лишней памяти

**Что если сделать в 2 раза больше (2 × CPU):**

```kotlin
// Плохая идея для CPU-bound
val executor = Executors.newFixedThreadPool(cpuCount * 2)
```

**Последствия:**

1. **Context switching overhead**:
```
8 cores, 16 потоков CPU-bound задач
Каждый поток хочет CPU постоянно
OS вынужден переключать контекст каждые несколько миллисекунд
Context switch стоит ~1-10 микросекунд + cache invalidation
При 16 потоках на 8 cores: постоянное switching
Потеря performance ~10-30%
```

2. **Cache thrashing**:
```
Каждый context switch инвалидирует L1/L2 cache
Новый поток должен прогреть cache заново
CPU-bound задачи сильно зависят от cache
Результат: больше cache misses → медленнее
```

3. **Scheduling latency**:
```
Каждый поток получает меньше времени CPU
Больше времени тратится на scheduling решения
Общая throughput падает
```

**Benchmark пример:**

```kotlin
// Тест: вычисление 1000 SHA-256 хешей
fun benchmark(threadCount: Int): Long {
    val executor = Executors.newFixedThreadPool(threadCount)
    val start = System.currentTimeMillis()

    val futures = (1..1000).map {
        executor.submit {
            MessageDigest.getInstance("SHA-256")
                .digest(ByteArray(1024))
        }
    }

    futures.forEach { it.get() }

    val duration = System.currentTimeMillis() - start
    executor.shutdown()
    return duration
}

// На устройстве с 8 cores:
benchmark(4)  // ~2000ms (underutilized)
benchmark(8)  // ~1000ms (оптимально!)
benchmark(16) // ~1200ms (context switch overhead)
benchmark(32) // ~1500ms (thrashing)
```

**Исключения когда можно больше:**

1. **Смешанная нагрузка** (CPU + некоторое IO):
```kotlin
val executor = Executors.newFixedThreadPool(cpuCount + 1)
// +1 для компенсации редких блокировок
```

2. **User responsiveness**:
```kotlin
// На Android для UI responsiveness
val executor = Executors.newFixedThreadPool(cpuCount + 2)
// Даже если все потоки заняты, новая задача стартует быстро
```

3. **Короткие burst задачи**:
```kotlin
// Если задачи очень короткие (<1ms)
val executor = Executors.newFixedThreadPool(cpuCount * 1.5)
// Компенсирует overhead между задачами
```

**Рекомендации:**

- **Pure CPU-bound**: `n_threads = n_cpu`
- **CPU-bound с редкими блокировками**: `n_threads = n_cpu + 1`
- **Mixed workload**: профилировать и настраивать
- **НЕ делать**: `n_threads >> n_cpu` для CPU-bound

</details>

## Связи

### android-async-evolution
Executors представляют собой важный этап в эволюции асинхронного программирования на Android. До Executors разработчики использовали низкоуровневые `Thread` и `AsyncTask` (устарел). Executors стали первой высокоуровневой абстракцией из `java.util.concurrent`, которая позволила эффективно управлять пулами потоков. Позднее появились RxJava (reactive подход) и Kotlin Coroutines (structured concurrency). Понимание Executors критично для миграции legacy кода и интеграции с библиотеками, которые ещё не перешли на Coroutines.

### android-threading
Executors — это конкретная реализация многопоточности на Android. В то время как threading концепции описывают общие принципы (main thread, background threads, Handler, Looper), Executors предоставляют практический инструмент для выполнения задач в фоновых потоках. ThreadPoolExecutor является альтернативой HandlerThread для случаев когда не нужна message queue, но нужен контроль над потоками. AppExecutors паттерн из Architecture Components стал стандартом для организации threading в Android приложениях до появления Coroutines.

### os-processes-threads
Executors построены поверх OS-level потоков. Каждый Thread в Java ThreadPoolExecutor — это native OS thread (pthread на Linux/Android). Понимание как OS создаёт потоки, управляет их stack memory (~1MB per thread), выполняет context switching, и распределяет CPU time через scheduler критично для правильной настройки ThreadPoolExecutor параметров (corePoolSize, maximumPoolSize, keepAliveTime). Неправильная конфигурация может привести к thread explosion и исчерпанию OS ресурсов.

### os-scheduling
OS scheduler напрямую влияет на performance ThreadPoolExecutor. Когда пул имеет больше потоков чем CPU cores, OS scheduler должен постоянно выполнять context switching. Каждый switch стоит CPU cycles и инвалидирует cache. Для CPU-bound задач оптимальное число потоков = CPU cores именно из-за минимизации scheduling overhead. Для IO-bound задач можно больше потоков, так как они большую часть времени блокируются и не конкурируют за CPU. Приоритеты потоков (Thread.setPriority) также влияют на scheduling decisions.

---

## Источники и дальнейшее чтение

### Книги

- **Goetz B. (2006)** *Java Concurrency in Practice* — фундаментальная книга по Executors, ThreadPoolExecutor и java.util.concurrent. Главы 6-8 подробно описывают task execution, thread pools и их правильную конфигурацию. Обязательное чтение для глубокого понимания Executors.
- **Bloch J. (2018)** *Effective Java* — Item 80 "Prefer executors, tasks, and streams to threads" и Item 81 "Prefer concurrency utilities to wait and notify" напрямую относятся к теме.
- **Moskala M. (2022)** *Kotlin Coroutines: Deep Dive* — объясняет, как Dispatchers.IO и Dispatchers.Default используют ThreadPoolExecutor под капотом, и почему Coroutines заменили Executors в современном Android.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*

