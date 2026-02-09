---
title: "Основы многопоточности в iOS"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/threading
  - type/deep-dive
  - level/intermediate
related:
  - "[[concurrency-parallelism]]"
  - "[[android-threading]]"
  - "[[swift-concurrency]]"
  - "[[ios-gcd-deep-dive]]"
---

# Основы многопоточности в iOS

## TL;DR

iOS использует **Grand Central Dispatch (GCD)** для управления потоками через очереди (queues). Главный поток (Main Thread) — единственное место для UI-операций. GCD автоматически управляет пулом потоков, распределяя задачи по очередям с разными приоритетами (QoS). Синхронная диспетчеризация блокирует текущий поток, асинхронная — нет. Последовательные очереди (serial) выполняют задачи по порядку, параллельные (concurrent) — одновременно. Избыток потоков (thread explosion) приводит к деградации производительности.

---

## Аналогия: Ресторанная кухня

Представьте многопоточность как работу ресторана:

```
┌─────────────────────────────────────────────────────────┐
│  Main Thread = Официант (единственный с доступом к залу)│
│  ┌──────────┐                                            │
│  │ Клиенты  │ ← Только официант может обслуживать        │
│  │   (UI)   │                                            │
│  └──────────┘                                            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  Background Threads = Повара на кухне                    │
│  ┌──────┐  ┌──────┐  ┌──────┐                           │
│  │Повар1│  │Повар2│  │Повар3│                           │
│  └──────┘  └──────┘  └──────┘                           │
│     ↓         ↓         ↓                                │
│  Готовят блюда параллельно                              │
│  (Network, Data Processing, File I/O)                   │
└─────────────────────────────────────────────────────────┘

Serial Queue = Один повар готовит блюда по порядку
Concurrent Queue = Несколько поваров готовят одновременно
```

**Правило**: Повара не могут выходить в зал (фоновые потоки не трогают UI), официант не должен стоять на кухне и готовить (Main Thread не блокируется тяжелыми задачами).

---

## Главный поток (Main Thread / UI Thread)

### Почему Main Thread особенный?

В iOS **все UI-операции** должны происходить на главном потоке. Это обусловлено архитектурой UIKit и AppKit, где компоненты UI не являются потокобезопасными.

```
┌─────────────────────────────────────────────────┐
│           Application Launch                     │
│                   ↓                              │
│            Main Run Loop                         │
│                   ↓                              │
│  ┌───────────────────────────────────────┐      │
│  │  Event Queue (Touch, Gestures, etc)   │      │
│  └───────────────────────────────────────┘      │
│                   ↓                              │
│         Process Events on Main Thread            │
│                   ↓                              │
│    Update UI → Layout → Render → Display        │
│         (60/120 fps = 16.67/8.33 ms)            │
└─────────────────────────────────────────────────┘
```

**Main Run Loop** работает на частоте дисплея. Если блокировать главный поток > 16.67ms (60Hz), UI "заикается" (jank).

```swift
// ❌ ПЛОХО: Блокировка Main Thread
class ProductViewController: UIViewController {
    func loadProducts() {
        // ПОЧЕМУ: Выполняется на главном потоке
        let products = fetchProductsFromAPI() // 2-3 секунды!
        tableView.reloadData() // UI замораживается
    }
}

// ✅ ХОРОШО: Фоновая загрузка
class ProductViewController: UIViewController {
    func loadProducts() {
        // ПОЧЕМУ: Переносим тяжелую работу на фон
        DispatchQueue.global(qos: .userInitiated).async {
            let products = self.fetchProductsFromAPI()

            // ПОЧЕМУ: UI обновляем только на Main Thread
            DispatchQueue.main.async {
                self.products = products
                self.tableView.reloadData()
            }
        }
    }
}
```

---

## Потокобезопасность (Thread Safety)

### Проблема: Race Conditions

Когда несколько потоков одновременно изменяют одни данные:

```
Thread 1: balance = 100
Thread 2: balance = 100
Thread 1: balance += 50  → balance = 150
Thread 2: balance += 30  → balance = 130 (перезаписал!)
Итог: balance = 130 (должно быть 180)
```

### Решения в iOS

```
┌──────────────────────────────────────────────────┐
│  Thread Safety Mechanisms                        │
├──────────────────────────────────────────────────┤
│  1. Serial Queue (порядок гарантирован)          │
│  2. Sync/Async barriers (для concurrent queues)  │
│  3. NSLock / os_unfair_lock (примитивы блокировки)│
│  4. Atomic properties (@atomic в Obj-C)          │
│  5. Actor (Swift 6) - современный подход          │
└──────────────────────────────────────────────────┘
```

```swift
// ❌ ПЛОХО: Race condition
class BankAccount {
    var balance: Double = 0

    func deposit(_ amount: Double) {
        // ПОЧЕМУ: Несколько потоков могут читать/писать одновременно
        balance += amount
    }
}

// ✅ ХОРОШО: Serial Queue для синхронизации
class BankAccount {
    private var balance: Double = 0
    private let queue = DispatchQueue(label: "com.bank.account")

    func deposit(_ amount: Double) {
        queue.sync {
            // ПОЧЕМУ: Очередь гарантирует, что только один поток
            // выполняет код в данный момент
            balance += amount
        }
    }

    func getBalance() -> Double {
        return queue.sync { balance }
    }
}
```

---

## DispatchQueue: Основы

GCD работает с очередями задач вместо прямого управления потоками.

```
┌─────────────────────────────────────────────────────┐
│              DispatchQueue Architecture              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Your Code → Dispatch Queue → Thread Pool           │
│                                                      │
│  ┌──────────────┐                                   │
│  │DispatchQueue │                                   │
│  │  (Очередь)   │                                   │
│  └──────┬───────┘                                   │
│         │                                            │
│         ├→ Block 1 ──┐                              │
│         ├→ Block 2 ──┼→ GCD распределяет по потокам │
│         └→ Block 3 ──┘   (вы НЕ управляете потоками)│
│                                                      │
└─────────────────────────────────────────────────────┘
```

### Основные типы очередей

```swift
// 1. Main Queue (главная очередь - serial)
DispatchQueue.main.async {
    // ПОЧЕМУ: Всегда выполняется на главном потоке
    self.label.text = "Updated!"
}

// 2. Global Queue (системная concurrent очередь)
DispatchQueue.global(qos: .userInitiated).async {
    // ПОЧЕМУ: GCD выбирает подходящий поток из пула
    let data = self.processHeavyComputation()
}

// 3. Custom Serial Queue (ваша последовательная очередь)
let serialQueue = DispatchQueue(label: "com.app.serial")
serialQueue.async {
    // ПОЧЕМУ: Задачи выполняются строго по порядку
}

// 4. Custom Concurrent Queue (ваша параллельная очередь)
let concurrentQueue = DispatchQueue(
    label: "com.app.concurrent",
    attributes: .concurrent
)
concurrentQueue.async {
    // ПОЧЕМУ: Задачи могут выполняться параллельно
}
```

---

## Quality of Service (QoS)

QCD использует приоритеты для оптимизации энергопотребления и производительности:

```
┌────────────────────────────────────────────────────────┐
│  QoS Levels (от высокого к низкому приоритету)         │
├────────────────────────────────────────────────────────┤
│                                                         │
│  .userInteractive  ───┐                                │
│  (UI updates)         │ High Priority                  │
│  Latency: ~ms         │ More CPU/Energy                │
│                       │                                │
│  .userInitiated   ────┤                                │
│  (User-triggered)     │                                │
│  Latency: seconds     │                                │
│                       │                                │
│  .default         ────┤                                │
│  (General tasks)      │                                │
│                       │                                │
│  .utility         ────┤                                │
│  (Long-running)       │                                │
│  Latency: minutes     │                                │
│                       │                                │
│  .background      ────┘                                │
│  (User-invisible)     Low Priority                     │
│  Latency: hours       Less CPU/Energy                  │
│                                                         │
└────────────────────────────────────────────────────────┘
```

### Практические примеры

```swift
class ImageGalleryViewController: UIViewController {

    // ❌ ПЛОХО: Неправильный QoS
    func loadThumbnails() {
        DispatchQueue.global(qos: .background).async {
            // ПОЧЕМУ: Пользователь ждет, но приоритет минимальный
            let thumbnails = self.generateThumbnails()
            DispatchQueue.main.async {
                self.collectionView.reloadData()
            }
        }
    }

    // ✅ ХОРОШО: Соответствие QoS и задачи
    func loadThumbnailsCorrectly() {
        // ПОЧЕМУ: Пользователь инициировал загрузку - используем userInitiated
        DispatchQueue.global(qos: .userInitiated).async {
            let thumbnails = self.generateThumbnails()

            // ПОЧЕМУ: UI обновление требует userInteractive (main всегда такой)
            DispatchQueue.main.async {
                self.collectionView.reloadData()
            }
        }
    }

    // Фоновая синхронизация
    func syncCacheInBackground() {
        // ПОЧЕМУ: Пользователь не ждет, экономим батарею
        DispatchQueue.global(qos: .background).async {
            self.cleanupExpiredCache()
        }
    }

    // Длительная загрузка с прогрессом
    func downloadLargeFile() {
        // ПОЧЕМУ: Видимый прогресс, но не критично для UI
        DispatchQueue.global(qos: .utility).async {
            self.downloadWithProgress { progress in
                DispatchQueue.main.async {
                    self.progressView.progress = progress
                }
            }
        }
    }
}
```

### Таблица выбора QoS

| Задача | QoS | Почему |
|--------|-----|--------|
| Анимация UI | `.userInteractive` | Должна быть мгновенной |
| Загрузка по нажатию кнопки | `.userInitiated` | Пользователь ждет результат |
| Парсинг JSON | `.default` | Общая работа |
| Скачивание большого файла | `.utility` | Длительная, с прогрессом |
| Аналитика, логи | `.background` | Невидимо для пользователя |

---

## Синхронная vs Асинхронная диспетчеризация

```
Синхронная (sync)                Асинхронная (async)
──────────────────               ─────────────────────

Thread A:                        Thread A:
  │                                │
  ├─ queue.sync { }                ├─ queue.async { }
  │      │                         │      │
  │   Блокируется                  │   Продолжает
  │   и ждет                       │   сразу
  │      │                         ↓
  │      ↓                         (другая работа)
  │   Задача
  │   выполняется                  Thread B:
  │      │                            ↓
  │   Возврат                      Задача
  ↓                                выполняется
(продолжение)                         ↓
                                   (завершение)
```

```swift
// ❌ ПЛОХО: Deadlock на Main Thread
DispatchQueue.main.async {
    // Мы УЖЕ на main queue
    DispatchQueue.main.sync {
        // ПОЧЕМУ: main ждет сам себя → зависание!
        print("Никогда не выполнится")
    }
}

// ✅ ХОРОШО: Правильное использование sync
class DatabaseManager {
    private let queue = DispatchQueue(label: "com.db.queue")
    private var cache: [String: Data] = [:]

    func getData(key: String) -> Data? {
        // ПОЧЕМУ: sync возвращает результат синхронно
        return queue.sync {
            return cache[key]
        }
    }

    func setData(_ data: Data, key: String) {
        // ПОЧЕМУ: async не блокирует вызывающий код
        queue.async {
            self.cache[key] = data
        }
    }
}

// ❌ ПЛОХО: Бесполезный sync на фоновой очереди
func processData() {
    DispatchQueue.global().sync {
        // ПОЧЕМУ: Блокируем текущий поток, но не используем результат
        heavyComputation()
    }
    // Зачем блокироваться? Используйте async!
}

// ✅ ХОРОШО: async для фоновой работы
func processDataCorrectly() {
    DispatchQueue.global(qos: .userInitiated).async {
        let result = self.heavyComputation()
        DispatchQueue.main.async {
            self.updateUI(with: result)
        }
    }
}
```

**Правило большого пальца**: Используйте `async` почти всегда. `sync` нужен только когда:
1. Вам нужен возвращаемый результат СЕЙЧАС
2. Вы синхронизируете доступ к данным (thread safety)
3. Вы НЕ на главном потоке и не создадите deadlock

---

## Serial vs Concurrent Queues

```
Serial Queue (последовательная)
──────────────────────────────
Task 1 → Task 2 → Task 3 → Task 4
  │       │        │        │
  └───────┴────────┴────────┘
     Один за другим

Concurrent Queue (параллельная)
───────────────────────────────
Task 1 ─────────┐
Task 2 ──────┐  │
Task 3 ───┐  │  │
Task 4 ─┐ │  │  │
        ↓ ↓  ↓  ↓
    Параллельно
```

```swift
// Serial Queue: Гарантированный порядок
let serialQueue = DispatchQueue(label: "com.app.serial")

serialQueue.async { print("1") }
serialQueue.async { print("2") }
serialQueue.async { print("3") }
// Вывод ВСЕГДА: 1, 2, 3

// Concurrent Queue: Порядок НЕ гарантирован
let concurrentQueue = DispatchQueue(
    label: "com.app.concurrent",
    attributes: .concurrent
)

concurrentQueue.async { print("A") }
concurrentQueue.async { print("B") }
concurrentQueue.async { print("C") }
// Вывод МОЖЕТ БЫТЬ: A, C, B или B, A, C и т.д.
```

### Когда использовать Serial vs Concurrent

```swift
// ✅ Serial: Доступ к разделяемым данным
class UserSession {
    private var user: User?
    private let queue = DispatchQueue(label: "com.session.queue")

    func updateUser(_ newUser: User) {
        queue.async {
            // ПОЧЕМУ: Serial гарантирует, что изменения происходят
            // по одному, без race conditions
            self.user = newUser
            self.saveToDefaults()
        }
    }
}

// ✅ Concurrent: Независимые задачи
class ImageProcessor {
    let queue = DispatchQueue(
        label: "com.images.processing",
        attributes: .concurrent
    )

    func processImages(_ images: [UIImage]) {
        for image in images {
            queue.async {
                // ПОЧЕМУ: Каждая картинка обрабатывается независимо,
                // concurrent ускоряет работу
                let processed = self.applyFilters(to: image)
                self.save(processed)
            }
        }
    }
}
```

### Barrier для Concurrent Queue

Барьер позволяет временно сделать concurrent очередь serial:

```
Без Barrier:              С Barrier:
Read  ─┐                  Read  ─┐
Read  ─┤ Параллельно      Read  ─┤ Параллельно
Read  ─┘                  Read  ─┘
Write ─┐ Параллельно           │
Write ─┘ (ПРОБЛЕМА!)           ↓
                           Write ── Барьер (один)
                                │
                                ↓
                           Read  ─┐
                           Read  ─┤ Параллельно
                           Read  ─┘
```

```swift
// ✅ ХОРОШО: Reader-Writer Lock с Barrier
class ThreadSafeCache {
    private var cache: [String: Data] = [:]
    private let queue = DispatchQueue(
        label: "com.cache.queue",
        attributes: .concurrent
    )

    func read(key: String) -> Data? {
        // ПОЧЕМУ: Чтение может быть параллельным
        return queue.sync {
            return cache[key]
        }
    }

    func write(data: Data, key: String) {
        // ПОЧЕМУ: Запись требует эксклюзивного доступа
        queue.async(flags: .barrier) {
            self.cache[key] = data
        }
    }
}
```

---

## Проблема взрыва потоков (Thread Explosion)

### Что это?

Создание слишком большого количества потоков приводит к:
- **Context switching overhead** (переключение контекста)
- **Memory pressure** (каждый поток ~ 512KB-1MB stack)
- **CPU thrashing** (процессор тратит время на переключение)

```
Оптимально:                    Thread Explosion:
Thread Pool (8 cores)          Thread Pool (переполнен)
┌─────────────────┐            ┌─────────────────────────┐
│ T1  T2  T3  T4  │            │ T1 T2 T3 T4 T5 T6 T7 T8 │
│ T5  T6  T7  T8  │            │ T9 T10 T11 ... T50 T100 │
└─────────────────┘            └─────────────────────────┘
  Эффективно                     Деградация производительности
  8 активных потоков             100 потоков борются за 8 ядер
```

### Как возникает

```swift
// ❌ ПЛОХО: Thread Explosion
func processItems(_ items: [Item]) {
    for item in items { // 1000 элементов
        DispatchQueue.global().async {
            // ПОЧЕМУ: Создается 1000 задач одновременно!
            // GCD может создать слишком много потоков
            self.process(item)
        }
    }
}

// ✅ ХОРОШО: Контроль параллелизма с DispatchSemaphore
func processItemsControlled(_ items: [Item]) {
    let semaphore = DispatchSemaphore(value: 4) // Макс. 4 параллельно
    let queue = DispatchQueue(label: "com.processing", attributes: .concurrent)

    for item in items {
        queue.async {
            semaphore.wait() // ПОЧЕМУ: Блокируем если уже 4 активных
            defer { semaphore.signal() } // Освобождаем по завершению

            self.process(item)
        }
    }
}

// ✅ ХОРОШО: OperationQueue с maxConcurrentOperationCount
func processItemsWithOperations(_ items: [Item]) {
    let queue = OperationQueue()
    queue.maxConcurrentOperationCount = 4 // ПОЧЕМУ: Явное ограничение

    for item in items {
        queue.addOperation {
            self.process(item)
        }
    }
}
```

### Признаки Thread Explosion

```swift
// Мониторинг в Xcode
// Debug Navigator → CPU → Threads
// Если видите > 64 потоков - вероятно explosion

// Programmatic detection
func checkThreadCount() {
    var threadCount: mach_msg_type_number_t = 0
    var threads: thread_act_array_t!

    task_threads(mach_task_self_, &threads, &threadCount)

    if threadCount > 64 {
        print("⚠️ Thread explosion: \(threadCount) threads")
    }
}
```

---

## Main Thread Checker

Xcode инструмент для обнаружения UI-операций вне главного потока.

### Включение

```
Xcode → Edit Scheme → Run → Diagnostics
☑ Main Thread Checker
```

### Типичные ошибки

```swift
// ❌ Обнаружит Main Thread Checker
DispatchQueue.global().async {
    // ПОЧЕМУ: UIKit не потокобезопасен
    self.label.text = "Done" // 🔴 Runtime warning!
    self.imageView.image = loadedImage // 🔴 Runtime warning!
    self.tableView.reloadData() // 🔴 Runtime warning!
}

// ✅ Правильный подход
DispatchQueue.global().async {
    let image = self.downloadImage()

    DispatchQueue.main.async {
        // ПОЧЕМУ: Все UI на главном потоке
        self.imageView.image = image
    }
}
```

### Ручная проверка

```swift
func updateLabel(_ text: String) {
    assert(Thread.isMainThread, "Must be called on main thread")
    label.text = text
}

// Или с автоматическим переключением
func safeUpdateUI(_ update: @escaping () -> Void) {
    if Thread.isMainThread {
        update()
    } else {
        DispatchQueue.main.async(execute: update)
    }
}
```

---

## @MainActor (Swift 6 Preview)

Современный подход к управлению главным потоком через Swift Concurrency.

```swift
// ✅ Swift 6: @MainActor гарантирует выполнение на главном потоке
@MainActor
class ProductViewModel: ObservableObject {
    @Published var products: [Product] = []
    @Published var isLoading = false

    // ПОЧЕМУ: Весь класс помечен @MainActor,
    // все свойства и методы автоматически на main thread
    func loadProducts() async {
        isLoading = true

        // ПОЧЕМУ: Сетевой запрос выполняется на фоне автоматически
        let products = await apiService.fetchProducts()

        // ПОЧЕМУ: После await возвращаемся на main thread
        self.products = products
        isLoading = false
    }
}

// Сравнение GCD vs Swift Concurrency
// ❌ GCD (старый подход)
class OldViewModel {
    var products: [Product] = []

    func loadProducts() {
        DispatchQueue.global().async {
            let products = self.apiService.fetchProductsSync()
            DispatchQueue.main.async {
                self.products = products
            }
        }
    }
}

// ✅ Swift Concurrency (новый подход)
@MainActor
class NewViewModel {
    var products: [Product] = []

    func loadProducts() async {
        // ПОЧЕМУ: Компилятор гарантирует безопасность потоков
        products = await apiService.fetchProducts()
    }
}
```

### Детальный контроль

```swift
@MainActor
class MixedViewModel {
    var title: String = ""

    // Этот метод НЕ на main thread
    nonisolated func heavyComputation() -> Int {
        // ПОЧЕМУ: nonisolated позволяет выполняться на любом потоке
        return (0..<1000000).reduce(0, +)
    }

    func updateTitle() async {
        // Выполняется на фоне
        let result = await Task.detached {
            self.heavyComputation()
        }.value

        // ПОЧЕМУ: Автоматически вернулись на main thread
        title = "Result: \(result)"
    }
}
```

---

## Сравнение с Android Threading

| Аспект | iOS | Android |
|--------|-----|---------|
| **Главный поток** | Main Thread / UI Thread | Main Thread / UI Thread |
| **Event Loop** | RunLoop (CFRunLoop) | Looper + MessageQueue |
| **Диспетчеризация** | GCD (DispatchQueue) | Handler + Looper |
| **Фоновые задачи** | DispatchQueue.global() | Thread / ExecutorService |
| **Приоритеты** | QoS (6 уровней) | Thread Priority (5 уровней) |
| **Современный API** | async/await + @MainActor | Coroutines + Dispatchers |

### Эквиваленты

```swift
// iOS: Переключение на главный поток
DispatchQueue.main.async {
    label.text = "Updated"
}

// Android: То же самое
runOnUiThread {
    label.text = "Updated"
}
```

```swift
// iOS: Фоновая работа
DispatchQueue.global(qos: .userInitiated).async {
    let result = heavyTask()
    DispatchQueue.main.async {
        updateUI(result)
    }
}

// Android (Kotlin Coroutines)
viewModelScope.launch(Dispatchers.IO) {
    val result = heavyTask()
    withContext(Dispatchers.Main) {
        updateUI(result)
    }
}
```

### Архитектурные различия

```
iOS RunLoop:
┌──────────────────────────────────┐
│  Main Thread                      │
│  ┌────────────────────────────┐  │
│  │ RunLoop (infinite loop)    │  │
│  │  - Process events          │  │
│  │  - Handle timers           │  │
│  │  - Execute blocks          │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘

Android Looper:
┌──────────────────────────────────┐
│  Main Thread                      │
│  ┌────────────────────────────┐  │
│  │ Looper.loop()              │  │
│  │  MessageQueue              │  │
│  │  │→ Message 1              │  │
│  │  │→ Message 2              │  │
│  │  └→ Message 3              │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

**Общее**: Оба используют event-driven архитектуру с единственным главным потоком для UI.

**Различие**: iOS использует RunLoop с источниками событий, Android — очередь сообщений (MessageQueue).

---

## 6 типичных ошибок

### 1. Блокировка Main Thread

```swift
// ❌ ПЛОХО
class LoginViewController: UIViewController {
    @IBAction func loginTapped() {
        // ПОЧЕМУ: Сетевой запрос блокирует UI на 2-5 секунд
        let response = NetworkManager.shared.loginSync(
            email: emailField.text!,
            password: passwordField.text!
        )
        handleResponse(response) // UI замерзает!
    }
}

// ✅ ХОРОШО
class LoginViewController: UIViewController {
    @IBAction func loginTapped() {
        showLoadingIndicator()

        DispatchQueue.global(qos: .userInitiated).async {
            let response = NetworkManager.shared.loginSync(
                email: self.emailField.text!,
                password: self.passwordField.text!
            )

            // ПОЧЕМУ: UI обновляется только на главном потоке
            DispatchQueue.main.async {
                self.hideLoadingIndicator()
                self.handleResponse(response)
            }
        }
    }
}
```

---

### 2. Deadlock с sync на той же очереди

```swift
// ❌ ПЛОХО: Классический deadlock
let queue = DispatchQueue(label: "com.app.queue")

queue.async {
    // Мы УЖЕ на этой очереди
    queue.sync {
        // ПОЧЕМУ: Serial queue ждет сама себя → зависание!
        print("Deadlock!")
    }
}

// ✅ ХОРОШО: Избегаем вложенного sync
let queue = DispatchQueue(label: "com.app.queue")

queue.async {
    // ПОЧЕМУ: Просто выполняем код напрямую
    print("No deadlock!")
}

// Или используем concurrent queue с осторожностью
let concurrentQueue = DispatchQueue(
    label: "com.app.concurrent",
    attributes: .concurrent
)

concurrentQueue.async {
    concurrentQueue.sync {
        // ПОЧЕМУ: Concurrent queue может это обработать,
        // но sync все равно блокирует текущий поток
        print("Works, but not recommended")
    }
}
```

---

### 3. Неправильный QoS

```swift
// ❌ ПЛОХО: Пользователь ждет, но приоритет низкий
@IBAction func searchButtonTapped() {
    DispatchQueue.global(qos: .background).async {
        // ПОЧЕМУ: .background для задач, которые пользователь НЕ ждет
        let results = self.searchDatabase(query: self.searchField.text!)
        DispatchQueue.main.async {
            self.displayResults(results) // Медленно!
        }
    }
}

// ✅ ХОРОШО: Соответствие приоритета и ожиданий пользователя
@IBAction func searchButtonTapped() {
    // ПОЧЕМУ: Пользователь нажал кнопку и ждет → .userInitiated
    DispatchQueue.global(qos: .userInitiated).async {
        let results = self.searchDatabase(query: self.searchField.text!)
        DispatchQueue.main.async {
            self.displayResults(results)
        }
    }
}
```

---

### 4. Race Condition без синхронизации

```swift
// ❌ ПЛОХО: Несколько потоков изменяют массив
class DataManager {
    var items: [Item] = []

    func addItem(_ item: Item) {
        // ПОЧЕМУ: Array не потокобезопасен
        items.append(item) // Crash возможен!
    }
}

// Использование:
let manager = DataManager()
DispatchQueue.global().async { manager.addItem(item1) }
DispatchQueue.global().async { manager.addItem(item2) }
// Race condition!

// ✅ ХОРОШО: Serial queue для синхронизации
class DataManager {
    private var items: [Item] = []
    private let queue = DispatchQueue(label: "com.data.queue")

    func addItem(_ item: Item) {
        queue.async {
            // ПОЧЕМУ: Serial queue гарантирует последовательность
            self.items.append(item)
        }
    }

    func getItems() -> [Item] {
        return queue.sync {
            return items
        }
    }
}
```

---

### 5. UI обновление вне Main Thread

```swift
// ❌ ПЛОХО: URLSession callback не на main thread
func loadImage(from url: URL) {
    URLSession.shared.dataTask(with: url) { data, _, _ in
        guard let data = data, let image = UIImage(data: data) else { return }

        // ПОЧЕМУ: Completion handler вызывается на фоновом потоке
        self.imageView.image = image // 🔴 Main Thread Checker warning!
    }.resume()
}

// ✅ ХОРОШО: Переключение на main thread
func loadImage(from url: URL) {
    URLSession.shared.dataTask(with: url) { data, _, _ in
        guard let data = data, let image = UIImage(data: data) else { return }

        // ПОЧЕМУ: Явно переключаемся на главный поток
        DispatchQueue.main.async {
            self.imageView.image = image
        }
    }.resume()
}
```

---

### 6. Retain Cycle в async блоках

```swift
// ❌ ПЛОХО: Strong reference cycle
class ProfileViewController: UIViewController {
    var userName: String = ""

    func loadProfile() {
        DispatchQueue.global().async {
            let profile = self.fetchProfile() // ПОЧЕМУ: self захватывается строго
            DispatchQueue.main.async {
                self.userName = profile.name // Strong reference
                self.tableView.reloadData()
            }
        }
        // ViewController может не освободиться!
    }
}

// ✅ ХОРОШО: Weak/unowned self
class ProfileViewController: UIViewController {
    var userName: String = ""

    func loadProfile() {
        DispatchQueue.global().async { [weak self] in
            guard let self = self else { return }
            let profile = self.fetchProfile()

            DispatchQueue.main.async { [weak self] in
                // ПОЧЕМУ: Проверяем, что VC еще существует
                guard let self = self else { return }
                self.userName = profile.name
                self.tableView.reloadData()
            }
        }
    }
}
```

---

## Ментальные модели

### 1. "Очередь — это конвейер задач"

Представьте DispatchQueue как конвейер на заводе:
- **Serial Queue** = один работник обрабатывает по одной детали
- **Concurrent Queue** = несколько работников обрабатывают параллельно
- **QoS** = приоритет срочности заказа
- **sync/async** = ждать результат на месте vs отправить и идти дальше

### 2. "Main Thread — единственная дверь к UI"

```
┌──────────────────────────────────────┐
│         UI Components                 │
│  (UILabel, UIButton, UIImageView)    │
└───────────────┬──────────────────────┘
                │
         Main Thread ONLY
          (single door)
                │
┌───────────────┴──────────────────────┐
│  Background Threads (many workers)   │
│  - Network requests                  │
│  - Data processing                   │
│  - File I/O                          │
└──────────────────────────────────────┘
```

Все фоновые потоки могут готовить данные, но **только Main Thread** может открыть дверь к UI.

### 3. "Thread Explosion = too many cooks"

```
Optimal:                   Explosion:
👨‍🍳 👨‍🍳 👨‍🍳 👨‍🍳              👨‍🍳👨‍🍳👨‍🍳👨‍🍳👨‍🍳👨‍🍳👨‍🍳👨‍🍳
8 поваров                 50 поваров
Эффективная работа        Толкаются, мешают друг другу
```

Слишком много потоков (как поваров на маленькой кухне) приводит к замедлению из-за конкуренции за ресурсы.

### 4. "QoS = срочность доставки"

- **userInteractive**: Экспресс-доставка (сегодня)
- **userInitiated**: Быстрая доставка (1-2 дня)
- **default**: Обычная доставка (3-5 дней)
- **utility**: Экономичная доставка (неделя)
- **background**: Морская почта (когда придет)

### 5. "Race Condition = два кассира и один счет"

```
Кассир 1: Читает баланс = 100₽
Кассир 2: Читает баланс = 100₽
Кассир 1: Добавляет 50₽ → Пишет 150₽
Кассир 2: Добавляет 30₽ → Пишет 130₽ (перезаписывает!)

Решение: Только один кассир за раз (Serial Queue)
```

---

## Практический чеклист

### Перед добавлением async кода:

- [ ] Определили нужный QoS для задачи?
- [ ] Используем async (не sync без необходимости)?
- [ ] UI обновления только на `DispatchQueue.main`?
- [ ] Добавили `[weak self]` если нужно?
- [ ] Проверили отсутствие deadlock возможности?
- [ ] Main Thread Checker включен в схеме?
- [ ] Ограничили параллелизм (если создаем много задач)?
- [ ] Обрабатываем ошибки асинхронно?

### Дебаггинг проблем потоков:

```swift
// Проверка текущего потока
print("Current thread: \(Thread.current)")
print("Is main thread: \(Thread.isMainThread)")

// Вывод всех потоков
Thread.callStackSymbols.forEach { print($0) }

// Breakpoint в Xcode:
// lldb: thread list
// lldb: thread backtrace all
```

---

## Викторина

### Вопрос 1
Что произойдет при выполнении этого кода?
```swift
DispatchQueue.main.async {
    DispatchQueue.main.sync {
        print("Hello")
    }
}
```
a) Выведет "Hello"
b) Deadlock
c) Crash
d) Ничего не произойдет

<details>
<summary>Ответ</summary>
<b>b) Deadlock</b> — Main queue (serial) ждет сама себя. Внешний блок выполняется на main, внутренний sync пытается выполниться на той же main, но она заблокирована внешним блоком.
</details>

---

### Вопрос 2
Какой QoS использовать для загрузки аватара после нажатия кнопки?
a) `.background`
b) `.utility`
c) `.userInitiated`
d) `.userInteractive`

<details>
<summary>Ответ</summary>
<b>c) `.userInitiated`</b> — Пользователь явно инициировал действие и ждет результат. `.userInteractive` только для UI-операций (анимации), `.utility` для длительных задач с прогрессом, `.background` для невидимых задач.
</details>

---

### Вопрос 3
Сколько раз выполнится print в этом коде?
```swift
let queue = DispatchQueue(label: "test", attributes: .concurrent)
for i in 1...5 {
    queue.async {
        print(i)
    }
}
```
a) 0 раз
b) 1 раз
c) 5 раз
d) Невозможно определить

<details>
<summary>Ответ</summary>
<b>c) 5 раз</b> — Каждая итерация создает async задачу, все 5 будут выполнены (порядок не гарантирован). Если бы после цикла программа сразу завершилась, могло бы быть меньше, но в обычных условиях все 5 выполнятся.
</details>

---

### Вопрос 4
В чем ошибка этого кода?
```swift
class ViewModel {
    var data: [String] = []
    let queue = DispatchQueue(label: "data", attributes: .concurrent)

    func addData(_ item: String) {
        queue.async {
            self.data.append(item)
        }
    }
}
```
a) Нет ошибки
b) Race condition
c) Deadlock
d) Memory leak

<details>
<summary>Ответ</summary>
<b>b) Race condition</b> — Concurrent queue позволяет нескольким потокам одновременно изменять массив `data`, что небезопасно. Решение: использовать serial queue или barrier для записи.
</details>

---

### Вопрос 5
Что выведет этот код?
```swift
let queue = DispatchQueue(label: "serial")
queue.async { print("1") }
queue.async { print("2") }
print("3")
```
a) 1, 2, 3
b) 3, 1, 2
c) Порядок случайный
d) 1, 3, 2 или 3, 1, 2

<details>
<summary>Ответ</summary>
<b>d) 1, 3, 2 или 3, 1, 2</b> — "3" выполнится синхронно на текущем потоке, может быть до или после async блоков. Но "1" ВСЕГДА будет перед "2" (serial queue гарантирует порядок своих задач).
</details>

---

### Вопрос 6
Когда использовать `DispatchQueue.main.sync`?
a) Для обновления UI
b) Почти никогда (риск deadlock)
c) Для фоновых задач
d) Вместо async для скорости

<details>
<summary>Ответ</summary>
<b>b) Почти никогда</b> — `main.sync` опасен, так как если вы уже на main thread, получите deadlock. Для UI используйте `main.async`. Единственный редкий случай: вызов с фонового потока когда нужен результат синхронно (но это плохая практика).
</details>

---

## Связанные темы

- [[concurrency-parallelism]] — Теоретические основы параллелизма
- [[android-threading]] — Сравнение с Android подходом
- [[swift-concurrency]] — async/await и actors в Swift
- [[ios-performance-optimization]] — Оптимизация производительности
- [[core-data-concurrency]] — Многопоточность в Core Data
- [[combine-framework]] — Реактивное программирование

---

## Ресурсы

### Apple Documentation
- [Concurrency Programming Guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ConcurrencyProgrammingGuide/)
- [Dispatch Framework](https://developer.apple.com/documentation/dispatch)
- [Swift Concurrency](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)

### WWDC Sessions
- WWDC 2021: Meet async/await in Swift
- WWDC 2021: Protect mutable state with Swift actors
- WWDC 2017: Modernizing Grand Central Dispatch Usage

### Книги
- "Concurrency by Tutorials" — Ray Wenderlich
- "Swift Concurrency by Tutorials" — Ray Wenderlich

---

**Последнее обновление**: 2026-01-11
**Версия**: 1.0
**Автор**: iOS Knowledge Base