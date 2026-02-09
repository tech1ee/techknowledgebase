---
title: "Хранение данных: Room, DataStore, Files"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [database-design, acid-properties, serialization, file-systems]
tags:
  - topic/android
  - topic/data
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-threading]]"
  - "[[android-architecture-patterns]]"
  - "[[kotlin-coroutines]]"
  - "[[kotlin-flow]]"
  - "[[database-design-optimization]]"
---

# Хранение данных: Room, DataStore, Files

Android предлагает несколько способов хранения данных: **Room** для структурированных данных (SQLite с compile-time проверками), **DataStore** для key-value настроек (замена SharedPreferences), и файловое хранилище для бинарных данных.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android
> - [[android-activity-lifecycle]] — почему данные нужно сохранять между пересозданиями Activity
> - Базовое понимание SQL (для Room) — SELECT, INSERT, UPDATE, DELETE

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Room** | ORM-библиотека над SQLite с compile-time проверками |
| **Entity** | Таблица в базе данных (data class) |
| **DAO** | Data Access Object — интерфейс для запросов |
| **DataStore** | Асинхронное key-value хранилище |
| **Proto DataStore** | DataStore с типизацией через Protocol Buffers |
| **Migration** | Обновление схемы БД между версиями |

---

## Когда какой способ хранения

| Способ | Когда использовать | Примеры | Почему именно это решение |
|--------|-------------------|---------|---------------------------|
| **SharedPreferences** (устарело) | Не использовать | - | Заменено на DataStore |
| **DataStore** | Простые настройки (key-value), небольшой объём | Темная тема, язык, флаги feature toggles | Асинхронность, типобезопасность, нет race conditions |
| **Room** | Структурированные данные, связи, запросы | Пользователи, заказы, чаты, избранное | SQL для сложных запросов, compile-time проверки, relations |
| **Files** (Internal) | Бинарные данные, большие файлы, нестандартные форматы | JSON кэш, загруженные PDF, временные файлы | Простота, не нужна структура БД |
| **Files** (External/MediaStore) | Медиа-файлы доступные другим приложениям | Фото, видео, музыка | Системная галерея, доступ из других приложений |
| **Network Cache** (OkHttp/Retrofit) | HTTP ответы для offline режима | API responses | Автоматическое управление, HTTP headers (Cache-Control) |

### Правило выбора

```
Нужно сохранить настройку (boolean/string/int)?
  └─> DataStore

Нужны SQL-запросы или связи между объектами?
  └─> Room

Файл больше 1MB или бинарный?
  └─> File Storage

HTTP-запрос нужно кэшировать?
  └─> OkHttp Cache (автоматически через Retrofit)
```

---

## Почему Room, а не SQLite напрямую?

### Проблема: работа с SQLite вручную

```kotlin
// ❌ Работа с SQLite без ORM — типичный код
class UserDbHelper(context: Context) : SQLiteOpenHelper(context, "users.db", null, 1) {

    override fun onCreate(db: SQLiteDatabase) {
        // Строковый SQL — опечатка = runtime crash
        db.execSQL("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                email TEXT,
                created_at INTEGER
            )
        """)
    }

    override fun onUpgrade(db: SQLiteDatabase, oldVersion: Int, newVersion: Int) {
        // Нужно писать миграции вручную для КАЖДОЙ версии
        if (oldVersion < 2) {
            db.execSQL("ALTER TABLE users ADD COLUMN avatar_url TEXT")
        }
    }

    fun insertUser(name: String, email: String): Long {
        val db = writableDatabase
        val values = ContentValues().apply {
            put("full_name", name)  // Строка "full_name" — легко опечататься
            put("email", email)
        }
        return db.insert("users", null, values)
    }

    fun getUsers(): List<User> {
        val db = readableDatabase
        // Строковый SQL — нет проверки на этапе компиляции
        val cursor = db.rawQuery("SELECT * FROM usres", null)  // ОПЕЧАТКА!
        // Этот код скомпилируется, но упадёт в runtime

        val users = mutableListOf<User>()
        cursor.use {
            while (it.moveToNext()) {
                users.add(User(
                    id = it.getLong(it.getColumnIndexOrThrow("id")),
                    fullName = it.getString(it.getColumnIndexOrThrow("full_name")),
                    email = it.getString(it.getColumnIndexOrThrow("email"))
                ))
            }
        }
        return users
    }

    fun searchUsers(query: String): List<User> {
        val db = readableDatabase
        // SQL injection уязвимость!
        val cursor = db.rawQuery(
            "SELECT * FROM users WHERE full_name LIKE '%$query%'",
            null
        )
        // Если query = "'; DROP TABLE users; --"
        // Все данные удалены
    }
}
```

### Типичные проблемы SQLite вручную

| Проблема | Последствие | В Room |
|----------|-------------|--------|
| Опечатка в названии таблицы/колонки | Runtime crash | Compile-time error |
| Неправильный SQL синтаксис | Runtime crash | Compile-time error |
| SQL injection | Уязвимость безопасности | Автоматический escaping |
| Несоответствие типов (String в INTEGER) | Data corruption или crash | Compile-time error |
| Забытый cursor.close() | Memory leak | Автоматическое управление |
| Миграции вручную | Ошибки, потеря данных | AutoMigration + проверки |
| Запрос на Main Thread | ANR | Принудительный async |

### Как Room решает эти проблемы

```kotlin
// ✅ Room — compile-time проверки

// Entity — таблица
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,

    @ColumnInfo(name = "full_name")
    val fullName: String,

    val email: String
)

// DAO — запросы
@Dao
interface UserDao {

    // Compile-time проверка SQL синтаксиса!
    @Query("SELECT * FROM usres")  // ❌ ОШИБКА КОМПИЛЯЦИИ: no such table: usres
    suspend fun getAll(): List<User>

    @Query("SELECT * FROM users")  // ✅ Правильно
    suspend fun getAllUsers(): List<User>

    // Compile-time проверка возвращаемого типа!
    @Query("SELECT full_name FROM users")
    suspend fun getAllNames(): List<String>  // ✅ Соответствует

    @Query("SELECT full_name FROM users")
    suspend fun getAllUsers2(): List<User>   // ❌ ОШИБКА: не все поля User

    // Безопасная параметризация — SQL injection невозможен
    @Query("SELECT * FROM users WHERE full_name LIKE '%' || :query || '%'")
    suspend fun search(query: String): List<User>
    // Room автоматически эскейпит параметры

    // Автоматический маппинг ContentValues → Entity
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User): Long

    // Принудительный suspend — нельзя вызвать на Main Thread
    // (без suspend функции Room не скомпилируется для не-allowMainThreadQueries)
}
```

### Визуальное сравнение

```
┌─────────────────────────────────────────────────────────────────┐
│                     SQLite напрямую                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Компиляция          Runtime                                    │
│  ┌─────────┐        ┌─────────────────────────────────────┐    │
│  │  Java   │───────▶│ SQL парсится                         │    │
│  │  Code   │ всё ок │ Ошибка = SQLiteException             │    │
│  │         │        │ Приложение крашится                   │    │
│  └─────────┘        └─────────────────────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          Room                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Компиляция                           Runtime                   │
│  ┌──────────────────────────────┐    ┌────────────────────┐    │
│  │ KSP/KAPT анализирует:        │    │ Гарантированно     │    │
│  │ - SQL синтаксис              │    │ корректный SQL     │    │
│  │ - Названия таблиц/колонок    │────│                    │    │
│  │ - Типы данных                │    │ Crash невозможен   │    │
│  │ - Соответствие Entity        │    │ (если скомпилилось)│    │
│  │                              │    │                    │    │
│  │ Ошибка = Build failed        │    │                    │    │
│  └──────────────────────────────┘    └────────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Почему не другие ORM (Realm, ObjectBox)?

| Критерий | Room | Realm | ObjectBox |
|----------|------|-------|-----------|
| **Поддержка Google** | Официальная | Сторонняя | Сторонняя |
| **Интеграция с Jetpack** | Нативная (LiveData, Flow, Paging) | Через адаптеры | Через адаптеры |
| **База данных** | SQLite (стандарт Android) | Собственная | Собственная |
| **Миграции** | AutoMigration + ручные | Автоматические | Автоматические |
| **Compile-time проверки SQL** | Да | Нет SQL | Нет SQL |
| **Размер библиотеки** | ~100KB | ~4MB | ~1MB |
| **Просмотр данных** | Любой SQLite viewer | Только Realm Studio | ObjectBox Browser |
| **Multiplatform** | Нет | Да (KMM) | Да |

**Когда выбрать Realm/ObjectBox:**
- Нужен KMM (Kotlin Multiplatform)
- Синхронизация с облаком (Realm Sync, ObjectBox Sync)
- Предпочитаете объектный подход вместо реляционного

**Когда выбрать Room:**
- Стандартный Android проект
- Важна интеграция с Jetpack
- Нужен контроль над SQL запросами
- Важен маленький размер библиотеки
- Привычный SQLite (легко инспектировать данные)

### Недостатки Room

1. **Boilerplate код:**
   - Entity + DAO + Database для каждой таблицы
   - Много аннотаций

2. **Только Android (пока):**
   - Нет поддержки KMM (но планируется)
   - Для multiplatform — SQLDelight или Realm

3. **Compile time:**
   - KSP/KAPT добавляет время компиляции
   - На больших проектах может быть заметно

4. **Сложные запросы:**
   - Для очень сложного SQL иногда проще rawQuery
   - Но теряется compile-time проверка

---

## Room: база данных

### Настройка

```kotlin
// build.gradle.kts
dependencies {
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")  // Coroutines support
    ksp("androidx.room:room-compiler:2.6.1")  // KSP вместо kapt
}
```

### Entity: таблица

```kotlin
@Entity(tableName = "users")
data class User(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,

    @ColumnInfo(name = "full_name")
    val fullName: String,

    val email: String,

    @ColumnInfo(defaultValue = "CURRENT_TIMESTAMP")
    val createdAt: Long = System.currentTimeMillis()
)

// Связь один-ко-многим
@Entity(
    tableName = "posts",
    foreignKeys = [
        ForeignKey(
            entity = User::class,
            parentColumns = ["id"],
            childColumns = ["user_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("user_id")]
)
data class Post(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,

    @ColumnInfo(name = "user_id")
    val userId: Long,

    val title: String,
    val content: String
)
```

### DAO: запросы

```kotlin
@Dao
interface UserDao {

    // Insert
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: User): Long

    @Insert
    suspend fun insertAll(users: List<User>)

    // Update
    @Update
    suspend fun update(user: User)

    // Delete
    @Delete
    suspend fun delete(user: User)

    @Query("DELETE FROM users WHERE id = :userId")
    suspend fun deleteById(userId: Long)

    // Query - возвращает один раз
    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getById(id: Long): User?

    @Query("SELECT * FROM users ORDER BY full_name")
    suspend fun getAll(): List<User>

    // Query - возвращает Flow (реактивно)
    @Query("SELECT * FROM users ORDER BY full_name")
    fun observeAll(): Flow<List<User>>

    @Query("SELECT * FROM users WHERE email LIKE '%' || :query || '%'")
    fun search(query: String): Flow<List<User>>

    // Сложные запросы
    @Query("""
        SELECT u.*, COUNT(p.id) as post_count
        FROM users u
        LEFT JOIN posts p ON u.id = p.user_id
        GROUP BY u.id
    """)
    fun getUsersWithPostCount(): Flow<List<UserWithPostCount>>
}

data class UserWithPostCount(
    @Embedded val user: User,
    @ColumnInfo(name = "post_count") val postCount: Int
)
```

### Database

```kotlin
@Database(
    entities = [User::class, Post::class],
    version = 2,
    exportSchema = true  // Для миграций
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {

    abstract fun userDao(): UserDao
    abstract fun postDao(): PostDao

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
                    .addMigrations(MIGRATION_1_2)
                    .build()
                    .also { INSTANCE = it }
            }
        }
    }
}

// Type Converters для сложных типов
class Converters {
    @TypeConverter
    fun fromTimestamp(value: Long?): Date? = value?.let { Date(it) }

    @TypeConverter
    fun dateToTimestamp(date: Date?): Long? = date?.time
}
```

### Миграции

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(database: SupportSQLiteDatabase) {
        database.execSQL(
            "ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT NULL"
        )
    }
}

// Автоматическая миграция (Room 2.4+)
@Database(
    version = 3,
    autoMigrations = [
        AutoMigration(from = 2, to = 3)
    ]
)
```

### Использование с ViewModel

```kotlin
class UserRepository(private val userDao: UserDao) {

    val allUsers: Flow<List<User>> = userDao.observeAll()

    suspend fun addUser(user: User) = userDao.insert(user)

    suspend fun deleteUser(user: User) = userDao.delete(user)
}

class UserViewModel(private val repository: UserRepository) : ViewModel() {

    val users: StateFlow<List<User>> = repository.allUsers
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun addUser(name: String, email: String) {
        viewModelScope.launch {
            repository.addUser(User(fullName = name, email = email))
        }
    }
}
```

---

## DataStore: key-value хранилище

### Preferences DataStore

```kotlin
// Определение ключей
object PreferencesKeys {
    val DARK_THEME = booleanPreferencesKey("dark_theme")
    val LANGUAGE = stringPreferencesKey("language")
    val NOTIFICATION_ENABLED = booleanPreferencesKey("notifications")
}

// Repository
class SettingsRepository(private val context: Context) {

    private val dataStore = context.dataStore

    // Чтение
    val darkTheme: Flow<Boolean> = dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.DARK_THEME] ?: false
        }

    val settings: Flow<Settings> = dataStore.data
        .map { preferences ->
            Settings(
                darkTheme = preferences[PreferencesKeys.DARK_THEME] ?: false,
                language = preferences[PreferencesKeys.LANGUAGE] ?: "en",
                notificationsEnabled = preferences[PreferencesKeys.NOTIFICATION_ENABLED] ?: true
            )
        }

    // Запись
    suspend fun setDarkTheme(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.DARK_THEME] = enabled
        }
    }

    suspend fun updateSettings(settings: Settings) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.DARK_THEME] = settings.darkTheme
            preferences[PreferencesKeys.LANGUAGE] = settings.language
            preferences[PreferencesKeys.NOTIFICATION_ENABLED] = settings.notificationsEnabled
        }
    }
}

// Extension для создания DataStore
val Context.dataStore by preferencesDataStore(name = "settings")

data class Settings(
    val darkTheme: Boolean,
    val language: String,
    val notificationsEnabled: Boolean
)
```

### Почему не SharedPreferences

| Критерий | SharedPreferences | DataStore |
|----------|-------------------|-----------|
| Потокобезопасность | Нет (apply async, но не safe) | Да (полностью async) |
| Обработка ошибок | Нет | Да (через Flow) |
| Блокировка UI | Возможна (getString на main) | Невозможна |
| Типизация | Нет | Есть (Proto DataStore) |

---

## Файловое хранилище

### Internal Storage

```kotlin
// Приватные файлы приложения
// /data/data/<package>/files/

// Запись
context.openFileOutput("data.txt", Context.MODE_PRIVATE).use { output ->
    output.write("Hello World".toByteArray())
}

// Чтение
context.openFileInput("data.txt").bufferedReader().use { reader ->
    val text = reader.readText()
}

// Файлы в filesDir
val file = File(context.filesDir, "data.json")
file.writeText(json)

// Кэш (может быть очищен системой)
val cacheFile = File(context.cacheDir, "temp.txt")
```

### External Storage (Scoped Storage)

С Android 10+ доступ к внешнему хранилищу ограничен:

```kotlin
// Свои файлы в external (не требуют разрешений)
val externalFile = File(context.getExternalFilesDir(null), "data.txt")

// Медиа файлы через MediaStore
val contentValues = ContentValues().apply {
    put(MediaStore.Images.Media.DISPLAY_NAME, "photo.jpg")
    put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
    put(MediaStore.Images.Media.RELATIVE_PATH, Environment.DIRECTORY_PICTURES)
}

val uri = contentResolver.insert(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    contentValues
)

uri?.let {
    contentResolver.openOutputStream(it)?.use { output ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, output)
    }
}
```

---

## Распространённые ошибки

### Room: запрос на Main Thread

```kotlin
// ПЛОХО: crash или StrictMode warning
val user = userDao.getById(1)  // Синхронный вызов

// ХОРОШО
suspend fun getUser(id: Long): User? = userDao.getById(id)

// Или с Flow
userDao.observeById(id).collect { user -> }
```

### DataStore: не обрабатывать IOException

```kotlin
// ПЛОХО
val settings = dataStore.data.first()

// ХОРОШО
val settings = dataStore.data
    .catch { exception ->
        if (exception is IOException) {
            emit(emptyPreferences())
        } else {
            throw exception
        }
    }
    .first()
```

---

## Чеклист

```
□ Room: все операции через suspend или Flow
□ Room: используем индексы для часто запрашиваемых полей
□ Room: миграции для изменения схемы
□ DataStore: обрабатываем IOException в catch
□ DataStore: не блокируем main thread (collect в coroutine)
□ Files: используем context.filesDir, не hardcode пути
□ External: используем Scoped Storage API
□ Credentials: EncryptedSharedPreferences
```

---

## Проверь себя

### 1. Чем DataStore лучше SharedPreferences?

<details>
<summary>Показать ответ</summary>

**DataStore решает критические проблемы SharedPreferences:**

1. **Потокобезопасность:**
   - SharedPreferences: `apply()` асинхронный, но операции чтения синхронные → race conditions
   - DataStore: полностью асинхронный через Flow → гарантированная консистентность

2. **Блокировка UI:**
   - SharedPreferences: `getString()` на main thread блокирует → ANR
   - DataStore: нет синхронных операций → невозможно заблокировать UI

3. **Обработка ошибок:**
   - SharedPreferences: нет механизма обработки (диск заполнен = silent fail)
   - DataStore: все ошибки через Flow.catch { }

4. **Типизация:**
   - SharedPreferences: только примитивы + String
   - DataStore Proto: строго типизированные объекты через Protobuf

**Когда SharedPreferences всё ещё ОК:**
- Legacy код, который уже работает и не требует изменений
- Быстрый прототип без production требований

</details>

### 2. Зачем Room если есть SQLite напрямую?

<details>
<summary>Показать ответ</summary>

**Room = SQLite + compile-time безопасность:**

1. **Опечатки становятся compile errors:**
   ```kotlin
   @Query("SELECT * FROM usres")  // ❌ Build fails: no such table
   ```
   Без Room → crash в production

2. **SQL injection невозможен:**
   Room автоматически экранирует параметры в `@Query`

3. **Проверка типов:**
   ```kotlin
   @Query("SELECT full_name FROM users")
   suspend fun getUsers(): List<User>  // ❌ Build fails: нет полей id, email
   ```

4. **Принудительный async:**
   `suspend` функции нельзя вызвать на main thread → нет ANR

5. **Миграции:**
   AutoMigration проверяет схему и генерирует код автоматически

**Недостаток:** больше boilerplate (Entity + DAO + Database классы)

</details>

### 3. Когда использовать File storage вместо Room?

<details>
<summary>Показать ответ</summary>

**Выбирай Files когда:**

1. **Данные НЕ структурированные:**
   - PDF документы
   - Изображения
   - Аудио/видео файлы
   - Произвольные бинарные данные

2. **Данные большие (> 1 MB на объект):**
   - Загруженные курсы
   - Офлайн карты
   - Room: BLOB поддерживается, но неэффективен для больших файлов

3. **Не нужны SQL-запросы:**
   - Если читаете весь файл целиком
   - Если данные — один большой JSON

**Выбирай Room когда:**
- Нужны связи (foreign keys)
- Нужна фильтрация (WHERE clauses)
- Нужна сортировка/группировка
- Объекты маленькие (< 100 KB)

**Гибридный подход:**
```kotlin
@Entity
data class Course(
    @PrimaryKey val id: Long,
    val title: String,
    val videoPath: String  // File path → actual video in filesDir
)
```
Метаданные в Room, файлы отдельно.

</details>

### 4. Что такое Single Source of Truth в контексте persistence?

<details>
<summary>Показать ответ</summary>

**Single Source of Truth (SSOT) = один источник данных для всего приложения.**

**Проблема без SSOT:**
```kotlin
// ViewModel 1
val users = api.getUsers()  // Network

// ViewModel 2
val users = database.getAllUsers()  // Local DB

// Какие данные актуальны? Конфликт!
```

**Решение с SSOT (Repository pattern):**
```kotlin
class UserRepository(
    private val api: UserApi,
    private val dao: UserDao
) {
    // Database = единственный источник истины
    val users: Flow<List<User>> = dao.observeAll()

    suspend fun refresh() {
        val networkUsers = api.getUsers()
        dao.insertAll(networkUsers)  // Update SSOT
    }
}

// Все ViewModels читают из одного источника
class UserListViewModel(repo: UserRepository) {
    val users = repo.users  // Всегда синхронизированы
}
```

**Паттерн:**
1. **UI читает из БД (SSOT)**
2. **Network обновляет БД**
3. **Flow автоматически обновляет UI**

**Зачем:**
- Нет конфликтов данных
- Офлайн режим "бесплатно"
- Consistent UI (все экраны видят одинаковые данные)

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "SharedPreferences = безопасно" | SharedPreferences хранит plaintext XML. На rooted device читается. Для secrets — EncryptedSharedPreferences |
| "Room медленнее чем raw SQLite" | Room добавляет compile-time overhead, не runtime. Generated DAO code = оптимальный SQLite. Иногда быстрее из-за query caching |
| "DataStore заменил SharedPreferences" | DataStore — эволюция, не replacement. Для простых key-value SharedPreferences достаточно. DataStore для typed data или when you need Flow |
| "Room.inMemoryDatabaseBuilder для production" | In-memory database теряется при process death. Только для тестов. Production = databaseBuilder |
| "@Transaction на каждый DAO метод" | Transaction добавляет overhead. Нужен только для multiple operations или read consistency. Single insert не требует explicit transaction |
| "Flow из Room = все обновления" | Flow emits при ЛЮБОМ изменении таблицы, даже нерелевантном. Используй distinctUntilChanged() для optimization |
| "SQLite поддерживает все SQL фичи" | SQLite — embedded DB, не PostgreSQL. Нет window functions (до 3.25), нет full outer join. Знай ограничения |
| "Room Migration можно пропустить" | Без migration при schema change — crash или data loss. AutoMigration помогает, но не всегда. Test migrations! |
| "DataStore Proto = сложно" | Proto DataStore требует .proto файл, но даёт type safety. Protobuf binary = компактнее JSON. Worth it для complex data |
| "ContentProvider для internal data" | ContentProvider для sharing с другими apps. Если данные только для вашего app — Room напрямую проще |

---

## CS-фундамент

| CS-концепция | Как применяется в Persistence |
|--------------|-------------------------------|
| **ACID Transactions** | SQLite (Room) обеспечивает Atomicity, Consistency, Isolation, Durability. @Transaction для multiple operations |
| **ORM (Object-Relational Mapping)** | Room = compile-time ORM. Entity ↔ Table. DAO methods → SQL queries. Type-safe access |
| **Normalization** | Database design для Room. 1NF, 2NF, 3NF. Relations через Foreign Keys. @Relation для joins |
| **Indexing** | @Index для ускорения WHERE queries. B-tree indexes в SQLite. Trade-off: insert speed vs query speed |
| **Reactive Streams** | Room возвращает Flow<List<T>>. DataStore возвращает Flow<T>. Push-based updates |
| **Serialization** | Protobuf для Proto DataStore. JSON для Preferences DataStore. Room TypeConverters для complex types |
| **Migration** | Schema versioning. Backward compatibility. AutoMigration для simple changes. Manual migration для complex |
| **Single Source of Truth** | Database = SSOT. Network updates SSOT. UI reads from SSOT. Consistency across app |
| **Key-Value Storage** | SharedPreferences, DataStore = key-value. Fast lookup O(1). Simple data structures |
| **File I/O** | DataStore uses coroutines для async file operations. Atomic writes через temp file + rename |

---

## Связи

**Фундамент (нужно знать сначала):**
→ [[android-overview]] — карта раздела Android, архитектурный контекст
→ [[android-activity-lifecycle]] — почему данные теряются при повороте экрана → нужна persistence
→ [[kotlin-coroutines]] — suspend функции в Room DAO, DataStore — это всё корутины
→ [[kotlin-flow]] — Room возвращает Flow<List<User>> для реактивных обновлений UI

**Архитектурные паттерны (как использовать persistence правильно):**
→ [[android-architecture-patterns]] — Repository pattern + Room = Single Source of Truth
→ [[android-threading]] — почему Room нельзя вызывать на main thread, где выполняются suspend функции

**Оптимизация (после базового понимания):**
→ [[database-design-optimization]] — индексы для WHERE clauses, нормализация таблиц, EXPLAIN QUERY PLAN

---

## Источники

- [Save Data in a Local Database Using Room - Android Developers](https://developer.android.com/training/data-storage/room) — официальная документация Room
- [Persist Data with Room Codelab](https://developer.android.com/codelabs/basic-android-kotlin-compose-persisting-data-room) — практический codelab
- [DataStore - Android Developers](https://developer.android.com/topic/libraries/architecture/datastore) — официальная документация DataStore

---

*Проверено: 2026-01-09 | На основе официальной документации Android*
