---
title: "Repository Pattern в iOS"
created: 2026-01-11
modified: 2026-01-11
type: deep-dive
status: published
tags:
  - topic/ios
  - topic/swift
  - topic/architecture
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-repository-pattern]]"
  - "[[ios-architecture-patterns]]"
  - "[[ios-data-persistence]]"
prerequisites:
  - "[[ios-overview]]"
  - "[[ios-architecture-patterns]]"
  - "[[ios-data-persistence]]"
---

# iOS Repository Pattern

## TL;DR

Repository Pattern в iOS — это архитектурный паттерн, который абстрагирует источники данных (API, база данных, кэш) за единым интерфейсом. Обеспечивает Single Source of Truth (SSOT), упрощает тестирование через протоколы, поддерживает offline-first подход и seamless переключение между источниками данных.

**Ключевые преимущества:**
- 🎯 Единая точка доступа к данным
- 🔄 Прозрачное кэширование и синхронизация
- 🧪 Простое тестирование с моками
- 📱 Offline-first архитектура
- 🔌 Легкая замена источников данных

## Аналогии

### Библиотекарь
Repository как библиотекарь: вы просите книгу, а библиотекарь решает, взять ее из хранилища, архива или заказать в другой библиотеке. Вам не нужно знать, откуда пришла книга.

### Кэширующий Proxy
Repository работает как умный прокси-сервер: сначала проверяет локальный кэш (memory), затем диск (persistent storage), и только в конце идет в сеть. Результат автоматически кэшируется для следующих запросов.

### Единое Окно
Repository как "единое окно" в госуслугах: один интерфейс для всех операций с данными, независимо от того, где они физически хранятся — в памяти, на диске или на сервере.

## Определение Repository Pattern

### Что такое Repository?

Repository — это посредник между бизнес-логикой (domain layer) и источниками данных (data sources), который:

```
┌─────────────────────────────────────────────────┐
│              Domain Layer                        │
│         (ViewModels, Use Cases)                  │
└────────────────┬────────────────────────────────┘
                 │ Protocol Interface
                 ▼
┌─────────────────────────────────────────────────┐
│         Repository (SSOT)                        │
│    ┌──────────┬──────────┬──────────┐          │
│    │  Cache   │  Local   │  Remote  │          │
│    │ Strategy │    DB    │   API    │          │
│    └──────────┴──────────┴──────────┘          │
└─────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           Data Sources                           │
│   Memory Cache │ Core Data │ URLSession         │
└─────────────────────────────────────────────────┘
```

### Основные обязанности

1. **Абстракция источников данных** — скрывает детали реализации
2. **Кэширование** — управляет многоуровневым кэшем
3. **Синхронизация** — координирует данные между источниками
4. **Error handling** — унифицирует обработку ошибок
5. **SSOT** — обеспечивает единый источник правды

## Single Source of Truth (SSOT)

### Концепция SSOT

```swift
// ❌ Неправильно: множественные источники правды
class UserViewModel {
    @Published var user: User?

    func loadUser() async {
        // Откуда брать данные? Cache? API? Core Data?
        let cachedUser = UserDefaults.standard.getUser()
        let apiUser = try? await api.fetchUser()
        let dbUser = database.loadUser()

        // Какой правильный? 🤷‍♂️
        user = apiUser ?? cachedUser ?? dbUser
    }
}
```

```swift
// ✅ Правильно: Repository как единственный источник правды
protocol UserRepositoryProtocol {
    func getUser(id: String) async throws -> User
    func observeUser(id: String) -> AnyPublisher<User, Error>
}

class UserViewModel {
    private let repository: UserRepositoryProtocol
    @Published var user: User?

    func loadUser() async {
        // Repository сам решает, откуда брать данные
        user = try? await repository.getUser(id: currentUserId)
    }
}
```

### Диаграмма потока данных SSOT

```
Request Flow:
─────────────
ViewModel → Repository → [Memory Cache?] → [Disk Cache?] → [Network API]
                              ↓ Hit           ↓ Hit          ↓ Success
                              ├──────────────┴───────────────┘
                              │
                              ▼
                         Update all caches
                              │
                              ▼
                         Return to ViewModel

Data Flow:
──────────
Network Response → Repository → Update Disk → Update Memory → Notify Observers
```

## Protocol-Based Repositories

### Определение протокола

```swift
// Базовый протокол Repository
protocol RepositoryProtocol {
    associatedtype Entity
    associatedtype ID: Hashable

    // CRUD операции
    func get(id: ID) async throws -> Entity
    func getAll() async throws -> [Entity]
    func save(_ entity: Entity) async throws
    func delete(id: ID) async throws

    // Реактивные операции
    func observe(id: ID) -> AnyPublisher<Entity, Error>
    func observeAll() -> AnyPublisher<[Entity], Error>
}

// Специфичный протокол для User
protocol UserRepositoryProtocol {
    func getUser(id: String) async throws -> User
    func getCurrentUser() async throws -> User
    func updateUser(_ user: User) async throws
    func observeCurrentUser() -> AnyPublisher<User?, Never>
    func logout() async throws
}
```

### Имплементация с протоколом

```swift
final class UserRepository: UserRepositoryProtocol {
    private let remoteDataSource: UserRemoteDataSource
    private let localDataSource: UserLocalDataSource
    private let cacheService: CacheService

    init(
        remoteDataSource: UserRemoteDataSource,
        localDataSource: UserLocalDataSource,
        cacheService: CacheService
    ) {
        self.remoteDataSource = remoteDataSource
        self.localDataSource = localDataSource
        self.cacheService = cacheService
    }

    func getUser(id: String) async throws -> User {
        // 1. Проверяем memory cache
        if let cached = cacheService.get(User.self, key: id) {
            return cached
        }

        // 2. Проверяем local database
        if let local = try? await localDataSource.getUser(id: id) {
            cacheService.set(local, key: id)
            return local
        }

        // 3. Запрашиваем из сети
        let remote = try await remoteDataSource.fetchUser(id: id)

        // 4. Сохраняем в кэш и БД
        cacheService.set(remote, key: id)
        try? await localDataSource.saveUser(remote)

        return remote
    }

    func observeCurrentUser() -> AnyPublisher<User?, Never> {
        localDataSource.observeCurrentUser()
            .catch { _ in Just(nil) }
            .eraseToAnyPublisher()
    }
}
```

## Кэширующие стратегии

### Трёхуровневое кэширование

```
┌─────────────────────────────────────┐
│     Level 1: Memory Cache           │ ← Fastest (NSCache, Dictionary)
│     Volatile, cleared on app kill   │
└──────────────┬──────────────────────┘
               │ Miss
               ▼
┌─────────────────────────────────────┐
│     Level 2: Disk Cache             │ ← Medium (Core Data, Files, UserDefaults)
│     Persistent across launches      │
└──────────────┬──────────────────────┘
               │ Miss
               ▼
┌─────────────────────────────────────┐
│     Level 3: Network (Remote API)   │ ← Slowest (URLSession, WebSocket)
│     Always up-to-date               │
└─────────────────────────────────────┘
          │ Response
          ▼
    Update L2 & L1
```

### Имплементация Cache Service

```swift
// Memory Cache
final class MemoryCache {
    private let cache = NSCache<NSString, CacheEntry>()
    private let queue = DispatchQueue(label: "com.app.memory-cache")

    struct CacheEntry {
        let value: Any
        let expirationDate: Date
    }

    func get<T>(_ type: T.Type, key: String) -> T? {
        queue.sync {
            guard let entry = cache.object(forKey: key as NSString),
                  entry.expirationDate > Date() else {
                return nil
            }
            return entry.value as? T
        }
    }

    func set<T>(_ value: T, key: String, ttl: TimeInterval = 300) {
        queue.async { [weak self] in
            let entry = CacheEntry(
                value: value,
                expirationDate: Date().addingTimeInterval(ttl)
            )
            self?.cache.setObject(entry, forKey: key as NSString)
        }
    }

    func clear() {
        queue.async { [weak self] in
            self?.cache.removeAllObjects()
        }
    }
}

// Disk Cache (UserDefaults wrapper)
final class DiskCache {
    private let userDefaults = UserDefaults.standard
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    func get<T: Codable>(_ type: T.Type, key: String) -> T? {
        guard let data = userDefaults.data(forKey: key) else { return nil }
        return try? decoder.decode(T.self, from: data)
    }

    func set<T: Codable>(_ value: T, key: String) {
        guard let data = try? encoder.encode(value) else { return }
        userDefaults.set(data, forKey: key)
    }

    func remove(key: String) {
        userDefaults.removeObject(forKey: key)
    }
}
```

### Cache Strategy Pattern

```swift
enum CacheStrategy {
    case cacheFirst       // Сначала кэш, потом сеть
    case networkFirst     // Сначала сеть, fallback на кэш
    case cacheOnly        // Только кэш (offline mode)
    case networkOnly      // Только сеть (no cache)
    case cacheAndNetwork  // Кэш сразу, потом обновление из сети
}

final class CacheableRepository<T: Codable> {
    private let memoryCache: MemoryCache
    private let diskCache: DiskCache
    private let networkService: NetworkService

    func fetch(
        key: String,
        strategy: CacheStrategy
    ) async throws -> T {
        switch strategy {
        case .cacheFirst:
            return try await cacheFirstStrategy(key: key)

        case .networkFirst:
            return try await networkFirstStrategy(key: key)

        case .cacheOnly:
            return try cacheOnlyStrategy(key: key)

        case .networkOnly:
            return try await networkOnlyStrategy(key: key)

        case .cacheAndNetwork:
            return try await cacheAndNetworkStrategy(key: key)
        }
    }

    private func cacheFirstStrategy(key: String) async throws -> T {
        // Memory → Disk → Network
        if let memory = memoryCache.get(T.self, key: key) {
            return memory
        }

        if let disk = diskCache.get(T.self, key: key) {
            memoryCache.set(disk, key: key)
            return disk
        }

        let network = try await networkService.fetch(T.self, endpoint: key)
        diskCache.set(network, key: key)
        memoryCache.set(network, key: key)
        return network
    }

    private func networkFirstStrategy(key: String) async throws -> T {
        do {
            let network = try await networkService.fetch(T.self, endpoint: key)
            diskCache.set(network, key: key)
            memoryCache.set(network, key: key)
            return network
        } catch {
            // Fallback на кэш
            if let disk = diskCache.get(T.self, key: key) {
                return disk
            }
            throw error
        }
    }

    private func cacheAndNetworkStrategy(key: String) async throws -> T {
        // Возвращаем кэш немедленно, обновляем в фоне
        if let cached = memoryCache.get(T.self, key: key)
            ?? diskCache.get(T.self, key: key) {

            // Background refresh
            Task {
                let network = try? await networkService.fetch(T.self, endpoint: key)
                if let network = network {
                    diskCache.set(network, key: key)
                    memoryCache.set(network, key: key)
                }
            }

            return cached
        }

        // Нет кэша — ждем сеть
        return try await networkFirstStrategy(key: key)
    }
}
```

## Offline-First архитектура

### Концепция Offline-First

```
User Action → Repository → Local DB (immediate save)
                    │
                    ├→ Sync Queue (pending operations)
                    │
                    └→ Background Sync (when online)
                              │
                              ▼
                         Remote API
                              │
                              ▼
                    Update Local DB with server response
```

### Имплементация Sync Queue

```swift
// Модель операции синхронизации
struct SyncOperation: Codable, Identifiable {
    let id: UUID
    let type: OperationType
    let entityId: String
    let data: Data
    let timestamp: Date
    let retryCount: Int

    enum OperationType: String, Codable {
        case create, update, delete
    }
}

// Sync Manager
final class SyncManager {
    private let repository: SyncableRepository
    private let localStorage: LocalStorage
    private let networkMonitor: NetworkMonitor

    @Published private(set) var isSyncing = false
    @Published private(set) var pendingOperations: [SyncOperation] = []

    private var cancellables = Set<AnyCancellable>()

    init(
        repository: SyncableRepository,
        localStorage: LocalStorage,
        networkMonitor: NetworkMonitor
    ) {
        self.repository = repository
        self.localStorage = localStorage
        self.networkMonitor = networkMonitor

        observeNetworkChanges()
        loadPendingOperations()
    }

    private func observeNetworkChanges() {
        networkMonitor.isConnectedPublisher
            .filter { $0 } // Только когда появляется сеть
            .sink { [weak self] _ in
                Task {
                    await self?.syncPendingOperations()
                }
            }
            .store(in: &cancellables)
    }

    func addOperation(_ operation: SyncOperation) {
        pendingOperations.append(operation)
        savePendingOperations()

        if networkMonitor.isConnected {
            Task {
                await syncPendingOperations()
            }
        }
    }

    func syncPendingOperations() async {
        guard !isSyncing, !pendingOperations.isEmpty else { return }

        isSyncing = true
        defer { isSyncing = false }

        var failedOperations: [SyncOperation] = []

        for operation in pendingOperations {
            do {
                try await executeOperation(operation)
            } catch {
                // Retry logic
                if operation.retryCount < 3 {
                    var retried = operation
                    retried = SyncOperation(
                        id: operation.id,
                        type: operation.type,
                        entityId: operation.entityId,
                        data: operation.data,
                        timestamp: operation.timestamp,
                        retryCount: operation.retryCount + 1
                    )
                    failedOperations.append(retried)
                }
            }
        }

        pendingOperations = failedOperations
        savePendingOperations()
    }

    private func executeOperation(_ operation: SyncOperation) async throws {
        switch operation.type {
        case .create:
            try await repository.syncCreate(data: operation.data)
        case .update:
            try await repository.syncUpdate(id: operation.entityId, data: operation.data)
        case .delete:
            try await repository.syncDelete(id: operation.entityId)
        }
    }
}
```

### Offline-First Repository

```swift
final class OfflineFirstRepository<T: Codable & Identifiable> {
    private let localDataSource: LocalDataSource<T>
    private let remoteDataSource: RemoteDataSource<T>
    private let syncManager: SyncManager

    // CRUD с offline support
    func create(_ entity: T) async throws -> T {
        // 1. Сохраняем локально сразу
        let saved = try await localDataSource.save(entity)

        // 2. Добавляем в очередь синхронизации
        let data = try JSONEncoder().encode(entity)
        let operation = SyncOperation(
            id: UUID(),
            type: .create,
            entityId: entity.id as! String,
            data: data,
            timestamp: Date(),
            retryCount: 0
        )
        syncManager.addOperation(operation)

        return saved
    }

    func update(_ entity: T) async throws {
        // Optimistic update
        try await localDataSource.update(entity)

        let data = try JSONEncoder().encode(entity)
        let operation = SyncOperation(
            id: UUID(),
            type: .update,
            entityId: entity.id as! String,
            data: data,
            timestamp: Date(),
            retryCount: 0
        )
        syncManager.addOperation(operation)
    }

    func get(id: String) async throws -> T {
        // Всегда читаем из локальной БД
        try await localDataSource.get(id: id)
    }

    func getAll() async throws -> [T] {
        try await localDataSource.getAll()
    }
}
```

## Data Synchronization Patterns

### Conflict Resolution Strategy

```swift
enum ConflictResolutionStrategy {
    case serverWins      // Сервер всегда прав
    case clientWins      // Клиент всегда прав
    case lastWriteWins   // Побеждает последнее изменение
    case manual          // Требуется ручное разрешение
}

struct SyncResult<T> {
    let entity: T
    let conflict: ConflictInfo?
    let resolved: Bool
}

struct ConflictInfo {
    let localVersion: Any
    let remoteVersion: Any
    let lastSyncDate: Date
}

final class SyncCoordinator<T: Syncable> {
    private let strategy: ConflictResolutionStrategy

    func sync(
        localEntity: T,
        remoteEntity: T
    ) async throws -> SyncResult<T> {
        guard localEntity.id == remoteEntity.id else {
            throw SyncError.idMismatch
        }

        // Проверяем конфликт
        if let conflict = detectConflict(local: localEntity, remote: remoteEntity) {
            let resolved = try resolveConflict(
                local: localEntity,
                remote: remoteEntity,
                conflict: conflict
            )
            return SyncResult(entity: resolved, conflict: conflict, resolved: true)
        }

        // Нет конфликта — используем более свежую версию
        let winner = localEntity.modifiedAt > remoteEntity.modifiedAt
            ? localEntity
            : remoteEntity

        return SyncResult(entity: winner, conflict: nil, resolved: true)
    }

    private func detectConflict(local: T, remote: T) -> ConflictInfo? {
        // Конфликт, если оба изменились после последней синхронизации
        guard local.modifiedAt > local.lastSyncedAt,
              remote.modifiedAt > local.lastSyncedAt else {
            return nil
        }

        return ConflictInfo(
            localVersion: local,
            remoteVersion: remote,
            lastSyncDate: local.lastSyncedAt
        )
    }

    private func resolveConflict(
        local: T,
        remote: T,
        conflict: ConflictInfo
    ) throws -> T {
        switch strategy {
        case .serverWins:
            return remote

        case .clientWins:
            return local

        case .lastWriteWins:
            return local.modifiedAt > remote.modifiedAt ? local : remote

        case .manual:
            throw SyncError.manualResolutionRequired(conflict)
        }
    }
}

protocol Syncable: Identifiable {
    var id: String { get }
    var modifiedAt: Date { get }
    var lastSyncedAt: Date { get }
}
```

### Incremental Sync

```swift
final class IncrementalSyncRepository {
    private let remoteAPI: RemoteAPI
    private let localStorage: LocalStorage
    private let syncStateStorage: SyncStateStorage

    func performIncrementalSync() async throws {
        let lastSyncTimestamp = syncStateStorage.getLastSyncTimestamp()

        // Запрашиваем только изменения после последней синхронизации
        let changes = try await remoteAPI.fetchChanges(since: lastSyncTimestamp)

        // Применяем изменения к локальной БД
        for change in changes.created {
            try await localStorage.insert(change)
        }

        for change in changes.updated {
            try await localStorage.update(change)
        }

        for change in changes.deleted {
            try await localStorage.delete(id: change.id)
        }

        // Сохраняем метку времени синхронизации
        syncStateStorage.updateLastSyncTimestamp(Date())
    }
}

struct SyncChanges<T> {
    let created: [T]
    let updated: [T]
    let deleted: [DeletedEntity]
    let timestamp: Date
}

struct DeletedEntity {
    let id: String
    let deletedAt: Date
}
```

## Repository с Combine Publishers

### Observable Repository

```swift
import Combine

final class CombineRepository<T: Codable & Identifiable> {
    private let dataSubject = CurrentValueSubject<[T], Never>([])
    private let errorSubject = PassthroughSubject<Error, Never>()

    private let localStorage: LocalDataSource<T>
    private let remoteDataSource: RemoteDataSource<T>

    // Observable streams
    var dataPublisher: AnyPublisher<[T], Never> {
        dataSubject.eraseToAnyPublisher()
    }

    var errorPublisher: AnyPublisher<Error, Never> {
        errorSubject.eraseToAnyPublisher()
    }

    func observeAll() -> AnyPublisher<[T], Never> {
        // Комбинируем локальные изменения и сетевые обновления
        Publishers.Merge(
            localStorage.observeAll(),
            refreshFromNetwork()
        )
        .catch { [weak self] error -> AnyPublisher<[T], Never> in
            self?.errorSubject.send(error)
            return Just([]).eraseToAnyPublisher()
        }
        .eraseToAnyPublisher()
    }

    func observe(id: String) -> AnyPublisher<T?, Never> {
        localStorage.observe(id: id)
            .catch { [weak self] error -> AnyPublisher<T?, Never> in
                self?.errorSubject.send(error)
                return Just(nil).eraseToAnyPublisher()
            }
            .eraseToAnyPublisher()
    }

    private func refreshFromNetwork() -> AnyPublisher<[T], Error> {
        remoteDataSource.fetchAll()
            .handleEvents(receiveOutput: { [weak self] entities in
                Task {
                    try? await self?.localStorage.saveAll(entities)
                }
            })
            .eraseToAnyPublisher()
    }
}

// Использование с SwiftUI
class ItemsViewModel: ObservableObject {
    @Published var items: [Item] = []
    @Published var error: Error?

    private let repository: CombineRepository<Item>
    private var cancellables = Set<AnyCancellable>()

    init(repository: CombineRepository<Item>) {
        self.repository = repository
        observeData()
    }

    private func observeData() {
        repository.observeAll()
            .receive(on: DispatchQueue.main)
            .assign(to: &$items)

        repository.errorPublisher
            .receive(on: DispatchQueue.main)
            .assign(to: &$error)
    }
}
```

### Reactive Operations

```swift
extension CombineRepository {
    // Реактивное создание с автоматическим обновлением
    func create(_ entity: T) -> AnyPublisher<T, Error> {
        Future { [weak self] promise in
            Task {
                do {
                    let saved = try await self?.localStorage.save(entity)
                    try await self?.remoteDataSource.create(entity)
                    promise(.success(saved!))
                } catch {
                    promise(.failure(error))
                }
            }
        }
        .handleEvents(receiveOutput: { [weak self] _ in
            self?.refreshData()
        })
        .eraseToAnyPublisher()
    }

    // Batch операции с debounce
    func search(query: String) -> AnyPublisher<[T], Never> {
        Just(query)
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .flatMap { [weak self] searchQuery -> AnyPublisher<[T], Never> in
                guard let self = self else {
                    return Just([]).eraseToAnyPublisher()
                }

                return self.localStorage.search(query: searchQuery)
                    .catch { _ in Just([]) }
                    .eraseToAnyPublisher()
            }
            .eraseToAnyPublisher()
    }

    private func refreshData() {
        Task {
            let data = try? await localStorage.getAll()
            dataSubject.send(data ?? [])
        }
    }
}
```

## Repository с Async/Await

### Modern Async Repository

```swift
actor AsyncRepository<T: Codable & Identifiable> {
    private let localStorage: LocalDataSource<T>
    private let remoteDataSource: RemoteDataSource<T>
    private let cacheService: CacheService

    private var activeRequests: [String: Task<T, Error>] = [:]

    // Async CRUD operations
    func get(id: String, cacheStrategy: CacheStrategy = .cacheFirst) async throws -> T {
        // Дедупликация запросов
        if let activeRequest = activeRequests[id] {
            return try await activeRequest.value
        }

        let task = Task<T, Error> {
            defer { activeRequests.removeValue(forKey: id) }

            switch cacheStrategy {
            case .cacheFirst:
                return try await getCacheFirst(id: id)
            case .networkFirst:
                return try await getNetworkFirst(id: id)
            default:
                return try await getCacheFirst(id: id)
            }
        }

        activeRequests[id] = task
        return try await task.value
    }

    private func getCacheFirst(id: String) async throws -> T {
        // Try memory cache
        if let cached = await cacheService.get(T.self, key: id) {
            return cached
        }

        // Try local database
        if let local = try? await localStorage.get(id: id) {
            await cacheService.set(local, key: id)
            return local
        }

        // Fetch from network
        let remote = try await remoteDataSource.fetch(id: id)

        // Update caches
        await cacheService.set(remote, key: id)
        try? await localStorage.save(remote)

        return remote
    }

    func getAll(
        forceRefresh: Bool = false
    ) async throws -> [T] {
        if forceRefresh {
            return try await refreshFromNetwork()
        }

        // Try local first
        let local = try await localStorage.getAll()

        if !local.isEmpty {
            // Background refresh
            Task {
                try? await refreshFromNetwork()
            }
            return local
        }

        return try await refreshFromNetwork()
    }

    func save(_ entity: T) async throws -> T {
        // Save locally first (optimistic update)
        let saved = try await localStorage.save(entity)

        // Sync with remote
        do {
            let remote = try await remoteDataSource.create(entity)
            // Update with server response
            try await localStorage.update(remote)
            await cacheService.set(remote, key: String(describing: remote.id))
            return remote
        } catch {
            // Rollback on failure
            try? await localStorage.delete(id: saved.id as! String)
            throw error
        }
    }

    private func refreshFromNetwork() async throws -> [T] {
        let remote = try await remoteDataSource.fetchAll()
        try await localStorage.saveAll(remote)
        return remote
    }
}
```

### Async Streams для непрерывных обновлений

```swift
extension AsyncRepository {
    // AsyncStream для наблюдения за изменениями
    func observeAll() -> AsyncStream<[T]> {
        AsyncStream { continuation in
            let task = Task {
                // Начальное значение из локальной БД
                if let initial = try? await localStorage.getAll() {
                    continuation.yield(initial)
                }

                // Подписываемся на изменения
                for await change in localStorage.changesStream() {
                    let updated = try? await localStorage.getAll()
                    if let updated = updated {
                        continuation.yield(updated)
                    }
                }
            }

            continuation.onTermination = { _ in
                task.cancel()
            }
        }
    }

    func observe(id: String) -> AsyncStream<T?> {
        AsyncStream { continuation in
            let task = Task {
                for await _ in localStorage.changesStream() {
                    let entity = try? await localStorage.get(id: id)
                    continuation.yield(entity)
                }
            }

            continuation.onTermination = { _ in
                task.cancel()
            }
        }
    }
}

// Использование в SwiftUI
class AsyncViewModel: ObservableObject {
    @Published var items: [Item] = []
    private let repository: AsyncRepository<Item>

    func startObserving() {
        Task {
            for await items in repository.observeAll() {
                await MainActor.run {
                    self.items = items
                }
            }
        }
    }
}
```

### Task Group для параллельных операций

```swift
extension AsyncRepository {
    // Параллельная загрузка множества entities
    func getMultiple(ids: [String]) async throws -> [T] {
        try await withThrowingTaskGroup(of: T.self) { group in
            for id in ids {
                group.addTask {
                    try await self.get(id: id)
                }
            }

            var results: [T] = []
            for try await entity in group {
                results.append(entity)
            }
            return results
        }
    }

    // Batch операция с retry
    func saveMultiple(
        _ entities: [T],
        maxRetries: Int = 3
    ) async throws -> [T] {
        try await withThrowingTaskGroup(of: T.self) { group in
            for entity in entities {
                group.addTask {
                    try await self.saveWithRetry(entity, maxRetries: maxRetries)
                }
            }

            var results: [T] = []
            for try await saved in group {
                results.append(saved)
            }
            return results
        }
    }

    private func saveWithRetry(
        _ entity: T,
        maxRetries: Int
    ) async throws -> T {
        var lastError: Error?

        for attempt in 0...maxRetries {
            do {
                return try await save(entity)
            } catch {
                lastError = error
                if attempt < maxRetries {
                    // Exponential backoff
                    try await Task.sleep(nanoseconds: UInt64(pow(2.0, Double(attempt)) * 1_000_000_000))
                }
            }
        }

        throw lastError ?? RepositoryError.saveFailed
    }
}
```

## Error Handling Strategies

### Типизированные ошибки

```swift
enum RepositoryError: LocalizedError {
    case networkUnavailable
    case cacheExpired
    case entityNotFound(id: String)
    case invalidData
    case syncConflict(ConflictInfo)
    case unauthorized
    case serverError(statusCode: Int)
    case unknown(Error)

    var errorDescription: String? {
        switch self {
        case .networkUnavailable:
            return "Нет подключения к интернету"
        case .cacheExpired:
            return "Кэш устарел, требуется обновление"
        case .entityNotFound(let id):
            return "Объект с ID \(id) не найден"
        case .invalidData:
            return "Некорректные данные"
        case .syncConflict:
            return "Конфликт синхронизации данных"
        case .unauthorized:
            return "Требуется авторизация"
        case .serverError(let code):
            return "Ошибка сервера: \(code)"
        case .unknown(let error):
            return error.localizedDescription
        }
    }

    var isRecoverable: Bool {
        switch self {
        case .networkUnavailable, .cacheExpired, .serverError:
            return true
        case .unauthorized, .entityNotFound, .invalidData:
            return false
        case .syncConflict:
            return true
        case .unknown:
            return false
        }
    }
}
```

### Result-based Repository

```swift
protocol ResultRepository {
    associatedtype Entity

    func get(id: String) async -> Result<Entity, RepositoryError>
    func getAll() async -> Result<[Entity], RepositoryError>
    func save(_ entity: Entity) async -> Result<Entity, RepositoryError>
}

final class SafeRepository<T: Codable>: ResultRepository {
    typealias Entity = T

    private let dataSource: DataSource<T>

    func get(id: String) async -> Result<T, RepositoryError> {
        do {
            let entity = try await dataSource.fetch(id: id)
            return .success(entity)
        } catch let error as NetworkError {
            return .failure(mapNetworkError(error))
        } catch {
            return .failure(.unknown(error))
        }
    }

    func save(_ entity: T) async -> Result<T, RepositoryError> {
        do {
            let saved = try await dataSource.save(entity)
            return .success(saved)
        } catch {
            return .failure(mapError(error))
        }
    }

    private func mapNetworkError(_ error: NetworkError) -> RepositoryError {
        switch error {
        case .noConnection:
            return .networkUnavailable
        case .unauthorized:
            return .unauthorized
        case .serverError(let code):
            return .serverError(statusCode: code)
        default:
            return .unknown(error)
        }
    }
}

// Использование
let result = await repository.get(id: "123")
switch result {
case .success(let user):
    print("User loaded: \(user)")
case .failure(let error):
    if error.isRecoverable {
        // Retry logic
    } else {
        // Show error to user
    }
}
```

### Error Recovery Strategy

```swift
final class ResilientRepository<T: Codable & Identifiable> {
    private let primarySource: RemoteDataSource<T>
    private let fallbackSource: LocalDataSource<T>
    private let logger: Logger

    func get(id: String) async throws -> T {
        do {
            // Пробуем основной источник
            return try await primarySource.fetch(id: id)
        } catch {
            logger.error("Primary source failed: \(error)")

            // Recovery strategy
            if let fallback = try? await fallbackSource.get(id: id) {
                logger.info("Fallback source succeeded")
                return fallback
            }

            // Обе попытки failed
            throw RepositoryError.entityNotFound(id: id)
        }
    }

    func getWithRecovery(
        id: String,
        maxAttempts: Int = 3
    ) async throws -> T {
        var lastError: Error?

        for attempt in 1...maxAttempts {
            do {
                return try await get(id: id)
            } catch {
                lastError = error
                logger.warning("Attempt \(attempt) failed: \(error)")

                if attempt < maxAttempts {
                    let delay = UInt64(attempt * 1_000_000_000) // 1s, 2s, 3s
                    try await Task.sleep(nanoseconds: delay)
                }
            }
        }

        throw lastError ?? RepositoryError.unknown(NSError(domain: "", code: -1))
    }
}
```

## Testing Repositories с Mocks

### Mock Data Sources

```swift
// Mock Remote Data Source
final class MockRemoteDataSource<T: Codable>: RemoteDataSource<T> {
    var fetchResult: Result<T, Error>?
    var fetchAllResult: Result<[T], Error>?
    var createResult: Result<T, Error>?

    var fetchCallCount = 0
    var fetchAllCallCount = 0
    var createCallCount = 0

    override func fetch(id: String) async throws -> T {
        fetchCallCount += 1

        guard let result = fetchResult else {
            throw MockError.notConfigured
        }

        switch result {
        case .success(let entity):
            return entity
        case .failure(let error):
            throw error
        }
    }

    override func fetchAll() async throws -> [T] {
        fetchAllCallCount += 1

        guard let result = fetchAllResult else {
            throw MockError.notConfigured
        }

        return try result.get()
    }

    override func create(_ entity: T) async throws -> T {
        createCallCount += 1

        guard let result = createResult else {
            throw MockError.notConfigured
        }

        return try result.get()
    }
}

// Mock Local Data Source
final class MockLocalDataSource<T: Codable & Identifiable>: LocalDataSource<T> {
    var storage: [String: T] = [:]

    override func get(id: String) async throws -> T {
        guard let entity = storage[id] else {
            throw RepositoryError.entityNotFound(id: id)
        }
        return entity
    }

    override func getAll() async throws -> [T] {
        Array(storage.values)
    }

    override func save(_ entity: T) async throws -> T {
        storage[entity.id as! String] = entity
        return entity
    }

    override func delete(id: String) async throws {
        storage.removeValue(forKey: id)
    }
}
```

### Unit Tests для Repository

```swift
import XCTest

final class UserRepositoryTests: XCTestCase {
    var sut: UserRepository!
    var mockRemote: MockRemoteDataSource<User>!
    var mockLocal: MockLocalDataSource<User>!
    var mockCache: MockCacheService!

    override func setUp() {
        super.setUp()
        mockRemote = MockRemoteDataSource<User>()
        mockLocal = MockLocalDataSource<User>()
        mockCache = MockCacheService()

        sut = UserRepository(
            remoteDataSource: mockRemote,
            localDataSource: mockLocal,
            cacheService: mockCache
        )
    }

    // Test: Cache hit
    func testGetUser_WhenCacheHit_ReturnsFromCache() async throws {
        // Given
        let expectedUser = User(id: "1", name: "John")
        mockCache.storage["1"] = expectedUser

        // When
        let result = try await sut.getUser(id: "1")

        // Then
        XCTAssertEqual(result, expectedUser)
        XCTAssertEqual(mockRemote.fetchCallCount, 0, "Should not call remote")
        XCTAssertEqual(mockLocal.getCallCount, 0, "Should not call local")
    }

    // Test: Cache miss, local hit
    func testGetUser_WhenCacheMissLocalHit_ReturnsFromLocal() async throws {
        // Given
        let expectedUser = User(id: "1", name: "John")
        mockLocal.storage["1"] = expectedUser

        // When
        let result = try await sut.getUser(id: "1")

        // Then
        XCTAssertEqual(result, expectedUser)
        XCTAssertEqual(mockCache.storage["1"] as? User, expectedUser)
        XCTAssertEqual(mockRemote.fetchCallCount, 0)
    }

    // Test: Full miss, network fetch
    func testGetUser_WhenFullMiss_FetchesFromNetwork() async throws {
        // Given
        let expectedUser = User(id: "1", name: "John")
        mockRemote.fetchResult = .success(expectedUser)

        // When
        let result = try await sut.getUser(id: "1")

        // Then
        XCTAssertEqual(result, expectedUser)
        XCTAssertEqual(mockRemote.fetchCallCount, 1)
        XCTAssertEqual(mockLocal.storage["1"], expectedUser)
        XCTAssertNotNil(mockCache.storage["1"])
    }

    // Test: Network error with local fallback
    func testGetUser_WhenNetworkFailsWithLocalData_ReturnsLocal() async throws {
        // Given
        let localUser = User(id: "1", name: "John")
        mockLocal.storage["1"] = localUser
        mockRemote.fetchResult = .failure(NetworkError.noConnection)

        // When
        let result = try await sut.getUser(id: "1")

        // Then
        XCTAssertEqual(result, localUser)
    }

    // Test: Save optimistic update
    func testSaveUser_SavesLocallyFirst() async throws {
        // Given
        let user = User(id: "1", name: "John")
        mockRemote.createResult = .success(user)

        // When
        let result = try await sut.save(user)

        // Then
        XCTAssertEqual(result, user)
        XCTAssertEqual(mockLocal.storage["1"], user)
        XCTAssertEqual(mockRemote.createCallCount, 1)
    }
}
```

### Integration Tests

```swift
final class RepositoryIntegrationTests: XCTestCase {
    var sut: UserRepository!
    var testDataSource: TestDataSource!

    override func setUp() async throws {
        try await super.setUp()

        // Реальная Core Data in-memory store
        let container = NSPersistentContainer.inMemory()
        testDataSource = TestDataSource(container: container)

        sut = UserRepository(
            remoteDataSource: TestRemoteDataSource(),
            localDataSource: CoreDataUserDataSource(context: container.viewContext),
            cacheService: MemoryCache()
        )
    }

    func testFullSyncCycle() async throws {
        // Given
        let user = User(id: "1", name: "John")

        // When: Create
        let created = try await sut.save(user)

        // Then: Verify persistence
        let fetched = try await sut.getUser(id: "1")
        XCTAssertEqual(created, fetched)

        // When: Update
        var updated = fetched
        updated.name = "Jane"
        try await sut.update(updated)

        // Then: Verify update
        let refetched = try await sut.getUser(id: "1")
        XCTAssertEqual(refetched.name, "Jane")

        // When: Delete
        try await sut.delete(id: "1")

        // Then: Verify deletion
        await XCTAssertThrowsError(
            try await sut.getUser(id: "1")
        ) { error in
            XCTAssertTrue(error is RepositoryError)
        }
    }
}
```

## Диаграммы

### Repository Architecture Flow

```
┌────────────────────────────────────────────────────────┐
│                     Presentation Layer                  │
│                  (SwiftUI Views, ViewModels)            │
└──────────────────────┬─────────────────────────────────┘
                       │
                       │ Protocol Interface
                       ▼
┌────────────────────────────────────────────────────────┐
│                  Repository Layer (SSOT)                │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Cache Strategy Coordinator               │  │
│  └──────────────────────────────────────────────────┘  │
│           │              │              │               │
│           ▼              ▼              ▼               │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐      │
│  │   Memory    │ │    Disk     │ │   Remote    │      │
│  │   Cache     │ │   Storage   │ │     API     │      │
│  │  (NSCache)  │ │ (Core Data) │ │(URLSession) │      │
│  └─────────────┘ └─────────────┘ └─────────────┘      │
└────────────────────────────────────────────────────────┘
                       │
                       │ Data Models
                       ▼
┌────────────────────────────────────────────────────────┐
│                      Data Layer                         │
│        (Network, Database, File System)                 │
└────────────────────────────────────────────────────────┘
```

### Sync State Machine

```
                    ┌─────────┐
                    │  IDLE   │
                    └────┬────┘
                         │
            User Action  │
                         ▼
                  ┌──────────────┐
                  │   PENDING    │◄──┐
                  │ (Queue Write)│   │
                  └──────┬───────┘   │
                         │           │
         Network Available           │ Network Unavailable
                         │           │
                         ▼           │
                  ┌──────────────┐  │
                  │   SYNCING    │  │
                  │ (API Request)│  │
                  └──────┬───────┘  │
                         │           │
              ┌──────────┴──────────┐
              │                     │
           Success               Failure
              │                     │
              ▼                     ▼
      ┌────────────┐        ┌────────────┐
      │  SYNCED    │        │   RETRY    │──┘
      │ (Complete) │        │ (Backoff)  │
      └────────────┘        └────────────┘
```

## 6 Common Mistakes

### Mistake 1: Прямой доступ к источникам данных

```swift
// ❌ Неправильно: ViewModel напрямую обращается к API и БД
class UserViewModel: ObservableObject {
    @Published var user: User?

    private let apiService: APIService
    private let database: CoreDataManager

    func loadUser(id: String) async {
        // Где правда? В API или БД?
        if let cached = database.fetchUser(id: id) {
            user = cached
        }

        if let remote = try? await apiService.fetchUser(id: id) {
            user = remote
            database.save(user: remote)
        }
    }
}

// ✅ Правильно: Repository инкапсулирует логику источников
class UserViewModel: ObservableObject {
    @Published var user: User?

    private let repository: UserRepositoryProtocol

    func loadUser(id: String) async {
        // Repository сам определяет стратегию
        user = try? await repository.getUser(id: id)
    }
}

final class UserRepository: UserRepositoryProtocol {
    func getUser(id: String) async throws -> User {
        // Централизованная логика кэширования
        if let cached = cache.get(User.self, key: id) {
            return cached
        }

        if let local = try? await localStorage.get(id: id) {
            cache.set(local, key: id)
            return local
        }

        let remote = try await remoteAPI.fetch(id: id)
        cache.set(remote, key: id)
        try? await localStorage.save(remote)
        return remote
    }
}
```

### Mistake 2: Отсутствие error handling при синхронизации

```swift
// ❌ Неправильно: Игнорирование ошибок сети
func save(user: User) async throws {
    try await localDatabase.save(user)
    try await remoteAPI.create(user) // Crash при offline!
}

// ✅ Правильно: Graceful degradation с offline queue
func save(user: User) async throws -> User {
    // Optimistic save
    let saved = try await localDatabase.save(user)

    // Пытаемся синхронизировать
    do {
        let remote = try await remoteAPI.create(user)
        try await localDatabase.update(remote)
        return remote
    } catch {
        // Добавляем в очередь синхронизации
        await syncQueue.enqueue(
            operation: .create,
            entity: user,
            error: error
        )

        // Возвращаем локальную версию
        return saved
    }
}
```

### Mistake 3: Race conditions при параллельных запросах

```swift
// ❌ Неправильно: Множественные одновременные запросы
func getUser(id: String) async throws -> User {
    return try await remoteAPI.fetch(id: id)
}

// Если вызвать 10 раз одновременно → 10 сетевых запросов!

// ✅ Правильно: Дедупликация с помощью Task dictionary
actor UserRepository {
    private var activeRequests: [String: Task<User, Error>] = [:]

    func getUser(id: String) async throws -> User {
        // Если запрос уже идет — возвращаем его
        if let existingTask = activeRequests[id] {
            return try await existingTask.value
        }

        // Создаем новый запрос
        let task = Task<User, Error> {
            defer { activeRequests.removeValue(forKey: id) }

            let user = try await remoteAPI.fetch(id: id)
            await cache.set(user, key: id)
            return user
        }

        activeRequests[id] = task
        return try await task.value
    }
}
```

### Mistake 4: Не учитываем TTL кэша

```swift
// ❌ Неправильно: Кэш без срока жизни
class SimpleCache {
    private var storage: [String: Any] = [:]

    func get<T>(key: String) -> T? {
        storage[key] as? T // Может быть устаревшим!
    }
}

// ✅ Правильно: Кэш с TTL и автоматической инвалидацией
class TTLCache {
    struct CacheEntry {
        let value: Any
        let expirationDate: Date

        var isExpired: Bool {
            Date() > expirationDate
        }
    }

    private var storage: [String: CacheEntry] = [:]
    private let defaultTTL: TimeInterval = 300 // 5 минут

    func get<T>(_ type: T.Type, key: String) -> T? {
        guard let entry = storage[key], !entry.isExpired else {
            storage.removeValue(forKey: key)
            return nil
        }
        return entry.value as? T
    }

    func set<T>(_ value: T, key: String, ttl: TimeInterval? = nil) {
        let expirationDate = Date().addingTimeInterval(ttl ?? defaultTTL)
        storage[key] = CacheEntry(value: value, expirationDate: expirationDate)
    }
}
```

### Mistake 5: Блокировка UI при первом запросе

```swift
// ❌ Неправильно: Ждем сеть, блокируя UI
func loadUsers() async {
    isLoading = true
    users = try? await repository.getAll() // Долгий запрос
    isLoading = false
}

// ✅ Правильно: Stale-While-Revalidate паттерн
func loadUsers() async {
    // Показываем кэш немедленно
    if let cached = await repository.getCachedUsers() {
        users = cached
        isLoading = false
    } else {
        isLoading = true
    }

    // Обновляем в фоне
    do {
        let fresh = try await repository.refreshUsers()
        users = fresh
        isLoading = false
    } catch {
        // Оставляем кэшированные данные при ошибке
        if users.isEmpty {
            error = error
        }
        isLoading = false
    }
}

// Repository implementation
func getCachedUsers() async -> [User]? {
    try? await localStorage.getAll()
}

func refreshUsers() async throws -> [User] {
    let remote = try await remoteAPI.fetchAll()
    try await localStorage.saveAll(remote)
    return remote
}
```

### Mistake 6: Нарушение Single Responsibility в Repository

```swift
// ❌ Неправильно: Repository делает всё подряд
class GodRepository {
    func getUser(id: String) async throws -> User { ... }
    func validateUser(_ user: User) -> Bool { ... } // Validation
    func formatUserName(_ user: User) -> String { ... } // Formatting
    func sendAnalytics(event: String) { ... } // Analytics
    func showUserProfile(_ user: User) { ... } // Presentation
}

// ✅ Правильно: Разделение ответственности
// Repository — только данные
protocol UserRepositoryProtocol {
    func getUser(id: String) async throws -> User
    func saveUser(_ user: User) async throws
    func deleteUser(id: String) async throws
}

// Validation — отдельный сервис
protocol UserValidatorProtocol {
    func validate(_ user: User) throws
}

// Formatting — отдельный презентер
protocol UserPresenterProtocol {
    func format(_ user: User) -> UserViewModel
}

// Использование
class UserService {
    private let repository: UserRepositoryProtocol
    private let validator: UserValidatorProtocol
    private let presenter: UserPresenterProtocol

    func createUser(_ user: User) async throws -> UserViewModel {
        try validator.validate(user)
        let saved = try await repository.saveUser(user)
        return presenter.format(saved)
    }
}
```

## Best Practices

### 1. Repository Guidelines
- Один Repository на один тип Entity
- Используйте протоколы для тестируемости
- Repository не содержит бизнес-логику
- Возвращайте domain models, а не DTO
- Всегда обрабатывайте ошибки gracefully

### 2. Caching Strategy
- Memory cache для hot data (часто используемые)
- Disk cache для persistent data
- Network только когда необходимо
- Устанавливайте разумный TTL (5-15 минут)
- Инвалидируйте кэш при изменениях

### 3. Offline Support
- Optimistic updates для лучшего UX
- Sync queue для pending operations
- Конфликт-резолюшн стратегия
- Background sync при появлении сети
- Показывайте статус синхронизации

### 4. Performance
- Дедупликация параллельных запросов
- Lazy loading и pagination
- Background processing для тяжелых операций
- Используйте actor для thread-safety
- Профилируйте с Instruments

### 5. Testing
- Mock всех зависимостей
- Тестируйте cache hit/miss scenarios
- Проверяйте error handling paths
- Integration tests для критичных flows
- Измеряйте покрытие кодом (>80%)

## Related Patterns

- **Data Source Pattern** — абстракция над конкретными источниками данных
- **Unit of Work** — группировка операций в транзакции
- **Observer Pattern** — реактивное обновление данных (Combine, AsyncStream)
- **Strategy Pattern** — выбор cache strategy динамически
- **Command Pattern** — инкапсуляция операций для sync queue

## Связь с другими темами

**[[android-repository-pattern]]** — Android Repository Pattern (Google Architecture Components) стал стандартом де-факто благодаря официальным рекомендациям Google, в то время как в iOS-мире паттерн реализуется более свободно. Оба подхода разделяют ключевые принципы: SSOT через локальную базу данных, абстракция через протоколы/интерфейсы, многоуровневое кэширование. Сравнение помогает перенять лучшие практики (Flow/LiveData vs Combine/AsyncStream для реактивных данных) и унифицировать data layer в KMP-проектах.

**[[ios-architecture-patterns]]** — Repository является частью data layer в Clean Architecture и связующим звеном между domain и infrastructure слоями. В MVVM Repository предоставляет данные для ViewModel, в VIPER — для Interactor-а. Без понимания архитектурных паттернов сложно определить правильные границы ответственности Repository. Рекомендуется сначала освоить архитектурные паттерны, затем реализовывать Repository как часть data layer.

**[[ios-data-persistence]]** — Repository инкапсулирует работу с различными механизмами хранения данных (Core Data, SwiftData, UserDefaults, Keychain, файловая система). Понимание persistence-механизмов необходимо для правильной реализации local data source внутри Repository, включая выбор стратегии кэширования (in-memory vs persistent) и настройку TTL для устаревания данных.

---

## Источники и дальнейшее чтение

### Книги
- Keur C., Hillegass A. (2020). *iOS Programming: Big Nerd Ranch Guide.* — демонстрирует построение data layer с разделением на network и persistence слои, что является основой для Repository Pattern; практические примеры с Core Data и URLSession.
- Neuburg M. (2023). *iOS 17 Programming Fundamentals with Swift.* — описывает протокол-ориентированное программирование, которое является основой для абстрагирования Repository через протоколы, а также работу с Codable для маппинга DTO в domain models.
- Eidhof C. et al. (2019). *Advanced Swift.* — глубокое погружение в generics, associated types и protocol composition, которые активно используются при проектировании гибких Repository-интерфейсов.

---

**Keywords:** iOS, Swift, Repository Pattern, SSOT, Clean Architecture, Caching, Offline-First, Data Layer, Combine, Async/Await, Testing, Protocol-Oriented Programming
