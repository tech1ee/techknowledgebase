---
title: "Типичные ошибки конкурентности в iOS"
created: 2026-01-11
modified: 2026-02-13
type: deep-dive
reading_time: 63
difficulty: 8
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/concurrency
  - type/deep-dive
  - level/advanced
related:
  - "[[android-coroutines-mistakes]]"
  - "[[ios-gcd-deep-dive]]"
  - "[[ios-async-await]]"
prerequisites:
  - "[[ios-threading-fundamentals]]"
  - "[[ios-gcd-deep-dive]]"
  - "[[ios-async-await]]"
---

# iOS Concurrency Mistakes

## TL;DR

Распространенные ошибки при работе с конкурентностью в iOS. Покрывает как классический GCD (Grand Central Dispatch), так и современный Swift Concurrency (async/await). Каждая ошибка включает симптомы, плохие и хорошие примеры кода, и детальные объяснения. Понимание этих паттернов критично для создания отзывчивых, безопасных и производительных iOS приложений.

---

## GCD (Grand Central Dispatch) Ошибки

### 1. Блокировка главного потока с sync на глобальной очереди

**Симптом:** UI замораживается, ANR (Application Not Responding), плохой UX.

#### ❌ ПЛОХО

```swift
class DataService {
    func fetchUserData() -> User? {
        var userData: User?

        // Блокируем main thread до завершения работы!
        DispatchQueue.global().sync {
            // Долгая сетевая операция
            let data = URLSession.shared.synchronousDataTask(
                with: URL(string: "https://api.example.com/user")!
            )
            userData = try? JSONDecoder().decode(User.self, from: data)
        }

        return userData
    }
}

// В ViewController
let user = dataService.fetchUserData() // UI зависает!
```

#### ✅ ХОРОШО

```swift
class DataService {
    func fetchUserData(completion: @escaping (Result<User, Error>) -> Void) {
        // Асинхронно выполняем на фоновой очереди
        DispatchQueue.global(qos: .userInitiated).async {
            do {
                let data = try Data(contentsOf: URL(string: "https://api.example.com/user")!)
                let user = try JSONDecoder().decode(User.self, from: data)

                // Результат возвращаем на main thread
                DispatchQueue.main.async {
                    completion(.success(user))
                }
            } catch {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
            }
        }
    }
}

// В ViewController
dataService.fetchUserData { result in
    // UI остается отзывчивым
    switch result {
    case .success(let user):
        self.updateUI(with: user)
    case .failure(let error):
        self.showError(error)
    }
}
```

**Объяснение:** Использование `sync` на main thread блокирует UI до завершения задачи. Всегда используйте `async` для длительных операций и возвращайте результаты через completion handlers. Main thread должен быть свободен для обработки пользовательских взаимодействий и обновлений UI.

---

### 2. Deadlock с sync на той же очереди

**Симптом:** Приложение полностью зависает, deadlock, не реагирует на ввод.

#### ❌ ПЛОХО

```swift
class PaymentProcessor {
    private let processingQueue = DispatchQueue(label: "com.app.payment")

    func processPayment() {
        processingQueue.async {
            print("Starting payment processing")

            // DEADLOCK! Ждем сами себя
            self.processingQueue.sync {
                print("This will never execute")
                self.validatePayment()
            }

            print("This will never print")
        }
    }

    private func validatePayment() {
        // Validation logic
    }
}
```

#### ✅ ХОРОШО

```swift
class PaymentProcessor {
    private let processingQueue = DispatchQueue(label: "com.app.payment")

    func processPayment() {
        processingQueue.async {
            print("Starting payment processing")

            // Прямой вызов - мы уже на нужной очереди
            self.validatePayment()

            print("Payment processed successfully")
        }
    }

    // Альтернатива: использовать другую очередь для вложенной задачи
    func processPaymentWithNestedQueue() {
        processingQueue.async {
            print("Starting payment processing")

            let validationQueue = DispatchQueue(label: "com.app.payment.validation")
            validationQueue.sync {
                self.validatePayment()
            }

            print("Payment processed successfully")
        }
    }

    private func validatePayment() {
        // Validation logic
    }
}
```

**Объяснение:** Serial queue может выполнять только одну задачу за раз. Когда вы вызываете `sync` на той же serial queue, где уже выполняется код, создается deadlock: текущая задача ждет завершения sync блока, а sync блок ждет освобождения очереди. Решение - либо прямой вызов функции, либо использование другой очереди.

---

### 3. Thread explosion с слишком большим количеством concurrent задач

**Симптом:** Высокое потребление памяти, thread overhead, снижение производительности.

#### ❌ ПЛОХО

```swift
class ImageProcessor {
    func processImages(_ images: [UIImage]) {
        // Создаем тысячи потоков одновременно!
        for image in images { // Например, 10,000 изображений
            DispatchQueue.global().async {
                let processed = self.applyFilters(to: image)
                self.saveToCache(processed)
            }
        }
    }

    private func applyFilters(to image: UIImage) -> UIImage {
        // Тяжелая обработка
        return image
    }

    private func saveToCache(_ image: UIImage) {
        // Save logic
    }
}
```

#### ✅ ХОРОШО

```swift
class ImageProcessor {
    // Ограничиваем количество concurrent операций
    private let processingQueue: OperationQueue = {
        let queue = OperationQueue()
        queue.maxConcurrentOperationCount = 4 // Оптимально для CPU-bound задач
        queue.qualityOfService = .userInitiated
        return queue
    }()

    func processImages(_ images: [UIImage]) {
        for image in images {
            let operation = BlockOperation {
                let processed = self.applyFilters(to: image)
                self.saveToCache(processed)
            }
            processingQueue.addOperation(operation)
        }
    }

    // Альтернатива с DispatchSemaphore
    func processImagesWithSemaphore(_ images: [UIImage]) {
        let semaphore = DispatchSemaphore(value: 4) // Максимум 4 одновременно

        for image in images {
            DispatchQueue.global().async {
                semaphore.wait() // Ждем свободный слот
                defer { semaphore.signal() } // Освобождаем слот

                let processed = self.applyFilters(to: image)
                self.saveToCache(processed)
            }
        }
    }

    // Современный подход с TaskGroup (async/await)
    func processImagesModern(_ images: [UIImage]) async {
        await withTaskGroup(of: Void.self) { group in
            for image in images {
                group.addTask {
                    let processed = self.applyFilters(to: image)
                    self.saveToCache(processed)
                }
            }
        }
    }

    private func applyFilters(to image: UIImage) -> UIImage {
        // Тяжелая обработка
        return image
    }

    private func saveToCache(_ image: UIImage) {
        // Save logic
    }
}
```

**Объяснение:** GCD создает новые потоки по мере необходимости, но слишком много concurrent задач приводит к thread explosion - система тратит больше ресурсов на управление потоками, чем на полезную работу. Используйте `OperationQueue` с `maxConcurrentOperationCount` или `DispatchSemaphore` для ограничения параллелизма. Оптимальное число для CPU-bound задач: количество ядер процессора (обычно 2-4).

---

### 4. Забывание dispatch UI updates на main thread

**Симптом:** Crash с "UIKit must be used from main thread", непредсказуемое поведение UI.

#### ❌ ПЛОХО

```swift
class ProfileViewController: UIViewController {
    @IBOutlet weak var avatarImageView: UIImageView!
    @IBOutlet weak var nameLabel: UILabel!

    func loadProfile() {
        DispatchQueue.global().async {
            let profileData = self.fetchProfileFromAPI()
            let avatar = self.downloadImage(from: profileData.avatarURL)

            // ОШИБКА: Обновляем UI не на main thread!
            self.avatarImageView.image = avatar
            self.nameLabel.text = profileData.name

            // Может вызвать crash или странное поведение
            self.view.setNeedsLayout()
        }
    }

    private func fetchProfileFromAPI() -> ProfileData {
        // Network call
        return ProfileData(name: "John", avatarURL: URL(string: "https://example.com")!)
    }

    private func downloadImage(from url: URL) -> UIImage {
        // Download logic
        return UIImage()
    }
}

struct ProfileData {
    let name: String
    let avatarURL: URL
}
```

#### ✅ ХОРОШО

```swift
class ProfileViewController: UIViewController {
    @IBOutlet weak var avatarImageView: UIImageView!
    @IBOutlet weak var nameLabel: UILabel!

    func loadProfile() {
        DispatchQueue.global(qos: .userInitiated).async {
            let profileData = self.fetchProfileFromAPI()
            let avatar = self.downloadImage(from: profileData.avatarURL)

            // Все UI обновления на main thread
            DispatchQueue.main.async {
                self.avatarImageView.image = avatar
                self.nameLabel.text = profileData.name
                self.view.setNeedsLayout()

                // Анимации тоже на main thread
                UIView.animate(withDuration: 0.3) {
                    self.avatarImageView.alpha = 1.0
                }
            }
        }
    }

    // Более элегантный подход с помощником
    func loadProfileWithHelper() {
        DispatchQueue.global(qos: .userInitiated).async {
            let profileData = self.fetchProfileFromAPI()
            let avatar = self.downloadImage(from: profileData.avatarURL)

            self.updateUI {
                self.avatarImageView.image = avatar
                self.nameLabel.text = profileData.name
            }
        }
    }

    private func updateUI(_ updates: @escaping () -> Void) {
        if Thread.isMainThread {
            updates()
        } else {
            DispatchQueue.main.async(execute: updates)
        }
    }

    private func fetchProfileFromAPI() -> ProfileData {
        return ProfileData(name: "John", avatarURL: URL(string: "https://example.com")!)
    }

    private func downloadImage(from url: URL) -> UIImage {
        return UIImage()
    }
}

struct ProfileData {
    let name: String
    let avatarURL: URL
}
```

**Объяснение:** UIKit не является thread-safe. Все обновления UI элементов (UILabel, UIImageView, etc.) должны выполняться на main thread. Runtime проверка в debug builds обнаружит это и вызовет crash. Всегда оборачивайте UI обновления в `DispatchQueue.main.async`. Можно создать helper метод для автоматической проверки `Thread.isMainThread`.

---

### 5. Retain cycles в async closures

**Симптом:** Memory leaks, объекты не освобождаются, рост памяти.

#### ❌ ПЛОХО

```swift
class DataManager {
    var data: [String] = []

    func loadData() {
        // Strong reference cycle: closure захватывает self
        DispatchQueue.global().async {
            let fetchedData = self.performExpensiveFetch()

            // Долгая операция - closure живет долго
            Thread.sleep(forTimeInterval: 5)

            DispatchQueue.main.async {
                // Еще один strong capture
                self.data = fetchedData
                self.notifyObservers()
            }
        }
    }

    private func performExpensiveFetch() -> [String] {
        return ["Item 1", "Item 2"]
    }

    private func notifyObservers() {
        print("Data updated")
    }
}

class ViewController: UIViewController {
    var dataManager: DataManager?

    func viewDidLoad() {
        super.viewDidLoad()
        dataManager = DataManager()
        dataManager?.loadData()

        // Даже если мы установим nil, DataManager не освободится
        // из-за strong reference в closure
    }
}
```

#### ✅ ХОРОШО

```swift
class DataManager {
    var data: [String] = []

    func loadData() {
        // Используем [weak self] для избежания retain cycle
        DispatchQueue.global().async { [weak self] in
            guard let self = self else { return }

            let fetchedData = self.performExpensiveFetch()

            Thread.sleep(forTimeInterval: 5)

            // Снова weak capture во вложенном closure
            DispatchQueue.main.async { [weak self] in
                guard let self = self else { return }
                self.data = fetchedData
                self.notifyObservers()
            }
        }
    }

    // Альтернатива: использовать [unowned self] если уверены что self существует
    func loadDataUnowned() {
        DispatchQueue.global().async { [unowned self] in
            let fetchedData = self.performExpensiveFetch()

            DispatchQueue.main.async { [unowned self] in
                self.data = fetchedData
                self.notifyObservers()
            }
        }
    }

    private func performExpensiveFetch() -> [String] {
        return ["Item 1", "Item 2"]
    }

    private func notifyObservers() {
        print("Data updated")
    }

    deinit {
        print("DataManager deallocated") // Будет вызван с weak/unowned
    }
}

class ViewController: UIViewController {
    var dataManager: DataManager?

    func viewDidLoad() {
        super.viewDidLoad()
        dataManager = DataManager()
        dataManager?.loadData()
    }

    deinit {
        print("ViewController deallocated")
    }
}
```

**Объяснение:** Async closures захватывают self со strong reference по умолчанию. Если closure выполняется долго или хранится где-то, создается retain cycle. Используйте `[weak self]` для безопасного захвата - если объект уничтожен, closure просто выйдет через guard. `[unowned self]` более опасен - crash если объект уже deallocated, но не создает дополнительного overhead.

---

### 6. Race conditions с shared mutable state

**Симптом:** Непредсказуемые результаты, data corruption, sporadic crashes.

#### ❌ ПЛОХО

```swift
class BankAccount {
    private var balance: Double = 1000.0

    func withdraw(_ amount: Double) {
        DispatchQueue.global().async {
            // RACE CONDITION: Несколько потоков читают и пишут одновременно
            if self.balance >= amount {
                Thread.sleep(forTimeInterval: 0.001) // Simulate processing
                self.balance -= amount
                print("Withdrew \(amount), new balance: \(self.balance)")
            } else {
                print("Insufficient funds")
            }
        }
    }

    func deposit(_ amount: Double) {
        DispatchQueue.global().async {
            // RACE CONDITION здесь тоже
            self.balance += amount
            print("Deposited \(amount), new balance: \(self.balance)")
        }
    }
}

// Использование
let account = BankAccount()
for _ in 0..<100 {
    account.withdraw(10) // Результат непредсказуем!
    account.deposit(5)
}
```

#### ✅ ХОРОШО

```swift
// Решение 1: Serial Queue для синхронизации
class BankAccount {
    private var balance: Double = 1000.0
    private let accountQueue = DispatchQueue(label: "com.app.bankaccount")

    func withdraw(_ amount: Double) {
        accountQueue.async {
            if self.balance >= amount {
                Thread.sleep(forTimeInterval: 0.001)
                self.balance -= amount
                print("Withdrew \(amount), new balance: \(self.balance)")
            } else {
                print("Insufficient funds")
            }
        }
    }

    func deposit(_ amount: Double) {
        accountQueue.async {
            self.balance += amount
            print("Deposited \(amount), new balance: \(self.balance)")
        }
    }

    func getBalance(completion: @escaping (Double) -> Void) {
        accountQueue.async {
            completion(self.balance)
        }
    }
}

// Решение 2: Barrier для читателей-писателей
class BankAccountConcurrent {
    private var balance: Double = 1000.0
    private let accountQueue = DispatchQueue(
        label: "com.app.bankaccount",
        attributes: .concurrent
    )

    func withdraw(_ amount: Double) {
        accountQueue.async(flags: .barrier) { // Эксклюзивный доступ
            if self.balance >= amount {
                Thread.sleep(forTimeInterval: 0.001)
                self.balance -= amount
                print("Withdrew \(amount), new balance: \(self.balance)")
            }
        }
    }

    func deposit(_ amount: Double) {
        accountQueue.async(flags: .barrier) { // Эксклюзивный доступ
            self.balance += amount
            print("Deposited \(amount), new balance: \(self.balance)")
        }
    }

    func getBalance(completion: @escaping (Double) -> Void) {
        accountQueue.async { // Читать могут многие одновременно
            completion(self.balance)
        }
    }
}

// Решение 3: NSLock (старый подход)
class BankAccountLocked {
    private var balance: Double = 1000.0
    private let lock = NSLock()

    func withdraw(_ amount: Double) {
        DispatchQueue.global().async {
            self.lock.lock()
            defer { self.lock.unlock() }

            if self.balance >= amount {
                Thread.sleep(forTimeInterval: 0.001)
                self.balance -= amount
                print("Withdrew \(amount), new balance: \(self.balance)")
            }
        }
    }

    func deposit(_ amount: Double) {
        DispatchQueue.global().async {
            self.lock.lock()
            defer { self.lock.unlock() }

            self.balance += amount
            print("Deposited \(amount), new balance: \(self.balance)")
        }
    }
}
```

**Объяснение:** Race condition возникает когда несколько потоков одновременно читают и модифицируют shared mutable state. Решения: 1) Serial queue - все операции выполняются последовательно. 2) Concurrent queue с barriers - чтение concurrent, запись эксклюзивная. 3) Locks (NSLock, os_unfair_lock) - низкоуровневая синхронизация. В современном Swift предпочтительнее использовать actors (см. async/await раздел).

---

## Swift Concurrency (async/await) Ошибки

### 1. Не обрабатывается Task cancellation

**Симптом:** Задачи продолжают работу после отмены, waste ресурсов, некорректное состояние.

#### ❌ ПЛОХО

```swift
class ImageDownloader {
    func downloadImages(urls: [URL]) async -> [UIImage] {
        var images: [UIImage] = []

        for url in urls {
            // Игнорируем cancellation - продолжаем работу даже после отмены
            let image = await downloadImage(from: url)
            images.append(image)
        }

        return images
    }

    private func downloadImage(from url: URL) async -> UIImage {
        // Долгая операция без проверки cancellation
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            return UIImage(data: data) ?? UIImage()
        } catch {
            return UIImage()
        }
    }
}

class ImageGalleryViewController: UIViewController {
    var downloadTask: Task<[UIImage], Never>?

    func loadGallery(urls: [URL]) {
        downloadTask = Task {
            let images = await ImageDownloader().downloadImages(urls: urls)
            await displayImages(images)
        }
    }

    func displayImages(_ images: [UIImage]) async {
        // Update UI
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        downloadTask?.cancel() // Отменяем, но задача продолжает работу!
    }
}
```

#### ✅ ХОРОШО

```swift
class ImageDownloader {
    func downloadImages(urls: [URL]) async throws -> [UIImage] {
        var images: [UIImage] = []

        for url in urls {
            // Проверяем cancellation перед каждой операцией
            try Task.checkCancellation()

            let image = await downloadImage(from: url)
            images.append(image)

            // Альтернатива: использовать Task.isCancelled для graceful handling
            if Task.isCancelled {
                print("Download cancelled, returning partial results")
                break
            }
        }

        return images
    }

    private func downloadImage(from url: URL) async throws -> UIImage {
        // URLSession автоматически поддерживает cancellation
        let (data, _) = try await URLSession.shared.data(from: url)

        // Проверка после долгой операции
        try Task.checkCancellation()

        return UIImage(data: data) ?? UIImage()
    }
}

class ImageGalleryViewController: UIViewController {
    var downloadTask: Task<[UIImage], Error>?

    func loadGallery(urls: [URL]) {
        downloadTask = Task {
            do {
                let images = try await ImageDownloader().downloadImages(urls: urls)

                // Проверяем cancellation перед UI update
                guard !Task.isCancelled else {
                    print("Task cancelled before displaying")
                    return
                }

                await displayImages(images)
            } catch is CancellationError {
                print("Download was cancelled")
            } catch {
                print("Download failed: \(error)")
            }
        }
    }

    @MainActor
    func displayImages(_ images: [UIImage]) {
        // Update UI
    }

    override func viewWillDisappear(_ animated: Bool) {
        super.viewWillDisappear(animated)
        downloadTask?.cancel() // Теперь задача корректно остановится
    }

    deinit {
        downloadTask?.cancel()
    }
}

// Продвинутый пример с withTaskCancellationHandler
class AdvancedImageDownloader {
    func downloadWithCancellationHandler(url: URL) async throws -> UIImage {
        try await withTaskCancellationHandler {
            let (data, _) = try await URLSession.shared.data(from: url)
            return UIImage(data: data) ?? UIImage()
        } onCancel: {
            print("Cleanup on cancellation")
            // Можно выполнить cleanup код
        }
    }
}
```

**Объяснение:** Task cancellation в Swift - это кооперативный механизм. Task не останавливается автоматически при вызове `cancel()`. Необходимо явно проверять `Task.checkCancellation()` (throws CancellationError) или `Task.isCancelled` (для graceful handling). URLSession и другие system APIs поддерживают cancellation автоматически. Всегда проверяйте cancellation перед долгими операциями и перед обновлением UI.

---

### 2. Создание detached tasks некорректно

**Симптом:** Loss of task context, missing priority, no structured concurrency benefits.

#### ❌ ПЛОХО

```swift
class AnalyticsService {
    @MainActor
    func trackUserAction(_ action: String) {
        // ПРОБЛЕМА 1: Detached task теряет приоритет MainActor
        Task.detached {
            await self.sendToServer(action)
            // Выполняется с низким приоритетом, может задержаться
        }
    }

    @MainActor
    func trackMultipleActions(_ actions: [String]) {
        for action in actions {
            // ПРОБЛЕМА 2: Detached tasks не связаны с parent
            // Нет structured concurrency - можем потерять задачи
            Task.detached {
                await self.sendToServer(action)
            }
        }
        // Function returns немедленно, не ждет завершения tasks
    }

    private func sendToServer(_ action: String) async {
        try? await Task.sleep(nanoseconds: 1_000_000_000)
        print("Tracked: \(action)")
    }
}

class ViewControllerBad: UIViewController {
    let analytics = AnalyticsService()

    @MainActor
    func userDidTapButton() {
        analytics.trackUserAction("button_tap")
        // Если контроллер закрывается сразу, задача может не выполниться
    }
}
```

#### ✅ ХОРОШО

```swift
class AnalyticsService {
    @MainActor
    func trackUserAction(_ action: String) {
        // ПРАВИЛЬНО: Обычный Task наследует контекст (priority, actor)
        Task {
            await sendToServer(action)
        }
    }

    @MainActor
    func trackMultipleActions(_ actions: [String]) async {
        // ПРАВИЛЬНО: Structured concurrency с TaskGroup
        await withTaskGroup(of: Void.self) { group in
            for action in actions {
                group.addTask {
                    await self.sendToServer(action)
                }
            }
            // Ждем завершения всех задач
        }
    }

    // Когда НУЖЕН detached task: долгие фоновые операции
    func startBackgroundSync() {
        Task.detached(priority: .background) { // Явно указываем priority
            while !Task.isCancelled {
                await self.performSync()
                try? await Task.sleep(nanoseconds: 300_000_000_000) // 5 min
            }
        }
    }

    private func sendToServer(_ action: String) async {
        try? await Task.sleep(nanoseconds: 1_000_000_000)
        print("Tracked: \(action)")
    }

    private func performSync() async {
        print("Syncing...")
    }
}

class ViewControllerGood: UIViewController {
    let analytics = AnalyticsService()
    var trackingTask: Task<Void, Never>?

    @MainActor
    func userDidTapButton() {
        // Сохраняем reference для возможной отмены
        trackingTask = Task {
            await analytics.trackMultipleActions(["button_tap", "screen_view"])
        }
    }

    deinit {
        trackingTask?.cancel()
    }
}

// Правильное использование detached task для fire-and-forget операций
extension AnalyticsService {
    func logCrash(_ error: Error) {
        // OK: Crash logging должен работать независимо от контекста
        Task.detached(priority: .high) {
            await self.sendCrashReport(error)
        }
    }

    private func sendCrashReport(_ error: Error) async {
        // Критичная операция с высоким приоритетом
    }
}
```

**Объяснение:** `Task.detached` создает задачу вне structured concurrency hierarchy - она не наследует priority, actor context, и не отменяется автоматически с parent task. Обычный `Task { }` предпочтительнее в 95% случаев - наследует контекст вызывающего кода. Detached tasks используйте только для long-running background операций или fire-and-forget логики, где изоляция от parent необходима. Всегда явно указывайте `priority` для detached tasks.

---

### 3. Missing @MainActor для UI updates

**Симптом:** Runtime warnings "Publishing changes from background threads", UI glitches, crashes.

#### ❌ ПЛОХО

```swift
class WeatherViewModel: ObservableObject {
    @Published var temperature: String = "--"
    @Published var condition: String = "Loading..."
    @Published var isLoading: Bool = false

    func loadWeather() async {
        isLoading = true // ⚠️ WARNING: Publishing from background thread!

        let weatherData = await fetchWeatherFromAPI()

        // ⚠️ Обновление UI properties не на main thread
        temperature = "\(weatherData.temp)°C"
        condition = weatherData.condition
        isLoading = false
    }

    private func fetchWeatherFromAPI() async -> WeatherData {
        try? await Task.sleep(nanoseconds: 2_000_000_000)
        return WeatherData(temp: 24, condition: "Sunny")
    }
}

struct WeatherView: View {
    @StateObject private var viewModel = WeatherViewModel()

    var body: some View {
        VStack {
            Text(viewModel.temperature)
            Text(viewModel.condition)
        }
        .task {
            await viewModel.loadWeather() // Может вызвать UI issues
        }
    }
}

struct WeatherData {
    let temp: Int
    let condition: String
}
```

#### ✅ ХОРОШО

```swift
// Решение 1: @MainActor на всем классе (рекомендуется для ViewModels)
@MainActor
class WeatherViewModel: ObservableObject {
    @Published var temperature: String = "--"
    @Published var condition: String = "Loading..."
    @Published var isLoading: Bool = false

    func loadWeather() async {
        isLoading = true // ✅ На main thread

        // Фоновая работа явно переносится на background
        let weatherData = await fetchWeatherFromAPI()

        // ✅ Возвращаемся на main thread автоматически
        temperature = "\(weatherData.temp)°C"
        condition = weatherData.condition
        isLoading = false
    }

    // Будет выполняться на background thread
    nonisolated func fetchWeatherFromAPI() async -> WeatherData {
        try? await Task.sleep(nanoseconds: 2_000_000_000)
        return WeatherData(temp: 24, condition: "Sunny")
    }
}

// Решение 2: @MainActor на отдельных методах
class WeatherViewModelPartial: ObservableObject {
    @Published var temperature: String = "--"
    @Published var condition: String = "Loading..."
    @Published var isLoading: Bool = false

    @MainActor
    func loadWeather() async {
        isLoading = true

        let weatherData = await fetchWeatherFromAPI()

        temperature = "\(weatherData.temp)°C"
        condition = weatherData.condition
        isLoading = false
    }

    private func fetchWeatherFromAPI() async -> WeatherData {
        try? await Task.sleep(nanoseconds: 2_000_000_000)
        return WeatherData(temp: 24, condition: "Sunny")
    }
}

// Решение 3: Явный MainActor.run для legacy code
class WeatherViewModelLegacy: ObservableObject {
    @Published var temperature: String = "--"
    @Published var condition: String = "Loading..."
    @Published var isLoading: Bool = false

    func loadWeather() async {
        await MainActor.run {
            isLoading = true
        }

        let weatherData = await fetchWeatherFromAPI()

        await MainActor.run {
            temperature = "\(weatherData.temp)°C"
            condition = weatherData.condition
            isLoading = false
        }
    }

    private func fetchWeatherFromAPI() async -> WeatherData {
        try? await Task.sleep(nanoseconds: 2_000_000_000)
        return WeatherData(temp: 24, condition: "Sunny")
    }
}

struct WeatherView: View {
    @StateObject private var viewModel = WeatherViewModel()

    var body: some View {
        VStack {
            Text(viewModel.temperature)
            Text(viewModel.condition)
        }
        .task {
            await viewModel.loadWeather()
        }
    }
}

struct WeatherData {
    let temp: Int
    let condition: String
}
```

**Объяснение:** SwiftUI и UIKit требуют обновления UI на main thread. `@MainActor` - это global actor, который гарантирует выполнение на main thread. Для ViewModels и UIViewControllers предпочтительнее маркировать весь класс `@MainActor`. Async методы внутри @MainActor класса автоматически возвращаются на main thread после await. Используйте `nonisolated` для методов, которые должны выполняться на background.

---

### 4. Data races с actors

**Симптом:** Sporadic crashes, data corruption, unpredictable behavior даже с actors.

#### ❌ ПЛОХО

```swift
actor DataCache {
    private var cache: [String: Data] = [:]

    // ПРОБЛЕМА: Возвращаем mutable reference
    func getData(for key: String) -> Data? {
        return cache[key] // Caller может модифицировать Data снаружи actor
    }

    // ПРОБЛЕМА: Принимаем mutable reference
    func setData(_ data: Data, for key: String) {
        cache[key] = data // Data может быть изменена снаружи
    }

    // ОПАСНО: Возвращаем reference type
    func getAllKeys() -> NSMutableArray {
        let keys = NSMutableArray()
        for key in cache.keys {
            keys.add(key)
        }
        return keys // Caller может модифицировать array
    }
}

class DataManager {
    let cache = DataCache()

    func loadData() async {
        let data = Data([1, 2, 3, 4, 5])
        await cache.setData(data, for: "user")

        // RACE: Модифицируем data после передачи в actor
        // Но actor может еще не закончить обработку
        var mutableData = data
        mutableData.append(6)
    }

    func accessKeys() async {
        let keys = await cache.getAllKeys()
        // RACE: Модифицируем returned reference type
        keys.add("new_key")
    }
}
```

#### ✅ ХОРОШО

```swift
actor DataCache {
    private var cache: [String: Data] = [:]

    // ✅ Data is value type - safe to return
    func getData(for key: String) -> Data? {
        return cache[key]
    }

    // ✅ Data is value type - safe to receive
    func setData(_ data: Data, for key: String) {
        cache[key] = data
    }

    // ✅ Возвращаем value type (Array)
    func getAllKeys() -> [String] {
        return Array(cache.keys)
    }

    // ✅ Если нужен reference type - копируем
    func getKeysCopy() -> NSArray {
        return NSArray(array: Array(cache.keys))
    }

    // ✅ Операции с данными внутри actor
    func appendToData(for key: String, value: UInt8) {
        guard var data = cache[key] else { return }
        data.append(value)
        cache[key] = data
    }
}

// Actor с Sendable types для безопасности
actor UserStore {
    // Sendable struct гарантирует thread-safety
    struct User: Sendable {
        let id: String
        let name: String
        let email: String
    }

    private var users: [String: User] = [:]

    func addUser(_ user: User) {
        users[user.id] = user
    }

    func getUser(id: String) -> User? {
        return users[id]
    }

    func getAllUsers() -> [User] {
        return Array(users.values)
    }
}

// Использование изолированного состояния
actor BankAccount {
    private(set) var balance: Double = 1000.0

    func withdraw(_ amount: Double) async throws {
        guard balance >= amount else {
            throw BankError.insufficientFunds
        }

        // Все операции с balance изолированы внутри actor
        try await Task.sleep(nanoseconds: 100_000_000)
        balance -= amount
    }

    func deposit(_ amount: Double) async {
        balance += amount
    }

    // Безопасный доступ к balance извне
    func getBalance() -> Double {
        return balance
    }
}

enum BankError: Error {
    case insufficientFunds
}

class DataManager {
    let cache = DataCache()
    let userStore = UserStore()

    func loadData() async {
        let data = Data([1, 2, 3, 4, 5])
        await cache.setData(data, for: "user")

        // ✅ Изменяем через actor method
        await cache.appendToData(for: "user", value: 6)
    }

    func accessKeys() async {
        let keys = await cache.getAllKeys()
        // ✅ keys - это value type copy, можем безопасно модифицировать
        var mutableKeys = keys
        mutableKeys.append("new_key")
    }

    func workWithUsers() async {
        let user = UserStore.User(id: "1", name: "John", email: "john@example.com")
        await userStore.addUser(user)

        if let retrievedUser = await userStore.getUser(id: "1") {
            print(retrievedUser.name) // Safe
        }
    }
}
```

**Объяснение:** Actors защищают от data races только для состояния ВНУТРИ actor. Если вы возвращаете reference types (NSArray, NSMutableDictionary) или принимаете их, actor не может гарантировать безопасность - вызывающий код может модифицировать эти объекты вне actor isolation. Используйте value types (struct, enum, Array, Dictionary) или возвращайте копии reference types. Swift 6 введет Sendable checking для compile-time гарантий безопасности.

---

### 5. Holding actor isolated state across suspension

**Симптом:** Unexpected state changes, race conditions, логические ошибки.

#### ❌ ПЛОХО

```swift
actor ShoppingCart {
    private var items: [String: Int] = [:] // product: quantity
    private var totalPrice: Double = 0.0

    func checkout() async throws -> Receipt {
        // 1. Читаем состояние
        let currentItems = items
        let currentTotal = totalPrice

        print("Starting checkout with \(currentItems.count) items")

        // ⚠️ SUSPENSION POINT - состояние actor может измениться!
        try await processPayment(amount: currentTotal)

        // 2. ОПАСНО: Используем старое значение currentItems/currentTotal
        // Но items и totalPrice могли измениться во время processPayment!
        let receipt = Receipt(
            items: currentItems,  // Может быть outdated
            total: currentTotal   // Может быть outdated
        )

        // 3. Очищаем cart на основе старого состояния
        items.removeAll()
        totalPrice = 0.0

        return receipt
    }

    func addItem(_ product: String, quantity: Int, price: Double) {
        items[product, default: 0] += quantity
        totalPrice += price * Double(quantity)
        print("Added \(product), new total: \(totalPrice)")
    }

    private func processPayment(amount: Double) async throws {
        // Долгая операция
        try await Task.sleep(nanoseconds: 2_000_000_000)
        print("Payment processed: $\(amount)")
    }
}

struct Receipt {
    let items: [String: Int]
    let total: Double
}

// Проблемный сценарий
func problematicScenario() async throws {
    let cart = ShoppingCart()

    await cart.addItem("iPhone", quantity: 1, price: 999.0)

    // Одновременно начинаем checkout и добавляем еще товар
    async let receipt = cart.checkout()

    // Во время processPayment добавляем товар
    try await Task.sleep(nanoseconds: 1_000_000_000)
    await cart.addItem("AirPods", quantity: 1, price: 199.0)

    let finalReceipt = try await receipt
    // Receipt может не включать AirPods, но они все равно удалятся из cart!
}
```

#### ✅ ХОРОШО

```swift
actor ShoppingCart {
    private var items: [String: Int] = [:]
    private var totalPrice: Double = 0.0
    private var isCheckingOut: Bool = false

    func checkout() async throws -> Receipt {
        // Защита от concurrent checkout
        guard !isCheckingOut else {
            throw CartError.checkoutInProgress
        }
        isCheckingOut = true
        defer { isCheckingOut = false }

        // ✅ Захватываем состояние один раз перед suspension
        let itemsToCheckout = items
        let totalToCharge = totalPrice

        // Очищаем cart ДО долгой операции
        items.removeAll()
        totalPrice = 0.0

        print("Checking out \(itemsToCheckout.count) items")

        do {
            // Долгая операция - состояние уже сохранено
            try await processPayment(amount: totalToCharge)

            // ✅ Используем captured значения
            return Receipt(
                items: itemsToCheckout,
                total: totalToCharge,
                timestamp: Date()
            )
        } catch {
            // Rollback: восстанавливаем items при ошибке
            await restoreItems(itemsToCheckout, total: totalToCharge)
            throw error
        }
    }

    func addItem(_ product: String, quantity: Int, price: Double) throws {
        guard !isCheckingOut else {
            throw CartError.checkoutInProgress
        }

        items[product, default: 0] += quantity
        totalPrice += price * Double(quantity)
        print("Added \(product), new total: \(totalPrice)")
    }

    private func restoreItems(_ restoredItems: [String: Int], total: Double) {
        items = restoredItems
        totalPrice = total
        print("Cart restored after payment failure")
    }

    private func processPayment(amount: Double) async throws {
        try await Task.sleep(nanoseconds: 2_000_000_000)
        print("Payment processed: $\(amount)")
    }

    // Дополнительный метод для проверки состояния
    func getCartSummary() -> (itemCount: Int, total: Double, checkingOut: Bool) {
        return (items.values.reduce(0, +), totalPrice, isCheckingOut)
    }
}

enum CartError: Error {
    case checkoutInProgress
    case invalidState
}

struct Receipt {
    let items: [String: Int]
    let total: Double
    let timestamp: Date
}

// Правильный сценарий
func correctScenario() async throws {
    let cart = ShoppingCart()

    await cart.addItem("iPhone", quantity: 1, price: 999.0)

    // Начинаем checkout
    async let receipt = cart.checkout()

    // Попытка добавить товар во время checkout
    try await Task.sleep(nanoseconds: 1_000_000_000)
    do {
        try await cart.addItem("AirPods", quantity: 1, price: 199.0)
    } catch CartError.checkoutInProgress {
        print("Cannot add items during checkout - correct!")
    }

    let finalReceipt = try await receipt
    print("Receipt: \(finalReceipt.items), Total: $\(finalReceipt.total)")

    // Теперь можем добавить товар
    try await cart.addItem("AirPods", quantity: 1, price: 199.0)
}

// Альтернативный подход: snapshot pattern
actor ShoppingCartSnapshot {
    private var items: [String: Int] = [:]
    private var totalPrice: Double = 0.0

    struct Snapshot {
        let items: [String: Int]
        let total: Double
        let timestamp: Date
    }

    func createSnapshot() -> Snapshot {
        return Snapshot(
            items: items,
            total: totalPrice,
            timestamp: Date()
        )
    }

    func checkout() async throws -> Receipt {
        // Создаем immutable snapshot
        let snapshot = createSnapshot()

        // Очищаем cart
        items.removeAll()
        totalPrice = 0.0

        // Работаем со snapshot - гарантированно consistent
        try await processPayment(amount: snapshot.total)

        return Receipt(
            items: snapshot.items,
            total: snapshot.total,
            timestamp: snapshot.timestamp
        )
    }

    func addItem(_ product: String, quantity: Int, price: Double) {
        items[product, default: 0] += quantity
        totalPrice += price * Double(quantity)
    }

    private func processPayment(amount: Double) async throws {
        try await Task.sleep(nanoseconds: 2_000_000_000)
    }
}
```

**Объяснение:** Actor isolation не сохраняется между suspension points (await). После await другой код мог изменить actor state. Захватывайте нужное состояние в локальные переменные ДО первого await. Не полагайтесь на то, что состояние останется неизменным после async операций. Используйте snapshot pattern для создания immutable копий состояния или блокируйте операции через флаги (isCheckingOut) для предотвращения concurrent modifications.

---

### 6. Misunderstanding structured concurrency lifetime

**Симптом:** Tasks cancelled prematurely, unexpected behavior, resource leaks.

#### ❌ ПЛОХО

```swift
class DataSyncService {
    func syncAllData() async {
        // ПРОБЛЕМА: TaskGroup завершается когда выходим из withTaskGroup
        await withTaskGroup(of: Void.self) { group in
            group.addTask {
                await self.syncUsers()
            }
            group.addTask {
                await self.syncMessages()
            }
            // Выходим из scope рано
        }

        // Tasks могут быть отменены, если parent завершился!
        print("Sync completed") // Может напечататься до завершения tasks
    }

    func syncWithEarlyReturn() async throws {
        try await withThrowingTaskGroup(of: Void.self) { group in
            group.addTask {
                await self.syncUsers()
            }

            group.addTask {
                try await self.syncCriticalData() // Может throw
            }

            group.addTask {
                await self.syncMessages()
            }

            // ПРОБЛЕМА: Early return отменяет все tasks
            for try await _ in group {
                // Если syncCriticalData throws, выходим сразу
                // Остальные tasks отменяются!
            }
        }
        // syncUsers и syncMessages могут не завершиться
    }

    func syncUsers() async {
        print("Syncing users...")
        try? await Task.sleep(nanoseconds: 2_000_000_000)
        print("Users synced")
    }

    func syncMessages() async {
        print("Syncing messages...")
        try? await Task.sleep(nanoseconds: 3_000_000_000)
        print("Messages synced")
    }

    func syncCriticalData() async throws {
        print("Syncing critical data...")
        try await Task.sleep(nanoseconds: 1_000_000_000)
        throw SyncError.networkError
    }
}

enum SyncError: Error {
    case networkError
}

// ПРОБЛЕМА: Detached task живет после deinit
class BackgroundSyncManager {
    func startSync() {
        Task.detached {
            while true {
                await self.performSync() // self может быть deallocated!
                try? await Task.sleep(nanoseconds: 60_000_000_000)
            }
        }
    }

    func performSync() async {
        print("Syncing...")
    }

    deinit {
        print("Manager deallocated - but task still running!")
    }
}
```

#### ✅ ХОРОШО

```swift
class DataSyncService {
    func syncAllData() async {
        // ✅ withTaskGroup ждет завершения ВСЕХ tasks
        await withTaskGroup(of: Void.self) { group in
            group.addTask {
                await self.syncUsers()
            }
            group.addTask {
                await self.syncMessages()
            }

            // Явно ждем все задачи
            await group.waitForAll()
        }

        // ✅ Гарантированно все tasks завершены
        print("All sync completed")
    }

    func syncWithGracefulError() async throws {
        var firstError: Error?

        await withThrowingTaskGroup(of: Void.self) { group in
            group.addTask {
                await self.syncUsers()
            }

            group.addTask {
                do {
                    try await self.syncCriticalData()
                } catch {
                    // Сохраняем ошибку, но не прерываем group
                }
            }

            group.addTask {
                await self.syncMessages()
            }

            // ✅ Обрабатываем результаты, но ждем все tasks
            for try await _ in group {
                // Process results
            }
        }

        // Все tasks завершены, теперь можем throw
        if let error = firstError {
            throw error
        }
    }

    func syncWithPartialResults() async -> SyncResult {
        var completedSyncs: [String] = []
        var errors: [String: Error] = [:]

        await withTaskGroup(of: SyncTaskResult.self) { group in
            group.addTask {
                do {
                    try await self.syncUsers()
                    return .success("users")
                } catch {
                    return .failure("users", error)
                }
            }

            group.addTask {
                do {
                    try await self.syncCriticalData()
                    return .success("critical")
                } catch {
                    return .failure("critical", error)
                }
            }

            group.addTask {
                do {
                    try await self.syncMessages()
                    return .success("messages")
                } catch {
                    return .failure("messages", error)
                }
            }

            // ✅ Собираем результаты всех tasks
            for await result in group {
                switch result {
                case .success(let name):
                    completedSyncs.append(name)
                case .failure(let name, let error):
                    errors[name] = error
                }
            }
        }

        return SyncResult(completed: completedSyncs, errors: errors)
    }

    func syncUsers() async throws {
        print("Syncing users...")
        try await Task.sleep(nanoseconds: 2_000_000_000)
        print("Users synced")
    }

    func syncMessages() async throws {
        print("Syncing messages...")
        try await Task.sleep(nanoseconds: 3_000_000_000)
        print("Messages synced")
    }

    func syncCriticalData() async throws {
        print("Syncing critical data...")
        try await Task.sleep(nanoseconds: 1_000_000_000)
        throw SyncError.networkError
    }
}

enum SyncTaskResult {
    case success(String)
    case failure(String, Error)
}

struct SyncResult {
    let completed: [String]
    let errors: [String: Error]
}

enum SyncError: Error {
    case networkError
}

// ✅ Правильное управление lifetime
class BackgroundSyncManager {
    private var syncTask: Task<Void, Never>?

    func startSync() {
        // Task привязан к lifetime объекта
        syncTask = Task { [weak self] in
            while !Task.isCancelled {
                guard let self = self else { return }
                await self.performSync()

                try? await Task.sleep(nanoseconds: 60_000_000_000)
            }
        }
    }

    func stopSync() {
        syncTask?.cancel()
        syncTask = nil
    }

    func performSync() async {
        print("Syncing...")
    }

    deinit {
        syncTask?.cancel()
        print("Manager deallocated - task cancelled")
    }
}

// Structured concurrency с async let
class StructuredSyncService {
    func syncAllDataStructured() async throws {
        // ✅ async let создает child tasks
        async let users = syncUsers()
        async let messages = syncMessages()
        async let critical = syncCriticalData()

        // Все tasks выполняются параллельно
        // await ждет завершения всех
        try await users
        try await messages
        try await critical

        print("All syncs completed")
        // Если один throws, остальные автоматически отменяются
    }

    func syncUsers() async throws {
        try await Task.sleep(nanoseconds: 2_000_000_000)
    }

    func syncMessages() async throws {
        try await Task.sleep(nanoseconds: 3_000_000_000)
    }

    func syncCriticalData() async throws {
        try await Task.sleep(nanoseconds: 1_000_000_000)
    }
}
```

**Объяснение:** Structured concurrency означает что child tasks автоматически управляются parent scope. `withTaskGroup` не завершится пока все child tasks не завершены или не отменены. Early return из group отменяет все оставшиеся tasks. `async let` создает child tasks которые отменяются если parent scope выходит или throws. Detached tasks НЕ участвуют в structured concurrency - их нужно отменять вручную. Храните Task references и отменяйте их в deinit для предотвращения утечек.

---

## Общие рекомендации

### Выбор между GCD и async/await

**Используйте async/await когда:**
- Новый Swift 6 код с iOS 15+
- Нужна type-safety и compile-time проверки
- Работа с actors и MainActor
- Structured concurrency для управления lifetime
- Интеграция с SwiftUI и modern APIs

**Используйте GCD когда:**
- Legacy код или поддержка iOS 14 и ниже
- Нужен низкоуровневый контроль над threads
- Performance-critical code с минимальным overhead
- Интеграция с C/Objective-C APIs
- Fire-and-forget операции

### Performance советы

1. **Избегайте thread hopping** - минимизируйте переключения между queues
2. **Используйте правильный QoS** - `.userInitiated` для UI-related, `.utility` для background
3. **Батчируйте операции** - группируйте мелкие tasks для снижения overhead
4. **Профилируйте с Instruments** - используйте Time Profiler и System Trace
5. **Ограничивайте параллелизм** - не создавайте больше tasks чем ядер CPU

### Debugging советы

1. **Main Thread Checker** - автоматически детектит UI updates не на main thread
2. **Thread Sanitizer (TSan)** - находит data races и race conditions
3. **Instruments: System Trace** - визуализирует thread activity
4. **Debug → View Debugging → Logging** - включить concurrency logging
5. **Swift Concurrency Instruments** - новый template для async/await debugging

---

## Связь с другими темами

**[[android-coroutines-mistakes]]** — Аналогичные ошибки конкурентности существуют в Android Coroutines (блокирование main thread, утечки корутин, некорректная обработка cancellation), но проявляются по-разному из-за различий в threading моделях. Сравнение ошибок на обеих платформах формирует универсальное понимание concurrent programming и помогает на кросс-платформенных собеседованиях. Рекомендуется изучить ошибки iOS первыми, затем сравнить с Android для закрепления паттернов.

**[[ios-gcd-deep-dive]]** — Глубокое понимание GCD (dispatch queues, sync vs async, serial vs concurrent, QoS) является обязательным prerequisite для понимания ошибок конкурентности. Многие классические ошибки (deadlock при sync на main queue, thread explosion при чрезмерном создании concurrent tasks) напрямую связаны с механикой GCD. Рекомендуется изучить GCD deep dive перед изучением ошибок, чтобы понять не только «что неправильно», но и «почему».

**[[ios-async-await]]** — Swift Concurrency (async/await, actors, Sendable) устраняет многие классические ошибки GCD на уровне компилятора: data races предотвращаются через actor isolation, UI updates на main thread гарантируются через @MainActor, а structured concurrency исключает утечки задач. Однако async/await вводит свои антипаттерны (избыточные suspension points, actor reentrancy). Изучите ошибки GCD, затем поймите, как async/await их решает.

**[[ios-threading-fundamentals]]** — Threading fundamentals (процессы, потоки, run loops, synchronization primitives) формируют базу для понимания всех ошибок конкурентности. Без знания того, как работают потоки на уровне ОС, невозможно понять, почему data race приводит к крашу или почему deadlock замораживает приложение. Рекомендуется изучить fundamentals перед ошибками.

## References

- [Swift Concurrency Documentation](https://docs.swift.org/swift-book/LanguageGuide/Concurrency.html)
- [WWDC21: Meet async/await in Swift](https://developer.apple.com/videos/play/wwdc2021/10132/)
- [WWDC21: Protect mutable state with Swift actors](https://developer.apple.com/videos/play/wwdc2021/10133/)
- [Concurrency Programming Guide](https://developer.apple.com/library/archive/documentation/General/Conceptual/ConcurrencyProgrammingGuide/)
- [Thread Sanitizer Documentation](https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early)

## Источники и дальнейшее чтение

- Eidhof C. et al. (2019). *Advanced Swift.* — продвинутые паттерны Swift, включая memory management и value semantics, которые помогают избежать data races
- Sundell J. (2022). *Swift by Sundell.* — практические примеры безопасной работы с конкурентностью, включая actors, Sendable и structured concurrency
- Apple (2023). *The Swift Programming Language.* — официальная глава по Concurrency с описанием actors, async/await и Sendable protocol, необходимая для понимания Swift 6 strict concurrency

---

## Проверь себя

> [!question]- Почему data race -- самая опасная ошибка конкурентности, и как Swift 6 помогает ее предотвратить на этапе компиляции?
> Data race возникает при одновременном доступе к мутабельному состоянию из разных потоков без синхронизации. Опасна тем, что проявляется непредсказуемо и часто не воспроизводится при отладке. Swift 6 strict concurrency требует Sendable для межпоточных передач и actor isolation для shared state, превращая runtime баги в ошибки компиляции.

> [!question]- Сценарий: ваш коллега использует DispatchQueue.main.sync внутри viewDidLoad(). Приложение зависает. Объясните причину и предложите fix.
> viewDidLoad() уже выполняется на Main Thread. DispatchQueue.main.sync пытается добавить задачу в main queue и ждать ее выполнения, но main queue занята текущим viewDidLoad(). Результат: deadlock. Fix: использовать DispatchQueue.main.async (если нужна отложенная отправка) или просто выполнить код напрямую (он уже на main thread).

> [!question]- В чем разница между retain cycle в Combine и в GCD, и какие подходы предотвращения у каждого?
> В GCD: closure захватывает self сильной ссылкой, если не использовать [weak self]. В Combine: AnyCancellable хранится в self, а sink-closure захватывает self -- образуется цикл. В Combine решение: [weak self] в sink + хранение cancellables в Set<AnyCancellable>. AnyCancellable автоматически отменяет подписку при deinit, разрывая цикл.

> [!question]- Почему Thread Sanitizer (TSan) не находит все data races, и какие дополнительные инструменты помогают?
> TSan обнаруживает races только на путях выполнения, которые реально были вызваны во время тестирования. Если race condition возникает редко, TSan может не заметить. Дополнительно: Swift 6 strict concurrency (статический анализ), Instruments Allocations (утечки от race), стресс-тесты с randomized scheduling, code review с фокусом на shared state.

---

## Ключевые карточки

Что такое deadlock в контексте iOS и как его избежать?
?
Deadlock -- взаимная блокировка, когда два потока ждут друг друга. Частый случай в iOS: DispatchQueue.main.sync из main thread. Правила: никогда не вызывать sync на текущей очереди, избегать вложенных sync-вызовов, использовать async вместо sync где возможно.

Что такое priority inversion и как GCD его решает?
?
Priority inversion: высокоприоритетная задача ждет ресурс, захваченный низкоприоритетной. GCD использует priority boosting -- временно повышает приоритет задачи, держащей ресурс. Но это не всегда работает с custom locks. Лучше: избегать блокировок, использовать actors.

Почему [weak self] важен в async-замыканиях?
?
Без [weak self] замыкание создает сильную ссылку на self, предотвращая деаллокацию. В async-контексте замыкание может жить дольше объекта (сетевой запрос продолжается после закрытия экрана). [weak self] позволяет объекту деаллоцироваться, а guard let self проверяет существование.

Что такое thread explosion и его симптомы?
?
Создание чрезмерного числа потоков (>64). Симптомы: высокий CPU при малой полезной нагрузке, медленный отклик UI, предупреждения в Instruments. Причины: sync-вызовы в concurrent queue, блокирующие I/O операции. Решение: async/await, OperationQueue с лимитом, serial queues.

Как actor isolation предотвращает data races?
?
Actor гарантирует, что его состояние доступно только одному вызову одновременно. Обращение к actor-свойствам извне требует await (ожидание очереди). Компилятор запрещает прямой доступ без await. Non-isolated методы не имеют доступа к мутабельному состоянию actor.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-debugging]] | Инструменты отладки для поиска concurrency-багов |
| Углубиться | [[ios-performance-profiling]] | Профилирование конкурентного кода в Instruments |
| Смежная тема | [[android-coroutines-mistakes]] | Типичные ошибки конкурентности в Android/Kotlin |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |