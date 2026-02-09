---
title: "Процессы и память: как Android управляет ресурсами"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
tags:
  - android
  - memory
  - process
  - lmk
  - gc
related:
  - "[[android-overview]]"
  - "[[android-architecture]]"
  - "[[android-activity-lifecycle]]"
  - "[[os-processes-threads]]"
  - "[[os-memory-management]]"
  - "[[jvm-gc-tuning]]"
  - "[[jvm-memory-model]]"
  - "[[android-memory-leaks]]"
cs-foundations: [process-priority, memory-management, garbage-collection, resource-constraints]
---

# Процессы и память: как Android управляет ресурсами

Android работает на устройствах с ограниченными ресурсами. В отличие от серверов с десятками гигабайт RAM, смартфон имеет 4-8 GB на всё: систему, все приложения, кэши. Система агрессивно управляет памятью, убивая процессы приложений для освобождения ресурсов. Понимание этих механизмов объясняет, почему ваше приложение "умирает" в фоне и как правильно с этим работать.

> **Prerequisites:**
> - [[os-memory-management]] — виртуальная память, paging
> - [[os-processes-threads]] — процессы на уровне ОС
> - [[android-activity-lifecycle]] — почему Android убивает процессы

---

## Терминология

| Термин | Значение |
|--------|----------|
| **LMK** | Low Memory Killer — убивает процессы при нехватке памяти |
| **OOM Adjustment** | Приоритет процесса для LMK (ниже = важнее) |
| **PSS** | Proportional Set Size — память процесса с учётом shared |
| **USS** | Unique Set Size — память только этого процесса |
| **Heap** | Память для объектов приложения |
| **Native Memory** | Память вне managed heap (NDK, графика) |
| **Process Death** | Убийство процесса системой |
| **Trim Memory** | Callback о необходимости освободить память |

---

## Один процесс — одно приложение

Каждое Android-приложение выполняется в отдельном Linux-процессе:

```
┌─────────────────────────────────────────────────────────────────┐
│                         ANDROID                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  System Server (PID 1234)                                       │
│  ├── ActivityManagerService                                     │
│  ├── WindowManagerService                                       │
│  └── ...                                                        │
│                                                                 │
│  com.example.app (PID 5678)      ← Ваше приложение             │
│  ├── Main Thread (UI)                                           │
│  ├── Worker Threads                                             │
│  └── Binder Threads                                             │
│                                                                 │
│  com.google.android.gms (PID 9012)                              │
│  └── Google Play Services                                       │
│                                                                 │
│  com.android.chrome (PID 3456)                                  │
│  └── Chrome Browser                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Следствия:**
- Crash приложения не роняет систему и другие приложения
- Система может убить процесс приложения, не затрагивая другие
- Коммуникация между приложениями — через IPC (Binder)

Подробнее о процессах в Linux — в [[os-processes-threads]].

---

## Приоритеты процессов и Low Memory Killer

### Иерархия приоритетов

Android присваивает каждому процессу **OOM adjustment** — число, определяющее важность процесса. Чем меньше число, тем важнее процесс.

```
OOM_ADJ    Категория             Описание
───────────────────────────────────────────────────────────────────
-1000     NATIVE                 Системные нативные процессы
-900      SYSTEM                 system_server
-800      PERSISTENT             Постоянные системные приложения
-700      PERSISTENT_SERVICE     Сервисы постоянных приложений
0         FOREGROUND             Текущее foreground приложение
100       VISIBLE                Видимое приложение (не в фокусе)
200       PERCEPTIBLE            Приложение с foreground service
300       BACKUP                 Backup/restore в процессе
400       HEAVY_WEIGHT           Heavy-weight приложение
500       SERVICE                Приложение с running service
600       HOME                   Launcher
700       PREVIOUS               Предыдущее foreground приложение
800       SERVICE_B              Старые services
900       CACHED                 Кэшированные (фоновые) приложения
1000      EMPTY                  Пустые процессы
───────────────────────────────────────────────────────────────────
          ▲                                                ▲
          │                                                │
    Убивается                                       Убивается
    последним                                       первым
```

### Как работает LMK

Low Memory Killer — модуль ядра Linux (Android-specific), который мониторит свободную память и убивает процессы когда память заканчивается.

```
Свободная память падает:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  100% ─────────────────────────────────────────────             │
│                                                                 │
│   80% ────────────── Threshold 1: убить EMPTY                   │
│                                                                 │
│   60% ────────────── Threshold 2: убить CACHED                  │
│                                                                 │
│   40% ────────────── Threshold 3: убить SERVICE                 │
│                                                                 │
│   20% ────────────── Threshold 4: убить VISIBLE (критично!)     │
│                                                                 │
│    0% ─────────────────────────────────────────────             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Отличие от стандартного OOM Killer Linux:**
- Linux OOM Killer срабатывает когда память **уже закончилась**
- Android LMK срабатывает **заранее**, поддерживая свободную память
- Это обеспечивает отзывчивость системы даже при высокой нагрузке

Подробнее об OOM Killer — в [[os-memory-management]].

### Что определяет приоритет приложения

| Состояние приложения | OOM_ADJ | Вероятность kill |
|---------------------|---------|------------------|
| Foreground Activity (пользователь смотрит) | 0 | Очень низкая |
| Visible Activity (диалог поверх) | 100 | Низкая |
| Foreground Service (музыка, навигация) | 200 | Низкая |
| Background Service | 500 | Средняя |
| Cached (ушли в фон) | 900 | Высокая |
| Empty (процесс без компонентов) | 1000 | Очень высокая |

---

## Память приложения: из чего состоит

### Структура памяти Android-приложения

```
┌─────────────────────────────────────────────────────────────────┐
│                    ПАМЯТЬ ПРИЛОЖЕНИЯ                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    JAVA/KOTLIN HEAP                       │   │
│  │  Объекты, созданные в коде                                │   │
│  │  - Activities, Fragments                                  │   │
│  │  - ViewModels, Adapters                                   │   │
│  │  - Ваши объекты и коллекции                               │   │
│  │                                                           │   │
│  │  Управляется: ART GC                                      │   │
│  │  Лимит: dalvik.vm.heapsize (128-512MB)                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    NATIVE HEAP                            │   │
│  │  Память, выделенная через malloc/new в native коде        │   │
│  │  - Bitmap pixels (до Android 8)                           │   │
│  │  - NDK библиотеки                                         │   │
│  │  - SQLite native structures                               │   │
│  │                                                           │   │
│  │  Управляется: вручную (или native allocator)              │   │
│  │  Лимит: нет жёсткого лимита                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    GRAPHICS MEMORY                        │   │
│  │  - Bitmap pixels (Android 8+)                             │   │
│  │  - OpenGL/Vulkan buffers                                  │   │
│  │  - Hardware layers                                        │   │
│  │                                                           │   │
│  │  Управляется: система                                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CODE & DEX                             │   │
│  │  - Код приложения (DEX)                                   │   │
│  │  - Framework code (shared)                                │   │
│  │                                                           │   │
│  │  Частично shared между приложениями (Zygote)              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Heap Limit

Каждое приложение имеет лимит на Java/Kotlin heap:

```kotlin
// Узнать лимит heap в MB
val activityManager = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
val memoryClass = activityManager.memoryClass  // Обычно 128-256MB
val largeMemoryClass = activityManager.largeMemoryClass  // 512MB+

// Для приложений с большими изображениями можно запросить large heap
// android:largeHeap="true" в Manifest
// НО: это не гарантия, и LMK будет убивать вас агрессивнее!
```

**Типичные значения:**
- Low-end устройства: 128MB
- Mid-range: 256MB
- Flagship: 384-512MB

При превышении лимита — **OutOfMemoryError**.

---

## Garbage Collection в Android

ART GC оптимизирован для мобильных устройств — короткие паузы важнее throughput.

### Concurrent Copying GC

```
┌─────────────────────────────────────────────────────────────────┐
│                    ART GARBAGE COLLECTION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. CONCURRENT MARK (параллельно с приложением)                 │
│     └── Находит все достижимые объекты                          │
│                                                                 │
│  2. CONCURRENT COPY (параллельно с приложением)                 │
│     └── Копирует живые объекты в новую область                  │
│     └── Read barrier обновляет ссылки на лету                   │
│                                                                 │
│  3. КОРОТКАЯ ПАУЗА (~2ms)                                       │
│     └── Финализация, обновление roots                           │
│                                                                 │
│  Сравнение с JVM:                                               │
│  ┌─────────────┬─────────────┬─────────────┐                   │
│  │             │ ART         │ JVM G1      │                   │
│  ├─────────────┼─────────────┼─────────────┤                   │
│  │ Паузы       │ 2-5ms       │ 50-200ms    │                   │
│  │ Throughput  │ 85%         │ 90%         │                   │
│  │ Heap size   │ 128-512MB   │ 1-32GB      │                   │
│  └─────────────┴─────────────┴─────────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Когда GC вызывает проблемы

GC в Android обычно незаметен. Но если создавать много объектов:

```kotlin
// ПЛОХО: создание объектов в draw loop (60 раз в секунду)
override fun onDraw(canvas: Canvas) {
    val paint = Paint()  // Новый объект каждый кадр!
    val rect = Rect(0, 0, 100, 100)  // И ещё один!
    canvas.drawRect(rect, paint)
}

// ХОРОШО: переиспользовать объекты
private val paint = Paint()
private val rect = Rect()

override fun onDraw(canvas: Canvas) {
    rect.set(0, 0, 100, 100)
    canvas.drawRect(rect, paint)
}
```

**Признаки GC pressure:**
- UI jank (пропуск кадров)
- В логах частые сообщения о GC
- Android Studio Profiler показывает зубчатый график памяти

Подробнее о GC — в [[jvm-gc-tuning]].

---

## Обработка нехватки памяти

### onTrimMemory callback

Система предупреждает приложение о нехватке памяти:

```kotlin
class MyApplication : Application() {

    override fun onTrimMemory(level: Int) {
        super.onTrimMemory(level)

        when (level) {
            // Приложение в фоне, памяти мало
            TRIM_MEMORY_RUNNING_MODERATE -> {
                // Освободить что можно
                imageCache.trimToSize(imageCache.maxSize() / 2)
            }

            // Приложение в фоне, памяти критически мало
            TRIM_MEMORY_RUNNING_CRITICAL -> {
                // Освободить почти всё
                imageCache.evictAll()
            }

            // Приложение перешло в фон
            TRIM_MEMORY_UI_HIDDEN -> {
                // Освободить UI-ресурсы
                releaseUiResources()
            }

            // Система убивает фоновые процессы
            TRIM_MEMORY_BACKGROUND,
            TRIM_MEMORY_MODERATE,
            TRIM_MEMORY_COMPLETE -> {
                // Освободить максимум
                clearAllCaches()
            }
        }
    }
}
```

### onLowMemory (устаревший)

Старый callback, вызывается когда совсем плохо:

```kotlin
override fun onLowMemory() {
    super.onLowMemory()
    // Освободить все некритичные ресурсы
    // Эквивалент TRIM_MEMORY_COMPLETE
}
```

---

## Process Death и восстановление

### Когда процесс умирает

```
Пользователь:
1. Открыл ваше приложение
2. Заполнил форму
3. Переключился на камеру (тяжёлое приложение)
4. Сделал фото, обработал
5. Вернулся в ваше приложение

Что произошло:
- Камера потребовала много памяти
- LMK убил процесс вашего приложения
- При возврате процесс создаётся заново
- Activity восстанавливается из savedInstanceState
- НО: данные в ViewModel/памяти потеряны!
```

### Как правильно обрабатывать

```kotlin
// 1. Сохранять критичные данные в onStop (не в onDestroy!)
override fun onStop() {
    super.onStop()
    // Сохранить черновик формы
    preferences.edit().putString("draft", formData).apply()
}

// 2. Использовать SavedStateHandle в ViewModel
class FormViewModel(private val savedState: SavedStateHandle) : ViewModel() {

    // Автоматически сохраняется при process death
    var formData: String
        get() = savedState["form_data"] ?: ""
        set(value) { savedState["form_data"] = value }
}

// 3. Проверять savedInstanceState в onCreate
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    if (savedInstanceState != null) {
        // Восстановление после process death или config change
        restoreState(savedInstanceState)
    }
}
```

### Тестирование process death

```bash
# Симулировать убийство процесса
# 1. Открыть приложение, перейти в нужное состояние
# 2. Нажать Home
# 3. Выполнить команду:
adb shell am kill com.example.app

# 4. Вернуться в приложение через Recent Apps
# 5. Проверить, что состояние восстановилось

# Или в Android Studio:
# Debug → Terminate Application (в Logcat)
```

---

## Отладка памяти

### Команды adb

```bash
# Общая информация о памяти системы
adb shell cat /proc/meminfo

# Память конкретного приложения
adb shell dumpsys meminfo com.example.app

# Вывод:
#                    Pss  Private  Private  SwapPss     Heap     Heap     Heap
#                  Total    Dirty    Clean    Dirty     Size    Alloc     Free
#                 ------   ------   ------   ------   ------   ------   ------
#   Native Heap    12345    12300       45        0    16384    14567     1817
#   Dalvik Heap    23456    23400       56        0    32768    28901     3867
#   ...

# Информация о процессах и OOM adj
adb shell dumpsys activity processes

# GC статистика
adb shell dumpsys meminfo --package com.example.app
```

### Android Studio Profiler

Memory Profiler показывает в реальном времени:
- Java Heap allocation
- Native memory
- Graphics
- Code

```
Как найти утечку памяти:
1. Открыть Profiler → Memory
2. Выполнить действие (открыть/закрыть Activity)
3. Нажать "Dump Java Heap"
4. Искать объекты, которые не должны существовать
5. Посмотреть GC roots — что держит объект
```

### LeakCanary

Автоматическое обнаружение утечек:

```kotlin
// build.gradle
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}

// Всё! LeakCanary автоматически:
// - Следит за Activities, Fragments, ViewModels
// - Обнаруживает утечки
// - Показывает уведомление с отчётом
```

---

## Подводные камни памяти в Android

### Context Leaks: когда Activity не может умереть

**Проблема:** Activity — это крупный объект (весь View hierarchy + context). Если удержать ссылку на Activity после её уничтожения, вся эта память не освободится.

```kotlin
// ПЛОХО: Activity в static переменной
class LoginActivity : AppCompatActivity() {
    companion object {
        var instance: LoginActivity? = null  // Утечка!
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        instance = this  // Activity никогда не будет собрана GC
    }
}

// Почему это опасно:
// 1. Activity держит весь View hierarchy (мегабайты)
// 2. Activity держит Context, который держит Resources
// 3. При повороте экрана создаётся новая Activity, старая остаётся в памяти
// 4. После 5-10 поворотов = OutOfMemoryError
```

**Решение:**

```kotlin
// ХОРОШО 1: Application Context для долгоживущих объектов
object Analytics {
    private lateinit var context: Context

    fun init(context: Context) {
        this.context = context.applicationContext  // Application живёт всегда
    }
}

// ХОРОШО 2: WeakReference если нужна именно Activity
class MyManager {
    private var activityRef: WeakReference<Activity>? = null

    fun setActivity(activity: Activity) {
        activityRef = WeakReference(activity)
    }

    fun doSomething() {
        activityRef?.get()?.let { activity ->
            // Используем, если Activity ещё жива
        }
    }
}
```

### Bitmap Memory Management: самый тяжёлый объект

**Почему Bitmap критичен:**

```kotlin
// 4K фотография (4096 x 3072 px) в формате ARGB_8888
val bitmapSizeBytes = 4096 * 3072 * 4  // 50MB на одно фото!

// Heap limit обычно 256MB
// = всего 5 таких фото и OutOfMemoryError
```

**Эволюция хранения Bitmap:**

```
Android версия     Где хранятся пиксели        Управление
────────────────────────────────────────────────────────────
< 8.0 (Oreo)      Native heap                 вручную (recycle)
≥ 8.0 (Oreo)      Graphics memory             автоматически (GC)
```

**Best practices для Bitmap:**

```kotlin
// 1. Downsampling: загружать только нужный размер
fun decodeSampledBitmap(file: File, reqWidth: Int, reqHeight: Int): Bitmap {
    return BitmapFactory.Options().run {
        inJustDecodeBounds = true
        BitmapFactory.decodeFile(file.path, this)

        // Рассчитать inSampleSize (2, 4, 8...)
        inSampleSize = calculateInSampleSize(this, reqWidth, reqHeight)

        inJustDecodeBounds = false
        BitmapFactory.decodeFile(file.path, this)
    }
}

// ImageView 200x200 загрузит фото 200x200, а не оригинал 4000x3000

// 2. Использовать Glide/Coil — они делают это автоматически
Glide.with(context)
    .load(imageUrl)
    .override(200, 200)  // Автоматический downsampling
    .into(imageView)

// 3. LRU Cache для переиспользования
val cache = LruCache<String, Bitmap>(maxMemory / 4)  // 25% heap
```

### LeakCanary: как читать отчёты

**Установка:**

```kotlin
// build.gradle
dependencies {
    debugImplementation 'com.squareup.leakcanary:leakcanary-android:2.12'
}
// Работает автоматически в debug builds
```

**Пример отчёта LeakCanary:**

```
┌─────────────────────────────────────────────────────────────────┐
│ LEAK DETECTED                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ MainActivity has leaked                                         │
│                                                                 │
│ Reference Path:                                                 │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │                                                          │   │
│ │  GC Root: Thread                                         │   │
│ │  │                                                       │   │
│ │  ├── Handler.mQueue                                     │   │
│ │  │   └── MessageQueue.mMessages                         │   │
│ │  │       └── Message.callback (Runnable)                │   │
│ │  │           └── MainActivity (LEAKED)                  │   │
│ │                                                          │   │
│ │  Причина: Handler.postDelayed() не отменён в onDestroy  │   │
│ │                                                          │   │
│ └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│ Retained Heap Size: 2.4 MB                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Как читать:**
1. **GC Root** — точка входа (Thread, Static field, etc)
2. **Reference Path** — цепочка ссылок от Root до утёкшего объекта
3. **LEAKED** — объект, который должен был быть собран GC
4. **Retained Heap Size** — сколько памяти не освобождается

**Типичные паттерны утечек:**

```
Паттерн                              Решение
────────────────────────────────────────────────────────────────
Handler → Runnable → Activity        removeCallbacks в onDestroy
Thread → Runnable → Activity         interrupt() в onDestroy
Listener → Activity                  unregister в onDestroy
Static → Activity                    использовать applicationContext
Singleton → Activity Context         использовать applicationContext
ViewModel → Activity                 НИКОГДА не храните Activity в VM!
```

### Large Heap: когда он нужен и его цена

**Запрос large heap:**

```xml
<!-- AndroidManifest.xml -->
<application
    android:largeHeap="true"
    ...>
```

```kotlin
// Результат:
val am = getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
println("Normal: ${am.memoryClass}MB")        // 256MB
println("Large: ${am.largeMemoryClass}MB")    // 512MB
```

**Когда использовать large heap:**
- Фоторедакторы (обработка больших изображений)
- Приложения для работы с PDF
- Видео/аудио редакторы
- Приложения с heavy 3D graphics

**Цена large heap:**

```
Последствие                         Почему это плохо
────────────────────────────────────────────────────────────────
GC паузы дольше                     Больше heap = дольше сканировать
LMK убивает агрессивнее             Ваш PSS выше → вы первый кандидат
Хуже на low-end устройствах         512MB на устройстве с 2GB RAM = проблема
Маскирует утечки памяти             Утечка в 100MB незаметна в 512MB heap
```

**Правило:** Large heap — это костыль. Сначала оптимизируйте потребление памяти (downsampling, кэши, освобождение ресурсов), и только если это не помогает — рассмотрите largeHeap.

**Альтернативы:**

```kotlin
// Вместо largeHeap используйте:
// 1. Aggressive downsampling
Glide.with(this)
    .load(largeImage)
    .downsample(DownsampleStrategy.AT_MOST)  // Не загружать больше чем нужно

// 2. Paging для списков
Pager(state = pagerState) {
    // Загружает страницы по мере прокрутки, выгружает старые
}

// 3. Disk cache вместо memory cache
val cache = DiskLruCache.open(cacheDir, 1, 1, 100 * 1024 * 1024)  // 100MB
```

---

## Распространённые утечки памяти

### 1. Static reference на Context

```kotlin
// ПЛОХО
object Singleton {
    lateinit var context: Context  // Activity context = утечка!
}

// ХОРОШО
object Singleton {
    lateinit var context: Context

    fun init(context: Context) {
        this.context = context.applicationContext  // Application context OK
    }
}
```

### 2. Inner class с reference на outer

```kotlin
// ПЛОХО: Handler держит implicit reference на Activity
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())

    fun startDelayedWork() {
        handler.postDelayed({
            // Этот Runnable держит reference на Activity
            updateUI()
        }, 60000)  // 60 секунд — Activity может уже умереть
    }
}

// ХОРОШО: WeakReference или отмена в onDestroy
class MyActivity : AppCompatActivity() {
    private val handler = Handler(Looper.getMainLooper())
    private val runnable = Runnable { updateUI() }

    override fun onDestroy() {
        handler.removeCallbacks(runnable)
        super.onDestroy()
    }
}
```

### 3. Listener не отписан

```kotlin
// ПЛОХО
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        EventBus.subscribe(this)  // Подписка
        // Где отписка?
    }
}

// ХОРОШО
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        EventBus.subscribe(this)
    }

    override fun onDestroyView() {
        EventBus.unsubscribe(this)
        super.onDestroyView()
    }
}
```

---

## Чеклист оптимизации памяти

```
□ Использовать Application context для singleton'ов
□ Отписываться от listeners в onDestroy/onDestroyView
□ Не создавать объекты в onDraw/onBindViewHolder
□ Использовать RecyclerView вместо ScrollView со списками
□ Bitmap: inSampleSize для downscaling, recycle() когда не нужен
□ Кэши: ограничивать размер, очищать в onTrimMemory
□ Реагировать на onTrimMemory callbacks
□ Тестировать process death
□ Использовать LeakCanary в debug builds
```

---

## Проверь себя

Эти вопросы помогут закрепить понимание управления памятью в Android:

1. **Как LMK (Low Memory Killer) решает какой процесс убить?**
   <details>
   <summary>Показать ответ</summary>

   LMK использует два фактора:
   - **OOM adjustment** (приоритет) — чем выше число, тем менее важен процесс
   - **Уровень свободной памяти** — разные пороги для разных категорий

   Алгоритм:
   1. Проверяет свободную память
   2. Определяет порог (например, < 60% = убивать CACHED)
   3. Находит процессы с OOM_ADJ выше порога
   4. Убивает процесс с наибольшим OOM_ADJ (наименее важный)
   5. Повторяет пока память не освободится

   Отличие от Linux OOM Killer: LMK действует проактивно (до исчерпания памяти), Linux OOM — реактивно (когда память уже закончилась).
   </details>

2. **Почему Activity нельзя хранить в static переменной?**
   <details>
   <summary>Показать ответ</summary>

   Activity — это тяжёлый объект, который должен уничтожаться при закрытии:

   **Что держит Activity:**
   - Весь View hierarchy (все UI виджеты)
   - Context с Resources
   - Theme, Configuration
   - Window, WindowManager

   **Размер:** 1 Activity ≈ 5-10 MB в памяти

   **Проблема static:**
   - Static живёт пока жив процесс
   - При повороте экрана создаётся НОВАЯ Activity
   - Старая Activity остаётся в памяти (через static)
   - После 5 поворотов = 50MB утекло
   - После 20 поворотов = OutOfMemoryError

   **Решение:** Использовать `applicationContext` для singleton'ов или `WeakReference` если нужна именно Activity.
   </details>

3. **Что такое PSS, USS, RSS и какой показатель важнее?**
   <details>
   <summary>Показать ответ</summary>

   **RSS (Resident Set Size):**
   - Вся память в RAM, включая shared
   - Проблема: shared библиотеки считаются полностью для каждого процесса
   - Пример: если framework занимает 50MB и используется 10 приложениями, RSS покажет 500MB

   **PSS (Proportional Set Size):**
   - Shared память делится пропорционально между процессами
   - Формула: `PSS = USS + (Shared / количество процессов)`
   - Пример: framework 50MB / 10 процессов = 5MB на процесс
   - **Это главный показатель для Android**

   **USS (Unique Set Size):**
   - Только уникальная память процесса
   - Shared библиотеки не учитываются
   - Показывает сколько освободится при убийстве процесса

   **Какой важнее:**
   - **PSS** — для понимания реального потребления памяти
   - **USS** — для оценки эффекта от освобождения процесса
   - RSS игнорируйте для Android (искажает картину)

   LMK принимает решения на основе PSS.
   </details>

4. **Как Android экономит память при fork() через Zygote?**
   <details>
   <summary>Показать ответ</summary>

   **Zygote pattern:**
   ```
   1. При загрузке системы стартует Zygote процесс
   2. Zygote загружает весь Android Framework в память
   3. Для запуска приложения — Zygote делает fork()
   4. Дочерний процесс наследует всю память родителя
   ```

   **Copy-on-Write (COW):**
   - После fork() память **не копируется физически**
   - Родитель и потомок указывают на одни и те же страницы памяти
   - Страницы помечены read-only
   - При попытке записи → page fault → копируется только эта страница

   **Экономия:**
   - Framework код: ~30-50MB shared между всеми приложениями
   - Без Zygote: каждое приложение загружало бы свою копию
   - 100 приложений × 50MB = 5GB вместо 50MB

   **Также ускоряет запуск:**
   - Без Zygote: загрузка Framework ~1-2 секунды
   - С Zygote: fork() ~10-50ms

   Подробнее: [[android-architecture]] — раздел про Zygote
   </details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Task killers улучшают производительность" | Task killers вредят. Система лучше знает что убивать. Очищенные apps перезапускаются, тратя больше battery. LMK оптимизирован |
| "Больше RAM = быстрее приложение" | До определённого предела. После 512MB heap мало влияет на обычные apps. GC pause важнее чем heap size |
| "GC = freeze на 50ms" | ART Concurrent Copying GC имеет паузы 1-5ms. Старый Dalvik — да, до 200ms. ART оптимизирован для low latency |
| "Memory leak = OOM crash" | Не сразу. LMK убьёт background apps раньше. Но leak сокращает "буфер" для foreground. Prolonged leak → ANR |
| "Zygote тратит память зря" | Наоборот, Zygote экономит память. Fork + COW = все apps разделяют Framework code. Без Zygote каждый app загружал бы свой |
| "USS = реальное потребление" | USS показывает private память. PSS — реальный вклад с учётом shared. LMK использует PSS |
| "Bitmap на 10MB = 10MB RAM" | Bitmap может быть в GPU memory (hardware bitmap). С Android 8+ большие bitmaps не occupate heap напрямую |
| "onTrimMemory = process death скоро" | onTrimMemory — предупреждение, не приговор. Система даёт шанс освободить кэши. Правильная реакция = меньше шанс death |
| "WeakReference решает все leaks" | WeakReference для caches, не для leak fix. Leak = неправильная архитектура. WeakRef маскирует проблему |
| "Мониторинг памяти замедляет app" | LeakCanary/MAT — dev tools, не production. В release сборках мониторинг отключён. Overhead минимальный |

---

## CS-фундамент

| CS-концепция | Как применяется в Memory Management |
|--------------|-------------------------------------|
| **Virtual Memory** | Каждый процесс имеет своё виртуальное адресное пространство. MMU транслирует virtual → physical. Изоляция процессов |
| **Copy-on-Write (COW)** | Fork от Zygote не копирует память. Pages shared пока не модифицированы. Экономия 10x при 100+ apps |
| **Garbage Collection** | ART Concurrent Copying GC. Tri-color marking. Concurrent evacuation. Паузы 1-5ms vs 50-200ms в Dalvik |
| **Memory Mapping (mmap)** | DEX/OAT файлы mapped в memory. Shared между процессами. Lazy loading страниц |
| **Page Replacement** | LRU для file-backed pages. Anonymous pages (heap) = primary target для LMK. kswapd для async reclaim |
| **OOM Killer vs LMK** | Linux OOM Killer — последняя мера. Android LMK — проактивный, убивает раньше по приоритету процессов |
| **Memory Pressure Signals** | onTrimMemory callbacks. PSI (Pressure Stall Information) для system-wide monitoring. cgroups для limits |
| **Reference Counting** | Не используется в ART (циклические ссылки). Но используется в Binder для IPC объектов |
| **Memory Fragmentation** | Concurrent Copying GC compacts heap. Нет fragmentation после collection. Allocation всегда O(1) bump pointer |
| **Process Priority** | ADJ (Adjustment) score. Foreground=0, Visible=100, Service=200, Background=700. LMK targets высокий ADJ |

---

## Связи

**Android раздел:**
→ [[android-overview]] — карта раздела Android
→ [[android-architecture]] — Zygote использует fork() для экономии памяти через Copy-on-Write, все приложения разделяют код Framework
→ [[android-activity-lifecycle]] — Process death происходит при нехватке памяти, savedInstanceState критичен для восстановления

**JVM/Runtime:**
→ [[jvm-gc-tuning]] — ART использует Concurrent Copying GC оптимизированный для низких пауз (2-5ms vs 50-200ms в JVM)
→ [[jvm-memory-model]] — понимание heap структуры и GC roots помогает находить утечки памяти

**Операционные системы:**
→ [[os-processes-threads]] — Android процессы = Linux процессы, один процесс на приложение для изоляции
→ [[os-memory-management]] — виртуальная память, Copy-on-Write при fork(), OOM Killer vs LMK

---

## Источники

- [Android Runtime and Dalvik - AOSP](https://source.android.com/docs/core/runtime) — управление памятью в ART
- [Manage Your App's Memory - Android Developers](https://developer.android.com/topic/performance/memory) — официальный гайд по памяти
- [Overview of Memory Management - Android Developers](https://developer.android.com/topic/performance/memory-overview) — обзор управления памятью

---

*Проверено: 2026-01-09 | На основе официальной документации Android и AOSP*
