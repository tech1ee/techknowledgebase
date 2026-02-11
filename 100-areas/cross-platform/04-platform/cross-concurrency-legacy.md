---
title: "Cross-Platform: Legacy Concurrency — GCD vs Handler/Looper"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - gcd
  - handler
  - threading
  - type/comparison
  - level/intermediate
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-memory-management]]"
related:
  - "[[ios-gcd-deep-dive]]"
  - "[[android-handler-looper]]"
  - "[[concurrency-vs-parallelism]]"
---

# Legacy Concurrency: GCD vs Handler/Looper

## TL;DR

| Аспект | iOS (GCD) | Android (Handler/Looper) |
|--------|-----------|--------------------------|
| **Основной механизм** | DispatchQueue | Handler + Looper + MessageQueue |
| **Main thread** | DispatchQueue.main | Looper.getMainLooper() |
| **Background work** | DispatchQueue.global() | Executors / HandlerThread |
| **Приоритеты** | QoS (6 уровней) | Thread.priority / Executor pools |
| **Группировка задач** | DispatchGroup | CountDownLatch / CompletableFuture |
| **Отложенное выполнение** | asyncAfter | postDelayed |
| **Барьеры** | DispatchWorkItem с barrier | Нет прямого аналога |
| **Современная альтернатива** | Swift Concurrency (async/await) | Kotlin Coroutines |
| **Отмена задач** | DispatchWorkItem.cancel() | Handler.removeCallbacks() |
| **Thread-safe коллекции** | Concurrent queue + barrier | Collections.synchronized* |

---

## 1. Архитектурное сравнение

### iOS: Grand Central Dispatch (GCD)

GCD — низкоуровневая библиотека Apple для управления параллелизмом. Основана на концепции очередей (queues), которые абстрагируют управление потоками.

```swift
// Базовая структура GCD
// DispatchQueue -> Thread Pool -> Threads
//
// Типы очередей:
// 1. Serial (последовательная) — задачи выполняются по одной
// 2. Concurrent (параллельная) — задачи могут выполняться одновременно

import Foundation

// Serial queue — задачи выполняются последовательно
let serialQueue = DispatchQueue(label: "com.app.serial")

// Concurrent queue — задачи выполняются параллельно
let concurrentQueue = DispatchQueue(
    label: "com.app.concurrent",
    attributes: .concurrent
)

// Global queue — системная concurrent queue
let globalQueue = DispatchQueue.global(qos: .userInitiated)

// Main queue — serial queue на главном потоке
let mainQueue = DispatchQueue.main
```

### Android: Handler/Looper/MessageQueue

Android использует паттерн "Message Loop" — каждый поток может иметь Looper, который обрабатывает сообщения из MessageQueue.

```kotlin
// Базовая структура Android Threading
// Thread -> Looper -> MessageQueue <- Handler
//
// Handler отправляет Message/Runnable в MessageQueue
// Looper извлекает и обрабатывает их последовательно

import android.os.Handler
import android.os.Looper
import android.os.HandlerThread
import java.util.concurrent.Executors

// Handler для главного потока
val mainHandler = Handler(Looper.getMainLooper())

// Создание фонового потока с Looper
val handlerThread = HandlerThread("BackgroundThread").apply { start() }
val backgroundHandler = Handler(handlerThread.looper)

// Executors для пула потоков (более современный подход)
val executor = Executors.newFixedThreadPool(4)
val singleExecutor = Executors.newSingleThreadExecutor()
```

---

## 2. Правило главного потока

### iOS: Main Thread

```swift
import UIKit

class DataManager {

    func loadData() {
        // Фоновая работа
        DispatchQueue.global(qos: .userInitiated).async {
            let data = self.fetchDataFromNetwork()

            // ОБЯЗАТЕЛЬНО: UI обновления на main thread
            DispatchQueue.main.async {
                self.updateUI(with: data)
            }
        }
    }

    // Проверка текущего потока
    func safeUIUpdate() {
        if Thread.isMainThread {
            updateUI(with: cachedData)
        } else {
            DispatchQueue.main.async {
                self.updateUI(with: self.cachedData)
            }
        }
    }

    // dispatchPrecondition для отладки
    func criticalUIMethod() {
        dispatchPrecondition(condition: .onQueue(.main))
        // Код, который должен выполняться только на main
    }

    private func fetchDataFromNetwork() -> Data { Data() }
    private func updateUI(with data: Data) { }
    private var cachedData: Data { Data() }
}
```

### Android: Main/UI Thread

```kotlin
import android.os.Handler
import android.os.Looper
import android.view.View
import java.util.concurrent.Executors

class DataManager(private val view: View) {

    private val mainHandler = Handler(Looper.getMainLooper())
    private val executor = Executors.newSingleThreadExecutor()

    fun loadData() {
        // Фоновая работа
        executor.execute {
            val data = fetchDataFromNetwork()

            // ОБЯЗАТЕЛЬНО: UI обновления на main thread
            mainHandler.post {
                updateUI(data)
            }
        }
    }

    // Альтернатива через View.post
    fun loadDataWithViewPost() {
        executor.execute {
            val data = fetchDataFromNetwork()

            // View.post автоматически использует main looper
            view.post {
                updateUI(data)
            }
        }
    }

    // Проверка текущего потока
    fun safeUIUpdate() {
        if (Looper.myLooper() == Looper.getMainLooper()) {
            updateUI(cachedData)
        } else {
            mainHandler.post {
                updateUI(cachedData)
            }
        }
    }

    // Проверка через аннотации (compile-time)
    @MainThread
    fun criticalUIMethod() {
        // Android Lint проверит вызовы этого метода
    }

    private fun fetchDataFromNetwork(): ByteArray = byteArrayOf()
    private fun updateUI(data: ByteArray) { }
    private val cachedData: ByteArray = byteArrayOf()
}
```

---

## 3. Quality of Service (QoS) / Приоритеты

### iOS: QoS классы

```swift
import Foundation

// 6 уровней QoS (от высшего к низшему)
enum QoSExamples {

    static func demonstrateQoS() {
        // 1. userInteractive — анимации, отклик на ввод
        DispatchQueue.global(qos: .userInteractive).async {
            // Максимальный приоритет, минимальная латентность
        }

        // 2. userInitiated — пользователь ждёт результат
        DispatchQueue.global(qos: .userInitiated).async {
            // Высокий приоритет, быстрый отклик
        }

        // 3. default — стандартный приоритет
        DispatchQueue.global(qos: .default).async {
            // Средний приоритет
        }

        // 4. utility — длительные задачи с прогрессом
        DispatchQueue.global(qos: .utility).async {
            // Индикатор прогресса, экономия энергии
        }

        // 5. background — невидимые пользователю задачи
        DispatchQueue.global(qos: .background).async {
            // Минимальный приоритет, максимальная экономия
        }

        // 6. unspecified — система решает сама
        DispatchQueue.global(qos: .unspecified).async {
            // Наследует QoS от контекста
        }
    }

    // Создание очереди с QoS
    static let imageProcessingQueue = DispatchQueue(
        label: "com.app.imageProcessing",
        qos: .userInitiated,
        attributes: .concurrent
    )
}
```

### Android: Thread Priority и Executor Pools

```kotlin
import android.os.Process
import java.util.concurrent.Executors
import java.util.concurrent.ThreadFactory
import java.util.concurrent.ThreadPoolExecutor
import java.util.concurrent.TimeUnit
import java.util.concurrent.LinkedBlockingQueue

// Android использует UNIX-style приоритеты (-20 до 19)
// Также есть Android-specific константы в Process

object PriorityExamples {

    fun demonstratePriorities() {
        // Установка приоритета текущего потока
        Thread {
            // Высокий приоритет (аналог userInteractive)
            Process.setThreadPriority(Process.THREAD_PRIORITY_FOREGROUND)
            // Или через Java API
            Thread.currentThread().priority = Thread.MAX_PRIORITY
        }.start()

        Thread {
            // Низкий приоритет (аналог background)
            Process.setThreadPriority(Process.THREAD_PRIORITY_BACKGROUND)
        }.start()
    }

    // Создание executor с кастомным приоритетом
    private val backgroundThreadFactory = ThreadFactory { runnable ->
        Thread(runnable).apply {
            priority = Thread.MIN_PRIORITY
            name = "BackgroundWorker"
        }
    }

    val backgroundExecutor: ThreadPoolExecutor = ThreadPoolExecutor(
        2,                      // corePoolSize
        4,                      // maximumPoolSize
        60L,                    // keepAliveTime
        TimeUnit.SECONDS,
        LinkedBlockingQueue(),
        backgroundThreadFactory
    )

    // Стандартные executors
    val ioExecutor = Executors.newCachedThreadPool()      // I/O задачи
    val cpuExecutor = Executors.newFixedThreadPool(       // CPU задачи
        Runtime.getRuntime().availableProcessors()
    )
}

// Соответствие iOS QoS и Android приоритетов
// iOS                  | Android Process Priority
// ---------------------|---------------------------
// .userInteractive     | THREAD_PRIORITY_DISPLAY (-4)
// .userInitiated       | THREAD_PRIORITY_FOREGROUND (-2)
// .default             | THREAD_PRIORITY_DEFAULT (0)
// .utility             | THREAD_PRIORITY_BACKGROUND (10)
// .background          | THREAD_PRIORITY_LOWEST (19)
```

---

## 4. Thread Pools и Dispatch Groups

### iOS: DispatchGroup

```swift
import Foundation

class ImageBatchProcessor {

    private let processingQueue = DispatchQueue(
        label: "com.app.imageProcessing",
        qos: .userInitiated,
        attributes: .concurrent
    )

    func processImages(_ urls: [URL], completion: @escaping ([UIImage]) -> Void) {
        let group = DispatchGroup()
        var results: [Int: UIImage] = [:]
        let lock = NSLock()

        for (index, url) in urls.enumerated() {
            group.enter()

            processingQueue.async {
                if let image = self.loadImage(from: url) {
                    lock.lock()
                    results[index] = image
                    lock.unlock()
                }
                group.leave()
            }
        }

        // Уведомление о завершении всех задач
        group.notify(queue: .main) {
            let sortedImages = results.sorted { $0.key < $1.key }.map { $0.value }
            completion(sortedImages)
        }
    }

    // С таймаутом
    func processImagesWithTimeout(_ urls: [URL]) -> [UIImage]? {
        let group = DispatchGroup()
        var results: [UIImage] = []
        let lock = NSLock()

        for url in urls {
            group.enter()
            processingQueue.async {
                if let image = self.loadImage(from: url) {
                    lock.lock()
                    results.append(image)
                    lock.unlock()
                }
                group.leave()
            }
        }

        // Ждём максимум 30 секунд
        let result = group.wait(timeout: .now() + 30)

        switch result {
        case .success:
            return results
        case .timedOut:
            return nil
        }
    }

    private func loadImage(from url: URL) -> UIImage? { nil }
}
```

### Android: ExecutorService и CountDownLatch

```kotlin
import java.util.concurrent.*
import java.util.concurrent.atomic.AtomicReference

class ImageBatchProcessor {

    private val executor = Executors.newFixedThreadPool(4)

    fun processImages(
        urls: List<String>,
        onComplete: (List<ByteArray>) -> Unit
    ) {
        val results = ConcurrentHashMap<Int, ByteArray>()
        val latch = CountDownLatch(urls.size)

        urls.forEachIndexed { index, url ->
            executor.execute {
                try {
                    val image = loadImage(url)
                    image?.let { results[index] = it }
                } finally {
                    latch.countDown()
                }
            }
        }

        // Ждём в отдельном потоке и уведомляем на main
        executor.execute {
            latch.await()
            val sortedImages = results.toSortedMap().values.toList()

            Handler(Looper.getMainLooper()).post {
                onComplete(sortedImages)
            }
        }
    }

    // С использованием CompletableFuture (API 24+)
    fun processImagesWithFutures(urls: List<String>): CompletableFuture<List<ByteArray>> {
        val futures = urls.map { url ->
            CompletableFuture.supplyAsync({ loadImage(url) }, executor)
        }

        return CompletableFuture.allOf(*futures.toTypedArray())
            .thenApply {
                futures.mapNotNull { it.get() }
            }
    }

    // С таймаутом
    fun processImagesWithTimeout(urls: List<String>): List<ByteArray>? {
        val latch = CountDownLatch(urls.size)
        val results = ConcurrentHashMap<Int, ByteArray>()

        urls.forEachIndexed { index, url ->
            executor.execute {
                try {
                    loadImage(url)?.let { results[index] = it }
                } finally {
                    latch.countDown()
                }
            }
        }

        // Ждём максимум 30 секунд
        val completed = latch.await(30, TimeUnit.SECONDS)

        return if (completed) {
            results.toSortedMap().values.toList()
        } else {
            null
        }
    }

    private fun loadImage(url: String): ByteArray? = null
}
```

---

## 5. Отложенное выполнение и отмена

### iOS: asyncAfter и DispatchWorkItem

```swift
import Foundation

class DelayedTaskManager {

    private var currentWorkItem: DispatchWorkItem?

    // Простое отложенное выполнение
    func executeAfterDelay() {
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            print("Выполнено через 2 секунды")
        }
    }

    // С возможностью отмены
    func scheduleTask() {
        // Отменяем предыдущую задачу
        currentWorkItem?.cancel()

        let workItem = DispatchWorkItem { [weak self] in
            guard let self = self else { return }
            self.performExpensiveOperation()
        }

        currentWorkItem = workItem

        // Отложенное выполнение
        DispatchQueue.global(qos: .userInitiated).asyncAfter(
            deadline: .now() + 0.5,
            execute: workItem
        )
    }

    func cancelCurrentTask() {
        currentWorkItem?.cancel()
        currentWorkItem = nil
    }

    // Проверка отмены внутри задачи
    func longRunningTask() {
        let workItem = DispatchWorkItem { [weak self] in
            for i in 0..<1000 {
                // Проверяем, не отменена ли задача
                if (self?.currentWorkItem?.isCancelled ?? true) {
                    print("Задача отменена на итерации \(i)")
                    return
                }
                // Выполняем работу
            }
        }

        currentWorkItem = workItem
        DispatchQueue.global().async(execute: workItem)
    }

    private func performExpensiveOperation() { }
}
```

### Android: postDelayed и removeCallbacks

```kotlin
import android.os.Handler
import android.os.Looper
import java.util.concurrent.ScheduledExecutorService
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.concurrent.Future

class DelayedTaskManager {

    private val handler = Handler(Looper.getMainLooper())
    private var currentRunnable: Runnable? = null
    private val scheduler: ScheduledExecutorService =
        Executors.newSingleThreadScheduledExecutor()
    private var currentFuture: Future<*>? = null

    // Простое отложенное выполнение
    fun executeAfterDelay() {
        handler.postDelayed({
            println("Выполнено через 2 секунды")
        }, 2000)
    }

    // С возможностью отмены через Handler
    fun scheduleTask() {
        // Отменяем предыдущую задачу
        currentRunnable?.let { handler.removeCallbacks(it) }

        val runnable = Runnable {
            performExpensiveOperation()
        }

        currentRunnable = runnable
        handler.postDelayed(runnable, 500)
    }

    fun cancelCurrentTask() {
        currentRunnable?.let { handler.removeCallbacks(it) }
        currentRunnable = null
    }

    // С использованием ScheduledExecutorService
    fun scheduleWithExecutor() {
        currentFuture?.cancel(true)

        currentFuture = scheduler.schedule({
            performExpensiveOperation()
        }, 500, TimeUnit.MILLISECONDS)
    }

    fun cancelExecutorTask() {
        currentFuture?.cancel(true)
        currentFuture = null
    }

    // Проверка отмены внутри задачи
    fun longRunningTask() {
        currentFuture = scheduler.submit {
            for (i in 0 until 1000) {
                // Проверяем, не прервана ли задача
                if (Thread.currentThread().isInterrupted) {
                    println("Задача отменена на итерации $i")
                    return@submit
                }
                // Выполняем работу
            }
        }
    }

    fun cleanup() {
        scheduler.shutdown()
    }

    private fun performExpensiveOperation() { }
}
```

---

## 6. Когда использовать Legacy vs Modern Async

### Сравнение подходов

| Сценарий | iOS Legacy (GCD) | iOS Modern | Android Legacy | Android Modern |
|----------|------------------|------------|----------------|----------------|
| Простой UI update | DispatchQueue.main | @MainActor | Handler(mainLooper) | Dispatchers.Main |
| Параллельная загрузка | DispatchGroup | TaskGroup | ExecutorService | coroutineScope |
| Отмена задач | DispatchWorkItem | Task.cancel() | Future.cancel() | Job.cancel() |
| Таймауты | wait(timeout:) | withTimeout | await(timeout) | withTimeout |
| Последовательность | Serial queue | async let | Single executor | suspend fun |

### Когда использовать Legacy

```swift
// iOS: GCD всё ещё актуален для:

// 1. Низкоуровневая синхронизация
class ThreadSafeCache<T> {
    private var cache: [String: T] = [:]
    private let queue = DispatchQueue(
        label: "com.app.cache",
        attributes: .concurrent
    )

    func get(_ key: String) -> T? {
        queue.sync { cache[key] }
    }

    func set(_ key: String, value: T) {
        queue.async(flags: .barrier) {
            self.cache[key] = value
        }
    }
}

// 2. Работа с legacy API, которое требует completion handlers
func legacyNetworkCall(completion: @escaping (Data?) -> Void) {
    DispatchQueue.global().async {
        // Сетевой запрос
        let data = Data()
        DispatchQueue.main.async {
            completion(data)
        }
    }
}

// 3. Точный контроль над QoS и приоритетами
let criticalQueue = DispatchQueue(
    label: "com.app.critical",
    qos: .userInteractive,
    attributes: [],
    autoreleaseFrequency: .workItem,
    target: nil
)
```

```kotlin
// Android: Handler/Executors всё ещё актуальны для:

// 1. Работа с Looper-based APIs (SurfaceView, MediaCodec)
class VideoRenderer(private val surface: Surface) {
    private val renderThread = HandlerThread("RenderThread").apply { start() }
    private val renderHandler = Handler(renderThread.looper)

    fun queueFrame(frame: ByteArray) {
        renderHandler.post {
            // Рендеринг на surface
        }
    }
}

// 2. Периодические задачи с точным таймингом
class PeriodicTask {
    private val handler = Handler(Looper.getMainLooper())
    private val interval = 16L // ~60 FPS

    private val frameCallback = object : Runnable {
        override fun run() {
            updateFrame()
            handler.postDelayed(this, interval)
        }
    }

    fun start() = handler.post(frameCallback)
    fun stop() = handler.removeCallbacks(frameCallback)
    private fun updateFrame() { }
}

// 3. Интеграция с Java-библиотеками
class JavaLibraryWrapper {
    private val executor = Executors.newSingleThreadExecutor()

    fun callLegacyJavaCode(callback: LegacyCallback) {
        executor.execute {
            // Вызов Java библиотеки
            callback.onResult(byteArrayOf())
        }
    }
}

interface LegacyCallback {
    fun onResult(data: ByteArray)
}
```

---

## 7. Шесть распространённых ошибок

### Ошибка 1: Блокировка главного потока

```swift
// iOS — НЕПРАВИЛЬНО
class BadExample1 {
    func loadData() {
        let data = URLSession.shared.synchronousDataTask(with: url) // Блокирует UI!
        updateUI(with: data)
    }

    // ПРАВИЛЬНО
    func loadDataCorrectly() {
        DispatchQueue.global().async {
            let data = self.fetchData()
            DispatchQueue.main.async {
                self.updateUI(with: data)
            }
        }
    }

    private var url: URL { URL(string: "https://example.com")! }
    private func fetchData() -> Data { Data() }
    private func updateUI(with data: Data) { }
}
```

```kotlin
// Android — НЕПРАВИЛЬНО
class BadExample1 {
    fun loadData() {
        val data = networkClient.blockingCall() // ANR через 5 секунд!
        updateUI(data)
    }

    // ПРАВИЛЬНО
    fun loadDataCorrectly() {
        Executors.newSingleThreadExecutor().execute {
            val data = fetchData()
            Handler(Looper.getMainLooper()).post {
                updateUI(data)
            }
        }
    }

    private val networkClient = object {
        fun blockingCall(): ByteArray = byteArrayOf()
    }
    private fun fetchData(): ByteArray = byteArrayOf()
    private fun updateUI(data: ByteArray) { }
}
```

### Ошибка 2: Retain cycle в closure/lambda

```swift
// iOS — НЕПРАВИЛЬНО
class BadExample2 {
    var data: Data?

    func startLoading() {
        DispatchQueue.global().async {
            self.data = self.fetchData() // Strong reference cycle!
        }
    }

    // ПРАВИЛЬНО
    func startLoadingCorrectly() {
        DispatchQueue.global().async { [weak self] in
            guard let self = self else { return }
            self.data = self.fetchData()
        }
    }

    private func fetchData() -> Data { Data() }
}
```

```kotlin
// Android — НЕПРАВИЛЬНО
class BadExample2 : Activity() {
    private var data: ByteArray? = null
    private val executor = Executors.newSingleThreadExecutor()

    fun startLoading() {
        executor.execute {
            data = fetchData() // Activity может быть уничтожена!
        }
    }

    // ПРАВИЛЬНО — использовать WeakReference
    fun startLoadingCorrectly() {
        val weakThis = WeakReference(this)
        executor.execute {
            weakThis.get()?.let { activity ->
                activity.data = activity.fetchData()
            }
        }
    }

    private fun fetchData(): ByteArray = byteArrayOf()
}
```

### Ошибка 3: Race condition при доступе к данным

```swift
// iOS — НЕПРАВИЛЬНО
class BadExample3 {
    var counter = 0

    func incrementFromMultipleThreads() {
        for _ in 0..<1000 {
            DispatchQueue.global().async {
                self.counter += 1 // Race condition!
            }
        }
    }

    // ПРАВИЛЬНО — использовать serial queue или barrier
    private let syncQueue = DispatchQueue(label: "com.app.sync")
    var safeCounter = 0

    func incrementSafely() {
        for _ in 0..<1000 {
            DispatchQueue.global().async {
                self.syncQueue.sync {
                    self.safeCounter += 1
                }
            }
        }
    }
}
```

```kotlin
// Android — НЕПРАВИЛЬНО
class BadExample3 {
    var counter = 0

    fun incrementFromMultipleThreads() {
        val executor = Executors.newFixedThreadPool(4)
        repeat(1000) {
            executor.execute {
                counter++ // Race condition!
            }
        }
    }

    // ПРАВИЛЬНО — использовать AtomicInteger или synchronized
    private val safeCounter = AtomicInteger(0)

    fun incrementSafely() {
        val executor = Executors.newFixedThreadPool(4)
        repeat(1000) {
            executor.execute {
                safeCounter.incrementAndGet()
            }
        }
    }
}
```

### Ошибка 4: Deadlock при вложенных sync

```swift
// iOS — НЕПРАВИЛЬНО: DEADLOCK!
class BadExample4 {
    let queue = DispatchQueue(label: "com.app.queue")

    func methodA() {
        queue.sync {
            methodB() // Deadlock — уже на этой очереди!
        }
    }

    func methodB() {
        queue.sync {
            // Никогда не выполнится
        }
    }

    // ПРАВИЛЬНО — не использовать sync внутри sync на той же очереди
    func methodASafe() {
        queue.async {
            self.methodBSafe()
        }
    }

    func methodBSafe() {
        // Не использовать sync, если уже на очереди
    }
}
```

```kotlin
// Android — НЕПРАВИЛЬНО: DEADLOCK!
class BadExample4 {
    private val lock = Object()

    fun methodA() {
        synchronized(lock) {
            methodB() // Потенциальный deadlock с другими locks
        }
    }

    fun methodB() {
        synchronized(lock) {
            // Re-entrant в Kotlin, но опасно с разными locks
        }
    }

    // ПРАВИЛЬНО — использовать ReentrantLock или избегать вложенности
    private val reentrantLock = ReentrantLock()

    fun methodASafe() {
        reentrantLock.lock()
        try {
            methodBSafe()
        } finally {
            reentrantLock.unlock()
        }
    }

    fun methodBSafe() {
        // Безопасно — ReentrantLock позволяет повторный захват
    }
}
```

### Ошибка 5: Забытый leave() в DispatchGroup

```swift
// iOS — НЕПРАВИЛЬНО: группа никогда не завершится
class BadExample5 {
    func processItems(_ items: [String]) {
        let group = DispatchGroup()

        for item in items {
            group.enter()
            DispatchQueue.global().async {
                guard self.isValid(item) else {
                    return // Забыли group.leave()!
                }
                self.process(item)
                group.leave()
            }
        }

        group.wait() // Бесконечное ожидание
    }

    // ПРАВИЛЬНО — использовать defer
    func processItemsCorrectly(_ items: [String]) {
        let group = DispatchGroup()

        for item in items {
            group.enter()
            DispatchQueue.global().async {
                defer { group.leave() } // Гарантированный вызов

                guard self.isValid(item) else { return }
                self.process(item)
            }
        }

        group.wait()
    }

    private func isValid(_ item: String) -> Bool { true }
    private func process(_ item: String) { }
}
```

```kotlin
// Android — НЕПРАВИЛЬНО: CountDownLatch никогда не достигнет 0
class BadExample5 {
    fun processItems(items: List<String>) {
        val latch = CountDownLatch(items.size)
        val executor = Executors.newFixedThreadPool(4)

        items.forEach { item ->
            executor.execute {
                if (!isValid(item)) {
                    return@execute // Забыли countDown()!
                }
                process(item)
                latch.countDown()
            }
        }

        latch.await() // Бесконечное ожидание
    }

    // ПРАВИЛЬНО — использовать try-finally
    fun processItemsCorrectly(items: List<String>) {
        val latch = CountDownLatch(items.size)
        val executor = Executors.newFixedThreadPool(4)

        items.forEach { item ->
            executor.execute {
                try {
                    if (!isValid(item)) return@execute
                    process(item)
                } finally {
                    latch.countDown() // Гарантированный вызов
                }
            }
        }

        latch.await()
    }

    private fun isValid(item: String): Boolean = true
    private fun process(item: String) { }
}
```

### Ошибка 6: UI-обновление не на главном потоке

```swift
// iOS — НЕПРАВИЛЬНО
class BadExample6 {
    func updateAfterNetworkCall() {
        DispatchQueue.global().async {
            let result = self.fetchData()
            self.label.text = result // CRASH или undefined behavior!
        }
    }

    // ПРАВИЛЬНО
    func updateAfterNetworkCallCorrectly() {
        DispatchQueue.global().async {
            let result = self.fetchData()
            DispatchQueue.main.async {
                self.label.text = result
            }
        }
    }

    private var label: UILabel { UILabel() }
    private func fetchData() -> String { "" }
}
```

```kotlin
// Android — НЕПРАВИЛЬНО
class BadExample6 {
    private lateinit var textView: TextView

    fun updateAfterNetworkCall() {
        Executors.newSingleThreadExecutor().execute {
            val result = fetchData()
            textView.text = result // CalledFromWrongThreadException!
        }
    }

    // ПРАВИЛЬНО
    fun updateAfterNetworkCallCorrectly() {
        Executors.newSingleThreadExecutor().execute {
            val result = fetchData()
            Handler(Looper.getMainLooper()).post {
                textView.text = result
            }
            // Или через Activity
            // runOnUiThread { textView.text = result }
        }
    }

    private fun fetchData(): String = ""
}
```

---

## 8. Три ментальные модели

### Модель 1: Очередь vs Цикл сообщений

```
iOS (GCD):                          Android (Handler/Looper):

┌─────────────────┐                 ┌─────────────────┐
│  DispatchQueue  │                 │     Looper      │
│  ┌───────────┐  │                 │  ┌───────────┐  │
│  │  Task 1   │──┼──► Thread 1     │  │  Message  │  │
│  │  Task 2   │──┼──► Thread 2     │  │  Message  │──┼──► Один Thread
│  │  Task 3   │──┼──► Thread 3     │  │  Runnable │  │    обрабатывает
│  │  Task 4   │  │                 │  │  Message  │  │    последовательно
│  └───────────┘  │                 │  └───────────┘  │
└─────────────────┘                 └─────────────────┘
                                              ▲
    Пул потоков                               │
    распределяет                      Handler.post()
    задачи                            отправляет
```

**iOS GCD** — абстракция над пулом потоков. Вы думаете о задачах, система думает о потоках.

**Android Handler/Looper** — паттерн message loop. Один поток обрабатывает сообщения последовательно.

### Модель 2: Синхронизация данных

```
┌─────────────────────────────────────────────────────────┐
│                   SHARED STATE                          │
│                   (общие данные)                        │
└─────────────────────────────────────────────────────────┘
         ▲                                    ▲
         │                                    │
    ┌────┴────┐                          ┌────┴────┐
    │  iOS    │                          │ Android │
    └────┬────┘                          └────┬────┘
         │                                    │
    ┌────▼────────────┐              ┌────────▼────────┐
    │ Serial Queue    │              │ synchronized    │
    │ или             │              │ или             │
    │ Concurrent +    │              │ AtomicXxx       │
    │ Barrier         │              │ или             │
    │ или             │              │ Single Executor │
    │ NSLock          │              │ или             │
    └─────────────────┘              │ Lock            │
                                     └─────────────────┘
```

Правило: **Один механизм синхронизации на один ресурс**

### Модель 3: Жизненный цикл асинхронных задач

```
┌─────────┐    ┌──────────┐    ┌───────────┐    ┌──────────┐
│ Created │───►│ Scheduled│───►│ Executing │───►│ Completed│
└─────────┘    └──────────┘    └───────────┘    └──────────┘
                    │               │
                    │               │
                    ▼               ▼
               ┌─────────┐    ┌──────────┐
               │Cancelled│    │ Cancelled│
               │(до start)│   │(во время)│
               └─────────┘    └──────────┘

iOS:
- Created: DispatchWorkItem создан
- Scheduled: async/asyncAfter вызван
- Executing: работает на потоке
- Cancelled: workItem.cancel()

Android:
- Created: Runnable/Callable создан
- Scheduled: post/execute вызван
- Executing: работает на потоке
- Cancelled: removeCallbacks/future.cancel()
```

---

## 9. Quiz

### Вопрос 1

Что произойдёт при выполнении этого кода?

```swift
let queue = DispatchQueue(label: "test")
queue.sync {
    print("A")
    queue.sync {
        print("B")
    }
    print("C")
}
```

<details>
<summary>Ответ</summary>

**Deadlock**. Внешний `sync` ждёт завершения блока, а внутренний `sync` пытается добавить задачу в ту же serial queue и ждёт её выполнения. Но внешний блок не может завершиться, пока не выполнится внутренний — замкнутый круг.

Напечатается только "A", после чего приложение зависнет.

**Решение**: не использовать `sync` для вызова на той же очереди или использовать concurrent queue с разными ключами.
</details>

### Вопрос 2

Почему этот Android-код может вызвать ANR (Application Not Responding)?

```kotlin
class MyActivity : Activity() {
    private val handler = Handler(Looper.getMainLooper())

    fun processLargeFile() {
        handler.post {
            val file = File("/sdcard/large_file.bin")
            val data = file.readBytes() // 500MB file
            processData(data)
        }
    }
}
```

<details>
<summary>Ответ</summary>

`handler.post` с `Looper.getMainLooper()` выполняет код на **главном потоке**. Чтение 500MB файла — блокирующая I/O операция, которая заблокирует UI на несколько секунд.

Android показывает ANR-диалог, если главный поток заблокирован более 5 секунд.

**Решение**: выполнять I/O на фоновом потоке:
```kotlin
Executors.newSingleThreadExecutor().execute {
    val data = file.readBytes()
    handler.post { processData(data) }
}
```
</details>

### Вопрос 3

Сколько раз выполнится блок completion?

```swift
func fetchAllData(completion: @escaping (Int) -> Void) {
    let group = DispatchGroup()
    var total = 0

    for i in 1...3 {
        group.enter()
        DispatchQueue.global().async {
            total += i
            group.leave()
        }
    }

    group.notify(queue: .main) {
        completion(total)
    }

    group.notify(queue: .main) {
        completion(total * 2)
    }
}
```

<details>
<summary>Ответ</summary>

**Два раза**. Можно добавить несколько `notify` блоков к одной DispatchGroup, и все они будут вызваны после завершения группы.

Первый вызов: `completion(total)` — значение может быть от 0 до 6 из-за race condition при `total += i`

Второй вызов: `completion(total * 2)`

**Важно**: значение `total` непредсказуемо из-за race condition. Для корректной работы нужна синхронизация:
```swift
let lock = NSLock()
lock.lock()
total += i
lock.unlock()
```
</details>

---

## Связь с другими темами

[[ios-gcd-deep-dive]] — Grand Central Dispatch — основа legacy-конкурентности на iOS. Заметка углублённо разбирает dispatch queues (serial, concurrent, main), Quality of Service классы, dispatch groups, semaphores и barrier blocks. Особое внимание уделено опасностям: thread explosion при слишком большом количестве concurrent задач, deadlock при sync вызове на текущей очереди, priority inversion. Эти знания необходимы для поддержки legacy iOS-кода и миграции на Swift Concurrency.

[[android-handler-looper]] — Handler/Looper/MessageQueue — это внутренний механизм межпоточной коммуникации в Android. Заметка раскрывает, как Main Looper обрабатывает сообщения, как Handler привязывается к конкретному потоку, и почему HandlerThread используется для фоновых операций с последовательной обработкой. Понимание этого механизма объясняет, почему runOnUiThread работает именно так и как устроен Dispatchers.Main под капотом в Kotlin Coroutines.

[[concurrency-vs-parallelism]] — Фундаментальное различие между конкурентностью (interleaving на одном ядре) и параллелизмом (одновременное выполнение на нескольких ядрах) определяет поведение GCD и Handler/Looper. Заметка объясняет модели потоков, scheduling алгоритмы и synchronization primitives (mutex, semaphore, monitor), которые являются основой для понимания race conditions и deadlocks в legacy-коде обеих платформ.

---

## Источники и дальнейшее чтение

- Neuburg M. (2023). *iOS Programming Fundamentals with Swift.* — Подробно разбирает GCD, OperationQueue, Thread, а также переход к Swift Concurrency. Объясняет, почему Apple создала structured concurrency для замены GCD-паттернов.
- Meier R. (2022). *Professional Android.* — Освещает Handler/Looper, AsyncTask (deprecated), Executors и переход к Kotlin Coroutines. Даёт полную картину эволюции конкурентности на Android от ранних версий до современных API.
