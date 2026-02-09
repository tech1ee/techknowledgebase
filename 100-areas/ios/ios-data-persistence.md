---
title: "iOS Data Persistence"
created: 2026-01-11
tags: [ios, swift, data-persistence, storage, security, keychain, userdefaults]
status: active
---

# iOS Data Persistence

## TL;DR

iOS предоставляет несколько механизмов хранения данных: **UserDefaults** для простых настроек, **FileManager** для файловой системы, **Keychain** для безопасного хранения секретов, **PropertyList** для структурированных данных, **iCloud KVS** для синхронизации между устройствами. Каждый инструмент имеет свои ограничения по размеру, безопасности и производительности. Ключевое правило: используйте Keychain для паролей/токенов, UserDefaults для настроек (< 1MB), FileManager для больших данных, и всегда учитывайте File Protection для защиты данных пользователя.

**Аналогия**: Представьте хранение данных как организацию офиса:
- **UserDefaults** — стикеры на мониторе (быстрый доступ к заметкам)
- **FileManager** — шкаф с папками (организованное хранение документов)
- **Keychain** — сейф (защищённое хранение ценностей)
- **iCloud KVS** — доска объявлений с синхронизацией между офисами
- **App Groups** — общая переговорная комната (доступ для нескольких сотрудников)

## Архитектура хранения данных

```
┌─────────────────────────────────────────────────────────────┐
│                    iOS App Sandbox                          │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Documents/  │  │   Library/   │  │     tmp/     │      │
│  │              │  │              │  │              │      │
│  │ User-created │  │ Preferences/ │  │  Temporary   │      │
│  │    files     │  │  Caches/     │  │    files     │      │
│  │ (backed up)  │  │Application   │  │ (auto-clean) │      │
│  │              │  │   Support/   │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              UserDefaults Storage                    │  │
│  │  (Library/Preferences/[BundleID].plist)             │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ├─── Shared Container (App Groups)
                           │
                           ├─── Keychain (outside sandbox)
                           │    ┌──────────────────────────┐
                           │    │  Encrypted Secure Store  │
                           │    │  - Passwords             │
                           │    │  - Tokens                │
                           │    │  - Certificates          │
                           │    └──────────────────────────┘
                           │
                           └─── iCloud
                                ┌──────────────────────────┐
                                │  Key-Value Storage       │
                                │  (max 1MB)               │
                                │  CloudKit                │
                                │  iCloud Drive            │
                                └──────────────────────────┘
```

## 1. UserDefaults

### Основы

UserDefaults — простое key-value хранилище для пользовательских настроек, работает на основе Property List файлов.

**Ограничения:**
- Максимальный размер: ~4MB (технически нет лимита, но при > 1MB возникают проблемы с производительностью)
- Синхронный API (блокирует главный поток)
- Не зашифровано (не для чувствительных данных)
- Не поддерживает сложные типы данных напрямую

```swift
import Foundation

// Базовое использование
class UserSettingsManager {
    private let defaults = UserDefaults.standard

    // Простые типы
    func saveUsername(_ name: String) {
        defaults.set(name, forKey: "username")
    }

    func getUsername() -> String? {
        return defaults.string(forKey: "username")
    }

    // Все поддерживаемые типы
    func saveSettings() {
        defaults.set("John Doe", forKey: "name")              // String
        defaults.set(25, forKey: "age")                       // Int
        defaults.set(3.14, forKey: "pi")                      // Double
        defaults.set(true, forKey: "isEnabled")               // Bool
        defaults.set(Date(), forKey: "lastLogin")             // Date
        defaults.set(["a", "b", "c"], forKey: "tags")        // Array
        defaults.set(["key": "value"], forKey: "metadata")   // Dictionary
        defaults.set(Data(), forKey: "rawData")              // Data
    }

    // Удаление
    func clearUsername() {
        defaults.removeObject(forKey: "username")
    }

    // Проверка существования
    func hasUsername() -> Bool {
        return defaults.object(forKey: "username") != nil
    }
}
```

### Property Wrappers для UserDefaults

Современный подход с использованием property wrappers для типобезопасного доступа:

```swift
import Foundation

@propertyWrapper
struct UserDefault<T> {
    let key: String
    let defaultValue: T
    var container: UserDefaults = .standard

    var wrappedValue: T {
        get {
            return container.object(forKey: key) as? T ?? defaultValue
        }
        set {
            container.set(newValue, forKey: key)
        }
    }
}

// Расширенная версия с поддержкой Codable
@propertyWrapper
struct CodableUserDefault<T: Codable> {
    let key: String
    let defaultValue: T
    var container: UserDefaults = .standard

    var wrappedValue: T {
        get {
            guard let data = container.data(forKey: key),
                  let value = try? JSONDecoder().decode(T.self, from: data) else {
                return defaultValue
            }
            return value
        }
        set {
            let data = try? JSONEncoder().encode(newValue)
            container.set(data, forKey: key)
        }
    }
}

// Использование
struct AppSettings {
    @UserDefault(key: "username", defaultValue: "Guest")
    static var username: String

    @UserDefault(key: "isDarkMode", defaultValue: false)
    static var isDarkMode: Bool

    @UserDefault(key: "fontSize", defaultValue: 14.0)
    static var fontSize: Double

    @UserDefault(key: "notifications", defaultValue: true)
    static var notificationsEnabled: Bool
}

// Для сложных типов
struct User: Codable {
    let id: String
    let name: String
    let email: String
}

struct UserSession {
    @CodableUserDefault(key: "currentUser", defaultValue: User(id: "", name: "", email: ""))
    static var currentUser: User

    @CodableUserDefault(key: "recentSearches", defaultValue: [])
    static var recentSearches: [String]
}

// Пример использования
func exampleUsage() {
    // Чтение
    print(AppSettings.username)           // "Guest"
    print(AppSettings.isDarkMode)         // false

    // Запись
    AppSettings.username = "John"
    AppSettings.isDarkMode = true

    // Сложные типы
    UserSession.currentUser = User(id: "123", name: "Jane", email: "jane@example.com")
    UserSession.recentSearches = ["iOS", "Swift", "SwiftUI"]
}
```

### Продвинутое использование

```swift
import Foundation
import Combine

// Reactive UserDefaults с Combine
@propertyWrapper
struct PublishedUserDefault<T> {
    let key: String
    let defaultValue: T
    var container: UserDefaults = .standard

    private let publisher = PassthroughSubject<T, Never>()

    var wrappedValue: T {
        get {
            return container.object(forKey: key) as? T ?? defaultValue
        }
        set {
            container.set(newValue, forKey: key)
            publisher.send(newValue)
        }
    }

    var projectedValue: AnyPublisher<T, Never> {
        return publisher.eraseToAnyPublisher()
    }
}

// Наблюдение за изменениями
class SettingsObserver {
    private var cancellables = Set<AnyCancellable>()

    @PublishedUserDefault(key: "theme", defaultValue: "light")
    var theme: String

    init() {
        // Подписка на изменения
        $theme
            .sink { newTheme in
                print("Theme changed to: \(newTheme)")
            }
            .store(in: &cancellables)
    }
}

// Группировка настроек
extension UserDefaults {
    // Использование App Groups
    static let shared = UserDefaults(suiteName: "group.com.example.app")!

    // Разделение по категориям
    enum Keys {
        static let username = "username"
        static let theme = "theme"
        static let notifications = "notifications"
    }
}

// Миграция версий настроек
class SettingsMigration {
    static func migrate() {
        let currentVersion = UserDefaults.standard.integer(forKey: "settingsVersion")

        if currentVersion < 1 {
            // Миграция с версии 0 на 1
            migrateToV1()
        }

        if currentVersion < 2 {
            // Миграция с версии 1 на 2
            migrateToV2()
        }

        UserDefaults.standard.set(2, forKey: "settingsVersion")
    }

    private static func migrateToV1() {
        // Переименование ключей
        if let oldValue = UserDefaults.standard.string(forKey: "old_username") {
            UserDefaults.standard.set(oldValue, forKey: "username")
            UserDefaults.standard.removeObject(forKey: "old_username")
        }
    }

    private static func migrateToV2() {
        // Изменение формата данных
        if let oldTheme = UserDefaults.standard.string(forKey: "theme"),
           oldTheme == "0" {
            UserDefaults.standard.set("light", forKey: "theme")
        }
    }
}
```

## 2. FileManager

### Основы работы с файлами

```swift
import Foundation

class FileStorageManager {
    private let fileManager = FileManager.default

    // Получение путей к директориям
    func getDocumentsDirectory() -> URL {
        return fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }

    func getLibraryDirectory() -> URL {
        return fileManager.urls(for: .libraryDirectory, in: .userDomainMask)[0]
    }

    func getCachesDirectory() -> URL {
        return fileManager.urls(for: .cachesDirectory, in: .userDomainMask)[0]
    }

    func getTemporaryDirectory() -> URL {
        return fileManager.temporaryDirectory
    }

    // Запись файла
    func writeFile(data: Data, filename: String, directory: FileDirectory = .documents) throws {
        let directoryURL = getDirectoryURL(for: directory)
        let fileURL = directoryURL.appendingPathComponent(filename)

        try data.write(to: fileURL, options: [.atomic, .completeFileProtection])
    }

    // Чтение файла
    func readFile(filename: String, directory: FileDirectory = .documents) throws -> Data {
        let directoryURL = getDirectoryURL(for: directory)
        let fileURL = directoryURL.appendingPathComponent(filename)

        return try Data(contentsOf: fileURL)
    }

    // Удаление файла
    func deleteFile(filename: String, directory: FileDirectory = .documents) throws {
        let directoryURL = getDirectoryURL(for: directory)
        let fileURL = directoryURL.appendingPathComponent(filename)

        try fileManager.removeItem(at: fileURL)
    }

    // Проверка существования
    func fileExists(filename: String, directory: FileDirectory = .documents) -> Bool {
        let directoryURL = getDirectoryURL(for: directory)
        let fileURL = directoryURL.appendingPathComponent(filename)

        return fileManager.fileExists(atPath: fileURL.path)
    }

    // Создание директории
    func createDirectory(name: String, in directory: FileDirectory = .documents) throws {
        let directoryURL = getDirectoryURL(for: directory)
        let newDirectoryURL = directoryURL.appendingPathComponent(name)

        try fileManager.createDirectory(
            at: newDirectoryURL,
            withIntermediateDirectories: true,
            attributes: nil
        )
    }

    // Список файлов
    func listFiles(in directory: FileDirectory = .documents) throws -> [String] {
        let directoryURL = getDirectoryURL(for: directory)
        let contents = try fileManager.contentsOfDirectory(atPath: directoryURL.path)
        return contents
    }

    // Размер файла
    func getFileSize(filename: String, directory: FileDirectory = .documents) throws -> Int64 {
        let directoryURL = getDirectoryURL(for: directory)
        let fileURL = directoryURL.appendingPathComponent(filename)

        let attributes = try fileManager.attributesOfItem(atPath: fileURL.path)
        return attributes[.size] as? Int64 ?? 0
    }

    // Копирование файла
    func copyFile(from source: String, to destination: String, directory: FileDirectory = .documents) throws {
        let directoryURL = getDirectoryURL(for: directory)
        let sourceURL = directoryURL.appendingPathComponent(source)
        let destinationURL = directoryURL.appendingPathComponent(destination)

        try fileManager.copyItem(at: sourceURL, to: destinationURL)
    }

    // Перемещение файла
    func moveFile(from source: String, to destination: String, directory: FileDirectory = .documents) throws {
        let directoryURL = getDirectoryURL(for: directory)
        let sourceURL = directoryURL.appendingPathComponent(source)
        let destinationURL = directoryURL.appendingPathComponent(destination)

        try fileManager.moveItem(at: sourceURL, to: destinationURL)
    }

    private func getDirectoryURL(for directory: FileDirectory) -> URL {
        switch directory {
        case .documents:
            return getDocumentsDirectory()
        case .library:
            return getLibraryDirectory()
        case .caches:
            return getCachesDirectory()
        case .temporary:
            return getTemporaryDirectory()
        }
    }
}

enum FileDirectory {
    case documents
    case library
    case caches
    case temporary
}

// Пример использования
func fileManagerExample() {
    let storage = FileStorageManager()

    do {
        // Запись
        let data = "Hello, World!".data(using: .utf8)!
        try storage.writeFile(data: data, filename: "greeting.txt")

        // Чтение
        let readData = try storage.readFile(filename: "greeting.txt")
        let text = String(data: readData, encoding: .utf8)
        print(text ?? "")

        // Проверка существования
        if storage.fileExists(filename: "greeting.txt") {
            print("File exists")
        }

        // Удаление
        try storage.deleteFile(filename: "greeting.txt")

    } catch {
        print("Error: \(error)")
    }
}
```

### Работа с JSON файлами

```swift
import Foundation

struct JSONFileManager<T: Codable> {
    private let fileManager = FileManager.default
    private let encoder = JSONEncoder()
    private let decoder = JSONDecoder()

    init() {
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601
        decoder.dateDecodingStrategy = .iso8601
    }

    // Сохранение объекта в JSON
    func save(_ object: T, to filename: String, in directory: URL) throws {
        let fileURL = directory.appendingPathComponent(filename)
        let data = try encoder.encode(object)
        try data.write(to: fileURL, options: [.atomic, .completeFileProtection])
    }

    // Загрузка объекта из JSON
    func load(from filename: String, in directory: URL) throws -> T {
        let fileURL = directory.appendingPathComponent(filename)
        let data = try Data(contentsOf: fileURL)
        return try decoder.decode(T.self, from: data)
    }

    // Асинхронное сохранение
    func saveAsync(_ object: T, to filename: String, in directory: URL) async throws {
        let fileURL = directory.appendingPathComponent(filename)
        let data = try encoder.encode(object)
        try await Task.detached {
            try data.write(to: fileURL, options: [.atomic, .completeFileProtection])
        }.value
    }

    // Асинхронная загрузка
    func loadAsync(from filename: String, in directory: URL) async throws -> T {
        let fileURL = directory.appendingPathComponent(filename)
        return try await Task.detached {
            let data = try Data(contentsOf: fileURL)
            return try self.decoder.decode(T.self, from: data)
        }.value
    }
}

// Пример использования
struct UserProfile: Codable {
    let id: String
    let name: String
    let email: String
    let createdAt: Date
}

func jsonFileExample() async {
    let jsonManager = JSONFileManager<UserProfile>()
    let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]

    let profile = UserProfile(
        id: "123",
        name: "John Doe",
        email: "john@example.com",
        createdAt: Date()
    )

    do {
        // Сохранение
        try await jsonManager.saveAsync(profile, to: "profile.json", in: documentsURL)

        // Загрузка
        let loadedProfile = try await jsonManager.loadAsync(from: "profile.json", in: documentsURL)
        print(loadedProfile.name)

    } catch {
        print("Error: \(error)")
    }
}
```

## 3. Директории: Documents vs Library vs tmp

### Сравнение директорий

```
┌────────────────────────────────────────────────────────────────┐
│                     App Sandbox Structure                      │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  Documents/                                                    │
│  ├─ user_photo.jpg          ← Пользовательский контент       │
│  ├─ document.pdf            ← Backup: YES                     │
│  └─ notes.txt               ← Видно в Files app               │
│                                                                │
│  Library/                                                      │
│  ├─ Application Support/    ← Данные приложения               │
│  │  ├─ database.sqlite      ← Backup: YES                     │
│  │  └─ config.json          ← НЕ видно пользователю           │
│  ├─ Caches/                 ← Кэш данных                      │
│  │  ├─ image_cache/         ← Backup: NO                      │
│  │  └─ api_responses/       ← Может быть удалено системой     │
│  └─ Preferences/            ← UserDefaults хранятся здесь     │
│     └─ [BundleID].plist                                        │
│                                                                │
│  tmp/                       ← Временные файлы                 │
│  ├─ upload_temp.dat         ← Backup: NO                      │
│  └─ processing.tmp          ← Удаляется при нехватке места    │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

### Рекомендации по использованию

```swift
import Foundation

class DirectoryManager {
    static let shared = DirectoryManager()
    private let fileManager = FileManager.default

    // Documents: Пользовательские файлы, которые должны быть видны пользователю
    // - Сохраняется в iCloud/iTunes backup
    // - Видно в Files app (если включено)
    // Примеры: PDF документы, изображения, экспортированные данные
    var documentsDirectory: URL {
        fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }

    // Library/Application Support: Данные приложения, невидимые пользователю
    // - Сохраняется в backup
    // - Для баз данных, конфигураций, загруженного контента
    // Примеры: SQLite БД, Core Data, ML модели
    var applicationSupportDirectory: URL {
        let library = fileManager.urls(for: .libraryDirectory, in: .userDomainMask)[0]
        let appSupport = library.appendingPathComponent("Application Support")

        // Создаём директорию, если не существует
        try? fileManager.createDirectory(at: appSupport, withIntermediateDirectories: true)
        return appSupport
    }

    // Library/Caches: Кэш данных, которые можно восстановить
    // - НЕ сохраняется в backup
    // - Может быть удалено системой при нехватке места
    // - Нужно устанавливать атрибут "do not backup"
    // Примеры: Кэш изображений, API ответы, офлайн контент
    var cachesDirectory: URL {
        fileManager.urls(for: .cachesDirectory, in: .userDomainMask)[0]
    }

    // tmp/: Временные файлы
    // - НЕ сохраняется в backup
    // - Удаляется системой периодически
    // - Приложение должно очищать самостоятельно
    // Примеры: Временные загрузки, обработка файлов
    var temporaryDirectory: URL {
        fileManager.temporaryDirectory
    }

    // Установка атрибута "exclude from backup"
    func excludeFromBackup(url: URL) throws {
        var resourceURL = url
        var resourceValues = URLResourceValues()
        resourceValues.isExcludedFromBackup = true
        try resourceURL.setResourceValues(resourceValues)
    }

    // Очистка кэша
    func clearCaches() throws {
        let cacheContents = try fileManager.contentsOfDirectory(
            at: cachesDirectory,
            includingPropertiesForKeys: nil
        )

        for fileURL in cacheContents {
            try fileManager.removeItem(at: fileURL)
        }
    }

    // Очистка временных файлов
    func clearTemporaryFiles() throws {
        let tmpContents = try fileManager.contentsOfDirectory(
            at: temporaryDirectory,
            includingPropertiesForKeys: nil
        )

        for fileURL in tmpContents {
            try fileManager.removeItem(at: fileURL)
        }
    }

    // Получение размера директории
    func getDirectorySize(_ directory: URL) throws -> Int64 {
        var totalSize: Int64 = 0

        guard let enumerator = fileManager.enumerator(
            at: directory,
            includingPropertiesForKeys: [.fileSizeKey],
            options: [.skipsHiddenFiles]
        ) else {
            return 0
        }

        for case let fileURL as URL in enumerator {
            let attributes = try fileManager.attributesOfItem(atPath: fileURL.path)
            totalSize += attributes[.size] as? Int64 ?? 0
        }

        return totalSize
    }
}

// Практические примеры использования
class FileStorageExamples {
    private let dirManager = DirectoryManager.shared

    // Сохранение пользовательского документа
    func saveUserDocument(data: Data, filename: String) throws {
        let fileURL = dirManager.documentsDirectory.appendingPathComponent(filename)
        try data.write(to: fileURL, options: .completeFileProtection)
    }

    // Сохранение базы данных
    func saveDatabaseFile(data: Data, filename: String) throws {
        let fileURL = dirManager.applicationSupportDirectory.appendingPathComponent(filename)
        try data.write(to: fileURL, options: .completeFileProtection)
    }

    // Сохранение кэша изображения
    func cacheImage(data: Data, filename: String) throws {
        let fileURL = dirManager.cachesDirectory.appendingPathComponent(filename)
        try data.write(to: fileURL)

        // Исключаем из backup
        try dirManager.excludeFromBackup(url: fileURL)
    }

    // Временная обработка файла
    func processTemporaryFile(data: Data) throws -> URL {
        let tempURL = dirManager.temporaryDirectory
            .appendingPathComponent(UUID().uuidString)
            .appendingPathExtension("tmp")

        try data.write(to: tempURL)
        return tempURL
    }
}
```

## 4. App Groups для обмена данными

App Groups позволяют нескольким приложениям (основное приложение, виджеты, расширения) обмениваться данными.

```swift
import Foundation

// Настройка в Xcode:
// 1. Capabilities → App Groups → включить
// 2. Создать группу: group.com.example.appname
// 3. Добавить ту же группу для всех таргетов (app, widget, extension)

class SharedDataManager {
    // Shared UserDefaults
    static let sharedDefaults = UserDefaults(suiteName: "group.com.example.appname")!

    // Shared Container Directory
    static let sharedContainerURL: URL? = {
        return FileManager.default.containerURL(
            forSecurityApplicationGroupIdentifier: "group.com.example.appname"
        )
    }()

    // Сохранение данных для виджета
    func saveDataForWidget<T: Codable>(_ data: T, key: String) throws {
        let encoder = JSONEncoder()
        let encoded = try encoder.encode(data)
        SharedDataManager.sharedDefaults.set(encoded, forKey: key)
    }

    // Чтение данных из виджета
    func loadDataFromWidget<T: Codable>(key: String, type: T.Type) throws -> T? {
        guard let data = SharedDataManager.sharedDefaults.data(forKey: key) else {
            return nil
        }

        let decoder = JSONDecoder()
        return try decoder.decode(T.self, from: data)
    }

    // Сохранение файла в shared container
    func saveSharedFile(data: Data, filename: String) throws {
        guard let containerURL = SharedDataManager.sharedContainerURL else {
            throw SharedDataError.containerNotFound
        }

        let fileURL = containerURL.appendingPathComponent(filename)
        try data.write(to: fileURL, options: [.atomic, .completeFileProtection])
    }

    // Чтение файла из shared container
    func loadSharedFile(filename: String) throws -> Data {
        guard let containerURL = SharedDataManager.sharedContainerURL else {
            throw SharedDataError.containerNotFound
        }

        let fileURL = containerURL.appendingPathComponent(filename)
        return try Data(contentsOf: fileURL)
    }

    // Координация доступа к файлам (NSFileCoordinator)
    func coordinatedReadSharedFile(filename: String) throws -> Data {
        guard let containerURL = SharedDataManager.sharedContainerURL else {
            throw SharedDataError.containerNotFound
        }

        let fileURL = containerURL.appendingPathComponent(filename)
        let coordinator = NSFileCoordinator(filePresenter: nil)
        var error: NSError?
        var resultData: Data?

        coordinator.coordinate(readingItemAt: fileURL, options: [], error: &error) { url in
            resultData = try? Data(contentsOf: url)
        }

        if let error = error {
            throw error
        }

        guard let data = resultData else {
            throw SharedDataError.fileNotFound
        }

        return data
    }

    // Координированная запись
    func coordinatedWriteSharedFile(data: Data, filename: String) throws {
        guard let containerURL = SharedDataManager.sharedContainerURL else {
            throw SharedDataError.containerNotFound
        }

        let fileURL = containerURL.appendingPathComponent(filename)
        let coordinator = NSFileCoordinator(filePresenter: nil)
        var error: NSError?

        coordinator.coordinate(writingItemAt: fileURL, options: [], error: &error) { url in
            try? data.write(to: url, options: [.atomic, .completeFileProtection])
        }

        if let error = error {
            throw error
        }
    }
}

enum SharedDataError: Error {
    case containerNotFound
    case fileNotFound
    case encodingFailed
}

// Пример для виджета
struct WidgetData: Codable {
    let title: String
    let value: Int
    let updatedAt: Date
}

// В основном приложении
func updateWidgetData() {
    let manager = SharedDataManager()
    let data = WidgetData(
        title: "Tasks Completed",
        value: 42,
        updatedAt: Date()
    )

    do {
        try manager.saveDataForWidget(data, key: "widgetData")

        // Уведомить виджет об обновлении
        #if canImport(WidgetKit)
        import WidgetKit
        WidgetCenter.shared.reloadAllTimelines()
        #endif
    } catch {
        print("Error updating widget: \(error)")
    }
}

// В виджете
func loadWidgetData() -> WidgetData? {
    let manager = SharedDataManager()
    return try? manager.loadDataFromWidget(key: "widgetData", type: WidgetData.self)
}
```

## 5. Keychain для безопасного хранения

### Нативный Keychain API

```swift
import Security
import Foundation

class KeychainManager {

    // MARK: - Save Item

    func save(key: String, data: Data, accessibility: CFString = kSecAttrAccessibleWhenUnlocked) -> Bool {
        // Удаляем старое значение, если существует
        delete(key: key)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: accessibility
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }

    func save(key: String, value: String, accessibility: CFString = kSecAttrAccessibleWhenUnlocked) -> Bool {
        guard let data = value.data(using: .utf8) else { return false }
        return save(key: key, data: data, accessibility: accessibility)
    }

    // MARK: - Load Item

    func load(key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess else { return nil }
        return result as? Data
    }

    func loadString(key: String) -> String? {
        guard let data = load(key: key) else { return nil }
        return String(data: data, encoding: .utf8)
    }

    // MARK: - Update Item

    func update(key: String, data: Data) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let attributes: [String: Any] = [
            kSecValueData as String: data
        ]

        let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        return status == errSecSuccess
    }

    // MARK: - Delete Item

    func delete(key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }

    // MARK: - Delete All

    func deleteAll() -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword
        ]

        let status = SecItemDelete(query as CFDictionary)
        return status == errSecSuccess || status == errSecItemNotFound
    }
}

// Пример использования
func keychainExample() {
    let keychain = KeychainManager()

    // Сохранение токена
    let token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    keychain.save(key: "authToken", value: token)

    // Чтение токена
    if let savedToken = keychain.loadString(key: "authToken") {
        print("Token: \(savedToken)")
    }

    // Удаление токена
    keychain.delete(key: "authToken")
}
```

### Расширенный Keychain с поддержкой Codable

```swift
import Security
import Foundation

class SecureStorage {
    enum KeychainError: Error {
        case encodingFailed
        case decodingFailed
        case saveFailed(OSStatus)
        case loadFailed(OSStatus)
        case deleteFailed(OSStatus)
        case itemNotFound
    }

    // Сохранение Codable объекта
    func save<T: Codable>(_ item: T, key: String, accessibility: CFString = kSecAttrAccessibleWhenUnlocked) throws {
        let encoder = JSONEncoder()
        guard let data = try? encoder.encode(item) else {
            throw KeychainError.encodingFailed
        }

        // Удаляем старое значение
        try? delete(key: key)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: accessibility,
            kSecAttrSynchronizable as String: false  // Не синхронизировать через iCloud Keychain
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        guard status == errSecSuccess else {
            throw KeychainError.saveFailed(status)
        }
    }

    // Загрузка Codable объекта
    func load<T: Codable>(key: String, type: T.Type) throws -> T {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess else {
            if status == errSecItemNotFound {
                throw KeychainError.itemNotFound
            }
            throw KeychainError.loadFailed(status)
        }

        guard let data = result as? Data else {
            throw KeychainError.decodingFailed
        }

        let decoder = JSONDecoder()
        guard let item = try? decoder.decode(T.self, from: data) else {
            throw KeychainError.decodingFailed
        }

        return item
    }

    // Удаление
    func delete(key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)

        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.deleteFailed(status)
        }
    }

    // Проверка существования
    func exists(key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        let status = SecItemCopyMatching(query as CFDictionary, nil)
        return status == errSecSuccess
    }
}

// Структуры для хранения
struct AuthCredentials: Codable {
    let username: String
    let accessToken: String
    let refreshToken: String
    let expiresAt: Date
}

struct APIKeys: Codable {
    let apiKey: String
    let apiSecret: String
}

// Специализированный менеджер для аутентификации
class AuthenticationStorage {
    private let storage = SecureStorage()
    private let credentialsKey = "com.app.credentials"

    func saveCredentials(_ credentials: AuthCredentials) throws {
        try storage.save(
            credentials,
            key: credentialsKey,
            accessibility: kSecAttrAccessibleAfterFirstUnlock
        )
    }

    func loadCredentials() throws -> AuthCredentials {
        return try storage.load(key: credentialsKey, type: AuthCredentials.self)
    }

    func deleteCredentials() throws {
        try storage.delete(key: credentialsKey)
    }

    func hasValidCredentials() -> Bool {
        guard let credentials = try? loadCredentials() else {
            return false
        }

        return credentials.expiresAt > Date()
    }
}
```

### KeychainAccess библиотека (рекомендуемая)

```swift
// В Package.swift добавьте:
// .package(url: "https://github.com/kishikawakatsumi/KeychainAccess.git", from: "4.2.2")

import KeychainAccess

class SimpleKeychainManager {
    private let keychain = Keychain(service: "com.example.app")
        .synchronizable(false)  // Не синхронизировать через iCloud
        .accessibility(.afterFirstUnlock)  // Доступно после первой разблокировки

    // Простое использование
    func saveToken(_ token: String) {
        keychain["authToken"] = token
    }

    func loadToken() -> String? {
        return keychain["authToken"]
    }

    func deleteToken() {
        keychain["authToken"] = nil
    }

    // С обработкой ошибок
    func saveSecurely(key: String, value: String) throws {
        try keychain.set(value, key: key)
    }

    func loadSecurely(key: String) throws -> String? {
        return try keychain.get(key)
    }

    // Работа с Data
    func saveData(key: String, data: Data) throws {
        try keychain.set(data, key: key)
    }

    func loadData(key: String) throws -> Data? {
        return try keychain.getData(key)
    }

    // Удаление всех данных
    func clearAll() throws {
        try keychain.removeAll()
    }

    // Получение всех ключей
    func allKeys() -> [String] {
        return keychain.allKeys()
    }
}

// Разные уровни accessibility
class KeychainAccessibilityExamples {

    // Для чувствительных данных (требует разблокировки устройства)
    let secureKeychain = Keychain(service: "com.example.app.secure")
        .accessibility(.whenUnlockedThisDeviceOnly)

    // Для данных, доступных в фоне
    let backgroundKeychain = Keychain(service: "com.example.app.background")
        .accessibility(.afterFirstUnlock)

    // Для данных, синхронизируемых через iCloud
    let cloudKeychain = Keychain(service: "com.example.app.cloud")
        .synchronizable(true)
        .accessibility(.whenUnlocked)

    func demonstrateUsage() {
        // Сохранение пароля (только на этом устройстве)
        secureKeychain["password"] = "secret123"

        // Сохранение токена (доступен в фоне)
        backgroundKeychain["refreshToken"] = "token_abc123"

        // Сохранение настройки (синхронизация через iCloud)
        cloudKeychain["userPreference"] = "darkMode"
    }
}

// Группировка по приложениям (App Groups)
class SharedKeychainManager {
    private let keychain = Keychain(
        service: "com.example.app",
        accessGroup: "group.com.example.app"
    )

    func saveForWidget(key: String, value: String) {
        keychain[key] = value
    }

    func loadFromWidget(key: String) -> String? {
        return keychain[key]
    }
}
```

### Уровни File Protection

```swift
import Foundation

class FileProtectionManager {
    enum ProtectionLevel {
        case complete                    // Самая высокая защита
        case completeUnlessOpen         // Защита, но файл остаётся открытым
        case completeUntilFirstAuth     // После первой разблокировки
        case none                        // Нет защиты

        var attribute: FileProtectionType {
            switch self {
            case .complete:
                return .complete
            case .completeUnlessOpen:
                return .completeUnlessOpen
            case .completeUntilFirstAuth:
                return .completeUntilFirstUserAuthentication
            case .none:
                return .none
            }
        }
    }

    // Сохранение файла с защитой
    func saveSecureFile(data: Data, filename: String, protection: ProtectionLevel) throws {
        let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileURL = documentsURL.appendingPathComponent(filename)

        try data.write(to: fileURL, options: [.atomic, protection.attribute])
    }

    // Изменение уровня защиты существующего файла
    func setProtection(for filename: String, protection: ProtectionLevel) throws {
        let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileURL = documentsURL.appendingPathComponent(filename)

        try FileManager.default.setAttributes(
            [.protectionKey: protection.attribute],
            ofItemAtPath: fileURL.path
        )
    }

    // Проверка текущего уровня защиты
    func getProtection(for filename: String) throws -> FileProtectionType? {
        let documentsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileURL = documentsURL.appendingPathComponent(filename)

        let attributes = try FileManager.default.attributesOfItem(atPath: fileURL.path)
        return attributes[.protectionKey] as? FileProtectionType
    }
}

// Сравнение уровней защиты
/*
┌──────────────────────────────────────────────────────────────────┐
│                     File Protection Levels                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  .complete (NSFileProtectionComplete)                           │
│  ├─ Самая высокая защита                                        │
│  ├─ Файл зашифрован, когда устройство заблокировано            │
│  ├─ НЕ доступен в фоне после блокировки                        │
│  └─ Использование: Личные документы, медицинские данные         │
│                                                                  │
│  .completeUnlessOpen (NSFileProtectionCompleteUnlessOpen)       │
│  ├─ Файл остаётся доступным, если был открыт до блокировки     │
│  ├─ Можно дописывать данные в фоне                             │
│  └─ Использование: Логи, background uploads                     │
│                                                                  │
│  .completeUntilFirstUserAuthentication                          │
│  ├─ Защищён до первой разблокировки после перезагрузки         │
│  ├─ После этого доступен всегда (даже при блокировке)          │
│  └─ Использование: База данных, кэш для background fetch        │
│                                                                  │
│  .none (NSFileProtectionNone)                                   │
│  ├─ Нет защиты                                                  │
│  ├─ Всегда доступен                                             │
│  └─ Использование: Публичные данные, кэш изображений            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
*/
```

## 6. PropertyListEncoder/Decoder

```swift
import Foundation

// PropertyList (plist) — формат Apple для хранения структурированных данных
// Поддерживает: String, Number, Boolean, Date, Data, Array, Dictionary

class PropertyListStorage {
    private let fileManager = FileManager.default

    // Сохранение в plist (XML формат)
    func saveToXML<T: Encodable>(_ object: T, filename: String) throws {
        let encoder = PropertyListEncoder()
        encoder.outputFormat = .xml

        let data = try encoder.encode(object)
        let url = getDocumentsURL().appendingPathComponent(filename)

        try data.write(to: url, options: [.atomic, .completeFileProtection])
    }

    // Сохранение в plist (Binary формат) - меньший размер
    func saveToBinary<T: Encodable>(_ object: T, filename: String) throws {
        let encoder = PropertyListEncoder()
        encoder.outputFormat = .binary

        let data = try encoder.encode(object)
        let url = getDocumentsURL().appendingPathComponent(filename)

        try data.write(to: url, options: [.atomic, .completeFileProtection])
    }

    // Загрузка из plist
    func load<T: Decodable>(filename: String, type: T.Type) throws -> T {
        let url = getDocumentsURL().appendingPathComponent(filename)
        let data = try Data(contentsOf: url)

        let decoder = PropertyListDecoder()
        return try decoder.decode(T.self, from: data)
    }

    // Работа с NSDictionary (старый подход)
    func saveDictionary(_ dict: [String: Any], filename: String) throws {
        let url = getDocumentsURL().appendingPathComponent(filename)
        let plistData = try PropertyListSerialization.data(
            fromPropertyList: dict,
            format: .xml,
            options: 0
        )

        try plistData.write(to: url)
    }

    func loadDictionary(filename: String) throws -> [String: Any] {
        let url = getDocumentsURL().appendingPathComponent(filename)
        let data = try Data(contentsOf: url)

        guard let dict = try PropertyListSerialization.propertyList(
            from: data,
            options: [],
            format: nil
        ) as? [String: Any] else {
            throw PropertyListError.invalidFormat
        }

        return dict
    }

    private func getDocumentsURL() -> URL {
        return fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
}

enum PropertyListError: Error {
    case invalidFormat
}

// Пример структур для plist
struct AppConfiguration: Codable {
    let appName: String
    let version: String
    let features: [String]
    let settings: Settings

    struct Settings: Codable {
        let enableNotifications: Bool
        let maxCacheSize: Int
        let apiEndpoints: [String: String]
    }
}

func propertyListExample() {
    let storage = PropertyListStorage()

    let config = AppConfiguration(
        appName: "MyApp",
        version: "1.0.0",
        features: ["darkMode", "offline", "sync"],
        settings: AppConfiguration.Settings(
            enableNotifications: true,
            maxCacheSize: 100,
            apiEndpoints: [
                "production": "https://api.example.com",
                "staging": "https://staging.api.example.com"
            ]
        )
    )

    do {
        // Сохранение
        try storage.saveToXML(config, filename: "config.plist")

        // Загрузка
        let loadedConfig = try storage.load(filename: "config.plist", type: AppConfiguration.self)
        print(loadedConfig.appName)

    } catch {
        print("Error: \(error)")
    }
}
```

## 7. Архивирование: NSCoding vs Codable

### NSCoding (Legacy)

```swift
import Foundation

// Старый подход с NSCoding (Objective-C legacy)
class LegacyUser: NSObject, NSCoding {
    var id: String
    var name: String
    var age: Int

    init(id: String, name: String, age: Int) {
        self.id = id
        self.name = name
        self.age = age
    }

    // Кодирование
    func encode(with coder: NSCoder) {
        coder.encode(id, forKey: "id")
        coder.encode(name, forKey: "name")
        coder.encode(age, forKey: "age")
    }

    // Декодирование
    required init?(coder: NSCoder) {
        guard let id = coder.decodeObject(forKey: "id") as? String,
              let name = coder.decodeObject(forKey: "name") as? String else {
            return nil
        }

        self.id = id
        self.name = name
        self.age = coder.decodeInteger(forKey: "age")
    }
}

// Использование NSKeyedArchiver
func legacyArchiving() {
    let user = LegacyUser(id: "123", name: "John", age: 30)

    do {
        // Архивирование
        let data = try NSKeyedArchiver.archivedData(
            withRootObject: user,
            requiringSecureCoding: false
        )

        // Сохранение
        let url = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("user.archive")
        try data.write(to: url)

        // Разархивирование
        let loadedData = try Data(contentsOf: url)
        if let loadedUser = try NSKeyedUnarchiver.unarchiveTopLevelObjectWithData(loadedData) as? LegacyUser {
            print(loadedUser.name)
        }

    } catch {
        print("Error: \(error)")
    }
}
```

### Codable (Modern)

```swift
import Foundation

// Современный подход с Codable
struct ModernUser: Codable {
    let id: String
    let name: String
    let age: Int
    let email: String
    let registeredAt: Date
    let preferences: Preferences

    struct Preferences: Codable {
        let theme: String
        let notifications: Bool
    }
}

class CodableArchiver {
    private let encoder: JSONEncoder
    private let decoder: JSONDecoder

    init() {
        encoder = JSONEncoder()
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
        encoder.dateEncodingStrategy = .iso8601

        decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
    }

    // Архивирование в JSON
    func archiveToJSON<T: Codable>(_ object: T, filename: String) throws {
        let data = try encoder.encode(object)
        let url = getDocumentsURL().appendingPathComponent(filename)
        try data.write(to: url, options: [.atomic, .completeFileProtection])
    }

    // Разархивирование из JSON
    func unarchiveFromJSON<T: Codable>(filename: String, type: T.Type) throws -> T {
        let url = getDocumentsURL().appendingPathComponent(filename)
        let data = try Data(contentsOf: url)
        return try decoder.decode(T.self, from: data)
    }

    // Архивирование в PropertyList
    func archiveToPlist<T: Codable>(_ object: T, filename: String) throws {
        let plistEncoder = PropertyListEncoder()
        plistEncoder.outputFormat = .binary

        let data = try plistEncoder.encode(object)
        let url = getDocumentsURL().appendingPathComponent(filename)
        try data.write(to: url, options: [.atomic, .completeFileProtection])
    }

    // Разархивирование из PropertyList
    func unarchiveFromPlist<T: Codable>(filename: String, type: T.Type) throws -> T {
        let url = getDocumentsURL().appendingPathComponent(filename)
        let data = try Data(contentsOf: url)

        let plistDecoder = PropertyListDecoder()
        return try plistDecoder.decode(T.self, from: data)
    }

    private func getDocumentsURL() -> URL {
        return FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
}

// Пример использования
func modernArchiving() {
    let archiver = CodableArchiver()

    let user = ModernUser(
        id: "123",
        name: "John Doe",
        age: 30,
        email: "john@example.com",
        registeredAt: Date(),
        preferences: ModernUser.Preferences(
            theme: "dark",
            notifications: true
        )
    )

    do {
        // JSON архивирование
        try archiver.archiveToJSON(user, filename: "user.json")
        let loadedUser = try archiver.unarchiveFromJSON(filename: "user.json", type: ModernUser.self)
        print(loadedUser.name)

        // PropertyList архивирование
        try archiver.archiveToPlist(user, filename: "user.plist")
        let plistUser = try archiver.unarchiveFromPlist(filename: "user.plist", type: ModernUser.self)
        print(plistUser.name)

    } catch {
        print("Error: \(error)")
    }
}
```

### Сравнение NSCoding vs Codable

```
┌────────────────────────────────────────────────────────────────┐
│              NSCoding vs Codable Comparison                    │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  NSCoding (Legacy)                 Codable (Modern)            │
│  ├─ Objective-C heritage          ├─ Pure Swift               │
│  ├─ Class only (NSObject)         ├─ Struct, Class, Enum      │
│  ├─ Runtime errors                ├─ Compile-time safety      │
│  ├─ Manual encode/decode          ├─ Auto-synthesis           │
│  ├─ NSKeyedArchiver               ├─ JSON/Plist/Custom        │
│  ├─ Больше boilerplate            ├─ Меньше кода              │
│  └─ Deprecated подход             └─ Рекомендуется            │
│                                                                │
└────────────────────────────────────────────────────────────────┘
```

## 8. iCloud Key-Value Storage

```swift
import Foundation

// iCloud KVS для синхронизации простых настроек между устройствами
// Ограничения:
// - Максимум 1MB данных
// - Максимум 1024 ключа
// - Максимум 1MB на ключ для Data/String
// - Максимум 8 байт для числовых типов

class iCloudKVSManager {
    private let store = NSUbiquitousKeyValueStore.default

    // MARK: - Setup

    init() {
        // Подписка на изменения из iCloud
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleiCloudStoreChange),
            name: NSUbiquitousKeyValueStore.didChangeExternallyNotification,
            object: store
        )

        // Синхронизация при запуске
        store.synchronize()
    }

    @objc private func handleiCloudStoreChange(notification: Notification) {
        guard let userInfo = notification.userInfo else { return }

        // Причина изменения
        if let reason = userInfo[NSUbiquitousKeyValueStoreChangeReasonKey] as? Int {
            switch reason {
            case NSUbiquitousKeyValueStoreServerChange:
                print("Changes from iCloud server")
            case NSUbiquitousKeyValueStoreInitialSyncChange:
                print("Initial sync from iCloud")
            case NSUbiquitousKeyValueStoreQuotaViolationChange:
                print("iCloud quota exceeded!")
            case NSUbiquitousKeyValueStoreAccountChange:
                print("iCloud account changed")
            default:
                break
            }
        }

        // Измененные ключи
        if let changedKeys = userInfo[NSUbiquitousKeyValueStoreChangedKeysKey] as? [String] {
            print("Changed keys: \(changedKeys)")
            handleChangedKeys(changedKeys)
        }
    }

    private func handleChangedKeys(_ keys: [String]) {
        for key in keys {
            // Обработка изменений
            if key == "theme" {
                let theme = getString(key: "theme") ?? "light"
                applyTheme(theme)
            }
        }
    }

    // MARK: - Save

    func setString(key: String, value: String) {
        store.set(value, forKey: key)
        store.synchronize()
    }

    func setInt(key: String, value: Int) {
        store.set(Int64(value), forKey: key)
        store.synchronize()
    }

    func setBool(key: String, value: Bool) {
        store.set(value, forKey: key)
        store.synchronize()
    }

    func setDouble(key: String, value: Double) {
        store.set(value, forKey: key)
        store.synchronize()
    }

    func setData(key: String, value: Data) {
        store.set(value, forKey: key)
        store.synchronize()
    }

    func setArray(key: String, value: [Any]) {
        store.set(value, forKey: key)
        store.synchronize()
    }

    func setDictionary(key: String, value: [String: Any]) {
        store.set(value, forKey: key)
        store.synchronize()
    }

    // MARK: - Load

    func getString(key: String) -> String? {
        return store.string(forKey: key)
    }

    func getInt(key: String) -> Int? {
        let value = store.longLong(forKey: key)
        return value == 0 && store.object(forKey: key) == nil ? nil : Int(value)
    }

    func getBool(key: String) -> Bool? {
        guard store.object(forKey: key) != nil else { return nil }
        return store.bool(forKey: key)
    }

    func getDouble(key: String) -> Double? {
        let value = store.double(forKey: key)
        return value == 0 && store.object(forKey: key) == nil ? nil : value
    }

    func getData(key: String) -> Data? {
        return store.data(forKey: key)
    }

    func getArray(key: String) -> [Any]? {
        return store.array(forKey: key)
    }

    func getDictionary(key: String) -> [String: Any]? {
        return store.dictionary(forKey: key)
    }

    // MARK: - Delete

    func remove(key: String) {
        store.removeObject(forKey: key)
        store.synchronize()
    }

    // MARK: - Codable Support

    func setCodable<T: Codable>(key: String, value: T) throws {
        let encoder = JSONEncoder()
        let data = try encoder.encode(value)
        setData(key: key, value: data)
    }

    func getCodable<T: Codable>(key: String, type: T.Type) throws -> T? {
        guard let data = getData(key: key) else { return nil }
        let decoder = JSONDecoder()
        return try decoder.decode(T.self, from: data)
    }

    private func applyTheme(_ theme: String) {
        // Применение темы
    }
}

// Типобезопасная обёртка
struct iCloudSettings {
    static let manager = iCloudKVSManager()

    static var theme: String {
        get { manager.getString(key: "theme") ?? "light" }
        set { manager.setString(key: "theme", value: newValue) }
    }

    static var fontSize: Int {
        get { manager.getInt(key: "fontSize") ?? 14 }
        set { manager.setInt(key: "fontSize", value: newValue) }
    }

    static var notificationsEnabled: Bool {
        get { manager.getBool(key: "notificationsEnabled") ?? true }
        set { manager.setBool(key: "notificationsEnabled", value: newValue) }
    }
}

// Пример использования
func iCloudExample() {
    // Запись (синхронизируется на все устройства пользователя)
    iCloudSettings.theme = "dark"
    iCloudSettings.fontSize = 16
    iCloudSettings.notificationsEnabled = false

    // Чтение
    print(iCloudSettings.theme)  // "dark"
}

// Проверка доступности iCloud
extension iCloudKVSManager {
    var isiCloudAvailable: Bool {
        return FileManager.default.ubiquityIdentityToken != nil
    }

    func checkQuota() {
        let dictionaryRepresentation = store.dictionaryRepresentation
        let totalSize = dictionaryRepresentation.values.reduce(0) { total, value in
            if let data = value as? Data {
                return total + data.count
            } else if let string = value as? String {
                return total + (string.data(using: .utf8)?.count ?? 0)
            }
            return total + 8  // Примерный размер для числовых типов
        }

        let limitMB = 1.0
        let usedMB = Double(totalSize) / (1024 * 1024)

        print("iCloud KVS usage: \(usedMB) MB / \(limitMB) MB")

        if usedMB > limitMB * 0.9 {
            print("Warning: Approaching iCloud KVS limit!")
        }
    }
}
```

## 9. Стратегии миграции данных

```swift
import Foundation

// Версионирование и миграция данных
class DataMigrationManager {
    private let currentVersion = 3
    private let versionKey = "dataSchemaVersion"

    func performMigrationIfNeeded() {
        let savedVersion = UserDefaults.standard.integer(forKey: versionKey)

        guard savedVersion < currentVersion else {
            print("Data is up to date (v\(currentVersion))")
            return
        }

        print("Migrating from v\(savedVersion) to v\(currentVersion)")

        // Последовательная миграция
        if savedVersion < 1 {
            migrateToV1()
        }
        if savedVersion < 2 {
            migrateToV2()
        }
        if savedVersion < 3 {
            migrateToV3()
        }

        // Сохранение новой версии
        UserDefaults.standard.set(currentVersion, forKey: versionKey)
        print("Migration completed to v\(currentVersion)")
    }

    // v0 → v1: Добавление новых полей
    private func migrateToV1() {
        print("Migrating to v1: Adding default settings")

        // Установка значений по умолчанию для новых настроек
        if UserDefaults.standard.object(forKey: "theme") == nil {
            UserDefaults.standard.set("light", forKey: "theme")
        }
        if UserDefaults.standard.object(forKey: "fontSize") == nil {
            UserDefaults.standard.set(14, forKey: "fontSize")
        }
    }

    // v1 → v2: Переименование ключей
    private func migrateToV2() {
        print("Migrating to v2: Renaming keys")

        // Переименование старых ключей
        let oldToNewKeys = [
            "user_name": "username",
            "user_email": "email",
            "dark_mode": "theme"
        ]

        for (oldKey, newKey) in oldToNewKeys {
            if let value = UserDefaults.standard.object(forKey: oldKey) {
                UserDefaults.standard.set(value, forKey: newKey)
                UserDefaults.standard.removeObject(forKey: oldKey)
            }
        }

        // Преобразование dark_mode (Bool) → theme (String)
        if let darkMode = UserDefaults.standard.object(forKey: "dark_mode") as? Bool {
            UserDefaults.standard.set(darkMode ? "dark" : "light", forKey: "theme")
            UserDefaults.standard.removeObject(forKey: "dark_mode")
        }
    }

    // v2 → v3: Миграция файлов
    private func migrateToV3() {
        print("Migrating to v3: Moving files to new location")

        let fileManager = FileManager.default
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let appSupportURL = fileManager.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]

        // Создание новой директории
        try? fileManager.createDirectory(at: appSupportURL, withIntermediateDirectories: true)

        // Перемещение файлов из Documents в Application Support
        let oldDatabaseURL = documentsURL.appendingPathComponent("database.sqlite")
        let newDatabaseURL = appSupportURL.appendingPathComponent("database.sqlite")

        if fileManager.fileExists(atPath: oldDatabaseURL.path) {
            try? fileManager.moveItem(at: oldDatabaseURL, to: newDatabaseURL)
            print("Moved database to Application Support")
        }
    }
}

// Миграция структур данных
struct MigratableUser: Codable {
    let id: String
    let name: String
    let email: String?  // Добавлено в v2
    let preferences: Preferences?  // Добавлено в v3

    struct Preferences: Codable {
        let theme: String
        let notifications: Bool
    }

    // Custom decoding для обработки старых версий
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)

        id = try container.decode(String.self, forKey: .id)
        name = try container.decode(String.self, forKey: .name)

        // email может отсутствовать в старых версиях
        email = try container.decodeIfPresent(String.self, forKey: .email)

        // preferences может отсутствовать в старых версиях
        if let prefs = try container.decodeIfPresent(Preferences.self, forKey: .preferences) {
            preferences = prefs
        } else {
            // Значения по умолчанию для старых версий
            preferences = Preferences(theme: "light", notifications: true)
        }
    }
}

// Миграция Keychain данных
class KeychainMigration {
    private let oldKeychain = KeychainManager()

    func migrateTokenFormat() {
        // Миграция токена из старого формата в новый
        if let oldToken = oldKeychain.loadString(key: "token") {
            // Преобразование формата токена
            let newToken = transformToken(oldToken)

            // Сохранение в новом формате
            let secureStorage = SecureStorage()
            let credentials = AuthCredentials(
                username: "",
                accessToken: newToken,
                refreshToken: "",
                expiresAt: Date().addingTimeInterval(3600)
            )

            try? secureStorage.save(credentials, key: "credentials")

            // Удаление старого токена
            oldKeychain.delete(key: "token")
        }
    }

    private func transformToken(_ oldToken: String) -> String {
        // Логика преобразования токена
        return oldToken
    }
}

// Резервное копирование перед миграцией
class BackupManager {
    func createBackupBeforeMigration() throws {
        let fileManager = FileManager.default
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let backupURL = documentsURL.appendingPathComponent("Backups")

        // Создание директории для backup
        try fileManager.createDirectory(at: backupURL, withIntermediateDirectories: true)

        // Backup UserDefaults
        let userDefaultsURL = backupURL.appendingPathComponent("userdefaults_backup.plist")
        let userDefaultsDict = UserDefaults.standard.dictionaryRepresentation()
        let plistData = try PropertyListSerialization.data(
            fromPropertyList: userDefaultsDict,
            format: .xml,
            options: 0
        )
        try plistData.write(to: userDefaultsURL)

        // Backup файлов
        let filesToBackup = ["database.sqlite", "config.json"]
        for filename in filesToBackup {
            let sourceURL = documentsURL.appendingPathComponent(filename)
            let destURL = backupURL.appendingPathComponent(filename)

            if fileManager.fileExists(atPath: sourceURL.path) {
                try? fileManager.copyItem(at: sourceURL, to: destURL)
            }
        }

        print("Backup created at: \(backupURL.path)")
    }

    func restoreFromBackup() throws {
        let fileManager = FileManager.default
        let documentsURL = fileManager.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let backupURL = documentsURL.appendingPathComponent("Backups")

        // Восстановление UserDefaults
        let userDefaultsURL = backupURL.appendingPathComponent("userdefaults_backup.plist")
        if let data = try? Data(contentsOf: userDefaultsURL),
           let dict = try? PropertyListSerialization.propertyList(from: data, options: [], format: nil) as? [String: Any] {

            for (key, value) in dict {
                UserDefaults.standard.set(value, forKey: key)
            }
        }

        print("Backup restored")
    }
}
```

## 10. Сравнение с Android

```swift
// Сравнение iOS и Android механизмов хранения данных
// См. также: [[android-data-persistence]]

/*
┌──────────────────────────────────────────────────────────────────────┐
│                   iOS vs Android Storage Comparison                  │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  iOS                           │  Android                           │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  UserDefaults                  │  SharedPreferences                 │
│  ├─ Key-Value хранилище        │  ├─ Key-Value хранилище            │
│  ├─ Синхронный API             │  ├─ Синхронный API                 │
│  ├─ .plist файлы               │  ├─ XML файлы                      │
│  ├─ Лимит: ~4MB                │  ├─ Нет жесткого лимита            │
│  └─ Thread-safe                │  └─ Thread-safe                    │
│                                                                      │
│  Keychain                      │  Encrypted SharedPreferences       │
│  ├─ Зашифрованное хранилище    │  ├─ Зашифрованное хранилище        │
│  ├─ За пределами sandbox       │  ├─ Jetpack Security               │
│  ├─ Синхронизация через iCloud │  ├─ Нет облачной синхронизации    │
│  ├─ SecItemAdd/Copy/Update     │  ├─ Android Keystore System        │
│  └─ Биометрия встроена         │  └─ Биометрия через BiometricPrompt│
│                                                                      │
│  FileManager                   │  File API                          │
│  ├─ Documents/ (backup)        │  ├─ Internal Storage               │
│  ├─ Library/Caches/            │  ├─ Cache Directory                │
│  ├─ tmp/ (temporary)           │  ├─ External Storage (SD card)     │
│  └─ Sandbox изоляция           │  └─ Scoped Storage (Android 10+)   │
│                                                                      │
│  iCloud KVS                    │  Firebase Remote Config            │
│  ├─ Встроенная синхронизация   │  ├─ Требует Firebase SDK           │
│  ├─ Лимит: 1MB                 │  ├─ Лимит: зависит от плана        │
│  ├─ Бесплатно для пользователей│  ├─ Бесплатный tier ограничен      │
│  └─ Автоматическая синхронизация│ └─ Ручная fetch политика          │
│                                                                      │
│  App Groups                    │  ContentProvider                   │
│  ├─ Обмен между приложениями   │  ├─ Обмен между приложениями       │
│  ├─ Shared Container           │  ├─ URI-based доступ               │
│  └─ Для виджетов/расширений    │  └─ Для других приложений          │
│                                                                      │
│  PropertyListEncoder           │  DataStore (Preferences)           │
│  ├─ XML/Binary формат          │  ├─ Protocol Buffers               │
│  ├─ Синхронный API             │  ├─ Асинхронный API (Flow)         │
│  └─ Старый подход              │  └─ Современная замена SharedPrefs │
│                                                                      │
│  NSCoding/NSKeyedArchiver      │  Serializable/Parcelable           │
│  ├─ Legacy подход              │  ├─ Legacy подход                  │
│  └─ Заменён на Codable         │  └─ Заменён на Kotlin Serialization│
│                                                                      │
│  Codable + JSON/Plist          │  Kotlin Serialization + JSON       │
│  ├─ Современный подход         │  ├─ Современный подход             │
│  ├─ Compile-time безопасность  │  ├─ Compile-time безопасность      │
│  └─ JSONEncoder/Decoder        │  └─ Json.encodeToString/decode     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
*/

// Концептуальное сравнение миграции
class iOSvsAndroidMigration {

    // iOS: Версионирование через UserDefaults
    func iOSMigration() {
        let version = UserDefaults.standard.integer(forKey: "schemaVersion")
        if version < 2 {
            // Миграция
            UserDefaults.standard.set(2, forKey: "schemaVersion")
        }
    }

    // Android эквивалент (концептуально):
    // val sharedPrefs = context.getSharedPreferences("app_prefs", Context.MODE_PRIVATE)
    // val version = sharedPrefs.getInt("schema_version", 0)
    // if (version < 2) {
    //     // Migration
    //     sharedPrefs.edit().putInt("schema_version", 2).apply()
    // }

    // iOS: Secure Storage
    func iOSSecureStorage() {
        let keychain = KeychainManager()
        keychain.save(key: "token", value: "abc123")
    }

    // Android эквивалент (концептуально):
    // val masterKey = MasterKey.Builder(context)
    //     .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
    //     .build()
    // val sharedPrefs = EncryptedSharedPreferences.create(
    //     context,
    //     "secure_prefs",
    //     masterKey,
    //     EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    //     EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    // )
    // sharedPrefs.edit().putString("token", "abc123").apply()
}
```

## Типичные ошибки

### ❌ Ошибка 1: Хранение чувствительных данных в UserDefaults

```swift
// НЕПРАВИЛЬНО: Пароли и токены в открытом виде
class InsecureStorage {
    func saveCredentials(username: String, password: String) {
        UserDefaults.standard.set(username, forKey: "username")
        UserDefaults.standard.set(password, forKey: "password")  // ОПАСНО!
    }

    func saveToken(_ token: String) {
        UserDefaults.standard.set(token, forKey: "authToken")  // ОПАСНО!
    }
}
```

```swift
// ✅ ПРАВИЛЬНО: Использование Keychain для чувствительных данных
class SecureCredentialsStorage {
    private let keychain = KeychainManager()

    func saveCredentials(username: String, password: String) {
        // Username можно в UserDefaults (не секретная информация)
        UserDefaults.standard.set(username, forKey: "username")

        // Password только в Keychain
        keychain.save(key: "password", value: password)
    }

    func saveToken(_ token: String) {
        // Токены всегда в Keychain
        keychain.save(
            key: "authToken",
            value: token,
            accessibility: kSecAttrAccessibleAfterFirstUnlock
        )
    }

    func loadCredentials() -> (username: String?, password: String?) {
        let username = UserDefaults.standard.string(forKey: "username")
        let password = keychain.loadString(key: "password")
        return (username, password)
    }
}
```

### ❌ Ошибка 2: Блокировка главного потока при работе с файлами

```swift
// НЕПРАВИЛЬНО: Синхронная работа с большими файлами на главном потоке
class SynchronousFileManager {
    func loadLargeFile() -> Data? {
        let url = getDocumentsURL().appendingPathComponent("large_file.dat")

        // Блокирует UI при загрузке большого файла!
        return try? Data(contentsOf: url)  // ПЛОХО!
    }

    func saveLargeData(_ data: Data) {
        let url = getDocumentsURL().appendingPathComponent("large_file.dat")

        // Блокирует UI при сохранении!
        try? data.write(to: url)  // ПЛОХО!
    }

    private func getDocumentsURL() -> URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
}
```

```swift
// ✅ ПРАВИЛЬНО: Асинхронная работа с файлами
class AsynchronousFileManager {
    func loadLargeFile() async throws -> Data {
        let url = getDocumentsURL().appendingPathComponent("large_file.dat")

        // Выполняем на background потоке
        return try await Task.detached(priority: .userInitiated) {
            try Data(contentsOf: url)
        }.value
    }

    func saveLargeData(_ data: Data) async throws {
        let url = getDocumentsURL().appendingPathComponent("large_file.dat")

        // Выполняем на background потоке
        try await Task.detached(priority: .utility) {
            try data.write(to: url, options: [.atomic, .completeFileProtection])
        }.value
    }

    // Альтернатива с замыканиями
    func loadLargeFileWithCompletion(completion: @escaping (Result<Data, Error>) -> Void) {
        let url = getDocumentsURL().appendingPathComponent("large_file.dat")

        DispatchQueue.global(qos: .userInitiated).async {
            do {
                let data = try Data(contentsOf: url)
                DispatchQueue.main.async {
                    completion(.success(data))
                }
            } catch {
                DispatchQueue.main.async {
                    completion(.failure(error))
                }
            }
        }
    }

    private func getDocumentsURL() -> URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
}
```

### ❌ Ошибка 3: Хранение больших данных в UserDefaults

```swift
// НЕПРАВИЛЬНО: Сохранение большого количества данных в UserDefaults
class BadCacheManager {
    func cacheImages(_ images: [UIImage]) {
        // ПЛОХО: UserDefaults не для больших данных!
        for (index, image) in images.enumerated() {
            if let data = image.jpegData(compressionQuality: 0.8) {
                UserDefaults.standard.set(data, forKey: "image_\(index)")  // ОПАСНО!
            }
        }
    }

    func cacheLargeJSON(_ json: [String: Any]) {
        // ПЛОХО: Большой JSON замедляет запуск приложения!
        UserDefaults.standard.set(json, forKey: "largeData")  // ПЛОХО!
    }
}
```

```swift
// ✅ ПРАВИЛЬНО: Использование FileManager для больших данных
class ProperCacheManager {
    private let fileManager = FileManager.default
    private let cacheDirectory: URL

    init() {
        cacheDirectory = fileManager.urls(for: .cachesDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("ImageCache")

        // Создаём директорию для кэша
        try? fileManager.createDirectory(at: cacheDirectory, withIntermediateDirectories: true)
    }

    func cacheImages(_ images: [UIImage]) async throws {
        for (index, image) in images.enumerated() {
            guard let data = image.jpegData(compressionQuality: 0.8) else { continue }

            let fileURL = cacheDirectory.appendingPathComponent("image_\(index).jpg")

            // Асинхронная запись
            try await Task.detached {
                try data.write(to: fileURL)
            }.value
        }

        // Исключаем из backup
        try excludeCacheFromBackup()
    }

    func cacheLargeJSON(_ json: [String: Any]) throws {
        let encoder = JSONEncoder()
        encoder.outputFormatting = .prettyPrinted

        // Сохраняем в файл, а не в UserDefaults
        let data = try JSONSerialization.data(withJSONObject: json)
        let fileURL = cacheDirectory.appendingPathComponent("data.json")

        try data.write(to: fileURL)

        // В UserDefaults сохраняем только метаданные
        UserDefaults.standard.set(Date(), forKey: "dataLastUpdated")
        UserDefaults.standard.set(true, forKey: "hasCachedData")
    }

    func loadImage(index: Int) async throws -> UIImage? {
        let fileURL = cacheDirectory.appendingPathComponent("image_\(index).jpg")

        let data = try await Task.detached {
            try Data(contentsOf: fileURL)
        }.value

        return UIImage(data: data)
    }

    private func excludeCacheFromBackup() throws {
        var resourceValues = URLResourceValues()
        resourceValues.isExcludedFromBackup = true
        var url = cacheDirectory
        try url.setResourceValues(resourceValues)
    }

    func clearCache() throws {
        let contents = try fileManager.contentsOfDirectory(
            at: cacheDirectory,
            includingPropertiesForKeys: nil
        )

        for fileURL in contents {
            try fileManager.removeItem(at: fileURL)
        }
    }
}
```

### ❌ Ошибка 4: Игнорирование File Protection

```swift
// НЕПРАВИЛЬНО: Сохранение без File Protection
class UnprotectedFileStorage {
    func saveUserData(_ data: Data) {
        let url = getDocumentsURL().appendingPathComponent("user_data.json")

        // Файл не защищён, доступен при блокировке устройства
        try? data.write(to: url)  // ПЛОХО!
    }

    private func getDocumentsURL() -> URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
}
```

```swift
// ✅ ПРАВИЛЬНО: Использование File Protection
class ProtectedFileStorage {
    func saveUserData(_ data: Data, sensitivity: DataSensitivity) throws {
        let url = getDocumentsURL().appendingPathComponent("user_data.json")

        // Выбираем уровень защиты в зависимости от чувствительности данных
        let protection: FileProtectionType

        switch sensitivity {
        case .high:
            // Медицинские данные, финансы - полная защита
            protection = .complete
        case .medium:
            // Личные документы - защита до первой разблокировки
            protection = .completeUntilFirstUserAuthentication
        case .low:
            // Кэш данных - минимальная защита
            protection = .completeUnlessOpen
        }

        try data.write(to: url, options: [.atomic, protection])

        print("Saved with protection: \(protection)")
    }

    func saveSensitiveDocument(_ data: Data) throws {
        let url = getDocumentsURL().appendingPathComponent("sensitive.pdf")

        // Для чувствительных документов - максимальная защита
        try data.write(to: url, options: [
            .atomic,
            .completeFileProtection  // Недоступен при блокировке
        ])
    }

    func saveCacheData(_ data: Data) throws {
        let cacheURL = FileManager.default.urls(for: .cachesDirectory, in: .userDomainMask)[0]
        let url = cacheURL.appendingPathComponent("cache.dat")

        // Для кэша - без защиты (можно удалить для экономии места)
        try data.write(to: url, options: [
            .atomic,
            FileProtectionType.none
        ])

        // Исключаем из backup
        var resourceValues = URLResourceValues()
        resourceValues.isExcludedFromBackup = true
        var mutableURL = url
        try mutableURL.setResourceValues(resourceValues)
    }

    private func getDocumentsURL() -> URL {
        FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
    }
}

enum DataSensitivity {
    case high    // Медицинские данные, финансы, пароли
    case medium  // Личные документы, фотографии
    case low     // Кэш, временные файлы
}
```

### ❌ Ошибка 5: Отсутствие миграции данных

```swift
// НЕПРАВИЛЬНО: Изменение структуры без миграции
class NoMigrationManager {
    // Версия 1
    struct UserV1: Codable {
        let name: String
        let age: Int
    }

    // Версия 2 - добавили email, но нет миграции!
    struct UserV2: Codable {
        let name: String
        let age: Int
        let email: String  // Новое поле - старые данные не загрузятся!
    }

    func saveUser() {
        let user = UserV2(name: "John", age: 30, email: "john@example.com")
        let data = try? JSONEncoder().encode(user)
        UserDefaults.standard.set(data, forKey: "user")
    }

    func loadUser() -> UserV2? {
        guard let data = UserDefaults.standard.data(forKey: "user") else { return nil }

        // Крашнется при загрузке данных версии 1!
        return try? JSONDecoder().decode(UserV2.self, from: data)  // ПЛОХО!
    }
}
```

```swift
// ✅ ПРАВИЛЬНО: Правильная миграция с версионированием
class ProperMigrationManager {
    private let versionKey = "userDataVersion"
    private let currentVersion = 2

    // Версия 1
    struct UserV1: Codable {
        let name: String
        let age: Int
    }

    // Версия 2
    struct UserV2: Codable {
        let name: String
        let age: Int
        let email: String
        let registeredAt: Date

        // Custom decoding для обратной совместимости
        init(from decoder: Decoder) throws {
            let container = try decoder.container(keyedBy: CodingKeys.self)

            name = try container.decode(String.self, forKey: .name)
            age = try container.decode(Int.self, forKey: .age)

            // email может отсутствовать в старых версиях
            email = try container.decodeIfPresent(String.self, forKey: .email) ?? ""

            // registeredAt может отсутствовать
            registeredAt = try container.decodeIfPresent(Date.self, forKey: .registeredAt) ?? Date()
        }

        init(name: String, age: Int, email: String, registeredAt: Date = Date()) {
            self.name = name
            self.age = age
            self.email = email
            self.registeredAt = registeredAt
        }
    }

    func performMigrationIfNeeded() {
        let savedVersion = UserDefaults.standard.integer(forKey: versionKey)

        if savedVersion < currentVersion {
            print("Migrating user data from v\(savedVersion) to v\(currentVersion)")
            migrateUserData(from: savedVersion, to: currentVersion)
            UserDefaults.standard.set(currentVersion, forKey: versionKey)
        }
    }

    private func migrateUserData(from oldVersion: Int, to newVersion: Int) {
        if oldVersion < 1 {
            // Миграция на версию 1
            print("No migration needed for v1")
        }

        if oldVersion < 2 {
            // Миграция v1 → v2
            migrateV1toV2()
        }
    }

    private func migrateV1toV2() {
        guard let data = UserDefaults.standard.data(forKey: "user"),
              let userV1 = try? JSONDecoder().decode(UserV1.self, from: data) else {
            return
        }

        // Создаём пользователя v2 с данными из v1
        let userV2 = UserV2(
            name: userV1.name,
            age: userV1.age,
            email: "",  // Значение по умолчанию для нового поля
            registeredAt: Date()
        )

        // Сохраняем в новом формате
        let newData = try? JSONEncoder().encode(userV2)
        UserDefaults.standard.set(newData, forKey: "user")

        print("Migrated user data to v2")
    }

    func saveUser(_ user: UserV2) {
        performMigrationIfNeeded()

        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601

        if let data = try? encoder.encode(user) {
            UserDefaults.standard.set(data, forKey: "user")
        }
    }

    func loadUser() -> UserV2? {
        performMigrationIfNeeded()

        guard let data = UserDefaults.standard.data(forKey: "user") else { return nil }

        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601

        return try? decoder.decode(UserV2.self, from: data)
    }
}

// Альтернатива: Wrapper для версионирования
struct VersionedData<T: Codable>: Codable {
    let version: Int
    let data: T

    init(data: T, version: Int = 1) {
        self.data = data
        self.version = version
    }
}

class VersionedStorage {
    func save<T: Codable>(_ object: T, key: String, version: Int) {
        let versioned = VersionedData(data: object, version: version)

        if let data = try? JSONEncoder().encode(versioned) {
            UserDefaults.standard.set(data, forKey: key)
        }
    }

    func load<T: Codable>(key: String, type: T.Type, expectedVersion: Int) -> T? {
        guard let data = UserDefaults.standard.data(forKey: key),
              let versioned = try? JSONDecoder().decode(VersionedData<T>.self, from: data) else {
            return nil
        }

        if versioned.version != expectedVersion {
            print("Version mismatch: expected \(expectedVersion), got \(versioned.version)")
            // Здесь можно выполнить миграцию
        }

        return versioned.data
    }
}
```

### ❌ Ошибка 6: Неправильное использование App Groups

```swift
// НЕПРАВИЛЬНО: Смешивание обычных и shared UserDefaults
class ConfusedSharedStorage {
    func saveForWidget() {
        // ПЛОХО: Виджет не имеет доступа к стандартному UserDefaults!
        UserDefaults.standard.set("value", forKey: "widgetData")  // Виджет не увидит!
    }

    func saveInMainApp() {
        let sharedDefaults = UserDefaults(suiteName: "group.com.example.app")
        sharedDefaults?.set("main", forKey: "source")

        // ПЛОХО: Дублирование данных в разных хранилищах
        UserDefaults.standard.set("main", forKey: "source")  // Несогласованность!
    }
}
```

```swift
// ✅ ПРАВИЛЬНО: Централизованное управление shared storage
class SharedStorageManager {
    // Единая точка доступа к shared storage
    private static let groupIdentifier = "group.com.example.app"

    static let shared = UserDefaults(suiteName: groupIdentifier)!
    static let sharedContainer = FileManager.default.containerURL(
        forSecurityApplicationGroupIdentifier: groupIdentifier
    )!

    // Ключи для shared данных
    enum SharedKeys {
        static let widgetData = "widgetData"
        static let lastUpdate = "lastUpdate"
        static let counter = "counter"
    }

    // Типобезопасные методы
    static func saveWidgetData<T: Codable>(_ data: T) {
        let encoder = JSONEncoder()
        if let encoded = try? encoder.encode(data) {
            shared.set(encoded, forKey: SharedKeys.widgetData)
            shared.set(Date(), forKey: SharedKeys.lastUpdate)

            // Уведомляем виджет
            notifyWidget()
        }
    }

    static func loadWidgetData<T: Codable>(type: T.Type) -> T? {
        guard let data = shared.data(forKey: SharedKeys.widgetData) else {
            return nil
        }

        let decoder = JSONDecoder()
        return try? decoder.decode(T.self, from: data)
    }

    static func saveSharedFile(data: Data, filename: String) throws {
        let fileURL = sharedContainer.appendingPathComponent(filename)

        // Используем NSFileCoordinator для безопасного доступа
        let coordinator = NSFileCoordinator(filePresenter: nil)
        var error: NSError?

        coordinator.coordinate(writingItemAt: fileURL, options: [], error: &error) { url in
            try? data.write(to: url, options: [.atomic, .completeFileProtection])
        }

        if let error = error {
            throw error
        }
    }

    static func loadSharedFile(filename: String) throws -> Data {
        let fileURL = sharedContainer.appendingPathComponent(filename)

        let coordinator = NSFileCoordinator(filePresenter: nil)
        var error: NSError?
        var resultData: Data?

        coordinator.coordinate(readingItemAt: fileURL, options: [], error: &error) { url in
            resultData = try? Data(contentsOf: url)
        }

        if let error = error {
            throw error
        }

        guard let data = resultData else {
            throw SharedStorageError.fileNotFound
        }

        return data
    }

    private static func notifyWidget() {
        #if canImport(WidgetKit)
        import WidgetKit
        WidgetCenter.shared.reloadAllTimelines()
        #endif
    }
}

enum SharedStorageError: Error {
    case fileNotFound
    case coordinationFailed
}

// Использование в основном приложении
class MainAppViewModel {
    struct WidgetData: Codable {
        let title: String
        let count: Int
        let updatedAt: Date
    }

    func updateWidget() {
        let data = WidgetData(
            title: "Tasks",
            count: 42,
            updatedAt: Date()
        )

        SharedStorageManager.saveWidgetData(data)
    }
}

// Использование в виджете
import WidgetKit

struct WidgetDataProvider: TimelineProvider {
    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> Void) {
        let data = SharedStorageManager.loadWidgetData(type: MainAppViewModel.WidgetData.self)

        // Используем данные из shared storage
        let entry = SimpleEntry(
            date: Date(),
            title: data?.title ?? "No Data",
            count: data?.count ?? 0
        )

        let timeline = Timeline(entries: [entry], policy: .atEnd)
        completion(timeline)
    }

    // ... остальные методы провайдера
}
```

## Заключение

Правильный выбор механизма хранения данных критически важен для безопасности, производительности и пользовательского опыта iOS приложения:

**Рекомендации по выбору:**

1. **UserDefaults** — для простых настроек (< 100KB)
2. **Keychain** — для паролей, токенов, API ключей
3. **FileManager** — для документов, изображений, больших данных
4. **App Groups** — для обмена данными между app/widget/extension
5. **iCloud KVS** — для синхронизации настроек между устройствами (< 1MB)
6. **PropertyList** — для конфигурационных файлов
7. **Codable** — для сериализации структурированных данных (вместо NSCoding)

**Безопасность:**
- Всегда используйте Keychain для чувствительных данных
- Устанавливайте File Protection для пользовательских файлов
- Исключайте кэш из backup
- Не храните секреты в UserDefaults или plist файлах

**Производительность:**
- Асинхронная работа с файлами (async/await)
- Правильное использование директорий (Documents/Library/Caches/tmp)
- Ограничение размера данных в UserDefaults
- Периодическая очистка кэша и временных файлов

**Миграция:**
- Версионирование схемы данных
- Резервное копирование перед миграцией
- Обратная совместимость (decodeIfPresent)
- Постепенная миграция с проверками

Следуя этим рекомендациям, вы создадите надёжную и безопасную систему хранения данных в iOS приложении.
