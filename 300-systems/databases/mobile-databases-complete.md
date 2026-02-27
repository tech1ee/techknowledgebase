---
title: "Mobile Databases: Complete Guide"
type: guide
status: published
tags:
  - topic/databases
  - type/guide
  - level/intermediate
related:
  - "[[android-data-persistence]]"
  - "[[ios-core-data]]"
  - "[[kmp-sqldelight-database]]"
modified: 2026-02-13
prerequisites:
  - "[[databases-sql-fundamentals]]"
reading_time: 24
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Mobile Databases: Complete Guide

> Полное руководство по мобильным базам данных — Android, iOS, Kotlin Multiplatform, Flutter, React Native

---

## Теоретические основы

> **Mobile Database** — встраиваемая СУБД, работающая в процессе мобильного приложения без отдельного сервера. Основной движок — **SQLite** (D. Richard Hipp, 2000): самая распространённая БД в мире (триллионы экземпляров на устройствах).

### SQLite: уникальная архитектура

| Аспект | Серверная СУБД (PostgreSQL) | Встраиваемая (SQLite) |
|--------|---------------------------|----------------------|
| Модель | Client-server (TCP/IP) | In-process (library) |
| Concurrency | Тысячи параллельных транзакций | Single-writer, multiple readers (WAL) |
| Хранилище | Множество файлов, tablespaces | Один файл (`.db`) |
| Размер | ~100MB+ binary | ~600KB library |
| ACID | Полный | Полный (через journaling) |

### Ключевые паттерны мобильных БД

| Паттерн | Проблема | Решение |
|---------|----------|---------|
| **Offline-first** | Нет сети → приложение не работает | Локальная БД + sync при подключении |
| **Optimistic UI** | Ожидание ответа сервера → лагает UI | Запись в локальную БД → async sync |
| **CRDT** (Conflict-free Replicated Data Types) | Конфликты при offline sync | Математически бесконфликтные структуры |
| **Event Sourcing** | Потеря данных при sync | Хранение событий вместо состояния |

> **См. также**: [[databases-sql-fundamentals]] — основы SQL, [[android-data-persistence]] — Android-специфика

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **Основы баз данных** | Понимание SQL, транзакций | [[databases-fundamentals-complete]] |
| **SQLite** | Все мобильные БД построены на SQLite | [[sql-databases-complete]] |
| **Android или iOS разработка** | Понимание хотя бы одной платформы | [[android-basics]] / iOS docs |
| **Kotlin/Swift basics** | Синтаксис языков мобильной разработки | [[kotlin-overview]] / Swift docs |

### Для кого этот материал

| Уровень | Что получите |
|---------|--------------|
| **Android разработчик** | Room, SQLDelight, offline-first архитектура |
| **iOS разработчик** | Core Data, SwiftData, GRDB |
| **Cross-platform** | Kotlin Multiplatform, Flutter, React Native решения |

---

## Терминология

> 💡 **Главная аналогия:**
>
> Мобильная БД = **блокнот в кармане**. Всегда с собой, работает без интернета. Sync = периодически сверяем записи с общим журналом на сервере.

| Термин | Значение | Аналогия |
|--------|----------|----------|
| **Room** | Android ORM поверх SQLite от Google | **Официальный переводчик** — Kotlin/Java ↔ SQLite |
| **Core Data** | Apple framework для persistence | **Яблочный органайзер** — не просто БД, а Object Graph |
| **SQLDelight** | Kotlin Multiplatform, SQL-first | **Универсальный переводчик** — один SQL для Android и iOS |
| **Offline-First** | Приложение работает без сети, синхронизируется потом | **Блокнот** — записал, потом переписал в общий журнал |
| **Migration** | Обновление схемы БД между версиями приложения | **Ремонт блокнота** — добавляем новые страницы, не теряя записи |
| **DAO** | Data Access Object — интерфейс к данным | **Секретарь** — принимает запросы, возвращает данные |
| **Entity** | Класс, отображаемый на таблицу | **Шаблон карточки** — структура записи |
| **TypeConverter** | Преобразование типов (Date → Long) | **Переводчик форматов** — дату в число и обратно |
| **Flow/LiveData** | Реактивные потоки данных | **Подписка на обновления** — данные изменились → UI обновился |
| **WAL mode** | Write-Ahead Logging для SQLite | **Журнал изменений** — сначала в журнал, потом в файл |

---

## Table of Contents

1. [Введение](#введение)
2. [SQLite Internals](#sqlite-internals)
3. [Android Databases](#android-databases)
   - [Room Database](#room-database)
   - [SQLDelight](#sqldelight)
   - [ObjectBox](#objectbox)
4. [iOS Databases](#ios-databases)
   - [Core Data](#core-data)
   - [SwiftData](#swiftdata)
   - [GRDB.swift](#grdbswift)
5. [Cross-Platform Databases](#cross-platform-databases)
   - [Kotlin Multiplatform](#kotlin-multiplatform)
   - [Flutter Databases](#flutter-databases)
   - [React Native](#react-native)
6. [Realm: Status & Alternatives](#realm-status--alternatives)
7. [Offline-First Architecture](#offline-first-architecture)
8. [Database Encryption](#database-encryption)
9. [Testing Strategies](#testing-strategies)
10. [Performance Optimization](#performance-optimization)
11. [Decision Guide](#decision-guide)

---

## Введение

### Зачем мобильным приложениям локальная БД?

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Why Mobile Apps Need Local Databases                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  1. OFFLINE AVAILABILITY                                                     │
│     User opens app with no network → data still accessible                  │
│                                                                              │
│  2. PERFORMANCE                                                              │
│     Local read: ~1ms | Network request: 100-1000ms                          │
│                                                                              │
│  3. REDUCED NETWORK COSTS                                                    │
│     Cache data locally, sync only changes                                   │
│                                                                              │
│  4. BATTERY EFFICIENCY                                                       │
│     Network operations drain battery; local queries don't                   │
│                                                                              │
│  5. DATA PERSISTENCE                                                         │
│     Survive app restarts, maintain user state                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Типы мобильных баз данных

| Тип | Примеры | Характеристики |
|-----|---------|----------------|
| SQLite-based | Room, SQLDelight, GRDB | Relational, SQL queries |
| Object-oriented | ObjectBox, Realm | NoSQL, object persistence |
| Key-Value | MMKV, DataStore | Simple, fast preferences |
| Document | Couchbase Lite | JSON documents |

---

## SQLite Internals

### Архитектура SQLite

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SQLite Architecture                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    SQL Compiler Frontend                             │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────┐  │    │
│  │  │  Tokenizer  │→ │   Parser    │→ │ Code Generator (VDBE code)  │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Virtual Database Engine (VDBE)                    │    │
│  │               Executes bytecode (like mini-VM)                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         B-Tree Module                                │    │
│  │  ┌──────────────────────────────────────────────────────────────┐   │    │
│  │  │ Tables: Rowid B-Tree   |   Indexes: B+Tree (sorted keys)     │   │    │
│  │  └──────────────────────────────────────────────────────────────┘   │    │
│  │  • Page size: 4096 bytes (default)                                  │    │
│  │  • Interior pages: keys + child pointers                            │    │
│  │  • Leaf pages: actual data                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          Pager Layer                                 │    │
│  │  ┌──────────────────┐  ┌─────────────────────────────────────────┐  │    │
│  │  │ Page Cache       │  │ Transaction Manager                      │  │    │
│  │  │ (LRU cache)      │  │ (Rollback Journal OR WAL)               │  │    │
│  │  └──────────────────┘  └─────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        OS Interface (VFS)                            │    │
│  │         File I/O, Locking (POSIX locks, Windows locks)               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### WAL Mode vs Rollback Journal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Write-Ahead Logging (WAL) Mode                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ROLLBACK JOURNAL (Legacy):                                                  │
│  ──────────────────────────                                                  │
│  1. Before write: Copy original page → journal file                         │
│  2. Modify page in main DB                                                   │
│  3. Commit: Delete journal file                                              │
│  4. Crash recovery: Replay journal to restore                               │
│                                                                              │
│  Limitations: Writers block readers, synchronous I/O                        │
│                                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                              │
│  WAL MODE (Recommended for mobile):                                          │
│  ───────────────────────────────────                                         │
│  1. Write: Append changes → WAL file                                         │
│  2. Commit: Write commit record to WAL                                       │
│  3. Readers: Check WAL first, then main DB                                   │
│  4. Checkpoint: WAL changes → main DB (automatic)                           │
│                                                                              │
│  Benefits:                                                                   │
│  • 4x faster writes (sequential I/O)                                        │
│  • Concurrent readers + 1 writer                                            │
│  • Fewer fsync() calls                                                       │
│  • synchronous=NORMAL is safe                                                │
│                                                                              │
│  Files: database.db, database.db-wal, database.db-shm                       │
│                                                                              │
│  Limitation: All processes must be on same host (no network FS)             │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Performance Tips

```sql
-- Enable WAL mode (do once at app start)
PRAGMA journal_mode = WAL;

-- Safe for WAL, faster than FULL
PRAGMA synchronous = NORMAL;

-- Use more memory for better performance
PRAGMA cache_size = -64000;  -- 64MB

-- Optimize after operations
PRAGMA optimize;

-- Analyze for query planner
ANALYZE;

-- Check query plan
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';
```

---

## Android Databases

### Room Database

#### Архитектура

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Room Architecture                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                       Application Layer                              │    │
│  │                                                                      │    │
│  │  ┌───────────────┐    ┌───────────────┐    ┌───────────────┐        │    │
│  │  │   ViewModel   │ →  │  Repository   │ →  │      DAO      │        │    │
│  │  └───────────────┘    └───────────────┘    └───────┬───────┘        │    │
│  │                                                    │                 │    │
│  └────────────────────────────────────────────────────┼─────────────────┘    │
│                                                       ↓                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Room Library                                 │    │
│  │                                                                      │    │
│  │  ┌───────────────────────────────────────────────────────────────┐  │    │
│  │  │                    @Database                                   │  │    │
│  │  │  • Defines entities (tables)                                  │  │    │
│  │  │  • Provides DAOs                                               │  │    │
│  │  │  • Version management                                          │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                              │                                       │    │
│  │  ┌───────────────────────────┴───────────────────────────────────┐  │    │
│  │  │              Generated Implementation                          │  │    │
│  │  │  • DAO implementations                                         │  │    │
│  │  │  • SQL statements                                              │  │    │
│  │  │  • Type converters                                             │  │    │
│  │  └───────────────────────────────────────────────────────────────┘  │    │
│  │                              │                                       │    │
│  └──────────────────────────────┼───────────────────────────────────────┘    │
│                                 ↓                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         SQLite (via SupportSQLite)                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### Setup (Kotlin DSL)

```kotlin
// build.gradle.kts
plugins {
    id("com.google.devtools.ksp") version "2.0.0-1.0.21"  // KSP instead of KAPT
}

dependencies {
    val roomVersion = "2.7.0-alpha01"  // KMP support

    implementation("androidx.room:room-runtime:$roomVersion")
    implementation("androidx.room:room-ktx:$roomVersion")  // Coroutines support
    ksp("androidx.room:room-compiler:$roomVersion")

    // Testing
    testImplementation("androidx.room:room-testing:$roomVersion")
}

// Schema export for migrations
ksp {
    arg("room.schemaLocation", "$projectDir/schemas")
}
```

#### Entity Definition

```kotlin
import androidx.room.*
import kotlinx.datetime.Instant

@Entity(
    tableName = "users",
    indices = [
        Index(value = ["email"], unique = true),
        Index(value = ["created_at"])
    ]
)
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,

    @ColumnInfo(name = "email")
    val email: String,

    @ColumnInfo(name = "display_name")
    val displayName: String,

    @ColumnInfo(name = "avatar_url")
    val avatarUrl: String? = null,

    @ColumnInfo(name = "is_premium")
    val isPremium: Boolean = false,

    @ColumnInfo(name = "created_at")
    val createdAt: Instant = Clock.System.now()
)

// Embedded object
data class Address(
    val street: String,
    val city: String,
    val zipCode: String
)

@Entity(tableName = "orders")
data class Order(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,

    @ColumnInfo(name = "user_id")
    val userId: Long,

    @Embedded(prefix = "shipping_")
    val shippingAddress: Address,

    val total: Double
)

// Relations
data class UserWithOrders(
    @Embedded val user: User,
    @Relation(
        parentColumn = "id",
        entityColumn = "user_id"
    )
    val orders: List<Order>
)
```

#### DAO with Flow

```kotlin
@Dao
interface UserDao {
    // Reactive query with Flow
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAllUsers(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE id = :id")
    fun getUserById(id: Long): Flow<User?>

    // Suspend functions for one-shot operations
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: User): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUsers(users: List<User>)

    @Update
    suspend fun updateUser(user: User)

    @Delete
    suspend fun deleteUser(user: User)

    @Query("DELETE FROM users WHERE id = :id")
    suspend fun deleteUserById(id: Long)

    // Transaction for complex operations
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    fun getUserWithOrders(userId: Long): Flow<UserWithOrders?>

    // Pagination with Paging 3
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getPagedUsers(): PagingSource<Int, User>
}
```

#### Database Class

```kotlin
@Database(
    entities = [User::class, Order::class],
    version = 2,
    autoMigrations = [
        AutoMigration(from = 1, to = 2)
    ],
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun orderDao(): OrderDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getInstance(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                )
                .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING)
                .addCallback(DatabaseCallback())
                .build()

                INSTANCE = instance
                instance
            }
        }
    }
}

// Type converters
class Converters {
    @TypeConverter
    fun fromInstant(value: Instant): Long = value.toEpochMilliseconds()

    @TypeConverter
    fun toInstant(value: Long): Instant = Instant.fromEpochMilliseconds(value)
}
```

#### Migration

```kotlin
// Manual migration when auto-migration not possible
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL(
            "ALTER TABLE users ADD COLUMN is_premium INTEGER NOT NULL DEFAULT 0"
        )
    }
}

// Usage
Room.databaseBuilder(context, AppDatabase::class.java, "app_database")
    .addMigrations(MIGRATION_1_2)
    .build()
```

### SQLDelight

#### Setup

```kotlin
// build.gradle.kts
plugins {
    id("app.cash.sqldelight") version "2.0.1"
}

sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.db")
            dialect("app.cash.sqldelight:sqlite-3-38-dialect:2.0.1")
        }
    }
}

dependencies {
    implementation("app.cash.sqldelight:android-driver:2.0.1")
    implementation("app.cash.sqldelight:coroutines-extensions:2.0.1")
}
```

#### SQL Files

```sql
-- src/main/sqldelight/com/example/db/User.sq

CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX idx_user_email ON User(email);

-- Queries
selectAll:
SELECT * FROM User ORDER BY created_at DESC;

selectById:
SELECT * FROM User WHERE id = ?;

selectByEmail:
SELECT * FROM User WHERE email = ?;

insert:
INSERT INTO User(email, display_name) VALUES (?, ?);

update:
UPDATE User SET email = ?, display_name = ? WHERE id = ?;

delete:
DELETE FROM User WHERE id = ?;
```

#### Usage

```kotlin
// Create driver
val driver: SqlDriver = AndroidSqliteDriver(AppDatabase.Schema, context, "app.db")
val database = AppDatabase(driver)
val userQueries = database.userQueries

// Insert
userQueries.insert("user@example.com", "John Doe")

// Query with Flow
val users: Flow<List<User>> = userQueries.selectAll()
    .asFlow()
    .mapToList(Dispatchers.IO)

// Collect
users.collect { userList ->
    println("Users: $userList")
}
```

### ObjectBox

```kotlin
// build.gradle.kts
plugins {
    id("io.objectbox")
}

// Entity
@Entity
data class User(
    @Id var id: Long = 0,
    @Index var email: String = "",
    var displayName: String = ""
)

// Usage
val boxStore = MyObjectBox.builder()
    .androidContext(context)
    .build()

val userBox = boxStore.boxFor(User::class.java)

// Insert
val user = User(email = "test@example.com", displayName = "Test")
userBox.put(user)

// Query
val users = userBox.query()
    .equal(User_.email, "test@example.com", StringOrder.CASE_INSENSITIVE)
    .build()
    .find()
```

---

## iOS Databases

### Core Data

```swift
import CoreData

// Entity (defined in .xcdatamodeld)
// Or programmatically:
@objc(User)
public class User: NSManagedObject {
    @NSManaged public var id: UUID
    @NSManaged public var email: String
    @NSManaged public var displayName: String
    @NSManaged public var createdAt: Date
}

// Persistent Container
class CoreDataStack {
    static let shared = CoreDataStack()

    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "MyApp")

        // Enable WAL mode
        let description = container.persistentStoreDescriptions.first
        description?.setOption(true as NSNumber, forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)

        container.loadPersistentStores { _, error in
            if let error = error {
                fatalError("Failed to load store: \(error)")
            }
        }
        return container
    }()

    var viewContext: NSManagedObjectContext {
        persistentContainer.viewContext
    }

    // Background context for heavy operations
    func newBackgroundContext() -> NSManagedObjectContext {
        persistentContainer.newBackgroundContext()
    }

    func save() {
        let context = viewContext
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Save error: \(error)")
            }
        }
    }
}

// Usage
let context = CoreDataStack.shared.viewContext

// Create
let user = User(context: context)
user.id = UUID()
user.email = "test@example.com"
user.displayName = "Test User"
user.createdAt = Date()

CoreDataStack.shared.save()

// Fetch
let request: NSFetchRequest<User> = User.fetchRequest()
request.predicate = NSPredicate(format: "email == %@", "test@example.com")
request.sortDescriptors = [NSSortDescriptor(keyPath: \User.createdAt, ascending: false)]

let users = try? context.fetch(request)
```

### SwiftData (iOS 17+)

```swift
import SwiftData

// Model definition - no separate file needed!
@Model
class User {
    @Attribute(.unique) var email: String
    var displayName: String
    var createdAt: Date

    init(email: String, displayName: String) {
        self.email = email
        self.displayName = displayName
        self.createdAt = Date()
    }
}

// In SwiftUI App
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: User.self)  // Auto setup!
    }
}

// In SwiftUI View
struct UserListView: View {
    @Query(sort: \User.createdAt, order: .reverse)
    var users: [User]

    @Environment(\.modelContext) private var context

    var body: some View {
        List(users) { user in
            Text(user.displayName)
        }
        .toolbar {
            Button("Add") {
                let user = User(email: "new@example.com", displayName: "New User")
                context.insert(user)
                // Auto-save!
            }
        }
    }
}
```

### GRDB.swift

```swift
import GRDB

// Record definition
struct User: Codable, FetchableRecord, PersistableRecord {
    var id: Int64?
    var email: String
    var displayName: String
    var createdAt: Date

    // Auto-increment
    mutating func didInsert(_ inserted: InsertionSuccess) {
        id = inserted.rowID
    }
}

// Database setup
let dbQueue = try DatabaseQueue(path: dbPath)

try dbQueue.write { db in
    try db.create(table: "user") { t in
        t.autoIncrementedPrimaryKey("id")
        t.column("email", .text).notNull().unique()
        t.column("displayName", .text).notNull()
        t.column("createdAt", .datetime).notNull()
    }
}

// Insert
try dbQueue.write { db in
    var user = User(id: nil, email: "test@example.com", displayName: "Test", createdAt: Date())
    try user.insert(db)
}

// Query with observation
let observation = ValueObservation.tracking { db in
    try User.fetchAll(db)
}

let cancellable = observation.start(in: dbQueue, onError: { error in
    print("Error: \(error)")
}, onChange: { users in
    print("Users: \(users)")
})
```

---

## Cross-Platform Databases

### Kotlin Multiplatform

#### Room KMP (2.7.0+)

```kotlin
// shared/build.gradle.kts
kotlin {
    androidTarget()
    iosX64()
    iosArm64()
    iosSimulatorArm64()

    sourceSets {
        commonMain.dependencies {
            implementation("androidx.room:room-runtime:2.7.0-alpha01")
        }
    }
}

// shared/src/commonMain/kotlin/Database.kt
@Database(entities = [User::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}

expect fun createDatabaseBuilder(context: Any?): RoomDatabase.Builder<AppDatabase>
```

#### SQLDelight KMP

```kotlin
// shared/build.gradle.kts
sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.shared.db")
        }
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation("app.cash.sqldelight:runtime:2.0.1")
            implementation("app.cash.sqldelight:coroutines-extensions:2.0.1")
        }
        androidMain.dependencies {
            implementation("app.cash.sqldelight:android-driver:2.0.1")
        }
        iosMain.dependencies {
            implementation("app.cash.sqldelight:native-driver:2.0.1")
        }
    }
}

// Platform-specific drivers
// androidMain
actual fun createDriver(context: Context): SqlDriver =
    AndroidSqliteDriver(AppDatabase.Schema, context, "app.db")

// iosMain
actual fun createDriver(): SqlDriver =
    NativeSqliteDriver(AppDatabase.Schema, "app.db")
```

### Flutter Databases

#### Drift (Recommended)

```dart
// pubspec.yaml
dependencies:
  drift: ^2.14.0
  sqlite3_flutter_libs: ^0.5.18

dev_dependencies:
  drift_dev: ^2.14.0
  build_runner: ^2.4.6

// database.dart
import 'package:drift/drift.dart';

part 'database.g.dart';

class Users extends Table {
  IntColumn get id => integer().autoIncrement()();
  TextColumn get email => text().unique()();
  TextColumn get displayName => text()();
  DateTimeColumn get createdAt => dateTime().withDefault(currentDateAndTime)();
}

@DriftDatabase(tables: [Users])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  @override
  int get schemaVersion => 1;

  // Queries
  Stream<List<User>> watchAllUsers() => select(users).watch();

  Future<int> insertUser(UsersCompanion user) => into(users).insert(user);

  Future<void> updateUser(User user) => update(users).replace(user);

  Future<int> deleteUser(int id) =>
      (delete(users)..where((t) => t.id.equals(id))).go();
}

LazyDatabase _openConnection() {
  return LazyDatabase(() async {
    final dbFolder = await getApplicationDocumentsDirectory();
    final file = File(p.join(dbFolder.path, 'app.db'));
    return NativeDatabase.createInBackground(file);
  });
}

// Usage
final db = AppDatabase();

// Watch
db.watchAllUsers().listen((users) {
  print('Users: $users');
});

// Insert
await db.insertUser(UsersCompanion.insert(
  email: 'test@example.com',
  displayName: 'Test User',
));
```

### React Native

#### WatermelonDB

```javascript
// model/User.js
import { Model } from '@nozbe/watermelondb';
import { field, date, readonly } from '@nozbe/watermelondb/decorators';

export default class User extends Model {
  static table = 'users';

  @field('email') email;
  @field('display_name') displayName;
  @readonly @date('created_at') createdAt;
}

// schema.js
import { appSchema, tableSchema } from '@nozbe/watermelondb';

export const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'users',
      columns: [
        { name: 'email', type: 'string', isIndexed: true },
        { name: 'display_name', type: 'string' },
        { name: 'created_at', type: 'number' },
      ],
    }),
  ],
});

// database.js
import { Database } from '@nozbe/watermelondb';
import SQLiteAdapter from '@nozbe/watermelondb/adapters/sqlite';
import { schema } from './schema';
import User from './model/User';

const adapter = new SQLiteAdapter({
  schema,
  jsi: true, // Enable JSI for better performance
  onSetUpError: (error) => {
    console.error('Database setup error:', error);
  },
});

export const database = new Database({
  adapter,
  modelClasses: [User],
});

// Usage in component
import { useDatabase } from '@nozbe/watermelondb/hooks';

function UserList() {
  const database = useDatabase();

  const [users, setUsers] = useState([]);

  useEffect(() => {
    const subscription = database.collections
      .get('users')
      .query()
      .observe()
      .subscribe((users) => setUsers(users));

    return () => subscription.unsubscribe();
  }, []);

  const addUser = async () => {
    await database.write(async () => {
      await database.collections.get('users').create((user) => {
        user.email = 'new@example.com';
        user.displayName = 'New User';
      });
    });
  };

  return (
    <View>
      {users.map((user) => (
        <Text key={user.id}>{user.displayName}</Text>
      ))}
      <Button onPress={addUser} title="Add User" />
    </View>
  );
}
```

---

## Realm: Status & Alternatives

### Deprecation Timeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Realm Deprecation Timeline                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  September 2024                September 2025                                │
│       │                              │                                       │
│       ▼                              ▼                                       │
│  ┌─────────────────┐          ┌─────────────────┐                           │
│  │ MongoDB announces│          │ Atlas Device    │                           │
│  │ deprecation      │ ──────→ │ Sync SHUTDOWN   │                           │
│  └─────────────────┘          └─────────────────┘                           │
│                                                                              │
│  What's affected:                                                            │
│  • Atlas Device Sync (server)                                               │
│  • Atlas Device SDKs (Realm SDKs)                                           │
│  • Edge Server                                                               │
│                                                                              │
│  What remains:                                                               │
│  • Realm open source (local-only) — but unmaintained                        │
│  • Community forks                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Migration Options

| From Realm | To | Effort | Sync Support |
|------------|-----|--------|--------------|
| Realm + Sync | PowerSync + SQLite | Medium | PostgreSQL/MongoDB |
| Realm + Sync | ObjectBox + Sync | Medium | ObjectBox Cloud |
| Realm + Sync | Couchbase Mobile | High | Full sync |
| Realm local | Room/SQLDelight | Medium | None (add PowerSync) |
| Realm local | ObjectBox | Low | Optional |

### PowerSync Example

```kotlin
// Android with Room + PowerSync
dependencies {
    implementation("com.powersync:powersync-sqlite:0.2.0")
}

// Setup
val database = PowerSyncDatabase(
    context = context,
    schema = Schema(
        tables = listOf(
            Table(
                name = "users",
                columns = listOf(
                    Column("email", ColumnType.TEXT),
                    Column("display_name", ColumnType.TEXT)
                )
            )
        )
    )
)

// Connect to backend
val connector = YourBackendConnector()  // Implements PowerSyncBackendConnector
database.connect(connector)

// Use like normal SQLite
database.execute("INSERT INTO users (id, email) VALUES (?, ?)", listOf(uuid, email))
```

---

## Offline-First Architecture

### Pattern Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     Offline-First Architecture                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                          UI Layer                                    │    │
│  │  • Always reads from local database                                  │    │
│  │  • Instant response (no loading spinners for data)                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                    │                                         │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        Repository Layer                              │    │
│  │  • Single Source of Truth: LOCAL DATABASE                           │    │
│  │  • Network is just a sync mechanism                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                     │                               │                        │
│                     ↓                               ↓                        │
│  ┌─────────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │      Local Database         │  │         Sync Queue                   │   │
│  │  • Room/SQLDelight/etc      │  │  • Pending writes                    │   │
│  │  • Immediate writes         │  │  • Retry with backoff               │   │
│  │  • Flow/StateFlow for UI    │  │  • WorkManager for Android          │   │
│  └─────────────────────────────┘  └─────────────────────────────────────┘   │
│                                                    │                         │
│                                                    ↓                         │
│                                    ┌─────────────────────────────────────┐   │
│                                    │         Sync Engine                  │   │
│                                    │  • Delta sync (only changes)        │   │
│                                    │  • Conflict resolution              │   │
│                                    │  • Retry on network restore         │   │
│                                    └─────────────────────────────────────┘   │
│                                                    │                         │
│                                                    ↓                         │
│                                    ┌─────────────────────────────────────┐   │
│                                    │         Remote Server                │   │
│                                    └─────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Conflict Resolution Strategies

```kotlin
sealed class ConflictResolution {
    object LastWriteWins : ConflictResolution()
    object ServerWins : ConflictResolution()
    object ClientWins : ConflictResolution()
    data class FieldMerge(val mergeLogic: (ServerData, ClientData) -> MergedData) : ConflictResolution()
    object ManualResolution : ConflictResolution()
}

// Example: Field-level merge
fun mergeUser(server: User, client: User): User {
    return User(
        id = server.id,
        // Take newer email
        email = if (server.emailUpdatedAt > client.emailUpdatedAt) server.email else client.email,
        // Take newer name
        displayName = if (server.nameUpdatedAt > client.nameUpdatedAt) server.displayName else client.displayName,
        // Merge preferences (both sides)
        preferences = server.preferences + client.preferences
    )
}
```

---

## Database Encryption

### SQLCipher with Room

```kotlin
// build.gradle.kts
dependencies {
    implementation("net.zetetic:sqlcipher-android:4.9.0")
    implementation("androidx.sqlite:sqlite-ktx:2.4.0")
}

// Database setup
class EncryptedDatabaseFactory(private val context: Context) {
    fun create(): AppDatabase {
        // Get or generate encryption key
        val passphrase = getOrCreatePassphrase()

        val factory = SupportSQLiteOpenHelper.Factory { configuration ->
            val options = SQLiteDatabaseConfiguration(
                configuration.context.filesDir.path + "/" + configuration.name,
                configuration.callback.version,
                passphrase
            )
            SQLiteDatabase.openOrCreateDatabase(options)
        }

        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "encrypted.db"
        )
        .openHelperFactory(factory)
        .build()
    }

    private fun getOrCreatePassphrase(): ByteArray {
        val sharedPrefs = EncryptedSharedPreferences.create(
            context,
            "db_prefs",
            MasterKey.Builder(context)
                .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                .build(),
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )

        val existingKey = sharedPrefs.getString("db_key", null)
        if (existingKey != null) {
            return Base64.decode(existingKey, Base64.DEFAULT)
        }

        val newKey = ByteArray(32).also { SecureRandom().nextBytes(it) }
        sharedPrefs.edit()
            .putString("db_key", Base64.encodeToString(newKey, Base64.DEFAULT))
            .apply()

        return newKey
    }
}
```

---

## Testing Strategies

### Room Instrumented Tests

```kotlin
@RunWith(AndroidJUnit4::class)
@SmallTest
class UserDaoTest {
    private lateinit var database: AppDatabase
    private lateinit var userDao: UserDao

    @Before
    fun setup() {
        // In-memory database for isolated tests
        database = Room.inMemoryDatabaseBuilder(
            ApplicationProvider.getApplicationContext(),
            AppDatabase::class.java
        )
        .allowMainThreadQueries()  // OK for tests
        .build()

        userDao = database.userDao()
    }

    @After
    fun teardown() {
        database.close()
    }

    @Test
    fun insertAndRetrieveUser() = runTest {
        // Given
        val user = User(email = "test@example.com", displayName = "Test")

        // When
        userDao.insertUser(user)
        val result = userDao.getUserByEmail("test@example.com").first()

        // Then
        assertThat(result?.email).isEqualTo("test@example.com")
    }

    @Test
    fun deleteUser() = runTest {
        // Given
        val user = User(email = "delete@example.com", displayName = "Delete")
        val id = userDao.insertUser(user)

        // When
        userDao.deleteUserById(id)
        val result = userDao.getUserById(id).first()

        // Then
        assertThat(result).isNull()
    }
}
```

### Migration Tests

```kotlin
@RunWith(AndroidJUnit4::class)
class MigrationTest {
    @get:Rule
    val helper = MigrationTestHelper(
        InstrumentationRegistry.getInstrumentation(),
        AppDatabase::class.java
    )

    @Test
    fun migrate1To2() {
        // Create database version 1
        helper.createDatabase("test.db", 1).apply {
            execSQL("INSERT INTO users (email, display_name) VALUES ('test@example.com', 'Test')")
            close()
        }

        // Run migration
        helper.runMigrationsAndValidate("test.db", 2, true, MIGRATION_1_2)

        // Verify data preserved
        val db = helper.openDatabase("test.db")
        val cursor = db.query("SELECT * FROM users WHERE email = 'test@example.com'")

        assertThat(cursor.count).isEqualTo(1)
        cursor.moveToFirst()
        assertThat(cursor.getInt(cursor.getColumnIndex("is_premium"))).isEqualTo(0)  // Default value
    }
}
```

---

## Performance Optimization

### Android/Room Optimization

```kotlin
// 1. Enable WAL mode
Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
    .setJournalMode(JournalMode.WRITE_AHEAD_LOGGING)
    .build()

// 2. Use transactions for batch operations
suspend fun insertUsers(users: List<User>) {
    database.withTransaction {
        users.forEach { userDao.insertUser(it) }
    }
}

// 3. Index frequently queried columns
@Entity(
    indices = [
        Index("email"),
        Index("created_at")
    ]
)
data class User(...)

// 4. Pagination for large datasets
@Dao
interface UserDao {
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getPagedUsers(): PagingSource<Int, User>
}

// 5. Use distinctUntilChanged for Flow
userDao.getAllUsers()
    .distinctUntilChanged()
    .collect { users -> /* update UI */ }

// 6. Limit query results
@Query("SELECT * FROM users ORDER BY created_at DESC LIMIT :limit")
fun getRecentUsers(limit: Int): Flow<List<User>>
```

### iOS/SQLite Optimization

```swift
// Enable WAL mode
try db.execute(sql: "PRAGMA journal_mode = WAL")
try db.execute(sql: "PRAGMA synchronous = NORMAL")

// Increase cache size
try db.execute(sql: "PRAGMA cache_size = -64000")  // 64MB

// Use transactions
try dbQueue.write { db in
    for user in users {
        try user.insert(db)
    }
}

// Run ANALYZE periodically
try db.execute(sql: "ANALYZE")

// Optimize on close
try db.execute(sql: "PRAGMA optimize")
```

---

## Decision Guide

### Quick Reference Table

| Platform | Recommended | Alternative | For Performance |
|----------|-------------|-------------|-----------------|
| Android Only | Room + Flow | SQLDelight | ObjectBox |
| iOS Only | SwiftData (17+) | Core Data | GRDB |
| Kotlin Multiplatform | Room KMP / SQLDelight | - | - |
| Flutter | Drift | sqflite | ObjectBox |
| React Native | WatermelonDB | AsyncStorage | - |
| With Sync | PowerSync | Couchbase | - |

### Decision Flowchart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    Mobile Database Decision Tree                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  What platform?                                                              │
│       │                                                                      │
│  ┌────┼────┬────────────┬──────────────┬─────────────┐                      │
│  ↓    ↓    ↓            ↓              ↓             ↓                      │
│ Android iOS  KMP      Flutter       React        Cross-                      │
│ Only   Only           Native        Platform                                 │
│  │      │     │         │             │             │                        │
│  ↓      ↓     ↓         ↓             ↓             ↓                        │
│ Room SwiftData Room  Drift     WatermelonDB    SQLite                        │
│       or      or                               (raw)                         │
│     CoreData SQLDelight                                                      │
│                                                                              │
│  Need sync?                                                                  │
│       │                                                                      │
│  ┌────┴────┐                                                                │
│  Yes       No                                                                │
│   │         │                                                                │
│   ↓         ↓                                                                │
│ PowerSync  Continue                                                          │
│ Couchbase  with local                                                        │
│ ObjectBox  database                                                          │
│                                                                              │
│  Performance critical?                                                       │
│       │                                                                      │
│  ┌────┴────┐                                                                │
│  Yes       No                                                                │
│   │         │                                                                │
│   ↓         ↓                                                                │
│ ObjectBox  Use                                                               │
│ GRDB       recommended                                                       │
│            default                                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Key Takeaways

1. **SQLite is the foundation** — Room, SQLDelight, GRDB, Core Data all use SQLite
2. **WAL mode is essential** — 4x write performance, concurrent reads
3. **Room KMP changes the game** — Official Android library now works cross-platform
4. **Realm is deprecated** — Migrate to alternatives (PowerSync, ObjectBox)
5. **Offline-first is not optional** — Local DB should be single source of truth
6. **Test migrations** — 23% of crashes come from bad database implementations

### Best Practices Checklist

- [ ] Enable WAL mode
- [ ] Use background threads for DB operations
- [ ] Test migrations with real data
- [ ] Index frequently queried columns
- [ ] Use transactions for batch operations
- [ ] Implement pagination for large datasets
- [ ] Encrypt sensitive data (SQLCipher)
- [ ] Monitor database size (<200MB optimal)
- [ ] Use Flow/StateFlow for reactive UI updates

## Связь с другими темами

[[android-data-persistence]] — Data persistence на Android описывает полный стек хранения данных: SharedPreferences для простых настроек, Room для реляционных данных, DataStore для типизированных настроек. Текущий документ углубляет тему Room и SQLDelight, сравнивая их с iOS и cross-platform альтернативами. Рекомендуется изучить android-data-persistence для Android-специфичного контекста.

[[ios-core-data]] — Core Data является основным фреймворком Apple для persistence, но работает принципиально иначе, чем Room: это Object Graph Manager, а не ORM. Понимание Core Data помогает оценить преимущества и ограничения кросс-платформенных решений (SQLDelight, Room KMP) и принять решение о shared database layer. Рекомендуется для iOS-разработчиков и KMP-архитекторов.

[[kmp-sqldelight-database]] — SQLDelight для Kotlin Multiplatform предоставляет SQL-first подход к кросс-платформенным базам данных: пишешь SQL, получаешь type-safe Kotlin API для Android, iOS, Desktop. Этот материал углубляет раздел о кросс-платформенных решениях из текущего документа и необходим для проектирования shared data layer в KMP-проектах.

[[databases-fundamentals-complete]] — Фундаментальные концепции баз данных (SQL, индексы, транзакции, нормализация) применимы и к мобильным БД: SQLite использует B-Tree индексы, Room обеспечивает ACID через транзакции, WAL mode улучшает concurrent access. Без этого фундамента сложно оптимизировать производительность мобильной базы данных.

## Источники и дальнейшее чтение

### Теоретические основы
- Shapiro M. et al. (2011). *Conflict-free Replicated Data Types*. — CRDT: математически бесконфликтная синхронизация для offline-first
- Hipp D.R. (2000). *SQLite*. — Самая распространённая БД в мире, основа всех мобильных платформ

### Практические руководства
- Kleppmann M. (2017). *Designing Data-Intensive Applications*. — Storage engines, репликация, механизмы SQLite (B-Tree, WAL)
- Redmond E., Wilson J.R. (2012). *Seven Databases in Seven Weeks*. — Обзор моделей данных для выбора мобильной БД
- Date C.J. (2003). *An Introduction to Database Systems*. — Теория реляционных БД для проектирования мобильных схем

---

---

## Проверь себя

> [!question]- Почему Room (Android) и Core Data (iOS) работают принципиально по-разному, хотя оба используют SQLite?
> Room — это ORM поверх SQLite: пишешь SQL-запросы (через аннотации @Query), получаешь type-safe доступ к данным. Core Data — Object Graph Manager: работает с объектами и их связями, а SQL генерируется под капотом. Room ближе к «чистому SQL», Core Data — к объектной модели. Поэтому Room-опыт не переносится напрямую на Core Data.

> [!question]- Когда SQLDelight лучше Room для KMP-проекта?
> SQLDelight: SQL-first (пишешь .sq файлы с SQL), генерирует Kotlin API, работает на Android/iOS/Desktop/Web — истинный мультиплатформенный. Room: только Android (KMP-поддержка экспериментальная), аннотации вместо SQL. Для KMP-проекта с shared data layer SQLDelight — правильный выбор. Для чисто Android-проекта Room проще и имеет больше интеграций (LiveData, Flow).

> [!question]- Почему WAL mode критичен для мобильных приложений?
> WAL (Write-Ahead Logging) mode позволяет параллельное чтение и запись в SQLite: readers не блокируют writers. Без WAL (journal mode) любая запись блокирует все чтения — UI зависает при фоновой синхронизации. Room включает WAL по умолчанию. Для мобильных приложений с async data loading WAL mode обязателен.

> [!question]- Как правильно реализовать offline-first подход с мобильной БД?
> Данные сначала сохраняются локально (Room/SQLite), затем синхронизируются с сервером. Конфликты разрешаются через: last-write-wins (простой), merge (сложный), CRDT (автоматический). UI всегда читает из локальной БД — мгновенный отклик. Sync-движок работает в фоне. Нужна очередь pending changes и стратегия retry. Библиотеки: PowerSync, Realm Sync, Firebase.

---

## Ключевые карточки

Что такое Room и зачем он нужен на Android?
?
Room — ORM-обёртка над SQLite от Google. Компилирует SQL-запросы на этапе сборки (compile-time safety), генерирует boilerplate, поддерживает Flow/LiveData для реактивного UI. Три компонента: Entity (таблица), DAO (запросы), Database (точка входа).

Чем SQLDelight отличается от Room?
?
SQLDelight: SQL-first — пишешь SQL в .sq файлах, получаешь Kotlin API. Мультиплатформенный (Android, iOS, Desktop, Web через KMP). Room: annotation-first — аннотации на Kotlin-классах. Только Android. SQLDelight даёт больше контроля над SQL.

Что такое Core Data в iOS?
?
Object Graph Manager от Apple. Не ORM — управляет графом объектов с lazy loading, faulting, undo/redo. NSManagedObject — базовый класс, NSFetchRequest — запросы. Может использовать SQLite, XML или binary как storage. SwiftData (iOS 17+) — современная замена.

Почему SQLite доминирует на мобильных платформах?
?
Serverless (нет отдельного процесса), zero-config, весь файл — одна БД, 600+ KB размер библиотеки, встроен в Android и iOS, ACID-совместимый, работает offline. Альтернативы (Realm, ObjectBox) предлагают нишевые преимущества, но SQLite — стандарт.

Что такое миграция схемы в мобильных БД?
?
Обновление структуры БД при новой версии приложения. Room: @Database(version = 2) + Migration(1, 2) с SQL ALTER TABLE. Деструктивная миграция (fallbackToDestructiveMigration) — удаляет все данные. Автомиграция (Room 2.4+) — для простых изменений.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[android-data-persistence]] | Room, DataStore, SharedPreferences на Android |
| Следующий шаг | [[ios-core-data]] | Core Data и SwiftData для iOS |
| Углубиться | [[kmp-sqldelight-database]] | SQLDelight для Kotlin Multiplatform |
| Смежная тема | [[android-architecture]] | Архитектура Android-приложения с data layer |
| Смежная тема | [[cross-data-persistence]] | Кросс-платформенные стратегии хранения данных |
| Обзор | [[databases-overview]] | Вернуться к карте раздела |

---

*Last updated: 2025-12-30*
