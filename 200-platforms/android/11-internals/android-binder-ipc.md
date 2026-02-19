---
title: "Binder IPC: межпроцессная коммуникация Android под капотом"
created: 2026-02-19
modified: 2026-02-19
type: deep-dive
area: android
confidence: high
tags:
  - topic/android
  - topic/binder
  - topic/ipc
  - topic/internals
  - type/deep-dive
  - level/expert
related:
  - "[[android-service-internals]]"
  - "[[android-intent-internals]]"
  - "[[android-window-system]]"
  - "[[android-notifications]]"
  - "[[android-system-services]]"
  - "[[android-kernel-extensions]]"
  - "[[android-bundle-parcelable]]"
  - "[[android-context-internals]]"
  - "[[android-activitythread-internals]]"
  - "[[android-boot-process]]"
  - "[[android-architecture]]"
  - "[[os-processes-threads]]"
cs-foundations: [ipc-mechanisms, client-server, proxy-pattern, memory-mapping, reference-counting, capability-security, serialization]
prerequisites:
  - "[[android-architecture]]"
  - "[[os-processes-threads]]"
  - "[[os-memory-management]]"
reading_time: 110
difficulty: 9
study_status: not_started
mastery: 0
last_reviewed:
next_review:
---

# Binder IPC: межпроцессная коммуникация Android под капотом

> В 2005 году команда Android выбирала механизм IPC для новой мобильной ОС. Unix sockets? Два копирования данных и нет идентификации вызывающего. D-Bus? Тяжёлый, string-based, спроектирован для десктопа. Shared memory? Нет синхронизации и безопасности. Решение нашлось в наследии компании Be Inc — **OpenBinder**, созданный Dieter Bohn для BeOS ещё в 2001 году. Google нанял ключевых разработчиков и адаптировал Binder для мобильного мира. Сегодня **каждое нажатие на экран Android генерирует 10-50 Binder-транзакций** — от `startActivity()` до отрисовки уведомления.

---

## Зачем это нужно

### Проблема: Binder — невидимый фундамент, ломающий приложения

| Симптом | Причина | Последствия |
|---------|---------|-------------|
| `TransactionTooLargeException` | Передача >1MB данных через Binder | Crash при передаче больших Bitmap, коллекций, savedInstanceState |
| ANR (Application Not Responding) | Синхронный Binder-вызов на Main Thread к перегруженному сервису | Приложение зависает, пользователь видит диалог |
| `DeadObjectException` | Удалённый процесс умер, IBinder-ссылка устарела | Crash при вызове метода на мёртвом сервисе |
| Binder thread pool exhaustion | Все 16 Binder-потоков заняты синхронными вызовами | Deadlock: ни один запрос не обрабатывается |
| `SecurityException` | Неправильная проверка permissions вызывающего | Crash или уязвимость безопасности |
| Утечки ServiceConnection | bindService() без unbindService() | Memory leak, Service живёт бесконечно |
| Медленный IPC | Передача данных через Parcel вместо shared memory | Низкая производительность для больших объёмов данных |

### Актуальность (2024-2026)

**Масштаб использования Binder:**

```
КАЖДОЕ ДЕЙСТВИЕ ПОЛЬЗОВАТЕЛЯ = Binder-транзакции:

Нажатие на иконку приложения:
  Launcher → AMS (startActivity)         = 1 транзакция
  AMS → Zygote (fork process)            = 1 транзакция (socket, не Binder)
  AMS → новый процесс (scheduleLaunch)   = 1 транзакция
  Процесс → WMS (addWindow)             = 1 транзакция
  WMS → SurfaceFlinger (createSurface)   = 1 транзакция
  Итого: ~5-10 Binder-транзакций

Отправка уведомления:
  App → NotificationManagerService       = 1 транзакция
  NMS → RankingHelper                    = 1-3 транзакции
  NMS → SystemUI (notify)               = 1 транзакция
  SystemUI → WMS (updateWindow)          = 1 транзакция
  Итого: ~5-8 Binder-транзакций
```

**Статистика:**
- `adb shell dumpsys binder_stats` показывает **тысячи** транзакций в секунду на активном устройстве
- Binder driver в AOSP: `drivers/android/binder.c` — **~6500 строк** C-кода в ядре
- libbinder (native): **~30 000 строк** C++
- Каждый процесс Android имеет **mmap-буфер** размером до 1 MB для приёма Binder-данных

---

## Терминология

| Термин | Что это | Аналогия |
|--------|---------|----------|
| **IBinder** | Базовый интерфейс для объектов, доступных через Binder | "Паспорт" объекта для IPC |
| **Binder** | Серверная реализация IBinder (Java-класс `android.os.Binder`) | "Служащий за стойкой" — обрабатывает запросы |
| **BinderProxy** | Клиентская прокси к удалённому Binder-объекту | "Телефонная трубка" — звоним служащему |
| **Parcel** | Контейнер бинарной сериализации для IPC | "Посылка" с данными между процессами |
| **AIDL** | Android Interface Definition Language — описание Binder-интерфейсов | "Контракт" между клиентом и сервером |
| **ServiceManager** | Реестр системных сервисов (handle 0) | "Справочная служба" — по имени находит сервис |
| **/dev/binder** | Файл устройства для взаимодействия с Binder-драйвером | "Почтовое отделение" в ядре |
| **BC_TRANSACTION** | Команда: отправить транзакцию | "Отправить письмо" |
| **BR_REPLY** | Ответ: результат транзакции | "Получить ответ" |
| **mmap** | Memory-mapped I/O — разделяемая память между ядром и процессом | "Общий почтовый ящик" |
| **oneway** | Асинхронный вызов без ожидания ответа | "Отправить SMS и не ждать ответа" |
| **linkToDeath** | Подписка на уведомление о смерти удалённого процесса | "Уведомить, если абонент отключился" |
| **Binder token** | IBinder-ссылка как capability — владение = право доступа | "Ключ от комнаты" |

---

## Историческая справка: от OpenBinder к Android

### Timeline

```
2001 ──── Be Inc: Dieter Bohn создаёт OpenBinder для BeOS
           │  Объектно-ориентированный IPC с reference counting
           │  и capability-based security
           │
2002 ──── PalmSource покупает Be Inc
           │  OpenBinder используется в Cobalt OS (PalmOS 6)
           │  Но Cobalt так и не вышел на рынок
           │
2005 ──── Google основывает Android Inc
           │  Нанимает ключевых разработчиков OpenBinder
           │  Адаптирует Binder для Linux kernel module
           │
2008 ──── Android 1.0 выходит с Binder как единственным IPC
           │  Binder driver в staging tree Linux kernel
           │
2010 ──── Greg Kroah-Hartman удаляет Android код из staging
           │  "Android не использует стандартные Linux API"
           │  Binder продолжает жить как out-of-tree модуль
           │
2015 ──── Binder принят в mainline Linux kernel (v4.1+)
           │  После долгих переговоров и рефакторинга
           │
2017 ──── Project Treble: три домена Binder
           │  /dev/binder (framework)
           │  /dev/hwbinder (HAL)
           │  /dev/vndbinder (vendor)
           │
2020 ──── Все основные Android kernel патчи в mainline
           │
2024 ──── Binder остаётся единственным IPC в Android
           Никаких альтернатив не планируется
```

### Почему не стандартные Linux IPC?

| Механизм | Копирований | Caller ID | Sync/Async | Ref counting | Проблема для Android |
|----------|-------------|-----------|------------|-------------|---------------------|
| **Unix sockets** | 2 (user→kernel→user) | Нет (опционально через SCM_CREDENTIALS) | Оба | Нет | Медленно, нет безопасности |
| **Pipes** | 2 | Нет | Только sync | Нет | Только однонаправленные |
| **System V SHM** | 0 (shared) | Нет | Нет (нужна синхронизация) | Нет | Нет синхронизации, clumsy API |
| **D-Bus** | 2+ | Да (через daemon) | Оба | Нет | Тяжёлый: XML, string-based, daemon |
| **Binder** | **1** (user→mmap) | **Да (kernel-level)** | **Оба** | **Да** | — |

```
Традиционный IPC (2 копирования):
┌──────────┐    copy_from_user()    ┌──────────┐    copy_to_user()    ┌──────────┐
│  Sender  │ ──────────────────►    │  Kernel  │ ──────────────────►  │ Receiver │
│ (user)   │                        │  buffer  │                      │ (user)   │
└──────────┘                        └──────────┘                      └──────────┘

Binder IPC (1 копирование через mmap):
┌──────────┐    copy_from_user()    ┌──────────────────────────────────────────┐
│  Sender  │ ──────────────────►    │  Kernel buffer                           │
│ (user)   │                        │  ↕ mmap (memory-mapped)                  │
└──────────┘                        │  ↓                                       │
                                    │  Receiver видит данные напрямую          │
                                    │  через mmap-область (без копирования)    │
                                    └──────────────────────────────────────────┘
```

**Почему 1 копирование важно:**
- Типичная Binder-транзакция: 100-500 байт (Intent extras, lifecycle commands)
- Тысячи транзакций в секунду
- Экономия ~50% CPU на копирование ≈ существенная экономия батареи

---

## Архитектура Binder: три уровня

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                                 │
│                                                                         │
│  ┌─────────────┐          ┌─────────────┐          ┌────────────────┐  │
│  │  Client App │          │   AIDL       │          │  Server App    │  │
│  │             │          │  Interface   │          │  (Service)     │  │
│  │  proxy.     │          │              │          │  impl.         │  │
│  │  method()   │          │              │          │  method()      │  │
│  └──────┬──────┘          └──────────────┘          └───────▲────────┘  │
│         │                                                    │          │
├─────────┼────────────────────────────────────────────────────┼──────────┤
│         │            JAVA/KOTLIN FRAMEWORK LAYER             │          │
│         │                                                    │          │
│  ┌──────▼──────┐                                    ┌───────┴────────┐ │
│  │ BinderProxy │    transact(code, data, reply, 0)  │ Binder (Stub)  │ │
│  │             │ ──────────────────────────────────► │ onTransact()   │ │
│  └──────┬──────┘                                    └───────▲────────┘ │
│         │                    JNI                             │          │
├─────────┼────────────────────────────────────────────────────┼──────────┤
│         │              NATIVE LAYER (libbinder)              │          │
│         │                                                    │          │
│  ┌──────▼──────┐                                    ┌───────┴────────┐ │
│  │  BpBinder   │                                    │    BBinder     │ │
│  │  (proxy)    │                                    │    (stub)      │ │
│  └──────┬──────┘                                    └───────▲────────┘ │
│         │                                                    │          │
│  ┌──────▼──────────────────────────────────────────────────▲────────┐  │
│  │              IPCThreadState (per-thread)                          │  │
│  │  writeTransactionData() ───► ioctl() ◄─── executeCommand()       │  │
│  └──────────────────────────────┬───────────────────────────────────┘  │
│         │                       │                            │          │
│  ┌──────▼───────────────────────▼────────────────────────────▼──────┐  │
│  │              ProcessState (per-process, singleton)                │  │
│  │  open("/dev/binder") + mmap(1MB)                                 │  │
│  └──────────────────────────────┬───────────────────────────────────┘  │
│                                 │                                       │
├─────────────────────────────────┼───────────────────────────────────────┤
│                                 │    KERNEL LAYER                       │
│                          ┌──────▼──────┐                                │
│                          │ /dev/binder │                                │
│                          │             │                                │
│                          │ binder.c    │                                │
│                          │ ioctl():    │                                │
│                          │  BINDER_    │                                │
│                          │  WRITE_READ │                                │
│                          └─────────────┘                                │
└─────────────────────────────────────────────────────────────────────────┘
```

### Уровень 1: Kernel Driver (/dev/binder)

Binder driver — это **модуль ядра Linux**, реализованный в `drivers/android/binder.c` (~6500 строк). Он предоставляет файловое устройство `/dev/binder`, через которое процессы взаимодействуют с помощью системных вызовов `open()`, `mmap()` и `ioctl()`.

#### Ключевые структуры данных ядра

```c
// Представляет процесс, открывший /dev/binder
struct binder_proc {
    struct hlist_node proc_node;    // Список всех процессов
    struct rb_root threads;          // Red-black tree потоков процесса
    struct rb_root nodes;            // Binder-узлы (объекты), принадлежащие процессу
    struct rb_root refs_by_desc;     // Ссылки на чужие узлы (по дескриптору)
    struct rb_root refs_by_node;     // Ссылки на чужие узлы (по узлу)
    struct list_head todo;           // Очередь ожидающих транзакций
    struct binder_alloc alloc;       // Управление mmap-буфером
    int pid;                         // PID процесса
    // ...
};

// Представляет Binder-объект (сервер)
struct binder_node {
    struct binder_proc *proc;        // Процесс-владелец
    struct hlist_head refs;          // Список ссылок на этот узел
    int internal_strong_refs;        // Счётчик сильных ссылок
    int local_strong_refs;
    binder_uintptr_t ptr;            // Указатель на BBinder в userspace
    binder_uintptr_t cookie;         // Cookie для идентификации
    // ...
};

// Представляет ссылку на чужой Binder-объект
struct binder_ref {
    struct rb_node rb_node_desc;     // В дереве по дескриптору
    struct rb_node rb_node_node;     // В дереве по узлу
    struct binder_node *node;        // Целевой узел
    struct binder_proc *proc;        // Процесс-владелец ссылки
    uint32_t desc;                   // Дескриптор (handle) для userspace
    // ...
};

// Представляет одну транзакцию
struct binder_transaction {
    struct binder_proc *from_proc;   // Отправитель
    struct binder_thread *from;      // Поток отправителя
    struct binder_proc *to_proc;     // Получатель
    struct binder_thread *to_thread; // Целевой поток (если есть)
    struct binder_buffer *buffer;    // Буфер с данными в mmap-области получателя
    unsigned int code;               // Код транзакции (номер метода)
    unsigned int flags;              // Флаги (TF_ONE_WAY и др.)
    kuid_t sender_euid;              // UID отправителя (устанавливается ядром!)
    pid_t sender_pid;                // PID отправителя (устанавливается ядром!)
    // ...
};
```

#### Механизм mmap: почему одно копирование

Когда процесс открывает `/dev/binder` и вызывает `mmap()`, ядро выделяет **виртуальную область** размером до 1 МБ в адресном пространстве процесса. Эта область отображена на **физические страницы**, которые ядро выделяет по мере необходимости.

При отправке транзакции:
1. Ядро вызывает `copy_from_user()` для копирования данных из буфера **отправителя** в **физические страницы** ядра
2. Эти же физические страницы уже **отображены** в mmap-область **получателя**
3. Получатель видит данные **напрямую** через своё mmap-отображение — **без второго копирования**

```
Отправитель (Process A)           Ядро                    Получатель (Process B)
┌────────────────────┐                                    ┌────────────────────┐
│ Виртуальная память │                                    │ Виртуальная память │
│                    │                                    │                    │
│ ┌────────────────┐ │     copy_from_user()               │ ┌────────────────┐ │
│ │ Parcel data    │ │ ──────────────────►                 │ │ mmap region    │ │
│ │ (user buffer)  │ │            ┌──────────────┐        │ │ (1MB)          │ │
│ └────────────────┘ │            │ Physical     │        │ │                │ │
│                    │            │ Pages        │◄───────│ │ mapped to same │ │
│                    │            │ (kernel)     │ mmap   │ │ physical pages │ │
│                    │            └──────────────┘        │ │                │ │
│                    │                                    │ │ Данные видны   │ │
│                    │                                    │ │ без копирования│ │
└────────────────────┘                                    │ └────────────────┘ │
                                                          └────────────────────┘
```

#### ioctl: основной интерфейс

Всё взаимодействие с драйвером идёт через один системный вызов:

```c
ioctl(fd, BINDER_WRITE_READ, &bwr);
```

Где `bwr` — структура `binder_write_read`:
```c
struct binder_write_read {
    binder_size_t write_size;     // Сколько байт записать
    binder_size_t write_consumed; // Сколько байт ядро прочитало
    binder_uintptr_t write_buffer; // Буфер команд для ядра
    binder_size_t read_size;      // Сколько байт прочитать
    binder_size_t read_consumed;  // Сколько байт ядро записало
    binder_uintptr_t read_buffer; // Буфер ответов от ядра
};
```

**Команды записи (BC = Binder Command):**
- `BC_TRANSACTION` — отправить транзакцию
- `BC_REPLY` — отправить ответ
- `BC_ACQUIRE` / `BC_RELEASE` — управление reference counting
- `BC_REQUEST_DEATH_NOTIFICATION` — подписка на смерть процесса

**Ответы чтения (BR = Binder Return):**
- `BR_TRANSACTION` — получена транзакция (нужно обработать)
- `BR_REPLY` — получен ответ на предыдущую транзакцию
- `BR_DEAD_BINDER` — процесс-владелец IBinder умер
- `BR_SPAWN_LOOPER` — команда создать новый Binder-поток

---

### Уровень 2: Native Layer (libbinder)

Native-слой (`frameworks/native/libs/binder/`) оборачивает ioctl-интерфейс ядра в удобные C++ классы.

```
┌─────────────────────────────────────────────────────────┐
│                    IBinder (interface)                    │
│  transact(code, data, reply, flags)                      │
├──────────────────────┬──────────────────────────────────┤
│                      │                                   │
│  ┌───────────────┐   │   ┌──────────────────┐           │
│  │   BpBinder    │   │   │    BBinder        │           │
│  │   (proxy)     │   │   │    (stub)         │           │
│  │               │   │   │                   │           │
│  │ Знает handle  │   │   │ Содержит          │           │
│  │ удалённого    │   │   │ реализацию        │           │
│  │ объекта       │   │   │ onTransact()      │           │
│  └───────┬───────┘   │   └─────────▲─────────┘           │
│          │           │             │                      │
│          ▼           │             │                      │
│  ┌────────────────────────────────────────────────┐      │
│  │         IPCThreadState (per-thread)             │      │
│  │                                                 │      │
│  │  talkWithDriver()  →  ioctl(BINDER_WRITE_READ)  │      │
│  │  writeTransactionData()                         │      │
│  │  executeCommand()                               │      │
│  └──────────────────────┬─────────────────────────┘      │
│                          │                                │
│  ┌──────────────────────▼─────────────────────────┐      │
│  │         ProcessState (per-process, singleton)    │      │
│  │                                                  │      │
│  │  open("/dev/binder")                             │      │
│  │  mmap(0, BINDER_VM_SIZE, ...)  // ~1MB           │      │
│  │  setThreadPoolMaxThreadCount(15)                 │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

**ProcessState** — синглтон на весь процесс:
- Открывает `/dev/binder` при первом обращении
- Вызывает `mmap()` для выделения 1 МБ буфера приёма
- Управляет thread pool (по умолчанию до 16 потоков)

**IPCThreadState** — один экземпляр на каждый поток (TLS):
- `talkWithDriver()` — отправляет и принимает данные через `ioctl()`
- `writeTransactionData()` — формирует `BC_TRANSACTION` команду
- `executeCommand()` — обрабатывает полученные `BR_*` ответы
- `joinThreadPool()` — бесконечный цикл: читать команду → выполнить → ответить

---

### Уровень 3: Java/Kotlin Layer

```
┌─────────────────────────────────────────────────────┐
│            android.os.IBinder (interface)             │
│  transact(int code, Parcel data, Parcel reply, int)  │
├─────────────────────┬───────────────────────────────┤
│                     │                                │
│  ┌───────────────┐  │  ┌────────────────────┐       │
│  │ BinderProxy   │  │  │ Binder             │       │
│  │               │  │  │                    │       │
│  │ Wraps native  │  │  │ extends BBinder    │       │
│  │ BpBinder      │  │  │ via JNI            │       │
│  │ via JNI       │  │  │                    │       │
│  │               │  │  │ onTransact() →     │       │
│  │ transact() →  │  │  │ dispatch to        │       │
│  │ native call   │  │  │ implementation     │       │
│  └───────────────┘  │  └────────────────────┘       │
│                     │                                │
│  JNI bridge: android_util_Binder.cpp                 │
│  (frameworks/base/core/jni/)                         │
└─────────────────────────────────────────────────────┘
```

**android.os.Binder** (серверная сторона):
- Наследуется AIDL-сгенерированным Stub-классом
- `onTransact()` вызывается из Binder-потока при получении транзакции
- `getCallingUid()` / `getCallingPid()` — идентификация вызывающего

**android.os.BinderProxy** (клиентская сторона):
- Автоматически создаётся при получении IBinder-ссылки из другого процесса
- `transact()` делегирует в native BpBinder через JNI
- Разработчик обычно не работает с BinderProxy напрямую — использует AIDL-сгенерированный Proxy

---

## AIDL: язык описания Binder-интерфейсов

AIDL (Android Interface Definition Language) — это язык описания интерфейсов для генерации Binder proxy/stub кода.

### Синтаксис

```java
// IBookManager.aidl
package com.example.app;

import com.example.app.Book;

interface IBookManager {
    List<Book> getBookList();
    void addBook(in Book book);
    oneway void notifyUpdate(in String message);
}
```

```java
// Book.aidl
package com.example.app;
parcelable Book;
```

### Что генерирует AIDL

```
IBookManager.aidl
        │
        ▼ (aidl compiler)
┌───────────────────────────────────────────────────┐
│              IBookManager.java                     │
│                                                    │
│  interface IBookManager extends IInterface {       │
│                                                    │
│    ┌──────────────────────────────────────────┐   │
│    │  abstract class Stub extends Binder      │   │
│    │    implements IBookManager                │   │
│    │                                          │   │
│    │  onTransact(code, data, reply, flags) {  │   │
│    │    switch(code) {                        │   │
│    │      case TRANSACTION_getBookList:       │   │
│    │        result = this.getBookList();      │   │
│    │        reply.writeParcelable(result);    │   │
│    │        break;                            │   │
│    │      case TRANSACTION_addBook:           │   │
│    │        book = data.readParcelable();     │   │
│    │        this.addBook(book);               │   │
│    │        break;                            │   │
│    │    }                                     │   │
│    │  }                                       │   │
│    │                                          │   │
│    │  ┌───────────────────────────────────┐   │   │
│    │  │  class Proxy implements           │   │   │
│    │  │    IBookManager                   │   │   │
│    │  │                                   │   │   │
│    │  │  getBookList() {                  │   │   │
│    │  │    data = Parcel.obtain();        │   │   │
│    │  │    reply = Parcel.obtain();       │   │   │
│    │  │    mRemote.transact(             │   │   │
│    │  │      TRANSACTION_getBookList,    │   │   │
│    │  │      data, reply, 0);            │   │   │
│    │  │    return reply.readList();       │   │   │
│    │  │  }                               │   │   │
│    │  └───────────────────────────────────┘   │   │
│    └──────────────────────────────────────────┘   │
│  }                                                 │
└───────────────────────────────────────────────────┘
```

### Kotlin-реализация сервиса

```kotlin
class BookManagerService : Service() {

    private val bookList = mutableListOf<Book>()

    // Реализация AIDL-интерфейса
    private val binder = object : IBookManager.Stub() {

        override fun getBookList(): List<Book> {
            // Вызывается из Binder-потока (НЕ Main Thread!)
            synchronized(bookList) {
                return bookList.toList()
            }
        }

        override fun addBook(book: Book) {
            synchronized(bookList) {
                bookList.add(book)
            }
        }

        override fun notifyUpdate(message: String) {
            // oneway — вызывающий не ждёт ответа
            Log.d("BookManager", "Update: $message")
        }
    }

    override fun onBind(intent: Intent): IBinder = binder
}
```

### Transaction codes

Каждый метод AIDL-интерфейса получает уникальный числовой код:
- `FIRST_CALL_TRANSACTION` (1) + порядковый номер метода
- `getBookList` → код 1
- `addBook` → код 2
- `notifyUpdate` → код 3

Этот код передаётся в `transact(code, data, reply, flags)` и используется в `switch` внутри `onTransact()` для маршрутизации к нужному методу.

### Модификатор `oneway`

```java
oneway void notifyUpdate(in String message);
```

- Вызов **не блокирует** вызывающий поток (не ждёт ответа)
- Метод **не может возвращать** значение (только void)
- Метод **не может выбрасывать** RemoteException вызывающему
- **Внимание:** `oneway` всё равно **блокирует**, если буфер ядра заполнен!

---

## Parcel: бинарная сериализация

Parcel — это контейнер для сериализации данных, передаваемых через Binder. Это **не** формат для долговременного хранения — только для IPC.

### Структура данных Parcel

```
┌───────────────────────────────────────────────────────────────┐
│                         PARCEL BUFFER                          │
├───────┬───────────┬───────┬───────────┬───────┬──────────────┤
│ type  │   data    │ type  │   data    │ type  │    data      │
│ (int) │  4 bytes  │(str)  │ "Hello"   │(bind) │ flat_binder_ │
│       │ = 42      │       │ len+UTF16 │       │ object       │
├───────┴───────────┴───────┴───────────┴───────┴──────────────┤
│                                                               │
│  Objects array: [offset_of_binder_1, offset_of_fd_1, ...]    │
│  (позиции специальных объектов: IBinder и FileDescriptor)     │
└───────────────────────────────────────────────────────────────┘
```

### Типы данных

| Метод | Размер | Что передаётся |
|-------|--------|---------------|
| `writeInt()` / `readInt()` | 4 байта | Целое число |
| `writeLong()` / `readLong()` | 8 байт | Длинное целое |
| `writeFloat()` / `readFloat()` | 4 байта | Число с плавающей точкой |
| `writeString()` / `readString()` | 4 + len×2 | UTF-16 строка (длина + данные) |
| `writeByteArray()` | 4 + len | Массив байт |
| `writeStrongBinder()` | flat_binder_object | **IBinder-ссылка** (handle в ядре) |
| `writeFileDescriptor()` | flat_binder_object | **Файловый дескриптор** (dup через ядро) |
| `writeParcelable()` | varies | Объект, реализующий Parcelable |

### Специальные объекты: IBinder и FileDescriptor

**writeStrongBinder()** — передаёт **не сериализованный объект**, а **handle** в ядре Binder:
- Ядро перехватывает `flat_binder_object` в Parcel
- Для локального Binder: создаёт `binder_node` + `binder_ref` в процессе получателя
- Получатель видит **BinderProxy**, указывающий на этот handle

**writeFileDescriptor()** — передаёт **файловый дескриптор** между процессами:
- Ядро вызывает `dup()` для создания копии fd в процессе получателя
- Позволяет делить файлы, sockets, pipes между процессами

### Лимит 1 MB

```
┌─────────────────────────────────────────────────────────┐
│        mmap BUFFER процесса (по умолчанию ~1 MB)         │
│                                                          │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐           │
│  │ Transaction│ │ Transaction│ │ Transaction│ свободно  │
│  │    #1      │ │    #2      │ │    #3      │           │
│  │   200 B    │ │   50 KB    │ │   300 B    │           │
│  └────────────┘ └────────────┘ └────────────┘           │
│                                                          │
│  Лимит 1 MB — это ОБЩИЙ буфер для ВСЕХ одновременных    │
│  транзакций к этому процессу, а НЕ на одну транзакцию!  │
└─────────────────────────────────────────────────────────┘
```

**Почему 1 MB:**
- Binder оптимизирован для **маленьких, частых** сообщений
- 1 MB более чем достаточно для lifecycle commands, Intent extras, system calls
- Для больших данных используются другие механизмы:
  - **ashmem / SharedMemory** — разделяемая память (ссылку передают через Binder)
  - **ParcelFileDescriptor** — передача файлового дескриптора
  - **ContentProvider** — потоковая передача через pipe

**Частая ошибка:**
```kotlin
// ❌ TransactionTooLargeException
val bigList = List(100_000) { "item_$it" }
intent.putStringArrayListExtra("data", ArrayList(bigList))
startActivity(intent)

// ✅ Правильно: передать ключ, данные через другой механизм
intent.putExtra("data_id", dataRepository.save(bigList))
startActivity(intent)
```

---

## ServiceManager: DNS системных сервисов

ServiceManager — это **первый** Binder-сервис, запускаемый при загрузке Android. Он имеет **хардкодированный handle 0** в ядре Binder и служит реестром для всех остальных системных сервисов.

```
┌─────────────────────────────────────────────────────────────┐
│                     ServiceManager                           │
│                     (handle = 0)                             │
│                                                              │
│  Реестр:                                                     │
│  ┌──────────────────┬──────────────────────────────┐        │
│  │  "activity"       │  → IBinder (AMS)              │        │
│  │  "window"         │  → IBinder (WMS)              │        │
│  │  "package"        │  → IBinder (PMS)              │        │
│  │  "power"          │  → IBinder (PowerManager)     │        │
│  │  "notification"   │  → IBinder (NMS)              │        │
│  │  "connectivity"   │  → IBinder (ConnectivitySvc)  │        │
│  │  "location"       │  → IBinder (LocationManager)  │        │
│  │  ...              │  → ...                        │        │
│  └──────────────────┴──────────────────────────────┘        │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
        ▼                  ▼                  ▼
  ┌──────────┐      ┌──────────┐      ┌──────────┐
  │  App      │      │ System   │      │ System   │
  │ Process   │      │ Server   │      │ UI       │
  │           │      │ (AMS,    │      │ Process  │
  │ getSystem │      │  WMS...) │      │          │
  │ Service() │      │          │      │          │
  └──────────┘      └──────────┘      └──────────┘
```

### Как работает регистрация

```kotlin
// В SystemServer при загрузке:
// (упрощённо, реальный код в ActivityManagerService.java)
ServiceManager.addService("activity", activityManagerService)
ServiceManager.addService("window", windowManagerService)
ServiceManager.addService("package", packageManagerService)
// ... ~100 сервисов
```

### Как работает поиск

```kotlin
// Когда приложение вызывает getSystemService()
val locationManager = getSystemService(Context.LOCATION_SERVICE) as LocationManager

// Внутри (ContextImpl.java → SystemServiceRegistry):
// 1. ServiceManager.getService("location")  — Binder-вызов к SM (handle 0)
// 2. SM возвращает IBinder сервиса
// 3. IBinder → BinderProxy → ILocationManager.Stub.asInterface()
// 4. asInterface() создаёт Proxy-обёртку
// 5. LocationManager хранит ссылку на Proxy
```

### Bootstrap-проблема

Как найти ServiceManager, если он сам — Binder-сервис? Ответ: **handle 0 хардкодирован в ядре**.

```c
// В ProcessState.cpp:
sp<IServiceManager> defaultServiceManager() {
    // Handle 0 — всегда ServiceManager
    return interface_cast<IServiceManager>(
        ProcessState::self()->getContextObject(nullptr));
    // getContextObject(nullptr) → BpBinder с handle 0
}
```

---

## Binder Thread Pool

Каждый процесс, использующий Binder, поддерживает **пул потоков** для обработки входящих транзакций.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Process (App)                                  │
│                                                                  │
│  ┌──────────────┐                                                │
│  │  Main Thread  │  ← UI, lifecycle (НЕ Binder-поток)            │
│  │  (Looper)     │                                                │
│  └──────────────┘                                                │
│                                                                  │
│  Binder Thread Pool (по умолчанию max 16):                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ Binder:1     │ │ Binder:2     │ │ Binder:3     │  ...        │
│  │ (ожидание)   │ │ (обработка   │ │ (ожидание)   │             │
│  │              │ │  транзакции) │ │              │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
│                                                                  │
│  Потоки создаются по требованию:                                 │
│  1. Процесс стартует с 1 Binder-потоком                          │
│  2. При нагрузке ядро посылает BR_SPAWN_LOOPER                   │
│  3. IPCThreadState создаёт новый поток                           │
│  4. Максимум: setMaxThreads(15) + 1 main Binder thread = 16     │
└─────────────────────────────────────────────────────────────────┘
```

### Идентификация вызывающего

Ядро Binder **автоматически записывает** UID и PID отправителя в каждую транзакцию. Эти значения **невозможно подделать** — они устанавливаются ядром.

```kotlin
// В Binder-потоке, обрабатывающем транзакцию:
class MyService : IMyService.Stub() {
    override fun sensitiveOperation(): Boolean {
        // UID/PID установлены ЯДРОМ — не приложением!
        val callerUid = Binder.getCallingUid()
        val callerPid = Binder.getCallingPid()

        // Проверка permission
        val hasPermission = checkCallingPermission(
            Manifest.permission.ACCESS_FINE_LOCATION
        ) == PackageManager.PERMISSION_GRANTED

        if (!hasPermission) {
            throw SecurityException("Missing permission")
        }

        return performOperation()
    }
}
```

### clearCallingIdentity / restoreCallingIdentity

```kotlin
// Когда системный сервис делает вызов от имени приложения:
override fun doSomethingForApp() {
    val callerUid = Binder.getCallingUid()
    // Проверяем права приложения
    enforceCallingPermission("com.example.PERMISSION", "Need permission")

    // Теперь нужно сделать вызов к другому системному сервису
    // от СВОЕГО имени (system), а не от имени приложения
    val token = Binder.clearCallingIdentity()
    try {
        // Здесь getCallingUid() вернёт наш UID (system)
        otherSystemService.internalOperation()
    } finally {
        Binder.restoreCallingIdentity(token)
    }
}
```

---

## Death Notification (linkToDeath)

Binder предоставляет механизм уведомления о **смерти удалённого процесса**. Когда процесс, владеющий Binder-объектом, умирает, ядро рассылает `BR_DEAD_BINDER` всем процессам, подписанным через `linkToDeath()`.

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│  Client App  │         │   Kernel     │         │ Server App   │
│              │         │  (Binder     │         │              │
│ linkToDeath  │────────►│   driver)    │◄────────│  IBinder     │
│ (recipient)  │         │              │         │  object      │
└──────┬───────┘         │ binder_ref   │         └──────┬───────┘
       │                 │ death_list   │                │
       │                 └──────┬───────┘                │
       │                        │                        │
       │                        │     Server процесс     │
       │                        │     умирает (crash     │
       │                        │     или kill)          │
       │                        │            ╳           │
       │                        ▼                        │
       │                 ┌──────────────┐                │
       │                 │ Kernel видит │                │
       │                 │ что процесс  │                │
       │   BR_DEAD_      │ умер, находит│                │
       │   BINDER        │ все binder_  │                │
       │◄────────────────│ ref с death  │                │
       │                 │ notification │                │
       ▼                 └──────────────┘
┌──────────────┐
│ DeathRecipient│
│ .binderDied()│
│ вызывается   │
│ на Binder-   │
│ потоке       │
└──────────────┘
```

### Kotlin-пример

```kotlin
class MyServiceConnection : ServiceConnection {
    private var binder: IMyService? = null

    private val deathRecipient = IBinder.DeathRecipient {
        // Вызывается на Binder-потоке, НЕ на Main Thread!
        Log.w("MyApp", "Remote service died!")
        binder = null
        // Попытка переподключения
        reconnectService()
    }

    override fun onServiceConnected(name: ComponentName, service: IBinder) {
        binder = IMyService.Stub.asInterface(service)
        // Подписываемся на уведомление о смерти
        service.linkToDeath(deathRecipient, 0)
    }

    override fun onServiceDisconnected(name: ComponentName) {
        // Вызывается при unbind, НЕ при смерти процесса
        binder = null
    }

    fun cleanup(service: IBinder) {
        // Отписка при ненадобности
        service.unlinkToDeath(deathRecipient, 0)
    }
}
```

---

## Security Model

### Три уровня безопасности Android

```
┌─────────────────────────────────────────────────────────────┐
│ Уровень 3: SELinux (Mandatory Access Control)                │
│                                                              │
│ Binder SELinux policy:                                       │
│ allow untrusted_app activity_service:service_manager find;   │
│ → Приложение МОЖЕТ искать AMS                               │
│                                                              │
│ neverallow untrusted_app kernel:binder call;                 │
│ → Приложение НЕ МОЖЕТ вызывать ядро через Binder            │
├──────────────────────────────────────────────────────────────┤
│ Уровень 2: Binder UID/PID (Kernel-level identity)           │
│                                                              │
│ Binder.getCallingUid() = 10142  (установлено ЯДРОМ)         │
│ checkCallingPermission("android.permission.CAMERA")          │
│ → PackageManager проверяет, есть ли у UID 10142 этот perm   │
├──────────────────────────────────────────────────────────────┤
│ Уровень 1: DAC (Unix file permissions)                       │
│                                                              │
│ /dev/binder:  crw-rw-rw-  (доступен всем)                   │
│ Файлы приложения: UID=10142, mode=0700 (только владелец)     │
└──────────────────────────────────────────────────────────────┘
```

### IBinder как capability token

В Binder-модели **владение IBinder-ссылкой = право на вызов**. Это capability-based security:

- Если вы получили IBinder, вы можете вызывать его методы
- Ядро контролирует, кто может получить ссылку
- PendingIntent — пример: содержит IBinder-токен, дающий право выполнить Intent от имени создателя

```kotlin
// PendingIntent — это capability token:
// Владелец PendingIntent может выполнить Intent
// от имени создателя (его UID и permissions)
val pendingIntent = PendingIntent.getActivity(
    context,
    0,
    intent,
    PendingIntent.FLAG_IMMUTABLE
)
// Внутри PendingIntent хранится IBinder-токен в system_server
// Любой, кто получит этот PendingIntent, может запустить Activity
// от имени создавшего его приложения
```

---

## Полный путь Binder-транзакции

Самая важная диаграмма — **15 шагов** от вызова метода на клиенте до получения ответа:

```
Client Process               Kernel (/dev/binder)           Server Process
══════════════               ═══════════════════           ══════════════

 1. proxy.getBookList()
    │
 2. Stub.Proxy.getBookList()
    │ data = Parcel.obtain()
    │ data.writeInterfaceToken()
    │
 3. mRemote.transact(
    │   TRANSACTION_getBookList,
    │   data, reply, 0)
    │
 4. BinderProxy.transact()
    │ → JNI → BpBinder::transact()
    │
 5. IPCThreadState::transact()
    │ writeTransactionData(
    │   BC_TRANSACTION, ...)
    │
 6. IPCThreadState::talkWithDriver()
    │ ioctl(fd, BINDER_WRITE_READ, &bwr)
    │
    ├──────────────►
    │               7. binder_ioctl()
    │                  binder_ioctl_write_read()
    │
    │               8. binder_transaction()
    │                  - Найти target process
    │                  - Аллоцировать буфер в
    │                    mmap-области получателя
    │                  - copy_from_user() данных
    │                    → в mmap-буфер
    │                  - Записать sender_euid,
    │                    sender_pid (ядром!)
    │                  - Добавить в todo-список
    │                    потока получателя
    │                  - wake_up() поток
    │               ◄──────────────┤
    │                              │
    │(клиент ждёт                  9. Binder-поток просыпается
    │ ответа в                     │  IPCThreadState::
    │ ioctl())                     │  talkWithDriver()
    │                              │  → читает BR_TRANSACTION
    │                              │
    │                             10. IPCThreadState::
    │                              │  executeCommand(BR_TRANSACTION)
    │                              │
    │                             11. BBinder::transact()
    │                              │  → JNI → Binder.execTransact()
    │                              │
    │                             12. Stub.onTransact(
    │                              │    TRANSACTION_getBookList,
    │                              │    data, reply, 0)
    │                              │  → this.getBookList()
    │                              │  → reply.writeList(result)
    │                              │
    │                             13. IPCThreadState::
    │                              │  sendReply()
    │                              │  writeTransactionData(
    │                              │    BC_REPLY, ...)
    │                              │  talkWithDriver()
    │               ┌──────────────┤
    │              14. binder_transaction()
    │                  (reply path)
    │                  - Буфер в mmap клиента
    │                  - wake_up() клиента
    ├──────────────►
    │
15. IPCThreadState читает
    BR_REPLY
    │ reply Parcel содержит данные
    │
    ▼
 return result
```

---

## Практическое применение: когда разработчик сталкивается с Binder

### startActivity() — ~5 Binder-транзакций

```kotlin
// Вы пишете:
startActivity(Intent(this, DetailActivity::class.java))

// Под капотом:
// 1. Context.startActivity()
// 2. → Instrumentation.execStartActivity()
// 3. → ActivityTaskManagerService.startActivity()  ← Binder IPC!
//    (через IActivityTaskManager.Stub.Proxy)
// 4. AMS проверяет permissions, находит Activity
// 5. AMS → ApplicationThread.scheduleLaunchActivity() ← Binder IPC!
//    (через IApplicationThread.Stub.Proxy)
// 6. ActivityThread получает команду на Main Thread (через Handler H)
// 7. performLaunchActivity() → onCreate()
```

### getSystemService() — путь к системным сервисам

```kotlin
val locationManager = getSystemService(LOCATION_SERVICE) as LocationManager

// Внутри:
// 1. ContextImpl.getSystemService("location")
// 2. SystemServiceRegistry.getSystemService() — создаёт/кэширует менеджер
// 3. ServiceManager.getService("location") ← Binder IPC к ServiceManager!
// 4. ILocationManager.Stub.asInterface(binder) — создаёт Proxy
// 5. LocationManager хранит Proxy для последующих вызовов

// Каждый вызов locationManager.getLastKnownLocation() — это Binder IPC:
val location = locationManager.getLastKnownLocation(LocationManager.GPS_PROVIDER)
// → ILocationManager.Stub.Proxy.getLastKnownLocation() → Binder → LocationManagerService
```

### ContentResolver.query() — IPC к ContentProvider

```kotlin
val cursor = contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null, null, null, null
)

// Если ContentProvider в ДРУГОМ процессе:
// 1. ContentResolver → ContentProviderProxy ← Binder IPC!
// 2. ContentProviderProxy.query() → Binder транзакция
// 3. Результат: CursorWindow (shared memory через ashmem)
//    — данные передаются через shared memory, НЕ через Parcel
//    — это обход 1MB лимита для больших результатов
```

---

## oneway Binder Calls

Модификатор `oneway` в AIDL делает вызов **асинхронным** — вызывающий не ждёт ответа.

```
Обычный вызов (синхронный):
Client ──── BC_TRANSACTION ──►  Server
       ◄─── BR_REPLY ────────
(клиент ждёт ответа)

oneway вызов (асинхронный):
Client ──── BC_TRANSACTION ──►  Server
       ◄─── BR_TRANSACTION_COMPLETE
(клиент продолжает работу, не ждёт обработки сервером)
```

### Важные нюансы oneway

1. **Всё равно блокирует**, если буфер ядра переполнен (backpressure)
2. **Не может возвращать** значение или выбрасывать исключение клиенту
3. **Доставка по порядку** для одного IBinder (FIFO в пределах connection)
4. **Lifecycle callbacks — это oneway**: `scheduleLaunchActivity`, `scheduleDestroyActivity` и т.д. отправляются из AMS как oneway, потому что AMS не должен ждать каждого приложения

---

## Binder Domains (Treble, Android 8+)

С Project Treble (Android 8.0) появились **три домена** Binder для изоляции framework и vendor кода:

```
┌───────────────────────────────────────────────────────────────┐
│                    Android Binder Domains                      │
├───────────────────────┬───────────────────┬───────────────────┤
│  /dev/binder          │  /dev/hwbinder    │  /dev/vndbinder   │
│                       │                   │                   │
│  Framework IPC        │  HAL IPC (HIDL)   │  Vendor-to-vendor │
│                       │                   │                   │
│  App ↔ SystemServer   │  Framework ↔ HAL  │  Vendor процессы  │
│  App ↔ App            │  (Camera HAL,     │  между собой      │
│  SystemServer внутри  │   Audio HAL,      │                   │
│                       │   Sensors HAL)    │                   │
│  ServiceManager       │  HwServiceManager │  VndServiceMgr    │
│  (handle 0)           │  (handle 0)       │  (handle 0)       │
├───────────────────────┴───────────────────┴───────────────────┤
│                                                               │
│  Зачем разделение:                                            │
│  • Framework обновляется через OTA независимо от vendor       │
│  • Vendor HAL не может напрямую вызывать framework сервисы    │
│  • SELinux политики жёстко ограничивают cross-domain вызовы   │
│  • Это позволяет обновлять Android без обновления vendor blob  │
└───────────────────────────────────────────────────────────────┘
```

---

## Подводные камни

### 1. TransactionTooLargeException

**Почему происходит:** 1 МБ — общий буфер для ВСЕХ одновременных транзакций к процессу. Большой Bundle в `savedInstanceState`, передача коллекций через Intent, большие Bitmap в RemoteViews.

**Как избежать:**
```kotlin
// ❌ Плохо: передача больших данных через Bundle
outState.putParcelableArrayList("items", ArrayList(bigList))  // может превысить 1MB

// ✅ Хорошо: сохранять только ID, данные в Room/файл
outState.putLongArray("item_ids", bigList.map { it.id }.toLongArray())
```

### 2. Binder thread pool exhaustion (deadlock)

**Почему происходит:** Все 16 Binder-потоков заняты обработкой запросов, а обработка каждого запроса делает синхронный Binder-вызов к другому сервису, который тоже ждёт ответа.

**Как избежать:** Не делать вложенные синхронные Binder-вызовы. Использовать `oneway` где возможно.

### 3. Синхронные Binder-вызовы на Main Thread

**Почему происходит:** Каждый вызов к системному сервису (`getSystemService()`, `PackageManager.getPackageInfo()`, `ContentResolver.query()`) — это синхронный Binder IPC. Если сервис перегружен, Main Thread блокируется.

**Как избежать:**
```kotlin
// ❌ На Main Thread:
val packageInfo = packageManager.getPackageInfo(packageName, 0)  // Binder IPC!

// ✅ В корутине:
val packageInfo = withContext(Dispatchers.IO) {
    packageManager.getPackageInfo(packageName, 0)
}
```

### 4. DeadObjectException

**Почему происходит:** Удалённый процесс умер (crash, killed by LMK), а клиент пытается вызвать метод через устаревший IBinder.

**Как избежать:** Использовать `linkToDeath()` для обнаружения смерти. Обрабатывать `DeadObjectException` в try/catch. Не кэшировать IBinder без death recipient.

### 5. Забыл проверить callingUid

**Почему опасно:** Если сервис обрабатывает запросы без проверки `getCallingUid()`, любое приложение может вызвать любой метод.

**Как избежать:**
```kotlin
override fun sensitiveMethod(): String {
    // ВСЕГДА проверяйте permissions или UID!
    enforceCallingPermission(
        "com.example.SENSITIVE_PERMISSION",
        "Caller doesn't have required permission"
    )
    return sensitiveData
}
```

### 6. Утечка ServiceConnection

**Почему происходит:** `bindService()` без `unbindService()` → Service живёт бесконечно, утечка памяти.

**Как избежать:** Всегда вызывать `unbindService()` в `onDestroy()` или `onStop()`.

---

## Мифы и заблуждения

**Миф:** "Binder — это просто RPC (Remote Procedure Call)"

**Реальность:** Binder — это **объектно-ориентированный IPC с lifecycle**. Каждый Binder-объект имеет reference counting (strong/weak refs), death notification, и kernel-level идентификацию. RPC — только один аспект Binder.

---

**Миф:** "Binder медленный, поэтому нужно минимизировать IPC"

**Реальность:** Binder — **самый быстрый IPC** для типичных Android-вызовов (~100-500 байт). Одна транзакция: ~10-20 μs (микросекунд). Проблемы возникают только при передаче больших данных (>100KB) или при массовых вызовах (тысячи в цикле).

---

**Миф:** "`oneway` — это fire-and-forget, вызов никогда не блокирует"

**Реальность:** `oneway` не ждёт ответа сервера, но **блокирует**, если kernel-буфер получателя переполнен. Это backpressure-механизм: если сервер не успевает обрабатывать, клиент затормозится.

---

**Миф:** "Лимит 1 MB — это на одну транзакцию"

**Реальность:** 1 МБ — это **общий буфер** mmap для **всех одновременных входящих транзакций** к процессу. Если 5 клиентов одновременно шлют по 200 КБ = 1 МБ → TransactionTooLargeException для следующего вызова.

---

**Миф:** "Можно подделать UID/PID вызывающего"

**Реальность:** UID и PID записываются **ядром** Linux, а не вызывающим процессом. Подделать их невозможно без root-доступа + модификации ядра. Это фундамент безопасности Android.

---

## Отладка Binder

### Полезные команды

```bash
# Список всех зарегистрированных Binder-сервисов
adb shell service list

# Статистика Binder-драйвера
adb shell cat /proc/binder/stats

# Активные транзакции
adb shell cat /proc/binder/transactions

# Состояние конкретного процесса
adb shell cat /proc/binder/proc/<pid>

# Информация о Binder thread pool
adb shell dumpsys activity processes | grep "Binder"

# StrictMode: обнаружить Binder-вызовы на Main Thread
```

```kotlin
// Включение StrictMode для обнаружения Binder-вызовов на Main Thread
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            // .detectCustomSlowCalls()  // Для обнаружения Binder
            .penaltyLog()
            .build()
    )
}
```

### Systrace / Perfetto

В Perfetto trace видны Binder-транзакции как отдельные события с информацией о:
- Отправитель и получатель (PID, TID)
- Код транзакции
- Размер данных
- Время ожидания

---

## CS-фундамент

| CS-концепция | Применение в Binder |
|--------------|-------------------|
| **IPC (Inter-Process Communication)** | Binder — основной механизм IPC в Android |
| **Proxy Pattern** | BinderProxy / Stub.Proxy — скрывает IPC за интерфейсом |
| **Memory-Mapped I/O** | mmap — ключ к 1-copy эффективности |
| **Reference Counting** | Strong/Weak refs для Binder-объектов, lifecycle management |
| **Capability-Based Security** | IBinder как capability token — владение = право |
| **Serialization** | Parcel — бинарная сериализация для IPC |
| **Client-Server** | Каждый Binder-вызов = клиент-серверное взаимодействие |
| **Thread Pool** | Binder thread pool обрабатывает входящие запросы |

---

## Проверь себя

<details>
<summary><strong>1. Почему Binder использует только 1 копирование данных, а Unix sockets — 2?</strong></summary>

Binder использует `mmap()` — ядро выделяет физические страницы и одновременно отображает их в адресное пространство получателя. При отправке транзакции `copy_from_user()` копирует данные из буфера отправителя **напрямую** в эти страницы. Получатель видит данные через своё mmap-отображение **без второго копирования**.

Unix sockets: `copy_from_user()` из отправителя в kernel buffer, затем `copy_to_user()` из kernel buffer в буфер получателя — два копирования.
</details>

<details>
<summary><strong>2. Что произойдёт, если все 16 Binder-потоков заняты синхронными вызовами?</strong></summary>

**Deadlock.** Новые входящие Binder-транзакции не могут быть обработаны, потому что нет свободных потоков. Если занятые потоки сами ждут ответа от этого же процесса (вложенные Binder-вызовы), возникает циклическая зависимость. Процесс перестаёт отвечать на любые Binder-запросы, что может привести к ANR.
</details>

<details>
<summary><strong>3. Почему UID/PID вызывающего нельзя подделать в Binder?</strong></summary>

UID и PID записываются **ядром Linux** в структуру `binder_transaction` при обработке `BC_TRANSACTION`. Ядро использует `current->cred->euid` и `current->pid` — реальные значения из контекста процесса. Пользовательский код не может модифицировать эти поля, потому что они записываются в kernel-space, недоступном для userspace. Единственный способ подделать — модификация ядра, что требует root + отключённый Verified Boot.
</details>

<details>
<summary><strong>4. Что такое handle 0 и почему он хардкодирован?</strong></summary>

Handle 0 — это Binder-дескриптор для **ServiceManager**. Он хардкодирован в ядре Binder-драйвера как "context manager". Это решает bootstrap-проблему: чтобы найти любой Binder-сервис, нужно обратиться к ServiceManager. Но чтобы найти ServiceManager, нужен его handle. Хардкодирование handle 0 разрывает эту циклическую зависимость.
</details>

<details>
<summary><strong>5. Почему лимит Binder-буфера — 1 MB, а не больше?</strong></summary>

Binder оптимизирован для **частых маленьких сообщений** (lifecycle commands, Intent extras: 100-500 байт). 1 МБ mmap-буфер выделяется **на каждый процесс** — при 100 активных процессах это 100 МБ физической памяти. Увеличение буфера увеличило бы потребление RAM на мобильном устройстве. Для передачи больших данных есть другие механизмы: ashmem/SharedMemory, ParcelFileDescriptor, ContentProvider с CursorWindow.
</details>

---

## Ключевые карточки

**Q:** Сколько копирований данных делает Binder при IPC?
**A:** Одно. Через mmap: `copy_from_user()` из отправителя в физические страницы, отображённые в mmap-область получателя.

**Q:** Что такое ServiceManager и какой у него handle?
**A:** Реестр системных сервисов. Handle 0 (хардкодирован в ядре). Все сервисы регистрируются через `addService()` и находятся через `getService()`.

**Q:** Сколько потоков в Binder thread pool по умолчанию?
**A:** Максимум 16 (15 + 1 main Binder thread). Создаются по требованию через `BR_SPAWN_LOOPER`.

**Q:** Что делает `oneway` модификатор в AIDL?
**A:** Делает вызов асинхронным: клиент не ждёт ответа сервера. Но всё равно блокирует при переполнении буфера.

**Q:** Как Binder обеспечивает security?
**A:** Три уровня: (1) ядро записывает UID/PID отправителя (нельзя подделать), (2) сервис проверяет permissions через `checkCallingPermission()`, (3) SELinux ограничивает, какие домены могут общаться.

**Q:** Что такое TransactionTooLargeException?
**A:** Исключение при превышении ~1 МБ общего mmap-буфера для ВСЕХ одновременных входящих транзакций к процессу.

**Q:** Чем `linkToDeath()` отличается от `onServiceDisconnected()`?
**A:** `linkToDeath()` — callback при смерти **процесса** (на Binder-потоке). `onServiceDisconnected()` — callback при отключении ServiceConnection (на Main Thread), может вызываться и при unbind.

**Q:** Зачем в Treble три Binder-домена?
**A:** Изоляция: `/dev/binder` (framework ↔ app), `/dev/hwbinder` (framework ↔ HAL), `/dev/vndbinder` (vendor ↔ vendor). Позволяет обновлять framework без обновления vendor.

---

## Куда дальше

| Тема | Зачем | Где |
|------|-------|-----|
| Service Internals | Как Binder используется в Bound Services | [[android-service-internals]] |
| Intent Internals | Intent resolution через Binder к AMS | [[android-intent-internals]] |
| System Services | AMS, WMS, PMS — все работают через Binder | [[android-system-services]] |
| ActivityThread | Как lifecycle callbacks доставляются через Binder | [[android-activitythread-internals]] |
| Bundle/Parcelable | Подробнее о Parcel и сериализации | [[android-bundle-parcelable]] |
| Kernel Extensions | Binder driver, ashmem, другие Android-патчи ядра | [[android-kernel-extensions]] |
| Window System | WMS работает через Binder IPC | [[android-window-system]] |
| Boot Process | Как ServiceManager стартует при загрузке | [[android-boot-process]] |

---

## Связи

### Фундамент
- [[android-architecture]] — высокоуровневый обзор архитектуры, включая Binder
- [[android-kernel-extensions]] — Binder driver как kernel module
- [[os-processes-threads]] — процессы и IPC на уровне ОС

### Используют Binder
- [[android-service-internals]] — Bound Service: Local Binder, Messenger, AIDL
- [[android-intent-internals]] — Intent resolution через AMS (Binder)
- [[android-window-system]] — WMS: все window-операции через Binder
- [[android-context-internals]] — getSystemService() использует ServiceManager (Binder)
- [[android-notifications]] — NotificationManagerService через Binder
- [[android-activitythread-internals]] — lifecycle callbacks через IApplicationThread (Binder)

### Сериализация
- [[android-bundle-parcelable]] — Parcel, Bundle, Parcelable: сериализация для Binder

---

## Источники

### Академические работы
| Источник | Описание |
|----------|----------|
| Schreiber T. *Android Binder — Android Interprocess Communication* (Master's thesis, TU Munich, 2011) | Самый подробный академический анализ Binder |

### AOSP Source Code
| Файл | Содержание |
|------|-----------|
| [drivers/android/binder.c](https://cs.android.com/android/kernel/superproject/+/common-android-mainline:common/drivers/android/binder.c) | Kernel Binder driver (~6500 строк) |
| [frameworks/native/libs/binder/](https://cs.android.com/android/platform/superproject/+/master:frameworks/native/libs/binder/) | Native libbinder (C++) |
| [frameworks/base/core/java/android/os/Binder.java](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/java/android/os/Binder.java) | Java Binder class |
| [frameworks/base/core/jni/android_util_Binder.cpp](https://cs.android.com/android/platform/superproject/+/master:frameworks/base/core/jni/android_util_Binder.cpp) | JNI bridge |
| [frameworks/native/cmds/servicemanager/](https://cs.android.com/android/platform/superproject/+/master:frameworks/native/cmds/servicemanager/) | ServiceManager native daemon |

### Документация
| Источник | URL | Описание |
|----------|-----|----------|
| Android Source — Binder IPC | https://source.android.com/docs/core/architecture/hidl/binder-ipc | Официальная документация AOSP |
| Android Source — AIDL | https://developer.android.com/develop/background-work/services/aidl | AIDL developer guide |

### Статьи и доклады
| Источник | Описание |
|----------|----------|
| [ProAndroidDev: Android Binder Mechanism](https://proandroiddev.com/android-binder-mechanism-the-backbone-of-ipc-in-android-6cfc279eb046) | Подробный обзор с диаграммами |
| Opersys — Android Internals training slides | Профессиональный курс по Android internals |
| eLinux.org — Android Binder | Техническое описание driver-уровня |
| LWN.net — Binder upstreaming | История принятия Binder в mainline Linux |

### Книги
| Книга | Применение |
|-------|-----------|
| Vasavada N. *Android Internals: A Confectioner's Cookbook* (2019) | Binder internals с AOSP анализом |
| Levin J. *Android Internals: Power User's View* (2015) | Kernel-level Binder |
| Meier R. *Professional Android* (4th ed, 2018) | AIDL и Service binding |
