---
title: "Компоненты приложения: Activity, Service, BR, CP"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [component-model, ipc-mechanisms, intent-pattern, process-lifecycle]
tags:
  - topic/android
  - topic/app-components
  - type/deep-dive
  - level/intermediate
related:
  - "[[android-overview]]"
  - "[[android-architecture]]"
  - "[[android-activity-lifecycle]]"
  - "[[android-process-memory]]"
  - "[[android-context-internals]]"
prerequisites:
  - "[[android-overview]]"
---

# Компоненты приложения: Activity, Service, BR, CP

Android-приложение не имеет единой точки входа main(). Вместо этого приложение состоит из **компонентов**, каждый из которых система может запустить независимо. Это фундаментальное отличие от desktop-приложений, где программа стартует, работает и завершается как единое целое.

> **Prerequisites:**
> - [[android-overview]] — базовое понимание Android
> - Понимание Intent как механизма коммуникации между компонентами

---

## Терминология

| Термин | Значение |
|--------|----------|
| **Activity** | Экран приложения с пользовательским интерфейсом |
| **Service** | Компонент для фоновой работы без UI |
| **BroadcastReceiver** | Получатель системных и пользовательских событий |
| **ContentProvider** | Интерфейс для доступа к данным между приложениями |
| **Intent** | Сообщение для запуска компонентов и передачи данных |
| **Context** | Доступ к ресурсам и сервисам системы |
| **Manifest** | XML-файл с декларацией компонентов приложения |

---

## Почему компоненты, а не main()

### Проблема мобильных устройств

Desktop-приложение живёт в "комфортных" условиях:
- Много памяти (8-64 GB RAM)
- Постоянное питание от сети
- Пользователь работает с 1-2 окнами одновременно
- Приложение работает пока пользователь не закрыл

Мобильное устройство — совсем другая среда:
- Мало памяти (2-8 GB на всё, включая систему)
- Ограниченная батарея
- Пользователь постоянно переключается между приложениями
- Приложение может быть убито в любой момент

### Что если бы Android использовал main()

```kotlin
// ❌ Гипотетическая модель с main()
fun main() {
    val app = Application()
    app.init()

    // Проблема 1: Как система узнает что показать при клике на уведомление?
    // Нужно запустить всё приложение и как-то передать "открой экран X"

    // Проблема 2: Другое приложение хочет контакты
    // Нужно запустить ВСЁ приложение ради одного запроса

    // Проблема 3: Система хочет sync в фоне
    // Нужно запустить UI, хотя он не нужен

    // Проблема 4: Мало памяти
    // Как убить часть приложения? Только всё целиком

    while (app.isRunning) {
        app.processEvents()
    }
}
```

### Как компоненты решают эти проблемы

```
┌─────────────────────────────────────────────────────────────────┐
│                    КОМПОНЕНТНАЯ МОДЕЛЬ                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Клик по уведомлению:                                           │
│  ┌─────────────────┐                                            │
│  │ DetailActivity  │ ← Запускается ТОЛЬКО этот компонент        │
│  └─────────────────┘   Остальное приложение не загружается      │
│                                                                 │
│  Другое приложение хочет контакты:                              │
│  ┌─────────────────┐                                            │
│  │ ContentProvider │ ← Запускается БЕЗ UI                       │
│  └─────────────────┘   Минимальное потребление ресурсов         │
│                                                                 │
│  Система хочет фоновую синхронизацию:                           │
│  ┌─────────────────┐                                            │
│  │    Service      │ ← Запускается БЕЗ UI                       │
│  └─────────────────┘   Экран выключен, батарея экономится       │
│                                                                 │
│  Мало памяти:                                                   │
│  Система убивает ТОЛЬКО неиспользуемые компоненты               │
│  Activity в фоне убита, Service продолжает работать             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Конкретные сценарии

| Сценарий | С main() | С компонентами |
|----------|----------|----------------|
| **Клик по deep link** | Загрузить всё приложение, найти обработчик URL, показать экран | Запустить только нужную Activity |
| **Получить контакт** | Запустить приложение контактов с UI | Вызвать ContentProvider, UI не нужен |
| **Push уведомление** | ??? Приложение не запущено | BroadcastReceiver срабатывает мгновенно |
| **Нехватка памяти** | Убить всё приложение или ничего | Убить фоновые Activity, оставить Service |
| **Share файла** | Писать API для каждого типа файла | Стандартный Intent + FileProvider |

### Альтернативные подходы и их проблемы

**1. Модель iOS (до iOS 4):**
- Одно приложение в памяти
- При переключении — полное завершение
- Проблема: нет многозадачности, потеря состояния

**2. Модель Windows Phone:**
- Tombstoning — сохранение состояния при уходе в фон
- Проблема: медленное восстановление, сложная логика сохранения

**3. Единая точка входа + роутинг:**
```kotlin
// Как в web-приложениях
fun main(args: Array<String>) {
    val route = args.getOrNull(0) ?: "/"
    when (route) {
        "/" -> showMain()
        "/detail" -> showDetail(args[1])
        // ...
    }
}
```
- Проблема: всё приложение загружается даже для простых операций
- Проблема: нет стандартного способа интеграции между приложениями

### Недостатки компонентной модели

1. **Сложность для разработчика:**
   - Нужно понимать жизненные циклы каждого компонента
   - Нужно правильно сохранять/восстанавливать состояние
   - Много boilerplate (регистрация в Manifest)

2. **Фрагментация состояния:**
   - Данные могут быть в Activity, Service, ContentProvider
   - Сложнее отслеживать общее состояние приложения

3. **Неочевидное поведение:**
   - Система может убить компонент в любой момент
   - Порядок вызова callback'ов не всегда интуитивен

4. **Overhead на IPC:**
   - Компоненты взаимодействуют через систему (Binder)
   - Медленнее прямого вызова функции

### Почему всё же это лучший выбор для мобилок

```
Desktop:                          Mobile:
┌─────────────────┐              ┌─────────────────┐
│ Много памяти    │              │ Мало памяти     │
│ Питание от сети │              │ Батарея         │
│ Мышь + клава    │              │ Touch + жесты   │
│ Большой экран   │              │ Маленький экран │
│ 1-2 окна        │              │ Постоянное      │
│ одновременно    │              │ переключение    │
└─────────────────┘              └─────────────────┘
         │                               │
         ▼                               ▼
    main() модель              Компонентная модель
    работает хорошо            единственный выбор
```

Компоненты — это не "лучший способ писать приложения", а **адаптация к ограничениям мобильных устройств**. Система должна уметь:
- Запускать части приложения независимо
- Убивать части для освобождения памяти
- Интегрировать приложения друг с другом

---

## Activity: экран приложения

Activity — компонент с пользовательским интерфейсом. Одна Activity = один экран (логически).

### Базовая структура

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Инициализация UI
        val button = findViewById<Button>(R.id.myButton)
        button.setOnClickListener {
            // Запустить другую Activity
            val intent = Intent(this, DetailActivity::class.java)
            intent.putExtra("item_id", 42)
            startActivity(intent)
        }
    }
}
```

### Регистрация в Manifest

Каждая Activity должна быть объявлена в `AndroidManifest.xml`:

```xml
<manifest>
    <application>
        <!-- Главная Activity (точка входа приложения) -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <!-- MAIN + LAUNCHER = иконка в лаунчере -->
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Обычная Activity (внутренняя) -->
        <activity
            android:name=".DetailActivity"
            android:exported="false" />
    </application>
</manifest>
```

### Activity Task и Back Stack

Activities организованы в **задачи (tasks)** со стеком:

```
Task 1 (приложение Email):
┌─────────────────┐
│ ComposeActivity │ ← Текущая (top)
├─────────────────┤
│ InboxActivity   │
├─────────────────┤
│ MainActivity    │ ← Первая в стеке
└─────────────────┘

Нажатие Back:
- ComposeActivity уничтожается
- InboxActivity становится видимой
```

Подробнее о жизненном цикле — в [[android-activity-lifecycle]].

---

## Service: фоновая работа

Service выполняет работу без UI. Существует два типа:

### Foreground Service

Видим пользователю через уведомление. Для долгих операций, которые пользователь осознаёт (музыка, навигация, скачивание).

```kotlin
class MusicService : Service() {

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Создать уведомление (обязательно для Foreground Service)
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Playing Music")
            .setContentText("Artist - Song")
            .setSmallIcon(R.drawable.ic_music)
            .build()

        // Перейти в foreground (обязательно в течение 5 секунд)
        startForeground(NOTIFICATION_ID, notification)

        // Начать воспроизведение
        playMusic()

        // START_STICKY = перезапустить service если система убьёт
        return START_STICKY
    }

    override fun onBind(intent: Intent): IBinder? = null

    override fun onDestroy() {
        stopMusic()
        super.onDestroy()
    }
}
```

**Запуск:**
```kotlin
val intent = Intent(this, MusicService::class.java)
// Android 8+: обязательно startForegroundService для foreground
ContextCompat.startForegroundService(this, intent)
```

### Background Service (устарел)

До Android 8 можно было запускать фоновые Service без уведомления. Сейчас это запрещено — система убьёт такой Service через минуту после ухода приложения в фон.

**Используйте вместо этого:**
- **WorkManager** — для отложенных/периодических задач
- **Foreground Service** — для долгих задач с уведомлением
- **JobScheduler** — для задач с условиями (сеть, зарядка)

### Bound Service

Service, к которому можно "привязаться" для двустороннего взаимодействия:

```kotlin
class CalculatorService : Service() {
    private val binder = LocalBinder()

    inner class LocalBinder : Binder() {
        fun getService(): CalculatorService = this@CalculatorService
    }

    override fun onBind(intent: Intent): IBinder = binder

    fun calculate(a: Int, b: Int): Int = a + b
}

// В Activity:
class MainActivity : AppCompatActivity() {
    private var calculatorService: CalculatorService? = null

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName?, binder: IBinder?) {
            calculatorService = (binder as CalculatorService.LocalBinder).getService()
        }

        override fun onServiceDisconnected(name: ComponentName?) {
            calculatorService = null
        }
    }

    override fun onStart() {
        super.onStart()
        Intent(this, CalculatorService::class.java).also { intent ->
            bindService(intent, connection, Context.BIND_AUTO_CREATE)
        }
    }

    override fun onStop() {
        super.onStop()
        unbindService(connection)
    }
}
```

### Return-значения onStartCommand

| Значение | Поведение после kill |
|----------|---------------------|
| `START_NOT_STICKY` | Не перезапускать |
| `START_STICKY` | Перезапустить с null Intent |
| `START_REDELIVER_INTENT` | Перезапустить с последним Intent |

---

## BroadcastReceiver: получение событий

BroadcastReceiver реагирует на системные или пользовательские события (broadcasts).

### Регистрация в Manifest (статическая)

```xml
<receiver
    android:name=".BootReceiver"
    android:exported="true"
    android:enabled="true">
    <intent-filter>
        <action android:name="android.intent.action.BOOT_COMPLETED" />
    </intent-filter>
</receiver>
```

```kotlin
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // Устройство загрузилось
            // Запланировать работу через WorkManager
            schedulePeriodicSync(context)
        }
    }
}
```

### Регистрация в коде (динамическая)

Для событий, которые нужны только пока приложение активно:

```kotlin
class MainActivity : AppCompatActivity() {
    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            updateBatteryUI(level)
        }
    }

    override fun onResume() {
        super.onResume()
        // Зарегистрировать для получения изменений батареи
        registerReceiver(
            batteryReceiver,
            IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        )
    }

    override fun onPause() {
        super.onPause()
        // Обязательно отменить регистрацию
        unregisterReceiver(batteryReceiver)
    }
}
```

### Ограничения Android 8+

Большинство implicit broadcasts больше не доставляются приложениям, зарегистрированным через Manifest. Это экономит батарею.

**Работают:**
- `ACTION_BOOT_COMPLETED`
- `ACTION_LOCALE_CHANGED`
- Broadcasts с explicit component

**Не работают через Manifest:**
- `ACTION_POWER_CONNECTED` — регистрируйте в коде
- `CONNECTIVITY_ACTION` — используйте `ConnectivityManager.NetworkCallback`

---

## ContentProvider: доступ к данным

ContentProvider предоставляет структурированный доступ к данным приложения. Другие приложения могут читать/писать данные через стандартный интерфейс.

### Зачем нужен ContentProvider

- **Системные данные:** Contacts, Calendar, MediaStore — всё через ContentProvider
- **Sharing между приложениями:** FileProvider для безопасной передачи файлов
- **Синхронизация:** SyncAdapter требует ContentProvider

### Использование системного ContentProvider

```kotlin
// Получить контакты (требует разрешение READ_CONTACTS)
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,  // URI данных
    arrayOf(                                  // Колонки
        ContactsContract.Contacts._ID,
        ContactsContract.Contacts.DISPLAY_NAME
    ),
    null,   // WHERE
    null,   // WHERE args
    null    // ORDER BY
)

cursor?.use {
    while (it.moveToNext()) {
        val id = it.getLong(0)
        val name = it.getString(1)
        Log.d("Contact", "ID: $id, Name: $name")
    }
}
```

### Создание своего ContentProvider

```kotlin
class NotesProvider : ContentProvider() {

    companion object {
        const val AUTHORITY = "com.example.app.provider"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/notes")
    }

    private lateinit var database: NotesDatabase

    override fun onCreate(): Boolean {
        database = NotesDatabase.getInstance(context!!)
        return true
    }

    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        return database.notesDao().getAllAsCursor()
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        val id = database.notesDao().insert(values.toNote())
        context?.contentResolver?.notifyChange(uri, null)
        return ContentUris.withAppendedId(CONTENT_URI, id)
    }

    override fun update(uri: Uri, values: ContentValues?,
                        selection: String?, selectionArgs: Array<String>?): Int {
        // ...
        return count
    }

    override fun delete(uri: Uri, selection: String?,
                        selectionArgs: Array<String>?): Int {
        // ...
        return count
    }

    override fun getType(uri: Uri): String {
        return "vnd.android.cursor.dir/vnd.$AUTHORITY.notes"
    }
}
```

**Manifest:**
```xml
<provider
    android:name=".NotesProvider"
    android:authorities="com.example.app.provider"
    android:exported="false" />
```

### FileProvider для sharing файлов

Безопасный способ передать файл другому приложению:

```kotlin
// Создать URI для файла через FileProvider
val file = File(context.filesDir, "shared_image.png")
val uri = FileProvider.getUriForFile(
    context,
    "${context.packageName}.fileprovider",
    file
)

// Отправить через Intent
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "image/png"
    putExtra(Intent.EXTRA_STREAM, uri)
    addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
}
startActivity(Intent.createChooser(shareIntent, "Share via"))
```

---

## Intent: связь между компонентами

Intent — сообщение, описывающее действие. Используется для:
- Запуска Activity, Service, BroadcastReceiver
- Передачи данных между компонентами

### Explicit Intent

Указывает конкретный компонент (класс):

```kotlin
// Запустить конкретную Activity
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("item_id", 42)
startActivity(intent)

// Запустить Service
val serviceIntent = Intent(this, DownloadService::class.java)
startService(serviceIntent)
```

### Implicit Intent

Описывает действие, система найдёт подходящий компонент:

```kotlin
// Открыть URL в браузере
val browserIntent = Intent(Intent.ACTION_VIEW, Uri.parse("https://example.com"))
startActivity(browserIntent)

// Отправить email
val emailIntent = Intent(Intent.ACTION_SENDTO).apply {
    data = Uri.parse("mailto:")
    putExtra(Intent.EXTRA_EMAIL, arrayOf("test@example.com"))
    putExtra(Intent.EXTRA_SUBJECT, "Hello")
}
if (emailIntent.resolveActivity(packageManager) != null) {
    startActivity(emailIntent)
}

// Сделать фото
val takePictureIntent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
startActivityForResult(takePictureIntent, REQUEST_IMAGE_CAPTURE)
```

### Intent Filter

Объявляет, какие implicit intents компонент может обработать:

```xml
<activity android:name=".ShareActivity">
    <intent-filter>
        <!-- Действие -->
        <action android:name="android.intent.action.SEND" />
        <!-- Категория -->
        <category android:name="android.intent.category.DEFAULT" />
        <!-- Тип данных -->
        <data android:mimeType="text/plain" />
    </intent-filter>
</activity>
```

Теперь приложение будет в списке "Share via" для текста.

### PendingIntent

Intent, который будет выполнен позже от имени вашего приложения:

```kotlin
// Создать PendingIntent для Activity
val intent = Intent(this, NotificationActivity::class.java)
val pendingIntent = PendingIntent.getActivity(
    this,
    REQUEST_CODE,
    intent,
    PendingIntent.FLAG_IMMUTABLE  // Android 12+ требует
)

// Использовать в уведомлении
val notification = NotificationCompat.Builder(this, CHANNEL_ID)
    .setContentTitle("New message")
    .setContentIntent(pendingIntent)  // Клик откроет Activity
    .setAutoCancel(true)
    .build()
```

---

## Context: точка доступа к системе

Context — интерфейс к системным сервисам и ресурсам. Activity и Service наследуют Context.

### Типы Context

| Тип | Жизненный цикл | Использовать для |
|-----|----------------|------------------|
| `Activity` | Activity | UI операции, dialogs |
| `Service` | Service | Фоновые операции |
| `Application` | Всё приложение | Singleton'ы, DI |

### Распространённая ошибка

```kotlin
// ПЛОХО: утечка памяти!
class MySingleton private constructor(private val context: Context) {
    companion object {
        private var instance: MySingleton? = null

        fun getInstance(context: Context): MySingleton {
            if (instance == null) {
                // Activity context в singleton → Activity не соберётся GC
                instance = MySingleton(context)
            }
            return instance!!
        }
    }
}

// ХОРОШО: использовать Application context
fun getInstance(context: Context): MySingleton {
    if (instance == null) {
        instance = MySingleton(context.applicationContext)
    }
    return instance!!
}
```

---

## Когда какой компонент использовать

### Decision Tree

```
Вопрос 1: Нужен пользовательский интерфейс?
├─ ДА → Activity
│   ├─ Один экран с UI
│   ├─ Взаимодействие с пользователем
│   └─ Примеры: главный экран, форма, детали товара
│
└─ НЕТ → Вопрос 2: Нужна фоновая работа?
    ├─ ДА → Вопрос 3: Насколько долгая?
    │   ├─ > 10 секунд, пользователь должен видеть → Foreground Service
    │   │   ├─ Обязательно уведомление
    │   │   └─ Примеры: музыка, навигация, скачивание, запись
    │   │
    │   └─ Отложенная/периодическая задача → WorkManager
    │       ├─ Выполнится когда система решит (батарея, сеть)
    │       └─ Примеры: синхронизация, backup, upload
    │
    └─ НЕТ → Вопрос 4: Реагировать на события?
        ├─ ДА → BroadcastReceiver
        │   ├─ Короткая работа (< 10 сек)
        │   ├─ Для долгой → запустить Service/WorkManager
        │   └─ Примеры: получен push, зарядка подключена, загрузка системы
        │
        └─ НЕТ → Вопрос 5: Предоставить данные?
            └─ ДА → ContentProvider
                ├─ Структурированный доступ к данным
                ├─ Sharing между приложениями
                └─ Примеры: контакты, календарь, FileProvider
```

### Конкретные сценарии

| Что нужно сделать | Используй | Почему |
|-------------------|-----------|--------|
| **Показать экран** | Activity | Единственный компонент с UI |
| **Проиграть музыку** | Foreground Service | Долгая работа, пользователь осознаёт (уведомление) |
| **Скачать файл** | Foreground Service | Пользователь видит прогресс, может занять долго |
| **Синхронизация каждые 6 часов** | WorkManager | Не критично когда именно, система оптимизирует |
| **Получить push** | BroadcastReceiver | Быстро отреагировать на событие |
| **Upload фото при WiFi** | WorkManager с constraints | Условная задача (сеть) |
| **Поделиться файлом** | FileProvider (ContentProvider) | Безопасная передача файла |
| **Дать доступ к БД** | ContentProvider | Стандартный CRUD интерфейс |
| **Запись голоса** | Foreground Service | Долго, пользователь видит уведомление |

### Activity: когда использовать

**Используй Activity когда:**
- Нужен пользовательский интерфейс (UI)
- Пользователь взаимодействует с экраном
- Нужна навигация между экранами

**Примеры:**
- Главный экран (список товаров)
- Форма логина
- Детали товара
- Настройки

**Не используй Activity для:**
- Фоновой работы без UI
- Долгих операций (скачивание, музыка)
- Реакции на события без пользователя

### Service: когда использовать

**Используй Foreground Service когда:**
- Долгая операция (> 10 секунд)
- Пользователь должен знать что происходит
- Обязательно показать уведомление

**Примеры:**
- Проигрывание музыки
- GPS навигация
- Скачивание большого файла
- Запись голоса/видео

**Используй WorkManager (НЕ Service) когда:**
- Задача может подождать
- Есть условия (сеть, зарядка)
- Периодическая задача
- Не критично когда выполнится

**Примеры:**
- Синхронизация данных
- Backup
- Upload фото
- Очистка кеша

**Не используй Background Service:**
- Android 8+ убьёт его через минуту
- Используй WorkManager или Foreground Service

### BroadcastReceiver: когда использовать

**Используй BroadcastReceiver когда:**
- Нужно отреагировать на системное событие
- Работа короткая (< 10 секунд)
- Приложение не активно, но должно среагировать

**Примеры:**
- Получен push notification
- Устройство загрузилось (BOOT_COMPLETED)
- Подключена зарядка
- Сменился часовой пояс

**Не используй BroadcastReceiver для:**
- Долгой работы → запусти Service/WorkManager из onReceive()
- Операций с UI → запусти Activity
- Большинство implicit broadcasts не работают через Manifest (Android 8+)

### ContentProvider: когда использовать

**Используй ContentProvider когда:**
- Нужно предоставить данные другим приложениям
- Нужна структурированная работа с данными (CRUD)
- Требуется SyncAdapter
- Нужно безопасно передать файл (FileProvider)

**Примеры:**
- Приложение контактов (системный ContentProvider)
- Календарь
- Sharing файла (FileProvider)
- Собственная БД для других приложений

**Не используй ContentProvider для:**
- Внутренней БД приложения (используй Room напрямую)
- Простой передачи данных между Activity (используй Intent extras)
- Если данные только для твоего приложения

---

## Проверь себя

Перед тем как изучать детали, убедись что понял основы:

**1. Чем Activity отличается от Service?**

<details>
<summary>Показать ответ</summary>

**Activity** — компонент с пользовательским интерфейсом, пользователь видит и взаимодействует с экраном. Живёт только пока пользователь на экране.

**Service** — компонент для фоновой работы без UI. Может работать даже когда приложение не активно.

**Ключевое отличие:** Activity = UI, Service = без UI.

</details>

**2. Когда использовать Foreground Service вместо WorkManager?**

<details>
<summary>Показать ответ</summary>

**Foreground Service:**
- Долгая операция, которую пользователь осознаёт
- Нужно показать уведомление
- Критично выполнить сейчас, не откладывая
- Примеры: музыка, навигация, скачивание

**WorkManager:**
- Задача может подождать
- Есть условия выполнения (WiFi, зарядка)
- Периодическая задача
- Система сама выберет лучшее время (батарея)
- Примеры: синхронизация, backup, upload

**Правило:** Если пользователь должен видеть что происходит → Foreground Service. Если может подождать → WorkManager.

</details>

**3. Зачем нужен ContentProvider?**

<details>
<summary>Показать ответ</summary>

**ContentProvider** предоставляет стандартный интерфейс для доступа к данным между приложениями.

**Зачем:**
1. **Sharing данных** — другие приложения могут читать/писать (контакты, календарь)
2. **Стандартный CRUD** — query, insert, update, delete
3. **Безопасность** — контроль разрешений, FileProvider для файлов
4. **Синхронизация** — SyncAdapter требует ContentProvider

**Когда НЕ нужен:** Если данные только для твоего приложения, используй Room напрямую.

</details>

**4. Что такое implicit vs explicit Intent?**

<details>
<summary>Показать ответ</summary>

**Explicit Intent** — указываешь конкретный класс компонента:
```kotlin
Intent(this, DetailActivity::class.java)  // Запустить именно DetailActivity
```

**Implicit Intent** — описываешь действие, система находит подходящий компонент:
```kotlin
Intent(Intent.ACTION_VIEW, Uri.parse("https://example.com"))  // Система найдёт браузер
```

**Разница:**
- Explicit → знаешь что запустить (внутри приложения)
- Implicit → система решает что запустить (интеграция с другими приложениями)

**Правило:** Explicit для своих компонентов, implicit для системных действий (открыть URL, отправить email, сделать фото).

</details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Activity = экран" | Activity — хост для UI, не сам экран. Compose screen, Fragment — части Activity. Single Activity + Navigation — современный подход |
| "Service работает в background thread" | Service работает на Main Thread! Для background work используй coroutines/WorkManager внутри Service. Или IntentService (deprecated) |
| "Foreground Service = гарантия" | Foreground Service имеет высокий приоритет, но система всё равно может убить при extreme memory pressure. WorkManager для гарантии |
| "BroadcastReceiver для всего" | Implicit broadcasts ограничены с Android 8. Многие broadcasts manifest-declared больше не работают. Используй explicit или JobScheduler |
| "ContentProvider только для sharing" | ContentProvider = structured data access. FileProvider для файлов. Но если данные только для вашего app — Room напрямую проще |
| "startActivity() мгновенный" | startActivity() планирует запуск, но Activity создаётся асинхронно. onActivityResult может прийти после вашего onResume |
| "finish() уничтожает Activity" | finish() планирует уничтожение. Activity может остаться в памяти. onDestroy вызывается позже, не сразу |
| "Intent = межпроцессное общение" | Intent может быть и in-process (explicit intent к своему компоненту). Binder используется для IPC, Intent — высокоуровневая абстракция |
| "Компоненты живут вечно" | Система убивает компоненты по приоритету. Process death уничтожает всё. SavedState и WorkManager для восстановления |
| "Context везде одинаков" | Application Context, Activity Context, Service Context — разные. Activity Context имеет theme. Application Context — singleton |

---

## CS-фундамент

| CS-концепция | Как применяется в Components |
|--------------|------------------------------|
| **Component Model** | Android Components = loosely coupled units. Intent для communication. Manifest для declaration |
| **Lifecycle Management** | Система управляет lifecycle. Callbacks (onCreate, onStart). State machine переходов |
| **Process Priority** | Foreground (Activity) → Visible → Service → Background → Empty. LMK убивает по приоритету |
| **Message Passing** | Intent = message object. Bundle = payload. Binder для IPC. Async delivery |
| **Pub/Sub Pattern** | BroadcastReceiver = subscriber. sendBroadcast = publish. Loose coupling |
| **Singleton Pattern** | Application class = app-wide singleton. ContentProvider initialized once per process |
| **Factory Pattern** | System services через getSystemService(). Activity instantiation через reflection |
| **State Preservation** | onSaveInstanceState/onRestoreInstanceState. Bundle serialization. Parcelable для efficiency |
| **Intent Resolution** | PackageManager resolves implicit intents. Intent filters matching. Chooser для multiple matches |
| **Task & Back Stack** | Task = stack of Activities. Back button pops stack. Launch modes control behavior |

---

## Связи

**Обязательно изучи далее:**
- [[android-activity-lifecycle]] — детальный разбор жизненного цикла Activity
  *Почему связано:* Activity — самый сложный компонент, нужно понимать onCreate, onStart, onResume и как система управляет жизненным циклом при нехватке памяти

- [[android-process-memory]] — как система решает какие компоненты убить
  *Почему связано:* Android может убить компоненты в любой момент, нужно понимать приоритеты процессов и как сохранять состояние

**Фундамент:**
- [[android-overview]] — карта раздела Android
  *Почему связано:* Компоненты — это core концепция Android, часть общей архитектуры системы

- [[android-architecture]] — как система запускает компоненты через ActivityManager и PackageManager
  *Почему связано:* Чтобы понять что происходит "под капотом" когда ты вызываешь startActivity() или startService()

**Операционные системы:**
- [[os-processes-threads]] — процессы, на которых основаны компоненты
  *Почему связано:* Каждое Android-приложение — это Linux процесс, компоненты работают в контексте процесса

---

## Источники и дальнейшее чтение

**Книги:**
- Phillips B. et al. (2022). Android Programming: The Big Nerd Ranch Guide, 5th Edition. — практический учебник Android с подробным разбором всех четырёх компонентов приложения
- Meier R. (2022). Professional Android, 4th Edition. — комплексное руководство по Android-разработке, включая компонентную модель и IPC
- Vasavada N. (2019). Android Internals: A Confectioner's Cookbook. — внутреннее устройство Android, детальное описание ActivityManagerService и механизма запуска компонентов

**Веб-ресурсы:**
- [Introduction to Activities - Android Developers](https://developer.android.com/guide/components/activities/intro-activities) — официальная документация
- [Services Overview - Android Developers](https://developer.android.com/guide/components/services) — документация по Services
- [Broadcasts Overview - Android Developers](https://developer.android.com/guide/components/broadcasts) — BroadcastReceiver
- [Content Providers - Android Developers](https://developer.android.com/guide/topics/providers/content-providers) — ContentProvider

---

*Проверено: 2026-01-09 | На основе официальной документации Android*
