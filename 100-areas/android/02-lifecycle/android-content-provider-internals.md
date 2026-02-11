---
title: "ContentProvider Internals: межпроцессный доступ к данным"
created: 2026-01-27
modified: 2026-01-28
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/data
  - type/deep-dive
  - level/expert
related:
  - "[[android-overview]]"
  - "[[android-app-components]]"
  - "[[android-data-persistence]]"
  - "[[android-permissions-security]]"
  - "[[android-intent-internals]]"
  - "[[android-context-internals]]"
  - "[[android-app-startup-performance]]"
  - "[[android-handler-looper]]"
  - "[[android-process-memory]]"
cs-foundations: [ipc, uri-scheme, crud, observer-pattern, proxy-pattern, facade-pattern, shared-memory, binder-ipc]
prerequisites:
  - "[[android-app-components]]"
  - "[[android-data-persistence]]"
  - "[[android-permissions-security]]"
  - "[[android-process-memory]]"
---

# ContentProvider Internals: межпроцессный доступ к данным

> ContentProvider — один из четырёх фундаментальных компонентов Android, обеспечивающий структурированный доступ к данным через Binder IPC. Это стандартный интерфейс для обмена данными между приложениями: контакты, медиафайлы, настройки — всё работает через ContentProvider. Но у него есть неожиданная вторая жизнь: библиотеки используют его как хук для ранней инициализации. А под капотом — CursorWindow с shared memory, Binder thread pool, и сложный lifecycle, привязанный к процессу.

---

## Зачем это нужно

### Проблемы без понимания ContentProvider

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| Нужно получить контакты/медиа из другого приложения | Прямой доступ к БД невозможен cross-process | Нужен стандартный IPC-интерфейс |
| FileUriExposedException при шаринге файлов | file:// URI запрещены с Android 7.0 | Crash при шаринге файлов |
| Медленный cold start (~20-50ms overhead) | 10+ ContentProvider при старте | Каждый CP стоит ~2-5ms |
| Crash при отсутствии данных | ContentProvider не инициализирован | Race condition при раннем доступе |
| TransactionTooLargeException | CursorWindow > 1MB или слишком много данных | Crash при большой выборке |
| SecurityException | Нет permission или exported=false | Нет доступа к данным другого приложения |
| Утечка Cursor | Cursor не закрыт после использования | Memory leak, finalize() warning |
| StaleDataException | CursorWindow recycled | Crash при доступе к закрытому Cursor |
| Медленные batch операции | Отдельный Binder call на каждую операцию | N insert = N IPC calls |

### Актуальность (2025-2026)

```
Эволюция ContentProvider:
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  API 1:       ContentProvider, ContentResolver — основа IPC данных    │
│  API 3:       ContentObserver — reactive data                        │
│  API 5:       ContentProviderClient — persistent connection          │
│  API 11:      CursorLoader — async loading (deprecated now)         │
│  API 19:      DocumentsProvider — Storage Access Framework           │
│  API 24 (7):  FileProvider обязателен (FileUriExposedException)      │
│  API 26 (8):  ContentProvider.requireContext()                       │
│  API 29 (10): Scoped Storage, MediaStore изменения                   │
│  API 30 (11): Package visibility, MANAGE_EXTERNAL_STORAGE           │
│  API 31 (12): Exact alarm permission, export requirement             │
│  API 33 (13): Photo picker, per-app language                         │
│  API 34 (14): Content URI permission changes                         │
│  API 35 (15): Partial media permissions                              │
│                                                                      │
│  2025+: ContentProvider остаётся ЕДИНСТВЕННЫМ                        │
│         стандартным IPC для structured data                          │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

- ContentProvider — единственный стандартный IPC для structured data (контакты, медиа, календарь)
- FileProvider — единственный безопасный способ шаринга файлов между приложениями
- App Startup library заменяет CP как хук инициализации (уменьшает cold start)
- Scoped Storage (Android 10+) изменил доступ к MediaStore
- Photo Picker (Android 13+) — альтернатива MediaStore для выбора изображений
- DocumentsProvider (SAF) — для документов и файлов вне sandbox

---

## Prerequisites

| Тема | Зачем нужна | Где изучить |
|------|-------------|-------------|
| Binder IPC | ContentProvider работает через Binder cross-process | [[android-handler-looper]] |
| Android Components | CP — один из 4 фундаментальных компонентов | [[android-app-components]] |
| Permissions | ContentProvider защищён read/write permissions | [[android-permissions-security]] |
| Intent и URI | URI-based addressing; Intent для шаринга через FileProvider | [[android-intent-internals]] |
| Context | ContentResolver через context.contentResolver | [[android-context-internals]] |
| Data Persistence | Room как backend; DataStore для settings | [[android-data-persistence]] |
| App Startup | CP как хук инициализации; App Startup library | [[android-app-startup-performance]] |

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **ContentProvider** | Компонент, предоставляющий данные через IPC | Библиотекарь — выдаёт книги по запросу |
| **ContentResolver** | Клиент для доступа к ContentProvider | Читатель — запрашивает книги |
| **ContentValues** | Набор key-value для insert/update | Карточка с данными для записи |
| **Cursor** | Итератор по результатам query | Палец, скользящий по строкам таблицы |
| **CursorWindow** | Shared memory buffer для данных Cursor | Лоток с книгами — передаётся через окно |
| **UriMatcher** | Маршрутизатор URI → код операции | Библиотечный каталог — по шифру к полке |
| **authority** | Уникальный идентификатор ContentProvider | Имя библиотеки |
| **content:// URI** | Адрес данных в ContentProvider | Шифр книги в каталоге |
| **FileProvider** | Безопасный шаринг файлов через content:// | Ксерокс — копия вместо оригинала |
| **ContentObserver** | Наблюдатель за изменениями данных | Подписка на обновления каталога |
| **ContentProviderClient** | Persistent connection к CP (без overhead) | Абонемент в библиотеке |
| **ContentProviderOperation** | Batch операция (atomic insert/update/delete) | Пакет запросов на выдачу |
| **DocumentsProvider** | CP для файлов (Storage Access Framework) | Файловый менеджер |
| **IContentProvider** | Binder interface для IPC | Телефонная линия к библиотекарю |
| **Transport** | Внутренний Binder stub в ContentProvider | Секретарь на линии |
| **App Startup Initializer** | Замена CP для инициализации библиотек | Автоматическая подготовка зала |

---

## Архитектура ContentProvider

### Общая схема

```
┌─────────────────────────────────────────────────────────────────────┐
│                     CONTENTPROVIDER ARCHITECTURE                    │
│                                                                     │
│  Client App (Process A)              Provider App (Process B)       │
│  ┌───────────────────────┐          ┌───────────────────────────┐   │
│  │                       │          │                           │   │
│  │  ContentResolver      │          │  ContentProvider           │   │
│  │   ├── query()         │          │   ├── query()             │   │
│  │   ├── insert()        │          │   ├── insert()            │   │
│  │   ├── update()        │          │   ├── update()            │   │
│  │   ├── delete()        │          │   ├── delete()            │   │
│  │   └── call()          │          │   ├── getType()           │   │
│  │       │               │          │   ├── openFile()          │   │
│  │       │               │          │   └── call()              │   │
│  │       ▼               │          │       ▲                   │   │
│  │  acquireProvider()    │          │       │                   │   │
│  │       │               │          │  Transport (Binder stub)  │   │
│  │       ▼               │          │   = IContentProvider.Stub │   │
│  │  IContentProvider     │  Binder  │       ▲                   │   │
│  │  (proxy)              │══════════│       │                   │   │
│  │       │               │   IPC    │       │                   │   │
│  │       ▼               │          │  ┌────────────────────┐   │   │
│  │  CursorWindow         │  shared  │  │ SQLite / Room      │   │   │
│  │  (shared memory)     │◄════════►│  │ Files / Network    │   │   │
│  │                       │  memory  │  │ In-memory data     │   │   │
│  │                       │          │  └────────────────────┘   │   │
│  └───────────────────────┘          └───────────────────────────┘   │
│                                                                     │
│                    system_server (AMS)                               │
│                    ┌─────────────────┐                               │
│                    │ ProviderMap     │                               │
│                    │ (authority →    │                               │
│                    │  ProviderInfo)  │                               │
│                    │                 │                               │
│                    │ Resolves        │                               │
│                    │ authority to    │                               │
│                    │ target process  │                               │
│                    └─────────────────┘                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### URI формат

```
content://com.example.app.provider/users/42
│         │                        │     │
│         authority                path   id
│
scheme (всегда content://)

Разбор URI:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Scheme:    content://                                       │
│  → Всегда "content" для ContentProvider                      │
│  → Указывает ContentResolver на Binder dispatch              │
│                                                              │
│  Authority: com.example.app.provider                         │
│  → Уникальный идентификатор ContentProvider                  │
│  → AMS использует для resolve → target process               │
│  → По конвенции: package name + ".provider"                  │
│                                                              │
│  Path:      /users                                           │
│  → Определяет тип данных (таблица, коллекция)                │
│  → UriMatcher маршрутизирует path → операцию                 │
│                                                              │
│  ID:        /42                                              │
│  → Конкретная запись (optional)                               │
│  → ContentUris.parseId(uri) → 42L                            │
│                                                              │
│  Query params: ?limit=10&offset=20                           │
│  → Дополнительные параметры (optional)                       │
│  → uri.getQueryParameter("limit")                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘

Примеры системных URI:
┌────────────────────────────────────────────────────────────┐
│  content://contacts/people              — контакты         │
│  content://com.android.contacts/contacts — новый URI       │
│  content://media/external/images/media  — изображения      │
│  content://media/external/video/media   — видео            │
│  content://settings/system              — системные        │
│  content://sms/inbox                    — SMS входящие     │
│  content://call_log/calls               — журнал звонков   │
│  content://calendar/events              — события          │
│  content://downloads/my_downloads       — загрузки         │
│  content://user_dictionary/words        — словарь          │
└────────────────────────────────────────────────────────────┘
```

### Lifecycle ContentProvider

```
ContentProvider Lifecycle в процессе:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Process Start (Zygote fork)                                     │
│       │                                                          │
│       ▼                                                          │
│  ActivityThread.main()                                           │
│       │                                                          │
│       ▼                                                          │
│  ActivityThread.handleBindApplication()                          │
│       │                                                          │
│       ├── 1. Create Application object                           │
│       │       app = mInstrumentation.newApplication(...)          │
│       │                                                          │
│       ├── 2. installContentProviders()  ← ВСЕ CP ДО onCreate!   │
│       │       │                                                  │
│       │       ├── for each ProviderInfo:                          │
│       │       │     cp = instantiateProvider(classLoader, info)   │
│       │       │     cp.attachInfo(context, info)                  │
│       │       │         → ContentProvider.onCreate()  ← ВЫЗОВ    │
│       │       │                                                  │
│       │       └── AMS.publishContentProviders()                  │
│       │             → Регистрация в system_server                │
│       │             → Другие процессы могут обращаться            │
│       │                                                          │
│       ├── 3. Application.onCreate()     ← ПОСЛЕ всех CP         │
│       │                                                          │
│       └── 4. Process ready                                       │
│                                                                  │
│  ВАЖНО:                                                          │
│  • CP.onCreate() вызывается на MAIN THREAD                       │
│  • Тяжёлая работа в onCreate() → медленный cold start            │
│  • CP.onCreate() вызывается ДО Application.onCreate()            │
│  • Если CP зависит от Application init → crash/NPE              │
│                                                                  │
│  ContentProvider ЖИВЁТ пока ЖИВЁТ процесс:                      │
│  • Нет onDestroy() или onStop()                                  │
│  • Убить CP = убить процесс                                      │
│  • CP не пересоздаётся при configuration changes                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## ContentResolver — клиентская сторона

### Под капотом: как работает запрос

```
ContentResolver.query(uri) — что происходит:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  1. ContentResolver.query(uri, projection, selection, ...)       │
│       │                                                          │
│       ▼                                                          │
│  2. acquireProvider(uri)                                         │
│       │                                                          │
│       ├── Проверить кэш: mProviderMap.get(authority)             │
│       │     → Если есть → использовать cached IContentProvider   │
│       │                                                          │
│       ├── Если нет в кэше:                                       │
│       │     AMS.getContentProvider(callingPkg, authority)         │
│       │       │                                                  │
│       │       ├── Resolve authority → ProviderInfo               │
│       │       ├── Проверить permissions                           │
│       │       ├── Если provider process не запущен:               │
│       │       │     → startProcessLocked()  ← запуск процесса!  │
│       │       │     → ждать ContentProvider.onCreate()           │
│       │       └── Вернуть IContentProvider Binder                │
│       │                                                          │
│       ▼                                                          │
│  3. provider.query(uri, projection, selection, args, sortOrder)  │
│       │                                                          │
│       ├── Binder IPC → target process                            │
│       ├── ContentProvider.Transport.query()                      │
│       ├── ContentProvider.query() ← ваш код                     │
│       └── Return Cursor (с CursorWindow)                        │
│                                                                  │
│  4. CursorWindow передаётся через shared memory                 │
│       │                                                          │
│       └── Client получает Cursor с данными                       │
│           (без копирования — shared memory!)                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### CRUD операции

```kotlin
// Получение ContentResolver (через Context)
val resolver: ContentResolver = context.contentResolver

// ═══ QUERY — выборка данных ═══
val cursor: Cursor? = resolver.query(
    ContactsContract.Contacts.CONTENT_URI,  // URI — какие данные
    arrayOf(                                 // projection — какие столбцы
        ContactsContract.Contacts._ID,
        ContactsContract.Contacts.DISPLAY_NAME,
        ContactsContract.Contacts.PHOTO_URI
    ),
    "${ContactsContract.Contacts.HAS_PHONE_NUMBER} = ?", // selection (WHERE)
    arrayOf("1"),                            // selectionArgs (параметры WHERE)
    "${ContactsContract.Contacts.DISPLAY_NAME} ASC" // sortOrder
)

// Обработка результата — ВСЕГДА закрывайте Cursor!
cursor?.use { c ->
    val idIdx = c.getColumnIndexOrThrow(ContactsContract.Contacts._ID)
    val nameIdx = c.getColumnIndexOrThrow(ContactsContract.Contacts.DISPLAY_NAME)
    val photoIdx = c.getColumnIndexOrThrow(ContactsContract.Contacts.PHOTO_URI)

    while (c.moveToNext()) {
        val id = c.getLong(idIdx)
        val name = c.getString(nameIdx)
        val photoUri = c.getString(photoIdx)
        // обработка строки
    }
} // cursor автоматически закрывается благодаря use {}
```

```kotlin
// ═══ INSERT — вставка данных ═══
val values = ContentValues().apply {
    put("name", "John Doe")
    put("email", "john@example.com")
    put("age", 30)
}
val insertedUri: Uri? = resolver.insert(MyProvider.CONTENT_URI, values)
// insertedUri = content://com.example.provider/users/42

// Получить ID вставленной записи
val id: Long = ContentUris.parseId(insertedUri!!) // 42


// ═══ UPDATE — обновление ═══
val updatedCount: Int = resolver.update(
    ContentUris.withAppendedId(MyProvider.CONTENT_URI, 42), // URI с ID
    ContentValues().apply {
        put("name", "Jane Doe")
        put("email", "jane@example.com")
    },
    null,  // selection (уже указано в URI)
    null   // selectionArgs
)


// ═══ DELETE — удаление ═══
val deletedCount: Int = resolver.delete(
    ContentUris.withAppendedId(MyProvider.CONTENT_URI, 42),
    null, null
)

// Удаление с condition
val deletedInactive: Int = resolver.delete(
    MyProvider.CONTENT_URI,
    "active = ? AND lastLogin < ?",
    arrayOf("0", "2024-01-01")
)
```

### ContentProviderClient — persistent connection

```kotlin
// Проблема: каждый вызов ContentResolver = acquireProvider + release
// Для batch операций — значительный overhead

// Решение: ContentProviderClient
val client: ContentProviderClient? =
    resolver.acquireContentProviderClient(MyProvider.CONTENT_URI)

client?.use { c ->  // AutoCloseable — закрывается автоматически
    // Множество операций через один connection
    val cursor1 = c.query(uri1, projection, null, null, null)
    val cursor2 = c.query(uri2, projection, null, null, null)
    c.insert(uri3, values)
    c.update(uri4, values, null, null)
    // Все через один Binder connection — без overhead
}

// Unstable client — для ненадёжных провайдеров
// При crash провайдера: DeadObjectException вместо kill ВАШЕГО процесса
val unstableClient: ContentProviderClient? =
    resolver.acquireUnstableContentProviderClient(MyProvider.CONTENT_URI)

// ВАЖНО: Разница stable vs unstable
// Stable:   при crash провайдера → ваш процесс тоже убивается
// Unstable: при crash провайдера → DeadObjectException (ваш процесс жив)
```

### Batch операции — ContentProviderOperation

```kotlin
// Проблема: 100 insert = 100 Binder IPC calls
// Решение: batch операции = 1 Binder IPC call

val operations = ArrayList<ContentProviderOperation>()

// Batch insert — все операции в одном IPC call
for (contact in contacts) {
    operations.add(
        ContentProviderOperation.newInsert(ContactsContract.RawContacts.CONTENT_URI)
            .withValue(ContactsContract.RawContacts.ACCOUNT_TYPE, accountType)
            .withValue(ContactsContract.RawContacts.ACCOUNT_NAME, accountName)
            .build()
    )

    // Можно ссылаться на результат предыдущей операции!
    operations.add(
        ContentProviderOperation.newInsert(ContactsContract.Data.CONTENT_URI)
            .withValueBackReference(
                ContactsContract.Data.RAW_CONTACT_ID,
                operations.size - 2  // index предыдущей операции
            )
            .withValue(
                ContactsContract.Data.MIMETYPE,
                ContactsContract.CommonDataKinds.StructuredName.CONTENT_ITEM_TYPE
            )
            .withValue(
                ContactsContract.CommonDataKinds.StructuredName.DISPLAY_NAME,
                contact.name
            )
            .build()
    )
}

// Выполнить все операции атомарно
try {
    val results: Array<ContentProviderResult> =
        resolver.applyBatch(ContactsContract.AUTHORITY, operations)
    // results[i].uri или results[i].count
} catch (e: OperationApplicationException) {
    Log.e("Batch", "Failed", e)
} catch (e: RemoteException) {
    Log.e("Batch", "Provider crash", e)
}
```

```
Batch vs Individual Operations:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Individual: 100 inserts                                     │
│  Client ──→ Binder ──→ Provider (insert #1)                 │
│  Client ──→ Binder ──→ Provider (insert #2)                 │
│  ...                                                         │
│  Client ──→ Binder ──→ Provider (insert #100)               │
│  = 100 IPC calls = ~100-500ms                                │
│                                                              │
│  Batch: 100 inserts in 1 call                                │
│  Client ──→ Binder ──→ Provider (batch of 100)              │
│  = 1 IPC call + atomic = ~10-50ms                            │
│                                                              │
│  Speedup: 5-20x                                              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## CursorWindow — shared memory для данных

### Как Cursor передаёт данные cross-process

```
CursorWindow: shared memory mechanism
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Provider Process                    Client Process              │
│  ┌──────────────┐                   ┌──────────────┐             │
│  │              │                   │              │             │
│  │  SQLiteCursor│                   │  Cursor      │             │
│  │       │      │                   │  (proxy)     │             │
│  │       ▼      │                   │       │      │             │
│  │  CursorWindow│ ═══ shared ═══   │  CursorWindow│             │
│  │  (native     │    memory        │  (mapped to  │             │
│  │   memory)    │    (ashmem /     │   same phys  │             │
│  │              │    memfd)        │   memory)    │             │
│  │  ┌──────────┐│                   │              │             │
│  │  │ Row 0    ││                   │              │             │
│  │  │ Row 1    ││  Данные НЕ       │              │             │
│  │  │ Row 2    ││  копируются!     │              │             │
│  │  │ ...      ││  Одна физическая │              │             │
│  │  │ Row N    ││  память.         │              │             │
│  │  └──────────┘│                   │              │             │
│  │              │                   │              │             │
│  │  DEFAULT     │                   │              │             │
│  │  SIZE: 2MB   │                   │              │             │
│  │              │                   │              │             │
│  └──────────────┘                   └──────────────┘             │
│                                                                  │
│  ФОРМАТ CursorWindow в памяти:                                   │
│  ┌────────┬────────┬────────┬────────┬─────────────────────┐    │
│  │ Header │ Row    │ Row    │ ...    │ Free space          │    │
│  │ (size, │ Slot 0 │ Slot 1 │        │                     │    │
│  │  rows, │ (offset│ (offset│        │                     │    │
│  │  cols) │  array)│  array)│        │                     │    │
│  └────────┴────────┴────────┴────────┴─────────────────────┘    │
│                                                                  │
│  Каждый Row Slot содержит:                                       │
│  ┌─────────┬──────────┬──────────┬──────────┐                   │
│  │ Col 0   │ Col 1    │ Col 2    │ Col 3    │                   │
│  │ (type+  │ (type+   │ (type+   │ (type+   │                   │
│  │  offset)│  offset) │  offset) │  offset) │                   │
│  └─────────┴──────────┴──────────┴──────────┘                   │
│                                                                  │
│  Types: NULL=0, INT=1, FLOAT=2, STRING=3, BLOB=4               │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### TransactionTooLargeException и CursorWindow overflow

```kotlin
// Проблема: CursorWindow default size = 2MB
// Если данные не влезают:

// ❌ Запрос возвращает слишком много данных
val cursor = resolver.query(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    null, // ВСЕ столбцы (включая BLOB!)
    null, null, null
)
// → CursorWindowAllocationException или TransactionTooLargeException

// ✅ Запрашивайте только нужные столбцы
val cursor = resolver.query(
    MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
    arrayOf(           // Только нужные столбцы!
        MediaStore.Images.Media._ID,
        MediaStore.Images.Media.DISPLAY_NAME,
        MediaStore.Images.Media.SIZE
    ),
    null, null,
    "${MediaStore.Images.Media.DATE_ADDED} DESC"
)

// ✅ Используйте LIMIT
val uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI.buildUpon()
    .appendQueryParameter("limit", "100")
    .build()

// ✅ Пагинация через offset
val uri = MediaStore.Images.Media.EXTERNAL_CONTENT_URI.buildUpon()
    .appendQueryParameter("limit", "50")
    .appendQueryParameter("offset", "100")
    .build()
```

```
CursorWindow Filling Process:
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  SQLiteCursor.fillWindow():                                 │
│                                                             │
│  1. Создать/очистить CursorWindow (2MB default)            │
│  2. Для каждой строки результата:                           │
│     a. Попробовать добавить строку в window                │
│     b. Если не влезает:                                    │
│        → Для SQLiteCursor: просто остановить filling       │
│           (остальные строки — при следующем moveToPosition) │
│        → Для CrossProcessCursor: fill новый window         │
│                                                             │
│  ПРОБЛЕМА: Если ОДНА строка > 2MB (например, BLOB):       │
│  → CursorWindowAllocationException                         │
│  → Решение: передавайте файлы через FileProvider/URI       │
│                                                             │
│  Window refill при scrolling:                               │
│  ┌────────────────────────────────────┐                     │
│  │ Window: rows 0-99                  │                     │
│  │ Cursor at: row 50 ✓                │                     │
│  │ moveToPosition(150) → rows 100-199 │ ← refill          │
│  │ moveToPosition(50) → rows 0-99     │ ← refill again    │
│  └────────────────────────────────────┘                     │
│                                                             │
│  СОВЕТ: Итерируйте Cursor последовательно (forward only)   │
│  для минимума refills                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Реализация ContentProvider

### 6 обязательных методов

```kotlin
class UserProvider : ContentProvider() {

    private lateinit var db: UserDatabase

    // ═══ onCreate() — инициализация ═══
    // Вызывается ДО Application.onCreate()!
    // На MAIN THREAD — должен быть быстрым
    override fun onCreate(): Boolean {
        // ВАЖНО: context доступен ТОЛЬКО после attachInfo()
        // context!! безопасен здесь
        db = Room.databaseBuilder(
            context!!.applicationContext,
            UserDatabase::class.java,
            "users.db"
        ).build()
        return true // true = инициализация успешна
    }

    // ═══ query() — выборка данных ═══
    // Вызывается из BINDER THREAD POOL (не main thread!)
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        val cursor = when (uriMatcher.match(uri)) {
            USERS -> {
                db.userDao().getAllCursor()
            }
            USER_ID -> {
                val id = ContentUris.parseId(uri)
                db.userDao().getByIdCursor(id)
            }
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }

        // Уведомлять наблюдателей при изменении данных
        cursor?.setNotificationUri(context?.contentResolver, uri)
        return cursor
    }

    // ═══ insert() — вставка ═══
    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        require(uriMatcher.match(uri) == USERS) {
            "Insert supported only for /users, got: $uri"
        }
        requireNotNull(values) { "ContentValues must not be null" }

        val id = db.userDao().insert(values.toUser())
        val insertedUri = ContentUris.withAppendedId(CONTENT_URI, id)

        // Уведомить наблюдателей
        context?.contentResolver?.notifyChange(insertedUri, null)
        return insertedUri
    }

    // ═══ update() — обновление ═══
    override fun update(
        uri: Uri,
        values: ContentValues?,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int {
        requireNotNull(values) { "ContentValues must not be null" }

        val count = when (uriMatcher.match(uri)) {
            USERS -> db.userDao().updateAll(values, selection, selectionArgs)
            USER_ID -> {
                val id = ContentUris.parseId(uri)
                db.userDao().updateById(id, values)
            }
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }

        if (count > 0) {
            context?.contentResolver?.notifyChange(uri, null)
        }
        return count
    }

    // ═══ delete() — удаление ═══
    override fun delete(
        uri: Uri,
        selection: String?,
        selectionArgs: Array<String>?
    ): Int {
        val count = when (uriMatcher.match(uri)) {
            USERS -> db.userDao().deleteAll(selection, selectionArgs)
            USER_ID -> {
                val id = ContentUris.parseId(uri)
                db.userDao().deleteById(id)
            }
            else -> throw IllegalArgumentException("Unknown URI: $uri")
        }

        if (count > 0) {
            context?.contentResolver?.notifyChange(uri, null)
        }
        return count
    }

    // ═══ getType() — MIME type ═══
    override fun getType(uri: Uri): String = when (uriMatcher.match(uri)) {
        USERS -> "vnd.android.cursor.dir/vnd.example.user"   // коллекция
        USER_ID -> "vnd.android.cursor.item/vnd.example.user" // один элемент
        else -> throw IllegalArgumentException("Unknown URI: $uri")
    }

    // ═══ call() — произвольные операции (Android 11+) ═══
    override fun call(method: String, arg: String?, extras: Bundle?): Bundle? {
        return when (method) {
            "getUserCount" -> Bundle().apply {
                putInt("count", db.userDao().getCount())
            }
            "clearCache" -> {
                db.userDao().clearCache()
                Bundle.EMPTY
            }
            else -> super.call(method, arg, extras)
        }
    }

    companion object {
        const val AUTHORITY = "com.example.app.provider"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/users")

        private const val USERS = 100
        private const val USER_ID = 101

        private val uriMatcher = UriMatcher(UriMatcher.NO_MATCH).apply {
            addURI(AUTHORITY, "users", USERS)
            addURI(AUTHORITY, "users/#", USER_ID)
        }
    }
}
```

### Manifest declaration

```xml
<!-- AndroidManifest.xml -->

<!-- Объявление custom permissions -->
<permission
    android:name="com.example.app.READ_USERS"
    android:protectionLevel="signature" />
<permission
    android:name="com.example.app.WRITE_USERS"
    android:protectionLevel="signature" />

<!-- ContentProvider registration -->
<provider
    android:name=".UserProvider"
    android:authorities="com.example.app.provider"
    android:exported="true"
    android:readPermission="com.example.app.READ_USERS"
    android:writePermission="com.example.app.WRITE_USERS"
    android:multiprocess="false"
    android:syncable="false">

    <!-- Granular permissions per path -->
    <path-permission
        android:pathPrefix="/users/public"
        android:readPermission="android.permission.INTERNET" />

    <!-- Grant URI permissions dynamically -->
    <grant-uri-permission android:pathPattern="/users/.*" />
</provider>
```

### Threading модель ContentProvider

```
ContentProvider Threading:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  onCreate():                                                     │
│  → MAIN THREAD (единожды при создании process)                   │
│  → Должен быть быстрым (блокирует app startup)                  │
│                                                                  │
│  query/insert/update/delete/call/openFile:                       │
│  → BINDER THREAD POOL (concurrent!)                              │
│  → Несколько клиентов могут вызывать одновременно                │
│  → НУЖНА thread safety!                                          │
│                                                                  │
│  Binder Thread Pool:                                             │
│  ┌────────────────────────────────────────────────┐              │
│  │ Thread 1: query() от App A                     │              │
│  │ Thread 2: insert() от App B                    │              │
│  │ Thread 3: query() от App A (другой вызов)      │              │
│  │ Thread 4: update() от App C                    │              │
│  │ ...                                            │              │
│  │ Max threads: 16 (default Binder thread pool)   │              │
│  └────────────────────────────────────────────────┘              │
│                                                                  │
│  Thread Safety Solutions:                                        │
│                                                                  │
│  1. Room + WAL (Write-Ahead Logging):                           │
│     → Concurrent reads ✅                                        │
│     → Single writer (serialized writes) ✅                       │
│     → Рекомендованный подход                                     │
│                                                                  │
│  2. synchronized blocks:                                         │
│     → Простой, но serializes ALL operations                      │
│     → Bottleneck при высокой нагрузке                            │
│                                                                  │
│  3. ReadWriteLock:                                               │
│     → Concurrent reads + exclusive writes                        │
│     → Хорошо для read-heavy workloads                            │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

```kotlin
// Thread-safe ContentProvider с ReadWriteLock
class ThreadSafeProvider : ContentProvider() {

    private val lock = ReentrantReadWriteLock()

    override fun query(uri: Uri, ...): Cursor? {
        lock.readLock().lock()
        try {
            // Concurrent reads allowed
            return db.query(...)
        } finally {
            lock.readLock().unlock()
        }
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        lock.writeLock().lock()
        try {
            // Exclusive write
            return db.insert(...)
        } finally {
            lock.writeLock().unlock()
        }
    }
}
```

---

## UriMatcher — маршрутизация запросов

### Алгоритм и паттерны

```kotlin
val uriMatcher = UriMatcher(UriMatcher.NO_MATCH).apply {
    // Порядок ВАЖЕН: specific ПЕРЕД wildcards!

    // Коллекции (dir)
    addURI(AUTHORITY, "users", USERS)              // /users
    addURI(AUTHORITY, "users/active", USERS_ACTIVE) // /users/active (ПЕРЕД #)
    addURI(AUTHORITY, "users/#", USER_BY_ID)       // /users/42 (# = число)
    addURI(AUTHORITY, "users/*", USER_BY_NAME)     // /users/john (* = строка)

    // Связанные данные
    addURI(AUTHORITY, "users/#/posts", USER_POSTS)      // /users/42/posts
    addURI(AUTHORITY, "users/#/posts/#", USER_POST)     // /users/42/posts/7

    // Другие таблицы
    addURI(AUTHORITY, "categories", CATEGORIES)
    addURI(AUTHORITY, "categories/#", CATEGORY_BY_ID)
}
```

```
UriMatcher Internal Tree:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Root (NO_MATCH)                                             │
│   └── "users"                                                │
│        ├── [match: USERS=100]                                │
│        ├── "active"                                          │
│        │    └── [match: USERS_ACTIVE=102]                    │
│        ├── # (number wildcard)                               │
│        │    ├── [match: USER_BY_ID=101]                      │
│        │    └── "posts"                                      │
│        │         ├── [match: USER_POSTS=103]                 │
│        │         └── # (number wildcard)                     │
│        │              └── [match: USER_POST=104]             │
│        └── * (string wildcard)                               │
│             └── [match: USER_BY_NAME=105]                    │
│                                                              │
│  Matching algorithm: depth-first tree traversal              │
│  Specific paths checked BEFORE wildcards                     │
│  "users/active" matches USERS_ACTIVE, not USER_BY_NAME      │
│                                                              │
│  ВАЖНО: # matches only digits, * matches any string         │
│  "users/abc" → USER_BY_NAME (*)                              │
│  "users/123" → USER_BY_ID (#) — numbers prefer # over *     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## FileProvider — безопасный шаринг файлов

### Проблема: file:// URI

```
До Android 7.0 (API 24):
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  val uri = Uri.fromFile(file)                                │
│  // → file:///data/data/com.myapp/files/secret.pdf           │
│                                                              │
│  ПРОБЛЕМЫ:                                                   │
│  1. Раскрывает структуру файловой системы                    │
│  2. Получающее приложение имеет прямой доступ к файлу        │
│  3. SELinux может заблокировать доступ cross-app             │
│  4. Нет контроля прав (read-only vs read-write)              │
│  5. Нет revocation — права нельзя отозвать                   │
│                                                              │
│  Android 7.0: FileUriExposedException                        │
│  → file:// URI запрещены в Intent для другого приложения     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Настройка FileProvider

```xml
<!-- AndroidManifest.xml -->
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

```xml
<!-- res/xml/file_paths.xml -->
<paths xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- Context.getFilesDir() / "images" -->
    <files-path name="internal_images" path="images/" />

    <!-- Context.getCacheDir() / "temp" -->
    <cache-path name="cache_files" path="temp/" />

    <!-- Context.getExternalFilesDir(null) / "photos" -->
    <external-files-path name="external_photos" path="photos/" />

    <!-- Context.getExternalCacheDir() -->
    <external-cache-path name="external_cache" path="." />

    <!-- Environment.getExternalStorageDirectory() (AVOID!) -->
    <!-- <external-path name="external" path="." /> -->

    <!-- ⚠️ НИКОГДА: открывает ВСЮ файловую систему! -->
    <!-- <root-path name="root" path="/" /> -->

</paths>
```

```
Path Mapping:

file_paths.xml entry           Actual path
─────────────────────────────────────────────────────────────
<files-path path="images/">    /data/data/com.app/files/images/
<cache-path path="temp/">      /data/data/com.app/cache/temp/
<external-files-path>          /sdcard/Android/data/com.app/files/
<external-cache-path>          /sdcard/Android/data/com.app/cache/

Генерируемый URI:
file:    /data/data/com.app/files/images/photo.jpg
       ↓ FileProvider.getUriForFile()
content: content://com.app.fileprovider/internal_images/photo.jpg
         ^scheme   ^authority           ^name         ^filename
```

### Использование FileProvider

```kotlin
// ═══ Шаринг файла ═══
fun shareFile(context: Context, file: File) {
    val uri = FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        file
    )
    // uri = content://com.example.app.fileprovider/internal_images/photo.jpg

    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "image/jpeg"
        putExtra(Intent.EXTRA_STREAM, uri)
        // Временное разрешение на чтение
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(Intent.createChooser(intent, "Поделиться"))
}

// ═══ Открытие файла во внешнем приложении ═══
fun openFile(context: Context, file: File, mimeType: String) {
    val uri = FileProvider.getUriForFile(
        context,
        "${context.packageName}.fileprovider",
        file
    )

    val intent = Intent(Intent.ACTION_VIEW).apply {
        setDataAndType(uri, mimeType)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }

    if (intent.resolveActivity(context.packageManager) != null) {
        context.startActivity(intent)
    }
}

// ═══ Камера → FileProvider ═══
fun takePicture(activity: Activity) {
    val photoFile = File.createTempFile(
        "photo_${System.currentTimeMillis()}_",
        ".jpg",
        activity.getExternalFilesDir(Environment.DIRECTORY_PICTURES)
    )

    val photoUri = FileProvider.getUriForFile(
        activity,
        "${activity.packageName}.fileprovider",
        photoFile
    )

    val intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
        putExtra(MediaStore.EXTRA_OUTPUT, photoUri)
        // Важно: Grant permission для camera app
        addFlags(Intent.FLAG_GRANT_WRITE_URI_PERMISSION)
    }
    activity.startActivityForResult(intent, REQUEST_TAKE_PHOTO)
}
```

### URI Grant Permissions

```kotlin
// Как работают temporary URI permissions
context.grantUriPermission(
    "com.target.app",           // Package получателя
    contentUri,                  // URI
    Intent.FLAG_GRANT_READ_URI_PERMISSION  // Права
)

// Отозвать разрешение
context.revokeUriPermission(
    contentUri,
    Intent.FLAG_GRANT_READ_URI_PERMISSION
)

// Через Intent (автоматически при startActivity)
val intent = Intent().apply {
    data = contentUri
    addFlags(
        Intent.FLAG_GRANT_READ_URI_PERMISSION or
        Intent.FLAG_GRANT_WRITE_URI_PERMISSION or
        Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION // Сохранить после reboot
    )
}
```

```
URI Permission Lifecycle:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  FLAG_GRANT_READ_URI_PERMISSION (через Intent):              │
│  → Действует пока Activity receiver жива                    │
│  → Автоматически revoked при finish()                       │
│                                                              │
│  grantUriPermission():                                       │
│  → Действует до revokeUriPermission()                       │
│  → Или до перезагрузки устройства                            │
│                                                              │
│  FLAG_GRANT_PERSISTABLE_URI_PERMISSION:                      │
│  → Переживает reboot                                        │
│  → Нужно takePersistableUriPermission() на стороне receiver │
│  → Используется в Storage Access Framework                   │
│                                                              │
│  contentResolver.takePersistableUriPermission(               │
│      uri,                                                    │
│      Intent.FLAG_GRANT_READ_URI_PERMISSION                   │
│  )                                                           │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## ContentProvider как хук инициализации

### Проблема: cascading ContentProviders

```
Cold Start Timeline с библиотеками:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Zygote fork                                                     │
│       │                                                          │
│       ▼                                                          │
│  ActivityThread.handleBindApplication()                          │
│       │                                                          │
│       ▼                                                          │
│  installContentProviders() ← БЛОКИРУЕТ MAIN THREAD              │
│       │                                                          │
│       ├── WorkManagerInitializer     : ~3ms                      │
│       ├── LifecycleDispatcher        : ~2ms                      │
│       ├── FirebaseInitProvider       : ~5ms                      │
│       ├── FacebookInitProvider       : ~4ms                      │
│       ├── CrashlyticInitProvider     : ~3ms                      │
│       ├── LeakCanaryInstaller        : ~2ms (debug)              │
│       ├── AnalyticsInitProvider      : ~3ms                      │
│       ├── CoilInitializer            : ~2ms                      │
│       ├── PushNotificationProvider   : ~3ms                      │
│       └── MyAppInitProvider          : ~2ms                      │
│       ────────────────────────────────────                       │
│       ИТОГО: ~29ms ДО Application.onCreate()                     │
│                                                                  │
│       ▼                                                          │
│  Application.onCreate()                                          │
│       │                                                          │
│       ▼                                                          │
│  First Activity.onCreate()                                       │
│                                                                  │
│  Каждый ContentProvider = 1 class load + 1 instantiation +       │
│  1 attachInfo() + 1 onCreate() = ~2-5ms overhead                 │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### App Startup Library — решение

```kotlin
// ОДИН ContentProvider (InitializationProvider) вместо N

// 1. Определяем Initializer
class AnalyticsInitializer : Initializer<Analytics> {
    override fun create(context: Context): Analytics {
        return Analytics.init(context, BuildConfig.ANALYTICS_KEY)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        // Зависимости: инициализируются ПЕРВЫМИ
        return listOf(CrashReportingInitializer::class.java)
    }
}

class CrashReportingInitializer : Initializer<CrashReporting> {
    override fun create(context: Context): CrashReporting {
        return CrashReporting.init(context)
    }

    override fun dependencies(): List<Class<out Initializer<*>>> {
        return emptyList() // Нет зависимостей
    }
}

// 2. Регистрация в Manifest
// ОДИН InitializationProvider вместо N отдельных
```

```xml
<!-- AndroidManifest.xml -->
<provider
    android:name="androidx.startup.InitializationProvider"
    android:authorities="${applicationId}.androidx-startup"
    android:exported="false"
    tools:node="merge">

    <!-- Eager initialization (при старте) -->
    <meta-data
        android:name="com.example.AnalyticsInitializer"
        android:value="androidx.startup" />

    <!-- Отключить CP библиотеки (заменяем на App Startup) -->
    <meta-data
        android:name="com.library.OldInitProvider"
        tools:node="remove" />
</provider>

<!-- Полностью удалить CP библиотеки -->
<provider
    android:name="com.firebase.FirebaseInitProvider"
    tools:node="remove" />
```

```kotlin
// 3. Lazy initialization (по требованию)
val analytics = AppInitializer.getInstance(context)
    .initializeComponent(AnalyticsInitializer::class.java)
// Инициализируется при первом вызове, не при старте
```

```
App Startup Dependency Graph:
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  InitializationProvider.onCreate()                           │
│       │                                                      │
│       ▼                                                      │
│  AppInitializer.discoverAndInitialize()                      │
│       │                                                      │
│       ▼                                                      │
│  Topological sort по зависимостям:                           │
│                                                              │
│  CrashReportingInitializer (нет зависимостей)               │
│       │                                                      │
│       ▼                                                      │
│  AnalyticsInitializer (зависит от CrashReporting)           │
│       │                                                      │
│       ▼                                                      │
│  NetworkInitializer (зависит от Analytics + Crash)           │
│                                                              │
│  Результат: 1 CP вместо N → экономия (N-1) * ~3ms          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### 4 стратегии инициализации

| Стратегия | Когда | Как | Пример |
|-----------|-------|-----|--------|
| **Eager + Fast** | Нужно сразу, быстро (<5ms) | App Startup eager | Crash reporting, logging |
| **Eager + Slow** | Нужно сразу, медленно (>5ms) | Background thread в Application.onCreate() | Database migration, network setup |
| **Lazy + Fast** | Не сразу, быстро | App Startup lazy | Image loader, analytics |
| **Lazy + Slow** | Не сразу, медленно | Первое использование + coroutine | ML model loading, large cache |

---

## ContentObserver — наблюдение за изменениями

### Как это работает

```
ContentObserver Pipeline:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Provider Process                    Observer Process             │
│  ┌──────────────────┐              ┌──────────────────┐          │
│  │                  │              │                  │          │
│  │  insert()/update()│             │  ContentObserver │          │
│  │       │          │              │  onChange()      │          │
│  │       ▼          │              │       ▲          │          │
│  │  notifyChange()  │              │       │          │          │
│  │       │          │              │       │          │          │
│  └───────┼──────────┘              └───────┼──────────┘          │
│          │                                 │                     │
│          ▼                                 │                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │  system_server (ContentService)                            │  │
│  │                                                            │  │
│  │  ObserverNode tree (trie по URI path)                      │  │
│  │  ┌──────────────────────────────────────┐                  │  │
│  │  │ content://authority                   │                  │  │
│  │  │   └── /users                         │                  │  │
│  │  │        ├── Observer 1 (notifyForDescendants=true)       │  │
│  │  │        └── /42                       │                  │  │
│  │  │             └── Observer 2           │                  │  │
│  │  └──────────────────────────────────────┘                  │  │
│  │                                                            │  │
│  │  notifyChange(content://authority/users/42):               │  │
│  │    → Match observers для /users/42 → Observer 2 ✓         │  │
│  │    → Match ancestors с notifyForDescendants:               │  │
│  │      → /users (Observer 1, descendants=true) ✓            │  │
│  │    → Dispatch onChange() через Binder IPC                  │  │
│  │                                                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

```kotlin
// Регистрация ContentObserver
class ContactsViewModel(
    private val app: Application
) : AndroidViewModel(app) {

    private val _contacts = MutableStateFlow<List<Contact>>(emptyList())
    val contacts: StateFlow<List<Contact>> = _contacts.asStateFlow()

    private val contactsObserver = object : ContentObserver(
        Handler(Looper.getMainLooper())
    ) {
        override fun onChange(selfChange: Boolean) {
            onChange(selfChange, null)
        }

        override fun onChange(selfChange: Boolean, uri: Uri?) {
            // selfChange = true если мы сами вызвали notifyChange
            // uri = конкретный URI изменения (или null)
            viewModelScope.launch {
                loadContacts()
            }
        }

        override fun onChange(
            selfChange: Boolean,
            uri: Uri?,
            flags: Int // Android 11+ (API 30)
        ) {
            // flags: NOTIFY_INSERT, NOTIFY_UPDATE, NOTIFY_DELETE
            viewModelScope.launch {
                when {
                    flags and ContentResolver.NOTIFY_INSERT != 0 -> handleInsert(uri)
                    flags and ContentResolver.NOTIFY_UPDATE != 0 -> handleUpdate(uri)
                    flags and ContentResolver.NOTIFY_DELETE != 0 -> handleDelete(uri)
                    else -> loadContacts() // полная перезагрузка
                }
            }
        }
    }

    init {
        // Регистрация — наблюдать за ВСЕМИ изменениями контактов
        app.contentResolver.registerContentObserver(
            ContactsContract.Contacts.CONTENT_URI,
            true, // notifyForDescendants = true → наблюдать за дочерними URI
            contactsObserver
        )
        viewModelScope.launch { loadContacts() }
    }

    override fun onCleared() {
        super.onCleared()
        // ОБЯЗАТЕЛЬНО отписаться!
        app.contentResolver.unregisterContentObserver(contactsObserver)
    }

    private suspend fun loadContacts() = withContext(Dispatchers.IO) {
        // load contacts from ContentResolver...
    }
}
```

### ContentObserver → Flow adapter

```kotlin
// Обёртка ContentObserver в Flow
fun ContentResolver.observeUri(
    uri: Uri,
    notifyForDescendants: Boolean = true
): Flow<Uri?> = callbackFlow {
    val observer = object : ContentObserver(Handler(Looper.getMainLooper())) {
        override fun onChange(selfChange: Boolean, uri: Uri?) {
            trySend(uri)
        }
    }

    registerContentObserver(uri, notifyForDescendants, observer)
    // Отправить начальное значение
    trySend(null)

    awaitClose {
        unregisterContentObserver(observer)
    }
}

// Использование
viewModelScope.launch {
    contentResolver.observeUri(ContactsContract.Contacts.CONTENT_URI)
        .debounce(300) // Не реагировать на быстрые серии изменений
        .collect { uri ->
            loadContacts()
        }
}
```

---

## Системные ContentProviders

### Полный каталог

| Provider | Authority | URI | Permission | Описание |
|----------|-----------|-----|------------|----------|
| **Contacts** | com.android.contacts | content://com.android.contacts/contacts | READ_CONTACTS | Контакты |
| **MediaStore** | media | content://media/external/images/media | READ_MEDIA_IMAGES (13+) | Медиафайлы |
| **Calendar** | com.android.calendar | content://com.android.calendar/events | READ_CALENDAR | Календарь |
| **Settings** | settings | content://settings/system | Varies | Системные настройки |
| **CallLog** | call_log | content://call_log/calls | READ_CALL_LOG | Журнал звонков |
| **SMS** | sms | content://sms/inbox | READ_SMS | SMS сообщения |
| **Downloads** | downloads | content://downloads/my_downloads | None (own) | Загрузки |
| **UserDictionary** | user_dictionary | content://user_dictionary/words | READ_USER_DICTIONARY | Словарь |
| **Browser** | browser | content://browser/bookmarks | Deprecated | Закладки |
| **VoicemailContract** | voicemail | content://voicemail/voicemail | ADD_VOICEMAIL | Голосовая почта |

### MediaStore — работа с медиафайлами

```kotlin
// Запрос изображений (Android 13+ с granular permissions)
@RequiresPermission(Manifest.permission.READ_MEDIA_IMAGES)
suspend fun loadImages(context: Context): List<MediaItem> = withContext(Dispatchers.IO) {
    val images = mutableListOf<MediaItem>()

    val projection = arrayOf(
        MediaStore.Images.Media._ID,
        MediaStore.Images.Media.DISPLAY_NAME,
        MediaStore.Images.Media.SIZE,
        MediaStore.Images.Media.DATE_ADDED,
        MediaStore.Images.Media.WIDTH,
        MediaStore.Images.Media.HEIGHT,
        MediaStore.Images.Media.MIME_TYPE
    )

    val selection = "${MediaStore.Images.Media.SIZE} > ?"
    val selectionArgs = arrayOf("0") // Исключить пустые файлы

    val sortOrder = "${MediaStore.Images.Media.DATE_ADDED} DESC"

    context.contentResolver.query(
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        projection,
        selection,
        selectionArgs,
        sortOrder
    )?.use { cursor ->
        val idCol = cursor.getColumnIndexOrThrow(MediaStore.Images.Media._ID)
        val nameCol = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DISPLAY_NAME)
        val sizeCol = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.SIZE)

        while (cursor.moveToNext()) {
            val id = cursor.getLong(idCol)
            val contentUri = ContentUris.withAppendedId(
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI, id
            )
            images.add(
                MediaItem(
                    id = id,
                    uri = contentUri,
                    name = cursor.getString(nameCol),
                    size = cursor.getLong(sizeCol)
                )
            )
        }
    }

    images
}

// Сохранение изображения через MediaStore (Scoped Storage)
suspend fun saveImage(
    context: Context,
    bitmap: Bitmap,
    displayName: String
): Uri? = withContext(Dispatchers.IO) {
    val values = ContentValues().apply {
        put(MediaStore.Images.Media.DISPLAY_NAME, displayName)
        put(MediaStore.Images.Media.MIME_TYPE, "image/jpeg")
        // Android 10+: указать relative path
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            put(MediaStore.Images.Media.RELATIVE_PATH, "Pictures/MyApp")
            put(MediaStore.Images.Media.IS_PENDING, 1) // Скрыть пока пишем
        }
    }

    val uri = context.contentResolver.insert(
        MediaStore.Images.Media.EXTERNAL_CONTENT_URI,
        values
    ) ?: return@withContext null

    context.contentResolver.openOutputStream(uri)?.use { stream ->
        bitmap.compress(Bitmap.CompressFormat.JPEG, 90, stream)
    }

    // Показать файл после записи
    if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
        val updateValues = ContentValues().apply {
            put(MediaStore.Images.Media.IS_PENDING, 0)
        }
        context.contentResolver.update(uri, updateValues, null, null)
    }

    uri
}
```

---

## DocumentsProvider — Storage Access Framework

```kotlin
// Открыть документ через SAF
val openDocumentLauncher = registerForActivityResult(
    ActivityResultContracts.OpenDocument()
) { uri: Uri? ->
    uri?.let { documentUri ->
        // Persistent permission
        contentResolver.takePersistableUriPermission(
            documentUri,
            Intent.FLAG_GRANT_READ_URI_PERMISSION
        )

        // Читать документ
        contentResolver.openInputStream(documentUri)?.use { stream ->
            val content = stream.bufferedReader().readText()
            processDocument(content)
        }
    }
}

// Вызов
openDocumentLauncher.launch(arrayOf(
    "application/pdf",
    "text/plain",
    "application/vnd.openxmlformats-officedocument.*"
))

// Создать документ через SAF
val createDocumentLauncher = registerForActivityResult(
    ActivityResultContracts.CreateDocument("text/plain")
) { uri: Uri? ->
    uri?.let { documentUri ->
        contentResolver.openOutputStream(documentUri)?.use { stream ->
            stream.write("Hello, World!".toByteArray())
        }
    }
}

createDocumentLauncher.launch("my_document.txt")
```

---

## Безопасность ContentProvider

### Permission модели

```
ContentProvider Permission Model:
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  Level 1: exported="false"                                       │
│  → Только своё приложение имеет доступ                           │
│  → Используйте для internal-only providers                      │
│                                                                  │
│  Level 2: readPermission / writePermission                       │
│  → Раздельные permissions для чтения и записи                    │
│  → Объявление: <permission protectionLevel="signature|normal">  │
│                                                                  │
│  Level 3: path-permission                                        │
│  → Разные permissions для разных paths                           │
│  → <path-permission pathPrefix="/public" readPermission="...">  │
│                                                                  │
│  Level 4: URI grants (temporary)                                 │
│  → FLAG_GRANT_READ_URI_PERMISSION через Intent                  │
│  → grantUriPermission() для programmatic grant                   │
│  → Временный доступ без declared permission                      │
│                                                                  │
│  Level 5: ContentProvider.getCallingPackage()                    │
│  → Проверка identity вызывающего пакета                          │
│  → Для custom authorization logic                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

```kotlin
// Безопасный ContentProvider с проверкой caller
class SecureProvider : ContentProvider() {

    override fun query(uri: Uri, ...): Cursor? {
        // Проверить caller
        val callingPackage = callingPackage
        if (callingPackage != null && !isAuthorized(callingPackage)) {
            throw SecurityException("Unauthorized access from $callingPackage")
        }

        // Дополнительная проверка permission
        val permission = context?.checkCallingPermission(
            "com.example.READ_DATA"
        )
        if (permission != PackageManager.PERMISSION_GRANTED) {
            throw SecurityException("Missing READ_DATA permission")
        }

        return performQuery(uri)
    }

    private fun isAuthorized(packageName: String): Boolean {
        // Проверить signing certificate
        val mySignature = getMySignature()
        val callerSignature = getSignature(packageName)
        return mySignature == callerSignature
    }
}
```

### SQL Injection Prevention

```kotlin
// ❌ УЯЗВИМО: SQL injection через selection
override fun query(uri: Uri, projection: Array<String>?,
                   selection: String?, selectionArgs: Array<String>?,
                   sortOrder: String?): Cursor? {
    // selection = "name = 'John'; DROP TABLE users; --"
    return db.rawQuery("SELECT * FROM users WHERE $selection", null)
    // → SQL injection!
}

// ✅ БЕЗОПАСНО: parametrized queries
override fun query(uri: Uri, projection: Array<String>?,
                   selection: String?, selectionArgs: Array<String>?,
                   sortOrder: String?): Cursor? {
    val qb = SQLiteQueryBuilder().apply {
        tables = "users"

        // Ограничить projection (whitelist)
        projectionMap = mapOf(
            "_id" to "_id",
            "name" to "name",
            "email" to "email"
        )

        // Ограничить sortOrder
        if (sortOrder != null && sortOrder !in ALLOWED_SORT_ORDERS) {
            throw IllegalArgumentException("Invalid sort order: $sortOrder")
        }
    }

    // Parametrized query — безопасно
    return qb.query(
        db.readableDatabase,
        projection,
        selection,       // WHERE clause с ? placeholders
        selectionArgs,   // Значения для ? (escaped автоматически)
        null, null,
        sortOrder
    )
}
```

---

## ContentProvider vs Room vs DataStore

| Аспект | ContentProvider | Room | DataStore |
|--------|----------------|------|-----------|
| **Scope** | Cross-process IPC | In-process только | In-process только |
| **API** | URI + Cursor (low-level) | Type-safe DAO + Entity | Preferences / Proto |
| **Threading** | Binder pool (concurrent) | Coroutines/Flow | Coroutines |
| **Type safety** | Нет (runtime errors) | Да (compile-time) | Да |
| **Reactive** | ContentObserver (manual) | Flow/LiveData (automatic) | Flow |
| **Schema** | Нет enforce (arbitrary) | Entity + migration | Proto schema / KV |
| **Performance** | IPC overhead (~1-5ms) | Direct (~0.1ms) | Direct (~0.1ms) |
| **Когда** | IPC, system data access | Local DB (structured) | Settings, preferences |
| **Complexity** | Высокая (6 methods + URI) | Низкая (annotation-based) | Низкая (KV pairs) |

```kotlin
// Современный паттерн: Room backend + ContentProvider фасад
// Room для internal использования, CP для external IPC

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAll(): Flow<List<User>>

    @Query("SELECT * FROM users")
    fun getAllCursor(): Cursor // Для ContentProvider

    @Insert
    suspend fun insert(user: User): Long

    @Query("SELECT * FROM users WHERE _id = :id")
    fun getByIdCursor(id: Long): Cursor // Для ContentProvider
}

class UserProvider : ContentProvider() {
    override fun query(uri: Uri, ...): Cursor? {
        return when (uriMatcher.match(uri)) {
            USERS -> db.userDao().getAllCursor()
            USER_ID -> db.userDao().getByIdCursor(ContentUris.parseId(uri))
            else -> null
        }
    }
}
```

---

## Распространённые паттерны

### Pattern 1: ContentProvider + ViewModel + Flow

```kotlin
@HiltViewModel
class MediaViewModel @Inject constructor(
    private val app: Application
) : AndroidViewModel(app) {

    private val _mediaItems = MutableStateFlow<List<MediaItem>>(emptyList())
    val mediaItems: StateFlow<List<MediaItem>> = _mediaItems.asStateFlow()

    init {
        // Наблюдать за изменениями MediaStore
        viewModelScope.launch {
            app.contentResolver.observeUri(
                MediaStore.Images.Media.EXTERNAL_CONTENT_URI
            ).collect {
                loadMedia()
            }
        }
    }

    private suspend fun loadMedia() {
        _mediaItems.value = withContext(Dispatchers.IO) {
            // query MediaStore...
            queryMediaStore(app.contentResolver)
        }
    }
}
```

### Pattern 2: Custom ContentProvider с Room

```kotlin
// Полная реализация: Room + ContentProvider + Hilt
@HiltViewModel
class NotesProvider : ContentProvider() {

    // Lazy Room database
    private val db: NotesDatabase by lazy {
        Room.databaseBuilder(
            context!!.applicationContext,
            NotesDatabase::class.java,
            "notes.db"
        ).build()
    }

    override fun onCreate(): Boolean = true // Lazy init — быстрый onCreate

    override fun query(uri: Uri, projection: Array<String>?,
                       selection: String?, selectionArgs: Array<String>?,
                       sortOrder: String?): Cursor? {
        val cursor = when (uriMatcher.match(uri)) {
            NOTES -> db.noteDao().selectAllCursor()
            NOTE_BY_ID -> db.noteDao().selectByIdCursor(ContentUris.parseId(uri))
            else -> null
        }
        cursor?.setNotificationUri(context?.contentResolver, uri)
        return cursor
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        val note = values?.toNote() ?: return null
        val id = db.noteDao().insertBlocking(note)
        val resultUri = ContentUris.withAppendedId(CONTENT_URI, id)
        context?.contentResolver?.notifyChange(resultUri, null)
        return resultUri
    }

    // ... update, delete, getType
}
```

---

## Мифы и заблуждения

| # | Миф | Реальность |
|---|-----|-----------|
| 1 | "ContentProvider нужен для доступа к базе данных" | Только для **cross-process** доступа. In-process — используйте Room напрямую |
| 2 | "ContentProvider работает в main thread" | onCreate() — на main thread, но query/insert/update/delete — из **Binder thread pool** (concurrent!) |
| 3 | "Room полностью заменяет ContentProvider" | Разные цели: Room — in-process typed DB, CP — IPC стандарт |
| 4 | "FileProvider — просто ContentProvider" | Специальная реализация с path mapping, temporary permissions и security sandboxing |
| 5 | "CP инициализируется по запросу" | ВСЕ CP инициализируются **при старте приложения** (до Application.onCreate) — даже если никто не запрашивает |
| 6 | "UriMatcher находит best match" | **First match wins** — порядок addURI() определяет приоритет |
| 7 | "CursorLoader — актуальный подход" | Deprecated. Замена: ViewModel + Flow + ContentObserver |
| 8 | "ContentProvider безопасен по умолчанию" | Exported=true по умолчанию (до targetSdk 31)! Нужны: permissions, exported=false, URI grants |
| 9 | "Cursor копирует данные через Binder" | Нет — CursorWindow использует **shared memory** (ashmem/memfd). Данные НЕ копируются |
| 10 | "ContentProvider медленный" | IPC overhead ~1-5ms, но CursorWindow через shared memory = zero-copy для данных |
| 11 | "Можно хранить большие BLOB в ContentProvider" | CursorWindow limit = 2MB. Большие файлы → FileProvider или openFile() |
| 12 | "ContentObserver гарантирует точный URI изменения" | Провайдер решает, какой URI передать в notifyChange(). Часто передаётся parent URI |

---

## CS-фундамент

| Концепция | Как используется в ContentProvider | Пример в Android |
|-----------|-------------------------------------|-------------------|
| **IPC (Inter-Process Communication)** | Binder для cross-process CRUD | ContentResolver → Binder → ContentProvider |
| **URI Scheme** | content://authority/path/id для адресации данных | content://contacts/people/42 |
| **CRUD** | Стандартные операции: query/insert/update/delete | ContentResolver.query(), insert(), update(), delete() |
| **Observer Pattern** | ContentObserver для уведомлений об изменениях | notifyChange() → onChange() |
| **Proxy Pattern** | ContentResolver — прокси к реальному CP через Binder | Скрывает IPC детали от клиента |
| **Facade Pattern** | CP скрывает SQLite/Files/Network за единым API | query() может обращаться к любому хранилищу |
| **Shared Memory** | CursorWindow через ashmem/memfd для zero-copy | Cursor данные доступны без копирования cross-process |
| **Dependency Injection** | CP как container для initialization (App Startup) | Initializer dependencies graph |

---

## Проверь себя

### Вопрос 1
**Q:** В каком потоке выполняются методы ContentProvider? Почему это важно?

<details>
<summary>Ответ</summary>

`onCreate()` — на **main thread** (блокирует app startup). Все остальные методы (query/insert/update/delete/call/openFile) — из **Binder thread pool** (concurrent, до 16 потоков).

Это важно:
1. Нужна **thread safety** (concurrent access от разных клиентов на разных потоках)
2. `onCreate()` должен быть быстрым (блокирует cold start)
3. Можно безопасно выполнять тяжёлые DB операции в query/insert (не main thread)
4. Room с WAL обеспечивает concurrent reads + serialized writes
</details>

### Вопрос 2
**Q:** Почему ContentProvider.onCreate() вызывается ДО Application.onCreate()?

<details>
<summary>Ответ</summary>

Это дизайн ActivityThread: при инициализации процесса вызывается `handleBindApplication()`, который:
1. Создаёт Application object
2. `installContentProviders()` — создаёт и инициализирует ВСЕ CP
3. `Application.onCreate()` — только потом

Это сделано чтобы ContentProvider были доступны другим приложениям как можно раньше (до того, как app начнёт обрабатывать свою логику). Побочный эффект: библиотеки используют CP для ранней инициализации (Firebase, WorkManager), что замедляет cold start. App Startup library решает эту проблему через одиночный CP + dependency graph.
</details>

### Вопрос 3
**Q:** Почему нельзя использовать `<root-path>` в FileProvider?

<details>
<summary>Ответ</summary>

`<root-path path="/">` открывает доступ к **всей файловой системе** устройства. Злоумышленник может:
1. Манипулировать path в content:// URI (path traversal: `../../../`)
2. Получить доступ к `/data/data/другие_приложения/`
3. Прочитать `/system/`, `/proc/`, `/dev/`
4. Украсть credentials, БД, shared preferences других приложений

Правильно: использовать конкретные paths (`files-path`, `cache-path`, `external-files-path`), которые ограничивают доступ sandbox'ом приложения.
</details>

### Вопрос 4
**Q:** Как CursorWindow передаёт данные cross-process без копирования?

<details>
<summary>Ответ</summary>

CursorWindow использует **shared memory** (ashmem на старых версиях, memfd на новых):
1. Provider создаёт CursorWindow — аллокация в native memory (default 2MB)
2. CursorWindow заполняется данными (строки в row slots)
3. File descriptor shared memory передаётся через Binder (fd passing)
4. Client получает fd и делает mmap() — те же физические страницы памяти
5. Client читает данные через Cursor API — **zero-copy**, прямой доступ к shared memory

Это намного эффективнее, чем сериализация/десериализация данных через Parcel (как было бы при обычном Binder IPC). Ограничение: default 2MB на один CursorWindow. При overflow — refill или TransactionTooLargeException.
</details>

### Вопрос 5
**Q:** Чем stable client отличается от unstable client?

<details>
<summary>Ответ</summary>

`acquireContentProviderClient()` (stable): если ContentProvider process крашится, ваш process тоже убивается. Это потому что stable reference создаёт сильную связь — система считает, что crash provider'а invalidates ваш state.

`acquireUnstableContentProviderClient()` (unstable): при crash provider'а вы получаете `DeadObjectException`, но ваш process остаётся живым. Можно обработать ошибку и retry.

Используйте unstable client для ненадёжных third-party providers или когда crash provider'а не должен убивать ваше приложение.
</details>

---

## Связь с другими темами

**[[android-app-components]]** — ContentProvider является одним из четырёх фундаментальных компонентов Android. Понимание общей модели компонентов (Activity, Service, BroadcastReceiver, ContentProvider) даёт контекст для осознания роли CP как единственного стандартного IPC-интерфейса для структурированных данных. Жизненный цикл CP управляется системой аналогично другим компонентам. Рекомендуется сначала изучить app-components, затем переходить к CP internals.

**[[android-data-persistence]]** — Room и DataStore часто выступают бэкэндом для ContentProvider. Типичный паттерн — Room для внутренней работы с данными, а ContentProvider как фасад для межпроцессного доступа. Понимание Room DAO, миграций и Flow-интеграции необходимо для реализации эффективного CP. Рекомендуется сначала изучить data-persistence, затем CP internals.

**[[android-handler-looper]]** — ContentProvider использует Binder thread pool для обработки запросов от клиентов, а ContentObserver callbacks доставляются через Handler. Понимание event loop, MessageQueue и threading модели Android объясняет, почему query/insert/update/delete выполняются в Binder потоках (concurrent), а onCreate() — на main thread. Изучение Handler/Looper помогает понять thread safety requirements для CP.

**[[android-process-memory]]** — ContentProvider влияет на приоритет процесса: если другой процесс использует ваш CP, система повышает приоритет вашего процесса. CursorWindow использует shared memory (ashmem/memfd) для zero-copy передачи данных между процессами. Понимание процессной модели Android объясняет, почему stable client при crash provider-а убивает и ваш процесс.

**[[android-permissions-security]]** — ContentProvider защищён многоуровневой моделью разрешений: readPermission/writePermission на уровне провайдера, path-permission для гранулярного контроля, и URI grants для временного доступа. Понимание permission модели Android критично для безопасной реализации CP. Рекомендуется изучать параллельно.

**[[android-intent-internals]]** — URI-based addressing в ContentProvider концептуально аналогична Intent resolution. FileProvider работает в связке с Intent для безопасного шаринга файлов между приложениями. Понимание Intent flags (FLAG_GRANT_READ_URI_PERMISSION) необходимо для работы с URI grants.

**[[android-app-startup-performance]]** — Библиотеки используют ContentProvider как хук для ранней инициализации (до Application.onCreate()), что замедляет cold start. App Startup library решает эту проблему через единый InitializationProvider с dependency graph. Понимание этой связи критично для оптимизации времени запуска приложения.

**[[android-context-internals]]** — ContentResolver получается через context.contentResolver, а сам ContentProvider получает Context через getContext() после attachInfo(). Понимание иерархии Context и различий между Application Context и Activity Context помогает правильно использовать CP в разных компонентах.

---

## Источники и дальнейшее чтение

| # | Источник | Тип | Описание |
|---|---------|-----|----------|
| 1 | [Content Providers](https://developer.android.com/guide/topics/providers/content-providers) | Docs | Официальная документация |
| 2 | [Content Provider Basics](https://developer.android.com/guide/topics/providers/content-provider-basics) | Docs | Основы создания и использования CP |
| 3 | [FileProvider](https://developer.android.com/reference/androidx/core/content/FileProvider) | Docs | FileProvider API reference |
| 4 | [App Startup](https://developer.android.com/topic/libraries/app-startup) | Docs | App Startup library |
| 5 | [AOSP: ContentProvider.java](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/core/java/android/content/ContentProvider.java) | AOSP | Исходный код ContentProvider |
| 6 | [AOSP: ContentResolver.java](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/core/java/android/content/ContentResolver.java) | AOSP | Исходный код ContentResolver |
| 7 | [AOSP: CursorWindow.java](https://cs.android.com/android/platform/superproject/+/main:frameworks/base/core/java/android/database/CursorWindow.java) | AOSP | CursorWindow shared memory |
| 8 | [Storage Access Framework](https://developer.android.com/guide/topics/providers/document-provider) | Docs | DocumentsProvider и SAF |
| 9 | [Sharing Files](https://developer.android.com/training/secure-file-sharing) | Docs | FileProvider best practices |
| 10 | [MediaStore](https://developer.android.com/training/data-storage/shared/media) | Docs | MediaStore для медиафайлов |
| 11 | [Scoped Storage](https://developer.android.com/about/versions/11/privacy/storage) | Docs | Scoped Storage изменения |
| 12 | [Photo Picker](https://developer.android.com/training/data-storage/shared/photopicker) | Docs | Android 13+ Photo Picker |

### Книги

- **Meier R. (2022)** *Professional Android* — глава о ContentProvider охватывает реализацию CRUD-операций, FileProvider и работу с системными провайдерами (MediaStore, Contacts). Полезно для понимания production-паттернов.
- **Phillips B. et al. (2022)** *Android Programming: The Big Nerd Ranch Guide* — практический подход к ContentProvider с пошаговыми примерами создания собственного провайдера и интеграции с Room.
- **Vasavada N. (2019)** *Android Internals* — детальное описание Binder IPC, CursorWindow shared memory и внутреннего устройства ContentProvider на уровне AOSP.
