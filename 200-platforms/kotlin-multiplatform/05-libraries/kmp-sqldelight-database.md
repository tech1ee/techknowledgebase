---
title: "SQLDelight в Kotlin Multiplatform: типобезопасная база данных"
created: 2026-01-03
modified: 2026-02-13
tags:
  - topic/jvm
  - topic/kmp
  - sqldelight
  - topic/databases
  - sqlite
  - type/concept
  - level/intermediate
related:
  - "[[kmp-overview]]"
  - "[[kmp-ktor-networking]]"
  - "[[kmp-architecture-patterns]]"
prerequisites:
  - "[[kmp-getting-started]]"
  - "[[kmp-project-structure]]"
  - "[[kmp-expect-actual]]"
cs-foundations:
  - "[[relational-database-theory]]"
  - "[[acid-transactions]]"
  - "[[sql-query-optimization]]"
  - "[[schema-migration-patterns]]"
  - "[[type-systems-theory]]"
status: published
reading_time: 47
difficulty: 5
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# SQLDelight в Kotlin Multiplatform

> **TL;DR:** SQLDelight 2.x генерирует типобезопасные Kotlin API из SQL-запросов. Compile-time verification схемы и запросов. Multiplatform: Android, iOS, JVM, JS, Native. Drivers: AndroidSqliteDriver, NativeSqliteDriver, JdbcSqliteDriver. Flow extensions для реактивных запросов. Миграции через .sqm файлы. Создан Cash App (Block), используется в production Netflix, McDonald's.

---

## Prerequisites

| Тема | Зачем нужно | Где изучить | CS-фундамент |
|------|-------------|-------------|--------------|
| SQL основы | Запросы, JOIN, индексы | SQLite docs | [[relational-database-theory]] |
| Kotlin Coroutines | Flow для реактивных данных | [[kotlin-coroutines]] | [[reactive-programming-paradigm]] |
| KMP структура | Source sets | [[kmp-project-structure]] | — |
| expect/actual | Platform-specific drivers | [[kmp-expect-actual]] | — |
| Транзакции | ACID, rollback | — | [[acid-transactions]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **.sq файл** | SQL-запросы и схема таблицы | Рецепт блюда — описание ингредиентов и шагов |
| **.sqm файл** | Файл миграции схемы | Инструкция по ремонту — как изменить существующее |
| **SqlDriver** | Платформо-специфичный драйвер SQLite | Адаптер розетки — один интерфейс, разные вилки |
| **Queries** | Сгенерированный класс с методами | Готовое меню — вызываешь по имени |
| **asFlow()** | Превращение запроса в Flow | Подписка на новости — получаешь обновления автоматически |

---

## Теоретические основы

### Формальное определение

> **Type-safe SQL** — подход к работе с реляционными базами данных, при котором SQL-запросы верифицируются компилятором на этапе сборки, а результаты автоматически маппятся в типизированные объекты языка программирования (Ceri, Gottlob, Tanca, 1990, Logic Programming and Databases).

SQLDelight инвертирует традиционный ORM-подход: вместо «Kotlin-объекты → SQL» используется «SQL → Kotlin-объекты».

### Сравнение подходов к базам данных в мобильной разработке

| Подход | Примеры | Схема определяется | Type safety | Platform |
|--------|---------|-------------------|-------------|----------|
| ORM | Room, Core Data, Realm | Через аннотации/модели | Частичная (runtime) | Platform-specific |
| SQL-first | SQLDelight | Через .sq файлы (SQL) | Полная (compile-time) | KMP multiplatform |
| NoSQL | Realm KMP, Firebase | Через модели | Схемалесс | KMP/Platform |
| Key-Value | DataStore, MMKV | Нет формальной схемы | Ключевая | KMP multiplatform |

### SQL-first vs ORM-first: теоретическое обоснование

ORM создаёт **Object-Relational Impedance Mismatch** (Ireland et al., 2009): несоответствие между объектной моделью (наследование, полиморфизм) и реляционной моделью (таблицы, foreign keys). SQLDelight избегает этой проблемы, делая SQL first-class citizen.

### Platform-specific Drivers: паттерн Abstract Factory

SQLDelight использует паттерн **Abstract Factory** (Gamma et al., 1994) для создания SqlDriver на каждой платформе:

| Платформа | Driver | Backend |
|-----------|--------|---------|
| Android | AndroidSqliteDriver | Android SQLite |
| iOS | NativeSqliteDriver | SQLite C library |
| JVM | JdbcSqliteDriver | JDBC + SQLite |

> **Академические источники:** Codd E. (1970). *A Relational Model of Data for Large Shared Data Banks.* — формальная теория реляционных БД. Ireland C. et al. (2009). *A Classification of Object-Relational Impedance Mismatch.* DBKDA.


## Почему SQLDelight? Теоретические основы

### Проблема типобезопасности SQL

SQL — мощный декларативный язык, но имеет фундаментальную проблему интеграции с типизированными языками: **SQL-запросы — это строки, а строки не проверяются компилятором**.

```kotlin
// Runtime error: опечатка в имени колонки
db.rawQuery("SELECT namme FROM users")  // 💥 Crash в runtime

// Runtime error: несовпадение типов
db.rawQuery("SELECT name FROM users WHERE id = 'abc'")  // id — INTEGER!
```

**SQLDelight решает это через compile-time verification:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPILE-TIME SQL VERIFICATION                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   .sq файл (SQL)                                                │
│   ┌─────────────────────────────────┐                          │
│   │ selectByEmail:                  │                          │
│   │ SELECT * FROM User              │                          │
│   │ WHERE email = ?;                │                          │
│   └─────────────────────────────────┘                          │
│                     ↓                                           │
│              SQLDelight Compiler                                │
│              (анализирует SQL)                                  │
│                     ↓                                           │
│   ┌─────────────────────────────────┐                          │
│   │ ✅ Проверяет: таблица User      │                          │
│   │ ✅ Проверяет: колонка email     │                          │
│   │ ✅ Выводит: тип параметра String│                          │
│   │ ✅ Выводит: тип возврата User   │                          │
│   └─────────────────────────────────┘                          │
│                     ↓                                           │
│   Generated Kotlin code:                                        │
│   fun selectByEmail(email: String): Query<User>                │
│                                                                 │
│   Ошибка в SQL → ошибка компиляции → не попадёт в production   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### SQL-first vs ORM: философия подходов

Существуют два принципиально разных подхода к работе с базами данных:

| Аспект | ORM (Room, Hibernate) | SQL-first (SQLDelight) |
|--------|----------------------|------------------------|
| **Исходная точка** | Kotlin/Java классы | SQL-запросы |
| **Генерация** | Код → SQL | SQL → Код |
| **Контроль** | Framework решает как делать запросы | Разработчик пишет точный SQL |
| **Оптимизация** | Сложно (за абстракцией) | Просто (видишь реальный SQL) |
| **N+1 проблема** | Легко допустить | Невозможна (нет lazy loading) |
| **Кривая обучения** | Учишь ORM API | Учишь SQL |

**SQLDelight philosophy:** "Если ты знаешь SQL — ты знаешь SQLDelight". Никакой магии, полный контроль.

### ACID и транзакции в SQLDelight

SQLite (и SQLDelight поверх него) гарантирует **ACID** свойства транзакций:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ACID PROPERTIES                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Atomicity (Атомарность)                                       │
│   └── Все операции в transaction {} либо применяются            │
│       полностью, либо откатываются целиком                      │
│                                                                 │
│   Consistency (Согласованность)                                 │
│   └── Foreign keys, constraints проверяются                     │
│       База не может оказаться в невалидном состоянии            │
│                                                                 │
│   Isolation (Изолированность)                                   │
│   └── Транзакции не видят незакоммиченные изменения             │
│       друг друга (SQLite: SERIALIZABLE по умолчанию)            │
│                                                                 │
│   Durability (Долговечность)                                    │
│   └── После COMMIT данные записаны на диск                      │
│       Выживают при crash приложения                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

```kotlin
// SQLDelight транзакция с ACID гарантиями
queries.transaction {
    queries.debitAccount(fromId, amount)   // -$100
    queries.creditAccount(toId, amount)    // +$100

    // Если упадёт здесь — обе операции откатятся
    if (amount > 10000) rollback()
}
// COMMIT — атомарно применены обе операции
```

### Schema Migration: теория эволюции схемы

База данных живёт долго — приложение обновляется, а данные пользователя должны сохраняться. **Schema migration** — это controlled evolution схемы:

```
┌─────────────────────────────────────────────────────────────────┐
│                    MIGRATION THEORY                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Version 1          Version 2          Version 3               │
│   ┌─────────┐       ┌─────────┐        ┌─────────┐             │
│   │ User    │  1.sqm│ User    │  2.sqm │ User    │             │
│   │ - id    │ ────→ │ - id    │ ────→  │ - id    │             │
│   │ - name  │       │ - name  │        │ - name  │             │
│   │         │       │ - email │        │ - email │             │
│   │         │       │         │        │ - avatar│             │
│   └─────────┘       └─────────┘        └─────────┘             │
│                                                                 │
│   Принципы:                                                     │
│   1. Миграции НИКОГДА не удаляются (history)                   │
│   2. Миграции НИКОГДА не изменяются (immutable)                │
│   3. Миграции применяются последовательно (v1→v2→v3)           │
│   4. .sq файл = ТЕКУЩАЯ схема (для новых установок)            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Важно:** .sqm файлы НЕ должны содержать `BEGIN/END TRANSACTION` — SQLDelight оборачивает каждую миграцию в транзакцию автоматически. Явные транзакции могут сломать некоторые драйверы.

### Code Generation: compile-time vs runtime

SQLDelight использует **compile-time code generation** (через KSP), а не runtime reflection:

| Подход | Примеры | Плюсы | Минусы |
|--------|---------|-------|--------|
| **Compile-time** | SQLDelight, kotlin-inject | Нет runtime overhead, ошибки при компиляции | Больше время сборки |
| **Runtime** | Gson reflection, Dagger (частично) | Простота | Performance cost, crash в runtime |

Compile-time генерация означает:
- Сгенерированный код такой же эффективный, как написанный вручную
- IDE видит все методы, autocomplete работает
- Минификация (R8/ProGuard) безопасна

---

## SQLDelight vs Room

### Сравнение подходов

| Критерий | SQLDelight | Room (KMP) |
|----------|------------|------------|
| **Подход** | SQL-first | DAO/Entity-first |
| **Язык запросов** | Пишешь SQL напрямую | Annotations + KAPT |
| **KMP поддержка** | Native с 2.x | С версии 2.7.0-alpha |
| **Compile-time safety** | ✅ Полная | ✅ Полная |
| **Coroutines/Flow** | ✅ Extension | ✅ Native |
| **LiveData** | ❌ (только Flow) | ✅ (только Android) |
| **Генерация кода** | KSP | KSP |
| **Миграции** | .sqm файлы | Migration classes |
| **Создатель** | Cash App (Block) | Google (Jetpack) |

### Когда выбирать

```
┌─────────────────────────────────────────────────────────────┐
│                   ВЫБОР БАЗЫ ДАННЫХ                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   SQLDelight выбирайте если:                                │
│   ✅ KMP проект с самого начала                             │
│   ✅ Комфортно писать SQL                                   │
│   ✅ Нужен полный контроль над запросами                    │
│   ✅ Хотите типобезопасность на уровне SQL                  │
│                                                             │
│   Room выбирайте если:                                      │
│   ✅ Существующий Android проект → KMP                      │
│   ✅ Уже используете Room                                   │
│   ✅ Предпочитаете Kotlin annotations                       │
│   ✅ Нужна интеграция с Jetpack (LiveData)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Настройка проекта

### Gradle конфигурация

```kotlin
// gradle/libs.versions.toml
[versions]
sqldelight = "2.2.1"

[libraries]
sqldelight-android = { module = "app.cash.sqldelight:android-driver", version.ref = "sqldelight" }
sqldelight-native = { module = "app.cash.sqldelight:native-driver", version.ref = "sqldelight" }
sqldelight-jvm = { module = "app.cash.sqldelight:sqlite-driver", version.ref = "sqldelight" }
sqldelight-js = { module = "app.cash.sqldelight:web-worker-driver", version.ref = "sqldelight" }
sqldelight-coroutines = { module = "app.cash.sqldelight:coroutines-extensions", version.ref = "sqldelight" }

[plugins]
sqldelight = { id = "app.cash.sqldelight", version.ref = "sqldelight" }
```

```kotlin
// shared/build.gradle.kts
plugins {
    alias(libs.plugins.kotlinMultiplatform)
    alias(libs.plugins.sqldelight)
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(libs.sqldelight.coroutines)
        }
        androidMain.dependencies {
            implementation(libs.sqldelight.android)
        }
        iosMain.dependencies {
            implementation(libs.sqldelight.native)
        }
        jvmMain.dependencies {
            implementation(libs.sqldelight.jvm)
        }
    }
}

sqldelight {
    databases {
        create("AppDatabase") {
            packageName.set("com.example.db")
            // Для миграций
            schemaOutputDirectory.set(file("src/commonMain/sqldelight/databases"))
            verifyMigrations.set(true)
        }
    }
}
```

### Структура файлов

```
shared/
├── src/
│   ├── commonMain/
│   │   ├── kotlin/
│   │   │   └── com/example/db/
│   │   │       └── DriverFactory.kt  # expect class
│   │   └── sqldelight/
│   │       └── com/example/db/       # Должен совпадать с packageName!
│   │           ├── User.sq
│   │           ├── Task.sq
│   │           └── migrations/
│   │               ├── 1.sqm
│   │               └── 2.sqm
│   ├── androidMain/
│   │   └── kotlin/
│   │       └── com/example/db/
│   │           └── DriverFactory.android.kt  # actual class
│   └── iosMain/
│       └── kotlin/
│           └── com/example/db/
│               └── DriverFactory.ios.kt      # actual class
```

---

## Создание схемы

### Определение таблиц (.sq файлы)

```sql
-- src/commonMain/sqldelight/com/example/db/User.sq

-- Создание таблицы (ВСЕГДА описывает АКТУАЛЬНУЮ схему)
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    avatar_url TEXT,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

-- Индексы
CREATE INDEX user_email_index ON User(email);

-- Именованные запросы (генерируются методы)
selectAll:
SELECT * FROM User ORDER BY created_at DESC;

selectById:
SELECT * FROM User WHERE id = ?;

selectByEmail:
SELECT * FROM User WHERE email = ?;

insert:
INSERT INTO User(email, name, avatar_url)
VALUES (?, ?, ?);

insertFull:
INSERT INTO User(email, name, avatar_url, created_at, updated_at)
VALUES ?;

update:
UPDATE User
SET name = ?, avatar_url = ?, updated_at = strftime('%s', 'now')
WHERE id = ?;

deleteById:
DELETE FROM User WHERE id = ?;

deleteAll:
DELETE FROM User;

count:
SELECT COUNT(*) FROM User;
```

```sql
-- src/commonMain/sqldelight/com/example/db/Task.sq

CREATE TABLE Task (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES User(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    is_completed INTEGER NOT NULL DEFAULT 0,
    priority INTEGER NOT NULL DEFAULT 0,
    due_date INTEGER,
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);

CREATE INDEX task_user_index ON Task(user_id);
CREATE INDEX task_completed_index ON Task(is_completed);

-- Все задачи пользователя
selectByUserId:
SELECT * FROM Task WHERE user_id = ? ORDER BY priority DESC, created_at DESC;

-- Незавершённые задачи
selectPending:
SELECT * FROM Task WHERE is_completed = 0 ORDER BY due_date ASC;

-- JOIN запрос
selectWithUser:
SELECT Task.*, User.name AS user_name, User.email AS user_email
FROM Task
INNER JOIN User ON Task.user_id = User.id
WHERE Task.id = ?;

insert:
INSERT INTO Task(user_id, title, description, priority, due_date)
VALUES (?, ?, ?, ?, ?);

toggleComplete:
UPDATE Task SET is_completed = NOT is_completed WHERE id = ?;

updatePriority:
UPDATE Task SET priority = ? WHERE id = ?;

deleteById:
DELETE FROM Task WHERE id = ?;

deleteCompleted:
DELETE FROM Task WHERE is_completed = 1;
```

---

## Platform-specific Drivers

### expect/actual pattern

```kotlin
// commonMain/kotlin/com/example/db/DriverFactory.kt
expect class DriverFactory {
    fun createDriver(): SqlDriver
}

fun createDatabase(driverFactory: DriverFactory): AppDatabase {
    return AppDatabase(driverFactory.createDriver())
}
```

```kotlin
// androidMain/kotlin/com/example/db/DriverFactory.android.kt
import android.content.Context
import app.cash.sqldelight.driver.android.AndroidSqliteDriver

actual class DriverFactory(private val context: Context) {
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
// iosMain/kotlin/com/example/db/DriverFactory.ios.kt
import app.cash.sqldelight.driver.native.NativeSqliteDriver

actual class DriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = AppDatabase.Schema,
            name = "app.db"
        )
    }
}
```

```kotlin
// jvmMain/kotlin/com/example/db/DriverFactory.jvm.kt
import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver

actual class DriverFactory {
    actual fun createDriver(): SqlDriver {
        val driver = JdbcSqliteDriver("jdbc:sqlite:app.db")
        AppDatabase.Schema.create(driver)
        return driver
    }
}
```

### iOS Xcode настройка

```
Build Settings → Other Linker Flags → добавить: -lsqlite3
```

---

## Использование запросов

### Базовые операции

```kotlin
// commonMain/kotlin/com/example/repository/UserRepository.kt
class UserRepository(database: AppDatabase) {

    private val queries = database.userQueries

    // SELECT ALL
    fun getAllUsers(): List<User> {
        return queries.selectAll().executeAsList()
    }

    // SELECT ONE
    fun getUserById(id: Long): User? {
        return queries.selectById(id).executeAsOneOrNull()
    }

    // INSERT
    fun insertUser(email: String, name: String, avatarUrl: String?): Long {
        queries.insert(email, name, avatarUrl)
        // Получить ID последней вставки
        return queries.selectByEmail(email).executeAsOne().id
    }

    // UPDATE
    fun updateUser(id: Long, name: String, avatarUrl: String?) {
        queries.update(name, avatarUrl, id)
    }

    // DELETE
    fun deleteUser(id: Long) {
        queries.deleteById(id)
    }

    // TRANSACTION
    fun insertMultipleUsers(users: List<UserData>) {
        queries.transaction {
            users.forEach { user ->
                queries.insert(user.email, user.name, user.avatarUrl)
            }
        }
    }

    // TRANSACTION с rollback
    fun insertWithRollback(users: List<UserData>) {
        queries.transaction {
            users.forEachIndexed { index, user ->
                if (index == 5) {
                    rollback()  // Откатить всю транзакцию
                }
                queries.insert(user.email, user.name, user.avatarUrl)
            }
        }
    }
}

data class UserData(
    val email: String,
    val name: String,
    val avatarUrl: String?
)
```

### Custom mapping

```kotlin
// Mapping в доменную модель
fun getUserDomain(id: Long): UserDomain? {
    return queries.selectById(id).executeAsOneOrNull()?.toDomain()
}

// Extension function
private fun User.toDomain(): UserDomain {
    return UserDomain(
        id = id,
        email = email,
        name = name,
        avatarUrl = avatar_url,
        createdAt = Instant.fromEpochSeconds(created_at)
    )
}

// Или с custom mapper в запросе
fun getUsersWithMapper(): List<UserDomain> {
    return queries.selectAll(
        mapper = { id, email, name, avatar_url, created_at, updated_at ->
            UserDomain(
                id = id,
                email = email,
                name = name,
                avatarUrl = avatar_url,
                createdAt = Instant.fromEpochSeconds(created_at)
            )
        }
    ).executeAsList()
}
```

---

## Reactive Queries с Flow

### Настройка

```kotlin
// Зависимость уже добавлена: sqldelight-coroutines
import app.cash.sqldelight.coroutines.asFlow
import app.cash.sqldelight.coroutines.mapToList
import app.cash.sqldelight.coroutines.mapToOne
import app.cash.sqldelight.coroutines.mapToOneOrNull
```

### Использование Flow

```kotlin
// commonMain/kotlin/com/example/repository/UserRepository.kt
class UserRepository(
    database: AppDatabase,
    private val dispatcher: CoroutineDispatcher = Dispatchers.IO
) {
    private val queries = database.userQueries

    // Flow<List<T>> — обновляется при любом изменении таблицы
    fun observeAllUsers(): Flow<List<User>> {
        return queries.selectAll()
            .asFlow()
            .mapToList(dispatcher)
    }

    // Flow<T?> — наблюдение за одной записью
    fun observeUserById(id: Long): Flow<User?> {
        return queries.selectById(id)
            .asFlow()
            .mapToOneOrNull(dispatcher)
    }

    // Flow<Int> — наблюдение за count
    fun observeUserCount(): Flow<Long> {
        return queries.count()
            .asFlow()
            .mapToOne(dispatcher)
    }

    // С custom mapping
    fun observeUsersDomain(): Flow<List<UserDomain>> {
        return queries.selectAll()
            .asFlow()
            .mapToList(dispatcher)
            .map { users -> users.map { it.toDomain() } }
    }
}
```

### Использование в ViewModel

```kotlin
class UserListViewModel(
    private val userRepository: UserRepository
) : ViewModel() {

    val users: StateFlow<List<User>> = userRepository
        .observeAllUsers()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    val userCount: StateFlow<Long> = userRepository
        .observeUserCount()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.Lazily,
            initialValue = 0
        )

    fun addUser(email: String, name: String) {
        viewModelScope.launch {
            userRepository.insertUser(email, name, null)
            // Flow автоматически получит обновление!
        }
    }
}
```

---

## Миграции

### Принцип версионирования

```
┌─────────────────────────────────────────────────────────────┐
│                   ВЕРСИОНИРОВАНИЕ                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Версия = количество .sqm файлов + 1                       │
│                                                             │
│   Файлы:           Версия БД:                               │
│   (нет файлов)  →  1                                        │
│   1.sqm         →  2                                        │
│   1.sqm, 2.sqm  →  3                                        │
│   1.sqm..5.sqm  →  6                                        │
│                                                             │
│   Имя файла: <версия_с_которой_мигрируем>.sqm               │
│   1.sqm = миграция С версии 1 НА версию 2                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Создание миграций

```sql
-- migrations/1.sqm (v1 → v2)
-- Добавляем колонку
ALTER TABLE User ADD COLUMN is_premium INTEGER NOT NULL DEFAULT 0;
```

```sql
-- migrations/2.sqm (v2 → v3)
-- Добавляем таблицу
CREATE TABLE Settings (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES User(id),
    theme TEXT NOT NULL DEFAULT 'light',
    notifications_enabled INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX settings_user_index ON Settings(user_id);
```

```sql
-- migrations/3.sqm (v3 → v4)
-- Создание индекса
CREATE INDEX user_premium_index ON User(is_premium);

-- Удаление колонки (SQLite workaround)
-- SQLite не поддерживает DROP COLUMN напрямую до версии 3.35.0
-- Создаём новую таблицу, копируем данные, удаляем старую
```

### Обновление .sq файла

**ВАЖНО:** После миграции обновите .sq файл, чтобы он отражал текущую схему:

```sql
-- User.sq (АКТУАЛЬНАЯ схема после миграции 1.sqm)
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    avatar_url TEXT,
    is_premium INTEGER NOT NULL DEFAULT 0,  -- Добавлено в миграции 1.sqm
    created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
    updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
);
```

### Проверка миграций

```bash
# Генерация схемы для верификации
./gradlew generateSqlDelightSchema

# Проверка миграций
./gradlew verifySqlDelightMigration
```

### Миграция при создании драйвера

```kotlin
// Android
actual class DriverFactory(private val context: Context) {
    actual fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(
            schema = AppDatabase.Schema,
            context = context,
            name = "app.db",
            callback = object : AndroidSqliteDriver.Callback(AppDatabase.Schema) {
                override fun onOpen(db: SupportSQLiteDatabase) {
                    // Выполняется при каждом открытии
                    db.setForeignKeyConstraintsEnabled(true)
                }
            }
        )
    }
}

// Native
actual class DriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = AppDatabase.Schema,
            name = "app.db",
            onConfiguration = { config ->
                config.copy(
                    extendedConfig = DatabaseConfiguration.Extended(foreignKeyConstraints = true)
                )
            }
        )
    }
}
```

---

## Тестирование

### In-memory база для тестов

```kotlin
// commonTest/kotlin/com/example/db/UserRepositoryTest.kt
class UserRepositoryTest {

    private lateinit var database: AppDatabase
    private lateinit var repository: UserRepository

    @BeforeTest
    fun setup() {
        // JVM: in-memory database
        val driver = JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY).also {
            AppDatabase.Schema.create(it)
        }
        database = AppDatabase(driver)
        repository = UserRepository(database)
    }

    @AfterTest
    fun tearDown() {
        // База уничтожается автоматически (in-memory)
    }

    @Test
    fun `insert and select user`() = runTest {
        // Arrange
        val email = "test@example.com"
        val name = "Test User"

        // Act
        val id = repository.insertUser(email, name, null)
        val user = repository.getUserById(id)

        // Assert
        assertNotNull(user)
        assertEquals(email, user.email)
        assertEquals(name, user.name)
    }

    @Test
    fun `observeAllUsers emits on insert`() = runTest {
        // Arrange
        val emissions = mutableListOf<List<User>>()
        val job = launch {
            repository.observeAllUsers().take(3).collect {
                emissions.add(it)
            }
        }

        // Act
        delay(100)  // Дождаться первой эмиссии
        repository.insertUser("user1@test.com", "User 1", null)
        delay(100)
        repository.insertUser("user2@test.com", "User 2", null)
        delay(100)

        job.cancel()

        // Assert
        assertEquals(3, emissions.size)
        assertEquals(0, emissions[0].size)  // Изначально пусто
        assertEquals(1, emissions[1].size)  // После первой вставки
        assertEquals(2, emissions[2].size)  // После второй вставки
    }

    @Test
    fun `transaction rolls back on error`() {
        // Arrange
        val users = listOf(
            UserData("user1@test.com", "User 1", null),
            UserData("user1@test.com", "Duplicate", null)  // Duplicate email
        )

        // Act & Assert
        assertFailsWith<Exception> {
            repository.insertMultipleUsers(users)
        }

        // Проверяем, что ничего не вставилось
        assertEquals(0, repository.getAllUsers().size)
    }
}
```

### iOS-specific тестирование

```kotlin
// iosTest
actual class TestDriverFactory {
    actual fun createDriver(): SqlDriver {
        return NativeSqliteDriver(
            schema = AppDatabase.Schema,
            name = "test.db",
            onConfiguration = { config ->
                config.copy(
                    inMemory = true  // In-memory для тестов
                )
            }
        )
    }
}
```

---

## Best Practices

### Checklist

| Практика | Описание |
|----------|----------|
| ✅ Маппинг в domain модели | Не используйте сгенерированные классы напрямую в UI |
| ✅ Repository pattern | Инкапсулируйте доступ к БД |
| ✅ Flow для наблюдения | Реактивные обновления без polling |
| ✅ Transactions | Групповые операции в транзакции |
| ✅ Индексы | CREATE INDEX для часто используемых WHERE |
| ✅ verifyMigrations | Включите проверку миграций в CI |
| ✅ Custom mapper | Используйте mapper parameter для оптимизации |
| ⚠️ Структура папок | sqldelight/ должна совпадать с packageName |
| ⚠️ .sq = актуальная схема | Обновляйте .sq после каждой миграции |

### Архитектура

```kotlin
// Рекомендуемая структура
//
// data/
//   ├── local/
//   │   ├── AppDatabase.kt          # Wrapper
//   │   ├── UserLocalDataSource.kt  # Queries wrapper
//   │   └── TaskLocalDataSource.kt
//   └── repository/
//       ├── UserRepository.kt       # Combines local + remote
//       └── TaskRepository.kt

class UserLocalDataSource(database: AppDatabase) {
    private val queries = database.userQueries

    fun getAll(): Flow<List<User>> = queries.selectAll().asFlow().mapToList(Dispatchers.IO)
    fun insert(email: String, name: String) = queries.insert(email, name, null)
    // ...
}

class UserRepository(
    private val local: UserLocalDataSource,
    private val remote: UserRemoteDataSource
) {
    fun getUsers(): Flow<List<UserDomain>> {
        return local.getAll().map { users -> users.map { it.toDomain() } }
    }

    suspend fun refresh() {
        val remoteUsers = remote.fetchUsers()
        local.insertAll(remoteUsers)
    }
}
```

---

## Миграция с Room

### Шаги миграции

1. **Экспорт схемы Room** → найти `*_Impl.java` с CREATE TABLE
2. **Создать .sq файлы** с той же схемой
3. **Создать миграции** .sqm для существующих данных
4. **Тестирование** на реальных данных

```kotlin
// Room Entity
@Entity
data class User(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val email: String,
    val name: String
)

// SQLDelight .sq
CREATE TABLE User (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    name TEXT NOT NULL
);
```

---

## Кто использует

| Компания | Применение | Результат |
|----------|------------|-----------|
| **Cash App** | Создатели SQLDelight | Основа приложения |
| **Bitkey (Block)** | Crypto wallet | KMP + SQLDelight |
| **Netflix** | Mobile apps | Shared persistence |
| **Worldline** | Fintech | Cross-platform data |

---

## Мифы и заблуждения

### Миф 1: "SQLDelight — это ORM"

**Реальность:** SQLDelight — это **NOT an ORM**. Это SQL-first code generator. Ключевое отличие:

| ORM | SQLDelight |
|-----|-----------|
| Генерирует SQL за вас | Вы пишете SQL, он генерирует Kotlin |
| Lazy loading, sessions | Нет магии, только ваши запросы |
| N+1 проблема возможна | N+1 невозможен (нет lazy relations) |

Если вам нужен ORM — смотрите Exposed или Room.

### Миф 2: "Нужно знать много SQL"

**Реальность:** Достаточно базовых знаний: `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `JOIN`, `WHERE`. SQLDelight IDE plugin подсвечивает ошибки и предлагает autocomplete для таблиц и колонок.

**Преимущество:** изучая SQLDelight, вы учите универсальный SQL, который работает везде.

### Миф 3: "Flow запросы дорогие — на каждое изменение перечитывают всю таблицу"

**Реальность:** Частично правда. SQLDelight `asFlow()` действительно перевыполняет запрос при **любом** изменении в отслеживаемых таблицах. Но:
- SQLite быстр для типичных запросов (< 1ms)
- Используйте индексы для WHERE clauses
- Для больших данных используйте пагинацию

**Оптимизация:** не подписывайтесь на `selectAll()` в таблицах с тысячами записей.

### Миф 4: "Миграции сложные"

**Реальность:** Миграции в SQLDelight проще чем в Room:
- Просто SQL файлы (1.sqm, 2.sqm, ...)
- Никаких Migration классов
- Автоматическая верификация с `verifyMigrations = true`

**Единственное правило:** не забывать обновлять .sq файл после миграции.

### Миф 5: "SQLDelight не поддерживает Room-like relations"

**Реальность:** SQLDelight не поддерживает *implicit* relations как Room @Relation. Но это **преимущество**:
- Вы пишете явный JOIN — контролируете производительность
- Нет "магии" — нет неожиданных N+1 запросов
- Результат JOIN можно замапить в nested data class

```sql
-- Явный JOIN вместо @Relation
selectTaskWithUser:
SELECT Task.*, User.name AS userName
FROM Task
JOIN User ON Task.userId = User.id;
```

### Миф 6: "package изменился — код сломается"

**Реальность:** В SQLDelight 2.0+ package действительно изменился с `com.squareup.sqldelight` на `app.cash.sqldelight`. Но миграция простая:
- Find & Replace в imports
- Обновить Gradle dependencies

**После миграции:** всё работает идентично.

---

## Рекомендуемые источники

| Источник | Тип | Описание |
|----------|-----|----------|
| [sqldelight.github.io](https://sqldelight.github.io/sqldelight/) | Official | Документация |
| [Cash App Case Study](https://blog.jetbrains.com/kotlin/2021/03/cash-app-case-study/) | Blog | История создания |
| [KMP + Ktor + SQLDelight](https://kotlinlang.org/docs/multiplatform/multiplatform-ktor-sqldelight.html) | Official | Tutorial |
| [Migrations Guide](https://sqldelight.github.io/sqldelight/2.0.2/multiplatform_sqlite/migrations/) | Official | Миграции |
| [Coroutines Extensions](https://sqldelight.github.io/sqldelight/2.0.2/android_sqlite/coroutines/) | Official | Flow support |

### CS-фундамент

| Концепция | Связь с SQLDelight | Где углубить |
|-----------|-------------------|--------------|
| [[relational-database-theory]] | Таблицы, отношения, нормализация | Stanford CS145 |
| [[acid-transactions]] | transaction {}, rollback() | Database Internals book |
| [[sql-query-optimization]] | Индексы, EXPLAIN QUERY PLAN | SQLite Query Planning |
| [[schema-migration-patterns]] | .sqm файлы, версионирование | Evolutionary Database Design |
| [[type-systems-theory]] | Compile-time SQL verification | Types and Programming Languages |

---

## Связь с другими темами

- **[[kmp-overview]]** — SQLDelight является основным решением для локального хранения данных в KMP-проектах. Понимание архитектуры KMP — source sets, expect/actual для platform-specific драйверов (AndroidSqliteDriver, NativeSqliteDriver, JdbcSqliteDriver) — необходимо для правильной настройки базы данных на каждой платформе. SQLDelight полностью вписывается в multiplatform-модель: SQL-схема в commonMain, драйверы через expect/actual.

- **[[kmp-ktor-networking]]** — SQLDelight и Ktor вместе формируют полный data layer в KMP: Ktor загружает данные с сервера, SQLDelight кэширует их локально. Repository pattern объединяет RemoteDataSource (Ktor) и LocalDataSource (SQLDelight), обеспечивая offline-first поведение. Flow-расширения SQLDelight позволяют реактивно обновлять UI при изменении кэшированных данных после сетевой синхронизации.

- **[[kmp-architecture-patterns]]** — SQLDelight диктует SQL-first подход к проектированию data layer, что влияет на всю архитектуру приложения. Сгенерированные классы не должны использоваться напрямую в domain/presentation слоях — необходимы mappers для преобразования в доменные модели. Repository pattern инкапсулирует доступ к базе, а Flow extensions обеспечивают реактивную связь между data и presentation слоями.

## Источники и дальнейшее чтение

### Теоретические основы

- **Codd E. F. (1970).** *A Relational Model of Data for Large Shared Data Banks.* — Реляционная модель, лежащая в основе SQL-first подхода SQLDelight.
- **Gamma E. et al. (1994).** *Design Patterns.* — Abstract Factory Pattern для платформенных SQL-драйверов (AndroidSqliteDriver, NativeSqliteDriver).

### Практические руководства

- **Jemerov D., Isakova S. (2017).** *Kotlin in Action.* — Kotlin для type-safe SQL-обёрток, генерируемых SQLDelight.
- **Moskala M. (2022).** *Kotlin Coroutines: Deep Dive.* — Flow для реактивных запросов в SQLDelight.
- [SQLDelight Documentation](https://cashapp.github.io/sqldelight/) — Официальная документация.

---

## Проверь себя

> [!question]- Почему SQLDelight предпочтительнее Room для KMP-проектов (до появления Room KMP)?
> SQLDelight изначально спроектирован как multiplatform: SQL-first подход, code generation из .sq файлов, поддержка всех KMP targets. Room был Android-only до версии 2.8. SQLDelight генерирует type-safe Kotlin API из SQL, Room -- из аннотаций.

> [!question]- Как SQLDelight обеспечивает type safety при работе с SQL-запросами?
> SQLDelight парсит .sq файлы с SQL-запросами при компиляции и генерирует Kotlin-интерфейсы с типизированными параметрами и результатами. Ошибки в SQL обнаруживаются при компиляции, а не в runtime.

> [!question]- Почему SqlDriver создаётся через expect/actual, а не в commonMain?
> SQLite драйвер платформо-специфичен: AndroidSqliteDriver на Android (использует Android SQLite), NativeSqliteDriver на iOS (статически линкованный SQLite), JdbcSqliteDriver на JVM. Каждый драйвер использует нативную реализацию SQLite своей платформы.

---

## Ключевые карточки

Как SQLDelight работает в KMP?
?
SQL-запросы пишутся в .sq файлах. Gradle plugin генерирует type-safe Kotlin API. Queries, schema, миграции -- в commonMain. SqlDriver -- через expect/actual для каждой платформы. Поддерживает Flow для реактивных запросов.

Что такое .sq файлы в SQLDelight?
?
Файлы с SQL-определениями (CREATE TABLE, SELECT, INSERT). SQLDelight compiler парсит их и генерирует Kotlin-интерфейсы с type-safe методами. Одна .sq файл = одна таблица с её запросами.

Как миграции работают в SQLDelight?
?
Через нумерованные .sqm файлы (1.sqm, 2.sqm). Каждый файл содержит ALTER TABLE и другие DDL-операции. SQLDelight автоматически применяет миграции при обновлении schema version.

Как получить реактивные обновления из SQLDelight?
?
Через .asFlow().mapToList() extension. SQLDelight отслеживает изменения таблиц и автоматически перевыполняет запросы при INSERT/UPDATE/DELETE. Flow размещается в commonMain и работает на всех платформах.

Как тестировать SQLDelight в KMP?
?
Через in-memory database: JdbcSqliteDriver(IN_MEMORY) в commonTest или jvmTest. Создаётся schema, выполняются запросы, проверяются результаты. Не нужен реальный файл базы данных.

---

## Куда дальше

| Направление | Куда | Зачем |
|-------------|------|-------|
| Следующий шаг | [[kmp-third-party-libs]] | Обзор экосистемы KMP-библиотек |
| Углубиться | [[kmp-integration-testing]] | Тестирование SQLDelight с in-memory DB |
| Смежная тема | [[kmp-ktor-networking]] | Сетевой слой, данные которого сохраняются в SQLDelight |
| Обзор | [[kmp-overview]] | Вернуться к навигации по разделу |

---

*Проверено: 2026-01-09 | SQLDelight 2.2.1, Kotlin 2.1.21*
