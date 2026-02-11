---
title: "Cross-Platform: Data Persistence — Core Data vs Room"
created: 2026-01-11
type: comparison
status: published
tags:
  - topic/cross-platform
  - persistence
  - core-data
  - room
  - type/comparison
  - level/intermediate
prerequisites:
  - "[[cross-platform-overview]]"
  - "[[cross-architecture]]"
related:
  - "[[android-data-persistence]]"
  - "[[ios-data-persistence]]"
  - "[[mobile-databases-complete]]"
---

# Data Persistence: iOS vs Android

## TL;DR

| Аспект | iOS | Android | Кросс-платформа |
|--------|-----|---------|-----------------|
| **ORM/Database** | Core Data | Room | SQLDelight |
| **Modern API** | SwiftData | Room + KSP | SQLDelight |
| **Key-Value** | UserDefaults | SharedPreferences | DataStore Preferences |
| **Encrypted K-V** | Keychain | EncryptedSharedPreferences | — |
| **File Storage** | FileManager | Context.filesDir | Okio |
| **Query Language** | NSPredicate / #Predicate | SQL + DAOs | SQL |
| **Reactive** | Combine / @Query | Flow / LiveData | Flow |
| **Migration** | Lightweight / Mapping Model | Migration classes | Migration |
| **Threading** | Contexts + background queues | Coroutines | Coroutines |
| **Schema** | .xcdatamodeld / @Model | @Entity classes | .sq files |

---

## 1. Архитектура: Core Data vs Room

### Core Data (iOS)

Core Data — это не просто база данных, а полноценный **object graph manager** с persistence layer.

```
┌─────────────────────────────────────────────────────┐
│                  NSManagedObject                     │
│              (объекты в памяти)                      │
├─────────────────────────────────────────────────────┤
│              NSManagedObjectContext                  │
│           (scratch pad, unit of work)                │
├─────────────────────────────────────────────────────┤
│           NSPersistentStoreCoordinator               │
│              (координатор хранилищ)                  │
├─────────────────────────────────────────────────────┤
│              NSPersistentStore                       │
│         (SQLite, Binary, In-Memory)                  │
└─────────────────────────────────────────────────────┘
```

```swift
// Core Data Stack Setup
import CoreData

class CoreDataStack {
    static let shared = CoreDataStack()

    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "MyApp")
        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Unable to load persistent stores: \(error)")
            }
        }
        // Автоматический merge изменений
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy
        return container
    }()

    var viewContext: NSManagedObjectContext {
        persistentContainer.viewContext
    }

    func newBackgroundContext() -> NSManagedObjectContext {
        persistentContainer.newBackgroundContext()
    }
}
```

### Room (Android)

Room — это **абстракция над SQLite** с compile-time проверкой SQL.

```
┌─────────────────────────────────────────────────────┐
│                   @Entity                            │
│              (data classes)                          │
├─────────────────────────────────────────────────────┤
│                    @Dao                              │
│           (Data Access Objects)                      │
├─────────────────────────────────────────────────────┤
│               RoomDatabase                           │
│          (abstract database class)                   │
├─────────────────────────────────────────────────────┤
│                  SQLite                              │
└─────────────────────────────────────────────────────┘
```

```kotlin
// Room Setup
import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    @ColumnInfo(name = "full_name")
    val fullName: String,
    val email: String,
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun observeAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getById(userId: Long): UserEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(user: UserEntity): Long

    @Delete
    suspend fun delete(user: UserEntity)

    @Query("DELETE FROM users")
    suspend fun deleteAll()
}

@Database(
    entities = [UserEntity::class],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                .fallbackToDestructiveMigration()
                .build()
                .also { INSTANCE = it }
            }
        }
    }
}
```

### Сравнение моделей Side-by-Side

```swift
// iOS: Core Data Entity (в .xcdatamodeld или код)
import CoreData

@objc(User)
public class User: NSManagedObject {
    @NSManaged public var id: UUID
    @NSManaged public var fullName: String
    @NSManaged public var email: String
    @NSManaged public var createdAt: Date
    @NSManaged public var posts: NSSet? // Relationship
}

extension User {
    @nonobjc public class func fetchRequest() -> NSFetchRequest<User> {
        return NSFetchRequest<User>(entityName: "User")
    }

    static func create(
        in context: NSManagedObjectContext,
        fullName: String,
        email: String
    ) -> User {
        let user = User(context: context)
        user.id = UUID()
        user.fullName = fullName
        user.email = email
        user.createdAt = Date()
        return user
    }
}
```

```kotlin
// Android: Room Entity
@Entity(
    tableName = "users",
    indices = [Index(value = ["email"], unique = true)]
)
data class UserEntity(
    @PrimaryKey
    val id: String = UUID.randomUUID().toString(),
    @ColumnInfo(name = "full_name")
    val fullName: String,
    val email: String,
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
) {
    companion object {
        fun create(fullName: String, email: String) = UserEntity(
            fullName = fullName,
            email = email
        )
    }
}
```

---

## 2. UserDefaults vs SharedPreferences/DataStore

### UserDefaults (iOS)

```swift
// UserDefaults — синхронный key-value storage
import Foundation

enum UserDefaultsKey: String {
    case isOnboardingCompleted
    case selectedTheme
    case lastSyncTimestamp
    case userToken
}

class AppSettings {
    private let defaults = UserDefaults.standard

    var isOnboardingCompleted: Bool {
        get { defaults.bool(forKey: UserDefaultsKey.isOnboardingCompleted.rawValue) }
        set { defaults.set(newValue, forKey: UserDefaultsKey.isOnboardingCompleted.rawValue) }
    }

    var selectedTheme: String {
        get { defaults.string(forKey: UserDefaultsKey.selectedTheme.rawValue) ?? "system" }
        set { defaults.set(newValue, forKey: UserDefaultsKey.selectedTheme.rawValue) }
    }

    var lastSyncTimestamp: Date? {
        get { defaults.object(forKey: UserDefaultsKey.lastSyncTimestamp.rawValue) as? Date }
        set { defaults.set(newValue, forKey: UserDefaultsKey.lastSyncTimestamp.rawValue) }
    }

    // Property wrapper для SwiftUI
    @AppStorage("username") var username: String = ""
}

// Observation с Combine
import Combine

class SettingsObserver {
    private var cancellables = Set<AnyCancellable>()

    func observeThemeChanges() {
        NotificationCenter.default.publisher(
            for: UserDefaults.didChangeNotification
        )
        .sink { _ in
            // Handle changes
        }
        .store(in: &cancellables)
    }
}
```

### SharedPreferences vs DataStore (Android)

```kotlin
// SharedPreferences — legacy синхронный API
class LegacySettings(context: Context) {
    private val prefs = context.getSharedPreferences("settings", Context.MODE_PRIVATE)

    var isOnboardingCompleted: Boolean
        get() = prefs.getBoolean("is_onboarding_completed", false)
        set(value) = prefs.edit().putBoolean("is_onboarding_completed", value).apply()

    var selectedTheme: String
        get() = prefs.getString("selected_theme", "system") ?: "system"
        set(value) = prefs.edit().putString("selected_theme", value).apply()
}

// DataStore Preferences — современный асинхронный API
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.*
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "settings")

class AppSettings(private val dataStore: DataStore<Preferences>) {

    companion object {
        val IS_ONBOARDING_COMPLETED = booleanPreferencesKey("is_onboarding_completed")
        val SELECTED_THEME = stringPreferencesKey("selected_theme")
        val LAST_SYNC_TIMESTAMP = longPreferencesKey("last_sync_timestamp")
    }

    val isOnboardingCompleted: Flow<Boolean> = dataStore.data
        .map { preferences -> preferences[IS_ONBOARDING_COMPLETED] ?: false }

    val selectedTheme: Flow<String> = dataStore.data
        .map { preferences -> preferences[SELECTED_THEME] ?: "system" }

    suspend fun setOnboardingCompleted(completed: Boolean) {
        dataStore.edit { preferences ->
            preferences[IS_ONBOARDING_COMPLETED] = completed
        }
    }

    suspend fun setTheme(theme: String) {
        dataStore.edit { preferences ->
            preferences[SELECTED_THEME] = theme
        }
    }

    suspend fun updateLastSync() {
        dataStore.edit { preferences ->
            preferences[LAST_SYNC_TIMESTAMP] = System.currentTimeMillis()
        }
    }
}

// Proto DataStore — типизированный storage
import androidx.datastore.core.Serializer
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class UserPreferences(
    val isOnboardingCompleted: Boolean = false,
    val selectedTheme: String = "system",
    val notificationsEnabled: Boolean = true
)

object UserPreferencesSerializer : Serializer<UserPreferences> {
    override val defaultValue = UserPreferences()

    override suspend fun readFrom(input: InputStream): UserPreferences {
        return Json.decodeFromString(input.readBytes().decodeToString())
    }

    override suspend fun writeTo(t: UserPreferences, output: OutputStream) {
        output.write(Json.encodeToString(UserPreferences.serializer(), t).toByteArray())
    }
}
```

---

## 3. Keychain vs EncryptedSharedPreferences

### Keychain (iOS)

```swift
// Keychain — безопасное хранилище для credentials
import Security
import Foundation

enum KeychainError: Error {
    case duplicateItem
    case itemNotFound
    case unexpectedStatus(OSStatus)
}

class KeychainManager {
    static let shared = KeychainManager()
    private let service = Bundle.main.bundleIdentifier ?? "com.app"

    func save(_ data: Data, for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly
        ]

        let status = SecItemAdd(query as CFDictionary, nil)

        if status == errSecDuplicateItem {
            try update(data, for: key)
        } else if status != errSecSuccess {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    func read(for key: String) throws -> Data {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess, let data = result as? Data else {
            throw KeychainError.itemNotFound
        }

        return data
    }

    func delete(for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]

        let status = SecItemDelete(query as CFDictionary)
        guard status == errSecSuccess || status == errSecItemNotFound else {
            throw KeychainError.unexpectedStatus(status)
        }
    }

    private func update(_ data: Data, for key: String) throws {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: key
        ]

        let attributes: [String: Any] = [
            kSecValueData as String: data
        ]

        let status = SecItemUpdate(query as CFDictionary, attributes as CFDictionary)
        guard status == errSecSuccess else {
            throw KeychainError.unexpectedStatus(status)
        }
    }
}

// Удобная обёртка для токенов
class TokenStorage {
    private let keychain = KeychainManager.shared

    var accessToken: String? {
        get {
            guard let data = try? keychain.read(for: "access_token") else { return nil }
            return String(data: data, encoding: .utf8)
        }
        set {
            if let value = newValue, let data = value.data(using: .utf8) {
                try? keychain.save(data, for: "access_token")
            } else {
                try? keychain.delete(for: "access_token")
            }
        }
    }
}
```

### EncryptedSharedPreferences (Android)

```kotlin
// EncryptedSharedPreferences — безопасное хранилище
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureStorage(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val encryptedPrefs = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    var accessToken: String?
        get() = encryptedPrefs.getString("access_token", null)
        set(value) = encryptedPrefs.edit().putString("access_token", value).apply()

    var refreshToken: String?
        get() = encryptedPrefs.getString("refresh_token", null)
        set(value) = encryptedPrefs.edit().putString("refresh_token", value).apply()

    fun clearTokens() {
        encryptedPrefs.edit()
            .remove("access_token")
            .remove("refresh_token")
            .apply()
    }
}

// Android Keystore для криптографических ключей
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.KeyGenerator

class KeystoreManager {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }

    fun getOrCreateKey(alias: String): SecretKey {
        val existingKey = keyStore.getKey(alias, null) as? SecretKey
        if (existingKey != null) return existingKey

        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val spec = KeyGenParameterSpec.Builder(
            alias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setUserAuthenticationRequired(false)
            .build()

        keyGenerator.init(spec)
        return keyGenerator.generateKey()
    }
}
```

---

## 4. SwiftData vs Room (Современные API)

### SwiftData (iOS 17+)

```swift
// SwiftData — декларативный persistence
import SwiftData
import SwiftUI

@Model
final class User {
    @Attribute(.unique) var id: UUID
    var fullName: String
    var email: String
    var createdAt: Date

    @Relationship(deleteRule: .cascade, inverse: \Post.author)
    var posts: [Post] = []

    init(fullName: String, email: String) {
        self.id = UUID()
        self.fullName = fullName
        self.email = email
        self.createdAt = Date()
    }
}

@Model
final class Post {
    @Attribute(.unique) var id: UUID
    var title: String
    var content: String
    var publishedAt: Date?
    var author: User?

    init(title: String, content: String, author: User) {
        self.id = UUID()
        self.title = title
        self.content = content
        self.author = author
    }
}

// Конфигурация SwiftData
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [User.self, Post.self])
    }
}

// Использование в SwiftUI
struct UserListView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \User.createdAt, order: .reverse) private var users: [User]

    var body: some View {
        List(users) { user in
            VStack(alignment: .leading) {
                Text(user.fullName)
                    .font(.headline)
                Text(user.email)
                    .font(.caption)
                    .foregroundStyle(.secondary)
            }
        }
        .toolbar {
            Button("Add") {
                addUser()
            }
        }
    }

    private func addUser() {
        let user = User(fullName: "New User", email: "new@example.com")
        modelContext.insert(user)
    }
}

// Сложные запросы с #Predicate
struct SearchableUserList: View {
    @Environment(\.modelContext) private var modelContext
    @State private var searchText = ""

    var body: some View {
        List {
            ForEach(filteredUsers) { user in
                Text(user.fullName)
            }
        }
        .searchable(text: $searchText)
    }

    private var filteredUsers: [User] {
        let predicate = #Predicate<User> { user in
            searchText.isEmpty || user.fullName.localizedStandardContains(searchText)
        }

        let descriptor = FetchDescriptor<User>(
            predicate: predicate,
            sortBy: [SortDescriptor(\.fullName)]
        )

        return (try? modelContext.fetch(descriptor)) ?? []
    }
}
```

### Room с KSP (Android)

```kotlin
// Room с Kotlin Symbol Processing
import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Entity(tableName = "users")
data class User(
    @PrimaryKey
    val id: String = UUID.randomUUID().toString(),
    val fullName: String,
    val email: String,
    val createdAt: Long = System.currentTimeMillis()
)

@Entity(
    tableName = "posts",
    foreignKeys = [
        ForeignKey(
            entity = User::class,
            parentColumns = ["id"],
            childColumns = ["author_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("author_id")]
)
data class Post(
    @PrimaryKey
    val id: String = UUID.randomUUID().toString(),
    val title: String,
    val content: String,
    @ColumnInfo(name = "author_id")
    val authorId: String,
    @ColumnInfo(name = "published_at")
    val publishedAt: Long? = null
)

// Relation для загрузки связанных данных
data class UserWithPosts(
    @Embedded val user: User,
    @Relation(
        parentColumn = "id",
        entityColumn = "author_id"
    )
    val posts: List<Post>
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun observeAll(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE full_name LIKE '%' || :query || '%'")
    fun search(query: String): Flow<List<User>>

    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserWithPosts(userId: String): UserWithPosts?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(user: User)

    @Delete
    suspend fun delete(user: User)
}

// Использование в ViewModel
class UserViewModel(
    private val userDao: UserDao
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")

    val users: StateFlow<List<User>> = _searchQuery
        .debounce(300)
        .flatMapLatest { query ->
            if (query.isEmpty()) {
                userDao.observeAll()
            } else {
                userDao.search(query)
            }
        }
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun search(query: String) {
        _searchQuery.value = query
    }

    fun addUser(fullName: String, email: String) {
        viewModelScope.launch {
            userDao.upsert(User(fullName = fullName, email = email))
        }
    }
}
```

---

## 5. KMP: SQLDelight для кросс-платформы

```kotlin
// shared/src/commonMain/sqldelight/com/app/db/User.sq
CREATE TABLE User (
    id TEXT NOT NULL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now') * 1000)
);

CREATE INDEX user_email_idx ON User(email);

selectAll:
SELECT * FROM User ORDER BY created_at DESC;

selectById:
SELECT * FROM User WHERE id = ?;

search:
SELECT * FROM User WHERE full_name LIKE '%' || ? || '%';

insert:
INSERT OR REPLACE INTO User(id, full_name, email, created_at)
VALUES (?, ?, ?, ?);

delete:
DELETE FROM User WHERE id = ?;

deleteAll:
DELETE FROM User;
```

```kotlin
// shared/src/commonMain/kotlin/com/app/data/UserRepository.kt
import com.app.db.AppDatabase
import com.app.db.User
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.withContext
import kotlin.coroutines.CoroutineContext

class UserRepository(
    private val database: AppDatabase,
    private val ioContext: CoroutineContext
) {
    private val queries = database.userQueries

    fun observeAll(): Flow<List<User>> =
        queries.selectAll().asFlow().mapToList(ioContext)

    fun search(query: String): Flow<List<User>> =
        queries.search(query).asFlow().mapToList(ioContext)

    suspend fun getById(id: String): User? = withContext(ioContext) {
        queries.selectById(id).executeAsOneOrNull()
    }

    suspend fun save(user: User) = withContext(ioContext) {
        queries.insert(
            id = user.id,
            full_name = user.full_name,
            email = user.email,
            created_at = user.created_at
        )
    }

    suspend fun delete(id: String) = withContext(ioContext) {
        queries.delete(id)
    }
}
```

```kotlin
// shared/src/androidMain/kotlin/com/app/data/DatabaseDriver.kt
import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.android.AndroidSqliteDriver
import android.content.Context
import com.app.db.AppDatabase

actual class DatabaseDriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = AppDatabase.Schema,
            context = context,
            name = "app.db"
        )
    }
}
```

```kotlin
// shared/src/iosMain/kotlin/com/app/data/DatabaseDriver.kt
import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.native.NativeSqliteDriver
import com.app.db.AppDatabase

actual class DatabaseDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = AppDatabase.Schema,
            name = "app.db"
        )
    }
}
```

```swift
// iOS: Использование SQLDelight через Kotlin/Native
import shared

class UserRepositoryWrapper {
    private let repository: UserRepository

    init() {
        let driverFactory = DatabaseDriverFactory()
        let database = AppDatabaseCompanion().invoke(driver: driverFactory.createDriver())
        self.repository = UserRepository(
            database: database,
            ioContext: Dispatchers.shared.IO
        )
    }

    func observeUsers() -> some Publisher<[User], Never> {
        // Используем FlowPublisher из SKIE или KMP-NativeCoroutines
        return createPublisher(for: repository.observeAllNative())
    }
}
```

---

## 6. Шесть распространённых ошибок

### Ошибка 1: Блокировка UI потока

```swift
// iOS: НЕПРАВИЛЬНО — fetch на main thread
func loadUsers() {
    let request = User.fetchRequest()
    let users = try? viewContext.fetch(request) // Блокирует UI!
    updateUI(with: users)
}

// iOS: ПРАВИЛЬНО — background fetch
func loadUsers() {
    let backgroundContext = persistentContainer.newBackgroundContext()
    backgroundContext.perform {
        let request = User.fetchRequest()
        let users = try? backgroundContext.fetch(request)
        DispatchQueue.main.async {
            self.updateUI(with: users)
        }
    }
}
```

```kotlin
// Android: НЕПРАВИЛЬНО — синхронный запрос
fun loadUsers(): List<User> {
    return userDao.getAllSync() // Crash на main thread!
}

// Android: ПРАВИЛЬНО — корутины
fun loadUsers() {
    viewModelScope.launch {
        val users = withContext(Dispatchers.IO) {
            userDao.getAll()
        }
        _uiState.value = users
    }
}
```

### Ошибка 2: Утечка контекста/объектов

```swift
// iOS: НЕПРАВИЛЬНО — использование объекта вне его контекста
var cachedUser: User? // NSManagedObject из другого контекста

func showUser() {
    // cachedUser может быть fault или из другого контекста
    print(cachedUser?.fullName) // Crash или неверные данные!
}

// iOS: ПРАВИЛЬНО — передача ID и повторный fetch
var cachedUserId: UUID?

func showUser() {
    guard let userId = cachedUserId else { return }
    let request = User.fetchRequest()
    request.predicate = NSPredicate(format: "id == %@", userId as CVarArg)
    if let user = try? viewContext.fetch(request).first {
        print(user.fullName)
    }
}
```

```kotlin
// Android: НЕПРАВИЛЬНО — хранение Entity со связями
class UserCache {
    var currentUser: UserWithPosts? = null // Room Entity с lazy relations
}

// Android: ПРАВИЛЬНО — хранение только ID или DTO
class UserCache {
    var currentUserId: String? = null
}

data class UserDto(
    val id: String,
    val fullName: String,
    val postCount: Int
)
```

### Ошибка 3: Игнорирование миграций

```swift
// iOS: НЕПРАВИЛЬНО — нет обработки миграций
let container = NSPersistentContainer(name: "MyApp")
container.loadPersistentStores { _, error in
    // При изменении схемы — crash!
}

// iOS: ПРАВИЛЬНО — настройка миграций
let container = NSPersistentContainer(name: "MyApp")
let description = container.persistentStoreDescriptions.first
description?.shouldMigrateStoreAutomatically = true
description?.shouldInferMappingModelAutomatically = true
container.loadPersistentStores { _, _ in }
```

```kotlin
// Android: НЕПРАВИЛЬНО — fallbackToDestructiveMigration в продакшене
Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .fallbackToDestructiveMigration() // Потеря данных!
    .build()

// Android: ПРАВИЛЬНО — явные миграции
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE users ADD COLUMN avatar_url TEXT")
    }
}

Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .addMigrations(MIGRATION_1_2)
    .build()
```

### Ошибка 4: Хранение токенов в UserDefaults/SharedPreferences

```swift
// iOS: НЕПРАВИЛЬНО — токен в UserDefaults
UserDefaults.standard.set(accessToken, forKey: "token") // Небезопасно!

// iOS: ПРАВИЛЬНО — токен в Keychain
try KeychainManager.shared.save(token.data(using: .utf8)!, for: "token")
```

```kotlin
// Android: НЕПРАВИЛЬНО — токен в SharedPreferences
prefs.edit().putString("token", accessToken).apply() // Небезопасно!

// Android: ПРАВИЛЬНО — EncryptedSharedPreferences
encryptedPrefs.edit().putString("token", accessToken).apply()
```

### Ошибка 5: Отсутствие индексов

```swift
// iOS Core Data: Добавление индекса в модели
// В .xcdatamodeld: выбрать атрибут -> Indexed = YES

// Или программно для Fetch Request
let request = User.fetchRequest()
request.propertiesToFetch = ["id", "fullName"] // Partial fetch
request.returnsObjectsAsFaults = false
```

```kotlin
// Android Room: Индексы в Entity
@Entity(
    tableName = "posts",
    indices = [
        Index(value = ["author_id"]),
        Index(value = ["created_at"]),
        Index(value = ["title", "content"]) // Составной индекс
    ]
)
data class Post(...)
```

### Ошибка 6: N+1 запросы

```swift
// iOS: НЕПРАВИЛЬНО — загрузка связей по одному
let users = try context.fetch(User.fetchRequest())
for user in users {
    print(user.posts.count) // Каждый раз новый запрос!
}

// iOS: ПРАВИЛЬНО — prefetch relationships
let request = User.fetchRequest()
request.relationshipKeyPathsForPrefetching = ["posts"]
let users = try context.fetch(request)
```

```kotlin
// Android: НЕПРАВИЛЬНО — отдельные запросы для связей
val users = userDao.getAll()
users.forEach { user ->
    val posts = postDao.getByAuthor(user.id) // N+1!
}

// Android: ПРАВИЛЬНО — @Transaction с @Relation
@Transaction
@Query("SELECT * FROM users")
suspend fun getUsersWithPosts(): List<UserWithPosts>
```

---

## 7. Три ментальные модели

### Модель 1: Object Graph vs Table Rows

```
Core Data мыслит графами объектов:
┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│  Post   │────▶│ Comment │
└─────────┘     └─────────┘     └─────────┘
     │               │
     └───────────────┘
   Relationships = pointers в памяти
   Fault = proxy до первого обращения

Room мыслит таблицами:
┌──────────────────┐
│ users            │
├──────────────────┤
│ id | name | ...  │
└──────────────────┘
         │ JOIN
         ▼
┌──────────────────┐
│ posts            │
├──────────────────┤
│ id | user_id |...│
└──────────────────┘
   Foreign Keys = явные связи
   @Relation = отдельный SELECT
```

**Вывод:** Core Data оптимизирован для работы с графами объектов в памяти.
Room оптимизирован для SQL-запросов с явным контролем.

### Модель 2: Sync vs Async первичность

```
iOS UserDefaults:
┌─────────────────────────────────────┐
│ Sync-first с async observation     │
│                                     │
│ defaults.set(value) // Мгновенно   │
│ defaults.bool(forKey:) // Мгновенно│
│                                     │
│ + NotificationCenter для изменений │
└─────────────────────────────────────┘

Android DataStore:
┌─────────────────────────────────────┐
│ Async-first с Flow                  │
│                                     │
│ dataStore.data.map { } // Flow     │
│ dataStore.edit { } // suspend      │
│                                     │
│ Всё через корутины                 │
└─────────────────────────────────────┘
```

**Вывод:** iOS традиционно sync-first, Android modern — async-first.
При миграции учитывайте эту разницу в API design.

### Модель 3: Уровни безопасности хранения

```
           Уровень безопасности
                   ▲
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    │  Keychain    │ AndroidKeystore
    │  (hardware)  │ (hardware)   │
    │              │              │
    ├──────────────┼──────────────┤
    │              │              │
    │  Keychain    │ Encrypted    │
    │  (software)  │ SharedPrefs  │
    │              │              │
    ├──────────────┼──────────────┤
    │              │              │
    │ UserDefaults │ SharedPrefs  │
    │ (plist)      │ (xml)        │
    │              │              │
    ├──────────────┼──────────────┤
    │              │              │
    │  Files       │  Files       │
    │ (sandbox)    │ (internal)   │
    │              │              │
    └──────────────┴──────────────┘
                   │
                   ▼
         Уровень доступности
```

**Правило выбора:**
- Токены, пароли → Keychain / EncryptedSharedPreferences
- Настройки пользователя → UserDefaults / DataStore
- Большие данные → Core Data / Room / Files

---

## 8. Quiz: Проверь понимание

### Вопрос 1: Контексты и потокобезопасность

Что произойдёт при выполнении этого кода?

```swift
let backgroundContext = persistentContainer.newBackgroundContext()
backgroundContext.perform {
    let user = User(context: backgroundContext)
    user.fullName = "Test"
    try? backgroundContext.save()

    DispatchQueue.main.async {
        print(user.fullName) // ???
    }
}
```

<details>
<summary>Ответ</summary>

**Потенциальный crash или некорректные данные.**

`NSManagedObject` привязан к своему контексту и потоку. Обращение к `user` из main thread, когда он создан в background context — нарушение thread confinement.

Правильное решение:
```swift
DispatchQueue.main.async {
    let mainUser = self.viewContext.object(with: user.objectID) as? User
    print(mainUser?.fullName)
}
```
</details>

### Вопрос 2: Room и корутины

Почему этот код может вызвать ANR?

```kotlin
@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAllSync(): List<User> // Без suspend
}

class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val users = database.userDao().getAllSync() // ???
    }
}
```

<details>
<summary>Ответ</summary>

**ANR (Application Not Responding)** произойдёт, потому что:

1. `getAllSync()` — синхронный метод без `suspend`
2. Room по умолчанию запрещает запросы на main thread
3. Если разрешить через `.allowMainThreadQueries()`, большой запрос заблокирует UI

Правильное решение:
```kotlin
@Query("SELECT * FROM users")
suspend fun getAll(): List<User>

// В Activity/ViewModel:
lifecycleScope.launch {
    val users = database.userDao().getAll()
}
```
</details>

### Вопрос 3: Безопасность хранения

Какая проблема безопасности в этом коде?

```kotlin
class AuthRepository(context: Context) {
    private val prefs = context.getSharedPreferences("auth", Context.MODE_PRIVATE)

    fun saveTokens(access: String, refresh: String) {
        prefs.edit()
            .putString("access_token", access)
            .putString("refresh_token", refresh)
            .apply()
    }
}
```

<details>
<summary>Ответ</summary>

**Токены хранятся в незашифрованном виде.**

SharedPreferences сохраняет данные в XML файл, который:
- Читается на rooted устройствах
- Может быть извлечён через backup
- Виден в debug builds

Правильное решение:
```kotlin
private val prefs = EncryptedSharedPreferences.create(
    context,
    "auth",
    masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```
</details>

---

## 9. Связь с другими темами

[[android-data-persistence]] — Android предоставляет разнообразные механизмы хранения данных: Room (ORM поверх SQLite с compile-time проверкой запросов), DataStore (замена SharedPreferences с поддержкой Proto и Preferences), EncryptedSharedPreferences для секретных данных. Заметка детально разбирает миграции Room, отношения между Entity, DAO паттерны и интеграцию с Flow для реактивных запросов. Понимание Android persistence необходимо для сравнения с iOS Core Data/SwiftData и для выбора стратегии в KMP-проектах.

[[ios-data-persistence]] — iOS экосистема хранения включает Core Data (мощный ORM с поддержкой миграций, NSFetchedResultsController), SwiftData (современная декларативная обёртка через @Model), UserDefaults, Keychain Services для секретов. Заметка объясняет NSManagedObjectContext, persistent store coordinator, lightweight vs heavyweight миграции и CloudKit синхронизацию. Сравнение с Android Room позволяет увидеть принципиальные различия в подходах к ORM и реактивности данных.

[[mobile-databases-complete]] — Полный обзор мобильных баз данных: SQLite (основа Room и Core Data), Realm (кросс-платформенная альтернатива), SQLDelight (KMP-решение с type-safe SQL), а также специализированные решения вроде MMKV и ObjectBox. Заметка помогает выбрать БД в зависимости от требований: производительность, кросс-платформенность, размер данных, необходимость синхронизации. Это ключевой контекст для принятия архитектурных решений о persistence layer.

---

## 10. Источники и дальнейшее чтение

- Meier R. (2022). *Professional Android.* — Полное руководство по Room, DataStore, ContentProvider и файловому хранению на Android. Включает best practices по миграциям, тестированию DAO и интеграции с Architecture Components.
- Neuburg M. (2023). *iOS Programming Fundamentals with Swift.* — Разбирает Core Data stack, SwiftData, UserDefaults и Keychain. Объясняет модель конкурентного доступа к NSManagedObjectContext и стратегии миграции данных.
- Martin R. (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design.* — Описывает принцип инверсии зависимостей для persistence layer: Repository pattern, разделение Domain и Data слоёв. Напрямую применим к проектированию слоя хранения данных на обеих платформах.
