---
title: "Grand Central Dispatch: глубокое погружение"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/concurrency
  - type/deep-dive
  - level/advanced
related:
  - "[[ios-async-evolution]]"
  - "[[ios-async-await]]"
  - "[[ios-threading-fundamentals]]"
prerequisites:
  - "[[ios-threading-fundamentals]]"
  - "[[ios-app-components]]"
---

# Grand Central Dispatch - Глубокое Погружение

## TL;DR

Grand Central Dispatch (GCD) - это низкоуровневая C-библиотека от Apple для управления конкурентным выполнением задач через очереди вместо потоков. Основана на libdispatch, работает через пулы потоков и кооперативную многопоточность. Предоставляет типы очередей (main, global, private), систему Quality of Service, инструменты синхронизации (semaphores, barriers, groups) и примитивы для событий (DispatchSource). С iOS 13+ частично заменяется async/await, но остается критически важной для событийного программирования и низкоуровневой оптимизации.

**Ключевые концепции:**
- Очереди вместо потоков - система управляет пулом
- QoS определяет приоритет выполнения через [[os-scheduling]]
- Барьеры для безопасных read/write паттернов
- DispatchGroup для координации множества задач
- Target queues для иерархии выполнения

---

## Аналогия: Ресторанная Кухня

Представьте GCD как кухню ресторана:

```
┌─────────────────────────────────────────────────────────────┐
│  РЕСТОРАН (Ваше приложение)                                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  MAIN QUEUE (Зал ресторана)                                 │
│  ┌──────────────────────────────────────┐                   │
│  │ Официант (Main Thread)               │                   │
│  │ - Принимает заказы (UI events)       │                   │
│  │ - Подает блюда (UI updates)          │                   │
│  │ - Только ОДИН официант!              │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
│  GLOBAL QUEUES (Кухня с поварами)                           │
│  ┌──────────────────────────────────────┐                   │
│  │ User-Interactive: Су-шеф (срочно!)   │ ← QoS.userInitiated
│  │ User-Initiated: Основные повара      │                   │
│  │ Utility: Помощники повара            │                   │
│  │ Background: Посудомойщик             │                   │
│  └──────────────────────────────────────┘                   │
│                                                               │
│  PRIVATE QUEUES (Специальные станции)                       │
│  ┌──────────────────────────────────────┐                   │
│  │ Serial: Гриль-станция (по очереди)   │                   │
│  │ Concurrent: Салатная станция (параллельно) │             │
│  └──────────────────────────────────────┘                   │
│                                                               │
│  DISPATCH GROUP (Комплексный заказ)                         │
│  ┌──────────────────────────────────────┐                   │
│  │ Стол 5: Суп + Основное + Десерт      │                   │
│  │ → Уведомить когда ВСЁ готово         │                   │
│  └──────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────┘
```

**Dispatch Barrier** = Генеральная уборка кухни (все останавливаются, один моет, потом все продолжают)

---

## Архитектура libdispatch

### Внутреннее Устройство

```
┌─────────────────────────────────────────────────────────────────┐
│                     LIBDISPATCH ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  User Space (Your Code)                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ DispatchQueue.main.async { ... }                           │ │
│  │ DispatchQueue.global(qos: .userInitiated).async { ... }   │ │
│  └─────────────────────┬──────────────────────────────────────┘ │
│                        │                                          │
│                        ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ DISPATCH QUEUE (FIFO Structure)                            │ │
│  │ ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐                    │ │
│  │ │Task 1│→ │Task 2│→ │Task 3│→ │Task 4│                    │ │
│  │ └──────┘  └──────┘  └──────┘  └──────┘                    │ │
│  │ QoS: .userInitiated  Target: root queue                   │ │
│  └─────────────────────┬──────────────────────────────────────┘ │
│                        │                                          │
│                        ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ DISPATCH QUEUE MANAGER                                     │ │
│  │ - Scheduling algorithm                                     │ │
│  │ - Priority inversion handling                              │ │
│  │ - Thread pool management                                   │ │
│  └─────────────────────┬──────────────────────────────────────┘ │
│                        │                                          │
│                        ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ THREAD POOL (Cooperative Threading)                        │ │
│  │ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐              │ │
│  │ │Thread 1│ │Thread 2│ │Thread 3│ │Thread N│              │ │
│  │ │ Active │ │ Active │ │ Idle   │ │ Idle   │              │ │
│  │ └────────┘ └────────┘ └────────┘ └────────┘              │ │
│  │ Pool size: MIN(64, 2 * core_count + 4)                    │ │
│  └─────────────────────┬──────────────────────────────────────┘ │
│                        │                                          │
│  Kernel Space          ▼                                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ KERNEL SCHEDULER (XNU)                                     │ │
│  │ - CPU core assignment                                      │ │
│  │ - Context switching                                        │ │
│  │ - Priority management                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘

Key Components:
1. Dispatch Objects (queues, groups, semaphores)
2. Work Items (blocks/closures to execute)
3. Thread Pool (worker threads managed by libdispatch)
4. Kernel Integration (kqueue, workqueue APIs)
```

### Кооперативная Многопоточность

GCD использует кооперативную модель вместо создания потоков напрямую:

```swift
// ❌ ПЛОХО: Ручное управление потоками (Thread Explosion)
class BadThreadManager {
    func downloadImages(_ urls: [URL]) {
        for url in urls {
            // Создаем 1000 потоков для 1000 URL!
            Thread.detachNewThread {
                let data = try? Data(contentsOf: url)
                // Context switching nightmare
            }
        }
    }
}

// ✅ ХОРОШО: GCD управляет пулом потоков
class GoodDispatchManager {
    func downloadImages(_ urls: [URL]) {
        let queue = DispatchQueue(label: "com.app.downloads",
                                   attributes: .concurrent)

        for url in urls {
            queue.async {
                // GCD распределяет по доступным потокам из пула
                let data = try? Data(contentsOf: url)
            }
        }
        // Максимум ~64 потока независимо от количества задач
    }
}
```

---

## Типы Очередей

### Main Queue - Главная Очередь

```swift
// Main Queue: Serial, работает на главном потоке UI
final class MainQueueExample {
    func updateUI() {
        // ✅ ПРАВИЛЬНО: UI обновления на main queue
        DispatchQueue.main.async {
            self.label.text = "Updated!"
            self.view.backgroundColor = .systemBlue
        }
    }

    // ❌ ОПАСНО: Deadlock при sync на main из main
    func deadlockExample() {
        // Выполняется на main queue
        print("Before sync")

        DispatchQueue.main.sync {
            // Main queue ждет себя же - DEADLOCK!
            print("Never printed")
        }

        print("Never reached")
    }

    // ✅ ПРАВИЛЬНО: sync с background queue
    func correctSync() {
        DispatchQueue.global().async {
            // На background queue

            let result = self.heavyComputation()

            // Sync переключение на main
            DispatchQueue.main.sync {
                self.label.text = "\(result)"
            }
        }
    }
}
```

### Global Queues - Глобальные Очереди

```swift
// Global Queues: Concurrent, разные QoS уровни
final class GlobalQueueExample {

    // User Interactive: Немедленный ответ (<100ms)
    func loadCriticalData() {
        DispatchQueue.global(qos: .userInteractive).async {
            // Анимации, события, критичные для UI
            let data = self.fetchFromCache()

            DispatchQueue.main.async {
                self.updateUI(with: data)
            }
        }
    }

    // User Initiated: Быстрый ответ (~секунды)
    func performSearch(query: String) {
        DispatchQueue.global(qos: .userInitiated).async {
            // Пользователь ждет результатов
            let results = self.searchDatabase(query)

            DispatchQueue.main.async {
                self.display(results)
            }
        }
    }

    // Utility: Длительные операции (секунды-минуты)
    func downloadLargeFile(url: URL) {
        DispatchQueue.global(qos: .utility).async {
            // Загрузки с progress bar
            let data = try? Data(contentsOf: url)

            DispatchQueue.main.async {
                self.saveFile(data)
            }
        }
    }

    // Background: Незаметные для пользователя задачи
    func syncDatabase() {
        DispatchQueue.global(qos: .background).async {
            // Prefetch, очистка кэша, аналитика
            self.performDatabaseMaintenance()
        }
    }
}
```

### Private Queues - Пользовательские Очереди

```swift
// Private Queues: Serial или Concurrent с настройками
final class PrivateQueueExample {

    // Serial Queue: Строгий порядок выполнения
    private let serialQueue = DispatchQueue(label: "com.app.serial")

    // Concurrent Queue: Параллельное выполнение
    private let concurrentQueue = DispatchQueue(
        label: "com.app.concurrent",
        attributes: .concurrent
    )

    // Queue с QoS
    private let utilityQueue = DispatchQueue(
        label: "com.app.utility",
        qos: .utility,
        attributes: .concurrent
    )

    func serialExample() {
        // ✅ Гарантированный порядок
        serialQueue.async { print("Task 1") }
        serialQueue.async { print("Task 2") }
        serialQueue.async { print("Task 3") }
        // Всегда: Task 1 → Task 2 → Task 3
    }

    func concurrentExample() {
        // ⚠️ Порядок не гарантирован
        concurrentQueue.async { print("Task A") }
        concurrentQueue.async { print("Task B") }
        concurrentQueue.async { print("Task C") }
        // Может быть: B → A → C или C → B → A
    }
}
```

---

## Quality of Service и Priority Inversion

### QoS Система

```
┌────────────────────────────────────────────────────────────────┐
│                    QoS PRIORITY HIERARCHY                       │
├────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Interactive (Highest Priority)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ UI animations, event handling                             │  │
│  │ CPU: High | Energy: High | Latency: <100ms               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↑                                     │
│  User Initiated                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ User-requested tasks (search, open file)                 │  │
│  │ CPU: High | Energy: High | Latency: ~seconds             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↑                                     │
│  Default (Unspecified)                                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ General tasks, no specific QoS                           │  │
│  │ CPU: Medium | Energy: Medium | Adaptive                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↑                                     │
│  Utility                                                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Long-running computations with progress                  │  │
│  │ CPU: Low | Energy: Efficient | Latency: seconds-minutes  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            ↑                                     │
│  Background (Lowest Priority)                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Maintenance, cleanup, prefetch                            │  │
│  │ CPU: Very Low | Energy: Very Efficient | User invisible  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  See also: [[os-scheduling]] for kernel-level details          │
└────────────────────────────────────────────────────────────────┘
```

### Priority Inversion Problem

```swift
// Priority Inversion: низкоприоритетная задача блокирует высокоприоритетную
final class PriorityInversionExample {
    private let lock = NSLock()
    private var sharedResource: String = ""

    // ❌ ПРОБЛЕМА: Priority Inversion
    func demonstratePriorityInversion() {
        // Low priority задача захватывает lock
        DispatchQueue.global(qos: .background).async {
            self.lock.lock()
            print("Background: Lock acquired")
            Thread.sleep(forTimeInterval: 5) // Долгая работа
            self.lock.unlock()
        }

        Thread.sleep(forTimeInterval: 0.1)

        // High priority задача ждет lock от background!
        DispatchQueue.global(qos: .userInteractive).async {
            print("UI: Waiting for lock...")
            self.lock.lock() // БЛОКИРОВАНА низким приоритетом!
            print("UI: Finally got lock")
            self.lock.unlock()
        }
    }

    // ✅ РЕШЕНИЕ: QoS Inference (автоматическое повышение)
    func gcdAutoSolution() {
        let serialQueue = DispatchQueue(label: "com.app.serial")

        // Low priority задача
        serialQueue.async {
            print("Background task running")
            Thread.sleep(forTimeInterval: 2)
        }

        // High priority задача - GCD автоматически повысит QoS
        serialQueue.async(qos: .userInteractive) {
            // GCD временно повышает приоритет предыдущей задачи!
            print("UI task running - no starvation")
        }
    }

    // ✅ АЛЬТЕРНАТИВА: Явное указание QoS для очереди
    func explicitQoS() {
        let queue = DispatchQueue(
            label: "com.app.shared",
            qos: .userInitiated // Все задачи получают этот QoS
        )

        queue.async {
            self.processSharedResource()
        }
    }
}
```

---

## DispatchGroup - Координация Задач

```swift
// DispatchGroup: Ожидание завершения множества асинхронных задач
final class DispatchGroupExample {

    // ✅ Базовое использование: enter/leave
    func downloadMultipleImages(urls: [URL]) {
        let group = DispatchGroup()
        var images: [UIImage] = []

        for url in urls {
            group.enter() // Увеличиваем счетчик

            URLSession.shared.dataTask(with: url) { data, _, error in
                defer { group.leave() } // Уменьшаем счетчик

                if let data = data, let image = UIImage(data: data) {
                    images.append(image)
                }
            }.resume()
        }

        // Notify вызывается когда счетчик == 0
        group.notify(queue: .main) {
            print("All images downloaded: \(images.count)")
            self.displayGallery(images)
        }
    }

    // ✅ Автоматический enter/leave через async
    func processFilesInGroup() {
        let group = DispatchGroup()
        let queue = DispatchQueue.global(qos: .utility)

        for i in 1...5 {
            queue.async(group: group) { // Автоматический enter
                print("Processing file \(i)")
                Thread.sleep(forTimeInterval: 1)
            } // Автоматический leave
        }

        group.notify(queue: .main) {
            print("All files processed!")
        }
    }

    // ✅ Ожидание с timeout
    func waitWithTimeout() {
        let group = DispatchGroup()

        group.enter()
        someAsyncOperation { group.leave() }

        // Блокирует текущий поток (не используйте на main!)
        let result = group.wait(timeout: .now() + 5)

        switch result {
        case .success:
            print("Completed in time")
        case .timedOut:
            print("Timeout exceeded")
        }
    }

    // ✅ Сложный пример: последовательные группы
    func complexWorkflow() {
        let downloadGroup = DispatchGroup()
        let processGroup = DispatchGroup()

        // Фаза 1: Загрузка
        for url in imageURLs {
            downloadGroup.enter()
            downloadImage(url) { image in
                self.tempStorage.append(image)
                downloadGroup.leave()
            }
        }

        // Фаза 2: Обработка (начнется после загрузки)
        downloadGroup.notify(queue: .global(qos: .utility)) {
            for image in self.tempStorage {
                processGroup.enter()
                self.applyFilters(image) { processed in
                    self.finalStorage.append(processed)
                    processGroup.leave()
                }
            }
        }

        // Фаза 3: Финализация
        processGroup.notify(queue: .main) {
            self.saveToDatabase(self.finalStorage)
            self.updateUI()
        }
    }

    // ❌ ОШИБКА: Несбалансированные enter/leave
    func unbalancedGroup() {
        let group = DispatchGroup()

        group.enter()
        someAsyncOperation { result in
            if result.isSuccess {
                group.leave()
            }
            // BUG: leave() не вызван при ошибке!
            // notify никогда не выполнится
        }

        group.notify(queue: .main) {
            print("This may never execute")
        }
    }

    // ✅ ИСПРАВЛЕНО: defer гарантирует вызов
    func balancedGroup() {
        let group = DispatchGroup()

        group.enter()
        someAsyncOperation { result in
            defer { group.leave() } // Всегда вызывается

            guard result.isSuccess else { return }
            processResult(result)
        }
    }
}
```

---

## DispatchSemaphore - Синхронизация

```swift
// DispatchSemaphore: Ограничение конкурентного доступа
final class DispatchSemaphoreExample {

    // ✅ Ограничение параллельных операций
    func limitConcurrentDownloads() {
        let semaphore = DispatchSemaphore(value: 3) // Макс 3 одновременно
        let queue = DispatchQueue.global(qos: .utility)

        for i in 1...10 {
            queue.async {
                semaphore.wait() // Декремент, блокирует если value = 0
                defer { semaphore.signal() } // Инкремент

                print("Download \(i) started")
                Thread.sleep(forTimeInterval: 2)
                print("Download \(i) finished")
            }
        }
        // Только 3 загрузки выполняются параллельно
    }

    // ✅ Синхронизация async → sync
    func asyncToSyncConversion() -> Data? {
        let semaphore = DispatchSemaphore(value: 0)
        var result: Data?

        URLSession.shared.dataTask(with: someURL) { data, _, _ in
            result = data
            semaphore.signal() // Разблокируем ожидание
        }.resume()

        semaphore.wait() // Блокируем до signal()
        return result
    }

    // ✅ Thread-safe доступ к ресурсу
    final class ThreadSafeCounter {
        private var value: Int = 0
        private let semaphore = DispatchSemaphore(value: 1) // Binary semaphore = mutex

        func increment() {
            semaphore.wait()
            value += 1
            semaphore.signal()
        }

        func getValue() -> Int {
            semaphore.wait()
            defer { semaphore.signal() }
            return value
        }
    }

    // ❌ DEADLOCK: Wait на main queue
    func deadlockExample() {
        let semaphore = DispatchSemaphore(value: 0)

        DispatchQueue.main.async {
            semaphore.signal()
        }

        // DEADLOCK: main queue ждет semaphore,
        // но signal() в main queue не может выполниться!
        semaphore.wait()
    }

    // ✅ ПРАВИЛЬНО: Wait на background queue
    func correctSemaphoreUsage() {
        let semaphore = DispatchSemaphore(value: 0)

        DispatchQueue.main.async {
            semaphore.signal()
        }

        DispatchQueue.global().async {
            semaphore.wait() // Безопасно
            print("Signaled!")
        }
    }

    // ⚠️ Semaphore vs Lock: когда использовать
    func comparisonExample() {
        // Semaphore: для ограничения количества
        let downloadSemaphore = DispatchSemaphore(value: 5)

        // Lock: для взаимоисключения (binary semaphore)
        let lock = NSLock()

        // Для простого mutex лучше NSLock (производительнее)
        lock.lock()
        sharedResource.modify()
        lock.unlock()
    }
}
```

---

## DispatchWorkItem - Управление Задачами

```swift
// DispatchWorkItem: Отмена и уведомления для задач
final class DispatchWorkItemExample {

    private var currentSearchItem: DispatchWorkItem?

    // ✅ Отмена предыдущего поиска при новом вводе
    func searchWithCancellation(query: String) {
        // Отменяем предыдущий поиск
        currentSearchItem?.cancel()

        // Создаем новую задачу
        let workItem = DispatchWorkItem { [weak self] in
            // Проверяем отмену перед тяжелыми операциями
            guard !Thread.current.isCancelled else {
                print("Search cancelled for: \(query)")
                return
            }

            let results = self?.performSearch(query)

            guard !Thread.current.isCancelled else { return }

            DispatchQueue.main.async {
                self?.displayResults(results ?? [])
            }
        }

        currentSearchItem = workItem
        DispatchQueue.global(qos: .userInitiated).async(execute: workItem)
    }

    // ✅ QoS и flags
    func workItemWithQoS() {
        let workItem = DispatchWorkItem(
            qos: .userInitiated,
            flags: [.enforceQoS, .assignCurrentContext]
        ) {
            print("Task with explicit QoS")
        }

        DispatchQueue.global().async(execute: workItem)

        // Ожидание завершения
        workItem.wait()
        print("Task completed")
    }

    // ✅ Notify при завершении
    func workItemWithNotification() {
        let workItem = DispatchWorkItem {
            print("Doing heavy work...")
            Thread.sleep(forTimeInterval: 2)
        }

        workItem.notify(queue: .main) {
            print("Work completed, updating UI")
        }

        DispatchQueue.global().async(execute: workItem)
    }

    // ✅ Debounce паттерн
    final class SearchDebouncer {
        private var workItem: DispatchWorkItem?
        private let delay: TimeInterval

        init(delay: TimeInterval = 0.3) {
            self.delay = delay
        }

        func debounce(action: @escaping () -> Void) {
            workItem?.cancel()

            let newItem = DispatchWorkItem(block: action)
            workItem = newItem

            DispatchQueue.main.asyncAfter(
                deadline: .now() + delay,
                execute: newItem
            )
        }
    }

    // Использование debouncer
    private let searchDebouncer = SearchDebouncer(delay: 0.3)

    func textDidChange(_ text: String) {
        searchDebouncer.debounce { [weak self] in
            self?.performSearch(text)
        }
    }

    // ✅ Barrier work item
    func barrierWorkItem() {
        let queue = DispatchQueue(label: "com.app.queue", attributes: .concurrent)

        let barrierItem = DispatchWorkItem(flags: .barrier) {
            print("Exclusive access - barrier")
        }

        queue.async { print("Task 1") }
        queue.async { print("Task 2") }
        queue.async(execute: barrierItem) // Ждет 1 и 2, блокирует 3 и 4
        queue.async { print("Task 3") }
        queue.async { print("Task 4") }
    }
}
```

---

## DispatchSource - Событийное Программирование

```swift
// DispatchSource: Мониторинг системных событий
final class DispatchSourceExample {

    // ✅ Timer source (предпочтительнее чем Timer для точности)
    func createRepeatingTimer() -> DispatchSourceTimer {
        let timer = DispatchSource.makeTimerSource(
            flags: [],
            queue: DispatchQueue.global(qos: .utility)
        )

        timer.schedule(
            deadline: .now() + 1.0,
            repeating: 1.0,
            leeway: .milliseconds(100) // Допустимая погрешность для энергоэффективности
        )

        timer.setEventHandler { [weak self] in
            self?.updateMetrics()
        }

        timer.resume() // ВАЖНО: source приостановлены по умолчанию!
        return timer
    }

    // ✅ File monitoring source
    final class FileWatcher {
        private var source: DispatchSourceFileSystemObject?
        private let fileDescriptor: Int32

        init?(path: String) {
            fileDescriptor = open(path, O_EVTONLY)
            guard fileDescriptor >= 0 else { return nil }

            source = DispatchSource.makeFileSystemObjectSource(
                fileDescriptor: fileDescriptor,
                eventMask: [.write, .delete, .rename],
                queue: DispatchQueue.global(qos: .utility)
            )

            source?.setEventHandler { [weak self] in
                guard let self = self else { return }

                let data = self.source?.data ?? []

                if data.contains(.write) {
                    print("File modified")
                }
                if data.contains(.delete) {
                    print("File deleted")
                }
                if data.contains(.rename) {
                    print("File renamed")
                }
            }

            source?.setCancelHandler { [weak self] in
                guard let fd = self?.fileDescriptor else { return }
                close(fd)
            }

            source?.resume()
        }

        deinit {
            source?.cancel()
        }
    }

    // ✅ Process monitoring source
    func monitorChildProcess(pid: pid_t) {
        let source = DispatchSource.makeProcessSource(
            identifier: pid,
            eventMask: [.exit, .fork],
            queue: .global(qos: .background)
        )

        source.setEventHandler {
            let data = source.data

            if data.contains(.exit) {
                print("Process \(pid) exited")
            }
            if data.contains(.fork) {
                print("Process \(pid) forked")
            }

            source.cancel()
        }

        source.resume()
    }

    // ✅ Signal handling source
    func handleInterruptSignal() {
        // Блокируем сигнал для текущего потока
        signal(SIGINT, SIG_IGN)

        let source = DispatchSource.makeSignalSource(
            signal: SIGINT,
            queue: .global(qos: .userInitiated)
        )

        source.setEventHandler {
            print("Received SIGINT, performing cleanup...")
            self.performCleanup()
            exit(0)
        }

        source.resume()
    }

    // ✅ Custom data source (для inter-thread communication)
    func customDataSource() {
        let source = DispatchSource.makeUserDataAddSource(
            queue: .global(qos: .utility)
        )

        source.setEventHandler {
            let accumulated = source.data
            print("Received \(accumulated) events")
        }

        source.resume()

        // Триггерим события из других потоков
        for i in 1...10 {
            DispatchQueue.global().async {
                source.add(data: 1) // Thread-safe инкремент
            }
        }
    }

    // ✅ Memory pressure source (iOS)
    #if os(iOS)
    func monitorMemoryPressure() {
        let source = DispatchSource.makeMemoryPressureSource(
            eventMask: [.warning, .critical],
            queue: .global(qos: .utility)
        )

        source.setEventHandler {
            let data = source.data

            if data.contains(.warning) {
                print("Memory warning - clearing caches")
                self.clearCaches()
            }
            if data.contains(.critical) {
                print("Critical memory - aggressive cleanup")
                self.aggressiveCleanup()
            }
        }

        source.resume()
    }
    #endif

    // ❌ ОШИБКА: Забыть вызвать resume()
    func forgottenResume() {
        let timer = DispatchSource.makeTimerSource(queue: .main)
        timer.schedule(deadline: .now(), repeating: 1.0)
        timer.setEventHandler { print("Tick") }
        // BUG: timer.resume() не вызван - событий не будет!
    }
}
```

---

## DispatchBarrier - Read/Write Locks

```swift
// DispatchBarrier: Безопасная синхронизация для читателей-писателей
final class ThreadSafeDictionary<Key: Hashable, Value> {

    private var storage: [Key: Value] = [:]
    private let queue = DispatchQueue(
        label: "com.app.dictionary",
        attributes: .concurrent
    )

    // ✅ Множественные читатели (concurrent reads)
    func value(forKey key: Key) -> Value? {
        var result: Value?

        queue.sync {
            result = storage[key]
        }

        return result
    }

    // ✅ Эксклюзивный писатель (barrier write)
    func setValue(_ value: Value, forKey key: Key) {
        queue.async(flags: .barrier) {
            self.storage[key] = value
        }
    }

    // ✅ Barrier для атомарности множественных операций
    func removeAll() {
        queue.async(flags: .barrier) {
            self.storage.removeAll()
        }
    }

    // ✅ Синхронный barrier для немедленного результата
    func getAllKeys() -> [Key] {
        var keys: [Key] = []

        queue.sync(flags: .barrier) {
            keys = Array(storage.keys)
        }

        return keys
    }
}

// Диаграмма работы barrier:
/*
┌──────────────────────────────────────────────────────────────┐
│                   DISPATCH BARRIER FLOW                       │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  Time →                                                        │
│                                                                │
│  [Read 1] ─────┐                                              │
│  [Read 2] ─────┼─────> Concurrent reads OK                   │
│  [Read 3] ─────┘                                              │
│                                                                │
│             ╔═══════════════════════════╗                     │
│             ║ [WRITE - Barrier]         ║  ← Exclusive access│
│             ║ Waits for reads to finish ║                     │
│             ║ Blocks new reads          ║                     │
│             ╚═══════════════════════════╝                     │
│                                                                │
│                       [Read 4] ─────┐                         │
│                       [Read 5] ─────┼─> Concurrent again      │
│                       [Read 6] ─────┘                         │
│                                                                │
└──────────────────────────────────────────────────────────────┘
*/

// ✅ Расширенный пример: Thread-safe cache
final class ThreadSafeCache<Key: Hashable, Value> {
    private var storage: [Key: Value] = [:]
    private let queue = DispatchQueue(
        label: "com.app.cache",
        attributes: .concurrent,
        target: .global(qos: .userInitiated) // Target queue для QoS
    )

    subscript(key: Key) -> Value? {
        get {
            queue.sync { storage[key] }
        }
        set {
            queue.async(flags: .barrier) {
                self.storage[key] = newValue
            }
        }
    }

    func getOrCreate(
        key: Key,
        creator: () -> Value
    ) -> Value {
        // Оптимистичное чтение
        if let existing = queue.sync(execute: { storage[key] }) {
            return existing
        }

        // Эксклюзивная запись с повторной проверкой
        return queue.sync(flags: .barrier) {
            if let existing = storage[key] {
                return existing // Создан другим потоком
            }

            let newValue = creator()
            storage[key] = newValue
            return newValue
        }
    }

    func removeExpired(
        isExpired: (Key, Value) -> Bool
    ) {
        queue.async(flags: .barrier) {
            self.storage = self.storage.filter { key, value in
                !isExpired(key, value)
            }
        }
    }
}

// ❌ АНТИПАТТЕРН: Барьер на serial queue (бессмысленно)
final class WrongBarrierUsage {
    private let serialQueue = DispatchQueue(label: "com.app.serial")

    func unnecessaryBarrier() {
        // Барьер НЕ имеет эффекта на serial queue!
        serialQueue.async(flags: .barrier) {
            print("This is just a regular async on serial queue")
        }
    }
}

// ✅ ПРАВИЛЬНО: Барьер только на concurrent queue
final class CorrectBarrierUsage {
    private let concurrentQueue = DispatchQueue(
        label: "com.app.concurrent",
        attributes: .concurrent
    )

    func properBarrier() {
        concurrentQueue.async(flags: .barrier) {
            print("This actually blocks other operations")
        }
    }
}
```

---

## Dispatch Functions - Основные Функции

### dispatch_async vs dispatch_sync

```swift
final class AsyncSyncComparison {

    // ✅ async: Не блокирует вызывающий поток
    func asyncExample() {
        print("1. Before async")

        DispatchQueue.global().async {
            print("3. Inside async block")
            Thread.sleep(forTimeInterval: 1)
            print("4. Async work done")
        }

        print("2. After async (не ждет завершения)")
        // Вывод: 1 → 2 → 3 → 4
    }

    // ✅ sync: Блокирует до завершения
    func syncExample() {
        print("1. Before sync")

        DispatchQueue.global().sync {
            print("2. Inside sync block")
            Thread.sleep(forTimeInterval: 1)
            print("3. Sync work done")
        }

        print("4. After sync (ждет завершения)")
        // Вывод: 1 → 2 → 3 → 4 (в строгом порядке)
    }

    // ❌ DEADLOCK: sync на своей же serial queue
    func deadlockPattern() {
        let queue = DispatchQueue(label: "com.app.queue")

        queue.async {
            // Выполняется на queue

            queue.sync {
                // DEADLOCK: ждет сам себя!
                print("Never executes")
            }
        }
    }

    // ✅ ПРАВИЛЬНО: sync на другую queue
    func correctSyncPattern() {
        let queueA = DispatchQueue(label: "com.app.queueA")
        let queueB = DispatchQueue(label: "com.app.queueB")

        queueA.async {
            let result = queueB.sync {
                return self.calculateValue()
            }
            print("Got result: \(result)")
        }
    }

    // ✅ Когда использовать sync
    func whenToUseSync() {
        let queue = DispatchQueue(label: "com.app.data", attributes: .concurrent)
        var data: [Int] = []

        // Thread-safe чтение через sync
        func getData() -> [Int] {
            queue.sync { data }
        }

        // Запись через async barrier
        func addData(_ value: Int) {
            queue.async(flags: .barrier) {
                data.append(value)
            }
        }
    }
}
```

### dispatch_after - Отложенное Выполнение

```swift
final class DispatchAfterExample {

    // ✅ Базовое использование
    func delayedExecution() {
        print("Starting...")

        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) {
            print("Executed after 2 seconds")
        }
    }

    // ✅ Отмена через DispatchWorkItem
    private var delayedWorkItem: DispatchWorkItem?

    func cancelableDelay() {
        delayedWorkItem?.cancel()

        let workItem = DispatchWorkItem {
            print("This can be cancelled")
        }

        delayedWorkItem = workItem
        DispatchQueue.main.asyncAfter(deadline: .now() + 5.0, execute: workItem)
    }

    func cancelDelay() {
        delayedWorkItem?.cancel()
    }

    // ✅ Debounce паттерн для search
    private var searchWorkItem: DispatchWorkItem?

    func onSearchTextChanged(_ text: String) {
        searchWorkItem?.cancel()

        let workItem = DispatchWorkItem { [weak self] in
            self?.performSearch(text)
        }

        searchWorkItem = workItem
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3, execute: workItem)
    }

    // ✅ Throttle паттерн для scroll
    private var isThrottled = false

    func onScrollEvent() {
        guard !isThrottled else { return }

        isThrottled = true
        updateScrollPosition()

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) { [weak self] in
            self?.isThrottled = false
        }
    }

    // ✅ Retry механизм с экспоненциальной задержкой
    func retryWithBackoff(
        attempt: Int = 0,
        maxAttempts: Int = 5
    ) {
        guard attempt < maxAttempts else {
            print("Max retries exceeded")
            return
        }

        performNetworkRequest { [weak self] success in
            guard !success else { return }

            let delay = pow(2.0, Double(attempt)) // 1, 2, 4, 8, 16 секунд

            DispatchQueue.global().asyncAfter(deadline: .now() + delay) {
                self?.retryWithBackoff(attempt: attempt + 1, maxAttempts: maxAttempts)
            }
        }
    }

    // ❌ ОШИБКА: asyncAfter не гарантирует точность
    func impreciseTimer() {
        // НЕ ИСПОЛЬЗУЙТЕ для точных интервалов!
        DispatchQueue.main.asyncAfter(deadline: .now() + 1.0) {
            self.impreciseTimer() // Drift накапливается
        }
    }

    // ✅ ПРАВИЛЬНО: DispatchSourceTimer для точности
    func preciseTimer() {
        let timer = DispatchSource.makeTimerSource(queue: .main)
        timer.schedule(deadline: .now(), repeating: 1.0, leeway: .milliseconds(10))
        timer.setEventHandler { [weak self] in
            self?.updateTimer()
        }
        timer.resume()
    }
}
```

---

## Target Queues - Иерархия Очередей

```swift
// Target Queues: Наследование QoS и сериализация
final class TargetQueueExample {

    // ✅ QoS наследование от target queue
    func qosInheritance() {
        let targetQueue = DispatchQueue.global(qos: .userInitiated)

        // Очередь без QoS наследует от target
        let queue = DispatchQueue(
            label: "com.app.child",
            target: targetQueue
        )

        queue.async {
            // Выполняется с .userInitiated QoS
            print("Inherited QoS from target")
        }
    }

    // ✅ Сериализация concurrent queues через общий target
    func serializeWithTarget() {
        let serialTarget = DispatchQueue(label: "com.app.serial")

        let queue1 = DispatchQueue(
            label: "com.app.queue1",
            attributes: .concurrent,
            target: serialTarget
        )

        let queue2 = DispatchQueue(
            label: "com.app.queue2",
            attributes: .concurrent,
            target: serialTarget
        )

        // queue1 и queue2 выполняются через один serial target
        // Все задачи сериализованы!
        queue1.async { print("Task 1") }
        queue2.async { print("Task 2") }
        queue1.async { print("Task 3") }
        // Вывод: Task 1 → Task 2 → Task 3 (последовательно)
    }

    // ✅ Иерархия для модульной архитектуры
    final class NetworkModule {
        private let targetQueue = DispatchQueue(
            label: "com.app.network",
            qos: .utility
        )

        let requestQueue = DispatchQueue(
            label: "com.app.network.requests",
            attributes: .concurrent,
            target: nil // Установим позже
        )

        let responseQueue = DispatchQueue(
            label: "com.app.network.responses",
            target: nil
        )

        init() {
            // Переназначаем target для обеих очередей
            requestQueue.setTarget(queue: targetQueue)
            responseQueue.setTarget(queue: targetQueue)
        }
    }

    // ✅ Динамическое изменение приоритета
    final class PriorityManager {
        private let lowPriorityTarget = DispatchQueue.global(qos: .background)
        private let highPriorityTarget = DispatchQueue.global(qos: .userInitiated)

        private let workQueue = DispatchQueue(label: "com.app.work")

        func setLowPriority() {
            workQueue.setTarget(queue: lowPriorityTarget)
        }

        func setHighPriority() {
            workQueue.setTarget(queue: highPriorityTarget)
        }
    }

    // ⚠️ Target queue ограничения
    func targetLimitations() {
        // НЕЛЬЗЯ изменить target для:
        // - Main queue
        // - Global queues
        // - Active queues (с выполняющимися задачами)

        // DispatchQueue.main.setTarget(queue: someQueue) // Ошибка компиляции
    }
}
```

---

## Thread Explosion и Thread Pool

```swift
// Thread Explosion: проблема и решения
final class ThreadManagementExample {

    // ❌ ПРОБЛЕМА: Thread Explosion
    func threadExplosion() {
        for i in 1...1000 {
            Thread.detachNewThread {
                // Создаем 1000 потоков!
                // Context switching overhead огромен
                self.processItem(i)
            }
        }

        // Результат:
        // - Сотни потоков в памяти (каждый ~512KB stack)
        // - Excessive context switching
        // - CPU время тратится на управление потоками
        // - Возможный kernel panic при исчерпании ресурсов
    }

    // ✅ РЕШЕНИЕ: GCD управляет пулом потоков
    func cooperativeThreading() {
        let queue = DispatchQueue(
            label: "com.app.processing",
            attributes: .concurrent
        )

        for i in 1...1000 {
            queue.async {
                // GCD использует пул из ~64 потоков
                // Задачи ставятся в очередь и выполняются по мере доступности
                self.processItem(i)
            }
        }

        // Результат:
        // - Фиксированное количество потоков
        // - Минимальный context switching
        // - Оптимальная утилизация CPU
    }

    // ⚠️ Блокирующие операции истощают пул
    func blockingOperationsProblem() {
        let queue = DispatchQueue.global(qos: .utility)

        for _ in 1...100 {
            queue.async {
                // ПРОБЛЕМА: semaphore wait блокирует поток!
                let semaphore = DispatchSemaphore(value: 0)

                someAsyncOperation {
                    semaphore.signal()
                }

                semaphore.wait() // Поток заблокирован
                // Если все потоки заблокированы → thread pool starvation
            }
        }
    }

    // ✅ РЕШЕНИЕ: Избегайте блокирующих операций
    func nonBlockingSolution() {
        let queue = DispatchQueue.global(qos: .utility)

        for _ in 1...100 {
            queue.async {
                someAsyncOperation { result in
                    // Callback на новую задачу вместо блокировки
                    queue.async {
                        self.processResult(result)
                    }
                }
            }
        }
    }

    // ✅ Мониторинг состояния пула потоков
    func monitorThreadPool() {
        let queue = DispatchQueue(label: "com.app.monitor")

        queue.async {
            // Информация о потоке
            let thread = Thread.current
            print("Thread: \(thread.name ?? "unnamed")")
            print("Priority: \(thread.threadPriority)")
            print("Stack size: \(thread.stackSize)")

            // Dispatch queue label
            let label = String(cString: __dispatch_queue_get_label(nil), encoding: .utf8)
            print("Queue label: \(label ?? "unknown")")
        }
    }

    // ✅ Оптимальное использование потоков
    func optimalThreadUsage() {
        let processorCount = ProcessInfo.processInfo.activeProcessorCount

        // CPU-bound задачи: не больше количества ядер
        let cpuQueue = DispatchQueue(
            label: "com.app.cpu",
            attributes: .concurrent
        )

        // I/O-bound задачи: можно больше (потоки часто ждут)
        let ioQueue = DispatchQueue(
            label: "com.app.io",
            attributes: .concurrent
        )

        // Ограничение для I/O через semaphore
        let ioSemaphore = DispatchSemaphore(value: processorCount * 2)

        for task in cpuBoundTasks {
            cpuQueue.async {
                self.performCPUWork(task)
            }
        }

        for task in ioBoundTasks {
            ioQueue.async {
                ioSemaphore.wait()
                defer { ioSemaphore.signal() }

                self.performIOWork(task)
            }
        }
    }
}
```

---

## GCD vs async/await - Сравнение

```swift
// Сравнение GCD и современного async/await (Swift 5.5+)
final class GCDvsAsyncAwait {

    // ═══════════════════════════════════════════════════════════
    // ПРИМЕР 1: Простая асинхронная операция
    // ═══════════════════════════════════════════════════════════

    // GCD версия
    func fetchUserGCD(id: Int, completion: @escaping (User?, Error?) -> Void) {
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                let user = try self.loadUser(id)
                DispatchQueue.main.async {
                    completion(user, nil)
                }
            } catch {
                DispatchQueue.main.async {
                    completion(nil, error)
                }
            }
        }
    }

    // async/await версия
    func fetchUserAsync(id: Int) async throws -> User {
        // Компилятор автоматически управляет потоками
        return try await loadUserAsync(id)
    }

    // ═══════════════════════════════════════════════════════════
    // ПРИМЕР 2: Последовательные зависимые операции
    // ═══════════════════════════════════════════════════════════

    // ❌ GCD: Callback hell
    func processOrderGCD(completion: @escaping (Result<Order, Error>) -> Void) {
        fetchUserGCD(id: 1) { user, error in
            guard let user = user else {
                completion(.failure(error!))
                return
            }

            self.fetchCartGCD(userId: user.id) { cart, error in
                guard let cart = cart else {
                    completion(.failure(error!))
                    return
                }

                self.calculateTotalGCD(cart: cart) { total, error in
                    guard let total = total else {
                        completion(.failure(error!))
                        return
                    }

                    self.createOrderGCD(total: total) { order, error in
                        if let order = order {
                            completion(.success(order))
                        } else {
                            completion(.failure(error!))
                        }
                    }
                }
            }
        }
    }

    // ✅ async/await: Линейный код
    func processOrderAsync() async throws -> Order {
        let user = try await fetchUserAsync(id: 1)
        let cart = try await fetchCartAsync(userId: user.id)
        let total = try await calculateTotalAsync(cart: cart)
        let order = try await createOrderAsync(total: total)
        return order
    }

    // ═══════════════════════════════════════════════════════════
    // ПРИМЕР 3: Параллельные независимые операции
    // ═══════════════════════════════════════════════════════════

    // GCD: DispatchGroup
    func loadDashboardGCD(completion: @escaping (Dashboard?, Error?) -> Void) {
        let group = DispatchGroup()
        var user: User?
        var posts: [Post]?
        var notifications: [Notification]?
        var errors: [Error] = []

        group.enter()
        fetchUserGCD(id: 1) { result, error in
            user = result
            if let error = error { errors.append(error) }
            group.leave()
        }

        group.enter()
        fetchPostsGCD { result, error in
            posts = result
            if let error = error { errors.append(error) }
            group.leave()
        }

        group.enter()
        fetchNotificationsGCD { result, error in
            notifications = result
            if let error = error { errors.append(error) }
            group.leave()
        }

        group.notify(queue: .main) {
            if let firstError = errors.first {
                completion(nil, firstError)
            } else if let user = user, let posts = posts, let notifications = notifications {
                let dashboard = Dashboard(user: user, posts: posts, notifications: notifications)
                completion(dashboard, nil)
            }
        }
    }

    // async/await: Task group (Swift 5.5+)
    func loadDashboardAsync() async throws -> Dashboard {
        try await withThrowingTaskGroup(of: Void.self) { group in
            var user: User?
            var posts: [Post]?
            var notifications: [Notification]?

            group.addTask {
                user = try await self.fetchUserAsync(id: 1)
            }

            group.addTask {
                posts = try await self.fetchPostsAsync()
            }

            group.addTask {
                notifications = try await self.fetchNotificationsAsync()
            }

            try await group.waitForAll()

            return Dashboard(
                user: user!,
                posts: posts!,
                notifications: notifications!
            )
        }
    }

    // ═══════════════════════════════════════════════════════════
    // ПРИМЕР 4: Отмена операций
    // ═══════════════════════════════════════════════════════════

    // GCD: DispatchWorkItem
    var searchWorkItem: DispatchWorkItem?

    func searchGCD(query: String) {
        searchWorkItem?.cancel()

        let workItem = DispatchWorkItem {
            let results = self.performSearch(query)
            DispatchQueue.main.async {
                self.displayResults(results)
            }
        }

        searchWorkItem = workItem
        DispatchQueue.global().async(execute: workItem)
    }

    // async/await: Task cancellation
    var searchTask: Task<Void, Never>?

    func searchAsync(query: String) {
        searchTask?.cancel()

        searchTask = Task {
            do {
                let results = try await performSearchAsync(query)

                guard !Task.isCancelled else { return }

                await MainActor.run {
                    displayResults(results)
                }
            } catch {
                print("Search failed: \(error)")
            }
        }
    }

    // ═══════════════════════════════════════════════════════════
    // КОГДА ИСПОЛЬЗОВАТЬ GCD vs async/await
    // ═══════════════════════════════════════════════════════════

    func comparisonTable() {
        /*
        ┌──────────────────────────────────────────────────────────────┐
        │                  GCD vs async/await                           │
        ├──────────────────┬─────────────────────┬─────────────────────┤
        │ Критерий         │ GCD                 │ async/await         │
        ├──────────────────┼─────────────────────┼─────────────────────┤
        │ iOS Version      │ iOS 4+              │ iOS 13+ (Swift 5.5) │
        │ Синтаксис        │ Closures, callbacks │ Linear, sync-like   │
        │ Отмена           │ DispatchWorkItem    │ Task.cancel()       │
        │ Приоритеты       │ QoS explicit        │ Inherited           │
        │ Event-driven     │ DispatchSource ✅   │ AsyncStream         │
        │ Низкий уровень   │ Полный контроль ✅  │ Абстрагировано      │
        │ Синхронизация    │ Semaphore, Barrier  │ Actor, Mutex        │
        │ Читаемость      │ Callback hell ❌    │ Linear flow ✅      │
        │ Thread safety    │ Ручная ⚠️          │ Actor модель ✅     │
        │ Structured conc. │ Нет ❌             │ Есть ✅            │
        └──────────────────┴─────────────────────┴─────────────────────┘

        Используйте GCD когда:
        - iOS < 13 поддержка
        - Event-driven программирование (DispatchSource)
        - Низкоуровневая оптимизация
        - Барьеры для read/write locks
        - Работа с legacy кодом

        Используйте async/await когда:
        - iOS 13+ минимум
        - Новый код
        - Нужна структурированная конкурентность
        - Actor изоляция для thread safety
        - Последовательные async операции
        */
    }
}
```

---

## 6 Частых Ошибок с GCD

### Ошибка 1: Deadlock при sync на своей очереди

```swift
// ❌ НЕПРАВИЛЬНО: sync deadlock
func deadlockExample() {
    let queue = DispatchQueue(label: "com.app.queue")

    queue.async {
        // Выполняется на queue

        queue.sync {
            // DEADLOCK: queue ждет сам себя!
            print("Never executes")
        }
    }
}

// ✅ ПРАВИЛЬНО: sync на другую очередь
func correctSyncExample() {
    let queueA = DispatchQueue(label: "com.app.queueA")
    let queueB = DispatchQueue(label: "com.app.queueB")

    queueA.async {
        let result = queueB.sync {
            return self.calculateValue()
        }
        print("Result: \(result)")
    }
}
```

### Ошибка 2: Обновление UI на background потоке

```swift
// ❌ НЕПРАВИЛЬНО: UI на background
func updateUIWrong() {
    DispatchQueue.global().async {
        // ОПАСНО: UI операции вне main thread!
        self.label.text = "Updated"
        self.view.backgroundColor = .red
        // Runtime warning или crash
    }
}

// ✅ ПРАВИЛЬНО: Всегда на main queue
func updateUICorrect() {
    DispatchQueue.global().async {
        let data = self.fetchData()

        DispatchQueue.main.async {
            self.label.text = data
            self.view.backgroundColor = .green
        }
    }
}
```

### Ошибка 3: Несбалансированные enter/leave в DispatchGroup

```swift
// ❌ НЕПРАВИЛЬНО: Пропущен leave
func unbalancedGroup() {
    let group = DispatchGroup()

    group.enter()
    fetchData { result in
        if result.isSuccess {
            self.processData(result)
            group.leave()
        }
        // BUG: leave не вызван при ошибке!
    }

    group.notify(queue: .main) {
        // Никогда не выполнится при ошибке
        print("Done")
    }
}

// ✅ ПРАВИЛЬНО: defer гарантирует leave
func balancedGroup() {
    let group = DispatchGroup()

    group.enter()
    fetchData { result in
        defer { group.leave() }

        guard result.isSuccess else { return }
        self.processData(result)
    }

    group.notify(queue: .main) {
        print("Always executes")
    }
}
```

### Ошибка 4: Race condition в concurrent queue

```swift
// ❌ НЕПРАВИЛЬНО: Race condition
class UnsafeCounter {
    private var value: Int = 0
    private let queue = DispatchQueue(label: "com.app.counter", attributes: .concurrent)

    func increment() {
        queue.async {
            // RACE CONDITION: несколько потоков пишут одновременно!
            self.value += 1
        }
    }
}

// ✅ ПРАВИЛЬНО: Barrier для эксклюзивной записи
class SafeCounter {
    private var value: Int = 0
    private let queue = DispatchQueue(label: "com.app.counter", attributes: .concurrent)

    func increment() {
        queue.async(flags: .barrier) {
            // Эксклюзивный доступ
            self.value += 1
        }
    }

    func getValue() -> Int {
        queue.sync { value }
    }
}
```

### Ошибка 5: Retain cycle в async closures

```swift
// ❌ НЕПРАВИЛЬНО: Strong reference cycle
class LeakyViewController: UIViewController {
    private var data: [String] = []

    func loadData() {
        DispatchQueue.global().async {
            // MEMORY LEAK: self захвачен сильной ссылкой!
            let result = self.fetchFromNetwork()
            self.data = result
        }
    }
}

// ✅ ПРАВИЛЬНО: Weak self
class SafeViewController: UIViewController {
    private var data: [String] = []

    func loadData() {
        DispatchQueue.global().async { [weak self] in
            guard let self = self else { return }

            let result = self.fetchFromNetwork()
            self.data = result
        }
    }
}
```

### Ошибка 6: Забыть resume() для DispatchSource

```swift
// ❌ НЕПРАВИЛЬНО: Не вызван resume
func brokenTimer() {
    let timer = DispatchSource.makeTimerSource(queue: .main)
    timer.schedule(deadline: .now(), repeating: 1.0)

    timer.setEventHandler {
        print("Tick")
    }

    // BUG: timer.resume() не вызван!
    // События не будут генерироваться
}

// ✅ ПРАВИЛЬНО: Всегда вызывайте resume
func workingTimer() {
    let timer = DispatchSource.makeTimerSource(queue: .main)
    timer.schedule(deadline: .now(), repeating: 1.0)

    timer.setEventHandler {
        print("Tick")
    }

    timer.resume() // ✅ Обязательно!
}
```

---

## Production-Ready Паттерны

### Thread-Safe Singleton

```swift
final class NetworkManager {
    static let shared = NetworkManager() // Thread-safe в Swift

    private let requestQueue = DispatchQueue(
        label: "com.app.network.requests",
        qos: .utility,
        attributes: .concurrent
    )

    private let responseQueue = DispatchQueue(
        label: "com.app.network.responses",
        qos: .userInitiated
    )

    private init() {} // Приватный инициализатор

    func request(
        _ url: URL,
        completion: @escaping (Result<Data, Error>) -> Void
    ) {
        requestQueue.async {
            // Network call
            let result = self.performRequest(url)

            self.responseQueue.async {
                completion(result)
            }
        }
    }
}
```

### Async Operation Queue

```swift
// Продвинутая синхронизация для сложных workflow
final class AsyncOperationQueue {
    private let queue: OperationQueue
    private let completionQueue: DispatchQueue

    init(
        maxConcurrentOperations: Int = 4,
        qos: QualityOfService = .utility
    ) {
        queue = OperationQueue()
        queue.maxConcurrentOperationCount = maxConcurrentOperations
        queue.qualityOfService = qos

        completionQueue = DispatchQueue(
            label: "com.app.operations.completion",
            qos: DispatchQoS(qosClass: qos.qosClass, relativePriority: 0)
        )
    }

    func addOperation(
        _ block: @escaping (@escaping () -> Void) -> Void
    ) {
        let operation = BlockOperation()

        let group = DispatchGroup()
        group.enter()

        operation.addExecutionBlock {
            block {
                group.leave()
            }
        }

        queue.addOperation(operation)

        group.notify(queue: completionQueue) {
            print("Operation completed")
        }
    }
}
```

### Debouncer и Throttler

```swift
// Универсальный debouncer
final class Debouncer {
    private let delay: TimeInterval
    private let queue: DispatchQueue
    private var workItem: DispatchWorkItem?

    init(delay: TimeInterval, queue: DispatchQueue = .main) {
        self.delay = delay
        self.queue = queue
    }

    func debounce(action: @escaping () -> Void) {
        workItem?.cancel()

        let item = DispatchWorkItem(block: action)
        workItem = item

        queue.asyncAfter(deadline: .now() + delay, execute: item)
    }
}

// Универсальный throttler
final class Throttler {
    private let interval: TimeInterval
    private let queue: DispatchQueue
    private var lastFireTime: DispatchTime = .now()
    private var workItem: DispatchWorkItem?

    init(interval: TimeInterval, queue: DispatchQueue = .main) {
        self.interval = interval
        self.queue = queue
    }

    func throttle(action: @escaping () -> Void) {
        let now = DispatchTime.now()
        let deadline = lastFireTime + interval

        if now >= deadline {
            lastFireTime = now
            queue.async(execute: action)
        } else {
            workItem?.cancel()

            let item = DispatchWorkItem { [weak self] in
                self?.lastFireTime = .now()
                action()
            }

            workItem = item
            queue.asyncAfter(deadline: deadline, execute: item)
        }
    }
}
```

---

## Связь с другими темами

**[[ios-async-await]]** — async/await (Swift 5.5+) является современной заменой GCD для большинства задач асинхронного программирования. GCD предоставляет низкоуровневый контроль над очередями и потоками, тогда как async/await абстрагирует управление потоками и предоставляет structured concurrency. Понимание GCD необходимо для работы с legacy-кодом, event-driven программированием (DispatchSource) и низкоуровневой оптимизацией. Рекомендуется изучить GCD перед async/await для глубокого понимания того, что происходит "под капотом".

**[[ios-threading-fundamentals]]** — GCD построен поверх примитивов потоков операционной системы и является абстракцией, скрывающей сложность ручного управления потоками. Понимание основ threading (что такое поток, main thread, context switching) критично перед погружением в GCD, поскольку позволяет осознанно выбирать между serial и concurrent очередями, понимать причины deadlock-ов и thread explosion. Эта тема является обязательным prerequisite.

**[[os-scheduling]]** — QoS-система GCD напрямую связана с планировщиком ядра XNU: приоритеты очередей (.userInteractive, .background и т.д.) транслируются в приоритеты потоков на уровне ядра. Изучение планирования процессов объясняет, почему priority inversion является проблемой и как система автоматически повышает приоритеты для предотвращения голодания. Рекомендуется для глубокого понимания производительности многопоточных приложений.

---

## Источники и дальнейшее чтение

### Книги
- Eidhof C. et al. (2019). *Advanced Swift.* — содержит детальный разбор concurrency-примитивов Swift, работы с замыканиями в контексте GCD и управления памятью в асинхронном коде; необходима для продвинутого понимания темы.
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — фундаментальное объяснение модели потоков iOS, Grand Central Dispatch и перехода к structured concurrency; отличная отправная точка.
- Apple (2023). *The Swift Programming Language.* — раздел Concurrency описывает взаимодействие async/await с GCD и объясняет, когда использовать каждый подход.

### Документация и ресурсы
- [Concurrency Programming Guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ConcurrencyProgrammingGuide/)
- [Dispatch Framework Reference](https://developer.apple.com/documentation/dispatch)
- [Quality of Service Classes](https://developer.apple.com/documentation/dispatch/dispatchqos)
- [libdispatch на GitHub](https://github.com/apple/swift-corelibs-libdispatch)

### WWDC Sessions
- WWDC 2017: Modernizing GCD Usage
- WWDC 2021: Swift concurrency: Behind the scenes
- WWDC 2016: Concurrent Programming With GCD in Swift 3