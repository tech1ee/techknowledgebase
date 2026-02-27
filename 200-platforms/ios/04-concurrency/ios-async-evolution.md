---
title: "Эволюция асинхронности в iOS"
created: 2026-01-11
modified: 2026-02-13
type: overview
reading_time: 51
difficulty: 4
study_status: not_started
mastery: 0
last_reviewed:
next_review:
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/concurrency
  - type/overview
  - level/intermediate
related:
  - "[[android-async-evolution]]"
  - "[[kotlin-coroutines]]"
  - "[[ios-async-await]]"
  - "[[ios-gcd-deep-dive]]"
---

# Эволюция асинхронности в iOS

## TL;DR

История асинхронного программирования в iOS — это путь от ручного управления потоками (NSThread, 2007) через революционный Grand Central Dispatch (2009) к современному async/await (2021). GCD остается фундаментом, но async/await делает код линейным и безопасным. Swift 6 (2024) добавил строгую проверку конкурентности на этапе компиляции, а Approachable Concurrency (2025) упростила вход для новичков.

**Аналогия**: Если NSThread — это ручная коробка передач с двойным сцеплением, то GCD — автомат, async/await — Tesla на автопилоте, а Swift 6 — система предупреждения о столкновениях.

## Теоретические основы

> **Определение:** Асинхронное программирование — парадигма, в которой операция инициируется, но её результат обрабатывается позже через callback, promise или continuation, позволяя потоку выполнения не блокироваться в ожидании. Формализовано в модели Communicating Sequential Processes (Hoare, 1978).

### Теоретические модели конкурентности

| Модель | Автор | Год | Реализация в iOS |
|--------|-------|-----|-----------------|
| Communicating Sequential Processes (CSP) | C. A. R. Hoare | 1978 | Channels (неявно в GCD) |
| Actor Model | Carl Hewitt | 1973 | Swift actors (iOS 15+) |
| Futures / Promises | Baker & Hewitt | 1977 | Combine, async/await |
| Structured Concurrency | Martin Sústrik (libdill) | 2016 | Swift TaskGroup, async let |
| Cooperative Multitasking | — (исторически) | — | Swift async/await (suspension points) |

> **Structured Concurrency (Elizarov et al., 2019):** Принцип, согласно которому конкурентные операции образуют иерархию: дочерняя задача не может пережить родительскую. Это устраняет проблему «огненных» задач (fire-and-forget) и утечки ресурсов. Реализован в Swift через `Task`, `TaskGroup`, `async let`.

### Эволюция как смена уровней абстракции

| Эпоха | Абстракция | Проблемы предыдущей эпохи | Решение |
|-------|-----------|--------------------------|---------|
| NSThread (2007) | Потоки | Отсутствие абстракций | Прямое управление pthreads |
| GCD (2009) | Очереди задач | Race conditions, deadlocks, boilerplate | Thread pool + work-stealing |
| Promises (2017) | Цепочки значений | Callback hell, pyramid of doom | Линейная цепочка .then/.catch |
| async/await (2021) | Suspension points | Ошибки в цепочках, memory leaks | Линейный код, structured concurrency |
| Swift 6 (2024) | Compile-time safety | Runtime data races | Статический анализ @Sendable, actor isolation |

### Связь с CS-фундаментом

- [[concurrency-fundamentals]] — теоретические модели конкурентности (CSP, Actor Model)
- [[ios-threading-fundamentals]] — GCD как практическая основа
- [[kotlin-coroutines]] — аналогичная эволюция в Kotlin (Coroutines = structured concurrency)

---

## Теоретические основы

> **Определение:** Асинхронное программирование — модель выполнения, при которой операции инициируются без блокировки вызывающего потока, а результат доставляется через callback, promise/future или suspension point. Формализовано в работах Friedman & Wise (1976) по futures и Liskov & Shrira (1988) по promises.

### Теоретическая классификация моделей асинхронности

| Модель | Теоретическая основа | Реализация в iOS | Эпоха |
|--------|---------------------|-----------------|-------|
| **Threads** | Dijkstra (1965), POSIX threads | NSThread, pthread | 2007-2009 |
| **Event Loop** | Reactor pattern (Schmidt, 1995) | RunLoop, CFRunLoop | 2007-н.в. |
| **Task Queues** | Work-stealing (Blumofe & Leiserson, 1999) | GCD / libdispatch | 2009-н.в. |
| **Operations** | Command pattern (GoF, 1994) | NSOperation, OperationQueue | 2010-н.в. |
| **Futures/Promises** | Friedman & Wise (1976) | PromiseKit, Combine | 2017-2019 |
| **Structured Concurrency** | Sutter (2005), Kotlin (2018) | Swift async/await, TaskGroup | 2021-н.в. |
| **Actor Model** | Hewitt et al. (1973, MIT) | Swift actors, @MainActor | 2021-н.в. |

> **Structured Concurrency (Elizarov, 2018):** Принцип, согласно которому каждая асинхронная операция имеет определённый scope (область жизни) и не может пережить своего родителя. Гарантирует отсутствие «orphaned tasks» и упрощает отмену/обработку ошибок.

### Actor Model

> **Actor Model (Hewitt, Bishop & Steiger, 1973):** Модель вычислений, где actor — это примитив параллелизма, который: (1) получает сообщения, (2) создаёт новых actors, (3) отправляет сообщения, (4) определяет поведение для следующего сообщения. В Swift actors реализуют *serial execution* всех обращений к своему состоянию.

### Связь с CS-фундаментом

- [[concurrency-fundamentals]] — теория параллелизма и модели синхронизации
- [[ios-threading-fundamentals]] — практика GCD и threading в iOS
- [[kotlin-coroutines]] — сравнение с Kotlin Coroutines (structured concurrency, suspend functions)

---

## Временная линия эволюции

```
2007            2009         2010              2014        2017           2021              2024           2025
│               │            │                 │           │              │                 │              │
NSThread        GCD          NSOperation       Swift 1.0   Promises       async/await       Swift 6        Approachable
(ручное         (очереди     (высокий          (GCD в      (3rd party)    (структур.        (строгая       Concurrency
управление)     и блоки)     уровень)          Swift)                     конкурентность)   проверка)      (упрощение)
│               │            │                 │           │              │                 │              │
▼               ▼            ▼                 ▼           ▼              ▼                 ▼              ▼
pthread_create  dispatch_    NSOperationQueue  DispatchQ.  PromiseKit     Task {           @Sendable      async let
Thread.detach   async()      addDependency     async {}    .then {}       await fetch()    actor          parallel
@synchronized   DispatchQ.   maxConcurrent     semaphore   .catch {}      }                MainActor      tasks
                main.async                                                                                 Мягкие
                serial/                                                                                    ошибки
                concurrent
```

## Эпоха 1: NSThread — Ручное управление (2007-2009)

### Описание

Низкоуровневая работа с потоками POSIX. Разработчик сам создает потоки, управляет их жизненным циклом, синхронизирует доступ к данным. Высокий риск race conditions, deadlocks, утечек памяти.

### Пример кода

```swift
// Objective-C эра (2007-2009)
@interface NetworkManager : NSObject
@property (nonatomic, strong) NSMutableArray *cachedData;
@property (nonatomic, strong) NSLock *lock;
@end

@implementation NetworkManager

- (void)fetchDataInBackground {
    // Создание нового потока вручную
    [NSThread detachNewThreadSelector:@selector(downloadData)
                             toTarget:self
                           withObject:nil];
}

- (void)downloadData {
    @autoreleasepool {
        // Работа в фоновом потоке
        NSData *data = [NSData dataWithContentsOfURL:url];

        // Ручная синхронизация доступа к shared state
        [self.lock lock];
        [self.cachedData addObject:data];
        [self.lock unlock];

        // Возврат в главный поток для UI
        [self performSelectorOnMainThread:@selector(updateUI:)
                               withObject:data
                            waitUntilDone:NO];
    }
}

- (void)updateUI:(NSData *)data {
    // Обновление UI в main thread
    self.imageView.image = [UIImage imageWithData:data];
}

@end
```

### Проблемы

- **Race conditions**: Несколько потоков изменяют `cachedData` одновременно
- **Deadlocks**: Неправильная последовательность `lock`/`unlock`
- **Нет управления приоритетами**: Все потоки равны
- **Утечки памяти**: Забытый `@autoreleasepool`
- **Callback hell**: Вложенные `performSelector`

## Эпоха 2: Grand Central Dispatch — Революция (2009-2014)

### Описание

Apple представила GCD в iOS 4 — систему управления конкурентностью на основе очередей (queues) вместо потоков. Разработчик отправляет задачи (blocks) в очереди, а система сама управляет пулом потоков. Поддержка serial и concurrent очередей, QoS (Quality of Service).

### Пример кода

```swift
// Objective-C с GCD (2009-2014)
- (void)fetchImageWithGCD:(NSURL *)url completion:(void(^)(UIImage *))completion {
    // Отправка задачи в глобальную concurrent очередь
    dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
        NSData *data = [NSData dataWithContentsOfURL:url];
        UIImage *image = [UIImage imageWithData:data];

        // Возврат в main queue для UI
        dispatch_async(dispatch_get_main_queue(), ^{
            completion(image);
        });
    });
}

// Синхронизация с serial queue
@property (nonatomic, strong) dispatch_queue_t syncQueue;

- (void)addToCache:(id)object forKey:(NSString *)key {
    dispatch_barrier_async(self.syncQueue, ^{
        self.cache[key] = object; // Thread-safe запись
    });
}

- (id)objectFromCache:(NSString *)key {
    __block id object;
    dispatch_sync(self.syncQueue, ^{
        object = self.cache[key]; // Thread-safe чтение
    });
    return object;
}

// Группы для параллельных задач
- (void)fetchMultipleImages:(NSArray *)urls completion:(void(^)(NSArray *))completion {
    dispatch_group_t group = dispatch_group_create();
    NSMutableArray *images = [NSMutableArray array];

    for (NSURL *url in urls) {
        dispatch_group_enter(group);
        dispatch_async(dispatch_get_global_queue(DISPATCH_QUEUE_PRIORITY_DEFAULT, 0), ^{
            NSData *data = [NSData dataWithContentsOfURL:url];
            UIImage *image = [UIImage imageWithData:data];

            @synchronized(images) {
                [images addObject:image];
            }
            dispatch_group_leave(group);
        });
    }

    dispatch_group_notify(group, dispatch_get_main_queue(), ^{
        completion(images);
    });
}
```

### Преимущества GCD

- **Автоматическое управление потоками**: Система сама создает/уничтожает потоки
- **Quality of Service**: `.userInteractive`, `.userInitiated`, `.utility`, `.background`
- **Барьеры**: `dispatch_barrier_async` для синхронизации
- **Группы**: `dispatch_group` для координации
- **Семафоры**: `dispatch_semaphore` для лимитов

## Эпоха 3: NSOperation — Высокий уровень (2010-2014)

### Описание

Объектно-ориентированная обертка над GCD. Позволяет создавать операции как объекты, добавлять зависимости между ними, отменять, приостанавливать, контролировать максимальное количество параллельных задач.

### Пример кода

```swift
// Objective-C NSOperation (2010-2014)
@interface ImageDownloadOperation : NSOperation
@property (nonatomic, strong) NSURL *imageURL;
@property (nonatomic, copy) void(^completion)(UIImage *);
@end

@implementation ImageDownloadOperation

- (void)main {
    if (self.isCancelled) return;

    NSData *data = [NSData dataWithContentsOfURL:self.imageURL];

    if (self.isCancelled) return;

    UIImage *image = [UIImage imageWithData:data];

    [[NSOperationQueue mainQueue] addOperationWithBlock:^{
        if (self.completion) {
            self.completion(image);
        }
    }];
}

@end

// Использование с зависимостями
- (void)processImagesWithDependencies {
    NSOperationQueue *queue = [[NSOperationQueue alloc] init];
    queue.maxConcurrentOperationCount = 3; // Максимум 3 параллельных

    // Операция 1: Загрузка
    ImageDownloadOperation *downloadOp = [[ImageDownloadOperation alloc] init];
    downloadOp.imageURL = url;

    // Операция 2: Фильтр (зависит от загрузки)
    NSBlockOperation *filterOp = [NSBlockOperation blockOperationWithBlock:^{
        // Применить CIFilter
    }];
    [filterOp addDependency:downloadOp];

    // Операция 3: Сохранение (зависит от фильтра)
    NSBlockOperation *saveOp = [NSBlockOperation blockOperationWithBlock:^{
        // Сохранить в Core Data
    }];
    [saveOp addDependency:filterOp];

    [queue addOperations:@[downloadOp, filterOp, saveOp] waitUntilFinished:NO];
}
```

### Когда использовать NSOperation

- **Сложные зависимости**: Операция B должна выполниться после A и C
- **Отмена**: Нужно отменить длинную операцию (например, при скролле tableView)
- **Лимит параллелизма**: Максимум 2 одновременных загрузки
- **KVO**: Наблюдение за прогрессом операции

## Эпоха 4: Swift 1.0 — GCD в Swift (2014-2017)

### Описание

Swift 1.0 принес синтаксический сахар для GCD, но концептуально ничего не изменилось. Trailing closures сделали код чище, но проблемы callback hell и retain cycles остались.

### Пример кода

```swift
// Swift 1.0-4.x с GCD (2014-2017)
class ImageLoader {
    private let syncQueue = DispatchQueue(label: "com.app.imageCache", attributes: .concurrent)
    private var cache: [String: UIImage] = [:]

    func loadImage(from url: URL, completion: @escaping (UIImage?) -> Void) {
        // Background работа
        DispatchQueue.global(qos: .userInitiated).async {
            guard let data = try? Data(contentsOf: url) else {
                DispatchQueue.main.async { completion(nil) }
                return
            }

            let image = UIImage(data: data)

            // Запись в кэш с barrier
            self.syncQueue.async(flags: .barrier) {
                self.cache[url.absoluteString] = image
            }

            // UI обновление
            DispatchQueue.main.async {
                completion(image)
            }
        }
    }

    func getFromCache(_ url: URL) -> UIImage? {
        var image: UIImage?
        syncQueue.sync {
            image = cache[url.absoluteString]
        }
        return image
    }
}

// Callback hell пример
func fetchUserProfile(userId: String, completion: @escaping (Profile?) -> Void) {
    fetchUser(userId) { user in
        guard let user = user else {
            completion(nil)
            return
        }

        self.fetchAvatar(user.avatarURL) { avatar in
            guard let avatar = avatar else {
                completion(nil)
                return
            }

            self.fetchPosts(userId) { posts in
                let profile = Profile(user: user, avatar: avatar, posts: posts)
                completion(profile)
            }
        }
    }
}
```

### Проблемы Swift + GCD

- **Пирамида doom**: Вложенные замыкания
- **Retain cycles**: `[weak self]` везде
- **Обработка ошибок**: Нет единого механизма
- **Отмена**: Нужно передавать `isCancelled` флаг вручную

## Эпоха 5: Promises/Futures — Третьесторонние решения (2017-2021)

### Описание

Сообщество создало библиотеки (PromiseKit, BrightFutures) для упрощения асинхронного кода. Промисы позволяют цепочки `.then()`, обработку ошибок `.catch()`, параллельные операции `when()`.

### Пример кода

```swift
// PromiseKit (2017-2021)
import PromiseKit

class UserService {
    func fetchProfile(userId: String) -> Promise<Profile> {
        return firstly {
            // Шаг 1: Загрузка пользователя
            fetchUser(userId)
        }.then { user in
            // Шаг 2: Параллельная загрузка аватара и постов
            when(fulfilled: self.fetchAvatar(user.avatarURL),
                           self.fetchPosts(userId))
                .map { avatar, posts in
                    Profile(user: user, avatar: avatar, posts: posts)
                }
        }.recover { error -> Promise<Profile> in
            // Обработка ошибок в одном месте
            if case NetworkError.unauthorized = error {
                return self.refreshToken().then { _ in
                    self.fetchProfile(userId: userId) // Retry
                }
            }
            throw error
        }
    }

    private func fetchUser(_ id: String) -> Promise<User> {
        return Promise { seal in
            DispatchQueue.global().async {
                guard let data = try? Data(contentsOf: URL(string: "/user/\(id)")!) else {
                    seal.reject(NetworkError.notFound)
                    return
                }
                let user = try! JSONDecoder().decode(User.self, from: data)
                seal.fulfill(user)
            }
        }
    }
}

// Использование
userService.fetchProfile(userId: "123")
    .done { profile in
        print("Profile: \(profile.user.name)")
    }
    .catch { error in
        print("Error: \(error)")
    }
```

### Преимущества Promises

- **Линейный код**: `.then()` вместо вложенных замыканий
- **Единая обработка ошибок**: `.catch()` в конце цепочки
- **Композиция**: `when()`, `race()`, `firstly()`
- **Типобезопасность**: `Promise<User>` вместо `Any?`

### Недостатки

- **Третьесторонние зависимости**: Не нативное решение
- **Overhead**: Дополнительные объекты и аллокации
- **Отмена**: Сложная реализация cancellation

## Эпоха 6: Swift 5.5 async/await — Структурная конкурентность (2021-2024)

### Описание

Apple интегрировала async/await в язык Swift 5.5 (iOS 15+). Асинхронные функции выглядят как синхронные, но не блокируют поток. Введены `Task`, `Task Group`, `AsyncSequence`, `MainActor`. Компилятор проверяет thread-safety на этапе компиляции.

### Пример кода

```swift
// Swift 5.5+ async/await (2021-2024)
actor ImageCache {
    private var cache: [URL: UIImage] = [:]

    func image(for url: URL) -> UIImage? {
        cache[url] // Actor изолирует доступ
    }

    func store(_ image: UIImage, for url: URL) {
        cache[url] = image
    }
}

class ImageLoader {
    private let cache = ImageCache()

    // Асинхронная функция выглядит как синхронная
    func loadImage(from url: URL) async throws -> UIImage {
        // Проверка кэша
        if let cached = await cache.image(for: url) {
            return cached
        }

        // Загрузка (URLSession.data теперь async)
        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw NetworkError.invalidResponse
        }

        guard let image = UIImage(data: data) else {
            throw NetworkError.invalidData
        }

        // Сохранение в кэш
        await cache.store(image, for: url)

        return image
    }
}

// Использование в SwiftUI
@MainActor
class ProfileViewModel: ObservableObject {
    @Published var profile: Profile?
    @Published var error: Error?

    private let imageLoader = ImageLoader()

    func fetchProfile(userId: String) async {
        do {
            // Последовательные операции
            let user = try await fetchUser(userId)

            // Параллельные операции с async let
            async let avatar = imageLoader.loadImage(from: user.avatarURL)
            async let posts = fetchPosts(userId)

            // Ожидание всех результатов
            let profile = try await Profile(
                user: user,
                avatar: avatar,
                posts: posts
            )

            self.profile = profile
        } catch {
            self.error = error
        }
    }

    private func fetchUser(_ id: String) async throws -> User {
        let url = URL(string: "https://api.example.com/users/\(id)")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode(User.self, from: data)
    }

    private func fetchPosts(_ userId: String) async throws -> [Post] {
        let url = URL(string: "https://api.example.com/users/\(userId)/posts")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([Post].self, from: data)
    }
}

// В SwiftUI View
struct ProfileView: View {
    @StateObject private var viewModel = ProfileViewModel()

    var body: some View {
        Group {
            if let profile = viewModel.profile {
                ProfileContent(profile: profile)
            } else if let error = viewModel.error {
                ErrorView(error: error)
            } else {
                ProgressView()
            }
        }
        .task { // .task автоматически отменяет при исчезновении view
            await viewModel.fetchProfile(userId: "123")
        }
    }
}
```

### Task Groups для динамического параллелизма

```swift
func downloadImages(urls: [URL]) async throws -> [UIImage] {
    try await withThrowingTaskGroup(of: (Int, UIImage).self) { group in
        // Добавление задач динамически
        for (index, url) in urls.enumerated() {
            group.addTask {
                let image = try await self.loadImage(from: url)
                return (index, image)
            }
        }

        // Сбор результатов с сохранением порядка
        var images: [Int: UIImage] = [:]
        for try await (index, image) in group {
            images[index] = image
        }

        return images.sorted(by: { $0.key < $1.key }).map { $0.value }
    }
}
```

### Отмена задач

```swift
class SearchViewModel: ObservableObject {
    @Published var results: [SearchResult] = []
    private var searchTask: Task<Void, Never>?

    func search(_ query: String) {
        // Отмена предыдущего поиска
        searchTask?.cancel()

        searchTask = Task {
            do {
                // Проверка отмены перед длинной операцией
                try Task.checkCancellation()

                // Задержка для debounce
                try await Task.sleep(for: .milliseconds(300))

                let results = try await performSearch(query)

                // Проверка отмены перед UI обновлением
                if !Task.isCancelled {
                    await MainActor.run {
                        self.results = results
                    }
                }
            } catch is CancellationError {
                // Игнорируем отмену
            } catch {
                print("Search error: \(error)")
            }
        }
    }
}
```

### Преимущества async/await

- **Линейный код**: Читается как синхронный
- **Автоматическая отмена**: Task отменяется при deinit
- **Безопасность**: `@MainActor` гарантирует UI в main thread
- **Производительность**: Нет overhead промисов
- **Встроенная обработка ошибок**: `try/catch`
- **Actor изоляция**: Автоматическая защита от data races

## Эпоха 7: Swift 6 — Строгая конкурентность (2024)

### Описание

Swift 6 делает проверку конкурентности обязательной по умолчанию. Введены `@Sendable`, полная изоляция акторов, проверка на data races на этапе компиляции. Код, который мог вызвать race condition в Swift 5.5, просто не скомпилируется в Swift 6.

### Пример кода

```swift
// Swift 6 строгая конкурентность (2024+)

// @Sendable типы могут безопасно передаваться между актерами
struct User: Sendable { // Все свойства должны быть Sendable
    let id: String
    let name: String
    let avatarURL: URL
}

// Класс НЕ может быть Sendable из-за mutable состояния
class UserManager { // ❌ Ошибка компиляции при передаче между акторами
    var currentUser: User?
}

// Actor для безопасного shared state
actor UserStore {
    private var users: [String: User] = [:]

    func getUser(id: String) -> User? {
        users[id]
    }

    func setUser(_ user: User) {
        users[user.id] = user
    }
}

// MainActor для UI компонентов
@MainActor
class HomeViewModel: ObservableObject {
    @Published var users: [User] = []

    private let store = UserStore()

    // Функция автоматически MainActor изолирована
    func loadUsers() async {
        do {
            let fetchedUsers = try await fetchUsers()

            // Доступ к actor требует await
            for user in fetchedUsers {
                await store.setUser(user)
            }

            // Обновление @Published автоматически в main thread
            self.users = fetchedUsers
        } catch {
            print("Error: \(error)")
        }
    }

    nonisolated func fetchUsers() async throws -> [User] {
        // nonisolated - выполняется вне MainActor
        let url = URL(string: "https://api.example.com/users")!
        let (data, _) = try await URLSession.shared.data(from: url)
        return try JSONDecoder().decode([User].self, from: data)
    }
}

// Global actor для custom изоляции
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

@DatabaseActor
class DatabaseManager {
    private var connection: DatabaseConnection?

    func query(_ sql: String) async throws -> [Row] {
        // Весь код автоматически изолирован в DatabaseActor
        guard let connection = connection else {
            throw DatabaseError.notConnected
        }
        return try await connection.execute(sql)
    }
}
```

### Sendable closures

```swift
// Swift 6 проверяет замыкания на Sendable
func performAsync(_ operation: @Sendable @escaping () async -> Void) {
    Task {
        await operation()
    }
}

class NotSendable {
    var value: Int = 0
}

let obj = NotSendable()

// ❌ Ошибка: NotSendable не Sendable
performAsync {
    obj.value += 1 // Потенциальный race condition
}

// ✅ Правильно: используем actor
actor SafeCounter {
    var value: Int = 0

    func increment() {
        value += 1
    }
}

let counter = SafeCounter()

performAsync {
    await counter.increment() // Безопасно
}
```

### Преимущества Swift 6

- **Compile-time безопасность**: Data races обнаруживаются при компиляции
- **Sendable**: Явное указание thread-safe типов
- **Actor изоляция**: Невозможно обойти защиту
- **Global actors**: Custom изоляция для доменов (Database, Analytics)

## Эпоха 8: Approachable Concurrency — Упрощение (2025)

### Описание

Swift Evolution предложила упрощения для новичков: мягкие ошибки конкурентности (warnings вместо errors), улучшенные диагностики, автоматический вывод `@Sendable`, упрощенный синтаксис `async let` для параллельных задач.

### Пример кода

```swift
// Swift 5.10+ Approachable Concurrency (2025+)

// Автоматический вывод @Sendable для простых типов
struct Product { // Компилятор автоматически делает Sendable
    let id: String
    let price: Double
}

// Упрощенный async let с автоматической отменой
func fetchProductDetails(id: String) async throws -> ProductDetails {
    async let product = fetchProduct(id)
    async let reviews = fetchReviews(id)
    async let recommendations = fetchRecommendations(id)

    // Автоматическая отмена всех async let при выходе из scope
    return try await ProductDetails(
        product: product,
        reviews: reviews,
        recommendations: recommendations
    )
}

// Parallel for-await
func processImages(_ urls: [URL]) async {
    await urls.parallelForEach { url in
        let image = try? await loadImage(from: url)
        await saveToCache(image, for: url)
    }
}

// Мягкие предупреждения для legacy кода
class LegacyManager { // Warning вместо error
    var cache: [String: Any] = [:] // Не Sendable, но компилируется

    func getData() -> Any? {
        cache["key"] // Warning: потенциальный race condition
    }
}
```

## Дерево решений: Какой подход использовать?

```
                                    Нужна асинхронность?
                                            │
                        ┌───────────────────┴────────────────────┐
                       ДА                                        НЕТ
                        │                                         │
                        ▼                                    Синхронный код
            Поддержка iOS 15+?
                        │
        ┌───────────────┴──────────────┐
       ДА                              НЕТ
        │                               │
        ▼                               ▼
  async/await                    GCD или Promises
        │                               │
        │                   ┌───────────┴──────────┐
        │                  iOS 13+                iOS 10+
        │                   │                       │
        │              Combine                   GCD/NSOperation
        │
        ▼
 Простая задача?
        │
   ┌────┴─────┐
  ДА         НЕТ
   │          │
   ▼          ▼
Task {}    TaskGroup / async let
   │          │
   │    ┌─────┴──────┐
   │   Фикс.         Динам.
   │   число         число
   │   задач         задач
   │    │             │
   │ async let    TaskGroup
   │
   ▼
Нужен shared state?
   │
   ┌────┴─────┐
  ДА         НЕТ
   │          │
   ▼          ▼
 actor    Task + await
```

### Когда использовать что

| Подход | Когда использовать | Примеры |
|--------|-------------------|---------|
| **NSThread** | Никогда (legacy) | Поддержка iOS 3 кода |
| **GCD** | Низкий уровень, iOS <15, интеграция с C | Dispatch semaphores, barriers, legacy код |
| **NSOperation** | Сложные зависимости, отмена, лимит параллелизма | Пакетная обработка изображений, загрузки с приоритетами |
| **Combine** | Реактивные потоки, iOS 13-14 | Поиск с debounce, form validation |
| **async/await** | Любая асинхронность в iOS 15+ | Network requests, database queries |
| **Task** | Простые async операции | Одна загрузка изображения |
| **async let** | Фиксированное число параллельных задач | Загрузка user + avatar + posts |
| **TaskGroup** | Динамическое число задач | Обработка массива URL |
| **actor** | Shared mutable state | Cache, database manager, state store |
| **MainActor** | UI обновления | ViewModel, SwiftUI ObservableObject |

## 6 распространенных ошибок

### Ошибка 1: Блокировка main thread с sync

```swift
// ❌ ПЛОХО: Блокирует UI
class ImageLoader {
    func loadImage(url: URL) -> UIImage? {
        let queue = DispatchQueue.global()
        var image: UIImage?

        queue.sync { // ⚠️ Sync в main thread = freeze UI
            let data = try? Data(contentsOf: url)
            image = UIImage(data: data ?? Data())
        }

        return image
    }
}

// Использование
let image = loader.loadImage(url: url) // UI замирает на секунды
imageView.image = image

// ✅ ХОРОШО: Async с callback
class ImageLoader {
    func loadImage(url: URL, completion: @escaping (UIImage?) -> Void) {
        DispatchQueue.global().async {
            let data = try? Data(contentsOf: url)
            let image = UIImage(data: data ?? Data())

            DispatchQueue.main.async {
                completion(image)
            }
        }
    }
}

// ✅ ОТЛИЧНО: async/await
class ImageLoader {
    func loadImage(url: URL) async throws -> UIImage {
        let (data, _) = try await URLSession.shared.data(from: url)
        guard let image = UIImage(data: data) else {
            throw ImageError.invalidData
        }
        return image
    }
}
```

**Почему плохо**: `sync` блокирует текущий поток до завершения задачи. В main thread это замораживает UI.

**Исправление**: Используйте `async` или async/await для фоновых операций.

---

### Ошибка 2: Retain cycle с [self] в async

```swift
// ❌ ПЛОХО: Retain cycle
class ProfileViewController: UIViewController {
    var profile: Profile?

    func loadProfile() {
        Task {
            // ⚠️ Strong reference на self → memory leak
            let profile = try await fetchProfile()
            self.profile = profile // self удерживается Task
            self.tableView.reloadData()
        }
    }

    private func fetchProfile() async throws -> Profile {
        try await Task.sleep(for: .seconds(2))
        return Profile(name: "John")
    }
}

// При закрытии экрана ViewController не освобождается

// ✅ ХОРОШО: [weak self] для UI контроллеров
class ProfileViewController: UIViewController {
    var profile: Profile?

    func loadProfile() {
        Task { [weak self] in
            guard let self else { return } // Early exit если deallocated

            let profile = try await self.fetchProfile()
            self.profile = profile
            self.tableView.reloadData()
        }
    }
}

// ✅ ОТЛИЧНО: Структурная конкурентность с .task
struct ProfileView: View {
    @State private var profile: Profile?

    var body: some View {
        Text(profile?.name ?? "Loading...")
            .task { // Автоматически отменяется при исчезновении view
                profile = try? await fetchProfile()
            }
    }
}
```

**Почему плохо**: Task создает strong reference на `self`. Если ViewController закрывается до завершения Task, возникает retain cycle.

**Исправление**:
- UIKit: `[weak self]` в Task
- SwiftUI: `.task` modifier (автоматическая отмена)
- Actors: Не нужен `[weak self]` (actor reference изолирована)

---

### Ошибка 3: Забыть dispatch на main thread для UI

```swift
// ❌ ПЛОХО: UI обновление в background thread
class ImageViewController: UIViewController {
    @IBOutlet weak var imageView: UIImageView!

    func loadImage(url: URL) {
        DispatchQueue.global().async {
            let data = try? Data(contentsOf: url)
            let image = UIImage(data: data ?? Data())

            // ⚠️ UI обновление в background thread → crash или undefined behavior
            self.imageView.image = image
        }
    }
}

// ✅ ХОРОШО: Явный dispatch на main
func loadImage(url: URL) {
    DispatchQueue.global().async {
        let data = try? Data(contentsOf: url)
        let image = UIImage(data: data ?? Data())

        DispatchQueue.main.async {
            self.imageView.image = image // UI в main thread
        }
    }
}

// ✅ ОТЛИЧНО: @MainActor гарантирует main thread
@MainActor
class ImageViewModel: ObservableObject {
    @Published var image: UIImage?

    func loadImage(url: URL) async {
        // Фоновая работа с nonisolated
        let image = await loadImageData(url)

        // Автоматически в main thread благодаря @MainActor
        self.image = image
    }

    nonisolated func loadImageData(_ url: URL) async -> UIImage? {
        let data = try? await URLSession.shared.data(from: url).0
        return data.flatMap { UIImage(data: $0) }
    }
}
```

**Почему плохо**: UIKit не thread-safe. Обновление UI вне main thread вызывает crashes, визуальные артефакты, undefined behavior.

**Исправление**:
- GCD: Всегда оборачивайте UI код в `DispatchQueue.main.async`
- async/await: Используйте `@MainActor` для ViewModel/ViewController
- SwiftUI: `@Published` автоматически dispatch в main если класс `@MainActor`

---

### Ошибка 4: Data race с shared mutable state

```swift
// ❌ ПЛОХО: Несколько потоков изменяют массив
class ImageCache {
    private var cache: [URL: UIImage] = [:] // ⚠️ Not thread-safe

    func setImage(_ image: UIImage, for url: URL) {
        cache[url] = image // Data race!
    }

    func getImage(for url: URL) -> UIImage? {
        cache[url] // Data race!
    }
}

// Thread 1
DispatchQueue.global().async {
    cache.setImage(image1, for: url1)
}

// Thread 2 одновременно
DispatchQueue.global().async {
    cache.setImage(image2, for: url2) // 💥 Crash или corruption
}

// ✅ ХОРОШО: Serial queue для синхронизации
class ImageCache {
    private var cache: [URL: UIImage] = [:]
    private let queue = DispatchQueue(label: "com.app.imageCache")

    func setImage(_ image: UIImage, for url: URL) {
        queue.async {
            self.cache[url] = image
        }
    }

    func getImage(for url: URL) -> UIImage? {
        queue.sync {
            self.cache[url]
        }
    }
}

// ✅ ОТЛИЧНО: Actor для автоматической изоляции
actor ImageCache {
    private var cache: [URL: UIImage] = [:]

    func setImage(_ image: UIImage, for url: URL) {
        cache[url] = image // Автоматически thread-safe
    }

    func getImage(for url: URL) -> UIImage? {
        cache[url]
    }
}

// Использование
let cache = ImageCache()
await cache.setImage(image, for: url) // await гарантирует безопасность
```

**Почему плохо**: Dictionary, Array, Set не thread-safe. Одновременное изменение из нескольких потоков приводит к data races, crashes, silent corruption.

**Исправление**:
- GCD: Serial queue или concurrent queue с `barrier`
- async/await: Actor изолирует mutable state
- Swift 6: Компилятор запретит небезопасный код

---

### Ошибка 5: Не обрабатывать отмену Task

```swift
// ❌ ПЛОХО: Игнорирование отмены
class SearchViewModel: ObservableObject {
    @Published var results: [Result] = []

    func search(_ query: String) {
        Task {
            // Долгая операция 10 секунд
            for i in 1...10 {
                try? await Task.sleep(for: .seconds(1))
                // ⚠️ Продолжает работу даже после отмены
            }

            let results = try? await performSearch(query)
            self.results = results ?? []
        }
    }
}

// Пользователь печатает быстро:
search("a")     // Task 1 стартует
search("ap")    // Task 2 стартует, Task 1 продолжает работать
search("app")   // Task 3 стартует, Task 1 и 2 продолжают

// Результат: 3 параллельных поиска, race condition в results

// ✅ ХОРОШО: Проверка отмены и сохранение Task
class SearchViewModel: ObservableObject {
    @Published var results: [Result] = []
    private var searchTask: Task<Void, Never>?

    func search(_ query: String) {
        // Отмена предыдущего поиска
        searchTask?.cancel()

        searchTask = Task {
            do {
                // Debounce
                try await Task.sleep(for: .milliseconds(300))

                // Проверка отмены перед API запросом
                try Task.checkCancellation()

                let results = try await performSearch(query)

                // Проверка отмены перед UI обновлением
                if !Task.isCancelled {
                    self.results = results
                }
            } catch is CancellationError {
                // Нормальная отмена, игнорируем
            } catch {
                print("Search error: \(error)")
            }
        }
    }
}

// ✅ ОТЛИЧНО: SwiftUI .task с автоотменой
struct SearchView: View {
    @State private var query = ""
    @State private var results: [Result] = []

    var body: some View {
        List(results) { result in
            Text(result.title)
        }
        .searchable(text: $query)
        .task(id: query) { // Автоматически отменяется при изменении query
            guard !query.isEmpty else { return }

            try? await Task.sleep(for: .milliseconds(300))

            results = (try? await performSearch(query)) ?? []
        }
    }
}
```

**Почему плохо**: Незавершенные Task продолжают работу и потребляют ресурсы. Множественные API запросы, race condition в UI, потеря батареи.

**Исправление**:
- Сохраняйте reference на Task и отменяйте через `.cancel()`
- Проверяйте `Task.isCancelled` перед длинными операциями
- Используйте `try Task.checkCancellation()` для выброса CancellationError
- SwiftUI: `.task(id:)` для автоматической отмены при изменении параметра

---

### Ошибка 6: Deadlock с вложенными sync

```swift
// ❌ ПЛОХО: Deadlock с вложенным sync
class DataManager {
    private let queue = DispatchQueue(label: "com.app.data")
    private var data: [String: Any] = [:]

    func getValue(_ key: String) -> Any? {
        queue.sync {
            return data[key]
        }
    }

    func processData() {
        queue.sync { // Захватили queue
            let value = self.getValue("key") // ⚠️ Попытка sync на уже захваченной queue
            // 💥 Deadlock! Queue ждет сама себя
            print(value ?? "nil")
        }
    }
}

// ✅ ХОРОШО: Избегать вложенных sync
class DataManager {
    private let queue = DispatchQueue(label: "com.app.data")
    private var data: [String: Any] = [:]

    // Private метод без sync (вызывается внутри queue)
    private func _getValue(_ key: String) -> Any? {
        return data[key]
    }

    // Public метод с sync
    func getValue(_ key: String) -> Any? {
        queue.sync {
            return _getValue(key)
        }
    }

    func processData() {
        queue.sync {
            let value = _getValue("key") // Прямой вызов без вложенного sync
            print(value ?? "nil")
        }
    }
}

// ✅ ОТЛИЧНО: Actor без возможности deadlock
actor DataManager {
    private var data: [String: Any] = [:]

    func getValue(_ key: String) -> Any? {
        data[key]
    }

    func processData() {
        let value = getValue("key") // Просто вызов внутри actor
        print(value ?? "nil")
    }
}
```

**Почему плохо**: Serial queue может выполнять только одну задачу одновременно. Если задача на queue пытается сделать sync на эту же queue, возникает deadlock (queue ждет освобождения, но освободиться не может).

**Исправление**:
- Никогда не вызывайте `sync` внутри блока этой же queue
- Создавайте private методы без sync для внутреннего использования
- Используйте actor — невозможно создать deadlock, компилятор проверяет изоляцию

---

## Аналогии для понимания

### NSThread → Ручная коробка передач
Вы сами переключаете передачи (создаете потоки), контролируете сцепление (синхронизация), следите за оборотами (приоритеты). Полный контроль, но легко заглохнуть (deadlock) или сжечь сцепление (race condition).

### GCD → Автоматическая коробка передач
Вы указываете направление (задачи в очереди), а коробка сама выбирает передачу (распределяет потоки). Удобнее, но иногда переключается не в тот момент (callback hell, pyramid of doom).

### async/await → Tesla с автопилотом
Вы пишете код как будто едете по прямой (линейный код), а система сама управляет переключением потоков (continuation). Комфортно, безопасно, эффективно.

### Swift 6 strict concurrency → Система предупреждения о столкновениях
Если вы пытаетесь выехать на встречную (data race), машина просто не даст это сделать. Компилятор = ассистент безопасности, который блокирует опасные маневры до их совершения.

### Actor → Выделенная полоса для автобусов
У каждого actor своя изолированная полоса (thread isolation). Обычные машины (другие потоки) не могут туда заехать. Все пассажиры (данные) в безопасности, нет столкновений.

## Связь с другими темами

### [[android-async-evolution]]
Сравнение эволюции async-подходов в iOS и Android демонстрирует параллельные пути к одной цели — безопасной и читаемой асинхронности. Android прошёл от AsyncTask через RxJava к Kotlin Coroutines, iOS — от NSThread через GCD к async/await. Обе платформы пришли к structured concurrency, но iOS пошла дальше с compile-time safety через Swift 6 strict concurrency. Кросс-платформенным разработчикам критично понимать обе эволюции.

### [[kotlin-coroutines]]
Kotlin coroutines и Swift async/await решают одну задачу разными путями. Kotlin использует CPS-трансформацию и state machines в компиляторе, Swift — continuation-based подход с actor isolation. Понимание Kotlin coroutines помогает оценить design decisions Swift concurrency: почему Apple выбрала actors вместо channels, почему @Sendable строже чем Kotlin `@SharedImmutable`. Для KMP-разработчиков связь между двумя моделями определяет архитектуру shared-кода.

### [[ios-async-await]]
Этот файл описывает историческое *почему* каждый подход появился, а ios-async-await — практическое *как* использовать современный async/await. Знание эволюции объясняет, почему `Task.checkCancellation()` необходим (урок из забытых callbacks), почему `@MainActor` критичен (проблема UI updates из background) и почему structured concurrency запрещает "fire and forget" (урок из memory leaks GCD-эры).

### [[ios-gcd-deep-dive]]
GCD остаётся фундаментом iOS concurrency — async/await работает поверх dispatch queues. Глубокое понимание GCD объясняет, почему `actor` использует serial queue для изоляции, почему `nonisolated` функции выполняются на cooperative thread pool, и в каких специфичных случаях (barriers, semaphores, точный timing) GCD по-прежнему предпочтительнее async/await.

---

## Источники и дальнейшее чтение

### Теоретические основы
- Friedman D. P., Wise D. S. (1976). *The Impact of Applicative Programming on Multiprocessing.* — концепция futures
- Liskov B., Shrira L. (1988). *Promises: Linguistic Support for Efficient Asynchronous Procedure Calls.* PLDI — формализация promises
- Hewitt C. et al. (1973). *A Universal Modular Actor Formalism for AI.* IJCAI — Actor Model
- Elizarov R. (2018). *Structured Concurrency.* — принцип structured concurrency (Kotlin)

### Практические руководства
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — GCD, NSOperation, async/await
- [Swift Concurrency](https://developer.apple.com/documentation/swift/concurrency) — Apple Documentation
- WWDC 2021: [Meet async/await in Swift](https://developer.apple.com/videos/play/wwdc2021/10132/)

## Связанные материалы

- [[android-async-evolution]] — Сравнение с AsyncTask → RxJava → Coroutines
- [[kotlin-coroutines]] — Как Kotlin решает конкурентность
- [[swift-concurrency-deep-dive]] — Детальное погружение в async/await
- [[gcd-best-practices]] — Когда все еще использовать GCD
- [[actor-isolation-patterns]] — Паттерны работы с actors

## Резюме

iOS прошла путь от ручного управления потоками (2007) до compile-time безопасности (2024). **GCD остается фундаментом** для низкоуровневых задач, но **async/await — это стандарт** для новых проектов на iOS 15+. **Swift 6** делает невозможным писать небезопасный конкурентный код. **Approachable Concurrency** снижает порог входа для новичков.

**Главное правило 2026**: Используйте async/await + actor для нового кода, GCD только для специфичных низкоуровневых задач (semaphores, barriers), NSOperation для сложных зависимостей в legacy проектах.

---

## Проверь себя

> [!question]- Почему Apple не удалила GCD после введения async/await, и в каких случаях GCD остается предпочтительным выбором?
> GCD остается фундаментом: async/await построен поверх libdispatch. GCD предпочтителен для: DispatchSource (системные события, таймеры), barriers (readers-writer lock), semaphores (ограничение concurrency), интеграции с C/ObjC API. Также GCD нужен для поддержки iOS < 15, где async/await недоступен.

> [!question]- Какую проблему решает Swift 6 strict concurrency checking и как она связана с data races?
> Swift 6 проверяет потокобезопасность на этапе компиляции. Все типы, передаваемые между isolation domains (actors, tasks), должны быть Sendable. Мутабельные reference types без синхронизации вызывают ошибку компиляции. Это исключает целый класс runtime багов -- data races, которые раньше проявлялись непредсказуемо.

> [!question]- Сценарий: вы поддерживаете приложение с 2015 года. Кодовая база использует NSOperationQueue, GCD и completion handlers. Как постепенно мигрировать на async/await?
> Поэтапно: 1) Обернуть существующие completion handlers через withCheckedContinuation. 2) Новый код писать на async/await. 3) Заменять NSOperationQueue на TaskGroup для новых фич. 4) Постепенно рефакторить GCD-код, начиная с верхних слоев (UI -> ViewModel -> Service). 5) Включить strict concurrency checking в warning mode, затем в error mode.

---

## Ключевые карточки

Какие 4 эпохи асинхронности в iOS можно выделить?
?
1) NSThread/pthreads (2007) -- ручное управление. 2) GCD/NSOperation (2009) -- очереди вместо потоков. 3) Combine (2019) -- реактивные потоки. 4) async/await + actors (2021) -- структурированная конкурентность с compile-time safety. Каждая эпоха не отменяет предыдущую.

Что такое Approachable Concurrency в Swift 6.2?
?
Инициатива Apple для снижения порога входа в Swift Concurrency. Упрощает работу с Sendable (автоматический вывод), улучшает диагностику ошибок компилятора, добавляет nonisolated(unsafe) для постепенной миграции. Цель -- сделать конкурентность доступной без глубокого понимания всей модели.

Чем NSOperation отличается от GCD?
?
NSOperation -- объектно-ориентированная обертка поверх GCD. Преимущества: зависимости между операциями (addDependency), отмена (cancel), KVO-наблюдение за состоянием, приоритеты. GCD легче и быстрее для простых задач. NSOperation нужен для сложных графов зависимостей.

Как withCheckedContinuation помогает в миграции на async/await?
?
withCheckedContinuation оборачивает callback-based API в async функцию. Внутри вызывается legacy функция с completion handler, который вызывает continuation.resume(returning:) или continuation.resume(throwing:). Checked-версия проверяет, что resume вызван ровно один раз (crash при нарушении).

Что изменил Swift 6 в модели конкурентности?
?
Swift 6 включил strict concurrency checking по умолчанию. Все передачи между isolation domains требуют Sendable. GlobalActor аннотации обязательны для shared mutable state. Компилятор выдает ошибки (не warnings) при потенциальных data races. Это сделало конкурентный код безопасным на уровне типов.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[ios-threading-fundamentals]] | Основы многопоточности -- фундамент для понимания эволюции |
| Углубиться | [[ios-async-await]] | Детальный разбор современной модели async/await |
| Смежная тема | [[android-coroutines-mistakes]] | Эволюция асинхронности в Android для сравнения |
| Обзор | [[ios-overview]] | Вернуться к карте раздела |
