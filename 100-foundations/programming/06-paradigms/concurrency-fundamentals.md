---
title: "Concurrency Fundamentals: потоки, корутины, синхронизация"
created: 2025-12-22
modified: 2026-02-19
type: deep-dive
status: draft
confidence: high
tags:
  - topic/programming
  - deep-dive/paradigms
  - concurrency
  - parallelism
  - coroutines
  - threads
  - level/intermediate
related:
  - "[[programming-overview]]"
  - "[[jvm-concurrency-overview]]"
  - "[[architecture-resilience-patterns]]"
  - "[[functional-programming]]"
prerequisites:
  - "[[os-processes-threads]]"
  - "[[solid-principles]]"
reading_time: 30
difficulty: 6
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Concurrency Fundamentals: потоки, корутины, синхронизация

> Concurrency is about dealing with lots of things at once. Parallelism is about doing lots of things at once. --- Rob Pike

---

## Исторический контекст

Проблема concurrent programming возникла с появлением многозадачных операционных систем в 1960-х. **Edsger Dijkstra** (1965) формализовал проблему взаимного исключения и предложил **семафоры** (semaphores) как примитив синхронизации в статье "Solution of a Problem in Concurrent Programming Control". Он же сформулировал проблему "обедающих философов" (1971), ставшую каноническим примером deadlock.

**C.A.R. Hoare** (1974) предложил **мониторы** (monitors) --- более структурированный подход к синхронизации, объединяющий данные и операции над ними с автоматической блокировкой. Мониторы легли в основу synchronized-блоков Java и lock-механизмов в большинстве современных языков. Позже Hoare (1978) описал **Communicating Sequential Processes (CSP)** --- формальный язык для описания concurrency через обмен сообщениями, а не через разделяемую память.

**Leslie Lamport** (1978) ввёл концепцию **happens-before** и логических часов, которые стали основой для рассуждения о порядке событий в распределённых системах. Его работы по Paxos (1998) и Byzantine fault tolerance заложили фундамент для distributed consensus.

В 2000-х произошёл "concurrency revolution": закон Мура перестал давать прирост тактовой частоты, и индустрия перешла к многоядерным процессорам. Rob Pike (2012) в докладе "Concurrency is not Parallelism" чётко разделил эти концепции, а язык Go (2009) воплотил идеи CSP в goroutines и channels. **Kotlin coroutines** (2018) привнесли structured concurrency --- иерархию корутин с автоматическим управлением жизненным циклом. Java virtual threads (Project Loom, 2023), Swift structured concurrency (2021) --- все они наследники этих фундаментальных идей.

---

## TL;DR

- **Concurrency** --- структурирование программы для работы с несколькими задачами
- **Parallelism** --- одновременное выполнение на нескольких CPU cores
- **Kotlin coroutines** --- легковесные "потоки" с structured concurrency
- **Race condition** --- баг из-за непредсказуемого порядка операций
- **Structured concurrency** --- иерархия корутин: parent управляет жизнью children
- **Channel** --- примитив обмена данными между корутинами (CSP)
- **Flow** --- холодный асинхронный поток данных (reactive streams)

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Thread** | Поток выполнения внутри процесса |
| **Process** | Изолированная единица выполнения с своей памятью |
| **Coroutine** | Легковесная единица конкурентного выполнения в Kotlin |
| **Race Condition** | Баг из-за timing-зависимости |
| **Deadlock** | Взаимная блокировка потоков |
| **Mutex** | Mutual Exclusion --- блокировка ресурса |
| **Semaphore** | Ограничение числа одновременных доступов |
| **Atomic** | Операция, выполняемая как единое целое |
| **Dispatcher** | Определяет, на каком потоке/пуле выполняется корутина |
| **Structured concurrency** | Иерархия корутин с автоматической отменой |
| **Channel** | Примитив для передачи данных между корутинами |
| **Flow** | Холодный асинхронный поток данных |
| **Suspension point** | Точка, где корутина может приостановиться без блокировки потока |

---

## Concurrency vs Parallelism

```
+----------------------------------------------------------------------------+
|                 CONCURRENCY vs PARALLELISM                                 |
+----------------------------------------------------------------------------+
|                                                                            |
|  CONCURRENCY (структура)                                                   |
|  +----------------------------------------------------------------------+  |
|  |                                                                      |  |
|  |  1 CPU, 3 Tasks (time-slicing)                                       |  |
|  |                                                                      |  |
|  |  Time: ---------------------------------------------------->         |  |
|  |                                                                      |  |
|  |  CPU:  [T1][T2][T1][T3][T1][T2][T3][T1][T2][T3]                     |  |
|  |                                                                      |  |
|  |  Tasks switch rapidly -> appears simultaneous                        |  |
|  |  Good for: I/O-bound work (waiting for network, disk)                |  |
|  |                                                                      |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|  PARALLELISM (исполнение)                                                  |
|  +----------------------------------------------------------------------+  |
|  |                                                                      |  |
|  |  4 CPUs, 4 Tasks (truly simultaneous)                                |  |
|  |                                                                      |  |
|  |  Time: ---------------------------------------------------->         |  |
|  |                                                                      |  |
|  |  CPU1: [-------------- Task 1 ---------------]                       |  |
|  |  CPU2: [-------------- Task 2 ---------------]                       |  |
|  |  CPU3: [-------------- Task 3 ---------------]                       |  |
|  |  CPU4: [-------------- Task 4 ---------------]                       |  |
|  |                                                                      |  |
|  |  Actually runs at the same time                                      |  |
|  |  Good for: CPU-bound work (calculations)                             |  |
|  |                                                                      |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|  KEY INSIGHT:                                                              |
|  * Concurrency = dealing with multiple things (design)                     |
|  * Parallelism = doing multiple things (execution)                         |
|  * Can have concurrency without parallelism (single core)                  |
|  * Parallelism requires concurrency structure                              |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## Threading Models

```
+----------------------------------------------------------------------------+
|                      THREADING MODELS                                      |
+----------------------------------------------------------------------------+
|                                                                            |
|  1. OS THREADS (1:1)                                                       |
|  +----------------------------------------------------------------------+  |
|  |  User Thread --------------------------> Kernel Thread                |  |
|  |                                                                      |  |
|  |  * Java (classic), C++, Rust (std::thread)                           |  |
|  |  * Heavy (~1MB stack per thread)                                     |  |
|  |  * Expensive context switch                                          |  |
|  |  * True parallelism                                                  |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|  2. GREEN THREADS / COROUTINES (M:N)                                       |
|  +----------------------------------------------------------------------+  |
|  |  Many Coroutines ----------------------> Few OS Threads               |  |
|  |                                                                      |  |
|  |  +---+ +---+ +---+ +---+                                            |  |
|  |  | C | | C | | C | | C |   Coroutines / Green threads               |  |
|  |  +-+-+ +-+-+ +-+-+ +-+-+   (lightweight, ~few hundred bytes)        |  |
|  |    +-----+-----+-----+                                              |  |
|  |          v                                                           |  |
|  |       +-----+ +-----+                                               |  |
|  |       | OS  | | OS  |     OS threads                                 |  |
|  |       +-----+ +-----+                                               |  |
|  |                                                                      |  |
|  |  * Kotlin coroutines, Go goroutines, Java 21+ virtual threads        |  |
|  |  * Lightweight (~hundreds of bytes per coroutine)                    |  |
|  |  * Cheap context switch (no kernel transition)                       |  |
|  |  * Runtime manages scheduling                                        |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|  3. EVENT LOOP (Single-threaded async)                                     |
|  +----------------------------------------------------------------------+  |
|  |                                                                      |  |
|  |     +---------------------------------------------+                 |  |
|  |     |             EVENT LOOP                       |                 |  |
|  |     |                                              |                 |  |
|  |     |  while (events.hasNext()) {                  |                 |  |
|  |     |      event = events.next()                   |                 |  |
|  |     |      handler(event)  // non-blocking         |                 |  |
|  |     |  }                                           |                 |  |
|  |     |                                              |                 |  |
|  |     +---------------------------------------------+                 |  |
|  |                                                                      |  |
|  |  * JavaScript (Node.js), Python (asyncio)                            |  |
|  |  * Single thread, non-blocking I/O                                   |  |
|  |  * Callbacks/Promises/async-await                                    |  |
|  |  * No parallelism for CPU-bound work                                 |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
+----------------------------------------------------------------------------+
```

---

## Kotlin Threads: базовый уровень

Kotlin работает на JVM и имеет полный доступ к Java-потокам. Однако чистые потоки --- низкоуровневый инструмент, и в большинстве случаев предпочтительнее корутины.

```kotlin
import kotlin.concurrent.thread

// ---- Создание потока через Kotlin API ----

fun main() {
    val t = thread(name = "worker") {
        println("Running on: ${Thread.currentThread().name}")
        Thread.sleep(1000)
        println("Done")
    }

    println("Main thread: ${Thread.currentThread().name}")
    t.join()  // Ждём завершения
    println("Worker finished")
}

// ---- Проблема потоков: они тяжёлые ----

fun heavyThreads() {
    // Создать 100_000 потоков --- OutOfMemoryError!
    // Каждый поток ~1MB стека
    val threads = (1..100_000).map {
        thread {
            Thread.sleep(5000)
        }
    }
    threads.forEach { it.join() }
}

// ---- Корутины: 100_000 --- без проблем ----

suspend fun lightweightCoroutines() = coroutineScope {
    // 100_000 корутин --- OK, каждая ~несколько сот байт
    val jobs = (1..100_000).map {
        launch {
            delay(5000)
        }
    }
    jobs.forEach { it.join() }
}
```

---

## Kotlin Coroutines: основная модель

Корутины --- первичная модель concurrency в Kotlin. Они легковесные, поддерживают structured concurrency и не блокируют потоки при ожидании.

```
+----------------------------------------------------------------------------+
|                  COROUTINE LIFECYCLE                                        |
+----------------------------------------------------------------------------+
|                                                                            |
|  launch { }                                                                |
|      |                                                                     |
|      v                                                                     |
|  [NEW] ----start()----> [ACTIVE] ----complete----> [COMPLETED]             |
|                             |                                              |
|                             | cancel()                                     |
|                             v                                              |
|                        [CANCELLING] ----cleanup----> [CANCELLED]           |
|                                                                            |
|  Structured concurrency:                                                   |
|  * Parent waits for all children                                           |
|  * Cancelling parent cancels all children                                  |
|  * Child failure cancels parent (unless SupervisorJob)                     |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Базовые конструкции

```kotlin
import kotlinx.coroutines.*

// ---- launch: fire-and-forget, возвращает Job ----

fun main() = runBlocking {
    val job: Job = launch {
        delay(1000)
        println("World!")
    }
    println("Hello,")
    job.join()
}
// Hello,
// World!

// ---- async: возвращает Deferred<T> (future с результатом) ----

fun main() = runBlocking {
    val deferred: Deferred<Int> = async {
        delay(1000)
        42
    }
    println("Computing...")
    val result = deferred.await()
    println("Result: $result")
}

// ---- Параллельное выполнение через async ----

suspend fun fetchUserData(userId: String): UserData = coroutineScope {
    val profile = async { fetchProfile(userId) }
    val orders = async { fetchOrders(userId) }
    val recommendations = async { fetchRecommendations(userId) }

    UserData(
        profile = profile.await(),
        orders = orders.await(),
        recommendations = recommendations.await()
    )
    // Все три запроса выполняются параллельно
    // coroutineScope ждёт завершения всех children
}
```

### Structured Concurrency

```kotlin
// ---- Structured concurrency: иерархия parent-child ----

suspend fun processOrder(order: Order) = coroutineScope {
    // coroutineScope создаёт scope и ждёт всех children

    val validation = async { validateOrder(order) }
    val inventory = async { checkInventory(order.items) }

    // Если validateOrder бросит исключение:
    // 1. checkInventory будет автоматически отменён
    // 2. coroutineScope пробросит исключение
    // 3. Никаких утечек корутин

    val isValid = validation.await()
    val hasStock = inventory.await()

    if (isValid && hasStock) {
        launch { sendConfirmationEmail(order) }
        launch { updateInventory(order) }
    }
}

// ---- supervisorScope: child failure не убивает parent ----

suspend fun fetchDashboardData(): DashboardData = supervisorScope {
    val news = async { fetchNews() }
    val weather = async { fetchWeather() }
    val stocks = async { fetchStocks() }

    DashboardData(
        news = runCatching { news.await() }.getOrDefault(emptyList()),
        weather = runCatching { weather.await() }.getOrNull(),
        stocks = runCatching { stocks.await() }.getOrDefault(emptyList())
    )
    // Если fetchWeather() упадёт --- остальные продолжат работу
}
```

### Dispatchers: где выполняется корутина

```kotlin
import kotlinx.coroutines.*

// ---- Dispatchers ----

suspend fun example() = coroutineScope {

    // Default: пул потоков = количество CPU cores
    // Для: CPU-intensive вычисления
    launch(Dispatchers.Default) {
        val result = (1..1_000_000).map { it * it }.sum()
    }

    // IO: пул до 64 потоков (или больше)
    // Для: сетевые запросы, файловый I/O, работа с БД
    launch(Dispatchers.IO) {
        val data = readFile("large-file.txt")
        val response = httpClient.get("https://api.example.com")
    }

    // Main: UI-поток (Android, JavaFX)
    // Для: обновление UI
    // launch(Dispatchers.Main) {
    //     textView.text = "Updated!"
    // }

    // Unconfined: стартует в текущем потоке, но после suspension
    // может продолжить в любом --- используется редко
    launch(Dispatchers.Unconfined) {
        println("Before: ${Thread.currentThread().name}")
        delay(100)
        println("After: ${Thread.currentThread().name}")  // Может быть другой поток!
    }
}

// ---- withContext: переключение dispatcher без создания новой корутины ----

suspend fun loadAndDisplay(url: String) {
    val data = withContext(Dispatchers.IO) {
        // Выполняется на IO-потоке
        httpClient.get(url).body<String>()
    }
    // Возвращаемся на предыдущий dispatcher
    withContext(Dispatchers.Main) {
        // Обновляем UI
        // textView.text = data
    }
}
```

### Cancellation и таймауты

```kotlin
// ---- Cooperative cancellation ----

suspend fun processLargeFile(file: File) = coroutineScope {
    val lines = file.readLines()
    for (line in lines) {
        ensureActive()  // Проверяет, не отменена ли корутина
        processLine(line)
    }
}

// Или: yield() --- точка suspension + проверка отмены

suspend fun computeHeavy(): List<Int> = coroutineScope {
    val results = mutableListOf<Int>()
    for (i in 1..1_000_000) {
        if (i % 1000 == 0) yield()  // Дать шанс другим корутинам + проверить отмену
        results.add(heavyComputation(i))
    }
    results
}

// ---- withTimeout: автоматическая отмена по таймауту ----

suspend fun fetchWithTimeout(url: String): String? =
    withTimeoutOrNull(5000L) {
        // Если за 5 секунд не успеет --- вернёт null
        httpClient.get(url).body<String>()
    }

// ---- Отмена Job ----

fun main() = runBlocking {
    val job = launch {
        repeat(1000) { i ->
            println("Processing $i ...")
            delay(500)
        }
    }

    delay(2500)
    println("Cancelling...")
    job.cancelAndJoin()  // Отменяет и ждёт завершения
    println("Cancelled")
}
// Processing 0 ...
// Processing 1 ...
// Processing 2 ...
// Processing 3 ...
// Processing 4 ...
// Cancelling...
// Cancelled
```

---

## Race Conditions

```
+----------------------------------------------------------------------------+
|                      RACE CONDITION                                        |
+----------------------------------------------------------------------------+
|                                                                            |
|  PROBLEM: Non-atomic read-modify-write                                     |
|                                                                            |
|  counter = 0                                                               |
|                                                                            |
|  Coroutine A                    Coroutine B                                |
|  -----------                    -----------                                |
|  read counter (0)               read counter (0)                           |
|  add 1 (= 1)                                                              |
|                                 add 1 (= 1)                               |
|  write counter (1)                                                         |
|                                 write counter (1)                          |
|                                                                            |
|  Expected: counter = 2                                                     |
|  Actual:   counter = 1  <-- BUG!                                           |
|                                                                            |
|  SOLUTION: Make operation atomic                                           |
|                                                                            |
|  Coroutine A                    Coroutine B                                |
|  -----------                    -----------                                |
|  LOCK                           waiting...                                 |
|  read counter (0)               waiting...                                 |
|  add 1 (= 1)                   waiting...                                 |
|  write counter (1)              waiting...                                 |
|  UNLOCK                         LOCK                                       |
|                                 read counter (1)                           |
|                                 add 1 (= 2)                               |
|                                 write counter (2)                          |
|                                 UNLOCK                                     |
|                                                                            |
|  Result: counter = 2                                                       |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Демонстрация race condition в Kotlin

```kotlin
import kotlinx.coroutines.*
import java.util.concurrent.atomic.AtomicInteger

// ---- Race condition с корутинами ----

suspend fun raceConditionDemo() = coroutineScope {
    var counter = 0

    val jobs = (1..100).map {
        launch(Dispatchers.Default) {
            repeat(1000) {
                counter++  // Не атомарная операция!
            }
        }
    }
    jobs.forEach { it.join() }

    println("Expected: 100000, Actual: $counter")
    // Actual будет < 100000 из-за race condition
}

// ---- Решение 1: AtomicInteger ----

suspend fun atomicSolution() = coroutineScope {
    val counter = AtomicInteger(0)

    val jobs = (1..100).map {
        launch(Dispatchers.Default) {
            repeat(1000) {
                counter.incrementAndGet()  // Атомарная операция
            }
        }
    }
    jobs.forEach { it.join() }

    println("Result: ${counter.get()}")  // Всегда 100000
}

// ---- Решение 2: Mutex (kotlinx.coroutines) ----

import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

suspend fun mutexSolution() = coroutineScope {
    val mutex = Mutex()
    var counter = 0

    val jobs = (1..100).map {
        launch(Dispatchers.Default) {
            repeat(1000) {
                mutex.withLock {
                    counter++
                }
            }
        }
    }
    jobs.forEach { it.join() }

    println("Result: $counter")  // Всегда 100000
}

// ---- Решение 3: Confinement (ограничение одним потоком) ----

suspend fun confinementSolution() = coroutineScope {
    val singleThread = newSingleThreadContext("counter-thread")
    var counter = 0

    val jobs = (1..100).map {
        launch {
            repeat(1000) {
                withContext(singleThread) {
                    counter++
                }
            }
        }
    }
    jobs.forEach { it.join() }
    singleThread.close()

    println("Result: $counter")  // Всегда 100000
}
```

---

## Deadlock

```
+----------------------------------------------------------------------------+
|                          DEADLOCK                                          |
+----------------------------------------------------------------------------+
|                                                                            |
|  Four conditions (ALL must be true):                                       |
|                                                                            |
|  1. MUTUAL EXCLUSION                                                       |
|     Resource can only be held by one thread                                |
|                                                                            |
|  2. HOLD AND WAIT                                                          |
|     Thread holding resource waits for another                              |
|                                                                            |
|  3. NO PREEMPTION                                                          |
|     Resource cannot be forcibly taken                                      |
|                                                                            |
|  4. CIRCULAR WAIT                                                          |
|     Thread A waits for B, B waits for A                                    |
|                                                                            |
|  EXAMPLE:                                                                  |
|  +----------------------------------------------------------------------+  |
|  |                                                                      |  |
|  |  Coroutine A                    Coroutine B                          |  |
|  |  -----------                    -----------                          |  |
|  |  lock(mutexA)                   lock(mutexB)                         |  |
|  |  ...                            ...                                  |  |
|  |  lock(mutexB) <-- WAITING       lock(mutexA) <-- WAITING            |  |
|  |         |                              |                             |  |
|  |         +--------- DEADLOCK! ----------+                             |  |
|  |                                                                      |  |
|  +----------------------------------------------------------------------+  |
|                                                                            |
|  PREVENTION:                                                               |
|  * Lock ordering: Always acquire locks in same order                       |
|  * Timeout: Give up if can't acquire lock in time                          |
|  * Lock-free data structures                                               |
|  * Single lock for related resources                                       |
|  * Use Channels instead of shared mutable state                            |
|                                                                            |
+----------------------------------------------------------------------------+
```

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock

// ---- Deadlock с Mutex (NB: Kotlin Mutex не реентрантный!) ----

val mutexA = Mutex()
val mutexB = Mutex()

// Deadlock: разный порядок захвата
suspend fun coroutineA() {
    mutexA.withLock {
        delay(100)
        mutexB.withLock {   // Ждёт mutexB
            println("A acquired both")
        }
    }
}

suspend fun coroutineB() {
    mutexB.withLock {
        delay(100)
        mutexA.withLock {   // Ждёт mutexA --> DEADLOCK
            println("B acquired both")
        }
    }
}

// ---- Решение: единый порядок захвата ----

suspend fun coroutineASafe() {
    mutexA.withLock {       // Всегда сначала A
        mutexB.withLock {   // Потом B
            println("A acquired both")
        }
    }
}

suspend fun coroutineBSafe() {
    mutexA.withLock {       // Тоже сначала A
        mutexB.withLock {   // Потом B
            println("B acquired both")
        }
    }
}

// ---- Решение: tryLock с таймаутом ----

suspend fun withTimeoutLock(
    mutex: Mutex,
    timeoutMs: Long = 5000,
    block: suspend () -> Unit
) {
    val acquired = withTimeoutOrNull(timeoutMs) {
        mutex.lock()
        true
    }
    if (acquired == true) {
        try {
            block()
        } finally {
            mutex.unlock()
        }
    } else {
        println("Failed to acquire lock within timeout")
    }
}
```

---

## Синхронизация в Kotlin

| Примитив | Блокирует поток? | Контекст | Когда использовать |
|----------|-----------------|----------|-------------------|
| **`Mutex`** (kotlinx.coroutines) | Нет (suspend) | Корутины | Защита shared state в корутинах |
| **`synchronized`** | Да | Потоки | JVM intrinsic lock, простые случаи |
| **`@Volatile`** | Нет (видимость) | Потоки | Visibility guarantee для одного поля |
| **`AtomicInteger`** / `AtomicReference` | Нет (CAS) | Потоки + корутины | Счётчики, простые обновления |
| **`ReentrantLock`** | Да | Потоки | Нужна повторная блокировка |
| **`Semaphore`** (kotlinx.coroutines) | Нет (suspend) | Корутины | Ограничение числа concurrent операций |

### Примеры

```kotlin
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.Semaphore
import kotlinx.coroutines.sync.withLock
import kotlinx.coroutines.sync.withPermit
import java.util.concurrent.atomic.AtomicInteger
import java.util.concurrent.atomic.AtomicReference

// ---- Mutex: основной примитив для корутин ----

class ThreadSafeCache<K, V> {
    private val mutex = Mutex()
    private val cache = mutableMapOf<K, V>()

    suspend fun get(key: K): V? = mutex.withLock {
        cache[key]
    }

    suspend fun put(key: K, value: V) = mutex.withLock {
        cache[key] = value
    }

    suspend fun getOrPut(key: K, compute: suspend () -> V): V = mutex.withLock {
        cache.getOrPut(key) {
            // NB: compute() внутри withLock --- осторожно с долгими операциями
            runBlocking { compute() }
        }
    }
}

// ---- AtomicInteger: lock-free счётчик ----

class RequestCounter {
    private val total = AtomicInteger(0)
    private val errors = AtomicInteger(0)

    fun recordSuccess() { total.incrementAndGet() }
    fun recordError() {
        total.incrementAndGet()
        errors.incrementAndGet()
    }

    fun errorRate(): Double {
        val t = total.get()
        return if (t == 0) 0.0 else errors.get().toDouble() / t
    }
}

// ---- AtomicReference: lock-free обновление объекта ----

data class AppState(val users: List<String>, val version: Int)

class StateHolder {
    private val state = AtomicReference(AppState(emptyList(), 0))

    fun addUser(user: String) {
        state.updateAndGet { current ->
            current.copy(
                users = current.users + user,
                version = current.version + 1
            )
        }
    }

    fun currentState(): AppState = state.get()
}

// ---- @Volatile: гарантия видимости ----

class Worker {
    @Volatile
    private var running = true

    fun stop() { running = false }

    fun work() {
        while (running) {    // Без @Volatile другой поток может не увидеть изменение
            doSomeWork()
        }
    }
}

// ---- synchronized: JVM intrinsic lock ----

class SynchronizedCounter {
    private var count = 0

    @Synchronized
    fun increment() { count++ }

    @Synchronized
    fun get(): Int = count
}

// Или через блок:
class SynchronizedList<T> {
    private val items = mutableListOf<T>()
    private val lock = Any()

    fun add(item: T) = synchronized(lock) {
        items.add(item)
    }

    fun snapshot(): List<T> = synchronized(lock) {
        items.toList()
    }
}

// ---- Semaphore: ограничение concurrency ----

suspend fun rateLimitedFetch(urls: List<String>): List<String> = coroutineScope {
    val semaphore = Semaphore(10)  // Максимум 10 одновременных запросов

    urls.map { url ->
        async {
            semaphore.withPermit {
                httpClient.get(url).body<String>()
            }
        }
    }.awaitAll()
}
```

---

## Channels: обмен данными между корутинами

Channel --- примитив CSP для передачи данных между корутинами. Каждое значение доставляется ровно одному получателю.

```
+----------------------------------------------------------------------------+
|                        CHANNEL TYPES                                       |
+----------------------------------------------------------------------------+
|                                                                            |
|  RENDEZVOUS (capacity = 0)            BUFFERED (capacity = N)              |
|  +---------------------------+        +---------------------------+        |
|  |                           |        |                           |        |
|  |  Sender    [  ]  Receiver |        |  Sender [1][2][3] Receiver|        |
|  |  suspends       suspends  |        |         buffer            |        |
|  |  until          until     |        |  suspends only when full  |        |
|  |  receiver       sender    |        |                           |        |
|  |  ready          sends     |        |                           |        |
|  +---------------------------+        +---------------------------+        |
|                                                                            |
|  UNLIMITED (capacity = MAX)           CONFLATED (keeps latest)             |
|  +---------------------------+        +---------------------------+        |
|  |                           |        |                           |        |
|  |  Sender [1][2]..  Receiver|        |  Sender   [3]   Receiver |        |
|  |  never suspends           |        |  overwrites old values    |        |
|  |  (can OOM!)               |        |  receiver gets latest     |        |
|  |                           |        |                           |        |
|  +---------------------------+        +---------------------------+        |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Базовое использование

```kotlin
import kotlinx.coroutines.channels.*

// ---- Простой producer-consumer ----

suspend fun producerConsumer() = coroutineScope {
    val channel = Channel<Int>(capacity = 10)  // Buffered

    // Producer
    launch {
        for (i in 1..10) {
            println("Sending $i")
            channel.send(i)
            delay(100)
        }
        channel.close()  // Сигнал: больше данных не будет
    }

    // Consumer
    launch {
        for (value in channel) {  // Итерация до close
            println("Received: $value")
        }
        println("Channel closed")
    }
}

// ---- produce { } builder --- более идиоматично ----

fun CoroutineScope.produceNumbers(): ReceiveChannel<Int> = produce {
    for (i in 1..10) {
        send(i)
        delay(100)
    }
    // Channel автоматически закроется при завершении корутины
}

suspend fun useProducer() = coroutineScope {
    val numbers = produceNumbers()

    for (n in numbers) {
        println("Got: $n")
    }
}
```

### Fan-out / Fan-in

```kotlin
// ---- Fan-out: один producer, несколько consumers ----

suspend fun fanOut() = coroutineScope {
    val tasks = Channel<Int>(capacity = 100)

    // Producer: генерирует задачи
    launch {
        for (i in 1..100) {
            tasks.send(i)
        }
        tasks.close()
    }

    // Workers: каждый берёт задачу из одного канала
    repeat(5) { workerId ->
        launch {
            for (task in tasks) {
                println("Worker $workerId processing task $task")
                delay((50..200).random().toLong())
            }
        }
    }
}

// ---- Fan-in: несколько producers, один consumer ----

suspend fun fanIn() = coroutineScope {
    val results = Channel<String>(capacity = 100)

    // Несколько producers
    launch { fetchFromSource("DB", results) }
    launch { fetchFromSource("API", results) }
    launch { fetchFromSource("Cache", results) }

    // Один consumer
    launch {
        repeat(30) {
            println(results.receive())
        }
        results.cancel()
    }
}

suspend fun fetchFromSource(name: String, channel: SendChannel<String>) {
    repeat(10) { i ->
        delay((50..300).random().toLong())
        channel.send("$name: item $i")
    }
}
```

### Pipeline: цепочка обработки

```kotlin
// ---- Pipeline: channel -> transform -> channel ----

fun CoroutineScope.generateNumbers(count: Int): ReceiveChannel<Int> = produce {
    for (i in 1..count) send(i)
}

fun CoroutineScope.square(input: ReceiveChannel<Int>): ReceiveChannel<Int> = produce {
    for (n in input) send(n * n)
}

fun CoroutineScope.filterEven(input: ReceiveChannel<Int>): ReceiveChannel<Int> = produce {
    for (n in input) if (n % 2 == 0) send(n)
}

suspend fun pipeline() = coroutineScope {
    val numbers = generateNumbers(20)
    val squared = square(numbers)
    val even = filterEven(squared)

    for (value in even) {
        println(value)  // 4, 16, 36, 64, 100, ...
    }
}
```

---

## Flow: асинхронные потоки данных

Flow --- холодный асинхронный поток данных. В отличие от Channel (горячий), Flow не производит данные, пока нет подписчика.

```
+----------------------------------------------------------------------------+
|                    CHANNELS vs FLOW                                        |
+----------------------------------------------------------------------------+
|                                                                            |
|  CHANNEL (hot)                          FLOW (cold)                        |
|  -----------------                      ----------------                   |
|  * Производит данные независимо          * Данные только при collect       |
|  * Каждое значение --- одному receiver   * Каждый collector --- свой поток |
|  * Нужно явно close()                    * Автоматический cleanup          |
|  * Producer-consumer (1:1)               * Observable stream (1:N)         |
|  * Mutable, shared state                 * Immutable, cold by default      |
|                                                                            |
|  Когда Channel:                         Когда Flow:                        |
|  * Fan-out/fan-in                       * Реактивные UI-обновления         |
|  * Worker pool                          * Потоки данных из БД/сети         |
|  * Точная доставка: один receiver       * Broadcast: несколько observers   |
|  * Координация между корутинами         * Трансформации (map/filter/etc)   |
|                                                                            |
+----------------------------------------------------------------------------+
```

### Базовое использование Flow

```kotlin
import kotlinx.coroutines.flow.*

// ---- Создание Flow ----

// Через flow { } builder
fun numberFlow(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(100)  // Имитация асинхронной работы
        emit(i)     // Отправляем значение в поток
    }
}

// Через extension functions
val simpleFlow: Flow<Int> = listOf(1, 2, 3).asFlow()
val rangeFlow: Flow<Int> = (1..10).asFlow()

// Через flowOf
val literalFlow: Flow<String> = flowOf("a", "b", "c")

// ---- Сбор данных ----

suspend fun collectFlow() {
    numberFlow()
        .filter { it % 2 != 0 }
        .map { it * it }
        .collect { value ->
            println(value)
        }
    // 1, 9, 25
}

// ---- Операторы трансформации ----

suspend fun flowOperators() {
    (1..10).asFlow()
        .filter { it > 3 }
        .map { "Item $it" }
        .take(3)
        .onEach { println("Processing: $it") }
        .collect { println("Result: $it") }
    // Processing: Item 4
    // Result: Item 4
    // Processing: Item 5
    // Result: Item 5
    // Processing: Item 6
    // Result: Item 6
}
```

### Flow: обработка ошибок и completion

```kotlin
// ---- catch: перехват ошибок в upstream ----

fun riskyFlow(): Flow<Int> = flow {
    emit(1)
    emit(2)
    throw RuntimeException("Oops!")
    emit(3)  // Не выполнится
}

suspend fun handleErrors() {
    riskyFlow()
        .catch { e -> println("Caught: ${e.message}") }
        .collect { println(it) }
    // 1
    // 2
    // Caught: Oops!
}

// ---- onCompletion: cleanup ----

suspend fun withCompletion() {
    (1..3).asFlow()
        .onCompletion { cause ->
            if (cause != null) println("Flow failed: $cause")
            else println("Flow completed normally")
        }
        .collect { println(it) }
}

// ---- retry: повтор при ошибке ----

fun networkFlow(): Flow<Data> = flow {
    emit(fetchFromNetwork())
}.retry(3) { cause ->
    cause is java.io.IOException    // Повторять только для I/O ошибок
}
```

### StateFlow и SharedFlow

```kotlin
import kotlinx.coroutines.flow.*

// ---- StateFlow: хранит текущее значение (аналог LiveData) ----

class CounterViewModel {
    private val _count = MutableStateFlow(0)
    val count: StateFlow<Int> = _count.asStateFlow()

    fun increment() {
        _count.update { it + 1 }  // Thread-safe update
    }

    fun reset() {
        _count.value = 0
    }
}

// ---- SharedFlow: broadcast событий без хранения текущего значения ----

class EventBus {
    private val _events = MutableSharedFlow<AppEvent>(
        replay = 0,                                    // Не хранить прошлые события
        extraBufferCapacity = 64,                      // Буфер
        onBufferOverflow = BufferOverflow.DROP_OLDEST  // Стратегия переполнения
    )
    val events: SharedFlow<AppEvent> = _events.asSharedFlow()

    suspend fun emit(event: AppEvent) {
        _events.emit(event)
    }
}

sealed class AppEvent {
    data class UserLoggedIn(val userId: String) : AppEvent()
    data class OrderCreated(val orderId: String) : AppEvent()
    data object NetworkLost : AppEvent()
}

// Подписка:
suspend fun observeEvents(eventBus: EventBus) = coroutineScope {
    // Каждый collector получает ВСЕ события (broadcast)
    launch {
        eventBus.events
            .filterIsInstance<AppEvent.UserLoggedIn>()
            .collect { println("Analytics: user ${it.userId} logged in") }
    }

    launch {
        eventBus.events
            .filterIsInstance<AppEvent.OrderCreated>()
            .collect { println("Notification: order ${it.orderId}") }
    }
}
```

### Flow: параллелизм и буферизация

```kotlin
// ---- buffer: producer не ждёт consumer ----

fun slowProducer(): Flow<Int> = flow {
    for (i in 1..5) {
        delay(300)    // Медленная генерация
        emit(i)
    }
}

suspend fun bufferedCollection() {
    slowProducer()
        .buffer(capacity = 10)
        .collect { value ->
            delay(500)   // Медленная обработка
            println(value)
        }
    // Без buffer: 5 * (300 + 500) = 4000ms
    // С buffer: 300 + 5 * 500 = 2800ms (producer не ждёт consumer)
}

// ---- conflate: пропускать устаревшие значения ----

suspend fun conflatedCollection() {
    slowProducer()
        .conflate()    // Если consumer медленный --- пропускаем промежуточные
        .collect { value ->
            delay(1000)
            println(value)  // Получит не все значения, а только "свежие"
        }
}

// ---- flatMapMerge: параллельная обработка ----

suspend fun parallelProcessing() {
    (1..10).asFlow()
        .flatMapMerge(concurrency = 4) { id ->
            flow {
                val result = fetchData(id)  // Параллельно для 4 элементов
                emit(result)
            }
        }
        .collect { println(it) }
}
```

---

## Паттерны concurrency в Kotlin

### Producer-Consumer через Channel

```kotlin
// ---- Типизированный producer-consumer ----

data class Task(val id: Int, val payload: String)
data class TaskResult(val taskId: Int, val result: String)

suspend fun workerPool(
    tasks: List<Task>,
    workerCount: Int = 4
): List<TaskResult> = coroutineScope {
    val taskChannel = Channel<Task>(capacity = Channel.BUFFERED)
    val resultChannel = Channel<TaskResult>(capacity = Channel.BUFFERED)

    // Producer: отправляет задачи
    launch {
        for (task in tasks) {
            taskChannel.send(task)
        }
        taskChannel.close()
    }

    // Workers: обрабатывают задачи
    repeat(workerCount) { workerId ->
        launch {
            for (task in taskChannel) {
                val result = processTask(task)  // Тяжёлая обработка
                resultChannel.send(TaskResult(task.id, result))
            }
        }
    }

    // Collector: собирает результаты
    val results = mutableListOf<TaskResult>()
    launch {
        repeat(tasks.size) {
            results.add(resultChannel.receive())
        }
        resultChannel.close()
    }.join()

    results
}
```

### Throttle / Debounce с Flow

```kotlin
// ---- Debounce: ждёт паузу в событиях ----

fun searchQueryFlow(queryFlow: Flow<String>): Flow<List<SearchResult>> =
    queryFlow
        .debounce(300)                              // Ждёт 300ms тишины
        .filter { it.length >= 3 }                  // Минимум 3 символа
        .distinctUntilChanged()                     // Не повторять одинаковые
        .flatMapLatest { query ->                   // Отменяет предыдущий запрос
            flow { emit(searchApi(query)) }
        }

// ---- Rate limiting через Semaphore ----

class RateLimiter(maxConcurrent: Int) {
    private val semaphore = Semaphore(maxConcurrent)

    suspend fun <T> execute(block: suspend () -> T): T =
        semaphore.withPermit { block() }
}

suspend fun fetchAll(urls: List<String>): List<String> = coroutineScope {
    val limiter = RateLimiter(maxConcurrent = 5)

    urls.map { url ->
        async {
            limiter.execute {
                httpClient.get(url).body<String>()
            }
        }
    }.awaitAll()
}
```

### Actor-like паттерн через Channel

```kotlin
// ---- Actor: один владелец state, общение через сообщения ----

sealed class CounterMsg {
    data object Increment : CounterMsg()
    data object Decrement : CounterMsg()
    data class GetCount(val response: CompletableDeferred<Int>) : CounterMsg()
}

fun CoroutineScope.counterActor(): SendChannel<CounterMsg> = actor {
    var count = 0
    for (msg in channel) {
        when (msg) {
            is CounterMsg.Increment -> count++
            is CounterMsg.Decrement -> count--
            is CounterMsg.GetCount -> msg.response.complete(count)
        }
    }
}

suspend fun useActor() = coroutineScope {
    val counter = counterActor()

    // Множество корутин могут отправлять сообщения
    repeat(1000) {
        launch { counter.send(CounterMsg.Increment) }
    }

    // Получить текущее значение
    val response = CompletableDeferred<Int>()
    counter.send(CounterMsg.GetCount(response))
    println("Count: ${response.await()}")

    counter.close()
}
```

---

## Happens-Before в Kotlin/JVM

```kotlin
// ---- Без volatile: compiler/CPU может переупорядочить ----

var flag = false
var value = 0

// Thread 1
fun writer() {
    value = 42
    flag = true
}

// Thread 2
fun reader() {
    if (flag) {
        // value может быть 0! CPU reordering
        println(value)
    }
}

// ---- С @Volatile: happens-before гарантия ----

@Volatile var flagSafe = false
var valueSafe = 0

// Thread 1
fun writerSafe() {
    valueSafe = 42
    flagSafe = true  // volatile write creates happens-before
}

// Thread 2
fun readerSafe() {
    if (flagSafe) {
        // valueSafe гарантированно 42
        // Volatile read видит всё, что было записано до volatile write
        println(valueSafe)
    }
}

// ---- Happens-before правила в Kotlin/JVM ----
// 1. synchronized block exit  HB  entry на том же мониторе
// 2. volatile write           HB  read той же переменной
// 3. Thread.start()           HB  первая инструкция потока
// 4. Последняя инструкция     HB  Thread.join() return
// 5. coroutineScope exit      HB  код после coroutineScope
// 6. channel.send()           HB  channel.receive() того же элемента
```

---

## Мифы и заблуждения

**Миф:** Корутины --- это потоки, только легче.

**Реальность:** Корутины --- это не потоки. Это suspend-функции, которые компилируются в state machines. Корутина может приостановиться на одном потоке и возобновиться на другом. Потоков может быть всего несколько, а корутин --- миллионы.

**Миф:** `Dispatchers.IO` создаёт бесконечное число потоков.

**Реальность:** По умолчанию `Dispatchers.IO` использует пул до 64 потоков (или `max(64, число_процессоров)`). Для задач, требующих больше параллелизма, можно создать свой dispatcher: `Dispatchers.IO.limitedParallelism(128)`.

**Миф:** `synchronized` работает с корутинами так же, как с потоками.

**Реальность:** `synchronized` блокирует поток, а не корутину. Если корутина захватит `synchronized`-блок и будет suspended внутри, поток останется заблокированным. Для корутин используйте `Mutex` из kotlinx.coroutines --- он suspend'ит корутину, не блокируя поток.

**Миф:** `Channel` можно использовать вместо `Flow` для всего.

**Реальность:** Channel --- hot, каждое значение доставляется одному receiver. Flow --- cold, каждый collector получает весь поток. Для UI-обновлений, реактивных потоков данных и трансформаций используйте Flow. Channel --- для координации между корутинами (worker pool, fan-out).

---

## Подводные камни

### Ошибка 1: GlobalScope.launch

**Почему происходит:** Разработчики привыкли к "fire and forget" в других языках.

**Как избежать:**

```kotlin
// GlobalScope --- утечка корутин, нет structured concurrency
GlobalScope.launch { fetchData() }   // Кто отменит? Когда?

// Правильно: привязать к lifecycle
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {   // Отменится при onCleared()
            fetchData()
        }
    }
}

// Или: coroutineScope для suspend-функций
suspend fun processAll(items: List<Item>) = coroutineScope {
    items.map { async { process(it) } }.awaitAll()
}
```

### Ошибка 2: блокирующий код в корутинах

**Почему происходит:** Вызов blocking I/O на `Dispatchers.Default` "съедает" потоки computation pool.

**Как избежать:**

```kotlin
// Thread.sleep() и блокирующий I/O --- на Dispatchers.IO
suspend fun readFile(path: String): String =
    withContext(Dispatchers.IO) {
        File(path).readText()  // Блокирующий вызов --- OK на IO dispatcher
    }

// Тяжёлые вычисления --- на Dispatchers.Default
suspend fun computeHash(data: ByteArray): String =
    withContext(Dispatchers.Default) {
        MessageDigest.getInstance("SHA-256")
            .digest(data)
            .joinToString("") { "%02x".format(it) }
    }
```

### Ошибка 3: забытая отмена (cancellation)

**Почему происходит:** Тяжёлый цикл без проверки `isActive`.

**Как избежать:**

```kotlin
// Плохо: не реагирует на отмену
suspend fun longRunning() {
    for (i in 1..1_000_000) {
        heavyComputation(i)  // Если отменить --- продолжит работать!
    }
}

// Хорошо: cooperative cancellation
suspend fun longRunningCooperative() {
    for (i in 1..1_000_000) {
        ensureActive()   // Бросит CancellationException если отменена
        heavyComputation(i)
    }
}
```

---

## Проверь себя

<details>
<summary>1. Когда использовать threads vs coroutines?</summary>

**Ответ:**

**Threads (потоки JVM):**
- CPU-bound работа, которая действительно параллелится на ядрах
- Интеграция с blocking Java-библиотеками
- Крайне низкоуровневые сценарии (реальное время)

**Coroutines:**
- I/O-bound работа (network, disk, database)
- Structured concurrency (автоматическое управление lifecycle)
- Высокое число concurrent задач (тысячи+)
- UI-программирование (Android, Desktop)

На практике в Kotlin-проектах 95% concurrency --- через корутины. Потоки напрямую нужны редко.

</details>

<details>
<summary>2. Как избежать deadlock?</summary>

**Ответ:**

**Стратегии:**

1. **Lock ordering:** Всегда acquire locks в одном и том же порядке
2. **Timeout:** Отказ если не удалось захватить за время
   ```kotlin
   withTimeoutOrNull(5000) { mutex.lock() }
   ```
3. **Single lock:** Один Mutex для связанных ресурсов
4. **Message passing:** Channel вместо shared mutable state
5. **Structured concurrency:** coroutineScope автоматически управляет жизненным циклом

</details>

<details>
<summary>3. Что такое structured concurrency?</summary>

**Ответ:**

Structured concurrency --- принцип, при котором корутины образуют дерево parent-child:

- **Parent ждёт всех children:** `coroutineScope` не завершится, пока все `launch`/`async` внутри не завершатся
- **Отмена parent отменяет children:** если parent отменяется, все дочерние корутины тоже отменяются
- **Ошибка child убивает parent:** если child бросает исключение, parent тоже отменяется (кроме `supervisorScope`)
- **Нет утечек:** невозможна ситуация "забытой" корутины

```kotlin
suspend fun example() = coroutineScope {
    val a = async { fetchA() }  // child 1
    val b = async { fetchB() }  // child 2
    // Если fetchA() упадёт --- fetchB() будет отменён
    // coroutineScope не завершится, пока оба не завершатся/отменятся
    a.await() to b.await()
}
```

</details>

<details>
<summary>4. Чем Channel отличается от Flow?</summary>

**Ответ:**

| | Channel | Flow |
|---|---------|------|
| **Тип** | Hot (горячий) | Cold (холодный) |
| **Производство** | Независимо от получателей | Только при collect |
| **Доставка** | Один receiver на значение | Каждый collector получает всё |
| **Lifecycle** | Нужен явный close() | Automatic (structured concurrency) |
| **Use case** | Worker pool, fan-out, координация | UI, reactive streams, data pipeline |

**Channel** --- "труба": producer кладёт, один consumer забирает.
**Flow** --- "радиостанция": начинает вещать при подписке, каждый слышит всё.

</details>

<details>
<summary>5. Что такое happens-before?</summary>

**Ответ:**

**Happens-before** --- гарантия порядка видимости изменений между потоками.

**В Kotlin/JVM:**
- `synchronized` block exit happens-before entry на том же мониторе
- `@Volatile` write happens-before read той же переменной
- `Thread.start()` happens-before любого кода в потоке
- Thread termination happens-before `Thread.join()` return
- `channel.send()` happens-before `channel.receive()` того же элемента

**Зачем:** Без happens-before компилятор и CPU могут переупорядочить операции --- другой поток может увидеть "будущее" значение flag, но "прошлое" значение value.

</details>

<details>
<summary>6. Чем Mutex из kotlinx.coroutines отличается от synchronized?</summary>

**Ответ:**

| | `Mutex` | `synchronized` |
|---|---------|----------------|
| **Блокировка** | Suspending (не блокирует поток) | Blocking (блокирует поток) |
| **Реентрантность** | Нет (повторный lock --- deadlock) | Да (тот же поток может войти повторно) |
| **Контекст** | Корутины | JVM-потоки |
| **Внутри suspend** | Безопасно | Опасно (заблокирует поток) |

**Правило:** В корутинном коде --- `Mutex`. В потоковом коде --- `synchronized` или `ReentrantLock`. Не смешивайте.

</details>

---

## Практическое применение

1. **Корутины по умолчанию:** для всего concurrency в Kotlin используйте корутины, не потоки напрямую
2. **Structured concurrency:** привязывайте корутины к lifecycle (`viewModelScope`, `lifecycleScope`, `coroutineScope`)
3. **Правильный dispatcher:** `IO` для сети/файлов, `Default` для вычислений, `Main` для UI
4. **Flow для реактивности:** UI-обновления через `StateFlow`, события через `SharedFlow`
5. **Channel для координации:** worker pool, fan-out/fan-in, producer-consumer
6. **Mutex вместо synchronized:** в suspend-функциях используйте `Mutex.withLock`, не `synchronized`
7. **Cooperative cancellation:** в длинных циклах вызывайте `ensureActive()` или `yield()`

---

## Связи

**[[programming-overview]]** --- Concurrency и parallelism --- фундаментальные концепции, которые пронизывают все уровни программирования. Overview описывает парадигмы и подходы, а concurrency добавляет ещё одно измерение: программа может быть одновременно объектно-ориентированной, функциональной и concurrent.

**[[jvm-concurrency-overview]]** --- JVM предоставляет конкретную реализацию concurrency-примитивов: Java Memory Model (JSR-133), synchronized/volatile, java.util.concurrent, а также современные абстракции --- Kotlin coroutines и Java virtual threads (Project Loom). Понимание теоретических основ делает работу с JVM-специфичными инструментами осмысленной.

**[[architecture-resilience-patterns]]** --- Паттерны resilience (retry, circuit breaker, bulkhead, timeout) напрямую связаны с concurrency: все они решают проблемы, возникающие при параллельных запросах к внешним сервисам. Circuit breaker использует atomic state transitions, bulkhead реализуется через semaphores, timeout --- через `withTimeoutOrNull`.

**[[functional-programming]]** --- Immutability и pure functions из FP устраняют race conditions по определению: если данные нельзя изменить, нет конфликтов при параллельном доступе. Flow --- функциональный API для асинхронных потоков данных.

---

## Источники

Goetz B. et al. (2006). *"Java Concurrency in Practice."* --- Золотой стандарт для JVM-разработчиков. Объясняет Java Memory Model, happens-before, thread safety и построение корректных concurrent-структур.

Elizarov R. (2018). *"Structured Concurrency."* --- Статья создателя Kotlin coroutines о принципах structured concurrency, которые легли в основу `coroutineScope`, `supervisorScope` и иерархии Job.

Moskala M. (2024). *"Kotlin Coroutines: Deep Dive."* --- Подробное руководство по Kotlin coroutines: от основ до продвинутых паттернов (Flow, Channel, testing). Лучшая книга по теме для Kotlin-разработчиков.

Herlihy M., Shavit N. (2012). *"The Art of Multiprocessor Programming."* --- Глубокое погружение в lock-free и wait-free алгоритмы, линеаризуемость, concurrent data structures.

Hoare C.A.R. (1978). *"Communicating Sequential Processes."* --- Оригинальная работа, описавшая CSP-модель concurrency через обмен сообщениями. Лежит в основе goroutines (Go) и каналов (Kotlin).

- [Kotlin Coroutines Guide](https://kotlinlang.org/docs/coroutines-guide.html) --- официальная документация по корутинам
- [Shared Mutable State and Concurrency](https://kotlinlang.org/docs/shared-mutable-state-and-concurrency.html) --- Mutex, Atomic, confinement в корутинах
- [Kotlin Channels](https://kotlinlang.org/docs/channels.html) --- официальная документация по каналам
- [Kotlin Flow](https://kotlinlang.org/docs/flow.html) --- холодные асинхронные потоки данных
- [Structured Concurrency by Roman Elizarov](https://elizarov.medium.com/structured-concurrency-722d765aa952) --- ключевая статья о принципах structured concurrency

---

---

## Ключевые карточки

В чём разница между concurrency и parallelism?
?
Concurrency --- структурирование программы для работы с несколькими задачами (design-time решение). Parallelism --- одновременное выполнение на нескольких ядрах CPU (runtime). Можно иметь concurrency без parallelism (один core, time-slicing). Parallelism требует concurrent структуры.

Какие четыре условия необходимы для deadlock?
?
1) Mutual Exclusion --- ресурс только у одного потока. 2) Hold and Wait --- поток держит ресурс и ждёт другой. 3) No Preemption --- ресурс нельзя отобрать. 4) Circular Wait --- A ждёт B, B ждёт A. Все четыре должны выполняться одновременно.

Что такое structured concurrency в Kotlin?
?
Принцип иерархии корутин: parent ждёт всех children, отмена parent отменяет children, ошибка child убивает parent (кроме supervisorScope). Реализуется через coroutineScope, supervisorScope. Гарантирует отсутствие утечек корутин. GlobalScope --- нарушение этого принципа.

Чем Kotlin Mutex отличается от synchronized?
?
Mutex.lock() --- suspending, не блокирует поток. synchronized --- blocking, блокирует поток. Mutex не реентрантный (повторный lock = deadlock). synchronized реентрантный. В корутинном коде --- Mutex. В потоковом --- synchronized.

Что такое race condition и как её предотвратить?
?
Баг из-за непредсказуемого порядка операций над shared state. Предотвращение в Kotlin: Mutex.withLock для корутин, AtomicInteger для простых счётчиков, confinement (один поток через withContext), или immutable data + message passing через Channel.

Когда использовать Channel, а когда Flow?
?
Channel: hot, каждое значение одному receiver, fan-out/fan-in, worker pool, координация. Flow: cold, каждый collector получает весь поток, UI-обновления (StateFlow), события (SharedFlow), data pipelines с трансформациями.

Какие Dispatchers есть в Kotlin coroutines и когда какой использовать?
?
Default: CPU-intensive вычисления (пул = число ядер). IO: blocking I/O, сеть, файлы, БД (пул до 64 потоков). Main: UI-поток (Android). Unconfined: стартует в текущем потоке, после suspension --- в любом (редко используется).

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kotlin-coroutines]] | Практическая реализация concurrency в Kotlin (advanced) |
| Углубиться | [[jvm-concurrency-overview]] | JVM-специфичные примитивы: Java Memory Model, volatile, CAS |
| Смежная тема | [[architecture-resilience-patterns]] | Circuit breaker, retry, bulkhead --- паттерны на базе concurrency |
| Обзор | [[programming-overview]] | Вернуться к карте раздела Programming |

---

*Проверено: 2026-02-19*
