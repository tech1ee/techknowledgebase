---
title: "iOS Async/Await и современная конкурентность в Swift"
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
  - "[[ios-threading-fundamentals]]"
  - "[[ios-async-evolution]]"
  - "[[ios-gcd-deep-dive]]"
prerequisites:
  - "[[ios-threading-fundamentals]]"
  - "[[ios-app-components]]"
---

# iOS Async/Await и Современная Конкурентность в Swift

## TL;DR

Swift async/await — это современная модель конкурентности, введённая в Swift 5.5 и улучшенная в Swift 6. Она заменяет completion handlers линейным, читаемым кодом. Ключевые концепции: **suspension points** (точки приостановки), **structured concurrency** (структурированная конкурентность), **actors** (изолированные объекты), **TaskGroup** (группы задач) и **MainActor** (главный поток UI). Swift 6.2 добавляет Approachable Concurrency для упрощения работы с конкурентностью.

**Аналогия**: Представьте ресторан. Официант (async функция) принимает заказ и вместо того, чтобы стоять у кухни и ждать (blocking), идёт обслуживать других клиентов (suspension). Когда блюдо готово (await), кухня вызывает официанта, и он продолжает обслуживание конкретного клиента. Каждый столик — это Task, а вся система — structured concurrency.

## Содержание

1. [Основы Async/Await](#основы-asyncawait)
2. [Точки Приостановки и Continuations](#точки-приостановки-и-continuations)
3. [Tasks: Единицы Асинхронной Работы](#tasks-единицы-асинхронной-работы)
4. [TaskGroup и Параллельное Выполнение](#taskgroup-и-параллельное-выполнение)
5. [Структурированная Конкурентность](#структурированная-конкурентность)
6. [Отмена Задач](#отмена-задач)
7. [TaskLocal Значения](#tasklocal-значения)
8. [Async Let для Параллельной Работы](#async-let-для-параллельной-работы)
9. [Actors и Изоляция](#actors-и-изоляция)
10. [MainActor для UI Обновлений](#mainactor-для-ui-обновлений)
11. [AsyncSequence и AsyncStream](#asyncsequence-и-asyncstream)
12. [Swift 6.2 Approachable Concurrency](#swift-62-approachable-concurrency)
13. [Интеграция с Combine](#интеграция-с-combine)
14. [Сравнение с Kotlin Coroutines](#сравнение-с-kotlin-coroutines)
15. [Типичные Ошибки](#типичные-ошибки)

---

## Основы Async/Await

### Синтаксис и Семантика

Async/await преобразует асинхронный код из callback-стиля в линейный, императивный стиль.

```swift
// ❌ Старый стиль с completion handlers
func fetchUserOld(id: String, completion: @escaping (Result<User, Error>) -> Void) {
    URLSession.shared.dataTask(with: URL(string: "https://api.com/users/\(id)")!) { data, response, error in
        if let error = error {
            completion(.failure(error))
            return
        }

        guard let data = data else {
            completion(.failure(NetworkError.noData))
            return
        }

        do {
            let user = try JSONDecoder().decode(User.self, from: data)
            completion(.success(user))
        } catch {
            completion(.failure(error))
        }
    }.resume()
}

// ✅ Современный стиль с async/await
func fetchUser(id: String) async throws -> User {
    let url = URL(string: "https://api.com/users/\(id)")!
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}
```

### ASCII Диаграмма: Execution Flow

```
Синхронный код:
Thread: [====A====][====B====][====C====]
        |         ||         ||         |
        Start     End       End        End

Async/await код:
Thread: [=A=]--suspend--[=A=]--suspend--[=A=]
             |              |              |
             [====B====]    [====C====]    |
                                          End

Легенда:
[===]  - активное выполнение на потоке
--     - suspension (поток свободен для другой работы)
```

### Ключевые Правила

1. **async** функция может приостанавливаться (suspend) в точках **await**
2. **await** можно использовать только внутри **async** контекста
3. **throws** работает с async: `async throws`
4. Async функции создают **suspension points**, где выполнение может быть приостановлено

```swift
// Производственный пример: Многоуровневая загрузка данных
actor DataRepository {
    private let cache = NSCache<NSString, CachedData>()

    func fetchData(for key: String) async throws -> Data {
        // Проверка кэша (синхронно)
        if let cached = cache.object(forKey: key as NSString) {
            if !cached.isExpired {
                return cached.data
            }
        }

        // Загрузка из сети (асинхронно)
        let data = try await networkFetch(key: key)

        // Кэширование результата
        cache.setObject(
            CachedData(data: data, timestamp: Date()),
            forKey: key as NSString
        )

        return data
    }

    private func networkFetch(key: String) async throws -> Data {
        let url = URL(string: "https://api.com/data/\(key)")!
        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.invalidResponse
        }

        return data
    }
}

private class CachedData {
    let data: Data
    let timestamp: Date

    var isExpired: Bool {
        Date().timeIntervalSince(timestamp) > 300 // 5 минут
    }

    init(data: Data, timestamp: Date) {
        self.data = data
        self.timestamp = timestamp
    }
}

enum NetworkError: Error {
    case invalidResponse
    case noData
}
```

---

## Точки Приостановки и Continuations

### Suspension Points

**Точка приостановки** (suspension point) — это место в async функции, где выполнение может быть приостановлено для выполнения другой работы.

```
Поток выполнения с suspension:

Time →
Thread 1: [func A start]--await network--[func A resume]--await DB--[func A end]
                         |                                |
                         During suspension:               During suspension:
                         [func B runs]                    [func C runs]

Преимущества:
- Поток не блокируется
- Эффективное использование CPU
- Тысячи concurrent operations на одном потоке
```

### Continuations: Мост к Legacy Code

**Continuations** позволяют обернуть callback-based код в async/await.

```swift
// ❌ Legacy callback API
class LocationManager {
    func requestLocation(completion: @escaping (Result<CLLocation, Error>) -> Void) {
        // Старый callback-based код
    }
}

// ✅ Обёртка с withCheckedContinuation
extension LocationManager {
    func requestLocation() async throws -> CLLocation {
        try await withCheckedThrowingContinuation { continuation in
            self.requestLocation { result in
                continuation.resume(with: result)
            }
        }
    }
}

// Использование
func getCurrentLocation() async throws -> CLLocation {
    let manager = LocationManager()
    let location = try await manager.requestLocation()
    return location
}
```

### Checked vs Unchecked Continuations

```swift
// ✅ withCheckedContinuation - проверяет двойной resume в debug
func safeWrapper() async -> String {
    await withCheckedContinuation { continuation in
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            continuation.resume(returning: "Done")
            // continuation.resume(returning: "Again") // ❌ Crash в debug
        }
    }
}

// ⚠️ withUnsafeContinuation - без проверок, чуть быстрее
func unsafeWrapper() async -> String {
    await withUnsafeContinuation { continuation in
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            continuation.resume(returning: "Done")
            // Двойной resume = undefined behavior
        }
    }
}

// Производственный пример: Firebase обёртка
extension DatabaseReference {
    func observeSingleValue() async throws -> DataSnapshot {
        try await withCheckedThrowingContinuation { continuation in
            self.observeSingleEvent(of: .value) { snapshot in
                continuation.resume(returning: snapshot)
            } withCancel: { error in
                continuation.resume(throwing: error)
            }
        }
    }
}
```

**Важно**: Continuation должен вызвать `resume` ровно один раз. Меньше — утечка памяти, больше — crash.

---

## Tasks: Единицы Асинхронной Работы

### Task {} - Unstructured Task

**Task** — это единица асинхронной работы. `Task {}` создаёт новую задачу, которая наследует приоритет и контекст.

```swift
// ✅ Создание Task из синхронного контекста
func viewDidLoad() {
    super.viewDidLoad()

    Task {
        // Async код внутри sync контекста
        let user = try await fetchUser(id: "123")
        await updateUI(with: user)
    }
}

// ✅ Захват результата Task
func loadData() {
    let task = Task<User, Error> {
        try await fetchUser(id: "123")
    }

    // Можно отменить позже
    // task.cancel()

    // Можно дождаться результата
    Task {
        let user = try await task.value
        print(user.name)
    }
}
```

### Task.detached - Полностью Независимая Задача

**Task.detached** создаёт задачу, которая **не наследует** приоритет, actor context или TaskLocal значения.

```swift
// ❌ Task {} - наследует контекст
@MainActor
func incorrectBackgroundWork() {
    Task {
        // ❌ Всё ещё на MainActor!
        let data = processLargeDataset() // Блокирует UI
    }
}

// ✅ Task.detached - независимая задача
@MainActor
func correctBackgroundWork() {
    Task.detached {
        // ✅ Выполняется на фоновом потоке
        let data = processLargeDataset()

        // Переключаемся на MainActor для UI
        await MainActor.run {
            self.updateUI(with: data)
        }
    }
}

// Производственный пример: Background processing
actor ImageProcessor {
    func processImages(_ urls: [URL]) async -> [UIImage] {
        await withTaskGroup(of: UIImage?.self) { group in
            for url in urls {
                group.addTask {
                    // Каждая задача выполняется независимо
                    try? await self.downloadAndProcess(url)
                }
            }

            var images: [UIImage] = []
            for await image in group.compactMap({ $0 }) {
                images.append(image)
            }
            return images
        }
    }

    private func downloadAndProcess(_ url: URL) async throws -> UIImage {
        let (data, _) = try await URLSession.shared.data(from: url)
        guard let image = UIImage(data: data) else {
            throw ProcessingError.invalidImage
        }
        return image.resized(to: CGSize(width: 300, height: 300))
    }
}

enum ProcessingError: Error {
    case invalidImage
}
```

### Task Priority

```swift
// Приоритеты задач
Task(priority: .high) {
    // Важная задача
}

Task(priority: .medium) {
    // Обычная задача
}

Task(priority: .low) {
    // Фоновая задача
}

Task(priority: .background) {
    // Некритичная работа
}

// ✅ Производственный пример
func loadCriticalData() {
    Task(priority: .userInitiated) {
        // Высокий приоритет для UI-critical операций
        let userData = try await fetchUser(id: currentUserId)
        await updateUI(with: userData)
    }

    Task(priority: .utility) {
        // Средний приоритет для prefetch
        let recommendations = try await fetchRecommendations()
        await cacheRecommendations(recommendations)
    }
}
```

---

## TaskGroup и Параллельное Выполнение

### withTaskGroup - Динамические Параллельные Задачи

**TaskGroup** позволяет создавать множество параллельных задач и собирать их результаты.

```swift
// ✅ Загрузка множества изображений параллельно
func downloadImages(urls: [URL]) async throws -> [UIImage] {
    try await withThrowingTaskGroup(of: (Int, UIImage).self) { group in
        // Добавляем задачи в группу
        for (index, url) in urls.enumerated() {
            group.addTask {
                let (data, _) = try await URLSession.shared.data(from: url)
                guard let image = UIImage(data: data) else {
                    throw ImageError.invalidData
                }
                return (index, image)
            }
        }

        // Собираем результаты в правильном порядке
        var images: [UIImage?] = Array(repeating: nil, count: urls.count)
        for try await (index, image) in group {
            images[index] = image
        }

        return images.compactMap { $0 }
    }
}

enum ImageError: Error {
    case invalidData
}
```

### ASCII Диаграмма: TaskGroup Execution

```
withTaskGroup параллельное выполнение:

Time →
Main:     [start]--create group--[collect results]--[end]
                   |                    ↑
                   └→ spawns tasks      └─── awaits all

Task 1:            [====fetch URL 1====]────┐
Task 2:            [========fetch URL 2========]─┤
Task 3:            [==fetch URL 3==]──────────────┤
Task 4:            [======fetch URL 4======]──────┤
                                                   │
                   All results collected here ─────┘

Преимущества:
- Все задачи выполняются параллельно
- Автоматическая отмена при ошибке
- Structured concurrency гарантирует завершение всех задач
```

### Производственный Пример: Batch API Requests

```swift
actor APIBatchProcessor {
    struct UserData {
        let profile: UserProfile
        let settings: UserSettings
        let subscriptions: [Subscription]
    }

    func fetchCompleteUserData(userId: String) async throws -> UserData {
        try await withThrowingTaskGroup(of: UserDataComponent.self) { group in
            // Параллельные запросы к разным endpoints
            group.addTask {
                let profile = try await self.fetchProfile(userId: userId)
                return .profile(profile)
            }

            group.addTask {
                let settings = try await self.fetchSettings(userId: userId)
                return .settings(settings)
            }

            group.addTask {
                let subs = try await self.fetchSubscriptions(userId: userId)
                return .subscriptions(subs)
            }

            // Собираем результаты
            var profile: UserProfile?
            var settings: UserSettings?
            var subscriptions: [Subscription]?

            for try await component in group {
                switch component {
                case .profile(let p):
                    profile = p
                case .settings(let s):
                    settings = s
                case .subscriptions(let subs):
                    subscriptions = subs
                }
            }

            guard let profile, let settings, let subscriptions else {
                throw DataError.missingComponents
            }

            return UserData(
                profile: profile,
                settings: settings,
                subscriptions: subscriptions
            )
        }
    }

    private enum UserDataComponent {
        case profile(UserProfile)
        case settings(UserSettings)
        case subscriptions([Subscription])
    }

    private func fetchProfile(userId: String) async throws -> UserProfile {
        // Network request
        fatalError("Implementation needed")
    }

    private func fetchSettings(userId: String) async throws -> UserSettings {
        // Network request
        fatalError("Implementation needed")
    }

    private func fetchSubscriptions(userId: String) async throws -> [Subscription] {
        // Network request
        fatalError("Implementation needed")
    }
}

enum DataError: Error {
    case missingComponents
}

struct UserProfile {}
struct UserSettings {}
struct Subscription {}
```

### withDiscardingTaskGroup - Без Сбора Результатов

```swift
// ✅ Fire-and-forget задачи с отслеживанием завершения
func logAnalyticsEvents(_ events: [AnalyticsEvent]) async {
    await withDiscardingTaskGroup { group in
        for event in events {
            group.addTask {
                await self.sendEventToBackend(event)
            }
        }
        // Ждём завершения всех задач, но результаты не собираем
    }
}
```

---

## Структурированная Конкурентность

### Принципы Structured Concurrency

**Структурированная конкурентность** гарантирует, что:
1. Родительская задача дожидается всех дочерних
2. Отмена родителя отменяет всех детей
3. Ошибка в дочерней задаче может прервать родителя
4. Нет утечек памяти и "висящих" задач

```
Иерархия задач:

Parent Task
├── Child Task 1
│   ├── Grandchild Task 1.1
│   └── Grandchild Task 1.2
├── Child Task 2
└── Child Task 3

Правила:
- Parent завершается только после всех детей
- Parent.cancel() → все дети отменяются
- Ошибка в любом child → может прервать parent
```

### Производственный Пример: Structured Download Manager

```swift
actor DownloadManager {
    func downloadEpisode(_ episode: Episode) async throws -> DownloadedEpisode {
        // Structured concurrency: все задачи завершатся
        try await withThrowingTaskGroup(of: DownloadComponent.self) { group in
            // Параллельная загрузка компонентов
            group.addTask {
                let video = try await self.downloadVideo(episode.videoURL)
                return .video(video)
            }

            group.addTask {
                let audio = try await self.downloadAudio(episode.audioURL)
                return .audio(audio)
            }

            group.addTask {
                let subtitles = try await self.downloadSubtitles(episode.subtitlesURL)
                return .subtitles(subtitles)
            }

            var video: VideoFile?
            var audio: AudioFile?
            var subtitles: SubtitlesFile?

            // Если любая задача упадёт, все остальные отменятся
            for try await component in group {
                switch component {
                case .video(let v): video = v
                case .audio(let a): audio = a
                case .subtitles(let s): subtitles = s
                }
            }

            guard let video, let audio, let subtitles else {
                throw DownloadError.incompleteDownload
            }

            return DownloadedEpisode(
                video: video,
                audio: audio,
                subtitles: subtitles
            )
        }
        // Гарантия: при выходе из withThrowingTaskGroup все задачи завершены
    }

    private enum DownloadComponent {
        case video(VideoFile)
        case audio(AudioFile)
        case subtitles(SubtitlesFile)
    }

    private func downloadVideo(_ url: URL) async throws -> VideoFile {
        let (data, _) = try await URLSession.shared.data(from: url)
        return VideoFile(data: data)
    }

    private func downloadAudio(_ url: URL) async throws -> AudioFile {
        let (data, _) = try await URLSession.shared.data(from: url)
        return AudioFile(data: data)
    }

    private func downloadSubtitles(_ url: URL) async throws -> SubtitlesFile {
        let (data, _) = try await URLSession.shared.data(from: url)
        return SubtitlesFile(data: data)
    }
}

struct Episode {
    let videoURL: URL
    let audioURL: URL
    let subtitlesURL: URL
}

struct DownloadedEpisode {
    let video: VideoFile
    let audio: AudioFile
    let subtitles: SubtitlesFile
}

struct VideoFile { let data: Data }
struct AudioFile { let data: Data }
struct SubtitlesFile { let data: Data }

enum DownloadError: Error {
    case incompleteDownload
}
```

---

## Отмена Задач

### Task.isCancelled и Task.checkCancellation()

```swift
// ✅ Проверка отмены и корректное завершение
func processLargeDataset(_ items: [Item]) async throws -> [ProcessedItem] {
    var results: [ProcessedItem] = []

    for item in items {
        // Проверка отмены перед тяжёлой работой
        try Task.checkCancellation()

        let processed = try await processItem(item)
        results.append(processed)

        // Альтернативная проверка
        if Task.isCancelled {
            throw CancellationError()
        }
    }

    return results
}

// ✅ Производственный пример: Cancellable search
actor SearchManager {
    private var currentSearchTask: Task<[SearchResult], Error>?

    func search(query: String) async throws -> [SearchResult] {
        // Отменяем предыдущий поиск
        currentSearchTask?.cancel()

        let task = Task<[SearchResult], Error> {
            // Debounce
            try await Task.sleep(nanoseconds: 300_000_000) // 300ms
            try Task.checkCancellation()

            // Поиск
            let results = try await performSearch(query: query)
            try Task.checkCancellation()

            return results
        }

        currentSearchTask = task
        return try await task.value
    }

    private func performSearch(query: String) async throws -> [SearchResult] {
        let url = URL(string: "https://api.com/search?q=\(query)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([SearchResult].self, from: data)
    }

    func cancelCurrentSearch() {
        currentSearchTask?.cancel()
    }
}

struct SearchResult: Codable {
    let title: String
}
```

### Отмена с Cleanup

```swift
// ✅ Правильная очистка ресурсов при отмене
func downloadFileWithCleanup(url: URL) async throws -> URL {
    let tempURL = FileManager.default.temporaryDirectory
        .appendingPathComponent(UUID().uuidString)

    do {
        let (localURL, _) = try await URLSession.shared.download(from: url)

        // Проверка отмены перед дорогой операцией
        try Task.checkCancellation()

        try FileManager.default.moveItem(at: localURL, to: tempURL)
        return tempURL
    } catch {
        // Cleanup при ошибке или отмене
        try? FileManager.default.removeItem(at: tempURL)
        throw error
    }
}
```

### ASCII Диаграмма: Task Cancellation

```
Отмена задачи:

Parent Task [start]--cancel()--[cancellation signal]--[cleanup]--[end]
                                      |
                                      ↓
Child Task 1  [running]--checkCancellation()--[throw CancellationError]
Child Task 2  [running]--isCancelled check----[graceful exit]
Child Task 3  [running]--ignores cancel-------[continues] ❌ Bad!

Правильная обработка:
1. Периодически проверять Task.isCancelled
2. Использовать Task.checkCancellation()
3. Очищать ресурсы в catch блоке
4. Не игнорировать CancellationError
```

---

## TaskLocal Значения

### TaskLocal - Контекстные Переменные

**TaskLocal** передаёт значения через всю иерархию задач без явных параметров.

```swift
enum RequestContext {
    @TaskLocal static var requestID: String?
    @TaskLocal static var userID: String?
}

// ✅ Установка TaskLocal значений
func handleRequest() async {
    await RequestContext.$requestID.withValue(UUID().uuidString) {
        await RequestContext.$userID.withValue("user_123") {
            await processRequest()
        }
    }
}

func processRequest() async {
    // Доступ к TaskLocal без параметров
    if let requestID = RequestContext.requestID {
        print("Processing request: \(requestID)")
    }

    await fetchData()
}

func fetchData() async {
    // TaskLocal доступен во всей иерархии
    if let requestID = RequestContext.requestID,
       let userID = RequestContext.userID {
        print("Fetching data for request \(requestID), user \(userID)")
    }
}

// Производственный пример: Logging context
enum LoggingContext {
    @TaskLocal static var correlationID: String?
    @TaskLocal static var feature: String?
}

actor AnalyticsLogger {
    func logEvent(_ event: String, metadata: [String: Any] = [:]) async {
        var enrichedMetadata = metadata

        // Автоматически добавляем контекст из TaskLocal
        if let correlationID = LoggingContext.correlationID {
            enrichedMetadata["correlation_id"] = correlationID
        }

        if let feature = LoggingContext.feature {
            enrichedMetadata["feature"] = feature
        }

        await sendToAnalytics(event: event, metadata: enrichedMetadata)
    }

    private func sendToAnalytics(event: String, metadata: [String: Any]) async {
        // Send to backend
        print("Event: \(event), Metadata: \(metadata)")
    }
}

// Использование
func userLoginFlow() async {
    await LoggingContext.$correlationID.withValue(UUID().uuidString) {
        await LoggingContext.$feature.withValue("authentication") {
            let logger = AnalyticsLogger()
            await logger.logEvent("login_started")
            // correlationID и feature автоматически добавлены

            await performLogin()
            await logger.logEvent("login_completed")
        }
    }
}

func performLogin() async {
    let logger = AnalyticsLogger()
    // Контекст всё ещё доступен
    await logger.logEvent("password_validated")
}
```

---

## Async Let для Параллельной Работы

### async let - Синтаксический Сахар для Параллелизма

**async let** позволяет запускать несколько async операций параллельно с минимальным синтаксисом.

```swift
// ❌ Последовательное выполнение
func loadUserDataSequential(userId: String) async throws -> UserDashboard {
    let profile = try await fetchProfile(userId: userId)      // 300ms
    let posts = try await fetchPosts(userId: userId)          // 400ms
    let friends = try await fetchFriends(userId: userId)      // 350ms

    return UserDashboard(profile: profile, posts: posts, friends: friends)
    // Total: 300 + 400 + 350 = 1050ms
}

// ✅ Параллельное выполнение с async let
func loadUserDataParallel(userId: String) async throws -> UserDashboard {
    async let profile = fetchProfile(userId: userId)          // Starts immediately
    async let posts = fetchPosts(userId: userId)              // Starts immediately
    async let friends = fetchFriends(userId: userId)          // Starts immediately

    // Ждём все результаты параллельно
    let (profileResult, postsResult, friendsResult) = try await (profile, posts, friends)

    return UserDashboard(profile: profileResult, posts: postsResult, friends: friendsResult)
    // Total: max(300, 400, 350) = 400ms
}

struct UserDashboard {
    let profile: UserProfile
    let posts: [Post]
    let friends: [Friend]
}

struct Post {}
struct Friend {}

func fetchProfile(userId: String) async throws -> UserProfile {
    try await Task.sleep(nanoseconds: 300_000_000)
    return UserProfile()
}

func fetchPosts(userId: String) async throws -> [Post] {
    try await Task.sleep(nanoseconds: 400_000_000)
    return []
}

func fetchFriends(userId: String) async throws -> [Friend] {
    try await Task.sleep(nanoseconds: 350_000_000)
    return []
}
```

### ASCII Диаграмма: async let vs Sequential

```
Sequential (1050ms total):
Timeline: |====profile====|====posts====|====friends====|
          0ms            300ms        700ms           1050ms

async let (400ms total):
Timeline: |====profile====|
          |====posts=========|
          |====friends======|
          0ms              400ms

Speedup: 1050ms / 400ms = 2.6x faster
```

### Производственный Пример: Dashboard с async let

```swift
@MainActor
class DashboardViewModel: ObservableObject {
    @Published var dashboard: Dashboard?
    @Published var isLoading = false
    @Published var error: Error?

    private let api: APIClient

    init(api: APIClient) {
        self.api = api
    }

    func loadDashboard(userId: String) async {
        isLoading = true
        defer { isLoading = false }

        do {
            // Параллельная загрузка всех секций
            async let userStats = api.fetchUserStats(userId: userId)
            async let recentActivity = api.fetchRecentActivity(userId: userId)
            async let recommendations = api.fetchRecommendations(userId: userId)
            async let notifications = api.fetchNotifications(userId: userId)

            // Ждём все результаты
            let (stats, activity, recs, notifs) = try await (
                userStats,
                recentActivity,
                recommendations,
                notifications
            )

            self.dashboard = Dashboard(
                stats: stats,
                activity: activity,
                recommendations: recs,
                notifications: notifs
            )
        } catch {
            self.error = error
        }
    }
}

struct Dashboard {
    let stats: UserStats
    let activity: [Activity]
    let recommendations: [Recommendation]
    let notifications: [Notification]
}

struct UserStats {}
struct Activity {}
struct Recommendation {}
struct Notification {}

actor APIClient {
    func fetchUserStats(userId: String) async throws -> UserStats {
        // Network request
        UserStats()
    }

    func fetchRecentActivity(userId: String) async throws -> [Activity] {
        []
    }

    func fetchRecommendations(userId: String) async throws -> [Recommendation] {
        []
    }

    func fetchNotifications(userId: String) async throws -> [Notification] {
        []
    }
}
```

---

## Actors и Изоляция

### Actor - Безопасная Конкурентность для Mutable State

**Actor** — это reference type, который защищает свой mutable state от data races через автоматическую изоляцию.

```swift
// ❌ Data race с обычным class
class CounterUnsafe {
    private var count = 0

    func increment() {
        count += 1  // ❌ Data race если вызывается с разных потоков
    }

    func getCount() -> Int {
        count  // ❌ Data race при чтении
    }
}

// ✅ Thread-safe с actor
actor CounterSafe {
    private var count = 0

    func increment() {
        count += 1  // ✅ Защищено actor isolation
    }

    func getCount() -> Int {
        count  // ✅ Безопасное чтение
    }
}

// Использование
func testCounter() async {
    let counter = CounterSafe()

    // Actor методы требуют await
    await counter.increment()
    let value = await counter.getCount()
    print(value)
}
```

### ASCII Диаграмма: Actor Isolation

```
Actor Serialization:

Thread 1: [call increment()]--await--[queued]--[executes]--[done]
Thread 2:                     [call getCount()]--await--[queued]--[executes]
Thread 3:                                       [call increment()]--await--[executes]

Actor's Internal Queue:
[increment()] → [getCount()] → [increment()]

Гарантии:
- Только один метод выполняется одновременно
- Нет data races
- Автоматическая serialization
- Мутации безопасны
```

### Производственный Пример: Thread-Safe Cache

```swift
actor ImageCache {
    private var cache: [String: CachedImage] = [:]
    private let maxSize: Int
    private var currentSize: Int = 0

    init(maxSize: Int = 100) {
        self.maxSize = maxSize
    }

    func image(for key: String) -> UIImage? {
        cache[key]?.image
    }

    func setImage(_ image: UIImage, for key: String) {
        let size = estimatedSize(of: image)

        // Проверяем лимит
        while currentSize + size > maxSize && !cache.isEmpty {
            evictOldest()
        }

        cache[key] = CachedImage(
            image: image,
            timestamp: Date(),
            size: size
        )
        currentSize += size
    }

    func removeImage(for key: String) {
        if let cached = cache.removeValue(forKey: key) {
            currentSize -= cached.size
        }
    }

    func clear() {
        cache.removeAll()
        currentSize = 0
    }

    private func evictOldest() {
        guard let oldest = cache.min(by: { $0.value.timestamp < $1.value.timestamp }) else {
            return
        }

        cache.removeValue(forKey: oldest.key)
        currentSize -= oldest.value.size
    }

    private func estimatedSize(of image: UIImage) -> Int {
        Int(image.size.width * image.size.height * 4) // RGBA bytes
    }

    private struct CachedImage {
        let image: UIImage
        let timestamp: Date
        let size: Int
    }
}

// Использование в ViewModel
@MainActor
class ImageGalleryViewModel: ObservableObject {
    @Published var images: [String: UIImage] = [:]

    private let cache = ImageCache()
    private let loader: ImageLoader

    init(loader: ImageLoader) {
        self.loader = loader
    }

    func loadImage(for url: String) async {
        // Проверяем кэш
        if let cached = await cache.image(for: url) {
            images[url] = cached
            return
        }

        // Загружаем
        do {
            let image = try await loader.load(from: url)

            // Сохраняем в кэш
            await cache.setImage(image, for: url)

            // Обновляем UI
            images[url] = image
        } catch {
            print("Failed to load image: \(error)")
        }
    }
}

actor ImageLoader {
    func load(from urlString: String) async throws -> UIImage {
        let url = URL(string: urlString)!
        let (data, _) = try await URLSession.shared.data(from: url)
        guard let image = UIImage(data: data) else {
            throw LoaderError.invalidImage
        }
        return image
    }
}

enum LoaderError: Error {
    case invalidImage
}
```

### nonisolated и Actor Isolation Control

```swift
actor DataProcessor {
    private var data: [String] = []

    // Actor-isolated (требует await)
    func addData(_ item: String) {
        data.append(item)
    }

    // nonisolated - синхронный доступ
    nonisolated func formatData(_ item: String) -> String {
        // ❌ Нет доступа к actor state
        // data.append(item)  // Compilation error

        // ✅ Только чистые вычисления
        return item.uppercased()
    }

    // nonisolated для констант
    nonisolated let processorID: String = UUID().uuidString
}
```

---

## MainActor для UI Обновлений

### @MainActor - Гарантированное Выполнение на Main Thread

**@MainActor** — это глобальный actor, который гарантирует выполнение на главном потоке. Критично для UI обновлений в iOS.

```swift
// ❌ UI обновление на фоновом потоке - CRASH!
func updateUIUnsafe() {
    Task {
        let data = try await fetchData()
        self.label.text = data  // ❌ UIKit crash: UI на фоновом потоке
    }
}

// ✅ Правильное UI обновление с MainActor
func updateUISafe() {
    Task {
        let data = try await fetchData()

        await MainActor.run {
            self.label.text = data  // ✅ Гарантированно на main thread
        }
    }
}

// ✅ Ещё лучше: @MainActor на весь класс
@MainActor
class ViewController: UIViewController {
    private var label: UILabel!

    func loadData() async {
        let data = try? await fetchData()

        // ✅ Автоматически на main thread
        label.text = data
    }
}

func fetchData() async throws -> String {
    ""
}
```

### SwiftUI и @MainActor

```swift
// ✅ SwiftUI ViewModel с @MainActor
@MainActor
class ArticleViewModel: ObservableObject {
    @Published var articles: [Article] = []
    @Published var isLoading = false
    @Published var error: Error?

    private let repository: ArticleRepository

    init(repository: ArticleRepository) {
        self.repository = repository
    }

    func loadArticles() async {
        isLoading = true

        do {
            // Загрузка на фоне
            let fetchedArticles = try await repository.fetchArticles()

            // Обновление UI - автоматически на main thread
            self.articles = fetchedArticles
            self.isLoading = false
        } catch {
            self.error = error
            self.isLoading = false
        }
    }

    func refreshArticles() async {
        await loadArticles()
    }
}

// SwiftUI View
struct ArticlesView: View {
    @StateObject private var viewModel: ArticleViewModel

    var body: some View {
        List(viewModel.articles) { article in
            ArticleRow(article: article)
        }
        .task {
            // ✅ async работа в SwiftUI
            await viewModel.loadArticles()
        }
        .refreshable {
            await viewModel.refreshArticles()
        }
    }
}

struct Article: Identifiable {
    let id: String
    let title: String
}

struct ArticleRow: View {
    let article: Article

    var body: some View {
        Text(article.title)
    }
}

actor ArticleRepository {
    func fetchArticles() async throws -> [Article] {
        let url = URL(string: "https://api.com/articles")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([Article].self, from: data)
    }
}
```

### Производственный Пример: Image Loading с MainActor

```swift
@MainActor
class AsyncImageView: UIView {
    private let imageView = UIImageView()
    private let activityIndicator = UIActivityIndicatorView(style: .medium)
    private var currentTask: Task<Void, Never>?

    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }

    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }

    private func setupUI() {
        imageView.contentMode = .scaleAspectFill
        imageView.clipsToBounds = true

        addSubview(imageView)
        addSubview(activityIndicator)

        imageView.frame = bounds
        imageView.autoresizingMask = [.flexibleWidth, .flexibleHeight]

        activityIndicator.center = CGPoint(x: bounds.midX, y: bounds.midY)
        activityIndicator.autoresizingMask = [.flexibleLeftMargin, .flexibleRightMargin,
                                              .flexibleTopMargin, .flexibleBottomMargin]
    }

    func loadImage(from url: URL) {
        // Отменяем предыдущую загрузку
        currentTask?.cancel()

        imageView.image = nil
        activityIndicator.startAnimating()

        currentTask = Task {
            do {
                // Фоновая загрузка
                let (data, _) = try await URLSession.shared.data(from: url)

                // Проверка отмены
                try Task.checkCancellation()

                guard let image = UIImage(data: data) else {
                    throw ImageLoadError.invalidData
                }

                // UI обновление - автоматически на main thread благодаря @MainActor
                self.imageView.image = image
                self.activityIndicator.stopAnimating()
            } catch is CancellationError {
                // Загрузка отменена - ничего не делаем
            } catch {
                // Обработка ошибки на main thread
                self.activityIndicator.stopAnimating()
                self.showErrorPlaceholder()
            }
        }
    }

    private func showErrorPlaceholder() {
        imageView.image = UIImage(systemName: "exclamationmark.triangle")
        imageView.tintColor = .systemRed
    }

    enum ImageLoadError: Error {
        case invalidData
    }
}
```

### ASCII Диаграмма: MainActor Execution

```
Without @MainActor:
Task:      [fetch data]--[process]--[❌ UI update on background thread] CRASH!
Thread:    Background   Background   Background

With @MainActor:
Task:      [fetch data]--[process]--await MainActor--[✅ UI update]
Thread:    Background   Background                   Main Thread

With @MainActor on class:
Task:      [fetch data (background)]--[✅ automatic main thread for all methods]
Thread:    Background                 Main Thread (automatic)
```

---

## AsyncSequence и AsyncStream

### AsyncSequence - Асинхронная Последовательность

**AsyncSequence** — это протокол для асинхронной итерации по значениям.

```swift
// ✅ Использование AsyncSequence
func processLines(from url: URL) async throws {
    let (bytes, _) = try await URLSession.shared.bytes(from: url)

    // AsyncSequence позволяет итерацию с await
    for try await line in bytes.lines {
        print(line)
    }
}

// Производственный пример: Real-time data stream
actor DataStreamProcessor {
    func processRealtimeData(from url: URL) async throws {
        let (bytes, _) = try await URLSession.shared.bytes(from: url)

        var buffer: [String] = []

        for try await line in bytes.lines {
            buffer.append(line)

            // Обрабатываем батчами по 100
            if buffer.count >= 100 {
                await processBatch(buffer)
                buffer.removeAll()
            }

            // Проверка отмены
            try Task.checkCancellation()
        }

        // Обрабатываем остатки
        if !buffer.isEmpty {
            await processBatch(buffer)
        }
    }

    private func processBatch(_ lines: [String]) async {
        print("Processing batch of \(lines.count) lines")
        // Обработка батча
    }
}
```

### AsyncStream - Создание Собственных Потоков

**AsyncStream** позволяет создавать custom асинхронные последовательности.

```swift
// ✅ AsyncStream для WebSocket сообщений
class WebSocketManager {
    func messageStream() -> AsyncStream<String> {
        AsyncStream { continuation in
            let task = URLSession.shared.webSocketTask(
                with: URL(string: "wss://api.example.com/ws")!
            )

            // Обработка сообщений
            Task {
                do {
                    while true {
                        let message = try await task.receive()

                        switch message {
                        case .string(let text):
                            continuation.yield(text)
                        case .data(let data):
                            if let text = String(data: data, encoding: .utf8) {
                                continuation.yield(text)
                            }
                        @unknown default:
                            break
                        }
                    }
                } catch {
                    continuation.finish()
                }
            }

            task.resume()

            // Cleanup при отмене
            continuation.onTermination = { _ in
                task.cancel()
            }
        }
    }
}

// Использование
func subscribeToWebSocket() async {
    let manager = WebSocketManager()

    for await message in manager.messageStream() {
        print("Received: \(message)")

        // Можно прервать в любой момент
        if message == "STOP" {
            break
        }
    }
}
```

### Производственный Пример: Location Updates Stream

```swift
import CoreLocation

@MainActor
class LocationStream: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private var continuation: AsyncStream<CLLocation>.Continuation?

    func locationUpdates() -> AsyncStream<CLLocation> {
        AsyncStream { continuation in
            self.continuation = continuation

            manager.delegate = self
            manager.requestWhenInUseAuthorization()
            manager.startUpdatingLocation()

            continuation.onTermination = { [weak self] _ in
                self?.manager.stopUpdatingLocation()
            }
        }
    }

    nonisolated func locationManager(
        _ manager: CLLocationManager,
        didUpdateLocations locations: [CLLocation]
    ) {
        Task { @MainActor in
            for location in locations {
                continuation?.yield(location)
            }
        }
    }

    nonisolated func locationManager(
        _ manager: CLLocationManager,
        didFailWithError error: Error
    ) {
        Task { @MainActor in
            continuation?.finish()
        }
    }
}

// Использование в SwiftUI
@MainActor
class LocationViewModel: ObservableObject {
    @Published var currentLocation: CLLocation?
    @Published var locationHistory: [CLLocation] = []

    private let locationStream = LocationStream()

    func startTracking() async {
        for await location in locationStream.locationUpdates() {
            currentLocation = location
            locationHistory.append(location)

            // Ограничиваем историю
            if locationHistory.count > 100 {
                locationHistory.removeFirst()
            }
        }
    }
}
```

### AsyncThrowingStream для Error Handling

```swift
// ✅ AsyncThrowingStream с обработкой ошибок
actor NetworkEventStream {
    enum NetworkEvent {
        case connected
        case disconnected
        case dataReceived(Data)
        case error(Error)
    }

    func eventStream() -> AsyncThrowingStream<NetworkEvent, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    // Подключение
                    try await connect()
                    continuation.yield(.connected)

                    // Получение данных
                    while true {
                        let data = try await receiveData()
                        continuation.yield(.dataReceived(data))
                    }
                } catch {
                    continuation.yield(.error(error))
                    continuation.finish(throwing: error)
                }
            }
        }
    }

    private func connect() async throws {
        // Connection logic
    }

    private func receiveData() async throws -> Data {
        // Data receiving logic
        Data()
    }
}

// Использование
func handleNetworkEvents() async {
    let stream = NetworkEventStream()

    do {
        for try await event in stream.eventStream() {
            switch event {
            case .connected:
                print("Connected")
            case .disconnected:
                print("Disconnected")
            case .dataReceived(let data):
                print("Received \(data.count) bytes")
            case .error(let error):
                print("Error: \(error)")
            }
        }
    } catch {
        print("Stream failed: \(error)")
    }
}
```

---

## Swift 6.2 Approachable Concurrency

### Новые Возможности Swift 6.2

Swift 6.2 вводит **Approachable Concurrency** — упрощённую модель для начинающих с более понятными error messages и warnings.

```swift
// Swift 6.2: Улучшенные диагностики

// ❌ До Swift 6.2: Запутанная ошибка
class DataManager {
    var data: [String] = []

    func addData(_ item: String) {
        data.append(item)  // Error: data race possible
    }
}

// ✅ Swift 6.2: Понятное предложение
// Error: 'data' is not thread-safe
// Fix: Consider using 'actor' instead of 'class'

actor DataManagerSafe {
    private var data: [String] = []

    func addData(_ item: String) {
        data.append(item)  // ✅ Thread-safe
    }
}
```

### @Sendable и Sendable Protocol

**Sendable** гарантирует, что тип безопасен для передачи между конкурентными контекстами.

```swift
// ✅ Sendable struct - безопасно
struct User: Sendable {
    let id: String
    let name: String
}

// ❌ Non-Sendable class - может быть опасно
class UserProfile {
    var name: String

    init(name: String) {
        self.name = name
    }
}

// ✅ Sendable class с immutable state
final class ImmutableUserProfile: Sendable {
    let name: String

    init(name: String) {
        self.name = name
    }
}

// Производственный пример
actor UserRepository {
    private var cache: [String: User] = [:]

    // ✅ User is Sendable - безопасно возвращать
    func getUser(id: String) async -> User? {
        cache[id]
    }

    func setUser(_ user: User) async {
        cache[user.id] = user
    }
}

// ❌ Опасно с non-Sendable
actor ProfileRepository {
    private var cache: [String: UserProfile] = [:]

    // ⚠️ Warning в Swift 6.2: UserProfile is not Sendable
    func getProfile(id: String) async -> UserProfile? {
        cache[id]
    }
}
```

### @preconcurrency для Legacy Code

```swift
// Legacy library без Sendable
@preconcurrency import OldNetworkLibrary

// ✅ Подавляем warnings для legacy code
actor LegacyAPIWrapper {
    @preconcurrency
    func fetchData() async throws -> LegacyDataModel {
        try await OldNetworkLibrary.fetch()
    }
}
```

---

## Интеграция с Combine

### Мост между Async/Await и Combine

```swift
import Combine

// ✅ Combine → Async/Await
extension Publisher {
    func asyncValue() async throws -> Output {
        try await withCheckedThrowingContinuation { continuation in
            var cancellable: AnyCancellable?

            cancellable = first()
                .sink(
                    receiveCompletion: { completion in
                        switch completion {
                        case .finished:
                            break
                        case .failure(let error):
                            continuation.resume(throwing: error)
                        }
                        cancellable?.cancel()
                    },
                    receiveValue: { value in
                        continuation.resume(returning: value)
                    }
                )
        }
    }
}

// Использование
func fetchUserWithCombine() async throws -> User {
    let publisher = URLSession.shared
        .dataTaskPublisher(for: URL(string: "https://api.com/user")!)
        .map(\.data)
        .decode(type: User.self, decorator: JSONDecoder())
        .eraseToAnyPublisher()

    return try await publisher.asyncValue()
}

// ✅ Async/Await → Combine
actor DataService {
    func fetchData() async throws -> Data {
        let url = URL(string: "https://api.com/data")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return data
    }
}

extension DataService {
    func fetchDataPublisher() -> AnyPublisher<Data, Error> {
        Future { promise in
            Task {
                do {
                    let data = try await self.fetchData()
                    promise(.success(data))
                } catch {
                    promise(.failure(error))
                }
            }
        }
        .eraseToAnyPublisher()
    }
}
```

### Производственный Пример: Hybrid Architecture

```swift
@MainActor
class HybridViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false

    private let repository: UserRepository
    private var cancellables = Set<AnyCancellable>()

    init(repository: UserRepository) {
        self.repository = repository
    }

    // Combine-based search (для reactive UI)
    func setupSearch(_ searchText: Published<String>.Publisher) {
        searchText
            .debounce(for: 0.3, scheduler: DispatchQueue.main)
            .removeDuplicates()
            .sink { [weak self] query in
                guard let self = self else { return }
                Task {
                    await self.performSearch(query: query)
                }
            }
            .store(in: &cancellables)
    }

    // Async/await для бизнес-логики
    private func performSearch(query: String) async {
        guard !query.isEmpty else {
            users = []
            return
        }

        isLoading = true
        defer { isLoading = false }

        do {
            let results = try await repository.searchUsers(query: query)
            users = results
        } catch {
            print("Search failed: \(error)")
            users = []
        }
    }
}

actor UserRepository {
    func searchUsers(query: String) async throws -> [User] {
        let url = URL(string: "https://api.com/users/search?q=\(query)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([User].self, from: data)
    }
}
```

---

## Сравнение с Kotlin Coroutines

### Swift Async/Await vs Kotlin Coroutines

См. также: [[kotlin-coroutines]]

```
┌─────────────────────┬──────────────────────────┬───────────────────────────┐
│ Концепция           │ Swift                    │ Kotlin                    │
├─────────────────────┼──────────────────────────┼───────────────────────────┤
│ Async функция       │ async func               │ suspend fun               │
│ Ожидание            │ await                    │ await (для Deferred)      │
│ Контекст            │ Task                     │ CoroutineScope            │
│ Запуск              │ Task {}                  │ launch {}                 │
│ Возврат значения    │ Task<T, Error>           │ async { }                 │
│ Изоляция            │ Actor                    │ Mutex, Synchronized       │
│ Main thread         │ @MainActor               │ Dispatchers.Main          │
│ Background          │ Task.detached            │ Dispatchers.IO            │
│ Отмена              │ Task.cancel()            │ Job.cancel()              │
│ Параллелизм         │ async let, TaskGroup     │ async {}, coroutineScope  │
│ Последовательности  │ AsyncSequence            │ Flow                      │
│ Structured          │ withTaskGroup            │ coroutineScope            │
└─────────────────────┴──────────────────────────┴───────────────────────────┘
```

### Примеры кода: Swift vs Kotlin

```swift
// Swift: Параллельная загрузка
func loadData() async throws -> (User, [Post]) {
    async let user = fetchUser()
    async let posts = fetchPosts()

    return try await (user, posts)
}

// Kotlin эквивалент:
// suspend fun loadData(): Pair<User, List<Post>> = coroutineScope {
//     val user = async { fetchUser() }
//     val posts = async { fetchPosts() }
//
//     Pair(user.await(), posts.await())
// }
```

```swift
// Swift: Actor для thread-safety
actor Counter {
    private var value = 0

    func increment() {
        value += 1
    }

    func getValue() -> Int {
        value
    }
}

// Kotlin эквивалент:
// class Counter {
//     private val mutex = Mutex()
//     private var value = 0
//
//     suspend fun increment() = mutex.withLock {
//         value++
//     }
//
//     suspend fun getValue() = mutex.withLock {
//         value
//     }
// }
```

```swift
// Swift: AsyncStream
func numberStream() -> AsyncStream<Int> {
    AsyncStream { continuation in
        Task {
            for i in 1...10 {
                try? await Task.sleep(nanoseconds: 100_000_000)
                continuation.yield(i)
            }
            continuation.finish()
        }
    }
}

// Kotlin эквивалент:
// fun numberFlow() = flow {
//     for (i in 1..10) {
//         delay(100)
//         emit(i)
//     }
// }
```

### Ключевые Различия

| Аспект | Swift | Kotlin |
|--------|-------|--------|
| **Type Safety** | Strict concurrency в Swift 6 | Менее строгая проверка |
| **UI Thread** | @MainActor (автоматически) | Dispatchers.Main (явно) |
| **Data Races** | Compiler ошибки | Runtime Mutex |
| **Actor Model** | Встроенные actors | Ручная синхронизация |
| **Cancellation** | Structured (автоматически) | Requires Job management |
| **Learning Curve** | Проще благодаря compiler | Больше boilerplate |

---

## Типичные Ошибки

### 1. Blocking Main Thread

```swift
// ❌ Блокировка main thread
@MainActor
class BadViewModel: ObservableObject {
    func loadData() {
        // ❌ Синхронный тяжёлый код на main thread
        let data = performHeavyComputation()  // UI зависает!
        updateUI(with: data)
    }

    private func performHeavyComputation() -> Data {
        // Долгая операция
        Data()
    }

    private func updateUI(with data: Data) {
        // UI update
    }
}

// ✅ Правильно: async работа
@MainActor
class GoodViewModel: ObservableObject {
    func loadData() async {
        // ✅ Тяжёлая работа на фоне
        let data = await Task.detached {
            self.performHeavyComputation()
        }.value

        // UI обновление на main thread
        updateUI(with: data)
    }

    private func performHeavyComputation() -> Data {
        Data()
    }

    private func updateUI(with data: Data) {
        // UI update
    }
}
```

### 2. Забытый await для async let

```swift
// ❌ Забыли await - компиляция не пройдёт
func loadUsers() async throws -> [User] {
    async let users = fetchUsers()

    // ❌ Error: missing await
    return users  // Compilation error!
}

// ✅ Правильно
func loadUsers() async throws -> [User] {
    async let users = fetchUsers()
    return try await users  // ✅
}

func fetchUsers() async throws -> [User] {
    []
}
```

### 3. Data Race с Class вместо Actor

```swift
// ❌ Data race с class
class UnsafeCache {
    private var cache: [String: Data] = [:]

    func set(_ data: Data, for key: String) {
        cache[key] = data  // ❌ Data race!
    }

    func get(_ key: String) -> Data? {
        cache[key]  // ❌ Data race!
    }
}

// ✅ Thread-safe с actor
actor SafeCache {
    private var cache: [String: Data] = [:]

    func set(_ data: Data, for key: String) {
        cache[key] = data  // ✅ Protected by actor
    }

    func get(_ key: String) -> Data? {
        cache[key]  // ✅ Protected by actor
    }
}
```

### 4. Неправильная Обработка Отмены

```swift
// ❌ Игнорирование отмены
func processItems(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []

    for item in items {
        // ❌ Не проверяем отмену - может работать вечно
        let result = try await processItem(item)
        results.append(result)
    }

    return results
}

// ✅ Правильная обработка отмены
func processItems(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []

    for item in items {
        // ✅ Проверяем отмену
        try Task.checkCancellation()

        let result = try await processItem(item)
        results.append(result)
    }

    return results
}

struct Item {}
struct Result {}

func processItem(_ item: Item) async throws -> Result {
    Result()
}
```

### 5. Detached Task Наследует Контекст

```swift
// ❌ Task {} наследует @MainActor
@MainActor
class ViewController: UIViewController {
    func loadLargeFile() {
        Task {
            // ❌ Всё ещё на MainActor - UI зависнет!
            let data = parseHugeJSON()
        }
    }

    private func parseHugeJSON() -> Data {
        Data()
    }
}

// ✅ Task.detached для фоновой работы
@MainActor
class ViewController2: UIViewController {
    func loadLargeFile() {
        Task.detached {
            // ✅ На фоновом потоке
            let data = self.parseHugeJSON()

            await MainActor.run {
                // UI обновление на main thread
                self.updateUI(with: data)
            }
        }
    }

    private func parseHugeJSON() -> Data {
        Data()
    }

    private func updateUI(with data: Data) {
        // UI update
    }
}
```

### 6. Двойной Resume в Continuation

```swift
// ❌ Двойной resume - crash!
func badContinuation() async -> String {
    await withCheckedContinuation { continuation in
        DispatchQueue.main.async {
            continuation.resume(returning: "First")
            continuation.resume(returning: "Second")  // ❌ CRASH!
        }
    }
}

// ✅ Правильно: resume только один раз
func goodContinuation() async -> String {
    await withCheckedContinuation { continuation in
        var hasResumed = false

        DispatchQueue.main.async {
            guard !hasResumed else { return }
            hasResumed = true
            continuation.resume(returning: "Success")
        }
    }
}

// ✅ Ещё лучше: используйте встроенные async API
func bestApproach() async throws -> String {
    try await withCheckedThrowingContinuation { continuation in
        URLSession.shared.dataTask(with: URL(string: "https://api.com")!) { data, response, error in
            if let error = error {
                continuation.resume(throwing: error)
            } else if let data = data {
                continuation.resume(returning: String(data: data, encoding: .utf8) ?? "")
            }
        }.resume()
    }
}
```

---

## Заключение

Swift async/await революционизирует конкурентное программирование на iOS:

1. **Линейный код** вместо callback hell
2. **Compiler safety** для предотвращения data races
3. **Structured concurrency** гарантирует правильное управление задачами
4. **Actors** обеспечивают thread-safety без ручных locks
5. **@MainActor** упрощает UI обновления
6. **AsyncSequence** для работы с потоками данных
7. **Swift 6.2** делает конкурентность доступнее

**Главное правило**: используйте async/await для всех асинхронных операций, actors для mutable state, и @MainActor для UI кода.

## Связь с другими темами

**[[ios-threading-fundamentals]]** — Threading fundamentals (GCD, OperationQueue, Thread) являются обязательным prerequisite для понимания async/await, поскольку Swift Concurrency построен поверх cooperative thread pool. Знание того, как работают dispatch queues и QoS classes, объясняет, почему async/await эффективнее: вместо блокирования потоков используются suspension points, позволяющие одному потоку обслуживать множество задач. Рекомендуется изучить threading fundamentals, затем перейти к async/await как к более высокоуровневой абстракции.

**[[ios-gcd-deep-dive]]** — GCD (Grand Central Dispatch) остаётся основой, на которой работает Swift Concurrency runtime. Понимание dispatch queues, sync/async, serial/concurrent помогает осознать, почему MainActor привязан к main queue и как cooperative thread pool отличается от GCD thread pool. Изучение GCD перед async/await создаёт прочную базу, а сравнение двух подходов углубляет понимание обоих.

**[[ios-combine]]** — Combine и async/await решают смежные задачи (асинхронная обработка данных), но с разными подходами: Combine предоставляет реактивные потоки данных с операторами (map, filter, combineLatest), тогда как async/await предлагает линейный императивный стиль. AsyncSequence частично заменяет Combine Publishers, но Combine остаётся предпочтительным для сложных реактивных UI-биндингов. Рекомендуется изучить оба подхода и комбинировать их в зависимости от задачи.

**[[ios-concurrency-mistakes]]** — Типичные ошибки конкурентности (data races, deadlocks, UI updates с фонового потока) остаются актуальными и при использовании async/await, хотя Swift 6 Strict Concurrency ловит многие из них на этапе компиляции. Изучение антипаттернов после освоения async/await помогает писать безопасный concurrent код и понимать, какие проблемы решает compiler, а какие остаются на ответственности разработчика.

## Источники и дальнейшее чтение

- Eidhof C. et al. (2019). *Advanced Swift.* — продвинутые паттерны Swift, включая generics и protocol-oriented design, которые активно используются в Swift Concurrency (AsyncSequence, Sendable)
- Sundell J. (2022). *Swift by Sundell.* — практические примеры использования async/await, actors и structured concurrency в реальных проектах
- Apple (2023). *The Swift Programming Language.* — официальная глава по Concurrency, описывающая async/await, actors, structured concurrency и Sendable protocol

---

**Дата создания**: 2026-01-11
**Последнее обновление**: 2026-01-11
**Версия Swift**: 6.2
**iOS Target**: iOS 18+
