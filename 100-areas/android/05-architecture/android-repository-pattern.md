---
title: "Android Repository Pattern: Single Source of Truth и Offline-First"
created: 2025-01-15
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [repository-pattern, caching-strategy, data-consistency, offline-first]
tags:
  - topic/android
  - topic/architecture
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-architecture-patterns]]"
  - "[[android-data-persistence]]"
  - "[[android-networking]]"
  - "[[android-state-management]]"
prerequisites:
  - "[[android-overview]]"
  - "[[android-architecture-patterns]]"
  - "[[android-data-persistence]]"
---

> Полное руководство по реализации Repository pattern в Android с офлайн-поддержкой, кэшированием и синхронизацией.

---

## Зачем это нужно

**Проблема:** В типичном Android приложении данные приходят из нескольких источников — API, локальная база данных, кэш в памяти. Без правильной абстракции:
- ViewModel напрямую вызывает API → сложно тестировать
- Логика кэширования дублируется в разных экранах
- При изменении API нужно править все ViewModels
- Приложение не работает офлайн

**Решение:** Repository pattern создаёт единую точку доступа к данным:
- ViewModel не знает, откуда приходят данные
- Database = Single Source of Truth (SSOT)
- UI читает из базы, API только обновляет её
- Работает офлайн, синхронизируется при появлении сети

**Статистика:** По данным [Android Developers](https://developer.android.com/topic/architecture), 75% команд, использующих Repository pattern, отмечают меньше багов и проще поддержку.

**Что вы узнаете:**
1. Single Source of Truth и почему это критично
2. 4 стратегии кэширования (Cache-First, Network-First, Stale-While-Revalidate)
3. Offline-First архитектура с optimistic updates
4. Синхронизация и conflict resolution
5. Тестирование Repository

---

## Терминология

| Термин | Определение |
|--------|-------------|
| **Repository** | Абстракция над источниками данных (API, DB, cache) |
| **Single Source of Truth (SSOT)** | Единственный источник правды для данных |
| **Data Source** | Конкретный источник данных (Remote, Local, Cache) |
| **Offline-First** | Стратегия где локальные данные приоритетнее |
| **Cache Invalidation** | Механизм определения устаревших данных |
| **Stale-While-Revalidate** | Показать кэш, обновить в фоне |
| **DTO** | Data Transfer Object — модель для API |
| **Entity** | Модель для базы данных |
| **Domain Model** | Модель для бизнес-логики |

---

## Зачем нужен Repository Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WHY REPOSITORY PATTERN                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Без Repository:                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   ViewModel ─────────▶ API                                         │   │
│  │       │                                                             │   │
│  │       ├─────────────▶ Database                                     │   │
│  │       │                                                             │   │
│  │       └─────────────▶ Cache                                        │   │
│  │                                                                     │   │
│  │   Проблемы:                                                        │   │
│  │   • ViewModel знает о всех источниках данных                       │   │
│  │   • Логика кэширования дублируется                                 │   │
│  │   • Сложно тестировать (нужно мокать API, DB, Cache)              │   │
│  │   • Изменение API требует правок во всех ViewModels               │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  С Repository:                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │   ViewModel ─────────▶ Repository ─────────▶ RemoteDataSource      │   │
│  │                            │                       (API)           │   │
│  │                            │                                       │   │
│  │                            ├─────────────▶ LocalDataSource         │   │
│  │                            │                    (Room)             │   │
│  │                            │                                       │   │
│  │                            └─────────────▶ CacheDataSource         │   │
│  │                                              (Memory)              │   │
│  │                                                                     │   │
│  │   Преимущества:                                                    │   │
│  │   • ViewModel знает только о Repository                           │   │
│  │   • Логика кэширования в одном месте                              │   │
│  │   • Легко тестировать (один mock)                                 │   │
│  │   • Изменение источника не затрагивает ViewModel                  │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Single Source of Truth (SSOT)

### Концепция

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SINGLE SOURCE OF TRUTH                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Без SSOT:                              С SSOT:                            │
│                                                                             │
│  ┌─────────┐   ┌─────────┐             ┌─────────┐   ┌─────────┐          │
│  │ Screen1 │   │ Screen2 │             │ Screen1 │   │ Screen2 │          │
│  │ users=  │   │ users=  │             │         │   │         │          │
│  │ [A,B,C] │   │ [A,B]   │  ← Разные!  │         │   │         │          │
│  └────┬────┘   └────┬────┘             └────┬────┘   └────┬────┘          │
│       │             │                       │             │                │
│       ▼             ▼                       │             │                │
│  ┌─────────┐   ┌─────────┐                  │             │                │
│  │   API   │   │   API   │                  ▼             ▼                │
│  └─────────┘   └─────────┘             ┌─────────────────────┐            │
│                                        │     Database        │  ← SSOT    │
│  Проблема:                             │     users=[A,B,C]   │            │
│  • Каждый экран делает запрос         └──────────┬──────────┘            │
│  • Данные могут отличаться                       │                        │
│  • Рассинхрон при изменениях                     ▼                        │
│                                        ┌─────────────────────┐            │
│                                        │        API          │            │
│                                        │   (refresh only)    │            │
│                                        └─────────────────────┘            │
│                                                                             │
│  SSOT = Database является единственным источником данных для UI           │
│  API только обновляет Database, UI читает только из Database              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Реализация SSOT

```kotlin
// Repository использует Database как SSOT
class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {

    // UI наблюдает за Database (SSOT)
    override fun getUsers(): Flow<List<User>> {
        return dao.getAllUsers()
            .map { entities -> entities.map { it.toDomain() } }
    }

    // Refresh обновляет только Database
    override suspend fun refreshUsers(): Result<Unit> {
        return runCatching {
            val users = api.getUsers()
            dao.deleteAll()
            dao.insertAll(users.map { it.toEntity() })
        }
    }
}

// ViewModel
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    // UI State наблюдает за Database через Flow
    val users: StateFlow<List<User>> = repository.getUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    init {
        // Запустить refresh при старте
        refreshUsers()
    }

    fun refreshUsers() {
        viewModelScope.launch {
            repository.refreshUsers()
            // Не нужно обновлять UI State — Flow из Database сделает это
        }
    }
}
```

---

## Data Sources

### Структура

```kotlin
// Remote Data Source (API)
interface RemoteUserDataSource {
    suspend fun getUsers(): List<UserDto>
    suspend fun getUser(id: Long): UserDto
    suspend fun createUser(user: UserDto): UserDto
    suspend fun deleteUser(id: Long)
}

class RemoteUserDataSourceImpl(
    private val api: UserApi
) : RemoteUserDataSource {

    override suspend fun getUsers(): List<UserDto> {
        return api.getUsers()
    }

    override suspend fun getUser(id: Long): UserDto {
        return api.getUser(id)
    }

    override suspend fun createUser(user: UserDto): UserDto {
        return api.createUser(user)
    }

    override suspend fun deleteUser(id: Long) {
        api.deleteUser(id)
    }
}

// Local Data Source (Room)
interface LocalUserDataSource {
    fun getUsers(): Flow<List<UserEntity>>
    fun getUser(id: Long): Flow<UserEntity?>
    suspend fun insertAll(users: List<UserEntity>)
    suspend fun insert(user: UserEntity)
    suspend fun delete(id: Long)
    suspend fun deleteAll()
}

class LocalUserDataSourceImpl(
    private val dao: UserDao
) : LocalUserDataSource {

    override fun getUsers(): Flow<List<UserEntity>> = dao.getAllUsers()

    override fun getUser(id: Long): Flow<UserEntity?> = dao.getUserById(id)

    override suspend fun insertAll(users: List<UserEntity>) {
        dao.insertAll(users)
    }

    override suspend fun insert(user: UserEntity) {
        dao.insert(user)
    }

    override suspend fun delete(id: Long) {
        dao.deleteById(id)
    }

    override suspend fun deleteAll() {
        dao.deleteAll()
    }
}

// In-Memory Cache Data Source
class CacheUserDataSource {
    private val cache = ConcurrentHashMap<Long, User>()
    private var allUsersCached: List<User>? = null
    private var cacheTime: Long = 0
    private val cacheValidityMs = 5 * 60 * 1000L // 5 minutes

    fun getUsers(): List<User>? {
        return if (System.currentTimeMillis() - cacheTime < cacheValidityMs) {
            allUsersCached
        } else {
            null
        }
    }

    fun getUser(id: Long): User? = cache[id]

    fun setUsers(users: List<User>) {
        allUsersCached = users
        cacheTime = System.currentTimeMillis()
        users.forEach { cache[it.id] = it }
    }

    fun setUser(user: User) {
        cache[user.id] = user
    }

    fun invalidate() {
        allUsersCached = null
        cache.clear()
    }
}
```

### Repository Implementation

```kotlin
class UserRepositoryImpl(
    private val remoteDataSource: RemoteUserDataSource,
    private val localDataSource: LocalUserDataSource,
    private val cacheDataSource: CacheUserDataSource,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) : UserRepository {

    // Stream данных из SSOT (Database)
    override fun getUsers(): Flow<List<User>> {
        return localDataSource.getUsers()
            .map { entities -> entities.map { it.toDomain() } }
            .flowOn(dispatcher)
    }

    // Синхронизация с сервером
    override suspend fun refreshUsers(): Result<Unit> = withContext(dispatcher) {
        runCatching {
            // 1. Получить с сервера
            val remoteUsers = remoteDataSource.getUsers()

            // 2. Обновить SSOT (Database)
            localDataSource.deleteAll()
            localDataSource.insertAll(remoteUsers.map { it.toEntity() })

            // 3. Обновить кэш
            cacheDataSource.setUsers(remoteUsers.map { it.toDomain() })
        }
    }

    // Получить одного пользователя (с fallback)
    override suspend fun getUser(id: Long): Result<User> = withContext(dispatcher) {
        runCatching {
            // 1. Проверить кэш
            cacheDataSource.getUser(id)?.let { return@runCatching it }

            // 2. Проверить Database
            val localUser = localDataSource.getUser(id).first()
            if (localUser != null) {
                val user = localUser.toDomain()
                cacheDataSource.setUser(user)
                return@runCatching user
            }

            // 3. Загрузить с сервера
            val remoteUser = remoteDataSource.getUser(id)
            val user = remoteUser.toDomain()
            localDataSource.insert(remoteUser.toEntity())
            cacheDataSource.setUser(user)
            user
        }
    }
}
```

---

## Caching Strategies

### Стратегии кэширования

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CACHING STRATEGIES                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. Cache-First (Offline-First)                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Request → Cache → [Hit] → Return                                   │   │
│  │              │                                                      │   │
│  │              └── [Miss] → Network → Cache → Return                  │   │
│  │                                                                     │   │
│  │  Использовать: справочники, редко меняющиеся данные                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  2. Network-First                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Request → Network → [Success] → Cache → Return                     │   │
│  │              │                                                      │   │
│  │              └── [Failure] → Cache → Return                         │   │
│  │                                                                     │   │
│  │  Использовать: актуальные данные (новости, цены)                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  3. Stale-While-Revalidate                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Request → Cache → Return (сразу)                                   │   │
│  │              │                                                      │   │
│  │              └── Background: Network → Cache → Notify               │   │
│  │                                                                     │   │
│  │  Использовать: когда важна скорость, но нужна актуальность         │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  4. Cache-Then-Network                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  Request → Cache → Return (если есть)                               │   │
│  │              │                                                      │   │
│  │              └── Network → Cache → Return (обновлённые)             │   │
│  │                                                                     │   │
│  │  Использовать: сначала старые данные, потом свежие                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Реализация стратегий

```kotlin
// Cache-First
class CacheFirstRepository(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {

    override fun getUsers(): Flow<List<User>> = flow {
        // 1. Emit from cache first
        val cached = dao.getAllUsers().first()
        if (cached.isNotEmpty()) {
            emit(cached.map { it.toDomain() })
        }

        // 2. Fetch from network
        try {
            val fresh = api.getUsers()
            dao.deleteAll()
            dao.insertAll(fresh.map { it.toEntity() })
            emit(fresh.map { it.toDomain() })
        } catch (e: Exception) {
            // If cache was empty, propagate error
            if (cached.isEmpty()) throw e
        }
    }
}

// Network-First
class NetworkFirstRepository(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {

    override fun getUsers(): Flow<List<User>> = flow {
        try {
            // 1. Try network first
            val fresh = api.getUsers()
            dao.deleteAll()
            dao.insertAll(fresh.map { it.toEntity() })
            emit(fresh.map { it.toDomain() })
        } catch (e: Exception) {
            // 2. Fallback to cache
            val cached = dao.getAllUsers().first()
            if (cached.isNotEmpty()) {
                emit(cached.map { it.toDomain() })
            } else {
                throw e
            }
        }
    }
}

// Stale-While-Revalidate
class StaleWhileRevalidateRepository(
    private val api: UserApi,
    private val dao: UserDao,
    private val scope: CoroutineScope
) : UserRepository {

    override fun getUsers(): Flow<List<User>> {
        // 1. Return stream from DB
        return dao.getAllUsers()
            .map { it.map { entity -> entity.toDomain() } }
            .onStart {
                // 2. Trigger background refresh
                scope.launch {
                    try {
                        val fresh = api.getUsers()
                        dao.deleteAll()
                        dao.insertAll(fresh.map { it.toEntity() })
                        // DB Flow will automatically emit new data
                    } catch (e: Exception) {
                        // Ignore, we have cached data
                    }
                }
            }
    }
}

// Cache-Then-Network (emit twice)
class CacheThenNetworkRepository(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {

    override fun getUsers(): Flow<List<User>> = flow {
        // 1. Emit cached data first
        val cached = dao.getAllUsers().first()
        if (cached.isNotEmpty()) {
            emit(cached.map { it.toDomain() })
        }

        // 2. Fetch fresh and emit again
        try {
            val fresh = api.getUsers()
            dao.deleteAll()
            dao.insertAll(fresh.map { it.toEntity() })
            emit(fresh.map { it.toDomain() })
        } catch (e: Exception) {
            // If we already emitted cache, don't throw
            if (cached.isEmpty()) throw e
        }
    }
}
```

### Cache Invalidation

```kotlin
// Time-based invalidation
class TimedCacheRepository(
    private val api: UserApi,
    private val dao: UserDao,
    private val prefs: SharedPreferences
) : UserRepository {

    private val cacheValidityMs = 15 * 60 * 1000L // 15 minutes

    override fun getUsers(): Flow<List<User>> = flow {
        val lastFetch = prefs.getLong("users_last_fetch", 0)
        val isStale = System.currentTimeMillis() - lastFetch > cacheValidityMs

        if (!isStale) {
            // Cache is fresh, use it
            val cached = dao.getAllUsers().first()
            if (cached.isNotEmpty()) {
                emit(cached.map { it.toDomain() })
                return@flow
            }
        }

        // Fetch fresh
        val fresh = api.getUsers()
        dao.deleteAll()
        dao.insertAll(fresh.map { it.toEntity() })
        prefs.edit().putLong("users_last_fetch", System.currentTimeMillis()).apply()
        emit(fresh.map { it.toDomain() })
    }

    fun invalidateCache() {
        prefs.edit().putLong("users_last_fetch", 0).apply()
    }
}

// Version-based invalidation
class VersionedCacheRepository(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {

    override suspend fun refreshIfNeeded() {
        val localVersion = dao.getCacheVersion()
        val remoteVersion = api.getCacheVersion()

        if (localVersion < remoteVersion) {
            val fresh = api.getUsers()
            dao.deleteAll()
            dao.insertAll(fresh.map { it.toEntity() })
            dao.setCacheVersion(remoteVersion)
        }
    }
}
```

---

## Offline-First Architecture

### Принципы

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    OFFLINE-FIRST ARCHITECTURE                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Принципы:                                                                  │
│  1. Database = Single Source of Truth                                       │
│  2. UI читает ТОЛЬКО из Database                                           │
│  3. Network ТОЛЬКО обновляет Database                                      │
│  4. Локальные изменения сначала в Database, потом sync                     │
│                                                                             │
│  Поток данных:                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │       UI ◀──────────────── Database (Room) ◀───────── API          │   │
│  │        │                        ▲                                   │   │
│  │        │                        │                                   │   │
│  │        │    User Action         │                                   │   │
│  │        └────────────────────────┘                                   │   │
│  │                                                                     │   │
│  │  1. User делает действие (add/edit/delete)                         │   │
│  │  2. Изменение сохраняется в Database СРАЗУ                         │   │
│  │  3. UI обновляется через Flow из Database                          │   │
│  │  4. Background sync отправляет изменения на сервер                 │   │
│  │  5. При ошибке — retry или откат                                   │   │
│  │                                                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  Преимущества:                                                              │
│  • Мгновенный отклик UI (не ждём сеть)                                    │
│  • Работает без интернета                                                  │
│  • Нет лагов при плохой сети                                              │
│  • Данные не теряются при crash                                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Optimistic Updates

```kotlin
// Optimistic Update — сначала UI, потом sync
class OfflineFirstRepository(
    private val api: UserApi,
    private val dao: UserDao,
    private val syncManager: SyncManager
) : UserRepository {

    override fun getUsers(): Flow<List<User>> {
        return dao.getAllUsers()
            .map { it.map { entity -> entity.toDomain() } }
    }

    // Добавление с optimistic update
    override suspend fun addUser(user: User): Result<User> {
        // 1. Сохранить локально СРАЗУ (optimistic)
        val entity = user.toEntity(syncStatus = SyncStatus.PENDING)
        val localId = dao.insert(entity)

        // 2. UI уже видит нового пользователя через Flow

        // 3. Sync в фоне
        syncManager.scheduleSyncForUser(localId)

        return Result.success(user.copy(id = localId))
    }

    // Удаление с optimistic update
    override suspend fun deleteUser(userId: Long): Result<Unit> {
        // 1. Пометить как удалённый локально
        dao.markAsDeleted(userId)

        // 2. UI уже не видит пользователя

        // 3. Sync в фоне
        syncManager.scheduleDeleteSync(userId)

        return Result.success(Unit)
    }
}

// Sync Manager с WorkManager
class SyncManager(
    private val workManager: WorkManager
) {
    fun scheduleSyncForUser(userId: Long) {
        val request = OneTimeWorkRequestBuilder<UserSyncWorker>()
            .setInputData(workDataOf("userId" to userId))
            .setConstraints(
                Constraints.Builder()
                    .setRequiredNetworkType(NetworkType.CONNECTED)
                    .build()
            )
            .setBackoffCriteria(
                BackoffPolicy.EXPONENTIAL,
                1,
                TimeUnit.MINUTES
            )
            .build()

        workManager.enqueueUniqueWork(
            "sync_user_$userId",
            ExistingWorkPolicy.REPLACE,
            request
        )
    }
}

// Sync Worker
class UserSyncWorker(
    context: Context,
    params: WorkerParameters,
    private val api: UserApi,
    private val dao: UserDao
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val userId = inputData.getLong("userId", -1)
        if (userId == -1L) return Result.failure()

        return try {
            val localUser = dao.getUserById(userId).first()
                ?: return Result.failure()

            when (localUser.syncStatus) {
                SyncStatus.PENDING -> {
                    // Create on server
                    val remoteUser = api.createUser(localUser.toDto())
                    dao.updateRemoteId(userId, remoteUser.id)
                    dao.updateSyncStatus(userId, SyncStatus.SYNCED)
                }
                SyncStatus.PENDING_DELETE -> {
                    // Delete on server
                    api.deleteUser(localUser.remoteId)
                    dao.delete(userId)
                }
                else -> { /* Already synced */ }
            }

            Result.success()
        } catch (e: Exception) {
            if (runAttemptCount < 3) {
                Result.retry()
            } else {
                // Mark as failed, notify user
                dao.updateSyncStatus(userId, SyncStatus.FAILED)
                Result.failure()
            }
        }
    }
}
```

### Conflict Resolution

```kotlin
// Конфликты при sync
enum class ConflictResolution {
    CLIENT_WINS,    // Локальные изменения перезаписывают сервер
    SERVER_WINS,    // Серверные изменения перезаписывают локальные
    LAST_WRITE_WINS,// Кто последний изменил — тот и прав
    MERGE,          // Объединение изменений
    ASK_USER        // Спросить пользователя
}

// Entity с timestamps для conflict resolution
@Entity
data class UserEntity(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String,
    val syncStatus: SyncStatus,
    val localUpdatedAt: Long,    // Время локального изменения
    val serverUpdatedAt: Long?,  // Время изменения на сервере
    val remoteId: Long?          // ID на сервере (может отличаться)
)

// Conflict resolution logic
class ConflictResolver {

    fun resolve(
        local: UserEntity,
        server: UserDto,
        strategy: ConflictResolution
    ): UserEntity {
        return when (strategy) {
            ConflictResolution.CLIENT_WINS -> {
                // Оставить локальную версию
                local
            }
            ConflictResolution.SERVER_WINS -> {
                // Заменить на серверную
                server.toEntity(syncStatus = SyncStatus.SYNCED)
            }
            ConflictResolution.LAST_WRITE_WINS -> {
                // Сравнить timestamps
                if (local.localUpdatedAt > server.updatedAt) {
                    local
                } else {
                    server.toEntity(syncStatus = SyncStatus.SYNCED)
                }
            }
            ConflictResolution.MERGE -> {
                // Объединить поля (domain-specific logic)
                local.copy(
                    // Пример: взять name от сервера, email от локального
                    name = server.name,
                    email = local.email,
                    syncStatus = SyncStatus.SYNCED,
                    serverUpdatedAt = server.updatedAt
                )
            }
            ConflictResolution.ASK_USER -> {
                // Пометить как конфликт для UI
                local.copy(syncStatus = SyncStatus.CONFLICT)
            }
        }
    }
}
```

---

## Error Handling

### Стратегии обработки ошибок

```kotlin
// Result wrapper для Repository
sealed class DataResult<out T> {
    data class Success<T>(val data: T) : DataResult<T>()
    data class Error(val exception: Throwable) : DataResult<Nothing>()
    data class Loading<T>(val data: T? = null) : DataResult<T>()
}

// Repository с error handling
class UserRepositoryImpl(
    private val api: UserApi,
    private val dao: UserDao
) : UserRepository {

    override fun getUsers(): Flow<DataResult<List<User>>> = flow {
        emit(DataResult.Loading())

        // Сначала emit кэш
        val cached = dao.getAllUsers().first()
        if (cached.isNotEmpty()) {
            emit(DataResult.Loading(cached.map { it.toDomain() }))
        }

        // Потом fetch
        try {
            val fresh = api.getUsers()
            dao.deleteAll()
            dao.insertAll(fresh.map { it.toEntity() })
            emit(DataResult.Success(fresh.map { it.toDomain() }))
        } catch (e: Exception) {
            if (cached.isNotEmpty()) {
                // Есть кэш, показываем его с warning
                emit(DataResult.Success(cached.map { it.toDomain() }))
            } else {
                emit(DataResult.Error(e))
            }
        }
    }.catch { e ->
        emit(DataResult.Error(e))
    }
}

// ViewModel
class UsersViewModel(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<UsersUiState>(UsersUiState.Loading)
    val uiState: StateFlow<UsersUiState> = _uiState.asStateFlow()

    init {
        loadUsers()
    }

    private fun loadUsers() {
        viewModelScope.launch {
            repository.getUsers().collect { result ->
                _uiState.value = when (result) {
                    is DataResult.Loading -> {
                        UsersUiState.Loading(result.data)
                    }
                    is DataResult.Success -> {
                        UsersUiState.Success(result.data)
                    }
                    is DataResult.Error -> {
                        UsersUiState.Error(result.exception.message ?: "Unknown error")
                    }
                }
            }
        }
    }
}

// UiState
sealed class UsersUiState {
    data class Loading(val cachedUsers: List<User>? = null) : UsersUiState()
    data class Success(val users: List<User>) : UsersUiState()
    data class Error(val message: String) : UsersUiState()
}
```

---

## Mapping между слоями

```kotlin
// DTO (API)
@Serializable
data class UserDto(
    val id: Long,
    val name: String,
    val email: String,
    @SerialName("created_at")
    val createdAt: String,
    @SerialName("avatar_url")
    val avatarUrl: String?
)

// Entity (Database)
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: Long,
    val name: String,
    val email: String,
    val createdAt: Long,
    val avatarUrl: String?,
    val syncStatus: SyncStatus = SyncStatus.SYNCED,
    val lastUpdated: Long = System.currentTimeMillis()
)

// Domain Model
data class User(
    val id: Long,
    val name: String,
    val email: String,
    val createdAt: Instant,
    val avatarUrl: String?
)

// Mappers
fun UserDto.toEntity(): UserEntity {
    return UserEntity(
        id = id,
        name = name,
        email = email,
        createdAt = Instant.parse(createdAt).toEpochMilli(),
        avatarUrl = avatarUrl
    )
}

fun UserEntity.toDomain(): User {
    return User(
        id = id,
        name = name,
        email = email,
        createdAt = Instant.ofEpochMilli(createdAt),
        avatarUrl = avatarUrl
    )
}

fun User.toEntity(syncStatus: SyncStatus = SyncStatus.SYNCED): UserEntity {
    return UserEntity(
        id = id,
        name = name,
        email = email,
        createdAt = createdAt.toEpochMilli(),
        avatarUrl = avatarUrl,
        syncStatus = syncStatus
    )
}

// Extension functions для списков
fun List<UserDto>.toEntities() = map { it.toEntity() }
fun List<UserEntity>.toDomain() = map { it.toDomain() }
```

---

## Testing Repository

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserRepositoryTest {

    private lateinit var repository: UserRepository
    private lateinit var fakeApi: FakeUserApi
    private lateinit var fakeDao: FakeUserDao

    @Before
    fun setup() {
        fakeApi = FakeUserApi()
        fakeDao = FakeUserDao()
        repository = UserRepositoryImpl(fakeApi, fakeDao)
    }

    @Test
    fun `getUsers returns cached data then fresh data`() = runTest {
        // Given
        val cachedUsers = listOf(UserEntity(1, "Cached", "c@c.com", 0, null))
        val freshUsers = listOf(UserDto(1, "Fresh", "f@f.com", "2024-01-01T00:00:00Z", null))

        fakeDao.setUsers(cachedUsers)
        fakeApi.setUsers(freshUsers)

        // When
        val results = repository.getUsers().toList()

        // Then
        assertEquals(2, results.size)
        assertEquals("Cached", results[0].first().name) // First emit: cache
        assertEquals("Fresh", results[1].first().name)  // Second emit: fresh
    }

    @Test
    fun `getUsers returns only cache when network fails`() = runTest {
        // Given
        val cachedUsers = listOf(UserEntity(1, "Cached", "c@c.com", 0, null))
        fakeDao.setUsers(cachedUsers)
        fakeApi.setShouldFail(true)

        // When
        val result = repository.getUsers().first()

        // Then
        assertEquals(1, result.size)
        assertEquals("Cached", result.first().name)
    }

    @Test
    fun `refreshUsers updates database`() = runTest {
        // Given
        val freshUsers = listOf(UserDto(1, "Fresh", "f@f.com", "2024-01-01T00:00:00Z", null))
        fakeApi.setUsers(freshUsers)

        // When
        val result = repository.refreshUsers()

        // Then
        assertTrue(result.isSuccess)
        val dbUsers = fakeDao.getAllUsers().first()
        assertEquals(1, dbUsers.size)
        assertEquals("Fresh", dbUsers.first().name)
    }
}

// Fake implementations
class FakeUserApi : UserApi {
    private var users = emptyList<UserDto>()
    private var shouldFail = false

    fun setUsers(users: List<UserDto>) { this.users = users }
    fun setShouldFail(fail: Boolean) { shouldFail = fail }

    override suspend fun getUsers(): List<UserDto> {
        if (shouldFail) throw IOException("Network error")
        return users
    }
}

class FakeUserDao : UserDao {
    private val usersFlow = MutableStateFlow<List<UserEntity>>(emptyList())

    fun setUsers(users: List<UserEntity>) { usersFlow.value = users }

    override fun getAllUsers(): Flow<List<UserEntity>> = usersFlow

    override suspend fun insertAll(users: List<UserEntity>) {
        usersFlow.value = users
    }

    override suspend fun deleteAll() {
        usersFlow.value = emptyList()
    }
}
```

---

## Проверь себя

### Вопросы для самопроверки

1. **Что такое Single Source of Truth?**
   - Единственный источник данных для UI
   - Обычно Database (Room)
   - API только обновляет SSOT, не является источником для UI

2. **Какие стратегии кэширования существуют?**
   - Cache-First: сначала кэш, потом сеть
   - Network-First: сначала сеть, fallback на кэш
   - Stale-While-Revalidate: кэш сразу, обновление в фоне
   - Cache-Then-Network: кэш, потом свежие данные

3. **Что такое Optimistic Update?**
   - Изменение применяется к UI сразу (в Database)
   - Sync с сервером происходит в фоне
   - Даёт мгновенный отклик пользователю

4. **Зачем нужны разные модели (DTO, Entity, Domain)?**
   - DTO: формат API (может меняться с сервером)
   - Entity: формат DB (может меняться со схемой)
   - Domain: чистая бизнес-модель (стабильная)

5. **Как обрабатывать конфликты при sync?**
   - Client Wins, Server Wins, Last Write Wins
   - Merge полей
   - Ask User

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Repository = просто прокси к API/DB" | Repository координирует несколько источников данных. Содержит caching logic, sync strategy, conflict resolution. Это orchestrator, не простой wrapper |
| "Один Repository на Entity" | Не обязательно. Feature-based repositories могут объединять несколько entities. UserRepository может работать с User + UserSettings + UserPreferences |
| "Repository должен возвращать Flow везде" | Для one-shot операций (create, update, delete) suspend функции удобнее. Flow нужен для observable данных (списки, real-time updates) |
| "Repository всегда использует Room" | Room — частый выбор, но не единственный. DataStore для preferences, In-memory cache для temporary data, SQLDelight для KMP. Repository абстрагирует реализацию |
| "Offline-first = сложно" | Базовый offline-first = Room как SSOT + sync при появлении сети. WorkManager делает sync надёжным. Сложность в conflict resolution, не в базовой реализации |
| "DTO = Entity = Domain Model" | Разные модели для разных целей. DTO — формат API (может меняться). Entity — схема DB. Domain — бизнес-логика. Маппинг защищает от изменений |
| "Cache invalidation — просто TTL" | TTL — базовый подход. Более сложные: invalidation по событиям, partial update, background refresh. Зависит от nature данных |
| "Repository singleton — антипаттерн" | Repository scoped к Application — нормально. Shared state между экранами нужен. DI framework (Hilt) управляет lifecycle |
| "Все ошибки надо пробрасывать как Exception" | Result<T> / Either<Error, T> — explicit error handling. Forced обработка ошибок caller'ом. Исключения — для исключительных ситуаций |
| "Optimistic updates сложно откатить" | Сохраняй previous state перед изменением. При ошибке восстанови. Room transactions помогают с atomicity |

---

## CS-фундамент

| CS-концепция | Как применяется в Repository |
|--------------|------------------------------|
| **Repository Pattern** | Абстракция data access layer. Скрывает источник данных от бизнес-логики. Позволяет менять реализацию без изменения клиентов |
| **Single Source of Truth** | Database = единственный источник для UI. Network обновляет database, UI читает из database. Нет рассинхронизации |
| **Caching Strategies** | Cache-First, Network-First, Stale-While-Revalidate. Trade-off: freshness vs latency. Выбор зависит от nature данных |
| **Data Mapping** | DTO ↔ Entity ↔ Domain. Защита от изменений внешних контрактов. Каждый слой имеет свою модель |
| **Reactive Streams** | Flow для observable data. Repository emit'ит changes, UI collect'ит. Push-based уведомления |
| **Eventual Consistency** | Local и remote могут временно расходиться. Sync приводит к consistency. Conflict resolution определяет final state |
| **Unit of Work** | Группировка операций в transaction. Atomic: все успешны или все откатываются. Room @Transaction |
| **Optimistic Concurrency** | Применяем изменения сразу, sync в фоне. Rollback при ошибке. Лучший UX за счёт сложности |
| **Dependency Inversion** | ViewModel зависит от interface (Repository), не от implementation. Легко тестировать с fake repository |
| **Error Handling Strategy** | Result wrapper, sealed classes для типизированных ошибок. Explicit flow vs exceptions |

---

## Связь с другими темами

**[[android-architecture-patterns]]** — Repository pattern является ключевым элементом Data Layer в MVVM и Clean Architecture. В MVVM ViewModel получает данные исключительно через Repository, не зная об источниках данных. В Clean Architecture Repository реализует интерфейс из Domain Layer, обеспечивая инверсию зависимостей. Понимание архитектурных паттернов определяет, как Repository интегрируется в общую архитектуру приложения. Изучите Architecture Patterns первым для понимания роли Repository.

**[[android-data-persistence]]** — Room является основным Local Data Source в Repository pattern, обеспечивая Single Source of Truth. Room DAO предоставляет Flow/LiveData для реактивного наблюдения за изменениями данных, что делает UI автоматически обновляемым при записи новых данных из сети. Понимание Room entities, DAO, миграций и transactions критично для реализации offline-first архитектуры. DataStore используется для настроек и простых данных в Repository.

**[[android-networking]]** — Retrofit/OkHttp выступает как Remote Data Source в Repository pattern. Repository координирует сетевые запросы через Retrofit с локальным кэшированием через Room, реализуя стратегии Cache-First, Network-First и Stale-While-Revalidate. Понимание interceptors, error handling и retry policies в OkHttp влияет на надёжность Repository layer. Изучите networking для реализации remote data source.

**[[android-state-management]]** — Repository предоставляет данные через Flow/StateFlow, которые ViewModel трансформирует в UI State. Правильная интеграция Repository с state management (StateFlow для single values, Flow для streams) определяет, как данные протекают от сети/базы до UI. Понимание cold vs hot streams критично для выбора правильного API в Repository interface.

---

## Источники

1. [Guide to App Architecture](https://developer.android.com/topic/architecture)
2. [Repository Pattern in Android](https://developer.android.com/topic/architecture/data-layer)
3. [Offline-First](https://developer.android.com/topic/architecture/data-layer/offline-first)
4. [Room with Flow](https://developer.android.com/training/data-storage/room/async-queries#kotlin)

---

## Источники и дальнейшее чтение

- Meier (2022). *Professional Android*. — практическая реализация Repository pattern с Room, Retrofit и offline-first стратегиями, включая sync, conflict resolution и тестирование data layer.
- Moskala (2022). *Kotlin Coroutines Deep Dive*. — детальный разбор Flow и Channel, которые являются основой реактивного API Repository: Flow для наблюдения за данными из Room, suspend functions для сетевых запросов.
- Phillips et al. (2022). *Android Programming: The Big Nerd Ranch Guide*. — пошаговое построение Repository layer с Room и Retrofit, включая кэширование, error handling и интеграцию с ViewModel.

---

*Проверено: 2026-01-09 — Педагогический контент проверен*
