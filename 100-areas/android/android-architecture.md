---
title: "Архитектура Android: от Linux до приложения"
created: 2025-12-17
modified: 2026-01-05
type: deep-dive
area: android
confidence: high
cs-foundations: [os-architecture, process-model, ipc-mechanisms, virtual-machine, memory-management, garbage-collection]
tags:
  - android
  - architecture
  - art
  - zygote
  - binder
related:
  - "[[android-overview]]"
  - "[[android-process-memory]]"
  - "[[android-activity-lifecycle]]"
  - "[[os-processes-threads]]"
  - "[[os-memory-management]]"
  - "[[jvm-basics-history]]"
  - "[[jvm-gc-tuning]]"
---

# Архитектура Android: от Linux до приложения

---

## Зачем это нужно (Проблема → Решение)

> **Проблема:** Как создать операционную систему для мобильных устройств, которая:
> - Запускает приложения мгновенно (не секунды, как JVM)
> - Экономит батарею (засыпает когда не нужна)
> - Изолирует приложения друг от друга (безопасность)
> - Работает на устройствах с 512MB RAM
> - Позволяет писать на Java/Kotlin (не на C/C++)
>
> **Решение:** Android — модифицированный Linux с собственным runtime (ART), уникальным IPC (Binder), и моделью быстрого запуска (Zygote).

Android — это не просто "Linux с Java". Это глубоко модифицированная система, где **каждый архитектурный выбор продиктован ограничениями мобильных устройств**. Понимание этой архитектуры объясняет:

- Почему Activity lifecycle такой сложный (система управляет процессами, не приложение)
- Почему приложения запускаются быстро (Zygote fork, не холодный старт JVM)
- Почему ANR происходит через 5 секунд (Main Thread = UI Thread)
- Почему приложение может быть "убито" в любой момент (Low Memory Killer)

**30-40% крашей в Android связаны с неправильным пониманием архитектуры** — особенно lifecycle и process death.

---

## Prerequisites (Что нужно знать)

| Тема | Зачем нужно | Где изучить |
|------|-------------|-------------|
| Процессы и потоки | Zygote использует fork(), каждое приложение = процесс | [[os-processes-threads]] |
| Виртуальная память | Copy-on-Write объясняет, как Zygote экономит RAM | [[os-memory-management]] |
| **CS: Process lifecycle** | Android управляет процессами как ОС | [[cs-operating-systems]] |
| **CS: IPC mechanisms** | Binder — это межпроцессная коммуникация | [[cs-ipc-mechanisms]] |
| JVM basics | ART — это альтернативная реализация VM | [[jvm-basics-history]] |
| Activity lifecycle | Следствие архитектуры процессов | [[android-activity-lifecycle]] |

---

## Терминология

| Термин | Что это | Аналогия из жизни |
|--------|---------|-------------------|
| **ART** | Android Runtime — среда выполнения Android-приложений | "Интерпретатор" для DEX-кода, как JVM для Java |
| **Dalvik** | Предшественник ART (до Android 5.0) | Устаревший "движок" — медленнее, только JIT |
| **DEX** | Dalvik Executable — формат байткода Android | "Язык" который понимает ART, оптимизирован для мобильных |
| **AOT** | Ahead-Of-Time compilation — компиляция при установке | Перевод книги заранее целиком |
| **JIT** | Just-In-Time compilation — компиляция во время выполнения | Синхронный переводчик — переводит по ходу |
| **Zygote** | Процесс-шаблон для fork() новых приложений | "Готовая заготовка" — клонируется для каждого приложения |
| **Binder** | Механизм межпроцессного взаимодействия Android | "Телефонная линия" между процессами с caller ID |
| **System Server** | Процесс с основными системными сервисами | "Мэрия города" — управляет всеми сервисами |
| **HAL** | Hardware Abstraction Layer — интерфейс к железу | "Переводчик" между Android и конкретным железом |
| **AIDL** | Android Interface Definition Language — описание Binder-интерфейсов | "Контракт" на языке Binder |
| **LMK** | Low Memory Killer — убивает процессы до нехватки памяти | "Превентивная чистка" — не ждёт кризиса |
| **Process death** | Убийство процесса системой | ОС "выселяет" приложение из памяти |
| **Copy-on-Write** | Память копируется только при записи | "Общая книга" — копия создаётся только если хочешь писать |

---

## Почему Android выбрал именно такую архитектуру?

Архитектура Android — это **ответ на ограничения мобильных устройств 2007 года**. Понимание этих ограничений объясняет каждое архитектурное решение.

### Проблема 1: Ограниченная память (256-512 MB RAM)

**Традиционный подход (Desktop):** Каждое приложение загружает всё что нужно. 10 приложений × 100MB = 1GB RAM.

**Решение Android — Zygote и fork():**
- Zygote загружает framework один раз (~50MB)
- Приложения клонируются от Zygote через fork()
- Copy-on-Write: код framework shared между всеми приложениями
- Результат: 10 приложений используют ~50MB (shared) + 10×20MB (private) = 250MB

### Проблема 2: Медленный запуск JVM (2-3 секунды)

**Традиционный подход:** Холодный старт JVM — загрузить VM, загрузить classloader, загрузить классы, инициализировать.

**Решение Android — Zygote:**
- При загрузке системы Zygote уже инициализирует ART
- Загружает ~8000 классов framework заранее
- fork() от Zygote = мгновенное копирование готового runtime
- Результат: запуск приложения за ~200ms вместо ~2000ms

### Проблема 3: Медленная межпроцессная коммуникация

**Традиционный IPC (sockets, pipes):** 2 копирования данных (user→kernel→user).

**Решение Android — Binder:**
- Только 1 копирование (напрямую в mmap-область получателя)
- Встроенная идентификация вызывающего (UID/PID)
- Оптимизирован для частых коротких сообщений
- Результат: ~10x быстрее для типичных Android вызовов

### Проблема 4: Нехватка памяти не должна "вешать" систему

**Традиционный OOM Killer:** Ждёт критической нехватки, потом убивает процесс. К этому моменту система уже тормозит.

**Решение Android — Low Memory Killer (LMK):**
- Превентивно убивает процессы ДО нехватки памяти
- Приоритеты: foreground > visible > service > cached > empty
- Система всегда остаётся отзывчивой
- Результат: плавный UX даже при нехватке памяти

### Проблема 5: Безопасность и изоляция приложений

**Традиционный подход (Desktop):** Все приложения запускаются от одного пользователя, могут читать память друг друга.

**Решение Android — Sandbox через Linux UID:**
- Каждое приложение = отдельный Linux user (UID)
- Файлы приложения принадлежат его UID
- Binder проверяет permissions на уровне ядра
- Результат: приложение не может читать данные другого приложения

```
┌─────────────────────────────────────────────────────────────────────┐
│                  АРХИТЕКТУРНЫЕ РЕШЕНИЯ ANDROID                       │
├─────────────────────────────────────────────────────────────────────┤
│ Проблема              │ Решение              │ Механизм             │
├───────────────────────┼──────────────────────┼──────────────────────┤
│ Мало RAM              │ Shared memory        │ Zygote + COW         │
│ Медленный запуск      │ Pre-initialized VM   │ fork() от Zygote     │
│ Медленный IPC         │ 1 копирование        │ Binder + mmap        │
│ Нехватка памяти       │ Превентивное kill    │ Low Memory Killer    │
│ Изоляция apps         │ Linux user sandbox   │ UID per app          │
│ Батарея               │ Засыпание            │ Wakelocks            │
└───────────────────────┴──────────────────────┴──────────────────────┘
```

---

## Слои архитектуры Android

```
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATIONS                                 │
│  Gmail, Chrome, Camera, ваше приложение                          │
├─────────────────────────────────────────────────────────────────┤
│                   APPLICATION FRAMEWORK                           │
│  ActivityManager, WindowManager, PackageManager, ContentProviders│
│  Notification, Telephony, Location, Resource Manager             │
├─────────────────────────────────────────────────────────────────┤
│                      ANDROID RUNTIME                              │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │ ART                  │  │ Core Libraries                   │   │
│  │ - DEX bytecode exec  │  │ - java.*, kotlin.*               │   │
│  │ - GC                 │  │ - android.*                      │   │
│  │ - AOT/JIT            │  │ - Kotlin stdlib                  │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│                   NATIVE LIBRARIES (C/C++)                        │
│  OpenGL ES, Media Framework, SQLite, WebKit, libc (Bionic)       │
├─────────────────────────────────────────────────────────────────┤
│                HARDWARE ABSTRACTION LAYER (HAL)                   │
│  Camera HAL, Audio HAL, Sensors HAL, Graphics HAL                │
├─────────────────────────────────────────────────────────────────┤
│                     LINUX KERNEL                                  │
│  Drivers: Display, Camera, Bluetooth, USB, WiFi                  │
│  + Binder IPC, Low Memory Killer, wakelocks, ashmem              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Linux Kernel: фундамент с модификациями

Android использует ядро Linux, но с важными дополнениями:

### Binder IPC — почему не стандартные механизмы Linux?

**Проблема:** Linux предоставляет множество IPC механизмов, но ни один не подходит для Android:

| Механизм | Проблема для мобильных |
|----------|------------------------|
| **Pipes** | Только parent-child, 2 копирования данных |
| **Sockets** | Overhead на сетевой стек, 2 копирования |
| **Shared memory** | Нет синхронизации, сложная безопасность |
| **Signals** | Слишком ограничены, только int |
| **Message queues** | 2 копирования, нет object references |

**Решение — Binder** — механизм, оптимизированный для Android:

```
┌─────────────────────────────────────────────────────────────────────┐
│              ТРАДИЦИОННЫЙ IPC vs BINDER                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Традиционный IPC (pipes, sockets) — 2 копирования:                 │
│                                                                     │
│  ┌─────────┐     copy_to_user    ┌─────────┐    copy_from_user     │
│  │ Process │─────────────────────│ Kernel  │────────────────────▶  │
│  │    A    │                     │  buffer │                       │
│  └─────────┘                     └─────────┘                       │
│                                       │                            │
│                                       ▼                            │
│                                  ┌─────────┐                       │
│                                  │ Process │                       │
│                                  │    B    │                       │
│                                  └─────────┘                       │
│                                                                     │
│  Binder IPC — 1 копирование через mmap:                            │
│                                                                     │
│  ┌─────────┐                    ┌──────────────────────────────┐   │
│  │ Process │   copy_from_user   │ Kernel                       │   │
│  │    A    │───────────────────▶│   │                          │   │
│  └─────────┘                    │   ▼                          │   │
│                                 │ mmap'd buffer ────────────▶  │   │
│                                 │ (mapped to B's address space)│   │
│                                 │                     │        │   │
│                                 └─────────────────────│────────┘   │
│                                                       │            │
│                                                       ▼            │
│                                                  ┌─────────┐       │
│                                                  │ Process │       │
│                                                  │    B    │       │
│                                                  └─────────┘       │
│                                                                     │
│  Результат: 50% меньше копирований = быстрее + меньше CPU          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Как работает Binder под капотом:**

```
Шаг 1: Регистрация сервиса
┌────────────────────────────────────────────────────────────────────┐
│ 1. System Server запускает ActivityManagerService                  │
│ 2. AMS регистрирует себя в ServiceManager:                         │
│    ServiceManager.addService("activity", ams)                      │
│ 3. ServiceManager записывает: "activity" → Binder handle 0x1234    │
└────────────────────────────────────────────────────────────────────┘

Шаг 2: Получение ссылки на сервис
┌────────────────────────────────────────────────────────────────────┐
│ 1. Приложение запрашивает сервис:                                  │
│    val am = getSystemService(ACTIVITY_SERVICE)                     │
│ 2. Context → ServiceManager.getService("activity")                 │
│ 3. ServiceManager возвращает Binder proxy (handle 0x1234)          │
│ 4. Приложение получает IBinder → приводит к IActivityManager       │
└────────────────────────────────────────────────────────────────────┘

Шаг 3: Вызов метода через Binder
┌────────────────────────────────────────────────────────────────────┐
│ 1. Приложение вызывает: am.getRunningAppProcesses()                │
│ 2. Proxy сериализует вызов в Parcel (method ID + args)             │
│ 3. Parcel отправляется в /dev/binder                               │
│ 4. Ядро копирует данные в mmap-область System Server               │
│ 5. System Server десериализует Parcel                              │
│ 6. Вызывается реальный метод в AMS                                 │
│ 7. Результат сериализуется и отправляется обратно                  │
│ 8. Приложение получает List<RunningAppProcessInfo>                 │
└────────────────────────────────────────────────────────────────────┘
```

**Ключевые возможности Binder:**

| Возможность | Как работает | Зачем нужно |
|-------------|--------------|-------------|
| **Caller identity** | UID/PID вызывающего проверяются ядром | Permissions нельзя подделать |
| **Death notification** | `linkToDeath()` — callback при смерти процесса | Cleanup при crash |
| **Reference counting** | Объекты удаляются когда нет ссылок | Автоматическое управление памятью |
| **Synchronous calls** | Вызывающий блокируется до ответа | Простая модель программирования |
| **Oneway calls** | Асинхронные вызовы без ответа | Для fire-and-forget операций |

**AIDL — Android Interface Definition Language:**

```kotlin
// IMyService.aidl — описание интерфейса
interface IMyService {
    // Синхронный вызов — вызывающий ждёт ответа
    String getData(int id);

    // Oneway — асинхронный, без ответа
    oneway void sendEvent(String event);
}

// Генерируется:
// - IMyService.Stub — для реализации сервиса
// - IMyService.Stub.Proxy — для клиента
```

```kotlin
// Реализация сервиса
class MyService : Service() {
    private val binder = object : IMyService.Stub() {
        override fun getData(id: Int): String {
            // Выполняется в Binder thread pool
            // Caller identity доступен:
            val callingUid = Binder.getCallingUid()
            val callingPid = Binder.getCallingPid()
            return "Data for $id from UID=$callingUid"
        }

        override fun sendEvent(event: String) {
            // Oneway — не блокирует вызывающего
            Log.d("MyService", "Event: $event")
        }
    }

    override fun onBind(intent: Intent): IBinder = binder
}

// Клиент
class MyClient {
    fun useService(context: Context) {
        val intent = Intent(context, MyService::class.java)
        context.bindService(intent, object : ServiceConnection {
            override fun onServiceConnected(name: ComponentName, service: IBinder) {
                // service — это Binder proxy
                val myService = IMyService.Stub.asInterface(service)

                // Этот вызов идёт через Binder IPC
                val data = myService.getData(42)
            }

            override fun onServiceDisconnected(name: ComponentName) {
                // Сервис умер — Binder уведомил
            }
        }, Context.BIND_AUTO_CREATE)
    }
}
```

### Low Memory Killer (LMK)

Стандартный OOM Killer в Linux срабатывает когда памяти уже нет. LMK более агрессивен — он начинает убивать процессы заранее, чтобы система оставалась отзывчивой.

```
Приоритеты процессов (от низкого к высокому):
┌─────────────────────────────────────────────────────────────────┐
│ Empty         │ Пустой процесс (кэширован)      │ Убивается первым │
│ Cached        │ Приложение в фоне               │                  │
│ Service       │ Сервис без UI                   │                  │
│ Home          │ Launcher                        │                  │
│ Perceptible   │ Видимый сервис (музыка)         │                  │
│ Visible       │ Видимое Activity                │                  │
│ Foreground    │ Активное Activity               │ Убивается последним │
│ System        │ Системные процессы              │ Не убивается      │
└─────────────────────────────────────────────────────────────────┘
```

Подробнее — в [[android-process-memory]].

### Wakelocks

Механизм предотвращения засыпания устройства. Когда все wakelocks отпущены, устройство может уснуть для экономии батареи.

```kotlin
// Получить wakelock (устройство не уснёт)
val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
val wakeLock = powerManager.newWakeLock(
    PowerManager.PARTIAL_WAKE_LOCK,
    "myapp:MyWakelockTag"
)

wakeLock.acquire(10 * 60 * 1000L)  // Максимум 10 минут
try {
    // Критическая работа
} finally {
    wakeLock.release()  // Всегда отпускать!
}
```

**Важно:** Неотпущенный wakelock = разряженная батарея пользователя. Android строго следит за этим и может убить приложение-нарушителя.

---

## ART: Android Runtime

ART — среда выполнения Android-приложений. Это не JVM, хотя выполняет похожую функцию.

### DEX vs Java Bytecode

JVM использует class files с Java bytecode. Android использует DEX (Dalvik Executable) — более компактный формат, оптимизированный для мобильных устройств.

```
Компиляция Java/Kotlin в Android:

.kt / .java ──▶ javac/kotlinc ──▶ .class (Java bytecode)
                                      │
                                      ▼
                                   d8/R8 ──▶ .dex (DEX bytecode)
                                      │
                                      ▼
                                   APK (ZIP с DEX, ресурсами, манифестом)
```

**Почему DEX, а не Java bytecode:**
- **Register-based** вместо stack-based — меньше инструкций для той же операции
- **Компактнее** — константы, строки, типы в единой таблице
- **Несколько классов в одном файле** — меньше I/O при загрузке

### AOT + JIT: гибридная компиляция

Dalvik (до Android 5.0) использовал только JIT — интерпретация + компиляция hot paths во время выполнения. Это давало быструю установку, но медленный первый запуск.

ART изначально использовал только AOT — полная компиляция при установке. Это давало быстрый запуск, но долгую установку и большой размер на диске.

**Современный ART (Android 7+)** использует Profile-Guided Compilation:

```
┌─────────────────────────────────────────────────────────────────┐
│                PROFILE-GUIDED COMPILATION                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Первый запуск:                                              │
│     - Интерпретация + JIT для hot code                          │
│     - Профиль использования сохраняется                         │
│                                                                 │
│  2. Фоновая компиляция (idle + charging):                       │
│     - AOT компиляция на основе профиля                          │
│     - Компилируется только часто используемый код               │
│                                                                 │
│  3. Последующие запуски:                                        │
│     - Hot code уже скомпилирован (AOT)                          │
│     - Cold code интерпретируется (экономия места)               │
│     - JIT для нового hot code                                   │
│                                                                 │
│  Результат: быстрая установка + быстрый запуск + меньше места   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Garbage Collection в ART

ART GC оптимизирован для мобильных устройств: маленькие паузы важнее throughput.

```
ART GC (Concurrent Copying):
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  1. Concurrent Mark (параллельно с приложением)                 │
│     - Находит все живые объекты                                 │
│     - Приложение работает                                       │
│                                                                 │
│  2. Concurrent Copy (параллельно с приложением)                 │
│     - Копирует живые объекты в новую область                    │
│     - Read barrier перенаправляет ссылки                        │
│                                                                 │
│  3. Короткая пауза (~2ms)                                       │
│     - Финализация, обновление roots                             │
│                                                                 │
│  Сравнение с JVM G1:                                            │
│  - ART: паузы 2-5ms, throughput 85%                             │
│  - G1:  паузы 50-200ms, throughput 90%                          │
│                                                                 │
│  Tradeoff: меньше пауз → больше CPU на GC                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

Подробнее о GC в JVM — в [[jvm-gc-tuning]].

---

## Zygote: почему приложения запускаются быстро

Запуск JVM-приложения с нуля — это секунды: загрузить VM, загрузить классы, инициализировать. На мобильном устройстве это неприемлемо.

### Идея Zygote

**Zygote** (зигота) — это процесс, который:
1. Запускается при загрузке системы
2. Инициализирует ART runtime
3. Загружает основные классы Android framework (~8000 классов)
4. Ждёт запросов на создание новых приложений

Когда нужно запустить приложение, система делает **fork()** от Zygote:

```
Загрузка системы:
┌─────────────────────────────────────────────────────────────────┐
│                           init                                    │
│                             │                                    │
│                             ▼                                    │
│                          Zygote                                  │
│                    (загружает ART, классы)                       │
│                    ┌────────┼────────┐                          │
│                    │        │        │                          │
│                    ▼        ▼        ▼                          │
│               System     App 1    App 2                          │
│               Server    (fork)   (fork)                          │
└─────────────────────────────────────────────────────────────────┘

fork() от Zygote:
- Копирует адресное пространство (COW — мгновенно)
- ART уже инициализирован
- Базовые классы уже загружены
- Нужно только загрузить код приложения

Результат: запуск приложения за ~200ms вместо ~2000ms
```

### Copy-on-Write и shared memory

fork() использует Copy-on-Write (см. [[os-processes-threads]]). Страницы памяти не копируются, пока процесс не попытается их изменить.

**Что это значит для Android:**
- Код framework (~50MB) shared между всеми приложениями
- Heap родительского Zygote read-only → shared
- Каждое приложение получает собственный heap только для своих объектов

```
Память после fork от Zygote:
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│  Zygote (parent)        App 1 (child)        App 2 (child)     │
│  ┌──────────────┐       ┌──────────────┐     ┌──────────────┐  │
│  │ ART code     │───────│ (shared)     │─────│ (shared)     │  │
│  │ Framework    │       │              │     │              │  │
│  │ classes      │       │              │     │              │  │
│  ├──────────────┤       ├──────────────┤     ├──────────────┤  │
│  │ Zygote heap  │       │ App 1 heap   │     │ App 2 heap   │  │
│  │ (read-only)  │       │ (own copy)   │     │ (own copy)   │  │
│  └──────────────┘       └──────────────┘     └──────────────┘  │
│                                                                 │
│  RAM использование: ~50MB shared + ~20MB per app                │
│  Без Zygote было бы: ~70MB × N apps                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## System Server: мозг Android

System Server — это процесс, запускаемый первым от Zygote. Он содержит все основные системные сервисы:

| Сервис | Ответственность |
|--------|-----------------|
| **ActivityManagerService (AMS)** | Жизненный цикл Activities, процессов |
| **WindowManagerService (WMS)** | Управление окнами, input events |
| **PackageManagerService (PMS)** | Установка, разрешения, интенты |
| **PowerManagerService** | Wakelocks, состояние экрана |
| **NotificationManagerService** | Уведомления |
| **LocationManagerService** | GPS, геолокация |

Приложения общаются с сервисами через Binder:

```kotlin
// Получить системный сервис через Context
// Context использует Binder под капотом
val activityManager = getSystemService(Context.ACTIVITY_SERVICE)
    as ActivityManager

// Это вызов через Binder к ActivityManagerService в System Server
val runningApps = activityManager.runningAppProcesses
```

---

## Как запускается приложение

```
1. Пользователь тапает иконку
         │
         ▼
2. Launcher отправляет Intent в ActivityManagerService (Binder IPC)
         │
         ▼
3. AMS проверяет: процесс приложения существует?
         │
         ├── Да ──▶ Отправить Intent в существующий процесс
         │
         └── Нет ──▶ 4. AMS просит Zygote fork() новый процесс
                           │
                           ▼
                    5. Zygote делает fork()
                           │
                           ▼
                    6. Новый процесс:
                       - Загружает APK
                       - Создаёт Application object
                       - Вызывает Application.onCreate()
                           │
                           ▼
                    7. AMS отправляет Intent для создания Activity
                           │
                           ▼
                    8. Activity создаётся:
                       - onCreate()
                       - onStart()
                       - onResume()
                       - Первый кадр отрисовывается
```

**Cold start** (~500ms+): Шаги 4-8
**Warm start** (~200ms): Процесс жив, но Activity уничтожена (шаги 7-8)
**Hot start** (~50ms): Activity в памяти (только шаг 8, resume)

---

## Что важно для разработчика

### 1. Каждое приложение = отдельный процесс

```
Следствия:
- Crash одного приложения не роняет другие
- Память изолирована (нельзя читать память другого приложения)
- Коммуникация только через IPC (Intent, Binder, ContentProvider)
- Система может убить процесс в любой момент
```

### 2. Main Thread = UI Thread

Каждое приложение имеет Main Thread, он же UI Thread. Этот поток:
- Обрабатывает UI events (тапы, скроллы)
- Рендерит View
- Получает callbacks жизненного цикла

**Блокировка Main Thread >5 секунд = ANR (Application Not Responding)**.

Подробнее — в [[android-threading]].

### 3. Не полагайтесь на живучесть процесса

```kotlin
// Плохо: данные пропадут при убийстве процесса
class MyActivity : AppCompatActivity() {
    private var importantData: String = ""  // Пропадёт!
}

// Хорошо: сохранять состояние
class MyActivity : AppCompatActivity() {
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("data", importantData)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        importantData = savedInstanceState?.getString("data") ?: ""
    }
}
```

---

## Команды для отладки

```bash
# Информация о процессах
adb shell dumpsys activity processes

# Информация о памяти приложения
adb shell dumpsys meminfo <package>

# Системные сервисы
adb shell service list

# Информация о Zygote
adb shell ps | grep zygote

# Binder транзакции
adb shell dumpsys binder_transactions
```

---

## Проверь себя

1. **Зачем Android использует Binder вместо стандартных IPC-механизмов Linux?**
   <details>
   <summary>Показать ответ</summary>

   Binder оптимизирован для мобильной среды с частыми короткими сообщениями. В отличие от традиционных IPC (pipes, sockets), Binder делает только одно копирование данных (напрямую в mmap-область получателя), а также предоставляет встроенную идентификацию вызывающего (UID/PID) и управление жизненным циклом объектов.
   </details>

2. **Почему приложения Android запускаются быстрее, чем обычные JVM-приложения?**
   <details>
   <summary>Показать ответ</summary>

   Благодаря Zygote — процессу-шаблону, который при загрузке системы инициализирует ART и загружает базовые классы framework (~8000 классов). Когда нужно запустить приложение, система делает fork() от Zygote, получая готовый runtime за ~200ms вместо ~2000ms. Copy-on-Write позволяет shared код framework между всеми приложениями.
   </details>

3. **В чём разница между AOT и JIT компиляцией в ART?**
   <details>
   <summary>Показать ответ</summary>

   AOT (Ahead-Of-Time) компилирует код при установке, давая быстрый запуск но долгую установку. JIT (Just-In-Time) компилирует во время выполнения, давая быструю установку но медленный первый запуск. Современный ART (Android 7+) использует Profile-Guided Compilation: первый запуск с JIT создаёт профиль, затем фоновая AOT компилирует только hot code, давая лучшее из обоих миров.
   </details>

4. **Почему Low Memory Killer убивает приложения, когда память ещё есть?**
   <details>
   <summary>Показать ответ</summary>

   LMK более агрессивен чем стандартный OOM Killer, чтобы система оставалась отзывчивой. Он начинает убивать процессы заранее (starting с Empty/Cached), не дожидаясь критической нехватки памяти. Это предотвращает зависания и даёт пользователю лучший опыт, так как мобильные устройства имеют ограниченную RAM.
   </details>

---

## Мифы и заблуждения

| Миф | Реальность |
|-----|-----------|
| "Android — это просто Linux с Java" | Android глубоко модифицирован: свой runtime (ART вместо JVM), свой IPC (Binder вместо sockets), свой запуск приложений (Zygote fork вместо холодного старта). Только ядро Linux, и то с патчами (LMK, wakelocks, binder driver). |
| "Мой код контролирует lifecycle Activity" | **Система контролирует lifecycle.** Android может убить процесс в любой момент для освобождения памяти. onDestroy() может не вызваться. Приложение должно быть готово к пересозданию в любой момент. |
| "ViewModel сохраняет данные навсегда" | ViewModel **не переживает process death**. Выживает только config changes (rotation) через ViewModelStore. Для сохранения при process death нужен SavedStateHandle или persistent storage. |
| "onDestroy() всегда вызывается" | **Не гарантируется.** При process death (LMK убивает процесс) onDestroy() не вызывается — процесс просто исчезает. Нельзя полагаться на onDestroy() для сохранения критических данных. |
| "JIT быстрее AOT" | **Зависит от сценария.** JIT быстрее устанавливает, AOT быстрее запускает. Современный ART использует гибридный подход: JIT для первого запуска, AOT для hot code в фоне. Profile-Guided Compilation даёт лучшее из обоих миров. |
| "Binder — это просто RPC" | Binder — полноценный объектный IPC с identity verification, death notifications, reference counting. Caller UID/PID проверяются ядром — permissions нельзя подделать на уровне приложения. |
| "Task killers улучшают производительность" | **Вредят.** Android сам оптимально управляет памятью через LMK. Убийство cached процессов заставляет их перезапускаться = больше CPU, больше батареи, медленнее запуск. LMK убьёт их когда действительно нужна память. |
| "Приложения работают изолированно" | Изоляция есть (UID sandbox), но коммуникация постоянна: Intent, ContentProvider, Binder services. Приложение ~50% времени общается с системными сервисами через Binder IPC. |
| "GC в ART как в JVM" | ART GC оптимизирован для мобильных: короткие паузы (~2ms) важнее throughput. Concurrent Copying GC с read barriers. JVM G1 имеет паузы 50-200ms но выше throughput — разные trade-offs для разных платформ. |
| "32-bit Android устарел" | В 2025 Google требует 64-bit APK, но 32-bit ABI всё ещё поддерживается для legacy devices. ART поддерживает оба режима. Play Store требует arm64-v8a, но armeabi-v7a можно включать дополнительно. |

---

## CS-фундамент

| CS-концепция | Применение в архитектуре Android |
|--------------|----------------------------------|
| **Process isolation** | Каждое приложение = отдельный Linux процесс. Crash одного не роняет другие. Память изолирована — приложение не может читать память другого. UID sandbox добавляет уровень безопасности. |
| **fork() и Copy-on-Write** | Zygote использует fork() для создания приложений. COW означает, что страницы памяти не копируются пока процесс не попытается их изменить. ~50MB framework code shared между всеми приложениями. |
| **Inter-Process Communication** | Binder — специализированный IPC для Android. Одно копирование через mmap (vs 2 для sockets). Object references, death notifications, caller identity — всё встроено. |
| **Memory Management** | Low Memory Killer превентивно освобождает память. OOM Adjuster назначает приоритеты процессам. Foreground > Visible > Service > Cached > Empty. Система всегда отзывчива. |
| **Virtual Machine** | ART — register-based VM (vs stack-based JVM). DEX bytecode компактнее Java bytecode. AOT+JIT hybrid compilation оптимизирует и установку, и запуск. |
| **Garbage Collection** | Concurrent Copying GC с read barriers. Приоритет на короткие паузы (~2ms), не throughput. Generational collection, large object space, compact heap. |
| **State Machine** | Activity lifecycle — это state machine управляемый системой. Transitions: CREATED→STARTED→RESUMED→PAUSED→STOPPED→DESTROYED. Система триггерит transitions, не приложение. |
| **Serialization** | Parcel — бинарный формат для Binder IPC. Intent extras, savedInstanceState, AIDL — всё сериализуется в Parcel. Bundle ограничен 1MB. Parcelable быстрее Serializable. |
| **Sandbox security model** | Каждое приложение получает уникальный UID при установке. Файлы принадлежат этому UID. Permissions проверяются на уровне ядра через Binder. SELinux добавляет mandatory access control. |
| **Shared libraries** | Android framework загружается один раз в Zygote и shared между всеми приложениями через COW. Native libraries (.so) тоже могут быть shared. Экономия RAM на устройствах с ограниченной памятью. |

---

## Куда дальше (Навигация)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    LEARNING PATH                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  → Если новичок в Android:                                          │
│    [[android-overview]] — карта раздела, с чего начать              │
│    [[android-activity-lifecycle]] — lifecycle как следствие         │
│                                     архитектуры процессов           │
│                                                                     │
│  → Если хочешь глубже понять память:                                │
│    [[android-process-memory]] — как LMK управляет процессами        │
│    [[os-memory-management]] — виртуальная память, paging            │
│    [[jvm-gc-tuning]] — сравнение GC в ART и JVM                     │
│                                                                     │
│  → Если хочешь понять threading:                                    │
│    [[android-threading]] — Main Thread, Handler, Looper             │
│    [[android-handler-looper]] — механизм сообщений под капотом      │
│    [[os-processes-threads]] — процессы vs потоки                    │
│                                                                     │
│  → Если интересует runtime:                                         │
│    [[jvm-basics-history]] — почему Android создал ART               │
│    [[android-compilation-pipeline]] — как код становится APK        │
│    [[jvm-virtual-machine-concept]] — register vs stack based VM     │
│                                                                     │
│  → Смежные темы:                                                    │
│    [[android-app-components]] — Activity, Service, Receiver         │
│    [[android-manifest]] — декларация компонентов                    │
│    [[android-permissions-security]] — как работают permissions      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Связи

### Фундамент
**Необходимые концепции ОС для понимания архитектуры Android:**
- [[os-processes-threads]] — процессы, потоки и fork() лежат в основе модели Zygote
- [[os-memory-management]] — виртуальная память и COW объясняют, как Zygote экономит RAM

### Контекст Android
**Как архитектура влияет на разработку:**
- [[android-overview]] — карта раздела и общая картина платформы
- [[android-process-memory]] — как LMK и OOM Adjuster управляют жизненным циклом
- [[android-threading]] — почему Main Thread = UI Thread из-за архитектуры
- [[android-activity-lifecycle]] — lifecycle как следствие архитектуры процессов

### Сравнение с JVM
**Понимание отличий ART от классической JVM:**
- [[jvm-basics-history]] — почему Android создал свой runtime вместо использования JVM
- [[jvm-gc-tuning]] — как GC в ART оптимизирован для мобильных устройств (короткие паузы)
- [[jvm-virtual-machine-concept]] — концепция виртуальной машины и отличия register-based от stack-based

---

## Источники

- [Android Runtime and Dalvik - AOSP](https://source.android.com/docs/core/runtime) — официальная документация ART
- [Platform Architecture - Android Developers](https://developer.android.com/guide/platform) — архитектура платформы
- [ART JIT Compiler - AOSP](https://source.android.com/docs/core/runtime/jit-compiler) — JIT компилятор
- [Configure ART - AOSP](https://source.android.com/docs/core/runtime/configure) — конфигурация ART
- [Binder IPC - Android Open Source](https://source.android.com/docs/core/architecture/hidl/binder-ipc) — Binder internals
- [Understanding ViewModel Persistence - droidcon](https://www.droidcon.com/2025/01/13/understanding-viewmodel-persistence-across-configuration-changes-in-android/) — ViewModel и process death

---

*Проверено: 2026-01-09 | На основе официальной документации AOSP и deep research*
