---
title: "KMP Android Integration: Полный гайд по интеграции с Android"
created: 2026-01-03
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - topic/android
  - jetpack
  - room
  - datastore
  - viewmodel
  - integration
  - type/concept
  - level/intermediate
related:
  - "[[kmp-overview]]"
  - "[[kmp-project-structure]]"
  - "[[android-architecture-patterns]]"
  - "[[kotlin-coroutines]]"
prerequisites:
  - "[[kmp-getting-started]]"
  - "[[kmp-project-structure]]"
cs-foundations:
  - "[[bytecode-virtual-machines]]"
  - "[[compilation-pipeline]]"
  - "[[memory-model-fundamentals]]"
  - "[[garbage-collection-explained]]"
status: published
reading_time: 43
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# KMP Android Integration

> **TL;DR:** Android — первоклассный target в KMP. Jetpack библиотеки (Room 2.8+, DataStore 1.1+, ViewModel 2.8+, Paging 3.3+) официально поддерживают KMP. Новый Android-KMP Gradle plugin (`com.android.kotlin.multiplatform.library`) заменяет устаревший `com.android.library`. Миграция инкрементальная: начните с data layer, потом domain, потом presentation. 60-80% бизнес-логики выносится в shared module без изменения существующего Android кода.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| **JVM & Bytecode** | Почему Android — "родной" target | [[bytecode-virtual-machines]] |
| **Compilation Pipeline** | Как Kotlin компилируется | [[compilation-pipeline]] |
| **GC (Garbage Collection)** | Memory management в JVM | [[garbage-collection-explained]] |
| Android Development | Базовое понимание Android | [Android Basics](https://developer.android.com/courses) |
| Kotlin Coroutines | Async код в KMP | [[kotlin-coroutines]] |
| Jetpack Compose | UI в Android | [[compose-basics]] |
| Gradle Kotlin DSL | Конфигурация проекта | [[gradle-kotlin-dsl]] |
| KMP Project Structure | Основы KMP | [[kmp-project-structure]] |

> **Рекомендация:** Для понимания ПОЧЕМУ Android — идеальный target для KMP, прочитай CS-фундамент о JVM и bytecode. Это объяснит архитектурные преимущества.

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **Shared Module** | KMP модуль с общим кодом | Рецептурная книга, используемая на всех кухнях |
| **androidMain** | Source set для Android-специфичного кода | Специи, которые добавляют только в определённой стране |
| **Android-KMP Plugin** | Новый Gradle plugin для Android targets | Новый адаптер вместо старого переходника |
| **BundledSQLiteDriver** | Кросс-платформенный SQLite драйвер | Универсальный ключ для всех замков |
| **Type-safe project accessors** | Доступ к модулям через `projects.shared` | GPS-навигатор вместо бумажной карты |

---

## Почему Android — идеальный target для KMP

### Фундаментальное преимущество: общий runtime

Android использует JVM-based runtime (ART — Android Runtime). Kotlin был создан как JVM язык. Это означает **zero impedance mismatch**:

```
Kotlin → JVM Bytecode → ART (Android Runtime)
         ↑
         └── Прямая компиляция, без bridges
```

Сравните с iOS, где нужен ObjC bridge:
```
Kotlin → LLVM IR → Native → ObjC Headers → Swift
                            ↑
                            └── Дополнительный слой
```

### Что это даёт на практике

| Аспект | Android | iOS |
|--------|---------|-----|
| **Interop** | Прямой (JVM ↔ JVM) | Через ObjC bridge |
| **Debugging** | Полный (JDWP) | Ограниченный (LLDB) |
| **Jetpack libraries** | Нативная поддержка | Портированные |
| **Build time** | Быстрый (JVM bytecode) | Медленнее (LLVM) |
| **Binary size** | +0 MB overhead | +9 MB (Compose MP) |
| **Memory model** | Одинаковый GC | Разные (GC vs ARC) |

### Jetpack: от Android-only к Multiplatform

Google активно портирует Jetpack библиотеки на KMP:

```
2023: Room, DataStore, Collection → KMP stable
2024: ViewModel, Paging, Lifecycle → KMP stable
2025: Navigation, SavedState → KMP stable
2026: Все core библиотеки → KMP first-class
```

**Это означает:** код, написанный для Android, может работать на iOS без изменений (если не использует Android-only APIs).

### Performance: практически нативный

Результаты бенчмарков 2025:
- **Startup time:** KMP +12ms vs native Android (negligible)
- **Runtime:** "on par or better" (Google Docs team)
- **Memory:** Same GC, same performance characteristics

**Вывод:** Android в KMP — это не "поддержка платформы", а естественная среда выполнения.

---

## Статус Jetpack библиотек в KMP (январь 2026)

```
┌─────────────────────────────────────────────────────────────────────┐
│               JETPACK LIBRARIES KMP SUPPORT MATRIX                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   Library          Version    Android  iOS  JVM  Web   Status      │
│   ────────────────────────────────────────────────────────────      │
│   Room             2.8.4      ✅       ✅   ✅   ❌   Stable        │
│   DataStore        1.2.0      ✅       ✅   ✅   ✅   Stable        │
│   ViewModel        2.10.0     ✅       ✅   ✅   ✅   Stable        │
│   Lifecycle        2.10.0     ✅       ✅   ✅   ✅   Stable        │
│   Paging           3.3.6      ✅       ✅   ✅   ✅   Stable        │
│   Navigation       2.9.6      ✅       ✅*  ✅*  ✅*  Stable        │
│   SavedState       1.4.0      ✅       ✅   ✅   ✅   Stable        │
│   Collection       1.5.0      ✅       ✅   ✅   ✅   Stable        │
│   Annotation       1.9.1      ✅       ✅   ✅   ✅   Stable        │
│   SQLite           2.6.2      ✅       ✅   ✅   ✅   Stable        │
│                                                                     │
│   * Navigation for non-Android via JetBrains Compose Multiplatform  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Tier Support:**
- **Tier 1 (Full CI testing):** Android, iOS, JVM
- **Tier 2 (Partial testing):** macOS, Linux
- **Tier 3 (Untested):** watchOS, tvOS, Windows, Web

---

## Добавление KMP к существующему Android проекту

### Способ 1: Android Studio Template (рекомендуется)

**Требования:**
- Android Studio Meerkat 2024.3.1+ или Otter 2025.2.1+
- Android Gradle Plugin 8.8.0+
- Kotlin 2.0.0+

```
1. File → New → New Module
2. Выбрать "Kotlin Multiplatform Shared Module"
3. Настроить:
   - Module name: shared
   - Package name: com.example.app.shared
4. Finish → Gradle Sync
```

**Результат — структура:**

```
project/
├── app/                          # Существующий Android app
│   └── build.gradle.kts
├── shared/                       # Новый KMP module
│   ├── build.gradle.kts
│   └── src/
│       ├── commonMain/kotlin/    # Общий код
│       ├── commonTest/kotlin/    # Общие тесты
│       ├── androidMain/kotlin/   # Android-специфичный код
│       └── iosMain/kotlin/       # iOS-специфичный код
└── settings.gradle.kts           # Включает :shared
```

### Способ 2: Ручное создание модуля

**1. Создать директорию shared/**

```bash
mkdir -p shared/src/{commonMain,commonTest,androidMain,iosMain}/kotlin
```

**2. Добавить в settings.gradle.kts:**

```kotlin
include(":shared")
```

**3. Создать shared/build.gradle.kts:**

```kotlin
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.kotlin.multiplatform.library)
}

kotlin {
    // Android target через новый plugin
    androidLibrary {
        namespace = "com.example.shared"
        compileSdk = 35
        minSdk = 24
    }

    // iOS targets
    listOf(
        iosX64(),
        iosArm64(),
        iosSimulatorArm64()
    ).forEach { iosTarget ->
        iosTarget.binaries.framework {
            baseName = "SharedKit"
            isStatic = true
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.kotlinx.coroutines.core)
        }

        androidMain.dependencies {
            implementation(libs.androidx.core.ktx)
        }
    }
}
```

**4. Подключить к Android app:**

```kotlin
// app/build.gradle.kts
dependencies {
    implementation(project(":shared"))
    // или с Type-safe accessors:
    // implementation(projects.shared)
}
```

---

## Новый Android-KMP Gradle Plugin

### Зачем новый plugin?

| com.android.library (устаревает) | com.android.kotlin.multiplatform.library |
|----------------------------------|------------------------------------------|
| Deprecated в AGP 9.0+ | Современный подход |
| Удаляется в AGP 10.0 (2026) | Долгосрочная поддержка |
| Сложная конфигурация | Simplified single-variant |
| Отдельный `android {}` блок | Интегрирован в `kotlin {}` DSL |

### Конфигурация нового plugin

**libs.versions.toml:**

```toml
[versions]
agp = "8.13.2"
kotlin = "2.1.21"

[plugins]
kotlin-multiplatform = { id = "org.jetbrains.kotlin.multiplatform", version.ref = "kotlin" }
android-kotlin-multiplatform-library = { id = "com.android.kotlin.multiplatform.library", version.ref = "agp" }
```

**Root build.gradle.kts:**

```kotlin
plugins {
    alias(libs.plugins.kotlin.multiplatform) apply false
    alias(libs.plugins.android.kotlin.multiplatform.library) apply false
}
```

**Module build.gradle.kts:**

```kotlin
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.kotlin.multiplatform.library)
}

kotlin {
    androidLibrary {
        namespace = "com.example.shared"
        compileSdk = 35
        minSdk = 24

        // Java compilation (отключено по умолчанию для скорости)
        withJava()

        // Android Resources (отключены по умолчанию)
        androidResources {
            enable = true
        }

        // Compiler options
        compilerOptions.configure {
            jvmTarget.set(JvmTarget.JVM_17)
        }
    }
}
```

### Тесты в новом plugin

```kotlin
kotlin {
    androidLibrary {
        // Host-side unit tests (локальная JVM)
        withHostTestBuilder {}.configure {
            // Конфигурация unit тестов
        }

        // Device-side instrumented tests
        withDeviceTestBuilder {
            sourceSetTreeName = "test"
        }.configure {
            instrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        }
    }
}
```

### Ключевые отличия

| Аспект | Старый plugin | Новый Android-KMP plugin |
|--------|---------------|-------------------------|
| Build Types | debug/release | Single variant |
| Product Flavors | Поддерживаются | Не поддерживаются |
| Java compilation | Включено | Отключено (opt-in) |
| Tests | Включены | Отключены (opt-in) |
| Configuration block | `android {}` | `androidLibrary {}` внутри `kotlin {}` |

---

## Интеграция Jetpack Room

### Полная настройка Room для KMP

**1. libs.versions.toml:**

```toml
[versions]
room = "2.8.4"
sqlite = "2.6.2"
ksp = "2.1.21-1.0.29"

[libraries]
androidx-room-runtime = { module = "androidx.room:room-runtime", version.ref = "room" }
androidx-room-compiler = { module = "androidx.room:room-compiler", version.ref = "room" }
androidx-sqlite-bundled = { module = "androidx.sqlite:sqlite-bundled", version.ref = "sqlite" }

[plugins]
ksp = { id = "com.google.devtools.ksp", version.ref = "ksp" }
androidx-room = { id = "androidx.room", version.ref = "room" }
```

**2. shared/build.gradle.kts:**

```kotlin
plugins {
    alias(libs.plugins.kotlin.multiplatform)
    alias(libs.plugins.android.kotlin.multiplatform.library)
    alias(libs.plugins.ksp)
    alias(libs.plugins.androidx.room)
}

kotlin {
    androidLibrary {
        namespace = "com.example.shared"
        compileSdk = 35
        minSdk = 24
    }

    listOf(iosX64(), iosArm64(), iosSimulatorArm64()).forEach {
        it.binaries.framework {
            baseName = "SharedKit"
            isStatic = true
            linkerOpts.add("-lsqlite3")  // Для NativeSQLiteDriver
        }
    }

    sourceSets {
        commonMain.dependencies {
            implementation(libs.androidx.room.runtime)
            implementation(libs.androidx.sqlite.bundled)
        }
    }
}

// KSP для каждого target
dependencies {
    add("kspAndroid", libs.androidx.room.compiler)
    add("kspIosSimulatorArm64", libs.androidx.room.compiler)
    add("kspIosX64", libs.androidx.room.compiler)
    add("kspIosArm64", libs.androidx.room.compiler)
}

// Schema export
room {
    schemaDirectory("$projectDir/schemas")
}
```

**3. Entity (commonMain):**

```kotlin
// commonMain/kotlin/com/example/shared/data/TodoEntity.kt
@Entity(tableName = "todos")
data class TodoEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val description: String,
    val isCompleted: Boolean = false,
    val createdAt: Long = System.currentTimeMillis()
)
```

**4. DAO (commonMain):**

```kotlin
// commonMain/kotlin/com/example/shared/data/TodoDao.kt
@Dao
interface TodoDao {
    @Query("SELECT * FROM todos ORDER BY createdAt DESC")
    fun getAllTodos(): Flow<List<TodoEntity>>

    @Query("SELECT * FROM todos WHERE id = :id")
    suspend fun getTodoById(id: Long): TodoEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertTodo(todo: TodoEntity): Long

    @Update
    suspend fun updateTodo(todo: TodoEntity)

    @Delete
    suspend fun deleteTodo(todo: TodoEntity)

    @Query("SELECT COUNT(*) FROM todos WHERE isCompleted = 0")
    fun getActiveTodoCount(): Flow<Int>
}
```

> ⚠️ **Важно:** Все DAO функции должны быть `suspend` для кросс-платформенной совместимости. Используйте `Flow<T>` вместо `LiveData`.

**5. Database (commonMain):**

```kotlin
// commonMain/kotlin/com/example/shared/data/AppDatabase.kt
@Database(
    entities = [TodoEntity::class],
    version = 1,
    exportSchema = true
)
@ConstructedBy(AppDatabaseConstructor::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun todoDao(): TodoDao
}

// Compiler сгенерирует реализацию
@Suppress("NO_ACTUAL_FOR_EXPECT")
expect object AppDatabaseConstructor : RoomDatabaseConstructor<AppDatabase> {
    override fun initialize(): AppDatabase
}

// Factory function для создания database
fun getRoomDatabase(
    builder: RoomDatabase.Builder<AppDatabase>
): AppDatabase {
    return builder
        .setDriver(BundledSQLiteDriver())
        .setQueryCoroutineContext(Dispatchers.IO)
        .build()
}
```

**6. Platform-specific builders:**

```kotlin
// androidMain/kotlin/com/example/shared/data/Database.android.kt
fun getDatabaseBuilder(context: Context): RoomDatabase.Builder<AppDatabase> {
    val dbFile = context.getDatabasePath("app.db")
    return Room.databaseBuilder<AppDatabase>(
        context = context.applicationContext,
        name = dbFile.absolutePath
    )
}

// iosMain/kotlin/com/example/shared/data/Database.ios.kt
fun getDatabaseBuilder(): RoomDatabase.Builder<AppDatabase> {
    val dbFilePath = documentDirectory() + "/app.db"
    return Room.databaseBuilder<AppDatabase>(
        name = dbFilePath
    )
}

private fun documentDirectory(): String {
    val documentDirectory = NSFileManager.defaultManager.URLForDirectory(
        directory = NSDocumentDirectory,
        inDomain = NSUserDomainMask,
        appropriateForURL = null,
        create = false,
        error = null
    )
    return requireNotNull(documentDirectory?.path)
}
```

### Room KMP Ограничения

| Функция | Android | KMP (iOS/JVM) |
|---------|---------|---------------|
| `LiveData` return types | ✅ | ❌ Используйте Flow |
| Sync DAO methods | ✅ | ❌ Только suspend |
| `@RawQuery` с SupportSQLiteQuery | ✅ | ❌ Используйте RoomRawQuery |
| Query callbacks | ✅ | ❌ |
| Auto-closing database | ✅ | ❌ |
| Pre-packaged databases | ✅ | ❌ |
| Multi-instance invalidation | ✅ | ❌ |

---

## Интеграция Jetpack DataStore

### Preferences DataStore в KMP

**libs.versions.toml:**

```toml
[versions]
datastore = "1.2.0"

[libraries]
androidx-datastore-preferences = { module = "androidx.datastore:datastore-preferences", version.ref = "datastore" }
```

**build.gradle.kts:**

```kotlin
commonMain.dependencies {
    implementation(libs.androidx.datastore.preferences)
}
```

**commonMain/kotlin/PreferencesDataStore.kt:**

```kotlin
// Expect declaration для platform-specific path
expect fun createDataStore(): DataStore<Preferences>

// Common preferences keys
object PreferencesKeys {
    val DARK_MODE = booleanPreferencesKey("dark_mode")
    val AUTH_TOKEN = stringPreferencesKey("auth_token")
    val USER_ID = longPreferencesKey("user_id")
    val ONBOARDING_COMPLETED = booleanPreferencesKey("onboarding_completed")
}

// Repository для работы с preferences
class UserPreferencesRepository(
    private val dataStore: DataStore<Preferences>
) {
    val darkModeFlow: Flow<Boolean> = dataStore.data
        .map { preferences ->
            preferences[PreferencesKeys.DARK_MODE] ?: false
        }

    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { preferences ->
            preferences[PreferencesKeys.DARK_MODE] = enabled
        }
    }

    suspend fun clearAll() {
        dataStore.edit { it.clear() }
    }
}
```

**androidMain/kotlin/PreferencesDataStore.android.kt:**

```kotlin
actual fun createDataStore(context: Context): DataStore<Preferences> {
    return PreferenceDataStoreFactory.createWithPath(
        produceFile = {
            context.filesDir.resolve("user_prefs.preferences_pb").absolutePath.toPath()
        }
    )
}
```

**iosMain/kotlin/PreferencesDataStore.ios.kt:**

```kotlin
actual fun createDataStore(): DataStore<Preferences> {
    return PreferenceDataStoreFactory.createWithPath(
        produceFile = {
            val documentDirectory = NSFileManager.defaultManager.URLForDirectory(
                directory = NSDocumentDirectory,
                inDomain = NSUserDomainMask,
                appropriateForURL = null,
                create = false,
                error = null
            )
            val path = requireNotNull(documentDirectory).path + "/user_prefs.preferences_pb"
            path.toPath()
        }
    )
}
```

### DataStore Ограничения в KMP

| Тип DataStore | Android | KMP |
|---------------|---------|-----|
| Preferences DataStore | ✅ | ✅ Полная поддержка |
| Proto DataStore | ✅ | ❌ Не поддерживается |
| Multi-process | ✅ | ❌ |

---

## Интеграция Jetpack ViewModel

### Shared ViewModel в KMP

**libs.versions.toml:**

```toml
[versions]
lifecycle = "2.10.0"

[libraries]
androidx-lifecycle-viewmodel = { module = "androidx.lifecycle:lifecycle-viewmodel", version.ref = "lifecycle" }
```

**build.gradle.kts:**

```kotlin
commonMain.dependencies {
    implementation(libs.androidx.lifecycle.viewmodel)
}

// Для Desktop нужен Swing dispatcher
jvmMain.dependencies {
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-swing:1.8.0")
}
```

**commonMain/kotlin/TodoViewModel.kt:**

```kotlin
class TodoViewModel(
    private val todoRepository: TodoRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(TodoUiState())
    val uiState: StateFlow<TodoUiState> = _uiState.asStateFlow()

    init {
        loadTodos()
    }

    private fun loadTodos() {
        viewModelScope.launch {
            todoRepository.getAllTodos()
                .catch { e ->
                    _uiState.update { it.copy(error = e.message) }
                }
                .collect { todos ->
                    _uiState.update { it.copy(
                        todos = todos,
                        isLoading = false
                    )}
                }
        }
    }

    fun addTodo(title: String, description: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                todoRepository.addTodo(title, description)
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message) }
            }
        }
    }

    fun toggleTodo(todo: Todo) {
        viewModelScope.launch {
            todoRepository.toggleCompleted(todo.id)
        }
    }
}

data class TodoUiState(
    val todos: List<Todo> = emptyList(),
    val isLoading: Boolean = true,
    val error: String? = null
)
```

### Использование в Android Compose

```kotlin
// Android app
@Composable
fun TodoScreen(
    viewModel: TodoViewModel = viewModel { TodoViewModel(todoRepository) }
) {
    val uiState by viewModel.uiState.collectAsState()

    when {
        uiState.isLoading -> LoadingIndicator()
        uiState.error != null -> ErrorMessage(uiState.error!!)
        else -> TodoList(
            todos = uiState.todos,
            onToggle = viewModel::toggleTodo
        )
    }
}
```

### ViewModel в Compose Multiplatform

```kotlin
// Для non-JVM platforms нужен explicit initializer
@Composable
fun TodoScreen() {
    // Нельзя: viewModel<TodoViewModel>() — нет reflection
    // Нужно: явный initializer
    val viewModel = viewModel {
        TodoViewModel(
            todoRepository = // provide dependency
        )
    }

    val uiState by viewModel.uiState.collectAsState()
    // ...
}
```

### Потенциальные конфликты

```kotlin
// Если используете activity-compose, может быть duplicate class error
// Исключите conflicting dependency:
implementation("androidx.activity:activity-compose:1.9.0") {
    exclude(group = "androidx.lifecycle", module = "lifecycle-viewmodel")
}
```

---

## Стратегия постепенной миграции

### Фаза 1: Подготовка (1-2 недели)

```
┌─────────────────────────────────────────────────────────────┐
│                     PREPARATION PHASE                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Аудит Android-специфичных зависимостей                  │
│     • RxJava → Coroutines/Flow                              │
│     • Retrofit → Ktor Client                                │
│     • Hilt/Dagger → Koin/manual DI                          │
│     • SharedPreferences → DataStore                         │
│                                                             │
│  2. Рефакторинг модульной структуры                         │
│     • Выделить :core:data                                   │
│     • Выделить :core:domain                                 │
│     • Изолировать UI от бизнес-логики                       │
│                                                             │
│  3. Убедиться в чистой архитектуре                          │
│     • Repository pattern                                    │
│     • Use cases / Interactors                               │
│     • Separated data sources                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Фаза 2: Data Layer Migration

**Шаг 1: Создать shared module**

```kotlin
// settings.gradle.kts
include(":shared")
```

**Шаг 2: Перенести models**

```kotlin
// commonMain/kotlin/com/example/shared/domain/model/
data class User(
    val id: String,
    val email: String,
    val name: String
)

data class Todo(
    val id: Long,
    val title: String,
    val isCompleted: Boolean
)
```

**Шаг 3: Перенести repository interfaces**

```kotlin
// commonMain/kotlin/com/example/shared/domain/repository/
interface TodoRepository {
    fun getAllTodos(): Flow<List<Todo>>
    suspend fun getTodoById(id: Long): Todo?
    suspend fun addTodo(title: String, description: String): Long
    suspend fun toggleCompleted(id: Long)
    suspend fun deleteTodo(id: Long)
}
```

**Шаг 4: Добавить implementations**

```kotlin
// commonMain/kotlin/com/example/shared/data/repository/
class TodoRepositoryImpl(
    private val todoDao: TodoDao
) : TodoRepository {

    override fun getAllTodos(): Flow<List<Todo>> =
        todoDao.getAllTodos().map { entities ->
            entities.map { it.toDomain() }
        }

    override suspend fun addTodo(title: String, description: String): Long =
        todoDao.insertTodo(
            TodoEntity(title = title, description = description)
        )

    // ... other implementations
}
```

### Фаза 3: Domain Layer Migration

```kotlin
// commonMain/kotlin/com/example/shared/domain/usecase/
class GetTodosUseCase(
    private val repository: TodoRepository
) {
    operator fun invoke(): Flow<List<Todo>> = repository.getAllTodos()
}

class AddTodoUseCase(
    private val repository: TodoRepository
) {
    suspend operator fun invoke(title: String, description: String): Long =
        repository.addTodo(title, description)
}
```

### Фаза 4: Presentation Layer (опционально)

```kotlin
// commonMain/kotlin/com/example/shared/presentation/
class TodoListViewModel(
    private val getTodosUseCase: GetTodosUseCase,
    private val addTodoUseCase: AddTodoUseCase
) : ViewModel() {
    // Shared ViewModel logic
}
```

### Checklist миграции

```markdown
## Data Layer
- [ ] Models перенесены в commonMain
- [ ] Repository interfaces в commonMain
- [ ] Room entities с @Entity в commonMain
- [ ] DAOs с suspend functions в commonMain
- [ ] Room Database настроена
- [ ] Platform-specific builders созданы

## Domain Layer
- [ ] Use cases в commonMain
- [ ] Business logic без Android dependencies

## Presentation Layer
- [ ] ViewModels в commonMain (опционально)
- [ ] UI State classes в commonMain
- [ ] Android app использует shared ViewModels

## Testing
- [ ] Common tests работают
- [ ] Android tests проходят
- [ ] iOS tests проходят (если добавлен iOS)
```

---

## Несовместимые библиотеки и замены

| Android-only | KMP-совместимая замена | Сложность миграции |
|--------------|------------------------|-------------------|
| RxJava | kotlinx-coroutines + Flow | Средняя |
| Retrofit | Ktor Client | Низкая |
| Hilt/Dagger | Koin / Kodein / Manual DI | Средняя |
| SharedPreferences | DataStore Preferences | Низкая |
| LiveData | StateFlow / SharedFlow | Низкая |
| Room (старые версии) | Room 2.7.0+ / SQLDelight | Низкая |
| Gson | kotlinx.serialization | Низкая |
| OkHttp | Ktor Client engine | Низкая |
| WorkManager | Platform-specific | Высокая |
| Firebase | Platform-specific wrappers | Высокая |

---

## Common Issues и Troubleshooting

### 1. Duplicate class: ViewModel

**Проблема:**
```
Duplicate class androidx.lifecycle.ViewModel found in modules
```

**Решение:**
```kotlin
implementation("androidx.activity:activity-compose:1.9.0") {
    exclude(group = "androidx.lifecycle", module = "lifecycle-viewmodel")
}
```

### 2. KSP не видит Room entities

**Проблема:** Room compiler не генерирует код

**Решение:**
```kotlin
// Добавить KSP для каждого target
dependencies {
    add("kspAndroid", libs.androidx.room.compiler)
    add("kspIosArm64", libs.androidx.room.compiler)
    add("kspIosSimulatorArm64", libs.androidx.room.compiler)
    add("kspIosX64", libs.androidx.room.compiler)
}
```

### 3. Kotlin Native compiler daemon issues

**Проблема:** Slow builds, daemon crashes

**Решение (gradle.properties):**
```properties
kotlin.native.disableCompilerDaemon=true
```

### 4. "Expected android module not found"

**Проблема:** IDE sync failure при dependency substitution

**Решение:** Обновить Android Studio до последней версии, проверить AGP compatibility

### 5. AGP 9.0+ deprecated APIs

**Проблема:** Warnings о deprecated APIs

**Решение:** Мигрировать на `com.android.kotlin.multiplatform.library`:

```kotlin
// OLD
plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.multiplatform")
}

android { /* ... */ }

// NEW
plugins {
    id("org.jetbrains.kotlin.multiplatform")
    id("com.android.kotlin.multiplatform.library")
}

kotlin {
    androidLibrary { /* ... */ }
}
```

### 6. Desktop ViewModel scope не работает

**Проблема:** `viewModelScope` uses Dispatchers.Main.immediate

**Решение:**
```kotlin
// jvmMain dependencies
implementation("org.jetbrains.kotlinx:kotlinx-coroutines-swing:1.8.0")
```

---

## Performance и Production

### Build Performance

```kotlin
// gradle.properties оптимизации
org.gradle.caching=true
org.gradle.parallel=true
org.gradle.jvmargs=-Xmx4g -XX:+UseParallelGC

# Kotlin specific
kotlin.incremental=true
kotlin.caching.enabled=true
```

### Runtime Performance

> "KMP avoids the performance overhead common in other cross-platform tools by compiling to native binaries and utilizing native UI toolkits."
> — [InfoQ: Evaluating KMP](https://www.infoq.com/articles/kotlin-multiplatform-evaluation/)

**Результаты в production:**
- **Google Docs iOS:** "Runtime performance is on par or better than before"
- **McDonald's:** "Fewer crashes and better performance across both platforms"
- **Netflix:** "Lowering long-term maintenance costs significantly"

### Benchmarking

```kotlin
// Использовать kotlinx-benchmark для KMP
plugins {
    id("org.jetbrains.kotlinx.benchmark") version "0.4.10"
}

// Добавить benchmark source set
benchmark {
    targets {
        register("android")
        register("jvm")
        register("native")
    }
}
```

---

## Кто использует в production

| Компания | Продукт | Результат |
|----------|---------|-----------|
| **Google Docs** | iOS app | Feature parity faster, KMP validated |
| **McDonald's** | Global mobile app | Fewer crashes, better performance |
| **Netflix** | Studio apps (12+) | 60% shared code, reduced maintenance |
| **Cash App** | Fintech | Shared business logic |
| **Philips** | Healthcare | Critical apps on KMP |
| **Forbes** | News app | Faster development |
| **Duolingo** | Education | Cross-platform features |
| **Blinkit** | Quick commerce | Shared core |
| **Swiggy** | Food delivery | Unified experience |
| **Zomato** | Food delivery | Shared business logic |

---

## Мифы и заблуждения

### Миф 1: "KMP на Android добавляет overhead"

**Реальность:** KMP на Android компилируется в точно такой же JVM bytecode, как обычный Kotlin/Android. Нет runtime overhead, нет дополнительных слоёв. Это тот же код, просто организованный в multiplatform structure.

**Бенчмарки:** +12ms startup difference (negligible, в пределах погрешности).

### Миф 2: "Jetpack библиотеки не работают с KMP"

**Реальность (январь 2026):** Room, DataStore, ViewModel, Lifecycle, Paging, Navigation — все stable в KMP. Google официально поддерживает и тестирует на Android, iOS, JVM.

**Ограничения:** Некоторые Android-only features (LiveData, RawQuery с SupportSQLiteQuery) не портированы — используйте Flow и suspend functions.

### Миф 3: "Нужно переписать весь проект для KMP"

**Реальность:** Миграция инкрементальная:
1. Добавить shared module (не трогая существующий код)
2. Постепенно выносить код из Android в shared
3. Android app использует shared как обычную dependency

Существующий Android код продолжает работать без изменений.

### Миф 4: "Новый Android-KMP plugin ломает существующие проекты"

**Реальность:** Старый `com.android.library` продолжает работать до AGP 10.0 (H2 2026). Миграция на `com.android.kotlin.multiplatform.library` опциональна, но рекомендуется. Новый plugin проще и быстрее.

### Миф 5: "Compose Multiplatform увеличивает размер Android APK"

**Реальность:** На Android Compose MP использует **встроенный Skia** системы. Увеличение размера минимальное (в отличие от iOS, где Skia bundled и добавляет ~9 MB).

### Миф 6: "Нельзя использовать Hilt/Dagger с KMP"

**Реальность:** Напрямую нельзя (они Android-only), но есть рабочие паттерны:
- Koin — полностью поддерживает KMP
- Manual DI — работает везде
- Hilt в androidMain + interface в commonMain

---

## Рекомендуемые источники

### CS-фундамент для глубокого понимания

| Материал | Зачем нужен |
|----------|-------------|
| [[bytecode-virtual-machines]] | Почему Android — "родной" target (JVM) |
| [[compilation-pipeline]] | Как Kotlin компилируется для разных платформ |
| [[garbage-collection-explained]] | Memory management в JVM/ART |
| [[memory-model-fundamentals]] | Threading и concurrency |

### Официальная документация

| Источник | Тип | Описание |
|----------|-----|----------|
| [Android KMP Guide](https://developer.android.com/kotlin/multiplatform) | Official | Главная документация |
| [Android-KMP Plugin](https://developer.android.com/kotlin/multiplatform/plugin) | Official | Новый Gradle plugin |
| [Room KMP Setup](https://developer.android.com/kotlin/multiplatform/room) | Official | Настройка Room |
| [DataStore KMP](https://developer.android.com/kotlin/multiplatform/datastore) | Official | DataStore configuration |
| [Migration Guide](https://developer.android.com/kotlin/multiplatform/migrate) | Official | Добавление KMP к существующему проекту |

### Codelabs и Samples

| Источник | Тип | Описание |
|----------|-----|----------|
| [KMP Get Started](https://developer.android.com/codelabs/kmp-get-started) | Codelab | Первый KMP проект |
| [Migrate Room to KMP](https://developer.android.com/codelabs/kmp-migrate-room) | Codelab | Миграция Room |
| [kotlin-multiplatform-samples](https://github.com/android/kotlin-multiplatform-samples) | GitHub | Official samples (Fruitties, DiceRoller) |

### Блоги и статьи

| Источник | Тип | Описание |
|----------|-----|----------|
| [Google I/O 2025 KMP](https://android-developers.googleblog.com/2025/05/android-kotlin-multiplatform-google-io-kotlinconf-2025.html) | Blog | Анонсы Google |
| [Touchlab KMP ViewModel](https://touchlab.co/kmp-viewmodel) | Expert | ViewModel guide |
| [John O'Reilly](https://johnoreilly.dev/) | Blog | KMP практики |
| [Marco Gomiero](https://www.marcogomiero.com/) | Blog | Migration guides |

### Сообщество

| Ресурс | Тип | Описание |
|--------|-----|----------|
| [#multiplatform](https://kotlinlang.slack.com/) | Slack | Kotlin Slack |
| [r/Kotlin](https://reddit.com/r/Kotlin) | Reddit | Community |
| [klibs.io](https://klibs.io) | Directory | 2000+ KMP библиотек |

---

## Связь с другими темами

**[[kmp-overview]]** — Обзорный материал по Kotlin Multiplatform, описывающий общую архитектуру проекта, структуру source sets и roadmap изучения. Android-интеграция является одной из ключевых платформенных целей KMP, и понимание общей картины помогает правильно позиционировать Android-специфичный код относительно shared-модулей. Начинать изучение KMP рекомендуется именно с overview перед погружением в платформенные детали.

**[[kmp-project-structure]]** — Структура проекта KMP определяет, как организованы source sets (commonMain, androidMain, iosMain) и как Gradle конфигурирует зависимости для каждой платформы. Для Android-интеграции критически важно понимать, как androidMain source set взаимодействует с commonMain и какие Jetpack-библиотеки можно подключать напрямую. Правильная организация модулей позволяет максимизировать переиспользование кода между платформами.

**[[android-architecture-patterns]]** — Паттерны Android-архитектуры (MVVM, MVI, Clean Architecture) напрямую влияют на то, как организуется shared-код в KMP. ViewModel, Repository и UseCase из Android Jetpack адаптируются для мультиплатформенного использования через lifecycle-viewmodel-compose. Знание Android-паттернов помогает проектировать shared-слой так, чтобы Android-приложение получало нативный developer experience.

**[[kotlin-coroutines]]** — Корутины обеспечивают асинхронные операции в shared KMP-коде, который затем используется на Android. Room KMP, Ktor, DataStore — все ключевые библиотеки в Android-интеграции работают через корутины и Flow. Понимание Dispatchers, structured concurrency и StateFlow необходимо для корректной реализации реактивного UI на Android с shared бизнес-логикой.

## Источники и дальнейшее чтение

1. **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* — Глубокое понимание Kotlin необходимо для работы с KMP на Android: корутины, sealed classes, delegation и extension functions используются повсеместно в Android-интеграции.
2. **Moskala M. (2022).** *Kotlin Coroutines: Deep Dive.* — Детальное руководство по корутинам, которые являются основой асинхронного программирования в KMP. Особенно важны главы про Flow, StateFlow и интеграцию с Android Lifecycle.
3. **Martin R. (2017).** *Clean Architecture.* — Принципы разделения ответственности и dependency inversion, которые определяют границу между shared KMP-модулем и Android-платформенным кодом. Помогает правильно спроектировать слой интеграции с Jetpack.

---

## Проверь себя

> [!question]- Почему KMP на Android не добавляет runtime overhead, в отличие от React Native?
> KMP компилируется в JVM bytecode -- точно такой же, как обычный Kotlin/Android код. Нет bridge между языками, нет дополнительного runtime. Shared-модуль подключается как обычная Android library (.aar), и ART исполняет его как нативный Android-код.

> [!question]- Вы интегрируете Room KMP в shared-модуль. Почему Room entity и DAO описываются в commonMain, а RoomDatabase.Builder создаётся в platform source sets?
> Entity и DAO -- это контракты (data classes и interfaces), не зависящие от платформы. А RoomDatabase.Builder требует platform-специфичный путь к файлу базы данных (Context.getDatabasePath на Android, NSHomeDirectory на iOS), поэтому создание builder вынесено в expect/actual.

> [!question]- Почему для KMP-интеграции на Android рекомендуется начинать с shared data layer, а не с shared ViewModel?
> Shared data layer (networking, repositories, use cases) минимально затрагивает существующую архитектуру Android-приложения. ViewModel требует перестройки UI-слоя и зависит от lifecycle-viewmodel-compose. Последовательная миграция снижу вверх снижает риски.

> [!question]- Какие Jetpack-библиотеки официально поддерживают KMP и почему это важно?
> Room, DataStore, ViewModel, Paging, Annotations, Collections. Это важно потому что Android-разработчики могут продолжать использовать привычные API в shared-коде, а не изучать альтернативные библиотеки. Это снижает порог входа и ускоряет миграцию.

---

## Ключевые карточки

Как shared KMP-модуль подключается к Android-приложению?
?
Как обычная Gradle-зависимость: implementation(project(":shared")). KMP компилирует commonMain + androidMain в JVM bytecode, и shared-модуль становится стандартной Android library (.aar).

Что такое lifecycle-viewmodel-compose в контексте KMP?
?
Multiplatform-версия Jetpack ViewModel, позволяющая создавать shared ViewModel в commonMain. На Android работает через стандартный Jetpack lifecycle, на iOS -- через Compose Multiplatform.

Как DataStore KMP работает с platform-specific storage?
?
DataStore в commonMain определяет preferences/proto schema. На Android использует файловую систему через Context.filesDir, на iOS -- NSDocumentDirectory. Путь к файлу передаётся через expect/actual factory.

Чем отличается интеграция Ktor на Android от других platform targets?
?
Android использует OkHttp engine (ktor-client-okhttp), оптимизированный для Android. На iOS -- Darwin engine, на JVM -- CIO. Выбор engine влияет на производительность, поддержку сертификатов и совместимость с platform networking stack.

Как Room KMP обеспечивает кросс-платформенную работу с базой данных?
?
Room KMP использует SQLite на всех платформах. Entity, DAO и queries описываются в commonMain. Platform-specific часть -- только создание RoomDatabase.Builder с путём к файлу БД через expect/actual.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-ios-deep-dive]] | Интеграция KMP с iOS: SwiftUI, SKIE, memory |
| Углубиться | [[kmp-architecture-patterns]] | Clean Architecture и MVI в KMP |
| Смежная тема | [[android-architecture-patterns]] | Android-паттерны, адаптированные для KMP |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | Room 2.8.4, DataStore 1.2.0, ViewModel 2.10.0, AGP 8.13.2, Kotlin 2.1.21*
